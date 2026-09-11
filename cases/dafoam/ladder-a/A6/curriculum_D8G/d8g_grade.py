#!/usr/bin/env python3
"""Curriculum D8G COMPARATOR -- A6 CRM wing-alone, a THREE-LEVEL GRID-CONVERGENCE
TRIPLE at r = 2 exactly on TWO TOOLCHAIN ROWS (PATCHED first, then SHIPPED), with an
adjoint FD table at L2 and NO GRADIENT TRIPLE (PREREGISTRATION.md section 7: the adjoint
is available at two of the three levels and two levels is not a triple).

PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.  The freeze is the
dafoam-supervisor's act (CLAUDE.md rule 2; SUPERVISION_CHARTER.md section 3) and this
file's md5 is recorded in PREREGISTRATION.md at that commit.  Computes nothing about
physics; renders verdicts from the FIXED vocabulary only (PASS / GATE REACHED /
GATE FAIL / NOT A RESULT / BLOCKED / PENDING).

DERIVED FROM cases/dafoam/ladder-a/A6/curriculum_D8R/d8r_grade.py -- a FROZEN instrument
behind a graded two-row PASS, WHICH THIS FILE DOES NOT EDIT.  The deltas are recorded in
d8g_grade_DELTAS_from_d8r.diff, exactly as D8R recorded its own from D16.  INHERITED
UNCHANGED from D8R: the ledger regex and its present-but-garbage refusal, the L-342 field
classes, the age guard and terminal-marker completion gate, the inspect-record fallback,
the CTRL and grader-level planted controls, G9 / G10 / G12, the ast.Assert census and the
selftest shape.  REMOVED because D8G runs no optimiser: G-O, G2, G3, G-BASE and the
four-arm O/F chain.  NEW here: G-MESH / G-MESH-STRICT / G-SYS / G-BODY / G-TE (section 4.1
- 4.4), G-PRIMAL (4.5), G-PLAT (AMENDMENT 1(a)), G-TRIPLE (4.6) and the rebuilt G-FD (4.7)
with its per-component plateau, its named-and-excluded flagged components, its full sweep
table and its TRIVIAL-BASELINE WITHDRAWAL.

WHAT IT GRADES (PREREGISTRATION.md section 4; the document governs):
  G1    completion, every arm SOLVER: kernel rc == 0 (docker inspect, harness rc must
        agree), OOMKilled false (hard), the AGE GUARD on the registered artefact, and the
        instrument's TERMINAL MARKER in the arm log.  Any clause fails -> REFUSE.
  G-MESH per level (4.1), read from the mesh record d8g_genmesh.sh wrote beside the level:
        cell count EXACTLY 5,568 / 44,544 / 356,352; exactly 3 patches wing(wall) /
        inout(patch) / sym(symmetry) at the registered nFaces; ZERO empty and ZERO wedge
        patches; and `Mesh has N geometric (non-empty/wedge) directions` == 3 on EVERY
        occurrence -- the GEOMETRIC line, never the `solution` line four lines away, on
        which a wedge reads 3.  A geometric N < 3 makes the ITEM NOT A RESULT.
  G-MESH-STRICT (4.2) strict checkMesh must fail EXACTLY the two registered checks and no
        others, and the small-determinant fraction must lie in [0.15, 0.28].  A third or
        different failing check, or a fraction outside the band, is GATE FAIL.  Registered
        as a CONSISTENCY gate because all four measured meshes -- the D8R graded one
        included -- fail these same two.
  G-SYS (4.3) cell-count ratios are the exact integers 8 and 8; the three surfaces are
        pairwise distinct in COORDINATES (md5 is NOT the instrument: re-coarsening is not
        byte-reproducible); patch faces scale by exactly 4 on all three patches.
  G-BODY (4.4) |d bbox| L3<->L2 <= 1.0e-4 and L2<->L1 <= 1.0e-2 in every coordinate.
  G-TE  (4.4) per level per spanwise band >= 4 points within 0.5 %c of the TE and TE
        z-spread/chord in [1.0e-3, 5.0e-3].  A level that closes the TE where a finer one
        does not is NOT A RESULT, not GATE FAIL.
  G-PRIMAL (4.5) per level, READ FROM THAT ARM'S OWN LOG:
        (a) `primalMinResTol` and `primalMinResTolDiff` are read back and asserted equal to
            the registered pair 1e-08 / 10000.  A MISMATCH IS A GRADER REFUSAL (exit 2),
            NOT A SOFT NOTE.  The accept floor is their PRODUCT, 1.0e-4 (N-D43 as
            corrected: the multiplier is not universally 1000, and A6 itself carries both
            10000 and 100).
        (b) the graded quantity is the MAXIMUM over the per-equation INITIAL residuals of
            the FINAL outer iteration -- {median(U0,U1,U2), he, p, nuTilda} (N-D44).
            `finalRes` IS NEVER READ: a finalRes comparator is structurally blind.
            MEASURED on all four D8R logs: `Primal min residual` occurs ZERO times while
            the initRes block prints at printInterval 10, so the banner route reads
            NOTHING on this case and a gate built on it would silently measure nothing.
        (c) max-initRes > 1.0e-4 -> that level NOT A RESULT, and by standing rule 5 the
            whole triple with it.  The 1.0e-6 tutorial floor is reported as a DIAGNOSTIC,
            never graded.
        AMENDMENT 1(b): this threshold equals the solver's own acceptance product, so it
        is RETAINED AS A COMPLETION PRECONDITION AND IS EXPLICITLY NOT THE DISCRIMINATING
        GATE.  The discriminating limb of standing rule 5 clause 1 is G-PLAT.
  G-PLAT (AMENDMENT 1(a)) -- THE LIMB WITH TEETH.  Per level, INDEPENDENTLY FOR CD AND CL:
        the iterative error must be at least PLAT_FACTOR (10x) SMALLER than the
        level-to-level difference in that same functional.
          statistic : PEAK-TO-PEAK, max - min, over the window.  AN ADJACENT-SAMPLE DELTA
                      IS REFUSED BY NAME and is computed only as a printed DIAGNOSTIC
                      labelled NOT_THE_GATE.  An adjacent difference is an INCREMENT, not
                      an EXCURSION: a steadily drifting signal has a small increment at
                      every step and never plateaus at all.  This is the defect the cfd
                      team's DrivAer Gate A1 plateau limb carried and this lab caught on
                      2026-09-10 -- an adjacent-iteration delta passing by 120x while the
                      signal's own excursion over 500 iterations was 8.35 %.
          source    : the SOLVER'S OWN LOG, the `CD:` / `CL:` lines calcAllFunctions emits
                      at printInterval.  MEASURED on the D8R producer's own arm
                      F-P_20260827T235119Z_1656338.log: printInterval 10 at :542, 3,232
                      `CD:` and 3,232 `CL:` lines against 3,233 `Time = ` lines.  There is
                      no per-iteration functional artefact on this case.
          window    : the last 10 % of printed samples OR the last 10 samples, WHICHEVER IS
                      LARGER.  A window holding FEWER THAN 10 samples makes that level
                      NOT A RESULT FOR WANT OF EVIDENCE -- a window that cannot exhibit an
                      excursion cannot prove a plateau.
          reference : DELTA_REF = min(|f_L1 - f_L2|, |f_L2 - f_L3|), the SMALLEST adjacent
                      level-to-level difference in the family, applied to every level.
                      REGISTERED CHOICE, stated because the rule does not name it: a
                      per-level adjacent difference would let a level pass on whichever
                      gap it happens to sit beside, and the triple's resolution is bounded
                      by its smallest gap.
        A failure on EITHER functional makes that level NOT A RESULT (section 4.6 grades
        CD AND CL; a plateau rule reading only CD leaves the second graded row ungated).
  G-TRIPLE (4.6) standing rule 5, IN ORDER, on CD and on CL separately, r = 2.000,
        Fs = 1.25: (1) any level not iteratively converged (G-PRIMAL) or not plateaued
        (G-PLAT) -> NOT A RESULT; (2) DIVERGENT / STAGNANT / OSCILLATORY / EXACT ->
        NOT A RESULT with the value, BOTH triples and BOTH observed orders printed beside
        it; (3) CONVERGING -> PASS inside the registered band p in [1.0, 3.0] else
        GATE FAIL, GCI printed.  THE GATE CAN ONLY TURN A PASS OR GATE FAIL INTO NOT A
        RESULT, NEVER THE REVERSE.  GCI IS QUOTED ONLY WHEN THE THREE VALUES ARE MONOTONE
        -- which CONVERGING implies, since a sign change in e32/e21 is OSCILLATORY.
        The classifier is the lab's own, transplanted from
        verification/runs/T-family/T1_runs/analyse_t1c.py:321 gci(), not reinvented.
  G-FD (4.7) THE BRIGHT LINE, at L2, on both rows (DAFOAM_CHARTER.md section 1: "a DAFoam
        gradient is not a result until a finite-difference table stands beside it at a
        step proved to lie in the plateau, and a DAFoam verdict is two rows"):
          * registered subset twist[0,1,3,4,5] plus the CTRL planted component.  twist[6]
            is NOT A RESULT BY NAME from D8 section 6 and is untouched.
          * PLATEAU READ PER COMPONENT: the component's FD estimate must vary by <= 10 %
            ACROSS THE THREE STEPS {3e-2, 1e-1, 3e-1} deg.  (D8R read "the middle agrees
            with at least one neighbour"; D8G's registration reads the SPREAD, which is
            strictly the stronger test, and this file implements what D8G registered.)
          * A COMPONENT THAT STABILISES NOWHERE IS FLAGGED AND EXCLUDED BY NAME from any
            aggregate quoted as agreement -- never dropped silently, never rescued by a
            step at which it happens to cross.  The names are carried in the output.
          * >= 3 graded components or the row is NOT A RESULT.
          * THE AGGREGATE IS THE VECTOR-RELATIVE ERROR ||J_an - J_fd|| / ||J_fd|| AS
            PRINTED -- not a per-component average, and never compared against the
            published per-component averages of the DAFoam/ADflow method papers.
          * BANDS: PASS at <= 5 % with ZERO flagged components; CONDITIONAL at 5-15 % and
            then only with a per-component breakdown printed; FAIL above 15 % OR ON ANY
            SIGN-FLIPPED COMPONENT REGARDLESS OF THE AGGREGATE.
            VOCABULARY, STATED BECAUSE IT MATTERS: `CONDITIONAL` and bare `FAIL` ARE NOT
            IN THE FIXED VERDICT VOCABULARY (CLAUDE.md rule 1).  The registered band label
            is carried in the field `band` as DATA; the VERDICT TOKEN is PASS for the PASS
            band and GATE FAIL for the CONDITIONAL and FAIL bands.  A <= 5 % aggregate
            WITH a flagged component is not the registered PASS band either, and lands as
            band CONDITIONAL_FLAGGED / verdict GATE FAIL.  Nothing is lost: the band, the
            aggregate, the flagged names and the per-component breakdown are all printed.
          * THE SWEEP TABLE PRINTS EVERY STEP INCLUDING THE FAILED ONES, in the registered
            shape | step | rel err | rel err (excl. flagged) | cosine | status |.
  G-FD-TRIVIAL (section 4 TRIVIAL BASELINE, DAFOAM_CHARTER.md section 4).  The same probe
        at 1e-3 deg, two orders below the registered step and below the bottom of D8's
        measured plateau, is REGISTERED AS PREDICTED TO GIVE > 15 %.  IF THE DELIBERATELY
        WRONG STEP ALSO PASSES, THE GATE IS NOT MEASURING WHAT IT CLAIMS AND THE FD VERDICT
        IT PRODUCED IS WITHDRAWN: the row's G-FD verdict becomes NOT A RESULT, the verdict
        that was withdrawn is printed in `withdrawn_verdict`, and the row is NOT A RESULT.
        This is implemented, not warned about.
  G9    toolchain per row: ledger DIGEST, the container's `D4S_IDWARP_SO_MD5:` print and
        the artefact's in-process libidwarp.so md5 must all name the row's registered
        toolchain.  INHERITED UNCHANGED (the container print string is D4S_*, inherited so
        the grader greps what the launcher writes).
  G10   caps: REPORT ONLY on this item.  PREREGISTRATION.md section 6.4 suspends the stop,
        quoting Sanaa 2026-09-10: "for all these 3D cases that still need to run, i dont
        want to see any budget gates ( time or money)".  A crossing is REPORTED with its
        ratio actual/predicted and DOES NOT COMPOSE TO GATE FAIL.  The estimate-vs-actual
        ratio is emitted per arm for the docs/COST_CALIBRATION.md row (rule 12).
  G12   placement: cpuset equals the launcher's registered set on every arm and is the
        SAME on every arm; delivered cores >= 3.0 of 4 where MEASURED, NOT_MEASURED
        disclosed otherwise.
  G6    dot-product / duality test: NOT MEASURED -- the tutorial exposes none; named.
  NO GRADIENT TRIPLE.  Section 7: the adjoint is BLOCKED at L3 on two independent grounds
        (memory, and independently conditioning -- naming only memory would be the L-15
        error).  This grader quotes NO order of accuracy for the gradient and says so.

  LEVEL = NOT A RESULT if G-PRIMAL, G-PLAT, G-TE or G-MESH's dimensionality clause fails;
        else GATE FAIL if G-MESH-STRICT, G-BODY or G-SYS fails; else PASS.
  ROW   = NOT A RESULT if any level is, or if G-TRIPLE is; else GATE FAIL if G-TRIPLE or
        G-FD is; else PASS.
  ITEM  = NOT A RESULT if either row is; else GATE FAIL if either row is; else PASS.
  A BLOCKED from any G-PLANT refusal overrides everything and NO VERDICT IS WRITTEN.
  The PATCHED row is the result-bearing row for the capability cell; A SHIPPED GATE FAIL
  STILL MAKES THE ITEM GATE FAIL, and a patched row NEVER replaces a shipped row.

PLANTED CONTROLS (standing rule 3; section 4.8), ALL THREE THROUGH THE REAL READER:
  (i)   THE FUNCTIONAL READER.  A copy of the level's artefact with CD overwritten by
        CD_PLANT = 1.234e-03 is read by the SAME read_P(); it must come back to 1e-12.
        Otherwise exit 2, NO VERDICT, the item is BLOCKED -- not GATE FAIL: nothing was
        measured.
  (ii)  THE RESIDUAL READER, WITH ITS DISCRIMINATING ANTI-PLANT.  A copy of the log
        carrying a synthetic final block with `nuTilda initRes: 9.876e-03` MUST read back
        9.876e-03.  A second copy carrying `nuTilda finalRes: 9.876e-03` with every
        initRes small MUST NOT.  A reader that returns it is reading finalRes and is
        structurally blind -> exit 2, BLOCKED.  A reader that passes the must-see plant
        but fails the anti-plant is the precise failure this control exists for.
  (iii) THE FD READER.  The CTRL component's analytic derivative is a harness-injected
        known constant recovered to 1e-9, plus this grader's own copy of each F table with
        PLANT added to every physical derivative, re-read through read_F.
L-342 (Sanaa, d4d0c29d): FIELDS_PHYSICS absent -> REFUSE; FIELDS_INFRASTRUCTURE absent ->
NOT_MEASURED, disclosed beside the verdict, never composed to PASS; present-but-garbage ->
REFUSE.  L-332: NO `assert` anywhere; the module counts ast.Assert nodes in its own source
and refuses on any.  No unconditional success print.

THE ARTEFACT CONTRACT THIS GRADER READS (the instrument d8g_of.py must write it; that
instrument is NOT part of this draft and is named as outstanding):
  <arm>/d8g_P.json  {item, mode:"P", level, cells, nprocs, identity:{libidwarp_so_md5},
                     points_md5, endTime, CD, CL}                     -- primal arms
  <arm>/d8g_A.json  {item, mode:"A", level, nprocs, identity, points_md5,
                     CD_baseline, CL_baseline,
                     adjoint:{CD:{twist:[...],patchV:[...]}, CL:{...}}} -- L2 adjoint arms
  <arm>/d8g_F.json  {item, mode:"F", level, nprocs, identity, components_requested, steps,
                     trivial_step, adjoint_source:{md5}, CD_baseline, CL_baseline,
                     eta_used, rows:[{dv,idx,status,fd:{repr(step):{step,ok,dCD,dCL}}},
                     ..., {dv:"CTRL",idx:0,status:"CONTROL",fd:{...},planted:{...}}]}
  <root>/mesh_record_<LEVEL>.json  written by d8g_genmesh.sh -- the G-MESH / G-SYS /
                     G-BODY / G-TE evidence, one per level.
"""
import ast
import glob
import hashlib
import json
import math
import os
import re
import sys
import time

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----------------
ITEM = "D8G"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple"
LEVELS = ["L1", "L2", "L3"]                       # coarse, medium, fine (section 2.2)
FD_LEVEL = "L2"                                   # section 4.7: the finest adjoint-capable level
ARMS_REQUIRED = ["L1-P", "L2-P", "L3-P", "A2-P", "F2-P",
                 "L1-S", "L2-S", "L3-S", "A2-S", "F2-S"]
ARM_KIND = {a: "SOLVER" for a in ARMS_REQUIRED}
ARM_ROW = {a: ("PATCHED" if a.endswith("-P") else "SHIPPED") for a in ARMS_REQUIRED}
ARM_RANKS = {a: 4 for a in ARMS_REQUIRED}         # section 3: every arm np = 4, scotch
ARM_LEVEL = {"L1-P": "L1", "L2-P": "L2", "L3-P": "L3", "A2-P": "L2", "F2-P": "L2",
             "L1-S": "L1", "L2-S": "L2", "L3-S": "L3", "A2-S": "L2", "F2-S": "L2"}
ARM_MODE = {a: ("P" if a[0] == "L" else a[0]) for a in ARMS_REQUIRED}   # P, A or F
ARTEFACT = {a: ("d8g_%s.json" % ARM_MODE[a]) for a in ARMS_REQUIRED}
TERMINAL = {a: ("D8G_%s_WRITTEN" % ARM_MODE[a]) for a in ARMS_REQUIRED}
DATUM_REF = {a: "0/U" for a in ARMS_REQUIRED}
PRIMAL_ARMS = [a for a in ARMS_REQUIRED if ARM_MODE[a] == "P"]

