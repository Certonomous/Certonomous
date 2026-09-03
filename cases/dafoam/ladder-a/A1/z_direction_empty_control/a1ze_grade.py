#!/usr/bin/env python3
"""A1ZE grader -- `empty` versus `symmetry` on the two bounding planes.

FROZEN GRADING PATH. This file is pinned by md5 in A1ZE_PREREGISTRATION.md and is
the ONLY path allowed to emit an A1ZE verdict. No reader may be substituted.

Verdict vocabulary, and only this vocabulary:
    PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING
VERDICT_CEILING is `GATE REACHED` -- this item has no pre-registered band for any
value and no Roache triple, so `PASS` is unreachable by construction and any
grading path emitting it is defective.

Usage:
    a1ze_grade.py --selftest              controls only, no run root needed
    a1ze_grade.py --root <A1ZE run root>  controls, then grade

SUBMISSIONS PARKED. Nothing here sends, files, uploads, registers or posts.
"""
import argparse
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONTROLS = os.path.join(HERE, "controls")

# ---------------------------------------------------------------- pinned facts
# Static planted-zero fixtures, authored at freeze, md5-pinned here. L-435: not
# one control reads anything produced by this item's own solves.
PINS = {
    "P1_dirn2.log": "66d4555036ebaf661673ca03541b02a1",
    "P1_dirn3.log": "28ac80cdc8823775cd9f1271ab600ef3",
    "P2_eqs.log": "412754b0a7673c6e65db010d66be51d9",
    "P2n_noU2.log": "8674c4a076872924a6248e636016c7c0",
    "P3_coef.log": "8693c7445260b7775d5ba6678cec72cd",
    "P4_stationary.log": "8d0d8023e95d4c305c81075433e5af1a",
    "P4_swinging.log": "83246d34f4b2828b2f6fef645d36596f",
    "P5_empty": "a681ef56baac150de46c2c846599fbe9",
    "P5_symmetry": "8343e69e4695ee363dc02c5d697dc79b",
}

# P3 expected literals, computed once from the fixture at freeze.
P3_CL_MEAN, P3_CD_MEAN = 1.0000065, 0.030000065
P3_CL_SPREAD, P3_CD_SPREAD = 8.999941500305982e-06, 2.999993500054091e-06

# Registered arms. iters is the FIXED stop -- both arms of a pair run the same
# number of iterations, because a tolerance-based stop would let them run
# different ones and that is a third variable (see registration section 2).
ARMS = {
    #  name : (mesh, cells, planes, alpha, iters, ranks, cap_core_min, tmo_s)
    "Sc": ("coarse", 4032, "symmetry", 4.0, 2000, 1, 9.0, 480),
    "Ec": ("coarse", 4032, "empty", 4.0, 2000, 1, 9.0, 480),
    "S3": ("L3", 130304, "symmetry", 12.0, 2000, 1, 257.0, 15360),
    "E3": ("L3", 130304, "empty", 12.0, 2000, 1, 257.0, 15360),
}
PAIRS = [("coarse", "Sc", "Ec"), ("L3", "S3", "E3")]
# 532.0, not 370.0. The predecessor figure DID NOT BIND: the driver's G-CEIL
# tests cumulative spend BEFORE an arm, never spend+cap, so the walk 0/9/18/275
# never reaches 370 and the worst case is the cap sum. A ceiling below the cap
# sum is not a ceiling. Corrected pre-compute (A1ZE_PREREGISTRATION ADDENDUM C).
ITEM_CEILING_CORE_MIN = 532.0

