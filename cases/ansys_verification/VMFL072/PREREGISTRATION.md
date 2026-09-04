# VMFL072 — PRE-REGISTRATION (DRAFT, NOT YET FROZEN)

**Case** VMFL072: Liquid Water Flow Over a Flat Plate Under the Influence of Gravity
**Manual** Ansys Fluid Dynamics Verification Manual, Release 2026 R1 (March 2026), **p. 211–212**
(sidecar `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`, lines 5493–5545;
title-page verified against the PDF by the supervisor under `CLAUDE.md` rule 15)
**Team** ansys-verification · **Drafted by** `ansys-lane-opus` · **Draft date** 2026-09-04
**Status** `DRAFT — UNTRACKED`. This file is **not frozen**. The freeze is the supervisor's
undelegable §3 check 4 (`ANSYS_VERIFICATION_CHARTER` §5.1, §11.2) and happens at the commit
that first tracks these bytes. **No solver may launch until that commit exists and is named.**

---

## §0. THE §37.2 FREEZE CLAIM — WHAT THIS IS FROZEN *BEFORE*

`ANSYS_VERIFICATION_CHARTER` §37.2 forbids a bare "frozen before compute" that leaves a reader
to supply the most flattering reading. Stated explicitly, and each clause is checkable:

This registration is frozen **before the run, before the data, and before the reading**:

1. **Before the run.** No solver has been launched for VMFL072. The run directory
   `verification/runs/ansys_verification/VMFL072/` **does not exist** — checked by name at draft
   time (`ls -d` returns `No such file or directory`). This is the §2b named-condition check.
2. **Before the data.** No `hf_film` field, no time directory, and no log for this case exists
   anywhere on this box. Nothing has been computed that this document could have been fitted to.
3. **Before the reading.** No monitor value has been read by any instrument, and the comparator
   `compare_vmfl072.py` has never been executed against any VMFL072 field.

**What is NOT claimed:** the numbers in §3 are **arithmetic from the manual's own printed
inputs plus a source reading of the installed solver**, performed before any run. They are a
*prediction*, and §6.1 registers them as one. They were not read off a solve.

---

## §1. THE REFERENCE, AS THE MANUAL STATES IT

| item | value |
|---|---|
| Source | **Roy, R.P. & Jain, S. (1989).** *A study of thin water film flow down an inclined plate without and with countercurrent air flow.* **Experiments in Fluids (7) 318–328** |
| Class | **EXPERIMENTAL** |
| Table | **Table .72.1: Comparison of Film Thickness** |
| **Reference result (the gate's reference)** | **Film Thickness = 0.555 mm** ("Target") |
| Ansys Fluent's own reported value | 0.5497 mm, ratio 0.99 — **quoted for context, NOT the gate** (§5.1) |

**Roy & Jain (1989) is NOT on this box.** Measured, not assumed: a search of
`/home/ubuntu/Certonomous/docs/papers/` for `roy`, `jain` and `film` returns only
`oberkampf_roy_2011_verification_validation.{pdf,txt}`, which is a different Roy and a
different subject. **The paper is not fetched** (submissions/retrievals are not this lane's
call) and **its Reynolds-number convention and its stated experimental uncertainty are
therefore NOT known to this lab from the source.** Everything §2 and §4 say about those two
things is inference from the manual's own printed inputs, and is labelled as such.

### The manual's stated inputs (transcribed from p. 211–212)

| quantity | value |
|---|---|
| Film Reynolds number | **417** |
| Plate inclination | **40°**, no countercurrent airflow |
| Domain | 500 mm × 100 mm × 100 mm |
| Injection width | **5 mm** |
| Wall-monitor width | **50 mm** |
| Mass flux of water-liquid | **76.2 kg/m²·s** |
| Gravity | gx = **6.305746**, gy = **0**, gz = **−7.514896** m/s² |
| Modelling note | *"Air flow is zero, and the film flow is laminar."* |
| Physics/Models | **Eulerian Wall Film** (Ansys Fluent) |

---

## §2. THE Re / Γ RECONCILIATION — SETTLED BEFORE ANY GATE IS WRITTEN

### §2.1 The gravity vector is internally consistent (confirmed)

9.81·sin40° = **6.305746**, 9.81·cos40° = **7.514896**, |g| = **9.810000**, implied angle
**40.0000°**. The manual's vector is exactly a 40° inclination of standard gravity. Confirmed
to all printed digits. **No finding against the manual here.**

### §2.2 Which Re definition? — settled by the data, not by assumption

Roy & Jain's own convention is unavailable (§1). The manual's *other* printed inputs
overdetermine the problem, so the convention can be **tested** rather than guessed. Using the
Nusselt film thickness δ = (3μΓ / (ρ²·g·sinθ))^(1/3) with the supervisor's property set
(μ = 1.003e-3 Pa·s, ρ = 998.2 kg/m³), Γ taken *from Re*:

| convention | Γ [kg/m/s] | δ [mm] | vs 0.555 mm |
|---|---|---|---|
| **Re = Γ/μ** | 0.41825 | **0.5851** | **+5.42 %** |
| Re = 4Γ/μ | 0.10456 | 0.3686 | **−33.59 %** |

**`Re = 4Γ/μ` is REFUTED** — it misses the reference by a third, far outside any plausible
model-form or property allowance. **`Re = Γ/μ` is adopted**, and it is the only one of the two
that is even in the right neighbourhood.

*Corroboration, offered as corroboration and not as proof:* under `Re = Γ/μ = 417` the
alternative group **4Γ/μ = 1668**, which sits just below the conventional falling-film
laminar–turbulent transition (≈1600–2000). That is consistent with the manual's explicit note
that *"the film flow is laminar"* — a note that would be unremarkable, and so probably unwritten,
had the film been at 4Γ/μ = 417 (firmly smooth-laminar).

### §2.3 ⚠ THE SUPERVISOR'S 5.4 % GAP IS AN ARTEFACT OF DERIVING Γ FROM Re. IT CLOSES TO 0.88 %.

**This is a refutation of the arithmetic handed down, and it is stated first because it changes
the case.** The supervisor's chain took Γ *from* Re (Γ = Re·μ) with μ = 1.003e-3 Pa·s (water at
20 °C) and obtained δ = 0.585 mm, 5.4 % above target — a gap large enough to look like a
model-form problem or a wrong Re convention.

**But the mass flux is a PRIMARY printed input and Re is a derived descriptor.** Reading
"Injection width: 5 mm" as the **streamwise extent of a full-span injection strip** (§2.4):

```
Γ = 76.2 kg/m²·s × 0.005 m = 0.381000 kg/m/s
```

This is an independent determination of Γ that uses **no** viscosity at all. The two printed
inputs then **overdetermine μ**, and self-consistency pins it:

```
μ = Γ / Re = 0.381000 / 417 = 9.136691e-04 Pa·s     →  water at ≈ 23.9 °C
```