# ---- cost, section 6.3 verbatim; caps are 3x the point estimate (CASE_PROTOCOL sec 1) --
# AMENDMENT 2 (a), 2026-09-11, PRE-COMPUTE: the FD arms were mispriced.  Section 6.3 scaled
# D8R's MEASURED F arms, which ran 3 steps x 5 components x 2 + 2 baselines = 32 primals
# (measured: 32 `Running Primal Solver` calls in D8R's own F-P log).  D8G's section 4
# registers a FOURTH step -- the trivial baseline at 1e-3 deg, which the comparator's
# _trivial_baseline REFUSES to grade without -- so the arm is 4 x 5 x 2 + 2 = 42 primals,
# a factor 42/32 = 1.3125.  F2-P 67.840 -> 89.040 and F2-S 71.395 -> 93.706 (CAPS below are
# derived as 3x, so they follow: 267.120 and 281.118).  TWO INDEPENDENT ROUTES AGREE TO
# 0.55 %: per-primal scaling gives 89.040, and D8R's measured 952.319 s F-P wall less its
# measured <= 15 s launch head gives 29.291 s/primal -> 88.550 at L2's cell count.
# WHY IT IS CORRECTED HERE AND NOT EXPLAINED LATER: G10's actual/predicted ratio is computed
# from THESE constants.  Left at 67.840 the run would report ~1.31 and rule 12's attribution
# would offer contention or waste for a gap whose true cause is an arithmetic error in the
# registration.  COMPUTE_BUDGET_CHARTER section 6 keeps waste separately named and never
# absorbed; the mirror obligation is that A MISPREDICTION IS NOT LAUNDERED INTO CONTENTION.
PREDICTED_CORE_MIN = {"L1-P": 15.659, "L2-P": 17.472, "L3-P": 31.974, "A2-P": 40.652, "F2-P": 89.040,
                      "L1-S": 15.659, "L2-S": 17.472, "L3-S": 31.974, "A2-S": 40.652, "F2-S": 93.706}
CAPS = {a: round(3.0 * v, 3) for a, v in PREDICTED_CORE_MIN.items()}
ITEM_CEILING_CORE_MIN = 1079.25                   # section 6.4, registered
CAP_IS_A_STOP = False                             # section 6.4: SUSPENDED for this 3D item
NPROCS_REGISTERED = 4

# ---- section 2.2, the three registered levels, measured not proposed -----------------
CELLS = {"L1": 5568, "L2": 44544, "L3": 356352}
SURFACE_QUADS = {"L1": 696, "L2": 2784, "L3": 11136}
SURFACE_POINTS = {"L1": 996, "L2": 3358, "L3": 12258}
PATCHES_REGISTERED = {"L1": [("wing", "wall", 696), ("inout", "patch", 696), ("sym", "symmetry", 272)],
                      "L2": [("wing", "wall", 2784), ("inout", "patch", 2784), ("sym", "symmetry", 1088)],
                      "L3": [("wing", "wall", 11136), ("inout", "patch", 11136), ("sym", "symmetry", 4352)]}
GEOMETRIC_DIRECTIONS_REQUIRED = 3
CELL_RATIOS_REGISTERED = (8, 8)                   # section 4.3: the exact integers, r^3 at r = 2
STRICT_EXPECTED_CHECKS = ("face tets", "small determinant")   # section 4.2, the only two allowed
SMALL_DET_BAND = (0.15, 0.28)                     # section 4.2, registered
BBOX_TOL = {("L3", "L2"): 1.0e-4, ("L2", "L1"): 1.0e-2}       # section 4.4, G-BODY
TE_MIN_POINTS_PER_BAND = 4                        # section 4.4, G-TE
TE_ZSPREAD_BAND = (1.0e-3, 5.0e-3)                # section 4.4, G-TE

# ---- section 4.5, G-PRIMAL.  THE ACCEPT FLOOR IS THE PRODUCT (N-D43 as corrected) -----
PRIMAL_MIN_RES_TOL = 1.0e-08
PRIMAL_MIN_RES_TOL_DIFF = 10000.0
ACCEPT_FLOOR = PRIMAL_MIN_RES_TOL * PRIMAL_MIN_RES_TOL_DIFF          # 1.0e-4, registered
TUTORIAL_FLOOR_DIAGNOSTIC = 1.0e-6                # reported per level, NEVER graded
PRIMAL_EQUATIONS = ("U", "he", "p", "nuTilda")    # U = median(U0, U1, U2), N-D44

# ---- AMENDMENT 3 (2026-09-11): G1-RUN, THE COMPLETION CLAUSE THAT WAS MISSING --------
# Until this amendment G1 implemented rc == 0, OOMKilled, the age guard and the terminal
# marker, and NONE of rule 4's remaining clauses.  MEASURED, not argued: `End` appeared ZERO
# times in this file, `endTime` was read into read_P and NEVER COMPARED TO ANYTHING, and
# `ExecutionTime` appeared ONCE -- in the fixture BUILDER, in no reader and no gate.
# A DEAD SOLVE THEREFORE GRADED `PASS`: a primal truncated at iteration 490 of a registered
# 1000, with a perfectly plateaued tail and its artefact still claiming endTime = 1000, came
# out G1 PASS / G-PRIMAL PASS / G-PLAT PASS (peak-to-peak 0.0) / G-TRIPLE CONVERGING at
# order 2.0000, GCI 0.5556 %, ITEM PASS on both rows.  A comparator that certifies a corpse
# at order 2.0000 is the most dangerous possible failure, because every number in the chain
# looks like success.
# THE NEAR-MISS IS KEPT BECAUSE IT IS THE LESSON: the first attempt at that demonstration was
# caught -- by G-PLAT, not by G1, and only because the fixture's "clean" history is a
# DECAYING OSCILLATION whose truncated tail still excurses.  A CONTROL THAT HAPPENS TO FIRE
# FOR AN UNRELATED REASON READS AS A GATE THAT WORKS.  Rebuilding with a flat tail removed
# the luck and turned a coincidence into a proof.
# AND THE LABEL: `max_initRes_at_endTime` named a property read_max_init_res never
# established -- it walks backwards to the last parseable block WHEREVER IT IS.  An absent
# check is a gap; AN ABSENT CHECK WEARING THE NAME OF A PRESENT ONE is an assertion the
# instrument cannot support.  The clause below makes the name true; the name stays only
# because it now is.
ENDTIME_REGISTERED = 1000.0                       # controlDict endTime, section 4.5
DELTAT_REGISTERED = 1.0                           # controlDict deltaT
PRINT_INTERVAL_REGISTERED = 10                    # daOptions printInterval, READ BACK from the log
# The field set DARhoSimpleCFoam writes at endTime.  MEASURED first-hand on D8R's graded
# F-P arm: present, gzipped, in ALL FOUR processor dirs at time 1000.  NOT the thermal
# family's set -- carrying that one here would refuse every correct arm.
FIELDS_AT_ENDTIME = ("T", "U", "p", "nuTilda", "nut", "alphat", "phi")

# ---- AMENDMENT 1(a), G-PLAT ----------------------------------------------------------
PLAT_FUNCTIONALS = ("CD", "CL")                   # section 4.6 grades BOTH
PLAT_WINDOW_FRAC = 0.10                           # "the last 10 % of printed samples"
PLAT_MIN_SAMPLES = 10                             # "OR the last 10 samples, whichever is larger"
PLAT_FACTOR = 10.0                                # "at least ten times smaller"

# ---- section 4.6, G-TRIPLE -----------------------------------------------------------
R_REFINE = 2.0                                    # exact, from the integer cell ratios 8 and 8
FS = 1.25                                         # standing rule 5
P_BAND = (1.0, 3.0)                               # registered, centred on 2

# ---- section 4.7, G-FD ---------------------------------------------------------------
COMPONENTS_REGISTERED = [["twist", 0], ["twist", 1], ["twist", 3], ["twist", 4], ["twist", 5]]
STEPS_REGISTERED = {"twist": [3.0e-2, 1.0e-1, 3.0e-1]}       # degrees; the MIDDLE is the reference
TRIVIAL_STEP = 1.0e-3                             # the section 4 trivial baseline, PREDICTED > 15 %
DVS = ("twist", "patchV")
PLATEAU_TOL_PCT = 10.0                            # per component, ACROSS THE THREE STEPS
FD_PASS_PCT = 5.0                                 # band PASS
FD_CONDITIONAL_PCT = 15.0                         # band CONDITIONAL upper edge == band FAIL floor
MIN_GRADED = 3
NEAR_ZERO_ABS = 1.0e-14
CTRL_STEP = 1.0e-1
PLANT = 1.234e-03
CD_PLANT = 1.234e-03                              # section 4.8 control (i), same constant
RES_PLANT = 9.876e-03                             # section 4.8 control (ii), must-see / must-NOT-see

# ---- section 3, toolchain identity BY DIGEST (read from this box 2026-09-10) ----------
IMG_DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
              "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663", "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}

# CPUSET: PREREGISTRATION.md section 3 registers "cpuset assigned by the launcher" and NO
# SPECIFIC SET.  This constant is INHERITED FROM THE D8R PRODUCER (d8r_run_arm.sh:141) and
# the launcher d8g_run_arm.sh carries the same value.  THE SUPERVISOR MUST REGISTER IT AT
# THE FREEZE OR THIS GATE IS READING AN UNREGISTERED NUMBER -- flagged, not hidden.
CPUSET_REGISTERED = "0,1,12,15"
DELIVERED_CORES_FLOOR = 3.0

PRED = {"P3_CD_triple_converging_in_band": "moderate confidence only (section 8)",
        "P4_shipped_FD_FAIL_patched_PASS": "a SPLIT is predicted at the baseline",
        "P5_rows_agree_to_1_eta_on_CD_and_CL": "the rotation patch cannot enter a fixed-design primal",
        "P6_core_min": 0.8447 * 359.748}
FIELDS_PHYSICS = ("rc", "inspect_exit", "oomkilled", "terminal_statement", "age_guard",
                  "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("memavail_pre_GiB", "memavail_post_GiB", "delivered", "siblings_pre",
                         "siblings_post", "log", "wall_s")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 50


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def md5_of(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


# ================= LEDGER (physics vs infrastructure, L-342) -- D5's regex, INHERITED ==
LEDGER_RE = re.compile(
    r"ARM=(?P<ARM>\S+)\s+ROW=(?P<ROW>\S+)\s+IMG=(?P<IMG>\S+)\s+"
    r"DIGEST=(?P<DIGEST>\S+)\s+rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall_s>\d+)\s+"
    r"ranks=(?P<ranks>\d+)\s+core_min=(?P<core_min>[\d.]+)\s+"
    r"cap_core_min=(?P<cap>[\d.]+)\s+enforced_wall_s=(?P<ewall>\d+)\s+"
    r"enforced_core_min=(?P<ecore>[\d.]+)\s+memory=(?P<mem>\S+)\s+"
    r"inspect\(exit,oomkilled\)=\[(?P<inspect>[^\]]*)\]"
    r"(?:\s+memavail_pre_GiB=(?P<mempre>[\d.]+|NOT_MEASURED))?"
    r"(?:\s+memavail_post_GiB=(?P<mempost>[\d.]+|NOT_MEASURED))?"
    r"\s+cpuset=(?P<cpuset>\S+)"
    r"(?:\s+delivered_cores_mean=\[(?P<delivered>[^\]]*)\])?"
    r"(?:\s+siblings_pre=\[(?P<sibpre>[^\]]*)\])?"
    r"(?:\s+siblings_post=\[(?P<sibpost>[^\]]*)\])?"
    r"(?:\s+log=(?P<log>\S+))?")


def _infra_float(v):
    if v is None or v == NOT_MEASURED:
        return None
    return float(v)


def read_ledger(path):
    if not os.path.isfile(path):
        refuse("ledger", {"absent": path})
    rows = {}
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        m = LEDGER_RE.search(line)
        if not m:
            refuse("ledger", {"row_unparseable": line.strip()[:300],
                              "note": "PRESENT-BUT-GARBAGE row: refused, never skipped"})
        g = m.groupdict()
        parts = g["inspect"].split()
        infra_nm = [k for k, v in (("memavail_pre_GiB", g["mempre"]), ("memavail_post_GiB", g["mempost"]),
                                   ("delivered", g["delivered"]), ("siblings_pre", g["sibpre"]),
                                   ("siblings_post", g["sibpost"]), ("log", g["log"]))
                    if v is None or NOT_MEASURED in str(v)]
        row = {"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"], "DIGEST": g["DIGEST"],
               "rc": int(g["rc"]), "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
               "core_min": float(g["core_min"]), "cap_core_min": float(g["cap"]),
               "enforced_core_min": float(g["ecore"]), "memory": g["mem"],
               "inspect_exit": (parts[0] if parts else None),
               "oomkilled": (parts[1] if len(parts) > 1 else None),
               "memavail_pre_GiB": _infra_float(g["mempre"]), "memavail_post_GiB": _infra_float(g["mempost"]),
               "cpuset": g["cpuset"], "delivered": g["delivered"], "siblings_pre": g["sibpre"],
               "siblings_post": g["sibpost"], "log": g["log"], "source": "ledger_row",
               "field_sources": {"all": "ledger_row"}, "infra_not_measured": infra_nm}
        if row["ARM"] in rows:
            refuse("ledger", {"duplicate_arm_row": row["ARM"], "note": "two records for one run is the defect"})
        rows[row["ARM"]] = row
    return rows


def inspect_file_fallback(base, arm):
    """L-342: an arm with no ledger row is read from the launcher's surviving inspect
    record `<ARM>_<stamp>.inspect.txt` (exit oom started finished cpuset memory); every
    infrastructure field NOT_MEASURED, the source named per field.  INHERITED FROM D8R."""
    cands = sorted(glob.glob(os.path.join(base, "%s_*.inspect.txt" % arm)))
    if len(cands) != 1:
        refuse("G1", {"arm_absent_from_ledger": arm, "inspect_record_candidates": cands,
                      "note": "exactly one surviving inspect record may stand in for a missing row"})
    parts = open(cands[0]).read().split()
    if len(parts) < 5:
        refuse("G1", {"inspect_record_unparseable": cands[0], "content": parts})
    logs = sorted(glob.glob(os.path.join(base, "%s_*.log" % arm)))
    try:
        rc = int(parts[0])
    except ValueError:
        refuse("G1", {"inspect_record_exit_unparseable": parts[0]})
    return {"ARM": arm, "ROW": ARM_ROW[arm], "IMG": None, "DIGEST": (parts[6] if len(parts) > 6 else None), "rc": rc, "wall_s": None,
            "ranks": ARM_RANKS[arm], "core_min": None, "cap_core_min": CAPS[arm],
            "enforced_core_min": CAPS[arm], "memory": parts[5] if len(parts) > 5 else None,
            "inspect_exit": parts[0], "oomkilled": parts[1].lower(), "memavail_pre_GiB": None,
            "memavail_post_GiB": None, "cpuset": parts[4], "delivered": NOT_MEASURED,
            "siblings_pre": NOT_MEASURED, "siblings_post": NOT_MEASURED,
            "log": (os.path.basename(logs[-1]) if logs else None), "source": "inspect_record",
            "field_sources": {"rc": "inspect.txt .State.ExitCode", "oomkilled": "inspect.txt .State.OOMKilled",
                              "cpuset": "inspect.txt HostConfig.CpusetCpus", "DIGEST": "inspect.txt 7th field (launcher's GOT_DIGEST)"},
            "infra_not_measured": list(FIELDS_INFRASTRUCTURE) + ["core_min"]}


# ================= G1: COMPLETION (INHERITED FROM D8R) ================================
def arm_datum(base, arm):
    d = os.path.join(base, arm)
    p = os.path.join(d, ".d8g_age_datum")
    if not os.path.isfile(p):
        refuse("G1", {"age_datum_absent": p, "arm": arm})
    datum = int(open(p).read().strip())
    ref = os.path.join(d, DATUM_REF[arm])
    if not os.path.isfile(ref):
        refuse("G1", {"age_reference_absent": ref})
    if int(os.path.getmtime(ref)) != datum:
        refuse("G1", {"age_reference_moved": ref, "recorded": datum, "on_disk": int(os.path.getmtime(ref))})
    return d, datum


def g_completion(base, rows):
    out = {"arms": {}, "not_measured": {}}
    for arm in ARMS_REQUIRED:
        r = rows.get(arm)
        if r is None:
            r = inspect_file_fallback(base, arm)
            rows[arm] = r
        ke = r.get("inspect_exit")
        if ke is None:
            refuse("G1", {"kernel_exit_absent": arm, "note": "inspect(exit,oomkilled) is a PHYSICS field"})
        try:
            kernel_rc = int(ke)
        except (TypeError, ValueError):
            refuse("G1", {"kernel_exit_unparseable": arm, "value": ke})
        if kernel_rc != r["rc"]:
            refuse("G1", {"rc_disagreement": arm, "kernel": kernel_rc, "harness": r["rc"]})
        oom = str(r.get("oomkilled")).lower()
        if oom not in ("false", "true"):
            refuse("G1", {"oomkilled_unparseable": arm, "value": r.get("oomkilled")})
        if kernel_rc != 0 or oom != "false":
            refuse("G1", {"arm": arm, "kernel_rc": kernel_rc, "oomkilled": oom,
                          "note": "a run that fails any clause is not done (rule 4); OOMKilled is hard"})
        adir, datum = arm_datum(base, arm)
        art = os.path.join(adir, ARTEFACT[arm])
        if not os.path.isfile(art):
            refuse("G1", {"artefact_absent": art, "arm": arm})
        if os.path.getmtime(art) <= datum:
            refuse("G1", {"artefact_not_newer_than_datum": art, "arm": arm, "datum": datum,
                          "artefact_mtime": os.path.getmtime(art), "note": "age guard, rule 4"})
        logname = r.get("log")
        logpath = os.path.join(base, logname) if logname else None
        if not logpath or not os.path.isfile(logpath):
            refuse("G1", {"log_absent": logname, "arm": arm, "note": "a missing log is a FAILED clause"})
        text = open(logpath, errors="replace").read()
        if TERMINAL[arm] not in text:
            refuse("G1", {"terminal_marker_absent": TERMINAL[arm], "arm": arm, "log": logname})
        r["log_text"] = text
        r["log_path"] = logpath
        # AMENDMENT 3: rule 4's remaining clauses.  Placed HERE, inside G1, so a failure is a
        # REFUSAL and no verdict is written -- not a gate that composes to GATE FAIL.
        out.setdefault("run_completion", {})[arm] = g1_run_completion(base, arm, text)
        out["arms"][arm] = {"kind": ARM_KIND[arm], "level": ARM_LEVEL[arm], "mode": ARM_MODE[arm],
                            "kernel_rc": kernel_rc, "oomkilled": oom, "artefact": ARTEFACT[arm],
                            "source": r["source"], "field_sources": r["field_sources"]}
        if r.get("infra_not_measured"):
            out["not_measured"][arm] = r["infra_not_measured"]
    return out


# ================= THE LOG READERS -- G-PRIMAL and G-PLAT read the SOLVER'S OWN LOG ====
# NEW in D8G.  D8R read everything from the instrument's JSON; D8G's two discriminating
# gates read the solver's stdout directly, so a defect in d8g_of.py cannot manufacture a
# converged level.  BOTH readers carry a planted control below (section 4.8).

