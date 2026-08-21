# A6 CRM wing-alone, coarsened rung N=16 (41,760 cells), np=1: PRE-REGISTRATION

**Filed 2026-08-21, Lane A, BEFORE any solver arm launched.** Predictions, ceilings and falsifiers
are committed first; `RESULTS.md` does not revise this file. Nothing filed upstream.

**Ordering disclosure, stated because it matters.** The **mesh was generated before this file was
written.** Mesh generation is deterministic case construction, not a measurement: the recipe fixes
the cell count as `wing_faces × (N−1)`, the pre-registration in `../adjoint_feasibility/` predicted
**41,760 cells** from `2,784 × 15`, and the generated mesh reports `Mesh region0 size: 41760` with a
`wing` patch of exactly **2,784 faces**. No solver arm, no adjoint and no gradient has been run.
Nothing below is retrofitted to an observed result.

---

## 1. What this rung is for

A6's adjoint has **never been attempted at any size** — `Main iteration` and `KSP Residual` appear
zero times in all four archived A6 logs. Full size (579,072 cells) is **BLOCKED** on two independent
grounds (`../adjoint_feasibility/RESULTS.md`). This rung buys the **first A6 adjoint that has ever
existed**, at a size the A3 ladder has already proven tractable for the same solver.

Three questions, in priority order:

1. **Does the A6 adjoint converge at all**, once `transonicPCOption` is set to its only live value?
2. **What does A6's FD-vs-adjoint agreement look like on the shipped toolchain**, and does it match
   A3's surprising stock-image passes?
3. **Does the rotation patch move A6's gradient**, and by how much?

## 2. Case as constructed

| item | value | provenance |
|---|---|---|
| geometry | CRM wing-alone, official `CRM_surfMesh.cgns.tar.gz` (already cached on disk; **no network access was used or required**) | `A6-crm-wing/CRM_surfMesh.cgns.tar.gz`, dated 2021-12-07 |
| recipe | `tar -xvf` → **`cgns_utils coarsen` ×2** (the archived recipe uses ×1) → `genWingMesh.py` (pyHyp, **`N=16`**, archived `N=53`; `s0=1e-4`, `marchDist=25*3.758151` unchanged) → `plot3dToFoam -noBlank` → `autoPatch 45` → `createPatch` → `renumberMesh` | `base/preProcessing.sh`, `base/genWingMesh.py` |
| **exactly two edits** to the archived recipe | one extra `cgns_utils coarsen` line; `"N": 53` → `"N": 16` | verified by `diff` against `A6-crm-wing/`, both diffs recorded in `RESULTS.md` |
| **measured cells** | **41,760** | `base/logMeshGeneration.txt`, `Mesh region0 size: 41760` |
| patches | `wing` 2,784 faces (wall), `inout` 2,784, `sym` 1,020 (symmetry) | `base/constant/polyMesh/boundary` |
| solver | `DARhoSimpleCFoam`, `primalMinResTol 1e-8`, `endTime 1000` | archived `runScript.py`, unchanged |
| design variables | `twist` **7 components** (FFD is 12×8×2, `alignIndex="j"` ⇒ `nRefAxPts = 8`), `shape` (`nom_addLocalDV` over all FFD points), `patchV` (2: U0, AoA) | `runScript.py:146-160`, `FFD/wingFFD.xyz` header |
| **decomposition disclosure** | **NONE. np=1, serial, undecomposed.** `system/decomposeParDict` is rewritten by DAFoam from `daOptions` to match the rank count; the log must print `nProcs : 1` or the arm is invalid | — |

## 3. The one mandatory configuration change

**`transonicPCOption: 2 → 1`.** `2` is dead code for `DARhoSimpleCFoam`
(`DAResidualRhoSimpleCFoam.C:172-176`; `== 1` is the only live value), and every archived ONERA M6
`-5` ran with it at `2`. Flipping this single token is what converted double `DIVERGED_BREAKDOWN`
into double `reason 2` at 368/383 iterations on A3 rung 1, proven by a negative control that
reproduced the archived failure **bit-for-bit**. A6's `runScript.py:83` inherits the tutorial default
of `2`. **Activity proof required in every log: the `DAFoam option dictionary:` dump must read
`transonicPCOption 1;`.** An arm whose log reads `2` is void.

Second edit, for cost only: `check_totals` is restricted to `of=["CD"], wrt=["twist","patchV"]`
(9 DVs, 19 primal solves). The archived script checks all DVs including `shape`, which has of order
10² components and would cost 10× the registered ceiling. **`shape` is therefore NOT graded by this
rung** — see §7.

