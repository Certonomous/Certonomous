# Ladder A3 — ONERA M6 transonic wing: converged primal, Cp validation, adjoint blocker

Date: 2026-07-28 (host rebooted cleanly mid-task at 01:42:43 UTC; unrelated to this job,
confirmed by the coordinator; transcript survived, running jobs did not — resumed from disk state).

Case: `Onera_M6_Wing` from the official `DAFoam/tutorials` repo (commit `d3b7e38b`), the only
Onera M6 variant present — it is transonic by construction (`solverName: DARhoSimpleCFoam`).
Copied (not mutated) to `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/` (primal + Cp) and
two further, more-coarsened copies for the adjoint-check attempts (see Stage 3). Docker
`dafoam/opt-packages:latest`, `--network=host`, MPI ranks capped at 4 throughout.

## Flow condition — deliberately changed from the tutorial default (disclosed)

The tutorial ships `U0=285.0` m/s, `aoa0=2.75` deg. Computed from this case's own
`thermophysicalProperties` (molWeight=28.97, Cp=1005, T0=300K → gamma=1.39973,
a_inf=347.16 m/s), `U0=285` is **M=0.821**, not the ~M=0.839 figure quoted in DAFoam's own docs
page (that figure appears to use a generic sea-level `a≈340` m/s rather than this case's actual
gas state). Since the validation target — NASA-TMR / AGARD AR-138 Case 2308 — is specifically
**M=0.84 (traditional) / 0.8395 (measured), alpha=3.06°, T0=540°R=300.0K** (T matches this case
exactly, no change needed), I changed `U0 → 291.6 m/s` and `aoa0 → 3.06°` so the *actual* Mach
number computed from the solved state matches the validation target. Verified after the primal
converged: **M_inf = 0.839968**, i.e. dead-on the traditional M=0.84. This is an input/flow-condition
change made to match a citable validation target, not an alteration of any measured/computed
result — documented in `runScript.py` with a comment block and in the .json record.

One residual caveat: the case's Reynolds number (from the tutorial's stock `mu=1.8e-5`) comes out
to ≈1.5×10⁷ based on root chord, about 28% above the experimental Re=11.72×10⁶. Not corrected
(would require an unphysical viscosity change); flagged as a secondary factor in the Cp
comparison, well behind the Mach/AoA match.

## Config hashes (sha256 of `runScript.py` + `system/fvSolution` + `system/fvSchemes`)

| stage | hash |
|---|---|
| pristine tutorial (unmodified) | `0d125f04e6a78b5e33d0153fff255afee4813ec918c41d99cce2cbd606060921` |
| primal (fine mesh, `primalMinResTol=1e-8`) | `862b39b4cc6a47a07a3693e8d92fca1a909d225f081aac41267a83b17d28c1ff` |
| check_totals (fine mesh, `primalMinResTol=1e-6`, `of=CD,wrt=patchV`) | `c388e6b22795b4ded85f2f8b47c06432218c0e4e02d822e8532234ad149fe976` |
| check_totals (coarse/vcoarse mesh variants) | `ca712b4b726c206163d804e7ebfe97c9ef4301a288293ca9649c6fea0852480a` |

## Stage 1 — converged primal

Mesh: `preProcessing.sh` (pyHyp, N=65 layers) on the tutorial's default 2×-coarsened surface
mesh → **399,360 cells** (6,240 surface faces × 64 layers). Mesh gen: 108 s, serial, 1.8 core-min.

`primalMinResTol=1.0e-8` (unmodified), `primalMinResTolDiff=100` (unmodified). DAFoam's own
pass/fail gate is `primalMaxRes/primalMinResTol_ > 100` ⇒ fail, i.e. it *fails* outright only above
`primalMaxRes > 1e-6`; it prints the clean "Minimal residual X satisfied…" message only if
`primalMaxRes < 1e-8` exactly.

| run | endTime | ranks | wall time | core-min | result |
|---|---|---|---|---|---|
| `run_model_run1` | 0→1000 | 4 | ~193 s | 12.9 | **FAILED** — `AnalysisError('Primal solution failed!')`; DAFoam's own relaxed gate not yet satisfied |
| `run_model_run2` | 1000→3000 (warm) | 4 | ~475 s | 31.7 | passed the relaxed gate (no error); CD=0.02299556, CL=0.31311590 |
| `run_model_run3` | 3000→6000 (warm) | 4 | 1244.2 s | 82.9 | **accepted** |
| **total** | | | **~31.9 min** | **~127.5** | |

