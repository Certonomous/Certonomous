# T13 — natural convection in a vertical slot, conduction regime, EXACT tier: pre-registration (FROZEN)

**Version 1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN IN THE REGISTERED
TREE.** Campaign T, rung **T13** — the natural-convection EXACT entry rung,
built on the T11 pattern (analytic referent derived in the rung's own module,
no experimental band, `V`-column only). Verdict vocabulary fixed by `CLAUDE.md`
rule 1: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.**

Written by a heat-transfer lane on the supervisor's dispatch; decisions in it are
`[lab-attributed]`. A predecessor lane built the instruments and the three
cases and died at the start of registration; this document registers what is on
disk after the two repairs disclosed in §9.

## 0. What this rung is, and what it is not

**Laminar natural convection between two infinite vertical plates, in the
conduction regime (`Ra_L` = 100), solved with `buoyantBoussinesqSimpleFoam` in
2-D.** The referent is the Batchelor (1954) parallel-flow solution of the
Boussinesq equations: linear temperature across the gap, cubic velocity profile
`v/u_ref = xi(1 - xi)(1 - 2xi)/12`, `Nu_L = 1` exactly.

> **T13 earns `V` for LAMINAR NATURAL CONVECTION, 2-D, EXACT tier** — the
> capability-grid cell *natural convection × laminar × 2D*
> (`docs/capability/heat-transfer_GRID.md`). It earns nothing for the
> boundary-layer regime (`Ra` ≫ 10^3), nothing turbulent, nothing 3-D.

**Condition at freeze** (`CLAUDE.md` rule 2), checked immediately before this
commit: `verification/runs/T-family/T13_runs/{T13_VS_c,T13_VS_m,T13_VS_f}`
each hold **`0.orig/`, `constant/`, `system/`, `BUILD.txt`, `CASE.txt`,
`log.blockMesh`, `log.checkMesh.build` — no `0/`, no numeric time directory, no
`log.solve`, no `STATUS.*`, no `DONE.*`** (`mark_done_t13.py T13_VS_c` reports
`REFUSE: no STATUS.T13_VS_c`). **Zero core-minutes have been spent in the
registered tree.**

**Disclosed scratch probe.** A copy of `T13_VS_c` was run **outside the
repository** for 400 iterations (§7, §9) to measure the rate and to drive both
arms of the launcher guard. Nothing in the registered tree was written by it.

## 1. The analytic referent — derived, not transcribed

`exact_t13.py` derives the solution from the Boussinesq equations
(energy → `T` linear; y-momentum with no-slip and **zero net vertical mass flux**
→ `dp/dy = 0` → `phi(xi) = xi^3/6 - xi^2/4 + xi/12`) and **verifies it by
finite differences on its own output** (`phi'' = xi - 1/2` to 2.6e-10,
`phi(0) = phi(1) = 0`, `∫phi = -2e-19`, antisymmetry). It is exact for: fully
developed flow (no `y`-dependence), constant properties, Boussinesq buoyancy,
laminar, no radiation. **The registered domain is a slot of aspect 16 and the
graded row is at mid-height; an end-effect witness (W1, §4) refuses a level that
is not in the parallel-flow regime.** Pr enters only through `Ra`; the profile
is Pr-independent.

| quantity | value |
|---|---|
| `xi* = 1/2 - sqrt(3)/6` | 0.21132486540518713 |
| `phi_max = 1/(72 sqrt 3)` | 8.0187537387e-03 |
| `Nu_L` | 1 exactly |

## 2. The registered case

| quantity | value |
|---|---|
| gap `L` / height `H` / depth | 0.02 m / 0.32 m (aspect 16) / 0.001 m (one cell, `empty`) |
| `nu`, `Pr`, `beta`, `TRef`, `g` | 1.5e-05 m²/s, 0.71, 1/300 K⁻¹, 300 K, 9.81 m/s² |
| `Ra_L` / `Gr_L` | **100** / 140.845 |
| `dT` = `T_hot - T_cold` | 0.12113968 K (300.06057 / 299.93943 K) |
| `u_ref = g beta dT L^2 / nu` | 0.10563380 m/s; `v_max` = 8.4705e-04 m/s |
| solver / turbulence / ranks | `buoyantBoussinesqSimpleFoam` / laminar / **1** |
| top and bottom | no-slip, `zeroGradient` T (closed slot) |

## 3. The mesh family (`build_t13.py`, `blockMesh`, `checkMesh` OK on all three)

| level | `N` across | `Ny` | cells | `dx` (m) | `endTime` (it.) | `writeInterval` |
|---|---:|---:|---:|---:|---:|---:|
| `T13_VS_c` | 20 | 320 | 6 400 | 1.0e-03 | 10 000 | 1 000 |
| `T13_VS_m` | 40 | 640 | 25 600 | 5.0e-04 | 20 000 | 2 000 |
| `T13_VS_f` | 80 | 1 280 | 102 400 | 2.5e-04 | 40 000 | 4 000 |

