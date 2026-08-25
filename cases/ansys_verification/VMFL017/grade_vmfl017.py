#!/usr/bin/env python3
"""VMFL017 comparator -- Transonic Flow over an RAE 2822 Airfoil (manual p.69).

Grades the drag and lift coefficients (Cd, Cl) against the manual's experimental
targets Cd=0.0168, Cl=0.803.

REFERENCE KIND -- DECLARED BEFORE ANY RUN: EXPERIMENTAL/MEASURED. Source =
P.H. Cook, M.A. McDonald, M.C.P. Firmin, "AEROFOIL RAE 2822 -- Pressure
Distribution and Boundary Layer and Wake Measurements", AGARD AR-138, 1979. A
measured reference CAN buy P: BOTH coefficients in-band at a CONVERGING finest
level -> PASS (validation vs experiment); else GATE FAIL; a non-converging triple
-> NOT A RESULT (rule 5). Manual context (Ansys Fluent, NEVER the gate):
Cd 0.016 (ratio 0.952), Cl 0.78 (0.971) -- i.e. Ansys ITSELF is 4.8% off on drag.

GEOMETRY PROVENANCE: airfoil = the in-repo RAE 2822 ordinates at
verification/runs/F12_runs/reference/rae2822_coordinates.dat (NPARC / AGARD
AR-138 Table 6.1, cross-checked to 3.1e-06 chord); mesh = the birth-certified
ratio-2 C-mesh family from that geometry (see PREREGISTRATION.md sec.7/8).

NO cell-centre radius, axis extrapolation or constructed geometry enters this gate
(supervisor standing instruction): Cd and Cl are read directly from OpenFOAM's
forceCoeffs function object, which integrates surface forces on the airfoil patch.

Reader: postProcessing/forceCoeffs1/<t>/coefficient.dat, columns
  Time  Cd  Cd(f)  Cd(r)  Cl  ...   -> col 1 = Cd, col 4 = Cl.
This grader RUNS NOTHING; --selftest exercises reader, plant, plateau, Roache.
REFUSES (exit 2) rather than degrading.
"""
import sys, os, re, glob, math, shutil, tempfile, argparse

REF_CD   = 0.0168          # AGARD AR-138 experimental drag target
REF_CL   = 0.803           # experimental lift target
ANSYS_CD = 0.016           # CONTEXT ONLY
ANSYS_CL = 0.78            # CONTEXT ONLY
TOL_CD   = 0.10            # relative band on Cd at finest level (justified in prereg sec.6)
TOL_CL   = 0.05            # relative band on Cl at finest level
ENDTIME  = 6000            # SIMPLE iterations (residualControl may converge earlier)
WINDOW_FRAC = 0.20         # steady window = last 20% of written iterations
PLATEAU_TOL = 0.02         # window coeff-of-variation must be < 2% (rule 5 gate 1)
LEVELS   = ("L1", "L2", "L3")
PLANT    = 7.531e-03
PLANT_TOL = 1e-9
COL_CD, COL_CL = 1, 4

def refuse(msg):
    sys.stderr.write("REFUSE (VMFL017): %s\n" % msg); sys.exit(2)

def _coeff_dat(level_dir):
    pats = glob.glob(os.path.join(level_dir, "postProcessing", "forceCoeffs1", "*", "coefficient.dat"))
    if len(pats) != 1:
        refuse("expected one forceCoeffs1 coefficient.dat in %s, found %d" % (level_dir, len(pats)))
    return pats[0]

def _series(path, col):
    rows = []
    with open(path) as f:
        for s in f:
            s = s.strip()
            if not s or s.startswith("#"):
                continue
            p = s.split()
            if len(p) <= col:
                refuse("row has %d cols, need col %d in %s" % (len(p), col, path))
            try:
                rows.append((float(p[0]), float(p[col])))
            except ValueError:
                refuse("unparseable row in %s: %r" % (path, s))
    if not rows:
        refuse("no data rows in " + path)
    return rows

def _window(path, col):
    ser = _series(path, col)
    tmax = ser[-1][0]
    tcut = tmax * (1.0 - WINDOW_FRAC)
    win = [v for (t, v) in ser if t >= tcut - 1e-9]
    if len(win) < 5:
        refuse("only %d rows in the final %.0f%% window of %s" % (len(win), 100 * WINDOW_FRAC, path))
    return win

