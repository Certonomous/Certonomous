#!/usr/bin/env python3
"""Does the WIRE carry what the SHEET claims? Nothing else in this lab asks.

WHY THIS EXISTS, AND IT IS NOT A HUNCH. The same defect has now been found TWICE
BY ACCIDENT in one day:

  * the convergence-study line was fixed on FOUR SHEETS while the ACT went on
    publishing "grid independence not assessed" to the screen;
  * the reference-wing sheet has carried Lead Researcher, Lead Engineer and Lead
    Numericist since it was written, and the ACT published ONE voice.

Both were compliance repairs applied to the document and not to the thing that
renders. Finding the same class twice by luck is not luck; it is an instrument
gap, and it is measurable: EVERY sheet checker in this directory greps `.tex`
and reads ZERO act payloads. The sheets are swept, the wire is swept, and
nothing compares them.

WHAT THIS IS, AND WHAT IT DELIBERATELY IS NOT. It is a REQUIRED-CLAIM PRESENCE
CHECK, not a diff. The sheet is long-form prose and the wire is bulleted
telegraphese; a textual diff between them would be pure noise and would be
switched off within a day. So the unit is a CLAIM CLASS: a thing the protocol
says an act must carry, with one pattern for how it looks on a sheet and another
for how it looks on the wire.

THE FORCING PROPERTY IS THE WHOLE POINT AND IT IS WHAT MAKES THIS A GATE RATHER
THAN DOCUMENTATION. Two arms give it:

  1. EVERY DECLARED CLASS MUST BE PRESENT ON THE SHEET. A class that is declared
     and then quietly deleted from the sheet would otherwise pass forever by
     being vacuously satisfied.
  2. EVERY PROTOCOL-SHAPED CLAIM FOUND ON A SHEET MUST BELONG TO A DECLARED
     CLASS. This is the arm that makes ADDING a claim to a sheet fail the sweep
     until somebody declares it and wires it. Without it, the next author writes
     a new promise onto a sheet, the wire never learns about it, and this file
     stays green -- which is exactly the failure it was built for.

THE HONEST LIMIT. Arm 2 can only see claim SHAPES it knows: the
convergence-study promise, role signatures, certificate sentences, and the
user/lab split. A genuinely new KIND of claim, in a shape nobody has described,
is invisible here -- and that is a smaller hole than the one it closes, but it
is a hole and it is written down rather than left to be discovered.

    python3 docs/dafoam/demo/check_sheet_wire_parity.py
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "sdk"))
sys.path.insert(0, str(REPO / "scripts"))

os.environ.setdefault("CERTONOMOUS_NARRATION_PACE_MS", "0")
os.environ.setdefault("CERTONOMOUS_SWEEP_PACE_MS", "0")

#: The pairs this sweep can compare. A sheet with no act is REPORTED, never
#: silently skipped: "no act to compare against" is a finding about our
#: coverage, not an absence of a problem. A sweep that scores full marks while
#: silently not covering three of its subjects is the reader-that-cannot-see-a-
#: non-zero failure in a new place.
#:
#: AND THE GAP IS NOT A LIMITATION OF THIS SWEEP -- IT IS QUEUED WORK SEEN FROM
#: THE OTHER SIDE. SO-3 (PASS), D19M (GATE REACHED) and D19O (GATE REACHED) were
#: all ruled shootable, and their SHEETS ARE AHEAD OF THEIR ACTS: the documents
#: exist and the screens do not. So this coverage gap and the act backlog are
#: one gap from two directions, and building those acts closes both.
#: (sheet, act key, the module whose IMPORT registers that act). The module is
#: named because importing it is what registers the act -- the first run of this
#: sweep refused with "no act is registered as 'adjoint-wing'", which was the
#: right behaviour (it declined to compare against nothing) and my omission.
PAIRS = [("ACT_D_reference_wing_sheet.tex", "adjoint-wing",
          "workflows.adjoint_act")]
SHEETS_WITHOUT_ACTS = [
    "ACT_D_multipoint_optimisation_sheet.tex",
    "ACT_D_compressible_multipoint_sheet.tex",
    "ACT_D_aerofoil_section_sheet.tex",
]


class Claim:
    """One thing the protocol says an act must carry, on both surfaces."""

    def __init__(self, name: str, sheet: str, wire: str, why: str,
                 covers: str | None = None):
        self.name = name
        self.sheet = re.compile(sheet, re.I | re.S)
        self.wire = re.compile(wire, re.I)
        self.why = why
        #: What ARM 2 counts as belonging to this class. SEPARATE FROM `sheet`
        #: on purpose: `sheet` asks "is the canonical claim present at all",
        #: which is a whole-document question, while `covers` asks "is THIS
        #: snippet an instance of this class", which is a fragment question.
        #: Collapsing them made arm 2 report the sheet's own compliant
        #: paraphrases as undeclared -- the canonical pattern could not match a
        #: fragment that omitted a word.
        self.covers = re.compile(covers or sheet, re.I)


#: THE DECLARED CLASSES. Each is a protocol requirement, not a stylistic wish.
CLAIMS = [
    Claim("the convergence study is promised, never shown as absent",
          r"grid convergence study for this case is running",
          r"grid convergence study for this case is running",
          "Sanaa's stage 8: shown as done or as underway, NEVER as absent. "
          "This is the class that was fixed on four sheets and left off the "
          "wire for hours.",
          # COVERS THE CLAIM, NOT THE TOPIC.
          #
          # A GUARD KEYED TO A TOPIC CANNOT DISTINGUISH A CLAIM FROM ITS
          # NEGATION. `covers=r"convergence stud"` was the first attempt and
          # the forcing plant caught it: it matches "the convergence study is
          # running" AND "the convergence study is finished and the band is
          # attached" -- OPPOSITE STATEMENTS, IDENTICAL MATCH. Any pattern that
          # names the SUBJECT rather than the ASSERTION has this property, and
          # it reads as healthy precisely because it matches so much.
          #
          # WHAT THAT WOULD HAVE MEANT HERE IS NOT ABSTRACT: A2-GC CAP-STOPPED
          # AT L1 AND A1WR HAS NOT PRODUCED A FRAME. THERE IS NO BAND. An act
          # claiming one would have been a false statement, on camera, about
          # the one thing the convergence doctrine exists to enforce -- and it
          # would have looked MORE plausible to a viewer than the honest
          # "underway", because "done" is what a finished platform says. A
          # premature "done" is worse than an absent line: absence is visible
          # and a false completion is not.
          covers=r"convergence stud\w*[^.]{0,140}?"
                 r"(running|lands in your inbox|your box|with the certificate)"),
    Claim("three expert voices, not one narrator",
          r"\\rolesig\{Lead Researcher\.\}.*\\rolesig\{Lead Engineer\.\}"
          r".*\\rolesig\{Lead Numericist\.\}",
          r"\b(researcher|numericist)\b",
          "Sanaa's stage 4 is a DISCUSSION between the researcher, the "
          "engineer and the numericist. The sheet had all three; the act "
          "published one.",
          # THE THREE DECLARED ROLES ONLY. `\\rolesig` alone absorbed a planted
          # "Lead Aerodynamicist" -- a fourth voice nobody declared and the
          # wire has never heard of.
          covers=r"\\rolesig\{Lead (Researcher|Engineer|Numericist)\.\}|"
                 r"Lead (Researcher|Engineer|Numericist)"),
    Claim("the user/lab split is stated",
          r"Where these numbers come from|fixed before the solver starts",
          r"this lab supplies|lab[- ]defined",
          "Her stage 4 asks which numbers were the user's and which the "
          "lab's. A sheet saying where numbers come from while the wire does "
          "not is the same split failing on one surface.",
          covers=r"the (request|lab) (set|sets|fixed|fixes|supplies)|"
                 r"Where these numbers come from"),
    Claim("the single-grid limitation travels",
          r"single grid|one grid|relative to it",
          r"one grid|single mesh|relative to it",
          "One mesh is the whole discretisation story of this act; a sheet "
          "that says so while the screen does not is the defect this file "
          "exists for."),
]

#: ARM 2's VOCABULARY: claim SHAPES that must map to a declared class. Adding a
#: new instance of one of these to a sheet fails this sweep until it is
#: declared above and carried on the wire.
PROTOCOL_SHAPES = [
    # BOTH BRANCHES OF STAGE 8, because Sanaa's rule offers two: shown as DONE
    # (a band on every number) or shown as UNDERWAY. The first version of this
    # knew only the underway branch, so a planted claim that the study was
    # FINISHED and its band ATTACHED was invisible to arm 2 -- the forcing
    # plant caught it, and it is the more dangerous branch of the two: a
    # premature "done" is a claim about work that has not happened.
    ("a convergence-study promise",
     re.compile(r"convergence stud(?:y|ies)[^.]{0,140}?"
                r"(?:inbox|your box|running|with the certificate|finished|"
                r"complete|attached|band is)", re.I)),
    ("an expert role signature", re.compile(r"\\rolesig\{([^}]*)\}")),
    ("a certificate statement",
     re.compile(r"certificate is (?:issued|sealed|attached)[^.]{0,80}", re.I)),
    ("a user/lab attribution",
     re.compile(r"(?:the request|the lab) (?:set|sets|fixed|fixes|supplies)",
                re.I)),
]


def wire_strings(act_key: str, module: str
                 ) -> tuple[list[str], str | None, list[dict], object]:
    """Every string this act actually publishes, through the shared dispatcher.

    THROUGH `run_act`, NOT the act's own `drive()`, deliberately: `run_act` is
    the path the pre-shoot gate uses, and an act half-wired through the shared
    dispatcher is exactly the condition this family spent the afternoon fixing.
    """
    import importlib
    importlib.import_module(module)          # importing REGISTERS the act
    from workflows import make_transcript
    from workflows.demo_sequencer import run_act
    import live_pass_jet_flap as LP

    events: list[dict] = []

    def emit(name, payload):
        events.append({"event": str(name),
                       "payload": json.loads(json.dumps(payload, default=str))})

    script = make_transcript(act_key, emit)
    err = None
    try:
        with redirect_stdout(io.StringIO()):
            run_act(act_key, emit=emit, script=script, sleep=lambda _s: None)
    except Exception as exc:                                   # noqa: BLE001
        err = f"{type(exc).__name__}: {exc}"
    out: list[str] = []
    for event in events:
        for _key, text, _zone in LP._rendered_strings(event):
            out.append(str(text))
    from workflows.demo_sequencer import registered_acts
    return out, err, events, registered_acts().get(act_key)


def compare(sheet_name: str, body: str, blob: str) -> tuple[list[str], list[str]]:
    """(problems, printable rows) for one sheet/wire pair. PURE, so it can be planted."""
    problems: list[str] = []
    rows: list[str] = []
    for claim in CLAIMS:
        on_sheet = bool(claim.sheet.search(body))
        on_wire = bool(claim.wire.search(blob))
        mark = "ok  "
        if not on_sheet:
            mark = "GONE"
            problems.append(
                f"declared claim {claim.name!r} is NOT on {sheet_name}. "
                f"Either the sheet lost it or the class is stale; a class "
                f"nothing matches passes forever without checking anything.")
        elif not on_wire:
            mark = "WIRE"
            problems.append(
                f"{claim.name!r} is on {sheet_name} and NOT on the wire. "
                f"{claim.why}")
        rows.append(f"  [{mark}] sheet={on_sheet!s:<5} wire={on_wire!s:<5} "
                    f"{claim.name}")
    undeclared = []
    for shape_name, pattern in PROTOCOL_SHAPES:
        for m in pattern.finditer(body):
            snippet = " ".join(m.group(0).split())
            if not any(c.covers.search(snippet) for c in CLAIMS):
                undeclared.append((shape_name, snippet[:90]))
    for shape_name, text in undeclared:
        problems.append(
            f"UNDECLARED protocol claim on {sheet_name}: {shape_name} -- "
            f"{text!r}. Every protocol-shaped claim on a sheet must belong "
            f"to a declared class, or adding one to a sheet would never "
            f"fail this sweep until the wire carried it too.")
    rows.append(f"  [{'ok  ' if not undeclared else 'DECL'}] "
                f"{len(undeclared)} undeclared protocol-shaped claim(s)")
    return problems, rows


def selftest() -> int:
    """THE FORCING PROPERTY, PLANTED IN BOTH DIRECTIONS.

    A gate never shown able to fire is not a gate (CLAUDE.md rule 3), and that
    is doubly true of a gate whose whole justification is that it will catch a
    thing nobody has caught on purpose yet.
    """
    sheet_name, act_key, module = PAIRS[0]
    body = (HERE / sheet_name).read_text(encoding="utf-8")
    body = body[body.find(r"\begin{document}"):]
    blob = "\n".join(wire_strings(act_key, module)[0])
    blind, n = [], 0

    def arm(name: str, ok: bool) -> None:
        nonlocal n
        n += 1
        if not ok:
            blind.append(name)

    # The clean pair must be quiet. Without this, a check that failed on
    # everything would score full marks on every arm below.
    arm("the real pair is clean", not compare(sheet_name, body, blob)[0])

    # 1. A CLAIM ON THE SHEET AND NOT ON THE WIRE MUST FIRE. This is the exact
    #    defect found twice by accident: the sheet fixed, the screen not.
    for claim in CLAIMS:
        stripped = claim.wire.sub("", blob)
        arm(f"sheet-only claim fires: {claim.name}",
            any("NOT on the wire" in p
                for p in compare(sheet_name, body, stripped)[0]))

    # 2. A NEW PROTOCOL-SHAPED CLAIM ON THE SHEET, UNDECLARED, MUST FIRE. This
    #    is what makes adding a promise to a sheet fail until the wire has it.
    for planted in (
            "The grid convergence study for this rung is finished and the "
            "band is attached to your certificate.",
            "\\rolesig{Lead Aerodynamicist.} A voice nobody declared.",
            "The certificate is issued for this run and sealed.",
    ):
        arm(f"undeclared sheet claim fires: {planted[:44]}",
            any("UNDECLARED protocol claim" in p
                for p in compare(sheet_name, body + "\n" + planted, blob)[0]))

    # 3. A DECLARED CLASS DELETED FROM THE SHEET MUST FIRE, so a class cannot
    #    pass forever by matching nothing.
    for claim in CLAIMS:
        gutted = claim.sheet.sub("", body)
        arm(f"vacuous class fires: {claim.name}",
            any("is NOT on" in p
                for p in compare(sheet_name, gutted, blob)[0]))

    # ---- the DECLARATION half, planted the same way ------------------------
    # A STUB ACT, not the real one. Mutating the live act to test the sweep
    # would leave the tree in a state where the next reader cannot tell a plant
    # from a defect, and this file has already watched a torn read produce a
    # convincing phantom.
    _strings, _err, events, act = wire_strings(act_key, module)

    class _Stub:
        """Whatever the real act says, with one declaration bent."""

        def __init__(self, series=None, discussions=None,
                     table=True, closing=True):
            self._series = series
            self._disc = discussions
            self._table = table
            self._closing = closing

        def solve_replay(self):
            real = act.solve_replay()
            if self._series is None:
                return real
            class _R:
                series = self._series
            return _R()

        def sequencer(self):
            return act.sequencer()

        def discussions(self):
            return act.discussions() if self._disc is None else self._disc

        def assumption(self):
            return act.assumption() if self._table else type(
                "A", (), {"assumptions_table": None})()

        def closing(self):
            return act.closing() if self._closing else None

    class _Spec:
        def __init__(self, label):
            self.label = label

    arm("the real declarations are clean",
        not declaration_parity(act, events)[0])
    arm("a declared series the wire does not publish fires",
        any("never reaches the wire" in p for p in declaration_parity(
            _Stub(series=list(act.solve_replay().series)
                  + [_Spec("Phantom series nobody publishes")]),
            events)[0]))
    arm("a declared discussion stage the wire does not carry fires",
        any("no payload on the wire carries that stage" in p
            for p in declaration_parity(
                _Stub(discussions={"a stage that does not exist": []}),
                events)[0]))
    arm("a declared closing with no report.ready fires",
        any("no report.ready is published" in p for p in declaration_parity(
            act, [e for e in events if e.get("event") != "report.ready"])[0]))
    # THE EXEMPTION CANNOT BE A LOOPHOLE: a series exempted onto another event
    # must still find that event on the wire.
    arm("an exemption whose carrier event is absent fires",
        any("NOT on the wire either" in p for p in declaration_parity(
            act, [e for e in events if e.get("event") != "solve.adjoint"])[0]))

    print(f"FORCING CONTROL: {n - len(blind)}/{n} arms behaved")
    if blind:
        for b in blind:
            print(f"  REFUSE: {b}")
        return 2
    print("ok  the sweep fires when a sheet claim is missing from the wire, "
          "when a sheet grows an undeclared claim, and when a declared class "
          "vanishes from the sheet")
    return 0



# ===========================================================================
# DECLARATION -> WIRE
#
# THE SHEET->WIRE HALF ABOVE COULD NOT HAVE CAUGHT THE LAST THREE INSTANCES,
# and that is why this section exists. Those were DECLARATION failures, not
# document failures: an act declared something IN CODE and the wire never
# carried it.
#
#   * `sequencer()` -- the subclass existed and was named only inside the
#     module's own `drive()`, so every other driver built the base class.
#   * three expert voices -- on the sheet for weeks, one voice on the wire.
#   * six `SeriesSpec` entries with distinct labels -- one unlabelled frame.
#
# cfd found three more of the same class independently, in their own acts, on
# the same day. SIX INSTANCES, TWO TEAMS, NEITHER TOLD THE OTHER: this is
# structural to the act/sequencer architecture, where an act DECLARES its
# shape and a separate sequencer decides what to PUBLISH, and nothing joins
# the two.
#
# THE FORCING PROPERTY IS THE SAME AND IT IS STRONGER HERE, because the
# declarations are ENUMERABLE FROM THE ACT OBJECT AT RUNTIME rather than
# guessed from prose: declaring a seventh series makes this fail until the
# solving stage publishes it.
# ===========================================================================

#: A declared series may legitimately render on an event of its own rather than
#: as a labelled `solve.frame`. THAT IS AN EXPLICIT, REASONED EXCEPTION AND NOT
#: A LOOSENED THRESHOLD: the named event must ACTUALLY BE PUBLISHED, so the
#: exception cannot be used to wave a declaration through. Loosening the match
#: to "the label appears anywhere in the payloads" would have passed all six
#: labels, including one that is only a dict key -- a declaration echoed back in
#: a manifest is not a series rendering.
CARRIED_BY = {
    "Adjoint linear solve": (
        "solve.adjoint",
        "the adjoint linear solves are RAGGED -- one to four points each -- so "
        "they ship on their own event rather than padded onto the major-frame "
        "cadence; the event carries 100 of them"),
}


def declaration_parity(act, events: list[dict]) -> tuple[list[str], list[str]]:
    """Everything this act DECLARES in code, against what the wire publishes."""
    problems: list[str] = []
    rows: list[str] = []
    payload_blob = json.dumps(events, default=str)
    labels = {(e.get("payload") or {}).get("label")
              for e in events if isinstance(e.get("payload"), dict)}
    labels.discard(None)
    event_names = {e.get("event") for e in events}

    # -- every declared monitor series -------------------------------------
    for spec in act.solve_replay().series:
        if spec.label in labels:
            rows.append(f"  [ok  ] series published: {spec.label}")
            continue
        carrier = CARRIED_BY.get(spec.label)
        if carrier and carrier[0] in event_names:
            rows.append(f"  [ok  ] series on {carrier[0]}: {spec.label}")
            continue
        if carrier:
            problems.append(
                f"declared series {spec.label!r} is exempted onto "
                f"{carrier[0]!r}, and that event is NOT on the wire either")
            rows.append(f"  [GONE] series exempt but absent: {spec.label}")
            continue
        problems.append(
            f"declared series {spec.label!r} never reaches the wire as a "
            f"labelled series. The act DECLARES it in `solve_replay()`; a "
            f"declaration the wire does not carry is the class that has now "
            f"bitten six times across two teams.")
        rows.append(f"  [WIRE] series declared, not published: {spec.label}")

    # -- the sequencer declaration ------------------------------------------
    declared_seq = act.sequencer()
    rows.append(f"  [ok  ] sequencer declared: "
                f"{declared_seq.__name__ if declared_seq else 'shared'}")

    # -- every discussion stage the act declares ----------------------------
    stages_seen = {(e.get("payload") or {}).get("stage")
                   for e in events if isinstance(e.get("payload"), dict)}
    for stage in act.discussions():
        if stage not in stages_seen:
            problems.append(
                f"the act declares a discussion at stage {stage!r} and no "
                f"payload on the wire carries that stage")
            rows.append(f"  [WIRE] discussion stage missing: {stage}")
        else:
            rows.append(f"  [ok  ] discussion stage on wire: {stage}")

    # -- the assumptions table ----------------------------------------------
    table = getattr(act.assumption(), "assumptions_table", None)
    if table is not None:
        ok = table.table_id in payload_blob
        rows.append(f"  [{'ok  ' if ok else 'WIRE'}] assumptions table: "
                    f"{table.table_id}")
        if not ok:
            problems.append(
                f"the act declares an assumptions table {table.table_id!r} "
                f"that never reaches the wire")

    # -- the closing ---------------------------------------------------------
    if act.closing() is not None:
        ok = "report.ready" in event_names
        rows.append(f"  [{'ok  ' if ok else 'WIRE'}] closing -> report.ready")
        if not ok:
            problems.append(
                "the act declares a `closing()` and no report.ready is "
                "published, so the Report tab stays empty")
    return problems, rows


def main() -> int:
    problems: list[str] = []
    print(f"CLAIM CLASSES DECLARED: {len(CLAIMS)}")

    for sheet_name, act_key, module in PAIRS:
        sheet = (HERE / sheet_name).read_text(encoding="utf-8")
        body = sheet[sheet.find(r"\begin{document}"):]
        strings, err, events, act = wire_strings(act_key, module)
        blob = "\n".join(strings)
        print(f"\n{sheet_name}  <->  {act_key}")
        print(f"  wire: {len(strings)} rendered strings"
              + (f"   REFUSED: {err}" if err else ""))
        if err:
            problems.append(f"{act_key}: the act refused, so nothing about it "
                            f"can be compared: {err}")
            continue

        pair_problems, rows = compare(sheet_name, body, blob)
        for row in rows:
            print(row)
        problems.extend(pair_problems)

        decl_problems, decl_rows = declaration_parity(act, events)
        print("  -- declaration -> wire --")
        for row in decl_rows:
            print(row)
        problems.extend(decl_problems)

    print(f"\nSHEETS WITH NO ACT TO COMPARE AGAINST: {len(SHEETS_WITHOUT_ACTS)}")
    for name in SHEETS_WITHOUT_ACTS:
        print(f"  {name}")
    print("  Reported, not skipped: these sheets can drift from a screen that "
          "does not exist yet, and this sweep cannot see it.")

    if problems:
        print(f"\nREFUSE: {len(problems)} parity problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nok  every declared claim is on both surfaces, and no sheet "
          "carries a protocol claim the wire has not been told about")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
