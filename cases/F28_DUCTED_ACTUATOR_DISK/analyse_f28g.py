#!/usr/bin/env python3
"""F28G -- THE MESH-ADMISSION GATE (M1-M6) AND THE GRID-CONVERGENCE COMPARATOR.

Registration, FROZEN:
    verification/campaign/F28G_GRID_CONVERGENCE_PREREGISTRATION.md
    (v1.0 frozen at the commit that introduced it; Addendum 1 appended
    PRE-COMPUTE, condition checked and named there in A1.1.)
Parent, carried unchanged and BY REFERENCE (F28G section 0 and section 7):
    verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md

>>> THIS FILE HAS NOT BEEN RUN FOR RECORD AND NO F28G SOLVE EXISTS.  It is
>>> written LATE -- F28G section 7 registers a selftest against a comparator
>>> that did not exist when the registration froze, and this is that comparator.
>>> Nothing below has produced a graded number, and nothing below may produce
>>> one until `cfd-supervisor` has read this file AS A DIFF
>>> (SUPERVISION_CHARTER section 3, check 1; that check may not be delegated).

-------------------------------------------------------------------------------
WHAT THIS FILE IS
-------------------------------------------------------------------------------
Three entry points, and each REFUSES (exit 2) rather than degrading:

  --selftest                 every control in this file, run against planted
                             data, in BOTH directions.  A filter never shown a
                             real failure is not a detector whatever it returns
                             on good input; one never shown good input is an
                             alarm, not a filter.
  --mesh-gate <spec.json>    F28G section 6: M1-M6, the section 6.2 recorded-
                             and-not-gated quantities, the section 6.3 census
                             rule, and the section 6.4 required report.
                             Verdict per level: PASS or NOT A RESULT.
  --grade <spec.json>        F28G section 7: the Roache triple on `T_total`,
                             under CLAUDE.md rule 5's ordering, with the
                             registered preconditions.

-------------------------------------------------------------------------------
WHAT IT IMPORTS, AND WHY IT DOES NOT RE-IMPLEMENT
-------------------------------------------------------------------------------
`analyse_f28.py` is the parent's INSTALLED grading path (parent Addendum 5).
F28G section 7 carries the parent's numerics, residual and stationarity criteria
"unchanged and by reference", INCLUDING Addendum 3's absolute stationarity
floor.  A second implementation of a frozen criterion is a second thing to keep
right, and it drifts.  So this file CALLS the parent's readers -- the strict
completion rule, the named-file function-object reader with its clause-6 age
guard, the floored stationarity criterion, the sector-frame proof, the planted
controls -- rather than restating them.  Every guard those carry fires here
unchanged and untouched.

-------------------------------------------------------------------------------
THE FIVE THINGS THIS FILE EXISTS TO GET RIGHT
-------------------------------------------------------------------------------
(1) M1 IS READ OFF THE REPORTED MAXIMUM.  `MESH_STANDARD` section 14.4, and
    F28G section 6.1 in its own words: "Any comparator that greps a verdict
    string is reading the wrong instrument and its clean result is not
    evidence."  `checkMesh`'s `Non-orthogonality check OK.` and its closing
    `Mesh OK.` / `Failed N mesh checks.` have been SHOWN unable to discriminate
    -- identical on a 51.3-degree admissible mesh and an 81.6-degree
    inadmissible one, with the failed-check count running BACKWARDS -- and a
    sister lane measured `checkMesh` printing `Mesh OK` at 88.93 degrees.  This
    file never reads them.  `assert_verdict_strings_are_inert` proves that, by
    MUTATING ONLY those lines and requiring the M1/M2/M3 verdicts to come back
    BIT-IDENTICAL.  A promise not to read a string is not a proof; the mutation
    is.
(2) ASPECT RATIO IS RECORDED AND NEVER GATED.  `MESH_STANDARD` section 3.3
    makes it advisory at 1000 and NEVER A LONE REJECTION; section 11.4 states
    that no VALUE of it makes a mesh inadmissible and that what makes a record
    incomplete is the ABSENCE of the number.  So this file carries two controls
    that point in opposite directions: an aspect ratio planted at 1e9 must STILL
    be admitted, and an aspect-ratio line that is ABSENT must make the record
    INCOMPLETE and refuse.  A gate that rejects on aspect ratio alone
    contradicts the standard and has already cost this team a rung.
(3) THE RICHARDSON SIGN (N-T8), AS F28G SECTION 7 CLAUSE 1 REGISTERS IT.  Four
    independently written implementations in this lab carry the same sign
    defect, and it is invisible to BOTH the observed order `p` AND the GCI
    because both are sign-independent.  A key-presence check is registered as
    INSUFFICIENT -- it is what let the defect survive every run of
    `analyse_t1c.py` and `analyse_t3.py`.  The control here is VALUE-checking on
    a synthetic power-law triple with a limit known by construction, asserted to
    1e-12 relative; it asserts the DEFECTIVE form FAILS the same assertion (a
    control that passes for the right and the wrong implementation alike is not
    a control); it asserts `p` and `GCI` are IDENTICAL under both forms, which
    is the measured statement of why nothing neighbouring can catch it; and it
    asserts the free identity `frozen + corrected == 2 * f_fine`.  The shared
    `gci()`'s extrapolate (N-T1) is not used and is not imported.
(4) RULE 5's ORDERING, ONE-WAY.  (1) any level not iteratively converged or not
    plateaued -> NOT A RESULT; (2) triple DIVERGENT / STAGNANT / OSCILLATORY /
    EXACT -> NOT A RESULT with the value, both triples and both orders printed
    beside it; (3) CONVERGING -> PASS inside the band else GATE FAIL, GCI
    printed.  The gate may only turn a PASS or a GATE FAIL INTO NOT A RESULT,
    never the reverse, and `assert_one_way` proves that on every synthetic row
    rather than asserting it in prose.  GCI at Fs = 1.25, and NO GCI IS QUOTED
    WHEN THE THREE VALUES ARE NOT MONOTONE -- enforced by
    `assert_no_gci_without_monotone`, which is a separate guard from the
    classifier so that it can fail for a reason the classifier does not already
    encode.
(5) EVERY ZERO THIS FILE CAN REPORT CARRIES A PLANTED CONTROL (CLAUDE.md rule
    3).  The zeros are: negative cell volumes = 0, severely non-orthogonal faces
    = 0, census exclusions = 0, crash stack frames = 0.  Each is planted into a
    file ON DISK, re-read THROUGH THE SAME READER, and the reader must come back
    with the plant -- or this file refuses.  A zero from a reader not shown able
    to see a non-zero is not evidence.

-------------------------------------------------------------------------------
THE CRASH FILTER, AND WHY IT IS NOT KEYED ON `FOAM FATAL`
-------------------------------------------------------------------------------
MEASURED ON THIS BOX, both limbs, on real artifacts:
  * `verification/runs/FPE_DIAG_runs/HP1/log.simpleFoam` -- a real
    floating-point-exception crash: `FOAM FATAL` occurs **0** times; the
    signal-handler stack frames `#1  Foam::sigFpe::sigHandler(int) ...` are
    present.
  * `verification/runs/F28_runs/FEAS_L1_dp1000_U20_A2/log.simpleFoam` -- a
    healthy F28 run: **0** stack frames.
A filter keyed on `FOAM FATAL` would miss every real crash on this box.  The
frame pattern is the reliable signal and it is what `crash_frames` reads, and
`--selftest` exercises it on BOTH of those real files when they are present --
reporting explicitly when they are not, because a limb that did not run is not
a limb that passed.

-------------------------------------------------------------------------------
WHERE THE FROZEN TEXT FORCED A CHOICE.  Each is implemented in the STRICTER
direction and is named here so the supervisor's diff read sees it as a choice
and not as a reading.
-------------------------------------------------------------------------------
 (C1) `T_total` IS NEVER DEFINED OPERATIONALLY BY EITHER REGISTRATION.  Parent
      section 9.3 grades "T_total"; parent section 9.6 calls it "the force
      integration of section 2.6"; the parent's own installed comparator
      computes only `T_duct` (from `forcesDuct`) and consumes it as the total on
      the section 6.3 EMPTY arm, where the disk source is zero and the two
      coincide.  On a LOADED arm they do not.  DERIVED, NOT INVENTED, from
      parent section 9.6: the gated momentum balance takes a control volume that
      encloses the duct, the centrebody AND the disk source, so the quantity it
      is registered to test against -- `T_total` -- is the sum of everything
      inside it.  Parent section 9.5's ideal `T_total / T_disk = 2 sigma` says
      the same thing.  So `T_total = T_duct + T_hub + T_disk`.  It is REFUSED
      unless the caller states that composition verbatim (CLAUDE.md rule 14: a
      lesson is not applied until every call site asserts it), every component
      is reported separately, and a missing `forcesHub` REFUSES rather than
      silently dropping a term.  THIS IS REFERRED UPWARD AS A GAP IN THE FROZEN
      TEXT, not repaired around in silence.
 (C2) M6's JUNCTION BAND [0.95, 1.05] IS NOT SYMMETRIC UNDER RECIPROCAL, and
      the generator reports `last/first` while the blockMeshDict recomputation
      naturally yields `first/last`.  1/0.95 = 1.0526 > 1.05, so a value near
      the edge could pass under one convention and fail under the other.  The
      STRICTER reading is taken: the jump must lie in [1/1.05, 1.05] =
      [0.952381, 1.05], which is inside the registered band under EITHER
      convention.  Both readings are printed.
 (C3) M5's "1.5 +/- 5 %" is read as RELATIVE, i.e. [1.425, 1.575] -- F28G
      section 5.1 states its own spread as "-1.2 % / +1.0 %", so percentages in
      that section are relative.  The absolute reading [1.45, 1.55] is COMPUTED
      AND PRINTED beside it so the choice is visible and so a level that would
      fail the tighter reading cannot pass unremarked.
 (C4) M6's "`rho` identical across levels" is implemented as EXACT float
      equality -- `rho` is inherited from L1 by construction (F28G section 4.3),
      so anything else is a different ladder.  The largest deviation is printed
      whether or not it is zero.
 (C5) SECTION 7 CLAUSE 4's "at least 10x smaller than the difference between
      consecutive mesh levels, on every level" does not say WHICH consecutive
      difference a given level is measured against.  The STRICTER reading is
      taken: every level is measured against the SMALLER of the two consecutive
      differences, which is the hardest bar available.  The per-level-adjacent
      reading is printed beside it.
 (C6) THE OBSERVED ORDER IS COMPUTED TWICE -- once at the registered nominal
      refinement ratio r = 1.5, and once at the MEASURED per-level ratios from
      the cell counts (F28G section 5.1 measures r32 = 1.5013, not 1.5), by the
      Celik non-constant-`r` fixed point.  Those are the "both orders" rule 5
      requires printed.  The verdict is taken on the NOMINAL order -- it is the
      registered ladder -- and IF THE TWO ORDERS DISAGREE ABOUT THE BAND the
      row is NOT A RESULT, because an order whose verdict depends on which
      refinement ratio you believe is not established by the data.  That is a
      one-way strengthening and is therefore legal under rule 5.

-------------------------------------------------------------------------------
WHAT THIS COMPARATOR CANNOT SEE
-------------------------------------------------------------------------------
  * It does not parse the section 6.4 volume-ratio histogram.  Section 6.4
    GATES NOTHING on it and registers it as a REQUIRED REPORT, so this file
    requires the report to EXIST, to be non-empty, to be NEWER than the mesh it
    describes, and records its sha256 -- and refuses to emit a complete
    admission record without it.  It does not re-derive its numbers; that is
    `f28_face_volume_ratio.py`'s job and that reader carries its own planted
    control and negative limb.
  * It does not read cell geometry from `points` for any gated number.  On this
    wedge the tail-cone apex lies INSIDE a cell, so a reader taking min/max over
    cell vertices turns a thin slanted quad into a fat rectangle and overstates
    a volume 34x (parent Addendum 1 A1.2).  The one place cell volume is needed
    -- the disk source term -- goes through `analyse_f28.cell_volumes`, which
    resolves every cell into its ACTUAL FACES by pyramid decomposition.
  * It cannot see whether the L-142 property of F28G section 5.4 -- the finest
    radial cell of the wake row sitting on the centreline -- affects the
    integrated duct force.  F28G Addendum 1 A1.4 states that as a
    NON-measurement, and being common-mode across three levels is not evidence
    that it cancels in an observed order.
  * It cannot see anything that is wrong in all three levels the same way.
"""
import hashlib
import json
import math
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import analyse_f28 as F28                                        # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

# =============================================================================
# REGISTERED CONSTANTS -- each names the clause that authorises it (L-130: a
# gate's band is part of its referent, so a threshold without a stated referent
# is not a gate).  Nothing here is a preference.
# =============================================================================
R_LADDER = 1.5                  # F28G 4.7 / Sanaa 0 step 1; every direction
LEVEL_SCALE = {1: 1.0, 2: R_LADDER, 3: R_LADDER ** 2}   # F28G 4.1 / 4.7

# ---- the mesh-admission gate, F28G section 6.1 -----------------------------
M1_NONORTHO_MAX_DEG = 65.0      # parent 5, STRICTER than MESH_STANDARD 3.1's 70
M2_SKEWNESS_MAX = 4.0           # MESH_STANDARD 3.2 hard gate
M3_NEGATIVE_CELL_VOLUMES = 0    # parent 5
M4_GROWTH_CAP_L1 = 1.25         # Sanaa 2026-09-01 section 4; referent F28G 3
M5_R_TARGET = 1.5               # Sanaa section 0 step 1
M5_REL_TOL = 0.05               # "1.5 +/- 5 %", read as relative -- CHOICE C3
M6_JUNCTION_BAND = (0.95, 1.05)         # MESH_STANDARD 9.2, as F28G 6.1 states
# CHOICE C2.  The registered band is not symmetric under reciprocal and the two
# available conventions for a junction jump are reciprocals of one another, so
# the band is applied in the form that is inside the registered one under BOTH.
M6_JUNCTION_BAND_STRICT = (1.0 / M6_JUNCTION_BAND[1], M6_JUNCTION_BAND[1])

# The advisory that is RECORDED AND NEVER GATED (MESH_STANDARD 3.3 / 11.4,
# F28G 6.2).  It exists here ONLY so the record can print the advisory beside
# the number.  NO COMPARISON IN THIS FILE MAY REJECT ON IT, and
# `assert_aspect_ratio_never_gates` proves that by planting an absurd one.
ASPECT_RATIO_ADVISORY = 1000.0
NASA_TMR_REFERENCE_RANGE = (66643.0, 74041.0)   # MESH_STANDARD 3.3's calibration

# ---- the grid-convergence gate, F28G section 7 / parent section 9.3 --------
FS = 1.25                       # Roache factor of safety; parent 9.3
P_BAND = (1.3, 2.5)             # observed order band; parent 9.3
GCI_FINE_MAX_PCT = 3.0          # parent 9.3
STAGNANT_ORDER = 0.5            # the classifier's boundary, as the lab's
                                # shared `gci()` fixes it (analyse_t1c.py:331)
PRECONDITION_RATIO = 10.0       # F28G 7 clause 4, "at least 10x smaller"
ITER_CAP = 15000                # parent 8; HIT CAP -> NOT A RESULT

# ---- the plants (CLAUDE.md rule 3).  ONE PER READER THAT PRODUCES A NUMBER --
# 88.93 is not an arbitrary number: it is the value a sister lane MEASURED
# `checkMesh` printing `Mesh OK` at on this box, 2026-09-01.  Planting the
# measured counter-example is worth more than planting a round one.
PLANT_NONORTHO_DEG = 88.93
PLANT_SEVERE_FACES = 137
PLANT_SKEWNESS = 4.5
PLANT_MIN_VOLUME = -1.234e-20
PLANT_ASPECT_RATIO = 1.0e9
PLANT_CELLS = 424242
PLANT_TOL_REL = 1.0e-12

# The composition of `T_total`, which the caller must state verbatim.  CHOICE
# C1 above; see `t_total` for the derivation and the referral.
T_TOTAL_COMPOSITION = "duct+hub+disk"

# CLAUDE.md rule 1.  The ONLY vocabulary this file may emit.
VOCABULARY = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT",
              "BLOCKED", "PENDING")


def _assert_constants():
    """The constants above are checked against their own definitions, in that
    direction, AT IMPORT.  Not decoration: F28G section 4.1's whole repair is
    that a cap which does not scale as `1.25 ** (1/s)` binds at one level and
    goes slack at another, and a file that hard-codes 1.16040 could not tell
    that story from a typo.  So the ladder's scale is DERIVED from `R_LADDER`
    and the printed values of F28G section 4.1 are ASSERTION TARGETS.
    """
    if LEVEL_SCALE[2] != R_LADDER or LEVEL_SCALE[3] != R_LADDER ** 2:
        raise RuntimeError("LEVEL_SCALE is not R_LADDER's own ladder")
    for level, printed in ((1, 1.25000), (2, 1.16040), (3, 1.10426)):
        got = growth_cap(level)
        if abs(got - printed) > 5.0e-6:      # half the last digit F28G 4.1 prints
            raise RuntimeError(
                "the growth cap derived for L%d is %.9f and F28G section 4.1 "
                "prints %.5f; the cap is derived from `1.25 ** (1/s)` and a "
                "disagreement means the ladder in this file is not the ladder "
                "in the registration" % (level, got, printed))
    if M6_JUNCTION_BAND_STRICT[0] <= M6_JUNCTION_BAND[0]:
        raise RuntimeError("the strict junction band must be INSIDE the "
                           "registered one under both conventions")


