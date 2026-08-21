# A3 ONERA M6 — grading confirmation (NO COMPUTE)

**2026-08-21, Lane A. Zero solver core-minutes: no container was started, no solve was run.** Every
number below is read out of a record or a log already on disk, at the line or section given.
Nothing filed upstream.

**Grading band, cited not invented** (`../../A_stepsize_study.md:91-93`): **PASS ≤5%** with zero
flagged components; **CONDITIONAL 5-15%**; **>15% or any flagged component → FAIL**. For the
reopened-ladder rungs the arms were graded under a *stricter, pre-registered* per-component rule
(`../../A3_FD3_PREREGISTRATION.md` §4) that adds an evaluability gate and a step-consistency gate on
top of the band; both are reported below.

> **Read this first: "A3" names two campaigns on two different mesh families, and merging them
> produces a false statement.** Campaign 1 is the original 2026-07-28 ladder rung at 399,360 cells,
> whose adjoint is **BLOCKED**. Campaign 2 is the reopened sweep ladder of 2026-08-08→08-11 on a
> different, much smaller mesh family, which is where A3's only FD-verified gradients exist. Neither
> supersedes the other; they are different meshes.

---

## 1. Campaign 1 — the original rung, 399,360 cells: adjoint BLOCKED

**Case identity.** `Onera_M6_Wing` from `DAFoam/tutorials` commit `d3b7e38b`, `DARhoSimpleCFoam`,
pyHyp N=65 → **399,360 cells** = 6,240 surface faces × 64 layers (`../../A3_onera_m6.md:43`), np≤4,
`dafoam/opt-packages:latest`. Flow condition deliberately changed from the tutorial's U0=285 m/s /
aoa0=2.75° to **U0=291.6 m/s, aoa0=3.06°** so the solved Mach matches AGARD Case 2308; verified
after convergence at **M_inf = 0.839968**.

### 1a. Primal — GATE REACHED

`run_model_run3.log`, t=6000: **CD = 0.0229955633492643, CL = 0.3131158872361974**, 1244.2 s at
np=4 = 82.9 core-min; three runs to reach it, ~127.5 core-min total.

The record's own honesty note is carried forward rather than smoothed: the strict
`primalMaxRes < 1e-8` message **never printed**, and DAFoam's `>1e-6` hard failure never fired
either, so the accepted state satisfies `1e-8 ≤ primalMaxRes ≤ 1e-6` **by construction** and the
exact value is not observable on that code path. What *is* observable: per-field OpenFOAM residuals
plateaued from t≈1500 through t=6000, and CD/CL are stable to 6 significant figures over the last
3000 iterations. **Verdict: GATE REACHED** — a shock-containing steady-RANS residual floor, not a
convergence failure, and not a claim of 1e-8.

### 1b. Cp validation — PASS

Against AGARD AR-138 Case 2308 (Schmitt & Charpin 1979) via the NASA-TMR mirror, `case_2308.dat`
archived verbatim at `../../logs_A3/case_2308.dat`. Pressure surface RMS deviation **0.0128–0.0265**
Cp at all seven stations; suction surface (which carries the shock) **0.0491–0.1139**. CFD shock sits
**aft** of experiment at 6 of 7 stations by 0.0221–0.0964 x/c, with a consistently shallower gradient
— the textbook signature of mesh/numerical diffusion smearing a shock on a 399k-cell grid where
published M6 studies run 2–6M+. eta=0.99 is the clear outlier (RMS 0.1139, bias +0.0652), in the
wingtip-vortex zone. **Verdict: PASS**, with the deviation attributed and quantified.

### 1c. Adjoint — BLOCKED. The eight mitigations, each with its own citation

Source table: `../../A3_onera_m6.md` §"Stage 3 → What was tried". Target was deliberately narrowed
to `of=CD, wrt=patchV` — 5 primal solves total — and **that restriction did not fix the blocker.**

