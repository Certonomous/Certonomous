# T14 — 2-D transient conduction in a square (T11b), EXACT tier: pre-registration (FROZEN)

**Version 1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN IN THE REGISTERED
TREE.** Campaign T, rung **T14** = the "second EXACT transient (T11b)" named in
the supervisor's registration order (`LAB_STATE.md` heat-transfer §, item 5).
Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE
FAIL / NOT A RESULT / BLOCKED / PENDING.** Written by a heat-transfer lane;
decisions `[lab-attributed]`.

## 0. Why this candidate, and what the rung is not

The supervisor named three EXACT candidates. **T11b was chosen** because its
analytic referent could be implemented and shown to refuse a planted wrong
value inside the hour: it is the exact product extension of T11's plane-wall
series, and T11's own registered numbers (`T11_PREREGISTRATION.md` §6) serve as
an **external cross-check** that this module did not compute. The
Morton–Taylor–Turner plume is an integral entrainment *model* with an empirical
coefficient, not an exact solution of the governing equations, so it cannot
anchor an EXACT-tier rung; the H-3a T10a ceiling refinement is registered
separately as a one-row successor (T10a-B1b) on T10a's own machinery.

**This is SOLID-ONLY 2-D transient conduction.** There is no fluid in it.
**T14 earns `V` for 2-D TRANSIENT CONDUCTION** — the capability-grid cell
*conduction × 2D* (laminar/turbulent does not apply; the dimension is stated
honestly as 2-D transient, not 3-D, not conjugate).

**Condition at freeze** (rule 2), checked immediately before this commit:
`verification/runs/T-family/T14_runs/{T14_SQ_c,T14_SQ_m,T14_SQ_f,T14_SQ_f_CT}`
each hold `0.orig/`, `constant/`, `system/`, `BUILD.txt`, `CASE.txt`,
`log.blockMesh`, `log.checkMesh.build` — **no `0/`, no numeric time directory,
no `log.solve`, no `STATUS.*`, no `DONE.*`.** Zero core-minutes in the
registered tree. **Disclosed scratch probe:** a copy of `T14_SQ_c` was run
outside the repository for 2 000 steps to measure the rate and drive both
launcher-guard arms (§7, §9).

## 1. The analytic referent — derived, not transcribed (`exact_t14.py`)

Quarter of a square of half-side `L`, symmetry planes at `x = 0`, `y = 0`,
Robin faces at `x = L`, `y = L` with `Bi = hL/k`, uniform initial `theta = 1`:

    theta(x*, y*, Fo) = f(x*, Fo) f(y*, Fo)
    f(x*, Fo) = SUM_n C_n exp(-zeta_n^2 Fo) cos(zeta_n x*),  C_n = 4 sin zeta_n / (2 zeta_n + sin 2 zeta_n),
    zeta_n tan zeta_n = Bi;   theta_mean = f_mean^2,  f_mean = SUM_n C_n exp(-zeta_n^2 Fo) sin zeta_n / zeta_n

Separation holds because the initial condition is a product and every boundary
condition is homogeneous and separable; uniqueness of the linear problem does
the rest. 80 terms. **Verified by Route B on its own output** (PDE residual by
centred differences at two stencil widths, 7.6e-06 at `h` = 1e-3 and falling as
`h²` — ratio required in [3, 5]; symmetry-plane gradients 0; Robin residual
9.5e-08; initial condition; `theta(x,y) = theta(y,x)`; Simpson mean to 3.7e-12)
**and cross-checked against T11's registered 1-D values to 1e-09**
(0.8515954577 / 0.9506417785 / 0.6433907845 at `Fo` = 0.2, `Bi` = 1).
**Planted wrong value:** `exact_t14.py --selftest` mutates `C_n` by 1 % and
requires `verify` to REFUSE (it does, at the initial-condition and cross-check
clauses); eigenvalues from `Bi` = 1.01 checked at `Bi` = 1 are refused at the
Robin clause. Both fire identically under `python3 -O`.

