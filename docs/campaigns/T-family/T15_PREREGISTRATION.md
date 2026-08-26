# T15 — the UNSTEADY successor of T8: one level, a registered steadiness gate, MTT similarity as V-rows: pre-registration (FROZEN)

**Version 1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS RUN IN THE REGISTERED
TREE.** Campaign T, rung **T15** — the successor the T8 record names as its own
sharpest next test. Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS /
GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.** Written by a
heat-transfer lane on the supervisor's dispatch; decisions `[lab-attributed]`.
**Nothing here has been sent, filed, submitted, uploaded, registered or posted
outside this box, and nothing in it may be (`CLAUDE.md` rule 7).**

## 0. What this rung is, what it is not, and what the predecessor lane left

T8 is **`NOT A RESULT`** on two independent grounds
(`T8_VERDICT_2026-08-26.md`): rule 5 clause (1) fired on all three levels, and
the axis-extrapolation precondition `r₂ = 3r₁` was **false on the mesh**. The
steadiness measurement that followed ends, after its own same-day correction,
with this:

> *"The discriminators named at §6.2 remain the right ones, and the **unsteady
> run at one level** is now the sharpest of them."*
> — `T8_STEADINESS_MEASUREMENT_2026-08-26.md` §7.4

and §6.2 specifies it:

> *"An unsteady run at one level (`buoyantBoussinesqPimpleFoam` on `f`'s mesh):
> under (2) it develops a persistent, statistically stationary fluctuation;
> under (1) it settles to the same steady state `f` reached. This is the direct
> test of the §4d question and it answers it in the only currently honest way,
> because it does not depend on reading a steady solver's residual."*

**T15 registers exactly that**, with the geometry, the physics, the closure and
the mesh of T8's fine level **unchanged**, and with **one** registered
difference: `ddt` is no longer `steadyState`.

**THIS RUNG HAS ONE MESH. THERE IS NO ROACHE TRIPLE, NONE IS COMPUTED, AND NO
`GCI`, RICHARDSON EXTRAPOLATE OR DISCRETISATION UNCERTAINTY IS QUOTED ON ANY
ROW.** The comparator imports `STAGNANT_FLOOR`, `P_MIN`, `FS` and `gci_equal`
from `scripts/roache_triple.py`, defines none of them, REFUSES if
`T15_registered.json`'s `roache_floors` block disagrees, **exercises the import
in its selftest so the floors are demonstrably live — and calls `gci_equal` on
no graded row.** The comparator additionally **REFUSES a registration that
records `grid_triple = true`** for this rung. Every row prints the stamp
`SINGLE MESH, NO TRIPLE, NO GCI`, and **the capability ceiling of every row
here is `CAN DO, CAVEATS`** (`docs/capability/heat-transfer_GRID.md`); a
single-mesh result can be nothing better.

**What the predecessor lane left, disclosed and left untouched.**
`verification/runs/T-family/T15_runs/exact_t15.py` was on disk, **untracked**,
when this lane arrived. It was read in full: it is a competent shooting-method
implementation of the **Ostrach (1953) similarity solution for laminar natural
convection on a vertical isothermal plate** — a *different physics from a
different rung*. **It is not this rung's referent, it is not in this rung's
freeze set, and it has not been edited, moved or committed.** It is named here
so that no later reader mistakes a file called `exact_t15.py` for T15's
reference, and so that whoever registers a laminar vertical-plate rung knows it
exists.

**Condition at freeze** (rule 2), checked immediately before this commit:
`verification/runs/T-family/T15_runs/T15_UP_f` holds `0.orig/`, `constant/`,
`system/`, `CASE.txt`, `log.blockMesh`, `log.checkMesh.build` — **no `0/`, no
numeric time directory, no `log.solve`, no `STATUS.*`, no `DONE.*`, no
`gate_t15.json`.** Zero core-minutes have been spent in the registered tree.
**Disclosed scratch probe:** copies of `T15_UP_f` were run **outside the
repository** (20 and 40 timesteps) to measure the rate and the start-up Courant
number and to drive both arms of the launcher guard (§7, §8).

