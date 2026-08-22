# LAB_STATE — the resume board

**This file is the only handoff channel between sessions.**

Agent teams do not survive a compaction, a session switch or a crashed terminal.
Nothing about a live agent is persisted anywhere else: not its brief, not what it
had read, not what it was part-way through. The session scratchpad is **not** a
handoff channel — it was wiped three times in one day and only the things already
in the repository survived (L-186). A repository document never cites a scratch
path.

So: **what is not on this board is lost.** Each supervisor owns its own section
and updates it **at every commit and at every verdict** — not at the end of a
turn, because the end of a turn may never arrive.

**How to read it.**

- Anything marked **VERIFY** was not confirmed by the writer at the time of
  writing. Treat it as a lead, not a fact.
- The board can be stale. `/form-teams` and `/lab-state` both take a live reading
  beside it (`git log`, `ps aux`, `readlink /proc/<pid>/cwd`) and **the reading
  wins**. A correction belongs to the supervisor who owns the section, not to
  whoever noticed.
- Verdict vocabulary only: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
  BLOCKED / PENDING.**

**Board populated 2026-08-22T18:05Z at HEAD `a5605f54` by the harness build.** It
was assembled from git log, the campaign index files, the charter records and a
live process reading. Every section below is a first fill by a third party, not by
the team that owns it; each supervisor should correct its own section on its first
commit. **HEAD moved six times during the two hours this board was assembled** —
re-derive rather than trust the shas below.

---

## CHIEF — standing directives in force

**The chief is the GLOBAL SUPERVISOR and never solves.** It routes and relays.
First action every session: read this board, run `/form-teams`, report the roster
to Sanaa. Sends are reserved to Sanaa.

| # | Directive | Source | State |
|---|---|---|---|
| **THERMAL BUILDUP DIRECTIVE (H-1 … H-7)** | DC-cooling is the destination; capacity priority behind only R4's CPU-minutes | Sanaa, recorded verbatim 2026-08-22, `docs/campaigns/T-family/THERMAL_BUILDUP_DIRECTIVE.md` | **IN FORCE**, ledger live in that file |
| H-1 | Vogel & Eaton (1985) unblocks T3's gate rows; confirm T5's primary status | same | (a) **NOT on disk** — repo-wide search, zero hits. (b) T5 primary **HELD**, sha256 re-verified |
| H-2 | DC spine order inside the T-family: **T3 → T5 → T8 → T12 → K2 rack row**; everything else interleaves | same | **IN FORCE**; index reordered, old order retained as superseded |
| H-3 | T10a follow-through, two arms: (a) ceiling refinement, (b) view-factor quadrature characterisation → upstream candidate #4 | same | both **PENDING**, lanes dispatched, preregs not yet written |
| H-4 | T9a 2.4 mK interface miss: diagnosis arm, **one change per run** | same | **EXECUTED** — T9a-D REPORTED 2026-08-22, prereg + results on disk (D454, L-227); cause is the interface scheme |
| H-5 | Tier order after the spine: T4, T6, T7, T2, T9b/c, T10b, T11 | same | queued behind the spine; nothing started ahead of it |
| H-6 | Every thermal gate feeds the DC certificate spec as it passes | same | `docs/product/DC_CERTIFICATE_TEMPLATE.md` created |
| H-7 | Two institutionalizations: bands-vs-corrections caveat into the charters verbatim; the libs lesson as law | same | **BOTH DONE** — VERIFICATION_CHARTER §2e (v1.10), CLOSURE_MODELLING §22.4 (v1.1.2); `scripts/foam_libs.py` + `lint_foam_libs.py` |
| **R3 = SpaRTA** | The closure line rebuilds on SpaRTA-class, Sanaa's pick from the R2 shortlist | Sanaa 2026-08-21, verbatim *"R3: Sparta"*, appended to `docs/closure/R2_SHORTLIST_MEMO.md` | **DECIDED** |
| **R4 approved** | Sanaa said *"R4 approved"* in the same message | same | **APPROVED**; R4 build **OPEN, no verdict** |
| **R4's CPU-minutes have first call on capacity** | named in the thermal directive's own header | Sanaa 2026-08-22 | **IN FORCE** |
| **SUBMISSIONS PARKED** | Nothing is sent, filed, uploaded, registered or posted anywhere. Sending is Sanaa's alone | Katie 2026-08-07; `GOALS_AND_PROPOSALS` §8, `CLOSURE_MODELLING` §19, `DAFOAM` §10 | **IN FORCE**, indefinitely |
| **Blanket compute approval** | Runs above the $25 pre-authorisation are blanket-approved, **and are still costed in their pre-registration** | Sanaa 2026-08-21 (owner-supplied; not found in the repo — **VERIFY**) | **IN FORCE** |
| **No GPU** | AWS quota denied, case 178725840000468. GPU work is recorded **BLOCKED-GPU** | owner-supplied; case number and the token `BLOCKED-GPU` appear **nowhere in the repo** — **VERIFY** | **IN FORCE** |

**Lab-wide live compute:** 12 single-core solvers, all `buoyantBoussinesqSimpleFoam`,
all owned by heat-transfer. At $0.0513/core-h that is **~$0.62/h** while all 12
run. No other team has anything on the box.

**On Sanaa's desk, aggregated:** the T10a view-factor defect as upstream candidate
#4 (filing is hers); **K2a rack row module, awaiting her approval**; four DAFoam upstream defect classes, all `NOT FILED`; the
`RESULT_PRIORITY_CHARTER` orderings (v0.5 draft, awaiting her ruling); the
`GATE FAIL` vs bare `FAIL` ledger-vocabulary conflict (referred, unruled); and the
D389 S13 normalisation question (re-grades the whole thermal corpus; no single
rung may take it).

---

## closure

