#!/usr/bin/env python3
# =============================================================================
# PERMISSION: NOT_FROZEN -- DRAFT.  NOT COMMITTED BY ITS AUTHOR.
#
# A5P -- U-BEND PRIMAL PLATEAU-BREAKING LADDER -- GRADER
#
# Grades one arm of the A5P ladder against the gates frozen in
#   cases/dafoam/ladder-a/A5/curriculum_A5P/PREREGISTRATION.md
# Every threshold below is a literal from that document.  This file IS the
# grading path fixed at the pre-registration commit (CLAUDE.md rule 2); it is
# hashed against the committed blob before any arm is graded.
#
# THREE DISCIPLINES THIS FILE IMPLEMENTS, EACH PAID FOR BY A NAMED FAILURE:
#
#  (1) initRes ONLY, NEVER finalRes  (N-D44).  DAFoam's accepted quantity is
#      the max over per-equation INITIAL residuals of the final outer
#      iteration, U entering by its MEDIAN component.  A comparator built on
#      finalRes is structurally blind.  The gate region of this file is
#      delimited by the two markers GATE-REGION-BEGIN / GATE-REGION-END and
#      the grader GREPS ITS OWN SOURCE and REFUSES if the forbidden token
#      appears between them.  See selfcheck_no_forbidden_token().
#
#  (2) A FIELD-BOUNDEDNESS CHECK BESIDE THE RESIDUAL GATE  (N-D45).  A
#      diverging field drives its own NORMALISED initial residual toward zero,
#      so a residual gate ALONE reports its best number when the solution is
#      worst -- measured on A4, which passed its accept test by 17,429x while
#      `omega Residual Norm2` stood at 1.13e+35 and omega was clipped at both
#      bounds every iteration.  An arm whose residual IMPROVES while ANY field
#      is being clipped is NOT A RESULT here, and the residual is PRINTED
#      BESIDE the Bounding count so the anti-correlation is visible on the
#      face of the row.
#
#  (3) PLANTED-ZERO CONTROLS THAT EXECUTE  (CLAUDE.md rule 3).  A zero from a
#      reader not shown able to see a non-zero is not evidence.  Before ANY
#      arm is graded this file plants a known residual BY LINE INDEX, plants a
#      Bounding line, and reads both back through the REAL path; it also
#      checks a must-be-absent sentinel so a reader that says yes to
#      everything is caught.  Any control failure => exit 2, grade nothing.
#
# EXIT CODES
#   0  graded (the verdict is on stdout; a GATE FAIL is still exit 0 -- the
#      verdict is the product, not the exit status)
#   2  REFUSED -- a planted-zero control failed, the decile has too few
#      samples, the self-check tripped, or an input could not be read.
#      A refusal NEVER degrades into a grade.
#   3  usage error
# =============================================================================

import argparse
import glob
import gzip
import hashlib
import os
import re
import shutil
import statistics
import sys
import tempfile

VERSION = "A5P-grade 0.1 DRAFT"

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS.  Every one is a literal from PREREGISTRATION.md.
# ---------------------------------------------------------------------------
END_TIME              = 5000        # PREREG 3.0
G1_P_INITRES_MAX      = 2.057e-05   # PREREG 4.1  -- one order below P0's 2.0568e-04
DECILE_FIRST_ITER     = 4500        # PREREG 4.2
DECILE_MIN_SAMPLES    = 5           # PREREG 4.2  -- ASSERTED, never weakened
SPREAD_BREAK_MIN      = 1.0e-03     # PREREG 4.2  -- G2 threshold
SPREAD_PLATEAU_MAX    = 1.0e-06     # PREREG 4.3  -- the falsifier

# P0 baseline reproduction (PREREG 3.1), to 6 significant figures
P0_P_INITRES_AT_1000  = 2.0568149526e-04
P0_NUTILDA_AT_1000    = 3.6201075e-04
P0_REPRO_SIGFIGS      = 6

# F-checks (PREREG 4.4)
F1_BOUNDING_MAX       = 0           # any Bounding line at all is a failure
F3A_YPLUS_MAX_MAX     = 110.7       # 2 x P0's 55.325
F3A_YPLUS_MIN_MIN     = 0.0         # strict >
F3B_NUTILDA_MIN       = 0.0         # >= 0
F3B_NUTILDA_MAX_MULT  = 1.0e+03     # x P0's max
F3C_UMAG_MAX          = 84.0        # 10 x U0 = 10 x 8.4 m/s (runScript.py:53)
F3D_T_LO              = 250.0
F3D_T_HI              = 400.0
F2_NORM2_MAX          = 1.0e+04     # PREREG 4.4 -- absolute ceiling on every
                                    # `Residual Norm2`.  MEASURED baselines:
                                    # Total 59.324 (tightened) / 55.776 (stock);
                                    # worst per-equation 43.504 / 41.160 (T).
                                    # A4's diverged omega stood at 1.13e+35
                                    # (N-D45), so this ceiling sits 168x above
                                    # a healthy A5 and 31 orders below A4's.
F4_OBJ_FINDING_FRAC   = 0.01        # >1% delta from P0 is a FINDING, not a refusal
P0_OBJ_TP1_MINUS_TP2  = 52.34517755

# Planted-zero controls (PREREG 4.6)
PLANT_P               = 7.654321e-09
PLANT_BOUNDING_LINE   = ("Bounding nuTilda, min: -1.0000e-09 "
                         "max: 1.0000e+00 average: 1.0000e-04")
ABSENT_SENTINEL       = "A5P_PLANT_MUST_BE_ABSENT"

# The fixed verdict vocabulary (CLAUDE.md rule 1).  Nothing else may be emitted.
VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

FORBIDDEN_TOKEN = "final" + "Res"   # split so the literal is not itself in the
                                    # gate region; see selfcheck below.


# ===========================================================================
# READERS.  Nothing below reads the forbidden token; the initRes regex stops
# at whitespace and never needs to know what follows on the line.
# ===========================================================================

