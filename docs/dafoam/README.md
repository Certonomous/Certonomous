# DAFoam and adjoint CFD — start here

The lane's map. **This is a map, not a report**: every number below is a pointer to the
record that owns it. Dated 2026-08-21.

**The standing rules are `docs/charters/DAFOAM_CHARTER.md`.** Read it before writing code
or a preregistration. Its line:

> **A DAFoam gradient is not a result until a finite-difference table stands beside it at a
> step proved to lie in the plateau, and a DAFoam verdict is two rows — shipped and patched —
> or it is not a verdict about DAFoam.**

---

## 1. What exists, and where

| Document | What it is | Size |
|---|---|---|
| `docs/charters/DAFOAM_CHARTER.md` | **The standing rules.** 12 clauses, each naming the incident in these records that earned it, plus an enforcement table that admits the seven clauses nothing checks. | 583 lines |
| `docs/dafoam/PRIOR_WORK_INVENTORY.md` | **The record of record for what has been measured.** Part A (Ladder A, defects, patched builds, the papers' own verification protocol) and Part B (Ladder B, F6, supervision records, the DOCKET/LESSONS/NUMERICS cross-reference, the charter and house-style findings). 83 records, every claim cited to a file. | 1,607 lines |
| `docs/dafoam/TOOLCHAIN_INVENTORY.md` | Components and versions, the hard-coded settings in the shipped adjoint linear solver, the three container images with their in-image md5s and line counts, what each patch does, and the verbatim commands that measured all of it. | 388 lines |
| `cases/dafoam/INDEX.md` | Where every case, record, log and work tree **actually** lives today, the convention gap stated plainly, and the proposed directory names for new work (proposals only — the supervisor confirms). | 238 lines |
| `cases/dafoam/FAMILY_SUPERVISION_GUIDELINES.md` | **Binding operational guidance**, issued 2026-08-07: R11 two-row grading, §3.6 nothing filed upstream ever, §4.2–4.3 the FD protocol's operational half, §8 the cold-start and staged-copy rules. | 269 lines |
| `cases/dafoam/DAFOAM_CASE_STATUS.md` | The family's long-form status record, per case. | 296 lines |
| `cases/dafoam/PROOF.md` | The evidence file the defect arcs were built in. §25.2 is the five-ordering sweep on CBFS; **§25.3 is the offline matrix proof of the ILU zero pivot**, reproduced with no DAFoam and no PETSc solver in the loop. | 3,086 lines |
| `cases/dafoam/ladder-a/`, `cases/dafoam/ladder-b/` | The rungs themselves. New work goes in a `<RUNG>/<run-slug>/` subdirectory as `PREREGISTRATION.md` then `RESULTS.md`. | 6.7 GB total tree |
| `cases/dafoam/patched_build/` | **Reproducible `Dockerfile`s for the patched images**, with their build gates and measured results: `idwarp_rot/`, `subpclu/`, `kspopts/`. | 3 directories |

**Data and run trees live outside the repo.** Every solve runs under
`/home/ubuntu/certonomous-runs/<slug>/` (66 GB), one directory per campaign, each carrying
its own `ledger.csv`, per-arm logs and staged case copies. The benchmark clone the Ladder B
cases score against is `/home/ubuntu/closure-challenge-benchmark`. **Container images are
local only; nothing has ever been pushed to a registry.**

**The F6 series is not ours, and its records are in a third tree.** `f6a_nasa_hump/`,
`f6a_epistemic_band/`, `f6b_periodic_hills/`, `f6c_duct_dns/`, `f6d_random_matrix_uq/` and
`rans_model_comparison/` sit under `cases/dafoam/` for historical reasons and are **88 % of
the tree by size**. Every one is a plain OpenFOAM `simpleFoam` solve with **no DAFoam adjoint
anywhere**; they belong to family F6 of the hard-case campaign, and their analysis records
live at `verification/campaign/` — `F6_closure_aligned_flows.md`, `F6a_epistemic_band.md`,
`F6a_epistemic_propagation.md`, `F6a_EPISTEMIC_CASE.md`, `F6a_DIFFUSION_{PREREGISTRATION,RESULTS}.md`,
`F6b_{ERCOFTAC,QCR,RELAXATION_INVARIANCE}_{PREREGISTRATION,RESULTS}.md`,
`F6d_random_matrix_uq.{md,json}`, `F6D_OPTION_A_{PREREGISTRATION,RESULT}.md`,
`F6D_COLLISION_INDEPENDENCE_CHECK.md`, `F6D_ENSEMBLE_CONVERGENCE_AUDIT.md`, plus
`verification/runs/F6b_runs/`. **A reader who looks only in `cases/dafoam/` will conclude
F6a-band and F6d have no records. They have many, in the other tree.**

---

## 2. Reading order for a new team member

1. **`docs/dafoam/PRIOR_WORK_INVENTORY.md`** — Part A §1 (the six Ladder A rungs) and Part B
   §1.0 (the B3 settlement). Twenty minutes, and it is the only place the whole picture is
   assembled with citations. **§1.0 first if you touch Ladder B**: "is B3 still BLOCKED?" is
   *"yes — and no. Both halves are true"*, and getting it wrong is the most likely mistake.
2. **`docs/dafoam/TOOLCHAIN_INVENTORY.md` §3.** Three images, four md5s. You cannot read any
   patched number in this tree without it.
3. **`docs/charters/DAFOAM_CHARTER.md` in full.** Nothing else is worth reading until you know
   what a result has to be here. §6 is the one that changes how you write every table.
4. **`cases/dafoam/INDEX.md` §0 and §7.** Where things are, and where new things go. **§0's
   warning bites every reader**: most records were written when this tree lived at
   `demo-output/website/dafoam/` and still say so.
5. **One case directory, end to end.** `ladder-b/B3/` is the cleanest: a `README.md` that
   states the two-row verdict, a frozen `PREREGISTRATION.md`, a `RESULTS.md` graded against it,
   and a filing-ready-but-**NOT FILED** defect note beside them.
6. **`cases/dafoam/patched_build/subpclu/BUILD.md`.** What a reproducible rebuild of a patched
   image looks like, including a gate that was **predicted to fail** and the substitute gates
   that carry the real claim.
7. **`cases/dafoam/PROOF.md` §25.3** when you need the mechanism rather than the verdict. Do not
   read `PROOF.md` cold; it is 3,086 lines.

---

## 3. Standing verdict table — shipped and patched are always two rows

**R11**: a patched grade is recorded *beside* a shipped grade and never in place of it. Moving
a shipped verdict requires the fix to ship upstream or Sanaa to adopt a forked toolchain, and
that is her call (`FAMILY_SUPERVISION_GUIDELINES.md` §3.4; `SUPERVISOR_RULINGS.md:195`).

| Rung | Toolchain | Verdict | Headline, with its record |
|---|---|---|---|
| **A1** NACA0012, 4,032 cells | SHIPPED | **GATE FAIL** | `CD/shape` **11.4274 %**, **one sign flip, idx6 at 640.37 %**, np=1, step 1e-3. `ladder-a/A1/reverify_patched_idwarp_np1/RESULTS.md` §2 (measured 2026-08-21) |
| | PATCHED `dafoam-idwarp-rot:v1` | **PASS** | **0.03796 %**, zero flips, idx6 right-signed at 1.1888 %. **8 of 8 raw FD components bit-identical across arms**, so the image is a clean single-variable change. Same file |
| | PATCHED, wrong step (2c control) | **GATE FAIL, as designed** | **132.75 %** at step 1e-8. Same file |
| **A2** MACH wing, 38,304 cells | SHIPPED | **PASS**, six rows, zero flagged | `CD/shape` **1.714 %**, `CL/shape` 1.165 %, `CD/patchV` **0.0212 %**. `ladder-a/A2/grading_confirmation/RESULTS.md` §1, §3 |
| | PATCHED (bind-mount, **not** the v1 image) | **PASS** | `CD/shape` **0.0506 %** (33.9× tighter). *The shipped rows were ~97–99 % rotation defect: A2 passed its gate carrying the defect at nearly full strength.* Same file §3 |
| | optimisation | **NOT A RESULT** (time-boxed, unconverged) | IPOPT 47 of ~100 majors, `converged_to_optimizer_tolerance: false`, no EXIT line; **28.275488 %** drag reduction reached. Same file §4 |
| **A3** ONERA M6 — **two campaigns, never merged** | SHIPPED, 399,360 cells | primal **GATE REACHED**, Cp **PASS**, adjoint **BLOCKED** | CD 0.0229955633492643; 8 mitigations exhausted, OOM at 399,360 **and** at 99,840. `ladder-a/A3/grading_confirmation/RESULTS.md` §3 |
| | SHIPPED-equivalent, sweep 21,840 / 42,120 | **GATE REACHED** + FD **PASS** | 368/383 and 987/1171 iterations, reason 2; FD **0.18 % / 0.93 %** and **0.0077 % / 0.2740 % / 0.0172 %**. Same file |
| | SHIPPED-equivalent, sweep 79,560 | **GATE FAIL** | reason −3 at the 4,000-iteration cap, 1.31× reduction, **peak 11.65 GiB against a 22 GiB cap — conditioning, not memory**. Same file |
| | PATCHED | **PENDING** everywhere | *"No patched-IDWarp arm was ever run on A3, at any mesh size … not clean-by-omission."* Same file. **Superseded 2026-08-26 by the D7FR rows below: a patched arm has now run on A3 at 42,120 cells.** |
| | **D7FR** (curriculum, 42,120 cells, np=4) — SHIPPED, endpoint FD at D7R arm `O`'s PHYSICAL endpoint | **PASS** | `CD` adjoint vs central FD on the five registered components: `shape[115]` **0.0697 %**, `twist[1]` 1.9589 %, `patchV[1]` 0.6271 %, `shape[0]` 0.7071 %, `shape[119]` 0.1459 %; zero sign flips; G6/G6b/G7 controls PASS; in-item adjoint reason 2. 72.667 core-min against 485.0 predicted. Graded 2026-08-26 under Addendum 4 (`faeda019`). `ladder-a/A3/curriculum_D7FR/RESULTS.md` §3 |
| | **D7FR** — PATCHED `dafoam-idwarp-rot:v1`, same endpoint, same five components | **PASS** | **Identical to the shipped row to every printed digit** — worst 1.9589 %, zero flips, FD artefacts byte-identical (md5 `e284d925…`) though computed independently (own primals, own adjoint, distinct `.so` md5 `85f59e87…` vs `f0fcb488…`, G9 PASS). **Item verdict `PASS`, two rows; shipped-vs-patched divergence 0.000 % on every component is the registered finding** — the rotation defect A1/A5 measured does not reach this endpoint's registered components. Item 149.534 core-min / $0.1279 DERIVED against 997.75 predicted (ratio 0.150), 0 waste. Pre-repair D7-port composition `NOT A RESULT` written beside. Same file §1, §3 |
| **A4** Ahmed-25, 2,777 cells | SHIPPED | **PASS** | **1.10 %** at np=1, the graded configuration. The published **10.04 %** is a `scotch`-decomposition artefact at np=4. `ladder-a/A4/README.md` |
| | PATCHED — **first optimisation**, np=1 | **PASS** | Measured 2026-08-21. **9 majors, `Optimal Solution Found.`, NLP error 6.28e-07**; shape −0.04999982, **CD 0.14153492, −7.478 %**. **It did not stop on the iteration cap**, so the GATE REACHED ceiling of prereg §9 does not bind. **The endpoint FD check is what makes it a result rather than a descent: `CD wrt shape` at the *final* design point is 0.4936 %, zero sign flips** (`2.141012e-01` vs `2.151633e-01`) — inside the ≤5 % band. Charter-2c trivial baseline (`scaler=-1.0`) behaved as designed: CD **+9.090 %**, shape `+0.04992374` → **NOT A RESULT**, as registered. **13.150 core-min, \$0.0112 — 21.9 % of the registered ceiling**, against a predicted 39. `ladder-a/A4/first_optimisation_np1/RESULTS.md` §2, §3, §8 |
| | *two-row gap this exposes* | — | The two A4 rows do **not** measure the same thing: the **1.10 %** gradient PASS is at the **undeformed baseline** and is **NOT MEASURED** on the patched image; the **0.4936 %** PASS is at the **optimised design** and is **NOT MEASURED** on the shipped one. Neither row is a shipped-vs-patched comparison, and the file says so. Same file §5 |
| **A5** U-bend, **4,800 cells** (not 21,000) | SHIPPED | **GATE FAIL** | **46.840 %** over 27 components, **two sign flips, idx8 205.52 % and idx17 121.86 %**, np=1. `ladder-a/A5/reverify_patched_idwarp_np1/RESULTS.md` §2 (measured 2026-08-21) |
| | PATCHED `dafoam-idwarp-rot:v1` | **PASS** on the aggregate band, per-component caveat | **2.768 %**, zero flips, **22 of 27** in band; **27 of 27 FD components bit-identical across arms**. Three registered predictions **missed and reported as misses**. Same file |
| **A6** CRM wing-alone, 579,072 cells | SHIPPED, full size | **BLOCKED** (memory) **and independently BLOCKED** (conditioning) | Predicted peak **94.7–116.0 GiB against a 30 GiB box**; de-biased **74.6 GiB**. *"This verdict is recorded from prediction, not from an OOM, and that is the point."* `ladder-a/A6/adjoint_feasibility/RESULTS.md` §1 |
| | rung N=16, 41,760 cells, np=1 — SHIPPED **and** PATCHED `dafoam-idwarp-rot:v1` | **GATE FAIL on both images** | Measured 2026-08-21. Primal **GATE REACHED** (`primalMaxRes` 5.556e-06, 1,000 iters); **P3 adjoint PASS — `CD` `reason 2` in 517 iterations, the first A6 adjoint that has ever existed**. But **P4 FD-vs-adjoint GATE FAILS**: 8 of 9 graded components >15 % (57.06–340.70 % patched), **3 sign flips**, only `patchV` idx1 inside band at 3.29 %. **The patched image is not better** — identical on `patchV`, 0.028 pp *worse* in FD relative error. **Measured cause is the FD reference, not the adjoint** (a primal stopping 556× short cannot resolve a derivative below 4.5e-3). **76.653 core-min, \$0.0655**, 23.4 % of it waste. `ladder-a/A6/rung_n16_np1/RESULTS.md` §6, §9 |
| | rung **N=29**, 79,560 cells | **NOT RUN — gate not met** | Sanaa's condition was *N=29 only if N=16 passes on the patched image*. It does not. **Decision 2026-08-21: no N=29 arm launched, staged or queued; zero compute spent.** And the gate should not be re-opened by re-running N=29 as-is — *"fixing the reference, not enlarging the mesh, is the next step"*, unregistered. Same file §9.2 |
| **B1** reproduction plans | — | no verdict; a ranked plan | Leaderboard rank 2 is the DAFoam field-inversion entry (Wu & Zhang, 0.0624). `ladder-b/B1_reproduction_plans.md` |
| **B2** duct baselines | plain OpenFOAM, not DAFoam | **PASS / reproduced**, two disclosed deviations | AR_1 **0.1290** vs floor 0.1288; CBFS field MAE **0.068 %**; ~30.9 core-min. `ladder-b/B2_duct_baseline.md` |
| **B3** CBFS field inversion, 21,000 cells | SHIPPED | **BLOCKED** | Adjoint GMRES `PetscConvergedReason = -9` at iteration 0, residual `7.091590452305e-04`. Re-measured 2026-08-21 at np=4 **and np=1** — the `-9` persists in serial. `ladder-b/B3/adjoint_unblock_reproduce/RESULTS.md` |
| | PATCHED `dafoam-subpclu:v2`, `DAFOAM_SUBPC_TYPE=lu` | **PASS** | `PetscConvergedReason: 2`, **667 iterations**, every printed residual bit-identical to the 2026-08-04 run, from a rebuilt image 17 days later; the 21,000-component gradient reproduces to every printed digit (`‖g‖ = 1.4558046603e-05`). Same file |
| | PATCHED, **FD re-anchor** and its Charter-2c wrong-step baseline | **PENDING** | The nine registered primal-only points did not land — a 4-rank job pinned to a shared `cpuset` collapsed ~400× under unpinned co-tenants. Re-run priced at **42.6 core-min**. Same file §4, §8 |
| | **minimum intervention** (which lever lifts the `-9`) | **the source change, and nothing cheaper** | Serial (np=1) keeps the `-9`; `-sub_pc_type lu` through PETSc's runtime channel keeps it too, with `PC Object: (sub_) … type: ilu` in the same run's `-ksp_view`. So an upstream fix that only relocates `KSPSetFromOptions` **would look like a fix and would not be one**. Same file §5 |
| | **runtime ILU shift / fill** — `-sub_pc_factor_shift_type`, `_shift_amount` 1e-10 and 1e-8, `_levels 2`, on `dafoam-kspopts:v1` | **BLOCKED, 5 arms of 5** | Measured 2026-08-21. All five return `Total iterations: 0. PetscConvergedReason: -9.`, residual `7.091590452305e-04` to 13 digits, **and every arm's `-ksp_view` dump is byte-identical to the control's**. The proof they were *overwritten*, not merely ineffective: arm L-2 requested fill level 2 and its own dump reads **`1 level of fill`**. **`[NONZERO]` in these logs is NOT evidence the shift landed — it is present in the control, which set no shift option**; the pre-registration flagged that row as non-discriminating before the runs. **5 predictions registered, 5 hit, 0 missed.** Cost **152.53 core-min ledger / 33.7 honest** — arm C alone is 125.60, an 18.5× load-contention artefact. `ladder-b/B3/ilu_shift_runtime/RESULTS.md` |
| | *what the shift arms discriminate* | — | **The pivot pathology is not a small-pivot perturbation problem.** The runtime axis is now closed from both ends: the one factor option DAFoam does *not* set (`zeropivot`, raised six decades to 1e-8 and **verified landed**) does not help, and the ones that might have helped **cannot land**. Ties to `PROOF.md` §25.3: `spilu` returns *"Factor is exactly singular"* at **every** drop-tolerance/fill setting swept, while `splu` always solves. **A perturbation of a singular factor is a different singular factor.** Same file §4 |
| | **decomposition disclosure** — serial np=1 vs scotch vs simple 4×1×1, all PCLU | **PASS on G1/G2/G3/G5, GATE FAIL on G4** | Measured 2026-08-21, reference is **D-serial** not D-scotch (Charter §5). All three converge `reason 2` — **serial 163 it** (predicted <667, band 50–500: the ASM block boundaries cost 4.09× in Krylov count), **scotch 667**, **simple 766**. Gradients, all mapped to serial cell order first: **G1 scotch-vs-serial 1.680861e-04 (0.01681 %)**, **G2 simple-vs-serial 1.415579e-04**, **G3 simple-vs-scotch 1.132033e-04** — all **PASS** (<1e-3), and all landing on the *"invariant at ~1e-04"* the D-B reach matrix predicted for CBFS. **So the S1 line does not inherit a decomposition defect**, and the contrast with A4 (8.95 % → 0.00054 % on the same lever) shows the defect is real but case-selective. **G4 GATE FAIL, recorded as a miss**: objectives are not bit-identical, spread **1.9e-07** — reconvergence noise from a primal that stops on a 1e-06 tolerance at 1580/1582/1584 iterations, not something an ASM choice can cause. **41.17 core-min graded / 69.70 charged / \$0.0596**, 58.1 % of the 120 ceiling; **28.53 core-min waste**. `ladder-b/B3/decomposition_np4/RESULTS.md` |
| | *two harness traps this arm found* | — | **(i) `system/decomposeParDict` is rewritten by DAFoam at every startup** from `daOptions["decomposeParDict"]` (`pyDAFoam.py:1463`, `:2212`), so setting the partitioner by editing that file is **silently ignored** — the first D-simple arm ran `scotch` and came back bit-identical to the reference, which on a case predicted *invariant* is exactly the answer that would have been believed. **(ii) `dRdWColoring_N.bin` is keyed on rank count, not partitioner**, but this one fails **loudly** — `Conflicting Colors Found!`, `DAColoring.C:1021` — a robustness credit to DAFoam. **(iii) Skipping the DV→serial permutation would have turned G2's 0.01416 % PASS into a 141.2 % GATE FAIL** — a factor of 9,977 and a headline-grade false positive. Same file §6, §8 |
| | B3 **Stage 4** (the inversion the rung exists for), shipped | **BLOCKED** | Blocked by construction until the fix ships upstream or Sanaa adopts a forked toolchain. `FAMILY_SUPERVISION_GUIDELINES.md` §3.4 |
| **S1** CBFS inversion line (all on the patched image) | PATCHED | **G1 PASS, G2 FAIL** (re-inversion); **both FAIL** (first inversion) | J_qoi **74.2 %** reduction after the objective repair; G2 **26.9 %** against a >50 % bar. **G2 was then measured at 35.38 % on the baseline gradient alone**, so as defined it scores the sensitivity map, not the closure's error location. `ladder-b/S1_CBFS_{INVERSION,REINVERSION}_RESULT.md`, `S1_SENSITIVITY_VS_ERROR.md` §3 |
| **NASA hump** adjoint | either | **uncharacterised** | Headline 3 **withdrawn as a causal claim** — the run was ended by a `docker stop` at `MemAvailable` 1.62 GB and `hump_sublu_computetotals.log` contains `ConvergedReason` **zero times**. M1+M2 at **40 core-min** are the decisive-cheapest repair and are unbought. `ladder-b/W4_ADJOINT_PC_UNBLOCK.md` §5b.1 |
| **D15** NACA0012 subsonic M 0.288, 4,032 cells (`DARhoSimpleFoam`) | SHIPPED | **GATE FAIL** | `CD` band D 5.0 %/component: 3 of 5 outside, worst **44.87 %** (`shape[6]`); `CL` `shape[6]` 30.07 %. Registered P5 **HIT**. `ladder-a/A1/curriculum_D15/RESULTS.md` (graded 2026-08-27, `5582a5a0`) |
| | PATCHED `dafoam-idwarp-rot:v1` | **PASS** | 5 of 5 in band, 0.0072–1.657 %; `patchV[1]` control identical on both rows, divergence exactly 0.000 %. Item **GATE FAIL**, 10.100 core-min. Same file |
| **D16** NACA0012 transonic M 0.685, 4,032 cells (`DARhoSimpleCFoam`) | SHIPPED | **GATE FAIL** | Fails on **`shape[0]`** at 5.15 % against the 5.0 % band — **not `shape[6]`**, which passes at 1.95 %; `CL` `shape[6]` 41.80 %. **Registered P5 MISS while the row still failed.** `ladder-a/A1/curriculum_D16/RESULTS.md` (`dd9bf92f`) |
| | PATCHED `dafoam-idwarp-rot:v1` | **PASS** | 5 of 5 in band, worst 0.528 % on `CD` (1.630 % on `CL`). Item **GATE FAIL**, 15.935 core-min. Same file |
| **D17** planar wedge M 1.958, 40,000 cells (`DAHisaFoam`, inviscid) | SHIPPED **and** PATCHED | **PASS** on both rows — **but NOT DISCRIMINATING** | First `DAHisaFoam` result in this lab; primal cleared DAFoam's own guard. **The item's worst shipped-vs-patched divergence (2.268 %) is SMALLER than its own patched control row's FD error (2.777 %), S/N 0.82**, so its P5 MISS carries no information about the defect in either direction. 172.833 core-min. `curriculum_D17_cone_supersonic/RESULTS.md` (`e733f5d4`) |
| **D19** NACA0012 **compressible FD-plateau sweep**, phase 1 of 2, M 0.288, 4,032 cells (`DARhoSimpleFoam`), four arms `MESH/X2/S2/S1`, **PATCHED row only by registration** | PATCHED `dafoam-idwarp-rot:v1` | **NO VERDICT OF RECORD — the grader REFUSED, `rc = 2`. A refusal is not a verdict and none is supplied here** | **Why there is no number in this row, in one clause: the comparator refused before it read a single gate.** `D19_phase1_grade_20260831T215400Z.out`: `{"REFUSE": "G1", "detail": {"age_datum_moved": ".../S1/0"}}` — the rule-4 age guard fired on a premise that is false for this solver family (the `patchV` DV makes DAFoam rewrite `0/U` mid-run), so **no gate was evaluated and no grade JSON was ever written**, though `STATUS.D19_chain` names one. **The physics is intact and is not what stopped this**: all four arms `rc=0`, `chain_rc=0`, `G9` toolchain identity OK, and phase 2 correctly never launched (`PHASE1_COMPLETE_PHASE2_NOT_LAUNCHED_NOT_AUTHORISED`). The selector *did* run: `s*` = shape 1e-3 / patchV 1e-2 (level 2), `s_star_score_pct` **21.629866013797557**, binding `shape[7]/CD/fine`, **`all_two_sided_at_s_star` false** — the plateau did not close here either. **8.683 core-min** against 8.7 registered (ratio **0.998**), \$0.00742 derived-not-measured. **CAUSE CLASS `INSTRUMENT`** — assigned by `ladder-a/A1/curriculum_D19R/PREREGISTRATION.md` §2.1–§2.2 (*"the guard refused rather than degrading, which is correct behaviour; it was enforcing a premise that does not hold for this solver family"*). **There is no `RESULTS.md` for this item, at HEAD or on disk**; its records are `docs/COST_CALIBRATION.md` row `C-20260831T223116.831784Z-f2a2dd3d`, that `.out`, and prereg `f032d94e` / instrument `32bd000f` |
| **D19R** the same sweep **re-bracketed at half-decades** with the age datum repaired, six arms `MESH/X2/S8/N2/S1/R1`, **PATCHED row only** (§9) | PATCHED `dafoam-idwarp-rot:v1` | **NO VERDICT OF RECORD — the grader REFUSED, `rc = 2`. A refusal is not a verdict; this is neither a `GATE FAIL` nor a `PASS`** | **Why there is no number: `D19R-GRADER-DEF-1` — as coded the instrument cannot emit a verdict on ANY input.** `D19R_phase1_grade_20260831T230742Z.out`: `{"REFUSE": "G-PROV", "detail": {"verdict_outside_the_fixed_vocabulary": null}}` — `d19r_grade.py:482` calls the provenance enforcer as the first statement of `grade()` on a literal `{}`, thirty lines before composition, so `verdict` is `None`, `None` is not in the vocabulary, and it refuses. **No grade JSON written. The arms are clean and re-gradable**: all six `rc=0`, `chain_rc=0`, `G9` OK on every arm, phase 2 held itself back with nobody alive. **12.416 core-min** against 13.6 predicted (ratio **0.913**), every arm inside its cap. The selector's reading, which is a measurement and NOT a verdict: `s*` level 3 = shape 1e-3 / patchV 1e-2, `score_pct` **21.060684242435336**, binding `shape[7]/CD/fine`, **`all_two_sided` false — THE PLATEAU NEVER CLOSED**, and that unclosed plateau is one half of the registered ceiling that holds D19O and D19M below `PASS`. **CAUSE CLASS `INSTRUMENT`** `[NEW]` — a comparator/reader defect with the physics unjudged; the boarded record words it *"INFRASTRUCTURE, not physics — bookkeeping never voids physics"*, and `INSTRUMENT` is the eight-class token for it, so the class is the supervisor's to ratify. **No `RESULTS.md` and no `docs/COST_CALIBRATION.md` row exist for this item**; its record of verdict is `docs/LAB_STATE.md` update S-23 §2, whose own table cell reads *"no verdict — grader REFUSED, `rc=2`"*, beside `d19r_selected_step.json` and prereg `5a809989` / `7f9c5b6e` |
| **D19R2** the **D19R re-grade** — grading only, **zero solver compute**, no run root of its own | PATCHED (it re-grades D19R's preserved arms) | **`NOT A RESULT`** — grading **attempt 1**, and **no later attempt exists on disk or at HEAD** | **Why there is no number: the grader refused again, `rc = 2`, and the refusal precedes the emit so no grade JSON exists.** `{"REFUSE": "G19R-1h", "detail": {"age_guard": {"REFUSE": "MANIFEST_ENTRY_MUTATED", "path": "system/decomposeParDict", "on_disk_md5": "c3f5f05d…", "recorded_md5": "68ecc827…"}}, "arm": "X2"}`. **The two provenance blockers ARE repaired and the repair held** — execution reached the completion gate, thirty lines past where D19R died — **and the third blocker sits inside a REGISTERED GATE that no successor may narrow.** Triaged and measured: OpenFOAM itself appends `kahipCoeffs` to that dictionary six seconds into each np=2 arm; the mismatch is **exactly one file in exactly the three np=2 arms**, and **151 of 152 manifest entries across six arms are byte-identical** after five days. Three routes are named and **none is taken here: route 1 is gate design, which D19R §5 reserves to Sanaa in terms.** **0.00096 core-min** (0.058 s × 1 rank) against a 2.0 ceiling; **zero solver core-min** — D19R's 12.416 stays charged to D19R. **CAUSE CLASS `GATE-DESIGN`** `[NEW]` — the record's own §5.1 words (*"This is a gate-design question"*); the comparator was correct and the gate as registered pins a path the run writes. `ladder-a/A1/curriculum_D19R2/RESULTS.md` (freeze `7441f392`, graded 2026-09-01, `944e40a8`); artefact `D19R2_phase1_grade_20260901T034416Z.out` in **D19R's** run root. **The record states the item is not complete and that a `COST_CALIBRATION` row is therefore not yet owed** |
| **D19O** NACA0012 **compressible single-point shape optimisation**, M 0.288, 4,032 cells (`DARhoSimpleFoam`), np=1, `CL = 0.5` **constrained** — the first compressible optimisation ever run in this lab | SHIPPED | **GATE REACHED** — `verdict_before_ceiling` **`PASS`**, `capped_by_ceiling` **true** | **THE CEILING IS THE HEADLINE AND IT IS NOT A FAILURE.** Every gate passed; `Optimal Solution Found.` in 13 rows / 12 iters. CD 0.01632675460978398 → 0.01279162168845058 = **−21.6524 %** at `CL` 0.49999946, α 4.0° → **0.795°** with positive camber on all eight `shape` components. Endpoint FD **at the optimum** (the first this lab holds anywhere but iteration 0): aggregate `CD` **0.042993 %**, `CL` 0.017651 %, `G-TB` at h=1e-8 passes as designed with **0 of 4** components in band — the FD instrument is shown able to go red. **It still cannot publish `PASS`, and the reason is inherited, not internal:** the compressible gradient it spends has **no graded verdict** (D19R refused `rc=2`; D19R2 attempt 1 `NOT A RESULT`) and D19R's plateau never closed. **CAUSE CLASS `REFERENT-CEILING`** `[NEW]` — capped, not failed; nothing in the item is a `GATE FAIL`. **THE FINDING IT WAS BOUGHT FOR: `shape[6]`, which the SHIPPED adjoint misses by 44.8738 % at the baseline (D15), agrees to 0.0232 % at the optimum — on this ground the IDWarp defect is a BASELINE-ONLY defect**, because the degenerate-rotation branch is certain at every non-corner node of an *undeformed* mesh and does not fire at a deformed one. **16.184 core-min** against 24.10 (ratio **0.6715**), \$0.013837 derived-not-measured. `ladder-a/A1/curriculum_D19O/RESULTS.md` (graded 2026-09-01, freeze `bb0c5b08`, arming `239fd2ef`) |
| | PATCHED `dafoam-idwarp-rot:v1` | **GATE REACHED** — `verdict_before_ceiling` **`PASS`**, `capped_by_ceiling` **true** | Aggregate `CD` **0.052679 %**, `CL` 0.016953 %; **−21.6501 %** at `CL` 0.50000232, `Optimal Solution Found.` in 10 rows / 9 iters. `G-PLAT7` returns **`NOT A RESULT` on both rows, set from the registered list and never from the measured value** — `shape[7]`'s plateau *does* close at the optimum (0.974 % / 1.061 %) and its magnitude is **28× larger** than at the baseline, and **that licenses a successor registration, not a retroactive promotion.** **How far this may be taken, at its true size: the two rows converged to nearly the same design**, so the endpoint each was evaluated at is nearly the same point — a weaker test of the shipped-vs-patched difference than two distant optima would be, and the record says so on its face. Both aggregates sit **47–58× below** the 2.5–5 % harness-sound floor of `VERIFICATION_CHARTER.md` §7 — **reported, never gated**, and labelled a claim about the harness. Three registered predictions (`P5`, `P6`, `P7`) **MISSED and are recorded as misses** — all three predicted a shipped-vs-patched difference at the endpoint and there is none. **Integrity note carried by the item's own dated §9: `d19o_grade.py:compose_item` tests its hard gates for `GATE FAIL` and never for `NOT A RESULT`** — a fail-open found by its successor D19M and **measured not to have acted here** (all eight hard readings are `PASS` in the frozen grade artefact), so this `GATE REACHED` stands unchanged; not repairable in place because the item has had first compute. Same file |
| **D19M** NACA0012 **compressible α-multipoint** shape optimisation, M 0.288, 4,032 cells (`DARhoSimpleFoam`), np=1, α = 2.787/4.787/6.787°, equal weights ⅓ | SHIPPED | **GATE REACHED** — `verdict_before_ceiling` **`PASS`**, `capped_by_ceiling` **true** | **THE CEILING IS THE HEADLINE AND IT IS NOT A FAILURE.** Every gate passed; IPOPT printed its own `Optimal Solution Found.` (10 iters / 11 rows against `max_iter` 40, cap not reached). Endpoint FD at the optimum: aggregate `J` **0.0465723 %**, `CL` **0.0193471 %** over `shape[0,3,6]`, bands D and E both 5.0 %, zero sign flips, every step **proved two-sided in the plateau**. `G-MP-STRUCT` (dJ vs Σw·dCD, 8 components, rtol 1e-10) worst **4.2547e-12**. `G-TB` at h=1e-8 fails band D on all three (108.6/90.8/50.7 %) — the FD instrument is shown able to go red. **It still cannot publish `PASS`:** the compressible gradient it spends has **no graded verdict** (D19R refused rc=2; D19R2 attempt 1 `NOT A RESULT`) and D19R's plateau never closed (`all_two_sided` false, 21.0607 %). Weighted drag **−25.9848 %** — and **`CL` is UNCONSTRAINED and travels with it**: baseline [0.29875, 0.50000, 0.67366] → **[−0.15775, 0.07176, 0.30495]**, the lift collapsing and going negative at point0. `ladder-a/A1/curriculum_D19M/RESULTS.md` (graded 2026-09-01, freeze `c7d7bf10`) |
| | PATCHED `dafoam-idwarp-rot:v1` | **GATE REACHED** — `verdict_before_ceiling` **`PASS`**, `capped_by_ceiling` **true** | Aggregate `J` **0.0302475 %**, `CL` **0.0186699 %**; `G-MP-STRUCT` worst **7.8671e-12**; `G-TB` 109.7/90.6/52.3 %. Weighted drag **−25.9849 %**, `CL` final **[−0.15737, 0.07216, 0.30540]**. Worst per-component shipped-vs-patched `dJ` divergence **2.190 %** (`k4`) — **reported as measured and NOT read as a two-row agreement claim**: the rows reached two different optima, so the divergence cannot be split into toolchain and design-point terms. `shape[7]` is a **REGISTERED NON-RESULT** excluded by name from every aggregate and published beside it (`J` rel 0.07695 %, plateau 2.9438 % two-sided) — **its plateau closing here corroborates D19O at a second optimum and promotes nothing.** Item **GATE REACHED**, **35.166 core-min** against 34.10 predicted (ratio 1.0313), \$0.030067 **derived, not measured**; birth register 9 readers / 9 born; `G6` `NOT MEASURED`, `GCI_roache` `NOT APPLICABLE`. Same file |

**Two integrity flags on the records above, neither quoted from.** `ladder-a/A1_naca0012_incompressible.md:167-172`
still names a refuted mechanism (`forceMeshWaveFrozen=True`) with zero strike and zero amendment
marker; `ladder-a/A5_ubend_internal.md:194-196` names the in-band component set as {1,2,16,24,25}
where the measured membership at np=4 is {1,2,24,25,26}. Both are frozen records, so both
corrections are the owner's and go in as dated notes.

### 3a. The supervisor's check-3 sweep on the P5 reach claim (2026-08-27)

**This is the DAFoam supervisor's own sweep** (`SUPERVISION_CHARTER.md` §3: verifying a big claim
before believing it is a personal duty and is not delegated), re-derived independently by the lane
that wrote it up. The full text is appended as a dated section at the foot of each of the three
`RESULTS.md` above; this is the map entry.

D15/D16/D17 registered **one** P5 at three Mach numbers — *does the IDWarp rotation defect reach the
compressible solvers?* — and scored **HIT / MISS / MISS**. **The naive reading of that pattern
("bounded to the incompressible path") is wrong, and so is a clean monotone-in-Mach story.**

Signal = worst `divergence_pct = |J_shipped − J_patched| / |J_shipped|` on the adjoint `CD` totals.
Noise = worst **PATCHED**-row FD relative error on the same objective — the common-mode error both
rows share against one FD reference. Both columns are the `CD` channel.

| item | M | worst shipped-vs-patched divergence (SIGNAL) | worst PATCHED-row FD error (COMMON-MODE NOISE) | S/N |
|---|---|---|---|---|
| D15 | 0.288 | **44.878 %** | 1.657 % | **27.1** |
| D16 | 0.685 | **5.487 %** | 0.528 % | **10.4** |
| D17 | 1.958 | 2.268 % | 2.777 % | **0.82** |

1. **The defect PERSISTS into the compressible solvers** — the SHIPPED row `GATE FAIL`s at both
   M 0.288 (`DARhoSimpleFoam`) and M 0.685 (`DARhoSimpleCFoam`).
2. **Its magnitude falls about 8x across that step** (44.878 % → 5.487 %, ratio 8.18).
3. **The component it lands on MOVES** — `shape[6]` at M 0.288, `shape[0]` at M 0.685. **That is why
   P5 read MISS at D16 while the row still failed: P5 was a prediction about a COMPONENT, not about
   the DEFECT, and the registered falsifier was mis-specified.** Carried as `L-352`.
4. **D17 is uninformative and is reported as such** — S/N 0.82, its divergence smaller than its own
   control row's error, its SHIPPED `PASS` resting on `shape[3]` at 4.982 % clearing a 5.0 % band by
   0.018 percentage points. **Its P5 MISS is a statement about D17's FD quality on a shock-containing
   inviscid case, not about the toolchain, and is not evidence of absence.**

**Not overstated.** Three points on three different geometries is **not a Mach sweep**: D17 changes
geometry, FFD block, DV definition, solver class and physics at once. **The D15 → D16 pair is the
only clean comparison — only the Mach number and the solver variant change — and finding 2's 8x is a
statement about that pair and nothing else.** No monotone-in-Mach claim is made; two points cannot
support one. No compute was spent on the sweep: **0.000 core-min**, every number read from the three
grade jsons already on disk.

---

## 4. The standing rules, in one screen

Full text and provenance: `docs/charters/DAFOAM_CHARTER.md`.

| § | Rule |
|---|---|
| 2 | **Every adjoint gradient ships an FD table**, graded PASS ≤5 % with zero flagged components, CONDITIONAL 5–15 %, FAIL >15 % or any sign flip. Name the statistic — **no DAFoam paper uses a vector norm**. Where forward-AD or complex step is reachable, say why you did not reach for it. |
| 3 | **The step sweep runs at the graded run's primal tolerance**, and the plateau is read **per component**, not off the vector. |
| 4 | **The registered trivial baseline for an FD gate is the same probe at a deliberately wrong step**, named in the preregistration before its own run. |
| 5 | **Serial before parallel.** Every parallel gradient discloses its decomposition; an FD reference is never carried across np. |
| 6 | **Two rows, always.** Toolchain identity is an image ID and a library md5 — **a version string is not an identity**. Assert the sub-LU banner and the cold start in the log. |
| 7 | **The memory envelope is predicted and stated before any adjoint launches.** A run ended by memory, or by a human on a shared box, is recorded as such and claims nothing about convergence. |
| 8 | Verdicts are exactly `PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`, only against a **registered** falsifier. |
| 9 | **An optimiser stopped by a wall clock or an iteration cap is GATE REACHED or NOT A RESULT, never PASS.** FD check at the **final design point** is mandatory. |
| 10 | **Upstream filing is Sanaa's alone.** Defect notes are filing-ready and marked NOT FILED on their first screen. |
| 11 | Lessons and numerics ids are **re-derived by command immediately before appending, never quoted from a document** — other teams commit concurrently. Numerics facts go at the **end of the N-B block, not the end of the file**. This lane filed **L-187 to L-194** and **N-D1 to N-D5** on 2026-08-21, then **L-210**, **N-D6** and **N-D7** later the same day (by which time concurrent teams had taken `L-` to **217** — the id was re-derived immediately before each append, never carried) — the `N-D` family exists because `N-B21..25` collided with a concurrent closure-team append the same hour. **`N-D6` is appended at end-of-file rather than after `N-D5`**, and says so in its own text: `NUMERICS_KNOWLEDGE.md` grew **2,555 → 2,732 lines during that single session**, so an in-place insert after `N-D5` would not have been an append-only edit. **Verification standing 2026-08-21: `grep -c 'N-D[1-5]\.'` = 5, each of `N-D1..N-D5` exactly once, `N-B22/23/24` exactly once each (closure team's, untouched).** The only `N-B21` and second `N-B25` strings in the file are both inside **one** line — this lane's own dated note recording the collision — and are a narrative range, not a dangling id, so they are deliberately left in place. |
| 12 | **Every run discloses its cost** in core-minutes and dollars from its own ledger, the prediction is made first and the miss reported as a miss, and anything over \$25 is listed for Sanaa rather than run. |

---

## 5. The images — and there is no such thing as "the fixed toolchain"

All three DAFoam images report **DAFoam 5.0.0, OpenFOAM v2506, PETSc 3.15.5, IDWarp 2.6.2**.
They differ only in the files below. **The hash is the identity; the version string is not.**

| Image | Image ID | Built from | What it carries | Identity |
|---|---|---|---|---|
| `dafoam/opt-packages:latest` | `9d45679d55fd` | — (one imported 7.83 GB layer) | stock everything | `DALinearEqn.C` md5 `f6a89e33b0f4772a0563cb0c8633ac48`, **507** lines |
| `dafoam-subpclu:v1` | `ba2d16ab9d57` | opt-packages, by hand-run `docker commit` in a scratch tree **that no longer exists** | `DAFOAM_SUBPC_TYPE=lu` → ASM sub-block complete LU, **off by default** | md5 `89e71ca2db5d80c06b1eda070ffc7a1b`, **526** lines |
| **`dafoam-subpclu:v2`** | `8352629516bb` | opt-packages, **reproducible `Dockerfile`** | same, plus the B-1 unrecognised-value warning | md5 `5b3159f88dbefcf7c52bd888401d097f`, **539** lines. `diff v1 v2` is **13 lines, all inside a branch neither arm of any recorded run enters** |
| `dafoam-kspopts:v1` | `d9d2aed02e36` | **`dafoam-subpclu:v1`** — so it carries the sub-LU patch too, env-gated and off | `KSPSetFromOptions` relocated from line 138 to line 351 | md5 `96f5762819e33efbdaad34181a214082`, **534** lines, 3 `DAFOAM_SUBPC_TYPE` occurrences |
| **`dafoam-team:v1`** | **`0b3c94c33a15`** (`sha256:0b3c94c33a15cc9b6be48ff1c7e8fa50e870f53d7626bd56b7e173bfd7e9dc1d`) | opt-packages + **both** DAFoam patches, **one committed `Dockerfile`** — `patched_build/team/` | **both levers in one image, both off by default**: `DAFOAM_SUBPC_TYPE=lu` (sub-block complete LU) **and** the relocated `KSPSetFromOptions` | md5 **`920cced7976531836145e08737eb7513`**, **547** lines, **4** `DAFOAM_SUBPC_TYPE` occurrences, exactly **one** `KSPSetFromOptions` call site at **line 364**. Built 2026-08-21, **220 s / 14.67 core-min / \$0.0125** against a registered 55 core-min. **The union is proven, not asserted**: applying the two patches to the stock file on the host passes through md5 `5b3159f88dbefcf7c52bd888401d097f` — `subpclu:v2`'s exact recorded identity — before reaching the image's own md5. **Not the same file as `kspopts:v1`** (534 lines, 3 occurrences, built on `subpclu:v1`), so `kspopts:v1` numbers are not re-attributed to it. **Both smoke gates PASS: G4 — both levers off → stock `-9`, residual `7.091590452305e-04` to 13 digits, primal 1580, no banner; G5 — `DAFOAM_SUBPC_TYPE=lu` → `reason 2`, `667` iterations, `OBJ 1.5279278906359758e-02` and `‖g‖ 1.4558046603e-05 / min -4.694367e-07 / max 1.916019e-06`, every archived digit.** T2 total **49.20 core-min, \$0.0421** against a registered 55. **Caveat: it ends `USER dafoamuser` where every other lab image runs as root, so a bind-mounted staged case needs `--user root`.** `patched_build/team/BUILD.md` §4b |
| **`dafoam-idwarp-rot:v1`** | `2927768a16ac` | opt-packages + the rotation fix | IDWarp reverse/forward `vectorUtils` degenerate-branch fix | **`libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425`** against stock `f0fcb488e0e98156575cd19548e91663`. **Both are 491,344 bytes and both report `2.6.2`** |

Sources: `docs/dafoam/TOOLCHAIN_INVENTORY.md` §3 and §6e; `cases/dafoam/patched_build/{subpclu,kspopts,idwarp_rot}/`.

**Three limits stated rather than discovered.** (i) `dafoam-idwarp-rot:v1` COPYs a prebuilt
`.so`; if `/home/ubuntu/certonomous-runs/W5-patch/idwarp` is lost, the image cannot be rebuilt
bit-for-bit. (ii) **No image combines the two patches**, and none removes the limiter or the
decomposition defect — *"this image is not 'the fixed toolchain'; it is one defect removed."*
(iii) `strcmp(subPCTypeEnv, "lu")` is an exact match, so `LU`, `Lu`, `lu ` or `superlu` all run
stock ILU **with no message** in `v1`: assert the banner in the log or the run is stock.

---

## 6. The unfiled defects — four classes, none filed, Sanaa files

*"Nothing is filed upstream by anyone in this family, ever … filing is Katie's call alone"*
(`FAMILY_SUPERVISION_GUIDELINES.md` §3.6). Both existing bug reports open with
**"Status: NOT FILED ANYWHERE."** **63 recorded searches across 10 venues** found no upstream
report of the ILU-singularity class, so novelty is answered and only the decision is open.

| Class | What it is | Status | Where it would go | Who files |
|---|---|---|---|---|
| **D-A / D-A2** | IDWarp `getRotationMatrix3d` degenerate-rotation branch zeroes `dMi/dnormals` **exactly** at every undeformed baseline; plus the near-threshold `acos` regime, real, measured and **unpatched** | **Root-caused to a line and confirmed by repair.** DOF 0: 210.16 % → **8.56e-06 %** | A comment on **`mdolab/idwarp#57`** — open since 2021-07-14, `bug` label applied 8 seconds after creation, **zero comments in five years** — not a new issue | **Sanaa** |
| **D-B / D-B2** | The parallel reverse-AD adjoint is **not the transpose Jacobian under decomposition** (cross-residual **328.8× ‖b‖** while the KSP converges at 1.7e-07); and the `cellLimited` limiter breaks the tape **in serial too** (A1 np=1, **92.8 %**, one sign flip) | **Subsystem-level, not line-level.** Reproducer on a stock upstream tutorial **NOT DONE**; mechanism-to-a-line **NOT DONE** | `mdolab/dafoam`. The serial limiter case is *"the better entry point for a maintainer: a single-process reproducer with a one-word on/off switch"* | **Sanaa** |
| **D-C** | `DALinearEqn.C:138` calls `KSPSetFromOptions` and then **13 later call sites override it**, so `-ksp_type`, `-pc_type` and `-sub_pc_type` are silently discarded while monitors and viewers still work | **Filing-ready, NOT FILED.** Class **diagnosability** — no wrong answer, an unactionable correct diagnosis | `mdolab/dafoam`. Recommendation revised to fix (a) **plus** an effective-value echo | **Sanaa** |
| **D-E** | The ASM sub-block **incomplete** factorization hits an **exact zero pivot** on wall-resolved separated cases; PETSc's `MAT_SHIFT_NONZERO` cannot catch it because the failure is factor growth, not a small pivot | **Filing-ready, NOT FILED**, with an offline reproducer needing no DAFoam at all | `mdolab/dafoam`; adjacent open threads **#1002**, **#1011** (both 2026-07, users exhausting the documented remedy ladder on official tutorials) | **Sanaa** |

Full note for D-E, drafted so that filing is a decision rather than a drafting job:
`cases/dafoam/ladder-b/B3/DEFECT_NOTE_ilu_zero_pivot.md`. Reports for D-A and D-B:
`cases/dafoam/UPSTREAM_BUG_REPORT_{mesh_warpDeriv,decomposition_adjoint}.md`. Candidate for
D-C: `cases/dafoam/DEFECT_CANDIDATE_ksp_options_override.md`.

**Two community reports were tested and closed** rather than claimed: `mdolab/dafoam` **#905**
reproduces but its cause is the FD step, not this lab's defect, and **#914** is not reproducible
from the information given. Both were resolved upstream and both earlier lab characterisations
were **withdrawn** (`cases/dafoam/W5_COMMUNITY_REPORTS_TESTED.md`).

---

*Nothing in this lane has been filed, sent, uploaded, registered or pushed. No container image
has left this box.*
