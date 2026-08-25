#!/usr/bin/env python3
"""VMFL017-R2 comparator -- Transonic Flow over an RAE 2822 Airfoil (manual p.69).

NEW ROW citing attempt 1 (register row #19, PENDING, commit d1de064b). Attempt 1
used rhoSimpleFoam, which diverged with 'Negative initial temperature T0' at
shock formation. The supervisor's ladder ruling switches the instrument to
rhoCentralFoam (density-based, explicit, transient, shock-capturing) -- the same
instrument that carried VMFL045 (rows #5/#7). THIS FILE IS THE GRADING PATH,
committed with the pre-registration that cites it by sha, before any graded
solver runs (CLAUDE.md rule 2). REFUSES (exit 2) rather than degrading.

Grades drag and lift coefficients (Cd, Cl) against the manual's experimental
targets Cd=0.0168, Cl=0.803 (AGARD AR-138, P.H. Cook/M.A. McDonald/M.C.P. Firmin
1979 -- measured/experimental, CAN buy P). Manual context, NEVER the gate:
Fluent Cd 0.016 (0.952), Cl 0.78 (0.971); CFX Cd 0.0162, Cl 0.7981.

Cd and Cl are read DIRECTLY from OpenFOAM's forceCoeffs function object (no
constructed geometry enters the gate). Reader:
  postProcessing/forceCoeffs1/<t>/coefficient.dat, columns
  Time  Cd  Cd(f)  Cd(r)  Cl  ...  -> col 1 = Cd, col 4 = Cl.

PLATEAU CLAUSE is the PREREG_TEMPLATE Amendment 4 required artifact: a fractional
window WITH a minimum-sample CANNOT_TELL refusal, a peak-to-peak / whole-run-range
statistic that REJECTS A GROWING (unsettled) series, a null-range refusal, and
the realised sample count recorded. CoV is carried only beside, never instead.
(Attempt 1 and the rhoSimpleFoam VMFL017 used CoV alone, which Amendment 4 classes
"Weakest": a monotonically drifting coefficient can have a small CoV.)

  python3 grade_vmfl017_r2.py --selftest
  python3 grade_vmfl017_r2.py --run-root <verification/runs/.../VMFL017/R2>
"""
import sys, os, re, glob, math, shutil, tempfile, argparse, json

REF_CD   = 0.0168          # AGARD AR-138 experimental drag target
REF_CL   = 0.803           # experimental lift target
ANSYS_CD = 0.016           # CONTEXT ONLY, never the gate
ANSYS_CL = 0.78            # CONTEXT ONLY, never the gate
TOL_CD   = 0.10            # relative band on Cd at finest level (prereg line 6)
TOL_CL   = 0.05            # relative band on Cl at finest level (prereg line 6)

# TRANSIENT rhoCentralFoam: endTime is a PHYSICAL settling time (seconds), NOT an
# iteration count.  Registered value; the plateau clause decides if it settled.
ENDTIME_PHYS   = 0.05      # s, registered settling endTime (prereg line 8/12)
ENDTIME_ATOL   = 1.0e-4    # last written time must be within this of endTime
                           # (adaptive-step: maxDeltaT-scale tolerance; VMFL045 form)
WINDOW_FRAC = 0.20         # settled window = last 20% of PHYSICAL time

# --- PLATEAU CLAUSE (PREREG_TEMPLATE Amendment 4, all five items) -------------
PLATEAU_MIN_SAMPLES = 20              # (2) fractional-window floor -> CANNOT_TELL below
PLATEAU_PTP_FRAC_OF_RANGE = 0.05      # (3) final-window ptp <= 5% of whole-run range;
                                      # a still-settling window is a large fraction.
                                      # 5% is looser than VMFL021's 3% because a lift/
                                      # drag coefficient settles by DAMPED OSCILLATION,
                                      # so a small residual ripple is physical.
PLATEAU_NULL_RANGE = 1.0e-6          # (4) if the coeff never resolvably moved over the
                                      # whole run -> CANNOT_TELL (a dead field and a
                                      # converged one are identical to a tolerance).
PLATEAU_COV = 0.02                   # CoV kept BESIDE ptp (never instead), also gated.

LEVELS   = ("L1", "L2", "L3")
PLANT    = 7.531e-03
PLANT_TOL = 1e-9
COL_CD, COL_CL = 1, 4
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg):
    sys.stderr.write("REFUSE (VMFL017-R2): %s\n" % msg); sys.exit(2)


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


