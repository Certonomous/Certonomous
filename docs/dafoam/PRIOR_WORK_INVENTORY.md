# DAFoam prior-work inventory — Part A: Ladder A, defects, patched builds

**Owner: Lane A of the DAFoam team. Created 2026-08-21. Part B (Ladder B, F6, S1, supervision and
family records, DOCKET/LESSONS cross-refs) was written by Lane B and merged below as '# PART B'
by the supervisor on 2026-08-21 (merge was mechanical; no numbers changed).**

---

## 0. Header — method, and what this document is and is not

**Method.** Every row below cites the `.md` (and where useful the line) it came from. Nothing is
from memory and nothing is inferred from a number's plausibility. Where two records disagree, both
are shown and the disagreement is named rather than resolved by preference. Where a record was
later superseded, struck or retracted **inside the record itself**, that supersession is carried
here — the ladder records are heavily amended in place and reading only their headline sections
gives the wrong answer in at least four places.

**Two conventions that matter for reading every percentage in this file.**

1. **SHIPPED vs PATCHED are never blended.** The lab's headline verdicts (11.43%, 46.64%, …) are
   against the *shipped* toolchain — DAFoam 5.0.0 + IDWarp 2.6.2 as installed in
   `dafoam/opt-packages:latest`. The much smaller numbers (0.037%, 2.24%, …) are against a
   **locally patched IDWarp that exists only as a host-side scratch clone and is in no container
   image** (`docs/dafoam/TOOLCHAIN_INVENTORY.md` §4). Nothing a reader can install produces the
   patched numbers. In §1 they are separate rows.
2. **The percentage metric is OpenMDAO's vector-relative error** `‖Jan − Jfd‖ / ‖Jfd‖` over the
   whole design-variable group, not a per-component error. The lab's own step-size study shows this
   aggregate is *fragile*: on one case at one well-converged plateau it swings 4.28% → 11.52% with
   nothing changing but the FD step (`ladder-a/A_stepsize_study.md`, sweep table). **None of the
   three DAFoam method papers uses this metric** (§7) — they report per-component relative error or
   agreement in significant digits. Comparisons of a lab percentage against a paper percentage are
   therefore not like-for-like, and this document does not make any.

**Nothing in the corpus has been filed, sent, uploaded or registered anywhere.** Three
filing-ready reports exist; all three carry an explicit NOT FILED status. See §2.

---

# PART A — Ladder A, defects, patched builds, toolchain-facing records (Lane A, 42 records)

## 1. Ladder A — one row per case, SHIPPED and PATCHED kept apart

Toolchain image for every row is `dafoam/opt-packages:latest` unless stated. "PATCHED" means
stock image + bind-mounted `/home/ubuntu/certonomous-runs/W5-patch/idwarp` on `PYTHONPATH`
(IDWarp rotation fix only; DAFoam itself unpatched).

### 1a. A1 — NACA0012 incompressible (official DAFoam tutorial)

| field | SHIPPED toolchain | PATCHED toolchain (rotation fix) |
|---|---|---|
| mesh cells | **4,032** (`ladder-a/A1_naca0012_incompressible.md:32`) | same, primal bit-identical |
| what ran | np=2, `DASimpleFoam`, `run_model`/`compute_totals`/`check_totals`, `--memory=8g`; 3.51 core-min total (`A1…md`, stage table) | np=2, `check_totals`, 65 s + 53 s = 3.9 core-min for the pair (`W5_GRADIENT_REGRADE.md` §5) |
| verdict AS RECORDED | **FAIL** — "A1 `CD wrt shape` = 11.43%, graded FAIL — HOLDS as published" (`W5_GRADIENT_REGRADE.md` §1); re-affirmed 2026-08-15: "FAIL against the shipped toolchain stands and is not in doubt" (`S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §1.4) | PASS-equivalent; **not a shipped verdict** |
| numbers | CD/shape **11.43%** (`1.142743e-01`, analytic 6.460294e-02 vs FD 6.489575e-02, `A1…md:115`); CL/shape 1.671%; CD/patchV 0.232%; CL/patchV 0.232%; volcon 4.4e-14, thickcon 1.3e-13, rcon 1.4e-10. **1 sign flip, idx6**, worst component **640.2586%** (`W5_GRADIENT_REGRADE.md` §7.1). idx6 alone carries **82.7%** of the squared-error norm (`A_stepsize_study.md:53`) | CD/shape **0.03745%** (305-fold error reduction, 7.415918e-03 → 2.430027e-05); CL/shape **0.01494%** (112-fold); idx6 **1.1649%, right sign**; **8/8 in band, 0 flips** on both CD and CL (`W5_GRADIENT_REGRADE.md` §1, §7.1). 196 of 204 Jacobian entries bit-identical to the stock run |
| root causes found | **M1** IDWarp `getRotationMatrix3d` degenerate-branch guard — root-caused to `src/utils/vectorUtils.f90:58` and confirmed by a primal-identical repair (`ROOTCAUSE_getRotationMatrix3d.md` §5). **M2** the `cellLimited` slope limiter's min/max stencil selection on the reverse tape — *characterised, not root-caused* (`S1_…HEAD_SETTLEMENT…md` §1.4). **Both flip component 6 of the same case, and M2 was measured with M1 already patched** (§1.1 E4) | — |
| what was patched, and where | `rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch` (2 files, +44 lines, `src/adjoint/output{Reverse,Forward}/vectorUtils_{b,d}.f90`); applied to the clone `/home/ubuntu/certonomous-runs/W5-patch/idwarp`; **no container image carries it** | — |
| what was never filed | the IDWarp report (`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md`: *"Status: NOT FILED ANYWHERE. No issue has been opened, no maintainer has been contacted, nothing has been posted."*). The M2 limiter finding is not in any prepared upstream report as a DAFoam issue | — |
| what remains open | M2 has **no operator-level measurement** (priced C-3, ~2 core-min); M2's one-word cure is **not primal-neutral** — converged CD moves **2.6711%** and the FD reference **5.294%**, so its 0.121% is agreement on a different flow (`S1_…HEAD_SETTLEMENT…md` §1.1 E5); whether stock IDWarp + limiter is worse than either has no arm; **`forceMeshWaveFrozen` is executed-REFUTED as the mechanism** (`grep` finds `forceMeshWaveFrozen 1;` in *both* stock and patched logs) yet `A1_naca0012_incompressible.md:167-168` still names it (and reinforces it at `:171-172` with "same case, same mechanism") with **zero strike or amendment marker** | 0.03745% residual is FD-truncation level and is not open |
| source .md(s) | `ladder-a/A1_naca0012_incompressible.md`, `A_stepsize_study.md`, `W5_GRADIENT_REGRADE.md` §1/§7.1, `ROOTCAUSE_getRotationMatrix3d.md`, `PATCH_getRotationMatrix3d.md` §9.2, `S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §1, `DEFECT_ROBUSTNESS_mesh_and_setup.md` R7, `VERIFICATION_A1_serial_limiter_supervisor_sweep.md` | |

### 1b. A1 serial-limiter arm — a second, independent A1 failure (SHIPPED-configuration, patched IDWarp)

| field | value |
|---|---|
| mesh / what ran | 4,032 cells; np=1 **and** np=4-scotch; `check_totals`; **patched IDWarp already in place** (`IDWARP_IMPORTED_FROM: /patch/idwarp/…` at line 3 of all four arm logs) |
| verdict AS RECORDED | the limiter breaks the **serial** adjoint; supervisor sweep: **"all five axes CONFIRMED"** (`VERIFICATION_A1_serial_limiter_supervisor_sweep.md`) |
| numbers | `div(phi,U) bounded Gauss linearUpwind limited` + `gradSchemes limited cellLimited Gauss linear 1`: CD/shape **92.8%** (`9.284586e-01`) at np=1 and `9.280696e-01` at np=4 — decomposition-invariant to **3.9e-04**; CL/shape 7.86%; **one sign flip, index 6** (analytic −0.02591213 vs FD +0.00849673). One-word lever `limited` → `default`: **0.121%** (`1.213592e-03`). Unlimited control: 0.0428% |
| the kink hypothesis, closed | the sweep mined the FD legs' own one-sided slopes at zero compute: at idx6 both one-sided slopes are **positive** (+0.0053 to +0.0143 across four secants) while the analytic is **−0.0259** — the analytic lies outside the [backward, forward] bracket, on the wrong side of zero, at 3× the magnitude. All 17 primal solves in all four logs print `Minimal residual … satisfied the prescribed tolerance 1e-08`, worst 9.99e-09 |
| what remains open | whether the limited tape is an *operator* defect of A4's kind or an FD-visible tape inconsistency only. Two findings named against the record: (F1) step-stability alone cannot exclude a symmetric kink; (F2) the "no acquisition" verdict's instrument was adopted post-hoc |
| source | `DEFECT_ROBUSTNESS_mesh_and_setup.md` R7/R7f, `VERIFICATION_A1_serial_limiter_supervisor_sweep.md` axes 1–3, `UPSTREAM_BUG_REPORT_decomposition_adjoint.md` acquisition addendum §2 |

### 1c. A2 — MACH Tutorial Wing (aero-only variant)

| field | SHIPPED toolchain | PATCHED toolchain |
|---|---|---|
| mesh cells | **38,304** (`ladder-a/A2_mach_tutorial_wing.md:7`) | same |
| what ran | np=4, `DARhoSimpleFoam`, `--memory=12g`; **`runScript_AeroOnly.py`**, not the shipped aerostructural `runScript.py`; `run_model` + `compute_totals` + `check_totals` + **`run_driver` (IPOPT)**; 485.34 core-min useful / 692.47 including a wasted OOM-killed attempt | np=4 `check_totals`, 236.7 core-min |
| verdict AS RECORDED | **"Verdict: verified, at or better than the calibration scale… Gate passes"** (`A2…md` §4). Regrade: **"All six VERIFIED rows HOLD, PASS at both toolchains"** (`W5_GRADIENT_REGRADE.md` §3a retraction block) | same rows, 34–115× tighter |
| numbers (extracted grading, 18 rows) | CD/shape (96 DVs) **1.71%** (`1.713791e-02`); CL/shape **1.17%**; CD/twist (7) **0.389%**; CL/twist **1.12%**; CD/patchV 0.0212%; CL/patchV 0.0015%; thickcon/shape 9.55e-11 %; volcon/shape 3.53e-10 %; lecon/tecon exact 0. **No sign flips recorded.** Primal CD 0.02772949388, CL 0.4775877833, reproduced from a pristine clone **to all ten printed digits** | CD/shape **0.0506%** (33.9×); CL/shape **0.0219%** (53.2×); CL/twist **0.0097%** (115.1×); **CD/twist DEGRADES 0.389% → 0.505%** — the one counter-instance, reported as such; every FD magnitude identical between halves on all 18 rows |
| root causes found | A2's rows were **~97–99% rotation defect** — the same M1 mechanism, invisible because the aggregate sat in the "1–12% normal band" (`W5_GRADIENT_REGRADE.md` §3, §3a). A2 is **decomposition-clean** (~1e-04 scotch vs simple) | — |
| what was patched | nothing in A2 itself | rotation patch as above |
| what was never filed | nothing about A2 was ever filed | — |
| what remains open | the **28.3% drag reduction** (0.029619634 → 0.021244538 at matched CL=0.5) came from a **time-boxed, unconverged** IPOPT run: 47 of ~100 major iterations in 60 min, `inf_pr` 1.44e-05 / `inf_du` 9.0e-05 against a 1e-5 tolerance, and `opt_IPOPT.txt` contains **zero occurrences of "EXIT" or any convergence statement** (`ladder-a/A2_optimization_history.json`, fields `converged_to_optimizer_tolerance: false`, `convergence_statement_in_log: null`). The **preserved A2 case directory is unusable** — its baseline reads CD 0.03142017502 vs the published 0.02772949388, because the IPOPT run left the mesh deformed; a mesh rebuild lands at 0.02964132667, 6.9% off. That provenance failure cost 238.4 core-min at perturbation 132 of 211 | — |
| source .md(s) | `ladder-a/A2_mach_tutorial_wing.md`, `ladder-a/A2_optimization_history.json`, `W5_GRADIENT_REGRADE.md` §3/§3a/§3b/§5, `W4_CARRY_TO_BLOCKED_RUNGS.md` | |

### 1d. A3 — ONERA M6 transonic. **Two distinct campaigns; do not merge them.**

**Campaign 1 — the original ladder rung (2026-07-28), 399,360 cells: adjoint BLOCKED by memory.**

| field | value |
|---|---|
| mesh cells | **399,360** (`ladder-a/A3_onera_m6.md:43`); coarsened variants 99,840 and 24,960 |
| what ran | np=4 (and np=2), `DARhoSimpleCFoam`, `dafoam/opt-packages:latest`; flow condition **deliberately changed** from the tutorial's U0=285 to **U0=291.6 m/s, aoa0=3.06°** to hit AGARD Case 2308's M=0.84; verified M_inf = 0.839968 |
| verdict AS RECORDED | primal **accepted** (CD = 0.0229955633492643, CL = 0.3131158872361974) with an honest caveat that the strict `primalMaxRes < 1e-8` message never printed; Cp validated against AGARD AR-138 / NASA-TMR Case 2308; **"Stage 3 — ONE FD-verified adjoint gradient: BLOCKED"** |
| numbers | Cp suction-surface RMS deviation 0.049–0.114, pressure surface 0.013–0.027; CFD shock aft of experiment at 6 of 7 stations by 0.02–0.10 x/c; eta=0.99 outlier RMS 0.114, bias +0.065. **No gradient number exists for this rung.** 8 mitigations tried and ruled out (2 memory caps 12g/18g, 2 rank counts, `gmresRestart` 1000→200, `pcFillLevel` 1→0); OOM at 399,360 and at 99,840; SEGV in `decomposePar` twice at 24,960 |
| root cause found | OpenMDAO's reverse sweep unavoidably builds `d[residuals]/d[vol_coords]` for **any** requested total derivative, so restricting `wrt=patchV` does not avoid a mesh-sized matrix |
| what remains open | this rung's adjoint. Note the 2026-08-15 settlement: the "memory wall" label is **misnamed at its source** — `PRODUCT_LIST.md:179` says A3 is *"conditioning, not memory"* while `:251` calls it a memory wall (`S1_…HEAD_SETTLEMENT…md` §3.6) |
| source | `ladder-a/A3_onera_m6.md` |

**Campaign 2 — the reopened sweep ladder (2026-08-08 → 08-11). This is where A3's gradients live.**
Image `dafoam-subpclu:v1` with `DAFOAM_SUBPC_TYPE` **unset** (= shipped behaviour, banner absent),
stock IDWarp, np=4. The single functional change from the archived configuration is
`transonicPCOption: 2 → 1`.

| rung | cells | adjoint | FD verification | verdict AS RECORDED |
|---|---|---|---|---|
| **1** | **21,840** | CD **368 iters**, CL **383 iters**, `PetscConvergedReason: 2` — "**CONVERGED — the A3 ladder REOPENS**… First time in this family's history, at any mesh size, ever" | **ARM PASS**: patchV[1] adjoint 7.64611788e−03 vs FD 7.66002800e−03 = **0.18%**; shape[115] −1.24189676e−01 vs −1.23048667e−01 = **0.93%**; twist[1] and shape[5] **not evaluable** (step-inconsistent at 5.29% / 8.20%) | **PASS** (`A3_SUBLU_RESULT.md`, FD-VERIFICATION RESULT) |
| **2** | **42,120** | CD **987**, CL **1171**, reason 2 (needed `gmresMaxIters` 1000→2000; the first `-3` was budget, proven by the iteration-1000 residual reproducing to **ten significant digits**) | **PASS, all three components**: patchV[1] **0.0077%**, twist[1] **0.2740%**, shape[115] **0.0172%**; noise floor 8.093e−07, every delta clears by 45×–3,213× | **PASS** (`A3_RUNG2_N28_RESULT.md`) |
| **3** | **79,560** | CD **4000 iters (the cap), reason −3, stagnation** — 1.31× total residual reduction, residual changes **3.79e−07 relative between iterations 1300 and 4000**; peak memory **11.65 GiB against a 22 GiB cap**, so this is a conditioning result, not a memory death | not launched (pre-registered as conditional) | **DIVERGED** (`A3_RUNG3_N52_RESULT.md`) |

**Negative control, causation nailed:** the archived configuration (`transonicPCOption 2`) rerun on
today's host reproduces the 2026-07-30 `-5` record **bit-for-bit** — the entire printed CL stall
sequence `1.839195903440e-01, 1.839114940558e-01, … 1.841505669984e-01` and terminal denormal
`3.945602898014e-308`, every digit. Both arms share cold-start continuity error
`0.5969274433533561`. One token separates double DIVERGED_BREAKDOWN from double reason-2.

**Twelve levers eliminated at rung 3** (`A3_TRIAGE_LEVERS_PREREGISTRATION.md` §8/§10,
`A3_SAAD_DELIBERATE_CONDITIONING_PREREGISTRATION.md`, `A3_RUNG3_FILL1_…`, `A3_RUNG3_RESTART_CHALLENGE_…`,
`A3_STAGE2_UNREACHABLE_CLASS_…`, `A3_NONNORMALITY_DIAGNOSTIC_…`): measured
**sMax/sMin = 9.57e+10** after preconditioning; diagonal spread **14.47 decades** at rung 3 vs
**14.40** at the converging rung 2; `asmOverlap` 1→2 makes it 1.062× *worse*; `pcFillLevel` 0→1
improves the residual only 1.859× despite improving the mid-cycle condition number by ~7 orders;
`gmresRestart` 200→1000 gives 1.647× against a pre-registered 10× bar; `-ksp_type lgmres` is
**5.10× worse**; `-pc_type gamg` **diverges catastrophically** (reason −5, residual 7.554e+179);
Hutchinson non-normality ratio 0.617 against a ≥3.0 bar — **the stalling rung is *less*
non-normal**. L3 Richardson, a material winner at rung 1 (−43%/−45% iterations), **collapses to
double `-5` at exactly iteration 200 at rung 2** and was withdrawn before rung 3 launched.

### 1e. A4 — Ahmed body, 25° rear slant

| field | SHIPPED toolchain | PATCHED toolchain |
|---|---|---|
| mesh cells | **fine 45,760** (primal comparison) / **coarse 2,777** (adjoint + FD) | coarse 2,777 |
| what ran | np=4 and np=1, `DASimpleFoam` kOmegaSST, `--memory=8g`, 10.91 core-min for the original rung; `primalMinResTol 1.0e-4` | np=4 / np=1, `check_totals` |
| verdict AS RECORDED | **PASS** — but the wording has been rewritten twice inside the file. Original 2026-07-28 "PASS, under this host's own calibration" is struck; a 2026-07-30 CONDITIONAL is struck; the live text reads *"the verdict of record is **PASS** — the 10.04% is an artifact of DAFoam's default `scotch` decomposition on this mesh, not a gradient defect. The graded configuration is **np=1 against the shipped toolchain: 1.10%**"* (`ladder-a/A4_ahmed_body.md:188-200`) | 8.953% at np=4-scotch; 0.00054% at np=4-`simple` 4×1×1 |
| numbers (single scalar FFD shape DV) | **np=1 stock 2.3965e-01 vs FD 2.4232e-01 = 1.10%** (`1.1032e-02`, `a4_np1_stock.log`) — the graded configuration. np=4-scotch stock **2.1821e-01 vs 2.4258e-01 = 10.04%** (`1.0044e-01`, `A4_ahmed_body.md:240`) — the published number. np=4-`simple` 4×1×1 stock 2.4037e-01 / 0.76% | np=1 0.34%; np=2 0.26%; np=3 **6.05%**; np=4-scotch **8.95%**; np=4-simple 4×1×1 **0.00054%**; np=4-simple 1×4×1 0.47%; np=4-simple 1×1×4 0.52%; np=4-simple 2×2×1 1.40%. Baseline CD invariant to 5 sig figs (0.15296979–0.15297237) across every arm |
| root causes found | **the parallel reverse-AD operator is not the transpose Jacobian under `scotch`**. Cross-residual of the mapped scotch ψ under the serial operator: **6.004e+01 = 328.8× ‖b‖**, against an np=1 control of 1.141e-04 and a `simple` arm of 9.37e-02 — while the scotch KSP itself finishes at true-residual 1.7e-07, `PetscConvergedReason: 2`. Error concentrates in **x-momentum rows of partition-interface cells**: 13 of the 15 entries with |r| > 0.5 own a scotch processor face, largest 42.2. Trigger is a **recorded branch**: the `cellLimited` slope limiter gates it (`limited` → `default` collapses the cross-residual to **0.0135× ‖b‖**, a 24,270× improvement, and the KSP from **719 to 41** iterations); `freestreamVelocity` is a necessary ingredient on this case by within-case control (arm N9) | — |
| what was patched | nothing for A4 — **the rotation patch does NOT rescue A4**: it moves the error 10.04% → 8.953%, i.e. ~11% of the gap. The decomposition closes the other ~92%. This was the result the regrade was most at risk of getting wrong | — |
| what was never filed | `UPSTREAM_BUG_REPORT_decomposition_adjoint.md`: **"Status: NOT FILED ANYWHERE. No issue has been opened, no maintainer has been contacted, nothing has been posted."** Submission-readiness table: reproducer on a stock upstream tutorial **NOT DONE**; mechanism to a line **NOT DONE**; discriminating instrument **Done**; independent verification **Done** | — |
| what remains open | the defective **source line** (needs an instrumented rebuild of `libDASolver.so`); the **22.05% primal gap** vs the lab's own `simpleFoam` baseline is **UNEXPLAINED** — its stated SIMPLEC cause was retracted 2026-08-10 after the source was re-read (`pEqnSimple.H:27`, `DAResidualSimpleFoam.C:189`) and `consistent yes` proven **ACTIVE** by a third leg (A1 converges in **435 iterations at `consistent false` vs 490 at `consistent true`**); the **0.2510 frontal-area CD is WITHDRAWN** (computed from a state whose omega field diverged while the normalised residual read converged); `primalMinResTol 1e-4` remains an **unseparated co-ingredient candidate** (1e-4 on both defective cases, 1e-6/1e-8 on all five clean ones) and is structurally un-testable within-case | — |
| source .md(s) | `ladder-a/A4_ahmed_body.md`, `ladder-a/A4_ahmed_body.json`, `W5_GRADIENT_REGRADE.md` §2, `DISCRIMINATORS_A4_decomposition_mechanism.md`, `UPSTREAM_BUG_REPORT_decomposition_adjoint.md`, `DEFECT_REACH_decomposition_cases.md`, `DEFECT_ROBUSTNESS_mesh_and_setup.md`, `VERIFICATION_A4_decomposition_supervisor_sweep.md`, `VERIFICATION_A4_mechanism_supervisor_sweep.md`, `A4_SIMPLEC_ACTIVITY_PROOF_PREREGISTRATION.md` | |

### 1f. A5 — U-bend internal flow, pressure-loss objective

| field | SHIPPED toolchain | PATCHED toolchain |
|---|---|---|
| mesh cells | **4,800** (`ladder-a/A5_ubend_internal.md:56`, `nCells: 4800`) — **not 21,000** | same |
| what ran | np=4, `DASimpleFoam` SA, `--memory=10g`; `UBend_Channel` (not `UBend_CHT`), objective adapted to pure `TP1 − TP2`; `check_totals` `of=["OBJ.val"] wrt=["shapexUpper"]` (27 components), central, `step=1e-4`; 25.95 core-min | np=4, 235 s + 250 s = 32.3 core-min for the pair |
| verdict AS RECORDED | **FAIL** — "FD verification: does NOT cleanly pass… reported as a documented, unresolved finding, not papered over as a pass" (`A5…md`, Bottom line); regrade: "graded FAIL — HOLDS as published against the shipped toolchain" | PASS-band, **not shipped** |
| numbers | aggregate **46.64%** (`4.663773e-01`, analytic 1.938364e+01 vs FD 3.340851e+01, `A5…md:159`); **5 of 27** components within ±12% (idx 1, 2, 16, 24, 25); **2 sign flips, idx8 (207.6%) and idx17 (121.6%)** (`A5…md:194-196`). Stock re-run reproduces the published 27-row table **to every printed digit** | aggregate **2.2372%**, **26/27 in band, 0 flips**; both flips gone (idx8 −0.84337 → +0.78790 against FD +0.78391; idx17 −0.62881 → +2.91314 against +2.90530). **Corrected to 0.1826%, 27/27 in band** once idx16's stored FD reference is re-measured (`W4_IDX16_IS_THE_REFERENCE.md`) |
| root causes found | **M1, the same IDWarp rotation defect as A1.** The clearance was **RETRACTED**: every earlier `warpDeriv` test on A5 used an arbitrary **random seed** and read 0.32–1.30%; under the real `d(OBJ)/dXv` seed the same components read **207.04%** and **121.59%**, sign-flipped — a **160× change from replacing an arbitrary direction with the objective's own**. A solve-free, pure-geometry test reproduces the whole CFD+adjoint disagreement component by component across 2.6%–207% including both flips. Bisection: `dXs/dShape` clean to **2.8e-12 – 6.4e-12**; `dObj/dXv` clean to **0.17–2.49%** at idx8/idx17 across two steps and two path protocols; OpenMDAO assembly exact to **0 – 2.1e-15** | — |
| refuted along the way | the primal-convergence hypothesis (tightening solver tolerances 1–2 orders and running 10× more iterations moved the aggregate 46.64% → 46.21% and made sign flips **worse**, 2 → 3); the residual-plateau-noise hypothesis (measured noise floor: four re-solves span **2.85e-12**, implied FD noise **1.4e-08** — seven orders too small); symmetry-plane proximity (idx8/idx17 sit at the FFD station **farthest** from the plane, sharing it with the two cleanest components); adjoint-solve accuracy (`gmresRelTol` 1e-5 → 1e-12, 10,000× tighter, moves idx8 by **0.0105%** and idx17 by **0.8826%**, both still flipped); `dR/dW` (closed as a `normalizeStates` units convention — 43 of 60 diagonal ratios land on exactly one of four constants 8.4 / 35.28 / 1e-3 / 300 to six significant figures); mesh-warp truncation `evalMode=exact`; matrix reordering `rcm` vs `natural` |
| what was patched | nothing in A5 | rotation patch |
| what was never filed | same IDWarp report, NOT FILED. **A5 falsified a qualification in the draft report**: `shapexUpper` is built by `nom_addLocalDV` — one FFD point, one axis, no combination construction — and idx8/idx17 flip sign anyway, so the report's claim that sign flips require the opposing-direction construction "is now falsified and must be removed" | — |
| what remains open | the **2.2372% residual after the patch is genuinely open and must not be described as root-caused** (A1's patched residual is 0.037%; A5's is 60× higher) — though the idx16 re-measurement puts the true figure at 0.1826%. The bisection is decisive at **idx8 only**; the warp-bypass probe is outside its linear regime at idx17 and idx2. `dF/dW`'s exact scaling pattern (`AN/FD = 35.28` for TP1, `8.4` for TP2, direction-independent) is **open and unexplained**; `getdFScaling` is the named place to look. A5's claimed decomposition-invariance is cited from a run whose `PYTHONPATH` was `/patch/idwarp` — i.e. it covers the **patched** gradient, not the stock one it is cited for | |
| source .md(s) | `ladder-a/A5_ubend_internal.md` (12 addenda), `W5_GRADIENT_REGRADE.md` §4/§7.2/§7.3, `ROOTCAUSE_getRotationMatrix3d.md` §4.4, `PATCH_getRotationMatrix3d.md` §9.3, `W4_IDX16_IS_THE_REFERENCE.md`, `S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §2 | |

### 1g. A6 — CRM wing-alone (SHIPPED only; no patched run exists, no adjoint ever attempted)

| field | value |
|---|---|
| mesh cells | **579,072** (`ladder-a/A6_crm_wingbody.md:47`). Log also prints `Global Adjoint States: 5244840` |
| what ran | np=4, `DARhoSimpleCFoam`, `--memory=12g`, `run_model` only, 431.0 s = 28.73 core-min accepted (38.4 across three attempts). **CRM_Wing, not DPW4_Aircraft** — wing-alone, disclosed as "honestly not a full wing-body reproduction" |
| verdict AS RECORDED | *"This is a genuinely converged primal, not a plateau accepted on faith"*; CD = 0.02090143421526141, CL = 0.5000146055201552 |
| numbers, and the four corrections | **Four published statements about A6 are wrong, all four still live at HEAD, all four free to fix** (`S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §3.7): (1) **"CONVERGED below 1e-8" is WRONG** — `grep -c "satisfied the prescribed tolerance"` on `run_model_run1.log` returns **0**, against positive controls of 21 and 17 on A1 logs; the run stopped at `endTime 1000` and never triggered its own convergence test. `nuTilda` is the binding field and **plateaued at t≈600** (1.318e-7 → 1.182e-7 over 400 iterations, factor 1.115), needing **15,573 further iterations ≈ 419 core-min** to cross 1e-8. (2) **"matches the published tutorial to 0.0067%" is WRONG** — recomputed 0.006862%, but the reference's own resolution is 0.023923% (3.5× coarser) and the run's own CD peak-to-peak over the last four write points is 0.007323%. (3) **the "~8.5e8 temperature-residual signature" is REFUTED three ways** — a validated ONERA run reads 5.9e8 of the same quantity; A4 has **no** `T Residual Norm2` at all (it is incompressible; its collapse was in *omega*); and `he initRes` falls monotonically 1.000 → 4.659e-08, 7.33 decades. (4) **"memory wall" is misnamed at source** — `Main iteration`/`KSP Residual` appear **zero** times in all four A6 logs, so no adjoint linear solve was ever attempted; and the case it inherits the wall from (A3) has an entry in the same file saying *"conditioning, not memory"* |
| what was never filed | nothing about A6 was filed |
| what remains open | **nothing needing compute.** The priced experiment P-2 (restart to `endTime 1250`, quoted ~7 core-min) is **KILLED** — correctly priced at ~419 core-min against a plateau with no sign of breaking. Any 0.0067% re-verification "must never be proposed" — no run can buy it |
| source .md(s) | `ladder-a/A6_crm_wingbody.md`, `A1_A5_A6_DIAGNOSIS.md` §2, `S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §3 |

### 1h. Step-size study (A1 case, 4,032 cells, np=2, `--memory=4g`, 12 invocations)

| field | value |
|---|---|
| verdict AS RECORDED | *"**Predominantly real** — the flat-curve branch, per component"* — 11.43% is **not** a step artefact |
| numbers | full-8-vector error vs step: 1e-8 **94.95%**, 1e-7 52.88%, 1e-6 17.64%, 1e-5 12.27%, 1e-4 11.52%, **1e-3 11.43%**, 5e-3 10.47%, 1e-2 8.94%, 2e-2 **4.28%**, 3e-2 9.83%; **5e-2 and 1e-1 FAIL** (primal non-convergence, idx6 stalls at 4.8e-5). Excluding idx0/idx1/idx6: **dead flat 2.5–3.0%** from 1e-4 to 3e-2, cosine 0.99998. idx6 alone carries **82.7%** of the squared-error norm — matching `PROOF.md`'s independently-derived 82.7%; cosine cross-checks reproduce to 5–6 significant figures |
| what it established | **the grading bands the lab uses**: PASS ≤ 5% with zero flagged components; CONDITIONAL 5–15% with a required per-component breakdown; **> 15% or any flagged component → FAIL**. A component is "flagged" if its FD changes sign or moves > 50% of its own magnitude across one decade of step. Recommended step **1e-3 to 1e-2**, central, `step_calc=abs`. **The old 1–12% "normal band" (n=1, from A1 alone) is retired** |
| the consequential judgement | it downgraded A4's 10.04% from PASS to CONDITIONAL — later overturned by the decomposition finding, but the reasoning ("A4 has a single scalar DV so it cannot exhibit vector-norm dilution") stands |
| source | `ladder-a/A_stepsize_study.md`, `ladder-a/A_stepsize_study.json`, logs in `ladder-a/logs_A1_stepsize/` |

### 1i. Non-ladder case carried in the same regrade (for completeness)

**naca0015_sail_coarse**, 63,920 cells, 8 shape DVs, np=3: published **PASS at 4.52%**; stock
re-run 4.5230%; **patched 0.0246%** — the error was **99.5% rotation defect**. CL/shape 0.53% →
0.0125% (97.6% defect). The comparative claim attached to it — *"better-behaved than the official
NACA0012 tutorial on the same class of derivative"* — **does not survive**: patched, the sail reads
0.0246% and A1 reads 0.0374%, within a factor of 1.5. `W5_GRADIENT_REGRADE.md` §4b.

---

## 2. Defects and candidate defects

| # | defect | status | evidence file | patch location | upstream status | reach (cases touched) |
|---|---|---|---|---|---|---|
| **D-A** | **IDWarp `getRotationMatrix3d` degenerate-rotation branch.** `src/utils/vectorUtils.f90:58` guards a removable coordinate singularity with `tol = 1.4901161193847656e-08` (= `sqrt(eps)`, line 44); Tapenade's reverse at `src/adjoint/outputReverse/vectorUtils_b.f90:123–128` zeroes `magv2b`, `axisb`, `axismagb`, so `dMi/dnormals = 0` **exactly**. At an undeformed baseline `axisMag = sqrt(1e-30) = 1e-15 < tol`, so **branch 0 is guaranteed at every non-corner surface node** — which is precisely the state every `check_totals` and every design iteration 0 evaluates at | **ROOT-CAUSED TO A LINE and CONFIRMED BY REPAIR.** Supervisor sweep: *"the claim survives"*, all four attacks CONFIRMED | `ROOTCAUSE_getRotationMatrix3d.md`, `PATCH_getRotationMatrix3d.md`, `VERIFICATION_rotation_patch_supervisor_sweep.md`, `UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` | `cases/dafoam/rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch` (2 files, +44 lines) → host clone `/home/ubuntu/certonomous-runs/W5-patch/idwarp` (+ built `libidwarp.so`). **In no container image** | **NOT FILED.** *"Status: NOT FILED ANYWHERE. No issue has been opened, no maintainer has been contacted, nothing has been posted."* It **answers** `mdolab/idwarp#57` (open since 2021-07-14, `bug` label applied 8 seconds after creation, **zero comments, five years untouched**) — the patch takes #57's DOF 0/3 from 210.16%/212.62% to **8.56e-06%/3.35e-05%**. Any filing is to be a comment on #57, not a new issue | **Six geometries**: A1 NACA0012, A5 UBend_Channel, and IDWarp's own `symm_block`, `o_mesh`, `co_mesh`, `sym_mesh`, `onera_m6`. Plus A2 (97–99% of its four VERIFIED rows) and naca0015_sail (99.5%). **Not** A4 (only ~11%) |
| **D-A2** | **Second regime of the same parameterisation** — `acos` ill-conditioning just above the threshold. Measured error-vs-angle: 1e-5 rad → 4.1e-08; 1e-6 → 6.7e-05; 5e-8 → 1.2e-02; ≤1.49e-08 → 1.0 (guard) | **REAL, MEASURED, UNPATCHED.** ONERA M6 reads 1.26% and **survives the patch, as predicted**. Cause tested rather than asserted: it is `vectorUtils.f90:69-70`'s `acos` **and** `vectorUtils_b.f90:133`'s cancellation *together* — each alone buys 1.0×–1.6×, the pair buys **3.7e+07×** | `ROOTCAUSE_getRotationMatrix3d.md` §1.6, §6.4, §7 | not patched. The recommended full fix is the reparameterisation `R = I + [v]ₓ + [v]ₓ²/(1+c)` — which **changes the primal's floating-point path**, so a proof-of-concept required to leave the primal bit-identical cannot use it | NOT FILED | ONERA M6 geometry test mesh; any evaluation off the exact baseline |
| **D-B** | **Parallel reverse-AD adjoint operator is not the transpose Jacobian under mesh decomposition.** The KSP converges (reason 2, true-residual 1.7e-07) on an operator that is a **different linear map** from the serial one: cross-residual **328.8× ‖b‖** vs an np=1 floor of 1.14e-04. Defect is in the recorded reverse tape's handling of inter-processor/halo coupling — common to both `dRdWTMatVecMultFunction` and `calcJacTVecProduct`, so not one call site, not the coloring, not the linear algebra. Trigger is a **recorded branch** × a cut that excites its reverse sweep | **SUBSYSTEM-LEVEL, not line-level.** Mechanism claim survives all five supervisor axes | `DISCRIMINATORS_A4_decomposition_mechanism.md`, `DEFECT_REACH_decomposition_cases.md`, `DEFECT_ROBUSTNESS_mesh_and_setup.md`, `UPSTREAM_BUG_REPORT_decomposition_adjoint.md`, `VERIFICATION_A4_{decomposition,mechanism}_supervisor_sweep.md`, `VERIFICATION_reach_matrix_supervisor_sweep.md`, `VERIFICATION_defect_robustness_supervisor_sweep.md` | **no patch exists.** Workarounds only: choose a planar `simple` decomposition, or drop the limiter | **NOT FILED ANYWHERE.** *"Whether it is sent is Katie's call, not the lab's."* Submission readiness: tutorial reproducer **NOT DONE**, mechanism-to-a-line **NOT DONE**; instrument and independent verification **Done**. 63 recorded searches across 10 venues found no prior report; "scotch" appears in **zero** issues and zero discussions in the project's history | **DEFECTIVE: A4 Ahmed-25 (2,777) and Ahmed-35 (2,777) — one mesh family, n=1 as breadth evidence.** Also A4 conformal remesh 2,336 cells, `cellLevel` uniformly 0 → **2.82%**, which refutes the hanging-node hypothesis. **CLEAN: A1 (4,032), A2 (38,304), A5 (4,800), CBFS (21,000), naca0015 sail (63,920)** — all invariant at ~1e-04. **The conjunction does not transplant**: A1 + `freestreamVelocity` + limiter under scotch is decomposition-invariant to 3.9e-04 |
| **D-B2** | **The `cellLimited` limiter breaks the adjoint tape in SERIAL too**, no MPI involved. On A1, 4,032 cells, np=1, patched IDWarp: CD/shape **92.8%** against a step-stable FD, one component sign-flipped; the one-word lever `limited` → `default` gives **0.121%**. On A4 the serial error is only 0.34% — the excitation is case-dependent, as a data-dependent branch's would be | **CHARACTERISED, not root-caused.** No operator-level measurement exists | `DEFECT_ROBUSTNESS_mesh_and_setup.md` R7/R7f, `VERIFICATION_A1_serial_limiter_supervisor_sweep.md`, `S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §1 | none | NOT FILED. Named in the decomposition report as "the better entry point for a maintainer: a single-process reproducer with a one-word on/off switch, no MPI in the loop" | A1 (92.8%), A4 (0.34% serial / gates the 8.95% parallel). **This is the second, independent mechanism that flips component 6 of A1 — the same component as D-A** |
| **D-C** | **DAFoam's adjoint KSP silently discards `KSPSetFromOptions`.** `DALinearEqn.C:138` calls it, then lines 142–343 override `-ksp_type` (hard GMRES), `-pc_type` (hard PCASM), `-sub_pc_type` (hard PCILU), restart, PC side, tolerances. Monitors and viewers are **not** overridden, so a user gets correct diagnostics and silently ignored remedies from the same mechanism | **FILING-READY, NOT FILED.** Class: **diagnosability** — no wrong answer is produced; the defect prevents a user acting on a correct diagnosis. Fix (a) implemented and regression-controlled | `DEFECT_CANDIDATE_ksp_options_override.md`, `A3_KSPOPTS_PATCH_PREREGISTRATION.md` §6 | `cases/dafoam/kspopts_patch/DALinearEqn_kspopts.patch` (one call relocated, 28 diff lines) → image **`dafoam-kspopts:v1`**. Measured behaviour-neutral by default: CD 368 / CL 383 iterations, reason 2, **bit-identical** to unpatched; and `-ksp_view` now reports `type: fgmres` where the unpatched build reports `gmres` | **NOT FILED.** Recommendation revised to **(a) + an effective-value echo** (`KSPGetType`/`PCGetType` queried *after* the options call), because the `printInfo` block still prints `Solver Type: gmres` under an override — the log naming a switch that did not run | The blocked diagnosis it prevented acting on: A3 rung 3, κ = **9.57e+10** after preconditioning, insensitive to every lever DAFoam does expose |
| **D-D** | **`adjUseColoring: False` hard-crashes the v5 mphys Krylov path by construction.** `solve_linear` skips `runColoring()` when the option is False, but `calcdRdWT` unconditionally calls `readJacConColoring()`, which reads a never-written file and aborts in `DAColoring::validateColoring` (`DAColoring.C:1021`) | **USABILITY FINDING, adjacent to D-B.** Workaround (call `runColoring()` explicitly) makes the identity coloring acceptable but the per-column FD assembly is memory-unbounded — on a 2,777-cell case it thrashed an 8 GiB cap and then a 20 GiB cap, dying *after* all 26,149 column evaluations completed | `UPSTREAM_BUG_REPORT_decomposition_adjoint.md`, "Usability finding" | none | NOT FILED | any v5 Krylov adjoint |
| **D-E** | **ASM sub-block ILU hits an exact zero pivot on wall-resolved separated cases** (CBFS 21k, NASA hump 51.6k): `KSPConvergedReason -9 DIVERGED_NANORINF` at iteration 0 for some orderings, flat `-3` for others; PETSc's `MAT_SHIFT_NONZERO` does not catch it because the failure is **factor growth, not a small pivot** | **WORKED AROUND, not filed as a defect report.** Complete LU with pivoting solves the same dumped system | `subpclu_patch/DALinearEqn_subpclu.patch` header; `A3_SUBLU_*` records | `cases/dafoam/subpclu_patch/DALinearEqn_subpclu.patch` → image **`dafoam-subpclu:v1`**, gated behind `DAFOAM_SUBPC_TYPE=lu`, off by default. **The patch file on disk is one hunk ahead of the built image** (the unrecognized-value warning block is NOT in v1 — verified in-image, `TOOLCHAIN_INVENTORY.md` §3) | not filed anywhere | CBFS, NASA hump. Not needed at A3 rung 1 once `transonicPCOption 1` was found |
| **D-F** | **`transonicPCOption: 2` is dead code for `DARhoSimpleCFoam`** — every archived ONERA M6 `-5` ran with the solver's own transonic mitigation silently off | **CAUSATION NAILED** by a bit-for-bit negative control (§1d) | `A3_TPC1_ARM_PREREGISTRATION.md` §2, `A3_TPC1_CONTROL_PREREGISTRATION.md`, `A3_SUBLU_RESULT.md` | not a patch — a `daOptions` value. `DAResidualRhoSimpleCFoam.C:172–176`; `== 1` is the only live value for this solver | not filed | A3, all rungs |