| # | mesh (cells) | mem cap | ranks | lever changed | outcome | log |
|---|---|---|---|---|---|---|
| 1 | fine 399,360 | 12g | 4 | none (baseline) | **OOM during adjoint Jacobian-coloring setup** | `../../logs_A3/check_totals_fine_12g_run1.log` |
| 2 | fine 399,360 | **18g** | 4 | memory cap raised 12g→18g | **OOM at the identical step**; cut once by an unrelated clean host reboot, then reproduced identically on retry | `../../logs_A3/check_totals_fine_18g_run4.log` |
| 3 | fine 399,360 | 18g | **2** | rank count 4→2 | did not hit the container cap but drove **host MemAvailable to 1.77 GB**, below the 6 GB safety floor; killed manually to protect other agents | — |
| 4 | **coarse 99,840** | 8g | 4 | mesh coarsened 4× (one extra `cgns_utils coarsen`) | coloring **succeeded** (1391 colors, cached) — proving coloring cost scales with mesh size — then **OOM later, during `Solving Linear Equation…` (GMRES)** | `../../logs_A3/check_totals_coarse_run1_default.log` |
| 5 | coarse 99,840 | 8g | 4 | **`gmresRestart` 1000 → 200** | **OOM at the identical GMRES point** — disproves Krylov subspace size as the dominant cost | `../../logs_A3/check_totals_coarse_run2_gmresRestart200.log` |
| 6 | coarse 99,840 | 8g | 4 | **`pcFillLevel` 1 → 0** (ILU(0)) | GMRES got past that point **only via `PetscConvergedReason: -5` (DIVERGED_BREAKDOWN)** — a failure code, despite the script printing "Residual tolerance satisfied" — then OOM'd immediately on the next step, `d[aero_residuals]/d[aero_vol_coords]` | `../../logs_A3/check_totals_coarse_run3_pcFillLevel0.log` |
| 7 | **vcoarse 24,960** | 8g | 4 | mesh coarsened again (2 extra passes) | new, unrelated **SEGV / corrupted field read during `decomposePar`** — not a memory issue, host had ~20 GB free | `../../logs_A3/check_totals_vcoarse_run1.log` |
| 8 | vcoarse 24,960 | 8g | 4 | retry of #7 | **same SEGV, twice-reproduced** | — |

Levers exhausted: **2 memory caps** (12g, 18g), **2 rank counts** (4, 2), **2 mesh coarsenings**
(4×, 16×), **GMRES restart** (1000→200), **ILU fill level** (1→0).

**Root cause, as recorded.** *"OpenMDAO's reverse-mode total-derivative sweep for a given `of` (CD)
is structural — it walks every upstream input in the model graph in one backward pass, which for
this mphys/DAFoam coupling group always includes `aero_vol_coords`… So `d[state_residuals]/
d[vol_coords]` — a mesh-sized matrix — gets computed as an unavoidable byproduct of asking for any
CD total derivative, including `wrt=patchV`."* A 4× cell cut did not remove the wall; it moved the
failure one pipeline stage later.

**Verdict: BLOCKED.** Not NOT-A-RESULT and not GATE FAIL — the arm never reached a gradient to
grade, and it says so with eight independently-reasoned disclosed mitigations behind it.

**One label correction carried in.** This blocker is called a "memory wall" in some downstream
surfaces. `docs/PRODUCT_LIST.md:176-179` says of A3 itself: *"`DIVERGED_BREAKDOWN` at every mesh
size incl. 21,840 cells with >20 GB free — **conditioning, not memory**"*, while `:251` calls the
same inherited blocker a memory wall. Both statements cannot be right, and Campaign 2 below settles
it: at 21,840 and 42,120 cells the blocker was **conditioning** and one `daOptions` token removed
it. At 399,360 cells the blocker genuinely **is** memory. The single label is what is wrong.

---

## 2. Campaign 2 — the reopened sweep ladder. Rungs 1 and 2 PASS, rung 3 DIVERGED

**Case identity.** `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/` and siblings; the
same wing, a different pyHyp mesh family (1,560 surface faces × (N−1) layers), `DARhoSimpleCFoam`,
np=4, image **`dafoam-subpclu:v1` with `DAFOAM_SUBPC_TYPE` UNSET** — i.e. stock preconditioner
behaviour, the absence of the sub-LU banner in every log being the standing proof
(`../../A3_TPC1_ARM_PREREGISTRATION.md` §2). **Stock IDWarp throughout: no rotation patch is
involved anywhere in Campaign 2.** The one functional change from the archived configuration is
`transonicPCOption: 2 → 1`.

### 2a. The token, and the negative control that earned the causal claim

Every archived M6 `-5` ran with `transonicPCOption: 2`, which is **dead code for
`DARhoSimpleCFoam`** — the solver's own transonic mitigation
(`DAResidualRhoSimpleCFoam.C:172-176`, drop `fvm::div(phid,p)` from the PC pressure equation) was
never on; `== 1` is the only live value.

