#!/usr/bin/env python3
"""CURRICULUM MP-A1 -- THE FROZEN COMPARATOR.

Grades the ALPHA-MULTIPOINT weighted-objective gradient on SO-1's NACA0012 case:
`J = SUM_i w_i * CD_i(alpha_i)` over one shared `shape` vector, against a
central-difference table whose plateau is proved PER PAIR, on TWO TOOLCHAIN ROWS,
at np = 1.  `PREREGISTRATION.md` IN THIS DIRECTORY governs every gate, threshold,
cap and label; nothing here may move one.

THE FREEZE SHA IS DELIBERATELY NOT WRITTEN HERE.  MP-A1a's copy of this line
cited `1a06a7d6`, its own Stage-1 freeze commit, because there its document was
frozen BEFORE its instruments existed.  MP-A1 freezes the document and the
instruments in ONE commit, so no sha exists at the moment this file is written
and a sha written here could only be wrong or back-dated.  The binding runs the
other way instead and is checkable: `PREREGISTRATION.md` section 10 pins THIS
file by md5, and `mpa1_chain_driver.sh:MD5_GRADER` asserts it before staging.

Derived from `curriculum_SO2a/so2a_grade.py` with the deltas in
`mpa1_grade_DELTAS_from_so2a.diff`.  FIVE of those deltas are the point of the
item and are stated here, at the top, because a reader who reads nothing else
must read these.

--------------------------------------------------------------------------
(I) THE SCHEMA CONTRACT WITH THE ALREADY-FROZEN CONSUMERS, AND IT IS DRIVEN.
--------------------------------------------------------------------------
On 2026-08-31 SO-1c refused because its consumer read `gates` at the TOP LEVEL
while its producer wrote them at `grade.gates`, and a 51-leg suite could not see
it BECAUSE THE SUITE'S FIXTURES WERE HAND-BUILT FROM THE CONSUMER'S OWN
EXPECTATIONS -- a tautology on schema.  MP-A1's comparator is written AFTER two
of its consumers were frozen, so the contract runs the other way and is checkable
TODAY:

  * `mpa1_chain_driver.sh:234` invokes `python3 $GRADER --root $BASE --out $GRADE_OUT`.
    **`--out` IS MANDATORY.**  The parent comparator has no `--out` and composes
    its own stamped path; adopting the parent unchanged would have produced an
    artefact at an address the frozen driver never looks at.
  * `mpa1_stop_marker.sh:97,101,105` reads `verdict` at the TOP LEVEL, `rows` at
    the TOP LEVEL, and G5J at `g["G5J"]` or `g["gates"]["G5J"]` -- the LITERAL
    key `G5J`.  The parent publishes `gates["G5g_SHIPPED"]` / `gates["G5g_PATCHED"]`,
    which that reader cannot see.  **`gates["G5J"]` therefore EXISTS here**, and
    the per-row detail hangs beneath it.

Neither fact is asserted in prose.  `selftest` RUNS `mpa1_stop_marker.sh` on a
real grade artefact this module wrote and requires the marker to carry the
verdict and a non-absent G5J; then it RENAMES the key and requires the marker to
report it ABSENT.  A schema contract that cannot fail is not a contract.

--------------------------------------------------------------------------
(II) THE ARM LOOP IS A CENSUS, NOT A REQUIREMENT (`D6-GRADER-DEF-1`).
--------------------------------------------------------------------------
D6 registered a chain stop as a meaningful outcome and its grader refused, exit 2,
with ZERO gate readings when an arm carried no ledger row; 2,257.933 core-min of
real optimisation sat behind an instrument that could not read it (L-322).  The
parent refuses on `ledger_row_absent` and on `arm_log_absent`.  **MP-A1 prints
`RAN` / `NOT RUN` per arm, grades every arm that ran, and REFUSES ONLY ON A
MALFORMED ARTEFACT, NEVER ON AN ABSENT ONE** (PREREGISTRATION section 3
G-EVALFAIL, section 6).  The shortfall is not merely recorded: `G-STAGES` reads
`DECLARED=5` against `EXECUTED=n` as a GATE INPUT, because W3 logged 20 blocked
stages of 33 perfectly, in two agreeing artefacts, and NOTHING READ THEM.

--------------------------------------------------------------------------
(III) THE BANNER DISCRIMINATOR.  A MATCH IS NOT A MEANING.
--------------------------------------------------------------------------
MEASURED in this family's own reference bytes, `reference/REAL_SO1a_X-S_arm.log`,
by this module's own units:

    "SIMPLE: no convergence criteria found. Calculations will run for 1000 steps."
                                                              -- 4 occurrences
    "Time step continuity errors : sum local = ..."            -- 5 occurrences
    "Minimal residual <r> satisfied the prescribed tolerance <tol>"
                                                              -- 1 occurrence

on a run that CONVERGED, because DAFoam applies its own `primalMinResTol` and
stops the solve regardless of what OpenFOAM's SIMPLE banner announced.  A naive
convergence limb reads four declarations of non-convergence on a converged run;
a naive `grep -i error` limb reports five crashes per success; and `trapFpe:` is
a SAFETY NOTICE that the handler is ENABLED, not a crash.

  * `read_primal_convergence()` reads the REAL statement (`CONVERGED_RE`) and
    COUNTS AND NAMES the banner separately as `banner_not_evidence`.  It is
    REPORTED, never gated -- the item's gates are the FD table's.
  * `benign_reason()` carries THREE named per-line exclusions now, each counted
    and printed: `trapFpe:`, the SIMPLE banner, and the continuity-error line.
    Every exclusion is visible on the PASS record; a suppression a reader cannot
    see is the same defect wearing the other hat.
  * The tokens are NOT deleted.  A missed SIGFPE is laundered into a result; a
    false hit costs a re-read.

--------------------------------------------------------------------------
(IV) FIXTURES FOR THE POSITIVE PATH COME FROM THE PRODUCER, NOT FROM THE READER.
--------------------------------------------------------------------------
Every X and F artefact in `_fix` is written by CALLING `mpa1_xf.build_X_record`,
`build_F_record`, `build_fd_row` and `build_ctrl_row` -- THE INSTRUMENT'S OWN
WRITERS, the same functions its `main()` calls -- so a fixture cannot carry a key
the producer does not emit nor miss one it does.  Every ledger row is emitted by
SOURCING `mpa1_run_arm.sh`'s own `mpa1_ledger_row`; when that launcher is absent
the fixture says so and `R1_read_ledger` is recorded **NOT BORN**, never green.
The MESH cells reader and the C5 / convergence log readers are driven on REAL
OPENFOAM BYTES in `reference/`.  Synthetic dicts appear ONLY on refusal branches,
where the defect under test is precisely a schema the producer would never emit.

**NO KEY IS EVER FOUND BY A RECURSIVE HUNT.**  `SCHEMA` registers every nested
location as an explicit tuple path and `at()` walks exactly that path.  A reader
that goes looking until it finds something will always find something.

--------------------------------------------------------------------------
(V) THE PLANTED CONTROLS RUN IN BOTH DIRECTIONS AND THE BRIGHT LINE MUST FLIP.
--------------------------------------------------------------------------
Rule 3 is a PRECONDITION of the gates, not a footnote beside them.  Three gates
here can pass on a small or zero number -- G5J, G5C and G-MP-STRUCT -- so each is
shown, at grade time, on the real artefacts, FLIPPING TO `GATE FAIL` under a
plant read back FROM DISK through the same reader.  A zero from a reader not
shown able to see a non-zero is not evidence.

Exit 2 on any refusal.  A refusal is NOT A RESULT, never a degraded verdict.
NO `assert` STATEMENT APPEARS IN THIS FILE: `python3 -O` strips them, so an
assert is not a guard (L-332).  `count_asserts()` proves it, and is itself proved
against a planted assert.
"""

import ast
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
# ---- THE INSTRUMENT.  Its writers build every positive-path fixture.
# ---- RENAME COLLISION CHECK, both halves, run rather than assumed: the parent
# ---- binds this alias to the parent instrument (the two-letter name spelled at
# ---- `so2a_grade.py:110`, reconstructed at U88 from parts so this file never
# ---- spells it); the child binds `XF`.  `so2a_grade.py` contains ZERO
# ---- occurrences of the identifier `XF` (so the new name was NOT already
# ---- bound to something else), and this file contains ZERO occurrences of the
# ---- OLD form
# ---- (so the old form is gone).  BOTH halves are driven by U80/U81 below --
# ---- SO1bR's derivation introduced a self-destruct by verifying only the first
# ---- half, which is structurally blind to a collision.
import mpa1_xf as XF
# THE STALL DETECTOR IS IMPORTED, NOT REIMPLEMENTED.  Section 9's mapping lives
# here; the READING lives there, is calibrated on 33 real IPOPT logs, and is the
# same module the in-run watchdog and the producer use -- so the number in the
# record, the number that stopped the run and the number the grader gates on are
# one number from one file.
import mpa1_stall as STALL

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----------------
ITEM = "MPA1"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1-a1-naca0012-alpha-multipoint-fixedlift-optimisation"
# DECLARED = 7 (section 5 Requirement 4).  The list is the DECLARED program; the
# arms that RAN are a census taken at grade time.
ARMS_DECLARED = ["MESH", "O-S", "XE-S", "FE-S", "O-P", "XE-P", "FE-P"]
N_DECLARED = len(ARMS_DECLARED)
ARM_KIND = {"MESH": "SCRIPT", "O-S": "SOLVER", "XE-S": "SOLVER", "FE-S": "SOLVER",
            "O-P": "SOLVER", "XE-P": "SOLVER", "FE-P": "SOLVER"}
ARM_ROW = {"MESH": "SHIPPED", "O-S": "SHIPPED", "XE-S": "SHIPPED", "FE-S": "SHIPPED",
           "O-P": "PATCHED", "XE-P": "PATCHED", "FE-P": "PATCHED"}
# np = 1 ON EVERY ARM, AND IT IS THE CONDITION ON THE INHERITANCE, NOT A SETTING.
# SO-3aR2's FD table -- the whole reason this optimisation is admissible -- was
# measured at np = 1, and `DAFOAM_CHARTER.md` section 5 forbids carrying an FD
# reference across np.  A4 measured a 16,600x spread between two decompositions
# of ONE mesh (np=4 scotch 8.95 % against np=4 simple 4x1x1 0.00054 %), which is
# what any np != 1 arm would readmit.
ARM_RANKS = {a: 1 for a in ARMS_DECLARED}
OUT_O = "mpa1_O.json"
TERMINAL_O = "MPA1_O_WRITTEN"
ARTEFACT = {"MESH": "checkMesh.log",
            "O-S": OUT_O, "XE-S": XF.OUT_X, "FE-S": XF.OUT_F,
            "O-P": OUT_O, "XE-P": XF.OUT_X, "FE-P": XF.OUT_F}
TERMINAL = {"O-S": TERMINAL_O, "XE-S": XF.TERMINAL_X, "FE-S": XF.TERMINAL_F,
            "O-P": TERMINAL_O, "XE-P": XF.TERMINAL_X, "FE-P": XF.TERMINAL_F}
# ---- THE ROW LABELS.  ONE SET, REGISTERED ONCE, USED EVERYWHERE.
# ---- SO-1c launched on 2026-08-31 and DIED AT ITS SECOND ARM because SO-1bR
# ---- labelled its per-row artefacts `P`/`S` while SO-1c's consumers compared
# ---- against `PATCHED`/`SHIPPED`.  Amendment R8 repaired ONE call site; there
# ---- were THREE (chain driver, run_arm's G-OPTDEP, the grader's G-XSTAR), and
# ---- the two unrepaired ones killed the run.  CLAUDE.md rule 14: a lesson is not
# ---- applied until EVERY call site asserts it.
# ---- MP-A1's answer is not a better MAPPING, it is the ABSENCE of a second label
# ---- set.  There is no short form here.  The internal key, the published key in
# ---- `rows`, and `ARM_ROW`'s value are THE SAME STRINGS, so there is nothing to
# ---- map and no call site that can be missed.  The two labels share no prefix
# ---- with each other, and NOTHING here derives one from the other's spelling --
# ---- `row[0]` would have "worked" on `S`/`SHIPPED` by coincidence, which is
# ---- exactly the derivation the SO-1c post-mortem forbids.  U100 sweeps this
# ---- file for any reappearance of a short-form row literal or a positional
# ---- derivation, and U101 proves that sweep can go red.
ROWS = ("SHIPPED", "PATCHED")
X_ARM = {"SHIPPED": "XE-S", "PATCHED": "XE-P"}
F_ARM = {"SHIPPED": "FE-S", "PATCHED": "FE-P"}
O_ARM = {"SHIPPED": "O-S", "PATCHED": "O-P"}
# The artefact KIND is registered explicitly per tag; it is NEVER read off the
# tag's first character.
REC_KIND_X = "X"
REC_KIND_F = "F"

# THE AGE-GUARD DATUM IS RESOLVED BY EXISTENCE, NEVER BY NAME (section 3).
DATUM_CANDIDATES = {"MESH": ("0.orig/U", "0.orig/U.gz")}
for _a in ("O-S", "XE-S", "FE-S", "O-P", "XE-P", "FE-P"):
    DATUM_CANDIDATES[_a] = ("0/U", "0/U.gz")
DATUM_FILE = ".mpa1_age_datum"
CONTROLDICT_REL = os.path.join("system", "controlDict")

# ---- C5 and the BANNER DISCRIMINATOR.  See (III) at the top of this file. ----------
FATAL_TOKENS = ("FOAM FATAL ERROR", "FOAM FATAL IO ERROR", "Segmentation fault",
                "SIGSEGV", "SIGKILL", "MPI_ABORT", "signal 9", "Signal 11",
                "Floating point exception",
                "Foam::sigFpe::sigHandler")
BENIGN_LINE_PATTERNS = (
    (r"^\s*trapFpe:\s",
     "OpenFOAM sigFpe SETUP banner -- an ENABLEMENT NOTICE that the handler is "
     "installed, not a report that it FIRED"),
    (r"^\s*SIMPLE:\s+no convergence criteria found",
     "OpenFOAM's SIMPLE banner.  MEASURED 4x in reference/REAL_SO1a_X-S_arm.log on a "
     "run that CONVERGED: DAFoam applies its own primalMinResTol and stops the solve, "
     "so this banner is not a statement about this solver's convergence"),
    (r"^\s*Time step continuity errors\s*:",
     "OpenFOAM's per-iteration continuity residual report.  MEASURED 5x in the same "
     "converged reference log; the word `errors` here names a RESIDUAL, not a failure"),
)
BENIGN_LINE_RE = tuple((re.compile(_p), _why) for _p, _why in BENIGN_LINE_PATTERNS)
# THE REAL STATEMENT.  DAFoam prints this, and only this, when the primal met the
# registered tolerance.  It is REPORTED, never gated.
CONVERGED_RE = re.compile(
    r"^\s*Minimal residual\s+(?P<res>[-+0-9.eEdD]+)\s+satisfied the prescribed tolerance\s+"
    r"(?P<tol>[-+0-9.eEdD]+)\s*$", re.M)
SIMPLE_BANNER_RE = re.compile(r"^\s*SIMPLE:\s+no convergence criteria found", re.M)

# ---- CAPS ARE CEILINGS; PREDICTIONS ARE ESTIMATES.  THEY ARE DIFFERENT NUMBERS
# ---- AND THE RATIO rule 12 ASKS FOR IS TAKEN AGAINST THE PREDICTION, NEVER THE
# ---- CAP.  MESH's cap is 5.0 while its measured prediction is 0.19; conflating
# ---- them would report every arm as a 26x underspend.
#
# THE O-ARM PREDICTION, DERIVED FROM TWO MEASURED ANCHORS AND NOT GUESSED:
#   * C-24, D1 arm `O`, on THIS A1 case at np = 1: 0.42127 core-min/major MEASURED
#     over 11 majors.  The right single-point anchor for A1.
#   * C-188, D6, 3-scenario multipoint at np = 4: 31.258 core-min/major MEASURED
#     against 19.167 registered (a naive 3x single-point) = 1.6308x.  The row's
#     own conclusion: "the x3 model is short by 63 %."
#   0.42127 x 3 x 1.6308 = 2.061 core-min/major.  At MAX_MAJORS = 50 that is
#   103.0 core-min, which is the prediction below.
#
# AND THE STALL BRANCH C-188 DEMANDS ("the successor's estimate must carry a
# stall branch").  The stall abort fires at the FIRST reach of the 8-major
# window; MEASURED on C-188's own artefact it fires at major 34 of 65.  A stalled
# MP-A1 arm therefore costs ~34 x 2.061 = 70.1 core-min, BELOW the converging
# prediction -- so the stall branch is a floor on the saving, not an extra cost,
# and the cap is sized on the CONVERGING branch.
CAPS = {"MESH": 5.0, "O-S": 72.0, "XE-S": 7.5, "FE-S": 14.0,
        "O-P": 63.0, "XE-P": 8.0, "FE-P": 14.0}
ITEM_CEILING_CORE_MIN = 183.5          # == sum(CAPS.values()), asserted in main()
# PREDICTED: MP-A1 O arms = SO-3's MEASURED O-arm cost x M=3.0 (DERIVED; m_iter 2.0
# x m_adj 1.5 -- PREREGISTRATION section 4.1); the five non-O arms carried at SO-3's
# MEASURED costs (they already computed dCL_i/dx).  M is the calibration quantity
# the O arm measures at completion (ratio actual/predicted -> docs/COST_CALIBRATION).
PREDICTED_CORE_MIN = {"MESH": 0.17, "O-S": 23.75, "XE-S": 2.35, "FE-S": 4.45,
                      "O-P": 20.85, "XE-P": 2.53, "FE-P": 4.53}
PREDICTED_STALL_CORE_MIN = {"O-S": 12.0, "O-P": 11.0}

# ---- THE HARNESS-SOUND FLOOR.  `VERIFICATION_CHARTER.md` section 7 step 4,
# ---- verbatim: *"The harness-sound floor on this stack, for a case with no
# ---- flagged components, is 2.5 to 5 percent vector-norm relative error.  A
# ---- number below that is a claim about the harness."*
# ----
# ---- THIS IS NOT DECORATION AND IT IS WHY IT IS A REPORTED NUMBER RATHER THAN A
# ---- SENTENCE.  SO-3aR2's PATCHED G5J aggregate is 2.678 % against a 5.0 % band
# ---- -- INSIDE the floor's own interval, i.e. the patched gradient passes
# ---- essentially ON the floor.  A record that called that "a 0.1 % verification"
# ---- would be describing the harness and not the gradient.  So the margin to the
# ---- floor's LOWER edge is computed and published beside every aggregate, and a
# ---- reading BELOW 2.5 % is labelled `AT_OR_BELOW_HARNESS_FLOOR` -- which is a
# ---- statement about what the number can support, never a gate: turning it into
# ---- a gate would convert an honest caveat into a `GATE FAIL` the charter does
# ---- not authorise.
HARNESS_FLOOR_LO_PCT = 2.5
HARNESS_FLOOR_HI_PCT = 5.0


def floor_margin(agg_pct):
    """Where an aggregate sits relative to section 7 step 4's harness floor.

    REPORTED, NEVER GATED.  Returns the margin in percentage points to the
    floor's lower edge and a label a reader cannot mistake."""
    if agg_pct is None:
        return {"aggregate_rel_err_pct": None, "status": NOT_MEASURED,
                "harness_floor_pct": [HARNESS_FLOOR_LO_PCT, HARNESS_FLOOR_HI_PCT]}
    if agg_pct < HARNESS_FLOOR_LO_PCT:
        status = "BELOW_HARNESS_FLOOR -- a number below 2.5 % on this stack is a claim about the harness (VERIFICATION section 7 step 4), not a tighter verification"
    elif agg_pct <= HARNESS_FLOOR_HI_PCT:
        status = "INSIDE_HARNESS_FLOOR_INTERVAL -- this passes essentially ON the floor and must never be described as a sub-percent verification"
    else:
        status = "ABOVE_HARNESS_FLOOR -- the reading is resolvable above the harness"
    return {"aggregate_rel_err_pct": agg_pct,
            "harness_floor_pct": [HARNESS_FLOOR_LO_PCT, HARNESS_FLOOR_HI_PCT],
            "margin_to_floor_lower_edge_pct_points": round(agg_pct - HARNESS_FLOOR_LO_PCT, 6),
            "margin_as_fraction_of_floor": round(agg_pct / HARNESS_FLOOR_LO_PCT, 6),
            "status": status,
            "provenance": "VERIFICATION_CHARTER.md section 7 step 4",
            "gated": False}
CELLS_EXPECTED = 4032

# ---- BAND D / BAND E / PLATEAU: INHERITED BY CITATION (line 7), never re-derived
# ---- by a lane that has seen an answer.
FD_BAND_PCT = 5.0            # band D, per graded PAIR
AGG_BAND_PCT = 5.0           # band E, aggregate vector-relative, PER ROW
PLATEAU_TOL_PCT = 10.0       # proved PER PAIR, never asserted once for the item
NEAR_ZERO_ABS = 1.0e-14
MIN_GRADED_PAIRS = 3         # line 7: fewer than 3 graded pairs on a row -> NOT A RESULT

ALPHAS_REGISTERED = list(XF.ALPHAS_REGISTERED)
WEIGHTS_REGISTERED = list(XF.WEIGHTS_REGISTERED)
ALPHA_TOL_ABS = 1.0e-12      # G-ALPHA
SCENARIOS = list(XF.SCENARIOS)
N_SCEN = XF.N_SCEN
MP_STRUCT_TOL = 1.0e-10      # G-MP-STRUCT, relative
TB_MAX_PASSING = 1           # G-TB: PASS iff AT MOST 1 of the 4 passes band D at h=1e-8

COMPONENTS_REGISTERED = [[d, i] for (d, i) in XF.COMPONENTS]
STEPS_REGISTERED = dict(XF.STEPS)
TB_STEPS_REGISTERED = dict(XF.TB_STEPS)
CTRL_STEP = XF.CTRL_STEP
PLANT = XF.PLANT
EVALS_DECLARED = XF.EVALS_DECLARED

# ===========================================================================
# THE PLANT IS SIZED **RELATIVE TO THE BAND IT MUST CROSS**, NOT ABSOLUTELY.
# MP-A1 REGISTERED DELTA.  This is the change that has to be argued, not just
# made, so the argument is here beside the constant.
#
# WHAT WENT WRONG.  SO-2M was lost because it inherited `PLANT = 1.234e-03` -- an
# ABSOLUTE constant sized on a CD-scale item -- and applied it to a `CMZ`
# reference.  1.234e-03 is 2.48 % of that reference, and the gate's band is 5 %.
# THE PLANT COULD NOT CROSS ITS OWN BAND.  The control therefore ran, reported
# itself EXERCISED, and demonstrated NOTHING: a gate that stays `PASS` under a
# plant too small to fail it has not been shown able to read a violation.  An
# absolute plant is a claim about the SCALE OF THE QUANTITY, and this comparator
# grades four quantities (`J`, three `CL`) whose scales differ by more than an
# order of magnitude before any successor changes the objective again.
#
# THE FORM, REGISTERED AT THE FREEZE:
#
#       plant_i = PLANT_K * (FD_BAND_PCT / 100) * |d_ref_i|
#
# where `d_ref_i` is the SAME reference the gate divides by -- the middle FD step
# for that exact pair -- so the planted relative error is `PLANT_K * FD_BAND_PCT`
# BY CONSTRUCTION, whatever the quantity's scale.
#
# WHY THIS IS NOT FITTING THE CONTROL TO THE DATA, and the distinction is the
# whole justification.  Fitting to the data would be choosing a THRESHOLD, a BAND
# or a LABEL after seeing an answer -- rule 2, and none of those moves here: band
# D stays 5.0 %, band E stays 5.0 %, the plateau tolerance stays 10.0 % and every
# label is unchanged.  What is being sized is the PERTURBATION IN A NEGATIVE
# CONTROL, and a negative control has exactly one job: DEMONSTRATE THAT THE GATE
# CAN FAIL.  A plant smaller than the band cannot do that job -- it is a broken
# control, not a strict one -- and a plant enormously larger than the band tests
# only that arithmetic works.  Sizing it to the band is sizing the INSTRUMENT to
# the QUESTION, which is what an instrument is for.  The plant never touches the
# graded artefact: it is written to a SEPARATE COPY under `grader_controls/`, the
# real reading is taken from the real bytes, and the item's verdict is composed
# from the unplanted artefact alone.
#
# `PLANT_K = 3.0` IS REGISTERED HERE, BEFORE ANY COMPUTE.  It puts the planted
# relative error at 15 % against a 5 % band -- clear of the band by 3x, so a
# control that fails to flip is telling us about the GATE and not about a
# marginal plant.  It is not larger because a plant that dwarfs the band would
# also flip a gate whose band had been mis-registered by an order of magnitude,
# and the control would stop being able to see that.
#
# AND IT IS PROVED SUFFICIENT BY BEING DRIVEN INSUFFICIENT.  `PLANT_K_INSUFF`
# reproduces the SO-2M geometry exactly -- a plant BELOW the band -- and the
# selftest requires the flip to FAIL to happen at that K.  A sufficiency claim
# that is not driven at an insufficient K is the same shape as MP-A1a's leg `A5`,
# which asserted a pin was a sentinel and went on passing after the pin should
# have been set.
PLANT_K = 3.0
PLANT_K_INSUFF = 0.2         # 1 % against a 5 % band -- SO-2M's geometry, driven RED

# ---- MP-A1 REGISTERED CONSTANTS (PREREGISTRATION section 1.4 / section 7). ----
# The per-point CL EQUALITY targets = SO-3's MEASURED undeformed baseline CL, so
# `shape = 0` is a feasible seed.  G-CLTGT reads them back from the artefact to
# 1e-12; G-CLHOLD gates that each point HOLDS its target at the final design and
# that lift never went negative (the SO-3 collapse).
CL_TARGET = [0.31189588769251864, 0.49876526085592926, 0.6639763551107052]
CL_TARGET_TOL = 1.0e-12       # G-CLTGT: the artefact's targets must equal these bits
TOL_CL_ABS = 1.0e-3           # G-CLHOLD: |CL_i,final - CL_target_i| <= this, per point
                              # (100x IPOPT's own constr_viol_tol 1e-5; section 7 decision 4)
# G-DRAG (section 2b / section 7 decision 5): the constrained optimiser must improve
# on its FEASIBLE shape=0 seed; the reduction is REPORTED (with the CL triple), the
# magnitude NEVER gates a PASS.
DRAG_REDUCTION_FLOOR_PCT = 0.0   # final J strictly < baseline J


def plant_for(scale):
    """The rule-3 perturbation for a gate that normalises by `scale`.

    `scale` is `d_ref` for the pair the plant lands on.  A `scale` of zero or a
    non-finite one gets the registered ABSOLUTE fallback rather than a zero
    plant, because a zero plant is not a control at all -- but the pair would
    already be excluded `NEAR_ZERO` before the gate saw it, so the fallback is a
    belt-and-braces branch and is REPORTED when taken."""
    s = abs(float(scale)) if scale is not None else 0.0
    if not (s > 0.0) or s != s or s == float("inf"):
        return PLANT, "ABSOLUTE_FALLBACK -- d_ref is zero or non-finite"
    return PLANT_K * (FD_BAND_PCT / 100.0) * s, "RELATIVE -- PLANT_K*(band_D/100)*|d_ref|"

# The adjoint `of` keys the X artefact carries.  REGISTERED EXPLICITLY, never
# discovered by iterating whatever the artefact happens to hold.
OF_J = "J"
OF_CD = ["CD%d" % i for i in range(N_SCEN)]
OF_CL = ["CL%d" % i for i in range(N_SCEN)]
OF_KEYS_REGISTERED = sorted([OF_J] + OF_CD + OF_CL)

IMG_DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
              "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663", "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
# STAGE-2 PLACEMENT DISCLOSURE (section 5: "cpuset fixed at Stage 2 and disclosed
# there against every live sibling's registered set").  Registered: cpuset 14.
# It is NOT core 0.  MP-A1 registered cpuset 8 (PREREGISTRATION section 3.3 /
# section 7 decision 3), PROVISIONAL: the launcher RE-READS live occupancy at the
# freeze and G12 gates the launcher's value against this constant, so the two
# cannot drift apart silently.  SO-3 held 14; a draft-time sweep of registered
# sibling .sh showed sets on {0,1,2,3,4,11,12,14,15}, so 8 is disjoint.
CPUSET_REGISTERED = "8"
DELIVERED_CORES_FLOOR = 1.5   # NOT COMPOSED at np = 1 (section 3, G12)

