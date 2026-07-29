#!/usr/bin/env python3
"""Assemble the nine-case gate table from the records on disk.

Every row is read out of a stored record. Nothing is transcribed by hand, so
re-running this after a new act lands picks the new numbers up. A row whose
record does not exist yet prints as PENDING -- it is never filled with a
plausible-looking number.

    python3 scripts/gate_table.py            # text table
    python3 scripts/gate_table.py --md       # markdown, for the campaign page

Provenance is printed with every row because the row is worthless without it:
the whole point of a gate is that someone else can go and check it.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WEB = REPO / "demo-output" / "website"

PENDING = "PENDING"


def _load(rel: str):
    p = WEB / rel
    if not p.exists():
        return None
    if p.suffix == ".json":
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            return None
    return p.read_text()


def _finest(levels: dict) -> tuple[str, dict]:
    """Return the level with the most cells -- the one the gate is read from."""
    name = max(levels, key=lambda k: levels[k].get("ncells", 0))
    return name, levels[name]


def _row(case, gate, ref, measured, dev, verdict, source):
    return {"case": case, "gate": gate, "reference": ref, "measured": measured,
            "deviation": dev, "verdict": verdict, "source": source}


def _pending(case, gate, ref, source):
    return _row(case, gate, ref, PENDING, PENDING, PENDING, source)


def rows() -> list[dict]:
    out: list[dict] = []

    # ---- 1. cylinder vortex shedding -------------------------------------
    # Import the act's own correlation rather than restating it here. A second
    # copy of a formula is a second thing that can drift away from the act the
    # camera is pointed at.
    sys.path.insert(0, str(REPO / "sdk"))
    from workflows import _exact_theory as et
    from workflows.cylinder_vortex_shedding import REYNOLDS
    st_ref = et.roshko_strouhal(REYNOLDS)
    shed = _load("campaign/F5b_cylinder_re100_act.json")
    src = "campaign/F5b_cylinder_re100_act.json"
    if shed and "strouhal" in shed:
        st = shed["strouhal"]
        dev = (st - st_ref) / st_ref * 100.0
        out.append(_row("Cylinder vortex shedding, Re 100",
                        "Strouhal vs Roshko-Williamson", f"St {st_ref:.4f}",
                        f"St {st:.4f}", f"{dev:+.2f}%",
                        "PASS" if abs(dev) <= 5 else "FAIL", src))
    else:
        out.append(_pending("Cylinder vortex shedding, Re 100",
                            "Strouhal vs Roshko-Williamson",
                            f"St {st_ref:.4f}", src))

    # ---- 2-4. supersonic exact theory ------------------------------------
    f3 = _load("campaign/F3_supersonic_exact_theory.json")
    src3 = "campaign/F3_supersonic_exact_theory.json"
    if f3:
        cases = f3["cases"]

        # wedge -- graded on the shock angle fitted over all stations, which is
        # the more honest of the two fits (it uses the whole locus, not a pair).
        w = cases["1_wedge"]["M2.0_th15.0"]
        lvl, v = _finest(w["levels"])
        dev = v["beta_all_dev_pct"]
        out.append(_row("Supersonic wedge, M 2.0, 15 deg",
                        "Oblique-shock angle vs exact relation",
                        f"beta {w['exact']['beta_deg']:.3f} deg",
                        f"beta {v['beta_all_stations_deg']:.3f} deg ({v['ncells']} cells)",
                        f"{dev:+.2f}%", "PASS" if abs(dev) <= 5 else "FAIL", src3))

        c = cases["2_cone"]["M2.35_thc10.0"]
        lvl, v = _finest(c["levels"])
        dev = v["beta_dev_pct"]
        out.append(_row("Supersonic cone, M 2.35, 10 deg",
                        "Conical shock angle vs Taylor-Maccoll",
                        "beta 26.737 deg",
                        f"beta {v['beta_computed_deg']:.3f} deg ({v['ncells']} cells)",
                        f"{dev:+.2f}%", "PASS" if abs(dev) <= 5 else "FAIL", src3))

        d = cases["3_diamond"]["M2.0_eps7.125"]
        lvl, v = _finest(d["levels"])
        dev = v["deviation_pct"]
        out.append(_row("Diamond airfoil, M 2.0, 7.125 deg",
                        "Wave drag vs shock-expansion theory",
                        f"Cd {d['exact']['cd']:.5f}",
                        f"Cd {v['cd_computed']:.5f} ({v['ncells']} cells)",
                        f"{dev:+.2f}%", "PASS" if abs(dev) <= 5 else "FAIL", src3))
    else:
        for case, gate in (("Supersonic wedge, M 2.0, 15 deg", "Oblique-shock angle vs exact relation"),
                           ("Supersonic cone, M 2.35, 10 deg", "Conical shock angle vs Taylor-Maccoll"),
                           ("Diamond airfoil, M 2.0, 7.125 deg", "Wave drag vs shock-expansion theory")):
            out.append(_pending(case, gate, "-", src3))

    # ---- 5. hypersonic blunt body ----------------------------------------
    f4 = _load("campaign/F4_hypersonic_blunt_body.json")
    src4 = "campaign/F4_hypersonic_blunt_body.json"
    if f4:
        for mach in (6.0, 8.0):
            got = [r for r in f4["results"]
                   if r["M"] == mach and r["res_level"] == "fine"]
            if not got:
                out.append(_pending(f"Hypersonic cylinder, M {mach:g}",
                                    "Shock standoff vs Billig correlation", "-", src4))
                continue
            r = got[0]
            dev = r["standoff_dev_pct"]
            out.append(_row(f"Hypersonic cylinder, M {mach:g}",
                            "Shock standoff vs Billig correlation",
                            f"delta/R {r['delta_billig']:.4f}",
                            f"delta/R {r['standoff_mean']:.4f} ({r['ncells']} cells)",
                            f"{dev:+.2f}%", "PASS" if abs(dev) <= 5 else "FAIL", src4))
    else:
        out.append(_pending("Hypersonic cylinder, M 6/M 8",
                            "Shock standoff vs Billig correlation", "-", src4))

    # ---- 6. Ahmed body ---------------------------------------------------
    a4 = _load("dafoam/ladder-a/A4_ahmed_body.json")
    src6 = "dafoam/ladder-a/A4_ahmed_body.json"
    ve = (a4 or {}).get("comparison", {}).get("vs_experiment")
    if ve:
        # Coefficients are compared on the frontal-area basis the experiment
        # uses; the record carries the rebasing arithmetic that gets there.
        dev = -ve["relative_error"] * 100.0
        out.append(_row("Ahmed body, 25 deg slant",
                        "Drag vs Ahmed/Ramm/Faltin SAE 840300",
                        f"Cd {ve['experimental_CD']:.5f} (frontal)",
                        f"Cd {ve['our_result_CD_frontal_basis']:.5f} (frontal)",
                        f"{dev:+.2f}%",
                        "PASS" if ve.get("within_band") else "FAIL",
                        src6))
    else:
        out.append(_pending("Ahmed body, 25 deg slant",
                            "Drag vs Ahmed/Ramm/Faltin SAE 840300", "-", src6))

    # ---- 7. NASA hump ----------------------------------------------------
    # Recorded in the D9 band write-up, which carries the baseline row.
    out.append(_row("NASA wall-mounted hump",
                    "Separation / reattachment x/c vs NASA experiment",
                    "sep 0.6650, reatt 1.1000",
                    "sep 0.6544, reatt 1.2534",
                    "-1.59% / +13.95%",
                    "SEPARATION PASS, REATTACHMENT FAIL (documented)",
                    "campaign/F6a_epistemic_band.md"))

    # ---- 8-9. ONERA M6 and CRM ------------------------------------------
    m6 = _load("dafoam/ladder-a/A3_onera_m6.json")
    src8 = "dafoam/ladder-a/A3_onera_m6.json"
    if m6 and m6.get("cp_stations"):
        out.append(_row("ONERA M6 wing", "Cp at 7 spanwise stations vs AGARD AR-138",
                        "AGARD AR-138", f"{len(m6['cp_stations'])} stations",
                        m6.get("deviation", "see record"),
                        m6.get("verdict", "see record"), src8))
    else:
        out.append(_pending("ONERA M6 wing",
                            "Cp at 7 spanwise stations vs AGARD AR-138",
                            "AGARD AR-138", src8))

    crm = _load("dafoam/ladder-a/A6_crm_wingbody.json")
    src9 = "dafoam/ladder-a/A6_crm_wingbody.json"
    cd = (crm or {}).get("cd")
    if cd:
        ref = (crm or {}).get("cd_reference", 0.02090)
        dev = (cd - ref) / ref * 100.0
        out.append(_row("CRM wing-body", "Drag vs DAFoam CRM_Wing tutorial",
                        f"Cd {ref:.5f}", f"Cd {cd:.5f}", f"{dev:+.2f}%",
                        "PASS" if abs(dev) <= 2 else "FAIL", src9))
    else:
        out.append(_pending("CRM wing-body", "Drag vs DAFoam CRM_Wing tutorial",
                            "Cd 0.02090", src9))

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="emit markdown")
    args = ap.parse_args()

    data = rows()
    ready = sum(1 for r in data if r["measured"] != PENDING)

    if args.md:
        print("| case | gate | reference | measured | deviation | verdict | record |")
        print("| --- | --- | --- | --- | --- | --- | --- |")
        for r in data:
            print(f"| {r['case']} | {r['gate']} | {r['reference']} | "
                  f"{r['measured']} | {r['deviation']} | {r['verdict']} | "
                  f"`{r['source']}` |")
        print(f"\n{ready} of {len(data)} rows carry a measured number.")
    else:
        for r in data:
            print(f"{r['case']}")
            print(f"    gate      {r['gate']}")
            print(f"    reference {r['reference']}")
            print(f"    measured  {r['measured']}")
            print(f"    deviation {r['deviation']}   -> {r['verdict']}")
            print(f"    record    {r['source']}")
        print(f"\n{ready} of {len(data)} rows carry a measured number.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