That is an entirely ordinary laboratory water temperature. With ρ = 997.4 kg/m³ at that
temperature:

```
δ_N = (3 μ Γ / (ρ² g sinθ))^(1/3) = 5.501148e-04 m = 0.5501 mm
```

| comparison | value | error |
|---|---|---|
| δ_N vs the manual's **Target 0.555 mm** | 0.5501 | **−0.88 %** |
| δ_N vs **Ansys Fluent's 0.5497 mm** | 0.5501 | **+0.075 %** |

**The manual's stated inputs ARE self-consistent**, under a single unstated but physically
ordinary property set, and that same property set reproduces Fluent's own answer to **0.075 %**
— which is far better agreement than either has with the experiment. That is strong evidence
that (a) the reading in §2.4 is the right one, and (b) Fluent's Eulerian Wall Film is, for this
configuration, integrating the same depth-averaged balance whose exact solution is δ_N.

**What is inferred and not printed:** the water temperature. The manual never states it. §4's
band carries that ambiguity as its dominant channel, quantified, rather than hiding it in a
fudge factor.

### §2.4 The geometric reading of "Injection width: 5 mm" — DECLARED, with the rejected alternatives

The manual does not say which direction the 5 mm runs. Four readings were tested against the
printed target; **only one closes.**

| reading | Γ [kg/m/s] | δ at μ = 1.003e-3 | verdict |
|---|---|---|---|
| **R1 — 5 mm is the STREAMWISE extent of a strip spanning the full 100 mm width** | **0.381** | 0.5669 mm (at 20 °C) | **ADOPTED** |
| R2 — 5 mm is the spanwise width, strip length unstated | underdetermined | — | unusable |
| R3 — injection is a 5 mm × 5 mm square, film spreads to the 50 mm monitor | 0.0381 | 0.2716 mm | **REFUTED, −51 %** |
| R4 — full-span 100 mm × 5 mm streamwise: ṁ = 76.2 × 0.1 × 0.005 = 0.0381 kg/s, Γ = ṁ/0.1 | **0.381** | as R1 | **identical to R1** |

R1 and R4 are the same physical statement reached two ways, which is why the reading is robust.
**The wall-monitor's 50 mm is a SAMPLING WINDOW, not a film width** — the film spans the full
100 mm and the monitor reads the middle half of it, away from the side walls. Under R3 (film
confined to a narrow ribbon that then spreads) the answer is off by half; that reading is dead.

**This is a declared reading of an ambiguous input, not a measurement.** If it is wrong, the
case is a different case, and §7's failure analysis names it as the first thing to re-examine.

### §2.5 Registered property closure (all derived from the manual's own printed inputs)

| symbol | value | provenance |
|---|---|---|
| Γ | **0.381000 kg/m/s** | 76.2 kg/m²·s × 0.005 m (printed inputs, §2.4 R1) |
| μ | **9.136691e-04 Pa·s** | Γ/Re with Re = 417 (printed inputs, §2.2 convention) |
| ρ | **997.4 kg/m³** | density of water at the temperature implied by μ, standard correlation |
| g·sinθ | **6.305746 m/s²** | printed (gx) |
| implied T | ≈ 23.9 °C | **inferred, not printed** |

ρ enters as ρ^(−2/3); using 998.2 instead of 997.4 moves δ by **+0.056 %**, which is inside
§4's channel B and is not carried separately.

---

## §3. THE PHYSICS PATH — MEASURED CAPABILITY, AND THE §12.2 SAMENESS RULING

### §3.1 What this box actually has (measured, with proving paths)

**Fork and version:** OpenFOAM **v2606, ESI / OpenFOAM.com fork**, at
`/usr/lib/openfoam/openfoam2606/` (`etc/bashrc` → `WM_PROJECT_VERSION=v2606`;
`META-INFO/api-info` → `api=2606`). Build **`linux64GccDPInt32Opt`** — **double precision**,
which §5.3 relies on. This is independently corroborated by a live solver process the
supervisor observed running from `platforms/linux64GccDPInt32Opt/bin/`.

**Two distinct film capabilities are present, source AND compiled library:**

| capability | source | compiled |
|---|---|---|
| **Finite-area thin film** (`regionFaModels`) — `kinematicThinFilm`, driven by the `velocityFilmShell` patch BC | `src/regionFaModels/liquidFilm/kinematicThinFilm/kinematicThinFilm.C` | `libregionFaModels.so` |
| Legacy 3D film-region (`regionModels/surfaceFilmModels`) — `kinematicSingleLayer`, `thermoSingleLayer` | `src/regionModels/surfaceFilmModels/` | `libsurfaceFilmModels.so`, `libsurfaceFilmDerivedFvPatchFields.so` |
| Standalone finite-area film solver | `applications/solvers/finiteArea/liquidFilmFoam/` | `bin/liquidFilmFoam` |
| VOF family (fallback path) | — | `bin/interFoam`, `interIsoFoam`, `libgeometricVoF.so` |

**Working templates shipped with the install — a tutorial is worth more than a header:**

- `tutorials/incompressible/pimpleFoam/laminar/inclinedPlaneFilm` — a **laminar liquid film
  draining down an inclined plane**, `constant/g = (4.905 0 −8.4957)` = 9.81·(sin30°, −cos30°).
  **This is VMFL072's exact construction at a different angle.**
- `tutorials/incompressible/pimpleFoam/laminar/filmPanel0` — the same machinery configured with
  **`friction quadraticProfile; Cf 0;`**, which is precisely the closure §3.2 requires.

**The film thickness is a directly-written primitive field**, `hf_film` (`dimensions [0 1 0 0 0
0 0]`), on the finite-area mesh. **The gate quantity needs no isosurface extraction, no
reconstruction and no post-processing model.** That is a decisive advantage over the VOF path
and it is why VOF is relegated to §3.5.

### §3.2 ⚠ THE LOAD-BEARING SOURCE FINDING: `quadraticProfile` IS THE NUSSELT BALANCE, EXACTLY

Verified by reading the installed source, not inferred from the option's name.

`src/regionFaModels/liquidFilm/kinematicThinFilm/kinematicThinFilm.C`, `UEqn()`:

```
fam::ddt(h_, U) + fam::div(phi2s_, U)
  == gs*h_ + turbulence_->Su(U) + faOptions()(...) + forces_.correct(U) + USp_
```
with `gs = g_ - ns*(ns & g_)` — gravity projected onto the plate.

`.../filmTurbulenceModel/laminar/laminar.C`: `Su(U) = primaryRegionFriction(U) + wallFriction(U)`,
and `wallFriction(U) = -fam::Sp(Cw, U) + Cw*Uw` with `Uw` the wall velocity (**= 0**).

`.../filmTurbulenceModel/filmTurbulenceModel.C`, `Cw()`, case `mquadraticProfile`:

```
Cw = 3*mu/((h + h0)*rho)
```