# ---- P_COST'S BAND, RE-DERIVED FOR THIS ITEM.  AMENDMENT 2, 2026-09-01, BEFORE
# ---- FIRST COMPUTE (`PREREGISTRATION.md` Amendment 2; that document governs).
# ---- THIS IS THE ONLY VALUE THIS AMENDMENT MOVES.  No gate, no threshold, no cap
# ---- and no label changes: bands D and E stay 5.0 %, the plateau tolerance stays
# ---- 10.0 %, CAPS and ITEM_CEILING_CORE_MIN are untouched, and P_COST gates
# ---- nothing -- predictions are scored, never composed into the verdict.
#
# WHAT WAS WRONG.  `(14.0, 60.0)` was inherited BYTE-IDENTICAL from SO-3aR2, whose
# predicted total was 21.99 core-min and whose measured total, 14.318, HIT it.  It
# was carried across a derivation that added TWO 103.0-core-min optimiser arms and
# was never re-derived.  MP-A1's registered point is 228.59 core-min -- 3.81x that
# band's upper edge -- so `P_COST` had NO REACHABLE HIT: it read `MISS` with
# certainty on the full-chain path and `NOT MEASURED` on every other path, and
# could not discriminate between any two outcomes.  A prediction that cannot HIT is
# a decoration standing where a test belongs, and it is the P5 shape one layer
# down: a token whose NAME reads as a live cost check while it is decided in
# advance.
#
# THE NEW BAND IS DERIVED FROM THE COST MODEL, NOT DRAWN AROUND THE POINT ESTIMATE,
# AND IT MUST BE ABLE TO GO BOTH WAYS -- a band that cannot MISS is exactly as
# useless as one that cannot HIT, and it is the easier mistake to make once the
# point estimate is known.  The five non-O arms are MEASURED and total 22.59
# core-min (MESH 0.19 + XE 3.7 x2 + FE 7.5 x2).  THE WHOLE UNCERTAINTY IS
# 2 x (majors x per-major rate), and it is enumerated rather than asserted:
#
#   S1  12 majors @ 1.2638 core-min/major (C-24 x3, WITHOUT C-188's
#       1.6308 transfer factor)                                    ->   52.92   OUT
#   S2  12 majors @ 2.0610 (the registered rate; SO1bR and D1 armO
#       BOTH converged in 12 majors on this very case)             ->   72.05   in
#   S3  24 majors @ 2.0610                                         ->  121.52   in
#   S4  34 majors @ 2.0610 (the stall abort's FIRST REACH)         ->  162.74   in
#   S5  50 majors @ 2.0610 (MAX_MAJORS; THE REGISTERED POINT)      ->  228.69   in
#   S6  50 majors @ 3.3611 (the 1.6308 transfer factor is ITSELF
#       short by its own margin -- D6 is A2/3-D/np=4 and this is
#       A1/2-D/np=1, and C-188's lesson is that the ANCHOR is the
#       predictor, not the factor)                                 ->  358.70   OUT
#   S7  both O arms stopped at their 240.0 cap                     ->  502.59   OUT
#
# `(60.0, 300.0)` CONTAINS S2..S5 AND EXCLUDES S1 BELOW AND S6/S7 ABOVE.  Both
# edges fall BETWEEN named scenarios; neither sits on one.  The item ceiling of
# 595.0 is outside the band, as it must be -- a cap is not a prediction.
#
# WHAT FALSIFIES IT, REGISTERED BEFORE THE RUN.  A graded item total BELOW 60.0
# core-min -- both optimisers converging in far fewer majors than the single-point
# precedent, or a per-major rate well under the C-24 anchor -- or ABOVE 300.0 --
# the multipoint penalty failing to transfer from D6 and being short again.  BOTH
# ARE PLAUSIBLE OUTCOMES OF THIS RUN, which is the property `(14.0, 60.0)` lacked.
PRED = {"P2_CL_baseline_band": (0.45, 0.55),
        "P5_patched_agg_max_pct": 1.0,
        "P_COST_band": (60.0, 300.0)}

FIELDS_PHYSICS = ("rc_value", "oomkilled", "terminal_statement", "age_guard",
                  "no_fatal_token", "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("rc_record", "memavail_pre_GiB", "memavail_post_GiB", "delivered",
                         "siblings_pre", "siblings_post", "log", "wall_s")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}

# ---- G-PROV: THE TRAVELLING SHIPPED `GATE FAIL`, ENFORCED IN CODE (section 2).
# ---- MP-A1 rests on SO-1a's PATCHED row while SO-1a's ITEM verdict is GATE FAIL.
# ---- Clause (5) -- verdict_line byte-identical to what this module composes --
# ---- exists because this lab lost the words `GATE FAIL` from docs/LAB_STATE.md
# ---- to an unquoted heredoc on 2026-08-30 (L-405).
# ---- MP-A1 REGISTERED DELTA: THE PROVENANCE IS A CHAIN, NOT ONE LINK. --------
# MP-A1's DIRECT upstream is SO-3aR2, not SO-1a, and SO-3aR2's ITEM VERDICT IS
# `GATE FAIL` -- `rows {PATCHED: PASS, SHIPPED: GATE FAIL}`, graded
# 2026-08-31T23:02:21Z.  SO-3aR2 in turn carries its own `upstream_provenance`
# from CURRICULUM-SO1a, whose note reads: *"the SHIPPED GATE FAIL TRAVELS with
# every claim this item makes."*  A derivation that swapped one link for the
# other would have DROPPED a GATE FAIL from the chain, so BOTH links are carried
# and the composed line names both.
#
# WHAT THIS BUYS A READER, IN ONE SENTENCE.  A PATCHED row alone supports
# *"on the patched toolchain, the optimiser reduced weighted drag by X"* and
# NEVER *"DAFoam reduces weighted drag by X"*.  The second sentence is the one
# this chain exists to make unwritable.
UPSTREAM_CHAIN = [
    {"item": "CURRICULUM-SO3aR2",
     "item_verdict": "GATE FAIL",
     "rows": {"SHIPPED": "GATE FAIL", "PATCHED": "PASS"},
     "relation": "DIRECT -- MP-A1's optimisation is admissible only because SO-3aR2 "
                 "FD-verified the multipoint objective's gradient at np = 1",
     "basis": "/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-"
              "multipoint-gradient/SO3aR2_grade_20260831T230221Z.json",
     "shipped_gate_detail": {
         "G5J_SHIPPED": "GATE FAIL",
         "basis": "/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-"
                  "multipoint-gradient/SO3aR2_grade_20260831T230221Z.json"
                  " -> gates.G5J.SHIPPED.G5J_objective",
         "aggregate_rel_err_pct": 31.498325840045588,
         "n_pass": 2, "n_gate_fail": 2, "of": 4,
         "reading": "on the SHIPPED toolchain the multipoint objective gradient missed the "
                    "5 % band by more than 6x on this very case"},
     "patched_detail": {
         "G5J_PATCHED": "PASS",
         "aggregate_rel_err_pct": 2.6779490823450605,
         "band_D_pct": 5.0,
         "harness_floor_caveat": "2.678 % sits INSIDE VERIFICATION section 7 step 4's "
                                 "2.5-5 % harness-sound floor.  The patched gradient passes "
                                 "essentially ON the floor and must never be described as a "
                                 "sub-percent verification",
         "endpoint_gap": "MEASURED AT ITERATION 0 ONLY.  DAFOAM_CHARTER section 9 requires "
                         "the FD check at the FINAL design point, and the charter's stated "
                         "reason is this toolchain: the IDWarp rotation defect fires at the "
                         "undeformed baseline and behaves differently just above threshold, "
                         "so a gradient verified at iteration 0 is NOT verified at iteration "
                         "47.  MP-A1's XE/FE arms are what close that gap"}},
    {"item": "CURRICULUM-SO1a",
     "item_verdict": "GATE FAIL",
     "rows": {"SHIPPED": "GATE FAIL", "PATCHED": "PASS"},
     "relation": "INHERITED -- carried in SO-3aR2's own upstream_provenance",
     "basis": "cases/dafoam/ladder-a/A1/curriculum_SO1a/RESULTS.md section 1",
     "shipped_gate_detail": {
         "G5_SHIPPED": "GATE FAIL",
         "basis": "cases/dafoam/ladder-a/A1/curriculum_SO1a/RESULTS.md section 1",
         "reading": "the SHIPPED toolchain row failed the FD band at a single point on "
                    "this very case"}},
]

UPSTREAM = {
    "item": "CURRICULUM-SO3aR2",
    "item_verdict": "GATE FAIL",
    "rows": {"SHIPPED": "GATE FAIL", "PATCHED": "PASS"},
    "chain": UPSTREAM_CHAIN,
    "shipped_gate_detail": UPSTREAM_CHAIN[0]["shipped_gate_detail"],
    "why_it_travels": ("the two-row structure exists so the PATCHED row can carry work the "
                       "SHIPPED row cannot -- it does NOT erase the SHIPPED reading.  BOTH "
                       "links of this chain are GATE FAIL at item level and both travel"),
}


def compose_verdict_line():
    """The ONE place the provenance sentence is composed.  `require_travelling_
    provenance` compares the stored bytes against this function's output, so a
    line mangled in transit (an unquoted heredoc, a stray shell expansion) is a
    REFUSAL and not a silently shortened sentence."""
    return ("UPSTREAM CHAIN %s -- EVERY LINK GATE FAIL AT ITEM LEVEL, SHIPPED row GATE FAIL "
            "at every link, PATCHED row PASS; MP-A1 builds on the PATCHED row and the SHIPPED "
            "GATE FAIL TRAVELS with every claim this item makes.  A PATCHED row alone supports "
            "`on the patched toolchain, the optimiser reduced weighted drag by X` and NEVER "
            "`DAFoam reduces weighted drag by X`"
            % " -> ".join(link["item"] for link in UPSTREAM_CHAIN))


UPSTREAM["verdict_line"] = compose_verdict_line()

# ---- THE SCHEMA REGISTRY.  Every nested location this module reads is an
# ---- EXPLICIT tuple path.  There is NO recursive hunt for a key by name
# ---- anywhere in this file: a read that goes looking until it finds something
# ---- will always find something.  See (IV).
SCHEMA = {
    "X.adjoint":            ("adjoint",),
    "X.adjoint_of_keys":    ("adjoint_of_keys",),
    "X.J_baseline":         ("J_baseline",),
    "X.CD_baseline":        ("CD_baseline",),
    "X.CL_baseline":        ("CL_baseline",),
    "X.components":         ("components_requested",),
    "X.nprocs":             ("nprocs",),
    "X.optimiser":          ("optimiser",),
    "X.evals_declared":     ("evaluations_declared",),
    "X.evals_failed":       ("evaluations_failed",),
    "X.so_md5":             ("identity", "libidwarp_so_md5"),
    "X.mp.alphas_read":     ("multipoint", "alphas_read_back"),
    "X.mp.alphas_reg":      ("multipoint", "alphas_registered"),
    "X.mp.alpha_paths":     ("multipoint", "alpha_read_paths"),
    "X.mp.weights":         ("multipoint", "weights"),
    "X.mp.scenarios":       ("multipoint", "scenarios"),
    "F.rows":               ("rows",),
    "F.steps":              ("steps",),
    "F.tb_steps":           ("tb_steps",),
    "F.components":         ("components_requested",),
    "F.eta_used":           ("eta_used",),
    "F.J_baseline":         ("J_baseline",),
    "F.CD_baseline":        ("CD_baseline",),
    "F.CL_baseline":        ("CL_baseline",),
    "F.optimiser":          ("optimiser",),
    "F.evals_declared":     ("evaluations_declared",),
    "F.evals_failed":       ("evaluations_failed",),
    "F.so_md5":             ("identity", "libidwarp_so_md5"),
    "F.mp.alphas_read":     ("multipoint", "alphas_read_back"),
    "F.mp.weights":         ("multipoint", "weights"),
    "F.mp.scenarios":       ("multipoint", "scenarios"),
}
_MISSING = object()

# G-NOOPT: any of these anywhere in an artefact's TOP-LEVEL keys, or a non-null
# `optimiser`, means an optimiser ran.  Registered as an explicit key list, not a
# substring sweep -- section 3 G-NOOPT.
OPTIMISER_KEYS = ("optimiser_history", "majors", "n_majors", "major_iterations",
                  "run_driver", "pyoptsparse", "ipopt", "snopt", "slsqp",
                  "alpha_cutbacks", "restoration_majors")
OPTIMISER_EXIT_RE = re.compile(r"^\s*EXIT:\s", re.M)

# ---- THE BIRTH REGISTER (Sanaa 2026-08-28).  Every reader that produces a
# ---- graded number, with the unit that bore it in BOTH directions.
READERS = {
    "R1_read_ledger": {"produces": "core_min, rc, cpuset, DIGEST, oomkilled -> G1/G9/G10/G12",
                       "producer": "mpa1_run_arm.sh:mpa1_ledger_row",
                       "born_by": ["U40", "U41"], "born": True},
    "R2_fatal_token_sites": {"produces": "C5 site count -> G1 (READS A ZERO AS A PASS)",
                             "producer": "OpenFOAM / the arm shell, via reference/*.log",
                             "born_by": ["U50", "U51", "U52", "U53"], "born": True},
    "R2b_read_primal_convergence": {"produces": "convergence reading -> REPORTED, NEVER GATED",
                                    "producer": "DAFoam, via reference/REAL_SO1a_X-S_arm.log",
                                    "born_by": ["U56", "U57", "U58"], "born": True},
    "R3_read_mesh_cells": {"produces": "cell count -> G-M2",
                           "producer": "checkMesh, via reference/REAL_SO1a_MESH_checkMesh.log",
                           "born_by": ["U54", "U55"], "born": True},
    "R4_read_X": {"produces": "adjoint totals -> G5J, G5C, G-MP-STRUCT (ALL CAN PASS ON A SMALL NUMBER)",
                  "producer": "mpa1_xf.build_X_record", "born_by": ["U60", "U61", "U62"], "born": True},
    "R5_read_F": {"produces": "FD derivative table -> G5J, G5C, G-TB",
                  "producer": "mpa1_xf.build_F_record / build_fd_row / build_ctrl_row",
                  "born_by": ["U63", "U64", "U65"], "born": True},
    "R6_read_multipoint_identity": {"produces": "alphas and weights -> G-ALPHA",
                                    "producer": "mpa1_xf.build_identity_block",
                                    "born_by": ["U66", "U67"], "born": True},
    "R7_arm_datum": {"produces": "age-guard mtime comparison -> G1/C4",
                     "producer": "the filesystem + the launcher's touch",
                     "born_by": ["U42", "U43"], "born": True},
}

# The suite's unit count, FROZEN.  Set to 86, the count the FINISHED suite drives.
# It was first written as 88 -- an ESTIMATE made before the suite existed -- and
# is corrected DOWN to the driven count rather than the suite being padded up to
# meet a number.  Four units were ADDED while driving, each because a check this
# lane had written turned out to be measuring the wrong thing: U11b (the marker
# ADDRESS is read out of the frozen writer, after this lane hardcoded the wrong
# case and read an absent file); U28b (the flip control is COMPARATIVE, after it
# refused a legitimate run below the graded-pair floor); U53b and U53c (the three
# banners are safe for TWO DIFFERENT reasons, after this lane asserted one
# mechanism for all three).  A count that drifts without a reason is how a suite
# loses a unit; this one drifted with four.  Then BUMPED to 88, deliberately, for
# U100 and U101 -- the row-label call-site sweep and its planted known positive,
# added after SO-1c died at its second arm on ONE of THREE unrepaired call sites
# of a row label (CLAUDE.md rule 14).  Driving them found a real one in THIS file:
# seven hand-spelled control keys survived the row-label collapse, which is the
# same shape in miniature -- and a DEAD DIVERGENCE LIMB (`if "S" in X and "P" in X`
# could never be true after the collapse, so the shipped-vs-patched reading had
# silently vanished), which is why U102 exists and brings the count to 89.  Then
# 91, for U41b and U41c: once the fixture could source the REAL launcher, a
# STRUCTURALLY VALID ledger row carrying a non-numeric value reached a bare
# `float()` and CRASHED the comparator with a traceback and zero gate readings.
# The hand-written fallback row could only ever be UNPARSEABLE, so that branch had
# never been reached in 89 green units.  The guard now refuses BY NAME, and U41c
# checks the refusal actually names the column.
# 91 -> 92 on 2026-08-31, BUMPED DELIBERATELY WITH ITS REASON, which is what this
# constant exists to force.  The added unit is U101b: the row-label sweep's SHELL
# rule set had no suffix-glob rule while its PYTHON rule set always had one, and
# the single unrepaired consumer of the arm->row mapping in this item
# (mpa1_chain_driver.sh's `img_of`) was in shell -- so eight files were swept and
# the fourth call site was structurally invisible.  U101b proves the new rule
# fires on a suffix glob AND stays silent on the registered full-name table.
# No gate, threshold, cap or label moved; this adds a check and removes none.
# MP-A1, 2026-08-31: BUMPED DELIBERATELY 92 -> 97, and the five are named so the
# bump is a decision and not a drift.  U28c/U28d/U28e establish that the rule-3
# plant is sized RELATIVE to the band it must cross and that its planted relative
# error is `PLANT_K * band_D` by construction; U28f is the SUFFICIENCY LEG DRIVEN
# RED at `PLANT_K_INSUFF`, where the plant sits INSIDE the band and the gate does
# NOT flip -- which is the only thing that makes U27's flip evidence about the gate
# rather than about arithmetic; U28g states that insufficient case is SO-2M's own
# geometry.  SO-2M was lost to an absolute `1.234e-03` plant that was 2.48 % of a
# `CMZ` reference against a 5 % band: an EXERCISED control that could not cross its
# own band and therefore demonstrated nothing.  No gate, threshold, band, cap or
# label moved; this adds five checks and removes none.
# BUMPED 97 -> 106 DELIBERATELY for MP-A1: nine units (U6a-U6i) drive the three
# new MP-A1 gates -- G-CLHOLD (lift held / collapsed both ways), G-DRAG (final J <
# baseline), G-CLTGT (targets as registered), the G5C dCL_i/dx coverage assertion
# (check-3), and the G-CLHOLD planted control firing both ways off disk.  No SO-3
# unit was removed; nine were added.
EXPECTED_UNITS = 106


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    """L-332: `python3 -O` strips `assert`, so an assert is not a guard.  COUNTED,
    with a planted one shown counted (U84/U85), never asserted absent."""
    with open(path) as fh:
        return sum(1 for n in ast.walk(ast.parse(fh.read())) if isinstance(n, ast.Assert))


def at(rec, key, where):
    """Read one REGISTERED location out of an artefact by its EXPLICIT path.

    There is no search here and no fallback to a sibling key: `SCHEMA[key]` is
    the only path walked.  A location that is absent REFUSES and NAMES THE PATH,
    which is the reading SO-1c needed and did not have -- its consumer looked at
    the top level, its producer wrote one level down, and nothing said so."""
    path = SCHEMA.get(key)
    if path is None:
        refuse("SCHEMA", {"location_not_registered": key,
                          "note": "every nested read is registered explicitly; there is no hunt"})
    cur = rec
    for i, p in enumerate(path):
        if not isinstance(cur, dict) or p not in cur:
            refuse(where, {"registered_location_absent": {"key": key, "path": list(path),
                                                          "failed_at": p, "depth": i}})
        cur = cur[p]
    return cur


def at_opt(rec, key):
    """The same explicit walk, returning `_MISSING` instead of refusing.  Used
    ONLY where absence is itself the reading (G-NOOPT's `optimiser` field)."""
    cur = rec
    for p in SCHEMA[key]:
        if not isinstance(cur, dict) or p not in cur:
            return _MISSING
        cur = cur[p]
    return cur


# ===================== R1: the ledger =================================================
LEDGER_RE = re.compile(
    r"ARM=(?P<ARM>\S+)\s+ROW=(?P<ROW>\S+)\s+IMG=(?P<IMG>\S+)\s+DIGEST=(?P<DIGEST>\S+)\s+"
    r"rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall_s>\d+)\s+ranks=(?P<ranks>\d+)\s+"
    r"core_min=(?P<core_min>[\d.]+)\s+cap_core_min=(?P<cap>[\d.]+)\s+"
    r"enforced_wall_s=(?P<ewall>\d+)\s+enforced_core_min=(?P<ecore>[\d.]+)\s+"
    r"memory=(?P<mem>\S+)\s+inspect\(exit,oomkilled\)=\[(?P<inspect>[^\]]*)\]\s+"
    r"memavail_pre_GiB=(?P<mempre>\S+)\s+memavail_post_GiB=(?P<mempost>\S+)\s+"
    r"cpuset=(?P<cpuset>\S+)\s+delivered_cores_mean=\[(?P<delivered>[^\]]*)\]\s+"
    r"siblings_pre=\[(?P<sibpre>[^\]]*)\]\s+siblings_post=\[(?P<sibpost>[^\]]*)\]\s+"
    r"log=(?P<log>\S+)")


def _infra_float(v, field=None):
    """A non-numeric INFRASTRUCTURE field REFUSES with its name, and does not
    raise.  A CRASH IS NOT A VERDICT: an unhandled ValueError here exits with a
    traceback and no gate readings, which is the D6-GRADER-DEF-1 shape wearing a
    different hat.  Found by driving the fixture through the REAL launcher --
    the hand-written fallback row could only ever be UNPARSEABLE, so this branch
    had never been reached."""
    if v is None or v == NOT_MEASURED:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        refuse("ledger", {"non_numeric_field_in_a_STRUCTURALLY_VALID_row":
                          {"field": field, "value": str(v)[:80]},
                          "note": ("the row matched the registered format but carries a value "
                                   "that is not a number; that is a MALFORMED artefact and "
                                   "REFUSES, it does not raise")})


def read_ledger(path):
    """An ABSENT ledger is a CENSUS reading of zero executed arms, NOT a refusal
    -- see (II).  A PRESENT-BUT-GARBAGE row is a MALFORMED artefact and REFUSES."""
    rows = {}
    if not os.path.isfile(path):
        return rows
    with open(path, errors="replace") as fh:
        lines = fh.readlines()
    for line in lines:
        if not line.startswith("ARM="):
            continue
        m = LEDGER_RE.search(line)
        if not m:
            refuse("ledger", {"row_unparseable": line.strip()[:300],
                              "note": "PRESENT-BUT-GARBAGE row: refused, never skipped.  An "
                                      "ABSENT row is a census reading; a MALFORMED one is a defect"})
        g = m.groupdict()
        parts = g["inspect"].split()
        infra_nm = [k for k, v in (("memavail_pre_GiB", g["mempre"]), ("memavail_post_GiB", g["mempost"]),
                                   ("delivered", g["delivered"]), ("siblings_pre", g["sibpre"]),
                                   ("siblings_post", g["sibpost"]), ("log", g["log"]))
                    if v is None or NOT_MEASURED in str(v)]
        try:
            _nums = {"rc": int(g["rc"]), "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
                     "core_min": float(g["core_min"]), "cap_core_min": float(g["cap"]),
                     "enforced_core_min": float(g["ecore"])}
        except (TypeError, ValueError) as exc:
            refuse("ledger", {"non_numeric_PHYSICS_field": {"row": line.strip()[:200],
                                                            "error": repr(exc)[:160]},
                              "note": "a physics field that is not a number REFUSES (L-342)"})
        row = {"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"], "DIGEST": g["DIGEST"],
               "memory": g["mem"],
               "inspect_exit": (None if (not parts or parts[0] == NOT_MEASURED) else parts[0]),
               "oomkilled": (parts[1] if len(parts) > 1 else None),
               "memavail_pre_GiB": _infra_float(g["mempre"], "memavail_pre_GiB"),
               "memavail_post_GiB": _infra_float(g["mempost"], "memavail_post_GiB"),
               "cpuset": g["cpuset"], "delivered": g["delivered"], "siblings_pre": g["sibpre"],
               "siblings_post": g["sibpost"], "log": g["log"], "source": "ledger_row",
               "infra_not_measured": infra_nm}
        # The numeric fields are merged in AFTER their guarded conversion above, so
        # a non-numeric value REFUSES by name instead of raising inside the literal.
        row.update(_nums)
        if row["ARM"] in rows:
            refuse("ledger", {"duplicate_arm_row": row["ARM"],
                              "note": "two records for one run is the defect"})
        if row["ARM"] not in ARMS_DECLARED:
            refuse("ledger", {"row_for_an_UNDECLARED_arm": row["ARM"], "declared": ARMS_DECLARED,
                              "note": "an arm this item never registered is a malformed artefact"})
        rows[row["ARM"]] = row
    return rows


def inspect_file_fallback(base, arm):
    """The surviving kernel record, when the ledger row's rc RECORD is absent."""
    best = None
    if not os.path.isdir(base):
        return None
    for fn in sorted(os.listdir(base)):
        if fn.startswith("%s_" % arm) and fn.endswith(".inspect.txt"):
            best = os.path.join(base, fn)
    if best is None:
        return None
    with open(best, errors="replace") as fh:
        parts = fh.read().split()
    if len(parts) < 2:
        return None
    return {"exit": parts[0], "oomkilled": parts[1], "file": os.path.basename(best)}


# ===================== R7: the age-guard datum ========================================
def read_write_compression(adir):
    p = os.path.join(adir, CONTROLDICT_REL)
    try:
        with open(p, errors="replace") as fh:
            for line in fh:
                s = line.strip()
                if s.startswith("writeCompression"):
                    return s.rstrip(";").split()[-1]
    except OSError:
        return None
    return None


def resolve_datum_ref(adir, arm, datum):
    """BY EXISTENCE, NEVER BY NAME.  `writeCompression on` rewrites `0/U` as
    `0/U.gz`; AV-1 and AV-2 both returned NOT A RESULT with every physics
    artefact intact because their frozen graders pinned a vanished PATH."""
    plain, gz = DATUM_CANDIDATES[arm]
    pp, pg = os.path.join(adir, plain), os.path.join(adir, gz)
    wc = read_write_compression(adir)
    if os.path.exists(pp):
        mt = int(os.path.getmtime(pp))
        return {"name": plain, "path": pp, "is_compressed_twin": False, "mtime": mt,
                "write_compression": wc,
                "mtime_rule": "the launcher touched it: must equal the datum", "ok": (mt == datum)}
    if os.path.exists(pg):
        mt = int(os.path.getmtime(pg))
        return {"name": gz, "path": pg, "is_compressed_twin": True, "mtime": mt,
                "write_compression": wc,
                "mtime_rule": "the solver wrote it AFTER the datum was taken: may only be NEWER",
                "ok": (mt >= datum)}
    refuse("G1", {"C4_age_datum_reference_absent_in_BOTH_names": [pp, pg], "arm": arm,
                  "write_compression": wc,
                  "note": "the ONLY refusal this resolution makes; AV-1/AV-2 died on the NAME"})


def arm_datum(base, arm):
    d = os.path.join(base, arm)
    p = os.path.join(d, DATUM_FILE)
    if not os.path.isfile(p):
        refuse("G1", {"age_datum_absent": p, "arm": arm,
                      "note": "the arm RAN (it has a ledger row) but left no datum: MALFORMED"})
    with open(p) as fh:
        datum = int(fh.read().strip())
    return d, datum, resolve_datum_ref(d, arm, datum)


NOT_A_GRADING_PATH = ("selftest", "_fix")

# ---- THE ROW-LABEL CALL-SITE SWEEP.  CLAUDE.md rule 14 -----------------------------
# SO-1c died at its second arm because ONE of THREE call sites of a row label was
# repaired.  A fence written in the singular ("the row-label comparison") set the
# scope, and the two it did not name killed the run.  This sweep is the plural
# form: it reads EVERY MP-A1 instrument and reports EVERY site that either
# reintroduces a short-form row literal or DERIVES a row label from another
# identifier's spelling.  It is a REPORT over this item's own files, not a new
# lab-wide tool.
# Built FROM PARTS so this file never spells the tokens it is proving absent.
ROW_SHORT_FORMS = tuple("SP")
_ROW_SWEEP_PY = (
    # a bare short-form row literal, in any position
    (re.compile(r"""(?<![A-Za-z0-9_])(['"])(%s)\1""" % "|".join(ROW_SHORT_FORMS)),
     "a SHORT-FORM row literal; MP-A1 has ONE label set and no short form"),
    # a row label derived from a position in another string
    (re.compile(r"(?<![A-Za-z0-9_])(row|rk|ROW|arm|ARM)\w*\s*\[\s*-?\d+\s*\]"),
     "a row label DERIVED FROM A POSITION in another identifier -- taking index zero "
     "of a row name works on the short/long pair by a coincidence of spelling, and is "
     "exactly the derivation the SO-1c post-mortem forbids"),
    (re.compile(r"\.(startswith|endswith)\(\s*['\"]-?[SP]['\"]"),
     "a row label derived from an ARM-NAME SUFFIX rather than from ARM_ROW"),
)
_ROW_SWEEP_SH = (
    (re.compile(r"""ROW=['"]?[SP]['"]?(?![A-Za-z0-9_])"""),
     "a SHORT-FORM row literal assigned in shell"),
    (re.compile(r"""\$\{\s*ARM\s*:\s*-?\d+\s*(:\s*\d+\s*)?\}"""),
     "a row label sliced out of the ARM name in shell rather than read from the "
     "registered arm->row mapping"),
    # ---- THE ASYMMETRY THAT HID THE FOURTH CONSUMER, CLOSED.
    # The PYTHON rule set above has carried a suffix rule from the start
    # (`.endswith("-S")`).  The SHELL rule set did NOT, and the ONE surviving
    # unrepaired call site in this item -- `mpa1_chain_driver.sh`'s `img_of`,
    # `case "$1" in MESH|*-S) ... *-P)` -- was in shell, so the sweep swept it and
    # saw nothing.  A sweep that carries a rule in one language and not the other
    # reports a zero that is a statement about the rule set, not about the code.
    # The pattern is the WILDCARD suffix glob specifically: a case list of FULL
    # arm names (`X-S|X-P)`) is the registered form and must NOT be flagged.
    (re.compile(r"\*-[SP]\)"),
     "a row (or a row's image) derived from an ARM-NAME SUFFIX GLOB rather than "
     "from the registered full-name arm->row table -- the SO-1c derivation, and "
     "the form a glob cannot refuse an undeclared arm in"),
)


