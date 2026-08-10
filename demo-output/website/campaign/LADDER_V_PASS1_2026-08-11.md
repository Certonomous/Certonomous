# Ladder V — PASS 1, RE-DERIVATION, re-executed on Katie's dispatch (deliverable dated 2026-08-11)

Protocol: `LADDER_V_TRIPLE_VERIFICATION.md`. Prior passes:
`LADDER_V_RUNGS_V1_V3_V4_V5_2026-08-08.md` (`9a21d65c`) and
`LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` (`49f71b8c`).

**These five rungs are RE-RUN, not cited.** The five verdicts below were produced by
executing the checks again today against current artifacts. Nothing here rests on the
2026-08-08 record; where this pass reaches the same conclusion, it reaches it from the
evidence, and where it does not, the difference is stated as a finding.

**Why re-run at all — the lab's own L-39.** A verdict is stale the moment a later commit
touches its evidence. Two commits since `9a21d65c` did touch Pass-1 evidence
(`cf6a0477`, `18120bf8`), so the 2026-08-08 verdicts were formally stale on their face
and had to be re-derived rather than re-read.

**Clock note (clock-audit discipline).** Execution ran 2026-08-10 **20:38–21:0x UTC**
(`date -u` at start and at close). The dispatch and this filename are dated 2026-08-11;
the deliverable is named as dispatched, and the machine clock is recorded here rather
than silently reconciled. Machine timezone is `Etc/UTC`, so every timestamp in this
document is UTC without conversion.

**MODEL-RULE OVERRIDE, stated not silent (SUPERVISION_CHARTER §5).** This pass ran on
**Opus**, not the Closure/UQ family's designated tier, because that tier is
credit-exhausted. Recorded here on the deliverable's face so a later reader knows which
model produced these verdicts.

**Scope discipline — Pass 1 only.** Rungs V6–V13 belong to Passes 2 and 3, which run
concurrently by other agents. Nothing below touches them. No agent verifies work it
produced: this executor produced none of the round-5 artifacts — not the QCR
implementation, not the rule freeze, not the solves, not the pre-registration, not the
scoring call, and not the surfaces.

---

## FRAME (stated before any count, per the binding discipline)

**What was examined.** The eight round-5 submission CSVs on disk; the two frozen
external checkouts re-cloned at their pinned commits; the surviving run tree
`/home/ubuntu/certonomous-runs/w3-qcr-rank1/` (5 arms); the round-5 machine records;
`R5_RULE_FREEZE.md` and `R5_PREREGISTRATION.md`; the two gate scripts in `sdk/scripts/`;
the QCR source, its Make files and the built `.so`; the full git history of every one of
those paths; and a text sweep of 920 `.md`/`.html`/`.json`/`.tex` files under
`demo-output/website/`.

**What was NOT examined.** The `.tex` beyond a Spalart-token count; `docs/PRODUCT_LIST.md`;
any surface outside `demo-output/website/` for the citation sweep (so the citation counts
below are a **lower bound on gaps**, not a corpus total); the cover email and description
document (Pass-2 territory, and unpark-bound); the four PH training pipelines beyond the
21-case gate fit; and any submission channel — nothing was prepared, assembled, or sent.

**Positive controls carried.** Every negative finding in this report is accompanied by a
planted-decoy or bit-flip control proving the instrument that returned the null could see
the thing it reported absent. Three of my own instruments over- or under-matched during
execution and are disclosed at the point of use rather than quietly fixed.

**Artifacts this pass created, and what reads them.** Everything written by this pass
lives under the session scratchpad (`.../scratchpad/a1/`, `/a3/`) — a venv, two git
clones, three regenerated CSVs, and one JSON of reproduced gate decisions. **Nothing in
the repo, no build, no page, and no other agent reads any of them**; they are deleted-safe
and are not referenced by this document except as provenance. The only artifact this pass
adds to the repo is this file, which is read by the Ladder V status ledger and by the V13
close-out.

---

## THE SCORING-CALL DISTINCTION, stated up front because it is load-bearing

Rung A1 recomputes the round-5 scores **offline**, with the benchmark's own scoring code
installed into a scratchpad venv outside the repo. **This is NOT a scoring call against
the lab's pre-registration ledger.** The prediction set re-scored is the identical,
hash-frozen, already-scored set of the 6th pre-registered call (2026-08-07, `07a7fe9e`);
no new prediction exists, no model decision hangs on the output, and the only thing the
recomputation can decide is PASS/FAIL of this verification rung.

**The ledger counts distinct prediction sets scored. It stood at 6 before this pass and
stands at 6 after it.** At no point did this pass need to run the scorer against new
predictions; had that need arisen, the instruction was to STOP and record why, and it did
not arise. The scorer in the lab's own environment was never invoked — the only
invocation was in the scratchpad venv, against bytes that were already scored on
2026-08-07.

---

## A1 — CLEAN-ENVIRONMENT RE-SCORE: **PASS** — re-verified today, not a digit moved

### The clean environment (all under the session scratchpad, outside the repo)

| element | value |
|---|---|
| interpreter | system `python3` **3.12.3**, fresh `python3 -m venv` |
| eval package | installed from a **fresh clone** of `/home/ubuntu/closure-challenge-pkg` checked out at `1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162`, working tree clean (0 modified paths) |
| **pinned package version recorded** | **`closure-challenge==0.3.1`** (pip metadata) |
| benchmark | **fresh clone** of `/home/ubuntu/closure-challenge-benchmark` at the frozen commit `deb91557184af3cb95f5190494ec52d8f2c6a0d1`, working tree clean |
| numpy | **2.5.2** |
| scipy / Ofpp (byte-compare leg only) | 1.18.0 / 0.12 |
| ground truth | the package's own bundled `data/ground_truth_test.npz` at the pinned commit, sha256 `6f28b512…e30d80` |

**Environment delta since 2026-08-08, disclosed:** the 08-08 pass recorded **numpy 2.5.1**;
a fresh install today resolves **numpy 2.5.2**. Every score below is bit-identical across
that patch bump, which strengthens the rung rather than weakening it — the numbers are not
resting on one pinned BLAS-adjacent build.

### Recomputation — `evaluate_from_csv_by_case` + `score_from_csv` on `demo-output/website/closure_challenge_submission_round5/test/`

Compared against `closure_challenge_round5_qcr.json`'s `round5_per_case_full` /
`round5_overall_full`, by `repr()` equality **and** by IEEE-754 byte equality:

| case | recomputed (fresh venv, today) | recorded (6th call, `07a7fe9e`) | repr-equal | bit-equal |
|---|---|---|---|---|
| alpha_15_13929_4048 | 0.05010529499681675 | 0.05010529499681675 | YES | YES |
| alpha_15_13929_2024 | 0.10111218200472648 | 0.10111218200472648 | YES | YES |
| alpha_05_4071_4048 | 0.04610779144551565 | 0.04610779144551565 | YES | YES |
| alpha_05_4071_2024 | 0.07186293244687289 | 0.07186293244687289 | YES | YES |
| AR_1_Ret_360 | 0.04547044480564218 | 0.04547044480564218 | YES | YES |
| AR_3_Ret_360 | 0.039982156323801255 | 0.039982156323801255 | YES | YES |
| AR_14_Ret_180 | 0.035338619029087186 | 0.035338619029087186 | YES | YES |
| NASA_2DWMH | 0.0631981125812468 | 0.0631981125812468 | YES | YES |
| **OVERALL** | **0.056647191704213645** | **0.056647191704213645** | **YES** | **YES** |

**Not a digit moved.**