| arm | token | CD solve | CL solve | log |
|---|---|---|---|---|
| **TPC1** | `transonicPCOption 1` | **368 iters, `PetscConvergedReason: 2`**, 70.57 s | **383 iters, reason 2**, 101.71 s | `A3-onera-m6-sweep-n15_21840/tpc1_computetotals.log:877, :891` |
| **negative control** | `transonicPCOption 2` (the archived script, zero edits) | 400 iters, **reason −5**, terminal denormal 6.544171804409e−310 | 600 iters, **reason −5**, terminal denormal 3.945602898014e−308 | `A3-onera-m6-sweep-n15_21840/ctrl_computetotals.log` |

The control reproduces the 2026-07-30 record **bit-for-bit** — the entire printed CL stall sequence
`1.839195903440e-01, 1.839114940558e-01, 1.839524885689e-01, 1.839160961071e-01,
1.865300757639e-01, 1.841505669984e-01` and the terminal denormal, every digit. Both arms share the
cold-start continuity error `0.5969274433533561` and the same iteration-0 KSP residual
`1.839195903440e-01` — identical linearization state, opposite outcomes. **One token separates
double DIVERGED_BREAKDOWN from double reason-2.**

### 2b. Rung 1 — 21,840 cells: PASS

FD arm pre-registered in `../../A3_FD3_PREREGISTRATION.md` (base commit `4aef4a2f`, addendum
`b9f42631`, each committed before the attempt it governs). Attempt 1 at h=1e−3 returned
**NOT EVALUABLE** by the pre-registered noise-floor rule (component CD deltas 3.3e−6 to 1.33e−5
against 10× the measured baseline drift of 2.107e−6); steps were re-sized *from the measured floor*
and attempt 2 run. Noise floor 1.626e−6; evaluability threshold 1.63e−5; h=1e−2, 2h=2e−2.

| component | adjoint | FD(h) | FD(2h) | Δ vs floor | step-cons. | rel. err | verdict |
|---|---|---|---|---|---|---|---|
| `patchV[1]` (AoA) | 7.64611788e−03 | 7.66002800e−03 | 7.62500232e−03 | 94× | 0.46% ✓ | **0.18%** | **PASS** |
| `shape[115]` (max \|g\|) | −1.24189676e−01 | −1.23048667e−01 | −1.22797280e−01 | 1513× | 0.20% ✓ | **0.93%** | **PASS** |
| `twist[1]` | 1.73254475e−03 | 1.75500957e−03 | 1.66219195e−03 | 22× | 5.29% ✗ | (1.28%) | **NOT A RESULT** — step-inconsistent, no verdict either way |
| `shape[5]` | 7.34091832e−03 | 7.82812275e−03 | 8.47020820e−03 | 96× | 8.20% ✗ | (6.22%) | **NOT A RESULT** — step-inconsistent |

**Arm verdict: PASS** — two evaluable components spanning two DV groups, including the single
largest gradient component, both well inside the 5% band, against a pre-registered rule requiring
≥2 evaluable and all evaluable passing. Logs `fd3_run_attempt1.log`, `fd3_run.log`.

**A disclosed error found en route, which strengthens rather than weakens the arm.** The
pre-registration's quoted reference value for `shape[5]` (−0.12418968) was a mis-parse of a
line-wrapped 120-wide numpy row; the true `shape[5]` is +7.34092e−3, and −0.12418968 is
`shape[115]`. The mapping-by-construction guard held — the arm always perturbed and read the true
component 5 — so only the prereg's quoted number was wrong, and `shape[115]`, the real max-|g|
component, was added under the correctly applied basis.

**Adjoint reproducibility, free:** across three independent adjoint runs (TPC1, FD attempt 1, FD
attempt 2) every compared component is identical to every printed digit, each converging in exactly
**368** iterations.

### 2c. Rung 2 — 42,120 cells: PASS, and stronger than rung 1

Pre-registration `../../A3_RUNG2_N28_PREREGISTRATION.md` (base `22c8e988`, addendum `2b3e6517`
committed before attempt 2). Mesh certified before launch: `checkMesh` clean, 42,120 cells,
`points_sha256 7eb9866e…`, max AR 608.214865637278, max non-orthogonality 61.49354913677975, max
skewness 1.916854554279592 — independently replicated to every digit by a second agent.

| solve | iterations | reason | residual path |
|---|---|---|---|
| CD | **987** | **2** | 2.121211553380e−02 → below the 1e−4 relative target, 237.01 s |
| CL | **1171** | **2** | 1.839192419993e−01 → 1.824629776972e−05, monotone, 423.13 s |