def plateau_stat(path, col, label):
    """Amendment 4 plateau clause on a coefficient series. REFUSES (CANNOT_TELL)
    below the sample floor or on a null-range series. Returns the mean over the
    settled window, the peak-to-peak / whole-run-range statistic (rejects an
    unsettled series), CoV beside it, the realised sample count, and plateaued."""
    ser = _series(path, col)
    allv = [v for (t, v) in ser]
    whole_range = max(allv) - min(allv)
    tmax = ser[-1][0]
    tcut = tmax * (1.0 - WINDOW_FRAC)
    win = [v for (t, v) in ser if t >= tcut - 1e-12]
    n = len(win)
    if n < PLATEAU_MIN_SAMPLES:      # Amendment 4 item 2
        refuse("%s: %d plateau samples in the final %.0f%% window < %d -- CANNOT_TELL, "
               "never a pass (Amendment 4 item 2)" % (label, n, WINDOW_FRAC * 100, PLATEAU_MIN_SAMPLES))
    if whole_range < PLATEAU_NULL_RANGE:   # Amendment 4 item 4
        refuse("%s: the %s series spanned only %.6e over the whole run -- it never "
               "resolvably moved; a dead field and a converged one are identical to a "
               "tolerance; CANNOT_TELL, never a pass (Amendment 4 item 4)" % (label, label, whole_range))
    mean = sum(win) / n
    ptp = max(win) - min(win)
    ptp_frac = ptp / whole_range
    var = sum((x - mean) ** 2 for x in win) / n
    cov = math.sqrt(var) / abs(mean) if mean != 0 else float("inf")
    plateaued = bool(ptp_frac <= PLATEAU_PTP_FRAC_OF_RANGE and cov <= PLATEAU_COV)
    return dict(mean=mean, ptp=ptp, whole_range=whole_range, ptp_frac=ptp_frac,
                cov=cov, n_window=n, plateaued=plateaued)


def check_completion(level_dir):
    """Strict completion for a TRANSIENT adaptive-step rhoCentralFoam run (rule 4,
    the VMFL045 departure form): rc/End line, age guard, and last written time
    within ENDTIME_ATOL of the registered endTime (an adaptive step can never land
    exactly on endTime)."""
    logs = glob.glob(os.path.join(level_dir, "log.rhoCentralFoam"))
    if not logs:
        refuse("no log.rhoCentralFoam in " + level_dir)
    txt = open(logs[0], errors="replace").read()
    if not re.search(r"^End\b", txt, re.M):
        refuse("no End line in solver log: " + level_dir)
    u0 = os.path.join(level_dir, "0", "U")
    if not os.path.exists(u0):
        refuse("no 0/U launch marker (age guard): " + level_dir)
    times = [d for d in os.listdir(level_dir)
             if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and float(d) > 0]
    if not times:
        refuse("no written time > 0 (settled state not written): " + level_dir)
    latest = max(times, key=float)
    if abs(float(latest) - ENDTIME_PHYS) > ENDTIME_ATOL:
        refuse("last written time %s is not within %.1e of endTime %g -- the run did "
               "NOT reach the registered settling time (likely capped): %s"
               % (latest, ENDTIME_ATOL, ENDTIME_PHYS, level_dir))
    uf = os.path.join(level_dir, latest, "U")
    if not os.path.exists(uf):
        refuse("no U at latestTime %s: %s" % (latest, level_dir))
    if os.path.getmtime(uf) <= os.path.getmtime(u0):
        refuse("age guard: U at %s not newer than 0/U in %s" % (latest, level_dir))
    return latest