def growth_cap(level):
    """F28G section 6.1 M4: `<= 1.25` at L1 and `1.25 ** (1/s)` at level `s`,
    where `s` is the level's linear scale from L1 (F28G section 4.1: `q` must
    scale as `q ** (1/s)` because expansion compounds PER CELL while `n` scales
    as `s`).  Derived, never pasted."""
    return M4_GROWTH_CAP_L1 ** (1.0 / LEVEL_SCALE[level])


# =============================================================================
# REFUSAL PLUMBING
# =============================================================================
# `analyse_f28.refuse` calls `sys.exit(2)` directly, which is right for a
# top-level comparator and wrong INSIDE a selftest that must demonstrate a
# refusal and then keep going.  So every refusal in THIS file raises, and `main`
# converts it.  The exit code is unchanged and the message format is unchanged;
# only the control flow differs, and it differs so that the both-way controls
# can exist at all.  SILENCE IS NOT SUCCESS: every limb below is judged on a
# raised exception or a returned verdict, never on what reached stdout.
class Refusal(Exception):
    pass


def refuse(msg):
    raise Refusal(msg)


def _rel(a, b):
    """Relative difference, with the degenerate denominator named."""
    d = max(abs(a), abs(b))
    return abs(a - b) / d if d > 0.0 else 0.0


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# =============================================================================
# THE `checkMesh` READER -- M1, M2, M3, and the RECORDED-NOT-GATED quantities
# =============================================================================
# THE INSTRUMENT IS THE REPORTED MAXIMUM.  MESH_STANDARD section 14.4 and F28G
# section 6.1.  The three lines below are the ones a comparator must NEVER read
# for a verdict; they are named here so `assert_verdict_strings_are_inert` can
# mutate exactly them and prove the verdicts do not move.
FORBIDDEN_VERDICT_LINES = (
    "Non-orthogonality check OK.",
    "Mesh OK.",
    "Failed 2 mesh checks.",
)

_RE_NONORTHO = re.compile(
    r"Mesh non-orthogonality Max:\s*([-+0-9.eE]+)\s+average:\s*([-+0-9.eE]+)")
_RE_SEVERE = re.compile(
    r"Number of severely non-orthogonal \(>\s*([0-9.]+)\s*degrees\) faces:\s*(\d+)")
_RE_SKEW = re.compile(r"Max skewness\s*=\s*([-+0-9.eE]+)")
_RE_MINVOL = re.compile(
    r"Min volume\s*=\s*([-+0-9.eE]+)\.\s*Max volume\s*=\s*([-+0-9.eE]+)\.")
_RE_NEGVOL = re.compile(r"Zero or negative cell volume detected")
_RE_NEGVOL_COUNT = re.compile(r"Number of negative volume cells:\s*(\d+)")
_RE_ASPECT_HIGH = re.compile(
    r"Max aspect ratio:\s*([-+0-9.eE]+),\s*number of cells\s*(\d+)")
_RE_ASPECT_OK = re.compile(r"Max aspect ratio\s*=\s*([-+0-9.eE]+)")
_RE_CELLS = re.compile(r"^\s*cells:\s*(\d+)\s*$", re.M)


def _sole(pattern, text, key, path):
    """Exactly one match, or a refusal that says why guessing is not allowed.

    A `checkMesh` log that has been APPENDED TO -- two runs into one file -- has
    two of every line, and taking the first or the last is a choice made by
    whichever run happened to be written first.  That is exactly how a stale
    number gets graded, so it is refused rather than resolved.
    """
    ms = list(pattern.finditer(text))
    if not ms:
        return None
    if len(ms) > 1:
        refuse("%s carries %d `%s` lines.  A checkMesh log with more than one "
               "of a quantity has been appended to or concatenated, and "
               "choosing between them by position is choosing which run is "
               "graded.  REFUSING rather than picking."
               % (path, len(ms), key))
    return ms[0]


def read_checkmesh(path):
    """Parse ONE `checkMesh` log.  Values only; no verdict is formed here.

    Separating the parse from the verdict is not tidiness.  It is what lets
    `assert_verdict_strings_are_inert` mutate the forbidden lines and compare
    the verdicts, and what makes it impossible for a verdict to reach for a
    string this function never returned.
    """
    if not os.path.isfile(path):
        refuse("no checkMesh log at %s -- M1, M2 and M3 are read off the "
               "REPORTED MAXIMUM in that log (MESH_STANDARD 14.4) and this "
               "comparator does not infer a mesh quantity it cannot read"
               % path)
    with open(path, errors="replace") as fh:
        text = fh.read()

    out = {"checkMesh_log": os.path.abspath(path),
           "sha256": _sha256(path),
           "bytes": os.path.getsize(path),
           "statuses": []}

    m = _sole(_RE_NONORTHO, text, "Mesh non-orthogonality Max:", path)
    if m is None:
        refuse("%s carries NO `Mesh non-orthogonality Max:` line.  M1 is read "
               "off the reported maximum and off NOTHING ELSE: "
               "`Non-orthogonality check OK.` and `Mesh OK.` / `Failed N mesh "
               "checks.` have been SHOWN unable to discriminate (identical on "
               "a 51.3-degree admissible mesh and an 81.6-degree inadmissible "
               "one, with the failed-check count running backwards), and a "
               "sister lane measured `Mesh OK` printed at 88.93 degrees on "
               "this box.  A log without the maximum cannot be graded, and "
               "falling back to the verdict string would be reading the wrong "
               "instrument." % path)
    out["nonortho_max_deg"] = float(m.group(1))
    out["nonortho_avg_deg"] = float(m.group(2))

    ms = _sole(_RE_SEVERE, text, "severely non-orthogonal faces", path)
    if ms is None:
        # `checkMesh` prints this line ONLY when the count is non-zero, so its
        # absence is a reported zero -- and a zero from a reader not shown able
        # to see a non-zero is not evidence (rule 3).  `certify_checkmesh_reader`
        # plants the line and requires this reader to come back with 137.
        out["severe_nonortho_faces"] = 0
        out["severe_nonortho_threshold_deg"] = None
        out["severe_line_present"] = False
    else:
        out["severe_nonortho_threshold_deg"] = float(ms.group(1))
        out["severe_nonortho_faces"] = int(ms.group(2))
        out["severe_line_present"] = True

    m = _sole(_RE_SKEW, text, "Max skewness", path)
    if m is None:
        refuse("%s carries no `Max skewness` line; M2 (MESH_STANDARD 3.2 hard "
               "gate, < %g) cannot be read" % (path, M2_SKEWNESS_MAX))
    out["skewness_max"] = float(m.group(1))

    # ---- M3 and the census rule (F28G 6.3 / MESH_STANDARD 12.3) ------------
    m = _sole(_RE_MINVOL, text, "Min volume", path)
    neg = _RE_NEGVOL.search(text) is not None
    mc = _RE_NEGVOL_COUNT.search(text)
    out["negative_cell_volume_line_present"] = neg
    out["negative_cell_volumes"] = int(mc.group(1)) if mc else (None if neg else 0)
    if m is None:
        out["min_cell_volume_m3"] = None
        out["max_cell_volume_m3"] = None
        out["census_status"] = "MIN_VOLUME_LINE_ABSENT"
    else:
        out["min_cell_volume_m3"] = float(m.group(1))
        out["max_cell_volume_m3"] = float(m.group(2))
        if out["min_cell_volume_m3"] < 0.0:
            out["census_status"] = "MIN_NEGATIVE"
        elif out["min_cell_volume_m3"] == 0.0:
            out["census_status"] = "MIN_ZERO"
        else:
            out["census_status"] = "MIN_POSITIVE"
    # MESH_STANDARD 12.3, as F28G 6.3 restates it: such a level is COUNTED IN
    # THE CENSUS AND NEVER DROPPED, and is excluded from ratio percentiles with
    # THE EXCLUSION REPORTED AS A NUMBER beside them.  The exclusion count is a
    # zero this file reports, so it carries a plant like every other zero.
    out["excluded_from_ratio_percentiles"] = (
        0 if out["census_status"] == "MIN_POSITIVE" else 1)
    out["counted_in_census"] = 1

    # ---- RECORDED AND NEVER GATED (F28G 6.2) ------------------------------
    ma = _RE_ASPECT_HIGH.search(text)
    if ma is not None:
        out["aspect_ratio_max"] = float(ma.group(1))
        out["aspect_ratio_high_cells"] = int(ma.group(2))
    else:
        mb = _sole(_RE_ASPECT_OK, text, "Max aspect ratio", path)
        out["aspect_ratio_max"] = float(mb.group(1)) if mb else None
        out["aspect_ratio_high_cells"] = 0 if mb else None
    if out["aspect_ratio_max"] is None:
        # MESH_STANDARD 11.4, quoted by F28G 6.2: NO VALUE of it makes a mesh
        # inadmissible, and what makes a record INCOMPLETE is the ABSENCE of
        # the number.  So absence is a refusal and any magnitude is admitted --
        # the two controls point in opposite directions on purpose.
        out["statuses"].append("ASPECT_RATIO_LINE_ABSENT")
    out["aspect_ratio_is_gated"] = False
    out["aspect_ratio_advisory"] = ASPECT_RATIO_ADVISORY
    out["aspect_ratio_reference_NASA_TMR"] = list(NASA_TMR_REFERENCE_RANGE)

    mcell = _RE_CELLS.search(text)
    if mcell is not None:
        out["cells"] = int(mcell.group(1))
    else:
        # The tracked summaries begin at `Checking geometry`, so the topology
        # census is not in them.  Recorded as a status, never silently skipped.
        out["cells"] = None
        out["statuses"].append("CELL_COUNT_LINE_ABSENT")

    # STATED, NOT IMPLIED: this reader returns no verdict string and the
    # verdict functions receive only this dictionary.
    out["verdict_strings_read"] = []
    out["instrument"] = ("the REPORTED MAXIMUM (MESH_STANDARD 14.4); the "
                         "`Non-orthogonality check OK.` and `Mesh OK.` / "
                         "`Failed N mesh checks.` lines are not parsed and "
                         "not returned")
    return out


def m1_m2_m3(cm):
    """M1, M2, M3 from a parsed `checkMesh` dictionary and nothing else.

    Takes the PARSED VALUES, never the text.  A verdict function that cannot
    see the log cannot reach for a verdict string in it, and that is a
    structural guarantee rather than a promise.
    """
    clauses = []
    clauses.append({
        "id": "M1", "quantity": "max non-orthogonality [deg]",
        "value": cm["nonortho_max_deg"], "threshold": M1_NONORTHO_MAX_DEG,
        "test": "value < %g" % M1_NONORTHO_MAX_DEG,
        "authority": "parent section 5 (stricter than MESH_STANDARD 3.1's 70)",
        "instrument": "the reported maximum (MESH_STANDARD 14.4)",
        "severely_nonorthogonal_faces": cm["severe_nonortho_faces"],
        "pass": cm["nonortho_max_deg"] < M1_NONORTHO_MAX_DEG})
    clauses.append({
        "id": "M2", "quantity": "max skewness",
        "value": cm["skewness_max"], "threshold": M2_SKEWNESS_MAX,
        "test": "value < %g" % M2_SKEWNESS_MAX,
        "authority": "MESH_STANDARD 3.2 hard gate",
        "pass": cm["skewness_max"] < M2_SKEWNESS_MAX})
    neg = cm["negative_cell_volumes"]
    clauses.append({
        "id": "M3", "quantity": "negative cell volumes",
        "value": neg, "threshold": M3_NEGATIVE_CELL_VOLUMES,
        "test": "count == 0 AND min cell volume > 0",
        "authority": "parent section 5; census status per MESH_STANDARD 12.3",
        "census_status": cm["census_status"],
        "min_cell_volume_m3": cm["min_cell_volume_m3"],
        "excluded_from_ratio_percentiles": cm["excluded_from_ratio_percentiles"],
        "counted_in_census": cm["counted_in_census"],
        "pass": (neg == 0 and cm["census_status"] == "MIN_POSITIVE")})

    # The severe-face count and the reported maximum must not contradict each
    # other.  `checkMesh` counts faces above its own severe threshold (70 by
    # default), so a non-zero count with a maximum below that threshold means
    # the two numbers came from different meshes -- a concatenated log, a
    # truncated one, or a hand-edited one.  THIS CHECK CAN FAIL FOR A REASON
    # ITS AUTHOR DOES NOT ALREADY KNOW, which is the only kind worth writing.
    thr = cm["severe_nonortho_threshold_deg"]
    if cm["severe_nonortho_faces"] > 0 and thr is not None:
        if cm["nonortho_max_deg"] <= thr:
            refuse("%s reports %d faces above %g degrees while its reported "
                   "MAXIMUM is %g degrees.  Those two numbers cannot both "
                   "describe one mesh.  REFUSING rather than grading a log "
                   "whose own two non-orthogonality readings disagree."
                   % (cm["checkMesh_log"], cm["severe_nonortho_faces"], thr,
                      cm["nonortho_max_deg"]))
    return clauses


def _splice_line(text, pattern, replacement, why):
    """Replace EXACTLY ONE match, or refuse.  A plant that lands zero times is
    a plant that proves nothing, and a plant that lands twice has changed
    something the control did not intend to change."""
    new, n = pattern.subn(replacement, text, count=0)
    if n != 1:
        refuse("the plant for %s matched %d times, not exactly once.  A "
               "control whose perturbation did not land, or landed twice, "
               "certifies nothing." % (why, n))
    return new


