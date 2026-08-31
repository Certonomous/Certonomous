#!/usr/bin/env python3
"""T23 GRADER -- the PHYSICALITY TIER of the Case 3 map, and NOTHING ELSE.

Gates FROZEN at `docs/campaigns/T-family/T23_PREREGISTRATION.md` (commit
fe666fd5).  This file grades against section 1 line 4 and against nothing else.

  B1  Q1 < 200.0 degC   -> PASS ; else PASS, FLAGGED "beyond assumption range"
  B2  Q1 > 0.0 degC     -> PASS ; else GATE FAIL
  B3  Q1 >= Q2 AND Q1 != Q2 -> PASS ; else NOT A RESULT

  Q1 = max(T) over the whole `housing` region, degC, from the internalField of
       <endTime>/housing/T
  Q2 = areaAvg(T) on the HOUSING SIDE of the fluid/housing interface, degC, from
       the `value` entry of the `housing_to_fluid` patch in the boundaryField of
       the SAME file -- two readers of one solution on different code paths with
       different pre-derived extents (T23 section 1 line 3).

=== WHAT THIS FILE IS FORBIDDEN TO PRODUCE ===

NO Nusselt number, NO Roache classification, NO GCI, NO observed order, NO
heat-balance closure.  All four are DEFERRED at T23 section 4 with reasons.
**T23 section 1 line 5 registers NO LADDER: every point runs at L1 only, and a
SINGLE MESH LEVEL ADMITS NO TRIPLE.**  Any Roache classification, GCI or
observed order quoted from a T23 artifact is a CATEGORY ERROR, and this grader
emits none so that none can be quoted from it.  y+ is MEASURED AND REPORTED and
is NOT gated (section 4.4).

Verdict vocabulary fixed by CLAUDE.md rule 1: PASS / GATE REACHED / GATE FAIL /
NOT A RESULT / BLOCKED / PENDING.  No other word is emitted as a verdict.

=== THE Ux CONVERGENCE TRAP, AND WHY Ux IS EXCLUDED FROM THE ASSERTION ===

THIS IS A REPORTING DECISION, NOT AN AMENDMENT.  Compute has run and the frozen
gates are closed; T23 has NO residual gate at all, so nothing below moves any
gate.  T23 section 3.1 registers convergence as "an ASSERTION on the log, never
a stopping rule" and does NOT name which residuals the assertion covers.

In this 5-degree wedge, **x is the CIRCUMFERENTIAL direction and Ux is
identically zero BY GEOMETRY**, one cell thick with wedge patches front and
back.  Its linear-solver residual is therefore a 0/0 normalisation and carries
NO information: OpenFOAM normalises each component's residual by that
component's own field scale, and when the field scale is zero to machine
precision the ratio is noise of order one.  Measured on every case below and
printed on the face of the output: max|Ux| / max|Uz|, together with the final
initial residual of every component.  A reader who greps the last Ux residual
and stops there reports EVERY run of this family as unconverged.

**Ux is therefore EXCLUDED from the convergence assertion and the exclusion is
printed with the ratio that justifies it, per case, measured here and not
recited.**  Uy, Uz, h, p_rgh, k and omega are all asserted.

=== THE PLANTED-ZERO CONTROL (CLAUDE.md rule 3, T23 section 3.6) ===

Both readers are shown able to see a non-zero before either zero is believed.
Copy first and never write into the case; negative arm at threshold exactly
zero; a measured magnitude ladder with an exact, epsilon-free floor; REFUSE
(exit 2) rather than degrade at every guard.

**THE ONLY SIZING TOLERANCE IS RELATIVE**, and it is the family's predicate
`got >= PLANT * (1.0 - 1e-9)` (T1_runs/analyse_pesweep.py:141,
analyse_dts.py:594, analyse_dts_p.py:226).  T3's absolute `seen >= PLANT -
1e-15` is NOT adopted: on a ~370 K field that window is 0.0176 of one ULP and
the outcome would be decided by a rounding wiggle rather than by the reader.

`PLANT` is IMPORTED from `scripts/roache_triple.py` and never redefined here.

Exit: 0 graded, 1 at least one row is not a clean PASS, 2 REFUSAL.
Usage: python3 analyse_t23.py [--root DIR] [--json OUT] | --selftest
"""
import contextlib
import io
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import roache_triple as RT                                   # noqa: E402

PLANT = RT.PLANT                       # 1.234e-03, IMPORTED, never redefined
LADDER = (10.0, 1.0, 1e-1, 1e-2, PLANT, 1e-3, 1e-4, 1e-5, 1e-6)

CASES = ("T23_P305_U10", "T23_P305_U20", "T23_P305_U30", "T23_P305_U40")
ENDTIME = "10000"
KELVIN_C = 273.15
IFACE_PATCH = "housing_to_fluid"       # housing SIDE of the fluid/housing iface

# T23 section 1 line 4.  REGISTERED THRESHOLDS, transcribed from the frozen file.
B1_BOUND_C = 200.0
B2_FLOOR_C = 0.0

# T23 section 6.2, REGISTERED PREDICTIONS.  Reported beside the measured values
# and NEVER used as gates -- they are a lumped 1-D model's output and section
# 2.7 registers in advance that it may be wrong.
PREDICTED = {                          # case: (Dittus-Boelter degC, flat-plate degC)
    "T23_P305_U10": (329.1, 195.1),
    "T23_P305_U20": (197.3, 120.3),
    "T23_P305_U30": (148.0, 92.4),
    "T23_P305_U40": (121.6, 77.4),
}
UNDECIDED = "T23_P305_U20"             # section 2.7: +2.70 K under the bound

