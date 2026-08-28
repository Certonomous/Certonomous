# CURRICULUM SO-1aR — THE RE-GRADE OF SO-1a's EXISTING ARTEFACTS: one instrument defect, five clean arms, zero new compute — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-28**. Lane: dafoam `lab-lane` (X, nineteenth session). Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

Every decision here is `[lab-attributed]`. **No agent's message is Sanaa's consent** (rule 9). Authority: Sanaa's SO-1…SO-8 programme order (standing directives 2026-08-27 §4), her 2026-08-21 blanket for CPU compute — of which this item spends none — and her **birth-requirement directive of 2026-08-28T17:01Z**, which this item is the first re-grade successor to be built under.

---

## 0. WHY THIS ITEM EXISTS

**SO-1a ran cleanly and was thrown away by one bare substring.**

| fact | value | artifact, verified by this lane from disk |
|---|---|---|
| arms | 5 of 5, `rc = 0`, `OOMKilled = false` | `<SO1a root>/ledger.txt`, `STATUS.{MESH,X-S,F-S,X-P,F-P}` |
| chain | `chain=COMPLETE` 2026-08-28T02:31:32Z | `<SO1a root>/STATUS.chain` |
| spend | **9.416 core-min** against a **75.0** ceiling | `ledger.txt`; re-derived independently by this item's own ledger reader (§10, leg B1) |
| gradient artefacts | `F-S/so1a_F.json` (8,140 B), `F-P/so1a_F.json` (8,087 B), `X-S/so1a_X.json` (1,292 B), `X-P/so1a_X.json` (1,240 B) | all four present |
| **verdict returned** | **`NOT A RESULT`, with ZERO gates evaluated** | `<SO1a root>/SO1a_grade_20260828T023132Z.json` |

Cause, read as code and confirmed against the artefact:

- `so1a_grade.py:122-125` puts the **bare substring** `"Floating point exception"` in `FATAL_TOKENS`;
- `so1a_grade.py:420` builds the C5 haystack as `text + checkMesh.log` for `SCRIPT` arms — **whole file, no line structure**;
- **line 18 of `MESH/checkMesh.log`** is, byte for byte, `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).` — OpenFOAM's ordinary startup notice that FPE trapping is **ENABLED**, i.e. the solver was **PROTECTED**. It is the **only** occurrence in that 99-line file.

**A second, smaller defect rode along.** The refusal's `"log"` field names `MESH_20260828T021739Z_1709267.log`, which contains the token **0** times (`checkMesh.log`: **1**) — the same `grep` pattern in the same invocation returning the known positive, so the zero is a measurement.

**IT CASCADED.** SO-1b read SO-1a's grade JSON, found no `gates.G5_PATCHED`, took its registered no-launch branch → `BLOCKED` at zero compute → **no artefacts at all**. SO-1c requires `optref/<ROW>/so1b_E.json` (`so1c_grade.py:985`, `:1406`) and `optref/so1b_mesh_points_sha256.txt` (`:1038`); `find /home/ubuntu -name so1b_E.json` returns **nothing**, against a live positive control in the same invocation (`find … -name so1a_F.json` → SO-1a's two files). No `*SO1b*` / `*SO1c*` run root exists. **Three rungs of Sanaa's SO ladder are stopped behind one bare substring.**

## 0.1 WHAT THIS ITEM IS, AND WHAT IT IS NOT

**SO-1a's gates are CLOSED** (`VERIFICATION_CHARTER.md` §2b) and **rule 6 forbids editing its frozen files; none is edited.** `so1a_grade.py`, `so1a_xf.py`, `so1a_run_arm.sh`, `so1a_chain_driver.sh` and SO-1a's `PREREGISTRATION.md` are **cited, never rewritten**; SO-1a's `NOT A RESULT` **stands permanently**.

**SO-1aR is a SEPARATE registration whose SUBJECT is SO-1a's EXISTING ON-DISK ARTEFACTS.** Precedent: `curriculum_D12R/PREREGISTRATION.md` §0, *"one re-registration, not four patches"*. **The difference from D12R is stated rather than blurred: D12R re-RAN its compute; SO-1aR re-READS compute already bought.** That is cheaper and it is also **weaker**, and §8 says exactly how much weaker.

## 1. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED

