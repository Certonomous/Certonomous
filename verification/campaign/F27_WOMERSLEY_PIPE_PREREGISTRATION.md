# F27_WOMERSLEY_PIPE — PRE-REGISTRATION

**Team:** cfd. **Rung:** F27. **Written 2026-08-27, BEFORE any compute in the
registered run root.** **Capability cell claimed: `3D · unsteady ·
incompressible` (`docs/capability/cfd_GRID.md`).**

**Run root:** `verification/runs/F27_WOMERSLEY_PIPE_runs`. **Absence verified in
this document's own preparation at 2026-08-27T17:03:41Z** by
`bash cases/F27_WOMERSLEY_PIPE/run_f27.sh --preflight`, which prints
`run root … is ABSENT` and exits 0 at zero compute. No solver has run against
this registration.

Verdict vocabulary is `CLAUDE.md` standing rule 1 and nothing else. Nothing in
this file is sent anywhere (standing rule 7).

---

## 1. The case, and what it is FOR

Pulsatile (Womersley) laminar flow of an incompressible Newtonian fluid in a
**circular pipe**, driven by a uniform oscillatory axial body force
`f(t) = A cos(omega t) z-hat` (= `-1/rho dp/dz`), solved with `pimpleFoam` in
PISO mode, laminar, axially cyclic.

**Exact solution** (the Bessel-function Womersley profile, in its
modified-Bessel form):

    u_z(r, t) = Re[ (A / (i omega)) ( 1 - I0(lambda r) / I0(lambda R) ) e^{i omega t} ],
    lambda = sqrt(i omega / nu),      u_r = u_theta = 0,      p = const

`I0(lambda r)` is identically `J0(i^{3/2} alpha r / R)`; the identity is DRIVEN
in `exact_f27.py::control_bessel_two_independent_implementations`, which also
cross-checks `scipy.special.iv` against `mpmath.besseli` to 1e-13 and plants
order 1 for order 0 to prove the check can fail.

**Frozen constants.**

| symbol | value | note |
|---|---|---|
| `R` | 1.0 | pipe radius |
| `LZ` | 1.0 | cyclic axial length |
| `omega` | `2 pi` | `PERIOD = 1` |
| `A` | 1.0 | kinematic body-force amplitude |
| **`alpha`** | **4.0 EXACTLY** | Womersley number `R sqrt(omega/nu)`, exact by construction of `nu` |
| `nu` | `pi/8 = 0.39269908169872414` | `= omega R^2 / alpha^2` |
| `U_REF` | `A/omega = 0.15915494309189535` | the Womersley velocity scale, the normaliser |
| `N_PERIODS` | 5 | derived in §7, not inherited |
| `T_END` | 5.25 | `5 T + T/4`, the locked phase |

**This rung exists to close one capability cell.** The cfd capability grid
records that this team has **never produced a CONVERGING 3-D triple**.
F25_DUCT3D is the other attempt on that cell. F27 is a *different* physics
(unsteady, not steady) on a *curved* domain, so the two are not redundant.

**Distinct from F21_WOMERSLEY**, which is the 2-D planar channel at `alpha = 5`
with a `cosh` profile on a uniform Cartesian mesh. F27 is the circular pipe at
`alpha = 4` with a Bessel profile on a butterfly O-grid. **Nothing is inherited
from F21's ladder** — see §7 (L-346) and §9.

---

## 2. GEOMETRY: a genuine 3-D butterfly O-grid, NOT an axisymmetric wedge

**Registered geometry: a GENUINE 3-D BUTTERFLY (O-GRID) MESH of the full
circular cross-section, refined by exactly 2 in ALL THREE directions across the
levels.** A wedge was NOT registered and is not a fallback taken here: the
sizing fits (§8), so the stronger claim is made.

Five blocks per cross-section: one `nc x nc` **Cartesian core** block whose
corners sit at `r = CORE_FRAC · R = 0.5`, and four `nr x nc` **O-ring** blocks
between one core edge and one quadrant of the wall. The wall quadrants are
`arc` edges through the points at 0°, 90°, 180° and 270° on `r = R`, so the
boundary is the **circle**, not a polygon inscribed by the block corners alone.
Cross-section cells `= nc^2 + 4 nc nr`; total `= that x nz`.

`cases/F27_WOMERSLEY_PIPE/case/system/blockMeshDict.template`.

---

## 3. MESH_STANDARD, QUOTED, AND MEASURED AT ALL THREE LEVELS BEFORE FREEZING

`docs/standards/MESH_STANDARD.md` **§8.1 BUILD BEFORE YOU FREEZE**, quoted:

> **No cfd mesh-ladder pre-registration is frozen until at least one level has
> been BUILT, `checkMesh`'d, and SHOWN ADMISSIBLE against the gates that
> registration will carry. Template speed does not exempt it.**