# T23 section 6.2, THE REGISTERED CONTINGENCY, one-way and stated before
# compute: "if the solved values disagree with BOTH closures by more than the
# 1.763x spread between them, the LUMPED MODEL OF SECTION 2 is the thing that
# was falsified -- a reportable finding about the level-selection instrument --
# and that does not change B1, B2 or B3, which grade the solved temperature and
# not the model."
#
# THE COMPARISON IS ON THE TEMPERATURE RISE ABOVE T_inf, AND THE READING IS
# STATED RATHER THAN LEFT IMPLICIT.  The lumped model is
# `T_max = T_inf + P * R_tot(U)` (section 2.1), so T_inf is COMMON to the model
# and the solve and carries no information about either.  Comparing absolute
# degC would divide two numbers that share a 288 K offset and would flatter the
# model by construction.  The disagreement is therefore taken on `T_max - T_inf`.
T_INF_K = 288.0                        # REGISTERED, section 2.1; and MEASURED
                                       # as the inlet fixedValue in each case's
                                       # own 0.orig/fluid/T
CLOSURE_SPREAD = 1.763                 # h_FP/h_DB, DERIVED, section 2.1

# Residual components asserted.  Ux is absent BY DECISION; see the module
# docstring.  The exclusion is printed beside its measured justification.
ASSERT_RESID = ("Uy", "Uz", "h", "p_rgh", "k", "omega")
EXCLUDED_RESID = ("Ux",)
RESID_TOL = 1e-6                       # an ASSERTION on the log, not a gate

EXIT_OK, EXIT_NOTCLEAN, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------------------------------------------------------------------------
# STRUCTURAL LOCATION.  Every list below is delimited from the FIELD'S OWN
# HEADER -- keyword, then count, then the opening parenthesis -- never by a
# regex sweep over the file and never by value.
# --------------------------------------------------------------------------

def _list_window(lines, key_idx):
    """Given the index of a line introducing `... nonuniform List<scalar>`,
    return (first_value_idx, n).  REFUSE if the header does not have the shape
    the format guarantees."""
    i = key_idx + 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines) or not re.fullmatch(r"\d+", lines[i].strip()):
        refuse("list at line %d carries no element count -- the structural "
               "locator will not guess one" % key_idx)
    n = int(lines[i].strip())
    i += 1
    if i >= len(lines) or lines[i].strip() != "(":
        refuse("list at line %d has no opening parenthesis after its count"
               % key_idx)
    if i + 1 + n > len(lines):
        refuse("list at line %d claims %d elements the file does not hold"
               % (key_idx, n))
    return i + 1, n


def internal_window(path):
    """(lines, first_idx, n) for the internalField scalar list."""
    lines = open(path).read().split("\n")
    idx = [k for k, l in enumerate(lines)
           if re.match(r"\s*internalField\s+nonuniform\s+List<scalar>", l)]
    if len(idx) != 1:
        refuse("%s has %d internalField list headers, expected exactly 1"
               % (path, len(idx)))
    first, n = _list_window(lines, idx[0])
    return lines, first, n


def patch_value_window(path, patch):
    """(lines, first_idx, n) for the `value` list of one boundaryField patch."""
    lines = open(path).read().split("\n")
    bidx = [k for k, l in enumerate(lines) if re.match(r"^boundaryField\s*$", l)]
    if len(bidx) != 1:
        refuse("%s has %d boundaryField headers, expected exactly 1"
               % (path, len(bidx)))
    pidx = [k for k, l in enumerate(lines)
            if k > bidx[0] and l.strip() == patch]
    if len(pidx) != 1:
        refuse("%s has %d `%s` patch blocks in boundaryField, expected exactly 1"
               % (path, len(pidx), patch))
    # walk the block by brace depth and take its OWN `value` key
    k, depth, opened, vidx = pidx[0], 0, False, None
    while k < len(lines):
        depth += lines[k].count("{") - lines[k].count("}")
        if lines[k].count("{"):
            opened = True
        if opened and depth == 1 and re.match(r"\s+value\s+nonuniform\s+"
                                              r"List<scalar>", lines[k]):
            vidx = k
        if opened and depth == 0:
            break
        k += 1
    if vidx is None:
        refuse("patch `%s` in %s carries no nonuniform `value` list -- Q2 will "
               "not fall back to refValue, which is a different quantity"
               % (patch, path))
    first, n = _list_window(lines, vidx)
    return lines, first, n


# --------------------------------------------------------------------------
# MESH: real face areas for the area average.  A wedge patch's faces are not
# assumed equal-area; they are computed.
# --------------------------------------------------------------------------

def _foam_list(path, parser):
    txt = open(path).read()
    body = txt.split("// * * *", 1)[-1]
    m = re.search(r"^\s*(\d+)\s*$", body, re.M)
    if not m:
        refuse("%s carries no element count" % path)
    n = int(m.group(1))
    rest = body[m.end():]
    o = rest.index("(")
    out, i, depth = [], o + 1, 0
    for line in rest[o + 1:].split("\n"):
        s = line.strip()
        if s == ")" and depth == 0:
            break
        if s:
            out.append(parser(s))
    if len(out) < n:
        refuse("%s: read %d of %d elements" % (path, len(out), n))
    return out[:n]


