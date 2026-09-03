# T21 CASE–SOLVER FEASIBILITY PROBE — 2026-09-03

> **THIS IS A FEASIBILITY PROBE, NOT A GRADED RUNG.**
> **No verdict from `CLAUDE.md` rule 1's fixed vocabulary is claimed anywhere in
> this directory.** The finding is **FEASIBLE**, and **`FEASIBLE` is NOT a synonym
> for `PASS`** — nothing here was gated, nothing was graded, no pre-registered
> threshold was tested, and no band, triple or GCI exists for any number below.
> Nothing in this directory may be cited as verification of anything.

**This is NOT `verification/runs/T-family/T21_runs/`, and that directory must stay
ABSENT.** `T21_PREREGISTRATION.md` §1 line 9 (ABSENT REGISTRY) requires
`T21_runs/` and every registered case directory to be measured absent **under a
live planted control, in the committing invocation of the freeze**. Creating
`T21_runs/` — even empty, even to hold this probe — would destroy the condition
that freeze is about to assert. The probe is therefore filed under its own dated
directory and touches nothing of T21's registered run root.

---

## 1. WHY THIS PROBE EXISTS

On 2026-09-03 this team ruled T5's `S_m` arm **`BLOCKED`**.
`chtMultiRegionSimpleFoam` at v2606 opens
`applications/solvers/heatTransfer/chtMultiRegionFoam/solid/createSolidMeshes.H:1`
with `const wordList solidNames(rp["solid"]);` — **unguarded** — and `S_m` was
registered with a `regionProperties` carrying **no `solid` entry at all**, so the
solver died in its constructor. The registered design and the registered solver
were **mutually unsatisfiable as written**, and the pre-compute check that should
have caught it verified the **mesh** and never the **case–solver pair**.

**The lesson: a pre-compute check that verifies the case and not the case–solver
pair will pass a case that cannot start.**

`docs/campaigns/T-family/T21_PREREGISTRATION.md` registers, at §1 lines 126–127,
`regionProperties` = `fluid ()` / `solid (core housing)` — **zero fluid regions**,
the mirror of the `S_m` shape. The freeze was therefore held until the pair was
**measured**, because the two shapes are not obviously the same defect: `S_m`
**omitted** the `solid` key, so `rp["solid"]` threw on a *missing* key, whereas
T21 **declares `fluid ()` explicitly** — the key is *present with an empty list*,
and `HashTable::at()` on a present-but-empty entry may perfectly well succeed.

---

## 2. THE FIVE ARMS

One harness, one shared case tree (`case_tree/`), 1 rank, `endTime 1`,
`writeInterval 1`. Each arm differs from `case_tree/` by **one dictionary entry
or one deleted file**, recorded in its own `ARM.txt`. `rc` was captured **directly
from `$?` on the solver line** — no `|| true` between the command and `$?`, and no
`setsid` wrapper (both are measured traps in this lab; the second returns 0 for
every outcome).

| arm | `constant/regionProperties` → `regions ( … )` | rc | outcome |
|---|---|---:|---|
| **A — the T21 shape** | `fluid ()  solid (core housing)` | **0** | no `Create fluid mesh` line at all; `Create solid mesh for region core` / `… housing`; `Time = 1`; `Min/max T: 300 350` (core) then `300 334.647` (housing); one `ExecutionTime` line; **`End`**; wrote `1/core/{T,p}` and `1/housing/{T,p}` (preserved as `armA/written_time_1/`) |
| **B — CONTROL: `solid` key removed entirely (the `S_m` shape)** | `fluid ()` | **1** | `FOAM FATAL ERROR … solid not found in table.  Valid entries: 1(fluid)` |
| **C — DISCRIMINATOR: `fluid` key removed entirely** | `solid (core housing)` | **1** | `FOAM FATAL ERROR … fluid not found in table.  Valid entries: 1(solid)` |
| **D — arm A minus `constant/g`** | as arm A | **1** | `FOAM FATAL ERROR … cannot find file "…/constant/g"` |
| **E — arm A minus the top-level `system/fvSolution`** | as arm A | **1** | `FOAM FATAL ERROR … cannot find file "…/system/fvSolution"` |

### Where each error came from

All paths under `/usr/lib/openfoam/openfoam2606/`.

| arm | raised at | reached from |
|---|---|---|
| B | `src/OpenFOAM/lnInclude/HashTableI.H:51` (`HashTable::at`) | `applications/solvers/heatTransfer/chtMultiRegionFoam/solid/createSolidMeshes.H:1` |
| C | `src/OpenFOAM/lnInclude/HashTableI.H:51` (`HashTable::at`) | `applications/solvers/heatTransfer/chtMultiRegionFoam/chtMultiRegionSimpleFoam/fluid/createFluidMeshes.H:1` |
| D | file-not-found on `constant/g` | `…/chtMultiRegionSimpleFoam/fluid/createFluidFields.H:26` — `meshObjects::gravity::New(runTime)`, **at file scope, above the `forAll` that opens at `:29`**; constructed `IOobject::READ_MODIFIED` per `src/finiteVolume/cfdTools/general/meshObjects/gravity/gravityMeshObject.C:43-55` |
| E | file-not-found on `system/fvSolution` | `…/chtMultiRegionFoam/include/createCoupledRegions.H:3` — `fvSolution solutionDict(runTime);`, read unconditionally before any region loop |

---

## 3. WHAT THE TABLE ESTABLISHES THAT READING THE SOURCE COULD NOT

**1. The zero is evidence, because the harness was shown able to produce a
non-zero.** Arm A's `rc = 0` comes off a harness that returned `rc = 1` on **four**
sibling arms differing from it by one entry or one file. **A probe that cannot
produce a failure has not demonstrated a success.** This one produced four. That
is `CLAUDE.md` rule 3's principle — a zero from a reader not shown able to see a
non-zero is not evidence — applied to a solver invocation rather than to a
comparator.

