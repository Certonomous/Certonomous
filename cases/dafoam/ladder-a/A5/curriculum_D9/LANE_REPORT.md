# D9 RECOVERY LANE — LANE REPORT

**Lane:** dafoam `lab-lane`, D9 RECOVERY. **Date:** 2026-08-25.
**Territory:** `cases/dafoam/ladder-a/A5/curriculum_D9/`,
`/home/ubuntu/certonomous-runs/CURRICULUM-D9-a5-ubend-opt/`.
Nothing sent, filed, posted or uploaded (rule 7).

---

## 0. THE BRIEF'S PREMISE IS WRONG, AND CORRECTING IT IS THE FIRST FINDING

The brief states: *"A session usage limit killed the D9 lane … the lane was in its FD phase
when it died … some or all of those four FD stages are partial trees left by a launcher that
was killed mid-build."*

**The launcher was NOT killed. It ran to completion.** The frozen launcher
`d9_stage_and_run.sh` writes exactly two lines after its FD loop closes — `TOTAL_SPENT_CORE_MIN`
(line 215) and `STAMP` (line 216). **Both are present, and they are the last two lines of**
`/home/ubuntu/certonomous-runs/CURRICULUM-D9-a5-ubend-opt/ledger.txt`:

- `TOTAL_SPENT_CORE_MIN=27.7833 CAP=110.0`
- `STAMP=20260825T181838Z_2370464`

The FD phase therefore **completed as a launcher and failed as physics.** The ledger records
`rc=1` for three of the four FD stages, written by the launcher itself at the time — not
inferred by me afterwards. The fleet kill landed *after* the run finished and before anything
was graded or committed.

**Consequence for the brief's instruction 2.** "Re-fire only what the kill left incomplete"
has an empty referent: the kill left nothing incomplete. What is incomplete was left so by a
**deterministic mesh-quality failure**, and re-firing it unchanged reproduces it. I re-fired
anyway, as *crash triage* rather than as recovery, and §4 reports what that bought.

---

## 1. THE FD PHASE STATE, PER STAGE, FROM DISK

Rule 4's clauses are applied in the form the frozen pre-registration registered for this
family (§5d), and **the two clauses that do not apply are named with their reason rather than
waved through**:

- **Age guard — `NOT EXERCISED`, disclosed in the pre-registration BEFORE compute** (§5d).
  DAFoam gzips `0/U` → `0/U.gz` mid-solve, so the file the guard dates against ceases to
  exist. `ls fd_1p0em5/0/` confirms it: `alphat.gz`, `nut.gz` are gzipped, `U` is not, and the
  guard's reference file is gone. The registered substitute is `COLDSTART_PROVED` — a
  **pre-launch** proof that no answer file, no time directory and no `0/U.gz` existed before
  the container started. It is present in the ledger for **all eight** stages.
- **`ExecutionTime count == endTime` — NOT APPLICABLE AS WRITTEN.** That clause assumes one
  solver run printing every timestep. A `check_totals` stage is **55 primals** at
  `printInterval 100` over `endTime 1000`, so the count is `55 × 11 = 605`, not 1000. The
  **stronger applicable equivalent** is used instead and is stated below: the completed-primal
  count must equal the registered `1 + 2 × 27 = 55` (one baseline plus a central-difference
  pair per component).

**Three independent readings of the completed-primal count agree exactly on every stage** —
`End` lines in the log, DAFoam pseudo-time directories on disk, and `checkMesh`
non-orthogonality blocks (which number one higher on a crashed stage, because the failing
primal ran its mesh check and then raised).

| step | `rc` | OOMKilled | `End` lines | time dirs | primals expected | answer record | `status` | **COMPLETE?** | clause that failed |
|---|---|---|---|---|---|---|---|---|---|
| **`fd_1p0em5`** (h=1e-5) | **0** | false | **55** | **55** | 55 | present | `COMPLETE` | **YES** | — |
| **`fd_1p0em4`** (h=1e-4) | **1** | false | 30 | 30 | 55 | **ABSENT** | — | **NO** | `rc≠0`; primal count 30 of 55; **no answer record** |
| **`fd_1p0em3`** (h=1e-3) | **1** | false | 24 | 24 | 55 | **ABSENT** | — | **NO** | `rc≠0`; primal count 24 of 55; **no answer record** |
| **`fd_1p0em2`** (h=1e-2) | **1** | false | 18 | 18 | 55 | **ABSENT** | — | **NO** | `rc≠0`; primal count 18 of 55; **no answer record** |

