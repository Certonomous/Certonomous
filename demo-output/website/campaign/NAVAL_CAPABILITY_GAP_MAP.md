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

**Build string:** `build=_481094f-20260618`. **Two things follow.** First, the
F7a run-log banner is **byte-identical** to this build, so
`F7_marine_free_surface.md`'s claim of *"vanilla OpenFOAM v2606, native (no
Docker)"* is **verified against the logs, not taken on trust**. Second, the
installed Debian package is **`2606.0~rc2-1` — a release candidate**, not a
final release. Nothing observed here is attributable to that, but a naval gate
built on an RC should say so on its face, and this is where it is said.

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
| **Relaxation zones** (zone-based wave generation/absorption) | **ABSENT** | Absorption is patch-local only: `activeAbsorption` at the generating patch plus exactly one `shallowWaterAbsorption` outlet model. **This is the one absence with real methodological weight — see below.** |
| **Any tutorial coupling waves to a hull** | **ABSENT** | Every one of the 15 wave tutorials is an empty 2-D flume: `find` for `*.stl*`/`triSurface` under the waves tree returns nothing. `DTCHull`/`DTCHullMoving` have **no `constant/waveProperties`** — their `constant/` holds only `dynamicMeshDict`, `g`, `hRef`, `transportProperties`, `turbulenceProperties`. **A ship-in-waves case is new construction, not a template edit.** |
| **`waves2Foam`** | **ABSENT** | **PC3** |
| **`olaFlow` / `olaFoam` / `IHFOAM`** | **ABSENT** | **PC3** |

**On relaxation zones — the absence that actually bites.** Most published
added-resistance and seakeeping CFD generates and absorbs waves in *relaxation
zones*: spatial regions where the solution is blended toward a target wave
field. That approach is **unavailable to us**, in either the ESI-native form
(no such zone model in `libwaveModels.so`) or the third-party form
(`waves2Foam`/`olaFlow` absent). We would be doing patch-based generation with
patch-local active absorption, which is a **different numerical method from the
one the literature we would compare against used**. That is not a blocker, but
it is a real methodological divergence and any added-resistance claim must
disclose it rather than compare as if like-for-like.

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
| S6 | Irregular seas / spectral added resistance | **NOT REACHABLE without new development** | Two absences compound: **no named spectra** and **no relaxation zones** (§3). See below |

**The one flat "cannot" on this page, and what it would take to change it.**
**Added resistance in irregular seas is out of reach without new development.**
That is not a configuration gap; it is two missing pieces of machinery:

1. **A spectrum discretiser we write ourselves** — JONSWAP or
   Pierson-Moskowitz sampled into the explicit `wavePeriods` /
   `waveHeights` / `wavePhases` / `waveDirections` component tables
   `irregularMultiDirectional` demands. Perhaps a day of work, plus a
   validation against a published spectrum, and it is precisely the
   unchecked-helper hazard docket B6 names.
2. **A wave-absorption method that survives a broadbanded sea.**
   `shallowWaterAbsorption` at a single outlet patch is the only absorber we
   have, and it is the piece most published irregular-sea work replaces with a
   relaxation zone. Whether patch-local absorption holds up against a
   multi-frequency train is **unknown to us and untested**, and it is the
   genuine technical risk — a reflecting outlet contaminates the very mean
   force added resistance is measured from.

Regular-wave added resistance (S5) is reachable. Spectral (S6) is not, today,
and no proposal on this line should imply otherwise.

**S5 is where the genuine methodological risk sits**, and it is a
*measurement-definition* risk of exactly the kind `F7a_REGATE_SPEC.md` was
written to retire: an averaging window and a transient cut-off that a later
reader can satisfy two ways will produce an added-resistance number that cannot
be adjudicated. **Any added-resistance proposal must pin its averaging
contract before it runs.** That lesson is already paid for; it should not be
paid for twice.

---

## 6. Reference data and geometry availability

### 6.1 Geometry we already hold, verified on disk

`ls /usr/lib/openfoam/openfoam2606/tutorials/resources/geometry/`:

| File | Size | Hull |
|---|---|---|
| `wigley.stl.gz` | 301,385 B | **Wigley parabolic hull** |
| `wigley-scaled-oriented.stl.gz` | 303,689 B | Wigley, pre-scaled and oriented |
| `DTC-scaled.stl.gz` | 3,525,029 B | Duisburg Test Case container ship |