# GUARD EXECUTION MARKERS -- "plant the run, not only the value". A control that
# proves a reader can see a non-zero does not prove the reader EXECUTED. Each of
# these is printed by a1ze_cmd.sh only after the guard it names has actually run
# and counted what it examined; a missing marker means the guard did not run, and
# an arm whose guards did not run is NOT A RESULT however clean its numbers look.
GUARD_MARKERS = {
    "A1ZE_G_EMPTY_OK": "G-EMPTY examined the mesh and a non-zero count of fields",
    "A1ZE_TIMEDIR_SCAN": "the age-guard precondition scan ran",
    "A1ZE_TOL_VAR_OK": "the staged runScript was proved to read A1WR_PRIMAL_TOL",
    "A1ZE_COLD_START": "0/ was reset from 0.orig last, dating the run",
}
RE_FIELDS_CHECKED = re.compile(r"A1ZE_G_EMPTY_OK .*fields_checked=(\d+)")

# Drift anchors -- MEASURED, per operating point, each from its own alpha
# segment of A1WR sweep_I/out/sweep.log (last 10 CL:/CD: prints of that segment).
# The L3 pair runs at alpha = 12 and is GATED on alpha = 12's own drift.
# The coarse pair runs at alpha = 4 on a DIFFERENT grid; the alpha = 4 figures
# below are an L3 cross-grid PROXY, so the coarse pair's G-COEF is REPORTED,
# never gated (Sanaa 2026-09-03 ~20:00Z: reported-not-gated is the default).
DRIFT = {
    "L3": {"CL": 4.830552e-04, "CD": 1.116421e-04, "gated": True},
    "coarse": {"CL": 2.300624e-04, "CD": 2.276654e-05, "gated": False},
}
CONTAM_MULT = 10.0   # a stated JUDGEMENT, not a measurement
STAT_MULT = 2.0      # G-STAT admits an arm at up to 2x its pair's drift anchor

# CONTEXT ONLY -- not a threshold and not read by any gate. The measured U2
# floor of the L3 mesh (A1WR_STAGE12_RESULTS.md section 16, minimum initRes over
# all 559 print steps of sweep_I/out/sweep.log). Registration section 1a
# measures U2 OUT of the declared quantity, so this number cannot gate anything:
# the U2-excluded per-iteration max at alpha = 12 floors at 2.997861e-08, and
# all 14 A1WR points miss 1e-8 with U2 excluded.
U2_FLOOR_L3 = 3.238410e-08
U2_EXCLUDED_FLOOR_A12 = 2.997861e-08

RE_DIRN = re.compile(r"Mesh has (\d+) solution \(non-empty\) directions \(([\d ]+)\)")
RE_EQ = re.compile(r"^(\w+) initRes: ([-\d.eE+]+) finalRes: ([-\d.eE+]+)")
RE_CL = re.compile(r"^CL:\s+([-\d.eE+]+)")
RE_CD = re.compile(r"^CD:\s+([-\d.eE+]+)")
RE_TIME = re.compile(r"^Time = (\d+)")
RE_EXEC = re.compile(r"^ExecutionTime = ")
RE_CONVERGED = re.compile(r"satisfied the prescribed tolerance")
RE_PATCH = re.compile(r"^\s*(\w+)\s*$")
RE_TYPE = re.compile(r"^\s*type\s+(\w+)\s*;")


class Refuse(Exception):
    """Any control refusal makes the whole item NOT A RESULT."""


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def spread(v):
    if len(v) < 2:
        raise Refuse("spread over fewer than two samples")
    m = sum(v) / len(v)
    if m == 0.0:
        raise Refuse("spread denominator is zero")
    return (max(v) - min(v)) / abs(m)


# ------------------------------------------------------------------- readers
def read_dirn(path):
    """-> (N, tuple) from the solution-directions line; None if absent."""
    with open(path, errors="replace") as f:
        for line in f:
            m = RE_DIRN.search(line)
            if m:
                return int(m.group(1)), tuple(int(x) for x in m.group(2).split())
    return None


def read_equations(path):
    """-> set of equation labels that appear in any `X initRes:` block."""
    out = set()
    with open(path, errors="replace") as f:
        for line in f:
            m = RE_EQ.match(line)
            if m:
                out.add(m.group(1))
    return out


