# VMFL072-R2 — PRE-REGISTRATION (DRAFT, NOT YET FROZEN)

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, VMFL072: Liquid
Water Flow Over a Flat Plate Under the Influence of Gravity** (pp. 211–212),
reproduced in this lab's own solver as a pre-registered lab verdict.

**This document SUPERSEDES the registration frozen at `e8cbe305`.** That freeze
was **struck in place** by `ANSYS_VERIFICATION_CHARTER` **§39.1** before any
compute. Its bytes are **not edited and not reverted**; they stand in history as
a registration that could never have produced a verdict, and **no queue row was
ever filed against it and none may be.** Everything in this document that was
inherited from it has been re-verified here, and **four things it asserted are
refuted below and are refuted AT THE POINT OF USE, not only in a footnote** —
`§30.3` of the charter exists because a correction filed only at the foot does
not reach the reader of the clause.

---

## §0. THE §37.2 FREEZE CLAIM — WHAT THIS IS FROZEN *BEFORE*

### §0.1 The condition, named and CHECKED, not asserted

`CLAUDE.md` rule 2 and charter `§7.3` require the pre-compute condition to be
**named and checked**. Checked 2026-09-04, by name:

- **`verification/runs/ansys_verification/VMFL072-R2/` DOES NOT EXIST.** Nor
  does `verification/runs/ansys_verification/VMFL072/`. Checked by name, and by
  `find verification/runs -name 'VMFL072*'` returning nothing.
- **No solver has been run at any registered level to any registered
  `endTime`.** No value of δ_mon at the monitor has been read by anyone, at any
  level, at any time.
- **No grading artifact exists.** `compare_vmfl072_r2.py` has never been run
  against solver output; its only executions are `--selftest`, on data the
  selftest fabricates itself.

So the `§37.2` claim holds in all three limbs: **frozen before the run, before
the data, and before the reading.**

### §0.2 ⚠ WHAT *HAS* BEEN RUN, DECLARED UNDER `§20.3` RATHER THAN LEFT SILENT