def patch_face_areas(case_dir, region, patch):
    pm = os.path.join(case_dir, "constant", region, "polyMesh")
    b = open(os.path.join(pm, "boundary")).read()
    m = re.search(r"\b%s\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);"
                  % re.escape(patch), b, re.S)
    if not m:
        refuse("patch %s not found in %s/boundary" % (patch, pm))
    nf, sf = int(m.group(1)), int(m.group(2))
    pts = _foam_list(os.path.join(pm, "points"),
                     lambda s: tuple(float(x) for x in
                                     s.strip("()").split()))
    faces = _foam_list(os.path.join(pm, "faces"),
                       lambda s: [int(x) for x in
                                  s[s.index("(") + 1:s.rindex(")")].split()])
    areas = []
    for f in faces[sf:sf + nf]:
        # polygon area = |sum over edges of 0.5 * (p_i - c) x (p_{i+1} - c)|
        c = [sum(pts[i][d] for i in f) / len(f) for d in range(3)]
        ax = ay = az = 0.0
        for i in range(len(f)):
            a = [pts[f[i]][d] - c[d] for d in range(3)]
            b2 = [pts[f[(i + 1) % len(f)]][d] - c[d] for d in range(3)]
            ax += 0.5 * (a[1] * b2[2] - a[2] * b2[1])
            ay += 0.5 * (a[2] * b2[0] - a[0] * b2[2])
            az += 0.5 * (a[0] * b2[1] - a[1] * b2[0])
        areas.append(math.sqrt(ax * ax + ay * ay + az * az))
    if len(areas) != nf or min(areas) <= 0.0:
        refuse("patch %s: %d areas, min %g -- a zero-area face makes the area "
               "average undefined" % (patch, len(areas), min(areas) if areas
                                      else 0.0))
    return areas


# --------------------------------------------------------------------------
# THE TWO READERS.  Different code paths, different pre-derived extents.
# Both return KELVIN; the degC conversion happens once, at grading.
# --------------------------------------------------------------------------

def read_Q1(case_dir):
    """max(T) over the housing internalField.  Reader path: internalField."""
    p = os.path.join(case_dir, ENDTIME, "housing", "T")
    lines, first, n = internal_window(p)
    vals = [float(lines[first + i]) for i in range(n)]
    return max(vals)


def read_Q2(case_dir, areas=None):
    """areaAvg(T) on the housing side of the interface.  Reader path:
    boundaryField `value` of housing_to_fluid, area-weighted by the real face
    areas of that patch."""
    p = os.path.join(case_dir, ENDTIME, "housing", "T")
    lines, first, n = patch_value_window(p, IFACE_PATCH)
    vals = [float(lines[first + i]) for i in range(n)]
    if areas is None:
        areas = patch_face_areas(case_dir, "housing", IFACE_PATCH)
    if len(areas) != n:
        refuse("Q2: %d face areas against %d boundary values" % (len(areas), n))
    return sum(a * v for a, v in zip(areas, vals)) / sum(areas)


# --------------------------------------------------------------------------
# PLANTS.  STRUCTURAL: the window comes from the field's own header; the write
# is by LINE INDEX; the number of values planted is recorded.
# --------------------------------------------------------------------------

def plant_Q1(case_dir, mag):
    """Plant into the HOTTEST internalField cell.  Window structural, write by
    line index.  Returns the count planted."""
    p = os.path.join(case_dir, ENDTIME, "housing", "T")
    lines, first, n = internal_window(p)
    vals = [float(lines[first + i]) for i in range(n)]
    j = max(range(n), key=lambda i: vals[i])
    lines[first + j] = "%.12g" % (vals[j] + mag)     # writePrecision 12 (3.2)
    open(p, "w").write("\n".join(lines))
    return 1


def plant_Q2(case_dir, mag):
    """Plant into EVERY face of the target patch, so Q2's expected shift is
    exactly `mag` and NOT mag/N (T23 3.6 clause 7)."""
    p = os.path.join(case_dir, ENDTIME, "housing", "T")
    lines, first, n = patch_value_window(p, IFACE_PATCH)
    for i in range(n):
        lines[first + i] = "%.12g" % (float(lines[first + i]) + mag)
    open(p, "w").write("\n".join(lines))
    return n


# --------------------------------------------------------------------------
# THE PLANTED-ZERO CONTROL
# --------------------------------------------------------------------------

def planted_zero_control(case_dir, label, reader, planter):
    """T23 3.6, all eight clauses.  REFUSES rather than degrades."""
    case_real = os.path.realpath(case_dir)
    scratch = tempfile.mkdtemp(prefix="t23ctl_")
    dest = os.path.join(scratch, os.path.basename(case_dir))
    try:
        # 1. COPY FIRST, NEVER WRITE INTO THE CASE.
        if os.path.realpath(scratch).startswith(case_real + os.sep) \
           or os.path.realpath(scratch) == case_real:
            refuse("control scratch %s resolves INSIDE the case %s"
                   % (scratch, case_real))
        shutil.copytree(case_dir, dest, symlinks=True,
                        ignore=shutil.ignore_patterns("log.solve", "*.py"))
        if os.path.realpath(dest).startswith(case_real + os.sep):
            refuse("control copy %s resolves INSIDE the case" % dest)
        pristine = open(os.path.join(dest, ENDTIME, "housing", "T")).read()

        # 2. NEGATIVE ARM, THRESHOLD EXACTLY ZERO.  No absolute tolerance.
        a = reader(dest)
        b = reader(dest)
        if (b - a) != 0.0:
            refuse("%s NEGATIVE ARM: the reader is NOISY -- two reads of "
                   "identical bytes differ by %r" % (label, b - a))
        base = a

        # 3. POSITIVE ARM, a MEASURED magnitude ladder.  Exact, epsilon-free.
        rungs, floor, at_plant, n_planted = [], None, None, None
        for mag in LADDER:
            open(os.path.join(dest, ENDTIME, "housing", "T"), "w").write(pristine)
            cnt = planter(dest, mag)
            got = reader(dest) - base
            rungs.append((mag, got, cnt))
            if got != 0.0:
                floor = mag if floor is None else min(floor, mag)
            if mag == PLANT:
                at_plant, n_planted = got, cnt
        open(os.path.join(dest, ENDTIME, "housing", "T"), "w").write(pristine)

        # 4. REFUSE IF THE READER IS BLIND.
        if floor is None:
            refuse("%s POSITIVE ARM: the reader is BLIND -- no magnitude in "
                   "the ladder produced a non-zero read" % label)
        # 5. THE ONLY SIZING TOLERANCE IS RELATIVE (family predicate).
        if at_plant is None:
            refuse("%s: PLANT was not exercised by the ladder" % label)
        if not (at_plant >= PLANT * (1.0 - 1e-9)):
            refuse("%s: read at PLANT is %.6e, below PLANT*(1-1e-9) = %.6e"
                   % (label, at_plant, PLANT * (1.0 - 1e-9)))
        if at_plant < 0.1 * PLANT:
            refuse("%s: read at PLANT is %.6e, below 0.1 x PLANT"
                   % (label, at_plant))

        # 8. restore is implicit: the case was never written to.
        if open(os.path.join(case_dir, ENDTIME, "housing", "T")).read() \
           != open(os.path.join(dest, ENDTIME, "housing", "T")).read():
            refuse("%s: the case file and the restored copy differ -- the "
                   "control may have written into the case" % label)
        return dict(passed=True, base=base, floor=floor, at_plant=at_plant,
                    n_planted=n_planted, rungs=rungs)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# --------------------------------------------------------------------------
