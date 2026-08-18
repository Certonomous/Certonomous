#!/usr/bin/env python3
"""Assemble the nine-act gate table from the artifacts the acts produce.

WHERE THE NUMBERS COME FROM, AND WHY IT MATTERS.

Each act writes a transcript under ``mission-output/<act>/`` when it runs, and
that transcript is what the camera records. The campaign records under
``demo-output/website/campaign/`` are a *different* set of runs. Mostly they
agree -- but not always: the wedge act's mesh ladder lands on 44.693 deg where
the campaign record's finest rung has 44.847 deg, because they are not the same
case. Citing the campaign record for a row the viewer watched the act produce
would make the provenance decorative.

So the act transcript is the source of truth here, and the record column names
the transcript. A row whose act has not run prints PENDING; it is never filled
in from a neighbouring run that happens to be close.

    python3 scripts/gate_table.py            # text
    python3 scripts/gate_table.py --md       # markdown
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "mission-output"

PENDING = "PENDING"


# --------------------------------------------------------------------------
# Transcript parsing. Acts emit their verdicts as pipe-delimited table rows;
# three shapes are in use and all three are parsed rather than normalised,
# because rewriting an act's output to suit this script would be the tail
# wagging the dog.
# --------------------------------------------------------------------------

def _transcript(act: str) -> Path | None:
    d = OUT / act
    for name in ("transcript.md", "transcript.txt"):
        p = d / name
        if p.exists():
            return p
    return None


def _verdict_rows(text: str) -> list[dict]:
    """``[... verdict] Quantity Q | Exact E | Solved S | Deviation D``

    ``Correlation`` appears in place of ``Exact`` where the reference is a
    fitted correlation rather than a closed form."""
    rows = []
    pat = re.compile(
        r"\[[^\]]*verdict\]\s*Quantity\s*(?P<q>[^|]+?)\s*\|\s*"
        r"(?:Exact|Correlation)\s*(?P<ref>[^|]+?)\s*\|\s*"
        r"Solved\s*(?P<got>[^|]+?)\s*\|\s*Deviation\s*(?P<dev>.+)")
    for line in text.splitlines():
        m = pat.search(line)
        if m:
            rows.append({k: v.strip() for k, v in m.groupdict().items()})
    return rows


def _gate_values(text: str) -> dict[str, str]:
    """``[<table title>] Quantity Q | Value V`` -- key/value table reporting.

    This used to require the title to begin ``Gate:``. When an act retitled
    its table (the Ahmed body's became "Measured drag against the published
    wind tunnel", and moved to the researcher), every row stopped parsing and
    the row silently became PENDING -- on a case that had passed, in a table
    the shoot guide calls safe to show on camera. The footer count fell from
    9 to 8 and nothing said why.

    So the shape being parsed is the table, not the title: any bracketed
    label followed by the Quantity/Value pair. A title is prose and will be
    rewritten again; the row shape is a contract. Keys stay per-act, so two
    tables sharing a quantity name in one transcript would still collide --
    that has not happened and is worth knowing if it ever does.
    """
    out: dict[str, str] = {}
    pat = re.compile(r"\[[^\]]*\]\s*Quantity\s*(?P<q>[^|]+?)\s*\|\s*"
                     r"Value\s*(?P<v>.+)")
    for line in text.splitlines():
        m = pat.search(line)
        if m:
            out[m.group("q").strip()] = m.group("v").strip()
    return out


def _verdict_line(text: str) -> str:
    """The act's own one-word tier, e.g. 'Verdict: solver-backed.'"""
    m = re.search(r"Verdict:\s*([a-z -]+)", text, re.I)
    return m.group(1).strip(" .").upper() if m else ""


# --------------------------------------------------------------------------
# The referent, its class, and the band. Added 2026-08-18.
#
# VERIFICATION_CHARTER.md §6a: "A verdict label (VALIDATED, PASS, verified,
# confirmed, reproduces) carries the thing it was checked against, on every
# surface it appears on. Where there is no external referent, the label says
# so." This table is the surface the charter's own §6a examples were drawn
# from, and until today it was the surface that did not carry it: three rows
# printed a verdict chip beside a reference VALUE with no statement of what
# CLASS of thing that value is, and every band any act declared for itself
# stayed in the act's transcript.
#
# The class is a judgement and is stated here with the file that settles it.
# The band is NOT stated here -- it is parsed back out of the act's own
# transcript below, because a band this script asserted would be this
# script's band and not the act's, which is the defect one level up.
# --------------------------------------------------------------------------

REFERENT_CLASS = {
    "cylinder-vortex-shedding": (
        "PUBLISHED CORRELATION, AND NOT THE ONE THE ACT CITES",
        "St = 0.198(1-19.7/Re) (sdk/workflows/_exact_theory.py:260). Roshko "
        "1954, NACA TR-1191 p. 11 eq (2a) gives St = 0.212(1-21.2/Re) for "
        "50<R<150, which is the range Re 100 sits in; neither 0.198 nor 19.7 "
        "occurs anywhere in that report (docs/papers/roshko_1954_naca_tr_1191.txt)"),
    "supersonic-wedge": (
        "EXACT THEORY",
        "theta-beta-M relation, own solver checked against NASA GRC oblshk.f"),
    "supersonic-cone": (
        "EXACT THEORY",
        "Taylor-Maccoll, own shooting solver"),
    "diamond-airfoil": (
        "EXACT THEORY",
        "shock-expansion theory, cross-checked against Ackeret"),
    "hypersonic-cylinder": (
        "PUBLISHED CORRELATION",
        "Billig 1967 via Anderson, Hypersonic and High-Temperature Gas "
        "Dynamics, Eq. 5.37"),
    "ahmed-body": (
        "PUBLISHED EXPERIMENT, EXTRACTION ROUTE NOT RECORDED",
        "Ahmed, Ramm and Faltin 1984, SAE 840300. No record states which "
        "table, figure or page Cd 0.285 came from "
        "(models/curriculum/ahmed_25/reference.yaml, one commit 5336dd57)"),
    "nasa-hump": (
        "PUBLISHED EXPERIMENT",
        "NASA Turbulence Modeling Resource, 2D wall-mounted hump validation "
        "case; noflow_cp.exp.dat / noflow_cf.exp.dat fetched and retained"),
    "onera-m6": (
        "SELF-REFERENTIAL, AND IT SAYS SO",
        "the primal's own residual tolerance. The external gate, Cp at 7 "
        "spanwise stations vs AGARD AR-138, was NOT evaluated"),
    "crm-wingbody": (
        "ANOTHER SOLVER, CODE-TO-CODE",
        "DAFoam's own CRM_Wing tutorial documentation, same code, same "
        "downloaded mesh, same unmodified daOptions. sdk/chief_engineer/lab.py:182 "
        "and :224-225 reserve VALIDATED for a published experiment; the chip on "
        "this row is assigned at sdk/workflows/crm_wingbody.py:330 without "
        "passing through that path"),
}

# The screen this script applies when an act's transcript carries no tier line
# of its own. It was always here (``_tolerance_verdict``'s default) and was
# never printed, so five rows read PASS against a limit no reader could see.
TABLE_SCREEN = "the table's own +/-5% screen (scripts/gate_table.py:_tolerance_verdict)"

# Quantity keys, in the acts' own words, whose VALUE is the declared band.
_BAND_KEYS = ("Acceptance band", "Separation gate", "Reattachment model-form band",
              "Gate", "Primal residual gate")
_PROSE_BAND = re.compile(r"Gate:[^\n]*?within ([0-9.]+\s*%)", re.I)


def _declared_band(text: str) -> str:
    """The band the ACT declared, read back out of the act's own transcript.

    Parsed, never asserted: a band this file supplied would be this file's
    band wearing the act's name, which is the same substitution the missing
    referent column allowed in the first place.
    """
    parts = []
    g = _gate_values(text)
    for k in _BAND_KEYS:
        if k in g:
            label = "gate" if k == "Gate" else k.lower()
            parts.append(f"{label} {g[k]}")
    if not parts:
        m = _PROSE_BAND.search(text)
        if m:
            parts.append(f"gate {m.group(1).replace(' ', '')}")
    return "; ".join(parts) if parts else ""


def _referent(act: str, text: str | None) -> tuple[str, str]:
    cls, named = REFERENT_CLASS.get(act, ("NOT CLASSIFIED", ""))
    band = _declared_band(text) if text else ""
    if not band:
        band = f"none declared by the act; graded here against {TABLE_SCREEN}"
    return f"{cls}. {named}", band


def _row(case, gate, ref, measured, dev, verdict, source, act=None, text=None):
    referent, band = _referent(act, text) if act else ("", "")
    return {"case": case, "gate": gate, "reference": ref, "measured": measured,
            "deviation": dev, "verdict": verdict, "source": source,
            "referent": referent, "band": band}


def _pending(case, gate, source, act=None):
    return _row(case, gate, PENDING, PENDING, PENDING, PENDING, source, act=act)


# --------------------------------------------------------------------------
# The nine acts.
# --------------------------------------------------------------------------

# act dir, display label, gate description, the quantity to read
SIMPLE_ACTS = [
    ("cylinder-vortex-shedding", "Cylinder vortex shedding, Re 100",
     "Strouhal vs Roshko-Williamson correlation", "Strouhal number"),
    ("supersonic-wedge", "Supersonic wedge, M 2.0, 15 deg",
     "Oblique-shock angle vs theta-beta-M relation", "Shock angle (deg)"),
    ("supersonic-cone", "Supersonic cone, M 2.35, 10 deg",
     "Conical shock angle vs Taylor-Maccoll", "Shock angle (deg)"),
    ("diamond-airfoil", "Diamond airfoil, M 2.0, 7.125 deg",
     "Wave drag vs shock-expansion theory", "Wave drag coefficient"),
    ("hypersonic-cylinder", "Hypersonic cylinder, M 8",
     "Shock standoff vs Billig correlation", "Shock standoff (delta/R)"),
]


def _tolerance_verdict(dev: str, limit: float = 5.0) -> str:
    m = re.search(r"([-+]?\d+(?:\.\d+)?)", dev or "")
    if not m:
        return "see record"
    return "PASS" if abs(float(m.group(1))) <= limit else "FAIL"


def rows() -> list[dict]:
    out: list[dict] = []

    for act, label, gate, quantity in SIMPLE_ACTS:
        t = _transcript(act)
        if not t:
            out.append(_pending(label, gate, f"mission-output/{act}/", act=act))
            continue
        text = t.read_text(errors="replace")
        got = [r for r in _verdict_rows(text) if r["q"] == quantity]
        src = f"mission-output/{act}/{t.name}"
        if not got:
            out.append(_pending(label, gate, src, act=act))
            continue
        r = got[0]
        out.append(_row(label, gate, r["ref"], r["got"], r["dev"],
                        _tolerance_verdict(r["dev"]), src,
                        act=act, text=text))

    # ---- Ahmed body: key/value gate, act states its own tier --------------
    t = _transcript("ahmed-body")
    if t:
        text = t.read_text(errors="replace")
        g = _gate_values(text)
        src = f"mission-output/ahmed-body/{t.name}"
        ref = next((v for k, v in g.items() if k.startswith("Published")), None)
        # The act renamed this row when it started naming its reference area
        # explicitly: "Rebased C_d (frontal basis)" became "On the published
        # area basis". Both are read, newest first, so regenerating this table
        # against an older transcript still works.
        got = (g.get("On the published area basis")
               or g.get("Rebased C_d (frontal basis)"))
        if ref and got:
            out.append(_row("Ahmed body, 25 deg slant",
                            "Drag vs Ahmed/Ramm/Faltin SAE 840300 (frontal basis)",
                            f"Cd {ref}", f"Cd {got}",
                            g.get("Deviation", "-"),
                            _verdict_line(text) or "see record", src,
                            act="ahmed-body", text=text))
        else:
            out.append(_pending("Ahmed body, 25 deg slant",
                                "Drag vs Ahmed/Ramm/Faltin SAE 840300", src,
                                act="ahmed-body"))
    else:
        out.append(_pending("Ahmed body, 25 deg slant",
                            "Drag vs Ahmed/Ramm/Faltin SAE 840300",
                            "mission-output/ahmed-body/", act="ahmed-body"))

    # ---- NASA hump: two quantities, one passes and one does not ----------
    t = _transcript("nasa-hump")
    if t:
        text = t.read_text(errors="replace")
        g = _gate_values(text)
        src = f"mission-output/nasa-hump/{t.name}"
        sep_dev = g.get("Separation deviation", "-")
        re_dev = g.get("Reattachment deviation", "-")
        out.append(_row(
            "NASA wall-mounted hump",
            "Separation / reattachment x/c vs NASA experiment",
            f"sep {g.get('Separation x/c (NASA Turbulence Modeling Resource, wall-mounted hump experiment, experiment)', '?')}, "
            f"reatt {g.get('Reattachment x/c (NASA Turbulence Modeling Resource, wall-mounted hump experiment, experiment)', '?')}",
            f"sep {g.get('Separation x/c (converged)', g.get('Separation x/c', '?'))}, "
            f"reatt {g.get('Reattachment x/c (converged)', '?')}",
            f"{sep_dev} / {re_dev}",
            _verdict_line(text) or "see record", src,
            act="nasa-hump", text=text))
    else:
        out.append(_pending("NASA wall-mounted hump",
                            "Separation / reattachment x/c vs NASA experiment",
                            "mission-output/nasa-hump/", act="nasa-hump"))

    # ---- ONERA M6 and CRM: separate engine, may not have run yet ---------
    # ``expect`` is the quantity the act was BUILT to grade. When a run reports
    # a different quantity, the intended gate was not evaluated -- and the row
    # has to say so. Printing the intended gate's description beside a number
    # measured on something else reads as "we tested that and missed", which is
    # a different and much worse claim than "we never got far enough to test
    # it". The ONERA M6 primal fails before any field is written, so its Cp
    # gate is not missed; it is unreachable.
    for act, label, gate, expect in (
            ("onera-m6", "ONERA M6 wing",
             "Cp at 7 spanwise stations vs AGARD AR-138", "Cp"),
            ("crm-wingbody", "CRM wing-body",
             "Drag vs DAFoam CRM_Wing tutorial, Cd 0.02090 +/-2%", "Drag")):
        t = _transcript(act)
        if not t:
            out.append(_pending(label, gate, f"mission-output/{act}/", act=act))
            continue
        text = t.read_text(errors="replace")
        src = f"mission-output/{act}/{t.name}"
        vr = _verdict_rows(text)
        if vr:
            r = vr[0]
            shown = gate
            if expect.lower() not in r["q"].lower():
                shown = (f"{r['q']} vs its own tolerance "
                         f"(intended gate, {gate}, NOT evaluated)")
            out.append(_row(label, shown, r["ref"], r["got"], r["dev"],
                            _verdict_line(text) or _tolerance_verdict(r["dev"]),
                            src, act=act, text=text))
            continue
        # An act can run, fail honestly, and produce no graded row -- an
        # unconverged primal never reaches the quantity its gate compares.
        # That is NOT the same as an act that has not run, and a table that
        # prints PENDING for both is lying by omission about which is which.
        tier = _verdict_line(text)
        if tier:
            out.append(_row(label, gate, "-", "not evaluated",
                            "-", tier, src, act=act, text=text))
        else:
            out.append(_pending(label, gate, src, act=act))

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="emit markdown")
    ap.add_argument("--filmed", action="store_true",
                    help="only the acts in the filmed sequence (those that "
                         "met their gate). The withheld acts are still named "
                         "in the footer with a pointer to the full record, so "
                         "this narrows the view, never hides that it did.")
    args = ap.parse_args()

    data = rows()
    withheld: list[str] = []
    if args.filmed:
        keep = [r for r in data if r["verdict"] not in ("UNCONVERGED", PENDING)]
        withheld = [r["case"] for r in data if r not in keep]
        data = keep
    ready = sum(1 for r in data if r["measured"] != PENDING)
    graded = sum(1 for r in data if r["deviation"] not in (PENDING, "-"))

    if args.md:
        print("| act | gate | referent and its class | band, as the act declared it | "
              "reference | measured | deviation | verdict | artifact |")
        print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for r in data:
            print(f"| {r['case']} | {r['gate']} | {r['referent']} | {r['band']} | "
                  f"{r['reference']} | "
                  f"{r['measured']} | {r['deviation']} | {r['verdict']} | "
                  f"`{r['source']}` |")
    else:
        for r in data:
            print(f"{r['case']}")
            print(f"    gate      {r['gate']}")
            print(f"    referent  {r['referent']}")
            print(f"    band      {r['band']}")
            print(f"    reference {r['reference']}")
            print(f"    measured  {r['measured']}")
            print(f"    deviation {r['deviation']}   -> {r['verdict']}")
            print(f"    artifact  {r['source']}")
    print(f"\n{ready} of {len(data)} acts have run; {graded} carry a graded number.")
    print("A verdict here carries the thing it was checked against and the band "
          "it was checked to, per VERIFICATION_CHARTER.md 6a. Where the band "
          "column says none was declared, the verdict cell was decided by "
          f"{TABLE_SCREEN}, which is this script's screen and not the act's.")
    if withheld:
        # Naming them is the point. A filtered table that concealed its own
        # filtering would be the kind of quiet edit this project exists to
        # not make -- and a reviewer who spots it later trusts nothing else.
        print(f"Not shown here ({len(withheld)}): {', '.join(withheld)}. "
              f"Graded in full via the same command without --filmed, and "
              f"recorded in demo-output/website/campaign/NOT_PASSING_REGISTER.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