`§20.3` requires a pre-freeze run to be **declared as one, with every revealed
quantity named** — *silence about a revealing smoke is the defect.* The
following were run in scratch on 2026-09-04, single core, `nice -n 19`,
**≈ 0.9 core-min measured, ≤ 1.5 core-min filed** ($0.0013 derived at
$0.0513/core-h; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER`
§5):

| what was run | what it revealed |
|---|---|
| the shipped `inclinedPlaneFilm` tutorial, 20 steps | the **file paths** `pimpleFoam` + `velocityFilmShell` writes (`§3.5`) |
| `blockMesh` + `makeFaMesh` + `checkFaMesh` on this case at L1/L2/L3 | faMesh **face counts, face areas, monitor-window face sets and their x-extents** (`§3.5`, `§6.2`) |
| six 20-step probes of this case, NZ ∈ {1, registered} | **per-step wall rates** (`§8.1`) |
| two 100-step (t = 0.5 s) L1 runs at NZ = 1 and NZ = 8 | the **`hf_film` field at t = 0.5 s at L1**, and the NZ-difference of it (`§3.6`) |
| the **driver, end to end** in a scratch git repository with `endTime` cut to 0.05 s | that the driver stages, meshes, age-guards and launches, and that each guard refuses what it claims to (`§9.2`). **10 solver steps at L1, stopping at t = 0.05 s** — the inlet signal travels 35 mm and the monitor keeps its untouched initial field |

**No gate quantity was revealed.** At t = 0.5 s the inlet signal has travelled
347 mm and has not reached the 450 mm monitor, which still carries its untouched
initial field; no level was run to steady state; and the 20-step probes stop at
t ≤ 0.1 s. **δ_mon is unknown to this lab at every level.**

---

## §1. THE REFERENCE, AS THE MANUAL STATES IT

Transcribed from pp. 211–212, character for character where it is a number.

| | |
|---|---|
| **Reference** | Roy, R.P. & Jain, S. (1989). *A study of thin water film flow down an inclined plate without and with countercurrent air flow.* Experiments in Fluids, (7) 318–328. **NOT ON THIS BOX** (`§10` item 1). |
| **Physics/Models** | Eulerian Wall Film |
| **Test case** | "A water film Reynolds number of 417 and a plate inclination angle of 40° without counter current airflow… The film is introduced as a mass flux boundary on the wall patch injection. **Film thickness is calculated at a downstream location wall-monitor.**" |
| **Domain** | 500 mm × 100 mm × 100 mm; injection width 5 mm; **wall-monitor width 50 mm** |
| **Boundary conditions** | Mass flux of water-liquid = **76.2 kg/m²·s**; gx = **6.305746 m/s²**, gy = 0, gz = **−7.514896 m/s²** |
| **Assumptions** | "Air flow is zero, and the film flow is laminar." |
| **Table .72.1** | Film Thickness (mm): **Target 0.555**, Ansys Fluent 0.5497, Ratio 0.99 |

**The manual gives the monitor's WIDTH and never its STREAMWISE STATION.** That
silence is `§10` item 3 and it is what makes `§6.2`'s station a **declared
reading**, not a transcription.

**0.555 mm is EXPERIMENTAL.** It is Roy & Jain's measurement of a real water
film, not the exact solution of any model. `§4` caps Limb A for that reason.

---

## §2. THE PROPERTY CLOSURE, AND TWO CORRECTIONS TO THE STRUCK DOCUMENT

### §2.1 Γ, μ, ρ — carried forward from `e8cbe305` and re-checked

`§39.6` records this closure as surviving intact; it is restated here so this
document stands alone.

| symbol | value | provenance |
|---|---|---|
| **Γ** | **0.381000 kg/m/s** | 76.2 kg/m²·s × 0.005 m — the manual's two printed inputs, no viscosity anywhere |
| **μ** | **9.136691e-04 Pa·s** | Γ/Re with Re = 417, the manual's printed Reynolds number |
| **ρ** | **997.4 kg/m³** | water at the temperature μ implies, ≈ 23.9 °C — **inferred, never printed** |
| **g·sinθ** | **6.305746 m/s²** | printed (gx); the vector is internally consistent, √(6.305746² + 7.514896²) = 9.80665 and atan(6.305746/7.514896) = 40.0° |
| **ν = μ/ρ** | **9.160508322e-07 m²/s** | |
| **q = Γ/ρ** | **3.819931823e-04 m²/s** | volumetric flux per unit width |

ρ enters as ρ^(−2/3); 998.2 instead of 997.4 moves δ by +0.056 %, inside `§5`
channel B and not carried separately.

### §2.2 The Nusselt thickness (context, and NOT Limb B's reference)

δ_N = (3μΓ/(ρ²·g sinθ))^(1/3) = **5.501147914e-04 m**.

−0.88 % from the manual's 0.555 mm and **+0.075 % from Fluent's 0.5497 mm** — a
different code, a different vendor, a different discretisation, arriving at the
same number. That corroboration is `§18.2` form (b)/(c) and is independent of
this lab entirely.

> **δ_N IS NOT LIMB B'S REFERENCE.** `§2.4` replaces it, and the reason is
> quantitative, not stylistic.

### §2.3 ⚠ CORRECTION 1 — THE RELAXATION LENGTH IS 25.4887 mm, NOT 76.4660 mm, AND THE ERROR IS EXACTLY A FACTOR OF 3

**The struck `§3.3` gives `L = U_eq·τ = 76.5 mm` with `τ = ρδ²/(3μ)`. That is
the relaxation of U at FIXED h. It is wrong here, and every constant derived
from it is wrong with it.**

In a constant-flux film `h = q/U`, so h and U are coupled and **both** restoring
terms respond to a perturbation. The steady one-dimensional balance implied by
`kinematicThinFilm.C:59–66` (verified at source, `§3.2`) is

```
q dU/dx = g_s·h − 3ν·U/(h + h₀) ,   h = q/U
        ≈ g_s·q/U − 3ν·U²/q                       (h₀ ≪ h)
```

Linearising about U_e, and using `g_s·q/U_e = 3ν·U_e²/q` to eliminate g_s:

```
f'(U_e) = −g_s·q/U_e² − 6ν·U_e/q = −3ν·U_e/q − 6ν·U_e/q = −9ν·U_e/q
```

— **nine, not three**, because the gravity term restores as well as the friction
term. Hence

> **L = q²/(9·ν·U_e) = 2.54871e-02 m = 25.4887 mm.**
> The struck value 76.4660 mm is **exactly 3.0000×** this.

**Consequences, each landing where it is used:**

1. The monitor at x = 450 mm is **17.65 relaxation lengths** downstream, not
   5.88. The registered inlet perturbation therefore decays far further than
   the struck document believed. **The error was in the SAFE direction** — the
   film is *more* developed than claimed — but it is an error.
2. **`§5.1`'s `STATION_SPREAD_MAX = 5.275e-06 m` in the struck document is
   STRUCK. Its input was 3× wrong, so the constant is wrong by construction.**
   `§6.3` re-derives the spatial bound from the instrument floor instead.
3. **⚠ AND THE STRUCK DOCUMENT'S BOLDED WARNING AT THAT POINT INVERTS.** It
   reads: *"Reusing §5.2's temporal threshold here — as this document's first
   draft did — would have FALSELY REFUSED A HEALTHY RUN by 10.7×."* With the
   corrected L the expected station spread at L3 is **1.956e-09 m, which is
   142× BELOW that threshold, not 10.7× above it.** The warning is exactly
   backwards under the corrected physics. **The charter recorded that warning
   approvingly; it is withdrawn here, at the point a reader of `§6.3` needs
   it.**

### §2.4 ⚠ CORRECTION 2 — LIMB B'S REFERENCE IS δ_N\*, THE EXACT *DISCRETE* STATE

`liquidFilmBase.C:74` sets `h₀ = 1e-7 m` by default and this registration keeps
it there. `filmTurbulenceModel.C:157` gives `Cw = 3μ/((h + h₀)ρ)`. The state the
solver actually admits exactly therefore satisfies

```
g_s·h = 3ν·U/(h + h₀) ,  U = q/h   ⟹   h²(h + h₀) = 3νq/g_s = δ_N³
```

> **δ_N\* = 5.500814601e-04 m**, which is **−0.006059 %** from δ_N.

The struck `§3.2` noted this bias and called it *"measured, negligible"* —
**correct against its 0.700 % Limb B band, where it is 0.9 % of the band.
Against this document's 0.101 % band it is 6.0 % of the band**, and a known,
computable bias sitting inside a reference is not admissible at that width.

**δ_N\* replaces δ_N in Limb B (`§5.2`) and in control C1 (`§6.4`). Limb A keeps
the manual's 0.555 mm and is unaffected** (the prediction moves from 0.8802 % to
0.8862 % against a 2.12 % band).

### §2.5 The registered closure, complete

| symbol | value |
|---|---|
| δ_N\* (Limb B reference) | **5.500814601e-04 m** |
| δ_N (context only) | 5.501147914e-04 m |
| U_eq = q/δ_N\* | **0.694430207 m/s** |
| relaxation length L | **2.54871e-02 m** |
| momentum relaxation time τ′ = δ_N\*²/(9ν) | **3.67022e-02 s** |
| plate advection time 0.5/U_eq | **0.720010 s** |

---

## §3. THE PHYSICS PATH — MEASURED, WITH PROVING PATHS

### §3.1 What this box has

OpenFOAM **v2606** at `/usr/lib/openfoam/openfoam2606`, build
`linux64GccDPInt32Opt` (double precision, ε = 2.22e-16). No Ansys solver of any
kind (`ANSYS_VERIFICATION_CHARTER` §2, checked 2026-08-24). The shipped
`tutorials/incompressible/pimpleFoam/laminar/inclinedPlaneFilm` is VMFL072's
construction at a different angle and is this case's working template.

### §3.2 `quadraticProfile` IS THE NUSSELT BALANCE, EXACTLY — re-verified at source

`src/regionFaModels/liquidFilm/kinematicThinFilm/kinematicThinFilm.C:55–66`:

```
const areaVectorField gs(g_ - ns*(ns & g_));
fam::ddt(h_, U) + fam::div(phi2s_, U)
  == gs*h_ + turbulence_->Su(U) + faOptions()(...) + forces_.correct(U) + USp_
```

with continuity `fam::ddt(h_) + fam::div(phif_, h_) == …` (`:140–141`) and
`phi2s_ = hEqn.flux()` (`:154`), so `phi2s` is the h-equation's own flux.

`.../filmTurbulenceModel/laminar/laminar.C:85`:
`Su(U) = primaryRegionFriction(U) + wallFriction(U)`, with `wallFriction(U) =
−fam::Sp(Cw, U) + Cw·Uw` and `Uw = 0`.

`.../filmTurbulenceModel/filmTurbulenceModel.C:157`, case `mquadraticProfile`:
`Cw = 3*mu/((h + h0)*rho)`.

**Therefore a spatially uniform (h, U) satisfying `g_s·h = Cw·U` makes `ddt`
vanish at steady state and `div(phi2s, U)` vanish identically — on ANY MESH.
The Nusselt state is an EXACT DISCRETE SOLUTION AT EVERY REFINEMENT LEVEL.**
That property is this case's central verification content (`§6.6`) and it is
also why `§7` declines a Roache triple.

Two source facts carried from `§39.6` and re-verified here:

- `Cw.clamp_max(5000.0)` (`:158`) binds only below `h + h₀ = 5.496e-10 m`, while
  `h₀ = 1e-7 m` floors it. **It can never fire and `§3.2`'s closure is exact as
  stated.**
- `gs = g − ns(ns·g)` carries the plate normal **twice**, so `|gs|` is
  sign-independent and the axis convention cannot silently move δ.

Two terms are active in the *developing* region and vanish on the uniform state:
the film pressure `pf_ = rho*gn*h − sigma*fac::laplacian(h) + pnSp_ + ppf_`
(`kinematicThinFilm.C:161`) enters momentum as `−h·∇(pf)/ρ` (`:118`), and both
`∇h` and `∇²h` are zero on a uniform field. **This is registered because it is
what a future developing-region registration would have to model, and `§7.4`
records that its magnitude there is comparable to the discretisation error
itself.**

### §3.3 SELECTED PATH — the registered configuration

**Solver** `pimpleFoam` (v2606), transient, incompressible, primary region
**laminar**, **SERIAL (one rank at every level)**.
**Film** `velocityFilmShell` BC on the plate patch, `liquidFilmModel
kinematicThinFilm`, finite-area region `film` built by `makeFaMesh`.

```
turbulence        laminar;
laminarCoeffs   { shearStress simple;  friction quadraticProfile;  Cf 0; }
injectionModels ();
forces          ();
region          film;
liquidFilmModel kinematicThinFilm;
h0              1e-7;
```

- **`Cf 0`** — the manual states air flow is zero. A non-zero `Cf` damps the
  film even against quiescent air and would corrupt the balance.
- **`forces ()`** — the tutorials carry `dynamicContactAngle`, an edge/rivulet
  force. This is a continuous 0.55 mm sheet with no dry patch; including it
  would add a term the manual's setup does not have and **would break `§6.9`
  condition 1.** Registered as excluded, before compute, with that reason.
- **`friction quadraticProfile`, not the tutorial's `ManningStrickler`** — the
  shipped `inclinedPlaneFilm` uses `ManningStrickler n 0.1, Cf 0.9`, an
  empirical open-channel law that is **wrong for a laminar film**. Copying the
  tutorial unmodified would silently have produced a different physical model.
- **Feeding the film.** `regionFaModels/liquidFilm` has no dictionary-driven
  mass-source injection model — `subModels/kinematic/injectionModel/` contains
  only `BrunDrippingInjection` and `filmSeparation`, both of which **remove**
  film. Mass therefore enters at the **finite-area inlet boundary** as
  prescribed `hf_film` and `Uf_film` with ρ·h_in·U_in = Γ.
- **SERIAL, and it is a design choice with a reason.** The struck launcher
  reconstructed with `-latestTime` and produced **two** time directories against
  a comparator demanding 200 (`§39.2` blocker 2). A serial run writes the 200
  directories the comparator reads. **The failure mode is designed out, not
  guarded.**

**Geometry and gravity, as printed.** Plate 500 mm (x, downslope) × 100 mm
(y, span); gas box 100 mm in z. `constant/g = (6.305746 0 −7.514896)`.

### §3.4 ⚠ THE CIRCULARITY THIS CREATES, AND HOW IT IS DEFEATED

Prescribing h at the inlet risks prescribing the gate quantity. It is defeated
by **deliberately setting the inlet off equilibrium** and reading the monitor
far downstream, so the monitor value is a *solved relaxation*, never a boundary
condition:

```
nominal (L1 L2 L3):  h_in = 1.30 δ_N* = 7.1510589810e-04 m,  U_in = 0.534177082 m/s
bracket  B2       :  h_in = 0.70 δ_N* = 3.8505702205e-04 m,  U_in = 0.992043153 m/s
control  C1       :  h_in = 1.00 δ_N* = 5.5008146008e-04 m,  U_in = 0.694430207 m/s
```

All three carry the **identical** Γ: ρ·h_in·U_in = 0.381000000 kg/m/s exactly.
**The bracket B2 (`§6.5`) MEASURES the residual rather than assuming it, and it
now runs at the GRADED level, not at L2.**

### §3.5 ⚠ `§39.5` — EVERY PATH THE COMPARATOR READS, SHOWN TO BE A PATH THE SOLVER WRITES

**This is the rule that struck the predecessor**, whose comparator read
`constant/film/Cf_film` and `constant/film/magSf_film` — names that appear in
**zero** code paths. `faMesh.C:64` fixes the finite-area prefix to the literal
`"finite-area"`.

**Verified on disk 2026-09-04 by BUILDING AND RUNNING THIS CASE**, not by
grepping and not by inference. A written time directory of the registered
configuration contains **exactly**:

```
U  p  phi
finite-area/{hf_film, Uf_film, pf_film, phif_film, phi2s_film, rhof, Tf_film}
uniform/{time, cumulativeContErr, functionObjects/functionObjectProperties}
```

and `constant/finite-area/faMesh/` contains **exactly** `{faceLabels,
faBoundary}`. **There is no `Cf_film` and no `magSf_film` anywhere.**

| path the comparator reads | the utility that writes it |
|---|---|
| `constant/polyMesh/points` | `blockMesh` |
| `constant/polyMesh/faces` | `blockMesh` |
| `constant/finite-area/faMesh/faceLabels` | `makeFaMesh` |
| `<t>/finite-area/hf_film` | `pimpleFoam` + `velocityFilmShell` |
| `log.checkFaMesh` "Face area: min = … max = …" | `checkFaMesh` |
| `log.pimpleFoam` "End", "ExecutionTime" | `pimpleFoam` |
| `RC.txt` | the driver's detached wrapper (`§9.2` G-08) |

**Face centres and areas are COMPUTED from `points` + `faces` + `faceLabels`,
and the computation is refused unless it agrees with numbers OpenFOAM produced
itself.** Four refusals, `§6.6` C-14…C-17. Measured at build time:

| level | faMesh faces | `checkFaMesh` min = max area [m²] | Σ magSf [m²] | monitor faces |
|---|---|---|---|---|
| L1 (64 × 16) | 1024 | 4.8828125e-05 | 0.050000000000 | **24** |
| L2 (128 × 32) | 4096 | 1.220703125e-05 | 0.050000000000 | **80** |
| L3 (256 × 64) | 16384 | 3.0517578125e-06 | 0.050000000000 | **352** |

> **A `--selftest` on synthetic data proves the comparator's LOGIC and says
> NOTHING about its INTERFACE** (`§39.5`). The comparator's selftest prints that
> sentence as its own banner, and the table above — not the selftest — is this
> registration's interface evidence.

### §3.6 NZ = 1, AND IT IS A MEASUREMENT WITH A LIVE CONTROL, NOT AN ASSUMPTION

The primary (gas) region is meshed **one cell thick in z at every level**. The
justification is two source lines and one measurement:

1. `filmTurbulenceModel.C:252`, case `msimple`:
   `tshearStress.ref() += -fam::Sp(Cf, U) + Cf*Up();`. With the registered
   `Cf 0` the **entire primary-region coupling is identically zero**, and the
   primary velocity `Up()` is multiplied by zero.
2. The gas is driven by nothing (`pimpleFoam` applies no buoyancy) and its
   Courant number was **measured at exactly zero** — `Courant Number mean: 0
   max: 0` — so `pg()`'s mapped primary pressure (`liquidFilmBase.C:360–378`)
   is uniform and contributes no gradient to `−h·∇(pf)/ρ`.

> **THE MEASUREMENT, WITH ITS PLANTED CONTROL (`CLAUDE.md` rule 3 applied to a
> NEGATIVE result).** Two 100-step (t = 0.5 s) L1 runs, at NZ = 1 and NZ = 8:
> `hf_film` is **bit-identical on all 1024 faces**, `max|Δh| = 0.0000e+00`.
> **A zero from a reader not shown able to see a non-zero is not evidence**, so:
> the field is genuinely non-trivial (range **5.633e-04 m**, i.e. it varies by
> 100 % of δ_N\* across the plate — the comparison is not vacuous), and the
> **same reader was then driven with a planted +1.234e-09 m in a single face and
> returned `max|Δh| = 1.2340e-09`.** The reader can see a difference; there is
> none to see.

**NZ = 1 is therefore not an approximation — it is the same computation for the
film — and it cuts the campaign from ~200 to ~61 core-min.**

**Honest limit:** the equivalence is measured at L1 over 100 steps, not at a
converged state, because a converged NZ-sensitivity run would have revealed the
gate before the freeze. The source argument, not the probe, is what carries the
claim to `endTime`; the probe is what makes the source argument checkable.

### §3.7 `§12.2` — THE SAMENESS RULING, answered in its own four required parts

1. **The continuum model the lab's solver discretises.** The depth-averaged
   (lubrication) thin-film equations on a surface — `∂h/∂t + ∇·(h**U**) = 0` and
   `∂(h**U**)/∂t + ∇·(h**UU**) = h**g**_t − (3μ/ρh)**U** − (h/ρ)∇p_f` —
   incompressible, Newtonian, laminar, parabolic through-thickness profile, zero
   gas shear. Verified against the installed source in `§3.2`.
2. **The model the reference is the exact solution of.** **None.** 0.555 mm is
   an experimental measurement of a real water film — the full 3-D
   incompressible Navier–Stokes system with a deformable free surface, including
   the interfacial waves a film at 4Γ/μ = 1668 certainly carries.
3. **Are those the same model?** **`DIFFERENT`.** An experiment is not the
   solution of any reduced model, and the residual between a smooth
   depth-averaged film and a real wavy film is **model-form error, which no grid
   triple and no exactness gate bounds.**
4. **Consequence.** **`GATE REACHED` from the outset**, per `§12.2` and
   `VERIFICATION_CHARTER` **§2h.8.1** — *"A reference drawn from a DIFFERENT
   MODEL — … **experiment** — CAPS AT `GATE REACHED`, HOWEVER EXACT ITS OWN
   ALGEBRA."*

---

## §4. THE CAP, AND WHOSE IT IS

> **Limb A's ceiling is `GATE REACHED`. THIS CAP BELONGS TO THE REFERENCE, NOT
> TO OUR WORKMANSHIP.** No amount of fixing on our side lifts it, and **no
> redesign in this document lifts it either** — the route change from
> `e8cbe305` was about the *triple*, never about the cap. **Reaching
> `GATE REACHED` is this limb's success, not its shortfall.**

`§33.2` does not fire. That clause governs *code-to-code* references and their
circularity. Fluent's 0.5497 mm is exactly such a reference and **it is not the
gate** — it is context (`§2.2`). The gate's reference is the experiment.

---

## §5. THE GATE

**Gate quantity** — the **area-weighted mean film thickness δ_mon over the
wall-monitor window**, at `endTime`, on the **graded level L3**. `§6.6`'s
exactness gate certifies that the choice of level does not move it.

### §5.1 Limb A — primary, against the manual

```
e_A = | δ_mon − 0.555 mm | / 0.555 mm   ≤   2.12 %
```

Inside → **`GATE REACHED`** (its ceiling, `§4`); outside → **`GATE FAIL`**;
either overridden to **`NOT A RESULT`** by `§6.6`, `§6.1`, `§6.3` or a refused
plant. **Admissible interval: δ_mon ∈ [0.543234, 0.566766] mm.**

**The band, channel by channel. It is the LINEAR sum, which is the conservative
choice and avoids any appearance of shrinking the band.**

| ch | source | magnitude | how it was obtained |
|---|---|---|---|
| **A** | reference's quoted precision | **0.090 %** | "0.555" is 3 s.f. → ±0.0005 mm. **A FLOOR on the reference's uncertainty, not an estimate of it** — Roy & Jain's own stated uncertainty is unavailable and is **not invented**. |
| **B** | unstated fluid properties | **1.926 %** | The manual never states water temperature. At fixed **Γ**, δ ∝ μ^(1/3): δ(20 °C) = 0.5669 mm, δ(25 °C) = 0.5455 mm, half-width about the midpoint 1.926 %. **91 % of the band, and it comes from the manual's silence, not from any run.** |
| **D′** | discretisation | **0.0504 %** | An *allowance enforced as a requirement*: `§6.6`'s exactness gate, `T = 2.7750e-07 m` on δ_N\*. **10× tighter than the struck document's 0.500 % GCI allowance.** |
| **E′** | inlet-relaxation residual | **0.0504 %** | An *allowance enforced as a requirement*: `§6.5`'s bracket, the same `T`. **4× tighter than the struck 0.200 %.** |
| | **BAND** | **2.1168 % → registered 2.12 %** | |

**Channel C — model form — is deliberately NOT in the band.** The residual
between a smooth depth-averaged model and a real wavy film is unbounded by any
instrument this lab owns. Folding an unbounded model-form error into a band is
precisely what `VERIFICATION_CHARTER` §2h.8.2 exists to prevent. It is instead
**the ground of the `GATE REACHED` cap** (`§4`).

**⚠ THE BAND IS NARROWER THAN THE STRUCK DOCUMENT'S 2.72 %, AND THAT IS THE
HARDER DIRECTION.** Channels D and E were *allowances enforced as requirements*
there too; enforcing them at the instrument's actual floor rather than at a
nominal figure is the honest number, and it makes the gate **easier to fail**,
never easier to pass. Rounding is **down to the arithmetic**, 2.1168 → 2.12 %.

**The band can fail.** Nothing in the plausible 20–25 °C property range,
combined with the full numerical allowance, places δ outside [0.543234,
0.566766] mm. A result outside it is not explicable by any admissible input
choice and would indicate a setup, mesh, boundary-condition or model defect.
**The band was not sized from Fluent's 0.5497 mm**, which appears in this
document only as `§2.2` context.

### §5.2 Limb B — CODE VERIFICATION against the exact solution of the same model

```
e_B = | δ_mon − δ_N* | / δ_N*   ≤   0.101 %      (= D′ 0.0504 + E′ 0.0504)
```

**Reference δ_N\* = 5.500814601e-04 m** (`§2.4`) — the **exact steady solution
of the very PDE the solver discretises**, including the solver's own `h₀`.
`PASS`-capable under `VERIFICATION_CHARTER` **§2h.8.1**.

Channels A and B **do not appear**: the property set is *shared* between our run
and δ_N\*, so it cancels identically, and no experimental reference is involved.
**Limb B's band is the numerical budget and nothing else.**

### §5.3 The registered PREDICTION (prediction-first, `CLAUDE.md` rule 2)

> **δ_mon = 0.550081 mm**, to within iterative and inlet-relaxation error.
> **e_A = 0.8862 %** against a 2.12 % band. **e_B ≈ 1.2e-06 %** against 0.101 %.

If the run lands materially away from this, **our reading of the installed
solver is refuted**, and that is a finding worth more than a passing row.

---

## §6. HOW THE NUMBER IS READ, AND THE CONTROLS ON THE READER

### §6.1 ONE instrument floor, four uses — and the derivation is the same each time

> **`T = 2.7750e-07 m` = 0.05 % of 0.555 mm = 0.050447 % of δ_N\*.**

Derived from the **gate tolerance**, never from an observed floor (`§16.2`): the
tightest band in play is Limb B's 0.101 %, and T is **2.0×** tighter than it, so
noise at T cannot move either verdict. It is a **number, not `ptp → 0`**, so it
is satisfiable against a bounded limit cycle (`§16.1`). Falsifiability
(`§35.1`/`§37.1`): T is **2.8e8 ×** the reader's 1e-15 m file quantum
(`writeFormat ascii; writePrecision 12;`, registered case setup) and **2.8e3 ×**
the registered `faSolution` tolerance of 1e-10 on `hf_film`. **It is resolvable
by the instrument that must test it.**

The same constant governs four checks because **all four are one statement —
two readings of the same quantity are indistinguishable at the run's own noise
floor** — and none can honestly be tightened past the wander each level is
permitted to carry:

| check | reading A | reading B |
|---|---|---|
| **C-10 plateau** | δ_mon at one write | δ_mon at another, inside the last 2.0 s |
| **C-11 station** | δ_mon at x = 450 mm | δ_mon at x = 300, 350, 400, 480 mm |
| **C-12 exactness** | δ_mon at one level | δ_mon at another |
| **C-21 bracket** | δ_mon from a +30 % inlet | δ_mon from a −30 % inlet |

**⚠ `§5.1` OF THE STRUCK DOCUMENT WARNED IN BOLD AGAINST EXACTLY THIS REUSE, AND
THAT WARNING DOES NOT SURVIVE ITS OWN CORRECTED INPUT.** See `§2.3` consequence
3: it rested on L = 76.5 mm; at the correct 25.4887 mm the expected station
spread is **142× BELOW** T, not 10.7× above it. The four uses here are one
criterion, not two criteria sharing a constant.

### §6.2 The reader, its window, and its resolution

**Reader:** `cases/ansys_verification/VMFL072-R2/compare_vmfl072_r2.py`, pinned
at `§9.1` and fixed at this document's freeze commit (`CLAUDE.md` rule 2).

**Field read:** `hf_film`, the finite-area film-thickness field, from the graded
level's `endTime` directory. No derived quantity, no isosurface, no
reconstruction.

**Monitor window** — the manual gives the width (50 mm) and **not** the
streamwise station; the station below is a **DECLARED READING** (`§10` item 3):

```
faces whose centres satisfy  x ∈ [0.440, 0.460] m  AND  y ∈ [0.025, 0.075] m
δ_mon = Σ(hf_i · A_i) / Σ(A_i)
```

- **50 mm spanwise**, centred on the 100 mm span — the manual's monitor width,
  keeping the side walls out of the reading.
- **x = 450 ± 10 mm** — 50 mm clear of the outlet, and 17.65 relaxation lengths
  clear of the inlet (`§2.3`).

> **⚠ DISCLOSED, MEASURED, AND DELIBERATELY NOT REPAIRED: THE WINDOW IS NOT
> NESTED ACROSS LEVELS.** The face-centre x-extents it selects are
> `[441.41, 457.03]` / `[443.36, 458.98]` / `[440.43, 459.96]` mm at L1/L2/L3, so
> the window's **effective centroid moves 449.22 → 451.17 → 450.20 mm — ±1 mm,
> and non-monotone.**
> **At x = 450 mm this contributes 2.5e-13 m to δ_mon**, six orders below T, and
> it is therefore **left alone**: changing a working, measured geometry to fix a
> contribution six orders below the threshold is unforced risk on exactly the
> surface that struck the predecessor.
> **IT IS RECORDED BECAUSE IT IS FATAL SOMEWHERE ELSE.** At a *developing*
> station the same drift changes δ by **2.196e-06 m against a level-to-level
> discretisation signal of 2.125e-06 m — 1.03×, i.e. the artifact exceeds the
> entire signal, and being non-monotone it would classify `OSCILLATORY`.** Any
> future developing-region registration **must** use cell-boundary-nested
> windows. `§7.4` records this.

**Reader resolution.** `writeFormat ascii; writePrecision 12;` gives a file
quantum of ≈ **1e-15 m** on a 5.5e-04 m value. Per `§25.4` the governing floor is
the **maximum** of the floors, so it is the solver's own iterative floor, held
below T by `faSolution` tolerances on `hf_film` and `Uf_film` of **1e-10**
(registered, `base/system/finite-area/faSolution`). **Every threshold in this
document is stated against that floor in `§6.1`.**

### §6.3 The station-development check — re-derived from the instrument floor

The comparator reports δ_mon over the same ±10 mm × 50 mm window at
**x = 300, 350, 400, 450, 480 mm** on the graded level, and

> **if the spread across those five stations exceeds `T = 2.7750e-07 m`, the
> film is not developed at the monitor and the verdict is `NOT A RESULT`.**
> The reading is **not** quietly relocated.

**Derivation, and it replaces a constant that was wrong by construction.** The
struck `5.275e-06 m` came from `resid(450)·(e^{130/L} − e^{−30/L})` with
L = 76.5 mm — a 3× wrong input (`§2.3`). Rather than rescale a residual model, the
bound is taken from the instrument floor, on the same principle as `§6.1`'s
other three uses. **Expected value at L3: 1.956e-09 m, i.e. 142× below T** — a
loose but live and falsifiable guard that fires if the film is genuinely
undeveloped (a wrong Γ, a wrong friction closure, a wrong inlet) and does not
fire on a healthy run.

### §6.4 Control C1 — exact-solution retention, and it can fail

A run at **L2** with the inlet set **exactly at equilibrium**
(h_in = δ_N\*, U_in = U_eq = 0.694430207 m/s), and the initial field uniform at
the same value. The exact solution is then present everywhere from t = 0, so the
solver must **retain** it.

> **Requirement: max over the plate of |h − δ_N\*| / δ_N\* < 0.05 % at
> `endTime`.**

**This is the cleanest possible test of `§6.9` condition 1 and it is genuinely
falsifiable.** If `§3.2`'s source reading is wrong in any respect — the friction
closure, the h₀ treatment, the gravity projection, an unnoticed active force
term, the `pf_` closure — the film **drifts off** the state we predicted it must
hold, visibly. **C1 failing refutes Limb B outright.**

### §6.5 Bracket B2 — the anti-circularity control, AT THE GRADED LEVEL

**L3** at h_in = 0.70 δ_N\* against the nominal **L3** at h_in = 1.30 δ_N\*,
**same Γ**.

> **Requirement: |δ_mon(B2) − δ_mon(L3)| ≤ `T`.**

**Promoted from L2 to L3 relative to the struck document, deliberately.** The
headline of this registration is *the answer is the exact solution at every
level*, and the obvious objection is *of course it is, you told it the answer at
the inlet.* Two inlets **60 % apart in h** converging to the same monitor value
is the refutation, and it belongs at the level that is graded. It costs
**33.71 core-min** instead of 5.47 (`§8.1`) and that is the reason.

Exceeding T means the film is not relaxed at the monitor: **channel E′ is not
widened** — the finding is reported and the monitor question is reopened as a
new registration, never as an amendment here.

### §6.6 ⚠ THE EXACTNESS GATE — what replaces the declined triple

> **`max` over all pairs of `|δ_mon(Li) − δ_mon(Lj)|` across L1, L2, L3
> `≤ T = 2.7750e-07 m`. One-way: failing it is `NOT A RESULT`, and no path in
> the comparator may turn that into a `PASS` or a `GATE REACHED`.**

**This is the falsifiable form of the statement `§39.4` identified as this
case's real result:** *the discretisation admits the exact solution at every
refinement level.* Three levels spanning **4× in Δx** are run, and the gate
requires them to be indistinguishable.

**Why this is STRICTER than the triple it replaces, quantitatively.** A
`CONVERGING` Roache triple permits level-to-level differences of **any** size
provided they are monotone with a plausible order; the struck document then
bounded the resulting GCI at channel D's **0.500 %**. This gate permits **no**
level-to-level difference above **0.0504 %**. **R2 replaces a test that was
structurally incapable of returning anything but `NOT A RESULT` with a test that
is 10× tighter on the same quantity, at the same compute.**

Alongside it, three geometry refusals and one field refusal, each against a
number OpenFOAM produced or a property that must hold for the reader's
arithmetic to be exact:

| clause | refusal |
|---|---|
| **C-14** | faMesh face count ≠ NX·NY |
| **C-15** | Σ magSf ≠ 0.05 m² to 1e-12 relative (the plate's exact area) |
| **C-16** | computed (min, max) face area ≠ **`checkFaMesh`'s own printed pair** to 1e-12 relative |
| **C-17** | any face is not a 4-vertex planar parallelogram (so "centroid = mean of vertices" is exact and no fan-decomposition ambiguity exists) |

> **⚠ THE HONEST LIMIT OF THE EXACTNESS GATE, STATED SO NO LATER READER TAKES IT
> FOR A CONVERGENCE RESULT.** The predicted level-to-level differences are
> `e21 = 2.17e-11 m` and `e32 = 5.37e-12 m` — **below the `faSolution` floor of
> 1e-10** — so the gate is expected to pass by roughly **four to five orders of
> magnitude**. **Its power is against GROSS level-dependence: a mesh-dependent
> boundary condition, a level-dependent setup error, a solver inconsistency, a
> broken reader. It has NO power against fine discretisation error, which is
> unmeasurable in this quantity by construction.** It detects truncation error
> at or above 0.0504 % relative and nothing below that. **A gate that passes by
> five orders is worth having only if the record says what it can and cannot
> catch; this is that statement.**

### §6.7 Admissibility floor

The comparator **refuses** any δ_mon that is non-positive or below
**1.0e-06 m** — 550× below δ_N\*, far too low to be mistaken for a gate, and a
value no film-producing run can return. **This closes the all-zeros hole, which
no additive plant on a linear reader can close** (`§6.8` limit 2).

### §6.8 The planted controls — designed against the REDUCTION, not the field (`CLAUDE.md` rule 3; L-487)

The comparator **refuses (exit 2)** and produces no number unless **both** fire.
Both act on **copies in scratch**; graded fields are never mutated. `P` is sized
from the **band** and the sub-region from the **geometry**, neither from any
measured value.

**P1 — against the MONITOR reduction (an area-weighted mean).** `P =
+1.234000e-05 m` is added to a **PROPER SUBSET by area** of the monitor window —
the faces with `y < 0.050 m` — the field is **re-written and RE-PARSED through
the same reader**, and the comparator requires

```
| δ_mon(planted) − δ_mon(clean) − P·f |  <  1.0e-09 m ,
      f = Σ(area of planted faces) / Σ(area of window faces)
```

`f` is computed from the geometry the comparator itself reads and is **never
hard-coded**. The comparator **refuses** if the sub-region selects zero faces or
**the whole window** — the degenerate case in which an additive plant over
exactly the reduction set **cancels identically for every possible input**,
which is the inert control the struck document had to repair once already.

**P2 — against the EXACTNESS-GATE reduction (a max over pairs).** `§6.6`'s gate
is a **null**: it expects zero. A null needs its own plant, and **the struck
comparator specified P2 and never wired it in** — `§39.3`, the defect that would
have granted an unauthorised credential. Here P2 is implemented and its firing
is shown. It plants into **one level only** and requires the statistic to take
the value the plant makes it take, computed from the **clean** triple plus the
analytically known increment so the check is not circular, **and to have
actually MOVED by more than 1.0e-09 m** — a control that cannot move is not a
control.

**⚠ TWO HONEST LIMITS, SO NO READER OVERRATES THESE CONTROLS.**

1. **On a uniform mesh the area-weighted and unweighted means are the same
   function** — not two readers — so that mutant is **not discriminable on the
   production meshes**, whose faces were measured to have min area == max area
   exactly (`§3.5`). The selftest exercises the weighting on a **graded-area
   arm** where the area fraction (0.425) and the count fraction (0.500) differ,
   and the unweighted mutant **is** refused there.
2. **An additive plant on a LINEAR reader shifts the mean by a field-independent
   amount.** That is a property of linearity and **no plant can defeat it**, so
   P1 alone still passes on an all-zeros field. That hole is closed by
   **admissibility** (`§6.7`), not by the plant.

### §6.9 ⚠ LIMB B IS AN EXACT-RETENTION TEST AND IS EXPECTED TO PASS

**A limb expected to pass must say so, or a later reader will read its passing
as evidence it was not.** `§3.2` establishes that the solver admits δ_N\* as an
exact discrete solution, so `e_B ≈ 0` by construction. **That is the case's
verification content, not a weakness** — the claim being tested is *that the
discretisation admits the exact solution*, and the only way to test a claim of
exactness is to measure the exactness.

**What makes it a real test rather than a tautology is that it can fail**, in
four named ways, each of which would refute a specific line of `§3.2`'s source
reading: an active `forces()` term, a different `h₀` treatment, a sign in the
gravity projection, or a `phi2s` that is not `hU`. `§6.4`'s C1 is the sharpest
of these — it tests retention over the **whole plate**, not just at the monitor.

**`§2h.4`'s five conditions, declared before compute as that clause requires:**

1. **Reference is the exact solution of the same continuum model.** **MET** —
   verified at source in `§3.2`, with file, function and line, and **corrected in
   `§2.4` to the h₀-consistent state δ_N\***. Model-form error is zero by
   construction. Preserved by the `forces ()` and `Cf 0` declarations of `§3.3`.
2. **Iterative error separately gated by rule 5 limb (1), one-way.** **MET** —
   `§6.1`'s plateau criterion, frozen before compute, applied one-way.
3. **Round-off stated with its magnitude and shown negligible.** **MET** —
   double precision, ε = 2.22e-16; over ~1.3e4 steps random-walk accumulation is
   ≈ 2.5e-14 relative, i.e. 1.4e-14 mm on δ. Against the 0.101 % band that is a
   ratio of **2.5e-11**. A number, not an assurance.
4. **The limb's wording makes no continuum claim.** **MET.** The only sentence
   the record may carry for Limb B is:
   > *"The combined iterative and inlet-relaxation error in δ_mon is below
   > 0.101 % at every level run, and the three levels are indistinguishable at
   > 0.0504 %."*
   It is **not** *"the solution is correct to 0.101 %"* and it makes no
   statement about nature.
5. **The claim is bounded by the levels actually run.** **MET** — asserted for
   L1, L2 and L3 **only**. Nothing is claimed about finer meshes.

### §6.10 Strict completion (`CLAUDE.md` rule 4) — the comparator refuses on any clause

| clause | requirement |
|---|---|
| **C-01** | `rc = 0`, captured **inside** the detached wrapper (`setsid timeout cmd` returns 0 for every outcome) |
| **C-02** | an **`End`** line in the solver log |
| **C-03** | last time directory == `endTime` == 10.0 |
| **C-04** | fields present at `endTime`: primary `U`, `p`; film `hf_film`, `Uf_film` |
| **C-05** | **written time directory count == 200** = `endTime`/`writeInterval`. Rule 4's "`ExecutionTime` count == `endTime`" is written for a fixed-step steady solve; the registered analogue is stated rather than silently substituted, and **both halves are checked** |
| **C-06** | `ExecutionTime` line count == the level's registered step count (2000/4000/8000/12800/4000) |
| **C-07** | **age guard** — every field at `endTime` strictly newer than the case's own `0/U`. **This is only valid if `0/U` is touched LAST at launch**, which the driver does and then **asserts** (`§9.2` G-07). The comparator's guard and the driver's assertion are two halves of one control; **neither is sufficient alone.** |

---

## §7. NO ROACHE TRIPLE IS DECLARED — the statement `CLAUDE.md` rule 5 requires, made up front

> **THIS CASE DECLARES NO GRID TRIPLE. IT COMPUTES NO RICHARDSON
> EXTRAPOLATION, NO OBSERVED ORDER AND NO GCI, AND NO ROW OF IT MAY EVER BE READ
> AS CARRYING ONE.** Three levels are run and are used **only** for `§6.6`'s
> exactness gate, which is a **level-independence** test, not a convergence
> test. `§2f.2`'s *"no triple never means no rule 5"* is honoured: **rule 5 limb
> (1) fires in full** (`§6.1`, `§6.10`). Only limb (2), the triple
> classification, is absent, because no triple is declared.

Three reasons, in order of weight, all a-priori.

1. **THE QUANTITY HAS NO DISCRETISATION ERROR TO EXTRAPOLATE.** `§3.2` proves
   the Nusselt state makes every gradient term vanish identically **on any
   mesh**, so it is an exact discrete solution at every level. The only
   level-dependence is the numerical decay of the inlet perturbation over the
   upstream relaxation length, and at 17.65 relaxation lengths (`§2.3`) that
   residual is:

   | | δ_mon − δ_N\* |
   |---|---|
   | L1 | 3.385e-11 m |
   | L2 | 1.213e-11 m |
   | L3 | 6.756e-12 m |

   → **e21 = 2.17e-11 m, e32 = 5.37e-12 m against T = 2.7750e-07 m — 7.8e-05 ×
   and 1.9e-05 ×.** `roache()` returns **`EXACT`**, and rule 5 step (2) makes
   that **`NOT A RESULT` on both limbs whatever the values.** **A 50,000× error
   in this estimate would not change that conclusion.** *(These are a model —
   upwind effective decay `L_eff = Δx/ln(1+Δx/L)` — stated so they can be
   checked, not a measurement.)*

   **And `e32 = 5.37e-12 m is BELOW the registered `faSolution` tolerance of
   1e-10 on `hf_film`.** A triple there would classify **solver noise**, and any
   order fitted to it would be an order fitted to noise.

2. **THE STRUCK DOCUMENT CLAIMED A COARSE L1 DEFEATED THIS AND IT DOES NOT.**
   Its `§5.6` argued that L1 at 9.8 cells per relaxation length made the
   truncation error unmistakable. **Coarsening changes the DECAY RATE of an
   already-tiny residual; it never changes the asymptotic value the monitor
   sees.** `§39.4` records this against the supervisor's own board, which called
   the design *"the trap named and defeated"* — **it was named and not
   defeated.** *(And the struck cell-per-relaxation-length figure itself rests on
   the 3× wrong L of `§2.3`: at the correct 25.4887 mm, L1 has 3.3 cells per
   relaxation length, not 9.8.)*

3. **A TRIPLE CANNOT BUY ANYTHING THIS CASE CAN USE ON ITS PRIMARY LIMB.** Limb
   A's ceiling is `GATE REACHED` on model-form grounds (`§4`), which a triple
   does not touch — a triple bounds discretisation error and says nothing about
   model-form or experimental error (`§2h.8.1`). The GCI would sit beside a row
   whose ceiling it cannot raise.

**PRECEDENT.** `cases/ansys_verification/VMFL024/PREREGISTRATION.md` §7 is this
team's standing precedent for a declined triple with an explicit defended
statement, and `§39.4` names it as the model for this document.

### §7.1 What this case ESTABLISHES

1. A **`GATE REACHED`** credential row: the lab's `pimpleFoam` +
   `kinematicThinFilm` finite-area film, set up from the manual's printed inputs
   alone, reproduces the experimental 0.555 mm inside a band frozen before
   compute.
2. A code-verification statement of the **exact-retention** class, `PASS`-capable:
   the discretisation admits the Nusselt state as an exact discrete solution,
   verified at three levels spanning **4× in Δx**, against a threshold that can
   fail.
3. That the monitor value **is not a boundary condition** (`§6.5`).
4. That the exact state is **retained over the whole plate** (`§6.4`).
5. A **measured** `pimpleFoam` + finite-area core-s/cell/step rate for this box
   (`§8.1`), closing a named unknown of the struck document.

### §7.2 What this case DOES NOT establish — stated so no reader infers it

1. **No order of accuracy, no GCI, no Richardson extrapolation, for any
   quantity.** This case says nothing whatever about the scheme's convergence
   *rate*. **This sentence must appear in the register row.**
2. **Nothing about nature.** Limb A is capped by its reference (`§4`);
   model-form error is unbounded by any instrument this lab owns.
3. **Nothing about meshes finer than L3.**
4. **Nothing about the monitor's true station**, which the manual never gives.
5. **Nothing about the water temperature** — inferred, and channel B is 91 % of
   the band.
6. **Nothing about Ansys** (charter §2).

### §7.3 If a limb fails — worked, fixed, solutioned; the gate is never widened

**No band, threshold, allowance or label in this document may be changed to
admit a result.** The repair order is:

1. **The injection geometry reading** (Γ = 76.2 × 0.005) — the one declared
   inference in the input chain. A different reading is a **different case** and
   gets its own registration and its own freeze.
2. **Setup defects** — the `Cf`/`forces`/`h₀` declarations, the faMesh boundary
   mapping, the inlet Γ.
3. **The exactness gate** — if it fails, the level-dependence is **measured**
   and is the finding; the gate is not widened and no level is dropped.
4. **Monitor development** — if B2 or the station check fails, extend the plate
   or move the monitor **as a new registration**, not as an edit here.
5. **The thin-film model itself** — if C1 holds (our numerics are sound) but Limb
   A still fails outside the band, the residual is **measured model-form error**.
   That is a **measured, persistent `GATE FAIL`** and it goes to Sanaa's desk
   with the evidence. It is **not** laundered into a pass.

### §7.4 What a future developing-region registration must know — recorded so it is not rediscovered expensively

A monitor sited in the **developing** region does carry genuine discretisation
error, and a triple there is non-degenerate. **It is not registered here**, for
reasons that were quantified rather than asserted:

- **Peak discriminability is at x ≈ 27 mm and reaches only 7.66 × T.** At that
  station δ = 0.6096 mm — **9.84 % from the manual's 0.555 mm** — so the primary
  limb is destroyed by construction. There is no station with both a defensible
  triple margin and a defensible δ.
- **The number there is set by OUR OWN arbitrary +30 % inlet perturbation.** A
  gate on it would be a gate on a free knob, and it could "pass" the manual's
  band for a reason we selected. That is worse than circular.
- **The non-nested monitor window (`§6.2`) contributes 2.196e-06 m there against
  a 2.125e-06 m signal — 1.03×, and non-monotone.** Cell-boundary-nested windows
  are mandatory for any such design.
- **A reference-based developing limb needs the `pf_` closure exactly right.**
  The hydrostatic part of `−h∇(pf)/ρ` is **0.27 % of gravity ≈ 1.5e-06 m in δ**
  there — **~70 % of the discretisation signal being measured.**

**If the lab wants an order-of-accuracy row for this solver, it gets its own
registration and its own freeze.**

### §7.5 The verdict logic, in the fixed vocabulary only (`CLAUDE.md` rule 1)

Evaluated in this order; the first that fires wins. **The comparator's
`verdict()` is a literal transcription of this conjunction and `--selftest`
carries ONE MUTANT PER CONJUNCT** — the answer to `§39.3`, where the struck
comparator would have granted a `PASS` on a condition strictly weaker than its
own document.

1. Strict completion (`§6.10` C-01…C-07) or a geometry refusal (`§6.6`
   C-14…C-17) or admissibility (`§6.7` C-13) fails → comparator **exit 2**,
   **`NOT A RESULT`**, no number produced and none may be quoted.
2. Plant **P1** or **P2** (`§6.8`) does not fire → comparator **exit 2**,
   **`NOT A RESULT`**.
3. **C-10** any level not plateaued, or **C-11** the station check fails →
   **`NOT A RESULT`** (exit 3).
4. **C-12** the exactness gate fails → **`NOT A RESULT`** (exit 3), the three
   values printed beside it.
5. Otherwise both limbs are graded:
   - **Limb A:** `C-18` e_A ≤ 2.12 % → **`GATE REACHED`** (its ceiling, `§4`);
     else **`GATE FAIL`**.
   - **Limb B:** `C-19` e_B ≤ 0.101 % **and** `C-20` C1 met **and** `C-21` B2 met
     → **`PASS`**; else **`GATE FAIL`**.

**A gate can only turn a `PASS`/`GATE REACHED` INTO `NOT A RESULT`, never the
reverse.** The case's registered ceiling is **`GATE REACHED` on Limb A and
`PASS` on Limb B.**

### §7.6 Amendment rule

Before first compute, amendments are legal and **must state the condition and
how it was checked** — naming the run directory that does not exist (`§0.1`).
**After first compute the gate is closed:** dated addenda only, which may not
alter a gate, threshold, cap or label, with originals struck and never
rewritten (`CLAUDE.md` rules 2 and 6).

---

## §8. COST (`CLAUDE.md` rule 12)

### §8.1 The method — MEASURED, not assumed

**The struck document's `§9` item 5 named the 2.0e-6 core-s/cell/step rate as
assumed and unmeasured on this box. It is now measured.** Per-step wall, single
core, `nice -n 19`, 20-step probes of this exact configuration (contended with a
live solver and including mesh read, so **an upper bound in two channels**):

| level | NZ = 1 s/step | steps | **core-min** |
|---|---|---|---|
| L1 (64 × 16 × 1) | 0.01300 | 2 000 | **0.43** |
| L2 (128 × 32 × 1) | 0.04100 | 4 000 | **2.73** |
| L3 (256 × 64 × 1) | 0.15800 | 8 000 | **21.07** |
| B2 (L3 geometry) | 0.15800 | 12 800 | **33.71** |
| C1 (L2 geometry) | 0.04100 | 4 000 | **2.73** |
| | | **METHOD TOTAL** | **60.66** |

**SERIAL, one rank, so core-minutes == wall minutes and the `timeout` cap is
exact.**

**Calibration of the struck document's assumed rate, as a by-product:** at the
registered NZ the measured s/step were 0.02450 / 0.13950 / 1.21450 at L1/L2/L3
against the model's 0.019661 / 0.15729 / 1.25830 — **ratio measured/model
1.246 / 0.887 / 0.965**, i.e. **accurate to 3.5 % at the level that dominates
cost** and ±25 % across the range. This row belongs in
`docs/COST_CALIBRATION.md` at completion.

**What NZ = 1 buys (`§3.6`):** at the struck NZ = 8/16/32 the same five runs cost
**199.95 core-min** — and that is what `e8cbe305` would actually have spent
against its own filed method total of 177.7.

### §8.2 What is filed, and the per-level caps

| | core-min |
|---|---|
| Method total | **60.66** |
| **FILED** | **92** (1.52 × method) |
| **CAP** | **185** (3.05 × method) |

**The `§26.2` cushion the struck document built against a 4.5× rate miss is
retired, because the rate is no longer assumed.** `§26.2`'s failure direction is
still respected: 185 is 3.05× the method, so an under-estimate cannot strangle
the run at the end.

**Per-level caps, enforced by `timeout` in the driver (`§9.2` G-08):**

| level | method | **cap** | cap seconds |
|---|---|---|---|
| L1 | 0.43 | **1.5** | 90 |
| L2 | 2.73 | **9** | 540 |
| L3 | 21.07 | **65** | 3 900 |
| B2 | 33.71 | **100** | 6 000 |
| C1 | 2.73 | **9** | 540 |
| | 60.66 | **184.5** | |

**An overrun STOPS THE RUN** (rule 12). It does not get a new budget: `timeout`
kills it, the wrapper records `rc = 124`, and the comparator refuses at C-01.

### §8.3 Dollars — DERIVED, never measured

At the owner-stated **$0.0513/core-h** (c7a.4xlarge; Sanaa 2026-08-21/22,
corroborated at `Xiao2016_EnKF/PREREGISTRATION.md:197`):

- filed 92 core-min = 1.533 core-h → **$0.079 derived**
- cap 185 core-min = 3.083 core-h → **$0.158 derived**

`cost_basis`: **derived from an owner-stated rate, NOT measured.** This box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5). Well inside the $25
pre-authorisation; CPU only, no GPU.

