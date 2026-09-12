#!/usr/bin/env python3
"""
SUBOFF_A1 -- THE COMPARATOR.  Grades ONE solved level against the frozen
pre-registration.  It REFUSES (exit 2) rather than degrade, and it is READ-ONLY on
the case it grades.

WHAT IT MAY AND MAY NOT RETURN
  * COMPLETION  : the seven clauses of pre-registration 7 + 11.4 limb 6.
  * Gate W      : PASS / GATE FAIL / BLOCKED.  y+ is REPORTED per patch whatever
                  the outcome (5.2).
  * S1 / S3     : the registered monitor states, as findings.
  * Gate D2     : **`NOT A RESULT`, ALWAYS, BY CONSTRUCTION.**  There is no
                  CONVERGING Roache triple for SUBOFF A1 -- Gate M has FAILED at L1
                  on the determinant limb (12.8) and L3 is BLOCKED on RAM (4.1), so
                  rule 5 fixes the label before any number exists.  `CT` is PRINTED
                  beside it because 5.3 requires it reported; the grader has NO code
                  path that can turn it into a PASS or a GATE FAIL, and a reader who
                  wants one must first produce a triple.

ARMING (11.2).  Every gate names what arms it and the UNARMED VERDICT IS `BLOCKED`,
never `PASS`.  "No disagreement found" and "nothing was compared" must not read the
same, and here they do not.

RULE 3 -- THREE PLANTED CONTROLS, ALL RUN BEFORE ANY CASE IS READ, ALL READ BACK
FROM DISK, ANY FAILURE => exit 2:
  P-A  the coefficient.dat reader is handed a synthetic file carrying a KNOWN Cd
       (1.234e-03) at a decoy time AND a different Cd at endTime, and must return
       the endTime one.  Exercises: column lookup by header name + row selection by
       time.  The same phenomenon (a wrong Cd) could also arrive from forceCoeffs
       writing a different column set, which is why the header is matched by NAME
       and the file is refused if `Cd` is absent rather than positionally guessed.
  P-B  the yPlus.dat reader is handed a synthetic file whose hull row carries a
       KNOWN max (987.654) and whose LAST row is a decoy patch, and must return the
       hull maximum over all written times.  Exercises: patch-name filtering and the
       max reduction.  A wrong y+ could also arrive from the LOG parser, so the log
       is parsed independently and both numbers go in the record.
  P-C  the completion checker is handed a synthetic case whose endTime field is
       OLDER than 0/U, and must report the age guard FAILED.  Exercises: the
       mtime comparison that is the whole content of rule 4's limb 6.  A pass here
       could also arrive from a checker that never looked, which is why the same
       plant is then re-run with the mtime corrected and must report PASS.

ZERO `assert` (L-332).
"""
import sys
if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n"); sys.exit(2)
import os, re, json, math, time, argparse, datetime

# Repository root, derived from THIS file's location (cases/navier_class/SUBOFF_A1/),
# never from cwd -- the grader is run detached by the queue runner from the case
# directory, and a cwd-derived root would silently resolve to the run tree.
REPO_ROOT_FOR_READER = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

PLANT_CD    = 1.234e-03
PLANT_YPLUS = 987.654
PLANT_DECOY_CD = 5.678e-03
REQUIRED_FIELDS = ("p", "U", "k", "omega", "nut", "phi")   # incompressible set (7)
YPLUS_CEILING = 300.0                                      # Gate W (5.2)
PLATEAU_WINDOW = 500                                       # S3, the regression window
PLATEAU_FRAC = 0.05                                        # S3, 5 %
S1_WINDOW = 500                                            # S1, consecutive iterations
WALL_PATCHES = ("hull", "sail")
REQUIRED_WALL_NUT = "nutUSpaldingWallFunction"             # 5.2, Gate W arming


# ------------------------------------------------------------------ readers --
def read_dat(path):
    """A `postProcessing` .dat file -> (header_tokens, [row_tokens...])."""
    if not os.path.isfile(path):
        return None, []
    hdr, rows = None, []
    with open(path) as f:
        for line in f:
            s = line.rstrip("\n")
            if s.startswith("#"):
                t = s.lstrip("#").split()
                if t and t[0].lower().startswith("time"):
                    hdr = t
                continue
            if s.strip():
                rows.append(s.split())
    return hdr, rows


