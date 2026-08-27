# T18 — 3-D transient conduction in a cube (T11c), EXACT tier: pre-registration (FROZEN)

**Version 1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN IN THE REGISTERED
TREE.** Campaign T, rung **T18** — the rung that puts a graded number into the
capability grid's **`conduction × laminar (no flow) × 3D`** cell, which at HEAD
`cbcb1127` reads **`CAN NOT DO — not attempted`**
(`docs/capability/heat-transfer_GRID.md:49`). Verdict vocabulary fixed by
`CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING.** Written by a heat-transfer lane on the supervisor's dispatch;
decisions in it are `[lab-attributed]`. **Nothing here has been sent, filed,
submitted, uploaded, registered or posted outside this box, and nothing in it
may be (`CLAUDE.md` rule 7).**

## 0. What this rung is, what it is not, and what it can reach

**Three-dimensional transient conduction in the octant of a cube of half-side
`L`**, symmetry planes at `x = y = z = 0`, convective (Robin) faces at
`x = y = z = L`, uniform initial temperature, constant properties, no
generation. Solved with `laplacianFoam`. It is the 3-D product extension of
T11 (1-D plane wall) and T14 (2-D square), and it is the family's **first 3-D
case of any kind that is not conjugate** — the grid's own census records that
"no 3D natural-convection or 3D forced-convection case has ever run"
(`heat-transfer_GRID.md:84`).

> **T18 earns a verdict for CONDUCTION, no flow, 3-D, EXACT tier**, and nothing
> else. It earns nothing conjugate, nothing with a fluid in it, and nothing
> about radiation.

**THE CEILING, STATED BEFORE THE RUN.** The reference is an exact series
solution. Under the upheld V/P ruling an exact or analytic reference scores
**V and never P**, so this rung reaches **GATE REACHED at best and can NEVER
reach HOLDS**. That is written here so no reader discovers it at grading.

**Condition at freeze** (rule 2), checked immediately before this commit:
`verification/runs/T-family/T18_runs/{T18_CU_c,T18_CU_m,T18_CU_f,T18_CU_f_CT}`
each hold `0.orig/`, `constant/`, `system/`, `BUILD.txt`, `CASE.txt`,
`log.blockMesh`, `log.checkMesh.build` — **no `0/`, no numeric time directory,
no `log.solve`, no `STATUS.*`, no `DONE.*`.** Zero core-minutes have been spent
in the registered tree. **No scratch rate probe was run either**: the lane that
wrote this was instructed to launch no solver, and §7 says what that costs the
cost estimate.

**`endTime` is 2.0 and it is NOT a placeholder.** It is 2.0 **seconds of
physical time**, which with `alpha` = 1e-5 m²/s and `L` = 0.01 m is
`Fo = alpha t / L² = 0.20` — the Fourier number the referent and every band in
§3 are evaluated at. The registered value and the built value are the same
number.

## 1. The analytic referent — derived, not transcribed (`exact_t18.py`)

Octant of a cube of half-side `L`, symmetry at `x = y = z = 0`, Robin at
`x = y = z = L` with `Bi = hL/k`, uniform initial `theta = 1`:

    theta(x*, y*, z*, Fo) = f(x*, Fo) f(y*, Fo) f(z*, Fo)
    f(x*, Fo) = SUM_n C_n exp(-zeta_n^2 Fo) cos(zeta_n x*),  C_n = 4 sin z / (2 z + sin 2 z)
    zeta_n tan zeta_n = Bi;   theta_mean = f_mean^3,  f_mean = SUM_n C_n exp(-zeta_n^2 Fo) sin z / z

Separation holds because the initial condition is a product and every boundary
condition is homogeneous and separable; uniqueness of the linear problem does
the rest. 80 terms.

**Verified by Route B on its own output** — the 3-D PDE residual by centred
differences at two stencil widths (1.00e-05 at `h` = 1e-3, falling with ratio
4.00, required in [3, 5]); all three symmetry-plane gradients 0; all three Robin
faces to 8.0e-08; the initial condition to 4.9e-05; permutation symmetry to
machine precision; the mean by 3-D Simpson agreeing with the closed form to
5.9e-10 — **and CROSS-CHECKED against TWO sets of numbers this module did not
compute**:

| cross-check | source | agreement required |
|---|---|---|
| `f_mean` 0.8515954577, `f(0)` 0.9506417785, `f(1)` 0.6433907845 | T11 (`T11_PREREGISTRATION.md` §6) | 1e-09 |
| `theta_mean_2D` 0.7252148236, `theta(0,0)` 0.9037197910, `theta(1,0)` 0.6116341596 | T14 (`T14_registered.json` graded_rows) | 1e-09 |

**Planted wrong value:** `exact_t18.py --selftest` mutates `C_n` by 1 %, by
1e-7, and takes eigenvalues from the wrong `Bi`; **all three are REFUSED**, the
1e-7 one by the cross-checks specifically (measured refusal at |diff| 8.5e-08
against the 1e-09 tolerance).

| quantity at `Fo` = 0.20, `Bi` = 1 | value |
|---|---|
| `theta_mean` | **0.6175896496** |
| `theta(0,0,0)` (centre of the full cube) | **0.8591137894** |
| `theta(1,0,0)` (face centre on two symmetry planes) | **0.5814449853** |

## 2. The registered case (`build_t18.py`)

| quantity | value |
|---|---|
| half-side `L` | 0.01 m |
| `alpha` (`DT`) / `Bi` | 1.0e-05 m²/s / **1.0** |
| `x = y = z = 0` | `zeroGradient` (three symmetry planes) |
| `x = y = z = L` | `mixed`, `valueFraction = Bi/(Bi + 2N)` **per level** (L-341, T11 §5) |
| initial / `T_inf` | 1 / 0, so `theta = T` |
| `endTime` / `deltaT` | **2.0 s physical (`Fo` = 0.20)** / **1.0e-04 s fixed on c/m/f** |
| schemes / solver | `Euler`, `Gauss linear corrected`; `laplacianFoam`, `PCG/DIC` 1e-12 |
| **ranks / decomposition seed** | **1 / `serial, 1 rank, no decomposition`** |

| level | `N` | cells | `dx` (m) | `deltaT` | steps | `valueFraction` |
|---|---:|---:|---:|---:|---:|---:|
| `T18_CU_c` | 20 | 8 000 | 5.0e-04 | 1e-04 | 20 000 | 2.43902439e-02 |
| `T18_CU_m` | 40 | 64 000 | 2.5e-04 | 1e-04 | 20 000 | 1.23456790e-02 |
| `T18_CU_f` | 80 | 512 000 | 1.25e-04 | 1e-04 | 20 000 | 6.21118012e-03 |
| `T18_CU_f_CT` | 80 | 512 000 | 1.25e-04 | **5e-05** | 40 000 | 6.21118012e-03 |

`r21 = r32 = 2` exactly; `checkMesh` Mesh OK on all four (`BUILD.txt`).
`build_t18.py --check-levels` refuses identical `valueFraction`s (driven).

## 3. Graded rows, bands, gate

**Floors imported** (`MESH_STANDARD.md` §10.5): `analyse_t18.py` imports
`STAGNANT_FLOOR, P_MIN, FS, gci_equal, PLANT` from `scripts/roache_triple.py`,
defines none, and refuses if `T18_registered.json`'s copy differs (driven).
`dim = 3`, `Fs` = 1.25.

| row | quantity | reference | band (relative) | predicted fine deviation |
|---|---|---|---|---|
| **G1** | `theta_mean`, arithmetic mean over the octant's equal-volume cell centres | 0.6175896496 | **±5.0e-05** | **+2.06e-05** |
| **G2** | `theta` at (0,0,0), separable linear extrapolation | 0.8591137894 | ±2.5e-04 | ~+1.2e-04 |
| **G3** | `theta` at (1,0,0), separable linear extrapolation | 0.5814449853 | ±3.0e-04 | ~+1.45e-04 |

**BAND GROUND, IN TWO NAMED COMPONENTS, BOTH COMPUTED BEFORE COMPUTE.**

*(a) The READER component is computed exactly*, by applying this comparator's
own reader to the **exact field at each level's cell centres**. G1's arithmetic
mean is the midpoint rule and is therefore **not** mesh-independent — T14 called
its own G1 "mesh-independent by construction" and for a 3-D product that
statement would be wrong:

| level | G1 reader | G2 reader | G3 reader |
|---|---|---|---|
| `c` (N=20) | +2.361e-04 | +1.615e-03 | +2.023e-03 |
| `m` (N=40) | +5.903e-05 | +4.030e-04 | +5.018e-04 |
| `f` (N=80) | **+1.476e-05** | **+1.007e-04** | **+1.250e-04** |

ratio 4.000 between levels — clean second order.

*(b) The FINITE-VOLUME component* is decomposed from T11's measurement rather
than guessed. T11 measured **+4.4e-06 total** at `N` = 100 on the 1-D mean
(`T11_PREREGISTRATION.md` §6.1); this module computes the 1-D **midpoint-reader**
component at `N` = 100 as **+3.148e-06**, leaving **+1.25e-06** as T11's FV part.
Scaled to `N` = 80 that is +1.95e-06 per factor and **+5.9e-06 across the
product**. G2/G3's FV part is estimated at the same order (~2e-05 including the
pointwise term) and **that estimate is the weakest number in this
registration** — it is named as such rather than buried.

**Why these bands and not wider ones.** G1 at ±5.0e-05 is cleared by the fine
level by 2.4× and is **FAILED by the medium level** (predicted +8.2e-05) and by
the coarse level (+5.7e-04). G2 at ±2.5e-04 is cleared by `f` (~2.1×) and failed
by `m` (~+4.5e-04). G3 at ±3.0e-04 likewise. **Every band discriminates the
ladder**; a 1e-03 band would be cleared by every level and would not be a gate.

**Gate order** (`apply_gate`, the only verdict-writing function): (1) any level
failing C_CONV or W0 → NOT A RESULT on every row; (2) triple not CONVERGING →
NOT A RESULT, `p` printed, GCI REFUSED; (3) CONVERGING → PASS / GATE FAIL, GCI
at `Fs` = 1.25. One way only.

**THE FINE VALUE IS GRADED, NEVER THE RICHARDSON EXTRAPOLATE.** The extrapolate
is carried in the gate JSON under `richardson_REPORTED_ONLY` and no verdict this
comparator emits is a function of it. The extrapolate's sign convention is a
known live defect in this family, survivable only because it is display-only
wherever it lives; this registration keeps it display-only.

| control | what | on failure |
|---|---|---|
| C_CONV | every `T` solve's final residual ≤ 1e-10; an `End` line | gate (1) |
| W0 | permutation-symmetry witness ≤ **1e-07** on every level | gate (1) |
| C_VF | `valueFraction` read from `CASE.txt` equals `Bi/(Bi+2N)` per level | exit 2 |
| C_REF | Route B + the T11 **and** T14 cross-checks (§1) | exit 2 |
| C_PZ | planted-zero control per reader (§4) | exit 2 |
| C-T | `T18_CU_f_CT`, `deltaT` halved: movement of G1 **REPORTED** | never gated |
| completion | `mark_done_t18.py`, rule 4 in full including the age guard | NOT DONE → the grader refuses the rung |

**W0's floor is 1e-07 and not 1e-09, and the reason is registered.** The DIC
preconditioner factorises in lexicographic cell order, which is not
axis-symmetric, so a benign round-off drift over 20 000 timesteps is expected.
On fields of order 0.3–0.9 a floor of 1e-07 is still a 3e-07 relative check and
catches any real asymmetry. The sharp expectation is **prediction P4**, which
can lose without voiding the rung.

**L-342 field classes** (registered): PHYSICS-CRITICAL = `rc`, `End`, last time,
field present, `ExecutionTime` count, age guard. INFRASTRUCTURE = `wall_s,
timeout_s, ranks, core_min, capped, checkmesh_rc, solver, solver_path, note,
started_utc, ended_utc` — absent → NOTE "NOT MEASURED", grade proceeds (driven).
`capped` is never a completion conjunct.

**THE PER-RUNG FIELD TUPLE, CHECKED AGAINST THE REGISTERED CLOSURE.** The
registered closure is **NONE** — this is solid conduction, `laplacianFoam`
solves for `T` alone, writes `T` alone and reads no `turbulenceProperties`. The
tuple is therefore **`('T',)`**. It is **not** copied from T1b's thermal-family
tuple `T U p_rgh alphat nut k omega`; requiring `omega` (or `k`, or `nut`) here
would make completion impossible, which is the defect that cost K0d its whole
829 core-minute rung. **This check was performed explicitly for this rung and
is recorded here as having been performed.**

## 4. The planted-zero control — rule 3, sized per reader (L-340)

`analyse_t18.py:planted_zero_control` copies the fine case to scratch (refuses
if the copy resolves inside the case tree); the negative arm must read exactly
0.0 on identical bytes; the positive arm plants `PLANT` = 1.234e-03 (the lab
constant, imported) **into ALL 512 000 cells for the averaging reader G1** and
**into cell 0 for G2 and cell `idx(N-1,0,0)` for G3** (point readers, located
structurally by index). A descending ladder records the demonstrated detection
floor; a read below 0.1 × plant refuses. The selftest runs a **blind reader
mutant** and requires the control to refuse it — driven, it does.

## 5. Instruments — L-332, and their measured selftest state

| instrument | selftest content | result |
|---|---|---|
| `exact_t18.py` | Route B (residual 1.00e-05, ratio 4.00); 1 % and 1e-7 `C_n` mutations REFUSED; wrong-`Bi` eigenvalues REFUSED; AST 0 | **PASS (0 failed)** |
| `build_t18.py` | L-341 guard fires on identical `N`; three Robin faces carry the derived `f`; three symmetry planes; `N×N×N`; CASE.txt records ranks and the decomposition seed; AST 0 | **PASS (0 failed)** |
| `analyse_t18.py` | 17 checks: floors import; rule-5 ladder at the floors (p = 2, 0.51, 0.49, 0.01, oscillatory, divergent, exact, outside band, gate (1)); VALUE CONTROL on the **registered** ladder (analytic field → PASS ×3, G1 p = 2.0005); residual 1e-08 → NOT A RESULT ×3; W0 broken → NOT A RESULT ×3; deviation 3.0/N² → GATE FAIL; blind reader refused; live tree without DONE refused; AST 0 | **PASS (0 failed)** |
| `mark_done_t18.py` | 10 forged clauses (STATUS absent → REFUSE; crash; capped; no End; wrong last time; missing field; wrong count; age guard; infra absent → DONE + NOTE) | **PASS (0 failed)** |

**0 `ast.Assert` in every instrument**; every refusal is `sys.exit(2)`.

**COMPARATOR STATUS — PROPOSED, NOT YET DIFF-READ.** The supervisor's §3 check 1
(measurement-script diffs read as diffs, personally, never delegated) **has not
happened yet**. The instruments are frozen by sha256 and git blob in §9 so the
artifact the supervisor reads cannot drift, and
`verification/runs/T-family/T18_runs/T18_INSTRUMENT_DIFFS.txt` carries the
unified diff of each file against its T14 parent so the read is one file open.
**No launch may occur before that read.** The lane deliberately did not use a
`*_PROPOSED.py` filename: the frozen document must cite the path that will
actually run, a later rename would change the `import` line in `analyse_t18.py`
and so could not be byte-identical, and rule 2 binds the **hash**, not the path.

## 6. Predictions — registered before compute, and every one can lose

- **P1.** G1, G2, G3 all **PASS**, at +2.06e-05 / ~+1.2e-04 / ~+1.45e-04.
  *Can lose* — the FV component of G2/G3 is an estimate, not a measurement.
- **P2.** All three triples CONVERGING with `p` in **[1.7, 2.3]**. *Can lose* —
  the reader error and the FV error are both nominally second order but they are
  not the same error and their sum need not be a clean power law.
- **P3.** C-T moves G1 by **< 20 % of the band** (|move| < 1e-05 relative).
  Ground: implicit-Euler global relative error on a mode decaying at rate
  `lambda` per unit `Fo` is `lambda² dFo Fo / 2`; with `lambda = zeta_1²` =
  0.7401, `dFo` = 1e-05 and `Fo` = 0.2 that is 5.5e-07 per factor, 1.6e-06 across
  the product, so halving `deltaT` should move G1 by about 8e-07. *Can lose.*
- **P4.** W0 < **1e-09** on every level, sharper than the 1e-07 gate floor.
  *Can lose*, and a loss here is **reported as a wrong prediction**, not as a
  failed rung.

**If a prediction loses it is reported as wrong.** No prediction in this
document may be quietly restated after the fact; §2 of the verification charter
closes the gates at first compute.

## 7. Cost — rule 12

**Rate: 1.64e-07 core-s per cell-step. BORROWED, NOT MEASURED ON THIS RUNG.**
It is T14's rate, MEASURED 2026-08-26T21:03Z on a scratch copy of `T14_SQ_c`
(`laplacianFoam`, `Euler`, `Gauss linear corrected`, `PCG/DIC` 1e-12, serial,
2 500 cells, 2 000 steps, `ExecutionTime` 0.82 s;
`T14_registered.json` `cost.rate_scratch_measured_core_s_per_cell_step`,
`T14_PREREGISTRATION.md` §7). **Same solver family, same schemes, same linear
solver, same transient class.**

**MISPREDICTION RISK, NAMED AND ONE-SIDED.** The rate is borrowed across (a) a
dimension change 2-D → 3-D, which raises the stencil from 4 neighbours to 6 and
roughly doubles the flux work per cell, and (b) a mesh jump 2 500 → 512 000
cells, which leaves cache and raises the PCG iteration count as the condition
number grows with `N`. **A rate borrowed across a mesh jump made T1b L4 miss by
31.4 %**, and that is the same failure shape. The expected miss here is an
**under-prediction by up to about 3×**. The caps are set at 4.3× to 6.9× the
point precisely to absorb it. **No scratch rate probe was run**, because the lane
was instructed to launch no solver; that is why this rate is borrowed rather than
measured, and it is stated rather than hidden.

| case | cell-steps | **POINT core-min** | **cap core-min** | `timeout` (s) | ranks |
|---|---:|---:|---:|---:|---:|
| `T18_CU_c` | 1.60e08 | 0.437 | **3** | 180 | 1 |
| `T18_CU_m` | 1.28e09 | 3.499 | **20** | 1 200 | 1 |
| `T18_CU_f` | 1.024e10 | 27.989 | **120** | 7 200 | 1 |
| `T18_CU_f_CT` | 2.048e10 | 55.977 | **240** | 14 400 | 1 |
| **total** | | **87.90** | **383** | | |

POINT 87.90 core-min = 1.465 core-h = **$0.0752 derived**; CAP 383 core-min =
6.383 core-h = **$0.327 derived**, at $0.0513/core-h — **derived, not measured;
reported-by-owner** (`COMPUTE_BUDGET_CHARTER` §5: the box cannot read its own
billing). `timeout = cap × 60 / ranks`; the launcher refuses a different
`--timeout`. **An overrun stops the run; it does not get a new budget.** A
calibration row in `docs/COST_CALIBRATION.md` is owed at completion, stating
actual/predicted and attributing the gap.

## 8. The launcher

`run_one_t18.sh` is `run_one_t14.sh` with the rung name, case set and
registered-JSON path changed: rc captured in the wrapper into
`T18_runs/STATUS.<case>`, `capped` as an independent expiry witness, cap read
from `T18_registered.json`, existing STATUS refused, regex-fullmatch time-dir
guard, **lineage-aware foreign-process guard** (T10aR2 AMENDMENT 1, `9fa66065`),
`0/T` touched last, `exit "$RC"`; **`--no-detach`** is the queue mode.

**THE LAUNCHER HAS NOT BEEN DRIVEN.** T14's registration could state that both
arms had been driven on scratch; this one cannot, because the lane was
instructed to launch no solver. **ARM A (a real launch) is UNDRIVEN** and is
named as such. `bash -n` passes.

**THIS DOCUMENT DOES NOT AUTHORISE A LAUNCH.** Nothing has been placed in
`verification/queue/heat-transfer/`. That directory is a launch button —
`queue_runner.py:223` globs it on a one-minute cron tick, `host` defaults to
this box, and the entry validator ignores unrecognised keys, so no `PENDING` or
`DO-NOT-RUN` annotation makes an entry inert. **Dropping is the supervisor's,
after his own check 4.**

## 9. The freeze set

Committed **in the same commit as this document**.

| file | sha256 (first 16) | git blob | lines |
|---|---|---|---:|
| `verification/runs/T-family/T18_runs/exact_t18.py` | `20f5eab324eac107` | `5a3a8ae825730129855f5083cc106d59c2f036a0` | 268 |
| `verification/runs/T-family/T18_runs/build_t18.py` | `37878f36f7e76bb3` | `c0010a43b4a9739f7921e9e8f48cd1ae3aa0d016` | 231 |
| `verification/runs/T-family/T18_runs/analyse_t18.py` | `2372422cde2e47f8` | `66477e3945f4a622c014613e941d671e0e5525b8` | 539 |
| `verification/runs/T-family/T18_runs/mark_done_t18.py` | `cd54e0450948fb19` | `89f752e69cd2ed1e557ce247cafd7c78b41178df` | 219 |
| `verification/runs/T-family/T18_runs/run_one_t18.sh` | `e1d7ba425e880232` | `3b796bfafd6e441cbbf3cf2564f446222d7d7940` | 193 |
| `verification/runs/T-family/T18_runs/T18_registered.json` | `5c215d060e8fe482` | `e6356dc1c4707076915c53bdd34dc9d517d8fa6a` | 186 |

Case inputs for the four cases (`0.orig/`, `constant/` **less `polyMesh`**,
`system/`, `BUILD.txt`, `CASE.txt`, build logs) are committed alongside; the
`polyMesh` directories are 166 MB and are regenerated by `build_t18.py`, so they
stay out of git and are named here so nothing is invisible merely because it is
big.

## 10. What this document does not do

It does not modify any frozen file of another rung; it does not authorise a
launch and **enqueueing is not authorisation** (`QUEUE_ENTRY_STANDARD` §1); it
does not claim a capability, a conjugate result or anything with a fluid in it;
and it authorises no send — **SUBMISSIONS REMAIN PARKED** (rule 7).