def planted_zero_control(level_dir, col):
    src = _coeff_dat(level_dir)
    ps_before = plateau_stat(src, col, "plant-before")
    before = ps_before["mean"]
    n_win = ps_before["n_window"]
    tmp = tempfile.mkdtemp(prefix="vmfl017r2plant_")
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
        after = plateau_stat(work, col, "plant-after")["mean"]
        moved = (after - before) * n_win  # only the last row was perturbed
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
    def chk(n, c, detail=""):
        nonlocal ok
        print(("  PASS " if c else "  FAIL ") + n + ("" if not detail else "  <- " + str(detail)))
        ok = ok and bool(c)

    def refuses(fn):
        pid = os.fork()
        if pid == 0:
            os.dup2(os.open(os.devnull, os.O_WRONLY), 2)
            try: fn()
            except SystemExit as e: os._exit(e.code if isinstance(e.code, int) else 1)
            os._exit(0)
        _, st = os.waitpid(pid, 0)
        return os.WIFEXITED(st) and os.WEXITSTATUS(st) == 2

    print("VMFL017-R2 comparator --selftest (NO run data touched)")
    chk("reference kind measured/experimental; team ceiling GATE REACHED", True)

    tmp = tempfile.mkdtemp(prefix="vmfl017r2self_")
    try:
        # settled: coefficient damps from a large early swing to a tight window
        d = os.path.join(tmp, "postProcessing", "forceCoeffs1", "0")
        os.makedirs(d)
        cdp = os.path.join(d, "coefficient.dat")
        with open(cdp, "w") as fh:
            fh.write("# Time\tCd\tCd(f)\tCd(r)\tCl\n")
            N = 100
            for k in range(N):
                t = ENDTIME_PHYS * (k + 1) / N
                # early: swings widely; late: settles tightly near 0.0180 / 0.800
                damp = math.exp(-8.0 * (k / N))
                cd = 0.0180 + 0.02 * damp * math.sin(6.0 * k) + 1e-6 * ((k % 2) * 2 - 1)
                cl = 0.800 + 0.30 * damp * math.sin(6.0 * k) + 1e-5 * ((k % 2) * 2 - 1)
                fh.write("%r\t%r\t0\t0\t%r\n" % (t, cd, cl))
        pcd = plateau_stat(cdp, COL_CD, "Cd")
        pcl = plateau_stat(cdp, COL_CL, "Cl")
        chk("Cd reader ~0.0180 over settled window", abs(pcd["mean"] - 0.0180) < 5e-4, pcd["mean"])
        chk("Cl reader ~0.800 over settled window", abs(pcl["mean"] - 0.800) < 5e-3, pcl["mean"])
        chk("settled Cd window -> PLATEAU", pcd["plateaued"], (pcd["ptp_frac"], pcd["cov"]))
        chk("plant seen (Cd)", planted_zero_control(tmp, COL_CD))

        print("  --- Amendment 4: ptp/range REJECTS an unsettled (drifting) series ---")
        d2 = os.path.join(tmp, "drift", "postProcessing", "forceCoeffs1", "0")
        os.makedirs(d2)
        cdp2 = os.path.join(d2, "coefficient.dat")
        with open(cdp2, "w") as fh:
            fh.write("# Time\tCd\tCd(f)\tCd(r)\tCl\n")
            N = 100
            for k in range(N):
                t = ENDTIME_PHYS * (k + 1) / N
                cd = 0.0180 + 0.004 * (k / N)   # still drifting UP the whole run
                fh.write("%r\t%r\t0\t0\t0.8\n" % (t, cd))
        pdrift = plateau_stat(cdp2, COL_CD, "Cd-drift")
        chk("drifting Cd -> NOT plateaued (ptp/range catches it)", not pdrift["plateaued"], pdrift["ptp_frac"])
        chk("drifting Cd final-window CoV is SMALL (the trap CoV alone misses)",
            pdrift["cov"] < PLATEAU_COV, pdrift["cov"])

        print("  --- Amendment 4: minimum-sample and null-range REFUSALS ---")
        d3 = os.path.join(tmp, "few", "postProcessing", "forceCoeffs1", "0")
        os.makedirs(d3)
        with open(os.path.join(d3, "coefficient.dat"), "w") as fh:
            fh.write("# Time\tCd\tCd(f)\tCd(r)\tCl\n")
            for k in range(10):    # 10 rows, window 20% = 2 < 20
                fh.write("%r\t0.018\t0\t0\t0.8\n" % (ENDTIME_PHYS * (k + 1) / 10))
        chk("<%d window samples REFUSED (CANNOT_TELL)" % PLATEAU_MIN_SAMPLES,
            refuses(lambda: plateau_stat(os.path.join(d3, "coefficient.dat"), COL_CD, "few")))
        d4 = os.path.join(tmp, "flat", "postProcessing", "forceCoeffs1", "0")
        os.makedirs(d4)
        with open(os.path.join(d4, "coefficient.dat"), "w") as fh:
            fh.write("# Time\tCd\tCd(f)\tCd(r)\tCl\n")
            for k in range(100):   # dead flat -> null range
                fh.write("%r\t0.018\t0\t0\t0.8\n" % (ENDTIME_PHYS * (k + 1) / 100))
        chk("null-range dead-flat series REFUSED (CANNOT_TELL)",
            refuses(lambda: plateau_stat(os.path.join(d4, "coefficient.dat"), COL_CD, "flat")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("  --- Roache classifier ---")
    chk("CONVERGING triple", roache([0.030, 0.020, 0.017])["triple"] == "CONVERGING")
    chk("DIVERGENT triple flagged", roache([0.017, 0.020, 0.030])["triple"] == "DIVERGENT")
    chk("OSCILLATORY triple flagged", roache([0.020, 0.017, 0.020])["triple"] == "OSCILLATORY")

    print("  --- gate can pass and can fail ---")
    chk("Cd +8%% inside 10%% band", abs((REF_CD * 1.08) - REF_CD) / REF_CD <= TOL_CD)
    chk("Cd +12%% outside 10%% band", abs((REF_CD * 1.12) - REF_CD) / REF_CD > TOL_CD)
    chk("Cl +6%% outside 5%% band", abs((REF_CL * 1.06) - REF_CL) / REF_CL > TOL_CL)

    print("SELFTEST", "OK" if ok else "FAILED"); sys.exit(0 if ok else 1)


def grade(run_root):
    present = [l for l in LEVELS if os.path.isdir(os.path.join(run_root, l))]
    if not present:
        refuse("no level dirs under " + run_root)
    cds, cls, per = [], [], {}
    for lvl in present:
        d = os.path.join(run_root, lvl)
        check_completion(d)
        cdat = _coeff_dat(d)
        pcd = plateau_stat(cdat, COL_CD, "%s/Cd" % lvl)
        pcl = plateau_stat(cdat, COL_CL, "%s/Cl" % lvl)
        for col, name in ((COL_CD, "Cd"), (COL_CL, "Cl")):
            if not planted_zero_control(d, col):
                refuse("planted-zero control did not fire for %s in %s" % (name, d))
        per[lvl] = dict(Cd=pcd, Cl=pcl)
        if not (pcd["plateaued"] and pcl["plateaued"]):
            print("VMFL017-R2  NOT A RESULT  %s not plateaued (Cd ptp/range=%.2f%% CoV=%.2f%% | "
                  "Cl ptp/range=%.2f%% CoV=%.2f%%) (Amendment 4; rule 5, L1)"
                  % (lvl, pcd["ptp_frac"] * 100, pcd["cov"] * 100, pcl["ptp_frac"] * 100, pcl["cov"] * 100))
            _dump(run_root, "NOT A RESULT", per, None, None)
            return
        cds.append(pcd["mean"]); cls.append(pcl["mean"])

    print("VMFL017-R2  levels=%s" % list(present))
    print("  Cd=%s  ref=%.4f  (n_window=%s)" % (["%.5f" % v for v in cds], REF_CD,
          [per[l]["Cd"]["n_window"] for l in present]))
    print("  Cl=%s  ref=%.4f" % (["%.4f" % v for v in cls], REF_CL))

    if len(present) < 3:
        print("  SINGLE/PARTIAL GRID (%d of 3 levels): no Roache triple, verdict is single-grid; "
              "family PENDING for GCI." % len(present))
        _dump(run_root, "PENDING", per, None, None)
        return

    rcd, rcl = roache(cds), roache(cls)
    cdf, clf = cds[-1], cls[-1]
    if rcd["triple"] != "CONVERGING" or rcl["triple"] != "CONVERGING":
        print("  NOT A RESULT  Cd triple=%s  Cl triple=%s  (rule 5)" % (rcd["triple"], rcl["triple"]))
        _dump(run_root, "NOT A RESULT", per, rcd, rcl)
        return
    rel_cd = abs(cdf - REF_CD) / REF_CD
    rel_cl = abs(clf - REF_CL) / REF_CL
    passed = rel_cd <= TOL_CD and rel_cl <= TOL_CL
    # team ceiling is GATE REACHED (Sanaa); a met gate on a measured reference is
    # reported as GATE REACHED, a missed gate as GATE FAIL.
    verdict = "GATE REACHED" if passed else "GATE FAIL"
    assert verdict in VERDICTS
    print("  %s  Cd=%.5f rel=%.2f%% tol=%.0f%% GCI=%.3g%% p=%.2f | Cl=%.4f rel=%.2f%% tol=%.0f%% GCI=%.3g%% p=%.2f"
          % (verdict, cdf, 100 * rel_cd, 100 * TOL_CD, 100 * rcd["gci"], rcd["p"],
             clf, 100 * rel_cl, 100 * TOL_CL, 100 * rcl["gci"], rcl["p"]))
    print("  (context only, never the gate: Ansys Fluent Cd=%.4f Cl=%.3f)" % (ANSYS_CD, ANSYS_CL))
    _dump(run_root, verdict, per, rcd, rcl)


def _dump(run_root, verdict, per, rcd, rcl):
    out = os.path.join(run_root, "GRADING_VMFL017_R2.json")
    try:
        with open(out, "w") as fh:
            json.dump(dict(case="VMFL017-R2", verdict=verdict, per_level=per,
                           roache_Cd=rcd, roache_Cl=rcl, ref=dict(Cd=REF_CD, Cl=REF_CL),
                           tol=dict(Cd=TOL_CD, Cl=TOL_CL), endTime=ENDTIME_PHYS),
                      fh, indent=2, sort_keys=True, default=str)
    except OSError:
        pass


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
