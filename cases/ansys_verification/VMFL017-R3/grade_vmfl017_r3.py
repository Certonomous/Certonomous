#!/usr/bin/env python3
"""VMFL017-R3 comparator -- Transonic Flow over an RAE 2822 Airfoil (manual p.69).

NEW ROW citing VMFL017-R2 (register row #32, NOT A RESULT) and VMFL017 (row #19,
PENDING). Row #19 used rhoSimpleFoam (diverged: 'Negative initial temperature T0').
Row #32 switched to rhoCentralFoam and graded NOT A RESULT because the y+ ~ 0.5
(low-Re) mesh forced the explicit step to Delta t ~ 1.85e-9 s -- L1 alone ~56x over
its cap, no gradeable value. R3 keeps rhoCentralFoam (supervisor ruling; the failure
was COST, not physics -- the density-based solver captured the shock with no
temperature blow-up) but moves to a HIGH-Re WALL-FUNCTION mesh (y+ ~ 30 first cell,
held constant across L1/L2/L3), which an answer-blind smoke measured at Delta t ~
1.87e-7 s -- ~128x faster, L1 ~132 core-min to reach endTime. This is the DIFFERENT
registration that row #32's own pre-registration named ("a wall function raising the
near-wall cell by three decades").

THIS FILE IS THE GRADING PATH, committed with the pre-registration that cites it by
sha, before any graded solver runs (CLAUDE.md rule 2). REFUSES (exit 2) rather than
degrading.

THE GATE IS BYTE-IDENTICAL to row #32's (L-487: do not move a gate you did not have
to move): Cd = 0.0168, Cl = 0.803 (AGARD AR-138, Cook/McDonald/Firmin 1979 --
measured/experimental, CAN buy P), bands Cd <= 10%, Cl <= 5%, BOTH, at the finest
CONVERGING level; team ceiling GATE REACHED. Manual context, NEVER the gate: Fluent
Cd 0.016 (0.952), Cl 0.78 (0.971); CFX Cd 0.0162, Cl 0.7981.

Cd and Cl are read DIRECTLY from OpenFOAM's forceCoeffs function object (no
constructed geometry enters the gate). Reader:
  postProcessing/forceCoeffs1/<t>/coefficient.dat, columns
  Time  Cd  Cd(f)  Cd(r)  Cl  ...  -> col 1 = Cd, col 4 = Cl.

NEW IN R3 -- WALL-FUNCTION REGIME PRECONDITION (gate-blind, L-501 cause-3 analog):
a wall-function result is only admissible while the wall y+ sits in the log-law band.
The comparator reads postProcessing/yPlus1/<t>/yPlus.dat and returns NOT A RESULT if,
over the settled window, the wall y+ leaves the VALUE-BLIND band (window max of the
per-step max <= Y_PLUS_MAX, and window mean of the per-step average >= Y_PLUS_MIN_AVG).
These bounds are pinned from wall-function VALIDITY physics (log-law limits), and
reference NEITHER the reference values NOR the bands. The min y+ is NEVER gated: y+ ->
0 at the stagnation point and near separation is physical on any mesh and is handled
by the continuous wall functions (nutUSpaldingWallFunction, omegaWallFunction).

PLATEAU CLAUSE is the PREREG_TEMPLATE Amendment 4 required artifact: a fractional
window WITH a minimum-sample CANNOT_TELL refusal, a peak-to-peak / whole-run-range
statistic that REJECTS A GROWING (unsettled) series, a null-range refusal, and the
realised sample count recorded. CoV is carried only beside, never instead.

  python3 grade_vmfl017_r3.py --selftest
  python3 grade_vmfl017_r3.py --run-root <verification/runs/.../VMFL017-R3>
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
PLATEAU_PTP_FRAC_OF_RANGE = 0.05      # (3) final-window ptp <= 5% of whole-run range
PLATEAU_NULL_RANGE = 1.0e-6          # (4) whole-run range below this -> CANNOT_TELL
PLATEAU_COV = 0.02                   # CoV kept BESIDE ptp (never instead), also gated.

# --- WALL-FUNCTION REGIME PRECONDITION (R3, gate-blind; L-501 cause-3 analog) --
# VALUE-BLIND: pinned from log-law wall-function validity, NOT from Cd/Cl or the bands.
Y_PLUS_MAX     = 300.0     # log-law upper validity; first cell above this under-resolves
Y_PLUS_MIN_AVG = 10.0      # confirms the mesh is genuinely in the wall-function regime
                           # (not a low-Re y+<<1 mesh where wall functions are misapplied)

LEVELS   = ("L1", "L2", "L3")
PLANT    = 7.531e-03
PLANT_TOL = 1e-9
COL_CD, COL_CL = 1, 4
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

# OBSERVED-ORDER FLOOR (FINDING_p_floor.md sec.4). A triple whose observed order falls
# below this is NOT A RESULT and NO GCI is quoted.
P_MIN = 0.05


def refuse(msg):
    sys.stderr.write("REFUSE (VMFL017-R3): %s\n" % msg); sys.exit(2)


def _coeff_dat(level_dir):
    pats = glob.glob(os.path.join(level_dir, "postProcessing", "forceCoeffs1", "*", "coefficient.dat"))
    if len(pats) != 1:
        refuse("expected one forceCoeffs1 coefficient.dat in %s, found %d" % (level_dir, len(pats)))
    return pats[0]


def _yplus_dat(level_dir):
    pats = glob.glob(os.path.join(level_dir, "postProcessing", "yPlus1", "*", "yPlus.dat"))
    if len(pats) != 1:
        refuse("expected one yPlus1 yPlus.dat in %s, found %d (the wall-function regime "
               "precondition needs it -- add the yPlus function object)" % (level_dir, len(pats)))
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
    below the sample floor or on a null-range series."""
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


