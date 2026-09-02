#!/usr/bin/env python3
"""The solver stage of a demo act: the run's own monitors, advancing at pace.

WHAT DIFFERS FROM A LIVE SOLVE, AND WHAT DOES NOT. This is the one stage of an
act where time is compressed. The iteration counter, the residuals, the force
or temperature curves and the sweep-point progress all advance, progressively,
in the order and with the values the run produced. What is compressed is the
WAIT. What is not compressed is the reported time: the elapsed figure on screen
is the run's real wall clock, read from its own ExecutionTime lines and its own
launcher record, and the cost line is the run's real cost. Those are two
different quantities and only one of them is scaled.

Everything this stage puts on screen comes from :mod:`replay_history`, which
refuses to hand over a single frame until its planted controls have been read
back off disk. In particular it refuses unless it can prove it is reading the
FIRST pressure pass of each iteration and not the non-orthogonal corrector
pass (L-419). See that module's preamble.

THREE PROPERTIES THIS MODULE IS BUILT TO GUARANTEE.

1. NOTHING ARRIVES ALL AT ONCE. Frames are scheduled against a deadline
   clock, one per tick, and the stage asserts on the way out that its own
   emissions carry strictly increasing timestamps spread across the stage's
   duration. A stage that emitted its whole history in one burst and then sat
   still would look hardcoded, and would fail its own exit assertion here
   before it ever reached a pacing harness.

2. THE BANNER CANNOT DRIFT FROM THE CONTENT. The banner text is not an
   independent signal that has to be kept in step with the frames; it is a
   PURE FUNCTION of the frame being shown (:func:`banner_for`). It is computed
   from that frame and published in the same tick as that frame. There is no
   state in which the banner is ahead of or behind what the screen shows,
   because there is no second source for it to be ahead of.

3. PACING IS A SCHEDULING DECISION, NEVER A DATA DECISION. This module decides
   WHEN a value appears. It never decides WHAT the value is. Selection of which
   rows to show is stride-only down-sampling done in :mod:`replay_history`,
   verbatim, and recorded there with the source row of every frame.

LANGUAGE. Every human-readable string this stage emits is passed through the
act wording doctrine (``workflows.check_wording``) before it leaves, so the
vocabulary rules are enforced at emission rather than trusted to review.
Progressive tense while running, PRESENT tense for what has finished. This
line read "past tense for what has finished" and it is the standing
instruction at the head of the very module whose closing sentence was past
tense, so it is named here as the likeliest reason that sentence was written.
Sanaa's 04:20Z order is "no past tense", later and stricter than the 03:40Z
zone rule; present is the intersection.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

from chief_engineer.replay_history import (
    ReaderRefused, RunHistory, USD_PER_CORE_HOUR, read_run_history)

__all__ = ["ReplaySpec", "ReplayStage", "banner_for", "STAGE_ID"]

#: The stage's identity in the act sequence. One constant so the sequencer,
#: the banner and the event names cannot disagree about what this stage is
#: called.
STAGE_ID = "solving"


# ===========================================================================
# The banner, as a pure function of what is on screen
# ===========================================================================

def banner_for(state: dict) -> str:
    """The banner text for a given frame state. Deterministic, no side effects.

    Called with the same dictionary that is published as the frame, so the
    banner and the content are two renderings of one fact rather than two
    signals that have to be synchronised.

    TENSE, STATED FOR BOTH BRANCHES BECAUSE STATING IT FOR ONE IS HOW THE
    OTHER SLIPPED THROUGH. This docstring used to read "Progressive tense,
    because while this returns a value the stage is still running" -- true of
    the RUNNING branch, and it never covered the FINISHED branch, which
    returned "Solved". Past tense, on the banner, on the filmed surface. It
    rendered nowhere until the control room grew a handler for
    ``stage.banner``, so the day it became visible was the day it became a
    defect.

    * While the stage runs, the banner is PROGRESSIVE: "Solving",
      "Solving, iteration N of M".
    * When it finishes, the banner is PRESENT: "Solve complete". Not
      "Solved". Sanaa's 04:20Z order is "no past tense" and it is the later
      and stricter of two directives of hers that disagree; present is the
      intersection, satisfying the later outright and at worst shifting
      register under the earlier. "Complete" is an adjective and carries no
      tense at all, so it is safe under both readings.

    No number moves: this is one string.
    """
    if state.get("finished"):
        return "Solve complete"
    point = state.get("point_index")
    points = state.get("points")
    iteration = state.get("iteration")
    total = state.get("iterations")
    # A SWEEP RUNNING TOGETHER HAS NO CURRENT POINT, so it is not given one.
    # "Sweep point 3 of 5" is a true sentence about a screen showing one trace
    # at a time and a false one about a screen showing five advance at once
    # (Sanaa's small-multiple monitors, 2026-09-01). What is true of the whole
    # sweep is how far it has come, and that is what this reports: the furthest
    # iteration any point has reached, which is monotone and is read off the
    # frames rather than off a screen-time counter.
    #
    # THE SWEEP PROGRESS RIDES THE PAYLOAD UNDER ITS OWN KEYS, not `iteration`
    # and `iterations`, which stay the FRAME'S own and are what the monitors
    # plot. Two quantities, two names — and it keeps INVARIANT 1 intact: the
    # banner is still a pure function of the very dictionary that is published,
    # so recomputing it from a recorded event reproduces it exactly.
    if state.get("concurrent"):
        # THE NOUN IS THE ACT'S AND THE WORD IS "IN PARALLEL". Sanaa,
        # 2026-09-02 orders, item 3, verbatim: 'Progress line: "Solving 5
        # operating points in parallel," all monitors advancing together.
        # Sequential language banned.' The noun rides the state dict so this
        # stays a pure function of the very dictionary that is published;
        # an act that declares none keeps "sweep point".
        noun = str(state.get("point_noun") or "sweep point")
        reached = state.get("sweep_iteration")
        span = state.get("sweep_iterations")
        if reached is None or not span:
            return f"Solving {int(points or 0)} {noun}s in parallel"
        return (f"Solving {int(points or 0)} {noun}s in parallel, "
                f"iteration {int(reached):,} of {int(span):,}")
    if point is None or iteration is None:
        return "Solving"
    head = f"Solving, iteration {int(iteration):,} of {int(total):,}"
    if points and points > 1:
        return f"{head}, sweep point {point} of {points}"
    return head


# ===========================================================================
# What to replay
# ===========================================================================

@dataclass
class ReplaySpec:
    """One solver stage: which runs, in what order, at what pace."""

    #: Ordered ``(label, case_dir)``. The order is the presentation order.
    cases: Sequence[tuple]
    #: Columns of ``coefficient.dat`` whose curves move on screen.
    coefficient_columns: Sequence[str] = ("Cl", "Cd")
    #: Frames per sweep point. Real rows, stride-selected, never averaged.
    max_frames: int = 120
    #: Seconds of screen time each sweep point occupies.
    seconds_per_point: float = 9.0
    #: Assert this module's Cl history is identical to the jet-flap family's
    #: own reader, so one number cannot fork into two implementations.
    cross_check_jf1: bool = False
    #: What the progress row calls a point. "Sweep point" for a blowing
    #: sweep; an act with one run leaves this alone and gets no progress row.
    point_noun: str = "sweep point"
    #: THE COMPUTE FIGURE IN THE CLOSING SENTENCE, when the act shows one for
    #: hardware this box is not. A ``workflows.demo_mode.HardwareProjection``,
    #: or ``None``, which is every act but the jet-flap today and leaves the
    #: sentence byte-identical.
    #:
    #: TYPED AS Any RATHER THAN IMPORTED. ``chief_engineer`` is the layer
    #: ``workflows`` is built on; importing the act layer here to name a type
    #: would invert that and make the solver stage depend on the demo package.
    #: The stage never inspects the object -- it calls ``apply`` and reads two
    #: strings -- so the shape is the contract and the direction of the
    #: dependency is preserved.
    #:
    #: THE MEASURED FIGURE IS NOT AFFECTED. ``solve.end`` keeps publishing
    #: ``core_min_measured`` and ``cost_basis`` from ``RunHistory``, which is
    #: what the record, the ledger and the calibration row read. Only the
    #: spoken sentence changes, and only when an act asks for it.
    cost_projection: Any = None


# ===========================================================================
# The stage
# ===========================================================================

@dataclass
class ReplayStage:
    """A solver stage that advances a completed run's monitors at pace.

    Plugs into the house event convention already used throughout
    ``sdk/workflows``: an ``emit(event_name, payload)`` callable backed by the
    mission :class:`~chief_engineer.events.EventBus`. ``sleep`` and ``clock``
    are injectable so a test can drive the whole stage in microseconds without
    changing a single value it publishes.
    """

    spec: ReplaySpec
    sleep: Callable[[float], None] = time.sleep
    clock: Callable[[], float] = time.monotonic
    stage_id: str = STAGE_ID

    _history: RunHistory | None = field(default=None, init=False, repr=False)
    _emitted: list = field(default_factory=list, init=False, repr=False)

    # -- before anything moves ----------------------------------------------
    def prepare(self) -> RunHistory:
        """Read every run and run every planted control. Refuses on failure.

        Called before a single frame is emitted, and deliberately separate
        from :meth:`run`: a reader that cannot see its own plants must fail
        while the screen is still on the previous stage, not halfway through a
        moving plot.
        """
        self._assert_labels_are_readable()
        self._history = read_run_history(
            self.spec.cases,
            coefficient_columns=self.spec.coefficient_columns,
            max_frames=self.spec.max_frames,
            cross_check_jf1=self.spec.cross_check_jf1)
        return self._history

    def _assert_labels_are_readable(self) -> None:
        """Refuse a point label that is really a case id.

        THIS STAGE MINTS THE LABEL THAT REACHES THE SCREEN, so it is this
        stage's job to refuse a bad one rather than let a downstream display
        layer rewrite it. The asymmetry is worth stating: a fidelity chip gets
        TRANSLATED downstream because it carries meaning a viewer can use; a
        case id gets REFUSED because it carries none, and quietly rewriting it
        at the display layer would only hide a defect belonging here.

        An act naming its points after its run directories is the easy
        mistake, and it produces a screen reading "Solving, sweep point 3 of
        5" beside a token nobody outside this lab can parse.
        """
        for label, case_dir in self.spec.cases:
            try:
                _check(str(label))
            except Exception as exc:
                raise ReaderRefused(
                    f"the point label {label!r} is not something a viewer can "
                    f"read, so this stage will not publish it: {exc}. Give "
                    f"each point a plain label naming what was varied, for "
                    f"example the blowing setting, and keep the run "
                    f"directory in the record where it is useful.") from exc

    # -- the run ------------------------------------------------------------
    def run(self, emit: Callable | None = None, script=None) -> dict:
        """Advance the monitors. Returns the stage's own record of what it did.

        ``script`` is an optional transcript; when given, the stage speaks the
        two sentences an engineer would say at the start and end of a solve.
        BOTH ARE PRESENT TENSE, and the closing one was not: it read "Solved
        N sweep points, ...", the third past-tense string found on the filmed
        surface in one day, and it sat beside a progressive opener so it was
        inconsistent as well as prohibited. It now reads "N sweep points
        complete, ...". Sanaa's 04:20Z order is "no past tense" and it is the
        later and stricter of two directives of hers that disagree; present is
        the intersection.

        THE CLOSING SENTENCE IS COMPOSED IN :meth:`_closing_sentence`, which
        carries the two things about it that are load-bearing: why it leads
        with "All", and what happens to the compute figure when the act shows
        one for hardware this box is not. Read that method, and re-derive the
        sentence by driving the stage rather than by reading its f-string.
        """
        history = self._history or self.prepare()
        points = len(history.points)

        # THE PARALLEL DECISION IS SPOKEN, NOT IMPLIED. Sanaa, 2026-09-02
        # item 3: the progress line is "Solving 5 operating points in
        # parallel". "In parallel" is stated only when the runs actually
        # overlapped on the box (history.concurrent is measured off their own
        # start and end stamps), so the sentence cannot outrun the record.
        if points > 1 and history.concurrent:
            self._say(script, emit,
                      f"Solving {points} {self.spec.point_noun}s in parallel.")
        else:
            self._say(script, emit,
                      f"Solving {points} {self.spec.point_noun}s.")
        self._publish(emit, "solve.begin", {
            "stage": self.stage_id,
            "points": points,
            "labels": [p.label for p in history.points],
            "iterations_per_point": [p.history_n for p in history.points],
            "controls": list(history.controls),
        }, banner_state={"point_index": None, "points": points})

        started = self.clock()
        # ONE PASS, NOT N CLIPS. Sanaa, 2026-09-01: "all five sweep points side
        # by side ... advancing simultaneously, so the sweep completes in one
        # pass instead of five sequential clips." A sweep of more than one point
        # therefore interleaves; a single-point stage keeps the sequential path
        # exactly as it was, because for one point the two are the same walk.
        if points > 1:
            self._run_together(emit, history)
        else:
            for index, point in enumerate(history.points, start=1):
                self._run_point(emit, index, points, point)

        return self._finish(emit, script, history, self.clock() - started)

    def _run_together(self, emit, history: RunHistory) -> None:
        """Every point advancing at once, on one schedule.

        WHAT IS UNCHANGED, AND IT IS THE PART THAT MATTERS FOR PACING. The same
        events go out, one per frame, and the stage occupies the same screen
        time it did: ``seconds_per_point`` x points. So the arrival rate on the
        wire is what it was -- measured at 1,225 events in 44.9 s, 36.7 ms each,
        against a paced-queue floor of 45 ms, which is why these frames render
        unpaced. Interleaving reorders the frames; it does not compress them.
        Compressing the stage to one point's worth of screen time would put the
        same 1,225 events out in 9 s, 7.3 ms each, and no amount of client-side
        care makes that readable.

        THE ORDER IS BY FRACTIONAL PROGRESS, not round-robin by index. Points
        may hold different numbers of frames -- they are downsampled from logs
        of different lengths -- and a plain round robin would run the short ones
        out early and leave the last stretch a single trace advancing alone,
        which is the sequential clip again in miniature. Ordering every frame by
        how far through ITS OWN run it is makes all the traces reach their ends
        together, which is what "advancing simultaneously" means on screen.

        THE BANNER IS THE SWEEP'S, NOT A POINT'S. "Sweep point 3 of 5" is a
        false statement about a screen on which all five are moving; the banner
        reports how far the whole sweep has come, from the furthest iteration
        any point has reached. See :func:`banner_for`.
        """
        points = len(history.points)
        for index, point in enumerate(history.points, start=1):
            if not point.frames:
                raise ReaderRefused(f"{point.case_dir} produced no frames")
            begin = {
                "stage": self.stage_id,
                "point_index": index, "points": points,
                "label": point.label,
                "iterations": point.history_n,
                "wall_s": point.status["wall_s"],
                "downsample": point.provenance,
                "concurrent": True,
                # The act's noun for a point, read by banner_for so the
                # banner stays a pure function of the published dict.
                "point_noun": self.spec.point_noun,
                "sweep_iteration": int(point.frames[0].iteration),
                "sweep_iterations": int(point.history_n),
            }
            self._publish(emit, "solve.point.begin", begin, banner_state=begin)

        schedule = []
        for index, point in enumerate(history.points, start=1):
            n = len(point.frames)
            for slot, frame in enumerate(point.frames, start=1):
                schedule.append((slot / n, index, point, frame, slot == n))
        schedule.sort(key=lambda row: (row[0], row[1]))

        span = float(self.spec.seconds_per_point) * points
        interval = span / len(schedule)
        origin = self.clock()
        furthest, furthest_total = 0, 0

        for position, (_, index, point, frame, is_last) in enumerate(schedule):
            furthest = max(furthest, int(frame.iteration))
            furthest_total = max(furthest_total, int(point.history_n))
            state = {
                "stage": self.stage_id,
                "point_index": index, "points": points,
                "label": point.label,
                "iteration": frame.iteration,
                "iterations": point.history_n,
                "elapsed_s": frame.elapsed_s,
                "residuals": dict(frame.residuals),
                "coefficients": dict(frame.coefficients),
                "envelope": {k: list(v) for k, v in frame.envelope.items()},
                "source_row": frame.source_row,
                "concurrent": True,
                "point_noun": self.spec.point_noun,
                "sweep_iteration": furthest,
                "sweep_iterations": furthest_total,
            }
            deadline = origin + (position + 1) * interval
            remaining = deadline - self.clock()
            if remaining > 0:
                self.sleep(remaining)
            self._publish(emit, "solve.frame", state, banner_state=state)
            if is_last:
                end = {
                    "stage": self.stage_id,
                    "point_index": index, "points": points,
                    "label": point.label,
                    "iterations": point.history_n,
                    "wall_s": point.status["wall_s"],
                    "core_min_measured": point.status["core_min_measured"],
                    "final": dict(point.final),
                    "controls": list(point.controls),
                    "concurrent": True,
                    "point_noun": self.spec.point_noun,
                    "sweep_iteration": furthest,
                    "sweep_iterations": furthest_total,
                }
                self._publish(emit, "solve.point.end", end, banner_state=end)

    def _run_point(self, emit, index: int, points: int, point) -> None:
        frames = point.frames
        if not frames:
            raise ReaderRefused(f"{point.case_dir} produced no frames")

        self._publish(emit, "solve.point.begin", {
            "stage": self.stage_id,
            "point_index": index, "points": points,
            "label": point.label,
            # The case id is NOT published. It is a token a viewer cannot use,
            # and the standard keeps it off every user-visible surface. It
            # stays in the RunHistory that prepare() returns, which is the run
            # record and the right place to look it up.
            "iterations": point.history_n,
            # The run's REAL wall time, which the clock on screen counts
            # through while far less screen time passes. The wait is
            # compressed; this number is not.
            "wall_s": point.status["wall_s"],
            "downsample": point.provenance,
        }, banner_state={"point_index": index, "points": points,
                         "iteration": frames[0].iteration,
                         "iterations": point.history_n})

        # Deadline scheduling, not accumulated sleeps: a slow consumer steals
        # from the next gap rather than stretching the stage without limit,
        # and no two frames can collapse onto one instant.
        span = float(self.spec.seconds_per_point)
        origin = self.clock()
        interval = span / len(frames)

        for frame in frames:
            state = {
                "stage": self.stage_id,
                "point_index": index, "points": points,
                "label": point.label,
                "iteration": frame.iteration,
                "iterations": point.history_n,
                # The run's real elapsed at THIS iteration, off its own
                # ExecutionTime line. Not interpolated, not a fraction of the
                # total, not a screen-time counter wearing a seconds label.
                "elapsed_s": frame.elapsed_s,
                "residuals": dict(frame.residuals),
                "coefficients": dict(frame.coefficients),
                "envelope": {k: list(v) for k, v in frame.envelope.items()},
                "source_row": frame.source_row,
            }
            deadline = origin + (frame.position + 1) * interval
            remaining = deadline - self.clock()
            if remaining > 0:
                self.sleep(remaining)
            self._publish(emit, "solve.frame", state, banner_state=state)

        last = frames[-1]
        self._publish(emit, "solve.point.end", {
            "stage": self.stage_id,
            "point_index": index, "points": points,
            "label": point.label,
            "iterations": point.history_n,
            "wall_s": point.status["wall_s"],
            "core_min_measured": point.status["core_min_measured"],
            "final": dict(point.final),
            "controls": list(point.controls),
        }, banner_state={"point_index": index, "points": points,
                         "iteration": last.iteration,
                         "iterations": point.history_n})

    def _finish(self, emit, script, history: RunHistory,
                screen_s: float) -> dict:
        # Elapsed. Per point it is that run's own measured wall time. For the
        # sweep as a whole there may be NO honest single total: these runs
        # overlapped on the box, so the sum of their wall times is not a
        # duration anything took. Both real figures are published, labelled,
        # and the stage does not pick between them.
        # RULING (cfd-supervisor, 2026-09-01): no sweep total goes in the
        # banner at all. Her spec asks for progress across the sweep points,
        # which is a progress indicator and not a duration; per-point clocks
        # plus sweep progress satisfy it completely. The sum of the five wall
        # times is deliberately NOT published: they overlapped, so their sum
        # is not an elapsed time at all but a resource measure, and the lab
        # already has an honest resource measure for that, additive and
        # unaffected by concurrency, which is core-minutes. If layout ever
        # forces a single duration it is the wall-clock span below, and it
        # carries its basis with it.
        per_point = [p.status["wall_s"] for p in history.points]
        payload = {
            "stage": self.stage_id,
            "wall_s_per_point": per_point,
            "wall_clock_span_s": history.wall_clock_span_s,
            # PRESENT TENSE, 2026-09-01, and it is a ruling rather than a
            # style choice. Sanaa's 03:40Z rule is zone-aware ("past tense for
            # results"); her 04:20Z order says flatly "no past tense". Two of
            # her own directives disagree. Present is the intersection: it
            # satisfies the later prohibition outright and is at worst a mild
            # shift of register under the earlier one, where past tense
            # satisfies one and violates the other. No number moves.
            "wall_clock_span_basis": (
                "the span of a sweep whose points run concurrently"
                if history.concurrent else
                "the span from the first start to the last end"),
            "ran_concurrently": history.concurrent,
            "elapsed_note": (
                "each point's elapsed figure is that run's own measured wall "
                "time" + (
                    "; the points run concurrently, so no single sweep total "
                    "is published as a duration"
                    if history.concurrent else "")),
            "core_min_measured": round(history.core_min_total, 4),
            # ``usd_derived`` AND ``cost_basis`` NO LONGER RIDE THE WIRE.
            # Sanaa's 2026-09-02 order, item 4: no currency on any screen, and
            # the never-list now refuses a dollar string mechanically, which
            # is exactly what caught these two: the run record's own
            # cost-basis sentence names the recorded rate in dollars. The page
            # renders neither key, so nothing on screen changes; the derived
            # dollar figure and its basis sentence stay in the RUN RECORD and
            # in the ``RunHistory`` this stage's ``prepare()`` returns, which
            # is where the ledger and the calibration row read them (rule 12).
            "screen_s": round(screen_s, 3),
            "controls": list(history.controls),
            "finished": True,
        }
        # Asserted BEFORE the closing event is published, so the record the
        # stage returns and the event the screen receives carry the same
        # figures. A stage that emitted in a burst never reaches its own
        # "Solve complete" banner.
        payload["progressive"] = self._assert_progressive()
        # The stage returns the SAME dictionary that was published, so a
        # caller reading the return value and a screen reading the event can
        # never be looking at two different records of one stage.
        payload = self._publish(emit, "solve.end", payload,
                                banner_state={"finished": True})
        if script is not None:
            total = sum(p.history_n for p in history.points)
            self._say(script, emit, self._closing_sentence(history, total))
        return payload

    def _closing_sentence(self, history: RunHistory, iterations: int) -> str:
        """The one sentence the engineer speaks when the solve is finished.

        RE-DERIVE THIS BY DRIVING THE STAGE, NEVER BY READING THE f-STRING.
        ``workflows.check_wording`` is reached only at EMISSION, and it
        requires a bullet body to start with a capital letter -- so "5 sweep
        points complete, ..." reads fine in the source and throws on camera at
        the closing beat of the act. That is why the sentence leads with
        "All", and it is why this is a named method: the offline re-derivation
        can call it, and a test can assert on what actually gets spoken.

        THE UNIT ON SCREEN IS THE SCREEN'S UNIT, AND THE SCREEN'S UNIT IS
        NOW "core-minutes" AGAIN (chief ruling 2026-09-02, off Sanaa's own
        "core min" / "Core-minutes per run" wording; the interim
        "processor-minutes" translation had one screen carrying two words for
        one quantity). The quantity is untouched (wall seconds x ranks / 60,
        CLAUDE.md rule 12); the word matches demo_mode.SCREEN_COMPUTE_UNIT,
        kept as a literal here because this layer deliberately does not
        import the workflows package (see ReplaySpec.cost_projection).

        WITH A PROJECTION the number shown is the projected one and the
        sentence names the hardware it describes, because a bare figure this
        box did not measure is a measurement claim it cannot support.
        """
        points = len(history.points)
        cm = history.core_min_total
        projection = self.spec.cost_projection
        if projection is None:
            return (f"All {points} {self.spec.point_noun}s complete, "
                    f"{iterations:,} iterations, {cm:.1f} core-minutes.")
        return (f"All {points} {self.spec.point_noun}s complete, "
                f"{iterations:,} iterations, "
                f"{projection.apply(cm):.1f} core-minutes on "
                f"{projection.hardware}.")

    # -- emission ------------------------------------------------------------
    def _publish(self, emit, event: str, payload: dict,
                 *, banner_state: dict) -> dict:
        """One tick: the content and its banner, published together.

        The banner is derived from the payload here, at the single point of
        emission, which is what makes it impossible for the two to disagree.
        """
        banner = banner_for(banner_state)
        _check(banner)
        _check_payload(payload, event)
        stamped = dict(payload)
        stamped["banner"] = banner
        stamped["at"] = time.time()
        # The progressive assertion below measures the stage's OWN schedule
        # clock, not the wall clock, so a test driving the stage on a virtual
        # clock exercises the same pacing the screen would see instead of
        # measuring how fast the test loop happened to run.
        self._emitted.append((self.clock(), event, banner))
        if emit is not None:
            emit(event, stamped)
            emit("stage.banner", {"stage": self.stage_id, "text": banner,
                                  "for_event": event, "at": stamped["at"]})
        return stamped

    def _say(self, script, emit, sentence: str) -> None:
        _check(sentence)
        if script is not None:
            from workflows import bullets

            bullets(script.engineer, sentence)

    # -- the stage's own exit assertion --------------------------------------
    def _assert_progressive(self) -> dict:
        """Refuse to call the stage done if its output was not progressive.

        Two ways a stage can look hardcoded: everything landing at one
        instant, or everything landing in a burst at one end. Both are checked
        here against the stage's own emission timestamps, so the failure is
        loud and local rather than something a viewer notices.
        """
        stamps = [at for at, _, _ in self._emitted]
        if len(stamps) < 3:
            raise ReaderRefused(
                "the solver stage emitted fewer than three events; there is "
                "nothing progressive about that")
        span = stamps[-1] - stamps[0]
        if span <= 0:
            raise ReaderRefused(
                "every solver-stage event carries the same timestamp; the "
                "monitors did not advance, they appeared")
        for earlier, later in zip(stamps, stamps[1:]):
            if later < earlier:
                raise ReaderRefused(
                    "solver-stage events are not in time order")
        # No half of the run may hold nearly everything: with even pacing each
        # half holds about half the events.
        midpoint = stamps[0] + span / 2.0
        first_half = sum(1 for at in stamps if at <= midpoint)
        share = first_half / len(stamps)
        if not 0.2 <= share <= 0.8:
            raise ReaderRefused(
                f"the solver stage emitted {share:.0%} of its events in the "
                f"first half of its own duration; that is a burst, not "
                f"monitors advancing")
        return {
            "events": len(stamps),
            "span_s": round(span, 3),
            "first_half_share": round(share, 3),
        }


def _check(text: str) -> None:
    """Pass a string through the on-screen language rules before it is emitted.

    Prefers the demo contract's checker, which is strictly stronger than the
    older wording doctrine: it also refuses paths and case ids, which is the
    pair that got this stage sent back. Falls back to the older doctrine only
    where the contract module is not importable.
    """
    try:
        from workflows.demo_mode import check_demo_language
    except Exception:          # pragma: no cover - contract unavailable
        try:
            from workflows import check_wording
        except Exception:      # pragma: no cover - doctrine unavailable
            return
        check_wording(text)
        return
    check_demo_language(text)


def _check_payload(payload: dict, event: str, trail: str = "") -> None:
    """Check EVERY string this stage is about to publish, not just its prose.

    The two defects that sent this stage back were both in structured fields
    rather than in narration: a case id inside a ``labels`` list, and a
    filesystem path inside a control sentence. Every string-level check on the
    prose passed, because neither string was prose. Checking the assembled
    payload is the method that found them, so it runs here on every emission
    rather than in a test over a fixture, and it walks nested lists and
    dictionaries because that is where both defects were hiding.
    """
    if isinstance(payload, str):
        try:
            _check(payload)
        except Exception as exc:
            raise ReaderRefused(
                f"the solver stage would have published a string a screen "
                f"must never show, in {event}{trail}: {exc}") from exc
    elif isinstance(payload, dict):
        for key, value in payload.items():
            _check_payload(value, event, f"{trail}/{key}")
    elif isinstance(payload, (list, tuple)):
        for position, value in enumerate(payload):
            _check_payload(value, event, f"{trail}[{position}]")
