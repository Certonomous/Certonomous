# Curriculum D6RF7 — A2-wing convergence probe `P_conv`, the GRADING-PATH-SURVIVAL successor to D6RF6 (BLOCKED)

Supersedes: D6RF6 — A2-wing convergence probe `P_conv`, **BLOCKED** (a HARNESS defect, not physics): the baseline primal reached `End`, then hit DAFoam's physically-EXPECTED post-`End` `Primal solution failed!` (p first-solve `initRes 1.6256e-05` > the `1.0e-05` accept floor). D6RF6's guard correctly caught the raise and STILL wrote the product — but with `points={}` and `primal_raised=True`. The section-3e planted-CD control (`d6rf6_cd_plant_control.py:172` `run_cd_control`) returned `NOT_EXERCISED` **only for a FILE-ABSENT** artefact, not for a PRESENT-BUT-EMPTY one, so it hard-**REFUSED** at `read_cd(cl05)` (`REFUSE:PLANT_CD`, `points_present=[]`) inside `run_planted_controls`, which runs BEFORE `gate_conv`. Grading therefore aborted (rc 2) and never reached G-CONV. Evidence (reproduced): `python3 d6rf6_grade.py --root /home/ubuntu/certonomous-runs/CURRICULUM-D6RF6-a2-wing-convergence-probe --skip-freeze` → `rc=2 REFUSE PLANT_CD → CD_READER point_absent cl05 points_present=[]`.

**PERMISSION = NOT_FROZEN.** This is a lane's prediction-first proposal. Nothing here is a registration until
the dafoam-supervisor replaces the `PERMISSION` placeholder in `d6rf7_run_arm.sh` with a pre-registration
sha (CLAUDE.md rule 2), after the supervisor's non-delegable check-1 of the grade.py + control DELTAS.
The freeze and the enqueue belong to the supervisor and are not taken here.
**No gate, threshold, cap or label below may be altered after first compute** (rule 2); before first
compute this file is amendable, and any amendment must state the condition and how it was checked.

---

## 0. WHY A SUCCESSOR AT ALL — the defect is in the harness, not the physics

D6RF6's `P_conv` arm produced the correct physics (guard fired, product written) and then the GRADER
**crashed on the predicted failure path**. The physics is confirmed in the raw log, both legs:
`p_first_uncorrected 1.6256e-05` (LIMITED + 3 correctors, L1) and `1.6583e-05` (D6RF4-original scheme, L3),
both **over** the `1.0e-05` floor — Fix #1 (limited corrected 0.333) + Fix #2 (`nNonOrthogonalCorrectors 3`)
are **insufficient** for the A2-wing binding field. The correct GRADED verdict is **G-CONV GATE FAIL**; the
D6RF6 harness simply could not survive the failure path to produce it.

Under rule 2, D6RF6 has COMPUTED — its gates are closed and its frozen files are not edited. Its BLOCKED
record stands. **The fix is a SUCCESSOR** (this item, D6RF7), not an edit to the frozen D6RF6 files.

## 1. THE ONE CLASS OF DELTA — grading FAILURE-PATH handling

D6RF7 makes the **entire grading path SURVIVE** the expected present-but-empty (primal-raised) product and
produce a graded G-CONV verdict. **Nothing in the numerics, the scheme, the mesh, or any gate / threshold /
band / cap / accept-floor changes** (N-D43, T25). The LIMITED fvSchemes, the D6RF4-original fvSchemes, the
fvSolution (`nNonOrthogonalCorrectors 3`), `d6rf7_opt_runScript.py` and `d6rf7_endpoint_locus.py` are all
carried **byte-identical** (md5 unchanged: `137539e0…`, `341189ca…`, `8374443e…`, `cf8f745d…`, `67fed3c2…`).

The class comprises these sites, all in `d6rf7_grade.py` + `d6rf7_cd_plant_control.py`. **One detector**,
`cdc.points_empty_by_primal_raise` (added to the control module, consulted by the grader — asserted
identical by `imported_symbol_identity`), decides the present-but-empty state from the artefact
(`points` empty AND `primal_raised` truthy; **fail-closed** — an empty product WITHOUT `primal_raised` is NOT
excused and still refuses):