**Community reports, tested and closed** (`W5_COMMUNITY_REPORTS_TESTED.md`, zero solver compute
against a 20 core-min estimate): `mdolab/dafoam` **#905** is **reproduced but its cause is the FD
step, not this defect** — the thread's steps were 1e-5 to 1e-7 and the maintainer said so; the
lab's own sweep on the same tutorial reads 52.879% at 1e-7 and 94.951% at 1e-8, collapsing to
11.427% at 1e-3. **#914** is **not reproducible from the information given** — its
constraint-vs-objective split appears identically with the branch live and corrected, so it
discriminates nothing. Both were **resolved upstream**, contrary to the lab's earlier reading, and
both prior characterisations were **withdrawn**. **#714/#833** is deliberately **not claimed** — its
reported ordering is the opposite of this regime.

**One disclosed gap:** the primary IDWarp reference (Secco, Kenway, He, Mader, Martins, AIAA J
59(4):1151–1168, 2021, doi 10.2514/1.J059491) **could not be retrieved** — five umich URLs return
403, OpenAlex reports `is_oa: false / oa_status: closed / oa_url: null`, Semantic Scholar returns
an empty `openAccessPdf`. The "undocumented" characterisation of `warpDeriv` rests on code, docs
and release notes only, and is explicitly conditional on that gap.

---

## 3. Patched builds and what each patch directory contains

Full detail, including the verbatim `docker images` / `docker history` output and the in-image
md5/line-count diffs, is in **`docs/dafoam/TOOLCHAIN_INVENTORY.md` §3–§5**. Summary:

| image | ID | built on | delta | carries |
|---|---|---|---|---|
| `dafoam/opt-packages:latest` | `9d45679d55fd` | — (single imported 7.83 GB layer, 5 weeks old) | — | stock everything; the digest the root-cause record pins IDWarp 2.6.2 to |
| `dafoam-subpclu:v1` | `ba2d16ab9d57` | opt-packages | +30.6 MB | `DALinearEqn.C` 507 → **526 lines**, md5 `89e71ca2…`; `DAFOAM_SUBPC_TYPE=lu` sub-block LU, **off by default** |
| `dafoam-kspopts:v1` | `d9d2aed02e36` | subpclu | +30.7 MB | 526 → **534 lines**, md5 `96f57628…`; `KSPSetFromOptions` relocated from line 138 to line 351 |

**There is no patched-IDWarp image.** IDWarp ships as a built Python package with no Fortran
sources in the image (`find … -path '*vectorUtils_b.f90'` returns nothing in all three). The
rotation fix lives only at `/home/ubuntu/certonomous-runs/W5-patch/idwarp` and is injected by
bind-mount + `PYTHONPATH`; the version string still reads `2.6.2` either way, which is why every
regrade log prints `IDWARP_IMPORTED_FROM:` as its provenance stamp.

Patch-directory contents: `rotation_branch/` holds the patch plus reproducers
(`repro_issue57_inflate_cube.py`, `repro_geometries.py`, `diag_rotation_ubend.py`), 8 stock
diagnostic logs `D1a…D6`, 8 five-mesh logs, the upstream anchors `issue57_rot_{on,off}.txt`, and
four subdirectories (`patched/`, `patch_unittest/`, `independent_check/`, `supervisor_sweep/`).
`kspopts_patch/` and `subpclu_patch/` hold one `.patch` file each. `upstream_repro/` holds a
self-contained clone-to-result reproducer bundle whose README states **"Nothing here has been sent
anywhere."** `work/`, `work_refined/`, `work_sail/`, `work_wing/` are **live OpenFOAM case trees
with no README** — A1 tutorial + ~15 probe scripts, the 3.65× refinement arm, three sail meshes
and a naca4412 wing.

---

## 4. A2, A3 and A6 specifically — is there an actual extracted grading, or only a claim?

The standing picture says these three "ran, logs exist, verdicts never confirmed." That is true of
**A6 only**. A2 and A3 both carry real, extracted, per-derivative gradings.

### A2 — **actual extracted grading, twice, plus an optimiser run**

Recorded verdict text, quoted: *"**Verdict: verified, at or better than the calibration scale.**
CD/shape (1.71%) and CL/shape (1.17%) both land inside the 1–12% normal band… every
geometric-constraint-vs-shape derivative is at machine precision, confirming the DVGeo/FFD Jacobian
chain is sound. **Gate passes — proceeding to the documented optimization.**"
(`ladder-a/A2_mach_tutorial_wing.md` §4.)

**This is a full 12-row extracted table** — analytic magnitude, FD magnitude, absolute error and
relative error per `of`/`wrt` pair, from a 3,153 s np=4 `check_totals` over 105 design variables
(210 primal re-solves). It was **re-measured in 2026-08-02**: `runScript_AeroOnly.py -task
check_totals`, stock then patched, np=4, returning **18 of 18 rows identical to the published log
to every printed digit**, `CD/shape`'s `1.713791e-02` included. The regrade's own earlier claim
that A2 "could not be regraded" is **RETRACTED in place** — that attempt invoked the wrong script
(`runScript.py`, the aerostructural TACS+MELD variant at `aoa0 = 4.65`, confirmed from
`a2_rebuilt_runmodel.log:688` `Transfer scheme [0]: Creating scheme of type MELD...`) rather than
the aero-only variant at `aoa0 = 4.0` the published numbers used.

The verdict of record is therefore **PASS at both toolchains, six VERIFIED rows HOLD**, with one
counter-instance (CD/twist degrades 0.389% → 0.505% under the patch).

**Log files that contain the grading:**
`/home/ubuntu/certonomous-runs/A2-mach-wing/check_totals_run1.log` (the accepted 18-row table);
`check_totals_run1_INCOMPLETE_prereboot.log` (the OOM-killed attempt, kept as evidence);
`compute_totals_run1.log`; `run_model_stdout.log`; `checkMesh.log`; `preproc_stdout.log`;
`opt_IPOPT.txt` + `opt_run_driver.log` + `OptView.hst` (the optimiser history).
Regrade pair: `/home/ubuntu/certonomous-runs/W4-a2-provenance/a2_ao_{stock,patched}_checktotals.log`,
plus `a2_ct_{scotch,simple}.log` (decomposition arms) and `a2_aeroonly_fresh_runmodel.log`.
Twist-subset pair: `/home/ubuntu/certonomous-runs/W5-regrade/a2_twist_{stock,patched}_checktotals.log`.
**There is no `ladder-a/logs_A2/` directory** — A2's logs were never copied into the ladder tree,
unlike A1/A3/A4/A5/A6.

### A3 — **actual extracted grading, on the reopened sweep ladder, not on the ladder-A record's mesh**

The ladder-A record's own verdict is unambiguous and is a **blocker, not a grading**:
*"**Stage 3 — ONE FD-verified adjoint gradient: BLOCKED** (documented, not hidden)"*
(`ladder-a/A3_onera_m6.md`). No gradient number exists at 399,360 or 99,840 or 24,960 cells.

But the reopened campaign **does** carry extracted per-component gradings, at two mesh sizes, both
pre-registered before the runs:

- Rung 1 (21,840 cells): *"**ARM PASS — the M6 gradient is no longer an existence proof**"*, with a
  four-row table of adjoint / FD(h) / FD(2h) / delta-vs-floor / step-consistency / relative error
  per component (`A3_SUBLU_RESULT.md`, FD-VERIFICATION RESULT §Attempt 2).
- Rung 2 (42,120 cells): *"**CONVERGED + FD PASS. The ladder has two verified rungs**"*, three
  components, all PASS (`A3_RUNG2_N28_RESULT.md`).
- Rung 3 (79,560 cells): *"**DIVERGED by stagnation. The reopened ladder has a ceiling, and it sits
  between 42,120 and 79,560 cells**"* — no grading, correctly not launched.

