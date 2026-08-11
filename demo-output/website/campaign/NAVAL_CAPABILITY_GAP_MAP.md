# Naval capability gap map

**Written 2026-08-11. Zero compute.** Katie's H4 brief: *"seakeeping / added
resistance … needs wave BCs we may not have, so the deliverable is the
capability-gap map, honest about what is missing."* The docket (§G4) adds:
*"An agent that discovers we lack the boundary conditions and quietly
substitutes something else has destroyed the deliverable. The map is the
product."*

**Frame for every check below:** machine-local OpenFOAM at
`/usr/lib/openfoam/openfoam2606`, and the git-**tracked** contents of
`/home/ubuntu/Certonomous` at commit `bfbf0523`. Repo searches use `git
ls-files` and `/usr/bin/grep` explicitly, because the shell's `grep` here is
`ugrep --ignore-files` and silently skips gitignored paths.

---

## 0. Headline — the brief's premise is refuted, and that is the finding

**We were told we may not have wave boundary conditions. We do.** The installed
OpenFOAM ships `libwaveModels.so`, nine wave theories, the `waveAlpha` /
`waveVelocity` boundary conditions, physical wavemaker models, 6-DOF rigid-body
motion and overset — fifteen wave tutorial cases in total.

**The gap is one layer up.** This lab has **no tooling that drives any of it**,
and no free-surface case of any kind outside the F7a dam break, which was built
by a 305-line bespoke script in a campaign directory rather than by the product.

So the honest map is not "we lack the physics." It is:

> **The solver can do seakeeping. The lab cannot yet ask it to.**

That is a smaller gap than the brief assumed, and a differently-shaped one. It
is also the more expensive kind to close, because it is our own work rather than
a missing dependency.

**One genuine solver-side absence was found** — the `setWaves` utility — and it
is documented in §2 with its positive control.

---

## 1. What is present — solver side

Every row was checked by the command shown. Nothing here is from recall.

| Capability | Verdict | Evidence |
|---|---|---|
| OpenFOAM version | **v2606, ESI/OpenCFD**, native | `/usr/lib/openfoam/openfoam2606/` — matches the version string in F7a's own `blockMeshDict` headers |
| Wave models library | **PRESENT** | `platforms/linux64GccDPInt32Opt/lib/libwaveModels.so` |
| Wave generation theories | **PRESENT, nine** | `src/waveModels/waveGenerationModels/derived/`: `StokesI`, `StokesII`, `StokesV`, `cnoidal`, `streamFunction`, `Boussinesq`, `Grimshaw`, `McCowan`, `irregularMultiDirectional` |
| Wave boundary conditions | **PRESENT** | `src/waveModels/derivedFvPatchFields/`: `waveAlpha`, `waveVelocity` |
| Irregular / multi-directional seas | **PRESENT** | `irregularMultiDirectional` above, plus tutorial `interFoam/laminar/waves/irregularMultiDirection` |
| Wave absorption | **PRESENT, one model** | `src/waveModels/waveAbsorptionModels/derived/`: `shallowWaterAbsorption` |
| Physical wavemakers | **PRESENT** | tutorials `waveMakerPiston`, `waveMakerFlap`, `waveMakerSolitary`, `waveMakerMultiPaddlePiston`, `waveMakerMultiPaddleFlap` |
| `waveProperties` dictionary support | **PRESENT** | e.g. `tutorials/multiphase/interFoam/laminar/waves/stokesI/constant/waveProperties` |
| 6-DOF rigid body motion | **PRESENT** | `lib/libsixDoFRigidBodyMotion.so`, `lib/librigidBodyDynamics.so`, `lib/libfvMotionSolvers.so`; tutorials `sloshingTank3D6DoF`, `sloshingTank3D3DoF`, `oscillatingBox` |
| Overset | **PRESENT** | `lib/liboverset.so`, solver `overInterDyMFoam` |
| Free-surface solvers | **PRESENT** | `bin/`: `interFoam`, `interIsoFoam`, `interMixingFoam`, `interPhaseChangeDyMFoam`, `overInterDyMFoam`, `compressibleInterDyMFoam` and others |

**Wave tutorial inventory, verbatim** from
`tutorials/multiphase/interFoam/laminar/waves/`: `cnoidal`,
`irregularMultiDirection`, `mangroveInteraction`, `solitary`,
`solitaryGrimshaw`, `solitaryMcCowan`, `stokesI`, `stokesII`, `stokesV`,
`streamFunction`, `waveMakerFlap`, `waveMakerMultiPaddleFlap`,
`waveMakerMultiPaddlePiston`, `waveMakerPiston`, `waveMakerSolitary`.

---

## 2. What is absent — solver side

Each absence carries a **positive control**: a demonstration that the identical
search method finds a known-present thing. An absence without one is not
evidence.

### 2.1 `setWaves` utility — **ABSENT**

- **Search:** `find /usr/lib/openfoam/openfoam2606 -name "setWaves*"` → **no
  output**.
- **Positive control:** `find /usr/lib/openfoam/openfoam2606 -name "setFields"
  -type f` → `…/platforms/linux64GccDPInt32Opt/bin/setFields`. **The same find,
  same root, same depth, returns a binary for a utility known to exist and
  nothing for `setWaves`.**
