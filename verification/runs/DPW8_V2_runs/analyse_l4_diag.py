#!/usr/bin/env python3
"""Grading reader for the DPW8_V2 L4 divergence diagnosis.

Pre-registration: verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_PREREGISTRATION.md
frozen at commit 99f939ee21ac5debbe6981e8f958bad02db4b82b (blob 55001f3a,
sha256 97938760db07b3a116da723df88b2440d528a79391d528bcc4a2a4ae9704d399).

Every threshold, window and expected control value below is transcribed from that
frozen document. Nothing here may be tuned to an arm's output; if a number here
disagrees with the frozen document, the frozen document wins and this file is the bug.

REFUSES (exit 2) rather than degrading:
  * if the positive control block C1-C5 does not reproduce the KNOWN NON-ZERO
    signature of the archived diverged L4 run (standing rule 3);
  * if coefficient.dat has no parseable header naming Cd and Cl (the exact misread
    that produced the parent record's original wrong L4 diagnosis -- see
    DPW8_V2_joukowski.md 3-CORRECTION). Column indices are NEVER hardcoded.

Usage:
    python3 analyse_l4_diag.py --controls-only
    python3 analyse_l4_diag.py --arm run_L4_diagA_relax [--arm run_L4_diagB_scheme]
"""

import argparse
import hashlib
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS -- transcribed from the pre-registration, section 4
# ---------------------------------------------------------------------------
END_TIME = 600

B1_STARTUP_GRACE = 50          # zero `bounding k` at Time > 50
B2_WINDOW = (100, 600)
B2_MAX_ABS_CD = 30.0
B3_WINDOW = (300, 600)
B3_MAX_ABS_CD = 5.0
B4_TIME = 600
B4_MAX_AVG_YPLUS = 20.0

REQUIRED_FIELDS = ["U", "p", "k", "omega", "nut"]

# ---------------------------------------------------------------------------
# FROZEN CONTROL EXPECTATIONS -- pre-registration section 5
# ---------------------------------------------------------------------------
ARCHIVE_LOG = os.path.join(
    REPO, "demo-output/website/solve_registry/dpw8_v2_L4_gate_20260729T231415Z.log")
ARCHIVE_LOG_MD5 = "a838e79619258cf9db2f7df328510322"

ARCHIVE_COEFF = os.path.join(
    HERE, "run_L4_gate/postProcessing/forceCoeffs1/0/coefficient.dat")
ARCHIVE_COEFF_MD5 = "aeac958a18d2376910b66391c8d858bc"

CLEAN_LOG = os.path.join(HERE, "run_L3_physics/log.simpleFoam")
CLEAN_LOG_MD5 = "16350124021757cde657ffb4f3d6827e"

ARCHIVE_YPLUS = os.path.join(HERE, "run_L4_gate/postProcessing/yPlus1/0/yPlus.dat")
CLEAN_YPLUS = os.path.join(HERE, "run_L3_physics/postProcessing/yPlus1/0/yPlus.dat")

C1_EXPECT_EVENTS = [(262, 2448938.729), (264, 2432568.241)]
C2_EXPECT_COUNT = 0
C3_EXPECT_IDX = {"Time": 0, "Cd": 1, "Cl": 4}
C3_EXPECT_POINTS = {201: (-563.6550, -396.5607), 401: (-332.8891, -8.8679)}
C3_EXPECT_W100 = (779.795, 105)
C3_EXPECT_W300 = 431.226
C4_EXPECT_YPLUS_DIVERGED = 122.159
C4_EXPECT_YPLUS_CLEAN = 3.3257

C5_PLANT_ITER = 350
C5_PLANT_CD = -9.8765e02

DP4 = 1e-4          # Cd/Cl compared to 4 decimal places
SIGFIG6 = 1e-6      # window maxima to 6 significant figures (relative)


class Refuse(Exception):
    """Raised when a control fails. The reader refuses; it does not degrade."""


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_md5(path, expected, label):
    got = md5(path)
    if got != expected:
        raise Refuse(f"{label}: md5 mismatch on {path}\n"
                     f"  expected {expected}\n  got      {got}\n"
                     f"  The control artifact is not the file the pre-registration froze.")
    return got


