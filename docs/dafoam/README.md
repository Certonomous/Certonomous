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
| | PATCHED | **PENDING** everywhere | *"No patched-IDWarp arm was ever run on A3, at any mesh size … not clean-by-omission."* Same file |
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

**Two integrity flags on the records above, neither quoted from.** `ladder-a/A1_naca0012_incompressible.md:167-172`
still names a refuted mechanism (`forceMeshWaveFrozen=True`) with zero strike and zero amendment
marker; `ladder-a/A5_ubend_internal.md:194-196` names the in-band component set as {1,2,16,24,25}
where the measured membership at np=4 is {1,2,24,25,26}. Both are frozen records, so both
corrections are the owner's and go in as dated notes.

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
