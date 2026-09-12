# A3GC-AR1 — ANCHOR RERUN. ONE LEVEL. PRE-REGISTRATION.

**FROZEN AT THIS COMMIT** by the dafoam-supervisor, 2026-09-12, before any AR1 compute exists
(CLAUDE.md rule 2; supervisor check 4, non-delegable). The run root `/home/ubuntu/certonomous-runs/A3GC-AR1`
**does not exist** at this commit — that is the condition, and it was checked by listing the parent
directory in the same invocation that wrote this line. Gates, thresholds, cap and label are closed from
here; anything later lands as a dated addendum. **SUBMISSIONS PARKED.**

## 1. What and why

One healthy, rule-4-complete, in-band 3D transonic ONERA M6 **primal**, with **fields saved**. It
reproduces the validated anchor, whose raw fields were overwritten on 2026-07-28 by later `check_totals`
runs (only `0` and `629` survive at np=2). This is **not** a grid triple and claims no observed order,
no GCI and no gradient.

## 2. The level

| item | value |
|---|---|
| surface | `c2`, **6,240** wing quad faces, from `/home/ubuntu/certonomous-runs/A3GC-L3/surfaceMesh.cgns` |
| pyHyp | `N = 65` (**64 wall-normal cells**), `s0 = 1.0e-4`, `marchDist = 12.0`, `cMax 0.1` |
| **growth ratio** | **r = 1.1674**, constant by construction from those three parameters |
| volume cells | **399,360** |
| ranks | **np = 4**, `scotch` |
| endTime / deltaT | **6000** / 1 |
| `writeInterval` | **2000** — divides endTime; three field sets land (2000, 4000, 6000) |
| `primalMinResTol` / `Diff` | **1.0e-08** / 100 → accept floor is the PRODUCT (`N-D43`) = **1e-06** |
| run root | **FRESH**; G-COLD refuses a case where `0` or any time dir already exists |

## 3. Settings provenance — unchanged, deliberately

`system/fvSolution` and `system/fvSchemes` are **byte-identical** to the validated anchor
(`diff` empty against `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/system/`), including
`nNonOrthogonalCorrectors 0` and p relaxation 1.0. **They are not changed.** The anchor converged to
p = 3.744179143218389e-07 on this geometry with exactly these settings; altering the numerics would
discard the one controlled experiment we have and reintroduce the variable just isolated. The only
thing that distinguishes this from the stalling A3GC L3 is **64 wall-normal cells instead of 16**,
and through that r = 1.1674 instead of 2.0880.

Flow conditions, re-asserted, never carried across: `U0 = 291.6`, `p0 = 101325.0`, `T0 = 300.0`,
`nuTilda0 = 4.5e-5`, `aoa0 = 3.06` (M∞ = 0.83997); `DARhoSimpleCFoam`; Spalart-Allmaras, wall
functions. **`patchV` is driven** (`set_solver_input({"patchV": [U0, aoa0]})`) and the applied angle is
asserted back out of the solver's own written U field before compute is spent; an undriven `patchV`
leaves the force frame at AoA 0 and omits a term worth 120% of CD.

## 4. Registered predictions — written before the run

| quantity | prediction | band |
|---|---|---|
| every per-equation initial residual at endTime | **< 1e-06** | gating (§5) |
| p initial residual at endTime | ≈ 3.74e-07 | reported, not gated |
| CD | **0.0229956** | **± 2 %** |
| CL | **0.3131159** | **± 2 %** |

The ±2 % band is set from the registered `A0`/`rho0` normalisation and the anchor's own reproducibility,
before this run exists. **A result outside the band is `GATE FAIL`, not a reason to widen the band.**

## 5. Gates

1. **Strict completion** (CLAUDE.md rule 4): `rc = 0`; `End` line; last time == `endTime` 6000; fields
   present at 6000; and **every field at 6000 newer than the case's own `0/T`** (age guard).
2. **Iterative convergence**: every per-equation initial residual at the last written time ≤ **1e-06**,
   and the printed `Primal min residual` below the §2 accept floor. Read from the `<eq> initRes:` lines
   and the `Primal min residual` line — **never from `finalRes`** (`N-D44`).
3. **Band**: CD and CL inside §4 → `PASS`; outside → `GATE FAIL`. Failing 1 or 2 → `NOT A RESULT`.
4. **G-COLD**, **G-TOL**, **G-MESH** (`checkMesh -allGeometry -allTopology`, every failed check named)
   apply. Decomposition disclosed with every number.

## 6. Grading path — fixed at this commit

`a3gc_grade.py`, **UNCHANGED**, md5 `73dbe368934956700da87e5a1f44ea0c` (verified against the committed
blob). AR1 claims no triple, so only the per-level limbs are read. **No grader delta is used here** —
the proposed `a3gc_grade_R2_GFIELD.diff` is NOT applied and is not part of AR1.

## 7. Cost

**81.4 core-min** (measured basis: the anchor's `ExecutionTime = 1221.21 s` × np=4,
`logs_A3/run_model_run3.log`), ≈ 20 min wall on an idle box. **~$0.07 at $0.0513/core-h — derived, not
measured**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Pre-authorised.
**CAP: 250 core-min, RECORDED AND REPORTED — NOT A STOP.** The supervisor struck the cap-stop clause
this document was drafted with, before freezing it, because it contradicted a standing owner directive:
Sanaa's third NO-CAP ruling of 2026-09-11 (`6f3abf8a3`) — nothing dafoam owns kills on spend or clock —
and her 2026-09-10 16:50Z words for 3D cases, *"i dont want to see any budget gates ( time or money)"*.
Crossing 250 core-min is therefore **written to the watch file and reported, and the run continues**.
The cap is not withdrawn as a *number*: rule 12's costing and the estimate-versus-actual calibration are
untouched, and an overrun is still reported as an overrun rather than absorbed.

**Contention disclosed:** launched beside two live solvers at load ≈ 39 on 16 cores; A3GC L2 measured
`ExecutionTime 4985.59 s` against `ClockTime 9358 s` = **1.88x**. Wall time will exceed 20 min
accordingly and the actual is reported gross with the contention named separately, never absorbed.
Estimate-versus-actual lands in `docs/COST_CALIBRATION.md` at completion (rule 12).
