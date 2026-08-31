#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMFL006 -- Multicomponent Species Transport in Pipe Flow.
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 27-28.

GATE QUANTITY: the MIXING-CUP (mass-weighted) average of the NORMALIZED mass
fraction of species A,  theta = (Y_wall - Y)/(Y_wall - Y_inlet) = (0.9 - Y)/0.4,
at the ten axial stations x = 0.01 ... 0.10 m, read from the solver's own
conserved flux on real mesh faces (surfaceFieldValue, weightedAverage, weightField
phi) -- never interpolated onto a constructed plane and never area-averaged.

REFERENCE: the manual's Table .06.1 "Target" column (p.28), which cites
W.M. Kays & M.E. Crawford, "Convective Heat and Mass Transfer", 3rd Ed.,
McGraw-Hill, pp.126-134, 1993 -- the GRAETZ series. REFERENCE KIND: ANALYTICAL
(closed form). It buys V, never P, so the TIER CEILING is GATE REACHED and this
comparator hard-codes GATE REACHED as its in-band verdict. Ansys Fluent's own
column is CONTEXT ONLY and is never the gate.

WHICH QUANTITY THE MANUAL'S NUMBERS ACTUALLY ARE -- MEASURED, NOT ASSUMED.
The manual's table CAPTION says "Along the Axis"; the manual's own prose one line
above says "the value of species A is the mass-weighted average of the normalized
species mass fraction A at x-locations". Those are two different quantities. The
lab evaluated the Graetz series itself, twice, by two independent instruments,
and the printed targets are the MIXING-CUP MEAN to a worst 0.048 % and differ
from the true ON-AXIS value by up to 78.5 %. The prose is right and the caption
is wrong; the gate is therefore the mixing cup. Full record:
PREREGISTRATION.md sec.3.

TWO FIELD CLASSES (Sanaa's universal rule, 2026-08-26, commit d4d0c29d; L-342:
"a bookkeeping failure invalidates the bookkeeping, never the physics artifacts").

  PHYSICS-CRITICAL -- these decide the verdict and REFUSE (exit 2) when violated:
      solver rc (from RUN_RC.txt WHEN PRESENT; see below for absent),
      the End line, last time vs endTime, the fields present at endTime,
      the residual/convergence clause, the AGE GUARD, the mesh birth certificate,
      the mixing-cup and flux instruments themselves, the face counts,
      the planted-zero control, the Roache triple and the observed-order floor.
      RUN_RC.txt ABSENT is the one special case: the row becomes NOT A RESULT and
      every physics number is still PRINTED -- it is not a refusal that voids the
      solve, because a missing bookkeeping file is not a broken solve.

  INFRASTRUCTURE -- these are REPORTED and NEVER refuse, never void, never move a
  verdict:  COST.txt, LAUNCH_RECORD.txt, CONTENTION.txt, core-minute figures,
      wall seconds, timeout values, pids/sids, and any mtime used for bookkeeping
      rather than for the age guard. A missing or malformed infrastructure field
      prints "WARNING [INFRA] ..." and grading proceeds on the physics artefacts.

CONTROLS (CLAUDE.md rules 3, 4, 5):
  * planted-zero (rule 3) -- a known perturbation is planted into a COPY of the
    mixing-cup data file, read back FROM DISK by the SAME parser, and the control
    REFUSES (exit 2) from INSIDE itself if the reader cannot see it. Calibrated to
    the reader (L-340): the comparator's gate reader is a SINGLE-VALUE parser on
    one .dat row, so a single-value plant is undiluted and the reader delta equals
    the plant. There is no 1/sqrt(N) averaging step on the comparator side -- the
    mass-weighting happens inside the solver, before the file exists.
  * strict completion (rule 4) -- see completion(); REFUSES rather than grading a
    partial run.
  * convergence -- a FIXED 200-sample window on the solver's own solverInfo.dat,
    with a minimum-iteration refusal, a null-range refusal and a trend test
    (PREREG_TEMPLATE Amendment 4). No fractional window is used anywhere.
  * CONSERVATION / ORIENTATION control -- sum(phi) on every station must equal the
    FLAT-WEDGE analytic flow rate 0.5*sin(5 deg)*R^2*Uavg. A face oriented against
    the flow makes the weighted average silently wrong and this sum wrong with it.
  * Roache triple (rule 5) + OBSERVED-ORDER FLOOR P_MIN (FINDING_p_floor.md sec.4),
    both DRIVEN by planted controls, not merely declared.
  * INFRASTRUCTURE-TOLERANCE control -- a constructed run is graded twice, once
    intact and once with COST.txt deleted and LAUNCH_RECORD.txt corrupted, and the
    verdict must be IDENTICAL; a second plant breaks a PHYSICS field (the End line)
    and must still REFUSE. A rule that is only written down is not a rule.

NO `assert` CARRIES ANY GUARD, REFUSAL, CONTROL OR GATE (PREREG_TEMPLATE
Amendment 6): `python3 -O` strips asserts. Every refusal below is SystemExit2.

Verdict vocabulary only: PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
"""
import os, re, sys, json, math, shutil, tempfile

HERE     = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = os.path.join(HERE, "..", "..", "..",
                        "verification", "runs", "ansys_verification", "VMFL006")
LEVELS   = ["L1", "L2", "L3"]
NR_OF    = {"L1": 20, "L2": 40, "L3": 80}
NX_OF    = {"L1": 200, "L2": 400, "L3": 800}

STATIONS = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
# THE GATE: the manual's printed Target column (p.28, Table .06.1).
MANUAL   = [0.8225, 0.7308, 0.6593, 0.5992, 0.5469,
            0.5006, 0.4589, 0.4212, 0.3869, 0.3555]
# Ansys Fluent's own column (p.28) -- CONTEXT ONLY, never the gate.
FLUENT   = [0.8227, 0.7309, 0.6594, 0.5993, 0.5471,
            0.5007, 0.4591, 0.4215, 0.3872, 0.3557]
# The LAB's OWN evaluation of the Graetz series, by two independent instruments
# (graetz_reference_vmfl006.py). A STATED PREDICTION, printed beside the verdict,
# NEVER the gate -- the gate is the manual's Target column above.
LAB_SHOOT = [0.822181458, 0.730506204, 0.658996267, 0.598933758, 0.546700651,
             0.500361116, 0.458734367, 0.421037574, 0.386717905, 0.355363267]
LAB_FV    = [0.822181728, 0.730506637, 0.658996811, 0.598934385, 0.546701342,
             0.500361858, 0.458735148, 0.421038385, 0.386718738, 0.355364114]

Y_IN     = 0.5              # manual p.27
Y_WALL   = 0.9              # manual p.27
TOL      = 0.01             # FROZEN BAND, relative, EVERY station, at L3. sec.6.
PLANT    = 1.234e-03        # planted-zero perturbation
FS       = 1.25             # Roache safety factor
RATIO    = 2.0              # grid refinement ratio
P_MIN    = 0.05             # observed-order floor (FINDING_p_floor.md sec.4)
TRIPLE_I = 9                # the Roache triple is taken on station x = 0.10 m

ENDTIME_EXPECTED = 3000     # frozen iteration count; there is no residualControl
MIN_ITERS        = 1000     # fewer than this -> CANNOT_TELL, never a pass
PLATEAU_WINDOW   = 200      # FIXED window (never a fraction of the run)
RES_FLOOR        = 1.0e-09  # T_initial must be at or below this across the window

# Flat-sided 5 deg wedge: flow rate = 0.5*sin(5 deg)*R^2*Uavg. This is NOT the
# true circular-sector value pi*R^2*(5/360)*Uavg = 2.7270769562411397e-07 -- the
# two differ by exactly sin(t)/t, N-AV9's azimuthal area deficit of 0.1269 %.
WEDGE_FLUX     = 2.7236169608643178e-07
FLUX_REL_TOL   = 1.0e-06


# --- SCRATCH-PATH NORMALISATION -------------------------------------------
# The launcher gates on `cmp` between the python3 and python3 -O --selftest
# outputs: a control that vanishes under -O is not a control (L-332).  A
# RANDOMISED tempdir name breaks that gate for a reason that has nothing to do
# with an interpreter flag, which would make the gate abort at zero compute on a
# healthy instrument -- a false alarm is not a control either.  Every emitted
# message therefore has its scratch root replaced by a fixed token.
# THIS TOUCHES NO CONTROL, NO READER, NO THRESHOLD AND NO VERDICT: it changes
# only the TEXT that a human and the launcher's `cmp` read.
_SCRATCH_RE = re.compile(r"/tmp/(vmfl006_plant_|vmfl006_infra_|st006_)[A-Za-z0-9_]+")


def _norm(msg):
    return _SCRATCH_RE.sub(lambda m: "/tmp/%s<scratch>" % m.group(1), str(msg))


class SystemExit2(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSED (exit 2): %s\n" % _norm(msg))
        SystemExit.__init__(self, 2)


INFRA_WARNINGS = []


def infra_warn(msg):
    """INFRASTRUCTURE class (L-342). Reported, never fatal, never verdict-moving."""
    line = "WARNING [INFRA]: %s" % _norm(msg)
    INFRA_WARNINGS.append(line)
    print(line)


def theta_of(y):
    """Normalized mass fraction, the quantity the manual's table reports."""
    return (Y_WALL - y) / (Y_WALL - Y_IN)


