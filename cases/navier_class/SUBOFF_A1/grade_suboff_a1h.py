#!/usr/bin/env python3
"""SUBOFF A1h -- FULL-DOMAIN MATCHED-REYNOLDS DRIFT SWEEP.  THE GRADING PATH.

This file is the comparator named in
`verification/campaign/SUBOFF_A1h_FULL_DOMAIN_DRIFT_SWEEP_PREREGISTRATION.md` §8, and
it is fixed at that file's freezing commit.  A grade produced by any other path is
NOT A RESULT.  Before its output is believed, hash this file against its committed
blob (`scripts/check_comparator_freeze.py`): the frozen file must BE the file that ran.

WHAT IT DOES
    Reads the seven solves at beta = -12 -8 -4 0 +4 +8 +12, enforces the strict
    completion rule (standing rule 4) on ALL of them before reading ANY force,
    extracts lateral force and yaw moment from the `forces` function object,
    non-dimensionalises per Roddy's page 3, fits Y_v' and N_v' by least squares over
    |beta| <= 8, GATES Y_v' against the frozen band, REPORTS N_v' ungraded, and emits
    one verdict from the fixed vocabulary:
        PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING

WHAT IT REFUSES TO DO (exit 2, never a degraded answer)
    - run before its four plants have been read back FROM DISK (standing rule 3)
    - read a force from a case that has not passed every completion clause
    - fit over fewer than the five registered points
    - write anything inside a case it grades

WHY THE PLANTS ARE NOT A FORMALITY -- two blind readers, both found 2026-09-12/13:
    (1) OpenFOAM v2606 `postProcess -func yPlus` returned ZERO on 53 of 53 patch
        readings, exiting clean, while `-postProcess` returned real values on the
        same input.
    (2) This act's own `zmin` reader, a greedy sed capture, reported that NO mesh in
        the lab had a negative zmin.  A planted log carrying zmin = -2.9927629 caught
        it: the reader still said "not-negative".  It had never once read a zmin.
        Repaired, the same sweep found 705 of 1,585 checkMesh logs with a negative
        zmin.  THE FIRST SWEEP'S CLEAN ZERO WAS FALSE.
    Assume every reader below is blind until a plant proves otherwise.

    P-A  the force reader is handed a synthetic force.dat carrying a DECOY total_z at
         t = 1 and the planted total_z at endTime, and must return the endTime one.
    P-B  the same, in the moment channel, on total_y.
    P-C  the completion checker is handed a case whose endTime fields are OLDER than
         0/U and must report the age guard FAILED; the mtime is then corrected and it
         must report PASS.  A guard that cannot fail is inert.
    P-D  THE PLANT THIS ACT TURNS ON.  A whole synthetic seven-point sweep with an
         exactly known slope is driven end to end through the fit and the gate --
         once with a slope OUTSIDE the band, which must return GATE FAIL, and once
         INSIDE, which must return PASS.  P-A..P-C prove the file readers see.  Only
         P-D proves the DERIVATIVE and THE GATE see.  A gate that cannot fail is not
         a gate.
    P-E  the normalisation constants and THE SIGN, checked against literals computed
         OUTSIDE this file from the pre-registration's own printed numbers.  The
         self-referential spelling -- compare nondim(x) against -x/Q_AREA -- passes
         for any Q_AREA and for a flipped sign, and would have caught nothing.

Author: cfd lab-lane, 2026-09-13.
"""

import argparse
import json
import math
import os
import re
import shutil
import sys
import time

if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O; the asserts are the point.\n")
    sys.exit(2)

# Repository root from THIS file's location (cases/navier_class/SUBOFF_A1/), never
# from cwd -- the grader is run detached by the queue runner from the case directory,
# and a cwd-derived root would silently resolve into the run tree.
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# ----------------------------------------------------------- frozen constants --
# Every number below is quoted from the pre-registration and may not be changed here.
PREREG = "verification/campaign/SUBOFF_A1h_FULL_DOMAIN_DRIFT_SWEEP_PREREGISTRATION.md"

U_INF       = 3.343886          # m/s, 6.5 knots exactly                    (prereg §1)
L_BP        = 4.2608602         # m, length between perpendiculars          (prereg §4)
Q_AREA      = 0.5 * U_INF ** 2 * L_BP ** 2      # 101.500341, rho = 1       (prereg §4)
Q_VOL       = 0.5 * U_INF ** 2 * L_BP ** 3      # 432.478763, rho = 1       (prereg §4)

# RODDY'S EXPERIMENTAL MEASUREMENTS.  NOT ANYTHING THIS LABORATORY COMPUTED.
# Roddy 1990, DTRC/SHD-1298-08, Table 4, report page 19, "Horizontal Plane",
# column printed `Config 4 / B.H. + Sail` -- the hull-with-fairwater body, named by
# its geometry and never by a bare number.  Read out of a printed table.  No reader
# may cite either as a Certonomous result.
RODDY_YV    = -0.023008         # EXPERIMENT, gated at +/-4%                (prereg §5)
RODDY_NV    = -0.015534         # EXPERIMENT, REPORTED NOT GRADED           (prereg §5)
YV_BAND     = (-0.023928, -0.022088)            # +/-4%, frozen             (prereg §5)

BETAS       = (-12, -8, -4, 0, 4, 8, 12)                                  # prereg §3
FIT_BETAS   = tuple(b for b in BETAS if abs(b) <= 8)      # the five fitted points
CASE_DIRS   = {-12: "BETA_m12", -8: "BETA_m08", -4: "BETA_m04", 0: "BETA_p00",
               4: "BETA_p04", 8: "BETA_p08", 12: "BETA_p12"}             # prereg §9