FD arm: noise floor (repeat-baseline drift) 8.093e−07; evaluability threshold 8.09e−06; every
component's CD delta clears it by **45×–3,213×**.

| component | adjoint | FD(h=1e−2) | FD(2h) | step-cons. | rel. err | verdict |
|---|---|---|---|---|---|---|
| `patchV[1]` (AoA) | 7.90292883e−03 | 7.90232345e−03 | 7.90521694e−03 | 0.0366% ✓ | **0.0077%** | **PASS** |
| `twist[1]` | 1.80386732e−03 | 1.80882369e−03 | 1.80327914e−03 | 0.3065% ✓ | **0.2740%** | **PASS** |
| `shape[115]` (runtime argmax \|g\|) | −1.30055677e−01 | −1.30078078e−01 | −1.30084297e−01 | 0.0048% ✓ | **0.0172%** | **PASS** |

**Arm verdict: PASS**, all three components evaluable and all three inside 5% — stricter than rung
1, where two of four were step-inconsistent. The runtime `argmax|g|` selection chose `shape[115]` on
its own, with no hand-transcribed index, which is what prevented a repeat of the rung-1 mis-parse.

**Attempt 1's `-3` was refused, not mapped.** It returned CL reason **−3** at exactly the default
`gmresMaxIters` 1000 after a monotone 1407× descent. Calling that DIVERGED would have been a false
statement; the pre-registered addendum predicted a raised budget alone would finish it, and attempt
2 (cap 1000→2000) **reproduces attempt 1's iteration-1000 residual as 1.307615740828e−04 against
1.307615741156e−04 — ten significant digits** — then converges at 1171. The two runs are the same
solve, one truncated. Logs `A3-rung2-n28-tpc1/tpc1_computetotals_attempt{1,2}.log`, `fd3_run.log`.

### 2d. Rung 3 — 79,560 cells: DIVERGED

| solve | iterations | reason | residual |
|---|---|---|---|
| CD | **4000 (the cap)** | **−3** | 2.121343646203e−02 → **1.615245992220e−02** |
| CL | never attempted | — | DAFoam raised `AnalysisError("Adjoint solution failed!")` after CD |

`A3-rung3-n52/rung3_stage1.log:915` — `**Completed**! Total iterations: 4000.
PetscConvergedReason: -3. 1416 s`. Ledger rc=1, 95.07 core-min.

**Why this `-3` is a wall and rung 2's was a budget** — a distinction pre-registered before either
was seen (`../../A3_RUNG3_N52_PREREGISTRATION.md` §5):

| | rung 2 CL (`-3`, budget) | rung 3 CD (`-3`, **wall**) |
|---|---|---|
| total residual reduction | **1407×**, monotone | **1.31×** |
| behaviour at the cap | still descending ~3× per 100 iterations | **flat** |
| residual change, iter 1300 → 4000 | n/a (converged at 1171) | **3.79e−07 relative over 2,700 iterations** |
| resolved by raising the cap? | **yes** — converged at 1171 | **no** |

**It is not a memory death, and that is what makes the verdict sayable.** Peak container usage
**11.65 GiB against a 22 GiB cap**, host MemAvailable never below 17 GB, no swap growth, no OOM.
Under the family rule a memory death is NOT EVALUABLE and never a conditioning verdict; memory was
comfortable and the solver still would not converge, so this **is** a conditioning result.

**Stage 2 (the FD arm) was correctly NOT LAUNCHED** — pre-registered as conditional on stage 1
converging. ~60–70 core-min not spent. Rung 3 total 111.0 core-min against an approved 170–190.

**A pre-registered cost law was falsified, and that is the rung's most durable output.** Rungs 1→2
gave iteration exponents of cells^1.50 (CD) and cells^1.70 (CL), predicting **CD ≈ 2,570 iterations**
at rung 3. The exponent **breaks by kind, not by magnitude**: no convergence at all. *"A two-point
slope in this family is a description of the two points, not a cost law."* Any extrapolation toward
the 399,360-cell class is now foreclosed by measurement.

### 2e. Twelve conditioning levers eliminated, with numbers