# ----------------------------------------------------------------- readers ----
def read_sfv(path, want_op, want_field, want_region):
    """Parse ONE surfaceFieldValue .dat file.

    ANCHORED ON THE QUANTITY NAME, never on a shared token (PREREG_TEMPLATE
    Amendment 5 item 3): the header must name the operation, the field AND the
    region, and the data column is taken by NAME from the header, not by
    position and not by 'the last number on the line'.
    """
    if not os.path.exists(path):
        raise SystemExit2("missing instrument file %s" % path)
    lines = [l.rstrip("\n") for l in open(path).read().splitlines()]
    hdr = [l for l in lines if l.startswith("#")]
    dat = [l for l in lines if l and not l.startswith("#")]
    if not dat:
        raise SystemExit2("%s carries a header and NO data row" % path)
    region = None
    faces = None
    weight = None
    for h in hdr:
        m = re.search(r"Region type\s*:\s*(.+?)\s*$", h)
        if m:
            region = m.group(1).strip()
        m = re.search(r"Faces\s*:\s*(\d+)", h)
        if m:
            faces = int(m.group(1))
        m = re.search(r"Weight field\s*:\s*(\S+)", h)
        if m:
            weight = m.group(1).strip()
    if region is None or want_region not in region:
        raise SystemExit2("%s: region header is %r, expected to contain %r"
                          % (path, region, want_region))
    colhdr = [h for h in hdr if "Time" in h and "(" in h]
    if not colhdr:
        raise SystemExit2("%s: no column header naming the quantity" % path)
    cols = [c.strip() for c in colhdr[-1].lstrip("#").split("\t") if c.strip()]
    target = "%s(%s)" % (want_op, want_field)
    if target not in cols:
        raise SystemExit2("%s: column %r is not present; columns are %r"
                          % (path, target, cols))
    idx = cols.index(target)
    fields = [f for f in dat[-1].split("\t") if f.strip()]
    if idx >= len(fields):
        raise SystemExit2("%s: column %d (%s) missing from the last data row"
                          % (path, idx, target))
    return {"value": float(fields[idx]), "faces": faces, "region": region,
            "weight": weight, "n_rows": len(dat), "time": float(fields[0])}


def read_solver_info(level_dir):
    """The solver's OWN residual record, on disk, one row per iteration."""
    base = os.path.join(level_dir, "postProcessing", "residuals")
    if not os.path.isdir(base):
        raise SystemExit2("no postProcessing/residuals in %s -- convergence is "
                          "UNEVALUABLE, and an unevaluable convergence is not a pass"
                          % level_dir)
    cand = []
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d, "solverInfo.dat")
        if os.path.exists(p):
            cand.append(p)
    if not cand:
        raise SystemExit2("no solverInfo.dat under %s" % base)
    rows, cols = [], None
    for p in cand:
        for l in open(p).read().splitlines():
            if l.startswith("#"):
                if "T_initial" in l:
                    cols = [c.strip() for c in l.lstrip("#").split("\t") if c.strip()]
                continue
            f = [x for x in l.split("\t") if x.strip()]
            if f:
                rows.append(f)
    if cols is None or "T_initial" not in cols:
        raise SystemExit2("solverInfo.dat carries no T_initial column")
    i = cols.index("T_initial")
    out = []
    for f in rows:
        if i < len(f):
            try:
                out.append((float(f[0]), float(f[i])))
            except ValueError:
                pass
    if not out:
        raise SystemExit2("solverInfo.dat has no parseable T_initial rows")
    return out