**Log files that contain the grading:**
`ladder-a/logs_A3/` holds the **primal and Cp** evidence only — `run_model_run{1,2,3}.log`,
`case_2308.dat`, `cp_{extracted,comparison}.json`, `shock_location.json`, the extraction scripts,
and the six **failed** adjoint attempts (`check_totals_fine_12g_run1.log`,
`check_totals_fine_18g_run4.log`, `check_totals_coarse_run{1,2,3}_*.log`,
`check_totals_vcoarse_run1.log`). The **passing** gradings are not in the ladder tree at all; they
are in `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/` (`tpc1_computetotals.log`,
`ctrl_computetotals.log`, `fd3_run.log`, `fd3_run_attempt1.log`, `run_opt5_onera_n15_21840.log`,
`sublu_tpc1_computetotals_attempt{1,2}.log`) and
`/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1/` (`tpc1_computetotals_attempt{1,2}.log`,
`fd3_run.log`) and `/home/ubuntu/certonomous-runs/A3-rung3-n52/` (`rung3_stage1.log`).

### A6 — **no grading exists, and none was ever attempted**

Recorded verdict text, quoted: *"**Accepted result: CD = 0.02090143421526141, CL =
0.5000146055201552** at t=1000… **This is a genuinely converged primal, not a plateau accepted on
faith** — every field residual is below the stated tolerance"* and, on the gradient, *"the gradient
is **known infeasible** on this host per A3's measured evidence… **not attempted**, per explicit
instruction"* (`ladder-a/A6_crm_wingbody.md`, §2 and header).

**This is a claim, and the 2026-08-15 settlement executed it and found it wrong.** The
"every field residual is below the stated tolerance" reading is an **identity-gate**: the `finalRes
< 1e-8` verdict is forced by `relTol 0.1` (0 violations in 66 parsed lines, max ratio 0.099617),
and the run's own convergence test — the `satisfied the prescribed tolerance` line — **never fired
once** in the log, against positive controls of 21 and 17 on A1 logs.

**Log files:** `ladder-a/logs_A6/` (6 files): `run_model_accepted_t0_to_t1000.log` (the only
substantive one, 914 lines), `run_model_attempt2_corrupted_checkpoint_read.log`,
`decomposePar.log`, `logMeshGeneration.txt`, `preproc_stdout.log`, `runScript.py`. Also
`/home/ubuntu/certonomous-runs/A6-crm-wing/` (4 `.log` files total). Attempt 1's log **no longer
exists standalone** — it was overwritten by filename reuse, disclosed in the record. **None of
these contains an adjoint solve**: `Main iteration` and `KSP Residual` appear zero times in all
four.

---

## 5. Standing-picture audit

The supervisor's held picture, line by line, against the records.

### 5.1 Toolchain

| claim | verdict |
|---|---|
| DAFoam 5.0.0 | **CONFIRMED** — measured in all three images today (`TOOLCHAIN_INVENTORY.md` §6a) |
| IDWarp 2.6.2 | **CONFIRMED**; and the installed `idwarp/*.py` are md5-identical to upstream tag `v2.6.2`, commit `647fd8fc2c06fc61b31cc07a7b63ffd4fbaf65ce` (`ROOTCAUSE…md` §1.1) |
| pygeo 1.13.0 | **CONFIRMED** |
| OpenFOAM v2506 | **CONFIRMED** (`WM_PROJECT_VERSION=v2506`) |
| image `dafoam/opt-packages:latest` | **CONFIRMED**, and its digest `sha256:9d45679d55fd…90f07fc` matches the one pinned in `ROOTCAUSE…md` §1.1 — the image on this box is the one every published number was measured on |
| DASimpleFoam | **CONFIRMED as the A1/A4/A5 solver.** **CORRECTED for the rest of the ladder**: A2 is `DARhoSimpleFoam`; A3 and A6 are `DARhoSimpleCFoam` (`A2…md:7`, `A3…md`, `A6…md` §2). Also **CORRECTED in kind**: `DASimpleFoam` is not an executable — `which DASimpleFoam` returns nothing; it is a solver class inside `pyDASolvers…so` |
| PETSc GMRES + ILU(k) | **CONFIRMED**, and quantified: PETSc **3.15.5**, `PETSC_ARCH=real-opt`. `KSPGMRES` at `DALinearEqn.C:142/144`; `PCASM` global PC at `:212`; fill level via `PCFactorSetLevels` |
| PCILU hard-coded in `DALinearEqn.C` | **CONFIRMED**, at **line 266** in the image on this box: `PCType localPCType = PCILU;` then `PCSetType(MLRsubpc, localPCType);` at 267. **Minor correction**: `DEFECT_CANDIDATE_ksp_options_override.md` §2 cites line **286** for this; the live file has it at 266 |
| pyOptSparse shipped but **NO optimiser ever run** | **CORRECTED.** pyOptSparse 2.10.1 is shipped **and an optimiser was run.** `ladder-a/A2_optimization_history.json` is the extracted 48-row per-major-iteration history of a real **IPOPT 3.13.5 (pyoptsparse), MUMPS, limited-memory BFGS** run on A2, 2026-07-28, `tol=1e-5`, `max_iter=100`, **47 major iterations completed in a 60-minute box**, drag reduction 28.275488% from CD 0.029619634 to 0.021244538 at matched CL≈0.5. It is a genuine extraction — `_primary_sources` names `opt_IPOPT.txt` with sha256 `638504c1c412ee…` and 6,546 bytes. **What is true is the weaker statement: no optimiser run has ever converged.** `converged_to_optimizer_tolerance: false`; `convergence_statement_in_log: null`; *"IPOPT prints no EXIT line and no convergence statement anywhere in `opt_IPOPT.txt`; the table simply stops after iteration 47."* |

### 5.2 Cases

| claim | verdict |
|---|---|
| **A1 NACA0012 4,032 cells FAIL shipped, 11.43% error, idx6 sign-flipped, 0.0375% patched** | **CONFIRMED, all four parts.** 4,032 cells (`A1…md:32`); 11.43% = `1.142743e-01` (`:115`); idx6 the single flip, **640.2586%** stock → **1.1649%** right-signed patched; aggregate **0.03745%** patched. One addition: A1's FAIL now has **two** independent mechanisms, not one — the limiter reads 92.8% in serial with the rotation patch already applied |
| **A4 Ahmed 2,777 cells PASS (1.10% np=1 stock); CONDITIONAL until decomposition effect isolated** | **CONFIRMED on the numbers; CORRECTED on the conditionality.** 2,777 cells and 1.10% at np=1 stock (`2.3965e-01` vs `2.4232e-01`, `a4_np1_stock.log`) are exact. But **the CONDITIONAL was withdrawn**: *"A4's CONDITIONAL is withdrawn: it is a PASS"*, and the supervisor sweep confirms the CONDITIONAL→PASS claim on all five axes, with an independent np=2 re-run reproducing a table cell **to every printed digit**. The decomposition effect **was** isolated — to subsystem level (the parallel reverse tape at partition interfaces), not to a line. Residual documentation defect **D-1 is still open**: `A4_ahmed_body.md:158` and `A4_ahmed_body.json` still carry retired wording |
| **A5 U-bend 21,000 cells FAIL shipped, 46.64%, idx8/idx17 > 200% sign-flipped, 0.0000% patched** | **CORRECTED in two places.** (i) **Cell count is 4,800, not 21,000** (`A5…md:56`, `nCells: 4800`). The 21,000 figure belongs to **CBFS**, a conformal-blockMesh case in the decomposition reach matrix; 21,840 is A3's sweep rung 1. (ii) **Only idx8 exceeds 200%** — idx8 is **207.6%** and idx17 is **121.6%** (`A5…md:194-196`); both are sign-flipped. (iii) **"0.0000% patched" is not the `check_totals` figure.** The 0.0000 readings are from the *isolated warp-identity* test (`PATCH…md` §9.3: idx8 3.0e-06, idx17 7.0e-06). The framework's own patched `check_totals` aggregate is **2.2372%**, corrected to **0.1826%, 27/27 in band**, once idx16's stored FD reference is re-measured. **CONFIRMED**: FAIL, 46.64%, both sign flips |
| **A2, A3, A6 ran, logs exist, verdicts never confirmed** | **CORRECTED for A2 and A3; CONFIRMED for A6.** A2 has an 18-row extracted grading, re-measured to every printed digit, verdict **PASS at both toolchains**. A3 has FD-PASS gradings at 21,840 and 42,120 cells and a DIVERGED at 79,560. A6 is the only one with no grading — and the reason is not that nobody looked but that **no adjoint was ever attempted**; four of its published statements have since been executed and found wrong, and all four are still live at HEAD |

### 5.3 The IDWarp defect

| claim | verdict |
|---|---|
| `src/utils/vectorUtils.f90:58` `getRotationMatrix3d` `sqrt(eps)` guard → `dMi/dnormals = 0` at baseline | **CONFIRMED, exactly.** Guard at line 58, `tol = 1.4901161193847656e-08` declared at line 44 (= `sqrt(eps)`). At baseline `axisMag = sqrt(1e-30) = 1e-15 < tol`, so branch 0 is guaranteed at every non-corner node. Independently re-verified line-for-line by a second pass that reused none of the lab's tooling |
| 4-line patch at `cases/dafoam/rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch` | **CONFIRMED with a size correction.** The *mathematical* fix is four lines of assignments in the reverse file's `branch .EQ. 0` block; the **diff is 2 files, +44 lines** (`PATCH…md` §10), because it also patches the forward-mode dual and carries fenced comments. **The path is right but note where the patched code lives**: `src/adjoint/output{Reverse,Forward}/vectorUtils_{b,d}.f90`, the Tapenade-generated files — **not** `src/utils/vectorUtils.f90:58`, which is the primal and is deliberately untouched (primal warp md5-identical, `8fafe12f848af490a5041c865112b5fb`, max diff 0.0) |
| fixes `mdolab/idwarp#57` | **CONFIRMED as an answer to #57.** DOF 0: 210.16% → **8.56e-06%**; DOF 3: 212.62% → **3.35e-05%**; in-plane DOFs 1/2/4/5 untouched to every printed digit; the **AD moved to the pre-existing FD**, which a comparison-rigging artifact cannot produce. **Qualify "fixes"**: it fixes the *first* regime. It does **not** fix D-A2, the near-threshold ill-conditioning — ONERA M6's 1.26% survives the patch, exactly as the patch's own §6 predicted. The patch is a proof-of-concept hand-edit of Tapenade output; upstream should fix the primal's parameterisation and regenerate. **And it has not been filed** |

### 5.4 The decomposition defect

| claim | verdict |
|---|---|
| Parallel adjoint not the transpose Jacobian under decomposition | **CONFIRMED**, and sharpened: it is not the exact adjoint of an equivalent-but-different parallel discretisation either — the scotch analytic disagrees by 8.95% with **its own decomposition's** FD. Cross-residual 328.8× ‖b‖ under the serial operator while the KSP itself converges at true-residual 1.7e-07 |
| scotch 8.95% vs simple 0.00054% | **CONFIRMED**, on the **patched-IDWarp** arms: np=4 scotch 2.2086e-01 / FD 2.4258e-01 = 8.95%; np=4 `simple` 4×1×1 2.4220e-01 / FD 2.4220e-01 = 0.00054%. The **stock** equivalents are 10.04% and 0.76%. Two additions the picture is missing: the effect is **np-dependent** (np=2 scotch 0.26%, np=3 scotch **6.05%**), and the **hanging-node hypothesis is refuted backwards** — scotch cuts 4 of the 456 refinement-interface faces (0.88%), `simple` 4×1×1 cuts 68 (14.91%), and it is the 68-cut arm that is cleanest |
| 56.77 core-min vs 45 budgeted | **CONFIRMED** — 26% overrun on the discriminators item. Two arithmetic slips inside that ledger were caught by the mechanism sweep: the "five decisive arms" subtotal is **12.80**, not the stated 12.63, and one arm's `cpus_cap` was recorded as 1 against a hardcoded 2 |

**Two things in the picture that are absent rather than wrong, and matter:** (1) the picture has no
entry for the **limiter** — which is the *gating ingredient* of the decomposition defect and an
independent serial defect in its own right; and (2) it has no entry for the **inletOutlet
counter-example**: the BC swap that makes A4's gradient read 0.019% leaves the **operator still
wrong at 1.047× ‖b‖, 163,548× its own np=1 floor**. A filed report must not describe
inletOutlet-family configurations as unaffected — *"they are affected and silent."*

---

## 6. Open items, prioritised

**Tier 1 — free or nearly free, and they correct live wrong statements.**