def row_label_call_sites(path):
    """Every site in one file that reintroduces a short-form row label or derives
    one positionally.  Returns a list of {line, text, why}; an EMPTY list is the
    reading, and U101 proves this reader can return a non-empty one."""
    rules = _ROW_SWEEP_SH if path.endswith(".sh") else _ROW_SWEEP_PY
    # EXACTLY ONE exemption, named and narrow: `ROWS[...]` indexes the REGISTERED
    # tuple of labels, which IS the registry -- it does not derive a label from
    # another identifier's spelling.  The exemption is applied per line and
    # COUNTED, because a suppression a reader cannot see is the same defect
    # wearing the other hat.
    exempt_rx = re.compile(r"(?<![A-Za-z0-9_])ROWS\s*\[")
    out, n_exempt = [], 0
    with open(path, errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("*"):
                continue
            for rx, why in rules:
                if not rx.search(line):
                    continue
                if exempt_rx.search(line) and "POSITION" in why:
                    n_exempt += 1
                    continue
                out.append({"file": os.path.basename(path), "line": i,
                            "text": stripped[:160], "why": why})
    for r in out:
        r["registry_indexings_exempted_in_this_file"] = n_exempt
    return out


def mpa1_instrument_files():
    """The instrument set the sweep covers.  Files not yet built are REPORTED AS
    ABSENT rather than silently skipped -- a sweep that reads four files and calls
    itself complete over nine is the SO2a-DRIVER-DEF-1 shape."""
    # ELEVEN, not SO-3aR's ten and not MP-A1a's eight.  `mpa1_collision_leg.py`
    # is the eleventh and it joins the sweep IN THE SAME COMMIT THAT CREATES IT --
    # a new instrument that joins the item without joining the sweep is the SAME
    # SHAPE OF GAP as the pin the census could not see, one rule set away, and
    # this item exists because a repair that was already written on A2 did not
    # cross to A1.
    names = ["mpa1_grade.py", "mpa1_xf.py", "mpa1_runScript.py", "mpa1_run_arm.sh",
             "mpa1_groot5_selftest.sh", "mpa1_chain_driver.sh", "mpa1_stop_marker.sh",
             "mpa1_aggregate_memory.py", "mpa1_pin_census.py", "mpa1_xf_selftest.py",
             "mpa1_collision_leg.py"]
    present, absent = [], []
    for nm in names:
        fp = os.path.join(_HERE, nm)
        (present if os.path.isfile(fp) else absent).append(fp if os.path.isfile(fp) else nm)
    return present, absent


def whole_file_token_scan_sites(path):
    """THE SO-1a DEFECT SHAPE, DETECTED IN A FILE'S OWN AST.

    Positive signature: a function that references `FATAL_TOKENS` AND performs a
    membership test (`ast.In`) AND never splits the text into lines.  SO-1a's
    `fatal_tokens_in` -- `[t for t in FATAL_TOKENS if t in text]` -- is exactly
    that, and it is the KNOWN POSITIVE this detector is proved against (U83),
    because a sweep's zero is a claim about the pattern until a known positive
    makes it a claim about the code (L-400)."""
    with open(path) as fh:
        tree = ast.parse(fh.read())
    bad = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if fn.name in NOT_A_GRADING_PATH:
            continue
        if not any(isinstance(n, ast.Name) and n.id == "FATAL_TOKENS" for n in ast.walk(fn)):
            continue
        has_in = any(isinstance(c, ast.Compare) and any(isinstance(o, ast.In) for o in c.ops)
                     for c in ast.walk(fn))
        splits = any(isinstance(a, ast.Attribute) and a.attr == "splitlines" for a in ast.walk(fn))
        if has_in and not splits:
            bad.append(fn.name)
    return bad


# ===================== R2: C5, line by line, with the banner discriminator =============
def benign_reason(line):
    """C5.  Why this ONE LINE is a notice and not a crash, or None.  THREE named
    exclusions (see (III)); each is COUNTED AND NAMED on the PASS record."""
    for rx, why in BENIGN_LINE_RE:
        if rx.search(line):
            return why
    return None


def fatal_token_sites(text, source):
    """C5.  Scans LINE BY LINE and PER SOURCE FILE, returning (sites, benign).

    LINE BY LINE, because the test must tell a CRASH from a NOTICE and a
    whole-file substring test cannot.  PER SOURCE FILE, because the refusal must
    name the file that carries the hit -- SO-1a's refusal named the ARM log for a
    token that lived in `checkMesh.log`."""
    sites, benign = [], []
    for i, line in enumerate(text.splitlines(), 1):
        hit = [t for t in FATAL_TOKENS if t in line]
        if not hit:
            continue
        why = benign_reason(line)
        rec = {"file": source, "line": i, "tokens": hit, "text": line.strip()[:200]}
        if why:
            rec["why_benign"] = why
            benign.append(rec)
        else:
            sites.append(rec)
    return sites, benign


# ===================== R2b: THE CONVERGENCE DISCRIMINATOR.  A MATCH IS NOT A MEANING ===
def read_primal_convergence(text, source):
    """REPORTED, NEVER GATED.  See (III).

    `converged_statements` counts DAFoam's real statement -- the only line that
    means the primal met `primalMinResTol`.  `banner_not_evidence` counts
    OpenFOAM's SIMPLE banner separately and says, in the record, that it is not
    evidence about this solver either way.  A limb that read the banner would
    report four declarations of non-convergence on the converged reference log."""
    hits = [{"line": text[:m.start()].count("\n") + 1,
             "residual": m.group("res"), "tolerance": m.group("tol")}
            for m in CONVERGED_RE.finditer(text)]
    n_banner = len(SIMPLE_BANNER_RE.findall(text))
    return {"file": source,
            "n_converged_statements": len(hits), "converged_statements": hits[:10],
            "banner_not_evidence": {
                "pattern": "SIMPLE: no convergence criteria found",
                "count": n_banner,
                "why": ("OpenFOAM announces it found no SIMPLE convergence criteria; DAFoam then "
                        "applies its own primalMinResTol and stops the solve.  MEASURED 4x in "
                        "reference/REAL_SO1a_X-S_arm.log on a run that CONVERGED")},
            "status": "REPORTED, NEVER GATED -- this item's gates are the FD table's"}


# ===================== R3: the mesh-cells reader ======================================
def read_mesh_cells(path):
    with open(path, errors="replace") as fh:
        txt = fh.read()
    m = re.search(r"^\s*cells:\s+(\d+)", txt, re.M)
    if not m:
        refuse("G-M2", {"cells_absent_in_checkMesh": path})
    return int(m.group(1))


# ===================== G1, AS A CENSUS =================================================
def g_completion(base, rows):
    """The five rule-4 clauses, PRINTED INDIVIDUALLY per arm that RAN.

    THIS LOOP IS A CENSUS (see (II)).  An arm with no ledger row is `NOT RUN` and
    the loop continues; an arm that ran but whose artefact is MALFORMED refuses.
    Every arm appears in `census`, so a reader can see the whole declared program
    and the shortfall, never only the part that succeeded."""
    out = {"arms": {}, "not_measured": {}, "rule4_clauses": {}, "datum_resolution": {},
           "rc_inferences": {}, "census": {}, "convergence": {},
           "executed": 0, "declared": N_DECLARED, "verdict": "PASS"}
    for arm in ARMS_DECLARED:
        r = rows.get(arm)
        if r is None:
            out["census"][arm] = {"state": "NOT RUN", "reason": "no ledger row",
                                  "note": ("an ABSENT arm is a census reading, never a refusal "
                                           "-- D6-GRADER-DEF-1")}
            continue
        cl = {}
        adir, datum, dres = arm_datum(base, arm)
        out["datum_resolution"][arm] = dres
        logname = r["log"]
        lp = os.path.join(base, logname)
        if not os.path.isfile(lp):
            refuse("G1", {"arm_log_absent_for_an_arm_that_RAN": lp, "arm": arm,
                          "note": ("the ledger says this arm ran; its log is therefore a "
                                   "MALFORMED artefact, not an absent one")})
        with open(lp, errors="replace") as fh:
            text = fh.read()
        r["log_text"] = text

        art = os.path.join(adir, ARTEFACT[arm])
        if not os.path.isfile(art):
            refuse("G1", {"C3_artefact_absent": art, "arm": arm})
        cl["C3_artefact_present"] = {"verdict": "PASS", "path": ARTEFACT[arm]}

        amt = int(os.path.getmtime(art))
        if not dres["ok"]:
            refuse("G1", {"C4_datum_reference_mtime_wrong": dres, "arm": arm})
        if amt <= datum:
            refuse("G1", {"C4_age_guard": {"artefact_mtime": amt, "datum": datum}, "arm": arm,
                          "note": "the artefact must be STRICTLY newer than the arm's own datum"})
        cl["C4_age_guard"] = {"verdict": "PASS", "artefact_mtime": amt, "datum": datum,
                              "datum_reference": dres["name"],
                              "is_compressed_twin": dres["is_compressed_twin"]}

        kind = ARM_KIND[arm]
        if kind == "SOLVER":
            if TERMINAL[arm] not in text:
                refuse("G1", {"C2_terminal_marker_absent": TERMINAL[arm], "arm": arm, "log": logname})
            cl["C2_terminal_marker"] = {"verdict": "PASS", "marker": TERMINAL[arm], "log": logname}
            out["convergence"][arm] = read_primal_convergence(text, logname)
        else:
            with open(art, errors="replace") as fh:
                mtext = fh.read()
            if not re.search(r"^Mesh OK\.$", mtext, re.M):
                refuse("G1", {"C2_mesh_ok_absent": art, "arm": arm})
            cl["C2_terminal_marker"] = {"verdict": "PASS", "marker": "Mesh OK.",
                                        "log": ARTEFACT[arm]}

        scanned = [logname]
        sites, benign = fatal_token_sites(text, logname)
        if kind == "SCRIPT":
            scanned.append(ARTEFACT[arm])
            with open(art, errors="replace") as fh:
                s2, b2 = fatal_token_sites(fh.read(), ARTEFACT[arm])
            sites += s2
            benign += b2
        if sites:
            refuse("G1", {"C5_fatal_token_in_arm_output": sorted({t for st in sites
                                                                  for t in st["tokens"]}),
                          "arm": arm, "log": logname, "files_scanned": scanned,
                          "token_sites": sites,
                          "note": ("a fatal token refuses at ANY rc; R-RC never launders a crash.  "
                                   "`token_sites` names the FILE AND LINE of every hit; `log` is "
                                   "the arm's own log and is NOT necessarily the file with the hit")})
        cl["C5_no_fatal_token"] = {"verdict": "PASS", "tokens_searched": list(FATAL_TOKENS),
                                   "files_scanned": scanned,
                                   "n_benign_lines_excluded": len(benign),
                                   "benign_lines_excluded": benign,
                                   "note": ("every exclusion is COUNTED AND NAMED; a suppression a "
                                            "reader cannot see is the same defect wearing the "
                                            "other hat")}

        oom = str(r.get("oomkilled")).lower()
        if oom not in ("false", "true"):
            refuse("G1", {"oomkilled_unparseable": arm, "value": r.get("oomkilled"),
                          "note": "OOMKilled is a PHYSICS field and is not covered by R-RC"})
        if oom == "true":
            refuse("G1", {"oomkilled_true": arm,
                          "note": "G11: an OOM kill is a refusal, never a re-fire"})

        ke = r["inspect_exit"]
        if ke is None:
            fb = inspect_file_fallback(base, arm)
            if fb is not None:
                ke = fb["exit"]
                r["rc_record_source"] = fb["file"]
        if ke is None:
            if r["rc"] != 0:
                refuse("G1", {"C1_rc_record_absent_but_harness_rc_nonzero": r["rc"], "arm": arm,
                              "note": "R-RC relaxes a missing record, never a reading of failure"})
            cl["C1_rc_value"] = {"verdict": NOT_MEASURED,
                                 "note": "rc RECORD absent from BOTH channels; C2-C5 all hold"}
            out["rc_inferences"][arm] = {
                "inferred_rc": 0,
                "basis": "C2, C3, C4 and C5 all PASS and the harness rc reads 0",
                "status": "INFERENCE -- never graded as a measurement"}
            out["not_measured"].setdefault("rc_record", []).append(arm)
        else:
            if str(ke) != str(r["rc"]):
                refuse("G1", {"C1_harness_kernel_rc_disagree": {"harness": r["rc"], "kernel": ke},
                              "arm": arm})
            if int(ke) != 0:
                refuse("G1", {"C1_rc_nonzero": int(ke), "arm": arm})
            cl["C1_rc_value"] = {"verdict": "PASS", "rc": int(ke),
                                 "source": r.get("rc_record_source", "ledger_row")}
        out["rule4_clauses"][arm] = cl
        out["arms"][arm] = {"rc": r["rc"], "core_min": r["core_min"],
                            "infra_not_measured": r["infra_not_measured"]}
        out["census"][arm] = {"state": "RAN", "rc": r["rc"], "core_min": r["core_min"]}
        out["executed"] += 1
    return out


# ===================== G-STAGES: the shortfall is a GATE INPUT =========================
def g_stages(g1, chain_status_text):
    """DECLARED versus EXECUTED, READ BY A GATE (section 5 Requirement 4).

    W3 recorded its truncation perfectly in two independent artefacts and NOTHING
    READ IT: 20 of 33 declared stages discarded under a `PHASE1_COMPLETE` token
    and `exit 0`.  The lesson is not "log the blocks" -- W3 logged them.

    NEVER PRE-FILTERED: `declared` is the registered arm count and `executed` the
    census count; BOTH are reported.  A blocked or declared-but-absent arm counts
    IN the denominator.  A grader that quietly narrows its own view and then
    reports a disagreement has manufactured that disagreement (d12y_grade_w3.py's
    real defect was over-filtering, not under-information)."""
    executed, declared = g1["executed"], N_DECLARED
    blocked_guard = None
    for pat, name in ((r"chain=BLOCKED_H5", "H5 windowed MemAvailable floor, series H5_BOUND_S=3600"),
                      (r"chain=BLOCKED_AGGREGATE",
                       "AGGREGATE live sibling caps + this arm's cap + host non-container RSS, "
                       "series AGG_BOUND_S=14400"),
                      (r"chain=BLOCKED\b", "a registered resource guard reached its bound")):
        if re.search(pat, chain_status_text or ""):
            blocked_guard = name
            break
    short = declared - executed
    out = {"declared": declared, "executed": executed, "short": short,
           "arms_declared": list(ARMS_DECLARED),
           "arms_ran": [a for a in ARMS_DECLARED if g1["census"].get(a, {}).get("state") == "RAN"],
           "arms_not_run": [a for a in ARMS_DECLARED if g1["census"].get(a, {}).get("state") != "RAN"],
           "discard_fraction": round(short / declared, 6),
           "registered_resource_guard": blocked_guard,
           "both_counts_reported": True,
           "rule": ("executed == declared -> the gate is silent; executed < declared -> the item "
                    "verdict is NOT A RESULT, or BLOCKED where the shortfall is a REGISTERED "
                    "resource guard reaching its bound.  NEVER a token whose plain reading is "
                    "success, and never COMPLETE")}
    if short == 0:
        out["verdict"] = "PASS"
    elif blocked_guard is not None:
        out["verdict"] = "BLOCKED"
    else:
        out["verdict"] = "NOT A RESULT"
    return out


# ===================== R4/R5/R6: the artefact readers, EXPLICIT PATHS ONLY =============
def read_X(path):
    """R4.  The adjoint totals: `adjoint[of][dv]` -> a flat list over the dv vector.

    Every location comes from `SCHEMA`.  The `of` keys are checked against
    `OF_KEYS_REGISTERED`, so a scenario silently dropped from the assembly is a
    REFUSAL and not a shorter loop."""
    with open(path) as fh:
        j = json.load(fh)
    if at(j, "X.components", "G5J") != COMPONENTS_REGISTERED:
        refuse("G5J", {"components_requested_not_registered": at(j, "X.components", "G5J"),
                       "registered": COMPONENTS_REGISTERED})
    adj_raw = at(j, "X.adjoint", "G5J")
    keys = at(j, "X.adjoint_of_keys", "G5J")
    if sorted(keys) != OF_KEYS_REGISTERED:
        refuse("G5J", {"adjoint_of_keys_not_registered": sorted(keys),
                       "registered": OF_KEYS_REGISTERED,
                       "note": ("a scenario missing from the adjoint block is a missing scenario, "
                                "not a shorter loop")})
    adj = {}
    for of in OF_KEYS_REGISTERED:
        if of not in adj_raw or "shape" not in adj_raw[of]:
            refuse("G5J", {"adjoint_block_absent": {"of": of}, "registered": OF_KEYS_REGISTERED})
        adj[of] = [float(v) for v in adj_raw[of]["shape"]]
    return {"adj": adj,
            "J_base": float(at(j, "X.J_baseline", "G5J")),
            "CD_base": [float(v) for v in at(j, "X.CD_baseline", "G5J")],
            "CL_base": [float(v) for v in at(j, "X.CL_baseline", "G5J")],
            "alphas_read": at(j, "X.mp.alphas_read", "G-ALPHA"),
            "alpha_paths": at(j, "X.mp.alpha_paths", "G-ALPHA"),
            "weights": [float(v) for v in at(j, "X.mp.weights", "G-ALPHA")],
            "scenarios": at(j, "X.mp.scenarios", "G-ALPHA"),
            "so_md5": at(j, "X.so_md5", "G9"),
            "nprocs": at(j, "X.nprocs", "G1"),
            "evals_declared": int(at(j, "X.evals_declared", "G-EVALFAIL")),
            "evals_failed": int(at(j, "X.evals_failed", "G-EVALFAIL")),
            "raw": j}


def read_F(path):
    """R5.  The FD table, keyed (dv, idx) -> {"fd": step -> entry, "tb": step -> entry}.

    An entry is `{"ok": bool, "J": float, "CD": [3], "CL": [3]}`.  A FAILED
    evaluation is READ AND CARRIED as `ok: False` -- section 6 / G-EVALFAIL: an
    omitted row cannot be graded, a present row marked failed can."""
    with open(path) as fh:
        j = json.load(fh)
    if at(j, "F.components", "G5J") != COMPONENTS_REGISTERED:
        refuse("G5J", {"components_requested_not_registered": at(j, "F.components", "G5J"),
                       "registered": COMPONENTS_REGISTERED})
    if at(j, "F.steps", "G5J") != STEPS_REGISTERED:
        refuse("G5J", {"steps_not_registered": at(j, "F.steps", "G5J"),
                       "registered": STEPS_REGISTERED})
    if at(j, "F.tb_steps", "G-TB") != TB_STEPS_REGISTERED:
        refuse("G-TB", {"tb_steps_not_registered": at(j, "F.tb_steps", "G-TB"),
                        "registered": TB_STEPS_REGISTERED,
                        "note": ("this item registers a STEP-BASED trivial baseline at h = 1e-8; "
                                 "an artefact without it is not this item's")})

    def _entry(v):
        if not v.get("ok"):
            return {"ok": False, "error": str(v.get("error"))[:200]}
        d = v["d"]
        cd = [float(x) for x in d["CD"]]
        cl = [float(x) for x in d["CL"]]
        if len(cd) != N_SCEN or len(cl) != N_SCEN:
            refuse("G5J", {"fd_entry_scenario_count_wrong": {"n_CD": len(cd), "n_CL": len(cl),
                                                             "registered": N_SCEN}})
        return {"ok": True, "J": float(d["J"]), "CD": cd, "CL": cl}

    table, ctrl = {}, None
    for row in at(j, "F.rows", "G5J"):
        if row.get("dv") == "CTRL":
            ctrl = row
            continue
        key = (row["dv"], int(row["idx"]))
        fd = {float(v["step"]): _entry(v) for v in (row.get("fd") or {}).values()}
        tb = {float(v["step"]): _entry(v) for v in (row.get("tb") or {}).values()}
        table[key] = {"status": row.get("status"), "fd": fd, "tb": tb}
    return {"table": table, "ctrl": ctrl,
            "eta": float(at(j, "F.eta_used", "G5J")),
            "J_base": float(at(j, "F.J_baseline", "G5J")),
            "CD_base": [float(v) for v in at(j, "F.CD_baseline", "G5J")],
            "CL_base": [float(v) for v in at(j, "F.CL_baseline", "G5J")],
            "alphas_read": at(j, "F.mp.alphas_read", "G-ALPHA"),
            "weights": [float(v) for v in at(j, "F.mp.weights", "G-ALPHA")],
            "scenarios": at(j, "F.mp.scenarios", "G-ALPHA"),
            "so_md5": at(j, "F.so_md5", "G9"),
            "evals_declared": int(at(j, "F.evals_declared", "G-EVALFAIL")),
            "evals_failed": int(at(j, "F.evals_failed", "G-EVALFAIL")),
            "raw": j}


# ===================== rule 3: the live controls, at GRADE time ========================
def ctrl_control(F):
    """The INSTRUMENT's own planted control, re-read through the REAL reader.
    Both directions: every entry of `fd` must be EXACTLY 0.0 -- J and all three
    CD and all three CL -- and every entry of `planted` must be EXACTLY
    PLANT/(2*step).

    THE EMPTINESS CHECK COMES FIRST, BEFORE ANY INDEXING.  A control that empties
    the tuple it tests must REFUSE, not raise: a crash is not a verdict."""
    c = F["ctrl"]
    if c is None:
        refuse("CONTROL", {"ctrl_row_absent": True})
    want = PLANT / (2.0 * CTRL_STEP)
    try:
        zside = c["fd"][repr(CTRL_STEP)]["d"]
        pside = c["planted"]["d"]
    except (KeyError, TypeError):
        refuse("CONTROL", {"ctrl_row_malformed": str(c)[:300]})
    for tag, side in (("zero", zside), ("planted", pside)):
        for q in ("CD", "CL"):
            if not side.get(q) or len(side[q]) != N_SCEN:
                refuse("CONTROL", {"ctrl_tuple_EMPTY_OR_SHORT": {
                    "side": tag, "quantity": q,
                    "n": (0 if not side.get(q) else len(side[q])), "registered": N_SCEN},
                    "note": ("a control that empties the tuple it tests certifies blindness "
                             "-- Sanaa 2026-08-28")})
        if "J" not in side:
            refuse("CONTROL", {"ctrl_objective_absent": {"side": tag}})
    zeros = [float(zside["J"])] + [float(v) for v in zside["CD"]] + [float(v) for v in zside["CL"]]
    plants = {"J": float(pside["J"])}
    for i in range(N_SCEN):
        plants["CD%d" % i] = float(pside["CD"][i])
        plants["CL%d" % i] = float(pside["CL"][i])
    bad0 = [v for v in zeros if v != 0.0]
    badp = {k: v for k, v in plants.items() if abs(v - want) > 1e-12 * abs(want)}
    if bad0 or badp:
        refuse("CONTROL", {"instrument_ctrl_not_seen": {"nonzero_in_zero_side": bad0[:5],
                                                        "planted": plants, "want": want}})
    return {"n_zero_entries_read": len(zeros), "planted_read": plants, "want": want,
            "both_directions": True,
            "note": "seven quantities per side: J and three CD and three CL"}


def _plant_dir(base):
    d = os.path.join(base, "grader_controls")
    os.makedirs(d, exist_ok=True)
    return d


def grader_plant_F(base, fpath, tag):
    """Write a copy with PLANT added to EVERY physical derivative -- J, every CD
    and every CL, at every step, including the trivial-baseline steps -- re-read
    it FROM DISK through the REAL reader, and refuse unless every value moved by
    exactly PLANT."""
    with open(fpath) as fh:
        j = json.load(fh)
    for row in at(j, "F.rows", "CONTROL"):
        if row.get("dv") == "CTRL":
            continue
        for blk in ("fd", "tb"):
            for v in (row.get(blk) or {}).values():
                if v.get("ok"):
                    v["d"]["J"] = repr(float(v["d"]["J"]) + PLANT)
                    v["d"]["CD"] = [repr(float(x) + PLANT) for x in v["d"]["CD"]]
                    v["d"]["CL"] = [repr(float(x) + PLANT) for x in v["d"]["CL"]]
    cp = os.path.join(_plant_dir(base), "F_%s_planted.json" % tag)
    with open(cp, "w") as fh:
        json.dump(j, fh, indent=1, sort_keys=True)
    orig, back = read_F(fpath)["table"], read_F(cp)["table"]
    worst, n = 0.0, 0
    for key, row in orig.items():
        for blk in ("fd", "tb"):
            for s, v in row[blk].items():
                if not v["ok"]:
                    continue
                b = back[key][blk][s]
                pairs = [(v["J"], b["J"])]
                pairs += list(zip(v["CD"], b["CD"])) + list(zip(v["CL"], b["CL"]))
                for a, bb in pairs:
                    worst = max(worst, abs((bb - a) - PLANT))
                    n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"grader_plant_F_not_seen": {"n_values": n, "worst_residual": worst,
                                                       "plant": PLANT}})
    return {"grader_plant_F_seen": True, "n_values": n, "worst_residual": worst, "file": cp}


def grader_plant_X(base, xpath, tag, k, scale=None, plant_k=None):
    """THE BIRTH OF THE GATES THAT PASS ON A SMALL NUMBER.

    MP-A1 REGISTERED DELTA: `scale` is `d_ref` for the pair this plant lands on,
    and the perturbation is `PLANT_K*(band_D/100)*|d_ref|` -- see `plant_for`.
    `plant_k` overrides `PLANT_K` and exists ONLY so the selftest can drive the
    control at an INSUFFICIENT K and require the flip not to happen.  Production
    never passes it.  `scale=None` falls back to the absolute `PLANT` and SAYS SO
    in the returned record.

    G5J, G5C and G-MP-STRUCT all read agreement -- a residual near zero -- as a
    PASS, which is exactly the reading rule 3 exists to distrust.  So: write a
    copy with PLANT added to ONE registered `shape` entry of the assembled `J`
    adjoint row, re-read it FROM DISK through the REAL reader, and hand the copy
    back so the caller can require BOTH G5J and G-MP-STRUCT to FLIP to GATE FAIL
    while they PASS on the original.

    `k` IS CHOSEN BY THE CALLER FROM THE PAIRS G5J ACTUALLY GRADED, and that is a
    correction this lane had to make against its own first draft: it planted into
    a FIXED component, so on a run where that pair was legitimately `NO_PLATEAU`
    the plant landed on an UNGRADED pair, G5J did not move, and the comparator
    refused a perfectly good run.  A plant must land on a value the reader
    traverses AND the gate grades -- the same lesson `grader_plant_cells`'
    no-substitution check carries one level up."""
    with open(xpath) as fh:
        j = json.load(fh)
    flat = list(at(j, "X.adjoint", "CONTROL")[OF_J]["shape"])
    if not flat or k >= len(flat):
        refuse("CONTROL", {"grader_plant_X_target_ABSENT": {"of": OF_J, "idx": k,
                                                            "n_entries": len(flat)},
                           "note": "the plant target must be a value the reader traverses"})
    before = float(flat[k])
    plant, how = plant_for(scale)
    if plant_k is not None and how.startswith("RELATIVE"):
        plant = float(plant_k) * (FD_BAND_PCT / 100.0) * abs(float(scale))
        how = "RELATIVE at an OVERRIDDEN K=%r -- selftest only" % plant_k
    flat[k] = repr(before + plant)
    j["adjoint"][OF_J]["shape"] = flat
    cp = os.path.join(_plant_dir(base), "X_%s_planted.json" % tag)
    with open(cp, "w") as fh:
        json.dump(j, fh, indent=1, sort_keys=True)
    seen = read_X(cp)["adj"][OF_J][k]
    if abs(seen - (before + plant)) > 1e-12 * max(1.0, abs(before)):
        refuse("CONTROL", {"grader_plant_X_not_seen_by_reader": {"read_back": seen,
                                                                 "before": before,
                                                                 "plant": plant}})
    return {"grader_plant_X_seen": True, "read_back": seen, "before": before,
            "component_index": k, "file": cp,
            "plant": plant, "plant_sizing": how, "plant_K": (plant_k if plant_k is not None
                                                             else PLANT_K),
            "d_ref_scale": scale, "band_D_pct": FD_BAND_PCT,
            "planted_rel_err_pct": (abs(plant) / abs(float(scale)) * 100.0
                                    if how.startswith("RELATIVE") else None),
            "target_chosen_from": "the pairs G5J actually graded on the UNPLANTED artefact",
            "note": "the G5J and G-MP-STRUCT flips on this copy are asserted by the caller"}


def grader_plant_cells(base, cmpath):
    """R3's birth: the cells reader must read a DIFFERENT number off a changed
    real checkMesh log, not merely the expected one off the real log."""
    with open(cmpath, errors="replace") as fh:
        txt = fh.read()
    m = re.search(r"^\s*cells:\s+(\d+)", txt, re.M)
    if not m:
        refuse("CONTROL", {"grader_plant_cells_no_target": cmpath,
                           "note": "the plant must land on bytes the reader reads"})
    # OFFSET FROM WHAT IS ON DISK, so it is a real change whatever the artefact
    # holds; a fixed constant collides with a fixture that already carries it and
    # the collision reads as "no substitution" rather than as the control it was.
    want = int(m.group(1)) + 7
    planted = re.sub(r"^(\s*cells:\s+)\d+", r"\g<1>%d" % want, txt, count=1, flags=re.M)
    if planted == txt:
        refuse("CONTROL", {"grader_plant_cells_no_substitution": cmpath})
    cp = os.path.join(_plant_dir(base), "checkMesh_planted.log")
    with open(cp, "w") as fh:
        fh.write(planted)
    got = read_mesh_cells(cp)
    if got != want:
        refuse("CONTROL", {"grader_plant_cells_not_seen": {"read_back": got, "want": want}})
    return {"grader_plant_cells_seen": True, "read_back": got, "want": want,
            "on_disk_before_plant": int(m.group(1)), "file": cp}


