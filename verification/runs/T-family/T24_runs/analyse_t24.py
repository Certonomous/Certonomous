#!/usr/bin/env python3
"""T24 -- the twelve points of the Case 3 motor-in-duct map, GRADED ON THE
PHYSICALITY TIER AND NOTHING ELSE.

THE FROZEN DOCUMENT IS `docs/campaigns/T-family/T24_PREREGISTRATION.md`, frozen
at commit `b9057489`.  Every threshold, band, label, tolerance and exclusion in
this file is TRANSCRIBED from that document with its section cited at the point
of use.  This comparator was authored WITHOUT READING ANY T24 CASE OUTPUT: no
`log.solve`, no time directory and no field file of any of the twelve cases was
opened, sampled or parsed while it was written.  A comparator whose author has
seen the answers is a gate fitted to its data, which is the exact failure
pre-registration exists to prevent.

WHAT THIS FILE DOES NOT COMPUTE, AND WILL NOT BE MADE TO COMPUTE
----------------------------------------------------------------
T24 section 0.3 (frozen lines 65-81): "T24 registers the PHYSICALITY TIER of
the map and NOTHING ELSE ... NO ROACHE TRIPLE, NO GCI, NO OBSERVED ORDER, NO
NUSSELT NUMBER, NO HEAT-BALANCE CLOSURE.  Every point runs at L1 only."  And:
"A SINGLE MESH LEVEL ADMITS NO TRIPLE.  Any Roache classification, GCI or
observed order quoted from a T24 artifact is a CATEGORY ERROR."

`CLAUDE.md` rule 5 is NOT weakened by that and is NOT waived here: it governs a
grid triple, and this rung produces none, so there is no row whose triple could
be non-CONVERGING.  This file therefore PRINTS that no ladder is registered
(the precedent is `T23_runs/analyse_t23.py:477`) and computes no triple, no GCI
and no observed order.  It also imports `roache_triple` for its `PLANT`
constant ONLY, and calls no classifier in it.

THE FOUR INSTRUMENT GUARDS THIS RUNG CARRIES
--------------------------------------------
1. THE PLANTED-ZERO CONTROL (`CLAUDE.md` rule 3; T24 section 3.6, frozen lines
   565-603).  Copy-first into scratch with a refusal if the destination
   realpath resolves inside the case; a NEGATIVE arm at bitwise 0.0 with NO
   absolute tolerance anywhere; a measured magnitude ladder with an exact,
   epsilon-free floor; REFUSE if the reader is BLIND.  THE ONLY SIZING
   TOLERANCE IS RELATIVE and the predicate is registered literally:
   `got >= PLANT * (1.0 - 1e-9)`.  Section 3.6 clause 5 EXPRESSLY REJECTS
   `analyse_t3.py:327`'s absolute `seen >= PLANT - 1e-15`, on the measured
   ground that on a ~300 K field that window is 0.0176 of one ULP -- narrower
   than the smallest representable step -- so the outcome would be decided by a
   rounding wiggle rather than by whether the reader saw the plant.  THE
   ABSOLUTE FORM IS NOT INHERITED HERE.

2. THE PER-CASE `Ux` EXCLUSION REFUSAL (T24 section 7.1, frozen lines
   995-1021).  In this 5-degree wedge `x` is the CIRCUMFERENTIAL direction, the
   mesh is one cell thick, and `Ux` is identically zero BY GEOMETRY, so its
   linear-solver residual is a 0/0 normalisation carrying no information.  The
   exclusion is justified PER CASE by THAT CASE'S OWN measured
   max|Ux|/max|Uz|, NEVER recited from T23, and A RATIO ABOVE 1e-12 REFUSES THE
   EXCLUSION FOR THAT CASE AND THE ROW REPORTS `Ux` ASSERTED.
   `T23_runs/analyse_t23.py:582-610` computes this ratio and prints it but
   carries NO threshold test and NO refusal branch; that guard is registered at
   T24 and is implemented here for the first time.  The excluded value is
   PRINTED, never suppressed.  THE EXCLUSION MOVES NO GATE, because section 3.1
   registers convergence as an ASSERTION on the log and T24 registers NO
   RESIDUAL GATE AT ALL.

3. THE MESH IDENTITY CHECK (T24 section 3.7, frozen lines 605-616).  Section 1
   line 1 registers that the mesh is identical across all twelve cases and
   identical to T23's, BY CONSTRUCTION.  A construction claim that is never
   checked is an assumption, so the twelve cases'
   `constant/{fluid,housing,core}/polyMesh/points` are hashed and asserted
   byte-identical to one another AND to `T23_P305_U10`'s.  A mismatch makes the
   AFFECTED ROWS `NOT A RESULT`.

4. THE y+ BLIND-LOG SENTINEL (T24 sections 4.4 and 7.2, frozen lines 698-712,
   1023-1028).  The generic `postProcess -func yPlus -region fluid` exits rc 0,
   prints that it cannot find the turbulence model, and then prints
   `y+ : min = 0, max = 0, average = 0` on every patch.  Those zeros are
   REFUSED, NOT READ.  y+ is MEASURED AND REPORTED and is NEVER A GATE.

WHAT IS DELEGATED
-----------------
Strict completion (`CLAUDE.md` rule 4; T24 sections 3.5 and 3.5a) belongs to
`mark_done_t24.py` and is CALLED here, never reimplemented.  A row is not
graded before its completion is marked, and a marker whose case no longer
passes the completion check is a stale marker and REFUSES.

`Ri` IS DECLARED VACUOUS AND IS NOT REPORTED AS A PASSING CHECK (section 3.4,
frozen lines 477-484).  With `g = (0 0 0)` registered at section 3.3, Ri is
identically zero by construction at every point of the map, so the directive's
`Ri < 0.1` criterion cannot fail and cannot inform.  Printing "Ri = 0 < 0.1,
PASS" would be evidence annotated as non-binding in its worst form.  What this
file prints instead is the honest statement.

Exit: 0 every row a clean unflagged PASS, 1 at least one row is not, 2 REFUSAL.
Usage: python3 analyse_t24.py [CASE ...] [--root DIR] [--json OUT] | --selftest
"""
import ast
import contextlib
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)
import roache_triple as RT                                      # noqa: E402
import mark_done_t24 as MD                                      # noqa: E402

# T24 section 3.6 clause 6: PLANT is IMPORTED, never redefined locally.
PLANT = RT.PLANT                        # 1.234e-03 K, scripts/roache_triple.py
# T24 section 3.6 clause 3: the registered magnitude ladder, in K, verbatim.
LADDER = (10.0, 1.0, 1e-1, 1e-2, PLANT, 1e-3, 1e-4, 1e-5, 1e-6)
# T24 section 3.6 clause 5: THE ONLY SIZING TOLERANCE, and it is RELATIVE.
PLANT_REL_SLACK = 1e-9

# T24 section 6.2, THE REGISTERED RUN SET.  Twelve, named, and closed.
POWERS_W = (80, 155, 230)
SPEEDS_MS = (10, 20, 30, 40)
CASES = tuple("T24_P%03d_U%d" % (p, u) for p in POWERS_W for u in SPEEDS_MS)

ENDTIME = "10000"                       # T24 section 3.1
KELVIN_C = 273.15
IFACE_PATCH = "housing_to_fluid"        # housing SIDE of the fluid/housing iface
YPLUS_HOUSING_PATCH = "fluid_to_housing"        # the same surface, fluid side

# T24 section 1 line 4, THE REGISTERED THRESHOLDS, transcribed from the frozen
# file.  B1's NOT-MET branch is a FLAGGED PASS and is NOT a GATE FAIL: frozen
# line 228, "B1's 'not met' branch is a FLAGGED PASS and NOT a GATE FAIL,
# registered here before compute exactly as T23 registered it, because
# directive 3.6 makes an over-bound point 'a real finding' and not a failure."
B1_BOUND_C = 200.0
B2_FLOOR_C = 0.0
B1_FLAG = "beyond assumption range"

# T24 section 2.4, THE REGISTERED PREDICTION INSTRUMENT.  The energy equation
# is linear in the source power and the flow field is decoupled from
# temperature, so at fixed U_inf the temperature RISE is exactly proportional
# to P_loss:
#     T_max(P, U) - T_inf = (P / 305) * [ T_max(305, U) - T_inf ]_MEASURED-AT-T23
# T_inf is REGISTERED at T23 section 2.1 and MEASURED as the inlet fixedValue
# in each case's own 0.orig/fluid/T.  The four bracketed rises are MEASURED at
# T23 and transcribed from the frozen T24 document, section 2.4.
T_INF_K = 288.0
P_REF_W = 305.0
T23_RISE_K = {10: 88.758, 20: 54.160, 30: 40.589, 40: 32.995}
# T24 section 2.4's REGISTERED CONTINGENCY: a departure above 2 % of the
# predicted rise falsifies THE LINEARITY ARGUMENT.  It is REPORTED and IS NOT A
# GATE -- "the affected row still carries whatever B1/B2/B3 say" (frozen line
# 421).
LINEARITY_TOL_FRAC = 0.02
# The frozen section 2.4 table, transcribed so that the arithmetic implemented
# here can be checked against the document rather than trusted.  degC.
PREDICTED_TMAX_C = {
    (80, 10): 38.131, (80, 20): 29.056, (80, 30): 25.496, (80, 40): 23.504,
    (155, 10): 59.957, (155, 20): 42.374, (155, 30): 35.477, (155, 40): 31.618,
    (230, 10): 81.782, (230, 20): 55.692, (230, 30): 45.458, (230, 40): 39.731,
}
# T23's four MEASURED rows, for the 16-point map of section 6.5.  Transcribed
# from the frozen T24 document section 1 line 4, which states the B1 margins
# +96.3922 / +130.9902 / +144.5611 / +152.1552 K against the 200.0 degC bound.
T23_TMAX_C = {(305, 10): 103.6078, (305, 20): 69.0098,
              (305, 30): 55.4389, (305, 40): 47.8448}

