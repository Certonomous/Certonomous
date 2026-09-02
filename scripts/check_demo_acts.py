#!/usr/bin/env python3
"""PRE-SHOOT CONFORMANCE GATE — can every registered demo act actually start?

WHY THIS EXISTS, and it is a specific event rather than a principle. On
2026-09-01 at 04:43Z the jet-flap act stopped being able to start. A figure
generator ran, wrote ``figure_provenance.json`` holding only its own four
entries, and two figures the act displays were left with no provenance. The
act's own guard refused correctly -- "a picture whose grid cannot be named
must not go on camera" -- but nothing ASKED it until a lane happened to drive
the act five minutes later, for an unrelated reason. Between those two moments
the demo was broken and the lab did not know.

The record it depends on is not even in git: it exists only on disk, as the
union of whichever generators have run since it was last cleared. So any lane
that clears the artefacts directory and re-runs one generator breaks every act
that displays a figure from another, silently.

THE POINT IS THE MOMENT, NOT THE CHECK. ``validate_act`` already existed and
already worked. What did not exist was anything that ran it BEFORE the curtain
went up. This is that: one command, run it before a shoot.

    python3 scripts/check_demo_acts.py

Exit 0 when every act can start, 1 when any cannot, 2 when the harness itself
could not run -- never a silent pass.

THIS GATE HAS BEEN SEEN TO FAIL. ``--selftest`` plants a missing provenance
entry into a copy of the record and asserts the gate reports it, then restores.
A gate never observed failing is not known to work; that is CLAUDE.md rule 3's
planted control applied to a check rather than to a reader, and it is the same
finding VERIFICATION_CHARTER 2n.18 records against guards two supervisors had
personally read and certified.

SECOND HALF, ADDED 2026-09-01: SANAA'S SHOOTING CHECKLIST, AS A PROGRAM.
Her 20:30Z shooting protocol ends in nine boxes a person ticks from memory
before a camera rolls. The section below ticks the ones a program can honestly
tick and refuses to tick the rest, printing beside every line what it does NOT
check. Three modes:

    python3 scripts/check_demo_acts.py                    # both halves
    python3 scripts/check_demo_acts.py --startup-only     # the original gate
    python3 scripts/check_demo_acts.py --checklist-selftest

ASKING WHETHER AN ACT CAN START IS NOT ASKING WHETHER IT FINISHES, and the
difference was worth the whole second half. This gate printed "shock-reflection:
can start" while driving that act refuses at the SOLVING stage, four of nine
stages in: ``solve_replay().cases`` is empty and ``_stage_solving`` requires it,
and ``validate_act`` never reads ``cases``. So the checklist DRIVES each act --
real mesher, real logs, sleeps removed, about seven seconds an act -- and grades
what it published rather than what it declared.

Exit 0 when every act starts AND every checklist line a program can judge is
satisfied, 1 when any is not, 2 when the harness could not run.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "sdk"))
sys.path.insert(0, str(REPO / "scripts"))

#: Importing an act module is what registers it; the registry is populated by
#: import side effect and nothing walks the package for us. Listed explicitly
#: so a missing act is a visible edit here rather than a silent empty run.
#: MOTOR-THERMAL WAS MISSING FROM THIS TUPLE AND SO HAS NEVER BEEN GATED.
#: It is one of the four acts Sanaa is shooting, it registers exactly like the
#: others, and this gate -- whose entire purpose is to ask whether every act
#: can start BEFORE the curtain goes up -- had never once asked it. The comment
#: above describes precisely the failure that then occurred: a missing act was
#: not a visible edit here, it was a silent omission, and the gate reported
#: "2 of 3 registered acts can start" while a fourth act nobody had listed
#: could not complete a drive at all.
#:
#: ADDING IT MAKES THE GATE REPORT A REAL FAILURE, which is the point. Measured
#: on the day it was added: driving ``motor-thermal`` refuses at the SOLVING
#: stage after 29 events -- ``solve_replay().cases`` is empty and the act
#: declares no sequencer of its own, the same defect this gate's own docstring
#: records against shock-reflection. That failure is not created by listing the
#: act; it is only made visible by it.
ACT_MODULES = ("workflows.jet_flap_act", "workflows.adjoint_act",
               "workflows.dmr_act", "workflows.motor_thermal_act",
               "workflows.battery_module_act")


def _load_acts() -> dict:
    from workflows.demo_mode import registered_acts

    for name in ACT_MODULES:
        __import__(name)
    return dict(registered_acts())


def _acts_the_package_registers() -> dict:
    """Every act module that registers on import, found by READING the source.

    THE CLASS THIS CLOSES, AND IT IS THE ONE THAT LET MOTOR-THERMAL THROUGH.
    :data:`ACT_MODULES` is hand-maintained, and a hand-maintained list has no
    way to know what it is missing: the gate can only ever check what somebody
    remembered to add. The comment above that tuple anticipated exactly this
    and it happened anyway, because a warning is not a mechanism. So the list
    is now CHECKED AGAINST THE PACKAGE rather than trusted.

    FOUND BY PARSING, NOT BY IMPORTING, and not by a text search either.
    Importing every module in the package to see which ones register would run
    arbitrary module-level code for the side effect of finding out. A text
    search for "register_act" is worse than useless here: it matches the
    definition in ``demo_mode``, matches docstrings, and -- the case that
    proved it -- matched ``sdk/workflows/battery_module_act.py`` back when
    that module called ``register_act`` INSIDE A FUNCTION and deliberately
    registered nothing on import. Counting that would have made this check
    demand the gating of an act whose whole purpose then was to refuse.
    (2026-09-02: that act now has a completed run behind it, registers at
    module level like the others, and IS gated; the parsing rule below is
    unchanged and simply finds it now, which is the rule working.)

    So: parse each module and count a call only when it sits at MODULE LEVEL,
    which is what "registers on import" actually means.

    Returns ``{key: module name}`` for every act key registered on import.

    THE FIRST CUT OF THIS FUNCTION WAS WRONG IN THE WAY ITS OWN DOCSTRING
    DENIED, and it was caught by the control rather than by reading it. It said
    "module level only" and used ``ast.walk`` over each top-level node --
    which descends into the bodies of top-level function and class
    definitions. So it found ``battery_module_act``'s call, which is inside a
    function precisely so that importing the module registers NOTHING, and
    demanded that the gate load an act whose entire purpose is to refuse. A
    comment asserting a property the code does not have is worth less than no
    comment: it stops the next reader checking.

    ``_descend`` therefore refuses to enter a ``def``, a ``class`` or an
    ``if __name__ == "__main__"`` guard, which are the three ways code sits in
    a module and does not run when it is imported.
    """  # noqa: D208
    import ast

    def _is_main_guard(node) -> bool:
        test = getattr(node, "test", None)
        if not isinstance(node, ast.If) or not isinstance(test, ast.Compare):
            return False
        left = test.left
        return isinstance(left, ast.Name) and left.id == "__name__"

    def _descend(node):
        """Yield every node that RUNS when the module is imported."""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)) or _is_main_guard(node):
            return
        yield node
        for child in ast.iter_child_nodes(node):
            yield from _descend(child)

    found: dict = {}
    package = REPO / "sdk" / "workflows"
    for path in sorted(package.glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for top in tree.body:
            for call in _descend(top):
                if not isinstance(call, ast.Call):
                    continue
                name = call.func
                target = (name.id if isinstance(name, ast.Name)
                          else getattr(name, "attr", ""))
                if target != "register_act" or not call.args:
                    continue
                key = call.args[0]
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    found[key.value] = f"workflows.{path.stem}"
    return found


def _ungated_acts() -> list:
    """Acts the package registers on import that this gate does not load.

    An act that registers and is not gated is itself a finding: it will be
    reachable in a shoot and will never have been asked whether it can start.
    """
    gated = set(ACT_MODULES)
    return sorted(f"{key} ({module})"
                  for key, module in _acts_the_package_registers().items()
                  if module not in gated)


def _problems() -> dict:
    """Every registered act's problem list, by key. The gate's raw reading.

    Separated from :func:`check` so the selftest can compare problem SETS
    rather than exit codes; an exit code cannot tell a gate that saw the plant
    from one that was already failing for another reason.
    """
    from workflows.demo_mode import validate_act

    from workflows.demo_sequencer import Sequencer

    out = {}
    for key, act in _load_acts().items():
        try:
            problems = list(validate_act(act))
        except Exception as exc:                   # noqa: BLE001 - reported
            out[key] = [f"validation raised {type(exc).__name__}: {exc}"]
            continue
        # A SILENT SKIP BECOMES A PERMANENT SKIP. At runtime, an act whose
        # mesh work_dir is a real case tree simply does not mesh -- the
        # non-destructive choice, and the one that keeps a working screen up.
        # But an act that quietly publishes "nothing was meshed" forever is an
        # act whose mesh stage nobody ever fixes, because nothing ever
        # complains. So the runtime skips and THIS reports. Different
        # surfaces, different severities.
        try:
            plan = act.mesh_plan()
            unsafe = Sequencer(act=act)._unsafe_work_dir(plan.work_dir)
        except Exception as exc:                   # noqa: BLE001 - reported
            problems.append(
                f"the mesh plan could not be read, so its working directory "
                f"could not be checked: {type(exc).__name__}: {exc}")
        else:
            if unsafe is not None:
                problems.append(
                    f"meshing: this act's mesher is aimed at a directory that "
                    f"must not be meshed into ({unsafe}). The live stage will "
                    f"SKIP meshing rather than risk it, so the screen shows no "
                    f"grid; repoint work_dir at a scratch directory.")
        out[key] = problems
    return out


def check(verbose: bool = True) -> int:
    """Validate every registered act. Returns the process exit code."""
    from workflows.demo_mode import validate_act

    try:
        acts = _load_acts()
    except Exception as exc:                       # noqa: BLE001 - reported
        print(f"HARNESS FAILED: could not import the acts: "
              f"{type(exc).__name__}: {exc}")
        return 2

    if not acts:
        print("HARNESS FAILED: no acts registered; this gate would pass "
              "vacuously and must not")
        return 2

    # ONE READING, RENDERED. check() used to call validate_act itself, so it
    # and _problems() were two implementations of "what is wrong with the
    # acts" and could disagree -- exactly the drift the sequencer's own
    # invariant 1 exists to prevent, reappearing in a gate.
    findings = _problems()
    bad = 0
    for key in sorted(acts):
        problems = findings.get(key, [])
        if problems:
            bad += 1
            print(f"  {key}: CANNOT START -- {len(problems)} problem(s)")
            for p in problems:
                print(f"      - {p}")
        elif verbose:
            print(f"  {key}: can start")

    # AN ACT THIS GATE DOES NOT LOAD IS ITSELF A FINDING, and it is the one
    # this gate was blind to for its whole life. Motor-thermal registers
    # exactly like the others, is one of the four acts being shot, and was
    # missing from ACT_MODULES -- so the gate reported "2 of 3 registered acts
    # can start" with perfect confidence while a fourth sat unexamined.
    #
    # THE COUNT IS THE TELL AND IT LOOKED FINE. "of 3" was true of the list and
    # false of the package, and nothing in the output could distinguish those
    # two readings. A gate that enumerates its own subjects can only check what
    # somebody remembered; this makes forgetting a failure instead of a
    # silence.
    ungated = _ungated_acts()
    if ungated:
        bad += 1
        print(f"  HARNESS: {len(ungated)} act(s) register on import and are "
              f"NOT gated here; add them to ACT_MODULES")
        for name in ungated:
            print(f"      - {name}")

    print(f"{len(acts) - bad} of {len(acts)} registered acts can start.")
    return 1 if bad else 0


def selftest() -> int:
    """Plant a missing provenance entry and prove the gate reports it.

    IT NEVER WRITES THE SHARED RECORD. The obvious implementation edits
    ``figure_provenance.json`` in place and restores it in a ``finally``, and
    that is wrong here for a reason this lab has already paid for: the figure
    generators write that same file, from other lanes, at unpredictable
    moments. A plant-and-restore would race them, and the restore would put
    back a version that had been superseded in between -- silently reverting
    somebody's work to fix nothing.

    So the plant is made in a TEMPORARY COPY and the reader is pointed at it,
    which tests exactly the same thing without touching a shared artifact.
    """
    import tempfile

    from workflows import _jf1_numbers

    record = Path(_jf1_numbers.RUN_ROOT) / "artefacts" / "figure_provenance.json"
    if not record.is_file():
        print("SELFTEST INCONCLUSIVE: the provenance record is not on disk, "
              "so a missing entry cannot be planted. This is itself the "
              "condition the gate exists to catch.")
        return 2
    try:
        entries = json.loads(record.read_text(encoding="utf-8"))
    except ValueError:
        print("SELFTEST INCONCLUSIVE: the record on disk is not readable "
              "JSON, so nothing can be planted into it.")
        return 2
    if not isinstance(entries, dict) or not entries:
        print("SELFTEST INCONCLUSIVE: the record holds no entries to remove.")
        return 2

    # COMPARE PROBLEM SETS, NOT EXIT CODES. Tonight the gate is already red
    # for an unrelated reason, and a selftest that only watched the exit code
    # would read "1 before, 1 after" and call itself proved. The question is
    # whether the plant introduces a problem NAMING THE ENTRY IT REMOVED,
    # which is answerable whether or not the tree is otherwise healthy.
    before = _problems()
    dropped = sorted(entries)[0]
    planted = {k: v for k, v in entries.items() if k != dropped}

    # PATCH WHERE THE READER IS DEFINED, NOT WHERE IT IS RE-EXPORTED. The
    # first cut of this selftest replaced ``_jf1_numbers.read_figure_provenance``
    # and the plant had NO EFFECT: ``assert_display_grids`` lives in
    # ``jf1_display_numbers`` and resolves the reader from that module's own
    # globals, so the re-exported alias is never consulted. The selftest
    # reported "0 new problems" and correctly failed itself. That is the
    # planted control catching the control, and it is why this plants rather
    # than reasons about what the patch would do.
    impl = _jf1_numbers._impl
    real_reader = impl.read_figure_provenance
    with tempfile.TemporaryDirectory() as tmp:
        stand_in = Path(tmp) / "figure_provenance.json"
        stand_in.write_text(json.dumps(planted, indent=2, sort_keys=True)
                            + "\n", encoding="utf-8")

        def reading_the_plant(path=None):
            return real_reader(stand_in)

        impl.read_figure_provenance = reading_the_plant
        try:
            after = _problems()
        finally:
            impl.read_figure_provenance = real_reader

    restored = _problems()
    flat_before = {p for ps in before.values() for p in ps}
    flat_after = {p for ps in after.values() for p in ps}
    new = flat_after - flat_before
    names_the_plant = [p for p in new if dropped in p]

    print()
    print(f"  problems before planting      : {len(flat_before)}")
    print(f"  problems with '{dropped}' removed: {len(flat_after)}")
    print(f"  new problems naming the plant : {len(names_the_plant)}")
    print(f"  problems after withdrawing    : "
          f"{len({p for ps in restored.values() for p in ps})}")
    print(f"  shared record written by this : no")

    if not names_the_plant:
        print("SELFTEST FAILED: removing a provenance entry produced no new "
              "problem naming it. The gate cannot see the defect it exists "
              "for.")
        return 1
    if restored != before:
        print("SELFTEST FAILED: the problem set did not return to its "
              "starting state, so the plant was not fully withdrawn.")
        return 1
    print("SELFTEST PASSED: removing one provenance entry produces a problem "
          "naming that entry, the plant withdraws cleanly, and the shared "
          "record was never written.")
    if flat_before:
        print("NOTE: the tree was ALREADY failing before the plant, so this "
              "run proves the gate reports a missing entry and does NOT "
              "prove it passes a healthy tree. Re-run when the acts are "
              "green.")
    return 0


# ===========================================================================
# THE SHOOTING CHECKLIST, AS A PROGRAM
# ===========================================================================
#
# Sanaa's pre-capture checklist (2026-09-01 ~20:30Z shooting protocol, lines
# 72-81) is nine boxes a person ticks from memory before a camera rolls. This
# section ticks the ones a program can honestly tick, and REFUSES TO TICK THE
# REST. That refusal is the whole design. A checklist that reports green on an
# item it cannot test manufactures confidence at the exact moment somebody is
# about to film, which is worse than no checklist at all: the person stops
# looking because the machine said it looked.
#
# WHAT THIS BOX CAN AND CANNOT SEE, stated once so every classification below
# can refer to it. Nothing on this machine executes CSS layout, paints a
# viewport or runs the browser's paced render queue. So a claim of the form
# "X is ON SCREEN", "X and Y are on ONE screen" or "X MATCHES what is on
# screen" is not decidable here by any harness we could write. What IS
# decidable is what the act PUBLISHED: the event stream is the complete set of
# facts the page is given, and every sentence a viewer reads is a string in it
# (control_room.html:1575-1581 states that property of the renderer: "NOT ONE
# WORD OF PROSE IS INVENTED HERE"). So the honest split, applied item by item,
# is: the CONTENT half is enforceable, the LAYOUT half is not.
#
# HOW THE STREAM IS OBTAINED. Each act is driven in process through
# `demo_sequencer.run_act` with the sleeps removed, and everything it publishes
# is collected. This is a dress rehearsal, not an inspection: the real mesher
# runs, the real logs are read, the real figures are staged. It costs about
# seven seconds and one mesher invocation per act.
#
# WHY DRIVING BEATS VALIDATING, and this is not theoretical. `validate_act`
# passed `shock-reflection` and this gate printed "can start"; driving it
# refuses at the SOLVING stage, four stages in, because `solve_replay().cases`
# is empty and `_stage_solving` requires it. `validate_act` never reads
# `cases`. An act that dies at stage six of nine was being reported as ready to
# film.

#: Emitted event -> the checklist evidence it carries. Kept as prose next to
#: the code that reads it because a reader of this gate needs to know which
#: fact came from which publication.
_STAGE_ORDER_EVENT = "stage.begin"


def _collect(key: str, module: str) -> tuple[list, str | None]:
    """Drive one act in process and return (events, refusal).

    ``refusal`` is None when the act walked all nine stages. It is a sentence
    when the act stopped early -- which is a FINDING, not a skip: an act that
    cannot reach its results stage cannot satisfy the checklist items that live
    there, and every one of them is failed below rather than passed over.

    A ``script`` is built because the meshing, gates and results stages publish
    their tables ONLY when one exists; driving with ``script=None`` would lose
    all three tables and make a missing table look like a content defect
    instead of a harness defect. Copied in intent from
    ``live_pass_jet_flap.collect_offline``, which learned it the hard way.
    """
    import importlib
    import json as _json

    from workflows import make_transcript
    from workflows.demo_sequencer import run_act

    importlib.import_module(module)          # importing REGISTERS the act

    events: list = []

    def emit(name, payload):
        # Serialised the way the live bus serialises it. A payload carrying a
        # Path crashes json.dumps on the real path; catching it here makes that
        # a finding offline rather than a mission failure on camera.
        events.append({"sequence": len(events) + 1, "event": str(name),
                       "payload": _json.loads(_json.dumps(payload, default=str))})

    script = make_transcript(key, emit)
    try:
        run_act(key, emit=emit, script=script, sleep=lambda _s: None)
    except Exception as exc:                                   # noqa: BLE001
        return events, f"{type(exc).__name__}: {exc}"
    return events, None


def _events_of(events: list, name: str) -> list:
    return [e for e in events if e.get("event") == name]


def _payloads_of(events: list, name: str) -> list:
    return [e.get("payload") or {} for e in events if e.get("event") == name]


def _first_index(events: list, name: str) -> int | None:
    for i, e in enumerate(events):
        if e.get("event") == name:
            return i
    return None


def _nonempty(value) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return value is not None


# ---------------------------------------------------------------------------
# Item 9: the forbidden-language sweep
# ---------------------------------------------------------------------------
#
# THIS SWEEP IS A SUPPLEMENT, NOT A SECOND OPINION, and the distinction is
# load-bearing. `demo_mode.NEVER_PHRASES` is the lab's forbidden vocabulary and
# `demo_mode.check_demo_language` is the one checker; `live_pass_jet_flap`
# already applies it to a collected stream through `_rendered_strings`, whose
# TIER1_RENDERED table names the exact key of the exact event that
# control_room.html renders, with the renderer line beside each. All of that is
# IMPORTED here. Rewriting any of it would be the second implementation this
# lab has twice built and twice watched drift.
#
# What is added is only the terms Sanaa's never-list has grown that
# NEVER_PHRASES does not yet carry. They live here rather than in
# `demo_mode.NEVER_PHRASES` -- their proper home -- because that file's content
# rules are being edited by another lane as this is written. THE SUPPLEMENT IS
# BUILT TO BE RETIRED: `--checklist-selftest` measures, per term, whether
# `check_demo_language` already refuses it, and prints the ones that have
# become redundant. When NEVER_PHRASES absorbs a term, this list is told so by
# its own selftest rather than by anybody remembering.
#
# EVERY PATTERN BELOW WAS MEASURED AGAINST HEALTHY STREAMS BEFORE IT WAS
# ADMITTED, over 7,223 rendered strings. A checker that fires on innocent prose
# gets switched off, and a switched-off checker is how the strings it was
# written for reach a screen.
#
# ONE TERM OF HERS IS DELIBERATELY NOT ENFORCED. Her list says "agreements".
# The singular pattern fires five times on healthy, correct prose the acts
# already publish -- "agreement 3.9% at blowing 0.4" on a report result row,
# and a verification line reading "No experimental comparison is available for
# this section". Statistical agreement with a published curve is the honest
# physics word and is not what her never-list is about. Banning it would refuse
# the act's own verification statement, so only the COUNTABLE PLURAL
# "agreements" is enforced -- the lab/contract sense, zero hits on healthy
# streams -- and the singular is reported as an open question for Sanaa rather
# than guessed at. A pattern invented to cover a word whose meaning we are
# unsure of is a false positive waiting for a shoot day.
SUPPLEMENTARY_NEVER: tuple[tuple[str, str, str], ...] = (
    # (label, regex, what to say instead)
    ("prior runs", r"\b(prior|previous|earlier)\s+runs?\b",
     "name this run and what it did"),
    ("agreements (plural, the contract sense)", r"\bagreements\b",
     "say what was compared and by how much it differs"),
    # NEVER_PHRASES carries `\btier[-\s]?\d\b`, which needs a DIGIT: "tier",
    # "tiers" and "top tier" all walk through it. This is the same
    # trailing-context blindness as \bPASS\b vs PASSED, in a different shape.
    ("tier words without a digit", r"\btiers?\b",
     "tier words are never user-visible"),
    # NEVER_PHRASES carries only `not recorded IN THIS BUNDLE`. The bare phrase
    # is the one on Sanaa's list and is the one an author would actually write.
    ("bare 'not recorded'", r"\bnot\s+recorded\b",
     "state the recorded fact"),
    # NEVER_PHRASES carries only `solver: none`. "no solver" is her wording.
    ("'no solver'", r"\bno\s+solver\b", "name the solver of the run"),
    # NEVER_PHRASES carries `already finish(ed|es)?` -- which misses
    # "finishing", the progressive, on a screen whose whole tense rule is
    # progressive-while-running. The inflection defect again, in the file that
    # documents the inflection defect.
    ("'already finished' and its inflections",
     r"\balready\s+(finish(ed|es|ing)?|done|complete[d]?)\b",
     "name the solve and its result, in the present tense"),
    # NEVER_PHRASES catches identifier VALUES (case ids, lesson ids, pids,
    # commit hashes). It does not catch the WORD "id", which Sanaa's grown list
    # names directly. Narrowed to the nouns an act would attach it to.
    ("the word 'id' on screen",
     r"\b(case|run|job|mission|lane|task|point|node)\s+ids?\b",
     "give the thing a plain-English label, not an identifier"),
)


def _supplementary_hits(events: list) -> list[dict]:
    """Every RENDERED string matching the supplementary never-list.

    Sweeps exactly the fields `live_pass_jet_flap._rendered_strings` sweeps:
    the tier-1 table of keys control_room.html demonstrably renders, plus the
    tier-2 `demo.`/`stage.`/`solve.` payloads walked the way the publication
    guard walks them. Audit keys (`for_event`, `table_id`, `beat`, `event`,
    `stage_id`, `url`, `file`) and the routing key `stage` are skipped there
    and so are skipped here.
    """
    import re as _re

    import live_pass_jet_flap as LP

    out: list[dict] = []
    for index, event in enumerate(events):
        for key, text, _zone in LP._rendered_strings(event):
            for label, pattern, remedy in SUPPLEMENTARY_NEVER:
                hit = _re.search(pattern, text, flags=_re.IGNORECASE)
                if hit:
                    out.append({"index": index, "event": event.get("event"),
                                "key": key, "text": text, "label": label,
                                "reason": f"{label}: {hit.group(0)!r} -- {remedy}"})
    return out


# ---------------------------------------------------------------------------
# The nine limbs
# ---------------------------------------------------------------------------
#
# Each limb returns a list of problems. An empty list means the limb's
# ENFORCED half holds; it never means the checklist line is satisfied, because
# most of these lines have a half no program here can reach.

_EXPERT_ROLES = {"CHIEF RESEARCHER", "LEAD RESEARCHER", "CHIEF ENGINEER",
                 "LEAD ENGINEER", "NUMERICIST", "LEAD NUMERICIST"}


#: The two ways a surface reaches the viewport, and the line is satisfied by
#: EITHER. `geometry.ready` hands the page an STL to draw on its canvas;
#: `mesh.panel` with panel="geometry" hands it a rendered picture of the same
#: body, photographed off the solved case. Sanaa, 2026-09-01: "Going forward
#: all acts use paraview." A checklist that still demanded the canvas event
#: would fail an act for obeying that directive -- and would quietly encode the
#: retired path as a requirement, which is how a check outlives the thing it
#: was checking.
def _digits(text):
    """The count inside a screen string, or None.

    The meshing card prints a SENTENCE ("39,984 cells"), not a number, so the
    comparison below is against the quantity a viewer reads rather than against
    a string that happens to contain it. A card with no digits gives no
    reading, which is an absent comparison and never a silently passing one.
    """
    import re as _re

    match = _re.search(r"\d[\d,]*", str(text or ""))
    return int(match.group(0).replace(",", "")) if match else None


def _is_surface(event) -> bool:
    name = event.get("event")
    if name == "geometry.ready":
        return True
    return (name == "mesh.panel"
            and (event.get("payload") or {}).get("panel") == "geometry")


def _limb_geometry(events, refusal, act) -> list[str]:
    problems = []
    ready = [e for e in events if _is_surface(e)]
    if not ready:
        return ["neither geometry.ready nor a rendered surface panel was "
                "published, so the viewport is given nothing to show at all"]
    first_stage = _first_index(events, _STAGE_ORDER_EVENT)
    ready_at = next(i for i, e in enumerate(events) if _is_surface(e))
    # "RENDERS ON LOAD" -- the enforceable half is ORDERING. Sanaa: the body is
    # on screen before the first word is spoken. The sequencer announces it
    # before the stage loop (demo_sequencer.run:386-413) precisely because the
    # geometry stage is the FOURTH of nine and a viewer who just handed over a
    # file watched three stages go by over an empty panel. If the announcement
    # has drifted back inside the loop, this fires.
    if first_stage is not None and ready_at > first_stage:
        problems.append(
            "the surface is announced AFTER the first stage opens, so a viewer "
            "watches the opening stages over an empty geometry panel")
    payload = ready[0].get("payload") or {}
    if not _nonempty(payload.get("label")):
        problems.append("the surface announcement carries no label, so the "
                        "viewport caption is blank")
    if not _nonempty(payload.get("url")):
        problems.append("the surface announcement carries no url, so the "
                        "browser has no address to fetch it from")
    if len(ready) > 1:
        # Two announcements of one body is two fetches and a second viewport
        # cycle. The sequencer guards against it with `self._announced`.
        problems.append(f"the surface is announced {len(ready)} times; each "
                        f"announcement re-fetches and re-cycles the viewport")
    return problems


def _limb_no_tessellation(events, refusal, act) -> list[str]:
    """The tessellated STL canvas NEVER paints on a ParaView act.

    Sanaa, three escalating orders: 04:55Z "make sure ALL runs show the
    paraview no tesselation pls"; 06:25Z "dont show the first geometry (it
    shows the tesellation)"; 09:30Z (relayed) the original tessellation plot
    must not appear AT ALL -- not first-then-replaced, not ever. The page's
    canvas draws ONLY on a ``geometry.ready`` event (control_room.html
    ``loadGeometry``), so the enforceable act-side half is: a stream that
    serves a rendered geometry panel (``mesh.panel`` with panel "geometry")
    must carry ZERO ``geometry.ready`` events, at any index. One such event
    is one window in which the triangle canvas can win the viewport.

    Graded from the STREAM first so the selftest (which grades with
    ``act=None``) exercises the same rule the acts are held to; the act's own
    ``rendered_panels`` declaration, where available, additionally makes an
    ABSENT panel loud rather than letting a missing render read as "nothing
    to check".
    """
    panel_at = [i for i, e in enumerate(events)
                if e.get("event") == "mesh.panel"
                and (e.get("payload") or {}).get("panel") == "geometry"]
    tess_at = [i for i, e in enumerate(events)
               if e.get("event") == "geometry.ready"]
    declares = "geometry" in tuple(getattr(act, "rendered_panels", ()) or ())
    problems = []
    if declares and not panel_at:
        problems.append(
            "the act declares a rendered geometry panel and none was "
            "published, so the page has no ParaView surface to paint and "
            "the viewport would sit empty or fall back")
    if (panel_at or declares) and tess_at:
        problems.append(
            f"a tessellation-source event (geometry.ready) is published at "
            f"index {tess_at[0]} of a stream that serves a rendered geometry "
            f"panel; the client STL canvas must never paint on this act "
            f"(Sanaa 09:30Z: not first-then-replaced, not ever)")
    return problems


def _limb_stages(events, refusal, act) -> list[str]:
    from workflows.demo_mode import STAGES

    problems = []
    begins = [p.get("stage") for p in _payloads_of(events, _STAGE_ORDER_EVENT)]
    if not begins:
        return ["no stage.begin was published, so the header has nothing to "
                "advance through"]
    if begins != list(STAGES):
        problems.append(
            f"the stages published are {begins}, not the nine in order "
            f"{list(STAGES)}; the header would advance through a different "
            f"sequence than the act performs")
    # THE BANNER/CONTENT PAIRING. Every publication carries `banner`, and every
    # `stage.banner` names the event it describes in `for_event`. That pairing
    # is the only machine-readable link between the header and the card under
    # it, so a banner naming an event that was never published is a header
    # describing a screen that does not exist.
    emitted = {e.get("event") for e in events}
    for p in _payloads_of(events, "stage.banner"):
        target = p.get("for_event")
        if target and target not in emitted:
            problems.append(
                f"a header banner describes the event {target!r}, which was "
                f"never published; the header would name a screen that is not "
                f"there")
        # A BANNER MAY BE DECLARED TO HAVE NO WORD, AND THAT IS NOT THE SAME
        # AS HAVING LOST ONE. Sanaa's seven stage words cover seven of the nine
        # stages the contract fixes; the feasibility beat has none of hers, and
        # every candidate contradicts her ORDER, so it declares an empty string
        # rather than being given an invented word. This line was written when
        # every banner carried text and could not tell that decision from an
        # accident.
        #
        # ``authored`` IS WHAT SEPARATES THEM and it is the payload's own flag,
        # not an inference here: ``demo_sequencer.resolve_banner`` reports True
        # for a stage that declares its word (including declaring that it has
        # none) and False for a stage nothing declared at all. So an empty
        # banner nobody wrote is still a finding, which is the case this line
        # exists for.
        authored = p.get("authored")
        declared_empty = (authored is True)
        if not _nonempty(p.get("text")) and not declared_empty:
            problems.append("a header banner carries no text")
    return problems


def _limb_discussion(events, refusal, act) -> list[str]:
    problems = []
    entries = _payloads_of(events, "transcript.entry")
    roles = {str(p.get("role") or "").upper() for p in entries}
    expert = roles & _EXPERT_ROLES
    if len(expert) < 2:
        problems.append(
            f"the conversation panel carries {len(expert)} expert voice(s) "
            f"{sorted(expert)}; the protocol's stage 4 is a DISCUSSION between "
            f"the researcher, the engineer and the numericist")
    if len([p for p in entries if _nonempty(p.get("message"))]) < 3:
        problems.append("fewer than three spoken entries reach the "
                        "conversation panel")
    # THE ASSUMPTIONS SIDE, in two limbs on purpose. Her protocol stage 4 asks
    # for a table splitting USER-DEFINED from LAB-DEFINED with a value and unit
    # on every quantity. Two different things can fail -- the CONTENT and the
    # SHAPE -- and collapsing them into one problem would leave a reader unable
    # to tell which.
    if not _payloads_of(events, "demo.assumption"):
        problems.append("no demo.assumption was published; the "
                        "user-assumption correction beat her stage 4 asks for "
                        "does not exist")
    # THE USER/LAB SPLIT IS SWEPT ACROSS THE WHOLE STREAM, and the first cut of
    # this limb was wrong in a way worth recording. It looked for the split
    # inside the `demo.assumption` payload alone and reported a healthy act as
    # failing. `demo.assumption` is the CORRECTION BEAT -- the one assumption
    # the team corrects on camera -- while the split itself is spoken into the
    # conversation panel ("What the request fixes ... What this lab supplies").
    # Two different screens, and the limb was reading the wrong one. It was
    # caught only because the selftest asserts the clean stream is not red,
    # which is the half of a planted control that is easiest to leave out.
    import re as _re

    import live_pass_jet_flap as LP

    user_side = lab_side = False
    for event in events:
        for _key, text, _zone in LP._rendered_strings(event):
            if _re.search(r"what the request|the request (fixes|sets|gives)"
                          r"|user[- ]defined|you (fixed|specified|gave)",
                          text, flags=_re.I):
                user_side = True
            if _re.search(r"this lab supplies|lab[- ]defined|representative "
                          r"(propert|value)|because the request does not",
                          text, flags=_re.I):
                lab_side = True
    if not (user_side and lab_side):
        got = ("only the request side" if user_side else
               "only the lab side" if lab_side else "neither side")
        problems.append(
            f"the assumptions never split what the REQUEST fixed from what the "
            f"LAB supplied ({got} is stated anywhere on the wire); her stage 4 "
            f"asks for both, and without them a viewer cannot tell which "
            f"numbers were theirs")
    return problems


def _limb_assumptions_table(events, refusal, act) -> list[str]:
    """The SHAPE of the assumptions screen, kept apart from its content.

    A STRICT READING OF HER WORD "TABLE", kept as its own limb because content
    and shape fail differently and a reader needs to know which. Her checklist
    says "assumptions table present", and a table is a shape a program can see:
    a `transcript.table`, not a `transcript.entry` of bullets.

    IT WAS RED WHEN THIS LIMB WAS WRITTEN, hours ago, and it is green now. The
    jet-flap act then published its assumptions as bullets and its three tables
    were the mesh resolution, the instrument checks and the lift table; it now
    publishes `jf_assumptions` -- "What the request set, and what the lab set",
    with Quantity, Value, Unit and Set-by over eight rows, which is her stage 4
    almost word for word. The history is kept because it is the argument for
    writing the strict reading rather than widening "table" until the tree
    turned green: the widening would have been permanent, and the act was four
    hours from doing the thing properly.
    """
    tables = _payloads_of(events, "transcript.table")
    ids = [str(t.get("table_id") or "") for t in tables]
    titles = [str(t.get("title") or "").lower() for t in tables]
    if any("assum" in i.lower() for i in ids) or any("assum" in t for t in titles):
        return []
    return [f"no assumptions TABLE is published: the tables on the wire are "
            f"{ids or 'none'}. The assumptions reach the screen as bulleted "
            f"prose in a transcript entry. Her checklist line reads "
            f"'assumptions table present'; a table is a shape a program can "
            f"see, and this is not one."]


def _limb_mesh(events, refusal, act) -> list[str]:
    problems = []
    mesh = _payloads_of(events, "demo.mesh")
    if not mesh:
        return ["no demo.mesh was published; the meshing stage produced no "
                "screen at all"]
    m = mesh[0]
    # `meshed` is True only when the REAL mesher ran AND the cell count read
    # back off the written polyMesh matched the solved grid within tolerance
    # (demo_sequencer._run_mesher). It is the difference between a stage that
    # says "Meshing" and a stage that meshes.
    if not m.get("meshed"):
        problems.append(
            "the real mesher did not run, so the cell count on screen is a "
            "number the act declared rather than a grid anybody built")
    # TWO WAYS THE GRID CAN BE SHOWN AS REAL CELLS, and the line is satisfied
    # by either. `drawn` reports the cell-by-cell canvas draw; `pictured`
    # reports that the grid reached the screen at all, which is now normally a
    # ParaView panel rendered off the case's own polyMesh. Sanaa retired the
    # canvas as a visual source on 2026-09-01, so a checklist that only knew
    # about the draw would fail an act for obeying her.
    #
    # WHAT IS STILL ENFORCED, AND IT IS THE PART THAT MATTERS. The old draw was
    # sliced out of the same polyMesh the on-screen count cites, so the picture
    # could not be of another grid without the number moving too. A rendered
    # panel carries no cell list, so the coupling is checked instead: the
    # panel's own count must equal the count the meshing card prints. This
    # campaign holds two grids on reference areas differing by a hundred, and
    # that equality is what keeps them off one screen.
    panels = [p for p in _payloads_of(events, "mesh.panel")
              if str(p.get("panel") or "").startswith("mesh")]
    grid = _payloads_of(events, "mesh.grid")
    if not m.get("drawn") and not m.get("pictured"):
        problems.append(
            "no grid reached the viewport, so 'mesh shown as real cells' is "
            "not what the screen does; it shows a cell COUNT")
    if not grid and not panels:
        problems.append("neither mesh.grid nor a rendered grid panel was "
                        "published, so the viewport never receives a grid")
    elif grid and not grid[0].get("cells"):
        problems.append("mesh.grid carries no cell count")
    elif panels:
        printed = _digits(m.get("cells"))
        for panel in panels:
            shown = panel.get("cells")
            if not shown:
                problems.append("a rendered grid panel carries no cell count, "
                                "so nothing ties the picture to the number")
            elif printed is not None and int(shown) != printed:
                problems.append(
                    f"a rendered grid panel records {int(shown):,} cells while "
                    f"the meshing card prints {printed:,}; the picture and the "
                    f"number beside it are two different grids")
    res = [t for t in _payloads_of(events, "transcript.table")
           if "resolution" in str(t.get("table_id") or "").lower()
           or "resolution" in str(t.get("title") or "").lower()]
    if not res:
        problems.append("no resolution table is published")
    elif not res[0].get("rows"):
        problems.append("the resolution table has headers and no rows")
    return problems


def _limb_monitors(events, refusal, act) -> list[str]:
    problems = []
    frames = _payloads_of(events, "solve.frame")
    if not frames:
        return ["no solve.frame was published, so there are no monitors on "
                "screen to arrange as anything"]
    labels = [str(f.get("label") or "") for f in frames]
    distinct = sorted(set(labels))
    if len(distinct) < 2:
        problems.append(
            f"only {len(distinct)} monitor series is published ({distinct}); "
            f"'small multiples' needs several")
    # SIMULTANEITY, WHICH IS THE HALF THAT IS ACTUALLY CHECKABLE. Whether the
    # monitors sit side by side is layout and is not decidable here. Whether
    # they are RUNNING TOGETHER is decidable from the stream: if every frame of
    # series A precedes every frame of series B, the sweep is being shown one
    # point after another, and no arrangement of panels makes that simultaneous.
    if len(distinct) >= 2:
        spans = {}
        for i, lab in enumerate(labels):
            lo, hi = spans.get(lab, (i, i))
            spans[lab] = (min(lo, i), max(hi, i))
        ordered = sorted(spans.values())
        for (a_lo, a_hi), (b_lo, b_hi) in zip(ordered, ordered[1:]):
            if a_hi < b_lo:
                problems.append(
                    "the monitor series do not interleave: one finishes "
                    "entirely before the next begins, so the sweep runs one "
                    "point at a time rather than together")
                break
    concurrent = {f.get("concurrent") for f in frames}
    if concurrent == {False} and len(distinct) > 1:
        problems.append("the frames declare concurrent=False while carrying "
                        "several series; the screen would claim a sweep it is "
                        "not running together")
    return problems


def _limb_results(events, refusal, act) -> list[str]:
    problems = []
    results = _payloads_of(events, "demo.results")
    if not results:
        return ["no demo.results was published; the act has no results screen"]
    r = results[0]
    if not _nonempty(r.get("cost")):
        problems.append("the results screen carries no compute line; her "
                        "stage 6 asks for compute time, estimate against "
                        "actual")
    if not _nonempty(r.get("estimate")):
        problems.append("the results screen states an actual cost with no "
                        "forecast beside it, so estimate-against-actual "
                        "cannot be read (CLAUDE.md rule 12)")
    # A RESULTS TABLE, not merely results prose. R1: numbers live in tables.
    # The mesh-resolution and instrument-check tables are not it, so they are
    # excluded by name; anything else published as a table counts.
    tables = [t for t in _payloads_of(events, "transcript.table")
              if "resolution" not in str(t.get("table_id") or "").lower()
              and "planted" not in str(t.get("table_id") or "").lower()]
    if not tables:
        problems.append("no results table is published; the numbers reach the "
                        "screen as sentences")
    elif not any(t.get("rows") for t in tables):
        problems.append("the results table has no rows")
    # THE CONCLUSION. It is the last thing the act says and it closes the
    # digest's Conclusion phase; an act whose last publication is a table ends
    # on a table, which her protocol forbids in as many words.
    entries = _payloads_of(events, "transcript.entry")
    phase_at = None
    for i, p in enumerate(entries):
        if str(p.get("role") or "").upper() == "PHASE" and \
                "conclusion" in str(p.get("message") or "").lower():
            phase_at = i
    if phase_at is None:
        problems.append("no Conclusion phase is opened, so the act ends "
                        "without one")
    elif not any(_nonempty(p.get("message")) for p in entries[phase_at + 1:]):
        problems.append("the Conclusion phase opens and nothing is said under "
                        "it")
    return problems


def _limb_report(events, refusal, act) -> list[str]:
    problems = []
    report = _payloads_of(events, "report.ready")
    if not report:
        return ["no report.ready was published, so the Report tab stays empty "
                "for the whole act"]
    rep = report[0]
    for field in ("title", "abstract", "methods", "results",
                  "next_investigations"):
        if not _nonempty(rep.get(field)):
            problems.append(f"the Report tab's {field} is empty")
    # PLOTS REACH THE REPORT BY TWO ROUTES and the renderer takes their union
    # (control_room.html renderMemo: "the union of the report's own plot
    # manifest (rep.plots ...) and everything that streamed in live"). Either
    # route satisfies the checklist line; NEITHER does not.
    plots = _events_of(events, "plot.ready")
    if not _nonempty(rep.get("plots")) and not plots:
        problems.append("no figure reaches the Report tab by either route: "
                        "the report carries no plot manifest and no plot.ready "
                        "was published")
    # THE FIGURE STANDARD, TEXT HALF ONLY. Sanaa's 03:10Z standard: title at
    # most 10 words, one caption line of at most 20 words. `demo_mode.Figure`
    # enforces both at construction, so this re-reads them ON THE WIRE, where a
    # caption that was dropped between the dataclass and the payload would show
    # up. The standard's other clauses -- axis labels with units, a colour bar
    # with numeric ticks, a legend inside the axes -- live INSIDE the PNG, and
    # nothing here reads pixels.
    for p in (e.get("payload") or {} for e in plots):
        title, caption = str(p.get("title") or ""), str(p.get("caption") or "")
        if not title.strip():
            problems.append("a figure reaches the Report tab with no title")
        elif len(title.split()) > 10:
            problems.append(f"figure title is more than 10 words: {title!r}")
        if not caption.strip():
            problems.append(f"figure {title!r} reaches the Report tab with no "
                            f"caption")
        elif len(caption.split()) > 20 or "\n" in caption:
            problems.append(f"figure caption is not one line of at most 20 "
                            f"words: {caption!r}")
    return problems


def _limb_convergence(events, refusal, act) -> list[str]:
    """Either the band is shown, or the platform says it is coming. Never neither.

    Her stage 8 is explicit that the platform ALWAYS runs the study, so the
    demo shows it as done or as automatically underway and never as absent.
    That is a disjunction, and it is written here as one: a gate that demanded
    the band would fail an act legitimately taking the second branch, and a
    gate that accepted the sentence alone would let an act take the second
    branch forever.

    THE SENTENCE IS MATCHED BY MEANING, NOT BY HER LITERAL WORDING. Her example
    reads "lands in your inbox with the certificate"; the jet-flap act says
    "Grid convergence study launched and results in your box in a few minutes."
    Those are the same promise and a literal-string check would fail the act
    for paraphrasing an example. So the pattern asks for the two things that
    make the promise real: the study named, and a delivery to the user.
    """
    import re as _re

    import live_pass_jet_flap as LP

    said = declined = False
    for event in events:
        for _key, text, _zone in LP._rendered_strings(event):
            names_study = _re.search(
                r"convergence\s+stud(y|ies)|grid\s+convergence", text,
                flags=_re.I)
            if names_study and \
               _re.search(r"\b(inbox|your box|in your|comes? to you|sent to "
                          r"you|with the certificate)\b", text, flags=_re.I):
                said = True
            # THE THIRD BRANCH (Sanaa 1100Z, adjoint act): the REQUEST
            # itself declines the study ("dont run convergence study" is now
            # in that act's registered prompt), and her always-run rule is
            # overridden only by the customer's own words. So this branch
            # requires BOTH the study named AND the decline attributed to
            # the request or customer in the same sentence-stream string; a
            # passive "the study was declined" attributes it to nobody,
            # reads as the platform's own omission, and does NOT satisfy the
            # limb (its planted control below proves that).
            if names_study and _re.search(
                    r"\b(request|customer)\b[^.?!]{0,80}\bdeclin"
                    r"|\bdeclined\s+by\s+the\s+(request|customer)\b",
                    text, flags=_re.I):
                declined = True
        if said or declined:
            break
    # THE OTHER BRANCH: a band on every number. The report's result rows carry
    # `envelope`, which is where a discretisation band would be stated.
    banded = False
    report = _payloads_of(events, "report.ready")
    if report:
        rows = report[0].get("results") or []
        if rows and all(_nonempty(r.get("envelope")) for r in rows
                        if isinstance(r, dict)):
            banded = True
    if said or banded or declined:
        return []
    return ["the convergence study is neither shown as done (no band on the "
            "report's result rows), nor promised (no sentence naming the "
            "study and its delivery to the user), nor declined by the "
            "request (no sentence naming the study and attributing the "
            "decline to the request or customer). Her stage 8 allows the "
            "first two for every act, her 1100Z prompt addition allows the "
            "third where the request itself forbids the study, and the "
            "screen never stays silent about it."]


def _limb_language(events, refusal, act) -> list[str]:
    """The lab's own sweep, plus the terms her list has grown since."""
    import live_pass_jet_flap as LP

    problems = []
    for v in LP.sweep_language(events):
        problems.append(f"[demo_mode] {v['event']}.{v['key'].split('.')[-1]}: "
                        f"{v['reason']}")
    for v in _supplementary_hits(events):
        problems.append(f"[supplement] {v['event']} {v['key']}: {v['reason']}")
    return problems