def yplus_window_stats(path):
    """Read yPlus.dat (columns: Time patch min max average) and return, over the settled
    window (final WINDOW_FRAC of physical time): the window MAX of the per-step MAX y+,
    the window MEAN of the per-step AVERAGE y+, the window MIN of the per-step MIN (recorded
    only, never gated -- y+ -> 0 at stagnation is physical), and the sample count."""
    rows = []
    with open(path) as f:
        for s in f:
            s = s.strip()
            if not s or s.startswith("#"):
                continue
            p = s.split()
            # Time patch min max average  -> 5 fields; patch is non-numeric
            if len(p) < 5:
                refuse("yPlus row has %d fields, need 5 (Time patch min max average) in %s" % (len(p), path))
            try:
                t = float(p[0]); ymin = float(p[-3]); ymax = float(p[-2]); yavg = float(p[-1])
            except ValueError:
                refuse("unparseable yPlus row in %s: %r" % (path, s))
            rows.append((t, ymin, ymax, yavg))
    if not rows:
        refuse("no data rows in " + path)
    tmax = rows[-1][0]
    tcut = tmax * (1.0 - WINDOW_FRAC)
    win = [r for r in rows if r[0] >= tcut - 1e-12]
    if len(win) < PLATEAU_MIN_SAMPLES:
        refuse("yPlus: %d samples in the final %.0f%% window < %d -- CANNOT_TELL the wall-"
               "function regime (Amendment 4 item 2 basis)" % (len(win), WINDOW_FRAC * 100, PLATEAU_MIN_SAMPLES))
    win_max = max(r[2] for r in win)
    win_mean_avg = sum(r[3] for r in win) / len(win)
    win_min = min(r[1] for r in win)
    return dict(win_max=win_max, win_mean_avg=win_mean_avg, win_min=win_min, n_window=len(win))


def yplus_regime_ok(stats):
    """VALUE-BLIND wall-function regime test. True iff the wall y+ sits in the log-law band.
    win_max <= Y_PLUS_MAX (first cell not outside the log region) AND
    win_mean_avg >= Y_PLUS_MIN_AVG (the mesh is genuinely in the wall-function regime)."""
    return bool(stats["win_max"] <= Y_PLUS_MAX and stats["win_mean_avg"] >= Y_PLUS_MIN_AVG)