1. **A1's two ladder records still name a refuted mechanism.**
   `ladder-a/A1_naca0012_incompressible.md:167-168` states the idx6 flip was *"traced (candidate
   mechanism, not proven) to `forceMeshWaveFrozen=True`"* and reinforces it at `:171-172`, with **zero
   strike and zero amendment marker**, four days after `forceMeshWaveFrozen 1;` was found active in
   *both* the stock and the patched log — i.e. identically present on both sides of the change that
   removes the flip. Zero compute. `S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §1.1 E3, §4.
2. **A6's four wrong published statements, all live at HEAD, all free to fix.** The "converged
   below 1e-8" claim (0 hits against controls of 21/17), the 0.0067% claim (finer than both
   instruments, 0.023923% and 0.007323%), the 8.5e8 T-residual claim (refuted three ways), and the
   "memory wall" label (`PRODUCT_LIST.md` contradicts itself between :179 and :251). Zero compute.
   `S1_…HEAD_SETTLEMENT…md` §3.7, docket rows D201–D205.
3. **A4's documentation defect D-1.** `ladder-a/A4_ahmed_body.md:158` still says "graded
   CONDITIONAL, not PASS" and `A4_ahmed_body.json` still cites the retired calibration band, against
   a verdict of record of PASS at np=1 stock 1.10%. Named **blocking** by the supervisor sweep and
   still open. Also W-3: the PASS is quoted at **0.76%** in some places and **1.10%** in others —
   name one graded configuration and use it everywhere.
4. **A5's decomposition-invariance claim is cited from the wrong stack.**
   `W4-a5-decomp/run.sh:28` sets `PYTHONPATH=/patch/idwarp`, so the cited measurement covers the
   **patched** gradient, not the stock one it is cited for. Flagged 08-11, re-confirmed live 08-15.
5. **The upstream IDWarp draft carries a claim A5 falsified.** It states the sign-flipping failure
   requires the opposing-direction combination construction; A5 idx8/idx17 are single-point,
   single-axis `nom_addLocalDV` variables and they flip at 207% and 122%. *"That qualification is
   now falsified and must be removed from the report."*
6. **The defect report's three A1 items** (`S1_…HEAD_SETTLEMENT…md` §8.3): the word "identical" in
   the abstract reads as a repair of the same problem when the cure moves the primal 2.67% and the
   FD 5.29%; the D1s summary row should say `primal moves 2.67%` beside D2's `primal
   md5-identical`; and **the strongest fact in the corpus is currently unstated** — that D1s and D2
   flip the same component of the same case, with the D1s arms run against an already-patched
   IDWarp.

**Tier 2 — small, discriminating compute.**

7. **C-3, ~2 core-min:** operator-level cross-residual on A1 **serial** with the limiter — the A4
   instrument applied to D-B2. This is the one measurement that would tell whether the limiter is
   an operator defect of A4's kind or an FD-visible tape inconsistency only. Highest information
   per core-minute in the corpus.
8. **C-2, ~16 core-min:** patched A5 pressure-loss `check_totals` with `useRotations=False`, to
   attack the 2.2372% (or 0.1826%) residual that survives the patch.
9. **The A4 confound separation named and not run:** the ~3–5 core-min control that separates the
   two confounded staging edits in the papers'-protocol arm — np=4 scotch, `inletOutlet` farfield,
   **no** `patchVelocity` input. (Partly answered by arm N9; the report says the causal weight sits
   there.)
10. **The `primalMinResTol` co-ingredient.** 1e-4 on both defective cases, 1e-6/1e-8 on all five
    clean ones — a **third perfect correlate**, structurally un-testable within-case because DAFoam
    treats a tightened tolerance as pass/fail rather than depth. Needs a designed arm, not a knob.
11. **`getdFScaling`** — A5's `dF/dW` scaling pattern (`AN/FD = 35.28` for TP1, `8.4` for TP2,
    exactly, direction-independent) is open and uninterpreted.
12. **A3's ceiling is bracketed, not located** — 42,120 converges, 79,560 stagnates. One arm at an
    intermediate size (~63k) halves the bracket for ~40–60 core-min. The one untried lever whose
    mechanism matches the failure mode is `gmresRestart` 200 → 1000 at rung 3 (memory is available:
    11.65 of 22 GiB used) — though the restart challenge at 1000 already returned only 1.647× against
    a 10× bar, which weakens it.

**Tier 3 — blocked or must-not-be-proposed.**

13. **Mechanism-to-a-line for D-B** requires an instrumented rebuild of `libDASolver.so`. The search
    space is now a single code object: the reverse sweep of the `cellLimited`/`limitedGrad`
    evaluation at processor boundaries, plus the freestream BC update inside the global tape.
14. **A tutorial-based reproducer for D-B** is the last NOT-DONE submission-readiness row that is
    buyable. It should include a `cellLimited`/`limited` convection scheme from the start, since
    that is the shipped-default scheme family of DAFoam's own Ahmed and bluff-body tutorials.
15. **Never propose:** any A6 0.0067% re-verification (no run can buy it — both instruments are
    coarser than the figure); P-2, the A6 restart to `endTime 1250` (quoted ~7 core-min, correctly
    priced at **~419 core-min** against a plateau with no sign of breaking); any A6 adjoint attempt
    on the stated premise, which is misnamed at source.

---

## 7. Appendix — the DAFoam papers' own verification protocol

Read from `docs/papers/adjoint_and_optimization/*.txt`. This is what the toolchain's own authors
did, and it is **not** what this lab does.

| paper | where | reference derivative | step size(s) | agreement criterion | reported result |
|---|---|---|---|---|---|
| **He, Mader, Martins & Maki, C&F 168 (2018) 285–303** | **§3.1, Tables 4 and 5, p.17–18** | brute-force finite difference | reference total derivative: **central difference, step 10⁻⁵**. Adjoint's *internal partial-derivative* FD step swept 10⁻⁵ → 10⁻¹⁰, **best 10⁻⁸** (scaled by `C_W ε`) | **per-component relative error**; no vector norm anywhere | dCD/du0: **−0.00049%** at the best step (26.44% at 10⁻⁵). dCD/dx over 4 FFD points: −0.03062%, −0.00569%, +0.01877%, **+0.25200%**; *"the average error is less than 0.1%"* |
| **He, Mader, Martins & Maki, AIAA J, DOI 10.2514/1.J058853** | **§2.4.2, Table 3, p.15–16** | brute-force finite difference | step-size studies for the **reference total** derivatives 10⁻⁵ → 10⁻², and for the **partial** derivatives 10⁻⁹ → 10⁻⁴, interval 0.1 in the exponent; **most common best: 10⁻³ (total) and 10⁻⁷ (partial)** | **per-row relative error** | 13 rows across 7 solver/turbulence-model combinations; *"The average relative error is less than 0.1%"*; worst row **0.195%** (rhoSimpleDAFoam, k−ω SST). **Jacobian-free is explicitly deferred to "future work"** in this paper |
| **Kenway, Mader, He & Martins, PAS, DOI 10.1016/j.paerosci.2019.05.002** | **§5.1, Tables 3 and 4, p.33–34** | **explicitly NOT finite difference** — *"the finite-difference method is subject to subtractive and cancellation errors, which degrades the accuracy of reference derivatives."* **Complex step** for ADflow; **full-code AD** (`adjointSimpleShapeCheckpointingFoam`) for DAFoam | n/a — no step | **agreement in significant digits** | Jacobian-free matches to **12 digits** (ADflow) and **10 digits** (DAFoam), against flows converged 14 and 12 orders. The **FD Jacobian** option matches to only **3–4 digits, ~0.1% average**. Run on **one CPU core**, deliberately: *"running the cases using one CPU core allows us to isolate the impact of parallel communication on the performance."* Conclusions: *"We do not have scalability data for the Jacobian-free (operator overloading) and the full-code AD (operator overloading) options because we run the adjoint computation only in serial in the ADODG Case 3 (Sec. 5.1)."* |

**Four consequences for this lab, each load-bearing:**

1. **No paper uses the vector-norm relative error.** Every published figure is per-component or
   per-digit. Every headline percentage in §1 is a vector norm. They are different statistics and
   must not be compared.
2. **No paper ever varies the decomposition of anything** — not at fixed np, not across np. The two
   papers that verify in (implied) parallel never state the decomposition; "decompose", "processor"
   and "scotch" are absent from the AIAA J paper entirely. A single-decomposition test cannot see
   D-B even in principle.
3. **The operator D-B lives in has exactly one published accuracy measurement, and it is serial by
   design** — and even that one benchmarked a **different AD tool** (dco/c++ operator overloading),
   where the shipped v5 records its global tape with **CoDiPack**. **The v4/v5 rewrite has no
   archival method paper at all**: the DAFoam publications page lists no framework paper after 2020,
   the README's citation section names only the two He et al. papers, a JOSS search finds nothing,
   and the Zenodo records (15636000 for v4.0.2, 20045081 for v5.0.0) are software deposits.
4. **The lab ran the papers' own acceptance check on the defect's own case, and it passes.** C&F
   2018's Table-4 check (dCD/du0 vs central FD) was run on A4 at np=1 and np=4-scotch: 3.55% and
   3.68% respectively — *"a decomposition-independent protocol floor of this loose-tolerance case,
   not a partition effect."* The pre-registered prediction that scotch would fail was **REFUTED**.
   **The historical check misses the defect twice over: it never varies the decomposition, and the
   configuration it instantiates is one the defect spares.** The papers' own §2.9 nevertheless names
   the delicate region — interprocessor boundary-patch state updates are *"essential for accurately
   computing the adjoint derivative"* — for the v1 architecture that handled them by *executing*
   the update; v5 must *record* it on the reverse tape, and that is where the cross-residual
   concentrates.

---

*Lane A, Phase 0. Reading and inventory only. No solve was launched. Nothing was sent, filed,
uploaded or registered anywhere. No frozen record under `cases/dafoam/` was edited.*

---

# PART B — Ladder B, F6 series, supervision records, DOCKET/LESSONS/NUMERICS cross-references (Lane B, 41 records)

<!-- Part B header as written by Lane B: -->
# DAFoam prior-work inventory — PART B (Ladder B, F6, supervision, cross-references)

**Lane B of the DAFoam team, Phase 0, 2026-08-21. Reading and inventory only: no solver
ran, no container was started, nothing was sent, filed, uploaded or registered, and no
existing record was edited.** Lane A owns
`docs/dafoam/PRIOR_WORK_INVENTORY.md` and `docs/dafoam/TOOLCHAIN_INVENTORY.md`
(Ladder A and the toolchain); this file is its sibling and does not duplicate them.

Companion: `cases/dafoam/INDEX.md` (this lane's other deliverable) maps the lab's
`PREREGISTRATION.md` + `RESULTS.md` convention onto the 6.7 GB tree as it actually is.

**Path convention throughout.** Most records were written when this tree lived at
`demo-output/website/dafoam/` and still cite that prefix in their "Evidence files"
sections. Read it as `cases/dafoam/`. Run trees under `/home/ubuntu/certonomous-runs/`
are outside this repository.

---

## 1. Ladder B — every rung and every S1/W4 CBFS sub-record

### 1.0 The B3 settlement, first, because it is the question most likely to be got wrong

**Is B3 still BLOCKED?** **Yes — and no. Both halves are true and the record is explicit
about which is which.** The distinction is grading policy R11, not hedging.

| grading frame | verdict | authority |
|---|---|---|
| **Against the SHIPPED toolchain** (DAFoam 5.0.0 + IDWarp 2.6.2 as installed; `DALinearEqn.C` still hard-codes `PCType localPCType = PCILU`) | **BLOCKED — stands today** | `DAFOAM_CASE_STATUS.md:134` (last sentence): *"The shipped image is unmodified: BLOCKED as graded against the shipped toolchain stands; nothing filed upstream."* Also `:285-287`. |
| **Against the locally rebuilt image** `dafoam-subpclu:v1` with `DAFOAM_SUBPC_TYPE=lu` | **UNBLOCKED, converged, FD-verified** | `ladder-b/W4_ADJOINT_PC_UNBLOCK.md:16-19` |

Quoted verdicts and numbers, as recorded:

- **The original block.** `ladder-b/B3_duct_field_inversion.md:24-34`: *"**Stage 3 (timed
  adjoint pilot): BLOCKED, not silently routed around.** The discrete-adjoint GMRES solve
  diverges with PETSc `KSPConvergedReason = -9` (`DIVERGED_NANORINF`) at iteration 0,
  reproduced identically across two primal convergence levels (1e-4, 1e-6), two
  objective-function types … and two ILU preconditioner fill levels (1, 4)."* Initial
  residual **7.09e-04**, **0 iterations completed** (`:232-237`). Mesh ruled out:
  `DACheckMesh` max aspect ratio **14.76**, max non-orthogonality **33.3°**, max skewness
  **0.26** (`:251-253`).
- **Primal, for the record:** converged at **1223 iterations** to `primalMinResTol=1e-6`,
  agreeing with B2's plain-OpenFOAM baseline to **0.0865% (U), 0.233% (p), 1.414% (k),
  1.198% (omega), 0.460% (nut)** scaled MAE (`ladder-b/B3_duct_field_inversion.md:158`).
  Cost 234.97 s serial, 0.192 s/iter (`:175`).
- **The unblock.** `ladder-b/W4_ADJOINT_PC_UNBLOCK.md:16-19`: *"**The CBFS adjoint
  converges — `PetscConvergedReason: 2`, 667 iterations — on B3's exact `-9`
  configuration, changed only by switching the ASM sub-block preconditioner from
  incomplete LU to complete LU.** First converged adjoint linear solve on any
  closure-relevant blocked case in this lab."* Printed at `:151-157`:
  `Main iteration 0 KSP Residual norm 7.091590452305e-04` → `Main iteration 667 … 6.922418564747e-10`
  → `**Completed**! Total iterations: 667. PetscConvergedReason: 2. 232.2 s`. 243 s wall,
  4 ranks, **16.2 core-min**.
- **The gate.** `W4_ADJOINT_PC_UNBLOCK.md:332-334`: *"The docket gate — 'the hump or CBFS
  adjoint converges and the resulting gradient is FD-verified on at least 3 components to
  the same order as S1's 2.67%' — is met, on the CBFS branch, with all evidence on disk."*
  FD table at `:317-322`: cells 5491 / 6740 / 12486 at h=0.05 →
  **0.085% / 0.059% / 0.199%**, zero sign flips.
- **Independent reproduction.** `VERIFICATION_cbfs_unblock_supervisor_sweep.md:96-111`: a
  cell the lab never published, **6490**, re-derived by the sweep's own driver in an
  isolated case copy → **0.0211%** relative error, *"tighter than any of the three
  published cells."* The env-off regression was also re-run cold by the sweep and
  reproduced `-9` at iteration 0 with **all 13 residual digits** matching (`:113-118`).
  Five attacks, five **CONFIRMED**, *"No defect found"* (`:21-30`).
- **Which image did it.** `dafoam-subpclu:v1` — the **sub-PC** patch. `dafoam-kspopts:v1`
  is **NOT** the unblocking image; `kspopts_patch/DALinearEqn_kspopts.patch` belongs to
  the separate **diagnosability** defect candidate (`DEFECT_CANDIDATE_ksp_options_override.md`,
  FILING-READY / NOT FILED), which documents that `KSPSetFromOptions` is called at
  `DALinearEqn.C:138` and then overridden at 13 later call sites, so `-sub_pc_type lu`
  from the command line is silently discarded.
- **What the unblock did NOT do.** It did not unblock B3 *Stage 4*: the CBFS field
  inversion under the shipped toolchain. The inversion that eventually ran
  (`S1_CBFS_INVERSION_RESULT.md`) ran on the patched image, is a **production-term**
  inversion, and its first attempt failed both gates.

**Root-cause chain, as recorded, in order:**

1. `B3_duct_field_inversion.md` (2026-07-28) — `-9` reproduced 4 ways, *"root cause is
   not resolved within this rung's time budget"* (`:257-258`).
2. `B3_supervisor_debug.md` (supervisor takeover) — rung 1 `primalVarBounds` k-floor
   (kMin 1e-10 vs wall BC 1e-15): **REFUTED**, identical `-9`, 0 iterations, 177.61 s
   (`:46-48`). Rung 2 `empty` instead of `symmetry`: **REFUTED** — DAFoam rejects meshes
   with <3 geometric directions (`DACheckGeometry.C:278`), so the conversion is
   *mandatory*, not a workaround (`:107-116`). Rung 3.5, zero compute: **886,833 numeric
   tokens** across 13 files scanned, **zero non-finite hits** — the primal state is clean
   cell-by-cell, so the NaN is generated during adjoint assembly (`:176-188`).
   *"B3 remains blocked."* (`:232`).
3. `S1_FIML_FIELD_INVERSION.md` (2026-07-31) — the `-9` is **not** a property of the SST
   adjoint: a kOmegaSST field-inversion adjoint with 5,000 per-cell beta DVs converges
   (**91 iterations, reason 2**) on the official tutorial case. On the hump, two levers
   change the signature without converging: `normalizeResiduals: ["None"]` → `-3`, 2000
   iterations, residual **exactly flat at 1.094138002900e+00 to 13 digits**;
   `jacMatReOrdering: natural` → `-3`, 1000 iterations, flat at 1.094138002841e+00.
4. `PROOF.md` §25.2 — the whole 5-way ordering axis on CBFS: `rcm` **-9** (0 iters,
   87.96 s), `1wd` **-9** (0, 90.53 s), `natural` **-3** (1000, 237.9 s), `nd` **-3**
   (1000, 353.5 s), `qmd` **-3** (1000, 245.43 s). *"Two of five produce the NaN, three
   produce honest stagnation, and none converges."* Initial residual identical
   (7.091590452305e-04) in all five.
5. `PROOF.md` §25.3 (`PROOF.md:2710-2803`) — **the mechanism, reproduced with no DAFoam in
   the loop.** `dRdWTPC` is 210,592², **13,710,468** nonzeros, `‖b‖₂ = 7.091590452305e-04`
   matching the printed iteration-0 residual to all 13 digits. **Zero zero-rows, zero
   zero-columns, zero zero-diagonal entries**; diagonal spread **log10 8.67** against the
   M6 family's 14.17 — *"CBFS is roughly five and a half decades better conditioned by the
   metric R5 used, and still fails. R5's diagonal-spread mechanism does not explain CBFS."*
   `scipy.sparse.linalg.spilu` → **`RuntimeError: Factor is exactly singular`** at every
   drop tolerance swept (1e-2/fill 3, 1e-3/fill 5, 1e-4/fill 5, 1e-5/fill 10);
   `scipy.sparse.linalg.splu` (full LU **with partial pivoting**) solves at every pivot
   threshold (`diag_pivot_thresh` 0 / 0.1 / 1 → residual 2.3769e-10 / 6.4063e-12 /
   **2.535461e-12**). Unpreconditioned scipy GMRES reproduces the stagnation
   (1.0 → 9.999687e-01 over 1000 matvecs), which **exonerates DAFoam's KSP/PC
   configuration**. *"fill adds fill, not pivoting"* — which is why `pcFillLevel: 4` also
   returned `-9`. Price of the repair, stated: complete factors carry **24–28× the
   matrix's own nonzeros, roughly 3 GB, on a 21,000-cell case**.
6. `W4_ADJOINT_PC_UNBLOCK.md` §1–§4 — the offline petsc4py harness reproduces DAFoam's
   failure bit-for-bit (`RESULT reason -9 its 0 finalres 7.091590452305e-04 wall 7.01s`,
   `:76-78`); §2 shows the runtime escape hatch is **reachable but empty**
   (`-sub_pc_factor_zeropivot 1e-8` visibly lands in `PCView` and still returns `-9`);
   §3 shows `PCSetType(subpc, PCLU)` converges offline in **347** iterations under `rcm`
   while `nd` *"did not finish — killed at 600 s"*; §4 is the one-hunk env-gated rebuild
   at `DALinearEqn.C:266–267`, with a regression control (env unset → `-9` at iteration 0,
   92 s, rc=1).

**Standing caveat the record itself carries:** the dumped matrix is the **assembled
preconditioner** `dRdWTPC`, not the matrix-free transpose Jacobian `dRdWTMF` that GMRES
applies. The singular-ILU finding is direct; the GMRES-stagnation controls are
corroborative (`PROOF.md` §25.3 closing paragraph; repeated in `W4` §5a and in the
2026-08-11 hump correction).

### 1.1 Ladder B rung table

| rung | what ran (np / solver / image / iterations) | verdict AS RECORDED | key numbers | root cause(s) | patched, and where | never filed | still open | source |
|---|---|---|---|---|---|---|---|---|
| **B1** | **nothing** — *"Research and planning only — no solver runs, no compute launched in this rung"* | no verdict; a ranked plan | Leaderboard read from the local benchmark clone: rank 1 Reissmann & Fang **0.0595**, **rank 2 Wu and Zhang 0.0624** (the DAFoam field-inversion entry), rank 3 Liu et al. 0.0737, rank 4 Montoya et al. 0.0779; our own entry **0.0741** against a RANS-identity floor **0.1036**. Cost estimate for a field inversion: **[ESTIMATE]** 140–420 core-min from the paper's ~140 SLSQP iterations | n/a | n/a | its own gap: *"our square duct family … has no confirmed FIML-lineage reproduction target in this rung"* (`:358-362`) | Picks 2 and 3 (Volpiani 2021 PRF 6 064607; Volpiani 2026 DOI 10.1103/dk9r-td14) were **never read in full** — publisher 403s — so no cost was estimated for either | `ladder-b/B1_reproduction_plans.md` |
| **B2** | np=1, **plain OpenFOAM `simpleFoam`, not DAFoam**, OpenFOAM v2606; AR_1 456 iters, AR_3 1,700 iters, CBFS 30,000 (fixed endTime by the case's own design) | **PASS / reproduced**, 2 disclosed deviations | AR_1_Ret_360 (3,025 cells) our score **0.1290** vs floor **0.1288** (+0.16%), field MAE **0.023%**; AR_3_Ret_360 (8,748 cells) **0.1251** vs **0.1243** (+0.64%), MAE **0.09%**; CBFS (21,000 cells) MAE **0.068%**. Total cost **~30.9 core-min** | fork gap OpenFOAM-7 (`7-3bcbaf946ae9`) vs v2606 → 10–13% iteration-count difference, 0.02–0.09% field difference | nothing patched; `libfrozenIncompressibleTurbulenceModels.so` dropped (source not distributed anywhere in the public clone), `#includeFunc residuals` dropped (v2606 renamed it `solverInfo`) | — | the missing library was **never verified against its own source** — *"Flagged, not asserted"* (`:86`) | `ladder-b/B2_duct_baseline.md`, `.json` |
| **B3** | np=1 (primal) and np=4 (adjoint), `DASimpleFoam`, `dafoam/opt-packages:latest` (DAFoam 5.0.0, OpenFOAM v2506, PETSc 3.15.5); primal **1223** iters; adjoint **0** iters | Stage 1 **DONE, verified**; Stage 2 **DONE**; **Stage 3 BLOCKED**; **Stage 4 DID NOT RUN** | see §1.0 | singular ASM sub-block ILU (exact zero pivot), located `PROOF.md` §25.3 | **repaired in a local rebuild only** — `subpclu_patch/DALinearEqn_subpclu.patch`, image `dafoam-subpclu:v1`; shipped image untouched | nothing filed upstream, ever (`FAMILY_SUPERVISION_GUIDELINES.md` §3.6) | Stage 4 under the **shipped** toolchain; hump adjoint uncharacterised; the `-9` on any new case | `ladder-b/B3_duct_field_inversion.md`, `B3_supervisor_debug.md`, `.json` |
| **B3 debug rungs 3–7** | not run | *"not yet run"* × 5 | rungs 3 (SA rebuilt from tutorial), 4 (frozen-turbulence adjoint), 5 (PC family swap), 6 (row scaling), 7 (objective regularisation) | — | — | — | rung 3 was **answered elsewhere** (S1 tutorial case converges under SST); rung 4 is **structurally unavailable to field inversion** — beta lives inside the turbulence model, so freezing those residuals deletes the sensitivity being solved for (`S1_FIML_FIELD_INVERSION.md` §4) | `ladder-b/B3_supervisor_debug.md:139-145` |

### 1.2 The S1 CBFS sub-records (all on the patched image, all production-term-labelled)

Every S1 CBFS run below uses `dafoam-subpclu:v1`, `DAFOAM_SUBPC_TYPE=lu`, **4 MPI ranks**,
`--cpus=2` under the concurrency instruction, cold `rm -rf processor*` reset, cold start
from `0/`, one fresh container per evaluation, host-side SciPy L-BFGS-B (maxcor 10,
maxls 8, ftol 1e-10, gtol 1e-6, bounds [0.2, 4.0]), beta = `betaFIOmega`, **21,000 DVs**.

| item | what ran | verdict AS RECORDED | numbers | source |
|---|---|---|---|---|
| **S1-fiml** (Stage 1 capability) | tutorial case 5,000 cells / 5,000 beta DVs, `DASimpleFoam`, 4 ranks, stock `dafoam/opt-packages:latest`; plus the NASA hump 51,626 cells / 51,626 DVs | capability **PASS on the resolvable set**; hump target **BLOCKED** | E1 kOmega **80 iters, reason 2**; E2 kOmegaSST **91 iters, reason 2**; E2-tight 91, reason 2. FD on the **real objective seed**: **2.674%** at h=1e-3 and **2.683%** at h=1e-4 — *"step-independent, convergence-independent, and unexplained"*. Primal tightened 1000× (1e-8→1e-11): disagreement moved 2.6739% → 2.6728%. Hump: coloring **68.62 s**, peak ~11 GB, MemAvailable never below **18.99 GB**, adjoint `-9` at iteration 0 | `ladder-b/S1_FIML_FIELD_INVERSION.md` |
| — *the retraction inside it* | zero compute | **B3's central disclosure RETRACTED** | *"No custom turbulence library is needed."* DAFoam v5's own `DAkOmegaSST` ships `betaFIOmega_`/`betaFIK_` as `READ_IF_PRESENT` fields defaulting to 1.0. **But** `betaFIOmega_` multiplies the omega **PRODUCTION** term (`DAkOmegaSST.C:743`), not the destruction term Wu/Zhang invert — *"The two are not equivalent"* | ibid. headline items 2–3 |
| — *the clip audit* | 12 FD points re-run at `printInterval 1` | verdict **re-affirmed on a narrower claim** | archive logged **3** clip events for those 12 runs; the truth is **689** — a **230× undercount**; **11 of 12 clip, the unperturbed baseline included**; all 12 objectives return **bit-identical to 16 significant figures**; all 689 events fall in iterations **27–142** of runs 1815–3291 iterations long | ibid. §3 |
| **W4 adjoint-PC unblock** | offline petsc4py ladder + CBFS + hump, 4 ranks | **gate MET on the CBFS branch** | 185.0 core-min against a 240 budget; CBFS reason 2 / 667 iters twice (patchV and beta); FD 0.085/0.059/0.199%; hump residual 1.094138002900e+00 → 9.544468674795e-01 over 900 iterations, then `docker stop` at MemAvailable **1.62 GB** | `ladder-b/W4_ADJOINT_PC_UNBLOCK.md` |
| — *the 2026-08-11 hump correction* | zero compute, log forensics | headline 3 **WITHDRAWN as a causal claim** | `hump_sublu_computetotals.log` is 2,279 lines and contains the string `ConvergedReason` **zero times**. *"The NASA-hump adjoint boundary is uncharacterised."* Missing measurements M1–M6 priced at **365 core-min**, of which **40 (M1+M2) are decisive-cheapest**; M4 *"needs ≥64 GB, or it does not produce the measurement it is bought for"*. Conditional M7–M8: 120 core-min | ibid. §5b, §5b.1 |
| — *the 2026-08-07 inlet correction* | zero compute | W4 §5c sentence **wrong** | *"the case's real nonuniform inlet is thereby restored rather than overridden"* — the on-disk `0/U` had already been overwritten by the patchV pilot to **Ux = 0.72 uniform on all 150 inlet faces**. Gate unaffected; loss carries a **27% inlet bulk mismatch** | ibid. §5c correction block |
| **S1 CBFS inversion** (`s1-cbfs-field-inversion-run`) | 17 evaluations, out-of-process driver | **BOTH GATES FAIL**, no softening | **G1 FAIL**: J_qoi fell to **0.99851** against ≤0.70 — a **0.149%** reduction. **G2 FAIL**: **29.0%** of top-decile \|beta−1\| cells in the window against >50%. Gradient norm down **106×** (9.528e-4 → 9.011e-6); **zero** cells pinned at either bound; eval-1 control reproduced W4's objective to all 17 digits and the archived gradient **bit-identically (max abs diff exactly 0)**. Cost **335.98 / 600 core-min** | `ladder-b/S1_CBFS_INVERSION_RESULT.md` |
| — *the diagnosis* | host-side, zero solver compute | primary cause **an objective defect** | RANS inlet bulk Ux **0.7194** vs LES **0.9153**, ratio **1.272**; Uz noise columns **byte-identical** — the overwrite fingerprint. **85.1%** of the loss at y>2; the physics window holds **3.7%**. Secondary: penalty balance, \|g_pen\|/\|g_QoI\| = **0.998**, cos = **0.9995**, rms\|beta−1\| pinned at **0.0165**. Contributing: the SST shear-stress limiter binds on **7.7%** of all cells but **49.5%** of top-decile cells (**6.4× enrichment**) | ibid. §4 |
| — *a second defect found en route* | calibration run, 31.07 core-min | **structural** | DAFoam's primal restarted **in-process** from its own converged state walks away from it: p residual 1e-6 → **0.2148** at the endTime-2500 cap, omega/k pinned at their 1e-16 floors, varianceU **+10.9%**; prints *"Primal solution failed!"* and **proceeds into the adjoint anyway**, which stagnates flat (**reason −3**, 4.6413e-02 → 4.6118e-02 over 1000 iterations, 0.64%). *"In-process multi-evaluation optimization is structurally unavailable on this case"* | ibid. Amendment 1 |
| **S1 CBFS re-inversion** (`s1-cbfs-objective-repair-and-reinversion`) | 16 evaluations at `-primalTol 1e-8` | **G1 PASS, G2 FAIL** | **P1 PASS beyond prediction**: baseline varianceU **1.5279278906359758e-02 → 6.1509017109920479e-04**, a **24.8× collapse** against a predicted "< 7.6e-3". Inlet bulk ratio **1.272 → 1.0005**. **P2 PASS**: y>2 loss share **85.1% → 25.6%**; window share **3.7% → 41.2%**. **G1 PASS**: J_qoi **0.25846573**, a **74.2%** reduction. **G2 FAIL**: **26.9%** vs >50%. Window error **−94.9%**, near-wall **−95.9%**, y>2 only **−21.6%**. **224 cells pinned** (223 low, 1 high). Cost **424.80 / 450 core-min**, stopped by the driver's own budget guard — *"recorded budget-capped, not converged"* | `ladder-b/S1_CBFS_REINVERSION_RESULT.md` |
| — *a protocol defect found and fixed by amendment* | 23.97 core-min of diagnosis | **FD bar missed at 1e-6, met at 1e-8** | At `primalMinResTol 1e-6` the cold primal stops at the first crossing (iters **383–458**) and central FD misses the adjoint by a systematic **fd/adj ≈ 0.7** on all three cells (**25.9% / 32.0% / 32.2%**). One pair at **1e-8**: **25.9% → 0.032%**. Re-verified: **0.032% / 0.115% / 0.009%**, zero sign flips, anchor ‖g‖ = 1.2218e-4 (**8.4×** the corrupted objective's) | `ladder-b/S1_CBFS_REINVERSION_PREREGISTRATION.md` Amendment 1 §B–§C |
| — *the DV→serial permutation correction* | zero compute | FD **neighbourhood labels retracted**, numbers stand | The DV vector is **not** in serial cell order. The exact permutation (from concatenated `processor*/constant/polyMesh/cellProcAddressing`, verified to **5.1e-15**) places DV 5363/5428/5491 at serial cells **187/330/471** — all three in the separated shear layer just downstream of the crest, **not** "step crest / downstream recovery / upstream channel". FD measurements are index-consistent and unaffected | `ladder-b/S1_CBFS_WEIGHTED_LOSS_VARIANT.md` §0b; addendum on `S1_CBFS_REINVERSION_RESULT.md` |
| **S1 weighted-loss offline variant** | **zero solver core-min** | **CAPTURABLE**, per the pre-registered rule | W1 window-only R = **0.9494**; W2 window ∪ near-wall R = **0.9468** (both ≥0.70 bar); W3 region-equalized 0.6348 (sensitivity, never decides); W4 Wu/Zhang sparse proxy **0.9340**. Hurt census: window **1.74%**, W2 support **1.02%**, near-wall outside window **exactly 0.00%** — both caps hold with 5–10× margin. **Relocation census, loud:** y>2 hurt **1.1531** over 4,288 cells against 3.2939 gross reduction there = **35.0%** | `ladder-b/S1_CBFS_WEIGHTED_LOSS_VARIANT.md` |
| **S1 weighted reinversion arm** | 7 evaluations + a 2-evaluation approved completion | gates **A PASS, B PASS, G1w FAIL, G2 FAIL** | **A** masked-beta control: R_W1(masked) **0.9458** vs full-beta 0.9494 — *"the window fix retains 99.6% of its reduction with every out-of-window deviation amputated"*. **B** FD gate: refpoint prints **5319 and 3591 exactly**, `Jw_raw = 27.465931825190644` vs the fixed 27.4659 cross-check, **one** adjoint (676 iters, reason 2), FD **0.033% / 0.007% / 0.029%**. **G1w FAIL** at **0.05713** (then **0.05710** after the approved eval-8) against ≤0.05320. **G2 FAIL** at **42.7%** against >50% — but top-decile membership is **79.7% inside the W2 support** and **0.0% at y>2** (was 31.5%). Cost **229.07 / 250**, then **267.07 / 278 amended** | `ladder-b/S1_CBFS_WEIGHTED_ARM_{PREREGISTRATION,RESULT}.md` |
| — *the honest reading of the completion* | 2 evaluations | **budget-limited hypothesis UNRESOLVABLE** | *"the restart's first step is steepest descent under cold curvature … and it bought 150× less than the live optimizer's recent steps … G1w failed at every state actually reachable within the approved budgets, and the budget-limited hypothesis for G1w is UNRESOLVABLE as posed, not vindicated."* The pre-registered prediction (window share > 50%) was **graded WRONG** | `S1_CBFS_WEIGHTED_ARM_RESULT.md` addendum |
| **S1 sensitivity-vs-error (R1)** | **zero solver compute** | headline statistic **INCONCLUSIVE**; the null-free leg **CONFIRMS reading 2** | The pre-declared abort fires: agreement between \|β_final−1\| and the pure-gradient-step null is **+0.9742** against a 0.9 abort threshold and a null pinned at **+1.0000 by arithmetic**. The null-free measurement: **G2 scored on the baseline gradient alone — an array with no inversion result in it — returns 35.38%, with 45.8% upstream**, reproduced by a second independent baseline gradient (**31.19%**, ρ = +0.945) and surviving cell-size normalisation (33.00% / 45.4%). **G2 as defined scores the adjoint's sensitivity map, not the closure's error location.** Third result: the top decile of the **per-cell baseline loss** is only **32.71%** in-window, so **no loss-following correction can clear the >50% bar**; the achieved 26.86% is **82% of that ceiling**. Kills **R5** (340 core-min) and **R8** at zero compute | `ladder-b/S1_SENSITIVITY_VS_ERROR.md` |
| **S1-priors** (`s1-regularization-…-posterior-on-beta`) | **NOT RUN — no run directory exists** | **proposed, unrun, blocked until post-send** | Cap **260 core-min**. Prior derived: lognormal, `log β ~ N(0, 0.75²)`, `λ_LN = 8.1335e-06` (band 2.0334e-06–8.1335e-06). Finding: the two equal-weight runs used **priors 16× apart in σ_β** (0.043 vs 0.676) while describing it as a "10× cut"; the repaired run's Gaussian prior puts **6.96% of its mass on β < 0**, physically impossible. Gates: G-P1, G-P2 (<60 pinned cells), G-P3, **G-P4 withdrawn 2026-08-14** and replaced by G-P4a + G-P4b | `ladder-b/S1_PRIORS_PREREGISTRATION.md` |
| — *the duplicate* | zero compute | **NOT CANONICAL, superseded 2026-08-11 by chief ruling** | Two chief sessions dispatched the same item off the same directive block and neither claimed it first. Retained for two things: the **independent** re-verification of the inlet premise (identical digits from a second agent) and the plateau-balance reconciliation addendum. Its 560 core-min plan and its gates are **withdrawn as a competing plan** | `ladder-b/S1_WITH_PRIORS_PREREGISTRATION.md:3-24` |

**What was never filed, across the whole of Ladder B:** nothing. `FAMILY_SUPERVISION_GUIDELINES.md`
§3.6 — *"Nothing is filed upstream by anyone in this family, ever. Both reports and the
tex carry NOT FILED status; filing is Katie's call alone."* Confirmed at the source:
`UPSTREAM_BUG_REPORT_decomposition_adjoint.md:3-4` and
`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md:3-4` both open with **"Status: NOT FILED ANYWHERE."**

**What remains open in Ladder B, in the records' own words:**

1. B3 Stage 4 under the shipped toolchain — the field inversion the ladder was for.
2. The NASA-hump adjoint boundary — *"uncharacterised"*, M1–M6 priced but unbought.
3. `w3-beta-on-omega-destruction-model-patch` — the term-parity item; *"the **only** route
   to an external referent for the S1 line"* (`S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md` §1b).
4. The residual **2.7%** FD gap on the tutorial field inversion — real, step-independent,
   convergence-independent, unexplained.
5. Stage 2 (learning β(features)) — held: *"ruling 3 conditions training on gates PASSING;
   they did not."*
6. The duct streamwise-profile deficit — *"≥76% of the duct error; the largest open closure
   item"*, unpriced.
7. `AR_14_Ret_180`, the third scored duct case, **never reproduced** (`f6c_duct_dns/F6c_duct_vs_dns.md:99-104`).

---

## 2. F6 series and `rans_model_comparison`

**Family attribution, stated first because it is easy to get wrong: none of these belong
to the DAFoam team.** They are family **F6** of the Certonomous hard-case campaign, every
one a plain OpenFOAM `simpleFoam` solve with **no DAFoam adjoint anywhere**. They sit
under `cases/dafoam/` for historical reasons only, and their analysis records live in a
**third** tree, `verification/campaign/` (see `cases/dafoam/INDEX.md` §3 for the file
list). The DAFoam link is one-directional: F6a's case is what S1's hump attempt was warm-
started from (`S1_FIML_FIELD_INVERSION.md` §4), and F6c is post-processing of B2's fields.

| case | what it is | family | verdict AS RECORDED | numbers | citation |
|---|---|---|---|---|---|
| **F6a NASA hump** | 51,626-cell 2D wall-mounted hump, `kOmegaSST`, np=4, 1,772 iterations | F6 (campaign) | **"GATE REACHED, PASS/FAIL AS MEASURED"** | Separation x/c **0.6544** vs experiment 0.665 (**−1.6%**) and vs NASA's own SST 0.654 (**+0.06%**). Reattachment **1.2534** vs experiment 1.100 (**+13.9%**), inside NASA's own quoted 1.25–1.27. Score 0.0622 vs floor 0.0621 (+0.16%); field MAE **0.02%**. Cost **~5.25 core-min** | `f6a_nasa_hump/F6a_nasa_hump.md:163-173` |
| **F6a epistemic band (D9)** | RANS inter-model sweep (channel 1) + eigenvalue perturbation (channel 3) + literature (channel 2), 1.3 GB of arms | F6 | band **CONTAINS** the miss — but **channel 3 is WITHDRAWN** | Published band **[1.0717, 1.2534]** is a **channel-1** result: lower edge kOmega, upper edge the kOmegaSST baseline, **no eigenvalue perturbation in it**. *"Every channel-3 run in this study applied the eigenvalue perturbation with the opposite sign to the one intended"* — imposed state was `b_eff = 2·b_Bouss − b_pert`. Entries oneC **0.5278**, twoC **0.6701**, threeC **1.1069** are **withdrawn as corner states**. The **pre-registered prediction leaned on channel 3** and is therefore partly unsupported | `verification/campaign/F6a_epistemic_band.md:1-23`; prediction at `cases/dafoam/f6a_epistemic_band/PREDICTION.md:48-58` |
| **F6b periodic hills** | 15,600-cell `PH_Breuer`, `kOmegaSST`, np=4, 10,000 iterations, 511 s = **34.1 core-min** | F6 | **"GATE REACHED"** — and the **pre-registered prediction is FALSIFIED**, left unedited | Reattachment **x/h = 7.6439** vs Fröhlich et al. (2005) LES **4.6–4.7** → **+63% to +66%** (midpoint 64.4%). Separation **0.2590** vs ~0.2. Profile scaled MAE **12.51%** (shipped/serial pipeline) / **12.95%** (our 4-rank run). Reproduces the benchmark's shipped RANS to **five significant figures** (7.6438953 vs 7.6439146) | `f6b_periodic_hills/F6b_periodic_hills.md:13-29, 147-156`; prediction `PREDICTION_before_run.md:33-45` |
| — *two corrections inside it* | zero compute | both applied in place | (1) `Re_H = Ubar·h/nu = 0.72/9.438e-05 = 7628, not 10595` — the case IS at the canonical Re_H because the literature's Re_H uses the **crest bulk velocity, 0.9982**, giving **10,576** (within 0.2%). (2) `gate_result.json`'s `profile_scaled_mae … overall_percent` is literally **`null`** — the station loop looked for `line_U.xy` while the run wrote `line_k_nut_omega_p_U.xy`, *"so it found nothing and returned an empty dict without erroring"* | ibid. `:42-50`, `:157-164` |
| — *the gate-checker false negative* | zero compute | **diagnosed, not overridden** | `check_convergence.py` returns `NOT_CONVERGED` because `system/fvSolution:82` sets `residualControl { p 1e-15; }`, unreachable on this mesh, so simpleFoam never prints its convergence sentence. *"This is a **sibling of L-21, not L-21 itself**"* — L-21 names a residualControl entry on a field the model does not transport; here `p` **is** transported and the tolerance is simply unreachable | ibid. `:108-121` |
| **F6c duct vs DNS** | **zero new CFD** — post-processing of B2's converged fields | F6 | **"GATE MEASURED, FAIL AS EXPECTED AND DOCUMENTED — not shipped as a pass"** | RANS secondary-flow RMS **2.01e-16 m/s (6.1e-16% of U_bulk)** on AR_1 and **9.12e-16 m/s (2.4e-15%)** on AR_3 — machine precision, i.e. genuinely zero — against DNS **0.734 m/s (2.22%)** and **0.796 m/s (2.07%)**. RANS captures **~0%** of the DNS secondary flow | `f6c_duct_dns/F6c_duct_vs_dns.md:70-79` |
| **F6d random-matrix UQ** | 80 + 15 ensemble members, 4.7 GB | F6 | **negative answer, recorded as one**; the Option-A continuation is **VOID** | The random-matrix band **contains** the LES truth but is **5.0× wider** than the eigenspace corner union at δ = 0.2 and **7.1× wider** at δ = 0.6 — *"It is not tighter at either of the paper's own settings."* At δ = 0.6, gating to the 5 of 40 members meeting the residual gate **loses containment entirely** while the unfiltered ensemble keeps it. **Option A is VOID**: control `d0.2_s000` moved **−0.491 x/h** against a 0.25 threshold, *"Ruled on the literal reading … a gate that can be dissolved by post-hoc argument is not a gate."* It also **found the F6a channel-3 sign error**, demonstrated four independent ways | `verification/campaign/F6d_random_matrix_uq.md:651-673`; `F6D_OPTION_A_RESULT.md:1-25` |
| — *the contaminated snapshot* | forensics only | **labelled, not deleted** | `f6d_option_a/d0.2_s000/7500/` was written by a **second `simpleFoam` process** launched by mistake at 02:54:51 on 2026-08-11, which died at Time 7859. 23 of 24 continuation snapshots are the survivor's; exactly one is not. Four independent lines of evidence (stored gradient 0.00759741462064012 vs the survivor's 0.0084247934089418; directory mtime 02:55:05.02 older than every file inside it at 02:55:27.88; a second `postProcessing/wallShearStress/7000/` series with exactly one write event; wall-shear extrema mismatch). **The run's own 7500 is gone and cannot be reconstructed.** No pre-registered metric moves | `f6d_random_matrix_uq/f6d_option_a/d0.2_s000/PROVENANCE_7500_CONTAMINATED.md` |
| **`rans_model_comparison`** | 5 turbulence models on `AR_1_Ret_360` (3,025 cells), plain `simpleFoam` | F6c follow-on | **no `.md` record in-tree** — only `sweep_results.json` | All four **linear** models produce secondary flow at machine precision: SA **6.64e-16%** of U_bulk (354 iters, 3.13 s), kEpsilon **5.54e-16%** (597, 6.29 s), kOmega **7.90e-16%** (274, 2.98 s), realizableKE **9.21e-16%** (2921, 38.6 s) — **~0% of DNS captured** in every case. The one **nonlinear** model, **LienCubicKE**, produces real secondary flow: **0.174% of U_bulk** (4780 iters, 53.13 s) = **7.85% of the DNS magnitude**. That single number is the cleanest in-lab demonstration that the deficit F6c measures is the **Boussinesq hypothesis itself**, not a numerics artefact — and it is currently recorded **only in a JSON file with no narrative record anywhere** | `rans_model_comparison/sweep_results.json`, `collect_results.py` |

---

## 3. Supervision, family and research records — the rulings and standing guidance

### 3.1 `FAMILY_SUPERVISION_GUIDELINES.md` (issued 2026-08-07; binding on every agent in this family)

Scope: *"everything in `demo-output/website/dafoam/` (ladders A and B, the defect
campaigns, the two unfiled upstream reports, the LaTeX companion), the run trees under
`/home/ubuntu/certonomous-runs/W4-*`/`W5-*`, and any future work touching DAFoam, IDWarp,
pyGeo/DVGeo, or the MACH-Aero adjoint stack"* (§scope). Standing rules, cited:

- **§1 — six one-word regression reproducers before any toolchain bump.** R-1 IDWarp
  rotation guard (stock: idx8 **207.0%** SIGN-FLIPPED, idx17 **121.6%** SIGN-FLIPPED;
  patched 3.0e-06 / 7.0e-06); R-2 A4 decomposition (scotch **8.95%**, simple 4x1x1
  **0.00054%**, np=1 stock **1.10%** — the graded configuration); R-3 limiter branch
  parallel (**8.95%**, KSP 719 → **0.849%**, KSP 41); R-4 limiter branch **serial** (A1
  CD/shape **92.8%**, one component sign-flipped → **0.121%**); **R-5 the ILU
  conditioning wall on B3/CBFS** (`DAFOAM_SUBPC_TYPE=lu` on `dafoam-subpclu:v1`; env off
  = `-9` at iter 0, initial residual 7.091590452305e-04 to 13 digits; on = reason 2, 667
  iterations; ~6 core-min off / ~16 on); R-6 `mdolab/idwarp#57` self-test. **Minimum bump
  protocol: R-1, R-2 (np=1 + scotch), R-3, R-5-off, R-6.** *"A run without its stamp does
  not count."*
