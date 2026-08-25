#!/usr/bin/env python3
"""VMFL059 comparator -- Conduction in a Composite Solid Block (manual p.185).

NO GRADED COMPUTE has been run by, or is triggered by, this file. It grades a
run that the ansys-verification SUPERVISOR unlocks after four personal checks;
until then `--selftest` exercises the reference, the plant and the classifier
with NO run data. It REFUSES (exit 2) rather than degrades; every refusal names
its clause (CLAUDE.md rule 4). Reference: Incropera & DeWitt, Fundamentals of
Heat and Mass Transfer, 5th ed. p.117 -- a CLOSED-FORM analytical solution
(buys V). Driving input q'''=1.5e6 W/m3 read from the Ansys archive case
(cond-slab.cas.h5), NOT from the 378/413 K targets.

Reader: postProcessing/patchAverage(name=<patch>,T)/<t>/surfaceFieldValue.dat
(areaAverage of T over the wall patch), produced post-solve by the run script.

Usage:
    python3 grade_vmfl059.py --selftest
    python3 grade_vmfl059.py --run-root <dir with L1 L2 L3>
"""
import sys, os, re, glob, shutil, tempfile, argparse

# ---- geometry / material inputs (manual p.185 + archive), NOT the targets ----
K1, K2   = 75.0, 150.0          # W/m-K  material 1 (gen), material 2      (manual)
L1, L2   = 0.05, 0.02           # m      slab-1 thickness; slab-2 = 0.07-0.05 (manual)
QGEN     = 1.5e6                # W/m3   volumetric generation (ARCHIVE cond-slab.cas.h5)
H_CONV   = 1000.0              # W/m2-K convective coefficient                (manual)
TINF     = 303.0              # K      free-stream temperature               (manual)

# ---- the reference: closed-form 1-D composite wall with generation ----
def T_cooled_exact():
    """Right (convective) wall surface temperature [K]. Global energy balance:
    all generated heat q'''*L1 leaves by convection: q''*=h(Ts-Tinf)."""
    qflux = QGEN * L1                       # W/m2 leaving the right face
    return TINF + qflux / H_CONV            # 303 + 75000/1000 = 378
def T_adiabatic_exact():
    """Left (adiabatic) wall temperature [K]. Interface temp + parabolic rise
    across the generating slab (adiabatic at x=0, max there)."""
    qflux = QGEN * L1
    T_interface = T_cooled_exact() + qflux * L2 / K2      # +10 -> 388
    return T_interface + QGEN * L1*L1 / (2.0*K1)          # +25 -> 413

REF_COOLED = T_cooled_exact()     # 378.0 K, EXACT (analytical) -- THE GATE reference
REF_ADIAB  = T_adiabatic_exact()  # 413.0 K, EXACT (analytical) -- THE GATE reference
MANUAL_COOLED, MANUAL_ADIAB = 378.0, 413.0   # printed targets (coincide with exact)
ANSYS_COOLED, ANSYS_ADIAB   = 378.14, 413.17 # Fluent, CONTEXT ONLY (never the gate)

# ---- THE GATE (frozen in PREREGISTRATION.md, sec.4) ----
TOL = 0.01                        # relative, on BOTH wall temperatures (absolute K)
PLANT     = 1.234                 # K, planted-zero control perturbation
PLANT_TOL = 1e-9

LEVELS = ("L1", "L2", "L3")
PATCH_COOLED, PATCH_ADIAB = "rightWall", "leftWall"

def refuse(msg):
    sys.stderr.write("REFUSE (VMFL059): %s\n" % msg); sys.exit(2)

# ---- reader ----
def _sfv_path(level_dir, patch):
    pats = glob.glob(os.path.join(level_dir, "postProcessing",
                                  "patchAverage(name=%s,T)" % patch, "*", "surfaceFieldValue.dat"))
    if len(pats) != 1:
        refuse("expected exactly one surfaceFieldValue.dat for patch %r in %s, found %d"
               % (patch, level_dir, len(pats)))
    return pats[0]

def _read_sfv(path):
    last = None
    with open(path) as f:
        for s in f:
            s = s.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) < 2:
                refuse("data row < 2 cols in %s: %r" % (path, s))
            try:
                last = (float(parts[0]), float(parts[-1]))
            except ValueError:
                refuse("unparseable row in %s: %r" % (path, s))
    if last is None:
        refuse("no data rows in " + path)
    return last                                   # (time, areaAverage(T))

def wall_temp(level_dir, patch):
    return _read_sfv(_sfv_path(level_dir, patch))[1]

# ---- strict completion (CLAUDE.md rule 4) ----
def check_completion(level_dir):
    log = glob.glob(os.path.join(level_dir, "log.laplacianFoam"))
    if not log:
        refuse("no solver log (log.laplacianFoam) in " + level_dir)
    txt = open(log[0]).read()
    if not re.search(r"^End\b", txt, re.M):
        refuse("no End line in solver log: " + level_dir)
    # age guard: every field at latestTime newer than 0/T
    t0 = os.path.join(level_dir, "0", "T")
    if not os.path.exists(t0):
        refuse("no 0/T launch marker (age guard cannot run): " + level_dir)
    times = [d for d in os.listdir(level_dir)
             if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and float(d) > 0]
    if not times:
        refuse("no written time directory > 0: " + level_dir)
    latest = max(times, key=float)
    tf = os.path.join(level_dir, latest, "T")
    if not os.path.exists(tf):
        refuse("no T field at latestTime %s: %s" % (latest, level_dir))
    if os.path.getmtime(tf) <= os.path.getmtime(t0):
        refuse("age guard: T at %s not newer than 0/T in %s" % (latest, level_dir))
    return latest