def cd_series(path):
    """THE GRADED CT READER.  -> [(time, Cd), ...] in file order.
    The `Cd` column is found BY NAME in the header; a file without one is REFUSED
    rather than guessed at positionally."""
    hdr, rows = read_dat(path)
    if hdr is None:
        return None
    if "Cd" not in hdr:
        sys.stderr.write(f"REFUSED: no 'Cd' column named in the header of {path}; "
                         "the column is matched by NAME, never by position.\n")
        sys.exit(2)
    j = hdr.index("Cd")
    out = []
    for r in rows:
        if len(r) > j:
            try:
                out.append((float(r[0]), float(r[j])))
            except ValueError:
                continue
    return out


def yplus_from_dat(path, patch):
    """THE GRADED y+ READER.  -> (min, max, avg) for `patch` over all written times,
    or None if the patch never appears."""
    hdr, rows = read_dat(path)
    if hdr is None:
        return None
    lo, hi, av, n = math.inf, -math.inf, 0.0, 0
    for r in rows:
        if len(r) >= 5 and r[1] == patch:
            try:
                a, b, c = float(r[2]), float(r[3]), float(r[4])
            except ValueError:
                continue
            lo = min(lo, a); hi = max(hi, b); av += c; n += 1
    if n == 0:
        return None
    return (lo, hi, av / n)


_LOG_YP = re.compile(r"patch\s+(\w+)\s+y\+\s*:\s*min\s*=\s*([-\d.eE+]+)\s*,\s*"
                     r"max\s*=\s*([-\d.eE+]+)\s*,\s*average\s*=\s*([-\d.eE+]+)")


def yplus_from_log(path, patch):
    """INDEPENDENT SECOND CHANNEL.  Parses the solver log's own y+ lines."""
    if not os.path.isfile(path):
        return None
    hi = -math.inf
    with open(path, errors="replace") as f:
        for line in f:
            m = _LOG_YP.search(line)
            if m and m.group(1) == patch:
                hi = max(hi, float(m.group(3)))
    return None if hi == -math.inf else hi


def initial_residual_series(path, field):
    """Worst initial residual per outer iteration, from solverInfo's .dat."""
    hdr, rows = read_dat(path)
    if hdr is None:
        return None
    col = f"{field}_initial"
    cands = [c for c in hdr if c == col or c.startswith(field + "_initial")]
    if not cands:
        return None
    j = hdr.index(cands[0])
    out = []
    for r in rows:
        if len(r) > j:
            try:
                out.append((float(r[0]), float(r[j])))
            except ValueError:
                continue
    return out


