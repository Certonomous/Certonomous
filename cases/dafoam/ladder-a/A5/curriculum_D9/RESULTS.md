# D9 — U-BEND PRESSURE-LOSS MINIMISATION, ladder A5 — RESULTS

**Run:** `20260825T181838Z_2370464`, `/home/ubuntu/certonomous-runs/CURRICULUM-D9-a5-ubend-opt/`.
**Graded by:** `d9_grade_SUPPLEMENT.py` (frozen; selftest 18/18 PASS incl. units R and S).
**Pre-registration:** `PREREGISTRATION.md`, frozen before the run directory existed.
Nothing sent, filed, posted or uploaded (rule 7).

---

## 1. VERDICT

# `NOT A RESULT`

**G9-4 — only 1 of the 4 registered endpoint FD steps produced a table.** A plateau requires
≥ 3 consecutive usable steps (`PLATEAU_MIN_STEPS = 3`) and cannot be demonstrated from 1.

**This is a registered honest outcome, written before compute.** `PREREGISTRATION.md` §5
states in advance: *"If fewer than 19 of 27 components have a demonstrated plateau, the verdict
is `NOT A RESULT` and that too is a good outcome."* No plateau was manufactured, and none could
be: the reference step is fixed by rule (longest qualifying window, ties → lowest start index,
middle step, per component) and only one of the four registered steps yielded a table at all.

### The full gate table

| gate | verdict | number / evidence |
|---|---|---|
| **G9-0** | `PASS` | four stage records present and `COMPLETE`; component count **27 == 27** registered |
| **G9-1** | `PASS` | `delta_repeat` = **0.000000e+00**, MEASURED BEFORE ANY FD STEP WAS SIZED (`rep1`, `rep2` both `OBJ = 52.34521691559307`, bit-identical). Floor falls back to representational eps·\|OBJ\| = **1.162297e-14** |
| **G9-2** | `PASS` | calibration major ran FIRST: `maxit=1`, `driver_iter_count=3`, `OBJ = 51.68311682555106`, wall 86 s. Buy timeout projected by the frozen rule → `TMO_OPT = 1806 s` |
| **G9-3** | **`GATE FAIL`** | **the SLSQP driver reported failure**: `driver_failed=True`, `driver_iter_count=47` against `maxit=20`. `OBJ_baseline` **52.34521691559307** → `OBJ_final` **50.27935096533333** |
| **G9-4** | **`NOT A RESULT`** | **1 of 4** registered endpoint steps produced a table |
| **G9-7** | `PASS` | every completed stage reports `measured_affinity=[11]` == registered cpuset 11, READ BACK from inside the process, never inferred from the flag |

**Probe verdict = worst of G9-0…G9-6 = `NOT A RESULT`.**

**The `GATE FAIL` at G9-3 is a second, independent negative and is not buried by the first.**
The improvement is **2.06587 (3.947 %)**, far above any noise floor — but the registered gate
maps *driver failed* to `GATE FAIL` irrespective of magnitude, and the driver failed. Per
`PREREGISTRATION.md` line 2 **the magnitude is REPORTED, never gated**, and it is not offered
as a success.

**A cap-stop did not occur.** The run finished inside its cap; the verdict is not a cap-stop.

---

## 2. WHY THREE OF FOUR FD STEPS HAVE NO TABLE — MEASURED, NOT ASSUMED

The three missing tables are **not** an interrupted run. The frozen launcher ran to completion
(its final two lines, `TOTAL_SPENT_CORE_MIN=27.7833 CAP=110.0` and
`STAMP=20260825T181838Z_2370464`, are the last two lines of `ledger.txt`). Three FD stages
exited `rc=1` with `AnalysisError: "Mesh quality error!"`
(`dafoam/mphys/mphys_dafoam.py:330`), `OOMKilled=false` on all of them.

| step | `rc` | primals completed | of expected | crashed on perturbation | component | peak `maxNonOrth` |
|---|---|---|---|---|---|---|
| **h = 1e-5** | **0** | **55** | 55 | — | — | **81.73** |
| h = 1e-4 | 1 | 30 | 55 | 30 of 54 | **idx 14** (−0.03221) | **89.46** |
| h = 1e-3 | 1 | 24 | 55 | 24 of 54 | **idx 11** (−0.03698) | **137.76** |
| h = 1e-2 | 1 | 18 | 55 | 18 of 54 | **idx 8** (−0.02914) | **116.01** |