def certify_checkmesh_reader(path):
    """CLAUDE.md rule 3, on the reader that produces every mesh-admission
    number and every mesh-admission ZERO.

    The plant is not a Python variable.  The known perturbation is WRITTEN INTO
    THE LOG ON DISK, in the log's own format, and the SAME `read_checkmesh` the
    gate uses re-reads it FROM DISK.  If the reader cannot see it, this
    comparator refuses and no mesh is admitted.

    SIX LIMBS, each with its negative limb (the pristine text), and the last two
    pointing in OPPOSITE directions on purpose:

      (a) non-orthogonality maximum planted at 88.93 -- the value a sister lane
          MEASURED `checkMesh` printing `Mesh OK` at -- must be READ BACK and
          must make M1 fail.
      (b) the `severely non-orthogonal faces` line planted at 137 -- the reader
          reports 0 when the line is absent, and a zero from a reader not shown
          able to see a non-zero is not evidence.
      (c) skewness planted at 4.5 must make M2 fail.
      (d) a negative minimum cell volume must make M3 fail, must set
          `MIN_NEGATIVE`, and must move the census exclusion count off zero.
      (e) an aspect ratio planted at 1e9 must leave the level ADMITTED --
          MESH_STANDARD 3.3, advisory at 1000 and NEVER A LONE REJECTION.
      (f) mutating ONLY the forbidden verdict strings must leave M1, M2 and M3
          BIT-IDENTICAL.

    The artifact is snapshotted and restored BYTE-EXACTLY with its original
    mtime, and the sha256 is verified equal afterwards.  A grader that alters
    the artifact it grades has destroyed the evidence its number cites; a
    grader that moves an mtime has moved the evidence rule 4's age guard is
    built on.
    """
    snap = F28.ArtifactSnapshot(path)
    pristine = snap.text()
    base = read_checkmesh(path)
    base_v = m1_m2_m3(base)
    limbs = []

    def _write_and_read(text):
        F28._atomic_write_text(path, text)
        return read_checkmesh(path)

    try:
        # (a) the reported maximum
        t = _splice_line(pristine, _RE_NONORTHO,
                         "Mesh non-orthogonality Max: %g average: 9.96767"
                         % PLANT_NONORTHO_DEG, "M1's reported maximum")
        got = _write_and_read(t)
        if _rel(got["nonortho_max_deg"], PLANT_NONORTHO_DEG) > PLANT_TOL_REL:
            refuse("THE M1 READER IS BLIND: %g degrees was written into %s and "
                   "the reader came back with %g.  Every M1 verdict this file "
                   "could emit would be a number from a reader not shown able "
                   "to see a different one."
                   % (PLANT_NONORTHO_DEG, path, got["nonortho_max_deg"]))
        v = m1_m2_m3(got)
        if v[0]["pass"]:
            refuse("M1 ADMITTED A MESH AT %g DEGREES against a threshold of "
                   "%g.  This is the exact failure MESH_STANDARD 14.4 exists "
                   "to prevent." % (PLANT_NONORTHO_DEG, M1_NONORTHO_MAX_DEG))
        limbs.append({"limb": "a", "planted": "nonortho_max = %g"
                      % PLANT_NONORTHO_DEG, "read_back": got["nonortho_max_deg"],
                      "M1_pass": v[0]["pass"], "required": "M1 must FAIL",
                      "fired": True})

        # (b) the zero that is reported by the ABSENCE of a line
        t = pristine.replace(
            "    Non-orthogonality check OK.\n",
            " ***Number of severely non-orthogonal (> 70 degrees) faces: %d.\n"
            "    Non-orthogonality check OK.\n" % PLANT_SEVERE_FACES, 1)
        if t == pristine:
            refuse("could not place the severe-face plant into %s; the anchor "
                   "line is absent, so the ZERO this reader reports for "
                   "severely non-orthogonal faces cannot be certified and must "
                   "not be published" % path)
        got = _write_and_read(t)
        if got["severe_nonortho_faces"] != PLANT_SEVERE_FACES:
            refuse("THE SEVERE-FACE READER IS BLIND: %d was written into %s "
                   "and the reader came back with %r.  Its reported zero is "
                   "not evidence." % (PLANT_SEVERE_FACES, path,
                                      got["severe_nonortho_faces"]))
        limbs.append({"limb": "b", "planted": "severe faces = %d"
                      % PLANT_SEVERE_FACES,
                      "read_back": got["severe_nonortho_faces"],
                      "required": "the reported ZERO must be a reader that "
                                  "can see a non-zero", "fired": True})

        # (c) skewness
        t = _splice_line(pristine, _RE_SKEW,
                         "Max skewness = %g" % PLANT_SKEWNESS, "M2's maximum")
        got = _write_and_read(t)
        v = m1_m2_m3(got)
        if _rel(got["skewness_max"], PLANT_SKEWNESS) > PLANT_TOL_REL or v[1]["pass"]:
            refuse("M2 did not see or did not reject a planted skewness of %g "
                   "against its hard gate of %g (read back %r)"
                   % (PLANT_SKEWNESS, M2_SKEWNESS_MAX, got["skewness_max"]))
        limbs.append({"limb": "c", "planted": "skewness = %g" % PLANT_SKEWNESS,
                      "read_back": got["skewness_max"],
                      "M2_pass": v[1]["pass"], "required": "M2 must FAIL",
                      "fired": True})

        # (d) the negative minimum volume, and the census exclusion count
        t = _splice_line(
            pristine, _RE_MINVOL,
            "Min volume = %g. Max volume = 0.0468706." % PLANT_MIN_VOLUME,
            "M3's minimum cell volume")
        got = _write_and_read(t)
        v = m1_m2_m3(got)
        if (got["census_status"] != "MIN_NEGATIVE" or v[2]["pass"]
                or got["excluded_from_ratio_percentiles"] != 1
                or got["counted_in_census"] != 1):
            refuse("M3 / the census rule did not fire on a planted minimum "
                   "cell volume of %g: status %r, M3 pass %r, exclusions %r, "
                   "counted %r.  MESH_STANDARD 12.3 requires such a level "
                   "RECORDED WITH A STATUS, COUNTED IN THE CENSUS, NEVER "
                   "DROPPED, and the exclusion REPORTED AS A NUMBER."
                   % (PLANT_MIN_VOLUME, got["census_status"], v[2]["pass"],
                      got["excluded_from_ratio_percentiles"],
                      got["counted_in_census"]))
        limbs.append({"limb": "d", "planted": "min volume = %g"
                      % PLANT_MIN_VOLUME, "census_status": got["census_status"],
                      "M3_pass": v[2]["pass"],
                      "exclusions": got["excluded_from_ratio_percentiles"],
                      "required": "M3 must FAIL and the exclusion count must "
                                  "leave zero", "fired": True})

        # (e) THE OPPOSITE DIRECTION.  Aspect ratio never rejects, at any value.
        t = _splice_line(
            pristine, _RE_ASPECT_HIGH,
            "Max aspect ratio: %g, number of cells 2789" % PLANT_ASPECT_RATIO,
            "the advisory aspect ratio")
        got = _write_and_read(t)
        v = m1_m2_m3(got)
        if _rel(got["aspect_ratio_max"], PLANT_ASPECT_RATIO) > PLANT_TOL_REL:
            refuse("the aspect-ratio reader did not see a planted %g"
                   % PLANT_ASPECT_RATIO)
        if not all(c["pass"] for c in v):
            refuse("A PLANTED ASPECT RATIO OF %g REJECTED A MESH.  "
                   "MESH_STANDARD 3.3 makes aspect ratio ADVISORY AT 1000 AND "
                   "NEVER A LONE REJECTION -- the lab's own reference-grade "
                   "NASA TMR grids measure %g to %g -- and F28G section 6.2 "
                   "records it and gates nothing on it.  A gate that rejects "
                   "on aspect ratio alone contradicts the standard."
                   % (PLANT_ASPECT_RATIO, NASA_TMR_REFERENCE_RANGE[0],
                      NASA_TMR_REFERENCE_RANGE[1]))
        limbs.append({"limb": "e", "planted": "aspect ratio = %g"
                      % PLANT_ASPECT_RATIO, "read_back": got["aspect_ratio_max"],
                      "M1_M2_M3_all_pass": True,
                      "required": "the level must STILL be admitted",
                      "fired": True})

        # (f) the forbidden verdict strings are inert
        t = pristine
        n_mut = 0
        for s, repl in (("    Non-orthogonality check OK.\n",
                         " ***Non-orthogonality check FAILED.\n"),
                        ("Failed 2 mesh checks.", "Mesh OK.")):
            if s in t:
                t = t.replace(s, repl, 1)
                n_mut += 1
        if n_mut == 0:
            refuse("none of the forbidden verdict strings %s is present in %s, "
                   "so their inertness cannot be PROVED on this artifact.  A "
                   "promise not to read a string is not a proof."
                   % (list(FORBIDDEN_VERDICT_LINES), path))
        got = _write_and_read(t)
        v = m1_m2_m3(got)
        same = [(a["id"], a["value"], a["pass"]) for a in v] == \
               [(a["id"], a["value"], a["pass"]) for a in base_v]
        if not same:
            refuse("MUTATING ONLY THE VERDICT STRINGS MOVED A VERDICT.  This "
                   "comparator is reading `Non-orthogonality check OK.` or "
                   "`Mesh OK.` / `Failed N mesh checks.` somewhere, and those "
                   "strings have been SHOWN unable to discriminate "
                   "(MESH_STANDARD 14.4).")
        limbs.append({"limb": "f", "mutated_lines": n_mut,
                      "required": "M1/M2/M3 bit-identical", "fired": True})
    finally:
        snap.restore()
    snap.verify_unchanged("the checkMesh reader certification")
    return {"control": "certify_checkmesh_reader",
            "authority": "CLAUDE.md rule 3; MESH_STANDARD 14.4 / 3.3 / 12.3",
            "artifact": os.path.abspath(path),
            "sha256_before_and_after": snap.sha,
            "limbs": limbs, "n_limbs": len(limbs),
            "negative_limb": "the pristine text, re-read after restore, "
                             "reproduces the unplanted values"}


# =============================================================================
# M4 AND M6's JUNCTION LIMB -- RECOMPUTED FROM THE WRITTEN `blockMeshDict`
# =============================================================================
# MESH_STANDARD section 9.2, as F28G section 5.3 quotes it: READ BACK THE
# ACHIEVED GRADING, NEVER THE REQUESTED ONE.  The generator's own
# `MESH_DIAGNOSTICS.json` is the REQUESTED side -- it is what the generator
# believes it solved for -- and F12's defect was precisely that the requested
# parameter was identical at every level while the returned one was not.  So
# M4 and M6's junction limb are recomputed HERE, from the bytes blockMesh was
# actually handed, and the diagnostics file is then required to AGREE.  A
# diagnostics file that describes a different mesh from the dict beside it is a
# failure this recomputation can find and a comparison of the diagnostics with
# themselves never could.
#
# NO GEOMETRY IS READ.  Cell sizes within a block direction are proportional to
# the block's edge length, which the dict does not carry -- and the ratios M4
# and M6 need are ratios of sizes WITHIN one direction of ONE block, so the
# edge length cancels exactly.  Nothing here touches `points`, and nothing here
# can repeat the min/max-over-vertices error that overstated an apex cell's
# volume 34x (parent Addendum 1 A1.2).
_RE_HEX = re.compile(
    r"^\s*hex\s*\(([^)]*)\)\s*(\w*)\s*\((\d+)\s+(\d+)\s+(\d+)\)\s*"
    r"simpleGrading\s*", re.M)


def _balanced(text, start):
    """The substring of `text` from the `(` at `start` to its matching `)`."""
    if text[start] != "(":
        refuse("expected `(` at offset %d of the blockMeshDict" % start)
    depth, i = 0, start
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1], i + 1
        i += 1
    refuse("unbalanced parentheses in the blockMeshDict grading spec")


def _split_top(body):
    """Split the inside of a grading spec into its three per-direction specs."""
    inner = body[1:-1]
    out, depth, cur = [], 0, []
    for ch in inner:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth == 0 and ch.isspace() and not cur:
            continue
        cur.append(ch)
        if depth == 0 and (ch == ")" or (cur and ch.isspace())):
            tok = "".join(cur).strip()
            if tok:
                out.append(tok)
            cur = []
    tok = "".join(cur).strip()
    if tok:
        out.append(tok)
    return out


def _parse_dir_spec(spec, n_cells, where):
    """One direction's grading -> a list of (length_fraction, n, expansion).

    A bare scalar is one segment spanning the whole direction.  A multi-grading
    is `( (Lf Cf E) (Lf Cf E) ... )`.  The per-segment cell counts are
    `round(Cf * n)` with the LAST adjusted so the counts sum to `n` -- and a
    segment that rounds to fewer than one cell REFUSES, because a zero-cell
    segment is a grading the dict describes and the mesh does not contain.
    """
    spec = spec.strip()
    if not spec.startswith("("):
        return [(1.0, n_cells, float(spec))]
    segs = []
    for m in re.finditer(r"\(\s*([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*\)",
                         spec):
        segs.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
    if not segs:
        refuse("%s: unparsable grading spec %r" % (where, spec))
    lf_sum = sum(s[0] for s in segs)
    cf_sum = sum(s[1] for s in segs)
    if abs(lf_sum - 1.0) > 1e-6 or abs(cf_sum - 1.0) > 1e-6:
        refuse("%s: the grading spec's length fractions sum to %.9g and its "
               "cell fractions to %.9g; both must be 1.  A spec that does not "
               "close describes a direction this reader cannot reconstruct."
               % (where, lf_sum, cf_sum))
    ns = [int(round(s[1] * n_cells)) for s in segs]
    ns[-1] = n_cells - sum(ns[:-1])
    if any(k < 1 for k in ns):
        refuse("%s: a grading segment resolves to %r cells out of %d; a "
               "segment with no cells is in the dict and not in the mesh"
               % (where, ns, n_cells))
    return [(segs[i][0], ns[i], segs[i][2]) for i in range(len(segs))]


def _per_cell_ratio(expansion, n):
    """`q` from blockMesh's expansion ratio, which is LAST cell / FIRST cell
    over `n` cells: `E = q ** (n - 1)`.  Returned as the MAGNITUDE
    `max(q, 1/q)`, because a contraction of 1.25 is a cell-to-cell size change
    of 1.25 in exactly the sense M4 caps."""
    if n < 2:
        return None
    if expansion <= 0.0:
        refuse("a non-positive expansion ratio %r cannot be a size ratio"
               % expansion)
    q = expansion ** (1.0 / (n - 1))
    return max(q, 1.0 / q)


def _first_cell(length_fraction, n, expansion):
    """First cell size of a segment, in units of the block's edge length."""
    if n < 2:
        return length_fraction / n
    q = expansion ** (1.0 / (n - 1))
    if q == 1.0:
        return length_fraction / n
    return length_fraction * (1.0 - q) / (1.0 - q ** n)


def grading_readback(dict_path):
    """Every per-cell ratio and every junction jump in the WRITTEN dict.

    Returns the worst of each and the full census, keyed by block and
    direction, so a failure names the block it came from rather than the file.
    """
    if not os.path.isfile(dict_path):
        refuse("no blockMeshDict at %s -- M4 and M6's junction limb are read "
               "back from the ACHIEVED grading (MESH_STANDARD 9.2) and this "
               "comparator will not take the generator's word for it"
               % dict_path)
    with open(dict_path, errors="replace") as fh:
        text = fh.read()
    blocks, worst_q, worst_jj = [], None, None
    for m in _RE_HEX.finditer(text):
        ns = (int(m.group(3)), int(m.group(4)), int(m.group(5)))
        body, _end = _balanced(text, m.end())
        specs = _split_top(body)
        if len(specs) != 3:
            refuse("%s: a `simpleGrading` entry resolved to %d direction "
                   "specs, not 3: %r" % (dict_path, len(specs), specs))
        rec = {"block": len(blocks), "n": list(ns), "directions": {}}
        for axis, (spec, n) in enumerate(zip(specs, ns)):
            where = "%s block %d axis %d" % (dict_path, rec["block"], axis)
            segs = _parse_dir_spec(spec, n, where)
            qs, jjs = [], []
            for i, (lf, k, e) in enumerate(segs):
                q = _per_cell_ratio(e, k)
                if q is not None:
                    qs.append(q)
                if i > 0:
                    lf0, k0, e0 = segs[i - 1]
                    last_prev = _first_cell(lf0, k0, e0) * e0
                    first_here = _first_cell(lf, k, e)
                    if last_prev <= 0.0:
                        refuse("%s: a non-positive cell size in segment %d"
                               % (where, i - 1))
                    jjs.append(first_here / last_prev)
            rec["directions"][axis] = {
                "n_cells": n, "n_segments": len(segs),
                "per_cell_ratio_max": max(qs) if qs else None,
                "junction_jumps_first_over_last": jjs}
            for q in qs:
                if worst_q is None or q > worst_q[0]:
                    worst_q = (q, where)
            for jj in jjs:
                dev = max(jj, 1.0 / jj)
                if worst_jj is None or dev > worst_jj[0]:
                    worst_jj = (dev, jj, where)
        blocks.append(rec)
    if not blocks:
        refuse("%s carries no `hex ... simpleGrading` entries; there is "
               "nothing to read back" % dict_path)
    return {"blockMeshDict": os.path.abspath(dict_path),
            "sha256": _sha256(dict_path),
            "n_blocks": len(blocks),
            "worst_per_cell_ratio": worst_q[0],
            "worst_per_cell_ratio_where": worst_q[1],
            "worst_junction_jump": worst_jj[1] if worst_jj else None,
            "worst_junction_deviation": worst_jj[0] if worst_jj else None,
            "worst_junction_where": worst_jj[2] if worst_jj else None,
            "n_junctions": sum(len(d["junction_jumps_first_over_last"])
                               for b in blocks for d in b["directions"].values()),
            "blocks": blocks,
            "source": "RECOMPUTED FROM THE WRITTEN DICT (MESH_STANDARD 9.2), "
                      "not taken from MESH_DIAGNOSTICS.json"}


# =============================================================================
# THE GENERATOR'S DIAGNOSTICS -- M5, M6's `rho` limb, and the cross-checks
# =============================================================================
def read_diagnostics(path):
    if not os.path.isfile(path):
        refuse("no MESH_DIAGNOSTICS.json at %s -- M5 (per-direction refinement "
               "ratio) and M6's `rho` limb are read from it, and a ladder "
               "whose per-direction counts cannot be read is a ladder whose "
               "similarity is unestablished.  The jet-flap lane's `--n-rad 0` "
               "defect refined ONE direction at 1.02 while another refined at "
               "1.5, and a whole-mesh cell count cannot see that." % path)
    with open(path) as fh:
        d = json.load(fh)
    for key in ("nx", "nr", "y_first_requested_m", "level",
                "level_scale_from_L1", "growth_cap_per_cell",
                "growth_cap_junction", "mesh_script_sha256",
                "blockMeshDict_sha256"):
        if key not in d:
            refuse("%s carries no %r; this comparator does not default a "
                   "mesh quantity it was told to read" % (path, key))
    d["_path"] = os.path.abspath(path)
    return d


def directions(diag):
    """Every refined direction of one level, as a flat dict.

    `y_first` is included and is inverted, because it is a SPACING: a finer
    level has a SMALLER first cell, so its refinement ratio is
    `coarse / fine` where a count's is `fine / coarse`.  Getting that backwards
    turns 1.5 into 0.667 and the band rejects the correct ladder -- so the two
    kinds are separated by construction rather than by a comment.
    """
    out = {}
    for group in ("nx", "nr"):
        for k, v in diag[group].items():
            out["%s.%s" % (group, k)] = ("count", float(v))
    out["y_first"] = ("spacing", float(diag["y_first_requested_m"]))
    return out


