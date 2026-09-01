#!/usr/bin/env python3
"""T23G -- the grid triple at (305 W, 20 m/s).  THE COMPARATOR.

FROZEN BY THE COMMIT THAT LANDS docs/campaigns/T-family/T23G_PREREGISTRATION.md.
CLAUDE.md rule 2: the gate, the threshold, the cap and the label were fixed
before any level ran, and this file is the grading path they were fixed with.

WHAT THIS FILE DOES NOT DO
--------------------------
It does not build a mesh, it does not launch a solver, and it does not decide
whether a case is complete.  Completion is rule 4's and is DELEGATED to
`../T23_runs/mark_done_t23.py`, CALLED as a subprocess and never reimplemented
here (T23G section 7.2).

THE SEVEN THINGS THIS INSTRUMENT REFUSES OVER, rather than degrading past
------------------------------------------------------------------------
1. A LEVEL THAT IS NOT DONE.  `mark_done_t23.py` is called first; a case
   without a fresh DONE marker is never read.  A stale marker -- one older than
   the case's own <endTime> fields -- is RE-VERIFIED from raw artefacts, not
   trusted (section 7.2).

2. A READER NOT SHOWN ABLE TO SEE A NON-ZERO.  CLAUDE.md rule 3.  Nine controls
   (three quantities x three levels), each: copy first with a realpath refusal
   if the scratch resolves inside the case; a NEGATIVE ARM at BITWISE 0.0 with
   NO absolute tolerance; a MEASURED magnitude ladder with an exact epsilon-free
   floor; REFUSAL if the reader is blind; and a sizing predicate that is
   RELATIVE, `got >= PLANT*(1-1e-9)`.  `PLANT` is IMPORTED from
   scripts/roache_triple.py and is NEVER redefined here.

3. A LADDER THAT IS NOT UNIFORM IN EVERY REGION.  The cell counts are re-read
   from each level's own checkMesh logs and every region's ratio must be
   EXACTLY 4.  A conjugate ladder whose three regions refine by different
   factors is not the same interface at three resolutions, and it is a build
   fault rather than a result (section 3.3).

4. A LADDER WHOSE LEVELS DIFFER IN ANYTHING BUT h.  Geometry, boundary
   conditions, material properties, schemes, operating point, iteration count
   and solver are BYTE-COMPARED across the three levels (section 2.2).
   ONE FILE IS EXEMPTED BY NAME -- `constant/cellToRegion`, amendment A1 of
   2026-09-01 -- because it is a DERIVED ARTEFACT of the mesh with one label
   per cell, so the comparison was a GUARANTEED REFUSAL rather than a check,
   and its whole aggregate content is already checked, more strictly, by
   check_ladder_structure against the FROZEN EXPECTED_CELLS.  See
   INVARIANT_SKIP_FILES for the argument and the measurement behind it.

   AND THESE CHECKS NOW HAVE A BUILD-TIME LIMB (amendment A2): run
   `--pre-solve` once the three meshes exist and BEFORE any solver starts, so
   a build fault costs seconds of meshing rather than 158.65 core-min of
   solving.  The grade-time limb is UNCHANGED and still refuses on its own
   authority -- the build-time limb is an addition, never a substitute.

5. A dT SHIFT THAT MOVED SOMETHING IT CANNOT MOVE.  Section 4.3 registers that
   grading on dT = T - 288 K changes GCI_pct and NOTHING ELSE.  That is
   ASSERTED, not trusted: the triple is run twice, on T and on dT, and the
   order, the state and GCI_abs must agree to 1e-12.

6. A GCI BESIDE A NON-MONOTONE OR NON-CONVERGING TRIPLE.  Delegated to
   roache_triple._seal, which raises rather than asserts so that -O cannot
   strip it.

7. A VERDICT OUTSIDE THE FIXED VOCABULARY, or a gate that moved a verdict in
   the direction rule 5 forbids.  Also roache_triple._seal.

THE FINE VALUE IS GRADED.  THE RICHARDSON EXTRAPOLATE IS NEVER GRADED
---------------------------------------------------------------------
scripts/roache_triple.py carries a LIVE, DOCUMENTED SIGN DEFECT in its
Richardson extrapolate (its docstring, lines 26-74: both parent implementations
return `f_fine + e21/den` where Roache's convention is `f_fine - e21/den`).
That defect is survivable there for exactly one reason -- it is DISPLAY-ONLY,
and no verdict the module emits is a function of it.

    NO GATE IN THIS FILE READS `richardson` OR
    `richardson_parent_convention`.  Both are PRINTED beside the fine value,
    under their own names, with the sign disclosure carried through.

Gating on the extrapolate would make a KNOWN display-only defect LOAD-BEARING in
a document written after the defect was known.  T23G section 5.3.

WHAT THIS RUNG CANNOT EARN, printed on the artifact's own face
--------------------------------------------------------------
A grid triple is CODE-AND-GRID CONVERGENCE evidence.  It is not a validation
against a physical experiment.  It can move the G column and it CANNOT move the
P column, and a PASS means "the answer is no longer changing appreciably with
mesh density at this operating point", NOT "the answer is right"
(T23G section 9).  That sentence is printed by this file, every run.

    exit 0  every quantity PASS
    exit 1  at least one GATE FAIL or NOT A RESULT (a graded outcome, not an
            instrument failure)
    exit 2  REFUSAL -- the instrument declined to grade
"""

import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
T23_RUNS = os.path.join(REPO, "verification", "runs", "T-family", "T23_runs")

sys.path.insert(0, os.path.join(REPO, "scripts"))
import roache_triple as RT                                       # noqa: E402

# The field-parsing and reader path is IMPORTED from the sibling rung, not
# reimplemented.  T23G section 11 declares this coupling and records the sha of
# the imported file beside the sha of this one, so a later edit to it is VISIBLE
# rather than silent.  The reason for accepting the coupling: it means this rung
# reads Q1 and Q2 through THE SAME PROVEN PARSING PATH Act A's numbers already
# come from, rather than through a second implementation that could drift.
sys.path.insert(0, T23_RUNS)
import analyse_t23 as T23                                        # noqa: E402

# --------------------------------------------------------------------------
# REGISTERED CONSTANTS -- transcribed from the frozen pre-registration.
# Every one of these is a threshold, a label or a cap fixed before compute.
# --------------------------------------------------------------------------

PLANT = RT.PLANT                    # 1.234e-03 K.  IMPORTED.  NEVER redefined.
LADDER = (10.0, 1.0, 1e-1, 1e-2, PLANT, 1e-3, 1e-4, 1e-5, 1e-6)

DIM = 2                             # section 1: a 5 deg wedge, ONE cell thick
                                    # circumferentially.  h = (1/N)^(1/2).
ENDTIME = "10000"                   # section 2.2: held FIXED across levels
N_STEPS = 10000
T_INF_K = 288.0                     # section 4.3; build_t23.py:75
KELVIN_C = 273.15

# section 2, the three levels, COARSE FIRST.  The middle row is build_t23.py's
# own eight integers unaltered; the outer rows are those integers halved and
# doubled.  EXPECTED_CELLS is VERIFIED against each level's checkMesh logs.
LEVELS = ("T23G_C", "T23G_M", "T23G_F")
EXPECTED_CELLS = {                  # section 3.1
    "T23G_C": {"fluid": 8800,   "core": 840,   "housing": 280},
    "T23G_M": {"fluid": 35200,  "core": 3360,  "housing": 1120},
    "T23G_F": {"fluid": 140800, "core": 13440, "housing": 4480},
}
CELL_RATIO = 4                      # section 3.2: EXACT, per region, per step