| # | Site | Assumption on empty points | D6RF6 behaviour | D6RF7 fix |
|---|------|----------------------------|-----------------|-----------|
| 1 | `cdc.read_cd` (leaf reader) | `point in points` | REFUSE `CD_READER point_absent, points_present=[]` | **unchanged** (leaf reader; callers detect empty first) |
| 2 | `cdc.run_cd_control` | reader returns a value | calls `read_cd` → `CDRefusal` | detect present-but-empty → **`NOT_EXERCISED`** (never refuse, never pass) |
| 3 | `run_planted_controls` control-3 (cd) | `run_cd_control` returns | catches `CDRefusal` → REFUSE `PLANT_CD` → **rc 2 BLOCK** | fixed via #2 (control returns `NOT_EXERCISED`) |
| 4 | `_cd_path` | file present ⇒ usable CD | returns the path | present-but-empty → **return `None`** → gates take their no-input branch |
| 5 | `gate_off` (`read_cd`) | CD readable | `read_cd` refuses → REFUSE `G-OFF` | via #4 → **NOT A RESULT** (`ARM_RAN_PRIMAL_RAISED_POINTS_EMPTY`) |
| 6 | `gate_price` (`read_cd cl05`) | CD readable | `read_cd` refuses → REFUSE `G-PRICE` | via #4 → **NOT A RESULT** (same token) |
| 7 | `report_cdlog` (`read_cd`) | CD readable | per-point NOT PRODUCED (already survivable) | via #4 → single clean NOT PRODUCED reason |
| 8 | `_no_input_reason` | arm RAN + no cdp ⇒ *not written* | would say `ARM_RAN_ARTEFACT_NOT_WRITTEN` (FALSE — file IS on disk) | new token **`ARM_RAN_PRIMAL_RAISED_POINTS_EMPTY`** (reads the artefact, never assumes) |
| 9 | `gate_fd` (`eta_used`) | primal produced a finite `eta_used` | `eta_used=NaN` → `NON_FINITE` → compose **rung 3 hoisted it above G-CONV**, masking it | detect empty BEFORE reading eta → **NOT A RESULT** (same token, NOT the non-finite reason) |
| 10 | `gate_conv` | reads p from the LOG, not points | INDEPENDENT of points (grades L1 p_first from log) | **no fix needed** — produces the GATE FAIL |
| 11 | `accept_floor_control` | reads tol from the LOG | INDEPENDENT of points | **no fix needed** (EXERCISED-PASS) |
| 12 | `finiteness_mutation` | selftest, own synthetic products | not on the graded runtime path | **no fix needed** |