#: (id, Sanaa's line, classification, the enforced half, the half no program
#: here can reach, the limb). The classification strings are printed verbatim
#: beside every result, so nobody reads a green line without also reading what
#: green does not cover.
CHECKLIST: tuple[tuple, ...] = (
    ("stl", "STL is the solved geometry and renders on load",
     "PARTIALLY ENFORCED",
     "the served surface is measured equal to the solved body and lives in the "
     "served directory (validate_act, geometry.matches); the announcement is "
     "published exactly once and BEFORE the first stage opens",
     "that the browser actually painted the surface. No WebGL, no viewport, no "
     "paint here -- a human watches the panel fill.",
     _limb_geometry),
    ("no_tessellation", "Tessellated canvas never paints on a ParaView act",
     "PARTIALLY ENFORCED",
     "a stream that serves a rendered geometry panel carries zero "
     "geometry.ready events at any index, so the page's triangle canvas is "
     "never given a surface to draw; an act declaring a rendered geometry "
     "panel that publishes none is refused rather than read as clean",
     "the PRE-MISSION upload preview: before any act event arrives, "
     "control_room.html's own upload path may paint the plain surface view, "
     "and no act stream can forbid what the page does before the act "
     "exists. That window is page-owned (loadGeometry / paraviewOwned) and "
     "needs a display-lane fix plus an eye on the recording.",
     _limb_no_tessellation),
    ("stages", "Header stages advance and match what is on screen",
     "PARTIALLY ENFORCED",
     "the nine stages are published once each in order, and every header "
     "banner names an event that was really published",
     "that the header and the card under it are in step AT ANY INSTANT. "
     "control_room.html paints the header through setStageBanner, which is "
     "'latest-wins and unpaced', while the stage cards ride a PACED queue -- so "
     "the header can legitimately run ahead of the card describing it. That is "
     "a timing property of the browser and needs an eye on the recording.",
     _limb_stages),
    ("discussion", "Expert discussion present, assumptions table present "
                   "(discussion + content)",
     "ENFORCED",
     "at least two distinct expert voices speak, at least three entries reach "
     "the panel, and the assumptions screen splits what the request fixed from "
     "what the lab supplied",
     "whether the discussion is any GOOD. Presence is checkable; judgement is "
     "not, and the checklist line asks only for presence.",
     _limb_discussion),
    ("assumptions_table", "... assumptions table present (shape)",
     "ENFORCED",
     "an assumptions table is published as a table, not as bulleted prose",
     "whether the table's own rows are RIGHT -- that every quantity carries a "
     "value and a unit, and that the Set-by column is honest. The shape is "
     "checkable; the truth of eight rows is a reading.",
     _limb_assumptions_table),
    ("mesh", "Mesh shown as real cells; resolution table present",
     "ENFORCED",
     "the real mesher ran and its written mesh reproduced the solved cell "
     "count; a cell-by-cell grid payload was produced and published; the "
     "resolution table is present with rows",
     "whether the drawn grid is LEGIBLE on camera -- cell density, zoom, "
     "contrast. A human looks at it.",
     _limb_mesh),
    ("monitors", "Sweep/multipoint monitors as small multiples on one screen",
     "PARTIALLY ENFORCED",
     "several monitor series exist and their frames INTERLEAVE, so the points "
     "are running together rather than one after another",
     "'as small multiples ON ONE SCREEN'. This is pure layout -- panel count, "
     "grid arrangement, whether they fit above the fold. Nothing on this box "
     "executes CSS. A human looks at one frame of the recording.",
     _limb_monitors),
    ("results", "Results table, compute line, conclusion",
     "ENFORCED",
     "a results table with rows, a compute line with a forecast beside the "
     "actual, and a Conclusion phase with something said under it",
     "whether the conclusion is the RIGHT two sentences. Presence and shape "
     "are checkable; editorial quality is not.",
     _limb_results),
    ("report", "Report tab populated: plots to the figure standard, summary, "
               "next steps",
     "PARTIALLY ENFORCED",
     "the report carries a title, abstract, methods, results and next "
     "investigations; at least one figure reaches the tab; every figure's "
     "title is at most 10 words and its caption one line of at most 20",
     "the figure standard INSIDE the image: axis labels with units, a colour "
     "bar with numeric ticks, a legend inside the axes. Those are pixels in a "
     "PNG and nothing here reads pixels. Also unmeasurable: whether plots "
     "arriving by the live route drain the paced queue before the viewer "
     "reaches the tab.",
     _limb_report),
    ("convergence", "Convergence study shown done, the 'lands in your "
                    "inbox' line, or declined by the request",
     "ENFORCED",
     "one of the two branches is demonstrably taken -- a band on every report "
     "result row, or a sentence naming the study and its delivery to the user "
     "-- and neither is never accepted",
     "nothing structural. The matching is by meaning rather than by her "
     "literal example, so a paraphrase far enough from both patterns could "
     "read as absent; that direction is the safe one.",
     _limb_convergence),
    ("language", "Zero forbidden language on any screen",
     "PARTIALLY ENFORCED",
     "every string on the fields control_room.html demonstrably renders is put "
     "through demo_mode.check_demo_language (paths, case/lesson/docket ids, "
     "pids, ports, commit hashes, gate vocabulary with its uppercase "
     "inflections) plus the supplementary list above",
     "two things. (1) BOTH ENUMERATIONS ARE HUMAN-MAINTAINED: the vocabulary "
     "is the words Sanaa has said so far, and the rendered-field table is the "
     "keys somebody read out of the renderer. A word she has not yet named, or "
     "a field a renderer edit newly displays, is invisible to this. (2) Text "
     "the PAGE ITSELF hardcodes is not on the wire at all; only two such "
     "strings are known and swept by hand. 'Zero forbidden language' is "
     "therefore enforced AS SPECIFIED, not absolutely.",
     _limb_language),
)