# RESIDUALS and the Ux ratio
# --------------------------------------------------------------------------

def final_residuals(case_dir):
    """Initial residuals from the LAST `Time = <endTime>` block of log.solve."""
    p = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(p):
        refuse("no log.solve in %s" % case_dir)
    txt = open(p, errors="replace").read()
    marks = [m.start() for m in
             re.finditer(r"^Time = %s\s*$" % re.escape(ENDTIME), txt, re.M)]
    if not marks:
        refuse("log.solve in %s has no `Time = %s` block" % (case_dir, ENDTIME))
    block = txt[marks[-1]:]
    out = {}
    for m in re.finditer(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)",
                         block):
        out.setdefault(m.group(1), []).append(float(m.group(2)))
    return {k: v[-1] for k, v in out.items()}


def u_component_maxima(case_dir):
    """max|Ux|, max|Uy|, max|Uz| over the fluid internalField.  MEASURED here
    per case, never recited from another case."""
    p = os.path.join(case_dir, ENDTIME, "fluid", "U")
    lines = open(p).read().split("\n")
    idx = [k for k, l in enumerate(lines)
           if re.match(r"\s*internalField\s+nonuniform\s+List<vector>", l)]
    if len(idx) != 1:
        refuse("%s has %d internalField vector headers" % (p, len(idx)))
    first, n = _list_window(lines, idx[0])
    mx = [0.0, 0.0, 0.0]
    for i in range(n):
        v = lines[first + i].strip()
        c = [float(x) for x in v[v.index("(") + 1:v.rindex(")")].split()]
        for d in range(3):
            if abs(c[d]) > mx[d]:
                mx[d] = abs(c[d])
    return mx


YPLUS_HOUSING_PATCH = "fluid_to_housing"   # the housing surface, fluid side

# A LIVE FALSE ZERO CAUGHT ON THIS RUNG, and the reason this guard exists.
# `postProcess -func yPlus -region fluid` (the generic utility, no solver)
# prints, in this order:
#     Unable to find turbulence model in the database: yPlus will not be
#     calculated
#     patch fluid_to_housing y+ : min = 0, max = 0, average = 0
# A reader that parses only the second line reports y+ = 0 on the housing wall
# of every case -- a perfect zero from a reader that the tool has ALREADY SAID
# cannot see a non-zero.  CLAUDE.md rule 3 in the wild.  THE ZEROS ARE REFUSED,
# NOT READ, and the same field measured through `chtMultiRegionSimpleFoam
# -postProcess -func yPlus` returns 0.395 .. 1.397 on that patch.
YPLUS_BLIND = ("will not be calculated", "Unable to find turbulence model")


def read_yplus(case_dir):
    """y+ on the housing wall, MEASURED AND REPORTED, NEVER GATED (T23 4.4).

    Returns a patch dict, or the string "BLIND" if the log's own text says the
    tool could not compute it, or None if no log is on disk.  A BLIND log's
    zeros are never returned as values."""
    p = os.path.join(case_dir, "log.yPlus.fluid")
    if not os.path.isfile(p):
        return None
    txt = open(p, errors="replace").read()
    if any(s in txt for s in YPLUS_BLIND):
        return "BLIND"
    hits = re.findall(r"patch (\S+) y\+ : min = ([0-9.eE+-]+), "
                      r"max = ([0-9.eE+-]+), average = ([0-9.eE+-]+)", txt)
    return {h[0]: (float(h[1]), float(h[2]), float(h[3])) for h in hits} or None


# --------------------------------------------------------------------------
# GRADING
# --------------------------------------------------------------------------