# ---------------------------------------------------------- strict completion --
def completion(level_dir, level):
    """CLAUDE.md rule 4, in the form FROZEN in PREREGISTRATION.md sec.7.

    There is no residualControl in this case, so the literal clause applies:
    last time == endTime, exactly, on every level.  scalarTransportFoam does not
    print an `ExecutionTime` line, so the equivalent iteration-count clause is
    used and is DECLARED here rather than improvised: the number of `Time = `
    lines in the log must equal endTime.

    PHYSICS-CRITICAL, except where marked. Any failed clause REFUSES (exit 2)
    rather than grading a partial run -- with ONE exception required by L-342:
    a MISSING RUN_RC.txt returns rc_unknown, which forces NOT A RESULT while
    still printing every physics number, because a bookkeeping file that was
    never written does not un-run a solver.
    """
    out = {"rc_unknown": False}
    rcf = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.exists(rcf):
        out["rc"] = None
        out["rc_unknown"] = True
        infra_warn("no RUN_RC.txt in %s -- the SOLVER RC IS UNKNOWN. Under L-342 "
                   "this does not void the physics: the row is NOT A RESULT and every "
                   "physics number below is still printed." % level_dir)
    else:
        # Parse TOLERANTLY (PREREG_TEMPLATE Amendment 5 item 2) and FAIL SAFE:
        # an unparseable record refuses rather than passes.
        m = re.search(r"^\s*rc\s*=\s*(-?\d+)", open(rcf).read(), re.M)
        if not m:
            raise SystemExit2("RUN_RC.txt in %s has no parseable rc line -- failing "
                              "SAFE (rc defaults to refusing, never to 0)" % level_dir)
        out["rc"] = int(m.group(1))
        if out["rc"] != 0:
            raise SystemExit2("rc=%d at %s (124 == the cap fired)" % (out["rc"], level_dir))

    log = os.path.join(level_dir, "log.scalarTransportFoam")   # EXACT name, never a glob
    if not os.path.exists(log):
        raise SystemExit2("no log.scalarTransportFoam in %s" % level_dir)
    lt = open(log, errors="replace").read()
    if lt.count("\nEnd") < 1:
        raise SystemExit2("no End line in %s/log.scalarTransportFoam" % level_dir)
    out["end_line"] = lt.count("\nEnd")

    times = [int(t) for t in re.findall(r"^Time = (\d+)", lt, re.M)]
    if not times:
        raise SystemExit2("%s: log carries no Time lines" % level_dir)
    out["last_time"] = times[-1]
    out["n_time_lines"] = len(times)

    ctl = os.path.join(level_dir, "system", "controlDict")
    if not os.path.exists(ctl):
        raise SystemExit2("no system/controlDict in %s" % level_dir)
    m = re.search(r"^endTime\s+([0-9.eE+-]+)\s*;", open(ctl).read(), re.M)
    if not m:
        raise SystemExit2("%s/system/controlDict has no endTime" % level_dir)
    out["endTime"] = float(m.group(1))
    if abs(out["endTime"] - ENDTIME_EXPECTED) > 1e-9:
        raise SystemExit2("%s ran endTime %g, but the FROZEN endTime is %d"
                          % (level_dir, out["endTime"], ENDTIME_EXPECTED))
    if out["last_time"] != int(out["endTime"]):
        raise SystemExit2("%s last time %d != endTime %d -- the run did not complete"
                          % (level_dir, out["last_time"], int(out["endTime"])))
    if out["n_time_lines"] != out["last_time"]:
        raise SystemExit2("%s: %d Time lines but last time is %d"
                          % (level_dir, out["n_time_lines"], out["last_time"]))

    t = str(out["last_time"])
    out["time_dir"] = t
    for f in ("T", "U", "phi"):
        if not (os.path.exists(os.path.join(level_dir, t, f))
                or os.path.exists(os.path.join(level_dir, t, f + ".gz"))):
            raise SystemExit2("field %s missing at %s/%s (X and X.gz both checked)"
                              % (f, level_dir, t))

    # AGE GUARD -- PHYSICS-CRITICAL. 0/T is touched last at launch, so it dates the
    # run allowed to produce the answer.
    def mt(p):
        for c in (p, p + ".gz"):
            if os.path.exists(c):
                return os.path.getmtime(c)
        raise SystemExit2("cannot stat %s" % p)
    z = mt(os.path.join(level_dir, "0", "T"))
    for f in ("T", "U"):
        if not mt(os.path.join(level_dir, t, f)) > z:
            raise SystemExit2("AGE GUARD: %s/%s/%s is not newer than 0/T"
                              % (level_dir, t, f))
    out["age_guard"] = "fields at endTime newer than 0/T"

    # Mesh birth certificate -- PHYSICS-CRITICAL (MESH_STANDARD sec.6).
    bc = os.path.join(level_dir, "birth_certificate.json")
    if not os.path.exists(bc):
        raise SystemExit2("no birth_certificate.json in %s -- an uncertified mesh "
                          "does not enter a graded run" % level_dir)
    b = json.load(open(bc))
    if not b.get("mesh_ok"):
        raise SystemExit2("%s: checkMesh did not report Mesh OK" % level_dir)
    if b.get("cells") != NX_OF[level] * NR_OF[level]:
        raise SystemExit2("%s: mesh has %s cells, the frozen level is %d x %d = %d"
                          % (level_dir, b.get("cells"), NX_OF[level], NR_OF[level],
                             NX_OF[level] * NR_OF[level]))
    out["birth_certificate"] = {k: b.get(k) for k in
                                ("cells", "mesh_ok", "max_skewness", "max_aspect_ratio",
                                 "max_non_orthogonality", "nx", "nr")}
    return out


def convergence(level_dir):
    """FIXED-window convergence clause (PREREG_TEMPLATE Amendment 4), PHYSICS-CRITICAL.

    1. FIXED window of PLATEAU_WINDOW samples -- never a fraction of the run, so
       the clause cannot silently loosen when endTime or writeInterval changes.
    2. Fewer than MIN_ITERS iterations -> REFUSE (CANNOT_TELL), never a lenient pass.
    3. NULL-RANGE refusal: a series with no variation at all is REFUSED -- a dead
       channel and a converged one look identical to a tolerance.
    4. A statistic that REJECTS A GROWING SERIES: the second half of the window
       must not sit above the first half (in log10), so a climbing residual fails.
    5. The realised sample count is RECORDED (n_window) in the grading artifact.

    L-338: T is the ONLY equation this solver solves. There is no transverse
    velocity and no pressure channel here, so there is no degenerate (near-zero)
    field whose normalized residual is meaningless noise. The clause gates on the
    driven channel and on nothing else, and that is stated, not inferred.
    """
    ser = read_solver_info(level_dir)
    n = len(ser)
    if n < MIN_ITERS:
        raise SystemExit2("%s: %d iterations recorded, fewer than the frozen minimum "
                          "%d -- CANNOT_TELL, never a pass" % (level_dir, n, MIN_ITERS))
    if n < PLATEAU_WINDOW:
        raise SystemExit2("%s: %d samples, fewer than the FIXED window %d"
                          % (level_dir, n, PLATEAU_WINDOW))
    win = [v for _, v in ser[-PLATEAU_WINDOW:]]
    if min(win) <= 0.0:
        raise SystemExit2("%s: a non-positive residual (%g) in the window -- "
                          "unreadable, refused" % (level_dir, min(win)))
    lg = [math.log10(v) for v in win]
    ptp = max(lg) - min(lg)
    if ptp <= 0.0:
        raise SystemExit2("%s: NULL RANGE -- the residual series is exactly flat over "
                          "the last %d iterations; a dead channel and a converged one "
                          "look identical to a tolerance" % (level_dir, PLATEAU_WINDOW))
    h = PLATEAU_WINDOW // 2
    m1 = sum(lg[:h]) / h
    m2 = sum(lg[h:]) / (PLATEAU_WINDOW - h)
    if m2 > m1:
        raise SystemExit2("%s: the residual is GROWING over the fixed window "
                          "(log10 mean %.4f -> %.4f)" % (level_dir, m1, m2))
    worst = max(win)
    if worst > RES_FLOOR:
        raise SystemExit2("%s: max T_initial over the fixed %d-iteration window is %.4g, "
                          "above the FROZEN floor %.4g -- not converged"
                          % (level_dir, PLATEAU_WINDOW, worst, RES_FLOOR))
    return {"n_iters": n, "n_window": PLATEAU_WINDOW, "res_max_in_window": worst,
            "res_final": win[-1], "log10_ptp": ptp, "log10_mean_first_half": m1,
            "log10_mean_second_half": m2, "floor": RES_FLOOR, "channel": "T (the only driven equation)"}