def checklist_problems(events: list, refusal: str | None, act) -> dict:
    """Every limb's problems for one act's stream.

    A REFUSAL FAILS EVERY LIMB IT COULD HAVE REACHED, and does not skip them.
    An act that stops at the solving stage published no results, no report and
    no convergence sentence; reporting those as clean because nothing was found
    would be the exact false green this gate exists to prevent. Absent evidence
    is a failure, never a pass.
    """
    out = {}
    for key, _line, _cls, _enf, _unenf, fn in CHECKLIST:
        try:
            out[key] = list(fn(events, refusal, act))
        except Exception as exc:                               # noqa: BLE001
            out[key] = [f"the limb itself raised {type(exc).__name__}: {exc}"]
    if refusal is not None:
        for key in out:
            out[key].append(
                f"the act stopped before finishing, so this line could not be "
                f"satisfied even in principle: {refusal}")
    return out


def checklist(verbose: bool = True) -> int:
    """Drive every registered act and grade it against the nine lines."""
    try:
        acts = _load_acts()
    except Exception as exc:                                   # noqa: BLE001
        print(f"HARNESS FAILED: could not import the acts: "
              f"{type(exc).__name__}: {exc}")
        return 2
    if not acts:
        print("HARNESS FAILED: no acts registered; this checklist would pass "
              "vacuously and must not")
        return 2

    # A REGISTERED ACT THIS GATE CANNOT NAME A MODULE FOR IS A HARNESS FAILURE,
    # not a skip: it would be graded on nothing and counted as clean.
    missing = sorted(set(acts) - set(_PLANT_ACT_MODULES))
    if missing:
        print(f"HARNESS FAILED: registered acts {missing} have no module named "
              f"in this gate, so they would be silently ungraded")
        return 2
    by_module = _PLANT_ACT_MODULES

    bad = 0
    for key in sorted(acts):
        print(f"\n  {key}")
        events, refusal = _collect(key, by_module[key])
        if refusal:
            print(f"      the act STOPPED before the end: {refusal}")
        findings = checklist_problems(events, refusal, acts[key])
        for cid, line, cls, _enf, _unenf, _fn in CHECKLIST:
            problems = findings.get(cid, [])
            mark = "FAIL" if problems else "ok  "
            if problems:
                bad += 1
            if problems or verbose:
                print(f"      [{mark}] {cls:20s} {line}")
            for p in problems[:6]:
                print(f"               - {p}")
            if len(problems) > 6:
                print(f"               - ... and {len(problems) - 6} more")
    print(f"\n{bad} checklist line(s) failed across {len(acts)} act(s).")
    return 1 if bad else 0