**All three levels were built and `checkMesh`'d before this document was
frozen**, in a scratch arm outside the run root, through the frozen
`build_f27.py` and the frozen `blockMeshDict.template`.

The gates, quoted:

* **§3.1 Max non-orthogonality: hard gate 70 degrees**, warning band 65–70.
* **§3.2 Max skewness: hard gate 4**, boundary faces included.
* **§3.3 Aspect ratio: advisory at 1000, never a lone rejection.**

**MEASURED, from `log.checkMesh` at each level:**

| level | nc/nr/nz | cells | max non-orthogonality | max skewness | max aspect ratio | `Mesh OK` |
|---|---|---|---|---|---|---|
| coarse | 8 / 8 / 12 | 3,840 | **28.5855°** | **0.9643** | 2.2193 | yes |
| medium | 16 / 16 / 24 | 30,720 | **36.1589°** | **0.9799** | 2.5287 | yes |
| fine | 32 / 32 / 48 | 245,760 | **40.4226°** | **0.9897** | 2.7379 | yes |
| **gate** | | | **≤ 70°** | **≤ 4** | advisory 1000 | |

**Every level passes both hard gates with margin, and the aspect ratio is three
orders below the advisory.**

**THE TREND IS UPWARD AND IT IS DISCLOSED, because F1 died of exactly this.**
`MESH_STANDARD` §8.1 records F1's ONERA-M6 ladder at **84.64 / 86.02 / 86.78°**,
worsening under refinement and **asymptoting toward 90°** — "a fixed fraction of
the mesh, not a marginal miss — so no finer level could ever have cleared it."
F27's non-orthogonality also rises with refinement: **28.59 → 36.16 → 40.42°**,
increments **+7.57, +4.26**, ratio **0.56**. The increments are *shrinking
geometrically*, so the sequence converges to roughly **45.8°** rather than to
90°, and the fine level sits **29.6° below the gate**. This is a converging
geometric artefact of the fixed core-to-ring transition angle, not F1's
divergence. It is recorded here as a measured trend and not waved past.

Skewness likewise converges (0.964 → 0.980 → 0.990, toward ~1.0), four times
below the gate.

**§8.2 `blockMesh` REFUSING IS A DIAGNOSTIC.** `blockMesh` accepted this
topology at the first attempt at every level, rc 0, with `Detected cyclic
patches; ordering boundary faces`. **No `polyMesh` was hand-written anywhere in
this rung**, and `build_f27.py` says so in its own abort message.

**§9.2 THE SIMILARITY CLAUSE — the required read-back.** The clause demands the
ACTUAL value of every grading and first-cell parameter, **read back from the
written dictionary or the built mesh, never from the parameter that was
requested**. F27 registers **NO grading parameter and NO first-cell parameter at
any level**: every block at every level is `simpleGrading (1 1 1)`, so the
branch-flip hazard has no branch to flip. `build_f27.py::read_back_grading`
nevertheless parses the **WRITTEN** `system/blockMeshDict` at each level, finds
exactly 5 `simpleGrading` triples, and **refuses** unless all five are exactly
`(1 1 1)`. Measured, all three levels: `{(1.0, 1.0, 1.0)}`.

Beside it, read back from the **built** mesh: min/max cell volume ratio
**2.9581 / 3.4301 / 3.7210** and total volume **3.121445 / 3.136548 / 3.140331**
against `pi R^2 LZ = 3.141593` — a faceting deficit of 0.64 % / 0.16 % / 0.04 %,
**second order, an independent confirmation that the family is geometrically
converging.** Recorded in `MESH_LINE.txt` per level.

---

## 4. THE LADDER, AND WHY IT IS A LADDER

| level | nc | nr | nz | cells | steps to `T_END` | `dt` | model radial cells |
|---|---|---|---|---|---|---|---|
| coarse | 8 | 8 | 12 | 3,840 | 672 | 1/128 | 12 |
| medium | 16 | 16 | 24 | 30,720 | 1,344 | 1/256 | 24 |
| fine | 32 | 32 | 48 | 245,760 | 2,688 | 1/512 | 48 |

`nc`, `nr`, `nz` and the step count all **double**; cells go **x8**;
`r21 = r32 = 2.000000` exactly at `dim = 3`, with `ratio_gap = 0.00e+00`.
`R`, `LZ` and `CORE_FRAC` are held fixed. Driven in
`exact_f27.py::control_ladder_is_geometrically_similar`.

**`dim = 3` is declared, never defaulted** (`VERIFICATION_CHARTER` §3.1) and is
printed beside every order and every GCI.

**Decomposition:** `simple`, `n (1 1 4)`, 4 subdomains, **axial bands; the
butterfly cross-section is never cut**. `nz` is divisible by 4 at every level.
**Decomposition seed: `none`** — `simple` is a deterministic geometric
decomposition and carries no RNG.

---

## 5. THE DIMENSIONLESS GROUPS, AND THE F21 FAILURE RECORDED BESIDE THEM