# T24 section 7.1.  The convergence ASSERTION set, and the excluded component.
ASSERT_RESID = ("Uy", "Uz", "h", "p_rgh", "k", "omega")
EXCLUDED_RESID = "Ux"
RESID_TOL = 1e-6                        # an ASSERTION on the log, never a gate
# T24 section 7.1: "a ratio above 1e-12 REFUSES the exclusion for that case and
# the row reports Ux asserted."  THIS IS THE GUARD T23 DOES NOT CARRY.
UX_UZ_RATIO_MAX = 1e-12

# T24 section 3.7.  The regions whose mesh identity is asserted, and the
# reference case the twelve are asserted against.
MESH_REGIONS = ("fluid", "housing", "core")
MESH_REF_CASE = "T23_P305_U10"
MESH_REF_ROOT = os.path.join(HERE, "..", "T23_runs")

# T24 section 4.4 / 7.2.  A log whose own text says the tool could not compute
# y+ is BLIND, and its zeros never reach a value slot.
YPLUS_BLIND = ("will not be calculated", "Unable to find turbulence model")
YPLUS_LOG = "log.yPlus.fluid"
# The REGISTERED measurement route (section 4.4, frozen lines 706-712).  It is
# printed for the operator; this file runs no solver and no OpenFOAM utility.
YPLUS_REGISTERED_CMD = ("chtMultiRegionSimpleFoam -postProcess -func yPlus "
                        "-region fluid -time 10000  (in a SCRATCH COPY)")

# T24 section 6, cost.  Serial, 1 rank (section 1 line 6), so core-minutes are
# wall seconds over 60.  The wall figure is taken from each case's OWN
# log.solve ExecutionTime line and NEVER from STATUS (section 3.5a).
RANKS = 1
PER_CASE_CAP_CORE_MIN = 45.0            # section 1 line 8, HARD
SUBSET_POINT_CORE_MIN = 360.4           # section 1 line 8
SUBSET_CAP_CORE_MIN = 540.0             # section 1 line 8, HARD

EXIT_OK, EXIT_NOTCLEAN, EXIT_REFUSE = 0, 1, 2

FREEZE_SHA = "b9057489"
FROZEN_DOC = "docs/campaigns/T-family/T24_PREREGISTRATION.md"


def refuse(msg):
    """T24 section 1 line 7 and section 3.5: the grading pass REFUSES (exit 2)
    rather than degrades.  There is no soft path out of this function."""
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def clear_pycache():
    """T24 section 3.6 clause 9.  A stale bytecode cache INVERTS a mutation
    control -- the clean arm fails and the mutated arm passes -- and
    PYTHONDONTWRITEBYTECODE does not fix it; the caches must be removed."""
    for d in (HERE, os.path.join(REPO, "scripts")):
        p = os.path.join(d, "__pycache__")
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)


def case_pu(case):
    """(P_loss W, U_inf m/s) from a registered case name.  REFUSES a name that
    is not one of section 6.2's twelve."""
    m = re.fullmatch(r"T24_P(\d{3})_U(\d+)", case)
    if not m or case not in CASES:
        refuse("%r is not a registered T24 case (section 6.2 names twelve): %s"
               % (case, " ".join(CASES)))
    return int(m.group(1)), int(m.group(2))


# --------------------------------------------------------------------------
# STRUCTURAL LOCATION.  Every list below is delimited from the FIELD'S OWN
# HEADER -- keyword, then count, then the opening parenthesis -- never by a
# regex sweep over the file and NEVER BY VALUE (T24 section 3.6 clause 7).
# --------------------------------------------------------------------------

def _list_window(lines, key_idx):
    """Given the index of a line introducing `... nonuniform List<...>`, return
    (first_value_idx, n).  REFUSE if the header does not have the shape the
    format guarantees -- a locator that guesses is not a locator."""
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
    """(lines, first_idx, n) for the `value` list of ONE boundaryField patch.

    T24 section 1 line 3 registers Q2 as read from the `value` entry, NEVER
    `refValue`.  Those are different quantities and this reader does not fall
    back from one to the other."""
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
               "NOT fall back to refValue, which is a different quantity "
               "(section 1 line 3)" % (patch, path))
    first, n = _list_window(lines, vidx)
    return lines, first, n


# --------------------------------------------------------------------------
# MESH.  Real face areas for the area average: a wedge patch's faces are NOT
# assumed equal-area (T24 section 1 line 3, "never assumed equal").
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
    out = []
    for line in rest[o + 1:].split("\n"):
        s = line.strip()
        if s == ")":
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
                     lambda s: tuple(float(x) for x in s.strip("()").split()))
    faces = _foam_list(os.path.join(pm, "faces"),
                       lambda s: [int(x) for x in
                                  s[s.index("(") + 1:s.rindex(")")].split()])
    areas = []
    for f in faces[sf:sf + nf]:
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
               "average undefined" % (patch, len(areas),
                                      min(areas) if areas else 0.0))
    return areas


# --------------------------------------------------------------------------
# T24 SECTION 3.7 -- THE MESH IDENTITY CHECK.
# Section 1 line 1 asserts the mesh is identical across all twelve cases and
# identical to T23's BY CONSTRUCTION.  An unchecked construction claim is an
# assumption, and section 2.4's prediction rests on it.
# --------------------------------------------------------------------------

def points_digest(case_dir, region):
    p = os.path.join(case_dir, "constant", region, "polyMesh", "points")
    if not os.path.isfile(p):
        refuse("no %s -- section 3.7's identity check cannot be evaluated and "
               "is NOT waived on absence" % p)
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mesh_identity(root, cases, ref_root=None, ref_case=MESH_REF_CASE):
    """-> (ok_by_case, digests_by_case, ref_digests).

    Every region's `points` of every case is asserted byte-identical to the
    reference case's.  A mismatch makes the AFFECTED ROWS `NOT A RESULT`
    (section 3.7) -- not because the mesh is bad, but because section 1 line
    1's registered claim would then be false."""
    ref_root = MESH_REF_ROOT if ref_root is None else ref_root
    ref_dir = os.path.join(ref_root, ref_case)
    if not os.path.isdir(ref_dir):
        refuse("no reference case %s -- section 3.7 registers identity "
               "against T23's mesh and that claim is not graded on trust"
               % ref_dir)
    ref = {r: points_digest(ref_dir, r) for r in MESH_REGIONS}
    digests, ok = {}, {}
    for case in cases:
        d = os.path.join(root, case)
        digests[case] = {r: points_digest(d, r) for r in MESH_REGIONS}
        ok[case] = all(digests[case][r] == ref[r] for r in MESH_REGIONS)
    return ok, digests, ref


# --------------------------------------------------------------------------
# THE TWO READERS (T24 section 1 line 3).  Different code paths, different
# pre-derived extents.  Both return KELVIN; degC conversion happens once.
# --------------------------------------------------------------------------

def read_Q1(case_dir):
    """Q1 = max(T) over the whole housing region.  Reader path: internalField."""
    p = os.path.join(case_dir, ENDTIME, "housing", "T")
    lines, first, n = internal_window(p)
    return max(float(lines[first + i]) for i in range(n))


def read_Q2(case_dir, areas=None):
    """Q2 = areaAvg(T) on the housing side of the fluid/housing interface.
    Reader path: boundaryField `value` of housing_to_fluid, area-weighted by
    the REAL face areas of that patch."""
    p = os.path.join(case_dir, ENDTIME, "housing", "T")
    lines, first, n = patch_value_window(p, IFACE_PATCH)
    vals = [float(lines[first + i]) for i in range(n)]
    if areas is None:
        areas = patch_face_areas(case_dir, "housing", IFACE_PATCH)
    if len(areas) != n:
        refuse("Q2: %d face areas against %d boundary values" % (len(areas), n))
    return sum(a * v for a, v in zip(areas, vals)) / sum(areas)


# --------------------------------------------------------------------------
# THE PLANTS (T24 section 3.6 clause 7).  The window comes from the field's OWN
# HEADER; the write is BY LINE INDEX; the count planted is recorded.  Nothing
# here locates anything by value.
# --------------------------------------------------------------------------

def plant_Q1(case_dir, mag):
    """Plant into the HOTTEST internalField cell.  Returns the count planted."""
    p = os.path.join(case_dir, ENDTIME, "housing", "T")
    lines, first, n = internal_window(p)
    vals = [float(lines[first + i]) for i in range(n)]
    j = max(range(n), key=lambda i: vals[i])
    lines[first + j] = "%.12g" % (vals[j] + mag)    # writePrecision 12 (3.2)
    open(p, "w").write("\n".join(lines))
    return 1


def plant_Q2(case_dir, mag):
    """Plant into EVERY face of the target patch, so Q2's expected shift is
    EXACTLY `mag` and NOT mag/N (section 3.6 clause 7)."""
    p = os.path.join(case_dir, ENDTIME, "housing", "T")
    lines, first, n = patch_value_window(p, IFACE_PATCH)
    for i in range(n):
        lines[first + i] = "%.12g" % (float(lines[first + i]) + mag)
    open(p, "w").write("\n".join(lines))
    return n


# --------------------------------------------------------------------------
# THE PLANTED-ZERO CONTROL -- CLAUDE.md rule 3, T24 section 3.6.
# A zero from a reader not shown able to see a non-zero is not evidence.
# A refusal here makes the WHOLE RUNG `NOT A RESULT`.
# --------------------------------------------------------------------------