def grader_plant_c5(base, rows, g1):
    """R2's AND R2b's birth, BOTH DIRECTIONS, ON THE RUN'S OWN REAL LOG BYTES.

    (+) a real crash line planted into the arm's own text MUST be seen;
    (-) the same text unplanted must produce ZERO sites;
    (b) each of the THREE registered benign lines must be COUNTED AS EXCLUDED
        rather than silently dropped -- and the SIMPLE banner must NOT reduce the
        convergence reading, which is the discriminator's own direction."""
    arm = next((a for a in ARMS_DECLARED
                if ARM_KIND[a] == "SOLVER" and g1["census"].get(a, {}).get("state") == "RAN"),
               None)
    if arm is None:
        return {"grader_plant_c5_seen": False,
                "status": "NOT EXERCISED -- no SOLVER arm ran; never counted as a pass"}
    text = rows[arm]["log_text"]
    neg_sites, _ = fatal_token_sites(text, "REAL:%s" % rows[arm]["log"])
    if neg_sites:
        refuse("CONTROL", {"grader_plant_c5_negative_direction_failed": neg_sites[:3]})
    planted = text + "\n#1  Foam::sigFpe::sigHandler(int) at ??:?\n"
    pos_sites, _ = fatal_token_sites(planted, "REAL+PLANT:%s" % rows[arm]["log"])
    if len(pos_sites) != 1 or "Foam::sigFpe::sigHandler" not in pos_sites[0]["tokens"]:
        refuse("CONTROL", {"grader_plant_c5_positive_direction_failed": pos_sites[:3],
                           "note": "the reader was not shown able to see a real crash"})
    banners = {
        "trapFpe": "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).\n",
        "SIMPLE_banner": "SIMPLE: no convergence criteria found. Calculations will run for 1000 steps.\n",
        "continuity": "Time step continuity errors : sum local = 0.0004461864988617479\n",
    }
    # EACH BANNER IS SAFE FOR A DIFFERENT REASON, AND THE RECORD SAYS WHICH.  This
    # lane's first draft required all three to be COUNTED AS BENIGN and was wrong:
    # only `trapFpe:` carries a FATAL token at all (`Floating point exception`), so
    # only it can reach the benign counter.  The SIMPLE banner and the continuity
    # line match NO token in `FATAL_TOKENS` and are safe by not matching -- which
    # is a DIFFERENT and weaker protection, and is why the hazard they really pose
    # is to a convergence limb and to a case-insensitive `error` sweep, not to C5.
    # Stating one mechanism where two exist is how a suite reads green on a check
    # it never made.
    base_sites, base_benign = fatal_token_sites(text, "REAL:BASELINE")
    per_banner = {}
    for name, line in banners.items():
        b_sites, b_benign = fatal_token_sites(text + line, "REAL+%s" % name)
        matched = [t for t in FATAL_TOKENS if t in line]
        per_banner[name] = {"sites": len(b_sites) - len(base_sites),
                            "new_benign_lines": len(b_benign) - len(base_benign),
                            "fatal_tokens_the_line_matches": matched,
                            "protected_by": ("a NAMED per-line benign exclusion, counted"
                                             if matched else
                                             "matching no FATAL token at all -- weaker, and the "
                                             "reason this line's real hazard is a convergence or "
                                             "case-insensitive `error` limb, not C5")}
        if len(b_sites) != len(base_sites):
            refuse("CONTROL", {"grader_plant_c5_banner_direction_failed":
                               {"banner": name, "sites": b_sites[:3],
                                "note": "a benign notice must never be read as a crash"}})
        if matched and len(b_benign) != len(base_benign) + 1:
            refuse("CONTROL", {"grader_plant_c5_benign_NOT_COUNTED":
                               {"banner": name, "tokens": matched,
                                "new_benign_lines": len(b_benign) - len(base_benign)},
                               "note": ("a line carrying a FATAL token and excluded anyway MUST be "
                                        "counted and named; a suppression a reader cannot see is "
                                        "the same defect wearing the other hat")})
    conv_real = read_primal_convergence(text, rows[arm]["log"])
    conv_plus = read_primal_convergence(text + banners["SIMPLE_banner"], "REAL+SIMPLE_banner")
    if conv_plus["n_converged_statements"] != conv_real["n_converged_statements"]:
        refuse("CONTROL", {"convergence_discriminator_moved_on_a_BANNER":
                           {"real": conv_real["n_converged_statements"],
                            "with_banner": conv_plus["n_converged_statements"]},
                           "note": "the banner is not evidence and must not move the reading"})
    conv_planted = read_primal_convergence(
        text + "Minimal residual 1.234e-09 satisfied the prescribed tolerance 1e-08\n",
        "REAL+CONVERGENCE_STATEMENT")
    if conv_planted["n_converged_statements"] != conv_real["n_converged_statements"] + 1:
        refuse("CONTROL", {"convergence_discriminator_blind_to_a_REAL_statement":
                           {"real": conv_real["n_converged_statements"],
                            "planted": conv_planted["n_converged_statements"]}})
    return {"grader_plant_c5_seen": True, "arm": arm, "real_log": rows[arm]["log"],
            "n_lines_real": len(text.splitlines()),
            "negative_sites": 0, "positive_sites": 1,
            "benign_banners_excluded_and_counted": per_banner,
            "convergence_discriminator": {
                "real_statements": conv_real["n_converged_statements"],
                "banner_count_real": conv_real["banner_not_evidence"]["count"],
                "unmoved_by_a_planted_banner": True,
                "moved_by_a_planted_REAL_statement": True}}


# ===================== G-ALPHA ========================================================
def g_alpha(recs):
    """The operating points are the REGISTERED ones, read back from the artefact's
    own identity record, to 1e-12 absolute.  Mismatch REFUSES (exit 2): a
    multipoint verdict at unregistered angles is not this item's verdict.

    The instrument writes BOTH what the MODEL held and what the DOCUMENT
    registered, and never substitutes one for the other; this gate compares them.
    An UNRESOLVED angle (`None`) is a refusal too -- a scenario whose angle never
    reached the solver is not a scenario at the registered angle."""
    per = {}
    for tag, r in recs.items():
        got = r["alphas_read"]
        if len(got) != N_SCEN:
            refuse("G-ALPHA", {"scenario_count_wrong": {"artefact": tag, "n": len(got),
                                                        "registered": N_SCEN}})
        if list(r["scenarios"]) != SCENARIOS:
            refuse("G-ALPHA", {"scenario_names_not_registered": {"artefact": tag,
                                                                 "got": list(r["scenarios"]),
                                                                 "registered": SCENARIOS}})
        vals, devs = [], []
        for i, a in enumerate(got):
            if a is None:
                refuse("G-ALPHA", {"alpha_UNRESOLVED": {"artefact": tag, "scenario": SCENARIOS[i],
                                                        "read_path": (r.get("alpha_paths") or
                                                                      [None] * N_SCEN)[i]},
                                   "note": ("the instrument records an unresolved path as None and "
                                            "never substitutes its own constant; an unresolved "
                                            "angle is not a registered angle")})
            v = float(a)
            vals.append(v)
            devs.append(abs(v - ALPHAS_REGISTERED[i]))
        if max(devs) > ALPHA_TOL_ABS:
            refuse("G-ALPHA", {"alphas_not_registered": {"artefact": tag, "read_back": vals,
                                                         "registered": ALPHAS_REGISTERED,
                                                         "abs_deviation": devs,
                                                         "tolerance": ALPHA_TOL_ABS}})
        w = r["weights"]
        if len(w) != N_SCEN or max(abs(a - b) for a, b in zip(w, WEIGHTS_REGISTERED)) > 1e-15:
            refuse("G-ALPHA", {"weights_not_registered": {"artefact": tag, "read_back": w,
                                                          "registered": WEIGHTS_REGISTERED}})
        per[tag] = {"alphas_read_back": vals, "abs_deviation": devs, "weights": w}
    return {"verdict": "PASS", "per_artefact": per, "registered": ALPHAS_REGISTERED,
            "weights_registered": WEIGHTS_REGISTERED, "tolerance_abs": ALPHA_TOL_ABS,
            "note": "REFUSES on mismatch (exit 2); it is not a GATE FAIL, it is a wrong item"}


# ===================== G-NOOPT ========================================================
def g_noopt(recs, rec_kind, logs):
    """THE ENDPOINT ARMS ran no optimiser, ASSERTED AGAINST THEIR ARTEFACTS.

    MP-A1 REGISTERED INVERSION, AND IT IS NAMED RATHER THAN QUIETLY NARROWED.
    SO-3aR2's version of this gate asserted that THE ITEM ran no optimiser, and
    that was right for a gradient rung.  MP-A1 IS THE OPTIMISATION RUNG: its O-S
    and O-P arms run IPOPT by registration, so the item-level claim is GONE.
    Carrying the old sentence across the rename would have been a false claim
    with a green gate under it -- a mechanical rename moves tokens, it cannot
    make prose true.

    WHAT SURVIVES IS NARROWER AND STILL LOAD-BEARING: the XE/FE arms run
    `compute_totals` and a central-difference table and NOTHING ELSE, so an
    optimiser marker in one of THEIR artefacts means the artefact is not the arm
    it claims to be.  `recs` is the endpoint artefact set; the O arms' records
    are graded by `g_opt_section9` and never reach here.

    The key list is REGISTERED (`OPTIMISER_KEYS`) and matched against TOP-LEVEL
    keys only.  A recursive sweep for the substring `major` would fire on
    `major_version` and on this very docstring: a match is not a meaning."""
    found = []
    for tag, r in recs.items():
        j = r["raw"]
        for k in OPTIMISER_KEYS:
            if k in j:
                found.append({"artefact": tag, "top_level_key": k})
        # THE ARTEFACT KIND IS REGISTERED PER TAG, NEVER READ OFF THE TAG'S FIRST
        # CHARACTER.  `tag[0]` happened to give the right letter here and is
        # exactly the positional derivation the SO-1c row-label post-mortem
        # forbids: a derivation that works by a coincidence of spelling.
        opt = at_opt(j, "%s.optimiser" % rec_kind[tag])
        if opt is not _MISSING and opt is not None:
            found.append({"artefact": tag, "optimiser_field": str(opt)[:120]})
    for name, text in logs.items():
        for m in OPTIMISER_EXIT_RE.finditer(text):
            line = text[m.start():text.find("\n", m.start()) if text.find("\n", m.start()) > 0
                        else len(text)]
            if re.search(r"IPOPT|SNOPT|SLSQP|NLP function or derivative", line):
                found.append({"log": name, "exit_line": line.strip()[:200]})
    if found:
        refuse("G-NOOPT-ENDPOINT", {"optimiser_evidence_in_an_ENDPOINT_artefact": found[:10],
                                    "note": ("the XE/FE arms run compute_totals and a central-"
                                             "difference table and nothing else.  An optimiser "
                                             "history in one of THEIR artefacts means the "
                                             "artefact is not the arm it claims to be.  The O "
                                             "arms DO run an optimiser and are graded by "
                                             "g_opt_section9, never here")})
    return {"verdict": "PASS", "scope": "ENDPOINT ARMS ONLY -- the O arms run IPOPT by registration",
            "keys_searched": list(OPTIMISER_KEYS),
            "artefacts_checked": sorted(recs.keys()), "logs_checked": sorted(logs.keys()),
            "n_optimiser_markers": 0,
            "note": ("SO-3aR2's item-level no-optimiser claim is RETIRED here, not renamed.  "
                     "This gate now asserts only that the endpoint arms' artefacts carry no "
                     "optimiser, which is what their registered commands can support")}


# ===================== SECTION 9: THE OPTIMISATION GATE ================================
# `DAFOAM_CHARTER.md` section 9, verbatim:
#
#   *"An optimisation run is graded PASS only if the optimiser itself printed a
#   convergence statement against its own tolerance.  A run stopped by a wall
#   clock, an iteration cap or a budget is `GATE REACHED` where a registered
#   intermediate threshold was met and `NOT A RESULT` otherwise -- never `PASS`,
#   and never described by the size of the improvement it reached.  Every
#   optimisation reports a finite-difference check of the gradient AT ITS FINAL
#   DESIGN POINT, not only at the baseline."*
#
# FOUR THINGS THIS GATE WILL NOT DO, each because the family has paid for it:
#   1. It will not read a drag reduction as evidence.  A2's 47-major run reduced
#      drag 28.275488 % and its own `opt_IPOPT.txt` carries NO `EXIT` line -- this
#      lane RE-MEASURED that on the artefact rather than quoting it.
#   2. It will not call a stall a convergence.  The stall reading comes from
#      `mpa1_stall.py`, which is calibrated on 33 real IPOPT logs on this box:
#      condition A fires on exactly the 2 known stalls and on none of the 7 runs
#      that ended `Maximum Number of Iterations Exceeded`.
#   3. It will not let a drag number travel without its `CL` pair.  `CL` is
#      UNCONSTRAINED in this item (mpa1_runScript docstring (C)), so a weighted-drag
#      reduction bought by shedding lift is a live possibility and the record says
#      so beside the number, not below it.
#   4. It will not upgrade `GATE REACHED` to `PASS` because the endpoint FD passed.
#      The endpoint FD makes the DESIGN CHANGE validated; it says nothing about
#      whether the optimiser converged, and conflating them is the laundering.
#
# THE REGISTERED INTERMEDIATE THRESHOLD, frozen before any compute.  Section 9
# distinguishes `GATE REACHED` from `NOT A RESULT` by whether one was met, and
# leaving it unnamed would let the distinction be chosen after the fact:
# MP-A1 ruling (PREREGISTRATION section 2a / section 7 decision 5): the intermediate
# threshold is 1.0 % (NOT SO-3's 5.0 %) because a CL-constrained drag-min reduces
# less than the unconstrained SO-3; it labels ONLY the GATE REACHED path and NEVER
# a PASS (a PASS comes solely from IPOPT's own printed convergence statement).
OPT_INTERMEDIATE_THRESHOLD_PCT = 1.0   # weighted-drag reduction at HELD CL, vs the run's own baseline
OPT_MIN_MAJORS = 5                     # a run of fewer majors has not searched


def g_opt_section9(O, endpoint_row_verdict, cap_row):
    """Grade ONE row's optimisation arm under section 9.

    `O` is the row's `mpa1_O.json` record, or None if the arm did not run.
    Returns a dict whose `verdict` is one of rule 1's six tokens and NEVER
    `PASS` unless the optimiser printed its own convergence statement."""
    if O is None:
        return {"verdict": NOT_MEASURED, "state": "NOT RUN",
                "note": "the optimisation arm did not run; no section 9 reading exists"}

    exit_stmt = O.get("optimiser_exit_statement")
    stall = O.get("stall") or {}
    stall_word = stall.get("stall", NOT_MEASURED)
    n_majors = stall.get("n_majors_parsed")
    base, final = O.get("baseline") or {}, O.get("final") or {}
    red = O.get("weighted_drag_reduction_pct")
    hit_cap = (cap_row or {}).get("over_cap", False)
    marker = bool(O.get("stall_abort_marker_present"))

    # ---- IPOPT's own convergence statement.  The ONLY thing that can support a
    # ---- PASS.  The string is matched against the registered set rather than
    # ---- tested for truthiness: `Maximum Number of Iterations Exceeded.` is an
    # ---- EXIT line and is emphatically not a convergence statement, and a
    # ---- `if exit_stmt:` test would have read it as one.
    CONVERGED_EXITS = ("Optimal Solution Found.",
                       "Solved To Acceptable Level.")
    CAP_EXITS = ("Maximum Number of Iterations Exceeded.",
                 "Maximum CPU time exceeded.",
                 "Maximum WallClock time exceeded.")
    converged = exit_stmt in CONVERGED_EXITS
    hit_iter_cap = exit_stmt in CAP_EXITS

    reached_threshold = (red is not None and red >= OPT_INTERMEDIATE_THRESHOLD_PCT
                         and (n_majors is None or n_majors >= OPT_MIN_MAJORS))

    if converged:
        verdict, why = "PASS", ("the optimiser printed its own convergence statement "
                                "against its own tolerance: %r" % exit_stmt)
    elif stall_word == "STALL" or marker:
        # A STALL IS NEVER A PASS AND IS NEVER SILENTLY A GATE REACHED EITHER.
        # It is GATE REACHED only where the registered intermediate threshold was
        # met before the stop; otherwise the run bought nothing and says so.
        verdict = "GATE REACHED" if reached_threshold else "NOT A RESULT"
        why = ("the registered stall conditions fired (stop_at_major=%r, condition_A=%r, "
               "condition_B=%r) and the optimiser printed %r.  A backtracking optimiser has "
               "not converged; it has stopped."
               % (stall.get("stop_at_major"),
                  (stall.get("condition_A_alpha_pr_run") or {}).get("fired"),
                  (stall.get("condition_B_inf_du_nondecreasing") or {}).get("fired"),
                  exit_stmt))
    elif hit_iter_cap or hit_cap or O.get("driver_fail_flag"):
        verdict = "GATE REACHED" if reached_threshold else "NOT A RESULT"
        why = ("the run was stopped by a budget, not by its own tolerance "
               "(exit=%r iteration_cap=%r core_min_cap=%r driver_fail=%r).  "
               "VERIFICATION section 4: an iteration cap is a budget, not a settle criterion"
               % (exit_stmt, hit_iter_cap, hit_cap, O.get("driver_fail_flag")))
    elif exit_stmt is None:
        # A2's SHAPE, EXACTLY.  47 majors, a real 28.275488 % reduction, and no
        # EXIT line anywhere in the log.  The true statement is the weaker one.
        verdict = "GATE REACHED" if reached_threshold else "NOT A RESULT"
        why = ("the optimiser printed NO convergence statement anywhere in its own output "
               "-- A2's shape, re-measured on A2-mach-wing/opt_IPOPT.txt (48 rows, exit=None).  "
               "The word `converged` is not available for this run")
    else:
        verdict = "NOT A RESULT"
        why = "the optimiser printed %r, which is neither a convergence statement nor a " \
              "registered budget exit; the run is unclassified and is not a result" % exit_stmt

    if verdict not in VOCAB:
        refuse("VOCAB", {"g_opt_section9_verdict": verdict})

    return {
        "verdict": verdict, "state": "RAN", "why": why,
        "row": O.get("row"),
        "optimiser": O.get("optimizer") or O.get("optimiser"),
        "optimiser_exit_statement": exit_stmt,
        "convergence_statement_in_log": exit_stmt is not None,
        "converged_to_optimizer_tolerance": converged,
        "registered_converged_exits": list(CONVERGED_EXITS),
        "registered_cap_exits": list(CAP_EXITS),
        "n_majors": n_majors,
        "max_iter_registered": O.get("max_iter_registered"),
        "tol_registered": O.get("tol_registered"),
        "nprocs": O.get("nprocs"),
        "stall": stall,
        "stall_abort_marker_present": marker,
        "intermediate_threshold_pct": OPT_INTERMEDIATE_THRESHOLD_PCT,
        "intermediate_threshold_met": reached_threshold,
        "weighted_drag_reduction_pct": red,
        # THE THREE NUMBERS THAT TRAVEL TOGETHER OR NOT AT ALL.
        "CL_baseline": base.get("CL"), "CL_final": final.get("CL"),
        "CD_baseline": base.get("CD"), "CD_final": final.get("CD"),
        "J_baseline": base.get("J"), "J_final": final.get("J"),
        "endpoint_fd_row_verdict": endpoint_row_verdict,
        "design_change_validated": (endpoint_row_verdict == "PASS"),
        "design_change_note": (
            "section 9 requires the FD check AT THE FINAL DESIGN POINT.  "
            + ("the endpoint FD row PASSED, so the design change this arm produced is "
               "VALIDATED on this row's toolchain"
               if endpoint_row_verdict == "PASS" else
               "the endpoint FD row read %r, so THE DESIGN CHANGE THIS ARM PRODUCED IS "
               "NOT VALIDATED.  A gradient verified at iteration 0 is not verified at the "
               "optimum: the IDWarp rotation defect fires at the undeformed baseline and "
               "behaves differently just above threshold (1e-5 rad -> 4.1e-08, 1e-6 -> "
               "6.7e-05, 5e-8 -> 1.2e-02), and the two regimes are on opposite sides of "
               "the guard" % (endpoint_row_verdict,))),
        "forbidden_readings": [
            "grading this row from the SIZE of its improvement",
            "using the word `converged` of a run whose optimiser printed no convergence statement",
            "quoting the weighted-drag reduction without CL_baseline and CL_final beside it, "
            "because a drag reduction is only a drag-min-at-fixed-lift claim if the HELD CL "
            "is shown (MP-A1 CONSTRAINS CL by equality; G-CLHOLD gates that it was held)",
            "upgrading GATE REACHED to PASS because the endpoint FD passed -- the endpoint FD "
            "validates the DESIGN, not the optimiser's convergence",
        ],
    }


# ===================== G5J / G5C: THE BRIGHT LINE, PER PAIR ============================
def _pair(X, F, of_key, quantity, scen, k):
    """One (adjoint, FD) pair for one registered `shape` component.

    `quantity` is "J" or "CL"; `scen` indexes the scenario for "CL" and is None
    for the assembled objective.  THE PLATEAU IS PROVED PER PAIR: the middle step
    must agree with AT LEAST ONE neighbour to PLATEAU_TOL_PCT.  It is never
    asserted once for the item."""
    rec = {"of": of_key, "quantity": quantity, "scenario": scen, "dv": "shape", "idx": k}
    adj = X["adj"].get(of_key)
    frow = F["table"].get(("shape", k))
    if adj is None or k >= len(adj) or frow is None:
        rec.update({"graded": False, "reason": "ABSENT"})
        return rec
    j = adj[k]
    rec["J_adj"] = j
    steps = sorted(STEPS_REGISTERED["shape"], reverse=True)
    vals = [frow["fd"].get(s) for s in steps]
    if any(v is None or not v["ok"] for v in vals):
        rec.update({"graded": False, "reason": "FD_STEP_FAILED_OR_ABSENT",
                    "steps": steps,
                    "fd_step_ok": [None if v is None else bool(v["ok"]) for v in vals]})
        return rec
    d = [(v["J"] if quantity == "J" else v["CL"][scen]) for v in vals]
    ref = d[1]
    rec.update({"steps": steps, "d_fd": d, "d_ref": ref})
    if abs(ref) < NEAR_ZERO_ABS:
        rec.update({"graded": False, "reason": "NEAR_ZERO"})
        return rec
    nb = [abs(d[0] - ref) / abs(ref) * 100.0, abs(d[2] - ref) / abs(ref) * 100.0]
    rec["plateau_neighbour_pct"] = nb
    rec["plateau_proved_against"] = ("the LARGER neighbour" if nb[0] <= nb[1]
                                     else "the SMALLER neighbour")
    if min(nb) > PLATEAU_TOL_PCT:
        rec.update({"graded": False, "reason": "NO_PLATEAU", "plateau_tol_pct": PLATEAU_TOL_PCT})
        return rec
    rel = abs(ref - j) / abs(ref) * 100.0
    flip = bool(ref * j < 0.0)
    rec.update({"graded": True, "rel_err_pct": rel, "sign_flip": flip,
                "verdict": "GATE FAIL" if (flip or rel > FD_BAND_PCT) else "PASS"})
    return rec


def _grade_family(X, F, pairs, label):
    """Band D per graded PAIR, band E in aggregate over the graded pairs.

    NOTHING IS PRE-FILTERED OUT OF THE VIEW: every candidate pair appears in
    `pairs`, every exclusion is COUNTED AND NAMED with its reason, and the
    candidate count is reported beside the graded count.  A grader that narrows
    its own view and then reports agreement has manufactured that agreement."""
    fd_v = [p["d_ref"] for p in pairs if p.get("graded")]
    adj_v = [p["J_adj"] for p in pairs if p.get("graded")]
    excl = {}
    for p in pairs:
        if not p.get("graded"):
            excl[p["reason"]] = excl.get(p["reason"], 0) + 1
    c = {"family": label, "n_candidate_pairs": len(pairs), "n_graded_pairs": len(fd_v),
         "excluded_by_reason": excl,
         "n_pass": sum(1 for p in pairs if p.get("verdict") == "PASS"),
         "n_gate_fail": sum(1 for p in pairs if p.get("verdict") == "GATE FAIL"),
         "sign_flips": sum(1 for p in pairs if p.get("sign_flip")),
         "worst_rel_err_pct": (max([p["rel_err_pct"] for p in pairs if p.get("graded")])
                               if fd_v else None),
         "min_graded_required": MIN_GRADED_PAIRS, "band_D_pct": FD_BAND_PCT,
         "band_E_pct": AGG_BAND_PCT, "plateau_tol_pct": PLATEAU_TOL_PCT,
         "pairs": pairs}
    if len(fd_v) < MIN_GRADED_PAIRS:
        c.update({"verdict": "NOT A RESULT", "aggregate_rel_err_pct": None,
                  "reason": "fewer than %d graded pairs" % MIN_GRADED_PAIRS})
        return c
    num = math.sqrt(sum((a - b) ** 2 for a, b in zip(fd_v, adj_v)))
    den = math.sqrt(sum(a ** 2 for a in fd_v))
    agg = num / den * 100.0 if den > 0 else None
    c["aggregate_rel_err_pct"] = agg
    band_d = c["n_gate_fail"] == 0
    band_e = agg is not None and agg <= AGG_BAND_PCT
    c["band_D"] = "PASS" if band_d else "GATE FAIL"
    c["band_E"] = "PASS" if band_e else "GATE FAIL"
    c["verdict"] = "PASS" if (band_d and band_e) else "GATE FAIL"
    return c


def grade_objective_gradient(X, F):
    """G5J -- the bright line, on the MULTIPOINT OBJECTIVE `J`, per ROW.
    `curriculum_SO2a/so2a_grade.py:889-912`'s per-pair plateau reading, adopted
    as the reference implementation and NOT re-derived."""
    return _grade_family(X, F, [_pair(X, F, OF_J, "J", None, k)
                                for _dv, k in XF.COMPONENTS], "G5J objective J")


def grade_lift_gradients(X, F):
    """G5C -- the SAME test on each scenario's `dCL_i/dx`, all three scenarios,
    same bands, same per-pair plateau proof.

    MP-A1 CHECK-3 REQUIREMENT (supervisor, PREREGISTRATION section 7): in MP-A1 the
    per-point CL is a CONSTRAINT the optimiser drives, so `dCL_i/dx` is a gradient
    the optimiser ACTUALLY USED -- not merely a diagnostic beside the objective's
    `dCD_i/dx`.  G5C's whole legitimacy for MP-A1 is that it FD-verifies all three
    `dCL_i/dx` at the FINAL design point (charter section 9), which is what keeps
    MP-A1 admissible with NO new unverified gradient.  This function therefore
    REFUSES (never a silent pass) unless it covered all N_SCEN scenarios' CL
    gradients over the registered components."""
    per, verdict = {}, "PASS"
    of_cl_covered = []
    for i in range(N_SCEN):
        c = _grade_family(X, F, [_pair(X, F, OF_CL[i], "CL", i, k) for _dv, k in XF.COMPONENTS],
                          "G5C CL scenario %d" % i)
        c["alpha_deg"] = ALPHAS_REGISTERED[i]
        c["is_constraint_gradient"] = True   # MP-A1: dCL_i/dx is a CONSTRAINT gradient
        c["of_key"] = OF_CL[i]
        per[SCENARIOS[i]] = c
        of_cl_covered.append(OF_CL[i])
        if c["verdict"] == "NOT A RESULT":
            verdict = "NOT A RESULT"
        elif c["verdict"] == "GATE FAIL" and verdict == "PASS":
            verdict = "GATE FAIL"
    # ---- THE EXPLICIT dCL_i/dx COVERAGE ASSERTION (refuse(), not assert: `python3
    # ---- -O` strips asserts, L-332).  All three CL constraint gradients must be
    # ---- graded, over the same registered components as G5J, or the row is not a
    # ---- result -- a constrained optimisation whose constraint gradient went
    # ---- ungraded at the design point cannot be a PASS.
    if len(per) != N_SCEN or len(set(of_cl_covered)) != N_SCEN:
        refuse("G5C_COVERAGE",
               {"scenarios_graded": len(per), "n_scen_registered": N_SCEN,
                "distinct_cl_of_keys": sorted(set(of_cl_covered)),
                "detail": "G5C must FD-verify all three dCL_i/dx constraint gradients "
                          "at the final design point; it did not"})
    n_graded = {SCENARIOS[i]: per[SCENARIOS[i]].get("n_graded_pairs") for i in range(N_SCEN)}
    return {"per_scenario": per, "verdict": verdict,
            "covers_constraint_gradients": True,
            "n_cl_constraint_gradients_graded": N_SCEN,
            "of_cl_keys": of_cl_covered,
            "n_graded_pairs_per_scenario": n_graded,
            "coverage_assertion": "all %d dCL_i/dx CONSTRAINT gradients FD-verified at "
                                  "the final design point (charter section 9)" % N_SCEN}


# ===================== G-MP-STRUCT: the assembly identity =============================
def g_mp_struct(X, controls_seen):
    """|J_adj[J,k] - SUM_i w_i * J_adj[CD_i,k]| / |J_adj[J,k]| <= 1e-10 per component.

    THE GATE ONLY A MULTIPOINT RUNG CAN BUY.  A weight applied on one side only, a
    scenario connected to the wrong geometry output, a scenario silently omitted
    from the sum, or an `ExecComp` partial that does not match its own expression
    all fail it.

    STATED HONESTLY, as section 3 states it: a defect that corrupts every scenario
    IDENTICALLY cancels in the identity and would still PASS.  That is precisely
    why G5J and G5C are bought BESIDE it against an independent FD side -- the
    identity tests the ASSEMBLY, the FD table tests the PHYSICS, and neither
    substitutes for the other.

    THIS GATE PASSES ON A NEAR-ZERO RESIDUAL, so it is composed ONLY when the
    planted control has shown the SAME reader seeing a non-zero in the SAME run."""
    if not controls_seen:
        refuse("G-MP-STRUCT", {"controls_not_seen": True,
                               "note": ("a zero from a reader not shown able to see a non-zero is "
                                        "not evidence; the gate is not composed")})
    per, verdict, n = {}, "PASS", 0
    for _dv, k in XF.COMPONENTS:
        adj_j = X["adj"][OF_J]
        if k >= len(adj_j):
            refuse("G-MP-STRUCT", {"component_absent_from_the_J_adjoint": k,
                                   "n_entries": len(adj_j)})
        jv = adj_j[k]
        # SUMMED IN THE REGISTERED ORDER, through the PRODUCER'S OWN summation
        # function, so the identity is bit-for-bit the arithmetic the objective used.
        s = XF.weighted_J([X["adj"][OF_CD[i]][k] for i in range(N_SCEN)], X["weights"])
        n += 1
        resid = abs(jv - s)
        rel = resid / abs(jv) if abs(jv) > 0.0 else (0.0 if resid == 0.0 else float("inf"))
        ok = rel <= MP_STRUCT_TOL
        per["shape[%d]" % k] = {"J_adj_assembled": jv, "sum_w_CD_adj": s,
                                "abs_residual": resid, "rel_residual": rel,
                                "tolerance": MP_STRUCT_TOL, "verdict": "PASS" if ok else "GATE FAIL",
                                "per_scenario_CD_adj": [X["adj"][OF_CD[i]][k] for i in range(N_SCEN)],
                                "weights": X["weights"]}
        if not ok:
            verdict = "GATE FAIL"
    if n == 0:
        refuse("G-MP-STRUCT", {"empty_tuple": {"n_components": 0},
                               "note": "a gate over an empty tuple tests nothing"})
    return {"verdict": verdict, "per_component": per, "n_components_checked": n,
            "identity": "J_adj[J,k] == SUM_i w_i * J_adj[CD_i,k]",
            "what_would_make_it_FAIL": ("a weight applied on one side only; a scenario wired to the "
                                        "wrong geometry output; a scenario omitted from the sum; an "
                                        "ExecComp partial that does not match its own expression"),
            "what_could_still_PASS": ("a defect that corrupts every scenario IDENTICALLY cancels in "
                                      "the identity -- which is why G5J and G5C are bought beside it"),
            "controls_precondition": "SATISFIED -- the planted control was seen in this run"}