RUN_ROOT    = "verification/runs/navier_class/SUBOFF_A1H_DRIFT"          # prereg §9

END_TIME    = 3000
DELTA_T     = 1.0
# The INCOMPRESSIBLE set, registered in prereg §8.1.  Rule 4's named list
# (T U p_rgh alphat nut k omega phi) is the THERMAL family's; this case has no
# temperature.  Same list as grade_suboff_a1.py:59 for this family.
REQUIRED_FIELDS = ("p", "U", "k", "omega", "nut", "phi")

FO_TOTAL    = "forces"          # patches (hull sail)
FO_HULL     = "forcesHull"      # split, reported not gated
FO_SAIL     = "forcesSail"

SYM_TOL     = 1.0e-4            # |Y'(0)| and |N'(0)| ceiling               (prereg §4.3)
PLATEAU_WIN = 500               # final-iteration window                   (prereg §8.1a)
PLATEAU_REL = 0.01              # drift <= 1% of |Y'| at endTime           (prereg §8.1a)
PLATEAU_ABS = 1.0e-4            # absolute floor, used at beta = 0         (prereg §8.1a)

# ---- rule-3 plant magnitudes.  House constant 1.234e-03 (T3_runs/analyse_t3.py).
PLANT_FZ        = 1.234e-03
PLANT_FZ_DECOY  = 5.678e-03
PLANT_MY        = -9.876e-04
PLANT_MY_DECOY  = 4.321e-04
# P-D slopes, chosen so one is unambiguously outside the band and one inside it.
PLANT_SLOPE_OUT = -0.030000     # outside [-0.023928, -0.022088]
PLANT_SLOPE_IN  = -0.023008     # Roddy's own value, squarely inside


class Refuse(Exception):
    """Raised anywhere a reader cannot be shown to see.  Always becomes exit 2."""


def refuse(msg):
    raise Refuse(msg)


# ------------------------------------------------------------------ readers ---
_NUMS = re.compile(r"[-+0-9.eEnaN]+")


def read_force_dat(path):
    """One OpenFOAM forces-FO .dat -> {time: (tot_x, tot_y, tot_z)}.

    Columns, verified against this box's own output
    (verification/runs/navier_class/MRF/coarse/postProcessing/impellerForces/0/force.dat):
        Time  total_x total_y total_z  pressure_xyz  viscous_xyz
    Parentheses are stripped before splitting, so the bracketed spelling some builds
    emit -- ((fx fy fz) (px py pz) (vx vy vz)) -- lands on the same column indices.
    """
    if not os.path.isfile(path):
        refuse(f"force/moment file absent: {path}")
    out = {}
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.replace("(", " ").replace(")", " ").split()
            if len(parts) < 4:
                continue
            try:
                t = float(parts[0])
                v = (float(parts[1]), float(parts[2]), float(parts[3]))
            except ValueError:
                continue
            if any(math.isnan(x) or math.isinf(x) for x in v):
                refuse(f"non-finite force at t={t} in {path}")
            out[t] = v
    if not out:
        refuse(f"no data rows parsed from {path}")
    return out


def fo_series(case, fo_name, leaf):
    """Union a function object's output across restart time-directories.

    A resumed run leaves postProcessing/<fo>/0/, /60/, ... .  Rows are collected per
    directory; where a time appears in more than one, THE DIRECTORY WITH THE LARGEST
    START TIME WINS -- it is the run that actually produced the final answer -- and
    every competing value is reported so a reader SEES a disagreement rather than
    being protected from it.
    """
    root = os.path.join(case, "postProcessing", fo_name)
    if not os.path.isdir(root):
        refuse(f"function object output absent: {root}")
    starts = []
    for d in os.listdir(root):
        p = os.path.join(root, d, leaf)
        if os.path.isfile(p):
            try:
                starts.append((float(d), p))
            except ValueError:
                continue
    if not starts:
        refuse(f"no {leaf} under {root}")
    starts.sort()
    merged, provenance, conflicts = {}, {}, {}
    for _st, p in starts:                       # ascending: later dirs overwrite
        for t, v in read_force_dat(p).items():
            if t in merged and merged[t] != v:
                conflicts.setdefault(t, []).append(
                    {"from": provenance[t], "value": merged[t]})
            merged[t] = v
            provenance[t] = p
    return merged, provenance, conflicts