**Last commit:** `fd3aa735` — *The train_log.json that three records called
nonexistent is committed, and the five places that said so now carry a dated
correction* (2026-08-22 18:03Z). This section refreshed **2026-08-22T18:19Z**;
repo HEAD at that moment was `b8647a74` (dafoam's section fill), so closure is
six commits behind the tip and none of the intervening commits is this team's.

**Live jobs:** the **R4 build lane is LIVE** and owns everything closure has on
the box — 9 processes, all read from `ps` and `/proc` at 18:19Z, no log states an
ETA for any of them.

| pid | what | cwd | started | ETA |
|---|---|---|---|---|
| `803458` | `closure-venv/bin/python fs3_select.py --cases <12 cases>` — **FS3 selection running**, detached (`ppid 1`), ~161 % CPU | `/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/R4_sparta_build` | 18:16:45Z | **unknown** — no log line states one. `/home/ubuntu/closure-data/r4/fs3.log` holds one line, `[R/prop/seed 0] terms=['T1','I1*T1','I2*T1','I2^2*T1'] cv_mse=43.5533 PZ=PASS`; `fs3/fs3.json` (8,281 B, 18:16Z) does not parse as JSON — it is being written |
| `805854` | `bash ./run_aposteriori.sh` — the a-posteriori driver | `R4_sparta_build` | 18:18Z (01:20 elapsed) | **unknown** |
| `805886` `805899` `805901` `805902` `805907` `805911` `805941` | 7 × `simpleFoam`, one per arm | `/home/ubuntu/closure-data/r4/aposteriori/{AR_1,AR_3,AR_5,AR_10}_Ret_180/{null,ceiling}` | 18:17:04Z | **unknown** |
| `809577` | `simpleFoam` | `/home/ubuntu/closure-data/r4/aposteriori/CBFS13700/ceiling` | 18:17:16Z | **unknown** |

`/home/ubuntu/closure-data/r4/aposteriori/driver.log` holds one completed row,
`[done rc=0 11s] AR_1_Ret_180/ceiling`; `build_manifest.json` covers 12 cases
× {null, ceiling}. `frozen/` holds 27 case directories plus `inventory.json`,
`build_manifest.json` and `driver.log`; the three spot-checked (`AR_1/3/10_Ret_180`)
each carry `rc=0` and a written time directory.

**The two R4 `kCorrectiveFrozenFoam` probes at `/home/ubuntu/closure-data/r4/`,
against the strict completion rule.** Reported for the R4 lane; **this section
decides nothing about them.** The board's earlier line — *"`ktestA` wrote `rc=0`
with no time directory beyond `0/` — VERIFY"* — was read at 17:49Z and is now
superseded: `ktestA` finished writing at 17:51:02Z.

| check | `ktestA` | `ktestB` |
|---|---|---|
| `rc` file | present, `0` | present, `0` |
| `End` line in `log.frozen` | yes (1), preceded by `ExecutionTime = 111.81 s` | yes (1), preceded by `ExecutionTime = 34.41 s` |
| last time dir | `20000` | `5000` |
| `endTime` in `system/controlDict` | `20000` | `5000` |
| last time dir == `endTime` | **yes** | **yes** |
| every field at `endTime` newer than `0/` | **yes** — `0/` written 17:49:14Z, all nine `20000/` fields 17:51:02Z | **yes** — `0/` written 17:49:14Z, all nine `5000/` fields 17:49:43Z |
| fields at `endTime` | `U bijData bijDelta k kDeficit nut omega phi tauij` + `uniform/` | same nine + `uniform/` |
| `ExecutionTime` count == `endTime` | **no — 1 line against 20000.** This solver writes one `ExecutionTime` and no `Time = ` lines at all; the iteration-count clause of the rule is a T-family log-format criterion and **does not transfer as written**. Flagged, not ruled |
| same | **no — 1 line against 5000**, same reason |

Every clause that applies is satisfied by both probes. Whether the
`ExecutionTime`-count clause binds a `kCorrectiveFrozenFoam` log is **the R4
lane's call, not this section's.**

**Rungs lacking verdicts:**

| rung | state |
|---|---|
| **R4** (SpaRTA build) | **R4 build lane LIVE, no verdict.** `cases/RANS_LES_closure_models/R4_sparta_build/PREREGISTRATION.md` exists (2026-08-21, D443, with a dated 2026-08-21 addendum A1/A2) and there is still **no `RESULTS.md`**. The lane has since written 10 more files there — `r4_lib.py`, `assemble_dataset.py`, `build_frozen_cases.py`, `build_aposteriori.py`, `fs3_select.py`, `score_apriori.py`, `score_aposteriori.py`, `run_frozen.sh`, `run_aposteriori.sh`, `__pycache__/` — **all still untracked** (`git ls-files … \| wc -l` → **0**; `git status --porcelain` → `?? R4_sparta_build/`) |
| **R5** (round-5 diagnostics as build constraints) | **no verdict artefact.** Partly discharged by the FS2/FS5 report; the R4 prereg does not cite R5 by name |
| **R6** (surfaces updated) | **NOT DONE.** "leaderboard" still appears in `web/closure.html` and `web/benchmarks.html`; **BLOCKED** on Sanaa approving the internal-scoring phrasing (doctrine open action 4) |
| **FS3** (selection methods) | **FS3 selection RUNNING, no verdict.** Registered in R4 prereg §3 — mutual information, permutation importance, elastic-net path, leave-one-**family**-out CV, top-20 Spearman agreement reported as a number. `fs3_select.py` live since 18:16:45Z over 12 cases; first output line written, nothing graded |
| **FS4** (joint iteration, features frozen before scoring) | **NOT RUN.** Registered in the R4 prereg §4 |
| **FS6** (comparative feature document) | **NOT DONE.** No artefact exists |

R1 closed (charter §22.1–22.5). R2 delivered (`R2_SHORTLIST_MEMO.md`; ranking
inverts the doctrine's order — SpaRTA, FIML-C, TBNN). R3 decided by Sanaa.
**FS1 done** (110 features, 40 cases, 641,652 cells). **FS2 and FS5 are STANDING
GATES** — permanently re-armed, never closed.

**Case verdicts on record:** Wu2018 a-priori **PASS** (7/8, loses `NASA_2DWMH`);
Wu2018 aposteriori and aposteriori_frozenk both **NOT A RESULT** (ceiling gate
failed, registered falsifier fired); Ling2016 **GATE REACHED** *(note:
`docs/closure/README.md` §3 still lists it PENDING — a known, flagged
disagreement)*; Kaandorp2020 **GATE FAIL** on all three preregistered claims,
Table 4 **BLOCKED**; Schmelzer2020_SpaRTA **PASS**; Xiao2016_EnKF **BLOCKED** at
the forward model; NASA_hump_gate **PASS** on the registered branch (B-G0a
BLOCKED, B-G0b PASS).

Two additions, both from tonight and neither moving a verdict:

- **`CBFS13700` LES `x_reatt`: the number of record is 4.241**, from the registered
  instrument `_common/sst_baseline_metrics.py::hill_wall_metrics` (linearly
  interpolated crossing, 4.240983). **4.170** (4.169625) is the *same*
  reattachment read at cell-centre resolution — the last still-reversed cell in
  row `j = 0` — low by **0.435 of one cell** (cell width 0.163947 there). Not a
  disagreement: two read-off criteria. `Wu2018_PIML_RF/aposteriori_frozenk/
  RESULTS.md` §4 is internally consistent because all four of its figures
  (`L_ml` 3.022, `L_null` 3.350, LES 4.170, `L_truth` 9.088) are row-`0` cell
  centres, so its `NOT A RESULT` verdict and fired falsifier stand untouched.
  **4.170 must not be differenced against 4.241, 4.384 (Kaandorp `TRUTH+R`) or
  5.891 (SST) without conversion** — those three are interpolated crossings.
  Full reconciliation: that file's `## RECONCILIATION` section; the
  `R2_SHORTLIST_MEMO.md` line carrying 4.170 was annotated at `074f60da` and the
  memo's ordering and its 16 %/137 % comparison are unaffected.
- **Kaandorp2020 outstanding rows: 3 BLOCKED, 6 PENDING** (dated NOTE in
  `Kaandorp2020_TBRF/aposteriori/RESULTS.md`; §1–§10 and the 2026-08-21 addendum
  untouched, no verdict moved). Zero of the nine qualifies under the strict
  completion rule — **none of the nine has a case directory anywhere on this
  host**, and `results.json` still holds the same 10 runs. `AR_3_Ret_360__ML0/1/2`
  are **BLOCKED** on a missing input: `/home/ubuntu/closure-data/kaandorp_tbrf/
  features_nodurbin.npz` carries 27 cases and `AR_3_Ret_360` is not one of them,
  which killed the detached driver four times with `ValueError: 'AR_3_Ret_360' is
  not in list`. The six `CBFS13700` rows (`NULL TRUTH MEANB ML0 ML1 ML2`) are
  **PENDING** only because they sit after the blocked row and the exception
  aborted the loop; every input they need is present. `run_lane.py` now raises a
  named `RowBlocked` and records `status: "BLOCKED"` in `results.json` instead of
  taking the loop down — **repaired, `py_compile` clean, NOT RUN.**

**Commits tonight** (closure lane, in `git log` order, newest first):

| sha | one line |
|---|---|
| `fd3aa735` | `Kaandorp2020_TBRF/train_log.json` committed — the file three records called nonexistent was merely untracked; five records gain a dated correction. **Also corrects `074f60da`/L-225's overstatement that "the whole `Kaandorp2020_TBRF/` directory is untracked": 19 files there were tracked, and `train_log.json` was the only untracked non-`__pycache__` file at any depth.** No number changed |
| `074f60da` | Follow-up, read-only: the `R2_SHORTLIST_MEMO.md` 4.170 line annotated; the "3.24" pointer found **on disk but untracked** (`basis_rank_mean = 3.2374`) and both records re-sourced with the *statistic* named (3.24 pooled-sample vs 3.738 case-mean); the nine Kaandorp rows costed and graded **3 BLOCKED / 6 PENDING**, $0.226 for all nine. Nothing launched |
| `5162ec8e` | The libs lesson as law (`docs/closure/LIBS_ASSERT_SWEEP.md`): 92 mentions, 75 writes, **8 library-load call sites — 3 already asserted, 4 newly asserted, 1 superseded by a concurrent lane's helper, 67 template lines n-a**. `frozen_R.py:69` was carrying the **live** defect. L-222, L-223, D448. Zero compute |
| `c46309f5` | `CLOSURE_MODELLING_CHARTER.md` **v1.1.1 → v1.1.2**: §22.4 gains the bands-vs-corrections caveat **verbatim** from L-220/D446, four additive requirements. *(This is the commit whose tree came from a stale `read-tree` — see `a5126378`.)* |
| `a5126378` | Content-only restore of the **nine** `eda10f39` files that `c46309f5` silently reverted; every blob byte-identical, no number changed. The charter lane's two files left standing |
| `eda10f39` | Closure reconcile: nine uncommitted closure edits closed out (`make_feature_library.py` regenerates `FEATURE_LIBRARY.md` byte-identically; `setup_case.py` L-221 pattern; four `LESSONS_DRAFT.md` banners; two `RESULTS.md` sweeps) and the **4.170 / 4.241 split ruled a read-off criterion, not a disagreement** |

**Next actions:**

| # | action | note |
|---|---|---|
| 1 | **R4 verification table + boundary report** — the lane is live and has no `RESULTS.md`. Every arm needs the strict completion rule applied row by row, and the report must state the boundary between what the build lane produced and what it inherited | the two `ktest` probes above are the first two rows |
| 2 | **Get `R4_sparta_build/` tracked** — 11 files + `PREREGISTRATION.md`, `git ls-files` returns **0**. The 2026-08-20 `tbrf.py` overwrite is what untracked closure directories cost | do not sweep the directory; name the files |
| 3 | **Kaandorp six `CBFS13700` rows, when load permits** — `NULL TRUTH MEANB ML0 ML1 ML2`, 3.40 core-hours, **$0.175** at $0.0513/core-h (the nine-row figure is $0.226; hard upper bound $0.462 for nine under `timeout 3600`). **Not launched: R4 holds first call on capacity** | serial, `nProcs : 1` |
| 4 | **Rebuild `features_nodurbin.npz` to include `AR_3_Ret_360`** — this is the single missing input that makes the three `AR_3_Ret_360__ML*` rows BLOCKED rather than queued | unblocks 3 rows |
| 5 | **Interpolated rescore of the six frozen-k §4 arm fields** — read-only, fields already on disk, minutes, no solve. It puts §4 on the registered interpolated basis so its numbers can be compared with 4.241/4.384/5.891. **Belongs to the lane that owns the grade**, not to the reconciliation that flagged it | explicitly left undone by `eda10f39` |
| 6 | **Reconcile `docs/closure/README.md` §3** — it lists Ling2016 **PENDING**; `Ling2016_TBNN/RESULTS.md` reads **GATE REACHED** (with a 2026-08-20 correction note). The same README flags two further integrity defects in that file: a stale §0 `GATE FAIL` line and a seed-count self-disagreement | one of the two must move |

**On Sanaa's desk:**

| item | why it is hers |
|---|---|
| **R6's internal-scoring phrasing** — approve it, or confirm leaderboard claims are dropped | doctrine open action **4**, owner **SANAA**. R6 is BLOCKED on it |
| **Repo 2 creation and every release into it** | doctrine open action **5**, owner **SANAA**. *"DO NOT create or push Repo 2"* — the doctrine records it and creates nothing |
| **The zero-shot scoring call** | scoring-call authorisation is reserved to Sanaa (lab constitution, FIRST-ACTION RULE). R4 prereg §0 carries the zero-shot discipline and a declared prior-exposure leakage risk; addendum A1 moves `NASA_2DWMH` to *checkable-at-the-scoring-call* |
| **`CLOSURE_MODELLING_CHARTER.md` is now v1.1.2** — to note | `c46309f5`: §22.4 amendment, four additive requirements, no clause widened or narrowed. `ls docs/charters/*_CHARTER.md \| wc -l` still returns 12 |
| **Three defects in `scripts/lint_foam_libs.py`, flagged to its owner, not repaired by this team** | (i) `--include-closure` does not widen the walk — it only lifts a skip for roots passed explicitly, so run bare it walks `verification/runs` only while printing `closure tree: INCLUDED`; (ii) it does not see the canonical asserted `re.sub` idiom as a write (`setup_case.py:109` reports *"libs mentioned, no write route matched"*, `frozen_R.py` is invisible); (iii) `scripts/foam_libs.py` was untracked at sweep time, so a closure builder importing it would break on checkout. Full text: `LIBS_ASSERT_SWEEP.md` §6 |

**Blocked:** R6, on Sanaa's internal-scoring phrasing. Kaandorp
`AR_3_Ret_360__ML0/1/2`, on the missing `AR_3_Ret_360` case in
`features_nodurbin.npz`. Xiao2016_EnKF, at the forward model. Kaandorp Table 4
(BFS5100), no such case on disk.

**⚠ Standing hazard in this tree — RE-READ 18:19Z, and it has mostly cleared.**
Of the four paths the board listed as *staged deleted while existing untracked*
(residue of the `c46309f5` → `a5126378` stale-base episode, L-223), **all four are
now tracked and clean at HEAD**: `NASA_hump_gate/` (**4** files, identical in
`git ls-files` and `git ls-tree HEAD`), `_common/uq_eigenspace/` (**4**),
`docs/closure/HUMP_BASELINE_EQUIVALENCE_NOTE.md` (**1**),
`docs/closure/LIBS_ASSERT_SWEEP.md` (**1**). `git status --porcelain` reports
nothing against any of them. **The one live exposure left is
`cases/RANS_LES_closure_models/R4_sparta_build/`, still wholly untracked** while
the lane writes into it — a blind `git checkout`, `reset --hard`, `stash` or
`clean` destroys R4's working code. Inspect, never revert. (Phantom `D ` entries
elsewhere in `git status` are the shared index being stale, not deletions; the
whole-tree `git status` also shows foreign `D `/` M` rows belonging to other
teams — closure touched none of them.)

**Compute:** 487 core-hours pre-authorised (charter §18). Above it, stop and cost
it. Live under this team right now: 8 serial `simpleFoam` a-posteriori arms plus
`fs3_select.py` (~1.6 cores observed) ≈ **9.6 cores**, ≈ **$0.49/h** at
$0.0513/core-h — **reported-by-owner rate, not measured**, and the elapsed spend
is not yet ledgered because the lane has written no `RESULTS.md`.

## dafoam

*Refreshed 2026-08-22T18:20Z by the DAFoam supervisor (Fable), replacing the harness
build's third-party first fill. Live reading: `git log`, `docker ps`, `docker inspect`.*

**Last commits (newest first):**

| sha | committed (UTC) | what |
|---|---|---|
| `79679a84` | 2026-08-22 18:10Z | *A2 per-component table* — zero compute. **PATCHED `CD/shape` carries a sign flip at idx46** (analytic `+2.27367571e-06` vs FD `-2.52460969e-06`) that `A2/grading_confirmation/RESULTS.md` §1 says does not exist; SHIPPED `CD/shape` has 7/96 components beyond 15 % (worst idx18 `-360.75 %`) under a 1.71 % aggregate. All published aggregates reproduce to 7-8 s.f. Log-integrity defect: MPI ranks splice `check_totals` arrays mid-number on one stdout; 1 of 4 printed CD copies usable, 0 of 4 CL copies |
| `8028d9ab` | 2026-08-22 18:09Z | *A6 N=16 fixed FD reference — pre-registration*: two stages on `dafoam-idwarp-rot:v1`, np=1; P1 predicts the 1e-8 primal gate FAILS at 6000 iters (residual flat from iter 100); forward-AD reachability probed (`libDASolverADF.so` carries `DARhoSimpleCFoam`, 28 symbols); 74.0 core-min registered, 120 ceiling |
| `a5605f54` | 2026-08-22 18:03Z | *A3 rung2 patched-IDWarp arm — pre-registration* (np=4, 42,120 cells, ceiling 120 core-min); staged and pre-flighted (0.200 core-min), **holding at its launch gate** (load ≤ 8 never met; min seen 20.40) |
| `804c3fd8` | 2026-08-21 | Phase 3B (final): ILU-shift class measured dead, `dafoam-team:v1` built and gated, B3 free of the decomposition defect |

**Live jobs (reading 18:17Z; both np=1, `--cpus=1`, launched under a disclosed
launch-condition amendment because the T-family holds 12 of 16 cores until
2026-08-23..26):**

| container | host pid | run root / cwd | item | ETA |
|---|---|---|---|---|
| `p3a6_s1b` | 802799 | `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/s1b` | A6 N=16 fixed reference, Stage 1 (primal-convergence gate + forward-AD probes), `--memory=12g` | Stage 1 ~20-40 min; Stage 2 contingent, ~1.5 h |
| `p3a4_opt` | 796052 | `/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/opt` | A4 shipped-image optimisation twin + endpoint FD, `--memory=8g`, prereg **VERIFY** committed — not yet seen in `git log` | ~15-25 min |
| *(none)* | — | `/home/ubuntu/certonomous-runs/P3-a3-rung2-patched/` | A3 rung-2 patched arm, np=4 — **driver polling, nothing launched**; window expires ~19:47Z | blocked by load |

**Rungs lacking verdicts:**

| item | state |
|---|---|
| **A3 patched column** | **PENDING at every size.** Prereg at `a5605f54` is np=4 and cannot launch while the box is saturated (np=4 MPI measured 18-21x inflation under contention). Decision pending: re-register at np=1 (shipped + patched twins) by pre-compute amendment, or hold |
| **A6 N=16 adjoint correctness** | **PENDING** — Stage 1 live. Prior verdict GATE FAIL both images on a noise-dominated FD reference (floor 4.5e-3, 8/9 components below it). N=29 stays NOT RUN (gate not met) |
| **A4 shipped column at the optimised design** | **PENDING** — live |
| **A2 `CD/shape` PATCHED** | aggregate 0.0506 % PASS now carries a **per-component sign flip (idx46)** — under the band ("ANY sign flip ⇒ FAIL") the row needs the per-component caveat A5 idx16 got; supervisor to record in `LADDER_A_STATUS` addendum + docket. Whether adjoint or FD artefact: NOT established (a sweep costs 207-238 core-min on A2; not bought) |
| **B3 Stage 4** | **BLOCKED by construction** — Sanaa's fork-adoption call. The rebuild rows are final: BLOCKED (shipped) / PASS (`subpclu:v2`, 667 iters, FD 0.085/0.059/0.199 %, decomposition G1-G3 PASS) |
| **W4 / NASA hump adjoint** | uncharacterised; M1+M2 at 40 core-min unbought |
| **B3 decomposition peak RSS** | NOT MEASURED (no 5 s watcher on that chain) |

**Two-row verdicts standing** (shipped / patched): A1 GATE FAIL / PASS; A2 PASS / PASS
with the idx46 caveat above, optimisation NOT A RESULT; A3 primal GATE REACHED, adjoint
BLOCKED (399k) — sweep rungs 1-2 PASS, rung 3 GATE FAIL (conditioning) / PENDING;
A4 PASS / PASS (first passing optimisation, CD −7.478 %); A5 GATE FAIL / PASS;
A6 BLOCKED (full) — N=16 GATE FAIL / GATE FAIL (reference). B2 PASS; B3 BLOCKED / PASS.

**Next actions:** (1) grade A4 twin and A6 Stage 1 as they land; A6 Stage 2 only if its
registered gate passes. (2) Resolve the A3 np=4 launch: pre-compute amendment to np=1
twins if the T-family holds the box past the poll window. (3) Supervisor docs commit per
verdict: `LADDER_A_STATUS` dated addendum, L-225+ (re-derive), D453+ (re-derive), N-D8+.
(4) Then: B3 decomposition RSS watcher re-run (cheap), W4 M1+M2 (40 core-min).

**On Sanaa's desk:** four upstream defect drafts, all **NOT FILED** (D-A/D-A2 IDWarp
rotation; D-B/D-B2 decomposition + limiter; D-C ksp options override; D-E ILU exact zero
pivot) — filing is hers alone. Fork-adoption decision for B3 Stage 4. Note for her: the
A2 per-component extraction shows the third near-zero sign-flip-under-a-passing-norm
(A1 idx6, A5 idx16, A2 idx46) — a class, not an incident.