A ladder that refines `dt` proportional to `h` holds the Courant number fixed
and makes the **diffusion number `Fo = nu dt / h_r^2` double every level**.
Measured across the cfd unsteady family (cfd-supervisor's own triage,
2026-08-27):

| case | outcome | `Fo` across the ladder |
|---|---|---|
| F21_WOMERSLEY | **fine level DIVERGED** | 10.72 → 21.45 → **42.89** |
| F22_LAMB_OSEEN | PASS x2 | 0.147 → 0.295 → 0.590 |
| F18b_TG2D_EXT | running | 0.208 → 0.415 → 0.830 |
| F18_TG2D | PASS, closed | 0.052 → 0.104 → 0.208 |
| **F27_WOMERSLEY_PIPE** | **this registration** | **0.4418 → 0.8836 → 1.7671** |

`h_r = R / (nc/2 + nr)` is the level's own radial spacing. **F27's fine level
runs at 1/24 of the diffusion number F21's diverging fine level reached**, and
about 3x the highest value the family has measured a PASS at. Courant number is
a ladder invariant at **0.0181** (to 0.1 %, the composite model's own `R_eff`
drift) — two orders below any stability concern; `Re` here is O(1).

**`FO_CEILING = 5.0` is registered before compute** and
`exact_f27.py::control_diffusion_number_and_courant` REFUSES the registration if
the fine level exceeds it.

**THIS IS NOT A CAUSAL CLAIM AND IS NOT OFFERED AS ONE.** The supervisor's
triage explicitly withheld mechanism: F21's mode was smooth (0.0 % energy in the
top 3 wavenumbers), wall-localized, two-dimensional and at wavenumber 6 — not
checkerboard — at `Re = 1.3`, and the wall stencil at `h = 0.0039` and `backward`
BDF2 under PISO with `nOuterCorrectors 1` remain live alternatives. **`Fo` is
registered here as the measured distinguishing group with the failure recorded
beside it, and nothing more.** What actually protects this rung is §6's
uniformity limb, which tests the invariance directly whatever breaks it.

---

## 6. THE GATES

### 6.1 Two GATED quantities

Both at the locked phase `t = T_END = 5.25`, both banded from **one declared
parameter**, `BAND_FACTOR = 5.0`, applied to the composite model's fine-level
prediction (§6.3).

**`G-F27-1_E2_velocity_locked_phase`** —
`E2 = sqrt( sum_i V_i |U_i - U_exact(r_i, T)|^2 / sum_i V_i ) / U_REF`, over
every cell. **Volume-weighted**: the butterfly's cells differ in volume by up to
3.72x, and an unweighted mean would grade the small cells twice.

* prediction at fine: **3.026369e-04**
* **band: [6.052738e-05, 1.513185e-03]**, reference 0.0, `dim = 3`

**`G-F27-2_Einf_axial_velocity_locked_phase`** —
`Einf = max_i |u_{z,i} - u_exact(r_i, T)| / U_REF`. A **different norm** of the
same error field: `L-infinity` is set by the **worst cell**, which is where a
wall-localized mode of the kind that killed F21's fine level appears first.

* prediction at fine: **5.698921e-04**
* **band: [1.139784e-04, 2.849461e-03]**, reference 0.0, `dim = 3`

### 6.2 One quantity REPORTED-NOT-GATED, and the reason is MEASURED

**`R-F27-W_bulk_mean_axial_velocity`** — `W = sum V u_z / sum V / U_REF` — is
computed, its triple is formed, **its observed order and GCI are printed, and NO
VERDICT IS ATTACHED TO IT.**

**Why, with the number.** A zero-compute coarse pilot run before this document
was frozen (§10) measured `W`'s error against the same-stencil reference as
**-7.27e-03** where the radial model predicted **+9.57e-04**: **wrong sign, 7.6x
magnitude.** A signed integral functional on this mesh is dominated by the
inscribed-polygon geometry and by cancellation, and the registered model cannot
read it. **L-345's rule is that a quantity the registered model cannot predict
is registered REPORTED-NOT-GATED, not banded around a prediction already known
to be wrong.** Banding it anyway would be registering around a known defect.

Three further REPORTED channels, all **pure error** because the exact solution
is identically axial, `z`-invariant and axisymmetric:
`R-F27-E_perp_spurious_cross_flow`, `R-F27-A_z_axial_non_uniformity`,
`R-F27-A_theta_azimuthal_non_uniformity`.

### 6.3 The composite model the bands come from, and its ONE approximation

The physics reduces exactly to a 1-D **cylindrical** finite-volume heat
equation: annular control volumes `V_j = 2 pi r_j dr`, face areas
`2 pi r_{j±1/2}`, the no-slip face gradient `(0 - u_P)/(dr/2)` at the wall, the
axis symmetry carried by the **vanishing face area** there (not by a ghost
cell), `backward` BDF2 with OpenFOAM's Euler-implicit first step, the explicit
cosine source at the new time level, started from the exact profile at `t = 0`.
Solved **directly at all three levels** — nothing is extrapolated.

