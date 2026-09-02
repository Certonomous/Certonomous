# T23G2 comparator — MUTATION SET, REGISTERED BEFORE EXECUTION
# heat-transfer lab-lane, 2026-09-02.  Written and frozen BEFORE any mutation was run.
# Control: scratch copy of the real tree; baseline exit 3, RUNG VERDICT NOT A RESULT.
#
# KILL CRITERION (fixed here, before running):
#   A mutation is KILLED if the mutated instrument set STOPS or CONTRADICTS:
#     - the comparator refuses (exit 2) with a message naming the defect; or
#     - mark_done returns NOT DONE (1) / REFUSE (2) and require_done refuses; or
#     - the owning --selftest reports FAIL on the mutated code; or
#     - a gate verdict moves in the RESTRICTIVE direction because the guard fired.
#   A mutation SURVIVES if the set completes with no refusal, no selftest failure,
#   and the defect is not named anywhere in the output.
#
# DIRECTION:
#   S = STRICT      would make a sound run look unsound / corrupts an artifact.
#   P = PERMISSIVE  would let an unsound run be graded, or move a verdict toward PASS.
#                   A permissive survivor is the severe class.

## FAMILY A — rule 4 completion, ARTIFACT mutations (detector: require_done -> mark_done_t23.py)
A1  S  L1 STATUS.T23G2_L1 rewritten with rc=1            -> conjunct 1, CRASH branch
A2  S  L2 log.solve: the single `End` line deleted        -> conjunct 2 (and derived-rc)
A3  S  L3 endTime dir 24000 deleted                       -> conjunct 3, last time != endTime
A4  S  L3 24000/housing/p deleted                         -> conjunct 4, per-region field tuple
A5  S  L1 0/housing/T touched NEWER than 6000 fields      -> conjunct 6, THE AGE GUARD
A6  S  mark_done invoked on T23G2_L4 (not in CASES)       -> allow-list refusal, exit 2
A7  S  L1 STATUS file deleted                             -> read_status refusal (K0d L1)
A8  S  L1 log.solve gains one extra ExecutionTime line    -> conjunct 5, count == endTime/deltaT

## FAMILY B — rule 4 completion, CODE mutations of mark_done_t23.py (detector: its --selftest)
B1  P  age guard neutered: `getmtime(...) < age` -> `< 0`   -> selftest "age guard" drive
B2  P  launcher_rc accepted as rc                           -> selftest planted controls
B3  P  End-line check neutered: `n_end != 1` -> `n_end < 0`  -> selftest "two End lines"
B4  P  NEEDED gutted to {"fluid": ("T",), housing/core: ()}  -> selftest per-region control
B5  P  endTime tolerance widened: `> 1e-9` -> `> 1e9`        -> selftest "last time 9000"
B6  P  run() ignores `fails`, always EXIT_OK + writes marker -> every selftest drive
B7  P  read_status returns {} instead of refusing on absence -> selftest "STATUS absent"

## FAMILY C — rule 5, CODE mutations of roache_triple.py (detector: --selftest, _seal)
C1  P  NOT_A_RESULT_STATES = ()  -> non-CONVERGING triples graded on the band
C2  P  step (b) sets row["verdict"] = bv instead of NOT A RESULT
       -> a DIRECT attempt to move NOT A RESULT back to PASS.  _seal is the named guard.
C3  P  gci_equal's OSCILLATORY branch also returns GCI_pct/GCI_abs
       -> a GCI quoted beside a NON-MONOTONE triple.  _seal's GCI check is the named guard.
C4  P  band_verdict's no-band refusal removed -> returns PASS on an infinite band
C5  P  assert_plant_control never refuses on passed=False
C6  P  STAGNANT_FLOOR = 0.0   (STAGNANT retired)
C7  P  P_MIN = 0.0            (DEGENERATE retired)
C8  S  FS = 3.0               (GCI inflated)
C9  P  C2 PLUS _seal's one-way check disabled — the paired control that says which
       of the two guards is actually load-bearing.

## FAMILY D — R5 planted-zero controls, CODE/ARTIFACT (detector: the comparator's own controls)
D1  P  yplus_from_fields ignores u_path (reads the frozen U always)
       -> control_yplus_field_reader's `a == b` IDENTICAL-value refusal