def rel_close(got, exp, tol):
    if exp == 0:
        return abs(got) <= tol
    return abs(got - exp) / abs(exp) <= tol


# ---------------------------------------------------------------------------
# READERS
# ---------------------------------------------------------------------------
def count_bounding_k(log_path):
    """Return [(iteration, k_max), ...] for every `bounding k` line in a solver log.

    Each line is attributed to the enclosing `Time = N` block. This is the same code
    path used for the known-2 archive log and the known-0 clean log; the zero is only
    admissible because the same function returns 2 on a log that has two.
    """
    events = []
    t = None
    time_re = re.compile(r"^Time = (\d+)")
    bnd_re = re.compile(r"bounding k, min: (\S+) max: (\S+) average: (\S+)")
    with open(log_path, "r", errors="replace") as f:
        for line in f:
            m = time_re.match(line)
            if m:
                t = int(m.group(1))
                continue
            b = bnd_re.search(line)
            if b:
                events.append((t, float(b.group(2))))
    return events


def read_coefficients(path):
    """Parse coefficient.dat. Columns are identified from the header BY NAME.

    Never by index: reading columns 8-9 as Cl is precisely the error that produced
    the parent record's original (wrong) L4 diagnosis. CmYaw happens to equal Cd/100
    for this setup, which is why the misread produced plausible-looking numbers.
    """
    idx = None
    rows = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                body = line.lstrip("#")
                names = [c.strip() for c in body.split("\t") if c.strip()]
                if "Time" in names and "Cd" in names and "Cl" in names:
                    idx = {n: i for i, n in enumerate(names)}
                continue
            parts = line.split()
            if parts:
                rows.append([float(x) for x in parts])
    if idx is None:
        raise Refuse(
            f"{path}: no parseable header line naming Time, Cd and Cl. "
            "Refusing to guess column positions -- a hardcoded index here is the "
            "documented failure mode of this exact case (3-CORRECTION).")
    for want in ("Time", "Cd", "Cl"):
        if idx[want] >= len(rows[0]) if rows else True:
            raise Refuse(f"{path}: header names {want} at column {idx[want]} "
                         f"but data rows have {len(rows[0]) if rows else 0} fields.")
    return idx, rows


def window_max_abs(rows, idx, col, lo, hi):
    """(max |value|, iteration at which it occurs) over lo <= Time <= hi."""
    it, ic = idx["Time"], idx[col]
    win = [r for r in rows if lo <= r[it] <= hi]
    if not win:
        return None, None
    best = max(win, key=lambda r: abs(r[ic]))
    return abs(best[ic]), int(best[it])


def value_at(rows, idx, col, iteration):
    it, ic = idx["Time"], idx[col]
    for r in rows:
        if int(r[it]) == iteration:
            return r[ic]
    return None