| quantity at `Fo` = 0.20, `Bi` = 1 | value |
|---|---|
| `theta_mean` | **0.7252148236** |
| `theta(0,0)` (centre of the full square) | **0.9037197910** |
| `theta(1,0)` (mid-face) | **0.6116341596** |

## 2. The registered case (`build_t14.py`)

| quantity | value |
|---|---|
| half-side `L` / depth | 0.01 m / 0.001 m (one cell, `empty`) |
| `alpha` (`DT`) / `Bi` | 1.0e-05 m²/s / **1.0** |
| `x = 0`, `y = 0` | `zeroGradient` (symmetry) |
| `x = L`, `y = L` | `mixed`, `valueFraction = Bi/(Bi + 2N)` **per level** (L-341, T11 §5) |
| initial / `T_inf` | 1 / 0, so `theta = T` |
| `endTime` / `deltaT` | 2.0 s (`Fo` = 0.20) / **1.0e-04 s fixed on c/m/f** (spatial-only refinement; temporal error common-mode, measured by C-T) |
| schemes / solver | `Euler`, `Gauss linear corrected`; `laplacianFoam`, `PCG/DIC` 1e-12; ranks 1 |

| level | `N` | cells | `dx` (m) | `deltaT` | steps | `valueFraction` |
|---|---:|---:|---:|---:|---:|---:|
| `T14_SQ_c` | 50 | 2 500 | 2.0e-04 | 1e-04 | 20 000 | 9.90099010e-03 |
| `T14_SQ_m` | 100 | 10 000 | 1.0e-04 | 1e-04 | 20 000 | 4.97512438e-03 |
| `T14_SQ_f` | 200 | 40 000 | 5.0e-05 | 1e-04 | 20 000 | 2.49376559e-03 |
| `T14_SQ_f_CT` | 200 | 40 000 | 5.0e-05 | **5e-05** | 40 000 | 2.49376559e-03 |

`r21 = r32 = 2` exactly; `checkMesh` Mesh OK on all four (BUILD.txt).
`build_t14.py --check-levels` refuses identical `valueFraction`s (driven).

## 3. Graded rows, bands, gate

**Floors imported** (`MESH_STANDARD.md` §10.5): `analyse_t14.py` imports
`STAGNANT_FLOOR, P_MIN, FS, gci_equal, PLANT` from `scripts/roache_triple.py`,
defines none, and refuses if `T14_registered.json`'s copy differs (driven).
`dim = 2`, `Fs` = 1.25.

| row | quantity | reference | band (relative) |
|---|---|---|---|
| **G1** | `theta_mean` over the quarter square — mesh-independent by construction | 0.7252148236 | **±5.0e-05** |
| **G2** | `theta` at (0,0), separable linear extrapolation from the four nearest centres | 0.9037197910 | ±1.0e-04 |
| **G3** | `theta` at (1,0), mid-face on the symmetry plane | 0.6116341596 | ±1.0e-04 |

**Band ground.** T11 measured +4.4e-06 relative on the 1-D mean at `N` = 100
(T11 §6.1). The product doubles the relative error and `N` = 50 quadruples it:
predicted **c ≈ 3.5e-05, m ≈ 9e-06, f ≈ 2.2e-06**. A 1e-04 band would be cleared
by every level and is not a gate; **±5e-05 is cleared by `f` ~20× and by `c`
only ~1.4×.** G2/G3 carry T11's pointwise band; interpolation error enters
their triples and is disclosed.

**Gate order** (`apply_gate`, the only verdict-writing function): (1) any
level failing C_CONV or W0 → NOT A RESULT on every row; (2) triple not
CONVERGING (EXACT / OSCILLATORY / DEGENERATE / DIVERGENT / STAGNANT) → NOT A
RESULT, `p` printed, GCI REFUSED; (3) CONVERGING → PASS / GATE FAIL, GCI at
`Fs` = 1.25. One way only.