_RE_TOL = re.compile(r"^\s*primalMinResTol\s+([0-9.eE+-]+)\s*;", re.M)
_RE_TOLDIFF = re.compile(r"^\s*primalMinResTolDiff\s+([0-9.eE+-]+)\s*;", re.M)
# THE RESIDUAL READER READS `initRes` AND NOTHING ELSE.  The regex stops before
# `finalRes` deliberately: on one lab case every per-equation finalRes read <= 1e-6 on the
# exact iteration DAFoam declared the primal failed (N-D44).  The anti-plant in
# residual_plant_control() is what PROVES this reader cannot see finalRes.
_RE_INITRES = re.compile(r"^(U0|U1|U2|he|p|nuTilda)\s+initRes:\s+([0-9.eE+-]+)", re.M)
_RE_TIMEHDR = re.compile(r"^Time = ", re.M)
_RE_PRIMAL_CALL = re.compile(r"^Running Primal Solver", re.M)


def last_primal_segment(text):
    """The graded primal is the LAST one the arm ran.  A primal arm runs exactly one; an
    F arm runs one per FD evaluation, and its last is its last.  If the marker never
    appears the solver never called solvePrimal() and there is nothing to read."""
    hits = list(_RE_PRIMAL_CALL.finditer(text))
    if not hits:
        refuse("G-PRIMAL", {"no_primal_solver_call": True,
                            "note": "`Running Primal Solver` never printed: solvePrimal() was never called"})
    return text[hits[-1].start():]


def read_primal_tolerances(text, arm):
    """AMENDMENT-registered: BOTH values are read back FROM THIS ARM'S OWN LOG and
    asserted equal to the registered pair.  A MISMATCH IS A REFUSAL (exit 2), NOT A SOFT
    NOTE -- A6 itself carries two different primalMinResTolDiff values (10000 in the D8R
    producer, 100 in the archived tutorial) and neither may be carried from the other."""
    mt, md = _RE_TOL.search(text), _RE_TOLDIFF.search(text)
    if mt is None or md is None:
        refuse("G-PRIMAL", {"arm": arm, "primalMinResTol_found": mt is not None,
                            "primalMinResTolDiff_found": md is not None,
                            "note": "the acceptance pair is a PHYSICS field; absent -> REFUSE"})
    tol, diff = float(mt.group(1)), float(md.group(1))
    if abs(tol - PRIMAL_MIN_RES_TOL) > 1e-18 or abs(diff - PRIMAL_MIN_RES_TOL_DIFF) > 1e-9:
        refuse("G-PRIMAL", {"arm": arm, "log_primalMinResTol": tol, "log_primalMinResTolDiff": diff,
                            "registered": [PRIMAL_MIN_RES_TOL, PRIMAL_MIN_RES_TOL_DIFF],
                            "note": "a family whose acceptance rule changes between levels is not a "
                                    "family; a mismatch is a grader REFUSAL, not a soft note"})
    return tol, diff


def read_max_init_res(segment):
    """The MAXIMUM over the per-equation INITIAL residuals of the FINAL outer iteration.
    The equation set is {U (median of U0,U1,U2), he, p, nuTilda} (N-D44).  `finalRes` IS
    NEVER READ.  Returns (max_init_res, per_equation_dict) or None if no block parsed."""
    blocks = _RE_TIMEHDR.split(segment)
    for chunk in reversed(blocks):
        vals = {}
        for m in _RE_INITRES.finditer(chunk):
            vals[m.group(1)] = float(m.group(2))
        if all(k in vals for k in ("U0", "U1", "U2", "he", "p", "nuTilda")):
            u = sorted([vals["U0"], vals["U1"], vals["U2"]])[1]      # the MEDIAN, N-D44
            per = {"U_median": u, "he": vals["he"], "p": vals["p"], "nuTilda": vals["nuTilda"]}
            return max(per.values()), per
    return None


_RE_PRINTINTERVAL = re.compile(r"^\s*printInterval\s+(\d+)\s*;", re.M)
_RE_END = re.compile(r"^End$", re.M)
_RE_EXECTIME = re.compile(r"^ExecutionTime = ", re.M)
_RE_TIMEVAL = re.compile(r"^Time = (\S+)", re.M)


def read_print_interval(text, arm):
    """READ BACK FROM THIS ARM'S OWN LOG, exactly as the acceptance pair is, and for the same
    reason: the printed-step count the completion clause checks is DERIVED from it, so a
    cadence this grader assumed rather than read would make the derivation describe a
    different run."""
    m = _RE_PRINTINTERVAL.search(text)
    if m is None:
        refuse("G1-RUN", {"arm": arm, "printInterval_absent_from_log": True,
                          "note": "the output cadence is a PHYSICS field here: the completion "
                                  "clause's expected step count is derived from it"})
    pi = int(m.group(1))
    if pi != PRINT_INTERVAL_REGISTERED:
        refuse("G1-RUN", {"arm": arm, "log_printInterval": pi, "registered": PRINT_INTERVAL_REGISTERED,
                          "note": "a family whose output cadence changes between arms is not a family"})
    return pi


def expected_printed_steps(end_time, delta_t, print_interval):
    """THE COUNT IS DERIVED, NEVER HARD-CODED.  DAFoam prints the step block when
    `iter % printInterval == 0` OR `iter == 1`, so the count is the SIZE OF THE SET
    {1} u {pi, 2pi, ... <= N}, N = endTime/deltaT.  Computed as a set so the printInterval == 1
    double-count cannot creep in.  A literal 101 here would silently become wrong the moment
    endTime, deltaT or printInterval moved -- the same class of defect as a memory ceiling
    that describes the wrong machine.  d8g_of.py's printed_sample_count() computes this same
    set, so the gate and the producer agree BY CONSTRUCTION and not by two copies of a number.
    MEASURED on D8R's graded F-P arm: endTime 1000 / deltaT 1 / printInterval 10 -> the last
    primal segment carries exactly 101 `ExecutionTime` lines, 101 `Time =` lines, last
    Time = 1000, and exactly one `End`."""
    if delta_t <= 0 or print_interval <= 0 or end_time <= 0:
        return 0
    n_iter = int(round(float(end_time) / float(delta_t)))
    pi = int(round(float(print_interval)))
    printed = {1} if n_iter >= 1 else set()
    printed.update(range(pi, n_iter + 1, pi))
    return len(printed)


def g1_run_completion(base, arm, logtext):
    """AMENDMENT 3.  CLAUDE.md rule 4's remaining clauses, on the LAST primal segment -- the
    same segment G-PRIMAL and G-PLAT grade, so the run this clause certifies is the run they
    read.  ANY clause failing is a REFUSAL: a run that fails any clause is not done."""
    pi = read_print_interval(logtext, arm)
    seg = last_primal_segment(logtext)
    want = expected_printed_steps(ENDTIME_REGISTERED, DELTAT_REGISTERED, pi)
    times = _RE_TIMEVAL.findall(seg)
    n_exec = len(_RE_EXECTIME.findall(seg))
    n_end = len(_RE_END.findall(seg))
    out = {"arm": arm, "printInterval_read_back": pi, "endTime_registered": ENDTIME_REGISTERED,
           "deltaT_registered": DELTAT_REGISTERED, "expected_printed_steps_DERIVED": want,
           "n_ExecutionTime": n_exec, "n_Time": len(times),
           "last_time": (times[-1] if times else None), "n_End": n_end,
           "derivation": "|{1} u {pi, 2pi, ... <= endTime/deltaT}| -- DERIVED, never hard-coded"}
    if not times:
        refuse("G1-RUN", {"arm": arm, "no_Time_lines_in_the_last_primal_segment": True})
    try:
        last_t = float(times[-1])
    except ValueError:
        refuse("G1-RUN", {"arm": arm, "last_time_unparseable": times[-1]})
    if abs(last_t - ENDTIME_REGISTERED) > 1e-9:
        refuse("G1-RUN", {"arm": arm, "last_time": last_t, "endTime_registered": ENDTIME_REGISTERED,
                          "note": "rule 4: last time == endTime.  A primal that stopped short is not "
                                  "done, however plateaued its tail looks"})
    if n_end != 1:
        refuse("G1-RUN", {"arm": arm, "n_End_in_last_primal_segment": n_end,
                          "note": "rule 4: an `End` line.  MEASURED on D8R's graded arm: exactly one "
                                  "per primal segment (33 in a 32-primal log, the extra being "
                                  "decomposePar's)"})
    if n_exec != want:
        refuse("G1-RUN", {"arm": arm, "n_ExecutionTime": n_exec, "expected_DERIVED": want,
                          "printInterval": pi, "endTime": ENDTIME_REGISTERED, "deltaT": DELTAT_REGISTERED,
                          "note": "rule 4 clause 5: the count must match the steps WRITTEN, not the "
                                  "steps TAKEN -- this family writes at printInterval, so the unit-step "
                                  "form round(endTime/deltaT) would refuse every correct arm"})
    adir = os.path.join(base, arm)
    datum_p = os.path.join(adir, ".d8g_age_datum")
    datum = int(open(datum_p).read().strip()) if os.path.isfile(datum_p) else None
    missing, stale = [], []
    procs = sorted(glob.glob(os.path.join(adir, "processor*")))
    if len(procs) != NPROCS_REGISTERED:
        refuse("G1-RUN", {"arm": arm, "processor_dirs": len(procs), "registered": NPROCS_REGISTERED,
                          "note": "rule 4: the field set at endTime, written by every rank"})
    tdir = ("%d" % int(ENDTIME_REGISTERED)) if float(ENDTIME_REGISTERED).is_integer() else repr(ENDTIME_REGISTERED)
    for pd in procs:
        for fld in FIELDS_AT_ENDTIME:
            hits = [q for q in (os.path.join(pd, tdir, fld), os.path.join(pd, tdir, fld + ".gz"))
                    if os.path.isfile(q)]
            if not hits:
                missing.append(os.path.join(os.path.basename(pd), tdir, fld))
                continue
            if datum is not None and os.path.getmtime(hits[0]) <= datum:
                stale.append(os.path.join(os.path.basename(pd), tdir, fld))
    if missing:
        refuse("G1-RUN", {"arm": arm, "fields_absent_at_endTime": missing[:12],
                          "n_missing": len(missing), "field_set": list(FIELDS_AT_ENDTIME),
                          "note": "rule 4: the field set present at endTime -> PHYSICS absent, REFUSE"})
    if stale:
        refuse("G1-RUN", {"arm": arm, "fields_not_newer_than_the_age_datum": stale[:12],
                          "n_stale": len(stale), "datum": datum,
                          "note": "rule 4's AGE GUARD on the fields themselves: 0/U is touched last at "
                                  "stage time, so a field not newer than it did not come from this run"})
    out["fields_at_endTime_present_and_newer_than_datum"] = True
    return out


def read_functional_history(segment, of):
    """The `CD:` / `CL:` lines calcAllFunctions emits at printInterval.  MEASURED on the
    D8R producer's own arm: 3,232 of each against 3,233 `Time = ` lines.  There is no
    per-iteration functional artefact on this case, so this is the source AMENDMENT 1(a)
    registers."""
    rex = re.compile(r"^%s:\s+([0-9.eE+-]+)" % of, re.M)
    return [float(m.group(1)) for m in rex.finditer(segment)]


def plateau_window(hist):
    """The window is the last 10 % of printed samples OR the last 10 samples, WHICHEVER IS
    LARGER.  Fewer than PLAT_MIN_SAMPLES in the window -> the caller makes that level
    NOT A RESULT for want of evidence."""
    n = len(hist)
    k = max(int(math.ceil(PLAT_WINDOW_FRAC * n)), PLAT_MIN_SAMPLES)
    k = min(k, n)
    return hist[n - k:]


def plateau_statistic(window):
    """PEAK-TO-PEAK, max - min.  THE ADJACENT-SAMPLE DELTA IS REFUSED BY NAME and is
    returned only as a DIAGNOSTIC labelled NOT_THE_GATE: an adjacent difference is an
    INCREMENT, not an EXCURSION, and a steadily drifting signal has a small increment at
    every step while never plateauing at all.  cfd's DrivAer Gate A1 limb, caught
    2026-09-10: an adjacent-iteration delta passed by 120x while the signal's own
    excursion over 500 iterations was 8.35 %."""
    ptp = max(window) - min(window)
    adj = max(abs(window[i + 1] - window[i]) for i in range(len(window) - 1)) if len(window) > 1 else 0.0
    return {"peak_to_peak": ptp, "n_window": len(window),
            "REFUSED_BY_NAME_adjacent_sample_delta_max": adj,
            "adjacent_delta_label": "DIAGNOSTIC ONLY -- NOT_THE_GATE (AMENDMENT 1(a) item 1)"}


# ================= ARTEFACT READERS ===================================================
def read_P(path):
    """The primal arm's functional artefact.  THE PLANTED CONTROL (section 4.8 (i)) DRIVES
    THIS SAME FUNCTION on a copy with CD overwritten by CD_PLANT."""
    j = json.load(open(path))
    return {"level": j.get("level"), "cells": j.get("cells"),
            "CD": float(j["CD"]), "CL": float(j["CL"]),
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"),
            "points_md5": j.get("points_md5"), "nprocs": j.get("nprocs"),
            "endTime": j.get("endTime"), "md5": md5_of(path)}


def read_A(path):
    j = json.load(open(path))
    adj = {}
    for of in ("CD", "CL"):
        adj[of] = {dv: [float(v) for v in j["adjoint"][of][dv]] for dv in DVS}
    return {"level": j.get("level"), "adjoint": adj, "CD": float(j["CD_baseline"]), "CL": float(j["CL_baseline"]),
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"),
            "points_md5": j.get("points_md5"), "nprocs": j.get("nprocs"), "md5": md5_of(path)}


def read_F(path):
    j = json.load(open(path))
    if j.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G-FD", {"components_requested_not_registered": j.get("components_requested"),
                        "registered": COMPONENTS_REGISTERED})
    if j.get("trivial_step") is not None and abs(float(j["trivial_step"]) - TRIVIAL_STEP) > 1e-15:
        refuse("G-FD", {"trivial_step_not_registered": j.get("trivial_step"), "registered": TRIVIAL_STEP})
    table, ctrl = {}, None
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            ctrl = row
            continue
        key = (row["dv"], int(row["idx"]))
        fd = {}
        for k, v in (row.get("fd") or {}).items():
            fd[float(v["step"])] = {"ok": bool(v.get("ok")),
                                    "dCD": (float(v["dCD"]) if v.get("ok") else None),
                                    "dCL": (float(v["dCL"]) if v.get("ok") else None)}
        table[key] = {"status": row.get("status"), "fd": fd}
    return {"level": j.get("level"), "table": table, "ctrl": ctrl,
            "CD": float(j["CD_baseline"]), "CL": float(j["CL_baseline"]), "eta": float(j["eta_used"]),
            "adjoint_md5": (j.get("adjoint_source") or {}).get("md5"),
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "nprocs": j.get("nprocs"), "raw": j}


def read_mesh_record(root, level):
    """The G-MESH / G-SYS / G-BODY / G-TE evidence, written per level by d8g_genmesh.sh.
    THE MESH IS THE CASE: an absent record is a PHYSICS field absent -> REFUSE (L-342)."""
    p = os.path.join(root, "mesh_record_%s.json" % level)
    if not os.path.isfile(p):
        refuse("G-MESH", {"mesh_record_absent": p, "level": level,
                          "note": "the mesh record is the level's construction evidence; absent -> REFUSE"})
    j = json.load(open(p))
    need = ("cells", "surface_points", "surface_quad_faces", "patches", "geometric_directions",
            "checkmesh_plain", "strict_failed_checks", "small_det_fraction", "bbox", "te_bands",
            "points_md5", "surface_max_coord_delta_to_finer")
    missing = [k for k in need if k not in j]
    if missing:
        refuse("G-MESH", {"mesh_record_incomplete": p, "missing": missing})
    return j


# ================= PLANTED CONTROLS (standing rule 3, section 4.8) ====================
def functional_plant_control(base, ppath, tag):
    """CONTROL (i).  Overwrite CD with CD_PLANT in a copy and re-read it through the SAME
    read_P().  A reader that returns the unplanted value, a zero, or nothing has not been
    shown able to see a non-zero: exit 2, NO VERDICT, the item is BLOCKED."""
    j = json.load(open(ppath))
    j["CD"] = repr(CD_PLANT)
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "P_%s_planted.json" % tag)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    back = read_P(cp)["CD"]
    orig = read_P(ppath)["CD"]
    if abs(back - CD_PLANT) > 1e-12:
        refuse("CONTROL", {"functional_reader_plant_not_seen": {"read_back": back, "plant": CD_PLANT,
                                                                "unplanted": orig, "file": cp},
                           "note": "BLOCKED, not GATE FAIL: nothing was measured"})
    return {"functional_plant_seen": True, "read_back": back, "unplanted": orig, "file": cp}


def residual_plant_control(base, logtext, tag):
    """CONTROL (ii), WITH ITS DISCRIMINATING ANTI-PLANT.  This is the reader N-D44 says is
    easy to get structurally wrong, so the control is built to catch exactly that error:
      must-see     : a synthetic final block with `nuTilda initRes: 9.876e-03` -> the
                     reader MUST return 9.876e-03.
      must-NOT-see : the same block with `nuTilda finalRes: 9.876e-03` and every initRes
                     small -> the reader MUST NOT return it.  A reader that does is
                     reading finalRes and is structurally blind.
    A reader that passes the must-see plant but fails the anti-plant is the precise
    failure this control exists for: a reader shown able to see a non-zero ON THE WRONG
    FIELD has not been shown able to see the right one."""
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    small = "1.0e-09"
    see = ("\nTime = 999999\n\n"
           "U0 initRes: %s finalRes: %s nIters: 2\n"
           "U1 initRes: %s finalRes: %s nIters: 2\n"
           "U2 initRes: %s finalRes: %s nIters: 2\n"
           "he initRes: %s finalRes: %s nIters: 2\n"
           "p initRes: %s finalRes: %s nIters: 9\n"
           "nuTilda initRes: %s finalRes: %s nIters: 2\n"
           % (small, small, small, small, small, small, small, small, small, small,
              repr(RES_PLANT), small))
    anti = ("\nTime = 999999\n\n"
            "U0 initRes: %s finalRes: %s nIters: 2\n"
            "U1 initRes: %s finalRes: %s nIters: 2\n"
            "U2 initRes: %s finalRes: %s nIters: 2\n"
            "he initRes: %s finalRes: %s nIters: 2\n"
            "p initRes: %s finalRes: %s nIters: 9\n"
            "nuTilda initRes: %s finalRes: %s nIters: 2\n"
            % (small, small, small, small, small, small, small, small, small, small,
               small, repr(RES_PLANT)))
    sp = os.path.join(cdir, "RES_%s_must_see.log" % tag)
    ap = os.path.join(cdir, "RES_%s_anti_plant.log" % tag)
    open(sp, "w").write(logtext + see)
    open(ap, "w").write(logtext + anti)
    seen = read_max_init_res(last_primal_segment(open(sp).read()))
    blind = read_max_init_res(last_primal_segment(open(ap).read()))
    if seen is None or abs(seen[0] - RES_PLANT) > 1e-12:
        refuse("CONTROL", {"residual_reader_must_see_plant_not_seen": {"read_back": (seen[0] if seen else None),
                                                                       "plant": RES_PLANT, "file": sp},
                           "note": "BLOCKED: a reader not shown able to see a non-zero is not evidence"})
    if blind is not None and abs(blind[0] - RES_PLANT) <= 1e-12:
        refuse("CONTROL", {"residual_reader_SAW_THE_FINALRES_ANTI_PLANT": {"read_back": blind[0],
                                                                           "plant": RES_PLANT, "file": ap},
                           "note": "the reader is reading finalRes and is STRUCTURALLY BLIND -> BLOCKED"})
    return {"residual_must_see": seen[0], "residual_anti_plant_read": (blind[0] if blind else None),
            "anti_plant_correctly_not_seen": True, "files": [sp, ap]}