def planted_zero_control(case_dir, label, reader, planter):
    """All nine clauses of section 3.6.  REFUSES rather than degrades."""
    clear_pycache()                                 # clause 9
    case_real = os.path.realpath(case_dir)
    scratch = tempfile.mkdtemp(prefix="t24ctl_")
    dest = os.path.join(scratch, os.path.basename(case_dir))
    fld = lambda d: os.path.join(d, ENDTIME, "housing", "T")    # noqa: E731
    try:
        # CLAUSE 1: COPY FIRST, NEVER WRITE INTO THE CASE.
        if os.path.realpath(scratch) == case_real \
           or os.path.realpath(scratch).startswith(case_real + os.sep):
            refuse("control scratch %s resolves INSIDE the case %s -- clause 1 "
                   "forbids writing into the case under any circumstance"
                   % (scratch, case_real))
        shutil.copytree(case_dir, dest, symlinks=True,
                        ignore=shutil.ignore_patterns("log.solve", "*.py"))
        if os.path.realpath(dest).startswith(case_real + os.sep):
            refuse("control copy %s resolves INSIDE the case" % dest)
        pristine = open(fld(dest)).read()

        # CLAUSE 2: NEGATIVE ARM, THRESHOLD EXACTLY ZERO.  Section 3.6: "the
        # difference must be bitwise 0.0 ... No absolute tolerance anywhere in
        # the negative arm."
        a = reader(dest)
        b = reader(dest)
        if (b - a) != 0.0:
            refuse("%s NEGATIVE ARM: the reader is NOISY -- two reads of "
                   "identical bytes differ by %r, and clause 2 registers the "
                   "threshold as bitwise 0.0 with no tolerance" % (label, b - a))
        base = a

        # CLAUSE 3: POSITIVE ARM, a MEASURED magnitude ladder, exact and
        # epsilon-free.  `floor` is the smallest magnitude with a strictly
        # non-zero read.
        rungs, floor, at_plant, n_planted = [], None, None, None
        for mag in LADDER:
            open(fld(dest), "w").write(pristine)
            cnt = planter(dest, mag)
            got = reader(dest) - base
            rungs.append((mag, got, cnt))
            if got != 0.0:
                floor = mag if floor is None else min(floor, mag)
            if mag == PLANT:
                at_plant, n_planted = got, cnt
        open(fld(dest), "w").write(pristine)

        # CLAUSE 4: REFUSE IF THE READER IS BLIND.
        if floor is None:
            refuse("%s POSITIVE ARM: the reader is BLIND -- no magnitude in "
                   "the registered ladder produced a non-zero read. An "
                   "instrument that cannot see a planted perturbation is not "
                   "entitled to certify a bound (section 3.6)" % label)

        # CLAUSE 5: THE ONLY SIZING TOLERANCE, AND IT IS RELATIVE.  The
        # absolute form of analyse_t3.py:327 is EXPRESSLY NOT ADOPTED here.
        if at_plant is None:
            refuse("%s: PLANT was not exercised by the ladder" % label)
        if not (at_plant >= PLANT * (1.0 - PLANT_REL_SLACK)):
            refuse("%s: read at PLANT is %.6e K, below the registered RELATIVE "
                   "predicate PLANT*(1-1e-9) = %.6e K"
                   % (label, at_plant, PLANT * (1.0 - PLANT_REL_SLACK)))

        # CLAUSE 8: the case was never written to, and that is CHECKED rather
        # than asserted in a comment.
        if open(fld(case_dir)).read() != open(fld(dest)).read():
            refuse("%s: the case file and the restored copy differ -- the "
                   "control may have written into the case" % label)
        return dict(passed=True, base=base, floor=floor, at_plant=at_plant,
                    n_planted=n_planted, rungs=rungs)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)  # clause 8, in a finally


# --------------------------------------------------------------------------
# RESIDUALS, AND THE SECTION 7.1 PER-CASE `Ux` DECISION.
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
    """max|Ux|, max|Uy|, max|Uz| over the fluid internalField.  MEASURED HERE
    PER CASE, and section 7.1 forbids reciting another case's ratio."""
    p = os.path.join(case_dir, ENDTIME, "fluid", "U")
    lines = open(p).read().split("\n")
    idx = [k for k, l in enumerate(lines)
           if re.match(r"\s*internalField\s+nonuniform\s+List<vector>", l)]
    if len(idx) != 1:
        refuse("%s has %d internalField vector headers, expected exactly 1"
               % (p, len(idx)))
    first, n = _list_window(lines, idx[0])
    mx = [0.0, 0.0, 0.0]
    for i in range(n):
        v = lines[first + i].strip()
        c = [float(x) for x in v[v.index("(") + 1:v.rindex(")")].split()]
        for d in range(3):
            if abs(c[d]) > mx[d]:
                mx[d] = abs(c[d])
    return mx


def ux_exclusion(mx):
    """T24 SECTION 7.1, AND THIS IS THE GUARD analyse_t23.py DOES NOT CARRY.

    -> (ratio, excluded, assert_set).  The exclusion of `Ux` from the
    convergence assertion is justified PER CASE by THAT CASE'S OWN measured
    max|Ux|/max|Uz|.  Section 7.1, frozen line 1012: "a ratio above 1e-12
    REFUSES the exclusion for that case and the row reports `Ux` asserted."

    NOTE ON WHAT "REFUSES" MEANS HERE, stated rather than left to a reader:
    section 7.1 spells out its own consequence in the same sentence -- the row
    REPORTS `Ux` ASSERTED.  It is a refusal of the EXCLUSION, not a refusal of
    the program, so this function returns a widened assertion set and does not
    exit.  It moves no gate either way, because section 3.1 registers
    convergence as an ASSERTION on the log and T24 REGISTERS NO RESIDUAL GATE
    AT ALL."""
    ratio = (mx[0] / mx[2]) if mx[2] else float("inf")
    excluded = ratio <= UX_UZ_RATIO_MAX
    aset = tuple(ASSERT_RESID) if excluded \
        else tuple(ASSERT_RESID) + (EXCLUDED_RESID,)
    return ratio, excluded, aset


# --------------------------------------------------------------------------
# y+ -- MEASURED AND REPORTED, NEVER GATED (sections 4.4, 7.2).
# --------------------------------------------------------------------------

def read_yplus(case_dir):
    """A patch dict, or "BLIND" if the log's OWN TEXT says the tool could not
    compute it, or None if no log is on disk.  A BLIND log's zeros never reach
    a value slot: a zero from a reader the tool has ALREADY SAID cannot see a
    non-zero is not evidence (CLAUDE.md rule 3)."""
    p = os.path.join(case_dir, YPLUS_LOG)
    if not os.path.isfile(p):
        return None
    txt = open(p, errors="replace").read()
    if any(s in txt for s in YPLUS_BLIND):
        return "BLIND"
    hits = re.findall(r"patch (\S+) y\+ : min = ([0-9.eE+-]+), "
                      r"max = ([0-9.eE+-]+), average = ([0-9.eE+-]+)", txt)
    return {h[0]: (float(h[1]), float(h[2]), float(h[3])) for h in hits} or None


# --------------------------------------------------------------------------
# COST AND LOAD (sections 3.5a, 5.5, 6.5).
# --------------------------------------------------------------------------

def wall_from_log(case_dir):
    """(ExecutionTime s, ClockTime s or None) from the LAST ExecutionTime line
    of log.solve.  Section 3.5a: the per-case wall time is sourced from the
    case's OWN log and NEVER from STATUS, which the queue runner clobbers."""
    p = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(p):
        refuse("no log.solve in %s -- the cost figure is not estimated" % case_dir)
    txt = open(p, errors="replace").read()
    hits = re.findall(r"ExecutionTime = ([0-9.eE+-]+) s"
                      r"(?:\s+ClockTime = ([0-9.eE+-]+) s)?", txt)
    if not hits:
        refuse("log.solve in %s carries no ExecutionTime line -- the cost is "
               "NOT MEASURED and is not guessed" % case_dir)
    ex, ck = hits[-1]
    return float(ex), (float(ck) if ck else None)


def read_start(case_dir, case):
    """The START.<case> load reading (section 3.5b), or None if absent.  It is
    written BEFORE the solver line, because after the fact a contended number
    is indistinguishable from a mispredicted one (section 5.5)."""
    p = os.path.join(case_dir, "START.%s" % case)
    if not os.path.isfile(p):
        return None
    return dict(re.findall(r"^([a-z_]+)=(.*)$", open(p).read(), re.M))


# --------------------------------------------------------------------------
# SECTION 2.4 -- THE LINEARITY PREDICTOR.  REPORTED, NEVER GATED.
# --------------------------------------------------------------------------

def predicted_rise_K(p_w, u_ms):
    if u_ms not in T23_RISE_K:
        refuse("no T23 reference rise for U = %s m/s -- section 2.4's "
               "predictor is not extrapolated" % u_ms)
    return (p_w / P_REF_W) * T23_RISE_K[u_ms]


def predicted_tmax_C(p_w, u_ms):
    return (T_INF_K - KELVIN_C) + predicted_rise_K(p_w, u_ms)


# --------------------------------------------------------------------------
# COMPLETION -- DELEGATED to mark_done_t24.py, section 3.5 / 3.5a.
# --------------------------------------------------------------------------