*Expected primal count = 1 baseline + 2 × 27 central-difference evaluations = 55. Three
independent readings of the completed count agree exactly on every stage: `End` lines in the
log, DAFoam pseudo-time directories on disk, and `checkMesh` blocks (one higher on a crashed
stage, because the failing primal ran its mesh check and then raised).*

**The mechanism, and it is a finding about the optimisation, not about the harness:**

1. **The optimised endpoint is already outside the case's own declared mesh-quality envelope.**
   The *unperturbed* endpoint geometry measures **`maxNonOrth = 80.930`** against the case's
   own `checkMeshThreshold { maxNonOrth 70; }`. SLSQP drove the design there and DAFoam did
   not stop it, because that metric errors only on face-pyramid inversion, not on exceeding 70.
2. **Mesh sensitivity to the design variables is stiff and linear in the step.** A perturbation
   of 1e-4 moves `maxNonOrth` by ≈ 8 degrees off the 80.93 base; 1e-5 moves it by ≈ 0.8.
   Inversion trips at ≈ 89, and `checkMesh` reports it explicitly — e.g.
   `***Error in face pyramids: 4 faces are incorrectly oriented`.
3. **The failure index moves monotonically with the step, which is the signature of physics and
   not of contention.** Every crash is on the **second (−h) perturbation of a large-negative
   design variable**, and a larger step needs less pre-existing deformation to invert a cell.

**`idx 8` is one of the three components the pre-registration NAMED IN ADVANCE** as a candidate
to be FD-ungradeable (§5c, "idx16-class": idx 8, 16, 17). **`idx 11` and `idx 14` were NOT
named**, which per §5c is the more interesting half of the finding: an ungradeable component
the document did not anticipate.

**Plain statement.** At three of the four registered steps the endpoint FD verification is not
merely unfinished — it is **not performable at that design point**, because the perturbation
the verification requires inverts cells in the warped mesh. `DAFOAM_CHARTER.md` §1's bright
line exists to expose exactly this, and it is reported rather than worked around.

---

## 3. THE ENDPOINT FD TABLE — the one that exists, h = 1e-5

At the optimised design point (`\|dv\|₂ = 1.2200735719e-01`, 27 components, `idx 15` at the
`+0.04` bound). `OBJ` at the endpoint = **50.279381596476924**.

| idx | `J_an` (adjoint) | `J_fd` (h=1e-5) | \|ΔJ\|/\|J_fd\| | sign | DV endpoint | named §5c |
|---|---|---|---|---|---|---|
| 0 | 0.0233014036 | −0.0405877144 | 157.4100 % | **FLIP** | +0.000457 | |
| 1 | −0.2902657322 | −0.3544692798 | 18.1126 % | same | +0.006537 | |
| 2 | −0.1382249714 | −0.2024270855 | 31.7162 % | same | +0.004988 | |
| 3 | 0.5325300289 | 0.4690086283 | 13.5438 % | same | −0.010765 | |
| 4 | 0.1789048437 | 0.1147980802 | 55.8431 % | same | −0.001818 | |
| 5 | −0.3567370876 | −0.4206695813 | 15.1978 % | same | +0.011458 | |
| 6 | −0.3564841735 | −0.4204042377 | 15.2044 % | same | −0.006167 | |
| 7 | 0.3858222172 | 0.3219070751 | 19.8552 % | same | −0.021314 | |
| **8** | 2.7264149439 | 2.6639885744 | 2.3433 % | same | −0.029144 | **YES** |
| 9 | −1.9228843631 | −1.9874529652 | 3.2488 % | same | +0.003901 | |
| 10 | −0.2045391052 | −0.2691414058 | 24.0031 % | same | −0.024702 | |
| 11 | 8.1766200438 | 8.1205932633 | 0.6899 % | same | −0.036977 | |
| 12 | −3.0213817238 | −3.0860663573 | 2.0960 % | same | +0.032543 | |
| 13 | 0.2460103425 | 0.1807659836 | 36.0933 % | same | −0.018302 | |
| 14 | 7.1083571131 | 7.0486399326 | 0.8472 % | same | −0.032211 | |
| 15 | −12.2248374770 | −12.2901266129 | 0.5312 % | same | **+0.040000** | |
| **16** | −1.2614000335 | −1.3278166996 | 5.0019 % | same | +0.035789 | **YES** |
| **17** | 5.5978880906 | 5.5349984006 | 1.1362 % | same | −0.026866 | **YES** |
| 18 | −7.9682696338 | −8.0325159715 | 0.7998 % | same | +0.037818 | |
| 19 | −0.8228868848 | −0.8884693412 | 7.3815 % | same | +0.015577 | |
| 20 | 5.8224063029 | 5.7565052826 | 1.1448 % | same | −0.034223 | |
| 21 | −2.4654849633 | −2.5293525760 | 2.5251 % | same | +0.030408 | |
| 22 | 0.1993497882 | 0.1344850291 | 48.2320 % | same | −0.001357 | |
| 23 | 0.8835231267 | 0.8196618780 | 7.7912 % | same | −0.013139 | |
| 24 | −0.7548905312 | −0.8165348126 | 7.5495 % | same | +0.018623 | |
| 25 | 0.5309389410 | 0.4650129327 | 14.1772 % | same | −0.013133 | |
| 26 | −1.7288671306 | −1.7918231185 | 3.5135 % | same | +0.027137 | |