def ctrl_control(F):
    """CONTROL (iii), INHERITED FROM D8R: the instrument's own CTRL component and its
    PLANTED row, re-read here; the grade REFUSES if the reader cannot see them."""
    c = F["ctrl"]
    if c is None:
        refuse("CONTROL", {"ctrl_row_absent": True})
    zero = float(c["fd"][repr(CTRL_STEP)]["dCD"])
    plant = float(c["planted"]["dCD"])
    want = PLANT / (2.0 * CTRL_STEP)
    if zero != 0.0 or abs(plant - want) > 1e-12 * abs(want):
        refuse("CONTROL", {"instrument_ctrl_not_seen": {"zero": zero, "planted": plant, "want": want}})
    return {"instrument_ctrl_zero": zero, "instrument_ctrl_planted": plant, "want": want}


def grader_plant_control(base, fpath, tag):
    """Write a copy with PLANT added to every physical dCD, re-read it through read_F,
    refuse unless every value moved by exactly PLANT.  INHERITED FROM D8R."""
    j = json.load(open(fpath))
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            continue
        for v in (row.get("fd") or {}).values():
            if v.get("ok"):
                v["dCD"] = repr(float(v["dCD"]) + PLANT)
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "F_%s_planted.json" % tag)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    orig, back = read_F(fpath)["table"], read_F(cp)["table"]
    worst = 0.0
    n = 0
    for key, row in orig.items():
        for s, v in row["fd"].items():
            if v["ok"]:
                worst = max(worst, abs((back[key]["fd"][s]["dCD"] - v["dCD"]) - PLANT))
                n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"grader_plant_not_seen": {"n_values": n, "worst_residual": worst, "plant": PLANT}})
    return {"grader_plant_seen": True, "n_values": n, "worst_residual": worst, "file": cp}


# ================= G-MESH / G-MESH-STRICT / G-SYS / G-BODY / G-TE (sections 4.1-4.4) ==
def g_mesh(recs):
    """Per level, from the mesh record.  NOTE THE TWO DIFFERENT checkMesh LINES: the
    authoritative one is `Mesh has N geometric (non-empty/wedge) directions`.  `Mesh has 3
    solution (non-empty) directions` sits four lines away AND A WEDGE READS 3 ON IT, so it
    is recorded BESIDE the geometric line and NEVER instead of it."""
    out = {"per_level": {}, "verdict": "PASS", "dimensionality_failed": []}
    for lv in LEVELS:
        j = recs[lv]
        cells_ok = (j["cells"] == CELLS[lv])
        pat = [(p["name"], p["type"], p["nFaces"]) for p in j["patches"]]
        pat_ok = (sorted(pat) == sorted([tuple(x) for x in PATCHES_REGISTERED[lv]]))
        bad_types = sorted({p["type"] for p in j["patches"]} & {"empty", "wedge"})
        gdirs = j["geometric_directions"]
        if not isinstance(gdirs, list) or not gdirs:
            refuse("G-MESH", {"geometric_directions_unreadable": gdirs, "level": lv,
                              "note": "the authoritative line is `Mesh has N geometric "
                                      "(non-empty/wedge) directions`; absent -> REFUSE"})
        dim_ok = all(int(g) == GEOMETRIC_DIRECTIONS_REQUIRED for g in gdirs)
        both_checkmesh = ("checkmesh_strict_log" in j and "checkmesh_plain_log" in j)
        ok = cells_ok and pat_ok and not bad_types and dim_ok
        out["per_level"][lv] = {"cells": j["cells"], "cells_registered": CELLS[lv], "cells_ok": cells_ok,
                                "patches": pat, "patches_ok": pat_ok, "empty_or_wedge_patches": bad_types,
                                "geometric_directions_every_occurrence": gdirs,
                                "solution_directions_recorded_beside_it": j.get("solution_directions"),
                                "dimensionality_ok": dim_ok,
                                "both_checkmesh_logs_retained": both_checkmesh,
                                "checkmesh_plain": j["checkmesh_plain"], "ok": ok}
        if not dim_ok:
            out["dimensionality_failed"].append(lv)
        if not ok:
            out["verdict"] = "GATE FAIL"
    return out


def g_mesh_strict(recs):
    """SECTION 4.2, and it is a CONSISTENCY gate, not a health gate.  MEASURED on all
    three generated levels AND on the D8R graded mesh: plain checkMesh reads `Mesh OK.` on
    all four while strict fails the SAME TWO checks on all four, at the HIGHEST
    small-determinant fraction (0.2331) on the mesh that already carries a two-row PASS.
    A "strict must pass" gate would therefore fail every level of a family whose finest
    member is already graded, and registering one would be theatre."""
    out = {"per_level": {}, "verdict": "PASS"}
    for lv in LEVELS:
        j = recs[lv]
        got = sorted(j["strict_failed_checks"])
        want = sorted(STRICT_EXPECTED_CHECKS)
        checks_ok = (got == want)
        frac = float(j["small_det_fraction"])
        frac_ok = SMALL_DET_BAND[0] <= frac <= SMALL_DET_BAND[1]
        out["per_level"][lv] = {"strict_failed_checks_by_name": got, "registered_two": want,
                                "exactly_the_registered_two": checks_ok,
                                "plain_checkMesh_said": j["checkmesh_plain"],
                                "bad_face_tets": j.get("bad_face_tets"), "small_det_cells": j.get("small_det_cells"),
                                "small_det_fraction": frac, "band": list(SMALL_DET_BAND), "fraction_in_band": frac_ok,
                                "ok": checks_ok and frac_ok}
        if not (checks_ok and frac_ok):
            out["verdict"] = "GATE FAIL"
    return out


def g_sys(recs):
    """SECTION 4.3 -- the discriminator A3's family fails.  Cell ratios must be the EXACT
    integers 8 and 8 (r^3 at r = 2): a ratio of ~2 means the family refines ONE direction
    whatever its cell count looks like.  THE SURFACES ARE COMPARED BY COORDINATES, NOT BY
    md5: re-running cgns_utils coarsen on the same input produced a file byte-different at
    identical size (552,960 bytes both ways), so CGNS file bytes are not reproducible and
    md5 equality across a regeneration proves nothing."""
    c = [recs[lv]["cells"] for lv in LEVELS]
    ratios = [c[1] / c[0], c[2] / c[1]]
    ratios_ok = (c[1] == c[0] * CELL_RATIOS_REGISTERED[0] and c[2] == c[1] * CELL_RATIOS_REGISTERED[1])
    pts = [recs[lv]["surface_points"] for lv in LEVELS]
    pts_ok = (pts == [SURFACE_POINTS[lv] for lv in LEVELS])
    deltas = {lv: recs[lv].get("surface_max_coord_delta_to_finer") for lv in LEVELS}
    distinct_ok = all((deltas[lv] is not None and float(deltas[lv]) > 1.0e-6) for lv in ("L1", "L2"))
    face_ok = True
    for i, lv in enumerate(LEVELS[1:], start=1):
        prev = LEVELS[i - 1]
        for name in ("wing", "inout", "sym"):
            a = [p["nFaces"] for p in recs[prev]["patches"] if p["name"] == name]
            b = [p["nFaces"] for p in recs[lv]["patches"] if p["name"] == name]
            if not a or not b or b[0] != 4 * a[0]:
                face_ok = False
    out = {"cells": dict(zip(LEVELS, c)), "cell_ratios": ratios, "registered_ratios": list(CELL_RATIOS_REGISTERED),
           "cell_ratios_are_the_exact_integers": ratios_ok,
           "surface_points": dict(zip(LEVELS, pts)), "surface_points_ok": pts_ok,
           "surface_max_coord_delta_to_finer": deltas, "surfaces_pairwise_distinct_in_coordinates": distinct_ok,
           "patch_faces_scale_by_exactly_4": face_ok,
           "md5_is_not_the_instrument_here": "CGNS bytes are not reproducible; coordinates are compared"}
    out["verdict"] = "PASS" if (ratios_ok and pts_ok and distinct_ok and face_ok) else "GATE FAIL"
    return out


def g_body(recs):
    """SECTION 4.4 -- the family must refine the DISCRETISATION, not change the BODY.
    L1's leading edge is truncated by 7.1e-3 against L2/L3 (0.41 % of root chord); that is
    registered BEFORE the run as a named non-similarity and the plausible cause of a
    non-CONVERGING triple (P3)."""
    out = {"pairs": {}, "verdict": "PASS"}
    for (fine, coarse), tol in sorted(BBOX_TOL.items()):
        worst, axis = 0.0, None
        for ax in ("x", "y", "z"):
            a, b = recs[fine]["bbox"][ax], recs[coarse]["bbox"][ax]
            for i in (0, 1):
                d = abs(float(a[i]) - float(b[i]))
                if d > worst:
                    worst, axis = d, "%s[%d]" % (ax, i)
        ok = worst <= tol
        out["pairs"]["%s<->%s" % (fine, coarse)] = {"max_abs_delta": worst, "on_axis": axis, "tol": tol, "ok": ok}
        if not ok:
            out["verdict"] = "GATE FAIL"
    return out


def g_te(recs):
    """SECTION 4.4, G-TE.  A LEVEL THAT CLOSES THE TE WHERE A FINER LEVEL DOES NOT IS NOT
    THE SAME BODY AND KILLS THE TRIPLE -> NOT A RESULT, not GATE FAIL.  This is why c4 is
    out of the family: its tip band drops to 8.441e-4 on the z-spread."""
    out = {"per_level": {}, "verdict": "PASS", "levels_failed": []}
    for lv in LEVELS:
        t = recs[lv]["te_bands"]
        mn = int(t["min_points"])
        lo, hi = float(t["zspread_over_chord_min"]), float(t["zspread_over_chord_max"])
        ok = (mn >= TE_MIN_POINTS_PER_BAND and TE_ZSPREAD_BAND[0] <= lo and hi <= TE_ZSPREAD_BAND[1])
        out["per_level"][lv] = {"min_points_per_band": mn, "min_points_required": TE_MIN_POINTS_PER_BAND,
                                "zspread_over_chord_range": [lo, hi], "band": list(TE_ZSPREAD_BAND), "ok": ok}
        if not ok:
            out["verdict"] = "NOT A RESULT"
            out["levels_failed"].append(lv)
    return out


# ================= G-PRIMAL (section 4.5) =============================================
def g_primal(arm, logtext):
    """Reads THIS ARM'S OWN LOG.  The tolerance read-back REFUSES on a mismatch.
    AMENDMENT 1(b): this threshold equals the solver's own acceptance product
    (checkPrimalFailure() tests primalMaxRes / primalMinResTol_ > primalMinResTolDiff), so
    a primal handed back without an AnalysisError has already satisfied approximately what
    this asks.  IT IS THEREFORE A COMPLETION PRECONDITION AND IS EXPLICITLY NOT THE
    DISCRIMINATING GATE, and it is never quoted alone as evidence that a level converged.
    The discriminating limb is G-PLAT."""
    tol, diff = read_primal_tolerances(logtext, arm)
    seg = last_primal_segment(logtext)
    got = read_max_init_res(seg)
    if got is None:
        refuse("G-PRIMAL", {"arm": arm, "no_initRes_block_parsed": True,
                            "note": "MEASURED on all four D8R logs: `Primal min residual` occurs ZERO "
                                    "times and the initRes block is the only route that reads anything. "
                                    "A gate built on the banner alone would silently measure nothing."})
    mx, per = got
    ok = mx <= ACCEPT_FLOOR
    return {"arm": arm, "log_primalMinResTol": tol, "log_primalMinResTolDiff": diff,
            "registered_pair": [PRIMAL_MIN_RES_TOL, PRIMAL_MIN_RES_TOL_DIFF],
            "accept_floor_is_the_PRODUCT": ACCEPT_FLOOR,
            "max_initRes_at_endTime": mx, "per_equation_initRes": per,
            "finalRes_read": False,
            "diagnostic_vs_1e-6_tutorial_floor": {"floor": TUTORIAL_FLOOR_DIAGNOSTIC,
                                                  "meets_tighter_floor": mx <= TUTORIAL_FLOOR_DIAGNOSTIC,
                                                  "status": "REPORTED, NEVER GRADED"},
            "is_a_completion_precondition_not_the_discriminating_gate": True,
            "verdict": "PASS" if ok else "NOT A RESULT"}


# ================= G-PLAT (AMENDMENT 1(a)) ============================================
def g_plat(hists, values):
    """hists[level][of] = the functional history; values[level][of] = the graded value.
    DELTA_REF is the SMALLEST adjacent level-to-level difference in the family, and the
    iterative error must be at least PLAT_FACTOR times smaller than it.  A failure on
    EITHER functional makes that level NOT A RESULT -- section 4.6 grades CD AND CL."""
    out = {"per_functional": {}, "levels_failed": [], "verdict": "PASS"}
    for of in PLAT_FUNCTIONALS:
        f = [values[lv][of] for lv in LEVELS]
        d21, d32 = abs(f[0] - f[1]), abs(f[1] - f[2])
        delta_ref = min(d21, d32)
        per = {"level_to_level_differences": {"L1-L2": d21, "L2-L3": d32},
               "DELTA_REF_min_adjacent": delta_ref,
               "DELTA_REF_choice": "the SMALLEST adjacent difference, applied to every level: a "
                                   "per-level adjacent difference would let a level pass on whichever "
                                   "gap it happens to sit beside",
               "required_max_iterative_error": delta_ref / PLAT_FACTOR, "levels": {}}
        for lv in LEVELS:
            h = hists[lv][of]
            if not h:
                refuse("G-PLAT", {"level": lv, "functional": of, "no_history": True,
                                  "note": "the source is the solver's own `%s:` lines at printInterval; "
                                          "none were printed" % of})
            w = plateau_window(h)
            st = plateau_statistic(w)
            if st["n_window"] < PLAT_MIN_SAMPLES:
                lvv = "NOT A RESULT"
                reason = ("window holds %d < %d samples: NOT A RESULT FOR WANT OF EVIDENCE -- a window "
                          "that cannot exhibit an excursion cannot prove a plateau" % (st["n_window"], PLAT_MIN_SAMPLES))
                ok = False
            else:
                ok = (delta_ref > 0.0) and (st["peak_to_peak"] * PLAT_FACTOR <= delta_ref)
                lvv = "PASS" if ok else "NOT A RESULT"
                reason = ("peak-to-peak %.6e x %g %s DELTA_REF %.6e"
                          % (st["peak_to_peak"], PLAT_FACTOR, "<=" if ok else ">", delta_ref))
            per["levels"][lv] = {"n_samples_printed": len(h), "window": st, "statistic": "PEAK_TO_PEAK_max_minus_min",
                                 "verdict": lvv, "reason": reason,
                                 "would_an_adjacent_delta_test_have_passed":
                                     (st["REFUSED_BY_NAME_adjacent_sample_delta_max"] * PLAT_FACTOR <= delta_ref)
                                     if delta_ref > 0.0 else False}
            if not ok:
                out["verdict"] = "NOT A RESULT"
                if lv not in out["levels_failed"]:
                    out["levels_failed"].append(lv)
        out["per_functional"][of] = per
    return out


# ================= G-TRIPLE (section 4.6) =============================================
def gci(f_coarse, f_med, f_fine):
    """Observed order and GCI on the finest level.  Refuses to invent an order.
    TRANSPLANTED VERBATIM from the lab's own frozen classifier,
    verification/runs/T-family/T1_runs/analyse_t1c.py:321, at R_REFINE = 2.0 and FS = 1.25.
    CONVERGING implies e32/e21 > 0, i.e. THE THREE VALUES ARE MONOTONE, so a GCI is quoted
    only on a monotone triple -- never otherwise (standing rule 5)."""
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    if e21 == 0.0:
        return dict(state="EXACT")
    if e32 / e21 < 0.0:
        return dict(state="OSCILLATORY")
    p = math.log(abs(e32 / e21)) / math.log(R_REFINE)
    if p <= 0.0:
        return dict(state="DIVERGENT", order=p)
    if p < 0.5:
        return dict(state="STAGNANT", order=p)
    den = R_REFINE ** p - 1.0
    return dict(state="CONVERGING", order=p,
                GCI_pct=100.0 * FS * abs(e21 / f_fine) / den,
                richardson=f_fine + e21 / den)