**2. Arm B is not merely a control; it is the positive discriminator, and it is
the single most load-bearing line in this directory.** Its error names the valid
entries it *did* find: **`1(fluid)`**. So the `fluid` key was present,
`rp["fluid"]` at `createFluidMeshes.H:1` **returned an empty list WITHOUT
throwing**, the zero-length `forAll` ran, and only the **later** `rp["solid"]`
fired. Arm C shows the other side: remove the key and the very same
`HashTableI.H:51` fires on `fluid` instead.

> **Present-but-empty and absent are measurably different.
> The `S_m` failure was a MISSING KEY, not an EMPTY LIST, and T21 does not share it.**

This also confirms the `S_m` ruling was **correctly scoped**: it was not
over-generalised into *"zero-region lists crash."*

**3. Arm A did real physics, not a no-op pass-through.** The `housing` region's
maximum reached **334.647 K** against its own 300 K outer wall — heat crossed the
solid–solid `mapped` interface within a single iteration. A run that started and
then did nothing would not show that.

### Upstream corroboration, independent of this lane

OpenFOAM v2606 **itself ships** a `chtMultiRegionSimpleFoam` tutorial with zero
fluid regions:
`/usr/lib/openfoam/openfoam2606/tutorials/heatTransfer/chtMultiRegionSimpleFoam/jouleHeatingSolid/constant/regionProperties`
reads `fluid ()` / `solid (solid)`. **The zero-fluid shape is a supported upstream
configuration.** This probe extends it from **one** solid to **two solids with a
live conjugate interface**, which is T21's shape and is what the tutorial does not
cover.

---

## 4. THE TWO REQUIREMENTS ARMS D AND E ESTABLISH FOR T21's CASE TREE

**`constant/g` — confirms T21 §6.2, which was already correct.** The draft
registers at lines 781–818 that `constant/g` is mandatory despite there being no
fluid region, citing `createFluidFields.H:26` and `READ_MODIFIED`. That
registration previously rested on a **source reading plus a one-solid precedent**
(T20's `T20_LC_FEAS_20260831T151828Z`). **Arm D is a direct crash in the exact
two-solid zero-fluid shape**, which is stronger.

**Top-level `system/fvSolution` — a requirement the draft did NOT register.** Arm
E shows it is read unconditionally at `createCoupledRegions.H:3`; a bare
`SIMPLE { }` suffices. A full grep of all 1,245 draft lines for `fvSolution` and
`fvSchemes` returned **zero hits**, so it was registered nowhere in the document.
It is registered by the pre-compute amendment that this probe motivated.

---

## 5. WHAT WAS **NOT** TESTED — stated plainly, not left to be assumed

- **Geometry.** A 3-D hex box (20 × 10 × 10 mm, 10 × 5 × 5 cells, split into two
  solid regions). **T21 registers a 2-D axisymmetric wedge at θ = 5.0°, one cell
  circumferentially.** Wedge-ness is orthogonal to the region-list question, but
  **it was not exercised here** and nothing in this directory bears on it.
- **Materials.** Placeholder `heSolidThermo`/`hConst`/`rhoConst`/`constIso`,
  κ 200 vs 20 W/mK — **not** T21's registered representative core and aluminium
  housing properties.
- **No `fvOptions` volumetric source.** T21's `core` carries one. §8.3 of the
  draft asks whether the solver runs to completion *"with `regions ( fluid ()
  solid (core housing) )`, **with an `fvOptions` source on `h` in one solid region**
  and a `mappedWall` couple to the other"*. **This probe answers the region-list
  and `mappedWall` halves of that question and NOT the `fvOptions` half**, which
  remains for `T21_CYL_c` exactly as staged.
- **One iteration.** Nothing about convergence, accuracy, the closed-form
  reference, the Roache triple, the error budget or any gate was measured, and
  nothing here may be cited for any of them.

---

## 6. COST

Five solver invocations plus `blockMesh`, `topoSet` and `splitMeshRegions`, all
**serial at 1 rank**. Wall time per solver arm measured **0 s** by `date +%s`
taken around each invocation — i.e. **below the resolution of the measurement**.

> **Gross cost: under 0.2 core-min. This is an UPPER BOUND, not a measurement.**

No `CLAUDE.md` rule-12 calibration row is owed: a feasibility probe carrying no
pre-registered estimate is not a completed process, and there is nothing to
compare an actual against. This probe's cost is **not** drawn against T21's
registered POINT (9.1901 core-min) or CAP (20.0 core-min), neither of which has
been touched.

---

## 7. CONTENTS

| path | what it is |
|---|---|
| `case_tree/` | the shared case as it stood when the arms ran — `system/` (incl. `blockMeshDict`, `topoSetDict`, per-region `fvSchemes`/`fvSolution`), `constant/` (both region `polyMesh`es, per-region `thermophysicalProperties`, `g`), `0/` (per-region `T` and `p`) |
| `logs_mesh/` | `log.blockMesh`, `log.topoSet`, `log.splitMeshRegions` |
| `armA/` … `armE/` | each arm's `regionProperties`, its solver log, and `ARM.txt` naming its one delta from `case_tree/` and its rc |
| `armA/written_time_1/` | the fields arm A actually wrote at `Time = 1` — the artifact behind the `rc = 0` |

**Reproduction**: from a copy of `case_tree/`, apply one arm's delta, then
`blockMesh` → `topoSet` → `splitMeshRegions -cellZones -overwrite` (already
applied in `case_tree/`) → `chtMultiRegionSimpleFoam`, capturing `$?` on the
solver line directly.