# ---------------------------------------------------------------------------
# The planted controls
# ---------------------------------------------------------------------------
#
# CLAUDE.md rule 3, applied to a checklist rather than to a reader: a clean
# result from an instrument not shown able to report a dirty one is not
# evidence. Every limb above is a limb that can only ever report "nothing
# wrong", so every limb below is planted before its silence is believed.
#
# AND PLANTED IN BOTH DIRECTIONS. A control validated only against failure is
# half a control -- this lab paid for that twice in one day, once with a crash
# filter that would have fired on every healthy run and once with one that
# would have missed every real crash. So each plant asserts TWO things: the
# planted stream produces a problem the clean stream does not have (the plant
# is visible), and the clean stream does not carry that problem (the limb is
# not simply always-red). The set difference is the mechanism, because an exit
# code cannot tell a limb that saw the plant from one already failing.
#
# THE VOCABULARY PLANTS ARE WRITTEN BY HAND, one per alternative and one per
# inflection, and NONE is generated from the pattern it tests. A plant derived
# from its own pattern proves only that a regex matches itself. This is the
# defect that reached a filmed screen twice: \bPASS\b does not match PASSED,
# \bdefect\b does not match defects, and the second instance survived BECAUSE
# THE FIRST HAD BEEN FIXED -- the repair created the belief the class was
# handled.