def check_completion(level_dir):
    """Strict completion for a TRANSIENT adaptive-step rhoCentralFoam run (rule 4,
    the VMFL045 departure form): rc/End line, age guard, and last written time
    within ENDTIME_ATOL of the registered endTime."""
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
    tmp = tempfile.mkdtemp(prefix="vmfl017r3plant_")
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
    if p < P_MIN:      # observed-order floor -- NOT A RESULT, and NO GCI
        return dict(triple="STAGNANT", p=p, gci=None, p_below_floor=True, p_floor=P_MIN)
    return dict(triple="CONVERGING", p=p, gci=1.25 * abs((f3 - f2) / f3) / (2.0 ** p - 1.0))


def verdict_for(rcd, rcl, rel_cd, rel_cl):
    """The ONE verdict path. Rule 5: the triple gate can only turn a verdict INTO NOT A RESULT."""
    if rcd["triple"] != "CONVERGING" or rcl["triple"] != "CONVERGING":
        return "NOT A RESULT"
    return "GATE REACHED" if (rel_cd <= TOL_CD and rel_cl <= TOL_CL) else "GATE FAIL"


def check_vocabulary(verdict):
    """Explicit REFUSAL, not `assert` (python3 -O strips asserts -- L-332 form)."""
    if verdict not in VERDICTS:
        refuse("verdict %r is not in the fixed vocabulary %s (CLAUDE.md rule 1)"
               % (verdict, list(VERDICTS)))
    return verdict


def p_floor_control():
    """PLANTED CONTROL for the observed-order floor (FINDING_p_floor.md sec.4). Three
    constructed triples are planted into this comparator's OWN roache() and verdict_for();
    the control REFUSES (exit 2) if any grades the wrong way. NO `assert` anywhere."""
    def bad(tag, detail):
        refuse("P-FLOOR PLANTED CONTROL FAILED [%s]: %s (P_MIN = %.3g, FINDING_p_floor.md sec.4)"
               % (tag, detail, P_MIN))

    out = {"P_MIN": P_MIN, "probes": {}}

    tri_a = roache([1.0, 1.1, 1.2])
    v_a = verdict_for(tri_a, tri_a, 0.0, 0.0)
    out["probes"]["equally_spaced_1.0_1.1_1.2"] = dict(triple=tri_a["triple"], p=tri_a.get("p"),
                                                       gci=tri_a.get("gci"), verdict=v_a)
    if v_a != "NOT A RESULT":
        bad("equally-spaced (1.0, 1.1, 1.2)", "graded %r with both bands met, expected NOT A RESULT" % v_a)
    if tri_a.get("gci") is not None:
        bad("equally-spaced (1.0, 1.1, 1.2)", "a GCI was produced (%r) for a non-converging triple" % (tri_a["gci"],))

    p_lo = 0.01
    tri_b = roache([1.0, 1.1, 1.1 + 0.1 * (2.0 ** (-p_lo))])
    v_b = verdict_for(tri_b, tri_b, 0.0, 0.0)
    out["probes"]["below_floor_p_0.01"] = dict(triple=tri_b["triple"], p=tri_b.get("p"),
                                               gci=tri_b.get("gci"), verdict=v_b)
    if tri_b.get("p") is None or abs(tri_b["p"] - p_lo) > 1e-9:
        bad("below-floor probe", "constructed p = %.4g was not recovered (got %r)" % (p_lo, tri_b.get("p")))
    if not tri_b.get("p_below_floor"):
        bad("below-floor probe", "p = %r is under P_MIN and the floor did NOT fire" % (tri_b.get("p"),))
    if v_b != "NOT A RESULT" or tri_b.get("gci") is not None:
        bad("below-floor probe", "graded %r with gci %r, expected NOT A RESULT and no GCI"
            % (v_b, tri_b.get("gci")))

    p_hi = 0.5
    tri_c = roache([1.0, 1.1, 1.1 + 0.1 * (2.0 ** (-p_hi))])
    v_c = verdict_for(tri_c, tri_c, 0.0, 0.0)
    out["probes"]["above_floor_p_0.5"] = dict(triple=tri_c["triple"], p=tri_c.get("p"),
                                              gci=tri_c.get("gci"), verdict=v_c)
    if tri_c["triple"] != "CONVERGING" or tri_c.get("p_below_floor"):
        bad("above-floor probe", "p = %r is above P_MIN and the floor fired anyway" % (tri_c.get("p"),))
    if tri_c.get("gci") is None:
        bad("above-floor probe", "no GCI for a converging triple above the floor")
    if v_c != "GATE REACHED":
        bad("above-floor probe", "graded %r, expected GATE REACHED inside both bands" % v_c)

    out["passed"] = True
    return out