def read_eq_min(path, label):
    """-> minimum initRes reached by one channel over the whole log."""
    best = None
    with open(path, errors="replace") as f:
        for line in f:
            m = RE_EQ.match(line)
            if m and m.group(1) == label:
                v = float(m.group(2))
                best = v if best is None else min(best, v)
    return best


def read_coefs(path):
    """-> (CL list, CD list) in print order, read as independent streams."""
    cl, cd = [], []
    with open(path, errors="replace") as f:
        for line in f:
            m = RE_CL.match(line)
            if m:
                cl.append(float(m.group(1)))
                continue
            m = RE_CD.match(line)
            if m:
                cd.append(float(m.group(1)))
    return cl, cd


def read_patch_types(path, names):
    """-> {patch name: type} from an OpenFOAM constant/polyMesh/boundary file."""
    out, pending = {}, None
    with open(path, errors="replace") as f:
        for line in f:
            m = RE_TYPE.match(line)
            if m and pending in names:
                out[pending] = m.group(1)
                pending = None
                continue
            m = RE_PATCH.match(line)
            if m:
                pending = m.group(1)
    return out


def read_field_patch_types(path, names):
    """Same shape, for a 0/ field file's boundaryField block."""
    return read_patch_types(path, names)


# ------------------------------------------------------ planted-zero controls
def controls(run_root=None):
    """Every reader is proved able to return BOTH answers before it is trusted.
    A reader never shown able to see a non-zero is not evidence (rule 3)."""
    log = []

    for name, pin in sorted(PINS.items()):
        p = os.path.join(CONTROLS, name)
        if not os.path.exists(p):
            raise Refuse(f"CONTROL_FIXTURE_ABSENT: {name}")
        got = md5(p)
        if got != pin:
            raise Refuse(f"CONTROL_FIXTURE_MOVED: {name} {got} != {pin}")
        if run_root is not None:
            if os.path.abspath(p).startswith(os.path.abspath(run_root) + os.sep):
                raise Refuse(f"CONTROL_FIXTURE_INSIDE_RUN_ROOT: {name}")
            if os.path.getmtime(p) >= os.path.getmtime(run_root):
                raise Refuse(f"CONTROL_FIXTURE_NOT_OLDER_THAN_RUN: {name}")
    log.append(f"P0 fixtures pinned and independent: {len(PINS)}/{len(PINS)}")

    # P1 -- the solution-directions reader must DISTINGUISH 3 from 2.
    a = read_dirn(os.path.join(CONTROLS, "P1_dirn3.log"))
    b = read_dirn(os.path.join(CONTROLS, "P1_dirn2.log"))
    if a != (3, (1, 1, 1)) or b != (2, (1, 1, 0)):
        raise Refuse(f"CONTROL_READER_NOT_BORN: P1 {a} {b}")
    log.append("P1 directions reader distinguishes 3 (1 1 1) from 2 (1 1 0)")

    # P2 -- positive leg: the per-equation reader must SEE U2 and its value.
    eqs = read_equations(os.path.join(CONTROLS, "P2_eqs.log"))
    if "U2" not in eqs:
        raise Refuse("CONTROL_READER_NOT_BORN: P2 cannot see U2")
    v = read_eq_min(os.path.join(CONTROLS, "P2_eqs.log"), "U2")
    if v != 3.0000e-04:
        raise Refuse(f"CONTROL_READER_NOT_BORN: P2 U2 value {v!r}")
    log.append("P2 equation reader sees U2 initRes 3.0000e-04 among five channels")

    # P2n -- negative leg: a reader that ALWAYS finds U2 is as blind as one that
    # never does. G-U2.E's whole content is an ABSENCE, so the absence must be
    # demonstrable (L-452 addendum).
    eqs_n = read_equations(os.path.join(CONTROLS, "P2n_noU2.log"))
    if "U2" in eqs_n:
        raise Refuse("CONTROL_READER_ALWAYS_FIRES: P2n reports U2 in a block without it")
    if not {"U0", "U1", "p", "nuTilda"} <= eqs_n:
        raise Refuse(f"CONTROL_READER_NOT_BORN: P2n lost the other channels {eqs_n}")
    log.append("P2n equation reader reports U2 ABSENT on a block that has no U2")

    # P3 -- the coefficient series reader, mean and spread to 1e-12 relative.
    cl, cd = read_coefs(os.path.join(CONTROLS, "P3_coef.log"))
    if len(cl) != 12 or len(cd) != 12:
        raise Refuse(f"CONTROL_READER_NOT_BORN: P3 counts {len(cl)}/{len(cd)}")
    for got, want, tag in (
        (sum(cl[-10:]) / 10, P3_CL_MEAN, "CL mean"),
        (sum(cd[-10:]) / 10, P3_CD_MEAN, "CD mean"),
        (spread(cl[-10:]), P3_CL_SPREAD, "CL spread"),
        (spread(cd[-10:]), P3_CD_SPREAD, "CD spread"),
    ):
        if abs(got - want) > 1e-12 * abs(want):
            raise Refuse(f"CONTROL_READER_NOT_BORN: P3 {tag} {got!r} != {want!r}")
    log.append("P3 coefficient reader reproduces mean and spread to 1e-12 relative")

    # P4 -- the G-STAT test must PASS one fixture and FAIL the other. A gate
    # never shown to return BOTH answers is not a gate.
    s_cl, s_cd = read_coefs(os.path.join(CONTROLS, "P4_stationary.log"))
    w_cl, w_cd = read_coefs(os.path.join(CONTROLS, "P4_swinging.log"))
    thr = STAT_MULT * DRIFT["L3"]["CL"]
    if not spread(s_cl[-10:]) <= thr:
        raise Refuse("CONTROL_GATE_STUCK: P4 rejects a stationary series")
    if spread(w_cl[-10:]) <= thr:
        raise Refuse("CONTROL_GATE_STUCK: P4 admits a swinging series")
    if not spread(s_cd[-10:]) <= STAT_MULT * DRIFT["L3"]["CD"]:
        raise Refuse("CONTROL_GATE_STUCK: P4 rejects a stationary CD series")
    if spread(w_cd[-10:]) <= STAT_MULT * DRIFT["L3"]["CD"]:
        raise Refuse("CONTROL_GATE_STUCK: P4 admits a swinging CD series")
    log.append("P4 G-STAT test passes the stationary fixture and FAILS the swinging one")

    # P5 -- the patch-type reader must distinguish symmetry from empty.
    ps = read_patch_types(os.path.join(CONTROLS, "P5_symmetry"), {"symmetry1", "symmetry2"})
    pe = read_patch_types(os.path.join(CONTROLS, "P5_empty"), {"symmetry1", "symmetry2"})
    if ps != {"symmetry1": "symmetry", "symmetry2": "symmetry"}:
        raise Refuse(f"CONTROL_READER_NOT_BORN: P5 symmetry leg {ps}")
    if pe != {"symmetry1": "empty", "symmetry2": "empty"}:
        raise Refuse(f"CONTROL_READER_NOT_BORN: P5 empty leg {pe}")
    log.append("P5 patch-type reader distinguishes symmetry from empty on both planes")

    return log