# section 5.1, the gates.  FROZEN.
BAND_DT_K = (273.15 - T_INF_K, 473.15 - T_INF_K)   # 0 degC .. 200 degC, on dT
ORDER_BAND = (0.80, 2.50)           # G-ORDER, section 6.2
GCI_DISPLAY_MAX_K = 0.050           # G-GCI-DISPLAY: half of the 0.1 degC quantum
GCI_LEGACY_MAX_PCT = 2.0            # G-GCI-LEGACY: T23_PREREGISTRATION.md:518
# --- REPAIR R1, 2026-09-01.  VERIFICATION_CHARTER.md §2d.1 exception GRANTED at
# DEAD_LEVER_AUDIT §27.2 (commit af6af856).  STRUCK, NOT OVERWRITTEN (rule 6):
# the pre-repair constant stays visible beside the corrected one.
#
#   STRUCK:  REPRO_REF_Q1_K = 342.1749743329   # "MEASURED from T23_P305_U20's
#            own fieldMinMax row 10000"
#
# WHY IT WAS WRONG.  The struck value came from the `fieldMinMax` FUNCTION
# OBJECT, whose max includes BOUNDARY FACE values: it is the max over the
# `housing_to_core` patch, 342.1749743330 K over 140 faces, MEASURED.  The gate
# below compares it against `read_max_T`, which reads the `internalField` ONLY.
# The two are DIFFERENT QUANTITIES, and the struck comment says so on its face.
#
# THE AUTHORITY IS THE FROZEN REGISTRATION, WHICH DECIDED THIS BEFORE ANY LEVEL
# RAN.  `T23G_PREREGISTRATION.md:228` registers Q1's reader path as
# `internalField` of `<endTime>/housing/T`.  THE READER IS CORRECT AS WRITTEN
# AND THE REFERENCE WAS THE OUTLIER.  Corroborated three ways:
#   * :230 registers Q3's reader path the same way, so this correction RESTORES
#     CONSISTENCY with how every max(T) in this rung is registered rather than
#     making a one-off judgement about one quantity;
#   * `T23_PREREGISTRATION.md:159` independently registers the same reader path
#     for Q1, so the definition is consistent across both registrations;
#   * `T23_PREREGISTRATION.md:163` had ALREADY recorded that `internalField` and
#     `boundaryField` are "different pre-derived extents" -- the family wrote the
#     distinction down in advance, and the constant was taken from the wrong side
#     of a distinction that was already registered.
# The registration's own :794 disclosure table names `fieldMinMax` as its source
# IN ITS OWN COLUMN HEADER and never claims that number is Q1 as registered.
#
# WHAT MOVED (§2d.1 condition 3): 1.514540e-02 K, against REPRO_TOL_K = 1.0e-6 K
# -- four orders of magnitude past the tolerance.
# PRE-REPAIR PUBLISHED VALUES (§2d.1 condition 4, met per §2d.3.3 by DISCLOSING A
# MEASURED ABSENCE): NONE.  Zero graded solves exist under this registration, and
# DONE.T23G_C, DONE.T23G_M, DONE.T23G_F, T23G_GRADED.json and T23G_RESULTS.md are
# absent both on disk and at HEAD -- measured and named in
# `docs/campaigns/T-family/T23G_PREFLIGHT_FINDINGS.md` §11.
#
# ⚠ THE SOURCE OF THE NEW VALUE, AND THE LEGALITY LIVES HERE RATHER THAN IN THE
# OUTCOME.  RE-READ FROM `T23_P305_U20` -- AN INDEPENDENT PRIOR CASE -- AND NEVER
# FROM `T23G_M`, THE CASE BEING GRADED.  Taking the reference from the case under
# grade would make this gate PASS BY CONSTRUCTION and destroy the determinism
# control it exists to be.  Artifact:
# `verification/runs/T-family/T23_runs/T23_P305_U20/10000/housing/T`,
# internalField, 1120 cells, read by `read_max_T` on 2026-09-01.
#
# NOT GRANTED AND NOT DONE: widening `read_max_T` to include boundary faces
# (REFUSED BY NAME at §27.2, because it contradicts the frozen §4 reader path and
# would move Q1 on all three levels after compute); any change to `REPRO_TOL_K`;
# any change to the rung aggregation at the foot of `grade()`.
REPRO_REF_Q1_K = 342.159828932      # G-REPRO, section 10.  See REPAIR R1 above.
REPRO_TOL_K = 1.0e-6                # UNTOUCHED by REPAIR R1.

# section 5.1 G-CONV.  Ux is EXCLUDED BY DECISION; section 7.3 carries the
# reason and this file prints max|Ux|/max|Uz| beside every exclusion.
ASSERT_RESID = T23.ASSERT_RESID     # ("Uy","Uz","h","p_rgh","k","omega")
EXCLUDED_RESID = T23.EXCLUDED_RESID  # ("Ux",)
RESID_TOL = 1.0e-6

# section 5.1 G-PLATEAU.
PLATEAU_FROM_ITER = 9000            # last 11 samples at writeInterval 100
PLATEAU_MAX_SPREAD_K = 0.010        # one tenth of the 0.1 degC display quantum

# section 4.3, the shift-invariance assertion.  RELATIVE, with an absolute
# floor of 1, and here is why it is not a bare absolute tolerance: driving this
# instrument on a synthetic first-order triple (p = 1, r = 2, GCI_abs = 0.84 K)
# measured the T-versus-dT disagreement at 9.8e-14 -- floating-point
# cancellation, not a defect.  A bare 1e-12 absolute bound has only 10x margin
# there and would SPURIOUSLY REFUSE a triple whose GCI_abs happened to be tens
# of kelvin.  A genuine failure of shift-invariance -- a sign error, a changed
# state -- is O(1), not O(1e-13), so a relative bound catches every failure this
# assertion exists to catch and no float noise.
SHIFT_INVARIANCE_RTOL = 1.0e-9


def shift_invariant(a, b):
    return abs(a - b) <= SHIFT_INVARIANCE_RTOL * max(1.0, abs(a), abs(b))

# section 7.4: y+ is MEASURED and REPORTED, NEVER GATED.  This is the DISCLOSURE
# threshold only -- crossing it prints a disclosure beside the order and does
# not change any verdict.
YPLUS_DISCLOSE_ABOVE = 5.0

IFACE_PATCH = T23.IFACE_PATCH       # "housing_to_fluid"
REGIONS = ("fluid", "housing", "core")

# section 2.2, the invariants byte-compared across levels.
INVARIANT_DIRS = (("0.orig",), ("constant",))
INVARIANT_FILES = (
    ("system", "fvSchemes"),
    ("system", "fluid", "fvSchemes"),
    ("system", "housing", "fvSchemes"),
    ("system", "core", "fvSchemes"),
    ("system", "fluid", "fvSolution"),
    ("system", "housing", "fvSolution"),
    ("system", "core", "fvSolution"),
    ("system", "controlDict"),
)
INVARIANT_SKIP_DIRS = ("polyMesh",)   # the meshes are SUPPOSED to differ