def completion_gate(root, case):
    """CRITERION 1 of section 1 line 7, and it is ONE-WAY.  Completion is
    `mark_done_t24.py`'s instrument and is CALLED, never reimplemented here.

    Two independent conditions, both required: the DONE marker exists (so the
    completion pass actually ran), and the completion check STILL passes now
    (so the marker is not stale).  Either failing REFUSES."""
    marker = os.path.join(root, "DONE.%s" % case)
    if not os.path.exists(marker):
        refuse("%s carries no DONE marker -- section 1 line 7 puts strict "
               "completion FIRST and one-way, and a row is not graded before "
               "its completion is marked. Run mark_done_t24.py first." % case)
    fails, notes = MD.check(root, case)
    if fails:
        refuse("%s carries a DONE marker but FAILS the completion check NOW, "
               "so the marker is STALE and the row is NOT graded: %s"
               % (case, "; ".join(fails)))
    return notes


# --------------------------------------------------------------------------
# THE BANDS -- section 1 line 4, applied in the ONE-WAY order of line 7.
# Kept in ONE function so the order is in one place and a mutation of it is
# visible as a mutation of the order.
# --------------------------------------------------------------------------

def apply_bands(q1_C, q2_C, mesh_ok):
    """-> (b3, b2, b1, verdict, flag).

    SECTION 1 LINE 7, THE REGISTERED ORDER, AND IT IS ONE-WAY:
      1. strict completion              (handled in completion_gate, before this)
      2. instrument admission           (handled by planted_zero_control, before this)
      2a. mesh identity, section 3.7    (a mismatch makes the row NOT A RESULT)
      3. B3 anti-degeneracy             -> failure is NOT A RESULT whatever the values say
      4. B2 then B1

    "A gate may only turn a PASS into NOT A RESULT, never the reverse"
    (frozen line 266).  That is why B3 is tested before B2 and B1, and why no
    later band can promote a row that an earlier one demoted.

    AUTHOR'S DISCLOSURE, flagged for the freezing supervisor: section 1 line 7
    enumerates FOUR criteria and does NOT name the section 3.7 mesh identity
    check among them, while section 3.7 says the check runs "before grading"
    and that a mismatch makes the affected rows NOT A RESULT.  This file places
    it immediately before B3.  The placement is the strictest reading available
    -- it can only demote -- but it IS a reading, and it is disclosed here
    rather than buried."""
    b3 = (q1_C >= q2_C) and (q1_C != q2_C)
    b2 = q1_C > B2_FLOOR_C
    b1 = q1_C < B1_BOUND_C
    if not mesh_ok:
        verdict, flag = "NOT A RESULT", None
    elif not b3:
        verdict, flag = "NOT A RESULT", None
    elif not b2:
        verdict, flag = "GATE FAIL", None
    elif not b1:
        # SECTION 1 LINE 4, FROZEN LINE 228: B1's not-met branch is a FLAGGED
        # PASS and is NOT a GATE FAIL.  Directive 3.6 makes an over-bound point
        # "a real finding" and not a failure.  Zero flags was never the
        # requirement of this tier and must not be engineered for.
        verdict, flag = "PASS", B1_FLAG
    else:
        verdict, flag = "PASS", None
    return b3, b2, b1, verdict, flag


# --------------------------------------------------------------------------
# GRADING
# --------------------------------------------------------------------------

def _header():
    print("T24 -- THE PHYSICALITY TIER OF THE 16-POINT MAP, AND NOTHING ELSE.")
    print("Gates: %s section 1 line 4, FROZEN at %s." % (FROZEN_DOC, FREEZE_SHA))
    print("SECTION 0.3: NO Nusselt correlation, NO Roache triple, NO GCI, NO "
          "observed order, NO heat-balance closure -- all DEFERRED at section 4.")
    print("SECTION 1 LINE 5 REGISTERS NO LADDER.  Every point is L1 only and a "
          "SINGLE MESH LEVEL ADMITS NO TRIPLE, so no Roache classification, "
          "GCI or observed order is computed, quoted or quotable from this "
          "artifact -- section 0.3 calls doing so a CATEGORY ERROR. CLAUDE.md "
          "rule 5 is not weakened by that: it governs a grid triple, and this "
          "rung produces none.")
    print("SECTION 3.4: the directive's Ri < 0.1 criterion is DECLARED VACUOUS "
          "here and is NOT reported as a passing check. With g = (0 0 0) "
          "registered at section 3.3, Ri is identically zero BY CONSTRUCTION, "
          "so the check cannot fail and cannot inform. The honest statement is "
          "the one registered: buoyancy is switched OFF in T24, its neglect is "
          "a declared omission, and whether forced convection genuinely "
          "dominates is NOT established by this rung.")
    print("PLANT = %.6e K, IMPORTED from scripts/roache_triple.py and never "
          "redefined here (section 3.6 clause 6).\n" % PLANT)