Two further latent read-path defects were **exposed by the fixture** (D6RF6 never reached them because it
BLOCKed at #3) and folded into the same class, because without them grading survives but cannot produce the
predicted G-CONV verdict — both are grading-side only and touch NO threshold/gate/scheme:

- **(A) rank-duplicate LEG markers.** `d6rf7_fd_endpoint.py`'s `leg_say` writes stdout markers from EVERY
  MPI rank (only the jsonl `emit` is rank-guarded), so a 4-rank container prints 4 identical consecutive
  `LEG_BEGIN` per leg (`n_segments = 2 legs × 4 = 8`). `read_legs` bound L1/L2 to the first two — EMPTY
  rank-duplicates — so `gate_conv` read `SEGMENT_WITHOUT_RESIDUALS` and the failing residual sat in an
  UNBOUND segment. **Fix:** `read_legs` folds a consecutive `LEG_BEGIN` of the same tag+mode into the open
  empty segment (a rank duplicate), never starting a new one; a different tag/mode or one after content is a
  real new leg. Changes no gate; makes segmentation survive the real multi-rank container.
- **(B) stale falsifier mode name.** The producer emits `mode=F5_scheme` (`MODES`/`LEG_MODE`), but
  `read_legs`' `f5` filter and `NO_FD_MODES` still read the retired `F5_loose`, so L3 would never bind and
  F5 would read UNRESOLVED on a run that DID produce it. **Fix:** bind `f5` on `LEG_MODE["L3"]`;
  `NO_FD_MODES = ("P_conv", "F5_scheme")`.

Full diffs: `d6rf7_grade.py_DELTAS_from_d6rf6.diff`, `d6rf7_cd_plant_control.py_DELTAS_from_d6rf6.diff`
(the grading logic — the supervisor's non-delegable check-1 subject); `d6rf7_endpoint_physical.py_DELTAS_from_d6rf6.diff`,
`d6rf7_run_arm.sh_DELTAS_from_d6rf6.diff` (pin/PERMISSION re-points only).

## 2. THE REGISTERED PREDICTION

**G-CONV GATE FAIL** on L1 (the LIMITED-scheme cl04 baseline): binding field
`p_first_uncorrected initRes 1.6256e-05` = **1.626×** the `1.0e-05` accept floor; `nuTilda 1.408e-05`
(1.408×) also over floor. Fix #1 + Fix #2 are insufficient. F5 (falsifier at D6RF4's ORIGINAL scheme, L3)
lands **AS PREDICTED** — L3 also GATE FAIL (`p_first 1.6583e-05`), withdrawal clause does NOT fire, G-CONV
stands. The CD-dependent gates (G-OFF, G-PRICE, G-FD) and G-DVL read **NOT A RESULT for want of an input**
(P_conv is a one-arm convergence probe; it buys none of those arms). Planted controls: `price_control`
EXERCISED-PASS; `cd_control` and `fd_control` **NOT EXERCISED** (no refuse).

**Overall verdict = NOT A RESULT**, per the REGISTERED ladder (`compose` rung 6): a gated row NOT A RESULT
for want of input precedes rung 7 (GATE FAIL), and rule 5 fixes that direction — a NOT A RESULT can only
turn a PASS/GATE FAIL INTO a NOT A RESULT. The item's substantive result is the **G-CONV GATE FAIL**
disclosed in the per-gate breakdown; the overall is NOT A RESULT because a one-arm probe leaves the
FD/CD/off/price rows ungraded. (This corrects the loose "overall GATE FAIL" phrasing of the task brief:
the ladder — unaltered, NOT widened — yields overall NOT A RESULT with G-CONV GATE FAIL inside.)

## 3. FIXTURE VALIDATION — the load-bearing proof, NO re-solve

Built from the EXISTING D6RF6 run root (`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF6-a2-wing-convergence-probe`)
copied to scratch, products renamed `d6rf6_*→d6rf7_*`, log markers `D6RF6→D6RF7` (the deterministic D6RF7
run emits `D6RF7_*` markers; same scheme, same physics), ledger `ITEM=D6RF7`, then
`python3 d6rf7_grade.py --root <fixture> --out <json> --skip-freeze`:

- **grade rc = 0** (D6RF6 was rc 2). No refuse anywhere on the path.
- **G-CONV = GATE FAIL** on L1. Per-field: `p_first_uncorrected 1.625570732e-05` (ratio 1.6256, **GATE FAIL**),
  `nuTilda 1.408231801e-05` (ratio 1.408, **GATE FAIL**), `U0/U1/U2/he/p_corrected` all PASS (under floor).
- **F5 = AS PREDICTED**; L3 G-CONV GATE FAIL (`p_first 1.658293343e-05`); withdraws=False; G-CONV stands.
- **G-OFF / G-PRICE / G-FD = NOT A RESULT**, reason `ARM_RAN_PRIMAL_RAISED_POINTS_EMPTY`.
- **G-SCHEME = PASS**; **ACCEPT_FLOOR_UNMOVED = EXERCISED-PASS** (tol 1e-08 × diff 1000 = floor 1e-05, unmoved).
- **planted controls**: `cd_control NOT EXERCISED`, `fd_control NOT EXERCISED`, `price_control EXERCISED-PASS`.
- **overall = NOT A RESULT** (rung 6, want-of-input on G-DVL/G-FD/G-OFF/G-PRICE).

Control drives all green: `d6rf7_cd_plant_control.py --drive` rc 0 (direction 1 EXERCISED-PASS; 4 blind
readers REFUSED for their named reason; direction 3 absent → NOT EXERCISED; **direction 4** present-but-empty
+ primal_raised → NOT EXERCISED, and fail-closed on empty-without-primal_raised). `d6rf7_grade.py --selftest`
rc 0 (finiteness=0, accept_floor=0, cd_plant=0).

## 4. PIN FIXPOINT

`ALL_PINS_MATCH = TRUE`. Owned files that changed content (rename and/or edit) were re-pinned; files carried
byte-identical keep their D6RF6 md5:

| Pin | File | md5 | vs D6RF6 |
|-----|------|-----|----------|
| MD5_RUNSCRIPT6 / PRODUCER_MD5 / physical.MD5_RUNSCRIPT | `d6rf7_opt_runScript.py` | `137539e0…` | unchanged |
| MD5_LOCUS6 | `d6rf7_endpoint_locus.py` | `341189ca…` | unchanged |
| MD5_FVSCHEMES_LIMITED / grade.FVSCHEMES_MD5 | `d6rf7_fvSchemes_LIMITED` | `8374443e…` | unchanged |
| MD5_FVSCHEMES_ORIG / grade.FVSCHEMES_MD5 | `d6rf7_fvSchemes_D6RF4_ORIGINAL` | `cf8f745d…` | unchanged |
| MD5_FVSOL | `d6rf7_fvSolution` | `67fed3c2…` | unchanged |
| MD5_EXTRACT6 / physical.MD5_EXTRACT | `d6rf7_extract_endpoint.py` | `baedb673…` | re-pinned (rename) |
| MD5_PHYS6 | `d6rf7_endpoint_physical.py` | `625bacf5…` | re-pinned (rename + MD5_EXTRACT) |
| MD5_FD | `d6rf7_fd_endpoint.py` | `6f4c8bcd…` | re-pinned (rename) |
| MD5_UNITS | `d6rf7_units_assert.py` | `34f477f9…` | re-pinned (rename) |
| MD5_ANCHOR_GATE | `d6rf7_anchor_gate.py` | `c549ec2e…` | re-pinned (rename) |

**Real-base stager dry-run exit 0** (into a scratch base; registered root untouched, launches nothing):
"all 10 staged instrument md5s match the launcher's own pins", ceiling guard rc 0, ledger OK.

## 5. COST — costed est / cap (rule 12)

Single-variable change is grading FAILURE-PATH handling; no compute-physics change. A deterministic re-run
of the SAME scheme is registered at **est 62.0 / cap 186.0 core-min** (carried from D6RF6, unchanged). The
realised cost of a raised-primal P_conv run is small: **D6RF6 measured 12.133 core-min** (ledger row
`rc=0 wall_s=182 ranks=4`); D6RF7's expected realised is **~12–16 core-min**. Cost is derived at the
recorded c7a.4xlarge rate ($0.0513/core-h) and is **reported-by-owner, not measured** (the box cannot read
its own billing). Estimate-vs-actual calibration lands in `docs/COST_CALIBRATION.md` at process completion.

## 6. WHAT I COULD NOT VERIFY

- **Real-run G-CONV**: proven only on the FIXTURE (the D6RF6 log, deterministic same-scheme re-run). The
  official verdict requires the supervisor's freeze + re-run.
- **Pre-existing cap inconsistency (NOT in this DELTA, flagged for the supervisor):**
  `d6rf7_stage_root.sh` carries `ITEM_CEILING_CORE_MIN = ARM_CAP_CORE_MIN = 54.00` and a comment citing
  `CAPS = {"P_conv": 54.00}`, while `d6rf7_grade.py` registers `CAPS = {"P_conv": 186.00}`. Inherited
  byte-for-byte from D6RF6 (its stager exited 0 with the same values); the stager dry-run here exits 0 too.
  I did NOT change it — it is outside the failure-path DELTA and is a cap question (supervisor/Sanaa).
- **The producer's unguarded `leg_say`** (root cause of defect A) is left as-is; I fixed it grading-side in
  `read_legs` rather than re-pinning a compute instrument. The supervisor may prefer rank-guarding `leg_say`
  instead (would re-pin MD5_FD); I flag it for check-1.