**⚠ Integrity flags on frozen records, none quoted from:**
`A1_naca0012_incompressible.md:167-172` (refuted mechanism, zero strike);
`A5_ubend_internal.md:194-196` (in-band set {1,2,16,24,25} vs measured {1,2,24,25,26});
`A2/grading_confirmation/RESULTS.md` §1 ("no sign flip anywhere in A2") falsified at
PATCHED idx46.

**Images:** `dafoam-idwarp-rot:v1` (only image carrying the rotation patch, md5
`85f59e87…`), `dafoam-subpclu:v2` (PCLU), `dafoam-kspopts:v1`, `dafoam-team:v1`
(`0b3c94c33a15`, both patches, ends `USER dafoamuser` → `--user root` for bind mounts).
*The hash is the identity; the version string is not.* F6 series under `cases/dafoam/`
is plain `simpleFoam`, not DAFoam work.

---

## heat-transfer

### T-family (thermal) — refreshed 2026-08-22 by the T-family lane (supervisor)

*This is the T-family (thermal) lane's section. Refreshed in place rather than
duplicated: the board's convention is one section per team, and this team is the
T-family/thermal one. Everything below replaces the harness build's first fill.*

**Last commits (newest first):**

| sha | committed (UTC) | what |
|---|---|---|
| `037abab8` | 2026-08-22T18:03:02Z | *T3 ext1: ladder extended from `latestTime` on convergence state alone (**D452**); 8 extensions running, `R_f` ETA 2026-08-25* — this commit is what put `T3_EXT1_AMENDMENT.md` on disk in git |
| `fd831c11` | 2026-08-22T17:53:19Z | *Thermal Buildup Directive recorded; T3 NOT A RESULT 4/4; charter §2e; DC certificate template; libs helper+lint* (**D449–D451, L-224**) |
| `89231930` | 2026-08-22T17:38:42Z | **merge** of `origin/main` — Sanaa's paper uploads `ddd2d75b`, `c99bce64`, `ad110f9d`; **no Vogel & Eaton among them** |

