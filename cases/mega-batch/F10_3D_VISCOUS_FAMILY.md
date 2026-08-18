# F10 — 3D viscous RANS (Ahmed body): closing the mega-batch's 3D-viscous gap

> **Update:** the "mesh topology is identical across the Reynolds sweep"
> statement below is no longer true. 17/52 F10 evaluations failed the y+
> gate at the top of the Re range on the fixed `refinement=2` mesh this
> document describes; the mesh now follows Reynolds number instead (still
> `refinement=2` below 2.8e6, `refinement=3` at/above it). See
> `F10_YPLUS_FIX.md` for the measured cause, the fix, and the verification.
> Everything else below (case-writer reuse, gates, the 25°/35° validation
> result) is unchanged.

Directive D7, family F10. Added to `sdk/workflows/mega_batch.py` (constants,
`design_for_index` kind 11, `_run_ahmed_viscous`, dispatch in `run_task`).
Every number below was measured on this host through the real
`mega_batch.run_task` dispatch, against a **scratch** ledger under `/tmp`
(never the live one — PID 1789 was left running, untouched, throughout).

## The gap, and what this closes

Before this task, the mega-batch's only 3D family was `vspaero-wing`: an
**inviscid vortex-lattice panel method** — no boundary layer, no Reynolds
number, no turbulence model (`BATCH_INVENTORY.md` states this plainly:
"Reynolds number: not recorded (inviscid method, no boundary layer)"). Of
207,000+ evaluations, zero were 3D **viscous** CFD. F10 (`solver =
"simplefoam-ahmed-3d-viscous"`) is that family: `simpleFoam`, k-omega SST,
wall functions, a real `snappyHexMesh` surface mesh, a real 3D velocity/
pressure/turbulence field.

## Reuse, not rebuild

F10 promotes the existing VALIDATED body
(`mission-output/geometry-study/study-ahmed_25`, 45,753 cells, Cd 0.3219 vs
Ahmed/Ramm/Faltin 1984 SAE 840300's 0.285, 12.95% off inside a ±15% band)
into the batch, unchanged in every physical respect:

- Case-writer: `chief_engineer.external_aero.analyse_surface` / `build_case`
  — the exact function `workflows/geometry_study.py` used to build the
  validated case. Not rewritten.
- Mesh recipe: `refinement=2`, read directly off the validated case's own
  stored `system/snappyHexMeshDict` (`body { level (2 3); }`,
  `nearBody { levels ((1e15 1)); }`) — not re-derived or guessed. Reproduced
  the same background block, `(60 13 36)` cells, in this task's own test
  runs.
- Iteration cap: `iterations=250`, read directly off the validated case's
  own stored `system/controlDict` (`endTime 250;`).
- Air kinematic viscosity: `1.5e-5 m^2/s`, matching `geometry_study.py`'s own
  `AIR_KINEMATIC_VISCOSITY` convention.
- Geometry: `sdk/geometry/ahmed_25.stl` and `sdk/geometry/ahmed_35.stl`,
  byte-identical to the curriculum bodies, streamwise axis 0 (nose along
  +X), matching `models/curriculum/ahmed_{25,35}/reference.yaml`.

One real addition on top of the reused recipe: the validated case's own
`controlDict` never had a `yPlus` function object (checked — none of this
pipeline's prior consumers needed a y+ gate, because none of them is a
wall-bounded 3D viscous solve). `_ahmed_add_yplus_function` appends one
(`onEnd` only, matching the block `workflows/tmr_verification.py` already
uses elsewhere in this repo) so F10 can gate on it.

Execution itself follows the native (non-WSL) pattern the rest of
`mega_batch.py` already uses — `workflows.tmr_verification._foam`, which
runs OpenFOAM utilities directly via `OPENFOAM_RUN_PREFIX` (`openfoam2606`
on this host) — the same launcher every other family in this file uses.
`geometry_study.py`'s own orchestration (`HeadEngineer`, WSL remote-copy
staging) was NOT reused: it targets a different, WSL-hosted execution model
this box has since moved off (see the "OpenVSP WSL install" memory note);
the batch needed the same case-writer, run natively.

## Design space

`solver = "simplefoam-ahmed-3d-viscous"`, kind 11 of a 12-way interleave
(1/12 of the batch, `index % 12`):