The four upstream stages `cal`, `rep1`, `rep2`, `opt` are all `rc=0`, record present,
`status=COMPLETE`, `measured_affinity=[11]` equal to the registered cpuset.

**`OOMKilled=false` on every stage.** The three failures are **not** memory failures, and the
memory-limited-family concern does not explain them.

---

## 2. WHY THE THREE STAGES DIED — TRIAGE, NOT ASSUMPTION

All three raise the identical exception at
`dafoam/mphys/mphys_dafoam.py:330` → `AnalysisError: "Mesh quality error!"`, preceded in the
log by `checkMesh` reporting **face-pyramid inversion**, e.g. in
`fd_1p0em2_20260825T181838Z_2370464.log:4788-4793`:
`Mesh non-orthogonality Max: 116.0098542474852`, `***Number of non-orthogonality errors: 2`,
`***Error in face pyramids: 4 faces are incorrectly oriented`, then `Failed 2 mesh checks`.

**The measured mechanism, and it is a finding about the buy, not about the harness:**

- **The optimised endpoint mesh is ALREADY outside the case's own declared quality envelope.**
  The *unperturbed* endpoint geometry measures **`maxNonOrth = 80.930`**
  (`fd_1p0em5_…log`, first block), against the case's own
  `checkMeshThreshold { maxNonOrth 70; }`. SLSQP drove the design there and DAFoam did not
  stop it, because that metric only *errors* on pyramid inversion, not on exceeding 70.
- **The local mesh sensitivity to the design variables is extremely stiff, and it is linear in
  the step.** Peak `maxNonOrth` reached over each stage: **81.73** at h=1e-5, **89.46** at
  h=1e-4, **137.76** at h=1e-3, **116.01** at h=1e-2 — i.e. a DV perturbation of 1e-4 moves
  `maxNonOrth` by ≈ 8 degrees off an 80.93 base, and 1e-5 moves it by ≈ 0.8. The
  inversion threshold sits at ≈ 89.
- **The failure index moves monotonically with the step, which is the signature of physics and
  not of contention.** Every failure occurred on the **second (−h) perturbation** of a
  large-negative design variable:

| step | crashed on perturbation # | component | that component's endpoint value | peak `maxNonOrth` at the crash |
|---|---|---|---|---|
| h=1e-2 | 18 of 54 | **idx 8** | −0.02914 | 116.01 |
| h=1e-3 | 24 of 54 | **idx 11** | −0.03698 | 137.76 |
| h=1e-4 | 30 of 54 | **idx 14** | −0.03221 | 89.46 |
| h=1e-5 | — (all 54 completed) | — | — | 81.73 |

**`idx 8` is one of the three components the pre-registration NAMED IN ADVANCE** as a candidate
to be FD-ungradeable (§5c, the "idx16-class": idx 8, 16, 17, idx 8 carrying 205.52 %
adjoint-vs-FD on the stock image). The largest registered step fails on exactly that component.
`idx 11` and `idx 14` were **not** named in advance, which per §5c is the more interesting half
of the finding.

**Plain statement of what this means.** The endpoint FD verification is not merely unfinished —
at three of the four registered steps it is **not performable at that design point**, because
the perturbation the verification requires inverts cells in the warped mesh. This is exactly
the situation `DAFOAM_CHARTER.md` §1's bright line exists to expose, and it is reported, not
worked around.

---

## 3. D9-DEF-2 — A SECOND DEFECT, FOUND UNCOMMITTED, VERIFIED AND APPLIED

The killed lane had already found a defect and written its repair but **was killed before
committing it**: `d9_def2_bridge.sh` was present in the working tree and **absent from HEAD**.

