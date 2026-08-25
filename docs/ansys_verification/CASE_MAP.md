# CASE_MAP — Ansys Fluid Dynamics Verification Manual (VM2026R1) → lab reproducibility map

**NOT FILED ANYWHERE. Nothing in this document leaves this box** (CLAUDE.md rules 7, 8).
The manual is proprietary Ansys documentation; the archives are Ansys project files
uploaded by Sanaa for this lab's private use.

**Zero compute.** This is a reading of the manual index and every case's Overview /
Test Case / Results-Comparison page — no solver was started to produce it.

- **Source (title-page verified by the supervisor):** *Ansys Fluid Dynamics
  Verification Manual*, ANSYS, Inc., Release 2026 R1, March 2026, 290 pp.
  Sidecar `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`
  (6992 lines) checked against the PDF beside it.
- **Manual page** = the manual's own printed page number (from the Table of Contents,
  lines 66–169 of the sidecar), not the PDF page.
- **Archive home (D-6 ruling):** `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/`
  (canonical, outside git). At the time of writing a haiku lane had already MOVED the
  set: the repo-root copy `VM2026R1_Fluids/` reads 0 files, the canonical home holds
  the archives. Both paths were inspected read-only; nothing was touched.
- **Lab solver** = OpenFOAM v2606 at `/usr/lib/openfoam/openfoam2606`. Applications
  confirmed present on this box were enumerated from
  `platforms/*/bin/`. `NONE` / `BLOCKED` is stated honestly where the box has no
  application for the physics.
- Drafted by `ansys-lane-opus48` (running as **claude-opus-4-8[1m]**) for the
  `ansys-verification-supervisor`, 2026-08-24. Draft for the supervisor's read; not a
  register and not a verdict.

---

## Legend

**Dimension** (manual §1.8 key): `2` = 2D · `3` = 3D · `A` = 2D axisymmetric.

**Reference type** (from the `Reference` line + Test-Case text):
- `AN` — analytical / closed-form or textbook correlation (exact target).
- `EXP` — experimental data (journal / conference measurements).
- `NUM` — other code / numerical benchmark (spectral, FEM, CFD reference solution).

**Quantity & N targets** — `discrete(N)` means the manual prints an N-row
Target/Ansys/Ratio table (gate-able against a number directly). `profile` means the
comparison is a plotted curve (figure) with no discrete target row — a lab PASS needs
a digitized profile or a scalar functional (peak, reattachment length, integral).

**Cost class** (order-of-magnitude, single grid level, CPU): `trivial` <5 core-min ·
`small` <60 · `medium` <600 · `large` ≥600. Multiply by ~3 for a full Roache triple.

**Ladder** — is a 3-level systematically-refined grid triple feasible for a Roache
`CONVERGING` verdict? `Y`/`N` + one-line reason. `Y*` = feasible but with a stated
caveat (wall-function y+ band, transient time-step coupling, or gate on a scalar
functional rather than a whole profile).

**Archive column** — `F` = Fluent `.wbpz` present in the canonical home · `+C` = CFX
`.def` archive also present · `Forte` = Forte archive present · `ABSENT` = no archive
for this case anywhere in the set.

**The index X-column headers could not be recovered** — in the PDF (§1.8, pp. 7–9) they
are rotated 90° and pdftotext extracts them as empty. Regime/physics below is taken
instead from each case's own `Physics/Models` line, which is authoritative.

---

## SCOPE, RUN STATUS AND TIER — the campaign at a glance (revised 2026-08-25, `ansys-lane-opus`)

**Sanaa's directive of 2026-08-25**, quoted byte-exact, typos preserved, **not
normalised**:

> *"i just meant for now cfd, ansys verification and heat transfer teams work on
> completeing all the tasks/ running all the cases and recording per our conventions,
> and record whether the case is hold, gate reached or surveyed or not held. Once that
> is done we will go back to the Matrix config. But for now these three teams work on
> that"*

**Sanaa's SCOPE RULING of 2026-08-25**, asked whether the `VMFLGPU` family and the
no-solver cases count toward "completed". Quoted byte-exact, **not normalised**:

> *"for now no. Well add the gpu ones once i turn the gpu back on later."*

**She wrote `Well add`, not `we'll add`.** The bytes are kept as she typed them.
**Normalised spelling is the signature of a relayed paraphrase** — this team's own
finding — so a re-quote that silently repairs her apostrophe is evidence that the line
passed through a summariser rather than coming from her turn. **At the time this
section was written, neither form appeared anywhere at `HEAD`** (checked with
`git grep` over all tracked files in both spellings), so this is the line's first
committed record and there was no normalised copy to correct.

---

# **THE CAMPAIGN FRACTION: 5 of 73 run. 68 never run.**

**THE DENOMINATOR IS 73, NOT 95 — BY SANAA'S RULING, NOT BY THIS LAB'S CHOICE.** The
`VMFLGPU` family (10) and the cases with no lab solver (12) are **out of scope for
now**. All **95** rows remain in the tables below; **22 of them are marked out of scope
and excluded from the denominator.** Nothing is deleted — an exclusion that hides the
excluded rows cannot be audited.

### The counts — DERIVED BY COUNTING THIS DOCUMENT'S OWN ROWS, never recalled

**Every figure is reproducible from this file, and the rule that derives it is printed
beside it so a reader reproduces it rather than trusting the header.** Let
`ROWS` = `grep -E '^\| *(VMFL|VMFLGPU|VMFRT)[0-9]'` over Tables A + B + C.

| figure | value | the rule that derives it from this file |
|---|---|---|
| **cases printed in the manual** | **95** | `ROWS \| wc -l` |
| **IN SCOPE (the denominator)** | **73** | `ROWS \| grep -c 'IN SCOPE'` |
| **run** | **5** | `ROWS \| grep 'IN SCOPE' \| grep -vc 'NEVER RUN'` |
| **never run** | **68** | `ROWS \| grep 'IN SCOPE' \| grep -c 'NEVER RUN'` |
| **DEFERRED — the `VMFLGPU` family** | **10** | `ROWS \| grep -c 'DEFERRED'` |
| **OUT OF SCOPE — no lab solver** | **12** | `ROWS \| grep -c 'OUT OF SCOPE'` |
| **overlap of the two exclusions** | **0** | `ROWS \| grep 'DEFERRED' \| grep -c 'OUT OF SCOPE'` |
| **check: 73 + 10 + 12** | **95** | the three groups partition the table exactly |

**A NOTE ON THE ROW SET, because it is the part that breaks silently.** Each rule is
scoped to `ROWS`. An **unscoped** `grep -c` over the whole file returns the wrong
answer, because this header's own prose contains the same phrases — e.g. unscoped
`grep -c 'OUT OF SCOPE'` counts this sentence too. **A count rule that is true only
until someone edits the prose above it is not a derivation.** Scope every count to the
row set.

### The two axes are SEPARATE and must not be read as one

**`Tier` and `Scope status` are different questions and are carried in different
columns.** A tier is a judgement about **evidence** and is written **at grading time**;
a scope status is a ruling about **whether the case is in this campaign at all**.
**An out-of-scope case has NO TIER — it has a scope status**, and its tier cell reads
`—` rather than `NEVER RUN`, because "never run" would imply it was in the queue.

- **Tier vocabulary** (in-scope rows only, unchanged): `HOLDS` · `GATE REACHED` ·
  `SURVEYED` · `NOT HELD` · `NEVER RUN`.
- **Scope status vocabulary:** `IN SCOPE` · `DEFERRED` · `OUT OF SCOPE — BY RULING`.
- **The tier and the rule-1 verdict are also different vocabularies**, recorded side by
  side, and **the tier never flatters the verdict**. They overlap at one word only,
  `GATE REACHED`. The rule-1 vocabulary — `PASS` / `GATE REACHED` / `GATE FAIL` /
  `NOT A RESULT` / `BLOCKED` / `PENDING` — is unchanged and is not replaced here.

### The EIGHT RUNS across SIX CASES, and their tiers — the supervisor's rulings, overrulable

**This table DUPLICATES facts derived elsewhere (the register's rows, the row table's tier
cells, the campaign fraction), and a hand-maintained duplicate DRIFTS — it did: it read "four
cases run" while listing five rows and omitting `VMFL003` entirely, under-reporting the
campaign and dropping a `NOT A RESULT`, which is the FLATTERING direction.** It is now checked
by `verification/runs/ansys_verification/check_case_map_glance.py`, which derives the expected
rows from the **register** and refuses on any mismatch. **The register is the authority; this
table is a convenience and is never the source.**