### §8.4 Calibration at completion (rule 12)

At completion the actual core-minutes from the logs are compared against the
**92** filed here; the row states the **ratio actual/predicted**, attributes the
gap (contention, waste, misprediction — **waste named separately, never absorbed
into the ratio**), and is appended to `docs/COST_CALIBRATION.md` under its append
rules and the rule-10 private-index protocol. **A completion report without that
row is incomplete.** It should additionally close out `§8.1`'s NZ = 1 rate for
the next film case.

---

## §9. THE GRADING PATH, THE DRIVER, AND THE FREEZE CHECKLIST

### §9.1 THE COMPARATOR PIN — complete, not deferred

> **COMPARATOR_BLOB = 7ff4abe4a8192cb71e8cd40d439e73baaff4827b**

This is `git hash-object cases/ansys_verification/VMFL072-R2/compare_vmfl072_r2.py`,
taken **without committing**. Writing it into this file changes *this* file's
blob and **does not change the comparator's**, so the pin is stable. The driver
reads it **out of this document** (G-03), so there is **one source of truth** and
no second copy that can drift, and **the check works before the freeze commit
exists as well as after it.**

At the freeze the comparator and this document are committed **in the same
commit**, and the driver additionally verifies every frozen file against its blob
at that commit (G-02).

`--selftest` result on this blob: **33 passed, 0 failed** — one mutant per
completion clause (C-01…C-07), per geometry refusal (C-14…C-17), the
admissibility mutant (C-13), **one mutant per verdict conjunct** (C-10, C-11,
C-12, C-18, C-19, C-20, C-21), both plants firing, five reader mutants refused by
P1, the degenerate plant set refused, the graded-area arm separating area
weighting from count weighting, and a P2 mutant that reads one level three times
refused. **And the selftest prints, as its own banner, that it proves LOGIC and
nothing about INTERFACE** (`§3.5`).