The model is solved on `MODEL_NR = nc/2 + nr = 12 / 24 / 48` radial cells: **the
level's OWN radial cell count along the +x ray** (through the Cartesian core,
then the O-ring), so the model refines by exactly 2 with the mesh.

**THE COMPOSITE STEP, and it is the one thing here that is an approximation
rather than a reduction.** The butterfly's wall faces are **chords**, so the
meshed domain is a polygon **inscribed** in the pipe, short of `pi R^2` by
`O(h^2)`. That deficit is the **dominant** error channel at these resolutions.
The model therefore places its wall at
`R_eff(level) = sqrt(A_mesh(level) / (pi LZ))`, the radius of the circle with
the **built mesh's own cross-sectional area**, while measuring error against the
**true** (radius `R`) exact solution. `R_eff = 0.996788 / 0.999197 / 0.999799`;
`R_eff -> R` at second order, so the composite prediction is still `O(h^2)`.

`A_MESH` is registered as a NUMBER per level and **`build_f27.py` REFUSES if the
mesh it builds does not reproduce the level's registered same-stencil reference
to 1e-9** — measured at all three levels, difference `-1.1e-16 / +1.1e-16 /
-3.3e-16`.

**What the model still cannot see, stated because a band that overstates its
basis is worse than a wide one:** the azimuthal discretisation, the Cartesian
core block, and the up-to-40.4° non-orthogonality of the ring. **`BAND_FACTOR =
5.0` is a DECLARED JUDGEMENT covering that mismatch. It is not a measurement,
and it was fixed before the pilot in §10 was read.**

### 6.4 Rule 5 limb 1 — three measured states per level, not two