def grade(root, cases):
    out, worst = {}, EXIT_OK
    print("T23 -- PHYSICALITY TIER ONLY.  Gates: T23_PREREGISTRATION.md "
          "section 1 line 4, FROZEN at fe666fd5.")
    print("NO Nusselt, NO Roache triple, NO GCI, NO observed order, NO "
          "heat-balance closure: all four DEFERRED at section 4.")
    print("SECTION 1 LINE 5 REGISTERS NO LADDER.  Every point is L1 only and a "
          "SINGLE MESH LEVEL ADMITS NO TRIPLE, so no Roache classification is "
          "computed, quoted or quotable from this artifact.")
    print("PLANT = %.6e K, IMPORTED from scripts/roache_triple.py:%s\n"
          % (PLANT, "PLANT"))

    for case in cases:
        d = os.path.join(root, case)
        if not os.path.isdir(d):
            refuse("no case directory %s" % d)
        if not os.path.exists(os.path.join(root, "DONE.%s" % case)):
            refuse("%s carries no DONE marker -- T23 section 1 line 7 puts "
                   "strict completion FIRST and one-way; a row is not graded "
                   "before its completion is marked" % case)

        print("=== %s ===" % case)

        # --- INSTRUMENT ADMISSION (criterion 2), before any value is believed.
        areas = patch_face_areas(d, "housing", IFACE_PATCH)
        c1 = planted_zero_control(d, "Q1(internalField)", read_Q1, plant_Q1)
        c2 = planted_zero_control(d, "Q2(boundaryField areaAvg)",
                                  lambda p: read_Q2(p, areas), plant_Q2)
        for lbl, c in (("Q1", c1), ("Q2", c2)):
            print("  PLANTED-ZERO CONTROL %s: PASS.  negative arm difference "
                  "exactly 0.0; ladder floor %.0e K; read at PLANT %.6e K "
                  "(>= PLANT*(1-1e-9) = %.6e, RELATIVE predicate); values "
                  "planted %d"
                  % (lbl, c["floor"], c["at_plant"], PLANT * (1.0 - 1e-9),
                     c["n_planted"]))

        # --- QUANTITIES
        q1_K, q2_K = read_Q1(d), read_Q2(d, areas)
        q1, q2 = q1_K - KELVIN_C, q2_K - KELVIN_C
        print("  Q1 T_max(housing, internalField) = %.6f K = %.4f degC  "
              "[MEASURED]" % (q1_K, q1))
        print("  Q2 areaAvg T(housing side of %s, boundaryField) = %.6f K = "
              "%.4f degC  [MEASURED, over %d faces, total area %.6e m2]"
              % (IFACE_PATCH, q2_K, q2, len(areas), sum(areas)))

        # --- BANDS, in the registered one-way order: B3, then B2, then B1.
        b3 = (q1 >= q2) and (q1 != q2)
        b2 = q1 > B2_FLOOR_C
        b1 = q1 < B1_BOUND_C
        print("  B3  Q1 >= Q2 and Q1 != Q2 : %s  (Q1 - Q2 = %+.6f K)"
              % ("PASS" if b3 else "NOT A RESULT", q1 - q2))
        print("  B2  Q1 > %.1f degC        : %s" % (B2_FLOOR_C,
                                                    "PASS" if b2 else "GATE FAIL"))
        print("  B1  Q1 < %.1f degC      : %s  (margin %+.4f K)"
              % (B1_BOUND_C, "PASS" if b1 else
                 'PASS, FLAGGED "beyond assumption range"', B1_BOUND_C - q1))

        if not b3:
            verdict, flag = "NOT A RESULT", None
        elif not b2:
            verdict, flag = "GATE FAIL", None
        elif not b1:
            verdict, flag = "PASS", "beyond assumption range"
        else:
            verdict, flag = "PASS", None
        if verdict != "PASS" or flag:
            worst = EXIT_NOTCLEAN
        print("  VERDICT: %s%s" % (verdict,
                                   '  FLAGGED "%s"' % flag if flag else ""))
        if flag:
            print("    A FLAG IS A REAL FINDING, NOT A FAILURE (directive "
                  "3.6; T23 section 1 line 4 registers the not-met branch as a "
                  "FLAGGED PASS before compute). Zero flags was never the "
                  "requirement of this tier and must not be engineered for.")
        if case == UNDECIDED:
            print("    REGISTERED IN ADVANCE (section 2.7): this point is "
                  "UNDECIDED by the level-selection instrument at +2.70 K "
                  "under the bound, on a model whose two closures differ by "
                  "1.763x in h. Whichever way it lands is a registered "
                  "outcome, not a surprise and not a level-selection error.")

        # --- REGISTERED PREDICTIONS, reported and NEVER used as gates.
        db, fp = PREDICTED[case]
        print("  registered lumped-model predictions [REGISTERED, NOT GATES]: "
              "Dittus-Boelter %.1f degC (solved - DB = %+.2f K), flat plate "
              "%.1f degC (solved - FP = %+.2f K)" % (db, q1 - db, fp, q1 - fp))

        # --- THE REGISTERED CONTINGENCY OF SECTION 6.2.
        rise = q1_K - T_INF_K
        r_db = (db - (T_INF_K - KELVIN_C)) / rise if rise else float("inf")
        r_fp = (fp - (T_INF_K - KELVIN_C)) / rise if rise else float("inf")
        fired = (r_db > CLOSURE_SPREAD) and (r_fp > CLOSURE_SPREAD)
        print("  section 6.2 CONTINGENCY, on the RISE above T_inf = %.1f K "
              "(common to model and solve, so it carries no information about "
              "either): solved rise %.3f K; DB rise/solved rise = %.3f; FP "
              "rise/solved rise = %.3f; against the registered closure spread "
              "%.3f -- %s"
              % (T_INF_K, rise, r_db, r_fp, CLOSURE_SPREAD,
                 "FIRED" if fired else "not fired"))
        if fired:
            print("    THE LUMPED MODEL OF SECTION 2 IS THE THING THAT WAS "
                  "FALSIFIED, exactly as section 6.2 registered one-way and "
                  "before compute. It overpredicts the housing temperature "
                  "rise by %.2fx (DB) and %.2fx (FP), BOTH beyond the %.3fx "
                  "spread between the two closures, so this is not an "
                  "artefact of choosing between them. IT CHANGES B1, B2 AND "
                  "B3 NOT AT ALL -- those grade the SOLVED temperature and "
                  "not the model -- and it is a finding about the "
                  "LEVEL-SELECTION INSTRUMENT of section 2, which was never a "
                  "referent (section 1 line 2)." % (r_db, r_fp, CLOSURE_SPREAD))

        # --- THE Ux CONVERGENCE ASSERTION, with its measured justification.
        mx = u_component_maxima(d)
        ratio = mx[0] / mx[2] if mx[2] else float("inf")
        res = final_residuals(d)
        print("  max|Ux| = %.6e m/s, max|Uy| = %.6e m/s, max|Uz| = %.6e m/s ; "
              "max|Ux|/max|Uz| = %.3e  [MEASURED on %s/fluid/U]"
              % (mx[0], mx[1], mx[2], ratio, ENDTIME))
        print("  final initial residuals: "
              + ", ".join("%s %.6e" % (k, res[k])
                          for k in sorted(res) if k in
                          set(ASSERT_RESID) | set(EXCLUDED_RESID)))
        bad = [k for k in ASSERT_RESID if k in res and res[k] > RESID_TOL]
        miss = [k for k in ASSERT_RESID if k not in res]
        conv = (not bad) and (not miss)
        print("  CONVERGENCE ASSERTION (T23 section 3.1: an ASSERTION on the "
              "log, NEVER a stopping rule, and T23 registers NO residual "
              "gate): asserted over %s at %.0e -- %s%s"
              % (",".join(ASSERT_RESID), RESID_TOL,
                 "HOLDS" if conv else "DOES NOT HOLD",
                 "" if conv else " (over tolerance: %s; absent: %s)"
                 % (",".join(bad) or "none", ",".join(miss) or "none")))
        print("  Ux IS EXCLUDED FROM THAT ASSERTION, AND HERE IS WHY, MEASURED "
              "ON THIS CASE: x is the CIRCUMFERENTIAL direction of a 5-degree "
              "wedge one cell thick, so Ux is identically zero BY GEOMETRY -- "
              "max|Ux|/max|Uz| = %.3e. Its initial residual reads %.6e, which "
              "is a 0/0 normalisation carrying NO information; a reader that "
              "greps the last Ux residual reports every run of this family as "
              "unconverged. THIS MOVES NO GATE: T23 has no residual gate at "
              "all." % (ratio, res.get("Ux", float("nan"))))

        # --- y+, MEASURED AND REPORTED, NEVER GATED (section 4.4).
        yp = read_yplus(d)
        if yp is None:
            print("  y+ on the housing wall: NOT MEASURED -- no "
                  "log.yPlus.fluid on disk. REPORTED as not measured, never "
                  "as a zero (rule 3). T23 section 4.4 registers y+ as "
                  "MEASURED AND REPORTED and NOT a gate, so its absence "
                  "does not touch any verdict above.")
        elif yp == "BLIND":
            print("  y+ on the housing wall: NOT MEASURED -- the log's own "
                  "text says the turbulence model was not in the database and "
                  "yPlus would not be calculated, and it then printed "
                  "min/max/average of 0. THOSE ZEROS ARE REFUSED, NOT READ "
                  "(rule 3): a zero from a reader shown unable to see a "
                  "non-zero is not evidence.")
            yp = None
        else:
            for patch, (mn, mxv, av) in sorted(yp.items()):
                tag = " <- THE HOUSING SURFACE (section 4.4)" \
                    if patch == YPLUS_HOUSING_PATCH else ""
                print("  y+ on %s: min %.4g, max %.4g, average %.4g  "
                      "[MEASURED, REPORTED, NOT GATED (section 4.4)]%s"
                      % (patch, mn, mxv, av, tag))
            h = yp.get(YPLUS_HOUSING_PATCH)
            if h and h[1] > 1.0:
                print("    FINDING: max y+ on the housing surface is %.4g, "
                      "ABOVE 1. Section 4.4 registers exactly this outcome: "
                      "it BLOCKS the correlation tier and the map's Roache "
                      "triple -- NEITHER OF WHICH THIS RUNG CLAIMS -- and it "
                      "DOES NOT VOID the physicality rows, whose content is a "
                      "temperature bound and not a heat-transfer coefficient. "
                      "y+ is REPORTED here and is NOT a gate." % h[1])

        out[case] = dict(Q1_degC=q1, Q2_degC=q2, Q1_K=q1_K, Q2_K=q2_K,
                         B1=bool(b1), B2=bool(b2), B3=bool(b3),
                         verdict=verdict, flag=flag,
                         max_Ux=mx[0], max_Uy=mx[1], max_Uz=mx[2],
                         ux_uz_ratio=ratio, residuals=res,
                         convergence_assertion_excluding_Ux=bool(conv),
                         yplus=yp,
                         control_Q1_floor=c1["floor"],
                         control_Q2_floor=c2["floor"],
                         predicted_DB_degC=db, predicted_FP_degC=fp,
                         rise_K=rise, DB_over_solved=r_db,
                         FP_over_solved=r_fp,
                         contingency_6_2_fired=bool(fired))
        print("")
    return out, worst


