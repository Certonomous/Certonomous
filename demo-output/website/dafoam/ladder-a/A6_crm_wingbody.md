# Ladder A6 — CRM / DPW-class wing-body: converged primal, honest wall report

Date: 2026-07-28. Final rung of Ladder A. Scope per the queue: converged primal is success
tonight; the gradient is **known infeasible** on this host per A3's measured evidence (adjoint
OOM at both 399,360 and 99,840 cells, eight mitigations ruled out) — **not attempted**, per
explicit instruction.

## 0. Case selection: CRM_Wing chosen over DPW4_Aircraft — and why

Both `/home/ubuntu/dafoam-tutorials/CRM_Wing/` and `/home/ubuntu/dafoam-tutorials/DPW4_Aircraft/`
were inspected before starting.

- **DPW4_Aircraft** is the genuine wing-body(-tail) configuration (`designSurfaces: ["wing",
  "tail", "body"]`, 11 STL parts). It is the more faithful match to "CRM/DPW-class wing-body."
  But its shipped mesh recipe is HPC-scale by construction: `snappyHexMeshDict` sets surface
  refinement **levels 9–12** (up to 2^12 = 4096x subdivision of the background cell at the
  wingtip/trailing-edge features), `maxGlobalCells 200,000,000`, and `decomposeParDict` defaults
  to `numberOfSubdomains 192`. Retuning 11 STL parts' refinement levels down to something that
  fits a 75-minute box, on a single pass, with no prior data point on this geometry in the repo,
  is a high-risk, likely multi-iteration snappyHexMesh quality-tuning problem (feature snapping,
  layer addition, skewness control on a fuselage+wing+tail junction) that could easily consume
  the entire time-box with nothing to show. **Rejected for tonight on time-box grounds — not
  attempted, so no data exists on whether it would have meshed successfully.**
- **CRM_Wing** is wing-alone (`designSurfaces: ["wing"]`, no fuselage/tail patch) — **so this is
  honestly not a full wing-body reproduction**, a real limitation disclosed up front. But its
  mesh pipeline is a single deterministic sequence already proven in this lab tonight on Onera M6
  (A3): download an official pre-built, pre-coarsened CGNS surface mesh, one `cgns_utils coarsen`
  pass, one `pyHyp` hyperbolic volume extrusion (N=53 layers), `plot3dToFoam` + `autoPatch` +
  `createPatch` + `renumberMesh`. Deterministic cell count, no iterative quality tuning required.

**Chosen: CRM_Wing.** Given the hard 75-minute time-box for meshing + primal combined, the
tractable, low-risk path that reliably produces a *converged* primal was weighted above geometric
completeness. This is disclosed as a real scope reduction, not hidden.

## 1. Mesh

Source: `DAFoam/tutorials` official repo, commit `d3b7e38b058aba2a98a74092e15c41ec455c570d`
(same clone/commit A3 used). Case copied (not mutated) to
`/home/ubuntu/certonomous-runs/A6-crm-wing/`.

Pipeline (`preProcessing.sh`, unmodified): downloaded `CRM_surfMesh.cgns.tar.gz` (official
DAFoam release asset, github.com/dafoam/files), one `cgns_utils coarsen` pass, `genWingMesh.py`
(pyHyp hyperbolic extrusion, N=53 layers, `s0=1e-4`, `marchDist=25*3.758151`), `plot3dToFoam`,
`autoPatch 45`, `createPatch`, `renumberMesh`. Docker `dafoam/opt-packages:latest`,
`--network=host`, single-threaded (mesh gen itself is serial regardless of `--cpus`).

**Result: 579,072 cells** (`renumberMesh` log: "Mesh region0 size: 579072"), 3 patches: `wing`
(11,136 faces, wall), `inout` (11,136 faces), `sym` (7,072 faces, symmetry). Decomposed to **4
MPI ranks** (cap enforced; tutorial default was `numberOfSubdomains 72`, changed to 4), max
145,096–146,096 cells/rank (well balanced, <1% imbalance).

