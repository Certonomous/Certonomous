#!/usr/bin/env python3
"""Curriculum D6RF4 -- THE FROZEN GRADING PATH for `P_conv`.

DERIVED FROM `curriculum_D6RF3/d6rf3_grade.py`
(md5 `639d23c4cfea45187561604001c21b44`, 87,818 bytes, re-hashed on disk before
this file was written).  The deltas are in `d6rf4_grade_DELTAS_from_d6rf3.diff`
beside this file, with the rename stripped out in
`d6rf4_grade_SUBSTANTIVE_after_rename.diff`.  THERE ARE SEVEN MECHANISMS, all
registered in `PREREGISTRATION.md` before compute:

  N1  `ACCEPT_FLOOR_UNMOVED` (section 7 instrument 4).  `d6rf4_accept_floor_
      control.py` is IMPORTED, not re-implemented, and the grading REFUSES
      (exit 2) unless `primalMinResTol` and `primalMinResTolDiff`, read back
      out of the arm's OWN container log, are exactly `1e-08` and `1000` and
      their product is exactly the registered accept floor `1.0e-05`.  IT
      REFUSES IN BOTH DIRECTIONS -- a tightened floor refuses too -- because
      the registered value is a value and not an inequality.  Whether a
      successor may ever register a different acceptance rule is ESCALATED TO
      SANAA AND UNRULED; this file makes that boundary executable instead of
      merely stated.

  N2  `G-CONV` (section 3.1), NEW AND GATED.  Per field, per point-primal, per
      leg: the final-iteration `initRes` of every field in `{U0, U1, U2, he,
      p, nuTilda}` against `1.0e-05`.  The threshold is the INHERITED accept
      floor RESTATED, not a new bar and not a moved one.  Per FIELD and never
      on `primalMaxRes` alone, because `D6RF3` had TWO fields over the floor
      (`p` at 1.3162x and `nuTilda` at 1.0504x) and a maximum names neither.

  N3  `G-SOLN` (section 3.2), NEW AND GATED.  The anti-cheat gate: the
      tightened `cl04` baseline's `CD` and `CL` against `D6RF3`'s MEASURED
      `0.0184758685` / `0.3999751808` at `1.0e-03` relative.  A GATE FAIL here
      says the `fvSolution` change MOVED THE SOLUTION rather than converging
      it, and then no `G-CONV` PASS may be quoted as `D6RF3`'s answer.

  N4  `D6RF4-DEF-7` (section 4), the `X-CDLOG` TOKEN GAP.  The parent's only
      absent-source branch read `ARM_DID_NOT_RUN` -- and the arm HAD run, for
      2.067 core-min.  ONE TOKEN FOR TWO STATES.  Three distinguishable tokens
      are registered here, including `ARM_RAN_ARTEFACT_NOT_WRITTEN`, and the
      same repair is applied to EVERY no-input branch in this file through
      `_no_input_reason`, so the class is closed rather than the instance.

  N5  `D6RF4-DEF-8` (section 5), THE NULL READING OF EVERY RUN-DERIVED BAR.
      `NULL_READINGS` registers, for each run-derived falsifier and gate, the
      token it reads as when its producing leg does not run, the leg's name
      and the artefact the token names.  `freeze_check` ASSERTS the table
      covers every run-derived quantity this file grades, so a quantity added
      later without a registered null reading refuses AT FREEZE rather than at
      grading.  `UNRESOLVED` naming its missing producer is honest; a bare
      `null` is silence.

  N6  Section 12.4's REGISTERED REPORT, inherited from `D6RF3` and now
      EXECUTABLE: every component's measured `plateau_pct` is printed BESIDE
      the 10 % bar with its clearance factor, and the record STATES WHETHER
      THE BAR WAS EXERCISED AT ALL.  Measured 2026-09-05: a 10 % bar admits a
      step carrying 7.931 % adjoint error, so a pass orders of magnitude
      inside it carries no information and the record must say so.

  N7  ONE REGISTERED ARM.  `F_mp` and `REF_off` are NOT REGISTERED at this
      freeze and are not priced here; every gate whose input they produce
      reads `NOT A RESULT` for want of an input, under its own registered
      token `ARM_NOT_REGISTERED_AT_THIS_FREEZE` and never under a token that
      reads as a failure.

INHERITED FROM `curriculum_D6RF2/d6rf2_grade.py` THROUGH `D6RF3`
(md5 `32a539780e34fe6d7945b7e301badc0f`, 43,462 bytes, re-hashed on disk before
this file was written).  The deltas are in
`d6rf4_grade_DELTAS_from_d6rf2.diff` beside this file and there are SIX
mechanisms in them, all registered in `PREREGISTRATION.md` before compute:

  M1  `CD_i(mp)` HAS A NEW SOURCE (section 2a).  `gate_off` and `gate_price`
      no longer read `hist["CD_<pt>"][-1]`.  `D6RF3-DEF-4` established BY
      COMPLETE ENUMERATION of the registered `OptView.hst` (md5
      `70fafa07bdee618fef13039433c01114`; 1,013 rows, 1,007 iteration records,
      863 carrying `funcs`) that **the file contains no `CD` at all**.  The
      source is now the FD arm's own `baseline` primal, which already measured
      it -- zero marginal core-minutes -- and every row carries
      `CD_mp_source = FD_BASELINE_PRIMAL`.
  M2  THE SECTION 3f FINITENESS CLAUSE, `D6RF3-DEF-5`'s repair.  The parent
      carried **zero** finiteness guards in 43,462 bytes.  `NaN < 0.0` is
      False, so its registered `negative -> NOT A RESULT` limb did not fire;
      `NaN <= 1.0e-3` is False, so the PASS limb did not fire; control reached
      `else` -> **`GATE FAIL`**.  With `cd_mp = NaN`, `cd_mp <= cd_ref` is also
      False -> `GATE FAIL` on all three off-design points.  **Four gated rows
      manufactured from a non-number, and nothing in the item would have said
      so.**  Every value read from an artefact and compared against a threshold
      now goes through `_ff`, which raises `NonFinite` naming the artefact, the
      key and the token as read.  STRICTLY RESTRICTIVE: it can only turn a PASS
      or GATE FAIL INTO a NOT A RESULT.
  M3  A THIRD PLANTED-ZERO CONTROL (section 3e), because the source moved: the
      CD reader.  Its reader is IMPORTED from `d6rf4_cd_plant_control.py` and
      is the same function the gates call.  All three controls now report one
      of `EXERCISED-PASS` / `EXERCISED-FAIL` / `NOT EXERCISED`, printed beside
      the verdict, never counted as a pass and never inferred from the absence
      of a failure.
  M4  `X-CDLOG` (section 3d), REPORTED AND GATED BY NOTHING: the per-point
      difference between the FD baseline CD and the stdout-recovered CD of the
      last finite major, with the composite-identity residual beside it.  NO
      THRESHOLD.  NO VERDICT.  IT MOVES NOTHING.
  M5  `PRODUCT_WRITER` and `cap_reachability`, two executable checks that
      would each have caught a real defect in a frozen set of this lineage.
  M6  The section 3g ladder gains a rung: non-finite input sits at rung 3,
      ABOVE the G-DVL and pathology rungs.

WHAT THE PLATEAU SAYS, AND WHAT IT DOES NOT.  The `s_lo`/`s_hi` pair IS
`VERIFICATION_CHARTER.md:854-855` step 1's "two or three point mini-sweep", and
`DAFOAM_CHARTER.md` section 20 (addendum 2026-09-04) rules that this SATISFIES
section 3.  **No shortfall caveat is printed and none is owed**; writing "no
plateau proof is claimed" would be a false self-deprecation, which is a
misstatement in the modest direction and still a misstatement.  What IS printed
per component is that the pair is ONE-SIDED by construction -- graded at `s_hi`
with its only neighbour below -- with the family's measured instance of the
blind side firing (D16 `shape[6]`, 14.0978 % coarse against 1.1268 % fine).

THIS ITEM SHIPS ONE ROW.  `DAFOAM_CHARTER.md` section 6 wants two.  The PATCHED
row is bought; the SHIPPED row is NOT bought and is PRICED anyway at 155.70
core-min, on the artefact's own face, because an unbought row that is priced can
be bought by a successor and an unbought row that is unpriced quietly becomes
never.

NO `assert` STATEMENT APPEARS IN THIS FILE.  `python -O` deletes them.

This file IS the grading path fixed at the pre-registration commit
(`CLAUDE.md` rule 2).  Its md5 is pinned in `PREREGISTRATION.md` section 7 and
in the queue row; it verifies at execution that its own bytes on disk equal the
committed blob at HEAD, and it REFUSES (exit 2) if they do not.

VOCABULARY.  `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` and
no other word (`CLAUDE.md` rule 1).  `GATE REACHED` is DELIBERATELY ABSENT: it
labels an optimiser stopped by a wall clock, an iteration cap or a budget
(`DAFOAM_CHARTER.md` section 9), and THIS ITEM RUNS NO OPTIMISER.  A word that
can never fire is not registered.

REFUSES RATHER THAN DEGRADES (exit 2), as this family's comparators do.

THE PLANTED-ZERO CONTROLS (`CLAUDE.md` rule 3) are not optional decoration and
are not skippable: `G-FD` and `G-PRICE` each plant a known perturbation into a
COPY of the artefact they read, read it back FROM DISK through the SAME reader,
and REFUSE if the reader cannot see it.  Both also assert the unperturbed
original is byte-unchanged.  A zero -- or an agreement -- from a reader not
shown able to see a non-zero is not evidence.

L-342 FIELD CLASSES.  Absent INFRASTRUCTURE (a delivered-cores sample, a
container kernel clock) is reported `NOT_MEASURED` beside the verdict and voids
only the claim that depends on it.  Absent PHYSICS (a log, an rc, a registered
artefact whose producing arm ran) REFUSES.  Bookkeeping never voids physics.
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys

# ============================ REGISTERED CONSTANTS ==========================
# Every value in this block is frozen by PREREGISTRATION.md before compute.
ITEM = "D6RF4"
# ONE ARM AT THIS FREEZE (PREREGISTRATION.md section 8.2).  The reason is
# arithmetic, not caution: the full FD arm prices at 934 core-min at the
# tightened settings, and it is not defensible to buy a 934 core-min arm to
# learn a 17.9 core-min fact.
ARMS = ["P_conv"]
ARM_KIND = {"P_conv": "SOLVER", "F_mp": "SOLVER", "REF_off": "SCRIPT"}
# NAME MAP ONLY.  `ARMS` is what this item REGISTERS and buys; `ARM_DIR` is
# what a directory would be CALLED if it existed.  The two unregistered rows
# are kept so a gate that has no input can still NAME the path it would have
# read, and so the section 3f mutation harness can exercise the finiteness
# fold on gates whose arm this freeze does not buy.  Membership of `ARM_DIR`
# grants nothing: `ARMS` is the only list `compose`, `gate_g1`, `gate_caps`
# and the cap arithmetic iterate.
ARM_DIR = {"P_conv": "P_conv", "F_mp": "F_mp", "REF_off": "REF_off"}
# NAMED, NOT SILENT.  These are D6RF3's arms.  They are NOT registered here,
# they buy nothing here, and every gate they would have fed reads NOT A RESULT
# for want of an input under its OWN token -- never under `ARM_DID_NOT_RUN`,
# which is a claim about a registered arm that failed to start.
ARMS_NOT_REGISTERED_AT_THIS_FREEZE = ("F_mp", "REF_off")
NOT_REGISTERED_STATE = "NOT_REGISTERED_AT_THIS_FREEZE"
NOT_REGISTERED_REASON = "ARM_NOT_REGISTERED_AT_THIS_FREEZE"
ARM_RAN_ARTEFACT_NOT_WRITTEN = "ARM_RAN_ARTEFACT_NOT_WRITTEN"

RANKS = 4
CAPS = {"P_conv": 54.00}
TMO = {"P_conv": 720}
FRAME_ALLOWANCE_S = 90
KILL_GRACE_S = 60
FRAME_GAP_ALLOWANCE_S = FRAME_ALLOWANCE_S - KILL_GRACE_S      # 30
CAP_INVERSION_TOL_CORE_MIN = 0.02

CPUSET = "2,3,4,14"
DELIVERED_MIN = 3.0
MEMORY = "20g"

DIGEST_PATCHED = ("sha256:2927768a16acdea0330180fff95c8879"
                  "c1dda9efcf6028728523b7dee30f6d35")
DIGEST_SHIPPED = ("sha256:9d45679d55fd47f5ca7afd99cabb86c7"
                  "c2729cf2acf34c438eb33af5290f07fc")     # NAMED UNBOUGHT
IDWARP_SO_MD5 = "85f59e87253e0a71a813f64ca6e4c425"

# FD bright line -- band D, inherited BY CITATION from D6R PREREGISTRATION.md
# section 3e (VERIFICATION_CHARTER.md section 7 through D6 section 3 and
# DAFOAM_CHARTER.md section 2).  NOT re-derived here.
FD_BAND_PCT = 5.0
AGG_BAND_PCT = 5.0
PLATEAU_TOL_PCT = 10.0
SIGN_FLIP_PATHOLOGY = 2

# D4's PATCHED single-point optimum, re-read from ITS OWN artefact and refused
# if it has moved.
CD_F_D4_RECORDED = 2.1125978108239574e-02
D4_OPT_IPOPT = ("/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/"
                "O/opt_IPOPT.txt")
PRICE_BAND = (0.0, 1.0e-3)

# REPORTED, NOT GATED (Sanaa 2026-09-03 ~20:00Z): the composite reduction is a
# number about an optimisation that exited on a non-finite objective.
RED_BAND_PCT = (15.0, 40.0)

POINTS = ["cl04", "cl05", "cl06"]
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}

PLANT = 1.234e-03                    # the planted-zero perturbation, registered
PLANT_REL_TOL = 1.0e-9

# ---------------------- section 2a: WHERE CD_i(mp) COMES FROM ---------------
# The gated source, FIXED BEFORE COMPUTE.  `d6rf4_major_history.json` is NOT
# the source and CANNOT be: D6RF3-DEF-4 enumerated the producing history
# COMPLETELY (OptView.hst md5 70fafa07bdee618fef13039433c01114; 1,013 rows,
# 1,007 iteration records, 863 carrying `funcs`) and found NO CD in any
# structure of any record.  A file that cannot contain the quantity is not a
# source for it.
CD_ARTEFACT = "d6rf4_fd_endpoint.json"
CD_JSON_PATH = ("points", "<pt>", "CD")     # section 2a's registered path
CD_MP_SOURCE_LABEL = "FD_BASELINE_PRIMAL"
CD_MP_SOURCE_STATEMENT = (
    "CD_i(mp) is prob.get_val('<pt>.aero_post.CD') in the `baseline` primal of "
    "d6rf4_fd_endpoint.py, at the endpoint design vector reconstructed to "
    "PHYSICAL units. It is NOT D6RF section 0a's `last accepted major of a "
    "failed optimisation`; the two agree only to primal convergence and THIS "
    "ITEM MAKES NO CLAIM THAT THEY ARE THE SAME NUMBER. No result of this item "
    "may be compared to a D6R- or D6RF-era CD_i(mp) without this label "
    "travelling with the number (DAFOAM_CHARTER.md section 18.6 refinement 2).")

# ---------------- section 3f: THE FINITENESS CLAUSE, D6RF3-DEF-5's repair ----
# `d6rf2_grade.py` carried ZERO finiteness guards in 43,462 bytes (measured).
# `NaN < 0.0` is False, so the registered `negative -> NOT A RESULT` limb did
# NOT fire and control fell through to GATE FAIL; `NaN <= cd_ref` is False, so
# all three off-design points read GATE FAIL.  FOUR GATED ROWS MANUFACTURED
# FROM A NON-NUMBER.  Registered before compute; STRICTLY RESTRICTIVE -- it can
# only turn a PASS or GATE FAIL INTO a NOT A RESULT, never the reverse.
NON_FINITE_REASON = "NON_FINITE_INPUT"
# The clause's binding list.  Section 3f as drafted registered FIVE; the
# dafoam-supervisor WIDENED it to SEVEN on 2026-09-05, BEFORE the freeze, on
# the ground that `G-CAPS` and `G1` carry `D6RF3-DEF-5`'s identical shape one
# gate over: both parse ledger floats through `_f` with a `"nan"` default, and
# `nan <= cap` is False, so a malformed `core_min` field would have produced a
# CONFIDENT WRONG `GATE FAIL` rather than an honest `NOT A RESULT`.
#
# THE WIDENING IS LEGAL AND IT IS RECORDED AS A WIDENING.  Rule 2 permits
# amendment BEFORE first compute and requires the condition be stated and
# checked: the run root
# `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-multipoint-fd` was
# asserted ABSENT BY EXECUTION on 2026-09-05, and this item has burned 0
# core-min.  After first compute it could not have been widened at all.
#
# IT ONLY EVER ADDS REFUSALS.  A finiteness check can turn a PASS or a GATE
# FAIL INTO a NOT A RESULT and can do nothing else; it cannot move any row
# toward PASS, so it is not a gate loosened to fit an answer.
FINITENESS_BINDS = ("G-OFF", "G-PRICE", "G-FD", "G-DVL", "R-RED",
                    "G-CAPS", "G1")
FINITENESS_BINDS_AS_DRAFTED = ("G-OFF", "G-PRICE", "G-FD", "G-DVL", "R-RED")
FINITENESS_WIDENED_TO = ("G-CAPS", "G1")

# ------- section 2b / 3d: X-CDLOG, REPORTED AND GATED BY NOTHING ------------
# The three CD recovered from D6R's O_mp stdout at the LAST FINITE MAJOR
# (history row 998), matched to that row by CL.  Registered here as CONSTANTS
# rather than re-derived at grading time, because re-deriving them means
# re-scanning a 262k-line log and the numbers are already fixed by section 2b.
CDLOG = {"cl04": 1.846929883e-02, "cl05": 2.176156349e-02, "cl06": 2.696277508e-02}
CDLOG_LINES = {"cl04": 262185, "cl05": 262411, "cl06": 261901}
CDLOG_SOURCE = ("/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-"
                "multipoint/O_mp -- stdout of the producing optimisation")
CDLOG_J_AT_ROW_998 = 0.022238800232340834
CDLOG_COMPOSITE_RESID_ABS = 9.840833e-12       # sum(w_i*CD_i) - J, recomputed
CDLOG_COMPOSITE_RESID_REL = 4.425074e-10

# ---------------- DAFOAM_CHARTER.md section 6: TWO ROWS OR IT IS NOT A -----
# ---------------- VERDICT.  THIS ITEM BUYS ONE, AND PRICES THE OTHER. -------
ROW_BOUGHT = "PATCHED"
ROW_NOT_BOUGHT = "SHIPPED"
# An unbought row that is PRICED can be bought by a successor; an unbought row
# that is UNPRICED quietly becomes never.  This is `F_mp`'s own estimate: a
# SHIPPED row is the same arm on stock IDWarp at the same cap.
SHIPPED_ROW_PRICE_CORE_MIN = 155.70
PREDICTED_CORE_MIN = {"P_conv": 17.90}

# ---- DAFOAM_CHARTER.md section 18.3, applied to PRODUCTS as well as to -----
# ---- instruments.  D6RF3-DEF-6: in the frozen D6RF2 set the grader, the -----
# ---- launcher and the writer disagreed on the name of a registered product.
LAUNCHER = "d6rf4_run_arm.sh"
PRODUCT_WRITER = {
    "d6rf4_endpoint_dvs_PHYSICAL.json": "d6rf4_endpoint_physical.py",
    "d6rf4_endpoint_dvs_DRIVERSCALED.json": "d6rf4_endpoint_physical.py",
    "d6rf4_endpoint_dvs.json": "d6rf4_extract_endpoint.py",
    "d6rf4_major_history.json": "d6rf4_extract_endpoint.py",
    "d6rf4_fd_endpoint.json": "d6rf4_fd_endpoint.py",
    "d6rf4_f5_endpoint.json": "d6rf4_fd_endpoint.py",
}

REGISTERED_CHAIN_OUTCOMES = ("STOPPED_AT_FIRST_NONZERO", "STOPPED_H5",
                             "BLOCKED_H5", "BLOCKED_AGGREGATE",
                             "REFUSED_ALREADY_BOUGHT", "ABORT")

ARTEFACT_PRODUCER = {
    "d6rf4_endpoint_dvs_PHYSICAL.json": "P_conv",
    "d6rf4_endpoint_dvs_DRIVERSCALED.json": "P_conv",
    "d6rf4_endpoint_dvs.json": "P_conv",
    "d6rf4_major_history.json": "P_conv",
    "d6rf4_fd_endpoint.json": "P_conv",
    "d6rf4_f5_endpoint.json": "P_conv",
    # NOT REGISTERED AT THIS FREEZE.  Kept in the map ON PURPOSE: deleting the
    # row would make the gates that read them silently disappear, and a gate
    # that vanishes is worse than one that reads NOT A RESULT with its reason
    # printed.  The census gives these arms their own state and their own
    # token (section 3.3, section 9 item 6).
    "d4_endpoint_dvs_PHYSICAL.json": "REF_off",
    "d4_endpoint_dvs.json": "REF_off",
    "d6rf4_ref_off.json": "REF_off",
}
REGISTERED_PRODUCTS = {
    "P_conv": ["d6rf4_endpoint_dvs_PHYSICAL.json", "d6rf4_endpoint_dvs_DRIVERSCALED.json",
               "d6rf4_endpoint_dvs.json", "d6rf4_major_history.json",
               "d6rf4_fd_endpoint.json", "d6rf4_f5_endpoint.json"],
}
TERMINAL_STATEMENT = "Finalising parallel run"

# ==================== section 3.1: G-CONV, NEW AND GATED ====================
# THE BAR IS THE INHERITED ACCEPT FLOOR, RESTATED, NOT MOVED.  It is imported
# from `d6rf4_accept_floor_control` rather than re-declared, so this file and
# the instrument that refuses on drift cannot disagree about what the floor is.
# `N-D43`: the floor is the PRODUCT `primalMinResTol x primalMinResTolDiff`,
# never the tolerance alone -- the wrong denominator was reported twice before
# a lane caught it, and 1316x versus 1.3162x point at opposite successors.
#
# PER FIELD, NEVER ON `primalMaxRes` ALONE.  D6RF3 had TWO fields over the
# floor -- `p` at 1.3162x AND `nuTilda` at 1.0504x -- and a maximum names
# neither, so a repair that fixed only `p` would still have failed and the
# record would not have said why.
CONV_FIELDS = ("U0", "U1", "U2", "he", "p", "nuTilda")
CONV_MEASURED_D6RF3 = {          # the parent's OWN measured final-iteration
    "U0": 1.381819607e-07,       # initRes, log :2088-:2096, Time = 1000
    "U1": 5.862105833e-07,
    "U2": 3.746855799e-08,
    "he": 7.03533873e-09,
    "p": 1.316217833e-05,        # the binding field, 1.3162x the floor
    "nuTilda": 1.050443706e-05,  # the SECOND binding field, 1.0504x the floor
}
PRIMAL_FAILURE_BANNER = "Primal solution failed!"

# ==================== section 3.2: G-SOLN, NEW AND GATED ====================
# THE ANTI-CHEAT GATE.  A different `fvSolution` could compute a different
# ANSWER rather than a better-converged one; `N-D42` establishes that
# `primalMinResTolDiff` changes only the LABEL, and no such result exists for
# a linear-solver stopping rule.  So it is measured instead of assumed.
# D6RF3's own values, MEASURED, log :2098-:2099 at Time = 1000.
G_SOLN_POINT = "cl04"
G_SOLN_CD_D6RF3 = 0.0184758685
G_SOLN_CL_D6RF3 = 0.3999751808
G_SOLN_REL_TOL = 1.0e-03
# Predicted: the two solutions differ by the residual level, O(1e-05) relative.
# 1e-05 < 1e-03 -- predicted PASS with two decades of margin.  Written down
# because a gate whose predicted value nobody wrote down is a gate nobody sized.
G_SOLN_PREDICTED_REL = 1.0e-05

# ====================== section 8.2: THE THREE LEGS =========================
# The arm runs ONE container and three legs inside it.  `d6rf4_fd_endpoint.py`
# prints `D6RF4_LEG_BEGIN`/`D6RF4_LEG_END` markers, which is how one container
# log is split into per-leg segments.  Without a marker the three legs are one
# undifferentiated log and NO PER-LEG NUMBER CAN BE CITED.
LEG_BEGIN = "D6RF4_LEG_BEGIN"
LEG_END = "D6RF4_LEG_END"
LEGS = ("L1", "L2", "L3")
LEG_TAG = {"L1": "baseline", "L2": "baseline_repeat", "L3": "baseline"}
LEG_MODE = {"L1": "P_conv", "L2": "P_conv", "L3": "F5_loose"}
LEG_FVSOLUTION = {"L1": "d6rf4_fvSolution_TIGHT",
                  "L2": "d6rf4_fvSolution_TIGHT",
                  "L3": "d6rf4_fvSolution_D6RF3_ORIGINAL"}
# THE BYTES EACH LEG IS REGISTERED TO RUN.  The launcher installs the file and
# PRINTS `D6RF4_FVSOLUTION_INSTALLED leg=<L> md5=<m> sites=<n>` into the log;
# this is what lets the grader ASSERT that L1 ran the tightened rule and L3 ran
# D6RF3's original one, instead of taking the launcher's word for it.
# WITHOUT THIS CHECK THE WHOLE ITEM IS UNFALSIFIABLE: a swap that silently
# failed would run L3 at the TIGHT settings, F5 would "fail to fail" for a
# bookkeeping reason, and its withdrawal clause would never fire.
FVSOL_MD5 = {"d6rf4_fvSolution_TIGHT": "0ac5bd00c63b9109d22a8e73b0795aa4",
             "d6rf4_fvSolution_D6RF3_ORIGINAL": "9e2669956be778acf7e7d8aa67a90ff6"}
FVSOL_INSTALL_MARKER = "D6RF4_FVSOLUTION_INSTALLED"
LEG_INSTALL_TAG = {"L1": "L1_L2", "L2": "L1_L2", "L3": "L3"}
# THE MODES REGISTERED TO TAKE NO FD STEP.  A product written by one of these
# is EMPTY BY REGISTRATION, and the rule-3 FD control over it is NOT EXERCISED
# rather than refused.  `full` is deliberately ABSENT from this set: a `full`
# arm with an empty product is a broken FD arm and must still refuse.
NO_FD_MODES = ("P_conv", "F5_loose")
LEG_ROLE = {"L1": "the tightened cl04 baseline -- G-CONV's and G-SOLN's subject",
            "L2": "the tightened cl04 baseline_repeat -- it BUYS eta_raw, "
                  "which is falsifier F1's bar (D6RF4-DEF-8 repair part 1)",
            "L3": "falsifier F5: the identical primal at D6RF3's ORIGINAL "
                  "fvSolution, predicted p initRes 1.3162e-05 > G-CONV's own "
                  "bar 1.0e-05, i.e. bound to FAIL its named gate at zero "
                  "compute (DAFOAM_CHARTER.md section 21.3)"}
F5_LEG = "L3"
F5_PREDICTED_P_INITRES = 1.316217833e-05
F5_NAMED_GATE = "G-CONV"

# ============ section 5: D6RF4-DEF-8, THE REGISTERED NULL READINGS ==========
# EVERY run-derived falsifier and gate declares, HERE, in the frozen file,
# exactly what it reads as when its producing leg does not run: the token, the
# field name and the artefact the token names.  `freeze_check` asserts this
# table covers every run-derived quantity this file grades, so a quantity added
# later WITHOUT a registered null reading refuses AT FREEZE rather than at
# grading.  `UNRESOLVED` naming its missing producer is honest; a bare `null`
# is silence.
BAR_NOT_PRODUCED = "BAR_NOT_PRODUCED"
BAR_PRODUCED = "BAR_PRODUCED"
NULL_READINGS = {
    "F1": {"run_derived_quantity": "eta_raw = |J - J_repeat|",
           "producing_leg": "L2 (baseline_repeat)",
           "token": "UNRESOLVED", "bar_state": BAR_NOT_PRODUCED,
           "bar_artefact": "d6rf4_fd_endpoint.json:eta_raw",
           "gated": False},
    "F3": {"run_derived_quantity": "G-FD aggregate, sign-flip count",
           "producing_leg": "the FD legs (NOT REGISTERED at this freeze)",
           "token": "UNRESOLVED", "bar_state": BAR_NOT_PRODUCED,
           "bar_artefact": "d6rf4_fd_endpoint.json:rows",
           "gated": False},
    "F5": {"run_derived_quantity": "per-field final initRes at the WRONG setting",
           "producing_leg": "L3 (F5_loose baseline)",
           "token": "UNRESOLVED", "bar_state": BAR_NOT_PRODUCED,
           "bar_artefact": "the arm log segment between L3's LEG_BEGIN/LEG_END",
           "gated": False},
    "G-CONV": {"run_derived_quantity": "per-field final initRes",
               "producing_leg": "L1 (P_conv tight baseline)",
               "token": "NOT A RESULT", "bar_state": BAR_NOT_PRODUCED,
               "bar_artefact": "the arm log segment between L1's LEG_BEGIN/LEG_END",
               "gated": True},
    "G-SOLN": {"run_derived_quantity": "tightened CD, CL at cl04",
               "producing_leg": "L1 (P_conv tight baseline)",
               "token": "NOT A RESULT", "bar_state": BAR_NOT_PRODUCED,
               "bar_artefact": "d6rf4_fd_endpoint.json:points.cl04.{CD,CL}",
               "gated": True},
    "X-CDLOG": {"run_derived_quantity": "points.<pt>.CD",
                "producing_leg": "L1 (the baseline point-primals)",
                "token": "NOT PRODUCED", "bar_state": BAR_NOT_PRODUCED,
                "bar_artefact": "d6rf4_fd_endpoint.json:points.<pt>.CD",
                "gated": False},
    "R-RED": {"run_derived_quantity": "composite reduction pct",
              "producing_leg": "the optimiser history (NOT REGISTERED here)",
              "token": "UNRESOLVED", "bar_state": BAR_NOT_PRODUCED,
              "bar_artefact": "d6rf4_major_history.json",
              "gated": False},
    "G-FD": {"run_derived_quantity": "per-component rel_err_pct, plateau_pct",
             "producing_leg": "the FD legs (NOT REGISTERED at this freeze)",
             "token": "NOT A RESULT", "bar_state": BAR_NOT_PRODUCED,
             "bar_artefact": "d6rf4_fd_endpoint.json:rows",
             "gated": True},
    "G-OFF": {"run_derived_quantity": "CD_REF_off, CL_REF_off",
              "producing_leg": "REF_off (NOT REGISTERED at this freeze)",
              "token": "NOT A RESULT", "bar_state": BAR_NOT_PRODUCED,
              "bar_artefact": "d6rf4_ref_off.json",
              "gated": True},
    "G-PRICE": {"run_derived_quantity": "CD_mp against D4's CD_f",
                "producing_leg": "L1 (the baseline point-primals)",
                "token": "NOT A RESULT", "bar_state": BAR_NOT_PRODUCED,
                "bar_artefact": "d6rf4_fd_endpoint.json:points.cl05.CD",
                "gated": True},
    "G-DVL": {"run_derived_quantity": "the design vector on disk",
              "producing_leg": "L1 (the staging wrapper)",
              "token": "NOT A RESULT", "bar_state": BAR_NOT_PRODUCED,
              "bar_artefact": "d6rf4_endpoint_dvs_PHYSICAL.json",
              "gated": True},
}
# THE COVERAGE ASSERTION'S SUBJECT.  Every name here must have a NULL_READINGS
# row, and `freeze_check` refuses if one does not.  It is the list of things
# this file grades or reports whose value comes OUT OF THE RUN.
RUN_DERIVED = ("F1", "F3", "F5", "G-CONV", "G-SOLN", "X-CDLOG", "R-RED",
               "G-FD", "G-OFF", "G-PRICE", "G-DVL")

# =============== section 12.4: THE PLATEAU BAR'S OWN REPORT =================
# Inherited from D6RF3 and made EXECUTABLE here.  MEASURED 2026-09-05 on
# S1FDP: the 10 % bar ADMITTED a step carrying 7.931 % adjoint error, so a
# component passing orders of magnitude inside the bar carries NO INFORMATION
# about the bar.  A pass on an unexercised bar is not wrong; it is
# uninformative, and the record must say WHICH IT IS
# (DAFOAM_CHARTER.md section 21.5).
PLATEAU_BAR_EXERCISED = "EXERCISED -- the bar rejected at least one component"
PLATEAU_BAR_NOT_EXERCISED = ("NOT EXERCISED -- every graded component sat "
                             "inside the bar, so this bar was never the "
                             "instrument that decided anything here")
PLATEAU_BAR_UNINFORMATIVE_EVIDENCE = (
    "MEASURED, DAFOAM_CHARTER.md section 21.5 and S1FDP 2026-09-05: this same "
    "10 %% bar ADMITTED an h = 0.5 step whose adjoint error was 7.931 %%. A "
    "component clearing it by orders of magnitude therefore says nothing "
    "about the bar, and this record says so rather than reporting a pass that "
    "reads as evidence.")
# ===========================================================================

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir,
                                    os.pardir, os.pardir))

sys.path.insert(0, HERE)
# THE ONE CD READER OF THIS ITEM.  Imported, not re-implemented: the reader the
# section 3e control plants into must be BYTE-FOR-BYTE the reader the gate uses,
# or the control controls nothing.
import d6rf4_cd_plant_control as cdc                               # noqa: E402
# THE ONE ACCEPT-FLOOR READER OF THIS ITEM.  Imported, not re-implemented, for
# the same reason `cdc` is: the control that plants a drift must be planting
# into THE SAME FUNCTION the gate reads through, or the control controls
# nothing.  `freeze_check` asserts the IDENTITY of the imported symbol, not the
# module name (section 7 carried strength 2).
import d6rf4_accept_floor_control as afc                           # noqa: E402

# The accept floor is DEFINED IN ONE PLACE and read from it here, so this file
# and the instrument that refuses on drift cannot disagree about the number.
ACCEPT_FLOOR = afc.ACCEPT_FLOOR                                    # 1.0e-05
CONV_BAR = ACCEPT_FLOOR


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail},
                             sort_keys=True, default=str)[:4000])


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def _f(x):
    """A repr()'d float from an artefact, or a float, or REFUSE."""
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x)
        except ValueError:
            refuse("float_parse", {"value": x[:120]})
    refuse("float_parse", {"type": type(x).__name__})