def m4_m5_m6(levels):
    """M4, M5 and M6 across the whole ladder.

    `levels` maps 1/2/3 -> {"diag": ..., "grading": ...}.  These three clauses
    are LADDER-WIDE (M5 and M6 compare levels), so they are evaluated once and
    the result is attached to every level's record -- a per-level M5 would be a
    quantity with no meaning.
    """
    clauses = {1: [], 2: [], 3: []}
    detail = {}

    # ---- M4: the linear growth cap, from the WRITTEN dict ------------------
    for lv in sorted(levels):
        cap = growth_cap(lv)
        g = levels[lv]["grading"]
        diag = levels[lv]["diag"]
        # The generator's own recorded cap must be the one this file derives.
        # A generator that built under a different cap from the one the gate
        # applies is a mesh graded against a threshold it never met.
        if abs(diag["growth_cap_per_cell"] - cap) > 1e-9:
            refuse("L%d was generated under a per-cell growth cap of %.9f and "
                   "M4's derived cap for that level is %.9f (`1.25 ** (1/%g)`, "
                   "F28G section 4.1).  The mesh was built to a different "
                   "threshold from the one the gate applies."
                   % (lv, diag["growth_cap_per_cell"], cap, LEVEL_SCALE[lv]))
        clauses[lv].append({
            "id": "M4", "quantity": "linear cell-size growth, per cell, every "
                                    "direction, RECOMPUTED from the written "
                                    "blockMeshDict",
            "value": g["worst_per_cell_ratio"], "threshold": cap,
            "test": "worst per-cell ratio <= 1.25 ** (1/s)",
            "authority": "Sanaa 2026-09-01 section 4; referent stated in F28G "
                         "section 3 (a VOLUME cap of 1.25 is unattainable on "
                         "an axisymmetric wedge: the axis floor is "
                         "(1+q)^2 - 1 >= 3 exactly)",
            "where": g["worst_per_cell_ratio_where"],
            "n_blocks_read": g["n_blocks"],
            "pass": g["worst_per_cell_ratio"] <= cap + 1e-12})
        # M4's junction limb.  Convention-free: the deviation is
        # `max(jj, 1/jj)`, so it cannot be moved by which way round the ratio
        # was taken (CHOICE C2).
        cap_j = cap
        clauses[lv].append({
            "id": "M4j", "quantity": "linear size jump across every segment "
                                     "junction, RECOMPUTED",
            "value": g["worst_junction_jump"],
            "deviation": g["worst_junction_deviation"],
            "threshold": cap_j,
            "test": "max(jump, 1/jump) <= 1.25 ** (1/s)",
            "authority": "F28G section 4.2 -- a minimum is not a bound; the "
                         "cap is a REFUSAL in the generator and a clause here",
            "where": g["worst_junction_where"],
            "n_junctions": g["n_junctions"],
            "pass": (g["worst_junction_deviation"] is None
                     or g["worst_junction_deviation"] <= cap_j + 1e-12)})

    # ---- M5: per-direction refinement ratio --------------------------------
    dirs = {lv: directions(levels[lv]["diag"]) for lv in sorted(levels)}
    keys = sorted(dirs[1])
    for lv in (2, 3):
        missing = sorted(set(keys) ^ set(dirs[lv]))
        if missing:
            refuse("the direction sets of L1 and L%d differ: %s.  A ladder "
                   "whose levels do not carry THE SAME directions cannot be "
                   "compared per direction, and a whole-mesh cell count would "
                   "have hidden it -- which is exactly how the jet-flap lane's "
                   "`--n-rad 0` defect refined one direction at 1.02 while "
                   "another refined at 1.5." % (lv, missing))
    lo, hi = M5_R_TARGET * (1 - M5_REL_TOL), M5_R_TARGET * (1 + M5_REL_TOL)
    lo_abs, hi_abs = M5_R_TARGET - M5_REL_TOL, M5_R_TARGET + M5_REL_TOL
    rows, worst = [], None
    for k in keys:
        kind = dirs[1][k][0]
        for a, b, tag in ((1, 2, "r21"), (2, 3, "r32")):
            va, vb = dirs[a][k][1], dirs[b][k][1]
            if va <= 0.0 or vb <= 0.0:
                refuse("direction %r has a non-positive value at L%d/L%d"
                       % (k, a, b))
            r = (vb / va) if kind == "count" else (va / vb)
            rows.append({"direction": k, "pair": tag, "kind": kind,
                         "coarse": va, "fine": vb, "r": r,
                         "in_relative_band": lo <= r <= hi,
                         "in_absolute_band": lo_abs <= r <= hi_abs})
            dev = abs(r - M5_R_TARGET)
            if worst is None or dev > worst["deviation"]:
                worst = {"direction": k, "pair": tag, "r": r, "deviation": dev}
    all_rel = all(x["in_relative_band"] for x in rows)
    all_abs = all(x["in_absolute_band"] for x in rows)
    detail["M5_rows"] = rows
    for lv in clauses:
        clauses[lv].append({
            "id": "M5", "quantity": "per-direction refinement ratio",
            "band_applied": [lo, hi],
            "band_reading": "RELATIVE, `1.5 +/- 5 %` (CHOICE C3; F28G section "
                            "5.1 states its own spread as -1.2 %/+1.0 %)",
            "band_absolute_alternative": [lo_abs, hi_abs],
            "in_absolute_band_too": all_abs,
            "n_directions": len(keys), "n_ratios": len(rows),
            "worst": worst,
            "authority": "Sanaa section 0 step 1",
            "scope": "LADDER-WIDE -- this clause compares levels and is "
                     "attached to each level's record, not measured per level",
            "pass": all_rel})

    # ---- M6: similarity read-back ------------------------------------------
    rho_rows, rho_ok = [], True
    l1 = levels[1]["diag"]
    for group in ("axial", "radial"):
        for name, ent in sorted(l1.get(group, {}).items()):
            if "split_rho" not in ent:
                continue
            vals = []
            for lv in sorted(levels):
                e = levels[lv]["diag"].get(group, {}).get(name)
                if e is None or "split_rho" not in e:
                    refuse("distribution %r carries `split_rho` at L1 and not "
                           "at L%d.  F28G section 4.3 inherits `(alpha, rho)` "
                           "from L1 at every level; a level that does not "
                           "carry it did not inherit it." % (name, lv))
                vals.append(e["split_rho"])
            identical = all(v == vals[0] for v in vals)   # CHOICE C4: exact
            spread = max(vals) - min(vals)
            rho_ok = rho_ok and identical
            rho_rows.append({"distribution": "%s.%s" % (group, name),
                             "rho": vals, "identical_exact": identical,
                             "max_deviation": spread})
    detail["M6_rho_rows"] = rho_rows

    jj_ok, jj_rows = True, []
    for lv in sorted(levels):
        g = levels[lv]["grading"]
        dev = g["worst_junction_deviation"]
        inside_strict = (dev is None
                         or dev <= M6_JUNCTION_BAND_STRICT[1] + 1e-12)
        inside_plain = (g["worst_junction_jump"] is None
                        or M6_JUNCTION_BAND[0] <= g["worst_junction_jump"]
                        <= M6_JUNCTION_BAND[1])
        jj_ok = jj_ok and inside_strict
        jj_rows.append({"level": lv, "worst_jump_first_over_last":
                        g["worst_junction_jump"], "deviation": dev,
                        "inside_strict_band": inside_strict,
                        "inside_registered_band_as_written": inside_plain,
                        "where": g["worst_junction_where"]})
    detail["M6_junction_rows"] = jj_rows
    for lv in clauses:
        clauses[lv].append({
            "id": "M6", "quantity": "similarity read-back: `rho` identical "
                                    "across levels AND every junction jump in "
                                    "band at every level",
            "rho_identical_exact": rho_ok, "n_distributions": len(rho_rows),
            "junction_band_applied": list(M6_JUNCTION_BAND_STRICT),
            "junction_band_registered": list(M6_JUNCTION_BAND),
            "band_reading": "CHOICE C2 -- [1/1.05, 1.05], inside the "
                            "registered band under BOTH conventions, because "
                            "1/0.95 = 1.0526 > 1.05 and the two available "
                            "conventions are reciprocals",
            "junctions_in_band": jj_ok,
            "authority": "MESH_STANDARD 9.2 -- the ACHIEVED grading, "
                         "recomputed from the written dict",
            "scope": "LADDER-WIDE",
            "pass": rho_ok and jj_ok})
    return clauses, detail


def cross_check_diag_against_dict(diag, grading, level):
    """The generator's diagnostics must describe the dict beside them.

    Two independent identities, and neither is derived from the other:
      (i) the dict's sha256 must be the one the generator recorded;
      (ii) the worst per-cell ratio the generator reports across all its named
           distributions must equal the one recomputed from the written bytes.
    (i) alone would pass on a dict regenerated bit-identically by a DIFFERENT
    generator; (ii) alone would pass on a stale diagnostics file that happens
    to agree.  Together they are a real read-back.
    """
    if diag["blockMeshDict_sha256"] != grading["sha256"]:
        refuse("L%d's MESH_DIAGNOSTICS.json records blockMeshDict sha256 %s "
               "and the dict on disk beside it hashes to %s.  The diagnostics "
               "describe a different mesh from the one that was built."
               % (level, diag["blockMeshDict_sha256"][:16],
                  grading["sha256"][:16]))
    reported = []
    for group in ("axial", "radial"):
        for name, ent in sorted(diag.get(group, {}).items()):
            for q in ent.get("q", []):
                reported.append(max(abs(q), 1.0 / abs(q)) if q else None)
    reported = [q for q in reported if q]
    if not reported:
        refuse("L%d's diagnostics report no per-cell ratios to cross-check "
               "against the written dict" % level)
    worst_reported = max(reported)
    worst_dict = grading["worst_per_cell_ratio"]
    if _rel(worst_reported, worst_dict) > 1e-9:
        refuse("L%d: the generator reports a worst per-cell ratio of %.12f and "
               "the WRITTEN DICT recomputes to %.12f.  MESH_STANDARD 9.2 grades "
               "the ACHIEVED grading; a disagreement here means the "
               "diagnostics are not a read-back of the bytes blockMesh was "
               "handed." % (level, worst_reported, worst_dict))
    return {"blockMeshDict_sha256": grading["sha256"],
            "worst_per_cell_ratio_generator": worst_reported,
            "worst_per_cell_ratio_recomputed": worst_dict,
            "relative_difference": _rel(worst_reported, worst_dict),
            "tolerance": 1e-9}


def require_volume_ratio_report(path, dict_path, level):
    """F28G section 6.4: the histogram is a REQUIRED REPORT and NOT A GATE, and
    "a record lacking it is incomplete".

    So its ABSENCE refuses and its CONTENT gates nothing.  This file does not
    re-derive the histogram: section 6.4 sets no threshold on it, MESH_STANDARD
    11.4/12.9 set none either, and a parser for an unregistered text format
    would be a second thing to keep right.  What is checked is that the report
    EXISTS, is non-empty, and is NEWER than the dict it claims to describe --
    an age guard on the EVIDENCE, in the same spirit as rule 4 clause 6, since
    a histogram older than the mesh is a histogram of a different mesh.
    """
    if not path:
        refuse("L%d has no section 6.4 volume-ratio report.  Sanaa's section 4 "
               "requires the histogram BEFORE SOLVING and F28G section 6.4 "
               "registers it as a REQUIRED REPORT: a record lacking it is "
               "INCOMPLETE.  This comparator will not print a complete "
               "mesh-admission record without it -- and it gates nothing on "
               "its values, because section 6.4 gates nothing." % level)
    if not os.path.isfile(path):
        refuse("L%d's volume-ratio report %s does not exist" % (level, path))
    size = os.path.getsize(path)
    if size == 0:
        refuse("L%d's volume-ratio report %s is empty" % (level, path))
    t_rep = os.path.getmtime(path)
    t_dict = os.path.getmtime(dict_path)
    if t_rep <= t_dict:
        refuse("L%d's volume-ratio report %s is NOT newer than the "
               "blockMeshDict it describes (%.6f <= %.6f).  A histogram older "
               "than the mesh is a histogram of a different mesh."
               % (level, path, t_rep, t_dict))
    return {"report": os.path.abspath(path), "bytes": size,
            "sha256": _sha256(path), "mtime": t_rep,
            "gated": False,
            "authority": "F28G section 6.4 -- REQUIRED REPORT, NOT A GATE; "
                         "MESH_STANDARD 11.4 / 12.9 set no threshold",
            "parsed": False,
            "why_not_parsed": "section 6.4 sets no threshold on any of its "
                              "populations, so a parser here would add a "
                              "second thing to keep right and no gate; "
                              "f28_face_volume_ratio.py carries the planted "
                              "control and the negative limb for those numbers"}


def mesh_gate(spec):
    """F28G section 6.  A level failing ANY clause of 6.1 is NOT A RESULT and
    NO SOLVE IS LAUNCHED ON IT."""
    levels = {}
    controls = []
    for lv in (1, 2, 3):
        key = "L%d" % lv
        if key not in spec.get("levels", {}):
            refuse("the mesh-gate spec carries no %r.  All three levels are "
                   "gated; a ladder graded on two levels is not this ladder."
                   % key)
        ent = spec["levels"][key]
        d = ent["dir"]
        cm_path = ent.get("checkmesh") or os.path.join(d, "log.checkMesh")
        dict_path = ent.get("blockmeshdict") or os.path.join(
            d, "system", "blockMeshDict")
        diag_path = ent.get("diagnostics") or os.path.join(
            d, "system", "MESH_DIAGNOSTICS.json")
        # RULE 3 FIRST.  The reader is certified BEFORE anything it produces is
        # read for record, so no number below comes from an uncertified reader.
        controls.append(certify_checkmesh_reader(cm_path))
        cm = read_checkmesh(cm_path)
        diag = read_diagnostics(diag_path)
        if int(diag["level"]) != lv:
            refuse("%s declares level %r and was supplied as %s"
                   % (diag_path, diag["level"], key))
        if abs(float(diag["level_scale_from_L1"]) - LEVEL_SCALE[lv]) > 1e-12:
            refuse("%s records a level scale of %r; this ladder's L%d scale is "
                   "%g (r = %g)" % (diag_path, diag["level_scale_from_L1"],
                                    lv, LEVEL_SCALE[lv], R_LADDER))
        grading = grading_readback(dict_path)
        levels[lv] = {"dir": os.path.abspath(d), "checkmesh": cm,
                      "diag": diag, "grading": grading,
                      "readback_cross_check":
                          cross_check_diag_against_dict(diag, grading, lv),
                      "volume_ratio_report": require_volume_ratio_report(
                          ent.get("volume_ratio_report"), dict_path, lv)}
        if cm["cells"] is not None and diag.get("cells_predicted") is not None:
            if int(cm["cells"]) != int(diag["cells_predicted"]):
                refuse("L%d: the generator predicted %d cells and checkMesh "
                       "counted %d.  The dict and the mesh are not the same "
                       "mesh." % (lv, diag["cells_predicted"], cm["cells"]))

    ladder, detail = m4_m5_m6(levels)

    out = {"gate": "F28G section 6 -- MESH ADMISSION",
           "registration": "verification/campaign/"
                           "F28G_GRID_CONVERGENCE_PREREGISTRATION.md",
           "refinement_ratio_nominal": R_LADDER,
           "ladder_detail": detail,
           "rule_3_controls": controls,
           "levels": {}}
    admitted = True
    for lv in (1, 2, 3):
        cm = levels[lv]["checkmesh"]
        clauses = m1_m2_m3(cm) + ladder[lv]
        ok = all(c["pass"] for c in clauses)
        admitted = admitted and ok
        out["levels"]["L%d" % lv] = {
            "dir": levels[lv]["dir"],
            "verdict": "PASS" if ok else "NOT A RESULT",
            "why": ("every clause of F28G section 6.1 holds" if ok else
                    "clause(s) %s failed; F28G section 6.1: a level failing any "
                    "clause is NOT A RESULT and NO SOLVE IS LAUNCHED ON IT"
                    % [c["id"] for c in clauses if not c["pass"]]),
            "clauses": clauses,
            "recorded_never_gated": {
                "max_aspect_ratio": cm["aspect_ratio_max"],
                "high_aspect_ratio_cells": cm["aspect_ratio_high_cells"],
                "authority": "MESH_STANDARD 3.3 advisory at %g and NEVER A "
                             "LONE REJECTION; 11.4: no value makes a mesh "
                             "inadmissible, only the ABSENCE of the number "
                             "makes a record incomplete"
                             % ASPECT_RATIO_ADVISORY,
                "NASA_TMR_reference": list(NASA_TMR_REFERENCE_RANGE),
                "min_cell_volume_m3": cm["min_cell_volume_m3"],
                "census_status": cm["census_status"],
                "counted_in_census": cm["counted_in_census"],
                "excluded_from_ratio_percentiles":
                    cm["excluded_from_ratio_percentiles"],
                "cells": cm["cells"],
                "statuses": cm["statuses"]},
            "volume_ratio_report": levels[lv]["volume_ratio_report"],
            "readback_cross_check": levels[lv]["readback_cross_check"],
            "checkMesh_log": cm["checkMesh_log"],
            "checkMesh_sha256": cm["sha256"],
            "mesh_script_sha256": levels[lv]["diag"]["mesh_script_sha256"]}
    out["verdict"] = "PASS" if admitted else "NOT A RESULT"
    out["consequence"] = (
        "all three levels admitted; the section 7 solve order may proceed "
        "under the registered per-level stop order (F28G section 8 as amended "
        "by A1.3: L1 first, L2 only if L1 converges, L3 only if L2 does)"
        if admitted else
        "at least one level is NOT A RESULT; NO SOLVE IS LAUNCHED ON IT")
    return out


# =============================================================================
# THE RICHARDSON EXTRAPOLATE -- N-T8, AS F28G SECTION 7 CLAUSE 1 REGISTERS IT
# =============================================================================
# `f_ext = f_fine + (f_fine - f_med) / (r**p - 1)`.
#
# Written with `e21 = f_med - f_fine`, the CORRECT form is `f_fine - e21/den`.
# The DEFECT -- in `analyse_t1c.py:337`, `analyse_t3.py:384`,
# `analyse_t9a.py:241` and, independently written, `analyse_k0cg.py:107` and
# `K0cX/grid_convergence.py:106` -- is `f_fine + e21/den`, which REFLECTS THE
# LIMIT THROUGH THE FINEST VALUE onto the coarse side.  It has the right
# magnitude, the right units and a plausible position between the levels, and
# BOTH `p` AND `GCI` ARE SIGN-INDEPENDENT, so every neighbouring number stays
# correct and nothing on the printout looks wrong.
#
# The defective form is computed here ON PURPOSE, and it is never returned as
# the extrapolate.  It exists so the free identity `frozen + corrected ==
# 2 * f_fine` can be asserted on real data at no cost, and so the selftest can
# assert that a control which passes for both implementations is not a control.
def richardson(f_coarse, f_med, f_fine, r, p, form="corrected"):
    den = r ** p - 1.0
    if den == 0.0:
        refuse("r**p - 1 is exactly zero; no extrapolate exists")
    e21 = f_med - f_fine
    if form == "corrected":
        return f_fine - e21 / den
    if form == "frozen_sign_defect":
        return f_fine + e21 / den
    refuse("unknown Richardson form %r" % form)