**The Wigley hull geometry ships with OpenFOAM.** That removes the geometry
acquisition risk from rung (b) entirely and was not previously recorded
anywhere in this campaign.

### 6.2 Reference data — verified this session by a dedicated literature pass

Each row records how it was checked. Anything not checked is labelled so.

| Case | Source | Access | Numbers | Verified how |
|---|---|---|---|---|
| **Wigley** | Kajitani et al. 1983, 17th ITTC, DTIC `ADP003037` | **Free** | Wave profile and hull pressure coefficients **tabulated**; **CT/Cw/Cwp vs Fn is FIGURE-ONLY** | Full text read |
| **Wigley (tabulated CT)** | MDPI *Fluids* **9(11) 266**, citing Bai & McCarthy 1979 | **Open** | Fr 0.250 → CT 0.003340; 0.316 → 0.003620; 0.408 → 0.004090 | Read |
| **KCS** | Tokyo 2015 workshop, `vary_Fr_2-1.xls` | **Fully open, no registration** | **Six** Froude numbers 0.108–0.282 with CT, sinkage at FP/AP, mean sinkage, trim. Design Fn 0.260, scale 1:31.59, Lpp 7.2786 m. Geometry IGES downloadable | Spreadsheet parsed; IGES route verified |
| **DTMB 5415** | ITTC 27th Resistance Committee report | Report **open** | Tabulated CT, sinkage, trim at Fr 0.1 / 0.28 / 0.41 across **eleven** towing tanks | Read |
| **DTMB 5415 geometry** | — | **NO VERIFIED OPEN ROUTE** | — | ITTC-cited navy host **DNS-dead**; simman2014 **registration-walled**; simman2008 **TLS cert mismatch** |
| **Propeller PPTC / VP1304** | SVA Potsdam Report **3752** | **Free with attribution** | Full J / KT / 10KQ / η tables **plus** polynomial fits | Read |
| **Propeller KP505** | — | Geometry available | **No open tabulated open-water data found** | Searched, not found |
| **Wageningen B-series** | Oosterveld & van Oossanen 1975 | **Not openly obtainable** | — | Searched, not found |

### 6.3 Three data hazards that decide gate verdicts, recorded before any gate is written

These are the same defect class `F7a_REGATE_SPEC.md` was written to retire —
prose that reads unambiguous until someone tries to reproduce it.

1. **SVA Report 3752 contains FOUR differently-corrected open-water tables, and
   they disagree materially.** A propeller gate that cites "SVA 3752" has
   **not named its reference** — it has named a document containing four
   answers. **Any propeller gate spec must name which table, by its
   correction**, exactly as the F7a spec names its threshold and station set.
2. **The Wigley tables are a 1983 scan with unreliable OCR.** Values must be
   read off the **page images**, not lifted from the extracted text layer.
3. **Wigley therefore has TWO independent wrong-number entry paths**: OCR of a
   scan (for the tabulated quantities) *and* manual digitisation of a plot (for
   CT/Cw vs Fn, which is figure-only). Both are labour and both are places a
   wrong number enters. Priced as such in the proposals, not waved through.

### 6.4 The blocker, stated as a blocker

**DTMB 5415 has tabulated reference data and no verified open geometry route.**
Every download path checked this session failed: DNS-dead host, registration
wall, TLS certificate mismatch. **A credibility case whose hull we cannot
obtain is not stageable**, and the H3 staging plan (`F7c_DTMB5415_STAGING.md`)
opens with a stage-zero gate on exactly this rather than assuming the geometry
will appear.

---

## 6A. Limits on the negatives — what this map could not check

Stated so the absences in §3 are not read as stronger than they are.

- **The Docker daemon refuses this user and `/var/lib/docker` is unreadable.**
  A containerised `waves2Foam` or `olaFlow` image **cannot be ruled out** by
  the checks run here. §3's third-party absences are established for the host
  filesystem and the repo, **not** for container images. This is a real limit
  on the negative, not a formality. It was **not** escalated to `sudo`.
- Wave-model behaviour is inferred from symbol tables, dictionaries and
  tutorials. **Nothing was executed**, so every §2 entry is a claim that the
  code is installed, never that it produces a correct wave here (§4, §7 W1).
- The install is a **release candidate** (`2606.0~rc2-1`).

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