**One instrument defect, mine, disclosed.** My first comparator compared
`repr(np.float64(x))` against `repr(float(y))` and printed **DIFFER on all nine rows** —
a false alarm caused entirely by the numpy scalar's `np.float64(...)` wrapper, not by any
digit. Corrected to compare `float()` reprs plus raw IEEE bytes. Recording it because a
comparator that cries wolf on a clean set is exactly as dangerous as one that stays quiet
on a dirty one.

**A refinement the 08-08 record slightly over-stated.** That report said "the overall also
equals the recomputed mean of the 8 per-case values exactly". It does — under `np.mean`,
under `math.fsum/8`, and under sequential summation **in the recorded case order** (all
give `0.056647191704213645`). It does **not** under sequential summation in the scorer's
own dict-iteration order, which returns `0.05664719170421365` — one ULP away. The identity
is real but order-conditional, and a later reader re-deriving it in a different order
should not read the last digit as drift.

### Byte-compare against the prediction files the solves actually wrote

Done the strong way: the three duct CSVs were **regenerated from the raw solve artifacts**
in the clean venv — `Ofpp` parse of `{case}_qcr/{t}/U` from the run tree, cell centres
`data/DUCT/{case}/constant/C` and evaluation coordinates
`data/evaluation_points/{case}_points.csv` from the **fresh `deb91557` clone**, scipy
`NearestNDInterpolator`, `np.savetxt(fmt="%.10g")` — with **no scoring-package function
imported**:

| file | regenerated from | cells | regen sha256 | committed sha256 | verdict |
|---|---|---|---|---|---|
| AR_1_Ret_360.csv | `395/U` | 3025 | `bb8d61fb…` | `bb8d61fb…` | **BYTE-IDENTICAL** |
| AR_3_Ret_360.csv | `1956/U` | 8748 | `c567ff25…` | `c567ff25…` | **BYTE-IDENTICAL** |
| AR_14_Ret_180.csv | `8947/U` | 31819 | `286610c0…` | `286610c0…` | **BYTE-IDENTICAL** |
| 5 non-duct CSVs | round-5 vs round-4 `test/` | — | — | — | all 5 **BYTE-IDENTICAL** to the round-4 files they claim to be |

And all eight on-disk sha256 were harvested and matched **programmatically** against both
`R5_PREREGISTRATION.md` §3 and `closure_challenge_round5_qcr.json`: **8 of 8 present in
both**.

**Positive control for the byte comparator.** One bit was flipped in a scratch copy of
`AR_1_Ret_360.csv`; `filecmp.cmp(shallow=False)` returned **False** and the sha256
differed. The comparator that reported "identical" nine times can see a single-bit change.

**Verdict A1: PASS — re-verified today.** Same pinned package `0.3.1` @ `1c4e22c8`, same
frozen benchmark `deb91557`, all 8 per-case scores and the overall reproduced to the last
bit under a *newer* numpy, duct CSVs regenerated from raw fields byte-identical, five
unchanged CSVs byte-identical to round 4. Offline re-derivation of already-scored,
hash-frozen bytes. **Ledger unchanged at 6.**

---

## A2 — PRE-REGISTRATION CHAIN AS A TABLE: **PASS** — re-verified today, and strengthened

Method: `git log --format='%h %cI %s'` on the round-5 artifact paths, re-run today; solver
log **headers** and `ledger.txt` from the surviving run tree; hashes recomputed on disk.

### The chain (all times UTC; machine TZ verified `Etc/UTC`)

| # | artifact | commit | timestamp | ordering proof |
|---|---|---|---|---|
| 1 | `campaign/R5_RULE_FREEZE.md` — the criterion that judged the solves: V1 (QCR/SST scaled-MAE ratio ≤ 0.70), V2 (in-plane r ≥ 0.85), V3 (both arms stop on `residualControl`), all-or-none, AR_14 loss accepted in writing, per-case `endTime` caps | `0bade54a` | 2026-08-05 **17:41:06** | precedes every solve below |
| 2 | AR_7_Ret_180 **QCR** validation solve | — (run tree) | log header `Date: Aug 05 2026 / Time: 17:41:36`; mtime 17:46:44; wall 308 s | started **30 s after** the freeze commit |
| 3 | AR_7_Ret_180 **SST** validation solve | — (run tree) | log header `Time: 17:41:36`; mtime 17:47:01; wall 325 s | started **30 s after** the freeze commit |
| 4 | AR_1_Ret_360 QCR **test** solve | — (run tree) | log header `Aug 07 2026 / 20:01:13`; mtime 20:01:22 | 2 days after the freeze |
| 5 | AR_3_Ret_360 QCR **test** solve | — (run tree) | log header `20:01:36`; mtime 20:03:01 | after the freeze |
| 6 | AR_14_Ret_180 QCR **test** solve | — (run tree) | log header `20:01:13`; mtime 20:26:03 | after the freeze |
| 7 | `campaign/R5_PREREGISTRATION.md` + `R5_validation_AR7.json` + the **8 staged CSVs** + `closure_challenge_round5_qcr_forward.json` — accept criterion (overall < 0.065438), expectation band (0.059–0.0666), AR_14 risk statement, §3 SHA-256 table | `e865076b` | 2026-08-07 **20:38:52** | after every solve, **before** the scoring call |
| 8 | 6th scoring call record — `closure_challenge_round5_qcr.json`, round-5 `MANIFEST.json`, status/board updates | `07a7fe9e` | 2026-08-07 **20:51:51** | last; **12 m 59 s** after the pre-registration |

**Strengthened relative to 2026-08-08.** That pass *inferred* the AR_7 start times from
`wall_s` subtraction ("started ≥ 17:41:36"). The OpenFOAM log headers state the start
directly — `Date : Aug 05 2026 / Time : 17:41:36` — and the two derivations agree to the
second. The ordering no longer depends on an arithmetic inference.

**Two tamper checks the rung needs and this pass added.**

1. `git diff --stat e865076b HEAD -- .../closure_challenge_submission_round5/test/` is
   **empty**: the eight prediction files have **not changed by one byte since the moment
   they were pre-registered**, through the scoring call and through everything since.
2. `R5_RULE_FREEZE.md` has **exactly one commit in its entire history** (`0bade54a`) — the
   criterion has never been edited, not once.

**One disclosure the chain requires.** `R5_PREREGISTRATION.md` **is not single-commit**: it
was appended to at `9a21d65c` (2026-08-08) by the previous Pass-1 executor, adding a
6-line dated Spalart citation note. Verified today: the change is **purely additive** (199
→ 205 lines, all 6 at the end, `@@ -197,3 +197,9 @@`), and the §3 SHA-256 region is
**byte-identical** to its `e865076b` state. The chain is intact. Flagging it anyway
because `cf6a0477`'s own commit message (2026-08-10) declares R5_PREREGISTRATION untouchable
*precisely because* V2 passed on it — while an earlier Ladder V rung had already appended
to it two days before. **Two Ladder V executors applied different freeze rules to the same
artifact.** No harm done here; the chief may want one rule.

### 6th call vs its pre-registration: **MATCH**, clause by clause

| pre-registered (`e865076b`) | the call's record (`07a7fe9e`) | verdict |
|---|---|---|
| accept iff overall < 0.065438 (§5) | `verdict.accept_criterion` = "overall < 0.065438 (R5_PREREGISTRATION.md section 5)"; `measured_overall` 0.056647191704213645 → `ACCEPT` | MATCH |
| expectation band 0.059–0.0666 (§5) | `expectation_band_prestated` "0.059-0.0666"; landed below it, "recorded, not celebrated" | MATCH |
| exactly ONE scoring call, made by the supervisor's designee, not the producing session (§5) | `scoring_calls.this_run` = 1, `cumulative_distinct_prediction_sets_scored` = 6, `made_by` = "the supervisor's designated scoring agent, 2026-08-07, per the pre-registration's reservation of the call" | MATCH |
| all-or-none: 3 ducts QCR, 5 CSVs byte-identical to round 4 (§3) | `changed_cases_sha256` **n = 3**, `unchanged_cases_sha256` **n = 5** | MATCH |
| §3 SHA-256 table, 8 files | recomputed on disk today: **all 8 present in §3 and in the record** | MATCH |
| AR_14 risk accepted in writing; any regression reported, not reverted (§4, §5) | `the_AR_14_risk_statement_scored`: risk materialised (0.0324698 → 0.0353386, +0.0029), tie lost, 3 of 5, best-on-board 5/8 → 4/8, explicitly **not reverted**, bundle judged as bundle | MATCH |