- **§2 — cross-residual instrument discipline (L-35).** The system is `A^T psi = -b`; an
  instrument computing `Atpsi - b` prints the degenerate `ratio=2.000000e+00` on its own
  control. `w4x_res_*.npy` hold `Atpsi - b` (need `+2b`); `w4x2_res_*.npy` hold the true
  residual — *"Do not mix them."* Map validation is a **gate**, not a printout (floors
  2.7e-15 .. 3.6e-15; integer addressing maps only, never coordinate matching). Bands in
  **floor units**, never absolute — *"The R5 band was mis-calibrated by ~5 orders and
  survived on luck."* **A clean gradient is not a clean operator (L-36)** and
  **decomposition-invariance is not correctness (L-38)**: `inletOutlet` hides a
  **1.047×‖b‖** wrong operator under a **0.019%** gradient; `a1lim` is
  decomposition-invariant to **4e-04** while **92.8%** wrong. **Branches first (L-37).**
- **§3 — shipped-vs-patched grading (ruling R11).** Verdicts are graded against the
  **shipped** toolchain. Patched numbers sit **beside** the stock verdict as
  diagnosis-confirmed-by-repair and **never move a grade**. *"A patched grade replaces a
  shipped grade only if the fix ships upstream or Katie formally adopts a forked
  toolchain. Not a session's call, not the chief's; Katie's."* **§3.6: nothing is filed
  upstream by anyone in this family, ever.**
- **§4 — pre-registration before compute.** FD protocol of record: `check_totals`, step
  **1e-3**, central, `step_calc="abs"`, error convention **‖Jan−Jfd‖/‖Jfd‖ as printed**,
  one convention throughout. Step-check required when the FD magnitude differs from the
  analytic np=1-class value by **>20%** or the verdict lands in a gray band. *"An arm
  whose primal fails, or whose adjoint returns no analytic, is NOT SCORED."*
  *"`primalMinResTol` is a pass/fail gate in DAFoam, not a depth control."*
  **Random-seed dot-product tests do not clear a derivative; only the real objective seed
  does** — any warpDeriv-class test uses `--seed real`.
- **§5 — crash triage table**, nine signatures with mechanisms and dispositions. The `-9`
  row is **KNOWN** on B3/CBFS and the hump; *"On a NEW case: dump the PC matrix + RHS
  (stock PETSc flags), reproduce offline before believing anything else."* Two standing
  meta-rules: **a converged solve (`reason 2`) is NOT evidence of a correct operator**
  (A4's 8.95% converged cleanly), and an OOM/stall without a captured error message is
  *"consistent with", never "confirmed"*.
- **§6 — six escalation triggers.** Any scoring-grade verdict move; anything
  upstream-filing-relevant; **any of the case file's headline numbers** (8.95% / 0.00054%
  / 329× / 1.047× / 92.8% / 0.121% / 634% / 207.0%/121.6% / 46.64% / 11.43% / 1.10% /
  **667-iteration unblock** / the FD-gate percentages); a new defect class; budget
  overrun; session-limit exposure.
- **§7 — record hygiene (L-32).** *"Verdict moves update the case's own ladder record
  first, satellites second, always quote-and-strike, never silent rewrite."*
- **§8 — cold-start restoration.** pyDAFoam writes the primal end state back into the
  time-0 directory at run end, so the **second** run of any case dir silently warm-starts;
  `renameSolution` (`pyDAFoam.py:1543`) hard-raises on a leftover `0.0001`. Prove the cold
  start **in the log** via the first `Time step continuity errors` value.
- **§9 — family state 2026-08-10: AT REST, "available by decision, not idle by default".**
  Restart condition: *"a new case, a toolchain bump (run the R-1/R-2/R-3/R-5-off/R-6
  regression set of §1 first), or a decision that actually turns on one of the parked
  items — not on the availability of an agent."* The one declined item (testing whether
  `pcFillLevel 1` also collapses at rung 2) was priced at ~29 core-min and declined
  because *"compute which cannot change a decision is not spent."*

### 3.2 `SUPERVISOR_FAMILY_REVIEW_2026-08-07.md` — the findings pass

Six cross-document discrepancies (DISC-1..6), eight code findings (A-1..A-8, B-1..B-3),
five corrections applied in place (F-1..F-5). Load-bearing for Lane B:

- **DISC-3 / F-3.** `DAFOAM_CASE_STATUS.md`'s "Explicitly blocked" section contradicted
  its own B3 entry — *"Root cause not identified within this rung's time budget"* was a
  **10-day-stale claim with no supersession marker**. Now struck in place with a dated
  note (`DAFOAM_CASE_STATUS.md:108-117`).
- **DISC-5 / F-5.** The B3 entry did not carry the sub-LU unblock beside its verdict — an
  **R11 pattern breach**. Now added at `:134`, including the inlet-contamination
  correction.
- **DISC-4 / F-4.** Cross-rung finding 1 recommended `adjUseColoring=False`, a path
  **measured to crash by construction** (`DAColoring.C:1021`); forced identity coloring is
  **memory-unbounded (>20 GiB on a 2,777-cell case whose colored path uses <2)**.
- **A-1 (SEVERITY HIGH, since FIXED).** The cross-residual instrument computed
  `res = Atpsi - b` for a system that is `A^T psi = -b` at two of three call sites.
  Control reproduction after the fix: old convention **2.000000e+00** (degenerate), new
  convention **1.140697e-04**, *"equal to every digit with the documented offline
  `res + 2b` correction."*
- **A-5 (latent footgun, FIXED).** `run_arm.sh` with an **empty** TAG made `D="$BASE/"`
  and `sudo rm -rf` would have removed the whole discriminators directory. `set -u` catches
  a missing argument but not an empty one.
- **B-1 (MEDIUM, patch text fixed, REBUILD DEFERRED).** `strcmp(subPCTypeEnv, "lu")` is an
  exact match: `LU`, `Lu`, `lu ` (trailing space from a shell export) or `superlu` all
  **silently run stock ILU with no message**. *"A run believed patched can be stock."*
  The deployed `dafoam-subpclu:v1` image is **not rebuilt** with the warn — so **drivers
  must assert the `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` Info line
  in-log before trusting any sub-LU result.** This is a live obligation on any new S1 run.
- **Escalation 3:** *"No scoring-grade claim was found wrong; no headline number moved.
  The discrepancies are currency and bookkeeping."*

### 3.3 `DAFOAM_CASE_STATUS.md` — the family's record of record (83 KB)

- **FD grading standard (`:9-12`):** *"PASS at ≤5% aggregate **and** no flagged component;
  CONDITIONAL 5–15%; FAIL above 15% **or** any sign-flipped/unstable component regardless
  of aggregate. The earlier '1–12% is normal' band (inferred from A1 alone) is retired."*
  Restated at `:85-90` with the flag rule: *"flag any component whose FD value changes
  sign or moves by >50% of its own magnitude across one decade of step."*
- **Grading policy R11** in full at `:14-38`.
- **Cross-rung finding 1 (`:176-220`) — the memory wall, and its own refutation.** Table:
  A1 4,032 works; A5 4,800 works; sail_coarse 63,920 works; sail_medium 156,089 stalls
  mid-coloring; wing_coarse 337,334 stalls mid-adjoint-setup; A3 fine 399,360 OOM; A3
  coarsened 99,840 still OOM. **Then refuted as a general statement:** the NASA hump
  (51,626 cells, 51,626 DVs) completed coloring in **68.62 s** with MemAvailable falling
  only 30.06 → **18.99 GB**. *"The envelope statement should be read as applying to the
  **compressible 6-field** family it was measured on."*
- **Cross-rung finding 2 (`:222-265`) — the A1 shape-derivative disagreement is real**,
  not a step artefact: **idx6 alone accounts for 82.7%** of the squared-error norm and
  never stabilizes; idx0/idx1 carry a stable **9–16%** across three decades. Root cause:
  `mesh.warpDeriv` mis-linearizes opposing-direction combination modes (idx6 **634%** rel
  err under the real seed; idx7 clean at 1.74%).
- **"Explicitly blocked, stated plainly" (`:267-289`)** — five entries: A3's adjoint, B3's
  field inversion (with the 2026-08-07 supersession note), sail_medium, wing_coarse, and
  naca0015_sail_full (*"never run at all — case scaffolding only"*).

### 3.4 `WARMSTART_AUDIT.md` (2026-08-08, zero solver core-min)

Audits the pyDAFoam time-0 overwrite hazard across 9 conclusion classes. **Signature (a)
— "warm primal an order of magnitude faster" — is declared INVALID as priced** before any
verdict; the audit rests on the **first `Time step continuity errors` value** (cold-from-
uniform **0.5969274433533561** to 16 digits, bit-reproducible across six independent cold
starts; **55×** the warm value on the M6 rung).

| row | conclusion audited | verdict |
|---|---|---|
| 1 | B3/CBFS reordering 2×2 + ordering ladder (9 logs) | **COLD-CLEAN** — every arm in its own staged case copy, first continuity error bit-identical (**9.30211816115683e-06**) across all 9 |
| 3 | **W4 sub-LU unblock** (regress / sublu / beta) | **COLD-CLEAN for the warm-start mechanism**; the separate 0/U = 0.72 inlet contamination *"stands as recorded … this audit adds nothing to and subtracts nothing from that disclosure"* |
| 4 | hump sub-LU arm | **COLD-CLEAN** — *"single-run record; no rerun existed to contaminate"*. **Re-labelled 2026-08-11**: read it as *"removes `-9`; no reason code reached"*. And the same fact read the other way is load-bearing: *"'single run; no rerun existed to contaminate' is the same fact as 'never reproduced' — the hump has 11 recorded adjoint attempts and zero deliberate reproductions."* |
| 6 | D3 n15 variant-lever nulls (11 arms) | **WARM-CONTAMINATED (presumptive; formally INDETERMINATE — logs lost, mechanism certain)** → **CLOSED 2026-08-10, RETIRED AS SUPERSEDED** |
| 7 | R5/M6 conditioning matrix dumps | **WARM-CONTAMINATED (state), conclusion-class robust** — 14-decade readings are insensitive to a 2% state drift |

Summary: *"**No standing record-grade conclusion is overturned.**"* Standing
recommendation: the **staged-copy pattern** (one fresh case subdir per arm) is
*"inherently immune to the hazard and is the recommended pattern for A/B arms going
forward"* — now guidelines §8.

### 3.5 `D3_VARIANT_COLD_RERUN_PREREGISTRATION.md` — filed, priced, and scope B executed

Three scopes priced from measured walls: **A** faithful reproduction of all 11 variants,
80–110 core-min; **B** retire as superseded, **0 core-min**; **C** re-ask the question on
the *working* config graded on iteration count, 110–150 core-min (3-lever triage subset
35–45). **Chief ruling 2026-08-10: scope B adopted, scope C triage approved, scope A
declined.** The retirement reasoning, in full at §6: every one of the 11 arms carried
`"transonicPCOption": 2`, which is **dead code for `DARhoSimpleCFoam`** (only `== 1` is
live at `DAResidualRhoSimpleCFoam.C:173`; `== 2` exists solely in
`DAResidualTurboFoam.C:176`), so each null means *"this lever did not rescue a run whose
preconditioner was off."* *"The audit's requirement — cold rerun before any future
citation — is **satisfied by never citing them**. Retirement is the stricter option, not
the lazier one."*

### 3.6 `S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md` (zero compute) — four results, three at R1's own expense

1. **D68 — PR-1, the one thing R1 asked to buy at 25 core-min, was already on disk.**
   `grad_anchorw.npy` is `dJw/dβ` at β = 1 against a genuinely different functional
   supported on **2,970 cells** versus varianceU's **21,000** — billed 16.83 core-min on
   2026-08-08. Scored against the first map: **Spearman +0.9894**, top-decile overlap
   **1,975 of 2,100 = 94.05%** against a 10% chance level, upstream shares **45.76% vs
   45.57% — agreeing to 0.19 percentage points**. *"Changing the objective's spatial
   support by a factor of seven moves the sensitivity geography less than repairing the
   inlet did"* (that comparator: Spearman +0.9450, overlap 61.14%).
2. **D67 — G-P4, the control gate on a 260 core-min item, cannot fail.** All three legs are
   functions of (β, g_QoI, λ_L2); the cosine is fixed by the other two through
   `ε² = 1 + r² − 2rc` to **2.2e-16**. A treatment reporting the **prior as the posterior**
   — the exact shape falsifier F1 exists to catch — reproduces all three to **0.0e+00**
   relative error and **PASSES**.
3. **D70 — the curvature R1 declared unreconstructible is on disk, twice.** True for
   consecutive-iterate pairs, false for **secant** pairs: `sᵀy = sᵀH̄s` **exactly** by the
   mean-value form. Reinversion `sᵀy_QoI = +7.313133e-01`, prior-preconditioned Rayleigh
   quotient **+1.966e+03** (data-dominated); inversion **+6.086e-01** (prior-dominated).
   Out-of-sample control on the corrupted run: linear term alone **99.98% wrong**, linear
   + ½sᵀy **0.06% error**.
4. **G2 is numerically exact.** Under a domain-decomposition change (scotch vs simple
   4×1×1), G2 moves by **+0.0000 percentage points** and the top-decile set agrees
   **2,100 of 2,100**. *"None of the spread between published G2 values is numerical noise
   from this source."* The trap is documented: compared **unpermuted**, Spearman is
   **+0.0901** and G2 reads 31.19% vs 14.10% — *"a 17-point 'decomposition destroys the
   geography' finding is available to anyone who skips the permutation."*
5. **D69 — G-P2's stated mechanism is the wrong comparison.** The 8.2× prior-pull ratio
   reproduces (**8.18×**), but unpinning is decided by prior pull versus **likelihood**
   pull, and at all 5 archived pinned cells the likelihood pull exceeds even the stronger
   prior's restoring pull (median **5.3×**). n = 5; filed as a caution, not a verdict.
6. **Ranked compute asks:** rank 1 M-A/R2 `-ksp_view` two-arm at **8 core-min** — *"the
   only item on the board that answers a question for 257 runs at once"*; rank 2 W1
   stokesI wave tutorial 5–15; rank 3 **hump adjoint characterisation 40 core-min**;
   rank 4 **PR-1 DO NOT BUY AS SPECIFIED** — *"An experiment whose every outcome leaves
   belief unmoved should not be run"*; rank 5 a/512 rung 760–1,520 **DO NOT BUY**.
   S1-priors: **hold** until G-P4 is replaced and G-P2 re-derived.

### 3.7 `S1_GP4_REPLACEMENT_2026-08-14.md` (zero compute) — the gate replaced, and the W-3 legality check

- **W-3 legality check, executed and tabulated (7 searches):** the **444** top-level run
  directories contain no `S1-priors`; **exactly three** `ledger.csv` files exist, all
  S1-cbfs (72 / 41 / 40 lines); **0 files** written in the archive since the
  pre-registration was authored; `docker ps` empty. *"No compute has run. The amendment is
  legal."* Rule **L-44** freezes pre-registrations *"and the freeze is what makes them
  evidence."*
- **The six-treatment discrimination table** — the old gate returns **PASS for W, Z, Q and
  R alike**; the new G-P4b returns PASS for **R alone**. W (prior-as-posterior) λ₁ = 0;
  Z (spectrum read off the prior) removes 5,906 variance units against 1.688 entitled;
  H (correct spectrum, Hv in the wrong frame) fails **leg B alone** at `sᵀHs` = +2.397e-03
  against the band [2.4377e-01, 2.1939e+00]; Q (intervals asserted) removes **1.181e+04**
  against **3.276** entitled, a factor **3,605**, failing **leg C alone**.
  *"H and Q are not straw men."*
- **The deliberate methodological choice:** treatment W is **the triage's specimen, taken
  over verbatim** — *"a wrong treatment built by the same hand that built the gate tends
  to be the wrong treatment that gate happens to catch. The bar the replacement had to
  clear was therefore fixed by someone else, before the replacement was designed."*
- **Rule W-2, stated operationally:** *"a gate whose quantity is derivable by construction
  from its own inputs is an identity, and may be reported but never gated on."* Applied as
  a sibling sweep over every gate in reach; **G-P1** is flagged as a W-2 identity
  (λ_LN = 8.133557e-06 recomputed against the 8.1335e-06 the document already publishes)
  and **filed, not withdrawn — the owner's call**. The same shape is self-declared in
  `S1_WITH_PRIORS_PREREGISTRATION.md` §7(a): *"Bar met in advance by construction."*