> **No SO-1aR output exists. `ls -d /home/ubuntu/certonomous-runs/*SO1aR*` → 0. `ls <SO1a root>/SO1aR_grade_*` → 0. `ls -d <SO1a root>/grader_controls_SO1aR` → 0.**

Checked at **2026-08-28T16:59:38Z**, before this document was written, with a **live control in the same invocation**: `ls <SO1a root>/SO1a_grade_*` returned **2**, so the glob can see a file that exists and the three zeros are measurements, not blindness.

**0 core-min of solver compute; no container launched; no queue entry.** `docker ps` reported **0** containers at 16:59:38Z. **After the first graded run, gates are CLOSED.**

**The graded run writes exactly two things and mutates nothing:** `<SO1a root>/SO1aR_grade_<stamp>.json` (+ `.out`) and `<SO1a root>/grader_controls_SO1aR/` (§6, delta 2). **No existing file in SO-1a's run root is opened for writing.** Measured after the birth run of §10: files under the run root newer than 16:52Z = **0**.

## 2. ESTABLISHED INPUTS — stated as inputs, NEVER as this item's predictions

Measured **before freezing**, most of them **through this item's own readers on the real artefacts** (§10). Listing them as predictions would be fitting a gate to an answer.

| input | reading | source |
|---|---|---|
| five arms `rc = 0`, `OOMKilled = false`; chain COMPLETE | established | `ledger.txt`, `STATUS.chain` |
| total spend | **9.416 core-min** | birth leg **B1**, this item's own `read_ledger` on the real ledger |
| the `trapFpe:` banner: present once, `checkMesh.log:18` | established | `sed -n 18p`; birth leg **B11** |
| the arm log carries the token **0** times | established | `grep -c`, with the known-positive control |
| **C5 on every artefact this item will grade: 0 real sites; benign exclusions 1 (MESH) / 0 / 0 / 0 / 0** | established | birth leg **B11**, the real scanner on the six real files |
| **age guard satisfiable on all five arms** | established | birth leg **B4**: datum resolves to `0.orig/U` (MESH) and to the **compressed twin `0/U.gz`** on all four solver arms; artefact newer by **+4 / +56 / +205 / +66 / +199 s** |
| `writeCompression` = `on` on all five arms | established | birth leg **B5** |
| the FD and adjoint tables are readable and non-degenerate | established | birth legs **B7/B8**: 20 non-zero adjoint entries per X row; 5 components, 15 non-zero FD `dCD`, 15 non-zero FD `dCL`, 5 non-zero trivial-baseline entries, CTRL row present, per F row |
| **the producer-written plant survives the real reader** | established | birth leg **B9** |
| the grader-level plant is seen on the real artefacts | established | birth leg **B10** |
| `so1b_E.json` does not exist anywhere on this box | established | `find`, with a live positive control |

**THE AGE GUARD IS THE ONE CLAUSE A RE-GRADE COULD HAVE FAILED, AND IT DOES NOT.** It dates the run allowed to produce the answer and is a property of the artefacts, unaffected by *when* the comparator runs. It was checked explicitly, because a re-grade whose age guard could not be satisfied would have to be **refused rather than registered**.

**Two predictions were RETIRED INTO THIS TABLE by the birth requirement, and the trade is stated openly.** An earlier draft registered the C5 benign counts and the grader plant as predictions. The birth requirement makes both **legs of a control that must run before grading**, so they are now measurements. **A control that must exist beats a prediction that would have been nice to score**, and pretending otherwise after running the battery would be the dishonesty the rule exists to prevent.

## 2.1 FULL DISCLOSURE OF WHAT THIS LANE READ BEFORE FREEZING

Verifying the refusal, and birthing the readers, required opening SO-1a's artefacts. This lane read:

- from `F-S`/`F-P` `so1a_F.json`: `CD_baseline = 0.02091051000679216`, `CL_baseline = 0.49876526415423195` (both rows identical to 9 s.f.), the repeat values, `eta_raw/eta_used = 3.714203840321506e-10`, `eta_floored = false`, `plant = 0.001234`, `components_requested`, `ctrl_step`, `nprocs = 1`, `n_rows = 6`, both `identity` blocks, and **two FD primal values** from the first row;
- through the birth battery, **counts and booleans only** — the battery is written so its FD/adjoint legs print no derivative value and no plateau structure (`birth()`, legs B7/B8, `values_withheld`).

**It read NO derivative, NO adjoint value, NO plateau structure, and NOT the cell count.**