| control | what | on failure |
|---|---|---|
| C_CONV | every T solve's final residual ≤ 1e-10; `End` line | gate (1) |
| W0 | max `|theta(x,y) − theta(y,x)|` ≤ 1e-09 on every level | gate (1) |
| C_VF | `valueFraction` read from `CASE.txt` equals `Bi/(Bi+2N)` per level | exit 2 |
| C_REF | Route B + T11 cross-check on the referent (§1) | exit 2 |
| C_PZ | planted-zero control per reader (§4) | exit 2 |
| C-T | `T14_SQ_f_CT`, `deltaT` halved: movement of G1 **REPORTED** as a fraction of the band | never gated |
| completion | `mark_done_t14.py`: in-wrapper `rc = 0`, `End`, last time == 2, field `T`, `ExecutionTime` count == `endTime/deltaT`, age guard vs `0/T` | NOT DONE → the grader refuses the rung |

**L-342 field classes** (registered): PHYSICS-CRITICAL = `rc`, `End`, last
time, field present, `ExecutionTime` count, age guard. INFRASTRUCTURE =
`wall_s, timeout_s, ranks, core_min, capped, checkmesh_rc, solver, solver_path,
note, started_utc, ended_utc` — absent → NOTE "NOT MEASURED", grade proceeds
(driven: all infrastructure fields absent → DONE with NOTE). `capped` is never
a completion conjunct.

## 4. The planted-zero control — rule 3, sized per reader (L-340)

`analyse_t14.py:planted_zero_control`: copies the fine case to scratch
(refuses if the copy resolves inside the case tree); negative arm must read
exactly 0.0 on identical bytes; positive arm plants `PLANT` = 1.234e-03 (the
lab constant, imported) — **into ALL 40 000 cells for the averaging reader G1**
(a one-cell plant would move a mean over `N²` cells by `PLANT/N²` and refuse a
working reader), **into cell 0 for G2 and cell `N−1` for G3** (point readers,
located structurally by index). A descending ladder records the demonstrated
detection floor; a read below 0.1 × plant refuses. The selftest runs a **blind
reader mutant** and requires the control to refuse it.

## 5. Instruments — L-332

| instrument | selftest content | `python3` | `python3 -O` |
|---|---|---|---|
| `exact_t14.py` | Route B; 1 % `C_n` mutation REFUSED; wrong-`Bi` eigenvalues REFUSED; AST 0 (planted 1) | PASS | PASS |
| `build_t14.py` | L-341 guard fires on identical `N`; written `0.orig/T` carries the derived `f` on both Robin faces; `N×N×1` | PASS | PASS |
| `analyse_t14.py` | 17 checks: floors import; rule-5 ladder at the floors (p = 2, 0.51, 0.49, 0.01, oscillatory, divergent, exact, outside band, gate (1)); forged-ladder VALUE CONTROL (PASS ×3, p = 2.000); residual 1e-08 → NOT A RESULT ×3; W0 broken → NOT A RESULT ×3; deviation outside band → GATE FAIL; blind reader refused; live tree without DONE refused; AST 0 | PASS | PASS, identical |
| `mark_done_t14.py` | 10 forged clauses (STATUS absent → REFUSE; crash; capped; no End; wrong last time; missing field; wrong count; age guard; infra absent → DONE + NOTE) | PASS | PASS |

**0 `ast.Assert` in every instrument**; every refusal is `sys.exit(2)`.

## 6. Predictions — registered before compute

- **P1.** G1, G2, G3 all **PASS** (G1 inside ±5e-05; G2/G3 inside ±1e-04).
- **P2.** All three triples CONVERGING with `p` in **[1.5, 2.5]**.
- **P3.** C-T moves G1 by **< 10 % of the band** (|move| < 5e-06 relative).
- **P4.** W0 < 1e-12 on every level.

## 7. Cost — rule 12

