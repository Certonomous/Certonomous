# Naval capability gap map — what this lab can and cannot do for marine free-surface work

**Written 2026-08-11** for docket §G item G4 (Katie's §8, H4 third item).
**Zero compute.** No solver, mesher or wave utility was launched to produce it.

**Frame for every claim below:** machine-local OpenFOAM install at
`/usr/lib/openfoam/openfoam2606`, `api=2606`, `patch=0`, `WM_PROJECT_VERSION=v2606`
(ESI/OpenCFD, not the Foundation fork), read from
`/usr/lib/openfoam/openfoam2606/META-INFO/api-info` and `etc/bashrc`; repo
`/home/ubuntu/Certonomous` at commit `1393b8b4`. Repo searches use
`git ls-files` or `find`, never bare `grep -r` — which here execs
`ugrep --ignore-files` and silently skips `.gitignore`d paths.

---

## 0. The headline, stated against the expectation it overturns

`docs/DOCKET.md` G4 records the assumption behind this exercise:
seakeeping / added resistance *"needs wave BCs **we may not have**"*, with the
instruction that the gap map is the product and that an agent who quietly
substitutes something else has destroyed the deliverable.

**The assumption is refuted by measurement. We have wave boundary conditions.**
This install carries the full ESI `waveModels` framework: nine wave theories,
the `waveAlpha` and `waveVelocity` patch fields, active absorption, five
physical wave-maker types, fifteen wave tutorials, 6-DOF rigid-body motion,
overset multiphase, and a complete container-ship free-surface resistance
tutorial with a moving-hull variant.

Katie's instruction cuts both ways: *missing is the answer if it is the true
one* — and **present is the answer here, because that is the true one.** The
honest deliverable is not a shortage; it is a precise inventory, and the real
gap turns out to sit somewhere else entirely (§4).

---

## 1. Method, and the positive controls that make the negatives credible

Every "absent" below is paired with a control showing the identical command
finds a known-present thing. A negative without one is not evidence.

| # | Control | Result |
|---|---|---|
| **PC1** | `find $R/platforms -name "*.so"` — the method used to look for wave libraries | Finds 162 `.so` files including `libsampling.so`, `libtwoPhaseMixture.so`. Method works. |
| **PC2** | Direct `-f` test at the same `bin/` path used to declare `setWaves` absent | `setWaves` **NOT FOUND**; `interFoam`, `snappyHexMesh`, `blockMesh`, `setFields` **all FOUND** at that same path. |
| **PC3** | `find / -maxdepth 7 -iname "*<toolbox>*"` — the method used for third-party toolboxes | Returns nothing for `waves2Foam`/`olaFlow`/`IHFoam`; the identical method returns `/usr/lib/openfoam/openfoam2606/src/waveModels` for a known-present name. |
| **PC4** | `git ls-files -z \| xargs -0 grep -l` — the method used to declare no repo wave usage | Returns **0** files for `waveAlpha\|waveVelocity\|waveModel`; the identical pipeline returns **1,825** files for `alpha.water` and **91** for `interFoam`. |
| **PC5** | `find . -name <dict>` — the method used to declare no `waveProperties` in the repo, gitignored paths included | Returns **0** for `waveProperties`; identical method returns **345** for `transportProperties`. |

---

## 2. PRESENT — verified, with the evidence

### 2.1 Wave generation

`libwaveModels.so` at
`/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/lib/`.
Classes read from the binary's own symbol table (`nm -DC`), not from
documentation:

| Wave theory | Symbol |
|---|---|
| Stokes I, II, V | `waveModels::StokesI`, `::StokesII`, `::StokesV` |
| Cnoidal | `waveModels::cnoidal` |
| Solitary — Boussinesq, Grimshaw, McCowan | `waveModels::Boussinesq`, `::Grimshaw`, `::McCowan` |
| Stream function | `waveModels::streamFunction` |
| Irregular, multi-directional | `waveModels::irregularMultiDirectional` |

### 2.2 Wave boundary conditions and absorption

- **`waveAlphaFvPatchScalarField`** and **`waveVelocityFvPatchVectorField`** —
  present in the same library. Used as `type waveAlpha;` / `type waveVelocity;`
  on an inlet patch, driven by `constant/waveProperties`.
- **Active absorption at the generating patch**: `activeAbsorption yes;`
- **Absorbing outlet**: `waveModels::shallowWaterAbsorption`.
- **`rampTime`** for smooth start-up.

Verified against a real dictionary, not recalled —
`tutorials/multiphase/interFoam/laminar/waves/stokesI/constant/waveProperties`
selects `waveModel StokesI`, `waveHeight 0.05`, `wavePeriod 3.0`,
`activeAbsorption yes`, with `outlet { waveModel shallowWaterAbsorption; }`,
and `0.orig/alpha.water` sets `inlet { type waveAlpha; }`.

### 2.3 Physical wave-makers (moving-boundary generation)

Fifteen tutorials under
`tutorials/multiphase/interFoam/laminar/waves/`: `stokesI`, `stokesII`,
`stokesV`, `cnoidal`, `solitary`, `solitaryGrimshaw`, `solitaryMcCowan`,
`streamFunction`, `irregularMultiDirection`, `mangroveInteraction`,
`waveMakerPiston`, `waveMakerFlap`, `waveMakerSolitary`,
`waveMakerMultiPaddlePiston`, `waveMakerMultiPaddleFlap`.

### 2.4 Rigid-body motion — the seakeeping half

All present as libraries: `libsixDoFRigidBodyMotion.so`,
`librigidBodyDynamics.so`, `librigidBodyMeshMotion.so`, `libdynamicFvMesh.so`,
`libdynamicMesh.so`, `liboverset.so`.

Solvers present: `interFoam`, `interIsoFoam`, `interPhaseChangeDyMFoam`,
**`overInterDyMFoam`** (overset + multiphase + dynamic mesh), plus
compressible variants. Overset floating-body tutorials exist:
`floatingBody`, `floatingBodyWithSpring`, `rigidBodyHull`.

### 2.5 A working ship-resistance template — better than expected

`tutorials/multiphase/interFoam/RAS/DTCHull` and **`DTCHullMoving`** — the
Duisburg Test Case container ship. `DTCHull` carries `snappyHexMesh` setup,
`surfaceFeatureExtract`, six staged `topoSetDict`/`refineMesh` passes, RAS
turbulence, and a `forces` function object on the `hull` patch with
`rhoInf 998.8` and `CofR (2.929541 0 0.2)`.

`DTCHullMoving` adds `constant/dynamicMeshDict` with `rigidBodyMotion`, a
`Newmark` solver, `mass 412.73`, `inertia (40 0 0 921 0 921)`, and a
`composite` joint of `Pz` (heave) + `Ry` (pitch) — **exactly the two degrees of
freedom a resistance-with-sinkage-and-trim case needs.** A `dynamicMeshDict.sixDoF`
alternative sits beside it.

This is a directly adaptable template for KCS and DTMB 5415, and it materially
lowers the cost estimate for both.

### 2.6 Force measurement

`etc/caseDicts/postProcessing/forces/` ships `forces`, `forcesIncompressible`,
`forceCoeffs` and their `.cfg` forms — the machinery a resistance coefficient
is extracted with.

---

## 3. ABSENT — verified, each with its control

| Capability | Verdict | Evidence and control |
|---|---|---|
| **`setWaves` utility** (initialise the *interior* field with a wave solution) | **ABSENT** | Not in `bin/`; `find $R -name "setWaves*"` and `find / -maxdepth 6 -name setWaves -type f` both return nothing. **PC2**: same path test finds `interFoam`, `blockMesh`, `snappyHexMesh`, `setFields`. |
| **Named spectra** — JONSWAP, Pierson-Moskowitz, Bretschneider | **ABSENT as generators** | No matching symbol in `libwaveModels.so`. `irregularMultiDirectional` instead takes **explicit component tables** — the tutorial supplies 57 `wavePeriods` rows × 26 directions, listed literally in the dictionary. |
| **`verticalDamping` / `isotropicDamping` fvOptions** (Foundation-fork relaxation-zone damping) | **ABSENT** | `libfvOptions.so` symbols are `fv::velocityDampingConstraint` and `fv::acousticDampingSource` only. Absorption here is patch-based, not zone-based. |
| **`waves2Foam`** | **ABSENT** | **PC3** |
| **`olaFlow` / `olaFoam` / `IHFOAM`** | **ABSENT** | **PC3** |

**On `setWaves` — what its absence actually costs.** Without it a wave case
must start from still water and ramp (`rampTime`), so the domain has to be
swept by the wave train before any measurement window opens. That is
**simulated time, hence compute** — not a blocked capability. It is a cost
item, and it is priced into the seakeeping proposal rather than hidden.

**On named spectra — what their absence actually costs.** Irregular seas are
runnable, but we must discretise the target spectrum ourselves and emit the
component table. That is a scripting task of maybe a day, not a capability
gap — and it must be **validated against a published spectrum**, because a
hand-rolled discretisation is exactly the kind of unchecked helper that docket
B6 warns about.

---

## 4. THE REAL GAP — installed is not exercised

This is the finding that matters, and it is not the one the docket anticipated.

| Question | Answer | Frame |
|---|---|---|
| Tracked repo files referencing `waveAlpha`, `waveVelocity` or `waveModel` | **0** | `git ls-files` + `/usr/bin/grep -l`; **PC4** finds 1,825 files with `alpha.water` and 91 with `interFoam` by the identical pipeline |
| `waveProperties` dictionaries anywhere in the repo, gitignored paths included | **0** | `find`; **PC5** finds 345 `transportProperties` by the identical method |
| Repo cases using 6-DOF or overset for a marine body | **0** found by the above | same frame |
| Naval free-surface cases the lab has actually run | **one** — F7a dam break, and its gate **FAILS** (`F7a_REGATE_SPEC.md` §3) | — |

**Per docket B7 — "configured is not active; log-verified or it is not
evidence" — this lab has never once exercised its wave machinery.** Every
capability in §2 is a property of the installation, not a demonstrated property
of this lab. The honest statement of our position:

> We possess the boundary conditions. We have never generated a wave, never
> moved a hull, and our single free-surface gate does not pass.

The gap is not in the software. It is that **nothing between "the dam break
fails its gate" and "added resistance in irregular seas" has ever been
attempted**, and the ladder rule blocks (b) and (c) behind a rung that fails.

---

## 5. Capability ladder for seakeeping / added resistance, with the gap at each rung

Ordered by dependency. "Gap" is what is missing *for us*, not for OpenFOAM.

| Rung | Needs | Have it? | Gap |
|---|---|---|---|
| S0 | A passing free-surface gate | **NO** — F7a FAILS at +11.0% | The blocking item. See `F7a_REGATE_SPEC.md` §4 |
| S1 | Steady calm-water ship resistance | Machinery **yes** (`DTCHull` template, `forces`, snappy) | Never run here. Needs a hull, a reference dataset, a mesh ladder |
| S2 | Sinkage and trim (2-DOF) | Machinery **yes** (`DTCHullMoving`, `rigidBodyMotion`, Pz+Ry) | Never run. Needs mass and inertia for the chosen hull at model scale |
| S3 | Regular-wave generation and absorption | Machinery **yes** (§2.1–2.2) | Never run. Needs a wave-only verification against an analytic Stokes profile before any hull is added |
| S4 | Ship in regular head waves — 2-DOF response | Machinery **yes** | Never run. Needs S1–S3, plus encounter-period run lengths |
| S5 | Added resistance in regular waves | Machinery **yes**; the quantity is a mean force difference | Never run. **The hard part is not the BCs — it is that added resistance is a small difference of two large, noisy, time-averaged forces.** Needs a declared averaging window, a declared transient-rejection rule, and an uncertainty estimate, all pre-registered |
| S6 | Irregular seas / spectral added resistance | Generation **yes**; **named spectra absent** (§3) | Needs our own spectrum discretiser, validated against a published spectrum |

**S5 is where the genuine methodological risk sits**, and it is a
*measurement-definition* risk of exactly the kind `F7a_REGATE_SPEC.md` was
written to retire: an averaging window and a transient cut-off that a later
reader can satisfy two ways will produce an added-resistance number that cannot
be adjudicated. **Any added-resistance proposal must pin its averaging
contract before it runs.** That lesson is already paid for; it should not be
paid for twice.

---

## 6. Reference data availability

Verification of published reference datasets was dispatched as a separate
literature task in this session. **At the time of writing this file that task
had not returned verified citations, so no dataset claim is made here.** Per
this lab's rule, an unverified citation is worse than none.

What can be said from the install alone, and is checked: the **DTC** hull
geometry ships inside the OpenFOAM tutorial as an STL under
`tutorials/resources/geometry/`, so DTC is the one hull for which we
demonstrably hold geometry today without an external download. Whether open
DTC *experimental* data is fetchable is **not established here**.

Reference-data verification for Wigley, DTMB 5415, KCS and propeller
open-water curves is carried in the H4 proposals and remains **an open
prerequisite**, not a settled input.

---

## 7. Compute requests arising, priced

None of these is authorised and none was run.

| # | Run | What it settles | est. core-min | Note |
|---|---|---|---|---|
| W1 | One `stokesI` tutorial case, unmodified | Whether the wave machinery **runs here at all** — converting §2 from an installation property into a lab property, per B7 | **≈ 5–15** | Cheapest possible removal of the §4 gap. Strongly recommended before any naval proposal is funded |
| W2 | Regular-wave verification: wave height and celerity vs the analytic Stokes solution, 3 mesh rungs | Whether we can generate a *correct* wave, not just a wave | **≈ 60–120** | Estimate carries low confidence — no wave case has ever been timed on this machine |
| W3 | `DTCHull` tutorial as shipped | Whether the ship-resistance template runs here, and what a hull case actually costs | **≈ 100–400** | Wide band, and the width is the point: **we have no measured basis for costing a ship case.** Every naval `est_core_min` in the H4 proposals inherits this uncertainty |

**W1 is the single highest-value purchase on this page**, and it is small.
Until it runs, every capability claim in §2 is a claim about a filesystem.