### §9.2 THE DRIVER — `launch_vmfl072_r2.sh`, and its eight guards

**It is a lab driver, not a tutorial `Allrun`.** It never `cd`s into the case
directory, never writes into `cases/`, and runs one registered level per
invocation into `verification/runs/ansys_verification/VMFL072-R2/<LEVEL>/`.

| guard | what it refuses |
|---|---|
| **G-00** | **every path this script reads or executes must EXIST** — all four frozen files, all fourteen case inputs, and `blockMesh makeFaMesh checkFaMesh pimpleFoam setsid timeout python3 git`, plus the run-root parent. **`bash -n` checks SYNTAX and never path existence** (`§38.1`), so this guard is executed, not asserted. |
| **G-01** | `VMFL072R2_PREREG_SHA` unset |
| **G-03** | comparator blob ≠ the `§9.1` pin **read out of this document**. **Runs BEFORE G-02, deliberately:** it needs no commit, so it is the check that still says something when G-02 cannot. |
| **G-02** | `VMFL072R2_PREREG_SHA` is not a commit, or any frozen file whose `git hash-object` ≠ its blob at that commit |
| **G-04** | a run root not under `verification/runs/`, or anywhere under `cases/` |
| **G-05** | a pre-existing run root — an existing run directory is **inspected, never overwritten** |
| **G-06** | any time directory but `0/` after staging |
| **G-07** | **the age guard.** `0/U` is touched **LAST** (after `blockMesh`, `makeFaMesh` and `checkFaMesh`, which write into `constant/`) and then **asserted**: `find 0 constant system -type f ! -path 0/U -newer 0/U` must be empty, else exit without launching |
| **G-08** | the solver runs under `timeout` at the level's `§8.2` cap, and **`rc` is captured INSIDE the detached wrapper** — `setsid timeout cmd` exits 0 for every outcome, so a wrapper capturing `rc` around the `setsid` line records a false success on a timeout, a signal or a crash alike |

