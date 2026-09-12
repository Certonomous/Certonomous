#!/usr/bin/env python3
"""RC3 ceiling-gate comparator -- the two-direction reader control, the strict
completion clause, and the V0 / V1a / V1b / V2 gates.

Registration: cases/RANS_LES_closure_models/RC3_wu_ceiling_gate_validation/
PREREGISTRATION.md -- section 4 (metrics), section 5 (gates and thresholds),
section 5.2 (the verdict ladder), section 6 (the planted-zero control), section
6.1 (no ast.Assert), section 8 (strict completion) and section 11 (this
module's registered job and refusals).

ORDER OF OPERATIONS, as registered
----------------------------------
1. the two-direction planted control (section 6) runs FIRST, on a real field
   written by simpleFoam on this box, on EVERY scoring pass -- "a control that
   runs only in the test harness certifies the test harness";
2. every row is put through the strict-completion clause (section 8);
3. the rows are scored (section 4);
4. V0, then V1a and V1b, then V2 (section 5);
5. one verdict from the fixed vocabulary (section 5.2).

REGISTERED REFUSALS (section 11), every one a sys.exit(2), never an assert:
  * either plant direction failing,
  * any strict-completion clause failing,
  * a continuity violation being silently accepted,
  * (amendment A2) a per-case continuity bar that has drifted from its rule, is
    tighter than the registered 1e-4, sits below 10x its measured instrument
    floor, or is vacuous or total on its own measured population.

The third is made structural rather than promissory: a row that fails section
4's continuity criterion is carried with `continuity_ok = False`, and
`gate_arithmetic()` REFUSES if such a row ever reaches it.  There is no code
path by which a continuity violation can enter a gate quietly.

AMENDMENT A2 -- CLAUSE 8 IS APPLIED PER CASE AT THE INSTRUMENT'S MEASURED FLOOR
------------------------------------------------------------------------------
The registered quantity and the registered number 1e-4 are UNCHANGED.  What A2
fixes, measured on all 54 real Wu rows before any compute, is that the number
was applied GLOBALLY to an instrument whose own truncation error on the CBFS
hill mesh is 50x larger than the number: the UNCORRECTED CBFS baseline reads
5.26e-03 on this formula while the producer's own continuity channel reads
4.52e-14 on the same row, and this formula's reading GROWS 2.16x when the grid
is coarsened 2x -- the signature of the reader, not of the field.  So the bar is
per case, by a stated RULE from a MEASURED floor
(`continuity_bar()`), never tighter than 1e-4, and `check_continuity_bars()`
runs AG-C1..AG-C6 on every scoring pass and PRINTS the direction of the change.
Both non-gating corroboration channels are recorded on every row and neither can
rescue or condemn one.  The screen stays GLOBAL.

FINDING B AND THE RUNNER
------------------------
Clauses 1-3 delegate to `r4_lib.solve_complete`, which reads a file named `rc`
that no Wu producer wrote (measured: 0 of 54).  The repair is `rc3_run.py`, which
makes the producer emit what the clause reads; the clause is NOT weakened.
`selftest()` therefore carries a FIXTURE-VERSUS-PRODUCER PARITY block that runs
clauses 1-6 against NAMED real `simpleFoam` output with only the runner's own
file added -- because a fixture that satisfies a clause certifies the fixture.

WHY THE PLANT BAR IS ABSOLUTE HERE AND THAT IS NOT L-508
---------------------------------------------------------
Section 5.1 registers direction A as "recomputed `U_rms` must move by > 1e-12".
That is a FLOOR to exceed, not a ceiling to fall under, so the L-508 hazard --
an absolute 1e-15 read-back tolerance false-refusing on O(1)+ data -- does not
bite: a bigger field makes the measured move bigger, not smaller.  Where this
module chooses a tolerance of its own (the read-back of the planted copy) the
bar IS plant-relative: machine epsilon at the field's own largest magnitude,
floored at 1e-12.  The real fields here are O(1e2) (the duct `U` is ~108 m/s),
which is exactly the regime L-508 was paid for.

NO ast.Assert CARRIES ANY REFUSAL, GUARD, CONTROL OR GATE (section 6.1, L-332 /
D476 section 31.3).  `--selftest` parses this file with `ast` and requires zero.

REUSE, SCOPED (L-512)
---------------------
`r4_lib.solve_complete` (R4_sparta_build/r4_lib.py:494) is reused UNMODIFIED,
called with `required=()` so that only the clauses it actually shares with
section 8 are taken from it: clause 1 (rc = 0), clause 2 (the End line) and
clause 3 (termination registered -- it carries BOTH branches, the
residualControl convergence line and the endTime backstop).  Its own field loop
is deliberately not used, because section 8's clause 4 has a different field
list and clause 6 dates every field against `0/U` specifically rather than
against each field's own `0/` copy; those two clauses, plus clause 5's
ExecutionTime accounting and clause 8's continuity, are implemented here.  The
helper is neither edited nor reimplemented, and its new use is exercised in
both directions by `--selftest`.
"""
from __future__ import annotations

import ast
import json
import math
import os
import re
import shutil
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)
COMMON = os.path.join(CLOSURE, "_common")
R4 = os.path.join(CLOSURE, "R4_sparta_build")
for _p in (HERE, COMMON, R4):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from of_read import (read_field, read_field_expand, sym_to_full,   # noqa: E402
                     anisotropy, realisability_violation, plane_axes,
                     structured_gradient, structured_shape, latest_time_dir)
import sst_baseline_metrics as SB                                  # noqa: E402
import r4_lib                                                      # noqa: E402
import build_rc3_ladder as B                                       # noqa: E402

PREREG = B.PREREG
PLANT = 1.234e-03                    # the lab's established comparator constant

# ---- section 5.1, the thresholds.  FIXED.  Never moved (sections 7, 9).
CEILING_CUT = 0.80                   # V0 / V1: "cuts U_rms by >= 80% vs NULL"
MIN_CASES = 2                        # "on >= 2 of the 3 in-scope cases"
N_INSCOPE = 3
CONTINUITY_MAX = 1e-4                # section 4, carried verbatim.  NEVER MOVED.
PLANT_MIN_MOVE = 1e-12               # section 5.1, V3 plant
FALSIFIED_BARS = (0.30, 0.50)        # section 5's V2: the predecessors' bars

# ---------------------------------------------------------------------------
# AMENDMENT A2 -- clause 8 applied PER CASE at the instrument's MEASURED FLOOR.
#
# The registered quantity (section 4: "RMS div(U) normalised by the field's own
# gradient scale") and the registered number (1e-4) are UNCHANGED.  What A2
# fixes is that the number was applied GLOBALLY to an instrument whose own
# truncation error on one of the three in-scope meshes is 50x larger than the
# number, so on that mesh the bar could not measure the quantity it names.
#
# CONTINUITY_FLOOR[tag] is the instrument's MEASURED floor on that mesh: the
# reading this module's own formula returns on the UNCORRECTED baseline solve
# already on disk (b^Delta = 0, so no correction can be blamed for it).  It is
# corroborated on two independent channels, both measured before compute:
#   * the producer's own `time step continuity errors : sum local` on the same
#     row (`continuityErrs.H:37-38`, `fvc::div(phi)`), and
#   * the grid-coarsening ratio of this module's own reading on the same field.
# On CBFS13700 the reading GROWS 2.16x when the grid is coarsened 2x -- the
# signature of the reader's own truncation error, not of a divergence in the
# field -- while the producer reports 4.52e-14 on that same row.  On both ducts
# the reading is 1e-17, grid-independent, and the producer reports 1e-13.
CONTINUITY_FLOOR = {
    "AR_1_Ret_360": 8.6010e-18,
    "AR_3_Ret_360": 1.1100e-17,
    "CBFS13700":    9.6193e-03,
}
# The NAMED artifact each floor was measured on, and its two corroborations.
CONTINUITY_FLOOR_ARTIFACT = {
    "AR_1_Ret_360": ("/home/ubuntu/closure-data/aposteriori/wu2018/"
                     "AR_1_Ret_360/null/200000/U", 7.158e-13, 0.99),
    "AR_3_Ret_360": ("/home/ubuntu/closure-data/aposteriori/wu2018/"
                     "AR_3_Ret_360/null/99000/U", 8.147e-13, 0.83),
    "CBFS13700":    ("/home/ubuntu/closure-data/aposteriori_frozenk/wu2018/"
                     "CBFS13700/L_null/1969/U", 3.925e-14, 1.23),
}
# THE RULE, stated so the numbers below cannot drift away from it:
#   bar(tag) = max(CONTINUITY_MAX, smallest decade >= 10 x floor(tag))
# It can never set a bar TIGHTER than the registered 1e-4, and it loosens only
# by the amount the instrument's measured floor on that mesh forces.
CONTINUITY_BAR = {
    "AR_1_Ret_360": 1e-4,            # rule gives 1e-16; floored at the
    "AR_3_Ret_360": 1e-4,            # registered 1e-4.  UNCHANGED.
    "CBFS13700":    1e-1,            # rule gives 1e-1 from a floor of 9.62e-3
}
# The MEASURED predecessor readings the failability test (AG-C1) is run
# against: this module's own formula on the real Wu population, 54 rows.  Each
# entry is (min, max, n_rows, n_admitted_by_this_bar, n_rejected_by_this_bar).
#
# AMENDMENT A4, pre-compute correction.  `AR_1_Ret_360`'s `min` cell read
# 8.6010e-18 -- byte-identical to its own `CONTINUITY_FLOOR` literal 26 lines
# above -- where the population minimum is 3.8536e-18, on the frozenk `S_null`
# row.  The census CONTRADICTED ITSELF and the arithmetic settles it without
# appeal to what "min" means: `n_rows` = 18 and `n_admitted` = 4 force a
# population containing `S_null` (3.853587e-18) and `L_null` (4.346180e-18),
# BOTH of which read below the tabulated min.  No definition can rescue a
# number its own sibling cells forbid.  The other two cases carry the TRUE
# population minimum, so this was a copy-paste and not a definition.  Corrected
# below; AG-C8 now RE-DERIVES every cell from the population, so this class of
# slip cannot recur silently.  No gate, threshold, cap or label moved: `min` is
# read by no executable path and the counts were already correct.
CONTINUITY_MEASURED = {
    "AR_1_Ret_360": (3.8536e-18, 2.5116e-03, 18, 4, 14),   # A4: min corrected
    "AR_3_Ret_360": (7.6729e-18, 1.6756e-03, 18, 4, 14),
    "CBFS13700":    (5.2451e-03, 3.0663e-01, 18, 13, 5),
}
# What the RETIRED global bar (`CONTINUITY_MAX`) admitted over the same 54 rows.
# Promoted by amendment A4 from a bare literal inside `check_continuity_bars()`
# to a registered constant, so that AG-C8 can RE-DERIVE it: it is one half of
# the AG-C4 direction disclosure and a disclosure standing on an unre-derivable
# literal is a transcription, not a measurement.  THE VALUE DOES NOT MOVE.
CONTINUITY_ADMITTED_OLD = 8
# The registered predecessor POPULATION, named so AG-C8 can enumerate it.  The
# rule, stated so the enumeration cannot be quietly narrowed to fit an answer:
# every configuration directory under <root>/<case> in BOTH roots that has a
# non-zero time directory.  Measured: 57 configuration directories exist, of
# which 3 (`stock`, one per case) never solved and carry only `0`; the
# remaining 54 -- 18 per case, 6 `aposteriori` + 12 `aposteriori_frozenk` --
# are the population.  `_g0a/` and `_fields/` are case-level SIBLINGS of the
# case directories, not configurations, and are therefore never reached.
WU_POPULATION_ROOTS = ("/home/ubuntu/closure-data/aposteriori/wu2018",
                       "/home/ubuntu/closure-data/aposteriori_frozenk/wu2018")
# Named rows the bars must admit and reject.  A bar that admits everything or
# rejects everything on its own case is not a screen, and AG-C1 refuses it.
CONTINUITY_AG_ADMIT = {"AR_1_Ret_360": 3.6402e-05, "AR_3_Ret_360": 8.6106e-05,
                       "CBFS13700": 2.9031e-02}
CONTINUITY_AG_REJECT = {"AR_1_Ret_360": 1.1425e-04, "AR_3_Ret_360": 1.0146e-04,
                        "CBFS13700": 3.0663e-01}
# The producer's own continuity channel, read as a REPORTED, NON-GATING second
# reading on every row (RC4's "both readings, neither hidden" form,
# rc4_score.py:96-97 / :301-304).  It can never rescue or condemn a row.
PRODUCER_CONT_RE = re.compile(
    r"^time step continuity errors : sum local = ([0-9.eE+-]+)", re.M)

# The DNS / LES references section 4 registers.
SEC_LES_PCT = {"AR_1_Ret_360": 1.508, "AR_3_Ret_360": 1.411}
X_REATT_LES = {"CBFS13700": 4.241}

# The log and rc filenames this campaign writes, matching the frozen helper
# r4_lib.solve_complete that reads clauses 1-3 out of them.
LOG_NAME = "log.solve"


