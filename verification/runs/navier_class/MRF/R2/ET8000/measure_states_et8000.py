#!/usr/bin/env python3
"""MRF R2 ET8000 -- measure the two STATE INPUTS the REGISTERED grader requires,
and emit its --levels JSON. MEASURES; asserts nothing.

WHY THIS FILE EXISTS AT ALL. The registered grading path is
cases/navier_class/MRF/grade_mrf_np.py (sha256 2a443bfe731ea43e...f08d, the LITERAL
pinned in MRF_R2_PREREGISTRATION.md:674), and it takes iterative_state and
plateau_state as INPUTS, per level. Those states are produced by
cases/navier_class/MRF/measure_states_mrf.py -- whose main() hardcodes

    root = ".../verification/runs/navier_class/MRF"      (measure_states_mrf.py:152)

and prints "MRF_R1 state measurement". CALLING IT WOULD SILENTLY MEASURE R1 AND HAND
R1's STATES TO AN R2 GRADE. So main() is never called. This file mirrors main()'s
state logic VERBATIM -- the same functions, the same order, the same thresholds --
with exactly one thing changed: the root. Nothing else is re-implemented; s12,
divergence_tells, read_total_axial and power_number are IMPORTED, not copied, so
they cannot drift from the pinned module.

THE MIRRORED LOGIC, from measure_states_mrf.py:180-192:
    fires, drift, mono, w = s12(np_series)
    nan, fpe, bnd, early, late, cascade = divergence_tells(log, n_iters=int(t[-1]))
    plateau  = "NOT_PLATEAUED" if fires else "PLATEAUED"
    diverged = bool(nan or fpe or cascade)
    iterative = "NOT_CONVERGED" if (diverged or fires) else "CONVERGED"

RULE 3. The plant control is run on EACH level's own moment.dat -- main() plants only
into coarse's and lets that one control license all three levels' readings. Planting
per level is STRICTLY STRONGER and can only make this refuse where main() would have
proceeded: fail-closed, never fail-open.

READ-ONLY. Plants into a tempfile.mkdtemp copy. Writes nothing into any case dir.
Emits no verdict, no gate, no band. The VERDICT comes from the registered grader.
"""
import importlib.util, json, math, os, shutil, sys, tempfile

BASE = "/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2/ET8000"
CASE = "/home/ubuntu/Certonomous/cases/navier_class/MRF"
LEVELS = ("coarse", "medium", "fine")
END = 8000


def load(nm, p):
    s = importlib.util.spec_from_file_location(nm, p)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


msm = load("msm", f"{CASE}/measure_states_mrf.py")


def cells(level):
    """Cells summed from the run's OWN decomposePar log, never from a document."""
    tot = 0
    for ln in open(os.path.join(BASE, level, "log.decomposePar"), errors="ignore"):
        if "Number of cells = " in ln:
            tot += int(ln.split("=")[1].strip())
    return tot


def plant_ok(mom):
    td = tempfile.mkdtemp(prefix="et8k_plant_")
    try:
        pl = os.path.join(td, "moment.dat"); shutil.copy(mom, pl)
        L = open(pl).read().splitlines()
        for i, ln in enumerate(L):
            if not ln.startswith("#"):
                tk = ln.replace("(", " ").replace(")", " ").split()
                L[i] = f"{tk[0]}\t({tk[1]} {tk[2]} {msm.PLANT:.12g})\t(0 0 0)\t(0 0 0)"
                break
        open(pl, "w").write("\n".join(L) + "\n")
        _, pv = msm.read_total_axial(pl)
        return abs(pv[0] - msm.PLANT) <= 1e-12
    finally:
        shutil.rmtree(td, True)


def main():
    print("MRF R2 ET8000 -- STATE MEASUREMENT (mirrors measure_states_mrf.main(), root changed)")
    print("  S12: window = trailing quarter, floor 20, cap 2000; fires iff "
          "|drift| >= 1e-3 AND monotone >= 0.90\n")
    cfg = []
    for name in LEVELS:
        d = os.path.join(BASE, name)
        mom = os.path.join(d, "postProcessing/impellerForces/0/moment.dat")
        if not os.path.isfile(mom):
            print(f"REFUSE: {mom} absent -- cannot measure {name}"); return 2
        if not plant_ok(mom):
            print(f"REFUSE (rule 3): the reader did not see {msm.PLANT:.6g} in "
                  f"{name}'s OWN moment.dat. A zero from a blind reader is not evidence.")
            return 2
        t, mz = msm.read_total_axial(mom)
        ser = [msm.power_number(q) for q in mz]
        if t[-1] < END:
            print(f"REFUSE: {name} last time {t[-1]:.0f} < endTime {END} -- not landed.")
            return 2
        idx = max(i for i, tt in enumerate(t) if tt <= END) + 1
        t, ser = t[:idx], ser[:idx]
        fires, drift, mono, w = msm.s12(ser)
        nan, fpe, bnd, early, late, cascade = msm.divergence_tells(
            os.path.join(d, "log.simpleFoam"), n_iters=int(t[-1]))
        plateau = "NOT_PLATEAUED" if fires else "PLATEAUED"
        diverged = bool(nan or fpe or cascade)
        iterative = "NOT_CONVERGED" if (diverged or fires) else "CONVERGED"
        finite = all(math.isfinite(v) for v in ser)
        print(f"--- {name} ---")
        print(f"  [rule 3] plant PASS on THIS level's own moment.dat")
        print(f"  samples={len(ser)}  all finite={finite}  last time={t[-1]:.0f}  cells={cells(name):,}")
        print(f"  S12 window w={w} (iters {int(t[-w])}..{int(t[-1])})")
        print(f"  relative drift  = {drift:+.4e}   (fires at |drift| >= 1e-3)")
        print(f"  monotone frac   = {mono:.4f}       (fires at >= 0.90)")
        print(f"  S12 {'FIRES -- still travelling' if fires else 'SILENT -- settled'}")
        print(f"  divergence tells: NaN={nan}  FPE(real, banner excluded)={fpe}")
        print(f"  bounding at {bnd if bnd else 'none'} -> first-q={early} final-q={late} "
              f"cascade_builds={cascade}")
        print(f"  Np window mean  = {sum(ser[-w:])/w:.6f}")
        print(f"  Np at endTime   = {ser[-1]:.6f}")
        print(f"  => iterative_state={iterative}  plateau_state={plateau}\n")
        cfg.append(dict(name=name, case_dir=d, cells=cells(name), end_time=END,
                        iterative_state=iterative, plateau_state=plateau))
    out = os.path.join(BASE, "levels_et8000.json")
    with open(out, "w") as fh:
        json.dump(cfg, fh, indent=2)
    print("STATES FOR THE REGISTERED GRADER (measured, not asserted):")
    for c in cfg:
        print(f"  {c['name']:7s} iterative={c['iterative_state']:13s} plateau={c['plateau_state']}")
    print(f"\nwritten: {out}")
    print("NO VERDICT HERE. The verdict comes from grade_mrf_np.py --levels this file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