| limb | measurement | tolerance |
|---|---|---|
| iterative | census over **every** time step's final `Ux`, `Uy`, `Uz` and `p` residuals | `p` ≤ 1e-10, `U` ≤ 1e-12 |
| plateau (periodicity) | `\|\|U(T) - U(T-T_period)\|\|_2,V / U_REF` at every level | `PERIOD_TOL = 1.0e-06` |
| **plateau (uniformity)** | `A_z` (each cell against its own z-column mean) and `A_theta` (each cell against its image under the mesh's exact 90° rotation) | `UNIFORMITY_FRACTION = 0.1` x **that level's own predicted `E2`** |

**The uniformity limb is the F21 instrument made explicit.** F21's fine level
diverged into a mode in a direction its exact solution is invariant along, and
was caught only because that ladder happened to carry a plateau gate at all.
Here the invariance is tested **directly**: a level whose `A_z` or `A_theta`
exceeds its tolerance is `NOT_UNIFORM` and rule 5 limb 1 turns the row into
`NOT A RESULT` **before any grid claim is made**.

**Declared blind spot.** The butterfly's symmetry group is D4, so `A_theta`
reads exactly zero on any `cos(4k theta)` mode. That class is carried in full by
`G-F27-1` and `G-F27-2`, which compare every cell against `u_exact(r)` and have
no null space. The planted control uses wavenumber **3** precisely because
wavenumber 4 would be invisible by construction.

### 6.5 Rule 5 order, and the one-way gate

`scripts/roache_triple.py::grade_ladder` is called **exactly once** in
`grade_f27.py` (AST-censused: 1 call node, line 985) and **rule 5 is reached
through that call and through nothing else**. GCI at `Fs = 1.25`, never quoted
on a non-monotone triple. The gate may only turn a PASS or GATE FAIL **into**
NOT A RESULT.

---

## 7. L-346 — EVERY RESOLUTION FLOOR DERIVED FROM **THIS** LADDER

L-346 cost 26.87 core-min and `NOT A RESULT` x2 on F17b, which inherited F17's
iterative floor byte-for-byte. **Nothing here is inherited.** Every floor below
is derived from **this** ladder's predicted fine-level discretisation error
(`E2_pred(fine) = 3.026369e-04`) and each derivation is **DRIVEN** in
`exact_f27.py::control_L346_resolution_derived_from_this_ladder`, which REFUSES
the registration if any of them falls outside its window.

1. **`N_PERIODS = 5`.** The model's period-to-period change at the fine level is
   **MEASURED at every period boundary**: `1.007e-05 → 6.251e-07 → 6.453e-08 →
   6.662e-09 → 6.878e-10`, a factor ~10 per period (the slowest viscous mode
   decays as `exp(-j_{0,1}^2 nu T / R^2) = 0.103` per period at `alpha = 4`).
   The residual transient at `T_END` is **5.4e-06 of the predicted fine `E2`**.
   The control requires the decay to be **monotone** and the first boundary's
   change to be **≥ 10x** the change at `T_END`, so `N_PERIODS` is shown to be
   doing measurable work rather than assumed adequate.
2. **`PERIOD_TOL = 1.0e-06`**, inside its derived window
   **[1.172e-07, 3.026e-05]**: at least 10x the model's worst predicted
   period-to-period change, and at most 0.1x the predicted fine `E2`.
3. **`W_PERIOD_TOL = 2.0e-06`**, inside **[6.064e-07, 2.798e-05]** by the same
   rule (a REPORTED channel, derived the same way regardless).
4. **The iterative floor.** `p` tolerance 1e-10, `U` tolerance 1e-12,
   `nCorrectors 2`, `nNonOrthogonalCorrectors 1`, `nOuterCorrectors 1`. The
   worst-case accumulated contribution of the per-step final residual to the
   graded quantity, **assuming no cancellation over steps**, is
   `steps_fine x max(p_tol, U_tol) = 2688 x 1e-10 = 2.688e-07` — **a factor 1126
   below** the predicted fine `E2`, where L-346 demands one order. The
   dictionaries are checked against these numbers by both the launcher and the
   grader.
5. **The Class-C plateau gate is on the graded quantity itself** and is kept:
   §6.4's periodicity limb reads the field, not the solver, and §6.4's
   uniformity limb reads it a second way.

---

## 8. COST — MEASURED BASIS, ESTIMATE AND CAP

**Unit: core-minutes** (`wall s x ranks / 60`). Ranks: **4** at every level.

**The rate is MEASURED on this case, not derived from another one.** Scratch
arms on this box, 4 ranks, 2026-08-27, at load average **19.66 on 16 cores**;
marginal cost per step obtained by **differencing the first and last
`ExecutionTime`/`ClockTime` readings** so startup is excluded:

| level | cells | arm | marginal ExecutionTime/step | marginal ClockTime/step | **registered rate** | mean p-solve iterations |
|---|---|---|---|---|---|---|
| coarse | 3,840 | 200 steps | 0.01256 s | 0.01005 s | **13.09** | 63.7 |
| medium | 30,720 | 150 steps | 0.12671 s | 0.13423 s | **17.48** | 116.0 |
| fine | 245,760 | 24 steps | 2.14435 s | 2.47826 s | **40.34** | 233.8 |

Registered rate = **the larger of the two readings x 4 ranks / cells**, in
**core-microseconds per cell-step**. The growth is the DIC-PCG pressure
iteration count roughly doubling per level.

| level | cell-steps | core-min |
|---|---|---|
| coarse | 2,580,480 | 0.563 |
| medium | 41,287,680 | 12.028 |
| fine | 660,602,880 | 444.145 |
| **total** | 704,471,040 | **456.74** |

**`cost_core_min_estimate` = 456.74. Registered `CAP_CORE_MIN` = 680** (1.489x
the estimate, and 45 % of the 1500 core-min ceiling the dispatch set). The cap
is a runaway guard, not a target. **An overrun STOPS the run; it does not get a
new budget** (rule 12).

Dollars at the owner-stated **$0.0513/core-h**, **reported-by-owner, DERIVED,
NOT MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5): **$0.39** at the estimate, **$0.58** at the cap.

**Two honest caveats on the estimate.** (a) The fine arm ran only 24 steps, from
rest, during the phase where the pressure field is changing fastest; its
iteration count is therefore likely an **over**-estimate, making 456.74
conservative. (b) The rate was measured under real contention, which is why §8.1
applies **no** contention multiplier.

### 8.1 The pre-spend projector — REPLACED, and why

**The F23/F24/F25 pre-spend projector is defective and is NOT used here.** That
form multiplies a frozen constant by `max(1, ranks / max(free_cores, 0.5))`,
which pins at **8.0x** for a 4-rank entry on a busy box. F24_PRANDTL_MEYER
halted at exit 3 before its fine level because of it, against a measured
contention effect of **1.86x** — overstated 4.3x (cfd-supervisor, verified
personally, 2026-08-27).

The structural objection matters more here than anywhere: **whether a registered
three-level ladder ever produces its FINE level — the level that IS this rung's
deliverable — must not depend on the instantaneous box load at the moment that
level starts.** A ladder that completes or not according to contention is not a
reproducible instrument, and it is self-defeating under the standing directive
to keep the instances busy.

`cases/F27_WOMERSLEY_PIPE/proj_f27.py` instead:

1. projects the **FIRST** level from the frozen **measured** rate above;
2. projects **every later** level from **THIS RUN's own completed levels** —
   once coarse has run, its `ClockTime x ranks / cell-steps` **is** the rate on
   this box under this load — carried forward by the frozen per-level growth
   factors (1.3353, 2.3078) from the same measurement;