- **What rank 6 in 21,000 dimensions actually looks like, computed:** the stand-in
  posterior removes **3.2757 of 11,812.5 units of prior variance — 0.0277%** — and its
  largest per-cell standard-deviation reduction is **0.0143%**.
- **Three proposal records are refused by the real inbox reader** and are invisible to the
  queue: `dafoam-restore-ksp-options-escape-hatch`, `f5c-unsteady-probe-run`,
  `test-the-solver-default-relaxation-across-the-family`. *"Reported, not repaired."*

### 3.8 `R5_ADJOINT_CONDITIONING.md` — and its retraction, and the correction to the retraction

Measured on the M6 (compressible transonic `DARhoSimpleCFoam`) family: assembled `dRdWTPC`
200,360², 22,017,324 nonzeros, **diagonal spread log10 14.17** (row 12.45, col 12.52).
`normalizeResiduals=["None"]` converts denormal collapse (`-5`, residual → 6.6e-310) into
**honest stagnation** (`-3`, residual ~2.0e-2) — confirmed three times, on both objectives
separately, with and without MGSO. **§5's follow-up closes the question the rest opened:**
under `normalizeResiduals=None` the diagonal spread is **16.14 decades — *worse* than the
14.17 baseline**, so *"residual scaling was never the whole story."*

The mechanical finding this family reuses: DAFoam's success gate is fooled by a collapsing
residual — a `-5` run prints *"Residual tolerance satisfied, solution finished!"* and lets
OpenMDAO continue. **This was later scoped:** `S1_FIML_FIELD_INVERSION.md` §25-addendum
item 5 counts the strings directly and finds **`-9` never fools the gate** (0 occurrences
of "satisfied" in every `-9` log; 2 in the `-5` log). *"Extending R5's `-5` result to `-9`
was an over-generalisation. It matters in the safe direction."*

**Three dated layers on §3, all retained rather than deleted:** (a) 2026-08-08 dead-lever
annotation — every M6 run echoed `transonicPCOption 2`, dead code, so *"no archived M6
adjoint — here or anywhere — ran with an active transonic preconditioner"*; (b) 2026-08-10
**RETRACTION** — with the token flipped to 1, both indicted strengthening levers converge
(`pcFillLevel: 1` → reason 2, CD 236 / CL 250 iterations, **−35.9% / −34.7%**;
Richardson → reason 2, CD 209 / CL 211, **−43.2% / −44.9%**); (c) **2026-08-10, same day,
CORRECTION TO THE RETRACTION** — at 42,120 cells **with the PC active**, L3 Richardson
collapses to exactly 0.0 at iteration 200, `gmresRestart`, reproducing §3's signature
verbatim. *"I over-corrected; §3's phenomenon is REAL, and mesh-dependent."* The
retraction and its correction are 3 minutes apart in the record and both are kept.

### 3.9 `ADJOINT_MEMORY_ENVELOPE.md` (D3) — a window, not a ceiling

- **The central claim of every earlier version — "the adjoint works below some cell count
  and fails above it" — "is wrong as stated."** Three distinct failure modes: too coarse
  (primal never converges — M6 at 10,920 cells), usable, too fine by memory, too fine by
  conditioning. The M6 family *"has never, at any tested size from 21,840 to 399,360 cells
  — an 18× range — produced a converged adjoint."*
- **Memory scaling law, fitted independently with `numpy.polyfit` on three controlled
  same-family points:** **memory (MiB) = 1.2125 × cells^0.8485, R² = 0.9992** (21,840 →
  5,876.6 MiB; 42,120 → 9,991.9; 79,560 → 17,603.8; residuals −0.87% / +1.79% / −0.90%).
  **The exponent is sublinear.** Extrapolated: 400,000 cells ≈ **67 GB**, A6's 579,072
  cells ≈ **92 GB** — *"both ordinary cloud sizes, not exotic hardware. **A bigger box does
  not fix this case's adjoint.**"* Hardware recommendation: **WITHHELD**.
- **The 3D constant, and it binds on every "2D" case here.** *"DAFoam rejects OpenFOAM
  `empty` patches outright"* (`DACheckGeometry.C:278`), reproduced in this very tree at
  `ladder-b/B3_work/fixA_kbounds/stage2_serial_run3.log:471`. *"Every nominally-2D DAFoam
  case is therefore a true 3D solve, and **both** Jacobian blocks are sized for the 3D
  mesh regardless of the physics being 2D."*

### 3.10 The liaison memos

**`LIAISON_RESEARCH_adjoint_conditioning.md` (2026-08-04)** — five leads on the `-9`, all
answered by W4 §6:

| lead | proposed | W4's measured answer |
|---|---|---|
| 1.1 shift already hard-coded | `PCFactorSetPivotInBlocks(PETSC_TRUE)`, `MAT_SHIFT_NONZERO`, `PETSC_DECIDE` present since sha `d4ccdb4e` (2022-03-21) | **Confirmed and extended** — *"demonstrated insufficient at a 6-decades-larger zero-pivot threshold"* |
| 1.2 `jacMatReOrdering` sweep | five values | **already complete before the memo** — PROOF §25.2, none converges |
| 1.3 options unreachable; nzdiag one-liner | claimed no runtime option reaches the sub-PC | **half-corrected, half-refuted** — factor options **are** reachable (`PCView` evidence); the proposed nzdiag reorder still returns `-9`; *"The one-word patch that does work is `PCILU` → `PCLU`"* |
| 1.4 `adjEqnSolMethod: fixedPoint` bypass | bypass GMRES+ILU entirely | **refuted at zero compute** — the adjoint state set is `(U, p, phi, nuTilda)`; `calcLduResidualTurb` is overridden **only** in `DASpalartAllmarasFv3`, and `DAkOmegaSST` inherits `FatalError "Child class not implemented!"`. *"there is no omega adjoint in that state set, so `dR/dbeta` can never be seeded through it"* |
| 1.5 `transonicPCOption` for M6 | — | out of the item's gate; later became the token that retracted R5 §3 |

Also correctly recorded: *"**`gmresPCMatOrdering` does not exist in v5**"*; the v5 name is
`jacMatReOrdering`, default `rcm`.

**`LIAISON_NOVELTY_SWEEP_decomposition_defect.md` (2026-08-04)** — **63 recorded searches
across 10 venues**, every hit and every explicit negative logged.

- **Target D (decomposition): no prior report found.** *"the word 'scotch' appears in
  **zero** issues and **zero** discussions in the project's history."* Upstream
  acknowledges parallel-wrong derivatives for **exactly one family** — periodic/AMI coupled
  patches (#379, #946, #972) — always attributing it to the coupled patch and naming no
  mechanism; *"our Ahmed-body case has **no coupled patches**."* The shipped default is
  scotch (`pyDAFoam.py:590-591`), *"i.e. the defect's triggering configuration is the
  default nobody is warned about."*
- **Target R (rotation): no other trace.** `getRotationMatrix3d` appears in **zero** GitHub
  issues/PRs globally; `mdolab/idwarp#57` (open since 2021-07-14, **zero comments**) is the
  sole community record.
- **Target S (sub-LU): no upstream doc, issue or discussion mentions ILU singularity, zero
  pivots, or a direct/sub-direct factorization** — 8 targeted searches plus 4 doc-page
  reads. The complete upstream remedy ladder is `renumberMesh -overwrite`; `pcFillLevel`
  1→2; `jacMatReOrdering` rcm→nd/natural; `gmresRestart`/`gmresMaxIters` up; `asmOverlap`
  up; upwind schemes; kahip; `transonicPCOption`. *"Nothing in that ladder changes the
  sub-PC **type**; the ILU choice itself is never questioned upstream."* The PETSc side
  supplies the precedent: Barry Smith, petsc-users `msg24474` (2015-03-26) **[verbatim]** —
  *"Try `-sub_pc_type lu` and see if that produces a different result."*
- **Live upstream today:** #1002 / #1011 (2026-07, open, unresolved) show users exhausting
  the documented ladder **on official tutorials** and stalling.

### 3.11 `DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` (2026-08-04, zero compute)

Three method papers **READ IN FULL**. Three facts fall out: (1) **no paper ever varies the
decomposition of anything**; (2) *"the operator our defect lives in — the matrix-free
reverse-AD transpose-product path — has exactly one published accuracy measurement, and it
is **serial**"* (Kenway et al. PAS 2019 §5.1, 8 components, 10-digit agreement,
*"np=1, stated twice, by design"*); (3) no verification combines a refinement-interface
mesh with a stated graph partitioning. **The DAFoam v4/v5 rewrite has no archival method
paper at all.** The correction this forced on our own record: the AIAA-J abstract's
*"<0.1% at up to 1536 cores"* is **two disjoint experiments** — a runtime-only Table 2 at
1536 cores on a 10.1M-cell mesh, and a ~103k-cell Table 3 accuracy study at an unstated
core count — **and both belong to the v1 explicit-FD-Jacobian architecture.** *"The report
does not contradict a published measurement; it fills a hole the survey's own conclusions
declare. This **strengthens** the report."*

### 3.12 `GENERATOR_FINDING_pyhyp_aspect_ratio.md` — and the cross-check that reframes it

**Status: not filed anywhere.** Measured with `checkMesh -allGeometry`: max cell aspect
ratio **97.87 → 167.50** under a refinement a user would expect to improve quality; max
non-orthogonality **22.75° → 26.96°** also worsens, while max skewness **1.432 → 0.862**
and every average metric improve. LE-band growth factor **×1.92**, the largest of four
bands. **The 2026-07-30 independent cross-check confirms both numbers exactly** and adds
two reframings that matter more than the finding: (1) these are **3D** meshes, so
OpenFOAM's aspect ratio takes a different code branch than an `empty`-patched 2D mesh —
*"a pyHyp '167' and a 2D TMR '20 million' are therefore not the same quantity"*; (2)
NASA's own TMR NACA0012 reference grids show the same behaviour far more strongly
(**20,650,841 → 26,446,227 → 29,899,837**), so *"'max aspect ratio worsens under
refinement' is … a property of reference-grade wall-resolved grid families in general and
cannot, on its own, indicate a generator defect."* The proposed
`epsE`/`epsI`/`theta`/`volSmoothIter` scaling ablation was **not run** — pyHyp is not
installed on the cross-check host.


---

## 4. DOCKET / LESSONS / NUMERICS_KNOWLEDGE cross-reference

**File sizes at reading (2026-08-21):** `docs/DOCKET.md` 804 lines; `docs/LESSONS.md` 8,283 lines;
`docs/NUMERICS_KNOWLEDGE.md` 2,401 lines.

### 4.0 Numbering, as measured (both asked for explicitly)

| file | scheme | highest id | line | contiguous? |
|---|---|---|---|---|
| `docs/LESSONS.md` | H2 headings matching `^## L-(\d+)\.` | **L-185** | **`:8261`** | **No.** 185 lesson blocks span **184 distinct numbers**: **L-52 does not exist**, and **L-43 is duplicated** (`## L-43.` at `:1885` and `## L-43, second corollary.` at `:1928`). The file is also **not in monotonic order on disk** — L-4 sits at `:220`, after L-5/L-6/L-7. The closure team's L-145..L-185 run occupies `:6856`–`:8261`. **There is no L-186 or higher.** The next lesson is **L-186**, and it must be derived with the period-anchored regex the file itself mandates (`:5405`), never by incrementing a remembered maximum. |
| `docs/NUMERICS_KNOWLEDGE.md` | **one** structured family, `N-B<n>` | **N-B20** | **`:2238`** | **Yes.** N-B1 (`:2078`) .. N-B20, no gaps, no duplicates, 20 definitions + 2 internal cross-references. |

**The `N-B` prefix means "Lane B", not a topic letter.** The family is introduced by the section
header at `:2073`: *"Closure-modelling numerics, measured on this machine — appended 2026-08-20
(Lane B, reviewed by supervisor)"*. **There is no `N-A` family** in that file or anywhere in the
repo. Everything else in `NUMERICS_KNOWLEDGE.md` is unnumbered prose under `##`/`###` headings,
with per-section `### 1.`, `### 2.` counters that **restart in every section** and are therefore
not stable ids.

**Trap for whoever appends N-B21:** the N-B block **ends at `:2249`**, and a *later*, entirely
**unnumbered** section follows it — `## Closure-modelling numerics from the Kaandorp 2020 TBRF
reproduction … (CLOSURE-REPRO, reviewed by supervisor)` at `:2252`, running to the file's end at
`:2401`. **An append at end-of-file lands in the wrong section.** N-B21 goes at `:2249`.

**DOCKET structure:** seven top-level sections (A Katie's; B Machinery; C Memory; D Rung residuals;
E Standing task-list; F Repo professionalization; G Naval), **each with its own table schema**.
474 numbered rows; highest **D439** at `:804`. **IDs are append-only and never renumbered**
(`:23`, Katie, W-4, 2026-08-11), which is why ordering is non-monotonic on disk (D201–D205 sit at
`:273-277`, between D79 and D80). **The D table has no status column** — its five fields are
`# | Item | Where found | What settles it | Owner`, and status is carried inline in bold inside the
Item cell. Anyone building a machine-readable DAFoam docket view must know that.

### 4.1 The cross-reference table

Y/N = still accurate against the case records as of 2026-08-21.

| id | file:line | one-line summary | still accurate? |
|---|---|---|---|
| **L-15** | `LESSONS.md:626` | Adjoint reported SUCCEEDED on `docker_exit=0`; both solves returned PETSc `-5` DIVERGED_BREAKDOWN with residual collapsing to ~1e-322 immediately before printing *"Residual tolerance satisfied"*. Adjoint works at 63,920 cells and breaks at 79,560 with >4 GB headroom unused — **convergence, not memory** | **Y**, and **scoped**: `S1_FIML_FIELD_INVERSION.md` §25-addendum item 5 counted the strings and found this false-success behaviour is specific to **`-5`**; **`-9` never fools the gate** (0 "satisfied" lines in every `-9` log). *"It matters in the safe direction."* |
| **L-16** | `LESSONS.md:664` | The pattern table entry: reading `ConvergedReason = -5` instead of the exit code cost *"a hardware recommendation, in the wrong direction"* | **Y** — reinforced by `ADJOINT_MEMORY_ENVELOPE.md`, whose hardware recommendation is **WITHHELD** |
| **L-22** | `LESSONS.md:995` | F5c has no adjoint/DAFoam variant and its RSS stays flat at ~79 MB; the real source of the OOM claim is **B3 CBFS**, which really does OOM and really does produce `DIVERGED_NANORINF` | **PARTLY — CORRECT ON ATTRIBUTION, WRONG ON MECHANISM.** B3/CBFS produces `-9` DIVERGED_NANORINF, confirmed; but the B3 record contains **no OOM**: `B3_duct_field_inversion.md` §Memory records *"no run was OOM-killed (`docker inspect` exit codes seen were 0, 1, 2, 59 — application/MPI-level failures, never 137)"*, at `--memory=6g`. The lesson's "really does OOM" conflates B3 with the A3/M6 memory wall |
| **L-29** | `LESSONS.md:1380` | IDWarp `getRotationMatrix3d` degenerate-branch guard (`vectorUtils.f90:58`, v2.6.2) differentiates to a hard zero: A1 **634%** sign-flipped, A5 **207%/122%**, upstream `mdolab/idwarp#57` **210%/213%** | **Y** — and the novelty sweep confirms #57 is still the **sole** community trace, zero comments since 2021-07-14 |
| **L-32** | `LESSONS.md:1544` | A4's verdict moved CONDITIONAL→PASS into four satellites and **zero** ladder files; `ladder-a/A4_ahmed_body.md:158` still asserted *"graded CONDITIONAL, not PASS"* | **N as written, and the record says so.** `SUPERVISOR_FAMILY_REVIEW_2026-08-07.md` Part 1 *"Checked and found consistent"*: *"`ladder-a/A4_ahmed_body.{md,json}` — the L-32 staleness is FIXED … L-32's 'it still is not' refers to the pre-fix state."* The **rule** stands; the **instance** is closed |
| **L-34** | `LESSONS.md:1611` | *"Unreachable at runtime" is a claim about the deployed object, not about one call site.* Three readings (R5, PROOF §25.3, the liaison memo) drew the reachability boundary in the wrong place; `-sub_pc_factor_zeropivot 1e-8` **does** land in the deployed factor, proven by `PCView` | **Y** — this is W4 §2's finding promoted to doctrine. The truly unreachable set is exactly what DAFoam overrides *after* `KSPSetUp`: type, ordering, fill, shift |
| **L-35** | `LESSONS.md:1643` | **A converged Krylov solve certifies the operator it was given, not the operator you meant.** A4 read 8.95% off FD at np=4 scotch with `reason 2` and rtol 1e-6; the converged psi evaluated under the np=1 operator gives **329× ‖b‖** against a **1.1e-04** serial floor. Map with integer `cellProcAddressing`, never coordinate matching; diff operator **actions**, not entries | **Y** — and it is the family's operator-level truth instrument (`FAMILY_SUPERVISION_GUIDELINES.md` §2). Note the instrument's own sign bug (A-1) was **FIXED 2026-08-07**; the control now reads **1.140697e-04** without an offline correction |
| **L-36** | `LESSONS.md:1675` | A gradient check certifies a **contraction**, not an operator. Ahmed-35: cross-residual **5.45×‖b‖** vs simple's 0.33× (16× larger) yet gradient shift **2.3× smaller** (1.36% vs 3.14%) | **Y** |
| **L-37** | `LESSONS.md:1703` | **Branches first.** One-word `linearUpwind limited → default` took np=4-scotch from **8.95% → 0.849%**, Krylov **719 → 41** (17.5×), cross-residual **329× → 0.0135×‖b‖**. The complementary trap: `inletOutlet` "cleans" the gradient to **0.019%** while leaving the operator at **1.047×‖b‖ = 163,548×** the np=1 floor | **Y**, with its own correction already applied in place: **590 → 719** struck and corrected 2026-08-07 per the defect-robustness sweep (commit 8bd47b35), and 163,600 annotated to the full-precision 163,548. This was `SUPERVISOR_FAMILY_REVIEW`'s finding **DISC-1 / F-1** |
| **L-38** | `LESSONS.md:1736` | Acquisition arm: np=1 and np=4-scotch analytics agreed to **3.9e-04**, FD columns to 1e-6, Krylov counts within one iteration — **and both analytics were 92.8% wrong together.** Decomposition-invariance is not correctness | **Y** |
| **L-40** | `LESSONS.md:1803` | *The switch you set is not the switch that ran.* Every archived ONERA M6 adjoint script set `transonicPCOption: 2`, dead code for `DARhoSimpleCFoam` (`DAResidualRhoSimpleCFoam.C:173` accepts only `== 1`) | **Y** — and it is the token that produced R5 §3's retraction, then the same-day correction to that retraction |
| **L-43, second corollary** | `LESSONS.md:1928` | FD-2 (*"`DASimpleFoam` drops `consistent yes`"*) **refuted** — SIMPLEC is implemented in both primal (`pEqnSimple.H:27`) and adjoint (`DAResidualSimpleFoam.C:189`), both `rAtU = 1/(1/rAU - UEqn.H1())`, in both images. *"The file list, not the search string, was the defect"* | **Y** |
| **L-63 CORRECTION** | `LESSONS.md:2745` | L-63 read a docstring sentinel as `W2_sparta_runs/cbfs_prop`; the git record points at `dafoam/ladder-b/B3_work`; the byte sequence appears in **18 files** | **Y** |
| **L-93** | `LESSONS.md:4166` | The closure-challenge check grades against `~/closure-challenge-benchmark/README.md`, **outside this repository** — no `git worktree` can pin it; mtime **2026-08-17 17:29:00 UTC** fell exactly between two runs and the board had gained an entrant | **Y**, and directly relevant: every Ladder B score in §1 was read from that same unpinnable clone |
| **L-102** | `LESSONS.md:4690` | **85 lines in 59 files** name `/home/ubuntu/closure-challenge-benchmark` (15 executable, 8 published `.json`); **17 lines in 14 files** name `/home/ubuntu/dafoam-tutorials` | **Y** |
| **L-122 / L-127 / L-138** | `LESSONS.md:5740`, `:5943`, `:6468` | The R22 move took `demo-output/website/dafoam` → `cases/dafoam`, **two segments shallower**, and broke path constants built on `parents[N]` | **Y and live** — see D385, D387, D402, D404 below; `cases/dafoam/INDEX.md` §0 records the reader-facing half |
| **L-147** | `LESSONS.md:6931` | Coupling/stabiliser table: **Singh 2017 FIML** uses a multiplier `beta(x)` on the **SA production** term with **no stabiliser** and convergence *"comparable to the baseline"* (p.22) | **Y**, and it is the closest external precedent for S1's production-term choice |
| **L-170** | `LESSONS.md:7805` | Pope basis mean rank **3.24** over 5,000 training cells (3,814 at rank 3, 1,185 at rank 4, one above 4, none above 5) | **Y** (also `N-B10`) |
| **L-177** | `LESSONS.md:7973` | The SpaRTA reproduction was **already done** on 2026-08-01 — twenty run directories, total prior cost **2.7 core-hours** against a 20 core-hour budget | **Y** |
| **N-B3** | `NUMERICS_KNOWLEDGE.md:2093` | `a1 = 0.31 < 1/3` is a realisability constraint; the SST shear-stress limiter is **active on 18–33% of cells in all 40 Closure Challenge cases** | **Y**, and it is the general-population number that gives S1's measurement its scale: the limiter binds on **7.7%** of CBFS cells at β=1 but **49.5%** of top-decile cells, and **24.8% / 51.6%** after the re-inversion |
| **N-B10** | `NUMERICS_KNOWLEDGE.md:2152` | Per-cell Pope-basis rank **3.24** mean | **Y** |
| **N-B20** | `NUMERICS_KNOWLEDGE.md:2238` | *Name your cell masks*: 342,014 (LES-only) vs 341,717 (also requires finite `b_RANS`) differ by 0.09%; all **567** separating cells are non-finite `b_RANS` | **Y** (last id in the family) |
| **NUMERICS `:533-536`** | `NUMERICS_KNOWLEDGE.md:533` | **The Ladder B gate, stated as a numerics fact:** *"the Wu/Zhang/Zhang duct zero-shot result (0.0455/0.0399 on `AR_1_Ret_360`/`AR_3_Ret_360`) is the number Ladder B is trying to reproduce; the gate is whether Ladder B3's blocked adjoint (`PETSc KSP_DIVERGED_NANORINF`) can be unblocked and the full CBFS-trained field inversion reproduced to within a stated tolerance of those two scores."* | **HALF Y, HALF N — and this is the single most important stale line for this lane.** The adjoint **was** unblocked (W4, on a patched image) and a full CBFS field inversion **has** run — twice, plus a weighted arm. What has **never** happened is the second half: no beta field has been carried forward to score `AR_1_Ret_360`/`AR_3_Ret_360`, because Stage 2 is held (gates did not pass) and the field is production-term-labelled. **This gate has no corresponding closed docket row** |
| **NUMERICS `:685-686`** | `NUMERICS_KNOWLEDGE.md:685` | DPW CRM grids never below ~5M cells — **9–55× our largest converged primal (579,072, A6)** and **75–495× our adjoint's measured OOM threshold (156,089)**; *"DAFoam's DPW4_Aircraft tutorial defaults to 192 ranks"* | **Y**, but the OOM-threshold framing should now carry `ADJOINT_MEMORY_ENVELOPE.md`'s correction: the threshold is **per-family**, and an incompressible 51,626-cell case gets past coloring with 18.99 GB free |
| **D5** | `DOCKET.md:129` | `sdk/workflows/adjoint_optimization.py` swallows the certificate `unlink` B2 fixed in ten places | **Y, still live** (confirmed live by D43 at `:236`) |
| **D8b** | `DOCKET.md:133` | The S1 plateau-balance triple unreconciled by **1.684×** | **N — CLOSED 2026-08-15 as superseded by D9.** The refutation landed at `57fd0d83`; the 1.684 came from pairing a plateau-state ratio and cosine with `‖g‖₂` reported at **eval 16**, a different state. Note the id was **corrected from a second `D8`** — a numbering collision |
| **D9** | `DOCKET.md:134` | The triple **reconciles exactly**: ratio 0.998441, cos 0.999542, rms 0.016502 | **Y** |
| **D10** | `DOCKET.md:135` | DAFoam's `printInfo` prints ASM/ILU levers regardless of the preconditioner actually built: `stage2_gamg.log:864,867,868` print `ASM Overlap: 1`, `Mat ReOrdering: natural`, `ILU PC Fill Level: 0` while `-ksp_view` at `:884` shows `type: gamg`; **0** `type: asm` and **0** `type: ilu` in the file. Cheapest close **M-A, ~8 core-min**, settles ordering for all **257** archived runs | **Y — "Not authorised; not run."** This is the highest-value cheap item touching this lane, and `S1_ZEROCOMPUTE_TRIAGE` ranks it **#1** independently. **It bears directly on every `rcm` citation in the B3/CBFS record** |
| **D11** | `DOCKET.md:136` | The hump adjoint family predates the launcher lever echo (`199e9d17`, 2026-08-10); DAFoam echoes neither `fvSchemes` nor relaxation factors | **Y — latent exposure, not a live gap.** *"Nothing, until a hump conclusion cites a scheme"* |
| **D16** | `DOCKET.md:141` | The FD-vs-adjoint **shared-primal** limitation is stated in `PROOF.md:917-940`, `W5_GRADIENT_REGRADE.md:622-631` and `VERIFICATION_A4_mechanism_supervisor_sweep.md:121-126` — and **absent from the gate lines** | **Y, open, zero compute** — and it applies to every FD number in §1.2 |
| **D40** | `DOCKET.md:233` | `ROOTCAUSE_getRotationMatrix3d.md` §4.7 tests P6 (*"reordering must not move the result at all"*), reports **207.04% vs 207.05%** and concludes reordering is not a factor — **a dead lever answers identically** | **Y — CLOSED as a finding, and it is a caution the DAFoam team owns**: a null result on an inactive lever is not evidence |
| **D45** | `DOCKET.md:238` | R5's premise measured false: top decile of `\|g(β=1)\|` is **35.4% in-window against an 8.44% base rate — ×4.19**; **do not buy R5 at 340 core-min**; both archived G2 values (29.0476%, 26.8571%) reproduce at zero compute; PR-1 worth 25 core-min | **Y on the R5 kill; N on the PR-1 price** — D68 (`:261`) supersedes it: the deliverable was already on disk |
| **D67** | `DOCKET.md:260` | Restored G-P4 is the same could-not-fail control in three parts; gates the most expensive unrun item on the S1 board | **Y, and superseded twice more** — D75 (`:268`) withdrew it a second time on the `ε² = 1 + r² − 2rc` identity (agreement **2.220e-16**); D98 (`:467`) then found the published `0.0e+00` was a **print literal** in `s1_zerocompute.py:295-296` with `G-P4: PASS.` **inside the format string** — *"the number is not wrong"*, but it was never computed at that call site |
| **D68** | `DOCKET.md:261` | PR-1 asks 25 core-min for a map already on disk (`grad_anchorw.npy`) | **Y** |
| **D69** | `DOCKET.md:262` | G-P2's stated mechanism reproduces (**8.18×**) but is the wrong comparison | **Y** |
| **D70** | `DOCKET.md:263` | *"Nine gradient arrays survive"* is frame-scoped — **14 survive** and **two secant pairs are reconstructible at zero compute**, falsifying the buy-curvature-fresh premise | **Y** |
| **D76** | `DOCKET.md:269` | Second W-2 identity in the S1-priors prereg: `λ_LN = λ_QoI·σ_d²/(3N·s²)` returns **8.133557e-06** against the **8.1335e-06** the document already publishes | **Y — reported, deliberately not withdrawn; the owner's call** |
| **D80** | `DOCKET.md:449` | `lab_check.py --only self_audit` on a purged tree returned **9 FAIL and 9 WARN**; among them, `dafoam/ladder-b/S1_FIML_FIELD_INVERSION.md:229` cites `scripts/analyze_fd.py`, actually at `.../S1_work/scripts/analyze_fd.py` | **Y — a live, one-line citation defect inside a Ladder B record.** It is a **path** error only; the finding it supports (the analyzer reads only the `OBJ` line and never inspects the log) stands |
| **D115 / D145 / D205** | `DOCKET.md:484`, `:515`, `:750` | `latex/closure_challenge_report.pdf` (41 pages, mtime 2026-08-11 03:26Z) predates the board move by 20 hours and contains withdrawn figures — `P(rank 1) = 68%` **twelve times**, margin `0.002878` four times, Yang absent from Table 1; **"no check in this lab opens a PDF"**; `closure_challenge_report.tex` is a day and a half **newer** than its own PDF | **Y** — and `dafoam_defect_report`'s ordering is healthy by contrast (.tex 03:24:39, .pdf 03:26:38) |
| **D201 / D202** | `DOCKET.md:273`, `:274` | Two **identity-gates** in the Ladder A record: A6's convergence gate holds by construction (`relTol 0.1; tolerance 0;`, **66 lines, violations 0**), and the `volcon`/`thickcon`/`rcon` `check_totals` rows read **4.37e-12% / 1.27e-11% / 1.36e-08%** and **cannot move under the IDWarp patch** — yet their non-movement is cited as evidence the patch did no harm | **Y** — Lane A's territory, but the **rule** (W-2: an identity may be reported and never gated on) binds Ladder B equally, and `S1_GP4_REPLACEMENT` §6 is its worked application |
| **D204** | `DOCKET.md:276` | A6's "memory wall" is misnamed — `PRODUCT_LIST.md:251` says *"Adjoint not attempted (memory wall)"* against `:176-179`'s `DIVERGED_BREAKDOWN` at 21,840 cells with **>20 GB free**; a probe at **79,560 cells / 724,609 adjoint states** ran 200 KSP iterations twice, each `-5` | **Y**, and it carries a **prohibition**: *"an A6 adjoint attempt (760–1,520 core-min) must NOT be proposed"* to settle this — a zero-cost analysis decides the same question |
| **D213 / D260 / D269** | `DOCKET.md:578`, `:625`, `:634` | The `s1-cbfs-w1-only-arm` proposal (150 core-min) — its named trigger **FIRED** on 2026-08-11 and the dispatch surface carried no record | **N as a live proposal — KILL RATIFIED** (D269, `LADDER_RULINGS_2026-08-16.md`) on D213's deliverable-level ground: **G2 invalidated six independent ways** |
| **D218 / D219 / D225** | `DOCKET.md:583`, `:584`, `:590` | The **two docket surfaces disagree on 45.3%** of shared items — **463 core-min of finished work advertised as available** and **7,650 core-min of approved work advertised as merely proposed**. Of 245 one-sided ids, **235 legitimately one-sided, 10 are faults** | **Y** — any DAFoam dispatch must read `docs/DOCKET.md` **and** `agenda/docket.json`, not either alone |
| **D383** | `DOCKET.md:748` | **Twelve gate rows** compare against an obtained reference with **no pre-registered tolerance**. Named instances: `ladder-a/A3_onera_m6.md`'s Cp-RMS and shock-location rows assert **GATE REACHED** after the deviations were read; **F6a's reattachment misses by +13.9% and the row reads GATE REACHED**, carried to the nine-act table as `VALIDATED` | **Y, and it lands squarely on §2 of this document.** *"There is no miss large enough to have failed it."* F6a's own text is honest about the miss; the **verdict token** is what is unearned |
| **D385 / D387 / D402 / D404** | `DOCKET.md:750`, `:752`, `:767`, `:769` | R22 path-move fallout: `test_a2_shape.py:28` `parents[3]` began naming `/home/ubuntu/sdk`; `.gitignore:140-158` routes `dafoam/`'s re-point to batch 7 when `dafoam/` is **batch 6**; `f6d_random_matrix_uq/make_campaign_json.py:7` `CAMP = HERE.parents[1] / "campaign"` became the non-existent `cases/campaign`; **eight path constants** still built as `REPO / "demo-output" / "website" / …` | D402 **CLOSED**; D385, D387, D404 **OPEN**. The `f6d` one is inside this tree |
| **D396** | `DOCKET.md:761` | `crm_wingbody.py:328-333` assigns `VALIDATED` directly against `PUBLISHED_CD = 0.02090`, bypassing `validate_against_reference()` — and the reference is **DAFoam's own `CRM_Wing` tutorial**, i.e. code-to-code, not experiment | **Y**, same class as D14 (`:139`) |

