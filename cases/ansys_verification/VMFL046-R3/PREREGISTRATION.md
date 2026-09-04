# VMFL046-R3 — PRE-REGISTRATION

**Supersonic flow with a normal shock in a converging–diverging nozzle.**
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **p. 155 (VMFL046)**.

> **THE GATE, THE BAND AND THE PLATEAU THRESHOLD DO NOT MOVE.**
> `x_shock` against **1.250 m**, band **5 %**, plateau **`DELTA_X = 6.250e-04 m`**.
> All three are carried forward from R1/R2 **unchanged, not re-derived, not re-rounded**.
> This document changes **the numerics and nothing else**, which is what
> VMFL046-R2's frozen branch (b) pre-committed before any R2 compute existed.

---

## 1. WHY THIS DOCUMENT EXISTS, AND WHO CHOSE ITS REMEDY

VMFL046-R2 graded **`NOT A RESULT`** (register row **#57**, freeze `f014449a`, 84.4167
core-min measured against 92 filed). Its own registration, frozen **before** it ran, said
what would happen next:

> **BRANCH (b) — ANY LEVEL FAILS THE PLATEAU AT `endTime = 60000`.** Verdict **`NOT A
> RESULT`** (rule 5 step 1), printed with every level's P1/P2/P3 beside it. **The successor,
> VMFL046-R3, CHANGES THE NUMERICS AND NEVER THE GATE, THE BAND OR THE PLATEAU THRESHOLD.**
> The remedy is charter **§20.2 option (c)**, *pre-committed on 2026-09-02 before any of this
> data existed and therefore uncontaminated*: **local time stepping (`ddtSchemes localEuler`),
> a genuinely transient run driven to steady state, or a density-based flux scheme
> (`rhoCentralFoam`).**
> **NO LOOSENED THRESHOLD AND NO LONGER `endTime` IS AVAILABLE AS A REMEDY IN BRANCH (b).**

**The remedy was chosen on 2026-09-02, two days before the data that triggered it existed.**
That is the whole evidentiary point and this document does not add to it. What this document
adds is **which** of the three options, and the answer was decided by measurement, not
preference — see §5.

**This case is `PENDING A RUN` under charter §37.4**, adopted from `VERIFICATION_CHARTER`
§2am.10: *"The obligation to re-run VMFL046 under a registration whose finest level reaches a
measured plateau SURVIVES this ruling and is owed by ansys-verification."* **No record of
this team may cite row #54's or row #57's `NOT A RESULT` as an absence of failure, and this
document does not do so.**

---

## 2. THE DETERMINATION THAT SELECTED THE ROUTE — **LIMIT CYCLE, NOT TRANSIENT**

Charter **§20** requires these be distinguished before a remedy is chosen, and says a
residual floor cannot distinguish them. The determination was made from **R2's completed
artifacts on disk**, through **R2's own frozen reader**, and it is not an inference from a
residual.

| line of evidence | measurement |
|---|---|
| **envelope does not decay** | L3 `ptp` per 10 000-iteration block, iterations 10 000→60 000: `1.1457e-01, 1.1725e-01, 1.1306e-01, 1.1960e-01, 1.1953e-01, 1.2004e-01`. Fitted `d(ln ptp)/d(iter) = +4.15e-07` — **positive**, e-folding 2.4e+06 iterations |
| **the endTime experiment already ran** | R1 ran L3 to 20 000, R2 to 60 000, same numerics (byte-parity enforced). R2's own `ptp` over 10 000–20 000 = **1.1457e-01**; over 50 000–60 000 = **1.2004e-01**. **Tripling the clock changed the amplitude by +4.8 %, in the wrong direction** |
| **it is periodic and monochromatic** | **80.0 %** of the variance of L3's `x_shock` (iterations 10 000–60 000) sits in a **single mode at 4 208 iterations**, its first harmonic (2 104) carrying 7.4 %. Autocorrelation: +0.888 at lag 8 samples, +0.783 at lag 17. Over 12 cycles the upper turning point repeats to **1.10e-03 m (0.35 cells)** and the lower to **9.4e-03 m (3.0 cells)** — an asymmetric **relaxation oscillation** |
| **the residuals carry the same frequency** | from `L3/log.rhoSimpleFoam`, iterations 10 000–60 000: Ux initial residual in **[7.5e-05, 7.1e-04]**, p in **[8.7e-05, 6.3e-03]**, `d(log10 res)/d(iter) = +1.2e-06` (**rising**), and **85.4 %** of the log-residual variance in a **single ~4 168-iteration mode — matching the `x_shock` period of 4 208 to within 1 %** |

### 2.1 THE CONTROL THAT ELIMINATES THE PHYSICAL HYPOTHESIS

The leading physical explanation was shock-induced laminar boundary-layer separation: the
case is `laminar` at Re ≈ 1e7 with a 328 K isothermal wall against T₀ = 500 K, so separation
was very plausible, and separation bubbles at these conditions are genuinely unsteady.
**It is refuted by an artifact that already existed** — the inviscid arm
`verification/runs/ansys_verification/VMFL046_INVISCID/` (μ = 0, slip walls, otherwise the
same frozen case), read through the same reader:

| level | **viscous** ptp | **inviscid** ptp |
|---|---|---|
| L1 | 1.1546e-13 (machine zero) | 8.19e-14 (machine zero) |
| L2 | 2.5667e-04 | **1.58e-12 (machine zero)** |
| L3 | 1.2004e-01 (38.4 cells) | **6.2713e-02 (20.07 cells, 100.3× `DELTA_X`)** |

The inviscid L3 amplitude is **flat** across the run (first half 6.13e-02, second half
6.24e-02) and periodic at ~4 000–5 000 iterations.