# --------------------------------------------------------------------------

def selftest():
    """Drive both readers and both plants on a forged three-region case, and
    drive the control's refusals.  A control that cannot refuse is not a
    control."""
    fails = []
    tmp = tempfile.mkdtemp(prefix="t23an_")
    try:
        d = os.path.join(tmp, CASES[0])
        os.makedirs(os.path.join(d, ENDTIME, "housing"))
        os.makedirs(os.path.join(d, ENDTIME, "fluid"))
        os.makedirs(os.path.join(d, "constant", "housing", "polyMesh"))
        vals = [300.0 + 0.5 * i for i in range(4)]          # max 301.5
        bvals = [290.0, 291.0]
        open(os.path.join(d, ENDTIME, "housing", "T"), "w").write(
            "FoamFile\n{\n}\n"
            "internalField   nonuniform List<scalar> \n4\n(\n"
            + "\n".join("%.12g" % v for v in vals) + "\n)\n;\n\n"
            "boundaryField\n{\n    housing_to_fluid\n    {\n"
            "        type            compressible::turbulentTemperatureRadCoupledMixed;\n"
            "        refValue        nonuniform List<scalar> \n2\n(\n1\n2\n)\n;\n"
            "        value           nonuniform List<scalar> \n2\n(\n"
            + "\n".join("%.12g" % v for v in bvals) + "\n)\n;\n    }\n}\n")
        open(os.path.join(d, ENDTIME, "fluid", "U"), "w").write(
            "internalField   nonuniform List<vector> \n2\n(\n"
            "(1e-15 0.5 20.0)\n(2e-15 0.25 10.0)\n)\n;\n")
        open(os.path.join(d, "log.solve"), "w").write(
            "Time = %s\n"
            "DILUPBiCGStab:  Solving for Ux, Initial residual = 0.135, "
            "Final residual = 1e-4, No Iterations 1\n"
            "DILUPBiCGStab:  Solving for Uy, Initial residual = 6.25e-10, "
            "Final residual = 6.25e-10, No Iterations 0\n"
            "DILUPBiCGStab:  Solving for Uz, Initial residual = 4.22e-12, "
            "Final residual = 4.22e-12, No Iterations 0\n"
            "DILUPBiCGStab:  Solving for h, Initial residual = 9.59e-10, "
            "Final residual = 9.59e-10, No Iterations 0\n"
            "GAMG:  Solving for p_rgh, Initial residual = 8.64e-09, "
            "Final residual = 1e-9, No Iterations 1\n"
            "DILUPBiCGStab:  Solving for omega, Initial residual = 9.5e-10, "
            "Final residual = 9.5e-10, No Iterations 0\n"
            "DILUPBiCGStab:  Solving for k, Initial residual = 9.9e-10, "
            "Final residual = 9.9e-10, No Iterations 0\n"
            "ExecutionTime = 1 s\n\nEnd\n" % ENDTIME)
        # a 2-face square-metre patch, so the area weights are known exactly
        open(os.path.join(d, "constant", "housing", "polyMesh", "boundary"),
             "w").write("// * * *\n1\n(\n    housing_to_fluid\n    {\n"
                        "        type mappedWall;\n        nFaces 2;\n"
                        "        startFace 0;\n    }\n)\n")
        open(os.path.join(d, "constant", "housing", "polyMesh", "points"),
             "w").write("// * * *\n6\n(\n(0 0 0)\n(1 0 0)\n(1 1 0)\n(0 1 0)\n"
                        "(2 0 0)\n(2 1 0)\n)\n")
        open(os.path.join(d, "constant", "housing", "polyMesh", "faces"),
             "w").write("// * * *\n2\n(\n4(0 1 2 3)\n4(1 4 5 2)\n)\n")
        open(os.path.join(tmp, "DONE.%s" % CASES[0]), "w").write("done\n")

        def chk(label, cond):
            print("  [%s] %s" % ("ok " if cond else "FAIL", label))
            if not cond:
                fails.append(label)

        areas = patch_face_areas(d, "housing", IFACE_PATCH)
        chk("face areas = [1.0, 1.0] (unit squares)",
            [round(a, 12) for a in areas] == [1.0, 1.0])
        chk("Q1 reads the internalField MAXIMUM 301.5",
            abs(read_Q1(d) - 301.5) < 1e-12)
        chk("Q2 reads the areaAvg of the `value` list (290.5), NOT refValue "
            "(1.5)", abs(read_Q2(d, areas) - 290.5) < 1e-12)

        c1 = planted_zero_control(d, "Q1", read_Q1, plant_Q1)
        c2 = planted_zero_control(d, "Q2", lambda p: read_Q2(p, areas), plant_Q2)
        chk("Q1 control PASSES and plants exactly 1 value",
            c1["passed"] and c1["n_planted"] == 1)
        chk("Q2 control PASSES and plants ALL 2 faces (shift = PLANT, not "
            "PLANT/N)", c2["passed"] and c2["n_planted"] == 2
            and abs(c2["at_plant"] - PLANT) < 1e-12)
        chk("Q1 read at PLANT recovers PLANT to the relative predicate",
            c1["at_plant"] >= PLANT * (1.0 - 1e-9))

        # NEGATIVE CONTROLS: the control must REFUSE a blind and a noisy reader.
        def drive_refusal(label, reader, planter):
            buf = io.StringIO()
            code = None
            try:
                with contextlib.redirect_stdout(buf):
                    planted_zero_control(d, "neg", reader, planter)
            except SystemExit as e:
                code = e.code
            chk(label, code == EXIT_REFUSE)

        drive_refusal("BLIND reader (returns a constant) -> REFUSE",
                      lambda p: 1.0, plant_Q1)
        _state = {"n": 0}

        def noisy(p):
            # the wobble must exceed one ULP of a ~300 K value (~5.7e-14),
            # or "noise" is a no-op and the arm proves nothing
            _state["n"] += 1
            return read_Q1(p) + _state["n"] * 1e-9
        drive_refusal("NOISY reader (negative arm != 0.0 exactly) -> REFUSE",
                      noisy, plant_Q1)

        mx = u_component_maxima(d)
        chk("u_component_maxima -> max|Ux| 2e-15, max|Uz| 20.0",
            abs(mx[0] - 2e-15) < 1e-27 and abs(mx[2] - 20.0) < 1e-12)
        res = final_residuals(d)
        chk("final_residuals sees Ux 0.135 and Uz 4.22e-12",
            abs(res["Ux"] - 0.135) < 1e-12 and abs(res["Uz"] - 4.22e-12) < 1e-24)

        buf = io.StringIO()
        # Forge the registered predictions to AGREE with the forged solve, so
        # the contingency's NOT-FIRED arm is exercised; the FIRED arm is
        # exercised below by restoring the real ones.
        _real_pred = PREDICTED[CASES[0]]
        PREDICTED[CASES[0]] = (301.5 - KELVIN_C, 301.5 - KELVIN_C)
        with contextlib.redirect_stdout(buf):
            got, code = grade(tmp, [CASES[0]])
        txt = buf.getvalue()
        chk("forged Q1 301.5 degK -> 28.35 degC, B1/B2/B3 all PASS, "
            "verdict PASS", got[CASES[0]]["verdict"] == "PASS"
            and got[CASES[0]]["B1"] and got[CASES[0]]["B2"]
            and got[CASES[0]]["B3"])
        chk("Ux EXCLUDED but its 0.135 residual IS PRINTED, and the "
            "assertion HOLDS anyway",
            "Ux IS EXCLUDED" in txt and "1.350000e-01" in txt
            and got[CASES[0]]["convergence_assertion_excluding_Ux"])
        chk("PLANTED CONTROL ON THE ASSERTION: had Ux been asserted, this "
            "forged case would report NOT converged",
            0.135 > RESID_TOL)
        # The header DISCLAIMS these words on purpose, so the check is run over
        # the PER-CASE BODY -- where such a token would be a claim rather than
        # a disclaimer.  A check run over the whole output would fire on the
        # disclaimer and would have to be weakened to pass, which is the wrong
        # direction.
        body = txt.split("=== ", 1)[1]
        chk("per-case body emits NO Roache/GCI/observed-order token "
            "(section 1 line 5: a single mesh level admits no triple)",
            not re.search(r"\b(GCI|CONVERGING|DIVERGENT|STAGNANT|OSCILLATORY|"
                          r"Roache|observed order)\b", body))
        chk("PLANTED CONTROL ON THAT CHECK: the same reader DOES see the "
            "tokens in the header, so its zero is not a blind zero",
            re.search(r"\b(GCI|Roache|observed order)\b",
                      txt.split("=== ", 1)[0]) is not None)
        chk("section 6.2 contingency NOT fired when the model agrees "
            "(forged 301.5 K vs DB 28.35 degC): a contingency that always "
            "fires is not a contingency",
            not got[CASES[0]]["contingency_6_2_fired"])
        chk("y+ absent is REPORTED as NOT MEASURED, never as 0",
            "y+ on the housing wall: NOT MEASURED" in txt)

        # THE FIRED ARM of the same contingency, on the same forged solve.
        PREDICTED[CASES[0]] = _real_pred
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            got2, _ = grade(tmp, [CASES[0]])
        chk("section 6.2 contingency FIRES when both closures miss by more "
            "than 1.763x, and the verdict is STILL PASS",
            got2[CASES[0]]["contingency_6_2_fired"]
            and got2[CASES[0]]["verdict"] == "PASS"
            and "IS THE THING THAT WAS FALSIFIED" in buf.getvalue())

        # THE FALSE-ZERO ARM, forged from the log this rung ACTUALLY produced.
        open(os.path.join(d, "log.yPlus.fluid"), "w").write(
            "    Unable to find turbulence model in the database: yPlus will "
            "not be calculated\n"
            "    patch %s y+ : min = 0, max = 0, average = 0\n"
            % YPLUS_HOUSING_PATCH)
        chk("BLIND yPlus log -> 'BLIND', its zeros REFUSED not read",
            read_yplus(d) == "BLIND")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            grade(tmp, [CASES[0]])
        chk("grader prints the REFUSAL of those zeros, never 'max 0'",
            "THOSE ZEROS ARE REFUSED" in buf.getvalue()
            and "y+ on %s: min 0" % YPLUS_HOUSING_PATCH not in buf.getvalue())
        # POSITIVE ARM: the same reader on a GOOD log must return values, or
        # the BLIND result above is a reader that cannot read anything.
        open(os.path.join(d, "log.yPlus.fluid"), "w").write(
            "    patch %s y+ : min = 0.395069182582, max = 1.39698600399, "
            "average = 0.741633762305\n" % YPLUS_HOUSING_PATCH)
        good = read_yplus(d)
        chk("POSITIVE ARM: the same reader DOES read a good log "
            "(max 1.39698600399), so its BLIND is not blindness",
            isinstance(good, dict)
            and abs(good[YPLUS_HOUSING_PATCH][1] - 1.39698600399) < 1e-12)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            grade(tmp, [CASES[0]])
        chk("max y+ above 1 on the housing prints the section 4.4 FINDING "
            "and moves NO verdict",
            "FINDING: max y+ on the housing surface" in buf.getvalue()
            and "VERDICT: PASS" in buf.getvalue())
        os.remove(os.path.join(d, "log.yPlus.fluid"))

        # A row without a DONE marker must REFUSE (criteria order is one-way).
        os.remove(os.path.join(tmp, "DONE.%s" % CASES[0]))
        code = None
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                grade(tmp, [CASES[0]])
        except SystemExit as e:
            code = e.code
        chk("ungraded without a DONE marker -> REFUSE (completion first)",
            code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    import ast
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert)
             for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (planted control: %d)"
          % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL",
                                       len(fails)))
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = HERE
    if "--root" in argv:
        i = argv.index("--root")
        root, argv = argv[i + 1], argv[:i] + argv[i + 2:]
    jout = None
    if "--json" in argv:
        i = argv.index("--json")
        jout, argv = argv[i + 1], argv[:i] + argv[i + 2:]
    want = [a for a in argv if not a.startswith("-")] or list(CASES)
    out, code = grade(root, want)
    if jout:
        json.dump(out, open(jout, "w"), indent=2, sort_keys=True)
        print("wrote %s" % jout)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