With `Cf = 0` (no gas shear — the manual says air flow is zero) and `forces ()`, the steady,
fully-developed, gradient-free state satisfies

```
g·sinθ · h = Cw · U = 3μU / (ρ(h+h₀))
  ⇒ U = ρ g sinθ h(h+h₀) / (3μ)          (Nusselt mean velocity, exactly)
  ⇒ Γ = ρhU  ⇒  h = (3μΓ / (ρ² g sinθ))^(1/3)   (Nusselt film thickness, exactly)
```

**`quadraticProfile` is literal: it is the parabolic-velocity-profile wall-shear closure, and
the Nusselt solution is an EXACT steady solution of the PDE this solver discretises** — not of a
reduction of it (uniform h and U make `ddt` and `div` vanish identically). This is what makes
§6's Limb B available.

`h₀` (`liquidFilmBase.C:74`) defaults to **1e-7 m**. Against δ ≈ 5.5e-4 m that is h₀/h = 1.8e-4,
biasing δ by ≈ **6e-5 relative** — measured, negligible, and **registered at its default**.

**The shipped `inclinedPlaneFilm` tutorial uses `friction ManningStrickler` with `n = 0.1` and
`Cf = 0.9`, which is an empirical open-channel law and is WRONG for a laminar film.** Copying
that tutorial unmodified would have silently produced a different physical model. Registered
here so it cannot happen by accident. Likewise `liquidFilmFoam` (§3.5) uses an empirical
`frictionFactor` correlation and is **rejected for the same reason**, despite being the
cheaper solver.

### §3.3 SELECTED PATH — registered configuration

**Solver** `pimpleFoam` (v2606), transient, incompressible, primary region **laminar**.
**Film** `velocityFilmShell` BC on the plate patch, `liquidFilmModel kinematicThinFilm`,
finite-area region `film` built by `makeFaMesh`.

```
turbulence        laminar;
laminarCoeffs { shearStress simple;  friction quadraticProfile;  Cf 0; }
injectionModels ();
forces          ();          // NO contact-angle force: continuous full-span sheet, no dry-out
region          film;
liquidFilmModel kinematicThinFilm;
```

- **`Cf 0`** — the manual states air flow is zero; a non-zero `Cf` is a damping on the film even
  with quiescent air (`Su += -Sp(Cf,U) + Cf*Up`, `Up = 0`), and would corrupt the balance.
- **`forces ()`** — the tutorials carry `dynamicContactAngle`, an edge/rivulet force. VMFL072 is a
  continuous sheet at 0.55 mm with no dry patch; including it would add a model term the manual's
  setup does not have **and would break §6's Limb B condition 1.** Registered as excluded, before
  compute, with that reason.
- **Feeding the film.** `regionFaModels/liquidFilm` has **no dictionary-driven mass-source
  injection model** — measured: `subModels/kinematic/injectionModel/` contains only
  `BrunDrippingInjection` and `filmSeparation`, both of which **remove** film. Mass therefore
  enters at the **finite-area inlet boundary**, as prescribed `hf_film` and `Uf_film` with
  ρ·h_in·U_in = Γ = 0.381 kg/m/s.

**⚠ The circularity this creates, and how it is defeated.** Prescribing h at the inlet risks
prescribing the gate quantity. It is defeated by **deliberately setting the inlet off
equilibrium** and reading the monitor far downstream, so the monitor value is a *solved
relaxation*, never a boundary condition:

```
nominal runs:   h_in = 1.30 × δ_N = 7.1515e-04 m ,  U_in = Γ/(ρ h_in) = 0.53415 m/s
bracket  B2  :  h_in = 0.70 × δ_N = 3.8508e-04 m ,  U_in = Γ/(ρ h_in) = 0.99200 m/s
```

Both carry the **identical** Γ. The momentum relaxation constant is τ = ρδ²/(3μ) = **0.1101 s**
and U_eq = **0.6944 m/s**, giving a relaxation length U_eq·τ = **76.5 mm**. The monitor at
x = 450 mm is **5.9 relaxation lengths** downstream, so a 30 % inlet perturbation decays to
≈ 0.08 %. **This is registered as a bound to be MEASURED by the B2 bracket, not assumed:**
§4 channel E allows 0.20 % for it and §6.4 requires the two inlet conditions to agree.

**Geometry and gravity, as printed.** Plate 500 mm (x, downslope) × 100 mm (y, span); gas box
100 mm in z. `constant/g = (6.305746 0 −7.514896)`.
**Material**, per §2.5: μ = 9.136691e-04 Pa·s, ρ = 997.4 kg/m³.
**Injection**: full-span film inlet at x = 0 (the §2.4 R1 reading).

### §3.4 §12.2 — THE SAMENESS RULING PROPOSED TO THE SUPERVISOR

Answered in §12.2's own four required parts, on the face of the document, before the freeze.

1. **The continuum model the lab's solver discretises.** The depth-averaged (lubrication) thin
   liquid-film equations on a surface: ∂h/∂t + ∇·(h**U**) = 0 and
   ∂(h**U**)/∂t + ∇·(h**UU**) = h**g**_t − (3μ/ρh)**U** − (1/ρ)[∇(p h) − p∇h],
   incompressible, Newtonian, laminar, parabolic through-thickness velocity profile, zero gas
   shear. Verified against the installed source in §3.2.
2. **The model the reference is the exact solution of.** **None.** The reference 0.555 mm is an
   **experimental measurement** of a real water film (Roy & Jain 1989) — the behaviour of the
   full three-dimensional incompressible Navier–Stokes system with a deformable free surface,
   including the interfacial waves that a film at 4Γ/μ = 1668 certainly carries.
3. **Are those the same model?** **`DIFFERENT`.** An experiment is not the solution of any
   reduced model, and the residual between a depth-averaged smooth-film model and a real wavy
   film is **model-form error, which no grid triple bounds.**
4. **Consequence.** Registered at **`GATE REACHED` from the outset**, per §12.2 and per
   `VERIFICATION_CHARTER` **§2h.8.1** (v1.27, 2026-08-31, the exact-PDE rule, as renumbered by
   v1.28; cited in the §12.3 long form, never as a bare `§2h.6`), whose text is explicit:
   *"A reference drawn from a DIFFERENT MODEL — nozzle relations, shock tables, lumped or
   series-resistance paths, correlations, **experiment** — CAPS AT `GATE REACHED`, HOWEVER EXACT
   ITS OWN ALGEBRA."* §2h.8.3 repeats it: *"experiment, correlation and every different-model
   reference remain capped at `GATE REACHED`."*

**This cap is a property of the reference, not of our workmanship.** No amount of fixing on our
side can lift Limb A to `PASS`, and §12.2's closing warning cuts the other way too — the cap is
the one the charter imposes, not the most conservative available. **`GATE REACHED` is this
limb's ceiling and reaching it is a success, not a shortfall**, which is the honest reading of
Sanaa's 2026-09-04 "at the very least a gate pass" bar for this case.