> **An Euler solve of a straight-walled CD nozzle at fixed back pressure has no boundary
> layer, no separation and no shedding — no physical unsteadiness mechanism at all — and it
> hunts at 20 cells anyway. THE INSTABILITY IS IN THE DISCRETISATION AND THE SIMPLE OUTER
> ITERATION, NOT IN THE FLOW.** Viscosity *advances* it (it is what makes viscous L2
> non-zero and viscous L3 twice the inviscid amplitude) but it is not the cause.

*Independently reproduced by the supervisor before the route was ruled (§3 check 3): L3 ptp
6.2713e-02 m = 20.07 cells = 100.3× `DELTA_X`, L1 and L2 machine-zero.*

### 2.2 THE AMPLITUDE SCALING IS A BIFURCATION, NOT AN ORDER OF ACCURACY

Diverging-block cell size `dx = 1.5/{120, 240, 480}` = 1.250e-02 / 6.250e-03 / 3.125e-03 m:

| level | ptp (m) | **in cells** | × `DELTA_X` |
|---|---|---|---|
| L1 | 1.1546e-13 | 9.2e-12 | 0.0 |
| L2 | 2.5667e-04 | **0.041** | 0.4 |
| L3 | 1.2004e-01 | **38.4** | **192** |

Nine orders across a 4× cell-count range is not a convergence rate. It is three regimes
across a **Hopf-type bifurcation of the discrete iteration operator**: L1 a stable fixed
point reached to machine precision (1.15e-13 m is the reader's own roundoff on a profile that
has stopped changing — it is zero, and **zero has no order**); L2 marginal (0.041 cells,
**not decaying**, spectrum broadband; the *inviscid* L2 is machine-zero); L3 a saturated
periodic orbit. **The control parameter is numerical dissipation, which falls linearly in
`dx`:** every convective term in R2's frozen `fvSchemes` is first-order upwind, whose
artificial viscosity is `nu_num ≈ |u|·dx/2`. Halving `dx` halves the damping available to
the shock-position mode; between L2 and L3 it falls below what the shock/back-pressure
feedback loop needs. **A quantity identically zero on one side of a bifurcation and 38 cells
on the other has no observed order — which is exactly why R2's Roache triple reads
`R = 0.723, DIVERGENT`.**

**Consequence recorded against a ruled clause: charter `§21.1` is refuted by 38× on its own
arithmetic.** It ruled that shock location needs **no** plateau criterion because *"tolerance
band = ±0.0625 m = 20.0 CELLS; hunt = ±1 cell = 5.0 % of the band."* Measured hunt: **38.4
cells, 96 % of the full band.** The method (tolerance in cells against hunt in cells) is
sound and survives; **its input was asserted, never measured**, which is `§24.3` repeating one
clause later. R2's authors imposed a plateau anyway, overriding `§21.1` in the strict
direction, and that override is the only reason the hunt was caught. *The amendment is the
supervisor's to file and is not made here.*

---

## 3. THE INDEPENDENT REFERENCE CHECK — **THE GATE REFERENCE IS SOUND**

Both arms converge *away* from 1.250 m under refinement (viscous +1.73 / −4.06 / −12.07 %;
inviscid +2.08 / −1.99 / −4.82 %), so a reader will eventually ask whether the reference
itself is wrong. **It is not, and the check was performed rather than asserted.**

An independent quasi-1D solve — area–Mach relation plus Rankine–Hugoniot, written from
scratch and not derived from R1's `quasi1d_reference.py` — for **this** contour (throat
`x = 0.5`, `h = 0.1`; exit `h = 0.3`, area ratio **3.0000**) and **these** boundary conditions
(`p0 = 301 325 Pa`, `p_back = 176 325 Pa`) places the normal shock at:

| quantity | independent path | frozen reference |
|---|---|---|
| **`x_shock`** | **1.248513 m** | **1.250 m** |
| difference | **0.12 %** | — |
| `M1` / `M2` / `M_exit` | 2.19608 / 0.54758 / 0.32620 | — |

**The reference is confirmed. The drift away from it is therefore a real finding, and it is
not viscous** — the inviscid arm drifts too.

---

## 4. THE CASE — UNCHANGED PHYSICS, AND THE PARITY IS ENFORCED NOT ASSERTED

Planar CD nozzle, half-modelled by symmetry about `y = 0`. Straight walls: inlet
`h = 0.2` → throat `h = 0.1` at `x = 0.5` → exit `h = 0.3` at `x = 2.0` (exit/throat area
ratio 3). Air as a perfect gas, `Cp = 1004.5`, `mu = 1.7894e-05`, `Pr = 0.72`, `laminar`.
Inlet `totalPressure p0 = 301 325 Pa` with `T = 500 K`; outlet `fixedValue p = 176 325 Pa`;
`noSlip` isothermal wall at 328 K; `symmetryPlane` centreline; `empty` front/back.

`r = 2` grid triple, **identical to R1 and R2**: `NXA/NXB/NY` = 40/120/20, 80/240/40,
160/480/80 → **3 200 / 12 800 / 51 200 cells**. Sampler `nPoints = 2(NXA+NXB)+1` =
321/641/1281, sampler/mesh ratio **0.499000 identically at all three levels**.

**Eight case inputs are BYTE-IDENTICAL to R2's frozen case and the driver ABORTS if any of
them differs** (`run_vmfl046_r3.sh` §2, exit 7): `0/T`, `0/U`, `0/p`,
`constant/fvOptions`, `constant/momentumTransport`, `constant/thermophysicalProperties`,
`constant/turbulenceProperties`, `system/blockMeshDict.template`. **The driver also ABORTS if
any of the three declared numerics files is byte-identical to R2's** — because that would
mean the numerics change branch (b) pre-committed was never made. The claim in §6 is an
**enforced property, not a sentence**, and it fails in both directions.

---

## 5. THE NUMERICS CHANGE — **WHAT CHANGED, AND EVERY PART OF IT WAS FORCED BY MEASUREMENT**