- **What it costs us.** `setWaves` initialises the *interior* of the domain with
  a wave field. Without it, waves must be generated at the inlet patch and
  allowed to propagate in, which means a longer domain and a longer run before
  the working zone is developed. **This is a cost, not a blocker** — the
  `waveAlpha` / `waveVelocity` BCs do the generation and are present.
- **Not investigated:** whether `setWaves` can be compiled from the shipped
  sources. It is a packaged install; that is a question for whoever owns the
  install, not a claim this map makes either way.

### 2.2 `verticalDamping` fvOption — **ABSENT**

- **Search:** `/usr/bin/grep -rl "verticalDamping" src tutorials` → **no output**.
- **Positive control:** `/usr/bin/grep -rl "limitTemperature" src` → three files
  under `src/fvOptions/corrections/limitTemperature/`. **The same grep, same
  root, finds a known fvOption and nothing for `verticalDamping`.**
- **What it costs us.** `verticalDamping` is the usual way to damp waves toward
  an outlet without a relaxation zone. Its absence, combined with only one
  absorption model (`shallowWaterAbsorption`, whose name states its regime),
  means **outlet wave reflection is the first thing to go wrong** in any
  ship-in-waves case here, and a reflection check belongs in that case's
  feasibility stage.

### 2.3 Third-party wave toolboxes — **NOT ASSESSED IN THIS MAP**

`waves2Foam`, `olaFlow` / `IHFOAM` were delegated to a parallel investigation
whose result had not returned when this map was written. **This map therefore
makes no claim about them in either direction.** Their absence would not change
§0's headline, because the native capability in §1 already exceeds what the
brief assumed.

---

## 3. What is absent — lab side. **This is the real gap.**

| Capability | Verdict | Evidence |
|---|---|---|
| Any SDK workflow that builds a free-surface case | **ABSENT** | `git ls-files \| /usr/bin/grep -iE "wave\|marine\|hull\|free_surface\|interfoam"` returns only F7 campaign artifacts, run logs, and unrelated images (a valve waveform, a submarine render) |
| `interFoam` driven by product code | **ABSENT** | `git ls-files sdk scripts \| xargs /usr/bin/grep -l interFoam` matches only monitoring and audit code: `scripts/check_convergence.py`, `sdk/chief_engineer/compute_audit.py`, `sdk/chief_engineer/lever_echo.py`, `sdk/scripts/is_idle.sh`, keepalive scripts. **Every one of these watches solves; none creates one.** |
| Free-surface case generator | **ONE, bespoke** | `demo-output/website/campaign/F7_runs/make_dambreak.py` — 305 lines, 2D structured `blockMesh`, dam-break only, not parameterised for a hull |
| Hull geometry handling | **ABSENT** | no hull STL/IGES anywhere in `git ls-files`; F8's `constant/triSurface/blade.stl` is a turbine blade |
| Wave BC tooling, dictionaries, or templates in-repo | **ABSENT** | no `waveProperties` under `git ls-files` |
| Any free-surface case other than F7a | **ABSENT** | `git ls-files` shows one free-surface family |

**Positive control for the whole table.** The identical filter shape
(`git ls-files | /usr/bin/grep -iE "mrf"`) returns
`demo-output/website/agenda/proposals/f8-mrf-forces-against-hand-2001.json`,
`campaign/F8_MRF_HAND2001_GATE.md` and `F8_runs/phase6_mrf/constant/MRFProperties`
— a real capability, found by the same method that finds nothing for waves. The
method works; the marine rows are empty because the capability is empty.

---

## 4. What this means for the three H4 proposals

| Proposal | Blocked by a missing capability? | The honest position |
|---|---|---|
| **KCS container ship** | **No.** `interFoam` + `snappyHexMesh` + 6-DOF are all present | Blocked by the **ladder rule** (F7a's gate fails), not by capability. Cost and geometry access are the real questions |
| **Propeller open-water** | **No.** Single-phase, submerged, no free surface — it needs MRF, which F8 exercises | The reuse claim needs checking against what F8 actually is, which is done in the proposal, not asserted here |
| **Seakeeping / added resistance** | **No — and this is the corrected premise.** Wave generation, irregular seas, 6-DOF and overset are all present | Blocked by **absent lab tooling** (§3) and by outlet-reflection control (§2.2). The work is ours to build, not a dependency to acquire |

**The substitution the docket warned against has not been made.** Nothing here
proposes a regular-wave stand-in for irregular seas, a fixed-hull stand-in for
6-DOF, or a 2D stand-in for a hull. Where something is missing it is listed as
missing.

---

## 5. Reference-data availability

Deliberately left to the proposals rather than asserted here. This agent
delegated the literature verification and **it had not returned when this map
was written**, so this map records no dataset claims. Any statement about what
towing-tank data is openly available, tabulated or paywalled belongs beside a
citation someone actually fetched — this lab has been burned by exactly the
opposite. **The absence of this section's content is deliberate and is itself
part of the honest map.**

---

## 6. What this map does not know

- Whether `setWaves` is buildable from the shipped sources (§2.1).
- Whether `waves2Foam` / `olaFlow` are present anywhere on this machine (§2.3).
- Whether `shallowWaterAbsorption` is adequate for a deep-water ship case — its
  name suggests a regime limit, and **no test was run**, because running one
  would be compute this agent does not hold.
- What a 3D hull free-surface case actually costs here. No 3D free-surface case
  has ever been run in this repo, so there is nothing to extrapolate from, and
  no core-min figure appears in this map for that reason.