**Rate MEASURED on this rung's own coarse case in scratch** (2026-08-26
21:03Z, `run_one_t14.sh` under the runner's `setsid nohup bash -c 'cd …'` form,
2 000 steps, `ExecutionTime` 0.82 s, rc 0): **1.64e-07 core-s per cell-step**
(T11's 1-D rate 5.255e-07 was overhead-dominated at 100 cells).

| case | cell-steps | **POINT core-min** | **cap core-min** | `timeout` (s) |
|---|---:|---:|---:|---:|
| `T14_SQ_c` | 5.0e07 | 0.137 | **2** | 120 |
| `T14_SQ_m` | 2.0e08 | 0.547 | **8** | 480 |
| `T14_SQ_f` | 8.0e08 | 2.187 | **30** | 1 800 |
| `T14_SQ_f_CT` | 1.6e09 | 4.373 | **60** | 3 600 |
| **total** | | **7.24** | **100** | |

POINT 7.24 core-min = **$0.0062 derived**; CAP 100 core-min = 1.67 core-h =
**$0.086 derived**, at $0.0513/core-h, **reported-by-owner, not measured**.
The cap ratio (~14×) guards a hang, not an overrun; the absolute cost is under
a tenth of a dollar. `timeout = cap × 60 / ranks`; the launcher refuses a
different `--timeout`. Calibration row owed in `docs/COST_CALIBRATION.md` at
completion.

## 8. The launcher

`run_one_t14.sh` is `run_one_t13.sh` (freeze `0d2dc150`) with the solver,
field set and rung name changed: rc captured in the wrapper into
`T14_runs/STATUS.<case>`, `capped` as an independent expiry witness, cap read
from `T14_registered.json`, existing STATUS refused, regex-fullmatch time-dir
guard, **lineage-aware foreign-process guard (`9fa66065`)**, `0/T` touched
last, `exit "$RC"`; **`--no-detach`** is the queue mode. **Driven on scratch,
both arms:** ARM A (runner form) → launched, solver rc 0, 2 000 steps, STATUS
written; ARM B (planted `sleep` with cwd in the case) → `REFUSE: pid 435811 is
already running in T14_SQ_c_armB (foreign process, outside this launcher's
lineage)`, exit 2, no STATUS written.

## 9. The freeze set

Committed **in the same commit as this document**.

| file | sha256 (first 16) | git blob | lines |
|---|---|---|---:|
| `verification/runs/T-family/T14_runs/exact_t14.py` | `251ea2afd6c350fd` | `4f72de8d124c2c515b1916b24635559dec162634` | 213 |
| `verification/runs/T-family/T14_runs/build_t14.py` | `71ef5e247f213464` | `677363dac3c028bb798a7157abac6b28e135b9bc` | 217 |
| `verification/runs/T-family/T14_runs/analyse_t14.py` | `67888ce0056fc811` | `386181db5b44f4fac236505f68344e40372cfdae` | 497 |
| `verification/runs/T-family/T14_runs/mark_done_t14.py` | `b6b16ce3f7df8430` | `680eddd3b924172c90abba2fd6b711e6787bfd5f` | 219 |
| `verification/runs/T-family/T14_runs/run_one_t14.sh` | `9ff22e41c486ca1a` | `8b2b7b526b43c6507ff226d1742775c6235e30c6` | 193 |
| `verification/runs/T-family/T14_runs/T14_registered.json` | `ad3930a7a9fc6673` | `149bbf0bacc783859d129bd096860e011a3924a9` | 175 |

Case inputs for the four cases (`0.orig/`, `constant/` less `polyMesh`,
`system/`, `BUILD.txt`, `CASE.txt`, build logs) are committed alongside.

## 10. What this document does not do

It does not modify any frozen file of another rung; it does not authorise a
launch (enqueueing is not authorisation, `QUEUE_ENTRY_STANDARD` §1); it does not
claim a capability or conjugate heat transfer; it authorises no send —
**SUBMISSIONS REMAIN PARKED** (rule 7).