# AMENDMENT v1.1, 2026-09-01 (T23G_PREREGISTRATION.md amendment A1).  ONE FILE,
# EXEMPTED BY NAME.  `constant/cellToRegion` is a DERIVED ARTEFACT OF THE MESH,
# deposited by `splitMeshRegions -cellZones -overwrite` (build_t23.py:804),
# carrying ONE LABEL PER CELL.  It differs across the ladder BECAUSE h DIFFERS --
# it is evidence that the ladder IS a ladder, not evidence that the case changed.
# Byte-comparing it asks the three levels to have the SAME CELL COUNT, which
# contradicts the ladder's entire purpose, so the comparison could never pass and
# was a GUARANTEED REFUSAL rather than a check.
#
# NOTHING IS LOST, AND THAT IS THE LOAD-BEARING POINT -- MEASURED, NOT ASSERTED:
# the file's whole aggregate content is three labels {0,1,2} with counts
# {35200, 3360, 1120} on T23_P305_U20, which are EXACTLY the per-region cell
# counts `check_ladder_structure` re-reads from each level's own checkMesh logs
# and matches against the FROZEN EXPECTED_CELLS, with every region's ratio
# required to be exactly 4.  That check is STRICTER than this one: it compares
# against a value frozen in the registration, not merely against a sibling level.
#
# EXEMPTED BY NAME, DELIBERATELY.  Not a pattern, not a widened SKIP_DIRS, and
# not a "files that differ" escape -- a named exemption stays auditable, a
# general one silently swallows the next surprise.
INVARIANT_SKIP_FILES = ("cellToRegion",)

EXIT_OK, EXIT_NOTCLEAN, EXIT_REFUSE = 0, 1, 2

CEILING = (
    "A grid triple is CODE-AND-GRID CONVERGENCE evidence.  It is NOT a "
    "validation against a physical experiment.\n"
    "  It can move the G column of the tiering directive and it CANNOT move "
    "the P column: there is no primary\n"
    "  experimental source for this geometry "
    "(T23_PREREGISTRATION.md:503-513).  A perfectly converged grid ladder on\n"
    "  a wrong model converges perfectly to the wrong answer, and this rung "
    "has no instrument that could tell.\n"
    "  A PASS means: the answer is no longer changing appreciably with mesh "
    "density AT THIS OPERATING POINT.\n"
    "  It does NOT mean the answer is right, and NOTHING here transfers to "
    "any other point of the T23 map."
)


