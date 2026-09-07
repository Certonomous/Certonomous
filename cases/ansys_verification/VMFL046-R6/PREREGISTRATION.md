# VMFL046-R6 — PRE-REGISTRATION

**Supersonic flow with a normal shock in a converging–diverging nozzle.**
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **p. 155 (VMFL046)**.

> **R6 IS TWO DELIBERATE CHANGES vs R5 AND NOTHING ELSE: (1) the SOLVER, rhoPimpleFoam →
> rhoCentralFoam (density-based KNP shock capturing); (2) the OUTLET relaxation length,
> `waveTransmissive lInf 2.0 → 0.3 m`, which REPAIRS the R5 back-pressure wash-out.** The
> gate (`x_shock` vs **1.250 m**, band **5 %**), the plateau threshold (`DELTA_X =
> 6.250e-04 m`), `endTime = 0.080 s`, the mesh, the refinement ratio **r = 2**, the sampler
> and every gate limb of the comparator are **carried forward from R5 byte-identical**. The
> only comparator change is the **N4 replacement** required because rhoCentralFoam has no
> `limitTemperature` fvOption. **Nothing in the gate is widened.**

---

## 1. WHY THIS DOCUMENT EXISTS — R5 WASHED OUT, AND R6 IS ITS PRE-COMMITTED SUCCESSOR WITH THE OUTLET FIXED

VMFL046 has been run R2/R3/R4 (`rhoPimpleFoam`, fully-reflecting `fixedValue` outlet) and R5
(`rhoPimpleFoam`, `waveTransmissive lInf 2.0`). The live verdicts:

- **R4 = `NOT A RESULT`** — the shock **HUNTS** (Roache triple `OSCILLATORY`; `x_shock` never
  plateaus). Hypothesised cause: acoustic reflection off the fully-reflecting outlet.