**§33.2 does not fire.** That clause governs *code-to-code* references and their circularity.
Fluent's 0.5497 mm is exactly such a reference — vendor-produced, and were it the gate it would
be circular and capped. **It is not the gate** (§5.1), it is context. The gate's reference is
the experiment.

### §3.5 The VOF alternative — considered, ruled SECONDARY, and why

A VOF reproduction (`interFoam`, thickness from the α = 0.5 isosurface) was assessed as the brief
directed. **It is ruled the secondary path and is not registered for this run.**

- **§12.2 sameness would be no better and arguably worse.** VOF discretises full 3D
  Navier–Stokes with a captured interface — closer to the *experiment*, but still `DIFFERENT`
  from it (an experiment is not a model), so **Limb A's cap is identical either way**. VOF buys
  nothing on the gate.
- **It destroys Limb B.** VOF's converged solution is not the exact Nusselt state, so the
  `PASS`-capable code-verification limb of §6.2 disappears entirely. **The film path is strictly
  better here.**
- **The reader gets worse, not better.** `hf_film` is a written primitive field; an α = 0.5
  isosurface thickness is a reconstruction with its own resolution floor, and resolving a
  0.55 mm film across a 100 mm domain needs ≳ 20 cells through the film — an interface-resolved
  mesh two to three orders of magnitude more expensive than §8's estimate.
- **Retained as the R2 path** if §7's failure analysis shows the thin-film assumption itself is
  the defect. It would then be registered separately, `GATE REACHED`-capped, with its own freeze.

---

## §4. THE GATE

**Gate quantity** — the **area-weighted mean film thickness δ_mon over the wall-monitor
window**, on the finest level run.

**Limb A (primary, against the manual).**

```
e_A = | δ_mon − 0.555 mm | / 0.555 mm   ≤   2.72 %
```

**Ceiling `GATE REACHED`** (§3.4). Inside the band → **`GATE REACHED`**; outside → **`GATE
FAIL`**; either is overridden to **`NOT A RESULT`** by rule 5, the plateau criterion (§5.2) or a
refused plant (§5.4). Admissible interval: **δ_mon ∈ [0.5399, 0.5701] mm**.

### §4.1 The band's derivation — channel by channel, none of it fitted to an answer

**The band is the linear (not RSS) sum of named channels.** Linear is the conservative choice
and it avoids any appearance of shrinking the band.

| ch | source | magnitude | how it was obtained |
|---|---|---|---|
| **A** | Reference's quoted precision | **0.090 %** | "0.555" is 3 s.f. → ±0.0005 mm. **A FLOOR on the reference's uncertainty, not an estimate of it** — Roy & Jain's own stated uncertainty is unavailable (§1) and is **not invented**. |
| **B** | Unstated fluid properties | **1.926 %** | The manual never states water temperature. **δ ∝ μ^(1/3) at fixed Γ** — δ = (3μΓ/(ρ²g sinθ))^(1/3), so at fixed **Γ** the exponent is **1/3**; the exponent 2/3 applies only at fixed **Re** (where Γ = Re·μ carries a second factor of μ). Computed at fixed Γ = 0.381: δ(20 °C) = 0.5669 mm, δ(25 °C) = 0.5455 mm; half-width about the midpoint = 1.926 %, which is the ^(1/3) span (μ(20)/μ(25) = 1.1250, ^(1/3) → 4.00 % full span) plus the small ρ variation. **The dominant channel, and it comes from the manual's silence, not from any run.** |
| **D** | Discretisation | **0.500 %** | An *allowance*, enforced as a **requirement**: GCI at Fs = 1.25 on the finest level must be ≤ 0.500 %. **If it exceeds this the mesh is refined — the band is NOT widened** (§7.2). |
| **E** | Inlet-relaxation residual | **0.200 %** | An *allowance*, enforced as a **requirement**: the B2 bracket must agree with the nominal within 0.200 % (§6.4). Consistent with the 5.9-relaxation-length estimate of §3.3, but **measured, not assumed**. |
| | **BAND** | **2.716 % → registered 2.72 %** | |

**Channel C — model form — is deliberately NOT in the band.** The residual between a smooth
depth-averaged film model and a real wavy film at 4Γ/μ = 1668 is unbounded by any instrument
this lab owns. **Folding an unbounded model-form error into a band is precisely the error
`VERIFICATION_CHARTER` §2h.8.2 exists to prevent.** It is instead **the ground of the
`GATE REACHED` cap** (§3.4). Naming it and capping for it is the honest treatment; pricing it
into a number would not be.

### §4.2 Why this band is not chosen to admit our answer

- Every channel was fixed from the **manual's printed inputs and its silences**, before compute.
  Channel B, which is 71 % of the band, is a property sweep over a temperature range the manual
  does not state; it has no dependence whatever on any lab result.
- **The band can fail.** Nothing in the plausible property range 20–25 °C, combined with the full
  numerical allowance, can place δ outside [0.5399, 0.5701] mm. A result outside it is **not
  explicable by any admissible input choice** and would indicate a setup, mesh, boundary-condition
  or model defect — which is exactly what a gate is for.
- Rounding is **down to the arithmetic**, 2.716 → 2.72 %, not up to a convenient 3 %.
- The band was **not** sized from Fluent's 0.5497 mm. Fluent's number appears in this document
  only as §5.1 context and as the §2.3 corroboration of the property closure.

---

## §5. HOW THE NUMBER IS READ, AND THE CONTROLS ON THE READER

### §5.1 The reader, its window, and its resolution

**Reader:** `cases/ansys_verification/VMFL072/compare_vmfl072.py` (draft alongside this file;
**its sha is fixed at this document's freeze commit** and the grading path is fixed there, per
`CLAUDE.md` rule 2 — the frozen file must be hashed against the committed blob before grading).

**Field read:** `hf_film`, the finite-area film-thickness field, from the **finest level's
`endTime` directory of the film region**. No derived quantity, no isosurface, no reconstruction.

**Monitor window** — the manual gives the monitor's width (50 mm) but **not its streamwise
station; the station below is a DECLARED reading:**

```
faces whose centres satisfy   x ∈ [0.440, 0.460] m   AND   y ∈ [0.025, 0.075] m
δ_mon = Σ(hf_i · A_i) / Σ(A_i)     (area-weighted mean over that set)
```

- **50 mm spanwise**, centred on the 100 mm span — the manual's monitor width, keeping the side
  walls out of the reading.
- **x = 450 ± 10 mm** — 50 mm clear of the outlet so the outlet BC cannot enter, and 5.9
  relaxation lengths clear of the inlet (§3.3).
