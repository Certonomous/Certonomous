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
#: coverage, not an absence of a problem.
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
          # COVERS THE CLAIM, NOT THE TOPIC. `covers=r"convergence stud"` was
          # the first attempt and the forcing plant caught it: it absorbed a
          # planted claim that the study was FINISHED AND ATTACHED, which is a
          # DIFFERENT claim from "underway" and is exactly the sort of new
          # promise this arm must refuse. A `covers` broad enough to match the
          # subject swallows every future claim about that subject.
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


def wire_strings(act_key: str, module: str) -> tuple[list[str], str | None]:
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
    return out, err


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

    print(f"FORCING CONTROL: {n - len(blind)}/{n} arms behaved")
    if blind:
        for b in blind:
            print(f"  REFUSE: {b}")
        return 2
    print("ok  the sweep fires when a sheet claim is missing from the wire, "
          "when a sheet grows an undeclared claim, and when a declared class "
          "vanishes from the sheet")
    return 0


def main() -> int:
    problems: list[str] = []
    print(f"CLAIM CLASSES DECLARED: {len(CLAIMS)}")

    for sheet_name, act_key, module in PAIRS:
        sheet = (HERE / sheet_name).read_text(encoding="utf-8")
        body = sheet[sheet.find(r"\begin{document}"):]
        strings, err = wire_strings(act_key, module)
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