### NO AGGREGATE IS QUOTED, AND THAT IS DELIBERATE

The pre-registration defines the G9-6 aggregate **only over GRADEABLE components** — those
with a demonstrated plateau over ≥ 3 consecutive usable steps. **Zero components are
gradeable**, because only one step exists. **The aggregate therefore does not exist for this
run and is not computed.** Quoting an aggregate over components whose FD was never shown to
lie in a plateau is precisely what `DAFOAM_CHARTER.md` §1 forbids, and the grader is built to
refuse it (selftest units B, C, F, G, Q).

The single sign disagreement at `idx 0` is **not** a G9-6 sign-flip count: G9-6 counts flips at
plateau-selected reference steps, and there are none.

---

## 4. PLATEAU EVIDENCE — THERE IS NONE, AND THE ONE STEP AVAILABLE LOOKS LIKE IT IS BELOW IT

The plateau **cannot be demonstrated**: it needs ≥ 3 of the 4 registered steps and 1 survived.
That alone settles G9-4. But the surviving table carries a structural signature worth recording,
because it bears on whether h = 1e-5 would have qualified even if the sweep had completed.

**`J_an − J_fd` is very nearly a CONSTANT across all 27 components:**

| statistic of `J_an − J_fd` over 27 components | value |
|---|---|
| mean | **+6.379282e-02** |
| standard deviation | 2.078606e-03 |
| stdev / mean | **3.26 %** |
| min / max | +5.602678e-02 / +6.641667e-02 |

A near-constant **additive** offset in a central-difference gradient is the classical signature
of a step that is **too small** — the difference quotient dominated by a systematic
evaluation-level error rather than by truncation. The implied per-evaluation objective
perturbation is **`mean × 2h` = 1.275856e-06 absolute**, i.e. **2.538e-08 relative** to
`OBJ = 50.279382` — entirely consistent with the primal's iterative convergence level.

**This is exactly the gap the pre-registration predicted it would have.** G9-1 records
`delta_repeat = 0` and the grader states, in the frozen instrument's own words, that *"a zero
repeat bounds REPRODUCIBILITY only; it does NOT bound iterative-truncation jitter, which the
step sweep does."* **The step sweep is the thing the mesh-quality failure prevented.** The
document anticipated the precise blind spot that then materialised.

**A caution, stated because the number is seductive.** If a single fitted constant is subtracted
from `J_an`, the residual disagreement falls below **0.81 % on every component and below
0.31 % on 24 of 27**. **This is recorded as a diagnostic observation about the STRUCTURE of the
discrepancy and is NOT a verification, NOT a correction, and NOT a gate evaluation.** Fitting a
nuisance parameter to a gradient comparison after seeing the numbers is exactly the move the
pre-registration's frozen step rule exists to prevent, and no verdict here rests on it. Whether
the offset is an FD artifact of too small a step or a genuine adjoint bias **cannot be
distinguished without the step sweep**, and the step sweep did not run.

---

## 5. THE TWO-ROW SHIPPED/PATCHED RULE

`DAFOAM_CHARTER.md` §6: *two rows or it is not a verdict about DAFoam.*