No clause was added, dropped, or re-thresholded between `e865076b` and `07a7fe9e`.

**Verdict A2: PASS — re-verified today**, with the AR_7 ordering upgraded from inference
to a logged start time, and two new tamper checks (CSVs byte-frozen since
pre-registration; rule freeze single-commit).

---

## A3 — LEAKAGE ASSERTIONS EXECUTED, NOT READ: **PASS** — re-verified today

Driver: `.../scratchpad/a3/a3_live.py`, run in the lab venv. **The guard was armed before
any case was touched and proven armed and still armed at exit.**

### (0) the armed guard

**17** scoring/truth entry points were stubbed with a raising stub across
`closure_challenge`, `closure_challenge.dataset_utils` and `closure_challenge.eval`
(`score`, `score_from_csv`, `evaluate_by_case`, `evaluate_from_csv_by_case`,
`evaluate_individual_case`, `_velocity_field`, `_ground_truth`, `_load_csv_predictions`,
`evaluation_points`). `cc.score_from_csv()` was then **called and proven to raise** before
the first case was opened, and **called again at exit and proven to still raise**. No
scoring entry point was reachable at any point in the run. *(The 08-08 pass recorded nine
stubs; the same nine names resolve to 17 bound attributes across the three modules — same
surface, counted per-attribute rather than per-name.)*

### (a) the assertion block, run live

`sdk/scripts/closure_baseline_error_gate.py` lines **84–86** (module level), executed
three ways in one process:

1. **by importing the module** — which runs the block; import succeeded, so all three
   asserts passed;
2. **by re-executing the three asserts verbatim** — `len(_PH_TRAIN)==21 and
   len(_PH_VAL)==4` → 21/4; `train ∩ val` → `set()`; `(train ∪ val) ∩ test` → `set()`;
3. under the armed guard, with the test list printed to show what it is:
   `['alpha_15_13929_4048', 'alpha_15_13929_2024', 'alpha_05_4071_4048',
   'alpha_05_4071_2024']` — imported **solely** to assert non-intersection.

### (b) NEGATIVE CONTROL — three injections, all fire

| injection | result |
|---|---|
| a **test** case injected into TRAIN | `AssertionError` **RAISED** |
| a **test** case injected into VAL | `AssertionError` **RAISED** |
| a val case duplicated into TRAIN (count violation) | `AssertionError` **RAISED** |

All three fire. The assertions are executable and load-bearing, not decorative. *(The
08-08 pass carried one injection; this pass carries three, covering both the intersection
asserts and the cardinality assert independently.)*

### (c) §4.1's line citations, re-cited against CURRENT code