#: One per alternative and one per inflection of SUPPLEMENTARY_NEVER. Hand
#: written. The marker is the substring the refusal must quote, so a plant that
#: fires for the WRONG rule is caught: a plant passing for another reason
#: proves nothing about the rule it was written for.
SUPPLEMENT_PLANTS: tuple[tuple[str, str, str], ...] = (
    # "prior runs" -- three adjectives, singular and plural.
    ("prior run", "The prior run settled at the same lift", "prior run"),
    ("prior runs", "Both prior runs settled at the same lift", "prior runs"),
    ("previous run", "The previous run settled at the same lift",
     "previous run"),
    ("earlier runs", "Two earlier runs settled at the same lift",
     "earlier runs"),
    # "agreements", countable plural only. The singular is deliberately legal;
    # see SUPPLEMENTARY_NEVER's note.
    ("agreements", "The agreements cover four blowing levels", "agreements"),
    # "tiers" without a digit -- the gap NEVER_PHRASES' \btier[-\s]?\d\b leaves.
    ("tier, bare", "This sits in the upper tier", "tier"),
    ("tiers, plural", "The tiers are assigned after the sweep", "tiers"),
    # "not recorded" bare, in two inflected contexts.
    ("not recorded", "The wall time was not recorded", "not recorded"),
    ("were not recorded", "The residuals were not recorded", "not recorded"),
    # "no solver".
    ("no solver", "There is no solver behind this figure", "no solver"),
    # "already finished" and the inflections NEVER_PHRASES misses.
    ("already finished", "The sweep already finished", "already finished"),
    ("already finishes", "The sweep already finishes early", "already finishes"),
    ("already finishing", "The sweep is already finishing",
     "already finishing"),
    ("already done", "The sweep is already done", "already done"),
    ("already complete", "The sweep is already complete", "already complete"),
    ("already completed", "The sweep already completed", "already completed"),
    # the WORD "id", which NEVER_PHRASES catches only as a VALUE.
    ("case id, as words", "The case id is shown beside each point", "case id"),
    ("run ids, plural", "The run ids are listed in the table", "run ids"),
    ("mission id", "The mission id appears on the header", "mission id"),
    ("point ids", "The point ids number one to five", "point ids"),
)