# ------------------------------------------------------------ completion rule
def completion(arm, root):
    """Strict completion rule -- ALL of it holds or the arm is not done.
    rc = 0; an `End` line; last `Time =` == the registered iteration count;
    the ExecutionTime print count == that count / print interval; and the AGE
    GUARD: the log is NEWER than the case's own 0/ directory, which is touched
    last at launch and so dates the run allowed to produce the answer."""
    _, _, _, _, iters, _, _, _ = ARMS[arm]
    d = os.path.join(root, arm)
    log_p, rc_p, zero_p = (os.path.join(d, "out", "sweep.log"),
                           os.path.join(d, "out", "rc.txt"),
                           os.path.join(d, "case", "0"))
    fails = []
    for p in (log_p, rc_p, zero_p):
        if not os.path.exists(p):
            fails.append(f"absent: {os.path.relpath(p, root)}")
    if fails:
        return False, fails, None

    rc = open(rc_p).read().strip()
    if rc != "0":
        fails.append(f"rc={rc}")

    last_time, n_exec, saw_end, n_print = None, 0, False, 0
    with open(log_p, errors="replace") as f:
        for line in f:
            m = RE_TIME.match(line)
            if m:
                last_time = int(m.group(1))
                n_print += 1
                continue
            if RE_EXEC.match(line):
                n_exec += 1
            elif line.strip() == "End":
                saw_end = True
    if not saw_end:
        fails.append("no End line")
    if last_time != iters:
        fails.append(f"last Time = {last_time} != endTime {iters}")
    if n_exec != n_print:
        fails.append(f"ExecutionTime count {n_exec} != Time print count {n_print}")
    if os.path.getmtime(log_p) <= os.path.getmtime(zero_p):
        fails.append("AGE GUARD: log not newer than the case's own 0/")
    return (not fails), fails, log_p