def refuse(msg):
    print("\nREFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------------------------------------------------------------------------
# READERS.  Every one of these is exercised by a planted-zero control below,
# on the SAME path, with the SAME parser, on every level.
# --------------------------------------------------------------------------

def field_path(case_dir, region):
    return os.path.join(case_dir, ENDTIME, region, "T")


def read_max_T(case_dir, region):
    """max(T) over a region's internalField.  Q1 at region='housing'
    (section 4, the housing peak Act A shows); Q3 at region='core'
    (Sanaa item (1), the column the 200 degC margin is computed on)."""
    lines, first, n = T23.internal_window(field_path(case_dir, region))
    return max(float(lines[first + i]) for i in range(n))


def read_iface_avg(case_dir, areas):
    """Q2: area-averaged T on the HOUSING SIDE of housing_to_fluid, weighted by
    the REAL face areas of that patch -- never by a face count."""
    lines, first, n = T23.patch_value_window(field_path(case_dir, "housing"),
                                             IFACE_PATCH)
    if len(areas) != n:
        refuse("Q2: %d face areas against %d boundary values in %s"
               % (len(areas), n, case_dir))
    tot = sum(areas)
    if tot <= 0.0:
        refuse("Q2: total face area of %s is %r" % (IFACE_PATCH, tot))
    return sum(float(lines[first + i]) * areas[i] for i in range(n)) / tot


# --------------------------------------------------------------------------
# PLANTERS.  STRUCTURAL: the window comes from the field's OWN header and the
# write is by LINE INDEX.  The number of values planted is recorded and printed.
# --------------------------------------------------------------------------

def plant_max_T(case_dir, region, mag):
    """Plant into the HOTTEST internalField cell, so the expected shift in a
    max() reader is exactly `mag`."""
    p = field_path(case_dir, region)
    lines, first, n = T23.internal_window(p)
    vals = [float(lines[first + i]) for i in range(n)]
    j = max(range(n), key=lambda i: vals[i])
    lines[first + j] = "%.12g" % (vals[j] + mag)      # writePrecision 12
    open(p, "w").write("\n".join(lines))
    return 1


def plant_iface(case_dir, mag):
    """Plant into EVERY face of the target patch, so Q2's expected shift is
    exactly `mag` and NOT mag/N (T23 3.6 clause 7)."""
    p = field_path(case_dir, "housing")
    lines, first, n = T23.patch_value_window(p, IFACE_PATCH)
    for i in range(n):
        lines[first + i] = "%.12g" % (float(lines[first + i]) + mag)
    open(p, "w").write("\n".join(lines))
    return n


# --------------------------------------------------------------------------
# THE PLANTED-ZERO CONTROL -- CLAUDE.md rule 3, T23G section 7.1, all eight
# clauses.  Region-parameterised, because Q3 reads `core` and Q1/Q2 read
# `housing`.  It REFUSES rather than degrades.
# --------------------------------------------------------------------------

def planted_zero_control(case_dir, region, label, reader, planter):
    case_real = os.path.realpath(case_dir)
    scratch = tempfile.mkdtemp(prefix="t23g_ctl_")
    dest = os.path.join(scratch, os.path.basename(case_dir))
    try:
        # 1. COPY FIRST.  NEVER write into the case.
        scratch_real = os.path.realpath(scratch)
        if scratch_real == case_real or scratch_real.startswith(case_real + os.sep):
            refuse("control scratch %s resolves INSIDE the case %s"
                   % (scratch_real, case_real))
        shutil.copytree(case_dir, dest, symlinks=True,
                        ignore=shutil.ignore_patterns("log.solve", "*.py"))
        if os.path.realpath(dest).startswith(case_real + os.sep):
            refuse("control copy %s resolves INSIDE the case" % dest)
        target = field_path(dest, region)
        pristine = open(target).read()

        # 2. NEGATIVE ARM.  THRESHOLD EXACTLY ZERO.  No absolute tolerance.
        a = reader(dest)
        b = reader(dest)
        if (b - a) != 0.0:
            refuse("%s NEGATIVE ARM: the reader is NOISY -- two reads of "
                   "identical bytes differ by %r" % (label, b - a))
        base = a

        # 3. POSITIVE ARM.  A MEASURED magnitude ladder.  Exact, epsilon-free.
        rungs, floor, at_plant, n_planted = [], None, None, None
        for mag in LADDER:
            open(target, "w").write(pristine)
            cnt = planter(dest, mag)
            got = reader(dest) - base
            rungs.append((mag, got, cnt))
            if got != 0.0:
                floor = mag if floor is None else min(floor, mag)
            if mag == PLANT:
                at_plant, n_planted = got, cnt
        open(target, "w").write(pristine)

        # 4. REFUSE IF THE READER IS BLIND.
        if floor is None:
            refuse("%s POSITIVE ARM: the reader is BLIND -- no magnitude in "
                   "the ladder produced a non-zero read.  Its zeros mean "
                   "nothing (CLAUDE.md rule 3)" % label)
        # 5. THE ONLY SIZING PREDICATE IS RELATIVE.
        if at_plant is None:
            refuse("%s: PLANT was not exercised by the ladder" % label)
        if not (at_plant >= PLANT * (1.0 - 1e-9)):
            refuse("%s: read at PLANT is %.6e, below PLANT*(1-1e-9) = %.6e"
                   % (label, at_plant, PLANT * (1.0 - 1e-9)))
        if at_plant < 0.1 * PLANT:
            refuse("%s: read at PLANT is %.6e, below 0.1 x PLANT"
                   % (label, at_plant))

        # 8. The case was never written to -- VERIFIED, not assumed.
        if open(field_path(case_dir, region)).read() != open(target).read():
            refuse("%s: the case file and the restored copy differ -- the "
                   "control may have written into the case" % label)

        # Handed to roache_triple as an EXTERNAL control: this comparator's own
        # raw artifact, its own parser, its own before/after.
        pc = RT.external_plant_control(label, base, base + at_plant,
                                       artifact=field_path(case_dir, region),
                                       level=os.path.basename(case_dir))
        pc.update(floor=floor, n_planted=n_planted, rungs=rungs)
        return pc
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# --------------------------------------------------------------------------
# LADDER STRUCTURE -- section 3.3 and section 2.2.  These run BEFORE anything
# is graded, because a ladder that is not a ladder cannot produce a result.
# --------------------------------------------------------------------------

def cells_from_checkmesh(case_dir, region):
    """The cell count from the level's OWN checkMesh log.  MEASURED, never
    recited from EXPECTED_CELLS -- which is then checked against it."""
    p = os.path.join(case_dir, "log.checkMesh.%s" % region)
    if not os.path.isfile(p):
        refuse("no %s -- the cell count cannot be measured and this ladder's "
               "refinement ratio cannot be derived" % p)
    m = re.findall(r"^\s*cells:\s+(\d+)\s*$", open(p, errors="replace").read(),
                   re.M)
    if len(m) != 1:
        refuse("%s carries %d `cells:` lines; exactly one is expected" % (p, len(m)))
    return int(m[0])


def check_ladder_structure(dirs):
    """REFUSAL 3: every region refines by EXACTLY 4 at every step, so r = 2 at
    dim = 2 in every region and the total-cell input to roache_triple is
    legitimate (section 3.3).  Returns {level: {region: cells, 'total': n}}."""
    print("LADDER STRUCTURE -- cell counts MEASURED from each level's own "
          "checkMesh logs\n")
    counts = {}
    for lvl in LEVELS:
        per = {r: cells_from_checkmesh(dirs[lvl], r) for r in REGIONS}
        per["total"] = sum(per[r] for r in REGIONS)
        counts[lvl] = per
        for r in REGIONS:
            if per[r] != EXPECTED_CELLS[lvl][r]:
                refuse("%s region %s has %d cells; the frozen registration "
                       "(section 3.1) says %d.  The mesh that ran is NOT the "
                       "mesh that was registered."
                       % (lvl, r, per[r], EXPECTED_CELLS[lvl][r]))
    hdr = "  %-10s %10s %10s %10s %12s" % ("region", LEVELS[0], LEVELS[1],
                                           LEVELS[2], "ratios")
    print(hdr)
    for r in REGIONS + ("total",):
        c, m_, f = (counts[l][r] for l in LEVELS)
        if m_ != c * CELL_RATIO or f != m_ * CELL_RATIO:
            refuse("region %s does not refine by exactly %d: %d -> %d -> %d.  "
                   "A conjugate ladder whose regions refine by different "
                   "factors is not the same interface at three resolutions; "
                   "that is a BUILD FAULT, not a result (section 3.3)."
                   % (r, CELL_RATIO, c, m_, f))
        print("  %-10s %10d %10d %10d   x%d, x%d  -> r = %.6f, %.6f"
              % (r, c, m_, f, m_ // c, f // m_,
                 RT.refinement_ratio(c, m_, DIM),
                 RT.refinement_ratio(m_, f, DIM)))
    r21 = RT.refinement_ratio(counts[LEVELS[0]]["total"],
                              counts[LEVELS[1]]["total"], DIM)
    r32 = RT.refinement_ratio(counts[LEVELS[1]]["total"],
                              counts[LEVELS[2]]["total"], DIM)
    print("\n  dim = %d, BECAUSE THE CASE IS A 5 deg WEDGE ONE CELL THICK "
          "CIRCUMFERENTIALLY: every block division is (nr nz 1) and the third\n"
          "  stays 1, so refinement happens in TWO directions.  h = (1/N)^(1/2), "
          "a 4x cell count is r = 2 -- NOT an 8x one." % DIM)
    print("  r21 = %.6f   r32 = %.6f   [DERIVED from the measured cell counts "
          "above, at dim = %d]\n" % (r21, r32, DIM))
    return counts


def _tree_files(root, rel=""):
    out = []
    base = os.path.join(root, rel) if rel else root
    for name in sorted(os.listdir(base)):
        if name in INVARIANT_SKIP_DIRS:
            continue
        p = os.path.join(base, name)
        r = os.path.join(rel, name) if rel else name
        if os.path.isdir(p):
            out.extend(_tree_files(root, r))
            continue
        if name in INVARIANT_SKIP_FILES:      # amendment A1, exempted BY NAME
            continue
        out.append(r)
    return out


def check_invariants(dirs):
    """REFUSAL 4: the levels must differ in h and in NOTHING ELSE.  Byte
    comparison, section 2.2.  Mesh identity does NOT apply to a grid ladder --
    the meshes are supposed to differ -- so what is asserted is everything that
    is not the mesh."""
    print("LEVEL INVARIANTS -- byte-compared across all three levels "
          "(section 2.2)\n")
    print("  EXEMPTED BY NAME (amendment A1, 2026-09-01): %s.  `cellToRegion` "
          "is a DERIVED ARTEFACT of the mesh with one\n"
          "  label per cell; it differs across the ladder BECAUSE h differs.  "
          "Its whole aggregate content -- the per-region cell\n"
          "  counts -- is checked ABOVE by check_ladder_structure against the "
          "FROZEN EXPECTED_CELLS, which is STRICTER than a\n"
          "  sibling-level byte comparison.  This exemption removes a check "
          "that was UNSATISFIABLE and REDUNDANT, and it is\n"
          "  printed here rather than left silent.\n"
          % ", ".join(INVARIANT_SKIP_FILES))
    ref = dirs[LEVELS[0]]
    checked = 0
    for parts in INVARIANT_DIRS:
        sub = os.path.join(*parts)
        names = _tree_files(os.path.join(ref, sub))
        for lvl in LEVELS[1:]:
            other = _tree_files(os.path.join(dirs[lvl], sub))
            if names != other:
                refuse("%s/ holds a different FILE SET in %s than in %s: %r vs %r"
                       % (sub, lvl, LEVELS[0],
                          sorted(set(names) ^ set(other)), sub))
            for nm in names:
                a, b = (os.path.join(ref, sub, nm),
                        os.path.join(dirs[lvl], sub, nm))
                if not filecmp.cmp(a, b, shallow=False):
                    refuse("%s/%s DIFFERS between %s and %s.  The levels must "
                           "differ in h and in nothing else (section 2.2)."
                           % (sub, nm, LEVELS[0], lvl))
                checked += 1
        print("  %-12s %3d files identical across all three levels"
              % (sub + "/", len(names)))
    for parts in INVARIANT_FILES:
        rel = os.path.join(*parts)
        for lvl in LEVELS[1:]:
            a, b = os.path.join(ref, rel), os.path.join(dirs[lvl], rel)
            if not os.path.isfile(a) or not os.path.isfile(b):
                refuse("%s is missing from %s or %s" % (rel, LEVELS[0], lvl))
            if not filecmp.cmp(a, b, shallow=False):
                refuse("%s DIFFERS between %s and %s (section 2.2)"
                       % (rel, LEVELS[0], lvl))
            checked += 1
    print("  %-12s %3d files identical across all three levels"
          % ("system/", len(INVARIANT_FILES)))

    # The geometry itself: the vertices block, which must NOT move when the
    # block divisions do.  The eight integers live in the `blocks` block only.
    verts = {}
    for lvl in LEVELS:
        txt = open(os.path.join(dirs[lvl], "system", "blockMeshDict"),
                   errors="replace").read()
        m = re.search(r"^vertices\s*\n\((.*?)^\);", txt, re.M | re.S)
        if not m:
            refuse("%s/system/blockMeshDict has no parsable `vertices` block"
                   % lvl)
        verts[lvl] = m.group(1)
    if len({v for v in verts.values()}) != 1:
        refuse("the `vertices` block of blockMeshDict DIFFERS between levels -- "
               "the GEOMETRY moved when only the divisions should have "
               "(section 2.2)")
    print("  %-12s vertices block byte-identical across all three levels "
          "-- the geometry did not move\n" % "blockMeshDict")
    return checked + 3


# --------------------------------------------------------------------------
# G-CONV and G-PLATEAU -- rule 5 step (1), evaluated BEFORE any grid claim.
# --------------------------------------------------------------------------

def iterative_state(case_dir):
    """G-CONV, section 5.1.  Ux is EXCLUDED BY DECISION and the exclusion is
    never bare: max|Ux|/max|Uz| is MEASURED and printed beside it."""
    res = T23.final_residuals(case_dir)
    missing = [k for k in ASSERT_RESID if k not in res]
    if missing:
        refuse("%s: log.solve's last `Time = %s` block carries no residual for "
               "%s; G-CONV cannot be evaluated and an unevaluated gate is not "
               "a passed one" % (case_dir, ENDTIME, ",".join(missing)))
    bad = {k: res[k] for k in ASSERT_RESID if res[k] > RESID_TOL}
    mx = T23.u_component_maxima(case_dir)
    ratio = (mx[0] / mx[2]) if mx[2] > 0.0 else float("inf")
    return ("CONVERGED" if not bad else "NOT CONVERGED"), res, bad, mx, ratio


def plateau_series(case_dir, region):
    """The fieldMinMax series a `<region>_T` function object writes every 100
    iterations.  Returns [(iteration, max_T)] or None if there is no series --
    and None is reported as NOT MEASURED, never as a pass (section 7.5)."""
    p = os.path.join(case_dir, "postProcessing", region, "%s_T" % region,
                     "0", "fieldMinMax.dat")
    if not os.path.isfile(p):
        return None
    out = []
    for line in open(p, errors="replace"):
        if line.startswith("#"):
            continue
        f = [c.strip() for c in line.split("\t") if c.strip()]
        if len(f) < 5 or f[1] != "T":
            continue
        out.append((float(f[0]), float(f[4])))
    return out or None


def plateau_state(case_dir, region):
    """G-PLATEAU, section 5.1: the peak-to-peak spread of the last 11 samples
    must be <= 0.010 K -- one tenth of the 0.1 degC display quantum."""
    ser = plateau_series(case_dir, region)
    if ser is None:
        return "NOT MEASURED", None, None
    tail = [v for (it, v) in ser if it >= PLATEAU_FROM_ITER]
    if len(tail) < 3:
        refuse("%s/%s: only %d fieldMinMax samples at or after iteration %d; "
               "G-PLATEAU needs at least 3 and an unevaluated gate is not a "
               "passed one" % (case_dir, region, len(tail), PLATEAU_FROM_ITER))
    spread = max(tail) - min(tail)
    state = "PLATEAUED" if spread <= PLATEAU_MAX_SPREAD_K else "NOT PLATEAUED"
    return state, spread, len(tail)


def read_yplus(case_dir):
    """Section 7.4: MEASURED and REPORTED, NEVER GATED.  A log whose own text
    says the tool could not compute y+ returns BLIND, and its perfect zeros are
    REFUSED rather than read -- a live false zero this family already caught
    (analyse_t23.py:436-447)."""
    return T23.read_yplus(case_dir)


# --------------------------------------------------------------------------
# COMPLETION -- rule 4, DELEGATED and CALLED (section 7.2).
# --------------------------------------------------------------------------

def require_done(dirs):
    """`mark_done_t23.py --root <T23G_runs> <levels>`, called as a subprocess.
    No completion logic lives in this file.  A DONE marker older than the case's
    own <endTime> fields is RE-VERIFIED from raw artefacts, not trusted."""
    md = os.path.join(T23_RUNS, "mark_done_t23.py")
    if not os.path.isfile(md):
        refuse("the completion instrument %s is not on disk; rule 4 cannot be "
               "evaluated and this file will not reimplement it" % md)
    print("COMPLETION -- rule 4, DELEGATED to %s and CALLED, never "
          "reimplemented\n" % os.path.relpath(md, REPO))
    r = subprocess.run([sys.executable, md, "--root", HERE] + list(LEVELS),
                       capture_output=True, text=True)
    for line in (r.stdout or "").rstrip().split("\n"):
        if line.strip():
            print("  | " + line)
    if r.returncode != 0:
        refuse("mark_done_t23.py returned %d -- at least one level is NOT DONE "
               "on rule 4's six clauses.  A run that fails any clause is not "
               "done, and an incomplete level is not graded." % r.returncode)
    # THE STALE-MARKER RE-CHECK.  A marker is not evidence if it predates the
    # fields it claims to have checked.
    for lvl in LEVELS:
        mk = os.path.join(HERE, "DONE.%s" % lvl)
        if not os.path.isfile(mk):
            refuse("mark_done_t23.py reported success but %s does not exist" % mk)
        mt = os.path.getmtime(mk)
        for region in REGIONS:
            f = field_path(dirs[lvl], region)
            if os.path.getmtime(f) > mt:
                refuse("DONE.%s is STALE: %s is NEWER than the marker.  The "
                       "marker was written against different bytes and is "
                       "re-verified rather than trusted (section 7.2)."
                       % (lvl, os.path.relpath(f, HERE)))
    print("\n  all %d levels DONE on all six clauses of rule 4, and no marker "
          "is stale\n" % len(LEVELS))


# --------------------------------------------------------------------------
# GRADING
# --------------------------------------------------------------------------

def _levels_arg(names, cells, values, shift):
    return [dict(name=n, cells=cells[n]["total"], value=values[n] - shift)
            for n in names]


def grade_quantity(qid, desc, values, cells, plant_controls,
                   it_states, pl_states):
    """rule 5, in its order, via scripts/roache_triple.py.  This function adds
    the three registered gates that sit ON TOP of the module's band verdict --
    G-ORDER, G-GCI-DISPLAY, G-GCI-LEGACY -- and it evaluates them ONLY in the
    CONVERGING branch.  A gate below a NOT A RESULT is printed as NOT EVALUATED,
    never as passed (VERIFICATION_CHARTER.md section 2, the M6 row)."""
    print("=" * 78)
    print("[%s]  %s" % (qid, desc))
    print("=" * 78)

    for lvl in LEVELS:
        pc = plant_controls[qid][lvl]
        print("  planted-zero control %-9s %s  floor %.0e K  read at PLANT "
              "%.6e K (>= PLANT*(1-1e-9) = %.6e, RELATIVE predicate)  "
              "values planted %d"
              % (lvl, "PASSED" if pc["passed"] else "FAILED", pc["floor"],
                 pc["reader_delta"], PLANT * (1.0 - 1e-9), pc["n_planted"]))
        if not pc["passed"]:
            refuse("%s planted-zero control FAILED on %s" % (qid, lvl))

    # section 4.3: graded on dT, and the shift-invariance ASSERTED, not trusted.
    lv_abs = _levels_arg(LEVELS, cells, values, 0.0)
    lv_dt = _levels_arg(LEVELS, cells, values, T_INF_K)
    t_abs = RT.all_triples(lv_abs, DIM)[-1]
    t_dt = RT.all_triples(lv_dt, DIM)[-1]
    if t_abs["state"] != t_dt["state"]:
        refuse("%s: the dT shift changed the triple STATE, %s -> %s.  Section "
               "4.3 registers that it cannot, and an assertion that fires is a "
               "finding, not a rounding" % (qid, t_abs["state"], t_dt["state"]))
    for key in ("order", "GCI_abs"):
        a, b = t_abs.get(key), t_dt.get(key)
        if (a is None) != (b is None):
            refuse("%s: the dT shift changed whether %s exists" % (qid, key))
        if a is not None and not shift_invariant(a, b):
            refuse("%s: the dT shift moved %s by %.3e, above the registered "
                   "relative tolerance %.0e.  Section 4.3 registers that a "
                   "constant shift cancels in every difference; this did not, "
                   "and an assertion that fires is a finding, not a rounding."
                   % (qid, key, abs(a - b), SHIFT_INVARIANCE_RTOL))
    print("\n  dT shift-invariance ASSERTED, not trusted (section 4.3): state, "
          "observed order and GCI_abs identical on T and on dT = T - %.1f K to "
          "%.0e relative.\n"
          "  ONLY GCI_pct moves, which is the whole point.  MEASURED on a "
          "synthetic first-order triple while this instrument was written: the "
          "same\n  ladder reads GCI_pct = 1.5771 %% on dT and 0.2471 %% on "
          "absolute T -- a factor of 6.4.  Grading the percentage on absolute "
          "kelvin\n  would have made the 2 %% legacy bar trivially passable, "
          "which is exactly the flattery-by-construction section 4.3 forbids."
          % (T_INF_K, SHIFT_INVARIANCE_RTOL))

    row = RT.grade_ladder(
        qid, lv_dt, DIM, BAND_DT_K, plant_controls[qid][LEVELS[-1]],
        iterative_states=it_states, plateau_states=pl_states)

    print("\n" + RT.format_row(row))

    extras, worst = {}, row["verdict"]
    if row["verdict"] == "NOT A RESULT":
        for g in ("G-ORDER", "G-GCI-DISPLAY", "G-GCI-LEGACY"):
            extras[g] = dict(verdict="NOT EVALUATED", value=None)
        print("\n  G-ORDER / G-GCI-DISPLAY / G-GCI-LEGACY: NOT EVALUATED.\n"
              "  Rule 5 step (1) or (2) fired first, and a gate that was not "
              "reached is stated as NOT REACHED -- never replaced by a nearer\n"
              "  gate that was (VERIFICATION_CHARTER.md section 2, the M6 row).")
    else:
        p = row["order"]
        ok = ORDER_BAND[0] <= p <= ORDER_BAND[1]
        extras["G-ORDER"] = dict(verdict="PASS" if ok else "GATE FAIL", value=p,
                                 band=list(ORDER_BAND))
        print("\n  G-ORDER        p = %.4f  band [%.2f, %.2f]        -> %s"
              % (p, ORDER_BAND[0], ORDER_BAND[1], extras["G-ORDER"]["verdict"]))
        print("                 REGISTERED PREDICTION (section 6.2): p ~ 1.0, "
              "because div(phi,h) = `bounded Gauss upwind` is FIRST ORDER\n"
              "                 and is rate-limiting.  A measured p > 1.5 "
              "FALSIFIES that reading and is a finding about the\n"
              "                 discretisation, reported as one.  This band is "
              "NOT T23_PREREGISTRATION.md:518's [1.3, 2.5]; the\n"
              "                 departure was declared in the frozen document "
              "before any level ran (section 6.2).")

        g_abs, g_pct = row["GCI_abs"], row["GCI_pct"]
        ok = g_abs <= GCI_DISPLAY_MAX_K
        extras["G-GCI-DISPLAY"] = dict(verdict="PASS" if ok else "GATE FAIL",
                                       value=g_abs, threshold=GCI_DISPLAY_MAX_K)
        print("\n  G-GCI-DISPLAY  GCI_abs = %.6g K  <= %.3f K            -> %s"
              % (g_abs, GCI_DISPLAY_MAX_K, extras["G-GCI-DISPLAY"]["verdict"]))
        print("                 THIS IS THE GATE THAT ANSWERS SANAA'S "
              "QUESTION.  %.3f K is half the 0.1 degC display quantum.\n"
              "                 %s"
              % (GCI_DISPLAY_MAX_K,
                 "Act A MAY print 0.1 degC significant figures for this "
                 "quantity." if ok else
                 "Act A MAY NOT print 0.1 degC significant figures for this "
                 "quantity; the honest display is 1 degC."))

        ok = g_pct < GCI_LEGACY_MAX_PCT
        extras["G-GCI-LEGACY"] = dict(verdict="PASS" if ok else "GATE FAIL",
                                      value=g_pct, threshold=GCI_LEGACY_MAX_PCT)
        print("\n  G-GCI-LEGACY   GCI_pct(dT) = %.4f %%  < %.1f %%          -> %s"
              % (g_pct, GCI_LEGACY_MAX_PCT, extras["G-GCI-LEGACY"]["verdict"]))
        print("                 T23_PREREGISTRATION.md:518's own bar, carried "
              "forward so it is not silently dropped.\n"
              "                 ON A ~54 K RISE 2 %% IS ~1.1 K.  PASSING THIS "
              "IS NOT PASSING G-GCI-DISPLAY AND MAY NEVER BE\n"
              "                 REPORTED AS LICENSING 0.1 degC (section 5.2).  "
              "The two bars are 22x apart.")

        print("\n  Richardson extrapolate, DISPLAY ONLY, NEVER GRADED "
              "(section 5.3): %.8g  [parent-convention form %.8g, sign-flipped,"
              "\n                 see scripts/roache_triple.py docstring lines "
              "26-74].  THE FINE VALUE IS WHAT WAS GRADED."
              % (row["richardson"], row["richardson_parent_convention"]))

        for g in ("G-ORDER", "G-GCI-DISPLAY", "G-GCI-LEGACY"):
            if extras[g]["verdict"] == "GATE FAIL" and worst == "PASS":
                worst = "GATE FAIL"

    row["extra_gates"] = extras
    row["quantity_verdict"] = worst
    print("\n  %-14s -> %s\n" % (qid + " VERDICT", worst))
    return row


def _level_dirs(root):
    dirs = {}
    for lvl in LEVELS:
        d = os.path.join(root, lvl)
        if not os.path.isdir(d):
            refuse("level directory %s does not exist" % d)
        dirs[lvl] = d
    return dirs


def pre_solve_check(root):
    """AMENDMENT v1.1, 2026-09-01 (T23G_PREREGISTRATION.md amendment A2) --
    A CHANGE TO THE ORDER OF OPERATIONS, AND TO NO GATE, THRESHOLD, CAP OR LABEL.

    THE DEFECT THIS EXISTS TO PREVENT WAS NEVER THE EXEMPTION -- IT WAS THE
    ORDERING.  `check_ladder_structure` and `check_invariants` are BUILD-TIME
    faults detected at GRADE time, i.e. after all three levels have solved and
    been marked DONE.  On this rung that is 158.65 core-min of solving bought to
    learn that a mesh was wrong, when the same answer was available for SECONDS
    of meshing.

    So the two checks are made callable ONCE THE THREE MESHES EXIST AND BEFORE
    ANY SOLVER STARTS.  Run as:

        analyse_t23g.py --pre-solve [--root <dir>]

    THEY REMAIN AT GRADE TIME AS WELL, UNCHANGED.  Belt and braces: a grading
    pass must refuse on its OWN authority and must never trust that a build-time
    check was run.  This function GRADES NOTHING, reads no field, evaluates no
    gate, and requires no level to be DONE -- a mesh has no solve to complete."""
    dirs = _level_dirs(root)
    print("=" * 78)
    print("T23G -- PRE-SOLVE STRUCTURAL CHECK (amendment A2).  GRADES NOTHING.")
    print("=" * 78)
    print("This runs AFTER the three meshes are built and BEFORE any solver "
          "starts, so that a build\nfault costs SECONDS OF MESHING rather than "
          "%.2f core-min of solving.  It evaluates no gate,\nreads no field, and "
          "does not require any level to be DONE.\n" % 158.65)
    cells = check_ladder_structure(dirs)
    n_inv = check_invariants(dirs)
    print("PRE-SOLVE CHECK PASSED: the ladder is uniform in every region and "
          "the levels differ in h and\nin nothing else.  %d invariant "
          "comparisons.  THIS IS NOT A VERDICT ON ANY QUANTITY -- no field has\n"
          "been read and no gate has been evaluated.  The same two checks run "
          "AGAIN at grade time, on\nthe grader's own authority.\n" % n_inv)
    return dict(cells=cells, invariants_checked=n_inv,
                skipped_by_name=list(INVARIANT_SKIP_FILES)), EXIT_OK


def grade(root):
    dirs = _level_dirs(root)

    print("=" * 78)
    print("T23G -- THE GRID TRIPLE AT (305 W, 20 m/s)")
    print("=" * 78)
    print("Frozen registration: docs/campaigns/T-family/T23G_PREREGISTRATION.md")
    print("Rule 5 machinery:    scripts/roache_triple.py, CALLED, never "
          "reimplemented.  Fs = %.2f, dim = %d." % (RT.FS, DIM))
    print("PLANT = %.6e K, IMPORTED from scripts/roache_triple.py, never "
          "redefined here.\n" % PLANT)
    print("HONEST CEILING, printed before any number:\n  " + CEILING + "\n")

    require_done(dirs)
    cells = check_ladder_structure(dirs)
    n_inv = check_invariants(dirs)

    # ---- rule 5 step (1): iterative convergence and plateau, per level ------
    print("PER-LEVEL CONVERGENCE (G-CONV) AND STATIONARITY (G-PLATEAU) -- "
          "rule 5 step (1), BEFORE any grid claim\n")
    it_states, pl_housing, pl_core, yplus = {}, {}, {}, {}
    for lvl in LEVELS:
        st, res, bad, mx, ratio = iterative_state(dirs[lvl])
        it_states[lvl] = st
        print("  %-9s G-CONV %-14s  %s" % (
            lvl, st, "  ".join("%s %.3e" % (k, res[k]) for k in ASSERT_RESID)))
        print("            Ux EXCLUDED BY DECISION (section 7.3): x is the "
              "wedge-normal direction, Ux ~ 0 everywhere, so its residual is a "
              "0/0\n            normalisation carrying no information.  "
              "MEASURED justification, never asserted bare: "
              "max|Ux| = %.4e, max|Uz| = %.4e, ratio %.3e"
              % (mx[0], mx[2], ratio))
        if bad:
            print("            ABOVE %.0e: %s" % (RESID_TOL, bad))
        for region, store in (("housing", pl_housing), ("core", pl_core)):
            s, spread, n = plateau_state(dirs[lvl], region)
            store[lvl] = s
            print("            G-PLATEAU %-7s %-13s %s"
                  % (region, s,
                     "spread %.6f K over the last %d samples (iterations "
                     ">= %d), threshold %.3f K"
                     % (spread, n, PLATEAU_FROM_ITER, PLATEAU_MAX_SPREAD_K)
                     if spread is not None else
                     "no fieldMinMax series on disk -- REPORTED AS ABSENT, "
                     "NEVER AS A PASS"))
        yp = read_yplus(dirs[lvl])
        yplus[lvl] = yp
        if yp == "BLIND":
            print("            y+ : the log's own text says the tool could not "
                  "compute it.  ITS ZEROS ARE REFUSED, NOT READ "
                  "(CLAUDE.md rule 3).")
        elif yp:
            hot = max(yp.items(), key=lambda kv: kv[1]["max"])
            print("            y+ MEASURED AND REPORTED, NEVER GATED "
                  "(section 7.4): %s" % "  ".join(
                      "%s max %.4f" % (k, v["max"]) for k, v in sorted(yp.items())))
            if hot[1]["max"] > YPLUS_DISCLOSE_ABOVE:
                print("            *** DISCLOSURE (section 7.4): y+ max %.4f "
                      "on %s EXCEEDS %.1f, so this level has crossed out of "
                      "the viscous\n            *** sublayer and the three "
                      "levels do NOT share one wall treatment.  The measured "
                      "order is partly a wall-model\n            *** artefact. "
                      "THIS DOES NOT BY ITSELF VOID THE TRIPLE, and it is "
                      "stated beside the order rather than used to\n"
                      "            *** excuse a bad one or quietly void a good "
                      "one." % (hot[1]["max"], hot[0], YPLUS_DISCLOSE_ABOVE))
        else:
            print("            y+ : no log.yPlus.fluid on disk -- REPORTED AS "
                  "ABSENT, never as a pass.")
        print()

    # ---- readers, controls, values ------------------------------------------
    print("READERS AND THE NINE PLANTED-ZERO CONTROLS -- CLAUDE.md rule 3\n")
    values = {"Q1": {}, "Q2": {}, "Q3": {}}
    controls = {"Q1": {}, "Q2": {}, "Q3": {}}
    for lvl in LEVELS:
        d = dirs[lvl]
        areas = T23.patch_face_areas(d, "housing", IFACE_PATCH)
        r1 = lambda p: read_max_T(p, "housing")
        r2 = lambda p, a=areas: read_iface_avg(p, a)
        r3 = lambda p: read_max_T(p, "core")
        p1 = lambda p, m: plant_max_T(p, "housing", m)
        p2 = plant_iface
        p3 = lambda p, m: plant_max_T(p, "core", m)
        controls["Q1"][lvl] = planted_zero_control(
            d, "housing", "Q1 max(T) housing internalField @%s" % lvl, r1, p1)
        controls["Q2"][lvl] = planted_zero_control(
            d, "housing", "Q2 areaAvg(T) %s boundaryField @%s"
            % (IFACE_PATCH, lvl), r2, p2)
        controls["Q3"][lvl] = planted_zero_control(
            d, "core", "Q3 max(T) core internalField @%s" % lvl, r3, p3)
        values["Q1"][lvl], values["Q2"][lvl], values["Q3"][lvl] = \
            r1(d), r2(d), r3(d)
        print("  %-9s Q1 %.9f K = %.4f degC   Q2 %.9f K = %.4f degC   "
              "Q3 %.9f K = %.4f degC"
              % (lvl, values["Q1"][lvl], values["Q1"][lvl] - KELVIN_C,
                 values["Q2"][lvl], values["Q2"][lvl] - KELVIN_C,
                 values["Q3"][lvl], values["Q3"][lvl] - KELVIN_C))

    # ---- G-REPRO -------------------------------------------------------------
    d_repro = abs(values["Q1"]["T23G_M"] - REPRO_REF_Q1_K)
    repro = "PASS" if d_repro <= REPRO_TOL_K else "GATE FAIL"
    print("\n  G-REPRO        |Q1(T23G_M) - %.10f K| = %.3e K  <= %.0e K  -> %s"
          % (REPRO_REF_Q1_K, d_repro, REPRO_TOL_K, repro))
    print("                 The MEDIUM level is the same mesh as the already-"
          "solved T23_P305_U20, and section 10 DISCLOSES that its answer\n"
          "                 was on disk and had been read before this document "
          "was frozen.  This is the determinism control that\n"
          "                 disclosure buys: a build differing in mesh, "
          "boundary condition or source term would NOT reproduce it to 1e-6 K,\n"
          "                 so it is a control and not an identity "
          "(VERIFICATION_CHARTER.md section 2a).\n")

    # ---- the three ladders ---------------------------------------------------
    rows = {}
    rows["Q1"] = grade_quantity(
        "Q1", "max(T) over the `housing` region -- the housing peak column",
        values["Q1"], cells, controls, it_states, pl_housing)
    print("  Q2 G-PLATEAU: NOT MEASURED.  There is no fieldMinMax series for a "
          "patch area-average, and no function object was added to\n"
          "  create one -- T23_PREREGISTRATION.md:534-543 registers that an "
          "inline function object that fails does so at CONSTRUCTION and\n"
          "  takes the whole solve with it.  A REGISTERED INSTRUMENT GAP "
          "(section 7.5), reported as ABSENT, never as a pass.\n")
    rows["Q2"] = grade_quantity(
        "Q2", "area-averaged T on the housing side of `%s`" % IFACE_PATCH,
        values["Q2"], cells, controls, it_states, None)
    rows["Q3"] = grade_quantity(
        "Q3", "max(T) over the `core` region -- Sanaa item (1), the column the "
        "200 degC margin is computed on", values["Q3"], cells, controls,
        it_states, pl_core)

    # ---- the rung verdict ----------------------------------------------------
    order = {"NOT A RESULT": 0, "GATE FAIL": 1, "PASS": 2}
    verdicts = [rows[q]["quantity_verdict"] for q in ("Q1", "Q2", "Q3")]
    verdicts.append(repro)
    rung = min(verdicts, key=lambda v: order.get(v, 0))

    print("=" * 78)
    print("T23G RUNG VERDICT: %s" % rung)
    print("=" * 78)
    print("  Q1 %s   Q2 %s   Q3 %s   G-REPRO %s"
          % (rows["Q1"]["quantity_verdict"], rows["Q2"]["quantity_verdict"],
             rows["Q3"]["quantity_verdict"], repro))
    print("  The rung verdict is the WORST of them (section 4.2).  No quantity "
          "here is a reported diagnostic: a printed discrepancy\n"
          "  labelled non-binding is worse than one never computed, so Act A "
          "does not get to keep two thirds of a grid convergence claim.\n")
    print("  " + CEILING)
    print("\n  TIER (THERMAL_TIERING_DIRECTIVE.md): this rung can move the G "
          "column for (305 W, 20 m/s) ONLY, and only on a CONVERGING\n"
          "  triple with every level plateaued.  It CANNOT move the P column.  "
          "Verdict and tier are two vocabularies and are never conflated.\n")

    shas = grading_path_shas()
    print("  GRADING PATH, sha of each file as it exists on disk right now "
          "(section 11):")
    for rel, sha in shas:
        print("    %-58s %s" % (rel, sha))
    print("  These are recorded so a divergence from the committed blobs is "
          "VISIBLE rather than silent.  The third entry is a\n"
          "  DECLARED COUPLING: this comparator imports a sibling rung's "
          "parser so that Q1 and Q2 are read through the same path\n"
          "  Act A's numbers already come from.\n"
          "  THE FOURTH ENTRY IS THE COMPLETION DELEGATE (REPAIR R2, "
          "DEAD_LEVER_AUDIT §27.4): section 7.2 delegates rule 4 to\n"
          "  mark_done_t23.py and evaluates it nowhere else, so it is on this "
          "grading path and is recorded here rather than\n"
          "  left as the one path member whose edits were silent.\n")

    return dict(rung_verdict=rung, quantities=rows, repro=dict(
        verdict=repro, delta_K=d_repro, reference_K=REPRO_REF_Q1_K,
        tolerance_K=REPRO_TOL_K), cells=cells, invariants_checked=n_inv,
        iterative=it_states, plateau=dict(housing=pl_housing, core=pl_core,
                                          Q2="NOT MEASURED"),
        grading_path=dict(shas)), (EXIT_OK if rung == "PASS" else EXIT_NOTCLEAN)


def grading_path_shas():
    out = []
    # REPAIR R2, 2026-09-01.  §2d.1 exception GRANTED at DEAD_LEVER_AUDIT §27.4,
    # and it is MANDATORY rather than optional: it is the condition on which
    # §27.3's D2 grant attaches, and the two land in one commit.
    # `mark_done_t23.py` is on this rung's grading path by §7.2's own delegation
    # -- `require_done` calls it and rule 4 is evaluated nowhere else -- but it
    # was NOT recorded here, so an edit to it left no trace on the artifact's own
    # face.  D2 widens that very file's CASES tuple, so without this the repair
    # would have been invisible in the record that exists to make it visible.
    # Adding a sha recorder is monotonically disclosure-increasing: it writes a
    # hash into the record, reads no field and moves no comparison.
    for rel in ("verification/runs/T-family/T23G_runs/analyse_t23g.py",
                "scripts/roache_triple.py",
                "verification/runs/T-family/T23_runs/analyse_t23.py",
                "verification/runs/T-family/T23_runs/mark_done_t23.py"):
        p = os.path.join(REPO, rel)
        r = subprocess.run(["git", "hash-object", p], cwd=REPO,
                           capture_output=True, text=True)
        out.append((rel, r.stdout.strip() if r.returncode == 0 else "UNAVAILABLE"))
    return out


def main(argv):
    root, jout = HERE, None
    if "--root" in argv:
        i = argv.index("--root")
        root, argv = argv[i + 1], argv[:i] + argv[i + 2:]
    if "--json" in argv:
        i = argv.index("--json")
        jout, argv = argv[i + 1], argv[:i] + argv[i + 2:]
    # amendment A2: the build-time limb.  It grades nothing and it does NOT
    # replace the grade-time limb, which runs the same two checks again.
    if "--pre-solve" in argv:
        out, code = pre_solve_check(root)
        if jout:
            json.dump(out, open(jout, "w"), indent=2, sort_keys=True,
                      default=str)
            print("wrote %s" % jout)
        return code
    out, code = grade(root)
    if jout:
        json.dump(out, open(jout, "w"), indent=2, sort_keys=True, default=str)
        print("wrote %s" % jout)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