3. applies **NO contention multiplier** (`CONTENTION_MULTIPLIER = 1.0`), because
   the frozen rates were themselves measured under load 19.66/16 — contention is
   already inside the basis and multiplying again double-counts it. The lab's
   only measured contention point is 1.86x at `free_cores = 0.5`; **one point is
   not a law and is not dressed as one.** The box probe is still taken and still
   recorded, as an INFRASTRUCTURE observation (L-342), and it enters no
   arithmetic;
4. leaves the **post-level check on ACTUAL spend unchanged** — `ClockTime x
   ranks / 60` summed over completed levels, HALT at exit 3 on a crossing.

**The halt path is DRIVEN in `proj_f27.py --selftest`, in both directions, on
INJECTED numbers only** — it never reads `/proc`, the box, or a run directory,
because a selftest that reads live load is load-flaky and a flaky selftest
teaches its readers to re-run it until it passes (the L-339 class). The selftest
also proves **structurally** that no `max()` call node exists in any projection
function and that `project_core_min`'s signature takes no box reading.

---

## 9. THE INSTRUMENT, AND WHAT IS CHECKED BEFORE ANY COMPUTE

* `exact_f27.py --selftest` — **9 controls**, all green.
* `grade_f27.py --selftest` — **16 controls**, all green; both gated quantities
  shown able to take a passing **and** a failing value through the real reader
  on the real decomposed write format, with the planted-zero control exercised
  on the same artifacts.
* `proj_f27.py --selftest` — green, halt path driven both ways.
* **`ast.Assert` nodes: 0** across `exact_f27.py`, `foam_io_f27.py`,
  `build_f27.py`, `grade_f27.py`, `proj_f27.py` (L-332).
* **`python3 -O` exits 2** for `exact_f27.py`, `grade_f27.py`, `proj_f27.py`.
* **Exactly one `grade_ladder` call node** in `grade_f27.py`.
* `scripts/check_launcher_can_launch.py run_f27.sh` — **rc 0**: no shell glob
  used as a time-directory matcher, no bashrc sourced under `set -u`.
* **L-343**: the launcher exports `USER` from `LOGNAME`/`id -un` before sourcing
  the bashrc, records `USER`, `id -un` and `FOAM_USER_LIBBIN`, and its preflight
  PROVES the solver resolves with `USER` unset by running `env -u USER` against
  it. Measured probe: `UNSET | /home/ubuntu/OpenFOAM/user-v2606/…/lib |
  /usr/lib/openfoam/openfoam2606/…/bin/pimpleFoam` — `FOAM_USER_LIBBIN` does
  collapse to the `user-v2606` path exactly as L-343 describes, and this case
  uses no user-built library, so the solver still resolves. **If it ever did
  not, the launcher aborts loudly rather than launching.**

**Rule 3, the planted-zero control.** `grade_f27.py` plants `RT.PLANT =
1.234e-03` into the **axial component of every cell of the real processor `U`
files**, re-reads through the **same** functions the grade uses, and REFUSES
(exit 2) if the reader does not report **exactly** the predicted move, or does
not move at all. Separately, on a synthetic level carrying the **exact** field
every reader must return **zero** to round-off, and each of four planted defects
(radial, axial, azimuthal, cross-flow) must be seen by its own channel **and by
no other** — the channels are shown independent, not assumed.

**Rule 4, strict completion**, `PHYSICS_CRITICAL` only: `rc == 0`; an `End`
line; last time `== endTime`; `Time` line count `== endTime/dt`; `U` and `p` at
`endTime` present in **all four** processor directories and **NEWER than the
serial `0/U`** (the age guard); `U` at `endTime - PERIOD` present; `0/C` and
`0/V` present. **L-342**: a missing INFRASTRUCTURE field is a bookkeeping defect
that voids only the cost claim and never the verdict; driven both ways in the
grader's selftest, including a stale field tripping the age guard.

---

## 10. THE PRE-COMPUTE PILOT, DISCLOSED IN FULL

A **coarse-level scratch arm** was run to `T_END` before this document was
frozen, **outside the registered run root**, at a cost of **1.20 core-min**
(ClockTime 18 s x 4 ranks; the ExecutionTime was 13.23 s, and the lab's unit is
ClockTime x ranks). It is disclosed here in full because it informed
§6.2 and because an undisclosed pilot is worse than none.

| quantity | pilot (coarse) | composite-model prediction | ratio |
|---|---|---|---|
| `E2` | 7.663017e-03 | 4.732636e-03 | **1.619** |
| `Einf` | 1.174077e-02 | 7.831765e-03 | **1.499** |
| `W - W_ref` | -7.266238e-03 | (radial model) +9.570974e-04 | **-7.59** |
| `E_perp` | 4.375e-15 | 0 | — |
| `A_z` | 3.075e-14 | 0 | — |
| `A_theta` | 2.476e-12 | 0 | — |
| periodicity | 1.587e-07 | (tol 1.0e-06) | — |