## 1. The referent — derived, not transcribed (`mtt_t15.py`)

Morton, Taylor & Turner (1956) top-hat plume theory, derived in the module from
the conservation equations, so no paper acquisition blocks this rung and rule 15
does not apply — there is no retrieved artifact to verify.

    Q = pi b^2 w,  M = pi b^2 w^2,  F = pi b^2 w g' = F0 (conserved)
    dQ/dz = 2 alpha sqrt(pi M),  dM/dz = F Q / M,  dF/dz = 0
    b = c_b (z - z0), c_b = 6 alpha/5;  w = c_w (z-z0)^(-1/3), c_w = (3 F0/(4 pi c_b^2))^(1/3)
    g' = c_g (z-z0)^(-5/3), c_g = (4/3) c_w^2;  Q ∝ (z-z0)^(+5/3)

**The three exponents −1/3, −5/3, +5/3 are exact consequences of the
conservation equations and carry no `α`. The radius law does carry `α`** — which
is why the spreading rate, and not the exponents, is where a closure's
entrainment error must appear (T8 §2's registered prediction P1).

**A CORRECTION TO THE PARENT'S PROSE, RECORDED BEFORE COMPUTE.**
`T8_PREREGISTRATION.md` §12 S2 states *"A source with `Γ₀ = 1` is pure from
`z = 0`, so the virtual origin sits at the source"*. **That is arithmetically
wrong for a source of finite radius.** `b(0) = b₀` forces
`z₀ = −b₀/c_b = −0.1/0.144 = −0.694444 m`: the virtual origin sits **0.694 m
BELOW the source plane**. Route B checks it — with `z₀` there, `w(0)` reproduces
the registered `w₀ = 0.6 m/s` **exactly** (relative difference `0.00e+00`), and
`g'(0)` to `1.6e-16`. **T8's own INSTRUMENT refits `z₀` from the radius (§12 S4)
and is unaffected; only the prose is wrong.** The size of the error is not
cosmetic: fitting `ln w` on `ln z` instead of `ln(z − z₀)` over `z/D ∈ [10, 25]`
returns about **−0.27**, outside T8's own ±0.05 band.

**Route B, all of it run before any comparison** (`mtt_t15.py --verify`; every
failure `sys.exit(2)`): **B1** the closed form satisfies the three ODEs —
centred-difference residuals `3.7e-10` / `1.0e-10` / `1.7e-15` at `z = 3 m`,
falling as `h²` (measured ratios 3.999, 4.000, required in [3, 5]); **B2** the
flux identities `Q²/(πM) = b²`, `M/Q = w`, `F/Q = g'` to `5.0e-16` relative;
**B3** the registered source lies ON the similarity solution (above); **B4** an
**independent RK4 integration** of the ODE system reproduces the closed form to
`1.5e-13` and returns the exponents to `6.7e-14`; **B5** a **planted 1 %
mutation of `c_b` is REFUSED by B3**, and a **planted 1 % mutation of an
exponent is REFUSED by B4** (deviation `1.28e-02` against a `1e-09` floor).

## 2. The registered case (`build_t15.py`, `T15_UP_f`)

**Geometry, physics, closure and mesh are T8's fine level, byte-for-byte in
intent** (`T8_PREREGISTRATION.md` §1, §5, §12): 5° axisymmetric wedge about `z`,
source `D = 0.2 m`, `R = 12 D`, `H = 40 D`, radial blocks **16/48/64/32**, axial
**640**, **102 400 cells**; `Γ₀ = 1` pure-plume source (`w₀ = 0.6 m/s`,
`g'₀ = 0.6912 m/s²`, `ΔT₀ = 21.1376 K`, `F₀ = 1.3028813053e-02 m⁴/s³`),
`kEpsilon`, `Pr = 0.71`, `Prt = 0.85`, `ν = 1.5e-05 m²/s`, `TRef = 300 K`,
`β = 1/300`, `g = (0 0 −9.81)`, open far field and top, adiabatic no-slip floor
annulus. `blockMesh` → **`Mesh OK`, non-orthogonality Max 0, max skewness
0.3308** (`log.checkMesh.build`).

| quantity | value |
|---|---|
| solver | **`buoyantBoussinesqPimpleFoam`**, serial, 1 rank |
| `ddtSchemes` | **`backward`** (second order) |
| `endTime` / `deltaT` | **240 s** / **0.01 s FIXED** (`adjustTimeStep no`), **24 000 steps** |
| divergence | `div(phi,U) Gauss linearUpwind grad(U)`; `T`, `k`, `epsilon` `Gauss limitedLinear 1` (T8's schemes, less the steady-state `bounded` prefix) |
| `p_rgh` / others | **`PCG/DIC`** 1e-08 (`Final` 1e-09) / `PBiCGStab/DILU` 1e-09 (`Final` 1e-10) — **T8's registered linear solvers, unchanged** |
| PIMPLE | `nOuterCorrectors 2`, `nCorrectors 2`, `nNonOrthogonalCorrectors 0` |
| averaging window | **`[120 s, 240 s]`**, `fieldAverage` `timeStart 120` on `U` and `T` |
| probes | `r = 0.0015625 m` (`= Δr₁/4`, strictly inside the innermost radial cell), `z = 2.0, 3.0, 4.0, 5.0 m`, every **10 steps** (0.1 s) |

**`backward`, and why the scheme is not allowed to help the gate.** Euler's
first-order damping would bias the measurement toward the STEADY side — which is
the registered gate's **PASS** side. A gate must not be assisted by its own
discretisation, so the second-order scheme is registered instead, and the
Courant control below is the price of it.

**The window, grounded before compute.** One domain flush is
`∫dz/w = (3/4)H^{4/3}/(0.75F₀)^{1/3} ≈ 56 s`; the eddy turnover at the graded
probe station is `b/w ≈ 0.43/0.148 ≈ 2.9 s`. The registered discard `[0, 120 s]`
is **2.1 flushes**; the registered window `[120, 240 s]` is **2.1 more flushes
and ≈ 41 eddy turnovers**, sampled 1 201 times.

**One thing changed, deliberately.** A `GAMG` `p_rgh` solver was **measured 32 %
faster** in the same scratch probe (2.35 against 3.27 core-s per step) and was
**declined**, so that the only registered difference from T8 is the time
derivative. The cost of that choice is stated in §7 and is paid rather than
hidden.

## 3. Graded rows, bands derived before compute

**Floors imported** (`MESH_STANDARD.md` §10.5, chief ruling `01967a7b`):
`analyse_t15.py` imports `STAGNANT_FLOOR, P_MIN, FS, gci_equal, PLANT` from
`scripts/roache_triple.py`, defines none, and refuses if the registered JSON's
copy differs (driven: `P_MIN` mutated to 0.5 → exit 2). **`gci_equal` is called
on no graded row** and the registered `grid_triple` is `false` (a registration
claiming `true` is refused — driven).

| row | quantity | reference | band | grading |
|---|---|---|---|---|
| **S1** | `σ(w)/mean(w)` at the axis probe, `z = 3.0 m`, over `[120, 240] s` | 0 | **[0, 0.020]** | band verdict, single mesh |
| **V1** | `n_w`: OLS of `ln(w_axis)` on `ln(z − z₀)`, `z/D ∈ [10, 25]`, 31 stations | **−1/3** | **[−0.383333, −0.283333]** | band verdict, single mesh |
| **V2** | `n_T`: OLS of `ln(T_axis − TRef)` on `ln(z − z₀)`, same stations | **−5/3** | **[−1.716667, −1.616667]** | band verdict, single mesh |
| **V3** | `db/dz`: OLS of the top-hat radius `b = Q/√(πM)` on `z`, same stations | **0.144** | **[0.132, 0.156]** | band verdict, single mesh |

**S1's threshold, grounded.** A puffing plume mode carries **10–30 %**
centreline velocity fluctuation; the numerical residue of a settled URANS field
is below **0.5 %**. **2 % sits an order of magnitude below the phenomenon and
four times above the residue**, and it is the only number in this rung that is
not inherited.

**What S1 falsifies, registered both ways.** **PASS (`≤ 0.020`) falsifies the
genuinely-unsteady hypothesis** as the explanation of T8's failure **at this
resolution and in this axisymmetric geometry**. **GATE FAIL (`> 0.020`), read
together with `S2 ≥ 0.5`, falsifies the settling prediction of the
under-resolution/closure hypothesis** and supports unsteady physics.

> **REGISTERED LIMIT, BEFORE COMPUTE AND NOT DISCOVERED AFTER: a 5° axisymmetric
> wedge admits NO azimuthal mode. A PASS on S1 excludes AXISYMMETRIC
> unsteadiness only. It cannot and does not exclude genuinely unsteady
> three-dimensional physics, and no reading of this rung may claim that it
> does.**

**V1/V2's bands are T8's `±0.05`, unwidened** — same quantity, same geometry,
same closure, same fit window (`T8_PREREGISTRATION.md` §4). They are
**modelling-tolerance** bands, not numerical ones: they separate a plume from a
jet (`n_w = −1`) by 13.3 band widths and from a non-entraining column
(`n_w = 0`) by 6.67.

**V3's band is EMPIRICAL and is labelled so.** MTT gives `b = (6α/5) z` exactly,
so `db/dz = 1.2α`; the band is `1.2 ×` the published pure-plume range
`α ∈ [0.11, 0.13]`. The registered point 0.144 is `1.2 × α_nominal`. **This is
the row where the `kEpsilon` round-jet/plane-jet anomaly is expected to bite**,
and §6's P4 says so before the run.

**Gate order** (`apply_gate`, the ONLY verdict-writing function): (1) any gate-1
control failed → **`NOT A RESULT` on every row**; (2) **there is no clause (2)
here — one mesh, no triple, and no GCI is ever quoted**; (3) inside the band
`PASS`, else `GATE FAIL`. One way only.

| control | what | on failure |
|---|---|---|
| **C_CO** | max Courant **over the registered window** `[120, 240] s` ≤ **1.0**. The max over the WHOLE run is REPORTED and never gated — the start-up transient is discarded by construction | gate (1) |
| **C_STAT** | **stationarity precondition**: `|OLS trend × window length| / |window mean| ≤ 0.05` on the S1 series. *A statistic taken on a series that is still moving is not a property of the run* — the failure `T8_STEADINESS_MEASUREMENT` §0 records twice | gate (1) |
| **S2** | persistence `σ(2nd half)/σ(1st half)`; registered reading fixed before compute: `≥ 0.5` PERSISTENT, `< 0.5` DECAYING | REPORTED, never gated |
| **S3** | the same statistic on `T` at the same probe | REPORTED, never gated |
| **C_BOUND** | `epsilon`/`k` bounding events per step | **REPORTED and DELIBERATELY never gated** — T8 bounded `epsilon` on every level from `Time = 24`, and gating the phenomenon this rung diagnoses would make the rung `NOT A RESULT` for its own subject |
| **C_OP** | operand identity (L-331): `ν, β, TRef, b₀, w₀, g'₀` READ FROM THE CASE FILES; `F₀` recomputed must match `CASE.txt` to 1e-09 | exit 2 |
| **C_GEOM** | **MEASURED geometry only** — §4 | exit 2 |
| **C_Z0** | `z₀` = x-intercept of the OLS `b(z) = s(z − z₀)`, T8's registered §12 S4 route; the exponents refitted at `z₀ = 0` and the closed-form `z₀ = −0.694444 m` are REPORTED beside | REPORTED |
| **C_PZ** | planted-zero control per reader, §5 | exit 2 |
| **C_REF** | Route B on `mtt_t15.py`, §1 | exit 2 |
| completion | `mark_done_t15.py`, §6 | NOT DONE → the grader refuses the rung |

**L-342 field classes** (registered in `T15_registered.json:completion`):
PHYSICS-CRITICAL = the in-wrapper `rc`, `End`, last time == `endTime`, the
fields present **including `UMean`, `TMean`, `UPrime2Mean`, `TPrime2Mean`**
(every graded V-row is built from the time average and an absent average is not
a zero), the `ExecutionTime` count, the age guard, and the probe series reaching
the window's end. INFRASTRUCTURE = `wall_s, timeout_s, ranks, core_min, capped,
checkmesh_rc, solver, solver_path, note, started_utc, ended_utc` — absent →
NOTE "NOT MEASURED", grade proceeds (driven: all infrastructure absent → DONE
with NOTE). **`capped` is never a completion conjunct.**

## 4. T8's GROUND 2, answered in the instrument

> **"READ CENTROIDS FROM DISK. NEVER REGISTER A RATIO TAKEN FROM THE NOMINAL
> MESH SPEC."** — `T8_VERDICT_2026-08-26.md` §4

`run_one_t15.sh` runs `postProcess -func writeCellCentres` and
`-func writeCellVolumes` into `0/` **before the solver starts and before `0/T`
is touched**, so the comparator reads `0/Cx`, `0/Cz`, `0/V` that **OpenFOAM
itself wrote**, and `0/T` still dates the run for the age guard. A failure of
either utility is a **pre-flight REFUSAL**: `0/` is removed, no solver starts and
no `STATUS` is written.

The axis value is the **parabolic-with-zero-axis-slope** extrapolation at the
**measured** radii,

    f(0) = ( f1 r2^2 - f2 r1^2 ) / ( r2^2 - r1^2 )

whose **only** precondition is the **structural** `r₂ > r₁ > 0` — driven: radii
that are not is `exit 2`. **No ratio is asserted anywhere.** The measured
`r₂/r₁`, the measured wedge→annulus `SCALE` beside its flat-sided nominal, and
the difference between the parabolic and the linear axis value are all
**PRINTED and gated on nothing**. Cell grouping into axial planes is structural
(by measured `Cz`, ordered by measured `Cx`) and **refuses** — never repairs — a
plane count or column count that is not the registered one.

*Measured on the built mesh during instrument development (scratch copy):*
640 planes × 160 columns; `r₁ = 4.16270092325e-03 m`, `r₂ = 9.7129688209e-03 m`,
`r₂/r₁ = 2.333333333333`; `SCALE` 72.09146648 measured against the flat-wedge
nominal 72.09146648, relative difference `2.4e-12`. **`r₁` differs from the
paper value `(2/3)Δr = 4.16667e-03` by 0.1 %** — which is the whole reason the
number is read rather than written down.

## 5. The planted-zero control — rule 3, sized per reader (L-340), and the T8 §7.2 inversion

`analyse_t15.py:planted_zero_control` copies **the files the readers read** into
scratch (refusing if the copy resolves inside the case tree), plants, reads back
**through the same readers that produce every graded number**, and refuses on a
blind or noisy reader. The negative arm must return **exactly 0.0** on identical
bytes. Sizing is **relative to each reader's own scale**, never to an absolute
constant:

| reader | class | plant |
|---|---|---|
| `w_axis`, `T_axis` | POINT (2 cells) | `PLANT × |value|` into the two cells the extrapolation reads, located structurally by index |
| `b_th` | INTEGRATING (~130 cells of the plume run) | **ALL-CELL** plant over the run, so the read moves by `~plant` and not `plant/N` |
| `S1` | **DISPERSION RATIO** | **ALTERNATING ±plant** over every window sample — a CONSTANT offset moves the mean and not `σ`, so a constant plant is invisible to a *working* reader; the constant-offset arm is driven too and the control refuses if `σ/mean` moves under it by more than half its own value |

> **THE SIZING RULE FOR `S1` IS NOT THE `0.1 × plant` RULE THE ADDITIVE READERS
> CARRY, AND THAT IS T8 §7.2's LESSON APPLIED RATHER THAN QUOTED.**
> `S1 = σ/mean` combines a plant **in quadrature** — an alternating `±p` raises
> `σ` to `√(σ² + p²)` — so the response to a small `p` on a series that is
> **already fluctuating** is second order, and **no fixed fraction of the plant
> can be demanded of it**. That is exactly the inversion T8 measured: *"THE
> CONTROL GETS WEAKER EXACTLY AS THE CASE GETS WORSE."* The registered answer is
> to demand instead: an **exactly zero** negative arm; a **visible** plant; a
> plant equal to the **whole mean** moving `σ/mean` by **≥ 0.5**; the registered
> plant moving it **above round-off (`> 1e-09`)**; and the **MEASURED** detection
> floor and the quadrature prediction **recorded rather than asserted in
> advance**.

Driven in the selftest on four forged regimes: on a settled series the
registered plant moves `σ/mean` by `1.234e-03` against a quadrature prediction
of `1.234e-03` (**ratio 1.000**); on a 10 %-fluctuating series by `1.54e-05`
against `1.03e-05` (ratio 1.494); the whole-mean plant moves it 0.93–1.00 in
every regime; a constant offset of one whole mean moves it 0 to 0.037. A **BLIND
field reader** (one that ignores the disk) is **REFUSED**.

## 6. Instruments — L-332

**0 `ast.Assert` nodes in each**, with the counter shown able to count a planted
assert (1). Every refusal is `sys.exit(2)`. Run under **`python3` and
`python3 -O`** before this commit; the `-O` refusals are **identical**, compared
line for line.

| instrument | selftest content | `python3` | `python3 -O` |
|---|---|---|---|
| `mtt_t15.py` | Route B B1–B4; 1 % `c_b` mutation REFUSED by B3; 1 % exponent mutation REFUSED by B4; readers exact on the analytic profile (`n_w` to 1e-14, `db/dz` to 1e-14, `z₀` to 1e-09); a non-positive `z − z₀` refused with a reason; AST 0 (planted 1) | PASS | PASS |
| `build_t15.py` | fresh build writes no `0/` and no time directory; the dict implies exactly 102 400 cells; an existing `0/` REFUSED; an existing `250/` REFUSED; the derived source constants checked; AST 0 | PASS | PASS |
| `analyse_t15.py` | **15 checks**: floors import (mutated `P_MIN` → exit 2); a registration claiming `grid_triple = true` → exit 2; the imported `gci_equal` classifying a five-rung ladder AT the floors (CONVERGING / CONVERGING at p=0.51 / STAGNANT at 0.49 / DEGENERATE at 0.01 / OSCILLATORY) so the import is demonstrably live; axis extrapolation exact on a parabola at the measured radii and REFUSING radii that are not `r₂ > r₁ > 0`; **VALUE CONTROL** — a forged analytic plume grades **V1 PASS, V2 PASS, V3 PASS, S1 PASS** with 4 planted controls PASS and **no GCI on any row**; Courant 1.9 in the window → NOT A RESULT ×4; a 20 % window drift → C_STAT → NOT A RESULT ×4; a persistent 10 % fluctuation → **S1 GATE FAIL**; `α` forged to 0.20 → **V3 GATE FAIL while V1 still PASS**; a BLIND reader REFUSED; the live tree without a DONE marker REFUSED; AST 0 | PASS | PASS, identical |
| `mark_done_t15.py` | **12 forged clauses**: pristine → DONE; STATUS absent → REFUSE; `rc=1` crash; `rc=124` capped; no `End`; last time 180 ≠ 240; `UMean` missing → NOT DONE; `ExecutionTime` 23 999 ≠ 24 000; age guard; probe series ending at 180 < 240; no probe series; all infrastructure absent → DONE + NOTE; AST 0 | PASS | PASS |

## 7. Cost — rule 12

**Parent rate, MEASURED, with its `STATUS` path named:**
`verification/runs/T-family/T8_runs/STATUS.T8_MTT_f` — `rc 0`, `wall_s 13101`,
`ranks 1`, `core_min 218.350` over **20 000** `buoyantBoussinesqSimpleFoam`
iterations on 102 400 cells → **0.655 core-s per iteration = 6.397e-06 core-s
per cell-iteration**.

**This rung's rate, MEASURED on a scratch copy of the registered case**
(2026-08-26, `run_one_t15.sh` under the runner's `setsid nohup bash -c 'cd …'`
form, the **registered** `fvSolution`, 20 timesteps): mean `ExecutionTime` delta
over steps 6–20 = **3.267 core-s per step**. The measured
**PIMPLE/SIMPLE ratio is 4.99×**, which is what 4 pressure solves per step
against 1 per SIMPLE iteration predicts — the ratio is *measured*, not assumed.

| case | steps | cells | **POINT core-min** | **cap core-min** | `timeout` (s) |
|---|---:|---:|---:|---:|---:|
| `T15_UP_f` | 24 000 | 102 400 | **1 307** | **2 600** | **156 000** |

POINT 1 307 core-min = 21.78 core-h = **$1.117 derived**; CAP 2 600 core-min =
43.33 core-h = **$2.223 derived**, at the owner-stated c7a.4xlarge
$0.0513/core-h — **reported-by-owner, not measured**
(`COMPUTE_BUDGET_CHARTER.md` §5). Under the $25 pre-authorisation. The cap is
**1.99 × the POINT** and is a hang guard: rule 12 **stops** the run at it and no
new budget follows. `timeout = cap_core_min × 60 / ranks`; the launcher REFUSES
a `--timeout` that is not equal to the registered value. Calibration row owed in
`docs/COST_CALIBRATION.md` at completion.

## 8. The launcher

`run_one_t15.sh` is `run_one_t14.sh` (freeze `5a870e54`) with the solver, the
field set, the rung name and the §4 geometry step changed: solver in the
wrapper's **FOREGROUND** under `timeout`; **rc captured in the wrapper** into
`T15_runs/STATUS.<case>`; `capped = (wall_s ≥ timeout_s)` as an independent
expiry witness; the cap read from `T15_registered.json` and a differing
`--timeout` refused; `--ranks` other than 1 refused; an existing `STATUS`
refused; time directories matched by **regex fullmatch, never a glob**; **`0/T`
touched LAST**; `exit "$RC"` last; **`--no-detach`** is the queue mode. The
**lineage-aware foreign-process guard** is the block copied from
`run_one_t14.sh:145-157` (`9fa66065`: own pid, ancestors to pid 1, descendants
excluded; any foreign process still refused).

**Driven on scratch, both arms, 2026-08-26:**
**ARM A** (runner form, registered dictionaries) → launched, **solver rc 0**, 20
timesteps, `STATUS` written (`wall_s 80`, `capped no`, `note clean`), `0/Cx`,
`0/Cz`, `0/V` written, probes and `UMean`/`TMean`/`UPrime2Mean`/`TPrime2Mean`
present at the write time. **ARM B** (planted `sleep` with cwd in the case) →
`REFUSE: pid 507407 is already running in T15_UP_f_armB (foreign process,
outside this launcher's lineage)`, **exit 2, no `STATUS` written**.

## 9. Predictions — registered before compute, each with its falsifier

- **P1 (the discriminator).** **S1 PASS**: `σ(w)/mean(w) ≤ 0.020` — the URANS
  plume **SETTLES**, and the genuinely-unsteady hypothesis is falsified as the
  explanation of T8's failure at this resolution in this geometry. Ground: a 5°
  wedge admits no azimuthal mode, so an unsteady answer here would have to be an
  **axisymmetric puffing** mode. **FALSIFIER: `S1 > 0.020` together with
  `S2 ≥ 0.5`** — a persistent fluctuation — which supports unsteady physics and
  makes P1 wrong.
- **P1-limit.** Registered above and repeated because it is the reading that
  will be over-claimed: a PASS excludes **axisymmetric** unsteadiness only.
- **P2.** **V1 PASS**, `n_w` inside `[−0.3833, −0.2833]`.
- **P3.** **V2 PASS**, `n_T` inside `[−1.7167, −1.6167]`.
- **P4.** **V3 GATE FAIL** — `db/dz` **outside** `[0.132, 0.156]` — **while V1
  and V2 PASS**: T8's registered P1 (the `kEpsilon` round-jet anomaly biases the
  entrainment coefficient and not the exponents) confirmed on the unsteady
  formulation. **FALSIFIER: V3 inside the band** (P4 wrong, the anomaly did not
  bite here), **or V1/V2 outside it** (T8's P1 wrong).
- **P5.** Max Courant over the window **≤ 0.8**. *Measured in the scratch probe:
  1.053 at start-up, decaying through 0.72 by `t = 0.12 s`* — which is why the
  gate is on the window and the whole-run maximum is reported.
- **P6.** `epsilon`/`k` bounding on **≥ 1 %** of steps (T8 bounded `epsilon` on
  every level from `Time = 24`). REPORTED, never gated. **FALSIFIER: zero
  bounding events**, itself the finding that the transient formulation removes
  the closure's unrealizability.
- **P7.** C_STAT drift **≤ 0.05**: statistical stationarity is reached inside the
  registered 120 s discard. **FALSIFIER: drift > 0.05** → `NOT A RESULT` on every
  row, and the registered finding is that the discard was too short.

## 10. The freeze set

Committed **in the same commit as this document**.

| file | sha256 (first 16) | git blob | lines |
|---|---|---|---:|
| `verification/runs/T-family/T15_runs/mtt_t15.py` | `17cbfca2b1c2c5df` | `f66b33c0e53b2b1231bb3de6ac91fa6f241e3d0f` | 337 |
| `verification/runs/T-family/T15_runs/build_t15.py` | `ff4d0a9c1747393b` | `9ddf02855d83ed9c374ab64d218c555ee374549c` | 505 |
| `verification/runs/T-family/T15_runs/analyse_t15.py` | `4ff5a01f27e11fe1` | `8b5e787fdace02e1dcb572652f95e5dd78069341` | 1056 |
| `verification/runs/T-family/T15_runs/mark_done_t15.py` | `eebff8554e115304` | `40eba7dbac2937637d214ba0a89910efd5864612` | 265 |
| `verification/runs/T-family/T15_runs/run_one_t15.sh` | `ca120dc883a46a1f` | `4f0b46303dd127fd85af6279eddbb0637a6d6a82` | 210 |
| `verification/runs/T-family/T15_runs/T15_registered.json` | `f0f73fdc7eeb30a2` | `61239ae9231a534137838d74580b200cc5588be1` | 160 |

Case inputs (`0.orig/`, `constant/` less `polyMesh`, `system/`, `CASE.txt`,
`log.blockMesh`, `log.checkMesh.build`) are committed alongside, on the T13/T14
convention; the mesh is regenerated by `build_t15.py` + `blockMesh` and checked
by the launcher.

## 11. What this document does not do

- It does not re-register T8, does not re-open T8's gates, and claims no T8 rung
  id. T8 stands **`NOT A RESULT`**.
- It does not modify any frozen file of another rung. `T8_PREREGISTRATION.md` is
  **not edited** — §1's correction to its §12 S2 prose is recorded **here**, in
  this rung's own document, for its owners to place.
- It does not touch `verification/runs/T-family/T15_runs/exact_t15.py`, the
  predecessor lane's unrelated module (§0).
- It does not authorise a launch: **enqueueing is not authorisation**
  (`QUEUE_ENTRY_STANDARD` §1); the supervisor's check 4 is personal.
- It does not claim a capability. No rung is a capability until it has reported,
  and this one's ceiling is **`CAN DO, CAVEATS`** — one mesh.
- It authorises no send. **SUBMISSIONS REMAIN PARKED** (rule 7).