- **Falsifiable station check, with its OWN threshold.** The comparator reports δ_mon at
  x = 300, 350, 400 and 480 mm. **If the spread across x ∈ [300, 480] mm exceeds
  `STATION_SPREAD_MAX = 5.275e-06 m`, the film is not developed at the monitor and the verdict
  is `NOT A RESULT`** — the reading is not quietly relocated.

  **Derivation, and it is a DIFFERENT physical criterion from §5.2's temporal plateau.**
  Channel E allows a residual of 0.200 % of δ_N at the monitor. The inlet perturbation decays as
  exp(−x/L) with L = 76.5 mm (§3.3), so a run just meeting channel E has a station spread of at
  most resid(450)·(e^(130/L) − e^(−30/L)) = 0.002·5.501e-4·(5.46 − 0.676) = **5.275e-06 m**.
  **⚠ Reusing §5.2's temporal threshold here — as this document's first draft did — would have
  FALSELY REFUSED A HEALTHY RUN by 10.7×**: a sound run with a 30 % inlet perturbation has an
  expected spread of 2.958e-06 m, which is 10.7 × the 2.775e-07 m plateau bound. A temporal
  drift bound and a streamwise development bound are two criteria and take two constants.
  Falsifiability: 5.275e-06 m is 5.3e9 × the reader quantum.

**Reader resolution (quantum), stated as a number.** `writeFormat ascii; writePrecision 12;` is
**registered as part of the case setup**, giving a file quantum of ≈ **1e-15 m** on a 5.5e-4 m
value. Per the §25.4 principle the registered quantum is the **maximum** of the floors, so the
governing floor is the solver's own iterative floor, held below it by
`faSolution` tolerances on `h` and `Uf` of **≤ 1e-10** (registered). **Every threshold in this
document is stated against that floor in §5.2 and §5.3, so none is unfalsifiable** (§35.1, §37.1).

### §5.2 The plateau criterion — FROZEN HERE, BEFORE COMPUTE (§16)

**Channel:** δ_mon(t), the §5.1 monitor mean, sampled at every write (`writeInterval 0.05 s`).
**Window:** the **last 2.0 s** of the run (t ∈ [8.0, 10.0] s), i.e. 40 samples.
**Threshold:** peak-to-peak of δ_mon over the window **≤ 0.05 % of 0.555 mm = 2.7750e-07 m.**

**Justified from the gate tolerance, never from an observed floor** (§16.2). The tightest band in
play is Limb B's 0.700 %; 0.05 % is **14×** tighter, so plateau noise can contribute at most
1/14 of the tighter band and cannot move either verdict. **It is a number, not `ptp → 0`,** so it
is satisfiable against a bounded limit cycle (§16.1).
**Falsifiability check (§35.1/§37.1):** the threshold 2.7750e-07 m is **2.8e8 ×** the reader's
1e-15 m quantum. It is resolvable by the instrument that must test it.
**One-way (§2h.4 condition 2):** a level failing this is **`NOT A RESULT`** regardless of any
other result, and no path in the comparator may turn that into a `PASS` or a `GATE REACHED`.

**`endTime` is generous enough that the criterion, not the clock, decides** (§16.2):
`endTime = 10.0 s` = **13.9** plate-advection times (0.720 s each) = **91 τ**. `endTime` was set
from these two physical time scales, computed before compute, **not from an observed settling
iteration.**

### §5.3 Round-off, stated with its magnitude (§2h.4 condition 3)

Build `linux64GccDPInt32Opt` — **double precision**, ε = 2.22e-16. Over the ~7.1e3 (L3) to ~1e5
(bound) time steps of this case, random-walk accumulation is ≈ **7.0e-14 relative**, i.e.
**3.9e-14 mm** on δ. Against Limb B's 0.700 % band that is a ratio of **1.0e-11**.
**Negligible, as a number.**

### §5.4 The planted-zero control (`CLAUDE.md` rule 3, §16.4, §35.2)

The comparator **refuses (exit 2)** and produces no number unless the plant fires.

**⚠ THIS SECTION'S FIRST DRAFT SPECIFIED A CONTROL THAT COULD NOT FAIL. RECORDED, NOT QUIETLY
REPLACED.** That draft planted P into **exactly** the faces it then averaged over. Plant set and
averaging set being the same set, the area-weighted mean shifts by exactly P **by algebra, for
every possible input**. Measured, not inferred: driven with ordinary film values, wildly
non-uniform values, all-identical values, negative garbage and **all zeros**, |shift − P| came
back ≤ 1.2e-14 and the control **passed every time, including on all zeros** — the precise
condition rule 3 exists to catch. The draft's own defence — *"P is fixed from the band, so there
is no configuration in which this passes by construction"* — had a **true premise and an invalid
conclusion**: sizing P from the band defeats *tuning*; it does nothing about *cancellation*.
This is `§29.3`/`§35.2` recurring inside a file that cited `§35.2` while breaching it.

**Plant P1 — the monitor reader.** The comparator copies the graded `hf_film` to a scratch file
and adds **P = +1.234000e-05 m to a PROPER SUBSET of the monitor window, by area** — the faces
with **y < 0.050 m**, the lower half-span (frozen here as `PLANT_SUBREGION_Y_MAX`). It re-reads
through the same reader code path and requires

```
| δ_mon(planted) − δ_mon(clean) − P·f |  <  1.0e-09 m ,
      f = Σ(area of planted faces) / Σ(area of window faces)
```

**`f` is computed from the geometry the comparator itself reads; it is never hard-coded.** The
comparator also **refuses** if the sub-region selects zero faces, or if it selects the *whole*
window — the degenerate case that reproduces the inert first draft.

**Why it can now fail — demonstrated, not asserted.** `--selftest` drives the control with six
mutant readers and **all six are refused**: unweighted mean, averages the whole plate, returns a
constant, reduces by max, reads a stale file, window shifted +20 mm. Recovering P·f requires the
reader to integrate the *right faces* with the *right weights*.

**⚠ TWO HONEST LIMITS, SO NO READER OVERRATES THIS CONTROL.**

1. **On a uniform mesh the area-weighted and unweighted means are the same function.** §5.6's
   production meshes are uniform, so that mutant is **not discriminable there** — not because the
   plant is weak, but because the two are not two readers. The `--selftest` non-uniform arm
   (area varying along the same axis as the sub-region predicate, f = 0.4221 ≠ 0.5000 = the count
   fraction) is where the weighting is exercised, and the unweighted mutant **is** refused there.
2. **An additive plant on a LINEAR reader shifts the mean by a field-independent amount.** That
   is a property of linearity and **no plant can defeat it**, so P1 alone still passes on an
   all-zeros field. **The all-zeros hole is closed by ADMISSIBILITY, not by the plant:** the
   comparator refuses any δ_mon that is non-positive or below **1.0e-06 m** — 550× below δ_N,
   far too low to be mistaken for a gate, and a value no film-producing run can return.