- **R5 = `NOT A RESULT`** (register **row #62**) — the non-reflecting `waveTransmissive lInf
  2.0` outlet **OVERSHOT**: it un-anchored the back-pressure (outlet static `p` collapsed to
  **~10 % of the 176 325 Pa target** — L1 18 126 / L2 17 880 / L3 17 757 Pa), the nozzle ran
  **fully supersonic**, and **the shock WASHED OUT of the domain** (zero downward `M = 1`
  crossings in all 33 window samples at all three levels; `M_outlet ≈ 2.24–2.43`). The frozen
  comparator refused (exit 2) with no gradeable `x_shock`.

**The R4/R5 pair leaves R4's outlet-reflection question OPEN** (register #62): R4's outlet is
at the **fully-reflecting** extreme, R5's at the **effectively-advective** extreme; the
manual's reference solver (Ansys Fluent, pressure-outlet) sits at the **partially-reflecting
middle**, reached by neither. R6, pre-committed in R5 §6, was to move the SOLVER to the
density-based path — but its recipe carried R5's `lInf 2.0` outlet forward **unrepaired**, so
R6 as pre-committed would reproduce the wash-out. **This registration makes the two changes R6
actually needs: the density-based solver AND an outlet that anchors the back-pressure while
still damping reflections.**

---

## 2. THE TWO DELIBERATE CHANGES, AND WHY EACH

| | R5 | **R6** | why |
|---|---|---|---|
| solver | `rhoPimpleFoam` (pressure-based, implicit PIMPLE) | **`rhoCentralFoam`** (density-based, explicit KNP central-upwind) | R4 hunted and R5 washed out under the segregated pressure solver; the density-based shock-capturing path of **Greenshields et al. (2010)** is what OpenFOAM provides for high-speed flow with shocks (§6, §9) |
| outlet `p` | `waveTransmissive … lInf 2.0` | **`waveTransmissive … lInf 0.3`** | R5's `lInf = domain length` gave the relaxation NO margin over the acoustic transit (§3), so the back-pressure was lost. `lInf 0.3` anchors ~6.7× faster while staying partially-reflecting |

**Everything else is carried from R5 byte-identical: the mesh, `0/T`, `0/U`, the thermophysical
and transport properties, `endTime`, the `r = 2` triple, the sampler, `DELTA_X` and the gate.**
The solver change *forces* four mechanical file changes — `system/fvSchemes` (KNP flux +
reconstruction), `system/fvSolution` (no PIMPLE), `system/controlDict.template` (`application`,
`maxCo`), and the **removal** of `constant/fvOptions` (rhoCentralFoam has no `limitTemperature`)
— all documented and proved from the bytes in §8.

---

## 3. THE OUTLET — `lInf = 0.3 m`, FIXED BY GEOMETRY AND THERMO ALONE, GATE-BLIND, NOT TUNED

This is the crux. R5's `lInf = 2.0 m` did not cure R4's hunt; it **overshot** and lost the
back-pressure. The fix is a **firmer** relaxation length — but chosen by an argument that does
**not** depend on where the shock sits (the shock location is the answer).

### 3.1 The relaxation formula, from the OpenFOAM v2606 source (ground truth, not a forum post)

`waveTransmissive` extends `advectiveFvPatchField`. From
`src/finiteVolume/fields/fvPatchFields/derived/advective/advectiveFvPatchField.txx` (Euler
`ddt`, which every rhoCentralFoam tutorial and R6 use), the outlet relaxes toward `fieldInf`
through the coefficient

```
k = w · Δt / lInf                 (advectiveFvPatchField.txx:193)
refValue = (p_old + k·fieldInf)/(1 + k)
```

so per unit time the boundary relaxes to `fieldInf` at rate `w / lInf`, i.e. with a
**relaxation timescale**

```
τ_relax = lInf / w ,   w = advectionSpeed = U_n + c   (waveTransmissiveFvPatchField.txx:125)
```

where `c = sqrt(γ/ψ) = sqrt(γ R T)` is the local sound speed. As `lInf → 0` the BC → `fixedValue`
(fully reflecting = R4's hunt); as `lInf → ∞` it → pure advection (no anchoring = R5's
wash-out). The community reading corroborates this exactly: *"the larger lInf, the further the
boundary deviates from fieldInf; the smaller lInf, the more reflective"* (OpenFOAM user-guide /
cfd-online), and the shipped tutorials use `lInf` a **fraction of the domain** (rhoPimpleFoam
`aerofoilNACA0012` `lInf 5` in a domain ≫ 5; `sineWaveDamping` `2.25`; sonicFoam `prism` `1`).

### 3.2 The gate-blind criterion — a pure ratio of geometry

Compare `τ_relax` to the **domain acoustic transit time** over the full nozzle length
`L = 2.0 m` (a frozen geometric constant, `t_acoustic = L / c`). Using the conservative lower
bound `w = c` (the subsonic-outlet `U_n ≥ 0` only makes the relaxation *faster*):

```
τ_relax / t_acoustic  =  (lInf / c) / (L / c)  =  lInf / L        ← INDEPENDENT of c
```

The ratio is **purely geometric** — it does not contain the sound speed, the shock location,
or any run output. This is the whole gate-blind argument:

| config | `lInf` | `lInf / L` = `τ_relax / t_acoustic` | outcome |
|---|---|---|---|
| R5 | 2.0 m (= L) | **1.00** | relaxation NO faster than an acoustic transit → back-pressure lost → **WASH-OUT** |
| **R6** | **0.3 m** | **0.15** | relaxation **~6.7× faster** than the transit → back-pressure held |

`lInf = 0.3 m` is the **exit-plane transverse half-height `h_exit`** — a fixed mesh vertex
coordinate (`blockMeshDict` vertex 5 = `(2.0 0.3 −0.05)`), the geometric length scale of the
outlet patch itself. It is **answer-independent**: it is the same number whether the shock
stands at 1.0, 1.25 or 1.5 m, so it **cannot be chosen to move `x_shock`** (the L-487/§3
anti-circularity requirement). No probe is run to select it.

### 3.3 The two failure modes are avoided, quantified from the frozen thermo

Sound speed from the frozen thermo alone (γ = 1.4, R = 287, inlet **total** temperature
`T0 = 500 K`, a frozen BC — **not** the shock): stagnation `c0 = sqrt(1.4·287·500) = 448.2 m/s`
(the upper bound, since static `T ≤ T0`). Then `t_acoustic = L/c0 = 4.46 ms`, and:

- `τ_relax(R6) = lInf/c ≤ 0.3/448.2 = 0.67 ms` — **~120× shorter than `endTime = 0.080 s`** and
  **~6.7× shorter than `t_acoustic`**: the boundary holds `fieldInf` firmly through the
  transient, before the shock can drift to the exit (R5's escape). ✓ anchors.
- `lInf = 0.3 m` is **~96× the finest boundary cell** (L3 diverging `Δx = 1.5/480 = 3.1e-3 m`),
  two orders above the `fixedValue` reflecting limit `lInf → 0`. ✓ still partially transmitting,
  not R4's reflecting wall.

**Why NOT the answer-dependent alternative.** The subsonic-region length `(exit − x_shock)` is a
function of the shock location — the answer — so it is **rejected** as an `lInf` basis, exactly
as R5 §3 rejected it. `lInf` is fixed to the answer-independent exit half-height.

### 3.4 The three candidates evaluated (register #62)

- **(a) waveTransmissive with a smaller geometric `lInf` — CHOSEN.** Minimal single-parameter
  move on the same BC type as R5; the gate-blind ratio above pins the value.
- **(b) an alternative anchoring BC — rejected as no cleaner.** Standard OpenFOAM v2606 offers
  no distinct "hold p while damping reflections" compressible-outlet BC; `fixedValue` is the
  fully-reflecting extreme (R4). The characteristic (NSCBC / Poinsot–Lele) partially-reflecting
  outlet is not in the shipped BC set. `waveTransmissive` **is** the partially-reflecting BC.
- **(c) the Fluent pressure-outlet equivalent — this IS (a).** Fluent's pressure-outlet holds a
  static pressure when subsonic and extrapolates when supersonic; `waveTransmissive` is its
  partially-reflecting OpenFOAM analogue, and a firm `lInf` gives it the Fluent-like anchoring.

**rhoCentralFoam reduces the reflection risk of a firmer anchor.** R4's hunt was a limit cycle
of the **PIMPLE pressure-velocity iteration** (R3 §5.3: 85.4 % of the log-residual variance in
one ~4168-iteration mode). rhoCentralFoam performs **no such iteration** (density-based explicit
time march), so the feedback loop that made a firm outlet dangerous in R4 does not exist here —
erring toward firmer anchoring is the *safe* error direction for R6.

---

## 4. THE GATE — CARRIED FORWARD FROM R5 BYTE-IDENTICAL; ONE COMPARATOR LIMB REPLACED (N4)

The grading path is the R5 comparator with **exactly three mechanical changes, all forced by
the two deliberate axes**, and **no gate quantity moved**:

| # | change | why it is NOT a gate change |
|---|---|---|
| 1 | **N4 REPLACED** — `check_limiters_nonbinding` → `check_T_physical_range` | rhoCentralFoam has **no** `fvOptions limitTemperature` (verified at source, §6), so R4/R5's "the limiter must be non-binding" limb has no subject. It is replaced by a **physical-range refusal** on the reconstructed `T` field, bounds `[50, 1000] K` derived gate-blind from `T0 = 500 K` and the case max Mach — non-binding on the true field (static `T ~ [254, 500] K`), firing only on a KNP blow-up |
| 2 | **`MAXCO_GRADED` 0.5 → 0.2** | a config-verification constant that pins the run to R6's frozen explicit acoustic-Courant limit (§6). Not a gate, band or threshold |
| 3 | **log filename** `log.rhoPimpleFoam` → `log.rhoCentralFoam` | the solver's name |

**Everything else is byte-for-behaviour identical to R5:** the primary reference `x_shock =
1.250 m`, band `±5 %` (half-width 0.0625 m), plateau `DELTA_X = 6.250e-04 m`, the plateau
statistic and window, the interpolating shock reader, the Roache triple, the demote-only
secondaries, W1/W2/W3, and PLANTS A/B/C1/C2/D — **every gate-core constant verified
byte-identical** (`ANALYTICAL_SHOCK`, `SHOCK_TOL`, `BAND`, `DELTA_X`, `W_FRACTION`,
`MIN_WINDOW_SAMPLES`, `N_WINDOWS`, `ENDTIME_GRADED`, `SAMPLE_DT`, `MAXDELTAT_GRADED`,
`P_OBS_LO/HI`, `GCI_FINE_MAX`, `R_REFINE`, `FS`, `PLANT_DX`, `PLANT_K_T`, `PROBE_FLOOR`).

**Refinement:** the `r = 2` grid triple, identical to R1–R5 (converging/diverging/transverse
counts doubling twice). Sampler `nPoints = 2(NXA+NXB)+1` refines with the mesh.

| level | axial converging | axial diverging | transverse | cells | nPoints |
|---|---|---|---|---|---|
| L1 | 40 | 120 | 20 | 3,200 | 321 |
| L2 | 80 | 240 | 40 | 12,800 | 641 |
| L3 | 160 | 480 | 80 | 51,200 | 1,281 |

**Grading pin:**

| artifact | git blob | note |
|---|---|---|
| **`grade_vmfl046_r6.py`** (**THE GRADING PATH / grading_freeze comparator**) | **`bad1408fd52e8d3bdc91bc64f28036de16f02af4`** | derived from R5's `476de16ab3e4f3572435e7e8a729ff617a08fc62` by the three mechanical changes above; `--selftest` = **70 arms, 70 ok, 0 FAILED** under `python3` **and** `python3 -O` |
| **model-sameness ceiling** | **`GATE REACHED`** | carried from R5/R4 byte-identical (charter §21.2: viscous 2-D NS vs inviscid quasi-1D reference). This registration does not re-open the §23 re-ruling; the frozen comparator contains no `PASS` code path |

> **THE GATE IS NOT WIDENED.** `1.250 m`, `±5 %`, `DELTA_X`, `endTime`, the plateau window and
> the reader are byte-identical to R5. `MAXCO_GRADED` tracks R6's own deliberately-changed
> stability constant (0.5 → 0.2); it is a config check, not a gate quantity.

---

## 5. THE DIAGNOSTIC LOGIC — PRE-COMMITTED, BEFORE ANY RUN

R6 changes the solver AND repairs the outlet. Its outcomes are pre-committed:

> **BRANCH (a) — THE SHOCK STANDS AND PLATEAUS.** Every level plateaus (`P1,P2,P3 ≤ DELTA_X`)
> and the Roache triple on `x_shock` is `CONVERGING`. The verdict is the comparator's:
> **`GATE REACHED`** inside the 5 % band with no secondary fired, else **`GATE FAIL`**. This
> would be VMFL046's **first graded result** — the finding "the density-based path with an
> anchored partially-reflecting outlet resolves the standing shock the pressure-based solver
> could not" is recorded.
>
> **BRANCH (b) — IT STILL HUNTS.** Any level fails the plateau at `endTime`. Verdict **`NOT A
> RESULT`** (rule 5 step 1), every level's P1/P2/P3 printed. Conclusion: the unsteadiness
> survives BOTH a non-reflecting outlet (R5, wash-out excluded) AND the density-based solver —
> escalates to Sanaa's desk under §37.4 ("the question is OPEN"). No threshold, `endTime`,
> `maxCo` or window is widened as a remedy.
>
> **BRANCH (b′) — IT WASHES OUT AGAIN.** The comparator refuses (no downward `M = 1` crossing
> in a window sample), exactly as R5. Verdict **`NOT A RESULT`** (instrument refusal). This
> would mean `lInf 0.3` is STILL too weak — but the §3 timescale margin (6.7×) makes this
> unlikely; if it occurs, the successor tightens `lInf` toward `h_throat = 0.1 m` (ratio 0.05)
> by the same gate-blind argument, never by which value best places the shock.
>
> **BRANCH (c) — A LEVEL HITS ITS COST CAP (`rc 124`).** **`NOT A RESULT`** (budget/kill class);
> the successor re-files its estimate from this run's own logs. No cap is raised mid-flight.

---

## 6. THE R6 RECIPE — `rhoCentralFoam`, VERIFIED AT SOURCE

- `application rhoCentralFoam`; `fluxScheme Kurganov` (KNP central-upwind);
- `reconstruct(rho)` `vanLeer`, `reconstruct(U)` `vanLeerV`, `reconstruct(T)` `vanLeer` (TVD);
- `ddtSchemes Euler`; `maxCo 0.2` (explicit density-based stepping needs a tighter Courant
  limit than implicit PIMPLE, and rhoCentralFoam's Courant is **acoustic**, `|U|+c` based);
- `maxDeltaT 1.0e-4` carried from R5 (non-binding: the explicit step is ~1e-6 s);
- outlet `waveTransmissive lInf 0.3` (§3);
- same mesh, `endTime`, sampler, `DELTA_X` and gate as R1–R5.

**TEMPERATURE BOUNDING — VERIFIED AT SOURCE, NOT ASSUMED.** rhoCentralFoam bounds `T` by its
**TVD reconstruction of the conserved variables**, not by an `fvOptions limitTemperature`, which
it **structurally lacks**: `applications/solvers/compressible/rhoCentralFoam/rhoCentralFoam.C`
computes `e = rhoE/rho − 0.5·magSqr(U); e.correctBoundaryConditions(); thermo.correct();` with
**no `fvOptions`, no `fvConstraints`, no `bound()` on T**. The comparator's **N4 limb is
therefore replaced** (§4, limb #1); `constant/fvOptions` is **removed** from the case (§8).

---

## 7. COST — POINT ESTIMATE FROM R4's MEASURED ACTUALS × A SOLVER-CONVERSION FACTOR (rule 12, §26.3)

**Point estimate: 538 core-min.** Method (reconciled against itself here, per §26.3, before the
freeze):

**BASIS** — R4's three measured per-level actuals (register **#61**; a **sustained shock
transient** at THIS mesh/endTime, `rhoPimpleFoam maxCo 0.5`): L1 **8.07** / L2 **54.67** / L3
**426.27** = **489.0 core-min**. R5's 197 core-min is *not* the basis — it was a **wash-out**
(steady supersonic, fewer steps, `docs/COST_CALIBRATION.md` row `C-20260907T030000`); an anchored
shock that actually stands is a sustained transient nearer R4's 489.

**SOLVER-CONVERSION FACTOR** `f_solver = m_steps × m_perstep`:

- `m_steps = (maxCo_R4 / maxCo_R6) × ((U+c)/U)|_{M≈2.2} = (0.5/0.2) × (3.2c/2.2c) = 2.5 × 1.4545
  = 3.64` — rhoCentralFoam steps on the **acoustic** Courant `(|U|+c)` at `maxCo 0.2`, where
  rhoPimpleFoam stepped on the **convective** Courant `(U)` at `maxCo 0.5`; the explicit path
  needs ~3.6× more steps.
- `m_perstep = 0.30` — rhoCentralFoam does ONE explicit update + two light diffusion sweeps per
  step, against rhoPimpleFoam's 3-outer × 2-inner PIMPLE **implicit** solves; ~0.2–0.4× per step.
- `f_solver = 3.64 × 0.30 = 1.09 ≈ 1.10`.

**RECONCILIATION (§26.3):** `489.0 × 1.10 = 537.9 → filed 538 core-min` (difference 0.1, pure
rounding). Per level: **L1 8.88 / L2 60.14 / L3 468.90**. Uncertainty: `f_solver ∈ [0.7, 1.5]`
(`m_perstep ∈ [0.2, 0.4]`); the ~3× cap absorbs the upside. **If the outlet fails to anchor (a
second wash-out) the run is CHEAPER, not dearer**, so the estimate errs in the safe direction
against §26.2's cap-kill trap.

**CAPS (§26.2, ~3× per-level, each ≥ 3× its basis):** per level **27 / 181 / 1 410**, running
total **1 614 core-min** (≥ 3 × 537.9). **An overrun STOPS the run** (`rc 124`, branch (c), rule
12); enforced twice in the driver (per-level + running total). Cap L3 = 1 410 covers up to
**~3.3× R4's L3 basis**, i.e. an `f_solver` up to ~3 — far beyond the plausible range.

**`cost_basis`.** core-min = wall_s × ranks(1) ÷ 60, **measured** at completion; the **estimate**
is R4's measured actuals × an arithmetic `f_solver` (a MODEL, stated above — not itself measured).
Dollars **derived, not measured** at **$0.0513/core-h** (c7a.4xlarge, owner-stated; the box
cannot read its own billing, `COMPUTE_BUDGET_CHARTER §5`): point estimate **538 core-min →
$0.460 derived**; running cap **1 614 core-min → $1.380 derived**.

**Predicted-vs-actual row owed at completion** (rule 12): a `docs/COST_CALIBRATION.md` row
comparing this 538-core-min estimate against R6's graded actual, attributing the gap and — the
key calibration question — **measuring the true rhoCentralFoam/rhoPimpleFoam `f_solver`** against
the assumed 1.10, so the lab's density-vs-pressure-solver estimates improve.

---

## 8. PARITY — PROVED FROM THE BYTES

`diff -rq VMFL046-R5/case VMFL046-R6/case` and per-file `git hash-object`:

- **SIX inputs byte-identical to R5** (blobs equal): `0/T`, `0/U`, `constant/momentumTransport`,
  `constant/thermophysicalProperties`, `constant/turbulenceProperties`,
  `system/blockMeshDict.template`.
- **FOUR inputs changed**, each attributable to the two deliberate axes:
  `0/p` (outlet `lInf 2.0 → 0.3`; blob `1f3a65e4… → c2393adb…`), `system/controlDict.template`
  (`application`, `maxCo`), `system/fvSchemes` (KNP flux + reconstruction), `system/fvSolution`
  (rhoCentralFoam solver set).
- **ONE input removed**: `constant/fvOptions` (rhoCentralFoam has no `limitTemperature`).
- **File set: 10** (= R5's 11 − `fvOptions`). The driver's both-directions parity assert
  (`run_vmfl046_r6.sh`, exit 7) refuses to launch unless all of the above holds.

---

## 9. FILES

| what | path |
|---|---|
| this registration | `cases/ansys_verification/VMFL046-R6/PREREGISTRATION.md` |
| **the grading path** (blob `bad1408f…`) | `cases/ansys_verification/VMFL046-R6/grade_vmfl046_r6.py` |
| the run driver (parity-asserted vs R5) | `cases/ansys_verification/VMFL046-R6/run_vmfl046_r6.sh` |
| case inputs (10 files) | `cases/ansys_verification/VMFL046-R6/case/` |
| predecessor, **READ-ONLY** | `cases/ansys_verification/VMFL046-R5/` · `verification/runs/ansys_verification/VMFL046-R5/` |
| R6 method paper (filed, title-verified rule 15) | `docs/papers/verification_validation/greenshields_2010_rhocentralfoam.pdf` + `.txt` (Int. J. Numer. Meth. Fluids 63:1–21, DOI 10.1002/fld.2069) |
| frozen reference (R1, unchanged) | `cases/ansys_verification/VMFL046/quasi1d_reference.py` |
| run root (**must not exist at freeze**) | `verification/runs/ansys_verification/VMFL046-R6/` |

### 9.1 FREEZE-READINESS

1. **Run driver** `run_vmfl046_r6.sh` — sources OpenFOAM v2606, asserts `blockMesh` +
   `rhoCentralFoam` on PATH (§14/§15), carries the both-directions R5-parity assert (§8),
   builds L1/L2/L3 from the templates, enforces per-level and running caps, writes `RUN_RC`.
   `bash -n` clean.
2. **Comparator** `grade_vmfl046_r6.py` — blob `bad1408f…`, `--selftest` 70 ok / 0 FAILED under
   `python3` and `python3 -O`; the N4-replacement limb carries its own planted controls
   (blow-up, collapse, edge-inclusive, true-range) and PLANTS A/B/C1/C2/D (the planted-zero
   controls, rule 3) all fire.
3. **Cost** (§7) — point estimate 538 core-min reconciled against its own stated method; caps
   27 / 181 / 1 410, running 1 614.

**No compute has been performed** — the run root
`verification/runs/ansys_verification/VMFL046-R6/` does not exist (a launch-ordering step, not a
freeze defect).