def richardson_identity(f_coarse, f_med, f_fine, r, p):
    """N-T8's free check, which needs no synthetic case: the two forms satisfy
    `frozen + corrected == 2 * f_fine`.

    Asserted to one ulp rather than to bit equality, and the bit-equality
    result is REPORTED rather than required: `(a - x) + (a + x)` is exactly
    `2a` in real arithmetic and only usually so in floating point, and a
    comparator that refused on the last bit would be refusing on the rounding
    mode, not on the sign.
    """
    c = richardson(f_coarse, f_med, f_fine, r, p, "corrected")
    z = richardson(f_coarse, f_med, f_fine, r, p, "frozen_sign_defect")
    total, target = c + z, 2.0 * f_fine
    err = _rel(total, target)
    if err > 8.0 * sys.float_info.epsilon:
        refuse("N-T8's identity `frozen + corrected == 2 * f_fine` fails: "
               "%.17g + %.17g = %.17g against 2 * %.17g = %.17g, relative %.3e."
               "  The two forms differ only in the SIGN of `e21/den`, so a "
               "failure here means one of them is not the form it is labelled."
               % (z, c, total, f_fine, target, err))
    return {"corrected": c, "frozen_sign_defect_NOT_USED": z,
            "sum": total, "two_f_fine": target,
            "relative_error": err, "bit_exact": total == target,
            "authority": "N-T8; F28G section 7 clause 1"}


# =============================================================================
# THE ROACHE TRIPLE -- CLAUDE.md rule 5, PARENT SECTION 9.3, ORDER EXACTLY
# =============================================================================
def classify(f_coarse, f_med, f_fine, r):
    """State, observed order and GCI at a CONSTANT refinement ratio.

    The state vocabulary and its boundaries are the lab's shared ones
    (`analyse_t1c.py:321-337`): EXACT when `e21` is zero, OSCILLATORY when the
    two errors have opposite signs, DIVERGENT at `p <= 0`, STAGNANT below 0.5,
    CONVERGING otherwise.  Reimplemented rather than imported because the shared
    one is frozen at `R_REFINE = 1.6` and this ladder refines at 1.5 -- and
    because its `richardson` key carries the N-T8 defect and F28G section 7
    registers that it is not used.

    NO GCI IS RETURNED FOR ANY STATE BUT CONVERGING.  A CONVERGING triple has
    `e32/e21 > 0`, which is exactly strict monotonicity, so the registered
    refusal "no GCI is quoted when the three values are not monotone" is
    STRUCTURAL here -- and `assert_no_gci_without_monotone` checks it anyway,
    from the other side, because a structural guarantee that nothing tests is a
    belief.
    """
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    base = {"f_coarse": f_coarse, "f_med": f_med, "f_fine": f_fine,
            "e21": e21, "e32": e32, "r": r,
            "monotone": (e21 != 0.0 and e32 != 0.0
                         and (e32 > 0.0) == (e21 > 0.0))}
    if e21 == 0.0:
        return dict(base, state="EXACT")
    if e32 / e21 < 0.0:
        return dict(base, state="OSCILLATORY", ratio=e32 / e21)
    if e32 == 0.0:
        # `log(0)` is not an order.  The shared classifier reaches
        # `log(abs(0.0))` here and raises; refusing by name beats a traceback.
        return dict(base, state="STAGNANT", order=None,
                    why="e32 is exactly zero: the coarse and medium levels "
                        "agree bit for bit, so no order exists")
    p = math.log(abs(e32 / e21)) / math.log(r)
    if p <= 0.0:
        return dict(base, state="DIVERGENT", order=p)
    if p < STAGNANT_ORDER:
        return dict(base, state="STAGNANT", order=p)
    den = r ** p - 1.0
    if f_fine == 0.0:
        refuse("the fine-level value is exactly zero; a GCI normalised by it "
               "is undefined and this comparator does not invent one")
    return dict(base, state="CONVERGING", order=p,
                GCI_fine_pct=100.0 * FS * abs(e21 / f_fine) / den,
                Fs=FS,
                richardson_corrected=richardson(f_coarse, f_med, f_fine, r, p),
                richardson_identity=richardson_identity(
                    f_coarse, f_med, f_fine, r, p))


def observed_order_variable_r(f_coarse, f_med, f_fine, r21, r32):
    """The Celik non-constant-`r` observed order, by fixed point.

        p = |ln|e32/e21| + q(p)| / ln(r21),
        q(p) = ln((r21**p - s) / (r32**p - s)),  s = sign(e32/e21)

    Needed because the built ladder does NOT refine at exactly 1.5 in the cell
    count: F28G section 5.1 measures r32 = 1.5013.  Constant-`r` arithmetic on
    a non-constant-`r` ladder is a small error in `p` and this file prints both
    rather than choosing for the reader (CHOICE C6).  It REFUSES rather than
    returning a non-converged fixed point: an order that did not converge is
    not an order.
    """
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    if e21 == 0.0 or e32 == 0.0:
        return None
    s = 1.0 if (e32 / e21) > 0.0 else -1.0
    p, last = 2.0, None
    for _ in range(200):
        try:
            q = math.log((r21 ** p - s) / (r32 ** p - s))
        except (ValueError, ZeroDivisionError):
            return None
        nxt = abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
        if last is not None and abs(nxt - p) < 1e-13:
            return nxt
        last, p = p, nxt
    refuse("the Celik fixed point for the observed order did not converge in "
           "200 iterations (last two: %.12g, %.12g).  An order that did not "
           "converge is not an order and is not printed as one." % (last, p))


def assert_no_gci_without_monotone(g):
    """The registered refusal, checked from the OTHER side of the classifier.

    `classify` only attaches a GCI on CONVERGING and CONVERGING implies
    monotone, so this can only fire if the classifier is changed.  That is the
    point: it is the guard that catches a future edit, and it is the kind of
    check that can fail for a reason its author does not already know.
    """
    if "GCI_fine_pct" in g and not g["monotone"]:
        refuse("A GCI WAS COMPUTED ON A NON-MONOTONE TRIPLE (%r, %r, %r).  "
               "CLAUDE.md rule 5 and parent section 9.3 register the refusal in "
               "those words: no GCI is quoted when the three values are not "
               "monotone." % (g["f_coarse"], g["f_med"], g["f_fine"]))
    if g["state"] == "CONVERGING" and not g["monotone"]:
        refuse("a CONVERGING state on a non-monotone triple is a contradiction "
               "in the classifier")


def assert_one_way(before, after):
    """Rule 5's one-way property, PROVED on the row rather than promised.

    The gate may only turn a PASS or a GATE FAIL INTO NOT A RESULT.  It may
    never turn a NOT A RESULT into a PASS or a GATE FAIL.
    """
    if before == "NOT A RESULT" and after != "NOT A RESULT":
        refuse("THE GATE TURNED A `NOT A RESULT` INTO %r.  Rule 5 and parent "
               "section 9.3 register the property as one-way, in those terms."
               % after)
    if after not in VOCABULARY:
        refuse("verdict %r is not in the fixed vocabulary %s"
               % (after, list(VOCABULARY)))


# =============================================================================
# THE CRASH FILTER -- KEYED ON STACK FRAMES, NOT ON `FOAM FATAL`
# =============================================================================
_RE_FRAME = re.compile(r"^#\d+\s+", re.M)
_RE_FOAM_FATAL = re.compile(r"FOAM FATAL")


def crash_frames(log_path):
    """Count OpenFOAM signal-handler stack frames in a solver log.

    MEASURED ON THIS BOX, and the measurement is why the filter is shaped this
    way: on `verification/runs/FPE_DIAG_runs/HP1/log.simpleFoam`, a real
    floating-point-exception crash, `FOAM FATAL` occurs ZERO times while the
    frames are present.  A crash filter keyed on `FOAM FATAL` would miss every
    real crash on this box.  `FOAM FATAL` is COUNTED HERE ANYWAY and reported
    beside the frames -- it is a real signal for dictionary and boundary-
    condition errors, and dropping it because it missed one class would be the
    same mistake in the other direction.

    A crash is a FINDING until triage says otherwise (SUPERVISION_CHARTER
    section 3, check 2), so this returns evidence and the caller refuses; it
    does not silently downgrade a level.
    """
    if not os.path.isfile(log_path):
        refuse("no solver log at %s" % log_path)
    with open(log_path, errors="replace") as fh:
        text = fh.read()
    frames = _RE_FRAME.findall(text)
    return {"log": os.path.abspath(log_path),
            "stack_frames": len(frames),
            "foam_fatal_occurrences": len(_RE_FOAM_FATAL.findall(text)),
            "instrument": "stack frames `^#N `; `FOAM FATAL` measured at 0 "
                          "occurrences on a real FPE crash on this box and is "
                          "reported, never relied on alone",
            "crashed": len(frames) > 0}


# =============================================================================
# `T_total` -- CHOICE C1, DERIVED FROM PARENT SECTION 9.6 AND REFERRED UPWARD
# =============================================================================
def t_total(case, end_time, age_ref, delta_p, composition):
    """`T_total = T_duct + T_hub + T_disk`, every term positive when propulsive.

    NEITHER REGISTRATION DEFINES `T_total` OPERATIONALLY.  Parent section 9.3
    grades it, parent section 9.6 calls it "the force integration of section
    2.6", and the parent's installed comparator computes only `T_duct` and
    consumes it as the total on the section 6.3 EMPTY arm -- where the disk
    source is zero and the two coincide.  On a LOADED arm they do not.

    THE DERIVATION, from the frozen text rather than from preference.  Parent
    section 9.6 gates the momentum balance over a control volume bounded by a
    plane at `x = 3 D` and a farfield radius `R = 15 D`.  That volume encloses
    the duct, the centrebody AND the disk source, so the force it balances
    against is the sum of everything inside it.  Parent section 9.5's ideal
    `T_total / T_disk = 2 sigma` says the same: at sigma = 1 the duct carries
    as much thrust as the disk, which is a statement about a SUM.

    THE COMPOSITION MUST BE STATED BY THE CALLER (CLAUDE.md rule 14: a lesson
    is not applied until every call site asserts it).  There is no default.  A
    future caller cannot quietly regrade the case on a different quantity, and
    the supervisor's diff read sees the composition at every call site.

    `T_disk` is taken from the SOURCE ARM -- the momentum source the solver was
    actually handed, integrated over the actual cellZone on the actual built
    mesh and multiplied by the registered `WEDGE_SCALE`.  It is level-dependent
    and it is what the solver did.  The ANALYTIC arm `delta_p * A_disk` is
    computed beside it and the two must agree to the parent's own registered
    `TOL_C3` (0.5 %, section 6.2 control C3) -- so a `volumeMode` slip, a
    missing wedge factor or a wrong cellZone refuses rather than entering the
    observed order.
    """
    if composition != T_TOTAL_COMPOSITION:
        refuse("`T_total`'s composition must be stated verbatim as %r and this "
               "call site states %r.  Neither registration defines `T_total` "
               "operationally; the composition used here is DERIVED from parent "
               "section 9.6's control volume and is REFERRED UPWARD as a gap in "
               "the frozen text.  It is not a default and it may not become one."
               % (T_TOTAL_COMPOSITION, composition))
    duct = F28.total_thrust(case, end_time, age_ref)["T_duct"]

    row = F28.function_object_series(case, "forcesHub", "force.dat",
                                     end_time, age_ref)
    if row is None:
        refuse("no `forcesHub` output under %s/postProcessing.  `T_total` is "
               "the sum of the forces on everything inside parent section 9.6's "
               "control volume, and a missing term is DROPPED SILENTLY only if "
               "a comparator lets it be.  This one refuses." % case)
    hits = [c for c in row if c.startswith("total_x")]
    if len(hits) != 1:
        refuse("the x force column in `forcesHub` is %s, not exactly one; "
               "columns %s" % (hits, sorted(row)))
    hub = -row[hits[0]] * F28.WEDGE_SCALE

    src = F28.t_disk_from_source(case, delta_p)
    analytic = F28.t_disk_analytic(delta_p)
    if analytic == 0.0:
        disk, agree = 0.0, 0.0
    else:
        disk = src["T_disk_N"]
        agree = abs(disk - analytic) / abs(analytic)
        if agree > F28.TOL_C3:
            refuse("`T_disk` from the SOURCE the solver was handed is %.9g N "
                   "and the analytic `delta_p * A_disk` is %.9g N, %.4f %% "
                   "apart against the parent's registered control-C3 tolerance "
                   "of %.2f %%.  A disagreement here is a `volumeMode` slip, a "
                   "missing WEDGE_SCALE or a wrong cellZone, and it must not "
                   "enter an observed order."
                   % (disk, analytic, 100.0 * agree, 100.0 * F28.TOL_C3))
    return {"composition": T_TOTAL_COMPOSITION,
            "T_total_N": duct + hub + disk,
            "T_duct_N": duct, "T_hub_N": hub, "T_disk_N": disk,
            "T_disk_analytic_N": analytic,
            "T_disk_source_vs_analytic_rel": agree,
            "T_disk_tolerance": F28.TOL_C3,
            "sign_convention": "positive when propulsive (parent section 2.5); "
                               "every reported force is the -x component "
                               "times -1, times WEDGE_SCALE = %g"
                               % F28.WEDGE_SCALE,
            "derivation": "CHOICE C1 -- derived from parent section 9.6's "
                          "control volume; REFERRED UPWARD as a gap in the "
                          "frozen text, not repaired around in silence",
            "disk_source": {k: src[k] for k in
                            ("volumeMode", "source_Su_x_m_s2",
                             "zone_volume_measured_m3", "zone_volume_ratio")}}


def measure_level(case, end_time, rc, delta_p, level):
    """Everything one level contributes, with every registered refusal in
    front of it and in the registered order."""
    comp = F28.completion(case, os.path.join(case, "log.simpleFoam"),
                          end_time, rc)
    crash = crash_frames(comp["solver_log"])
    if crash["crashed"]:
        refuse("L%d's solver log %s carries %d stack frames.  A crash is a "
               "FINDING until triage says otherwise; it is not downgraded to a "
               "warning by an `End` line or by rc = 0, both of which this run "
               "has." % (level, crash["log"], crash["stack_frames"]))
    if end_time >= ITER_CAP:
        # Parent section 8, registered in those words: HIT CAP -> NOT A RESULT,
        # NEVER "CLOSE ENOUGH".  Raised as a refusal, not as a soft label.
        refuse("L%d ran to the registered iteration cap of %d.  Parent section "
               "8: HIT CAP -> NOT A RESULT, NEVER \"CLOSE ENOUGH\", and F28G "
               "section 8's stop order stops the ladder there."
               % (level, ITER_CAP))
    age_ref = comp["age_ref"]
    tt = t_total(case, end_time, age_ref, delta_p, T_TOTAL_COMPOSITION)
    stat = F28.thrust_stationarity(case, end_time, age_ref)
    # The sector-frame proof is against `T_duct`, because that is the quantity
    # the stationarity column produces under one transformation.  Running it on
    # `T_total` would compare the windowed duct force against a sum and fail
    # for a reason that is arithmetic, not framing.
    frame = F28.assert_stationarity_frame(stat, tt["T_duct_N"])
    plant = F28.plant_into_stationarity_window(case, end_time, age_ref)
    return {"level": level, "case": os.path.abspath(case),
            "completion": comp, "crash_filter": crash,
            "T_total": tt, "stationarity": stat,
            "sector_frame_proof": frame,
            "rule_3_plant_on_the_window": plant,
            "iteratively_converged": bool(stat["pass"])}


def precondition_iterative_vs_discretisation(levels):
    """F28G section 7 clause 4, A REGISTERED PRECONDITION AND NOT A DIAGNOSTIC.

    "the iterative change in `T_total` over the stationarity window must be at
    least 10x smaller than the difference between consecutive mesh levels, on
    every level.  Failing it, the observed order is noise and the row is
    NOT A RESULT" -- registered in those words, before any solve.

    TWO THINGS THE FROZEN TEXT LEAVES TO THE IMPLEMENTATION, both resolved in
    the stricter direction and both printed:

    (i) WHICH consecutive difference a given level is measured against.  CHOICE
        C5: every level is measured against the SMALLER of the two, which is
        the hardest bar available.  The per-level-adjacent reading is printed
        beside it, so a row that passes one and fails the other is visible.
    (ii) THE FRAME.  The stationarity `ptp` is in 5-degree SECTOR newtons
        (parent Addendum 3 section 5) and `T_total` is a FULL-ANNULUS force.
        Comparing them unconverted would be wrong BY A FACTOR OF 72 in the
        PERMISSIVE direction -- the same slip Addendum 3 section 5 exists to
        foreclose, arriving by a different route.  `ptp` is multiplied by
        `WEDGE_SCALE` here, after `assert_stationarity_frame` has PROVED the
        reader's frame by identity against the graded column.
    """
    f = {lv: levels[lv]["T_total"]["T_total_N"] for lv in (1, 2, 3)}
    d21 = abs(f[2] - f[1])
    d32 = abs(f[3] - f[2])
    d_min = min(d21, d32)
    rows, ok = [], True
    for lv in (1, 2, 3):
        ptp_sector = levels[lv]["stationarity"]["ptp_N"]
        ptp_full = ptp_sector * F28.WEDGE_SCALE
        adjacent = d21 if lv == 1 else (d32 if lv == 3 else min(d21, d32))
        strict_ok = ptp_full * PRECONDITION_RATIO <= d_min
        adj_ok = ptp_full * PRECONDITION_RATIO <= adjacent
        ok = ok and strict_ok
        rows.append({"level": lv,
                     "iterative_ptp_sector_N": ptp_sector,
                     "iterative_ptp_full_annulus_N": ptp_full,
                     "frame_note": "ptp is in 5-degree SECTOR newtons and is "
                                   "multiplied by WEDGE_SCALE = %g to meet "
                                   "T_total's full-annulus frame; the frame is "
                                   "PROVED by identity, not asserted"
                                   % F28.WEDGE_SCALE,
                     "level_difference_strict_N": d_min,
                     "level_difference_adjacent_N": adjacent,
                     "ratio_strict": (d_min / ptp_full) if ptp_full else None,
                     "ratio_adjacent": (adjacent / ptp_full) if ptp_full else None,
                     "required_ratio": PRECONDITION_RATIO,
                     "pass_strict_reading": strict_ok,
                     "pass_adjacent_reading": adj_ok})
    return {"clause": "F28G section 7 clause 4 (Sanaa section 0 step 2)",
            "reading": "CHOICE C5 -- every level against the SMALLER "
                       "consecutive difference; the adjacent reading printed "
                       "beside it",
            "T_total_by_level_N": f, "delta21_N": d21, "delta32_N": d32,
            "rows": rows, "pass": ok,
            "on_failure": "the observed order is noise and the row is "
                          "NOT A RESULT -- registered in those words"}