`r21 = r32 = 2` exactly, uniform square cells (`checkMesh` max aspect 1.0000,
non-orthogonality 0). `dim = 2` for `roache_triple.gci_equal`.

## 4. Graded rows, controls, floors

**Roache floors are IMPORTED** (`MESH_STANDARD.md` §10.5, chief ruling
`01967a7b`): `analyse_t13.py:62` `from roache_triple import STAGNANT_FLOOR,
P_MIN, FS, gci_equal`; the file **defines neither** and **REFUSES** if
`T13_registered.json`'s copy (0.5 / 0.05) differs from the import — shown able
to fire in the selftest (`P_MIN` mutated → exit 2).

| row | quantity | reference | band | grading |
|---|---|---|---|---|
| **G1** | `v(xi*)/u_ref` at mid-height, 4-point Lagrange at `xi*` | 8.0187537387e-03 | **±1.5e-03 relative** | Roache triple, rule 5 |
| **G1b** | `xi_max`, cubic through the 4 cells around the maximum | 0.2113248654 | **±1.5e-04 absolute** | Roache triple, rule 5 |
| **G2** | RMS over the mid-height row of `(T - T_lin)/dT` | 0 | **floor 1e-06** | absolute floor (EXACT-class) |
| **G3** | `Nu_L` from the half-cell wall gradient, both walls | 1 | **floor 2e-04** | absolute floor (EXACT-class) |

**Band ground (G1, G1b).** The band is **2.1× / 2.2× the DERIVED fine-level
discretisation error** of the 1-D discrete model (`exact_t13.discrete_expectation`:
+7.031e-04 relative and −6.765e-05 at `N` = 80); the coarse (1.125e-02,
−1.081e-03) and medium (2.812e-03, −2.705e-04) levels are predicted **OUTSIDE**
it, so the band is a gate the ladder must earn at `f`, not one the coarsest
level clears.

**EXACT-class rows (G2, G3).** A linear `T` lies in the null space of the
scheme's truncation error, so the G2/G3 triples are round-off and their state is
arbitrary (EXACT / DEGENERATE / OSCILLATORY at 1e-13). Rule 5(2) would return
NOT A RESULT for a row that cannot be wrong by discretisation; the registered
rule is therefore: **triple state PRINTED, verdict by the absolute floor.** The
G3 floor 2e-04 is grounded: the half-cell gradient amplifies a temperature
deviation `delta` by `2N`; at `N_f` = 80 the G2 floor 1e-06 gives 1.6e-04.

**Gate order (`apply_gate`, the only verdict-writing function):** (1) any level
failing C_CONV / C_PLAT / W0 / W1 → **NOT A RESULT on every row**; (2) a G1/G1b
triple DIVERGENT / STAGNANT (`p < STAGNANT_FLOOR`) / OSCILLATORY / DEGENERATE
(`|p| < P_MIN`) → NOT A RESULT with `p` printed and GCI **REFUSED**; (3)
CONVERGING → PASS inside the band else GATE FAIL, GCI at `Fs` = 1.25. The gate
can only move a row **into** NOT A RESULT.

| control | what it does | on failure |
|---|---|---|
| C_CONV | initial residuals of `Uy`, `T`, `p_rgh` ≤ 1e-06 at EVERY iteration of the final 10 %; `Ux` (degenerate channel, L-338) REPORTED, never gated | gate (1) |
| C_PLAT | `|G1(end) - G1(end - writeInterval)|/G1` ≤ 1e-07 | gate (1) |
| W0 | y-invariance mirror: rows above/below mid-height agree in `v` and `T` to 1e-06 | gate (1) |
| W1 | end-effect witness: rows at `H/2 ± L, ±2L, ±4L` agree with the graded row to 1e-06 | gate (1) — the level is not parallel flow |
| C_RA | operand identity (L-331): `nu, Pr, beta, TRef, g, T_hot, T_cold, L, N` READ FROM THE CASE FILES; `Ra_L` recomputed must equal 100 to 1e-09 | exit 2 |
| C_ORDER | the graded row's `T` falls hot → cold with slope `-dT/L` to 1e-06; a transposed (y-fastest) ordering shows a constant row | exit 2 |
| C_PZ | planted-zero control per reader (§5) | exit 2 |
| completion | `mark_done_t13.py`: STATUS present with the in-wrapper `rc = 0`, `End`, last time == `endTime`, fields `T U p_rgh phi`, `ExecutionTime` count == `endTime`, every `endTime` field NEWER than `0/T`; `DONE.<case>` written only then | NOT DONE → the grader refuses the whole rung |