### 4.2 What is NOT in the docket, and should be noticed

- **The NUMERICS `:533-536` Ladder B gate has no docket row of its own.** It names the reproduction
  target (0.0455 / 0.0399) and the blocker in one sentence, and nothing tracks its state.
- **`rans_model_comparison` has no docket row, no `.md` record, and no lesson.** Its LienCubicKE
  result (7.85% of the DNS secondary flow against ~0% for four linear models) is the cleanest
  in-lab demonstration of the Boussinesq deficit and exists only in a JSON file.
- **`f6a_epistemic_band` and `f6d_random_matrix_uq` — 6.0 GB, 88% of this tree — have no `.md`
  record inside `cases/dafoam/` at all.** Their records are in `verification/campaign/`.

---

## 5. Standing-picture audit

Each line as handed to this lane, marked **CONFIRMED** / **CORRECTED** / **NOT IN RECORDS**.

| # | standing line | verdict | correct value and citation |
|---|---|---|---|
| 1 | *B1 research only* | **CONFIRMED** | `ladder-b/B1_reproduction_plans.md:3-4`: *"**Research and planning only — no solver runs, no compute launched in this rung.**"* Restated at `DAFOAM_CASE_STATUS.md:121` |
| 2 | *B2 CBFS baseline (plain simpleFoam)* | **CONFIRMED** | `DAFOAM_CASE_STATUS.md:123` heads the entry *"**not a DAFoam run** — plain OpenFOAM `simpleFoam`/`kOmegaSST`"*. `B2_duct_baseline.json` `environment.solver`: *"simpleFoam (plain OpenFOAM, not DAFoam -- this is an uncorrected baseline, no adjoint needed)"*, `ranks: 1`. **Add**, because it is easy to miss: B2 covers **three** cases, not one — `AR_1_Ret_360`, `AR_3_Ret_360` and CBFS, of which only CBFS is the field-inversion training case |
| 3 | *B3 CBFS field inversion **BLOCKED*** | **CONFIRMED, with the R11 frame made explicit** | **BLOCKED stands against the SHIPPED toolchain and only against it.** `DAFOAM_CASE_STATUS.md:134` (closing sentence): *"The shipped image is unmodified: BLOCKED as graded against the shipped toolchain stands; nothing filed upstream."* Against the locally rebuilt `dafoam-subpclu:v1`, the same configuration converges: **`PetscConvergedReason: 2`, 667 iterations** (`ladder-b/W4_ADJOINT_PC_UNBLOCK.md:16-19`, `:157`). Stating one half without the other misreads the record in either direction. Full settlement in §1.0 above |
| 4 | *primal converged in **1223** iterations* | **CONFIRMED** | `ladder-b/B3_duct_field_inversion.md:158`: *"1223 (converged, tol satisfied)"* at `primalMinResTol=1e-6`, serial, 234.97 s, 0.192 s/iter (`:175`), agreeing with B2's baseline to **0.0865% / 0.233% / 1.414% / 1.198% / 0.460%** (U/p/k/omega/nut) |
| 5 | *adjoint diverges `PetscConvergedReason -9`* | **CONFIRMED** | `ladder-b/B3_duct_field_inversion.md:232-237`, printed verbatim: `**Completed**! Total iterations: 0. PetscConvergedReason: -9.` **`-9` is `KSP_DIVERGED_NANORINF`**, detected at GMRES iteration 0 with a finite nonzero initial residual **7.09e-04** and **zero iterations completed** — a linear-algebra failure, not a gradient blow-up (`B3_supervisor_debug.md:15-17`) |
| 6 | *root cause an **exact zero pivot in ILU*** | **CONFIRMED** | `PROOF.md` §25.3: *"`scipy.sparse.linalg.spilu` on the same matrix fails with `RuntimeError: Factor is exactly singular`. **The incomplete factorization hits an exact zero pivot.**"* Not a knife-edge drop tolerance — the whole strength axis was swept and **incomplete factorization never succeeds** (drop_tol 1e-2/fill 3, 1e-3/fill 5, 1e-4/fill 5, 1e-5/fill 10, all singular) |
| 7 | *reproduced with `scipy.sparse.spilu`* | **CONFIRMED, module path worth stating exactly** | It is **`scipy.sparse.linalg.spilu`** (and `scipy.sparse.linalg.splu`), not `scipy.sparse.spilu`. `PROOF.md` §25.3 and `DAFOAM_CASE_STATUS.md:133` |
| 8 | *full LU with partial pivoting succeeds on the same matrix* | **CONFIRMED, with three thresholds and the price** | `splu` solves at **every** pivot threshold: `diag_pivot_thresh=0` → **2.3769e-10**, `0.1` → **6.4063e-12**, `1` → **2.535461e-12**. The record also states the cost the standing line omits: the complete factors carry **24–28× the matrix's own 13,710,468 nonzeros, roughly 3 GB, on a 21,000-cell case** (`PROOF.md` §25.3) |
| 9 | *no pivoting option exposed via `daOptions`* | **CONFIRMED — and it is now a stronger, better-scoped statement** | `PROOF.md` §25.3: *"`DALinearEqn.C` hard-codes `PCType localPCType = PCILU;` … so no `daOptions` lever reaches a pivoting-capable factorization without recompiling `libDASolver.so`."* **But the neighbouring claim that nothing at all reaches the sub-PC is too strong and was corrected**: `sub_`-prefixed **factor** options (`nonzeros_along_diagonal`, `zeropivot`, `diagonal_fill`, `mat_solver_type`) **are** consumed, measured by `PCView`, because `PCSetUp_ASM` calls `KSPSetFromOptions` on each sub-KSP inside `KSPSetUp` — **before** DAFoam's overrides (`W4_ADJOINT_PC_UNBLOCK.md` §2 and §6 lead 1.3; promoted to **L-35's neighbour L-34**, `LESSONS.md:1611`). **Every one of the reachable options was tested and none fixes the failure**, which is what justified the rebuild as measurement rather than taste |
| 10 | *needs a recompile of `libDASolver.so` or an upstream change* | **CORRECTED — the recompile was done, on 2026-08-04, and it worked** | The one-hunk env-gated patch at `DALinearEqn.C:266–267` (`DAFOAM_SUBPC_TYPE=lu` → `PCLU`), built as `dafoam-subpclu:v1` across all three AD modes in ~40 s of compile, **converges B3's exact configuration** (reason 2, 667 iterations) and produced the first FD-verified field-inversion gradient in this lab (`W4_ADJOINT_PC_UNBLOCK.md` §4–§5d). The patch is at `subpclu_patch/DALinearEqn_subpclu.patch`, regenerated 2026-08-07 so `git apply --check` passes. **The upstream change was never made and never filed.** What remains true: under the **shipped** library the statement stands verbatim |
| 11 | ***Three defects identified**, none filed upstream* | **HALF CONFIRMED, HALF CORRECTED** | **"None filed upstream" is CONFIRMED and is standing policy**, not merely a state of affairs: `FAMILY_SUPERVISION_GUIDELINES.md` §3.6 — *"Nothing is filed upstream by anyone in this family, ever. Both reports and the tex carry NOT FILED status; filing is Katie's call alone."* Verified at both sources: `UPSTREAM_BUG_REPORT_decomposition_adjoint.md:3` and `UPSTREAM_BUG_REPORT_mesh_warpDeriv.md:3` both open **"Status: NOT FILED ANYWHERE."** **"Three" is CORRECTED — the count depends on what is being counted, and the records give three different answers:** (a) **four defect classes**, per `FAMILY_SUPERVISION_GUIDELINES.md` §6.4, which defines a new defect class as *"anything that is not the rotation guard, the decomposition branch defect, the serial limiter tape, or the ILU wall"*; (b) **three filing-ready artifacts** — `UPSTREAM_BUG_REPORT_mesh_warpDeriv.md`, `UPSTREAM_BUG_REPORT_decomposition_adjoint.md`, and `DEFECT_CANDIDATE_ksp_options_override.md` (FILING-READY, NOT FILED), all three unfiled; (c) **three local patches** — `rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch`, `subpclu_patch/DALinearEqn_subpclu.patch`, `kspopts_patch/DALinearEqn_kspopts.patch`, matching §3.2's *"ALL THREE local patches"*. **A DAFoam charter or README should say "four defect classes, three filing-ready reports, three local patches, nothing filed"** rather than a bare "three defects" |
| 12 | *PETSc ILU singularity is **defect (3)*** | **CORRECTED** | It is **not numbered (3) anywhere**, and in the only enumeration the family maintains it is **listed fourth**: `FAMILY_SUPERVISION_GUIDELINES.md` §6.4 orders them *rotation guard, decomposition branch defect, serial limiter tape, **ILU wall***. It is also the **only one of the four with no upstream bug report drafted** — `PROOF.md` §25.3 records it as *"a located limitation, not a recommendation; nothing has been filed."* The filing-ready artifact on that axis is a **different and narrower** defect: `DEFECT_CANDIDATE_ksp_options_override.md`, class **diagnosability**, which documents that `KSPSetFromOptions(ksp)` at `DALinearEqn.C:138` is followed by **13 overriding call sites** (142–144, 158, 170, 185, 192, 212, 216, 249/259, 286, 328, 343), so `-sub_pc_type lu`, `-ksp_type lgmres`, `-pc_type gamg` and six other documented PETSc remedies are **accepted without error and silently ignored**. *"This is not a wrong answer; it is a defect that prevents a user who has correctly diagnosed their own problem from acting on the diagnosis."* |

---

## 6. Charter and house-style findings

### 6.1 The house-style skeleton of a team charter

Template: `docs/charters/CLOSURE_MODELLING_CHARTER.md` (872 lines, Version 1.1, dated 2026-08-20).

- **No front matter.** No YAML block, no `---` fence, no owner line, no status line. The file opens
  with an H1 at `:1`, a blank line, and the version paragraph at `:3`.
- **Version line, mandated format** (`docs/charters/README.md:104-106`): *"**Bump the version and
  date in the file.** Charters carry `Version N.M, dated YYYY-MM-DD` on the first line, exactly as
  the demo discretion charter does."* The line then continues in the **same paragraph** with a
  *"Governs …"* / *"Defines …"* scope sentence and an *"It binds …"* enumeration of the concrete
  paths the charter reaches. **Ten of eleven charters carry this at line 3.**
  `FILING_CHARTER.md` is the single exception and has **no version line at all** — copy the
  closure charter, not that one.