def coeff(level_dir, col):
    win = _window(_coeff_dat(level_dir), col)
    return sum(win) / len(win)

def plateau_ok(level_dir, col):
    win = _window(_coeff_dat(level_dir), col)
    m = sum(win) / len(win)
    if m == 0:
        return False
    var = sum((x - m) ** 2 for x in win) / len(win)
    return math.sqrt(var) / abs(m) <= PLATEAU_TOL

def check_completion(level_dir):
    logs = glob.glob(os.path.join(level_dir, "log.rhoSimpleFoam"))
    if not logs:
        refuse("no log.rhoSimpleFoam in " + level_dir)
    txt = open(logs[0]).read()
    if not re.search(r"^End\b", txt, re.M):
        refuse("no End line in solver log: " + level_dir)
    u0 = os.path.join(level_dir, "0", "U")
    if not os.path.exists(u0):
        refuse("no 0/U launch marker (age guard): " + level_dir)
    times = [d for d in os.listdir(level_dir)
             if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and float(d) > 0]
    if not times:
        refuse("no written time > 0 (steady state not written): " + level_dir)
    latest = max(times, key=float)
    uf = os.path.join(level_dir, latest, "U")
    if not os.path.exists(uf):
        refuse("no U at latestTime %s: %s" % (latest, level_dir))
    if os.path.getmtime(uf) <= os.path.getmtime(u0):
        refuse("age guard: U at %s not newer than 0/U in %s" % (latest, level_dir))
    # steady solver: EITHER residualControl converged OR reached endTime
    converged = ("SIMPLE solution converged" in txt) or (abs(float(latest) - ENDTIME) < 1e-6)
    if not converged:
        refuse("steady solve neither converged nor reached endTime (last=%s) in %s" % (latest, level_dir))
    return latest

def planted_zero_control(level_dir, col):
    src = _coeff_dat(level_dir)
    before = sum(_window(src, col)) / len(_window(src, col))
    tmp = tempfile.mkdtemp(prefix="vmfl017plant_")
    try:
        work = os.path.join(tmp, "coefficient.dat")
        lines = open(src).read().splitlines()
        for i in range(len(lines) - 1, -1, -1):
            s = lines[i].strip()
            if s and not s.startswith("#"):
                p = lines[i].split()
                p[col] = repr(float(p[col]) + PLANT)
                lines[i] = "\t".join(p)
                break
        open(work, "w").write("\n".join(lines) + "\n")
        after = sum(_window(work, col)) / len(_window(work, col))
        moved = (after - before) * len(_window(src, col))  # only last row perturbed
        return abs(moved - PLANT) <= PLANT_TOL
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def roache(vals):
    f1, f2, f3 = vals
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0 or e32 == 0:
        return dict(triple="EXACT", p=None, gci=None)
    R = e32 / e21
    if R <= 0:
        return dict(triple="OSCILLATORY", p=None, gci=None)
    if R >= 1:
        return dict(triple="DIVERGENT", p=None, gci=None)
    p = math.log(e21 / e32) / math.log(2.0)
    return dict(triple="CONVERGING", p=p, gci=1.25 * abs((f3 - f2) / f3) / (2.0 ** p - 1.0))