# ---------------------------------------------------------- gate instruments ---
def station_files(level_dir, i):
    tag = "x%02d" % (i + 1)
    base = os.path.join(level_dir, "postProcessing")
    def one(name):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            raise SystemExit2("no postProcessing/%s in %s" % (name, level_dir))
        subs = sorted(os.listdir(d))
        for s in subs:
            p = os.path.join(d, s, "surfaceFieldValue.dat")
            if os.path.exists(p):
                return p
        raise SystemExit2("no surfaceFieldValue.dat under postProcessing/%s" % name)
    return one("mixCup_" + tag), one("flux_" + tag), tag


def read_station(level_dir, level, i):
    mp, fp, tag = station_files(level_dir, i)
    region = "outlet" if i == len(STATIONS) - 1 else tag
    mc = read_sfv(mp, "weightedAverage", "T", region)
    fx = read_sfv(fp, "sum", "phi", region)
    if mc["weight"] != "phi":
        raise SystemExit2("%s: the mixing cup is weighted by %r, not by phi -- an "
                          "area-weighted average is the WRONG statistic here and is "
                          "78 %% away from the reference" % (mp, ))
    nr = NR_OF[level]
    for nm, d in (("mixCup", mc), ("flux", fx)):
        if d["faces"] != nr:
            raise SystemExit2("%s %s: %s faces on station %s, the level's radial cell "
                              "count is %d -- the zone does not span one cross-section"
                              % (level, nm, d["faces"], tag, nr))
    rel = abs(fx["value"] - WEDGE_FLUX) / WEDGE_FLUX
    if rel > FLUX_REL_TOL:
        raise SystemExit2("%s CONSERVATION/ORIENTATION CONTROL FAILED at %s: sum(phi) = "
                          "%.12e against the flat-wedge analytic %.12e (rel %.3e > %.1e). "
                          "A face oriented against the flow makes the mixing cup silently "
                          "wrong; a mixing cup whose weight sum is wrong is not a number."
                          % (level, tag, fx["value"], WEDGE_FLUX, rel, FLUX_REL_TOL))
    return {"station_m": STATIONS[i], "tag": tag, "Y_mixcup": mc["value"],
            "theta": theta_of(mc["value"]), "flux": fx["value"], "flux_rel_dev": rel,
            "faces": mc["faces"], "region": mc["region"]}


# ------------------------------------------------------- planted-zero control --
def planted_zero(level_dir):
    """CLAUDE.md rule 3, calibrated to the reader (L-340).

    The comparator's gate reader is a SINGLE-VALUE parser on one .dat row, so a
    single-value plant is undiluted and the reader delta equals the plant exactly.
    FALL-THROUGH REFUSAL (PREREG_TEMPLATE Amendment 6a item 2): the only way this
    function RETURNS is to have seen the plant.
    """
    mp, _, tag = station_files(level_dir, 0)
    tmp = tempfile.mkdtemp(prefix="vmfl006_plant_")
    try:
        dst = os.path.join(tmp, "surfaceFieldValue.dat")
        shutil.copy(mp, dst)
        base = read_sfv(dst, "weightedAverage", "T", tag)["value"]
        lines = open(dst).read().splitlines()
        for k in range(len(lines) - 1, -1, -1):
            if lines[k] and not lines[k].startswith("#"):
                f = lines[k].split("\t")
                cols = [c for c in f if c.strip()]
                cols[1] = "%.12e" % (float(cols[1]) + PLANT)
                lines[k] = "\t".join(cols)
                break
        open(dst, "w").write("\n".join(lines) + "\n")
        seen = read_sfv(dst, "weightedAverage", "T", tag)["value"]
        delta = seen - base
        if abs(delta - PLANT) > 1e-12:
            raise SystemExit2("planted-zero control FAILED: planted %g into the mixing-cup "
                              "record on disk, the reader moved by %g -- a reader not shown "
                              "able to see a non-zero cannot certify a zero (CLAUDE.md rule 3)"
                              % (PLANT, delta))
        return {"passed": True, "planted": PLANT, "reader_delta": delta,
                "file": os.path.basename(mp), "station": tag}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------ Roache triple ----
def roache(f1, f2, f3, r=RATIO, fs=FS):
    """f1 coarse, f2 medium, f3 fine."""
    d32 = f3 - f2
    d21 = f2 - f1
    out = {"f_coarse": f1, "f_med": f2, "f_fine": f3, "ratio": r, "fs": fs,
           "d21": d21, "d32": d32}
    if d21 == 0.0 and d32 == 0.0:
        out["state"] = "EXACT"; out["p"] = None; out["gci_fine"] = None; return out
    if d21 == 0.0 or d32 == 0.0:
        out["state"] = "STAGNANT"; out["p"] = None; out["gci_fine"] = None; return out
    R = d32 / d21
    out["R"] = R
    if R < 0.0:
        out["state"] = "OSCILLATORY"; out["p"] = None; out["gci_fine"] = None; return out
    if R >= 1.0:
        out["state"] = "DIVERGENT"; out["p"] = None; out["gci_fine"] = None; return out
    p = math.log(abs(d21 / d32)) / math.log(r)
    out["p"] = p
    # OBSERVED-ORDER FLOOR. R near 1 is a STAGNANT family and ln(R)/ln(r) of it is a
    # floating-point crumb that reads as a valid, very small order; a GCI computed
    # from it is a number with no meaning. FINDING_p_floor.md sec.4.
    if p < P_MIN:
        out["state"] = "STAGNANT"; out["p_floor"] = P_MIN; out["p_below_floor"] = True
        out["gci_fine"] = None; out["f_extrapolated"] = None
        return out
    out["state"] = "CONVERGING"
    out["f_extrapolated"] = f3 + d32 / (r ** p - 1.0)
    out["gci_fine"] = fs * abs(d32 / f3) / (r ** p - 1.0)
    return out


VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def verdict_for(tri, inside, rc_unknown=False):
    """The ONE verdict path. main() grades through it and the planted controls
    DRIVE it, so the controls exercise the code that actually decides."""
    if rc_unknown:
        v, why = ("NOT A RESULT",
                  "the solver rc could not be read (RUN_RC.txt absent). Under L-342 a "
                  "bookkeeping failure invalidates the bookkeeping and not the physics: "
                  "every physics number is printed above and nothing is voided, but a row "
                  "whose rc is unknown is not a result.")
    elif tri["state"] != "CONVERGING":
        if tri.get("p_below_floor"):
            v, why = ("NOT A RESULT",
                      "observed order p = %.6g is below the frozen floor P_MIN = %.3g; the "
                      "triple is %s and NO GCI is quoted (FINDING_p_floor.md sec.4)"
                      % (tri["p"], P_MIN, tri["state"]))
        else:
            v, why = ("NOT A RESULT",
                      "grid triple is %s, not CONVERGING (CLAUDE.md rule 5 step 2) -- "
                      "NOT A RESULT whatever the value" % tri["state"])
    elif inside:
        v, why = ("GATE REACHED",
                  "every station within %.3g of the manual's Target column, triple "
                  "CONVERGING. Ceiling is GATE REACHED, not PASS: the reference is "
                  "ANALYTICAL, which buys V and never P (PREREG_TEMPLATE Amendment 1)."
                  % TOL)
    else:
        v, why = ("GATE FAIL", "at least one station outside the frozen %.3g band" % TOL)
    # rule 1's vocabulary guard, as an EXPLICIT refusal -- `python3 -O` strips
    # asserts, so this may never be an assert (PREREG_TEMPLATE Amendment 6 item 2).
    if v not in VERDICTS:
        raise SystemExit2("V0: %r is not in the fixed verdict vocabulary %r" % (v, VERDICTS))
    return (v, why)