# ------------------------------------------------------- completion (rule 4) --
def check_completion(case, end_time, ranks):
    """The seven clauses of 7 plus 11.4 limb 6.  Returns a dict; `ok` is the AND."""
    r = {}
    rcp = os.path.join(case, "solve_rc")
    r["rc_file"] = rcp if os.path.isfile(rcp) else None
    r["rc"] = int(open(rcp).read().strip()) if os.path.isfile(rcp) else None
    r["clause_rc_zero"] = (r["rc"] == 0)

    # AMENDMENT 2026-09-12 -- THE STEP COUNT IS READ ACROSS EVERY LOG SEGMENT AND IS
    # KEYED ON THE PHYSICS, NOT ON ONE FILE'S LINE COUNT.
    #
    # The block this replaces opened ONE file, `log.simpleFoam`, and counted
    # `ExecutionTime` LINES.  A killed-and-resumed run does not have one file, and
    # -- the part the obvious repair gets wrong -- CONCATENATING THE SEGMENTS DOES
    # NOT FIX IT.  MEASURED ON THIS CASE'S OWN SOLVE_L2, live at 21:52Z:
    #
    #     segment 1, killed by the 21:32Z reboot   Time = 1 .. 63
    #     resume from the t = 60 checkpoint        Time = 61 .. 3000
    #     duplicate steps in the appended log      Time = 61, 62, 63   (read back
    #                                              from the live log, not predicted)
    #     naive line sum                           3,002
    #     required                                 3,000
    #     distinct physics steps reached           3,000
    #
    # Iterations 61-63 were RUN TWICE, because the checkpoint they resume from is
    # t = 60.  A line count credits them twice.  The overlap's size varies with
    # every kill and is invisible from the log, so no fixed correction is possible;
    # the count has to be taken on the physics.
    #
    # WHAT IS REQUIRED DOES NOT CHANGE.  WHERE IT IS READ FROM DOES.  Standing rule
    # 4 is not weakened -- the age guard, the endTime match, the End line and the
    # field list all still stand below, untouched -- and one hole is closed on the
    # way: the old count was satisfied by 3,000 lines that skipped a step, and is
    # now satisfied only by the distinct steps being exactly {1 .. endTime}.
    #
    # Sanaa's ruling, 2026-08-26 and again 2026-09-12: BOOKKEEPING NEVER VOIDS
    # PHYSICS.  An ExecutionTime line count is bookkeeping.
    sys.path.insert(0, os.path.join(REPO_ROOT_FOR_READER, "scripts"))
    import solver_log_set as _sls
    _scan = _sls.scan(case, "simpleFoam", end_time=end_time, delta_t=1.0)
    r["log"] = (os.path.join(case, "log.simpleFoam")
                if os.path.isfile(os.path.join(case, "log.simpleFoam")) else None)
    r["log_segments"] = _scan["segments"]
    r["n_log_segments"] = _scan["n_segments"]
    r["resumed"] = _scan["resumed"]
    r["n_steps_distinct"] = _scan["n_steps"]
    # REPORTED, NEVER GATED.  Printed so a reader SEES the double-count rather than
    # being protected from it -- an unexplained discrepancy that no record shows is
    # worse than one shown and named.
    r["n_ExecutionTime_lines_raw_BOOKKEEPING"] = _scan["n_exec_lines_raw"]
    r["line_count_overcounts_by"] = _scan["line_count_overcounts_by"]
    r["clause_end_line"] = _scan["end_line"]
    r["n_ExecutionTime"] = _scan["n_steps"]
    r["last_Time"] = _scan["last_time"]
    r["clause_last_eq_endTime"] = _scan["clause_last_eq_endTime"]
    r["clause_exec_count"] = _scan["clause_exec_count"]
    r["missing_steps"] = _scan.get("missing_steps")
    r["n_missing_steps"] = _scan.get("n_missing_steps")
    r["step_count_method"] = _scan["counting"]

    td = os.path.join(case, str(end_time))
    r["endTime_dir"] = td if os.path.isdir(td) else None
    present = sorted(os.listdir(td)) if r["endTime_dir"] else []
    r["fields_present"] = [f for f in REQUIRED_FIELDS if f in present]
    r["fields_missing"] = [f for f in REQUIRED_FIELDS if f not in present]
    r["clause_fields"] = (len(r["fields_missing"]) == 0)

    # limb 6.1 -- reconstructed fields strictly newer than the case's own 0/U
    anchor = os.path.join(case, "0", "U")
    r["age_anchor"] = anchor if os.path.isfile(anchor) else None
    if r["age_anchor"] and r["endTime_dir"]:
        t0 = os.path.getmtime(anchor)
        ages = {f: os.path.getmtime(os.path.join(td, f)) - t0
                for f in r["fields_present"]}
        r["age_margins_s"] = ages
        r["clause_age_guard"] = bool(ages) and all(v > 0 for v in ages.values())
    else:
        r["age_margins_s"] = {}
        r["clause_age_guard"] = False

    # limb 6.2 / 6.3 -- the processor* anchor and the ordering test
    procs = sorted(d for d in os.listdir(case)
                   if d.startswith("processor") and os.path.isdir(os.path.join(case, d))) \
        if os.path.isdir(case) else []
    r["n_processor_dirs"] = len(procs)
    if not procs:
        # 11.4's own limitation, honoured: a SERIAL run has no anchor, and the limb
        # is BLOCKED, never passed.
        r["limb62"] = "BLOCKED"; r["limb63"] = "BLOCKED"
    else:
        t0 = os.path.getmtime(anchor) if r["age_anchor"] else None
        newest, oldest, missing = -math.inf, math.inf, []
        for p in procs:
            d = os.path.join(case, p, str(end_time))
            if not os.path.isdir(d):
                missing.append(p); continue
            got = [f for f in REQUIRED_FIELDS if f in os.listdir(d)]
            if len(got) != len(REQUIRED_FIELDS):
                missing.append(p + ":fields")
            for f in got:
                m = os.path.getmtime(os.path.join(d, f))
                newest = max(newest, m); oldest = min(oldest, m)
        r["processor_missing"] = missing
        r["limb62"] = ("PASS" if (not missing and t0 is not None and oldest > t0)
                       else "GATE FAIL")
        ld = os.path.join(case, "log.decomposePar.solve")
        lr = os.path.join(case, "log.reconstructPar.solve")
        if os.path.isfile(ld) and os.path.isfile(lr) and newest > -math.inf:
            r["ordering_decompose_older"] = os.path.getmtime(ld) < oldest
            r["ordering_reconstruct_newer"] = os.path.getmtime(lr) > newest
            r["limb63"] = ("PASS" if (r["ordering_decompose_older"] and
                                      r["ordering_reconstruct_newer"]) else "GATE FAIL")
        else:
            r["limb63"] = "BLOCKED"

    r["ok"] = all([r["clause_rc_zero"], r["clause_end_line"],
                   r["clause_last_eq_endTime"], r["clause_exec_count"],
                   r["clause_fields"], r["clause_age_guard"]])
    return r