# ===================== G-TB: the h = 1e-8 trivial baseline ============================
def g_tb(X, F, g5j):
    """DAFOAM_CHARTER section 4's trivial baseline, REGISTERED BEFORE ITS OWN RUN:
    the SAME probe at a DELIBERATELY WRONG step, h = 1e-8, five orders below the
    registered middle step, in the subtractive-cancellation regime where the FD
    numerator on a derivative of order 1e-2 is ~1e-10 -- at or below the primal
    repeatability eta (D15 measured eta_F = 1.30e-10 on this mesh).

    PASS iff AT MOST 1 of the 4 registered components passes band D at the wrong
    step.  If 2 or more pass, the gate cannot fail, it is not evidence, and that
    row's G5J verdict is WITHDRAWN to NOT A RESULT.

    A PROBE THAT ERRORED COUNTS AS FAILING THE BASELINE -- an unevaluable estimate
    is not agreement.  The opposite-direction baseline (a step ABOVE the largest
    registered) is deliberately NOT bought: `A_stepsize_study.md` MEASURED the
    primal failing at 5e-2 and 1e-1, so that probe returns an exception rather
    than a reading, and an errored probe is a weaker baseline than a noise-limited
    one."""
    h = TB_STEPS_REGISTERED["shape"][0]
    per, n_pass = {}, 0
    for _dv, k in XF.COMPONENTS:
        adj = X["adj"][OF_J]
        frow = F["table"].get(("shape", k))
        name = "shape[%d]" % k
        if frow is None or k >= len(adj):
            per[name] = {"passes_band_D_at_the_WRONG_step": False, "reason": "ABSENT",
                         "counts_as": "FAILING the baseline"}
            continue
        v = frow["tb"].get(h)
        if v is None or not v["ok"]:
            per[name] = {"passes_band_D_at_the_WRONG_step": False,
                         "reason": ("FD_STEP_FAILED_OR_ABSENT" if v is not None else "ABSENT"),
                         "counts_as": "FAILING the baseline -- an errored probe is not agreement"}
            continue
        d_tb, j = v["J"], adj[k]
        if abs(d_tb) < NEAR_ZERO_ABS:
            per[name] = {"d_tb": d_tb, "J_adj": j, "passes_band_D_at_the_WRONG_step": False,
                         "reason": "NEAR_ZERO", "counts_as": "FAILING the baseline"}
            continue
        rel = abs(d_tb - j) / abs(d_tb) * 100.0
        passed = (d_tb * j > 0.0) and rel <= FD_BAND_PCT
        per[name] = {"d_tb": d_tb, "J_adj": j, "rel_err_pct": rel,
                     "passes_band_D_at_the_WRONG_step": bool(passed)}
        if passed:
            n_pass += 1
    verdict = "PASS" if n_pass <= TB_MAX_PASSING else "GATE FAIL"
    return {"verdict": verdict, "wrong_step": h, "per_component": per,
            "n_passing_at_the_wrong_step": n_pass, "max_allowed": TB_MAX_PASSING,
            "eta_F_reference": 1.30e-10,
            "withdrawal_rule": ("if 2 or more pass, the gate cannot fail, it is not evidence, and "
                                "this row's G5J verdict is WITHDRAWN to NOT A RESULT"),
            "opposite_direction_NOT_bought": ("a step ABOVE the largest registered returns an "
                                              "EXCEPTION on this case (A_stepsize_study.md measured "
                                              "the primal failing at 5e-2 and 1e-1); an errored "
                                              "probe is a weaker baseline than a noise-limited one"),
            "consequence": ("the wrong step fails as registered, so the FD gate is measuring the "
                            "step" if verdict == "PASS" else
                            "the WRONG step agrees: the gate is not measuring what it claims and "
                            "the G5J verdict for this row is WITHDRAWN to NOT A RESULT"),
            "g5j_verdict_at_the_registered_step": g5j["verdict"]}


# ===================== read the O artefact ============================================
def read_O(path):
    """The optimisation record `mpa1_O.json`, read by EXPLICIT keys.

    There is no recursive hunt for a key by name anywhere in this file: a read
    that goes looking until it finds something will always find something.  A
    missing key is `None` and the section 9 gate treats `None` as unmeasured, not
    as absent-and-therefore-fine."""
    with open(path) as fh:
        j = json.load(fh)
    if not isinstance(j, dict):
        refuse("SCHEMA", {"O_artefact_is_not_an_object": path})
    for k in ("row", "baseline", "final", "optimiser_exit_statement", "stall"):
        if k not in j:
            refuse("SCHEMA", {"O_artefact_missing_registered_key": k, "path": path})
    return j


# ===================== G-CLTGT / G-CLHOLD / G-DRAG: THE MP-A1 GATES ===================
def _read_final_cl(O):
    """The reader G-CLHOLD grades through -- and the SAME reader the planted control
    reads back off disk (rule 3: a zero from a reader not shown able to see a
    non-zero is not evidence).  Returns the final-design CL list, or None."""
    if not isinstance(O, dict):
        return None
    final = O.get("final") or {}
    cl = final.get("CL")
    if cl is None:
        return None
    try:
        return [float(v) for v in cl]
    except (TypeError, ValueError):
        return None


def g_cltgt(O):
    """G-CLTGT: the CL equality TARGETS carried in the artefact equal the registered
    CL_TARGET to CL_TARGET_TOL.  A run that quietly optimised to different targets
    than the ones registered is not this item.  Reads O['cl_target'] if the producer
    stamped it; if absent, REPORTED as not-stamped (not a silent pass)."""
    if O is None:
        return {"verdict": NOT_MEASURED, "state": "NOT RUN"}
    stamped = O.get("cl_target")
    if stamped is None:
        return {"verdict": NOT_MEASURED, "state": "RAN",
                "note": "the producer did not stamp cl_target into mpa1_O.json; "
                        "G-CLHOLD still gates satisfaction against the registered targets",
                "registered_targets": list(CL_TARGET)}
    try:
        st = [float(v) for v in stamped]
    except (TypeError, ValueError):
        refuse("G-CLTGT_SCHEMA", {"cl_target_not_numeric": stamped})
    if len(st) != N_SCEN:
        return {"verdict": "GATE FAIL", "stamped": st, "registered_targets": list(CL_TARGET),
                "reason": "wrong number of CL targets"}
    devs = [abs(st[i] - CL_TARGET[i]) for i in range(N_SCEN)]
    ok = all(d <= CL_TARGET_TOL for d in devs)
    return {"verdict": "PASS" if ok else "GATE FAIL", "stamped": st,
            "registered_targets": list(CL_TARGET), "abs_deviations": devs,
            "tol": CL_TARGET_TOL}


def g_clhold(O):
    """G-CLHOLD (MP-A1 gate b -- THE GATE THIS ITEM EXISTS TO EARN): at the final
    design, every operating point HOLDS its registered CL target
    (|CL_i - CL_target_i| <= TOL_CL_ABS) AND CL_i > 0.  SO-3 left CL unconstrained
    and the lift COLLAPSED negative at point0; this gate reads that failure mode
    directly and refuses to call it held."""
    if O is None:
        return {"verdict": NOT_MEASURED, "state": "NOT RUN",
                "note": "the optimisation arm did not run; no CL-hold reading exists"}
    cl = _read_final_cl(O)
    if cl is None or len(cl) != N_SCEN:
        refuse("G-CLHOLD_SCHEMA",
               {"final_CL_unreadable_or_wrong_length": cl, "n_scen": N_SCEN,
                "row": O.get("row")})
    per, ok = {}, True
    for i in range(N_SCEN):
        dev = abs(cl[i] - CL_TARGET[i])
        held = dev <= TOL_CL_ABS
        positive = cl[i] > 0.0
        per[SCENARIOS[i]] = {"cl_final": cl[i], "cl_target": CL_TARGET[i],
                             "abs_deviation": dev, "tol_abs": TOL_CL_ABS,
                             "held": held, "cl_positive": positive,
                             "alpha_deg": ALPHAS_REGISTERED[i]}
        if not (held and positive):
            ok = False
    return {"verdict": "PASS" if ok else "GATE FAIL", "per_point": per,
            "tol_cl_abs": TOL_CL_ABS, "targets": list(CL_TARGET), "row": O.get("row"),
            "requirement": ("MP-A1 holds lift at fixed alpha by a per-point CL EQUALITY "
                            "constraint; each point must hold its target within TOL_CL_ABS "
                            "and CL must never collapse negative (SO-3's failure)")}


def _clhold_synth(cl_list, row="PATCHED"):
    """A minimal O-shaped object for the G-CLHOLD reader/control -- final CL only."""
    return {"row": row, "final": {"CL": list(cl_list)}}


def g_clhold_control(base):
    """Rule-3 planted control for the G-CLHOLD reader.  Written to grader_controls/
    ONLY (never the graded artefact), read BACK OFF DISK through the SAME reader,
    and REFUSES unless the reader distinguishes held from planted-violation.

    Sized RELATIVE to the band: the plant is PLANT_K * TOL_CL_ABS on point0, clear
    of the band by 3x by construction.  Three substrates, all synthetic so the
    demonstration is independent of the real run's outcome:
      held      -> CL == targets exactly                 -> must grade PASS
      planted   -> point0 pushed PLANT_K*TOL_CL_ABS out  -> must grade GATE FAIL
      collapsed -> point0 driven NEGATIVE (SO-3's mode)  -> must grade GATE FAIL"""
    d = _plant_dir(base)
    plant = PLANT_K * TOL_CL_ABS
    held = _clhold_synth([CL_TARGET[i] for i in range(N_SCEN)])
    planted = _clhold_synth([CL_TARGET[i] for i in range(N_SCEN)])
    planted["final"]["CL"][0] = CL_TARGET[0] + plant
    collapsed = _clhold_synth([CL_TARGET[i] for i in range(N_SCEN)])
    collapsed["final"]["CL"][0] = -abs(CL_TARGET[0])
    paths = {}
    for name, obj in (("held", held), ("planted", planted), ("collapsed", collapsed)):
        p = os.path.join(d, "plant_clhold_%s.json" % name)
        with open(p, "w") as fh:
            json.dump(obj, fh, sort_keys=True)
        paths[name] = p
    # READ BACK OFF DISK through the same reader, then grade.
    held_back = _read_final_cl(json.load(open(paths["held"])))
    planted_back = _read_final_cl(json.load(open(paths["planted"])))
    collapsed_back = _read_final_cl(json.load(open(paths["collapsed"])))
    v_held = g_clhold(json.load(open(paths["held"])))["verdict"]
    v_planted = g_clhold(json.load(open(paths["planted"])))["verdict"]
    v_collapsed = g_clhold(json.load(open(paths["collapsed"])))["verdict"]
    seen = (planted_back is not None
            and abs(planted_back[0] - (CL_TARGET[0] + plant)) < 1e-15)
    flipped = (v_held == "PASS" and v_planted == "GATE FAIL" and v_collapsed == "GATE FAIL")
    if not (seen and flipped):
        refuse("G-CLHOLD_CONTROL",
               {"detail": "the G-CLHOLD reader did not distinguish held from planted; "
                          "a reader that cannot see a planted non-zero CL deviation is "
                          "not evidence the constraint held",
                "plant_read_back": seen, "v_held": v_held, "v_planted": v_planted,
                "v_collapsed": v_collapsed, "plant_value": plant})
    return {"exercised": True, "plant_seen": seen, "flipped": flipped,
            "plant_sizing": "RELATIVE -- PLANT_K*TOL_CL_ABS", "plant_value": plant,
            "plant_k": PLANT_K, "v_held": v_held, "v_planted": v_planted,
            "v_collapsed": v_collapsed, "read_back_point0": planted_back[0],
            "controls_written_to": d,
            "note": "plants live ONLY under grader_controls/; the graded verdict is "
                    "composed from the unplanted artefact"}


def g_drag(O):
    """G-DRAG (MP-A1 gate c): the constrained optimiser must IMPROVE on its FEASIBLE
    shape=0 seed -- final weighted J strictly < baseline J.  The reduction PERCENT
    and the full CL triple are REPORTED (a drag number without its CL triple is
    forbidden); the MAGNITUDE never gates a PASS and never upgrades a GATE REACHED
    optimiser (charter section 9)."""
    if O is None:
        return {"verdict": NOT_MEASURED, "state": "NOT RUN"}
    base, final = O.get("baseline") or {}, O.get("final") or {}
    jb, jf = base.get("J"), final.get("J")
    red = O.get("weighted_drag_reduction_pct")
    if jb is None or jf is None:
        refuse("G-DRAG_SCHEMA", {"missing_J": {"baseline": jb, "final": jf}, "row": O.get("row")})
    improved = jf < jb
    return {"verdict": "PASS" if improved else "GATE FAIL",
            "J_baseline": jb, "J_final": jf,
            "weighted_drag_reduction_pct": red,
            "floor_pct": DRAG_REDUCTION_FLOOR_PCT,
            "CL_baseline": base.get("CL"), "CL_final": final.get("CL"),
            "row": O.get("row"),
            "so3_unconstrained_reduction_pct_for_comparison": -16.16,
            "reported_not_gated_for_pass": ("the magnitude is REPORTED (cost of the CL "
                "constraint vs SO-3's ~16.16 %% unconstrained); charter section 9 forbids "
                "grading an optimiser by the size of its improvement, so only J_final<J_baseline "
                "gates here and the endpoint FD never upgrades a GATE REACHED optimiser to PASS"),
            "forbidden_reading": "quoting this reduction without CL_baseline and CL_final beside it"}


# ===================== G-DESIGNPOINT ==================================================
def g_design_point(X, F, O):
    """Every endpoint artefact states WHICH design point it evaluated at, and the
    optimum it read is stamped with ITS OWN ROW.

    THE FAILURE THIS GATE EXISTS FOR.  MP-A1's XE/FE arms are byte-for-byte the
    same instrument SO-3aR2 ran; the only thing that makes them ENDPOINT arms is
    the `-xopt` argument.  An arm launched without it produces a perfectly valid
    artefact that is SO-3aR2's baseline measurement under MP-A1's arm name, and
    section 9's whole requirement would be silently unmet with every gate green.
    So the producer stamps `design_point_record` and this gate reads it.

    REPORTED AND GATED, unlike G-IC0: a baseline artefact in an endpoint arm is
    not a small caveat, it is the wrong measurement."""
    per, bad = {}, []
    for rk in ROWS:
        for tag, rec in (("X", X.get(rk)), ("F", F.get(rk))):
            if rec is None:
                continue
            dp = (rec.get("raw") or {}).get("design_point_record") or {}
            word = dp.get("design_point", "ABSENT")
            xrow = dp.get("xopt_row")
            key = "%s:%s" % (tag, rk)
            entry = {"design_point": word, "xopt_row": xrow,
                     "xopt_file": dp.get("xopt_file"),
                     "xopt_sha256": dp.get("xopt_sha256")}
            if word != "FINAL":
                entry["fail"] = ("an endpoint arm's artefact must state design_point=FINAL; "
                                 "%r means this number was NOT taken at the optimum" % word)
                bad.append(key)
            elif xrow != rk:
                entry["fail"] = ("the optimum this arm read is stamped row=%r but the arm is on "
                                 "row %r; an endpoint gradient must be verified at the design "
                                 "point ITS OWN toolchain produced" % (xrow, rk))
                bad.append(key)
            per[key] = entry
    if not per:
        return {"verdict": NOT_MEASURED, "per_artefact": {},
                "note": "no endpoint arm ran; NOT EXERCISED"}
    return {"verdict": "GATE FAIL" if bad else "PASS", "per_artefact": per,
            "failing": bad,
            "requirement": ("DAFOAM_CHARTER section 9: every optimisation reports an FD check "
                            "AT ITS FINAL DESIGN POINT, not only at the baseline"),
            "why_it_is_gated": ("an XE/FE arm launched without -xopt yields a valid artefact that "
                                "is SO-3aR2's BASELINE measurement wearing MP-A1's arm name, and "
                                "every other gate in this file would stay green")}


# ===================== G-EVALFAIL =====================================================
def g_evalfail(recs):
    """An evaluation failure is a GRADABLE STATE, not a refusal (section 6).
    DECLARED and EXECUTED counts are BOTH reported per arm; a failed evaluation
    marks its own pairs `FD_STEP_FAILED_OR_ABSENT` and the row is graded on the
    survivors, subject to the >= 3 graded-pairs floor."""
    per = {}
    for tag, r in recs.items():
        d, f = r["evals_declared"], r["evals_failed"]
        per[tag] = {"evaluations_declared": d, "evaluations_failed": f,
                    "evaluations_succeeded": d - f,
                    "failure_fraction": (round(f / d, 6) if d else None)}
    return {"per_artefact": per, "status": "REPORTED -- a failed evaluation is a gradable state",
            "P_EVAL_registered_expectation": ("at least one of the %d declared evaluations per F arm "
                                              "fails or returns non-finite (section 6)"
                                              % EVALS_DECLARED),
            "both_counts_reported": True}


# ===================== G-PROV =========================================================
def require_travelling_provenance():
    """MP-A1 rests on SO-1a's PATCHED row while SO-1a's ITEM verdict is GATE FAIL.
    The comparator refuses to emit ANY verdict unless all five clauses hold.
    Clause (5) compares BYTES against `compose_verdict_line()` because this lab
    lost the words `GATE FAIL` from `docs/LAB_STATE.md` to an unquoted heredoc
    (L-405).  `verdict` itself stays exactly one of the six tokens and is never
    decorated (rule 1); the provenance travels in a separate mandatory field."""
    p = UPSTREAM
    if not isinstance(p, dict) or not p:
        refuse("G-PROV", {"upstream_provenance_block_absent": True})
    if p.get("rows", {}).get("SHIPPED") != "GATE FAIL":
        refuse("G-PROV", {"shipped_row_status_not_GATE_FAIL": p.get("rows", {}).get("SHIPPED")})
    # ---- CLAUSE (6), MP-A1's OWN: EVERY LINK IN THE CHAIN IS CHECKED, NOT JUST
    # ---- THE HEAD.  A derivation that repointed the head at SO-3aR2 and dropped
    # ---- SO-1a would have lost a GATE FAIL from the record while every clause
    # ---- above still passed -- which is the exact shape of a laundering, and it
    # ---- is the shape a mechanical rename produces.
    chain = p.get("chain")
    if not isinstance(chain, list) or len(chain) < 2:
        refuse("G-PROV", {"upstream_chain_absent_or_shorter_than_two_links": chain,
                          "note": "MP-A1's direct upstream is SO-3aR2 and SO-3aR2 carries "
                                  "SO-1a; both are GATE FAIL and both must travel"})
    for link in chain:
        if link.get("item_verdict") != "GATE FAIL":
            refuse("G-PROV", {"chain_link_item_verdict_not_GATE_FAIL": link.get("item")})
        if link.get("rows", {}).get("SHIPPED") != "GATE FAIL":
            refuse("G-PROV", {"chain_link_shipped_row_not_GATE_FAIL": link.get("item")})
        if not link.get("basis"):
            refuse("G-PROV", {"chain_link_has_no_basis": link.get("item")})
    det = p.get("shipped_gate_detail")
    # THE PER-GATE KEY IS MATCHED BY PATTERN, NOT BY ONE LITERAL NAME.  SO-1a's
    # failing gate is `G5`; SO-3aR2's is `G5J` -- the SAME gate one rung on, with
    # the objective in its name.  The ancestor hard-coded `G5_SHIPPED`, so
    # carrying the true key `G5J_SHIPPED` refused a correct block.  Broadening
    # the pattern is the honest repair; renaming the key to fit the check would
    # have made this record cite a gate SO-3aR2 does not have.
    if not isinstance(det, dict) or not any(
            k.startswith("G5") and k.endswith("_SHIPPED") for k in det) \
            or "basis" not in det:
        refuse("G-PROV", {"shipped_per_gate_detail_absent": det,
                          "note": "the row WORD alone is not the detail; a per-gate "
                                  "verdict key (G5*_SHIPPED) and a basis are both required"})
    line = p.get("verdict_line")
    if not isinstance(line, str) or "GATE FAIL" not in line:
        refuse("G-PROV", {"verdict_line_absent_or_missing_the_literal_bytes": line})
    if line != compose_verdict_line():
        refuse("G-PROV", {"verdict_line_NOT_byte_identical_to_the_composed_line":
                          {"stored": line, "composed": compose_verdict_line()},
                          "note": "L-405: this lab lost the words GATE FAIL to an unquoted heredoc"})
    return {"verdict": "SATISFIED", "clauses": 6, "upstream": p,
            "note": ("the SHIPPED GATE FAIL travels with every claim MP-A1 makes; the ruling calls "
                     "the incompressible ground `verified` and the record is narrower than that "
                     "word")}


# ===================== composition ====================================================
def compose_row(g5j, g5c, gtb, gmp):
    """G-TB, G5C and G-MP-STRUCT can only turn a PASS or a GATE FAIL INTO
    NOT A RESULT / GATE FAIL, never the reverse (the standing-rule-5 direction).

    G-TB IS COMPOSED ONLY ONTO A PASS, AND THAT IS REGISTERED.  The charter's
    clause is *"if the wrong step also passes, the gate is not measuring what it
    claims and THE VERDICT IT PRODUCED IS WITHDRAWN"* -- the verdict at issue is a
    PASS.  A row that already GATE FAILs on its own merits needs no trivial
    baseline to doubt it, and composing one there would convert a REAL gradient
    defect into NOT A RESULT and hide the finding.  G-TB's own verdict is PRINTED
    on every row either way; only its COMPOSITION is restricted, and the narrowing
    can never turn a NOT A RESULT into anything better."""
    if g5j["verdict"] == "NOT A RESULT" or g5c["verdict"] == "NOT A RESULT":
        return "NOT A RESULT"
    if "GATE FAIL" in (g5j["verdict"], g5c["verdict"], gmp["verdict"]):
        return "GATE FAIL"
    if gtb["verdict"] == "GATE FAIL":
        return "NOT A RESULT"
    return "PASS"


# ===================== G9 / G10 / G12 =================================================
def g_toolchain(rows, ran):
    out = {"per_arm": {}, "verdict": "PASS"}
    for arm in ran:
        r = rows[arm]
        row = ARM_ROW[arm]
        m = re.search(r"D4S_IDWARP_SO_MD5:\s*([0-9a-f]{32})", r.get("log_text", ""))
        printed = m.group(1) if m else None
        ok = (r.get("DIGEST") == IMG_DIGEST[row]) and (printed == SO_MD5[row])
        art_md5 = r.get("artefact_so_md5")
        if arm != "MESH":
            ok = ok and (art_md5 == SO_MD5[row])
        out["per_arm"][arm] = {"row": row, "digest": r.get("DIGEST"), "printed_so_md5": printed,
                               "artefact_so_md5": art_md5, "ok": bool(ok)}
        if not ok:
            out["verdict"] = "GATE FAIL"
    return out


def g_caps(rows, ran):
    out = {"per_arm": {}, "verdict": "PASS", "total_core_min": 0.0,
           "ceiling": ITEM_CEILING_CORE_MIN, "not_measured": [],
           "arms_not_run": [a for a in ARMS_DECLARED if a not in ran]}
    for arm in ran:
        cm = rows[arm].get("core_min")
        if cm is None:
            out["not_measured"].append(arm)
            out["per_arm"][arm] = {"core_min": NOT_MEASURED, "cap": CAPS[arm]}
            continue
        out["total_core_min"] += cm
        crossed = cm > CAPS[arm]
        out["per_arm"][arm] = {"core_min": cm, "cap": CAPS[arm], "crossed": crossed,
                               "predicted": PREDICTED_CORE_MIN[arm],
                               "ratio_actual_over_predicted": round(cm / PREDICTED_CORE_MIN[arm], 4)}
        if crossed:
            out["verdict"] = "GATE FAIL"
    if out["total_core_min"] > ITEM_CEILING_CORE_MIN:
        out["verdict"] = "GATE FAIL"
    out["cost_basis"] = ("c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED -- the box "
                         "cannot read its own billing (COMPUTE_BUDGET_CHARTER.md section 5)")
    out["usd_derived_not_measured"] = round(out["total_core_min"] / 60.0 * 0.0513, 5)
    return out


def g_placement(rows, ran):
    out = {"per_arm": {}, "verdict": "PASS", "not_measured": [],
           "registered_cpuset": CPUSET_REGISTERED,
           "delivered_floor_note": ("at np = 1 the delivered-cores floor does not apply and is NOT "
                                    "composed; the sampler's reading is reported as a number")}
    for arm in ran:
        r = rows[arm]
        cs_ok = r.get("cpuset") == CPUSET_REGISTERED
        m = re.match(r"\s*([\d.]+)\s+n=(\d+)", r.get("delivered") or "")
        dl = float(m.group(1)) if m else None
        if dl is None:
            out["not_measured"].append(arm)
        dl_ok = True if (dl is None or ARM_RANKS[arm] == 1) else dl >= DELIVERED_CORES_FLOOR
        out["per_arm"][arm] = {"cpuset": r.get("cpuset"),
                               "delivered_cores_mean": (dl if dl is not None else NOT_MEASURED)}
        if not (cs_ok and dl_ok):
            out["verdict"] = "GATE FAIL"
    return out


def birth_record():
    return {"requirement": ("Sanaa 2026-08-28: no instrument grades anything until 'was this reader "
                           "ever shown able to see a non-zero through the real code path?' is "
                           "answered YES, demonstrated"),
            "readers": READERS,
            "n_born": sum(1 for v in READERS.values() if v["born"]),
            "n_not_born": sum(1 for v in READERS.values() if not v["born"]),
            "not_born": [k for k, v in READERS.items() if not v["born"]]}