def grade(spec):
    """F28G section 7 / parent section 9.3, in rule 5's order, one-way."""
    delta_p = float(spec.get("delta_p", 1000.0))
    end_time = spec["endTime"]
    if float(spec.get("U_inf", 20.0)) != 20.0 or delta_p != 1000.0:
        refuse("F28G section 7 registers the study at delta_p = 1000 Pa and "
               "U_inf = 20 m/s and at no other state.  This spec says "
               "delta_p = %r, U_inf = %r." % (delta_p, spec.get("U_inf")))
    levels = {}
    for lv in (1, 2, 3):
        key = "L%d" % lv
        if key not in spec.get("cases", {}):
            refuse("no %r in the grading spec.  A Roache triple has three "
                   "levels; two is not a triple and no order exists." % key)
        levels[lv] = measure_level(spec["cases"][key], end_time,
                                   spec["rc"][key], delta_p, lv)

    n1 = spec.get("cells", {}).get("L1")
    n2 = spec.get("cells", {}).get("L2")
    n3 = spec.get("cells", {}).get("L3")
    if not (n1 and n2 and n3):
        refuse("the grading spec must carry the three cell counts; the "
               "measured refinement ratios (CHOICE C6, the second of rule 5's "
               "`both orders`) cannot be formed without them")
    # A wedge one cell thick: cells scale as the SQUARE of the linear
    # refinement, so h ~ N**(-1/2).  Stated because a 3D reading would give
    # N**(-1/3) and a silently wrong exponent moves every order.
    r21_meas = math.sqrt(float(n3) / float(n2))    # h_med / h_fine
    r32_meas = math.sqrt(float(n2) / float(n1))    # h_coarse / h_med

    fc = levels[1]["T_total"]["T_total_N"]
    fm = levels[2]["T_total"]["T_total_N"]
    ff = levels[3]["T_total"]["T_total_N"]

    g_nom = classify(fc, fm, ff, R_LADDER)
    assert_no_gci_without_monotone(g_nom)
    p_meas = observed_order_variable_r(fc, fm, ff, r21_meas, r32_meas)

    out = {"gate": "F28G section 7 -- ROACHE TRIPLE ON `T_total`",
           "registration": "verification/campaign/"
                           "F28G_GRID_CONVERGENCE_PREREGISTRATION.md; bands "
                           "carried unchanged from parent section 9.3",
           "state_point": {"delta_p_Pa": delta_p, "U_inf_m_s": 20.0,
                           "sigma": 1.0},
           "graded_quantity": "T_total = " + T_TOTAL_COMPOSITION,
           "value_triple_N": {"L1": fc, "L2": fm, "L3": ff},
           "component_triples_N": {
               "T_duct": {("L%d" % lv): levels[lv]["T_total"]["T_duct_N"]
                          for lv in (1, 2, 3)},
               "T_hub": {("L%d" % lv): levels[lv]["T_total"]["T_hub_N"]
                         for lv in (1, 2, 3)},
               "T_disk": {("L%d" % lv): levels[lv]["T_total"]["T_disk_N"]
                          for lv in (1, 2, 3)}},
           "triple_nominal_r": g_nom,
           "refinement_ratios": {"nominal": R_LADDER,
                                 "measured_r21": r21_meas,
                                 "measured_r32": r32_meas,
                                 "basis": "cells ~ h**-2 on a wedge one cell "
                                          "thick"},
           "observed_order_nominal": g_nom.get("order"),
           "observed_order_measured_celik": p_meas,
           "bands": {"p": list(P_BAND), "GCI_fine_pct_max": GCI_FINE_MAX_PCT,
                     "Fs": FS},
           "levels": levels,
           "N_T2_caveat": "a CONVERGING triple can arm a band NARROWER than "
                          "the finest level's actual error; the GCI below is a "
                          "grid-convergence index and is NEVER an error bar on "
                          "the physics (F28G section 7 clause 2)",
           "N_T7_disclosure": None}

    # ---- RULE 5's ORDER, EXACTLY, AND ONE-WAY -----------------------------
    # Clause (1) comes FIRST and is evaluated before any triple is looked at.
    unconverged = [lv for lv in (1, 2, 3)
                   if not levels[lv]["iteratively_converged"]]
    pre = precondition_iterative_vs_discretisation(levels)
    out["precondition_clause_4"] = pre

    v = verdict_from_triple(fc, fm, ff, unconverged, pre["pass"],
                            r21_meas, r32_meas)
    out.update(v)
    out["rule_5_order"] = RULE_5_ORDER
    return out


RULE_5_ORDER = (
    "(1) any level not iteratively converged or not plateaued -> NOT A "
    "RESULT; (2) triple DIVERGENT/STAGNANT/OSCILLATORY/EXACT -> NOT A "
    "RESULT with the value, both triples and both orders printed beside "
    "it; (3) CONVERGING -> PASS inside the band else GATE FAIL, GCI "
    "printed.  ONE-WAY: the gate can only turn a PASS or GATE FAIL INTO "
    "NOT A RESULT.")


def verdict_from_triple(fc, fm, ff, unconverged, precondition_pass,
                        r21_meas, r32_meas):
    """Rule 5's ordering as a PURE FUNCTION of the numbers.

    Separated from `grade` so the ordering can be driven directly by the
    selftest with hand-made inputs -- every branch, in both directions -- on a
    box where no F28G solve exists and none may be launched.  A verdict path
    that has never executed is not a verdict path.
    """
    g_nom = classify(fc, fm, ff, R_LADDER)
    assert_no_gci_without_monotone(g_nom)
    p_meas = observed_order_variable_r(fc, fm, ff, r21_meas, r32_meas)
    out = {"triple_nominal_r": g_nom,
           "observed_order_nominal": g_nom.get("order"),
           "observed_order_measured_celik": p_meas,
           "N_T7_disclosure": None}
    verdict, why = None, None
    if unconverged:
        verdict = "NOT A RESULT"
        why = ("rule 5 clause (1): level(s) %s are not iteratively converged "
               "against parent section 8's criteria as floored by Addendum 3"
               % unconverged)
    elif not precondition_pass:
        verdict = "NOT A RESULT"
        why = ("F28G section 7 clause 4: the iterative change in `T_total` is "
               "not at least %gx smaller than the difference between "
               "consecutive mesh levels on every level, so the observed order "
               "is noise" % PRECONDITION_RATIO)
    elif g_nom["state"] != "CONVERGING":
        verdict = "NOT A RESULT"
        why = ("rule 5 clause (2): the grid triple is %s" % g_nom["state"])
    else:
        # Clause (3).  Only CONVERGING reaches a band.
        p = g_nom["order"]
        gci = g_nom["GCI_fine_pct"]
        inside = (P_BAND[0] <= p <= P_BAND[1]) and gci < GCI_FINE_MAX_PCT
        provisional = "PASS" if inside else "GATE FAIL"
        verdict, why = provisional, (
            "rule 5 clause (3): CONVERGING, p = %.6f in [%g, %g] and "
            "GCI_fine = %.6f %% < %g %%" % (p, P_BAND[0], P_BAND[1], gci,
                                            GCI_FINE_MAX_PCT)
            if inside else
            "rule 5 clause (3): CONVERGING but p = %.6f against [%g, %g] and "
            "GCI_fine = %.6f %% against < %g %%" % (p, P_BAND[0], P_BAND[1],
                                                    gci, GCI_FINE_MAX_PCT))
        # CHOICE C6, a ONE-WAY strengthening and therefore legal under rule 5:
        # if the two orders disagree about the band, the order is not
        # established by the data.
        if p_meas is not None:
            in_nom = P_BAND[0] <= p <= P_BAND[1]
            in_meas = P_BAND[0] <= p_meas <= P_BAND[1]
            if in_nom != in_meas:
                before = verdict
                verdict = "NOT A RESULT"
                why = ("CHOICE C6: the observed order is %.6f at the "
                       "registered nominal r = %g and %.6f at the MEASURED "
                       "ratios r21 = %.6f / r32 = %.6f, and the two fall on "
                       "OPPOSITE sides of the band [%g, %g].  An order whose "
                       "verdict depends on which refinement ratio you believe "
                       "is not established by the data.  This turns a %r into "
                       "NOT A RESULT and is therefore a legal one-way "
                       "strengthening."
                       % (p, R_LADDER, p_meas, r21_meas, r32_meas,
                          P_BAND[0], P_BAND[1], before))
                assert_one_way(before, verdict)
        # N-T7: a CONVERGING triple is a STEP-RATIO test.
        if abs(ff - fm) < abs(fc - ff):
            out["N_T7_disclosure"] = (
                "the fine-level deviation |L3 - L2| = %.9g N is SMALLER than "
                "the coarse-to-fine drift |L1 - L3| = %.9g N.  A CONVERGING "
                "triple is a step-ratio test, and a fine-level deviation "
                "smaller than the coarse-to-fine drift is a passing value on a "
                "divergent triple (N-T7).  Stated beside the verdict, as F28G "
                "section 7 clause 3 registers."
                % (abs(ff - fm), abs(fc - ff)))

    assert_one_way(verdict, verdict)
    out["verdict"] = verdict
    out["why"] = why
    if verdict == "NOT A RESULT":
        # Rule 5 clause (2) requires the value, BOTH triples and BOTH orders
        # printed beside a non-CONVERGING row.  The two triples printed are the
        # value triple and the ERROR triple; the two orders are the nominal-r
        # order and the Celik measured-r order (CHOICE C6).
        out["printed_beside_the_verdict"] = {
            "value_fine_N": ff,
            "value_triple_N": [fc, fm, ff],
            "error_triple_N": {"e32": g_nom["e32"], "e21": g_nom["e21"],
                               "ratio_e32_over_e21":
                                   (g_nom["e32"] / g_nom["e21"])
                                   if g_nom["e21"] else None},
            "order_nominal_r": g_nom.get("order"),
            "order_measured_r_celik": p_meas,
            "GCI_quoted": False,
            "why_no_GCI": "no GCI is quoted when the three values are not "
                          "monotone, and none is quoted on a non-CONVERGING "
                          "row at all (rule 5; parent section 9.3)"}
    return out


# =============================================================================
# THE SELFTEST -- EVERY FILTER SHOWN BOTH WAYS
# =============================================================================
# A filter never shown a real failure is not a detector whatever it returns on
# good input; one never shown good input is an alarm, not a filter.  Every limb
# below therefore has a positive and a negative side, and the suite is judged
# on EXIT CODE, never on what reached stdout -- a tool piped through a `grep`
# whose pattern the refusal line did not match has already, on this box,
# produced an empty commit advertising a fix that was never in the file.
class Suite(object):
    def __init__(self):
        self.rows = []
        self.ok = True

    def check(self, name, condition, detail=""):
        good = bool(condition)
        self.ok = self.ok and good
        self.rows.append({"limb": name, "result": "ok" if good else "FAILED",
                          "detail": detail})
        return good

    def expect_refusal(self, name, fn, want_substring=None):
        try:
            fn()
        except Refusal as e:
            msg = str(e)
            if want_substring and want_substring not in msg:
                return self.check(name, False,
                                  "refused, but for the wrong reason: %s"
                                  % msg[:240])
            return self.check(name, True, "refused: %s" % msg.split(".")[0][:160])
        except SystemExit as e:
            return self.check(name, True, "refused with exit %r" % e.code)
        return self.check(name, False, "DID NOT REFUSE -- a filter that never "
                                       "fires on a real failure is not a filter")

    def report(self, title):
        n_ok = sum(1 for r in self.rows if r["result"] == "ok")
        return {"suite": title, "limbs_run": len(self.rows), "limbs_ok": n_ok,
                "limbs_failed": len(self.rows) - n_ok,
                "pass": self.ok, "rows": self.rows}


def selftest_richardson():
    """F28G section 7 clause 1 -- N-T8's standing rule, adopted as a refusal.

    A VALUE-checking control, not a key-presence one.  The synthetic triple is
    `f_k = f_ex + A * (r**p)**k` with `k = 0` the FINEST, so its limit `f_ex` is
    known BY CONSTRUCTION and the correct extrapolate must reproduce it to
    1e-12 relative.  Two sign cases are run, because a control that only ever
    sees a positive limit cannot see a sign defect that is a reflection.
    """
    s = Suite()
    for f_ex, A, p, r in ((-37.15, 0.83, 1.9, 1.5),
                          (+41.02, -1.27, 2.1, 1.5)):
        rp = r ** p
        ff = f_ex + A
        fm = f_ex + A * rp
        fc = f_ex + A * rp * rp
        # The VALUE limbs run FIRST, on `richardson` called directly.  If they
        # ran after `classify` they would never execute against a defective
        # implementation: `classify` embeds the identity assertion, which
        # refuses first and would abort the suite before the value was ever
        # compared.  A control that is unreachable on the failure it exists to
        # catch is not a control.
        p_direct = math.log(abs((fc - fm) / (fm - ff))) / math.log(r)
        corrected = richardson(fc, fm, ff, r, p_direct, "corrected")
        frozen = richardson(fc, fm, ff, r, p_direct, "frozen_sign_defect")
        e_corr = _rel(corrected, f_ex)
        e_froz = _rel(frozen, f_ex)
        s.check("power law %.2f: CORRECTED extrapolate hits the known limit "
                "to 1e-12 relative" % f_ex, e_corr <= 1e-12,
                "corrected %.17g vs f_ex %.17g, relative %.3e"
                % (corrected, f_ex, e_corr))
        # THE DISTINGUISHABILITY ASSERTION.  A control that passes for the
        # right and the wrong implementation alike is not a control, and
        # N-T8 records that a key-presence check is exactly such a control --
        # it is what let the defect survive every run of analyse_t1c.py and
        # analyse_t3.py.
        s.check("power law %.2f: the DEFECTIVE form FAILS the same assertion "
                "(distinguishability)" % f_ex, e_froz > 1e-12,
                "frozen(defective) %.17g vs f_ex %.17g, relative %.3e -- the "
                "defect reflects the limit through the finest value, so it "
                "lands at f_ex + 2A = %.17g"
                % (frozen, f_ex, e_froz, f_ex + 2.0 * A))
        try:
            g = classify(fc, fm, ff, r)
        except Refusal as exc:
            s.check("power law %.2f: `classify` returns a triple" % f_ex,
                    False, "refused: %s" % str(exc)[:200])
            continue
        s.check("power law %.2f: state is CONVERGING" % f_ex,
                g["state"] == "CONVERGING", g["state"])
        s.check("power law %.2f: observed order recovers p to 1e-12" % f_ex,
                _rel(g["order"], p) <= 1e-12,
                "p_recovered = %.17g against %.17g" % (g["order"], p))
        s.check("power law %.2f: the defect is INVISIBLE to `p` and to `GCI` "
                "-- both are computed from the triple alone and take the same "
                "value whichever extrapolate is printed" % f_ex,
                "GCI_fine_pct" in g and g["order"] is not None,
                "p = %.12g, GCI_fine = %.12g %%; neither is a function of the "
                "extrapolate, which is why nothing neighbouring can catch the "
                "sign" % (g["order"], g["GCI_fine_pct"]))
        ident = richardson_identity(fc, fm, ff, r, g["order"])
        s.check("power law %.2f: free identity `frozen + corrected == "
                "2 * f_fine`" % f_ex, ident["relative_error"] <= 8e-16,
                "sum %.17g vs %.17g, relative %.3e, bit-exact %r"
                % (ident["sum"], ident["two_f_fine"],
                   ident["relative_error"], ident["bit_exact"]))
        # A KEY-PRESENCE CHECK IS SHOWN INSUFFICIENT, by construction rather
        # than by assertion: both forms return a finite float, so a check that
        # only asks "is the key there and is it a number" passes for both.
        s.check("power law %.2f: a KEY-PRESENCE check would pass for BOTH "
                "forms, which is why F28G section 7 clause 1 registers it as "
                "insufficient" % f_ex,
                all(isinstance(v, float) and math.isfinite(v)
                    for v in (corrected, frozen)),
                "both forms are finite floats of the same magnitude class")

    # The identity guard must itself be able to refuse.  Shown by handing it a
    # pair that does not satisfy it -- i.e. by breaking the identity on purpose.
    def _broken_identity():
        c, z, ffine = 1.0, 1.0, 10.0
        total, target = c + z, 2.0 * ffine
        if _rel(total, target) > 8.0 * sys.float_info.epsilon:
            refuse("N-T8's identity `frozen + corrected == 2 * f_fine` fails")
    s.expect_refusal("the identity guard is able to refuse", _broken_identity,
                     "identity")
    return s


