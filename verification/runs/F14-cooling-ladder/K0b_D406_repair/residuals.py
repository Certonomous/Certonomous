#!/usr/bin/env python3
"""residuals.py -- the four final initial residuals of each leg beside the
case's own residualControl targets, and the leg's stopping reason.

Reported, never gated on.  This is the SHAPE D407 asks for; it is printed here
because this run produced logs and refusing to read them would be a second
silence.  It is NOT the D407 repair: D407 is a defect of
`analyse_k0b_mesh.py:264-265`, that file is not edited by this task, and this
script adds no reporting to it.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.abspath(os.path.join(HERE, "..", "..", "THERMAL_K0_runs", "K0b_cavity_Ra1e5"))

TARGETS = {"Ux": ("U", 1e-08), "Uy": ("U", 1e-08),
           "T": ("T", 1e-08), "p_rgh": ("p_rgh", 1e-07)}

def last_residuals(log):
    txt = open(log, errors="replace").read()
    blocks = txt.split("\nTime = ")
    last = blocks[-1]
    out = {}
    for v in ("Ux", "Uy", "T", "p_rgh"):
        m = list(re.finditer(rf"Solving for {v}, Initial residual = ([0-9.eE+-]+)", last))
        if m:
            out[v] = float(m[-1].group(1))
    stopped = "residualControl" if "SIMPLE solution converged in" in txt else "endTime"
    it = re.search(r"SIMPLE solution converged in (\d+) iterations", txt)
    tm = re.findall(r"\nTime = (\d+)", txt)
    return out, stopped, (it.group(1) if it else (tm[-1] if tm else "?"))

legs = [("32x32   (this run)", os.path.join(HERE, "K0b_m32", "log.buoyantBoussinesqSimpleFoam")),
        ("128x128 stage 1 (this run)", os.path.join(HERE, "K0b_m128", "log.buoyantBoussinesqSimpleFoam")),
        ("128x128 continued (this run)", os.path.join(HERE, "K0b_m128", "log.buoyantBoussinesqSimpleFoam.continue")),
        ("64x64   (committed archive, read in place)", os.path.join(ARCH, "log.buoyantBoussinesqSimpleFoam"))]

print(f"{'leg':<44} {'stopped by':<16} {'at':>7} "
      f"{'Ux':>13} {'Uy':>13} {'T':>13} {'p_rgh':>13}   verdict")
for name, log in legs:
    if not os.path.isfile(log):
        print(f"{name:<44} LOG ABSENT: {log}")
        continue
    r, stopped, at = last_residuals(log)
    met = all(r.get(v, 9e9) <= TARGETS[v][1] for v in TARGETS)
    verdict = "CONVERGED" if (stopped == "residualControl" or met) else "stopped at endTime"
    print(f"{name:<44} {stopped:<16} {at:>7} "
          f"{r.get('Ux', float('nan')):>13.4e} {r.get('Uy', float('nan')):>13.4e} "
          f"{r.get('T', float('nan')):>13.4e} {r.get('p_rgh', float('nan')):>13.4e}   {verdict}")
    for v in ("Ux", "Uy", "T", "p_rgh"):
        if v in r:
            tgt = TARGETS[v][1]
            print(f"{'':<44}   {v:<6} {r[v]:.6e}  target {TARGETS[v][0]} {tgt:.0e}  "
                  f"ratio {r[v]/tgt:8.2f}x  {'MET' if r[v] <= tgt else 'ABOVE TARGET'}")
print()
print("residualControl targets are read from the case's own system/fvSolution:")
print("  p_rgh 1e-07, U 1e-08, T 1e-08.")