| case | verdict (rule 1) | **tier** | why the tier is what it is |
|---|---|---|---|
| **VMFL001** run 1 | `NOT A RESULT` | **`NOT HELD`** | the comparator refused on the v2606 sampled-file naming and produced no number, and L3 independently failed the registered convergence clause. **Nothing was measured**, so there is nothing to hold |
| **VMFL001-R2** | `PASS` | **`HOLDS`** — **a CANDIDATE, stated as one** | V and G both strong: `CONVERGING`, observed order **2.0102**, GCI **0.0563 %**, Richardson landing on the analytic value to **3.7 ppm**. **A candidate and not a settled hold because the P limb is UNRESOLVED**; calling it settled on V and G alone is the flattery this column exists to prevent |
| **VMFL005** | `PASS` | **`GATE REACHED`** | gate genuinely met and triple genuinely `CONVERGING` — **P is the missing limb and is named**: the deviation is **9.92× the fine GCI** and Richardson extrapolates **away** from exact, so ~90 % of the residual is a modelling signature (`N-AV7`); mechanism open at docket **`D512`** |
| **VMFL051** | `NOT A RESULT` | **`NOT HELD`** | **V present, G ABSENT, G decides it**: `OSCILLATORY` at **R = −1.348600**, no observed order, no quotable GCI, two of three levels failing the frozen plateau clause. **`GATE REACHED` was refused deliberately** — that word fits a case with a *believable measurement* lacking one column (VMFL005). **VMFL051 produced no usable measurement at all; its G column is not missing, it is actively negative** |
| **VMFL045** run 1 | `NOT A RESULT` | **`NOT HELD`** | **produced NO measurement at all** — `rhoCentralFoam` died at wall 0 s on its first timestep with `Entry 'e' not found in fvSolution/solvers`, a frozen-`fvSolution` `e`/`h` defect inherited from the inviscid VMFL051 (VMFL045 is viscous, μ=1e-8, so the implicit energy corrector runs, the path μ=0 never took). **No triple, no observed order, no GCI, no plateau statistics — nothing to hold.** `GATE REACHED` needs a believable measurement lacking one column; there is no measurement. Repaired as the VMFL045-R2 rung, which RAN: verdict `PASS`, tier `GATE REACHED` (register row #7; `cases/ansys_verification/VMFL045/R2/RESULTS.md`) |
| **VMFL003** | `NOT A RESULT` | **`NOT HELD`** | **V present, G ACTIVELY NEGATIVE, as in VMFL051.** Rule 5 step 1 fired before any triple: **all three levels failed the frozen iterative-convergence residual leg** (L3 missed on **ε alone, 2.523e−08, by 2.5×**). **`GATE REACHED` was refused deliberately — the gate was not reached, it was MISSED by 3.6× the band** (Δp 20800.8245 Pa vs 21744 = **−4.3376 %** on a 2.5 % band). **The miss is MODEL-LEVEL, not discretisation:** the deviation vs the manual's target and vs the closed-form Colebrook correlation are **nearly identical** (−4.34 % / −4.55 %), so it is not the 3-s.f. chart read — exactly the k-ε wall-treatment hazard its own pre-registration named as principal risk BEFORE compute |
| **VMFL045-R2** | `PASS` | **`GATE REACHED`** | **G is the missing limb and is NAMED.** Gate met by **24×** (lab **1.874779041082** vs target 1.874 = **+0.041571 %** on a 1 % band) and **V is strong** — the exact closed form derived here, **1.874976957681054**, is matched to **−0.010556 %, about one part in 10⁴**. **But the observed order p = 3.3862 is ABOVE the scheme's formal order**, past the pre-registration's own declared *p ≈ 1 expected, p ≈ 2 suspicious*; and **d21 = −2.447e−04 is only ~3× L3's plateau ptp of 7.77e−05**, so the medium–fine difference sits within a small factor of the NOISE FLOOR — the diagnostic that condemned VMFL051 at ~1×. **So GCI_fine 0.0017 % is NOT a discretisation-uncertainty statement** (`N-AV7` in its second form: a small GCI licenses nothing). Order recorded as **MEASURED BUT NOT TRUSTED** |
| **VMFL007** run 1 | `NOT A RESULT` | **`NOT HELD`** | **NO NUMBER WAS PRODUCED — the case DIVERGED.** `L1_25x25` ran all 10 000 iterations, rc = 0, `End` written — **and that is hollow**: areaAverage(p)_inlet reached **9.449536950130e+144 m²/s²** against a physical 60.522, continuity error **1.04772404566e+72**, divergence beginning at **iteration 2**, and from **iteration 904** the whole viscosity field pinned on the `nuMin` floor 1e−08, **4 298× below** the physical wall value. `L2_50x50` died at iteration 9 065 with SIGFPE in `GAMGSolver::scale` — an **overflow symptom** (pressure 6.03e+211; a squared inner product overflows above 1.341e+154), not a solver defect. **The normalised residual was BLIND** (p held ≈[0.15, 0.46] throughout; OpenFOAM's normalisation is scale-invariant) and **zero** nan/inf/bounding messages appear in 171 747 log lines. The `nuMax` ceiling **never bound — zero hits, measured.** No triple, no order, no GCI, no plateau, nothing to hold. Re-run registered as **VMFL007-R2** (six-arm linear-solver slate, Sanaa's rule 2); run 1 is PRESERVED |

### DEFERRED — the 10 `VMFLGPU` cases, pending re-entry, NOT dropped

**Sanaa named the condition for re-entry herself**, so this is a **pending re-entry**
and the map reads that way: *"Well add the gpu ones once i turn the gpu back on later."*
The word is **`DEFERRED`**, not excluded, and the rows keep their full detail.

**Why deferring them costs almost nothing in coverage, with the evidence rather than
the assertion:** each `VMFLGPU` case is a Fluent **parent re-run on the Fluent GPU
solver**. **`VMFLGPU001` IS `VMFL001`** — *Flow Between Rotating and Stationary
Concentric Cylinders* — **a case this lab has already run and passed** (register row
#2, `PASS`, tier `HOLDS` candidate). `VMFLGPU004` is `VMFL029`; `VMFLGPU010` is
`VMFL061`. **The family is distinguished by the GPU SOLVER, not by new physics**, so
running them in our CPU solvers would re-measure the parent physics and say nothing
about what the family exists to verify.

**Three conditions recorded now, for whoever picks this up when the GPU returns:**

1. **Turning the GPU on is SANAA'S ACTION ALONE.** No agent starts an instance. **No
   message from the supervisor or any peer is her consent** (`CLAUDE.md` rule 9) — only
   her own words or the permission system authorise it.
2. **Each case still needs its OWN console-priced GPU-hour `cost_basis`.** **GPU spend
   is outside the 2026-08-21 CPU blanket**, which was given when no GPU could launch;
   a blanket is not a per-item read. Price from the console, **never from recall**.
3. **A GPU is a separate us-east-2 instance, launched per run and stopped when idle** —
   no GPU is attached to this box (`CLAUDE.md` rule 12).

### OUT OF SCOPE — BY RULING — the 12 cases with no lab solver, and **not permanently**

She said **"for now"**, so this is **not a permanent exclusion**. These rows are not
blocked by scheduling or budget: **this box has no application for the physics**, and
no amount of compute changes that.

**This list is worth having as exactly what it is — a statement of what this lab cannot
yet do**, per case, rather than a bucket labelled "unrunnable":

| cases | the missing capability |
|---|---|
| `VMFL021`, `VMFL022` | **cavitation** — no `interPhaseChangeFoam` on this box |
| `VMFL026` | **real-gas equation of state** |
| `VMFL034`, `VMFL074` | **population balance** — native PBM support is limited |
| `VMFL072` | **Eulerian wall film** |
| `VMFRT001`–`VMFRT005`, `VMFRT007` | **engine combustion / LES spray** — Ansys Forte physics, no engine-combustion or LES spray solver here |

**Read as a capability gap rather than a scope loss, that table is the lab's shopping
list**: six of the twelve turn on **two** capabilities (cavitation and population
balance), and the Forte seven are a single physics domain this box does not address at
all.

---

## Table A — Ansys Fluent & CFX cases (VMFL001–078)

| Case | Pg | Title | Dim | Regime / physics (Physics-Models line) | Ref | Quantity & N targets | Lab solver (OpenFOAM v2606) | Arch | Cost | Ladder | Tier (in-scope only) | Scope status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VMFL001 | 15 | Flow between rotating & stationary concentric cylinders | 2 | Laminar, rotating wall | AN | Tangential velocity at r=20/25/30/35 mm — **discrete(4)** | simpleFoam / icoFoam (rotatingWallVelocity) | F+C | trivial | Y — structured annulus, monotone | **`NOT HELD`** (run 1) → **`HOLDS`** *candidate* (R2) | `IN SCOPE` |
| VMFL002 | 17 | Laminar flow through pipe, uniform heat flux | A | Laminar + heat transfer (Mercury) | AN | Pressure drop + centreline outlet T — **discrete(2)** | simpleFoam + energy / buoyantSimpleFoam | F+C | trivial | Y — axisym wedge, monotone | `NEVER RUN` | `IN SCOPE` |
| VMFL003 | 19 | Pressure drop, turbulent pipe flow | A | Turbulent, standard k-ε | AN | Pressure drop — **discrete(1)** | simpleFoam (kEpsilon) | F+C | trivial | Y* — hold y+ band across levels | `NOT HELD` | `IN SCOPE` |
| VMFL004 | 21 | Plain Couette flow with pressure gradient | 2 | Laminar, moving wall, periodic | AN | X-velocity profile at X=0.75 m — **profile** | pimpleFoam/simpleFoam (cyclic + pressureGradient) | F+C | trivial | Y* — gate on profile / centre value | `NEVER RUN` | `IN SCOPE` |
| VMFL005 | 25 | Poiseuille flow in a pipe | A | Steady laminar | AN | Pressure drop (Hagen-Poiseuille) — **discrete(1)** | icoFoam / simpleFoam | F+C | trivial | Y — axisym, exact analytic | **`GATE REACHED`** | `IN SCOPE` |
| VMFL006 | 27 | Multicomponent species transport in pipe flow | A | Laminar, species transport | AN | Mass fraction of species A along axis — **profile** | reactingFoam (inert) / scalarTransportFoam | F+C | small | Y* — gate on profile | `NEVER RUN` | `IN SCOPE` |
| VMFL007 | 29 | Non-Newtonian flow in a pipe | A | Laminar, power-law viscosity | AN | Pressure drop — **discrete(1)** | nonNewtonianIcoFoam (powerLaw) | F+C | trivial | Y — axisym, analytic | `NOT HELD` | `IN SCOPE` |
| VMFL008 | 31 | Flow inside a rotating cavity | A | Laminar, rotating reference frame | NUM | Radial & swirl velocity at X=0.6 m — **profile** | SRFSimpleFoam | F+C | small | Y* — gate on profile | `NEVER RUN` | `IN SCOPE` |
| VMFL009 | 35 | Natural convection in concentric annulus | 2 | Natural convection, laminar, heat | EXP | Wall static-temperature distribution — **profile** | buoyantSimpleFoam / buoyantBoussinesqSimpleFoam | F+C | small | Y* — gate on profile | `NEVER RUN` | `IN SCOPE` |
| VMFL010 | 39 | Laminar flow in a 90° tee-junction | 2 | Laminar | NUM | Flow split (fractional flow) — **discrete(1)** | simpleFoam / icoFoam | F+C | trivial | Y — 2D, monotone | `NEVER RUN` | `IN SCOPE` |
| VMFL011 | 41 | Laminar flow in a triangular cavity | 2 | Laminar (driven) | NUM | Normalized X-velocity on bisector — **profile** | icoFoam / simpleFoam | F+C | small | Y* — gate on profile | `NEVER RUN` | `IN SCOPE` |
| VMFL012 | 45 | Turbulent flow in a wavy channel | 2 | Turbulent, separation, periodic | EXP | Normalized X-velocity at crest/trough — **profile** | simpleFoam/pimpleFoam (kEpsilon) | F+C | small | Y* — y+ band | `NEVER RUN` | `IN SCOPE` |
| VMFL013 | 51 | Turbulent flow + heat, backward-facing step | 2 | Incompressible turbulent, heat, reattachment | EXP | Local Nusselt number along heated wall — **profile** | rhoSimpleFoam / simpleFoam + energy | F+C | small | Y* — y+ band + profile | `NEVER RUN` | `IN SCOPE` |
| VMFL014 | 55 | Species mixing in co-axial turbulent jets | A | Multi-species, turbulent, jet mixing | EXP | Propane & X-velocity along jet axis — **profile** | reactingFoam (inert) / simpleFoam+scalarTransport | F+C | small | Y* — profile | `NEVER RUN` | `IN SCOPE` |
| VMFL015 | 61 | Flow through an engine inlet valve | 3 | 3D turbulent | EXP | Z-velocity at Z=−5/+10 mm — **profile** | simpleFoam (kEpsilon) | F+C | large | Y* — 3D, y+; costly | `NEVER RUN` | `IN SCOPE` |
| VMFL016 | 65 | Turbulent flow in a transition duct | 3 | 3D turbulent, Reynolds stress model | EXP | Pressure coefficient (station 5, centreline) — **profile** | simpleFoam (RSM: LRR/SSG) | F+C | large | Y* — 3D RSM; costly | `NEVER RUN` | `IN SCOPE` |
| VMFL017 | 69 | Transonic flow over an RAE 2822 airfoil | 2 | Compressible, turbulent | EXP | Drag & lift coefficient — **discrete(2)** | rhoSimpleFoam (SST) | F+C | small | Y* — y+ + shock capture | `NEVER RUN` | `IN SCOPE` |
| VMFL018 | 71 | Shock reflection in supersonic flow | 2 | Reflecting shocks, compressible turbulent | EXP | Afterbody static pressure & heat flux — **profile** | sonicFoam / rhoCentralFoam | F+C | small | Y* — shock capture | `NEVER RUN` | `IN SCOPE` |
| VMFL019 | 77 | Transient flow near a wall set in motion | 2 | Unsteady, moving wall (Stokes 1st problem) | AN | Near-wall velocity profile at outlet — **profile** | pimpleFoam / icoFoam (transient) | F+C | trivial | Y* — space+time refinement | `NEVER RUN` | `IN SCOPE` |
| VMFL020 | 79 | Adiabatic compression of air by a piston | 2 | Dynamic mesh, transient, ideal gas | AN | Static T & p vs time — **profile** | rhoPimpleFoam (dynamicMesh) | F+C | small | Y* — mesh-motion + time | `NEVER RUN` | `IN SCOPE` |
| VMFL021 | 85 | Cavitation over a sharp-edged orifice A (high p) | A | Turbulent multiphase, cavitation, phase change | EXP | Discharge coefficient — **discrete(1)** | **BLOCKED** — no cavitation solver (interPhaseChangeFoam absent) | F+C | — | N — no solver | — | **`OUT OF SCOPE — BY RULING`** — cavitation (no `interPhaseChangeFoam`) |
| VMFL022 | 87 | Cavitation over a sharp-edged orifice B (low p) | A | Turbulent multiphase, cavitation, phase change | EXP | Discharge coefficient — **discrete(1)** | **BLOCKED** — no cavitation solver | F | — | N — no solver | — | **`OUT OF SCOPE — BY RULING`** — cavitation (no `interPhaseChangeFoam`) |
| VMFL023 | 89 | Oscillating laminar flow around a circular cylinder | 2 | Laminar, transient (vortex shedding) | AN | Strouhal / drag (from table) — **discrete(1)** | pimpleFoam / icoFoam | F+C | small | Y* — time-accurate | `NEVER RUN` | `IN SCOPE` |
| VMFL024 | 91 | Interface of two immiscible liquids in rotating cylinder | A | Multiphase (VOF), transient, body force | EXP | Non-dim swirl velocity at 3 radii (t=80 s) — **discrete(3)** | interFoam (SRF/MRF) | F | small | Y* — VOF interface | `NEVER RUN` | `IN SCOPE` |
| VMFL025 | 93 | Turbulent non-premixed methane combustion, swirling air | A | Turbulent swirl, non-premixed combustion | EXP | Axial/swirl velocity, T, CO at X=40 mm — **profile** | reactingFoam (hard — combustion model) | F | medium | Y* — hard physics | `NEVER RUN` | `IN SCOPE` |
| VMFL026 | 99 | Supersonic real-gas flow inside a shock tube | 3 | Transient compressible, real gas, shock | NUM | Centreline static T & p — **profile** | sonicFoam/rhoCentralFoam (perfect-gas; **real-gas EOS BLOCKED**) | F+C | medium | Y* — perfect-gas only | — | **`OUT OF SCOPE — BY RULING`** — real-gas EOS |
| VMFL027 | 103 | Turbulent flow over a backward-facing step | 2 | 2D turbulent, realizable k-ε | EXP | Skin-friction coefficient along wall — **profile** | simpleFoam (realizableKE) | F+C | small | Y* — y+ + reattachment | `NEVER RUN` | `IN SCOPE` |
| VMFL028 | 107 | Turbulent heat transfer in a pipe expansion | A | Heat transfer, turbulent, recirculation | EXP | Nusselt number along heated wall — **profile** | rhoSimpleFoam / simpleFoam + energy | F | small | Y* — y+ band | `NEVER RUN` | `IN SCOPE` |
| VMFL029 | 109 | Anisotropic conduction heat transfer | 2 | Heat conduction, anisotropic conductivity | AN | Normalized T at X=0.5 m — **profile** | laplacianFoam (isotropic only; **anisotropic tensor DT not native** → custom) | F | trivial | Y* — needs tensor diffusivity | `NEVER RUN` | `IN SCOPE` |
| VMFL030 | 111 | Turbulent flow in a 90° pipe-bend | 3 | 3D turbulent, RNG k-ε, non-equilibrium wall fns | EXP | Velocity magnitude at 75° along bend — **profile** | simpleFoam (RNGkEpsilon) | F | medium | Y* — 3D, half-domain, y+ | `NEVER RUN` | `IN SCOPE` |
| VMFL031 | 113 | Turbulent flow behind an open-slit V-gutter | 2 | Turbulent | EXP | X-velocity 22 mm downstream — **profile** | simpleFoam / pimpleFoam | F | small | Y* — profile | `NEVER RUN` | `IN SCOPE` |
| VMFL032 | 115 | Turbulent separated flow along axisymmetric afterbody | A | Turbulent, separation | EXP | Pressure & skin-friction along afterbody — **profile** | simpleFoam (kOmegaSST) | F+C | small | Y* — y+ + separation | `NEVER RUN` | `IN SCOPE` |
| VMFL033 | 119 | Viscous heating in an annulus | 2 | Viscous flow + heating, moving wall (dissipation) | AN | Velocity & temperature profiles — **profile** | rhoSimpleFoam / chtMultiRegion (viscous dissipation) | F | trivial | Y* — profile | `NEVER RUN` | `IN SCOPE` |
| VMFL034 | 121 | Particle aggregation inside a turbulent stirred tank | 2 | Multiphase, population balance, turbulent | AN | Moments m0–m5 of PBE — **discrete(6)** | reactingMultiphaseEulerFoam (PBM, hard) / **NONE (native PBM limited)** | F | medium | N — no clean PBM solver | — | **`OUT OF SCOPE — BY RULING`** — population balance (native PBM limited) |
| VMFL035 | 123 | 3-D single-stage axial compressor | 3 | Compressible transonic, turbulent, moving ref frame | NUM | Stator-outlet pressure & mass-flow — **discrete(2)** | rhoSimpleFoam (MRF) | F | large | Y* — 3D turbomachinery; costly | `NEVER RUN` | `IN SCOPE` |
| VMFL036 | 125 | Laminar flow past a sphere | A | Laminar | NUM | Drag coefficient (Re≈50) — **discrete(1)** | simpleFoam (axisym) | F | small | Y — axisym, monotone (large far-field) | `NEVER RUN` | `IN SCOPE` |
| VMFL037 | 127 | Turbulent flow over a forward-facing step | 2 | SST, turbulent, separation/reattachment | EXP | Pressure coefficient along wall — **profile** | simpleFoam (kOmegaSST) | F+C | small | Y* — y+ band | `NEVER RUN` | `IN SCOPE` |
| VMFL038 | 131 | Falling film over an inclined plane | 2 | Laminar, free-surface (VOF) | AN | Velocity profile at outlet — **profile** | interFoam | F | small | Y* — VOF interface | `NEVER RUN` | `IN SCOPE` |
| VMFL039 | 133 | Boiling in a pipe with heated wall | A | Multiphase, phase change, RPI wall boiling | EXP | Temperature along pipe wall — **profile** | reactingTwoPhaseEulerFoam (wall boiling, hard) | F+C | medium | N* — RPI boiling hard/partial | `NEVER RUN` | `IN SCOPE` |
| VMFL040 | 137 | Separated turbulent flow in a diffuser | A | SST, adverse pressure gradient, separation | EXP | (profile) — **profile** | simpleFoam (kOmegaSST) | F+C | small | Y* — separation | `NEVER RUN` | `IN SCOPE` |
| VMFL041 | 141 | Transonic flow over an airfoil | 2 | Transonic, shock, SST | EXP | Pressure coefficient on airfoil — **profile** | rhoSimpleFoam (SST) | F | small | Y* — shock + y+ | `NEVER RUN` | `IN SCOPE` |
| VMFL042 | 143 | Turbulent mixing of two streams, different densities | 2 | SST, mixing layer, density diff, buoyancy | EXP | Salt-water mass fraction at x=10 m — **profile** | simpleFoam + energy / buoyantSimpleFoam | F+C | small | Y* — profile | `NEVER RUN` | `IN SCOPE` |
| VMFL043 | 147 | Laminar→turbulent transition of BL over flat plate | 2 | SST, transitional | EXP | Skin-friction coefficient on plate — **profile** | simpleFoam (kOmegaSSTLM transition) | F | small | Y* — transition model | `NEVER RUN` | `IN SCOPE` |
| VMFL044 | 149 | Supersonic nozzle flow | A | Compressible supersonic, SST | EXP | Pressure ratio along nozzle wall — **profile** | rhoSimpleFoam / sonicFoam | F+C | small | Y* — shock capture | `NEVER RUN` | `IN SCOPE` |
| VMFL045 | 153 | Oblique shock over an inclined ramp | 2 | Compressible supersonic, oblique shock | AN | Mach, T, density downstream — **discrete(3)** | rhoCentralFoam / sonicFoam | F+C | trivial | Y — μ=1e-8 (near-inviscid but NONZERO → viscous energy path; run-1 finding), monotone | **`NOT HELD`** (run 1) → **`GATE REACHED`** (R2) | `IN SCOPE` |
| VMFL046 | 155 | Normal shock in a converging-diverging nozzle | 2 | Compressible supersonic, normal shock | AN | Mach along centreline (vs analytic) — **profile** | rhoCentralFoam / sonicFoam | F | small | Y* — shock capture | `NEVER RUN` | `IN SCOPE` |
| VMFL047 | 157 | Turbulent separated flow in an asymmetric diffuser | 2 | Turbulent separation, standard k-ω | EXP | X-velocity at X=24 (profile) — **profile** | simpleFoam (kOmega) | F+C | small | Y* — separation | `NEVER RUN` | `IN SCOPE` |
| VMFL048 | 159 | Turbulent flow in a 180° pipe bend | 3 | SST, turbulent, separation/reattachment | EXP | Axial velocity at a section — **profile** | simpleFoam (kOmegaSST) | F | medium | Y* — 3D, y+ | `NEVER RUN` | `IN SCOPE` |
| VMFL049 | 161 | Combustion in axisymmetric natural-gas furnace | A | Turbulent non-premixed combustion, EDM, k-ε | EXP | Mole fraction of CH4 along axis — **profile** | reactingFoam (EDM, hard) | F | medium | Y* — hard physics | `NEVER RUN` | `IN SCOPE` |
| VMFL050 | 163 | Transient heat conduction in a semi-infinite slab | 2 | Transient heat transfer, conduction | AN | Wall T & T at 150 mm, t=120 s — **discrete(2)** | laplacianFoam | F | trivial | Y* — space + time refinement | `NEVER RUN` | `IN SCOPE` |
| VMFL051 | 165 | Isentropic expansion over a convex corner | 2 | Compressible inviscid (Prandtl-Meyer) | AN | Mach after expansion — **discrete(1)** | rhoCentralFoam / sonicFoam | F+C | trivial | Y — inviscid, monotone | **`NOT HELD`** | `IN SCOPE` |
| VMFL052 | 167 | Turbulent natural convection inside a tall cavity | 2 | Turbulent, buoyancy, Boussinesq | EXP | Vertical velocity at Y/h — **profile** | buoyantBoussinesqSimpleFoam / buoyantSimpleFoam | F+C | small | Y* — y+ + buoyancy | `NEVER RUN` | `IN SCOPE` |
| VMFL053 | 171 | Compressible turbulent mixing layer | 2 | RNG k-ε, compressible, energy | EXP | (profile) — **profile** | rhoSimpleFoam (RNGkEpsilon) | F | small | Y* — profile | `NEVER RUN` | `IN SCOPE` |
| VMFL054 | 173 | Laminar flow in a trapezoidal cavity | 2 | Viscous, driven by moving walls | NUM | X-velocity (profile) — **profile** | icoFoam / simpleFoam | F+C | small | Y* — gate on profile | `NEVER RUN` | `IN SCOPE` |
| VMFL055 | 177 | Transitional recirculatory flow in ventilation enclosure | 2 | Transitional (k-kl model) | EXP | X-velocity at Y=2 — **profile** | simpleFoam (kkLOmega) | F | small | Y* — transition model | `NEVER RUN` | `IN SCOPE` |
| VMFL056 | 179 | Combined conduction & radiation in a square cavity | 2 | Radiation (discrete-ordinate), conduction | NUM | Non-dim T at X=0 — **profile** | chtMultiRegionSimpleFoam + fvDOM | F | small | Y* — radiation model | `NEVER RUN` | `IN SCOPE` |
| VMFL057 | 181 | Radiation & conduction in composite solid layers | 2 | Radiation (DO), participating medium, conduction | NUM | (profile) — **profile** | chtMultiRegion + fvDOM | F | small | Y* — radiation model | `NEVER RUN` | `IN SCOPE` |
| VMFL058 | 183 | Turbulent flow in an axisymmetric diffuser | A | Turbulent, adverse pressure gradient | EXP | Pressure coefficient along diffuser — **profile** | simpleFoam (kOmegaSST) | F | small | Y* — separation | `NEVER RUN` | `IN SCOPE` |
| VMFL059 | 185 | Conduction in a composite solid block | 2 | Conduction with heat source | AN | Side-wall temperatures — **discrete(2)** | chtMultiRegionSimpleFoam / laplacianFoam | F+C | trivial | Y — pure conduction, monotone | `NEVER RUN` | `IN SCOPE` |
| VMFL060 | 187 | Transitional supersonic flow over rearward-facing step | 2 | Compressible, transitional (Transition SST) | EXP | Non-dim static pressure on stepped wall — **profile** | rhoSimpleFoam / sonicFoam (transition SST) | F | small | Y* — shock + transition | `NEVER RUN` | `IN SCOPE` |
| VMFL061 | 189 | Surface-to-surface radiation between two concentric cylinders | 2 | Radiation modeling (S2S) | AN | Temperature along radius — **profile** | chtMultiRegion + viewFactor (S2S) radiation | F | trivial | Y* — radiation only | `NEVER RUN` | `IN SCOPE` |
| VMFL062 | 191 | Fully developed turbulent flow over a "hill" | 2 | Low-Re k-ε turbulent | EXP | Skin-friction along wall — **profile** | simpleFoam (low-Re kEpsilon) | F | small | Y* — low-Re mesh | `NEVER RUN` | `IN SCOPE` |
| VMFL063 | 193 | Separated laminar flow over a blunt plate | 2 | Laminar, high-resolution schemes | EXP | Non-dim reattachment length (LR/2t) — **discrete(1)** | icoFoam / simpleFoam | F+C | small | Y — laminar, gate on LR | `NEVER RUN` | `IN SCOPE` |
| VMFL064 | 195 | Low-Re flow in a channel with sudden asymmetric expansion | 2 | Laminar, separation, reattachment | EXP | Non-dim reattachment length — **discrete(1)** | icoFoam / simpleFoam | F | small | Y — laminar, gate on LR | `NEVER RUN` | `IN SCOPE` |
| VMFL065 | 197 | Swirling turbulent flow inside a diffuser | A | Turbulent, swirl, Reynolds stress model | EXP | Swirl velocity at X=0 — **profile** | simpleFoam (RSM) | F | small | Y* — RSM, swirl | `NEVER RUN` | `IN SCOPE` |
| VMFL066 | 199 | Radiative heat transfer in enclosure, participating medium | 2 | Radiation (discrete-ordinate) | NUM | Non-dim heat flux along hot wall — **profile** | fireFoam / chtMultiRegion + fvDOM | F | small | Y* — radiation model | `NEVER RUN` | `IN SCOPE` |
| VMFL067 | 201 | Boiling in a pipe — critical heat flux | A | Multiphase, heat & mass transfer, boiling | NUM | Wall temperature — **profile** | reactingTwoPhaseEulerFoam (boiling, hard) | F | medium | N* — boiling hard/partial | `NEVER RUN` | `IN SCOPE` |
| VMFL068 | 203 | Axial flow in an eccentric annulus | 3 | Steady, periodic, turbulent, RSM | EXP | Normalized axial velocity at plane 2 — **profile** | simpleFoam (RSM) | **ABSENT** | medium | Y* — 3D RSM; **no archive** | `NEVER RUN` | `IN SCOPE` |
| VMFL069 | 205 | Two-phase Poiseuille flow | 3 | Steady, laminar, two-phase | NUM | Velocity profile (two-phase) — **profile** | interFoam (or viscosity-stratified simpleFoam) | F | small | Y* — 3D, laminar, interface fixed | `NEVER RUN` | `IN SCOPE` |
| VMFL070 | 207 | Radiation between two parallel surfaces | 2 | Heat transfer, radiation | AN | Normalized T (vs analytic) — **profile** | chtMultiRegion + fvDOM / viewFactor | F | trivial | Y* — radiation only | `NEVER RUN` | `IN SCOPE` |
| VMFL071 | 209 | Mid-span flow over a Goldman stator blade | 2 | Turbomachinery (transonic cascade) | EXP | Pressure ratio (vs experiment) — **profile** | rhoSimpleFoam (cascade) | F | small | Y* — transonic cascade | `NEVER RUN` | `IN SCOPE` |
| VMFL072 | 211 | Liquid water flow over flat plate under gravity | 3 | Eulerian wall film | EXP | Film thickness — **discrete(1)** | **NONE** — no Eulerian wall-film solver on box | F | small | N — no solver | — | **`OUT OF SCOPE — BY RULING`** — Eulerian wall film |
| VMFL073 | 213 | Turbulent separated flow in axisymmetric diffuser | A | Turbulence, separation | EXP | Skin-friction along diffuser wall — **profile** | simpleFoam (kOmegaSST) | F | small | Y* — separation | `NEVER RUN` | `IN SCOPE` |
| VMFL074 | 215 | Modeling of a plug-flow atomizer | 2 | Multiphase, population balance, turbulence | NUM | Number density of bin-2 fraction — **profile** | reactingParcelFoam / **NONE (native PBM limited)** | F | medium | N — no clean PBM solver | — | **`OUT OF SCOPE — BY RULING`** — population balance (native PBM limited) |
| VMFL075 | 217 | Supersonic flow over a circular-arc bump | 2 | Inviscid, compressible, supersonic | NUM | Mach along lower wall (vs reference) — **profile** | rhoCentralFoam / sonicFoam | F | small | Y* — shock capture | `NEVER RUN` | `IN SCOPE` |
| VMFL076 | 219 | Forced convection over a flat plate | 2 | Laminar, convection (low Prandtl) | AN | Normalized T (vs analytic) — **profile** | simpleFoam + energy / rhoSimpleFoam | F | trivial | Y* — Blasius/low-Pr, profile | `NEVER RUN` | `IN SCOPE` |
| VMFL077 | 221 | Free-surface flow around a ship | 3 | Turbulent, free surface (VOF) | EXP | Water level on hull — **profile** | interFoam | F | large | Y* — 3D VOF; costly | `NEVER RUN` | `IN SCOPE` |
| VMFL078 | 223 | Polyhedral mesh accuracy (3D lid-driven cubic cavity, Re=1000) | 3 | Laminar, driven by moving wall | NUM | X-velocity on vertical centreline (symmetry plane) — **profile** | icoFoam / simpleFoam | F | medium | Y — structured hex triple, benchmark | `NEVER RUN` | `IN SCOPE` |

## Table B — Ansys Fluent GPU cases (VMFLGPU001–010)

The GPU cases are the **same physics as a Fluent parent**, re-run on the Fluent GPU
solver. The lab has **no GPU attached** (a GPU is a separate us-east-2 instance,
launched per run — CLAUDE.md rule 12); every GPU case runs on the **same OpenFOAM CPU
application** as its parent. **No GPU `.wbpz` archive exists in the set** (all ABSENT).

| Case | Pg | Title | Dim | Parent | Ref | Quantity & N targets | Lab solver | Arch | Cost | Ladder | Tier (in-scope only) | Scope status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VMFLGPU001 | 225 | Rotating & stationary concentric cylinders | 2 | VMFL001 | AN | Tangential velocity, 4 radii — **discrete(4)** | simpleFoam / icoFoam | ABSENT | trivial | Y | — | **`DEFERRED`** — GPU off; Sanaa: *"Well add the gpu ones once i turn the gpu back on later."* |
| VMFLGPU002 | 227 | Laminar flow in a 90° tee-junction | 2 | VMFL010 | NUM | Flow split — **discrete(1)** | simpleFoam / icoFoam | ABSENT | trivial | Y | — | **`DEFERRED`** — GPU off; Sanaa: *"Well add the gpu ones once i turn the gpu back on later."* |
| VMFLGPU003 | 229 | Laminar flow in a triangular cavity | 2 | VMFL011 | NUM | Normalized X-velocity on bisector — **profile** | icoFoam / simpleFoam | ABSENT | small | Y* | — | **`DEFERRED`** — GPU off; Sanaa: *"Well add the gpu ones once i turn the gpu back on later."* |
| VMFLGPU004 | 233 | Anisotropic conduction heat transfer | 2 | VMFL029 | AN | Normalized T at X=0 — **profile** | laplacianFoam (anisotropic → custom) | ABSENT | trivial | Y* | — | **`DEFERRED`** — GPU off; Sanaa: *"Well add the gpu ones once i turn the gpu back on later."* |
| VMFLGPU005 | 235 | Turbulent natural convection in a tall cavity | 2 | VMFL052 | EXP | Vertical velocity at Y/h — **profile** | buoyantBoussinesqSimpleFoam | ABSENT | small | Y* | — | **`DEFERRED`** — GPU off; Sanaa: *"Well add the gpu ones once i turn the gpu back on later."* |
| VMFLGPU006 | 239 | Mid-span flow over a Goldman stator blade | 2 | VMFL071 | EXP | Pressure ratio (vs experiment) — **profile** | rhoSimpleFoam (cascade) | ABSENT | small | Y* | — | **`DEFERRED`** — GPU off; Sanaa: *"Well add the gpu ones once i turn the gpu back on later."* |
| VMFLGPU007 | 243 | Turbulent flow + heat, backward-facing step | 2 | VMFL013 | EXP | Surface Nusselt number — **profile** | rhoSimpleFoam / simpleFoam + energy | ABSENT | small | Y* | — | **`DEFERRED`** — GPU off; Sanaa: *"Well add the gpu ones once i turn the gpu back on later."* |
| VMFLGPU008 | 247 | Radiative heat transfer, participating medium | 2 | VMFL066 | NUM | Non-dim heat flux vs x* (vs analytic) — **profile** | chtMultiRegion + fvDOM | ABSENT | small | Y* | — | **`DEFERRED`** — GPU off; Sanaa: *"Well add the gpu ones once i turn the gpu back on later."* |
| VMFLGPU009 | 249 | Two-phase Poiseuille flow | 3 | VMFL069 | NUM | Velocity magnitude vs position — **profile** | interFoam | ABSENT | small | Y* | — | **`DEFERRED`** — GPU off; Sanaa: *"Well add the gpu ones once i turn the gpu back on later."* |
| VMFLGPU010 | 251 | Surface-to-surface radiation, concentric cylinders | 2 | VMFL061 | AN | Non-dim T vs normalized radius — **profile** | chtMultiRegion + viewFactor (S2S) | ABSENT | trivial | Y* | — | **`DEFERRED`** — GPU off; Sanaa: *"Well add the gpu ones once i turn the gpu back on later."* |

## Table C — Ansys Forte cases (VMFRT001–007)

All are **Ansys Forte** engine / spray / combustion cases. The lab has **no Forte
solver and no engine-combustion CFD application** on the box; most are `NONE`. Forte
archives ARE present in the canonical home (`VMFRT_v261/`).

| Case | Pg | Title | Dim | Regime / physics | Ref | Quantity & N targets | Lab solver | Arch | Cost | Ladder | Tier (in-scope only) | Scope status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VMFRT001 | 255 | LES in an internal-combustion engine | 3 | LES, IC engine, reacting | EXP | (validation profiles) — **profile** | **NONE** — no LES engine-combustion solver | Forte | large | N — no solver | — | **`OUT OF SCOPE — BY RULING`** — engine combustion / LES spray |
| VMFRT002 | 259 | ECN nonreacting flow — bklraAL4 | 3 | Non-reacting spray, gas-phase | EXP | (spray/gas profiles) — **profile** | reactingParcelFoam (spray, no reaction) — partial / **NONE** | Forte | large | N* — engine spray hard | — | **`OUT OF SCOPE — BY RULING`** — engine combustion / LES spray |
| VMFRT003 | 261 | ECN nonreacting flow — bklfaAL4 | 3 | ECN non-reacting spray | EXP | (spray/gas profiles) — **profile** | reactingParcelFoam — partial / **NONE** | Forte | large | N* | — | **`OUT OF SCOPE — BY RULING`** — engine combustion / LES spray |
| VMFRT004 | 263 | ECN nonreacting flow — bkldaAL4 | 3 | ECN non-reacting spray | EXP | (spray/gas profiles) — **profile** | reactingParcelFoam — partial / **NONE** | Forte | large | N* | — | **`OUT OF SCOPE — BY RULING`** — engine combustion / LES spray |
| VMFRT005 | 265 | ECN reacting flow — jkldaAL4 | 3 | ECN reacting spray combustion | EXP | (combustion profiles) — **profile** | sprayFoam / reactingParcelFoam (hard) / **NONE** | Forte | large | N — no clean solver | — | **`OUT OF SCOPE — BY RULING`** — engine combustion / LES spray |
| VMFRT006 | 269 | Adiabatic compression of air by a reciprocating piston | 3 | Dynamic mesh, transient, ideal gas (no reaction) | AN | Static T & p vs crank angle — **profile/discrete** | rhoPimpleFoam (dynamicMesh) — **feasible** | Forte | small | Y* — mesh-motion + time | `NEVER RUN` | `IN SCOPE` |
| VMFRT007 | 273 | Small-bore direct-injection diesel engine | 3 | Engine combustion (light-duty diesel) | EXP | (engine profiles) — **profile** | **NONE** — no engine-combustion solver | Forte | large | N — no solver | — | **`OUT OF SCOPE — BY RULING`** — engine combustion / LES spray |

---

## 1. Counts

**By dimension (all 95 cases):**

| Dim | VMFL (78) | GPU (10) | RT (7) | Total |
|---|---|---|---|---|
| 2 (2D) | 45 | 9 | 0 | **54** |
| A (2D axisymmetric) | 22 | 0 | 0 | **22** |
| 3 (3D) | 11 | 1 | 7 | **19** |

**By reference type (all 95):** `AN` (analytical) = **26** · `EXP` (experimental) =
**50** · `NUM` (other code / numerical benchmark) = **19**.
- VMFL78: AN 22, EXP 41, NUM 15. · GPU10: AN 3, EXP 3, NUM 4. · RT7: AN 1, EXP 6.

**By regime (VMFL78 `Physics/Models` keyword flags — these overlap):**
- Turbulent (RANS: k-ε / k-ω / SST / RSM / RNG / k-kl): **38**
- Laminar (keyword): **17**
- Heat transfer / conduction / convection / radiation / thermal: **17**
  - of which radiation: **5** (VMFL056, 057, 061, 066, 070) · pure conduction: **3**
    (VMFL029, 050, 059)
- Compressible / supersonic / transonic / shock / inviscid: **13**
- Rotating / MRF / SRF / swirl / moving-wall: **12**
- Multiphase / two-phase / VOF / cavitation / boiling / free-surface / wall-film /
  population-balance: **10**
- Transient / unsteady / dynamic-mesh: **6**
- Species / combustion / reacting: **4**
- Transitional-turbulence: **3**

**Result-comparison form (VMFL78):** discrete Target/Ansys/Ratio tables exist for **21**
cases (001, 002, 003, 005, 007, 010, 017, 021, 022, 024, 034, 035, 036, 045, 050, 051,
059, 063, 064, 072 — plus 006 is a *tabulated profile*). The remaining ~57 compare via
plotted profiles (figures) only — a lab PASS on those needs a digitized profile or a
scalar functional.

**Lab-solver coverage (honest):** cases the box has **NO solver** for, or only a
`BLOCKED`/`NONE` path: **VMFL021, VMFL022** (cavitation — no `interPhaseChangeFoam`),
**VMFL034, VMFL074** (population-balance — no clean native PBM solver), **VMFL072**
(Eulerian wall film — no solver), and **VMFRT001, VMFRT002, VMFRT003, VMFRT004,
VMFRT005, VMFRT007** (Forte engine spray/combustion — no engine-combustion CFD app).
That is **11 cases with no usable lab solver.** A further band is *partial / hard*
(a solver exists but the physics is incomplete or difficult): VMFL025, VMFL049
(combustion via reactingFoam), VMFL026 (real-gas EOS unavailable — perfect-gas only),
VMFL029/GPU004 (anisotropic conduction needs a tensor diffusivity, not native to
laplacianFoam), VMFL039, VMFL067 (RPI wall boiling). Everything else maps to a
first-class OpenFOAM application.

**Archive presence:** Fluent `.wbpz` present for **77 of 78** VMFL cases — **VMFL068 is
the sole missing Fluent archive**. CFX `.def` present for the **37**-case CFX-supported
subset. Forte archives present for all **7** VMFRT. **All 10 VMFLGPU archives are
ABSENT** — no GPU project files were shipped in this set.

---

## 2. First tranche — cheap pipeline-proving cases (VMFL001 fixed as case 1)

Selection rule (from the brief): cheap, an existing lab solver reproduces it, prefer
**analytical** references and a **feasible 3-level ladder**, prefer a **discrete
target** so the gate is a number not a digitized curve. The supervisor has already
chosen **VMFL001** (concentric rotating cylinders, exact White solution) as case 1.
The next four, ranked, deliberately exercise **four different OpenFOAM solver
families** so passing them proves the whole pipeline end to end:

1. **VMFL005 — Poiseuille flow in a pipe** (p. 25, A, laminar, `AN`). Reference
   Hagen-Poiseuille is *exact*; one discrete target (ΔP = 10.24 Pa, Fluent ratio
   0.998); `icoFoam`/`simpleFoam`; trivial cost; axisymmetric wedge refines cleanly
   for a monotone triple. The canonical laminar pipeline test — **strongest #2.**
2. **VMFL003 — Pressure drop, turbulent pipe** (p. 19, A, k-ε, `AN`). One discrete
   target (ΔP = 21744 Pa, Fluent ratio 0.988) against the Moody/friction-factor
   analytic; `simpleFoam` + `kEpsilon`. Extends the pipeline to **turbulence** while
   the target stays a single scalar. Ladder feasible with the y+ band held across
   levels.
3. **VMFL007 — Non-Newtonian flow in a pipe** (p. 29, A, power-law, `AN`). One discrete
   target (ΔP = 60.52 kPa, Fluent ratio 0.998) against Schaum's analytic; exercises
   **`nonNewtonianIcoFoam` (powerLaw viscosity)** — a distinct solver/model — trivially
   cheap, monotone ladder.
4. **VMFL050 — Transient heat conduction in a semi-infinite slab** (p. 163, 2D,
   `AN`). Two discrete targets (wall T = 393 K, T at 150 mm = 318.4 K at t = 120 s)
   against the error-function analytic; exercises **`laplacianFoam`** and the
   **transient/conduction** path — a third solver family with an exact reference.
   Ladder feasible on space; note the transient case couples spatial and temporal
   refinement (refine Δt with Δx).

*Alternates if any of the above stalls:* **VMFL010** (2D laminar tee, discrete flow
split 0.887, `simpleFoam`, `NUM` reference), **VMFL036** (axisymmetric laminar sphere
drag, discrete Cd = 1.0895, `NUM`), **VMFL002** (adds the coupled energy equation —
2 targets, `AN`). VMFL004 (Couette) is analytical but its comparison is a *profile*, so
it is a weaker clean-gate candidate and is ranked below the discrete-target four.

Net: the tranche VMFL001→005→003→007→050 proves **icoFoam, simpleFoam(kEpsilon),
nonNewtonianIcoFoam, and laplacianFoam** all end to end, every one against an
analytical reference with a discrete numeric target and a feasible Roache triple.

## 3. Cheapest 3D cases to close the lab's 3D gap (second tranche)

The lab today has **no 3D case with a CONVERGING Roache triple and no 3D PASS against
experiment with a prereg on disk** (`docs/inventory/2026-08-24/LAB_INVENTORY.md`
§2, §7). The cheapest 3D cases with a feasible triple and an experimental **or**
analytical/benchmark reference, ranked:

1. **VMFL078 — 3D lid-driven cubic cavity, Re=1000** (p. 223, 3D, laminar, `NUM`).
   `icoFoam`/`simpleFoam`; a structured hex mesh refines uniformly for the cleanest
   possible 3D triple; the reference (Wang & Wan 2011 FEM benchmark) provides tabulated
   centreline velocities, so the profile reduces to gate-able values. Laminar and
   well-conditioned — **best first 3D.** (The manual runs it on a 279,894-cell
   polyhedral mesh to demonstrate poly accuracy; the lab would use hex.)
2. **VMFL030 — Turbulent flow in a 90° pipe-bend** (p. 111, 3D, RNG k-ε, `EXP`).
   `simpleFoam` (RNGkEpsilon), half-domain by symmetry, structured mesh ladder
   feasible; the Enayet 1982 LDA data is the experimental target (velocity magnitude at
   75° along the bend). Medium cost. **This is the case that most directly closes the
   "3D PASS vs experiment" gap.**
3. **VMFL069 — Two-phase Poiseuille flow** (p. 205, 3D, laminar, `NUM`). `interFoam`
   (interface undeformed — can even be a viscosity-stratified single fluid); analytical/
   FEM reference (Marchandise 2006); laminar and cheap. A lower-risk 3D alternate that
   also feeds VMFLGPU009.

*Heavier 3D options (deferred):* VMFL048 (180° bend, turbulent, EXP), VMFL016
(transition duct, RSM, EXP), VMFL068 (eccentric annulus, RSM, EXP — **but its archive
is ABSENT**), VMFL035/077 (compressor / ship — large). **Caveat for the whole 3D
tranche:** VMFL078/030/069 all compare via *profile plots*, not discrete tables, so
each needs a digitized profile or an agreed scalar functional pinned in the
pre-registration before compute.

---

## 4. Candidate numerics facts for the lab to record (draft N-AV rows — do NOT edit NUMERICS_KNOWLEDGE.md)

Drafted as bullets for the supervisor's read; each cites the manual page.

- **N-AV (Ansys' own accuracy target):** the manual states its goal is *"results
  accuracy within 3% of the target solution"* and reports target and Ansys values to a
  *"consistent number of significant digits"* (§1.3, p. 5; §1.2, p. 4). This is the
  natural default band for a lab reproduction gate on these cases — a lab tolerance
  tighter than 3% would be stricter than Ansys' own stated goal.
- **N-AV (single-instance, not grid-independent):** Ansys explicitly warns these are
  *"single instance simulations using one mesh, one turbulence model, and one
  scenario"* and are *"not validation cases"*; where results are not grid-independent
  it is *"due to the need to limit run time"* (§1.2, p. 4; §1.4, p. 5). Consequence for
  us: **the lab's Roache triple is doing something the manual does not** — the manual
  reports a single grid, so a lab CONVERGING triple is genuinely new information, not a
  reproduction of an Ansys result.
- **N-AV (machine-dependent digits):** the manual notes non-linear/iterative solutions
  *"are among the most likely to exhibit machine-dependent numerical differences"* and
  that a value printed as 0.01234 may appear as 0.012335271 elsewhere (§1.2, pp. 4–5).
  A lab gate should compare at the manual's reported precision, not to spurious extra
  digits.
- **N-AV (ratios far from 1.000 — where even Ansys' own codes disagree):** worth
  recording as the realistic reproduction envelope:
  - **VMFL001** (p. 15): Fluent tangential-velocity ratios fall to **0.978** at r=35 mm
    and CFX to **0.976** — the outermost radius is the hardest point (both codes lose
    ~2–2.5%); Fluent CFX also split (0.991/0.998/0.988/0.976).
  - **VMFL017** RAE 2822 (p. 69): Fluent **drag ratio 0.952**, CFX **lift ratio 0.934**
    — a transonic airfoil is ~5–7% off even for Ansys; a demanding reproduction target.
  - **VMFL035** compressor (p. 123): Fluent **mass-flow ratio 1.026**.
  - **VMFL045** oblique shock (p. 153): Fluent **Mach ratio 1.015, density 0.981**.
  - **VMFL063/064** reattachment length (pp. 193/195): ratios **1.04 / 0.982** — a
    length-scale functional is intrinsically noisier than a point value.
  - **VMFL007** CFX (p. 29): **1.0165**; **VMFL005** CFX **1.024** — the CFX column is
    routinely looser than Fluent on the same case.
- **N-AV (turbulence-model inventory used by Ansys):** across VMFL78 the manual uses
  standard/realizable/RNG **k-ε**, standard **k-ω** and **SST**, **Reynolds-stress
  (RSM)**, and transition models **k-kl** and **Transition SST** — the lab must match
  the *stated model per case* (§1.2's single-model warning), not substitute a default.
- **N-AV (index / page anomaly to flag):** the §1.8 index table (PDF pp. 7–9) lists
  **VMFL036 at "p. 141"**, but the Table of Contents and the case body place VMFL036 at
  **p. 125** (p. 141 is VMFL041). Use the TOC page; the index cell is a manual typo.
  Also the index table's **X-column physics headers are rotated text and are not
  machine-extractable** — regime must be read from each case's `Physics/Models` line.
- **N-AV (mesh statement worth capturing):** VMFL078 discloses its mesh size
  (**279,894 polyhedral cells**, p. 223) — a rare explicit cell count, useful as the
  order-of-magnitude anchor for the lab's 3D lid-cavity ladder sizing.

---

## GAP-CLOSING PRIORITY — the never-run classes, ranked (appended 2026-08-25, `ansys-lane-opus48`)

**Purpose.** Sanaa's priority, relayed by the chief: *where there is a choice, take a
case from a class the lab has NEVER RUN over one that re-covers held ground.* This
section ranks the manual cases that close each of the lab's four **declared gaps** —
compressible/supersonic, 3D, turbulent thermal, and a converging Roache triple outside
the thermal family — so the supervisor can pick the next case on evidence.

**Caveat carried, as instructed.** This priority follows the chief's **reconstruction
of Sanaa's instruction, not her verbatim words**, and is labelled as such. It is a
draft for the supervisor's read, not a dispatch.

**Ranking criterion (multiplicative — a case scores on all four or it falls):**
closes a declared gap **×** has an EXACT/analytical target (which is what lets a row
hold the **V** column) **×** cheap **×** the lab has a working solver on this box.

**Cost bands are ESTIMATES for a full 3-level Roache triple, not measured** — priced
by analogy to VMFL005's laminar triple (4.0 core-min measured) and inflated for
density-based/explicit solvers, which take small time steps to a steady state.
`trivial` < 15 core-min · `small` 15–180 · `medium` 180–1800 · `large` > 1800. Every
one is re-costed in its own pre-registration before compute (CLAUDE.md rule 12).

**Solver column** reads the box's OpenFOAM v2606 application set (per CASE_MAP Table A).

### Gap 1 — compressible / supersonic

| Rank | Case | Pg | Dim | Target type | Solver on box? | Cost band (triple) | Note |
|---|---|---|---|---|---|---|---|
| — | **VMFL051** Prandtl–Meyer expansion | 165 | 2D | **AN** discrete(1), Mach | **yes** rhoCentralFoam | trivial | **IN FLIGHT — assigned to another lane, being pre-registered now. DO NOT TOUCH `cases/ansys_verification/VMFL051/`.** |
| **1** | **VMFL045** oblique shock over a ramp | 153 | 2D | **AN** discrete(3), Mach/T/ρ | **yes** rhoCentralFoam/sonicFoam | trivial | Inviscid, monotone (ladder `Y`, not `Y*`); exact oblique-shock relations for all three targets. **Recommended second case — see below.** |
| 2 | **VMFL046** normal shock in a C–D nozzle | 155 | 2D | **AN** (profile → gate a scalar: exit Mach / shock x) | **yes** rhoCentralFoam/sonicFoam | small | Analytic 1-D area–Mach + normal-shock relations; profile, so gate a functional. |
| 3 | **VMFL075** supersonic circular-arc bump | 217 | 2D | NUM (profile) | **yes** rhoCentralFoam | small | Inviscid; reference is a benchmark, not analytic — weaker V. |
| 4 | **VMFL044** supersonic nozzle | 149 | A | EXP (profile) | **yes** rhoSimpleFoam/sonicFoam | small | Experimental wall-pressure ratio; V would be correlation at best. |
| 5 | **VMFL017** RAE 2822 transonic airfoil | 69 | 2D | EXP discrete(2), Cd/Cl | **yes** rhoSimpleFoam(SST) | small | Turbulent + shock + y+ band; even Ansys is 5–7 % off (Fluent Cd 0.952). Demanding. |
| 6 | **VMFL041** transonic airfoil | 141 | 2D | EXP (profile) Cp | **yes** rhoSimpleFoam(SST) | small | Shock + y+. |
| 7 | **VMFL018** shock reflection | 71 | 2D | EXP (profile) | **yes** sonicFoam/rhoCentralFoam | small | Afterbody p + heat flux; profile. |
| 8 | **VMFL053** compressible turbulent mixing layer | 171 | 2D | EXP (profile) | **yes** rhoSimpleFoam(RNG k-ε) | small | Profile. |
| 9 | **VMFL060** transitional supersonic rearward step | 187 | 2D | EXP (profile) | **partial** transition SST | small | Shock + transition model. |
| 10 | **VMFL020** adiabatic piston compression | 79 | 2D | **AN** (profile) T,p vs t | **yes** rhoPimpleFoam+dynamicMesh | small | Analytic target, but transient + moving mesh — harder tooling. |
| — | **VMFL026** real-gas shock tube | 99 | 3D | NUM (profile) | **BLOCKED** real-gas EOS absent | medium | Perfect-gas only; real-gas limb cannot run. Also a 3D case. |

### Gap 2 — 3D

| Rank | Case | Pg | Dim | Target type | Solver on box? | Cost band (triple) | Note |
|---|---|---|---|---|---|---|---|
| **1** | **VMFL078** lid-driven cubic cavity, Re=1000 | 223 | 3D | NUM (benchmark; Ku-type) | **yes** icoFoam/simpleFoam | medium | Laminar, **clean structured-hex triple** (ladder `Y`); the cleanest 3D converging-triple candidate. Reference is a benchmark, not analytic → V = correlation/benchmark, not exact. Manual discloses 279,894 cells (sizing anchor). |
| 2 | **VMFL069** two-phase Poiseuille | 205 | 3D | NUM (profile) | yes interFoam | small | Laminar, fixed interface; benchmark reference. |
| 3 | **VMFL030** 90° pipe bend | 111 | 3D | EXP (profile) | yes simpleFoam(RNG k-ε) | medium | Turbulent, half-domain, y+ band. |
| 4 | **VMFL048** 180° pipe bend | 159 | 3D | EXP (profile) | yes simpleFoam(SST) | medium | Turbulent, y+. |
| 5 | **VMFL035** 3D axial compressor | 123 | 3D | NUM discrete(2) | yes rhoSimpleFoam(MRF) | large | **Also compressible** (closes two gaps) but turbomachinery + MRF + large cost. |
| 6 | **VMFL015** engine inlet valve | 61 | 3D | EXP (profile) | yes simpleFoam | large | Costly. |
| 7 | **VMFL016** transition duct (RSM) | 65 | 3D | EXP (profile) | yes simpleFoam(RSM) | large | RSM, costly. |
| 8 | **VMFL077** ship free surface (VOF) | 219 | 3D | EXP (profile) | yes interFoam | large | Costly VOF. |
| — | **VMFL068** eccentric annulus (RSM) | 203 | 3D | EXP (profile) | yes simpleFoam(RSM) | medium | **ARCHIVE ABSENT** — no `.wbpz` anywhere in the set. |

### Gap 3 — turbulent thermal

| Rank | Case | Pg | Dim | Target type | Solver on box? | Cost band (triple) | Note |
|---|---|---|---|---|---|---|---|
| **1** | **VMFL028** turbulent heat transfer, pipe expansion | 107 | A | EXP (profile) Nusselt | **yes** rhoSimpleFoam / simpleFoam+energy | small | Cheapest turbulent-thermal; axisymmetric wedge (note the wedge-area finding below). |
| 2 | **VMFL013** turbulent + heat, backward-facing step | 51 | 2D | EXP (profile) Nusselt | yes rhoSimpleFoam | small | Reattachment + heated wall; y+ band. |
| 3 | **VMFL052** turbulent natural convection, tall cavity | 167 | 2D | EXP (profile) | yes buoyantSimpleFoam | small | Buoyancy + y+. |

**All three are EXP profiles — none has an analytical target**, so none can hold the
**V** column as `exact`; V would be `correlation` at best and the row's ceiling is
GATE REACHED / SURVEYED, not HOLDS. This gap is real but cannot be closed to HOLDS
from the manual alone.

### Gap 4 — a converging Roache triple OUTSIDE the thermal family

**Already partially closed.** VMFL001-R2 (laminar rotating cylinders) and VMFL005
(Poiseuille) each provide a CONVERGING triple outside the thermal family. To broaden
into *new physics classes* with a converging triple:

| Rank | Case | Pg | Dim | Target type | Solver on box? | Cost band (triple) | Note |
|---|---|---|---|---|---|---|---|
| **1** | **VMFL045** oblique shock | 153 | 2D | **AN** discrete(3) | yes rhoCentralFoam | trivial | Inviscid, monotone triple; **also closes Gap 1**. Best two-gap-for-one pick. |
| 2 | **VMFL078** lid-driven cubic cavity | 223 | 3D | NUM benchmark | yes icoFoam | medium | Clean hex triple; **also closes Gap 2**. |
| 3 | **VMFL036** laminar flow past a sphere, Re≈50 | 125 | A | NUM discrete(1) Cd | yes simpleFoam(axisym) | small | Monotone; benchmark reference. |
| 4 | **VMFL063 / VMFL064** reattachment length | 193/195 | 2D | EXP discrete(1) LR | yes icoFoam/simpleFoam | small | Laminar, gate on a length functional (noisier). |

### The recommended SECOND case — VMFL045 (after the in-flight VMFL051)

**Run VMFL045 (oblique shock over an inclined ramp, p. 153) next.** It is the only
other case that scores on **all four** ranking factors at once:

1. **Closes a declared gap — two of them.** Compressible/supersonic **and** a
   converging Roache triple outside the thermal family, in one case.
2. **EXACT analytical target.** The downstream Mach number, temperature and density
   come from the exact oblique-shock relations (θ–β–M, Rankine–Hugoniot) — a
   `discrete(3)` target, so the **V** column can hold `exact`, unlike the profile-only
   supersonic cases. Being **inviscid**, its converging triple's Richardson extrapolate
   can be expected to land on the exact value (no wall-model or wedge-area limb like
   VMFL005's), making it a genuine HOLDS candidate rather than a GATE REACHED.
3. **Cheap.** Inviscid, 2D, trivial cost band; a full triple is a few tens of
   core-minutes at most, well under the pre-authorised ceiling.
4. **The lab has the solver.** rhoCentralFoam (density-based, shock-capturing) is on
   the box; VMFL045's CASE_MAP ladder is `Y` (clean monotone), not `Y*`.

And it is the **natural sibling of the in-flight VMFL051** — same solver
(rhoCentralFoam), same inviscid-supersonic class — so the tooling, mesh style and
grading harness built for VMFL051 transfer directly, cutting VMFL045's setup cost.
VMFL078 is the strongest **3D** pick and should follow once a compressible case holds,
but its reference is a benchmark (V = benchmark, not exact) and its cost is `medium`,
so it ranks behind VMFL045 for a *next* case under the stated criterion.

### A note that bears on every axisymmetric (`A`) case above

VMFL005 (axisymmetric wedge) showed that an OpenFOAM wedge under-represents the true
circular cross-section by the factor **sin(t)/t = 0.99873 at t = 5°** (a 0.127 % area
deficit), which contributes an estimated **~a quarter to ~half** of that case's
0.4979 % deviation from the exact reference (full arithmetic in
`docs/ansys_verification/COVERAGE_ROWS.md`). Any axisymmetric case run against an
**exact** target (VMFL002, VMFL007, VMFL028, VMFL036, VMFL044, VMFL058, VMFL073,
VMFL076) inherits this geometric bias and should either use a **smaller wedge angle**
to shrink it or **carry it explicitly** in the pre-registration's error budget. This
is the pending numerics candidate in `docs/ansys_verification/RECORDS_DRAFTS.md`.