def g_triple(values, level_ok, why_not):
    """STANDING RULE 5, IN ORDER.  (1) any level not iteratively converged or not plateaued
    -> NOT A RESULT; (2) DIVERGENT / STAGNANT / OSCILLATORY / EXACT -> NOT A RESULT with
    the value, BOTH triples and BOTH observed orders printed beside it; (3) CONVERGING ->
    PASS inside the registered band else GATE FAIL, GCI printed.
    THE GATE CAN ONLY TURN A PASS OR GATE FAIL INTO NOT A RESULT, NEVER THE REVERSE."""
    triples = {of: [values[lv][of] for lv in LEVELS] for of in PLAT_FUNCTIONALS}
    states = {of: gci(*triples[of]) for of in PLAT_FUNCTIONALS}
    out = {"r": R_REFINE, "Fs": FS, "p_band": list(P_BAND), "levels": list(LEVELS),
           "triples_both": triples,
           "orders_both": {of: states[of].get("order") for of in PLAT_FUNCTIONALS},
           "states_both": {of: states[of]["state"] for of in PLAT_FUNCTIONALS},
           "per_functional": {},
           "no_gradient_triple": "section 7: the adjoint is BLOCKED at L3 on memory AND, independently, "
                                 "on conditioning (DARhoSimpleCFoam stagnates at 79,560 cells, "
                                 "PetscConvergedReason -3).  TWO LEVELS IS NOT A TRIPLE and NO ORDER OF "
                                 "ACCURACY IS QUOTED FOR THE GRADIENT."}
    if not all(level_ok.values()):
        out["verdict"] = "NOT A RESULT"
        out["reason"] = "clause 1: level(s) not iteratively converged or not plateaued: %s" % why_not
        return out
    verdicts = []
    for of in PLAT_FUNCTIONALS:
        g = states[of]
        e = {"triple": triples[of], "state": g["state"], "order": g.get("order")}
        if g["state"] != "CONVERGING":
            e["verdict"] = "NOT A RESULT"
            e["reason"] = "clause 2: triple is %s; value, BOTH triples and BOTH orders printed beside it" % g["state"]
            e["GCI_pct"] = None
            e["gci_note"] = "NO GCI IS QUOTED: the three values are not monotone/converging"
        else:
            inside = P_BAND[0] <= g["order"] <= P_BAND[1]
            e["verdict"] = "PASS" if inside else "GATE FAIL"
            e["GCI_pct"] = g["GCI_pct"]
            e["richardson_extrapolated_fine"] = g["richardson"]
            e["reason"] = "clause 3: observed order %.4f %s the registered band %s" % (
                g["order"], "inside" if inside else "OUTSIDE", list(P_BAND))
        out["per_functional"][of] = e
        verdicts.append(e["verdict"])
    out["verdict"] = "NOT A RESULT" if "NOT A RESULT" in verdicts else ("GATE FAIL" if "GATE FAIL" in verdicts else "PASS")
    return out


# ================= G-FD: THE BRIGHT LINE (section 4.7) ================================
def _vec_rel_err_pct(fd, an):
    """THE NAMED STATISTIC (DAFOAM_CHARTER.md section 2): the VECTOR-RELATIVE error
    ||J_an - J_fd|| / ||J_fd|| AS PRINTED.  NOT a per-component average, and never
    compared against the published per-component averages of the method papers."""
    den = math.sqrt(sum(a ** 2 for a in fd))
    if den <= 0.0:
        return None
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(fd, an))) / den * 100.0


def _cosine(fd, an):
    na = math.sqrt(sum(a ** 2 for a in fd))
    nb = math.sqrt(sum(b ** 2 for b in an))
    if na <= 0.0 or nb <= 0.0:
        return None
    return sum(a * b for a, b in zip(fd, an)) / (na * nb)


def _sweep_table(A, F, of, flagged_keys):
    """THE SWEEP TABLE REPORTS EVERY STEP AS A ROW, INCLUDING THE FAILED ONES, in the
    registered shape | step | rel err | rel err (excl. flagged) | cosine | status |.  The
    trivial baseline is a row here too, marked as the control it is."""
    key_d = "dCD" if of == "CD" else "dCL"
    rows = []
    for s in sorted(STEPS_REGISTERED["twist"] + [TRIVIAL_STEP]):
        fd_all, an_all, fd_ex, an_ex, missing = [], [], [], [], []
        for dv, idx in COMPONENTS_REGISTERED:
            j = A["adjoint"][of][dv][idx] if idx < len(A["adjoint"][of][dv]) else None
            row = F["table"].get((dv, idx))
            v = (row or {}).get("fd", {}).get(s)
            if j is None or v is None or not v["ok"]:
                missing.append("%s[%d]" % (dv, idx))
                continue
            fd_all.append(v[key_d])
            an_all.append(j)
            if (dv, idx) not in flagged_keys:
                fd_ex.append(v[key_d])
                an_ex.append(j)
        status = "MEASURED" if not missing else "INCOMPLETE: missing %s" % ",".join(missing)
        if abs(s - TRIVIAL_STEP) < 1e-15:
            status += " | SECTION-4 TRIVIAL BASELINE CONTROL, PREDICTED > %.1f %%" % FD_CONDITIONAL_PCT
        rows.append({"step_deg": s, "rel_err_pct": (_vec_rel_err_pct(fd_all, an_all) if fd_all else None),
                     "rel_err_pct_excl_flagged": (_vec_rel_err_pct(fd_ex, an_ex) if fd_ex else None),
                     "cosine": (_cosine(fd_all, an_all) if fd_all else None),
                     "n_components": len(fd_all), "status": status})
    return rows


def grade_components(A, F, of):
    """PLATEAU READ PER COMPONENT across the three registered steps; a component that
    stabilises nowhere is FLAGGED AND EXCLUDED BY NAME.  D8R read "the middle agrees with
    at least one neighbour to 10 %"; D8G's registration reads the SPREAD across the three
    steps, which is strictly the stronger test, and this file implements what D8G
    registered."""
    key_d = "dCD" if of == "CD" else "dCL"
    comps, graded_fd, graded_adj, flagged, flagged_keys = [], [], [], [], set()
    for dv, idx in COMPONENTS_REGISTERED:
        name = "%s[%d]" % (dv, idx)
        j = A["adjoint"][of][dv][idx] if idx < len(A["adjoint"][of][dv]) else None
        row = F["table"].get((dv, idx))
        c = {"dv": dv, "idx": idx, "name": name, "J_adj": j}
        if row is None or j is None:
            c.update({"verdict": "NOT A RESULT", "reason": "ABSENT", "flagged": True})
            flagged.append(name); flagged_keys.add((dv, idx)); comps.append(c)
            continue
        steps = sorted(STEPS_REGISTERED[dv])
        vals = [row["fd"].get(s) for s in steps]
        if any(v is None or not v["ok"] for v in vals):
            c.update({"verdict": "NOT A RESULT", "reason": "FD_STEP_FAILED_OR_ABSENT",
                      "steps_present": sorted(row["fd"]), "flagged": True})
            flagged.append(name); flagged_keys.add((dv, idx)); comps.append(c)
            continue
        d = [v[key_d] for v in vals]
        ref = d[1]                                    # the MIDDLE step is the reference
        c.update({"steps": steps, "d_fd": d, "d_ref": ref})
        if abs(ref) < NEAR_ZERO_ABS:
            c.update({"verdict": "NOT A RESULT", "reason": "NEAR_ZERO", "flagged": True})
            flagged.append(name); flagged_keys.add((dv, idx)); comps.append(c)
            continue
        spread_pct = (max(d) - min(d)) / abs(ref) * 100.0
        c["plateau_spread_pct_across_three_steps"] = spread_pct
        c["plateau_tol_pct"] = PLATEAU_TOL_PCT
        if spread_pct > PLATEAU_TOL_PCT:
            c.update({"verdict": "NOT A RESULT", "reason": "NO_PLATEAU_ANYWHERE_IN_THE_SWEEP",
                      "flagged": True,
                      "note": "FLAGGED AND EXCLUDED BY NAME from any aggregate quoted as agreement -- "
                              "never dropped silently and never rescued by a step at which it crosses"})
            flagged.append(name); flagged_keys.add((dv, idx)); comps.append(c)
            continue
        rel = abs(ref - j) / abs(ref) * 100.0
        flip = bool(ref * j < 0.0)
        c.update({"rel_err_pct": rel, "sign_flip": flip, "flagged": False})
        c["verdict"] = "GATE FAIL" if (flip or rel > FD_PASS_PCT) else "PASS"
        graded_fd.append(ref)
        graded_adj.append(j)
        comps.append(c)
    out = {"objective": of, "components": comps, "n_graded": len(graded_fd),
           "flagged_components_BY_NAME": flagged,
           "n_pass": sum(1 for c in comps if c.get("verdict") == "PASS"),
           "n_gate_fail": sum(1 for c in comps if c.get("verdict") == "GATE FAIL"),
           "n_not_a_result": sum(1 for c in comps if c.get("verdict") == "NOT A RESULT"),
           "sign_flips": sum(1 for c in comps if c.get("sign_flip")),
           "sign_flipped_BY_NAME": [c["name"] for c in comps if c.get("sign_flip")],
           "statistic": "vector-relative error ||J_an - J_fd|| / ||J_fd|| AS PRINTED "
                        "(NOT a per-component average)",
           "sweep_table": _sweep_table(A, F, of, flagged_keys)}
    if out["n_graded"] < MIN_GRADED:
        out.update({"verdict": "NOT A RESULT", "aggregate_rel_err_pct": None, "band": None,
                    "reason": "fewer than %d graded components" % MIN_GRADED})
        return out
    agg = _vec_rel_err_pct(graded_fd, graded_adj)
    out["aggregate_rel_err_pct"] = agg
    out["cosine_graded"] = _cosine(graded_fd, graded_adj)
    # ---- THE REGISTERED BANDS.  `CONDITIONAL` and bare `FAIL` are NOT verdict tokens
    # ---- (CLAUDE.md rule 1): the band label is DATA, the verdict is from the fixed six.
    if out["sign_flips"] > 0:
        out["band"] = "FAIL"
        out["band_reason"] = ("ANY sign-flipped component is FAIL REGARDLESS OF THE AGGREGATE: %s"
                              % out["sign_flipped_BY_NAME"])
        out["verdict"] = "GATE FAIL"
    elif agg > FD_CONDITIONAL_PCT:
        out["band"] = "FAIL"
        out["band_reason"] = "aggregate %.4f %% > %.1f %%" % (agg, FD_CONDITIONAL_PCT)
        out["verdict"] = "GATE FAIL"
    elif agg > FD_PASS_PCT:
        out["band"] = "CONDITIONAL"
        out["band_reason"] = ("aggregate %.4f %% in (%.1f, %.1f] %%; the per-component breakdown is "
                              "printed above, as the band requires" % (agg, FD_PASS_PCT, FD_CONDITIONAL_PCT))
        out["verdict"] = "GATE FAIL"
    elif flagged:
        out["band"] = "CONDITIONAL_FLAGGED"
        out["band_reason"] = ("aggregate %.4f %% <= %.1f %% BUT the registered PASS band requires ZERO "
                              "flagged components and these stabilised nowhere: %s" % (agg, FD_PASS_PCT, flagged))
        out["verdict"] = "GATE FAIL"
    else:
        out["band"] = "PASS"
        out["band_reason"] = "aggregate %.4f %% <= %.1f %% with ZERO flagged components" % (agg, FD_PASS_PCT)
        out["verdict"] = "PASS"
    out["vocabulary_note"] = ("the registered band label is carried as DATA in `band`; the VERDICT token is "
                              "from the fixed six (CLAUDE.md rule 1), GATE FAIL for CONDITIONAL and FAIL")
    # ---- THE SECTION-4 TRIVIAL BASELINE, AND ITS WITHDRAWAL -----------------------
    trivial = _trivial_baseline(A, F, of, [c for c in comps if not c.get("flagged")])
    out["trivial_baseline"] = trivial
    if trivial["also_passed"]:
        out["withdrawn_verdict"] = out["verdict"]
        out["withdrawn_band"] = out["band"]
        out["verdict"] = "NOT A RESULT"
        out["band"] = None
        out["reason"] = ("TRIVIAL_BASELINE_ALSO_PASSED -- THE FD VERDICT IS WITHDRAWN.  The deliberately "
                         "wrong step %.0e deg, registered as PREDICTED > %.1f %%, returned %.4f %%.  "
                         "A gate a two-orders-too-small step also satisfies is not measuring what it "
                         "claims, so the verdict it produced does not stand."
                         % (TRIVIAL_STEP, FD_CONDITIONAL_PCT, trivial["aggregate_rel_err_pct"]))
    return out


def _trivial_baseline(A, F, of, graded_comps):
    """SECTION 4 TRIVIAL BASELINE (DAFOAM_CHARTER.md section 4), registered BEFORE its own
    run: the same probe at 1e-3 deg, two orders below the registered step and below the
    bottom of D8's measured plateau, PREDICTED TO GIVE > 15 %.  IF THE DELIBERATELY WRONG
    STEP ALSO PASSES, THE GATE IS NOT MEASURING WHAT IT CLAIMS AND THE FD VERDICT IT
    PRODUCED IS WITHDRAWN.  `also passed` means the trivial aggregate did NOT exceed the
    registered FAIL floor -- i.e. the control failed to discriminate."""
    key_d = "dCD" if of == "CD" else "dCL"
    fd, an, missing = [], [], []
    for c in graded_comps:
        dv, idx = c["dv"], c["idx"]
        row = F["table"].get((dv, idx))
        v = (row or {}).get("fd", {}).get(TRIVIAL_STEP)
        j = A["adjoint"][of][dv][idx] if idx < len(A["adjoint"][of][dv]) else None
        if v is None or not v["ok"] or j is None:
            missing.append(c["name"])
            continue
        fd.append(v[key_d])
        an.append(j)
    if len(fd) < MIN_GRADED:
        refuse("G-FD-TRIVIAL", {"objective": of, "n_components_at_trivial_step": len(fd),
                                "missing": missing, "trivial_step": TRIVIAL_STEP,
                                "note": "the trivial baseline is REGISTERED and is not optional; without "
                                        "it the FD gate has not been shown able to fail"})
    agg = _vec_rel_err_pct(fd, an)
    return {"step_deg": TRIVIAL_STEP, "n_components": len(fd), "aggregate_rel_err_pct": agg,
            "registered_prediction": "> %.1f %%" % FD_CONDITIONAL_PCT,
            "prediction": "HIT" if agg > FD_CONDITIONAL_PCT else "MISS",
            "also_passed": bool(agg <= FD_CONDITIONAL_PCT),
            "consequence_if_also_passed": "THE FD VERDICT IS WITHDRAWN (implemented, not warned about)"}


# ================= G9 / G10 / G12 (INHERITED FROM D8R; G10 is REPORT-ONLY here) ========
def g_toolchain(rows):
    out = {"per_arm": {}, "verdict": "PASS"}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        row = ARM_ROW[arm]
        m = re.search(r"D4S_IDWARP_SO_MD5:\s*([0-9a-f]{32})", r.get("log_text", ""))
        printed = m.group(1) if m else None
        art_md5 = r.get("artefact_so_md5")
        ok = (r.get("DIGEST") == IMG_DIGEST[row]) and (printed == SO_MD5[row]) and (art_md5 == SO_MD5[row])
        out["per_arm"][arm] = {"row": row, "digest": r.get("DIGEST"), "printed_so_md5": printed,
                               "artefact_so_md5": art_md5, "ok": bool(ok)}
        if not ok:
            out["verdict"] = "GATE FAIL"
    return out


def g_caps(rows):
    """D8G DELTA, AND IT IS A REGISTERED ONE.  PREREGISTRATION.md section 6.4 suspends the
    stop for this item, quoting Sanaa 2026-09-10: "for all these 3D cases that still need
    to run, i dont want to see any budget gates ( time or money)".  A crossing is therefore
    REPORTED WITH ITS RATIO AND DOES NOT COMPOSE TO GATE FAIL.  THE ESTIMATE IS STILL MADE,
    THE ACTUAL IS STILL MEASURED AND THE CALIBRATION ROW IS STILL OWED (rule 12)."""
    out = {"per_arm": {}, "verdict": "PASS", "total_core_min": 0.0, "ceiling": ITEM_CEILING_CORE_MIN,
           "cap_is_a_stop": CAP_IS_A_STOP, "crossings_reported": [], "not_measured": [],
           "exemption": "section 6.4, Sanaa 2026-09-10: no budget gates on the 3D cases; the cap is "
                        "CALIBRATION, NOT A STOP, and this gate is REPORT-ONLY on this item"}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        cm = r.get("core_min")
        if cm is None:
            out["not_measured"].append(arm)
            out["per_arm"][arm] = {"core_min": NOT_MEASURED, "cap": CAPS[arm],
                                   "predicted": PREDICTED_CORE_MIN[arm], "ratio_actual_over_predicted": NOT_MEASURED}
            continue
        out["total_core_min"] += cm
        crossed = cm > CAPS[arm]
        out["per_arm"][arm] = {"core_min": cm, "cap": CAPS[arm], "crossed": crossed,
                               "predicted": PREDICTED_CORE_MIN[arm],
                               "ratio_actual_over_predicted": round(cm / PREDICTED_CORE_MIN[arm], 4)}
        if crossed:
            out["crossings_reported"].append(arm)
    out["total_predicted_core_min"] = round(sum(PREDICTED_CORE_MIN.values()), 3)
    if not out["not_measured"]:
        out["ratio_actual_over_predicted_item"] = round(out["total_core_min"] / out["total_predicted_core_min"], 4)
        out["calibration_row_owed"] = "docs/COST_CALIBRATION.md (CLAUDE.md rule 12); the gap is attributed "
    if out["total_core_min"] > ITEM_CEILING_CORE_MIN:
        out["ceiling_crossed_REPORTED"] = True
    return out


def g_placement(rows):
    out = {"per_arm": {}, "verdict": "PASS", "not_measured": [], "cpusets_seen": [],
           "cpuset_registered": CPUSET_REGISTERED,
           "cpuset_provenance": "INHERITED FROM THE D8R PRODUCER; PREREGISTRATION.md section 3 registers "
                                "'cpuset assigned by the launcher' and NO SPECIFIC SET -- the supervisor "
                                "must register it at the freeze"}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        cs = r.get("cpuset")
        if cs not in out["cpusets_seen"]:
            out["cpusets_seen"].append(cs)
        cs_ok = cs == CPUSET_REGISTERED
        d = r.get("delivered")
        dl = None
        m = re.match(r"\s*([\d.]+)\s+n=(\d+)", d or "")
        if m:
            dl = float(m.group(1))
        if dl is None:
            out["not_measured"].append(arm)
        dl_ok = True if dl is None else dl >= DELIVERED_CORES_FLOOR
        out["per_arm"][arm] = {"cpuset": cs, "delivered_cores_mean": (dl if dl is not None else NOT_MEASURED)}
        if not (cs_ok and dl_ok):
            out["verdict"] = "GATE FAIL"
    if len(out["cpusets_seen"]) > 1:
        out["verdict"] = "GATE FAIL"
        out["reason"] = "placement is not constant across the family: %s" % out["cpusets_seen"]
    return out


# ================= VERDICT COMPOSITION (section 4.9) ==================================
def compose_level(g_mesh_lv, g_strict_lv, g_sys_v, g_body_v, g_te_lv, g_primal_v, g_plat_lv):
    """LEVEL = NOT A RESULT if G-PRIMAL, G-TE or the dimensionality clause of G-MESH
    fails, or if G-PLAT fails; else GATE FAIL if G-MESH-STRICT, G-BODY or G-SYS fails;
    else PASS."""
    if g_primal_v == "NOT A RESULT" or g_te_lv == "NOT A RESULT" or not g_mesh_lv["dimensionality_ok"] \
            or g_plat_lv == "NOT A RESULT":
        return "NOT A RESULT"
    if (not g_strict_lv["ok"]) or g_body_v == "GATE FAIL" or g_sys_v == "GATE FAIL" or not g_mesh_lv["ok"]:
        return "GATE FAIL"
    return "PASS"


