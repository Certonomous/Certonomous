#!/usr/bin/env python3
"""One row per solver run: how far it got, how it ended, and on what evidence.

Reads the solver logs directly rather than any hand-kept note, so every field
in the table is traceable to the log named in the first column.
"""
import glob
import json
import os
import re
import sys

LOGS = "/home/ubuntu/certonomous-runs/dpw5-committee-probe/logs"
MEAS = "/home/ubuntu/certonomous-runs/dpw5-committee-probe/measurements.jsonl"

mem = {}
if os.path.exists(MEAS):
    for ln in open(MEAS):
        try:
            d = json.loads(ln)
        except ValueError:
            continue
        mem[d["tag"]] = d

rows = []
for path in sorted(glob.glob(f"{LOGS}/*_solve.log")):
    tag = os.path.basename(path)[:-len("_solve.log")]
    txt = open(path, errors="replace").read()
    iters = len(re.findall(r"^Time = (\d+)", txt, re.M))
    last = re.findall(r"^Time = (\d+)", txt, re.M)
    last = int(last[-1]) if last else 0

    # NB: OpenFOAM prints "sigFpe : Enabling floating point exception trapping"
    # in its startup banner, so the plain phrase is not evidence of a crash.
    # Only the MPI abort line or the signal report is.
    fpe = ("exited on signal 8" in txt
           or "Signal: Floating point exception (8)" in txt)
    ceiling = len(re.findall(r"Solving for p.*No Iterations 1000", txt))
    converged = "SIMPLE solution converged" in txt
    ended = "End\n" in txt or "Finalising" in txt

    # last finite Ux initial residual
    ux = re.findall(r"Solving for Ux, Initial residual = ([0-9.e+-]+)", txt)
    ux0 = float(ux[0]) if ux else float("nan")
    uxN = float(ux[-1]) if ux else float("nan")

    # continuity error trace
    cont = [float(m) for m in re.findall(
        r"continuity errors : sum local = ([0-9.e+-]+)", txt)]
    contmax = max((abs(c) for c in cont), default=float("nan"))

    cl = re.findall(r"^\s*Cl:\s+([0-9.e+-]+)", txt, re.M)
    cd = re.findall(r"^\s*Cd:\s+([0-9.e+-]+)", txt, re.M)
    m = mem.get(tag, {})
    rows.append(dict(tag=tag, iters=last, rc=m.get("exit_code"),
                     wall=m.get("wall_s"), peak=m.get("sum_vmhwm_mib"),
                     fpe=fpe, ceiling=ceiling, converged=converged,
                     ux0=ux0, uxN=uxN, contmax=contmax,
                     cl=float(cl[-1]) if cl else float("nan"),
                     cd=float(cd[-1]) if cd else float("nan")))

w = max(len(r["tag"]) for r in rows) if rows else 10
print(f"{'run':<{w}} {'iters':>6} {'rc':>4} {'wall_s':>8} {'peakMiB':>8} "
      f"{'p@1000':>7} {'FPE':>4} {'Ux_res_last':>12} {'max|cont|':>11} "
      f"{'Cl':>12} {'Cd':>12}")
for r in rows:
    print(f"{r['tag']:<{w}} {r['iters']:>6} {str(r['rc']):>4} "
          f"{r['wall'] if r['wall'] is not None else 0:>8.1f} "
          f"{r['peak'] if r['peak'] is not None else 0:>8.0f} "
          f"{r['ceiling']:>7} {'yes' if r['fpe'] else '-':>4} "
          f"{r['uxN']:>12.4g} {r['contmax']:>11.4g} "
          f"{r['cl']:>12.5g} {r['cd']:>12.5g}")