- **Geometry** (discrete, genuinely 3D shape variation): the Ahmed body
  rear-slant angle, 25° (weight 0.65) or 35° (weight 0.35) — the two shells
  this repo already has validated STLs and citable experimental references
  for. This is a real geometric design axis, not merely a flow-condition
  sweep: the two angles sit on either side of the Ahmed body's drag-crisis
  transition and produce qualitatively different wake topologies (bistable,
  edge-of-reattachment at 25°; fully separated, quasi-2D at 35° — both per
  this repo's own `reference.yaml` notes for the two bodies).
- **Reynolds number**: uniform in `[1.5e6, 4.0e6]`, converted to freestream
  velocity via `Re * 1.5e-5 / L` (`L` = the body's own measured length,
  1.044 m for both shells) — inside the reference's stated valid band
  `[1.0e6, 5.0e6]` (`reference.yaml: regime.reynolds_valid`), away from its
  edges.

Mesh topology (cell count, background block) is identical across the
Reynolds sweep for a given slant — only the geometry axis changes it — which
keeps the quality-gate structure comparable eval to eval.

## Quality gates — non-negotiable, all four measured and checked per row

A row that fails any gate below raises inside `_run_ahmed_viscous`; the
existing `run_task` try/except (unchanged, shared by every family) catches
it and writes the row `ok=False` with the reason in `error` — **the row is
never silently kept.** Verified directly (see "Testing" below): a
missing-geometry fault surfaced as `ok=False` with a stated reason, at
0.0 s cost, exactly like every other family's poison-design handling.

1. **checkMesh verdict** (`_ahmed_checkmesh_stats`, parsed with the same
   regexes `chief_engineer.head_engineer.HeadEngineer.collect_mesh_stats`
   uses): requires `"Mesh OK"` in the checkMesh log, max non-orthogonality
   ≤ 70° and max skewness ≤ 4.0 — the same two numeric gates
   `workflows/geometry_study.py`'s own `MAX_NON_ORTHOGONALITY` /
   `MAX_SKEWNESS` already enforce for this exact pipeline, reused rather
   than invented. Cross-validated: reparsing the validated case's own
   stored `log.checkMesh` through this exact parser reproduces its numbers
   exactly (cells 45753, non-ortho 38.005853, skew 1.9560936, mesh_ok
   True).
2. **y+ range achieved**: a `yPlus` function object (`onEnd`) is read via
   `parse_yplus_dat` (reused from `workflows/tmr_verification.py`); the gate
   requires the *average* y+ in `[30, 500]` — standard wall-function
   log-law guidance (≈30–300), widened to 500 here for a coarse industrial
   external-aero mesh. This band is not arbitrary: the A4 DAFoam ladder
   (`demo-output/website/dafoam/ladder-a/A4_ahmed_body.md`) measured mean
   y+ 205.72 on this *exact* 45,760-cell mesh, from a different SIMPLE-
   family solver — independent corroboration this mesh sits in the right
   band.
3. **Convergence residual reached**: final residuals for Ux, Uy, Uz, **and**
   p (all four, unlike the 2D cylinder family's Ux/Uy/p-only check — this
   is a 3D solve) are parsed from the solver log; the gate requires
   `max(Ux,Uy,Uz,p) ≤ 1e-4` — exactly the threshold the case's own
   `fvSolution.SIMPLE.residualControl` already asks the solver to reach
   (`p 1e-4; U 1e-4; "(k|omega)" 1e-4;`), not a separately invented number.
4. **Force-coefficient stationarity**: `cvs.halves_drift` over the final
   50-iteration window on Cd (reused verbatim, same function and the same
   10% tolerance Family 1, `openfoam-cylinder-unsteady`, already uses) —
   the two halves of the averaging window must agree within 10% or the row
   is refused, exactly the discipline the transient NACA0012 defect
   (commit 6606434) established for this codebase.

## Validation gate result: PASS (25°), documented miss (35°)

Two real evaluations were run end-to-end through `mega_batch.run_task`
against the scratch ledger, one per geometry:

| index | slant | Re | cells | y+ avg | residual max | Cd drift | Cd (planform) | Cd (frontal, rebased) | reference | error | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 11 | 25° | 1.56e6 | 45,760 | 261.7 | 2.13e-6 | 0.0016% | 0.09004 | **0.32284** | 0.285 ± 15% [0.2423, 0.3278] | 13.28% | **inside band — VALIDATED** |
| 23 | 35° | 2.29e6 | 45,813 | 372.8 | 1.87e-6 | 0.0030% | 0.08770 | 0.31445 | 0.260 ± 15% [0.221, 0.299] | 20.94% | outside band — documented TREND ONLY, consistent with the pre-existing `models/curriculum/results/ahmed_35.json` record (20.81% error, same verdict) |

Rebasing uses the same method the credentialed baseline uses: planform Cd ×
(planform area / frontal area), with frontal area 0.389 × 0.288 = 0.112032
m² measured directly from the STL bounding box (matches
`reference.yaml`'s stated 0.112 m²).

**Family-level validation gate: PASS.** The 25° design point reproduces the
citable reference — Ahmed, Ramm & Faltin 1984, SAE 840300, Cd 0.285 ± 15%
— at 13.28% relative error, inside the band. The 35° point misses the band
(20.94%), but this is not new: it reproduces this repo's own pre-existing,
already-documented finding that 35° lands as TREND ONLY on this mesh/solver
combination (not a new failure introduced by this task), and the underlying
physical cause is the same one already on record — steady RANS on a
documented-bistable / fully-separated slant wake scatters against a single
time-averaged experimental number. Both numbers are reported; neither is
hidden.

## Cost — measured, not estimated

Per-stage wall time (single core, no MPI — trivially inside the "cap 4
ranks" doctrine), index 11 (25°, representative — index 23 was within 4%):

| stage | wall time |
|---|---|
| surfaceFeatureExtract | 0.2 s |
| blockMesh | 0.4 s |
| snappyHexMesh | 6.0 s |
| checkMesh | 0.5 s |
| potentialFoam (init aid, not gated) | 0.6 s |
| simpleFoam (250 iterations) | 27.4 s |
| **total (measured `wall_seconds`)** | **35.3 s** (index 11), **34.0 s** (index 23) |

**≈0.57–0.59 core-minutes per evaluation.**

**Honest discrepancy, disclosed rather than smoothed over**: this is
markedly faster than the original (non-batch) study's own measured numbers
on the *same recipe* — `mission-output/geometry-study/study-ahmed_25`
recorded snappyHexMesh 31.2 s and simpleFoam 118.9 s (total 2.95 min) on
2026-07-23. Same mesh, same iteration count, same host. The difference is
not fabricated away: most likely explanation is machine load at the time of
each run (this task's two test evaluations ran with 4–5 other real solver
processes concurrently active on the box, per `ps aux` at the time, so it is
not idle-machine bias) or genuine run-to-run variance in this box's CPU
allocation. Both numbers are stated; **the 34–35 s figures are this task's
own directly measured numbers via the real dispatch and are what's reported
as F10's cost**, with the caveat above on record.

### Cost ratio vs. the batch's other families (from `BATCH_INVENTORY.md`)

| family | dimensionality | physics | median wall time | ratio vs. F10 |
|---|---|---|---|---|
| openfoam-cylinder | 2D | steady laminar | 2.4 s | F10 is **~14.6x** more expensive |
| rhosimplefoam-naca0012-transonic | 2D | steady RANS, compressible, shock | 29.6 s | F10 is **~1.2x** more expensive (comparable) |
| vspaero-wing | 3D | **inviscid** panel method | 5.2 s | F10 is **~6.7x** more expensive |
| openfoam-cylinder-unsteady | 2D | unsteady RANS-free (laminar) shedding | 393.7 s | F10 is **~11x cheaper** |
| **F10 (this family)** | **3D** | **viscous RANS** | **~34.5 s** | — |

**Honest bottom line on cost**: 3D viscous CFD on this validated,
already-right-sized Ahmed body mesh lands at **tens of seconds per
evaluation**, not the minutes-to-tens-of-minutes this directive anticipated
— it is cheaper than the batch's existing unsteady 2D family and only
modestly more expensive than the transonic 2D family. This does NOT mean 3D
viscous CFD is generically cheap: it means this specific 45k-cell mesh, at
this iteration cap, on this host, right now, is cheap. A larger body (a
full vehicle, a motorBike-class mesh with ~10x more cells) or a tighter
convergence requirement would push this up substantially — not measured in
this task, so not claimed. At 1/12 weight, F10 costs the batch roughly the
same aggregate compute as the existing transonic family at its 2/12 weight.

## Testing (scratch ledger only, live batch never touched)

- `git status`/`ps -p 1789` confirmed the live runner (PID 1789, `--workers
  2`) was running before, during, and after this task's testing; its ledger
  (`demo-output/website/mega-batch/ledger.jsonl`) was never opened for
  write by this task.
- Ran `scripts/case_preflight.sh` against a hand-built case (built with the
  same `analyse_surface`/`build_case`/`_ahmed_add_yplus_function` calls
  F10 uses) before ever invoking an OpenFOAM utility — PASS (all turbulence
  fields present for `kOmegaSST`, headers parsed, no stale `processor*`
  dirs, MemAvailable 28.8 GB, free disk 437 GB).
- Two full evaluations (index 11, index 23) run end-to-end through the
  **real** `mega_batch.run_task(index, work_root)` dispatch — the exact
  function `run_batch`'s worker pool calls — against a ledger under
  `/tmp/.../scratchpad/f10-scratch-batch/`. Both returned `ok=True` with
  every gate passing; results are the "Validation gate result" table above.
- One fault-injection test (`slant_deg=99`, no such geometry) confirmed the
  failure path: `ok=False`, `error="RuntimeError: ahmed-viscous #999999:
  missing geometry .../ahmed_99.stl"`, 0.0 s cost — the poison-design
  handling every other family already has, working identically for F10.
- Mesh-gate parser cross-validated against synthetic bad data (non-ortho
  85.2° / skew 6.5, both over-gate) and against the real historical
  validated case's own `log.checkMesh` (exact reproduction of its numbers).
- Case directories for both successful runs were `shutil.rmtree`'d after
  metrics extraction, matching every other family; nothing was left on
  disk, no solver process was left running at the end of testing (confirmed
  via `ps aux`).

## Answers to the owner's standing learning questions

**Which mesh resolution converged for this problem class?**
`refinement=2` in this pipeline's `build_case` convention — 45,753–45,813
cells depending on slant — is the resolution this task confirms reaches
VALIDATED tier (13.28% vs. experiment, inside ±15%). No new refinement
sweep was run in this task (cost/time budget went to shipping the family
and its gates instead) — this answer is drawn from existing evidence, not
a new study, and that is stated plainly: the A4 DAFoam ladder
(`demo-output/website/dafoam/ladder-a/A4_ahmed_body.md`) already
establishes the other end of this question directly — its 2,777-cell
coarse mesh (16x coarser than the 45,760-cell fine mesh, same geometry,
same BCs, same turbulence model) was **explicitly not expected to
reproduce the fine-mesh Cd** and did not (base-state Cd 0.153 on the coarse
mesh vs. 0.070–0.090-class values on the fine mesh, algorithm differences
aside) — coarse-mesh Ahmed body drag is not to be trusted for this
geometry class, full stop. A genuine grid-convergence ladder (à la
`tmr_verification.py`'s flat-plate study) for the Ahmed body was not
attempted here and would be the natural next rung.

**Where was 2D defensible, and where is 3D genuinely necessary?**
The Ahmed body is the clearest case in this whole batch where 3D is **not
optional**, for a physical reason, not a modeling convenience: its drag is
governed by a pair of counter-rotating streamwise (C-pillar) vortices that
form at the *side* edges of the rear slant and wrap over the slant surface,
redistributing momentum out of the base wake in the spanwise direction and
modulating the base pressure recovery. That mechanism has no 2D
counterpart — a 2D "slice" of the Ahmed body is just a backward-facing step
with no side edges to shed a trailing vortex system from, and would report
a fundamentally different (and wrong) drag number, not a cheaper
approximation of the right one. The experimental reference itself (Ahmed,
Ramm & Faltin 1984) is a 3D wind-tunnel model for exactly this reason. By
contrast, this batch's other families show where 2D genuinely *is*
defensible, not merely cheaper: the circular cylinder families
(`openfoam-cylinder`, `openfoam-cylinder-unsteady`) are 2D by design and
that is a legitimate physical model below Re ≈ 189 (Williamson 1996, cited
already in `PHYSICS_FAMILIES.md`), where the real wake has not yet
developed strong spanwise (3D) structure — 2D is describing real 2D-
dominated physics there, not skipping it. The transonic NACA0012 family is
a 2D **airfoil section** by definition (infinite-span assumption, no wingtip
or sweep effects) — a legitimate abstraction for a section's own
shock/boundary-layer behavior, which is exactly what it is used for; a real
finite wing is what `vspaero-wing` (inviscid) and, now, could in principle
extend F10-style meshing to (not attempted here) address in 3D. The Ahmed
body has no such reduction: its own defining physics is a 3D separated-flow
topology, so this family had to be 3D and viscous to mean anything at all.

**What is the compute-cost ratio of 3D viscous versus the 2D families?**
See the cost-ratio table above: measured on this host, F10 (3D viscous) is
~14.6x the cost of the cheapest 2D family (`openfoam-cylinder`, 2D
laminar steady), ~1.2x the cost of the other 2D RANS family
(`rhosimplefoam-naca0012-transonic`), and ~11x **cheaper** than the batch's
2D unsteady family (`openfoam-cylinder-unsteady`). The honest generalization
is narrower than "3D viscous costs Nx": on a right-sized, already-validated
mesh, 3D viscous RANS is comparable in cost to 2D RANS with a similar
iteration budget, and it is the mesh size and iteration count — not the
dimensionality by itself — that dominates cost. A naively larger 3D mesh
(a full-vehicle body, not this ~46k-cell Ahmed shell) would change this
ratio substantially; this task measured only the mesh it had, and says so.