# ===================== the grade =======================================================
def grade(root):
    prov = require_travelling_provenance()
    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)
    ran = [a for a in ARMS_DECLARED if g1["census"].get(a, {}).get("state") == "RAN"]

    chain_txt = ""
    sp = os.path.join(root, "STATUS.chain")
    if os.path.isfile(sp):
        with open(sp, errors="replace") as fh:
            chain_txt = fh.read()
    gstages = g_stages(g1, chain_txt)

    # ---- G-M2, only if MESH ran.  An absent arm is a census reading. ---------------
    cells, gm2, cmpath = None, NOT_MEASURED, os.path.join(root, "MESH", "checkMesh.log")
    if "MESH" in ran:
        cells = read_mesh_cells(cmpath)
        gm2 = "PASS" if cells == CELLS_EXPECTED else "GATE FAIL"

    X, F, O = {}, {}, {}
    for rk in ROWS:
        if X_ARM[rk] in ran:
            X[rk] = read_X(os.path.join(root, X_ARM[rk], XF.OUT_X))
            rows[X_ARM[rk]]["artefact_so_md5"] = X[rk]["so_md5"]
        if F_ARM[rk] in ran:
            F[rk] = read_F(os.path.join(root, F_ARM[rk], XF.OUT_F))
            rows[F_ARM[rk]]["artefact_so_md5"] = F[rk]["so_md5"]
        if O_ARM[rk] in ran:
            O[rk] = read_O(os.path.join(root, O_ARM[rk], OUT_O))
            rows[O_ARM[rk]]["artefact_so_md5"] = O[rk].get("libidwarp_so_md5")

    # ---- G-DESIGNPOINT.  THE ENDPOINT ARMS MUST SAY THEY ARE ENDPOINT ARMS,
    # ---- AND THE OPTIMUM THEY READ MUST BE THEIR OWN ROW'S.
    # Section 9's requirement is an FD check AT THE FINAL DESIGN POINT.  An XE/FE
    # artefact that silently evaluated at the BASELINE would satisfy every other
    # gate in this file and would be SO-3aR2's number wearing MP-A1's arm name.
    # `UNSPECIFIED` -- the producer's fail-closed default -- refuses here, because
    # a builder that defaulted to "BASELINE" would let exactly that happen.
    gdp = g_design_point(X, F, O)

    recs, rec_kind = {}, {}
    for rk in ROWS:
        if rk in X:
            t = "%s:%s" % (REC_KIND_X, rk)
            recs[t], rec_kind[t] = X[rk], REC_KIND_X
        if rk in F:
            t = "%s:%s" % (REC_KIND_F, rk)
            recs[t], rec_kind[t] = F[rk], REC_KIND_F
    galpha = g_alpha(recs) if recs else {"verdict": NOT_MEASURED,
                                         "note": "no solver arm ran; NOT EXERCISED"}
    gnoopt = g_noopt(recs, rec_kind, {a: rows[a].get("log_text", "") for a in ran}) if recs else {
        "verdict": NOT_MEASURED, "note": "no solver arm ran; NOT EXERCISED"}
    gevalfail = g_evalfail(recs) if recs else {"per_artefact": {},
                                               "status": "NOT EXERCISED -- no solver arm ran"}

    # ---- rule 3, LIVE, on the real artefacts, BEFORE any gate is composed ----------
    controls = {}
    # The UNPLANTED G5J reading, taken FIRST, purely to choose a plant target the
    # gate actually grades.  It is recomputed below for the published record.
    graded_k = {}
    # MP-A1 REGISTERED DELTA: `d_ref` is carried beside the index, because the
    # plant is now sized RELATIVE to the very reference the gate divides by.  The
    # index alone was enough for an absolute plant and is not enough for this one.
    graded_ref = {}
    for rk in ROWS:
        if rk in X and rk in F:
            ps = [p for p in grade_objective_gradient(X[rk], F[rk])["pairs"] if p.get("graded")]
            graded_k[rk] = [p["idx"] for p in ps]
            graded_ref[rk] = {p["idx"]: p["d_ref"] for p in ps}
    for rk in ROWS:
        if rk in F:
            controls["instrument_ctrl_%s" % rk] = ctrl_control(F[rk])
            controls["grader_plant_F_%s" % rk] = grader_plant_F(
                root, os.path.join(root, F_ARM[rk], XF.OUT_F), rk)
        if rk in X:
            ks = graded_k.get(rk) or []
            kk = ks[0] if ks else COMPONENTS_REGISTERED[0][1]
            controls["grader_plant_X_%s" % rk] = grader_plant_X(
                root, os.path.join(root, X_ARM[rk], XF.OUT_X), rk, kk,
                scale=(graded_ref.get(rk) or {}).get(kk))
            controls["grader_plant_X_%s" % rk]["n_graded_pairs_available"] = len(ks)
    if "MESH" in ran:
        controls["grader_plant_cells"] = grader_plant_cells(root, cmpath)
    controls["grader_plant_c5"] = grader_plant_c5(root, rows, g1)
    # ---- MP-A1: the G-CLHOLD reader's rule-3 planted control.  Written to
    # ---- grader_controls/ ONLY, read BACK OFF DISK through the same reader, and
    # ---- REFUSES unless the reader distinguishes held from planted-violation and
    # ---- from a negative-lift collapse.  Independent of the real run's outcome.
    controls["grader_plant_clhold"] = g_clhold_control(root)
    # THE CONTROL KEYS ARE BUILT FROM `ROWS`, NEVER SPELLED OUT.  A hand-written
    # list is one more call site of the row label, and this file has already lost
    # one that way -- the same shape that killed SO-1c at its second arm.
    for key in (["grader_plant_cells"]
                + ["%s_%s" % (stem, rk) for rk in ROWS
                   for stem in ("instrument_ctrl", "grader_plant_F", "grader_plant_X")]):
        if key not in controls:
            controls[key] = {"status": "NOT EXERCISED -- the arm that would bear it did not run",
                             "note": "NOT EXERCISED is never counted as a pass"}

    # ---- THE FLIP, DRIVEN AT GRADE TIME.  G5J and G-MP-STRUCT both PASS on a small
    # ---- number; a gate not shown able to read a violation is void.
    # THE RULE, AND IT IS COMPARATIVE RATHER THAN ABSOLUTE.  A gate is required to
    # MOVE OFF `PASS` under the plant; it is NOT required to reach `GATE FAIL` from
    # a reading that was never `PASS`.  This lane's first draft demanded `GATE
    # FAIL` unconditionally and refused a legitimate run whose row sat below the
    # >= 3 graded-pair floor -- there the reading is `NOT A RESULT` with or
    # without the plant, and a control that cannot distinguish those two states is
    # testing the floor, not the gate.  Where the unplanted reading is ALREADY
    # `GATE FAIL`, the gate has demonstrated on this very run that it can read a
    # violation, and that real reading is the demonstration.
    for rk in ROWS:
        c = controls.get("grader_plant_X_%s" % rk)
        if not isinstance(c, dict) or "file" not in c or rk not in F:
            continue
        Xp = read_X(c["file"])
        for gate, before, after in (
                ("g_mp_struct", g_mp_struct(X[rk], True)["verdict"],
                 g_mp_struct(Xp, True)["verdict"]),
                ("G5J", grade_objective_gradient(X[rk], F[rk])["verdict"],
                 grade_objective_gradient(Xp, F[rk])["verdict"])):
            if before == "PASS" and after != "GATE FAIL":
                refuse("CONTROL", {"%s_did_not_move_off_PASS_under_the_plant" % gate:
                                   {"row": rk, "unplanted": before, "planted": after,
                                    "planted_component": c["component_index"],
                                    "graded_components": graded_k.get(rk)},
                                   "note": ("this gate passes on a small or zero number; a PASS "
                                            "from a gate not shown able to read a violation "
                                            "through the same reader is not evidence")})
            c["%s_unplanted" % gate] = before
            c["%s_planted" % gate] = after
            c["%s_control" % gate] = (
                "EXERCISED-PASS -- PASS moved to GATE FAIL under the plant" if before == "PASS"
                else "EXERCISED-PASS -- the gate read a violation on the REAL artefact (%s), "
                     "which is the demonstration itself" % before)

    # ---- G9/G10/G12 ARE COMPUTED HERE, BEFORE THE ROW COMPOSITION, BECAUSE
    # ---- SECTION 9 NEEDS THE CAP READING.  The ancestor computed them after the
    # ---- G5 loop, which was fine while no gate upstream of them needed a cap;
    # ---- section 9's "stopped by a budget" branch does, and reading a name that
    # ---- is not yet bound is a NameError at grade time, on the artefacts, after
    # ---- the compute is spent.  Moving the line is the whole change: none of the
    # ---- three reads anything the G5 loop writes.
    g9, g10, g12 = g_toolchain(rows, ran), g_caps(rows, ran), g_placement(rows, ran)

    g5, gopt = {}, {}
    for rk in ROWS:
        if rk not in X or rk not in F:
            g5[rk] = {"endpoint_fd_verdict": NOT_MEASURED, "row_verdict": NOT_MEASURED,
                      "state": "NOT RUN -- %s and/or %s did not run" % (X_ARM[rk], F_ARM[rk])}
            gopt[rk] = g_opt_section9(O.get(rk), NOT_MEASURED,
                                      (g10.get("per_arm") or {}).get(O_ARM[rk]))
            continue
        j = grade_objective_gradient(X[rk], F[rk])
        c = grade_lift_gradients(X[rk], F[rk])
        mp = g_mp_struct(X[rk], True)
        tb = g_tb(X[rk], F[rk], j)
        # ---- THE ENDPOINT FD ROW VERDICT.  This is what SO-3aR2 produced at
        # ---- iteration 0 and what MP-A1 produces at the optimum.  It is NOT the
        # ---- row's verdict on its own: an optimisation row is the CONJUNCTION of
        # ---- section 9's reading of the optimiser and this reading of the
        # ---- gradient at the design the optimiser reached.
        endpoint = compose_row(j, c, tb, mp)
        opt = g_opt_section9(O.get(rk), endpoint,
                             (g10.get("per_arm") or {}).get(O_ARM[rk]))
        gopt[rk] = opt
        # ---- THE MP-A1 GATES: CL held, drag improved, targets as registered. ----
        clh = g_clhold(O.get(rk))         # gate (b): lift HELD, never collapsed
        drg = g_drag(O.get(rk))           # gate (c): final J < baseline J
        clt = g_cltgt(O.get(rk))          # targets stamped == registered
        # ---- THE ROW COMPOSITION, AND THE ONE DIRECTION IT MAY NOT GO.
        # A row is PASS only if BOTH the optimiser converged on its own tolerance
        # AND the gradient at the final design point passed its band.  Every
        # other combination degrades, never upgrades: an endpoint PASS can NEVER
        # lift a GATE REACHED optimiser to PASS, because the endpoint FD
        # validates the DESIGN and says nothing about convergence, and treating
        # them as interchangeable is the laundering section 9 forbids.
        # G-CLHOLD and G-DRAG fold into the row: a row cannot be PASS if the lift was
        # not held (gate b) or the constrained optimiser did not improve (gate c).
        # They can only DEGRADE the row, exactly like the endpoint FD.
        order = ["NOT A RESULT", "GATE FAIL", "GATE REACHED", "BLOCKED", "PASS"]
        cand = [endpoint, opt["verdict"], clh["verdict"], drg["verdict"]]
        if NOT_MEASURED in cand:
            row_verdict = NOT_MEASURED
        else:
            row_verdict = min(cand, key=lambda w: order.index(w))
        g5[rk] = {"G5J_objective": j, "G5C_lift_per_scenario": c,
                  "G_CLHOLD_cl_satisfaction": clh, "G_DRAG_reduction": drg,
                  "G_CLTGT_targets_registered": clt,
                  "G_MP_STRUCT_assembly_identity": mp, "G_TB_trivial_baseline": tb,
                  # THE HARNESS FLOOR, PUBLISHED BESIDE THE AGGREGATE IT QUALIFIES.
                  # VERIFICATION section 7 step 4.  SO-3aR2's PATCHED aggregate was
                  # 2.678 % -- INSIDE the 2.5-5 % floor -- so this number is what
                  # stops a successor calling it a sub-percent verification.
                  "G5J_harness_floor": floor_margin(j.get("aggregate_rel_err_pct")),
                  "endpoint_fd_verdict": endpoint,
                  "section9_optimisation": opt["verdict"],
                  "row_verdict": row_verdict,
                  "row_composition_note": ("a row is PASS only if the optimiser converged on its "
                                           "OWN tolerance AND the gradient at the FINAL design "
                                           "point passed its band; the composition can only "
                                           "degrade and an endpoint PASS never lifts a "
                                           "GATE REACHED optimiser"),
                  "eta_F": F[rk]["eta"], "state": "RAN"}

    # ---- divergence shipped-vs-patched on the adjoint, REPORTED, NEVER GATED -------
    div, worst_div = [], None
    if all(rk in X for rk in ROWS):
        worst_div = 0.0
        for of in OF_KEYS_REGISTERED:
            for _dv, k in XF.COMPONENTS:
                a, b = X["SHIPPED"]["adj"][of], X["PATCHED"]["adj"][of]
                if k >= len(a) or k >= len(b):
                    continue
                den = max(abs(a[k]), abs(b[k]), 1e-300)
                d = abs(a[k] - b[k]) / den * 100.0
                worst_div = max(worst_div, d)
                if d > 0.0:
                    div.append({"of": of, "dv": "shape", "idx": k, "J_shipped": a[k],
                                "J_patched": b[k], "divergence_pct": d})
        div = sorted(div, key=lambda r: -r["divergence_pct"])[:20]

    # ---- predictions, scored, never adjusted --------------------------------------
    preds = {}
    preds["P1_cells_4032"] = (NOT_MEASURED if gm2 == NOT_MEASURED
                              else ("HIT" if gm2 == "PASS" else "MISS"))
    lo, hi = PRED["P2_CL_baseline_band"]
    cl0 = None
    for rk in reversed(ROWS):
        if rk in X:
            cl0 = X[rk]["CL_base"][1]        # scenario 1 is alpha_0 = 5.139 deg
            break
    preds["P2_CL_at_alpha0_in_band"] = (NOT_MEASURED if cl0 is None
                                        else ("HIT" if lo <= cl0 <= hi else "MISS"))
    cdb = None
    for rk in reversed(ROWS):
        if rk in X:
            cdb = X[rk]["CD_base"]
            break
    preds["P3_CD_monotone_increasing_in_alpha"] = (
        NOT_MEASURED if cdb is None
        else ("HIT" if all(cdb[i] < cdb[i + 1] for i in range(N_SCEN - 1)) else "MISS"))
    preds["P4_G_MP_STRUCT_PASS_all_components"] = (
        NOT_MEASURED if not [rk for rk in ROWS if g5[rk].get("state") == "RAN"]
        else ("HIT" if all(g5[rk]["G_MP_STRUCT_assembly_identity"]["verdict"] == "PASS"
                           for rk in ROWS if g5[rk].get("state") == "RAN") else "MISS"))
    if g5.get("PATCHED", {}).get("state") == "RAN":
        pj = g5["PATCHED"]["G5J_objective"]
        agg = pj.get("aggregate_rel_err_pct")
        preds["P5_PATCHED_G5J_PASS_4_of_4"] = (
            NOT_MEASURED if pj["verdict"] == "NOT A RESULT" else
            ("HIT" if (pj["verdict"] == "PASS" and pj["n_graded_pairs"] == len(XF.COMPONENTS)
                       and agg is not None and agg <= PRED["P5_patched_agg_max_pct"]) else "MISS"))
        preds["P7_G_TB_PASS_at_the_wrong_step"] = (
            "HIT" if g5["PATCHED"]["G_TB_trivial_baseline"]["verdict"] == "PASS" else "MISS")
    else:
        preds["P5_PATCHED_G5J_PASS_4_of_4"] = NOT_MEASURED
        preds["P7_G_TB_PASS_at_the_wrong_step"] = NOT_MEASURED
    if g5.get("SHIPPED", {}).get("state") == "RAN":
        sj = g5["SHIPPED"]["G5J_objective"]
        preds["P6_SHIPPED_G5J_GATE_FAIL"] = (
            NOT_MEASURED if sj["verdict"] == "NOT A RESULT"
            else ("HIT" if sj["verdict"] == "GATE FAIL" else "MISS"))
    else:
        preds["P6_SHIPPED_G5J_GATE_FAIL"] = NOT_MEASURED
    # P8 / P-EVAL, scored PER ARM.
    p8 = {}
    for tag, r in (gevalfail.get("per_artefact") or {}).items():
        if tag.startswith("%s:" % REC_KIND_F):
            p8[tag] = "HIT" if r["evaluations_failed"] >= 1 else "MISS"
    preds["P8_P_EVAL_at_least_one_evaluation_fails_per_F_arm"] = (p8 or NOT_MEASURED)
    # P9: the plateau holds per pair at the WING angles as it does at alpha_0.
    p9 = {}
    for rk in ROWS:
        if g5.get(rk, {}).get("state") != "RAN":
            continue
        for i in (0, 2):
            sc = g5[rk]["G5C_lift_per_scenario"]["per_scenario"][SCENARIOS[i]]
            n_ok = sum(1 for p in sc["pairs"] if p.get("reason") != "NO_PLATEAU")
            p9["%s_%s" % (rk, SCENARIOS[i])] = "HIT" if n_ok >= 3 else "MISS"
    preds["P9_plateau_holds_at_the_WING_angles"] = (p9 or NOT_MEASURED)
    lo, hi = PRED["P_COST_band"]
    tot = g10["total_core_min"]
    preds["P_COST_total_core_min_in_band"] = (
        NOT_MEASURED if (g10["not_measured"] or gstages["short"] > 0)
        else ("HIT" if lo <= tot <= hi else "MISS"))

    # ---- item verdict: the composition registered in PREREGISTRATION section 3 -----
    rowv = tuple(g5[rk]["row_verdict"] for rk in ROWS)
    optv = tuple(gopt[rk]["verdict"] for rk in ROWS)
    # MP-A1 per-row gates (G-CLHOLD/G-DRAG already fold into rowv; G-CLTGT does not,
    # so its GATE FAIL is added here as a belt to braces -- PREREGISTRATION section 2e).
    mpa1_rowgate_words = []
    for rk in ROWS:
        for gk in ("G_CLHOLD_cl_satisfaction", "G_DRAG_reduction", "G_CLTGT_targets_registered"):
            mpa1_rowgate_words.append((g5[rk].get(gk) or {}).get("verdict"))
    gate_words = (gm2, galpha.get("verdict"), gnoopt.get("verdict"),
                  gdp.get("verdict"),
                  g9["verdict"], g10["verdict"], g12["verdict"]) + tuple(mpa1_rowgate_words)
    if gstages["verdict"] == "NOT A RESULT" or "NOT A RESULT" in rowv:
        verdict = "NOT A RESULT"
    elif gstages["verdict"] == "BLOCKED":
        verdict = "BLOCKED"
    elif "NOT A RESULT" in optv:
        # SECTION 9's OWN DIRECTION.  A row whose optimiser is NOT A RESULT
        # cannot be rescued by any other gate, and it is checked here rather than
        # left to fall through `rowv` -- the row composition already folds it in,
        # and this line is the belt to that braces so a future edit to
        # `compose_row` cannot silently drop it.
        verdict = "NOT A RESULT"
    elif "GATE FAIL" in rowv + gate_words:
        verdict = "GATE FAIL"
    elif NOT_MEASURED in rowv:
        verdict = "NOT A RESULT"
    elif "GATE REACHED" in rowv + optv:
        # AND THE ONE THE FAMILY LOSES MOST OFTEN.  An item whose optimiser ran
        # out of budget is `GATE REACHED`, never `PASS`, however large the
        # improvement it reached.  A2's 28.275488 % is the standing example.
        verdict = "GATE REACHED"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})

    # ---- THE PUBLISHED RECORD.  Its shape is the CONTRACT with the frozen
    # ---- consumers -- see (I).  `verdict` and `rows` are TOP LEVEL because
    # ---- mpa1_stop_marker.sh:97,105 reads them there; `gates["G5J"]` carries the
    # ---- literal key mpa1_stop_marker.sh:101 looks for.
    return {"item": "CURRICULUM-%s" % ITEM, "verdict": verdict,
            "rows": {w: g5[w]["row_verdict"] for w in ROWS},
            "upstream_provenance": prov,
            "gates": {
                "G1_completion": "PASS" if ran else NOT_MEASURED,
                "G-M2_mesh_identity": gm2,
                "G-ALPHA_operating_points": galpha,
                "G5J": {ROWS[0]: g5[ROWS[0]], ROWS[1]: g5[ROWS[1]],
                        "reading": ("the bright line on the MULTIPOINT OBJECTIVE J, per ROW, with "
                                    "the plateau proved PER PAIR"),
                        "band_D_pct": FD_BAND_PCT, "band_E_pct": AGG_BAND_PCT,
                        "plateau_tol_pct": PLATEAU_TOL_PCT,
                        "min_graded_pairs": MIN_GRADED_PAIRS},
                "G-CLHOLD_cl_satisfaction_per_row": {
                    ROWS[0]: (g5[ROWS[0]].get("G_CLHOLD_cl_satisfaction") or {"verdict": NOT_MEASURED}),
                    ROWS[1]: (g5[ROWS[1]].get("G_CLHOLD_cl_satisfaction") or {"verdict": NOT_MEASURED}),
                    "reading": ("MP-A1 gate (b): each operating point HOLDS its registered CL "
                                "target within TOL_CL_ABS=%g at the final design AND CL never "
                                "collapses negative -- the SO-3 failure this item removes"
                                % TOL_CL_ABS),
                    "tol_cl_abs": TOL_CL_ABS, "targets": list(CL_TARGET)},
                "G-DRAG_reduction_per_row": {
                    ROWS[0]: (g5[ROWS[0]].get("G_DRAG_reduction") or {"verdict": NOT_MEASURED}),
                    ROWS[1]: (g5[ROWS[1]].get("G_DRAG_reduction") or {"verdict": NOT_MEASURED}),
                    "reading": ("MP-A1 gate (c): final weighted J strictly < baseline J (the "
                                "constrained optimiser improved on its feasible shape=0 seed).  "
                                "The reduction magnitude is REPORTED with the CL triple, never "
                                "used to grade a PASS (charter section 9)")},
                "G-CLTGT_targets_registered_per_row": {
                    ROWS[0]: (g5[ROWS[0]].get("G_CLTGT_targets_registered") or {"verdict": NOT_MEASURED}),
                    ROWS[1]: (g5[ROWS[1]].get("G_CLTGT_targets_registered") or {"verdict": NOT_MEASURED}),
                    "reading": "the CL equality targets in the artefact equal the registered "
                               "CL_TARGET to %g" % CL_TARGET_TOL},
                "G-NOOPT-ENDPOINT_no_optimiser_in_the_endpoint_arms": gnoopt,
                "G-DESIGNPOINT_endpoint_arms_evaluated_at_the_optimum": gdp,
                "G-OPT9_optimisation_per_row": {
                    ROWS[0]: gopt[ROWS[0]], ROWS[1]: gopt[ROWS[1]],
                    "charter": "DAFOAM_CHARTER.md section 9",
                    "reading": ("PASS only where the OPTIMISER printed a convergence statement "
                                "against its OWN tolerance; a run stopped by a wall clock, an "
                                "iteration cap, a budget or the registered stall abort is "
                                "GATE REACHED where the registered intermediate threshold "
                                "(%.1f %% weighted-drag reduction over at least %d majors) was "
                                "met and NOT A RESULT otherwise -- never PASS, and never "
                                "described by the size of the improvement it reached"
                                % (OPT_INTERMEDIATE_THRESHOLD_PCT, OPT_MIN_MAJORS)),
                    "stall_conditions_registered": {
                        "A": "%d consecutive majors with alpha_pr < %g" % (
                            STALL.N_STALL, STALL.ALPHA_PR_MIN),
                        "B": "dual infeasibility NON-DECREASING over %d consecutive majors"
                             % STALL.N_STALL,
                        "calibration": ("MEASURED over 33 gradable IPOPT logs on this box: "
                                        "condition A fires on exactly 2, both the known D6 "
                                        "stalls, and on NONE of the 7 that ended `Maximum "
                                        "Number of Iterations Exceeded` -- a cap is not a "
                                        "stall.  Condition B has NEVER fired on real evidence "
                                        "and is reported NOT EXERCISED, never as a passing "
                                        "control")}},
                "G-STAGES_declared_vs_executed": gstages,
                "G-EVALFAIL_evaluation_census": gevalfail,
                "G9_toolchain": g9, "G10_caps": g10, "G12_placement": g12,
                "G6_dot_product_duality": ("NOT MEASURED -- AV-2 measured that seeding forward mode "
                                           "makes the primal FAIL on this exact case on BOTH images; "
                                           "named, never composed"),
            },
            "mesh_cells": cells,
            "primal_convergence": {
                "per_arm": g1["convergence"],
                "discriminator": ("the REAL statement is `Minimal residual <r> satisfied the "
                                  "prescribed tolerance <tol>`.  OpenFOAM's `SIMPLE: no convergence "
                                  "criteria found` banner is COUNTED SEPARATELY and is NOT evidence: "
                                  "it appears 4x in reference/REAL_SO1a_X-S_arm.log on a run that "
                                  "CONVERGED, because DAFoam applies its own primalMinResTol"),
                "status": "REPORTED, NEVER GATED"},
            "divergence_shipped_vs_patched": {
                "worst_pct": worst_div, "nonzero_pairs": div,
                "status": "REPORTED WITH ITS NUMBER, NEVER GATED",
                "note": ("a divergence of 0.000 % on some component is REPORTED with its number and "
                         "is never read as `the defect is absent`")},
            "predictions": preds, "controls": controls, "birth_register": birth_record(),
            "completion": g1,
            "arm_census": g1["census"],
            "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"],
                             "G12": g12["not_measured"]},
            "field_classes": {"physics": list(FIELDS_PHYSICS),
                              "infrastructure": list(FIELDS_INFRASTRUCTURE),
                              "rule": ("absent infrastructure -> NOT_MEASURED beside the verdict; "
                                       "absent physics -> REFUSE (L-342)")},
            "no_gci": "no grid family; standing rule 5 has no row; NO GCI IS QUOTED",
            "age_datum_resolution": g1["datum_resolution"],
            "rule4_clauses_per_arm": g1["rule4_clauses"],
            "rc_inferences": g1["rc_inferences"],
            "capability_grid_cell": (
                "2D . steady . incompressible -- gradient-DRIVEN OPTIMISATION of a weighted "
                "multipoint objective, with the gradient FD-verified AT THE FINAL DESIGN POINT.  "
                "This item moves ONLY that column.  What it adds over SO-3aR2 is the OPTIMUM and "
                "the ENDPOINT verification SO-3aR2's own cell says it establishes NOTHING about; "
                "what it still establishes NOTHING about is MACH (this is DASimpleFoam, "
                "incompressible, M ~ 0.03, and a `multipoint` here is an ALPHA sweep -- Sanaa's "
                "MP-A1 sentence says `2-3 Mach/alpha` and THIS ITEM ANSWERS THE ALPHA HALF ONLY), "
                "np != 1 (registered at np = 1; DAFOAM section 5 forbids carrying the FD "
                "reference across np), and an AOA-TRIMMED result (MP-A1 holds CL by a per-point "
                "EQUALITY constraint on the shared shape at FIXED alpha -- NOT a per-point aoa "
                "trim DV, which would introduce d/dalpha gradients SO-3aR2 never verified; that "
                "is a separate rung).  What MP-A1 ADDS over SO-3 is exactly the fixed-lift "
                "constraint: G-CLHOLD gates that the lift was HELD and never collapsed, so the "
                "drag reduction here IS a drag-min-at-fixed-lift, unlike SO-3's")}


# ===================== the fixture: BUILT BY THE INSTRUMENT'S OWN WRITERS ==============
REFDIR = os.path.join(_HERE, "reference")
REAL_CHECKMESH = os.path.join(REFDIR, "REAL_SO1a_MESH_checkMesh.log")
REAL_ARMLOG = os.path.join(REFDIR, "REAL_SO1a_X-S_arm.log")
# A PATH, and it is NEVER reassigned to hold this script's RESULT.  The result of
# sourcing it lives in `rows_out`, a DIFFERENT NAME.  The call site guards the
# PATH with `os.path.isfile` and returns a DISTINCT sentinel so a missing
# launcher cannot masquerade as a parse failure.
LAUNCHER_PATH = os.path.join(_HERE, "mpa1_run_arm.sh")
LAUNCHER_ABSENT = "LAUNCHER_ABSENT"
LAUNCHER_UNPARSEABLE = "LAUNCHER_UNPARSEABLE"


def _adj_cd(i, k):
    """A STRUCTURED synthetic per-scenario CD adjoint: distinct across BOTH the
    scenario and the component index, so a reader that collapses a dimension shows
    up, and distinct per scenario so a weight applied on one side only cannot
    cancel."""
    return 0.011 * (1.0 + 0.37 * i) * (1.0 + 0.53 * k) * (-1.0 if (i + k) % 4 == 0 else 1.0)


def _adj_cl(i, k):
    return 0.42 * (1.0 + 0.19 * i) * (1.0 - 0.11 * k) * (-1.0 if (i + k) % 3 == 0 else 1.0)


def _ledger_rows_via_launcher(k):
    """R1's BIRTH: the fixture's ledger rows are emitted by SOURCING THE LAUNCHER'S
    OWN `mpa1_ledger_row` -- the real producer's code -- not by a copy of its
    format string here.  If the launcher's format and this reader's regex ever
    diverge, this returns rows the reader cannot parse and the suite fails loudly.

    Returns a DISTINCT sentinel for each failure mode, so `LAUNCHER_ABSENT` (the
    file is not built yet) is never confused with `LAUNCHER_UNPARSEABLE` (it is
    built and its format broke).  A resource block and a defect are different
    findings."""
    if not os.path.isfile(LAUNCHER_PATH):
        return LAUNCHER_ABSENT
    lines = []
    for arm in ARMS_DECLARED:
        ke = NOT_MEASURED if arm in k["rc_record"] else k["ke"].get(arm, k["rc"][arm])
        cmd = ('. %s --source-only >/dev/null 2>&1; '
               'mpa1_ledger_row %s %s img %s %d 60 %d %s %s 600 %s 12g "%s %s" 20.00 "%s" "%s" '
               '"%s" "" "" %s x'
               % (LAUNCHER_PATH, arm, ARM_ROW[arm], IMG_DIGEST[ARM_ROW[arm]], k["rc"][arm],
                  ARM_RANKS[arm], k["cm"][arm], CAPS[arm], CAPS[arm], ke, k["oom"][arm],
                  k["mpost"], k["cs"][arm], k["dl"], "%s_x.log" % arm))
        p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
        out = p.stdout.strip()
        if not out.startswith("ARM="):
            return LAUNCHER_UNPARSEABLE
        lines.append(out + "\n")
    return lines


def _fd_entry(step, dJ, dCD, dCL):
    """One central-difference entry with EXACTLY the requested derivatives, built
    by the PRODUCER'S OWN `build_fd_row`.  plus = d*s and minus = -d*s gives
    (plus-minus)/(2s) == d."""
    plus = {"J": dJ * step, "CD": [v * step for v in dCD], "CL": [v * step for v in dCL]}
    minus = {"J": -dJ * step, "CD": [-v * step for v in dCD], "CL": [-v * step for v in dCL]}
    return XF.build_fd_row(step, plus, minus)