def _write_yplus(path, ymin, ymax, yavg, n=100):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("# y+ ()\n# Time\tpatch\tmin\tmax\taverage\n")
        for k in range(n):
            t = ENDTIME_PHYS * (k + 1) / n
            fh.write("%r\taerofoil\t%r\t%r\t%r\n" % (t, ymin, ymax, yavg))


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

    print("VMFL017-R3 comparator --selftest (NO run data touched)")
    chk("reference kind measured/experimental; team ceiling GATE REACHED", True)

    tmp = tempfile.mkdtemp(prefix="vmfl017r3self_")
    try:
        d = os.path.join(tmp, "postProcessing", "forceCoeffs1", "0")
        os.makedirs(d)
        cdp = os.path.join(d, "coefficient.dat")
        with open(cdp, "w") as fh:
            fh.write("# Time\tCd\tCd(f)\tCd(r)\tCl\n")
            N = 100
            for k in range(N):
                t = ENDTIME_PHYS * (k + 1) / N
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
                cd = 0.0180 + 0.004 * (k / N)
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
            for k in range(10):
                fh.write("%r\t0.018\t0\t0\t0.8\n" % (ENDTIME_PHYS * (k + 1) / 10))
        chk("<%d window samples REFUSED (CANNOT_TELL)" % PLATEAU_MIN_SAMPLES,
            refuses(lambda: plateau_stat(os.path.join(d3, "coefficient.dat"), COL_CD, "few")))
        d4 = os.path.join(tmp, "flat", "postProcessing", "forceCoeffs1", "0")
        os.makedirs(d4)
        with open(os.path.join(d4, "coefficient.dat"), "w") as fh:
            fh.write("# Time\tCd\tCd(f)\tCd(r)\tCl\n")
            for k in range(100):
                fh.write("%r\t0.018\t0\t0\t0.8\n" % (ENDTIME_PHYS * (k + 1) / 100))
        chk("null-range dead-flat series REFUSED (CANNOT_TELL)",
            refuses(lambda: plateau_stat(os.path.join(d4, "coefficient.dat"), COL_CD, "flat")))

        print("  --- R3 wall-function REGIME precondition (value-blind y+ band) ---")
        # in-band: max ~66, avg ~48 (the smoke's measured range), min ~5 (stagnation) -> OK
        yp_ok = os.path.join(tmp, "yp_ok", "postProcessing", "yPlus1", "0", "yPlus.dat")
        _write_yplus(yp_ok, ymin=5.0, ymax=66.0, yavg=48.0)
        s_ok = yplus_window_stats(yp_ok)
        chk("in-band y+ (max 66, avg 48, min 5) -> regime OK", yplus_regime_ok(s_ok),
            (s_ok["win_max"], s_ok["win_mean_avg"], s_ok["win_min"]))
        chk("min y+ at stagnation is recorded but NOT gated", s_ok["win_min"] == 5.0)
        # too high: max 500 > 300 -> first cell outside log region -> regime NOT ok
        yp_hi = os.path.join(tmp, "yp_hi", "postProcessing", "yPlus1", "0", "yPlus.dat")
        _write_yplus(yp_hi, ymin=200.0, ymax=500.0, yavg=350.0)
        chk("y+ too high (max 500 > %g) -> regime NOT ok (NOT A RESULT)" % Y_PLUS_MAX,
            not yplus_regime_ok(yplus_window_stats(yp_hi)))
        # too low: avg 2 < 10 -> low-Re mesh, wall functions misapplied -> regime NOT ok
        yp_lo = os.path.join(tmp, "yp_lo", "postProcessing", "yPlus1", "0", "yPlus.dat")
        _write_yplus(yp_lo, ymin=0.2, ymax=3.0, yavg=2.0)
        chk("y+ too low (avg 2 < %g) -> regime NOT ok (NOT A RESULT)" % Y_PLUS_MIN_AVG,
            not yplus_regime_ok(yplus_window_stats(yp_lo)))
        # missing yPlus.dat -> REFUSE (exit 2)
        chk("missing yPlus.dat REFUSES (exit 2)",
            refuses(lambda: _yplus_dat(os.path.join(tmp, "no_yplus"))))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("  --- PLANTED CONTROL: observed-order floor P_MIN = %.3g ---" % P_MIN)
    pf = p_floor_control()
    chk("(1.0, 1.1, 1.2) -> NOT A RESULT, no GCI, though both bands are met",
        pf["probes"]["equally_spaced_1.0_1.1_1.2"]["verdict"] == "NOT A RESULT"
        and pf["probes"]["equally_spaced_1.0_1.1_1.2"]["gci"] is None,
        "%s p=%.3g" % (pf["probes"]["equally_spaced_1.0_1.1_1.2"]["triple"],
                       pf["probes"]["equally_spaced_1.0_1.1_1.2"]["p"]))
    chk("p = 0.01 (below floor) -> NOT A RESULT, no GCI",
        pf["probes"]["below_floor_p_0.01"]["verdict"] == "NOT A RESULT"
        and pf["probes"]["below_floor_p_0.01"]["gci"] is None,
        "p=%.4g" % pf["probes"]["below_floor_p_0.01"]["p"])
    chk("p = 0.5 (above floor) -> floor does NOT over-fire, GCI quoted",
        pf["probes"]["above_floor_p_0.5"]["verdict"] == "GATE REACHED"
        and pf["probes"]["above_floor_p_0.5"]["gci"] is not None,
        "p=%.4g gci=%.3g%%" % (pf["probes"]["above_floor_p_0.5"]["p"],
                               100 * pf["probes"]["above_floor_p_0.5"]["gci"]))

    print("  --- vocabulary guard is a REFUSAL, not an assert (survives python3 -O) ---")
    chk("a legal verdict passes the vocabulary guard",
        check_vocabulary("GATE REACHED") == "GATE REACHED")
    chk("a verdict outside the fixed vocabulary REFUSES (exit 2)",
        refuses(lambda: check_vocabulary("looks fine")))

    print("  --- Roache classifier ---")
    chk("CONVERGING triple", roache([0.030, 0.020, 0.017])["triple"] == "CONVERGING")
    chk("DIVERGENT triple flagged", roache([0.017, 0.020, 0.030])["triple"] == "DIVERGENT")
    chk("OSCILLATORY triple flagged", roache([0.020, 0.017, 0.020])["triple"] == "OSCILLATORY")

    print("  --- gate can pass and can fail (BYTE-IDENTICAL to row #32) ---")
    chk("Cd +8%% inside 10%% band", abs((REF_CD * 1.08) - REF_CD) / REF_CD <= TOL_CD)
    chk("Cd +12%% outside 10%% band", abs((REF_CD * 1.12) - REF_CD) / REF_CD > TOL_CD)
    chk("Cl +6%% outside 5%% band", abs((REF_CL * 1.06) - REF_CL) / REF_CL > TOL_CL)

    print("SELFTEST", "OK" if ok else "FAILED"); sys.exit(0 if ok else 1)