**The defect.** The frozen launcher and the frozen grader disagree on the endpoint stage
directory name:

- launcher (`d9_stage_and_run.sh:207`): `sed 's/\./p/; s/-/m/'` on `1.0e-5` → **`fd_1p0em5`**
- grader (`d9_grade_SUPPLEMENT.py:147-149`, `fmt_tag`): `"%.1e" % h` → `1.0e-05` → **`fd_1p0em05`**

**Left alone the grader finds ZERO endpoint tables and returns a FALSE `NOT A RESULT` — the
right label for the wrong reason, an antecedent firing for a cause the gate mapping never
contemplated.** I confirmed this by running the grader before the bridge: it printed
*"only 0 of 4 registered endpoint steps produced a table"* while
`fd_1p0em5/d9_out.json` sits on disk with 27 `J_an` and 27 `J_fd` entries.

**The repair, and why it is legitimate.** The bridge creates a **symlink per step inside the
run tree** from the name the grader looks for to the directory the launcher wrote. It edits no
frozen file; it copies, regenerates and recomputes nothing. Against `VERIFICATION_CHARTER.md`
§2d.1's four conditions: (i) the defect is in path construction, not in the result;
(ii) it is disclosed here; (iii) the substitute is byte-identical — same inode;
(iv) **no gate, threshold, cap or label moves**, and the verdict after the bridge is still
`NOT A RESULT`, now for the true reason.

**I did not take the bridge's own assertion on trust.** Its md5 comparison
(`d9_def2_bridge.sh:25-27`) is **VACUOUS for the three crashed stages**: `md5sum` on a missing
`d9_out.json` yields an empty string through both paths, and `"" = ""` passes. I disclose that
rather than quote it. I verified the aliases **independently by inode** instead:
`fd_1p0em05→fd_1p0em5` inode 5297655, `fd_1p0em04→fd_1p0em4` 5298981,
`fd_1p0em03→fd_1p0em3` 5299627, `fd_1p0em02→fd_1p0em2` 5300157 — alias and target identical
in every case.

---

## 4. THE GRADER — VERIFIED BEFORE USE, NOT MODIFIED

Per the brief, all four instruments were hashed against their HEAD blobs **before** grading.
**All four match**, so the frozen file is the file that ran:

| instrument | md5 (working == `git show HEAD:…`) | matches pre-registration §11 |
|---|---|---|
| `d9_stage_and_run.sh` | `7bb4234f75fa53556303c0c2408bb5a7` | **yes** |
| `d9_run_script.py` | `af5f07bc1d3b4aca4fb427e089df0761` | **yes** |
| `d9_grade.py` | `7704513424bf623b024814f4b86f8f31` | **yes** |
| `d9_grade_SUPPLEMENT.py` | `baf7d69b3f6c32f64d5a47bf9d88c717` | (added at `beb90c52`) |

`python3 d9_grade_SUPPLEMENT.py --selftest` → **18/18 PASS**, and units **R** and **S** — the
two previously-silent `None` paths of the reader plant — are present in the suite and pass
(`d9_grade_SUPPLEMENT.py:583`, `:595`). **The grader was not modified.**

---

## 5. VERDICT — `NOT A RESULT`

Graded from the ORIGINAL run tree by the frozen instrument:

| gate | verdict | number |
|---|---|---|
| **G9-0** | PASS | four stage records COMPLETE; component count **27 == 27** |
| **G9-1** | PASS | `delta_repeat` = **0.000000e+00**, measured BEFORE any FD step was sized; floor falls back to representational eps·\|OBJ\| = **1.162297e-14** |
| **G9-2** | PASS | calibration major ran FIRST, `maxit=1`, `driver_iter_count=3`, OBJ = **51.68311682555106** |
| **G9-3** | **GATE FAIL** | **the SLSQP driver reported failure** (`driver_failed=True`, `driver_iter_count=47` against `maxit=20`). OBJ_baseline **52.34521691559307** → OBJ_final **50.27935096533333** |
| **G9-4** | **NOT A RESULT** | **only 1 of 4 registered endpoint steps produced a table**; a plateau needs ≥ 3 consecutive usable steps and cannot be demonstrated from 1 |