**⚠ THE DRIVER WAS EXERCISED END TO END, NOT READ.** In a scratch git repository
holding a byte-copy of this case with `endTime` cut to 0.05 s — so **no gate
quantity could be produced** — every guard was driven:

| driven | result |
|---|---|
| G-00 with a case input removed | refused, **naming the missing path** |
| G-00 without the OpenFOAM environment | refused, naming `pimpleFoam` |
| G-01 with the sha unset | refused, exit 2 |
| G-02 with `deadbeef` | refused: *not a commit in this repository* |
| G-03 with the comparator edited and this document untouched | refused, both blobs printed |
| G-03 with the pin key renamed | refused: *carries no COMPARATOR_BLOB pin* |
| **a real launch at L1** | staged, meshed, age-guarded, launched; `RC.txt` recorded `rc=0`, `cap_sec=90`, `ranks=1`; the log carried `End` |
| G-07's predicate after `touch constant/g` | would refuse, **naming `constant/g`** |
| G-05 on a second invocation of the same level | refused |
| anything written under `cases/` | **nothing** |
| the comparator on that incomplete run | **REFUSED (exit 2): `C-03 L1: last time 0.05 != endTime 10.000000`** — no number produced |

> **⚠ AND RUNNING IT FOUND THREE DEFECTS IN IT THAT READING IT DID NOT.**
> (1) G-01 was written as `${VAR:?msg}`, which **exits 1 under `set -e`** while
> this script documents 2 for every guard refusal. (2) **`git rev-parse
> <bad>:<path>` ECHOES ITS INPUT** rather than failing cleanly, so the bogus-sha
> refusal printed the literal string `deadbeef:cases/…` as though it were a
> blob; it now uses `--verify --quiet` plus a 40-hex assertion. (3) G-03 sat
> *after* G-02 and was therefore unreachable in every case G-02 could also
> catch — it is moved ahead of it, which is also where it belongs, since it is
> the guard that works without a commit. **`bash -n` reported this script clean
> before all three.**