def read_yplus_avg(path, at_time):
    """Average y+ on the airfoil patch at a given Time, from a yPlus.dat history."""
    with open(path, "r", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.split()
            if not parts:
                continue
            try:
                t = int(float(parts[0]))
            except ValueError:
                continue
            if t == at_time:
                # columns: Time  patch  min  max  average
                return float(parts[-1])
    return None


# ---------------------------------------------------------------------------
# POSITIVE CONTROL BLOCK -- standing rule 3
# ---------------------------------------------------------------------------
def run_controls(out):
    def say(s):
        out.append(s)
        print(s)

    say("=" * 78)
    say("POSITIVE CONTROL BLOCK (pre-registration section 5) -- standing rule 3")
    say("A zero from a reader not shown able to see a non-zero is not evidence.")
    say("=" * 78)

    # --- C1: the k-bounding counter sees a known non-zero -------------------
    assert_md5(ARCHIVE_LOG, ARCHIVE_LOG_MD5, "C1")
    ev = count_bounding_k(ARCHIVE_LOG)
    say(f"C1  archived diverged L4 log  md5 OK")
    say(f"    bounding k events found: {len(ev)} -> {ev}")
    if len(ev) != len(C1_EXPECT_EVENTS):
        raise Refuse(f"C1: expected {len(C1_EXPECT_EVENTS)} bounding k events, got {len(ev)}")
    for (gi, gk), (ei, ek) in zip(ev, C1_EXPECT_EVENTS):
        if gi != ei or not rel_close(gk, ek, SIGFIG6):
            raise Refuse(f"C1: expected event (iter {ei}, kmax {ek}), got (iter {gi}, kmax {gk})")
    say(f"    C1 PASS -- reader demonstrably sees the known non-zero signature")

    # --- C2: the same counter returns zero on a known-clean log -------------
    assert_md5(CLEAN_LOG, CLEAN_LOG_MD5, "C2")
    ev3 = count_bounding_k(CLEAN_LOG)
    say(f"C2  healthy L3 log  md5 OK")
    say(f"    bounding k events found: {len(ev3)}")
    if len(ev3) != C2_EXPECT_COUNT:
        raise Refuse(f"C2: expected {C2_EXPECT_COUNT} events on the clean log, got {len(ev3)}")
    say(f"    C2 PASS -- this zero is admissible ONLY because C1 above returned 2 "
        f"from the same function in this same invocation")

    # --- C3: the coefficient reader sees the known divergence signature -----
    assert_md5(ARCHIVE_COEFF, ARCHIVE_COEFF_MD5, "C3")
    idx, rows = read_coefficients(ARCHIVE_COEFF)
    say(f"C3  archived diverged L4 coefficient.dat  md5 OK")
    got_idx = {k: idx[k] for k in ("Time", "Cd", "Cl")}
    say(f"    header-identified column indices: {got_idx}")
    if got_idx != C3_EXPECT_IDX:
        raise Refuse(f"C3: expected column indices {C3_EXPECT_IDX}, got {got_idx}")
    for it, (ecd, ecl) in C3_EXPECT_POINTS.items():
        gcd, gcl = value_at(rows, idx, "Cd", it), value_at(rows, idx, "Cl", it)
        say(f"    iter {it}: Cd={gcd:.4f} Cl={gcl:.4f}  (expected {ecd:.4f} / {ecl:.4f})")
        if abs(gcd - ecd) > DP4 or abs(gcl - ecl) > DP4:
            raise Refuse(f"C3: iter {it} expected Cd={ecd} Cl={ecl}, got Cd={gcd} Cl={gcl}")
    m100, i100 = window_max_abs(rows, idx, "Cd", *B2_WINDOW)
    m300, _ = window_max_abs(rows, idx, "Cd", *B3_WINDOW)
    say(f"    max|Cd| {B2_WINDOW[0]}-{B2_WINDOW[1]} = {m100:.6g} at iter {i100} "
        f"(expected {C3_EXPECT_W100[0]} at {C3_EXPECT_W100[1]})")
    say(f"    max|Cd| {B3_WINDOW[0]}-{B3_WINDOW[1]} = {m300:.6g} (expected {C3_EXPECT_W300})")
    if not rel_close(m100, C3_EXPECT_W100[0], SIGFIG6) or i100 != C3_EXPECT_W100[1]:
        raise Refuse(f"C3: window {B2_WINDOW} expected {C3_EXPECT_W100}, got ({m100}, {i100})")
    if not rel_close(m300, C3_EXPECT_W300, SIGFIG6):
        raise Refuse(f"C3: window {B3_WINDOW} expected {C3_EXPECT_W300}, got {m300}")
    say(f"    C3 PASS")

    # --- C4: the y+ reader sees the known non-zero --------------------------
    yd = read_yplus_avg(ARCHIVE_YPLUS, B4_TIME)
    yc = read_yplus_avg(CLEAN_YPLUS, B4_TIME)
    say(f"C4  avg y+ at Time {B4_TIME}: diverged L4 = {yd:.6g} (expected {C4_EXPECT_YPLUS_DIVERGED}), "
        f"healthy L3 = {yc:.6g} (expected {C4_EXPECT_YPLUS_CLEAN})")
    if not rel_close(yd, C4_EXPECT_YPLUS_DIVERGED, 1e-5):
        raise Refuse(f"C4: diverged y+ expected {C4_EXPECT_YPLUS_DIVERGED}, got {yd}")
    if not rel_close(yc, C4_EXPECT_YPLUS_CLEAN, 1e-4):
        raise Refuse(f"C4: clean y+ expected {C4_EXPECT_YPLUS_CLEAN}, got {yc}")
    say(f"    C4 PASS")
    say("")
    return True


def run_c5_plant(arm_dir, out):
    """C5 -- plant into a scratch copy of THIS ARM'S OWN coefficient.dat.

    C1-C4 prove the reader works on the archive. They do NOT prove it is reading this
    arm's file. The arm's real file is never modified; the plant lives only in a
    scratch copy, which is deleted afterwards.
    """
    def say(s):
        out.append(s)
        print(s)

    real = os.path.join(arm_dir, "postProcessing/forceCoeffs1/0/coefficient.dat")
    idx, rows = read_coefficients(real)
    own_max, _ = window_max_abs(rows, idx, "Cd", *B2_WINDOW)

    plant = C5_PLANT_CD
    if own_max is not None and own_max >= abs(C5_PLANT_CD):
        plant = -10.0 * own_max
        say(f"C5  arm's own max|Cd| ({own_max:.6g}) exceeds the nominal plant; "
            f"plant raised to {plant:.6g} per section 5")

    before = md5(real)
    tmpd = tempfile.mkdtemp(prefix="l4diag_plant_")
    try:
        copy = os.path.join(tmpd, "coefficient.dat")
        shutil.copy2(real, copy)
        # replace the Cd field of the existing iteration-350 row, in place, by index
        lines = open(copy, "r", errors="replace").read().splitlines(keepends=True)
        planted_line = None
        for n, line in enumerate(lines):
            if line.startswith("#"):
                continue
            parts = line.split()
            if parts and int(float(parts[0])) == C5_PLANT_ITER:
                parts[idx["Cd"]] = f"{plant:.10e}"
                lines[n] = "\t".join(parts) + "\n"
                planted_line = n
                break
        if planted_line is None:
            raise Refuse(f"C5: no row at iteration {C5_PLANT_ITER} in {real} to plant into")
        open(copy, "w").write("".join(lines))

        pidx, prows = read_coefficients(copy)
        g100, _ = window_max_abs(prows, pidx, "Cd", *B2_WINDOW)
        g300, _ = window_max_abs(prows, pidx, "Cd", *B3_WINDOW)
        say(f"C5  planted Cd = {plant:.6g} at iteration {C5_PLANT_ITER} "
            f"(line index {planted_line}) into a scratch copy of {os.path.basename(arm_dir)}'s own file")
        say(f"    read back: max|Cd| {B2_WINDOW} = {g100:.6g}, max|Cd| {B3_WINDOW} = {g300:.6g}, "
            f"expected {abs(plant):.6g} for both")
        if not rel_close(g100, abs(plant), SIGFIG6) or not rel_close(g300, abs(plant), SIGFIG6):
            raise Refuse(f"C5: reader could not see the plant in {arm_dir}'s own file "
                         f"(got {g100} / {g300}, expected {abs(plant)}). "
                         "Refusing to grade this arm.")
        say(f"    C5 PASS -- reader demonstrably reads THIS arm's file")
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    after = md5(real)
    if before != after:
        raise Refuse(f"C5: the arm's real coefficient.dat changed during planting "
                     f"({before} -> {after}). The plant must live only in the scratch copy.")
    say(f"    arm's real file unmodified (md5 {after} before and after)")
    return True


# ---------------------------------------------------------------------------
# COMPLETION -- pre-registration section 6 (standing rule 4)
# ---------------------------------------------------------------------------
def check_completion(arm_dir, out):
    def say(s):
        out.append(s)
        print(s)

    log = os.path.join(arm_dir, "log.simpleFoam")
    rcf = os.path.join(arm_dir, "solver.rc")
    clauses = {}

    if not os.path.exists(log):
        return False, {"log_present": False}, None
    text = open(log, "r", errors="replace").read()

    rc = None
    if os.path.exists(rcf):
        try:
            rc = int(open(rcf).read().strip())
        except ValueError:
            rc = None
    clauses["rc_zero"] = (rc == 0)

    clauses["End_line"] = bool(re.search(r"^End\s*$", text, re.M))

    times = [int(m) for m in re.findall(r"^Time = (\d+)", text, re.M)]
    last_time = times[-1] if times else None
    clauses["last_time_is_endTime"] = (last_time == END_TIME)

    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    clauses["ExecutionTime_count"] = (n_exec == END_TIME)

    # pre-declared exception: legitimate early convergence
    conv = re.search(r"SIMPLE solution converged in (\d+) iterations", text)
    effective_end = END_TIME
    if conv:
        n = int(conv.group(1))
        say(f"    NOTE: pre-declared early-convergence exception fired: "
            f"'SIMPLE solution converged in {n} iterations'")
        effective_end = n
        clauses["last_time_is_endTime"] = (last_time == n)
        clauses["ExecutionTime_count"] = (n_exec == n)

    tdir = os.path.join(arm_dir, str(effective_end))
    clauses["time_dir_present"] = os.path.isdir(tdir)
    present = os.listdir(tdir) if clauses["time_dir_present"] else []
    clauses["fields_present"] = all(f in present for f in REQUIRED_FIELDS)

    # age guard: every field at endTime newer than the arm's own 0/U
    ref = os.path.join(arm_dir, "0", "U")
    if clauses["time_dir_present"] and os.path.exists(ref):
        t0 = os.path.getmtime(ref)
        ages = {f: os.path.getmtime(os.path.join(tdir, f)) - t0
                for f in REQUIRED_FIELDS if f in present}
        clauses["age_guard"] = bool(ages) and all(v > 0 for v in ages.values())
        clauses["_age_margins_s"] = {k: round(v, 1) for k, v in ages.items()}
    else:
        clauses["age_guard"] = False

    ok = all(v for k, v in clauses.items() if not k.startswith("_"))
    say(f"    completion clauses: " +
        ", ".join(f"{k}={v}" for k, v in clauses.items() if not k.startswith("_")))
    if "_age_margins_s" in clauses:
        say(f"    age-guard margins vs 0/U (s): {clauses['_age_margins_s']}")
    return ok, clauses, effective_end


# ---------------------------------------------------------------------------
# GRADING -- pre-registration section 4
# ---------------------------------------------------------------------------
def grade_arm(arm_name, out):
    def say(s):
        out.append(s)
        print(s)

    arm_dir = os.path.join(HERE, arm_name)
    say("=" * 78)
    say(f"ARM: {arm_name}")
    say("=" * 78)

    complete, clauses, eff_end = check_completion(arm_dir, out)
    if not complete:
        say(f"  -> BLOCKED (pre-registration section 6: run did not complete). "
            f"Not graded. A crash is a finding and goes to the supervisor for triage.")
        return {"arm": arm_name, "label": "BLOCKED", "clauses": clauses}

    run_c5_plant(arm_dir, out)

    log = os.path.join(arm_dir, "log.simpleFoam")
    coeff = os.path.join(arm_dir, "postProcessing/forceCoeffs1/0/coefficient.dat")
    yplus = os.path.join(arm_dir, "postProcessing/yPlus1/0/yPlus.dat")

    # B1
    ev = count_bounding_k(log)
    late = [e for e in ev if e[0] is not None and e[0] > B1_STARTUP_GRACE]
    b1 = (len(late) == 0)
    say(f"  B1  bounding k after iter {B1_STARTUP_GRACE}: {len(late)} "
        f"(total in log: {len(ev)}) -> {'PASS' if b1 else 'FAIL'}")
    if ev:
        say(f"      all events: {ev}")

    # B2 / B3
    idx, rows = read_coefficients(coeff)
    m2, i2 = window_max_abs(rows, idx, "Cd", *B2_WINDOW)
    m3, i3 = window_max_abs(rows, idx, "Cd", *B3_WINDOW)
    b2 = (m2 is not None and m2 < B2_MAX_ABS_CD)
    b3 = (m3 is not None and m3 < B3_MAX_ABS_CD)
    say(f"  B2  max|Cd| {B2_WINDOW[0]}-{B2_WINDOW[1]} = {m2:.6g} at iter {i2} "
        f"(threshold < {B2_MAX_ABS_CD}) -> {'PASS' if b2 else 'FAIL'}")
    say(f"  B3  max|Cd| {B3_WINDOW[0]}-{B3_WINDOW[1]} = {m3:.6g} at iter {i3} "
        f"(threshold < {B3_MAX_ABS_CD}) -> {'PASS' if b3 else 'FAIL'}")

    # B4
    y = read_yplus_avg(yplus, B4_TIME)
    b4 = (y is not None and y < B4_MAX_AVG_YPLUS)
    say(f"  B4  avg y+ at Time {B4_TIME} = {y if y is None else f'{y:.6g}'} "
        f"(threshold < {B4_MAX_AVG_YPLUS}) -> {'PASS' if b4 else 'FAIL'}")

    label = "BOUNDED" if (b1 and b2 and b3 and b4) else "NOT BOUNDED"
    say(f"  -> {label}   (B1={b1} B2={b2} B3={b3} B4={b4})")
    say("      NOTE: BOUNDED / NOT BOUNDED are stability-indicator outcome labels,")
    say("      NOT gate verdicts. L4 remains NOT GATED. No CL/Cd/Cp claim follows.")

    # reported alongside, non-gating context
    cd_final = value_at(rows, idx, "Cd", eff_end)
    cl_final = value_at(rows, idx, "Cl", eff_end)
    say(f"      context (not a physics result): Cd({eff_end})={cd_final}, Cl({eff_end})={cl_final}")

    return {"arm": arm_name, "label": label,
            "B1_late_bounding_k": len(late), "B1": b1,
            "B2_max_abs_cd": m2, "B2": b2,
            "B3_max_abs_cd": m3, "B3": b3,
            "B4_avg_yplus": y, "B4": b4}


def outcome_map(results, out):
    def say(s):
        out.append(s)
        print(s)

    by = {r["arm"]: r["label"] for r in results}
    a = by.get("run_L4_diagA_relax")
    b = by.get("run_L4_diagB_scheme")
    say("")
    say("=" * 78)
    say("DIAGNOSIS -- pre-registration section 7 outcome map")
    say("=" * 78)
    say(f"  Arm A (relaxation only)      : {a}")
    say(f"  Arm B (momentum scheme only) : {b}")
    if a is None or b is None:
        say("  -> PENDING: both arms are required for the outcome map.")
        return "PENDING"
    if "BLOCKED" in (a, b):
        say("  -> PENDING on the BLOCKED arm. A single BOUNDED arm plus a BLOCKED arm")
        say("     licenses only that that one lever is sufficient; nothing about the other.")
        return "PENDING"
    if a == "BOUNDED" and b == "NOT BOUNDED":
        say("  -> Cause INCLUDES startup/relaxation robustness. The relaxation carried")
        say("     over unchanged from the coarser rungs is insufficient at L4 spacing.")
        say("     The momentum-convection lever alone does not rescue it.")
        return "A_ONLY"
    if a == "NOT BOUNDED" and b == "BOUNDED":
        say("  -> Cause INCLUDES the momentum-convection discretisation at L4.")
        say("     The relaxation lever alone does not rescue it.")
        return "B_ONLY"
    if a == "BOUNDED" and b == "BOUNDED":
        say("  -> BOTH levers independently restore boundedness. Informative, NOT")
        say("     contradictory. NEITHER lever is uniquely identified as the cause,")
        say("     and no claim is made that one of them is 'the' root cause.")
        return "BOTH"
    say("  -> NOT A RESULT for the diagnosis question. Both cheapest single-lever")
    say("     hypotheses are ELIMINATED; the cause lies outside relaxation and")
    say("     convective discretisation. Remaining suspects: near-wall treatment /")
    say("     wall functions, the omega wall BC at L4 first-cell spacing, and the")
    say("     linear-solver stall of DPW8_V2_joukowski.md section 3b. No cause asserted.")
    return "NOT A RESULT"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--controls-only", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    out = []
    try:
        run_controls(out)
    except Refuse as e:
        print(f"\nREFUSED (exit 2): {e}", file=sys.stderr)
        return 2

    if args.controls_only:
        print("Controls only -- no arm graded.")
        if args.out:
            open(args.out, "w").write("\n".join(out) + "\n")
        return 0

    results = []
    for arm in args.arm:
        try:
            results.append(grade_arm(arm, out))
        except Refuse as e:
            print(f"\nREFUSED (exit 2) while grading {arm}: {e}", file=sys.stderr)
            return 2

    verdict = outcome_map(results, out)
    out.append(f"OUTCOME_MAP_CELL: {verdict}")
    print(f"OUTCOME_MAP_CELL: {verdict}")

    if args.out:
        open(args.out, "w").write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
