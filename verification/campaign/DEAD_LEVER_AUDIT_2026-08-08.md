# Dead-lever audit — 2026-08-08 (Katie's AUDIT ORDER 1, L-40 / Verification Charter v1.5 §9)

Executed by the dead-lever auditor under the rule THE SWITCH YOU SET IS NOT THE
SWITCH THAT RAN (`LESSONS.md` L-40; charter §9 `levers_verified_active`): a
solver option cited by a conclusion's reasoning is evidence only when the
archived RUNTIME LOG proves it was active — presence in an input dictionary
proves nothing. Zero solver core-min; read-only on all existing records; this
file is the audit's only write.

**Method.** Every conclusion-bearing record under `demo-output/website/`
(campaign/, dafoam/, and the family status files `ACTIVE_RESEARCH.md`,
`CLOSURE_CHALLENGE_STATUS.md`, `OTHER_WORK_STATUS.md`) was swept for sentences
whose conclusion leans on a named option — preconditioners, turbulence-model
switches, scheme selections, MRF settings, adjoint modes, limiter settings,
initialization choices, env-var levers. Each cited lever was then hunted in the
archived runtime logs (selection banners, printCoeffs, `Exec :` lines, DAFoam
daOptions echoes, DALinearEqn printInfo blocks, PETSc PCView output, MRF zone
reports) and classified three ways. Verification was fanned out over five
parallel batch agents plus inline work by the auditor; **the F-family batch
agent died mid-report (the standing lesson: forks die with the agent) — its
completed findings were recovered from its transcript and five of its quoted
evidence lines were re-confirmed inline byte-for-byte before use (F2, F3
wedge, D5 SSG registry + donor-trap, F6a a1 banners). That section is marked
[recovered + spot-checked] below.**

Prior activity proof cited per the order rather than redone:
`QCR_ACTIVITY_CHECK_2026-08-08.md` (1a14e90b) for the hump/hills/duct QCR legs.

---

## Summary counts

| classification | as counted per batch | distinct after cross-batch merge |
| --- | --- | --- |
| VERIFIED (log line quoted) | 20 + 21 + 43 + 26 + 15 groups + 1 (family-N a0 arms, auditor-inline) = **126 lever/conclusion pairs (~180 individual log lines)** | ~125 (sub-LU unblock rows and hump QCR rows each appear in two batch tables) |
| UNVERIFIABLE-FROM-LOGS | 6 + 2 + 2 + 5 + 3 + 1 = **19** | **16** (the three SIMPLEC-attribution entries — Ahmed baseline, ACTIVE_RESEARCH narrative, hump/BFS setup mentions — merge into one structural finding) |
| FOUND-DEAD | **4** | **4** — 1 conclusion-reopening (the A3 specimen, already reopened) + 3 previously-caught-and-integrated |

**Headline: no NEW conclusion-reopening dead lever was found anywhere in the
archive. The A3 transonicPCOption specimen remains the only lever that was
silently off while a conclusion implied it had been tried.** Its blast radius
is now fully mapped (below). The audit's second-order product is a list of 16
levers whose activity the archived logs cannot prove either way — per charter
§9 these must ship as unverifiable-from-logs on the conclusions' faces.

---

## FOUND-DEAD list, ranked by how much each reopening matters