**L-342 field classes** (registered in `T13_registered.json:completion`):
PHYSICS-CRITICAL = the in-wrapper `rc`, `End`, last time, fields present,
`ExecutionTime` count, the age guard. INFRASTRUCTURE = `wall_s, timeout_s,
ranks, core_min, capped, checkmesh_rc, solver, solver_path, note, started_utc,
ended_utc` — an absent infrastructure field is NOT MEASURED, disclosed, and the
grade proceeds; **`capped` is never a completion conjunct.**

## 5. The planted-zero control — rule 3, sized per reader (L-340)

`analyse_t13.py` copies the case to scratch (refuses if the copy resolves inside
the case tree), plants into the copy, reads back through **the same readers that
produce every graded number**, and refuses on a blind or noisy reader. **Sizing
follows L-340:** a **point plant** for the point readers G1, G1b, G3 and W1_max
(one cell, plant 1.304e-04 in `U` / 1.495e-04 in `T` = `PLANT` scaled by the
row's own scale), and an **ALL-ROW plant** for the RMS reader G2 (**every cell of
the graded row**, 20/40/80 cells, so the averaging reader moves by ~`PLANT`
rather than `PLANT/√N`). Both arms run: the negative arm must read exactly 0.0,
the positive arm must recover the plant; a descending ladder records the
demonstrated detection floor (1e-07 × scale on every reader in the selftest).
The selftest also runs a **BLIND reader mutant** and requires the control to
refuse it, so the control's pass is a reading, not a default.

## 6. Instruments — L-332

Four Python instruments and one launcher; **0 `ast.Assert` nodes in each**
(the AST counter in `analyse_t13.py --selftest` is shown able to count a planted
assert: 1). Every refusal is `sys.exit(2)`. The selftests were run under
**`python3` and `python3 -O`** before this commit:

| instrument | selftest | `python3` | `python3 -O` |
|---|---|---|---|
| `analyse_t13.py` | 23 checks: floors import, rule-5 ladder at the floors (p = 2, 0.51, 0.49, 0.01, oscillatory, divergent, outside band, gate (1)), EXACT-class floor, forged-ladder VALUE CONTROL (fine G1 equals the 1-D model to 1e-12, p = 2.000), W1 bump → NOT A RESULT ×4, residual 1e-05 → NOT A RESULT ×4, plateau bump → NOT A RESULT ×4, C_ORDER / uniform-T / C_RA refusals, blind-reader refusal, live-tree no-DONE refusal, AST count | PASS, rc 0 | PASS, rc 0, identical refusals |
| `build_t13.py` | 4 refusals driven | PASS | PASS |
| `mark_done_t13.py` | every clause and the STATUS refusal forged in scratch | PASS | PASS |
| `exact_t13.py` | derivation verified by finite differences; readers exact on the analytic cubic at N = 20/40/80 | PASS | — (no assert; same code path) |

## 7. Cost — rule 12

**POINT rate MEASURED on this rung's own coarse case in scratch** (2026-08-26
20:52Z, `run_one_t13.sh` under the queue runner's `setsid nohup bash -c 'cd …'`
form, 400 iterations, `ExecutionTime` 4.58 s, wall 5 s, rc 0):
**1.789e-06 core-s per cell-iteration.** The **cap** rate is the higher T4
kOmegaSST figure 5.874e-06 (`STATUS.T4_IJ_c`, C-119), so an overrun stops a run
that is 3.3× slower than measured; caps are unchanged from the predecessor's
registration.

| level | cell-iterations | **POINT core-min** (scratch rate) | **cap core-min** | `timeout` (s) |
|---|---:|---:|---:|---:|
| `c` | 6.4e07 | 1.91 | **8** | 480 |
| `m` | 5.12e08 | 15.27 | **64** | 3 840 |
| `f` | 4.096e09 | 122.13 | **500** | 30 000 |
| **total** | | **139.3** | **572** | |

POINT 139.3 core-min = 2.32 core-h = **$0.119 derived**; CAP 572 core-min =
9.53 core-h = **$0.489 derived**, at $0.0513/core-h c7a.4xlarge,
**reported-by-owner, not measured** (`COMPUTE_BUDGET_CHARTER` §5). Under the
$25 pre-authorisation. `timeout = cap_core_min × 60 / ranks`; the launcher
REFUSES a `--timeout` that is not equal to the registered value. Calibration
against the POINT lands in `docs/COST_CALIBRATION.md` at rung completion.

## 8. Predictions — registered before compute

- **P1.** G1 and G1b triples CONVERGING, observed order `p` in [1.5, 2.5]
  (derived expectation 2.000 / 2.000).