# -------------------------------------------------------------------- grading
def grade(root):
    out, verdict_bits = [], []
    arm_state = {}

    # G-EMPTY / G-SYM: the mesh and every 0/ field must agree on the patch type.
    # A patch cannot be `empty` in the mesh and `symmetry` in the field --
    # OpenFOAM refuses the combination, and so does this gate, BEFORE the run is
    # read for anything else.
    for arm, (_, _, want, _, _, _, _, _) in ARMS.items():
        d = os.path.join(root, arm, "case")
        b = os.path.join(d, "constant", "polyMesh", "boundary")
        if not os.path.exists(b):
            arm_state[arm] = "BLOCKED"
            out.append(f"G-EMPTY {arm}: BLOCKED -- boundary file absent")
            continue
        seen = {b: read_patch_types(b, {"symmetry1", "symmetry2"})}
        fd = os.path.join(d, "0")
        if os.path.isdir(fd):
            for fn in sorted(os.listdir(fd)):
                fp = os.path.join(fd, fn)
                if os.path.isfile(fp) and not fn.endswith(".gz"):
                    t = read_field_patch_types(fp, {"symmetry1", "symmetry2"})
                    if t:
                        seen[fp] = t
        bad = {p: t for p, t in seen.items()
               if set(t.values()) != {want} or len(t) != 2}
        nfield = len(seen) - 1
        if bad:
            arm_state[arm] = "BLOCKED"
            out.append(f"G-EMPTY {arm}: BLOCKED -- {len(bad)} file(s) not "
                       f"'{want}' on both planes")
        elif nfield <= 0:
            # THE SAME VACUOUS PASS THIS ITEM SWEPT FOR IN a1ze_cmd.sh, FOUND
            # HERE BY THE FIRST FIRE: the arm never ran, `case/0` did not exist,
            # so the loop examined NOTHING and the guard reported both planes
            # fine. "Checked and clean" must not look like "did not check".
            arm_state[arm] = "BLOCKED"
            out.append(f"G-EMPTY {arm}: BLOCKED -- the mesh reads '{want}' but "
                       f"ZERO field files were examined; the check did not run")
        else:
            out.append(f"G-EMPTY {arm}: both planes '{want}' in the mesh and in "
                       f"{nfield} field file(s)")

    for arm in ARMS:
        if arm_state.get(arm) == "BLOCKED":
            continue
        ok, fails, log_p = completion(arm, root)
        if not ok:
            arm_state[arm] = "NOT A RESULT"
            out.append(f"COMPLETION {arm}: NOT A RESULT -- {'; '.join(fails)}")
            continue
        out.append(f"COMPLETION {arm}: all clauses hold (rc=0, End, "
                   f"last time == endTime, counts match, age guard clear)")
        arm_state[arm] = log_p

    # G-DIRN and G-U2, the mechanism gates.
    for arm, (_, _, planes, _, _, _, _, _) in ARMS.items():
        log_p = arm_state.get(arm)
        if not isinstance(log_p, str) or not log_p.endswith(".log"):
            continue
        d = read_dirn(log_p)
        if d is None:
            out.append(f"G-DIRN {arm}: NOT A RESULT -- no directions line")
            arm_state[arm] = "NOT A RESULT"
            continue
        n, trip = d
        eqs = read_equations(log_p)
        if planes == "symmetry":
            if n != 3 or trip != (1, 1, 1):
                out.append(f"G-DIRN.S {arm}: NOT A RESULT -- premise does not "
                           f"reproduce, N={n} {trip}")
                verdict_bits.append("NOT A RESULT")
            else:
                out.append(f"G-DIRN.S {arm}: N=3 (1 1 1) as registered")
            if "U2" not in eqs:
                out.append(f"G-U2.S {arm}: NOT A RESULT -- U2 absent on a "
                           f"symmetry arm; the premise does not reproduce")
                verdict_bits.append("NOT A RESULT")
            else:
                fl = read_eq_min(log_p, "U2")
                out.append(f"G-U2.S {arm}: U2 present, floor {fl:.6e}")
        else:
            if n == 2:
                out.append(f"G-DIRN.E {arm}: GATE REACHED -- N=2 {trip}")
            else:
                out.append(f"G-DIRN.E {arm}: GATE FAIL -- N={n} {trip}; the "
                           f"change did not take effect. CONDEMNS COMMIT "
                           f"d3f47bfa50944c466ff0bad019b36a7b048a0fae.")
                verdict_bits.append("GATE FAIL")
            if "U2" in eqs:
                out.append(f"G-U2.E {arm}: GATE FAIL -- U2 still printed; the "
                           f"mechanism is not the patch type. CONDEMNS COMMIT "
                           f"d3f47bfa50944c466ff0bad019b36a7b048a0fae.")
                verdict_bits.append("GATE FAIL")
            else:
                out.append(f"G-U2.E {arm}: GATE REACHED -- U2 absent from every "
                           f"printed block")

    # G-GUARDS: did the in-container guards RUN? Their markers are read from the
    # arm's own docker log. A zero that cannot distinguish "checked and found
    # nothing" from "did not check" must refuse, so a missing marker -- or a
    # fields_checked count of zero -- makes the arm NOT A RESULT.
    for arm in ARMS:
        log_p = arm_state.get(arm)
        if not isinstance(log_p, str) or not log_p.endswith(".log"):
            continue
        d = os.path.dirname(os.path.dirname(log_p))
        cand = [os.path.join(d, "out", "guards.log"), log_p]
        blob = ""
        for c in cand:
            if os.path.exists(c):
                with open(c, errors="replace") as f:
                    blob += f.read()
        missing = [m for m in GUARD_MARKERS if m not in blob]
        if missing:
            out.append(f"G-GUARDS {arm}: NOT A RESULT -- {len(missing)} guard(s) "
                       f"left no execution marker, so they cannot be shown to have "
                       f"run: {sorted(missing)}")
            arm_state[arm] = "NOT A RESULT"
            verdict_bits.append("NOT A RESULT")
            continue
        m = RE_FIELDS_CHECKED.search(blob)
        n = int(m.group(1)) if m else 0
        if n <= 0:
            out.append(f"G-GUARDS {arm}: NOT A RESULT -- G-EMPTY reported "
                       f"fields_checked={n}; it examined nothing")
            arm_state[arm] = "NOT A RESULT"
            verdict_bits.append("NOT A RESULT")
            continue
        out.append(f"G-GUARDS {arm}: all {len(GUARD_MARKERS)} guards left an "
                   f"execution marker; G-EMPTY examined {n} field(s)")

    # G-TOL: neither arm may have stopped on tolerance. Justified on EQUAL
    # ITERATION COUNT alone -- if either arm stops early the comparison is a
    # three-variable one. It does NOT rest on the falsified convergence account:
    # registration section 1a measures U2 out of the declared quantity, so no
    # gate here predicts that removing U2 changes convergence.
    for arm in ARMS:
        log_p = arm_state.get(arm)
        if not isinstance(log_p, str) or not log_p.endswith(".log"):
            continue
        early = False
        with open(log_p, errors="replace") as f:
            for line in f:
                if RE_CONVERGED.search(line):
                    early = True
                    break
        if early:
            out.append(f"G-TOL {arm}: GATE FAIL -- a tolerance-satisfied line is "
                       f"present; the arms did not run equal iteration counts")
            verdict_bits.append("GATE FAIL")
        else:
            out.append(f"G-TOL {arm}: stop was the fixed iteration count, not a "
                       f"tolerance")

    # R-MAXRES and R-DECL -- REPORTED, NEVER GATED. Neither appends to
    # verdict_bits. R-MAXRES is the per-iteration max over PRINTED channels,
    # which is not the quantity the solver declares on; R-DECL counts the
    # solver's own declarations. Registered expectation: neither arm declares.
    for arm in ARMS:
        log_p = arm_state.get(arm)
        if not isinstance(log_p, str) or not log_p.endswith(".log"):
            continue
        best, cur, ndecl = None, {}, 0
        with open(log_p, errors="replace") as f:
            for line in f:
                if RE_TIME.match(line):
                    if cur:
                        v = max(cur.values())
                        best = v if best is None else min(best, v)
                    cur = {}
                    continue
                m = RE_EQ.match(line)
                if m:
                    cur[m.group(1)] = float(m.group(2))
                    continue
                if RE_CONVERGED.search(line):
                    ndecl += 1
        if cur:
            v = max(cur.values())
            best = v if best is None else min(best, v)
        if best is None:
            out.append(f"R-MAXRES {arm} [REPORTED]: no residual blocks read")
        else:
            out.append(f"R-MAXRES {arm} [REPORTED]: min-over-iterations of the "
                       f"max over PRINTED channels = {best:.6e}")
        out.append(f"R-DECL {arm} [REPORTED]: {ndecl} tolerance-satisfied "
                   f"declaration(s); registered expectation is 0")

    # G-STAT then G-COEF, per pair, each on its OWN operating point's anchor.
    for mesh, s_arm, e_arm in PAIRS:
        anc = DRIFT[mesh]
        gated = anc["gated"]
        tag = "GATED" if gated else "REPORTED (cross-grid proxy anchor)"
        logs = {a: arm_state.get(a) for a in (s_arm, e_arm)}
        if not all(isinstance(v, str) and v.endswith(".log") for v in logs.values()):
            out.append(f"G-COEF {mesh}: NOT A RESULT -- an arm of the pair did "
                       f"not complete")
            if gated:
                verdict_bits.append("NOT A RESULT")
            continue
        means, stat_ok = {}, True
        for a, p in logs.items():
            cl, cd = read_coefs(p)
            if len(cl) < 10 or len(cd) < 10:
                out.append(f"G-STAT {a}: NOT A RESULT -- fewer than 10 samples")
                stat_ok = False
                continue
            scl, scd = spread(cl[-10:]), spread(cd[-10:])
            if scl > STAT_MULT * anc["CL"] or scd > STAT_MULT * anc["CD"]:
                out.append(f"G-STAT {a}: NOT A RESULT -- last-10 spread CL "
                           f"{scl:.6e} CD {scd:.6e} against {STAT_MULT}x anchor "
                           f"CL {anc['CL']:.6e} CD {anc['CD']:.6e}")
                stat_ok = False
            else:
                out.append(f"G-STAT {a}: stationary, last-10 spread CL {scl:.6e} "
                           f"CD {scd:.6e}")
            means[a] = (sum(cl[-10:]) / 10, sum(cd[-10:]) / 10)
        if not stat_ok:
            out.append(f"G-COEF {mesh}: NOT A RESULT -- stationarity precondition "
                       f"not met; no coefficient comparison is admissible")
            if gated:
                verdict_bits.append("NOT A RESULT")
            continue
        for j, q in enumerate(("CL", "CD")):
            ms, me = means[s_arm][j], means[e_arm][j]
            drel = abs(me - ms) / abs(ms)
            if drel <= anc[q]:
                lab = "GATE REACHED -- no contamination detected at this " \
                      "instrument's resolution"
            elif drel <= CONTAM_MULT * anc[q]:
                lab = "NOT A RESULT -- larger than drift, smaller than " \
                      f"{CONTAM_MULT:g}x drift; this instrument cannot separate them"
            else:
                lab = "GATE FAIL -- CONTAMINATION"
            out.append(f"G-COEF {mesh} {q} [{tag}]: mean_S {ms!r} mean_E {me!r} "
                       f"drel {drel:.6e} vs drift {anc[q]:.6e} -> {lab}")
            if gated:
                verdict_bits.append(lab.split(" --")[0])

    # G-CAP, G-CEIL, G-NP.
    total = 0.0
    for arm, (_, _, _, _, _, ranks, cap, tmo) in ARMS.items():
        p = os.path.join(root, arm, "out", "core_min.txt")
        if not os.path.exists(p):
            out.append(f"G-CAP {arm}: PENDING -- no cost record")
            continue
        cm = float(open(p).read().strip())
        total += cm
        if ranks != 1:
            out.append(f"G-NP {arm}: GATE FAIL -- ranks {ranks} != 1")
            verdict_bits.append("GATE FAIL")
        if cm > cap:
            out.append(f"G-CAP {arm}: GATE FAIL -- {cm:.4f} > cap {cap}")
            verdict_bits.append("GATE FAIL")
        else:
            out.append(f"G-CAP {arm}: {cm:.4f} core-min of cap {cap} "
                       f"(TMO {tmo} s)")
    if total:
        if total > ITEM_CEILING_CORE_MIN:
            out.append(f"G-CEIL: GATE FAIL -- {total:.4f} > ceiling "
                       f"{ITEM_CEILING_CORE_MIN}")
            verdict_bits.append("GATE FAIL")
        else:
            out.append(f"G-CEIL: {total:.4f} core-min of {ITEM_CEILING_CORE_MIN}")

    for arm, st in arm_state.items():
        if st in ("BLOCKED", "NOT A RESULT"):
            verdict_bits.append(st)

    if "NOT A RESULT" in verdict_bits:
        verdict = "NOT A RESULT"
    elif "GATE FAIL" in verdict_bits:
        verdict = "GATE FAIL"
    elif "BLOCKED" in verdict_bits:
        verdict = "BLOCKED"
    elif verdict_bits:
        verdict = "GATE REACHED"
    else:
        verdict = "PENDING"
    return out, verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root")
    a = ap.parse_args()

    try:
        log = controls(a.root)
    except Refuse as e:
        print(f"A1ZE_CONTROLS REFUSED -- {e}")
        print("A1ZE_VERDICT NOT A RESULT")
        return 2
    for line in log:
        print(f"CONTROL {line}")
    print(f"A1ZE_BIRTH {len(log)} readers born, both legs proved on P2n and P4")

    if a.selftest and not a.root:
        print("A1ZE_SELFTEST OK -- controls only, no run root graded")
        return 0
    if not a.root:
        print("A1ZE_VERDICT PENDING -- no run root given")
        return 0
    if not os.path.isdir(a.root):
        print(f"A1ZE_VERDICT PENDING -- run root absent: {a.root}")
        return 0

    lines, verdict = grade(a.root)
    for line in lines:
        print(line)
    if verdict == "PASS":
        print("A1ZE_VERDICT NOT A RESULT -- VERDICT_CEILING is GATE REACHED and "
              "this path emitted PASS; the grading path is defective")
        return 2
    print(f"A1ZE_VERDICT {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