class NonFinite(Exception):
    """Section 3f.  Raised AT THE POINT OF READING, carrying the artefact, the
    key and the token AS READ -- not a bare flag, because a gate that says
    NON_FINITE_INPUT without naming what it read is not actionable."""

    def __init__(self, artefact, key, token):
        self.detail = {"reason": NON_FINITE_REASON, "artefact": artefact,
                       "key": key, "token_as_read": token}
        Exception.__init__(self, json.dumps(self.detail, sort_keys=True,
                                            default=str))


def _ff(x, artefact, key):
    """THE SECTION 3f READER.  Every value this grader reads from an artefact
    and compares against a threshold goes through here.

    `_f` parses `float('nan')`, `float('inf')` and `float('-inf')` WITHOUT
    COMPLAINT -- that is not a bug in `_f`, it is what `float()` does -- and
    every ordered comparison against a NaN is False, so a NaN silently takes
    the `else` branch of any two-limb test.  D6RF3-DEF-5 is exactly that: the
    endpoint row of the producing history is index 1006, whose `funcs` are ALL
    NaN (687 of 863 `funcs` rows are non-finite), and the parent grader would
    have printed GATE FAIL on four gated rows from it.

    THE REPAIR IS STRICTLY RESTRICTIVE.  Raising here can only turn a PASS or
    a GATE FAIL INTO a NOT A RESULT.  It can never produce a PASS, never
    produce a GATE FAIL, and never rescue a row -- which is `CLAUDE.md` rule
    5's own permitted direction of travel."""
    v = _f(x)
    if not math.isfinite(v):
        raise NonFinite(artefact, key, repr(x) if isinstance(x, str) else v)
    return v


def _nar_non_finite(base, exc):
    """Fold a NonFinite into a gate result.  ALWAYS `NOT A RESULT`, NEVER
    `GATE FAIL` and NEVER `PASS` (section 3f)."""
    out = dict(base)
    out["verdict"] = "NOT A RESULT"
    out["reason"] = NON_FINITE_REASON
    out["non_finite"] = exc.detail
    out["clause"] = ("PREREGISTRATION.md section 3f: a non-finite value makes "
                     "its gate NOT A RESULT naming the artefact, the key and "
                     "the token as read. It is NEVER GATE FAIL and never PASS.")
    return out


def _no_input_reason(census, arm, artefact=None, root=None):
    """`D6RF4-DEF-7`, GENERALISED FROM THE INSTANCE TO THE CLASS.

    The parent had ONE token, `ARM_DID_NOT_RUN`, for what are three different
    states -- and `D6RF3` landed in the one it had no token for: the arm RAN,
    for 2.067 core-min, and the artefact was never written.  The record could
    therefore have read `ARM_DID_NOT_RUN` about an arm that had consumed
    compute, which is a false statement about the run, not merely a vague one.

    THE REPAIR IS APPLIED AT EVERY NO-INPUT BRANCH IN THIS FILE, not only at
    `X-CDLOG`, because a token gap repaired at the site it was found at is a
    repaired instance and an unrepaired class (`CLAUDE.md` rule 14's shape).

    Returns `(reason, detail)`.  The four registered states:
      ARM_NOT_REGISTERED_AT_THIS_FREEZE  the arm is not part of this item
      ARM_DID_NOT_RUN                    a registered arm bought 0 core-min
      ARM_RAN_ARTEFACT_NOT_WRITTEN       the arm RAN and the artefact is absent
      (no reason)                        the artefact is present
    """
    st = census.get(arm) or {"state": "UNKNOWN"}
    detail = {"producing_arm": arm, "arm_state": st}
    if st.get("state") == NOT_REGISTERED_STATE:
        detail["note"] = (
            "`%s` is NOT REGISTERED at this freeze (PREREGISTRATION.md section "
            "8.2). It bought 0 core-min and was never expected to run, so this "
            "gate has NO INPUT. That is NOT a GATE FAIL and NOT an arm that "
            "failed to start -- nothing was measured that could fail." % arm)
        return NOT_REGISTERED_REASON, detail
    if st.get("state") != "RAN":
        detail["note"] = ("the registered arm that writes this artefact did "
                          "not run, so this gate has NO INPUT. That is NOT a "
                          "GATE FAIL -- nothing was measured that could fail.")
        return "ARM_DID_NOT_RUN", detail
    # THE STATE D6RF3 ACTUALLY HIT AND HAD NO TOKEN FOR.
    detail["note"] = (
        "the producing arm RAN and the registered artefact was NOT WRITTEN. "
        "This is D6RF4-DEF-7's own state: D6RF3's arm ran for 2.067 core-min "
        "and its grader had only `ARM_DID_NOT_RUN` to say so with.")
    if artefact is not None:
        detail["artefact"] = artefact
        detail["expected_at"] = (os.path.join(root or "", ARM_DIR.get(arm, arm),
                                              artefact) if root else None)
    return ARM_RAN_ARTEFACT_NOT_WRITTEN, detail