> **`P2` (CL baseline ∈ 0.45–0.55) and `P3` (CD baseline ∈ 0.015–0.028) ARE NOT THIS LANE'S PREDICTIONS.** They are **carried by citation** from `curriculum_SO1a/PREREGISTRATION.md`, frozen **2026-08-27, before any container started**. The freeze that gives them weight is SO-1a's; this lane's reading the answers afterwards cannot retroactively have chosen them. A reader who finds that too fine a distinction should treat P2 and P3 as **already scored under SO-1a** and ignore them here.

## 3. GATES — SO-1a's, UNCHANGED, CARRIED BY CITATION

**Not one gate, threshold, band, cap or label is altered.**

| gate | what it decides | threshold / band | label on failure |
|---|---|---|---|
| **G-BIRTH** *(new, §10)* | every reader that contributes a graded number has been shown able to see a non-zero **through the real code path** | all legs BORN | **NOT A RESULT** — and **nothing is graded** |
| **G1** completion, arm-kind and R-RC aware | the five rule-4 clauses **printed individually per arm**: C1 rc value, C2 terminal marker (`End`/`Mesh OK.`), C3 artefact present, C4 age guard, **C5 no fatal token** | any clause failing → REFUSE | **NOT A RESULT** |
| **G-M2** mesh identity | `cells == 4032` | exact | **GATE FAIL** |
| **G5** / **G5c** the bright line, per row | reference = the **middle** of three registered steps; **PLATEAU** = middle agrees with ≥1 neighbour to **10 %**; **band D** = per-component **≤ 5.0 %**, **same sign**; **band E** = aggregate vector-relative **≤ 5.0 %**. `G5` on `CD`, `G5c` on the equality-constraint `CL`, **graded as equals** | 5.0 / 5.0 / 10 % | inside → **PASS**, outside → **GATE FAIL**, fewer than **3** graded components → **NOT A RESULT** |
| **G-TB** the `DAFOAM_CHARTER.md` §4 trivial baseline | the same probe at a deliberately wrong step (`shape` 1e-8, `patchV` 1e-6); if **> 1** of 5 components passes band D there, the gate cannot fail | `TB_MAX_PASSING = 1` | the row's G5 verdict is **WITHDRAWN to NOT A RESULT** — it can only turn PASS or GATE FAIL **into** NOT A RESULT, never the reverse |
| **G6** duality / dot-product | **NOT MEASURED** — the tutorial exposes none; named, never inferred | — | — |
| **G9** toolchain per row | **BY HASH, NEVER A VERSION STRING** — image `DIGEST` + printed `libidwarp.so` md5 + the md5 **inside** the artefact | exact | **GATE FAIL** |
| **G10** caps | every row `core_min ≤` its cap; sum `≤ 75.0` | §5 | **GATE FAIL** |
| **G12** placement | `cpuset == 9` on every row; at np = 1 the delivered-cores floor does not apply and is not composed | exact | **GATE FAIL** |
| DIVERGENCE shipped-vs-patched | **REPORTED, NEVER GATED** | — | — |

**Verdict vocabulary is rule 1's and only rule 1's**: `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`.

### 3.1 THE FD BRIGHT LINE — an FD table beside every adjoint gradient

`DAFOAM_CHARTER.md` §5. **Every adjoint number this item reports has a central-FD table beside it**, on the same components, from the same run, on the same image: `X-S`↔`F-S` (SHIPPED), `X-P`↔`F-P` (PATCHED). The FD table is a **three-step** table per component with a **plateau requirement**, not a single step; a component with no plateau is **NOT A RESULT**, not a number with a caveat. **The trivial baseline is bought and graded (G-TB)**, so a gate that cannot fail is detected rather than trusted. **No adjoint value is reported without its FD partner and its plateau state.**

### 3.2 THE TWO ROWS — `DAFOAM_CHARTER.md` §6, identity BY HASH

| row | image digest | `libidwarp.so` md5 | arms |
|---|---|---|---|
| **SHIPPED** | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` | MESH, X-S, F-S |
| **PATCHED** | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` | X-P, F-P |

**No version string appears anywhere in G9.** The ledger's md5 is cross-checked against the md5 the producer wrote **inside** the artefact, so a mislabelled image fails the gate rather than passing it. Both digests were re-read from the real ledger by this item's own reader (leg **B1**) and match.

## 4. NUMBERED PREDICTIONS — points and bands