def grade(root, cases, ref_root=None):
    out, worst = {}, EXIT_OK
    _header()

    # SECTION 3.7, before any row is graded.
    mesh_ok, digests, ref = mesh_identity(root, cases, ref_root=ref_root)
    print("SECTION 3.7 MESH IDENTITY, against %s: %s"
          % (MESH_REF_CASE,
             "ALL %d CASES BYTE-IDENTICAL in every region" % len(cases)
             if all(mesh_ok.values()) else
             "MISMATCH on %s -- those rows are NOT A RESULT"
             % ",".join(c for c in cases if not mesh_ok[c])))
    for r in MESH_REGIONS:
        print("  %s/polyMesh/points sha256 %s  [reference %s]"
              % (r, ref[r][:16], MESH_REF_CASE))
    print("")

    for case in cases:
        p_w, u_ms = case_pu(case)
        d = os.path.join(root, case)
        if not os.path.isdir(d):
            refuse("no case directory %s" % d)

        print("=== %s   (P_loss %d W, U_inf %d m/s) ===" % (case, p_w, u_ms))

        # --- CRITERION 1: STRICT COMPLETION, delegated and one-way.
        notes = completion_gate(root, case)
        for n in notes:
            print("  completion NOTE: %s" % n)

        # --- CRITERION 2: INSTRUMENT ADMISSION, before any value is believed.
        areas = patch_face_areas(d, "housing", IFACE_PATCH)
        c1 = planted_zero_control(d, "Q1(internalField)", read_Q1, plant_Q1)
        c2 = planted_zero_control(d, "Q2(boundaryField areaAvg)",
                                  lambda x: read_Q2(x, areas), plant_Q2)
        for lbl, c in (("Q1", c1), ("Q2", c2)):
            print("  PLANTED-ZERO CONTROL %s: PASS. negative arm difference "
                  "exactly 0.0 (no tolerance); ladder floor %.0e K; read at "
                  "PLANT %.6e K, against the RELATIVE predicate "
                  "PLANT*(1-1e-9) = %.6e K (section 3.6 clause 5; the absolute "
                  "form of analyse_t3.py:327 is expressly NOT adopted); values "
                  "planted %d"
                  % (lbl, c["floor"], c["at_plant"],
                     PLANT * (1.0 - PLANT_REL_SLACK), c["n_planted"]))

        # --- SECTION 3.7 for this row.
        if not mesh_ok[case]:
            print("  SECTION 3.7 MESH IDENTITY: FAILED -- this case's points "
                  "differ from %s's. Section 1 line 1's registered claim that "
                  "the mesh is identical by construction would then be FALSE, "
                  "and section 2.4's prediction rests on it. THIS ROW IS NOT A "
                  "RESULT." % MESH_REF_CASE)

        # --- QUANTITIES (section 1 line 3).
        q1_K, q2_K = read_Q1(d), read_Q2(d, areas)
        q1, q2 = q1_K - KELVIN_C, q2_K - KELVIN_C
        print("  Q1 T_max(housing, internalField)          = %.6f K = %.4f degC"
              "  [MEASURED]" % (q1_K, q1))
        print("  Q2 areaAvg T(housing side of %s, boundaryField `value`, never "
              "refValue) = %.6f K = %.4f degC  [MEASURED, over %d faces, total "
              "area %.6e m2]" % (IFACE_PATCH, q2_K, q2, len(areas), sum(areas)))
        print("  Q1 - Q2 = %+.6f K" % (q1 - q2))

        # --- BANDS, in the registered one-way order (section 1 line 7).
        b3, b2, b1, verdict, flag = apply_bands(q1, q2, mesh_ok[case])
        print("  B3  Q1 >= Q2 and Q1 != Q2 : %s"
              % ("PASS" if b3 else "NOT A RESULT -- the two readers returned "
                 "the same object twice, which is a finding about the "
                 "INSTRUMENT and not about the solver (section 1 line 3)"))
        print("  B2  Q1 > %.1f degC        : %s"
              % (B2_FLOOR_C, "PASS" if b2 else "GATE FAIL"))
        print("  B1  Q1 < %.1f degC      : %s  (margin %+.4f K)"
              % (B1_BOUND_C,
                 "PASS" if b1 else 'PASS, FLAGGED "%s"' % B1_FLAG,
                 B1_BOUND_C - q1))
        print("  VERDICT: %s%s"
              % (verdict, '  FLAGGED "%s"' % flag if flag else ""))
        if flag:
            print("    A FLAG IS A REAL FINDING, NOT A FAILURE (directive 3.6; "
                  "section 1 line 4 registers the not-met branch as a FLAGGED "
                  "PASS before compute). Zero flags was never the requirement "
                  "of this tier and must not be engineered for.")
        if verdict != "PASS" or flag:
            worst = EXIT_NOTCLEAN

        # --- SECTION 2.4, THE LINEARITY PREDICTOR.  REPORTED, NEVER GATED.
        pred_rise = predicted_rise_K(p_w, u_ms)
        pred_C = predicted_tmax_C(p_w, u_ms)
        rise = q1_K - T_INF_K
        dep = (rise - pred_rise) / pred_rise * 100.0 if pred_rise else float("inf")
        fired = abs(dep) > LINEARITY_TOL_FRAC * 100.0
        print("  section 2.4 LINEARITY PREDICTOR [REGISTERED, REPORTED, NEVER "
              "A GATE]: predicted rise %.4f K -> predicted T_max %.4f degC "
              "(from T23's MEASURED rise %.3f K at U = %d m/s, scaled by "
              "P/305); solved rise %.4f K; departure %+.4f %% of the predicted "
              "rise, against the registered 2 %% tolerance -- %s"
              % (pred_rise, pred_C, T23_RISE_K[u_ms], u_ms, rise, dep,
                 "FIRED" if fired else "not fired"))
        if fired:
            print("    THE LINEARITY ARGUMENT OF SECTION 2.4 IS THE THING THAT "
                  "WAS FALSIFIED, exactly as that section registered one-way "
                  "and before compute -- a reportable finding about the case "
                  "construction or the solver (a temperature-dependent "
                  "property that should not be there, an unconverged field, a "
                  "source that is not what was entered, or a mesh that is not "
                  "the mesh assumed). IT CHANGES B1, B2 AND B3 NOT AT ALL, "
                  "because those grade the SOLVED temperature and not the "
                  "predictor, and this row still carries the verdict above.")

        # --- SECTION 7.1: the Ux decision, MEASURED ON THIS CASE.
        mx = u_component_maxima(d)
        ratio, excluded, aset = ux_exclusion(mx)
        res = final_residuals(d)
        print("  max|Ux| = %.6e m/s, max|Uy| = %.6e m/s, max|Uz| = %.6e m/s ; "
              "max|Ux|/max|Uz| = %.3e  [MEASURED ON THIS CASE, %s/fluid/U, "
              "never recited from T23]" % (mx[0], mx[1], mx[2], ratio, ENDTIME))
        print("  final initial residuals (LAST Time = %s block): %s"
              % (ENDTIME, ", ".join("%s %.6e" % (k, res[k]) for k in sorted(res)
                                    if k in set(ASSERT_RESID) | {EXCLUDED_RESID})))
        if excluded:
            print("  section 7.1: max|Ux|/max|Uz| = %.3e is AT OR BELOW the "
                  "registered %.0e, so the EXCLUSION OF Ux IS JUSTIFIED ON "
                  "THIS CASE. x is the CIRCUMFERENTIAL direction of a 5-degree "
                  "wedge one cell thick, so Ux is identically zero BY "
                  "GEOMETRY, and its initial residual %.6e is a 0/0 "
                  "normalisation carrying NO information. THE EXCLUDED VALUE "
                  "IS PRINTED, NEVER SUPPRESSED."
                  % (ratio, UX_UZ_RATIO_MAX, res.get("Ux", float("nan"))))
        else:
            print("  section 7.1: max|Ux|/max|Uz| = %.3e is ABOVE the "
                  "registered %.0e, WHICH REFUSES THE EXCLUSION FOR THIS CASE. "
                  "Ux is NOT identically zero here, so its residual is not a "
                  "0/0 artefact and this row REPORTS Ux ASSERTED. The guard "
                  "fired on this case's OWN measurement and not on T23's."
                  % (ratio, UX_UZ_RATIO_MAX))
        bad = [k for k in aset if k in res and res[k] > RESID_TOL]
        miss = [k for k in aset if k not in res]
        conv = (not bad) and (not miss)
        print("  CONVERGENCE ASSERTION (section 3.1: an ASSERTION on the log, "
              "NEVER a stopping rule; T24 registers NO residual gate at all): "
              "asserted over %s at %.0e -- %s%s"
              % (",".join(aset), RESID_TOL, "HOLDS" if conv else "DOES NOT HOLD",
                 "" if conv else " (over tolerance: %s; absent: %s)"
                 % (",".join(bad) or "none", ",".join(miss) or "none")))
        print("  THIS MOVES NO GATE EITHER WAY: no band in section 1 line 4 "
              "reads a residual, and section 3.1 registers no residualControl "
              "stopping criterion in any region.")

        # --- y+, MEASURED AND REPORTED, NEVER GATED (sections 4.4, 7.2).
        yp = read_yplus(d)
        yplus_max = None
        if yp is None:
            print("  y+ on the housing wall: NOT MEASURED -- no %s on disk. "
                  "REPORTED as not measured, NEVER as a zero (rule 3). The "
                  "registered route is: %s. Section 4.4 registers y+ as "
                  "reported and NOT a gate, so its absence touches no verdict "
                  "above." % (YPLUS_LOG, YPLUS_REGISTERED_CMD))
        elif yp == "BLIND":
            print("  y+ on the housing wall: NOT MEASURED -- the log's OWN TEXT "
                  "says the turbulence model was not in the database and yPlus "
                  "would not be calculated, and it then printed min/max/average "
                  "of 0. THOSE ZEROS ARE REFUSED, NOT READ (rule 3, section "
                  "7.2): a zero from a reader shown unable to see a non-zero is "
                  "not evidence. Re-measure through the registered route: %s"
                  % YPLUS_REGISTERED_CMD)
            yp = None
        else:
            for patch, (mn, mxv, av) in sorted(yp.items()):
                tag = "  <- THE HOUSING SURFACE (section 4.4)" \
                    if patch == YPLUS_HOUSING_PATCH else ""
                print("  y+ on %s: min %.4g, max %.4g, average %.4g  "
                      "[MEASURED, REPORTED, NOT GATED]%s"
                      % (patch, mn, mxv, av, tag))
            h = yp.get(YPLUS_HOUSING_PATCH)
            if h:
                yplus_max = h[1]
                if h[1] > 1.0:
                    print("    max y+ on the housing surface is %.4g, ABOVE 1. "
                          "Section 4.4 registers exactly this outcome IN "
                          "ADVANCE and states it is NOT a discovery this rung "
                          "makes: it BLOCKS the correlation tier and the map's "
                          "triple -- NEITHER OF WHICH THIS RUNG CLAIMS -- and "
                          "it DOES NOT VOID the physicality rows, whose "
                          "content is a temperature bound and not a "
                          "heat-transfer coefficient." % h[1])

        # --- COST (sections 3.5a, 5.5, 6.5).
        ex_s, ck_s = wall_from_log(d)
        core_min = ex_s * RANKS / 60.0
        print("  cost: ExecutionTime %.1f s at %d rank = %.4f core-min "
              "[MEASURED, DERIVED FROM THIS CASE'S OWN log.solve, never from "
              "STATUS (section 3.5a)]%s; per-case CAP %.1f core-min"
              % (ex_s, RANKS, core_min,
                 "; ClockTime %.1f s" % ck_s if ck_s is not None else "",
                 PER_CASE_CAP_CORE_MIN))
        if core_min > PER_CASE_CAP_CORE_MIN:
            print("    OVER THE REGISTERED PER-CASE CAP by %.4f core-min. Rule "
                  "12: an overrun STOPS the run and does not get a new budget. "
                  "This is REPORTED here and the completion instrument owns the "
                  "capping decision." % (core_min - PER_CASE_CAP_CORE_MIN))
        st = read_start(d, case)
        if st is None:
            print("  START.%s: ABSENT -- the pre-solver load reading is NOT "
                  "MEASURED for this case (section 3.5b registered that the "
                  "launcher writes one)." % case)
        else:
            la = st.get("loadavg", "NOT MEASURED")
            npr = st.get("nproc", "NOT MEASURED")
            print("  START.%s [section 3.5b, written BEFORE the solver line]: "
                  "start_utc %s, loadavg %s, nproc %s, solvers already running "
                  "%s" % (case, st.get("start_utc", "NOT MEASURED"), la, npr,
                          st.get("solvers_already_running", "NOT MEASURED")))
            try:
                if float(la.split()[0]) > float(npr):
                    print("    SATURATED at launch (1-minute load average above "
                          "nproc). Section 5.5 registers this as producing a "
                          "COST but NOT a calibration row: after the fact a "
                          "contended number is indistinguishable from a "
                          "mispredicted one.")
            except (ValueError, IndexError, AttributeError):
                pass

        out[case] = dict(
            P_loss_W=p_w, U_inf_ms=u_ms,
            Q1_degC=q1, Q2_degC=q2, Q1_K=q1_K, Q2_K=q2_K, Q1_minus_Q2_K=q1 - q2,
            B1=bool(b1), B2=bool(b2), B3=bool(b3),
            B1_margin_K=B1_BOUND_C - q1,
            verdict=verdict, flag=flag,
            mesh_identical_to_T23=bool(mesh_ok[case]),
            points_sha256=digests[case],
            predicted_rise_K=pred_rise, predicted_Tmax_degC=pred_C,
            solved_rise_K=rise, linearity_departure_pct=dep,
            linearity_contingency_fired=bool(fired),
            max_Ux=mx[0], max_Uy=mx[1], max_Uz=mx[2], ux_uz_ratio=ratio,
            ux_excluded=bool(excluded), assertion_set=list(aset),
            residuals=res, convergence_assertion=bool(conv),
            yplus_housing_max=yplus_max,
            execution_time_s=ex_s, core_min=core_min,
            start=st,
            control_Q1_floor=c1["floor"], control_Q2_floor=c2["floor"],
            control_Q1_at_plant=c1["at_plant"],
            control_Q2_at_plant=c2["at_plant"],
        )
        print("")
    return out, worst