def p_floor_control():
    """PLANTED CONTROL for the observed-order floor. A floor nobody tests is a floor
    nobody has (FINDING_p_floor.md sec.4). Three constructed triples are fed through
    this comparator's OWN roache() and OWN verdict_for(); any mis-grading REFUSES."""
    def refuse(tag, detail):
        raise SystemExit2("P-FLOOR PLANTED CONTROL FAILED [%s]: %s (P_MIN = %.3g)"
                          % (tag, detail, P_MIN))
    out = {"P_MIN": P_MIN, "probes": {}}

    tri_a = roache(1.0, 1.1, 1.2)            # equally spaced -- FINDING_p_floor sec.2
    v_a, _ = verdict_for(tri_a, True)
    out["probes"]["equally_spaced_1.0_1.1_1.2"] = {
        "state": tri_a["state"], "p": tri_a.get("p"),
        "gci_fine": tri_a.get("gci_fine"), "verdict": v_a}
    if v_a != "NOT A RESULT":
        refuse("equally-spaced", "graded %r, expected NOT A RESULT; state %s"
               % (v_a, tri_a["state"]))
    if tri_a.get("gci_fine") is not None:
        refuse("equally-spaced", "a GCI was produced (%r) for a non-converging triple"
               % (tri_a["gci_fine"],))
    if tri_a["state"] == "CONVERGING":
        refuse("equally-spaced", "classified CONVERGING with p = %r -- the defect this "
               "floor exists for" % (tri_a.get("p"),))

    p_lo = 0.01                              # genuinely computed, BELOW the floor
    tri_b = roache(1.0, 1.1, 1.1 + 0.1 * (RATIO ** (-p_lo)))
    v_b, _ = verdict_for(tri_b, True)
    out["probes"]["below_floor_p_0.01"] = {
        "state": tri_b["state"], "p": tri_b.get("p"),
        "gci_fine": tri_b.get("gci_fine"), "verdict": v_b}
    if tri_b.get("p") is None or abs(tri_b["p"] - p_lo) > 1e-9:
        refuse("below-floor", "constructed p = %.4g was not recovered (got %r)"
               % (p_lo, tri_b.get("p")))
    if not tri_b.get("p_below_floor"):
        refuse("below-floor", "p = %r is under P_MIN and the floor did NOT fire"
               % (tri_b.get("p"),))
    if v_b != "NOT A RESULT":
        refuse("below-floor", "graded %r, expected NOT A RESULT" % (v_b,))
    if tri_b.get("gci_fine") is not None:
        refuse("below-floor", "a GCI was produced (%r) below the floor" % (tri_b["gci_fine"],))

    p_hi = 0.5                               # ABOVE the floor: it must not over-fire
    tri_c = roache(1.0, 1.1, 1.1 + 0.1 * (RATIO ** (-p_hi)))
    v_c, _ = verdict_for(tri_c, True)
    out["probes"]["above_floor_p_0.5"] = {
        "state": tri_c["state"], "p": tri_c.get("p"),
        "gci_fine": tri_c.get("gci_fine"), "verdict": v_c}
    if tri_c["state"] != "CONVERGING" or tri_c.get("p_below_floor"):
        refuse("above-floor", "p = %r is above P_MIN and the floor fired anyway"
               % (tri_c.get("p"),))
    if tri_c.get("gci_fine") is None:
        refuse("above-floor", "no GCI for a converging triple above the floor")
    if v_c != "GATE REACHED":
        refuse("above-floor", "graded %r, expected GATE REACHED inside the band" % (v_c,))
    out["passed"] = True
    return out


def infra_report(run_root, level_dirs):
    """INFRASTRUCTURE class (L-342). EVERY read here is best-effort: absent or
    malformed is a WARNING and grading proceeds. Nothing in this function can
    refuse, and nothing it returns is allowed to reach a verdict."""
    rep = {"cost": None, "launch_record": None, "contention": None, "per_level": {}}
    def kv(path):
        d = {}
        if not os.path.exists(path):
            infra_warn("%s absent -- bookkeeping only, the verdict is unaffected" % path)
            return None
        try:
            for l in open(path, errors="replace").read().splitlines():
                m = re.match(r"^\s*(\w+)\s*=\s*(.*)$", l)
                if m:
                    d[m.group(1)] = m.group(2).strip()
        except Exception as e:
            infra_warn("%s unreadable (%s) -- bookkeeping only" % (path, e))
            return None
        if not d:
            infra_warn("%s parsed to nothing -- bookkeeping only" % path)
            return None
        return d
    rep["cost"] = kv(os.path.join(run_root, "COST.txt"))
    rep["launch_record"] = kv(os.path.join(run_root, "LAUNCH_RECORD.txt"))
    if not os.path.exists(os.path.join(run_root, "CONTENTION.txt")):
        infra_warn("CONTENTION.txt absent -- bookkeeping only")
    for lv, d in level_dirs.items():
        rc = kv(os.path.join(d, "RUN_RC.txt")) or {}
        rep["per_level"][lv] = {"wall_s": rc.get("wall_s"), "core_min": rc.get("core_min"),
                                "timeout_s": rc.get("timeout_s")}
    return rep


# ----------------------------------------------------------- grading of a run --
def grade_levels(root):
    """Reads the three levels and returns the full result dict. Shared by main()
    and by the INFRASTRUCTURE-TOLERANCE control, so the control grades through the
    code that actually decides rather than a paraphrase of it."""
    res = {"case": "VMFL006", "manual_page": "27-28", "tol": TOL,
           "reference": MANUAL, "reference_kind": "ANALYTICAL (Graetz series; Kays & Crawford 1993 pp.126-134)",
           "ansys_context_only": FLUENT, "lab_graetz_shooting": LAB_SHOOT,
           "lab_graetz_finite_volume": LAB_FV, "stations_m": STATIONS,
           "comparator": os.path.abspath(__file__),
           "completion": {}, "convergence": {}, "levels": {}, "planted_zero": None}
    res["p_floor_control"] = p_floor_control()
    level_dirs = {}
    rc_unknown = False
    for lv in LEVELS:
        d = os.path.join(root, lv)
        level_dirs[lv] = d
        c = completion(d, lv)
        rc_unknown = rc_unknown or c["rc_unknown"]
        res["completion"][lv] = c
        res["convergence"][lv] = convergence(d)
        st = [read_station(d, lv, i) for i in range(len(STATIONS))]
        res["levels"][lv] = {"stations": st,
                             "theta": [s["theta"] for s in st],
                             "worst_flux_rel_dev": max(s["flux_rel_dev"] for s in st)}
    res["rc_unknown"] = rc_unknown
    res["planted_zero"] = planted_zero(level_dirs[LEVELS[-1]])
    res["infrastructure"] = infra_report(root, level_dirs)
    res["infra_warnings"] = list(INFRA_WARNINGS)

    fine = res["levels"][LEVELS[-1]]["theta"]
    devs = [abs(fine[i] - MANUAL[i]) / abs(MANUAL[i]) for i in range(len(STATIONS))]
    res["rel_dev_per_station"] = devs
    res["worst_rel_dev"] = max(devs)
    res["worst_station_m"] = STATIONS[devs.index(max(devs))]
    res["lab_value_x010"] = fine[TRIPLE_I]
    tri = roache(res["levels"]["L1"]["theta"][TRIPLE_I],
                 res["levels"]["L2"]["theta"][TRIPLE_I],
                 res["levels"]["L3"]["theta"][TRIPLE_I])
    res["triple"] = tri
    res["triple_station_m"] = STATIONS[TRIPLE_I]
    inside = res["worst_rel_dev"] <= TOL
    res["inside_band"] = inside
    v, why = verdict_for(tri, inside, rc_unknown)
    res["verdict"], res["why"] = v, why
    return res