**Probe verdict = worst of G9-0…G9-6 = `NOT A RESULT`.**

**This is a registered honest outcome, written before the run** (pre-registration §5): the
document states in advance that a demonstrated plateau is required and that its absence is
`NOT A RESULT` and "a good outcome". **No plateau was manufactured by choosing a step after
seeing the numbers**, and none could be: the reference step is fixed by rule, and only one of
the four registered steps yielded a table at all.

**The G9-3 `GATE FAIL` is a second, independent negative and is not buried by the first.** The
improvement is **2.0659 (3.95 %)**, far above the noise floor — but the gate maps a *failed
driver* to `GATE FAIL` regardless, and the driver failed. SLSQP consumed 47 evaluations against
`maxit=20` and did not converge. The magnitude is **reported, never gated** (§ line 2).

---

## 6. WHAT WAS RE-FIRED, AND WHY

Because the three failures are deterministic by inspection, re-firing them cannot recover a
table. It can, and did, buy **crash triage**: proof that the failure is reproducible physics
and not a contention or fleet-kill artifact, plus proof that the one surviving table is itself
reproducible. Four stages re-fired **as a parallel batch** into a **fresh** run directory,
leaving the killed trees untouched as evidence.

- Driver: `d9_fd_replicate.sh` — **NOT a frozen instrument**, written after first compute and
  labelled as such in its own header. It **feeds no gate**; the D9 verdict above is graded from
  the original tree only. Its docker invocation is **copied verbatim** from the frozen
  launcher's `run_stage` (`d9_stage_and_run.sh:115-120`), flags included, and it is handed the
  **same** endpoint `opt_dv.json` (md5 `e921664a6e99aa838c01ed50ba89f50d`, asserted equal
  across all four members).
- **Saturation:** 4 concurrent single-core containers on **idle cores 11, 12, 14, 15** — within
  the 5-core cap. At launch the box had 7 cores pinned (D4 arm O on cpuset 5,6,7,9; plus 8, 10,
  13 busy) and 9 idle at ~77 %.
- **Memory guard, ENFORCED and MEASURED:** each member checks `free -g` before launching and
  holds while available < 6 GiB. All four cleared at 16–17 GiB available. Measured resident,
  `docker stats`: **355.6 MiB / 773.9 MiB / 744 MiB** per container — **≈ 3 GiB total resident
  across the batch, against the 8 GiB budget.** Each container capped explicitly at
  `--memory=3g --memory-swap=3g`, identical to the frozen launcher.
- **Determinism:** `np=1` throughout, `PYTHONHASHSEED=0` pinned. `decomposePar` is never
  invoked at np=1, so the trivial single domain is the effective decomposition and scotch's
  randomness is never reached — as registered (§ line 6).

Results are recorded in §7 of `RESULTS.md`.

---

## 7. ANSWER TO THE SUPERVISOR'S 19:20Z STATUS CHECK

The supervisor asked which of two things was true: (1) still doing the per-stage
strict-completion analysis, or (2) blocked and unable to say so.

**Neither. There is a third case, and it is the finding.** At 19:20Z the box showed no D9
compute because **the replication batch had just finished** — four concurrent containers ran
on cores 11, 12, 14, 15 from **19:11:18Z**, and the last of them (h=1e-5, 454 s) exited at
**≈ 19:19:30Z**. The supervisor's reading was taken roughly one minute after the batch closed.

**On "D9's FD stages are armed":** they were not armed in the sense of waiting to be fired.
The frozen launcher **ran to completion** — its final two lines, `TOTAL_SPENT_CORE_MIN=27.7833`
and `STAMP=20260825T181838Z_2370464`, are the last two lines of `ledger.txt`. Three FD stages
had already been fired and had **failed on deterministic physics**: `AnalysisError: Mesh
quality error!`, `OOMKilled=false`, face-pyramid inversion in the warped mesh at the optimised
endpoint. **Re-firing them unchanged reproduces the failure exactly, which is what happened
and what the replication proves.** The per-stage table is §1; the triage is §2.