**Ordering, disclosed not smoothed:** the eight T3 ext1 extensions launched at
17:51:43–46Z, i.e. **11 min 19 s before** `037abab8` committed the amendment that
registers them; and `fd831c11` (17:53:19Z) *cited* `T3_EXT1_AMENDMENT.md` in the
directive and the T-family index for **9 min 43 s before** the file itself was
committed. The pre-launch guarantee rests on the on-disk write order — §1's
timestamped 17:41:39Z precondition check (no `log.solve.ext1` anywhere, rc = 2),
§5's cost and §6's predictions, all written before launch — not on the commit
time. Frozen-artifact sha256s were unchanged across the interval (7 of 8
byte-identical; the 8th traced in §13 to another lane's commit, not this one).
Full record: `T3_EXT1_AMENDMENT.md` **§14**.

**Live jobs — 12 solvers, all this team's, all single-core
`buoyantBoussinesqSimpleFoam`.** Reading taken 2026-08-22T18:05Z. **Do not touch
them.**

*T1b L4 arms, running since 2026-08-21:*

| pid | cwd (under `verification/runs/T-family/T1_runs/`) | iteration | endTime | ETA |
|---|---|---|---|---|
| 442445 | `R_300k_x` | 15402 | 80000 | ~2026-08-26 06–08Z |
| 450274 | `R_100k_x` | 15348 | 80000 | ~2026-08-26 06–08Z |
| 488219 | `R_30k_x` | 14454 | 80000 | ~2026-08-26 06–08Z |
| 503891 | `R_10k_x` | 14236 | **20000** | **~2026-08-23 01:40Z** |

*T3 ext1 extensions, launched 2026-08-22 ~17:53Z:*

| pid | cwd (under `verification/runs/T-family/T3_runs/`) | iteration | endTime |
|---|---|---|---|
| 754946 | `R_c` | 24076 | 80000 |
| 756428 | `R_m` | 20793 | 36000 |
| 757934 | `R_f` | 20185 | 78000 |
| 759476 | `P_m` | 20792 | 36000 |
| 761058 | `C_lam_m` | 21294 | 80000 |
| 762535 | `W_m` | 29317 | 80000 |
| 763872 | `D_m` | 21364 | 28000 |
| 764454 | `O_m` | 20458 | 46000 |

`R_f` is the critical path: ETA **2026-08-25T14:54Z** (amendment §10.4, 68.9 h
≈ 2.9 days); the other seven finish earlier and their individual ETAs are
**VERIFY** — not recomputed at this writing. The launched-before-committed
ordering noted above is now written up in full as **§14 of the amendment**
(appended 2026-08-22), with the rule the lane takes forward: commit the
pre-registration before launching what it registers. **Note `R_10k_x` carries `endTime
20000` where its three siblings carry 80000** — intended per the L4 design, or a
mismatched triple? **VERIFY before the triple is graded**, because Roache gating
turns on exactly this.

**Rung verdicts on record:**

| rung | verdict |
|---|---|
| **T1c** laminar pipe (EXACT) | **GATE FAIL 3/4** — 3 of 4 graded rows pass, 1 fails; the L4 row is NOT A RESULT |
| **T1b** turbulent pipe (FORMULA) | **PASS ×4 as returned by the frozen comparator — but every grid triple DIVERGENT or STAGNANT** (D440). Until the L4 arms land, the four Nu rows **carry no mesh-converged value** |
| **T1a** turbulent flat plate | **BLOCKED** — reference held, but no band can be armed from one correlation |
| **T3** heated BFS (the spine's first rung) | **NOT A RESULT 4/4** — gates (1)/(2) of prereg §7.1: no case at 1e-6, triples DIVERGENT/OSCILLATORY. Primary (Vogel & Eaton 1985) **NOT OBTAINED** — necessary, not sufficient, and **not today's binding constraint; the ladder is.** **ext1 running** (D452), 8 extensions, critical path `R_f` ETA **2026-08-25T14:54Z**; a still-non-CONVERGING triple stays NOT A RESULT |
| **T9a** composite wall / fin (EXACT) | **GATE FAIL** — 2 of 3 graded rows pass; interface 1 misses by **2.4 mK** against a 0.92 mK GCI band; 2 fin rows GATE REACHED below the 0.025% O(Bi) floor; 4 controls MET (D442). **T9a-D interface diagnosis arm REPORTED 2026-08-22 (D454, L-227)** — the interface scheme is the whole of the 2.41 mK: `Gauss harmonic` removes it to round-off at every level (A1 PASS, drop 8.15e+08) while a fourth level leaves the triple STAGNANT and a band armed there would be 11× too wide; C1 GATE FAIL, the error **grew** 27–31× at 40× contrast. `gate_t9a.json` unchanged, no T9a row moved; T9a's own verdict stays GATE FAIL. `T9aD_RESULTS.md`, committed in the T9a-D commit of 2026-08-22 (sha in the Last-commits table above) |
| **T10a** view-factor enclosures (EXACT) | **GATE FAIL** — 3 of 4 box rows PASS, ceiling fails 0.125% against a 0.077% band; **both sphere rows NOT A RESULT** on DIVERGENT triples; outer-sphere row-sum defect 4.3–4.8%, non-converging under fixed quadrature; 12 controls MET, 6 UNMEASURED (D447). **T10a-R ceiling refinement arm IN FLIGHT** |
| **T4** impinging jet | **half-open** — ERCOFTAC case025 held, Martin correlation held, but Nu uncertainty is **second-hand** (2.4%, KB Wiki quoting Baughn & Shimizu). Report-only enabled; graded rows need the closed ASME primaries |
| **T5** heated cubes (the rack physic) | **PRIMARY HELD** — Meinders 1998 TU Delft thesis, open, title-page verified, sha256 `36c89a54…`, stated uncertainty 5% mid-face / 10% edges. **Pre-registration draft IN FLIGHT**; primary stays **HELD** and the graded rows wait on it. Cost registration rides with the draft |
| **T2, T6, T7, T8, T9b/c, T10b, T11, T12, T13** | not started. T6/T12/T13 and likely T7, T9c are **over $25** |

**F14 / DC-cooling ladder** (records in `docs/campaigns/F14-cooling-ladder/`, run
trees in `verification/runs/F14-cooling-ladder/`):

| rung | state |
|---|---|
| **K0c** laminar | **PASS** |
| **K0cS**, **K0cT**, **K0cX** | **GATE FAIL** |
| **K0b** | D403 rerun and D406 repair both have prereg + results; **VERIFY** the verdicts |
| **K0cG / K0cP / K0cQ / K0cR** | prereg + results on record; **VERIFY** the verdicts |
| **K2a** rack row module | **awaiting owner approval** — on Sanaa's desk |
| **K2b** | **cost VOID** — the recorded cost basis does not stand; re-cost before any successor cites it |
| **K2e**, **KV1** | run trees present; **VERIFY** against their records |

**Next actions** (the directive's own order, H-3a/H-4/H-3b): 1. T10a ceiling
refinement arm — **T10a-R in flight**. 2. T9a interface diagnosis, one change per
run — **T9a-D REPORTED 2026-08-22 (D454, L-227)**; the successor is a re-graded T9a
under a new pre-registration with `Gauss harmonic`. 3. T10a view-factor quadrature characterisation —
prereg not yet written. Then T5 — **prereg draft in flight**, primary held.

**On Sanaa's desk** (T-family lane, 2026-08-22):

- **Vogel & Eaton (1985) purchase, ~25–40 USD** — the paper is still not on disk
  and H-1 assumed it was; the figure is a **recollection, not a quote** and needs
  confirming before it is spent. Obtaining it is **necessary and not sufficient**
  for T3's graded rows; it is not today's binding constraint (the ladder is).
- **T5 draft INTERPRETATIONs** — for her when written; the prereg draft is in
  flight and the primary (Meinders 1998) stays HELD until she rules.
- **T1b L4 cost: 10.54 USD registered against ~5 USD approved — and the arms are
  running.** The overrun is on the record, not on the future; the four solvers
  are live (see the pid table above) and were not stopped on this lane's own
  authority.
- **T10a's view-factor defect as upstream candidate #4** — filing is hers alone.
- **K2a (rack row module) awaits her approval.**

**Blocked:** T1a (no band from one correlation); T3's graded rows on the missing
primary *in addition to* the ladder; T4's graded rows on closed ASME primaries.

**⚠ D389 is open and deliberately unrepaired:** S13 normalises peak-to-peak spread
by the **mean**, which on an absolute temperature is ~24× looser than it reads.
Changing it moves verdicts across the whole thermal corpus (K0c's eleven, K2e's
thirty, KV1's three). **No single rung may take that decision.** Owner: chief.

---

## cfd

**Last commit:** `cc4f1a64` — *Twenty-six dead paper paths in forty files…*
(2026-08-18 17:54Z). **This lane has been idle four days** while the other four
committed today.

**Live jobs:** none.

**Standards — and these are two documents, not two copies.** `docs/standards/MESH_STANDARD.md`
(**v1.2, 2026-08-11**) carries the **quality gates**; `docs/MESH_STANDARD.md` carries
the **grid families**. They are complementary and neither supersedes the other, so
do not "reconcile" them into one. Read both. Also `docs/OPENFOAM.md` — **stale; it
describes the phase-1 adapter** — and `docs/OPENFOAM_SOLVER_BUILD.md`.

**Open run families (lacking verdicts):**

| family | why open |
|---|---|
| **DPW8_V2** | *Status: SALVAGE.* L4 fine gate rung **INCOMPLETE — not gated**; `run_L4_gate.stdout.log` is **0 bytes**. Two lower rungs PASS |
| **F5b** | the run dir is **exactly one file**, `run_pitch.py`. No case tree, no logs |
| **F5c** | headline **withdrawn to *unmeasured***. The 1.313 H attributed to SIMPLEC was **RELAXATION** — misattributed. Chief-approved **Stage B was never run** |
| **R4** (Ahmed turn) | *n = 2 of a planned 4*; leg-2: *"No SIGNAL/NOISE verdict is claimed."* Plus a withdrawal record. **Note: this R4 is the Ahmed-body draw series, NOT the closure team's R4 SpaRTA build** |
| **GEN_ALT** | measured, never written up, and **no solve ever ran** — mesh only. Both meshes breach non-orthogonality (70.13 / 70.11 > 70) |
| **F12** | pre-registration only; `F12_runs/` is just `reference/` |
| **F7a re-gate** | spec frozen, unexecuted |
| **MODEL_FORM successors** | three preregs, no results |
| **mbc_retry, uq_batch** | *"Nothing here is graded."* |
| **F4** | SWBLI θ=32.5°/35° gate cases *"NOT yet built or run"* |
| **F5** | 1e5 and 1e6 ladder rungs have no run tree |

**Closed, verdicts on record:** 4G, B52_RUNG6 (REPRODUCE), D5_rsm (SSG and LRR
bracket the DNS; *which* RSM is right is not settled), DMR, F2 (PASS banded), F3
(PASS), F8 (**NO VERDICT — and that is the result**), F9 (PASS quasi-steady, gate 2
stays FAIL vs Womersley), F11 (GATE REACHED), FPE_DIAG (SHARED-BY-CLASS, recorded
only by citation from its successor prereg), MESH_AUDIT, W1, W1_hump, W2_sparta,
W3.

**⚠ Structural fact this team must know:** with five exceptions, the run dirs under
`verification/runs/` carry **no README, RESULTS, PREREG or DONE marker at all**.
**The verdicts live one level up, in `verification/campaign/*.md`.** Do not
conclude a family is ungraded because its run directory is bare.

**Next actions:** reconcile the two MESH_STANDARD copies. Decide DPW8_V2 L4 —
finish the gate rung or record it as abandoned with a reason. Write up GEN_ALT,
which is measured and unpublished.

**On Sanaa's desk:** nothing currently.

**Blocked:** nothing currently identified.

**⚠ VERIFY:** `verification/runs/W2_sparta_runs/setup_sparta_case.sh` has mtime
**2026-08-22 17:38** and shows `MM` in git status — the only non-thermal file
touched under `runs/` in three days. **Find out who did that before assigning W2.**

**Case tree:** `cases/{committee-grids, demo-surfaces, hlpw6, mega-batch, tmr,
unsteady-cylinder, valve}` is **dormant in git** — none is the subject of a recent
commit. **`tmr` is the most open of them**; **`mega-batch` has a broken driver
path** (it points into `demo-output/website/...`, and stale paths of that shape are
**systemic** across this team's records — treat any such citation as suspect until
resolved). `models/tmr/**` deliberately holds solver cases outside a run tree, a
documented `FILING_CHARTER` §3 exception: *the rule was wrong, not the tree.*

---

## verification

**Last commit:** `fd831c11` — *T-family: Thermal Buildup Directive recorded; T3
NOT A RESULT 4/4; charter 2e; DC certificate template; libs helper+lint
(D449-D451, L-224)* (2026-08-22 17:53Z).

**Live jobs:** none.

**Charters owned:** `VERIFICATION_CHARTER.md` **v1.10, 2026-08-22** (§2e appended
at the foot on Sanaa's H-7 directive, L-219/L-220 verbatim, zero lines moved
above); `RESULT_PRIORITY_CHARTER.md` **v0.5 — a DRAFT**, whose orderings are
proposals awaiting Sanaa's ruling.

**Open items:**

| item | state |
|---|---|
| **VM2026R1_Fluids** (Ansys verification suite) | **UNTRACKED, and unpacked TWICE** — at the repo root `VM2026R1_Fluids/` and under `docs/papers/verification_validation/VM2026R1_Fluids/`, both mode 700, both dated 2026-08-22. Holds `VM2026R1_FLUENT_ARCHIVES` and `VM2026R1_CFX_ARCHIVES`. **Decide the canonical home under FILING_CHARTER R6/R8 and say which copy is authoritative before grading anything from it.** Nothing graded yet |
| **Ansys Fluid Dynamics Verification Manual** | on disk at `docs/papers/verification_validation/`, 8.5 MB, **PDF with no `.txt` sidecar**. `FILING_CHARTER` R8 requires the pair — *a PDF and its sidecar always travel together* |
| **`GATE FAIL` vs bare `FAIL`** | charter §2 says `GATE FAIL`; `scripts/check_verdict_cells.py --strict-fail` counted **4 ledger cells** reading bare `FAIL`. Both defensible, neither touched. **Referred for a ruling, unruled** |
| **Comparator freeze audit** | `scripts/check_comparator_freeze.py` first pass found **two of six frozen** — *"the honest baseline this rule starts from."* The other four are unaudited since |
| **The six standing audits** | `DEAD_LEVER`, `EXTERNAL_REFERENT`, `FAIL_OPEN_GATE`, `H4_ALLOCATION`, `LEDGER_HEADLINE`, `SWEEP_REFRAME`. None re-run since 2026-08-16 — **VERIFY** |

**Freshness flag:** nothing under `verification/campaign/`, `certificates/`,
`credibility/` or `monitor/` has been written since **2026-08-18 17:40** — four
days.

**Cross-team gate audit — this team's standing mandate.** Open any other team's
rung and ask: could this gate have failed (§2a identity test); was the comparator
frozen before its cases could answer it (§2d); were the controls **fired** rather
than described. Current highest-value targets, from the other four sections:

- **T1b's four `PASS` rows sit on triples that are every one DIVERGENT or
  STAGNANT** (D440). The rows are PASS as the frozen comparator returned them and
  carry no mesh-converged value. That is the sharpest live instance of the rule
  this team owns.
- **T10a** has 6 controls **UNMEASURED** and a 2d.1 zero-referent repair disclosed.
- **A4's two rows are measured at different design points** — so the shipped/patched
  comparison the DAFoam charter's bright line requires has never actually been made.
- **Wu2018 aposteriori** returned NOT A RESULT with the registered falsifier fired
  — check the falsifier was the pre-registered one and not re-read after the fact.

**Next actions:** rule on the VM2026R1 canonical home and get it tracked or
explicitly gitignored. Produce the missing `.txt` sidecar for the Ansys manual.
Re-run `check_comparator_freeze.py` across all six.

**On Sanaa's desk:** the `RESULT_PRIORITY_CHARTER` orderings (v0.5, *"still need to
think abt how to go abt this"*); the `GATE FAIL`/`FAIL` vocabulary ruling.

**Blocked:** nothing currently identified.