def print_map(out):
    """SECTION 6.5: the full 16-point map assembled from T23's four rows and
    these twelve, WITH EACH ROW'S PROVENANCE RUNG NAMED -- "a map that does not
    say which rung measured which row is not auditable"."""
    print("=== THE 16-POINT P_loss x U_inf MAP (section 6.5) ===")
    print("T_max on the housing, degC. Provenance named per row: T24 rows are "
          "MEASURED by this pass; T23 rows are MEASURED at T23 and TRANSCRIBED "
          "here from the frozen T24 document section 1 line 4 (200.0 degC minus "
          "the stated B1 margins). NO ROW IS RE-GRADED and T23's frozen numbers "
          "are NOT rewritten (CLAUDE.md rule 6).")
    print("  %-9s %-10s %-12s %-14s %s"
          % ("P_loss W", "U_inf m/s", "T_max degC", "provenance", "verdict"))
    for p in POWERS_W + (305,):
        for u in SPEEDS_MS:
            if p == 305:
                print("  %-9d %-10d %-12.4f %-14s %s"
                      % (p, u, T23_TMAX_C[(p, u)], "T23 [MEASURED]",
                         "PASS (T23, not re-graded here)"))
            else:
                case = "T24_P%03d_U%d" % (p, u)
                r = out.get(case)
                if r is None:
                    print("  %-9d %-10d %-12s %-14s %s"
                          % (p, u, "PENDING", "T24", "PENDING: %s" % case))
                else:
                    print("  %-9d %-10d %-12.4f %-14s %s%s"
                          % (p, u, r["Q1_degC"], "T24 [MEASURED]", r["verdict"],
                             ' FLAGGED "%s"' % r["flag"] if r["flag"] else ""))
    done = [r for r in out.values()]
    if done:
        tot = sum(r["core_min"] for r in done)
        print("  subset cost so far: %.4f core-min over %d rows, against the "
              "registered POINT %.1f and hard CAP %.1f core-min (section 1 "
              "line 8)" % (tot, len(done), SUBSET_POINT_CORE_MIN,
                           SUBSET_CAP_CORE_MIN))
    print("  THE 120 degC ISOTHERM IS NOT TRACED (sections 2.3(b), 4.5): it is "
          "registered IN ADVANCE as predicted to lie OFF THE MAP ENTIRELY, and "
          "that is a finding about the level set rather than a defect "
          "discovered here.")


# --------------------------------------------------------------------------
# SELFTEST.  Forged trees only.  A control that cannot refuse is not a control,
# and a selftest that only drives the passing arm measures nothing.
# --------------------------------------------------------------------------

