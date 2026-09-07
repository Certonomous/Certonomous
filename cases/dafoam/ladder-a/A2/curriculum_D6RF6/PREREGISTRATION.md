# Curriculum D6RF6 — A2-wing convergence probe `P_conv`, the HARNESS-SURVIVAL successor to D6RF5 (BLOCKED)

Supersedes: D6RF5 — A2-wing convergence probe `P_conv`, **BLOCKED** (a HARNESS defect, not physics): the baseline primal converged to `End` (CD 0.01849, CL 0.399) then hit DAFoam's physically-EXPECTED post-`End` `Primal solution failed!` (p first-solve `initRes 1.625570732e-05` > the `1.0e-05` accept floor), but the `P_conv` baseline primal was UNGUARDED (unlike the F5_scheme path), so the raise aborted the run before `d6rf5_fd_endpoint.json` was written and the grader refused at G1 (product absent). D6RF6's ONE substantive delta is the guard; the numerics, the gate and the accept floor are UNCHANGED. Evidence of the D6RF5 measured binding field: `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF5-a2-wing-convergence-probe/P_conv_20260907T152802Z_41782.log` (`End`, then `Primal solution failed!`; final-Time-block p first-solve `1.625570732e-05`).

**PERMISSION = NOT_FROZEN.** This is a lane's prediction-first proposal. Nothing here is a registration until
the dafoam-supervisor replaces the `PERMISSION` placeholder in `d6rf6_run_arm.sh` with a pre-registration
sha (CLAUDE.md rule 2). The freeze and the enqueue belong to the supervisor and are not taken here.
**No gate, threshold, cap or label below may be altered after first compute** (rule 2); before first
compute this file is amendable, and any amendment must state the condition and how it was checked.

---

## 0. WHY A SUCCESSOR AT ALL — the defect is in the harness, not the physics

D6RF5's `P_conv` arm produced the correct physics and then **crashed on it**. The `F5_scheme` path in
`d6rf5_fd_endpoint.py` already wrapped its baseline primal in a `try/except` that catches DAFoam's
post-`End` `AnalysisError("Primal solution failed!")`, records `primal_raised=True`, and STILL writes the
product json — so the grader can read the leg and grade it. The `P_conv`/`full` baseline primal at
`d6rf5_fd_endpoint.py:316` was **UNGUARDED**. The physically-EXPECTED over-floor plateau therefore raised
through an unguarded call and aborted the container before the product was written; the grader refused at
its first gate G1 (product absent) and the item graded **BLOCKED**.

Under rule 2, D6RF5 has COMPUTED — its gates are closed and its frozen files are not edited. Its BLOCKED
record stands. **The fix is a SUCCESSOR** (this item, D6RF6), not an edit to the frozen D6RF5 files.

## 1. THE ONE SUBSTANTIVE DELTA (§2 of the instrument docstrings; `d6rf6_fd_endpoint.py`)

`d6rf6_fd_endpoint.py` guards the `P_conv`/`full` baseline primal **the same way the `F5_scheme` path is
already guarded**: the baseline `primal("baseline")` call is wrapped in a `try/except Exception` that

- on success sets `primal_raised=False`, records `J_baseline`/`points`, and writes the product (the
  unchanged D6RF5 success path — `j0`/`per0` remain in scope, LEG 2 `baseline_repeat` follows exactly as
  before);
- on the expected `AnalysisError` appends `baseline_RAISED` to the legs, records `primal_raised=True`, the
  `primal_error`, and a `primal_raised_statement` (the refusal is the prediction landing, not the arm
  failing), **STILL writes the product json**, prints `D6RF6_LEG_END baseline ... primal_raised=True` and
  `D6RF6_MODE_COMPLETE`, barriers, and returns.

