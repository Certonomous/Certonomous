"""DEMO MODE — the stage sequencer.

One walk through :data:`demo_mode.STAGES`, for all four acts. Sanaa: "every
stage renders in its normal place and its normal order. The only difference
from a fresh run is that the solver stage replays the stored logs at
accelerated pace instead of computing."

The act supplies facts (:class:`demo_mode.DemoAct`); this module supplies
order, pacing, banners and wording mechanics. An act emits nothing.

THREE INVARIANTS, ENFORCED CENTRALLY RATHER THAN PER STAGE
----------------------------------------------------------
Each is a defect class that has already cost this lab a screen, and each is
asserted in ONE place here so a later stage cannot reintroduce it:

1. **The banner is a pure function of the content, published in the same
   tick.** Not a synchronised pair — a single fact rendered twice. Set on
   stage entry, a banner has a second source and drifts; derived at the point
   of publication from the very dictionary being published, it cannot. The
   pattern is the replay stage's (``chief_engineer.replay_stage.banner_for``),
   adopted wholesale, and its solving banner is delegated to it rather than
   reimplemented.

2. **A stage returns the dictionary it published.** The replay lane found this
   in itself: its first cut asserted progressiveness after publishing, so the
   record the caller read and the event the screen received carried different
   fields. That reproduces at every stage boundary, so :meth:`_publish` returns
   the stamped payload and :func:`run_act` asserts the stage handed back
   exactly what went out.

3. **Every payload passes :func:`demo_mode.assert_screen_safe` at
   publication** — including the ones this module generates: banners, stage
   headers, progress lines. The case id that reached a screen through a
   published ``labels`` list arrived from a payload nobody thought of as text.

PACING
------
``control_room.html`` already owns an ordered paced reveal queue with a FAST
mode that "replays at the real inter-event timing, clamped to a watchable
band". This module does not add a second notion of pacing; it stamps each
publication from an injectable clock and lets that queue reveal it. What it
does assert is that a stage never emitted its whole content in one instant.

``sleep`` and ``clock`` are injectable, so a harness drives a whole act in
microseconds without changing one published value.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from .demo_mode import (BANNERS, STAGES, DemoAct, DemoContractError,
                        assert_screen_safe, check_running_line, cost_line,
                        registered_acts, validate_act)

__all__ = ["Sequencer", "run_act", "banner_for_stage", "SequencerRefused"]


class SequencerRefused(RuntimeError):
    """The sequencer will not start, or will not continue, this act.

    Distinct from :class:`demo_mode.DemoContractError`, which is an authorship
    fault in the act. This is the sequencer refusing to put something on a
    screen: a failed validation, a broken invariant, a stage that returned a
    record other than the one it published.
    """


# ---------------------------------------------------------------------------
# The banner, as a pure function of what is on screen
# ---------------------------------------------------------------------------

def banner_for_stage(state: dict) -> str:
    """The banner text for a stage's published state. No side effects.

    Called with the same dictionary that is published, so the banner and the
    content are two renderings of one fact. The solving stage's banner is not
    computed here: it belongs to the replay stage, which already derives it
    from the frame, and one banner with two implementations is exactly the
    drift this shape exists to prevent.
    """
    stage = state.get("stage")
    if stage == "solving":
        from chief_engineer.replay_stage import banner_for

        return banner_for(state)
    return BANNERS.get(str(stage), "")


# ---------------------------------------------------------------------------
# The sequencer
# ---------------------------------------------------------------------------

@dataclass
class Sequencer:
    """Walks one act through the nine stages, once, in order."""

    act: DemoAct
    sleep: Callable[[float], None] = time.sleep
    clock: Callable[[], float] = time.monotonic
    #: Screen seconds each non-solving stage occupies. The solving stage paces
    #: itself from its own spec.
    seconds_per_stage: float = 3.0

    _emitted: list = field(default_factory=list, init=False, repr=False)
    _published: list = field(default_factory=list, init=False, repr=False)

    # -- the one publication point -----------------------------------------
    def _publish(self, emit, event: str, payload: dict) -> dict:
        """Publish one fact and its banner together, and return what went out.

        Every payload this act produces passes through here, so the three
        invariants hold by construction rather than by each stage remembering
        them.
        """
        stamped = dict(payload)
        stamped["banner"] = banner_for_stage(stamped)
        assert_screen_safe(stamped)
        banner_payload = {"stage": stamped.get("stage"),
                          "text": stamped["banner"],
                          "for_event": event}
        # INVARIANT 3 applies to the payloads this module generates too, and
        # the banner is one of them. Assembling a whole act and guarding what
        # it really published found this unguarded: the case id that reached a
        # screen arrived from a payload nobody thought of as text, and a
        # banner is exactly such a payload.
        assert_screen_safe(banner_payload)
        if emit is not None:
            emit(event, stamped)
            emit("stage.banner", banner_payload)
        self._emitted.append((self.clock(), event, stamped["banner"]))
        self._published.append(stamped)
        return stamped

    def _guarded(self, emit):
        """Wrap a delegated stage's emit so INVARIANT 3 has no bypass.

        A stage this module delegates to publishes on its own emit and so
        never passes through :meth:`_publish`. Measured on the assembled
        jet-flap act, that bypass carried ten strings a screen must never
        show: five raw case ids on ``solve.point.begin``, and five planted-
        control sentences on ``solve.point.end`` each ending in a full
        filesystem path. Both are on her never-list, and both would have
        rendered.

        The guard REFUSES rather than rewriting. A sequencer that quietly
        stripped a case id out of another stage's payload would leave the
        defect in that stage, and the next caller would ship it.
        """
        if emit is None:
            return None

        def guarded(name, payload):
            assert_screen_safe(payload)
            emit(name, payload)

        return guarded

    def _say(self, script, line: str, *, tense: str) -> None:
        """Speak one line, tense-checked before it can be spoken."""
        check_running_line(line, tense=tense)
        if script is not None:
            from . import bullets

            bullets(script.engineer, line)

    def _beat(self) -> None:
        """Let a stage occupy screen time. Nothing appears all at once."""
        self.sleep(self.seconds_per_stage)

    # -- the walk -----------------------------------------------------------
    def run(self, emit=None, script=None) -> dict:
        """Walk the nine stages. Returns the record of what was published."""
        problems = validate_act(self.act)
        if problems:
            raise SequencerRefused(
                "this act does not satisfy the demo-mode contract, so nothing "
                "is put on screen: " + "; ".join(problems))

        record = self.act.run_record()
        census = dict(self.act.agent_census())
        stages: dict[str, dict] = {}

        for stage in STAGES:
            self._publish(emit, "stage.begin", {
                "stage": stage,
                "agents": census.get(stage, 0),
            })
            handler = getattr(self, f"_stage_{stage}")
            published = handler(emit, script, record)
            if published is not None:
                # INVARIANT 2, asserted centrally.
                if published not in self._published:
                    raise SequencerRefused(
                        f"stage {stage!r} returned a record that was never "
                        f"published; a caller and a screen would be reading "
                        f"two different accounts of one stage")
                stages[stage] = published
            self._beat()

        self._assert_not_all_at_once()
        return {"stages": stages, "emitted": len(self._emitted)}

    # -- the nine stages ----------------------------------------------------
    def _stage_prompt(self, emit, script, record) -> dict:
        prompt = self.act.prompt()
        return self._publish(emit, "demo.prompt",
                             {"stage": "prompt", "text": prompt.text})

    def _stage_restatement(self, emit, script, record) -> dict:
        r = self.act.restatement()
        return self._publish(emit, "demo.restatement", {
            "stage": "restatement",
            "restatement": r.restatement,
            "confidence": r.confidence,
            "estimate": r.cost_estimate.on_screen(),
        })

    def _stage_assumption(self, emit, script, record) -> dict:
        a = self.act.assumption()
        payload = {"stage": "assumption", "assumption": a.assumption,
                   "finding": a.finding}
        if a.correction:
            payload["correction"] = a.correction
        return self._publish(emit, "demo.assumption", payload)

    def _stage_geometry(self, emit, script, record) -> dict:
        g = self.act.geometry()
        mesh = self.act.mesh_plan()
        # Refuses here, on its own stage, rather than letting a later stage
        # render a sentence the measurement does not support.
        sentence = g.solved_geometry_sentence(mesh.cell_count)
        from . import announce_geometry

        announce_geometry(emit, name=g.served_stl.name, label=g.display_label)
        return self._publish(emit, "demo.geometry", {
            "stage": "geometry",
            "label": g.display_label,
            "statement": sentence,
        })

    def _stage_meshing(self, emit, script, record) -> dict:
        """The real mesher, its wall-layer zoom and its resolution table.

        The cell-by-cell draw is a separate renderer and is NOT a gate on this
        stage: with it absent the stage still runs the mesher and still shows
        the measured resolution table and wall-layer zoom, which are the
        numbers a reader needs. ``drawn`` says which of the two happened, so
        nothing on screen implies a draw that did not occur.
        """
        mesh = self.act.mesh_plan()
        self._say(script, "Meshing", tense="progressive")
        from . import emit_table

        if script is not None:
            emit_table(emit, script, role="NUMERICIST",
                       title="Wall and slot resolution",
                       headers=list(mesh.resolution_headers),
                       rows=[list(r) for r in mesh.resolution_rows],
                       table_id="mesh_resolution")
        return self._publish(emit, "demo.mesh", {
            "stage": "meshing",
            "cells": mesh.cell_count.on_screen(),
            "zoom": mesh.wall_zoom_hint,
            "drawn": False,
        })

    def _stage_feasibility(self, emit, script, record) -> dict:
        f = self.act.feasibility()
        return self._publish(emit, "demo.feasibility", {
            "stage": "feasibility",
            "check": f.check,
            "result": f.result.on_screen(),
            "verdict": f.verdict_for_user,
        })

    def _stage_solving(self, emit, script, record) -> dict:
        """Delegated whole to the replay stage, which owns the plants.

        Its ``prepare()`` runs every planted control BEFORE a frame moves, so
        a reader that cannot see its plant refuses while the screen is still
        on the previous stage. That placement is deliberate and is preserved
        here by calling prepare separately from run.
        """
        replay = self.act.solve_replay()
        if not replay.cases:
            raise SequencerRefused(
                "the solving stage has no cases to read; an act with no cases "
                "must say how its logs are read before it can be shown")
        from chief_engineer.replay_stage import ReplaySpec, ReplayStage

        stage = ReplayStage(
            spec=ReplaySpec(cases=list(replay.cases),
                            seconds_per_point=max(
                                replay.pace * 9.0, 0.001)),
            sleep=self.sleep, clock=self.clock)
        stage.prepare()
        published = stage.run(emit=self._guarded(emit), script=script)
        clock = replay.clock()
        self._publish(emit, "demo.elapsed", {
            "stage": "solving",
            "elapsed": clock.on_screen(),
            "finished": True,
        })
        self._published.append(published)
        return published

    def _stage_gates(self, emit, script, record) -> dict:
        g = self.act.gates()
        from . import emit_table

        if script is not None:
            emit_table(emit, script, role="NUMERICIST",
                       title=g.planted_checks.title,
                       headers=list(g.planted_checks.headers),
                       rows=[list(r) for r in g.planted_checks.rows],
                       table_id=g.planted_checks.table_id)
        return self._publish(emit, "demo.gates", {
            "stage": "gates",
            "grid": g.grid_statement,
        })

    def _stage_results(self, emit, script, record) -> dict:
        r = self.act.results()
        replay = self.act.solve_replay()
        from . import announce_plot, emit_table

        for figure in list(r.fields) + list(r.plots):
            announce_plot(emit, "results", figure.path, figure.title)
        if script is not None:
            for table in r.tables:
                emit_table(emit, script, role=table.role, title=table.title,
                           headers=list(table.headers),
                           rows=[list(row) for row in table.rows],
                           table_id=table.table_id)
        return self._publish(emit, "demo.results", {
            "stage": "results",
            "solver": record.solver_header(),
            "verification": list(r.verification_lines),
            "limitations": list(r.limitations),
            "cost": cost_line(replay.core_minutes()),
            "estimate": r.cost_estimate_from_stage_2.on_screen(),
        })

    # -- pacing -------------------------------------------------------------
    def _assert_not_all_at_once(self) -> None:
        """Refuse an act whose content arrived in a single instant.

        Not a style rule: a burst means the paced queue had nothing to pace,
        and the viewer sees a finished page rather than a run.
        """
        instants = {round(t, 6) for t, _, _ in self._emitted}
        if len(self._emitted) > 1 and len(instants) == 1:
            raise SequencerRefused(
                f"all {len(self._emitted)} publications carried one instant; "
                f"the screen would pop rather than run")


def run_act(key_or_act, emit=None, script=None, **kwargs) -> dict:
    """Resolve an act by key (or take one directly) and walk it."""
    act = key_or_act
    if isinstance(key_or_act, str):
        try:
            act = registered_acts()[key_or_act]
        except KeyError:
            raise SequencerRefused(
                f"no act is registered as {key_or_act!r}") from None
    if not isinstance(act, DemoAct):
        raise DemoContractError(
            f"{type(act).__name__} does not implement DemoAct")
    return Sequencer(act=act, **kwargs).run(emit=emit, script=script)