- **P2.** G1 relative deviation at `f` in **[+4.9e-04, +9.1e-04]** (the derived
  +7.03e-04 within 30 %), POSITIVE sign; `c` and `m` OUTSIDE the ±1.5e-03 band.
- **P2b.** `xi_max` error at `f` in **[−8.8e-05, −4.7e-05]**, NEGATIVE sign.
- **P3.** `|Nu − 1|` < 1e-04 on both walls at `f`.
- **P4.** W1 < 1e-07 on every level.
- **P5.** G2 RMS < 1e-07 at `f`.
- **P6.** All three levels meet C_CONV and C_PLAT within their registered
  `endTime` (scratch: `Uy` initial residual fell 5.2e-03 → 1.5e-04 over
  iterations 100 → 400 at `c`).

## 9. The launcher, and the two repairs made before this freeze

`run_one_t13.sh`: solver in the wrapper's FOREGROUND under `timeout`, **rc
captured in the wrapper** into `T13_runs/STATUS.<case>` (the queue runner's own
`<case>/STATUS.<case_id>` carries only the launcher rc, an infrastructure
record); `capped = (wall_s ≥ timeout_s)` as an independent expiry witness; cap
read from `T13_registered.json` and a differing `--timeout` refused; existing
STATUS refused; time directories matched by regex fullmatch, never a glob;
`0/T` touched last; `exit "$RC"` last. **`--no-detach`** is the queue mode.

**Repair 1 — the foreign-process guard.** The predecessor's guard excluded only
`$$`; under the runner's `setsid nohup bash -c 'cd <cwd>; …'` form the runner's
wrapper shell holds the case as cwd and the guard refuses its own launch (the
defect that bit three launchers on 2026-08-26). Replaced by the **lineage-aware
scan of `9fa66065`** (own pid, ancestors to pid 1, descendants excluded; any
foreign process still refused by pid). **Driven on scratch, both arms:**
ARM A (runner form, no foreign process) → launched, solver rc 0, 400 iterations,
STATUS written; ARM B (planted `sleep` with cwd in the case) → `REFUSE: pid
413453 is already running in T13_VS_c_armB (foreign process, outside this
launcher's lineage)`, exit 2, **no STATUS written**.

**Repair 2 — `analyse_t13.py` selftest, VALUE CONTROL clause.** The forged
EXACT-class row's triple came out OSCILLATORY at 1e-13 (round-off) and the
selftest clause required EXACT/DEGENERATE/STAGNANT; the clause now requires the
forged fine G2/G3 values to sit at round-off (< 1e-09 / < 1e-06), since an
EXACT-class row's state is printed, not gated (§4). The grader was not changed.

**Repair 3 — provenance-check path.** The launcher resolves
`scripts/check_case_provenance.py` relative to itself and falls back to the
repository path when run from a scratch copy; absent → refuse.

## 10. The freeze set

Committed **in the same commit as this document**.

| file | sha256 (first 16) | git blob | lines |
|---|---|---|---:|
| `verification/runs/T-family/T13_runs/exact_t13.py` | `bdc0d2c5faae445a` | `e730a9157ce9ce8668efbfdba08d8e577dc6d8fc` | 328 |
| `verification/runs/T-family/T13_runs/build_t13.py` | `25825620285134ae` | `e1e8894b43f48a38eee6b5cd7a4b4d8aeafaa3ac` | 427 |
| `verification/runs/T-family/T13_runs/analyse_t13.py` | `d69cff74cea8ba18` | `127ae6d3794fb987cbe719fb8df7c8e74faa1edd` | 760 |
| `verification/runs/T-family/T13_runs/mark_done_t13.py` | `fbd78fd5daacc0a8` | `02f43ea7dabf1853318411e77974edfd332804a6` | 263 |
| `verification/runs/T-family/T13_runs/run_one_t13.sh` | `a4a5ca72bac800d6` | `cc88b1fe3ede27481626c076455125b2d958b7a5` | 193 |
| `verification/runs/T-family/T13_runs/T13_registered.json` | `f53d44929c48dbcf` | `aecd9682b01dd22284216889e26b02980b247814` | 194 |

Case inputs (`0.orig/`, `constant/` less `polyMesh`, `system/`, `BUILD.txt`,
`CASE.txt`, build logs) for the three levels are committed alongside, on the
T10aR2 convention; the mesh is regenerated by `build_t13.py` and checked by the
launcher.

## 11. What this document does not do

- It does not modify any frozen file of another rung.
- It does not authorise a launch: enqueueing is not authorisation
  (`QUEUE_ENTRY_STANDARD` §1); the supervisor's check 4 is personal.
- It does not claim a capability. No rung is a capability until it has reported.
- It does not authorise any send. **SUBMISSIONS REMAIN PARKED** (rule 7).