# ------------------------------------------------------- completion (rule 4) --
def check_completion(case, end_time=END_TIME):
    """Standing rule 4, every clause.  `ok` is the AND of the six."""
    r = {"case": case}
    rcp = os.path.join(case, "solve_rc")
    r["rc"] = int(open(rcp).read().strip()) if os.path.isfile(rcp) else None
    r["clause_rc_zero"] = (r["rc"] == 0)

    # Distinct PHYSICS steps unioned across every log segment, never a line count:
    # a resumed run re-runs the iterations between the checkpoint and the kill, and
    # a line count credits them twice (measured on SOLVE_L2: 3,002 lines, 3,000
    # steps).  Sanaa 2026-08-26 and 2026-09-12: bookkeeping never voids physics.
    sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
    import solver_log_set as _sls
    sc = _sls.scan(case, "simpleFoam", end_time=end_time, delta_t=DELTA_T)
    r["clause_end_line"] = sc["end_line"]
    r["clause_last_eq_endTime"] = sc["clause_last_eq_endTime"]
    r["clause_exec_count"] = sc["clause_exec_count"]
    r["last_Time"] = sc["last_time"]
    r["n_steps_distinct"] = sc["n_steps"]
    r["n_exec_lines_raw_BOOKKEEPING"] = sc["n_exec_lines_raw"]
    r["n_log_segments"] = sc["n_segments"]
    r["resumed"] = sc["resumed"]

    td = os.path.join(case, str(end_time))
    r["endTime_dir"] = td if os.path.isdir(td) else None
    present = sorted(os.listdir(td)) if r["endTime_dir"] else []
    r["fields_missing"] = [f for f in REQUIRED_FIELDS if f not in present]
    r["clause_fields"] = not r["fields_missing"]

    # THE AGE GUARD.  0/U is touched last at launch and so dates the run that was
    # allowed to produce the answer; every endTime field must be strictly newer.
    anchor = os.path.join(case, "0", "U")
    r["age_anchor"] = anchor if os.path.isfile(anchor) else None
    if r["age_anchor"] and r["endTime_dir"]:
        t0 = os.path.getmtime(anchor)
        ages = {f: os.path.getmtime(os.path.join(td, f)) - t0
                for f in REQUIRED_FIELDS if f in present}
        r["age_margins_s"] = ages
        r["clause_age_guard"] = bool(ages) and all(v > 0 for v in ages.values())
    else:
        r["age_margins_s"] = {}
        r["clause_age_guard"] = False

    r["ok"] = all([r["clause_rc_zero"], r["clause_end_line"],
                   r["clause_last_eq_endTime"], r["clause_exec_count"],
                   r["clause_fields"], r["clause_age_guard"]])
    return r


# ------------------------------------------------------------- the physics ----
def nondim(fz, my):
    """Mesh-frame force/moment -> Roddy's SNAME-frame coefficients.

    Derived in prereg §4.1 and not re-derived here.  Mesh x is bow-to-stern, y is up
    (the sail sits at +y), z is lateral; SNAME body axes are x forward, y starboard,
    z down, so x_b = -x_mesh, z_b = -y_mesh and right-handedness forces y_b = -z_mesh.
    Hence Y_b = -F_z,mesh and N_b = -M_y,mesh.
    """
    return (-fz / Q_AREA, -my / Q_VOL)


def lsq(xs, ys):
    """Ordinary least squares slope and intercept.  Refuses a degenerate abscissa."""
    n = len(xs)
    if n < 2:
        refuse(f"least squares needs >= 2 points, got {n}")
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0.0:
        refuse("least squares abscissa is degenerate (all beta identical)")
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    return slope, my - slope * mx


def plateau(series_times, series_y, y_end, window=PLATEAU_WIN):
    """Prereg §8.1a.  Total drift of Y' over the final `window` iterations."""
    pairs = sorted((t, v) for t, v in zip(series_times, series_y))
    tail = pairs[-window:]
    if len(tail) < window:
        return {"verdict": "NOT A RESULT",
                "reason": f"only {len(tail)} iterations available, need {window}"}
    slope, _ = lsq([p[0] for p in tail], [p[1] for p in tail])
    drift = abs(slope) * (tail[-1][0] - tail[0][0])
    ceiling = max(PLATEAU_REL * abs(y_end), PLATEAU_ABS)
    return {"verdict": "PASS" if drift <= ceiling else "NOT A RESULT",
            "drift": drift, "ceiling": ceiling,
            "window_iters": len(tail), "slope_per_iter": slope}


def grade_sweep(points):
    """points: {beta: {"Yp":…, "Np":…}} -> the verdict.  No I/O; P-D drives this."""
    missing = [b for b in FIT_BETAS if b not in points]
    if missing:
        return {"verdict": "NOT A RESULT",
                "reason": f"fitted points missing: {missing}; there is no fit over "
                          f"fewer than the five registered points"}
    v = [math.sin(math.radians(b)) for b in FIT_BETAS]
    yv, y0 = lsq(v, [points[b]["Yp"] for b in FIT_BETAS])
    nv, n0 = lsq(v, [points[b]["Np"] for b in FIT_BETAS])
    out = {"Y_v_prime": yv, "N_v_prime": nv,
           "Y_intercept": y0, "N_intercept": n0,
           "roddy_Y_v_prime_EXPERIMENT": RODDY_YV,
           "roddy_N_v_prime_EXPERIMENT": RODDY_NV,
           "band": list(YV_BAND),
           "N_v_prime_status": "REPORTED, NOT GRADED (A1e Addendum 1; the extension "
                               "test splits and N_v' fails it 13.8% IN OUR FAVOUR, so "
                               "gating it would fit a gate to a known-favourable ground)",
           # Set HERE, where `out` is built, so that EVERY return path carries it --
           # a symmetry or sign return is exactly when a reader most wants to see how
           # far off the value was, and setting it only on the band branch would hide
           # it precisely then.
           "Y_v_prime_pct_of_roddy": 100.0 * (yv - RODDY_YV) / abs(RODDY_YV),
           "N_v_prime_pct_of_roddy": 100.0 * (nv - RODDY_NV) / abs(RODDY_NV)}

    # prereg §4.3 -- the symmetry check the half mesh could never have provided.
    if 0 in points:
        out["symmetry_Yp_at_beta0"] = points[0]["Yp"]
        out["symmetry_Np_at_beta0"] = points[0]["Np"]
        if abs(points[0]["Yp"]) > SYM_TOL or abs(points[0]["Np"]) > SYM_TOL:
            out["verdict"] = "GATE FAIL"
            out["reason"] = (f"beta=0 symmetry: |Y'|={abs(points[0]['Yp']):.3e}, "
                             f"|N'|={abs(points[0]['Np']):.3e}, ceiling {SYM_TOL:.1e}. "
                             f"THE MIRROR IS NOT SYMMETRIC -- this is a GATE FAIL on "
                             f"the mesh, not on the physics.")
            return out

    # prereg §4.2 -- the sign clause, registered before any number existed.
    if yv >= 0.0:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = (f"Y_v' = {yv:+.6f} >= 0 is ANTI-DAMPING. That is not a bad "
                         f"answer to the physics question, it is evidence the sign "
                         f"convention (prereg §4.1) or the solve is inverted. "
                         f"Registered as NOT A RESULT before compute (§4.2) so it "
                         f"could not be reached for as an escape from a failing gate.")
        return out

    lo, hi = YV_BAND
    if lo <= yv <= hi:
        out["verdict"] = "PASS"
        out["reason"] = f"Y_v' = {yv:.6f} inside the frozen band [{lo}, {hi}]"
    else:
        out["verdict"] = "GATE FAIL"
        out["reason"] = f"Y_v' = {yv:.6f} outside the frozen band [{lo}, {hi}]"
    return out