**Scored, never adjusted.** A MISS is a finding, not a reason to move a band. **Three predictions, deliberately few**, because §2 records honestly how much the birth battery established before the freeze.

| # | prediction | point | band / criterion |
|---|---|---|---|
| **R1** | **G1 completion PASSES on all five arms** and the item verdict is **NOT** `NOT A RESULT` — i.e. gates are actually evaluated. **Genuinely open**: C1/C4/C5 and OOMKilled are established (§2), but **this lane has NOT read the C2 terminal markers** (`SO1A_X_WRITTEN` / `SO1A_F_WRITTEN` on the four solver arms, `^Mesh OK.$` on MESH) or the C3 artefact-name clause, and did not look | 5 of 5 arms | binary. A MISS means the C5 defect was not the only thing wrong, and the re-grade has found a second one — **which is a result, not a failure** |
| **R3** | the item's **total instrument cost** stays inside its cap | ≤ **1.0 core-min** | §9; an overrun **stops the run** |
| **R4** | **no G5/G5c component is refused for a missing FD plateau** on either row | 0 of 10 component-objective pairs | a MISS is a **finding about the registered step ladder**, reported, never repaired by widening a band. The birth battery was written to withhold plateau structure precisely so this stays open |

**Carried by citation** from `curriculum_SO1a/PREREGISTRATION.md` (frozen 2026-08-27, pre-compute): `P1` cells = 4032 · `P2` CL ∈ (0.45, 0.55) · `P3` CD ∈ (0.015, 0.028) · `P4` PATCHED row CD passes 5/5 · `P5` SHIPPED `shape[6]` outside band D or sign-flipped · `P6` PATCHED CL aggregate ≤ 1.0 % · `P7` the trivial baseline fails on ≥ 4 of 5 PATCHED components · `P8` total core-min ∈ (4.0, 22.0) · `P8b` MESH wall ≤ 120 s · `P9` the age datum resolves to the compressed twin on every solver arm. **`P2`/`P3` are flagged in §2.1; `P8`/`P9` are already established in §2 and are therefore corroborations, not predictions, in this document.**

## 5. CAPS AND CEILING — SO-1a's, unchanged

`MESH 5.0` · `X-S 10.0` · `F-S 25.0` · `X-P 10.0` · `F-P 25.0`; item ceiling **75.0 core-min**, asserted by the comparator to equal the sum. **These grade SO-1a's already-spent 9.416 core-min; they are not a budget for this item**, whose own budget is §9.

## 6. THE INSTRUMENT — `so1ar_grade.py`, and its EXACTLY THREE deltas

Derived from `so1a_grade.py` (md5 `6966d19eeccd275b45fe9a5492eef6d2`), **verified identical to the HEAD blob `1b87f8dcb5108d4eab037c9684514f8f3f29c12a`** by `git hash-object` against `git rev-parse HEAD:<path>` **before** deriving — the file derived from **is** the file that was frozen. Registered deltas: `so1ar_grade_DELTAS_from_so1a_grade.diff`, **17 hunks**.

### DELTA 1 — C5, THE ONE GRADING CHANGE. **PORTED, NOT REINVENTED.**

Ported in shape from `curriculum_SO1c/so1c_grade.py` amendment R6 (commit `42c7c8c3`):

1. **`FATAL_TOKENS` keeps every original token** and **adds** `Foam::sigFpe::sigHandler`, adopted from `sdk/chief_engineer/head_engineer.py:188` — an **additional** refusal on a genuine crash signature, which can only **strengthen** detection.
2. **That file's `^` line anchor is DELIBERATELY NOT adopted.** The realistic multi-rank FPE report is OpenMPI's — `mpirun noticed that process rank 2 exited on signal 8 (Floating point exception).` — **neither line-initial nor carrying the handler symbol**; `^Floating point exception` would **miss** it. **An over-narrow exclusion costs a FALSE REFUSAL; an over-narrow positive anchor costs a MISSED CRASH.** The false refusal is the survivable error, so an **exclusion list** is used. Driven by **U43**.
3. **`fatal_token_sites(text, source)` scans LINE BY LINE and PER SOURCE FILE**, so a refusal names the **file and line** carrying the hit — closing SO-1a's second defect. Driven by **U40**, **U44**.
4. **`BENIGN_LINE_PATTERNS` holds exactly ONE entry**, `^\s*trapFpe:\s`, applied **per line**, so a benign banner on line 18 can never suppress a real crash on line 400. Driven by **U41**, **U44**, **U47**.
5. **EVERY EXCLUSION IS COUNTED AND PRINTED ON THE PASS RECORD** — count, file, line, tokens, text, reason. **A suppression a reader cannot see is the same defect wearing the other hat.** Driven by **U38**, **U46**.