def cap_reachability():
    """THE CAP-versus-DEADLINE REACHABILITY CHECK, run at every grading and
    printable as ARITHMETIC.

    Two independent stopping conditions guard each arm and they are stated in
    DIFFERENT UNITS: `cap_core_min` (core-minutes, rule 12's unit) and `TMO`
    (in-container wall seconds, what `timeout` actually enforces).  If they
    are not reconciled, one of them is decorative:

        cap_wall_equivalent_s = cap_core_min * 60 / ranks
        max_spend_at_TMO_core_min = TMO * ranks / 60

    If `cap_wall_equivalent_s` <= `TMO` the CAP fires first and the deadline
    never runs; if it exceeds `TMO` by more than the frame allowance, the CAP
    IS UNREACHABLE and a cap breach can never be the recorded stopping
    condition -- the run is always killed on the clock instead, and the ledger
    records the wrong reason for the stop.  The registered design here is
    `TMO + FRAME_ALLOWANCE_S == cap_wall_equivalent_s` EXACTLY: the deadline
    bounds the in-container program and the frame allowance is the container
    start/stop outside it, so the two together are the cap and neither is
    decorative.  REFUSES if that identity does not hold."""
    out = {"ranks": RANKS, "frame_allowance_s": FRAME_ALLOWANCE_S, "arms": {}}
    for arm in ARMS:
        cap, tmo = CAPS[arm], TMO[arm]
        cap_wall = cap * 60.0 / RANKS
        max_spend = tmo * RANKS / 60.0
        residual = cap_wall - (tmo + FRAME_ALLOWANCE_S)
        r = {"cap_core_min": cap, "TMO_s": tmo,
             "cap_wall_equivalent_s": cap_wall,
             "TMO_plus_frame_s": tmo + FRAME_ALLOWANCE_S,
             "identity_residual_s": residual,
             "max_spend_at_TMO_core_min": max_spend,
             "cap_headroom_core_min": cap - max_spend,
             "cap_reachable": cap_wall > tmo,
             "predicted_core_min": PREDICTED_CORE_MIN[arm],
             "predicted_over_cap": PREDICTED_CORE_MIN[arm] > cap}
        if abs(residual) > 1.0e-6:
            refuse("CAP_REACHABILITY",
                   dict(r, arm=arm,
                        note="cap_core_min*60/ranks != TMO + frame allowance: "
                             "the cap and the deadline are not reconciled and "
                             "one of them is decorative"))
        if r["predicted_over_cap"]:
            refuse("CAP_REACHABILITY",
                   dict(r, arm=arm, note="the registered estimate exceeds the "
                                         "cap it is registered under"))
        out["arms"][arm] = r
    out["ceiling_core_min"] = sum(CAPS.values())
    out["total_predicted_core_min"] = sum(PREDICTED_CORE_MIN.values())
    return out


# ------------------ DAFOAM_CHARTER.md section 18.3, on PRODUCTS -------------
def product_writer_check():
    """EVERY registered product is asserted to be NAMED, as a literal, in the
    instrument registered as writing it -- existence of the writer asserted
    BEFORE any read of it.

    This exists because `D6RF3-DEF-6` happened in the frozen `D6RF2` set:
    `d6rf2_grade.py:94/:104/:458` and `d6rf2_run_arm.sh:546` registered
    `d6rf2_endpoint_dvs_PHYSICAL.json` while `d6rf2_endpoint_physical.py:75`,
    the only writer, still wrote `D6RF`'s `d6rf_endpoint_dvs_PHYSICAL.json`.
    `gate_g1`'s age guard walks `REGISTERED_PRODUCTS` and refuses
    `registered_product_absent` when the producing arm RAN -- so the item
    would have refused at grading however clean the arms were, and no md5
    freeze over the instrument set could have seen it: every pinned file
    hashed correctly.  Section 18.3's own sentence: these are different
    questions and the second cannot be inferred from the first at any level
    of agreement.

    REFUSES rather than grading, because a product-name disagreement makes
    every downstream reading meaningless rather than merely failing."""
    out = {}
    for arm in ARMS:
        for prod in REGISTERED_PRODUCTS[arm]:
            writer = PRODUCT_WRITER.get(prod)
            if writer is None:
                out[prod] = {"writer": None, "named_by_writer": None,
                             "note": "d4_* products are D4's own instruments, "
                                     "staged unchanged and out of scope"}
                continue
            wpath = os.path.join(HERE, writer)
            if not os.path.isfile(wpath):                 # EXISTENCE FIRST
                refuse("PRODUCT_WRITER", {"product": prod, "writer": writer,
                                          "writer_absent_on_disk": wpath})
            with open(wpath, errors="replace") as fh:
                named = prod in fh.read()
            out[prod] = {"writer": writer, "named_by_writer": named}
            if not named:
                refuse("PRODUCT_WRITER",
                       {"product": prod, "writer": writer,
                        "the_writer_does_not_name_the_product": True,
                        "note": "D6RF3-DEF-6's class. A product registered "
                                "under a name no instrument writes makes G1's "
                                "age guard refuse on a clean run."})
            # ---- THE THIRD SIDE OF THE TRIANGLE --------------------------
            # `D6RF3-DEF-6` was a THREE-way disagreement, not a two-way one:
            # the grader registered a name, the LAUNCHER preserved that name,
            # and only the WRITER disagreed. Checking grader-against-writer
            # alone would have caught it -- but checking the launcher too is
            # what makes the check symmetric, so the defect cannot reappear by
            # moving which of the three is the odd one out.
            lpath = os.path.join(HERE, LAUNCHER)
            if os.path.isfile(lpath):                      # EXISTENCE FIRST
                with open(lpath, errors="replace") as fh:
                    lnamed = prod in fh.read()
                out[prod]["named_by_launcher"] = lnamed
                if not lnamed:
                    refuse("PRODUCT_WRITER",
                           {"product": prod, "launcher": LAUNCHER,
                            "the_launcher_does_not_name_the_product": True,
                            "note": "the launcher stages, cleans and preserves "
                                    "products by name; one it does not name is "
                                    "one it will not clean between fires, "
                                    "which is D6RF-DEF-2's stale-artefact "
                                    "shape"})
            else:
                out[prod]["named_by_launcher"] = "LAUNCHER_ABSENT"
    return out


# ------------------------------------------------------------ freeze check
ITEM_DIR_REL = "cases/dafoam/ladder-a/A2/curriculum_D6RF4"
# EVERY FILE THIS GRADING PATH EXECUTES OR IMPORTS.  `frozen_path_coverage`
# below EXTRACTS that set FROM THIS FILE'S OWN BYTES and REFUSES if this tuple
# does not contain it -- so the tuple is checkable rather than remembered.
# `SO2a-DRIVER-DEF-1` is the reason (DAFOAM_CHARTER.md section 18.3): a gate
# was frozen without its implementation and an md5-agreement control read
# `eight of eight AGREE`, because the eight pins did not include the file the
# driver ran.
FROZEN_PATHS = tuple("%s/%s" % (ITEM_DIR_REL, n) for n in (
    "PREREGISTRATION.md",
    "d6rf4_grade.py",
    "d6rf4_cd_plant_control.py",
    "d6rf4_accept_floor_control.py",
    "d6rf4_endpoint_locus.py",
    "d6rf4_endpoint_physical.py",
    "d6rf4_extract_endpoint.py",
    "d6rf4_fd_endpoint.py",
    "d6rf4_anchor_gate.py",
    "d6rf4_opt_runScript.py",
    "d6rf4_units_assert.py",
    "d6rf4_finiteness_mutation.py",
    "d6rf4_run_arm.sh",
    "d6rf4_fvSolution_TIGHT",
    "d6rf4_fvSolution_D6RF3_ORIGINAL",
))
# CROSS-ITEM DEPENDENCIES, NAMED RATHER THAN EXCLUDED.  `d4_opt_runScript.py`
# is D4's own instrument, staged unchanged and read here as `G-DVL`'s D4-side
# reference.  It lives in another item's directory and is frozen at ITS path;
# excluding it from the extraction because it is "not ours" is exactly how
# SO2a's frozen set lost the file its driver ran.
CROSS_ITEM = {
    "d4_opt_runScript.py":
        "cases/dafoam/ladder-a/A2/curriculum_D4/d4_opt_runScript.py",
    # Opened by d6rf4_anchor_gate.py:167/:177 and d6rf4_endpoint_locus.py:554,
    # in their SELFTEST paths.  A selftest path is still an executed path, and
    # D6RF3's own extraction listed this row for the same reason.
    "d6r_opt_runScript.py":
        "cases/dafoam/ladder-a/A2/curriculum_D6R/d6r_opt_runScript.py",
}
FROZEN_PATHS = FROZEN_PATHS + tuple(CROSS_ITEM.values())


def frozen_path_coverage():
    """DAFOAM_CHARTER.md section 18.3, APPLIED TO THIS FILE BY EXTRACTION.

    Reads THIS FILE'S OWN BYTES with `ast`, collects every LOCAL module it
    imports and every `d6rf4_*` / `d4_*` filename literal it names, and REFUSES
    if any of them is absent from `FROZEN_PATHS` or absent from disk.  EXISTENCE
    IS ASSERTED FIRST AND SEPARATELY, before any md5 -- section 18.3's own
    sentence: an md5-agreement figure over a subset is NOT evidence the set is
    complete, at 8 of 8 or at 800 of 800.

    IT IS THE EXTRACTION AND NOT THE DILIGENCE THAT IS BINDING.  A prose list
    names what its author thought of; a list derived from the code cannot have
    that failure mode."""
    import ast as _ast
    me = os.path.abspath(__file__)
    tree = _ast.parse(open(me, errors="replace").read(), filename=me)
    imported, literals = set(), set()
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            for a in node.names:
                if a.name.startswith(("d6rf4_", "d4_")):
                    imported.add(a.name + ".py")
        elif isinstance(node, _ast.ImportFrom) and node.module:
            if node.module.startswith(("d6rf4_", "d4_")):
                imported.add(node.module + ".py")
        elif isinstance(node, _ast.Constant) and isinstance(node.value, str):
            v = node.value
            if (v.startswith(("d6rf4_", "d4_"))
                    and v.endswith((".py", ".sh"))):
                literals.add(v)
    referenced = sorted(imported | literals)
    frozen_names = {p.rsplit("/", 1)[-1] for p in FROZEN_PATHS}

    def _resolve(n):
        """Item directory first, then the REGISTERED cross-item path.  A file
        found only by an unregistered guess is NOT resolved: it must be named
        in `CROSS_ITEM`, so the set of places this check will look is itself
        frozen."""
        p = os.path.join(HERE, n)
        if os.path.isfile(p):
            return p
        if n in CROSS_ITEM:
            q = os.path.join(REPO, CROSS_ITEM[n])
            if os.path.isfile(q):
                return q
        return None
    out = {"extracted_from": os.path.basename(me),
           "imported_local_modules": sorted(imported),
           "executed_or_named_scripts": sorted(literals),
           "n_referenced": len(referenced)}
    if not referenced:
        refuse("FROZEN_PATH_COVERAGE",
               {"n_referenced": 0,
                "note": "the extraction found NOTHING. A derivation that "
                        "quietly finds nothing is indistinguishable from one "
                        "that found nothing wrong (CLAUDE.md rule 3)."})
    # ---- EXISTENCE FIRST, AND SEPARATELY --------------------------------
    absent = [n for n in referenced if _resolve(n) is None]
    unfrozen = [n for n in referenced if n not in frozen_names]
    out["absent_on_disk"] = absent
    out["referenced_but_not_in_FROZEN_PATHS"] = unfrozen
    if absent or unfrozen:
        refuse("FROZEN_PATH_COVERAGE",
               dict(out, note="section 18.3: a registered gate whose "
                              "implementing file is not in the instrument "
                              "table is not frozen -- it is UNIMPLEMENTED -- "
                              "and the item does not launch."))
    out["resolved_to"] = {n: _resolve(n) for n in referenced}
    out["cross_item"] = dict(CROSS_ITEM)
    out["existence_asserted_before_any_md5"] = True
    out["coverage_complete"] = True
    return out


def null_reading_coverage():
    """`D6RF4-DEF-8`, part 3.  ASSERTED AT FREEZE, NOT AT GRADING.

    Every run-derived falsifier and gate this file grades or reports must have
    a `NULL_READINGS` row naming its token, its producing leg and the artefact
    the token names.  A row absent from that table is a run-derived quantity
    NOBODY REGISTERED A NULL READING FOR, and this refuses on it -- BEFORE any
    compute, which is the whole point.  `UNRESOLVED` naming its missing
    producer is honest; a bare `null` is silence.

    IT ALSO REFUSES ON THE OTHER DIRECTION: a `NULL_READINGS` row for a
    quantity not in `RUN_DERIVED` is a registration for something this file
    does not grade, and a table that has drifted away from the code is not
    evidence about the code."""
    missing = [k for k in RUN_DERIVED if k not in NULL_READINGS]
    extra = [k for k in NULL_READINGS if k not in RUN_DERIVED]
    REQUIRED = ("run_derived_quantity", "producing_leg", "token",
                "bar_state", "bar_artefact")
    incomplete = {k: [f for f in REQUIRED if not NULL_READINGS[k].get(f)]
                  for k in NULL_READINGS
                  if [f for f in REQUIRED if not NULL_READINGS[k].get(f)]}
    if missing or extra or incomplete:
        refuse("NULL_READINGS",
               {"run_derived_without_a_registered_null_reading": missing,
                "registered_but_not_graded_by_this_file": extra,
                "rows_missing_a_required_field": incomplete,
                "required_fields": list(REQUIRED),
                "note": "PREREGISTRATION.md section 5: a row absent from this "
                        "table is a run-derived quantity nobody registered a "
                        "null reading for. UNRESOLVED naming its missing "
                        "producer is honest; a bare null is silence."})
    return {"n_run_derived": len(RUN_DERIVED),
            "n_registered": len(NULL_READINGS),
            "coverage_complete": True,
            "table": NULL_READINGS}


def imported_symbol_identity():
    """Section 7 carried strength 2, MADE EXECUTABLE ON THE SYMBOL.

    The planted controls must plant into THE LITERAL FUNCTION THE GATE CALLS,
    not into a re-implementation of it.  Checking the MODULE NAME would pass on
    a module that had been re-implemented; this asserts that the object the
    gate reads through IS the object the control drives, by identity."""
    import d6rf4_cd_plant_control as _cdc_again
    import d6rf4_accept_floor_control as _afc_again
    checks = {
        "cdc.read_cd is the gate's CD reader":
            cdc.read_cd is _cdc_again.read_cd,
        "cdc.run_cd_control defaults to that same reader":
            (cdc.run_cd_control.__defaults__ or (None,))[0] is cdc.read_cd,
        "afc.read_accept_floor is the gate's accept-floor reader":
            afc.read_accept_floor is _afc_again.read_accept_floor,
        "afc.run_floor_control defaults to that same reader":
            afc.run_floor_control.__defaults__[-1] is afc.read_accept_floor,
        "the accept floor this file grades against IS the instrument's":
            ACCEPT_FLOOR is afc.ACCEPT_FLOOR,
    }
    bad = [k for k, v in checks.items() if not v]
    if bad:
        refuse("IMPORTED_SYMBOL_IDENTITY",
               {"failed": bad, "checks": {k: bool(v) for k, v in checks.items()},
                "note": "a control that plants into a COPY of the reader the "
                        "gate calls controls nothing"})
    return {k: bool(v) for k, v in checks.items()}


def freeze_check(paths):
    """The frozen file IS the file that ran: disk == git blob at HEAD."""
    out = {}
    for rel in paths:
        disk = os.path.join(REPO, rel)
        if not os.path.isfile(disk):
            refuse("FREEZE", {"absent_on_disk": rel})
        on_disk = md5_of(disk)
        try:
            blob = subprocess.run(["git", "-C", REPO, "cat-file", "blob",
                                   "HEAD:%s" % rel],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  check=True).stdout
        except Exception as e:                                   # noqa: BLE001
            refuse("FREEZE", {"git_cat_file_failed": rel, "error": repr(e)[:300]})
        committed = hashlib.md5(blob).hexdigest()
        out[rel] = {"on_disk_md5": on_disk, "committed_blob_md5_HEAD": committed,
                    "disk_equals_committed_blob": on_disk == committed}
        if on_disk != committed:
            refuse("FREEZE", {"path": rel, "on_disk_md5": on_disk,
                              "committed_blob_md5_HEAD": committed,
                              "note": "the grading path is fixed at the "
                                      "pre-registration commit (rule 2)"})
    return out


# ------------------------------------------------------------ ledger reader
_TOK = re.compile(r'(?P<k>[A-Za-z_][\w(),]*)=(?P<v>\[[^\]]*\]|\S*)')


def parse_ledger(path):
    """Return {arm: row-dict} plus the raw extra lines.  REFUSES on a duplicate
    arm row -- D6's grader silently kept the last of two, and a strengthening
    can only turn a pass into a stop."""
    if not os.path.isfile(path):
        refuse("LEDGER", {"absent": path})
    rows, extra, seen = {}, [], []
    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.startswith("ARM="):
                extra.append(line)
                continue
            rec = {m.group("k"): m.group("v") for m in _TOK.finditer(line)}
            arm = rec.get("ARM")
            seen.append(arm)
            if arm in rows:
                refuse("LEDGER", {"duplicate_arm_row": arm, "arms_seen": seen,
                                  "note": "refused, not last-wins"})
            rec["_raw"] = line
            rows[arm] = rec
    return rows, extra


def read_chain_status(path):
    """REFUSES on multiplicity: exactly one `chain=started`, at most one
    terminal outcome (D6R AMENDMENT 1)."""
    if not os.path.isfile(path):
        return None
    started, terminal, arm_rc = [], [], {}
    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("chain=started"):
                started.append(line)
            elif line.startswith("chain="):
                terminal.append(line)
            elif line.startswith("arm="):
                m = re.match(r'arm=(\S+)\s+rc=(-?\d+)', line)
                if m:
                    arm_rc[m.group(1)] = int(m.group(2))
    if len(started) != 1:
        refuse("CHAIN_STATUS", {"n_chain_started": len(started),
                               "note": "a second fire into an existing root "
                                       "makes the census unreadable"})
    if len(terminal) > 1:
        refuse("CHAIN_STATUS", {"n_terminal_outcomes": len(terminal),
                               "lines": terminal})
    out = {"started": started[0], "arm_rc": arm_rc, "terminal": None,
           "outcome": None, "stop_arm": None, "stop_rc": None, "not_run": []}
    if terminal:
        t = terminal[0]
        out["terminal"] = t
        m = re.match(r'chain=(\S+)', t)
        out["outcome"] = m.group(1) if m else None
        m = re.search(r'\barm=(\S+)', t)
        out["stop_arm"] = m.group(1) if m else None
        m = re.search(r'\brc=(-?\d+)', t)
        out["stop_rc"] = int(m.group(1)) if m else None
        m = re.search(r'not_run=\[([^\]]*)\]', t)
        out["not_run"] = m.group(1).split() if m else []
    return out


# ------------------------------------------------------------- arm census
def arm_census(root, ledger_rows, chain):
    """1 ledger row -> RAN.  2 no row, chain accounts for the absence ->
    NOT_RUN with its reason.  3 otherwise REFUSE."""
    census = {}
    for arm in ARMS:
        if arm in ledger_rows:
            census[arm] = {"state": "RAN", "source": "ledger_row"}
            continue
        if chain and chain["outcome"] in REGISTERED_CHAIN_OUTCOMES \
                and arm in chain["not_run"]:
            census[arm] = {"state": "NOT_RUN",
                           "reason": "REGISTERED_CHAIN_%s" % chain["outcome"],
                           "stop_arm": chain["stop_arm"],
                           "stop_rc": chain["stop_rc"],
                           "chain_record": os.path.join(root, "STATUS.chain"),
                           "note": "the registration names this outcome; the "
                                   "arm bought 0 core-min"}
            continue
        refuse("CENSUS", {"arm": arm, "arm_absent_from_ledger": True,
                          "chain_outcome": (chain or {}).get("outcome"),
                          "chain_not_run": (chain or {}).get("not_run"),
                          "note": "COMPLETE accounts for nothing -- after a "
                                  "complete chain no arm may be missing"})
    # ---- THE ARMS THIS FREEZE DOES NOT REGISTER (section 8.2) -------------
    # They get a state of their own so that every gate they would have fed can
    # say WHY it has no input, instead of borrowing `ARM_DID_NOT_RUN`, which
    # is a claim about a registered arm that failed to start.  A ledger row
    # for one of them REFUSES: it would mean this item bought compute it never
    # registered.
    for arm in ARMS_NOT_REGISTERED_AT_THIS_FREEZE:
        if arm in ledger_rows:
            refuse("CENSUS", {"unregistered_arm_has_a_ledger_row": arm,
                              "note": "this item registers ONLY %r "
                                      "(PREREGISTRATION.md section 8.2); a "
                                      "row for %r means compute was bought "
                                      "outside the registration"
                                      % (ARMS, arm)})
        census[arm] = {"state": NOT_REGISTERED_STATE,
                       "reason": NOT_REGISTERED_REASON,
                       "core_min": 0.0,
                       "note": "not registered at this freeze; bought 0 "
                               "core-min; every gate it would have fed reads "
                               "NOT A RESULT for want of an input"}
    return census


