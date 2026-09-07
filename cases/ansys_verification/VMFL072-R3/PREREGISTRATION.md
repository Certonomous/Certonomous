# VMFL072-R3 — PRE-REGISTRATION (DRAFT, NOT YET FROZEN)

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, VMFL072: Liquid
Water Flow Over a Flat Plate Under the Influence of Gravity** (pp. 211–212),
reproduced in this lab's own solver as a pre-registered lab verdict.

**This document SUCCEEDS VMFL072-R2, frozen at `f5c81c2f2febc7f8a267af1d28631af8f9205d89`
and landed `NOT A RESULT` (validation register #58, 2026-09-04).** R2's finest
level **L3 dewetted and died** — `pimpleFoam` `rc = 136` (SIGFPE) at
`Time = 6.605 / 10.0`, the stack ending in `DILUPreconditioner::calcReciprocalD`
← `PBiCGStab::scalarSolve` ← `kinematicThinFilm::evolveRegion()`. The last
written film field carried `h_min = 1.000000e-07 m` — **exactly the `h₀` floor**
— and `h_max = 5.275373e-03 m` (9.6 × δ_N): **the film dewetted**, and a
vanishing/poisoned diagonal killed the finite-area linear solve. R2's triage is
adopted here, not re-litigated; **R3 is the fix-until-runs successor Sanaa's
directive requires** ("if it's the model change the model, if it's the numerics
change the numerics"). **The gate, the bands, `T`, the exactness-gate design and
the Limb A/B structure of R2 are UNCHANGED. The single deliberate change is a
precursor-film regularization (`§3.8`), and it preserves the L-487
anti-circularity at full strength.**

R2 is **not edited and not reverted**; it stands in history. Everything inherited
here has been re-checked at source, and the one thing that moves — the Limb B
reference δ_N\* — moves **because and only because** h₀ moved, and it is
recomputed to the solver's own new exact discrete state so Limb B stays exact and
non-circular (`§2.4`).

---

## §0. THE FREEZE CLAIM — WHAT THIS IS FROZEN *BEFORE*

### §0.1 The condition, named and CHECKED, not asserted

`CLAUDE.md` rule 2 and charter `§7.3` require the pre-compute condition to be
**named and checked**. Checked 2026-09-07, by name:

- **`verification/runs/ansys_verification/VMFL072-R3/` DOES NOT EXIST.** Checked
  by name, and by `find verification/runs -name 'VMFL072-R3*'` returning nothing.
  (R2's run root `verification/runs/ansys_verification/VMFL072-R2/` exists and is
  untouched by this registration.)
- **No solver has been run at any R3 level to any endTime.** No value of δ_mon at
  the monitor has been read by anyone under this registration, at any level.
- **No grading artifact exists.** `compare_vmfl072_r3.py` has been run **only**
  `--selftest` (on data the selftest fabricates itself), never against solver
  output.

So the freeze claim holds in all three limbs: **frozen before the run, before the
data, and before the reading.**

### §0.2 ⚠ WHAT *HAS* BEEN RUN, DECLARED UNDER `§20.3` RATHER THAN LEFT SILENT

**NOTHING has been run for R3.** No smoke, no probe, no partial solve. `§20.3`
requires any pre-freeze run to be declared with every revealed quantity named;
there is nothing to declare because nothing was run. The interface evidence R3
relies on (`§3.5`) is R2's disk evidence, produced under R2's own `§20.3`
declaration, and it holds byte-for-byte because **the remedy changes no field
name** (`§3.8`). δ_mon is unknown to this lab at every level.

---

## §1. THE REFERENCE, AS THE MANUAL STATES IT

Transcribed from pp. 211–212, character for character where it is a number
(title-page verified against the PDF, `CLAUDE.md` rule 15; the sidecar
`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`
lines 5493–5555).

| | |
|---|---|
| **Reference** | Roy, R.P. & Jain, S. (1989). *A study of thin water film flow down an inclined plate without and with countercurrent air flow.* Experiments in Fluids, (7) 318–328. **NOT ON THIS BOX** (`§10` item 1). |
| **Physics/Models** | Eulerian Wall Film |
| **Test case** | "A water film Reynolds number of 417 and a plate inclination angle of 40° without counter current airflow… The film is introduced as a mass flux boundary on the wall patch injection. **Film thickness is calculated at a downstream location wall-monitor.**" |
| **Domain** | 500 mm × 100 mm × 100 mm; injection width 5 mm; **wall-monitor width 50 mm** |
| **Boundary conditions** | Mass flux of water-liquid = **76.2 kg/m²·s**; gx = **6.305746 m/s²**, gy = 0, gz = **−7.514896 m/s²** |
| **Assumptions** | "Air flow is zero, and the film flow is laminar." |
| **Table .72.1** | Film Thickness (mm): **Target 0.555**, Ansys Fluent 0.5497, Ratio 0.99 |

**0.555 mm is EXPERIMENTAL** — Roy & Jain's measurement of a real water film, not
the exact solution of any model. `§4` caps Limb A for that reason. The manual
gives the monitor's WIDTH and never its STREAMWISE STATION (`§10` item 3), which
is what makes `§6.2`'s station a **declared reading**.

---

## §2. THE PROPERTY CLOSURE, AND THE ONE THING THE REMEDY MOVES

### §2.1 Γ, μ, ρ — carried forward from R2 unchanged

| symbol | value | provenance |
|---|---|---|
| **Γ** | **0.381000 kg/m/s** | 76.2 kg/m²·s × 0.005 m — the manual's two printed inputs |
| **μ** | **9.136691e-04 Pa·s** | Γ/Re with Re = 417 |
| **ρ** | **997.4 kg/m³** | water at ≈ 23.9 °C — **inferred, never printed** |
| **g·sinθ** | **6.305746 m/s²** | printed (gx); √(6.305746² + 7.514896²) = 9.80665, atan = 40.0° |
| **ν = μ/ρ** | **9.160508322e-07 m²/s** | |
| **q = Γ/ρ** | **3.819931823e-04 m²/s** | volumetric flux per unit width |

None of these changes in R3. The remedy (`§3.8`) is a change to the film model's
**precursor thickness h₀**, not to any fluid property.

### §2.2 The Nusselt thickness (context, and NOT Limb B's reference)

δ_N = (3μΓ/(ρ²·g sinθ))^(1/3) = **5.501147914e-04 m** — the h₀-free Nusselt
state. It is **−0.88 % from the manual's 0.555 mm and +0.075 % from Fluent's
0.5497 mm**. **δ_N IS NOT LIMB B'S REFERENCE** (`§2.4`); it is context only, and
the comparator carries it as `D_NUSSELT`, never as a gate.

### §2.3 The relaxation length (carried from R2, unchanged)

In a constant-flux film `h = q/U`, so h and U are coupled and the linearised
restoring rate is **9ν·U_e/q** (nine, not three — the gravity term restores as
well as the friction term). Hence

> **L = q²/(9·ν·U_e) = 2.54871e-02 m = 25.4887 mm** (evaluated at U_e = U_eq).

The monitor at x = 450 mm is **17.7 relaxation lengths** downstream — the inlet
perturbation decays far below `T` before it is read. (R3's U_eq differs from R2's
by 0.6 %, moving L by the same 0.6 %; the monitor is >17 relaxation lengths
downstream either way. This is context; no threshold is derived from L, `§6.3`.)

### §2.4 ⚠ THE ONE MOVE THE REMEDY FORCES — LIMB B'S REFERENCE IS δ_N\*(h₀ = 1e-5)

`liquidFilmBase.C:74` reads `h0` from the film dictionary (default 1e-7). R3
**sets it to 1e-5 m** (`§3.8`). `filmTurbulenceModel.C:157` gives the friction
coefficient `Cw = 3μ/((h + h₀)ρ)`, so the state the solver admits **exactly**
satisfies

```
g_s·h = 3ν·U/(h + h₀) ,  U = q/h   ⟹   h²(h + h₀) = 3νq/g_s = δ_N³ = 1.664792e-10
```

> **With h₀ = 1e-5 m: δ_N\* = 5.468015742732e-04 m** (Newton-solved), which is
> **−0.602277 %** from δ_N.

**δ_N\* is Limb B's reference, in `§5.2` and in control C1 (`§6.4`), exactly as in
R2 — only its value moves.** Because both our run and δ_N\* carry the *same* h₀,
the h₀ shift **cancels identically** in Limb B: it is the solver's own exact
discrete state, so `e_B ≈ 0` by construction regardless of h₀'s value (`§6.9`).
The **only** place the h₀ shift is visible is Limb A (against the experiment),
where it moves the prediction from 0.886 % to 1.477 % — inside the 2.12 % band
(`§5.3`). Limb A keeps the manual's 0.555 mm.

**This is the same design R2 used** — δ_N\* defined as the solver's own exact
state — applied at the new h₀. R2 §2.4 chose δ_N\* precisely so that a change in
h₀ leaves Limb B exact; R3 exercises that property.

### §2.5 The registered closure, complete

| symbol | value |
|---|---|
| **h₀ (precursor, the R3 remedy)** | **1.0e-05 m** (R2 used 1e-7) |
| δ_N\* (Limb B reference) | **5.468015742732e-04 m** |
| δ_N (context only) | 5.501147914e-04 m |
| U_eq = q/δ_N\* | **0.698595615 m/s** |
| relaxation length L | **2.5487e-02 m** (context) |

---

## §3. THE PHYSICS PATH — MEASURED, WITH PROVING PATHS

### §3.1 What this box has

OpenFOAM **v2606** at `/usr/lib/openfoam/openfoam2606`, build
`linux64GccDPInt32Opt` (double precision, ε = 2.22e-16). No Ansys solver of any
kind (charter §2). The shipped
`tutorials/incompressible/pimpleFoam/laminar/inclinedPlaneFilm` is VMFL072's
construction at a different angle and is this case's working template.

### §3.2 `quadraticProfile` IS THE NUSSELT BALANCE, EXACTLY — and it stays exact under the remedy

`kinematicThinFilm.C:55–66` forms `gs = g − ns(ns·g)` and solves
`fam::ddt(h_, U) + fam::div(phi2s_, U) == gs*h_ + turbulence_->Su(U) + …`;
`laminar.C:85` gives `Su(U) = −fam::Sp(Cw, U) + Cw·Uw` with `Uw = 0`;
`filmTurbulenceModel.C:157` case `mquadraticProfile`: `Cw = 3μ/((h + h₀)ρ)`.

**A spatially uniform (h, U) with `g_s·h = Cw·U` makes every gradient term vanish
identically on ANY MESH — the Nusselt state is an EXACT DISCRETE SOLUTION AT
EVERY REFINEMENT LEVEL.** Raising h₀ does not touch this property: it only shifts
which uniform h satisfies the balance, from δ_N\*(1e-7) to δ_N\*(1e-5) (`§2.4`),
and a uniform field still zeroes `div`, `grad` and `laplacian` at every level.
This is the case's central verification content (`§6.6`) and why `§7` declines a
Roache triple.

Two source facts, re-verified for the new h₀:

- `Cw.clamp_max(5000.0)` (`filmTurbulenceModel.C:158`) binds only below
  `h + h₀ = 3μ/(5000ρ) = 5.496e-10 m`. With **h₀ = 1e-5 m**, `h + h₀ ≥ 1e-5 ≫
  5.496e-10` always, so the clamp **can never fire** and the Cw closure is exact
  as stated — *more* robustly than at R2's h₀.
- `gs = g − ns(ns·g)` carries the plate normal twice, so `|gs|` is
  sign-independent; the axis convention cannot silently move δ.

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
h0              1e-5;      <-- THE R3 REMEDY (§3.8). R2 used 1e-7.
deltaWet        1e-5;      (== h0 in R3)
```

- **`Cf 0`** (air flow is zero), **`forces ()`** (no contact-angle/rivulet
  term), **`friction quadraticProfile`** (the laminar closure, not the tutorial's
  empirical `ManningStrickler`) — all unchanged from R2, all load-bearing (R2
  §3.3). Mass enters at the finite-area inlet boundary as prescribed `hf_film`
  and `Uf_film` with ρ·h_in·U_in = Γ.
- **SERIAL** — a serial run writes the 200 time directories the comparator reads;
  the failure mode of reconstructing to two directories is designed out (R2 §3.3).

**Geometry and gravity, as printed.** Plate 500 mm (x, downslope) × 100 mm
(y, span); gas box 100 mm in z. `constant/g = (6.305746 0 −7.514896)`.

### §3.4 ⚠ THE CIRCULARITY, AND HOW IT IS DEFEATED — UNCHANGED, AT FULL STRENGTH

Prescribing h at the inlet risks prescribing the gate quantity. It is defeated by
**deliberately setting the inlet off equilibrium** and reading the monitor far
downstream, so the monitor value is a *solved relaxation*, never a boundary
condition (L-487):

```
nominal (L1 L2 L3):  h_in = 1.30 δ_N* = 7.1084204656e-04 m,  U_in = 0.537381243 m/s
bracket  B2       :  h_in = 0.70 δ_N* = 3.8276110199e-04 m,  U_in = 0.997993736 m/s
control  C1       :  h_in = 1.00 δ_N* = 5.4680157427e-04 m,  U_in = 0.698595615 m/s
```

All three carry the **identical** Γ: ρ·h_in·U_in = 0.381000000 kg/m/s exactly.

> **⚠ THE 1.30 δ_N\* OVER-THICK INLET IS UNCHANGED FROM R2, AND THAT IS
> DELIBERATE.** R2's L3 dewetted *because* of this over-thick inlet (register
> #58: a film thicker than equilibrium accelerates, thins, and at fine mesh
> overshoots toward dewetting; B2, the same 256×64 mesh with the *thinner* 0.70
> δ_N\* inlet, completed cleanly). **The over-thick inlet is the anti-circularity
> measure itself, and R2 correctly refused to retract it** — dropping it would
> restore the circularity the perturbation exists to defeat. R3 keeps the full
> 30 % perturbation and instead makes the *model* robust to the dewetting it
> provokes (`§3.8`). The anti-circularity is therefore preserved at **full
> strength**: two inlets 60 % apart in h (B2 at 0.70, nominal at 1.30) must still
> converge to the same monitor value (`§6.5`), and that convergence — not the
> inlet — is what a Limb-B PASS would rest on.

### §3.5 ⚠ `§39.5` — EVERY PATH THE COMPARATOR READS IS A PATH THE SOLVER WRITES — UNCHANGED FROM R2

**This is the rule that struck the original VMFL072** (charter §39), whose
comparator read `constant/film/Cf_film` and `constant/film/magSf_film` — names in
**zero** code paths. R2 closed it by BUILDING AND RUNNING the case and reading the
written directory. **R3 changes NO field name** — the remedy is a scalar
dictionary value (`h0`) — so R2's disk evidence holds byte-for-byte:

| path the comparator reads | the utility that writes it |
|---|---|
| `constant/polyMesh/{points,faces}` | `blockMesh` |
| `constant/finite-area/faMesh/faceLabels` | `makeFaMesh` |
| `<t>/finite-area/hf_film` | `pimpleFoam` + `velocityFilmShell` |
| `log.checkFaMesh` "Face area: min = … max = …" | `checkFaMesh` |
| `log.pimpleFoam` "End", "ExecutionTime" | `pimpleFoam` |
| `RC.txt` | the driver's detached wrapper |

R2 verified on disk (register #58: four of five levels — L1, L2, B2, C1 — wrote
`<t>/finite-area/hf_film` to endTime, and L3 wrote it to `Time = 6.6` before the
SIGFPE) that the written time directory contains exactly `U p phi` +
`finite-area/{hf_film, Uf_film, pf_film, phif_film, phi2s_film, rhof, Tf_film}` +
`uniform/…`, and `constant/finite-area/faMesh/` exactly `{faceLabels, faBoundary}`
— **no `Cf_film`, no `magSf_film` anywhere.** Face centres and areas are COMPUTED
from `points`+`faces`+`faceLabels` and cross-checked against `checkFaMesh`'s own
printed min/max area (C-16). The faMesh face counts / areas at each level are
mesh-only quantities, independent of h₀, and are unchanged: L1 1024 faces
@ 4.8828125e-05 m², L2 4096 @ 1.220703125e-05, L3 16384 @ 3.0517578125e-06, each
Σ magSf = 0.05 m² exactly; monitor faces 24 / 80 / 352.

> **A `--selftest` proves the comparator's LOGIC and NOTHING about its INTERFACE
> (§39.5).** The interface evidence is this table and R2's disk build, not the
> selftest — and it transfers to R3 **only because the remedy touches no field
> name.** `§3.8` states this is precisely why the precursor remedy was chosen
> over a framework change.

### §3.6 NZ = 1, a measurement with a live control — unchanged

The primary (gas) region is one cell thick in z. With `Cf 0` the primary-region
coupling is identically zero (`filmTurbulenceModel.C:252`) and the gas Courant
number is measured at exactly 0, so the mapped primary pressure is uniform. R2
measured (100 steps, L1, NZ ∈ {1, 8}): `hf_film` bit-identical on all 1024 faces,
`max|Δh| = 0`, on a field of range 5.633e-04 m, and the same reader saw a planted
+1.234e-09 m. h₀ does not enter this argument. NZ = 1 is carried forward.

### §3.7 `§12.2` — THE SAMENESS RULING, in its four required parts — unchanged

1. **The continuum model the solver discretises.** Depth-averaged (lubrication)
   thin-film equations on a surface, incompressible, Newtonian, laminar,
   parabolic through-thickness, zero gas shear (verified at source, `§3.2`).
2. **The model the reference is the exact solution of.** **None** — 0.555 mm is an
   experimental measurement of a real water film (full 3-D Navier–Stokes with a
   deformable, wavy free surface at 4Γ/μ = 1668).
3. **Same model?** **`DIFFERENT`.** The residual between a smooth depth-averaged
   film and a real wavy film is model-form error, which no grid triple and no
   exactness gate bounds.
4. **Consequence.** **`GATE REACHED` from the outset** for Limb A, per `§12.2` and
   `VERIFICATION_CHARTER` §2h.8.1 — an experimental reference caps at
   `GATE REACHED`, however exact its own algebra.

### §3.8 ⚠ THE R3 REMEDY — A PRECURSOR-FILM REGULARIZATION OF THE DEWETTING SINGULARITY

**The finding R3 fixes** (register #58, triaged and adopted): R2's L3 (256×64,
inlet 1.30 δ_N\*) reached `h = 1e-7 m` (the h₀ floor) and died in
`DILUPreconditioner::calcReciprocalD` (diagonal inversion) with a SIGFPE at
`t = 6.605 s`. Courant numbers were 2.3e-17…1.3e-05 throughout — **not** a CFL
blow-up in the gas. B2 (same mesh, thinner 0.70 δ_N\* inlet) completed cleanly.
**The over-thick inlet drives a thinning overshoot that, at the finest mesh where
numerical dissipation no longer smears it, dewets to the floor.** This is
numerics/model, not a capability gap; the over-thick inlet is the L-487
anti-circularity measure and must not be retracted (`§3.4`).

**THE MECHANISM AT SOURCE, and why raising h₀ removes it.** h₀ is the film's own
**precursor-film** thickness, and it appears at two sites:

1. `kinematicThinFilm.C:159` — `h_ = max(h_, h0_)`: a **hard post-solve floor**.
   A film that dewets is clamped to h₀. At h₀ = 1e-7 the clamp sits at a
   numerically singular thickness; at h₀ = 1e-5 it sits at a well-conditioned one.
2. `filmTurbulenceModel.C:157` — `Cw = 3μ/((h + h₀)ρ)`, the **friction
   denominator**. `Cw.clamp_max(5000)` caps Cw *above* but **does not catch a
   negative `(h + h₀)`**. When the steepening dewetting wave drives h transiently
   below −h₀, `(h + h₀)` crosses zero, `Cw → ±∞`, and the `−Sp(Cw, U)` term
   poisons the matrix diagonal — precisely the `calcReciprocalD` failure R2 saw.
   **R2's h₀ = 1e-7 gave only a 1e-7 m guard against that undershoot, and it was
   breached. h₀ = 1e-5 is a 100× larger guard,** and drops the friction stiffness
   at the floor by 100× (`Cw` at `h = h₀`: **13.74 s⁻¹ → 0.137 s⁻¹**).

**This is the precursor-film regularization the thin-film literature prescribes
for exactly this dewetting/contact-line singularity.** Wu, Long, Wang & Gao,
*Macroscopic simulations of thin film wetting/dewetting using a precursor film
model*, arXiv:2609.01444 (2026-09-01), title-page verified per rule 15 and filed
at `docs/papers/thin_film_flows/wu_2026_precursor_film_dewetting.pdf` (+ `.txt`
sidecar): "the precursor film model assumes the existence of an ultra-thin liquid
film … surrounding the macroscopic bulk liquid," and a **"relatively thick
precursor film"** can be used **"while preserving the macroscopic flow
dynamics."** That is exactly R3's move: a **mesoscopic** precursor (h₀ = 1e-5 m,
100× the physical R2 value) that de-stiffens the numerics while leaving the
fully-wet macroscopic monitor uncorrupted beyond the exactly-computable δ_N\*
shift.

**Why (b) and not (a) an alternate film model or (c) a VOF re-formulation** — the
two other remedies evaluated:

- **(a) `kinematicSingleLayer` (a different regional-film framework).** The
  overshoot-to-dewetting is intrinsic to depth-averaged film models regardless of
  framework, so a framework change does not address the mechanism; it would
  require a different solver (not `pimpleFoam`) and **new field names**, re-opening
  the §39.5 trap that struck this case once. **Rejected** — expensive, off-target,
  interface-risky.
- **(c) VOF (interFoam-family), resolving the 0.55 mm film directly.** Requires
  many cells across a 0.55 mm film in a 500 mm domain (enormous mesh) and captures
  a wavy free surface — a different, far costlier verification problem — and it
  **destroys the case's exactness content**: the discretisation no longer admits
  the Nusselt state as an exact discrete solution, so Limb B's PASS-capable
  code-verification statement (`§6.9`) and the exactness gate (`§6.6`) collapse.
  **Rejected.**
- **(b) precursor-film regularization via h₀ (SELECTED).** Keeps the solver, the
  framework, every field name (§39.5 avoided by construction), the exactness-gate
  design, and the Limb A/B structure; addresses the measured root cause directly;
  the reference δ_N\* tracks it exactly. It is a **one-scalar dictionary change**
  in `base/0.orig/U`.

**How L-487 anti-circularity is preserved — stated explicitly.** The remedy does
**nothing** to the inlet: h_in stays at 1.30 δ_N\* (nominal) / 0.70 (B2) / 1.00
(C1), off equilibrium, at full 30 % strength. The monitor at x = 450 mm is
**fully wet** (h ≈ δ_N\* = 0.547 mm ≫ h₀ = 0.01 mm), so the `max(h, h₀)` clamp
never binds there and the monitor value remains a **solved relaxation** from an
off-equilibrium inlet, not a boundary condition read back. The precursor binds
only in the thin/dewetted transient region, which is far from the monitor and far
below δ_N\*. **Quantitatively, h₀ = 1e-5 m = 1.818 % of δ_N; the fully-wet
equilibrium it produces is δ_N\* = 0.546802 mm, corrupting Limb A's prediction by
0.591 percentage points (0.886 % → 1.477 %), well inside the 2.12 % band and with
0.65 % margin to the lower band edge** (`§5.3`). The precursor does **not** corrupt
the graded monitor: it shifts the exact discrete state by a known amount that
Limb B's reference absorbs identically and that Limb A carries inside its band.

### §3.9 The magnitude of the precursor — why 1e-5 m, and its honest limit

h₀ = 1e-5 m is chosen as the smallest **decade** step that (i) gives a 100× guard
against the transient undershoot and 100× lower floor-stiffness, and (ii) equals
the existing `deltaWet` wet/dry scale, so the precursor and the wet/dry threshold
are one consistent regularization length; while (iii) keeping h₀/δ_N = 1.82 %,
so Limb A stays inside its band with margin (`§5.3`). A smaller precursor
(5e-6 m) would give more Limb-A margin but only a 50× guard; a larger one would
erode the Limb-A margin. 1e-5 m is the balance.

> **⚠ HONEST LIMIT — THE CURE IS ARGUED FROM SOURCE, NOT MEASURED.** No R3 solve
> has run (`§0`). The claim that h₀ = 1e-5 m carries L3 to endTime rests on: the
> source mechanism above (the singular `(h + h₀)` denominator and the near-zero
> floor are both regularized 100×), and the fact that R2's B2 — the *same 256×64
> mesh* — completed a healthy film cleanly, so the mesh and solver handle a
> well-conditioned film; only the excursion to the floor was fatal, and that
> excursion is what h₀ regularizes. **It is possible the overshoot still reaches
> the floor at 1e-5; if so, the clamp catches it at a well-conditioned thickness
> and the solve proceeds — that is the point of a precursor.** If R3 nonetheless
> fails, `§7.3` states the repair order (and the escalation to Sanaa's desk), and
> **no band, threshold or label is widened to admit a result.**

---

## §4. THE CAP, AND WHOSE IT IS

> **Limb A's ceiling is `GATE REACHED`. THIS CAP BELONGS TO THE REFERENCE, NOT TO
> OUR WORKMANSHIP.** No fix on our side lifts it, and the R3 remedy does not lift
> it — the remedy is about the *run completing*, never about the cap. Reaching
> `GATE REACHED` is Limb A's success.

`§33.2` does not fire: Fluent's 0.5497 mm is code-to-code context (`§2.2`), not
the gate. The gate's reference is the experiment.

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

**The band, channel by channel, the LINEAR (conservative) sum — UNCHANGED from
R2**, because every channel is set by the manual and the instrument, not by h₀:

| ch | source | magnitude | how it was obtained |
|---|---|---|---|
| **A** | reference's quoted precision | **0.090 %** | "0.555" is 3 s.f. → ±0.0005 mm; a FLOOR on the reference's uncertainty, not invented |
| **B** | unstated fluid temperature | **1.926 %** | δ ∝ μ^(1/3) at fixed Γ over 20–25 °C; **91 % of the band, from the manual's silence** |
| **D′** | discretisation | **0.0504 %** | `§6.6`'s exactness gate, `T = 2.7750e-07 m` on δ_N\* |
| **E′** | inlet-relaxation residual | **0.0504 %** | `§6.5`'s bracket, the same `T` |
| | **BAND** | **2.1168 % → registered 2.12 %** | |

**Channel C — model form — is deliberately NOT in the band** (`VERIFICATION_CHARTER`
§2h.8.2); it is the ground of the `GATE REACHED` cap (`§4`).

**The band can fail.** Nothing in the 20–25 °C property range plus the full
numerical allowance places δ outside [0.543234, 0.566766] mm; a result outside it
indicates a setup/mesh/BC/model defect and is not laundered into a pass.

### §5.2 Limb B — CODE VERIFICATION against the exact solution of the same model

```
e_B = | δ_mon − δ_N* | / δ_N*   ≤   0.101 %      (= D′ 0.0504 + E′ 0.0504)
```

**Reference δ_N\* = 5.468015742732e-04 m** (`§2.4`) — the **exact steady solution
of the very PDE the solver discretises, including the solver's own h₀ = 1e-5**.
`PASS`-capable under §2h.8.1. Channels A and B cancel (shared property set);
Limb B's band is the numerical budget and nothing else.

### §5.3 The registered PREDICTION (prediction-first, `CLAUDE.md` rule 2)

> **δ_mon = 0.546802 mm**, to within iterative and inlet-relaxation error.
> **e_A = 1.477194 %** against a 2.12 % band (margin to the lower band edge
> 0.6524 %). **e_B ≈ 1e-6 %** against 0.101 %.

If the run lands materially away from this, **our reading of the installed solver
is refuted**, and that is a finding worth more than a passing row.

---

## §6. HOW THE NUMBER IS READ, AND THE CONTROLS ON THE READER

### §6.1 ONE instrument floor, four uses — UNCHANGED

> **`T = 2.7750e-07 m` = 0.05 % of 0.555 mm = 0.050752 % of δ_N\*.**

Derived from the **gate tolerance** (Limb B's 0.101 %, 2.0× tighter), never from
an observed floor (`§16.2`). It is a number, not `ptp → 0`, so it is satisfiable
against a bounded limit cycle. It is 2.8e8× the reader's ≈1e-15 m file quantum
(`writeFormat ascii; writePrecision 12`) and 2.8e3× the `faSolution` tolerance of
1e-10 on `hf_film`. The four uses (C-10 plateau, C-11 station, C-12 exactness,
C-21 bracket) are one statement — two readings of the same quantity are
indistinguishable at the run's own noise floor.

### §6.2 The reader, its window, and its resolution — UNCHANGED

**Reader:** `cases/ansys_verification/VMFL072-R3/compare_vmfl072_r3.py`, pinned at
`§9.1`, fixed at this document's freeze commit. **Field read:** `hf_film` from the
graded level's `endTime` directory. **Monitor window:** faces with centres in
`x ∈ [0.440, 0.460] m` (50 mm clear of the outlet, 17.7 relaxation lengths clear
of the inlet) AND `y ∈ [0.025, 0.075] m` (the manual's 50 mm width, centred);
`δ_mon = Σ(hf_i·A_i)/Σ(A_i)`. The window is not nested across levels; at x = 450 mm
the drift contributes ≈2.5e-13 m to δ_mon, six orders below `T`, and is left
alone and recorded (fatal only at a *developing* station, `§7.4`). Reader
resolution is held below `T` by the `faSolution` 1e-10 tolerances on `hf_film`
and `Uf_film`.

### §6.3 The station-development check — UNCHANGED

δ_mon is reported over the same ±10 mm × 50 mm window at x = 300, 350, 400, 450,
480 mm on the graded level; **if the spread exceeds `T = 2.7750e-07 m`, the film
is not developed at the monitor and the verdict is `NOT A RESULT`** (the reading
is not quietly relocated). A loose but live, falsifiable guard against a wrong Γ,
friction closure or inlet.

### §6.4 Control C1 — exact-solution retention, and it can fail — UNCHANGED (new δ_N\*)

A run at **L2** with the inlet **exactly at equilibrium** (h_in = δ_N\* =
5.4680157427e-04, U_in = U_eq = 0.698595615) and the initial field uniform at the
same value, so the exact solution is present from t = 0 and the solver must
**retain** it.

> **Requirement: max over the plate of |h − δ_N\*| / δ_N\* < 0.05 % at
> `endTime`.**

If `§3.2`'s source reading is wrong in any respect the film drifts off the state
we predicted, visibly. **C1 failing refutes Limb B outright.** (C1's inlet is at
equilibrium, so C1 never dewets — it is a pure retention test, and it is the arm
least perturbed by the remedy.)

### §6.5 Bracket B2 — the anti-circularity control, AT THE GRADED LEVEL — UNCHANGED

**L3** at h_in = 0.70 δ_N\* against the nominal **L3** at h_in = 1.30 δ_N\*, same
Γ.

> **Requirement: |δ_mon(B2) − δ_mon(L3)| ≤ `T`.**

Two inlets 60 % apart in h converging to the same monitor value is the refutation
of "you told it the answer at the inlet." Exceeding `T` means the film is not
relaxed at the monitor: **channel E′ is not widened** — the finding is reported and
the monitor question reopened as a new registration. **B2 is the arm register #58
proved completes at the finest mesh** (it ran clean under R2 at h₀ = 1e-7), so it
is the least at risk of the dewetting the remedy targets.

### §6.6 ⚠ THE EXACTNESS GATE — UNCHANGED

> **`max` over all pairs of `|δ_mon(Li) − δ_mon(Lj)|` across L1, L2, L3
> `≤ T = 2.7750e-07 m`. One-way: failing it is `NOT A RESULT`.**

Three levels spanning 4× in Δx must be indistinguishable — the falsifiable form
of *the discretisation admits the exact solution at every level*. Stricter than a
`CONVERGING` triple (which permits any monotone difference up to channel D's
0.500 %); this permits **none above 0.0504 %**. Alongside it, four geometry/field
refusals (each against an OpenFOAM-produced number):

| clause | refusal |
|---|---|
| **C-14** | faMesh face count ≠ NX·NY |
| **C-15** | Σ magSf ≠ 0.05 m² to 1e-12 relative |
| **C-16** | computed (min, max) face area ≠ `checkFaMesh`'s own printed pair to 1e-12 relative |
| **C-17** | any face is not a 4-vertex planar parallelogram |

> **⚠ HONEST LIMIT.** The predicted level-to-level differences are far below the
> `faSolution` floor of 1e-10, so the gate is expected to pass by orders of
> magnitude. **Its power is against GROSS level-dependence** (a mesh-dependent BC,
> a level-dependent setup error, a broken reader), **not against fine
> discretisation error**, which is unmeasurable in this quantity by construction.

### §6.7 Admissibility floor — UNCHANGED

The comparator refuses any δ_mon ≤ **1.0e-06 m** — 547× below δ_N\*, a value no
film-producing run returns. This closes the all-zeros hole that no additive plant
on a linear reader can close (`§6.8` limit 2). **Note the precursor h₀ = 1e-5 m is
10× ABOVE this floor**, so even a monitor sitting on the precursor (it does not —
it is fully wet) would not be mistaken for admissible.

### §6.8 The planted controls — UNCHANGED (`CLAUDE.md` rule 3; L-487)

The comparator refuses (exit 2) unless **both** fire, on copies in scratch; graded
fields are never mutated. **P1** (against the area-weighted monitor mean): `P =
+1.234e-05 m` added to a **proper subset by area** of the window (faces with
y < 0.050 m), re-written and re-parsed through the same reader; requires the shift
to equal `P·f` with `f` computed from the geometry, never hard-coded; refuses if
the sub-region is empty or the whole window. **P2** (against the exactness-gate
null): plants into one level and requires the max-over-pairs statistic to take the
analytically-known value **and to have moved** by > 1e-9 m. Two honest limits
carried unchanged: on a uniform mesh the weighted/unweighted means are one
function (the selftest exercises the weighting on a graded-area arm); an additive
plant on a linear reader is field-independent (the all-zeros hole is closed by
admissibility, `§6.7`).

### §6.9 ⚠ LIMB B IS AN EXACT-RETENTION TEST AND IS EXPECTED TO PASS — UNCHANGED

`§3.2` establishes the solver admits δ_N\* as an exact discrete solution, so
`e_B ≈ 0` by construction — the case's verification content, not a weakness. It
can fail in four named ways, each refuting a specific line of `§3.2`: an active
`forces()` term, a different h₀ treatment, a sign in the gravity projection, or a
`phi2s` that is not `hU`. **`§2h.4`'s five conditions** are all MET, declared
before compute (reference is the exact solution of the same model, corrected to
the h₀ = 1e-5 state δ_N\*; iterative error one-way gated; round-off ≈2.5e-11 of the
band; the limb makes no continuum claim; the claim is bounded by L1/L2/L3 only).
The only sentence the record may carry for Limb B: *"The combined iterative and
inlet-relaxation error in δ_mon is below 0.101 % at every level run, and the three
levels are indistinguishable at 0.0504 %."*

### §6.10 Strict completion (`CLAUDE.md` rule 4) — UNCHANGED

The comparator refuses on any of: **C-01** `rc = 0` captured inside the detached
wrapper (this is the clause R2's L3 tripped: `rc = 136`); **C-02** an `End` line;
**C-03** last time == `endTime` = 10.0; **C-04** fields present at `endTime` (`U`,
`p`; `hf_film`, `Uf_film`); **C-05** 200 written time directories; **C-06**
`ExecutionTime` count == the level's step count (2000/4000/8000/12800/4000);
**C-07** age guard — every field at `endTime` newer than `0/U`, which the driver
touches last and asserts.

---

## §7. NO ROACHE TRIPLE IS DECLARED — the statement `CLAUDE.md` rule 5 requires

> **THIS CASE DECLARES NO GRID TRIPLE. IT COMPUTES NO RICHARDSON EXTRAPOLATION,
> NO OBSERVED ORDER AND NO GCI, AND NO ROW OF IT MAY EVER BE READ AS CARRYING
> ONE.** Three levels are run and used **only** for `§6.6`'s exactness (level-
> independence) gate. `§2f.2`'s *"no triple never means no rule 5"* is honoured:
> **rule 5 limb (1) fires in full** (`§6.1`, `§6.10`). Only limb (2), the triple
> classification, is absent, because no triple is declared.

Three reasons, all a-priori and unchanged from R2: (1) the quantity has no
discretisation error to extrapolate — the Nusselt state is exact at every level
(`§3.2`), and the predicted level-to-level residual is below the `faSolution`
floor, so a triple would classify solver noise (`roache()` returns `EXACT` →
`NOT A RESULT`); (2) coarsening changes the decay rate of an already-tiny residual,
never the asymptotic monitor value; (3) a triple bounds discretisation error and
cannot raise Limb A's model-form ceiling (`§4`). **Precedent:**
`cases/ansys_verification/VMFL024/PREREGISTRATION.md` §7.

### §7.1 What this case ESTABLISHES

A `GATE REACHED` credential (the lab's `pimpleFoam` + `kinematicThinFilm` film,
set up from the manual's printed inputs, reproduces 0.555 mm inside a pre-frozen
band); a `PASS`-capable exact-retention code-verification statement at three
levels spanning 4× in Δx; that the monitor value is not a boundary condition
(`§6.5`); that the exact state is retained over the whole plate (`§6.4`); **and
that the precursor-film regularization carries the over-thick-inlet case to
endTime at the finest mesh where R2 dewetted** — the specific thing R3 exists to
show.

### §7.2 What this case DOES NOT establish

No order of accuracy, no GCI, no Richardson extrapolation, for any quantity
(**this sentence must appear in the register row**); nothing about nature (Limb A
capped by its reference); nothing about meshes finer than L3; nothing about the
monitor's true station; nothing about the water temperature (channel B is 91 % of
the band); nothing about Ansys. **And R3 adds one:** nothing about the film's
behaviour at the *physical* precursor scale (h₀ = 1e-7) — R3 deliberately runs a
*mesoscopic* precursor (1e-5), and says only that the macroscopic monitor is
uncorrupted by it (`§3.8`), not that the microscopic dewetting dynamics are
resolved.

### §7.3 If a limb fails — worked, fixed, solutioned; the gate is never widened

**No band, threshold, allowance or label may be changed to admit a result.** The
repair order:

1. **If L3 (or any level) STILL DEWETS AND DIES at h₀ = 1e-5** — the primary R3
   risk (`§3.9`). The measured evidence (last written field, `h_min`, the stack)
   is recorded. Next, in order, each as a **new registration and freeze**, never a
   band change: (a) a larger mesoscopic precursor (h₀ = 2e-5 or 5e-5, re-checking
   Limb A margin — at 5e-5, δ_N\* ≈ 0.539 mm falls **below** the band, so this is
   bounded); (b) the `limitHeight` finite-area faOption to cap the pile-up side
   (OpenFOAM v2606; inactive on the uniform state, so it does not corrupt `§3.2`);
   (c) a gentler inlet perturbation (< 1.30 δ_N\*), which weakens but does not
   abandon the anti-circularity. **If a defensible precursor within the Limb-A
   band cannot carry the run, that is a measured persistent property of the
   depth-averaged film model at this refinement, and it goes to Sanaa's desk with
   its evidence** — it is not laundered into a pass.
2. **The injection geometry reading** (Γ = 76.2 × 0.005) — the one declared input
   inference; a different reading is a different case.
3. **Setup defects** — `Cf`/`forces`/`h₀`/faMesh mapping/inlet Γ.
4. **The exactness gate** — if it fails, the level-dependence is measured and is
   the finding; the gate is not widened and no level dropped.
5. **The thin-film model itself** — if C1 holds but Limb A fails outside the band,
   the residual is measured model-form error, a persistent `GATE FAIL` to Sanaa's
   desk.

### §7.4 What a future developing-region registration must know — carried from R2

A monitor in the *developing* region carries genuine discretisation error and a
non-degenerate triple, but there is no station with both a defensible triple
margin and a defensible δ (peak discriminability ≈7.66×T at x≈27 mm where δ is
9.8 % from 0.555 mm); the number there is set by our own inlet perturbation (a
gate on a free knob); the non-nested window is fatal there; and the `pf_` closure
must be exact. **It gets its own registration and freeze.** R3's mesoscopic
precursor would additionally have to be justified as not corrupting a *developing*
reading — a further reason it is out of scope here.

---

## §8. COST (`CLAUDE.md` rule 12)

### §8.1 The method — from R2's MEASURED completed levels

R3 changes only a scalar dictionary value (h₀); the mesh sizes, step counts and
serial execution are identical to R2, so per-step wall time is essentially R2's
(the linear systems are the same size). The basis is therefore R2's **measured**
gross costs (register #58), with L3 extrapolated from its 66 % partial:

| level | steps | R2 measured core-min | R3 method basis |
|---|---|---|---|
| L1 | 2 000 | 0.3627 | 0.36 |
| L2 | 4 000 | 2.9222 | 2.92 |
| L3 | 8 000 | 14.3138 (died at 66 %) | **≈ 21.7** (14.3138 / 0.66) |
| B2 | 12 800 | 28.9933 | 28.99 |
| C1 | 4 000 | 2.7312 | 2.73 |
| | | | **METHOD TOTAL ≈ 56.7** |

**SERIAL, one rank, so core-minutes == wall minutes and the `timeout` cap is
exact.** **Honest caveat:** the precursor may change the number of PBiCGStab
iterations per step in the thin/dewetted region (the system is better-conditioned
there than R2's, but the dynamics differ), so per-step wall could move within the
cap cushion; the completed-level costs (L1, L2, B2, C1) are unaffected by the
remedy since those films stayed healthy under R2.

### §8.2 What is filed, and the per-level caps

| | core-min |
|---|---|
| Method total | **≈ 56.7** |
| **FILED** | **92** (1.62 × method) |
| **CAP** | **184.5** (3.25 × method) |

**Per-level caps, enforced by `timeout` in the driver (G-08), identical to R2:**

| level | method | **cap** | cap seconds |
|---|---|---|---|
| L1 | 0.36 | **1.5** | 90 |
| L2 | 2.92 | **9** | 540 |
| L3 | 21.7 | **65** | 3 900 |
| B2 | 28.99 | **100** | 6 000 |
| C1 | 2.73 | **9** | 540 |
| | 56.7 | **184.5** | |

**An overrun STOPS THE RUN** (rule 12): `timeout` kills it, the wrapper records
`rc = 124`, and the comparator refuses at C-01. The L3 cap (65 core-min, 3.0× the
extrapolated method) is the cushion against a precursor-driven iteration increase;
if L3 needs more than 65 core-min, the run is stopped, not re-budgeted.

### §8.3 Dollars — DERIVED, never measured

At the owner-stated **$0.0513/core-h** (c7a.4xlarge; Sanaa 2026-08-21/22):
filed 92 core-min = 1.533 core-h → **$0.079 derived**; cap 184.5 core-min =
3.075 core-h → **$0.158 derived**. `cost_basis`: **derived from an owner-stated
rate, NOT measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5). Well inside the $25 pre-authorisation; CPU only.

### §8.4 Calibration at completion (rule 12)

At completion the actual core-minutes from the logs are compared against the **92**
filed here; the row states the ratio actual/predicted, attributes the gap
(contention, waste, misprediction — waste named separately, never absorbed), and
is appended to `docs/COST_CALIBRATION.md` under the rule-10 private-index
protocol. **This closes out R2's open calibration:** R2 could not quote a clean
ratio because L3 died at 66 %; a completed R3 L3 is the first clean measurement of
this quantity, and it should also close out the NZ = 1 film rate for the next case.
A completion report without this row is incomplete.

---

## §9. THE GRADING PATH, THE DRIVER, AND THE FREEZE CHECKLIST

### §9.1 THE COMPARATOR PIN — complete, not deferred

> **COMPARATOR_BLOB = 2fcc0ced1bb99192f25c80b323af161cf25b90ac**

This is `git hash-object cases/ansys_verification/VMFL072-R3/compare_vmfl072_r3.py`,
taken **without committing**, so the pin is stable (writing it here changes *this*
file's blob, not the comparator's). The driver reads it out of this document
(G-03), so there is one source of truth and the check works before the freeze
commit exists as well as after it. At the freeze the comparator and this document
are committed **in the same commit**, and the driver verifies every frozen file
against its blob at that commit (G-02).

`--selftest` result on this blob: **33 passed, 0 failed** under both `python3` and
`python3 -O` — one mutant per completion clause (C-01…C-07), per geometry refusal
(C-14…C-17), the admissibility mutant (C-13), one mutant per verdict conjunct
(C-10, C-11, C-12, C-18, C-19, C-20, C-21), both plants firing, five reader
mutants refused by P1, the degenerate plant set refused, the graded-area arm
separating area from count weighting, and a P2 mutant that reads one level three
times refused. **The selftest prints, as its own banner, that it proves LOGIC and
nothing about INTERFACE** (`§3.5`).

### §9.2 THE DRIVER — `launch_vmfl072_r3.sh`, and its eight guards

A lab driver, not a tutorial `Allrun`: it never `cd`s into the case directory,
never writes into `cases/`, and runs one registered level per invocation into
`verification/runs/ansys_verification/VMFL072-R3/<LEVEL>/`. Guards, in order:
**G-00** every path it reads/executes exists (all frozen files, all case inputs,
`blockMesh makeFaMesh checkFaMesh pimpleFoam setsid timeout python3 git`, the
run-root parent); **G-01** `VMFL072R3_PREREG_SHA` set; **G-03** comparator blob ==
the `§9.1` pin read out of this document (before G-02, needs no commit); **G-02**
the sha is a commit and every frozen file hashes equal to its blob there; **G-04**
run root under `verification/runs/` and not under `cases/`; **G-05** run root does
not already exist; **G-06** no time directory but `0/` after staging; **G-07** the
age guard (`0/U` touched last and asserted); **G-08** `timeout` at the level's cap
with `rc` captured inside the detached wrapper. The driver is byte-identical to
R2's (register #58: exercised end to end, three defects found and fixed by
running it) except its retargeting to R3 paths, the SHA variable name, and the
comparator filename — mechanical substitutions, `bash -n` clean.

### §9.3 FREEZE CHECKLIST — for the supervisor's `§3` check 4

- [ ] **No open gate question**: every gate, band, threshold, cap, level, ceiling
      and label is a number or a fixed label. `§3.7`'s `DIFFERENT` ruling and the
      `GATE REACHED` cap are stated here, not deferred.
- [ ] `VERIFICATION_CHARTER` `§2b` condition named and checked:
      `verification/runs/ansys_verification/VMFL072-R3/` **does not exist**
      (`§0.1`).
- [ ] **`§20.3`: no pre-freeze run was performed for R3** (`§0.2`).
- [ ] **`§38.1`: every path the driver reads/executes exists at the freeze
      commit** (G-00, exercised in R2).
- [ ] **`§39.5`: every path the comparator reads is one the registered solver
      writes** (`§3.5`) — R2 disk evidence, transferred because **no field name
      changed** (`§3.8`).
- [ ] `compare_vmfl072_r3.py`, `apply_level.sh`, `launch_vmfl072_r3.sh` and the
      fourteen `base/` inputs committed in the **same commit** as this file.
- [ ] The `§9.1` pin matches the committed comparator blob.
- [ ] `check_freeze_ready.py --case cases/ansys_verification/VMFL072-R3 --freeze
      <sha>` returns rc 0 (C7 WARN on the absent run root is non-blocking, and is
      required: the run root must not exist at freeze).

**This draft is untracked. Committing it IS the freeze. No solver may launch
before that commit exists and is named in the launch record.**

---

## §10. WHAT THIS REGISTRATION DOES NOT KNOW — stated plainly

1. **Roy & Jain (1989) is not on this box.** Its Reynolds convention, water
   temperature, monitor station and experimental uncertainty are unknown from the
   source; `§5.1` channel A is a quoted-precision floor, not the experiment's
   uncertainty.
2. **The water temperature is inferred (≈ 23.9 °C).** Channel B carries it and is
   91 % of the band.
3. **The monitor's streamwise station is a declared reading** (`§6.2`), tested by
   `§6.3` but not known from the manual.
4. **The injection geometry (Γ = 76.2 × 0.005) is a declared reading**, first in
   the repair order (`§7.3`).
5. **NZ = 1 is verified at L1 over 100 steps** (R2 §3.6), not at a converged state.
6. **Model-form error is unbounded** by anything this lab owns; it is the ground
   of Limb A's cap.
7. **⚠ WHETHER h₀ = 1e-5 m CURES THE DEWETTING IS ARGUED FROM SOURCE, NOT
   MEASURED** (`§3.9`). No R3 solve has run. The source mechanism and R2's
   healthy B2 (same mesh) are the grounds; `§7.3` states the escalation if the run
   still fails, and no band is widened to admit a result.
8. **The precursor is mesoscopic, not physical** (h₀ = 1e-5 m, 100× the R2
   value). R3 claims only that the macroscopic monitor is uncorrupted (`§3.8`),
   not that microscopic dewetting dynamics are resolved (`§7.2`).