### DELTA 2 — THE CONTROL WRITE PATH. **NOT A GRADING CHANGE, DISCLOSED RATHER THAN SMUGGLED.**

`grader_plant_control()` wrote to `<root>/grader_controls/`; a re-grade runs a **second** comparator against a root a **first** one already owns, so the path is namespaced to `<root>/grader_controls_SO1aR/`. **Alters no gate, threshold, band, cap or label.** Driven by **U49**. **This is a departure from "the one instrument change and nothing beyond it", flagged here for the supervisor to accept or reject rather than left to be found in the diff.**

### DELTA 3 — `read_cells()`, EXTRACTED TO A NAME. **NO BEHAVIOUR CHANGE.**

The cell-count regex was inline in `grade()`. It is now a named function called by `grade()` **and** by the birth battery, **so the control drives the same reader the grading path uses instead of a copy of it**. Re-implementing a reader inside its own control is the self-referential defect the birth directive names; this delta exists to avoid it. Driven by **B6**.

### Mechanical, non-grading renames (complete list)

`ITEM "SO1a" → "SO1aR"` · the selftest tmpdir name and the usage string · **U21's producer path** now points at SO-1a's `so1a_xf.py`, the file that actually wrote the artefacts being re-graded · `EXPECTED_UNITS 35 → 54` · the module docstring · the new `--birth` / `--workdir` arguments. **`BASE` is UNCHANGED and points at SO-1a's run root, deliberately and by registration** — that is the subject of the item.

### The retained defect, kept as evidence

SO-1a's whole-file predicate `fatal_tokens_in()` is **kept verbatim and kept OFF the grading path**, so the selftest can run the **defect** and the **repair** on the **same real bytes** and print the contrast. That it is off the path is **checked by AST over the module's own source** in **U48**, not asserted.

## 7. THE FREEZE

| file | md5 | role |
|---|---|---|
| `so1ar_grade.py` | ``d2051f59089f3e71ae0fbfa315c3b784`` | the comparator. **The grading path is fixed at this commit**; hash the worktree file against the committed blob before grading (rule 2) |
| `so1ar_grade_DELTAS_from_so1a_grade.diff` | ``eb62982ff74839f9e3c5b03abfebbd65`` | the registered deltas, 17 hunks |
| `so1ar_fixture_REAL_SO1a_MESH_checkMesh.log` | `22aa9cfa6725eb904123aefaebf63cfd` | **byte-identical copy** of `<SO1a root>/MESH/checkMesh.log` — 99 lines, banner at line 18 |
| `so1ar_fixture_REAL_D12R2W3_S0_solver.log` | `ccc4f40fa0e1c1849bb7bc15a4042d47` | **byte-identical copy** of `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady/S0_20260828T162848Z_1898005.log` — a **real 339-line np-4 solver log this lane did not produce**, 4 banners, 5 `End` lines, **0 real fatal tokens**. Opened read-only; nothing else in that run root was touched |
| `so1ar_grade_selftest_evidence.txt` | — | the selftest under both interpreters **and the birth run on the real artefacts**, verbatim |

**Both fixture md5s are frozen inside the comparator and CHECKED BY A UNIT (U36)**, so a fixture that drifts from the artefact it claims to be **fails the selftest** rather than quietly becoming a different test.

**Instruments NOT re-frozen because they are not re-run:** `so1a_xf.py`, `so1a_run_arm.sh`, `so1a_chain_driver.sh`, `so1a_runScript.py`, `so1a_decomposeParDict`. They are SO-1a's; this item launches nothing. **`so1a_run_arm.sh` is nonetheless EXECUTED IN PART** — see leg B2 in §10 — and that is deliberate: its own emitting statement is what produces the ledger row the birth battery reads back.

## 8. WHAT A RE-GRADE MAY NOT CONCLUDE

**This is the price of not re-running, stated before any number is produced.**

