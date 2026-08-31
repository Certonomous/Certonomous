#!/usr/bin/env python3
"""Read the SO-3a alpha feasibility solves and state the physics answer.

UNREGISTERED FEASIBILITY RUNG. Nothing here is a verdict and no value produced
by this reader may be graded as one (Sanaa 2026-08-31; queue_entry_check.py's
UNREGISTERED_PREREG_TAGS).

The question: do alpha = 3.139, 5.139, 7.139 degrees solve on A1's 4,032-cell
NACA0012 mesh, and is the top angle still attached?

ATTACHMENT INDICATOR, stated before the numbers exist so it cannot be chosen to
fit them: for attached flow on a thin symmetric section, CL is very nearly
LINEAR in alpha. This reader reports the two secant slopes dCL/dalpha across
the bracket, and their ratio. A ratio near 1 means the bracket is in the linear
(attached) range; a ratio materially below 1 means lift is going nonlinear at
the top of the bracket, which is the separation-onset signature. This is an
INDICATOR, not a separation measurement -- a real attachment claim needs wall
shear, and this rung does not buy it. Said plainly rather than overclaimed.

The reader PLANTS A CONTROL: it is shown able to report a non-null CL before any
"no CL found" line is trusted (standing rule 3 -- a zero from a reader not shown
able to see a non-zero is not evidence).
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

# DAFoam prints its evaluated functions; accept the common spellings rather than
# pinning one format we have never seen on this case.
PATTERNS = {
    "CL": [re.compile(r"\bCL\b\s*[:=]\s*([-+0-9.eE]+)"),
           re.compile(r"aero_post\.CL\s*[:=]?\s*\[?\s*([-+0-9.eE]+)")],
    "CD": [re.compile(r"\bCD\b\s*[:=]\s*([-+0-9.eE]+)"),
           re.compile(r"aero_post\.CD\s*[:=]?\s*\[?\s*([-+0-9.eE]+)")],
}
RES = re.compile(r"Initial residual\s*=\s*([-+0-9.eE]+)")
CONVERGED = "Primal solution converged"


def last_match(text: str, pats: list[re.Pattern]) -> float | None:
    val = None
    for p in pats:
        for m in p.finditer(text):
            try:
                val = float(m.group(1))
            except ValueError:
                continue
    return val


def read_alpha(log: Path) -> dict:
    text = log.read_text(errors="replace")
    resids = [float(m.group(1)) for m in RES.finditer(text)]
    return {
        "log": str(log),
        "CL": last_match(text, PATTERNS["CL"]),
        "CD": last_match(text, PATTERNS["CD"]),
        "converged_line": CONVERGED in text,
        "n_residual_lines": len(resids),
        "final_residual": resids[-1] if resids else None,
        "max_residual": max(resids) if resids else None,
    }


def plant_control() -> bool:
    """Prove the reader can see a non-null CL before any null is believed."""
    probe = "some preamble\n CL = 0.4987654\n CD: 0.0123456\n Primal solution converged\n"
    cl = last_match(probe, PATTERNS["CL"])
    cd = last_match(probe, PATTERNS["CD"])
    ok = cl is not None and abs(cl - 0.4987654) < 1e-9 and cd is not None
    print(f"PLANTED CONTROL: reader sees CL={cl} CD={cd} from a synthetic log -> "
          f"{'FIRES' if ok else 'DOES NOT FIRE'}")
    return ok


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: so3af_read.py <run root>")
        return 64
    root = Path(sys.argv[1])

    if not plant_control():
        print("REFUSING: the reader cannot see a planted non-null CL, so a null "
              "reading from the real logs would not be evidence (standing rule 3).")
        return 2

    out = root / "out"
    if not out.is_dir():
        print(f"REFUSING: no out/ directory under {root}")
        return 2

    logs = sorted(out.glob("primal_alpha_*.log"))
    print(f"\nlogs found: {len(logs)}")
    if not logs:
        print("NO LOGS -- nothing executed. This is not a physics answer.")
        return 2

    rows = []
    for lg in logs:
        a = lg.name.replace("primal_alpha_", "").replace(".log", "")
        try:
            alpha = float(a)
        except ValueError:
            continue
        r = read_alpha(lg)
        r["alpha_deg"] = alpha
        rows.append(r)
    rows.sort(key=lambda r: r["alpha_deg"])

    print(f"\n{'alpha_deg':>18} {'CL':>12} {'CD':>12} {'converged':>10} "
          f"{'final_resid':>13} {'n_res':>6}")
    for r in rows:
        print(f"{r['alpha_deg']:>18.11f} "
              f"{('%.6f' % r['CL']) if r['CL'] is not None else 'None':>12} "
              f"{('%.6f' % r['CD']) if r['CD'] is not None else 'None':>12} "
              f"{str(r['converged_line']):>10} "
              f"{('%.3e' % r['final_residual']) if r['final_residual'] is not None else 'None':>13} "
              f"{r['n_residual_lines']:>6}")

    print("\n--- FEASIBILITY READINGS (not verdicts) ---")
    print(f"declared alphas: 3   solved logs present: {len(rows)}   "
          f"converged: {sum(1 for r in rows if r['converged_line'])}")

    cds = [r["CD"] for r in rows]
    if all(c is not None for c in cds) and len(cds) == 3:
        mono = cds[0] < cds[1] < cds[2]
        print(f"CD monotone increasing across the bracket: {mono}  ({cds})")
        if not mono:
            print("  A non-monotone CD at Re~6.7e5 on an attached NACA0012 means a "
                  "scenario is not solving the case it is registered to solve.")

    cls = [r["CL"] for r in rows]
    alphas = [r["alpha_deg"] for r in rows]
    if all(c is not None for c in cls) and len(cls) == 3:
        s1 = (cls[1] - cls[0]) / (alphas[1] - alphas[0])
        s2 = (cls[2] - cls[1]) / (alphas[2] - alphas[1])
        print(f"dCL/dalpha lower pair: {s1:.6f} /deg")
        print(f"dCL/dalpha upper pair: {s2:.6f} /deg")
        if abs(s1) > 0:
            ratio = s2 / s1
            print(f"slope ratio upper/lower: {ratio:.4f}")
            print(f"thin-airfoil reference 2*pi/rad = {2*math.pi/180.0:.6f} /deg")
            print("  ratio near 1.0 -> bracket is in the linear, attached range.")
            print("  ratio materially below 1.0 -> lift going nonlinear at the top "
                  "of the bracket: SEPARATION ONSET SIGNATURE, and SO-3a's "
                  "registered +2 deg wing would need re-examination.")
            print("  INDICATOR ONLY -- a real attachment claim needs wall shear, "
                  "which this rung does not buy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