# ---------------------------------------------- INFRASTRUCTURE-TOLERANCE control --
def _write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(s)


def build_fake_run(root, thetas_by_level, endtime=ENDTIME_EXPECTED):
    """Construct a complete, gradable run on disk. Used ONLY by the selftest and by
    the infrastructure-tolerance control."""
    for lv in LEVELS:
        d = os.path.join(root, lv)
        nr = NR_OF[lv]
        _write(os.path.join(d, "RUN_RC.txt"),
               "rc = 0\nlevel = %s\nwall_s = 12\nranks = 1\ncore_min = 0.2\ntimeout_s = 600\n" % lv)
        body = "".join("Time = %d\n" % i for i in range(1, endtime + 1))
        _write(os.path.join(d, "log.scalarTransportFoam"), body + "\nEnd\n")
        _write(os.path.join(d, "system", "controlDict"), "endTime %d;\n" % endtime)
        _write(os.path.join(d, "birth_certificate.json"),
               json.dumps({"cells": NX_OF[lv] * nr, "mesh_ok": True, "max_skewness": 0.33,
                           "max_aspect_ratio": 8.8, "max_non_orthogonality": 0.0,
                           "nx": NX_OF[lv], "nr": nr}))
        rows = ["# Solver information",
                "# Time\tT_solver\tT_initial\tT_final\tT_iters\tT_converged"]
        for i in range(1, endtime + 1):
            rows.append("%d\tsmoothSolver\t%.12e\t1e-14\t4\ttrue"
                        % (i, max(1e-14, 1.0 * (0.99 ** i)) + 1e-12 * (1.0 / (1 + i))))
        _write(os.path.join(d, "postProcessing", "residuals", "0", "solverInfo.dat"),
               "\n".join(rows) + "\n")
        for i, th in enumerate(thetas_by_level[lv]):
            tag = "x%02d" % (i + 1)
            region = ("patch outlet" if i == len(STATIONS) - 1 else "faceZone %s" % tag)
            y = Y_WALL - (Y_WALL - Y_IN) * th
            _write(os.path.join(d, "postProcessing", "mixCup_" + tag, "0", "surfaceFieldValue.dat"),
                   "# Region type :     %s\n# Faces             : %d\n# Area              : 2.7e-07\n"
                   "# Scale factor      : 1.000000000000e+00\n# Weight field      : phi\n"
                   "# Time              \tweightedAverage(T)\n%d                  \t%.12e\n"
                   % (region, nr, endtime, y))
            _write(os.path.join(d, "postProcessing", "flux_" + tag, "0", "surfaceFieldValue.dat"),
                   "# Region type :     %s\n# Faces             : %d\n# Area              : 2.7e-07\n"
                   "# Scale factor      : 1.000000000000e+00\n"
                   "# Time              \tsum(phi)\n%d                  \t%.12e\n"
                   % (region, nr, endtime, WEDGE_FLUX))
        # 0/T is the age-guard marker: make it OLDER than the endTime fields.
        _write(os.path.join(d, "0", "T"), "T0\n")
        for f in ("T", "U", "phi"):
            _write(os.path.join(d, str(endtime), f), "%s\n" % f)
        zt = os.path.getmtime(os.path.join(d, str(endtime), "T")) - 10
        os.utime(os.path.join(d, "0", "T"), (zt, zt))
    _write(os.path.join(root, "COST.txt"), "total_wall_s = 36\nranks = 1\ntotal_core_min = 0.6\n")
    _write(os.path.join(root, "LAUNCH_RECORD.txt"), "launched_utc = 2026-01-01T00:00:00Z\nmode = graded\n")
    _write(os.path.join(root, "CONTENTION.txt"), "loadavg = 0 0 0\n")


def infra_tolerance_control():
    """PLANTED CONTROL for Sanaa's universal rule (L-342), DRIVEN not declared.

      plant 1: a constructed run is graded intact, then graded again with COST.txt
               DELETED and LAUNCH_RECORD.txt CORRUPTED. The verdict, the lab value
               and the observed order must be IDENTICAL. If an infrastructure field
               can move a verdict, this control REFUSES.
      plant 2: the same run has a PHYSICS field broken (the End line removed). The
               comparator must still REFUSE (exit 2). A rule that tolerates
               bookkeeping must not thereby tolerate a broken solve.
    """
    def refuse(tag, detail):
        raise SystemExit2("INFRASTRUCTURE-TOLERANCE CONTROL FAILED [%s]: %s" % (tag, detail))
    # a triple that converges cleanly at p = 2 on every station
    base = {}
    for k, lv in enumerate(LEVELS):
        eps = 0.004 / (RATIO ** (2 * k))
        base[lv] = [MANUAL[i] * (1.0 + eps) for i in range(len(STATIONS))]
    d = tempfile.mkdtemp(prefix="vmfl006_infra_")
    try:
        root = os.path.join(d, "run")
        build_fake_run(root, base)
        del INFRA_WARNINGS[:]
        a = grade_levels(root)
        os.remove(os.path.join(root, "COST.txt"))
        open(os.path.join(root, "LAUNCH_RECORD.txt"), "w").write("<<<corrupt binary garbage>>>\n")
        del INFRA_WARNINGS[:]
        b = grade_levels(root)
        if a["verdict"] != b["verdict"]:
            refuse("plant 1", "verdict moved from %r to %r when COST.txt was deleted and "
                              "LAUNCH_RECORD.txt corrupted" % (a["verdict"], b["verdict"]))
        if a["lab_value_x010"] != b["lab_value_x010"]:
            refuse("plant 1", "the lab value moved (%r -> %r) on an infrastructure change"
                   % (a["lab_value_x010"], b["lab_value_x010"]))
        if a["triple"].get("p") != b["triple"].get("p"):
            refuse("plant 1", "the observed order moved on an infrastructure change")
        if not b["infra_warnings"]:
            refuse("plant 1", "the missing COST.txt produced NO warning -- an unreported "
                              "absence and a healthy read must not look alike")
        # plant 2: break a PHYSICS field. It must still refuse.
        p = os.path.join(root, "L2", "log.scalarTransportFoam")
        _t = open(p).read()          # READ FIRST (see the same trap above)
        _t = _t.replace("\nEnd\n", "\nNOT-AN-END\n")
        open(p, "w").write(_t)
        refused = False
        try:
            del INFRA_WARNINGS[:]
            grade_levels(root)
        except SystemExit as ex:
            refused = (ex.code == 2)
        if not refused:
            refuse("plant 2", "a broken PHYSICS field (the End line) did NOT refuse -- "
                              "tolerating bookkeeping must not tolerate a broken solve")
        return {"passed": True, "verdict_intact": a["verdict"], "verdict_degraded": b["verdict"],
                "infra_warnings_seen": len(b["infra_warnings"]),
                "physics_plant_refused": refused}
    finally:
        del INFRA_WARNINGS[:]
        shutil.rmtree(d, ignore_errors=True)