#: (event, key, the value is a list) -- one rendered surface each, chosen to
#: span the page: the Report tab's densest prose, the conversation panel, a
#: figure caption, the viewport label, a table heading and the results screen.
#: Every one is a key `live_pass_jet_flap.TIER1_RENDERED` names with the
#: control_room.html line that draws it, or a tier-2 payload the publication
#: guard walks.
SURFACE_PLANTS: tuple[tuple[str, str, bool], ...] = (
    ("report.ready", "abstract", True),
    ("transcript.entry", "message", False),
    ("plot.ready", "caption", False),
    # THE VIEWPORT LABEL, BY WHICHEVER ROUTE THIS ACT USES. A surface reaches
    # the panel either as an STL announcement the canvas draws, or as a
    # rendered picture of the solved case; both write the same element. The
    # plant is made on whichever the act publishes, because an entry naming
    # only the retired route would report "cannot be shown able to read" and
    # look like blindness when it is only absence — and an entry naming only
    # the new route would go quiet on every act still using the old one.
    (("geometry.ready", "mesh.panel"), "label", False),
    ("transcript.table", "title", False),
    ("demo.results", "solver", False),
)


#: One per structural limb. Each mutates a COPY of a healthy stream in the one
#: way that limb exists to catch.
def _plant_drop_event(name):
    def mutate(events):
        return [e for e in events if e.get("event") != name]
    return mutate