§4.1 lives in `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` at lines **262–286** (heading at
262; §4.2 at 288) — re-cited here, **not edited there** (Katie's send package).
`cf6a0477` inserted 18 lines into that file on 2026-08-10, but at line ~1073, **below**
§4.1, so §4.1's own position is unmoved. Both gate scripts are unchanged since
2026-07-31 (`fe121af2`) and 2026-07-28 (`5719374e`) respectively.

| §4.1 claim | §4.1 cites | **actual, HEAD today** | still holds? |
|---|---|---|---|
| `_load_ground_truth_U` inside `for case in gate._PH_TRAIN` | line 115 | **line 128**, loop at **126** (`# 21 cases, train only`) | **YES** — train-only loop |
| test-case loop calls `ph._load_rans_fields` only, annotated `# no U_LES read` | lines 165–167 | loop at **178**, annotated call at **179** | **YES** — features only |
| `_load_ground_truth_U` inside `for c in ph._PH_TRAIN` | line 215 | **line 228**, loop at **225** | **YES** — train-only loop |
| gate split asserts in `closure_baseline_error_gate.py` | quoted, unnumbered | **84–86** | **YES** — executed live above |
| *(completeness, not in §4.1)* duct ground truth `ext._load_duct_ground_truth_U` | — | **line 264**, inside `for case in ext._DUCT_TRAIN` at **262** | training ducts only |

**Line numbers have NOT shifted since 2026-08-08** (128 / 178–180 / 228 / 84–86 / 262–264
then and now). An exhaustive grep of the file's 421 lines finds **no other ground-truth
read**.

**Standing defect, re-raised not fixed.** §4.1 *as written in the draft* still cites the
pre-`fe121af2` line numbers (115, 165–167, 215). Every **claim** holds; every **citation**
is off by +13. The 08-08 pass deliberately re-cited in its own report rather than edit
Katie's send package, and this pass does the same — but the draft is an outward-facing
artifact, and a reviewer who opens line 115 will find the wrong line. **Reported to the
chief for a ruling on who edits the send package.**

### (d) the four test-case gate decisions, reproduced from train-only inputs

Full STAGE-1/STAGE-2 pipeline re-run under the armed guard: features and baseline targets
from the 21 train cases only → screening → top-3 → RidgeCV → train-LOO median threshold →
frozen model evaluated on the 4 PH test cases' RANS-only features.

- ground truth read for **exactly 21** cases; **`set(truth_reads) ∩ set(test)` = `False`**
- top-3 screened (train-only Pearson r): **`p90_I4_W2S` (−0.7579), `frac_backflow`
  (−0.5912), `p90_I3_S3` (−0.5785)** — matches record
- RidgeCV **alpha = 0.7499** — matches record
- train-LOO median **threshold = 0.1263** — matches record

| case | reproduced today | recorded (`closure_challenge_trained_entry_round3_gated.json`) | verdict |
|---|---|---|---|
| alpha_15_13929_4048 | 0.1503 → **APPLY** | 0.1503 → APPLY | MATCH |
| alpha_15_13929_2024 | 0.1525 → **APPLY** | 0.1525 → APPLY | MATCH |
| alpha_05_4071_4048 | 0.0420 → **DECLINE** | 0.0420 → DECLINE | MATCH |
| alpha_05_4071_2024 | 0.0034 → **DECLINE** | 0.0034 → DECLINE | MATCH |

All four decisions reproduce from train-only inputs, to the recorded 4 dp, with no test
truth readable in the process.

**Verdict A3: PASS — re-verified today.** Assertion block executed three ways with three
firing negative controls; §4.1's claims re-anchored against HEAD with **zero line shift
since 08-08**; all four gate decisions reproduced train-only under a guard proven armed at
entry and at exit.

---

## A4 — ONE DUCT CASE TRACED BY HAND, END TO END: **PASS** — re-verified today

Case: **`AR_1_Ret_360`**. Run dir:
`/home/ubuntu/certonomous-runs/w3-qcr-rank1/AR_1_Ret_360_qcr/`. Comparison baseline: the
**fresh `deb91557` clone**, not the live checkout.

**Link 1 — CONFIG.** `constant/turbulenceProperties`: `RASModel kOmegaSSTQCR`, `turbulence
on`, `printCoeffs on`, and — verified by pattern, not by eye — **zero coefficient-dict
entries** (`grep -cE 'Coeffs$|Ccr1'` = **0**; positive control: the same pattern scores
**2** on a planted `kOmegaSSTQCRCoeffs { Ccr1 0.9; }` file, so it can see an override).
Diff against the shipped file is **one line**: `kOmegaSST` → `kOmegaSSTQCR`.
`system/controlDict` differs from shipped in **exactly four ways**, all read in the diff:
`libs ("libkOmegaSSTQCRTurbulenceModels.so")` instead of the organisers' frozen-model lib;
`startFrom startTime; startTime 0`; `endTime 3000` annotated `// frozen cap, RULE_FREEZE.md
§5`; two `#includeFunc` probe lines commented out.
`constant/transportProperties`, `system/fvSchemes`, `system/fvSolution`,
`system/fvOptions`, `caseDef`, `0/U`, `0/k`, `0/omega`, `0/p`, `0/nut`: **all
byte-identical to shipped**.

**Link 2 — MESH.** All five `constant/polyMesh` files (`points`, `faces`, `owner`,
`neighbour`, `boundary`) **byte-identical to shipped**. Header note:
`nPoints:6272 nCells:3025 nFaces:12210 nInternalFaces:5940`. **No `*_LES` file anywhere in
the case** — 0 hits, and the fresh benchmark clone ships **3** for this very case
(`0/U_LES`, `0/k_LES`, `0/tauij_LES`), so truth existed to be copied and was not.
*(Positive control: a planted `__probe_U_LES` is found by the same `find`. Instrument
defect disclosed: my first sweep used `-iname "*LES*"`, which matched `fi**les**`,
`source**Files**` and `variab**les**` and reported 3 false hits; corrected to the actual
`*_LES*` truth-file pattern.)*

**Link 3 — SOLVER LOG.** `log.simpleFoam`: OpenFOAM **v2606** `simpleFoam`, build
`_481094f-20260618`, host `ip-172-31-43-247`, PID 3548, `Date : Aug 07 2026 / Time :
20:01:13`, `nProcs : 1`. `Selecting RAS turbulence model kOmegaSSTQCR`. `printCoeffs`
prints the full dict — **stock SST constants throughout** (`alphaK1 0.85`, `alphaK2 1`,
`alphaOmega1 0.5`, `alphaOmega2 0.856`, `gamma1 0.555556`, `gamma2 0.44`, `beta1 0.075`,
`beta2 0.0828`, `betaStar 0.09`, `a1 0.31`, `b1 1`, `c1 10`, `F3 false`, `decayControl
false`, `kInf 0`, `omegaInf 0`) — **plus exactly one new line, `Ccr1 0.3`**.
`meanVelocityForce` selects 3025 cells. **395 real `Time =` iterations** with 395
per-iteration `Solving for Ux` residual blocks (counted, not asserted). Terminates
`SIMPLE solution converged in 395 iterations` under `fvSolution`'s
`residualControl { k 5e-6; omega 1e-10; }` — **final-iteration initial residuals: k
4.89517e-06 (< 5e-6), omega 6.21022e-11 (< 1e-10)**, both under their thresholds, U
components ~1.5e-6 to 8.6e-6. `ledger.txt`: `AR_1_Ret_360_qcr rc=0 wall_s=9`. This is a
real, converged, uncapped solve — 395 of a 3000 cap.

**Link 4 — FIELD.** `395/U`: `class volVectorField`, `nonuniform List<vector>`, **3025**
entries — one per mesh cell — parsed cleanly by Ofpp.

**Link 5 — INTERPOLATION.** `NearestNDInterpolator(C, U)` with the fresh clone's
`constant/C` (3025 centres) onto the fresh clone's
`data/evaluation_points/AR_1_Ret_360_points.csv` (1000×3, coordinates only), written
`np.savetxt(delimiter=",", fmt="%.10g")`. Re-executed today in the A1 clean venv: output
**byte-identical** to the committed CSV.

**Link 6 — CSV ROW COUNT AND SHAPE.** **1000 rows × 3** comma-separated columns;
headerless (first row float-parses: `[10.8266, 0.0301466, -0.0597579]`); **all 3000 values
finite**; LF line endings, **no CR**, trailing newline present; sha256
`bb8d61fbbfd99f5099628cedf7b76a203558daa87e3235006b0c8527ea703e7e` = the
`R5_PREREGISTRATION.md` §3 value = the call record's value.

**Link 7 — SCORED NUMBER.** That byte-exact file scores **0.04547044480564218** under the
pinned harness in the fresh venv (A1) — the recorded AR_1 round-5 number, digit for digit,
feeding the recorded overall **0.056647191704213645**.

Config → mesh → solve → field → interpolation → CSV → score. **No link is asserted from
prose; every link was re-checked on the artifacts today.**

**Verdict A4: PASS — re-verified today.** One complete unbroken chain, byte-level at every
link, against a fresh benchmark clone rather than the live checkout.

---

## A5 — QCR PROVENANCE: **PASS on legs 1–2; leg 3 CHANGED** → **PASS WITH EXCEPTIONS**

### Leg 1 — in-house history: **PASS**

`git log --follow` on `sdk/openfoam/qcr/kOmegaSSTQCR/kOmegaSSTQCR.C` and `.H`:
**a single commit each — `303247bb`, 2026-08-05T17:33:27Z**, author `Ubuntu` (in-repo),
"The quadratic term the linear model cannot express…". The whole `sdk/openfoam/qcr` tree
has the same single commit. That is the exact `library_commit` the round-5 record claims,
**two days before the test solves and 8 minutes before the rule freeze** (`0bade54a`,
17:41:06Z).

The built library
`/home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/lib/libkOmegaSSTQCRTurbulenceModels.so`
hashes to sha256
`b741839596bc8624789652fdc69b476594dc24419edd21faedac004e2c1cc808` — **exactly the
record's `library_sha256`**.

`kOmegaSSTQCR` does not exist in stock OpenFOAM v2606: **0 files** under
`/usr/lib/openfoam/openfoam2606/src` contain the string. *(Positive control: `kOmegaSST`
returns **29** files in the same tree, so the grep reaches it.)* The implementation is the
lab's own.

### Leg 2 — ZERO fitted parameters, proven structurally: **PASS**

The rung demands proof that **nothing COULD be fitted**, not merely that nothing was. Every
element of the duct path enumerated, with what it actually contains:

| path element | what could carry a fitted number | measured finding |
|---|---|---|
| `kOmegaSSTQCR.C` / `.H` | any coefficient | **Exhaustive enumeration of every numeric literal in both files**: `0.3` (line 97, the `Ccr1` default), and only `0`, `1`, `2`, `3` besides — all structural (`SMALL` floor at 25, tensor identity at 37, the Boussinesq `(2/3)k` isotropic factor at 43). **Exactly one free coefficient exists in the entire implementation**, `Ccr1_`, declared `dimensioned<scalar>::getOrAddToDict("Ccr1", coeffDict_, 0.3)` and documented "(Spalart 2000, untrained)". k/omega transport is inherited unchanged from `kOmegaSST`. |
| the only override channel | `Ccr1_.readIfPresent(this->coeffDict())` (line 115) | the sole route by which 0.3 could become anything else — and it reads a dict that, in all three test arms, has **zero** coefficient entries (verified with a positive control) |
| `constant/turbulenceProperties`, **all 3 test ducts** | could override any coefficient | overrides **nothing**; single-line diff from shipped in each; `printCoeffs` in all three logs shows stock SST constants + `Ccr1 0.3` |
| mesh, `0/` fields, `fvSchemes`, `fvSolution`, `fvOptions`, `caseDef`, **all 3 test ducts** | could encode tuned inputs | **all 14 shipped files byte-identical to the `deb91557` clone in every one of the three cases** |
| `controlDict` | could encode a tuned stopping rule | only the four enumerated differences: lib swap, fresh start, the `RULE_FREEZE.md` §5 frozen cap, commented probes |
| `dynamicCode/` | on-the-fly compiled code | the benchmark's **own** `#calc "$Re_b*$nu/$h"` at `fvOptions` line 20 — a byte-identical shipped file — emitting the bulk velocity from shipped `caseDef` physics (log: `uncorrected Ubar = 85.3812`) |
| interpolation to the 1000 points | could smuggle a learned map | `NearestNDInterpolator` — **parameterless** nearest neighbour |
| the run tree | training data / ML artifacts / test truth | **0** files matching `*.pkl / *.pickle / *.joblib / *.npz / *.npy / *.h5 / *.pt / *.onnx / *.ckpt` anywhere under `w3-qcr-rank1/`. *(Positive control: a planted `__probe_model.pkl` is found by the identical `find`.)* `*_LES` truth: **0** in each of the three **test** arms; **3** each in the two **AR_7** arms, which is the benchmark's designated **validation** duct, read for the pre-registered V1/V2 gate metrics. |

**There is nothing in the duct path with a free parameter to fit, except one constant fixed
in 2000 in the open literature.** The claim is structural, as the ladder demands.

### Leg 3 — Spalart (2000) cited wherever QCR is named: **CHANGED — five load-bearing gaps**

**Frame.** Swept **920** `.md`/`.html`/`.json`/`.tex` files under `demo-output/website/`.
**55** name QCR; **27** also name Spalart; **28** do not. This is a lower bound on gaps —
the sweep did not leave `demo-output/website/`.

Most of the 28 are passing mentions where QCR names *someone else's* model (Wu & Zhang's
SST-QCRC), a docket line, or a cross-reference — the 08-08 pass explicitly and reasonably
excluded those. But **five carry the load-bearing "untrained / nothing fitted" claim about
OUR model without naming whose constant 0.3 is**, and the 08-08 PASS does not cover them:

| surface | what it says | why it matters | status |
|---|---|---|---|
| `demo-output/benchmarks.html` | "a converged forward solve of the untrained QCR2000 physics term — nothing fitted to anything" ×2 | **a PUBLIC page.** `git log -S` shows this sentence was written by **`49f71b8c`** — the sibling Ladder V **V10** rung, 2026-08-08T02:08:13, i.e. **13 minutes before the V5 sweep committed** | **NEW since the 08-08 sweep's scope** |
| `CLOSURE_CHALLENGE_STATUS.md` §0f | "the untrained QCR2000 constitutive term (`kOmegaSSTQCR`, `Ccr1 = 0.3`, nothing fitted to anything)" ×9 QCR mentions | the lab's primary closure status surface | gap, from `07a7fe9e` |
| `closure_challenge_submission_round5/MANIFEST.json` | "QCR2000 forward solve (kOmegaSSTQCR, Ccr1=0.3 untrained, library commit 303247bb)" ×3 rows | the **submission package's own manifest** | gap, from `07a7fe9e` |
| `closure_challenge_round5_qcr_forward.json` | `"RASModel": "kOmegaSSTQCR", "Ccr1": 0.3, "trained": false` | its **sibling** `closure_challenge_round5_qcr.json` **does** carry the full journal reference; the forward record does not | gap, from `e865076b` |
| `campaign/QCR_ACTIVITY_CHECK_2026-08-08.md` | **27** QCR mentions, a dedicated QCR record | committed `1a14e90b` at 2026-08-08T**02:18:29** — **3 minutes before** the V5 sweep's own commit at 02:21:52 | **raced the sweep** |

Confirmed still citing correctly (controls for the sweep): `closure.html` (**3** Spalart
mentions), the `.tex` (**4**), `closure_challenge_round5_qcr.json` (**1**, the full
journal reference in `model.provenance`), plus `R5_RULE_FREEZE.md`,
`W3_QCR_DUCT_FALSIFIER.md`, `LADDER_V_TRIPLE_VERIFICATION.md`, and the five records the
08-08 pass gave dated citation notes (`R5_PREREGISTRATION.md`, `F6b_QCR_*`,
`W1_HUMP_CHALLENGE_*`) — **all five notes verified present today**.

**REPORTED, NOT EDITED — and why.** `MANIFEST.json` and `closure_challenge_round5_qcr_forward.json`
are frozen scoring/pre-registration artifacts (A2 rests on their immutability);
`QCR_ACTIVITY_CHECK_2026-08-08.md` is another verification agent's signed report, left to
its owner exactly as the 08-08 pass left the V2/V7/V10 record to its owner;
`benchmarks.html` and `CLOSURE_CHALLENGE_STATUS.md` are live surfaces whose closure block
is Pass-2/V10 territory, and Pass 2 is running concurrently — editing them now would put
two passes in the same file. **This pass changed no file other than this report.**

**The finding in one sentence.** The 08-08 V5 PASS was true of the surfaces it swept, and
its sweep frame (`campaign/*.md`, `closure.html`, the `.tex`, the round-5 JSONs) did not
include the public `benchmarks.html` — into which a *sibling Ladder V rung*, executing the
same night, wrote a fresh uncited "untrained QCR2000 / nothing fitted to anything" claim.
**A verification pass introduced the defect a concurrent verification pass had just
cleared, and neither could see it.** That is the structural finding of this re-run, and it
is an argument for the ladder's own no-self-grading rule being extended to *cross-rung*
sweeps within a pass.