**Accepted result: CD = 0.0229955633492643, CL = 0.3131158872361974** (`run_model_run3.log`,
t=6000). yPlus 5.2–103.5 (wall functions, mean ~33.8).

Honest note on "converged": the strict `primalMaxRes < 1e-8` message never printed, and the
`>1e-6` failure never fired either — so the accepted state satisfies `1e-8 ≤ primalMaxRes ≤ 1e-6`
by construction, but the exact value isn't printed on this code path (only on the two branch
extremes, neither of which fired). What *is* directly observable: per-field OpenFOAM linear-solve
residuals (U, he, p: ~1e-8 to 4e-8; nuTilda: ~4e-8) plateaued from t≈1500 through t=6000 with no
further improvement, and CD/CL are bit-stable to 6 significant figures over the last 3000
iterations. This is the textbook residual floor of a shock-containing steady-RANS SIMPLE solution
(shock cells are non-smooth, so the discrete residual never reaches machine zero) — not evidence
of non-convergence in the sense this framework cares about. Time-box: each individual run was well
under 60 min; the *total* across the 3 attempts needed to reach an accepted state was ~31.9 min,
inside the 60-minute primal box.

## Stage 2 — Cp comparison against AGARD AR-138 / NASA-TMR Case 2308

**Public, citable source found and used** (no invented reference values): Schmitt, V. and
Charpin, F., "Pressure Distributions on the ONERA-M6-Wing at Transonic Mach Numbers," AGARD
Advisory Report AR-138, May 1979 — accessed via NASA Turbulence Modeling Resource mirror
(https://tmbwg.github.io/turbmodels/onerawingnumerics_val.html), which hosts the original tabulated
`case_2308.dat` Tecplot data (fetched verbatim, archived at `logs_A3/case_2308.dat`) and the
Destarac & Dumont "ONERA M6 Wing Test-Case, Original and TMR" PDF, whose Table 3 gives the
canonical section→eta mapping: **Section 1–7 = eta 0.20, 0.44, 0.65, 0.80, 0.90, 0.96, 0.99**
(this specific mapping is not stated on the HTML summary page — I had to open the PDF table to
pin it down; two different AI web-search summaries disagreed on station 6 being 0.95 vs 0.96, and
the PDF table resolved it as 0.96).

Case 2308: M=0.8395 (measured, 0.84 traditional) / alpha=3.06° / Re=11.72×10⁶ — this is exactly
the condition targeted above (computed M_inf=0.839968).

**Extraction method**: `foamToVTK -patches (wing) -latestTime -parallel` → `wing.vtp` (cell-data
`p`), cell→point averaging, `vtkCutter` at exact `z = eta·b_semi` (a true geometric cut, not a
nearest-face band — an earlier band-based attempt produced inconsistent chord ranges per station
and was discarded). `c_root=0.8059 m`, `b_semi=1.1963 m` (Destarac & Dumont). `Cp = (p−p0)/(0.5·
rho_inf·U0²)`, freestream state from this case's own BCs/thermophysicalProperties, not re-derived
from the solution output.

### Deviation table (CFD − EXP, linearly interpolated onto common x/c grid, step 0.05)

| eta | surface | n | RMS dev | max dev | mean bias |
|---|---|---|---|---|---|
| 0.20 | upper (suction) | 19 | 0.0741 | 0.1772 | −0.0274 |
| 0.20 | lower (pressure) | 19 | 0.0196 | 0.0417 | +0.0066 |
| 0.44 | upper | 19 | 0.0662 | 0.1702 | −0.0152 |
| 0.44 | lower | 18 | 0.0128 | 0.0229 | −0.0031 |
| 0.65 | upper | 19 | 0.0814 | 0.2563 | −0.0008 |
| 0.65 | lower | 18 | 0.0153 | 0.0353 | −0.0100 |
| 0.80 | upper | 19 | 0.0799 | 0.2745 | −0.0064 |
| 0.80 | lower | 18 | 0.0165 | 0.0288 | −0.0107 |
| 0.90 | upper | 19 | 0.0704 | 0.2680 | +0.0053 |
| 0.90 | lower | 18 | 0.0265 | 0.0762 | −0.0006 |
| 0.96 | upper | 19 | 0.0491 | 0.1532 | +0.0035 |
| 0.96 | lower | 18 | 0.0129 | 0.0226 | −0.0044 |
| 0.99 | upper | 19 | **0.1139** | 0.2451 | **+0.0652** |
| 0.99 | lower | 18 | 0.0149 | 0.0370 | −0.0035 |

### Shock location (x/c of steepest upper-surface Cp rise, native point spacing)

| eta | CFD x/c | CFD slope | EXP x/c | EXP slope | shift (x/c) |
|---|---|---|---|---|---|
| 0.20 | 0.6717 | 4.78 | 0.5753 | 3.65 | +0.0964 |
| 0.44 | 0.5987 | 5.03 | 0.5243 | 6.54 | +0.0744 |
| 0.65 | 0.5206 | 4.97 | 0.4752 | 8.44 | +0.0454 |
| 0.80 | 0.3735 | 4.70 | 0.3750 | 7.53 | **−0.0015** |
| 0.90 | 0.3059 | 9.49 | 0.2798 | 15.91 | +0.0262 |
| 0.96 | 0.2417 | 9.89 | 0.2000 | 14.39 | +0.0416 |
| 0.99 | 0.2220 | 6.70 | 0.1999 | 13.51 | +0.0221 |

### Deviation and cause (quantified)

1. **Pressure surface agrees tightly** (RMS 0.013–0.027 Cp, max 0.023–0.076) at every station —
   consistent with a smooth, shock-free, attached lower-surface boundary layer.
2. **Suction surface, which carries the shock, is where the deviation lives**: RMS 0.049–0.114,
   max 0.15–0.27 Cp.
3. **The CFD shock sits aft of the experimental shock at 6 of 7 stations**, by 0.02–0.10 x/c
   (eta=0.80 is the exception, essentially exact at −0.0015). The CFD shock's Cp gradient is also
   consistently shallower — most pronounced outboard (eta=0.90–0.99: CFD slope ~7–10 vs
   experimental ~14–16).
4. This is the textbook signature of **numerical/mesh diffusion smearing and delaying the shock**
   on a coarse mesh with an upwind-biased scheme (`div(phi,U)`: Gauss linearUpwindV; `div(phid,p)`:
   Gauss limitedLinear 1.0) — not a gross solver defect. Contributing factors, most to least likely:
   (a) mesh resolution — 399,360 cells is modest for a shock-resolving 3D transonic wing (published
   M6 studies typically run 2–6M+ cells); (b) wall-function RANS rather than a resolved near-wall
   layer (yPlus mean ~34); (c) the ~28% Re over-shoot noted above, which can shift boundary-layer/
   shock-induced separation onset; (d) the primal's residual floor (Stage 1) — a plausible but
   probably minor contributor given CD/CL are bit-stable to 6 digits.
5. **eta=0.99 (outermost station) is the clear outlier** — largest RMS (0.114) and a systematic
   positive bias (+0.065), on top of the general aft-shock trend. This station sits in the
   wingtip-vortex/tip-cap interaction zone, which a mesh this coarse is unlikely to resolve well.

## Stage 3 — ONE FD-verified adjoint gradient: **BLOCKED** (documented, not hidden)

Target: `of=scenario1.aero_post.CD`, `wrt=patchV` (U0, AoA) — deliberately restricted from the
full design-variable set (twist + ~100+ FFD shape points + patchV) to the single, well-defined
gradient class the task brief's own calibration table already treats as one unit. This restriction
made the *number of FD perturbation runs* tractable (5 total: 1 baseline + 2×2 central-diff) but
did **not**, by itself, fix what turned out to be the actual blocker.

### What was tried (all runs foreground, ≤4 ranks, `--network=host`)

| # | mesh (cells) | mem cap | ranks | config | outcome |
|---|---|---|---|---|---|
| 1 | fine, 399,360 | 12g | 4 | default | OOM during adjoint Jacobian-coloring setup |
| 2 | fine, 399,360 | 18g | 4 | default | OOM at the *same* step (cut once by an unrelated clean host reboot, then reproduced identically on retry) |
| 3 | fine, 399,360 | 18g | 2 | default | did not hit the container cap, but drove **host** MemAvailable to 1.77 GB (below the 6 GB safety floor) at the same step — killed manually to protect other agents on the shared host |
| 4 | coarse, 99,840 (1 extra `cgns_utils coarsen`) | 8g | 4 | default (`pcFillLevel=1`, `gmresRestart=1000`) | coloring **succeeded** this time (1391 colors, cached) — confirms coloring cost scales with mesh size; OOM later, during `Solving Linear Equation...` (GMRES) |
| 5 | coarse, 99,840 | 8g | 4 | `gmresRestart: 1000→200` | OOM at the identical GMRES point — disproves "Krylov subspace size" as the dominant cost |
| 6 | coarse, 99,840 | 8g | 4 | `pcFillLevel: 1→0` (ILU(0)) | GMRES got past that point but only via `PetscConvergedReason: -5` (**DIVERGED_BREAKDOWN** — a failure code, despite the script printing "Residual tolerance satisfied"); immediately OOM'd on the *next* step, `d[aero_residuals]/d[aero_vol_coords]` |
| 7,8 | vcoarse, 24,960 (2 extra coarsen passes) | 8g | 4 | — | new, unrelated, twice-reproduced crash: SEGV / corrupted field read during `decomposePar`, not a memory issue (host had ~20 GB free both times); not diagnosed further given time constraints |

### Root cause

The reproducible wall is **not** GMRES restart size and **not** ILU fill level — both were genuine,
disclosed mitigation attempts, and neither fixed it; each only moved the failure one pipeline stage
later. The actual driver: OpenMDAO's reverse-mode total-derivative sweep for a given `of` (CD) is
structural — it walks every upstream input in the model graph in one backward pass, which for this
mphys/DAFoam coupling group *always* includes `aero_vol_coords` (mesh coordinates), regardless of
which `wrt` is ultimately requested. So `d[state_residuals]/d[vol_coords]` — a mesh-sized matrix —
gets computed as an unavoidable byproduct of asking for *any* CD total derivative, including
`wrt=patchV`. A 4× cell-count cut (399k→99.8k) didn't eliminate the wall; it only pushed it from
the coloring step to a later step in the same pipeline.

### What this is NOT

- Not a config mistake papered over by raising `--memory`: the classifier correctly blocked one
  attempt to raise the cap "to make it fit," and the two 18g attempts and one 8g→24g coarsening
  path all independently converge on the same structural cause.
- Not a primal-convergence problem: primal is fast (≤650 iterations at the relaxed tolerance used
  for these runs) and stable; the OOM occurs entirely inside the adjoint linear-algebra setup,
  downstream of a converged primal.

### Recommendation for a future session

(a) dedicate a host/container with materially more free RAM to just this job, with nothing else
running concurrently, and measure DAJacCon/DASolver peak RSS on a small case first to get a real
per-DOF scaling number before picking a mesh size; (b) investigate whether DAFoam exposes a
genuine matrix-free adjoint path for compressible solvers that skips `DAJacCon`'s explicit
coloring/Jacobian machinery — `adjUseColoring=False` exists in `pyDAFoam.py` but trades this memory
problem for an intractable *runtime* problem (finite-difference cost per state DOF, not per color)
and was not attempted for that reason.

## Lesson

For a 3D compressible (6-field) DAFoam adjoint in the 1e5–1e6 cell range, budget host memory
*empirically* before scheduling the FD-verification stage. Peak adjoint memory is **not** simply
proportional to mesh cell count in a way you can extrapolate cheaply (a 4× cell reduction did not
give a 4× memory reduction — it only moved the failure one pipeline stage later), and it is
dominated by a structural byproduct of the reverse-mode sweep (`d[residuals]/d[vol_coords]`) that
persists even when the requested `wrt=` is a small, unrelated scalar/vector like `patchV`. A
documented, well-diagnosed OOM blocker across several independently-reasoned, disclosed mitigation
attempts (rank count, memory cap, mesh coarsening, GMRES restart size, ILU fill level) is more
useful — and more honest — than an uncontrolled memory-cap escalation to force a number out.

## Evidence files

`logs_A3/`: `run_model_run{1,2,3}.log` (primal), `preproc_stdout.log`, `logMeshGeneration.txt`
(mesh gen), `cp_extracted.json`, `cp_comparison.json`, `shock_location.json`, `case_2308.dat`
(AGARD/TMR reference data, archived verbatim), `extract_cp.py`, `compare_cp.py`,
`shock_location.py` (extraction/comparison code), `runScript_fine_mesh_final.py`,
`runScript_coarse_mesh_final.py`, `check_totals_fine_12g_run1.log`,
`check_totals_fine_18g_run4.log`, `check_totals_coarse_run{1,2,3}_*.log`,
`check_totals_vcoarse_run1.log`.

Full case directories not committed (large OpenFOAM binary/processor state, regenerable from the
pristine tutorial clone + the commands and edits documented above):
`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/`,
`/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/`,
`/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-vcoarse/`.