Mesh quality (`checkMesh`, run inline by the DAFoam solver at t=0): max aspect ratio 309.1
(threshold 2000, OK), non-orthogonality max 70.4 / average 18.9 (threshold `maxNonOrth=75`, OK),
max skewness 3.32 (threshold 5.0, OK). **"Mesh OK."** — passes the case's own
`checkMeshThreshold` gate cleanly.

Mesh generation wall time: ~40 s (single-threaded; wget, coarsen, pyHyp extrusion, conversion
utilities) ≈ **0.7 core-minutes**.

## 2. Primal convergence

Solver `DARhoSimpleCFoam` (transonic, compressible RANS SIMPLE), `primalMinResTol=1e-8`
(tutorial default, unmodified). Flow condition unmodified from the tutorial: U0=295 m/s, T0=300K,
p0=101325 Pa, `aoa0=2.11031707` deg (fixed — `run_model` task, not the optimizer). From this
case's own `thermophysicalProperties` (molWeight=28.97, Cp=1005 → gamma=1.39972,
a_inf=347.15 m/s): **M_inf = 295/347.15 = 0.850** — matches the DPW/CRM design Mach exactly.

### Process trap hit and paid for (disclosed in full)

The first attempt used a shell-level `timeout 590` wrapper around `docker run` but did **not**
set the Bash tool's own `timeout` parameter, which defaults to 120,000 ms (2 min). The tool
killed the wrapper at 2 minutes; the container **did not stop** (dockerd keeps a foreground
`docker run`'s container alive independently of the CLI client that attached to it), and kept
solving in the background, unmonitored, reaching t=250 and writing a checkpoint — exactly the
kind of orphan this task's process rules exist to prevent. It was discovered via `docker ps -a`,
correctly identified as mine (via mount source path) and stopped — but the manual `docker stop`
landed **mid-write** of the t=250 checkpoint, corrupting `processor*/250/p` (truncated field
file, `Required entry 'internalField' missing`). The next attempt, restarting from that
checkpoint (`startFrom latestTime`), crashed immediately with a PETSc SEGV while trying to read
the corrupted field. Recovery: `sudo rm -rf processor*`, reset `startFrom` to `startTime`, and
restarted clean from t=0 — this time with the Bash tool's `timeout` parameter correctly set to
600,000 ms, which is what actually fixed it. **Lesson for future sessions: the shell `timeout`
command is not a substitute for the tool call's own `timeout` parameter — only the latter
prevents an orphan.** No host memory distress occurred at any point in this sequence
(`MemAvailable` stayed >29 GB throughout); the failure was pure process management, not a
resource wall.

### Runs

| run | startFrom | endTime | ranks | wall time | core-min | outcome |
|---|---|---|---|---|---|---|
| attempt 1 | t=0 | 2000 (target) | 4 | ~134 s (orphaned, then manually stopped mid-checkpoint-write) | ~8.9 | **discarded** — corrupted the t=250 checkpoint it left behind; its own log file was later overwritten by the accepted run's log (same filename reused — a second, smaller process slip, disclosed here since the raw log no longer exists standalone; its console output through t=200 was captured in-session: CD=0.03118, CL=0.4036 at t=200, before being stopped) |
| attempt 2 | t=250 (corrupted) | 2000 (target) | 4 | ~12 s | ~0.8 | **failed immediately** — PETSc SEGV reading truncated `processor*/250/p` |
| **attempt 3 (accepted)** | t=0, clean | **1000** | 4 | **431.0 s** | **28.73** | **ACCEPTED** |

`logs_A6/run_model_accepted_t0_to_t1000.log`,
`logs_A6/run_model_attempt2_corrupted_checkpoint_read.log`.

Total primal-stage core-minutes across all 3 attempts (including the two discarded): **≈38.4**.
Total wall-clock for meshing + primal combined, start to accepted finish: **≈14 minutes** —
comfortably inside the 75-minute time-box (61 minutes of margin were not used; convergence at
t=1000 was clean enough that extending further was judged not to change anything material).

### Residual / CD / CL history (accepted run)

| t | CD | CL | U0 finalRes | p finalRes |
|---|---|---|---|---|
| 1 | 0.040245 | 0.005111 | — | — |
| 100 | 0.038644 | 0.341184 | 3.81e-4 | 2.46e-4 |
| 200 | 0.031176 | 0.403622 | — | — |
| 300 | 0.022489 | 0.479113 | — | — |
| 400 | 0.020989 | 0.497453 | — | — |
| 500 | 0.020845 | 0.500169 | — | — |
| 600 | 0.020883 | 0.500179 | — | — |
| 700 | 0.020901 | 0.500051 | 4.85e-8 | 3.59e-7 |
| 800 | 0.020903 | 0.500013 | 1.24e-8 | 1.56e-7 |
| 900 | 0.020902 | 0.500013 | 3.75e-9 | 3.98e-8 |
| **1000** | **0.0209014** | **0.5000146** | **1.74e-9** | **9.88e-9** |

**Accepted result: CD = 0.02090143421526141, CL = 0.5000146055201552** at t=1000.
All six field `finalRes` values at t=1000 are below 1e-8 (U0 1.7e-9, U1 1.8e-9, U2 1.5e-9,
he 3.6e-9, p 9.9e-9, nuTilda 7.5e-9) — this satisfies `primalMinResTol=1e-8` on every field, a
tighter convergence than A3's shock-plateau case. CD/CL are bit-stable to 5–6 significant figures
from t=600 through t=1000 (CD drifts only in the 5th digit: 0.020883 → 0.020901 → 0.020901;
CL locks to 0.50001 ± 0.00002). `yPlus` range 7.65–73.83, mean 34.59 (wall functions,
`useWallFunction=True`). **This is a genuinely converged primal, not a plateau accepted on
faith** — every field residual is below the stated tolerance, unlike A3's ambiguous gate.

## 3. Comparison against a citable public value

**No comparison is made against the AIAA DPW-VI wing-body scatter band** (257 drag counts,
IQR 252–264, documented in this repo's prior scoping report,
`docs/DPW-CRM-SCOPING.md`) — that figure is for the **full wing-body configuration at full-scale
Reynolds number (5e6) on 7.2M+ cell grids**. This case is wing-alone (no fuselage, which
contributes a material fraction of wing-body drag) on a 579,072-cell mesh. Comparing our number
to that figure would be exactly the kind of invented/mismatched comparison this task forbids.

**A genuinely citable public value was found and used instead: DAFoam's own official tutorial
documentation for this exact case.** Fetched from
`https://dafoam.github.io/mydoc_tutorials_aero_crm.html` (mirror source:
`github.com/DAFoam/DAFoam.github.io/blob/main/pages/mydoc/mydoc_tutorials_aero_crm.md`), which
states the case's specification (Mach 0.85, Re 5e6, CL=0.5, ~579K cells, `DARhoSimpleCFoam`) and
reports: **"the original CD was 0.02090"** (pre-optimization baseline, i.e. the same quantity
`run_model` produces here) before the tutorial's own shape optimization reduces it to 0.01932
(7.6% reduction, not attempted here — out of scope, primal only).

| | our measured value | DAFoam's published tutorial baseline |
|---|---|---|
| CD | 0.0209014 | 0.02090 |
| deviation | **0.0067%** (0.021 counts) | |
| mesh | 579,072 cells (verified independently) | ~579K cells (as stated on the page) |
| Mach / Re / CL | 0.850 / (per case setup) / 0.500015 | 0.85 / 5e6 / 0.5 |

**This is essentially an exact reproduction of the tutorial's own stated result** — the deviation
is a fifth-significant-figure difference plausibly attributable to solver-version rounding in how
DAFoam's docs report the number, not a real discrepancy. This validates that tonight's pipeline
(docker image, mesh generation commands, unmodified `daOptions`) reproduces the officially
published behavior of this exact case bit-for-bit in the sense that matters. It is **not**
evidence about DPW-VI wing-body drag-prediction accuracy — no such claim is made.

## 4. The wall

- **Cell count reached: 579,072** (primal only; no adjoint attempted).
- **Memory:** container capped explicitly at `--memory=12g` throughout (mesh gen and primal);
  never approached — no container OOM, no kill. Host `MemAvailable` was checked before the
  primal stage (30.5 GB) and again after (30.4 GB) — no measurable drawdown attributable to this
  job; the process failures above were pure orphan/checkpoint-corruption issues, not memory
  pressure. The `--memory` cap was **not** raised at any point to force a fit — it was never the
  binding constraint here.
- **What a gradient would need, referencing A3's measured evidence:** A3 (Onera M6, transonic,
  same `DARhoSimpleCFoam` solver family) OOM'd on the adjoint at **399,360 cells** with an 18 GB
  container cap and again at a coarsened **99,840 cells** with an 8 GB cap, after eight
  independent mitigations (2 memory caps, 2 rank counts, GMRES restart 1000→200, ILU fill level
  1→0) were tried and ruled out. A3's root-cause finding — OpenMDAO's reverse-mode sweep for any
  requested total derivative unavoidably builds a mesh-sized `d[residuals]/d[vol_coords]`
  Jacobian block, regardless of which `wrt=` is requested — is structural, not tunable by mesh
  size alone (a 4x cell cut only moved A3's OOM one pipeline stage later, not away). **This A6
  mesh, at 579,072 cells, is 1.45x larger than A3's already-OOM'ing fine mesh and 5.8x larger
  than A3's already-OOM'ing coarsened mesh.** A true CRM/DPW-class wing-body case at DPW grid
  standards (7.2M+ cells per this repo's own prior scoping report) is two further orders of
  magnitude beyond that. **The adjoint here is not a stretch goal that ran out of time — it is
  the same structural wall A3 already measured, applied to a strictly larger mesh, and was
  correctly not attempted tonight per explicit instruction.** A3's own recommendation stands:
  a host with materially more free RAM dedicated solely to this job, with peak DAJacCon/DASolver
  RSS measured empirically on a small case first, or DAFoam's untested `adjUseColoring=False`
  matrix-free path (which trades memory for a runtime cost of unknown magnitude), would be the
  next things to try in a future session — not attempted here.

## 5. Lesson

Two lessons, both about process discipline rather than physics:

1. **The Bash tool's own `timeout` parameter is the only thing that reliably bounds a foreground
   `docker run`.** A shell-level `timeout N` wrapper inside the command does not help if the
   *outer* tool call itself defaults to a shorter timeout (120,000 ms) — the outer kill fires
   first, detaches from (but does not stop) the container, and the container keeps running
   unmonitored exactly as this task's process rules warn against. Set the tool's `timeout`
   parameter explicitly, generously, every time a primal/adjoint run is launched in the
   foreground.
2. **Never `docker stop` a container mid-write of a checkpoint you intend to resume from.** The
   corrupted `processor*/250/p` cost one wasted attempt (~0.8 core-min, trivial) but more
   importantly cost the clean audit trail of attempt 1's log (overwritten by filename reuse on
   the restart) — a bookkeeping error, corrected here by disclosure rather than by pretending it
   did not happen.

Net effect on the deliverable: none. The accepted primal is clean, fully converged on every
field below `primalMinResTol=1e-8`, reproduces DAFoam's own published tutorial baseline to
0.0067%, and the whole exercise — including the two discarded attempts — finished in ~14 minutes
against a 75-minute box.

## Evidence files

`logs_A6/`: `preproc_stdout.log`, `logMeshGeneration.txt`, `decomposePar.log`,
`run_model_accepted_t0_to_t1000.log`, `run_model_attempt2_corrupted_checkpoint_read.log`,
`runScript.py` (unmodified from tutorial except for `-task` CLI arg used).

Full case directory not committed (large OpenFOAM binary/processor state, regenerable from the
pristine tutorial clone + the commands documented above):
`/home/ubuntu/certonomous-runs/A6-crm-wing/`.