**Verdict A5: PASS WITH EXCEPTIONS.** Legs 1 and 2 re-verified today, identically and with
stronger controls. Leg 3 **CHANGED**: as literally worded ("Spalart (2000) is cited
wherever QCR is named") it does **not** hold today; under the 08-08 pass's narrower frame
it does. Five load-bearing gaps named above, reported not edited. **Chief ruling
requested** on (a) the frame, and (b) who fixes the public page and the frozen artifacts.

---

## WHAT CHANGED SINCE 2026-08-08 (the explicit list this pass was dispatched to produce)

| # | change | effect on a Pass-1 verdict |
|---|---|---|
| 1 | **`cf6a0477`** (2026-08-10) added one key to `closure_challenge_round5_qcr.json`: `leaderboard_comparison_dated_2026_08_07.rank_companion_2026_08_10`. Verified by full flat-key diff: **1 key added, 0 removed, 0 changed** (146 → 147 leaf values). | **None.** Every score, hash and verdict A1/A2 compare against is byte-unchanged. |
| 2 | **`cf6a0477`** appended 18 lines to `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` at ~line 1073 (external-wording rank caveat). | **None on A3.** §4.1 is at 262–286, above the insert; unmoved. |
| 3 | **`18120bf8`** (2026-08-10) touched `CLOSURE_CHALLENGE_STATUS.md` and `closure.html` (rank-1 companion clause). | **None on A1–A5.** Neither is a Pass-1 evidence artifact; `closure.html` still carries 3 Spalart citations. |
| 4 | **numpy 2.5.1 → 2.5.2** in a freshly built venv. | **None** — every score is bit-identical across the bump, which strengthens A1. |
| 5 | **A2 evidence upgraded**: AR_7 start times now read from log headers (`17:41:36`) rather than inferred from `wall_s`; two new tamper checks added (CSVs byte-frozen since `e865076b`; `R5_RULE_FREEZE.md` single-commit). | A2 PASS on stronger evidence than 08-08. |
| 6 | **A5 leg 3 gaps identified** (five surfaces above), including a **public page** whose uncited claim was introduced on 2026-08-08 by the sibling V10 rung at `49f71b8c`. | **A5 downgraded to PASS WITH EXCEPTIONS.** This is the finding. |
| 7 | **Freeze-rule inconsistency surfaced**: `9a21d65c` appended to `R5_PREREGISTRATION.md`; `cf6a0477` declared the same file untouchable on freeze grounds. Both defensible; the rules differ. | No verdict changes; **chief ruling requested**. |
| 8 | **§4.1's line citations in the send draft remain stale** (115/165–167/215 vs actual 128/178–180/228), unchanged since 08-08 because two passes in a row correctly declined to edit Katie's package. | A3 PASS (claims hold); **standing defect re-raised**. |

**Unchanged and re-confirmed:** both gate scripts (last touched 2026-07-31 / 2026-07-28);
the QCR source (single commit `303247bb`); the built `.so` hash; the eight submission CSVs
(zero bytes changed since `e865076b`); `R5_RULE_FREEZE.md` (single commit); the run tree;
both frozen external checkouts at their pinned commits.

**Not touched by this pass, deliberately:** every submission CSV and MANIFEST/scoring JSON
(immutable); `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` (Katie's send package); the `.tex`;
`docs/PRODUCT_LIST.md` (chief's); `benchmarks.html` and `CLOSURE_CHALLENGE_STATUS.md`
(concurrent Pass-2 territory); the sibling 08-08 rung records (their owners');
`QCR_ACTIVITY_CHECK_2026-08-08.md` (another agent's signed report); both frozen checkouts
(all A1 work ran on fresh clones in the scratchpad); and the scorer in the lab's own
environment (never invoked — the offline recomputation ran only in the scratchpad venv).

**The ledger stands at 6, untouched.** No scoring call was made, needed, or approached.

---

## VERDICTS

- **A1 — clean-environment re-score: PASS (re-verified today).** Pinned
  `closure-challenge 0.3.1` @ `1c4e22c8` in a fresh venv, benchmark clone @ `deb91557`;
  all 8 per-case scores and the overall **0.056647191704213645** reproduced to the last
  bit under a newer numpy; the three duct CSVs regenerated from the raw solve fields
  **byte-identical**; the five unchanged CSVs byte-identical to round 4; all 8 hashes
  matched programmatically against §3 and the call record; byte comparator positive-controlled.
  **Offline re-derivation of already-scored, hash-frozen bytes — not a ledger scoring call.**
- **A2 — pre-registration chain: PASS (re-verified today, strengthened).** `0bade54a`
  (17:41:06) predates the first validation solve by **30 s** (from the log's own start
  time, not inferred) and the test solves by two days; `e865076b` predates the one scoring
  call by **12 m 59 s**; the 8 prediction files are **byte-unchanged since
  pre-registration**; `R5_RULE_FREEZE.md` has one commit ever; the 6th call MATCHES its
  pre-registration clause by clause, 6 clauses of 6.
- **A3 — leakage assertions EXECUTED: PASS (re-verified today).** Assertion block run three
  ways with **three** firing negative controls, under 17 armed raising stubs proven armed
  at entry and still armed at exit; §4.1's claims re-anchored against HEAD with **zero line
  shift since 08-08**; all four gate decisions (0.1503 APPLY / 0.1525 APPLY / 0.0420
  DECLINE / 0.0034 DECLINE, alpha 0.7499, threshold 0.1263) reproduced from train-only
  inputs with ground truth read for exactly 21 non-test cases.
- **A4 — one duct traced end to end: PASS (re-verified today).** `AR_1_Ret_360` walks
  config (14 shipped files byte-identical; 4 enumerated `controlDict` deltas; zero
  coefficient overrides, positive-controlled) → mesh (5/5 byte-identical, 3025 cells, zero
  `*_LES` where the benchmark ships 3) → a real 395-iteration solve converging on
  `residualControl` (k 4.9e-6 < 5e-6, omega 6.2e-11 < 1e-10) → `395/U` with 3025 entries →
  parameterless nearest-neighbour interpolation → a 1000×3 headerless all-finite CSV,
  sha256 `bb8d61fb…` → **0.04547044480564218**.
- **A5 — QCR provenance: PASS WITH EXCEPTIONS.** In-house single-commit history at
  `303247bb` with the built `.so` hash matching the record and zero occurrences in stock
  v2606 (positive-controlled); **untrained proven structurally by exhaustive numeric-literal
  enumeration — exactly one free coefficient exists in the implementation, `Ccr1`, default
  0.3, Spalart's published constant**, with every override channel measured shut across all
  three test ducts and zero ML artifacts in the run tree (positive-controlled). **Leg 3
  CHANGED**: five load-bearing surfaces name our untrained QCR2000 without citing Spalart,
  one of them a public page into which the sibling V10 rung wrote the claim on 2026-08-08.
  Reported, not edited; chief ruling requested.

Signed: **Closure/UQ family supervisor, as PASS-1 owner**, personally per charter §3,
running on **Opus under a stated §5 model-rule override** (designated tier
credit-exhausted). Ladder rule "no agent may verify work it produced" satisfied — none of
the verified round-5 artifacts were produced by this executor. Passes 2 and 3 run
concurrently by other agents; rungs V6–V13 are theirs and are untouched here.

---

*Nothing below this line existed when the five verdicts above were committed
(`5a21b4fd`). The addendum below is dated and additive only; not one line of the
verdicts, tables or evidence above is changed by it.*

## ADDENDUM, 2026-08-10 21:0x UTC — chief's disposition of Pass 1 (additive only)

All five rungs **ACCEPTED**. **A5's verdict is held at PASS WITH EXCEPTIONS — the chief
declined to upgrade it**, on the grounds that five surfaces carrying the load-bearing
untrained claim without naming whose constant it is, one of them public, is a real
exception.

### A5 became L-53 (`e59ae644`, 2026-08-10T20:56:41Z)

> A verification rung wrote the defect its sibling rung had just cleared, thirteen minutes
> apart, and the ladder's own design made it invisible. Parallel passes buy independence,
> and independence means neither sees what the other writes.

**The rule taken from it, now binding on this ladder:**

1. **A rung that EDITS is itself unverified material.** Read-only rungs re-run *after*
   writing rungs land — a read-only rung executed concurrently with, or before, an editing
   rung has not verified that rung's output.
2. **`git log -S` any defect's sentence before assuming provenance.** The author may be our
   own machinery. That is precisely how A5's finding was reached: the uncited
   "untrained QCR2000" sentence on the public page was traced by `git log -S` to
   `49f71b8c`, the sibling V10 rung, and not to the round-5 producers.

### Ruling 1 — the pre-registration file: BOTH rules stand; there is no conflict

A frozen artifact **may take a dated addendum** and **may never take a revision** (L-44).
`9a21d65c` did the former; `cf6a0477` correctly refused the latter. Additions go below the
freeze line, never inside it, and any addendum must state its date and that the text above
is unchanged.

**Checked against the artifact today, and NO EDIT WAS MADE — the append already complies
on its face.** `R5_PREREGISTRATION.md` lines 197–205:

- the file carries its own frontier at line 197: *"Nothing below this line existed when
  this file was committed…"*;
- the append sits at 201–205, **below** it;
- and it opens: **"Dated citation note, 2026-08-08 (Ladder V rung V5; additive only, no
  frozen clause touched)"** — which states the date, the authoring rung, and that the
  frozen text above is untouched.

Date, attribution, and the unchanged-above declaration are all present. Adding framing
that is already there would mean editing a frozen artifact to no purpose — and under L-53,
just born, an edit to a frozen artifact is itself unverified material. **Reported as
compliant; the file was not touched.** *(The addendum you are reading applies the same
discipline to this report.)*

### Ruling 2 — the stale §4.1 citations: ASSIGNED TO PASS 2, not to this pass

The chief's ruling: these are not nobody's, they are the chief's to assign, and they go to
**Pass 2**, which already owns the send package's claims table under A8 and is editing
those files tonight. Two passes declining to edit was correct in both cases; the failure
would have been for a third to assume someone else had it.

**Reported, not made. Pass 1 stays off `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`.** The
correction is mechanical, and A3 re-verified every target line against HEAD today
(`apply_closure_ph_gate.py`, unchanged since `fe121af2`, 2026-07-31), so Pass 2 need
re-derive nothing:

| draft line | reads today | must read | verified against HEAD |
|---|---|---|---|
| **268** | "occur at line **115** inside" | "occur at line **128** inside" | `_load_ground_truth_U` at **128**, loop `for case in gate._PH_TRAIN:  # 21 cases, train only` at **126** |
| **269** | "and at line **215** inside" | "and at line **228** inside" | `_load_ground_truth_U` at **228**, loop `for c in ph._PH_TRAIN:` at **225** |
| **271** | "The test-case loop (lines **165–167**)" | "The test-case loop (lines **178–180**)" | loop `for case in ph._PH_TEST:` at **178**, `# no U_LES read` annotation at **179** |

The fourth §4.1 claim (the gate's executable assertions) is quoted unnumbered in the draft
and needs no change; the assertions are at **84–86** and were executed live under A3 with
three firing negative controls. **Every §4.1 *claim* was and remains true — only the
*citations* are stale.** A reviewer who opens line 115 finds the wrong line, which is the
whole reason the fix is worth making before any send.

### Precedent recorded at the chief's instruction

Three Pass-1 practices are kept as precedent for future rungs:

1. **Re-score under a different environment build than the prior pass, and say so.** The
   numpy 2.5.1 → 2.5.2 delta turned "the number reproduces" into "the number does not rest
   on one pinned environment" — a strictly stronger claim than the rung asked for.
2. **Disclose your own instruments misfiring at the point of use**, and carry a
   planted-decoy or bit-flip positive control on every negative finding. Three of this
   pass's instruments misfired and are disclosed inline rather than quietly corrected.
3. **Record the machine clock rather than reconciling it to the dispatch header.** This one
   caught a real error upstream: the chief's changelog entries had taken their date from
   the paperwork instead of the clock, and are corrected in `e59ae644`.

**Pass 1 is closed.** Nothing further from this pass unless Pass 2's landing raises
something on rungs A1–A5 — and under L-53 clause 1, Pass 2's landing is exactly the event
that would require the read-only rungs here to be re-run against what it writes.

---

## PRE-REGISTERED RE-RUN — L-53 clause 1, first operational application

*Written 2026-08-10 while Pass 2 is still open and its diff does not yet exist, so the
scope of the re-run cannot be tuned to what Pass 2 turns out to have written. Additive
only; nothing above this line is changed. Recorded on the artifact rather than left in
messages so the loop survives a fleet termination.*

**Status: ACCEPTED by the chief; ARMED, NOT RUN. Trigger = the chief's signal that Pass 2
has committed.** Pass 1 is otherwise idle and takes no other work.

### Scope, fixed in advance

**RE-RUN — exactly two legs:**

| leg | what it re-checks |
|---|---|
| **A3 leg (c)** | §4.1's line citations in `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` against `apply_closure_ph_gate.py` at the then-current HEAD |
| **A5 leg 3** | the Spalart-citation sweep across `demo-output/website/` |

**DO NOT RE-RUN — A1, A2, A4.** They rest on artifacts Pass 2 cannot touch without
breaking the chain A2 itself proves: the 8 submission CSVs (byte-frozen since `e865076b`),
`R5_RULE_FREEZE.md` (single-commit), the two pinned external checkouts, the run tree, and
the QCR source and its `.so`. The point of L-53 clause 1 is to close the window a writing
rung opens, **not** to repeat work that nothing touched. If Pass 2's commit is found to
have touched any of those paths, that is a separate and much larger finding, and the full
pass re-runs.

### Method, fixed in advance so it cannot be tuned

1. `git diff --stat <pass-2-commit>^ <pass-2-commit>` first — enumerate exactly what moved
   before looking at any of it.
2. **A3:** re-locate §4.1 by heading (not by line number), re-derive the anchors in
   `apply_closure_ph_gate.py` at HEAD by pattern (`_load_ground_truth_U`, `for case in
   gate._PH_TRAIN`, `for case in ph._PH_TEST`, `# no U_LES read`, `for c in
   ph._PH_TRAIN`), and check the three citations against what the code actually says. Also
   re-check the two gate scripts' commit hashes for movement (`5719374e` / `fe121af2` as of
   this pass).
3. **A5 leg 3:** re-run the identical sweep — same file set (`.md`/`.html`/`.json`/`.tex`
   under `demo-output/website/`), same patterns (`\bQCR\b|kOmegaSSTQCR|QCR2000|SA-QCR`
   against `Spalart`) — and report the same three counts, so the numbers are comparable
   rather than merely recomputed.
4. **L-53 clause 2 applied throughout:** `git log -S` every sentence found changed or
   newly uncited, to attribute provenance before assuming it. The author may again be our
   own machinery.
5. Every negative finding carries a positive control, as in this pass.

### Baseline to compare against (this pass's measured numbers)

920 files swept · **55** name QCR · **27** also cite Spalart · **28** do not · **5** of
those 28 carry the load-bearing untrained claim.

### Pre-registered prediction, so the re-run can be scored rather than narrated

I expect the three §4.1 citations corrected to **128 / 228 / 178–180**, and the
`benchmarks.html` and `CLOSURE_CHALLENGE_STATUS.md` citation gaps closed. I expect the
other three gaps **NOT** closed, for reasons that are correct rather than negligent:
`MANIFEST.json` and `closure_challenge_round5_qcr_forward.json` are frozen artifacts that
A2's chain rests on, and `QCR_ACTIVITY_CHECK_2026-08-08.md` is another agent's signed
report. **So I predict the 28 falls to roughly 26, not to 0 — and a drop to 0 would itself
be a finding**, because it would mean a frozen artifact was revised rather than
addended.

**Failure conditions, stated before the evidence exists:** any §4.1 citation still stale,
or corrected to a wrong line; any *new* uncited load-bearing claim introduced by Pass 2's
own edits (the exact L-53 failure mode, and the reason this re-run exists); or any change
to the A1/A2/A4 artifact set.

---

## RE-RUN EXECUTED — 2026-08-10 21:03 UTC, against Pass 2 at `92562841`

*Additive only; nothing above this line is changed, including the pre-registration, which
is left exactly as written so the prediction can be scored against it.*

**Escalation guard, checked first (method step 1).** `git diff --stat 92562841^ 92562841`
enumerated 14 files / 1117 insertions **before** any of it was read. Pass 2 touched **none**
of the A1/A2/A4 artifact set: the 8 CSVs, `R5_RULE_FREEZE.md`, `R5_PREREGISTRATION.md`,
`closure_challenge_round5_qcr.json` and `sdk/openfoam/qcr/` are all untouched, and the 8
CSVs remain byte-frozen since `e865076b`. **A1, A2 and A4 correctly do not re-run.** *(Pass
2 did touch `closure_round5_qcr_forward.py` — docstring only, scoping a stale "ledger stays
at 5" sentence to its own run date. No code changed; not in the artifact set.)*

### A3 leg (c) re-run: **FAIL** — pre-registered failure condition 1 is met

**§4.1 still cites 115 / 215 / 165–167. The correct numbers appear nowhere in it.**
Verified three independent ways, §4.1 located by heading (line 262) and never by the line
number under test:

1. Pass 2's diff to `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` contains **exactly one hunk**,
   `@@ -484,6 +484,38 @@` — a blocking banner on §5. **Nothing at 262–288.**
2. Direct read of §4.1 at HEAD: `line 115`, `line 215`, `lines 165–167` all still present;
   grep for `128` / `228` / `178–180` in the section returns **0**.
3. **L-53 clause 2 applied:** `git log -S "occur at line 115 inside"` returns **one commit
   in the file's entire history** — `87084eec`, 2026-07-30, the original author. Nothing
   has touched that sentence since it was written.

Anchors re-derived by pattern at HEAD, unchanged from Pass 1 (both gate scripts still at
`5719374e` / `fe121af2`): `_load_ground_truth_U` at **128** and **228**; loops at **126**
and **225**; `for case in ph._PH_TEST` at **178** with `# no U_LES read` at **179**. Every
§4.1 **claim** remains true. Only the **citations** are wrong, still by +13.

**Why it did not happen, stated fairly.** Pass 2 did not overlook this — it **decided** it.
Its own report (`LADDER_V_PASS2_2026-08-11.md`, line 68) records: *"**STALE — reported, not
edited.** … Pass 1 re-anchored them in its own report and declined to edit Katie's package;
**I make the same call** and record it twice so it is not lost a third time."* Pass 2 had
the handoff table and used the correct numbers (128 / 228 / 178–180) in its own line 67. It
reasoned exactly as Pass 1 did, and reached the same conclusion.

**So the assignment did not take, and this is the finding.** The chief's ruling 2 assigned
the fix to Pass 2 precisely so that a third party would not assume someone else had it —
and a third party has now declined it, on the same correct-sounding grounds, in writing.
**Three consecutive passes have each individually made a defensible decision, and the
aggregate is a defect that has survived all three.**

One observation offered neutrally, because it is the sharpest available evidence about the
grounds: **Pass 2 added 32 lines to that same file in that same commit.** A blocking banner
was judged permissible; a three-number citation correction in the same document was not.
Both calls are arguable — a banner is additive and framed, while editing §4.1's body is a
revision of Katie's prose. But the distinction was not stated, and the net effect is that
the file was open and the defect was left. **Escalated to the chief: this now needs an
owner who is not a verification pass, because verification passes have declined it three
times for a reason that will recur a fourth.**

### A5 leg 3 re-run: **PASS** — the live failure condition did NOT fire

Identical sweep: same file set (`.md`/`.html`/`.json`/`.tex` under `demo-output/website/`),
same patterns (`\bQCR\b|kOmegaSSTQCR|QCR2000|SA-QCR` vs `Spalart`).

| measure | Pass 1 baseline (pre-Pass-2) | re-run (post-`92562841`) |
|---|---|---|
| files swept | 920 | **925** |
| name QCR | 55 | **61** |
| also cite Spalart | 27 | **33** |
| **do NOT cite** | **28** | **28** |

**Zero closed, zero new — the 28 is the identical set, file for file.** Six new files name
QCR and **all six cite Spalart**.

**The failure condition this re-run existed for did not fire.** The chief flagged Pass 2's
new prose as where an unattributed claim would be born. It was not born:

| new/edited outward surface | QCR | Spalart | the load-bearing claim as written |
|---|---|---|---|
| `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md` (**349 new lines — the document that actually travels**) | 7 | **3** | *"`kOmegaSSTQCR` with `Ccr1 = 0.3` — **Spalart (2000)'s published constant**, nothing fitted to anything"*; *"`Ccr1 = 0.3` frozen before any solve, Spalart's published constant"*; *"Spalart published QCR2000 in 2000"* |
| `closure_challenge_submission_round5/README.md` (93 new) | 2 | 1 | cites |
| `CLOSURE_CHALLENGE_PRIOR_ART.md` (+25) | 1 | 1 | cites |
| `closure.html` | 10 | 3 | cites |
| `LADDER_V_PASS2_2026-08-11.md`, `LADDER_V_TRIPLE_VERIFICATION.md` | 8 / 5 | 2 / 2 | cite |

**Every one of Pass 2's new outward-facing claims about the untrained term names whose
constant it is.** This is the first time in this ladder that a writing rung has landed
without opening a citation gap, and it is the direct result of L-53 existing when Pass 2
wrote.

**Touched-and-left, reported not fixed.** Pass 2 edited `benchmarks.html` — the public
surface A5 flagged — adding a 3-line best-on-board caveat, and **left the uncited
"untrained QCR2000 … nothing fitted to anything" sentence in place**. Not a new claim; a
known gap that was open in the editor and stayed. `git log -S` re-confirms provenance
unchanged: **`49f71b8c`, the sibling V10 rung**. Same for `benchmarks.json`, `wall.json`
and `PROBABILITY_OF_RANK_2026-08-10.md` — single passing mentions, edited, gap unchanged.

**Positive control on the sweep's null.** The sweep is not blind to movement: it detected
**6** newly-citing files and independently classified **4** Pass-2-touched files as still
uncited. It sees change in both directions, so "28 → 28" is a measurement, not a
non-observation.

### PREDICTION SCORED — 3 of 5 wrong, and the misses share one cause

| # | pre-registered at `97eb51d2` | outcome | score |
|---|---|---|---|
| 1 | three §4.1 citations corrected to 128 / 228 / 178–180 | not fixed; Pass 2 declined in writing | **WRONG** |
| 2 | `benchmarks.html` and `CLOSURE_CHALLENGE_STATUS.md` gaps closed | neither closed; `benchmarks.html` edited and left | **WRONG** |
| 3 | the other three **not** closed (`MANIFEST.json`, forward JSON, `QCR_ACTIVITY_CHECK`) — frozen artifacts and another agent's report | all three still uncited, for exactly those reasons | **RIGHT** |
| 4 | 28 falls to **roughly 26** | 28 → **28** | **WRONG on the number** |
| 5 | a fall to **0** would itself be a finding (a frozen artifact revised rather than appended) | branch not taken — no frozen artifact was revised | **RIGHT; branch correctly not taken** |

**Diagnosis of the miss, since a prediction that survives by being vague is worth less than
one that misses cleanly.** Predictions 1, 2 and 4 all rest on **one** unstated assumption:
that the chief's assignment to Pass 2 would take. They are not three independent errors;
they are one error counted three times. Predictions 3 and 5 were about **artifact
properties** — frozen files do not get revised — and both held exactly.

**The rule I would take from my own miss: predictions about artifact properties held; every
prediction about another agent's future compliance failed.** I had direct evidence for the
first class and none whatever for the second, and I did not mark the difference when I
wrote them down. A pre-registration should label which of its predictions are measurements
and which are forecasts of behaviour.

**What my prediction did NOT cover, stated plainly.** Pass 2 changed 14 files and 1117
lines. My prediction covered the §4.1 citations and the five named citation gaps — nothing
else. It had no term for: the description document existing at all (349 lines of new
outward prose, the single largest new-claim surface and the very thing the chief flagged),
the submission README, the prior-art additions, the §5 blocking banner, `self_audit.py`,
the withdrawal of the internal-only gate on P(rank 1), or the retirement of the sweep-count
check. Most importantly, **the count staying at 28 is a movement my model had no shape
for**: I modelled the total as decreasing through closures, and what actually occurred was
zero closures plus six fully compliant additions. The number I predicted moving for one
reason stayed still for two reasons that cancel — and my prediction would have been
"roughly right" at 26 for entirely wrong reasons had two gaps happened to close.

### Re-run verdicts

- **A3 leg (c): FAIL.** §4.1's citations are unchanged and still stale by +13. Every claim
  holds; every citation is wrong. Failure condition 1 met. **Needs a non-verification
  owner.**
- **A5 leg 3: PASS.** The 28 is unchanged as a set, six new QCR-naming files all cite
  Spalart, and **no new uncited load-bearing claim was introduced by Pass 2's writing** —
  the L-53 failure mode did not recur. One touched-and-left gap on `benchmarks.html`,
  reported not fixed.
- **A1 / A2 / A4: not re-run, per the pre-registration**, escalation guard clear.

**Ledger stands at 6.** No scoring call. Pass 1 wrote only this file.