**What it changed:** `W` moved from GATED to REPORTED-NOT-GATED (§6.2), and the
`R_eff` composite step was adopted for the band model (§6.3) — a step whose
parameter is read from the **mesh**, not fitted to any solve.

**What it did NOT change: `BAND_FACTOR` stays at the 5.0 fixed before the pilot
was read.** The gate was not widened to fit what was measured. If the fine level
lands outside its band, that is an honest `GATE FAIL`, and the triple's
CONVERGING state — the capability claim this rung exists to make — is unaffected
by it.

**The pilot is not a ladder level, is not in the run root, and no verdict cites
it.**

---

## 11. L-345 — THE REGISTERED MODEL'S OWN TRIPLES, THROUGH THE GRADING CLASSIFIER

L-345 cost F19 a gate on a completed, otherwise clean ladder: the registration's
own numbers already showed the triple could not read an order, and nobody
classified them. **Here they are classified, before compute, through
`scripts/roache_triple.py::triple_from_cells`, at the same `dim = 3` the run
will be graded at, with the same `P_MIN` and `STAGNANT_FLOOR`:**

| quantity | coarse | medium | fine | **state** | observed order |
|---|---|---|---|---|---|
| **`E2` (GATED)** | 4.732636e-03 | 1.205167e-03 | 3.026369e-04 | **CONVERGING** | **1.9666** |
| **`Einf` (GATED)** | 7.831765e-03 | 2.173170e-03 | 5.698921e-04 | **CONVERGING** | **1.8194** |
| `W` (reported) | 0.644732736 | 0.643391393 | 0.643067906 | CONVERGING | 2.0343 |

`r21 = r32 = 2.000000`, `ratio_gap = 0.00e+00` (equal-ratio path).

**Neither gated quantity's model triple is DEGENERATE, STAGNANT, OSCILLATORY or
EXACT**, so neither is registered around a prediction the instrument cannot
read. `exact_f27.py::control_L345_model_triples_are_gradeable` **REFUSES the
registration** if that ever stops being true, and carries a positive control (an
equal-increment triple must be classified DEGENERATE) so the check is shown able
to fail.

---

## 12. WHAT WOULD MAKE THIS RUNG `NOT A RESULT`

Any of: a level not iteratively converged; a level not periodic to
`PERIOD_TOL`; **a level not uniform to its own tolerance in `A_z` or
`A_theta`**; a finest triple that is DIVERGENT, STAGNANT, OSCILLATORY, EXACT or
DEGENERATE; a `checkMesh` gate breach at build time (the build ABORTS, so the
level never runs); a same-stencil-reference pin failure (likewise); a crash
(`rc != 0`) — a crash is a **FINDING** until triage says otherwise and is never
retried by the launcher.

`GATE FAIL` is reserved for a CONVERGING triple whose **fine** value sits
outside its pre-registered band. `PASS` requires both.

---

## 13. FILES FROZEN BY THIS REGISTRATION

`cases/F27_WOMERSLEY_PIPE/` — `exact_f27.py`, `foam_io_f27.py`, `build_f27.py`,
`grade_f27.py`, `proj_f27.py`, `run_f27.sh`, and `case/` (`0/U.template`,
`0/p.template`, `constant/{transportProperties,turbulenceProperties,fvOptions}`,
`system/{blockMeshDict.template,controlDict.template,fvSchemes,fvSolution,decomposeParDict}`).

The grading path is fixed at this commit. Run outputs go **only** to
`verification/runs/F27_WOMERSLEY_PIPE_runs/`.

**Amendments before first compute must state the condition and how it was
checked. After first compute this document is closed and changes land only as
dated addenda that cannot alter a gate, threshold, cap or label**
(`CLAUDE.md` rule 2).

---

## 14. DEPARTURES, STATED RATHER THAN BURIED

1. **The band model is an approximation, not a reduction.** §6.3. The 1-D
   cylindrical model plus the `R_eff` geometric step cannot see the azimuthal
   discretisation, the Cartesian core block, or the ring's non-orthogonality.
   `BAND_FACTOR = 5.0` is a declared judgement covering that, fixed before the
   §10 pilot was read.
2. **One gated quantity was demoted before freezing.** §6.2. `W` is
   REPORTED-NOT-GATED because a pre-compute measurement showed the registered
   model mis-predicts it by sign.
3. **A pre-compute pilot was run and is disclosed.** §10. 1.20 core-min, outside
   the run root, informing §6.2 and §6.3 but not `BAND_FACTOR`.
4. **`A_theta` has a declared null space.** §6.4. D4-invariant azimuthal modes
   read exactly zero; that class is carried by the two gated norms instead.
5. **`Fo` is a correlate, not a mechanism.** §5.
6. **The pre-spend projector departs from the F23/F24/F25 template**, and §8.1
   says exactly why and what replaced it.