## 4. Bounded execution, designed so no kill is ever needed

* **Iteration caps are the bound, not a timer.** `endTime 1000` (unchanged) caps the primal;
  `gmresMaxIters 2000` (unchanged) caps the adjoint. Every arm terminates on its own.
* `timeout` on each `docker run`; `--rm`; `--cpus=4` (= the lane cap); `--memory=12g` (= the RSS cap).
* **RSS monitoring is record-only.** A polling loop samples `docker stats --no-stream` and writes to
  a file. **It never kills anything.** If a sample exceeds **12 GiB**, the run is declared **over
  budget**, the observation is recorded, and **no further arms are launched** — the running arm is
  allowed to finish or die against its own container cap, which is what `--memory=12g` is for.
* Pre-launch: `uptime` and `MemAvailable` checked; the arm waits on a bounded loop if load > 10 or
  MemAvailable < 8 GiB. **Lane B may be holding ~3 GiB and 4 cores.**
* **Step 0 is a calibration primal** (`-task run_model`, ~2 core-min) run before the FD arms, purely
  to measure the per-solve cost. **If a single primal exceeds 250 s at np=1**, the FD set is cut to
  `wrt=["patchV"]` alone (5 solves) and the reduction is disclosed in `RESULTS.md`.

## 5. Predictions and falsifiers

### P1 — peak RSS

> **Predicted peak RSS ≈ 6.8 GiB** (model M2 of `../adjoint_feasibility/RESULTS.md`:
> 2,048 + 0.164 × 41,760 MiB = 8,897 MiB, de-biased by the measured 1.27× conservatism ⇒ **7.0 GiB**;
> quoted as ~6.8 GiB). **Hard ceiling 12 GiB.**
>
> **FALSIFIER:** a sample above 12 GiB. That would mean the envelope under-predicts for CRM at a size
> where it was validated for ONERA M6, and the full-size BLOCKED verdict would need re-deriving
> upward, not downward.

### P2 — primal

> **Predicted: the primal does NOT reach `primalMinResTol = 1e-8` and runs the full 1,000
> iterations, with CD/CL stable to ≥4 significant figures over the last 200.** Basis: at 579,072
> cells this exact case never triggered its own convergence test — `satisfied the prescribed
> tolerance` appears **zero** times in `run_model_run1.log` — because `nuTilda` plateaued at t≈600
> and needed ~15,573 further iterations. A coarser mesh may plateau higher, not lower.
> **Verdict language: GATE REACHED, not PASS**, if the objective is stable but the tolerance is unmet.
>
> **FALSIFIER:** the log printing `Minimal residual … satisfied the prescribed tolerance 1e-08`.
> That would be the first time this case has done so and would be reported as a positive surprise.

### P3 — adjoint

> **Predicted: both CD and CL adjoint solves return `PetscConvergedReason: 2`, with the CD solve in
> 400–1,500 iterations.** Basis: A3 rung 2 at 42,120 cells — nearly the same size, same solver, same
> `transonicPCOption 1` — converged at **987 (CD) / 1,171 (CL)**.
>
> **FALSIFIERS.** (a) Any negative reason ⇒ **GATE FAIL**, and the A3-derived expectation does not
> transfer across geometry at fixed size, which is itself a finding. (b) `reason -3` at exactly the
> 2,000 cap **with monotone descent** ⇒ budget-limited, reported as such and NOT as a wall, per the
> pre-registered distinction that separated A3 rung 2's `-3` from rung 3's.

### P4 — FD vs adjoint, and the reading it tests

