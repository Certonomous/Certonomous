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

   **This invariant was stated here and not held.** Five delegated
   publications took the RAW ``emit`` and so never met the guard: the geometry
   announcement, the meshing resolution table, the gates planted-check table,
   the results figure announcements and the results tables. Between them they
   carry every TABLE CELL and every FIGURE TITLE the act shows, and ``Table``
   and ``MeshPlan`` validate their titles and headers but NOT their rows, so a
   bad cell was constructible with nothing between it and the screen.

   It is now held by construction rather than by five patches.
   :meth:`Sequencer.run` wraps ``emit`` ONCE in :meth:`Sequencer._guarded` and
   hands only the wrapper down, so no stage ever holds the raw emit and a
   sixth delegated publication cannot be added unguarded — there is nothing
   left to get wrong. :meth:`Sequencer._publish` refuses an emit that does not
   carry :data:`GUARD_MARK`, so the wrapping is checked and not assumed. The
   planted controls that drive the guard to its refusal, one per forbidden
   class per site, are ``tests/test_demo_sequencer_guard.py``: a guard that is
   called but cannot abort is worse than one that is absent.

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

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .demo_mode import (BANNERS, STAGES, DemoAct, DemoContractError,
                        assert_screen_safe, check_running_line, cost_line,
                        registered_acts, screen_refusal_class,
                        translate_chips, validate_act)


#: The mesh slicer, loaded from the repository script that owns it. Loaded BY
#: EXPLICIT PATH rather than by import, the same way ``_jf1_geometry`` reaches
#: the surface generator: the implementation belongs beside the other repository
#: scripts, and a second copy vendored into this package would be a copy free to
#: drift from the one a person runs by hand. A moved tree returns None and the
#: meshing stage simply shows no grid.
_SLICER_SOURCE = Path("/home/ubuntu/Certonomous/scripts/polymesh_slice_payload.py")
_slicer_cache: list = []


def _load_slicer():
    if _slicer_cache:
        return _slicer_cache[0]
    module = None
    if _SLICER_SOURCE.is_file():
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "polymesh_slice_payload", _SLICER_SOURCE)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception:                                  # noqa: BLE001
                module = None
    _slicer_cache.append(module)
    return module