`../../A3_TRIAGE_LEVERS_PREREGISTRATION.md`, `../../A3_SAAD_DELIBERATE_CONDITIONING_PREREGISTRATION.md`,
`../../A3_STAGE2_UNREACHABLE_CLASS_PREREGISTRATION.md`, `../../A3_NONNORMALITY_DIAGNOSTIC_PREREGISTRATION.md`,
`../../A3_RUNG3_FILL1_ENGINEERING_PREREGISTRATION.md`, `../../A3_RUNG3_RESTART_CHALLENGE_PREREGISTRATION.md`:

- preconditioned **κ = sMax/sMin = 9.57e+10** at rung 3, measured through `KSPComputeExtremeSingularValues`
- diagonal spread **14.47 decades** at rung 3 vs **14.40** at the *converging* rung 2 — the
  discriminator does not discriminate
- `asmOverlap` 1→2: **1.062× worse**
- `pcFillLevel` 0→1: residual improves only **1.859×** despite a ~7-order improvement in the
  mid-cycle condition number
- `gmresRestart` 200→1000: **1.647×** against a pre-registered 10× bar
- `-ksp_type lgmres`: **5.10× worse**; `-pc_type gamg`: **diverges catastrophically**, reason −5,
  residual 7.554e+179 (both only reachable at all on `dafoam-kspopts:v1`)
- Hutchinson non-normality ratio **0.617** against a ≥3.0 bar — **the stalling rung is *less*
  non-normal than the converging one**
- L3 Richardson, a material winner at rung 1 (−43%/−45% iterations), **collapses to double `-5` at
  exactly iteration 200 — `gmresRestart`, the first restart boundary — at rung 2**, and was
  withdrawn *before* rung 3 launched. That mandatory transfer test is what stopped rung 3 launching
  on a lever that would have collapsed it, for 15.93 core-min.

---

## 3. Verdict rows per rung — SHIPPED and PATCHED kept separate

**No patched-IDWarp arm was ever run on A3, at any mesh size.** The PATCHED column is therefore
PENDING everywhere, not clean-by-omission.

| rung | cells | image / toolchain | arm | measured | verdict |
|---|---|---|---|---|---|
| original | 399,360 | SHIPPED `dafoam/opt-packages:latest`, stock IDWarp | primal | CD 0.0229955633492643 / CL 0.3131158872361974 | **GATE REACHED** |
| original | 399,360 | SHIPPED | Cp vs AGARD 2308 | pressure RMS 0.0128–0.0265; suction 0.0491–0.1139 | **PASS** |
| original | 399,360 | SHIPPED | adjoint / FD | none — 8 mitigations exhausted | **BLOCKED** |
| original | 399,360 | PATCHED | — | never run | **PENDING** |
| coarse | 99,840 | SHIPPED | adjoint | reason −5 at ILU(0), then OOM | **BLOCKED** |
| vcoarse | 24,960 | SHIPPED | decomposePar | SEGV ×2 | **BLOCKED** (not evaluable) |
| **sweep 1** | **21,840** | SHIPPED-equivalent (`dafoam-subpclu:v1`, env unset), stock IDWarp | adjoint | 368 / 383 iters, reason 2 | **GATE REACHED** |
| **sweep 1** | **21,840** | SHIPPED-equivalent | FD, 4 components | patchV[1] **0.18%**, shape[115] **0.93%**; 2 not evaluable | **PASS** |
| **sweep 1** | 21,840 | PATCHED | — | never run | **PENDING** |
| **sweep 2** | **42,120** | SHIPPED-equivalent | adjoint | 987 / 1171 iters, reason 2 | **GATE REACHED** |
| **sweep 2** | **42,120** | SHIPPED-equivalent | FD, 3 components | **0.0077% / 0.2740% / 0.0172%**, all evaluable | **PASS** |
| **sweep 2** | 42,120 | PATCHED | — | never run | **PENDING** |
| **sweep 3** | **79,560** | SHIPPED-equivalent | adjoint | 4000 iters, reason −3, 1.31× reduction | **GATE FAIL** (stagnation; memory comfortable at 11.65/22 GiB) |
| **sweep 3** | 79,560 | SHIPPED-equivalent | FD | correctly not launched | **NOT A RESULT** |
| negative control | 21,840 | SHIPPED-equivalent, `transonicPCOption 2` | adjoint | reason −5 ×2, bit-identical to the 2026-07-30 record | **GATE FAIL, as designed** — this arm's job was to fail |

**The reopened ladder's ceiling is bracketed between 42,120 and 79,560 cells, and is not located.**
Nothing here says 79,560 is *the* boundary, and nothing says the M6 adjoint is unreachable at that
size by any means — only that the configuration working at two rungs stagnates at this one with
memory to spare.