def forge_case(root, case, q1_vals=(300.0, 300.5, 301.0, 301.5),
               q2_vals=(290.0, 291.0), ux=(1e-15, 2e-15), uz=(20.0, 10.0),
               ux_resid=0.135, yplus="good", mesh_tag="REF",
               endtime=None, exec_s=1200.0, with_done=True, with_start=True):
    """A three-region case tree with known values.  NO REAL CASE DATA IS USED
    OR READ ANYWHERE IN THIS FILE'S TESTS."""
    et = endtime or ENDTIME
    d = os.path.join(root, case)
    for sub in (os.path.join(et, "housing"), os.path.join(et, "fluid"),
                os.path.join(et, "core"), os.path.join("0", "housing"),
                "system"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    for r in MESH_REGIONS:
        os.makedirs(os.path.join(d, "constant", r, "polyMesh"), exist_ok=True)

    open(os.path.join(d, et, "housing", "T"), "w").write(
        "FoamFile\n{\n}\n"
        "internalField   nonuniform List<scalar> \n%d\n(\n" % len(q1_vals)
        + "\n".join("%.12g" % v for v in q1_vals) + "\n)\n;\n\n"
        "boundaryField\n{\n    %s\n    {\n" % IFACE_PATCH
        + "        type            compressible::turbulentTemperatureRadCoupledMixed;\n"
        "        refValue        nonuniform List<scalar> \n2\n(\n1\n2\n)\n;\n"
        "        value           nonuniform List<scalar> \n%d\n(\n" % len(q2_vals)
        + "\n".join("%.12g" % v for v in q2_vals) + "\n)\n;\n    }\n}\n")
    open(os.path.join(d, et, "fluid", "U"), "w").write(
        "internalField   nonuniform List<vector> \n%d\n(\n" % len(ux)
        + "\n".join("(%r 0.5 %r)" % (ux[i], uz[i]) for i in range(len(ux)))
        + "\n)\n;\n")
    for region, flds in MD.NEEDED.items():
        for f in flds:
            p = os.path.join(d, et, region, f)
            if not os.path.exists(p):
                open(p, "w").write("dummy\n")
    open(os.path.join(d, "0", "housing", "T"), "w").write("age reference\n")

    log = ["Time = %s" % et,
           "DILUPBiCGStab:  Solving for Ux, Initial residual = %r, Final "
           "residual = 1e-4, No Iterations 1" % ux_resid,
           "DILUPBiCGStab:  Solving for Uy, Initial residual = 6.25e-10, "
           "Final residual = 6.25e-10, No Iterations 0",
           "DILUPBiCGStab:  Solving for Uz, Initial residual = 4.22e-12, "
           "Final residual = 4.22e-12, No Iterations 0",
           "DILUPBiCGStab:  Solving for h, Initial residual = 9.59e-10, "
           "Final residual = 9.59e-10, No Iterations 0",
           "GAMG:  Solving for p_rgh, Initial residual = 8.64e-09, Final "
           "residual = 1e-9, No Iterations 1",
           "DILUPBiCGStab:  Solving for omega, Initial residual = 9.5e-10, "
           "Final residual = 9.5e-10, No Iterations 0",
           "DILUPBiCGStab:  Solving for k, Initial residual = 9.9e-10, "
           "Final residual = 9.9e-10, No Iterations 0"]
    # rule 4 conjunct 5: one ExecutionTime line per iteration.
    log += ["ExecutionTime = %r s  ClockTime = %r s" % (exec_s, exec_s + 5)
            for _ in range(int(float(et)) - 1)]
    log += ["ExecutionTime = %r s  ClockTime = %r s" % (exec_s, exec_s + 5),
            "", "End", ""]
    open(os.path.join(d, "log.solve"), "w").write("\n".join(log))
    open(os.path.join(d, "system", "controlDict"), "w").write(
        "endTime %s;\ndeltaT 1;\n" % et)
    open(os.path.join(d, "STATUS.%s" % case), "w").write("launcher_rc=0\n")
    if with_start:
        open(os.path.join(d, "START.%s" % case), "w").write(
            "case=%s\nstart_utc=2026-08-31T20:01:00Z\nloadavg=0.50 0.40 0.30\n"
            "nproc=16\nsolvers_already_running=0\n" % case)

    # a 2-face unit-square patch, so the area weights are exactly 1.0 each
    for r in MESH_REGIONS:
        pm = os.path.join(d, "constant", r, "polyMesh")
        open(os.path.join(pm, "boundary"), "w").write(
            "// * * *\n1\n(\n    %s\n    {\n        type mappedWall;\n"
            "        nFaces 2;\n        startFace 0;\n    }\n)\n" % IFACE_PATCH)
        open(os.path.join(pm, "points"), "w").write(
            "// * * *\n6\n(\n(0 0 0)\n(1 0 0)\n(1 1 0)\n(0 1 0)\n(2 0 0)\n"
            "(2 1 0)\n)\n" + ("" if mesh_tag == "REF" else "// %s\n" % mesh_tag))
        open(os.path.join(pm, "faces"), "w").write(
            "// * * *\n2\n(\n4(0 1 2 3)\n4(1 4 5 2)\n)\n")

    # every field at endTime must be NEWER than 0/housing/T (rule 4 conjunct 6)
    ref_t = os.path.getmtime(os.path.join(d, "0", "housing", "T"))
    for region, flds in MD.NEEDED.items():
        for f in flds:
            os.utime(os.path.join(d, et, region, f), (ref_t + 10, ref_t + 10))
    if with_done:
        open(os.path.join(root, "DONE.%s" % case), "w").write("done\n")
    return d


def forge_mesh_reference(root, tag="REF"):
    """A T23_P305_U10 stand-in carrying the reference `points`."""
    d = os.path.join(root, MESH_REF_CASE)
    for r in MESH_REGIONS:
        pm = os.path.join(d, "constant", r, "polyMesh")
        os.makedirs(pm, exist_ok=True)
        open(os.path.join(pm, "points"), "w").write(
            "// * * *\n6\n(\n(0 0 0)\n(1 0 0)\n(1 1 0)\n(0 1 0)\n(2 0 0)\n"
            "(2 1 0)\n)\n" + ("" if tag == "REF" else "// %s\n" % tag))
    return root


def selftest():
    fails = []

    def chk(label, cond):
        print("  [%s] %s" % ("ok " if cond else "FAIL", label))
        if not cond:
            fails.append(label)

    def drive(label, fn, want_refuse=False):
        buf, code, val = io.StringIO(), None, None
        try:
            with contextlib.redirect_stdout(buf):
                val = fn()
        except SystemExit as e:
            code = e.code
        if want_refuse:
            chk(label, code == EXIT_REFUSE)
            if code != EXIT_REFUSE:
                print(buf.getvalue())
            return None
        chk(label, code is None)
        if code is not None:
            print(buf.getvalue())
        return val, buf.getvalue()

    clear_pycache()
    tmp = tempfile.mkdtemp(prefix="t24an_")
    try:
        case = CASES[0]                                   # T24_P080_U10
        d = forge_case(tmp, case)
        forge_mesh_reference(tmp)

        # --- THE TWO READERS
        areas = patch_face_areas(d, "housing", IFACE_PATCH)
        chk("face areas = [1.0, 1.0] (unit squares, computed not assumed)",
            [round(a, 12) for a in areas] == [1.0, 1.0])
        chk("Q1 reads the internalField MAXIMUM 301.5",
            abs(read_Q1(d) - 301.5) < 1e-12)
        chk("Q2 reads the areaAvg of the `value` list (290.5) and NOT refValue "
            "(1.5)", abs(read_Q2(d, areas) - 290.5) < 1e-12)

        # --- THE PLANTED-ZERO CONTROL, both arms and both refusals.
        c1 = planted_zero_control(d, "Q1", read_Q1, plant_Q1)
        c2 = planted_zero_control(d, "Q2", lambda x: read_Q2(x, areas), plant_Q2)
        chk("Q1 control PASSES and plants exactly 1 value",
            c1["passed"] and c1["n_planted"] == 1)
        chk("Q2 control PASSES and plants ALL 2 faces, so the shift is PLANT "
            "and not PLANT/N", c2["passed"] and c2["n_planted"] == 2
            and abs(c2["at_plant"] - PLANT) < 1e-12)
        chk("read at PLANT satisfies the RELATIVE predicate PLANT*(1-1e-9)",
            c1["at_plant"] >= PLANT * (1.0 - PLANT_REL_SLACK))
        drive("BLIND reader (returns a constant) -> REFUSE",
              lambda: planted_zero_control(d, "neg", lambda p: 1.0, plant_Q1),
              want_refuse=True)
        _st = {"n": 0}

        def noisy(p):
            # the wobble must exceed one ULP of a ~300 K value (~5.7e-14), or
            # "noise" is a no-op and the arm proves nothing
            _st["n"] += 1
            return read_Q1(p) + _st["n"] * 1e-9
        drive("NOISY reader (negative arm != bitwise 0.0) -> REFUSE",
              lambda: planted_zero_control(d, "neg", noisy, plant_Q1),
              want_refuse=True)
        _st2 = {"n": 0}

        def faintly_noisy(p):
            # A wobble of 1e-13 K: BELOW any plausible absolute tolerance
            # somebody might smuggle into the negative arm, and ABOVE one ULP
            # of a ~300 K value (5.7e-14), so it is a real difference and not a
            # rounding artefact. Clause 2 registers the threshold as BITWISE
            # 0.0 with NO tolerance, so this MUST still refuse -- and this arm
            # is what makes that "no tolerance" load-bearing rather than
            # decorative.
            _st2["n"] += 1
            return read_Q1(p) + _st2["n"] * 1e-13
        drive("FAINTLY noisy reader (wobble 1e-13 K, below any smuggled "
              "tolerance) -> STILL REFUSE, because clause 2 is bitwise 0.0",
              lambda: planted_zero_control(d, "neg", faintly_noisy, plant_Q1),
              want_refuse=True)

        # THE REGISTERED PREDICATE IS RELATIVE, AND HERE IS THE READER THAT
        # SEPARATES IT FROM THE REJECTED ABSOLUTE ONE.  A read that loses ONE
        # ULP of a ~301.5 K field (5.684e-14 K) is a rounding wiggle, not a
        # blind reader: section 3.6 clause 5 registers the RELATIVE predicate
        # precisely so such a read is ADMITTED, and records that the absolute
        # window `PLANT - 1e-15` is 0.0176 of that ULP and would REFUSE it.
        # This arm drives that difference through the control itself.
        _base = {}
        LOSS = math.ulp(301.5)

        def one_ulp_lossy(p):
            v = read_Q1(p)
            if "v0" not in _base:
                _base["v0"] = v
                return v
            if v == _base["v0"]:
                return v                    # negative arm stays bitwise exact
            return v - LOSS                 # a planted read loses one ULP
        lossy_ctl = planted_zero_control(d, "one-ULP-lossy", one_ulp_lossy,
                                         plant_Q1)
        chk("a read that lost ONE ULP of a 301.5 K field (%.3e K) is ADMITTED "
            "by the registered RELATIVE predicate (window %.3e K) and would be "
            "REFUSED by the rejected absolute one (window 1.0e-15 K) -- this "
            "is section 3.6 clause 5's ground, driven through the control"
            % (LOSS, PLANT * PLANT_REL_SLACK),
            lossy_ctl["passed"]
            and lossy_ctl["at_plant"] >= PLANT * (1.0 - PLANT_REL_SLACK)
            and lossy_ctl["at_plant"] < PLANT - 1e-15)

        # CLAUSE 4 IS SHADOWED BY CLAUSE 5, AND THAT IS MEASURED HERE RATHER
        # THAN LEFT FOR SOMEBODY TO ASSUME OTHERWISE.  `floor is None` holds
        # only if EVERY ladder magnitude read zero, PLANT among them, so
        # `at_plant` is then 0.0 and clause 5 refuses the same reader.  Clause
        # 4's value is DIAGNOSTIC -- it names the reader BLIND instead of
        # merely undersized -- and it is not an independent gate.
        blind_at_plant = []

        def blind(p):
            blind_at_plant.append(1.0)
            return 1.0
        drive("BLIND reader -> REFUSE (and see the shadowing note below)",
              lambda: planted_zero_control(d, "neg", blind, plant_Q1),
              want_refuse=True)
        chk("MEASURED: clause 4 (BLIND) is SHADOWED by clause 5 (sizing) -- a "
            "reader with floor None reads 0.0 at PLANT, and 0.0 >= "
            "PLANT*(1-1e-9) is false, so clause 5 refuses the same reader. "
            "Clause 4 is a DIAGNOSTIC, not an independent gate.",
            not (0.0 >= PLANT * (1.0 - PLANT_REL_SLACK)))

        # THE REGISTRATION'S OWN REJECTED ALTERNATIVE, DRIVEN AS A CONTROL.
        # Section 3.6 clause 5 rejects analyse_t3.py:327's absolute predicate
        # because on a ~300 K field `PLANT - 1e-15` is 0.0176 of one ULP.  This
        # arm MEASURES that claim rather than reciting it: a reader that loses
        # the plant entirely to rounding is caught by the RELATIVE predicate,
        # and the absolute one would be decided by the rounding wiggle.
        ulp = math.ulp(301.5)
        chk("section 3.6 clause 5's ground is MEASURED here: 1e-15 is %.4f of "
            "one ULP at 301.5 K (< 1, so the absolute window is narrower than "
            "the smallest representable step)" % (1e-15 / ulp), 1e-15 < ulp)

        # --- SECTION 7.1, BOTH LIMBS.  This is the guard T23 does not carry.
        mx = u_component_maxima(d)
        ratio, excluded, aset = ux_exclusion(mx)
        chk("u_component_maxima -> max|Ux| 2e-15, max|Uz| 20.0",
            abs(mx[0] - 2e-15) < 1e-27 and abs(mx[2] - 20.0) < 1e-12)
        chk("section 7.1 LIMB A: ratio %.3e <= 1e-12 -> Ux EXCLUDED, assertion "
            "set is the registered six" % ratio,
            excluded and aset == tuple(ASSERT_RESID))
        d2 = forge_case(tmp, CASES[1], ux=(1.0, 2.0), uz=(20.0, 10.0))
        mx2 = u_component_maxima(d2)
        ratio2, excluded2, aset2 = ux_exclusion(mx2)
        chk("section 7.1 LIMB B: ratio %.3e > 1e-12 -> THE EXCLUSION IS "
            "REFUSED and Ux joins the assertion set" % ratio2,
            (not excluded2) and EXCLUDED_RESID in aset2 and len(aset2) == 7)
        # AND THE EXCLUSION IS SHOWN LOAD-BEARING (section 7.1's own words):
        # had Ux been asserted, this forged case would report NOT converged.
        res = final_residuals(d)
        chk("section 7.1 LOAD-BEARING CONTROL: with Ux asserted the forged "
            "case reports NOT converged (Ux residual %.3f > %.0e), while with "
            "Ux excluded it reports converged -- so the exclusion changes the "
            "assertion and is not decoration"
            % (res["Ux"], RESID_TOL),
            res["Ux"] > RESID_TOL
            and not [k for k in ASSERT_RESID if res.get(k, 0.0) > RESID_TOL])

        # --- SECTION 3.7, BOTH LIMBS.
        ok, dig, ref = mesh_identity(tmp, [case], ref_root=tmp)
        chk("section 3.7 LIMB A: identical points -> identity HOLDS", ok[case])
        d3 = forge_case(tmp, CASES[2], mesh_tag="DIFFERENT")
        ok2, _, _ = mesh_identity(tmp, [CASES[2]], ref_root=tmp)
        chk("section 3.7 LIMB B: one byte different -> identity FAILS and the "
            "row is NOT A RESULT", not ok2[CASES[2]])
        chk("section 3.7 mismatch DEMOTES a row that would otherwise PASS",
            apply_bands(28.35, 17.35, False)[3] == "NOT A RESULT"
            and apply_bands(28.35, 17.35, True)[3] == "PASS")

        # --- THE BANDS, every branch, in the registered order.
        chk("B1/B2/B3 all met -> PASS, unflagged",
            apply_bands(28.35, 17.35, True) == (True, True, True, "PASS", None))
        chk("B1 UNMET -> PASS FLAGGED 'beyond assumption range', NOT a GATE "
            "FAIL (section 1 line 4, frozen line 228)",
            apply_bands(250.0, 100.0, True)[3:] == ("PASS", B1_FLAG))
        # THE THRESHOLDS ARE PINNED BEHAVIOURALLY, AT THEIR OWN EDGES, not just
        # by an equality on the constant: a band tested only far from its
        # threshold does not measure where the threshold is.
        chk("B1 threshold is pinned AT ITS EDGE: 199.99 degC is unflagged PASS "
            "and 200.01 degC is FLAGGED, so the registered bound is 200.0 and "
            "not merely 'some number above the forged value'",
            apply_bands(199.99, 100.0, True)[3:] == ("PASS", None)
            and apply_bands(200.01, 100.0, True)[3:] == ("PASS", B1_FLAG))
        chk("B1_BOUND_C is the frozen 200.0 degC (section 1 line 4)",
            B1_BOUND_C == 200.0)
        chk("B2 unmet (Q1 <= 0 degC) -> GATE FAIL",
            apply_bands(-5.0, -10.0, True)[3] == "GATE FAIL")
        chk("B2 threshold is pinned AT ITS EDGE: 0.01 degC PASSES and 0.0 degC "
            "GATE FAILs (the band is strict, Q1 > 0.0)",
            apply_bands(0.01, -10.0, True)[3] == "PASS"
            and apply_bands(0.0, -10.0, True)[3] == "GATE FAIL")
        chk("B2_FLOOR_C is the frozen 0.0 degC (section 1 line 4, directive 3.6)",
            B2_FLOOR_C == 0.0)
        chk("B3 unmet (two readers return the same object) -> NOT A RESULT",
            apply_bands(28.35, 28.35, True)[3] == "NOT A RESULT")
        chk("B3 unmet (Q1 < Q2) -> NOT A RESULT",
            apply_bands(17.35, 28.35, True)[3] == "NOT A RESULT")
        chk("ONE-WAY ORDER: a B3 failure DEMOTES a row whose B1 and B2 both "
            "pass -- a gate may only turn a PASS into NOT A RESULT, never the "
            "reverse (frozen line 266)",
            apply_bands(28.35, 28.35, True)[:3] == (False, True, True)
            and apply_bands(28.35, 28.35, True)[3] == "NOT A RESULT")
        chk("ONE-WAY ORDER: B3 failure OUTRANKS a B2 failure, so a row cannot "
            "be promoted from NOT A RESULT to GATE FAIL by a later band",
            apply_bands(-5.0, -5.0, True)[3] == "NOT A RESULT")

        # --- SECTION 2.4, the predictor, checked AGAINST THE FROZEN TABLE.
        worst = 0.0
        for (p_w, u_ms), want in sorted(PREDICTED_TMAX_C.items()):
            worst = max(worst, abs(predicted_tmax_C(p_w, u_ms) - want))
        chk("section 2.4 predictor reproduces ALL TWELVE frozen table entries "
            "to %.4f degC (the arithmetic is checked against the document, not "
            "trusted)" % worst, worst < 5e-4)
        chk("the four T23 rows of the map agree with T_inf + the frozen rises "
            "(an independent path to the same numbers)",
            all(abs(T23_TMAX_C[(305, u)]
                    - ((T_INF_K - KELVIN_C) + T23_RISE_K[u])) < 1e-3
                for u in SPEEDS_MS))

        # --- y+, BOTH LIMBS DRIVEN (section 7.2).
        open(os.path.join(d, YPLUS_LOG), "w").write(
            "Unable to find turbulence model in the database: yPlus will not "
            "be calculated\npatch %s y+ : min = 0, max = 0, average = 0\n"
            % YPLUS_HOUSING_PATCH)
        chk("section 7.2 LIMB A: a BLIND log returns the SENTINEL and its "
            "zeros never reach a value slot", read_yplus(d) == "BLIND")
        open(os.path.join(d, YPLUS_LOG), "w").write(
            "patch %s y+ : min = 0.1, max = 1.39698600399, average = 0.8\n"
            % YPLUS_HOUSING_PATCH)
        good = read_yplus(d)
        chk("section 7.2 LIMB B: the SAME reader on a good log returns a real "
            "non-zero, so the BLIND result is a READING and not blindness",
            isinstance(good, dict)
            and abs(good[YPLUS_HOUSING_PATCH][1] - 1.39698600399) < 1e-12)
        os.remove(os.path.join(d, YPLUS_LOG))

        # --- COMPLETION IS DELEGATED, AND ITS ABSENCE REFUSES.
        chk("completion is delegated: mark_done_t24.check is the callee and is "
            "not reimplemented here",
            completion_gate.__doc__ is not None and MD.check is not None)
        os.remove(os.path.join(tmp, "DONE.%s" % case))
        drive("no DONE marker -> REFUSE (completion is FIRST and one-way)",
              lambda: completion_gate(tmp, case), want_refuse=True)
        open(os.path.join(tmp, "DONE.%s" % case), "w").write("done\n")
        # a STALE marker: the marker exists but the case no longer completes
        shutil.move(os.path.join(d, "log.solve"),
                    os.path.join(d, "log.solve.hidden"))
        drive("a STALE DONE marker (marker present, completion now fails) -> "
              "REFUSE", lambda: completion_gate(tmp, case), want_refuse=True)
        shutil.move(os.path.join(d, "log.solve.hidden"),
                    os.path.join(d, "log.solve"))

        # --- AN UNREGISTERED CASE NAME REFUSES: section 6.2's set is closed.
        drive("an UNREGISTERED case name -> REFUSE (6.2 names twelve, and P305 "
              "is T23's level, not this rung's)",
              lambda: case_pu("T24_P305_U10"), want_refuse=True)

        # --- END TO END on the forged tree.
        got = drive("end-to-end grade of a forged clean case",
                    lambda: grade(tmp, [case], ref_root=tmp))
        if got:
            res_map, code = got[0]
            txt = got[1]
            r = res_map[case]
            chk("forged Q1 301.5 K -> 28.35 degC, B1/B2/B3 all PASS, verdict "
                "PASS", r["verdict"] == "PASS" and r["B1"] and r["B2"]
                and r["B3"] and abs(r["Q1_degC"] - 28.35) < 1e-9)
            chk("the row carries every section 6.5 field",
                all(k in r for k in ("Q1_degC", "Q2_degC", "Q1_minus_Q2_K",
                                     "B1_margin_K", "predicted_Tmax_degC",
                                     "linearity_departure_pct",
                                     "yplus_housing_max", "residuals",
                                     "core_min", "start", "ux_uz_ratio")))
            chk("the excluded Ux residual is PRINTED, never suppressed -- it "
                "appears in the residual line AND beside the ratio that "
                "justifies its exclusion (section 7.1)",
                ("Ux %.6e" % 0.135) in txt
                and txt.count("%.6e" % 0.135) >= 2)
            chk("NO Roache/GCI/observed-order/Nusselt/heat-balance token is "
                "emitted as a computed quantity, and the no-ladder statement "
                "IS emitted (section 0.3)",
                "SINGLE MESH LEVEL ADMITS NO TRIPLE" in txt
                and "GCI =" not in txt and "observed order =" not in txt
                and "Nu =" not in txt)
            chk("section 3.4: no 'Ri = 0 < 0.1, PASS' row is printed, and the "
                "VACUOUS statement is",
                "DECLARED VACUOUS" in txt and "Ri = 0 < 0.1" not in txt)
            chk("the linearity predictor is labelled NEVER A GATE",
                "NEVER A GATE" in txt)

        # --- THE AST CONTROL.  Under `python3 -O` every `assert` is stripped,
        # so a control written as an assert would vanish silently.  This file
        # carries none, and the counter is shown able to see one.
        src = open(__file__).read()
        n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
        n1 = sum(isinstance(n, ast.Assert)
                 for n in ast.walk(ast.parse(src + "\nassert 1\n")))
        chk("AST assert count = %d, and the counter SEES a planted one (%d) -- "
            "no control in this file can be stripped by python3 -O"
            % (n0, n1), n0 == 0 and n1 == 1)
        chk("PLANT is IMPORTED, not redefined: PLANT is roache_triple.PLANT",
            PLANT is RT.PLANT and abs(PLANT - 1.234e-03) < 1e-18)
        chk("the registered run set is TWELVE distinct cases (section 6.2)",
            len(CASES) == 12 and len(set(CASES)) == 12)
        chk("the ladder is the registered nine magnitudes and contains PLANT",
            LADDER == (10.0, 1.0, 1e-1, 1e-2, PLANT, 1e-3, 1e-4, 1e-5, 1e-6))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL",
                                       len(fails)))
    return 0 if not fails else 1