1. **`transonicPCOption: 2` — dead code for `DARhoSimpleCFoam`** (only `== 1`
   exists, `DAResidualRhoSimpleCFoam.C:173`; `== 2` lives only in
   `DAResidualTurboFoam.C:176`). **Status: found-dead / ALREADY REOPENED** (the
   motivating specimen, `A3_SUBLU_RESULT.md` + `A3_SUBLU_SWEEP_PREREGISTRATION.md`
   §2–3; not redone here). **Blast radius mapped by this audit:** the dead value
   `transonicPCOption 2;` is echoed in EVERY archived M6 adjoint log —
   `dafoam/ladder-a/logs_A3/check_totals_coarse_run3_pcFillLevel0.log:485`, the
   July-28 mitigation runs, all seven R5 conditioning-campaign logs
   (`r5_*…log:489`), `W4-m6-reordering/m6_{natural,rcm}.log:489`, the D3
   envelope baseline (`run_opt5_onera_n15_21840.log:410`) — so every archived
   M6 `-5` was measured with the transonic PC silently OFF. None of those
   records *claims* the transonic PC was tried, so no additional verdict flips,
   but per the sweep prereg's own §3 mandate, `R5_ADJOINT_CONDITIONING.md`,
   `ADJOINT_MEMORY_ENVELOPE.md`, and `PROOF.md` §25.2 should carry the
   retroactive annotation (chief's reopen process — not written by this audit).
   Latent: `A6_crm_wingbody`'s script echoes the same dead value
   (`logs_A6/run_model_accepted_t0_to_t1000.log:487`) — harmless until an A6
   adjoint is ever attempted; the attempt-2/-3 sub-LU sweep logs prove the live
   value `transonicPCOption 1;` plus the sub-LU banner
   (`sublu_tpc1_computetotals_attempt2.log:410,861`).
2. **`consistent yes` (SIMPLEC) — dead for `DASimpleFoam`**, which silently
   runs plain SIMPLE. Previously caught and *integrated into* the A4 Ahmed
   conclusion (the deadness IS the cross-code-gap explanation;
   `ladder-a/A4_ahmed_body.md` §2a, `ACTIVE_RESEARCH.md`). No reopening — but
   the attribution's OTHER half (that the OpenFOAM baseline really ran SIMPLEC)
   is unverifiable-from-logs (entry 2 in the list below) and the record should
   say so on its face.
3. **Editing `system/decomposeParDict` is a silent no-op** — pyDAFoam
   regenerates it (`PROOF.md` §25.5). Previously caught live by reading the
   log's own `Decomposition method` line back; now standing practice. No
   conclusion was ever shipped on the dead edit.
4. **`DAFOAM_SUBPC_TYPE` silent fallthrough** — any value other than exact
   `"lu"` falls back to stock ILU with no log tell in the deployed v1 image
   (patch header's own B-1 note). Hazard class, not a shipped defect: every
   conclusion-bearing sub-LU run in the archive has the activity banner
   present, plus a negative control proving the off-state
   (`W4-adjoint-pc-unblock/cbfs_regress_computetotals.log`: no banner, reason
   −9). The banner-assert discipline must stay mandatory.

---

## UNVERIFIABLE-FROM-LOGS register (charter §9: these caveats belong on the conclusions' faces)

Ranked by load-bearing weight:

1. **F5c SIMPLEC attribution** (`F5bc_unsteady_statistics.md` incl. the
   2026-08-08 amendment's corrected −10.5% headline "the SIMPLEC coarse
   case") — the six original diagnostic runs' logs are not archived
   (`F5c_runs/` holds only `sign_convention_control`; the extended run's case
   lived in a deleted scratchpad, see
   `solve_registry/f5c_extended_simplec20k_20260730T042423Z.log:10` case path)
   AND simpleFoam prints identical `SIMPLE:` banners with or without
   `consistent yes` — no surviving or possible log line distinguishes them.
   Freshly load-bearing; highest priority for a face caveat.
2. **Ahmed A4 baseline-SIMPLEC half of the cross-code attribution**
   (`ladder-a/A4_ahmed_body.md` §2a, `AHMED_BODY_RECONCILIATION.md`,
   `ACTIVE_RESEARCH.md` bistable-wake section) — configured at
   `mission-output/{ahmed-body/act7-ahmed_25,geometry-study/study-ahmed_25}/case/system/fvSolution:21`;
   structurally no runtime tell exists.
3. **TMR NACA 0012 scheme-substitution root cause**
   (`W1_TMR_NACA0012_DISPOSITION.md`) — OpenFOAM never echoes `fvSchemes`;
   archived rungs keep at most one log and no `system/fvSchemes`. The
   *dismissal* survives on log-backed pricing/non-convergence; only the
   root-cause narrative needs the caveat.
4. **A3 Stage-2 shock-scheme claim** (`ladder-a/A3_onera_m6.md`,
   `Gauss linearUpwindV`/`limitedLinear`) — same structural fvSchemes gap.
5. **R5 `useMGSO` arm** (`R5_ADJOINT_CONDITIONING.md` §2) — only the
   parsed-dict echo exists (`r5_noresnorm_mgso…log:536`); the DALinearEqn
   printInfo block prints no orthogonalization line, and identical residual
   histories are equally consistent with an inactive switch — exactly the
   transonicPCOption ambiguity. Would prove it: KSPView showing the GS type,
   or a source read of `DALinearEqn.C`'s useMGSO handling (in-container only).
6. **R5 §1 source claims** (PC family hard-coded PCASM/PCILU, matrix-free
   operator) — in-container source reads, not locally re-readable;
   corroborated by `LIAISON_RESEARCH_adjoint_conditioning.md`'s sha-pinned
   upstream fetches.
7. **`ADJOINT_MEMORY_ENVELOPE.md` Opt 1** (`adjUseColoring=False` crash) —
   solver logs died with the session scratchpad; only 2-line collector stubs
   survive (exit/wall/RSS match the record digit-for-digit). Independent
   surviving proof of the lever class on A4:
   `W4-a4-discriminators/d_np4scotch_nocolor.log:483` `adjUseColoring 0;`.
8. **`ADJOINT_MEMORY_ENVELOPE.md` Opt 2** (sparsify levers) — same scratchpad
   loss; RSS numbers corroborated by stubs, option echoes gone.
9. **W4-a4-stepsweep patched-IDWarp provenance** — no `IDWARP_IMPORTED_FROM`
   stamp in those logs (the sweep's own W-2 finding); mitigated by the stamped
   bit-identical re-run `VERIFY-a4-np2-20260804` and stamped
   `W5-regrade/a4_patched_checktotals.log`.
10. **W4-idx16 patched-IDWarp provenance** — driver-only; mitigated by the
    probes' analytic −5.04787848 matching the stamped
    `W5-regrade/a5pl_patched_checktotals.log` value, not the stock −3.77.
11. **S1_FIML E1 kOmega leg** — only `s1_e1_kw.json` survives, no selection
    banner anywhere; non-load-bearing (the record's own words: "E2 is the case
    that matters"). (Second ladder-b/S1 batch gap: the 1000×
    primal-tightening arm survives only as a runtime json summary.)
12. **F4 SWBLI diagnostic arms** (`warmup20_bounded{,_realtime,_farfield}`) —
    no logs archived; conclusions ("LTS artifact confirmed", farfield
    eliminated) rest on unarchived foreground output. Low stakes (case sits in
    `NOT_PASSING_REGISTER.md` as a documented failure).
13. **F5b pitching-airfoil feasibility** — no surviving log for the
    potentialFoam-init fix or the moving-mesh solve; record explicitly
    incomplete, no shipped conclusion.
14. **F3/F4 "inviscid (μ=0)"** — laminar *selection* is log-proven; the μ=0
    value is dictionary-only (rhoCentralFoam never echoes μ). Sub-1% agreement
    with inviscid theory corroborates but is the conclusion itself.
15. **F8 omega magnitude/sign (±7.5398)** — MRF-zone activity is log-proven;
    the omega value is never echoed; the flip arm is distinguishable only by
    its force outcome.
16. **QCR hills SST control leg's missing case-dir log** — CLOSED during this
    audit: the genuine log was located at
    `solve_registry/f6b2_medium_20260805T171046Z.log:50` (Case header names
    `campaign/F6b_runs/medium`); the QCR check's "(2026-08-05 gate record)"
    citation now has a line.

**Structural lesson for the chief (charter material):** four whole lever
classes have NO possible activity echo in stock OpenFOAM logs — fvSchemes
tokens, fvSolution `consistent`, boundary-condition types, and dictionary
values like μ or MRF omega. Every future conclusion on such a lever is
unverifiable-from-logs at birth unless the driver cats the dictionary into the
log or the code prints a banner. The sub-LU patch (self-printing banner +
negative control) is the model; a one-line driver step (`cat fvSchemes` into
the log) would close the largest class.

---

## Full classification table

Legend: V = VERIFIED (log line proves activity), U = UNVERIFIABLE-FROM-LOGS,
FD = FOUND-DEAD. Paths under `/home/ubuntu/Certonomous/demo-output/website/`
unless absolute; run paths under `/home/ubuntu/certonomous-runs/` where noted.
Line numbers for `.gz` logs are decompressed line numbers.

### 1. Motivating specimen (already recorded — included per the order)

| record | conclusion | lever | class | evidence |
| --- | --- | --- | --- | --- |
| `dafoam/A3_SUBLU_RESULT.md` (+ every archived M6 record it annotates) | every archived M6 conditioning-wall `-5` was measured with the transonic PC off | `transonicPCOption: 2` | **FD / already-reopened** | dead code: `DAResidualRhoSimpleCFoam.C:173` accepts only `== 1`; dead value echoed in all M6 adjoint logs (list in ranked item 1 above) |
| `dafoam/A3_SUBLU_RESULT.md` | vcoarse arm NOT EVALUABLE — neither lever ever exercised (mesh-gate abort at t=0) | `DAFOAM_SUBPC_TYPE=lu`, `transonicPCOption: 1` | V (of the *non*-run) | `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-vcoarse/sublu_tpc1_computetotals.log` tail = "Failed 5 mesh checks" abort; no KSP line exists; record claims nothing about either lever — L-40-clean |
| `dafoam/A3_SUBLU_SWEEP_PREREGISTRATION.md` §8–9 | attempt-2 activity proofs delivered before OOM | same two levers | V | `sublu_tpc1_computetotals_attempt2.log:861` "DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU", `:410` `transonicPCOption 1;` (attempt-3 log ends with no reason code — arm unresolved, flagged for the chief/solver agent, not an audit matter) |

### 2. DAFoam ladder-a / adjoint conditioning

| record | conclusion | lever | class | evidence |
| --- | --- | --- | --- | --- |
| `dafoam/ladder-a/A1_naca0012_incompressible.md` | 11.43% CD/shape is the unmodified tutorial (wall-function SA RANS) | SpalartAllmaras; `primalMinResTol 1e-8` | V | `dafoam/ladder-a/logs/compute_totals_run1.log:160` "Selecting RAS turbulence model SpalartAllmaras"; `:710` "Minimal residual 9.646409714038222e-09 satisfied the prescribed tolerance 1e-08" |
| `dafoam/PROOF.md` §11–12 | frozen wall-distance hypothesis refuted; lever active in every run | `forceMeshWaveFrozen` | V | daOptions dump `compute_totals_run1.log:433` `forceMeshWaveFrozen 1;` + measured always-frozen yWall behavior |
| `dafoam/ladder-a/A2_mach_tutorial_wing.md` | 28.3% partial drag reduction under IPOPT at matched CL | IPOPT optimizer | V | `/home/ubuntu/certonomous-runs/A2-mach-wing/opt_run_driver.log:1818` `pyOptSparse_IPOPT`; CD 0.02961963478 (`:1659`) → 2.1241776e-02 (`:22753`); SA banner `run_model_stdout.log:214` |
| `dafoam/DAFOAM_CASE_STATUS.md` §A2 regrade | published A2 numbers are the aero-only variant | aero-only vs aerostructural script | V | `A2-mach-wing/check_totals_run1.log` contains 0 `MELD`/`TacsDVComp` mentions |
| `dafoam/ladder-a/A3_onera_m6.md` §Stage 2 | shock smeared/aft by upwind-biased schemes | `Gauss linearUpwindV`, `limitedLinear 1.0` | **U** | no scheme echo exists in `logs_A3/run_model_run3.log` (structural; see register item 4) |
| same §Stage 3 | Krylov-size hypothesis disproven | `gmresRestart` 1000→200 | V | `logs_A3/check_totals_coarse_run2_gmresRestart200.log:938` "GMRES Restart: 200" (control run1: "1000") |
| same | ILU(0) moves failure to `-5` | `pcFillLevel` 1→0 | V | `logs_A3/check_totals_coarse_run3_pcFillLevel0.log:943` "ILU PC Fill Level: 0", `:951` reason −5 |
| `dafoam/R5_ADJOINT_CONDITIONING.md` §2 | `normalizeResiduals=None` converts denormal −5 to honest −3 | `normalizeResiduals` | V | `solve_registry/r5_measure_scaling…log:547` default 11-field list, reason −5; `r5_noresnorm…log:547` `normalizeResiduals 1 ( None );`, reason −3 `:963`; reproduced −3 in `cl_only`, `mgso`, `bigbudget` logs `:973` |
| `R5` §3 | fill=1 / Richardson collapse exactly at restart boundary | `pcFillLevel=1`; `globalPCIters/localPCIters=3` | V | DALinearEqn printInfo (runtime): `r5_noresnorm_fill1…log:946` "ILU PC Fill Level: 1", −5 at exactly 1000; `r5_noresnorm_richardson…log:943-944` "Global PC Iters: 3 / Local PC Iters: 3", −5@1000 |
| `R5` §3 | 2× budget doesn't help | `gmresMaxIters=2000` | V | `r5_noresnorm_bigbudget…log:947` "GMRES Max Iterations: 2000"; "Total iterations: 2000" `:973` |
| `R5` §2 | orthogonality loss ruled out | `useMGSO=1` | **U** | dict echo only (`:536`); printInfo has no orthogonalization line — configured-vs-active indistinguishable (register item 5) |
| `R5` §1/§5 | pmat scale-spread measurements | `PETSC_OPTIONS -ksp_view_pmat` | V | dumps exist: `A3-onera-m6-sweep-n15_21840/dump_pmat_n15.dat`, `dump_pmat_noresnorm_n15.dat` |
| `R5` §1 | PC family hard-coded; operator matrix-free | compiled-in PCASM/PCILU | **U** | source claim, in-container only (register item 6) |
| `dafoam/ADJOINT_MEMORY_ENVELOPE.md` Opt 1 | coloring-off ruled out (crash) | `adjUseColoring` | **U** | logs lost with scratchpad; collector stubs match record; surviving class-proof `W4-a4-discriminators/d_np4scotch_nocolor.log:483` `adjUseColoring 0;` (register item 7) |
| same Opt 2 | sparsify cuts RSS ~30%, doesn't fix −5 | `maxResConLv4JacPCMat=1`, `jacLowerBounds` | **U** | stubs corroborate RSS digit-for-digit; option echoes lost (register item 8) |
| same Opt 4/5 + headline | M6 family −5 at every size; sail converges; n8 primal never converges | per-case reason codes | V | `run_opt5_onera_n15_21840.log:935/951` −5; `…n28_42120.log:925/937` −5; `run_opt4_probe80k.log:937` KSP 1.482196937524e-322 + `:938/:950` −5 (false-success line as quoted); `run_opt5_sail_coarse_uncap.log:775/786` reason 2 |
| `PROOF.md` §25.2 / `DAFOAM_CASE_STATUS.md` | reordering is not the M6 blocker | `jacMatReOrdering` natural vs rcm | V | `W4-m6-reordering/m6_natural.log:945` "Mat ReOrdering: natural" −5; `m6_rcm.log:945` "rcm" −5 |
| `ladder-a/A4_ahmed_body.md` §2a | 22% cross-code gap = SIMPLE vs SIMPLEC on bistable wake — DAFoam half | `consistent yes` dead in DASimpleFoam | **FD (previously caught, integrated)** | ranked item 2 above |
| same — baseline half | baseline simpleFoam actually ran SIMPLEC | `consistent yes;` | **U** | register item 2 |
| `A4` / `PROOF.md` §25.5 / `DAFOAM_CASE_STATUS.md` §A4 | PASS verdict: 10.04% was a scotch artifact; np=1 stock = 1.10% | decomposition method | V | `W4-a4-stepsweep/a4_np1_stock.log:11506` rel err 1.1032e-02; `W4-a4-discriminators/d_np4scotch.log:48` "Decomposition method scotch [4]", `d_np4simple.log:48` "simple [4]" |
| `PROOF.md` §25.5 | decomposeParDict edit = silent no-op | decomposeParDict | **FD (previously caught)** | ranked item 3 above |
| `ladder-a/A5_ubend_internal.md` | adjoint-solve accuracy eliminated (7-orders tightening, flagged comps <1%) | `gmresRelTol` 1e-5→1e-12 | V | `dafoam/A5_work/UBend_Channel_pressureloss/tightadjoint_out.log:915` "GMRES Relative Tolerance: 1e-12", `:920-921` KSP 8.049e-12@126 reason 2; stock control `ladder-a/logs/A5_compute_totals_run1.log:950` 86 iters reason 2 |
| `A5` addendum 1b | residualControl+tightening active, plateau intrinsic | `residualControl` | V | `logs/A5_compute_totals_tightened_endtime1000_run2.log:187` "SIMPLE: convergence criteria" vs stock "no convergence criteria found" |
| `A5` addendum | dR/dW closed as units artifact | `normalizeStates` constants | V | `diagratio_out.log` in case dir; four exact constant clusters |
| `dafoam/VERIFICATION_A1_serial_limiter_supervisor_sweep.md` | `cellLimited…limited` breaks serial adjoint 92.8%; one-word cure 0.121% | limiter scheme | V (behavioral) | `W4-defect-robustness/a1lim_np1.log:2319` 9.284586e-01; byte-audit: fvSchemes is the only differing input, outcome moves 92.8%→0.121% |
| `dafoam/ladder-a/A6_crm_wingbody.md` | 0.0067% tutorial reproduction, unmodified daOptions | solver/model/tolerances | V | `logs_A6/run_model_accepted_t0_to_t1000.log:213` SA banner (note: `:487` echoes the dead `transonicPCOption 2;` — latent only, no adjoint ever ran) |

### 3. DAFoam decomposition-defect / W4 / W5

| record | conclusion | lever | class | evidence |
| --- | --- | --- | --- | --- |
| `dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md` | CBFS adjoint converges under sub-LU (reason 2, 667 its) | `DAFOAM_SUBPC_TYPE=lu` | V | `/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/cbfs_sublu_computetotals.log:12049` "DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU"; `:12069` "Total iterations: 667. PetscConvergedReason: 2" |
| same | beta-field gate gradient exists under sub-LU | same | V | `cbfs_beta_computetotals.log:12047` banner, `:12067` reason 2/667, `:12074` "GRAD n=21000 norm=1.4558046603e-05" |
| same | regression control: env unset reproduces −9 | env-off control | V (negative control) | `cbfs_regress_computetotals.log:12062` reason −9; no banner anywhere in file |
| same | hump −9 becomes descending residual under sub-LU | same | V | `hump_sublu_computetotals.log:2256` banner; iter-0 1.094138 → iter-900 0.954447 (`:2268/:2279`) |
| same | B3-exact config carried | `jacMatReOrdering rcm`, `pcFillLevel 1` | V | `cbfs_sublu_computetotals.log:513-514` daOptions echo |
| same §2 | zeropivot reaches the factor but doesn't fix −9; ILU −9 vs LU converged | PETSc `-sub_*` options | V | `zeropivot_rcm.log` PCView "tolerance for zero pivot 1e-08"; `control_rcm.log:4` reason −9 + PCView `type: ilu`; `sublu_rcm.log:7` reason 2/347 + `type: lu` |
| `dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md` + `DEFECT_REACH_decomposition_cases.md` | np-sweep: scotch np3/np4 dirty, np2/simple clean | decomposition method + rank count | V (every row) | `W4-a4-stepsweep/a4_np2_patched.log:41` "Decomposition method scotch [2]"; `a4_np3_patched.log:43` [3]; `a4_np4_patched.log:45` [4]; `a4_np4_simple4x1x1.log:45` / `a4_np4_simple1x4x1.log:45` "simple [4]"; each with 4× nProcs banners and exact OpenMDAO rows (e.g. `a4_np4_patched.log:11684`) |
| same records | those runs used patched IDWarp | PYTHONPATH lever | **U** (the sweep's own W-2) | register item 9 |
| `DEFECT_REACH…md` N1–N9 | all reach arms' decomposition claims | scotch/simple layouts, np | V | `W4-defect-reach/` logs all carry "Decomposition method …" + nProcs banners + `IDWARP_IMPORTED_FROM: /patch/...` at line 3 (8 arms listed in batch report) |
| same N6 | CBFS invariance arm ran sub-LU like the record arm | `DAFOAM_SUBPC_TYPE=lu` | V | `W4-defect-reach/cbfs_simple411.log:12091` banner |
| `DEFECT_ROBUSTNESS_mesh_and_setup.md` R3a/R3a1/R3a2/R6a/R6b/R2b | limiter branch gates the defect | `div(phi,U)`/`gradSchemes` tokens | V (indirect — field deltas; no scheme echo exists) | `a4knob_schemes.log:11680` analytic 3.0977e-01 + KSP 68 (record baseline 719); `a4knob_divupwind.log:11680` 2.7681e-01/KSP 41; `a4knob_gradlim.log:11687` 3.1706e-01/KSP 780; `a4knob_divlinear.log:11682` 2.0299e-01; `a4knob_divlinupw_unlim.log:11680` 2.0572e-01; `a4med_divlinupw_unlim.log:22450` 7.2627e-02 + reason 2@149; driver one-line-diff assertions |
| same N9/R5b/R1/R7 | freestream vs inletOutlet BC claims | U farfield BC type | V (indirect) | as-run dicts (`a1fs_np1/0/U:39` "freestreamVelocity"; `a4_inletOutlet_scotch/0.orig/U:18` "inletOutlet") + runtime discriminator `io_d_np4scotch.log:4385` CD0=1.522907906302396e-01 (0.44% off freestream's, N9 analytic to 16 digits) |
| same R3c | restart-60 stagnation | `gmresRestart 60` | V | `a4knob_restart60.log:492` echo; `:4384` reason −3@1000 |
| same R3b | primalMinResTol is a gate, not depth control | `primalMinResTol 1e-10` | V | `a4knob_primal10.log:344` echo; `:15015` "Primal solution failed!" |
| same R2/R4 | refined-mesh scotch diverges; defect fires on conformal mesh | np4 scotch | V | `a4med_np4scotch.log` scotch [4] + reason −3@1000; `a4conf_np4scotch.log` scotch [4] + `:11671` row |
| same R7/R7f | limiter breaks the serial tape (92.8%) | np1 vs np4, limiter token | V | `a1lim_np1.log:2315` 1.066449e-01; `a1lim_np4scotch.log:2665` 1.066142e-01 + scotch banner; `a1limdef_np1.log:2315` 6.516374e-02; stamps at line 3 |
| `DISCRIMINATORS_A4…md` + `VERIFICATION_A4_mechanism…md` | scotch psi leaves 329× ‖b‖ under serial operator | np/decomposition + instrument | V | `W4-a4-discriminators/d_crossres.log:4124` "W4X tag=np4scotch … ratio=3.288139e+02"; `d_np4scotch.log:48` scotch [4], `d_np4simple.log:48` simple [4] |
| robustness/reach survey rows | turbulence model is not a correlate | RAS model per case | V | `a4knob_schemes.log:180` kOmegaSST; `cbfs_simple411.log:210` kOmegaSST; `a1fs_np1.log:49`, `a1lim_np1.log:49`, `sail_simple3x1x1.log:185` SpalartAllmaras |
| `dafoam/W5_GRADIENT_REGRADE.md` (+ `PATCH_…`, `W4_CARRY_…`) | stock-vs-patched IDWarp regrades A1/A2/A4/A5/sail | patched IDWarp | V | every `W5-regrade/*.log` line 3 stamps `IDWARP_IMPORTED_FROM:` (`/patch/idwarp/...` vs `…/site-packages/idwarp/...`; 14 logs checked) |
| `dafoam/ROOTCAUSE_getRotationMatrix3d.md`, `VERIFICATION_rotation_patch…md` | degenerate-rotation branch is root cause; ON/OFF discriminates | `useRotations`, nRanks, h | V | `dafoam/rotation_branch/D1a_pl_real_rot_ON.txt:4` "REPRO … nRanks=4 h=1.0e-04 useRotations=on"; `D1b…OFF.txt:4` "useRotations=off" |
| `dafoam/W4_IDX16_IS_THE_REFERENCE.md` | idx16 FD reference probes under patched IDWarp | patched IDWarp | **U** | register item 10 |
| `subpclu_patch/DALinearEqn_subpclu.patch` B-1 | non-"lu" values fall silently to stock ILU | `DAFOAM_SUBPC_TYPE` | **FD hazard (known, mitigated)** | ranked item 4 above |

### 4. DAFoam ladder-b / S1 CBFS / W2 SPARTA

| record | conclusion | lever | class | evidence |
| --- | --- | --- | --- | --- |
| `dafoam/ladder-b/B2_duct_baseline.md` | baseline reproduced with STOCK SST after custom lib removed | `RASModel kOmegaSST` | V | `dafoam/ladder-b/duct_baseline/AR_1_Ret_360/log.run:55` selection (AR_3 gz:55, CBFS gz:47; Case/Build headers prove provenance) |
| same | periodic ducts driven by fixed bulk velocity | `meanVelocityForce` fvOption | V | `AR_1…/log.run:86` "Selecting finite volume options type meanVelocityForce"; `:101` Ubar echo |
| same | CBFS runs to fixed endTime 30000; iteration counts 456/1700 | endTime; convergence criterion | V | single terminal `Time = 30000` in CBFS gz; `AR_1 log.run:6481` "SIMPLE solution converged in 456 iterations"; AR_3 gz:23897 "…1700" |
| `dafoam/ladder-b/B3_duct_field_inversion.md` | `useWallFunction: True` silently replaces low-Re walls → REJECTED; final run no override | `primalBC.useWallFunction` | V (both arms) | `dafoam/B3_work/CBFS/stage2_serial_run3.log:180-185` "Setting k wall BC … BCType=kqRWallFunction"; final `stage2_warm_run5.log:202-205` empty `primalBC { }`, zero BCType lines |
| same | adjoint −9 across objective and fill level | `pcFillLevel` 1 vs 4; variance vs force | V | `adjoint_pilot_run5.log:514/4338`; `diag_force_run2.log:516` `pcFillLevel 4` + `:12098` −9 |
| same | objective genuinely reads LES data | `DAFunctionVariance` ref data | V | `adjoint_pilot_run5.log:265` "Find 63000 reference points for variance of U" |
| `ladder-b/B3_supervisor_debug.md` | primalVarBounds floors don't fix −9 | `kMin/omegaMin` floors | V | `B3_work/fixA_kbounds/testA.log:413-415` echoes; `:12099` −9, 177.61 s |
| `ladder-b/S1_FIML_FIELD_INVERSION.md` | E2 SST field-inversion adjoint converges | kOmegaSST | V (indirect) | `S1_work/logs/fd_points/base_a.log:214` selection, objective bit-identical to E2's |
| same | E1 kOmega leg | kOmega | **U** | register item 11 |
| same | warp genuinely absent from FIML chain | mesh-warp subsystem | V | `s1_e2_sst.json` runtime probe `"warper_init": 0, "warper_jacvec": 0` |
| same rungs 1–4 | wall functions applied → −9; limitVelocity removed → −9; normalizeResiduals None → −3; natural ordering stops NaN | `useWallFunction`; `limitVelocity`; `normalizeResiduals`; `jacMatReOrdering` | V (all four) | `hump_wf_run1.log:386` BCType=nutkWallFunction + −9; `hump_nofvopt_run1.log` no limitVelocity line + −9 (baseline `hump_adjoint_run1.log:252` has it); `hump_nrn_run1.log:571` None echo + −3; `hump_nat_run1.log:552` natural + −3 |
| same addendum | 5-ordering split 2×(−9)/3×(−3); objective controls nothing | ordering × objective | V (7/7) | `W4-cbfs-reordering/cbfs_{rcm,1wd}…log:513`+−9; `cbfs_{natural,nd,qmd}…log:513`+−3 (exact seconds match); `cbfs_force_{rcm,natural}` |
| same | M6 family was already running natural | ordering echo | V | `jacMatReOrdering natural` in all 5 `A3-onera-m6-transonic/check_totals_run*.log` |
| same clip audit | printInterval hid 230× clip events | `printInterval`, `UMax` | V | `fd_points/base_a.log:474` `printInterval 100`; `fd_clip_audit_run1.log:22-27` per-iteration census |
| `ladder-b/S1_CBFS_INVERSION_RESULT.md` | all 17 eval adjoints sub-LU, reason 2/667 | `DAFOAM_SUBPC_TYPE=lu` | V (17/17) | banner in `S1-cbfs-inversion/log.eval001…017` (eval001:12047); eval018 none — killed pre-adjoint per ledger |
| same | DV is per-cell beta field | `betaFIOmega` inputInfo | V | `log.eval001:413` `fieldName betaFIOmega` |
| same | beta multiplies the PRODUCTION term (not Wu/Zhang-comparable) | which omega term | V-by-source | `DAkOmegaSST.C:743`; nothing echoes the term at runtime — a term-echo would need a patch |
| same | final-state control reproduces eval 16 | cold-start control | V | `log.final` terminal `OBJ varianceU: 1.5256460061195715e-02` (all digits) |
| same Amendment 1 | failed primal proceeds into stagnating adjoint | in-process restart defect | V | `log.calib:29935` "Primal solution failed!" + flat KSP |
| `ladder-b/S1_CBFS_REINVERSION_RESULT.md` | every eval sub-LU + 1e-8 tol; adjoint 2/675 | `DAFOAM_SUBPC_TYPE=lu`; `primalMinResTol 1e-08` | V (16/16) | banners in all `S1-cbfs-reinversion/log.eval001…016`; `log.eval001:371` 1e-08 + `:18663` reason 2/675; superseded stage `log.baseA:371` 1e-06 — both sides of the amendment's discriminating pair log-evidenced |
| same | inlet repair collapsed baseline 24.8× | `0/U` inlet profile | V (behavioral) | eval001 logged baseline varianceU 6.1509017109920479e-04 vs corrupted 1.5279278906359758e-02 + on-disk diff |
| `campaign/W2_SPARTA_FROZEN_CBFS.md` | frozen extraction ran the frozen model; propagation ran corrected model; sign falsifiers flipped | `kOmegaSSTFrozen`/`kCorrectiveFrozenFoam`; `kOmegaSSTCorrected` `RScale/bScale` ±1 | V | `campaign/W2_sparta_runs/cbfs_frozen/log.frozen:10` Exec + `:41` selection; `cbfs_prop/log.run:47` + printCoeffs `:70-71` `RScale 1; bScale 1;`; `cbfs_e2_signR/log.run:51` `RScale -1`; `cbfs_e2_signB/log.run:51` `bScale -1` |
| `campaign/W2_SPARTA_REGRESSION.md` | nine propagations ran the symbolic model with exact claimed coefficients | `kOmegaSSTSparta` RTerms/bDeltaTerms | V | printCoeffs echoes: `cbfs_m3pub/log.run:49` `RTerms ( ( 1 0 0 0.93 ) )`; `cbfs_m1pub:51` (0.39); `ph_m2pub:60-61` (1.39 + bDeltaTerms); `cbfs_mdisc:51` (0.544787); E3 `cbfs_e3_minus:51` (−0.544787); all `:47` selection |
| `campaign/W5_SPARTA_GATE_STATUS.md` | gate met by prior record, zero solves | none | V (derivative) | cites records verified above |

### 5. Campaign F-families / ladders [recovered from the dead fork's transcript + spot-checked inline]

| record | conclusion | lever | class | evidence |
| --- | --- | --- | --- | --- |
| `campaign/F2_transonic_naca0012.md` | Cd/Cl/shock reproduction stands | rhoSimpleFoam + kOmegaSST | V (spot-checked) | `campaign/F2_runs/primary_M0.8_a1.25_Re6e6/log.rhoSimpleFoam.gz:10` "Exec : rhoSimpleFoam", `:61` selection; secondary run same |
| `campaign/F3_supersonic_exact_theory.md` | all three exact-theory gates PASS | rhoCentralFoam, Kurganov flux, laminar | V (spot-checked) | `F3_runs/wedge/M2.5_th10/fine/log.rhoCentralFoam:10/:48/:50` incl. "fluxScheme: Kurganov"; identical in cone and diamond fine logs |
| `campaign/F4_hypersonic_blunt_body.md` §4–5 | Billig standoff / Cp gates PASS | rhoCentralFoam, Kurganov, laminar | V | `F4_runs/cyl/M{6.0,7.0,8.0}/fine/log.rhoCentralFoam:10/:48/:50` |
| same §7 | crashed SWBLI warmup was kOmegaSST + LTS + Kurganov | kOmegaSST, localEuler, Kurganov | V | `solve_registry/f4_swbli_warmup20_20260730T004453Z.log:16639` "Using LTS", `:16658` selection, `:16683` fluxScheme |
| same diagnostics | LTS artifact / farfield elimination arms | rhoCentralFoamBounded, farfield BC | **U** | register item 12 |
| `campaign/F5a_cylinder_reynolds_ladder.md` | dimensionality attribution: every rung un-modelled laminar (incl. Re 3900 revert) | laminar | V | `solve_registry/f5a_re2000_20260729T021645Z.log:41`, `f5a_re3900_20260729T203008Z.log:41`, `f5a_re3900_correctedspacing_20260729T233553Z.log:41`, `f5a_re1000_3d_pilot_20260729T215854Z.log:52` "Selecting turbulence model type laminar"; `F5_runs/re1000/log.pimpleFoam:41` |
| `campaign/F5bc_unsteady_statistics.md` (F5c) | model in play was kOmegaSST | kOmegaSST | V | `solve_registry/f5c_extended_simplec20k_20260730T042423Z.log:46`; laminar control `F5c_runs/sign_convention_control/log.simpleFoam.gz:43` |
| same incl. 2026-08-08 amendment | −10.5% headline attributed to "the SIMPLEC coarse case" | SIMPLEC | **U — most consequential gap** | register item 1 |
| same (F5b) | pitching feasibility potentialFoam-init fix | potentialFoam init | **U** | register item 13 |
| `campaign/F6a_DIFFUSION_RESULTS.md` T1 | a1 cap sweep moves bubble as predicted | kOmegaSST `a1` 0.31/0.25/0.40 | V (spot-checked) | `solve_registry/f6a_diff_SST_control_20260801T000426Z.log:140` selection + `:180` "a1 0.31"; `…a1_025…log:168` "a1 0.25"; `…a1_040…log:168` "a1 0.4" |
| same T2 | LRR fails 3×; SSG/EBRSM run | LRR/SSG/EBRSM selection | V | `solve_registry/f6a_diff_LRR_20260801T003703Z.log:132`, `f6a_diff_SSG_20260801T004155Z.log:132`, EBRSM logs present |
| `campaign/F6a_epistemic_band.md` | 4-model channel-1 band | kOmega/kEpsilon/realizableKE/SA | V | `dafoam/f6a_epistemic_band/channel1_rans_sweep/{kOmega:140,kEpsilon:67,realizableKE:66}/log.simpleFoam`; SA via `solve_registry/hump_SA_resume2_20260729T204648Z.log:59` |
| same oneC ladder | eigenvalue perturbation active; divergence at δ≥0.5 is the perturbed model | UQEigenPerturb fvOption | V | `r4_band_tightening_hump/oneC_delta0.25/log.simpleFoam:197-201` "Selecting finite volume options type vectorCodedSource / Source: UQEigenPerturb / State: active", `:214` per-case dynamicCode |
| `campaign/F6b_ERCOFTAC_RESULTS.md` | stock SST +72% hills over-prediction | kOmegaSST | V | `solve_registry/f6b2_medium_20260805T171046Z.log:50`, `f6b2_veryfine…:50`, `f6b_gate_20260729T035745Z.log:58` |
| `campaign/F6b_QCR_RESULTS.md`, W1 hump QCR | QCR nulls are real physics | kOmegaSSTQCR + Ccr1 | V (cited) | `QCR_ACTIVITY_CHECK_2026-08-08.md` (1a14e90b); re-sighted `F6b_runs/medium_qcr2000/log.simpleFoam:61` |
| `campaign/F7_marine_free_surface.md` | dam-break gates; VOF laminar | interFoam, laminar | V | `F7_runs/F7a_R1/res16_base/log.interFoam:10` "Exec : interFoam -parallel", `:55` laminar |
| `campaign/F8_MRF_HAND2001_GATE.md` | steady-MRF branch closed on evidence; impulsive-start hypothesis refuted | MRF zone, potentialFoam init, SA | V | `F8_runs/phase6_mrf/log.simpleFoam:59-60` "Creating MRF zone list from MRFProperties / creating MRF zone: MRF" (also omegaflip, pfinit); `phase6_mrf_pfinit/log.potentialFoam:10` "Exec : potentialFoam -writephi"; SA `:56` |
| same | omega magnitude/sign ±7.5398 | MRF omega value | **U** | register item 15 |
| `campaign/F9_pulsatile_valve.md` | laminar Womersley gates | pimpleFoam, laminar | V | `solve_registry/F9_physio_dt_half_20260730T150516Z.log:10/:41`, `F9_lowalpha_ext…:10/:41` |
| `campaign/F11_lid_driven_cavity_ladder.md` | Ghia cavity gates | simpleFoam, laminar | V | `solve_registry/f11_re1000_n128_20260730T041833Z.log:10/:43` |
| `campaign/DMR_RESULTS.md` | double-Mach reflection result | rhoCentralFoam, Kurganov, laminar | V | `DMR_runs/res120/log.rhoCentralFoam:10/:62/:64` |
| `campaign/D5_RSM_RESULT.md` | SSG 55% / LRR 207% / EBRSM 52% | SSG/LRR/EBRSM selection | V (spot-checked) | `solve_registry/d5_SSG_20260729T022019Z.log:55` "Selecting RAS turbulence model SSG" (Case `:16` = `D5_rsm_runs/SSG`); `d5_LRR…:55`; `d5_EBRSM…:55`; continuations `d5b_*…:46`, `d5g_EBRSM…:46`. **TRAP:** `D5_rsm_runs/{SSG,LRR,EBRSM}/log.run` are donor COPIES of the kOmegaSST duct-baseline log (Case line `:16` names `ladder-b/duct_baseline/AR_1_Ret_360`) — verifying from the case dirs alone would misread D5 as dead-lever; the registry logs are the real proof |
| `campaign/B52_RUNG7_RESULTS.md`, `B52_RUNG8_RESULTS.md` | rung solves per recipe | potentialFoam init, kOmegaSST | V | `/home/ubuntu/certonomous-runs/study-b52-rung7-uq/log.potentialFoam:10`, `log.simpleFoam:56`; rung8 identical |
| `campaign/R4_ASYMPTOTIC_RESULTS.md` | refinement verdicts | kOmegaSST | V | `R4_runs/c1/log.simpleFoam:56` (c2–c5 alongside) |
| `campaign/R7_STROUHAL_SPACING_RESULTS.md` | spacing robustness | pimpleFoam laminar | V | `F5_runs/re1000_coarsespacing/log.pimpleFoam:10/:52` |
| `campaign/LADDER_V_RUNGS_*.md` | V-rung hand-trace PASS | kOmegaSSTQCR Ccr1 0.3 | V | `/home/ubuntu/certonomous-runs/w3-qcr-rank1/AR_1_Ret_360_qcr/log.simpleFoam:55/:79/:5628`; `AR_7_Ret_180_qcr:55/:79` |
| `campaign/MODEL_FORM_BAND.md` + `N_A10_THIRD_MEMBER_PREREGISTRATION.md` | per-member model identity of every band | SA/SST/kEpsilon/realizableKE | V | `MODEL_FORM_runs/N_a10_{SpalartAllmaras,kOmegaSST,kEpsilon}/log.simpleFoam.gz:45`; `H_re10595_{SpalartAllmaras,realizableKE}:51`; `B_re3e6_kEpsilon:45` |
| `campaign/W1_bump_nasa_grids.md` | TMR bump ladder on NASA grids | simpleFoam + kOmegaSST | V | `W1_runs/medium/log.simpleFoam.gz:10/:45` (coarse/fine archived) |
| `campaign/DPW8_V2_joukowski.md` L1/L3 | Joukowski convergence signature | kOmegaSST | V | `DPW8_V2_runs/run_L3_physics/log.simpleFoam:45`; L4 honestly has no log (killed pre-write, disclosed; divergence from `run_L4_gate.stdout.log`) |
| `campaign/F3/F4` inviscid claims | μ=0 | transport dict | **U** | register item 14 |

### 6. W1 / W3 / model comparison / status files / dafoam f6 cases

| record | conclusion | lever | class | evidence |
| --- | --- | --- | --- | --- |
| `campaign/RANS_MODEL_COMPARISON.md` | 5-of-5 linear models machine-zero duct secondary flow; LienCubicKE 0.174% | SA/kEpsilon/realizableKE/kOmega/SST; LienCubicKE | V (all six) | `dafoam/rans_model_comparison/SpalartAllmaras/log.run:45`, `kEpsilon:55`, `realizableKE:43`, `kOmega:55`; `LienCubicKE/log.run:56886` (the reported reduced-relaxation run's second selection banner; discarded run's at `:43`); SST via `ladder-b/duct_baseline/AR_1_Ret_360/log.run:55` |
| same | "F7a NOT APPLICABLE — no turbulence model active" | `simulationType laminar` | V (upgraded — record cited only dictionaries) | `campaign/F7_runs/damBreak_MM_a2p25in_coarse/log.interFoam:44`, `…medium/log.interFoam:55`, `…medium_closedbox/log.interFoam:55` |
| `campaign/W3_QCR_DUCT_FALSIFIER.md` | falsifier CONFIRMED + 4-duct battery | kOmegaSST ×4 / kOmegaSSTQCR Ccr1 0.3 ×4 / Ccr1=0 control | V (all 9 arms) | `/home/ubuntu/certonomous-runs/w3-qcr-duct/{AR_1,AR_3,AR_5,AR_10}_{sst,sst_qcr}/log.simpleFoam:55` (+`:79` "Ccr1 0.3"); control `qcr_cr0/log.simpleFoam:46` + `:51` "Ccr1 0" |
| `campaign/W1_HUMP_CHALLENGE_RESULTS.md` | QCR null on hump | kOmegaSST / kOmegaSSTQCR | V (= QCR check, re-confirmed) | `W1_hump_runs/sst/log.simpleFoam:71`; `sst_qcr/log.simpleFoam:71` + `:94` "Ccr1 0.3"; both echo stock `a1 0.31` at `:87` |
| `campaign/W1_HUMP_A1_RESULTS.md` | a1 limiter is a mechanism (−0.0498 x/c at a1=0.34) | kOmegaSST `a1` coefficient | V | `W1_hump_runs/a1_034/log.simpleFoam:75` "a1 0.34"; `a1_028/log.simpleFoam:75` "a1 0.28" |
| `campaign/AHMED_BODY_RECONCILIATION.md` | both sides were kOmegaSST (SA attribution would be wrong) | kOmegaSST both codes | V | `mission-output/ahmed-body/act7-ahmed_25/log.simpleFoam:56`; `mission-output/geometry-study/study-ahmed_25/log.simpleFoam:45`; `/home/ubuntu/certonomous-runs/A4-ahmed-body/fine/compute_run_model_par4.log:177` |
| same + `ACTIVE_RESEARCH.md` | differing knob was SIMPLE vs SIMPLEC | SIMPLEC | **U** | register item 2 |
| `campaign/W1_TMR_NACA0012_DISPOSITION.md` | scheme-substitution root cause | div schemes per arm | **U** | register item 3 (dismissal itself survives on log-backed grounds) |
| `campaign/W3_PUBLISHED_RUNG_REPLICATES.md` §4 | cube production run never converged | absence of convergence line | V (with path drift) | 0 occurrences in `mission-output/geometry-study/study-cube/log.simpleFoam` (kOmegaSST `:56`); replicates `w3-published-rung-cube/{a,b}` also 0. Cited path `certonomous-runs/study-cube-2904cb/…` no longer exists |
| `campaign/NOT_PASSING_REGISTER.md` F8 entry | never converged under steady MRF | MRF zone; model | V + hedge settled | `F8_runs/phase6_mrf/log.simpleFoam:59-60` MRF zone; `:56` — the model was **SpalartAllmaras**, not the entry's hedged "k-omega" |
| `dafoam/f6a_nasa_hump/F6a_nasa_hump.md` | +13.9% reattachment bias under STOCK kOmegaSST | kOmegaSST (not Augmented) | V | `dafoam/f6a_nasa_hump/case/log.{rung1_feasibility,rung2_physics,rung3_gate}:71` |
| `dafoam/f6b_periodic_hills/F6b_periodic_hills.md` | hills gate under stock SST | kOmegaSST | V (log in registry, not case dir) | `solve_registry/f6b_gate_20260729T035745Z.log:58` (Case header = the f6b case) |
| `dafoam/f6c_duct_dns/F6c_duct_vs_dns.md` | duct zero under SST vs DNS | kOmegaSST | V | `ladder-b/duct_baseline/AR_1_Ret_360/log.run:55`; `AR_3…/log.run.gz:55` |
| `CLOSURE_CHALLENGE_STATUS.md` §0f | duct signal is the QCR term itself (round-5 0.0566) | kOmegaSSTQCR Ccr1 0.3, 3 ducts + AR_7 pair | V | `w3-qcr-rank1/{AR_1_Ret_360,AR_3_Ret_360,AR_14_Ret_180,AR_7_Ret_180}_qcr/log.simpleFoam:55/:79`; `AR_7_Ret_180_sst:55` |
| `campaign/CASES_FAMILY_FIRST_PASS_FINDINGS_2026-08-07.md` family-N arms | model-arm identities | kEpsilon/SA/SST/realizableKE at a0 and a10 | V (auditor-inline) | `MODEL_FORM_runs/N_a0_{SpalartAllmaras,kEpsilon,kOmegaSST,realizableKE}/log.simpleFoam.gz:45` all selection banners; `N_a10_realizableKE…gz:45` (a10 SA/SST/kEpsilon in section 5 row) |

### 7. Narrative / reading / doctrine files — passing mentions only (swept, nothing load-bearing of their own)

`W2_CLOSURE_LITERATURE_READING.md`, `W2_DAFOAM_AIAAJ2020_VERIFICATION_READING.md`,
`W2_DAFOAM_CAF2018_VERIFICATION_READING.md`, `W2_DOW_STRUCTURAL_UQ_{PROGRAM,READING}.md`,
`W2_KENWAY_PAS2019_EFFECTIVE_ADJOINT_READING.md`, `W2_POPE_1975_INTEGRITY_BASIS.md`,
`W2_TBNN_SPARTA_READING.md`, `W2_WU_ZHANG_DESTRUCTION_FIML_READING.md`,
`W2_CFD_DRIVEN_TRAINING_READING.md`, `LITERATURE_REPRODUCTION_REVIEW.md` (its SIMPLEC
and preconditioner lines restate F6a / A3 records audited above),
`CHALLENGE_SLATE_2026-08.md`, `NEXT_CASES_SLATE.md`, `D9_TALKING_POINTS.md`,
`CASES_FAMILY_SUPERVISION_GUIDELINES.md`, `dafoam/FAMILY_SUPERVISION_GUIDELINES.md`,
`dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md`, `dafoam/SUPERVISOR_FAMILY_REVIEW_2026-08-07.md`,
`SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`, `SHARED_TREE_COMMIT_HAZARD.md`,
`NAVYFOAM_FINDING.md` (availability scoping, zero runs), `dafoam/LIAISON_RESEARCH_adjoint_conditioning.md`,
`dafoam/LIAISON_NOVELTY_SWEEP_decomposition_defect.md`, `dafoam/W5_COMMUNITY_REPORTS_TESTED.md`,
`dafoam/UPSTREAM_BUG_REPORT_{decomposition_adjoint,mesh_warpDeriv}.md` (summaries of
verified runs), all preregistrations whose RESULTS records were audited instead,
`R5_RULE_FREEZE.md`, `MODEL_FORM_BATCH_DESIGN.md`, `DPW8_AEPW4_SCOPING.md`,
`LADDER_V_TRIPLE_VERIFICATION.md`, `F6d_random_matrix_uq.md` (analysis layer; its one
cited solve log-verified), all `.json` twins of audited `.md` records,
`OTHER_WORK_STATUS.md` (its class-7 verdict and proposal queue cite no archived-run
levers; its SIMPLEC audit line is the queued proposal, covered by register item 2).

---

## Secondary defects surfaced (for the chief — not corrected by this audit, per the negative-verdict process)

1. **`dafoam/DAFOAM_CASE_STATUS.md:84` misstates A4's DAFoam turbulence model as
   SA** — all four archived A4 logs print `Selecting RAS turbulence model
   kOmegaSST` (`logs_A4/*.log:177`), matching the baseline. The logs strengthen
   the A4 bistability conclusion (model parity held); one-word correction needed.
2. **`NOT_PASSING_REGISTER.md` F8 model hedge** ("k-omega… SA per 0/nuTilda") is
   settled by the log: SpalartAllmaras. Dated correction line warranted.
3. **Stale evidence paths:** `W3_PUBLISHED_RUNG_REPLICATES.md:63` cites the
   deleted `certonomous-runs/study-cube-2904cb/` (log survives at
   `mission-output/geometry-study/study-cube/`); F6b's gate/control solver logs
   exist only in `solve_registry/`, not the case dirs the records point at; the
   D5 case dirs carry donor logs (trap, section 5).
4. **`ADJOINT_MEMORY_ENVELOPE.md` Options 1–2 lost their solver logs** with the
   dead session scratchpad; recommend the record note this on its face.
5. **A3_SUBLU attempt-3 log ends with no reason code** — that arm is unresolved
   business for the chief/solver agent.
6. **Face caveats owed** per charter §9 on register items 1–4 (F5c SIMPLEC, Ahmed
   SIMPLEC, TMR scheme narrative, A3 shock-scheme claim).

## Scope and truncation statement (nothing silently truncated)

Exhaustive on conclusion-bearing records under `campaign/`, `dafoam/`, and the
three family status files. Not exhaustively line-swept, stated openly: PROOF.md
§1–24 hypothesis-ladder interior (grep-swept; its lever conclusions surface in
the section-2 rows); rotation_branch D2–D6 diagnostics beyond the D1a/D1b pair
(same REPRO echo format confirmed on the pair opened); `W4-a4-du0check` (its
value independently confirmed to 16 digits in `io_d_np4scotch.log:4385`);
top-level `closure_challenge_*` records outside the ordered scope (closure
family's rails) except `CLOSURE_CHALLENGE_STATUS.md` §0f, which was verified
(section 6). The F-family section was verified by a batch agent that died
mid-report; its findings were recovered from its transcript and five quoted
evidence lines re-confirmed inline before inclusion.

---

# Addendum, 2026-08-10 — L-43 re-check of this audit's 20 at-risk rows

Ordered by the chief after the batch dead-lever sweep (`DEAD_LEVER_AUDIT_BATCH_2026-08-10.md`)
withdrew its own first-pass headline, and the near-miss became `LESSONS.md` L-43:
**an audit's null result is a claim about the audit's REACH before it is a claim
about the world.** That sweep's instrument had been blind to gzipped logs and to
gitignored trees. This audit was executed with the same shell, so its
**16 UNVERIFIABLE-FROM-LOGS rows and 4 FOUND-DEAD rows** — the rows that rest on
*absence* of evidence — were re-tested with a reach-proven instrument. The 126
VERIFIED rows are not re-tested: they quote lines, so the instrument saw them.

## The positive-control line this audit lacked

This audit stated a negative control (`W4-adjoint-pc-unblock/cbfs_regress_computetotals.log`,
no banner, reason -9) but never a positive one — it never showed that its search
*could* see evidence where evidence was known to exist. Supplied now, three ways:

| control | test | result |
| --- | --- | --- |
| **PC-1 run corpus** | `grep -rn "adjUseColoring" /home/ubuntu/certonomous-runs/W4-a4-discriminators/` | **PASS** — `d_np4scotch_nocolor.log:483: adjUseColoring 0;`, the exact line this audit cites at register item 7 |
| **PC-2 gzip** | `zgrep -c "Selecting RAS turbulence model"` on an archived `log.simpleFoam.gz` | **PASS** — banner read inside gz |
| **PC-3 gitignored tree** | `command grep -rl` for the same banner under `mega-batch/work/` (gitignored) | **PASS** — 17 files found |

A fourth, incidental: the first attempt at PC-1 returned nothing because a
79 GB unscoped sweep was killed at timeout before reaching the directory. The
null was a timeout, not an absence — L-43 arriving a second time, in the
instrument built to test L-43.

## Result: 0 of 20 rows change classification

**No FOUND-DEAD row turned out verifiable-and-alive. No conclusion was reopened
wrongly.** The 16 unverifiable rows remain unverifiable and the 4 found-dead
rows remain dead. Re-test evidence by reason class:

| reason class | rows | re-test | outcome |
| --- | --- | --- | --- |
| Structural (no possible echo) | 2, 3, 4, 14, 15, half of 1 | unfalsifiable by search; confirmed against the stated mechanism | **stands** |
| File destroyed (scratchpad/session loss) | 7, 8, 13, half of 1 | `F5c_runs/` re-listed: holds only `sign_convention_control` as stated; no `f5b` artifact in `solve_registry/` | **stands** |
| In-container source, not locally readable | 5, 6 | `find / -name DALinearEqn.C -o -name DAResidualRhoSimpleCFoam.C` → **no hits anywhere on this host** | **stands** — the "in-container only" claim is true, not an excuse |
| Claimed absence of an archived log | 11, 12 | full-name search: `warmup20_bounded` appears in three records and **zero logs**; S1-fiml swept for a plain-`kOmega` banner | **stands** |
| Claimed absence of a line in an existing log | 9, 10 | stamp grep on the named run dirs | **stands** (refined, below) |
| Already closed by this audit | 16 | — | **stands** |

## Two refinements — better evidence, same classification

**Register item 9 (W4-a4-stepsweep patched-IDWarp provenance).** This audit says
"no `IDWARP_IMPORTED_FROM` stamp in those logs". Precisely true of the arms:
`a4_h1e-3_patched.log`, `a4_h1e-4_patched.log` and `a4_h1e-3_stock.log` carry
zero stamps. But **the same directory holds a stamped log this audit did not
cite** — `W4-a4-stepsweep/a4_dcddxv.log:3` reads
`IDWARP_IMPORTED_FROM: /patch/idwarp/idwarp/__init__.py`, written 34 minutes
after `a4_h1e-3_patched.log` in the same session. It does not make the
individual step-sweep arms self-proving, so the row stays UNVERIFIABLE, but it
is a third independent corroboration alongside the two already named.

**Register item 11 (S1_FIML E1 kOmega leg).** This audit says "only
`s1_e1_kw.json` survives, no selection banner anywhere". The case directory
survives too: `S1-fiml/ramp_kw/c2/constant/turbulenceProperties` reads
`RASModel kOmega;` (and `tf_training/` likewise), against `c1/`'s `kOmegaSST`.
So configuration survives; activity does not, which is exactly what L-40 says is
worth nothing on its own. Local positive control for this row: the S1-fiml
corpus contains **108** `Selecting RAS turbulence model` banners and **every one
reads `kOmegaSST`** — the instrument would have seen a plain-`kOmega` banner had
one ever been written. Row stays UNVERIFIABLE, now with a sharper reason: the
kOmega leg was configured and its log was never archived.

## Standing caveat this re-check surfaces

**FD-1 and FD-2's deadness cannot be re-verified on this host.** FD-1's proof is
a source read (`DAResidualRhoSimpleCFoam.C:173`, only `== 1` exists) performed
in-container at `12d3a7a3`; FD-2 cites no independent evidence in this audit at
all, inheriting from prior records. Neither source file exists on this host. The
log side of FD-1 re-confirms cleanly — `W4-m6-reordering/m6_natural.log:489`
reads `transonicPCOption 2;`, and `W4-adjoint-pc-unblock/cbfs_beta_computetotals.log:474`
reads `transonicPCOption -1;` — but a log echo proves the value was *configured*,
never that it was dead. **Both FOUND-DEAD verdicts rest on in-container reads
that no one can currently reproduce.** Nothing suggests they are wrong; they are
simply not independently checkable from this machine, and a future container
session should re-read both lines and stamp the result.

### CAVEAT CLOSED 2026-08-10 — re-read in-container under the chief's provenance rider. **FD-1 CONFIRMED. FD-2 REFUTED.**

Both source reads were performed inside a live container (`docker exec` into the
running rung-3 solver, zero marginal cost) and, for FD-2, repeated in the stock
image. Image tags stamped so the reads are reproducible.

**FD-1 — CONFIRMED, exactly as recorded.** Image `dafoam-subpclu:v1`:

```
adjoint/DAResidual/DAResidualRhoSimpleCFoam.C:173
    if (isPC && daOption_.getOption<label>("transonicPCOption") == 1)
```
— and it is the file's ONLY `transonicPCOption` occurrence (grep: 1 hit), so
`== 2` is unreachable for `DARhoSimpleCFoam`. The `== 2` branch exists only at
`adjoint/DAResidual/DAResidualTurboFoam.C:176` (a different solver), with a
`== 1` branch at `DAResidualTurboFoam.C:161`. Repo-wide there are exactly three
occurrences, matching the audit's account precisely. FD-1's deadness verdict now
has a reproducible provenance line.

**FD-2 — REFUTED. The FOUND-DEAD verdict is WRONG, and it had propagated into a
physics conclusion.** `consistent yes;` (SIMPLEC) is NOT dead for
`DASimpleFoam`: it is implemented in the primal AND the adjoint residual, in
BOTH images (`dafoam-subpclu:v1` and stock `dafoam/opt-packages:latest`):

```
adjoint/DASolver/DASimpleFoam/pEqnSimple.H:27    if (simple.consistent())
adjoint/DAResidual/DAResidualSimpleFoam.C:189    if (simple_.consistent())
        rAtU = 1.0 / (1.0 / rAU - UEqn.H1());
        phiHbyA += fvc::interpolate(rAtU() - rAU) * fvc::snGrad(p) * mesh.magSf();
        HbyA -= (rAU - rAtU()) * fvc::grad(p);
```

That is the textbook SIMPLEC correction gated on exactly the flag the A4 baseline
case sets.

**Root cause of the wrong verdict, named so the class is closed:** the original
search (quoted in `ladder-a/A4_ahmed_body.md`) grepped `DASimpleFoam.C` and
`DASolver.C`. The SIMPLEC logic is in neither — it lives in the **included**
`pEqnSimple.H` and in `DAResidualSimpleFoam.C`. `DASimpleFoam.C`'s only
`consistent` hits are two comments about the *consistent fixed-point adjoint*
(lines 187, 220) — precisely the "unrelated comment usages" the original text
reports. **An include-blind grep over a C++ solver whose equations live in `.H`
includes manufactured a FOUND-DEAD verdict.** The file list, not the search
string, was the defect.

**Blast radius, already actioned:** FD-2 was *integrated into* the A4 Ahmed
conclusion as the mechanism for its 22.05% cross-code gap. That cause claim and
the lesson built on it are RETRACTED on A4's face (7ca80f8d); the measured 22.05%
stands, its stated cause does not, and the gap is now UNEXPLAINED pending a
controlled `consistent` on/off arm under `DASimpleFoam` (filed, not run).

**Instrument rule this yields:** a deadness claim must quote the line, the file,
the image tag — and the file list it searched — so a later reader can reproduce
the search that failed, not merely the search that succeeded.