# ------------------------------------------------------------------- selftest --
def selftest():
    ok = True

    def chk(c, name, got=""):
        nonlocal ok
        print("  [%s] %s  %s" % ("PASS" if c else "FAIL", name, got))
        ok = ok and bool(c)

    print("--- selftest: normalisation and the reference identity")
    chk(abs(theta_of(Y_IN) - 1.0) < 1e-15, "theta(inlet) == 1")
    chk(abs(theta_of(Y_WALL) - 0.0) < 1e-15, "theta(wall) == 0")
    chk(len(MANUAL) == 10 and len(STATIONS) == 10 and len(FLUENT) == 10,
        "ten stations, ten targets, ten Fluent values")
    w = max(abs(LAB_SHOOT[i] - MANUAL[i]) / MANUAL[i] for i in range(10))
    chk(w < 1e-3, "the lab's own Graetz evaluation corroborates the manual within 0.1 %",
        "worst %.5f %%" % (100 * w))
    w2 = max(abs(LAB_SHOOT[i] - LAB_FV[i]) / LAB_FV[i] for i in range(10))
    chk(w2 < 1e-5, "the lab's TWO independent Graetz instruments agree",
        "worst %.3e" % w2)

    print("--- selftest: Roache classifier")
    chk(roache(1.0, 1.5, 1.75)["state"] == "CONVERGING", "first-order -> CONVERGING")
    chk(abs(roache(1.0, 1.5, 1.75)["p"] - 1.0) < 1e-9, "p == 1")
    chk(abs(roache(1.0, 1.25, 1.3125)["p"] - 2.0) < 1e-9, "second-order family -> p == 2")
    chk(roache(1.0, 2.0, 4.0)["state"] == "DIVERGENT", "divergent")
    chk(roache(1.0, 2.0, 1.5)["state"] == "OSCILLATORY", "oscillatory")
    chk(roache(2.0, 2.0, 2.0)["state"] == "EXACT", "identical -> EXACT")

    print("--- selftest: PLANTED CONTROL -- the observed-order floor P_MIN = %.3g" % P_MIN)
    pf = p_floor_control()
    chk(pf["probes"]["equally_spaced_1.0_1.1_1.2"]["verdict"] == "NOT A RESULT"
        and pf["probes"]["equally_spaced_1.0_1.1_1.2"]["gci_fine"] is None,
        "(1.0, 1.1, 1.2) -> NOT A RESULT, no GCI",
        pf["probes"]["equally_spaced_1.0_1.1_1.2"]["state"])
    chk(pf["probes"]["below_floor_p_0.01"]["verdict"] == "NOT A RESULT",
        "p = 0.01 (below floor) -> NOT A RESULT, no GCI")
    chk(pf["probes"]["above_floor_p_0.5"]["verdict"] == "GATE REACHED"
        and pf["probes"]["above_floor_p_0.5"]["gci_fine"] is not None,
        "p = 0.5 (above floor) -> the floor does NOT over-fire, GCI quoted")

    print("--- selftest: the gate can PASS and can FAIL")
    chk(0.005 <= TOL, "+0.5 %% is inside the band")
    chk(not (0.02 <= TOL), "+2 %% is OUTSIDE the band")
    chk(max(abs(FLUENT[i] - MANUAL[i]) / MANUAL[i] for i in range(10)) < TOL,
        "Ansys Fluent's own numbers would sit INSIDE this band",
        "worst %.4f %%" % (100 * max(abs(FLUENT[i] - MANUAL[i]) / MANUAL[i] for i in range(10))))

    print("--- selftest: end-to-end grading on a CONSTRUCTED run whose answer is known")
    d = tempfile.mkdtemp(prefix="st006_")
    try:
        # a triple converging at p = 2 towards a value 0.4 % above the target: inside
        # the 1 % band, so the constructed answer is deliberately NOT the target itself
        # -- a reader that returned the reference would be caught here.
        th = {}
        for k, lv in enumerate(LEVELS):
            eps = 0.004 / (RATIO ** (2 * k))
            th[lv] = [MANUAL[i] * (1.0 + eps) for i in range(10)]
        root = os.path.join(d, "run")
        build_fake_run(root, th)
        del INFRA_WARNINGS[:]
        r = grade_levels(root)
        chk(r["verdict"] == "GATE REACHED", "constructed in-band converging run -> GATE REACHED",
            r["verdict"])
        chk(abs(r["triple"]["p"] - 2.0) < 1e-6, "the constructed observed order is recovered",
            "%.6f" % r["triple"]["p"])
        expect_fine = MANUAL[TRIPLE_I] * (1.0 + 0.004 / (RATIO ** (2 * (len(LEVELS) - 1))))
        chk(abs(r["lab_value_x010"] - expect_fine) < 1e-12
            and abs(r["lab_value_x010"] - MANUAL[TRIPLE_I]) > 1e-6,
            "the fine value read from disk is the CONSTRUCTED one, not the reference",
            "%.9f (constructed %.9f, reference %.4f)"
            % (r["lab_value_x010"], expect_fine, MANUAL[TRIPLE_I]))
        chk(r["planted_zero"]["passed"]
            and abs(r["planted_zero"]["reader_delta"] - PLANT) < 1e-12,
            "planted-zero sees the plant undiluted (L-340)")

        # a BLIND reader must REFUSE
        global read_sfv
        _orig = read_sfv
        try:
            read_sfv = lambda p, o, f, rg: {"value": 0.0, "faces": None, "region": rg,
                                            "weight": "phi", "n_rows": 1, "time": 0.0}
            blind = False
            try:
                planted_zero(os.path.join(root, "L3"))
            except SystemExit as ex:
                blind = (ex.code == 2)
            chk(blind, "planted-zero REFUSES (exit 2) a reader that cannot see the plant")
        finally:
            read_sfv = _orig

        # out-of-band construction must GATE FAIL, not silently pass
        th2 = {lv: [v * 1.05 for v in th[lv]] for lv in LEVELS}
        root2 = os.path.join(d, "run2")
        build_fake_run(root2, th2)
        del INFRA_WARNINGS[:]
        r2 = grade_levels(root2)
        chk(r2["verdict"] == "GATE FAIL", "a 5 %% offset run -> GATE FAIL", r2["verdict"])

        # a wrong flux (orientation) must REFUSE
        root3 = os.path.join(d, "run3")
        build_fake_run(root3, th)
        p = os.path.join(root3, "L1", "postProcessing", "flux_x05", "0", "surfaceFieldValue.dat")
        _t = open(p).read()          # READ FIRST -- open(p,"w") truncates before the read runs
        _t = _t.replace("%.12e" % WEDGE_FLUX, "%.12e" % (-WEDGE_FLUX))
        open(p, "w").write(_t)
        ref = False
        try:
            del INFRA_WARNINGS[:]
            grade_levels(root3)
        except SystemExit as ex:
            ref = (ex.code == 2)
        chk(ref, "a reversed sum(phi) REFUSES (conservation/orientation control)")

        # a NON-ZERO rc must REFUSE (this is the clause that says the solver failed)
        root5 = os.path.join(d, "run5")
        build_fake_run(root5, th)
        pr = os.path.join(root5, "L3", "RUN_RC.txt")
        _t = open(pr).read().replace("rc = 0", "rc = 1")
        open(pr, "w").write(_t)
        ref5 = False
        try:
            del INFRA_WARNINGS[:]
            grade_levels(root5)
        except SystemExit as ex:
            ref5 = (ex.code == 2)
        chk(ref5, "a non-zero solver rc REFUSES (exit 2) -- strict completion, rule 4")

        # and an UNPARSEABLE RUN_RC.txt must FAIL SAFE (refuse), never default to 0
        root6 = os.path.join(d, "run6")
        build_fake_run(root6, th)
        open(os.path.join(root6, "L1", "RUN_RC.txt"), "w").write("garbage with no rc key\n")
        ref6 = False
        try:
            del INFRA_WARNINGS[:]
            grade_levels(root6)
        except SystemExit as ex:
            ref6 = (ex.code == 2)
        chk(ref6, "an UNPARSEABLE RUN_RC.txt fails SAFE (refuses), never defaults to rc = 0")

        # a missing RUN_RC.txt must NOT void the physics: NOT A RESULT, numbers printed
        root4 = os.path.join(d, "run4")
        build_fake_run(root4, th)
        os.remove(os.path.join(root4, "L2", "RUN_RC.txt"))
        del INFRA_WARNINGS[:]
        r4 = grade_levels(root4)
        chk(r4["verdict"] == "NOT A RESULT" and r4["lab_value_x010"] == r["lab_value_x010"],
            "absent RUN_RC.txt -> NOT A RESULT with the physics STILL COMPUTED (L-342)",
            r4["verdict"])
    finally:
        del INFRA_WARNINGS[:]
        shutil.rmtree(d, ignore_errors=True)

    print("--- selftest: PLANTED CONTROL -- infrastructure tolerance (L-342)")
    it = infra_tolerance_control()
    chk(it["passed"] and it["verdict_intact"] == it["verdict_degraded"],
        "deleting COST.txt and corrupting LAUNCH_RECORD.txt leaves the verdict IDENTICAL",
        "%s == %s, %d warnings" % (it["verdict_intact"], it["verdict_degraded"],
                                   it["infra_warnings_seen"]))
    chk(it["physics_plant_refused"],
        "breaking a PHYSICS field (the End line) STILL refuses (exit 2)")

    print("\nSELFTEST: %s" % ("all checks passed" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


# ----------------------------------------------------------------------- main --
def main():
    root = os.path.normpath(RUN_ROOT)
    print("=" * 78)
    print("VMFL006 -- Multicomponent Species Transport in Pipe Flow")
    print("Ansys FD Verification Manual 2026 R1, pp. 27-28")
    print("gate: MIXING-CUP theta = (0.9 - Y)/0.4 at x = 0.01..0.10 m vs the manual's")
    print("      Target column (ANALYTICAL -- Graetz; Kays & Crawford 1993 pp.126-134)")
    print("      band |theta_lab - theta_ref|/theta_ref <= %.3g at EVERY station, at L3" % TOL)
    print("=" * 78)

    # PLANTED CONTROLS, driven on the FROZEN grading path itself, before any level
    # is read. Each REFUSES (exit 2) rather than grading.
    pf = p_floor_control()
    print("p-floor planted control OK (P_MIN = %.3g): (1.0,1.1,1.2) -> %s, no GCI"
          % (P_MIN, pf["probes"]["equally_spaced_1.0_1.1_1.2"]["verdict"]))
    it = infra_tolerance_control()
    print("infrastructure-tolerance control OK (L-342): verdict %s with COST.txt present "
          "and %s with it deleted; a broken End line still refuses"
          % (it["verdict_intact"], it["verdict_degraded"]))

    res = grade_levels(root)
    res["p_floor_control"] = pf
    res["infra_tolerance_control"] = it

    print("\n--- mixing-cup theta per station (fine level %s) ---" % LEVELS[-1])
    print("   x (m)    lab theta      manual Target   rel dev      lab Graetz (prediction)")
    fine = res["levels"][LEVELS[-1]]["theta"]
    for i, x in enumerate(STATIONS):
        print("   %.2f     %.9f    %.4f          %+8.4f %%   %.9f"
              % (x, fine[i], MANUAL[i], 100 * (fine[i] - MANUAL[i]) / MANUAL[i], LAB_SHOOT[i]))
    print("  worst |lab - Target|/Target = %.5f %% at x = %.2f m"
          % (100 * res["worst_rel_dev"], res["worst_station_m"]))
    print("  worst conservation-control deviation across all levels = %.3e"
          % max(res["levels"][lv]["worst_flux_rel_dev"] for lv in LEVELS))

    print("\nplanted-zero control on %s: %s" % (LEVELS[-1], json.dumps(res["planted_zero"])))

    tri = res["triple"]
    print("\n--- Roache triple on theta at x = %.2f m (r = %.1f) ---"
          % (res["triple_station_m"], RATIO))
    print("  %.9f / %.9f / %.9f  -> %s"
          % (tri["f_coarse"], tri["f_med"], tri["f_fine"], tri["state"]))
    if tri["state"] == "CONVERGING":
        print("  observed order p = %.4f   GCI_fine (Fs = %.2f) = %.6f %%"
              % (tri["p"], FS, 100.0 * tri["gci_fine"]))
    elif tri.get("p_below_floor"):
        print("  observed order p = %.6g is BELOW the frozen floor P_MIN = %.3g -- the "
              "triple is\n  reported %s and NO GCI is quoted (FINDING_p_floor.md sec.4)."
              % (tri["p"], P_MIN, tri["state"]))
    else:
        print("  observed order: undefined for a %s triple; NO GCI is quoted." % tri["state"])

    for lv in LEVELS:
        c = res["convergence"][lv]
        print("  %s convergence: n_iters=%d n_window=%d max T_initial in window=%.3e "
              "(floor %.1e)" % (lv, c["n_iters"], c["n_window"], c["res_max_in_window"],
                                c["floor"]))

    print("\nVERDICT: %s -- %s" % (res["verdict"], res["why"]))
    if res["infra_warnings"]:
        print("infrastructure warnings (bookkeeping only, no verdict effect): %d"
              % len(res["infra_warnings"]))

    out = os.path.join(root, "GRADING_VMFL006.json")
    try:
        with open(out, "w") as fh:
            json.dump(res, fh, indent=2, sort_keys=True, default=str)
        print("grading written to %s" % out)
    except Exception as e:
        infra_warn("could not write %s (%s) -- the verdict above stands" % (out, e))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