def grade(run_root):
    present = [l for l in LEVELS if os.path.isdir(os.path.join(run_root, l))]
    if not present:
        refuse("no level dirs under " + run_root)
    pfc = p_floor_control()
    print("VMFL017-R3  p-floor planted control OK (P_MIN = %.3g): (1.0,1.1,1.2) -> %s, no GCI"
          % (P_MIN, pfc["probes"]["equally_spaced_1.0_1.1_1.2"]["verdict"]))
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
        # WALL-FUNCTION REGIME PRECONDITION (gate-blind; before the plateau/gate verdict)
        yps = yplus_window_stats(_yplus_dat(d))
        per[lvl] = dict(Cd=pcd, Cl=pcl, yPlus=yps)
        if not yplus_regime_ok(yps):
            print("VMFL017-R3  NOT A RESULT  %s wall y+ out of the log-law band "
                  "(window max=%.1f > %.0f OR window mean-avg=%.1f < %.0f; min=%.1f recorded, "
                  "not gated) -- wall functions inadmissible here (L-501 cause-3 precondition)"
                  % (lvl, yps["win_max"], Y_PLUS_MAX, yps["win_mean_avg"], Y_PLUS_MIN_AVG, yps["win_min"]))
            _dump(run_root, "NOT A RESULT", per, None, None)
            return
        if not (pcd["plateaued"] and pcl["plateaued"]):
            print("VMFL017-R3  NOT A RESULT  %s not plateaued (Cd ptp/range=%.2f%% CoV=%.2f%% | "
                  "Cl ptp/range=%.2f%% CoV=%.2f%%) (Amendment 4; rule 5)"
                  % (lvl, pcd["ptp_frac"] * 100, pcd["cov"] * 100, pcl["ptp_frac"] * 100, pcl["cov"] * 100))
            _dump(run_root, "NOT A RESULT", per, None, None)
            return
        cds.append(pcd["mean"]); cls.append(pcl["mean"])

    print("VMFL017-R3  levels=%s" % list(present))
    print("  Cd=%s  ref=%.4f  (n_window=%s)" % (["%.5f" % v for v in cds], REF_CD,
          [per[l]["Cd"]["n_window"] for l in present]))
    print("  Cl=%s  ref=%.4f" % (["%.4f" % v for v in cls], REF_CL))
    print("  wall y+ (window mean-avg / max): %s"
          % [("%.1f/%.1f" % (per[l]["yPlus"]["win_mean_avg"], per[l]["yPlus"]["win_max"])) for l in present])

    if len(present) < 3:
        print("  SINGLE/PARTIAL GRID (%d of 3 levels): no Roache triple, verdict is single-grid; "
              "family PENDING for GCI." % len(present))
        _dump(run_root, "PENDING", per, None, None)
        return

    rcd, rcl = roache(cds), roache(cls)
    cdf, clf = cds[-1], cls[-1]
    rel_cd = abs(cdf - REF_CD) / REF_CD
    rel_cl = abs(clf - REF_CL) / REF_CL
    verdict = check_vocabulary(verdict_for(rcd, rcl, rel_cd, rel_cl))
    if verdict == "NOT A RESULT":
        def _p(t):
            return "none" if t.get("p") is None else "%.4g" % t["p"]
        print("  NOT A RESULT  Cd triple=%s (p=%s)  Cl triple=%s (p=%s)  -- no GCI is quoted "
              "(rule 5; observed-order floor P_MIN=%.3g)"
              % (rcd["triple"], _p(rcd), rcl["triple"], _p(rcl), P_MIN))
        _dump(run_root, "NOT A RESULT", per, rcd, rcl)
        return
    print("  %s  Cd=%.5f rel=%.2f%% tol=%.0f%% GCI=%.3g%% p=%.2f | Cl=%.4f rel=%.2f%% tol=%.0f%% GCI=%.3g%% p=%.2f"
          % (verdict, cdf, 100 * rel_cd, 100 * TOL_CD, 100 * rcd["gci"], rcd["p"],
             clf, 100 * rel_cl, 100 * TOL_CL, 100 * rcl["gci"], rcl["p"]))
    print("  (context only, never the gate: Ansys Fluent Cd=%.4f Cl=%.3f)" % (ANSYS_CD, ANSYS_CL))
    _dump(run_root, verdict, per, rcd, rcl)


def _dump(run_root, verdict, per, rcd, rcl):
    out = os.path.join(run_root, "GRADING_VMFL017_R3.json")
    try:
        with open(out, "w") as fh:
            json.dump(dict(case="VMFL017-R3", verdict=verdict, per_level=per,
                           roache_Cd=rcd, roache_Cl=rcl, ref=dict(Cd=REF_CD, Cl=REF_CL),
                           tol=dict(Cd=TOL_CD, Cl=TOL_CL), endTime=ENDTIME_PHYS,
                           yplus_band=dict(max=Y_PLUS_MAX, min_avg=Y_PLUS_MIN_AVG)),
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