| row | toolchain | image ID | bought? | outcome |
|---|---|---|---|---|
| **patched** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` (resolved and logged at run time, `ledger.txt` line 2) | **YES** | **`NOT A RESULT`** |
| **shipped** | stock `dafoam/opt-packages:latest` | `sha256:9d45679d…90f07fc` | **NOT BOUGHT** | — |

**The shipped row is NOT BOUGHT, with the reason registered before compute** (§9): A5's
`OBJ.val wrt shapexUpper` is `GATE FAIL` on stock — 46.840 % aggregate with **two sign flips**
(idx 8 at 205.52 %, idx 17 at 121.86 %) — and `PASS` on the patched image at 2.768 % with zero
flips. An optimiser driven by the stock gradient would descend on a derivative already measured
to be wrong **including in sign**, which is not the registered question.

**Consequence, restated: D9 CANNOT claim a toolchain-independent result**, and does not.

---

## 6. INSTRUMENT PROVENANCE — THE GRADING PATH WAS FIXED AT THE PRE-REGISTRATION COMMIT

Each instrument hashed against its committed blob **before** grading. **All match.**

| file | md5 (working tree) | == `git show HEAD:…` | == `PREREGISTRATION.md` §11 |
|---|---|---|---|
| `d9_stage_and_run.sh` | `7bb4234f75fa53556303c0c2408bb5a7` | **yes** | **yes** |
| `d9_run_script.py` | `af5f07bc1d3b4aca4fb427e089df0761` | **yes** | **yes** |
| `d9_grade.py` | `7704513424bf623b024814f4b86f8f31` | **yes** | **yes** |
| `d9_grade_SUPPLEMENT.py` | `baf7d69b3f6c32f64d5a47bf9d88c717` | **yes** | added at `beb90c52` |

`--selftest` → **18/18 PASS**, including units **R** and **S** (the two previously-silent `None`
paths of the reader plant). **The grader was not modified by this lane.**

### D9-DEF-2 — a naming defect between the two frozen files, repaired without touching either

The frozen launcher and the frozen grader disagree on the endpoint stage directory name:
launcher `sed 's/\./p/; s/-/m/'` on `1.0e-5` → **`fd_1p0em5`**; grader `fmt_tag` =
`"%.1e" % h` → **`fd_1p0em05`**. Left alone the grader finds **zero** tables and returns a
**FALSE** `NOT A RESULT` — the right label for the wrong reason. Confirmed empirically: before
the bridge the grader printed *"only 0 of 4 registered endpoint steps produced a table"* while
`fd_1p0em5/d9_out.json` sat on disk with 27 `J_an` and 27 `J_fd` entries.

The repair is `d9_def2_bridge.sh`: a **symlink per step inside the run tree**, from the name
the grader looks for to the directory the launcher wrote. No frozen file is touched; nothing is
copied, regenerated or recomputed. Against `VERIFICATION_CHARTER.md` §2d.1: (i) the defect is
in path construction, not in the result; (ii) disclosed here; (iii) the substitute is the same
inode; (iv) **no gate, threshold, cap or label moves** — and the verdict after the bridge is
still `NOT A RESULT`, now for the true reason.

**The bridge's own md5 assertion is VACUOUS for the three crashed stages** — `md5sum` on a
missing `d9_out.json` yields an empty string through both paths and `"" = ""` passes. That is
disclosed rather than quoted, and the aliases were verified **independently by inode**:
`fd_1p0em05→fd_1p0em5` 5297655, `fd_1p0em04→fd_1p0em4` 5298981, `fd_1p0em03→fd_1p0em3` 5299627,
`fd_1p0em02→fd_1p0em2` 5300157 — alias and target identical in every case.

### Rule 4, and the clauses NOT EXERCISED

- **Age guard — `NOT EXERCISED`, disclosed BEFORE compute** (`PREREGISTRATION.md` §5d): DAFoam
  gzips `0/U` → `0/U.gz` mid-solve, so the file the guard dates against ceases to exist.
  Substitute: `COLDSTART_PROVED`, a **pre-launch** proof of absence, present in `ledger.txt`
  for **all eight** stages of the original run and all four of the replication.
- **`ExecutionTime count == endTime` — NOT APPLICABLE AS WRITTEN.** That clause assumes one
  solver run printing every timestep; a `check_totals` stage is 55 primals at
  `printInterval 100` over `endTime 1000`, giving 605. The **stronger applicable equivalent**
  is used: completed-primal count == registered `1 + 2 × 27 = 55`, cross-checked three ways
  (§2).

---

## 7. REPLICATION — CRASH TRIAGE, FEEDING NO GATE

A crash is a finding until triage says otherwise. Four stages were re-fired **as a parallel
batch** into a **fresh** run directory
(`/home/ubuntu/certonomous-runs/CURRICULUM-D9-a5-ubend-opt-REPLICATE-REP_20260825T191118Z/`),
leaving the original trees untouched as evidence. Driver: `d9_fd_replicate.sh` — **NOT a frozen
instrument**, written after first compute, labelled as such in its own header, **feeding no
gate**. Its docker invocation is copied **verbatim** from the frozen launcher's `run_stage`
(`d9_stage_and_run.sh:115-120`), and all four members were handed the **same** endpoint
`opt_dv.json` (md5 `e921664a6e99aa838c01ed50ba89f50d`, asserted equal across the batch).

**Determinism as registered:** `np = 1` throughout, so `decomposePar` is never invoked and the
effective decomposition is the trivial single domain — scotch's randomness is never reached.
`PYTHONHASHSEED=0` pinned into every container. No stochastic component exists in this chain.



---

## 8. COST

`cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED.` The box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **All dollar figures are DERIVED, NOT
MEASURED.**
### 7a. What the replication measured

**The crash is deterministic to the primal.** Every crashed stage reproduced at **exactly** the
same completed-primal count and the same `checkMesh` block count as the original:

| step | original: primals / `checkMesh` blocks / `rc` | replicate: primals / blocks / `rc` | identical? |
|---|---|---|---|
| h = 1e-4 | 30 / 31 / 1 | **30 / 31 / 1** | **yes** |
| h = 1e-3 | 24 / 25 / 1 | **24 / 25 / 1** | **yes** |
| h = 1e-2 | 18 / 19 / 1 | **18 / 19 / 1** | **yes** |

`OOMKilled=false` on all three replicates, memory cap `3221225472` bytes (3 GiB) as the frozen
launcher sets. **These are not memory failures and not contention artifacts.**

**The one surviving table is reproducible to the BIT.** The h = 1e-5 replicate returned
`rc=0`, 55 of 55 primals, and a record **bit-identical to the original in every field**:

- `J_an` — 27 values, **bit-identical**
- `J_fd` — 27 values, **bit-identical**
- `shapexUpper` — 27 values, **bit-identical**
- `OBJ_val` — `50.279381596476924` in both
- whole-record equality: **True**

This is the determinism the pre-registration claimed (§ line 6) and did not previously
demonstrate. It also means the near-constant `J_an − J_fd` offset of §4 is a **property of the
computation, not run-to-run scatter.**

**Saturation and the memory guard.** Four concurrent single-core containers on idle cores
**11, 12, 14, 15** — within the 5-core cap, alongside 7 cores already pinned (D4 arm O on
cpuset 5,6,7,9; plus 8, 10, 13 busy). Each member checked `free -g` before launching and would
have held while available < 6 GiB; all four cleared at **16–17 GiB available**. Measured
resident, `docker stats`: **355.6 / 773.9 / 744 MiB** — **≈ 3 GiB total across the batch
against the 8 GiB budget**, well inside it. Batch wall ≈ **8.6 min** against **19.0 min** if run
serially: a **2.2× throughput gain** for the same core-minutes.

**Contention, DISCLOSED and not absorbed** (`COMPUTE_BUDGET_CHARTER.md` §6): replicate-vs-
original wall time was **+0.00 %** (h=1e-5, 454 s both), **−4.29 %** (h=1e-4), **+5.07 %**
(h=1e-3), **+5.59 %** (h=1e-2). The band **−4.3 % to +5.6 %** sits inside the 5–11 % the lab
records as acceptable, and the identical 454 s on the longest stage shows the cpuset pinning
held. **This is disclosed, not treated as a defect, and it is NOT folded into the
actual/predicted ratio below.**

---

### 8a. Cost — actual against the pre-registered prediction

**Registered cap: 110.0 core-min. Total D9 spend across EVERY container: 46.7667 core-min =
42.5 % of cap. NO OVERRUN, and the verdict is not a cap-stop.**

| channel | core-min | $ DERIVED |
|---|---|---|
| **registered chain** (`cal`, `rep1`, `rep2`, `opt`, 4 × `fd_*`) | **27.7833** | **$0.0238** |
| diagnostic replication (crash triage, §7a — **not** in the prediction) | **18.9834** | $0.0162 |
| grading, hashing, analysis (python, seconds; not separately metered) | < 0.2 | — |
| **D9 TOTAL** | **46.7667** | **$0.0400** |
| pre-registered prediction | 43.0 | $0.0368 |
| registered cap | 110.0 | $0.0940 |

**Estimate-versus-actual, per stage** (predictions from `PREREGISTRATION.md` §6; the table there
sums to 42.5 and the document quotes ≈ 43):

| stage | predicted | actual | ratio actual/predicted | attribution |
|---|---|---|---|---|
| `cal` (1 major) | 2.80 | 1.4333 | **0.51** | **misprediction** — the anchor's 146 s one-off startup was ≈ 86 s here |
| `rep1`+`rep2` | 4.20 | 0.4666 | **0.11** | **misprediction, the largest in the item** — the anchor assumed ≈ 125 s per `run_model`; measured **14 s**, a **9.0× overprediction** |
| `opt` (20 majors) | 10.60 | 7.0500 | **0.67** | **misprediction** — the driver stopped at 47 evaluations, cheaper per major than the anchor implied |
| `fd_*` — the ONE stage that completed | 6.225 | 7.5667 | **1.22** | **misprediction the other way** — a complete `check_totals` is ≈ 22 % dearer than the measured anchor arm |
| **registered chain total** | **43.0** | **27.7833** | **0.65** | **see the warning immediately below** |

**THE 0.65 HEADLINE RATIO IS NOT A CALIBRATION OF THE ESTIMATE AND MUST NOT BE USED AS ONE.**
Three of the four FD stages aborted at 33–55 % of their primal count, so the chain underspent
because it **failed**, not because the estimate was high. The defensible per-stage figures are
the four rows above; the honest like-for-like FD number is the **1.22** row, the only FD stage
that ran to completion.

**Waste, NAMED SEPARATELY and never absorbed into any ratio** (`COMPUTE_BUDGET_CHARTER.md` §6):
the three crashed FD stages consumed **11.2667 core-min** and produced **no registered
artifact** — no table, no answer record. They did buy the mesh-quality finding of §2, which is
why it is reported as a finding rather than written off; but it is **not** netted against the
prediction.

**Diagnostic replication (18.9834 core-min) is likewise held OUTSIDE the ratio.** It was not
predicted, because it is post-hoc crash triage, and folding unpredicted spend into an
actual/predicted ratio would flatter the estimate.

`cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED.` **Every dollar
figure above is DERIVED at that rate, not measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

---

## 9. WHAT THIS ITEM DOES NOT ESTABLISH

Carried forward verbatim in force from `PREREGISTRATION.md` §10, plus what this run adds:

- **Nothing about the other five DV groups.** `shapeyUpper`, `shapezUpper`, `shapexLower`,
  `shapeyLower`, `shapezLower` are declared to pyGeo but are not optimiser design variables;
  none of their total derivatives has ever been FD-verified on this ladder. **A single-DV-group
  optimum is not the case's optimum and is not reported as one.**
- **Nothing at np > 1.** The np=4 FD path carries a measured anomaly at idx 16 and was
  deliberately not used.
- **Nothing about the stock image.** §5: the shipped row is NOT BOUGHT.
- **Nothing about a plateau at the baseline.** A plateau at the optimised endpoint would say
  nothing about one at the baseline — and in any case none was demonstrated at either.
- **NEW, from this run: nothing about the adjoint gradient at the optimised endpoint.** One FD
  table at one step is not a verification. The `J_an` column of §3 is **not** a verified
  gradient and must not be quoted as one.
- **NEW: nothing about whether h = 1e-5 lies in the plateau.** §4 gives a measured reason to
  doubt it. The question is open and is answerable only by a step sweep that the mesh-quality
  limit prevents at this design point.

---

## 10. WHAT WOULD MOVE THIS FORWARD — for the supervisor, not acted on by this lane

Stated as options, **not** taken. Each would need a **new pre-registration**, because D9's is
frozen and its gates are closed.

1. **The registered steps cannot be changed to fit the geometry.** Substituting smaller steps
   (3e-6, 1e-6 …) to obtain three tables would be choosing steps after seeing which ones crash
   — exactly what §5's frozen step rule forbids. A new item with its own frozen sweep is the
   only legitimate route.
2. **The endpoint is the problem, not the sweep.** The optimisation ran without a mesh-quality
   constraint and terminated at `maxNonOrth = 80.93` against the case's own threshold of 70. A
   follow-on that constrains the optimiser to the declared quality envelope would produce an
   endpoint at which an FD sweep is performable.
3. **`check_totals` aborts the whole table when one component's perturbation breaks the mesh.**
   Per-component isolation would salvage the surviving components. **This lane did not
   implement it**: it is a change to the measurement path, and a measurement-script change
   needs the supervisor's read **as a diff** before its output is believed.
4. **The near-constant offset of §4 is the most interesting open question** and is cheap to
   settle at a design point where the sweep runs.
