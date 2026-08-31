#!/usr/bin/env python3
"""F28 -- THE PLANTED-DELTA_P CONTROL COMPARATOR AND THE EMPTY-DUCT PASS-THROUGH.

Registration: verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md
FROZEN at 76ce0ed5.  Sections 6.2 (C1-C4, including the NEGATIVE LIMB) and 6.3.

>>> THIS FILE HAS NOT BEEN RUN FOR RECORD.  Stage 1 onward is gated behind the
>>> supervisor's SUPERVISION_CHARTER section 3 check 1 -- the measurement code is
>>> read AS A DIFF before any number out of it is believed.  Nothing below has
>>> produced a number.

-------------------------------------------------------------------------------
WHAT THIS COMPARATOR IS, AND WHAT IT IS NOT
-------------------------------------------------------------------------------
Section 6.1: "It is NOT a hand-computed check.  The control is a FULL L1
simpleFoam solve through the REAL `fvOptions` path, with the REAL
`vectorSemiImplicitSource`, read back by the REAL function objects and the REAL
comparator that will grade the gated runs.  Nothing about it is a special code
path."

Sanaa's control-birth directive, 2026-08-28, verbatim: "A control defined in
terms of the thing it controls is not a control.  A planted control must travel
the real production path -- written by the real producer's code, read through
the real reader -- and prove the instrument sees a non-zero the same way reality
would deliver one."

So the plant here is NOT injected into a Python variable.  It WRITES A KNOWN
PERTURBATION INTO A FILE ON DISK, in the case's own format, and the SAME reader
the gated number comes through reads it back off the disk.  If the reader cannot
see it, THE COMPARATOR REFUSES (exit 2) and no gated solve is launched.  A zero
from a reader not shown able to see a non-zero is not evidence (CLAUDE.md rule 3).

-------------------------------------------------------------------------------
REPAIR CANDIDATE -- WHAT THIS FILE CHANGES AND WHY, ver. R2
-------------------------------------------------------------------------------
This is a CANDIDATE repair of `analyse_f28.py` (763 lines, md5
f217d293762b0a644a95f32fb63b850f), written after TWO independent
SUPERVISION_CHARTER section 3 check-1 reads that both refused to open Stage 1:
`cases/F28_DUCTED_ACTUATOR_DISK/CHECK1_ANALYSE_F28.md` (cfd, ea6f9992) and
`verification/credibility/CHECK1_ANALYSE_F28_VERIFICATION.md` (3fb0d0a3).

>>> NOTHING BELOW HAS PRODUCED A NUMBER.  Stage 1 REMAINS unauthorised, and this
>>> candidate does not open it.  It replaces nothing until the supervisor has
>>> read it AS A DIFF against the file above.

THE DEFECT THE WHOLE REPAIR TURNS ON.  The superseded file planted into
`read_volScalarField` -- and `read_volScalarField`'s VALUE reaches ZERO graded
numbers.  Every one of the six graded quantities arrives through a reader that
had NO planted control: C1's `delta_p`, C2's `mdot`, C4 and section 6.3's
`T_total` through `function_object_series`, and C3 arm (b) through
`read_fvoptions_source` + `cell_volumes`.  Rule 3 was satisfied in FORM and
defeated in SUBSTANCE.  Every one of those readers now carries its own planted
control, with a POSITIVE and a NEGATIVE limb, through the real production path.

THE MEASURED DEFECTS THIS REPAIR CLOSES.  Each was verified at the superseded
file's own line numbers before a line was written; two were found by measurement
during the repair and are on NEITHER check-1 list.

 (1) rule 3 -- the plant certified a reader that grades nothing (above).
 (2) rule 4 clause 6 -- the age guard reached `FIELDS_REQUIRED` inside the time
     directory and NEVER reached `postProcessing/`, which is where every graded
     number lives.  The only time check on graded data compared the two disk
     planes TO EACH OTHER, so two equally stale files from a previous run passed
     it.  The age guard now fires on every function-object file read, and every
     graded row's `Time` is checked against `endTime`.
 (3) THE GRADER REWROTE THE ARTIFACT IT GRADES.  MEASURED, not argued: run on a
     real F28 `p` field (410,646 bytes), the superseded `plant_into_p` reported
     `fired: True, unperturbed_twin_silent: True` -- a fully successful control
     -- and left the file 409,911 bytes, having DELETED THE ENTIRE `FoamFile`
     HEADER BLOCK.  `_body()` truncates at the header separator and
     `write_volScalarField_values` wrote that truncated text back, so a
     SUCCESSFUL control silently destroyed the artifact's identity as an
     OpenFOAM field file, and nothing downstream noticed because this
     comparator's own reader only needs the separator.  Planting is now a
     ONE-TOKEN SPLICE into the full file text, the artifact is snapshotted and
     restored BYTE-EXACTLY with its original mtime, and the sha256 is verified
     equal afterwards -- refusing if it is not.
 (4) TWO REGISTERED GUARDS WITH ZERO CALL SITES.  `guard_virgin_case` now has a
     call site (`--guard-virgin`, for the launcher; see below).
     `read_volVectorField` is STRUCK: it had never executed, nothing graded
     needs it, and a reader never shown able to see a non-zero must not sit in a
     comparator waiting to be trusted.
 (5) NON-DETERMINISTIC ROW SELECTION.  `os.listdir` in arbitrary order with a
     `>=` tie-break, and `row.get("Time", 0)` silently defaulting a missing Time
     column to 0.  Now: sorted iteration, STRICT `>`, REFUSAL on a missing
     `Time` column, and REFUSAL on an ambiguous tie instead of a coin flip.
 (6) `%.12g` SAFE ONLY BY ACCIDENT.  `writeFormat ascii` is now ASSERTED with a
     refusal that says why.  `writePrecision` is RECORDED AND NOT GATED, and the
     reason is stated honestly in `assert_write_format`: under the splice fix of
     (3) nothing is re-rendered through a `%g` format at any point, so the
     precision is no longer load-bearing.  It was load-bearing, and unasserted,
     in the superseded file.
 (7) FOUND BY MEASUREMENT, ON NEITHER CHECK-1 LIST -- THE COMPARATOR READ A
     MOMENT AND CALLED IT A FORCE.  A `forces` function object writes BOTH
     `force.dat` AND `moment.dat` into the SAME directory with IDENTICAL column
     names (`Time total_x total_y total_z pressure_x ... viscous_x ...`) and
     IDENTICAL `Time` values.  `function_object_series` iterated every file in
     the directory and broke the tie with `>=`, so the LAST-VISITED file won.
     Measured on `verification/runs/F28_runs/FEAS_L1_dp1000_U20_A2`, the
     superseded reader returned `total_x = -4.3230998769e-19` -- the moment
     file's row -- where `force.dat` carries `-3.2288097331e-01`.  Section 6.3
     would have reported `T_total = +3.11e-17 N` where the force gives
     `+23.25 N`: SEVENTEEN ORDERS OF MAGNITUDE DOWN, AND A DIFFERENT PHYSICAL
     QUANTITY IN DIFFERENT UNITS (N.m, not N).  Both happen to carry the same
     sign on this arm, so the failure is not a sign flip -- it is worse than
     that: section 6.3's registered SIGN gate would have been decided by the
     sign of a rounding-level moment component, which carries no physical
     information and could fall either way on the next run.  Sorting the listing
     does NOT fix this (`moment.dat` sorts after `force.dat` and would still win
     the `>=`): the graded FILE IS NOW NAMED, never discovered.
 (9) FOUND BY MEASUREMENT, AND THE MOST SERIOUS OF ALL -- THE `volumeMode`
     GUARD READ A COMMENT.  `read_fvoptions_source` searched the whole file for
     `volumeMode\\s+(\\w+)\\s*;` and took the FIRST match, which in
     `constant/fvOptions` is LINE 6, INSIDE THE BANNER COMMENT, where the
     template writes "`volumeMode specific;` APPEARS HERE VERBATIM AND IS
     LOAD-BEARING".  The live entry is line 56.  MEASURED: with line 56 set to
     `absolute` and the comment untouched, the superseded reader returns
     `specific` AND DOES NOT REFUSE.  Since the comment is fixed boilerplate in
     `fvOptions.template`, THE GUARD WAS PERMANENTLY BLIND TO THE ONLY THING IT
     WAS WATCHING -- and `volumeMode` is the first of the three silent factors,
     the one registration section 2.4 calls load-bearing and this file's own
     header calls a case that "would still mesh, still run, still converge and
     produce an entirely wrong map".  BOTH check-1 reads passed this guard as
     sound; it is caught here only because the repair's selftest tried to make
     it fire.  `verification` then measured it independently and found the
     stronger statement (05088e94): WITH THE LIVE ENTRY DELETED ENTIRELY the
     guard STILL reports `specific`.  IT CANNOT FAIL -- it returns `specific`
     for every possible state of the entry it claims to check, absence included.
     THE FIX IS STRUCTURAL AND COVERS ALL FOUR KEYS, not just the one that
     failed: comments are blanked before any dictionary is searched (offsets
     preserved, so the plant splices the bytes the reader reads), and every
     entry goes through `sole_entry`, which REFUSES ON ABSENCE and REFUSES ON
     MULTIPLICITY instead of taking `re.search`'s first match.  See
     `sole_entry`'s docstring for the tested mechanism -- `\\s+` DOES cross
     newlines, a backtick before the VALUE blocks a match while a backtick
     before the KEYWORD blocks nothing, and the real rule is that a guard of
     this shape goes blind whenever a comment QUOTES THE ENTRY VERBATIM.
     `selectionMode` and `cellZone` are correct today by luck of what the
     comments happen to say; they are now correct by construction.
(10) FOUND BY RUNNING IT -- SECTION 6.3 COULD NEVER HAVE PASSED.  The launcher
     writes `Su_x = 0` for the registered `delta_p = 0` empty duct, and
     `read_fvoptions_source` refused ANY source with `su[0] <= 0.0`, citing
     section 2.5's +x rule.  So `control_6_3` would have refused every
     empty-duct control it was ever handed, naming the wrong reason -- and
     since section 9.2 requires BOTH V controls to pass before any gated solve,
     NO GATED SOLVE COULD EVER HAVE BEEN LAUNCHED.  Neither check-1 read caught
     it and neither did this repair until the comparator was run END TO END,
     which is the argument for the plumbing limb in the selftest.  A zero source
     is now accepted ONLY where a caller explicitly registers one, and that
     caller then requires it to be exactly zero.
(11) FOUND BY MEASUREMENT -- `rc_baseline` WAS AN ACCEPTED AND UNUSED PARAMETER.
     `control_6_2` took `rc_baseline` and never referenced it: the delta_p = 0
     baseline supplied C2's comparand and NEVER PASSED THE STRICT COMPLETION
     RULE.  `completion()` now runs on the baseline too.

WHAT THIS REPAIR DELIBERATELY DOES NOT TOUCH, because both reads called it
sound and a repair that rewrites what the reviews called correct is a
regression: the three silent factors -- `volumeMode` refused unless literally
`specific` (the RULE is untouched; what changed is that it is now read from the
LIVE ENTRY instead of from a comment, per (9), which is a repair OF that guard
and not a relaxation of it), `WEDGE_SCALE` as a NAMED constant, and the
kinematic rho = 1.2 caught by C3's two genuinely independent arms; C4's ONE-WAY negative
limb; section 6.3 registering SIGN as well as magnitude; `cell_volumes` reading
the BUILT mesh; and the six clauses of the strict completion rule.  The
pyramid-decomposition arithmetic of `cell_volumes` is BYTE-IDENTICAL to the
superseded file -- only the polyMesh parsing moved into `_read_polymesh` so the
planted control can address a point by index without a second, drifting copy of
those regexes.

VERIFICATION_CHARTER section 2d.2 -- THE LIMB, RULED AGAINST THIS LANE'S FIRST
ANSWER, AND THE REPAIR SURVIVES ON THE STRICTER ONE.
This lane first wrote that the PRE-COMPUTE limb applied, because section 2d
closed the grading path "once THE FIRST GRADED SOLVE HAS STARTED" and F28 has
had none.  THAT GROUND WAS WRONG.  `verification` ruled at commit 05088e94
(charter v1.32, section 2d.2), read here at the sha: CLAUDE.md RULE 2 GOVERNS,
gates close at THE FIRST COMPUTE UNDER THE REGISTRATION -- FEASIBILITY COMPUTE
INCLUDED -- and section 2d's narrower wording is a defect in that charter,
corrected prospectively on the ground of its own section 2g (a narrower clause
cannot except a standing rule) and of section 2i, which already said the freeze
bites when compute begins.  F28's gates therefore closed at the earliest
`started_utc` of the `FEAS_*` runs.

SO THE OPERATIVE LIMB IS SECTION 2d.1's POST-COMPUTE REPAIR EXCEPTION, and this
repair is legal on it because the four conditions were checked anyway, before
the ruling existed and while this lane believed they were unnecessary:

  (1) DEMONSTRABLE ERROR, NOT PREFERENCE -- MET.  Eleven defects, each a
      closed-form or measured fact: a MOMENT graded as a FORCE (17 orders of
      magnitude, different units); a guard that reports `specific` for every
      possible state of the entry it checks INCLUDING ITS ABSENCE; a control
      that deletes 735 bytes of `FoamFile` header while reporting success; a
      section 6.3 that could never have passed.  No band, threshold, cap or
      label is touched and no tuning parameter is chosen.
  (2) ESTABLISHED BY AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS -- MET, and it
      is the load-bearing condition.  The defects were found by two check-1 code
      reads that grade nothing and by a selftest harness that grades nothing,
      driven against LABEL=FEASIBILITY artifacts registered as never gradeable.
      THE COMPARATOR HAS PRODUCED NO NUMBER, so nothing here can have been
      selected to move a verdict in a wanted direction -- there is no verdict.
  (3) THE RECORD DISCLOSES IT, NAMES THE INSTRUMENT, AND QUANTIFIES WHAT MOVED
      -- MET.  This header, defect by defect, with line numbers and measured
      values.
  (4) PRE-REPAIR VALUES RECORDED BESIDE THE PUBLISHED ONES -- MET, and more
      strongly than the condition asks: nothing is published, and THE SUPERSEDED
      FILE ITSELF IS THE MUTANT in six selftest limbs, so its behaviour is
      MEASURED rather than described.

THIS FILE RULES ON NOTHING.  The determination above is `verification`'s,
already made; it is recorded here so the next reader inherits the ruling and not
this lane's first, mistaken answer.

WIRING `guard_virgin_case`.  It belongs in the LAUNCHER, not in the comparator:
the comparator grades a finished run and by then the time directory MUST exist,
so the guard can only be true where a run is STARTED.  `--guard-virgin <case>`
gives it a real call site; `run_f28.sh` must call it in the ASSEMBLE phase,
BEFORE the `mkdir -p "$RUN_DIR/system" ...` that creates `0` (run_f28.sh:229),
i.e. immediately after `PHASE="assemble"` at run_f28.sh:228.  That edit is NOT
made here: it is a change to a launcher, it returns to the supervisor as its own
diff, and this lane does not make it unasked.

ADDENDUM 3's FLOORED STATIONARITY CRITERION IS NOW WIRED, AND section 6.3's
STANDING REFUSAL IS STRUCK.  Addendum 3 (registration commit 0a62c5c6, under
Sanaa's personal approval at `5dd94f4f`) registers thrust stationarity as
`ptp <= max(0.001*|T_mean|, T_floor)` over the last 2000 iterations, IN
5-DEGREE SECTOR NEWTONS, and its section 6 grades V(b) on it.  The earlier
candidate implemented nothing and REFUSED rather than issuing `GATE REACHED`
with a registered channel unevaluated; the supervisor ruled that refusal correct
and standing until the criterion was wired.  It is now wired, and five things
carry the weight:

  (a) `T_floor` IS DERIVED, NEVER PASTED.  `assert_floor_derivation` runs
      Addendum 3 section 4's chain from constants already frozen above and
      REFUSES AT IMPORT unless it reproduces section 4's `A_disk`, section 6.2
      control C3's 42.7257 N and Addendum 3's 5.934119457e-04 N, each to half
      the last digit the registration prints.  The literals are asserted
      against the derivation; the derivation is never fitted to the literals.
  (b) THE FRAME IS PROVED, NOT ASSERTED.  `assert_stationarity_frame` requires
      `T_total == -(last windowed total_x) * WEDGE_SCALE` BIT-EXACTLY, so the
      series is demonstrably the pre-multiplication quantity taken from the
      column that was actually graded -- not a frame inferred from a comment.
      A slip here is a factor of 72 in the PERMISSIVE direction and would have
      rescued the zero-source arm (Addendum 3 section 5).
  (c) THE READER CARRIES ITS OWN PLANT.  `plant_into_stationarity_window`
      plants into the FIRST ROW OF THE WINDOW -- the row no other control
      addresses -- and requires `ptp` to move AND `T_mean` to move by exactly
      the displacement over the window.  The last-row plant already on
      `forcesDuct` certifies `T_total` and certifies nothing about 1999 of the
      2000 graded rows.
  (d) `ptp` AND `T_mean` KEEP `read_ptp_f28.py:8`'s DEFINITIONS, including its
      plain `sum(w)/len(w)`, because Addendum 3 registers them as "unchanged
      from" that file -- not a re-derivation, however better.
  (e) THE FLOOR IS THRUST-ONLY, ENFORCED.  Addendum 3 section 3's final
      paragraph leaves the disk mass-flow row unfloored; `stationarity_criterion`
      REFUSES any quantity outside `FLOORED_QUANTITIES`, so the floor cannot
      reach a second registered row by a caller's copy-paste.

An UNSTATIONARY V(b) is now `NOT A RESULT` through the verdict field, not
through a refusal: stationarity is a registered criterion with a threshold, and
a comparator refuses for instrument failures, not for failing gates.

-------------------------------------------------------------------------------
THE THREE SILENT FACTORS THIS COMPARATOR EXISTS TO CATCH
-------------------------------------------------------------------------------
Each produces a map that is smooth, monotone, self-consistent and WRONG.

(1) `volumeMode`  (section 2.4).  `volumeMode` is a REQUIRED entry of
    `SemiImplicitSource` -- `read()` at SemiImplicitSource.C:534 uses a `get`,
    not a defaulted lookup -- and it SILENTLY RESCALES the supplied number:
    `absolute` sets `VDash_ = V_` (the cell-zone volume) while `specific` leaves
    `VDash_ = 1`, and the value is divided by `VDash_`.  The class constructor's
    own default is `vmAbsolute`.  THE FROZEN `fvOptions` STATES
    `volumeMode specific;` VERBATIM and this comparator REFUSES if the file on
    disk does not.

(2) `WEDGE_SCALE` (section 2.6).  The domain is a 5-degree wedge, 5/360 of the
    annulus, so every force this case reports is the wedge force times 72.
    A missing factor of 72 is invisible in a residual and invisible in a map.

(3) THE KINEMATIC SOURCE.  `simpleFoam` IS INCOMPRESSIBLE: its momentum
    equation is divided by rho and carries NO rho at all
    (`constant/transportProperties` holds `nu` only).  The directive's
    `injectionRateSuSp = delta_p / t` in N/m^3 is a FORCE density and is right
    for a COMPRESSIBLE solver; the value this case must supply is
    `delta_p / (rho * t)` in m/s^2.  The two differ by rho = 1.2 -- A FACTOR OF
    1.2, which is exactly the size that looks like a modelling detail rather
    than an error.  C3 closes on this because arm (a) is analytic from
    `delta_p` and arm (b) integrates what the solver was actually told to apply.

-------------------------------------------------------------------------------
SIGN CONVENTION (section 2.5), stated once and used everywhere
-------------------------------------------------------------------------------
Freestream and bulk flow are +x; upstream is -x.  The momentum source on the
cellZone `disk` is +x (it accelerates the fluid downstream).  THRUST IS POSITIVE
IN -x: every reported force is the -x component times -1, so `T_disk`, `T_duct`
and `T_total` are POSITIVE WHEN PROPULSIVE.  `T_duct` going negative means the
duct has become net drag.

-------------------------------------------------------------------------------
COMPLETION (CLAUDE.md rule 4, registration section 11.1)
-------------------------------------------------------------------------------
A run is done only if EVERY clause holds: rc = 0; an `End` line; last time ==
`endTime`; fields `U p k omega nut` present at `endTime` (this case is
NON-THERMAL and the substitution is registered at 11.1 clause 4);
`ExecutionTime` count == `endTime`; and THE AGE GUARD -- every field at
`endTime` NEWER than the case's own `0/U`.  Any clause failing means the run is
not done and this comparator REFUSES (exit 2) RATHER THAN DEGRADING.

Actuator-disk representation; no rotor.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys

# =============================================================================
# REGISTERED CONSTANTS -- section 4 unless noted.  NAMED, never inlined.
# =============================================================================
WEDGE_DEG    = 5.0
WEDGE_SCALE  = 360.0 / WEDGE_DEG        # 72.0  -- section 2.6, A NAMED CONSTANT
RHO          = 1.2                      # kg/m^3, section 4
NU           = 1.5e-5                   # m^2/s, section 4
D            = 0.25
R_DUCT       = D / 2.0
TIP_GAP      = 0.01 * D
R_TIP        = R_DUCT - TIP_GAP         # 0.12250
R_HUB        = 0.15 * D                 # 0.03750
A_DISK       = math.pi * (R_TIP ** 2 - R_HUB ** 2)      # 0.042725660088821185
T_DISK       = 0.02 * D                 # 0.005
DELTA_P_CTRL = 1000.0                   # Pa, section 6.2
U_INF_CTRL   = 0.0                      # static, section 6.2
DELTA_P_C4   = 2000.0                   # Pa, section 6.2 C4 negative limb
U_INF_PASS   = 30.0                     # m/s, section 6.3
FIELDS_REQUIRED = ("U", "p", "k", "omega", "nut")       # section 11.1 clause 4

# Registered tolerances -- section 6.2 / 6.3.  FROZEN; not arguments.
TOL_C1 = 0.02      # area-averaged disk pressure rise vs delta_p
TOL_C3 = 0.005     # T_disk computed two independent ways
TOL_C6_3 = 0.02    # empty-duct |T_total| as a fraction of the loaded thrust

# The plant.  A known non-zero, delivered the way reality delivers one --
# written into the solved field ON DISK and read back through the real reader.
# ONE PLANT PER READER THAT PRODUCES A GRADED NUMBER.  The superseded file
# carried only PLANT_PA, on a reader whose VALUE reached no graded number.
PLANT_PA = 3.21e-02        # Pa,     into the solved `p`     -> read_volScalarField
PLANT_FO = 3.21e-02        # into a function-object row      -> function_object_series
PLANT_SU = 3.21e-02        # m/s^2,  into the fvOptions Su_x -> read_fvoptions_source
PLANT_DX = 1.0e-05         # m,      into a polyMesh point   -> cell_volumes
PLANT_TOL = 1.0e-9

# The plant is read back as a DIFFERENCE against a value parsed from the file,
# so the floor on what is resolvable is the double-precision spacing at that
# value.  `Su_x` for delta_p = 1000 Pa is 1.667e+05 m/s^2, whose ulp is 2.9e-11
# -- far below PLANT_TOL -- but the tolerance is written as a function of the
# operand rather than as a bare constant so it cannot silently become optimistic
# on a case with a larger one.  The superseded file's bare 1e-9 was comfortable
# for kinematic `p` and would have failed spuriously above |p| ~ 1e4.
def plant_tol(operand):
    return max(PLANT_TOL, 1.0e-12 * abs(operand))


# WHICH FILE EACH GRADED FUNCTION OBJECT LIVES IN, AND WHICH COLUMN IS GRADED.
# THE FILE IS NAMED, NEVER DISCOVERED.  A `forces` function object writes BOTH
# `force.dat` and `moment.dat` into the same directory with IDENTICAL column
# names and IDENTICAL `Time` values; the superseded reader iterated the whole
# directory and broke the tie by iteration order, and MEASURED on
# `verification/runs/F28_runs/FEAS_L1_dp1000_U20_A2` it returned the Z-MOMENT
# row (`total_x = -4.3230998769e-19`) where `force.dat` carries
# `-3.2288097331e-01`.  A column value of `None` is resolved from the header by
# the caller and REFUSES unless exactly one column matches.
FO_GRADED = {
    "diskPlaneUp":   ("surfaceFieldValue.dat", "areaAverage(p)"),
    "diskPlaneDown": ("surfaceFieldValue.dat", "areaAverage(p)"),
    "diskFlow":      ("surfaceFieldValue.dat", None),
    "forcesDuct":    ("force.dat", "total_x"),
}

# =============================================================================
# ADDENDUM 3's FLOORED THRUST-STATIONARITY CRITERION -- WIRED, AND DERIVED
# =============================================================================
# Registration Addendum 3 (commit 0a62c5c6), section 3, as struck and corrected
# by Addendum 4.  THE CRITERION IN FORCE:
#
#     ptp <= max( STATIONARITY_REL * |T_mean| , T_floor )
#
# over the last STATIONARITY_WINDOW_ITERS iterations, `ptp = max(Fx) - min(Fx)`
# and `T_mean = mean(Fx)` over that window, BOTH UNCHANGED FROM
# `read_ptp_f28.py:8`.  The limbs are joined by `max`, so the test is THE MORE
# PERMISSIVE OF THE TWO and can never divide by a vanishing denominator.
#
# THE FLOOR IS DERIVED HERE, NOT PASTED.  Addendum 3 section 4 exists to forbid
# exactly a floor that arrives as a literal: a threshold chosen once the answers
# are in hand is what pre-registration exists to prevent, and a pasted constant
# cannot be told apart from one by reading it.  Every input below is already
# frozen above -- `A_DISK` from section 4's geometry, `DELTA_P_CTRL` from
# section 9.3's registered triple point, `WEDGE_SCALE` from section 2.6 -- and
# the chain runs section 4's four steps in order.  The registration's PRINTED
# figures appear below only as ASSERTION TARGETS: the constant is asserted
# against the derivation, never the derivation against the constant.
STATIONARITY_REL = 0.001                # section 8's 0.1 %, as a fraction
STATIONARITY_WINDOW_ITERS = 2000        # section 8; `read_ptp_f28.py:30`

# Step 1 is `A_DISK` above.  Steps 2-4:
T_DISK_REF_FULL_N   = DELTA_P_CTRL * A_DISK             # 42.7256600888 N
T_DISK_REF_SECTOR_N = T_DISK_REF_FULL_N / WEDGE_SCALE   # 0.593411945678 N
STATIONARITY_FLOOR_SECTOR_N = STATIONARITY_REL * T_DISK_REF_SECTOR_N

# THE WRONG FRAME, NAMED SO IT CANNOT BE REACHED BY ACCIDENT.  Addendum 3
# section 5: applied to sector data this value would have RESCUED the
# zero-source arm (0.020422 N < 0.042726 N), and that near-miss is recorded
# there as the exact error the section exists to foreclose.  It is defined so
# refusals and diagnostics can PRINT it; NO criterion in this file compares
# against it, and `assert_stationarity_frame` proves the frame by identity
# against the graded column rather than by anyone's reading of a template.
STATIONARITY_FLOOR_FULL_N = STATIONARITY_REL * T_DISK_REF_FULL_N

# The registration's own printed figures, quoted ONLY to be asserted against.
# Three different sections, so one transcription slip cannot satisfy all three.
REG_A_DISK_M2                   = 0.0427257        # section 4
REG_T_DISK_REF_FULL_N           = 42.7257          # section 6.2, control C3
REG_STATIONARITY_FLOOR_SECTOR_N = 5.934119457e-04  # Addendum 3 section 4,
                                                   # re-affirmed by Addendum 4

# Addendum 3 section 3, FINAL PARAGRAPH -- a boundary, not a note:
#   "The disk mass-flow stationarity row of section 8 is NOT touched.  Sanaa's
#    approval names the thrust floor.  A mass-flow floor is not derived, not
#    registered and not in force."
# CLAUDE.md rule 9: the approval's width is the width of the change and no
# wider.  `stationarity_criterion` REFUSES any quantity outside this tuple, so
# a floor cannot reach a second registered row by a caller's copy-paste -- the
# leak has to DEFEAT A GUARD, not merely go unnoticed.
FLOORED_QUANTITIES = ("thrust",)


class Refusal(Exception):
    pass


def refuse(msg):
    sys.stderr.write("NOT A RESULT -- comparator refuses (exit 2): %s\n" % msg)
    sys.exit(2)


def assert_floor_derivation():
    """THE DERIVED FLOOR IS CHECKED AGAINST THE REGISTRATION -- IN THAT DIRECTION.

    Five agreements.  The first two are EXACT-EQUALITY checks that the geometry
    constants frozen above are literally Addendum 3 section 4's chain, written
    differently: section 4 gives `r_hub = 0.3 D / 2` where line 304 above writes
    `0.15 * D`, and a chain that is only *described* as matching is not a chain.
    The remaining three are agreements with numbers frozen in THREE DIFFERENT
    sections, so a single transcription slip cannot satisfy them all:

        A_disk            vs section 4's registered            0.0427257 m^2
        T_disk_ref,full   vs section 6.2 control C3's analytic 42.7257 N
        T_floor (sector)  vs Addendum 3 section 4's            5.934119457e-04 N

    Each tolerance is HALF THE LAST DIGIT THE REGISTRATION PRINTS, so the test
    is exactly "agrees to every digit that section prints" -- not a slack band
    sized until the assertion passed.  Addendum 3 section 4 says the value is
    "defensible to 4 s.f." and that "nothing turns on any digit beyond the
    first"; these tolerances are far tighter than that and are therefore a
    stricter test than the registration requires, never a looser one.

    It runs AT IMPORT.  A comparator whose floor does not reproduce the
    registered one must not be importable, let alone gradeable.
    """
    for name, lhs, rhs, expr in (
            ("r_tip", R_TIP, D / 2.0 - 0.01 * D, "D/2 - 0.01 D"),
            ("r_hub", R_HUB, 0.3 * D / 2.0, "0.3 D / 2")):
        if lhs != rhs:
            refuse("THE FLOOR'S GEOMETRY CHAIN IS NOT SECTION 4's: this file's "
                   "%s is %.17g and Addendum 3 section 4's `%s` is %.17g.  The "
                   "floor is derived from these, so a chain that only LOOKS "
                   "like section 4's is a pasted constant with extra steps."
                   % (name, lhs, expr, rhs))
    out = {"r_tip_m": R_TIP, "r_hub_m": R_HUB,
           "chain": "A_disk = pi (r_tip^2 - r_hub^2); T_full = delta_p A_disk; "
                    "T_sector = T_full / WEDGE_SCALE; T_floor = %g T_sector"
                    % STATIONARITY_REL}
    for name, derived, registered, tol, unit, where in (
            ("A_disk", A_DISK, REG_A_DISK_M2, 5.0e-8, "m^2",
             "registration section 4"),
            ("T_disk_ref,full", T_DISK_REF_FULL_N, REG_T_DISK_REF_FULL_N,
             5.0e-5, "N", "registration section 6.2, control C3"),
            ("T_floor,sector", STATIONARITY_FLOOR_SECTOR_N,
             REG_STATIONARITY_FLOOR_SECTOR_N, 5.0e-14, "N",
             "registration Addendum 3 section 4")):
        if not abs(derived - registered) <= tol:
            refuse("THE DERIVED FLOOR DOES NOT REPRODUCE THE REGISTERED ONE: "
                   "%s derives to %.17g %s and %s registers %.17g %s, a "
                   "difference of %.3e against a tolerance of %.3e (half the "
                   "last digit the registration prints).  Addendum 3 section 4 "
                   "derives the floor from frozen inputs precisely so that this "
                   "disagreement is loud.  REFUSING RATHER THAN GRADING AGAINST "
                   "A THRESHOLD THE REGISTRATION DOES NOT CARRY."
                   % (name, derived, unit, where, registered, unit,
                      abs(derived - registered), tol))
        out[name] = {"derived": derived, "registered": registered,
                     "abs_difference": abs(derived - registered),
                     "tolerance": tol, "unit": unit, "authority": where}
    return out


# Runs at import.  Nothing below is reachable with a floor that disagrees.
FLOOR_DERIVATION = assert_floor_derivation()


# =============================================================================
# OpenFOAM FIELD I/O -- the REAL reader.  The plant travels through this.
# =============================================================================
_HDR = "// * * *"

# Hoisted so the READER and the PLANT that certifies it cannot drift apart: one
# pattern, used by both.  A second copy in the plant is a second thing to keep
# right, and the plant would then certify a pattern the reader does not use.
_SCALAR_LIST_RE = re.compile(
    r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n\(")
_VEC_RE = re.compile(
    r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)")
_SU_RE = re.compile(
    r"U\s*\(\s*\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)"
    r"\s+([-\d.eE+]+)\s*\)")
_VOLUME_MODE_RE = re.compile(r"volumeMode\s+(\w+)\s*;")
_SELECTION_MODE_RE = re.compile(r"selectionMode\s+(\w+)\s*;")
_CELLZONE_RE = re.compile(r"cellZone\s+(\w+)\s*;")
_WRITE_FORMAT_RE = re.compile(r"writeFormat\s+(\w+)\s*;")


def sole_entry(pattern, text, key, path, why=""):
    """THE one way this comparator reads a dictionary entry.  THREE REFUSALS.

    ABSENCE      -- a missing or DELETED entry REFUSES.  It never falls through
                    to a class default.  This is the property the superseded
                    guard did not have: with the live `volumeMode` entry DELETED
                    ENTIRELY it still reported `specific`.
    MULTIPLICITY -- more than one match REFUSES.  It never silently takes the
                    FIRST.  `re.search` taking the first match is the whole
                    mechanism of the blind guard.
    COMMENTS     -- `text` MUST already be comment-stripped by the caller, so a
                    comment can never be read as an entry.

    WHY ALL THREE, AND WHY ON EVERY KEY RATHER THAN JUST THE ONE THAT FAILED.
    Measured in `constant/fvOptions`: `volumeMode` has TWO matches (line 6 in
    the banner comment, line 56 live) and `selectionMode` and `cellZone` have
    ONE each (lines 54 and 55, both live).  The siblings are therefore correct
    TODAY, and correct BY LUCK OF WHAT THE COMMENTS HAPPEN TO SAY.  The precise
    hazard, tested rather than assumed:

      * `\\s+` DOES cross newlines -- `cellZone\\n  disk;` matches -- so the
        header's line 2 "on the cellZone" reaches across the line break.
      * A backtick before the VALUE blocks the match, and that alone is what
        saves line 2: the next line begins "`disk`." and `(\\w+)` cannot match a
        backtick.  MEASURED: that string returns None.
      * A backtick before the KEYWORD blocks NOTHING -- the match simply starts
        after it.  MEASURED: "`selectionMode cellZone;` is registered" MATCHES
        and yields `cellZone`.  Line 6 is backticked and is exactly what blinded
        `volumeMode`.

    So the operative rule is neither "backticks save us" nor "\\s+ stops at a
    newline": A GUARD OF THIS SHAPE GOES BLIND WHENEVER A COMMENT QUOTES THE
    ENTRY VERBATIM as keyword-word-semicolon -- which is precisely what a
    careful author writes to explain why the entry matters.  The siblings escape
    only because nobody has yet quoted them in that form, and the next careful
    comment removes that.  Fixed structurally on all four keys, not patched on
    the one that happened to fail.
    """
    ms = list(pattern.finditer(text))
    if not ms:
        refuse("ABSENT ENTRY: %s states NO `%s`.  A missing or deleted entry "
               "REFUSES; it never falls through to a class default.  %s"
               % (path, key, why))
    if len(ms) > 1:
        lines = [text[:m.start()].count("\n") + 1 for m in ms]
        refuse("AMBIGUOUS ENTRY: %s carries %d matches for `%s`, at lines %s, "
               "AFTER comments were stripped -- so these are %d live entries, "
               "not a comment quoting one.  The superseded guard used "
               "`re.search` and took the FIRST silently, which is how a banner "
               "comment came to stand in for a dictionary entry.  REFUSING "
               "rather than choosing." % (path, len(ms), key, lines, len(ms)))
    return ms[0]


def _strip_foam_comments(t):
    """Blank `/* ... */` and `// ...` comments, PRESERVING EVERY OFFSET.

    THE DEFECT THIS EXISTS TO CLOSE, MEASURED.  `read_fvoptions_source` searched
    the WHOLE FILE for `volumeMode\\s+(\\w+)\\s*;` and took the FIRST match --
    which in `constant/fvOptions` is on LINE 6, INSIDE THE BANNER COMMENT, where
    the template says "`volumeMode specific;` APPEARS HERE VERBATIM AND IS
    LOAD-BEARING".  The LIVE entry is on line 56.  Measured: with the live entry
    set to `absolute` and the comment untouched, the superseded reader returned
    `specific` AND DID NOT REFUSE.  The comment is fixed boilerplate in
    `fvOptions.template`, so it always reads `specific` and the guard on the
    FIRST of the three silent factors -- the one the registration calls
    load-bearing, the one that "would still mesh, still run, still converge and
    produce an entirely wrong map" -- was permanently blind to the only thing it
    was watching.

    Comment characters become SPACES rather than being deleted, so a match found
    in this view has the SAME SPAN in the raw text.  That is what lets the
    planted control splice into the real bytes using a span located here.
    """
    out = list(t)
    i, n = 0, len(t)
    while i < n:
        if t.startswith("/*", i):
            j = t.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
        elif t.startswith("//", i):
            j = t.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = " "
            i = j
        else:
            i += 1
    return "".join(out)


def _body(path):
    t = open(path, errors="replace").read()
    i = t.find(_HDR)
    if i < 0:
        raise Refusal("no FoamFile header separator in %s" % path)
    return t[i:]


def read_volScalarField(path):
    """Return (values, uniform_value_or_None, raw_text).

    THE reader.  C1 uses it, and `plant_into_p` proves it can see a non-zero by
    making the field on disk carry one and reading it back through this call.
    """
    t = _body(path)
    m = re.search(r"internalField\s+uniform\s+([-\d.eE+]+)\s*;", t)
    if m:
        return None, float(m.group(1)), t
    m = _SCALAR_LIST_RE.search(t)
    if not m:
        raise Refusal("cannot parse internalField in %s" % path)
    n = int(m.group(1))
    start = t.index("(", m.end() - 1)
    end = t.index(")", start)
    vals = [float(v) for v in t[start + 1:end].split()]
    if len(vals) != n:
        raise Refusal("%s declares %d values and carries %d" % (path, n, len(vals)))
    return vals, None, t


# `write_volScalarField_values` IS STRUCK.  It re-rendered EVERY value of the
# field through `%.12g` and rewrote the whole block, and because it was handed
# `_body()`'s output -- which begins at the header separator -- it wrote back a
# file with the `FoamFile` dictionary DELETED.  MEASURED on a real F28 `p`
# field: 410,646 bytes in, 409,911 bytes out, `FoamFile` absent, after a control
# that reported success.  Planting is now a one-token splice (`splice_scalar_value`).
#
# `read_volVectorField` IS STRUCK.  It had ZERO call sites, so it had never
# executed and no planted control had ever been through it.  Nothing graded in
# this case needs a vector field, and a reader never shown able to see a
# non-zero must not sit in a comparator waiting to be trusted by a later editor.


# =============================================================================
# BYTE-EXACT ARTIFACT HANDLING -- THE GRADER LEAVES NO FINGERPRINT
# =============================================================================
# This lab's product is a number that cites AN ARTIFACT STILL ON DISK.  A plant
# that mutates the graded artifact spends the evidence to certify the reader.
# Every plant below snapshots the file's exact bytes and its exact mtime,
# restores them, and REFUSES if the sha256 or the mtime moved.
def _atomic_write_bytes(path, data):
    tmp = path + ".plant.tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _atomic_write_text(path, text):
    # latin-1 is byte-transparent: every byte round-trips, so a splice into
    # decoded text cannot corrupt a byte it did not address.
    _atomic_write_bytes(path, text.encode("latin-1"))


class ArtifactSnapshot(object):
    """Exact bytes and exact mtime of one graded artifact, restorable."""

    def __init__(self, path):
        self.path = path
        with open(path, "rb") as fh:
            self.raw = fh.read()
        st = os.stat(path)
        self.times_ns = (st.st_atime_ns, st.st_mtime_ns)
        self.sha = hashlib.sha256(self.raw).hexdigest()

    def text(self):
        return self.raw.decode("latin-1")

    def restore(self):
        _atomic_write_bytes(self.path, self.raw)
        os.utime(self.path, ns=self.times_ns)

    def verify_unchanged(self, why):
        with open(self.path, "rb") as fh:
            now = fh.read()
        sha = hashlib.sha256(now).hexdigest()
        if sha != self.sha:
            refuse("THE GRADER ALTERED THE ARTIFACT IT GRADES: %s is %d bytes "
                   "sha256 %s where it was %d bytes sha256 %s before %s.  This "
                   "lab's product is a number that cites an artifact STILL ON "
                   "DISK."
                   % (self.path, len(now), sha[:16], len(self.raw),
                      self.sha[:16], why))
        mt = os.stat(self.path).st_mtime_ns
        if mt != self.times_ns[1]:
            refuse("THE GRADER RESTORED THE BYTES OF %s BUT NOT ITS mtime "
                   "(%d -> %d) after %s.  Rule 4 clause 6's age guard reads "
                   "mtime, so a grader that moves it has moved the evidence "
                   "the guard is built on." % (self.path, self.times_ns[1],
                                               mt, why))
        return {"sha256": sha, "bytes": len(now), "mtime_ns": mt}


def _token_spans(s):
    return [m.span() for m in re.finditer(r"\S+", s)]


def splice_scalar_value(full_text, index, new_value):
    """Replace ONE value of the internalField list, BY INDEX, leaving every
    other byte of the file -- the `FoamFile` header included -- untouched.

    `repr(float)` round-trips exactly, so nothing is lost to a `%g` format and
    `writePrecision` never enters the plant path.
    """
    m = _SCALAR_LIST_RE.search(full_text)
    if not m:
        raise Refusal("cannot plant into a uniform or unparsable scalar field")
    start = full_text.index("(", m.end() - 1)
    end = full_text.index(")", start)
    body = full_text[start + 1:end]
    spans = _token_spans(body)
    if index >= len(spans):
        raise Refusal("cell index %d is past the %d values on disk"
                      % (index, len(spans)))
    a, b = spans[index]
    return (full_text[:start + 1] + body[:a] + repr(float(new_value))
            + body[b:] + full_text[end:])


def splice_point_x(full_text, index, new_x):
    """Replace the x-coordinate of ONE polyMesh point, BY INDEX.

    Split at the SAME header separator `_body()` uses, so the match index here
    is the same point index `_read_polymesh` assigns.
    """
    i = full_text.find(_HDR)
    if i < 0:
        raise Refusal("no FoamFile header separator in the points file")
    head, body = full_text[:i], full_text[i:]
    ms = list(_VEC_RE.finditer(body))
    if index >= len(ms):
        raise Refusal("point index %d is past the %d points on disk"
                      % (index, len(ms)))
    a, b = ms[index].span(1)
    return head + body[:a] + repr(float(new_x)) + body[b:]


# =============================================================================
# MESH READERS -- the cellZone and the cell volumes come off the BUILT mesh
# =============================================================================
def read_cellzone(case, name):
    p = os.path.join(case, "constant", "polyMesh", "cellZones")
    if not os.path.exists(p):
        raise Refusal("no cellZones file: %s" % p)
    t = _body(p)
    m = re.search(re.escape(name) + r"\s*\{.*?cellLabels\s+List<label>\s*\n?\s*"
                  r"(\d+)\s*\n\(", t, re.S)
    if not m:
        raise Refusal("cellZone %r not found in %s" % (name, p))
    n = int(m.group(1))
    start = t.index("(", m.end() - 1)
    end = t.index(")", start)
    ids = [int(v) for v in t[start + 1:end].split()]
    if len(ids) != n:
        raise Refusal("cellZone %s declares %d and carries %d" % (name, n, len(ids)))
    return ids


def _read_polymesh(case):
    """Points, faces, owner and neighbour off the BUILT mesh.

    EXTRACTED UNCHANGED from `cell_volumes` so the planted control on
    `cell_volumes` can address a point BY INDEX without a second, drifting copy
    of these regexes.  The pyramid-decomposition arithmetic below is untouched.
    """
    pm = os.path.join(case, "constant", "polyMesh")
    pts = [(float(m.group(1)), float(m.group(2)), float(m.group(3)))
           for m in _VEC_RE.finditer(_body(os.path.join(pm, "points")))]
    faces = [[int(v) for v in m.group(2).split()]
             for m in re.finditer(r"(\d+)\(([\d\s]+)\)",
                                  _body(os.path.join(pm, "faces")))]
    t = _body(os.path.join(pm, "owner"))
    own = [int(v) for v in t[t.index("\n(") + 2:t.rindex(")")].split()]
    t = _body(os.path.join(pm, "neighbour"))
    nei = [int(v) for v in t[t.index("\n(") + 2:t.rindex(")")].split()]
    return pm, pts, faces, own, nei


def cell_volumes(case):
    """Exact cell volumes from `constant/polyMesh`, by pyramid decomposition.

    Read off the BUILT mesh, never from the requested grading
    (MESH_STANDARD 9.2: the requested value is the one that lies).
    """
    _pm, pts, faces, own, nei = _read_polymesh(case)
    nc = max(own) + 1

    fctr, farea = [], []
    for f in faces:
        c = [sum(pts[i][k] for i in f) / len(f) for k in range(3)]
        a = [0.0, 0.0, 0.0]
        cw = [0.0, 0.0, 0.0]
        tot = 0.0
        for i in range(len(f)):
            p1, p2 = pts[f[i]], pts[f[(i + 1) % len(f)]]
            u = [p2[k] - p1[k] for k in range(3)]
            v = [c[k] - p1[k] for k in range(3)]
            tri = [0.5 * (u[1] * v[2] - u[2] * v[1]),
                   0.5 * (u[2] * v[0] - u[0] * v[2]),
                   0.5 * (u[0] * v[1] - u[1] * v[0])]
            mag = math.sqrt(sum(q * q for q in tri))
            tc = [(p1[k] + p2[k] + c[k]) / 3.0 for k in range(3)]
            for k in range(3):
                a[k] += tri[k]
                cw[k] += tc[k] * mag
            tot += mag
        fctr.append([q / tot for q in cw] if tot > 0 else c)
        farea.append(a)

    est = [[0.0, 0.0, 0.0, 0] for _ in range(nc)]
    for fid in range(len(faces)):
        for cid in [own[fid]] + ([nei[fid]] if fid < len(nei) else []):
            for k in range(3):
                est[cid][k] += fctr[fid][k]
            est[cid][3] += 1
    ec = [[e[k] / e[3] for k in range(3)] for e in est]

    vol = [0.0] * nc
    for fid in range(len(faces)):
        for cid, sgn in ([(own[fid], 1.0)]
                         + ([(nei[fid], -1.0)] if fid < len(nei) else [])):
            d = [fctr[fid][k] - ec[cid][k] for k in range(3)]
            vol[cid] += sgn * sum(farea[fid][k] * d[k] for k in range(3)) / 3.0
    return vol


# =============================================================================
# fvOptions -- READ FROM DISK, NEVER ASSUMED (section 2.4)
# =============================================================================
def read_fvoptions_source(case, zero_source_expected=False):
    """`zero_source_expected` is REQUIRED to be explicit and is True in exactly
    one registered context: section 6.3's empty duct, where `delta_p = 0`.

    MEASURED DEFECT THIS CLOSES.  The superseded guard refused any source with
    `su[0] <= 0.0`, citing section 2.5's rule that the source is +x.  Section
    6.3 REGISTERS `delta_p = 0`, and the launcher writes `Su_x = 0` for it, so
    `control_6_3` -- which calls this reader through
    `read_fvoptions_source_or_none` -- WOULD HAVE REFUSED EVERY EMPTY-DUCT
    CONTROL IT WAS EVER GIVEN, with a message naming the wrong reason.  Section
    9.2 requires BOTH V controls to pass before any gated solve, so V(b) could
    never pass and NO GATED SOLVE COULD EVER BE LAUNCHED.  Found the first time
    the repaired comparator was run end to end.

    THIS IS NOT A RELAXATION.  Section 2.5 forbids a source in -x; a ZERO source
    is not in -x.  Under this flag the reader still refuses a negative source,
    and the ONE caller that sets it -- `control_6_3` -- then REQUIRES the source
    to be exactly zero and refuses otherwise, which is strictly stronger than
    the general guard.
    """
    p = os.path.join(case, "constant", "fvOptions")
    if not os.path.exists(p):
        raise Refusal("no constant/fvOptions: %s" % p)
    # COMMENTS ARE BLANKED FIRST.  The banner of this very file states
    # "`volumeMode specific;` APPEARS HERE VERBATIM" on line 6, and the
    # superseded reader matched THAT instead of the live entry on line 56.
    t = _strip_foam_comments(open(p, errors="replace").read())
    mode = sole_entry(
        _VOLUME_MODE_RE, t, "volumeMode", p,
        "It is a REQUIRED entry (SemiImplicitSource.C:534 uses a `get`) and "
        "the class default is vmAbsolute, which rescales the supplied value by "
        "the cell-zone volume.  Section 2.4 registers `volumeMode specific;` "
        "VERBATIM.").group(1)
    if mode != "specific":
        refuse("constant/fvOptions states `volumeMode %s;`.  Section 2.4 "
               "registers `specific` VERBATIM: under `absolute` the supplied "
               "number is divided by the cell-zone volume and the case still "
               "meshes, still runs, still converges and produces an entirely "
               "wrong map." % mode)
    sel = sole_entry(_SELECTION_MODE_RE, t, "selectionMode", p,
                     "Section 2.4 registers `selectionMode cellZone;`.").group(1)
    if sel != "cellZone":
        refuse("constant/fvOptions selectionMode is %r, not `cellZone`" % sel)
    zone = sole_entry(_CELLZONE_RE, t, "cellZone", p,
                      "Section 2.4 registers `cellZone disk;`.").group(1)
    if zone != "disk":
        refuse("constant/fvOptions cellZone is %r, not `disk`" % zone)
    m = sole_entry(_SU_RE, t, "the U source vector", p,
                   "Section 2.4 registers a single `U ((Su_x 0 0) 0);` source "
                   "on the disk cellZone; C3 arm (b) integrates it.")
    su = tuple(float(m.group(i)) for i in (1, 2, 3))
    sp = float(m.group(4))
    if sp != 0.0:
        refuse("the implicit part Sp of the U source is %g, not 0" % sp)
    if su[1] != 0.0 or su[2] != 0.0:
        refuse("the U source has non-axial components %r -- section 2.1 "
               "registers NO SWIRL AND NO ROTATION" % (su,))
    if su[0] < 0.0:
        refuse("the U source x-component is %g, which is in -x; section 2.5 "
               "registers the source as +x (it accelerates the fluid "
               "DOWNSTREAM)" % su[0])
    if su[0] == 0.0 and not zero_source_expected:
        refuse("the U source x-component is 0 and this caller did not register "
               "a zero source.  Only section 6.3's empty duct registers "
               "`delta_p = 0`; a loaded case with no source is not a loaded "
               "case." )
    return {"volumeMode": mode, "Su": su, "Sp": sp, "path": os.path.abspath(p)}


def assert_write_format(case):
    """`writeFormat ascii` is REQUIRED and is asserted, not hoped for.

    `writePrecision` is RECORDED AND NOT GATED, and the reason is worth stating
    because the superseded file's safety turned on it: that file restored the
    planted field by re-rendering EVERY value through `%.12g`, which round-trips
    only while `writePrecision <= 12`.  It is 10 in `controlDict.template`, so
    the restore was exact BY ACCIDENT of a setting in a different file, asserted
    nowhere.  This candidate SPLICES ONE TOKEN and re-renders nothing, so no
    value in any graded artifact passes through a `%g` format at any point and
    the precision is no longer load-bearing.  `writeFormat` still is: a binary
    field would be handed to an ASCII parser.
    """
    p = os.path.join(case, "system", "controlDict")
    if not os.path.exists(p):
        refuse("no system/controlDict at %s -- the write format of the fields "
               "this comparator parses cannot be established" % p)
    t = _strip_foam_comments(open(p, errors="replace").read())
    m = sole_entry(_WRITE_FORMAT_RE, t, "writeFormat", p,
                   "The OpenFOAM default is `ascii`, but this comparator parses "
                   "the fields as text and REFUSES to infer the format of the "
                   "evidence.")
    if m.group(1) != "ascii":
        refuse("system/controlDict states `writeFormat %s;`.  Every reader in "
               "this comparator parses OpenFOAM ASCII, and the planted control "
               "splices an ASCII token into the field on disk.  Under a binary "
               "format the parse is not wrong, it is MEANINGLESS, and a "
               "meaningless parse that happens to return a number is exactly "
               "what rule 3 exists to stop." % m.group(1))
    mp = re.search(r"writePrecision\s+(\d+)\s*;", t)
    return {"writeFormat": m.group(1),
            "writePrecision": int(mp.group(1)) if mp else None,
            "writePrecision_is_gated": False,
            "why_not_gated": "the plant splices one token and re-renders no "
                             "value through any %g format, so precision cannot "
                             "affect the restore",
            "controlDict": os.path.abspath(p)}


# =============================================================================
# COMPLETION (CLAUDE.md rule 4, section 11.1) -- ALL SIX CLAUSES OR NOTHING
# =============================================================================
def completion(case, log, end_time, rc):
    """Refuse (exit 2) unless every clause of section 11.1 holds."""
    fails = []
    if rc != 0:
        fails.append("clause 1: rc = %r, not 0" % rc)
    if not os.path.exists(log):
        refuse("clause 2: no solver log at %s" % log)
    text = open(log, errors="replace").read()
    if "\nEnd\n" not in text and not text.rstrip().endswith("End"):
        fails.append("clause 2: no End line in %s" % log)

    times = sorted(
        (float(d) for d in os.listdir(case)
         if re.fullmatch(r"\d+(\.\d+)?", d)
         and os.path.isdir(os.path.join(case, d))))
    if not times:
        fails.append("clause 3: no time directories under %s" % case)
        last = None
    else:
        last = times[-1]
        if abs(last - end_time) > 1e-9:
            fails.append("clause 3: last time %g != endTime %g" % (last, end_time))

    tdir = None
    if last is not None:
        tdir = os.path.join(case, ("%g" % last))
        if not os.path.isdir(tdir):
            for d in os.listdir(case):
                if os.path.isdir(os.path.join(case, d)):
                    try:
                        if abs(float(d) - last) < 1e-12:
                            tdir = os.path.join(case, d)
                    except ValueError:
                        pass
        for f in FIELDS_REQUIRED:
            if not os.path.exists(os.path.join(tdir, f)):
                fails.append("clause 4: field %s absent at %s" % (f, tdir))

    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    if n_exec != int(end_time):
        fails.append("clause 5: %d ExecutionTime lines, endTime is %g"
                     % (n_exec, end_time))

    # CLAUSE 6 -- THE AGE GUARD.  `0/U` is touched last at launch and so DATES
    # THE RUN THAT WAS ALLOWED TO PRODUCE THE ANSWER.  A field older than it is
    # a field from a previous run.
    zero_u = os.path.join(case, "0", "U")
    if not os.path.exists(zero_u):
        fails.append("clause 6: no 0/U to age the run against")
    elif tdir is not None:
        t0 = os.path.getmtime(zero_u)
        for f in FIELDS_REQUIRED:
            fp = os.path.join(tdir, f)
            if os.path.exists(fp) and os.path.getmtime(fp) <= t0:
                fails.append("clause 6 AGE GUARD: %s is NOT newer than 0/U "
                             "(%.6f <= %.6f) -- it is a field from a previous "
                             "run" % (fp, os.path.getmtime(fp), t0))

    # CLAUSE 7 -- THE AGE GUARD REACHES `postProcessing/` TOO.  Clause 6 guards
    # the FIELDS, and EVERY NUMBER THIS COMPARATOR GRADES IS READ FROM
    # `postProcessing/`, not from the fields.  The superseded file never stat'd
    # a function-object file at all, so a `postProcessing/` tree surviving from
    # an earlier solve was graded in silence -- precisely the failure clause 6
    # exists to prevent, on the only data that matters.  This is the CHEAP,
    # EARLY refusal; the BINDING per-file guard is in `_select_fo_row`, which
    # fires on exactly the files a given grading reads.
    pp = os.path.join(case, "postProcessing")
    if not os.path.isdir(pp):
        fails.append("clause 7: no postProcessing/ under %s -- every graded "
                     "number in this case is read from a function object" % case)
    elif os.path.exists(zero_u):
        t0 = os.path.getmtime(zero_u)
        newest = None
        for root, _dirs, files in os.walk(pp):
            for f in files:
                mt = os.path.getmtime(os.path.join(root, f))
                if newest is None or mt > newest:
                    newest = mt
        if newest is None:
            fails.append("clause 7: postProcessing/ under %s is EMPTY" % case)
        elif newest <= t0:
            fails.append("clause 7 AGE GUARD: NOTHING under %s is newer than "
                         "0/U (%.6f <= %.6f) -- the entire function-object tree "
                         "predates the run that was allowed to produce the "
                         "answer" % (pp, newest, t0))

    if fails:
        refuse("STRICT COMPLETION RULE (section 11.1) -- the run is NOT done:\n  "
               + "\n  ".join(fails))
    return {"clauses": "1-6 all hold, plus clause 7 (postProcessing age guard)",
            "endTime": end_time, "time_dir": tdir,
            "age_ref": os.path.abspath(zero_u),
            "solver_log": os.path.abspath(log)}


def guard_virgin_case(case):
    """Section 11.1: a guard refuses a case where `0` or any time directory
    already exists.  NO RUN IN THIS CASE IS EVER STARTED ON TOP OF ONE."""
    if os.path.isdir(os.path.join(case, "0")):
        refuse("a `0` directory already exists at %s -- no run in this case is "
               "ever started on top of an existing time directory" % case)
    for d in os.listdir(case) if os.path.isdir(case) else []:
        if re.fullmatch(r"\d+(\.\d+)?", d) and os.path.isdir(os.path.join(case, d)):
            refuse("time directory %r already exists at %s" % (d, case))


# =============================================================================
# THE PLANT (CLAUDE.md rule 3) -- through the real path, off the real disk
# =============================================================================
def plant_into_p(p_path):
    """Write a KNOWN perturbation into the solved `p` on disk and read it back
    through the SAME reader C1 uses.  Refuse if the reader cannot see it.

    THE PLANT IS NOT A PYTHON VARIABLE.  It is written into the field file in
    the case's own format, the file is re-read from disk by
    `read_volScalarField`, and the perturbation must come back.  Then the file
    is restored and the reader must NO LONGER see it -- the negative limb,
    because a reader that reports the plant on every input has certified
    nothing.
    """
    vals, uniform, _t = read_volScalarField(p_path)
    if vals is None:
        raise Refusal("cannot plant into a uniform field: %s (uniform %r).  "
                      "A solved p field is nonuniform; a uniform one means the "
                      "solver wrote nothing." % (p_path, uniform))
    original = list(vals)
    idx = len(vals) // 3          # BY INDEX, not by value: a plant chosen by
                                  # value can land on a cell that already
                                  # carries it and prove nothing.
    before = original[idx]
    tol = plant_tol(before)
    snap = ArtifactSnapshot(p_path)
    try:
        _atomic_write_text(p_path,
                           splice_scalar_value(snap.text(), idx, before + PLANT_PA))
        back, _, _ = read_volScalarField(p_path)
        seen = back[idx] - before
        if abs(seen - PLANT_PA) > tol:
            refuse("PLANTED CONTROL DID NOT FIRE: planted %.6g Pa into cell %d "
                   "of %s and the reader read back %.6g.  A zero from a reader "
                   "not shown able to see a non-zero is not evidence."
                   % (PLANT_PA, idx, p_path, seen))
        # NEGATIVE LIMB -- restore, and the reader must NOT still report it.
        snap.restore()
        twin, _, _ = read_volScalarField(p_path)
        if abs(twin[idx] - before) > tol:
            refuse("PLANTED CONTROL NEGATIVE LIMB FAILED: after restoring the "
                   "field the reader still reports %.6g at cell %d.  A reader "
                   "that reports the plant on every input passes a fire-only "
                   "test and is worthless." % (twin[idx] - before, idx))
        if len(twin) != len(original) or any(a != b for a, b in zip(twin, original)):
            refuse("the plant did not restore the field value-for-value; the "
                   "case's own p field has been altered and is no longer evidence")
    finally:
        # Restore under EVERY exit, refusal and exception included.  The
        # superseded file left the field perturbed on some paths.
        snap.restore()
    ident = snap.verify_unchanged("the planted control on read_volScalarField")
    return {"plant_Pa": PLANT_PA, "cell_index": idx,
            "fired": True, "unperturbed_twin_silent": True,
            "artifact_byte_identical": True, "artifact": ident,
            "field": os.path.abspath(p_path)}


def plant_into_function_object(case, name, column, end_time, age_ref):
    """THE PLANT THAT WAS MISSING, on THE READER THAT ACTUALLY GRADES.

    C1's `delta_p`, C2's `mdot`, C4's re-measured `delta_p` and section 6.3's
    `T_total` ALL arrive through `function_object_series`, and in the superseded
    file that reader had no planted control of any kind.  This perturbs a known
    row of the REAL `.dat` file on disk, reads it back through THE SAME CALL the
    graded quantity comes through, refuses if it does not come back, restores
    the file BYTE-EXACTLY, and REQUIRES THE NEGATIVE LIMB.

    BY ROW AND COLUMN INDEX, never by value: the row is the LAST data line --
    the one the reader returns -- and the column index is resolved once from the
    header.  A plant chosen by value can land on a datum that already carries it.
    """
    filename = FO_GRADED[name][0]
    row, path = _select_fo_row(case, name, filename, end_time, age_ref)
    if row is None:
        raise Refusal("cannot plant into `%s`: no postProcessing/%s under %s"
                      % (name, name, case))
    if column not in row:
        raise Refusal("cannot plant into `%s`: no %r column; columns: %s"
                      % (name, column, sorted(row)))
    snap = ArtifactSnapshot(path)
    lines = snap.text().splitlines(keepends=True)
    hdr_i = max(i for i, ln in enumerate(lines) if ln.startswith("#"))
    dat_i = max(i for i, ln in enumerate(lines)
                if ln.strip() and not ln.startswith("#"))
    cols = lines[hdr_i].lstrip("#").split()
    ci = cols.index(column)
    before = float(re.findall(r"\S+", lines[dat_i])[ci])
    tol = plant_tol(before)
    a, b = _token_spans(lines[dat_i])[ci]
    try:
        planted = list(lines)
        planted[dat_i] = (lines[dat_i][:a] + repr(before + PLANT_FO)
                          + lines[dat_i][b:])
        _atomic_write_text(path, "".join(planted))
        back, _p = _select_fo_row(case, name, filename, end_time, age_ref)
        seen = back[column] - before
        if abs(seen - PLANT_FO) > tol:
            refuse("PLANTED CONTROL ON function_object_series DID NOT FIRE: "
                   "planted %.6g into column %r (index %d) of the last row of "
                   "%s and the reader read back a change of %.6g.  EVERY "
                   "GRADED NUMBER IN THIS CASE COMES THROUGH THIS READER, and a "
                   "zero from a reader not shown able to see a non-zero is not "
                   "evidence." % (PLANT_FO, column, ci, path, seen))
        snap.restore()
        twin, _p = _select_fo_row(case, name, filename, end_time, age_ref)
        if abs(twin[column] - before) > tol:
            refuse("PLANTED CONTROL ON function_object_series NEGATIVE LIMB "
                   "FAILED: after restoring %s the reader still reports a "
                   "change of %.6g in column %r.  A reader that reports the "
                   "plant on every input passes a fire-only test and is "
                   "worthless." % (path, twin[column] - before, column))
    finally:
        snap.restore()
    ident = snap.verify_unchanged(
        "the planted control on function_object_series")
    return {"function_object": name, "file": os.path.abspath(path),
            "column": column, "column_index": ci, "row": "last",
            "plant": PLANT_FO, "value_before": before,
            "fired": True, "unperturbed_twin_silent": True,
            "artifact_byte_identical": True, "artifact": ident}


def plant_into_fvoptions(case):
    """C3 arm (b), half one: the planted control on `read_fvoptions_source`.

    C3 arm (b) is a GRADED number and it does not pass through
    `function_object_series` at all -- it is `read_fvoptions_source` +
    `cell_volumes`.  Both halves therefore need their own control, or arm (b)
    reproduces exactly the defect this repair exists to close.  The source
    x-component is perturbed IN PLACE BY THE REGEX GROUP'S OWN SPAN, so the
    plant addresses the same bytes the reader reads.
    """
    path = os.path.join(case, "constant", "fvOptions")
    src0 = read_fvoptions_source(case)
    before = src0["Su"][0]
    tol = plant_tol(before)
    snap = ArtifactSnapshot(path)
    text = snap.text()
    # The span is located in the COMMENT-FREE view and spliced into the RAW
    # bytes; `_strip_foam_comments` preserves offsets so the two agree.  Via
    # `sole_entry`, so the plant addresses the SAME single entry the reader
    # resolved -- a plant that silently picked a different match would certify
    # bytes nothing grades.
    m = sole_entry(_SU_RE, _strip_foam_comments(text), "the U source vector",
                   path, "the planted control must address the entry the "
                   "reader resolved, not another match of the same shape.")
    a, b = m.span(1)
    try:
        _atomic_write_text(path, text[:a] + repr(before + PLANT_SU) + text[b:])
        seen = read_fvoptions_source(case)["Su"][0] - before
        if abs(seen - PLANT_SU) > tol:
            refuse("PLANTED CONTROL ON read_fvoptions_source DID NOT FIRE: "
                   "planted %.6g m/s^2 into the Su x-component of %s and the "
                   "reader read back a change of %.6g.  C3 ARM (b) IS COMPUTED "
                   "FROM THIS READER." % (PLANT_SU, path, seen))
        snap.restore()
        twin = read_fvoptions_source(case)["Su"][0]
        if abs(twin - before) > tol:
            refuse("PLANTED CONTROL ON read_fvoptions_source NEGATIVE LIMB "
                   "FAILED: after restoring %s the reader still reports a "
                   "change of %.6g." % (path, twin - before))
    finally:
        snap.restore()
    ident = snap.verify_unchanged("the planted control on read_fvoptions_source")
    return {"reader": "read_fvoptions_source", "file": os.path.abspath(path),
            "plant_m_s2": PLANT_SU, "Su_x_before": before,
            "fired": True, "unperturbed_twin_silent": True,
            "artifact_byte_identical": True, "artifact": ident}


def _zone_volume(case, zone_name):
    vol = cell_volumes(case)
    return sum(vol[i] for i in read_cellzone(case, zone_name))


def plant_into_points(case, zone_name="disk"):
    """C3 arm (b), half two: the planted control on `cell_volumes`.

    A point of a cell IN THE GRADED ZONE is moved by a known distance and the
    zone volume the REAL reader returns must CHANGE.  The magnitude of the
    change is NOT predicted and NOT compared to anything -- predicting it would
    re-derive the reader inside its own control.  What is asserted is that the
    reader is not blind (the volume moves) and not stuck (after a byte-exact
    restore the volume returns EXACTLY, bit for bit, because the arithmetic is
    deterministic on identical input bytes).

    THE POINT MUST BE ON THE ZONE BOUNDARY, and this is not a detail.  A point
    whose every touching cell lies INSIDE the zone is interior to it: moving
    such a point takes volume from one zone cell and gives exactly that volume
    to another, and THE ZONE TOTAL IS CONSERVED EXACTLY.  MEASURED on the F28 L1
    mesh while building this control: point 23253 is shared by cells 11384 and
    11385, both in the `disk` zone, and moving it 1.0e-05 m in x changed the
    zone volume by EXACTLY ZERO.  A plant placed there refuses a HEALTHY reader
    -- a false alarm, which is as much a broken control as a false clear.  The
    point is therefore the LOWEST-INDEXED point of the zone that has at least
    one touching cell OUTSIDE it, which is deterministic and boundary-crossing.
    """
    pm, pts, faces, own, nei = _read_polymesh(case)
    zone = set(read_cellzone(case, zone_name))
    touch = {}
    for fid, f in enumerate(faces):
        cells = [own[fid]] + ([nei[fid]] if fid < len(nei) else [])
        for pnt in f:
            touch.setdefault(pnt, set()).update(cells)
    zone_points = sorted({pnt for fid, f in enumerate(faces)
                          if own[fid] in zone
                          or (fid < len(nei) and nei[fid] in zone)
                          for pnt in f})
    pid = next((p for p in zone_points if not touch[p] <= zone), None)
    if pid is None:
        refuse("cellZone %r has no point with a touching cell outside it -- "
               "every candidate is interior, where a displacement conserves the "
               "zone volume exactly and the plant could not distinguish a live "
               "reader from a dead one.  REFUSING rather than planting a control "
               "that cannot fire." % zone_name)
    path = os.path.join(pm, "points")
    snap = ArtifactSnapshot(path)
    v0 = _zone_volume(case, zone_name)
    try:
        _atomic_write_text(path,
                           splice_point_x(snap.text(), pid, pts[pid][0] + PLANT_DX))
        v1 = _zone_volume(case, zone_name)
        if v1 == v0:
            refuse("PLANTED CONTROL ON cell_volumes DID NOT FIRE: point %d of "
                   "%s -- a point of the %r cellZone -- was moved %.6g m in x "
                   "and the zone volume read back UNCHANGED at %.17g m^3.  C3 "
                   "ARM (b) IS COMPUTED FROM THIS READER, and a reader that "
                   "cannot see the mesh move has certified nothing."
                   % (pid, path, zone_name, PLANT_DX, v0))
    finally:
        snap.restore()
    v2 = _zone_volume(case, zone_name)
    if v2 != v0:
        refuse("PLANTED CONTROL ON cell_volumes NEGATIVE LIMB FAILED: after a "
               "byte-exact restore of %s the zone volume is %.17g where it was "
               "%.17g.  The reader is not a function of the bytes on disk."
               % (path, v2, v0))
    ident = snap.verify_unchanged("the planted control on cell_volumes")
    return {"reader": "cell_volumes", "file": os.path.abspath(path),
            "point_index": pid, "plant_dx_m": PLANT_DX, "zone": zone_name,
            "zone_volume_m3": v0, "zone_volume_perturbed_m3": v1,
            "fired": True, "unperturbed_twin_silent": True,
            "artifact_byte_identical": True, "artifact": ident}


# =============================================================================
# THE MEASUREMENTS
# =============================================================================
def disk_pressure_rise(case, tdir, end_time, age_ref):
    """Area-averaged static pressure rise ACROSS the disk zone, from the
    written `p` field, read through the real reader.  C1's quantity.

    `simpleFoam` carries KINEMATIC pressure (p/rho, m^2/s^2), so the reader
    multiplies by RHO to get Pa.  Getting THAT wrong is another silent factor
    of 1.2 and it is why the multiplication is written here once, named.
    """
    p_path = os.path.join(tdir, "p")
    vals, uniform, _ = read_volScalarField(p_path)
    if vals is None:
        raise Refusal("p at %s is uniform %r -- the solver wrote no field"
                      % (tdir, uniform))
    zone = read_cellzone(case, "disk")
    vol = cell_volumes(case)
    if len(vals) != len(vol):
        raise Refusal("p carries %d values and the mesh has %d cells"
                      % (len(vals), len(vol)))
    # Upstream and downstream neighbours of the zone are needed for a JUMP.
    # The zone is one block thick in x by construction (section 5 / the mesh
    # generator), so the jump is taken between the cells immediately upstream
    # and downstream of the zone in the same radial band.  Those are supplied
    # by the run's own `surfaceFieldValue` function objects; this reader
    # consumes their written output rather than re-deriving a topology.
    # TWO SEPARATE function objects, because that is how OpenFOAM writes them:
    # each `surfaceFieldValue` owns its own `postProcessing/<name>/<t>/
    # surfaceFieldValue.dat` with a single `areaAverage(p)` column.  A reader
    # that expected one file with two suffixed columns would find neither.
    up_row = function_object_series(case, "diskPlaneUp",
                                    FO_GRADED["diskPlaneUp"][0], end_time, age_ref)
    dn_row = function_object_series(case, "diskPlaneDown",
                                    FO_GRADED["diskPlaneDown"][0], end_time, age_ref)
    if up_row is None or dn_row is None:
        raise Refusal("C1 needs BOTH `diskPlaneUp` and `diskPlaneDown` "
                      "surfaceFieldValue output under %s/postProcessing; got "
                      "%r / %r" % (case, up_row is not None, dn_row is not None))
    col = "areaAverage(p)"
    for nm, row in (("diskPlaneUp", up_row), ("diskPlaneDown", dn_row)):
        if col not in row:
            raise Refusal("%s carries no %s column; columns: %s"
                          % (nm, col, sorted(row)))
    if abs(up_row["Time"] - dn_row["Time"]) > 1e-9:
        raise Refusal("the two disk planes were written at different times "
                      "(%g vs %g) -- they are not the same solution"
                      % (up_row["Time"], dn_row["Time"]))
    up, dn = up_row[col], dn_row[col]
    return {"delta_p_measured_Pa": RHO * (dn - up),
            "p_upstream_kinematic": up, "p_downstream_kinematic": dn,
            "rho_used": RHO, "zone_cells": len(zone)}


def _parse_fo_file(path):
    """Header columns and the LAST data row of one function-object file."""
    hdr, last = None, None
    for line in open(path, errors="replace"):
        if line.startswith("#"):
            hdr = line
        elif line.strip():
            last = line
    if hdr is None or last is None:
        return None
    cols = hdr.lstrip("#").split()
    vals = last.split()
    if len(cols) != len(vals):
        raise Refusal("%s: %d header columns, %d data columns -- the "
                      "reader will not guess the alignment"
                      % (path, len(cols), len(vals)))
    if "Time" not in cols:
        raise Refusal("%s carries NO `Time` column; columns: %s.  The "
                      "superseded reader scored such a file as `Time = 0` via "
                      "`row.get(\"Time\", 0)` and sorted it silently to the "
                      "bottom.  A reader that will not guess a COLUMN "
                      "ALIGNMENT must not guess a TIME either." % (path, cols))
    return dict(zip(cols, (float(v) for v in vals)))


def _select_fo_row(case, name, filename, end_time, age_ref):
    """The last row of `postProcessing/<name>/<t>/<filename>`, and its path.

    THE FILE IS NAMED, NEVER DISCOVERED.  The superseded reader iterated every
    file in every time directory in `os.listdir` order and broke ties with `>=`,
    so on equal `Time` the LAST-VISITED file won by OS iteration order.  A
    `forces` function object writes `force.dat` AND `moment.dat` side by side
    with identical column names and identical times, and MEASURED on
    `FEAS_L1_dp1000_U20_A2` that reader returned the MOMENT row.  Sorting alone
    does not fix it -- `moment.dat` sorts last and would still win.

    THE AGE GUARD (rule 4 clause 6) FIRES HERE, on exactly the files that carry
    the graded numbers, and the returned row's `Time` is checked against
    `endTime` (rule 4 clause 3, applied to the graded data instead of only to
    the time directory).
    """
    root = os.path.join(case, "postProcessing", name)
    if not os.path.isdir(root):
        return None, None
    tdirs = sorted(d for d in os.listdir(root)
                   if os.path.isdir(os.path.join(root, d)))     # DETERMINISTIC
    paths = [os.path.join(root, d, filename) for d in tdirs
             if os.path.exists(os.path.join(root, d, filename))]
    if not paths:
        present = sorted({f for d in tdirs for f in os.listdir(os.path.join(root, d))})
        raise Refusal("no %r under any time directory of %s; the files present "
                      "are %s.  The graded file is NAMED, never discovered: a "
                      "`forces` function object writes force.dat AND moment.dat "
                      "with IDENTICAL column names, and choosing between them by "
                      "directory-iteration order is how a MOMENT gets graded as "
                      "a FORCE." % (filename, root, present))

    t0 = os.path.getmtime(age_ref)
    rows = {}
    for p in paths:
        mt = os.path.getmtime(p)
        if mt <= t0:
            raise Refusal("clause 6 AGE GUARD ON THE GRADED DATA: %s is NOT "
                          "newer than %s (%.6f <= %.6f) -- it is function-object "
                          "output from a PREVIOUS run.  The superseded "
                          "comparator age-guarded only the fields inside the "
                          "time directory and never stat'd a function-object "
                          "file, while EVERY number it graded was read from one."
                          % (p, age_ref, mt, t0))
        row = _parse_fo_file(p)
        if row is not None:
            rows[p] = row
    if not rows:
        raise Refusal("every %r under %s is empty or headerless" % (filename, root))

    top = max(r["Time"] for r in rows.values())
    tied = sorted(p for p, r in rows.items() if r["Time"] == top)   # STRICT >
    if len(tied) > 1:
        first = rows[tied[0]]
        if any(rows[p] != first for p in tied[1:]):
            raise Refusal("AMBIGUOUS TIE AT Time = %g: %d files carry the same "
                          "final time with DIFFERENT rows -- %s.  A restart is "
                          "exactly how two series come to share a final time, "
                          "and the superseded reader let the winner be decided "
                          "by directory-iteration order.  REFUSING rather than "
                          "flipping a coin over a graded number."
                          % (top, len(tied), ", ".join(tied)))
    best, best_path = rows[tied[0]], tied[0]
    if abs(best["Time"] - end_time) > 1e-9:
        raise Refusal("%s: the last function-object row is at Time %g and the "
                      "run's endTime is %g.  Rule 4 clause 3 applied to THE "
                      "GRADED DATA: a series that does not reach endTime is not "
                      "the answer the run was allowed to produce, and the "
                      "superseded comparator checked no function-object time "
                      "against endTime anywhere."
                      % (best_path, best["Time"], end_time))
    return best, best_path


def function_object_series(case, name, filename, end_time, age_ref):
    """Last row of a function-object time series under `postProcessing/<name>`.

    `filename`, `end_time` and `age_ref` are REQUIRED and have no defaults, so
    no call site can reach this reader without naming the file it grades from
    and the two things that date it.
    """
    return _select_fo_row(case, name, filename, end_time, age_ref)[0]


def _flow_column(row, case):
    """The ONE `diskFlow` column C2 grades, or a refusal.

    `surfaceFieldValue` names the column after the operation, so it is
    `sum(phi)` or `areaNormalIntegrate(U)` depending on the entry, and the
    registration does not fix which.  It is therefore resolved from the header
    -- but resolved to EXACTLY ONE column.  The superseded file took `key[0]`
    from an unordered comprehension.
    """
    hits = sorted(c for c in row if c.startswith("sum(phi)")
                  or c.startswith("areaNormalIntegrate"))
    if len(hits) != 1:
        raise Refusal("the `diskFlow` flow column in %s is %s, not exactly one; "
                      "columns: %s" % (case, hits, sorted(row)))
    return hits[0]


def resolve_flow_column(case, end_time, age_ref):
    row = function_object_series(case, "diskFlow", FO_GRADED["diskFlow"][0],
                                 end_time, age_ref)
    if row is None:
        raise Refusal("no `diskFlow` surfaceFieldValue output under "
                      "%s/postProcessing" % case)
    return _flow_column(row, case)


def t_disk_analytic(delta_p):
    """(a) T_disk = delta_p * A_disk.  42.7256600888 N at 1000 Pa."""
    return delta_p * A_DISK


def t_disk_from_source(case, delta_p):
    """(b) The disk-zone momentum source INTEGRATED FROM THE CASE'S OWN INPUTS
    AND ITS OWN BUILT MESH, times WEDGE_SCALE.

    This arm touches `delta_p` ONLY through the frozen `fvOptions` value on
    disk.  It reads the source density the solver was actually handed, the
    actual cellZone, and the actual cell volumes, and applies the actual wedge
    factor.  So it disagrees with arm (a) if `volumeMode` is wrong, if
    `WEDGE_SCALE` is missing or wrong, if the source was written as a force
    density instead of an acceleration, or if the cellZone is not the registered
    rectangle.  THAT DISAGREEMENT IS THE WHOLE POINT OF C3.
    """
    src = read_fvoptions_source(case)
    zone = read_cellzone(case, "disk")
    vol = cell_volumes(case)
    v_zone = sum(vol[i] for i in zone)
    if v_zone <= 0.0:
        refuse("the disk cellZone has non-positive volume %g" % v_zone)
    # `volumeMode specific` => Su is a per-unit-volume ACCELERATION [m/s^2].
    # simpleFoam is incompressible, so the force is rho * Su * V.
    force_wedge = RHO * src["Su"][0] * v_zone
    force_full = force_wedge * WEDGE_SCALE
    expected_v = A_DISK * T_DISK / WEDGE_SCALE
    return {"T_disk_N": force_full,
            "wedge_force_N": force_wedge,
            "WEDGE_SCALE": WEDGE_SCALE,
            "source_Su_x_m_s2": src["Su"][0],
            "volumeMode": src["volumeMode"],
            "zone_volume_measured_m3": v_zone,
            "zone_volume_expected_m3": expected_v,
            "zone_volume_ratio": v_zone / expected_v,
            "expected_source_for_delta_p": delta_p / (RHO * T_DISK),
            "fvOptions": src["path"]}


def total_thrust(case, end_time, age_ref):
    """`T_duct` in NEWTONS, POSITIVE WHEN PROPULSIVE.

    Section 2.5: thrust is positive in -x, so every reported force is the -x
    component of the integrated force times -1, and then times WEDGE_SCALE
    because the `forces` function object integrates the WEDGE patches only and
    returns 5/360 of the full annular force (section 2.6).

    ONE quantity, named for what it is.  The superseded docstring promised
    "T_total, T_disk and T_duct" and the loop returned only `T_duct`, which
    `control_6_3` then consumed as `t_total`.  No number was wrong -- on an
    empty duct with no source the duct force IS the total, and the registration
    registers V(b)'s comparand on `forcesDuct` -- but a measurement script whose
    docstring names three quantities and returns one is how a later reader
    mis-cites the result.
    """
    out = {}
    for key, fo in (("T_duct", "forcesDuct"),):
        row = function_object_series(case, fo, FO_GRADED[fo][0], end_time, age_ref)
        if row is None:
            raise Refusal("no `%s` forces output under %s/postProcessing"
                          % (fo, case))
        hits = [c for c in row
                if c.startswith("total_x") or c == "Fx" or c.endswith("(x)")]
        if len(hits) != 1:
            raise Refusal("the x force column in %s is %s, not exactly one; "
                          "columns: %s.  The superseded reader took the FIRST "
                          "match and broke out of the loop, which is a choice "
                          "made by dictionary order over a graded number."
                          % (fo, hits, sorted(row)))
        out[key] = -row[hits[0]] * WEDGE_SCALE
    return out


# =============================================================================
# ADDENDUM 3's FLOORED THRUST STATIONARITY -- READER, CRITERION, FRAME PROOF
# AND PLANTED CONTROL
# =============================================================================
def _fo_window_values(case, name, filename, column, end_time, age_ref,
                      window=STATIONARITY_WINDOW_ITERS):
    """The last `window` values of ONE column of the graded function-object file.

    THE FILE IS THE ONE `_select_fo_row` ALREADY CHOSE, and it is chosen BY
    CALLING THAT FUNCTION rather than by repeating its logic.  Every guard the
    check-1 reads certified therefore fires here unchanged and without being
    touched: the file is NAMED not discovered, the clause-6 age guard runs on
    `postProcessing`, the strict-`>` tie refusal runs, and the last row is
    checked against `endTime`.  A second implementation of that selection would
    be a second thing to keep right, and it would drift.

    THE WINDOW IS THE LAST `window` DATA ROWS, which is `read_ptp_f28.py:64`'s
    `rows[-2000:]` exactly.  Section 8 and Addendum 3 both say "the last 2000
    ITERATIONS"; rows and iterations coincide only where the function object
    writes every iteration, which is true of every F28 arm on disk (15,000 rows
    for 15,000 iterations).  This reader follows the FROZEN READER's definition
    because Addendum 3 registers the criterion as "unchanged from
    `read_ptp_f28.py:8`", and it RECORDS the window's first and last `Time` and
    its sample count in the output so the two readings are visibly the same on
    any case where they are -- and visibly different on any case where they are
    not.  Nothing here decides that question; it reports it.

    A file with fewer than `window` rows REFUSES.  `read_ptp_f28.py:61` already
    refuses a short window -- "a short window is not the registered criterion" --
    and a comparator may not be more permissive than the reader whose
    definitions it inherits.
    """
    row, path = _select_fo_row(case, name, filename, end_time, age_ref)
    if row is None:
        raise Refusal("no `%s` output under %s/postProcessing" % (name, case))
    if column not in row:
        raise Refusal("`%s` carries no %r column; columns: %s"
                      % (name, column, sorted(row)))
    hdr, vals, times = None, [], []
    for line in open(path, errors="replace"):
        if line.startswith("#"):
            hdr = line
        elif line.strip():
            if hdr is None:
                raise Refusal("%s carries data before any header line" % path)
            cols = hdr.lstrip("#").split()
            f = line.split()
            if len(cols) != len(f):
                raise Refusal("%s: %d header columns, %d data columns -- the "
                              "reader will not guess the alignment"
                              % (path, len(cols), len(f)))
            if "Time" not in cols or column not in cols:
                raise Refusal("%s: header %s carries no %r/`Time` column"
                              % (path, cols, column))
            times.append(float(f[cols.index("Time")]))
            vals.append(float(f[cols.index(column)]))
    if not vals:
        raise Refusal("%s has no data rows" % path)
    if len(vals) < window:
        raise Refusal("%s carries %d data rows and the registered stationarity "
                      "window is %d (section 8; `read_ptp_f28.py:30`).  A SHORT "
                      "WINDOW IS NOT THE REGISTERED CRITERION -- "
                      "`read_ptp_f28.py:61` refuses it in those words, and this "
                      "comparator will not be more permissive than the reader "
                      "whose definitions Addendum 3 says it inherits."
                      % (path, len(vals), window))
    return vals[-window:], times[-window], times[-1], path


def _ptp_and_mean(values):
    """`ptp` and `T_mean` WITH `read_ptp_f28.py:8`'s DEFINITIONS AND ARITHMETIC.

    Addendum 3 section 3 registers the criterion "where `ptp = max(Fx) -
    min(Fx)` over the window and `T_mean = mean(Fx)` over the same window, BOTH
    UNCHANGED FROM `read_ptp_f28.py:8`".  So the mean is `sum(w) / len(w)` --
    plain left-to-right summation, the expression at `read_ptp_f28.py:65` -- and
    NOT `math.fsum`.  Compensated summation is a better estimator and a
    DIFFERENT REGISTERED QUANTITY, and "better" is not a licence to substitute
    one definition for another inside a frozen criterion.

    MEASURED, and disclosed because it bounds what this choice is worth: on all
    three arms on disk the two summations agree BIT FOR BIT, so no selftest limb
    can distinguish them and none claims to.  The definition is matched because
    it is the registered one, not because a difference was found.
    """
    lo, hi = min(values), max(values)
    mean = sum(values) / len(values)
    return lo, hi, mean, hi - lo


def stationarity_criterion(ptp, mean, quantity):
    """`ptp <= max( STATIONARITY_REL * |mean| , T_floor )` -- Addendum 3 s.3.

    THE FLOOR APPLIES TO THRUST AND TO NOTHING ELSE, and that is enforced here
    rather than trusted to call sites.  Addendum 3 section 3's final paragraph
    leaves the disk mass-flow stationarity row untouched: Sanaa's approval names
    the thrust floor, so a mass-flow floor is not derived, not registered and
    not in force.  A criterion function that accepted any caller's quantity
    would make the boundary a matter of who calls it, and the next reader
    grading a second row would inherit an unapproved gate change by
    copy-and-paste.  So the guard is IN THE CRITERION: `quantity` is required
    and is refused unless it is registered as floored.
    """
    if quantity not in FLOORED_QUANTITIES:
        refuse("THE ABSOLUTE STATIONARITY FLOOR IS NOT REGISTERED FOR %r.  "
               "Addendum 3 section 3, final paragraph: \"The disk mass-flow "
               "stationarity row of section 8 is NOT touched.  Sanaa's approval "
               "names the thrust floor.  A mass-flow floor is not derived, not "
               "registered and not in force.\"  The approval's width is the "
               "width of the change and no wider (CLAUDE.md rule 9).  The only "
               "floored quantity is %s; grade %r against the UNFLOORED "
               "criterion registered for it, or obtain an approval for a floor "
               "-- which no agent at any level may grant."
               % (quantity, " / ".join(repr(q) for q in FLOORED_QUANTITIES),
                  quantity))
    rel = STATIONARITY_REL * abs(mean)
    floor = STATIONARITY_FLOOR_SECTOR_N
    limit = max(rel, floor)
    # The limbs are joined by `max`, so the governing term is whichever is
    # larger.  A tie is reported as FLOOR, because the floor is the limb that
    # does not depend on the run -- reporting the run-dependent one on a tie
    # would name a term that could move under a re-read.
    governing = "FLOOR" if floor >= rel else "RELATIVE"
    return {"quantity": quantity,
            "criterion": "ptp <= max(%g * |T_mean|, T_floor)" % STATIONARITY_REL,
            "authority": "registration Addendum 3 section 3, in force; the "
                         "struck relative-only form is not evaluated",
            "frame": "5-degree SECTOR newtons (Addendum 3 section 5)",
            "window_iters": STATIONARITY_WINDOW_ITERS,
            "ptp_N": ptp, "T_mean_N": mean,
            "relative_limb_N": rel, "floor_limb_N": floor,
            "limit_N": limit, "governing_limb": governing,
            "floor_over_relative": (floor / rel) if rel > 0.0 else None,
            "ptp_over_limit": ptp / limit,
            "pass": ptp <= limit}


def thrust_stationarity(case, end_time, age_ref):
    """V(b)'s registered thrust-stationarity channel, IN SECTOR NEWTONS.

    Graded on the SAME file and the SAME column as `T_total` -- `forcesDuct`'s
    `force.dat`, `total_x` -- taken RAW, with no sign flip and no `WEDGE_SCALE`.
    `read_ptp_f28.py:53` takes the same column with no scale factor, and
    Addendum 3 section 5 registers the floor in that frame for that reason.
    `assert_stationarity_frame` then PROVES the frame instead of asserting it.
    """
    filename, column = FO_GRADED["forcesDuct"]
    vals, t_first, t_last, path = _fo_window_values(
        case, "forcesDuct", filename, column, end_time, age_ref)
    lo, hi, mean, ptp = _ptp_and_mean(vals)
    res = stationarity_criterion(ptp, mean, "thrust")
    res.update({"file": os.path.abspath(path), "column": column,
                "n_samples": len(vals),
                "window_first_Time": t_first, "window_last_Time": t_last,
                "window_Time_span": t_last - t_first + 1.0,
                "min_N": lo, "max_N": hi,
                "last_value_sector_N": vals[-1]})
    return res


def assert_stationarity_frame(st, t_total_N):
    """THE CLAUSE THE WHOLE CHANGE STANDS OR FALLS ON, PROVED NOT ASSERTED.

    Addendum 3 section 5 names the sector-versus-full-annulus frame as exactly
    that, and a slip is wrong BY A FACTOR OF 72 in the PERMISSIVE direction: the
    full-annulus floor 4.2726e-02 N applied to sector data would have RESCUED
    the zero-source arm (ptp 0.020422 N), which is the error that section exists
    to foreclose.  So the frame is not taken from `controlDict.template`'s
    comment, nor from this file's own docstrings.  It is proved by identity
    against THE ACTUAL GRADED COLUMN:

        `total_thrust` computes  T_total = -(raw `total_x` at endTime) * 72

    If the value THIS reader took from `total_x` at `endTime` reproduces the
    graded `T_total` BIT-EXACTLY under that one transformation, then this
    reader's series is the PRE-multiplication, PRE-sign-flip quantity -- sector
    newtons -- and it is the same column of the same file `T_total` came from.
    Bit-exact, not tolerant: both sides are the same product of the same two
    doubles, so anything but equality means a different column, a different
    file, a different row, or a scale factor that has crept in.
    """
    implied = -st["last_value_sector_N"] * WEDGE_SCALE
    if implied != t_total_N:
        refuse("SECTOR-FRAME PROOF FAILED, AND THE FLOOR IS UNUSABLE WITHOUT "
               "IT: the stationarity reader's last windowed sample is %.17g "
               "from column %r of %s, which implies T_total = %.17g N, and the "
               "graded T_total is %.17g N.  The stationarity floor "
               "%.9e N is registered in 5-DEGREE SECTOR NEWTONS (Addendum 3 "
               "section 5); the full-annulus value is %.4e N, a DIFFERENT "
               "NUMBER a factor of %g away, and applying it to sector data "
               "would move the criterion in the PERMISSIVE direction.  This "
               "comparator will not grade a floor whose frame it cannot prove."
               % (st["last_value_sector_N"], st["column"], st["file"],
                  implied, t_total_N, STATIONARITY_FLOOR_SECTOR_N,
                  STATIONARITY_FLOOR_FULL_N, WEDGE_SCALE))
    return {"identity": "T_total == -(last windowed total_x) * WEDGE_SCALE",
            "last_windowed_total_x_sector_N": st["last_value_sector_N"],
            "WEDGE_SCALE": WEDGE_SCALE,
            "implied_T_total_N": implied, "graded_T_total_N": t_total_N,
            "bit_exact": True,
            "frame_proved": "5-degree SECTOR newtons",
            "floor_sector_N": STATIONARITY_FLOOR_SECTOR_N,
            "floor_full_annulus_N_NOT_USED": STATIONARITY_FLOOR_FULL_N}


def plant_into_stationarity_window(case, end_time, age_ref,
                                   window=STATIONARITY_WINDOW_ITERS):
    """THE PLANTED CONTROL ON THE STATIONARITY WINDOW (standing rule 3).

    `plant_into_function_object` certifies the LAST row -- the one row
    `_select_fo_row` returns.  `ptp` and `T_mean` are graded numbers computed
    from `window` rows, and that control never touches `window - 1` of them, so
    it certifies the wrong thing here: a window reader that silently graded only
    the final row, or averaged some other set of rows, would sail through it.

    THIS plant therefore goes into THE FIRST ROW OF THE WINDOW -- inside the
    graded window, and the one row no other control in this file addresses.

    The displacement is `(max - min) + PLANT_FO`, and that is not a taste: it
    GUARANTEES a new maximum, because the perturbed sample is at least
    `min + (max - min) + PLANT_FO > max` wherever the chosen row sat in the
    range.  A plant whose visibility depends on the data is a control that can
    be silently absent on the next case.  TWO things must then move, and the
    second is the one that matters: `ptp` must increase (the reader is not
    blind), and `T_mean` must move by EXACTLY the displacement over the window
    (the reader averaged THE WINDOW and not some other set of rows -- an
    arithmetic identity a last-row-only or wrong-length reader cannot satisfy).
    The negative limb requires both to return EXACTLY after a byte-exact
    restore.
    """
    filename, column = FO_GRADED["forcesDuct"]
    before_stat = thrust_stationarity(case, end_time, age_ref)
    _row, path = _select_fo_row(case, "forcesDuct", filename, end_time, age_ref)
    snap = ArtifactSnapshot(path)
    lines = snap.text().splitlines(keepends=True)
    hdr_i = max(i for i, ln in enumerate(lines) if ln.startswith("#"))
    data_i = [i for i, ln in enumerate(lines)
              if ln.strip() and not ln.startswith("#")]
    if len(data_i) < window:
        raise Refusal("cannot plant into the stationarity window of %s: %d data "
                      "rows, window %d" % (path, len(data_i), window))
    tgt = data_i[-window]                   # THE FIRST ROW OF THE WINDOW
    cols = lines[hdr_i].lstrip("#").split()
    ci = cols.index(column)
    before = float(re.findall(r"\S+", lines[tgt])[ci])
    delta = (before_stat["max_N"] - before_stat["min_N"]) + PLANT_FO
    tol = plant_tol(max(abs(before), abs(delta), abs(before_stat["T_mean_N"])))
    a, b = _token_spans(lines[tgt])[ci]
    try:
        planted = list(lines)
        planted[tgt] = lines[tgt][:a] + repr(before + delta) + lines[tgt][b:]
        _atomic_write_text(path, "".join(planted))
        after = thrust_stationarity(case, end_time, age_ref)
        d_ptp = after["ptp_N"] - before_stat["ptp_N"]
        d_mean = after["T_mean_N"] - before_stat["T_mean_N"]
        if d_ptp <= 0.0:
            refuse("PLANTED CONTROL ON THE STATIONARITY WINDOW DID NOT FIRE: "
                   "%.6g was added to column %r (index %d) of the FIRST ROW OF "
                   "THE WINDOW (data row %d of %d) in %s -- a displacement "
                   "chosen to guarantee a new maximum -- and `ptp` read back "
                   "%.17g where it was %.17g.  V(b)'s registered stationarity "
                   "verdict is computed from this reader, and a zero from a "
                   "reader not shown able to see a non-zero is not evidence."
                   % (delta, column, ci, len(data_i) - window + 1, len(data_i),
                      path, after["ptp_N"], before_stat["ptp_N"]))
        if abs(d_mean - delta / window) > tol:
            refuse("PLANTED CONTROL ON THE STATIONARITY WINDOW AVERAGED THE "
                   "WRONG ROWS: %.6g was added to ONE row of the %d-row window "
                   "of %s, so `T_mean` must move by exactly %.6g and it moved "
                   "by %.6g (difference %.3e against tolerance %.3e).  `ptp` "
                   "moved, so the reader is not blind -- it is reading a "
                   "DIFFERENT SET OF ROWS than the registered window, which is "
                   "the failure a last-row plant cannot see."
                   % (delta, window, path, delta / window, d_mean,
                      abs(d_mean - delta / window), tol))
        snap.restore()
        twin = thrust_stationarity(case, end_time, age_ref)
        if (twin["ptp_N"] != before_stat["ptp_N"]
                or twin["T_mean_N"] != before_stat["T_mean_N"]):
            refuse("PLANTED CONTROL ON THE STATIONARITY WINDOW NEGATIVE LIMB "
                   "FAILED: after a byte-exact restore of %s the reader reports "
                   "ptp %.17g / mean %.17g where it reported %.17g / %.17g.  A "
                   "reader that reports the plant on every input passes a "
                   "fire-only test and is worthless."
                   % (path, twin["ptp_N"], twin["T_mean_N"],
                      before_stat["ptp_N"], before_stat["T_mean_N"]))
    finally:
        snap.restore()
    ident = snap.verify_unchanged(
        "the planted control on the stationarity window")
    return {"reader": "thrust_stationarity", "file": os.path.abspath(path),
            "column": column, "column_index": ci,
            "row": "first of the %d-row window" % window,
            "row_index_in_file": tgt, "window": window,
            "plant_N": delta, "value_before": before,
            "ptp_before_N": before_stat["ptp_N"], "ptp_planted_N": after["ptp_N"],
            "mean_shift_expected_N": delta / window,
            "mean_shift_observed_N": d_mean,
            "fired": True, "unperturbed_twin_silent": True,
            "artifact_byte_identical": True, "artifact": ident}


# =============================================================================
# SECTION 6.2 -- THE PLANTED CONTROL, C1..C4
# =============================================================================
def control_6_2(case_plant, case_baseline, case_c4, end_time, rc_plant,
                rc_baseline, rc_c4):
    res = {"section": "6.2", "conditions": {}}
    comp = completion(case_plant, os.path.join(case_plant, "log.simpleFoam"),
                      end_time, rc_plant)
    res["completion"] = comp
    tdir = comp["time_dir"]
    age = comp["age_ref"]

    # THE BASELINE IS A GRADED RUN AND IS NOW HELD TO THE COMPLETION RULE.
    # `rc_baseline` was an ACCEPTED AND UNUSED PARAMETER in the superseded file:
    # C2's comparand came off a run that was never checked for rc, an End line,
    # its endTime, its fields or its age.
    comp_base = completion(case_baseline,
                           os.path.join(case_baseline, "log.simpleFoam"),
                           end_time, rc_baseline)
    res["completion_baseline"] = comp_base
    age_base = comp_base["age_ref"]

    res["write_format"] = {
        "plant": assert_write_format(case_plant),
        "baseline": assert_write_format(case_baseline),
        "c4": assert_write_format(case_c4)}

    # THE PLANTS, before any number is believed -- ONE ON EVERY READER THAT
    # PRODUCES A GRADED NUMBER.  The superseded file planted only into
    # `read_volScalarField`, whose VALUE reaches none of them.
    res["planted_control"] = {
        "read_volScalarField": plant_into_p(os.path.join(tdir, "p")),
        "function_object_series": {
            "C1_diskPlaneUp": plant_into_function_object(
                case_plant, "diskPlaneUp", FO_GRADED["diskPlaneUp"][1],
                end_time, age),
            "C1_diskPlaneDown": plant_into_function_object(
                case_plant, "diskPlaneDown", FO_GRADED["diskPlaneDown"][1],
                end_time, age),
            "C2_diskFlow_loaded": plant_into_function_object(
                case_plant, "diskFlow",
                resolve_flow_column(case_plant, end_time, age), end_time, age),
            "C2_diskFlow_baseline": plant_into_function_object(
                case_baseline, "diskFlow",
                resolve_flow_column(case_baseline, end_time, age_base),
                end_time, age_base),
        },
        "read_fvoptions_source": plant_into_fvoptions(case_plant),
        "cell_volumes": plant_into_points(case_plant, "disk"),
    }

    # C1 -- pressure rise across the disk == delta_p within 2%
    dp = disk_pressure_rise(case_plant, tdir, end_time, age)
    err = abs(dp["delta_p_measured_Pa"] - DELTA_P_CTRL) / DELTA_P_CTRL
    res["conditions"]["C1"] = {
        "measured_delta_p_Pa": dp["delta_p_measured_Pa"],
        "registered_delta_p_Pa": DELTA_P_CTRL,
        "relative_error": err, "tolerance": TOL_C1,
        "pass": err <= TOL_C1, "detail": dp}

    # C2 -- disk mass flow positive AND increased over the delta_p = 0 baseline
    m_plant = function_object_series(case_plant, "diskFlow",
                                     FO_GRADED["diskFlow"][0], end_time, age)
    m_base = function_object_series(case_baseline, "diskFlow",
                                    FO_GRADED["diskFlow"][0], end_time, age_base)
    if m_plant is None or m_base is None:
        raise Refusal("C2 needs `diskFlow` surfaceFieldValue output on BOTH "
                      "the loaded case and the delta_p = 0 baseline")
    key = _flow_column(m_plant, case_plant)
    if key != _flow_column(m_base, case_baseline):
        raise Refusal("the loaded case grades `diskFlow` on column %r and the "
                      "baseline on %r -- C2 differences two different quantities"
                      % (key, _flow_column(m_base, case_baseline)))
    q_plant, q_base = m_plant[key], m_base[key]
    res["conditions"]["C2"] = {
        "mdot_loaded": q_plant, "mdot_baseline": q_base,
        "pass": q_plant > 0.0 and q_plant > q_base}

    # C3 -- T_disk two independent ways within 0.5%.  THE CLAUSE THAT CATCHES
    # THE FACTOR-72 WEDGE ERROR AND THE volumeMode FACTOR OF SECTION 2.4.
    ta = t_disk_analytic(DELTA_P_CTRL)
    tb = t_disk_from_source(case_plant, DELTA_P_CTRL)
    err3 = abs(tb["T_disk_N"] - ta) / ta
    res["conditions"]["C3"] = {
        "T_disk_analytic_N": ta, "T_disk_from_source_N": tb["T_disk_N"],
        "relative_error": err3, "tolerance": TOL_C3,
        "pass": err3 <= TOL_C3, "detail": tb}

    # C4 -- THE NEGATIVE LIMB.  The same L1 case is re-run with delta_p
    # deliberately mis-set by a factor of 2 (2000 Pa in fvOptions, 1000 Pa
    # asserted here).  C1 MUST REFUSE.  If the mis-set run passes C1 the
    # instrument is blind and THE ENTIRE CASE is NOT A RESULT.
    comp4 = completion(case_c4, os.path.join(case_c4, "log.simpleFoam"),
                       end_time, rc_c4)
    age4 = comp4["age_ref"]
    # C4 grades through the same reader on a DIFFERENT case, so it needs its own
    # planted control: a reader certified on the plant case is not thereby
    # certified on the C4 case's files.
    res["planted_control"]["function_object_series"]["C4_diskPlaneUp"] = (
        plant_into_function_object(case_c4, "diskPlaneUp",
                                   FO_GRADED["diskPlaneUp"][1], end_time, age4))
    res["planted_control"]["function_object_series"]["C4_diskPlaneDown"] = (
        plant_into_function_object(case_c4, "diskPlaneDown",
                                   FO_GRADED["diskPlaneDown"][1], end_time, age4))
    dp4 = disk_pressure_rise(case_c4, comp4["time_dir"], end_time, age4)
    err4 = abs(dp4["delta_p_measured_Pa"] - DELTA_P_CTRL) / DELTA_P_CTRL
    c1_would_pass = err4 <= TOL_C1
    res["conditions"]["C4"] = {
        "fvOptions_delta_p_Pa": DELTA_P_C4,
        "asserted_delta_p_Pa": DELTA_P_CTRL,
        "measured_delta_p_Pa": dp4["delta_p_measured_Pa"],
        "relative_error": err4, "tolerance": TOL_C1,
        "C1_refused_as_it_must": not c1_would_pass,
        "pass": not c1_would_pass}
    if c1_would_pass:
        refuse("C4 NEGATIVE LIMB: the run with delta_p MIS-SET BY A FACTOR OF "
               "2 still passed C1 (measured %.6g Pa against an asserted %.6g "
               "Pa, %.4f%% -- inside the %.1f%% tolerance).  THE INSTRUMENT IS "
               "BLIND AND THE ENTIRE CASE IS NOT A RESULT.  C4 is one-way: it "
               "can only withdraw confidence, never grant it."
               % (dp4["delta_p_measured_Pa"], DELTA_P_CTRL, 100 * err4,
                  100 * TOL_C1))

    res["verdict"] = ("GATE REACHED"
                      if all(c["pass"] for c in res["conditions"].values())
                      else "NOT A RESULT")
    return res


# =============================================================================
# SECTION 6.3 -- THE EMPTY-DUCT PASS-THROUGH, MAGNITUDE **AND SIGN**
# =============================================================================
def control_6_3(case_empty, t_total_loaded_N, end_time, rc_empty):
    comp = completion(case_empty, os.path.join(case_empty, "log.simpleFoam"),
                      end_time, rc_empty)
    age = comp["age_ref"]
    wf = assert_write_format(case_empty)
    src = read_fvoptions_source_or_none(case_empty, zero_source_expected=True)
    if src is not None and src["Su"][0] != 0.0:
        refuse("section 6.3 registers delta_p = 0, and constant/fvOptions "
               "carries a source of %g m/s^2" % src["Su"][0])
    # THE PLANT ON THE READER THAT PRODUCES `T_total`.  This is the reader that,
    # MEASURED, returned a MOMENT where the force file carries a force.
    plant = plant_into_function_object(case_empty, "forcesDuct",
                                       FO_GRADED["forcesDuct"][1], end_time, age)
    # THE SECOND PLANT ON THE SAME FILE, ON A DIFFERENT READER.  The control
    # above certifies the LAST ROW, which is all `T_total` needs; Addendum 3's
    # channel grades 2000 rows, and a control on one of them certifies nothing
    # about the other 1999.  Both fire before either number is believed.
    plant_window = plant_into_stationarity_window(case_empty, end_time, age)
    t = total_thrust(case_empty, end_time, age)
    t_total = t["T_duct"]
    frac = abs(t_total) / abs(t_total_loaded_N)
    ok_mag = frac < TOL_C6_3
    ok_sign = t_total < 0.0
    # ADDENDUM 3's FLOORED CRITERION, WIRED.  Addendum 3 section 6 grades V(b)
    # on it -- "not the struck relative-only form" -- under Sanaa's approval at
    # `5dd94f4f`.  The frame is PROVED against the graded column before the
    # criterion is read, because a floor evaluated in the wrong frame is wrong
    # by 72 in the permissive direction (Addendum 3 section 5).
    stat = thrust_stationarity(case_empty, end_time, age)
    frame = assert_stationarity_frame(stat, t_total)
    ok_stat = stat["pass"]
    res = {"section": "6.3", "U_inf_m_s": U_INF_PASS,
           "T_total_N": t_total, "T_total_loaded_reference_N": t_total_loaded_N,
           "fraction_of_loaded": frac, "tolerance": TOL_C6_3,
           "magnitude_pass": ok_mag, "sign_pass_must_be_drag": ok_sign,
           "thrust_stationarity": stat, "stationarity_pass": ok_stat,
           "sector_frame_proof": frame, "floor_derivation": FLOOR_DERIVATION,
           "completion": comp, "write_format": wf, "planted_control": plant,
           "planted_control_stationarity": plant_window,
           "verdict": ("GATE REACHED" if (ok_mag and ok_sign and ok_stat)
                       else "NOT A RESULT")}
    if not ok_sign:
        refuse("section 6.3: T_total = %+.6g N is POSITIVE with delta_p = 0.  "
               "Under section 2.5's convention that is NET THRUST FROM NOTHING. "
               "NOT A RESULT regardless of magnitude -- registering the SIGN as "
               "well as the magnitude closes the hole the directive's 'small' "
               "leaves open." % t_total)

    # ADDENDUM 3's CHANNEL IS NOW EVALUATED, so the refusal that stood here --
    # "SECTION 6.3 CANNOT BE GRADED BY THIS COMPARATOR" -- is struck.  It was
    # correct while the criterion was unwired: a `GATE REACHED` issued while a
    # REGISTERED channel went unevaluated is a verdict on a criterion that was
    # never applied.  It is now applied, its frame is proved, its floor is
    # derived and its reader carries its own plant, and an UNSTATIONARY V(b) is
    # reported as `NOT A RESULT` through the verdict field above rather than
    # through a refusal -- because stationarity is a REGISTERED CRITERION with a
    # threshold, not a defect in the instrument.  The comparator still refuses
    # (exit 2) for every instrument failure: a blind plant, an unprovable frame,
    # a floor that does not reproduce the registration, a short window.
    return res


def read_fvoptions_source_or_none(case, zero_source_expected=False):
    p = os.path.join(case, "constant", "fvOptions")
    if not os.path.exists(p):
        return None
    return read_fvoptions_source(case, zero_source_expected)


# =============================================================================
def main():
    sys.stderr.write(
        "F28 comparator.  This file is an INSTRUMENT.  It takes the three "
        "section 6.2 case directories, the section 6.3 case directory, their "
        "endTime and their solver rcs, and it REFUSES (exit 2) rather than "
        "degrading.  It has not been run for record: Stage 1 onward is gated "
        "behind the supervisor's check-1 read of this diff.\n")
    # THE CALL SITE `guard_virgin_case` NEVER HAD.  The guard implements section
    # 11.1's rule that no run in this case is ever started on top of an existing
    # time directory, and it can only be true where a run is STARTED -- by the
    # time the comparator sees a case the time directory MUST exist.  So it
    # belongs to the LAUNCHER, and this is the entry point the launcher calls:
    #
    #     python3 analyse_f28.py --guard-virgin "$RUN_DIR" || exit 1
    #
    # in run_f28.sh's ASSEMBLE phase, immediately after `PHASE="assemble"`
    # (run_f28.sh:228) and BEFORE the `mkdir -p "$RUN_DIR/system" ...` at
    # run_f28.sh:229 that creates `0`.  That launcher edit is NOT made by this
    # file and returns to the supervisor as its own diff.
    if len(sys.argv) >= 3 and sys.argv[1] == "--guard-virgin":
        guard_virgin_case(sys.argv[2])
        print(json.dumps({"guard": "guard_virgin_case", "case": sys.argv[2],
                          "result": "VIRGIN -- no `0` and no time directory",
                          "authority": "registration section 11.1"}, indent=2))
        sys.exit(0)
    if len(sys.argv) < 2 or sys.argv[1] != "--grade":
        sys.stderr.write(
            "usage: analyse_f28.py --grade <spec.json>\n"
            "       analyse_f28.py --guard-virgin <case_dir>\n"
            "  spec.json: {\"case_plant\":..., \"case_baseline\":..., "
            "\"case_c4\":..., \"case_empty\":..., \"endTime\":..., "
            "\"rc\":{...}, \"T_total_loaded_N\":...}\n")
        sys.exit(2)
    spec = json.load(open(sys.argv[2]))
    out = {"case": "F28_DUCTED_ACTUATOR_DISK",
           "disclosure": "Actuator-disk representation; no rotor.",
           "registration": "verification/campaign/"
                           "F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md"}
    try:
        out["V_a_planted_control"] = control_6_2(
            spec["case_plant"], spec["case_baseline"], spec["case_c4"],
            spec["endTime"], spec["rc"]["plant"], spec["rc"]["baseline"],
            spec["rc"]["c4"])
        out["V_b_pass_through"] = control_6_3(
            spec["case_empty"], spec["T_total_loaded_N"], spec["endTime"],
            spec["rc"]["empty"])
    except Refusal as e:
        refuse(str(e))
    both = (out["V_a_planted_control"]["verdict"] == "GATE REACHED"
            and out["V_b_pass_through"]["verdict"] == "GATE REACHED")
    out["verdict"] = "GATE REACHED" if both else "NOT A RESULT"
    out["note"] = ("Section 9.2: BOTH controls must pass before any gated solve "
                   "is launched.  Either failing is NOT A RESULT for the case.")
    print(json.dumps(out, indent=2, sort_keys=True))
    sys.exit(0 if both else 1)


if __name__ == "__main__":
    main()