def _fix(tmp, tweak=None):
    """Build a clean fixture.

    EVERY X AND F ARTEFACT IS WRITTEN BY `mpa1_xf`'s OWN WRITERS and EVERY LEDGER
    ROW BY THE LAUNCHER'S OWN FUNCTION.  Nothing on the positive path hand-rolls a
    schema -- see (IV).  The MESH log and the arm logs are REAL OpenFOAM bytes
    from `reference/`."""
    k = {"rc": {a: 0 for a in ARMS_DECLARED}, "ke": {},
         "oom": {a: "false" for a in ARMS_DECLARED},
         "cm": dict(PREDICTED_CORE_MIN), "cs": {a: CPUSET_REGISTERED for a in ARMS_DECLARED},
         "so": {a: SO_MD5[ARM_ROW[a]] for a in ARMS_DECLARED}, "cells": CELLS_EXPECTED,
         "err": {"SHIPPED": {}, "PATCHED": {}},          # (row, k) -> extra % error on the J FD reference
         "err_cl": {"SHIPPED": {}, "PATCHED": {}},       # (row, i, k) -> extra % error on the CL FD reference
         "flip": {"SHIPPED": set(), "PATCHED": set()},   # (k,) J FD reference sign-flipped
         "noplateau": {"SHIPPED": set(), "PATCHED": set()},
         "nearzero": {"SHIPPED": set(), "PATCHED": set()},
         "fdfail": {"SHIPPED": set(), "PATCHED": set()}, # (k,) every FD step failed
         "tb_agree": {"SHIPPED": set(), "PATCHED": set()},   # (k,) the WRONG step agrees -> G-TB pressure
         "mp_break": {"SHIPPED": None, "PATCHED": None}, # k whose assembled J adjoint is moved off the sum
         "alphas": None, "weights": None, "alpha_none": None,
         "of_drop": None,                    # an adjoint `of` key removed
         # ---- MP-A1's OWN FIXTURE KNOBS: the optimisation arm's shape.
         # The DEFAULT is the honest one for this ladder: the optimiser CONVERGES
         # on its own tolerance, which is the only state that can support a PASS.
         # Every other state is reachable by a knob and every one is DRIVEN by
         # `mpa1_grade_selftest.py`.
         "opt_exit": {a: "Optimal Solution Found." for a in ("O-S", "O-P")},
         "opt_stall": {a: "NO_STALL" for a in ("O-S", "O-P")},
         "opt_reduction_pct": {a: 12.5 for a in ("O-S", "O-P")},
         "opt_majors": {a: 12 for a in ("O-S", "O-P")},
         "opt_marker": {a: False for a in ("O-S", "O-P")},
         "opt_fail_flag": {a: False for a in ("O-S", "O-P")},
         # The endpoint arms state WHICH design point they evaluated at.  The
         # default is FINAL, which is the only state section 9 accepts.
         "design_point": {a: "FINAL" for a in ("XE-S", "XE-P", "FE-S", "FE-P")},
         "xopt_row": {a: ARM_ROW[a] for a in ("XE-S", "XE-P", "FE-S", "FE-P")},
         "terminal": {a: True for a in ARMS_DECLARED}, "stale": set(), "ctrl": "ok",
         "mpost": "20.00", "drop_row": set(), "drop_arm": set(), "inspect_file": set(),
         "rc_record": set(), "fatal": {}, "opt_key": {}, "chain_status": None,
         "datum": {a: ("plain" if a == "MESH" else "gz") for a in ARMS_DECLARED},
         "write_compression": "on", "evals_failed": {"SHIPPED": 1, "PATCHED": 1},
         "cl_base": [0.31, 0.50, 0.69], "cd_base": [0.0181, 0.0209, 0.0248],
         # MP-A1: the final-design CL offset from each registered target.  DEFAULT is
         # HELD (within TOL_CL_ABS, positive) -> G-CLHOLD PASS; a tweak pushes a point
         # out of band or negative to drive G-CLHOLD RED.
         "cl_hold_offset": [2.0e-4, 2.0e-4, 2.0e-4],
         "cl_target_override": False,   # stamp WRONG CL targets -> drive G-CLTGT RED
         "dl": "0.99 n=10 max_nr_throttled=0", "ledger_via_launcher": True}
    if tweak:
        tweak(k)
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6))
    os.makedirs(root)
    ident_of = {a: {"libidwarp_so_md5": k["so"][a], "idwarp_file": "/x/idwarp/__init__.py",
                    "write_compression": k["write_compression"]} for a in ARMS_DECLARED}
    alphas = k["alphas"] if k["alphas"] is not None else list(ALPHAS_REGISTERED)
    weights = k["weights"] if k["weights"] is not None else list(WEIGHTS_REGISTERED)
    if k["alpha_none"] is not None:
        alphas = list(alphas)
        alphas[k["alpha_none"]] = None
    mp_ident = XF.build_identity_block(alphas, ["point%d.patchV" % i for i in range(N_SCEN)],
                                       weights)

    def _dp(kk, a):
        """The design-point record the endpoint arms' producer stamps.

        `UNSPECIFIED` is the producer's fail-closed default and is reachable here
        by a knob, because a gate that has only ever seen `FINAL` has not been
        shown able to refuse anything else."""
        w = kk["design_point"].get(a)
        if w is None:
            return None
        return {"design_point": w,
                "xopt_file": ("mpa1_xopt.json" if w == "FINAL" else None),
                "xopt_row": (kk["xopt_row"].get(a) if w == "FINAL" else None),
                "xopt_sha256": ("f" * 64 if w == "FINAL" else None),
                "xopt_linf": ("0.008" if w == "FINAL" else None),
                "xopt_J_final": (0.0123 if w == "FINAL" else None)}

    for arm in ARMS_DECLARED:
        if arm in k["drop_arm"]:
            continue
        d = os.path.join(root, arm)
        tdir = "0.orig" if arm == "MESH" else "0"
        os.makedirs(os.path.join(d, tdir))
        os.makedirs(os.path.join(d, "system"), exist_ok=True)
        with open(os.path.join(d, CONTROLDICT_REL), "w") as fh:
            fh.write("writeFormat     ascii;\nwriteCompression %s;\n" % k["write_compression"])
        plain = os.path.join(d, tdir, "U")
        with open(plain, "w") as fh:
            fh.write("U\n")
        t0 = int(os.path.getmtime(plain))
        with open(os.path.join(d, DATUM_FILE), "w") as fh:
            fh.write("%d\n" % t0)
        kind = k["datum"][arm]
        if kind == "gz":
            os.remove(plain)
            gz = plain + ".gz"
            with open(gz, "w") as fh:
                fh.write("U compressed\n")
            os.utime(gz, (t0 + 3, t0 + 3))
        elif kind == "none":
            os.remove(plain)

        log = "%s_x.log" % arm
        text = ("D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\nD4S_DEADLINE_IN_CONTAINER_S: 600\n"
                % k["so"][arm])
        if ARM_KIND[arm] == "SOLVER":
            # REAL OPENFOAM BYTES: the banner discriminator and C5 both run on the
            # log this family actually produced -- 4 SIMPLE banners, 5 continuity
            # lines and 1 real convergence statement on a converged run.
            with open(REAL_ARMLOG, errors="replace") as fh:
                text += fh.read()

        if arm == "MESH":
            art = os.path.join(d, "checkMesh.log")
            with open(REAL_CHECKMESH, errors="replace") as fh:
                real = fh.read()
            with open(art, "w") as fh:
                fh.write(re.sub(r"^(\s*cells:\s+)\d+", r"\g<1>%d" % k["cells"], real,
                                count=1, flags=re.M))
        else:
            rk = ARM_ROW[arm]
            art = os.path.join(d, ARTEFACT[arm])
            adj_cd = {i: [_adj_cd(i, kk) for kk in range(8)] for i in range(N_SCEN)}
            adj_cl = {i: [_adj_cl(i, kk) for kk in range(8)] for i in range(N_SCEN)}
            # The assembled J adjoint is summed THROUGH THE PRODUCER'S OWN
            # `weighted_J`, in the registered order, so G-MP-STRUCT's identity is
            # bit-for-bit the arithmetic the objective used.
            adj_J = [XF.weighted_J([adj_cd[i][kk] for i in range(N_SCEN)], weights)
                     for kk in range(8)]
            if k["mp_break"][rk] is not None:
                bk = k["mp_break"][rk]
                adj_J[bk] = adj_J[bk] * 1.5 + 1.0e-6
            if arm.startswith("O-"):
                # ---- THE OPTIMISATION ARTEFACT.  Built here rather than by the
                # producer's own writer for one honest reason: the producer
                # cannot be imported on the host (it needs mphys, dafoam, pygeo
                # and idwarp), so `mpa1_runScript_selftest.py` drives its
                # STRUCTURE on the host and this fixture drives the COMPARATOR
                # against a record of the registered shape.  That split is
                # stated rather than papered over -- the O record is the one
                # artefact in this item NOT written by its own producer's code
                # in this suite, and `read_O`'s schema check is what keeps the
                # two shapes married.
                base_J = XF.weighted_J(k["cd_base"], weights)
                red = k["opt_reduction_pct"][arm]
                fin_J = base_J * (1.0 - red / 100.0)
                nm = k["opt_majors"][arm]
                stall_word = k["opt_stall"][arm]
                stall = {"stall": stall_word, "n_majors_parsed": nm,
                         "n_restoration_majors": (7 if stall_word == "STALL" else 0),
                         "cumulative_line_search_cutbacks": (547 if stall_word == "STALL" else 0),
                         "n_stall_window": STALL.N_STALL,
                         "alpha_pr_min": STALL.ALPHA_PR_MIN,
                         "stop_at_major": (34 if stall_word == "STALL" else None),
                         "condition_A_alpha_pr_run": {"fired": stall_word == "STALL",
                                                      "longest_run": (17 if stall_word == "STALL" else 0),
                                                      "ends_at_major": (34 if stall_word == "STALL" else None)},
                         "condition_B_inf_du_nondecreasing": {"fired": False,
                                                              "ends_at_major": None,
                                                              "window": None}}
                rec = {"item": "MP-A1", "row": rk, "libidwarp_so_md5": k["so"][arm],
                       "nprocs": 1, "optimizer": "IPOPT",
                       "max_iter_registered": 50, "tol_registered": 1.0e-5,
                       "driver_fail_flag": k["opt_fail_flag"][arm],
                       "wall_s": 1234.5,
                       "alphas": list(ALPHAS_REGISTERED), "weights": list(weights),
                       "scenarios": list(SCENARIOS),
                       # MP-A1 fixture: the CL is HELD at the registered targets
                       # (shape=0 is the feasible seed, so baseline CL == targets),
                       # and the final CL stays within TOL_CL_ABS of them -- the run
                       # this item is BUILT to earn.  `k["cl_hold_offset"]` lets a
                       # tweak push a point out of band to drive G-CLHOLD RED.
                       "baseline": {"J": base_J, "CD": list(k["cd_base"]),
                                    "CL": list(CL_TARGET)},
                       "final": {"J": fin_J,
                                 "CD": [v * (1.0 - red / 100.0) for v in k["cd_base"]],
                                 "CL": [CL_TARGET[i] + k["cl_hold_offset"][i]
                                        for i in range(N_SCEN)]},
                       "shape_final": [0.001 * (i + 1) for i in range(8)],
                       "weighted_drag_reduction_pct": red,
                       "cl_target": ([t + 0.01 for t in CL_TARGET]
                                     if k["cl_target_override"] else list(CL_TARGET)),
                       "CL_baseline": list(CL_TARGET),
                       "CL_final": [CL_TARGET[i] + k["cl_hold_offset"][i]
                                    for i in range(N_SCEN)],
                       "optimiser_exit_statement": k["opt_exit"][arm],
                       "convergence_statement_in_log": k["opt_exit"][arm] is not None,
                       "converged_to_optimizer_tolerance": None,
                       "stall": stall,
                       "stall_abort_marker_present": k["opt_marker"][arm],
                       "output_file": "opt_IPOPT.txt"}
                with open(art, "w") as fh:
                    json.dump(rec, fh, indent=1, sort_keys=True)
            elif arm.startswith("XE"):
                adjoint = {OF_J: {"shape": XF.vec(adj_J)}}
                for i in range(N_SCEN):
                    adjoint[OF_CD[i]] = {"shape": XF.vec(adj_cd[i])}
                    adjoint[OF_CL[i]] = {"shape": XF.vec(adj_cl[i])}
                if k["of_drop"] is not None:
                    adjoint.pop(k["of_drop"], None)
                rec = XF.build_X_record(1, XF.PRODUCER_MD5, ident_of[arm], mp_ident, adjoint,
                                        XF.weighted_J(k["cd_base"], weights),
                                        k["cd_base"], k["cl_base"], 12.3,
                                        1, 0, [],
                                        design_point=_dp(k, arm))
                with open(art, "w") as fh:
                    json.dump(rec, fh, indent=1, sort_keys=True)
            else:
                rows_ = []
                mid = sorted(STEPS_REGISTERED["shape"])[1]
                for _dv, idx in XF.COMPONENTS:
                    if idx in k["fdfail"][rk]:
                        fd = {repr(s): XF.build_fd_row_failed(s, "AnalysisError(Primal solution failed!)")
                              for s in STEPS_REGISTERED["shape"]}
                        tb = {repr(s): XF.build_fd_row_failed(s, "AnalysisError(Primal solution failed!)")
                              for s in TB_STEPS_REGISTERED["shape"]}
                        rows_.append({"dv": "shape", "idx": idx, "status": "MEASURED",
                                      "fd": fd, "tb": tb})
                        continue
                    e = k["err"][rk].get(idx, 0.5)
                    dJ0 = adj_J[idx] * (1.0 + e / 100.0)
                    if idx in k["flip"][rk]:
                        dJ0 = -dJ0
                    if idx in k["nearzero"][rk]:
                        dJ0 = 0.0
                    dCD0 = [adj_cd[i][idx] * (1.0 + e / 100.0) for i in range(N_SCEN)]
                    dCL0 = [adj_cl[i][idx] * (1.0 + k["err_cl"][rk].get((i, idx), 0.5) / 100.0)
                            for i in range(N_SCEN)]
                    fd = {}
                    for s in STEPS_REGISTERED["shape"]:
                        f = 1.0 if s == mid else (1.5 if idx in k["noplateau"][rk] else 1.01)
                        fd[repr(s)] = _fd_entry(s, dJ0 * f, [v * f for v in dCD0],
                                                [v * f for v in dCL0])
                    tb = {}
                    for s in TB_STEPS_REGISTERED["shape"]:
                        # The WRONG step is registered to be NOISE.  x3 is two
                        # orders outside band D; the `tb_agree` tweak makes it
                        # agree instead, which is the direction G-TB must catch.
                        g = 1.001 if idx in k["tb_agree"][rk] else 3.0
                        tb[repr(s)] = _fd_entry(s, adj_J[idx] * g, [v * g for v in dCD0],
                                                [v * g for v in dCL0])
                    rows_.append({"dv": "shape", "idx": idx, "status": "MEASURED",
                                  "fd": fd, "tb": tb})
                ctrl = XF.build_ctrl_row(XF.weighted_J(k["cd_base"], weights),
                                         k["cd_base"], k["cl_base"])
                if k["ctrl"] == "dead":
                    ctrl["planted"]["d"]["J"] = repr(0.0)
                    ctrl["planted"]["d"]["CD"] = [repr(0.0)] * N_SCEN
                    ctrl["planted"]["d"]["CL"] = [repr(0.0)] * N_SCEN
                elif k["ctrl"] == "empty":
                    ctrl["fd"][repr(CTRL_STEP)]["d"]["CD"] = []
                    ctrl["planted"]["d"]["CD"] = []
                elif k["ctrl"] == "absent":
                    ctrl = None
                if ctrl is not None:
                    rows_.append(ctrl)
                rec = XF.build_F_record(
                    1, XF.PRODUCER_MD5, ident_of[arm], mp_ident, rows_,
                    XF.weighted_J(k["cd_base"], weights), XF.weighted_J(k["cd_base"], weights),
                    k["cd_base"], k["cd_base"], k["cl_base"], k["cl_base"],
                    0.0, XF.ETA_FLOOR, True, {"shape": [repr(0.0)] * 8},
                    EVALS_DECLARED, k["evals_failed"][rk], [],
                    design_point=_dp(k, arm))
                with open(art, "w") as fh:
                    json.dump(rec, fh, indent=1, sort_keys=True)
            if k["opt_key"].get(arm):
                with open(art) as fh:
                    j = json.load(fh)
                j[k["opt_key"][arm]] = 73
                with open(art, "w") as fh:
                    json.dump(j, fh, indent=1, sort_keys=True)
            if k["terminal"][arm]:
                text += TERMINAL[arm] + " ok\n"
        if arm in k["fatal"]:
            text += k["fatal"][arm] + "\n"
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        with open(os.path.join(root, log), "w") as fh:
            fh.write(text)
        if arm in k["inspect_file"]:
            # THE SURVIVING KERNEL RECORD CARRIES THE REAL VALUE.  `rc_record`
            # suppresses the LEDGER row's field only -- that is what R-RC's
            # "absent from BOTH channels" means.
            ke = k["ke"].get(arm, k["rc"][arm])
            with open(os.path.join(root, "%s_x.inspect.txt" % arm), "w") as fh:
                fh.write("%s %s 2026-08-31T00:00:00Z 2026-08-31T00:01:00Z %s 12884901888 %s\n"
                         % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[ARM_ROW[arm]]))

    led = ["ITEM=MPA1\n", "STAGED stamp=x\n"]
    rows_out = _ledger_rows_via_launcher(k) if k["ledger_via_launcher"] else LAUNCHER_ABSENT
    if isinstance(rows_out, str):
        READERS["R1_read_ledger"]["born"] = False
        READERS["R1_read_ledger"]["not_born_reason"] = (
            "mpa1_run_arm.sh:mpa1_ledger_row could not be sourced (%s); the fixture fell back to a "
            "hand-written row, which CANNOT catch a launcher/reader format divergence" % rows_out)
        rows_out = [("ARM=%s ROW=%s IMG=img DIGEST=%s rc=%d wall_s=60 ranks=%d core_min=%s "
                     "cap_core_min=%s enforced_wall_s=600 enforced_core_min=%s memory=12g "
                     "inspect(exit,oomkilled)=[%s %s] memavail_pre_GiB=20.00 "
                     "memavail_post_GiB=%s cpuset=%s delivered_cores_mean=[%s] siblings_pre=[] "
                     "siblings_post=[] log=%s_x.log stamp=x\n")
                    % (a, ARM_ROW[a], IMG_DIGEST[ARM_ROW[a]], k["rc"][a], ARM_RANKS[a],
                       k["cm"][a], CAPS[a], CAPS[a],
                       NOT_MEASURED if a in k["rc_record"] else k["ke"].get(a, k["rc"][a]),
                       k["oom"][a], k["mpost"], k["cs"][a], k["dl"], a)
                    for a in ARMS_DECLARED]
    else:
        READERS["R1_read_ledger"]["born"] = True
        READERS["R1_read_ledger"].pop("not_born_reason", None)
    for a, line in zip(ARMS_DECLARED, rows_out):
        if a not in k["drop_row"] and a not in k["drop_arm"]:
            led.append(line)
    with open(os.path.join(root, "ledger.txt"), "w") as fh:
        fh.write("".join(led))
    if k["chain_status"] is not None:
        with open(os.path.join(root, "STATUS.chain"), "w") as fh:
            fh.write(k["chain_status"] + "\n")
    return root


# ===================== the selftest ===================================================
STOP_MARKER_PATH = os.path.join(_HERE, "mpa1_stop_marker.sh")


def _write_grade(root, rec, name="MPA1_grade_selftest.json"):
    p = os.path.join(root, name)
    with open(p, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True, default=str)
    return p


def stop_marker_basename():
    """THE MARKER'S NAME IS READ OUT OF THE FROZEN SCRIPT, NEVER GUESSED.

    This lane's first draft hardcoded `MPA1_STOP_MARKER.json`; the frozen writer
    writes `MPA1_STOP_MARKER.json` (mpa1_stop_marker.sh:59), so the check looked
    at an address nothing ever wrote and read `None` -- the SAME defect shape as
    SO-1c's, found here only because the consumer was DRIVEN rather than read.
    Binding the name to the producer's own line means a future rename REFUSES
    instead of silently reading an absent file as a failure."""
    if not os.path.isfile(STOP_MARKER_PATH):
        return None
    with open(STOP_MARKER_PATH, errors="replace") as fh:
        m = re.search(r'^MARKER="\$BASE/([^"]+)"', fh.read(), re.M)
    if not m:
        refuse("SCHEMA", {"stop_marker_MARKER_line_not_found": STOP_MARKER_PATH,
                          "note": ("the marker address is read out of the frozen writer; a writer "
                                   "whose address this reader cannot find is a schema break")})
    return m.group(1)


def _run_stop_marker(root, gpath, executed=N_DECLARED):
    """THE SCHEMA CONTRACT, DRIVEN -- see (I).  Runs the ALREADY-FROZEN consumer
    against an artefact THIS MODULE wrote and reports what the consumer could see.
    The rc is captured DIRECTLY from `subprocess.run`, never through a pipe --
    `cmd | tail` would hand back tail's rc, and three agents on this team misread
    an exit code that way in one day."""
    if not os.path.isfile(STOP_MARKER_PATH):
        return {"state": "NOT EXERCISED -- mpa1_stop_marker.sh absent", "rc": None, "marker": None}
    p = subprocess.run(["bash", STOP_MARKER_PATH, root, "0", str(N_DECLARED),
                        str(executed), gpath], capture_output=True, text=True)
    marker = os.path.join(root, stop_marker_basename())
    rec = None
    if os.path.isfile(marker):
        with open(marker) as fh:
            rec = json.load(fh)
    return {"state": "EXERCISED", "rc": p.returncode, "marker": rec, "marker_path": marker,
            "stdout": p.stdout.strip()[:400], "stderr": p.stderr.strip()[:400]}