1. **NOTHING about reproducibility.** One set of artefacts, one chain, one night. A PASS is a statement about **that run**, not about it being repeatable. Any reproducibility claim needs a second chain and is **not** registered here.
2. **NOTHING about the mesh** beyond what SO-1a's MESH arm already wrote. **No mesh-convergence study is bought**; `G-M2` is an **identity** check, not a **convergence** check. **No Roache triple exists, so no GCI is quoted and none may be** (rule 5).
3. **NOTHING SO-1a's own scope excluded**: `G6` duality stays **NOT MEASURED**; every arm is np = 1, so **no statement about np = 4 is available** — A4's measured 16,600× decomposition effect is *removed from the chain*, not shown absent; no optimiser is run; RAE2822 transonic is a different item.
4. **NOTHING about the launcher.** The artefacts were produced under **SO-1a's** launcher, chain driver and containers; SO-1aR neither re-verifies nor re-certifies that infrastructure.
5. **It cannot rehabilitate SO-1a's verdict.** SO-1a is `NOT A RESULT` **permanently**. SO-1aR produces **its own** verdict about the **same artefacts**: two records, one run, and the record says so.
6. **A PASS here does not by itself make SO-1b runnable.** SO-1b needs `gates.G5_PATCHED` from a grade JSON its own registered branch reads. **Whether SO-1b may read SO-1aR's JSON instead of SO-1a's is a change to SO-1b's registered input and is the supervisor's call, not this lane's.** Named here as the next decision; not taken here.
7. **The C5 repair is not retroactive.** Registered for **this** item only. **A post-compute edit to a frozen comparator is barred by rule 2** and none is made.
8. **The birth battery certifies READERS, not PHYSICS.** BORN means each reader was shown seeing a non-zero through the real path. It says nothing about whether the gradients are right — that is what §3's gates are for.

## 9. COST — rule 12

**Solver compute: 0.000 core-min.** No container started, no queue entry made. The 9.416 core-min this item grades was **already spent under SO-1a** and is **not re-charged** — double-counting would corrupt the ladder's ledger.

| line | ranks | wall | core-min | basis |
|---|---|---|---|---|
| `--selftest`, `python3` | 1 | 0.489 s | **0.0082** | **MEASURED** (`so1ar_grade_selftest_evidence.txt`) |
| `--selftest`, `python3 -O` | 1 | 0.585 s | **0.0098** | **MEASURED**, same |
| `--birth --root <SO1a root>` | 1 | 0.122 s | **0.0020** | **MEASURED**, same — the battery of §10, which **grades nothing** |
| earlier development selftests | 1 | 0.77 s | **0.0129** | **MEASURED**, this session |
| **spent to the freeze** | | | **≈ 0.033** | measured |
| the graded run (`--root`, once) | 1 | ≤ 10 s predicted | ≤ **0.167** | **PREDICTED**; basis: the selftest builds and grades ~50 fixture roots plus 4 birth batteries in 0.489 s, and the birth battery alone reads the real root in 0.122 s |
| repeats, re-verify of the frozen hash | 1 | — | ≤ **0.30** | predicted headroom |
| **ITEM CAP** | | | **1.0 core-min** | **an overrun STOPS the run; it does not get a new budget** |

**Dollars: 1.0 core-min = 0.01667 core-h × $0.0513/core-h = $0.00086 — DERIVED, NOT MEASURED.** `cost_basis`: **REPORTED-BY-OWNER, NOT MEASURED**; the rate is Sanaa's owner-stated c7a.4xlarge figure (2026-08-21/22, corroborated at `Xiao2016_EnKF/PREREGISTRATION.md:197`), and **the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). **No GPU is used**, so the GPU carve-out does not apply.

**Estimate-versus-actual calibration (rule 12; Sanaa 2026-08-23) is OWED AT COMPLETION.** When the graded run lands: actual instrument core-min against the ≤ 1.0 cap, the ratio actual/predicted, the gap attributed, and a row appended to `docs/COST_CALIBRATION.md`. **A completion report without that comparison is incomplete.**

## 10. THE BIRTH REQUIREMENT — Sanaa, 2026-08-28T17:01Z

> *"A control defined in terms of the thing it controls is not a control. A planted control must travel the real production path — written by the real producer's code, read through the real reader — and prove the instrument sees a non-zero the same way reality would deliver one. … no instrument grades anything until that answer is yes, demonstrated."*

