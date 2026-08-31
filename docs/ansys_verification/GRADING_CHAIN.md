# ansys-verification — THE GRADING CHAIN

**Sanaa's GRADING TRANSPARENCY ORDER, 2026-08-31** (`etc/sessions/2026-08-31T2055Z_sanaa_grading_transparency_order.md`, captured at `4116024a`): *"Publish your grading chain, ≤10 bullets per team … If any link in your chain can't be named in one bullet, that's a finding, not a formatting problem."*

Written by `ansys-verification-supervisor`. Every citation below is a path or a symbol, not a description. **Three links are findings and are marked `FINDING`; they are not smoothed over.**

1. **WHAT IS GRADED.** Solver-written fields at `endTime` and `postProcessing/*/<time>/surfaceFieldValue.dat` under `verification/runs/ansys_verification/<CASE>/<LEVEL>/`, plus that level's own `log.<solver>` and `system/controlDict`. **Nothing in `cases/` is graded and no archive value is ever graded** — a setup input may come from the Ansys archive (`/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/`), a gate value may not, ever.

2. **WHICH READER.** The frozen comparator's own production readers — `read_sfv()`, `read_solver_info()`, `read_station()` (`cases/ansys_verification/VMFL006-R2/grade_vmfl006_r2.py:417,465,868`). The same functions that produce the verdict are the ones the controls exercise; no paraphrase reader exists.

3. **WHICH FILE THE READER IS POINTED AT.** `pick_time_dir()` (`:369`) selects the time directory **numerically with a cardinality refusal** — never `sorted(glob)[-1]`. Lexicographic ordering puts `900` after `1500`; row #46's grading record shows `lexicographic_would_have_misread = True` at **all three levels**, so this link is load-bearing and not theoretical.

4. **AGAINST WHICH FROZEN GATE.** Module-level constants in the comparator, fixed at the pre-registration commit and hashed against it: band `TOL`, `GCI_MAX`, `P_MIN`, `FS`, `RATIO`, and the reference (`REF_LAB` — **the lab's own full-double-precision evaluation, never the manual's printed 4-dp column**, which carries a 1.406470e-04 rounding floor and is corroboration only).

5. **THAT THE FROZEN FILE IS THE FILE THAT RAN.** `git hash-object` of each frozen file on disk against its blob **at the freeze commit and at HEAD**, plus the `prereg_blob` / `comparator_blob` the launcher independently recorded in `RUN_RC.<LEVEL>` at launch. Rule 2 is checked as **freeze-commit time vs the earliest byte anywhere in the run root** — e.g. VMFL006-R2 `+111 s`, VMFL038-R2 `+157 s`, run root absent at the freeze.

6. **WHO PROVED THE READER CAN SEE.** `planted_zero()` (`:896`) writes a known perturbation (`PLANT = 1.234e-03`) **to disk** and reads it back **through the production reader**, refusing (exit 2) if it cannot see it. Cited firing: VMFL006-R2 and VMFL033-R2 and VMFL038-R2 at **all three levels** (`GRADING_VMFL006.json`, `GRADING_RECORD_2026-08-31T2003Z.json`). **`FINDING`: rows #44, #46 and #49 fired the plant at L1 ONLY while the gate is decided at L3** — disclosed on each row, and the reason every registration since runs the controls **before** any clause that can refuse.

7. **WHAT ELSE MUST FIRE BEFORE A NUMBER IS BELIEVED.** `ast_no_assert_guard()` (`:288`) reads the comparator's own bytes on disk, because `python3 -O` strips `assert`; `reference_reproduction()` (`:320`) reproduces the frozen gate reference live by a **second, independent instrument** (measured spread 2.383599e-06 against a frozen 1e-5); `convergence()` (`:624`) and `completion()` (`:504`) enforce CLAUDE.md rule 4 with **anchored** patterns, because a bare `Time =` also matches inside every `ExecutionTime = ` line.

8. **HOW THE VERDICT IS DECIDED.** `roache()` (`:933`) then `verdict_for()` (`:967`), under CLAUDE.md rule 5: not-converged → `NOT A RESULT`; triple not `CONVERGING` → `NOT A RESULT` whatever the value; else in-band → `PASS`/`GATE REACHED` per the registered ceiling, out-of-band → `GATE FAIL`. A GCI ceiling sits beside the `P_MIN` floor and **can only turn a PASS or GATE FAIL *into* NOT A RESULT, never the reverse.**

9. **WHERE THE VERDICT LANDS.** `GRADING_*.json` in the **run root** (the verdict is read from the JSON, never from stdout) → `RESULTS.md` in the **run root** (never beside the prose) → an append-only row in `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` → a rule-12 calibration row in `docs/COST_CALIBRATION.md`. **`FINDING`: `grade_vmfl033_r2.py` has NO JSON mode**, so row #48's verdict was read from `GRADING_STDOUT_2026-08-31T1715Z.txt`. Deferred, not waived: a machine-readable record is now frozen **with** the comparator on every new registration.

10. **CAUSE CLASS ON EVERY NON-`PASS` ROW.** One of Sanaa's eight classes, **assigned by the grading record and cited like any other claim**, with the report headline carrying the physics-adverse / non-physics split. **`FINDING`: the register carries two row-id formats** (`| **N** |` and `| **#N** |`); a scan matching one returned max 43 when the true max was 48 and produced a duplicate row 44 on 2026-08-31. Audited clean at 51 rows, max 51, no gaps; the safe scan is `grep -oE '^\| \*\*#?[0-9]+\*\* \|'`.

---

**Provenance discipline that binds every number above:** each carries `MEASURED` / `DERIVED` / `EXTRAPOLATED` / `REGISTERED` / `REPORTED-BY-OWNER`. Dollars are always **DERIVED, not measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5).