def compose_row(levels, g_triple_v, g_fd_cd, g_fd_cl):
    """ROW = NOT A RESULT if any level is, or if G-TRIPLE is; else GATE FAIL if G-TRIPLE
    or G-FD is; else PASS."""
    vs = list(levels.values())
    if "NOT A RESULT" in vs or g_triple_v == "NOT A RESULT" or "NOT A RESULT" in (g_fd_cd, g_fd_cl):
        return "NOT A RESULT"
    if "GATE FAIL" in vs + [g_triple_v, g_fd_cd, g_fd_cl]:
        return "GATE FAIL"
    return "PASS"


# ================= the grade ==========================================================
def grade(root):
    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)

    # ---- the mesh family, from the per-level construction records -------------------
    recs = {lv: read_mesh_record(root, lv) for lv in LEVELS}
    gmesh, gstrict, gsys, gbody, gte = g_mesh(recs), g_mesh_strict(recs), g_sys(recs), g_body(recs), g_te(recs)

    # ---- G-M2: every arm ran THE LEVEL'S OWN MESH, by hash --------------------------
    gm2 = {"per_arm": {}, "verdict": "PASS", "level_points_md5": {lv: recs[lv]["points_md5"] for lv in LEVELS}}
    for arm in ARMS_REQUIRED:
        p = os.path.join(root, arm, "constant", "polyMesh", "points.gz")
        if not os.path.isfile(p):
            refuse("G-M2", {"points_absent": p, "arm": arm})
        h = md5_of(p)
        want = recs[ARM_LEVEL[arm]]["points_md5"]
        gm2["per_arm"][arm] = {"level": ARM_LEVEL[arm], "points_md5": h, "registered": want, "ok": h == want}
        if h != want:
            gm2["verdict"] = "GATE FAIL"

    # ---- the artefacts, per row -----------------------------------------------------
    P, A, F = {"S": {}, "P": {}}, {}, {}
    for arm in ARMS_REQUIRED:
        rk = "S" if arm.endswith("-S") else "P"
        path = os.path.join(root, arm, ARTEFACT[arm])
        if ARM_MODE[arm] == "P":
            P[rk][ARM_LEVEL[arm]] = read_P(path)
            rows[arm]["artefact_so_md5"] = P[rk][ARM_LEVEL[arm]]["so_md5"]
            if P[rk][ARM_LEVEL[arm]]["level"] != ARM_LEVEL[arm]:
                refuse("G-MESH", {"artefact_level_mismatch": arm, "artefact_says": P[rk][ARM_LEVEL[arm]]["level"]})
            if P[rk][ARM_LEVEL[arm]]["cells"] != CELLS[ARM_LEVEL[arm]]:
                refuse("G-MESH", {"artefact_cells_not_registered": arm, "cells": P[rk][ARM_LEVEL[arm]]["cells"],
                                  "registered": CELLS[ARM_LEVEL[arm]]})
        elif ARM_MODE[arm] == "A":
            A[rk] = read_A(path)
            rows[arm]["artefact_so_md5"] = A[rk]["so_md5"]
        else:
            F[rk] = read_F(path)
            rows[arm]["artefact_so_md5"] = F[rk]["so_md5"]
        art = P[rk][ARM_LEVEL[arm]] if ARM_MODE[arm] == "P" else (A[rk] if ARM_MODE[arm] == "A" else F[rk])
        if art.get("nprocs") != NPROCS_REGISTERED:
            refuse("G12", {"nprocs_not_registered": arm, "nprocs": art.get("nprocs"), "registered": NPROCS_REGISTERED})
    for rk, fa in (("S", "F2-S"), ("P", "F2-P")):
        if F[rk]["adjoint_md5"] != A[rk]["md5"]:
            refuse("G-FD", {"F_arm_gradient_is_not_this_rows_A_artefact": fa,
                            "adjoint_source_md5": F[rk]["adjoint_md5"], "A_md5": A[rk]["md5"]})
        if F[rk]["level"] != FD_LEVEL or A[rk]["level"] != FD_LEVEL:
            refuse("G-FD", {"FD_not_at_the_registered_level": fa, "F_level": F[rk]["level"],
                            "A_level": A[rk]["level"], "registered": FD_LEVEL})

    # ---- THE PLANTED CONTROLS, THROUGH THE REAL PATH (rule 3, section 4.8) ----------
    controls = {}
    for rk, parm, farm in (("S", "L2-S", "F2-S"), ("P", "L2-P", "F2-P")):
        controls["functional_plant_" + rk] = functional_plant_control(
            root, os.path.join(root, parm, "d8g_P.json"), rk)
        controls["residual_plant_" + rk] = residual_plant_control(root, rows[parm]["log_text"], rk)
        controls["ctrl_" + rk] = ctrl_control(F[rk])
        controls["grader_plant_" + rk] = grader_plant_control(root, os.path.join(root, farm, "d8g_F.json"), rk)

    # ---- the per-row grade ----------------------------------------------------------
    g = {}
    for rk in ("P", "S"):
        values = {lv: {"CD": P[rk][lv]["CD"], "CL": P[rk][lv]["CL"]} for lv in LEVELS}
        gp = {lv: g_primal("%s-%s" % (lv, rk), rows["%s-%s" % (lv, rk)]["log_text"]) for lv in LEVELS}
        hists = {}
        for lv in LEVELS:
            seg = last_primal_segment(rows["%s-%s" % (lv, rk)]["log_text"])
            hists[lv] = {of: read_functional_history(seg, of) for of in PLAT_FUNCTIONALS}
        gpl = g_plat(hists, values)
        level_ok, why_not = {}, []
        for lv in LEVELS:
            plat_lv = "PASS"
            for of in PLAT_FUNCTIONALS:
                if gpl["per_functional"][of]["levels"][lv]["verdict"] != "PASS":
                    plat_lv = "NOT A RESULT"
            ok = (gp[lv]["verdict"] == "PASS" and plat_lv == "PASS")
            level_ok[lv] = ok
            if not ok:
                why_not.append("%s (G-PRIMAL=%s, G-PLAT=%s)" % (lv, gp[lv]["verdict"], plat_lv))
        gt = g_triple(values, level_ok, why_not)
        fd_cd = grade_components(A[rk], F[rk], "CD")
        fd_cl = grade_components(A[rk], F[rk], "CL")
        lvv = {}
        for lv in LEVELS:
            plat_lv = "PASS"
            for of in PLAT_FUNCTIONALS:
                if gpl["per_functional"][of]["levels"][lv]["verdict"] != "PASS":
                    plat_lv = "NOT A RESULT"
            lvv[lv] = compose_level(gmesh["per_level"][lv], gstrict["per_level"][lv], gsys["verdict"],
                                    gbody["verdict"], ("NOT A RESULT" if lv in gte["levels_failed"] else "PASS"),
                                    gp[lv]["verdict"], plat_lv)
        g[rk] = {"values": values, "G-PRIMAL": gp, "G-PLAT": gpl, "G-TRIPLE": gt,
                 "G-FD_CD": fd_cd, "G-FD_CL": fd_cl, "level_verdicts": lvv,
                 "row_verdict": compose_row(lvv, gt["verdict"], fd_cd["verdict"], fd_cl["verdict"]),
                 "eta_F": F[rk]["eta"]}

    # ---- P5: the free negative control on the two-row machinery (section 8) ---------
    p5 = {}
    for lv in LEVELS:
        p5[lv] = {of: {"shipped": P["S"][lv][of], "patched": P["P"][lv][of],
                       "abs_diff": abs(P["S"][lv][of] - P["P"][lv][of]),
                       "eta_units": abs(P["S"][lv][of] - P["P"][lv][of]) / max(F["P"]["eta"], 1e-300)}
                  for of in PLAT_FUNCTIONALS}
    p5_hit = all(p5[lv][of]["eta_units"] <= 1.0 for lv in LEVELS for of in PLAT_FUNCTIONALS)

    # ---- divergence shipped vs patched on the L2 adjoint (REPORTED, a reading) ------
    div = []
    for dv, idx in COMPONENTS_REGISTERED:
        a, b = A["S"]["adjoint"]["CD"][dv], A["P"]["adjoint"]["CD"][dv]
        if idx < len(a) and idx < len(b):
            den = max(abs(a[idx]), abs(b[idx]), 1e-300)
            div.append({"dv": dv, "idx": idx, "J_shipped": a[idx], "J_patched": b[idx],
                        "divergence_pct": abs(a[idx] - b[idx]) / den * 100.0,
                        "note": "SAME baseline design on both rows, so this IS comparable -- unlike D8R, "
                                "whose two rows sat at different endpoints"})

    g9, g10, g12 = g_toolchain(rows), g_caps(rows), g_placement(rows)

    # ---- predictions, scored never adjusted (section 8) -----------------------------
    preds = {"P1_construction_reproduced": "HIT" if (gmesh["verdict"] == "PASS" and gstrict["verdict"] == "PASS")
             else "MISS",
             "P2_systematicity": "HIT" if gsys["verdict"] == "PASS" else "MISS",
             "P3_CD_triple_CONVERGING_in_band": "HIT" if g["P"]["G-TRIPLE"]["per_functional"].get("CD", {}).get("verdict") == "PASS"
             else ("NOT_MEASURED" if g["P"]["G-TRIPLE"]["verdict"] == "NOT A RESULT" else "MISS"),
             "P4_shipped_FD_FAIL_patched_PASS":
                 "HIT" if (g["S"]["G-FD_CD"]["band"] == "FAIL" and g["P"]["G-FD_CD"]["band"] == "PASS")
                 else ("NOT_MEASURED" if "NOT A RESULT" in (g["S"]["G-FD_CD"]["verdict"], g["P"]["G-FD_CD"]["verdict"])
                       else "MISS"),
             "P5_rows_agree_to_1_eta": "HIT" if p5_hit else "MISS"}
    preds["P6_cost"] = (NOT_MEASURED if g10["not_measured"]
                        else {"total_core_min": g10["total_core_min"],
                              "predicted": g10["total_predicted_core_min"],
                              "ratio_actual_over_predicted": g10.get("ratio_actual_over_predicted_item")})

    # ---- ITEM verdict (composition registered in section 4.9) -----------------------
    rv = (g["S"]["row_verdict"], g["P"]["row_verdict"])
    structural = (gm2["verdict"], gsys["verdict"], gbody["verdict"], gstrict["verdict"], gmesh["verdict"],
                  g9["verdict"], g12["verdict"])
    if "NOT A RESULT" in rv or gte["verdict"] == "NOT A RESULT" or gmesh["dimensionality_failed"]:
        verdict = "NOT A RESULT"
    elif "GATE FAIL" in rv + structural:
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})
    return {"item": "CURRICULUM-%s" % ITEM, "verdict": verdict,
            "rows": {"SHIPPED": g["S"]["row_verdict"], "PATCHED": g["P"]["row_verdict"]},
            "row_reading": ("the PATCHED row is the result-bearing row for the capability cell; A SHIPPED "
                            "GATE FAIL STILL MAKES THE ITEM GATE FAIL, and a patched row never replaces a "
                            "shipped row (DAFOAM_CHARTER.md section 6)"),
            "gates": {"G1_completion": "PASS", "G-MESH": gmesh, "G-MESH-STRICT": gstrict, "G-SYS": gsys,
                      "G-BODY": gbody, "G-TE": gte, "G-M2_mesh_identity_per_level": gm2,
                      "SHIPPED": g["S"], "PATCHED": g["P"],
                      "G6_dot_product_duality": "NOT MEASURED -- the tutorial exposes no dot-product/duality "
                                                "test; named, never composed",
                      "G9_toolchain": g9, "G10_caps_REPORT_ONLY": g10, "G12_placement": g12},
            "P5_two_row_primal_agreement": {"per_level": p5, "hit": p5_hit,
                                            "note": "the IDWarp rotation patch lives in the REVERSE-MODE "
                                                    "mesh-warp derivative and cannot enter a primal at a "
                                                    "fixed baseline design; a larger disagreement is a "
                                                    "finding about the IMAGES, not about the grid"},
            "divergence_shipped_vs_patched_L2_adjoint_CD": div, "predictions": preds,
            "controls": controls, "completion": g1,
            "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"], "G12": g12["not_measured"]},
            "field_classes": {"physics": list(FIELDS_PHYSICS), "infrastructure": list(FIELDS_INFRASTRUCTURE),
                              "rule": "absent infrastructure -> NOT_MEASURED beside the verdict; absent "
                                      "physics -> REFUSE (L-342)"},
            "no_gradient_triple": ("section 7: TWO LEVELS IS NOT A TRIPLE.  The gradient carries a two-row FD "
                                   "table at L2 and NO ORDER OF ACCURACY AT ALL."),
            "not_a_validation": ("section 0.2: no external reference value for CD or CL is registered and none "
                                 "is reachable from this box for this geometry at these conditions.  THIS ITEM "
                                 "CAN NEVER RETURN A PASS AGAINST A MEASUREMENT, ONLY AGAINST A CONVERGENCE "
                                 "CRITERION."),
            "capability_grid_cell": "3D . steady . transonic -- grid convergence on the functionals; the "
                                    "gradient column is evidenced at L2 only"}


# ================= selftest: planted fixtures, counted against a FROZEN unit count ======
# INHERITED SHAPE FROM D8R.  A SUITE THAT PASSES PROVES NOTHING UNTIL IT IS SEEN TO FAIL:
# every gate below is driven in BOTH directions, and d8g_grade_selftest.sh additionally
# MUTATES A COPY OF THIS FILE and asserts the suite then FAILS.
ROWFMT = ("ARM={arm} ROW={row} IMG={img} DIGEST={dig} rc={rc} wall_s={wall} ranks={ranks} core_min={cm} "
          "cap_core_min={cap} enforced_wall_s=600 enforced_core_min={cap} memory=14g inspect(exit,oomkilled)=[{ke} {oom}] "
          "memavail_pre_GiB=20.00 memavail_post_GiB={mpost} cpuset={cs} delivered_cores_mean=[{dl}] "
          "siblings_pre=[] siblings_post=[] log={log} stamp=x\n")

FIX_CD = {"L1": 0.0400, "L2": 0.0380, "L3": 0.0375}       # d21 = 2.0e-3, d32 = 5.0e-4 -> p = 2.000
FIX_CL = {"L1": 0.5000, "L2": 0.4800, "L3": 0.4750}       # same ratio -> p = 2.000
FIX_J = {"twist": [-0.0023, -0.0020, -0.0017, -0.0013, -0.00086, -2.0e-5, -0.00020],
         "patchV": [0.00087, 0.0106]}
FIX_BBOX = {"L3": {"x": [-0.0000, 3.2474], "y": [0.0000, 3.7667], "z": [-0.2029, 0.3461]},
            "L2": {"x": [-0.0000, 3.2474], "y": [0.0000, 3.7667], "z": [-0.2029, 0.3461]},
            "L1": {"x": [0.0071, 3.2471], "y": [0.0000, 3.7659], "z": [-0.2017, 0.3456]}}
FIX_TE = {"L3": {"min_points": 13, "zspread_over_chord_min": 2.099e-3, "zspread_over_chord_max": 3.953e-3},
          "L2": {"min_points": 7, "zspread_over_chord_min": 1.725e-3, "zspread_over_chord_max": 3.369e-3},
          "L1": {"min_points": 4, "zspread_over_chord_min": 1.797e-3, "zspread_over_chord_max": 3.285e-3}}
FIX_STRICT = {"L1": (34, 1284, 0.2306), "L2": (100, 8505, 0.1909), "L3": (159, 73232, 0.2055)}
FIX_NBLOCK = 101                                          # endTime 1000 at printInterval 10


def _history(mode, target, amp):
    """clean : a decaying excursion -- the last-window peak-to-peak is tiny.
    drift : A STEADY DRIFT WHOSE ADJACENT-SAMPLE DELTA IS SMALL AND WHOSE EXCURSION IS NOT.
            This is the shape an adjacent-delta test passes and a peak-to-peak test
            refuses -- the cfd DrivAer Gate A1 defect, reproduced here as a control.
    short : too few printed samples to judge."""
    if mode == "short":
        return [target + amp * 1e-6 * i for i in range(6)]
    if mode == "dead":
        # THE DEAD SOLVE (AMENDMENT 3).  Fifty printed steps -- iteration 490 of a registered
        # 1000 -- with a PERFECTLY FLAT tail, which is what a primal that is converging
        # normally looks like right up to the moment it is killed.  THE FLATNESS IS THE POINT:
        # the first attempt at this fixture used the decaying-oscillation "clean" history, and
        # G-PLAT caught it for an unrelated reason, which would have made a suite with NO
        # completion gate look like a suite with a working one.
        return [target] * 50
    if mode == "drift":
        # per-sample increment amp*2e-3; over the 11-sample window the EXCURSION is 10x
        # that, which FAILS the peak-to-peak gate, while the increment itself PASSES an
        # adjacent-delta test.  The two verdicts disagree BY CONSTRUCTION -- that is the
        # point of the control.  The drift ends AT the registered value.
        return [target - amp * 2.0e-3 * (FIX_NBLOCK - 1 - i) for i in range(FIX_NBLOCK)]
    return [target + amp * math.exp(-i / 10.0) * (1.0 if i % 2 == 0 else -1.0) for i in range(FIX_NBLOCK)]