7. **Non-orthogonality rises across the ladder** (28.59 → 36.16 → 40.42°). §3
   shows the increments shrinking geometrically to a limit near 45.8°, well
   under the 70° gate — the opposite of F1's approach to 90° — and records the
   trend rather than only the three passing numbers.


---

## AMENDMENT 1 — 2026-08-27, PRE-COMPUTE: a mislabelled scratch cost corrected

**THE CONDITION, AND HOW IT WAS CHECKED.** This amendment is legal only before
first compute (`CLAUDE.md` rule 2). **The registered run root
`verification/runs/F27_WOMERSLEY_PIPE_runs` DOES NOT EXIST**, checked in this
amendment's own preparation at **2026-08-27T17:10:35Z** by `ls -d` on that exact
path, which returned `No such file or directory`, and again by
`bash cases/F27_WOMERSLEY_PIPE/run_f27.sh --preflight`, which prints
`run root … is ABSENT` and exits 0 at zero compute. **No solver has run against
this registration. Zero core-minutes have been spent in the run root.**

**WHAT WAS WRONG.** §10 stated the pre-compute coarse pilot's cost as
**0.88 core-min "(ClockTime 13 s x 4 ranks)"**. **13.23 s was the pilot's
`ExecutionTime`, not its `ClockTime`.** The pilot's `ClockTime` is **18 s**, so
its cost in the lab's unit (`ClockTime x ranks / 60`) is **1.20 core-min**.
Read back from `log.pimpleFoam` of the pilot arm:
`ExecutionTime = 13.23 s  ClockTime = 18 s`.

**WHAT CHANGED.** TWO figures, both the same number in two places. In §10,
`0.88 core-min (ClockTime 13 s x 4 ranks)` becomes `1.20 core-min (ClockTime
18 s x 4 ranks; the ExecutionTime was 13.23 s, and the lab's unit is ClockTime x
ranks)`; in §14 departure 3, `0.88 core-min` becomes `1.20 core-min`. Nothing
else in the document is edited, and a grep for the superseded figure returns
hits ONLY inside this amendment, where it is quoted as the thing corrected.

**WHAT DID NOT CHANGE, and this is the whole point of disclosing it.** **NO
GATE, NO THRESHOLD, NO BAND, NO CAP AND NO LABEL MOVES.** `BAND_FACTOR` is 5.0;
both bands are unchanged; `CAP_CORE_MIN` is 680; `cost_core_min_estimate` is
456.74 — the corrected figure is the cost of a **scratch arm outside the run
root**, which is not part of the ladder's estimate and is not charged against
the cap. The capability cell, the ladder, the levels, the tolerances and the
verdict rules are untouched.

**WHY IT IS CORRECTED RATHER THAN LEFT.** A cost figure carrying the wrong
label is worse than one omitted: a reader would have taken 0.88 core-min as a
ClockTime-basis number and it is an ExecutionTime-basis number. The two bases
differ here by 38 %, and the lab's unit is fixed at `ClockTime x ranks / 60`
(`CLAUDE.md` rule 12).

**THE FULL SCRATCH SPEND OF THIS REGISTRATION, stated here so it is on the
record in one place.** All of it outside the run root, all on 4 ranks,
**MEASURED** as `ClockTime x 4 / 60` from each arm's own `log.pimpleFoam`:

| scratch arm | steps | ClockTime | core-min |
|---|---|---|---|
| rate arm, coarse | 200 | 4 s | 0.267 |
| rate arm, medium | 150 | 20 s | 1.333 |
| rate arm, fine | 24 | 59 s | 3.933 |
| physics pilot, coarse, to `T_END` | 672 | 18 s | 1.200 |
| **measured total** | | | **6.733** |

Beside it, **NOT MEASURED and stated as an estimate**: an earlier 30-step probe
whose log was overwritten (~0.07 core-min) and the serial `blockMesh`,
`checkMesh` and `postProcess` work across two builds of three levels
(~1.5 core-min). **Estimated grand total ≈ 8.3 core-min, of which 6.733 is
measured.** None of it is charged against the registered cap, and none of it is
a result.

**A LINE-NUMBER NOTE.** Rule 6's `lines whose number changed above this section:
0` assertion governs POST-compute addenda to frozen files. This is a
**pre-compute** amendment under rule 2, and it replaces one sentence in place
with a sentence of the same line count, so **no line number in this document
changes**. No other record cites this file by line: it was committed at
`4bb0226dcac06719b1a16a2d53647fcd5d0b9c9e` eleven minutes before this amendment
and is cited only by path.

**CONSEQUENCE FOR THE FREEZE.** This amendment produces a **new freeze sha**,
and `cases/F27_WOMERSLEY_PIPE/queue_entry_F27_WOMERSLEY_PIPE.json` is re-issued
against it in the same push. The superseded sha
`4bb0226dcac06719b1a16a2d53647fcd5d0b9c9e` is struck, not rewritten, and no run
ever cited it.