def refuse(msg):
    sys.stderr.write("RC3 REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


# ------------------ amendment A2: clause 8's per-case bar, and its anti-gaming
def continuity_bar(tag):
    """The registered per-case bar, RECOMPUTED FROM THE RULE every time.

    `bar = max(CONTINUITY_MAX, smallest decade >= 10 x measured floor)`.  The
    tabulated value in `CONTINUITY_BAR` is checked against the rule and this
    REFUSES if they disagree, so the number in the table can never drift away
    from the derivation that justifies it.
    """
    if tag not in CONTINUITY_FLOOR or tag not in CONTINUITY_BAR:
        refuse("continuity_bar: " + repr(tag) + " has no registered floor or "
               "bar; a case with no measured instrument floor cannot be "
               "screened on this channel")
    # AMENDMENT A3, repair 1.  BOTH operands of the two `math.log10` calls below
    # are guarded as POSITIVE and FINITE *before* either call.  Before A3 only
    # the FLOOR was guarded, and only against `<= 0.0`; the TABULATED BAR was
    # not guarded at all and neither was guarded against nan/inf.  DRIVEN, in
    # process, on a probe tag: tabulated bar 0.0 and -1.0 both raised
    # `ValueError: math domain error`; floor nan raised `ValueError: cannot
    # convert float NaN to integer` and floor inf `OverflowError`; and -- the
    # one that did not raise at all -- a tabulated bar of nan RETURNED nan,
    # because every comparison against nan is False, so it passed the drift
    # check, the never-tighter check and the 10x-floor check in silence and
    # would then have made `div <= nan` False on EVERY row.  None of those four
    # outcomes is a registered refusal: section 11 registers every refusal as a
    # `sys.exit(2)`, never an exception and never a silent return.
    floor = float(CONTINUITY_FLOOR[tag])
    if not math.isfinite(floor) or floor <= 0.0:
        refuse("continuity_bar: FLOOR_NOT_POSITIVE_FINITE -- the measured "
               "instrument floor for " + tag + " is " + repr(floor)
               + "; it must be a positive finite float, because the registered "
               "rule takes its base-10 logarithm and a floor that is zero, "
               "negative, nan or inf has no decade")
    tabulated = float(CONTINUITY_BAR[tag])
    if not math.isfinite(tabulated) or tabulated <= 0.0:
        refuse("continuity_bar: BAR_NOT_POSITIVE_FINITE -- the tabulated bar "
               "for " + tag + " is " + repr(tabulated) + "; it must be a "
               "positive finite float, because the drift check below takes its "
               "base-10 logarithm.  A nan bar in particular passes every "
               "comparison in this function and would be returned in silence")
    derived = 10.0 ** math.ceil(math.log10(10.0 * floor))
    bar = max(CONTINUITY_MAX, derived)
    if abs(math.log10(tabulated) - math.log10(bar)) > 1e-9:
        refuse("continuity_bar: the tabulated bar for " + tag + " is "
               + repr(tabulated) + " but the registered rule derives "
               + repr(bar) + " from the measured floor " + repr(floor)
               + "; the table has drifted from its own derivation")
    if tabulated < CONTINUITY_MAX:
        refuse("continuity_bar: " + tag + "'s bar " + repr(tabulated)
               + " is TIGHTER than the registered " + repr(CONTINUITY_MAX)
               + "; the rule may never tighten below the registered number")
    if tabulated < 10.0 * floor:
        refuse("continuity_bar: " + tag + "'s bar " + repr(tabulated)
               + " is less than 10x its measured instrument floor "
               + repr(floor) + "; a bar at or below the instrument's own "
               "truncation error measures the reader, not the field")
    return tabulated


# ---- AMENDMENT A3, repair 3: the FIRST link of the chain artifact -> floor -> bar.
#
# `continuity_bar()` defends the SECOND link: it recomputes the bar from the
# floor by the registered rule and refuses on drift.  Nothing defended the
# FIRST.  `CONTINUITY_FLOOR_ARTIFACT` named a real `U` file per case and NO
# EXECUTABLE PATH EVER READ IT -- driven by AST with a control: neither
# `check_continuity_bars` nor `continuity_bar` contains a single file-IO call,
# while the controls `producer_continuity` (exists/open/read) and `score_row`
# (read_field/read_field_expand) do, so the probe is not blind.  Consequence: a
# floor mistyped by one decade would pass every guard in this file and the bar
# would move with it.  The floor is the single load-bearing MEASURED quantity in
# amendment A2 -- it is the whole justification for CBFS13700's bar standing at
# 1e-1 rather than 1e-4 -- and `scripts/check_bar_above_floor.py` cannot catch
# it either, because that check ALSO reads the tabulated floor.  This is L-530's
# shape (a bar below its instrument's floor) transposed one level up.
#
# THE TOLERANCE, stated and justified, not a fudge band.  The re-derivation is
# DETERMINISTIC: the same three files, the same `structured_gradient` metric
# `score_row` uses, no solver, no randomness.  The ONLY genuine source of
# disagreement is that the tabulated constants are 5-significant-figure
# transcriptions of the re-derived floats, whose rounding band is at most
# 0.5e-4 relative (worst case, mantissa 1).  MEASURED disagreement at the time
# A3 was written, all three cases:
#     AR_1_Ret_360  tabulated 8.6010e-18  re-derived 8.600960e-18  rel 4.63e-06
#     AR_3_Ret_360  tabulated 1.1100e-17  re-derived 1.109988e-17  rel 1.06e-05
#     CBFS13700     tabulated 9.6193e-03  re-derived 9.619317e-03  rel 1.75e-06
# 1e-4 is that transcription band with one factor of two of headroom.  The
# defect it exists to catch -- a floor mistyped by one decade -- is 9e-1
# relative, roughly 10,000x outside the band, so the band cannot hide it.
FLOOR_PROVENANCE_REL_TOL = 1e-4


def floor_mesh_centres_path(tag):
    """The cell-centre file this case's floor must be re-derived on.

    Replicates `_common/sst_baseline_metrics.py:79-85`, the C-path `load_case`
    picks and therefore the mesh `score_row` scores on, so the re-derivation
    runs on the SAME mesh and not a lookalike.  `selftest` proves the two are
    byte-identical rather than assuming it.
    """
    if tag not in B.CASES:
        refuse("floor_mesh_centres_path: " + repr(tag) + " is not a registered "
               "case; its floor cannot be re-derived from any mesh")
    src, fam = B.CASES[tag]
    if fam == "duct":
        return os.path.join(src, "constant", "C")
    t = latest_time_dir(src)
    c = os.path.join(src, t, "C")
    return c if os.path.exists(c) else os.path.join(src, "0", "C")


def rederive_continuity_floor(tag):
    """RE-DERIVE this case's instrument floor FROM THE ARTIFACT IT NAMES.

    Reads the `U` file `CONTINUITY_FLOOR_ARTIFACT[tag]` names and the cell
    centres `load_case` would pick, and applies THIS MODULE'S OWN clause-8
    formula -- the identical three lines `score_row` uses:
        A = structured_gradient(C, U); divU = einsum("nii->n", A)
        gscale = sqrt((A**2).sum(axis=(1,2)).mean())
        floor  = sqrt(mean(divU**2)) / gscale
    ZERO SOLVER COMPUTE: three `U` files and three `C` files already on disk.
    REFUSES (sys.exit 2) if either artifact is absent or unreadable, or if the
    mesh and the field disagree on the cell count -- never returns a number it
    could not actually measure.
    """
    if tag not in CONTINUITY_FLOOR_ARTIFACT:
        refuse("rederive_continuity_floor: " + repr(tag) + " names no floor "
               "artifact; a floor with no named artifact cannot be re-derived "
               "and must not be trusted")
    art = CONTINUITY_FLOOR_ARTIFACT[tag][0]
    if not os.path.exists(art):
        refuse("FLOOR_ARTIFACT_ABSENT: " + tag + "'s instrument floor names "
               + art + ", which is NOT ON DISK.  A floor whose artifact cannot "
               "be read is not a measurement and the bar derived from it has "
               "no provenance")
    cpath = floor_mesh_centres_path(tag)
    if not os.path.exists(cpath):
        refuse("FLOOR_MESH_ABSENT: " + tag + "'s floor must be re-derived on "
               + cpath + ", which is NOT ON DISK")
    try:
        U = np.asarray(read_field(art), float).reshape(-1, 3)
        C = np.asarray(read_field(cpath), float).reshape(-1, 3)
    except SystemExit:
        raise
    except BaseException as exc:
        refuse("FLOOR_ARTIFACT_UNREADABLE: " + tag + "'s floor artifact " + art
               + " or mesh " + cpath + " could not be read: "
               + type(exc).__name__ + ": " + str(exc))
    if U.shape[0] != C.shape[0]:
        refuse("FLOOR_ARTIFACT_SHAPE: " + tag + "'s floor artifact " + art
               + " carries " + str(U.shape[0]) + " cells but its mesh "
               + cpath + " carries " + str(C.shape[0])
               + "; the floor cannot have been measured on this pair")
    A = structured_gradient(C, U)
    gscale = float(np.sqrt((A ** 2).sum(axis=(1, 2)).mean()))
    if not math.isfinite(gscale) or gscale <= 0.0:
        refuse("FLOOR_GRADIENT_SCALE: " + tag + "'s floor artifact " + art
               + " has gradient scale " + repr(gscale) + "; the clause-8 metric "
               "is 0/0 on it and no floor can be re-derived")
    divU = np.einsum("nii->n", A)
    v = float(np.sqrt((divU ** 2).mean()) / gscale)
    if not math.isfinite(v):
        refuse("FLOOR_REDERIVED_NON_FINITE: " + tag + " re-derives " + repr(v)
               + " from " + art)
    return v


def check_floor_provenance():
    """AG-C7 (amendment A3): the chain's FIRST link, defended on every pass.

    Every tabulated `CONTINUITY_FLOOR` is RE-DERIVED from the artifact it names,
    by this module's own formula, and this REFUSES if any of them disagrees by
    more than `FLOOR_PROVENANCE_REL_TOL`, or if any named artifact is absent or
    unreadable.  Run from `check_continuity_bars()`, so it runs before any row
    is scored, on every pass -- the same place the bar's own drift check runs.
    """
    out = {}
    for tag in sorted(CONTINUITY_FLOOR):
        tab = float(CONTINUITY_FLOOR[tag])
        if not math.isfinite(tab) or tab <= 0.0:
            refuse("AG-C7: " + tag + "'s tabulated floor is " + repr(tab)
                   + "; it must be a positive finite float")
        got = rederive_continuity_floor(tag)
        rel = abs(got - tab) / abs(tab)
        art = CONTINUITY_FLOOR_ARTIFACT[tag][0]
        if rel > FLOOR_PROVENANCE_REL_TOL:
            refuse("AG-C7 FLOOR_PROVENANCE: " + tag + "'s tabulated instrument "
                   "floor is " + repr(tab) + " but re-deriving it from the "
                   "artifact it names (" + art + ") with this module's own "
                   "clause-8 formula gives " + repr(got) + " -- a relative "
                   "disagreement of " + ("%.3e" % rel) + ", outside the stated "
                   + repr(FLOOR_PROVENANCE_REL_TOL) + " transcription band.  "
                   "The bar derived from this floor has no provenance and NO "
                   "ROW MAY BE SCORED against it")
        print("[clause 8 floor provenance AG-C7] %-13s tabulated %.4e  "
              "RE-DERIVED FROM ARTIFACT %.6e  rel %.2e (tol %.0e)  <- %s"
              % (tag, tab, got, rel, FLOOR_PROVENANCE_REL_TOL, art))
        out[tag] = (tab, got, rel)
    return out


# ---- AMENDMENT A4: AG-C8, the census RE-DERIVED FROM THE POPULATION.
#
# A3's AG-C7 anchored the FLOOR to the artifact it names.  It left the level
# above it open, and this is that level.  `CONTINUITY_MEASURED` is offered as a
# MEASUREMENT of 54 real rows on disk -- AG-C1 refuses a bar that is "vacuous or
# total on its own measured population" out of it, and AG-C4's direction
# disclosure ("21 of 54 where the retired global bar admitted 8 of 54") is built
# entirely out of it -- and NOTHING re-derived it.  The anti-gaming block
# screened a TABLE rather than the DATA the table claims to summarise.
#
# THE SEVERITY, STATED HONESTLY AND NOT INFLATED.  A pre-registration is
# ENTITLED to carry constants measured before compute; that is what a
# pre-registration IS, and hardcoding is not the defect.  The defect is that a
# number offered as a MEASUREMENT of a population on disk had no executable path
# back to that population.  DRIVEN, and it was not hypothetical: re-deriving the
# census found `AR_1_Ret_360`'s `min` wrong by 2.23x (A4's correction above).
# The honest limit of that finding is stated too -- the wrong cell was read by
# NO executable path, and every cell AG-C1 and AG-C4 actually read (all three
# `n_rows`, `n_admitted`, `n_rejected`, and `CONTINUITY_ADMITTED_OLD`) re-derived
# EXACTLY.  The direction disclosure was never wrong.
#
# THE COST, DISCLOSED RATHER THAN ENGINEERED AWAY.  This reads 54 `U` files and
# 3 `C` files -- 57 files, ZERO SOLVER COMPUTE -- and it runs before any row is
# scored, on every pass.  MEASURED, single-threaded at `nice -n 19` on a box
# under load 60-76 of 16 cores: 5.80 s warm, 16.86 s on a cold or contended
# draw, four draws spanning 5.80/6.00/12.75/16.86 s.  The figure is
# load-dependent and is quoted as a range rather than as one flattering draw.
# Against AG-C7's 0.067 s on the same box in the same process that is ~87x.
# A cache keyed on artifact mtime+size would buy that back and was DELIBERATELY
# REJECTED: it adds a stale-cache acceptance path to the one check whose entire
# point is that no number is trusted without re-derivation.  The cost is the
# honest price of the guarantee.
#
# THE TOLERANCE.  Counts are integers and are compared EXACTLY -- there is no
# band in which a row count is nearly right.  `min` and `max` are
# 5-significant-figure transcriptions of re-derived floats, so they carry the
# same rounding band A3 justified for the floor (at most 0.5e-4 relative, worst
# case mantissa 1), and the same 1e-4 with one factor of two of headroom.
CENSUS_PROVENANCE_REL_TOL = 1e-4


def wu_population_rows(tag):
    """Enumerate this case's registered predecessor population FROM DISK.

    The rule is `WU_POPULATION_ROOTS`': every configuration directory under
    `<root>/<tag>` in BOTH roots that has a non-zero time directory.  A
    directory that never solved (only `0`) is not a row and is reported as
    skipped, never silently dropped.  Returns [(name, path-to-U), ...] and the
    list of skipped names.  ZERO SOLVER COMPUTE: it only lists and reads.
    """
    rows = []
    skipped = []
    for root in WU_POPULATION_ROOTS:
        base = os.path.join(root, tag)
        if not os.path.isdir(base):
            refuse("CENSUS_ROOT_ABSENT: " + tag + "'s population requires "
                   + base + ", which is NOT A DIRECTORY.  A census cannot be "
                   "re-derived from a population that is not on disk")
        label = os.path.basename(os.path.dirname(root))
        for cfg in sorted(os.listdir(base)):
            case = os.path.join(base, cfg)
            if not os.path.isdir(case):
                continue
            name = label + "/" + cfg
            try:
                lt = r4_lib.latest_time(case)
            except SystemExit:
                raise
            except BaseException as exc:
                refuse("CENSUS_TIME_UNREADABLE: " + name + " (" + case + ") "
                       "is in " + tag + "'s population directory but its time "
                       "directories could not be read: " + type(exc).__name__
                       + ": " + str(exc))
            if lt is None or str(lt) == "0":
                skipped.append(name)
                continue
            u = os.path.join(case, str(lt), "U")
            if not os.path.exists(u):
                refuse("CENSUS_U_ABSENT: " + name + " has a non-zero time "
                       "directory " + str(lt) + " but no U at " + u
                       + "; it is a population row whose reading cannot be "
                       "re-derived and it must not be silently dropped")
            rows.append((name, u))
    return rows, skipped


def rederive_case_census(tag):
    """RE-DERIVE one case's 5-cell census FROM THE POPULATION ON DISK.

    Applies THIS MODULE'S OWN clause-8 formula -- the identical three lines
    `score_row()` and `rederive_continuity_floor()` use -- to every row of the
    population, on the same mesh `load_case` picks, and counts admissions
    against that case's REGISTERED bar.  ZERO SOLVER COMPUTE.

    Every operand is checked POSITIVE AND FINITE BEFORE it is compared.  A
    tabulated `nan` once passed every comparison in this file in silence (every
    comparison against `nan` is False) and was returned; a `nan` reading here
    would count as REJECTED without a word.  It refuses instead.
    """
    if tag not in CONTINUITY_MEASURED:
        refuse("rederive_case_census: " + repr(tag) + " has no tabulated "
               "census; there is nothing to re-derive it against")
    bar = continuity_bar(tag)
    if not math.isfinite(bar) or bar <= 0.0:
        refuse("CENSUS_BAR_NON_FINITE: " + tag + "'s bar is " + repr(bar)
               + "; no row can be admitted or rejected against it")
    cpath = floor_mesh_centres_path(tag)
    if not os.path.exists(cpath):
        refuse("CENSUS_MESH_ABSENT: " + tag + "'s census must be re-derived on "
               + cpath + ", which is NOT ON DISK")
    try:
        C = np.asarray(read_field(cpath), float).reshape(-1, 3)
    except SystemExit:
        raise
    except BaseException as exc:
        refuse("CENSUS_MESH_UNREADABLE: " + tag + "'s mesh " + cpath
               + " could not be read: " + type(exc).__name__ + ": " + str(exc))
    rows, skipped = wu_population_rows(tag)
    if not rows:
        refuse("CENSUS_EMPTY: " + tag + "'s population re-derives to ZERO rows. "
               "An empty population is not a measurement and every count taken "
               "from it would be a vacuous zero")
    readings = []
    for name, upath in rows:
        try:
            U = np.asarray(read_field(upath), float).reshape(-1, 3)
        except SystemExit:
            raise
        except BaseException as exc:
            refuse("CENSUS_ROW_UNREADABLE: " + tag + " row " + name + " ("
                   + upath + ") could not be read: " + type(exc).__name__
                   + ": " + str(exc))
        if U.shape[0] != C.shape[0]:
            refuse("CENSUS_ROW_SHAPE: " + tag + " row " + name + " carries "
                   + str(U.shape[0]) + " cells but the mesh " + cpath
                   + " carries " + str(C.shape[0]) + "; the reading cannot "
                   "have been measured on this pair")
        A = structured_gradient(C, U)
        gscale = float(np.sqrt((A ** 2).sum(axis=(1, 2)).mean()))
        if not math.isfinite(gscale) or gscale <= 0.0:
            refuse("CENSUS_GRADIENT_SCALE: " + tag + " row " + name
                   + " has gradient scale " + repr(gscale) + "; the clause-8 "
                   "metric is 0/0 on it and no reading can be re-derived")
        v = float(np.sqrt((np.einsum("nii->n", A) ** 2).mean()) / gscale)
        if not math.isfinite(v) or v < 0.0:
            refuse("CENSUS_READING_NON_FINITE: " + tag + " row " + name
                   + " re-derives " + repr(v) + "; it must be a finite "
                   "non-negative float BEFORE it is compared to any bar")
        readings.append((name, v))
    vals = [v for _, v in readings]
    n_adm = sum(1 for v in vals if v <= bar)
    n_old = sum(1 for v in vals if v <= CONTINUITY_MAX)
    return {"rows": readings, "skipped": skipped, "bar": bar,
            "min": min(vals), "max": max(vals), "n_rows": len(vals),
            "n_admitted": n_adm, "n_rejected": len(vals) - n_adm,
            "n_admitted_retired_global": n_old}


def check_case_census(tag):
    """AG-C8 for ONE case: every tabulated cell against the re-derived one."""
    tab = CONTINUITY_MEASURED[tag]
    if len(tab) != 5:
        refuse("AG-C8: " + tag + "'s tabulated census has " + str(len(tab))
               + " cells, not the registered 5 (min, max, n_rows, n_admitted, "
                 "n_rejected)")
    t_lo, t_hi = float(tab[0]), float(tab[1])
    t_n, t_adm, t_rej = int(tab[2]), int(tab[3]), int(tab[4])
    for nm, val in (("min", t_lo), ("max", t_hi)):
        if not math.isfinite(val) or val <= 0.0:
            refuse("AG-C8: " + tag + "'s tabulated census " + nm + " is "
                   + repr(val) + "; it must be a positive finite float BEFORE "
                   "it is compared to anything")
    got = rederive_case_census(tag)
    for nm, tv, gv in (("n_rows", t_n, got["n_rows"]),
                       ("n_admitted", t_adm, got["n_admitted"]),
                       ("n_rejected", t_rej, got["n_rejected"])):
        if tv != gv:
            refuse("AG-C8 CENSUS_PROVENANCE: " + tag + "'s tabulated " + nm
                   + " is " + str(tv) + " but RE-DERIVING it from the "
                   "population on disk (" + str(got["n_rows"]) + " rows, bar "
                   + repr(got["bar"]) + ") gives " + str(gv) + ".  Counts are "
                   "compared EXACTLY.  AG-C1's non-vacuity refusal and AG-C4's "
                   "direction disclosure are both built on this cell and NO ROW "
                   "MAY BE SCORED while it does not re-derive")
    for nm, tv, gv in (("min", t_lo, got["min"]), ("max", t_hi, got["max"])):
        rel = abs(gv - tv) / abs(tv)
        if rel > CENSUS_PROVENANCE_REL_TOL:
            refuse("AG-C8 CENSUS_PROVENANCE: " + tag + "'s tabulated census "
                   + nm + " is " + repr(tv) + " but RE-DERIVING it from the "
                   "population on disk gives " + repr(gv) + " -- a relative "
                   "disagreement of " + ("%.3e" % rel) + ", outside the stated "
                   + repr(CENSUS_PROVENANCE_REL_TOL) + " transcription band")
    for nm, table in (("ADMIT", CONTINUITY_AG_ADMIT),
                      ("REJECT", CONTINUITY_AG_REJECT)):
        if tag not in table:
            refuse("AG-C8: " + tag + " names no AG-C1 " + nm + " reading")
        named = float(table[tag])
        if not math.isfinite(named) or named <= 0.0:
            refuse("AG-C8: " + tag + "'s AG-C1 " + nm + " reading is "
                   + repr(named) + "; it must be a positive finite float")
        hit = None
        for rname, v in got["rows"]:
            if abs(v - named) / abs(named) <= CENSUS_PROVENANCE_REL_TOL:
                hit = rname
                break
        if hit is None:
            refuse("AG-C8 CENSUS_PROVENANCE: " + tag + "'s AG-C1 " + nm
                   + " reading " + repr(named) + " DOES NOT OCCUR in the "
                   "re-derived population of " + str(got["n_rows"]) + " rows.  "
                   "AG-C1 calls it a NAMED REAL READING; a reading that occurs "
                   "in no row is not real and the bar it pins has no provenance")
        got["named_" + nm] = hit
    print("[clause 8 census provenance AG-C8] %-13s %d rows RE-DERIVED FROM "
          "POPULATION  min %.6e  max %.6e  admits %d rejects %d (bar %.0e)  "
          "retired-global admits %d  |  admit %s <- %s  reject %s <- %s"
          % (tag, got["n_rows"], got["min"], got["max"], got["n_admitted"],
             got["n_rejected"], got["bar"], got["n_admitted_retired_global"],
             ("%.4e" % float(CONTINUITY_AG_ADMIT[tag])), got["named_ADMIT"],
             ("%.4e" % float(CONTINUITY_AG_REJECT[tag])), got["named_REJECT"]))
    return got


def check_census_provenance():
    """AG-C8 (amendment A4): the census RE-DERIVED, before any row is scored.

    Every cell of `CONTINUITY_MEASURED` is re-derived from the 54-row Wu
    population on disk by this module's own clause-8 formula, and this REFUSES
    (`sys.exit 2`) on any disagreement -- counts exactly, `min`/`max` inside the
    stated transcription band.  `CONTINUITY_ADMITTED_OLD`, the other half of
    AG-C4's direction disclosure, is re-derived against `CONTINUITY_MAX` over
    the same population.  The AG-C1 named readings are checked to OCCUR in it.
    Run from `check_continuity_bars()`, the same place AG-C7 runs.
    """
    out = {}
    admitted_old = 0
    admitted_new = 0
    total = 0
    for tag in sorted(CONTINUITY_MEASURED):
        got = check_case_census(tag)
        out[tag] = got
        admitted_old += got["n_admitted_retired_global"]
        admitted_new += got["n_admitted"]
        total += got["n_rows"]
    if admitted_old != CONTINUITY_ADMITTED_OLD:
        refuse("AG-C8 CENSUS_PROVENANCE: the registered retired-global-bar "
               "admit count is " + str(CONTINUITY_ADMITTED_OLD) + " but "
               "RE-DERIVING it from the population on disk against "
               + repr(CONTINUITY_MAX) + " gives " + str(admitted_old)
               + ".  This is one half of the AG-C4 DIRECTION DISCLOSURE and a "
               "disclosure whose baseline does not re-derive is not a "
               "disclosure")
    print("[clause 8 census provenance AG-C8] TOTAL %d rows RE-DERIVED: "
          "per-case bars admit %d, retired global %g admits %d (registered %d)"
          % (total, admitted_new, CONTINUITY_MAX, admitted_old,
             CONTINUITY_ADMITTED_OLD))
    return {"per_case": out, "measured_rows": total,
            "admitted_per_case_bars": admitted_new,
            "admitted_retired_global_bar": admitted_old,
            "census_provenance_rel_tol": CENSUS_PROVENANCE_REL_TOL}


def check_continuity_bars():
    """AG-C1 / AG-C2 / AG-C4 / AG-C7: run before any row is scored, every pass.

    AG-C2  every bar is >= 10x its case's MEASURED instrument floor and never
           tighter than the registered CONTINUITY_MAX -- enforced by
           `continuity_bar()` above.
    AG-C1  every bar is FAILABLE AND NON-VACUOUS on its own case's measured
           predecessor population: it must ADMIT at least one named real
           reading and REJECT at least one.  A bar that admits everything or
           rejects everything on its own case is not a screen.
    AG-C4  the DIRECTION of the change is printed on every pass, so the fact
           that the per-case bars admit more predecessor rows than the retired
           global bar did is on the face of the output and cannot be discovered
           afterwards.
    """
    # AG-C7, amendment A3.  FIRST, before any bar is quoted: every floor is
    # re-derived from the artifact it names.  The bar's own drift check below is
    # worthless if the floor it derives from was never checked against anything.
    provenance = check_floor_provenance()
    # AG-C8, amendment A4.  SECOND, still before any bar is quoted: the whole
    # 54-row census AG-C1 and AG-C4 read is re-derived from the population on
    # disk.  AG-C7 anchored the floor to its artifact; this anchors the table to
    # its data, so the anti-gaming block screens the DATA and not a TABLE.
    census = check_census_provenance()
    admitted_new = 0
    admitted_old = 0
    total = 0
    for tag in sorted(CONTINUITY_BAR):
        bar = continuity_bar(tag)
        adm = float(CONTINUITY_AG_ADMIT[tag])
        rej = float(CONTINUITY_AG_REJECT[tag])
        if not adm <= bar:
            refuse("AG-C1: " + tag + "'s bar " + repr(bar) + " REJECTS the "
                   "named real reading " + repr(adm) + " it must admit; a "
                   "screen that admits nothing on its own case is not a screen")
        if rej <= bar:
            refuse("AG-C1: " + tag + "'s bar " + repr(bar) + " ADMITS the "
                   "named real reading " + repr(rej) + " it must reject; a "
                   "screen that rejects nothing is not a screen")
        lo, hi, n, n_adm, n_rej = CONTINUITY_MEASURED[tag]
        if n_adm + n_rej != n:
            refuse("AG-C1: " + tag + "'s measured census does not close: "
                   + str(n_adm) + " + " + str(n_rej) + " != " + str(n))
        if n_adm == 0 or n_rej == 0:
            refuse("AG-C1: " + tag + "'s bar is vacuous or total on its own "
                   "measured population (" + str(n_adm) + " admitted, "
                   + str(n_rej) + " rejected of " + str(n) + ")")
        admitted_new += n_adm
        total += n
        art, prod, ratio = CONTINUITY_FLOOR_ARTIFACT[tag]
        print("[clause 8 bar] %-13s floor %.4e (%s)  producer %.3e  "
              "grid ratio 2h/h %.2f  ->  BAR %.1e  (admits %d of %d measured "
              "predecessor rows)"
              % (tag, CONTINUITY_FLOOR[tag], os.path.basename(
                  os.path.dirname(os.path.dirname(art))), prod, ratio, bar,
                 n_adm, n))
    # what the RETIRED global bar admitted on the same 54 rows, measured.
    # Amendment A4: the registered constant, RE-DERIVED from the population by
    # AG-C8 above -- no longer a literal that nothing could check.
    admitted_old = CONTINUITY_ADMITTED_OLD
    print("[clause 8 AG-C4 DIRECTION DISCLOSURE] the registered per-case bars "
          "admit %d of %d measured predecessor rows; the RETIRED global %g bar "
          "admitted %d of %d.  This is a LOOSENING on CBFS13700 only, of the "
          "size its measured instrument floor forces, and the registered "
          "number %g is unchanged on both ducts."
          % (admitted_new, total, CONTINUITY_MAX, admitted_old, total,
             CONTINUITY_MAX))
    print("[clause 8 AG-C5] CBFS13700 stays in the denominator: N_INSCOPE = %d,"
          " MIN_CASES = %d, both unchanged; its bar still rejects %d of its %d "
          "measured rows." % (N_INSCOPE, MIN_CASES,
                              CONTINUITY_MEASURED["CBFS13700"][4],
                              CONTINUITY_MEASURED["CBFS13700"][2]))
    return {"bars": {t: continuity_bar(t) for t in sorted(CONTINUITY_BAR)},
            "admitted_per_case_bars": admitted_new,
            "admitted_retired_global_bar": admitted_old,
            "measured_rows": total,
            # amendment A3 AG-C7: (tabulated, re-derived-from-artifact, rel)
            "floor_provenance": provenance,
            "floor_provenance_rel_tol": FLOOR_PROVENANCE_REL_TOL,
            # amendment A4 AG-C8: the census re-derived from the population
            "census_provenance": census}


def producer_continuity(case):
    """The REPORTED, NON-GATING second reading: the producer's own continuity.

    `continuityErrs.H:44-47` prints `time step continuity errors : sum local =
    <x>` once per pressure solve; this returns the LAST value in the row's own
    log.  It is recorded on every row and it has NO gate power: it can neither
    rescue a row that failed clause 8 nor condemn one that passed.
    """
    log = os.path.join(case, LOG_NAME)
    if not os.path.exists(log):
        return None
    ms = PRODUCER_CONT_RE.findall(open(log, errors="replace").read())
    return float(ms[-1]) if ms else None


def grid_readings(C, U):
    """AMENDMENT A3, repair 2.  The two RAW readings `grid_ratio` is built from.

    Returns `(fine, coarse)`: this module's own clause-8 metric on the field,
    and on the SAME field with the structured grid decimated 2x.  A reading is
    `None` if and ONLY IF that grid's gradient scale is zero (or non-finite),
    which makes the reading 0/0 -- a reading that DOES NOT EXIST, which is not
    the same thing as a reading OF zero.  Recorded on every row beside the
    ratio so a measured zero can never be laundered into a silence.

    NO gate power, and it NEVER RAISES: this is a corroboration channel called
    from `score_row`, and before A3 it could destroy a whole scoring pass.
    """
    ns, nf = structured_shape(C)
    if ns < 8 or nf < 8:
        return (None, None)
    Cr = np.asarray(C, float).reshape(ns, nf, 3)[::2, ::2, :].reshape(-1, 3)
    Ur = np.asarray(U, float).reshape(ns, nf, 3)[::2, ::2, :].reshape(-1, 3)
    A = structured_gradient(C, U)
    Ar = structured_gradient(Cr, Ur)

    def m(g):
        d = np.einsum("nii->n", g)
        s = float(np.sqrt((g ** 2).sum(axis=(1, 2)).mean()))
        if not math.isfinite(s) or s <= 0.0:
            return None                 # 0/0: this grid has no reading at all
        v = float(np.sqrt((d ** 2).mean()) / s)
        return v if math.isfinite(v) else None

    return (m(A), m(Ar))


def grid_ratio(C, U):
    """The REPORTED, NON-GATING third reading: is the number truncation error?

    Re-reads this module's own metric on the SAME field with the structured grid
    decimated 2x.  A second-order truncation error grows ~4x; a real divergence
    in the field is grid-independent.  Recorded so the attribution is on the
    record at grading time instead of being argued afterwards.  NO gate power.

    AMENDMENT A3, repair 2.  Two defects are repaired here, BOTH DRIVEN:
      (a) `if not fine: return None` was a TRUTHINESS test on a MEASURED float.
          Driven on an exactly solenoidal structured field (gradient scale
          1.414214e+00, so the reading exists): the metric measured 0.000000e+00
          and the channel reported "could not compute".  A real reading was
          laundered into a silence.
      (b) `float(coarse / fine)` raised when the COARSE reading did not exist.
          Driven on a period-2 alternating field, whose 2x decimation is
          CONSTANT: fine gradient scale 5.3033e+00, coarse 0.0000e+00, and the
          channel raised `TypeError: unsupported operand type(s) for /:
          'NoneType' and 'float'` straight out of `score_row`, discarding every
          gate finding already computed in that pass.  (Note: a UNIFORM field
          does NOT trigger this -- it short-circuits at the truthiness test in
          (a) and returns None.  The trigger is fine-scale non-zero WITH
          coarse-scale zero.)
    `None` now means, and only means, that no finite ratio exists; the two raw
    readings recorded beside it in `score_row` say which of the two it was.
    """
    return ratio_from_readings(*grid_readings(C, U))


def ratio_from_readings(fine, coarse):
    """AMENDMENT A3, repair 2.  The ONE place the two readings become a ratio.

    `score_row` records the readings and the ratio, and must not re-implement
    this rule beside it.  Returns `None` when no FINITE ratio exists -- either
    grid has no reading, or the fine reading is a MEASURED zero denominator --
    and the readings themselves are on the row either way.  NEVER RAISES.
    """
    if fine is None or coarse is None:
        return None                     # one grid has no reading: 0/0
    if fine == 0.0:
        return None                     # a MEASURED zero denominator: the ratio
        #                                 has no finite value, but the reading
        #                                 itself is on the row as 0.0, not lost
    return float(coarse / fine)


# ------------------------------------------- section 6, the reader control
def u_rms(U, U_LES, uref):
    e = np.linalg.norm(np.asarray(U, float) - np.asarray(U_LES, float), axis=1)
    return float(np.sqrt((e ** 2).mean()) / uref)


def swap_internal_vector(src_path, dst_path, vals):
    """Write a copy of an OpenFOAM vector field with a new internalField.

    The header and the whole boundaryField block are carried over byte for
    byte, so the copy differs from the original in exactly the values planted.
    Re-implemented here: the predecessor's version lives in a file section 1.5
    forbids this item to touch (Kaandorp2020_TBRF/aposteriori/frozen_R.py:32).
    """
    s = open(src_path).read()
    if "internalField" not in s or "boundaryField" not in s:
        refuse("not an OpenFOAM field file: " + src_path)
    i = s.index("internalField")
    j = s.index("boundaryField")
    a = np.asarray(vals, float).reshape(-1, 3)
    rows = "\n".join("(" + " ".join("%.17g" % c for c in r) + ")" for r in a)
    body = ("internalField   nonuniform List<vector>\n" + str(a.shape[0])
            + "\n(\n" + rows + "\n)\n;\n\n")
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    open(dst_path, "w").write(s[:i] + body + s[j:])


def plant_control(u_path, U_LES, uref, scratch, reader=read_field):
    """Section 6, BOTH directions, on a field simpleFoam wrote on this box.

    Direction A -- can the reader SEE a non-zero?  PLANT is added at cell index
    0 and cell index n // 2, the copy is written to DISK, and it is re-read
    through the SAME reader the scorer uses.  The recomputed `U_rms` must move
    by more than 1e-12 (section 5.1).  Otherwise: sys.exit(2).

    Direction B -- does the reader see a genuine zero AS zero?  The unmodified
    copy is re-read through the same reader; the recomputed `U_rms` must be
    BITWISE identical to the original's.  Otherwise: sys.exit(2).

    `reader` is injectable so `--selftest` can drive a blinded reader and a
    noisy reader and show that each direction actually FIRES.
    """
    if not os.path.exists(u_path):
        refuse("planted control has no real field to work on: " + u_path)
    U0 = np.asarray(reader(u_path), float).reshape(-1, 3)
    U_LES = np.asarray(U_LES, float).reshape(-1, 3)
    if U0.shape != U_LES.shape:
        refuse("planted control: field " + u_path + " has shape "
               + str(U0.shape) + " but U_LES has " + str(U_LES.shape))
    base = u_rms(U0, U_LES, uref)

    # Direction B first: an unmodified copy, byte for byte.
    copy_b = os.path.join(scratch, "control_B", os.path.basename(u_path))
    os.makedirs(os.path.dirname(copy_b), exist_ok=True)
    shutil.copyfile(u_path, copy_b)
    Ub = np.asarray(reader(copy_b), float).reshape(-1, 3)
    rms_b = u_rms(Ub, U_LES, uref)
    if rms_b != base:
        refuse("section 6 direction B: the reader does NOT see a genuine zero "
               "as zero -- U_rms of an unmodified copy is %.17g against the "
               "original's %.17g (difference %.3g); the reader is not "
               "deterministic and no zero it produces is evidence"
               % (rms_b, base, rms_b - base))

    # Direction A: PLANT at cell 0 and cell n // 2, written to disk.
    n = U0.shape[0]
    idx = sorted({0, n // 2})
    Up = U0.copy()
    Up[idx, 0] = Up[idx, 0] + PLANT
    copy_a = os.path.join(scratch, "control_A", os.path.basename(u_path))
    swap_internal_vector(u_path, copy_a, Up)
    Ua = np.asarray(reader(copy_a), float).reshape(-1, 3)
    rms_a = u_rms(Ua, U_LES, uref)
    move = abs(rms_a - base)
    if not (move > PLANT_MIN_MOVE):
        refuse("section 6 direction A: the reader CANNOT see the plant -- "
               "U_rms moved by %.3g, which is not more than the registered "
               "%.3g, after PLANT = %g was written into %d cells of %s.  A "
               "zero from this reader is not evidence"
               % (move, PLANT_MIN_MOVE, PLANT, len(idx), copy_a))

    # A stronger, plant-RELATIVE read-back of the planted values themselves
    # (L-508: never an absolute 1e-15 bar on O(1)+ data).  Reported either way;
    # it refuses only if the planted cells did not survive the round trip.
    amax = float(np.abs(Up).max())
    tol = max(1e-12, 8.0 * float(np.finfo(float).eps) * amax)
    recov = np.abs((Ua[idx, 0] - U0[idx, 0]) - PLANT).max() if len(idx) else 0.0
    if float(recov) > tol:
        refuse("section 6 direction A read-back: the planted value did not "
               "survive the round trip -- max|recovered - PLANT| = %.3g > "
               "tol %.3g (field max %.3g)" % (float(recov), tol, amax))

    print("[V3 planted-zero control] field=%s n=%d PLANT=%g at cells %s"
          % (u_path, n, PLANT, idx))
    print("[V3 direction A] U_rms %.17g -> %.17g, moved %.3g (> %.3g) : PASS"
          % (base, rms_a, move, PLANT_MIN_MOVE))
    print("[V3 direction B] U_rms of the unmodified copy %.17g, bitwise "
          "identical : PASS" % rms_b)
    return {"field": u_path, "n_cells": int(n), "plant": PLANT,
            "planted_cells": idx, "u_rms_base": base, "u_rms_planted": rms_a,
            "u_rms_move": float(move), "min_move": PLANT_MIN_MOVE,
            "u_rms_unplanted_copy": rms_b, "bitwise_identical": True,
            "readback_error": float(recov), "readback_tol": float(tol),
            "verdict": "PASS"}


# ------------------------------------------ section 8, strict completion
EXEC_RE = re.compile(r"^ExecutionTime = ", re.M)
TIME_RE = re.compile(r"^Time = ", re.M)


def completion(case, required_fields=B.REQUIRED_FIELDS):
    """Section 8, all eight clauses, as a (ok, reason, info) triple.

    Clauses 1, 2 and 3 come from the frozen helper r4_lib.solve_complete,
    called with `required=()` (see the module docstring).  Clauses 4, 5 and 6
    are here.  Clause 7 is the builder's (build_rc3_ladder.guard_no_existing_times).
    Clause 8 is continuity, measured by `score_row` and enforced by
    `gate_arithmetic`.
    """
    info = {}
    if not os.path.isdir(case):
        return False, "clause 0: case directory absent: " + case, info
    ok, reason, sub = r4_lib.solve_complete(case, required=())
    info.update(sub)
    if not ok:
        return False, "clauses 1-3 (r4_lib.solve_complete): " + reason, info
    lt = r4_lib.latest_time(case)
    info["latest_time"] = lt
    if lt == "0":
        return False, "clause 3: no non-zero time directory in " + case, info
    tdir = os.path.join(case, lt)

    # clause 4: fields present at the last written time
    missing = [f for f in required_fields
               if not os.path.exists(os.path.join(tdir, f))]
    if missing:
        return False, ("clause 4: fields absent at " + lt + "/: "
                       + ", ".join(missing)), info

    # clause 5: ExecutionTime count == the number of steps the log reports
    log = os.path.join(case, LOG_NAME)
    if not os.path.exists(log):
        return False, "clause 5: no " + LOG_NAME + " in " + case, info
    txt = open(log, errors="replace").read()
    n_exec = len(EXEC_RE.findall(txt))
    n_time = len(TIME_RE.findall(txt))
    info["n_execution_time"] = n_exec
    info["n_time_steps"] = n_time
    if n_exec != n_time:
        return False, ("clause 5: ExecutionTime lines %d != steps taken %d"
                       % (n_exec, n_time)), info

    # clause 6: THE AGE GUARD.  Every field at the last written time must be
    # NEWER than the case's own 0/U, which the builder touches last.
    zu = os.path.join(case, "0", "U")
    if not os.path.exists(zu):
        return False, "clause 6: 0/U absent, the age guard has no reference", info
    t0 = os.path.getmtime(zu)
    info["age_reference_mtime"] = t0
    stale = [f for f in required_fields
             if os.path.getmtime(os.path.join(tdir, f)) <= t0]
    if stale:
        return False, ("clause 6 AGE GUARD: field(s) at " + lt + "/ not newer "
                       "than 0/U: " + ", ".join(stale)
                       + " -- they came from somewhere else"), info
    return True, "complete (" + str(info.get("stop_state")) + ")", info


# ------------------------------------------------- section 4, the metrics
def score_row(tag, case, bench):
    """Section 4's metrics for one configuration directory."""
    d = bench
    C, n = d["C"], d["n"]
    lt = r4_lib.latest_time(case)
    if lt == "0":
        refuse("score_row: no non-zero time directory in " + case)
    td = os.path.join(case, lt)
    U = np.asarray(read_field(os.path.join(td, "U")), float).reshape(-1, 3)
    k = np.asarray(read_field(os.path.join(td, "k")), float).reshape(-1)
    nut = np.asarray(read_field(os.path.join(td, "nut")), float).reshape(-1)
    UL = np.asarray(d["U_LES"], float).reshape(-1, 3)
    kL = np.asarray(d["k_LES"], float).reshape(-1)
    uref = float(np.mean(np.linalg.norm(UL, axis=1)))
    e = np.linalg.norm(U - UL, axis=1)
    A = structured_gradient(C, U)
    S = 0.5 * (A + A.transpose(0, 2, 1))
    divU = np.einsum("nii->n", A)
    gscale = float(np.sqrt((A ** 2).sum(axis=(1, 2)).mean()))
    kref = float(np.mean(np.abs(kL)))
    tau = ((2.0 / 3.0) * k)[:, None, None] * np.eye(3)[None] \
        - 2.0 * nut[:, None, None] * S
    bd = read_field_expand(os.path.join(case, "0", "bijDelta"), n)
    tau = tau + 2.0 * k[:, None, None] * sym_to_full(np.asarray(bd, float))
    b_tot, okb = anisotropy(tau, k, k_ref=kref)
    bL, okL = anisotropy(sym_to_full(np.asarray(d["tau_LES"], float)), kL)
    both = okb & okL & np.isfinite(b_tot).all(axis=(1, 2))
    viol, _ = realisability_violation(np.nan_to_num(b_tot[both]), tol=1e-6)
    div_over_grad = float(np.sqrt((divU ** 2).mean()) / gscale)
    # amendment A3, repair 2: the grid-coarsening channel, read ONCE and turned
    # into a ratio by the SAME helper `grid_ratio` uses, so the two cannot drift.
    gr_fine, gr_coarse = grid_readings(C, U)
    gr_ratio = ratio_from_readings(gr_fine, gr_coarse)
    row = {
        "time": lt, "n_cells": int(n),
        "u_rms": float(np.sqrt((e ** 2).mean()) / uref),
        "u_mae": float(e.mean() / uref),
        "k_mean": float(k.mean()),
        "k_over_k_base": float(k.mean() / float(np.asarray(d["k"], float).mean())),
        "k_over_k_LES": float(k.mean() / kref),
        "b_rms_vs_LES": float(np.sqrt(((b_tot[both] - bL[both]) ** 2)
                                      .sum(axis=(1, 2)).mean())),
        "unrealisable_frac": float(viol.mean()),
        "divU_rms_over_gradscale": div_over_grad,
        # clause 8, amendment A2: the PER-CASE bar, recomputed from the rule.
        "continuity_ok": bool(div_over_grad <= continuity_bar(tag)),
        "continuity_bar": continuity_bar(tag),
        "continuity_bar_rule": ("max(CONTINUITY_MAX, smallest decade >= 10 x "
                                "measured instrument floor)"),
        "continuity_instrument_floor": CONTINUITY_FLOOR.get(tag),
        # the REGISTERED global number, still reported on every row so that what
        # was retired, and on which rows it would have bitten, stays visible.
        "continuity_registered_bar": CONTINUITY_MAX,
        "continuity_inside_registered_bar": bool(div_over_grad
                                                 <= CONTINUITY_MAX),
        # the two NON-GATING corroboration channels (amendment A2).
        "producer_continuity_sum_local": producer_continuity(case),
        "divU_grid_ratio_2h_over_h": gr_ratio,
        # amendment A3, repair 2: the two RAW readings the ratio is built from,
        # recorded unconditionally.  A measured zero is now visible AS a zero,
        # and a ratio of None can be told apart from a reading that never was.
        "divU_grid_reading_h": gr_fine,
        "divU_grid_reading_2h": gr_coarse,
    }
    keep, thin = plane_axes(C)
    if tag in SEC_LES_PCT:
        ip = np.delete(U, thin, axis=1)
        ub = float(np.abs(U[:, thin]).mean())
        row["inplane_pct_bulk"] = float(np.mean(np.linalg.norm(ip, axis=1))
                                        / ub * 100.0)
        row["inplane_pct_bulk_DNS"] = SEC_LES_PCT[tag]
    if tag in X_REATT_LES:
        ns, nf = structured_shape(C)
        r = SB._longest_reversed_run(C[:nf, keep[0]], U[:nf, keep[0]])
        row["x_sep"] = r["x_sep"]
        row["x_reatt"] = r["x_reatt"]
        row["x_reatt_LES"] = X_REATT_LES[tag]
    return row


# ------------------------------------------------ section 5, the gates
def cut(u_rms_row, u_rms_null):
    """The fraction by which a row cuts U_rms relative to C0 NULL."""
    if u_rms_null is None or u_rms_null <= 0.0:
        refuse("cut(): a NULL U_rms of " + repr(u_rms_null)
               + " cannot be a denominator")
    return (u_rms_null - u_rms_row) / u_rms_null


def criterion(cut_value):
    """The CANDIDATE ceiling criterion under validation (section 5, V1):
    'the ceiling row for a case is the row that cuts U_rms by >= 80% relative
    to NULL'.  Returns 'PASS' or 'FAIL' -- and nothing else, ever."""
    return "PASS" if cut_value >= CEILING_CUT else "FAIL"


def gate_arithmetic(rows):
    """Turn the scored rows into V0 / V1a / V1b / V2 readings.

    REFUSES (section 11) if a row that failed section 4's continuity criterion
    or section 8's completion clause is handed to it: a continuity violation
    cannot be silently accepted, because there is no path here that accepts one.
    """
    out = {"per_case": {}, "V0_cases": [], "V1b_cases": [], "blocked": []}
    for tag in sorted(rows):
        cfgs = rows[tag]
        for cfg, r in sorted(cfgs.items()):
            if r.get("status") != "SCORED":
                continue
            if not r.get("complete", False):
                refuse("gate_arithmetic: row " + tag + "/" + cfg + " reached "
                       "the gates without passing section 8: "
                       + str(r.get("reason")))
            if not r.get("continuity_ok", False):
                refuse("gate_arithmetic: row " + tag + "/" + cfg + " reached "
                       "the gates with divU_rms_over_gradscale = "
                       + repr(r.get("divU_rms_over_gradscale")) + " > its "
                       "registered per-case bar "
                       + repr(r.get("continuity_bar")) + " (instrument floor "
                       + repr(r.get("continuity_instrument_floor"))
                       + ", producer channel "
                       + repr(r.get("producer_continuity_sum_local"))
                       + ", grid ratio 2h/h "
                       + repr(r.get("divU_grid_ratio_2h_over_h"))
                       + "); it is NOT CONVERGED and a continuity violation is "
                       "never silently accepted")
        null = cfgs.get("C0", {})
        if null.get("status") != "SCORED":
            out["blocked"].append(tag)
            out["per_case"][tag] = {"status": "BLOCKED",
                                    "reason": "C0 NULL not scored"}
            continue
        u0 = null["u_rms"]
        per = {"status": "SCORED", "u_rms_C0": u0, "cuts": {}, "criterion": {}}
        for cfg in ("C1", "C2", "C3", "C4", "CX"):
            r = cfgs.get(cfg, {})
            if r.get("status") != "SCORED":
                per["cuts"][cfg] = None
                per["criterion"][cfg] = None
                continue
            c = cut(r["u_rms"], u0)
            per["cuts"][cfg] = c
            per["criterion"][cfg] = criterion(c)
        # V2: the b-only ceiling is max(cut over C1, C2, C3), configuration named
        bonly = [(per["cuts"][c], c) for c in ("C1", "C2", "C3")
                 if per["cuts"][c] is not None]
        if bonly:
            best = max(bonly)
            per["b_only_ceiling_cut"] = best[0]
            per["b_only_ceiling_config"] = best[1]
            per["bars_falsified_by_measurement"] = [
                bar for bar in FALSIFIED_BARS if best[0] < bar]
        out["per_case"][tag] = per
        if per["criterion"].get("C4") == "PASS":
            out["V0_cases"].append(tag)
            if per["criterion"].get("CX") == "FAIL":
                out["V1b_cases"].append(tag)
    out["V0_hold"] = len(out["V0_cases"]) >= MIN_CASES
    out["V1a_hold"] = out["V0_hold"]          # definitional: same rows, same criterion
    out["V1b_hold"] = len(out["V1b_cases"]) >= MIN_CASES
    return out


def verdict(rows, plant_ok, fixedpoint):
    """Section 5.2's ladder.  One label from the fixed vocabulary, and only
    from it.  `fixedpoint` maps case -> bool (did C4's outer loop contract)."""
    vocab = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED",
             "PENDING")
    res = {"verdict": None, "reasons": []}

    if not plant_ok:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append("V3: the section 6 reader control failed")
        return _seal(res, vocab)

    incomplete = [t + "/" + c for t in sorted(rows) for c, r in sorted(rows[t].items())
                  if r.get("status") == "SCORED" and not r.get("complete", False)]
    if incomplete:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append("section 8 strict completion failed on: "
                              + ", ".join(incomplete))
        return _seal(res, vocab)
    notconv = [t + "/" + c for t in sorted(rows) for c, r in sorted(rows[t].items())
               if r.get("status") == "SCORED" and not r.get("continuity_ok", False)]
    if notconv:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append(
            "section 8 clause 8 (continuity) NOT CONVERGED on: "
            + ", ".join(notconv) + ".  Each row is judged against its own "
            "registered per-case bar " + repr({t: continuity_bar(t)
                                               for t in sorted(CONTINUITY_BAR)})
            + "; CBFS13700 is NOT dropped from the denominator (section 9) and "
            "no bar is moved")
        return _seal(res, vocab)

    contracted = [t for t in sorted(fixedpoint) if fixedpoint[t]]
    res["c4_fixed_point_contracted"] = contracted
    if len(contracted) < MIN_CASES:
        res["verdict"] = "NOT A RESULT"
        res["reasons"].append(
            "section 7 third falsifier: C4's fixed point contracted on only "
            + str(len(contracted)) + " of " + str(N_INSCOPE)
            + " cases, so there is no reference to validate against; N_outer "
            "is NOT raised above 5")
        return _seal(res, vocab)

    g = gate_arithmetic(rows)
    res["gates"] = g
    scorable = [t for t in sorted(rows)
                if g["per_case"].get(t, {}).get("status") == "SCORED"]
    if len(scorable) < MIN_CASES:
        res["verdict"] = "BLOCKED"
        res["reasons"].append(
            "only " + str(len(scorable)) + " of " + str(N_INSCOPE)
            + " in-scope cases could be scored (benchmark fields absent at run "
            "time); the denominator is NOT rescaled (section 9)")
        return _seal(res, vocab)

    if not g["V0_hold"]:
        res["verdict"] = "GATE FAIL"
        res["reasons"].append(
            "V0 FAILS: the exact LES Reynolds stress cut U_rms by >= "
            + str(int(CEILING_CUT * 100)) + "% relative to NULL on only "
            + str(len(g["V0_cases"])) + " of " + str(N_INSCOPE)
            + " cases.  The apparatus cannot express the correct answer; the "
            "ceiling gate is not repairable by re-registration.  The 80% "
            "threshold is NOT lowered (section 7)")
        return _seal(res, vocab)

    if not g["V1b_hold"]:
        res["verdict"] = "GATE REACHED"
        res["reasons"].append(
            "V0 and V1a hold, V1b FAILS: the criterion also ADMITS the "
            "SCRAMBLED-truth row on " + str(len(g["V0_cases"])
                                             - len(g["V1b_cases"]))
            + " of the " + str(len(g["V0_cases"]))
            + " V0 cases.  A gate that passes a structureless tensor passes "
            "anything; the criterion form is WITHDRAWN, not re-tuned "
            "(section 7, second falsifier), and the apparatus finding stands "
            "alone")
        return _seal(res, vocab)

    res["verdict"] = "PASS"
    res["reasons"].append(
        "V0 holds, V1a and V1b hold on the same " + str(len(g["V1b_cases"]))
        + " of " + str(N_INSCOPE) + " cases (" + ", ".join(g["V1b_cases"])
        + "), V3 holds.  The ceiling criterion is a VALIDATED INSTRUMENT: it "
        "admits the exact-stress reference and rejects the scrambled-truth "
        "planted negative on the same cases")
    return _seal(res, vocab)


def _seal(res, vocab):
    if res["verdict"] not in vocab:
        refuse("verdict '" + str(res["verdict"]) + "' is not in the fixed "
               "vocabulary " + str(vocab))
    return res


# ---------------------------------------------------------------- selftest
def _fires(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except SystemExit as e:
        return int(e.code or 0) == 2
    return False


REAL_U = "/home/ubuntu/closure-data/aposteriori/kaandorp/AR_1_Ret_360__TRUTHR/788/U"
REAL_ULES = ("/home/ubuntu/closure-challenge-benchmark/data/DUCT/"
             "AR_1_Ret_360/0/U_LES")


def _fake_case(root, name, iters=100, converged=True, fields=None,
               exec_lines=None, rc="0", end=True, age_ok=True):
    """A synthetic OpenFOAM case directory, complete by section 8 unless a
    clause is deliberately broken by the caller."""
    fields = list(fields if fields is not None else B.REQUIRED_FIELDS)
    case = os.path.join(root, name)
    os.makedirs(os.path.join(case, "0"))
    os.makedirs(os.path.join(case, "system"))
    tdir = os.path.join(case, str(iters))
    os.makedirs(tdir)
    for f in B.REQUIRED_FIELDS:
        open(os.path.join(case, "0", f), "w").write("0\n")
    open(os.path.join(case, "system", "controlDict"), "w").write(
        "endTime         " + str(iters) + ";\n")
    open(os.path.join(case, "rc"), "w").write(rc + "\n")
    n_exec = iters if exec_lines is None else exec_lines
    lines = []
    for i in range(1, iters + 1):
        lines.append("Time = " + str(i))
        if i <= n_exec:
            lines.append("ExecutionTime = " + str(i * 0.1) + " s  ClockTime = 1 s")
    if converged:
        lines.append("SIMPLE solution converged in " + str(iters) + " iterations")
    if end:
        lines.append("End")
    open(os.path.join(case, LOG_NAME), "w").write("\n".join(lines) + "\n")
    t0 = os.path.getmtime(os.path.join(case, "0", "U"))
    for f in fields:
        p = os.path.join(tdir, f)
        open(p, "w").write("0\n")
        os.utime(p, (t0 + (60 if age_ok else -60), t0 + (60 if age_ok else -60)))
    return case


# The fixture carries MEASURED readings, never a number chosen to be green.
# `_fake_case` and `_row` used to hardcode 1e-6 on every synthetic row -- 5,000x
# tighter than the real CBFS13700 baseline -- which is precisely the R5D failure
# mode in the admissibility channel: a fixture greener than the population.
FIXTURE_DIV = {"AR_1_Ret_360": 3.6402e-05,      # apost AR_1_Ret_360/mean
               "AR_3_Ret_360": 8.6106e-05,      # apost AR_3_Ret_360/truth
               "CBFS13700":    2.9031e-02}      # apost CBFS13700/truth


def _row(u, complete=True, cont=True, status="SCORED", tag="AR_1_Ret_360",
         div=None):
    d = FIXTURE_DIV[tag] if div is None else float(div)
    return {"status": status, "u_rms": u, "complete": complete,
            "continuity_ok": cont and bool(d <= continuity_bar(tag)),
            "divU_rms_over_gradscale": d,
            "continuity_bar": continuity_bar(tag),
            "continuity_instrument_floor": CONTINUITY_FLOOR[tag],
            "continuity_registered_bar": CONTINUITY_MAX,
            "continuity_inside_registered_bar": bool(d <= CONTINUITY_MAX),
            "producer_continuity_sum_local": None,
            "divU_grid_ratio_2h_over_h": None,
            "reason": "synthetic"}


def _table(c4_cut, cx_cut, cases=("AR_1_Ret_360", "AR_3_Ret_360", "CBFS13700")):
    """A synthetic score table with a chosen C4 cut and CX cut on every case."""
    out = {}
    for t in cases:
        u0 = 0.20
        out[t] = {"C0": _row(u0, tag=t),
                  "C1": _row(u0 * (1 - 0.10), tag=t),
                  "C2": _row(u0 * (1 - 0.15), tag=t),
                  "C3": _row(u0 * (1 - 0.29), tag=t),
                  "C4": _row(u0 * (1 - c4_cut), tag=t),
                  "CX": _row(u0 * (1 - cx_cut), tag=t)}
    return out


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    # ---- 0. AMENDMENT A2: clause 8's per-case bars, and their anti-gaming.
    bars = check_continuity_bars()
    note("AG-C2 every per-case bar is >= 10x its MEASURED instrument floor and "
         "never tighter than the registered 1e-4",
         all(bars["bars"][t] >= 10.0 * CONTINUITY_FLOOR[t]
             and bars["bars"][t] >= CONTINUITY_MAX for t in bars["bars"]))
    note("AG-C2 the duct bars are the REGISTERED 1e-4, unmoved",
         bars["bars"]["AR_1_Ret_360"] == 1e-4
         and bars["bars"]["AR_3_Ret_360"] == 1e-4)
    note("continuity_bar REFUSES when the tabulated bar drifts from the rule",
         _fires(lambda: (CONTINUITY_BAR.__setitem__("_probe", 1.0),
                         CONTINUITY_FLOOR.__setitem__("_probe", 1e-9),
                         continuity_bar("_probe"))[-1]))
    CONTINUITY_BAR.pop("_probe", None)
    CONTINUITY_FLOOR.pop("_probe", None)
    note("continuity_bar REFUSES a case with no measured instrument floor",
         _fires(continuity_bar, "NASA_2DWMH"))
    note("AG-C1 every bar ADMITS its named real reading and REJECTS its named "
         "real reading -- measured, per case",
         all(CONTINUITY_AG_ADMIT[t] <= continuity_bar(t)
             < CONTINUITY_AG_REJECT[t] for t in sorted(CONTINUITY_BAR)))
    note("the MEASURED CBFS13700 baseline 5.2451e-03 (frozenk S_null, whose "
         "producer channel reads 5.665e-15) is ADMITTED by CBFS's own bar and "
         "was REJECTED by the retired global bar",
         5.2451e-03 <= continuity_bar("CBFS13700")
         and 5.2451e-03 > CONTINUITY_MAX)
    note("the MEASURED CBFS13700 frozenk L_truth 3.0663e-01 is REJECTED by "
         "CBFS's own bar -- the loosening is not a licence",
         3.0663e-01 > continuity_bar("CBFS13700"))
    note("the MEASURED AR_1_Ret_360 apost truth 1.1425e-04 is REJECTED by the "
         "unmoved duct bar", 1.1425e-04 > continuity_bar("AR_1_Ret_360"))
    note("AG-C5 CBFS13700 stays in the denominator: N_INSCOPE and MIN_CASES "
         "unchanged", N_INSCOPE == 3 and MIN_CASES == 2)

    # ---- 0a. AMENDMENT A3, REPAIR 1: continuity_bar's log10 operands.
    # Each probe is DRIVEN to a REGISTERED refusal (sys.exit 2), not an
    # exception and not a silent return.  _fires returns False for BOTH.
    def _probe_bar(barval, floorval=1e-9):
        CONTINUITY_BAR["_probe"] = barval
        CONTINUITY_FLOOR["_probe"] = floorval
        try:
            return _fires(continuity_bar, "_probe")
        finally:
            CONTINUITY_BAR.pop("_probe", None)
            CONTINUITY_FLOOR.pop("_probe", None)

    note("A3-1 continuity_bar REFUSES a tabulated bar of 0.0 (before A3: "
         "ValueError: math domain error, an UNREGISTERED exception)",
         _probe_bar(0.0))
    note("A3-1 continuity_bar REFUSES a tabulated bar of -1.0 (before A3: "
         "ValueError: math domain error)", _probe_bar(-1.0))
    note("A3-1 continuity_bar REFUSES a tabulated bar of nan (before A3 the "
         "WORST of the four: it RETURNED nan in silence, because every "
         "comparison against nan is False)", _probe_bar(float("nan")))
    note("A3-1 continuity_bar REFUSES a tabulated bar of inf",
         _probe_bar(float("inf")))
    note("A3-1 continuity_bar REFUSES a floor of nan (before A3: ValueError: "
         "cannot convert float NaN to integer)", _probe_bar(1e-1, float("nan")))
    note("A3-1 continuity_bar REFUSES a floor of inf (before A3: OverflowError)",
         _probe_bar(1e-1, float("inf")))
    note("A3-1 continuity_bar REFUSES a floor of 0.0", _probe_bar(1e-1, 0.0))
    note("A3-1 CONTROL: the guards did not swallow the REGISTERED drift "
         "refusal -- a positive finite bar off the rule still refuses",
         _probe_bar(1.0))
    note("A3-1 CONTROL: a positive finite bar ON the rule is NOT refused and "
         "returns its own value -- the guards are not a blanket",
         (lambda: (CONTINUITY_BAR.__setitem__("_probe", 1e-4),
                   CONTINUITY_FLOOR.__setitem__("_probe", 1e-9),
                   continuity_bar("_probe") == 1e-4,
                   CONTINUITY_BAR.pop("_probe", None),
                   CONTINUITY_FLOOR.pop("_probe", None))[2])())
    note("A3-1 the THREE REGISTERED BARS are undisturbed by every probe above",
         continuity_bar("AR_1_Ret_360") == 1e-4
         and continuity_bar("AR_3_Ret_360") == 1e-4
         and continuity_bar("CBFS13700") == 1e-1
         and CONTINUITY_MAX == 1e-4)

    # ---- 0b. AMENDMENT A3, REPAIR 2: the non-gating grid channel cannot raise.
    _gs, _gf = 16, 16
    _x = np.linspace(0.0, 1.0, _gs)
    _y = np.linspace(0.0, 1.0, _gf)
    _X, _Y = np.meshgrid(_x, _y, indexing="ij")
    _C = np.stack([_X.ravel(), _Y.ravel(), np.zeros(_gs * _gf)], axis=1)
    # (b) the REAL trigger: fine gradient scale non-zero, COARSE scale zero.
    # A period-2 field decimates 2x to a CONSTANT.  A UNIFORM field does NOT
    # trigger it -- measured 5.3033e+00 fine / 0.0000e+00 coarse here, against
    # 0/0 for uniform.
    _alt = (np.where((np.arange(_gs) % 2) == 0, 0.0, 1.0)[:, None]
            * np.ones((1, _gf)))
    _U_alt = np.stack([_alt.ravel(), np.zeros(_gs * _gf),
                       np.zeros(_gs * _gf)], axis=1)
    _U_uni = np.tile(np.array([1.0, 0.0, 0.0]), (_gs * _gf, 1))
    # (a) exactly solenoidal (u=y, v=-x): div == 0 with a NON-ZERO gradient
    # scale, so the fine reading is a MEASURED ZERO, not an absent one.
    _U_sol = np.stack([_Y.ravel(), -_X.ravel(), np.zeros(_gs * _gf)], axis=1)
    _U_div = np.stack([_X.ravel(), _Y.ravel(), np.zeros(_gs * _gf)], axis=1)

    def _no_raise(fn, *a):
        try:
            return (True, fn(*a))
        except BaseException as exc:
            return (False, type(exc).__name__ + ": " + str(exc))

    _ok_alt, _v_alt = _no_raise(grid_ratio, _C, _U_alt)
    note("A3-2b grid_ratio does NOT RAISE when the COARSE reading does not "
         "exist (before A3: TypeError: unsupported operand type(s) for /: "
         "'NoneType' and 'float', straight out of score_row)",
         _ok_alt and _v_alt is None, "returned " + repr(_v_alt))
    note("A3-2b the readings behind it are told apart: coarse ABSENT (0/0), "
         "fine PRESENT and non-zero",
         grid_readings(_C, _U_alt)[1] is None
         and (grid_readings(_C, _U_alt)[0] or 0.0) > 0.0,
         "readings " + repr(grid_readings(_C, _U_alt)))
    _ok_sol, _v_sol = _no_raise(grid_readings, _C, _U_sol)
    note("A3-2a a MEASURED ZERO is reported AS 0.0 and not as 'could not "
         "compute' (before A3 the truthiness test `if not fine` silenced it)",
         _ok_sol and _v_sol[0] == 0.0 and _v_sol[0] is not None,
         "fine reading " + repr(_v_sol[0] if _ok_sol else _v_sol))
    note("A3-2a CONTROL: an ABSENT reading is still None, so 0.0 and None are "
         "not the same answer", grid_readings(_C, _U_uni)[0] is None)
    note("A3-2 CONTROL: the channel is NOT blind -- a genuinely divergent "
         "field still returns a real ratio",
         grid_ratio(_C, _U_div) == 1.0,
         "ratio " + repr(grid_ratio(_C, _U_div)))
    note("A3-2 ratio_from_readings is the ONE rule score_row and grid_ratio "
         "share", ratio_from_readings(2.0, 8.0) == 4.0
         and ratio_from_readings(0.0, 8.0) is None
         and ratio_from_readings(None, 8.0) is None
         and ratio_from_readings(2.0, None) is None)

    # ---- 0c. AMENDMENT A3, REPAIR 3: the floor's OWN provenance.
    _prov = bars["floor_provenance"]
    note("A3-3 every registered floor RE-DERIVES from the artifact it names, "
         "by this module's own clause-8 formula, inside the stated band",
         all(r <= FLOOR_PROVENANCE_REL_TOL for _, _, r in _prov.values())
         and set(_prov) == set(CONTINUITY_FLOOR),
         "; ".join("%s tab %.4e got %.6e rel %.2e" % (t, a, b, r)
                   for t, (a, b, r) in sorted(_prov.items())))
    note("A3-3 the re-derivation runs on the SAME mesh score_row scores on: "
         "floor_mesh_centres_path is byte-identical to load_case's own C",
         all(np.array_equal(
             np.asarray(SB.load_case(t, *B.CASES[t])["C"], float).reshape(-1, 3),
             np.asarray(read_field(floor_mesh_centres_path(t)),
                        float).reshape(-1, 3)) for t in sorted(B.CASES)))

    def _mutate_floor(tag, val):
        keep = CONTINUITY_FLOOR[tag]
        CONTINUITY_FLOOR[tag] = val
        try:
            return _fires(check_floor_provenance)
        finally:
            CONTINUITY_FLOOR[tag] = keep

    note("A3-3 a floor MISTYPED BY ONE DECADE is REFUSED -- the defect the "
         "check exists to catch, driven on CBFS13700, whose floor is the whole "
         "justification for its 1e-1 bar",
         _mutate_floor("CBFS13700", 9.6193e-02))
    note("A3-3 the same mistype in the OTHER direction is REFUSED",
         _mutate_floor("CBFS13700", 9.6193e-04))
    note("A3-3 a duct floor mistyped by one decade is REFUSED too",
         _mutate_floor("AR_1_Ret_360", 8.6010e-17))
    note("A3-3 CONTROL: a perturbation INSIDE the stated transcription band is "
         "NOT refused -- the tolerance is a band, not a rubber stamp",
         not _mutate_floor("CBFS13700", 9.6193e-03 * (1.0 + 2e-5)))
    note("A3-3 CONTROL: a perturbation just OUTSIDE the band IS refused",
         _mutate_floor("CBFS13700", 9.6193e-03 * (1.0 + 5e-4)))

    def _absent_artifact(tag):
        keep = CONTINUITY_FLOOR_ARTIFACT[tag]
        CONTINUITY_FLOOR_ARTIFACT[tag] = (os.path.join(
            keep[0], "no_such_artifact", "U"),) + keep[1:]
        try:
            return _fires(rederive_continuity_floor, tag)
        finally:
            CONTINUITY_FLOOR_ARTIFACT[tag] = keep

    # A3-3, THE NARROWING.  The severity originally put on this defect was that
    # "a floor mistyped by one decade would pass every guard and the bar would
    # move with it".  DRIVEN on the pre-A3 module, that scenario DOES NOT
    # EXIST, and the record says so rather than flattering the repair:
    #   * CBFS13700 floor x10 UP with its bar moved consistently to 1e0, and
    #     x10 DOWN with its bar moved to 1e-2: BOTH were ALREADY REFUSED before
    #     A3, by AG-C1, whose named readings 2.9031e-02 and 3.0663e-01 bracket
    #     the bar and pin it to exactly 1e-1 -- no decade but 1e-1 fits between
    #     them, so no floor error can move THAT bar past AG-C1.
    #   * both duct floors are FLOORED at the registered 1e-4 by the rule, so
    #     their bars do not move at all: driven at x10 and at x1e12, the bar
    #     stayed 1e-4 and the pre-A3 module PASSED both.
    # What A3 actually closes is therefore NARROWER and still worth closing: the
    # floor is a MEASURED CLAIM standing on the record with no artifact behind
    # it -- the number amendment A2 cites as its entire justification -- and the
    # two constants that pin the bar (AG_ADMIT / AG_REJECT) are transcriptions
    # from THE SAME census, so they cross-check the bar, not the floor.  A3 is
    # the only path in this file that reaches the named artifact at all.
    def _pre_a3_would_have_passed(tag, floor_val, bar_val=None):
        """Does EVERY guard OTHER than A3's provenance check accept this?"""
        keepf, keepb = CONTINUITY_FLOOR[tag], CONTINUITY_BAR[tag]
        CONTINUITY_FLOOR[tag] = floor_val
        if bar_val is not None:
            CONTINUITY_BAR[tag] = bar_val
        try:
            for t in sorted(CONTINUITY_BAR):
                b = continuity_bar(t)
                if not CONTINUITY_AG_ADMIT[t] <= b < CONTINUITY_AG_REJECT[t]:
                    return False
            return True
        except SystemExit:
            return False
        finally:
            CONTINUITY_FLOOR[tag], CONTINUITY_BAR[tag] = keepf, keepb

    note("A3-3 NARROWING: a CBFS decade mistype with the bar moved WITH it was "
         "ALREADY caught pre-A3 by AG-C1 -- the original severity is withdrawn",
         not _pre_a3_would_have_passed("CBFS13700", 9.6193e-02, 1e0)
         and not _pre_a3_would_have_passed("CBFS13700", 9.6193e-04, 1e-2))
    note("A3-3 NARROWING: what WAS undefended and now is -- a duct floor wrong "
         "by twelve decades, bar unmoved at 1e-4, passed every pre-A3 guard",
         _pre_a3_would_have_passed("AR_1_Ret_360", 8.6010e-06)
         and _mutate_floor("AR_1_Ret_360", 8.6010e-06))
    note("A3-3 NARROWING: and a CBFS floor wrong INSIDE its own decade window "
         "(5.0e-03 for 9.6193e-03), bar unmoved at 1e-1, passed every pre-A3 "
         "guard -- this is the number A2's justification is written on",
         _pre_a3_would_have_passed("CBFS13700", 5.0e-03)
         and _mutate_floor("CBFS13700", 5.0e-03))

    note("A3-3 an ABSENT floor artifact is REFUSED, not skipped",
         all(_absent_artifact(t) for t in sorted(CONTINUITY_FLOOR_ARTIFACT)))
    note("A3-3 a case that names no floor artifact at all is REFUSED",
         _fires(rederive_continuity_floor, "NASA_2DWMH"))
    note("A3-3 the floors and artifacts are restored after every probe above, "
         "and the THREE REGISTERED BARS are still 1e-4 / 1e-4 / 1e-1",
         all(r <= FLOOR_PROVENANCE_REL_TOL
             for _, _, r in check_floor_provenance().values())
         and continuity_bar("AR_1_Ret_360") == 1e-4
         and continuity_bar("AR_3_Ret_360") == 1e-4
         and continuity_bar("CBFS13700") == 1e-1)
    # ---- 0b. AMENDMENT A4, AG-C8: the CENSUS re-derived from the POPULATION.
    # Every probe below is DRIVEN to a REGISTERED refusal (sys.exit 2) and the
    # UNMUTATED CONTROL is shown to stay SILENT.  A check that cannot be shown
    # to fire is decoration (L-529).  The mutations are driven on
    # `AR_1_Ret_360` -- the cheapest case, and the one whose `min` cell A4
    # corrected -- so the selftest pays for one duct, not the whole population.
    def _mutate_census(tag, idx, val):
        keep = CONTINUITY_MEASURED[tag]
        t = list(keep)
        t[idx] = val
        CONTINUITY_MEASURED[tag] = tuple(t)
        try:
            return _fires(check_case_census, tag)
        finally:
            CONTINUITY_MEASURED[tag] = keep

    def _mutate_named(table, tag, val):
        keep = table[tag]
        table[tag] = val
        try:
            return _fires(check_case_census, tag)
        finally:
            table[tag] = keep

    def _absent_population(tag):
        keep = WU_POPULATION_ROOTS
        globals()["WU_POPULATION_ROOTS"] = tuple(
            os.path.join(r, "no_such_population") for r in keep)
        try:
            return _fires(check_case_census, tag)
        finally:
            globals()["WU_POPULATION_ROOTS"] = keep

    def _mutate_admitted_old(val):
        keep = CONTINUITY_ADMITTED_OLD
        globals()["CONTINUITY_ADMITTED_OLD"] = val
        try:
            return _fires(check_census_provenance)
        finally:
            globals()["CONTINUITY_ADMITTED_OLD"] = keep

    note("A4 AG-C8 CONTROL: the UNMUTATED census re-derives and stays SILENT "
         "-- all 54 rows, every cell, no refusal",
         isinstance(bars.get("census_provenance"), dict)
         and bars["census_provenance"]["measured_rows"] == 54
         and bars["census_provenance"]["admitted_per_case_bars"] == 21
         and bars["census_provenance"]["admitted_retired_global_bar"] == 8
         and not _fires(check_case_census, "AR_1_Ret_360"))
    note("A4 AG-C8 a MUTATED n_admitted is REFUSED -- the cell AG-C1's "
         "non-vacuity refusal is built on, compared EXACTLY",
         _mutate_census("AR_1_Ret_360", 3, 5)
         and _mutate_census("AR_1_Ret_360", 3, 3))
    note("A4 AG-C8 a MUTATED n_rows is REFUSED -- the denominator of the AG-C4 "
         "direction disclosure", _mutate_census("AR_1_Ret_360", 2, 17))
    note("A4 AG-C8 a MUTATED n_rejected is REFUSED",
         _mutate_census("AR_1_Ret_360", 4, 13))
    note("A4 AG-C8 the SLIP THIS AMENDMENT CORRECTED is refused if reinstated: "
         "AR_1_Ret_360's min back at its floor literal 8.6010e-18",
         _mutate_census("AR_1_Ret_360", 0, 8.6010e-18))
    note("A4 AG-C8 CONTROL: a min perturbation INSIDE the stated transcription "
         "band is NOT refused -- the tolerance is a band, not a rubber stamp",
         not _mutate_census("AR_1_Ret_360", 0, 3.8536e-18 * (1.0 + 2e-5)))
    note("A4 AG-C8 CONTROL: a min perturbation just OUTSIDE the band IS "
         "refused", _mutate_census("AR_1_Ret_360", 0, 3.8536e-18 * (1.0 + 5e-4)))
    note("A4 AG-C8 a tabulated min of nan is REFUSED, not passed in silence -- "
         "every comparison against nan is False and this file has been bitten "
         "by exactly that shape before",
         _mutate_census("AR_1_Ret_360", 0, float("nan"))
         and _mutate_census("AR_1_Ret_360", 1, float("inf")))
    note("A4 AG-C8 an AG-C1 ADMIT reading that OCCURS IN NO ROW of the "
         "population is REFUSED -- AG-C1 calls it a named REAL reading",
         _mutate_named(CONTINUITY_AG_ADMIT, "AR_1_Ret_360", 1.2345e-05))
    note("A4 AG-C8 an AG-C1 REJECT reading that occurs in no row is REFUSED "
         "too", _mutate_named(CONTINUITY_AG_REJECT, "AR_1_Ret_360", 9.8765e-04))
    note("A4 AG-C8 an ABSENT population root is REFUSED, not skipped -- a "
         "census re-derived from nothing would be a vacuous zero",
         _absent_population("AR_1_Ret_360"))
    note("A4 AG-C8 a MUTATED CONTINUITY_ADMITTED_OLD is REFUSED -- the other "
         "half of the AG-C4 direction disclosure, re-derived against "
         "CONTINUITY_MAX over the same 54 rows",
         _mutate_admitted_old(9) and _mutate_admitted_old(7))
    note("A4 AG-C8 the census, named readings and population are restored "
         "after every probe above, and the THREE REGISTERED BARS are still "
         "1e-4 / 1e-4 / 1e-1",
         CONTINUITY_MEASURED["AR_1_Ret_360"] == (3.8536e-18, 2.5116e-03,
                                                 18, 4, 14)
         and CONTINUITY_ADMITTED_OLD == 8
         and len(WU_POPULATION_ROOTS) == 2
         and CONTINUITY_MAX == 1e-4
         and continuity_bar("AR_1_Ret_360") == 1e-4
         and continuity_bar("AR_3_Ret_360") == 1e-4
         and continuity_bar("CBFS13700") == 1e-1)

    note("no fixture row carries the retired hardcoded 1e-6",
         all(v != 1e-6 for v in FIXTURE_DIV.values()))

    tmp = tempfile.mkdtemp(prefix="rc3_ceiling_selftest_")
    try:
        # ---- 1. the section 6 control, on a REAL simpleFoam field, both
        #         directions, and BOTH directions shown to FIRE.
        if os.path.exists(REAL_U) and os.path.exists(REAL_ULES):
            UL = np.asarray(read_field(REAL_ULES), float).reshape(-1, 3)
            uref = float(np.mean(np.linalg.norm(UL, axis=1)))
            rec = plant_control(REAL_U, UL, uref, os.path.join(tmp, "ctl"))
            note("V3 control PASSES on a real simpleFoam-written U field",
                 rec["verdict"] == "PASS",
                 "U_rms moved %.3g" % rec["u_rms_move"])
            note("V3 direction A FIRES against a BLINDED reader (returns the "
                 "original whatever path it is given)",
                 _fires(plant_control, REAL_U, UL, uref,
                        os.path.join(tmp, "ctlA"),
                        lambda p, _c=[None]: (_c.__setitem__(0, _c[0] if _c[0]
                                              is not None else read_field(REAL_U))
                                              or _c[0])))

            def noisy(path, _state=[0]):
                a = np.asarray(read_field(path), float)
                _state[0] += 1
                return a + (1e-9 if _state[0] > 1 else 0.0)

            note("V3 direction B FIRES against a NON-DETERMINISTIC reader",
                 _fires(plant_control, REAL_U, UL, uref,
                        os.path.join(tmp, "ctlB"), noisy))
            note("V3 FIRES when the field it is pointed at does not exist",
                 _fires(plant_control, os.path.join(tmp, "nope"), UL, uref,
                        os.path.join(tmp, "ctlC")))
        else:
            note("V3 control has a real simpleFoam field to work on", False,
                 "absent: " + REAL_U)

        # ---- 2. section 8, each clause shown to FIRE on its own violation.
        good = _fake_case(tmp, "good")
        okc, reason, info = completion(good)
        note("completion PASSES a synthetic complete case", okc, reason)
        c = _fake_case(tmp, "bad_rc", rc="137")
        note("clause 1 FIRES on rc != 0", not completion(c)[0])
        c = _fake_case(tmp, "bad_end", end=False)
        note("clause 2 FIRES on a missing End line", not completion(c)[0])
        c = _fake_case(tmp, "bad_stop", converged=False, iters=50)
        open(os.path.join(c, "system", "controlDict"), "w").write(
            "endTime         100;\n")
        note("clause 3 FIRES when the run neither converged nor reached endTime",
             not completion(c)[0])
        c = _fake_case(tmp, "bad_fields",
                       fields=[f for f in B.REQUIRED_FIELDS if f != "phi"])
        note("clause 4 FIRES on a missing field (phi)", not completion(c)[0])
        c = _fake_case(tmp, "bad_exec", exec_lines=90)
        note("clause 5 FIRES on ExecutionTime lines != steps taken",
             not completion(c)[0])
        c = _fake_case(tmp, "bad_age", age_ok=False)
        note("clause 6 AGE GUARD FIRES on a field older than 0/U",
             not completion(c)[0])
        c = _fake_case(tmp, "bad_zero")
        os.remove(os.path.join(c, "0", "U"))
        note("clause 6 FIRES when 0/U is absent (no age reference)",
             not completion(c)[0])
        note("completion FIRES on an absent case directory",
             not completion(os.path.join(tmp, "absent"))[0])

        # ---- 2b. FIXTURE-VERSUS-PRODUCER PARITY (FINDING B, and the check the
        #          R5D freeze did not have).  The synthetic case above proves
        #          only that the fixture satisfies the clause.  These rows are
        #          REAL `simpleFoam` output on disk, reached by symlink, with
        #          nothing added but the file rc3_run.record() writes.
        import rc3_run as RUN                                   # noqa: E402
        for src in RUN.REAL_CASES:
            nm = (os.path.basename(os.path.dirname(src)) + "/"
                  + os.path.basename(src))
            if not os.path.isdir(src):
                note("PARITY: real producer case present: " + nm, False,
                     "absent")
                continue
            dst = RUN.link_real_case(src, os.path.join(
                tmp, "parity_" + nm.replace("/", "_")))
            done = os.path.join(src, RUN.DONE_NAME)
            rrc = 0
            if os.path.exists(done):
                rrc = int(open(done).read().strip().split("rc=")[1].split()[0])
            RUN.record(dst, rrc, 1.0)
            okp, rp, _ip = completion(dst)
            note("PARITY: section 8 clauses 1-6 SATISFIED by REAL producer "
                 "output plus only the file rc3_run writes -- " + nm, okp, rp)
            os.remove(os.path.join(dst, RUN.RC_NAME))
            note("PARITY, OTHER DIRECTION: the same real tree WITHOUT that file "
                 "fails clause 1 -- which is exactly FINDING B, measured 0 of "
                 "54 on the predecessor population",
                 not completion(dst)[0])
        if os.path.isdir(RUN.REAL_TIMED_OUT):
            dst = RUN.link_real_case(RUN.REAL_TIMED_OUT,
                                     os.path.join(tmp, "parity_timedout"))
            RUN.record(dst, 124, 3600.0)
            note("PARITY: a REAL `timeout 3600` row (rc=124, no End line, "
                 "n_exec = n_time - 1) is REJECTED",
                 not completion(dst)[0])

        # ---- 3. the gate arithmetic and the verdict ladder.
        note("criterion ADMITS a row at exactly the 80% bar",
             criterion(0.80) == "PASS")
        note("criterion REJECTS a row at 79.9%", criterion(0.799) == "FAIL")
        note("cut() REFUSES a zero NULL denominator", _fires(cut, 0.1, 0.0))

        v = verdict(_table(c4_cut=0.90, cx_cut=0.05), True,
                    {t: True for t in ("AR_1_Ret_360", "AR_3_Ret_360",
                                       "CBFS13700")})
        note("PASS when C4 is admitted and CX is rejected on all three",
             v["verdict"] == "PASS", v["verdict"])
        note("V2 publishes the b-only ceiling with its configuration named",
             v["gates"]["per_case"]["AR_1_Ret_360"]["b_only_ceiling_config"] == "C3")
        note("V2 records the predecessors' 30% and 50% bars as FALSIFIED BY "
             "MEASUREMENT where the measured ceiling falls below them",
             v["gates"]["per_case"]["AR_1_Ret_360"]
             ["bars_falsified_by_measurement"] == [0.30, 0.50],
             "measured ceiling cut %.3f"
             % v["gates"]["per_case"]["AR_1_Ret_360"]["b_only_ceiling_cut"])

        # THE REJECTING LIMB, shown rejecting: CX admitted -> GATE REACHED.
        v2 = verdict(_table(c4_cut=0.90, cx_cut=0.90), True,
                     {t: True for t in ("AR_1_Ret_360", "AR_3_Ret_360",
                                        "CBFS13700")})
        note("GATE REACHED when the criterion ALSO admits SCRAMBLED (V1b's "
             "rejecting limb is what fails, and it is what fires)",
             v2["verdict"] == "GATE REACHED", v2["verdict"])
        note("V1b is the limb that failed, not V0/V1a",
             v2["gates"]["V0_hold"] and not v2["gates"]["V1b_hold"])

        v3 = verdict(_table(c4_cut=0.50, cx_cut=0.05), True,
                     {t: True for t in ("AR_1_Ret_360", "AR_3_Ret_360",
                                        "CBFS13700")})
        note("GATE FAIL when the exact stress does not clear 80%",
             v3["verdict"] == "GATE FAIL", v3["verdict"])

        v4 = verdict(_table(c4_cut=0.90, cx_cut=0.05), False,
                     {t: True for t in ("AR_1_Ret_360",)})
        note("NOT A RESULT when the V3 reader control fails",
             v4["verdict"] == "NOT A RESULT")

        t5 = _table(c4_cut=0.90, cx_cut=0.05)
        t5["CBFS13700"]["C4"]["complete"] = False
        v5 = verdict(t5, True, {t: True for t in ("AR_1_Ret_360",
                                                  "AR_3_Ret_360", "CBFS13700")})
        note("NOT A RESULT when any scored row fails strict completion",
             v5["verdict"] == "NOT A RESULT")

        t6 = _table(c4_cut=0.90, cx_cut=0.05)
        t6["CBFS13700"]["C1"] = _row(0.18, tag="CBFS13700", div=3.0663e-01)
        v6 = verdict(t6, True, {t: True for t in ("AR_1_Ret_360",
                                                  "AR_3_Ret_360", "CBFS13700")})
        note("NOT A RESULT on the MEASURED CBFS13700 frozenk L_truth continuity "
             "of 3.0663e-01, which is outside even that case's own 1e-1 bar",
             v6["verdict"] == "NOT A RESULT")
        note("gate_arithmetic REFUSES (sys.exit 2) if a continuity-violating "
             "row is handed to it directly -- no silent acceptance path exists",
             _fires(gate_arithmetic, t6))
        t7 = _table(c4_cut=0.90, cx_cut=0.05)
        t7["CBFS13700"]["C2"]["complete"] = False
        note("gate_arithmetic REFUSES an incomplete row handed to it directly",
             _fires(gate_arithmetic, t7))

        v8 = verdict(_table(c4_cut=0.90, cx_cut=0.05), True,
                     {"AR_1_Ret_360": True, "AR_3_Ret_360": False,
                      "CBFS13700": False})
        note("NOT A RESULT when C4's fixed point contracts on fewer than 2 of 3",
             v8["verdict"] == "NOT A RESULT")

        t9 = _table(c4_cut=0.90, cx_cut=0.05)
        for t in ("AR_3_Ret_360", "CBFS13700"):
            t9[t]["C0"]["status"] = "BLOCKED"
        v9 = verdict(t9, True, {t: True for t in ("AR_1_Ret_360",
                                                  "AR_3_Ret_360", "CBFS13700")})
        note("BLOCKED when fewer than 2 in-scope cases can be scored, and the "
             "denominator is not rescaled", v9["verdict"] == "BLOCKED")

        note("_seal REFUSES a label outside the fixed vocabulary",
             _fires(_seal, {"verdict": "roughly converged"},
                    ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT",
                     "BLOCKED", "PENDING")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(n) for n, _, _ in ok)
    for name, passed, detail in ok:
        print(("  %-" + str(width) + "s  %s%s")
              % (name, "PASS" if passed else "FAIL",
                 ("   [" + detail + "]") if detail else ""))
    bad = [n for n, p, _ in ok if not p]
    if bad:
        sys.stderr.write("SELFTEST FAILED: " + "; ".join(bad) + "\n")
        raise SystemExit(1)
    print("rc3_ceiling selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def score_all(root=B.ROOT, out_path=None):
    """The scoring pass.  Refuses while RC3 is DRAFT/UNFROZEN."""
    B.refuse_if_unfrozen()
    check_continuity_bars()          # amendment A2: AG-C1/C2/C4/C5, every pass
    scratch = os.path.join(root, "_control")
    rows, fixedpoint, plant = {}, {}, None
    for tag in sorted(B.CASES):
        src, fam = B.CASES[tag]
        bench = SB.load_case(tag, src, fam)
        UL = np.asarray(bench["U_LES"], float).reshape(-1, 3)
        uref = float(np.mean(np.linalg.norm(UL, axis=1)))
        rows[tag] = {}
        for cfg in ("C0", "C1", "C2", "C3", "C4", "CX"):
            case = os.path.join(root, tag, cfg)
            if not os.path.isdir(case):
                rows[tag][cfg] = {"status": "BLOCKED",
                                  "reason": "case directory absent: " + case}
                continue
            okc, reason, info = completion(case)
            if plant is None:
                lt = r4_lib.latest_time(case)
                plant = plant_control(os.path.join(case, lt, "U"), UL, uref,
                                      scratch)
            row = {"status": "SCORED", "complete": okc, "reason": reason,
                   "completion": info}
            if okc:
                row.update(score_row(tag, case, bench))
            else:
                row["continuity_ok"] = False
            rows[tag][cfg] = row
        fp = os.path.join(root, tag, "C4", "fixedpoint.json")
        fixedpoint[tag] = (json.load(open(fp)).get("contracted", False)
                           if os.path.exists(fp) else False)
    if plant is None:
        refuse("no case directory carried a field for the section 6 control; "
               "a zero from an unexercised reader is not evidence")
    res = verdict(rows, plant.get("verdict") == "PASS", fixedpoint)
    res["plant_control"] = plant
    res["rows"] = rows
    print("VERDICT: " + res["verdict"])
    for r in res["reasons"]:
        print("  " + r)
    if out_path:
        json.dump(res, open(out_path, "w"), indent=1, default=str)
    if res["verdict"] == "NOT A RESULT":
        raise SystemExit(2)
    return res


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--score" in argv:
        score_all()
        return 0
    sys.stderr.write("usage: rc3_ceiling.py --selftest | --score\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