**Plant P2 — the null control (§16.4).** Limb B's control C1 (§6.3) expects **zero** drift, and a
null needs its own plant. The same subset plant is applied to C1's retained field and the drift
metric must move by P·f within 1.0e-09 m, else **REFUSE**.

**§35.2 compliance.** The plant acts on a **copy in scratch**; graded fields are never mutated.
P's magnitude was fixed from the **band** and the sub-region from the **geometry**, neither from
any measured value; §4's tolerances came from the manual's inputs, not from any run. **And the
control is now demonstrated to fail on six distinct mutant readers — which is the claim the
first draft made and could not support.**

### §5.5 Strict completion (`CLAUDE.md` rule 4) — the comparator refuses (exit 2) on any clause

1. **`rc = 0`**, captured **inside** the detached wrapper, never around the `setsid` line
   (`setsid timeout cmd` returns 0 for every outcome).
2. An **`End`** line in the solver log.
3. **Last time directory == `endTime` == 10.0**.
4. **Fields present at `endTime`:** primary region `U`, `p`; film region `hf_film`, `Uf_film`.
5. **Step accounting.** Rule 4's "`ExecutionTime` count == `endTime`" is written for a
   fixed-step steady solve and does not transfer verbatim to an adjustable-step transient.
   **Registered analogue, stated rather than silently substituted:** the number of written time
   directories == `endTime`/`writeInterval` == **200**, and the `ExecutionTime` line count equals
   the solver's own reported time-step count. **Both are checked; neither is skipped.**
6. **Age guard.** Every field at `endTime` is **strictly newer** than the case's own `0/U`.
   **⚠ This is only valid if `0/U` is touched LAST at launch, and until the launcher existed
   that was an ASSUMPTION, not a property.** It is now a property:
   `cases/ansys_verification/VMFL072/launch_vmfl072.sh` touches `0/U` after every other input,
   then **asserts** it — `find 0 constant system -type f ! -path 0/U -newer 0/U` must return
   empty, and **the launcher exits 2 without launching if it does not.** The comparator's guard
   and the launcher's assertion are two halves of one control; neither is sufficient alone.
7. **Launch guard.** The launcher **refuses** if `0/` or any time directory already exists, and
   **refuses to launch at all unless `VMFL072_PREREG_SHA` is set and the pre-registration on disk
   hashes equal to the committed blob at that sha** (`CLAUDE.md` rule 2 — the frozen file must be
   *the file that ran*).

### §5.6 Grid triple (`CLAUDE.md` rule 5)

**A triple IS required.** The gate quantity is a field value at a station, the case has no
symmetry that makes it mesh-exact, and Limb B's discretisation-error claim needs it.

| level | film patch (x × y) | Δx | 3D cells | r |
|---|---|---|---|---|
| **L1** | 64 × 16 | 7.813 mm | 8 192 | — |
| **L2** | 128 × 32 | 3.906 mm | 65 536 | 2 |
| **L3** | 256 × 64 | 1.953 mm | 524 288 | 2 |

Uniform refinement ratio **r = 2** in all directions, satisfying Roache's requirement. GCI at
**Fs = 1.25**, printed beside the verdict; **never quoted when the three values are not
monotone.**

**⚠ The trap this design is built to avoid, named before compute.** The fully-developed film is
*near-uniform*, and a triple on a solution that is uniform to machine precision returns `EXACT`
or `STAGNANT` — which under rule 5 is **`NOT A RESULT`**, whatever the value. That is defeated by
**deliberately making L1 coarse enough for its truncation error to be unmistakable**: at
Δx = 7.813 mm there are only **9.8 cells per 76.5 mm relaxation length**, so the advective
relaxation is genuinely under-resolved at L1 and the triple carries real signal. This is a
design choice made **for** the triple's informativeness, recorded so it is not mistaken for an
arbitrary mesh ladder.

**The `EXACT`/`STAGNANT` threshold, and what actually guards the trap.** Two levels are declared
indistinguishable when they differ by less than **`TRIPLE_RESOLVE_M = 2.7750e-07 m`, the run's own
temporal plateau noise (§5.2)** — levels closer together than the experiment's own noise are not
resolved by it, whatever the file precision.

> **⚠ The first draft used the 1e-15 m file quantum here. At 2e-12 relative that limb could
> essentially never fire — an inert guard that reads as protective.** It is corrected rather than
> left in place, **and the honest statement is this: even repaired, the coded threshold is a
> backstop, not the primary guard. The primary guard against the near-uniform-film `EXACT` trap
> is the DESIGN — L1 deliberately coarse at 9.8 cells per relaxation length.** A reader of these
> bytes should not credit the constant with work the mesh ladder is doing.

**A non-`CONVERGING` triple is `NOT A RESULT`** — standing law (rule 5), applied, not a question
left open. The Clause B smoke (post-freeze) additionally *reports* |δ_L1 − δ_L3| against
`TRIPLE_RESOLVE_M` as a **diagnostic**; **that diagnostic may not alter any gate, band or label.**

---

## §6. THE TWO LIMBS

### §6.1 The registered PREDICTION (prediction-first, `CLAUDE.md` rule 2)

From §3.2's source reading and §2.5's property closure, computed **before any run**:

> **δ_mon = 0.5501 mm**, to within discretisation, iterative and inlet-relaxation error.

If the run lands materially away from this, **our reading of the installed solver is refuted**,
and that is a finding worth more than a passing row. This is the strongest form the freeze can
take: the document states the answer it expects and names what would break it.

### §6.2 Limb B — CODE VERIFICATION against the exact solution of the same continuum model

Distinct from Limb A and graded separately.

**Reference:** δ_N = (3μΓ/(ρ²g sinθ))^(1/3) = **5.501148e-04 m**, evaluated at §2.5's closure.
**This is `PASS`-capable** under `VERIFICATION_CHARTER` **§2h.8.1** (v1.27, 2026-08-31, the
exact-PDE rule, as renumbered by v1.28), because — unlike Limb A's experiment — it **is** the
exact steady solution of the very PDE the solver discretises (§3.2).

```
e_B = | δ_mon − δ_N | / δ_N   ≤   0.700 %      (= channel D 0.500 % + channel E 0.200 %)
```

Channels A and B **do not appear** in Limb B: the property set is *shared* between our run and
δ_N, so it cancels identically, and no experimental reference is involved. **Limb B's band is
the numerical budget and nothing else** — which is exactly what makes it a discretisation claim.

**§2h.4's five conditions, declared before compute as that clause requires:**

1. **Reference is the exact solution of the same continuum model.** **MET** — verified at source
   in §3.2, with the file, function and line cited. Uniform h and U make `ddt` and `div` vanish
   identically, so δ_N solves the full PDE, not a reduction of it. Model-form error is **zero by
   construction**, which is what §2h.4 calls the load-bearing condition. Preserved by the
   `forces ()` and `Cf 0` declarations of §3.3 — adding either term would break this condition,
   which is why both are frozen here.