# ------------------------------------------------------------------- G1
def gate_g1(root, ledger_rows, census):
    res = {"gate": "G1_completion", "arms": {}, "all_arms_ran": True,
           "ran_clean": True, "not_measured": []}
    for arm in ARMS:
        st = census[arm]
        if st["state"] != "RAN":
            res["all_arms_ran"] = False
            res["arms"][arm] = {"state": "NOT_RUN", "reason": st.get("reason"),
                                "core_min": 0.0}
            continue
        row = ledger_rows[arm]
        a = {"state": "RAN", "arm_kind": ARM_KIND[arm]}
        rc = int(row.get("rc", "999"))
        insp = row.get("inspect(exit,oomkilled)", "[]").strip("[]").split()
        if len(insp) != 2:
            refuse("G1", {"arm": arm, "inspect_field_unreadable": row.get(
                "inspect(exit,oomkilled)")})
        kernel_rc, oom = int(insp[0]), insp[1]
        if kernel_rc != rc:
            refuse("G1", {"arm": arm, "harness_rc": rc, "kernel_rc": kernel_rc,
                          "note": "harness and kernel disagree on rc"})
        a["rc"] = rc
        a["kernel_rc"] = kernel_rc
        a["oomkilled"] = oom
        a["rc_clause_pass"] = (rc == 0)
        a["oom_clause_pass"] = (oom == "false")

        log = os.path.join(root, row.get("log", ""))
        if not os.path.isfile(log):
            refuse("G1", {"arm": arm, "log_absent": log,
                          "note": "a log is PHYSICS, not infrastructure"})
        a["log"] = log
        if ARM_KIND[arm] == "SOLVER":
            last = None
            with open(log, errors="replace") as fh:
                for line in fh:
                    s = line.strip()
                    if s:
                        last = s
            a["terminal_last_line"] = last
            a["terminal_clause_pass"] = (last == TERMINAL_STATEMENT)
        else:
            ok = [f for f in os.listdir(root)
                  if f.startswith(os.path.basename(log) + ".ok.")]
            a["ok_markers"] = ok
            a["terminal_clause_pass"] = (len(ok) == 1)

        # ---- the AGE GUARD (rule 4) -------------------------------------
        wd = os.path.join(root, ARM_DIR[arm])
        datum_file = os.path.join(wd, ".d4_age_datum")
        if not os.path.isfile(datum_file):
            refuse("G1", {"arm": arm, "age_datum_absent": datum_file,
                          "note": "without the datum the age guard cannot run, "
                                  "and the age guard is PHYSICS"})
        with open(datum_file) as fh:
            datum_raw = fh.read().strip()
        # CALL SITE 2 OF 2 OF THE UN-TRUNCATED DATUM (CLAUDE.md rule 14; the
        # other is `d6rf4_endpoint_physical.py`'s C3).  `float()` of a
        # SERIALISED INTEGER is invisible to the committed truncation census --
        # it resolves `datum` as carrying no mtime provenance at all -- so the
        # floor has to be caught HERE, on the bytes, by asserting the decimal
        # point the launcher's `stat -c '%.9Y'` always emits.  A floored datum
        # sits EARLIER than the sentinel and this guard accepts on
        # `mt > datum`, so the failure is FAIL-OPEN by up to 1.000 s, and every
        # REGISTERED_PRODUCT it guards is a STAGED/GENERATED JSON file.
        if "." not in datum_raw:
            refuse("G1", {"arm": arm, "age_datum_truncated": datum_file,
                          "age_datum_raw": datum_raw,
                          "note": "the age datum carries NO FRACTIONAL PART, so "
                                  "it was floored to the whole second; that opens "
                                  "the age guard by up to 1.000 s in the "
                                  "ACCEPTING direction and the age guard is PHYSICS"})
        datum = float(datum_raw)
        ages, age_pass = {}, True
        for prod in REGISTERED_PRODUCTS[arm]:
            p = os.path.join(wd, prod)
            if not os.path.isfile(p):
                refuse("G1", {"arm": arm, "registered_product_absent": p,
                              "note": "the producing arm RAN, so an absent "
                                      "product refuses (D6's behaviour, kept)"})
            mt = os.stat(p).st_mtime
            ages[prod] = {"mtime": mt, "newer_than_datum": mt > datum}
            age_pass = age_pass and mt > datum
        a["age_datum"] = datum
        a["age_detail"] = ages
        a["age_clause_pass"] = age_pass

        # ---- section 3f, WIDENED to G1 (2026-09-05, pre-compute) ----------
        # `_f(row.get("core_min", "nan"))` returned a NaN silently on a
        # malformed or absent field, and `core_min` is what `compose` sums into
        # `spend_core_min` and what every cost claim rests on. A NaN spend is
        # not a small spend; it is an unmeasured one.
        try:
            a["core_min"] = _ff(row.get("core_min", "nan"), "ledger.txt",
                                "%s.core_min" % arm)
            a["wall_s"] = _ff(row.get("wall_s", "nan"), "ledger.txt",
                              "%s.wall_s" % arm)
        except NonFinite as e:
            a["core_min"] = 0.0
            a["wall_s"] = None
            a["non_finite"] = e.detail
            a["reason"] = NON_FINITE_REASON
            a["clauses_all_pass"] = False
            res["ran_clean"] = False
            res["non_finite"] = e.detail
            res["reason"] = NON_FINITE_REASON
            res["arms"][arm] = a
            continue
        a["ranks"] = int(row.get("ranks", "0"))
        a["clauses_all_pass"] = all([a["rc_clause_pass"], a["oom_clause_pass"],
                                     a["terminal_clause_pass"],
                                     a["age_clause_pass"]])
        if not a["clauses_all_pass"]:
            res["ran_clean"] = False
        res["arms"][arm] = a
    return res


# ---------------------------------------------------- G-CAPS / G9 / G12
def gate_caps(ledger_rows, census):
    res = {"gate": "G-CAPS", "arms": {}, "verdict": "PASS", "not_measured": []}
    for arm in ARMS:
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"state": "NOT_RUN", "core_min": 0.0}
            continue
        row = ledger_rows[arm]
        cap = CAPS[arm]
        # ---- section 3f, WIDENED to G-CAPS (2026-09-05, pre-compute) ------
        # THIS IS `D6RF3-DEF-5` ONE GATE OVER, and it is not hypothetical:
        # `nan <= cap` is False, so a malformed `core_min` would have set
        # `within_cap` False and produced `G-CAPS GATE FAIL` -- an accusation
        # that an arm BREACHED ITS BUDGET, manufactured from a non-number.
        # That is the most damaging shape this defect can take, because a cap
        # breach is a finding about discipline, not about physics.
        try:
            cm = _ff(row.get("core_min", "nan"), "ledger.txt",
                     "%s.core_min" % arm)
        except NonFinite as e:
            res["arms"][arm] = _nar_non_finite(
                {"cap_core_min": cap, "state": "RAN"}, e)
            res["verdict"] = "NOT A RESULT"
            res["reason"] = NON_FINITE_REASON
            res["non_finite"] = e.detail
            continue
        a = {"core_min": cm, "cap_core_min": cap, "within_cap": cm <= cap}
        inv = (TMO[arm] + FRAME_ALLOWANCE_S) * RANKS / 60.0
        a["deadline_in_container_s"] = TMO[arm]
        a["cap_inversion_core_min"] = inv
        a["inversion_matches_cap"] = abs(inv - cap) <= CAP_INVERSION_TOL_CORE_MIN
        cw = row.get("container_wall_s")
        if cw in (None, "", "NOT_MEASURED"):
            a["container_wall_s"] = "NOT_MEASURED"
            a["deadline_frame_pass"] = "NOT_MEASURED"
            a["frame_gap_within_allowance"] = "NOT_MEASURED"
            res["not_measured"].append("%s/container_wall_s" % arm)
        else:
            try:
                cwv = _ff(cw, "ledger.txt", "%s.container_wall_s" % arm)
                ws = _ff(row.get("wall_s", "nan"), "ledger.txt",
                         "%s.wall_s" % arm)
            except NonFinite as e:
                res["arms"][arm] = _nar_non_finite(dict(a, state="RAN"), e)
                res["verdict"] = "NOT A RESULT"
                res["reason"] = NON_FINITE_REASON
                res["non_finite"] = e.detail
                continue
            a["container_wall_s"] = cwv
            a["deadline_frame_pass"] = cwv <= TMO[arm] + KILL_GRACE_S
            gap = ws - cwv
            a["host_minus_container_s"] = gap
            a["frame_gap_within_allowance"] = gap <= FRAME_GAP_ALLOWANCE_S
        fa = row.get("frame_allowance_s")
        try:
            fav = (None if fa is None
                   else _ff(fa, "ledger.txt", "%s.frame_allowance_s" % arm))
        except NonFinite as e:
            res["arms"][arm] = _nar_non_finite(dict(a, state="RAN"), e)
            res["verdict"] = "NOT A RESULT"
            res["reason"] = NON_FINITE_REASON
            res["non_finite"] = e.detail
            continue
        a["frame_allowance_matches_registered"] = (
            fav is not None and int(fav) == FRAME_ALLOWANCE_S)
        limbs = [a["within_cap"], a["inversion_matches_cap"],
                 a["frame_allowance_matches_registered"]]
        for k in ("deadline_frame_pass", "frame_gap_within_allowance"):
            if a[k] is not True and a[k] != "NOT_MEASURED":
                limbs.append(False)
        a["verdict"] = "PASS" if all(limbs) else "GATE FAIL"
        if a["verdict"] == "GATE FAIL":
            res["verdict"] = "GATE FAIL"
        res["arms"][arm] = a
    return res


def gate_toolchain(root, ledger_rows, census):
    res = {"gate": "G9_toolchain", "arms": {}, "verdict": "PASS",
           "shipped_row": "NAMED UNBOUGHT: %s" % DIGEST_SHIPPED}
    for arm in ARMS:
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"state": "NOT_RUN"}
            continue
        row = ledger_rows[arm]
        a = {"row": row.get("ROW"), "digest": row.get("DIGEST")}
        a["digest_is_patched"] = (row.get("DIGEST") == DIGEST_PATCHED)
        a["row_is_patched"] = (row.get("ROW") == "PATCHED")
        log = os.path.join(root, row.get("log", ""))
        seen = None
        if os.path.isfile(log):
            with open(log, errors="replace") as fh:
                for line in fh:
                    if "D4S_IDWARP_SO_MD5:" in line or "D4_IDWARP_SO_MD5:" in line:
                        seen = line.strip().split(":")[-1].strip()
                        break
        a["idwarp_so_md5_in_log"] = seen
        a["idwarp_so_md5_matches"] = (seen == IDWARP_SO_MD5)
        a["verdict"] = "PASS" if all([a["digest_is_patched"], a["row_is_patched"],
                                      a["idwarp_so_md5_matches"]]) else "GATE FAIL"
        if a["verdict"] == "GATE FAIL":
            res["verdict"] = "GATE FAIL"
        res["arms"][arm] = a
    return res


def gate_placement(ledger_rows, census):
    res = {"gate": "G12_placement", "arms": {}, "verdict": "PASS",
           "not_measured": []}
    for arm in ARMS:
        if census[arm]["state"] != "RAN":
            res["arms"][arm] = {"state": "NOT_RUN"}
            continue
        row = ledger_rows[arm]
        a = {"cpuset": row.get("cpuset"), "memory": row.get("memory")}
        a["cpuset_matches_registered"] = (row.get("cpuset") == CPUSET)
        a["memory_matches_registered"] = (row.get("memory") == MEMORY)
        dm = row.get("delivered_cores_mean", "[]").strip("[]").split()
        if not dm or dm[0] == "NOT_MEASURED":
            a["delivered_cores_mean"] = "NOT_MEASURED"
            a["delivered_pass"] = "NOT_MEASURED"
            res["not_measured"].append("%s/delivered_cores_mean" % arm)
        else:
            a["delivered_cores_mean"] = _f(dm[0])
            a["delivered_pass"] = a["delivered_cores_mean"] >= DELIVERED_MIN
        limbs = [a["cpuset_matches_registered"], a["memory_matches_registered"]]
        if a["delivered_pass"] is not True and a["delivered_pass"] != "NOT_MEASURED":
            limbs.append(False)
        a["verdict"] = "PASS" if all(limbs) else "GATE FAIL"
        if a["verdict"] == "GATE FAIL":
            res["verdict"] = "GATE FAIL"
        res["arms"][arm] = a
    return res


# -------------------------------------------------------------- G-DVL
DV_KEYS = ("twist", "shape", "patchV_cl04", "patchV_cl05", "patchV_cl06")


def _dv_finiteness(path, artefact):
    """Section 3f over a PHYSICAL design-vector artefact.  Raises `NonFinite`
    naming the first offending component; returns the census otherwise."""
    if not os.path.isfile(path):
        refuse("G-DVL", {"artefact_absent_although_producer_ran": path})
    with open(path) as fh:
        doc = json.load(fh)
    out = {"n_checked": 0, "keys": {}}
    for k in DV_KEYS:
        if k not in doc:
            continue
        vals = doc[k]
        out["keys"][k] = len(vals)
        for i, v in enumerate(vals):
            out["n_checked"] += 1
            _ff(v, artefact, "%s[%d]" % (k, i))
    if out["n_checked"] == 0:
        refuse("G-DVL", {"path": path, "no_registered_dv_family_present": True,
                         "keys_present": sorted(doc)[:40],
                         "note": "a finiteness control with nothing to check "
                                 "is not a control (L-302)"})
    return out


def gate_dvl(root, census, runscript_d6r, runscript_d4):
    """Re-read BOTH published physical artefacts from disk and re-assert the two
    locus controls at GRADING time.  Never trusts the producer's say-so."""
    sys.path.insert(0, HERE)
    import d6rf4_endpoint_locus as locus
    res = {"gate": "G-DVL_endpoint_locus", "arms": {}}
    verdicts = []
    # THE REGISTERED ARM IS `P_conv`, NOT `F_mp`.  Caught by the section 3f
    # mutation harness: the parent's hard-coded `F_mp` made this gate look for
    # `root/F_mp/d6rf4_endpoint_dvs_PHYSICAL.json` on a run that writes to
    # `root/P_conv/`, and it REFUSED `artefact_absent_although_producer_ran`
    # on a clean fixture.  A refusal is not the registered behaviour and it
    # would have fired on the real run too.
    for arm, art, rs in ((ARMS[0], "d6rf4_endpoint_dvs_PHYSICAL.json", runscript_d6r),
                         ("REF_off", "d4_endpoint_dvs_PHYSICAL.json", runscript_d4)):
        if census[arm]["state"] != "RAN":
            _r, _d = _no_input_reason(census, arm, art, root)
            res["arms"][arm] = dict({"verdict": "NOT A RESULT", "reason": _r,
                                     "artefact": art}, **_d)
            verdicts.append("NOT A RESULT")
            continue
        path = os.path.join(root, ARM_DIR[arm], art)
        # ---- section 3f binds G-DVL --------------------------------------
        # Checked HERE, at the grader's boundary, and NOT by editing
        # `d6rf4_endpoint_locus.py`: a non-finite design component makes every
        # locus control (pinned witness, bounds containment) return False for
        # a reason that has nothing to do with the locus, which would read as
        # `GATE FAIL -- the design point is not the one the registration
        # names`. That is the wrong finding stated confidently.
        try:
            nf = _dv_finiteness(path, art)
        except NonFinite as e:
            r = _nar_non_finite({"artefact": path,
                                 "registration_source": rs}, e)
            res["arms"][arm] = r
            verdicts.append("NOT A RESULT")
            continue
        try:
            r = locus.gate(path, rs)
            r["verdict"] = "PASS"
        except locus.LocusRefusal as e:
            r = {"verdict": "GATE FAIL", "artefact": path,
                 "registration_source": rs, "control_refusal": str(e)[:900]}
        r["finiteness"] = nf
        res["arms"][arm] = r
        verdicts.append(r["verdict"])
    res["verdict"] = ("NOT A RESULT" if "NOT A RESULT" in verdicts else
                      ("GATE FAIL" if "GATE FAIL" in verdicts else "PASS"))
    return res


# -------------------------------------------- readers + planted-zero controls
def read_fd(path):
    """THE FD READER.  One function, used for the real artefact AND for the
    planted copy -- a control that exercises a different reader controls
    nothing."""
    with open(path) as fh:
        doc = json.load(fh)
    rows = []
    for r in doc.get("rows", []):
        rec = {"dv": r.get("dv"), "idx": r.get("idx"), "status": r.get("status")}
        if r.get("status") == "PLANNED":
            rec["J_adj"] = _f(r.get("J_adj"))
            fd = r.get("fd") or {}
            for lab in ("s_lo", "s_hi"):
                leg = fd.get(lab) or {}
                rec[lab] = {"ok": bool(leg.get("ok")),
                            "step": leg.get("step"),
                            "d": _f(leg["d"]) if leg.get("ok") else None}
        rows.append(rec)
    return {"rows": rows, "n_rows": doc.get("n_rows"),
            "eta_used": _f(doc.get("eta_used", "nan")),
            "eta_floored": doc.get("eta_floored"),
            "producer_md5": doc.get("producer_md5")}