def _open_maybe_gz(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", errors="replace")
    return open(path, "rt", errors="replace")


def read_log(path):
    """Return the log as a list of lines.  Refuses rather than returning []."""
    if not os.path.isfile(path):
        refuse("log not found: %s" % path)
    with _open_maybe_gz(path) as fh:
        lines = fh.read().splitlines()
    if not lines:
        refuse("log is EMPTY: %s -- an empty read is not a zero, it is a refusal"
               % path)
    return lines


# >>> GATE-REGION-BEGIN
# ---------------------------------------------------------------------------
# EVERYTHING BETWEEN THESE TWO MARKERS EVALUATES A GATE.  The forbidden token
# must not appear here.  selfcheck_no_forbidden_token() enforces it against
# THIS FILE'S OWN BYTES, not against a copy.
# ---------------------------------------------------------------------------

RE_TIME     = re.compile(r"^Time = (\d+)\s*$")
RE_INITRES  = re.compile(r"^\s*(\S+) initRes:\s*([-+0-9.eEdD]+)")
RE_BOUNDING = re.compile(r"^Bounding ")
RE_YPLUS    = re.compile(r"^yPlus min:\s*([-+0-9.eE]+)\s+max:\s*([-+0-9.eE]+)"
                         r"\s+mean:\s*([-+0-9.eE]+)")
RE_TP       = re.compile(r"^(TP1|TP2|HFX):\s*([-+0-9.eE]+)")
RE_EXECTIME = re.compile(r"^ExecutionTime = ([0-9.]+) s")
RE_END      = re.compile(r"^End\s*$")
# N-D45: the per-equation and total residual NORMS, which are the quantity a
# residual gate alone cannot see.  U is printed as a bracketed vector.
RE_NORM2    = re.compile(r"^(\S+) Residual Norm2:\s*(.+?)\s*$")


def parse_blocks(lines):
    """Split a solver log into per-iteration blocks.

    Returns (blocks, meta) where blocks is an ordered list of dicts:
        {'iter': int, 'res': {eqn: initRes}, 'yplus': (min,max,mean)|None,
         'obj': {'TP1':v,'TP2':v,...}, 'exec_s': float|None}
    and meta carries the whole-log facts rule 4 needs.
    """
    blocks, cur = [], None
    meta = {"bounding_count": 0, "bounding_lines": [], "has_end": False,
            "exec_count": 0, "n_lines": len(lines),
            "has_residual_norm2": False, "norm2": {}}
    for ln in lines:
        if RE_BOUNDING.match(ln):
            meta["bounding_count"] += 1
            if len(meta["bounding_lines"]) < 5:
                meta["bounding_lines"].append(ln.strip())
        mn = RE_NORM2.match(ln)
        if mn:
            meta["has_residual_norm2"] = True
            raw = mn.group(2).replace("(", " ").replace(")", " ")
            vals = []
            for tok in raw.split():
                try:
                    vals.append(float(tok))
                except ValueError:
                    pass
            if vals:
                meta["norm2"][mn.group(1)] = vals
        if RE_END.match(ln):
            meta["has_end"] = True
        m = RE_TIME.match(ln)
        if m:
            cur = {"iter": int(m.group(1)), "res": {}, "yplus": None,
                   "obj": {}, "exec_s": None}
            blocks.append(cur)
            continue
        if cur is None:
            continue
        m = RE_INITRES.match(ln)
        if m:
            try:
                cur["res"][m.group(1)] = float(m.group(2).replace("D", "E"))
            except ValueError:
                pass
            continue
        m = RE_YPLUS.match(ln)
        if m:
            cur["yplus"] = (float(m.group(1)), float(m.group(2)),
                            float(m.group(3)))
            continue
        m = RE_TP.match(ln)
        if m:
            cur["obj"][m.group(1)] = float(m.group(2))
            continue
        m = RE_EXECTIME.match(ln)
        if m:
            cur["exec_s"] = float(m.group(1))
            meta["exec_count"] += 1
    return blocks, meta


def p_initres_series(blocks):
    """[(iter, p initRes)] for every block that printed one."""
    return [(b["iter"], b["res"]["p"]) for b in blocks if "p" in b["res"]]


def primal_max_res(block):
    """N-D44: max over per-equation INITIAL residuals, U by MEDIAN component.

    Reported, never gated -- this item's registered gate is on p (PREREG 4.5).
    Returns (value, equation_name) or (None, None).
    """
    r = dict(block["res"])
    ucomp = [r.pop(k) for k in ("U0", "U1", "U2") if k in r]
    cand = list(r.items())
    if len(ucomp) == 3:
        cand.append(("U(median)", statistics.median(ucomp)))
    elif ucomp:
        cand.append(("U(partial-max)", max(ucomp)))
    if not cand:
        return (None, None)
    name, val = max(cand, key=lambda kv: kv[1])
    return (val, name)


def decile_samples(series, first_iter=DECILE_FIRST_ITER):
    return [v for (it, v) in series if it >= first_iter]


def decile_spread(samples):
    """(max - min) / max.  Refuses on a non-positive max rather than dividing."""
    mx, mn = max(samples), min(samples)
    if mx <= 0.0:
        return None
    return (mx - mn) / mx


def is_monotone_non_increasing(samples):
    return all(samples[i + 1] <= samples[i] for i in range(len(samples) - 1))


def eval_g1(p_at_end):
    """PREREG 4.1: p initRes(endTime) <= 2.057e-05."""
    return (p_at_end is not None) and (p_at_end <= G1_P_INITRES_MAX)


def eval_g2(samples):
    """PREREG 4.2: monotone non-increasing AND spread >= 1.0e-03."""
    sp = decile_spread(samples)
    if sp is None:
        return (False, None, False)
    mono = is_monotone_non_increasing(samples)
    return (mono and sp >= SPREAD_BREAK_MIN, sp, mono)


def eval_f2_norm2(norm2):
    """PREREG 4.4 F2 (N-D45).  Every `Residual Norm2` must be finite and within
    the absolute ceiling.  Returns (ok, worst_name, worst_value).

    This is the check A4 did not have: its residual gate read 5.74e-04 and
    passed by 17,429x while this quantity stood at 1.13e+35.
    """
    worst_n, worst_v = None, None
    for name, vals in norm2.items():
        for v in vals:
            if worst_v is None or v > worst_v:
                worst_n, worst_v = name, v
    if worst_v is None:
        return (None, None, None)          # absent, not pass and not fail
    if worst_v != worst_v or worst_v in (float("inf"), float("-inf")):
        return (False, worst_n, worst_v)   # NaN / inf
    return (worst_v <= F2_NORM2_MAX, worst_n, worst_v)


def is_new_plateau(spread):
    """PREREG 4.3 falsifier: spread < 1.0e-06 => NEW PLATEAU."""
    return (spread is not None) and (spread < SPREAD_PLATEAU_MAX)

# <<< GATE-REGION-END


# ===========================================================================
# FIELD READING FROM DISK (F3b/c/d).  Decomposed runs: processor*/<t>/<field>.
# ===========================================================================

RE_NUMBER = re.compile(r"^[-+0-9.eE]+$")


def _field_values(path):
    """Crude but sufficient OpenFOAM ASCII internalField reader.

    Returns a flat list of floats (vector components flattened) or None if the
    internalField is uniform/unparseable -- the caller distinguishes the two.
    """
    with _open_maybe_gz(path) as fh:
        txt = fh.read()
    m = re.search(r"internalField\s+uniform\s+\(?([^;)]+)\)?;", txt)
    if m:
        return [float(x) for x in m.group(1).split()]
    m = re.search(r"internalField\s+nonuniform\s+List<(scalar|vector)>\s*\n"
                  r"(\d+)\s*\n\(\s*\n(.*?)\n\)\s*\n?;", txt, re.S)
    if not m:
        return None
    body = m.group(3)
    vals = []
    for tok in body.replace("(", " ").replace(")", " ").split():
        if RE_NUMBER.match(tok):
            try:
                vals.append(float(tok))
            except ValueError:
                pass
    return vals


def field_minmax(case_dir, time_name, field):
    """Global min/max of one field across all processor dirs.

    Returns (min, max, n_files).  n_files == 0 means the field was NOT FOUND,
    which is a refusal at the call site, not a zero.
    """
    pats = [os.path.join(case_dir, "processor*", str(time_name), field),
            os.path.join(case_dir, "processor*", str(time_name), field + ".gz"),
            os.path.join(case_dir, str(time_name), field),
            os.path.join(case_dir, str(time_name), field + ".gz")]
    files = []
    for p in pats:
        files.extend(sorted(glob.glob(p)))
    lo = hi = None
    n = 0
    for f in files:
        vals = _field_values(f)
        if not vals:
            continue
        n += 1
        flo, fhi = min(vals), max(vals)
        lo = flo if lo is None else min(lo, flo)
        hi = fhi if hi is None else max(hi, fhi)
    return (lo, hi, n)


def vector_mag_max(case_dir, time_name, field):
    """Max |vector| across processor dirs.  Returns (maxmag, n_files)."""
    pats = [os.path.join(case_dir, "processor*", str(time_name), field),
            os.path.join(case_dir, "processor*", str(time_name), field + ".gz"),
            os.path.join(case_dir, str(time_name), field),
            os.path.join(case_dir, str(time_name), field + ".gz")]
    files = []
    for p in pats:
        files.extend(sorted(glob.glob(p)))
    best, n = None, 0
    for f in files:
        vals = _field_values(f)
        if not vals or len(vals) % 3 != 0:
            continue
        n += 1
        for i in range(0, len(vals), 3):
            m = (vals[i] ** 2 + vals[i + 1] ** 2 + vals[i + 2] ** 2) ** 0.5
            best = m if best is None else max(best, m)
    return (best, n)


# ===========================================================================
# REFUSAL
# ===========================================================================

def refuse(msg):
    print("")
    print("REFUSED (exit 2): %s" % msg)
    print("A refusal is not a grade and never degrades into one "
          "(CLAUDE.md rule 4, comparators refuse rather than degrade).")
    sys.exit(2)


# ===========================================================================
# THE PLANTED-ZERO CONTROLS (PREREG 4.6).  These EXECUTE before any grade.
# Each plants BY LINE INDEX into a scratch copy -- never a regex-replace-all,
# never the arm log on disk -- and reads back through the REAL path.
# ===========================================================================

def _plant_p_by_line_index(lines):
    """Rewrite the LAST `p initRes:` line's value to PLANT_P, by index.

    Returns (new_lines, index) or (None, None) if no such line exists.
    """
    idx = None
    for i, ln in enumerate(lines):
        m = RE_INITRES.match(ln)
        if m and m.group(1) == "p":
            idx = i
    if idx is None:
        return (None, None)
    out = list(lines)
    out[idx] = "p initRes: %.7e" % PLANT_P
    return (out, idx)


def control_plant_residual(lines, reader=None):
    """CONTROL A.  Plant PLANT_P into the final `p initRes:` line and require
    the reader to see it AND G1 to FLIP to True.

    `reader` is injectable so the selftest can substitute a DELIBERATELY BROKEN
    reader and prove this control can FAIL -- a control that cannot fail is not
    a control.
    Returns (ok, detail).
    """
    reader = reader or (lambda ls: p_initres_series(parse_blocks(ls)[0]))
    before = reader(lines)
    if not before:
        return (False, "the unplanted read found NO `p initRes:` samples at all")
    g1_before = eval_g1(before[-1][1])
    planted, idx = _plant_p_by_line_index(lines)
    if planted is None:
        return (False, "no `p initRes:` line to plant into")
    after = reader(planted)
    if not after:
        return (False, "the reader saw nothing after the plant")
    seen = after[-1][1]
    if abs(seen - PLANT_P) > 1e-18:
        return (False, "reader returned %.9e, not the planted %.9e "
                       "(planted at line index %d)" % (seen, PLANT_P, idx))
    g1_after = eval_g1(seen)
    if g1_before is True:
        return (False, "the UNPLANTED log already satisfies G1, so the flip "
                       "proves nothing; control is vacuous on this input")
    if g1_after is not True:
        return (False, "G1 did not FLIP on the plant (before=%s after=%s)"
                       % (g1_before, g1_after))
    return (True, "reader saw %.9e at line index %d; G1 flipped %s -> %s"
                  % (seen, idx, g1_before, g1_after))


def control_plant_bounding(lines, counter=None):
    """CONTROL B.  Insert one Bounding line by index and require F1 0 -> 1."""
    counter = counter or (lambda ls: parse_blocks(ls)[1]["bounding_count"])
    before = counter(lines)
    if before != 0:
        return (False, "the arm log ALREADY has %d Bounding lines, so the "
                       "0->1 flip cannot be demonstrated on it" % before)
    idx = min(len(lines), max(1, len(lines) // 2))
    planted = lines[:idx] + [PLANT_BOUNDING_LINE] + lines[idx:]
    after = counter(planted)
    if after != before + 1:
        return (False, "Bounding count went %d -> %d, expected %d -> %d"
                       % (before, after, before, before + 1))
    return (True, "Bounding count flipped %d -> %d (planted at line index %d)"
                  % (before, after, idx))


def control_absent_sentinel(lines):
    """CONTROL C.  A token present in no log must read as 0 through the same
    path -- so a reader that says yes to everything is caught."""
    n = sum(1 for ln in lines if ABSENT_SENTINEL in ln)
    if n != 0:
        return (False, "must-be-absent sentinel %s was found %d times"
                       % (ABSENT_SENTINEL, n))
    planted = lines + [ABSENT_SENTINEL]
    n2 = sum(1 for ln in planted if ABSENT_SENTINEL in ln)
    if n2 != 1:
        return (False, "the sentinel reader cannot see its own plant "
                       "(got %d, expected 1)" % n2)
    return (True, "absent=0 and its own plant reads 1")


def run_all_controls(lines):
    """All three controls, in order.  ANY failure => exit 2, grade nothing."""
    print("PLANTED-ZERO CONTROLS (CLAUDE.md rule 3) -- these run BEFORE any grade")
    results = [("A residual plant", control_plant_residual(lines)),
               ("B Bounding plant", control_plant_bounding(lines)),
               ("C absent sentinel", control_absent_sentinel(lines))]
    bad = []
    for name, (ok, detail) in results:
        print("  control %-18s %-7s  %s" % (name, "OK" if ok else "FAILED", detail))
        if not ok:
            bad.append(name)
    if bad:
        refuse("planted-zero control(s) failed: %s. A zero from a reader not "
               "shown able to see a non-zero is not evidence." % ", ".join(bad))
    print("  -> all three controls passed; the reader is demonstrably live.")
    print("")


# ===========================================================================
# SELF-CHECK: the forbidden token must not appear in the gate region (N-D44)
# ===========================================================================

def selfcheck_no_forbidden_token(src_path=None):
    """Grep THIS FILE'S OWN BYTES between the gate-region markers.

    Returns (ok, detail).  Asserts the markers exist -- a check whose region is
    empty is the planted zero this lab keeps paying for.
    """
    src_path = src_path or os.path.abspath(__file__)
    try:
        with open(src_path, "rt", errors="replace") as fh:
            src = fh.read()
    except OSError as e:
        return (False, "cannot read own source %s: %s" % (src_path, e))
    b = src.find(">>> GATE-REGION-BEGIN")
    e = src.find("<<< GATE-REGION-END")
    if b < 0 or e < 0 or e <= b:
        return (False, "gate-region markers missing or inverted "
                       "(begin=%d end=%d) -- the check would be vacuous" % (b, e))
    region = src[b:e]
    if len(region.splitlines()) < 20:
        return (False, "gate region is only %d lines -- implausibly small, "
                       "refusing a vacuous check" % len(region.splitlines()))
    n = region.count(FORBIDDEN_TOKEN)
    if n:
        return (False, "the forbidden token appears %d time(s) in the gate "
                       "region: gates must read initRes only (N-D44)" % n)
    return (True, "gate region is %d lines and contains 0 occurrences of the "
                  "forbidden token" % len(region.splitlines()))


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ===========================================================================
# RULE-4 COMPLETION (CLAUDE.md rule 4), applied to an arm
# ===========================================================================

def check_completion(blocks, meta, rc, end_time):
    """Returns (ok, [failed clause strings]).  All-or-nothing."""
    fails = []
    if rc is not None and rc != 0:
        fails.append("rc = %s (must be 0)" % rc)
    if not meta["has_end"]:
        fails.append("no `End` line")
    if not blocks:
        fails.append("no `Time = ` blocks at all")
    else:
        last = blocks[-1]["iter"]
        if last != end_time:
            fails.append("last time %d != endTime %d" % (last, end_time))
    if meta["exec_count"] == 0:
        fails.append("no `ExecutionTime = ` lines -- the solver never "
                     "completed a step")
    n_steps = sum(1 for b in blocks if b["exec_s"] is not None)
    if meta["exec_count"] != n_steps:
        fails.append("ExecutionTime count %d != printed steps %d"
                     % (meta["exec_count"], n_steps))
    return (not fails, fails)


# ===========================================================================
# THE GRADE
# ===========================================================================

def grade_arm(arm, log_path, case_dir, rc, is_baseline, end_time=END_TIME,
              p0_nutilda_max=None):
    lines = read_log(log_path)

    ok, detail = selfcheck_no_forbidden_token()
    print("SELF-CHECK (N-D44, initRes only): %s -- %s"
          % ("OK" if ok else "FAILED", detail))
    if not ok:
        refuse("grader self-check failed: %s" % detail)
    print("")

    run_all_controls(lines)

    blocks, meta = parse_blocks(lines)
    series = p_initres_series(blocks)

    print("=" * 74)
    print("A5P ARM %s -- GRADE" % arm)
    print("=" * 74)
    print("log            : %s" % os.path.abspath(log_path))
    print("log md5        : %s" % md5_of(log_path))
    print("blocks parsed  : %d ; p initRes samples: %d" % (len(blocks), len(series)))
    print("")

    # ---- rule 4 completion -------------------------------------------------
    comp_ok, comp_fails = check_completion(blocks, meta, rc, end_time)
    print("RULE-4 COMPLETION: %s" % ("OK" if comp_ok else "FAILED"))
    for f in comp_fails:
        print("   - %s" % f)
    print("")

    # ---- F1 Bounding -------------------------------------------------------
    nb = meta["bounding_count"]
    p_end = None
    for (it, v) in series:
        if it == end_time:
            p_end = v
    if p_end is None and series:
        p_end = series[-1][1]

    # ---- decile ------------------------------------------------------------
    dec = decile_samples(series)
    if len(dec) < DECILE_MIN_SAMPLES:
        refuse("the decile (iterations >= %d) holds only %d printed sample(s); "
               "PREREGISTRATION.md 4.2 asserts at least %d. The grader refuses "
               "rather than evaluating G2 on a weaker basis than the one frozen."
               % (DECILE_FIRST_ITER, len(dec), DECILE_MIN_SAMPLES))
    spread = decile_spread(dec)
    if spread is None:
        refuse("decile max is non-positive (%r); the spread is undefined and "
               "will not be faked" % max(dec))
    g1 = eval_g1(p_end)
    g2, _sp, mono = eval_g2(dec)
    plateau = is_new_plateau(spread)
    pmr, pmr_eq = primal_max_res(blocks[-1]) if blocks else (None, None)

    print("RESIDUAL GATE (initRes only -- N-D44)")
    print("  p initRes(%d)                = %.10e" % (end_time, p_end)
          if p_end is not None else "  p initRes(end)               = ABSENT")
    print("  G1  p initRes <= %.4e   : %s" % (G1_P_INITRES_MAX, g1))
    print("  decile (iter >= %d)        : %d samples" % (DECILE_FIRST_ITER, len(dec)))
    print("        values               : %s" % ", ".join("%.6e" % v for v in dec))
    print("        monotone non-increasing: %s" % mono)
    print("        spread (max-min)/max : %.6e   (G2 needs >= %.1e)"
          % (spread, SPREAD_BREAK_MIN))
    print("  G2                          : %s" % g2)
    print("  BREAK = G1 AND G2           : %s" % (g1 and g2))
    print("  falsifier: spread < %.1e  : %s%s"
          % (SPREAD_PLATEAU_MAX, plateau,
             "  <== NEW PLATEAU" if plateau else ""))
    if pmr is not None:
        print("  primalMaxRes (N-D44, REPORTED not gated) = %.6e  on %s"
              % (pmr, pmr_eq))
        print("  DAFoam accept floor = primalMinResTol 1e-8 x "
              "primalMinResTolDiff 1e7 = 0.1 (runScript.py:59-60);")
        print("  this arm passes DAFoam's own test by %.1fx -- which is why the "
              "plateau never tripped a refusal." % (0.1 / pmr))
    print("")

    # ---- field-boundedness, BESIDE the residual gate (N-D45) ---------------
    print("FIELD-BOUNDEDNESS CHECK, BESIDE THE RESIDUAL GATE (N-D45)")
    print("  F1 Bounding line count      = %d   (threshold: must be %d)"
          % (nb, F1_BOUNDING_MAX))
    # THE ANTI-CORRELATION, PRINTED SIDE BY SIDE.  This is the whole point of
    # N-D45: the residual looks BEST when the solution is WORST.
    print("  ---- N-D45 side-by-side: residual BESIDE the clip count ----")
    print("       p initRes(%d) = %-18s | Bounding lines = %d"
          % (end_time, ("%.6e" % p_end) if p_end is not None else "ABSENT", nb))
    for bl in meta["bounding_lines"]:
        print("       clipped: %s" % bl)
    f_fails = []
    if nb > F1_BOUNDING_MAX:
        f_fails.append("F1: %d Bounding line(s) -- a field is being clipped" % nb)

    # F2 -- the quantity a residual gate alone cannot see (N-D45)
    f2_ok, f2_eq, f2_v = eval_f2_norm2(meta["norm2"])
    if f2_ok is None:
        print("  F2 `Residual Norm2`         : ABSENT from this log. It IS present "
              "in both A5 baselines (6 lines each),")
        print("       so its absence here means the arm did not reach the print. "
              "F2 cannot pass on an absent reading.")
        f_fails.append("F2: no `Residual Norm2` line -- a check that did not run "
                       "is not a pass")
    else:
        print("  F2 worst Residual Norm2     = %.6e  on %s   (ceiling %.1e)"
              % (f2_v, f2_eq, F2_NORM2_MAX))
        print("       all: %s" % ", ".join(
            "%s=%s" % (k, "/".join("%.4g" % x for x in v))
            for k, v in sorted(meta["norm2"].items())))
        if not f2_ok:
            f_fails.append("F2: %s Residual Norm2 = %.6e exceeds %.1e -- a field "
                           "is diverging while the residual gate reads small "
                           "(N-D45)" % (f2_eq, f2_v, F2_NORM2_MAX))

    # F3a yPlus from the log
    yp = blocks[-1]["yplus"] if blocks else None
    if yp is None:
        f_fails.append("F3a: no `yPlus min/max/mean` line in the final block")
        print("  F3a yPlus                   : ABSENT")
    else:
        print("  F3a yPlus min/max           = %.6g / %.6g   (need min > %.1f, "
              "max <= %.1f)" % (yp[0], yp[1], F3A_YPLUS_MIN_MIN, F3A_YPLUS_MAX_MAX))
        if not (yp[0] > F3A_YPLUS_MIN_MIN):
            f_fails.append("F3a: yPlus min %.6g is not > %.1f" % (yp[0], F3A_YPLUS_MIN_MIN))
        if not (yp[1] <= F3A_YPLUS_MAX_MAX):
            f_fails.append("F3a: yPlus max %.6g exceeds %.1f" % (yp[1], F3A_YPLUS_MAX_MAX))

    # F3b/c/d from disk
    if case_dir:
        lo, hi, n = field_minmax(case_dir, end_time, "nuTilda")
        if n == 0:
            f_fails.append("F3b: nuTilda not found at time %d under %s -- "
                           "a missing field is a refusal condition, not a pass"
                           % (end_time, case_dir))
            print("  F3b nuTilda                 : NOT FOUND on disk")
        else:
            cap = (p0_nutilda_max * F3B_NUTILDA_MAX_MULT) if p0_nutilda_max else None
            print("  F3b nuTilda min/max         = %.6g / %.6g  (%d file(s); "
                  "need min >= %g%s)" % (lo, hi, n, F3B_NUTILDA_MIN,
                  ", max <= %.6g" % cap if cap else ", no P0 cap supplied"))
            if lo < F3B_NUTILDA_MIN:
                f_fails.append("F3b: nuTilda min %.6g < %g" % (lo, F3B_NUTILDA_MIN))
            if cap is not None and hi > cap:
                f_fails.append("F3b: nuTilda max %.6g > %.6g" % (hi, cap))

        um, nu = vector_mag_max(case_dir, end_time, "U")
        if nu == 0:
            f_fails.append("F3c: U not found at time %d under %s" % (end_time, case_dir))
            print("  F3c |U| max                 : NOT FOUND on disk")
        else:
            print("  F3c |U| max                 = %.6g m/s  (%d file(s); need "
                  "<= %.1f = 10 x U0)" % (um, nu, F3C_UMAG_MAX))
            if um > F3C_UMAG_MAX:
                f_fails.append("F3c: |U| max %.6g exceeds %.1f m/s" % (um, F3C_UMAG_MAX))

        tlo, thi, nt = field_minmax(case_dir, end_time, "T")
        if nt == 0:
            f_fails.append("F3d: T not found at time %d under %s" % (end_time, case_dir))
            print("  F3d T                       : NOT FOUND on disk")
        else:
            print("  F3d T min/max               = %.6g / %.6g K  (%d file(s); "
                  "need within [%.0f, %.0f])" % (tlo, thi, nt, F3D_T_LO, F3D_T_HI))
            if tlo < F3D_T_LO or thi > F3D_T_HI:
                f_fails.append("F3d: T [%.6g, %.6g] outside [%.0f, %.0f]"
                               % (tlo, thi, F3D_T_LO, F3D_T_HI))
    else:
        f_fails.append("F3b/c/d: no --case-dir supplied, so no field was read "
                       "from disk. A field check that did not run is not a pass.")
        print("  F3b/c/d                     : NOT RUN (no --case-dir)")

    # F4 objective -- a FINDING, never an automatic refusal
    obj = None
    if blocks and "TP1" in blocks[-1]["obj"] and "TP2" in blocks[-1]["obj"]:
        obj = blocks[-1]["obj"]["TP1"] - blocks[-1]["obj"]["TP2"]
        d = abs(obj - P0_OBJ_TP1_MINUS_TP2) / abs(P0_OBJ_TP1_MINUS_TP2)
        print("  F4 TP1-TP2                  = %.8f  (P0 %.8f, delta %.3e)"
              % (obj, P0_OBJ_TP1_MINUS_TP2, d))
        if d > F4_OBJ_FINDING_FRAC:
            print("     FINDING: delta exceeds %.0f%%. The state must be "
                  "inspected before this arm is called a success. NOT an "
                  "automatic refusal (PREREG 4.4)." % (F4_OBJ_FINDING_FRAC * 100))
    else:
        print("  F4 TP1-TP2                  : ABSENT from the final block")
    for f in f_fails:
        print("   - FAILED %s" % f)
    print("")

    # ---- baseline reproduction (P0 only) -----------------------------------
    repro_fail = None
    if is_baseline:
        got_p = got_n = None
        for b in blocks:
            if b["iter"] == 1000:
                got_p = b["res"].get("p")
                got_n = b["res"].get("nuTilda")
        print("P0 BASELINE REPRODUCTION (PREREG 3.1), at iteration 1000")
        for nm, got, exp in (("p", got_p, P0_P_INITRES_AT_1000),
                             ("nuTilda", got_n, P0_NUTILDA_AT_1000)):
            if got is None:
                print("  %-8s : ABSENT at iteration 1000" % nm)
                repro_fail = repro_fail or "%s absent at iteration 1000" % nm
                continue
            rel = abs(got - exp) / abs(exp)
            okr = rel < 10 ** (-(P0_REPRO_SIGFIGS - 1)) * 0.5
            print("  %-8s : got %.10e  expected %.10e  rel %.3e  %s"
                  % (nm, got, exp, rel, "OK" if okr else "MISMATCH"))
            if not okr:
                repro_fail = repro_fail or ("%s reproduced to worse than %d "
                                            "significant figures" % (nm, P0_REPRO_SIGFIGS))
        print("")

    # ---- VERDICT -----------------------------------------------------------
    if is_baseline and repro_fail:
        verdict = "BLOCKED"
        why = ("P0 did not reproduce (%s). A ladder measured against an "
               "irreproducible baseline is not a ladder; no arm is graded."
               % repro_fail)
    elif not comp_ok:
        verdict = "NOT A RESULT"
        why = "rule-4 completion failed: " + "; ".join(comp_fails)
    elif f_fails:
        verdict = "NOT A RESULT"
        why = ("field-boundedness failed BESIDE the residual gate (N-D45): "
               + "; ".join(f_fails)
               + ". An arm whose residual improves while a field is clipped is "
                 "NOT a success.")
    elif g1 and g2:
        verdict = "GATE REACHED"
        why = ("the plateau BROKE: p initRes(%d) = %.6e <= %.4e and the decile "
               "is monotone with spread %.3e >= %.1e."
               % (end_time, p_end, G1_P_INITRES_MAX, spread, SPREAD_BREAK_MIN))
        if arm.upper().startswith("P4"):
            verdict = "GATE REACHED"
            why += (" DIAGNOSTIC ONLY -- PREREG 3.5 binds: a frozen-turbulence "
                    "primal is NEVER a candidate configuration for A5's grid "
                    "triple and may not be promoted to one.")
    elif plateau:
        verdict = "GATE FAIL"
        why = ("NEW PLATEAU at p initRes = %.10e (decile spread %.3e < %.1e). "
               "Registered response: report it. Extending endTime, re-running, "
               "or combining levers are FORBIDDEN (PREREG 4.3)."
               % (p_end, spread, SPREAD_PLATEAU_MAX))
    else:
        verdict = "GATE FAIL"
        why = ("indeterminate drift: spread %.3e lies between %.1e and %.1e; "
               "G1=%s G2=%s." % (spread, SPREAD_PLATEAU_MAX, SPREAD_BREAK_MIN,
                                 g1, g2))

    assert verdict in VOCAB, "verdict outside the fixed vocabulary"
    print("=" * 74)
    print("VERDICT  %s" % verdict)
    print("  %s" % why)
    print("=" * 74)
    return 0


# ===========================================================================
# SELFTEST -- synthetic fixtures, a pass/fail tally, nonzero exit on any fail
# ===========================================================================

def _mk_log(path, p_vals, iters, bounding=0, end=True, yplus=(1.85, 55.3, 23.7),
            tp=(88.11834518, 35.77316763), last_iter=None, nutilda=3.62e-04,
            norm2_p=8.19651084009335):
    """Synthesise a DAFoam-shaped solver log."""
    out = []
    out.append("Running Primal Solver 001")
    for i, (it, pv) in enumerate(zip(iters, p_vals)):
        out.append("Time = %d" % it)
        out.append("")
        out.append("U0 initRes: 2.236362847801647e-06 finalR" + "es: 1.0e-08 nIters: 6")
        out.append("U1 initRes: 5.524654088963006e-06 finalR" + "es: 1.7e-08 nIters: 8")
        out.append("U2 initRes: 1.548647088192214e-05 finalR" + "es: 9.4e-08 nIters: 6")
        out.append("p initRes: %.16g finalR" % pv + "es: 1.2e-06 nIters: 3")
        out.append("T initRes: 1.863008928766540e-05 finalR" + "es: 1.0e-07 nIters: 6")
        out.append("nuTilda initRes: %.10g finalR" % nutilda + "es: 8.1e-07 nIters: 4")
        out.append("TP1: %.8f final: %.8f" % (tp[0], tp[0]))
        out.append("TP2: %.8f final: %.8f" % (tp[1], tp[1]))
        out.append("HFX: 301.8136235323786 final: 301.8136235323786")
        out.append("yPlus min: %g max: %g mean: %g" % yplus)
        out.append("ExecutionTime = %.2f s  ClockTime = %d s" % (3.0 + i * 0.3, 3 + i))
        out.append("")
    for k in range(bounding):
        out.insert(3, "Bounding nuTilda, min: -1e-09 max: 1 average: 1e-04")
    out.append("U Residual Norm2: (%g %g %g)" % (28.35, 24.90, 11.63))
    out.append("p Residual Norm2: %g" % norm2_p)
    out.append("T Residual Norm2: 43.50353040790415")
    out.append("nuTilda Residual Norm2: 0.4913723805389348")
    out.append("phi Residual Norm2: 0.04816627726459843")
    out.append("Total Residual Norm2: %g" % (norm2_p * 7.238))
    if end:
        out.append("End")
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")
    return path


def _mk_fields(case_dir, t, nutilda=(1e-6, 2e-3), umag=8.4, T=(300.0, 305.0)):
    d = os.path.join(case_dir, "processor0", str(t))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "nuTilda"), "w") as fh:
        fh.write("internalField   nonuniform List<scalar>\n3\n(\n%g\n%g\n%g\n)\n;\n"
                 % (nutilda[0], (nutilda[0] + nutilda[1]) / 2, nutilda[1]))
    with open(os.path.join(d, "U"), "w") as fh:
        fh.write("internalField   nonuniform List<vector>\n2\n(\n(%g 0 0)\n(0 0 0)\n)\n;\n"
                 % umag)
    with open(os.path.join(d, "T"), "w") as fh:
        fh.write("internalField   nonuniform List<scalar>\n2\n(\n%g\n%g\n)\n;\n"
                 % (T[0], T[1]))
    return case_dir


def selftest():
    tally = {"pass": 0, "fail": 0}

    def chk(name, cond, detail=""):
        if cond:
            tally["pass"] += 1
            print("  PASS  %-52s %s" % (name, detail))
        else:
            tally["fail"] += 1
            print("  FAIL  %-52s %s" % (name, detail))

    print("=" * 74)
    print("%s -- SELFTEST" % VERSION)
    print("=" * 74)

    tmp = tempfile.mkdtemp(prefix="a5p_selftest_")
    try:
        iters = list(range(100, END_TIME + 1, 100))
        n = len(iters)

        # (1) the forbidden-token self-check on this file's own bytes
        ok, detail = selfcheck_no_forbidden_token()
        chk("self-check: no forbidden token in gate region", ok, detail)

        # (2) the self-check must be able to FAIL -- mutate a copy
        mut = os.path.join(tmp, "mutant.py")
        with open(os.path.abspath(__file__)) as fh:
            src = fh.read()
        b = src.find(">>> GATE-REGION-BEGIN")
        cut = b + len(">>> GATE-REGION-BEGIN")
        src_mut = src[:cut] + "\n# " + FORBIDDEN_TOKEN + "\n" + src[cut:]
        with open(mut, "w") as fh:
            fh.write(src_mut)
        okm, dm = selfcheck_no_forbidden_token(mut)
        chk("self-check DETECTS an injected forbidden token", not okm, dm)

        # (3) plateau log -> GATE FAIL / NEW PLATEAU
        plateau_vals = [2.0568149526e-04 * (1 + 1e-12 * i) for i in range(n)]
        lp = _mk_log(os.path.join(tmp, "plateau.log"), plateau_vals, iters)
        blocks, meta = parse_blocks(read_log(lp))
        ser = p_initres_series(blocks)
        dec = decile_samples(ser)
        sp = decile_spread(dec)
        chk("plateau: >= %d decile samples" % DECILE_MIN_SAMPLES,
            len(dec) >= DECILE_MIN_SAMPLES, "%d samples" % len(dec))
        chk("plateau: spread < 1e-06 => NEW PLATEAU", is_new_plateau(sp),
            "spread=%.3e" % sp)
        chk("plateau: G1 False", not eval_g1(ser[-1][1]),
            "p=%.6e" % ser[-1][1])
        chk("plateau: G2 False", not eval_g2(dec)[0])

        # (4) breaking log -> BREAK
        brk = [2.0568149526e-04 * (0.90 ** i) for i in range(n)]
        lb = _mk_log(os.path.join(tmp, "break.log"), brk, iters)
        sb = p_initres_series(parse_blocks(read_log(lb))[0])
        db = decile_samples(sb)
        g2b, spb, monob = eval_g2(db)
        chk("break: G1 True", eval_g1(sb[-1][1]), "p=%.6e" % sb[-1][1])
        chk("break: G2 True (monotone, spread >= 1e-3)", g2b,
            "spread=%.3e monotone=%s" % (spb, monob))
        chk("break: BREAK = G1 AND G2", eval_g1(sb[-1][1]) and g2b)
        chk("break: not a NEW PLATEAU", not is_new_plateau(spb))

        # (5) indeterminate drift: spread between 1e-6 and 1e-3
        drift = [2.0568149526e-04 * (1 - 2e-6 * i) for i in range(n)]
        ld = _mk_log(os.path.join(tmp, "drift.log"), drift, iters)
        sd = decile_samples(p_initres_series(parse_blocks(read_log(ld))[0]))
        spd = decile_spread(sd)
        chk("drift: neither BREAK nor NEW PLATEAU",
            (SPREAD_PLATEAU_MAX <= spd < SPREAD_BREAK_MIN), "spread=%.3e" % spd)

        # (6) too few decile samples -> the grader must REFUSE, not weaken
        few = _mk_log(os.path.join(tmp, "few.log"), brk[:20],
                      list(range(100, 2001, 100)))
        sfew = decile_samples(p_initres_series(parse_blocks(read_log(few))[0]))
        chk("few samples: decile is under the asserted minimum",
            len(sfew) < DECILE_MIN_SAMPLES,
            "%d samples -> grade_arm() refuses (exit 2)" % len(sfew))

        # (7) CONTROL A on a plateau log: must pass and G1 must flip
        okA, dA = control_plant_residual(read_log(lp))
        chk("control A: residual plant read back, G1 flips", okA, dA)

        # (8) CONTROL A must FAIL with a deliberately broken reader
        broken = lambda ls: [(END_TIME, 2.0568149526e-04)]
        okA2, dA2 = control_plant_residual(read_log(lp), reader=broken)
        chk("control A DETECTS a blind reader (can fail)", not okA2, dA2)

        # (9) CONTROL B: Bounding 0 -> 1
        okB, dB = control_plant_bounding(read_log(lp))
        chk("control B: Bounding count flips 0 -> 1", okB, dB)

        # (10) CONTROL B must FAIL with a counter stuck at zero
        stuck = lambda ls: 0
        okB2, dB2 = control_plant_bounding(read_log(lp), counter=stuck)
        chk("control B DETECTS a stuck counter (can fail)", not okB2, dB2)

        # (11) CONTROL C: absent sentinel
        okC, dC = control_absent_sentinel(read_log(lp))
        chk("control C: absent sentinel reads 0, its plant reads 1", okC, dC)

        # (12) Bounding present -> N-D45: NOT A RESULT even though it broke
        lbb = _mk_log(os.path.join(tmp, "break_bounded.log"), brk, iters, bounding=3)
        _, mbb = parse_blocks(read_log(lbb))
        chk("N-D45: a BREAKING arm with Bounding lines is caught",
            mbb["bounding_count"] == 3 and mbb["bounding_count"] > F1_BOUNDING_MAX,
            "count=%d beside p=%.6e" % (mbb["bounding_count"], brk[-1]))

        # (13) rule-4: missing End
        lne = _mk_log(os.path.join(tmp, "noend.log"), brk, iters, end=False)
        bne, mne = parse_blocks(read_log(lne))
        okc, fc = check_completion(bne, mne, 0, END_TIME)
        chk("rule 4: missing `End` fails completion", not okc, "; ".join(fc))

        # (14) rule-4: last time != endTime
        short = _mk_log(os.path.join(tmp, "short.log"), brk[:40],
                        list(range(100, 4001, 100)))
        bs, ms = parse_blocks(read_log(short))
        okc2, fc2 = check_completion(bs, ms, 0, END_TIME)
        chk("rule 4: last time != endTime fails completion", not okc2,
            "; ".join(fc2))

        # (15) rule-4: rc != 0
        okc3, fc3 = check_completion(*parse_blocks(read_log(lb)), rc=1,
                                     end_time=END_TIME)
        chk("rule 4: rc != 0 fails completion", not okc3, "; ".join(fc3))

        # (16) N-D44: primalMaxRes is nuTilda and uses the U MEDIAN
        bpm, _ = parse_blocks(read_log(lp))
        pmr, eq = primal_max_res(bpm[-1])
        chk("N-D44: primalMaxRes picks nuTilda (max over equations)",
            eq == "nuTilda", "%.6e on %s" % (pmr, eq))
        fake = {"res": {"U0": 1.0, "U1": 5.0, "U2": 9.0, "p": 2.0}}
        pmr2, eq2 = primal_max_res(fake)
        chk("N-D44: U enters by MEDIAN (5.0), not max (9.0)",
            abs(pmr2 - 5.0) < 1e-12 and eq2 == "U(median)",
            "%.3f on %s" % (pmr2, eq2))

        # (17) field readers
        cd = _mk_fields(os.path.join(tmp, "case"), END_TIME)
        lo, hi, nf = field_minmax(cd, END_TIME, "nuTilda")
        chk("field reader: nuTilda min/max from disk", nf == 1 and lo > 0,
            "min=%.3e max=%.3e files=%d" % (lo, hi, nf))
        um, nu = vector_mag_max(cd, END_TIME, "U")
        chk("field reader: |U| max from disk",
            nu == 1 and abs(um - 8.4) < 1e-9, "|U|max=%.4f" % um)
        tl, th, nt = field_minmax(cd, END_TIME, "T")
        chk("field reader: T min/max from disk",
            nt == 1 and F3D_T_LO <= tl and th <= F3D_T_HI,
            "T=[%.1f, %.1f]" % (tl, th))
        _, _, nmiss = field_minmax(cd, 9999, "nuTilda")
        chk("field reader: a MISSING field reads 0 files, not a pass",
            nmiss == 0, "files=%d" % nmiss)

        # (18) F3 thresholds bite
        cdb = _mk_fields(os.path.join(tmp, "case_bad"), END_TIME,
                         nutilda=(-1.0, 2e-3), umag=900.0, T=(300.0, 900.0))
        lob, _, _ = field_minmax(cdb, END_TIME, "nuTilda")
        umb, _ = vector_mag_max(cdb, END_TIME, "U")
        _, thb, _ = field_minmax(cdb, END_TIME, "T")
        chk("F3b bites: negative nuTilda detected", lob < F3B_NUTILDA_MIN,
            "min=%.3f" % lob)
        chk("F3c bites: |U| over 10 x U0 detected", umb > F3C_UMAG_MAX,
            "|U|max=%.1f > %.1f" % (umb, F3C_UMAG_MAX))
        chk("F3d bites: T outside [250,400] detected", thb > F3D_T_HI,
            "Tmax=%.1f" % thb)

        # (19) F2 -- the A4 failure mode, reproduced and caught
        okf2, eqf2, vf2 = eval_f2_norm2(parse_blocks(read_log(lb))[1]["norm2"])
        chk("F2: healthy Residual Norm2 passes the ceiling", okf2 is True,
            "worst %.4g on %s <= %.1e" % (vf2, eqf2, F2_NORM2_MAX))
        la4 = _mk_log(os.path.join(tmp, "a4like.log"), brk, iters,
                      norm2_p=1.1347097e+35)
        okf2b, eqf2b, vf2b = eval_f2_norm2(parse_blocks(read_log(la4))[1]["norm2"])
        sa4 = p_initres_series(parse_blocks(read_log(la4))[0])
        chk("F2 CATCHES the A4 mode: tiny residual, huge Norm2",
            okf2b is False and eval_g1(sa4[-1][1]),
            "p initRes=%.3e PASSES G1 while %s Norm2=%.3e -- N-D45 exactly"
            % (sa4[-1][1], eqf2b, vf2b))
        okf2c, _, _ = eval_f2_norm2({})
        chk("F2: an ABSENT reading is neither pass nor fail", okf2c is None,
            "returns None -> the grader records a failure, not a pass")

        # (20) empty log is a refusal condition, not a zero
        empty = os.path.join(tmp, "empty.log")
        open(empty, "w").close()
        chk("empty log is size 0 (read_log refuses on it)",
            os.path.getsize(empty) == 0, "read_log() would exit 2")

        # (21) the vocabulary is closed
        chk("verdict vocabulary is exactly the six fixed labels",
            set(VOCAB) == {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT",
                           "BLOCKED", "PENDING"}, ", ".join(VOCAB))

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("-" * 74)
    print("SELFTEST TALLY: %d passed, %d failed" % (tally["pass"], tally["fail"]))
    print("-" * 74)
    return 0 if tally["fail"] == 0 else 1


def main():
    ap = argparse.ArgumentParser(description="A5P plateau-ladder grader")
    ap.add_argument("--selftest", action="store_true",
                    help="run the fixture suite and exit nonzero on any failure")
    ap.add_argument("--arm", help="arm name, e.g. P0 P1 P2 P3 P4")
    ap.add_argument("--log", help="path to the arm's solver log")
    ap.add_argument("--case-dir", default=None,
                    help="arm case dir holding processor*/<endTime>/ fields")
    ap.add_argument("--rc", type=int, default=None,
                    help="the solver's rc, READ FROM THE PROCESS, never inferred")
    ap.add_argument("--baseline", action="store_true",
                    help="this arm is P0: also check baseline reproduction")
    ap.add_argument("--end-time", type=int, default=END_TIME)
    ap.add_argument("--p0-nutilda-max", type=float, default=None,
                    help="P0's nuTilda field max, for the F3b cap")
    ap.add_argument("--md5", action="store_true", help="print own md5 and exit")
    a = ap.parse_args()

    if a.md5:
        print(md5_of(os.path.abspath(__file__)))
        return 0
    if a.selftest:
        return selftest()
    if not a.arm or not a.log:
        ap.print_usage()
        print("error: --arm and --log are required unless --selftest")
        return 3
    return grade_arm(a.arm, a.log, a.case_dir, a.rc, a.baseline,
                     a.end_time, a.p0_nutilda_max)


if __name__ == "__main__":
    sys.exit(main())