> **Predicted: `CD wrt twist` inside the ≤5% PASS band on BOTH images, and `CD wrt patchV` inside
> ≤1% on both and BIT-IDENTICAL between them.**
>
> **What A3's stock passes imply, stated explicitly as instructed.** A3's rungs pass at
> **0.0077–0.93%** on **stock IDWarp**, i.e. with the `getRotationMatrix3d` degenerate-branch defect
> fully present and `check_totals` evaluating at exactly the baseline where the guard is guaranteed
> to fire. On A1, A2, A5 and the naca0015 sail that same defect accounted for **97–99.5%** of the
> shape-derivative error. **Nobody has explained the discrepancy.** Two readings are live:
> **(R1)** the defect's reach is set by how strongly the objective's own `dObj/dXv` field contracts
> with the discarded rotation term, and transonic-wing objectives happen to contract weakly; or
> **(R2)** the DV *class* matters — A3 graded `patchV`, `twist` and one `shape` component, and
> `patchV` provably never crosses the warp.
>
> **This rung discriminates them, which is why `twist` was chosen over `patchV` as the graded row.**
> `twist` *does* cross `DVGeo → warpDeriv`: on A2's aero-only case the patch improved `CL/twist` by
> **115×** and *degraded* `CD/twist` from 0.389% to 0.505%.
>
> * If **stock `CD/twist` is small (<1%) and the patch barely moves it**, R1 gains and the
>   "rotation defect is regime-1-only, and regime 1 is objective-dependent" reading survives.
> * If **stock `CD/twist` is large (>10%) and the patch collapses it**, then A3's stock passes were
>   a property of A3's chosen components, not of transonic wings — and **A3's rungs 1 and 2 would
>   need re-grading on a warp-crossing DV before their PASS can be read as a statement about the
>   case rather than about `patchV`.** That is the outcome that would most change the standing
>   picture, and it is registered here as the thing to look for.
>
> **FALSIFIER of the 'regime-1-only' reading:** the patched arm's `CD/twist` differing from the
> stock arm's by more than the FD's own resolution while `CD/patchV` stays bit-identical. That
> combination cannot be explained by anything except the warp chain.
>
> **THE CONTROL, as on A1 and A5: every FD magnitude must be bit-identical between the stock and
> patched arms.** The patch is derivative-only and the primal warp is md5-identical. **If any FD
> entry moves, stop and report** — the comparison would be between two different functions.

### P5 — trivial baseline (Charter 2c)

> Registered FD step: **`step=1e-3, form=central, step_calc=abs`** (the archived A6 value).
> **Wrong-step arm: `step=1e-8`, patched image, otherwise identical**, predicted **>50%** and a
> **GATE FAIL on a stack predicted to pass at the registered step**. Basis: A1's measured step sweep
> gives 94.95% at 1e-8 against 11.43% at 1e-3, and A1's own trivial baseline measured **132.75%**.
> Purpose: prove the instrument can still fail, so a pass in P4 is a property of the derivative and
> not of a harness incapable of returning a large number.
>
> **FALSIFIER:** the wrong-step arm returning ≤5%, which would invalidate every FD number here.

## 6. Cost ceiling — 160 core-min, hard

| step | ranks | predicted core-min |
|---|---|---|
| mesh generation (already done) | 1 serial | ~1 |
| step 0 calibration primal | 1 | ~2 |
| arm 1 `check_totals` STOCK (19 solves) | 1 | ~40 |
| arm 2 `check_totals` PATCHED (19 solves) | 1 | ~40 |
| arm 3 wrong-step, patched (19 solves) | 1 | ~40 |
| **total** | | **~123** |

Basis: full-size A6 ran 1,000 primal iterations in 431 s at np=4 on 579,072 cells ⇒
2.98e-3 core-s per cell per 1,000 iterations ⇒ **≈2.07 core-min per primal solve at 41,760 cells,
np=1**. **Hard ceiling 160 core-min ($0.137).** If the ceiling is reached, remaining arms are not
launched and the shortfall is reported rather than absorbed.

## 7. What this rung will not be able to see — stated before it runs

1. **It is not 579,072 cells.** 41,760 is **13.9× smaller**. **What transfers:** the solver, the
   geometry family, the mesh generator and recipe, the boundary-condition set, the DV
   parameterisation, and — if it converges — the fact that an A6 adjoint is reachable at *some*
   size. **What does NOT transfer:** any memory number for full size (this rung will produce the
   first CRM-specific data point, and one point cannot re-fit a scaling law); any claim that the
   full-size adjoint would converge, since the same solver stagnates at 79,560 cells; and any drag
   number — a 41,760-cell CRM wing will not reproduce the tutorial's CD = 0.02090 and **no
   drag-accuracy claim will be attached to it**.
2. **`shape` is not graded.** The DV group with of order 10² components — and the one most
   analogous to A1's and A5's failing rows — is excluded on cost. `twist` is the warp-crossing
   substitute, and it is a substitute.
3. **The decomposition axis** is absent by construction at np=1.
4. **Regime 2 of the rotation defect** is invisible: `check_totals` sits at the undeformed baseline
   where the `sqrt(eps)` guard fires. Regime 2 is unpatched by design and would govern any
   optimisation from iteration 1.
5. **The limiter axis** is not varied. A6's `fvSchemes` will be audited from disk for a `cellLimited`
   scheme and the result reported, but no `limited`/`default` arm is run.

## 8. Verdict vocabulary

PASS, GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING. Shipped-toolchain and
patched-toolchain verdicts are reported as **two separate rows**, never merged. An adjoint that
stops on its iteration cap without meeting tolerance is **GATE FAIL** or budget-limited per P3(b),
never PASS.