def _armlog(so, terminal, tol, toldiff, maxres, cdh, clh, pi=10, end=True, nblocks=None):
    """`nblocks` DECOUPLES THE STEP COUNT FROM THE FUNCTIONAL-SAMPLE COUNT, and that
    separation is required by AMENDMENT 3.  Before it, the only way to build a
    too-few-samples fixture was to shorten the whole log -- which is now a COMPLETION
    failure, so G1 would refuse it and G-PLAT's want-of-evidence limb could never be
    reached.  A run CAN complete to endTime and still print too few `CD:` lines, and that
    degenerate case is precisely what G-PLAT's minimum window exists for.  Keeping the two
    fixtures independent is the same lesson as the near-miss: a control reached only
    because a DIFFERENT control let it through is not a control."""
    L = ["D4S_CONTAINER_UID: 0", "D4S_IDWARP_SO_MD5: %s" % so, "D4S_DEADLINE_IN_CONTAINER_S: 600",
         "    primalMinResTol %s;" % repr(tol), "    primalMinResTolDiff %s;" % repr(toldiff),
         "    printInterval   %d;" % pi, "Running Primal Solver 001", "", "Starting time loop"]
    small = repr(maxres / 5.0)
    nb = len(cdh) if nblocks is None else nblocks
    for i in range(nb):
        cd = cdh[i] if i < len(cdh) else None
        cl = clh[i] if i < len(clh) else None
        L += ["", "Time = %d" % (i * pi if i else 1), "",
              "U0 initRes: %s finalRes: 1e-09 nIters: 2" % small,
              "U1 initRes: %s finalRes: 1e-09 nIters: 2" % small,
              "U2 initRes: %s finalRes: 1e-09 nIters: 2" % small,
              "he initRes: %s finalRes: 1e-09 nIters: 2" % repr(maxres / 2.0),
              "p initRes: %s finalRes: 1e-09 nIters: 10" % repr(maxres),
              "nuTilda initRes: %s finalRes: 1e-09 nIters: 2" % small,
              ]
        if cd is not None:
            L += ["CD: %s final: %s" % (repr(cd), repr(cd)), "CL: %s final: %s" % (repr(cl), repr(cl))]
        L += ["ExecutionTime = %.2f s  ClockTime = %d s" % (2.5 + i * 0.3, 3 + i)]
    # A REAL DAFoam ARM LOG PRINTS `End` AFTER THE TIME LOOP.  MEASURED on D8R's graded
    # F-P arm: exactly one per primal segment (33 in a 32-primal log, the extra being
    # decomposePar's).  A fixture without it would make AMENDMENT 3's clause refuse every
    # correct arm, so the fixture is corrected to match the instrument it stands in for.
    if end:
        L += ["", "End", ""]
    if terminal:
        L.append(terminal + " ok")
    return "\n".join(L) + "\n"


def _fix(tmp, tweak=None):
    """Build a clean fixture; `tweak` mutates the dict of knobs before writing."""
    k = {"rc": {a: 0 for a in ARMS_REQUIRED}, "ke": {}, "oom": {a: "false" for a in ARMS_REQUIRED},
         "cm": dict(PREDICTED_CORE_MIN), "cs": {a: CPUSET_REGISTERED for a in ARMS_REQUIRED},
         "so": {a: SO_MD5[ARM_ROW[a]] for a in ARMS_REQUIRED},
         "points": {lv: ("points-%s-bytes" % lv).encode() for lv in LEVELS},
         "terminal": {a: True for a in ARMS_REQUIRED}, "stale": set(), "ctrl_ok": True, "mpost": "20.00",
         "drop_row": set(), "inspect_file": set(), "dl": "3.98 n=10 max_nr_throttled=0", "nprocs": 4,
         "cd": dict(FIX_CD), "cl": dict(FIX_CL), "hist": {a: "clean" for a in PRIMAL_ARMS},
         "toldiff": {a: PRIMAL_MIN_RES_TOL_DIFF for a in PRIMAL_ARMS},
         "maxres": {a: 5.0e-5 for a in PRIMAL_ARMS},
         "pi": {a: 10 for a in PRIMAL_ARMS}, "end": {a: True for a in ARMS_REQUIRED},
         "fields": {a: "ok" for a in ARMS_REQUIRED},
         "err": {"S": {}, "P": {}}, "flip": {"S": set(), "P": set()}, "nospread": {"S": set(), "P": set()},
         "trivial_scale": {"S": 1.30, "P": 1.30}, "adjoint_ok": {"S": True, "P": True},
         "mesh": {lv: {} for lv in LEVELS}}
    if tweak:
        tweak(k)
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6))
    os.makedirs(root)
    led = ["ITEM=D8G\n", "STAGED stamp=x\n"]
    # ---- the per-level mesh construction records (d8g_genmesh.sh writes these) -------
    for i, lv in enumerate(LEVELS):
        rec = {"level": lv, "cells": CELLS[lv], "surface_points": SURFACE_POINTS[lv],
               "surface_quad_faces": SURFACE_QUADS[lv],
               "patches": [{"name": n, "type": t, "nFaces": f} for n, t, f in PATCHES_REGISTERED[lv]],
               "geometric_directions": [3, 3], "solution_directions": [3, 3],
               "checkmesh_plain": "Mesh OK.", "checkmesh_plain_log": "checkMesh_%s.log" % lv,
               "checkmesh_strict_log": "checkMesh_strict_%s.log" % lv,
               "strict_failed_checks": list(STRICT_EXPECTED_CHECKS),
               "bad_face_tets": FIX_STRICT[lv][0], "small_det_cells": FIX_STRICT[lv][1],
               "small_det_fraction": FIX_STRICT[lv][2], "bbox": FIX_BBOX[lv], "te_bands": FIX_TE[lv],
               "points_md5": hashlib.md5(k["points"][lv]).hexdigest(),
               "surface_max_coord_delta_to_finer": (None if lv == "L3" else (7.1e-3 if lv == "L1" else 5.0e-3)),
               "image_digest": IMG_DIGEST["PATCHED"]}
        rec.update(k["mesh"][lv])
        json.dump(rec, open(os.path.join(root, "mesh_record_%s.json" % lv), "w"), indent=1, sort_keys=True)
    amd5 = {}
    for arm in ARMS_REQUIRED:
        lv, mode, rk = ARM_LEVEL[arm], ARM_MODE[arm], ("S" if arm.endswith("-S") else "P")
        d = os.path.join(root, arm)
        os.makedirs(os.path.join(d, "0"))
        os.makedirs(os.path.join(d, "constant", "polyMesh"))
        open(os.path.join(d, "constant", "polyMesh", "points.gz"), "wb").write(k["points"][lv])
        ref = os.path.join(d, DATUM_REF[arm])
        open(ref, "w").write("U\n")
        t0 = int(os.path.getmtime(ref))
        open(os.path.join(d, ".d8g_age_datum"), "w").write("%d\n" % t0)
        # THE FIELD SET EVERY RANK WRITES AT endTime (AMENDMENT 3).  MEASURED on D8R's graded
        # F-P arm: present, gzipped, in all four processor dirs at time 1000, every one newer
        # than the arm's own age datum.
        if k["fields"][arm] != "none":
            tdir = "%d" % int(ENDTIME_REGISTERED)
            for pn in range(NPROCS_REGISTERED):
                fd = os.path.join(d, "processor%d" % pn, tdir)
                os.makedirs(fd, exist_ok=True)
                for fld in FIELDS_AT_ENDTIME:
                    if k["fields"][arm] == "missing" and fld == "phi" and pn == 2:
                        continue
                    fp = os.path.join(fd, fld + ".gz")
                    open(fp, "w").write("field\n")
                    os.utime(fp, (t0 - 5, t0 - 5) if k["fields"][arm] == "stale" else (t0 + 5, t0 + 5))
        log = "%s_x.log" % arm
        so = k["so"][arm]
        ident = {"libidwarp_so_md5": so, "idwarp_file": "/x/idwarp/__init__.py"}
        art = os.path.join(d, ARTEFACT[arm])
        pmd5 = hashlib.md5(k["points"][lv]).hexdigest()
        if mode == "P":
            pi = k["pi"][arm]
            # THE BLOCK COUNT FOLLOWS THE CADENCE, DERIVED THE SAME WAY THE GATE DERIVES IT.
            # A fixture with a hard-coded 101 could not exercise the derivation at all.
            nb = expected_printed_steps(ENDTIME_REGISTERED, DELTAT_REGISTERED, pi)
            cdh = _history(k["hist"][arm], k["cd"][lv], 0.01)
            clh = _history(k["hist"][arm], k["cl"][lv], 0.10)
            if k["hist"][arm] == "clean" and nb != FIX_NBLOCK:
                cdh, clh = cdh[:1] * nb, clh[:1] * nb
            # A DEAD arm is TRUNCATED -- its step count is its sample count.  Every other
            # mode runs the full registered length and varies only what it PRINTS.
            nbl = len(cdh) if k["hist"][arm] == "dead" else nb
            text = _armlog(so, (TERMINAL[arm] if k["terminal"][arm] else None), PRIMAL_MIN_RES_TOL,
                           k["toldiff"][arm], k["maxres"][arm], cdh, clh, pi=pi, end=k["end"][arm],
                           nblocks=nbl)
            json.dump({"item": "D8G", "mode": "P", "level": lv, "cells": CELLS[lv], "nprocs": k["nprocs"],
                       "identity": ident, "points_md5": pmd5, "endTime": 1000,
                       "CD": repr(k["cd"][lv]), "CL": repr(k["cl"][lv])}, open(art, "w"))
        elif mode == "A":
            text = _armlog(so, (TERMINAL[arm] if k["terminal"][arm] else None), PRIMAL_MIN_RES_TOL,
                           PRIMAL_MIN_RES_TOL_DIFF, 5.0e-5, [k["cd"][lv]] * FIX_NBLOCK,
                           [k["cl"][lv]] * FIX_NBLOCK, end=k["end"][arm])
            adj = {"CD": {dv: [repr(v) for v in FIX_J[dv]] for dv in FIX_J},
                   "CL": {dv: [repr(v * 10.0) for v in FIX_J[dv]] for dv in FIX_J}}
            json.dump({"item": "D8G", "mode": "A", "level": lv, "nprocs": k["nprocs"], "identity": ident,
                       "points_md5": pmd5, "CD_baseline": repr(k["cd"][lv]), "CL_baseline": repr(k["cl"][lv]),
                       "adjoint": adj}, open(art, "w"))
            amd5[rk] = None                                # filled after the file is written
        else:
            text = _armlog(so, (TERMINAL[arm] if k["terminal"][arm] else None), PRIMAL_MIN_RES_TOL,
                           PRIMAL_MIN_RES_TOL_DIFF, 5.0e-5, [k["cd"][lv]] * FIX_NBLOCK,
                           [k["cl"][lv]] * FIX_NBLOCK, end=k["end"][arm])
            rows_ = []
            for dv, idx in COMPONENTS_REGISTERED:
                j = FIX_J[dv][idx]
                e = k["err"][rk].get((dv, idx), 0.5)       # default 0.5 % error
                dref = j * (1.0 + e / 100.0)
                if (dv, idx) in k["flip"][rk]:
                    dref = -dref
                fd = {}
                mid = sorted(STEPS_REGISTERED[dv])[1]
                for s in STEPS_REGISTERED[dv]:
                    scale = 1.0 if s == mid else 1.01
                    if (dv, idx) in k["nospread"][rk]:
                        scale = 1.0 if s == mid else 1.5   # 50 % spread: NO PLATEAU ANYWHERE
                    fd[repr(s)] = {"step": s, "ok": True, "dCD": repr(dref * scale), "dCL": repr(dref * 10.0 * scale)}
                ts = k["trivial_scale"][rk]
                fd[repr(TRIVIAL_STEP)] = {"step": TRIVIAL_STEP, "ok": True,
                                          "dCD": repr(dref * ts), "dCL": repr(dref * 10.0 * ts)}
                rows_.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
            planted = PLANT / (2.0 * CTRL_STEP) if k["ctrl_ok"] else 0.0
            rows_.append({"dv": "CTRL", "idx": 0, "status": "CONTROL",
                          "fd": {repr(CTRL_STEP): {"step": CTRL_STEP, "ok": True, "dCD": repr(0.0), "dCL": repr(0.0)}},
                          "planted": {"step": CTRL_STEP, "plant": PLANT, "dCD": repr(planted), "ok": True}})
            json.dump({"item": "D8G", "mode": "F", "level": lv, "nprocs": k["nprocs"], "identity": ident,
                       "components_requested": COMPONENTS_REGISTERED, "steps": STEPS_REGISTERED["twist"],
                       "trivial_step": TRIVIAL_STEP,
                       "adjoint_source": {"md5": ("PLACEHOLDER_%s" % rk if k["adjoint_ok"][rk] else "0" * 32)},
                       "CD_baseline": repr(k["cd"][lv]), "CL_baseline": repr(k["cl"][lv]),
                       "eta_used": repr(1.08e-5), "rows": rows_}, open(art, "w"))
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        open(os.path.join(root, log), "w").write(text)
        ke = k["ke"].get(arm, k["rc"][arm])
        if arm in k["inspect_file"]:
            open(os.path.join(root, "%s_x.inspect.txt" % arm), "w").write(
                "%d %s 2026-09-11T00:00:00Z 2026-09-11T00:01:00Z %s 15032385536 %s\n"
                % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[ARM_ROW[arm]]))
        if arm in k["drop_row"]:
            continue
        led.append(ROWFMT.format(arm=arm, row=ARM_ROW[arm], img="img", dig=IMG_DIGEST[ARM_ROW[arm]], rc=k["rc"][arm],
                                 wall=60, ranks=ARM_RANKS[arm], cm=k["cm"][arm], cap=CAPS[arm], ke=ke, oom=k["oom"][arm],
                                 mpost=k["mpost"], cs=k["cs"][arm], dl=k["dl"], log=log))
    # ---- the F arm's adjoint_source md5 must be THIS ROW's A artefact ---------------
    for rk, aarm, farm in (("S", "A2-S", "F2-S"), ("P", "A2-P", "F2-P")):
        real = md5_of(os.path.join(root, aarm, "d8g_A.json"))
        fp = os.path.join(root, farm, "d8g_F.json")
        st = os.stat(fp)
        j = json.load(open(fp))
        if j["adjoint_source"]["md5"].startswith("PLACEHOLDER"):
            j["adjoint_source"]["md5"] = real
            json.dump(j, open(fp, "w"))
            os.utime(fp, (st.st_atime, st.st_mtime))
    open(os.path.join(root, "ledger.txt"), "w").write("".join(led))
    return root