The full diff is `d6rf6_fd_endpoint.py_DELTAS_from_d6rf5.diff`. **Nothing else in the numerics changes.**
The LIMITED fvSchemes (`Gauss linear limited corrected 0.333` / `limited corrected 0.333`, Fix #1), the
D6RF4-original scheme for F5, and `d6rf6_fvSolution` (`nNonOrthogonalCorrectors 3`, Fix #2, on the
tightened stopping rule) are **carried BYTE-IDENTICAL** from D6RF5 (md5s `8374443e…`, `cf8f745d…`,
`67fed3c2…`). The bright line (`primalMinResTol 1e-08` × `primalMinResTolDiff 1000` = accept floor
`1.0e-05`) is untouched — **the accept floor is NOT moved (`N-D43`).** This successor changes the
harness's SURVIVAL of the expected refusal so the grader can GRADE it; it does not change the
discretisation, the accept floor, or the gate.

## 2. THE FROZEN GATE — `G-CONV`, UNCHANGED FROM D6RF5, and NOT WIDENED (T25)

> **`G-CONV`. For the tightened baseline primal, the final-iteration `initRes` of EVERY field in
> `{U0, U1, U2, he, p_first_uncorrected, p_corrected, nuTilda}` must be `< 1.0e-05` and the primal must
> be accepted by DAFoam. `p`'s FIRST (uncorrected) solve is read explicitly as `p_first_uncorrected` and
> is the binding field. A field at or over `1.0e-05` is `GATE FAIL`.**

The floor `1.0e-05` is `primalMinResTol 1e-08 × primalMinResTolDiff 1000` on this A2-wing case; it is the
carried case floor, not portable (`N-D43`: the S1 CBFS family uses `1e-06`). **The gate threshold, the
field set, and the accept floor are byte-carried from D6RF5. They are not widened to manufacture a pass
(T25 ruling: a case is worked until it passes its gate; the gate is never widened to fit).**

The landed-verdict conjunction is carried unchanged: `PASS` requires `G-CONV` **and** `G-FD` at a plateau
step; `G-CONV GATE FAIL` → the item is `GATE FAIL` and the FD/adjoint legs do not run (`G-FD` reads
`NOT A RESULT` for want of a converged primal); `G-SCHEME` fail or accept-floor-moved → `NOT A RESULT`.
The plateau/step machinery, the 2-point clearance/ratio mini-sweep, `CLEARANCE_FLOOR 5.0`,
`RATIO_MIN 2.0`, `PLATEAU_TOL 10.0`, `ETA_FLOOR 1e-14` and the shape ladder are all carried BYTE-IDENTICAL
in `d6rf6_fd_endpoint.py` (the `P_conv` arm buys only the convergence measurement; the full FD arm is
priced but not bought, §5).

## 3. THE REGISTERED PREDICTION, BEFORE D6RF6 COMPUTE (falsifiable, and on the record so it can be wrong)

> **REGISTERED PREDICTION: Fix #1 (`limited corrected 0.333`) + Fix #2 (`nNonOrthogonalCorrectors 3`)
> are INSUFFICIENT for the binding field. The `p` first-solve (uncorrected) `initRes` will plateau ABOVE
> the `1.0e-05` accept floor, DAFoam will raise `Primal solution failed!` after `End`, and `G-CONV` will
> read `GATE FAIL` (so the item reads `GATE FAIL`).**

This prediction is INFORMED by D6RF5's own measured run (binding p first-solve `1.625570732e-05`, ~1.63×
the floor, essentially unchanged from D6RF4's `1.658293702e-05`) — Fix #1 + Fix #2 did **not** bring the
binding field under floor. **The gate is NOT widened to turn this into a pass** (T25). The value of D6RF6
is that the expected `GATE FAIL` becomes a GRADED, defensible verdict with the product json on disk,
rather than a harness crash to BLOCKED with no product. If, against the prediction, the binding field
comes in `< 1.0e-05`, the guard's success path runs unchanged and `G-CONV` reads what it measures — the
guard cannot bias the reading either way (it only survives the refusal; the per-field residuals the gate
reads come from the container log, single-reader, planted-zero-controlled in `d6rf6_grade.py`).

## 4. THE INSTRUMENT SET AND THE md5 PIN FIXPOINT (`ALL_PINS_MATCH`)

D6RF6 is derived from the frozen D6RF5 instrument set with (a) the one guard delta in `fd_endpoint`,
(b) self-identity re-tokenisation `d6rf5→d6rf6` / `D6RF5→D6RF6`, and (c) every functional md5 pin
re-derived so it resolves against the D6RF6-owned file it names (never a parent D6RF5/D6RF4 value or
root). Four files are carried **BYTE-IDENTICAL** (rename only, md5 preserved), which is what guarantees
the numerics are unchanged: `d6rf6_opt_runScript.py` (`137539e0…`), `d6rf6_fvSchemes_LIMITED`
(`8374443e…`), `d6rf6_fvSchemes_D6RF4_ORIGINAL` (`cf8f745d…`), `d6rf6_fvSolution` (`67fed3c2…`).

The launcher/stager pin fixpoint (verified by the REAL-path stager dry-run against the real
`REGISTERED_BASE`, rc 0, 0 ABORT/REFUSE, 10/10 SOURCE OK):

| pin (in file) | names | pinned value = md5(D6RF6 file) |
|---|---|---|
| `PRODUCER_MD5` (fd) / `MD5_RUNSCRIPT6` (run_arm) / `MD5_RUNSCRIPT` (physical) | `d6rf6_opt_runScript.py` | `137539e0a99be27f27fdb69e063b2a87` (byte-identical) |
| `MD5_FD` (run_arm) | `d6rf6_fd_endpoint.py` | `6b753ab17c7a598106ede906123d4103` (guard delta) |
| `MD5_EXTRACT6` (run_arm) / `MD5_EXTRACT` (physical) | `d6rf6_extract_endpoint.py` | `c93adc8b4d20c6097bb35e82592e6dae` |
| `MD5_LOCUS6` (run_arm) | `d6rf6_endpoint_locus.py` | `341189ca866f302a7e1bba8eefad3a57` (byte-identical) |
| `MD5_PHYS6` (run_arm) | `d6rf6_endpoint_physical.py` | `f61a96653a0d4d71931f4f553bef911f` |
| `MD5_UNITS` (run_arm) | `d6rf6_units_assert.py` | `f4a1524836cefe9fd5df66242f970ae0` |
| `MD5_ANCHOR_GATE` (run_arm) | `d6rf6_anchor_gate.py` | `21bd642c136df97fd6d5d883ecd3ceef` |
| `MD5_FVSCHEMES_LIMITED` (run_arm) / grade dict | `d6rf6_fvSchemes_LIMITED` | `8374443e7a374e9d353cffccdb654aaf` (byte-identical) |
| `MD5_FVSCHEMES_ORIG` (run_arm) / grade dict | `d6rf6_fvSchemes_D6RF4_ORIGINAL` | `cf8f745dcc594ce7a9c67ad2d41e4b06` (byte-identical) |
| `MD5_FVSOL` (run_arm) | `d6rf6_fvSolution` | `67fed3c2ffd2765e51f2563270060648` (byte-identical) |

External/carried pins UNCHANGED (they name files outside this item): `MD5_FVSCHEMES_BASE 58dbed0a…`
(base-case pre-image), `MD5_CEILING_GUARD 1ea97c92…` (`_common/item_ceiling_guard.py`), `MD5_REF_MESH
0fb1935a…` (undeformed reference mesh), the D4 comparison pins (`MD5_EXTRACT4/RUNSCRIPT4/LOCUS4/PHYS4`,
`MD5_D4_HST`), `IDWARP_SO_MD5 85f59e87…`, and the two toolchain image sha256 digests. `PERMISSION` holds
the placeholder `NOT_FROZEN`.

## 5. COST — costed before compute (CLAUDE.md rule 12); numerics identical to D6RF5 so the model is carried

- **Ranks: `4`.** Unit: **core-minutes** = `wall_s × ranks ÷ 60`.
- **`P_conv` estimate (full-run sizing, carried from D6RF5): `62.0` core-min.** Cap: `max(3.0×62.0,
  1.6667×62.0) = 186.0` → **cap `186.0` core-min**, deadline `TMO 2700 s` (`cap_wall = 186.0×60÷4 =
  2790 s = 2700 + 90 frame`). `d6rf6_grade.py` carries `CAPS = {"P_conv": 186.00}` and
  `PREDICTED_CORE_MIN = {"P_conv": 62.00}`. **The cap does not move (`N-D43`; rule 2).**
- **EXPECTED REALISED, given the §3 prediction:** the baseline primal runs to `End` and then raises, so
  the guard writes the product and STOPS (`baseline_repeat` does not run). That is ONE baseline primal.
  D6RF5's measured baseline primal was `ExecutionTime 95.37 s` → `95.37×4÷60 = 6.36` core-min of solve,
  ≈ **`7.6` core-min gross** including the container frame — far under the `186.0` cap. (If, against the
  prediction, the primal is accepted, `L1+L2+L3` run at ≈ `20.6` core-min; the full FD arm is priced but
  NOT bought.)
- **`cost_basis`: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER, NOT MEASURED** (the box cannot read
  its own billing, `COMPUTE_BUDGET_CHARTER.md` §5). Dollars DERIVED, not measured: estimate `62.0`
  core-min = `1.033` core-h → **`$0.053`**; cap `186.0` core-min = `3.100` core-h → **`$0.159`**;
  expected realised `7.6` core-min = `0.127` core-h → **`$0.0065`**. All far under the `$25`
  pre-authorisation. **An overrun STOPS the run; it does not get a new budget** (rule 12).
- **Calibration at completion (rule 12):** when D6RF6 runs and grades, the team compares the pre-registered
  estimate against the actual core-min from the log and lands a row in `docs/COST_CALIBRATION.md`. Not
  done here — D6RF6 has not run.

## 6. COMPLETION, PLANTED-ZERO AND FREEZE DISCIPLINE (carried)

The strict completion rule (rule 4: `rc=0`, an `End` line, last time == `endTime`, fields present,
`ExecutionTime` count == `endTime`, and the age guard) is carried in `d6rf6_grade.py`. **Note the
expected path RAISES after `End`** — the guard records `primal_raised=True` and the grade reads the
binding p residual from the container log's leg segment (single-reader, N5), which is why the item can
read a GRADED `GATE FAIL` rather than BLOCKED. The planted-zero control (`PLANT = 1.234e-03`,
`PLANT_REL_TOL 1e-9`) and the comparator-freeze self-checks are carried byte-identical. `d6rf6_run_arm.sh`
refuses to launch while `PERMISSION` holds `NOT_FROZEN` (G-FREEZE placeholder limb) — "do not launch" is
an exit code, not a sentence in a report.

---

**Lineage:** `O-01 → D6RF3 (NOT A RESULT) → D6RF4 (NOT A RESULT) → D6RF5 (BLOCKED, harness defect) →
D6RF6 (this item)`. Recorded in `cases/dafoam/DAFOAM_SUCCESSOR_LINEAGE_MAP.md` §2 (`Supersedes: D6RF5`).