# ------------------------------------------------------------ rule-3 plants --
def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def plants(scratch, end_time):
    out = {}

    # ---- P-A : the Cd reader -------------------------------------------------
    pa = os.path.join(scratch, "PLANT_A", "coefficient.dat")
    _write(pa, "# Force coefficients\n"
               "# Time\tCm\tCd\tCl\tCl(f)\tCl(r)\n"
               f"1\t0\t{PLANT_DECOY_CD:.9g}\t0\t0\t0\n"
               f"{end_time}\t0\t{PLANT_CD:.9g}\t0\t0\t0\n")
    ser = cd_series(pa)
    got = dict(ser).get(float(end_time)) if ser else None
    if got is None or abs(got - PLANT_CD) > 1e-15:
        sys.stderr.write("REFUSED (rule 3, P-A): the Cd reader could not see the "
                         f"planted {PLANT_CD} at t={end_time}; it returned {got!r}. "
                         "A CT from this reader is NOT evidence.\n")
        sys.exit(2)
    out["P_A_cd_reader"] = {"planted": PLANT_CD, "decoy_at_t1": PLANT_DECOY_CD,
                            "returned": got, "verdict": "ARMED"}

    # ---- P-B : the y+ reader -------------------------------------------------
    pb = os.path.join(scratch, "PLANT_B", "yPlus.dat")
    _write(pb, "# y+ ()\n"
               "# Time\tpatch\tmin\tmax\taverage\n"
               f"{end_time}\thull\t1.5\t{PLANT_YPLUS:.9g}\t40\n"
               f"{end_time}\tsail\t0.9\t1.1\t1.0\n")
    gb = yplus_from_dat(pb, "hull")
    if gb is None or abs(gb[1] - PLANT_YPLUS) > 1e-9:
        sys.stderr.write("REFUSED (rule 3, P-B): the y+ reader could not see the "
                         f"planted max {PLANT_YPLUS} on 'hull'; it returned {gb!r}. "
                         "A y+ from this reader is NOT evidence.\n")
        sys.exit(2)
    if yplus_from_dat(pb, "NOT_A_PATCH") is not None:
        sys.stderr.write("REFUSED (rule 3, P-B): the y+ reader returned a value for a "
                         "patch that is not in the file; its patch filter is inert.\n")
        sys.exit(2)
    out["P_B_yplus_reader"] = {"planted_max": PLANT_YPLUS, "returned": gb,
                               "absent_patch_returns": None, "verdict": "ARMED"}

    # ---- P-C : the age guard -------------------------------------------------
    base = os.path.join(scratch, "PLANT_C")
    def build(stale):
        import shutil as _sh
        if os.path.isdir(base):
            _sh.rmtree(base)
        for f in REQUIRED_FIELDS:
            _write(os.path.join(base, str(end_time), f), "x\n")
        time.sleep(0.02)
        for f in ("U", "p", "k", "omega", "nut"):
            _write(os.path.join(base, "0", f), "x\n")
        _write(os.path.join(base, "solve_rc"), "0\n")
        _write(os.path.join(base, "log.simpleFoam"),
               "".join(f"Time = {i}\nExecutionTime = {i}.0 s\n"
                       for i in range(1, end_time + 1)) + "End\n")
        if not stale:                    # make endTime fields NEWER than 0/U
            time.sleep(0.02)
            for f in REQUIRED_FIELDS:
                os.utime(os.path.join(base, str(end_time), f), None)
    build(stale=True)
    bad = check_completion(base, end_time, 1)
    if bad["clause_age_guard"]:
        sys.stderr.write("REFUSED (rule 3, P-C): the age guard PASSED a case whose "
                         "endTime fields are OLDER than 0/U.  It is inert.\n")
        sys.exit(2)
    build(stale=False)
    good = check_completion(base, end_time, 1)
    if not good["clause_age_guard"]:
        sys.stderr.write("REFUSED (rule 3, P-C): the age guard FAILED a case whose "
                         "endTime fields are correctly newer than 0/U.  It cannot "
                         "distinguish, so its verdict carries nothing.\n")
        sys.exit(2)
    out["P_C_age_guard"] = {"stale_case_reported_pass": bad["clause_age_guard"],
                            "fresh_case_reported_pass": good["clause_age_guard"],
                            "verdict": "ARMED"}
    return out