- **Section order** (`CLOSURE_MODELLING_CHARTER.md`): H1 title → version/scope paragraph → a
  *"what this version adds"* paragraph → a provenance paragraph (*"Every clause below names the
  thing that earned it"*, `:19-20`) → `## 1. The line` — **a single blockquoted bright line** →
  numbered clauses grouped under `# PART I / II / III` dividers, each clause opening with a
  **blockquoted bold normative statement** followed by the incident that earned it →
  `# 20. Enforcement` → `# 21. Changes to other charters` → `# 23. Related` →
  `# 24. Amendment record`.
- **The abstract shape** is stated at `docs/charters/README.md:56-71`: *"(1) A version and a date.
  (2) One bright testable line, stated before any of the reasoning. (3) Numbered sections working
  that line out, with explicit lists of what is required, what is allowed and what is forbidden.
  (4) Worked examples drawn from things this lab actually did. (5) Enforcement: what checks the
  clause, or an honest statement that nothing does yet."* And: *"A clause carrying a lesson number
  is a rule the lab paid for. A clause without one is either obvious or new, and if it is new it
  says so."*

**"What this charter does not cover" — the section does not exist under that name, anywhere.**
Grepped across all eleven charters for `does not cover`, `not in scope`, `Non-scope`,
`outside this charter`: no hit. The house-style equivalents are three:

1. **The `# N. Related` table**, whose column header *is* the scope-exclusion device:
   `CLOSURE_MODELLING_CHARTER.md:852` — `| Document | What it owns that this charter does not |`,
   with 12 rows pointing at VERIFICATION, LITERATURE, COMPUTE_BUDGET, SUPERVISION, FILING,
   RESULT_PRIORITY, and the lane's own doctrine/README/manifest/baselines files.
2. **Per-clause `**Cross-reference.**` paragraphs** stating what a neighbouring charter already
   owns (`:79-81`, `:301-302`, `:364-366`, `:400-403`, `:435-438`, `:613-616`, `:772-774`,
   `:814-816`).
3. **Explicit reach-limit subsections** in `VERIFICATION_CHARTER.md`:
   `:1787` `### Where this rule does not reach, stated so nobody re-derives it by spending`, and
   `:1890` `### What this rule does NOT reach (2c's boundary, applied to itself)`.
   **If a DAFoam charter wants a "does not cover" heading, `### Where this rule does not reach,
   stated so nobody re-derives it by spending` is the existing house heading to copy.**

**Disclosure conventions the house style mandates** (seven, each cited):

1. **PROPOSAL marker, fixed wording** (`docs/charters/README.md:75-86`):
   *"> **PROPOSAL.** Nobody has ruled on this. Written so there is something to argue with."*
   *"the lab must never present its own invention as the owner's policy."*
2. **Enforcement written from what exists, admitting the gaps** (`CLOSURE_MODELLING_CHARTER.md:633-635`,
   `:649-650`): the enforcement table's cells read **`Automatic: no.`**, **`Nothing.`**,
   **`Proposed, not built.`** — *"**Four clauses have no enforcement and are marked so.** A clause
   nobody can fail is a preference, and this table is where that gets admitted rather than
   discovered."*
3. **Known defects disclosed in place** (`:116-120`, `:189-198`), e.g. *"The 297-cell discrepancy
   is unreconciled … flagged here so the next person does not discover it as a surprise"* and
   *"**Do not quote 3.24 until it has a live source.**"*
4. **Additivity disclosure on every version bump** (`:10-12`): *"It is additive: **nothing in 1.0
   was weakened**"* — the formula recurs across charters.
5. **Strike-in-place, never delete** (`VERIFICATION_CHARTER.md:165`): *"**Originals are always
   retained and struck, never rewritten**, under either condition."* Mechanism shown at
   `SUPERVISION_CHARTER.md:184-190` and `ESCALATION_CHARTER.md:154-165`.
6. **Line-stability disclosure on amendments** (`VERIFICATION_CHARTER.md:1732`):
   *"**Lines whose number changed above this section: 0.**"* — because other records cite the file
   by line and one citation sits inside an executable check.
7. **Every clause names the incident that earned it** — executed via `**The incident, 2026-08-20.**`,
   `**The measurement that earned it.**`, `**Three occurrences, nineteen days.**`.

### 6.2 The verdict vocabulary, and where it is defined

**All six tokens are defined in exactly one place: `docs/charters/CLOSURE_MODELLING_CHARTER.md`
§12, the table at `:413-420`.** The permitted-set statement, `:407-409`, verbatim:

> **The permitted verdicts are: `PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`,
> `PENDING`. No other word grades a closure run. A verdict is valid only against a falsifier that
> was in the preregistration before the run.**

| token | line | definition, verbatim |
|---|---|---|
| `PASS` | `:415` | Every registered acceptance criterion met, on the ladder as written. |
| `GATE REACHED` | `:416` | A registered intermediate threshold met; the full ladder is not yet answered. |
| `GATE FAIL` | `:417` | A registered criterion or falsifier fired. **Only a registered one.** |
| `NOT A RESULT` | `:418` | The run produced numbers that do not bear on the question — a broken instrument, an identity gated as a control, an unphysical field under §4, or an a-priori score offered as a prediction claim. |
| `BLOCKED` | `:419` | Cannot proceed: source, data or compute. Names which, and the acquisition path. |
| `PENDING` | `:420` | A registered criterion's control has not landed. Not a failure and not a pass. |

**The conflict a DAFoam charter must resolve explicitly, not inherit.**
`VERIFICATION_CHARTER.md:95-96` and `REPORTING_CHARTER.md:210-211` both *fix* the vocabulary and
both list **five** tokens, **omitting `PENDING`**, and **neither defines any of them**:

> **The verdict vocabulary is fixed.** Gate verdicts: PASS, GATE REACHED, GATE FAIL, NOT A RESULT,
> BLOCKED. *(`VERIFICATION_CHARTER.md:95`)*

`docs/DOCKET.md` records this as a live class of defect twice — D249 (`:614`) and D338 (`:703`) —
for the tokens `PASS WITH EXCEPTIONS` and `DELIVERED`, both of which return **zero occurrences
anywhere under `docs/charters/`**. **`PENDING` is the same defect, and it is unrecorded**: DOCKET
uses it 36 times, `LESSONS.md` L-180 recommends it as the honest verdict where `GATE FAIL` was
written, and no charter outside the closure one defines it. `PASS WITH RESIDUALS` is likewise
outside the five and `DOCKET.md:19-20` still relies on it.

**A seventh token exists and is not a verdict:** `NOT OBTAINED`, owned by
`VERIFICATION_CHARTER.md` §6b — *"it is a statement about a **document**, carries four fields, and
changes no tier by itself. A closure record blocked on a paper says `BLOCKED` in its verdict line
and `NOT OBTAINED` against the reference"* (`CLOSURE_MODELLING_CHARTER.md:422-425`). And an
eighth, from the compute charter: **`UNPRICED`**, `COMPUTE_BUDGET_CHARTER.md:390-395` — *"a
repricing crosses solver families only from that case's own record. Where no such record exists,
the item is reported UNPRICED rather than given a number."*

**Fidelity chips are a separate axis and *are* defined** in `VERIFICATION_CHARTER.md:95-96`:
`VALIDATED`, `SOLVER-BACKED`, `RESEARCH MODEL`, `UNCONVERGED`.

**How this lane's own records score against the vocabulary.** Ladder B's S1 line uses **GATE
PASS / GATE FAIL** consistently and correctly against *registered* gates (`S1_CBFS_INVERSION_RESULT.md`
§3, `S1_CBFS_REINVERSION_RESULT.md` §3, `S1_CBFS_WEIGHTED_ARM_RESULT.md` gate ledger). **F6 does
not**: F6a and F6b both read **GATE REACHED** where the deviation was read before the token was
chosen — `DOCKET.md:748` (D383) names F6a's `+13.9%` reattachment row specifically and says
*"there is no miss large enough to have failed it."*

### 6.3 The FD-vs-adjoint acceptance criterion the lab actually uses

**`docs/charters/VERIFICATION_CHARTER.md` §7, heading at `:833`
(`## 7. FD tables are required for every adjoint`), rule at `:835-836`, criterion at `:838-850`.**
Verbatim:

> No gradient enters a record, a report or an optimisation without a finite-difference table
> beside it.
>
> **The grading standard, current and applied uniformly, including to cases graded under the old
> band:**
>
> - **PASS** at 5 percent or better on the aggregate **and** zero flagged components.
> - **CONDITIONAL** between 5 and 15 percent, and it requires a per-component breakdown before it
>   can be graded at all.
> - **FAIL** above 15 percent **or** on any sign-flipped or unstable component, regardless of the
>   aggregate.
>
> The earlier "1 to 12 percent is normal" band was inferred from a single rung and is **retired**.

**The five-step reporting protocol, `:852-864`, none optional:**

1. Confirm the step sits in the well-converged plateau with a two- or three-point mini-sweep.
   **Not assumed.**
2. Report per-component or cosine-similarity agreement alongside the aggregate percentage.
3. **Flag any component whose FD value changes sign, or moves by more than 50 percent of its own
   magnitude across one decade of step.**
4. *"The harness-sound **floor** on this stack, for a case with no flagged components, is 2.5 to 5
   percent vector-norm relative error. **A number below that is a claim about the harness.**"*
5. **Central differences, `step_calc=abs`, step between 1e-3 and 1e-2.**

**Step 4 is the clause most likely to be misread and it matters for Ladder B**: it is a *floor*,
not a target. Every S1 CBFS FD number — **0.085% / 0.059% / 0.199%** (W4), **0.032% / 0.115% /
0.009%** (re-inversion), **0.033% / 0.007% / 0.029%** (weighted arm), **0.0211%** (the sweep's
cell 6490) — sits **one to two orders below the stated harness floor**. The records explain why in
their own terms (`W4` §5d: *"the agreement is step-limited, not noise-limited, which is the
signature of a correct derivative measured against a resolvable objective"*), and the charter's
own number is calibrated on **shape** derivatives through IDWarp, not on a per-cell field DV with
no warp in the chain (`S1_FIML_FIELD_INVERSION.md` §1: `WARP PROBE: {"warper_init": 0,
"warper_jacvec": 0}`). **The two are not the same instrument, and a DAFoam charter should say so
rather than let §7 step 4 read as an accusation against the S1 numbers.**

**Number of components is NOT fixed by the charter.** §7 quotes A5's 27 components as an instance.
Sign agreement **is** load-bearing: `sign match` is a required column (`:876`) and one sign-flipped
component is a FAIL regardless of aggregate. The family's own protocol adds the operational half
(`FAMILY_SUPERVISION_GUIDELINES.md` §4.2-4.3): `check_totals`, step **1e-3**, central,
`step_calc="abs"`, error convention **‖Jan−Jfd‖/‖Jfd‖ as printed**, one convention throughout, plus
a step-check when the FD magnitude differs from the analytic np=1-class value by **>20%**.

**Closing caution, `:891-897`:** *"**Do not prescribe 'converge harder' before checking whether
convergence is available.**"* — iterations 1000→10000 produced bit-identical residuals and moved
the FD aggregate from **46.64% to 46.21%**.

### 6.4 The "Charter 2c trivial baseline" rule

**`docs/charters/VERIFICATION_CHARTER.md` §2c, heading at `:1726`:**
`## 2c. The discrimination test: a row that grades a hypothesis separates it from that hypothesis being absent (added 2026-08-18)`

**The rule, `:1735-1741`, verbatim:**

> **A gate row whose verdict is counted as evidence about a hypothesis is DISCRIMINATING or it is
> not evidence. A row that returns the same verdict for the hypothesis and for a registered
> trivial baseline of that hypothesis may be reported. It may not be counted toward the
> hypothesis's verdict.**
>
> **The rule reaches GRADE rows only. A GUARD row is exempt, and the exemption holds only while
> the row is counted toward no verdict.**

**Relation to 2a, `:1743-1748`:** *"2a catches a row whose value is fixed by ALGEBRA … 2c catches
a row whose value is fixed by nothing THE HYPOTHESIS CONTROLS: geometry, mesh, boundary
conditions, anything but the thing under test. Both are rows that cannot come out differently.
Both read exactly like a row that passed on merit."*

**The incident that earned it, `:1750-1756`:** the K0cS square-cavity rung ran a registered
RECOGNITION control C1 with the turbulence model switched off. *"**C1 passed four rows. kOmegaSST
passed two. The set of rows kOmegaSST passed that no turbulence model at all did not pass was
EMPTY.**"* On one row the closure and its absence sat **0.0055%** of the reference apart. Docket
**D411**.

**The GRADE-vs-GUARD table, `:1764-1770`,** is the load-bearing half; the creation-time question,
`:1772-1773`: *"if this row fails, what is withdrawn — the hypothesis, or the run?"*

**Reach limit 3, `:1799-1804`, the clause a DAFoam charter must instantiate:** *"**What counts as
the trivial baseline is a judgement, not a datum.** For a turbulence closure it is the model
switched off; for a correction, the uncorrected run; for a mesh claim, the coarser mesh. **The null
arm is registered before its own run … and a null chosen after the numbers were read makes the
instrument the thing it exists to detect.**"* Enforcement:
`scripts/check_row_discrimination.py`, rules `D1-HOLLOW-PASS`, `D2-INERT-ROW`, `D3-GUARD-GRADED`.

**The closure lane instantiated it** (`CLOSURE_MODELLING_CHARTER.md:111-114`): *"**The train-mean
tensor is that registered trivial baseline for anisotropy**, and this clause fixes it by name so no
future preregistration has to re-derive which baseline is trivial."*

**Ladder B's records already contain the exact shape 2c forbids, and already caught it themselves
— which is the strongest argument for naming a DAFoam trivial baseline explicitly.**
`S1_SENSITIVITY_VS_ERROR.md` §3 measures **G2 scored on the baseline gradient alone — an array
with no inversion result in it — at 35.38%**, against the inversion's achieved 26.86%. That is a
GRADE row whose value is fixed by something the hypothesis does not control. The record's own
conclusion is 2c stated in the lane's terms: *"G2 as currently defined is therefore scoring the
adjoint's sensitivity map, not the closure's error location."* **The registered trivial baseline
for a DAFoam field-inversion gate is `|g(β=1)|` scored under the same rule, and it should be named
in the charter rather than rediscovered.**

### 6.5 The closure team's docs/cases layout — two premises refuted by `ls`

| assumed | actual |
|---|---|
| `cases/closure/<ladder>/<case>/` | **`cases/closure/` does not exist.** The path is **`cases/RANS_LES_closure_models/`**, named at `CLOSURE_MODELLING_CHARTER.md:7` |
| `<ladder>/<case>/` — two levels | **One level.** `cases/RANS_LES_closure_models/<Author><Year>_<Method>/` — `Kaandorp2020_TBRF`, `Ling2016_TBNN`, `Schmelzer2020_SpaRTA`, `Wu2018_PIML_RF`, plus a sibling **`_common/`** holding `BASELINES.md`, `FEASIBILITY.md`, the scorer and the dataset builders |
| `PREREGISTRATION.md` + `RESULTS.md` | **CONFIRMED, 4 of 4 case directories, exact filenames** — and these eight files are the only `PREREGISTRATION.md`/`RESULTS.md` pair-files anywhere under `cases/` |
| `docs/closure/*` as a themed tree | **CONFIRMED but flat** — five files, no subdirectories: `README.md`, `CLOSURE_LINE_RESTART_DOCTRINE.md`, `CLOSURE_METHOD_CLASSES_INVENTORY.md`, `FOUNDATIONAL_MODELS_INVENTORY.md`, `PAPER_CATALOGUE.md` |

**A third per-case record type is in use and is worth adopting:**
`Kaandorp2020_TBRF/INCIDENT_<topic>_<YYYY-MM-DD>.md`, the form mandated by
`CLOSURE_MODELLING_CHARTER.md` §14 for shared-directory write collisions. `cases/dafoam` has the
same hazard and no such form — `f6d_random_matrix_uq/f6d_option_a/d0.2_s000/PROVENANCE_7500_CONTAMINATED.md`
is an incident record under a different name.

**Naming divergence a DAFoam README must decide, not inherit:** the closure tree uses
**`RESULTS.md` plural** in per-case directories; `cases/dafoam` uses **`_RESULT.md` singular** in
flat prefixed filenames (`A3_SUBLU_RESULT.md`, `S1_CBFS_INVERSION_RESULT.md`). The DAFoam form is
what `FILING_CHARTER.md` **R7** actually mandates — *"Campaign records are `<RUNG>_<PURPOSE>.md`"*
— so the existing tree is compliant and the closure tree is the departure. **Do not "fix" one to
match the other without a ruling.**

### 6.6 The skeleton `docs/dafoam/README.md` must mirror

Section order of `docs/closure/README.md`:

| line | heading |
|---|---|
| `:1` | `# Closure modelling — start here` |
| `:14` | `## 1. What exists, and where` |
| `:33` | `## 2. Reading order for a new team member` |
| `:52` | `## 3. Scoreboard — the four reproductions` |
| `:74` | `## 4. The standing rules, in one screen` |
| `:101` | `## 5. PENDING-MIT — 16 titles needing institutional access` |

Header, `:1-11`, verbatim — note the map-not-report disclaimer, the date, and the charter pointer
with its bright line quoted:

> # Closure modelling — start here
>
> The lane's map. **This is a map, not a report**: every number below is a pointer to the record
> that owns it. Dated 2026-08-20.
>
> **The standing rules are `docs/charters/CLOSURE_MODELLING_CHARTER.md`.** Read it before writing
> code or a preregistration. Its line:
>
> > **A closure is not a result until it has been re-solved, and a score against a baseline a
> > constant can beat is not an evaluation.**

Three conventions inside it that a DAFoam README owes directly:

1. **§1's table** is `| Document | What it is | Size |`, and it ends with a **data-lives-outside-
   the-repo** note naming the benchmark clone and its commit (`deb91557184af3cb95f5190494ec52d8f2c6a0d1`).
   The DAFoam analogue is `/home/ubuntu/certonomous-runs/` and the same benchmark clone.
2. **§3's cross-tree pointer paragraph** (`:61-65`), required by charter §13: *"The SpaRTA line
   lives in `verification/campaign/`: …"* — **the direct analogue of what a DAFoam README owes
   toward `verification/campaign/` for the entire F6 series**, which is 88% of `cases/dafoam` by
   size and has no `.md` record in the tree.
3. **§3's integrity-flag paragraph** (`:67-70`): *"Two integrity flags on the records above, both
   scheduled for correction, **neither quoted from**"*. A DAFoam README's equivalents are named in
   §4.2 and §5 above.

### 6.7 Filing and compute rules that bind new DAFoam work

**`FILING_CHARTER.md`** (106 lines, adopted 2026-08-18, **no version line**). The binding artifact
is `scripts/check_filing.py`, not the page (`:12-15`): *"Where the two disagree, that is a defect
in one of them and a docket item, not a matter of interpretation."* Rules R0–R3, R5–R8 (**no R4**;
**R9 exists only in the script**, `check_filing.py:248-272`, `R9-SIDECAR-MISSING`). The one that
governs DAFoam records is **R7**: *"Campaign records are `<RUNG>_<PURPOSE>.md`; helper code inside
a campaign directory is `lower_snake.py`."* §5 (`:76-90`) is the operative instruction for this
lane: *"Before writing any durable file, find the nearest existing sibling and copy its pattern"*,
then run `python3 scripts/check_filing.py` and `--selftest`.

**`FILING_CHARTER.md` says nothing about INDEX files, frozen records, or who may edit what.**
Grepped for `index`, `INDEX`, `frozen`, `freeze`, `append-only`, `immutable`: **zero hits.** It
covers paths and names only. Freezing lives in `CLOSURE_MODELLING_CHARTER.md` §11 (*"the
preregistration itself is never edited after the run"*) and `VERIFICATION_CHARTER.md` §2b
(`:165`: *"**Originals are always retained and struck, never rewritten**"*). Edit rights are
scattered: `CLOSURE_MODELLING_CHARTER.md:573-575` (*"A sub-agent never appends to either live
file"*), §14 on shared-directory writes, `SUPERVISION_CHARTER.md:106-109`,
`ESCALATION_CHARTER.md:128-132` and `:143-173` (*"1. **Never `git reset --hard`, `git stash`,
`git checkout --` or `git clean`.**"*, *"4. **An unexpected uncommitted change is inspected, never
reverted.**"*). **If DAFoam needs an INDEX convention or a record-freezing rule, it is new work,
not a citation** — `cases/dafoam/INDEX.md` is written as a map under R7 and claims no rule.

**`COMPUTE_BUDGET_CHARTER.md`** (Version 1.3, dated 2026-08-17). The line (`:19`):
*"**Every budget is measured, and every hold on the box expires by itself.**"* Unit: **core-minutes**
(`:28-30`) — note the closure charter states its authorisation in **core-hours** (487 = 29,220
core-min), so a DAFoam charter must state which. Key clauses for this lane:

- **Cost honesty** (`:36-40`): *"**No cost is ever presented as measured unless a record backs
  it.**"* And `:58-65`: *"**A cost basis may not cite a run the lab has since superseded,
  withdrawn or graded out of band.**"*
- **Gross vs cleaned** (`:89-110`): a spend figure states which it is and names the cleaning rule
  (*"a ledger row over 3600 wall seconds is an infrastructure stall, not solver cost"*). Waste
  stays **inside both figures** and is reported by the waste split.
- **Per-rung defaults** (`:130-141`): new capability 60, written report 20, **one ladder rung 20**,
  benchmark-resource bump 30 — *"apply only when nothing measured is available"*.
- **The iteration-count rule** (`:143-175`), the one that matters most for an adjoint ladder:
  *"**A rung estimate states the iteration count it assumes, and the evidence for it.** … settling
  is the half that overruns."* Measured: **32 of 37 rung-shaped compute proposals name no iteration
  count**, 26 unstarted, largest 400 core-min.
- **Session budgets are three numbers** (`:177-181`): core-minutes, cores, memory —
  *"container-enforced … with explicit `--cpus` and `--memory` caps"*. Every S1 record complies.
- **Overrun** (`:197-200`): *"**A budget overrun stops the run. It does not get a new budget.**"*
  The weighted arm's eval-8 completion is the worked example of the correct route: a **dated budget
  amendment with chief approval (`d66f82a5`)**, not a silent extension.
- **Approval bands are NOT in this charter** — §5 is explicitly blocked (`:276-278`,
  *"**PROPOSAL, and currently blocked.** There is no spot policy … Writing one here would be
  inventing policy"*). They live in `ESCALATION_CHARTER.md` §4 (`:190-195`), themselves marked
  **PROPOSAL, unratified**: **Free ≤60 core-min; Notify 60–240; Ask >240; Ask >480 aggregated per
  night.** Two riding rules: *"the threshold is on the estimate, and an estimate that was wrong
  crosses it too"*, and *"the aggregate band is per night, not per agent"*. Plus
  `ESCALATION_CHARTER.md:243-253`: *"A pre-registered cap she has approved in an item, like the
  600, overrides these by exactly its own amount and nothing more."*
- **Pre-registration before compute is NOT in the compute charter** — the word does not appear. It
  is `SUPERVISION_CHARTER.md:99-104` §3 check 4: *"**No family compute launches without its
  pre-registration committed.** … the reason scientific loss was zero every time was that the
  pre-registrations were committed before the compute was. The family supervisor checks the commit
  exists, not that somebody meant to write one."*
- **Auto-stop** (`:202-272`): root cron every five minutes, 30-minute idle timeout; the busy-test
  `pgrep -f` pattern **includes `dafoam`** (`:214-216`), so *"a long solve is safe by
  construction"*. Prohibitions at `:250-256` — never disable or lengthen the timer, never start an
  unbounded hold, never leave a hold running.

---

## 7. Open items, prioritised

Priced where the records price them. **Nothing here is authorised and nothing was run.**

### Tier 0 — zero compute, and each removes a live defect

| # | item | why now | citation |
|---|---|---|---|
| **0.1** | **Write `docs/dafoam/README.md`** mirroring `docs/closure/README.md` §§1–5, and make its §3 carry the cross-tree pointer to `verification/campaign/` for the whole F6 series | 88% of `cases/dafoam` by size (6.0 GB) has **no record inside the tree**; a reader looking only here concludes F6a-band and F6d have none | §2, `cases/dafoam/INDEX.md` §3; charter §13 requires the pointer |
| **0.2** | **Fix the one broken citation inside a Ladder B record**: `S1_FIML_FIELD_INVERSION.md:229` cites `scripts/analyze_fd.py`, actually at `S1_work/scripts/analyze_fd.py` | It is a live `lab_check.py` FAIL (1 of 1112) and a one-line edit — but it is a **frozen record**, so the correction is the owner's and goes in as a dated note, not a silent rewrite | `DOCKET.md:449` (D80) |
| **0.3** | **Write the `rans_model_comparison` record.** Five models, one JSON, no `.md`, no docket row, no lesson | LienCubicKE recovers **7.85% of the DNS secondary flow** where four linear models recover ~0% (1e-16 to 1e-15 of U_bulk) — the cleanest in-lab evidence that F6c's deficit is the Boussinesq hypothesis itself | §2; `rans_model_comparison/sweep_results.json` |
| **0.4** | **Settle the F6a/F6b `GATE REACHED` tokens** against D383 | Two rows in this tree assert `GATE REACHED` after the deviation was read; F6a's is carried onward to the nine-act table as `VALIDATED`. The **numbers are honest**; the **token** is not earned | `DOCKET.md:748` (D383); §2 |
| **0.5** | **Decide the DAFoam verdict vocabulary explicitly** — six tokens (closure charter) or five (verification/reporting charters) — and name the **registered trivial baseline** for a field-inversion gate under Charter 2c | `PENDING` is defined in exactly one charter and used 36 times in DOCKET with no definition elsewhere; and `S1_SENSITIVITY_VS_ERROR.md` §3 already demonstrates a 2c-failing GRADE row (G2 = 35.38% on the baseline gradient alone) | §6.2, §6.4 |
| **0.6** | **Z-1: the free first-Hv correctness control.** Whichever Hv machinery S1-priors builds, its first product along `s = β₁₀ − β₁` must reproduce `sᵀy_QoI = +7.313133e-01` | *"Costs nothing and strictly dominates"* the planned symmetry check, which passes for a consistently-wrong operator | `S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md` §3 |

### Tier 1 — cheap compute, high discrimination

| # | item | price | discriminating outcome | citation |
|---|---|---|---|---|
| **1.1** | **M-A / R2: the `-ksp_view` two-arm.** Does DAFoam's `printInfo` echo the ordering that actually ran? | **8 core-min** | Same ordering in both PETSc dumps → the `rcm` lever is **DEAD** and **257 archived runs' `rcm` citations are void**, including every ordering claim in the B3/CBFS record and PROOF §25.2; they differ → the lever is **ACTIVE** and those 257 runs inherit a proven lever; neither dump carries an ordering line → **NO VERDICT**, itself a statement about the build | `DOCKET.md:135` (D10); ranked **#1** independently by `S1_ZEROCOMPUTE_TRIAGE` §3 |
| **1.2** | **M2 — the hump env-off negative control**, never run: A6's exact configuration with `DAFOAM_SUBPC_TYPE` unset, same image, cold case dir | **15 core-min** | Makes the `-9` → sub-LU attribution reproducible **on the hump** instead of inherited from CBFS. *"The programme has an env-off control on CBFS and **none** on the hump"* | `W4_ADJOINT_PC_UNBLOCK.md` §5b.1 |
| **1.3** | **M1 — dump the hump's `dRdWTPC` and RHS and run the existing offline `pc_ladder.py` harness on them** | **25 core-min**, then <1 each per offline variant | *"Decides **singular vs ill-conditioned vs merely slow** offline, without a single long solve. This is the measurement whose absence makes the boundary an assumption."* **If M1 returns a singular or catastrophically ill-conditioned assembled operator, M4 and M5 should not be bought at all** | ibid. |

**M1 + M2 together are 40 core-min and are the sequencing the record itself recommends**:
*"40 core-min buys the singular-or-not answer offline plus the negative control the programme never
ran."*

### Tier 2 — the real Ladder B frontier

| # | item | price | note | citation |
|---|---|---|---|---|
| **2.1** | **M3 — a deliberate reproduction of any hump adjoint attempt.** *"11 attempts, 0 reproduced."* Gate: residual reproduces to 13 digits at iterations 0/300/600/900 | **55 core-min** | Buy only after M1 | `W4` §5b.1; `WARMSTART_AUDIT.md` row 4's 2026-08-11 note |
| **2.2** | **M4 — run the hump to a `KSPConvergedReason`.** Converts *"no convergence observed in 900 iterations"* into a measured rate | **100 core-min**, and **≥64 GB of host**, *"or it does not produce the measurement it is bought for"* | The 30.5 GB box this ran on went to 1.62 GB by iteration 900 with the basis still filling | ibid. |
| **2.3** | **`w3-beta-on-omega-destruction-model-patch`** — beta on the omega **destruction** term, requiring a model patch and a rebuild | **UNPRICED** | *"The **only** route to an external referent for the S1 line."* It is the term Wu/Zhang actually invert; until it exists, **no S1 number can be set beside theirs** (C2, R6) | `S1_ZEROCOMPUTE_TRIAGE` §1b; `S1_FIML_FIELD_INVERSION.md` headline 3 |
| **2.4** | **PR-1, respecified** — a second sensitivity map against a **structurally different quantity** (a force, integrated wall shear over the step face, a reattachment location), **not** another velocity-variance functional | **~25 core-min** | *"An experiment whose every outcome leaves belief unmoved should not be run, and PR-1 as filed is now in that condition."* The support-change version is answered from disk at Spearman **+0.9894**; the quantity-change version is not | `S1_ZEROCOMPUTE_TRIAGE` §3 rank 4 |
| **2.5** | **B3 Stage 4 under the shipped toolchain** — the field inversion Ladder B exists for | not priced | Blocked by construction until the sub-LU fix ships upstream or Katie adopts a forked toolchain (**R11 point 4 — Katie's call, not a session's**) | `FAMILY_SUPERVISION_GUIDELINES.md` §3.4 |
| **2.6** | **The duct streamwise-profile deficit** — *"≥76% of the duct error; the largest open closure item"* | **UNPRICED**, needs a solving budget | And `AR_14_Ret_180`, the third scored duct case, has **never been reproduced** by this campaign | `S1_ZEROCOMPUTE_TRIAGE` §1b; `f6c_duct_dns/F6c_duct_vs_dns.md:99-104` |

### Tier 3 — do not buy, and the records say why

| item | price | why not |
|---|---|---|
| **R5, the whitened re-inversion** | 340 core-min | Enabling premise measured **false**: high-sensitivity cells are enriched **inside** the window by **×4.19**, the largest enrichment of any region, so whitening moves G2 **down** from 26.86%, not up. And no loss-following correction can clear >50% at all — the loss's own top-decile ceiling is **32.71%** (`S1_SENSITIVITY_VS_ERROR.md` §6; `DOCKET.md:238` D45) |
| **R8, the physics-informed transferable prior** | unpriced | Condition (a) measured absent; its proposed shape (*"β departs from 1 in the separated shear layer and nowhere else"*) is contradicted by both the correction (26.9% in-window, 39.6% upstream) and the sensitivity (35.4% / 45.8%) |
| **`s1-cbfs-w1-only-arm`** | 150 core-min | **KILL RATIFIED** (`DOCKET.md:634`, D269) on D213's deliverable-level ground: G2 invalidated **six independent ways** |
| **An A6 adjoint attempt** | 760–1,520 core-min | *"must NOT be proposed"* to settle the memory-vs-conditioning question — a zero-cost analysis decides it (`DOCKET.md:276`, D204) |
| **S1-priors as currently gated** | 260 core-min | **HOLD** until G-P4b is adopted and G-P2 re-derived. Two of its four gates *"cannot presently fail or rest on the wrong comparison"*, and the proposal JSON an agent would dispatch from carried the **withdrawn** G-P4 (D41, D67, D69, D75, D76) |

### 7.1 Two standing obligations any new DAFoam run inherits

1. **Assert the sub-LU Info line in-log before trusting any sub-LU result.** `strcmp(subPCTypeEnv,
   "lu")` is an exact match: `LU`, `Lu`, `lu ` (trailing space) or `superlu` all **silently run
   stock ILU with no message**, and *"a run believed patched can be stock."* The warn was added to
   the **patch text** on 2026-08-07 but the deployed `dafoam-subpclu:v1` image was **not rebuilt**
   (`SUPERVISOR_FAMILY_REVIEW_2026-08-07.md` B-1, outcome block).
2. **Prove the cold start in the log.** pyDAFoam writes the primal end state back into the time-0
   directory at run end, so the second run of any case dir silently warm-starts. Use the
   **staged-copy pattern** (one fresh case subdir per arm), or restore from the pristine serial
   `0/` and check the first `Time step continuity errors` value against the case's known
   cold-from-uniform signature (`FAMILY_SUPERVISION_GUIDELINES.md` §8; `WARMSTART_AUDIT.md`).

---

*Nothing in this document was sent, filed, uploaded or registered. No solver ran, no container was
started, no `git` operation was performed, and no existing record was edited. The only files this
lane created are this one and `cases/dafoam/INDEX.md`.*