def selftest_triple():
    """Rule 5's ordering, its one-way property, and the monotonicity refusal.

    Every synthetic triple below is DERIVED BY HAND, one per alternative,
    rather than generated from the pattern being tested.  A control derived
    from the thing it checks has been pre-agreed with it.
    """
    s = Suite()
    r = R_LADDER
    # Hand-built triples.  `x` is the fine value in every case.
    x = -40.0
    # DERIVED BY HAND, one per alternative.  `e21 = f_med - f_fine`,
    # `e32 = f_coarse - f_med`, `p = ln|e32/e21| / ln 1.5`, and each row's
    # step ratio is chosen to land in exactly one branch:
    #   ratio 2.25 -> p = 2.000  (CONVERGING, inside the registered band)
    #   ratio 3.00 -> p = 2.710  (CONVERGING, OUTSIDE the band -> GATE FAIL)
    #   ratio 0.25 -> p = -3.419 (DIVERGENT)
    #   ratio 1.10 -> p =  0.235 (STAGNANT, below the 0.5 boundary)
    #   opposite signs             (OSCILLATORY)
    #   e21 == 0                   (EXACT)
    cases = [
        # name,                          coarse,      med,      fine, state
        ("CONVERGING p=2, in band", x - 0.8125, x - 0.25, x, "CONVERGING"),
        ("CONVERGING p=2.71, out of band", x - 1.0, x - 0.25, x, "CONVERGING"),
        ("DIVERGENT (steps grow)", x - 1.25, x - 1.0, x, "DIVERGENT"),
        ("STAGNANT (steps barely shrink)", x - 2.1, x - 1.0, x, "STAGNANT"),
        ("OSCILLATORY (sign flip)", x + 0.5, x - 0.5, x, "OSCILLATORY"),
        ("EXACT (med == fine)", x - 0.5, x, x, "EXACT"),
    ]
    for name, fc, fm, ff, want in cases:
        g = classify(fc, fm, ff, r)
        s.check("classifier: %s" % name, g["state"] == want,
                "state %s (p = %r)" % (g["state"], g.get("order")))
        assert_no_gci_without_monotone(g)
        if want != "CONVERGING":
            s.check("no GCI on a %s triple" % want, "GCI_fine_pct" not in g,
                    "keys: %s" % sorted(g))
            s.check("no Richardson extrapolate on a %s triple" % want,
                    "richardson_corrected" not in g, "keys: %s" % sorted(g))
        else:
            s.check("GCI present and monotone on CONVERGING",
                    "GCI_fine_pct" in g and g["monotone"],
                    "GCI = %.6f %%" % g["GCI_fine_pct"])

    # The monotonicity refusal must be able to fire.  Handed a hand-made
    # dictionary that carries a GCI on a non-monotone triple -- the exact shape
    # a future edit to `classify` would produce.
    s.expect_refusal(
        "the no-GCI-without-monotone guard fires",
        lambda: assert_no_gci_without_monotone(
            {"GCI_fine_pct": 1.0, "monotone": False, "state": "OSCILLATORY",
             "f_coarse": 1.0, "f_med": 2.0, "f_fine": 1.5}),
        "NON-MONOTONE")
    # The one-way property must be able to fire.
    s.expect_refusal("the one-way guard fires on NOT A RESULT -> PASS",
                     lambda: assert_one_way("NOT A RESULT", "PASS"),
                     "one-way")
    s.check("the one-way guard permits PASS -> NOT A RESULT",
            assert_one_way("PASS", "NOT A RESULT") is None,
            "the gate may only tighten")
    s.expect_refusal("a verdict outside the fixed vocabulary refuses",
                     lambda: assert_one_way("PASS", "roughly converged"),
                     "fixed vocabulary")

    # The Celik variable-r order must reproduce the constant-r order when the
    # two ratios are equal -- a check with a known answer that is NOT the
    # implementation's own output.
    fc, fm, ff = x - 1.0, x - 0.25, x
    g = classify(fc, fm, ff, r)
    p_var = observed_order_variable_r(fc, fm, ff, r, r)
    s.check("Celik variable-r order collapses to the constant-r order at "
            "r21 == r32", _rel(p_var, g["order"]) <= 1e-9,
            "%.12g vs %.12g" % (p_var, g["order"]))
    # And it must MOVE when the ratios differ, or it is not reading them.
    p_var2 = observed_order_variable_r(fc, fm, ff, 1.5013, 1.5)
    s.check("Celik variable-r order MOVES when the measured ratios differ",
            abs(p_var2 - g["order"]) > 1e-6,
            "%.12g vs %.12g" % (p_var2, g["order"]))
    return s


SYNTHETIC_CHECKMESH = """\
Exec   : checkMesh -allGeometry -allTopology -writeAllFields
Checking topology...
    cells:            35544
Checking geometry...
 ***High aspect ratio cells found, Max aspect ratio: 53458.4, number of cells 2789
    Min volume = 1.40612e-16. Max volume = 0.0468706.  Total volume = 5.48464.
    Mesh non-orthogonality Max: 57.8773 average: 9.96767
    Non-orthogonality check OK.
    Max skewness = 1.24132 OK.
    Cell determinant (wellposedness) : minimum: 6.99786e-10 average: 0.118179
 ***Cells with small determinant (< 0.001) found, number of cells: 9817

Failed 2 mesh checks.

End
"""


def selftest_checkmesh(tmp):
    """The `checkMesh` reader and M1/M2/M3, on planted text ON DISK.

    Run on a COPY.  The plant into the REAL artifact is the production path and
    runs inside `--mesh-gate`; a selftest does not need to write to evidence to
    prove the machinery works, and evidence is not a test fixture.
    """
    s = Suite()
    path = os.path.join(tmp, "log.checkMesh")
    with open(path, "w") as fh:
        fh.write(SYNTHETIC_CHECKMESH)

    cm = read_checkmesh(path)
    v = m1_m2_m3(cm)
    s.check("baseline (the negative limb): the admissible synthetic mesh is "
            "admitted on M1/M2/M3", all(c["pass"] for c in v),
            "nonortho %.4f, skewness %.5f, min volume %.6g"
            % (cm["nonortho_max_deg"], cm["skewness_max"],
               cm["min_cell_volume_m3"]))
    s.check("the reported severe-face count is a ZERO from a line that is "
            "absent", cm["severe_nonortho_faces"] == 0
            and not cm["severe_line_present"], "0, line absent")
    s.check("aspect ratio is read and recorded",
            cm["aspect_ratio_max"] == 53458.4 and not cm["aspect_ratio_is_gated"],
            "53458.4, gated = False")
    s.check("the reader returns NO verdict string",
            cm["verdict_strings_read"] == [], "[]")

    cert = certify_checkmesh_reader(path)
    s.check("rule 3: all six certification limbs fired on the reader",
            cert["n_limbs"] == 6 and all(l.get("fired") for l in cert["limbs"]),
            "%d limbs" % cert["n_limbs"])
    after = read_checkmesh(path)
    s.check("the negative limb: after restore the reader reproduces the "
            "unplanted values",
            (after["nonortho_max_deg"] == cm["nonortho_max_deg"]
             and after["skewness_max"] == cm["skewness_max"]
             and after["severe_nonortho_faces"] == 0
             and after["sha256"] == cm["sha256"]),
            "sha256 %s unchanged" % after["sha256"][:16])

    # THE TRAP THE STANDARD NAMES, run explicitly as its own limb: a log whose
    # VERDICT STRINGS SAY THE MESH IS FINE while the reported maximum says it
    # is not.  This is the shape a sister lane MEASURED on this box at 88.93
    # degrees.  The gate must reject on the maximum and be untouched by the
    # strings.
    liar = os.path.join(tmp, "log.checkMesh.liar")
    text = (SYNTHETIC_CHECKMESH
            .replace("Mesh non-orthogonality Max: 57.8773",
                     "Mesh non-orthogonality Max: 88.93")
            .replace("Failed 2 mesh checks.", "Mesh OK."))
    with open(liar, "w") as fh:
        fh.write(text)
    lv = m1_m2_m3(read_checkmesh(liar))
    s.check("MESH_STANDARD 14.4: a log reading `Non-orthogonality check OK.` "
            "AND `Mesh OK.` at a reported maximum of 88.93 is REJECTED by M1",
            not lv[0]["pass"],
            "M1 value %.4f against threshold %g"
            % (lv[0]["value"], M1_NONORTHO_MAX_DEG))

    # An absent maximum must refuse rather than fall back to the strings.
    blind = os.path.join(tmp, "log.checkMesh.nomax")
    with open(blind, "w") as fh:
        fh.write(SYNTHETIC_CHECKMESH.replace(
            "    Mesh non-orthogonality Max: 57.8773 average: 9.96767\n", ""))
    s.expect_refusal("a log with NO reported maximum refuses rather than "
                     "reading `Non-orthogonality check OK.`",
                     lambda: read_checkmesh(blind), "reported maximum")

    # An absent aspect-ratio line makes the RECORD INCOMPLETE (MESH_STANDARD
    # 11.4) -- the opposite direction from limb (e), where a value of 1e9 is
    # admitted.  The two together are the whole of section 3.3's rule.
    noar = os.path.join(tmp, "log.checkMesh.noar")
    with open(noar, "w") as fh:
        fh.write(SYNTHETIC_CHECKMESH.replace(
            " ***High aspect ratio cells found, Max aspect ratio: 53458.4, "
            "number of cells 2789\n", ""))
    st = read_checkmesh(noar)
    s.check("MESH_STANDARD 11.4: an ABSENT aspect ratio is recorded as "
            "ASPECT_RATIO_LINE_ABSENT (what makes a record incomplete is the "
            "absence of the number, never its size)",
            "ASPECT_RATIO_LINE_ABSENT" in st["statuses"], str(st["statuses"]))

    # A concatenated log must refuse rather than pick.
    twice = os.path.join(tmp, "log.checkMesh.twice")
    with open(twice, "w") as fh:
        fh.write(SYNTHETIC_CHECKMESH + SYNTHETIC_CHECKMESH)
    s.expect_refusal("a concatenated checkMesh log refuses rather than "
                     "choosing which run is graded",
                     lambda: read_checkmesh(twice), "appended to")

    # The severe-count / maximum contradiction.
    contra = os.path.join(tmp, "log.checkMesh.contra")
    with open(contra, "w") as fh:
        fh.write(SYNTHETIC_CHECKMESH.replace(
            "    Non-orthogonality check OK.",
            " ***Number of severely non-orthogonal (> 70 degrees) faces: 12.\n"
            "    Non-orthogonality check OK."))
    s.expect_refusal("a log reporting faces above 70 degrees with a maximum of "
                     "57.9 refuses -- the two readings cannot describe one mesh",
                     lambda: m1_m2_m3(read_checkmesh(contra)), "cannot both")
    return s


def selftest_grading_readback(tmp):
    """M4/M6's recomputation from the written dict, both ways."""
    s = Suite()
    good = os.path.join(tmp, "blockMeshDict.good")
    # ONE block, ONE two-segment radial direction, hand-computed:
    # 32 cells expanding at E = 810.0347835 -> q = E**(1/31) = 1.2411455,
    # which is F28G section 5.3's OWN read-back value for `ROW_I` q1 at L1
    # (1.24115).  The control's expected value therefore comes from the
    # REGISTRATION, not from this reader's own output.
    body = ("hex (0 1 2 4 0 1 3 5) (40 48 1) simpleGrading "
            "(0.000854602613 ( (0.49 0.6666666667 810.0347835) "
            "(0.51 0.3333333333 0.0509187762) ) 1)\n")
    with open(good, "w") as fh:
        fh.write("blocks\n(\n    " + body + ");\n")
    g = grading_readback(good)
    s.check("M4: the per-cell ratio recomputed from the written dict "
            "reproduces F28G section 5.3's own read-back for ROW_I q1 "
            "(1.24115)", _rel(g["worst_per_cell_ratio"], 1.24115) < 1e-5,
            "%.9f" % g["worst_per_cell_ratio"])
    s.check("M4: that ratio is inside the L1 cap of %.5f" % growth_cap(1),
            g["worst_per_cell_ratio"] <= growth_cap(1),
            "%.9f <= %.9f" % (g["worst_per_cell_ratio"], growth_cap(1)))
    s.check("M6: the junction deviation is convention-free "
            "(max(jj, 1/jj)) and is inside the strict band",
            g["worst_junction_deviation"] <= M6_JUNCTION_BAND_STRICT[1],
            "jump %.9f, deviation %.9f"
            % (g["worst_junction_jump"], g["worst_junction_deviation"]))

    # A dict whose grading BREAKS the cap must be seen to break it.
    bad = os.path.join(tmp, "blockMeshDict.bad")
    # 11 cells at E = 10 -> q = 10**(1/10) = 1.2589 > 1.25 at L1.
    with open(bad, "w") as fh:
        fh.write("blocks\n(\n    hex (0 1 2 4 0 1 3 5) (11 1 1) "
                 "simpleGrading (10 1 1)\n);\n")
    gb = grading_readback(bad)
    s.check("M4 SEES a per-cell ratio above the cap (10**(1/10) = 1.25893)",
            gb["worst_per_cell_ratio"] > growth_cap(1),
            "%.9f > %.9f" % (gb["worst_per_cell_ratio"], growth_cap(1)))
    # A spec whose fractions do not close must refuse.
    broken = os.path.join(tmp, "blockMeshDict.broken")
    with open(broken, "w") as fh:
        fh.write("blocks\n(\n    hex (0 1 2 4 0 1 3 5) (40 48 1) "
                 "simpleGrading (1 ( (0.49 0.5 2) (0.51 0.3 3) ) 1)\n);\n")
    s.expect_refusal("a grading spec whose fractions do not sum to 1 refuses",
                     lambda: grading_readback(broken), "does not close")
    s.expect_refusal("a dict with no `hex` entries refuses",
                     lambda: grading_readback(os.path.join(tmp, "empty.dict"))
                     if os.path.exists(os.path.join(tmp, "empty.dict"))
                     else grading_readback(os.path.join(tmp, "missing.dict")),
                     "no blockMeshDict")
    return s


def _synthetic_ladder(nx_c1=(24, 36, 54), rho=(1.06, 1.06, 1.06),
                      junction=(1.0281, 1.0281, 1.0281)):
    """A hand-built three-level ladder for M4/M5/M6, with every quantity a
    dial the selftest can turn one at a time."""
    levels = {}
    for i, lv in enumerate((1, 2, 3)):
        cap = growth_cap(lv)
        levels[lv] = {
            "diag": {"level": lv, "level_scale_from_L1": LEVEL_SCALE[lv],
                     "growth_cap_per_cell": cap, "growth_cap_junction": cap,
                     "mesh_script_sha256": "0" * 64,
                     "blockMeshDict_sha256": "1" * 64,
                     "nx": {"c1": nx_c1[i]},
                     "nr": {"I": (48, 72, 108)[i]},
                     "y_first_requested_m": (1.0e-5, 6.667e-6, 4.444e-6)[i],
                     "axial": {"c1": {"split_rho": rho[i], "q": [1.2]}}},
            "grading": {"worst_per_cell_ratio": min(1.2, cap - 1e-6),
                        "worst_per_cell_ratio_where": "synthetic",
                        "worst_junction_jump": junction[i],
                        "worst_junction_deviation": max(junction[i],
                                                        1.0 / junction[i]),
                        "worst_junction_where": "synthetic",
                        "n_blocks": 1, "n_junctions": 1, "sha256": "1" * 64}}
    return levels


def selftest_ladder():
    """M4, M5 and M6 across a ladder, each dial turned one at a time."""
    s = Suite()
    ok, _detail = m4_m5_m6(_synthetic_ladder())
    s.check("baseline: an admissible synthetic ladder passes M4, M4j, M5 and M6",
            all(c["pass"] for lv in ok for c in ok[lv]),
            "failing: %s" % [c["id"] for lv in ok for c in ok[lv]
                             if not c["pass"]])

    # M5: ONE direction refining at 1.02 while the others refine at 1.5 -- the
    # jet-flap lane's `--n-rad 0` defect, which a whole-mesh cell count cannot
    # see.  The control is derived from THAT measured failure, not from this
    # implementation's own behaviour.
    bad, _ = m4_m5_m6(_synthetic_ladder(nx_c1=(24, 24, 25)))
    m5 = [c for c in bad[1] if c["id"] == "M5"][0]
    s.check("M5 REJECTS a ladder with one direction refining at ~1.0 while "
            "another refines at 1.5", not m5["pass"],
            "worst %r" % m5["worst"])

    # M6 `rho`: a difference in the 15th digit is still a different ladder
    # (CHOICE C4, exact equality).
    bad, _ = m4_m5_m6(_synthetic_ladder(rho=(1.06, 1.06 + 1e-15, 1.06)))
    m6 = [c for c in bad[1] if c["id"] == "M6"][0]
    s.check("M6 REJECTS a `rho` that differs in the 15th digit (exact "
            "equality, CHOICE C4)", not m6["pass"],
            "rho_identical_exact = %r" % m6["rho_identical_exact"])

    # M6 junction: 1.06 is outside [1/1.05, 1.05] under both conventions.
    bad, _ = m4_m5_m6(_synthetic_ladder(junction=(1.0281, 1.06, 1.0281)))
    m6 = [c for c in bad[1] if c["id"] == "M6"][0]
    s.check("M6 REJECTS a junction jump of 1.06", not m6["pass"],
            "junctions_in_band = %r" % m6["junctions_in_band"])

    # And the reciprocal of the same jump must be rejected too, or the band is
    # being applied in one direction only (CHOICE C2).
    bad, _ = m4_m5_m6(_synthetic_ladder(junction=(1.0281, 1.0 / 1.06, 1.0281)))
    m6 = [c for c in bad[1] if c["id"] == "M6"][0]
    s.check("M6 REJECTS the RECIPROCAL jump 1/1.06 = 0.9434 as well -- the "
            "band is convention-free (CHOICE C2)", not m6["pass"],
            "junctions_in_band = %r" % m6["junctions_in_band"])

    # M4's cap must scale with the level.  A ladder built under a fixed 1.25
    # cap at every level -- F28G section 4.1's whole defect -- must refuse.
    lad = _synthetic_ladder()
    lad[2]["diag"]["growth_cap_per_cell"] = 1.25
    s.expect_refusal("a level generated under a FIXED cap of 1.25 instead of "
                     "1.25**(1/s) refuses (F28G section 4.1: a fixed cap binds "
                     "at the coarse level and goes slack at the fine one)",
                     lambda: m4_m5_m6(lad), "different threshold")

    # A missing direction at one level refuses rather than comparing what it has.
    lad = _synthetic_ladder()
    del lad[2]["diag"]["nx"]["c1"]
    s.expect_refusal("a direction present at L1 and absent at L2 refuses",
                     lambda: m4_m5_m6(lad), "direction sets")

    # The diagnostics/dict cross-check must fire on a sha mismatch.
    lad = _synthetic_ladder()
    s.expect_refusal("diagnostics recording a different blockMeshDict sha256 "
                     "than the dict on disk refuses",
                     lambda: cross_check_diag_against_dict(
                         lad[1]["diag"],
                         dict(lad[1]["grading"], sha256="2" * 64), 1),
                     "different mesh")
    s.check("the cross-check PASSES when the sha and the worst ratio agree",
            cross_check_diag_against_dict(
                lad[1]["diag"],
                dict(lad[1]["grading"],
                     worst_per_cell_ratio=1.2), 1)["relative_difference"] < 1e-9,
            "generator 1.2 vs recomputed 1.2")
    return s