def plant_into_fd(src, dst):
    """Plant PLANT into the FIRST PLANNED row's s_hi derivative, BY KEY, and
    write the perturbed copy.  Returns the row identity that was planted."""
    with open(src) as fh:
        doc = json.load(fh)
    for r in doc.get("rows", []):
        if r.get("status") != "PLANNED":
            continue
        leg = (r.get("fd") or {}).get("s_hi") or {}
        if not leg.get("ok"):
            continue
        leg["d"] = repr(float(leg["d"]) + PLANT)
        with open(dst, "w") as fh:
            json.dump(doc, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        return {"dv": r.get("dv"), "idx": r.get("idx")}
    return None


def read_d4_cd_f(path):
    """THE PRICE READER.  Takes the LAST field of the single `^Objective` line
    of D4's IPOPT summary.  Refuses on zero or more than one such line."""
    if not os.path.isfile(path):
        refuse("PRICE_READER", {"absent": path})
    hits = []
    with open(path, errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if line.startswith("Objective"):
                hits.append((i, line.rstrip("\n")))
    if len(hits) != 1:
        refuse("PRICE_READER", {"n_objective_lines": len(hits), "path": path})
    parts = hits[0][1].replace(":", " ").split()
    return _f(parts[-1]), {"line_no": hits[0][0], "line": hits[0][1]}


def plant_into_d4(src, dst):
    """Plant PLANT into the objective on a COPY, BY LINE INDEX."""
    with open(src, errors="replace") as fh:
        lines = fh.readlines()
    idx = [i for i, l in enumerate(lines) if l.startswith("Objective")]
    if len(idx) != 1:
        refuse("PRICE_PLANT", {"n_objective_lines": len(idx)})
    i = idx[0]
    parts = lines[i].replace(":", " ").split()
    val = float(parts[-1]) + PLANT
    lines[i] = "Objective...............:   %.16e    %.16e\n" % (val, val)
    with open(dst, "w") as fh:
        fh.writelines(lines)
        fh.flush()
        os.fsync(fh.fileno())
    return i + 1


def run_planted_controls(ctrl_dir, fd_path):
    """CLAUDE.md rule 3.  THREE controls now, not two -- section 3e.  Each
    plants, reads back FROM DISK through the SAME reader the gate uses, and
    REFUSES if the reader is blind.  Each asserts the unperturbed original is
    byte-unchanged: a control that modifies what it grades is not a control.

    EVERY CONTROL REPORTS ONE OF THREE STATES -- `EXERCISED-PASS`,
    `EXERCISED-FAIL`, `NOT EXERCISED` -- and `NOT EXERCISED` is printed beside
    the verdict, never counted as a pass and never inferred from the absence of
    a failure.  `DAFOAM_CHARTER.md` section 18.5 records this as a PROPOSAL for
    the whole lab and deliberately does NOT enact it there, because that is
    Sanaa's call; it is taken here, inside this item's own comparator, where
    this item may take it.  The finding behind it is this lineage's own: D6R's
    frozen grader short-circuited `g_price` when an arm did not run, so its
    planted control never executed and nothing said so -- the control's silence
    and the control's success were indistinguishable in the record."""
    os.makedirs(ctrl_dir, exist_ok=True)
    out = {"PLANT": PLANT, "rel_tol": PLANT_REL_TOL}

    # ---- control 1: the FD reader ----
    # ========== FOUND BY THE PRE-COMPUTE DRIVE, AND IT IS A REAL ONE ========
    # The parent REFUSES when the FD product carries no PLANNED row -- correct
    # for an FD arm, where an empty product means the control has nothing to
    # control and a pass would be a false one.  BUT `P_conv` TAKES NO FD STEP
    # AT ALL (`--mode P_conv`; section 8.2), so its product is EMPTY BY
    # REGISTRATION and the parent's refusal would stop every clean grading of
    # the arm this item actually buys.
    #
    # THE DISTINCTION IS READ FROM THE ARTEFACT, NOT ASSUMED: the producer
    # writes its own `mode`, and only a mode that IS registered to take FD
    # steps can have an empty product held against it.  A product with NO
    # `mode` key at all falls to the parent's refusal, because an artefact
    # that will not say what program wrote it cannot excuse itself.
    #
    # AND IT IS `NOT EXERCISED`, NOT A PASS.  Section 18.5's own finding:
    # the control's silence and the control's success must not be
    # indistinguishable in the record.
    _fd_skip = False
    if fd_path is not None and os.path.isfile(fd_path):
        try:
            with open(fd_path) as _fh:
                _mode = json.load(_fh).get("mode")
        except (OSError, ValueError):
            _mode = None
        if _mode in NO_FD_MODES:
            out["fd_control"] = {
                "state": cdc.NOT_EXERCISED,
                "reader_saw_the_plant": None,
                "artefact": fd_path,
                "producer_mode": _mode,
                "why": "the producing leg ran in mode %r, which TAKES NO FD "
                       "STEP by registration (PREREGISTRATION.md section "
                       "8.2), so the FD product carries no PLANNED row and "
                       "there is nothing to plant into. NOT EXERCISED, "
                       "printed beside the verdict, NEVER counted as a pass "
                       "and NEVER inferred from the absence of a failure. "
                       "G-FD reads NOT A RESULT for want of an input on the "
                       "same data." % _mode}
            _fd_skip = True
    # `fd_path` IS NOT NULLED HERE, and the first draft of this repair nulled
    # it -- which silently sent CONTROL 3, the CD reader, to NOT EXERCISED as
    # well.  Caught by the pre-compute drive.  The CD reader IS exercisable on
    # a P_conv product: `points.<pt>.CD` is written by the baseline primal
    # (D6RF4-DEF-7's repair) and is exactly what G-PRICE and X-CDLOG read.
    # Skipping a control that CAN be exercised is the same failure as counting
    # one that cannot as a pass, in the other direction.
    if _fd_skip:
        pass
    elif fd_path is None or not os.path.isfile(fd_path):
        out["fd_control"] = {"state": cdc.NOT_EXERCISED,
                             "reader_saw_the_plant": None,
                             "why": "the FD artefact's producing arm did "
                                    "not run; there is nothing to read and "
                                    "no gate is computed from it"}
    else:
        m_before = md5_of(fd_path)
        base = read_fd(fd_path)
        planted_copy = os.path.join(ctrl_dir, "d6r_fd_endpoint.PLANTED.json")
        who = plant_into_fd(fd_path, planted_copy)
        if who is None:
            refuse("PLANT_FD", {"no_PLANNED_row_with_an_ok_s_hi_leg": True,
                                "note": "a control with nothing to plant into "
                                        "is not a control (L-302)"})
        got = read_fd(planted_copy)
        b = [r for r in base["rows"]
             if r["dv"] == who["dv"] and r["idx"] == who["idx"]][0]["s_hi"]["d"]
        g = [r for r in got["rows"]
             if r["dv"] == who["dv"] and r["idx"] == who["idx"]][0]["s_hi"]["d"]
        delta = g - b
        seen = abs(delta - PLANT) <= PLANT_REL_TOL * max(abs(PLANT), abs(b), 1.0)
        m_after = md5_of(fd_path)
        out["fd_control"] = {"planted_into": who, "unperturbed": b,
                             "planted_read_back": g, "delta": delta,
                             "reader_saw_the_plant": seen,
                             "state": (cdc.EXERCISED_PASS if seen
                                       else cdc.EXERCISED_FAIL),
                             "original_md5_before": m_before,
                             "original_md5_after": m_after,
                             "original_unchanged": m_before == m_after,
                             "planted_copy": planted_copy}
        if not seen:
            refuse("PLANT_FD", out["fd_control"])
        if m_before != m_after:
            refuse("PLANT_FD", {"the_control_modified_the_artefact_it_grades":
                                True, **out["fd_control"]})

    # ---- control 2: the D4 price reader ----
    m_before = md5_of(D4_OPT_IPOPT)
    base_cd, where = read_d4_cd_f(D4_OPT_IPOPT)
    planted_copy = os.path.join(ctrl_dir, "d4_opt_IPOPT.PLANTED.txt")
    ln = plant_into_d4(D4_OPT_IPOPT, planted_copy)
    got_cd, _ = read_d4_cd_f(planted_copy)
    delta = got_cd - base_cd
    seen = abs(delta - PLANT) <= PLANT_REL_TOL * max(abs(PLANT), abs(base_cd), 1.0)
    m_after = md5_of(D4_OPT_IPOPT)
    out["price_control"] = {"planted_at_line": ln, "unperturbed": base_cd,
                            "planted_read_back": got_cd, "delta": delta,
                            "reader_saw_the_plant": seen,
                            "state": (cdc.EXERCISED_PASS if seen
                                      else cdc.EXERCISED_FAIL),
                            "source_line": where,
                            "original_md5_before": m_before,
                            "original_md5_after": m_after,
                            "original_unchanged": m_before == m_after,
                            "planted_copy": planted_copy}
    if not seen:
        refuse("PLANT_PRICE", out["price_control"])
    if m_before != m_after:
        refuse("PLANT_PRICE", {"the_control_modified_D4s_preserved_artefact":
                               True, **out["price_control"]})

    # ---- control 3: THE CD READER -- NEW, because the SOURCE MOVED ---------
    # Section 3e.  `G-OFF` and `G-PRICE` no longer read CD from the producing
    # history (D6RF3-DEF-4: it contains none) but from the FD arm's own
    # baseline primal.  A CD read from a new source is not evidence until a
    # reader has been shown able to see a non-zero in it.  The control and the
    # graded path are LITERALLY THE SAME FUNCTION -- `cdc.read_cd` -- so the
    # control cannot drift away from what it controls.
    try:
        out["cd_control"] = cdc.run_cd_control(ctrl_dir, fd_path)
    except cdc.CDRefusal as e:
        refuse("PLANT_CD", {"cd_control_refused": str(e)[:1500]})

    out["control_states"] = {k: out[k].get("state")
                             for k in ("fd_control", "price_control",
                                       "cd_control")}
    out["n_not_exercised"] = sum(1 for v in out["control_states"].values()
                                 if v == cdc.NOT_EXERCISED)
    with open(os.path.join(ctrl_dir, "planted_controls.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    return out


# ============ section 3.1 / 3.2: THE PER-LEG CONTAINER-LOG READER ==========
_RES_LINE = re.compile(
    r'^(?P<f>\S+) initRes: (?P<i>\S+) finalRes: (?P<r>\S+) nIters: (?P<n>\d+)\s*$')
_TIME_LINE = re.compile(r'^Time = (?P<t>\d+)\s*$')
_CDCL_LINE = re.compile(r'^(?P<q>CD|CL): (?P<v>\S+) final: (?P<f>\S+)\s*$')
_EXEC_LINE = re.compile(r'^ExecutionTime = (?P<e>\S+) s\s+ClockTime = (?P<c>\S+) s\s*$')


def read_legs(log_path):
    """Split ONE container log into the arm's three registered legs and read
    each leg's OWN final-iteration per-field `initRes`.

    WHY SEGMENTS AND NOT A WHOLE-LOG SCAN.  `P_conv` runs three primals in one
    container at TWO DIFFERENT `fvSolution` settings.  A whole-log reader would
    hand `G-CONV` the LAST `Time = 1000` block it found, which is `L3`'s -- the
    DELIBERATELY WRONG SETTING -- and the gate would grade the falsifier as if
    it were the repair.  The segmentation is what keeps those apart, and it is
    read from markers the producer PRINTS rather than from line numbers.

    FAILS CLOSED.  A leg with no `LEG_BEGIN` is `BAR_NOT_PRODUCED` and named;
    a leg with a begin and no residual block is `SEGMENT_WITHOUT_RESIDUALS`
    and named.  Neither is silently treated as absent, and neither is treated
    as a pass."""
    out = {"log": log_path, "segments": {}, "order": [],
           "last_leg_completed": None, "markers_seen": 0}
    if not log_path or not os.path.isfile(log_path):
        out["state"] = BAR_NOT_PRODUCED
        out["why"] = ("the arm's container log is not on disk, so no leg was "
                      "read. UNMEASURED, never a pass.")
        return out
    cur, segs, installs = None, [], []
    with open(log_path, errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            s = line.rstrip("\n")
            if s.startswith(FVSOL_INSTALL_MARKER):
                kv = dict(x.split("=", 1) for x in s.split()[1:] if "=" in x)
                kv["line"] = ln
                installs.append(kv)
                continue
            if s.startswith(LEG_BEGIN):
                parts = s.split()
                cur = {"tag": parts[1] if len(parts) > 1 else None,
                       "mode": next((x.split("=", 1)[1] for x in parts
                                     if x.startswith("mode=")), None),
                       "begin_line": ln, "end_line": None, "times": [],
                       "fields": {}, "CD": None, "CL": None,
                       "execution_time_s": None, "primal_failed": None,
                       "primal_raised": None}
                segs.append(cur)
                out["markers_seen"] += 1
                continue
            if s.startswith(LEG_END):
                out["markers_seen"] += 1
                if cur is not None:
                    cur["end_line"] = ln
                    cur["primal_raised"] = ("primal_raised=True" in s)
                    out["last_leg_completed"] = cur["tag"]
                    cur = None
                continue
            if cur is None:
                continue
            m = _TIME_LINE.match(s)
            if m:
                cur["times"].append(int(m.group("t")))
                cur["fields"] = {}          # the LAST time block is the graded one
                continue
            m = _RES_LINE.match(s)
            if m:
                cur["fields"][m.group("f")] = {
                    "initRes": m.group("i"), "finalRes": m.group("r"),
                    "nIters": int(m.group("n")), "line": ln}
                continue
            m = _CDCL_LINE.match(s)
            if m:
                cur[m.group("q")] = m.group("v")
                continue
            m = _EXEC_LINE.match(s)
            if m:
                cur["execution_time_s"] = m.group("e")
                continue
            if PRIMAL_FAILURE_BANNER in s:
                cur["primal_failed"] = True
    # ---- BIND THE SEGMENTS TO THE REGISTERED LEGS, IN ORDER ---------------
    # L1 and L2 are `P_conv` mode, L3 is `F5_loose`.  Binding is by the MODE
    # the producer printed and by ORDER OF APPEARANCE -- never by assuming
    # three segments exist, because a truncated arm has fewer.
    pconv = [s for s in segs if s.get("mode") == "P_conv"]
    f5 = [s for s in segs if s.get("mode") == "F5_loose"]
    for leg, seg in list(zip(("L1", "L2"), pconv)) + list(zip(("L3",), f5)):
        seg["leg"] = leg
        seg["registered_role"] = LEG_ROLE[leg]
        seg["registered_fvSolution"] = LEG_FVSOLUTION[leg]
        seg["final_time"] = seg["times"][-1] if seg["times"] else None
        if not seg["fields"]:
            seg["state"] = "SEGMENT_WITHOUT_RESIDUALS"
        else:
            seg["state"] = "READ"
        out["segments"][leg] = seg
        out["order"].append(leg)
    out["fvSolution_installs"] = installs
    # BIND EACH LEG TO THE LAST INSTALL THAT PRECEDED ITS `LEG_BEGIN`.  By
    # LINE ORDER, because that is the order the container executed in.
    for leg, seg in out["segments"].items():
        prior = [i for i in installs if i["line"] < seg["begin_line"]]
        got = prior[-1] if prior else None
        want_name = LEG_FVSOLUTION[leg]
        want_md5 = FVSOL_MD5[want_name]
        seg["fvSolution_install"] = got
        if got is None:
            seg["fvSolution_state"] = "INSTALL_MARKER_NOT_PRODUCED"
        elif got.get("md5") != want_md5:
            seg["fvSolution_state"] = "WRONG_FVSOLUTION"
        elif got.get("leg") not in (None, LEG_INSTALL_TAG[leg]):
            seg["fvSolution_state"] = "WRONG_FVSOLUTION"
        else:
            seg["fvSolution_state"] = "AS_REGISTERED"
        seg["fvSolution_registered_md5"] = want_md5
        seg["fvSolution_installed_md5"] = (got or {}).get("md5")
        seg["fvSolution_sites"] = (got or {}).get("sites")
    out["n_segments"] = len(segs)
    out["n_bound"] = len(out["segments"])
    out["state"] = BAR_PRODUCED if out["segments"] else BAR_NOT_PRODUCED
    out["unbound_segments"] = [s for s in segs if "leg" not in s]
    return out


# ------------------------------------------------------------ G-CONV
def gate_conv(root, census, legs):
    """`G-CONV`, section 3.1.  NEW AND GATED.

    THE BAR IS THE INHERITED ACCEPT FLOOR RESTATED, NOT MOVED.  `1.0e-05` =
    `primalMinResTol x primalMinResTolDiff` = `1e-08 x 1000`, carried forward
    from `D6RF3` unchanged, and `ACCEPT_FLOOR_UNMOVED` REFUSES the grading if
    the values in the arm's own log are not those.  This gate does not
    introduce a bar; it makes the bar DAFoam already applies post-`End` (`N-D42`)
    GRADEABLE PER FIELD, so a failure NAMES THE FIELD instead of a maximum.

    THE SUBJECT IS `L1`, THE TIGHTENED BASELINE, AND ONLY `L1`.  `L3` is the
    falsifier at the deliberately wrong setting; it is READ against this gate's
    own bar and reported, and its outcome drives F5's withdrawal clause -- it
    is never averaged into the gate's verdict."""
    base = {"gate": "G-CONV_per_field_final_initRes",
            "bar": CONV_BAR, "fields": list(CONV_FIELDS),
            "bar_provenance": (
                "1.0e-05 = primalMinResTol 1e-08 x primalMinResTolDiff 1000, "
                "carried forward from D6RF3 UNCHANGED. N-D43: the accept floor "
                "is the PRODUCT, never the tolerance alone. This gate RESTATES "
                "the bar DAFoam already applies post-End; it does not move it, "
                "and d6rf4_accept_floor_control.py refuses if it has moved."),
            "graded_leg": "L1", "reported_legs": ["L2", "L3"],
            "d6rf3_measured": CONV_MEASURED_D6RF3,
            "per_leg": {}}
    producer = ARTEFACT_PRODUCER["d6rf4_fd_endpoint.json"]
    if census[producer]["state"] != "RAN":
        _r, _d = _no_input_reason(census, producer, None, root)
        base.update(dict({"verdict": "NOT A RESULT", "reason": _r}, **_d))
        base.update(NULL_READINGS["G-CONV"])
        return base
    if legs.get("state") != BAR_PRODUCED or "L1" not in legs["segments"]:
        base.update({"verdict": "NOT A RESULT",
                     "reason": "SEGMENT_NOT_PRODUCED",
                     "bar_state": BAR_NOT_PRODUCED,
                     "producing_leg": NULL_READINGS["G-CONV"]["producing_leg"],
                     "legs_seen": sorted(legs.get("segments", {})),
                     "note": "the arm ran but L1's log segment was not "
                             "produced, so the per-field residuals this gate "
                             "grades do not exist. NOT A RESULT for want of "
                             "an input, with the missing producer NAMED."})
        return base
    verds, nonfinite = [], []
    for leg, seg in sorted(legs["segments"].items()):
        row = {"leg": leg, "role": seg["registered_role"],
               "fvSolution": seg["registered_fvSolution"],
               "fvSolution_state": seg.get("fvSolution_state"),
               "fvSolution_registered_md5": seg.get("fvSolution_registered_md5"),
               "fvSolution_installed_md5": seg.get("fvSolution_installed_md5"),
               "fvSolution_sites": seg.get("fvSolution_sites"),
               "final_time": seg["final_time"],
               "primal_failure_banner": bool(seg.get("primal_failed")),
               "per_field": {}, "fields_absent": []}
        # THE LEG MUST HAVE RUN THE BYTES IT WAS REGISTERED TO RUN.
        # NOT A RESULT, never GATE FAIL: a leg that ran the wrong fvSolution
        # did not measure the thing this gate's name says, so its number is
        # not evidence about the repair in EITHER direction.
        if seg.get("fvSolution_state") != "AS_REGISTERED":
            row.update({"verdict": "NOT A RESULT",
                        "reason": "FVSOLUTION_NOT_AS_REGISTERED",
                        "note": "this leg's log does not show the registered "
                                "fvSolution installed before it. A leg that "
                                "may have run the other stopping rule cannot "
                                "grade the stopping rule."})
            base["per_leg"][leg] = row
            if leg == "L1":
                verds.append("NOT A RESULT")
            continue
        worst, worst_f = None, None
        for f in CONV_FIELDS:
            got = seg["fields"].get(f)
            if got is None:
                row["fields_absent"].append(f)
                row["per_field"][f] = {"initRes": None,
                                       "verdict": "NOT A RESULT",
                                       "reason": "FIELD_ABSENT_FROM_SEGMENT"}
                continue
            try:
                v = _ff(got["initRes"], os.path.basename(legs["log"]),
                        "%s.%s.initRes" % (leg, f))
            except NonFinite as e:
                row["per_field"][f] = _nar_non_finite(
                    {"initRes": got["initRes"]}, e)
                nonfinite.append({"leg": leg, "field": f, **e.detail})
                if "non_finite" not in base:
                    # SURFACE IT AT THE GATE'S OWN LEVEL.  A disclosure only a
                    # reader who knows the nesting can find is a disclosure
                    # `compose` cannot act on and a harness cannot assert.
                    base["reason"] = NON_FINITE_REASON
                    base["non_finite"] = e.detail
                continue
            ratio = v / CONV_BAR
            row["per_field"][f] = {
                "initRes": v, "finalRes": got["finalRes"],
                "nIters": got["nIters"], "log_line": got["line"],
                "ratio_to_bar": ratio,
                "d6rf3_measured": CONV_MEASURED_D6RF3.get(f),
                "improvement_vs_d6rf3": (CONV_MEASURED_D6RF3[f] / v
                                         if f in CONV_MEASURED_D6RF3 and v > 0
                                         else None),
                "verdict": "PASS" if v < CONV_BAR else "GATE FAIL"}
            if worst is None or v > worst:
                worst, worst_f = v, f
        row["worst_field"] = worst_f
        row["worst_initRes"] = worst
        row["worst_ratio_to_bar"] = (worst / CONV_BAR) if worst is not None else None
        vs = [c.get("verdict") for c in row["per_field"].values()]
        row["verdict"] = ("NOT A RESULT" if "NOT A RESULT" in vs else
                          ("PASS" if all(v == "PASS" for v in vs) else "GATE FAIL"))
        base["per_leg"][leg] = row
        if leg == "L1":
            verds.append(row["verdict"])
    base["non_finite_rows"] = nonfinite
    base["verdict"] = verds[0] if verds else "NOT A RESULT"
    base["bar_state"] = BAR_PRODUCED
    # ---- the report this gate OWES, pass or fail (section 3.1) ------------
    base["registered_report"] = (
        "The full per-field initRes table at the final iteration, per leg, "
        "with each field's ratio to the bar %g, is in `per_leg`. L1 is the "
        "graded leg; L2 and L3 are REPORTED beside it and never averaged into "
        "the verdict." % CONV_BAR)
    return base


# ------------------------------------------------------------ F5
def falsifier_f5(conv):
    """`F5`, section 6.  DAFOAM_CHARTER.md section 21.3's shape, executed.

    IT NAMES THE GATE IT IS PREDICTED TO FAIL -- `G-CONV` -- AND THAT IS THE
    GATE ITS WITHDRAWAL CLAUSE WITHDRAWS.  The predicted value is not an
    estimate: it is `D6RF3`'s MEASURED `p initRes` at the identical settings,
    `1.316217833e-05`, against `G-CONV`'s OWN bar of `1.0e-05`.  The inequality
    `1.3162e-05 > 1.0e-05` fails that gate by `1.3162x` AT ZERO COMPUTE, which
    is the property section 21.1 found missing in `S1FDP`'s limb 2."""
    res = {"falsifier": "F5_wrong_setting_must_fail_G-CONV",
           "named_gate": F5_NAMED_GATE,
           "named_gates_own_bar": CONV_BAR,
           "predicted_value": F5_PREDICTED_P_INITRES,
           "predicted_value_provenance": (
               "D6RF3's MEASURED primalMaxRes / p initRes at Time = 1000 at "
               "the identical fvSolution settings, log "
               "F_mp_20260905T222250Z_43793.log :2092. MEASURED, not estimated."),
           "the_inequality": "1.3162e-05 > 1.0e-05 -- FAILS G-CONV by 1.3162x",
           "predicted_to_fail_its_named_gate": (
               F5_PREDICTED_P_INITRES > CONV_BAR),
           "withdrawal_clause": (
               "If the WRONG setting ALSO passes G-CONV, then G-CONV is not "
               "measuring the linear-solver stopping rule, section 1.3's "
               "mechanism is refuted, G-CONV'S VERDICT IS WITHDRAWN, and no "
               "claim about the repair may be made from this item.")}
    seg = (conv.get("per_leg") or {}).get(F5_LEG)
    if not seg:
        res.update({"verdict": "UNRESOLVED",
                    "bar_state": BAR_NOT_PRODUCED,
                    "producing_leg": NULL_READINGS["F5"]["producing_leg"],
                    "bar_artefact": NULL_READINGS["F5"]["bar_artefact"],
                    "withdraws": False,
                    "note": "L3 did not run, so the falsifier has no reading. "
                            "UNRESOLVED naming its missing producer -- a bare "
                            "null would be silence (section 5)."})
        return res
    res["measured_at_the_wrong_setting"] = seg.get("per_field", {})
    res["worst_field"] = seg.get("worst_field")
    res["worst_initRes"] = seg.get("worst_initRes")
    res["G-CONV_verdict_at_the_wrong_setting"] = seg.get("verdict")
    res["bar_state"] = BAR_PRODUCED
    if seg.get("verdict") == "PASS":
        res.update({"verdict": "FALSIFIED",
                    "withdraws": True,
                    "withdraws_gate": F5_NAMED_GATE,
                    "note": "the DELIBERATELY WRONG setting PASSED G-CONV. "
                            "G-CONV's verdict is WITHDRAWN and this item makes "
                            "no claim about the repair."})
    elif seg.get("verdict") == "GATE FAIL":
        res.update({"verdict": "AS PREDICTED", "withdraws": False,
                    "note": "the wrong setting failed the gate it names, as "
                            "registered. G-CONV stands."})
    else:
        res.update({"verdict": "UNRESOLVED", "withdraws": False,
                    "bar_state": BAR_NOT_PRODUCED,
                    "producing_leg": NULL_READINGS["F5"]["producing_leg"],
                    "note": "L3 produced no gradeable reading (%s)."
                            % seg.get("verdict")})
    return res


# ------------------------------------------------------------ G-SOLN
def gate_soln(root, census, legs):
    """`G-SOLN`, section 3.2.  NEW AND GATED.  THE ANTI-CHEAT GATE.

    The one honest objection to this item is that a different `fvSolution`
    computes a different ANSWER, not a better-converged one.  `N-D42` shows
    that `primalMinResTolDiff` computes the SAME answer and changes only the
    LABEL; NO SUCH RESULT EXISTS for a linear-solver stopping rule, so it is
    MEASURED here rather than assumed.

    A `GATE FAIL` means the change MOVED THE SOLUTION.  The repair would then
    be a different case, not a better solve, and NO `G-CONV` PASS MAY BE
    QUOTED AS `D6RF3`'s ANSWER."""
    res = {"gate": "G-SOLN_solution_unmoved", "point": G_SOLN_POINT,
           "rel_tol": G_SOLN_REL_TOL,
           "reference": {"CD": G_SOLN_CD_D6RF3, "CL": G_SOLN_CL_D6RF3,
                         "source": ("D6RF3 F_mp_20260905T222250Z_43793.log "
                                    ":2098-:2099, Time = 1000. MEASURED.")},
           "predicted_rel": G_SOLN_PREDICTED_REL,
           "the_inequality": ("predicted 1e-05 < bar 1e-03 -- predicted PASS "
                              "with two decades of margin"),
           "consequence_of_a_GATE_FAIL": (
               "the fvSolution change MOVED THE SOLUTION rather than "
               "converging it; the repair is then a different case and no "
               "G-CONV PASS may be quoted as D6RF3's answer.")}
    producer = ARTEFACT_PRODUCER["d6rf4_fd_endpoint.json"]
    if census[producer]["state"] != "RAN":
        _r, _d = _no_input_reason(census, producer, None, root)
        res.update(dict({"verdict": "NOT A RESULT", "reason": _r}, **_d))
        res.update(NULL_READINGS["G-SOLN"])
        return res
    seg = (legs.get("segments") or {}).get("L1")
    if not seg or seg.get("CD") is None or seg.get("CL") is None:
        res.update({"verdict": "NOT A RESULT",
                    "reason": "SEGMENT_NOT_PRODUCED",
                    "bar_state": BAR_NOT_PRODUCED,
                    "producing_leg": NULL_READINGS["G-SOLN"]["producing_leg"],
                    "legs_seen": sorted(legs.get("segments", {})),
                    "note": "L1 produced no CD/CL line, so there is nothing "
                            "to compare. NOT A RESULT for want of an input."})
        return res
    try:
        cd = _ff(seg["CD"], os.path.basename(legs["log"]), "L1.CD")
        cl = _ff(seg["CL"], os.path.basename(legs["log"]), "L1.CL")
    except NonFinite as e:
        return _nar_non_finite(res, e)
    res["measured"] = {"CD": cd, "CL": cl, "final_time": seg["final_time"]}
    res["rel_CD"] = abs(cd - G_SOLN_CD_D6RF3) / abs(G_SOLN_CD_D6RF3)
    res["rel_CL"] = abs(cl - G_SOLN_CL_D6RF3) / abs(G_SOLN_CL_D6RF3)
    res["worst_rel"] = max(res["rel_CD"], res["rel_CL"])
    res["bar_state"] = BAR_PRODUCED
    res["verdict"] = ("PASS" if res["worst_rel"] <= G_SOLN_REL_TOL
                      else "GATE FAIL")
    return res


# ---------------------------------------------------------------- G-FD
def gate_fd(root, census):
    art = "d6rf4_fd_endpoint.json"
    producer = ARTEFACT_PRODUCER[art]
    base = {"gate": "G-FD_bright_line_on_J", "artefact": art,
            "producing_arm": producer, "band_pct": FD_BAND_PCT,
            "aggregate_band_pct": AGG_BAND_PCT,
            "plateau_tol_pct": PLATEAU_TOL_PCT,
            "sign_flip_pathology_at": SIGN_FLIP_PATHOLOGY,
            "band_provenance": "band D, inherited BY CITATION from D6R "
                               "PREREGISTRATION.md section 3e; NOT re-derived"}
    if census[producer]["state"] != "RAN":
        _r, _d = _no_input_reason(census, producer, art, root)
        base.update(dict({"verdict": "NOT A RESULT", "reason": _r},
                         **_d))
        base.update(NULL_READINGS["G-FD"])
        base["bar_state"] = BAR_NOT_PRODUCED
        base["plateau_bar_state"] = BAR_NOT_PRODUCED
        base["plateau_bar_exercised"] = None
        base["plateau_bar_report"] = (
            "section 12.4: NO COMPONENT WAS GRADED, so the %.1f %% plateau bar "
            "was NOT PRODUCED and is NOT EXERCISED. It is reported as its own "
            "state and is NEVER inferred from the absence of a failure. %s"
            % (PLATEAU_TOL_PCT, PLATEAU_BAR_UNINFORMATIVE_EVIDENCE))
        return base
    path = os.path.join(root, ARM_DIR[producer], art)
    if not os.path.isfile(path):
        refuse("G-FD", {"artefact_absent_although_producer_ran": path})
    doc = read_fd(path)
    comps, flips, num, den = [], 0, 0.0, 0.0
    n_planned = 0
    n_nonfinite = 0
    for r in doc["rows"]:
        c = {"dv": r["dv"], "idx": r["idx"], "status": r["status"]}
        if r["status"] != "PLANNED":
            c["verdict"] = "NOT A RESULT"
            c["reason"] = "component status %s -- no FD was taken" % r["status"]
            comps.append(c)
            continue
        lo, hi = r.get("s_lo") or {}, r.get("s_hi") or {}
        if not (lo.get("ok") and hi.get("ok")):
            c["verdict"] = "NOT A RESULT"
            c["reason"] = "an FD step did not evaluate"
            c["s_lo_ok"], c["s_hi_ok"] = lo.get("ok"), hi.get("ok")
            comps.append(c)
            continue
        n_planned += 1
        d_hi, d_lo, jadj = hi["d"], lo["d"], r["J_adj"]
        # ---- section 3f, per component -----------------------------------
        try:
            jadj = _ff(jadj, art, "rows[%s[%s]].J_adj" % (r["dv"], r["idx"]))
            d_lo = _ff(d_lo, art, "rows[%s[%s]].fd.s_lo.d" % (r["dv"], r["idx"]))
            d_hi = _ff(d_hi, art, "rows[%s[%s]].fd.s_hi.d" % (r["dv"], r["idx"]))
        except NonFinite as e:
            c.update(_nar_non_finite({}, e))
            n_nonfinite += 1
            comps.append(c)
            continue
        c.update({"J_adj": jadj, "d_s_lo": d_lo, "d_s_hi": d_hi,
                  "step_lo": lo["step"], "step_hi": hi["step"]})
        c["rel_err_pct"] = (abs(d_hi - jadj) / abs(d_hi) * 100.0
                            if d_hi != 0.0 else float("inf"))
        c["plateau_pct"] = (abs(d_hi - d_lo) / abs(d_hi) * 100.0
                            if d_hi != 0.0 else float("inf"))
        # ---- the plateau, per DAFOAM_CHARTER.md section 3 and section 20 ---
        # The `s_lo`/`s_hi` pair IS `VERIFICATION_CHARTER.md` section 7 step
        # 1's "two or three point mini-sweep", which section 3 delegates the
        # definition to and section 20 (addendum 2026-09-04) RULES satisfies
        # section 3.  No shortfall caveat is printed and none is owed.
        # WHAT IS PRINTED, because it is TRUE and is strength of evidence
        # rather than compliance: the pair is graded at `s_hi` with its only
        # neighbour BELOW, so the coarse side is unmeasured.  This family has a
        # measured instance of that blind side firing.
        c["plateau_proved_against"] = [lo["step"]]
        c["plateau_graded_at"] = hi["step"]
        c["plateau_sidedness"] = "ONE-SIDED (fine side only; coarse unmeasured)"
        c["plateau_authority"] = (
            "VERIFICATION_CHARTER.md:854-855 step 1, two-or-three-point "
            "mini-sweep; DAFOAM_CHARTER.md section 3 delegates to it and "
            "section 20 rules that a two-point mini-sweep SATISFIES section 3")
        c["coarse_side_note"] = (
            "A third, COARSER point is the cheapest evidence available and is "
            "a STRENGTHENING, not a duty; declining it is not a breach "
            "(DAFOAM_CHARTER.md section 20.2). Measured instance of the blind "
            "side firing: D15_D16_FD_STEP_TABLE.md:234, D16 PATCHED CL "
            "shape[6], 14.0978 % coarse-side deviation against 1.1268 % "
            "fine-side. THIS ITEM DECLINES THE THIRD POINT AND SAYS SO.")
        c["sign_flip"] = (d_hi * jadj) < 0.0
        if c["sign_flip"]:
            flips += 1
        c["in_band"] = c["rel_err_pct"] <= FD_BAND_PCT
        c["plateau_pass"] = c["plateau_pct"] <= PLATEAU_TOL_PCT
        c["verdict"] = ("PASS" if (c["in_band"] and c["plateau_pass"]
                                   and not c["sign_flip"]) else "GATE FAIL")
        num += (d_hi - jadj) ** 2
        den += d_hi ** 2
        comps.append(c)
    base["components"] = comps
    # ============ section 12.4's REGISTERED REPORT, EXECUTABLE =============
    # EVERY component's measured `plateau_pct` is printed BESIDE the bar with
    # its clearance factor, AND the record STATES WHETHER THE BAR WAS
    # EXERCISED AT ALL.  Inherited from D6RF3 as a requirement; made
    # executable here because a requirement nobody can fail is a preference
    # (DAFOAM_CHARTER.md section 13's own sentence).
    _graded = [c for c in comps if isinstance(c.get("plateau_pct"), float)
               and math.isfinite(c["plateau_pct"])]
    _rejected = [c for c in _graded if not c.get("plateau_pass")]
    base["plateau_bar_pct"] = PLATEAU_TOL_PCT
    base["plateau_per_component"] = [
        {"component": "%s[%s]" % (c["dv"], c["idx"]),
         "plateau_pct_measured": c["plateau_pct"],
         "bar_pct": PLATEAU_TOL_PCT,
         "clearance_factor": (PLATEAU_TOL_PCT / c["plateau_pct"]
                              if c["plateau_pct"] > 0 else None),
         "admitted_by_the_bar": bool(c.get("plateau_pass")),
         "rel_err_pct": c.get("rel_err_pct"),
         "band_D_pct": FD_BAND_PCT,
         "which_bar_actually_decided": (
             "band D at %.1f %%" % FD_BAND_PCT
             if c.get("plateau_pass") and not c.get("in_band")
             else ("the plateau bar at %.1f %%" % PLATEAU_TOL_PCT
                   if not c.get("plateau_pass") else "NEITHER -- both passed"))}
        for c in _graded]
    # THREE STATES, NOT TWO.  Caught by the end-to-end drive: with ZERO graded
    # components the two-state form printed "every graded component sat inside
    # the bar", which is a claim about components that do not exist -- the
    # NOT-EXERCISED token's own hazard, one level up.  `P_conv` grades no FD
    # component at all, so this is the state the REGISTERED arm actually lands
    # in and it must not read as a quiet pass.
    base["n_graded_components"] = len(_graded)
    base["plateau_bar_exercised"] = None if not _graded else bool(_rejected)
    base["plateau_bar_state"] = (
        BAR_NOT_PRODUCED if not _graded
        else (PLATEAU_BAR_EXERCISED if _rejected else PLATEAU_BAR_NOT_EXERCISED))
    base["plateau_bar_rejected_components"] = [
        "%s[%s]" % (c["dv"], c["idx"]) for c in _rejected]
    base["plateau_bar_structure"] = (
        "CONJUNCTION, not exclusion: verdict = PASS if in_band AND "
        "plateau_pass AND not sign_flip. Band D at %.1f %% binds BEFORE the "
        "plateau bar at %.1f %%, so a component the loose bar admits fails the "
        "agreement band anyway. DAFOAM_CHARTER.md section 21.4 names this the "
        "structure where the plateau bar is REDUNDANT rather than "
        "load-bearing; this item does NOT migrate to the exclusion structure."
        % (FD_BAND_PCT, PLATEAU_TOL_PCT))
    base["plateau_bar_report"] = (
        ("ZERO components were graded, so the %.1f %% plateau bar was NOT "
         "PRODUCED. It was not exercised, it did not pass, and it decided "
         "NOTHING here -- which is the expected state of the P_conv arm, "
         "because P_conv buys a CONVERGENCE measurement and takes no FD step "
         "at all (PREREGISTRATION.md section 8.2 and section 9 item 6). "
         "Producing leg: %s." % (PLATEAU_TOL_PCT,
                                 NULL_READINGS["G-FD"]["producing_leg"]))
        if not _graded else
        ("%d of %d graded component(s) were REJECTED by the %.1f %% plateau "
         "bar, so the bar was EXERCISED here and its pass carries information."
         % (len(_rejected), len(_graded), PLATEAU_TOL_PCT)) if _rejected else
        ("NO graded component was rejected by the %.1f %% plateau bar, so THE "
         "BAR WAS NOT EXERCISED HERE and a pass on it carries NO INFORMATION "
         "about the bar. %s" % (PLATEAU_TOL_PCT,
                                PLATEAU_BAR_UNINFORMATIVE_EVIDENCE)))
    base["n_planned"] = n_planned
    base["n_non_finite_components"] = n_nonfinite
    base["sign_flips"] = flips
    base["eta_used"] = doc["eta_used"]
    base["eta_floored"] = doc["eta_floored"]
    base["plateau_authority"] = (
        "VERIFICATION_CHARTER.md:854-855 step 1's two-or-three-point "
        "mini-sweep. DAFOAM_CHARTER.md section 20 rules that the two-point "
        "ladder SATISFIES section 3; NO SHORTFALL CAVEAT IS OWED and printing "
        "one would be a false self-deprecation.")
    # ---- section 3f on eta: the aggregate is scaled by it ------------------
    try:
        _ff(doc["eta_used"], art, "eta_used")
    except NonFinite as e:
        return _nar_non_finite(base, e)
    if n_planned == 0:
        base.update({"verdict": "NOT A RESULT",
                     "reason": ("no component produced a usable FD pair"
                                if n_nonfinite == 0 else
                                "no component produced a FINITE FD pair; %d "
                                "were non-finite" % n_nonfinite)})
        return base
    agg = (math.sqrt(num) / math.sqrt(den) * 100.0
           if den > 0 else float("inf"))
    # ---- section 3f on the aggregate --------------------------------------
    # `inf` is non-finite and reaches here when every `d_hi` is zero.  It is
    # NOT a 100 %-style failure to be graded GATE FAIL; it is an absent
    # measurement wearing a float's type.
    if not math.isfinite(agg):
        return _nar_non_finite(base, NonFinite(
            art, "aggregate_rel_err_pct", repr(agg)))
    base["aggregate_rel_err_pct"] = agg
    base["aggregate_pass"] = base["aggregate_rel_err_pct"] <= AGG_BAND_PCT
    if flips >= SIGN_FLIP_PATHOLOGY:
        base["pathology_NOT_A_RESULT"] = True
        base["verdict"] = "NOT A RESULT"
        base["reason"] = ("%d sign flips >= the registered pathology threshold "
                          "%d -- named in advance" % (flips, SIGN_FLIP_PATHOLOGY))
        return base
    base["pathology_NOT_A_RESULT"] = False
    per_ok = all(c.get("verdict") == "PASS" for c in comps
                 if c.get("status") == "PLANNED" and "verdict" in c
                 and c.get("rel_err_pct") is not None)
    any_nar = any(c.get("verdict") == "NOT A RESULT" for c in comps)
    if any_nar:
        base["verdict"] = "NOT A RESULT"
        base["reason"] = "at least one registered component produced no FD pair"
    else:
        base["verdict"] = "PASS" if (per_ok and base["aggregate_pass"]) else "GATE FAIL"
    return base


# ------------------------------------------------------- G-OFF / G-PRICE
def _major_history(root, census):
    art = "d6rf4_major_history.json"
    producer = ARTEFACT_PRODUCER[art]
    if census[producer]["state"] != "RAN":
        return None, producer, art
    path = os.path.join(root, ARM_DIR[producer], art)
    if not os.path.isfile(path):
        refuse("MAJOR_HISTORY", {"absent_although_producer_ran": path})
    with open(path) as fh:
        return json.load(fh), producer, art


def _cd_path(root, census):
    """The path of section 2a's registered CD source, or None if its producing
    arm did not run."""
    producer = ARTEFACT_PRODUCER[CD_ARTEFACT]
    if census[producer]["state"] != "RAN":
        return None, producer
    p = os.path.join(root, ARM_DIR[producer], CD_ARTEFACT)
    if not os.path.isfile(p):
        refuse("CD_SOURCE", {"absent_although_producer_ran": p})
    return p, producer


def gate_off(root, census):
    """G-OFF, section 3a.  RE-POINTED: `CD_i(mp)` is section 2a's source.

    `d6rf2_grade.py:760` read `hist["CD_<pt>"][-1]` from the producing
    optimiser's history.  D6RF3-DEF-4 established by COMPLETE ENUMERATION that
    the history holds no CD at all, and D6RF3-DEF-5 established that its last
    row is `NaN` throughout -- so on the frozen parent, had the extractor not
    refused first, all three points would have read `GATE FAIL` off a
    non-number, because `NaN <= cd_ref` is False."""
    res = {"gate": "G-OFF_per_point",
           "artefacts": [CD_ARTEFACT, "d6rf4_ref_off.json"],
           "CD_mp_source": CD_MP_SOURCE_LABEL,
           "CD_mp_source_statement": CD_MP_SOURCE_STATEMENT,
           "caveat": ("The producing optimisation exited `Invalid number in "
                      "NLP function or derivative detected.` (D6R "
                      "O_mp/opt_IPOPT.txt:822, G-D6R-OPT UNCLASSIFIED) and 687 "
                      "of its 863 recorded funcs rows are non-finite. The "
                      "endpoint is a design point, not an optimum, and this "
                      "gate makes no optimality claim."),
           "per_point": {}}
    cdp, cdprod = _cd_path(root, census)
    if cdp is None:
        _r, _d = _no_input_reason(census, cdprod, CD_ARTEFACT, root)
        res.update(dict({"verdict": "NOT A RESULT", "reason": _r,
                         "artefact": CD_ARTEFACT,
                         "per_point": {p: {"verdict": "NOT A RESULT",
                                           "reason": _r,
                                           "CD_mp_source": CD_MP_SOURCE_LABEL}
                                       for p in POINTS}}, **_d))
        res.update(NULL_READINGS["G-OFF"])
        return res
    if census["REF_off"]["state"] != "RAN":
        _r, _d = _no_input_reason(census, "REF_off", "d6rf4_ref_off.json", root)
        res.update(dict({"verdict": "NOT A RESULT", "reason": _r,
                         "artefact": "d6rf4_ref_off.json",
                         "per_point": {p: {"verdict": "NOT A RESULT",
                                           "reason": _r,
                                           "CD_mp_source": CD_MP_SOURCE_LABEL}
                                       for p in POINTS}}, **_d))
        res.update(NULL_READINGS["G-OFF"])
        return res
    rp = os.path.join(root, ARM_DIR["REF_off"], "d6rf4_ref_off.json")
    if not os.path.isfile(rp):
        refuse("G-OFF", {"artefact_absent_although_producer_ran": rp})
    with open(rp) as fh:
        ref = json.load(fh)
    verds = []
    for p in POINTS:
        row = {"CL_target": CL_TARGETS[p], "CD_mp_source": CD_MP_SOURCE_LABEL,
               "CD_mp_key": "points.%s.CD" % p, "CD_mp_artefact": CD_ARTEFACT}
        if p not in ref.get("points", {}):
            refuse("G-OFF", {"ref_off_missing_point": p})
        try:
            # ONE reader for CD, shared with the section 3e control.
            cd_mp = _ff(cdc.read_cd(cdp, p), CD_ARTEFACT, "points.%s.CD" % p)
            cd_ref = _ff(ref["points"][p]["CD"], "d6rf4_ref_off.json",
                         "points.%s.CD" % p)
            cl_ref = _ff(ref["points"][p]["CL"], "d6rf4_ref_off.json",
                         "points.%s.CL" % p)
        except cdc.CDRefusal as e:
            refuse("G-OFF", {"cd_reader_refused": str(e)[:1200]})
        except NonFinite as e:
            row.update(_nar_non_finite({}, e))
            res["per_point"][p] = row
            verds.append("NOT A RESULT")
            continue
        v = "PASS" if cd_mp <= cd_ref else "GATE FAIL"
        verds.append(v)
        row.update({"CD_mp": cd_mp, "CD_REF_off": cd_ref, "CL_REF_off": cl_ref,
                    "gain_REF_minus_mp": cd_ref - cd_mp, "verdict": v})
        res["per_point"][p] = row
    res["verdict"] = ("NOT A RESULT" if "NOT A RESULT" in verds else
                      ("PASS" if all(v == "PASS" for v in verds)
                       else "GATE FAIL"))
    return res


def report_cdlog(root, census, g1=None, legs=None):
    """`X-CDLOG`, section 3d.  REPORTED, NOT GATED.  NO THRESHOLD, NO VERDICT,
    AND IT MOVES NOTHING.

    Section 2b's registered reasons for demoting the stdout reconstruction to a
    cross-check: the SERIES is not reconstructable (977 converged primal
    terminations against the 2,589 point-primals implied by 863 major rows,
    distributed 760/110/98); the registered instrument's own docstring chose
    the history file over stdout because it is immune to the MPI interleave;
    and it cannot become the gated source without becoming outcome-selected
    (section 5).  A disagreement here is a FINDING TO BE REPORTED and does not
    move any gate, because the gated source was fixed before either number
    existed."""
    res = {"row": "X-CDLOG_stdout_cross_check", "gating": False,
           "threshold": None, "verdict": None,
           "log_source": CDLOG_SOURCE,
           "log_lines": CDLOG_LINES,
           "CD_log_at_last_finite_major": CDLOG,
           "composite_identity": {
               "weights": WEIGHTS,
               "J_history_row_998": CDLOG_J_AT_ROW_998,
               "residual_abs": CDLOG_COMPOSITE_RESID_ABS,
               "residual_rel": CDLOG_COMPOSITE_RESID_REL,
               "note": "sum(w_i*CD_i) against the history's J at the last "
                       "FINITE major, at the log's 10-significant-figure "
                       "print precision. It grades nothing and has no "
                       "direction."},
           "why_not_gated": ("section 2b, three registered reasons; and the "
                             "gated source was fixed before either number "
                             "existed"),
           "per_point": {}}
    cdp, cdprod = _cd_path(root, census)
    if cdp is None:
        # ============ D6RF4-DEF-7, THE REPAIR, AT ITS OWN SITE =============
        # THE PARENT HAD ONE BRANCH AND ONE TOKEN HERE: `ARM_DID_NOT_RUN`.
        # D6RF3's arm RAN, for 2.067 core-min, and this row would have said
        # the arm did not run.  Three distinguishable states are registered
        # now, and `_no_input_reason` picks between them from the CENSUS and
        # the DISK rather than from a single default.
        _r, _d = _no_input_reason(census, cdprod, CD_ARTEFACT, root)
        res.update(dict({"verdict": None, "reason": _r,
                         "artefact": CD_ARTEFACT,
                         "row_state": "NOT PRODUCED"}, **_d))
        res.update({k: v for k, v in NULL_READINGS["X-CDLOG"].items()})
        if _r == ARM_RAN_ARTEFACT_NOT_WRITTEN:
            res["arm_rc"] = ((g1 or {}).get("arms", {})
                             .get(cdprod, {}).get("rc"))
            res["arm_core_min"] = ((g1 or {}).get("arms", {})
                                   .get(cdprod, {}).get("core_min"))
            res["last_leg_completed"] = ((legs or {}).get("last_leg_completed"))
            res["legs_seen"] = sorted((legs or {}).get("segments", {}))
            res["def7_statement"] = (
                "THE ARM RAN AND THE GATED ARTEFACT WAS NOT WRITTEN. The "
                "producer now writes `points.<pt>.CD` AS EACH BASELINE "
                "POINT-PRIMAL COMPLETES, BEFORE ANY FD LEG "
                "(d6rf4_fd_endpoint.py `_write_out`), so a run that dies at "
                "point k still leaves points 0..k-1 readable. Reaching this "
                "branch after a run therefore means the arm died BEFORE its "
                "first baseline primal completed, and the record says that "
                "instead of accusing the arm of never starting.")
        res["per_point"] = {p: {"row_state": "NOT PRODUCED", "reason": _r,
                                "CD_mp_source": CD_MP_SOURCE_LABEL}
                            for p in POINTS}
        return res
    missing = []
    for p in POINTS:
        try:
            cd_b = _f(cdc.read_cd(cdp, p))
        except cdc.CDRefusal as e:
            # A PARTIAL SOURCE REPORTS PARTIALLY; IT NEVER REPORTS SILENTLY.
            # The present points are reported and each missing point reads
            # NOT PRODUCED BY NAME (section 4, token set 3 of 3).
            missing.append(p)
            res["per_point"][p] = {"row_state": "NOT PRODUCED",
                                   "reason": "POINT_ABSENT_FROM_SOURCE",
                                   "producing_leg": NULL_READINGS["X-CDLOG"]["producing_leg"],
                                   "artefact": cdp,
                                   "unreadable": str(e)[:400]}
            continue
        finite = math.isfinite(cd_b)
        rel = (abs(cd_b - CDLOG[p]) / abs(CDLOG[p])) if finite else None
        res["per_point"][p] = {"CD_baseline_primal": cd_b,
                               "CD_log_last_finite_major": CDLOG[p],
                               "abs_rel_difference": rel,
                               "finite": finite,
                               "CD_mp_source": CD_MP_SOURCE_LABEL}
    # Falsifier F1 (section 8), REPORTED: the primal's own repeatability,
    # measured in the same run as |J - J_repeat|, is the yardstick the
    # disagreement is read against.  F1 is a reported falsifier and does NOT
    # move G-OFF or G-PRICE.
    try:
        with open(cdp) as fh:
            doc = json.load(fh)
        res["F1_yardstick_eta_raw"] = _f(doc.get("eta_raw", "nan"))
        res["F1_statement"] = (
            "If points.<pt>.CD disagrees with the stdout reconstruction by "
            "more than the primal's own repeatability (eta_raw), section 2a's "
            "premise that the baseline primal measures the same physical "
            "quantity the log recorded is FALSE and this item reports that as "
            "its finding. REPORTED, not gated.")
    except (OSError, ValueError):
        res["F1_yardstick_eta_raw"] = None
    return res


def gate_price(root, census, controls):
    res = {"gate": "G-PRICE_single_point", "band": list(PRICE_BAND),
           "reference_recorded": CD_F_D4_RECORDED,
           "reference_source": D4_OPT_IPOPT}
    cd_f, where = read_d4_cd_f(D4_OPT_IPOPT)
    res["reference_reread"] = cd_f
    res["reference_line"] = where
    res["planted_control"] = controls.get("price_control", {}).get(
        "reader_saw_the_plant")
    res["planted_control_state"] = controls.get("price_control", {}).get("state")
    res["cd_planted_control_state"] = controls.get("cd_control", {}).get("state")
    res["CD_mp_source"] = CD_MP_SOURCE_LABEL
    res["CD_mp_source_statement"] = CD_MP_SOURCE_STATEMENT
    res["band_provenance"] = (
        "[0, 1.0e-3] and the negative -> NOT A RESULT limb are D6RF's, carried "
        "BYTE-FOR-BYTE and NOT WIDENED. Sanaa's standing boundary, 2026-09-04: "
        "`it never means adjusting the gate until the answer fits.`")
    if cd_f != CD_F_D4_RECORDED:
        refuse("G-PRICE", {"D4_reference_moved": {"recorded": CD_F_D4_RECORDED,
                                                  "reread": cd_f}})
    cdp, cdprod = _cd_path(root, census)
    if cdp is None:
        _r, _d = _no_input_reason(census, cdprod, CD_ARTEFACT, root)
        res.update(dict({"verdict": "NOT A RESULT", "reason": _r,
                         "artefact": CD_ARTEFACT}, **_d))
        res.update(NULL_READINGS["G-PRICE"])
        return res
    try:
        cd_mp = _ff(cdc.read_cd(cdp, "cl05"), CD_ARTEFACT, "points.cl05.CD")
    except cdc.CDRefusal as e:
        refuse("G-PRICE", {"cd_reader_refused": str(e)[:1200]})
    except NonFinite as e:
        # D6RF3-DEF-5's exact repair.  The parent computed `NaN - cd_f = NaN`,
        # found `NaN < 0.0` False so the registered `negative -> NOT A RESULT`
        # limb did NOT fire, found `NaN <= 1.0e-3` False so the PASS limb did
        # not fire, and reached `else` -> GATE FAIL.  A verdict manufactured
        # from a non-number.  It is NOT A RESULT here, and it is NOT A RESULT
        # for the stated reason, naming the artefact and the key.
        return _nar_non_finite(res, e)
    price = cd_mp - cd_f
    res["CD_cl05_mp"] = cd_mp
    res["price"] = price
    if price < 0.0:
        res["verdict"] = "NOT A RESULT"
        res["reason"] = ("a negative price is a finding about D4, named in "
                         "advance as pending triage")
    elif price <= PRICE_BAND[1]:
        res["verdict"] = "PASS"
    else:
        res["verdict"] = "GATE FAIL"
    return res


def report_reduction(root, census):
    """REPORTED, NOT GATED (Sanaa 2026-09-03 ~20:00Z)."""
    res = {"row": "R-RED_composite_reduction", "gating": False,
           "band_pct_for_reference": list(RED_BAND_PCT),
           "why_not_gated": ("the producing optimisation exited on a "
                             "non-finite objective (G-D6R-OPT UNCLASSIFIED), "
                             "so a reduction along its trajectory is a number, "
                             "not a claim about a converged optimum")}
    hist, hp, ha = _major_history(root, census)
    if hist is None:
        _r, _d = _no_input_reason(census, hp, ha, root)
        res.update(dict({"value_pct": None, "reason": _r}, **_d))
        res.update(NULL_READINGS["R-RED"])
        return res
    J = [_f(v) for v in hist["J"]]
    res["n_major"] = len(J)
    res["n_non_finite_J"] = sum(1 for v in J if not math.isfinite(v))
    # ---- section 3c + section 3f: THE NON-FINITE DISCLOSURE ----------------
    # `J_f` from this history IS non-finite (D6RF3-DEF-5: the last row of the
    # producing history is index 1006 and every one of its `funcs` is NaN).
    # The row must SAY SO rather than print a number derived from one.  This
    # is a REPORTED row, so there is no verdict to make NOT A RESULT -- the
    # disclosure is the whole obligation, and a reduction printed from a NaN
    # would be exactly the "evidence annotated as non-binding" failure.
    try:
        j0 = _ff(J[0], "d6rf4_major_history.json", "J[0]")
        jf = _ff(J[-1], "d6rf4_major_history.json", "J[-1]")
    except NonFinite as e:
        res.update({"J0": J[0], "Jf": J[-1], "value_pct": None,
                    "reason": NON_FINITE_REASON, "non_finite": e.detail,
                    "inside_reference_band": None,
                    "disclosure": (
                        "NO REDUCTION IS PRINTED. %d of %d recorded J values "
                        "in this history are non-finite and the endpoint row "
                        "is one of them. A percentage computed from a NaN is "
                        "not a small number, it is not a number."
                        % (res["n_non_finite_J"], res["n_major"]))})
        return res
    res["J0"], res["Jf"] = j0, jf
    res["value_pct"] = (j0 - jf) / j0 * 100.0 if j0 != 0 else None
    res["inside_reference_band"] = (
        res["value_pct"] is not None
        and RED_BAND_PCT[0] <= res["value_pct"] <= RED_BAND_PCT[1])
    return res


# ------------------------------------------------------------- composition
def compose(g1, dvl, fd, off, price, caps, tool, place, census,
            conv=None, soln=None, f5=None):
    """THE REGISTERED VERDICT LADDER, in order.  A NOT A RESULT can only turn a
    PASS or GATE FAIL INTO a NOT A RESULT, never the reverse."""
    reasons = []
    ran = [a for a in ARMS if census[a]["state"] == "RAN"]
    notrun = [a for a in ARMS if census[a]["state"] != "RAN"]

    # ---- rung 0: ANY GATED INPUT NON-FINITE, INCLUDING THE LEDGER ---------
    # HOISTED ABOVE rung 1 when section 3f was widened to `G-CAPS` and `G1`
    # (2026-09-05, pre-compute), and the hoist changes the REASON REPORTED, NOT
    # THE VERDICT: rung 1 also returns `NOT A RESULT`, so no row moves between
    # tokens and nothing that could previously have failed can now pass.
    #
    # It is hoisted because a non-finite `core_min` sets `clauses_all_pass`
    # False, so WITHOUT the hoist the item would report "completion clause
    # failed on arm X" -- an accusation that the RUN misbehaved -- when what
    # actually happened is that a bookkeeping FIELD was unreadable. That is
    # `bookkeeping never voids physics` inverted: it would be bookkeeping
    # SLANDERING physics. The artefact and key are named instead.
    nf0 = []
    for src in (g1, caps):
        if src.get("reason") == NON_FINITE_REASON:
            nf0.append({"gate": src.get("gate"),
                        "non_finite": src.get("non_finite")})
        for arm, row in (src.get("arms") or {}).items():
            if isinstance(row, dict) and row.get("reason") == NON_FINITE_REASON:
                nf0.append({"gate": src.get("gate"), "arm": arm,
                            "non_finite": row.get("non_finite")})
    if nf0:
        reasons.append("rung 0: a LEDGER field a gate compares against a "
                       "threshold is NON-FINITE, artefact and key named: %s. "
                       "This is NOT a completion-clause failure and is not "
                       "reported as one -- the run is not accused of "
                       "misbehaving because a bookkeeping field was "
                       "unreadable."
                       % json.dumps(nf0, sort_keys=True, default=str)[:1200])
        return "NOT A RESULT", reasons

    dirty = [a for a in ran if not g1["arms"][a].get("clauses_all_pass")]
    if dirty:
        reasons.append("rung 1: completion clause failed on arm(s) %s" % dirty)
        return "NOT A RESULT", reasons
    if notrun:
        reasons.append("rung 2: registered arm(s) %s did not run; the item can "
                       "never be PASS with an arm unbought" % notrun)
        return "NOT A RESULT", reasons
    # ---- rung 3: ANY GATED INPUT NON-FINITE (section 3f, D6RF3-DEF-5) ------
    # Placed ABOVE the G-DVL and pathology rungs deliberately.  A gate whose
    # input was a NaN did not measure the thing its name says, so its GATE FAIL
    # or PASS is not evidence about the design point OR about the gradient, and
    # attributing it to either would be the confident wrong finding.
    nf = []
    for g in (dvl, fd, off, price, conv or {}, soln or {}):
        if g.get("reason") == NON_FINITE_REASON:
            nf.append({"gate": g.get("gate"), "non_finite": g.get("non_finite")})
        for p, row in (g.get("per_point") or {}).items():
            if row.get("reason") == NON_FINITE_REASON:
                nf.append({"gate": g.get("gate"), "point": p,
                           "non_finite": row.get("non_finite")})
        for c in (g.get("components") or []):
            if c.get("reason") == NON_FINITE_REASON:
                nf.append({"gate": g.get("gate"),
                           "component": "%s[%s]" % (c.get("dv"), c.get("idx")),
                           "non_finite": c.get("non_finite")})
        # G-CONV reports PER LEG and PER FIELD, a shape the parent had no gate
        # in.  A rung that cannot see a gate's disclosure is a rung that
        # reports the wrong reason for the right verdict.
        for leg, row in (g.get("per_leg") or {}).items():
            for fld, c in (row.get("per_field") or {}).items():
                if isinstance(c, dict) and c.get("reason") == NON_FINITE_REASON:
                    nf.append({"gate": g.get("gate"), "leg": leg,
                               "field": fld, "non_finite": c.get("non_finite")})
    if nf:
        reasons.append("rung 3: gated input(s) NON-FINITE, artefact and key "
                       "named: %s" % json.dumps(nf, sort_keys=True,
                                                default=str)[:1500])
        return "NOT A RESULT", reasons
    # ---- rung 3a: F5's WITHDRAWAL CLAUSE, AND IT WITHDRAWS THE GATE IT ----
    # ---- NAMES AND NO OTHER (DAFOAM_CHARTER.md section 21.3). -------------
    # A falsifier pointed at gate A cannot license a withdrawal of gate B's
    # verdict: it was never a test of B.  F5 names G-CONV, and G-CONV is what
    # this rung withdraws.
    if (f5 or {}).get("withdraws"):
        reasons.append(
            "rung 3a: falsifier F5 FIRED -- the DELIBERATELY WRONG setting "
            "(D6RF3's original fvSolution, L3) ALSO passed %s. That gate is "
            "therefore not measuring the linear-solver stopping rule, "
            "section 1.3's mechanism is refuted, %s's VERDICT IS WITHDRAWN "
            "and NO CLAIM ABOUT THE REPAIR MAY BE MADE FROM THIS ITEM. "
            "F5 detail: %s"
            % (f5.get("named_gate"), f5.get("named_gate"),
               json.dumps({k: f5.get(k) for k in
                           ("worst_field", "worst_initRes",
                            "G-CONV_verdict_at_the_wrong_setting")},
                          sort_keys=True, default=str)[:600]))
        return "NOT A RESULT", reasons
    # ---- rung 3b: G-SOLN GATE FAIL -- THE SOLUTION MOVED ------------------
    # Section 3.2's own registered consequence.  A tightened fvSolution that
    # computes a DIFFERENT answer is a different case, not a better solve, so
    # no G-CONV PASS may be quoted as D6RF3's answer.  STRICTLY RESTRICTIVE:
    # it can only turn a PASS or a GATE FAIL INTO a NOT A RESULT.
    if (soln or {}).get("verdict") == "GATE FAIL":
        reasons.append(
            "rung 3b: G-SOLN GATE FAIL -- the tightened fvSolution MOVED THE "
            "SOLUTION (worst relative difference %s against a bar of %s at "
            "point %s) rather than converging it. The repair is then a "
            "DIFFERENT CASE, not a better solve, and NO G-CONV PASS MAY BE "
            "QUOTED AS D6RF3's ANSWER."
            % (soln.get("worst_rel"), soln.get("rel_tol"), soln.get("point")))
        return "NOT A RESULT", reasons
    if dvl["verdict"] == "GATE FAIL":
        reasons.append("rung 4: G-DVL GATE FAIL -- the design point on disk is "
                       "not the one the registration names, so nothing "
                       "downstream of it measures what it says")
        return "NOT A RESULT", reasons
    if fd.get("pathology_NOT_A_RESULT"):
        reasons.append("rung 5: the registered FD sign-flip pathology fired")
        return "NOT A RESULT", reasons
    if price["verdict"] == "NOT A RESULT" and price.get("price", 0.0) < 0.0:
        reasons.append("rung 5: negative single-point price -- a finding about "
                       "D4, named in advance")
        return "NOT A RESULT", reasons
    nar = [g["gate"] for g in (dvl, fd, off, price, conv or {}, soln or {})
           if g.get("verdict") == "NOT A RESULT"]
    if nar:
        reasons.append("rung 6: gate(s) %s NOT A RESULT for want of an input" % nar)
        return "NOT A RESULT", reasons
    gf = [g["gate"] for g in (dvl, fd, off, price, caps, tool, place,
                             conv or {}, soln or {})
          if g.get("verdict") == "GATE FAIL"]
    if gf:
        reasons.append("rung 7: gate(s) %s GATE FAIL" % gf)
        return "GATE FAIL", reasons
    reasons.append("rung 8: every gated row PASS")
    return "PASS", reasons


# ------------------------------------------------------------------- main
def grade(root, out_path, skip_freeze=False, runscript_d6r=None,
          runscript_d4=None, d4_ref=None):
    global D4_OPT_IPOPT
    if d4_ref:
        D4_OPT_IPOPT = d4_ref
    nulls = null_reading_coverage()          # DEF-8: refuses BEFORE compute
    symbols = imported_symbol_identity()      # the controls plant into the
                                              # literal functions the gates call
    frozen = {}
    if not skip_freeze:
        # DAFOAM_CHARTER.md section 18.3: EXISTENCE IS ASSERTED FIRST AND
        # SEPARATELY, and `freeze_check` does exactly that (`absent_on_disk`
        # refuses before any md5 is taken).  The list is EVERY file this
        # grading path EXECUTES OR IMPORTS, extracted from the code rather than
        # written from memory -- `d6rf4_cd_plant_control.py` is on it because
        # this file imports it, and it is the row a list written from memory
        # would have missed, which is SO2a-DRIVER-DEF-1's exact shape.
        frozen = freeze_check(list(FROZEN_PATHS))
    coverage = frozen_path_coverage()        # section 18.3, on THIS file
    rs6 = runscript_d6r or os.path.join(HERE, "d6rf4_opt_runScript.py")
    rs4 = runscript_d4 or os.path.join(
        HERE, os.pardir, "curriculum_D4", "d4_opt_runScript.py")
    rs6, rs4 = os.path.abspath(rs6), os.path.abspath(rs4)

    products = product_writer_check()
    ledger_rows, extra = parse_ledger(os.path.join(root, "ledger.txt"))
    chain = read_chain_status(os.path.join(root, "STATUS.chain"))
    census = arm_census(root, ledger_rows, chain)

    ctrl_dir = os.path.join(os.path.dirname(os.path.abspath(out_path)),
                            "grader_controls")
    fd_path = None
    _fd_arm = ARTEFACT_PRODUCER["d6rf4_fd_endpoint.json"]
    if census[_fd_arm]["state"] == "RAN":
        fd_path = os.path.join(root, ARM_DIR[_fd_arm], "d6rf4_fd_endpoint.json")
    controls = run_planted_controls(ctrl_dir, fd_path)

    # ========== ACCEPT_FLOOR_UNMOVED -- section 7 instrument 4 ============
    # READ BACK OUT OF THE ARM'S OWN CONTAINER LOG, before any gate is graded.
    # This item is lawful because it tightens a stopping rule at an UNCHANGED
    # acceptance bar; if the bar in the bytes that ran is not the registered
    # one, every number below is earned against a bar nobody registered and
    # this grading STOPS.  It refuses in BOTH directions.  Whether a successor
    # may ever register a different acceptance rule is ESCALATED TO SANAA AND
    # UNRULED, and a GATE FAIL here is evidence for that desk, never a licence
    # to widen anything.
    arm_log = None
    if ARMS[0] in ledger_rows and ledger_rows[ARMS[0]].get("log"):
        arm_log = os.path.join(root, ledger_rows[ARMS[0]]["log"])
    try:
        floor = afc.run_floor_control(os.path.join(ctrl_dir, "accept_floor"),
                                      arm_log)
    except afc.AcceptFloorRefusal as e:
        refuse("ACCEPT_FLOOR_UNMOVED", {"instrument_refused": str(e)[:2500]})
    legs = read_legs(arm_log)
    reach = cap_reachability()

    g1 = gate_g1(root, ledger_rows, census)
    caps = gate_caps(ledger_rows, census)
    tool = gate_toolchain(root, ledger_rows, census)
    place = gate_placement(ledger_rows, census)
    dvl = gate_dvl(root, census, rs6, rs4)
    fd = gate_fd(root, census)
    off = gate_off(root, census)
    price = gate_price(root, census, controls)
    conv = gate_conv(root, census, legs)
    soln = gate_soln(root, census, legs)
    f5 = falsifier_f5(conv)
    red = report_reduction(root, census)
    cdlog = report_cdlog(root, census, g1, legs)

    verdict, reasons = compose(g1, dvl, fd, off, price, caps, tool, place,
                               census, conv, soln, f5)
    spend = sum(g1["arms"][a].get("core_min", 0.0) for a in ARMS)
    doc = {
        "item": ITEM,
        "verdict": verdict,
        "verdict_reasons": reasons,
        "frozen": frozen,
        "frozen_path_coverage": coverage,
        "null_reading_coverage": nulls,
        "imported_symbol_identity": symbols,
        "accept_floor_unmoved": floor,
        "legs": legs,
        "product_writer_check": products,
        "cap_reachability": reach,
        "census": census,
        "chain_status": chain,
        "planted_controls": controls,
        "grade": {"G1": g1, "G-DVL": dvl, "G-FD": fd, "G-OFF": off,
                  "G-PRICE": price, "G-CAPS": caps, "G9": tool, "G12": place,
                  "G-CONV": conv, "G-SOLN": soln},
        "falsifiers": {"F5": f5},
        "reported_not_gated": {"R-RED": red, "X-CDLOG": cdlog},
        # ---- DAFOAM_CHARTER.md section 6, ON THE ARTEFACT'S OWN FACE -------
        "two_row_rule": {
            "row_bought": ROW_BOUGHT,
            "row_not_bought": ROW_NOT_BOUGHT,
            "shipped_row_price_core_min": SHIPPED_ROW_PRICE_CORE_MIN,
            "shipped_row_price_basis": (
                "a second F_mp on stock IDWarp at the same cap; F_mp's own "
                "registered estimate, PREREGISTRATION.md section 4a"),
            "is_a_full_charter_section_6_verdict": False,
            "statement": (
                "THIS IS A ONE-ROW, PATCHED-ROW VERDICT AND IS LABELLED SO "
                "WHEREVER IT APPEARS. A one-row item is NOT a full "
                "DAFOAM_CHARTER.md section 6 verdict about DAFoam and must "
                "not be reported as one. The SHIPPED row is NOT BOUGHT and is "
                "PRICED anyway at %.2f core-min: an unbought row that is "
                "priced can be bought by a successor; an unbought row that is "
                "unpriced quietly becomes never."
                % SHIPPED_ROW_PRICE_CORE_MIN),
            "version_string_is_not_an_identity": (
                "all three images report DAFoam 5.0.0 / OpenFOAM v2506 / "
                "PETSc 3.15.5 while the IDWarp patch moves the reverse-mode "
                "derivative on the defect's own DOFs by seven orders of "
                "magnitude and the version string still reads 2.6.2")},
        "spend_core_min": spend,
        "cost_basis": ("c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT "
                       "MEASURED (COMPUTE_BUDGET_CHARTER.md section 5). "
                       "Dollars DERIVED, never measured."),
        "spend_usd_derived": round(spend / 60.0 * 0.0513, 6),
        "ceiling_core_min": sum(CAPS.values()),
        "ledger_extra_lines": extra,
    }
    with open(out_path, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    print("D6RF4_VERDICT %s  spend %.3f core-min of a %.1f ceiling  -> %s"
          % (verdict, spend, sum(CAPS.values()), out_path))
    # G1 reports TWO SEPARATE FACTS and they are never the same verdict:
    # a chain stop makes `all_arms_ran` false and can leave `ran_clean` true.
    print("  %-26s ran_clean=%s all_arms_ran=%s"
          % (g1["gate"], g1["ran_clean"], g1["all_arms_ran"]))
    for g in (conv, soln, dvl, fd, off, price, caps, tool, place):
        print("  %-26s %s%s" % (g["gate"], g.get("verdict", "-"),
                                ("  reason=%s" % g["reason"])
                                if g.get("reason") == NON_FINITE_REASON else ""))
    # ---- G-CONV's own registered report, pass or fail (section 3.1) -------
    for leg in LEGS:
        row = (conv.get("per_leg") or {}).get(leg)
        if not row:
            print("  %-26s %-3s %s -- %s"
                  % ("G-CONV per leg", leg, BAR_NOT_PRODUCED,
                     "no log segment; NOT A RESULT for want of an input, "
                     "producing leg NAMED"))
            continue
        print("  %-26s %-3s %-11s fvSolution=%s  worst=%s %s (%.4gx the bar "
              "%g)  banner=%s"
              % ("G-CONV per leg", leg, row["verdict"], row["fvSolution"],
                 row.get("worst_field"), row.get("worst_initRes"),
                 row.get("worst_ratio_to_bar") or float("nan"), CONV_BAR,
                 row.get("primal_failure_banner")))
        for f in CONV_FIELDS:
            c = row["per_field"].get(f, {})
            print("  %-26s     %-8s initRes=%-14s ratio_to_bar=%-10s %s"
                  % ("", f, c.get("initRes"), c.get("ratio_to_bar"),
                     c.get("verdict", "-")))
    print("  %-26s %s  named_gate=%s  predicted %.6g vs that gate's own bar "
          "%.6g -> predicted_to_fail=%s  withdraws=%s"
          % ("F5 falsifier", f5.get("verdict"), f5.get("named_gate"),
             F5_PREDICTED_P_INITRES, CONV_BAR,
             f5.get("predicted_to_fail_its_named_gate"), f5.get("withdraws")))
    # ---- section 12.4's REGISTERED REPORT on the plateau bar --------------
    print("  %-26s bar=%.1f %%  graded_components=%s  exercised=%s  %s"
          % ("plateau bar (12.4)", fd.get("plateau_bar_pct", PLATEAU_TOL_PCT),
             fd.get("n_graded_components"), fd.get("plateau_bar_exercised"),
             fd.get("plateau_bar_state")))
    for row in (fd.get("plateau_per_component") or []):
        print("  %-26s     %-18s plateau_pct=%-12.6g bar=%-6.1f "
              "clearance=%-10s decided_by=%s"
              % ("", row["component"], row["plateau_pct_measured"],
                 row["bar_pct"], row["clearance_factor"],
                 row["which_bar_actually_decided"]))
    if not (fd.get("plateau_per_component") or []):
        print("  %-26s     %s" % ("", fd.get("plateau_bar_report")))
    print("  %-26s %s   accept_floor_unmoved=%s  read tol=%s diff=%s "
          "floor=%s  (ESCALATED TO SANAA AND UNRULED; this item moves nothing)"
          % ("ACCEPT_FLOOR_UNMOVED", floor.get("state"),
             floor.get("accept_floor_unmoved"),
             (floor.get("read") or {}).get("primalMinResTol"),
             (floor.get("read") or {}).get("primalMinResTolDiff"),
             (floor.get("read") or {}).get("accept_floor")))
    print("  %-26s %s (REPORTED, NOT GATED)"
          % (red["row"], red.get("value_pct")))
    print("  %-26s per-point rel diff, NO THRESHOLD, NO VERDICT (REPORTED, "
          "NOT GATED)  row_state=%s reason=%s"
          % (cdlog["row"], cdlog.get("row_state", "PRODUCED"),
             cdlog.get("reason")))
    print("  %-26s %d run-derived quantities, %d registered null readings, "
          "coverage_complete=%s" % ("null readings (DEF-8)",
                                    nulls["n_run_derived"],
                                    nulls["n_registered"],
                                    nulls["coverage_complete"]))
    # Every rule-3 control's state is printed BESIDE the verdict, and
    # `NOT EXERCISED` is never omitted and never counted as a pass.
    print("  %-26s %s   NOT EXERCISED count = %d"
          % ("planted controls", json.dumps(controls.get("control_states", {}),
                                            sort_keys=True),
             controls.get("n_not_exercised", 0)))
    print("  %-26s row bought = %s; row NOT bought = %s, PRICED at %.2f "
          "core-min; NOT a full charter section 6 verdict"
          % ("two-row rule", ROW_BOUGHT, ROW_NOT_BOUGHT,
             SHIPPED_ROW_PRICE_CORE_MIN))
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--skip-freeze", action="store_true",
                    help="selftest fixtures only; NEVER on a real grading run")
    ap.add_argument("--runscript-d6r")
    ap.add_argument("--runscript-d4")
    ap.add_argument("--d4-ref")
    ap.add_argument("--drive-accept-floor", action="store_true",
                    help="drive ACCEPT_FLOOR_UNMOVED in both directions and "
                         "exit; no run root needed, no compute")
    ap.add_argument("--freeze-selfcheck", action="store_true",
                    help="run the pre-compute assertions only -- null-reading "
                         "coverage, imported-symbol identity and section "
                         "18.3's frozen-path extraction -- and exit")
    ap.add_argument("--cap-arithmetic", action="store_true",
                    help="print the cap/deadline reachability arithmetic and "
                         "exit; no run root needed, no compute")
    a = ap.parse_args()
    if a.drive_accept_floor:
        return afc.drive()
    if a.freeze_selfcheck:
        try:
            n = null_reading_coverage()
            s = imported_symbol_identity()
            c = frozen_path_coverage()
        except Refusal as e:
            sys.stderr.write("D6RF4_GRADE REFUSED %s\n" % e)
            return 2
        print("D6RF4 FREEZE SELF-CHECK -- no compute, no run root")
        print("  null readings (DEF-8): %d run-derived, %d registered, "
              "coverage_complete=%s"
              % (n["n_run_derived"], n["n_registered"], n["coverage_complete"]))
        for k, v in sorted(s.items()):
            print("  symbol identity: %-58s %s" % (k, v))
        print("  section 18.3 extraction: %d referenced, existence asserted "
              "first=%s, absent=%s, unfrozen=%s"
              % (c["n_referenced"], c["existence_asserted_before_any_md5"],
                 c["absent_on_disk"], c["referenced_but_not_in_FROZEN_PATHS"]))
        print("    imported local modules : %s"
              % " ".join(c["imported_local_modules"]))
        print("    executed/named scripts : %s"
              % " ".join(c["executed_or_named_scripts"]))
        print("  FROZEN_PATHS (%d): %s"
              % (len(FROZEN_PATHS),
                 " ".join(p.rsplit("/", 1)[-1] for p in FROZEN_PATHS)))
        return 0
    if a.cap_arithmetic:
        try:
            r = cap_reachability()
        except Refusal as e:
            sys.stderr.write("D6RF4_GRADE REFUSED %s\n" % e)
            return 2
        print("D6RF4 CAP / DEADLINE REACHABILITY -- ranks=%d frame_allowance_s=%d"
              % (r["ranks"], r["frame_allowance_s"]))
        for arm in ARMS:
            x = r["arms"][arm]
            print("  %-8s cap %7.2f core-min x 60 / %d ranks = %8.1f wall s"
                  % (arm, x["cap_core_min"], r["ranks"],
                     x["cap_wall_equivalent_s"]))
            print("  %-8s TMO %7d s + frame %d s          = %8.1f wall s   "
                  "residual %+.1e s" % ("", x["TMO_s"], r["frame_allowance_s"],
                                        x["TMO_plus_frame_s"],
                                        x["identity_residual_s"]))
            print("  %-8s max spend at TMO = %d x %d / 60 = %7.2f core-min  "
                  "(cap headroom %.2f)" % ("", x["TMO_s"], r["ranks"],
                                           x["max_spend_at_TMO_core_min"],
                                           x["cap_headroom_core_min"]))
            print("  %-8s predicted %7.2f core-min  <= cap %.2f : %s"
                  % ("", x["predicted_core_min"], x["cap_core_min"],
                     "OK" if not x["predicted_over_cap"] else "REFUSE"))
        print("  TOTAL predicted %.2f core-min against ceiling %.1f core-min"
              % (r["total_predicted_core_min"], r["ceiling_core_min"]))
        return 0
    if a.selftest:
        # The parent named `d6rf2_grade_selftest`, which DOES NOT EXIST on
        # disk -- `--selftest` was an ImportError in the frozen D6RF2 set.
        # This item's section 3f harness IS the selftest that matters and it
        # is a real file beside this one.
        import d6rf4_finiteness_mutation as st
        rc = st.drive()
        rc2 = afc.drive()
        rc3 = cdc.drive()
        print("D6RF4 SELFTEST  finiteness=%d accept_floor=%d cd_plant=%d"
              % (rc, rc2, rc3))
        return max(rc, rc2, rc3)
    if not a.root or not a.out:
        sys.stderr.write("usage: d6rf4_grade.py --root <run root> --out <json>\n")
        return 64
    try:
        grade(a.root, a.out, a.skip_freeze, a.runscript_d6r, a.runscript_d4,
              a.d4_ref)
    except Refusal as e:
        sys.stderr.write("D6RF4_GRADE REFUSED %s\n" % e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