2. **Iterative error separately gated by rule 5 limb (1), one-way.** **MET** — §5.2's plateau
   criterion, frozen before compute, applied one-way: not plateaued → `NOT A RESULT`, and no
   comparator path converts that to a `PASS`.
3. **Round-off stated with its magnitude and shown negligible against the band.** **MET** —
   §5.3: 7.0e-14 relative, ratio 1.0e-11 to the 0.700 % band. A number, not an assurance.
4. **The limb's wording makes no continuum claim.** **MET.** Limb B's registered sentence, and
   the only sentence the record may carry for it, is:
   > *"The combined discretisation, iterative and inlet-relaxation error in δ_mon is below
   > 0.700 % at every level run."*
   It is **not** *"the solution is correct to 0.700 %"*, and it makes no statement about nature.
5. **The claim is bounded by the levels actually run.** **MET** — the claim is asserted for L1,
   L2 and L3 **only**. Nothing is claimed about finer meshes; that is what a triple is for and
   this limb deliberately does not extend past its levels.

### §6.3 Control C1 — exact-solution retention (and it can fail)

A separate run at L2 with the inlet set **exactly** at equilibrium (h_in = δ_N,
U_in = U_eq = 0.6944 m/s). The exact solution is then attained at the boundary, so the solver
must **retain** it across the whole plate.

**Requirement:** max over the plate of |h(x,y) − δ_N|/δ_N **< 0.05 %** at `endTime`.

**This is the cleanest possible test of §6.2 condition 1 and it is genuinely falsifiable** — if
§3.2's source reading is wrong in any respect (the friction closure, the h₀ treatment, the
gravity projection, an unnoticed active force term), the film will **drift off** the state we
predicted it must hold, and it will do so visibly. C1 failing refutes Limb B outright. Its null
result carries its own plant, P2 (§5.4).

### §6.4 Bracket B2 — the inlet-relaxation bound (channel E, measured not assumed)

L2 run at h_in = 0.70 δ_N against the nominal L2 at h_in = 1.30 δ_N, **same Γ**.

**Requirement:** |δ_mon(B2) − δ_mon(L2 nominal)| / δ_N **≤ 0.200 %** = channel E's allowance.

Exceeding it means the film is not relaxed at the monitor: **channel E is not widened** — the
finding is reported and the monitor question is reopened as an R2 (§7.2).

### §6.5 §18 — the independent path, and what the Nusselt solution is NOT

**Limb A's reference is printed in the manual (0.555 mm), so §18 does not fire on it.**

**Limb B's reference δ_N is lab-generated, so §18 fires and is answered here, in the frozen
bytes, before compute.** The independent path is **§18.2 form (a), the strongest form**: closed-form
algebra that a second party can re-derive from the manual's own stated inputs without sight of
this derivation. The check is fully specified so it can be executed independently:

> From the printed 76.2 kg/m²·s, 5 mm, 417 and 6.305746 m/s²: Γ = 76.2 × 0.005;
> μ = Γ/417; ρ from a standard water correlation at the temperature implied by μ;
> δ_N = (3μΓ/(ρ²·g·sinθ))^(1/3).

**The corroboration §18 asks for already exists and is unusually strong:** δ_N reproduces
**Fluent's independently-computed 0.5497 mm to 0.075 %** — a different code, a different vendor,
a different discretisation, arriving at the same number. Per §18.2 form (b)/(c) that is
independent of *this lab* entirely.

**⚠ THE SEPARATION THE BRIEF DEMANDS, STATED SO IT CANNOT BE BLURRED.**

- **The manual's 0.555 mm is the GATE'S REFERENCE. It is EXPERIMENTAL. It caps Limb A at
  `GATE REACHED`.**
- **δ_N = 0.5501 mm is NOT a substitute for it and never appears in Limb A.** It is (i) a
  **cross-check on our own setup**, and (ii) the reference of the **separate** code-verification
  Limb B.
- **δ_N is NOT independent of our own solver's converged answer** — §3.2 proves it is that
  solver's exact steady solution. **Agreement in Limb B therefore certifies our numerics, and
  says nothing whatever about nature.** Reading Limb B as physical agreement would be exactly
  §18.3's worst failure mode: converting an instrument check into a credential.

---

## §7. VERDICT LOGIC, AND WHAT HAPPENS IF IT FAILS

### §7.1 The label, in the fixed vocabulary only (`CLAUDE.md` rule 1)

Evaluated in this order; the first that fires wins.

1. Strict completion (§5.5) fails on any clause → comparator **exit 2**, **`NOT A RESULT`**.
2. Plant P1 or P2 (§5.4) does not fire → comparator **exit 2**, **`NOT A RESULT`**.
3. Any level not plateaued (§5.2), or the §5.1 station check fails → **`NOT A RESULT`**.
4. Triple not `CONVERGING` (§5.6) → **`NOT A RESULT`**, value and both triples and orders printed.
5. Otherwise, both limbs graded, GCI printed:
   - **Limb A**: e_A ≤ 2.72 % → **`GATE REACHED`** (its ceiling, §3.4); else **`GATE FAIL`**.
   - **Limb B**: e_B ≤ 0.700 %, **and** C1 and B2 both met → **`PASS`**; else **`GATE FAIL`**.

**The gate can only turn a `PASS`/`GATE REACHED` INTO `NOT A RESULT`, never the reverse**
(rule 5). The case's registered ceiling is **`GATE REACHED` on Limb A and `PASS` on Limb B.**

### §7.2 If a limb fails — worked, fixed, solutioned; the gate is never widened

Sanaa's 2026-09-04 standing order with its stated boundary. **No band, threshold, allowance or
label in this document may be changed to admit a result.** The repair order is:

1. **The §2.4 geometric reading** — the first thing re-examined, since it is the one declared
   inference in the input chain. A different reading is a **different case** and gets its own
   registration and its own freeze, never an amendment to this one.
2. **Setup defects** — the `Cf`/`forces`/`h₀` declarations, the faMesh boundary mapping, the
   inlet Γ.
3. **Mesh** — if GCI > 0.500 %, **refine** (add L4 at r = 2); do not widen channel D.
4. **Monitor development** — if B2 or the station check fails, extend the plate or move the
   monitor downstream **as a new registration**, not as an edit here.
5. **The thin-film model itself** — if C1 holds (so our numerics are sound) but Limb A still
   fails outside the band, the residual is **measured** model-form error, i.e. the depth-averaged
   model cannot represent this film. That is a **measured, persistent `GATE FAIL`** and it goes
   to Sanaa's desk with the evidence. It is **not** laundered into a pass, and the VOF R2 path
   (§3.5) is then registered separately.

### §7.3 Amendment rule

Before first compute, amendments are legal and **must state the condition and how it was
checked** — naming the run directory that does not exist (§0.1). **After first compute the gate
is closed:** dated addenda only, which may not alter a gate, threshold, cap or label, with
originals struck and never rewritten (`CLAUDE.md` rule 2, rule 6).

