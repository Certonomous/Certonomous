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
    """``[Gate: ...] Quantity Q | Value V`` -- key/value gate reporting."""
    out: dict[str, str] = {}
    pat = re.compile(r"\[Gate:[^\]]*\]\s*Quantity\s*(?P<q>[^|]+?)\s*\|\s*"
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


def _row(case, gate, ref, measured, dev, verdict, source):
    return {"case": case, "gate": gate, "reference": ref, "measured": measured,
            "deviation": dev, "verdict": verdict, "source": source}


def _pending(case, gate, source):
    return _row(case, gate, PENDING, PENDING, PENDING, PENDING, source)


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
            out.append(_pending(label, gate, f"mission-output/{act}/"))
            continue
        text = t.read_text(errors="replace")
        got = [r for r in _verdict_rows(text) if r["q"] == quantity]
        src = f"mission-output/{act}/{t.name}"
        if not got:
            out.append(_pending(label, gate, src))
            continue
        r = got[0]
        out.append(_row(label, gate, r["ref"], r["got"], r["dev"],
                        _tolerance_verdict(r["dev"]), src))

    # ---- Ahmed body: key/value gate, act states its own tier --------------
    t = _transcript("ahmed-body")
    if t:
        text = t.read_text(errors="replace")
        g = _gate_values(text)
        src = f"mission-output/ahmed-body/{t.name}"
        ref = next((v for k, v in g.items() if k.startswith("Published")), None)
        got = g.get("Rebased C_d (frontal basis)")
        if ref and got:
            out.append(_row("Ahmed body, 25 deg slant",
                            "Drag vs Ahmed/Ramm/Faltin SAE 840300 (frontal basis)",
                            f"Cd {ref}", f"Cd {got}",
                            g.get("Deviation", "-"),
                            _verdict_line(text) or "see record", src))
        else:
            out.append(_pending("Ahmed body, 25 deg slant",
                                "Drag vs Ahmed/Ramm/Faltin SAE 840300", src))
    else:
        out.append(_pending("Ahmed body, 25 deg slant",
                            "Drag vs Ahmed/Ramm/Faltin SAE 840300",
                            "mission-output/ahmed-body/"))

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
            _verdict_line(text) or "see record", src))
    else:
        out.append(_pending("NASA wall-mounted hump",
                            "Separation / reattachment x/c vs NASA experiment",
                            "mission-output/nasa-hump/"))

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
            out.append(_pending(label, gate, f"mission-output/{act}/"))
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
                            src))
            continue
        # An act can run, fail honestly, and produce no graded row -- an
        # unconverged primal never reaches the quantity its gate compares.
        # That is NOT the same as an act that has not run, and a table that
        # prints PENDING for both is lying by omission about which is which.
        tier = _verdict_line(text)
        if tier:
            out.append(_row(label, gate, "-", "not evaluated",
                            "-", tier, src))
        else:
            out.append(_pending(label, gate, src))

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="emit markdown")
    args = ap.parse_args()

    data = rows()
    ready = sum(1 for r in data if r["measured"] != PENDING)
    graded = sum(1 for r in data if r["deviation"] not in (PENDING, "-"))

    if args.md:
        print("| act | gate | reference | measured | deviation | verdict | artifact |")
        print("| --- | --- | --- | --- | --- | --- | --- |")
        for r in data:
            print(f"| {r['case']} | {r['gate']} | {r['reference']} | "
                  f"{r['measured']} | {r['deviation']} | {r['verdict']} | "
                  f"`{r['source']}` |")
    else:
        for r in data:
            print(f"{r['case']}")
            print(f"    gate      {r['gate']}")
            print(f"    reference {r['reference']}")
            print(f"    measured  {r['measured']}")
            print(f"    deviation {r['deviation']}   -> {r['verdict']}")
            print(f"    artifact  {r['source']}")
    print(f"\n{ready} of {len(data)} acts have run; {graded} carry a graded number.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