### 5.1 ⚠ ROUTE A (`ddtSchemes localEuler` IN `rhoSimpleFoam`) DOES NOT EXIST

The brief that commissioned this design asserted that `rhoSimpleFoam` supports local time
stepping via `localEuler`. **It does not.**
`grep -rn "ddt" /usr/lib/openfoam/openfoam2606/applications/solvers/compressible/rhoSimpleFoam/`
(excluding the porous and overset variants) returns **nothing**. `UEqn.H` reads
`fvm::div(phi,U) + MRF.DDt(rho,U) + turbulence->divDevRhoReff(U) == fvOptions(rho,U)` —
`MRF.DDt` is a Coriolis term, not a time derivative, and MRF is inactive here. There is no
`setRDeltaT.H`, no `localEulerDdtScheme.H` include and no `LTS` flag; all three exist in
`rhoPimpleFoam` and none in `rhoSimpleFoam`.

> **Writing `ddtSchemes { default localEuler; }` into a `rhoSimpleFoam` case is a SILENT
> NO-OP THAT NEVER ERRORS** — no `fvm::ddt` is ever constructed, so the dictionary entry is
> never looked up. **A registration built on it would have run 60 000 identical iterations
> and claimed a numerics change that never happened.**

Recorded because it is load-bearing: **R2's own `steadyState` is therefore not a "steady
discretisation of the transient problem" — it is the absence of any time derivative at all,**
which is precisely why its fixed point is the fixed point of a *relaxation iteration* and not
of the physical equations. *(The supervisor recorded this as his own error, 2026-09-04:
"a brief naming a solver capability is a claim, and a lane may not treat a supervisor's claim
as a measurement.")*

### 5.2 ROUTE C (`rhoCentralFoam`) — REFUSED, AND THE OBSTACLE IS MEASURED

**§12.2, answered.** `§21.2` fixed the principle: *"§12.2 asks the prior question of whether
the two objects are the same KIND of thing."* **A discretisation scheme is not a model.**
`rhoSimpleFoam` and `rhoCentralFoam` integrate the same compressible Navier–Stokes system
with the same thermophysics, BCs and mesh; they differ in flux scheme and time integration.
So the swap changes the **numerics** and not the model — **and it also does not improve the
model-sameness position by one inch**, because the case stays viscous either way. `§12.2`'s
ruling for VMFL046 is about viscous-NS versus inviscid-quasi-1D and is untouched.

> **THE COROLLARY, STATED BECAUSE IT CONSTRAINS THIS DOCUMENT:** making the model **SAME**
> means running **inviscid**, which is a **MODEL** change, not a numerics change. **Branch (b)
> pre-committed a numerics change, so an inviscid R3 would break the pre-commitment.** That
> belongs in its own registration and is not done here.

**And it was built and run.** With `hePsiThermo` (rhoCentralFoam requires psiThermo),
Kurganov flux, vanLeer reconstruction and `maxCo 0.4`, it **aborted at time step 58,
`ExecutionTime` 0.25 s**, in `species::thermo::T` — the out-of-range-temperature abort — and
**`rhoCentralFoam` has no `limitTemperature` fvOptions path**, which is the mechanism
`constant/fvOptions` provides for this very case. Rescuing it would need five simultaneous
changes (thermo type, whole `fvSchemes`, whole `fvSolution`, a new initial condition, and
almost certainly a non-reflecting outlet), and a plateau obtained under five changes at once
would be **unattributable** — `§24`'s lesson inverted.

### 5.3 ⚠ THE STABILITY PROBE — **AND IT DID NOT CONFIRM THE DESIGN, IT CHANGED IT**

**Declared under `§20.3` in full at §14.** The probe was run BEFORE this file was frozen, on
the coarsest mesh first and then at every level, and **no threshold, band, cap, window or
label in this document is set from it.**

**Twelve configurations of `rhoPimpleFoam` retaining R2's first-order upwind convective
schemes were tested. EVERY ONE FAILED**, at `t` between **4.1 and 6.4 ms**, across
`maxCo ∈ {0.05, 0.1, 0.2, 0.5, 1.0}`, `nOuterCorrectors ∈ {2, 3, 4}`, relaxation
`∈ {0.5, 0.7, 1.0}`, `transonic ∈ {yes, no}`, tight and widened limiters, cold start and
restart from R2's converged field:

| what was tried | outcome |
|---|---|
| `nOuterCorrectors 2`, maxCo 0.5, relax 0.7 | SIGFPE at `t = 6.44e-03` s |
| `nOuterCorrectors 3`, maxCo 0.5, relax **1.0** | SIGFPE at `t = 4.82e-03` s |
| `nOuterCorrectors 3/4`, maxCo 0.5/1.0, relax 0.7, `transonic` yes **and** no | all SIGFPE at `t = 4.4–5.8e-03` s |
| **widened limiters** `pMinFactor 0.02 / pMaxFactor 20 / limitTemperature [100, 4000]` | **still fails at the same physical time, with every widened limiter saturated** |
| **restart from R2's converged field** (no starting shock at all) | dt collapses to ~2e-07 s and hangs; the instability is **at the shock**, `x ≈ 1.28–1.54` |

**The mechanism, read off the instrumented trace:** at `t = 4.376 ms` the pressure reaches
6.88e+05 Pa (2.3× the inlet total pressure) at `x ≈ 0.806` in the diverging section, `p` hits
its `pMinFactor` floor exactly, `limitTemperature` then binds at **both** ends, and once every
limiter is clipping the velocity runs 1.9e+03 → 8.8e+03 → 3.5e+14 → 7.1e+43 m/s.

> **THE R2 SHOCK PROFILE IS NOT STABLE UNDER A PHYSICAL TIME DERIVATIVE.** Its steadiness at
> L1 and L2 is a property of a relaxation iteration with no time derivative in it, not of a
> discretisation of the transient problem.

**THE CONTROL THAT MAKES THIS EVIDENCE RATHER THAN A LUCKY CONFIGURATION:** with first-order
upwind retained and `maxCo` set to **0.05 — ten times finer than configurations that had
already failed — it still died at `t = 4.11e-03` s.** A step-size instability yields to a
smaller step. This one does not, because it is not one.

**Both TVD variants tested reached `endTime` on the first attempt:**

| scheme | steps to `t = 0.020 s` | `ExecutionTime` |
|---|---|---|
| `limitedLinear(V) 1` | 6 816 | 98.18 s |
| **`vanLeer(V) 1`** ← chosen | **5 476** | **78.51 s** |

`vanLeer` because it is cheaper on the same problem (measured), and because it carries **no
free coefficient** — one fewer number that could be accused of tuning.

**THE FROZEN CONSTANTS, AND WHY EACH IS THE VALUE IT IS:**

| constant | value | why |
|---|---|---|
| `ddtSchemes` | `Euler` | first order in time, matching the scheme family and the more robust of the two |
| `nOuterCorrectors` | **3** | 2 diverged (measured) |
| relaxation (non-final) | **0.7** | 1.0 diverged (measured); `Final` is 1 |
| `transonic` / `consistent` | `no` / `no` | behave identically on the failure that mattered; the simpler formulation is kept |
| **`maxCo`** | **0.5** | **the value the FINE-LEVEL (L3) probe validated.** `maxCo 1.0` also ran to `endTime` **at L1** and would roughly halve the bill — **and it was NOT tested at L3, so it is refused.** Both of this lab's failures on 2026-09-04 were fine-level instabilities the coarse meshes suppressed |
| `maxDeltaT` | `1.0e-04` s | a hard ceiling so `dt` cannot run away; it also makes rule-4 limb N2c computable |
| `pMinFactor` / `pMaxFactor` | **0.1 / 3.0, UNCHANGED from R2** | widening them was tested and **does not help**; they were a symptom, never the cause |
| `constant/fvOptions` | **byte-identical to R2** | and its `limitTemperature` bounds are now a **REFUSAL limb** (N4) rather than a silent backstop |

**ALL THREE LEVELS RAN TO THEIR OWN `endTime` UNDER THE FROZEN CONFIGURATION:**
L1 5 476 steps / 20 ms / 78.5 s · L2 1 560 steps / 8 ms / 76.1 s · **L3 3 404 steps / 8 ms /
661.6 s**. The L3 probe carried **no centreline sampler at all** (`functions {}`), so **no
gate quantity could be read from it, by construction and not by restraint.**

### 5.4 `endTime` — DERIVED A PRIORI FROM GEOMETRY, NOT READ OFF ANY SETTLING TIME

`endTime = 0.080 s`. The slowest adjustment channel is an acoustic signal travelling
**upstream** through the subsonic section downstream of the shock: length ≈ 0.85 m at
`c − u ≈ 400 − 180 = 220 m/s` → **3.9 ms per traverse**. Shock equilibration in a nozzle
needs of order 10–20 such traverses; **0.080 s is ≈ 20.** The full-duct convective traverse
is ≈ 5 ms, so this is also ≈ 16 flow-throughs. **Every input is geometry and the reference
state. No observed settling time enters, and none could: no transient run of this case to
any comparable time existed when this number was fixed.**

### 5.5 THE COMPLETE NUMERICS DELTA — three files, and that is all

| file | change |
|---|---|
| `system/fvSchemes` | `ddtSchemes steadyState → Euler`; the five convective schemes `Gauss upwind → Gauss vanLeer(V) 1`; **`div(phiv,p)` ADDED** (rhoPimpleFoam's pEqn uses the volumetric flux where rhoSimpleFoam uses `phid`; without it the solver aborts at once with `Entry 'div(phiv,p)' not found` — measured, not anticipated) |
| `system/fvSolution` | `SIMPLE → PIMPLE` with the §5.3 constants |
| `system/controlDict.template` | `rhoSimpleFoam → rhoPimpleFoam`; `endTime` iterations → **physical seconds**; `writeControl timeStep → adjustableRunTime`; `adjustTimeStep yes`, `maxCo`, `maxDeltaT` added |

**Nothing else. Eight files byte-identical, enforced by the driver in both directions.**

**Consequence named, not concealed:** `§21.4` accepted R2's first-order scheme *"as
disclosed, with its consequence named — it forces Roache order ≈ 1 … a higher-order R2 is
future work, not a defect concealed."* R3 makes that change — **and it is forced, not
chosen.** The observed order will still be near 1 on a captured shock (TVD limiters revert to
first order at discontinuities), so the demote-only secondary band `p ∈ [0.5, 2.5]` remains
appropriate and **is not moved**.

---

## 6. THE GATE — **UNCHANGED, AND THE COMPARATOR CANNOT PRINT A `PASS`**

| limb | value | provenance |
|---|---|---|
| primary reference | **`x_shock` = 1.250 m** | R1's frozen analytical normal-shock location, **UNCHANGED**; independently confirmed at 1.248513 m (§3) |
| band | **5 %** (half-width 0.0625 m) | **UNCHANGED from R1 and R2** |
| plateau | **`DELTA_X = 6.250e-04 m`** | **UNCHANGED from R2**, which adopted it unchanged from charter `§31`. Not chosen by this document |
| plateau statistic | `ptp` over two adjacent windows `W = endTime/10`, plus their mean drift | **UNCHANGED from R2** |
| reader | interpolating last downward `M = 1` crossing | **UNCHANGED from R2**; resolution 5.2e+10× finer than `DELTA_X` |
| ceiling | **`GATE REACHED`** | charter `§21.2` model-sameness **DIFFERENT** (viscous 2-D NS vs inviscid quasi-1D). **`PASS` is unreachable and `grade_vmfl046_r3.py` contains no code path that prints it** |
| secondaries | `p ∈ [0.5, 2.5]`, GCI ≤ 15 % | **DEMOTE-ONLY** (`§21.3`). They may turn a pass into a fail and may **never** license one; a secondary that does **not** fire is **not** evidence of quality, and the comparator prints that beside the verdict |

**The plateau window now holds 16 samples where R2's held 13** (`endTime/10 = 8.0e-03 s` at
`SAMPLE_DT = 5.0e-04 s`). **A peak-to-peak over more samples can only be larger, so this limb
is STRICTLY STRICTER than R2's at the same unchanged threshold. Nothing is loosened.**

---

## 7. THE TWO PRE-REGISTERED BRANCHES — **BOTH FROZEN BEFORE COMPUTE**

> **BRANCH (a) — EVERY LEVEL PLATEAUS.** Roache triple on `x_shock`: if not `CONVERGING`,
> **`NOT A RESULT`** (rule 5 step 2), value and both triples printed beside it. If
> `CONVERGING`: **`GATE REACHED`** inside the 5 % band with no secondary fired,
> **`GATE FAIL`** outside it or with a secondary fired.
>
> **BRANCH (b) — ANY LEVEL FAILS THE PLATEAU AT `endTime = 0.080 s`.** Verdict
> **`NOT A RESULT`** (rule 5 step 1), with every level's P1/P2/P3 and its multiple of
> `DELTA_X` printed beside it.
>
> **AND IN BRANCH (b) THE FINDING IS NOT ANOTHER NULL.** R3 has a **physical clock**. A
> non-plateau here is a **measured unsteadiness with a frequency in Hz**, computed from the
> same series, and it means the manual's *steady* reference is inapplicable to this
> configuration at this resolution. **That is a finding for Sanaa's desk under `§37.4`'s
> "the question is OPEN", not a reason to widen anything.** Sanaa's 2026-09-04 order binds in
> both halves: **a first `NOT A RESULT` is a waypoint, not a resting place — and gates are
> never widened to fit.**
>
> **NO LOOSENED THRESHOLD, NO LONGER `endTime` AND NO LARGER `maxCo` IS AVAILABLE AS A
> REMEDY IN BRANCH (b).**

---

## 8. COST — **BASIS IS THE MEASURED RATE OF THIS EXACT CONFIGURATION AT ALL THREE LEVELS**

R2 landed at **0.917×** filed because it costed from measured actuals of the configuration it
was re-running. R3 does the same, from the §5.3 probes — **all three of which ran to their own
`endTime` under the frozen settings**.

| level | probe steps | probe `t` | probe `ExecutionTime` | equilibrium `dt` | rate (s/cell-step) |
|---|---|---|---|---|---|
| L1 | 5 476 | 0.02000 s | 78.5 s | 2.0076e-06 s | 4.4803e-06 |
| L2 | 1 560 | 0.00800 s | 76.1 s | 4.1749e-06 s | 3.8131e-06 |
| L3 | 3 404 | 0.00800 s | 661.6 s | 1.8921e-06 s | 3.7963e-06 |

Projection to `endTime = 0.080 s`, **serial, `RANKS = 1`** (matching R2, and keeping every
comparator path exactly as the §12 evidence shows them):

| level | steps | wall | core-min | level cap (≥3×) |
|---|---|---|---|---|
| L1 | 39 848 | 571 s | **9.52** | 30 |
| L2 | 19 162 | 935 s | **15.59** | 50 |
| L3 | 42 282 | 8 218 s | **136.97** | 420 |
| **TOTAL** | | **9 725 s** | **162.08** | **running cap 540** |

**FILED: 180 core-min** (11 % over the estimate). **Running cap 540 ≥ 3× 162.08 = 486.2**;
per-level caps ≥ 3× each level's own estimate. **An overrun STOPS the run (rc 124); it does
not get a new budget.** Serial wall time at the estimate: **2.70 h**.

**cost_basis:** core-min = wall_s × ranks ÷ 60, **MEASURED** from the driver and from
`ExecutionTime`. Dollars **DERIVED** at $0.0513/core-h (owner-stated, `COMPUTE_BUDGET_CHARTER`
§5 — the box cannot read its own billing): 180 core-min = 3.0 core-h → **$0.154, derived, not
measured**; cap $0.462. Under the $25 pre-authorisation. **A predicted-vs-actual row for
`docs/COST_CALIBRATION.md` is owed at completion** (rule 12).

**Honest caveat on the basis:** every probe ran on a box also running other work
(load average 4.9–11.2 of 16 cores), as did R2's own actuals. The rates are therefore
contended in the same direction as the basis they are compared against.

**Ratio to R2: 1.92×.** R2 was 60 000 steady iterations; R3 is ~101 000 adaptive time steps
with 3 outer correctors each. The physics being asked for is different — physical time, not
pseudo-time — and it costs what it costs.

---

## 9. THE GRADING PIN — **COMPLETE, NOT "TO BE PINNED"**

The grading path is fixed at this pre-registration. `git hash-object` gives the blob before
the commit exists, so there is no window in which this reads "to be pinned by blob" — the
defect that forced VMFL046-R2's `§14` to be completed by a dated addendum (`9145dff7`) after
the queue daemon logged `GRADER-FREEZE … UNPINNED`.

| artifact | blob sha |
|---|---|
| **`grade_vmfl046_r3.py`** (**THE GRADING PATH**) | **`2f0eb7a8ba0718b484fadcd5f4c128cd9450eff3`** |
| `run_vmfl046_r3.sh` | `14062b5c2c95f3e13fc5664a3e72a45da9a3c968` |
| `case/0/T` | `e3dbbd24fffbbcaba1fe5424502d802e3d98b5b3` |
| `case/0/U` | `1035057ac3c4703a1439049b01a274ce10374284` |
| `case/0/p` | `b2bdcfcf658a27eb289f9ce01c2cfbab14b8baec` |
| `case/constant/fvOptions` | `cc81891fd7445e2777a245e16baf0c9b829ec299` |
| `case/constant/momentumTransport` | `f7d93d54ebae9785586564ad6eb86faf764ebcc3` |
| `case/constant/thermophysicalProperties` | `051327833c9cf108289684de01e03618f26eab66` |
| `case/constant/turbulenceProperties` | `f7d93d54ebae9785586564ad6eb86faf764ebcc3` |
| `case/system/blockMeshDict.template` | `26acdba2b5a68fc0c220c162c0b0ac84e3080948` |
| `case/system/controlDict.template` | `bbbd4ac5874b62dac668d3b6a76ebb4c93af270e` |
| `case/system/fvSchemes` | `415eab1a859050b5a34cae9f6eba2493ad0cebf9` |
| `case/system/fvSolution` | `9be09f0642f3ec592be1485e39e4f9538b6265c9` |

**The driver re-verifies every `case/` blob against `HEAD` at launch and ABORTS on any
mismatch** (exit 6). **⚠ Disclosed limitation, carried forward from R2 and not fixed here:
that check pins to `HEAD`, not to this registration's own freeze commit; rule 6 is the
backstop.**

---

## 10. THE DECLARED DEPARTURE (N2) — **RULE 4's `ExecutionTime`-COUNT LIMB**

**Declared here, on the face of this document, BEFORE the answer is known**, exactly as
VMFL051's freeze declared its own DEPARTURE 2 (*"replaces the steady-iteration
`ExecutionTime` count clause — which a transient adaptive-step solver can never satisfy —
with a direct check of the invariant it protects"*).

R2's limb was `count of ExecutionTime lines == endTime`. That equals the iteration count
**only** for a steady solver where one iteration prints one line and `endTime` **is** the
iteration count. For R3, `int(round(0.080)) = 0` against ~40 000 lines, and the limb would
**refuse every level**. **RULE 4 IS NOT THE PROBLEM; THAT IMPLEMENTATION OF IT IS.**

**The replacement is STRICTLY STRONGER, and every term is computable from frozen constants:**

| limb | check |
|---|---|
| **N2a** | `n(ExecutionTime) == n("Time = ")` — every advanced step printed its cost; catches a log truncated mid-step |
| **N2b** | last `Time` == `endTime` within `maxDeltaT` — the run advanced all the way |
| **N2c** | `n("Time = ") >= endTime / maxDeltaT` = **800** — it cannot have got there in fewer steps |
| **N2d** | the `Time` sequence is **STRICTLY INCREASING** — **catches a restart splice that a bare count never would, and which R2's limb did not test at all** |

Every other rule-4 limb is unchanged: `RUN_RC == 0`, no `FOAM FATAL`, an `End` line, last
time dir == `endTime`, `T U p` present at `endTime`, and **the age guard** — every field at
`endTime` newer than the case's own `0/T`, with the driver refusing to start on a level that
already holds a numeric time dir.

**The five N2 limbs are exercised by `--selftest` against planted logs** (complete run,
truncated log, stopped early, too-few-steps, restart splice) and all five behave as designed.

---

## 11. THE PLANTED CONTROLS (rule 3) — **AND PLANT C IS REPLACED, NOT PATCHED**

`grade_vmfl046_r3.py` refused to grade R2 on its own PLANT C. **The refusal was correct and
the control was wrong.** R2's PLANT C shifted the Mach **field** across the whole window and
asserted the `ptp` of the `x_shock` **series** was unchanged. That premise — that a rigid
field shift translates the interpolated series — holds only when the profile **shape** is
identical across samples, **i.e. only when the shock is already steady**. Measured on R2's own
data:

| level | base ptp | old PLANT C statistic | old PLANT C |
|---|---|---|---|
| L1 (ptp 1.15e-13, steady) | 1.154632e-13 | 1.07e-14 | PASS |
| L2 (ptp 2.57e-04) | 2.566666e-04 | **3.953e-05** | **REFUSE** |
| L3 (ptp 1.15e-01) | 1.150264e-01 | **2.962e-05** | **REFUSE** |

> **A CONTROL WHOSE VALIDITY DEPENDS ON THE ANSWER IT IS CHECKING IS NOT A CONTROL.** This is
> the **third** distinct plant-design defect in this family — after **CANCELLATION** (a plant
> covering the whole reduction set) and **ABSORPTION** (an interior plant inside an
> already-wide range) — and it is a new class: **ANSWER-DEPENDENCE**. Note also that the old
> arm would have refused at **L3 as well**, so the defect was never confined to the level that
> tripped first.

**THE REPLACEMENT, IN TWO ARMS, EACH WITH AN ANSWER-INDEPENDENT PREMISE:**

**PLANT C1 — the cancellation demonstration, moved to the REDUCTION where the claim lives.**
Add the plant to every member of the `x_shock` **series** and assert the `ptp` is unchanged;
then add it to the **argmax** alone and assert the `ptp` rises by exactly the plant.
Premise: `max(x+d) − min(x+d) = max(x) − min(x)`, **an identity of the reals** — true whether
the shock is steady, hunting over 38 cells, or absent. Measured on R2's real window-A samples:

| level | base ptp | C1 inert (all + Δ) | C1 live (argmax + Δ) |
|---|---|---|---|
| L1 | 1.154632e-13 | change **0.000000e+00** | **+1.000000e-02** |
| L2 | 2.566666e-04 | change **0.000000e+00** | **+1.000000e-02** |
| L3 | 1.150264e-01 | change **0.000000e+00** | **+1.000000e-02** |

**It is not a tautology and it can fail:** it fails the moment `ptp` is mutated into a
reducer that is not translation-invariant — a relative spread, a normalised range, a
`max|x|` — a mutation that would silently change the plateau verdict. The **live** arm proves
the inertness comes from **the covering** and not from a dead reducer. Both refusals are
exercised in `--selftest`.

**PLANT C2 — the field-level contact PLANT C had, with the steadiness premise removed.**
Recover the planted displacement **per sample, independently**, and require each within
**25 % of the plant** — PLANT A's already-frozen, answer-independent tolerance, applied N
times instead of once. **It asserts nothing about the relationship between samples, which is
exactly where the old premise entered.** Measured on R2's real windows:

| level | `d_i` range | worst `|d_i − Δ|` | as % of Δ |
|---|---|---|---|
| L1 | 1.004635e-02 … 1.004635e-02 | 4.635e-05 | **0.46 %** |
| L2 | 1.000520e-02 … 1.004473e-02 | 4.473e-05 | **0.45 %** |
| L3 | 9.993160e-03 … 1.004134e-02 | 4.134e-05 | **0.41 %** |

**54× inside tolerance at every level, including the one hunting over 38 cells.** And C2's
own spread statistic at L2 is **3.953e-05 — identically the old PLANT C's refusal figure**,
so this is demonstrably **the same measurement**, moved from a between-sample invariance
premise to a within-sample read-back premise.

**What is given up, said plainly:** C1 and C2 no longer assert that a field-level rigid shift
leaves the `ptp` unchanged. **That statement is false for a hunting shock — R2 measured it
false. DELETING A FALSE ASSERTION IS THE REPAIR, NOT A LOSS OF COVERAGE.**

**The full plant set, and every arm is a REFUSAL, never a printed diagnostic:**

| plant | target | design |
|---|---|---|
| **A** | the GATE reader | a `+1.000e-02 m` profile shift; the reader must recover it to 25 % of the plant |
| **B** | the PLATEAU reducer | the plant into the window's **current MAXIMUM** (a proper subset), `ptp` must rise by ≥ 0.75Δ |
| **C1** | the reduction's translation-invariance | inert arm + live arm, premise an identity of the reals |
| **C2** | the reader on **each** window profile | per-sample read-back, tolerance 25 % of the plant |
| **D** | the physical `T` field | a uniform plant into a scratch copy, read back per value |
| **N4** | the frozen `limitTemperature` bounds | **REFUSE** if `T` at `endTime` reaches within 1 % of `[150, 2000]` K. Those bounds bound at **both** ends in every failed probe of §5.3; a run in which they bind is not reporting the registered physics, and printing that as a diagnostic beside a verdict would be worse than never computing it |

**`--selftest`: 30 arms, ALL PASS** — readers, quantum discrimination, C1 on steady/hunting/
drifting series plus two mutant refusals, C2 with three mutant refusals (dead, half-scale, and
R1's node-snapping reader at plant = `DELTA_X`), A and B with their mutants, the five N2 limbs,
four Roache states and three N4 arms. **Per `§39.5` this proves LOGIC and NOT INTERFACE; §12
is the interface evidence.**

---

## 12. `§39.5` — EVERY PATH THE COMPARATOR READS, SHOWN SOLVER-WRITTEN ON DISK

**The CLAUSE-B smoke ran under a DELIBERATELY BARE ENVIRONMENT** —
`env -u WM_PROJECT_DIR -u FOAM_APPBIN PATH=/usr/bin:/bin` — which is **the exact condition
that made every one of VMFL072-R2's five queue rows refuse at rc = 2**. The driver sourced
`/usr/lib/openfoam/openfoam2606/etc/bashrc` itself, asserted `blockMesh` and `rhoPimpleFoam`
on PATH **after** sourcing, and ran: **rc 0, 0.0167 core-min, L1 only, `endTime` 4.0e-04 s.**

`grade_vmfl046_r3.py --paths` against that real run root reports **all 10 L1 paths OK**:

```
L1/RUN_RC · L1/log.rhoPimpleFoam · L1/system/controlDict · L1/system/blockMeshDict
L1/0/T · L1/0.0004/{T,U,p} · L1/postProcessing/centreline/{0.0001,0.0004}/line_T_U.xy
```

The sampler wrote **321 rows** in the five-column `x T Ux Uy Uz` layout that
`read_centreline_raw` parses, into directories named as **exact decimals**
(`0.0001, 0.0002, 0.0003, 0.0004`) that `centreline_history`'s regex matches, and the log
carries exactly one `End`.

**⚠ AND A DEFECT IN THE ENUMERATOR ITSELF, FOUND BY POINTING IT AT REALITY AND FIXED BEFORE
FREEZING.** On its first run, `--paths` **refused** the smoke root, because it called the
strict `read_controls`, which asserts the graded `endTime`. **A path enumerator that refuses
every run root it could actually be pointed at before the graded run exists is `§39.5`'s own
failure in miniature — an instrument internally immaculate that never touches reality.**
`check_paths` now reads the controls non-strictly; that non-strict path **is not reachable
from `grade()`**, so no verdict can be produced without every assertion having passed. Both
behaviours are verified: `--paths` enumerates the smoke root, and `grade()` **refuses** it
(exit 2, *"endTime 0.0004 is not the GRADED 0.08"*).

**⚠ AND THE CHECKER IS NOT `§39.5` COMPLIANCE.** `check_freeze_ready.py`'s C2 defers every
runtime-composed path as **UNDETERMINED** — for R2 that was 6 of 7 driver paths. **The
driver's own explicit existence loop (§0, exit 2) is what discharges `§39.5` on the driver
side, and this document's §12 is what discharges it on the comparator side.** The checker has
two further declared gaps: it **cannot catch a wrong field name**, and it **cannot catch a
missing runtime environment** — which is why the smoke above was run under a bare PATH.

---

## 13. WHAT THIS REGISTRATION KNOWS, AND WHAT IT DOES NOT PRETEND

### 13.1 THE FREEZE CLAIM — stated so no reader supplies the most flattering reading

> **THIS DOCUMENT IS FROZEN BEFORE THE R3 RUN. IT IS NOT FROZEN BEFORE THE R2 DATA, AND IT IS
> NOT FROZEN BEFORE THE READING.** R2's L1/L2/L3 data and the inviscid arm exist on disk; the
> drafting lane read all of it and §2 publishes what it says. **A registration frozen after
> its predecessor's data existed carries less evidentiary weight than one frozen before, and
> this document does not pretend otherwise.**

**What protects it anyway, as an argument a reader can check rather than as reassurance:**
1. **The gate, band and plateau threshold are not this document's to set.** All three are
   carried forward unchanged and their provenance is R1, R2 and charter `§31`.
2. **The remedy was pre-committed on 2026-09-02**, in R2's branch (b) and in charter
   `§20.2(c)`, before any of the data in §2 existed.
3. **The one number this document does choose — `endTime = 0.080 s` — is derived from
   geometry and the reference state alone** (§5.4), and no transient run of this case to any
   comparable time existed when it was fixed.
4. **Every stability constant was fixed by a probe that could not read a gate quantity**, and
   the L3 probe carried no sampler at all.

### 13.2 WHAT THIS DOCUMENT CANNOT VERIFY, STATED PLAINLY

- **The settling time is an estimate, not a measurement.** `endTime = 0.080 s` is ≈ 20
  acoustic traverses by an a-priori argument. **If it is short, R3 grades `NOT A RESULT` on
  branch (b) and that is the answer** — a longer clock is not available as a remedy.
- **The probes were run to 8–20 ms, not to 80 ms.** Stability is demonstrated over 10–25 % of
  the graded duration at every level. **A late-onset instability is not excluded**, and the
  per-level caps (which stop the run rather than extend it) are the backstop.
- **`maxCo 1.0` was stable at L1 and would roughly halve the bill. It was not tested at L3 and
  is refused.** That is a deliberate ~2× cost paid for a stability margin at the level that
  decides the verdict.
- **Serial, `RANKS = 1`**, giving a 2.70 h wall time at the estimate. Parallel decomposition
  would cut wall time without cutting core-minutes, at the price of `decomposePar`/
  `reconstructPar` machinery that would invalidate the §12 path evidence. **Not taken; flagged
  for the supervisor.**
- **The `HEAD`-not-freeze-commit pin limitation of §9 is carried forward from R2 and is not
  fixed here.**

---

## 14. `§20.3` DECLARATION — EVERY QUANTITY THE PRE-FREEZE WORK REVEALED

**These are NOT CLAUSE-B smokes and this document does not frame them as such.** Charter
`§20.3` requires that a pre-freeze run of this team either obey CLAUSE B or be **declared as a
pre-freeze production run with every quantity it revealed named explicitly**, so a reader can
price which decisions were taken with an answer in hand. **Silence about a revealing smoke is
the defect.**

**WHAT RAN:** the twelve failed configurations and the three surviving probes of §5.3, plus
the `rhoCentralFoam` attempt of §5.2 and the R2/inviscid re-analysis of §2. All in the
scratchpad, never in a run root, single-core.

**EVERY QUANTITY THEY REVEALED, EXHAUSTIVELY:**
- that `rhoSimpleFoam` contains no `ddt` term (a source fact, not a run);
- that `div(phiv,p)` is a required `fvSchemes` entry for `rhoPimpleFoam`;
- the sampler's output path, filename, row count, column layout and directory naming;
- per-cell-step rates 4.4803e-06 / 3.8131e-06 / 3.7963e-06 s and equilibrium time steps
  2.0076e-06 / 4.1749e-06 / 1.8921e-06 s;
- that twelve first-order-upwind configurations die at `t = 4.1–6.4 ms` and two TVD
  configurations do not, with their step counts and execution times;
- the blow-up mechanism and its location (`x ≈ 0.64–0.93`, limiters saturating);
- that `rhoCentralFoam` aborts at step 58;
- and, from **R2's already-graded artifacts**, the §2 and §11 numbers, all of which are
  **already on the public record in register row #57 and charter `§24`/`§31`/`§35.1`**.

**WHAT NONE OF IT IS:** ⚠ **not one of these is an R3 gate quantity.** No R3 shock location,
plateau, observed order or GCI exists, at any level, because **the L3 probe carried no
centreline sampler and the L1/L2 probes ran to 20 ms and 8 ms against a graded 80 ms.**
**No threshold, band, cap, window or label in this document was set from any of it**, and the
one number this document does choose is derived from geometry alone (§5.4).

**AND THE ONE THING THE PROBES DID CHANGE, DISCLOSED:** they changed the **design**. The
route arrived as "two lines of numerics delta" and the probe refuted that: first-order upwind
cannot be integrated in physical time on this case at all, and the control at `maxCo 0.05`
proves it. **The probe was not a formality before the freeze; it is what earned it.**

---

## 15. FILES

| what | path |
|---|---|
| this registration | `cases/ansys_verification/VMFL046-R3/PREREGISTRATION.md` |
| **the grading path** | `cases/ansys_verification/VMFL046-R3/grade_vmfl046_r3.py` |
| the driver | `cases/ansys_verification/VMFL046-R3/run_vmfl046_r3.sh` |
| case inputs | `cases/ansys_verification/VMFL046-R3/case/` (11 files) |
| run root (**must not exist or be empty at launch**) | `verification/runs/ansys_verification/VMFL046-R3/` |
| predecessor, **READ-ONLY** | `cases/ansys_verification/VMFL046-R2/` · `verification/runs/ansys_verification/VMFL046-R2/` |
| the inviscid control arm, **READ-ONLY** | `verification/runs/ansys_verification/VMFL046_INVISCID/` |