def selftest(tmp):
    n = 0; fails = []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    def refused(root):
        try:
            grade(root); return False
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

    # ================= the clean fixture ==============================================
    r = grade(_fix(tmp))
    # POSITIVE EVIDENCE FOR U50: a gate that merely fails to refuse has not been shown to have
    # READ anything.  This captures what G1-RUN actually measured on a correct arm.
    _clean_run_completion = r["completion"]["run_completion"]["L2-P"]
    unit("U1 clean fixture -> item PASS, both rows PASS, G-MESH/G-MESH-STRICT/G-SYS/G-BODY/G-TE/G-M2/G9/G12 PASS",
         r["verdict"] == "PASS" and r["rows"] == {"SHIPPED": "PASS", "PATCHED": "PASS"}
         and r["gates"]["G-MESH"]["verdict"] == "PASS" and r["gates"]["G-MESH-STRICT"]["verdict"] == "PASS"
         and r["gates"]["G-SYS"]["verdict"] == "PASS" and r["gates"]["G-BODY"]["verdict"] == "PASS"
         and r["gates"]["G-TE"]["verdict"] == "PASS" and r["gates"]["G-M2_mesh_identity_per_level"]["verdict"] == "PASS"
         and r["gates"]["G9_toolchain"]["verdict"] == "PASS" and r["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("U2 clean fixture -> P1 P2 P3 P5 HIT; P4 MISS (the shipped row is clean by construction)",
         all(r["predictions"][kk] == "HIT" for kk in ("P1_construction_reproduced", "P2_systematicity",
                                                      "P3_CD_triple_CONVERGING_in_band", "P5_rows_agree_to_1_eta"))
         and r["predictions"]["P4_shipped_FD_FAIL_patched_PASS"] == "MISS")
    t = r["gates"]["PATCHED"]["G-TRIPLE"]
    unit("U3 G-TRIPLE: CD and CL both CONVERGING at observed order 2.000 in the band [1.0, 3.0], GCI printed",
         t["states_both"] == {"CD": "CONVERGING", "CL": "CONVERGING"}
         and abs(t["orders_both"]["CD"] - 2.0) < 1e-9 and abs(t["orders_both"]["CL"] - 2.0) < 1e-9
         and t["per_functional"]["CD"]["GCI_pct"] is not None and t["verdict"] == "PASS")
    c = r["controls"]
    unit("U4 ALL FOUR PLANTED CONTROLS through the real path: functional plant SEEN, residual must-see SEEN, "
         "finalRes ANTI-PLANT correctly NOT seen, CTRL zero 0.0, grader plant SEEN",
         c["functional_plant_P"]["functional_plant_seen"] and abs(c["functional_plant_P"]["read_back"] - CD_PLANT) < 1e-12
         and abs(c["residual_plant_P"]["residual_must_see"] - RES_PLANT) < 1e-12
         and c["residual_plant_P"]["anti_plant_correctly_not_seen"]
         and abs(c["residual_plant_P"]["residual_anti_plant_read"] - RES_PLANT) > 1e-12
         and c["ctrl_P"]["instrument_ctrl_zero"] == 0.0 and c["grader_plant_P"]["grader_plant_seen"])
    unit("U5 the FD sweep table prints EVERY step as a row, including the 1e-3 trivial baseline control",
         len(r["gates"]["PATCHED"]["G-FD_CD"]["sweep_table"]) == 4
         and any(abs(x["step_deg"] - TRIVIAL_STEP) < 1e-15 and "TRIVIAL BASELINE" in x["status"]
                 for x in r["gates"]["PATCHED"]["G-FD_CD"]["sweep_table"]))
    unit("U6 G-PRIMAL reports the 1e-6 tutorial floor as a DIAGNOSTIC and grades against the 1e-4 PRODUCT",
         r["gates"]["PATCHED"]["G-PRIMAL"]["L2"]["verdict"] == "PASS"
         and r["gates"]["PATCHED"]["G-PRIMAL"]["L2"]["diagnostic_vs_1e-6_tutorial_floor"]["meets_tighter_floor"] is False
         and r["gates"]["PATCHED"]["G-PRIMAL"]["L2"]["accept_floor_is_the_PRODUCT"] == 1.0e-4
         and r["gates"]["PATCHED"]["G-PRIMAL"]["L2"]["finalRes_read"] is False)
    unit("U7 the trivial baseline at 1e-3 is PREDICTED > 15 % and the clean fixture HITS it (verdict NOT withdrawn)",
         r["gates"]["PATCHED"]["G-FD_CD"]["trivial_baseline"]["prediction"] == "HIT"
         and r["gates"]["PATCHED"]["G-FD_CD"]["trivial_baseline"]["also_passed"] is False
         and "withdrawn_verdict" not in r["gates"]["PATCHED"]["G-FD_CD"])

    # ================= MUTATION CONTROLS: the suite must be SEEN TO FAIL =============
    r = grade(_fix(tmp, tw(hist={"L2-P": "drift"})))
    pl = r["gates"]["PATCHED"]["G-PLAT"]["per_functional"]["CD"]["levels"]["L2"]
    unit("U8 MUTATION drifting CD history on L2-P: G-PLAT REFUSES on peak-to-peak WHILE AN ADJACENT-DELTA "
         "TEST WOULD HAVE PASSED -- the DrivAer Gate A1 defect, reproduced and caught",
         pl["verdict"] == "NOT A RESULT" and pl["would_an_adjacent_delta_test_have_passed"] is True
         and pl["statistic"] == "PEAK_TO_PEAK_max_minus_min")
    unit("U9 the same drift makes the PATCHED row and the item NOT A RESULT, and G-TRIPLE returns NOT A RESULT "
         "by clause 1 naming L2 (rule 5: the gate can only turn a verdict INTO NOT A RESULT)",
         r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT"
         and r["gates"]["PATCHED"]["G-TRIPLE"]["verdict"] == "NOT A RESULT"
         and "L2" in r["gates"]["PATCHED"]["G-TRIPLE"]["reason"])
    unit("U10 MUTATION primalMinResTolDiff 100 in L3-S's own log (A6's OTHER registered value) -> REFUSAL, "
         "not a soft note", refused(_fix(tmp, tw(toldiff={"L3-S": 100.0}))))
    r = grade(_fix(tmp, tw(trivial_scale={"P": 1.005})))
    fd = r["gates"]["PATCHED"]["G-FD_CD"]
    unit("U11 MUTATION the deliberately-wrong 1e-3 step ALSO PASSES -> THE FD VERDICT IS WITHDRAWN: verdict "
         "NOT A RESULT, the withdrawn verdict recorded, the row NOT A RESULT",
         fd["trivial_baseline"]["also_passed"] is True and fd["verdict"] == "NOT A RESULT"
         and fd.get("withdrawn_verdict") == "PASS" and r["rows"]["PATCHED"] == "NOT A RESULT"
         and r["verdict"] == "NOT A RESULT")
    r = grade(_fix(tmp, tw(flip={"S": {("twist", 5)}})))
    fd = r["gates"]["SHIPPED"]["G-FD_CD"]
    unit("U12 MUTATION sign-flipped twist[5] with a SMALL aggregate (<= 5 %) -> band FAIL ANYWAY, verdict "
         "GATE FAIL, the flipped component named, row and item GATE FAIL",
         fd["aggregate_rel_err_pct"] <= FD_PASS_PCT and fd["band"] == "FAIL"
         and fd["sign_flipped_BY_NAME"] == ["twist[5]"] and fd["verdict"] == "GATE FAIL"
         and r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(hist={"L1-S": "short"})))
    pl = r["gates"]["SHIPPED"]["G-PLAT"]["per_functional"]["CD"]["levels"]["L1"]
    unit("U13 a history of 6 printed samples -> window < 10 -> that level NOT A RESULT FOR WANT OF EVIDENCE",
         pl["verdict"] == "NOT A RESULT" and pl["window"]["n_window"] < PLAT_MIN_SAMPLES
         and r["rows"]["SHIPPED"] == "NOT A RESULT")
    r = grade(_fix(tmp, tw(maxres={"L3-P": 2.0e-4})))
    unit("U14 max-initRes 2e-4 > the 1e-4 accept floor on L3-P -> that level NOT A RESULT and the whole triple "
         "with it (rule 5 clause 1)",
         r["gates"]["PATCHED"]["G-PRIMAL"]["L3"]["verdict"] == "NOT A RESULT"
         and r["gates"]["PATCHED"]["G-TRIPLE"]["verdict"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")

    # ================= G-FD bands, flagged components, and the >= 3 rule =============
    r = grade(_fix(tmp, tw(nospread={"S": {("twist", 1)}})))
    fd = r["gates"]["SHIPPED"]["G-FD_CD"]
    unit("U15 a component that stabilises NOWHERE is FLAGGED AND EXCLUDED BY NAME, never dropped silently: "
         "band CONDITIONAL_FLAGGED, verdict GATE FAIL, 4 graded",
         fd["flagged_components_BY_NAME"] == ["twist[1]"] and fd["n_graded"] == 4
         and fd["band"] == "CONDITIONAL_FLAGGED" and fd["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(nospread={"P": {("twist", 0), ("twist", 3), ("twist", 5)}})))
    unit("U16 three flagged components -> 2 graded < 3 -> G-FD NOT A RESULT -> row and item NOT A RESULT",
         r["gates"]["PATCHED"]["G-FD_CD"]["verdict"] == "NOT A RESULT"
         and r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
    r = grade(_fix(tmp, tw(err={"S": {("twist", 0): 40.0}})))
    fd = r["gates"]["SHIPPED"]["G-FD_CD"]
    unit("U17 a 40 % error on shipped twist[0] -> aggregate > 15 % -> band FAIL, row GATE FAIL, item GATE FAIL, "
         "P4 HIT", fd["aggregate_rel_err_pct"] > FD_CONDITIONAL_PCT and fd["band"] == "FAIL"
         and r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL"
         and r["predictions"]["P4_shipped_FD_FAIL_patched_PASS"] == "HIT")
    r = grade(_fix(tmp, tw(err={"S": {("twist", 0): 10.0}})))
    fd = r["gates"]["SHIPPED"]["G-FD_CD"]
    unit("U18 a 10 % error on shipped twist[0] -> aggregate in (5, 15] % -> band CONDITIONAL with the "
         "per-component breakdown printed; the VERDICT TOKEN is GATE FAIL (CONDITIONAL is not in the vocabulary)",
         FD_PASS_PCT < fd["aggregate_rel_err_pct"] <= FD_CONDITIONAL_PCT and fd["band"] == "CONDITIONAL"
         and fd["verdict"] == "GATE FAIL" and fd["verdict"] in VOCAB and len(fd["components"]) == 5)

    # ================= the mesh family ===============================================
    r = grade(_fix(tmp, tw(mesh={"L2": {"cells": 44545}})))
    unit("U19 L2 cell count 44,545 != the registered 44,544 -> G-MESH GATE FAIL, item GATE FAIL",
         r["gates"]["G-MESH"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(mesh={"L1": {"geometric_directions": [3, 2]}})))
    unit("U20 `Mesh has 2 geometric (non-empty/wedge) directions` on ONE occurrence at L1 -> dimensionality "
         "clause fails -> item NOT A RESULT (a wedge reads 3 on the SOLUTION line, which is why the "
         "GEOMETRIC line is the authority)",
         r["gates"]["G-MESH"]["dimensionality_failed"] == ["L1"] and r["verdict"] == "NOT A RESULT")
    r = grade(_fix(tmp, tw(mesh={"L3": {"strict_failed_checks": list(STRICT_EXPECTED_CHECKS) + ["aspect ratio"]}})))
    unit("U21 a THIRD failing strict check at L3 -> G-MESH-STRICT GATE FAIL, the checks enumerated BY NAME",
         r["gates"]["G-MESH-STRICT"]["verdict"] == "GATE FAIL"
         and "aspect ratio" in r["gates"]["G-MESH-STRICT"]["per_level"]["L3"]["strict_failed_checks_by_name"])
    r = grade(_fix(tmp, tw(mesh={"L1": {"small_det_fraction": 0.30}})))
    unit("U22 small-determinant fraction 0.30 outside the registered band [0.15, 0.28] -> G-MESH-STRICT GATE FAIL",
         r["gates"]["G-MESH-STRICT"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(mesh={"L3": {"cells": 89088}})))
    unit("U23 cell ratio 2 instead of the exact integer 8 -> G-SYS GATE FAIL (the discriminator A3's family "
         "fails: a family refining ONE direction)",
         r["gates"]["G-SYS"]["verdict"] == "GATE FAIL"
         and r["gates"]["G-SYS"]["cell_ratios_are_the_exact_integers"] is False)
    r = grade(_fix(tmp, tw(mesh={"L2": {"surface_max_coord_delta_to_finer": 0.0}})))
    unit("U24 L2 and L3 surfaces identical in COORDINATES (delta 0) -> G-SYS GATE FAIL; md5 is NOT the "
         "instrument here because CGNS bytes are not reproducible",
         r["gates"]["G-SYS"]["surfaces_pairwise_distinct_in_coordinates"] is False
         and r["gates"]["G-SYS"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(mesh={"L3": {"bbox": {"x": [-0.0000, 3.2484], "y": [0.0000, 3.7667],
                                                 "z": [-0.2029, 0.3461]}}})))
    unit("U25 L3<->L2 bounding-box delta 1.0e-3 > the 1.0e-4 tolerance -> G-BODY GATE FAIL (the family must "
         "refine the discretisation, not change the body)",
         r["gates"]["G-BODY"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(mesh={"L1": {"te_bands": {"min_points": 3, "zspread_over_chord_min": 1.797e-3,
                                                     "zspread_over_chord_max": 3.285e-3}}})))
    unit("U26 3 TE points in a band at L1 (< 4) -> G-TE NOT A RESULT, item NOT A RESULT -- a level that closes "
         "the TE where a finer level does not is NOT THE SAME BODY and KILLS THE TRIPLE",
         r["gates"]["G-TE"]["verdict"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")

    # ================= completion, identity, placement, caps (INHERITED FROM D8R) =====
    unit("U27 rc=1 on L2-P -> REFUSAL", refused(_fix(tmp, tw(rc={"L2-P": 1}, ke={"L2-P": 1}))))
    unit("U28 OOMKilled=true on F2-S -> REFUSAL (hard)", refused(_fix(tmp, tw(oom={"F2-S": "true"}))))
    unit("U29 terminal marker absent in A2-P's log -> REFUSAL", refused(_fix(tmp, tw(terminal={"A2-P": False}))))
    unit("U30 artefact OLDER than the age datum (L3-S) -> REFUSAL (rule 4)", refused(_fix(tmp, tw(stale={"L3-S"}))))
    unit("U31 instrument CTRL planted row broken -> REFUSAL (a reader not shown able to see a non-zero)",
         refused(_fix(tmp, tw(ctrl_ok=False))))
    unit("U32 F arm whose adjoint_source md5 is not this row's A artefact -> REFUSAL",
         refused(_fix(tmp, tw(adjoint_ok={"S": False}))))
    unit("U33 nprocs 1 in an artefact (registered 4) -> REFUSAL", refused(_fix(tmp, tw(nprocs=1))))
    unit("U34 harness rc 0 vs kernel exit 1 disagreement -> REFUSAL", refused(_fix(tmp, tw(ke={"F2-P": 1}))))
    unit("U35 ledger row absent and no inspect record -> REFUSAL", refused(_fix(tmp, tw(drop_row={"F2-P"}))))
    r = grade(_fix(tmp, tw(drop_row={"F2-P"}, inspect_file={"F2-P"})))
    unit("U36 ledger row absent, ONE inspect record -> read from it, the source named, core_min NOT_MEASURED, "
         "verdict PASS (L-342)",
         r["verdict"] == "PASS" and r["completion"]["arms"]["F2-P"]["source"] == "inspect_record"
         and "F2-P" in r["not_measured"]["G10"])
    r = grade(_fix(tmp, tw(so={"L2-P": SO_MD5["SHIPPED"]})))
    unit("U37 L2-P carrying the SHIPPED .so md5 -> G9 GATE FAIL, item GATE FAIL",
         r["gates"]["G9_toolchain"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cs={"L3-S": "8,10,11,13"})))
    unit("U38 L3-S on a different cpuset -> G12 GATE FAIL (placement is not constant across the family)",
         r["gates"]["G12_placement"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cm={"L3-P": 4.0 * CAPS["L3-P"]})))
    unit("U39 L3-P at 4x its cap -> REPORTED WITH ITS RATIO AND THE ITEM IS STILL PASS: section 6.4 suspends "
         "the stop for this 3D item, and the estimate-vs-actual ratio is still emitted (rule 12)",
         r["gates"]["G10_caps_REPORT_ONLY"]["crossings_reported"] == ["L3-P"]
         and r["gates"]["G10_caps_REPORT_ONLY"]["verdict"] == "PASS" and r["verdict"] == "PASS"
         and r["gates"]["G10_caps_REPORT_ONLY"]["per_arm"]["L3-P"]["ratio_actual_over_predicted"] > 1.0)
    r = grade(_fix(tmp, tw(mesh={"L2": {"points_md5": "0" * 32}})))
    unit("U40 the L2 arms' points.gz does not hash to the L2 mesh record's registered points_md5 -> G-M2 "
         "GATE FAIL (an arm that ran a mesh other than its level's)",
         r["gates"]["G-M2_mesh_identity_per_level"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(mpost="NOT_MEASURED", dl="NOT_MEASURED")))
    unit("U41 absent infrastructure fields -> verdict unchanged PASS, NOT_MEASURED named beside it (L-342)",
         r["verdict"] == "PASS" and r["not_measured"]["G1"].get("L3-S") and "L3-S" in r["not_measured"]["G12"])
    here = os.path.dirname(os.path.abspath(__file__))
    unit("U42 ast.Assert count = 0 in this comparator (L-332)", count_asserts(os.path.abspath(__file__)) == 0)
    p = os.path.join(tmp, "planted_assert.py")
    open(p, "w").write("x = 1\nassert x == 1\n")
    unit("U43 the assert counter is shown able to COUNT a planted assert (=1)", count_asserts(p) == 1)

    # ================= AMENDMENT 3: G1-RUN, THE COMPLETION CLAUSE ====================
    # U44 IS THE DEMONSTRATION THAT FORCED THE AMENDMENT, TURNED INTO A REGRESSION TEST.
    # Before the clause this exact fixture came out G1 PASS / G-PRIMAL PASS / G-PLAT PASS at
    # peak-to-peak 0.0 / G-TRIPLE CONVERGING at order 2.0000, GCI 0.5556 %, ITEM PASS on both
    # rows -- a comparator certifying a corpse at order 2.0000, where every number in the
    # chain looks like success.
    unit("U44 THE DEAD SOLVE: a primal truncated at iteration 490 of a registered 1000, with a "
         "PERFECTLY FLAT tail and its artefact still claiming endTime 1000, is REFUSED by G1 "
         "-- it graded PASS on both rows before AMENDMENT 3",
         refused(_fix(tmp, tw(hist={"L2-P": "dead"}))))
    # U45 IS THE NEAR-MISS, MADE INTO A MEASUREMENT.  The first attempt at U44's demonstration
    # truncated the DECAYING-OSCILLATION history, and G-PLAT caught it -- for a reason that has
    # nothing to do with completion.  A suite built on that fixture would have shown a green
    # completion story while having NO completion gate at all.  The two truncations are NOT
    # equivalent and this unit measures the difference: a FLAT tail is INVISIBLE to G-PLAT, so
    # only G1 can catch it.  A CONTROL REACHED ONLY BECAUSE A DIFFERENT CONTROL LET IT THROUGH
    # IS NOT A CONTROL.
    _dref = min(abs(FIX_CD["L1"] - FIX_CD["L2"]), abs(FIX_CD["L2"] - FIX_CD["L3"]))
    _flat = plateau_statistic(plateau_window([FIX_CD["L2"]] * 50))["peak_to_peak"]
    _osc = plateau_statistic(plateau_window(_history("clean", FIX_CD["L2"], 0.01)[:50]))["peak_to_peak"]
    unit("U45 a FLAT truncated tail is INVISIBLE to G-PLAT (peak-to-peak 0.0, clears DELTA_REF/%g) "
         "while a DECAYING-OSCILLATION truncation is not -- so U44's fixture reaches G1 and the "
         "first attempt at it never did.  The near-miss, measured rather than recalled"
         % PLAT_FACTOR,
         _flat == 0.0 and _flat * PLAT_FACTOR <= _dref and _osc * PLAT_FACTOR > _dref)
    unit("U46 a log that completed to endTime but carries NO `End` line is REFUSED (rule 4)",
         refused(_fix(tmp, tw(end={"L3-P": False}))))
    unit("U47 a log whose printInterval read-back is not the registered cadence is REFUSED -- "
         "the expected step count is DERIVED from it, so an unread cadence would make the "
         "derivation describe a different run",
         refused(_fix(tmp, tw(pi={"L1-P": 100}))))
    unit("U48 the field set at endTime absent from ANY rank is REFUSED (rule 4: PHYSICS absent)",
         refused(_fix(tmp, tw(fields={"L2-S": "missing"}))))
    unit("U49 fields present at endTime but NOT NEWER than the arm's own age datum are REFUSED "
         "-- 0/U is touched last at stage time, so a field older than it did not come from "
         "this run", refused(_fix(tmp, tw(fields={"L1-S": "stale"}))))
    # U50 IS THE ANTI-HARD-CODING UNIT THE AMENDMENT DEMANDS.  A literal 101 would pass every
    # test above and be silently wrong the moment endTime, deltaT or printInterval moved.
    unit("U50 the expected step count is DERIVED, not the literal 101: the formula returns 101 / "
         "51 / 1000 / 11 at printInterval 10 / 20 / 1 / 100, and the clean fixture's own gate "
         "reports the value the formula gives for the cadence it read back",
         expected_printed_steps(1000.0, 1.0, 10) == 101
         and expected_printed_steps(1000.0, 1.0, 20) == 51
         # 1000, NOT 1001.  At printInterval 1 the printed set is {1} u {1,2,...,1000}, whose
         # SIZE IS 1000 -- iteration 1 is in both halves.  The first draft of this unit
         # asserted 1001 and was WRONG: it fell for exactly the double-count the set-based
         # formula exists to prevent.  The formula was right and the test was wrong, which is
         # the direction that only gets caught by driving the function rather than trusting it.
         and expected_printed_steps(1000.0, 1.0, 1) == 1000
         and expected_printed_steps(1000.0, 1.0, 100) == 11
         and _clean_run_completion["expected_printed_steps_DERIVED"]
         == expected_printed_steps(ENDTIME_REGISTERED, DELTAT_REGISTERED,
                                   _clean_run_completion["printInterval_read_back"])
         and _clean_run_completion["n_ExecutionTime"] == 101
         and float(_clean_run_completion["last_time"]) == ENDTIME_REGISTERED
         and _clean_run_completion["n_End"] == 1)

    print("D8G GRADER SELFTEST units=%d expected=%d failures=%d python_O=%s" % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("D8G GRADER SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if count_asserts(os.path.abspath(__file__)) != 0:
        print("REFUSAL: this comparator carries an assert statement (L-332)"); return 2
    if a.selftest:
        d = os.path.join(a.tmpdir, "d8g_selftest_%d" % os.getpid()); os.makedirs(d, exist_ok=True)
        return selftest(d)
    if not a.root:
        print("usage: d8g_grade.py --root <run root> [--out FILE] | --selftest"); return 64
    try:
        r = grade(a.root)
    except Refusal as e:
        print("REFUSAL: %s -> NOT A RESULT" % e)
        if a.out:
            json.dump({"item": "CURRICULUM-%s" % ITEM, "verdict": "NOT A RESULT", "refusal": str(e)}, open(a.out, "w"), indent=1)
        return 2
    print(json.dumps(r, indent=1, default=str))
    if a.out:
        json.dump(r, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