# ---- planted-zero control (CLAUDE.md rule 3) ----
def planted_zero_control(level_dir, patch):
    src = _sfv_path(level_dir, patch)
    before = _read_sfv(src)[1]
    tmp = tempfile.mkdtemp(prefix="vmfl059plant_")
    try:
        work = os.path.join(tmp, os.path.basename(src))
        # plant into the value column of the LAST data row, then re-read
        lines = open(src).read().splitlines()
        for i in range(len(lines)-1, -1, -1):
            s = lines[i].strip()
            if s and not s.startswith("#"):
                p = lines[i].split()
                p[-1] = repr(float(p[-1]) + PLANT)
                lines[i] = "\t".join(p)
                break
        open(work, "w").write("\n".join(lines) + "\n")
        after = _read_sfv(work)[1]
        moved = after - before
        return dict(passed=abs(moved - PLANT) <= PLANT_TOL, planted=PLANT, seen=moved)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# ---- Roache triple (CLAUDE.md rule 5), r=2 ----
def roache(vals):
    f1, f2, f3 = vals                              # coarse->fine (L1,L2,L3)
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0:
        return dict(triple="EXACT", p=None, gci=None)
    R = e32 / e21
    if R <= 0:
        return dict(triple="OSCILLATORY", p=None, gci=None)
    if R >= 1:
        return dict(triple="DIVERGENT", p=None, gci=None)
    import math
    p = math.log(e21 / e32) / math.log(2.0)
    gci = 1.25 * abs((f3 - f2) / f3) / (2.0**p - 1.0)
    return dict(triple="CONVERGING", p=p, gci=gci)

def selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok
        print(("  PASS " if cond else "  FAIL ") + name); ok = ok and cond
    print("VMFL059 comparator --selftest (NO run data touched)")
    chk("cooled-wall exact == 378.0 K", abs(REF_COOLED - 378.0) < 1e-9)
    chk("adiabatic-wall exact == 413.0 K", abs(REF_ADIAB - 413.0) < 1e-9)
    chk("exact coincides with manual targets", REF_COOLED == MANUAL_COOLED and REF_ADIAB == MANUAL_ADIAB)
    # plant on a synthetic .dat
    tmp = tempfile.mkdtemp(prefix="vmfl059self_")
    try:
        d = os.path.join(tmp, "postProcessing", "patchAverage(name=rightWall,T)", "10")
        os.makedirs(d); p = os.path.join(d, "surfaceFieldValue.dat")
        open(p, "w").write("# Time areaAverage(T)\n10\t378.0\n")
        chk("reader reads 378.0", abs(wall_temp(tmp, "rightWall") - 378.0) < 1e-9)
        pc = planted_zero_control(tmp, "rightWall")
        chk("plant %.3f seen by reader" % PLANT, pc["passed"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # classifier
    r = roache([412.0, 412.8, 412.95]); chk("monotone-in triple CONVERGING", r["triple"] == "CONVERGING")
    r = roache([413.0, 412.0, 413.0]); chk("non-monotone triple OSCILLATORY", r["triple"] == "OSCILLATORY")
    print("SELFTEST", "OK" if ok else "FAILED"); sys.exit(0 if ok else 1)

def grade(run_root):
    cooled, adiab = [], []
    for lvl in LEVELS:
        d = os.path.join(run_root, lvl)
        if not os.path.isdir(d):
            refuse("missing level directory %s (run is LOCKED until supervisor unlock)" % d)
        check_completion(d)
        for patch in (PATCH_COOLED, PATCH_ADIAB):
            if not planted_zero_control(d, patch)["passed"]:
                refuse("planted-zero control did not fire for %s in %s" % (patch, d))
        cooled.append(wall_temp(d, PATCH_COOLED))
        adiab.append(wall_temp(d, PATCH_ADIAB))
    print("VMFL059  cooled(L1,L2,L3)=%s  adiabatic=%s" % (cooled, adiab))
    for name, vals, ref in (("cooled", cooled, REF_COOLED), ("adiabatic", adiab, REF_ADIAB)):
        rc = roache(vals); vf = vals[-1]; rel = abs(vf - ref) / abs(ref)
        if rc["triple"] != "CONVERGING":
            print("  %s: NOT A RESULT  triple=%s  value=%.4f" % (name, rc["triple"], vf)); continue
        verdict = "PASS" if rel <= TOL else "GATE FAIL"
        print("  %s: %s  value=%.4f ref=%.4f rel=%.4f%% tol=%.1f%% GCI=%.3g%% p=%.2f"
              % (name, verdict, vf, ref, 100*rel, 100*TOL, 100*rc["gci"], rc["p"]))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run-root")
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.run_root: grade(a.run_root)
    else: ap.error("give --selftest or --run-root")