---

## 4. The 1.26% residual under the patch — what it is, and what it is not

`../../ROOTCAUSE_getRotationMatrix3d.md` §4.2 and §9.4 report an **ONERA M6 geometry reading 1.26%
that survives the rotation patch**. Two things must be said precisely, because the name invites a
mistake.

**It is not this CFD case.** The 1.258–1.26% figure is measured on **IDWarp's own `onera_m6` test
mesh under a shear-sweep deformation**, one of the five geometries in `repro_geometries.py` taken
verbatim from upstream's `tests/test_USMesh.py`. It is a pure mesh-warp `verifyWarpDeriv` number
with **no DAFoam, no OpenFOAM, and no CFD anywhere in it**. It is not an adjoint/FD gradient error
on Ladder A3's wing, and there is no A3 CFD number to compare it against — A3 has never been run on
patched IDWarp (§3).

**What it is: the second regime, and its survival is a passed prediction.** The rotation patch fixes
regime 1 (the guard firing at `n ≈ n0`, where the derivative is set to exactly zero). Regime 2 is
the ill-conditioned band just *above* the threshold, where `1 − arg²` is formed by catastrophic
cancellation from an `arg` carrying `eps` of roundoff. `PATCH_getRotationMatrix3d.md` §6 stated
**before the runs** that the patch would leave regime 2 untouched; §9.4 confirms the `onera_m6`
`verifyWarpDeriv` lines are **bit-identical** patched vs unpatched, "exactly as §6 predicted for a
patch that only touches the degenerate branch." The measured error-vs-angle curve
(`ROOTCAUSE…md` §6.4): 1e-5 rad → 4.1e-08; 1e-6 → 6.7e-05; 1e-7 → 4.0e-04; 5e-8 → 1.2e-02;
≤1.49e-08 → 1.0 (guard). The 1.26% sits in that band.

**Why it matters for A3 specifically, and this is the operationally important part.** A
`check_totals` is evaluated at the undeformed baseline, where regime 1 dominates. **An optimiser is
not.** From iteration 1 onward every gradient is evaluated on a deformed mesh where the guard no
longer fires and regime 2 takes over — and regime 2 **is not patched, and its recommended fix
changes the primal's floating-point path**, so it cannot be delivered by a primal-bit-identical
proof-of-concept. Any future A3 optimisation would run on gradients this class of verification has
never graded.

**Verdict on the 1.26%: NOT A RESULT for Ladder A3** — right mesh name, wrong object. Recorded here
only so the number is not later cited as an A3 gradient error.

---

## 5. What this grading cannot see

1. **No patched-IDWarp arm exists for A3 at any mesh size.** A3's PASS rows are stock-IDWarp
   results, so they carry whatever rotation-defect content this case's `dObj/dXv` field happens to
   contract with — which on A1, A2, A5 and the sail was 97–99.5% of the error. That A3's rungs pass
   at 0.0077–0.93% *without* the patch is genuinely interesting and is not explained.
2. **Rung 1's and rung 2's PASS rest on 2 and 3 components respectively**, not on a full-vector
   `check_totals`. The vector-norm aggregate over the full DV set has never been computed at either
   rung. A5's idx16 is the standing demonstration that a component nobody looked at can be the one
   that matters.
3. **`twist[1]` and `shape[5]` at rung 1 carry no verdict in either direction** — they are the two
   smallest signals and their step-inconsistency is the plateau-noise/O(h²) tradeoff. They are not
   passes and they are not failures.
4. **The limiter lever was never varied on A3.** A3's `fvSchemes` uses `div(phi,U) Gauss
   linearUpwindV` and `div(phid,p) Gauss limitedLinear 1.0` (`../../A3_onera_m6.md`, Stage 2 §4). The
   `limited`/`default` arm that moves A1 from 92.8% to 0.121% has no A3 counterpart.
5. **The decomposition axis was never varied on A3.** Every rung ran np=4 on one partition. Per the
   decomposition report, a gradient consistent under the tested decomposition certifies nothing
   about the parallel operator.
6. **Campaign 2's rungs do not license any statement about Campaign 1's mesh.** 399,360 cells is
   4.7× rung 3, which already stagnates, and 18.3× rung 2, the largest that passes.

---

## 6. Ledger

| item | value |
|---|---|
| solver core-minutes spent by this document | **0.00** |
| dollars spent | **$0.00** |
| containers started | 0 |
| frozen files edited | 0 |
| filed upstream | nothing |