### §9.3 FREEZE CHECKLIST — for the supervisor's `§3` check 4

- [ ] **No open gate question** (`§11.2`): every gate, band, threshold, cap,
      level, ceiling and label in this document is a **number or a fixed
      label**. `§3.7`'s `DIFFERENT` ruling and the `GATE REACHED` cap are stated
      here, not deferred. Nothing reads "flagged for the supervisor".
- [ ] `VERIFICATION_CHARTER` `§2b` condition named and checked:
      `verification/runs/ansys_verification/VMFL072-R2/` **does not exist**
      (`§0.1`). *(`§2b` lives in `VERIFICATION_CHARTER.md`, not in this team's
      charter; the bare form appears nowhere in `ANSYS_VERIFICATION_CHARTER.md`
      and is qualified here so a reader can find it.)*
- [ ] **`§20.3` pre-freeze runs declared with every revealed quantity named**
      (`§0.2`).
- [ ] **`§38.1`: EVERY PATH THE DRIVER READS OR EXECUTES EXISTS AT THE FREEZE
      COMMIT** — enumerated in G-00 and **exercised**, not asserted.
- [ ] **`§39.5`: every path the comparator reads shown to be one the registered
      solver actually writes** (`§3.5`), by disk evidence and not by selftest.
- [ ] `compare_vmfl072_r2.py`, `apply_level.sh`, `launch_vmfl072_r2.sh` and the
      fourteen `base/` inputs committed in the **same commit** as this file; the
      grading path fixed there.