**SO-1aR is a newborn comparator and the first re-grade successor built under this rule. The rule is ENFORCED IN CODE, NOT PROMISED IN THIS DOCUMENT.** `graded()` is the only grading entry point; it runs `birth(root, workdir)` **first** and **REFUSES the whole item** (`G-BIRTH` → `NOT A RESULT`, nothing graded) if any leg fails. The birth record is embedded in the output JSON.

**Every reader that contributes a graded number, and its birth status:**

| leg | reader | producer of the artefact it reads | the non-zero it was shown seeing | BORN? |
|---|---|---|---|---|
| **B1** | `read_ledger` | `so1a_run_arm.sh`, the real run | five real rows, every `core_min > 0`, both real digests | **BORN** |
| **B2a** | `read_ledger` (rc value) | **`so1a_run_arm.sh:482` — THE PRODUCER'S OWN `echo`, LIFTED BY EXACT CONTENT MATCH AND EXECUTED** | `rc = 1`, `inspect_exit = 1` read back | **BORN** |
| **B2b** | `read_ledger` (OOMKilled) | same, executed | `oomkilled = true` read back | **BORN** |
| **B3** | `inspect_file_fallback` | `docker inspect` | — | **NOT BORN, AND BARRED** |
| **B4** | `arm_datum` + `resolve_datum_ref` | `so1a_run_arm.sh` (datum) + the solver's own time-0 write | real epoch datum, strictly positive age delta on every arm, twin resolution recorded | **BORN** |
| **B5** | `read_write_compression` | the tutorial's `system/controlDict` | a real keyword value on every arm, with its file named | **BORN** |
| **B6** | `read_cells` *(delta 3 — the same function `grade()` calls)* | OpenFOAM `checkMesh` in the SHIPPED container | a positive integer cell count (**value withheld**: P1 is registered) | **BORN** |
| **B7** | `read_X` | `so1a_xf.py -mode X`, in the real containers | counted non-zero adjoint entries (**values withheld**) | **BORN** |
| **B8** | `read_F` | `so1a_xf.py -mode F`, in the real containers | counted non-zero FD `dCD`, `dCL` and trivial-baseline entries (**values and plateau structure withheld**: R4 is registered) | **BORN** |
| **B9** | `read_F` + `ctrl_control` | **`so1a_xf.py`, WHICH INSERTED THE PLANT DURING THE REAL RUN** | the CTRL row's planted derivative reads exactly `PLANT/(2·ctrl_step)` while its unplanted twin reads `0.0` — **the reader shown seeing a non-zero AND a zero, from the same file, through the same code path** | **BORN** |
| **B10** | `read_F` | the real artefacts, replanted by the comparator's own registered control code | every physical `dCD` moves by exactly `PLANT` on re-read | **BORN** |
| **B11** | `fatal_token_sites` | the real containers | the same scanner shown **refusing** on real crash bytes (U41–U44, U47) and here **reading** the six real files, exclusions counted | **BORN** |

**B3 IS THE HONEST GAP, AND IT IS NAMED RATHER THAN PAPERED.** `inspect_file_fallback`'s producer is a `docker inspect` command that cannot be driven without launching a container, and **every one of the 53 `.inspect.txt` files on this box records exit 0**, so no real non-zero record exists to birth it from. Rather than hand-build a file that would agree with the reader by construction, **the reader is declared NOT BORN and BARRED from contributing a graded number.** The leg passes only by proving **the fallback is never reached on this root** — all five arms carry ledger rows. **If a row were missing, this item would REFUSE rather than grade through an unborn reader**, and that is driven by **U51**.

**The two failure modes Sanaa named are structurally excluded, and each is driven:**