def _translated(node):
    """Render every fidelity chip in a payload as its plain-English meaning.

    TRANSLATE, NEVER STRIP, and note the deliberate asymmetry with the case
    ids the guard refuses outright. A chip carries real information about how
    well a number is backed, so deleting it makes the screen say less than the
    lab knows and the honest move is to say what it means. A case id carries
    no meaning a viewer can use, so rewriting it here would only hide a defect
    that belongs to the stage that minted it.
    """
    if isinstance(node, dict):
        return {k: _translated(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_translated(v) for v in node]
    if isinstance(node, tuple):
        return tuple(_translated(v) for v in node)
    return translate_chips(node)

__all__ = ["Sequencer", "run_act", "banner_for_stage", "SequencerRefused",
           "GUARD_MARK", "figure_namespace"]

#: A figure NAMESPACE is one segment of the served URL, and it is a DIRECTORY
#: NAME rather than prose. ``announce_plot`` composes
#: ``/api/plot/<namespace>/<file>``; ``chief_engineer.server._serve_artifact``
#: splits that into exactly four segments and resolves it as
#: ``<output root>/<namespace>/<file>``, refusing anything that escapes the
#: root. So a namespace with a slash, a leading dot or a space does not reach a
#: 404 -- it reaches a URL the server cannot even parse -- and the act that
#: minted it would never learn.
_NAMESPACE_SHAPE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def figure_namespace(figure) -> str:
    """The namespace one figure publishes under: the ACT'S OWN declaration.

    THE DEFECT THIS REPLACES, measured rather than reported. The results stage
    passed the literal string ``"results"`` to ``announce_plot`` for every
    figure of every act, and :class:`demo_mode.Figure` carries a ``beat`` field
    that was read by nothing. Two consequences, and the second is the one that
    was missed:

    * an act declaring any other namespace had that declaration DISCARDED, so
      its figures were advertised under a namespace it never chose;
    * and because the results stage also staged nothing, ``<output root>``
      held no ``results/`` directory at all -- so the URL did not resolve for
      ANY act, the jet-flap act included. Measured on the assembled jet-flap
      results stage before this change: four of four figure URLs answered 404,
      against a planted control URL that answered 200 from the same resolver.

    Deriving the namespace is therefore only half a fix. The other half is
    :meth:`Sequencer._stage_figure`, which puts the file where the derived URL
    says it is; a namespace nothing serves from is a tidier 404.
    """
    beat = str(getattr(figure, "beat", "") or "").strip()
    if not beat:
        raise SequencerRefused(
            "a figure published from the results stage declares the namespace "
            "it is served under; this one declares none, so the screen would "
            "advertise a picture at an address nobody chose")
    if beat in {".", ".."} or not _NAMESPACE_SHAPE.match(beat):
        raise SequencerRefused(
            "a figure namespace is one directory name under the served root; "
            "this act declared one that is not, so the address would not "
            "resolve and the failure would be invisible to the act")
    return beat

#: The attribute :meth:`Sequencer._guarded` stamps on the wrapper it returns.
#: It makes "this emit has been through the guard" a fact that can be READ,
#: which is what lets :meth:`Sequencer._publish` refuse an unguarded one and
#: what lets the wrap be idempotent instead of nesting 605 frames deep.
GUARD_MARK = "_demo_sequencer_guarded"


def _as_count(value) -> int | None:
    """A cell count as an integer, however the act chose to record it.

    An act records a :class:`demo_mode.Measured` value in whatever form it
    read or shows, and the jet-flap act records its cell count as the string
    it displays, commas and all. ``int("39,984")`` raises, which would have
    turned the live-mesh check into an exception rather than a comparison.
    Returns ``None`` when the value is not a count at all, so the caller
    refuses rather than silently skipping the check.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    try:
        return int(round(float(str(value).replace(",", "").strip())))
    except (TypeError, ValueError):
        return None


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
    #: WHAT THE USER ACTUALLY TYPED, shown on the prompt stage in place of the
    #: act's registered prompt. ``None`` keeps the act's own wording, which is
    #: right for a scripted rehearsal and wrong for a live user.
    #:
    #: Measured before it was added: an act registers its prompt verbatim and
    #: the prompt stage published THAT string whatever was typed, so a viewer
    #: who paraphrased saw canned text echoed back as if it were their own
    #: words, silently and with no mismatch shown. Sanaa's standard is "exactly
    #: like what a user would experience if they were running the case"; a
    #: screen quoting someone words they did not write is the most
    #: recorded-looking thing this act could do, and it fails in front of the
    #: one person able to tell.
    #:
    #: The act's own wording is NOT threaded from here — the typed string sets
    #: the prompt line and nothing else. Every other sentence stays the act's,
    #: so a prompt still cannot reword a screen fixed by directive.
    typed_prompt: str | None = None

    _emitted: list = field(default_factory=list, init=False, repr=False)
    _published: list = field(default_factory=list, init=False, repr=False)

    # -- the one publication point -----------------------------------------
    def _publish(self, emit, event: str, payload: dict) -> dict:
        """Publish one fact and its banner together, and return what went out.

        Every payload this act produces passes through here, so the three
        invariants hold by construction rather than by each stage remembering
        them.
        """
        stamped = _translated(dict(payload))
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
            # THE CHOKE POINT, ASSERTED RATHER THAN TRUSTED. A stage may only
            # ever hold the guarded emit (:meth:`run` wraps once and hands
            # that down), so an emit arriving here without the mark is an emit
            # that came from somewhere other than the walk. Refusing it is
            # what makes "no stage can obtain the raw emit" a property of the
            # code instead of a convention a later edit may not have read.
            if not getattr(emit, GUARD_MARK, False):
                raise SequencerRefused(
                    "a stage published on an emit that did not come through "
                    "the sequencer's guard; every publication is guarded, so "
                    "this one would have reached a screen unswept")
            emit(event, stamped)
            emit("stage.banner", banner_payload)
        self._emitted.append((self.clock(), event, stamped["banner"]))
        self._published.append(stamped)
        return stamped

    def _guarded(self, emit):
        """THE ONE PUBLICATION PATH. Wrap ``emit`` so nothing reaches a screen
        unswept, and mark the wrapper so the wrapping can be asserted.

        A stage this module delegates to publishes on its own emit and so
        never passes through :meth:`_publish`. Measured on the assembled
        jet-flap act, that bypass carried ten strings a screen must never
        show: five raw case ids on ``solve.point.begin``, and five planted-
        control sentences on ``solve.point.end`` each ending in a full
        filesystem path. Both are on her never-list, and both would have
        rendered.

        WHY A CHOKE POINT AND NOT FIVE PATCHED CALL SITES. Three independent
        readings of this file counted the delegated publications that took the
        RAW emit as four, five and five; the disputed one, the geometry
        announcement, is on the filmed path. A count that three careful
        readers disagree about is not a count to patch site by site, because
        patching the instances leaves the next author free to add a sixth.
        :meth:`run` therefore wraps ONCE and hands the guarded emit down, so
        no stage ever holds the raw one and there is nothing for a new call
        site to get wrong. :meth:`_publish` refuses an unmarked emit, which
        turns that from a convention into a check.

        IDEMPOTENT ON PURPOSE. Wrapping an already-guarded emit returns it
        unchanged rather than nesting: the solving stage walks 605 frames, and
        a second sweep of each would cost real screen time to re-answer a
        question already answered.

        The guard REFUSES rather than rewriting. A sequencer that quietly
        stripped a case id out of another stage's payload would leave the
        defect in that stage, and the next caller would ship it.
        """
        if emit is None:
            return None
        if getattr(emit, GUARD_MARK, False):
            return emit

        def guarded(name, payload):
            payload = _translated(payload)
            assert_screen_safe(payload)
            emit(name, payload)

        setattr(guarded, GUARD_MARK, True)
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
        """Walk the nine stages. Returns the record of what was published.

        THE RAW ``emit`` STOPS HERE. It is wrapped once, on the next line, and
        only the guarded wrapper is handed to the stages, so INVARIANT 3 has
        no bypass to close per call site and no sixth bypass to add.
        """
        problems = validate_act(self.act)
        if problems:
            raise SequencerRefused(
                "this act does not satisfy the demo-mode contract, so nothing "
                "is put on screen: " + "; ".join(problems))

        emit = self._guarded(emit)

        record = self.act.run_record()
        census = dict(self.act.agent_census())
        discussions = self._checked_discussions()
        stages: dict[str, dict] = {}

        # THE BODY IS ON SCREEN BEFORE THE FIRST WORD IS SPOKEN.
        #
        # Sanaa, 2026-09-01: "The uploaded STL renders the moment it is loaded
        # (no 'surface renders here once it lands', no 'no surface loaded'
        # during planning)." Measured before this: the only announcement was
        # inside the geometry stage, which is the FOURTH of nine, so a viewer
        # watched the prompt, the restatement and the assumption go by with an
        # empty stage carrying a line of placeholder prose where the body
        # belongs. The stage still does its own work -- it is the stage that
        # MEASURES the body against the solved section and refuses if they
        # disagree -- and nothing about that moves. This only puts the picture
        # up first, which is what a person who has just handed over a file
        # expects to see.
        # ONE ANNOUNCEMENT, NOT TWO. The geometry stage's own call is skipped
        # when this one lands (`self._announced`), because two announcements of
        # one body is two fetches of the same surface and a second cycle of the
        # viewport, and the live check counts them.
        self._announced = False
        try:
            body = self.act.geometry()
        except Exception:                                      # noqa: BLE001
            body = None       # the geometry stage will raise it properly, there
        if body is not None:
            # THE PANEL FIRST, AND THE CANVAS ONLY WHERE THERE IS NO PANEL.
            # Sanaa, 2026-09-01: "Going forward all acts use paraview." A
            # `geometry.ready` announcement is fetched and DRAWN by the page's
            # canvas; a rendered panel is the same body photographed off the
            # solved case. Where the act's cited grid has renders beside it the
            # canvas never runs, and where it has none the old path is left
            # exactly as it was rather than taking a working screen off the air.
            shown = None
            try:
                shown = self._publish_panel(
                    emit, self.act.mesh_plan(), "geometry", stage="geometry",
                    label=body.display_label)
            except SequencerRefused:
                raise
            except Exception:                                  # noqa: BLE001
                shown = None      # the geometry stage will raise it properly
            if shown is None:
                from . import announce_geometry

                announce_geometry(emit, name=body.served_stl.name,
                                  label=body.display_label,
                                  url=self._stage_surface(body))
            self._announced = True

        for stage in STAGES:
            self._publish(emit, "stage.begin", {
                "stage": stage,
                "agents": census.get(stage, 0),
            })
            handler = getattr(self, f"_stage_{stage}")
            published = handler(emit, script, record)
            self._speak_discussion(stage, script, discussions)
            # THE REPORT CLOSES THE ACT, AND IT CLOSES IT LAST. Fired from
            # inside the results stage it landed BEFORE that stage's own
            # discussion beat, so the Conclusion heading opened above a
            # specialist still talking about the numbers. Measured on the
            # assembled act, not reasoned: the numericist's closing entry
            # arrived at sequence 1292, three publications after the
            # Conclusion phase at 1289.
            if stage == STAGES[-1]:
                self._stage_closing(emit, script)
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

    # -- the expert-agent discussion ----------------------------------------
    def _checked_discussions(self) -> dict:
        """The act's discussion beats, validated BEFORE the screen lights.

        A beat keyed to a stage that does not exist is a beat that silently
        never plays, and the act's author would have no way to tell that from
        one that played and said nothing. So an unknown stage name and an
        unknown role are both refusals here, at validation time, with the
        screen still dark, in the same spirit as the rest of this sequencer.
        """
        beats = dict(self.act.discussions() or {})
        for stage, entries in beats.items():
            if stage not in STAGES:
                raise SequencerRefused(
                    f"the act keys a discussion beat to {stage!r}, which is "
                    f"not one of the act's stages, so it would never be "
                    f"spoken and nothing would say so")
            for role, lines in entries:
                if role not in DemoAct.DISCUSSION_ROLES:
                    raise SequencerRefused(
                        f"{role!r} is not a transcript role this act can "
                        f"speak as; the page gives each role its own accent "
                        f"and an unknown one would render as nobody")
                for line in lines:
                    check_running_line(line, tense="past")
        return beats

    def _speak_discussion(self, stage: str, script, beats: dict) -> None:
        """Speak the beats that belong to the stage just finished.

        AFTER the stage, not before: the geometry summary follows the geometry,
        the model choice follows the plan it belongs to, and the closing
        numerics follow the numbers. One bulleted entry per speaker, which is
        what makes consecutive beats read as a conversation between several
        agents rather than as one narrator changing subject.
        """
        if script is None:
            return
        from . import bullets

        for role, lines in beats.get(stage, ()):  # already validated
            bullets(getattr(script, role), *lines)

    # -- the nine stages ----------------------------------------------------
    def _stage_prompt(self, emit, script, record) -> dict:
        """Show what was typed, or the act's own prompt when nothing was.

        A FLAGGED TRADE-OFF, stated rather than buried: the typed string is
        published through :meth:`_publish` like every other payload, so a user
        who types a filesystem path or a case id makes the act REFUSE and the
        mission end as failed with the reason. The alternative — exempting the
        typed prompt from the guard — puts a hole in the one gate that stops
        internal identifiers reaching a screen, and the alternative to BOTH is
        the silent substitution this replaced. Refusing is the only one of the
        three that is honest, and it is the caller's to reconsider, not this
        stage's to soften.
        """
        prompt = self.act.prompt()
        typed = (self.typed_prompt or "").strip()
        if typed:
            # THE REFUSAL MUST NOT LEAK WHAT IT REFUSED. Everything else this
            # module publishes was written by the lab, so quoting it back is
            # how an author finds their own mistake. This one string was typed
            # by a user, and the refusal is published as the mission's failure
            # reason -- so letting check_demo_language's message through would
            # put the very path it refused onto the screen, through the guard
            # that exists to keep it off. Named by CLASS, never by value, and
            # chained with `from None` so the original message cannot follow
            # it out.
            bad = screen_refusal_class(typed)
            if bad is not None:
                raise SequencerRefused(
                    f"that request cannot be shown on screen because it "
                    f"contains {bad}; retype it without that part") from None
        return self._publish(emit, "demo.prompt",
                             {"stage": "prompt", "text": typed or prompt.text})

    def _stage_restatement(self, emit, script, record) -> dict:
        r = self.act.restatement()
        return self._publish(emit, "demo.restatement", {
            "stage": "restatement",
            "restatement": r.restatement,
            "confidence": r.confidence,
            "estimate": r.cost_estimate.on_screen(),
        })

    def _stage_assumption(self, emit, script, record) -> dict:
        """The assumption beat, and the table that says who chose what.

        THE TABLE IS EMITTED BEFORE THE PAYLOAD, so it lands above the
        correction that refers to it rather than under it. Sanaa's 20:30Z
        protocol puts it in the expert-discussion beat, which is where this
        stage sits, and it is a real table rather than prose because "every
        quantity with a value and unit" is a table's job.
        """
        a = self.act.assumption()
        if script is not None and a.assumptions_table is not None:
            from . import emit_table

            t = a.assumptions_table
            emit_table(emit, script, role=t.role, title=t.title,
                       headers=list(t.headers),
                       rows=[list(row) for row in t.rows],
                       table_id=t.table_id)
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
        # ALREADY ON SCREEN. :meth:`run` announces the body before the first
        # stage opens, so a viewer sees their surface through the planning
        # beats instead of a placeholder. Announcing it again here would be a
        # second fetch of the same file and a second cycle of the viewport for
        # no new fact. The stage's real work -- measuring the supplied body
        # against the solved section and refusing when they disagree -- is the
        # line above, and it is untouched.
        if not getattr(self, "_announced", False):
            from . import announce_geometry

            announce_geometry(emit, name=g.served_stl.name,
                              label=g.display_label,
                              url=self._stage_surface(g))
        return self._publish(emit, "demo.geometry", {
            "stage": "geometry",
            "label": g.display_label,
            "statement": sentence,
        })

    # -- the live mesher ----------------------------------------------------
    #: Directory contents that mean "this is a real case tree, not scratch".
    #: A time directory, a solver log or a controlDict all say a solve has
    #: lived here.
    _CASE_TELLS = ("system/controlDict", "constant/turbulenceProperties")

    def _unsafe_work_dir(self, work_dir) -> str | None:
        """Refuse to point a mesher at anything that looks like a real case.

        THE CONSTRAINT IS STRUCTURAL, NOT A COMMENT. The act's ``work_dir``
        used to be a landed, complete, graded run; a mesher writing a fresh
        ``constant/polyMesh`` into one destroys the provenance of a result
        that cannot be re-solved, because the strict completion rule's age
        guard turns on every field at ``endTime`` being newer than the case's
        own ``0/``. It has since been moved to a scratch directory, and the
        whole value of that move is lost if nothing checks it stayed moved.

        An absent mesh stage is recoverable. A corrupted graded case is not.

        Returns the reason it is unsafe, or ``None`` when meshing there is
        fine. It REPORTS rather than raises, because the answer differs by
        act: one act's stage having no safe scratch directory is that act's
        defect to fix, and killing it outright would take a working screen off
        the air to punish a misconfiguration. The caller skips the mesher and
        says on the payload that nothing was meshed.
        """
        from pathlib import Path

        work = Path(work_dir)
        for tell in self._CASE_TELLS:
            if (work / tell).exists():
                return (f"it looks like a real case directory (it holds "
                        f"{tell})")
        for child in work.glob("*"):
            if child.is_dir() and child.name not in {"constant", "system", "0"}:
                try:
                    float(child.name)
                except ValueError:
                    continue
                return f"it holds a solved time directory ({child.name})"
        return None

    def _live_cell_count(self, work_dir) -> int:
        """Cells in the mesh just written, READ OFF DISK.

        Not taken from the mesher's stdout: a generator that printed a count
        it did not write would be believed, and the whole point of running the
        mesher is that the screen shows a grid somebody built rather than a
        number somebody typed. ``owner`` lists the owning cell of every face,
        so the highest label plus one is the cell count.
        """
        from pathlib import Path

        owner = Path(work_dir) / "constant" / "polyMesh" / "owner"
        if not owner.is_file():
            raise SequencerRefused(
                "the mesher reported success but wrote no mesh, so the screen "
                "has no grid to show and says so rather than implying one")
        top = -1
        started = False
        for line in owner.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not started:
                if s == "(":
                    started = True
                continue
            if s == ")":
                break
            if s:
                try:
                    top = max(top, int(s))
                except ValueError:
                    continue
        if top < 0:
            raise SequencerRefused(
                "the mesh written by the mesher could not be read back")
        return top + 1

    def _run_mesher(self, mesh) -> int:
        """Run the act's real mesher and return the cell count it produced.

        Sanaa's directive: "Meshing runs live ... the real mesher on the
        uploaded STL". Before this, the stage spoke the word "Meshing" and ran
        nothing at all -- ``MeshPlan.command`` was declared by every act and
        invoked by nothing in the repository. A stage that says it is meshing
        while no mesher runs is the one thing on this screen that would be
        narrated as live and would not be.
        """
        import subprocess

        unsafe = self._unsafe_work_dir(mesh.work_dir)
        if unsafe is not None:
            # NOT AN EXCEPTION, AND THE ASYMMETRY IS DELIBERATE. Running the
            # mesher here could destroy a landed run that cannot be re-solved;
            # not running it costs a picture. So the mesher does not run, and
            # the stage says plainly that nothing was meshed rather than
            # implying a grid it did not build.
            return None
        try:
            done = subprocess.run(
                [str(part) for part in mesh.command],
                capture_output=True, text=True,
                timeout=max(float(mesh.expected_seconds) * 4.0, 30.0))
        except FileNotFoundError as exc:
            raise SequencerRefused(
                f"the meshing stage names a mesher that is not on this "
                f"machine, so nothing was meshed: {type(exc).__name__}"
            ) from None
        except subprocess.TimeoutExpired:
            raise SequencerRefused(
                "the mesher did not finish in four times its own forecast, so "
                "the stage stops rather than showing a part-built grid"
            ) from None
        if done.returncode != 0:
            raise SequencerRefused(
                f"the mesher exited {done.returncode}; the screen shows no "
                f"grid rather than a grid nobody built")

        live = self._live_cell_count(mesh.work_dir)
        # ``Measured.value`` is the value as the act recorded it, and an act is
        # free to record a cell count as the string it shows ("39,984").
        # Measured, not assumed: int() on that raises. Parsed defensively so a
        # comparison this stage exists to make cannot be skipped by a
        # formatting choice upstream.
        want = _as_count(mesh.cell_count.value)
        if want is None:
            raise SequencerRefused(
                "the act's declared cell count cannot be read as a number, so "
                "the live mesh cannot be checked against the solved grid")
        # A LIVE MESH THAT DOES NOT REPRODUCE THE SOLVED GRID IS A FINDING.
        # The pressures, the lift table and the fields all come from the
        # solved grid; a stage that meshed something ELSE and showed it would
        # put a picture of one grid beside numbers from another.
        if abs(live - want) > float(mesh.cell_tolerance) * max(want, 1):
            raise SequencerRefused(
                f"the mesher built {live:,} cells where the solved grid has "
                f"{want:,}; the screen will not show a grid that is not the "
                f"one the numbers came from")
        return live

    def _stage_meshing(self, emit, script, record) -> dict:
        """The real mesher, its wall-layer zoom and its resolution table.

        THE MESHER NOW ACTUALLY RUNS. Measured before this: nothing in the
        repository ever invoked ``MeshPlan.command`` -- the only references to
        it were its own emptiness check and a comment -- so this stage spoke
        the progressive line "Meshing", published ``drawn: False``, and meshed
        nothing. Against a directive reading "Meshing runs live ... the real
        mesher on the uploaded STL", that is the one stage that was out of
        compliance, and it is the stage a narrator would call live.

        It meshes into ``MeshPlan.work_dir`` and refuses outright if that
        looks like a real case tree. The cell count is READ BACK off the mesh
        just written and checked against the solved grid, so the picture and
        the numbers are the same grid.

        ``drawn`` REPORTS THE CELL-BY-CELL DRAW AND IT IS NOW TRUE WHEN THE
        DRAW HAPPENED, and False when it did not, which is the only reason to
        publish the key at all. :meth:`_grid_payload` serves the grid the
        SOLVED case actually holds; when it cannot -- no solved grid cited, not
        a 2-D case, a mesh it will not slice honestly -- the key stays False
        and the stage says no more than it did before.
        """
        mesh = self.act.mesh_plan()
        self._say(script, "Meshing", tense="progressive")
        from . import emit_table

        live_cells = self._run_mesher(mesh)
        if script is not None:
            emit_table(emit, script, role="NUMERICIST",
                       title="Wall and slot resolution",
                       headers=list(mesh.resolution_headers),
                       rows=[list(r) for r in mesh.resolution_rows],
                       table_id="mesh_resolution")
        # THE RENDERED PANELS COME FIRST AND THE CANVAS ONLY WHERE THERE ARE
        # NONE. The cell-by-cell draw is retired as a visual source by
        # directive; :meth:`_panel` re-establishes, as an assertion, the
        # count-to-picture coupling that the draw held by construction. The
        # canvas payload is still built for an act whose cited grid carries no
        # renders, because showing no grid at all would be a worse screen than
        # the one being replaced.
        printed = _as_count(mesh.cell_count.value)
        wide = self._panel(mesh, "mesh")
        close = self._panel(mesh, "mesh_zoom")
        panels = [p for p in (wide, close) if p is not None]
        grid = self._grid_payload(mesh) if not panels else None
        payload = {
            "stage": "meshing",
            "cells": mesh.cell_count.on_screen(),
            "zoom": mesh.wall_zoom_hint,
            "meshed": live_cells is not None,
            # ``drawn`` still reports the cell-by-cell DRAW and nothing else, so
            # it stays False when the grid is shown as a rendered panel. That is
            # not a downgrade of the screen: ``pictured`` is the key that says
            # the viewer saw the grid, and keeping the two apart is what stops a
            # later reader concluding the canvas ran when it did not.
            "drawn": grid is not None,
            "pictured": grid is not None or bool(panels),
        }
        if live_cells is not None:
            payload["meshed_cells"] = f"{live_cells:,}"
        published = self._publish(emit, "demo.mesh", payload)
        if grid is not None:
            self._publish(emit, "mesh.grid", dict(grid, stage="meshing"))
        # THE REVEAL IS PRESERVED BY SEQUENCING FRAMES. The draw built outward
        # off the wall, held, then eased into the slot; two panels published in
        # order are the same three beats -- the whole grid, then the wall layers
        # at the slot -- and the page holds each one on its own beat.
        label = "the grid the numbers on this screen are computed on"
        if wide is not None:
            self._publish(emit, "mesh.panel", dict(
                wide, stage="meshing", label=label,
                caption=f"{printed:,} cells." if printed is not None else ""))
        if close is not None:
            self._publish(emit, "mesh.panel", dict(
                close, stage="meshing", label=label,
                caption=f"Closing on {mesh.wall_zoom_hint}."))
        return published

    #: Where a served grid is written. Under the output root because that is
    #: the only tree the control-room server will serve a JSON body from, and
    #: it is a served copy of a run's mesh rather than the run's own tree --
    #: nothing here ever writes into a landed case.
    GRID_DIR = "demo-grid"

    def _grid_payload(self, mesh) -> dict | None:
        """The solved grid, one quadrilateral per cell, ready to be drawn.

        THE GRID IS THE ONE THE NUMBERS COME FROM, and that is the whole
        safety property. It is read from ``MeshPlan.cell_count.source`` -- the
        artifact the act already cites for the cell count it puts on screen --
        so a picture of some other grid cannot reach the stage without the
        count beside it moving too. This campaign has two grids whose
        reference areas differ by a hundred; a mesh picture sourced
        independently of the count is exactly how they would get mixed.

        IT IS NOT THE GRID THE MESHER JUST BUILT, and the difference matters.
        The mesher writes into a scratch tree and its output is checked
        against the solved grid's cell count (see :meth:`_run_mesher`); the
        SOLVED grid is the one the lift table was integrated on. Drawing the
        scratch copy would put a picture on screen whose provenance is a
        temporary directory.

        Returns ``None`` for anything it cannot do honestly -- no cited mesh, a
        source that is not a ``polyMesh``, a case that is not one cell thick.
        A stage that shows no grid is a stage that shows no grid; a stage that
        shows the wrong one is unrecoverable.
        """
        source = getattr(mesh.cell_count, "source", None)
        if source is None:
            return None
        poly = Path(source)
        if poly.name != "polyMesh" or not poly.is_dir():
            return None
        import json

        slicer = _load_slicer()
        if slicer is None:
            return None
        # THE BODY PATCH IS THE ACT'S TO NAME. Left unnamed the slicer looks
        # for ``airfoil``, finds nothing on a case that calls its wall
        # something else, and frames the whole domain in place of the wall the
        # zoom sentence promises.
        kwargs = {}
        if getattr(mesh, "wall_patch", None):
            kwargs["wall_patch"] = mesh.wall_patch
        try:
            payload = slicer.slice_payload(poly, **kwargs)
        except (slicer.SliceRefused, OSError, ValueError):
            return None
        from . import OUT_ROOT

        out = Path(OUT_ROOT) / self.GRID_DIR
        out.mkdir(parents=True, exist_ok=True)
        name = f"grid_{payload['cells']}.json"
        (out / name).write_text(json.dumps(payload, separators=(",", ":")))
        return {
            "url": f"/api/field/{self.GRID_DIR}/{name}",
            "cells": payload["cells"],
            "label": "the grid the lift and the pressures are computed on",
            "caption": f"{payload['cells']:,} cells, drawn one at a time, "
                       f"closing on {mesh.wall_zoom_hint}.",
        }

    # -- the rendered panels ------------------------------------------------
    #: Where a served ParaView panel is written. Under the output root because
    #: that is the only tree the control-room server serves from, and it is a
    #: served COPY of a run's render rather than the run's own tree -- nothing
    #: here ever writes into a landed case.
    PANEL_DIR = "demo-panels"

    #: The panels a case's ParaView render writes, and the screen-safe name
    #: each is served under. The rendered files are named after their case, and
    #: a case id is on the never-list; the served copy therefore carries a name
    #: a viewer could read without learning anything internal.
    PANEL_NAMES = {"geometry": "surface", "mesh": "grid",
                   "mesh_zoom": "grid_zoom",
                   "field_u": "field_velocity", "field_p": "field_pressure"}

    def _panel(self, mesh, panel: str, namespace: str | None = None) -> dict | None:
        """One rendered panel of the SOLVED case, or a refusal, or nothing.

        WHAT THIS REPLACES, AND THE PROPERTY IT HAD TO PUT BACK.
        :meth:`_grid_payload` derived the grid from ``MeshPlan.cell_count.source``
        -- the same artifact the on-screen cell count cites -- and that coupling
        is what made a wrong-grid picture impossible without the printed count
        moving too. It IS the 39,984-versus-46,180 guard: two grids on
        reference areas of 0.01 and 1.0, so mixing them misreports lift by a
        hundred.

        A rendered image cannot carry a cell list, so the coupling cannot
        survive as construction. It survives as an ASSERTION over three
        independent readings of one number, and this refuses unless all three
        agree:

          * the count the act PRINTS (``cell_count.value``);
          * the count the polyMesh the act cites actually holds, read off
            ``owner`` here and now (:meth:`_live_cell_count`);
          * the count the panel's own provenance sidecar records.

        The sidecar's declared case must also be the case the count cites, so a
        panel rendered from a neighbouring run cannot be served under this
        one's number.

        THE PANEL IS FOUND THROUGH THE CITED ARTIFACT, never through a path of
        its own. The paraview directory is located from ``cell_count.source``,
        so pointing the act at another case moves the count and the pictures
        together, exactly as before.

        Returns ``None`` for anything it cannot do honestly -- no cited mesh, no
        render beside it -- and RAISES for anything it can measure and finds
        wrong. The difference matters: an act with no panels is an act with no
        panels, and an act whose panel disagrees with its own number is a
        finding.
        """
        import json
        import shutil

        source = getattr(mesh.cell_count, "source", None)
        if source is None:
            return None
        poly = Path(source)
        if poly.name != "polyMesh" or not poly.is_dir():
            return None
        case = poly.parent.parent
        shot = case / "paraview" / f"{case.name}_{panel}.png"
        side = shot.with_suffix(".json")
        if not (shot.is_file() and side.is_file()):
            return None

        printed = _as_count(mesh.cell_count.value)
        if printed is None:
            raise SequencerRefused(
                "the act's declared cell count cannot be read as a number, so "
                "the picture cannot be checked against it")
        try:
            record = json.loads(side.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise SequencerRefused(
                "a rendered panel has no readable provenance beside it; a "
                "picture whose grid cannot be named does not go on camera"
            ) from None
        claimed = record.get("cells")
        if not isinstance(claimed, int) or claimed != printed:
            raise SequencerRefused(
                f"the rendered panel records {claimed} cells and the screen "
                f"prints {printed:,}; the picture and the number beside it "
                f"are two different grids")
        declared = record.get("case")
        if declared is None or Path(declared).resolve() != case.resolve():
            raise SequencerRefused(
                "the rendered panel names a case other than the one the "
                "on-screen cell count is read from; the picture and the "
                "number would describe two different runs")
        # Cached per case: `owner` lists one label per face, so on this grid it
        # is 79,000 lines, and five panels would read it five times for one
        # answer that cannot change between them.
        cache = getattr(self, "_disk_cells", None)
        if cache is None:
            cache = self._disk_cells = {}
        key = str(case.resolve())
        if key not in cache:
            cache[key] = self._live_cell_count(case)
        on_disk = cache[key]
        if on_disk != printed:
            raise SequencerRefused(
                f"the grid the screen cites now holds {on_disk:,} cells and "
                f"the screen prints {printed:,}; the panel was rendered "
                f"before the case it cites changed under it")

        from . import OUT_ROOT

        # THE ACT'S OWN NAMESPACE WHEN THE PANEL IS ANNOUNCED AS ONE OF ITS
        # FIGURES. A figure served from somewhere other than the namespace the
        # act declares is the 404 this package fixed today: the address the
        # screen publishes and the directory the file is in have to be the same
        # place, and the guard that says so reads every announced figure's URL.
        # The mesh and surface panels are the SEQUENCER's, not the act's, and
        # keep the panel store.
        out = Path(OUT_ROOT) / (namespace or self.PANEL_DIR)
        out.mkdir(parents=True, exist_ok=True)
        served = self.PANEL_NAMES.get(panel, panel)
        shutil.copy2(shot, out / f"{served}.png")
        # THE PROVENANCE TRAVELS WITH THE PICTURE. The sidecar is copied beside
        # the served panel, so the case, the time and the cell count behind
        # what is on screen are readable from the served root at
        # /api/field/demo-panels/<name>.json. It is deliberately NOT published
        # on the wire: it carries a case path, and a case path may not reach a
        # payload that renders.
        shutil.copy2(side, out / f"{served}.json")
        return {
            "url": f"/api/plot/{namespace or self.PANEL_DIR}/{served}.png",
            "panel": panel,
            # Both numbers travel so the DISPLAY can make the same assertion
            # this method just made. A guard that only ever runs on the
            # publishing side cannot see a payload edited on the way out.
            "cells": claimed,
            "printed_cells": printed,
        }

    def _publish_panel(self, emit, mesh, panel: str, *, stage: str,
                       label: str = "", caption: str = "") -> dict | None:
        """Put one rendered panel on the stage, if the act has one.

        ``stage`` is the beat the panel belongs to, not a constant: the banner
        every payload carries is composed from it, so a surface published under
        the meshing stage would be announced with the mesher's words.
        """
        payload = self._panel(mesh, panel)
        if payload is None:
            return None
        if label:
            payload["label"] = label
        if caption:
            payload["caption"] = caption
        return self._publish(emit, "mesh.panel", dict(payload, stage=stage))

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
                                replay.pace * 9.0, 0.001),
                            # ONE DECLARATION REACHES BOTH SURFACES THAT STATE
                            # A COST. The solving stage speaks a closing
                            # sentence and the results stage publishes a cost
                            # line; wiring the act's projection into only one
                            # of them would put two different compute figures
                            # on one screen two beats apart.
                            cost_projection=replay.cost_projection),
            sleep=self.sleep, clock=self.clock)
        stage.prepare()
        published = stage.run(emit=emit, script=script)
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

    #: The served root's directory for act bodies. Not ``sdk/geometry``: that
    #: is where the server's upload handler writes, and an act whose body lives
    #: there can have it replaced by any upload of the same filename.
    SURFACE_NAMESPACE = "act-geometry"

    def _stage_surface(self, body) -> str | None:
        """Serve the act's body from a directory uploads cannot write into.

        Copies the act's declared surface into ``<output root>/act-geometry/``
        and returns ``/api/surface/act-geometry/<file>``, which
        ``server._serve_surface_artifact`` resolves under the output root and
        returns as the same viewport payload ``/api/geometry`` does. No server
        change: that route already existed for mission-produced surfaces.

        Returns ``None`` when the file is not on disk, which leaves the caller
        on the old address rather than announcing one that resolves nowhere.
        An act whose surface is missing is already refused by
        :func:`demo_mode.validate_act` before any stage opens.
        """
        import shutil

        from . import OUT_ROOT

        source = Path(body.served_stl)
        if not source.is_file():
            return None
        out = Path(OUT_ROOT) / self.SURFACE_NAMESPACE
        out.mkdir(parents=True, exist_ok=True)
        target = out / source.name
        if not (target.exists() and target.samefile(source)):
            shutil.copy2(source, target)
        return f"/api/surface/{self.SURFACE_NAMESPACE}/{source.name}"

    def _stage_figure(self, namespace: str, figure) -> None:
        """Put the figure where the address the screen is about to publish
        says it is.

        The served root is not the run tree. ``announce_plot`` advertises
        ``/api/plot/<namespace>/<file>`` and the server resolves that under
        ``<output root>``, while an act's ``Figure.path`` points into the run's
        own artefacts directory -- two different places, with nothing between
        them. The legacy jet-flap surface already bridged the gap by copying
        (``jet_flap_display._serve``); the sequencer path did not, which is why
        every figure URL it published answered 404.

        It copies INTO the served root and never out of it, so no run tree is
        written to. A source that is not on disk is left alone rather than
        raising: :func:`demo_mode.validate_act` already refuses an act whose
        figures are missing, and :meth:`run` runs that before a stage opens, so
        raising a second time here would only turn a clear authorship refusal
        into a stage-time one.
        """
        import shutil

        from . import OUT_ROOT

        source = Path(figure.path)
        if not source.is_file():
            return
        out = Path(OUT_ROOT) / namespace
        out.mkdir(parents=True, exist_ok=True)
        target = out / source.name
        if target.exists() and target.samefile(source):
            return
        shutil.copy2(source, target)

    def _stage_results(self, emit, script, record) -> dict:
        r = self.act.results()
        replay = self.act.solve_replay()
        from . import announce_plot, emit_table

        field_paths = {Path(f.path) for f in r.fields}
        for figure in list(r.fields) + list(r.plots):
            # THE NAMESPACE IS THE ACT'S, NOT A CONSTANT. See
            # :func:`figure_namespace` for what the constant cost and why
            # deriving it without staging would still leave a 404.
            namespace = figure_namespace(figure)
            self._stage_figure(namespace, figure)
            # THE CAPTION IS THE ACT'S AND IT WAS BEING THROWN AWAY.
            # :class:`demo_mode.Figure` requires a caption, validates it
            # (one line, at most twenty words) and passes it through
            # ``check_demo_language`` at construction -- and this call site
            # published the title alone, so four authored, validated captions
            # reached nothing on every run of this act. Measured on the
            # assembled results stage: four of four figures on the wire with
            # no caption key at all.
            # A FIELD PICTURE TAKES THE STAGE, A GRAPH TAKES THE STRIP.
            # Sanaa's panel sequence ends in fields, and both lists were being
            # announced identically, so the page could not tell a picture of
            # the flow from a picture of a curve and the grid stayed on the
            # stage through the report. The flag is derived from the act's own
            # `fields` list, so no act has to declare it twice.
            announce_plot(emit, namespace, figure.path,
                          figure.title, figure.caption,
                          field=Path(figure.path) in field_paths)
        # THE SOLVED FIELDS, RENDERED FROM THE CASE, ON THE EXISTING RASTER
        # PATH. No new plumbing: `field.ready`'s stage state is already an
        # <img> fed by a URL, so a rendered panel needs only to be served and
        # announced. They go LAST so the stage closes on the flow rather than
        # on a graph, which is the order Sanaa's panel sequence ends in.
        #
        # Guarded exactly as the mesh panels are -- :meth:`_panel` refuses a
        # picture whose provenance disagrees with the count the screen prints --
        # so a field picture cannot arrive from a grid the numbers did not come
        # from. The wording is deliberately the sequencer's own and plain: these
        # panels are found generically, beside whatever grid the act cites, so
        # an act-specific sentence written here would be a sentence about a
        # picture this method has not read.
        try:
            mesh = self.act.mesh_plan()
        except Exception:                                      # noqa: BLE001
            mesh = None
        if mesh is not None:
            # PRESSURE FIRST AND VELOCITY LAST, and the order is a looked-at
            # decision rather than an alphabetical one. The last field
            # announced is the one left standing on the stage, and the two do
            # not read equally well: the pressure panel's diverging scale is
            # symmetric about zero over the full data range, so a near-slot
            # extremum flattens the whole section into pale tints, while the
            # velocity panel shows the jet leaving the slot and turning the
            # wake. Both are honest and both carry their scale; only one of
            # them is worth the beat a viewer spends looking at it.
            fields = (
                ("field_p", "Solved pressure field",
                 "Pressure over the solved section, on the grid the numbers "
                 "come from."),
                ("field_u", "Solved velocity field",
                 "Velocity magnitude over the solved section, on the grid "
                 "the numbers come from."),
            )
            # The namespace is the ACT'S, taken from a figure it declares, so a
            # panel announced beside the act's own figures is served from the
            # same directory they are. Derived rather than constant: see
            # :func:`figure_namespace` for what a constant here cost.
            declared = list(r.fields) + list(r.plots)
            space = figure_namespace(declared[0]) if declared else self.PANEL_DIR
            for panel, title, caption in fields:
                shot = self._panel(mesh, panel, namespace=space)
                if shot is None:
                    continue
                announce_plot(emit, space, Path(shot["url"]).name,
                              title, caption, field=True)
        if script is not None:
            for table in r.tables:
                emit_table(emit, script, role=table.role,
                           title=table.title,
                           headers=list(table.headers),
                           rows=[list(row) for row in table.rows],
                           table_id=table.table_id)
        published = self._publish(emit, "demo.results", {
            "stage": "results",
            "solver": record.solver_header(),
            "verification": list(r.verification_lines),
            "limitations": list(r.limitations),
            "cost": cost_line(replay.core_minutes(),
                              projection=replay.cost_projection),
            # THE FORECAST NOW SAYS IT IS ONE, and says what it is a forecast
            # for. It published as a bare "56.8 processor-minutes" beside the
            # spend, and ``stageLines`` renders every string leaf in payload
            # order, so the screen carried an unlabelled second number under
            # the cost sentence with nothing to say which was which. That was
            # merely confusing while both figures described one machine. It
            # stops being merely confusing the moment the spend is shown for
            # OTHER hardware: an unlabelled 56.8 sitting under a projected
            # 23.5 invites a division that is not a ratio of anything.
            "estimate": self._estimate_line(r, replay),
            **self._certificate_field(),
        })
        return published

    def _certificate_field(self) -> dict:
        """The certificate statement on the results card, or nothing at all.

        RENDERED, NEVER RESOLVED. ``stageLines`` publishes every string leaf of
        this payload in order, so the sentence the act wrote is the sentence
        the screen carries. Nothing here looks a certificate up by mission
        name, intent or path, which is the lookup that has already rendered
        one body's document under another body's name.
        """
        closing = self.act.closing()
        if closing is None:
            return {}
        return {"certificate": closing.certificate_state}

    def _estimate_line(self, results, replay) -> str:
        """The up-front forecast, labelled, and honest about what it is for.

        The forecast was made for the machine the sweep RAN on. When the act
        shows its spend projected onto other hardware, the two numbers are no
        longer commensurable and the sentence says so rather than leaving a
        viewer to divide them. R8 still gets its estimate beside its spend.
        """
        shown = results.cost_estimate_from_stage_2.on_screen()
        if replay.cost_projection is None:
            return f"Forecast before the run: {shown}."
        return (f"Forecast before the run: {shown} on the machine it runs on, "
                f"which is not the machine the figure above describes.")

    def _stage_closing(self, emit, script) -> None:
        """THE ACT ENDS IN A REPORT. Sanaa: "nothing ends on a table."

        Three publications, all of which the control room has always known how
        to render and none of which any act was sending:

        * the Conclusion phase, which is what puts the heading in the digest,
          advances the cycle counter and moves the masthead off MISSION
          RUNNING;
        * ``report.ready``, which is what UNHIDES the Report tab -- the button
          carries ``hidden`` in the markup until a report arrives, so an act
          with no report has no Report tab at all;
        * and the certificate block, which is a STATEMENT and not a link. See
          :class:`demo_mode.Closing` for the two measured defects behind that:
          the certificate builder aliases weaker tiers onto "SOLVER-BACKED",
          and the certificate store is keyed by intent and is
          last-writer-wins, so a link resolved by path can render a document
          belonging to a different run. Nothing here mints or resolves one.
          The act says whether this run has a certificate and that sentence is
          rendered as written.

        AN ACT WITH NO ``closing()`` IS UNCHANGED, byte for byte.
        """
        closing = self.act.closing()
        if closing is None:
            return
        from chief_engineer.lab import lab_report
        from . import bullets

        if script is not None:
            script.phase("Conclusion")
            bullets(script.engineer, *closing.conclusion_lines)
        if emit is None:
            return
        emit("report.ready", lab_report(
            title=closing.title,
            # THE CERTIFICATE BLOCK, at the foot of the abstract, because the
            # abstract is the one section of the memo the page renders as
            # paragraphs and because the statement belongs beside the claim it
            # qualifies rather than under a heading of its own.
            abstract=list(closing.abstract) + [closing.certificate_state],
            methods=list(closing.methods),
            results=[dict(row) for row in closing.results],
            uncertainty=list(closing.uncertainty),
            next_investigations=list(closing.next_investigations)))

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


def make_act_entry(key: str, *, act_module: str, label: str | None = None,
                   driver: str | None = None, use_act=None, fallback=None):
    """THE ONE WAY AN ACT IS REACHED FROM THE DISPATCHER. Returns its ``main``.

    A workflow module adopts DEMO MODE in one line::

        main = make_act_entry("jet-flap", act_module="workflows.jet_flap_act")

    and the router reaches it exactly as it reaches every other workflow. Four
    acts adopting this is ONE implementation with four call sites; four acts
    each carrying their own copy of the delegation is four implementations of
    one thing, and copies diverge. This campaign has already paid for that
    lesson twice in one night.

    WHY NOT A BRANCH IN THE SHARED DISPATCHER, which is the obvious place. The
    guarantee wanted is "an act cannot be wired up wrong"; the cost of getting
    it there is an edit to ``chief_engineer.server._run_workflow``, through
    which EVERY team's intent runs. This shape gives the same guarantee for
    ZERO bytes changed in ``server.py`` or ``router.py``, so every other
    intent's path stays byte-identical by construction rather than by
    inspection. A fifth act is a one-line adoption that cannot get the
    plumbing wrong, because there is no plumbing left to get wrong.

    WHAT THE ONE IMPLEMENTATION CARRIES, each of which was a separate finding:

    * **The act module is imported here**, because importing it is what
      REGISTERS the act. Nothing walks the package; an act that is never
      imported is not in the registry, and ``run_act`` would refuse with "no
      act is registered".
    * **``emit`` is passed straight through** and is the mission EventBus's
      ``publish``, so ``stage.banner`` and ``solve.frame`` reach the page.
    * **``script`` is built here, and it is load-bearing rather than
      decorative.** The meshing, gates and results stages publish their tables
      only when a script exists; with ``script=None`` all three measured
      tables would silently not render.
    * **``request`` sets the prompt line and NOTHING else**, as
      ``typed_prompt``. Measured before it was wired: the prompt stage
      published the act's registered string whatever was typed, so a viewer
      who paraphrased saw canned text echoed back as their own words.
    * **``params`` IS DROPPED, and that is a property of the design rather
      than an oversight** -- and it is the safer half. The served geometry
      comes from the ACT's own ``served_stl`` by way of ``_stage_geometry``,
      never from what an operator happened to upload, so the picture on screen
      and the grid behind the numbers are bound structurally instead of by
      convention. Threading an uploaded filename in is exactly what would
      break that bind.
    * **A refusal is not caught.** ``SequencerRefused``, ``DemoContractError``
      and any reader's refusal propagate to ``_run_workflow``, which publishes
      ``mission.failed`` with the reason. Swallowing one would put a silent
      completion on screen in place of a screen that refused.

    ``label`` names the transcript; it defaults to the act key.
    """
    import importlib

    def main(request: str | None = None, params: dict | None = None,
             emit=None) -> int:
        from . import make_transcript

        # THE FORK: ONE INTENT MAY SERVE MORE THAN ONE ACT, and only some of
        # them are built. The thermal intent covers two, and only one has an
        # act module; the other must keep reaching the surface that serves it
        # today, UNCHANGED, until its act exists. This is the "legacy stays
        # reachable" rule generalised from one module to the mechanism -- put
        # in each act's module instead, it would reintroduce exactly the
        # per-act duplication this factory removes.
        #
        # No ``use_act`` means this entry always walks the stages, which is
        # the single-act case and the common one.
        if use_act is not None and not use_act(params, request):
            if fallback is None:
                raise SequencerRefused(
                    f"this request does not select the {key!r} act and no "
                    f"other surface is wired to serve it, so nothing is shown "
                    f"rather than the wrong act being shown")
            return fallback(request=request, params=params, emit=emit)

        module = importlib.import_module(act_module)
        script = make_transcript(label or key, emit)
        # AN ACT MAY OWN ITS SEQUENCER, AND ONE DOES. Measured while proving
        # this mechanism act-agnostic: the adjoint act subclasses Sequencer to
        # override the solving stage, and driving it through the plain
        # run_act refused with "the solving stage has no cases to read" -- the
        # base stage looking for a replay the subclass supplies another way.
        # A factory that assumed one sequencer would have made the second
        # adoption silently wrong, which is exactly the divergence this exists
        # to prevent. So an act names its own driver and the factory calls it.
        if driver is not None:
            import inspect

            fn = getattr(module, driver)
            kwargs = {"emit": emit, "script": script}
            # PASS THE TYPED PROMPT ONLY WHERE IT IS ACCEPTED, AND SAY SO WHEN
            # IT IS NOT. Measured: the adjoint act's driver does not take one,
            # so passing it unconditionally raises and passing it silently
            # would lose the prompt echo without anyone noticing. Neither is
            # acceptable, so the attribute below records the truth and the
            # act's owner can add the one-line passthrough.
            takes = inspect.signature(fn).parameters
            if "typed_prompt" in takes or any(
                    p.kind is inspect.Parameter.VAR_KEYWORD
                    for p in takes.values()):
                kwargs["typed_prompt"] = request
                main.typed_prompt_reaches_screen = True
            else:
                main.typed_prompt_reaches_screen = False
            fn(**kwargs)
        else:
            run_act(key, emit=emit, script=script, typed_prompt=request)
        return 0

    main.__name__ = "main"
    main.__qualname__ = "main"
    main.__doc__ = (
        f"Run the {key!r} act through the nine DEMO MODE stages.\n\n"
        f"Adopted from :func:`demo_sequencer.make_act_entry`, which holds the "
        f"whole implementation; see it for what is threaded and what is "
        f"deliberately dropped.")
    #: Read by the pre-shoot gate and by anything auditing which workflow
    #: modules are DEMO MODE acts, so the adoption is discoverable rather than
    #: inferred from the source.
    main.demo_act_key = key
    main.demo_act_module = act_module
    main.demo_act_driver = driver
    #: Set on first call when a driver is used; None until then.
    main.typed_prompt_reaches_screen = None if driver else True
    return main


def run_act(key_or_act, emit=None, script=None, **kwargs) -> dict:
    """Resolve an act by key (or take one directly) and walk it.

    THE SEQUENCER IS THE ACT'S TO NAME, and this function used to name it
    itself. ``Sequencer(act=act)`` was hard-coded here, so an act that replaces
    a stage -- the shock-reflection and adjoint acts both replace SOLVING,
    because the shared replay reader wants a force history a compressible solve
    does not write -- was walked by the base sequencer whatever it declared,
    and refused at the solving stage with "no cases to read". Measured:
    ``run_act("shock-reflection")`` published 29 events and stopped seven
    stages in; the act's own driver published 208 and finished. Since
    ``scripts/check_demo_acts.py`` -- the pre-shoot gate -- drives through
    here, the gate could not reach either act's results stage at all.

    :meth:`demo_mode.DemoAct.sequencer` returns ``None`` for every act that
    uses the shared walk, so this is byte-identical for all of them.
    """
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
    cls = act.sequencer() or Sequencer
    # A DECLARATION THAT IS NOT A SEQUENCER IS A REFUSAL, NOT A FALLBACK.
    # Silently walking the base sequencer here would put the act back in the
    # exact state this repaired, and the author would have no way to tell.
    if not (isinstance(cls, type) and issubclass(cls, Sequencer)):
        raise SequencerRefused(
            f"{type(act).__name__} declares a sequencer that is not a "
            f"Sequencer subclass, so the stage it means to replace would be "
            f"walked by the shared one instead")
    return cls(act=act, **kwargs).run(emit=emit, script=script)