def _plant_drop_surface(events):
    """Announce no surface at all, by EITHER route.

    A plant aimed at one of the two announcements would stop firing the moment
    an act moved to the other, and a plant that no longer fires is a check that
    is no longer being tested. Both go.
    """
    return [e for e in events if not _is_surface(e)]


def _plant_drop_grid(events):
    """Let no grid reach the viewport, by EITHER route, and say so on the card.

    Dropping the events alone is not enough: the meshing card publishes
    ``drawn``/``pictured``, and the limb reads those first, so a stream with
    the grid events removed and the flags still True would fail for the right
    reason by luck rather than by construction.
    """
    out = []
    for event in copy.deepcopy(events):
        name = event.get("event")
        if name == "mesh.grid" or (
                name == "mesh.panel"
                and str((event.get("payload") or {}).get("panel") or ""
                        ).startswith("mesh")):
            continue
        if name == "demo.mesh":
            payload = event.get("payload") or {}
            payload["drawn"] = False
            payload["pictured"] = False
        out.append(event)
    return out


def _plant_grid_count_mismatch(events):
    """Put the OTHER grid's count on the picture and leave the card alone.

    This is the 39,984-versus-46,180 case in miniature: two grids on reference
    areas differing by a hundred, so a picture of one captioned with the
    other's number misreports lift by that ratio. The canvas draw made this
    impossible by construction, because it was sliced from the polyMesh the
    count cites; a rendered panel makes it possible again, and the check that
    replaces the construction is only worth something if it has been seen to
    fire.
    """
    out = copy.deepcopy(events)
    for event in out:
        if event.get("event") != "mesh.panel":
            continue
        payload = event.get("payload") or {}
        if str(payload.get("panel") or "").startswith("mesh"):
            payload["cells"] = 46180
    return out


def _plant_move_geometry_late(events):
    """Announce the surface after the walk has started."""
    out = [e for e in events if not _is_surface(e)]
    ready = [e for e in events if _is_surface(e)]
    if not ready:
        return out
    at = next((i for i, e in enumerate(out)
               if e.get("event") == _STAGE_ORDER_EVENT), 0)
    return out[:at + 1] + ready + out[at + 1:]


def _plant_scramble_stages(events):
    out = copy.deepcopy(events)
    begins = [i for i, e in enumerate(out) if e.get("event") == _STAGE_ORDER_EVENT]
    if len(begins) >= 2:
        a, b = begins[0], begins[-1]
        out[a]["payload"]["stage"], out[b]["payload"]["stage"] = (
            out[b]["payload"]["stage"], out[a]["payload"]["stage"])
    return out


def _plant_single_role(events):
    out = copy.deepcopy(events)
    for e in out:
        if e.get("event") == "transcript.entry":
            e["payload"]["role"] = "CHIEF ENGINEER"
    return out


def _plant_no_user_lab_split(events):
    """Blank the sentences that tell a viewer which numbers were theirs.

    Rewritten rather than deleted: an act that simply stops saying which side
    an assumption came from still speaks, still fills the panel, and looks
    entirely healthy. That is the shape this limb has to catch.
    """
    import re as _re

    out = copy.deepcopy(events)
    pattern = (r"what the request|the request (fixes|sets|gives)"
               r"|user[- ]defined|you (fixed|specified|gave)"
               r"|this lab supplies|lab[- ]defined|representative "
               r"(propert|value)|because the request does not")
    bland = "The setup is as described."
    for e in out:
        payload = e.get("payload") or {}
        for k, v in list(payload.items()):
            if isinstance(v, str) and _re.search(pattern, v, flags=_re.I):
                payload[k] = bland
            elif isinstance(v, list):
                payload[k] = [bland if isinstance(x, str) and
                              _re.search(pattern, x, flags=_re.I) else x
                              for x in v]
    return out


def _plant_unmeshed(events):
    out = copy.deepcopy(events)
    for e in out:
        if e.get("event") == "demo.mesh":
            e["payload"]["meshed"] = False
            e["payload"]["drawn"] = False
    return out


def _plant_sequential_sweep(events):
    """Reorder the frames so every series finishes before the next starts."""
    out = copy.deepcopy(events)
    frames = [(i, e) for i, e in enumerate(out)
              if e.get("event") == "solve.frame"]
    if len(frames) < 2:
        return out
    slots = [i for i, _ in frames]
    ordered = sorted((e for _, e in frames),
                     key=lambda e: str((e.get("payload") or {}).get("label")))
    for slot, ev in zip(slots, ordered):
        out[slot] = ev
    return out


def _plant_tessellation(events):
    """Plant the banned mix: a rendered geometry panel AND a geometry.ready.

    The host act may serve no rendered panel at all, so one is planted first
    where absent -- the limb's rule is about the MIX, and a plant that could
    not create the mix on an old-path act would be invisible there.
    """
    out = copy.deepcopy(events)
    has_panel = any(e.get("event") == "mesh.panel"
                    and (e.get("payload") or {}).get("panel") == "geometry"
                    for e in out)
    if not has_panel:
        out.insert(0, {"sequence": 0, "event": "mesh.panel",
                       "payload": {"panel": "geometry", "stage": "geometry",
                                   "url": "/api/plot/planted/surface.png",
                                   "label": "planted body"}})
    out.insert(1, {"sequence": 0, "event": "geometry.ready",
                   "payload": {"stage": "geometry", "label": "planted body",
                               "url": "/api/geometry?name=planted.stl"}})
    return out


def _plant_no_cost(events):
    out = copy.deepcopy(events)
    for e in out:
        if e.get("event") == "demo.results":
            e["payload"]["cost"] = ""
    return out


def _plant_long_caption(events):
    out = copy.deepcopy(events)
    for e in out:
        if e.get("event") == "plot.ready":
            e["payload"]["caption"] = " ".join(["word"] * 25)
            break
    return out


def _rewrite_convergence_strings(node, replacement):
    """Replace every convergence-naming string ANYWHERE in a payload.

    RECURSIVE ON PURPOSE, and the depth is the finding: the first cut of
    these plants walked only ``payload[k]`` and one level of list, while
    ``_rendered_strings`` descends into nested structures -- so an
    assumptions-table CELL ("Grid convergence study, declined by the
    request", a list inside ``rows`` inside the payload) kept the limb green
    under both convergence plants and the selftest reported them INVISIBLE
    (measured on the adjoint-wing host stream, 2026-09-02). A plant that
    reaches fewer surfaces than the limb it controls is not a control.
    """
    import re as _re

    if isinstance(node, str):
        return (replacement if _re.search(
            r"convergence\s+stud|grid\s+convergence", node, flags=_re.I)
            else node)
    if isinstance(node, list):
        return [_rewrite_convergence_strings(x, replacement) for x in node]
    if isinstance(node, dict):
        return {k: _rewrite_convergence_strings(v, replacement)
                for k, v in node.items()}
    return node


def _plant_no_convergence(events):
    """Remove ALL THREE branches: promise, bands, and the declined form."""
    out = copy.deepcopy(events)
    for e in out:
        payload = e.get("payload") or {}
        for k, v in list(payload.items()):
            payload[k] = _rewrite_convergence_strings(
                v, "The sweep settled at every point.")
        if e.get("event") == "report.ready":
            for row in payload.get("results") or []:
                if isinstance(row, dict):
                    row["envelope"] = ""
    return out


def _plant_unattributed_decline(events):
    """The declined branch's own control: a decline attributed to NOBODY.

    The third convergence branch (request-declined, Sanaa 1100Z) is only
    honest because the decline is the customer's: "the request declined the
    study". A passive "the grid convergence study was declined" names no
    decliner, reads as the platform's own omission, and must NOT satisfy the
    limb. This plant rewrites every convergence-naming string into exactly
    that passive form and blanks the report bands, so a limb that accepted
    an unattributed decline would read this stream clean and be caught here.
    """
    out = copy.deepcopy(events)
    passive = "The grid convergence study was declined."
    for e in out:
        payload = e.get("payload") or {}
        for k, v in list(payload.items()):
            payload[k] = _rewrite_convergence_strings(v, passive)
        if e.get("event") == "report.ready":
            for row in payload.get("results") or []:
                if isinstance(row, dict):
                    row["envelope"] = ""
    return out


STRUCTURAL_PLANTS: tuple[tuple[str, str, object], ...] = (
    ("stl", "the surface is announced after the walk has started",
     _plant_move_geometry_late),
    ("stl", "no surface is announced at all", _plant_drop_surface),
    ("no_tessellation", "a geometry.ready rides a stream that serves a "
                        "rendered geometry panel", _plant_tessellation),
    ("stages", "two stages swap places in the header",
     _plant_scramble_stages),
    ("discussion", "one voice speaks instead of a discussion",
     _plant_single_role),
    ("discussion", "the correction beat is never published",
     _plant_drop_event("demo.assumption")),
    ("discussion", "the assumptions stop saying which side each number came "
                   "from", _plant_no_user_lab_split),
    ("mesh", "the mesher did not run and nothing was drawn", _plant_unmeshed),
    ("mesh", "the grid never reaches the viewport", _plant_drop_grid),
    ("mesh", "the grid picture is of a different grid than the count",
     _plant_grid_count_mismatch),
    ("monitors", "the sweep points run one after another, not together",
     _plant_sequential_sweep),
    ("monitors", "no monitors are published at all",
     _plant_drop_event("solve.frame")),
    ("results", "the compute line is blank", _plant_no_cost),
    ("results", "the results screen never appears",
     _plant_drop_event("demo.results")),
    ("report", "a figure caption runs past the figure standard",
     _plant_long_caption),
    ("report", "the Report tab is never populated",
     _plant_drop_event("report.ready")),
    ("convergence", "neither the band nor the promise is on any screen",
     _plant_no_convergence),
    ("convergence", "the study is said to be declined but by nobody",
     _plant_unattributed_decline),
)