def selftest_both_modes(argv):
    """T24 section 3.6 clause 9: the selftest runs under BOTH `python3` and
    `python3 -O`.  Under -O the interpreter strips `assert`, so a suite that
    only ever runs unoptimised can be green on controls that do not exist."""
    rc = selftest()
    if "--no-reexec" in argv:
        return rc
    mode = "python3 -O" if not __debug__ else "python3"
    print("\n[that run was under %s; re-running the same suite under the "
          "other mode -- clause 9]" % mode)
    flag = [] if not __debug__ else ["-O"]
    clear_pycache()
    p = subprocess.run([sys.executable] + flag
                       + [os.path.abspath(__file__), "--selftest", "--no-reexec"],
                       capture_output=True, text=True)
    ok = p.returncode == 0
    print("  [%s] the suite also passes under %s"
          % ("ok " if ok else "FAIL", "python3" if not __debug__ else "python3 -O"))
    if not ok:
        print(p.stdout[-4000:])
    return rc if rc else (0 if ok else 1)


def main(argv):
    if "--selftest" in argv:
        return selftest_both_modes(argv)
    root, jsonout = HERE, None
    if "--root" in argv:
        i = argv.index("--root")
        root = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if "--json" in argv:
        i = argv.index("--json")
        jsonout = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    want = [a for a in argv if not a.startswith("-")] or list(CASES)
    for c in want:
        case_pu(c)
    out, worst = grade(root, want)
    print_map(out)
    if jsonout:
        with open(jsonout, "w") as fh:
            json.dump(dict(rung="T24", frozen_at=FREEZE_SHA,
                           frozen_document=FROZEN_DOC, plant_K=PLANT,
                           rows=out), fh, indent=2, sort_keys=True)
        print("\nwrote %s" % jsonout)
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