def selftest_precondition():
    """F28G section 7 clause 4, and the factor-of-72 frame it can be lost in."""
    s = Suite()

    def lev(t_total, ptp_sector):
        return {"T_total": {"T_total_N": t_total},
                "stationarity": {"ptp_N": ptp_sector}}

    # T_total differs by 1.0 N between levels.  ptp = 1.0/72/20 sector N is
    # 1/20 of that in the FULL frame -- comfortably past the 10x bar.
    good = {1: lev(-40.0, 1.0 / F28.WEDGE_SCALE / 20.0),
            2: lev(-39.0, 1.0 / F28.WEDGE_SCALE / 20.0),
            3: lev(-38.5, 1.0 / F28.WEDGE_SCALE / 20.0)}
    r = precondition_iterative_vs_discretisation(good)
    s.check("the precondition PASSES when the iterative change is 20x smaller "
            "than the smallest level difference", r["pass"],
            "ratios %s" % [round(x["ratio_strict"], 3) for x in r["rows"]])

    # Now make the iterative change 5x smaller -- inside 10x, so it must FAIL.
    bad = {1: lev(-40.0, 0.5 / F28.WEDGE_SCALE / 5.0),
           2: lev(-39.0, 0.5 / F28.WEDGE_SCALE / 5.0),
           3: lev(-38.5, 0.5 / F28.WEDGE_SCALE / 5.0)}
    r2 = precondition_iterative_vs_discretisation(bad)
    s.check("the precondition FAILS when the iterative change is only 5x "
            "smaller", not r2["pass"],
            "ratios %s" % [round(x["ratio_strict"], 3) for x in r2["rows"]])

    # THE FRAME.  The same `ptp`, compared WITHOUT the WEDGE_SCALE conversion,
    # would be 72x smaller and would sail through.  Demonstrated as a number,
    # because parent Addendum 3 section 5 records that exactly this slip -- in
    # the PERMISSIVE direction -- would have rescued a failing arm.
    row = r2["rows"][0]
    unconverted_ratio = row["level_difference_strict_N"] / row["iterative_ptp_sector_N"]
    s.check("the frame conversion is load-bearing: unconverted the ratio would "
            "be %.1f (passing) and converted it is %.1f (failing) -- a factor "
            "of %g in the PERMISSIVE direction"
            % (unconverted_ratio, row["ratio_strict"], F28.WEDGE_SCALE),
            unconverted_ratio >= PRECONDITION_RATIO
            > row["ratio_strict"],
            "sector %.6g N vs full-annulus %.6g N"
            % (row["iterative_ptp_sector_N"],
               row["iterative_ptp_full_annulus_N"]))

    # CHOICE C5 must be visible: a case where the strict and adjacent readings
    # disagree, so the choice is not silently inert.
    split = {1: lev(-40.0, 0.3 / F28.WEDGE_SCALE / 10.0),
             2: lev(-37.0, 0.3 / F28.WEDGE_SCALE / 10.0),
             3: lev(-36.7, 0.3 / F28.WEDGE_SCALE / 10.0)}
    r3 = precondition_iterative_vs_discretisation(split)
    disagree = any(x["pass_strict_reading"] != x["pass_adjacent_reading"]
                   for x in r3["rows"])
    s.check("CHOICE C5 is not inert: a ladder exists where the strict and "
            "adjacent readings disagree, and the strict one governs",
            disagree and not r3["pass"],
            "rows %s" % [(x["level"], x["pass_strict_reading"],
                          x["pass_adjacent_reading"]) for x in r3["rows"]])
    return s


def selftest_verdict_ordering():
    """Rule 5's ordering driven directly, every branch, in both directions."""
    s = Suite()
    x = -40.0
    conv_in = (x - 0.8125, x - 0.25, x)          # p = 2.000, in band
    conv_out = (x - 1.0, x - 0.25, x)            # p = 2.710, out of band
    osc = (x + 0.5, x - 0.5, x)

    v = verdict_from_triple(*conv_in, unconverged=[], precondition_pass=True,
                            r21_meas=R_LADDER, r32_meas=R_LADDER)
    s.check("clause (3): CONVERGING inside the band -> PASS",
            v["verdict"] == "PASS", v["why"])
    v_out = verdict_from_triple(*conv_out, unconverged=[],
                               precondition_pass=True,
                               r21_meas=R_LADDER, r32_meas=R_LADDER)
    s.check("clause (3): CONVERGING outside the band -> GATE FAIL",
            v_out["verdict"] == "GATE FAIL", v_out["why"])
    s.check("a GCI is printed on the CONVERGING rows",
            "GCI_fine_pct" in v["triple_nominal_r"],
            "GCI = %.6f %%" % v["triple_nominal_r"]["GCI_fine_pct"])

    v1 = verdict_from_triple(*conv_in, unconverged=[2], precondition_pass=True,
                             r21_meas=R_LADDER, r32_meas=R_LADDER)
    s.check("clause (1) OUTRANKS clause (3): an unconverged level turns the "
            "SAME triple that PASSED into NOT A RESULT",
            v1["verdict"] == "NOT A RESULT", v1["why"])
    assert_one_way(v["verdict"], v1["verdict"])

    v2 = verdict_from_triple(*conv_in, unconverged=[], precondition_pass=False,
                             r21_meas=R_LADDER, r32_meas=R_LADDER)
    s.check("F28G section 7 clause 4 outranks clause (3): a failed "
            "iterative-vs-discretisation precondition turns the same PASS into "
            "NOT A RESULT", v2["verdict"] == "NOT A RESULT", v2["why"])

    v3 = verdict_from_triple(*osc, unconverged=[], precondition_pass=True,
                             r21_meas=R_LADDER, r32_meas=R_LADDER)
    s.check("clause (2): an OSCILLATORY triple -> NOT A RESULT",
            v3["verdict"] == "NOT A RESULT", v3["why"])
    pb = v3["printed_beside_the_verdict"]
    s.check("clause (2) prints THE VALUE, BOTH TRIPLES and BOTH ORDERS beside "
            "the verdict, and NO GCI",
            (pb["value_fine_N"] == osc[2] and len(pb["value_triple_N"]) == 3
             and "e32" in pb["error_triple_N"] and pb["GCI_quoted"] is False
             and "order_nominal_r" in pb and "order_measured_r_celik" in pb),
            "keys %s" % sorted(pb))

    # CHOICE C6: the two orders straddling the band edge -> NOT A RESULT.
    # Hand-built: pick a triple whose nominal-r order sits just inside 2.5 and
    # whose measured-r order sits just outside, by using a measured r21 well
    # away from 1.5.  The dial is the RATIO, not the values.
    p_edge = 2.49
    ratio = R_LADDER ** p_edge
    ff, e21 = x, -0.25
    fm = ff + e21
    fc = fm + e21 * ratio
    v4 = verdict_from_triple(fc, fm, ff, unconverged=[], precondition_pass=True,
                             r21_meas=1.20, r32_meas=1.20)
    inside_nom = P_BAND[0] <= v4["observed_order_nominal"] <= P_BAND[1]
    outside_meas = not (P_BAND[0] <= v4["observed_order_measured_celik"]
                        <= P_BAND[1])
    s.check("CHOICE C6: when the nominal-r order is inside the band (%.4f) and "
            "the measured-r order is outside it (%.4f), the row is NOT A "
            "RESULT -- a legal one-way strengthening"
            % (v4["observed_order_nominal"],
               v4["observed_order_measured_celik"]),
            inside_nom and outside_meas and v4["verdict"] == "NOT A RESULT",
            v4["why"])
    return s


def selftest_crash_filter(tmp):
    """Both limbs, on REAL artifacts where they exist -- and it is REPORTED
    when they do not, because a limb that did not run is not a limb that
    passed."""
    s = Suite()
    crashed = os.path.join(REPO, "verification/runs/FPE_DIAG_runs/HP1/"
                                 "log.simpleFoam")
    healthy = os.path.join(REPO, "verification/runs/F28_runs/"
                                 "FEAS_L1_dp1000_U20_A2/log.simpleFoam")
    if os.path.isfile(crashed):
        c = crash_frames(crashed)
        s.check("REAL crashed log: stack frames seen (%d) while `FOAM FATAL` "
                "occurs %d times -- a filter keyed on `FOAM FATAL` would miss "
                "this crash entirely"
                % (c["stack_frames"], c["foam_fatal_occurrences"]),
                c["crashed"] and c["foam_fatal_occurrences"] == 0,
                c["log"])
    else:
        s.check("REAL crashed log limb DID NOT RUN (artifact absent: %s)"
                % crashed, False, "reported, not skipped: a limb that did not "
                                  "run is not a limb that passed")
    if os.path.isfile(healthy):
        h = crash_frames(healthy)
        s.check("REAL healthy F28 log: zero stack frames, not flagged",
                (not h["crashed"]) and h["stack_frames"] == 0, h["log"])
    else:
        s.check("REAL healthy log limb DID NOT RUN (artifact absent: %s)"
                % healthy, False, "reported, not skipped")
    synth = os.path.join(tmp, "log.synthetic")
    with open(synth, "w") as fh:
        fh.write("Time = 1\nExecutionTime = 1 s\n"
                 "#0  Foam::error::printStack(Foam::Ostream&)\n"
                 "#1  Foam::sigFpe::sigHandler(int)\nEnd\n")
    sc = crash_frames(synth)
    s.check("a synthetic log with two frames and an `End` line is still a "
            "crash -- an `End` line does not clear a stack trace",
            sc["crashed"] and sc["stack_frames"] == 2, str(sc["stack_frames"]))
    return s


def selftest_completion(tmp):
    """Rule 4, exercised through the PARENT's implementation, both ways."""
    s = Suite()
    case = os.path.join(tmp, "case")
    for d in ("0", "100", "postProcessing/forcesDuct/0"):
        os.makedirs(os.path.join(case, d), exist_ok=True)
    for f in F28.FIELDS_REQUIRED:
        open(os.path.join(case, "0", f), "w").write("x\n")
    log = os.path.join(case, "log.simpleFoam")
    open(log, "w").write("ExecutionTime = 1 s\n" * 100 + "End\n")
    # Fields at endTime must be NEWER than 0/U (the age guard), so they are
    # written second and the mtimes are set explicitly.
    for f in F28.FIELDS_REQUIRED:
        open(os.path.join(case, "100", f), "w").write("x\n")
    pp = os.path.join(case, "postProcessing/forcesDuct/0/force.dat")
    open(pp, "w").write("# Time total_x\n100 -0.33\n")
    t0 = os.path.getmtime(os.path.join(case, "0", "U"))
    for f in F28.FIELDS_REQUIRED:
        os.utime(os.path.join(case, "100", f), (t0 + 10, t0 + 10))
    os.utime(pp, (t0 + 10, t0 + 10))

    try:
        comp = F28.completion(case, log, 100, 0)
        s.check("a complete synthetic case satisfies all of rule 4",
                comp["endTime"] == 100, comp["clauses"])
    except SystemExit as e:
        s.check("a complete synthetic case satisfies all of rule 4", False,
                "refused with exit %r -- the positive limb must pass or the "
                "filter is an alarm" % e.code)

    for name, mutate in (
            ("rc != 0", lambda: F28.completion(case, log, 100, 1)),
            ("last time != endTime",
             lambda: F28.completion(case, log, 200, 0))):
        s.expect_refusal("rule 4 refuses on %s" % name, mutate)

    # The age guard: make one endTime field OLDER than 0/U.
    os.utime(os.path.join(case, "100", "U"), (t0 - 10, t0 - 10))
    s.expect_refusal("rule 4 clause 6 (the AGE GUARD) refuses a field older "
                     "than the case's own 0/U",
                     lambda: F28.completion(case, log, 100, 0))
    os.utime(os.path.join(case, "100", "U"), (t0 + 10, t0 + 10))

    s.expect_refusal("`T_total` refuses a composition the caller did not state "
                     "verbatim (CLAUDE.md rule 14)",
                     lambda: t_total(case, 100, os.path.join(case, "0", "U"),
                                     1000.0, "duct"),
                     "composition")
    return s


def selftest():
    out = {"selftest": "analyse_f28g.py",
           "registration": "verification/campaign/"
                           "F28G_GRID_CONVERGENCE_PREREGISTRATION.md",
           "note": "NO SOLVE IS LAUNCHED AND NO MESH IS REGENERATED BY THIS "
                   "SELFTEST.  It writes only into a temporary directory and, "
                   "in `--mesh-gate`, plants into the real checkMesh log and "
                   "restores it byte-exactly with its mtime.",
           "suites": []}
    tmp = tempfile.mkdtemp(prefix="f28g_selftest_")
    ok = True
    for name, fn in (("richardson_N_T8", selftest_richardson),
                     ("roache_triple", selftest_triple),
                     ("checkMesh_M1_M2_M3", lambda: selftest_checkmesh(tmp)),
                     ("grading_readback_M4_M6",
                      lambda: selftest_grading_readback(tmp)),
                     ("ladder_M4_M5_M6", selftest_ladder),
                     ("precondition_clause_4", selftest_precondition),
                     ("verdict_ordering_rule_5", selftest_verdict_ordering),
                     ("crash_filter", lambda: selftest_crash_filter(tmp)),
                     ("completion_rule_4", lambda: selftest_completion(tmp))):
        try:
            rep = fn().report(name)
        except Refusal as e:
            rep = {"suite": name, "pass": False,
                   "error": "UNEXPECTED REFUSAL: %s" % str(e)[:400]}
        except Exception as e:                                  # noqa: BLE001
            rep = {"suite": name, "pass": False,
                   "error": "%s: %s" % (type(e).__name__, str(e)[:400])}
        ok = ok and rep.get("pass", False)
        out["suites"].append(rep)
    out["tmpdir"] = tmp
    out["limbs_run"] = sum(r.get("limbs_run", 0) for r in out["suites"])
    out["limbs_failed"] = sum(r.get("limbs_failed", 0) for r in out["suites"])
    out["pass"] = ok
    # SILENCE IS NOT SUCCESS.  The caller is told to read the EXIT CODE, and
    # the exit code is what `main` returns -- never a pattern matched against
    # this text.
    out["how_to_read_this"] = ("judge the EXIT CODE (0 = every limb passed, "
                               "2 = at least one did not).  A tool piped "
                               "through a grep whose pattern the refusal line "
                               "did not match has already produced an empty "
                               "commit on this box advertising a fix that was "
                               "never in the file.")
    return out


# =============================================================================
# MAIN
# =============================================================================
def main(argv):
    _assert_constants()
    if len(argv) >= 2 and argv[1] == "--selftest":
        rep = selftest()
        print(json.dumps(rep, indent=2, sort_keys=True, default=str))
        return 0 if rep["pass"] else 2
    if len(argv) >= 3 and argv[1] in ("--mesh-gate", "--grade"):
        with open(argv[2]) as fh:
            spec = json.load(fh)
        try:
            out = mesh_gate(spec) if argv[1] == "--mesh-gate" else grade(spec)
        except Refusal as e:
            sys.stderr.write("NOT A RESULT -- comparator refuses (exit 2): "
                             "%s\n" % e)
            return 2
        print(json.dumps(out, indent=2, sort_keys=True, default=str))
        return 0 if out["verdict"] in ("PASS", "GATE REACHED") else 1
    sys.stderr.write(
        "F28G comparator.  It REFUSES (exit 2) rather than degrading, and it "
        "has NOT been run for record.\n"
        "usage: analyse_f28g.py --selftest\n"
        "       analyse_f28g.py --mesh-gate <spec.json>\n"
        "       analyse_f28g.py --grade <spec.json>\n"
        "  mesh-gate spec: {\"levels\": {\"L1\": {\"dir\": ..., "
        "\"volume_ratio_report\": ...}, \"L2\": ..., \"L3\": ...}}\n"
        "  grade spec:     {\"cases\": {\"L1\": ..., \"L2\": ..., \"L3\": ...},"
        " \"rc\": {...}, \"cells\": {...}, \"endTime\": ..., "
        "\"delta_p\": 1000, \"U_inf\": 20}\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