- [ ] The `§9.1` pin matches the committed comparator blob.
- [ ] Queue entry filed and committed (`§11.4`) — the queue carries the plan,
      not the agent.

**This draft is untracked. Committing it IS the freeze. No solver may launch
before that commit exists and is named in the launch record.**

---

## §10. WHAT THIS REGISTRATION DOES NOT KNOW — stated plainly

1. **Roy & Jain (1989) is not on this box.** Its Reynolds convention, its water
   temperature, its monitor station and its experimental uncertainty are
   **unknown to this lab from the source**. `§2.1`'s convention is inferred from
   the manual's own arithmetic; `§5.1` channel A is a **quoted-precision floor,
   not the experiment's uncertainty**.
2. **The water temperature is inferred (≈ 23.9 °C), never printed.** Channel B
   carries it and is **91 % of the band**.
3. **The monitor's streamwise station is a declared reading** (`§6.2`), tested by
   `§6.3` but not known from the manual.
4. **The injection geometry (Γ = 76.2 × 0.005) is a declared reading.** Strongly
   corroborated (0.075 % against Fluent) but an inference, and `§7.3` puts it
   first in the repair order.
5. **NZ = 1 is verified at L1 over 100 steps, not at a converged state**
   (`§3.6`). A converged NZ-sensitivity run would have revealed the gate before
   the freeze.
6. **`§7`'s residual table is a model, not a measurement.** It is stated with its
   form so a reader can check it, and the conclusion it supports survives a
   50,000× error in it.
7. **The solver's converged time-integration floor is not measured.** `§6.1`'s T
   is derived from the gate tolerance, as `§16.2` requires — which is why `§6.6`
   states plainly that the exactness gate has power against gross
   level-dependence and none against fine discretisation error.
8. **Model-form error is unbounded** by anything this lab owns (`§5.1` channel
   C). That is the ground of Limb A's cap and it is not quantified anywhere in
   this document.