# ------------------------------------------------------------ rule-3 plants ---
def _w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def _synthetic_dat(kind, at_end, decoy, end_time=END_TIME):
    """A force.dat/moment.dat in this box's exact v2606 layout."""
    head = (f"# {kind}\n# CofR          : (2.013 0 0)\n#\n"
            "# Time          \ttotal_x total_y total_z\tpressure_x pressure_y "
            "pressure_z\tviscous_x viscous_y viscous_z\n")
    rows = []
    for t, trip in ((1, decoy), (end_time, at_end)):
        rows.append("%-16d %.8e %.8e %.8e %.8e %.8e %.8e %.8e %.8e %.8e\n"
                    % (t, trip[0], trip[1], trip[2], 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    return head + "".join(rows)


def plant_a_and_b(scratch):
    """P-A the force reader, P-B the moment reader.  Decoy at t=1, plant at endTime."""
    out = {}
    c = os.path.join(scratch, "PLANT_AB")
    _w(os.path.join(c, "postProcessing", FO_TOTAL, "0", "force.dat"),
       _synthetic_dat("Force", (0.0, 0.0, PLANT_FZ), (0.0, 0.0, PLANT_FZ_DECOY)))
    _w(os.path.join(c, "postProcessing", FO_TOTAL, "0", "moment.dat"),
       _synthetic_dat("Moment", (0.0, PLANT_MY, 0.0), (0.0, PLANT_MY_DECOY, 0.0)))

    f, _prov, _cf = fo_series(c, FO_TOTAL, "force.dat")
    got = f.get(float(END_TIME), (None, None, None))[2]
    if got is None or abs(got - PLANT_FZ) > 1e-15:
        refuse(f"rule 3, P-A: the FORCE reader is blind. Planted total_z={PLANT_FZ} "
               f"at t={END_TIME} behind a decoy {PLANT_FZ_DECOY} at t=1; it returned "
               f"{got!r}. A zero from a reader not shown able to see a non-zero is "
               f"not evidence.")
    out["P_A_force_reader"] = {"planted": PLANT_FZ, "decoy_at_t1": PLANT_FZ_DECOY,
                               "returned": got, "verdict": "PASS"}

    m, _prov, _cf = fo_series(c, FO_TOTAL, "moment.dat")
    gotm = m.get(float(END_TIME), (None, None, None))[1]
    if gotm is None or abs(gotm - PLANT_MY) > 1e-15:
        refuse(f"rule 3, P-B: the MOMENT reader is blind. Planted total_y={PLANT_MY} "
               f"at t={END_TIME} behind a decoy {PLANT_MY_DECOY}; it returned {gotm!r}.")
    out["P_B_moment_reader"] = {"planted": PLANT_MY, "decoy_at_t1": PLANT_MY_DECOY,
                                "returned": gotm, "verdict": "PASS"}

    # ---- P-E : the constants and the SIGN, against INDEPENDENT LITERALS --------
    # The obvious spelling of this check -- compare nondim(x) against -x/Q_AREA --
    # is SELF-REFERENTIAL: it recomputes the thing under test, so it passes for any
    # Q_AREA and for a flipped sign.  It would have caught nothing.  The literals
    # below are computed OUTSIDE this file from the pre-registration's own printed
    # constants (§4: L_BP = 4.2608602, U = 3.343886, 0.5*rho*U^2*L^2 = 101.500341,
    # 0.5*rho*U^2*L^3 = 432.478763) and hard-coded here, so a mutation of U_INF,
    # L_BP, Q_AREA, Q_VOL or the sign in nondim() fires this refusal.
    if abs(Q_AREA - 101.500341) > 1e-6 or abs(Q_VOL - 432.478763) > 1e-6:
        refuse(f"rule 3, P-E: normalisation constants do not match the frozen "
               f"pre-registration §4. Q_AREA={Q_AREA!r} (frozen 101.500341), "
               f"Q_VOL={Q_VOL!r} (frozen 432.478763).")
    yp, np_ = nondim(got, gotm)
    exp_yp, exp_np = -1.215759464292e-05, 2.283580340844e-06
    if abs(yp - exp_yp) > 1e-17 or abs(np_ - exp_np) > 1e-18:
        refuse(f"rule 3, P-E: the non-dimensionalisation is wrong or its SIGN is "
               f"flipped. Planted F_z={PLANT_FZ}, M_y={PLANT_MY} must give "
               f"Y'={exp_yp:.12e} and N'={exp_np:.12e}; it returned Y'={yp:.12e}, "
               f"N'={np_:.12e}. A sign error here flips a GATED value.")
    out["P_E_constants_and_sign"] = {
        "Q_AREA": Q_AREA, "Q_VOL": Q_VOL, "Yp": yp, "Np": np_,
        "expected_Yp_independent_literal": exp_yp,
        "expected_Np_independent_literal": exp_np, "verdict": "PASS"}
    return out


def plant_c(scratch):
    """P-C the age guard.  It must FAIL a stale case and PASS a fresh one."""
    res = {}
    for stale in (True, False):
        c = os.path.join(scratch, "PLANT_C_" + ("stale" if stale else "fresh"))
        if os.path.isdir(c):
            shutil.rmtree(c)
        os.makedirs(os.path.join(c, "0"))
        os.makedirs(os.path.join(c, str(END_TIME)))
        _w(os.path.join(c, "solve_rc"), "0\n")
        _w(os.path.join(c, "log.simpleFoam"),
           "".join(f"Time = {i}\nExecutionTime = {float(i)} s  ClockTime = {i} s\n\n"
                   for i in range(1, END_TIME + 1)) + "End\n")
        for f in REQUIRED_FIELDS:                      # endTime fields first ...
            _w(os.path.join(c, str(END_TIME), f), "x\n")
        time.sleep(0.02)
        _w(os.path.join(c, "0", "U"), "x\n")           # ... then 0/U -> STALE
        if not stale:                                  # correct it: fields newest
            time.sleep(0.02)
            for f in REQUIRED_FIELDS:
                os.utime(os.path.join(c, str(END_TIME), f), None)
        r = check_completion(c)
        res["stale" if stale else "fresh"] = {
            "clause_age_guard": r["clause_age_guard"], "ok": r["ok"],
            "clause_end_line": r["clause_end_line"],
            "clause_exec_count": r["clause_exec_count"]}
        if stale and r["clause_age_guard"]:
            refuse("rule 3, P-C: the AGE GUARD PASSED a case whose endTime fields are "
                   "OLDER than 0/U. It is inert.")
        if (not stale) and not r["clause_age_guard"]:
            refuse("rule 3, P-C: the AGE GUARD FAILED a case whose endTime fields are "
                   "correctly newer than 0/U. It cannot distinguish, so it cannot "
                   "certify.")
        if (not stale) and not r["ok"]:
            refuse(f"rule 3, P-C: a fully correct synthetic case did not satisfy the "
                   f"completion rule: {r}. The checker cannot pass anything.")
    res["verdict"] = "PASS"
    return res


def plant_d(scratch):
    """P-D.  The whole fit-and-gate path, driven on a sweep of exactly known slope.

    This is the plant this act turns on.  P-A..P-C prove the FILE readers see; only
    this proves the DERIVATIVE and THE GATE see -- and it proves the gate in BOTH
    directions, because a gate that cannot fail is not a gate.
    """
    res = {}
    for tag, slope, want in (("outside_band", PLANT_SLOPE_OUT, "GATE FAIL"),
                             ("inside_band", PLANT_SLOPE_IN, "PASS")):
        pts = {}
        for b in BETAS:
            vprime = math.sin(math.radians(b))
            pts[b] = {"Yp": slope * vprime, "Np": RODDY_NV * vprime}
        g = grade_sweep(pts)
        if g["verdict"] != want:
            refuse(f"rule 3, P-D ({tag}): a sweep built with slope {slope} returned "
                   f"verdict {g['verdict']!r} (Y_v'={g.get('Y_v_prime')!r}); "
                   f"{want!r} was required. The fit or the gate is blind.")
        if abs(g["Y_v_prime"] - slope) > 1e-12:
            refuse(f"rule 3, P-D ({tag}): the fit recovered Y_v'={g['Y_v_prime']!r} "
                   f"from a sweep built with slope {slope}. The derivative channel "
                   f"does not read what is in it.")
        res[tag] = {"planted_slope": slope, "recovered": g["Y_v_prime"],
                    "verdict_returned": g["verdict"], "verdict_required": want}

    # And the sign clause, which must also be able to fire.
    pts = {b: {"Yp": 0.02 * math.sin(math.radians(b)),
               "Np": RODDY_NV * math.sin(math.radians(b))} for b in BETAS}
    g = grade_sweep(pts)
    if g["verdict"] != "NOT A RESULT":
        refuse(f"rule 3, P-D (sign): a POSITIVE Y_v' returned {g['verdict']!r}, not "
               f"NOT A RESULT. Prereg §4.2 is not implemented.")
    res["sign_clause"] = {"planted_slope": 0.02, "verdict": g["verdict"]}

    # And the symmetry clause.
    pts = {b: {"Yp": RODDY_YV * math.sin(math.radians(b)) + 1.0,
               "Np": RODDY_NV * math.sin(math.radians(b))} for b in BETAS}
    g = grade_sweep(pts)
    if g["verdict"] != "GATE FAIL":
        refuse(f"rule 3, P-D (symmetry): a sweep with |Y'(0)|=1.0 returned "
               f"{g['verdict']!r}, not GATE FAIL. Prereg §4.3 is not implemented.")
    res["symmetry_clause"] = {"planted_Yp_at_0": 1.0, "verdict": g["verdict"]}

    # And the refusal to fit a short sweep.  ADDED AFTER A MUTATION TEST: a mutant
    # that deleted the missing-point check survived every other plant, because
    # nothing ever handed grade_sweep an incomplete sweep.
    for drop in FIT_BETAS:
        pts = {b: {"Yp": RODDY_YV * math.sin(math.radians(b)),
                   "Np": RODDY_NV * math.sin(math.radians(b))}
               for b in BETAS if b != drop}
        g = grade_sweep(pts)
        if g["verdict"] != "NOT A RESULT":
            refuse(f"rule 3, P-D (short sweep): a sweep MISSING the beta={drop} point "
                   f"returned {g['verdict']!r}, not NOT A RESULT. The comparator would "
                   f"silently fit four points and grade the result.")
    res["short_sweep_refusal"] = {"dropped_each_of": list(FIT_BETAS),
                                  "verdict": "NOT A RESULT on every drop"}
    res["verdict"] = "PASS"
    return res


def plant_f():
    """P-F.  The plateau gate (prereg §8.1a), in BOTH directions and on a short series.

    ADDED AFTER A MUTATION TEST FOUND IT UNPLANTED.  A mutant that deleted the
    short-series guard survived every other plant and returned rc=0, because with no
    real cases on disk nothing ever reached plateau().  An UNPLANTED GATE IS A BLIND
    READER THAT HAS SIMPLY NOT BEEN ASKED YET.
    """
    res = {}
    y_end = RODDY_YV
    ts = list(range(1, PLATEAU_WIN + 1))

    flat = [y_end] * PLATEAU_WIN
    g = plateau(ts, flat, y_end)
    if g["verdict"] != "PASS":
        refuse(f"rule 3, P-F: a PERFECTLY FLAT series returned {g['verdict']!r}. "
               f"The plateau test cannot pass anything.")
    res["flat"] = {"verdict": g["verdict"], "drift": g["drift"]}

    # A drift of exactly 10x the ceiling across the window.
    ceiling = max(PLATEAU_REL * abs(y_end), PLATEAU_ABS)
    per = 10.0 * ceiling / (PLATEAU_WIN - 1)
    ramp = [y_end + per * (t - 1) for t in ts]
    g = plateau(ts, ramp, y_end)
    if g["verdict"] != "NOT A RESULT":
        refuse(f"rule 3, P-F: a series drifting 10x the ceiling returned "
               f"{g['verdict']!r}, not NOT A RESULT. The plateau gate cannot fail, "
               f"so it is not a gate.")
    res["drifting"] = {"verdict": g["verdict"], "drift": g["drift"],
                       "ceiling": g["ceiling"]}

    g = plateau(ts[:PLATEAU_WIN - 1], flat[:PLATEAU_WIN - 1], y_end)
    if g["verdict"] != "NOT A RESULT":
        refuse(f"rule 3, P-F: a series ONE ITERATION SHORT of the {PLATEAU_WIN}-"
               f"iteration window returned {g['verdict']!r}. The window guard is "
               f"absent, so a truncated run would be graded as plateaued.")
    res["short_window"] = {"verdict": g["verdict"]}
    res["verdict"] = "PASS"
    return res


def _synthetic_case(c, beta, slope, end_time=END_TIME, complete=True):
    """One fully-formed synthetic run: log, rc, endTime fields, forces, moments."""
    if os.path.isdir(c):
        shutil.rmtree(c)
    os.makedirs(os.path.join(c, "0"))
    os.makedirs(os.path.join(c, str(end_time)))
    if complete:
        _w(os.path.join(c, "solve_rc"), "0\n")
    _w(os.path.join(c, "log.simpleFoam"),
       "".join(f"Time = {i}\nExecutionTime = {float(i)} s  ClockTime = {i} s\n\n"
               for i in range(1, end_time + 1)) + "End\n")

    vprime = math.sin(math.radians(beta))
    fz = -(slope * vprime) * Q_AREA          # invert nondim: Y' = -F_z / Q_AREA
    my = -(RODDY_NV * vprime) * Q_VOL
    head = ("# Force\n# CofR          : (2.013 0 0)\n#\n# Time\ttotal_x total_y "
            "total_z\tpressure\tviscous\n")
    rows_f, rows_m = [], []
    for t in range(end_time - PLATEAU_WIN + 1, end_time + 1):   # flat -> plateaued
        rows_f.append("%-10d %.10e %.10e %.10e %.1e %.1e %.1e %.1e %.1e %.1e\n"
                      % (t, 0.0, 0.0, fz, 0, 0, 0, 0, 0, 0))
        rows_m.append("%-10d %.10e %.10e %.10e %.1e %.1e %.1e %.1e %.1e %.1e\n"
                      % (t, 0.0, my, 0.0, 0, 0, 0, 0, 0, 0))
    _w(os.path.join(c, "postProcessing", FO_TOTAL, "0", "force.dat"),
       head + "".join(rows_f))
    _w(os.path.join(c, "postProcessing", FO_TOTAL, "0", "moment.dat"),
       head.replace("# Force", "# Moment") + "".join(rows_m))

    _w(os.path.join(c, "0", "U"), "x\n")     # the age anchor, written FIRST
    time.sleep(0.01)
    for f in REQUIRED_FIELDS:                # endTime fields NEWER than 0/U
        _w(os.path.join(c, str(end_time), f), "x\n")


def plant_g(scratch):
    """P-G.  THE WHOLE COMPARATOR, END TO END, ON A SYNTHETIC RUN ROOT ON DISK.

    ADDED AFTER A MUTATION TEST.  Two mutants -- one that ignored the completion
    result entirely, one that turned a missing force file into an empty dict --
    survived every other plant and exited 0, because with no cases on disk the run
    never reached the code they broke.  A COMPARATOR EXERCISED ONLY ON AN EMPTY
    DIRECTORY HAS NOT BEEN EXERCISED.

    Drives grade_run_root -- the same function main() calls, not a copy of it.
    """
    res = {}
    root = os.path.join(scratch, "PLANT_G_root")
    if os.path.isdir(root):
        shutil.rmtree(root)
    for b in BETAS:
        _synthetic_case(os.path.join(root, CASE_DIRS[b]), b, PLANT_SLOPE_IN)
    r = grade_run_root(root)
    if r.get("verdict") != "PASS":
        refuse(f"rule 3, P-G: a complete synthetic sweep built at the in-band slope "
               f"{PLANT_SLOPE_IN} returned {r.get('verdict')!r} "
               f"({r.get('reason')!r}). The comparator cannot grade a good sweep.")
    if abs(r["Y_v_prime"] - PLANT_SLOPE_IN) > 1e-9:
        refuse(f"rule 3, P-G: end to end, the planted slope {PLANT_SLOPE_IN} came "
               f"back as {r['Y_v_prime']!r}. The READ-AND-FIT path does not carry "
               f"what was written to disk.")
    res["complete_sweep"] = {"verdict": r["verdict"], "planted": PLANT_SLOPE_IN,
                             "recovered": r["Y_v_prime"]}

    # Now break ONE fitted point's completion: the verdict must fall to NOT A RESULT.
    os.remove(os.path.join(root, CASE_DIRS[-4], "solve_rc"))
    r2 = grade_run_root(root)
    if r2.get("verdict") != "NOT A RESULT":
        refuse(f"rule 3, P-G: removing solve_rc from the beta=-4 point left the "
               f"verdict at {r2.get('verdict')!r}. THE COMPLETION RULE IS NOT "
               f"ENFORCED -- an unfinished run would be graded.")
    res["broken_completion"] = {"broke": "beta=-4 solve_rc removed",
                                "verdict": r2["verdict"]}

    # And a missing force file must REFUSE, not read as empty.
    shutil.rmtree(os.path.join(root, CASE_DIRS[-4]))
    _synthetic_case(os.path.join(root, CASE_DIRS[-4]), -4, PLANT_SLOPE_IN)
    os.remove(os.path.join(root, CASE_DIRS[-4], "postProcessing", FO_TOTAL,
                           "0", "force.dat"))
    try:
        r3 = grade_run_root(root)
        refuse(f"rule 3, P-G: a MISSING force.dat did not refuse; the run returned "
               f"{r3.get('verdict')!r}. Refuse rather than degrade.")
    except Refuse as e:
        if "force/moment file absent" not in str(e) and "no " not in str(e):
            raise
        res["missing_force_file"] = {"verdict": "REFUSED, as required"}

    shutil.rmtree(root)
    res["verdict"] = "PASS"
    return res


def plants(scratch):
    """RULE 3, FIRST, ALWAYS.  Nothing real is opened until all seven have passed."""
    os.makedirs(scratch, exist_ok=True)
    out = {}
    out.update(plant_a_and_b(scratch))
    out["P_C_age_guard"] = plant_c(scratch)
    out["P_D_fit_and_gate"] = plant_d(scratch)
    out["P_F_plateau_gate"] = plant_f()
    out["P_G_end_to_end"] = plant_g(scratch)
    return out


# ------------------------------------------------ the whole path, in one place --
def grade_run_root(run_root, end_time=END_TIME):
    """Completion on all seven, then the forces, then the fit and the gate.

    Factored out of main() so that P-G can drive THE REAL PATH over a synthetic run
    root.  A comparator that has only ever been exercised on an empty directory has
    not been exercised.
    """
    rep = {}
    cases = {b: os.path.join(run_root, CASE_DIRS[b]) for b in BETAS}
    completion, absent = {}, []
    for b in BETAS:
        c = cases[b]
        if not os.path.isdir(c):
            absent.append(c)
            completion[b] = {"case": c, "ok": False, "reason": "case directory absent"}
            continue
        completion[b] = check_completion(c, end_time)
    rep["completion"] = {str(b): completion[b] for b in BETAS}

    if len(absent) == len(BETAS):
        rep["verdict"] = "PENDING"
        rep["reason"] = (f"no point has run: all seven case directories are absent "
                         f"under {run_root}")
        return rep

    incomplete = [b for b in FIT_BETAS if not completion[b]["ok"]]
    if incomplete:
        rep["verdict"] = "NOT A RESULT"
        rep["reason"] = (f"fitted points failing the strict completion rule: "
                         f"{incomplete}. There is no fit over fewer than the five "
                         f"registered points and no degradation to a shorter sweep.")
        return rep

    points, per_point = {}, {}
    te = float(end_time)
    for b in BETAS:
        if not completion[b]["ok"]:
            per_point[b] = {"status": "NOT A RESULT (completion)"}
            continue
        c = cases[b]
        f, fprov, fcon = fo_series(c, FO_TOTAL, "force.dat")
        m, mprov, mcon = fo_series(c, FO_TOTAL, "moment.dat")
        if te not in f or te not in m:
            refuse(f"beta={b}: no force/moment row at endTime={end_time} in {c}")
        yp, np_ = nondim(f[te][2], m[te][1])
        ts = sorted(t for t in f if t <= te)
        pl = plateau(ts, [(-f[t][2] / Q_AREA) for t in ts], yp)
        rec = {"case": c, "Yp": yp, "Np": np_,
               "F_z_mesh": f[te][2], "M_y_mesh": m[te][1],
               "force_from": fprov[te], "moment_from": mprov[te],
               "restart_value_conflicts": {"force": fcon, "moment": mcon},
               "plateau": pl, "in_fit": b in FIT_BETAS}
        # hull/sail split -- REPORTED, NOT GATED; absence does not void the gate.
        for nm, fo in (("hull", FO_HULL), ("sail", FO_SAIL)):
            try:
                sf, _p, _c2 = fo_series(c, fo, "force.dat")
                rec[f"F_z_{nm}"] = sf.get(te, (None, None, None))[2]
            except Refuse as e:
                rec[f"F_z_{nm}"] = None
                rec[f"F_z_{nm}_status"] = f"BLOCKED: {e}"
        per_point[b] = rec
        points[b] = {"Yp": yp, "Np": np_}
    rep["points"] = {str(b): per_point[b] for b in BETAS}

    stalled = [b for b in FIT_BETAS
               if per_point[b].get("plateau", {}).get("verdict") != "PASS"]
    if stalled:
        rep["verdict"] = "NOT A RESULT"
        rep["reason"] = (f"fitted points not plateaued over the final {PLATEAU_WIN} "
                         f"iterations (prereg §8.1a): {stalled}")
        return rep

    rep.update(grade_sweep(points))

    # beta = +/-12 are solved, reported and EXCLUDED from the fit; their residual
    # against the |beta| <= 8 line is printed so a reader sees where linearity ends.
    if "Y_v_prime" in rep:
        rep["linearity_check_excluded_points"] = {
            str(b): {"Yp": points[b]["Yp"],
                     "Yp_from_fit": rep["Y_v_prime"] * math.sin(math.radians(b))
                                    + rep["Y_intercept"],
                     "residual": points[b]["Yp"]
                                 - (rep["Y_v_prime"] * math.sin(math.radians(b))
                                    + rep["Y_intercept"])}
            for b in BETAS if abs(b) > 8 and b in points}
    return rep


# ------------------------------------------------------------------- main -----
def main():
    ap = argparse.ArgumentParser(description="SUBOFF A1h drift-sweep comparator")
    ap.add_argument("--run-root", default=os.path.join(REPO_ROOT, RUN_ROOT),
                    help="holds BETA_m12 … BETA_p12 (prereg §9)")
    ap.add_argument("--scratch", required=True, help="plant scratch; MUST be outside "
                                                     "every graded case")
    ap.add_argument("--out", required=True, help="JSON verdict; MUST be outside "
                                                 "every graded case")
    ap.add_argument("--end-time", type=int, default=END_TIME)
    a = ap.parse_args()

    report = {"comparator": os.path.relpath(os.path.abspath(__file__), REPO_ROOT),
              "preregistration": PREREG,
              "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    # -- THE NON-INTERFERENCE ASSERTION, printed in the comparator's own output ---
    # This comparator does not write into the cases it grades.  It writes only under
    # --out and --scratch, and it proves here that neither is inside one.
    cases = {b: os.path.join(a.run_root, CASE_DIRS[b]) for b in BETAS}
    graded = [os.path.abspath(p) for p in cases.values()] + [os.path.abspath(a.run_root)]
    for label, p in (("--scratch", a.scratch), ("--out", a.out)):
        ap_ = os.path.abspath(p)
        for g in graded:
            if ap_ == g or ap_.startswith(g + os.sep):
                sys.stderr.write(f"REFUSED: {label}={ap_} lies inside the graded tree "
                                 f"{g}. The comparator does not write into the cases "
                                 f"it grades.\n")
                sys.exit(2)
    report["non_interference"] = {
        "assertion": "this comparator writes ONLY to --out and --scratch; neither is "
                     "inside any graded case directory, nor inside the run root",
        "graded_trees": graded, "scratch": os.path.abspath(a.scratch),
        "out": os.path.abspath(a.out), "verdict": "PASS"}

    # -- RULE 3, BEFORE ANY REAL CASE IS OPENED ---------------------------------
    try:
        report["rule3_plants"] = plants(os.path.abspath(a.scratch))
    except Refuse as e:
        sys.stderr.write(f"REFUSED (rule 3): {e}\n")
        sys.exit(2)

    report.update(grade_run_root(a.run_root, a.end_time))
    _emit(report, a.out)
    return 0


def _emit(report, out):
    # A TRACKED HAZARD THAT NOBODY DISPLAYS IS WORSE THAN ONE NEVER COMPUTED.
    # `restart_value_conflicts` records a time whose force differs between restart
    # directories.  Recording it in the JSON is not enough -- it has to be RAISED to
    # the top of the report and PRINTED, or it sits unread and becomes the
    # "evidence annotated as non-binding" shape.  It does not change the verdict;
    # it is a disclosure, and the disclosure is the point.
    conflicted = {}
    for b, rec in (report.get("points") or {}).items():
        c = (rec or {}).get("restart_value_conflicts") or {}
        hits = {k: v for k, v in c.items() if v}
        if hits:
            conflicted[b] = hits
    report["restart_value_conflicts_present"] = bool(conflicted)
    report["restart_value_conflicts_by_point"] = conflicted

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
    v = report.get("verdict", "BLOCKED")
    print(f"SUBOFF A1h -- VERDICT: {v}")
    if conflicted:
        print(f"  *** RESTART VALUE CONFLICT at {len(conflicted)} point(s): "
              f"{sorted(conflicted)} -- a time appears in more than one restart "
              f"directory with DIFFERENT forces. The later directory was used. "
              f"This does not change the verdict and is disclosed, not absorbed.")
    if "Y_v_prime" in report:
        print(f"  Y_v' = {report['Y_v_prime']:+.6f}   GATED, band "
              f"[{YV_BAND[0]}, {YV_BAND[1]}]   Roddy EXPERIMENT {RODDY_YV:+.6f}")
        print(f"  N_v' = {report['N_v_prime']:+.6f}   REPORTED, NOT GRADED   "
              f"Roddy EXPERIMENT {RODDY_NV:+.6f}")
        print("  Roddy's two values are EXPERIMENTAL MEASUREMENTS read from a printed "
              "table. They are not anything this laboratory computed.")
    if "reason" in report:
        print(f"  reason: {report['reason']}")
    print(f"  report: {out}")


if __name__ == "__main__":
    sys.exit(main())
