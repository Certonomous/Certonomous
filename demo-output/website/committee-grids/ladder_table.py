#!/usr/bin/env python3
"""Emit the diagnosis-ladder table as markdown, straight from the solver logs.

The table in the write-up is produced by this script rather than typed, so no
number in it passes through a human transcription step.
"""
import glob
import json
import os
import re

R = "/home/ubuntu/certonomous-runs/dpw5-committee-probe"
LOGS = f"{R}/logs"

DESC = {
    "base": ("the exact HLPW6 configuration", "-- (reference)"),
    "nonorth2": ("2 non-orthogonal correctors", "nNonOrthogonalCorrectors 0 -> 2"),
    "nonorth6": ("6 non-orthogonal correctors", "nNonOrthogonalCorrectors 0 -> 6"),
    "uncorr": ("no non-orthogonal correction at all", "snGrad/laplacian -> uncorrected"),
    "limlin": ("TVD face limiter, no gradient reconstruction", "div(phi,U) -> limitedLinear 1"),
    "linupV": ("vector-limited linear upwind", "div(phi,U) -> linearUpwindV"),
    "pcg": ("PCG/DIC instead of GAMG", "p solver -> PCG"),
    "pcap": ("pressure solve capped at 100 iterations", "GAMG -> DICGaussSeidel, maxIter 100"),
    "wdpois": ("Poisson wall distance", "wallDist -> Poisson"),
    "potinit": ("potential-flow initial field", "potentialFoam pre-step"),
    "potprod": ("potential-flow start + production schemes", "potentialFoam + limitedLinear + 2 correctors"),
    "prod": ("production-shaped combination", "limitedLinear, 2 correctors, limited 0.25, p 0.2 / U 0.4"),
    "combo": ("linearUpwindV + 2 correctors + limited 0.5", "three axes at once"),
    "base_sa": ("Spalart-Allmaras instead of k-omega SST", "turbulence model"),
    "slow": ("slower relaxation", "p 0.3 -> 0.1, U 0.5 -> 0.3"),
    "crawl": ("much slower relaxation", "p 0.05, U 0.2"),
    "crawl2": ("much slower relaxation + 2 correctors", "p 0.05, U 0.2, nNonOrth 2"),
    "crawl3": ("slowest, everything stabilising at once", "p 0.02, U 0.1, limitedLinear, capped p"),
    "upwind1": ("FIRST ORDER -- control, not a submission", "div(phi,U) -> upwind"),
}

mem = {}
for ln in open(f"{R}/measurements.jsonl"):
    try:
        d = json.loads(ln)
    except ValueError:
        continue
    mem[d["tag"]] = d

rows = []
for path in sorted(glob.glob(f"{LOGS}/hybrid_*_incompressible_a2.11_solve.log")):
    tag = os.path.basename(path)[:-len("_solve.log")]
    v = tag[len("hybrid_"):-len("_incompressible_a2.11")]
    txt = open(path, errors="replace").read()
    it = re.findall(r"^Time = (\d+)", txt, re.M)
    last = int(it[-1]) if it else 0
    died = ("exited on signal 8" in txt
            or "Signal: Floating point exception (8)" in txt)
    m = mem.get(tag, {})
    rc = m.get("exit_code")
    survived = (rc == 0 and last >= 120)
    rows.append((v, last, rc, m.get("wall_s"), survived, died))

order = ["base", "nonorth2", "nonorth6", "uncorr", "limlin", "linupV", "combo",
         "prod", "pcg", "pcap", "wdpois", "potinit", "potprod", "base_sa",
         "slow", "crawl", "crawl2", "crawl3", "upwind1"]
rows.sort(key=lambda r: order.index(r[0]) if r[0] in order else 99)

print("| variant | what was changed | iterations of 120 | exit | outcome |")
print("|---|---|---:|---:|---|")
for v, last, rc, wall, survived, died in rows:
    what = DESC.get(v, (v, v))[1]
    if survived:
        out = "**completed**"
    elif died:
        out = "diverged, signal 8"
    else:
        out = f"stopped (rc {rc})"
    star = " **(first order)**" if v == "upwind1" else ""
    print(f"| `{v}`{star} | {what} | {last} | {rc} | {out} |")