D2  P  yplus_from_log ignores `path` (reads the frozen log always)
       -> control_yplus_log_reader -> external_plant_control delta 0 -> assert refusal
D3  P  plant_control_for re-reads the ORIGINAL file, not the planted temp
       -> RT.assert_plant_control in all_quantity_plant_controls
D4  P  D3 PLUS the assert removed from all_quantity_plant_controls
       -> tests whether g_ratio's own assert_plant_control is a real SECOND line of defence
D5  P  g_ratio called with control=None on the exact-zero branch
       -> g_ratio's explicit "NO planted-zero control was supplied" refusal
D6  P  _plant_u_file scale -> 1 + 2*PLANT, expectation left at sqrt(1+PLANT)
       -> "saw SOMETHING but not the planted quantity" refusal
D7  P  _plant_u_file's "matched NO vector" refusal removed AND scale set to 1.0
       -> a VACUOUS plant; the `a == b` refusal is the named guard
D8  P  YPLUS_PLANT_TOL_REL = 1.0, paired with D6 -> is the tolerance load-bearing?
D9  P  ARTIFACT: every y+ in L3 log.yPlus.fluid zeroed
       -> yplus_from_log's perfect-zero refusal
D10 P  D9 PLUS the perfect-zero refusal removed
       -> the 2 % instrument-disagreement refusal is the named second guard

## FAMILY E — G-ORDER (REPAIR R3)
E1  S  ORDER_BAND = (2.5, 3.5) on the real CONVERGING Q4 triple (p = 0.6111)
       -> G-ORDER must return GATE FAIL and that must reach the rollup (R3 reachability)
E2  P  Q4 dropped from the graded loop -> gate_order's "no row for it was graded" refusal
E3  P  gate_order returns PASS where the triple is not CONVERGING
       -> an unevaluated gate reported as a passed one

## FAMILY F — G-BAND / REPAIR R4
F1  P  BAND_TRANSFER_REGISTERED widened to include Q4 and Q6
       -> Q4/Q6 keep an UNREGISTERED band PASS instead of being downgraded
F2  S  BAND_TRANSFER_REGISTERED narrowed to ("Q1",) -> Q3/Q2 wrongly downgraded
F3  P  the downgrade line in _apply_band_registration deleted
       -> the row keeps its unregistered band verdict

## FAMILY G — G-MESHSIM
G1  S  CELLS["T23G2_L2"] = 90721 -> "the mesh that ran is not the mesh registered"
G2  S  ARTIFACT: L2 fluid polyMesh owner mutated so nCells differs -> same refusal, mesh side
G3  P  MESHSIM_CELL_TOL = 1.0 -> the 2.25 similarity ratio check neutered
G4  P  the total-cells refusal downgraded to a note, carrying G2's mutated mesh
       -> do the ratio checks catch what the total check would have?

## FAMILY H — G-CONV
H1  S  UX_EXCLUSION_MAX = 1e-30 -> the measurement no longer supports the Ux exclusion
H2  S  ARTIFACT: L1 6000/fluid/U given a large Ux -> ratio above 1e-12 from the artifact side
H3  P  RESID_TOL["h"] = 1.0 -> Sanaa's tightened 1e-9 criterion gutted

## FAMILY I — R2 grading-path recorder
I1  S  T23G2_PREREGISTRATION.md removed -> "grading-path member is not on disk" refusal
I2  S  mark_done_t23.py removed          -> same refusal, and require_done should also refuse
I3  P  GRADING_PATH shrunk to four entries (mark_done dropped)
       -> is the widened five-file list guarded by anything?

## FAMILY J — the transcribed-constant class (the control for that class)
J1  P  BAND_Q1 = (-1e9, 1e9)
J2  P  RATIO_MIN = 0.0
J3  P  PLATEAU_MAX_SPREAD_K = 1e9
J4  P  YPLUS_MAX = 1e9

# TOTAL REGISTERED: 54.  S = 18, P = 36.
# __pycache__ is deleted before EVERY run (stale bytecode inverts mutation tests).