- **Self-reference (D6R's mutation control, defined in terms of the tuple it empties):** no leg re-implements the reader it controls — **delta 3 exists precisely to remove the last copy** — and **U53 is a control on the control**: point the producer lookup at a script without the anchor and the B2 legs go **NOT BORN**, closing the gate, instead of silently falling back to a hand-built row.
- **Schema drift (AV2R's fixture writing a field into a schema the producer never emits):** **B2 does not write a ledger row at all — it executes the producer's own emitting statement**, lifted from the frozen `so1a_run_arm.sh` by exact content match, never by line number. Producer and reader are therefore compared against **each other**, not against this lane's transcription. Driven by **U52**.

**Result on the real artefacts, 2026-08-28, `--birth --root <SO1a root>`, rc = 0: `BORN`, 12 legs, 12 born.** Files under the run root newer than 16:52Z: **0** — the battery writes its control copies to a workdir **outside** what it grades.

## 10.1 THE C5 PROOF, IN BOTH DIRECTIONS, ON REAL BYTES

| direction | driven by | outcome required |
|---|---|---|
| the benign banner **alone must NOT refuse** | **U37**, **U38** | item PASS, MESH C5 PASS, **exactly 1** exclusion, counted and printed with file, line, token and reason |
| **the UNREPAIRED logic must FAIL that same case** | **U39** | SO-1a's **frozen comparator is imported and executed** on the **same fixture root** and must **REFUSE** with `["Floating point exception"]` on arm MESH. **The contrast is executed, not described** |
| the unrepaired refusal's second defect | **U40** | the old `log` field names the arm log, shown to contain **0** occurrences of the token it cites |
| a real `FOAM FATAL ERROR` **must still refuse** | **U41** | REFUSAL |
| a real **SIGFPE stack trace** with no shell line | **U42** | REFUSAL; the handler token is **hard-coded in the unit**, so deleting it from `FATAL_TOKENS` fails the unit |
| OpenMPI's `exited on signal 8 (Floating point exception)` | **U43** | REFUSAL — the measured reason the `^` anchor was not adopted |
| a real crash **BESIDE** the banner | **U44**, **U47** | the refusal names **one** site, in `checkMesh.log`, at the crash's line; on the real 339-line log the four banners suppress nothing |
| the line split **loses no token** | **U45** | each of the **10** registered tokens, planted one at a time, refuses |
| a real log the lane did not produce reads clean | **U46** | item PASS, **exactly 4** benign exclusions counted |
| the predicate-level contrast on SO-1a's **own real 99-line file** | **U48** | unrepaired returns `["Floating point exception"]`; repaired returns **0 sites, 1 benign at line 18**; and the unrepaired predicate is referenced by **no** grading-path function, **by AST** |
| the fixtures have not drifted | **U36** | both md5s match §7 |
| the control write path cannot collide | **U49** | writes under `grader_controls_SO1aR/` |
| the birth gate opens on a clean root | **U50** | 12 legs, all born, each naming producer, reader and non-zero |
| **the birth gate CLOSES** | **U51**, **U53**, **U54** | a missing ledger row, a drifted producer anchor, and a broken producer-written plant each **REFUSE** and grade nothing |
| the grader-level plant (inherited) | **U19** | every physical `dCD` moves by exactly `PLANT`; if not, **NOT A RESULT** |

**Selftest, both interpreters, `__pycache__` cleared before each:** `python3` **54/54, 0 failures, rc = 0**; `python3 -O` **54/54, 0 failures, rc = 0**. **`ast.Assert` nodes in the comparator: 0** (L-332), counted by the comparator against its own source. Verbatim in `so1ar_grade_selftest_evidence.txt`.

> **COUNTING UNITS MEASURES THIS SELFTEST'S SIZE, NOT ITS COVERAGE.** 54 is a size. The coverage claim is the two tables above.

## 11. HOW IT IS RUN, AND BY WHOM

    python3 cases/dafoam/ladder-a/A1/curriculum_SO1aR/so1ar_grade.py \
        --root /home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient \
        --out  <root>/SO1aR_grade_<stamp>.json

**The comparator's exit status is NOT the verdict** (`rc = 2` is a registered refusal — rule 4's *"comparators refuse rather than degrade"*). The verdict is the `verdict` field of the JSON, from rule 1's vocabulary only. `--birth --root <root>` runs the §10 battery alone and grades nothing.

**THIS LANE DID NOT RUN THE GRADED PATH AND IS NOT ENQUEUEING IT.** Freezing is this lane's whole job; the graded run is the supervisor's call after his personal check-1 read of `so1ar_grade_DELTAS_from_so1a_grade.diff` **as a diff** (`SUPERVISION_CHARTER.md` §3 — a check that may never be delegated). **`verification/queue/` was not opened, read or written.** D6R was live on this box throughout and was not touched; `docker ps` read 0 containers at the freeze check.

## 12. FILING

**Nothing here is filed, sent, uploaded, registered, posted or commented** (rule 7). Nothing leaves the box (rule 8). No scratch path is cited by this document (rule 13). The two fixtures are copies **into** the repository; the run roots they came from were opened read-only.