def selftest():
    ok = True
    def chk(n, c):
        nonlocal ok
        print(("  PASS " if c else "  FAIL ") + n); ok = ok and c
    print("VMFL017 comparator --selftest (NO run data touched)")
    chk("reference kind measured/experimental -> both bands + CONVERGING can score PASS", True)
    tmp = tempfile.mkdtemp(prefix="vmfl017self_")
    try:
        d = os.path.join(tmp, "postProcessing", "forceCoeffs1", "0")
        os.makedirs(d)
        with open(os.path.join(d, "coefficient.dat"), "w") as fh:
            fh.write("# Time\tCd\tCd(f)\tCd(r)\tCl\n")
            for k in range(50):
                cd = 0.0180 * (1.0 + 1e-3 * (49 - k))
                cl = 0.800 * (1.0 + 1e-3 * (49 - k))
                fh.write("%d\t%r\t0\t0\t%r\n" % (100 * (k + 1), cd, cl))
        chk("Cd reader ~0.0180", abs(coeff(tmp, COL_CD) - 0.0180) < 5e-4)
        chk("Cl reader ~0.800", abs(coeff(tmp, COL_CL) - 0.800) < 5e-3)
        chk("plateau detected (Cd)", plateau_ok(tmp, COL_CD))
        chk("plant seen (Cd)", planted_zero_control(tmp, COL_CD))
        # non-plateaued window must be rejected (fresh dir with one series)
        tmp2 = tempfile.mkdtemp(prefix="vmfl017wob_")
        try:
            dw = os.path.join(tmp2, "postProcessing", "forceCoeffs1", "0")
            os.makedirs(dw)
            with open(os.path.join(dw, "coefficient.dat"), "w") as fh:
                fh.write("# Time\tCd\tCd(f)\tCd(r)\tCl\n")
                for k in range(50):
                    fh.write("%d\t%r\t0\t0\t0.8\n" % (100 * (k + 1), 0.018 * (1 + 0.1 * (k % 2))))
            chk("non-plateaued Cd rejected", not plateau_ok(tmp2, COL_CD))
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    chk("CONVERGING triple", roache([0.030, 0.020, 0.017])["triple"] == "CONVERGING")
    chk("DIVERGENT triple flagged", roache([0.017, 0.020, 0.030])["triple"] == "DIVERGENT")
    chk("OSCILLATORY triple flagged", roache([0.020, 0.017, 0.020])["triple"] == "OSCILLATORY")
    print("SELFTEST", "OK" if ok else "FAILED"); sys.exit(0 if ok else 1)

def grade(run_root):
    present = [l for l in LEVELS if os.path.isdir(os.path.join(run_root, l))]
    if not present:
        refuse("no level dirs under " + run_root)
    cds, cls = [], []
    for lvl in present:
        d = os.path.join(run_root, lvl)
        check_completion(d)
        for col, name in ((COL_CD, "Cd"), (COL_CL, "Cl")):
            if not planted_zero_control(d, col):
                refuse("planted-zero control did not fire for %s in %s" % (name, d))
            if not plateau_ok(d, col):
                print("VMFL017  NOT A RESULT  %s/%s not plateaued (rule 5 gate 1)" % (lvl, name)); return
        cds.append(coeff(d, COL_CD)); cls.append(coeff(d, COL_CL))
    print("VMFL017  levels=%s" % list(present))
    print("  Cd=%s  ref=%.4f" % (["%.5f" % v for v in cds], REF_CD))
    print("  Cl=%s  ref=%.4f" % (["%.4f" % v for v in cls], REF_CL))
    if len(present) < 3:
        print("  SINGLE/PARTIAL GRID (%d of 3 levels): no Roache triple, verdict is single-grid; "
              "family PENDING for GCI." % len(present))
        return
    rcd, rcl = roache(cds), roache(cls)
    cdf, clf = cds[-1], cls[-1]
    if rcd["triple"] != "CONVERGING" or rcl["triple"] != "CONVERGING":
        print("  NOT A RESULT  Cd triple=%s  Cl triple=%s  (rule 5)" % (rcd["triple"], rcl["triple"])); return
    rel_cd = abs(cdf - REF_CD) / REF_CD
    rel_cl = abs(clf - REF_CL) / REF_CL
    passed = rel_cd <= TOL_CD and rel_cl <= TOL_CL
    verdict = "PASS" if passed else "GATE FAIL"
    print("  %s  Cd=%.5f rel=%.2f%% tol=%.0f%% GCI=%.3g%% p=%.2f | Cl=%.4f rel=%.2f%% tol=%.0f%% GCI=%.3g%% p=%.2f"
          % (verdict, cdf, 100 * rel_cd, 100 * TOL_CD, 100 * rcd["gci"], rcd["p"],
             clf, 100 * rel_cl, 100 * TOL_CL, 100 * rcl["gci"], rcl["p"]))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run-root")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.run_root:
        grade(a.run_root)
    else:
        ap.error("give --selftest or --run-root")