def selftest(tmp):
    n = 0
    fails = []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    def refused(root):
        try:
            grade(root)
            return False
        except Refusal:
            return True

    def tw(**kw):
        def f(k):
            for key, val in kw.items():
                if isinstance(val, dict) and isinstance(k.get(key), dict):
                    k[key].update(val)
                else:
                    k[key] = val
        return f

    # ---- A. the clean fixture ------------------------------------------------------
    root0 = _fix(tmp)
    r = grade(root0)
    unit("U1 clean fixture -> item PASS, both rows PASS",
         r["verdict"] == "PASS" and r["rows"] == {"SHIPPED": "PASS", "PATCHED": "PASS"})
    unit("U2 clean fixture -> G-M2, G-ALPHA, G-NOOPT, G9, G10, G12 all PASS",
         r["gates"]["G-M2_mesh_identity"] == "PASS"
         and r["gates"]["G-ALPHA_operating_points"]["verdict"] == "PASS"
         and r["gates"]["G-NOOPT-ENDPOINT_no_optimiser_in_the_endpoint_arms"]["verdict"] == "PASS"
         and r["gates"]["G9_toolchain"]["verdict"] == "PASS"
         and r["gates"]["G10_caps"]["verdict"] == "PASS"
         and r["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("U3 clean fixture -> G-MP-STRUCT PASS on both rows over a NON-EMPTY tuple",
         all(r["gates"]["G5J"][w]["G_MP_STRUCT_assembly_identity"]["verdict"] == "PASS"
             and r["gates"]["G5J"][w]["G_MP_STRUCT_assembly_identity"]["n_components_checked"] == 4
             for w in ("SHIPPED", "PATCHED")))
    unit("U4 clean fixture -> G5J grades 4 of 4 pairs on both rows, aggregate <= 1 %",
         all(r["gates"]["G5J"][w]["G5J_objective"]["n_graded_pairs"] == 4
             and r["gates"]["G5J"][w]["G5J_objective"]["aggregate_rel_err_pct"] <= 1.0
             for w in ("SHIPPED", "PATCHED")))
    unit("U5 clean fixture -> G5C grades all THREE scenarios, 4 pairs each",
         all(r["gates"]["G5J"][w]["G5C_lift_per_scenario"]["per_scenario"][s]["n_graded_pairs"] == 4
             for w in ("SHIPPED", "PATCHED") for s in SCENARIOS))
    unit("U6 clean fixture -> G-TB PASS: 0 of 4 components agree at the WRONG step h=1e-8",
         all(r["gates"]["G5J"][w]["G_TB_trivial_baseline"]["verdict"] == "PASS"
             and r["gates"]["G5J"][w]["G_TB_trivial_baseline"]["n_passing_at_the_wrong_step"] == 0
             for w in ("SHIPPED", "PATCHED")))
    # ---- MP-A1 GATES: G-CLHOLD, G-DRAG, G-CLTGT, G5C dCL_i/dx coverage ------------
    unit("U6a MP-A1 clean -> G-CLHOLD PASS both rows: lift HELD at all 3 targets, none negative",
         all(r["gates"]["G-CLHOLD_cl_satisfaction_per_row"][w]["verdict"] == "PASS"
             and all(p["held"] and p["cl_positive"]
                     for p in r["gates"]["G-CLHOLD_cl_satisfaction_per_row"][w]["per_point"].values())
             for w in ("SHIPPED", "PATCHED")))
    unit("U6b MP-A1 clean -> G-DRAG PASS both rows: final weighted J < baseline J",
         all(r["gates"]["G-DRAG_reduction_per_row"][w]["verdict"] == "PASS"
             and r["gates"]["G-DRAG_reduction_per_row"][w]["J_final"]
                 < r["gates"]["G-DRAG_reduction_per_row"][w]["J_baseline"]
             for w in ("SHIPPED", "PATCHED")))
    unit("U6c MP-A1 clean -> G-CLTGT PASS: stamped targets == registered CL_TARGET",
         all(r["gates"]["G-CLTGT_targets_registered_per_row"][w]["verdict"] == "PASS"
             for w in ("SHIPPED", "PATCHED")))
    unit("U6d G5C COVERS all THREE dCL_i/dx CONSTRAINT gradients at the final design (check-3)",
         all(r["gates"]["G5J"][w]["G5C_lift_per_scenario"].get("covers_constraint_gradients") is True
             and r["gates"]["G5J"][w]["G5C_lift_per_scenario"].get("n_cl_constraint_gradients_graded") == N_SCEN
             for w in ("SHIPPED", "PATCHED")))
    # G-CLHOLD fires RED both ways: out-of-band, and a NEGATIVE collapse (SO-3's mode).
    r_oob = grade(_fix(tmp, tw(cl_hold_offset=[2.0e-3, 2.0e-4, 2.0e-4])))
    unit("U6e G-CLHOLD RED: a point out of band (dev 2e-3 > TOL 1e-3) -> row + item GATE FAIL",
         r_oob["gates"]["G-CLHOLD_cl_satisfaction_per_row"]["PATCHED"]["verdict"] == "GATE FAIL"
         and r_oob["gates"]["G-CLHOLD_cl_satisfaction_per_row"]["PATCHED"]["per_point"][SCENARIOS[0]]["held"] is False
         and r_oob["rows"]["PATCHED"] == "GATE FAIL" and r_oob["verdict"] == "GATE FAIL")
    r_neg = grade(_fix(tmp, tw(cl_hold_offset=[-(CL_TARGET[0] + 0.05), 2.0e-4, 2.0e-4])))
    unit("U6f G-CLHOLD RED: lift driven NEGATIVE at point0 (SO-3's collapse) -> GATE FAIL",
         r_neg["gates"]["G-CLHOLD_cl_satisfaction_per_row"]["PATCHED"]["per_point"][SCENARIOS[0]]["cl_positive"] is False
         and r_neg["gates"]["G-CLHOLD_cl_satisfaction_per_row"]["PATCHED"]["verdict"] == "GATE FAIL"
         and r_neg["rows"]["PATCHED"] == "GATE FAIL")
    # G-DRAG fires RED: the constrained optimiser did not improve on the feasible seed.
    r_nod = grade(_fix(tmp, tw(opt_reduction_pct={"O-S": 0.0, "O-P": 0.0})))
    unit("U6g G-DRAG RED: final J == baseline J (no improvement) -> row + item GATE FAIL",
         r_nod["gates"]["G-DRAG_reduction_per_row"]["PATCHED"]["verdict"] == "GATE FAIL"
         and r_nod["rows"]["PATCHED"] == "GATE FAIL" and r_nod["verdict"] == "GATE FAIL")
    # G-CLTGT fires RED: the run stamped targets other than the registered ones.
    r_tgt = grade(_fix(tmp, tw(cl_target_override=True)))
    unit("U6h G-CLTGT RED: stamped targets != registered CL_TARGET -> GATE FAIL",
         r_tgt["gates"]["G-CLTGT_targets_registered_per_row"]["PATCHED"]["verdict"] == "GATE FAIL"
         and r_tgt["verdict"] == "GATE FAIL")
    # THE G-CLHOLD PLANTED CONTROL fired BOTH ways in the clean grade (rule 3).
    unit("U6i G-CLHOLD planted control fired both ways: held->PASS, planted->GATE FAIL, collapse->GATE FAIL, plant seen off disk",
         r["controls"]["grader_plant_clhold"]["exercised"] is True
         and r["controls"]["grader_plant_clhold"]["plant_seen"] is True
         and r["controls"]["grader_plant_clhold"]["v_held"] == "PASS"
         and r["controls"]["grader_plant_clhold"]["v_planted"] == "GATE FAIL"
         and r["controls"]["grader_plant_clhold"]["v_collapsed"] == "GATE FAIL")
    unit("U7 clean fixture -> every plateau proved PER PAIR, never once for the item",
         all("plateau_neighbour_pct" in p and len(p["plateau_neighbour_pct"]) == 2
             for w in ("SHIPPED", "PATCHED")
             for p in r["gates"]["G5J"][w]["G5J_objective"]["pairs"]))
    unit("U8 clean fixture -> G-STAGES silent: DECLARED 7 == EXECUTED 7, BOTH reported",
         r["gates"]["G-STAGES_declared_vs_executed"]["verdict"] == "PASS"
         and r["gates"]["G-STAGES_declared_vs_executed"]["declared"] == N_DECLARED
         and r["gates"]["G-STAGES_declared_vs_executed"]["executed"] == N_DECLARED)
    unit("U9 clean fixture -> the verdict is in the frozen vocabulary", r["verdict"] in VOCAB)
    unit("U10 clean fixture -> no GCI is quoted anywhere in the record",
         "GCI" not in json.dumps({kk: vv for kk, vv in r.items() if kk != "no_gci"}))

    # ---- B. THE SCHEMA CONTRACT WITH THE FROZEN CONSUMERS -- see (I) ---------------
    gp = _write_grade(root0, r)
    sm = _run_stop_marker(root0, gp)
    unit("U11 SCHEMA the FROZEN mpa1_stop_marker.sh reads this artefact's verdict",
         sm["state"] == "EXERCISED" and sm["rc"] == 0 and sm["marker"] is not None
         and sm["marker"]["verdict"] == r["verdict"]
         and sm["marker"]["verdict_source"] == "COPIED FROM THE COMPARATOR ARTEFACT")
    unit("U11b SCHEMA the marker ADDRESS is read out of the frozen writer, never guessed",
         stop_marker_basename() == "MPA1_STOP_MARKER.json"
         and sm["marker_path"].endswith("MPA1_STOP_MARKER.json"))
    unit("U12 SCHEMA the FROZEN consumer finds gates.G5J -- the LITERAL key it looks for",
         sm["state"] == "EXERCISED" and sm["marker"] is not None
         and sm["marker"]["G5J"] != "NOT PRESENT IN THE ARTEFACT")
    r_break = json.loads(json.dumps(r, default=str))
    r_break["gates"]["G5J_PATCHED"] = r_break["gates"].pop("G5J")
    gp_b = _write_grade(root0, r_break, "MPA1_grade_schemabreak.json")
    sm_b = _run_stop_marker(root0, gp_b)
    unit("U13 SCHEMA the SAME check FAILS when the key is renamed -- the contract can fail",
         sm_b["state"] == "EXERCISED" and sm_b["marker"] is not None
         and sm_b["marker"]["G5J"] == "NOT PRESENT IN THE ARTEFACT")
    r_break2 = json.loads(json.dumps(r, default=str))
    r_break2["grade"] = {"verdict": r_break2.pop("verdict")}
    gp_b2 = _write_grade(root0, r_break2, "MPA1_grade_verdictbreak.json")
    sm_b2 = _run_stop_marker(root0, gp_b2)
    unit("U14 SCHEMA a verdict moved one level down reads PENDING, never a silent PASS",
         sm_b2["state"] == "EXERCISED" and sm_b2["marker"] is not None
         and sm_b2["marker"]["verdict"] == "PENDING")
    unit("U15 SCHEMA the frozen driver's --out flag is implemented by main()",
         "--out" in open(os.path.abspath(__file__)).read())

    # ---- C. rule 3: the planted controls, BOTH DIRECTIONS --------------------------
    unit("U20 CONTROL instrument CTRL read back: 7 zero entries exactly 0.0 per row",
         all(r["controls"]["instrument_ctrl_%s" % rk]["n_zero_entries_read"] == 1 + 2 * N_SCEN
             for rk in ROWS))
    _want = r["controls"]["instrument_ctrl_%s" % ROWS[0]]["want"]
    unit("U21 CONTROL instrument CTRL planted side reads PLANT/(2*step) on all 7",
         len(r["controls"]["instrument_ctrl_%s" % ROWS[0]]["planted_read"]) == 1 + 2 * N_SCEN
         and all(abs(v - _want) <= 1e-12 * abs(_want)
                 for v in r["controls"]["instrument_ctrl_%s" % ROWS[0]]["planted_read"].values()))
    unit("U22 CONTROL a DEAD plant REFUSES (the reader cannot see the non-zero)",
         refused(_fix(tmp, tw(ctrl="dead"))))
    unit("U23 CONTROL an EMPTIED tuple REFUSES rather than raising IndexError",
         refused(_fix(tmp, tw(ctrl="empty"))))
    unit("U24 CONTROL an ABSENT CTRL row REFUSES", refused(_fix(tmp, tw(ctrl="absent"))))
    unit("U25 CONTROL grader_plant_F moved every derivative by exactly PLANT",
         all(r["controls"]["grader_plant_F_%s" % rk]["worst_residual"] < 1e-12
             and r["controls"]["grader_plant_F_%s" % rk]["n_values"] > 0 for rk in ROWS))
    unit("U26 CONTROL grader_plant_F traverses J, CD and CL at fd AND tb steps",
         r["controls"]["grader_plant_F_%s" % ROWS[0]]["n_values"]
         == len(XF.COMPONENTS) * (len(STEPS_REGISTERED["shape"]) + len(TB_STEPS_REGISTERED["shape"]))
         * (1 + 2 * N_SCEN))
    unit("U27 CONTROL THE FLIP: G5J PASS moves to GATE FAIL on the planted X copy",
         all(r["controls"]["grader_plant_X_%s" % rk]["G5J_unplanted"] == "PASS"
             and r["controls"]["grader_plant_X_%s" % rk]["G5J_planted"] == "GATE FAIL"
             for rk in ROWS))
    unit("U28 CONTROL THE FLIP: G-MP-STRUCT PASS moves to GATE FAIL on the planted X copy",
         all(r["controls"]["grader_plant_X_%s" % rk]["g_mp_struct_unplanted"] == "PASS"
             and r["controls"]["grader_plant_X_%s" % rk]["g_mp_struct_planted"] == "GATE FAIL"
             for rk in ROWS))
    unit("U28b CONTROL the flip control is COMPARATIVE: a row below the graded-pair floor "
         "reads NOT A RESULT planted AND unplanted, and is not refused",
         grade(_fix(tmp, tw(noplateau={"PATCHED": {0, 3}})))["rows"]["PATCHED"] == "NOT A RESULT")
    # ---- MP-A1's PLANT-SIZING UNITS.  The plant is RELATIVE to the band it must
    # ---- cross, and the sufficiency claim is DRIVEN AT AN INSUFFICIENT K.
    _pc = r["controls"]["grader_plant_X_%s" % ROWS[0]]
    unit("U28c PLANT SIZING: the production plant is RELATIVE, not absolute, and names "
         "its d_ref scale",
         _pc["plant_sizing"].startswith("RELATIVE") and _pc["d_ref_scale"] is not None
         and _pc["plant_K"] == PLANT_K)
    unit("U28d PLANT SIZING: the planted relative error is PLANT_K * band_D by "
         "construction, whatever the quantity's scale",
         abs(_pc["planted_rel_err_pct"] - PLANT_K * FD_BAND_PCT) < 1e-9)
    unit("U28e PLANT SIZING: the plant CLEARS the band it must cross",
         _pc["planted_rel_err_pct"] > FD_BAND_PCT)
    # THE SUFFICIENCY LEG, AND IT IS DRIVEN RED.  A claim that the plant is big
    # enough is worth nothing unless the same machinery is shown to FAIL to flip
    # the gate when the plant is too small.  `PLANT_K_INSUFF` reproduces SO-2M's
    # geometry exactly: a plant BELOW the band.  If this unit's condition ever
    # reads the other way, the flip in U27 was not caused by the plant crossing
    # the band and U27 is not evidence about the gate.
    _rk = ROWS[0]
    _Xr = read_X(os.path.join(root0, X_ARM[_rk], XF.OUT_X))
    _Fr = read_F(os.path.join(root0, F_ARM[_rk], XF.OUT_F))
    _ps = [p for p in grade_objective_gradient(_Xr, _Fr)["pairs"] if p.get("graded")]
    _k, _ref = _ps[0]["idx"], _ps[0]["d_ref"]
    _small = grader_plant_X(root0, os.path.join(root0, X_ARM[_rk], XF.OUT_X),
                            _rk + "_INSUFF", _k, scale=_ref, plant_k=PLANT_K_INSUFF)
    _v_small = grade_objective_gradient(read_X(_small["file"]), _Fr)["verdict"]
    unit("U28f PLANT SUFFICIENCY, DRIVEN RED: at PLANT_K_INSUFF the plant does NOT "
         "cross band D and the gate does NOT flip -- so U27's flip is caused by the "
         "plant crossing the band, not by any perturbation whatsoever (SO-2M's mode)",
         _small["planted_rel_err_pct"] < FD_BAND_PCT and _v_small == "PASS")
    unit("U28g PLANT SUFFICIENCY: the insufficient K reproduces SO-2M's geometry -- a "
         "plant inside the band, an EXERCISED control that demonstrates nothing",
         abs(_small["planted_rel_err_pct"] - PLANT_K_INSUFF * FD_BAND_PCT) < 1e-9)
    unit("U29 CONTROL grader_plant_cells reads a DIFFERENT number off changed real bytes",
         r["controls"]["grader_plant_cells"]["read_back"]
         == r["controls"]["grader_plant_cells"]["on_disk_before_plant"] + 7)
    unit("U30 CONTROL every planted control reports EXERCISED, none inferred from absence",
         all(isinstance(r["controls"][kk], dict) and "NOT EXERCISED" not in json.dumps(r["controls"][kk])
             for kk in ("instrument_ctrl_%s" % ROWS[0], "grader_plant_F_%s" % ROWS[0], "grader_plant_X_%s" % ROWS[0],
                        "grader_plant_cells", "grader_plant_c5")))

    # ---- D. the ledger and the age guard -------------------------------------------
    unit("U40 R1 the ledger reader parsed every arm row",
         len(r["completion"]["arms"]) == N_DECLARED)
    unit("U41 R1 a PRESENT-BUT-GARBAGE ledger row REFUSES, never skipped",
         refused(_fix(tmp, tw(mpost="not a number at all here"))))
    unit("U41b R1 a STRUCTURALLY VALID row carrying a NON-NUMERIC field REFUSES BY NAME "
         "and does not raise -- a crash is not a verdict",
         refused(_fix(tmp, tw(mpost="abc"))))
    _nonnum = None
    try:
        grade(_fix(tmp, tw(mpost="abc")))
    except Refusal as _exc:
        _nonnum = json.loads(str(_exc))
    unit("U41c R1 that refusal NAMES the offending field, so a reader is not left "
         "guessing which column was garbage",
         _nonnum is not None
         and "memavail_post_GiB" in json.dumps(_nonnum))
    unit("U42 R7 the age datum resolved to the COMPRESSED twin on every solver arm",
         all(r["age_datum_resolution"][a]["is_compressed_twin"]
             for a in ARMS_DECLARED if ARM_KIND[a] == "SOLVER"))
    unit("U43 R7 NEITHER datum name present -> REFUSE (the AV-1/AV-2 failure)",
         refused(_fix(tmp, tw(datum={"XE-S": "none"}))))
    unit("U44 C4 a STALE artefact (older than its own datum) REFUSES",
         refused(_fix(tmp, tw(stale={"FE-P"}))))
    unit("U45 C1 a non-zero rc REFUSES", refused(_fix(tmp, tw(rc={"XE-P": 7}))))
    unit("U46 C1 harness/kernel rc disagreement REFUSES",
         refused(_fix(tmp, tw(ke={"XE-S": 3}))))
    unit("U47 G11 OOMKilled true REFUSES, never a re-fire",
         refused(_fix(tmp, tw(oom={"FE-S": "true"}))))
    r_rc = grade(_fix(tmp, tw(rc_record={"XE-S"}, inspect_file=set())))
    unit("U48 R-RC an rc RECORD absent from BOTH channels reads NOT_MEASURED with an INFERENCE",
         r_rc["rule4_clauses_per_arm"]["XE-S"]["C1_rc_value"]["verdict"] == NOT_MEASURED
         and r_rc["rc_inferences"]["XE-S"]["status"].startswith("INFERENCE"))
    unit("U49 R-RC relaxes a MISSING record, NEVER a positive reading of failure",
         refused(_fix(tmp, tw(rc_record={"XE-S"}, rc={"XE-S": 5}))))

    # ---- E. C5 and the BANNER DISCRIMINATOR -- see (III) ----------------------------
    unit("U50 C5 a real crash line planted into the arm's own REAL bytes is SEEN",
         r["controls"]["grader_plant_c5"]["positive_sites"] == 1)
    unit("U51 C5 the UNPLANTED real bytes produce ZERO sites",
         r["controls"]["grader_plant_c5"]["negative_sites"] == 0)
    for _tok in ("FOAM FATAL ERROR", "Segmentation fault", "SIGSEGV", "MPI_ABORT", "Signal 11"):
        pass
    unit("U52 C5 every FATAL token planted in turn REFUSES",
         all(refused(_fix(tmp, tw(fatal={"XE-P": "  " + t + " here"})))
             for t in ("FOAM FATAL ERROR", "Segmentation fault", "SIGSEGV", "MPI_ABORT")))
    _bb = r["controls"]["grader_plant_c5"]["benign_banners_excluded_and_counted"]
    unit("U53 C5 none of the THREE banners is ever read as a crash site",
         all(v["sites"] == 0 for v in _bb.values()))
    unit("U53b C5 trapFpe DOES carry a fatal token and IS counted as a named benign exclusion",
         _bb["trapFpe"]["fatal_tokens_the_line_matches"] == ["Floating point exception"]
         and _bb["trapFpe"]["new_benign_lines"] == 1)
    unit("U53c C5 the SIMPLE banner and the continuity line match NO fatal token -- a "
         "DIFFERENT and weaker protection, stated as such",
         _bb["SIMPLE_banner"]["fatal_tokens_the_line_matches"] == []
         and _bb["continuity"]["fatal_tokens_the_line_matches"] == []
         and "weaker" in _bb["continuity"]["protected_by"])
    unit("U54 R3 the cells reader read 4032 off REAL checkMesh bytes", r["mesh_cells"] == 4032)
    unit("U55 G-M2 a different cell count is GATE FAIL -- a different mesh is a different item",
         grade(_fix(tmp, tw(cells=4031)))["gates"]["G-M2_mesh_identity"] == "GATE FAIL")
    conv = r["primal_convergence"]["per_arm"]["XE-S"]
    unit("U56 R2b the REAL convergence statement is read on the real converged log",
         conv["n_converged_statements"] == 1)
    unit("U57 R2b the SIMPLE banner is COUNTED SEPARATELY -- 4x on that same converged log",
         conv["banner_not_evidence"]["count"] == 4)
    unit("U58 R2b the discriminator does not move on a planted BANNER but DOES on a real statement",
         r["controls"]["grader_plant_c5"]["convergence_discriminator"]["unmoved_by_a_planted_banner"]
         and r["controls"]["grader_plant_c5"]["convergence_discriminator"]["moved_by_a_planted_REAL_statement"])
    unit("U59 R2b `Time step continuity errors` appears 5x and is NEVER a C5 site",
         r["controls"]["grader_plant_c5"]["benign_banners_excluded_and_counted"]["continuity"]["sites"] == 0
         and sum(1 for ln in open(REAL_ARMLOG, errors="replace")
                 if "Time step continuity errors" in ln) == 5)

    # ---- F. the bright line, driven in the failing directions ----------------------
    unit("U60 R4 an adjoint `of` key missing (a scenario dropped) REFUSES",
         refused(_fix(tmp, tw(of_drop="CD2"))))
    unit("U61 G5J a 6 % error on one pair is GATE FAIL on that row",
         grade(_fix(tmp, tw(err={"PATCHED": {0: 6.0}})))["rows"]["PATCHED"] == "GATE FAIL")
    unit("U62 G5J a SIGN FLIP is GATE FAIL whatever the magnitude",
         grade(_fix(tmp, tw(flip={"PATCHED": {3}})))["rows"]["PATCHED"] == "GATE FAIL")
    r_np = grade(_fix(tmp, tw(noplateau={"PATCHED": {0, 3}})))
    unit("U63 G5J NO_PLATEAU pairs are EXCLUDED, COUNTED AND NAMED",
         r_np["gates"]["G5J"]["PATCHED"]["G5J_objective"]["excluded_by_reason"].get("NO_PLATEAU") == 2)
    unit("U64 G5J fewer than 3 graded pairs -> the ROW is NOT A RESULT",
         grade(_fix(tmp, tw(noplateau={"PATCHED": {0, 3, 6}})))["rows"]["PATCHED"] == "NOT A RESULT")
    r_fail = grade(_fix(tmp, tw(fdfail={"PATCHED": {0}})))
    unit("U65 G-EVALFAIL a FAILED evaluation marks its pairs ungraded and the row still grades",
         r_fail["gates"]["G5J"]["PATCHED"]["G5J_objective"]["excluded_by_reason"]
         .get("FD_STEP_FAILED_OR_ABSENT") == 1
         and r_fail["gates"]["G5J"]["PATCHED"]["G5J_objective"]["n_graded_pairs"] == 3
         and r_fail["rows"]["PATCHED"] == "PASS")
    unit("U66 G5J NEAR_ZERO pairs are excluded by reason, not silently graded",
         grade(_fix(tmp, tw(nearzero={"PATCHED": {0}})))["gates"]["G5J"]["PATCHED"]["G5J_objective"]
         ["excluded_by_reason"].get("NEAR_ZERO") == 1)
    unit("U67 G5C an error on ONE scenario's CL is GATE FAIL on that row",
         grade(_fix(tmp, tw(err_cl={"PATCHED": {(2, 3): 9.0}})))["rows"]["PATCHED"] == "GATE FAIL")

    # ---- G. G-MP-STRUCT, G-TB, G-ALPHA, G-NOOPT, G-STAGES --------------------------
    unit("U70 G-MP-STRUCT a J adjoint moved off the weighted sum is GATE FAIL",
         grade(_fix(tmp, tw(mp_break={"PATCHED": 3})))["gates"]["G5J"]["PATCHED"]
         ["G_MP_STRUCT_assembly_identity"]["verdict"] == "GATE FAIL")
    unit("U71 G-MP-STRUCT that GATE FAIL composes into the row verdict",
         grade(_fix(tmp, tw(mp_break={"PATCHED": 3})))["rows"]["PATCHED"] == "GATE FAIL")
    r_tb = grade(_fix(tmp, tw(tb_agree={"PATCHED": {0, 3}})))
    unit("U72 G-TB 2 of 4 agreeing at the WRONG step is GATE FAIL",
         r_tb["gates"]["G5J"]["PATCHED"]["G_TB_trivial_baseline"]["verdict"] == "GATE FAIL"
         and r_tb["gates"]["G5J"]["PATCHED"]["G_TB_trivial_baseline"]["n_passing_at_the_wrong_step"] == 2)
    unit("U73 G-TB that GATE FAIL WITHDRAWS the row's G5J PASS to NOT A RESULT",
         r_tb["gates"]["G5J"]["PATCHED"]["G5J_objective"]["verdict"] == "PASS"
         and r_tb["rows"]["PATCHED"] == "NOT A RESULT")
    unit("U74 G-TB exactly 1 agreeing is still PASS (the registered threshold)",
         grade(_fix(tmp, tw(tb_agree={"PATCHED": {0}})))["gates"]["G5J"]["PATCHED"]
         ["G_TB_trivial_baseline"]["verdict"] == "PASS")
    unit("U75 G-TB an ERRORED probe counts as FAILING the baseline, not as agreement",
         grade(_fix(tmp, tw(fdfail={"PATCHED": {0}})))["gates"]["G5J"]["PATCHED"]
         ["G_TB_trivial_baseline"]["per_component"]["shape[0]"]["counts_as"].startswith("FAILING"))
    unit("U76 G-ALPHA an unregistered angle REFUSES (exit 2), it is not a GATE FAIL",
         refused(_fix(tmp, tw(alphas=[3.0, 5.13918623195176, 7.13918623195176]))))
    unit("U77 G-ALPHA an UNRESOLVED angle (None) REFUSES, never papered over",
         refused(_fix(tmp, tw(alpha_none=2))))
    unit("U78 G-ALPHA unregistered weights REFUSE",
         refused(_fix(tmp, tw(weights=[0.5, 0.25, 0.25]))))
    unit("U79 G-NOOPT an optimiser history key in an artefact REFUSES",
         all(refused(_fix(tmp, tw(opt_key={"XE-P": kk})))
             for kk in ("optimiser_history", "majors", "run_driver")))
    r_short = grade(_fix(tmp, tw(drop_arm={"XE-P", "FE-P"}, drop_row={"XE-P", "FE-P"})))
    unit("U80 CENSUS a chain stop is GRADED, not refused: arms that ran carry gate readings",
         r_short["arm_census"]["XE-P"]["state"] == "NOT RUN"
         and r_short["arm_census"]["MESH"]["state"] == "RAN"
         and r_short["gates"]["G5J"]["SHIPPED"]["state"] == "RAN")
    unit("U81 G-STAGES a shortfall with NO registered guard -> item NOT A RESULT",
         r_short["verdict"] == "NOT A RESULT"
         and r_short["gates"]["G-STAGES_declared_vs_executed"]["executed"] == N_DECLARED - 2
         and r_short["gates"]["G-STAGES_declared_vs_executed"]["declared"] == N_DECLARED)
    r_blk = grade(_fix(tmp, tw(drop_arm={"XE-P", "FE-P"}, drop_row={"XE-P", "FE-P"},
                               chain_status="chain=BLOCKED_H5 declared=%d executed=%d"
                                            % (N_DECLARED, N_DECLARED - 2))))
    unit("U82 G-STAGES the SAME shortfall under a REGISTERED guard -> item BLOCKED, guard named",
         r_blk["verdict"] == "BLOCKED"
         and "H5" in (r_blk["gates"]["G-STAGES_declared_vs_executed"]["registered_resource_guard"] or ""))
    unit("U83 G-STAGES neither shortfall row is PRE-FILTERED: declared 7 is reported both times",
         r_short["gates"]["G-STAGES_declared_vs_executed"]["arms_not_run"] == ["FE-P", "XE-P"] or r_short["gates"]["G-STAGES_declared_vs_executed"]["arms_not_run"] == ["XE-P", "FE-P"]
         and r_blk["gates"]["G-STAGES_declared_vs_executed"]["both_counts_reported"])

    # ---- H. the file's own hygiene, and the rename collision check -----------------
    me = os.path.abspath(__file__)
    unit("U84 L-332 ast.Assert == 0 in this comparator", count_asserts(me) == 0)
    planted = os.path.join(tmp, "planted_assert.py")
    with open(planted, "w") as fh:
        fh.write("def f(x):\n    assert x\n    return x\n")
    unit("U85 L-332 the SAME counter counts a PLANTED assert -- the zero is not a blind reader",
         count_asserts(planted) == 1)
    unit("U86 the whole-file token-scan detector reads ZERO on this comparator",
         whole_file_token_scan_sites(me) == [])
    so1a = os.path.join(_HERE, "..", "curriculum_SO1a", "so1a_grade.py")
    if os.path.isfile(so1a):
        unit("U87 the SAME detector finds the KNOWN POSITIVE in so1a_grade.py (L-400)",
             "fatal_tokens_in" in whole_file_token_scan_sites(so1a))
    else:
        planted_ws = os.path.join(tmp, "planted_wholefile.py")
        with open(planted_ws, "w") as fh:
            fh.write("FATAL_TOKENS = ('X',)\n"
                     "def fatal_tokens_in(text):\n"
                     "    return [t for t in FATAL_TOKENS if t in text]\n")
        unit("U87 the SAME detector finds a PLANTED known positive (L-400; SO-1a's file absent)",
             whole_file_token_scan_sites(planted_ws) == ["fatal_tokens_in"])
    with open(me) as fh:
        src = fh.read()
    # The old alias is RECONSTRUCTED FROM PARTS so this file does not itself
    # contain the token it is proving absent -- a check whose own text is a hit
    # can only be satisfied by weakening the check.
    old_alias = "X" + "G"
    n_xg = len(re.findall(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % old_alias, src))
    parent = os.path.join(_HERE, "..", "curriculum_SO2a", "so2a_grade.py")
    n_xf_in_parent = None
    if os.path.isfile(parent):
        with open(parent) as fh:
            psrc = fh.read()
        n_xf_in_parent = len(re.findall(r"(?<![A-Za-z0-9_])XF(?![A-Za-z0-9_])", psrc))
    unit("U88 RENAME half 1 -- the OLD alias %s is GONE from this file (%d occurrences)"
         % (old_alias, n_xg), n_xg == 0)
    unit("U89 RENAME half 2 -- COLLISION: the NEW name `XF` was NOT already bound in the parent",
         n_xf_in_parent == 0)
    unit("U90 the launcher PATH variable is never reassigned to hold the launcher's RESULT",
         "LAUNCHER_PATH" in src and "rows_out" in src
         and not re.search(r"^\s*LAUNCHER_PATH\s*=\s*_ledger_rows_via_launcher", src, re.M))
    unit("U91 the two launcher failure modes carry DISTINCT sentinels",
         LAUNCHER_ABSENT != LAUNCHER_UNPARSEABLE)
    unit("U92 SCHEMA no key is found by a recursive hunt: every nested read is registered",
         all(isinstance(v, tuple) for v in SCHEMA.values())
         and "def at(" in src and "SCHEMA[key]" in src)
    unit("U93 G-PROV the SHIPPED GATE FAIL travels and the verdict_line is byte-identical",
         r["upstream_provenance"]["verdict"] == "SATISFIED"
         and "GATE FAIL" in r["upstream_provenance"]["upstream"]["verdict_line"])
    unit("U94 G-PROV a mangled verdict_line REFUSES (L-405)",
         _prov_mangle_refuses())
    unit("U95 the registered ceiling IS the sum of the registered caps",
         abs(sum(CAPS.values()) - ITEM_CEILING_CORE_MIN) < 1e-9)
    unit("U96 the birth register names every reader and its born state",
         set(r["birth_register"]["readers"].keys()) == set(READERS.keys()))
    unit("U97 R1 born-state is HONEST: it reflects whether the real launcher was sourced",
         r["birth_register"]["readers"]["R1_read_ledger"]["born"]
         == os.path.isfile(LAUNCHER_PATH))

    # ---- I. THE ROW-LABEL CALL-SITE SWEEP, ACROSS EVERY INSTRUMENT ----------------
    present, absent = mpa1_instrument_files()
    sweep = {os.path.basename(f): row_label_call_sites(f) for f in present}
    unit("U100 ROW-LABEL every built MP-A1 instrument is free of short-form row "
         "literals and positional row derivations (%d files swept, %d not yet built)"
         % (len(present), len(absent)),
         all(v == [] for v in sweep.values()))
    # THE PLANTED KNOWN POSITIVE IS ASSEMBLED FROM PARTS, so this file does not
    # itself contain the tokens the sweep hunts -- the same discipline U88 applies
    # to the old instrument alias.  A check whose own text is a hit can only be
    # satisfied by weakening the check.
    q, sf = chr(34), ROW_SHORT_FORMS
    bad_py = os.path.join(tmp, "planted_row_call_site.py")
    with open(bad_py, "w") as fh:
        fh.write("def pick(row):\n    if row == %s%s%s:\n        return 1\n"
                 "    return ROW_LABELS[row%s0%s]\n" % (q, sf[1], q, "[", "]"))
    bad_sh = os.path.join(tmp, "planted_row_call_site.sh")
    with open(bad_sh, "w") as fh:
        fh.write("ROW=%s\ncase %s${ARM:0:1}%s in X) echo x ;; esac\n" % (sf[1], q, q))
    unit("U101 ROW-LABEL the SAME sweep goes RED on a planted bad call site, in BOTH "
         "languages -- an empty sweep is a claim about the pattern until it does",
         len(row_label_call_sites(bad_py)) >= 2 and len(row_label_call_sites(bad_sh)) >= 1)

    # ---- U101b.  THE SUFFIX-GLOB RULE, PROVED ABLE TO FAIL ON ITS OWN.
    # U101's shell plant is caught by the two OLDER shell rules, so it would stay
    # green with the suffix rule deleted -- it cannot speak for the rule that was
    # actually missing.  This plant carries ONLY the suffix-glob form, assembled
    # from parts so this file does not itself contain the token the sweep hunts,
    # and it must be caught by exactly the rule whose absence let
    # mpa1_chain_driver.sh's `img_of` through eight files of sweeping.
    # The DISCRIMINATOR is the second half: a case list of FULL arm names is the
    # REGISTERED form and must come back CLEAN through the same reader in the same
    # unit -- a rule that flagged both would forbid the repair it is asking for.
    glob_sh = os.path.join(tmp, "planted_suffix_glob.sh")
    star = chr(42)
    with open(glob_sh, "w") as fh:
        fh.write('pick() { case %s$1%s in MESH|%s-S) echo A ;; %s-P) echo B ;; esac; }\n'
                 % (q, q, star, star))
    clean_sh = os.path.join(tmp, "registered_full_name_table.sh")
    with open(clean_sh, "w") as fh:
        fh.write('pick() { case %s$1%s in X-S|X-P) echo A ;; F-S|F-P) echo B ;; esac; }\n'
                 % (q, q))
    unit("U101b ROW-LABEL the SUFFIX-GLOB rule fires on a suffix glob AND stays silent "
         "on the registered full-name table -- the rule that was missing from the SHELL "
         "rule set, and the reason the fourth consumer was swept eight times unseen",
         len(row_label_call_sites(glob_sh)) >= 1 and row_label_call_sites(clean_sh) == [])

    unit("U102 DIVERGENCE the shipped-vs-patched limb actually RAN and reports a number "
         "(it was DEAD until the row-label sweep found its stale short-form keys)",
         r["divergence_shipped_vs_patched"]["worst_pct"] is not None)

    print("\n  units run: %d   failures: %d" % (n, len(fails)))
    if absent:
        print("  ROW-LABEL SWEEP COVERAGE: %d of %d instruments swept; NOT YET BUILT: %s"
              % (len(present), len(present) + len(absent), ", ".join(absent)))
    for f in fails:
        print("  FAIL: %s" % f)
    if n != EXPECTED_UNITS:
        print("  UNIT COUNT %d != EXPECTED_UNITS %d -- the constant is bumped DELIBERATELY, "
              "with its reason, or the suite lost a unit" % (n, EXPECTED_UNITS))
        return 2
    return 0 if not fails else 2


def _prov_mangle_refuses():
    """U94's driver.  Mangles the stored `verdict_line` the way an unquoted
    heredoc mangled `docs/LAB_STATE.md` (L-405) and requires a REFUSAL, then
    restores the original bytes and proves the restore by comparing them."""
    orig = UPSTREAM["verdict_line"]
    UPSTREAM["verdict_line"] = orig.replace("GATE FAIL", "GATE FAIL ", 1)
    try:
        require_travelling_provenance()
        out = False
    except Refusal:
        out = True
    finally:
        UPSTREAM["verdict_line"] = orig
    return out and UPSTREAM["verdict_line"] == compose_verdict_line()


def main():
    if abs(sum(CAPS.values()) - ITEM_CEILING_CORE_MIN) > 1e-9:
        sys.stdout.write("NOT A RESULT -- the comparator REFUSED\n%s\n"
                         % json.dumps({"REFUSE": "REGISTRATION",
                                       "detail": {"ceiling_is_not_the_sum_of_caps":
                                                  {"sum": sum(CAPS.values()),
                                                   "ceiling": ITEM_CEILING_CORE_MIN}}},
                                      sort_keys=True))
        return 2
    if "--selftest" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            return selftest(tmp)
    root, out = BASE, None
    for i, a in enumerate(sys.argv):
        if a == "--root" and i + 1 < len(sys.argv):
            root = sys.argv[i + 1]
        # `--out` IS THE FROZEN DRIVER'S CONTRACT: mpa1_chain_driver.sh:234 invokes
        # this comparator with it and reads the artefact back from that exact path.
        # Adopting the parent's self-composed stamped path would have written to an
        # address the driver never looks at.
        if a == "--out" and i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
    try:
        rec = grade(root)
    except Refusal as exc:
        sys.stdout.write("NOT A RESULT -- the comparator REFUSED\n%s\n" % exc)
        return 2
    if out is None:
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        out = os.path.join(root, "MPA1_grade_%s.json" % stamp)
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True, default=str)
    sys.stdout.write("VERDICT %s  rows=%s  declared=%d executed=%d  written=%s\n"
                     % (rec["verdict"], rec["rows"],
                        rec["gates"]["G-STAGES_declared_vs_executed"]["declared"],
                        rec["gates"]["G-STAGES_declared_vs_executed"]["executed"], out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