---

## §8. COST (`CLAUDE.md` rule 12; `ANSYS_VERIFICATION_CHARTER` §26, §27)

### §8.1 The method, shown

Unit rate: **2.0e-6 core-s per cell per time step** for `pimpleFoam` PISO with two pressure
correctors, **plus 20 % for the finite-area film solve**. Time step from the **film** surface
Courant number at `maxCo 0.5` with U_eq = 0.6944 m/s (the gas is quiescent and does not
constrain it). `endTime` 10.0 s.

| run | cells | Δt [s] | steps | **core-min** |
|---|---|---|---|---|
| L1 (nominal, h_in = 1.30 δ_N) | 8 192 | 5.63e-03 | 1 778 | **0.58** |
| L2 (nominal) | 65 536 | 2.81e-03 | 3 555 | **9.32** |
| L3 (nominal) | 524 288 | 1.41e-03 | 7 111 | **149.12** |
| B2 bracket (L2 geometry, h_in = 0.70 δ_N) | 65 536 | 2.81e-03 | 3 555 | **9.32** |
| C1 retention control (L2 geometry, h_in = δ_N) | 65 536 | 2.81e-03 | 3 555 | **9.32** |
| | | | **METHOD TOTAL** | **177.7** |

### §8.2 What is filed, and the §26.2/§27 trap it is filed to avoid

| | core-min |
|---|---|
| Method total | 177.7 |
| **FILED** | **360** |
| **ratio filed / method** | **2.03** |
| **CAP** | **800** (2.22× filed, **4.50× method**) |

**⚠ The cap is set BELOW the mechanical 3× of the filed figure, deliberately.** 3 × 360 = 1 080
is **6.08 × the method total**, which is loose on a box other teams queue behind. The cap's only
job is to survive a miss in the one genuinely uncertain input — the assumed 2.0e-6
core-s/cell/step rate — so it is sized directly against that:

| cap [core-min] | × filed | × method | rate miss survived |
|---|---|---|---|
| 720 | 2.00 | 4.05 | 4.0× |
| **800** | **2.22** | **4.50** | **4.5×** |
| 1 080 | 3.00 | 6.08 | 6.1× |

**800 is recommended and is what the comparator carries.** A 4.5× miss on a
standard-order PISO rate would be extraordinary, and §26.2's failure direction is still
respected: 800 is 4.5 × the method, so an under-estimate cannot strangle the run at the end.
**The supervisor rules at the freeze; if 800 is judged too tight, raising it is a pre-compute
amendment under §7.3 and costs nothing.**

**Filed ABOVE its own method, deliberately, and the reason is the clause.** §26.2/§27 record that
the ~3× cap rule makes the estimate load-bearing **in the direction that kills runs rather than
overspending them**: a cap set at 3× an *under-filed* estimate does not overspend — it
**strangles its own run at the end, after all the compute is already spent.** The dominant
uncertainty here is the **2.0e-6 core-s/cell/step rate, which is ASSUMED and has not been
measured on this box** for `pimpleFoam` with a coupled finite-area region; it could plausibly be
2–3× worse. Filing at 2.03× the method carries that. **The cap is then sized against the METHOD
total, not mechanically against the filed figure** — 800 core-min is **4.50× the method**, which
is the number that decides whether a rate miss strangles the run. Stated explicitly so no
successor re-derives the cap from the wrong base in either direction: it is neither 3× the method
(533, too tight — a 3× rate miss would kill it) nor 3× the filed figure (1 080, too loose on a
shared box).

**An overrun of 800 core-min STOPS THE RUN** (rule 12). It does not get a new budget.

### §8.3 Dollars — DERIVED, never measured

At the owner-stated **$0.0513/core-h** (c7a.4xlarge; Sanaa 2026-08-21/22, corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`):

- filed 360 core-min = 6.0 core-h → **$0.31 derived**
- cap 800 core-min = 13.33 core-h → **$0.68 derived**

`cost_basis`: **derived from an owner-stated rate, NOT measured.** This box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER` §5). Well inside the $25 pre-authorisation; CPU only, no GPU,
so nothing here touches the separate GPU regime.

### §8.4 Calibration at completion (rule 12, §5.7)

At completion the actual core-minutes from the logs are compared against the **360** filed here;
the row states the **ratio actual/predicted**, attributes the gap (contention, waste,
misprediction — **waste named separately, never absorbed into the ratio**), and is appended to
`docs/COST_CALIBRATION.md` under its append rules and the rule-10 private-index protocol.
**A completion report without that row is incomplete.** The assumed rate of §8.1 is the specific
thing this calibration should correct for the next film case.

---

## §9. WHAT THIS REGISTRATION DOES NOT KNOW — stated plainly

1. **Roy & Jain (1989) is not on this box** (§1). Its Reynolds convention, its water
   temperature, its monitor station and its experimental uncertainty are **unknown to this lab
   from the source**. §2.2's convention is inferred from the manual's own arithmetic; §4's
   channel A is a **quoted-precision floor, not the experiment's uncertainty**.
2. **The water temperature is inferred (≈ 23.9 °C), never printed.** §4 channel B carries it.
3. **The monitor's streamwise station is a declared reading** (§5.1), tested by the station check
   but not known from the manual.
4. **The §2.4 injection geometry is a declared reading.** It is strongly corroborated
   (§2.3: 0.075 % against Fluent) but it is an inference, and §7.2 puts it first in the repair
   order.
5. **The 2.0e-6 core-s/cell/step rate is assumed, not measured** on this box for this solver
   combination (§8.2).
6. **Model-form error is unbounded** by anything this lab owns (§4.1 channel C). That is the
   ground of Limb A's cap and it is not quantified anywhere in this document.

---

## §10. FREEZE CHECKLIST — for the supervisor's §3 check 4

- [ ] **No open gate question** (§11.2): every gate, band, threshold, cap, level, ceiling and
      label in this document is a **number or a fixed label**. §3.4's `DIFFERENT` ruling and the
      resulting `GATE REACHED` cap are **stated here, not deferred**. Nothing reads "flagged for
      the supervisor".
- [ ] §2b condition named and checked: `verification/runs/ansys_verification/VMFL072/` **does not
      exist** (§0.1).
- [ ] `compare_vmfl072.py` committed in the **same commit** as this file; its sha recorded; the
      grading path fixed at that commit.
- [ ] Prereg sha recorded before the first solver launch.
- [ ] Queue entry filed and committed (§11.4) — the queue carries the plan, not the agent.
- [ ] **After the freeze:** Clause B pre-flight smoke, run in the **launcher's own environment**
      (§14.3 as sharpened by §15.1 — not `env -i`, not a hand-sourced shell).

**This draft is untracked. Committing it IS the freeze. No solver may launch before that commit
exists and is named in the launch record.**