#: The act the plants are made against. It must be one that walks all nine
#: stages, because a plant into a stream that never reached the results screen
#: could not be seen there. Chosen by measurement at run time, not by name.
#:
#: MOTOR-THERMAL ADDED 2026-09-01. Two maps name the act modules in this gate
#: and only ``ACT_MODULES`` (line 86) was updated when the act registered, so
#: the checklist half refused with "registered acts ['motor-thermal'] have no
#: module named in this gate" and every team's checklist verification was
#: blind. THE REFUSAL WAS CORRECT and is not what was fixed: an act graded on
#: nothing counts as clean, so the harness is right to stop rather than grade
#: three of four and print a total. What was wrong is that the two maps could
#: drift at all -- this map is keyed by act and that one is a flat tuple, so
#: adding an act to one is not adding it to the other and nothing said so.
_PLANT_ACT_MODULES = {"jet-flap": "workflows.jet_flap_act",
                      "adjoint-wing": "workflows.adjoint_act",
                      "shock-reflection": "workflows.dmr_act",
                      "motor-thermal": "workflows.motor_thermal_act",
                      "battery-module": "workflows.battery_module_act"}

#: THE ASSERT THAT STOPS THE THIRD OCCURRENCE, rather than a third manual fix.
#: Every module named in ``ACT_MODULES`` must be reachable from this map, so a
#: fifth act added to one and not the other fails HERE, at import, naming the
#: act -- instead of at the point where the checklist silently has nothing to
#: plant into. L-221/L-222: a lesson is not applied until every call site
#: asserts it, and this is the second call site of one list of acts.
assert set(_PLANT_ACT_MODULES.values()) == set(ACT_MODULES), (
    "the two act-module maps in this gate disagree: "
    f"{sorted(set(ACT_MODULES) ^ set(_PLANT_ACT_MODULES.values()))} "
    "is named in one and not the other, so that act would be graded on "
    "nothing or could not host a plant")


def checklist_selftest() -> int:
    """Show every limb able to fail, and show the clean stream not failing it.

    Exit 0 when every plant fired and no plant's problem was already present in
    the clean stream; 1 when a plant was invisible; 2 when the harness could
    not do its job, which includes finding no act able to walk to the end.
    """
    import re as _re

    from workflows.demo_mode import check_demo_language, DemoContractError

    host_key = host_events = None
    for key, module in sorted(_PLANT_ACT_MODULES.items()):
        events, refusal = _collect(key, module)
        if refusal is None and events:
            host_key, host_events = key, events
            break
    if host_events is None:
        print("SELFTEST REFUSED: no registered act walks all nine stages, so "
              "no plant could be made into a complete stream. Every checklist "
              "line below the solving stage is untestable until one does.")
        return 2

    print(f"  planting into the {host_key} stream ({len(host_events)} events)")
    clean = checklist_problems(host_events, None, None)

    # --- the vocabulary plants ------------------------------------------
    # Planted at stage.banner.text: a key the rendered-field table really
    # reads, and the banner's only prose field. ONE PLANT PER COPY, so a single
    # detection can never stand in for twenty.
    host_at = _first_index(host_events, "stage.banner")
    if host_at is None:
        print("SELFTEST REFUSED: no stage.banner to plant into; the language "
              "sweep cannot be shown able to see anything")
        return 2

    import live_pass_jet_flap as LP

    invisible: list[str] = []
    redundant: list[str] = []
    fired = 0
    all_plants = list(LP.GATE_PLANTS) + list(LP.CLASS_PLANTS)
    for _label, text, marker in all_plants:
        salted = copy.deepcopy(host_events)
        salted[host_at]["payload"]["text"] = text
        hits = [v for v in LP.sweep_language(salted) if v["index"] == host_at]
        if not hits or not any(marker in v["reason"] for v in hits):
            invisible.append(f"[demo_mode] {text!r} was planted and the sweep "
                             f"did not refuse it for {marker!r}")
        else:
            fired += 1
    for label, text, marker in SUPPLEMENT_PLANTS:
        salted = copy.deepcopy(host_events)
        salted[host_at]["payload"]["text"] = text
        hits = [v for v in _supplementary_hits(salted) if v["index"] == host_at]
        if not hits or not any(_re.search(_re.escape(marker), v["reason"],
                                          flags=_re.I) for v in hits):
            invisible.append(f"[supplement] {label}: {text!r} was planted and "
                             f"the supplementary sweep did not refuse it for "
                             f"{marker!r}")
        else:
            fired += 1
        # DRIFT CONTROL. If demo_mode has since absorbed this term, say so, so
        # the supplement can be retired instead of quietly shadowing the real
        # vocabulary for the rest of its life.
        try:
            check_demo_language(text)
        except DemoContractError:
            redundant.append(label)

    # --- the sweep is planted on EVERY rendered surface, not just one ----
    # A sweep proven at one key is proven at one key. The vocabulary plants
    # above all land on `stage.banner.text`, which is one field of one event;
    # if `_rendered_strings` were blind to a whole surface -- the Report tab,
    # the figure captions, the viewport label -- every one of those plants
    # would still fire and the blindness would be invisible. So one violation
    # is planted on each surface a viewer actually reads, and each must be
    # seen by BOTH sweeps.
    for name, key, is_list in SURFACE_PLANTS:
        # A name may be a GROUP of alternative routes onto one element. The
        # plant lands on whichever the act publishes; it is invisible only when
        # the act publishes none of them.
        names = (name,) if isinstance(name, str) else tuple(name)
        at = next((i for i in (_first_index(host_events, n) for n in names)
                   if i is not None), None)
        if at is None:
            invisible.append(
                f"[surface] no {' or '.join(names)} event exists in the "
                f"{host_key} stream, so the sweep cannot be shown able to "
                f"read its {key}")
            continue
        name = host_events[at].get("event")
        salted = copy.deepcopy(host_events)
        text = "The prior runs are already done in tier 2"
        if is_list:
            existing = list(salted[at]["payload"].get(key) or [])
            salted[at]["payload"][key] = [text] + existing[1:]
        else:
            salted[at]["payload"][key] = text
        sup = [v for v in _supplementary_hits(salted) if v["index"] == at]
        dmo = [v for v in LP.sweep_language(salted) if v["index"] == at]
        if not sup or not dmo:
            invisible.append(
                f"[surface] a violation planted at {name}.{key} was seen by "
                f"{len(sup)} supplementary and {len(dmo)} demo_mode rule(s); a "
                f"rendered surface no sweep reads is how the first case id "
                f"reached a screen")
        else:
            fired += 1

    # --- the structural plants ------------------------------------------
    for cid, what, mutate in STRUCTURAL_PLANTS:
        salted = mutate(copy.deepcopy(host_events))
        after = checklist_problems(salted, None, None)
        new = set(after.get(cid, [])) - set(clean.get(cid, []))
        if not new:
            invisible.append(
                f"[{cid}] planting '{what}' produced no problem the clean "
                f"stream did not already have; that limb is not known to see "
                f"the defect it exists for")
        else:
            fired += 1

    # --- the other half of the control ----------------------------------
    # A limb that is always red would "detect" every plant by standing still.
    # Naming the limbs that are red on the CLEAN stream is what separates a
    # working control from a stuck one, and it is printed whether or not the
    # selftest passes.
    stuck = [cid for cid, problems in clean.items() if problems]

    total = (len(all_plants) + len(SUPPLEMENT_PLANTS) + len(SURFACE_PLANTS)
             + len(STRUCTURAL_PLANTS))
    print(f"  plants made                    : {len(all_plants)} demo_mode + "
          f"{len(SUPPLEMENT_PLANTS)} supplementary + "
          f"{len(SURFACE_PLANTS)} rendered-surface + "
          f"{len(STRUCTURAL_PLANTS)} structural = {total}")
    print(f"  plants that fired              : {fired}")
    print(f"  plants that were INVISIBLE     : {len(invisible)}")
    print(f"  limbs already red when clean   : {stuck or 'none'}")
    if redundant:
        print(f"  supplementary terms demo_mode now covers (retire them): "
              f"{redundant}")
    else:
        print(f"  supplementary terms demo_mode now covers: none -- every "
              f"term in the supplement is still load-bearing")
    for line in invisible:
        print(f"      - {line}")
    if invisible:
        print("SELFTEST FAILED: a plant was invisible, so at least one limb's "
              "clean result is not evidence.")
        return 1
    print("SELFTEST PASSED: every plant produced a refusal the clean stream "
          "does not carry, and the limbs red on the clean stream are named "
          "above rather than hidden.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true",
                        help="plant a missing provenance entry and prove the "
                             "gate reports it")
    parser.add_argument("--checklist-selftest", action="store_true",
                        help="plant one violation per checklist limb and per "
                             "vocabulary inflection, and prove each is seen")
    parser.add_argument("--startup-only", action="store_true",
                        help="the pre-2026-09-01 behaviour: only ask whether "
                             "each act can start, without driving it")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.checklist_selftest:
        return checklist_selftest()
    startup = check()
    if args.startup_only:
        return startup
    print()
    print("SHOOTING CHECKLIST (Sanaa, 2026-09-01 20:30Z). Each line carries "
          "what this gate does NOT check;")
    print("read it before believing a green one. Nothing here executes CSS, "
          "so no layout claim is tested.")
    return max(startup, checklist())


if __name__ == "__main__":
    raise SystemExit(main())