**Not blocked. Nothing on Sanaa's desk.** And per the supervisor's own closing instruction —
*"if the honest answer is that … there is nothing to re-fire, that is a fine answer … do not
invent work to fill the budget"* — the budget was **not** filled for its own sake: 46.7667 of
110 core-min, 42.5 % of cap. The one thing worth buying was crash triage, and it bought a
bit-identical replication that turns "it crashed" into "it crashes deterministically, here,
for this reason".

**One correction the supervisor should have.** The brief's premise — partial trees left by a
launcher killed mid-build — is wrong, and acting on it as written would have been the
expensive mistake: it would have re-fired stages as *recovery*, found the same crash, and
read it as a second kill. The launcher was never killed.

---

## 8. REPORTING ORDER

**Commits**
- `50c61e8d` — *D9 RECOVERY: the launcher was NEVER KILLED — it ran to completion and THREE FD
  stages died of MESH-QUALITY CELL INVERSION at the optimised endpoint; verdict NOT A RESULT*
  (`LANE_REPORT.md`; `d9_def2_bridge.sh`, the killed lane's uncommitted work; `d9_fd_replicate.sh`)
- `f8916f36` — *D9 GRADED: NOT A RESULT, with the FD table, the plateau evidence (there is
  none), both toolchain rows, and cost calibration row C-79* (`RESULTS.md`;
  `docs/COST_CALIBRATION.md`)
- this commit — the supervisor's status check answered and the report closed

**Verdicts**
- **D9 probe verdict: `NOT A RESULT`.** G9-4: only **1 of 4** registered endpoint FD steps
  produced a table; a plateau needs ≥ 3 consecutive usable steps.
- **G9-3: `GATE FAIL`.** The SLSQP driver reported failure (`driver_failed=True`,
  `driver_iter_count=47` against `maxit=20`). `OBJ_baseline` **52.34521691559307** →
  `OBJ_final` **50.27935096533333**, improvement **2.06587 = 3.947 %**, **reported, not gated**.
- G9-0, G9-1, G9-2, G9-7: `PASS`. `delta_repeat` = **0.000000e+00**, measured before any FD
  step was sized; noise floor falls back to representational eps·\|OBJ\| = **1.162297e-14**.
- **Cost: 46.7667 core-min across every D9 container = 42.5 % of the registered 110.0 cap.
  NO OVERRUN; the verdict is not a cap-stop.** Registered chain 27.7833 core-min = **$0.0238
  DERIVED**; all containers **$0.0400 DERIVED**. `cost_basis: c7a.4xlarge at $0.0513/core-h,
  REPORTED-BY-OWNER, NOT MEASURED.` Calibration row **C-79**, id derived by hand from the HEAD
  blob inside the committing shell.
- Both toolchain rows carried: **patched BOUGHT** → `NOT A RESULT`; **shipped NOT BOUGHT**,
  with the registered reason. **D9 cannot claim a toolchain-independent result and does not.**

**Runs live** — **none.** The replication batch closed at ≈ 19:19:30Z; no D9 container is
running and no D9 process remains.

**On Sanaa's desk** — **none.**

**Blocked** — **none.**

**What I could not verify, stated plainly**
- **Whether h = 1e-5 lies in the plateau.** §4 of `RESULTS.md` gives a measured reason to doubt
  it — a near-constant `J_an − J_fd` offset of **+6.379282e-02** with only 3.26 % relative
  spread — but distinguishing an FD artifact from a genuine adjoint bias needs the step sweep
  the mesh-quality limit prevents at this design point. **The question is open.**
- **Whether the surviving components would agree under a completed sweep.** `check_totals`
  aborts the whole table when one component's perturbation breaks the mesh, so the components
  after the crash index were never evaluated at h = 1e-4, 1e-3, 1e-2. Per-component isolation
  would salvage them; **this lane did not implement it**, because it is a change to the
  measurement path and needs the supervisor's read as a diff.
- **The physical cause of the constant offset.** A sequence-correlated evaluation error of
  ≈ 1.28e-06 in the objective fully accounts for it arithmetically, but that is a **hypothesis
  I did not test** and it is not asserted as the cause.