# ------------------------------------------------------------------- gates ---
def gate_w(case, end_time):
    """5.2 + 11.2.  UNARMED => BLOCKED, never PASS."""
    nutf = os.path.join(case, "0", "nut")
    arm_bc, bc = True, {}
    if not os.path.isfile(nutf):
        arm_bc = False
    else:
        txt = open(nutf, errors="replace").read()
        for p in WALL_PATCHES:
            m = re.search(re.escape(p) + r"\s*\{([^}]*)\}", txt)
            t = re.search(r"type\s+(\w+)\s*;", m.group(1)) if m else None
            bc[p] = t.group(1) if t else None
            if bc[p] != REQUIRED_WALL_NUT:
                arm_bc = False
    ydat = os.path.join(case, "postProcessing", "yPlus", "0", "yPlus.dat")
    meas = {p: yplus_from_dat(ydat, p) for p in WALL_PATCHES}
    logm = {p: yplus_from_log(os.path.join(case, "log.simpleFoam"), p)
            for p in WALL_PATCHES}
    armed = arm_bc and all(meas[p] is not None for p in WALL_PATCHES)
    res = {"arming": {"wall_nut_types": bc, "required": REQUIRED_WALL_NUT,
                      "yPlus_dat": ydat if os.path.isfile(ydat) else None},
           "measured_from_dat_min_max_avg": meas,
           "measured_from_log_max": logm,
           "ceiling": YPLUS_CEILING}
    if not armed:
        res["verdict"] = "BLOCKED"
        res["why"] = ("a gate armed by its own data passes when the data is missing; "
                      "11.2 fixes the unarmed verdict at BLOCKED.")
        return res
    worst = max(meas[p][1] for p in WALL_PATCHES)
    res["max_yPlus_over_wall_patches"] = worst
    res["verdict"] = "PASS" if worst < YPLUS_CEILING else "GATE FAIL"
    res["WHAT_WOULD_HAVE_FAILED_THIS"] = (
        f"any wall-patch y+ maximum >= {YPLUS_CEILING}, or any wall patch in 0/nut "
        f"carrying a boundary condition other than {REQUIRED_WALL_NUT}.")
    return res


