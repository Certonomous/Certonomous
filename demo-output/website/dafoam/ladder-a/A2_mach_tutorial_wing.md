# Ladder A2 — MACH Tutorial Wing (official DAFoam/MACH 3D wing tutorial, aero-only)

**Case:** `MACH_Tutorial_Wing`, official tutorial cloned at `/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing/`, run from a copy at `/home/ubuntu/certonomous-runs/A2-mach-wing/` (pristine clone never mutated).

**Variant used:** `runScript_AeroOnly.py` (the aero-only script shipped alongside the tutorial's aerostructural `runScript.py`). The DAFoam docs page for this tutorial (`tutorials-aerostruct-mach-wing.html`) documents only the aerostructural variant (`runScript_AeroStruct.py`/`runScript.py`, TACS + FUNtoFEM); per this ladder's standing instruction to prefer the aerodynamic-only variant, and since the repo ships one, the aero-only script was used instead. This is a deviation from the docs' own headline case, noted explicitly rather than silently substituted.

**Solver:** `DARhoSimpleFoam` (compressible RANS, Spalart-Allmaras). Mesh: 38,304 cells (matches the docs' "~38,000 cells" figure). `checkMesh`: OK (max aspect ratio 684, max non-orthogonality 66.97 < 70 threshold, max skewness 1.34).

**Docker:** `dafoam/opt-packages:latest`, `--network=host --memory=12g`, 4 MPI ranks throughout (cap respected).

## 1. Docs' own reported drag reduction — not stated for this case

Checked `https://dafoam.github.io/tutorials-aerostruct-mach-wing.html` (and its GitHub markdown source) directly. The page states the problem setup (CL target 0.5, 96 FFD shape DVs, 7 twist DVs, 1 AoA DV, 118 constraints, ~38k cells, Mach ~0.3/Re ~30M) but **contains no before/after CD values or drag-reduction percentage**. Per instructions, this is reported rather than invented.

For context only (NOT a target for this case — different geometries/conditions): the DAFoam docs report a 7.6% drag reduction for the CRM wing tutorial and 17.2% for the ADODG3 wing tutorial.

## 2. Converged primal

`run_model` (1000 SIMPLE iterations, `primalMinResTol=1e-8`), np=4, wall time 21s.

| Quantity | Value |
|---|---|
| CD | 0.02772949388 |
| CL | 0.4775877833 |
| U finalRes (3 components) | 9.56e-09, 1.20e-08, 1.19e-09 |
| p finalRes | 1.01e-07 |
| nuTilda finalRes | 4.32e-07 |
| yPlus | min 68.79, max 1266.5, mean 321.9 |

CD/CL are stable to 8+ significant figures over the last 400 iterations — converged.

## 3. Adjoint total derivatives (`compute_totals`)

np=4, wall time 490s (8.17 min). Reverse-mode adjoint solved for CD and CL w.r.t. `aero_vol_coords`, `patchV` (U0, AoA), plus all four geometric constraints (thickcon, volcon, lecon, tecon) w.r.t. `shape` (96 DVs) and `twist` (7 DVs). Coloring computed once (`dRdWColoring_4.bin`, 1323 columns) and reused by later stages.

## 4. FD verification (`check_totals`) — GATES step 5

**First attempt failed for infrastructure reasons, not gradient reasons**: started 00:50:44Z, was 170/210 FD perturbation solves complete (81%) when, at 01:37:05Z, the kernel OOM-killed the container's python ranks (cgroup memory cap hit, `--memory=12g`, four ranks each ~10.6GB total-vm) during a period of heavy multi-agent contention on the host; the host then took a separate clean orderly reboot at 01:42:43Z that tore down the session. `prob.check_totals()` only prints its comparison table after all perturbations finish, so no partial table was recoverable — the run had to be redone from scratch. Wasted cost: 3107s x 4 ranks = 207.1 core-minutes. Log kept as `check_totals_run1_INCOMPLETE_prereboot.log`.

**Second attempt (clean host, no contention) succeeded**: started 02:31:54Z, ended 03:24:27Z, wall time 3153s (52.55 min), np=4, exit code 0. Central-difference FD (`step=1e-3`, `step_calc=abs`), 105 design variables (96 shape + 7 twist + 2 patchV) x 2 (central diff) = 210 full primal re-solves, plus the analytic (adjoint) pass. `sudo rm -rf processor*` was needed before the rerun (stale decomposed state from the killed attempt) — the same trap ladder A1 hit.

### FD verification table

Calibration reference (measured tonight on the official unmodified NACA0012 tutorial, ladder A1): geometric constraints wrt shape verify to 4.4e-14–1.4e-10 (machine precision); CD/CL wrt patchV ~0.232%; CL wrt shape ~1.67%; CD wrt shape ~11.43% on the difference-vector norm (with the two vectors' magnitudes agreeing to 0.451% — directional per-component FD noise, not a scale error). A shape-derivative FD gap of 1–12% is normal for this problem class, not evidence of a broken adjoint.

| Derivative (of / wrt) | Analytic magnitude | FD magnitude (central) | Abs error | Rel error |
|---|---|---|---|---|
| CD / patchV (U0, AoA) | 5.615356e-03 | 5.616540e-03 | 1.192085e-06 | **0.0212%** |
| CD / shape (96) | 4.801625e-02 | 4.858158e-02 | 8.325869e-04 | **1.71%** |
| CD / twist (7) | 1.922238e-03 | 1.922103e-03 | 7.478526e-06 | **0.389%** |
| CL / patchV (U0, AoA) | 7.040571e-02 | 7.040500e-02 | 1.021434e-06 | **0.0015%** |
| CL / shape (96) | 8.480582e-01 | 8.572992e-01 | 9.988934e-03 | **1.17%** |
| CL / twist (7) | 2.371825e-02 | 2.398459e-02 | 2.687753e-04 | **1.12%** |
| geometry.thickcon / shape | 9.718825e+00 | 9.718825e+00 | 9.285216e-12 | 9.55e-11% |
| geometry.thickcon / twist | 4.127369e-15 | 3.351352e-12 | 3.351467e-12 | 100%* |
| geometry.volcon / shape | 3.357042e-01 | 3.357042e-01 | 1.186017e-12 | 3.53e-10% |
| geometry.volcon / twist | 2.722885e-08 | 2.722884e-08 | 3.455266e-13 | 0.0013% |
| geometry.lecon / shape (linear) | 4.0 | 4.0 | 0 | 0% (exact) |
| geometry.tecon / shape (linear) | 4.0 | 4.0 | 0 | 0% (exact) |

\* `thickcon wrt twist`: both the analytic value (4.1e-15) and the FD value (3.4e-12) are numerically indistinguishable from zero (thickness constraints genuinely don't depend on twist in this parameterization); the "100%" relative error is a ratio of two noise-floor quantities, not a real gradient disagreement.

**Verdict: verified, at or better than the calibration scale.** CD/shape (1.71%) and CL/shape (1.17%) both land inside the 1–12% normal band and are noticeably tighter than A1's shape-derivative agreement; CD/CL/patchV agree to ~0.02% and ~0.0015% (tighter than A1's 0.232%); every geometric-constraint-vs-shape derivative is at machine precision, confirming the DVGeo/FFD Jacobian chain is sound. **Gate passes — proceeding to the documented optimization.**

## 5. Documented optimization (`run_driver`, IPOPT default)

Time-boxed to 60 minutes wall per instruction; the run was still iterating when the deadline hit and was terminated cleanly (SIGTERM, containers confirmed stopped, no leftover processes). This is reported as an honest partial result, not a completed optimization.

- Optimizer: IPOPT (pyoptsparse), `tol=1e-5`, `max_iter=100`.
- Pre-optimization step: `findFeasibleDesign` adjusted `patchV` (AoA) to hit `CL_target=0.5` before the optimizer's first iteration — this moves the starting point off the raw `run_model` baseline (CD=0.0277 at CL=0.478) to a CL=0.5-feasible baseline (CD=0.0296) used as IPOPT iteration 0. Comparing CD at matched CL=0.5 is the correct apples-to-apples baseline for the objective.
- Wall time run: 3606s (60.1 min), np=4. Completed 47 logged IPOPT major iterations (OpenMDAO driver counted through iteration 50, including the constraint-Jacobian/linear-solve work for iteration 48-50 in flight at kill time).

| Milestone | CD | CL |
|---|---|---|
| IPOPT iter 0 (CL=0.5-feasible baseline) | 0.029619634 | ~0.500 (inf_pr 4.16e-08) |
| IPOPT iter 42 (best logged) | 0.021241776 | — |
| IPOPT iter 47 (last logged, before kill) | 0.021244538 | — |
| Last evaluated point at kill (driver iter 50, in-flight) | 0.02124151 | 0.49994819 |

By iteration 30–47 the objective had plateaued to a narrow band (0.02134–0.02152), with `inf_pr` down to 1.4e-05 and `inf_du` down to 9.0e-05 (target tolerances both 1e-5) — close to, but not formally inside, IPOPT's convergence tolerance when the clock ran out. Constraints at the final evaluated point: CL=0.49995 (target 0.5, satisfied to 0.01%), `geometry.volcon`=1.0000783 (bound ≥1.0, barely satisfied), `geometry.thickcon` in [0.50, 1.73] (bound [0.5, 3.0], satisfied).

**Achieved drag reduction (partial, time-boxed): (0.029619634 − 0.021244538) / 0.029619634 = 28.3%**, at matched CL=0.5, after 47 major iterations in 60 minutes, not fully converged to the optimizer's own stopping tolerance.

No tutorial-stated target exists for this case (see §1) to compare against directly. For context only: this 28.3% partial result is larger than the CRM wing's documented 7.6% and the ADODG3 wing's documented 17.2% reductions from other DAFoam tutorials — those are different geometries/conditions and not a validated comparison, only a sanity check that the number is in a plausible range for wing shape optimization with FFD.

## 6. Wall-time / core-minutes accounting

| Stage | Ranks | Wall time | Core-minutes | Result |
|---|---|---|---|---|
| mesh preprocessing | 1 | ~30s | 0.50 | ok |
| checkMesh | 1 | ~10s | 0.17 | ok |
| primal (`run_model`) | 4 | 21s | 1.40 | ok, converged |
| adjoint (`compute_totals`) | 4 | 490s (8.17 min) | 32.67 | ok |
| check_totals attempt 1 | 4 | 3107s (51.78 min) | 207.13 | **failed — OOM + host reboot, not a gradient issue** |
| check_totals attempt 2 | 4 | 3153s (52.55 min) | 210.20 | ok, gate passed |
| optimization (`run_driver`) | 4 | 3606s (60.1 min, time-boxed) | 240.40 | partial, time-boxed stop |
| **Total useful** | | **~121.8 min (2.03 hr)** | **485.34 (8.09 core-hr)** | |
| **Total incl. wasted attempt** | | **~173.5 min (2.89 hr)** | **692.47 (11.54 core-hr)** | |

## 7. Blocker record

1. **check_totals attempt 1 destroyed by host reboot mid-run.** Not a gradient/adjoint problem — an infrastructure interruption (OOM cgroup kill of the container under multi-agent memory contention, followed by a clean host reboot). No partial FD table was recoverable because `prob.check_totals()` buffers its comparison output until every perturbation finishes. Fixed by rerunning from a clean host (attempt 2, accepted).
2. **Stale `processor*` state** after each `--rm` docker run leaves root-owned `processorN/` directories on the host bind mount; a fresh `-task` invocation that redecomposes from `0/` can collide with them. Cleared with `sudo rm -rf processor*` before each new stage — same trap documented in ladder A1.
3. **Optimization not converged.** 47/~100 IPOPT major iterations completed in the 60-minute box; objective was in a tight plateau (0.0213-0.0215) with first-order metrics an order of magnitude above tolerance, suggesting it was close to converging but not there. Reported as a partial, time-boxed result per instructions, not claimed as final.

## 8. Lesson

The two costly failure modes tonight were both **infrastructure**, not **numerics**: (a) an OOM+reboot losing 3.5 core-hours of FD work because DAFoam's `check_totals` has no incremental/checkpointed output — a multi-hour FD sweep on a large-DV case (105 DVs here vs. 8 on the NACA0012 case) is an all-or-nothing bet against host stability, and should be budgeted with that in mind (or split into custom `of`/`wrt` subsets if the case is modified from tutorial-default); and (b) `--memory=12g` per container being a real, working safety net — it killed the container cleanly rather than let the host itself OOM, which is the correct behavior, but it means container memory sizing on wide-DV cases deserves headroom-aware capping, not just a fixed default. Numerically, the FD verification came back cleaner than the NACA0012 calibration case (tighter patchV agreement, similar-or-better shape-derivative agreement) despite 12x more design variables (105 vs 8) and 3D geometry, which is a reassuring signal that DAFoam's discrete adjoint scales in DV count without degrading in accuracy on this problem class.