def monitors(case, end_time):
    """S1 (rising residual) and S3 (the 500-iteration plateau REGRESSION)."""
    sdat = os.path.join(case, "postProcessing", "residuals", "0", "solverInfo.dat")
    out = {"solverInfo": sdat if os.path.isfile(sdat) else None}
    worst_rise = None
    for fld in ("p", "Ux", "U", "k", "omega"):
        s = initial_residual_series(sdat, fld)
        if not s or len(s) <= S1_WINDOW:
            continue
        a, b = s[-S1_WINDOW - 1][1], s[-1][1]
        out.setdefault("residual_last_and_500_back", {})[fld] = {"back": a, "last": b}
        if a > 0 and b > a:
            worst_rise = fld if worst_rise is None else worst_rise
    out["S1_rising_over_last_500"] = worst_rise
    out["S1_state"] = "RISING" if worst_rise else "NOT RISING"

    cdat = os.path.join(case, "postProcessing", "forceCoeffs", "0", "coefficient.dat")
    ser = cd_series(cdat)
    if not ser:
        out["S3_state"] = "BLOCKED"
        out["S3_why"] = "no coefficient.dat to regress; nothing was compared."
        return out, None
    win = ser[-PLATEAU_WINDOW:]
    if len(win) < PLATEAU_WINDOW:
        out["S3_state"] = "BLOCKED"
        out["S3_why"] = f"fewer than {PLATEAU_WINDOW} rows; the registered window is " \
                        "a regression, not a two-point difference (7, S3)."
        return out, ser[-1][1]
    n = len(win)
    mx = sum(t for t, _ in win) / n
    my = sum(v for _, v in win) / n
    sxx = sum((t - mx) ** 2 for t, _ in win)
    sxy = sum((t - mx) * (v - my) for t, v in win)
    slope = sxy / sxx if sxx > 0 else 0.0
    drift = slope * (win[-1][0] - win[0][0])
    frac = abs(drift) / abs(my) if my != 0 else math.inf
    out["S3_regression"] = {"window_iterations": PLATEAU_WINDOW,
                            "slope_per_iteration": slope,
                            "drift_over_window": drift, "mean_Cd": my,
                            "drift_fraction_of_mean": frac,
                            "threshold": PLATEAU_FRAC}
    out["S3_state"] = "PLATEAUED" if frac <= PLATEAU_FRAC else "NOT PLATEAUED"
    out["WHAT_WOULD_HAVE_FAILED_THIS"] = (
        f"a fitted drift over the final {PLATEAU_WINDOW} iterations exceeding "
        f"{PLATEAU_FRAC:.0%} of the window mean.  R1b's medium drifted -10.02 % per "
        "hundred iterations and its two-point comparator still called it PLATEAUED.")
    return out, win[-1][1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--level", required=True)
    ap.add_argument("--end-time", type=int, required=True)
    ap.add_argument("--ranks", type=int, required=True)
    ap.add_argument("--ct-reference", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    pl = plants(a.scratch, a.end_time)           # RULE 3, FIRST, ALWAYS

    if not os.path.isdir(a.case):
        sys.stderr.write(f"REFUSED: {a.case} is not a directory.\n"); sys.exit(2)
    with open(a.ct_reference) as f:
        ref = json.load(f)

    comp = check_completion(a.case, a.end_time, a.ranks)
    w = gate_w(a.case, a.end_time)
    mon, ct = monitors(a.case, a.end_time)

    band = ref["GATE_D2_BAND"]
    inside = (ct is not None and band["lo"] <= ct <= band["hi"])
    d2 = {
        "verdict": "NOT A RESULT",
        "CT_reported": ct,
        "CT_ref": ref["CT_ref"], "band": band,
        "inside_band_IF_A_TRIPLE_EXISTED": inside,
        "WHY_NOT_A_RESULT":
            "CLAUDE.md rule 5.  TWO LEVELS CANNOT GIVE AN OBSERVED ORDER, so under "
            "SUBOFF_A1b there is no triple by construction and no GCI, observed order or "
            "Richardson extrapolation is computed anywhere.  Under SUBOFF A1 the reason "
            "was different and equally final: Gate D2 grades the FINEST LEVEL OF A **CONVERGING "
            "ROACHE TRIPLE**.  SUBOFF A1 has no triple: Gate M has FAILED at L1 on "
            "the minimum-determinant limb (8.6227045e-04 against a floor of 1.0e-03, "
            "one cell in 3,268,613, invariant to partitioning AND to alignment -- "
            "pre-registration 12.8), and L3 is BLOCKED on RAM (4.1 of the status "
            "table).  A row whose triple is not CONVERGING is NOT A RESULT whatever "
            "its value.  The number above is REPORTED because 5.3 requires it "
            "reported; it is NOT graded and this comparator HAS NO CODE PATH that "
            "turns it into a PASS or a GATE FAIL.",
        "WHAT_WOULD_HAVE_FAILED_THIS":
            "nothing this run can produce.  The gate is unreachable until a "
            "CONVERGING triple of admissible levels exists, which is the "
            "cfd-supervisor's family ruling and not this comparator's.",
    }
    if comp["ok"] is not True:
        d2["ALSO"] = "the run did not clear the completion rule, which is itself a " \
                     "BLOCKED arming condition for D2 (11.2)."

    rep = {
        "case": os.path.abspath(a.case), "level": a.level,
        "graded_utc": datetime.datetime.now(datetime.timezone.utc)
                      .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule3_plants": pl,
        "COMPLETION": comp,
        "GATE_W": w,
        "MONITORS": mon,
        "GATE_D2": d2,
        "READ_ONLY": "this comparator wrote nothing into the case it graded.",
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps({"level": a.level,
                      "COMPLETION_ok": comp["ok"],
                      "GATE_W": w["verdict"],
                      "S1": mon.get("S1_state"), "S3": mon.get("S3_state"),
                      "GATE_D2": d2["verdict"], "CT_reported": ct,
                      "plants": {k: v["verdict"] for k, v in pl.items()}}, indent=2))


if __name__ == "__main__":
    main()
