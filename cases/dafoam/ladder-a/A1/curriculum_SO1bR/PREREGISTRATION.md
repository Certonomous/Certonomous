# SO-1bR — PRE-REGISTRATION (FROZEN). SO-1b's successor: the precondition re-registered against SO-1aR

**Item:** `SO1bR` — successor to `SO1b` on Sanaa's shape-optimisation ladder SO-1.
**Team:** dafoam. **Lane:** AA. **Date:** 2026-08-30.
**Solver compute: ZERO.** Nothing meshed, nothing solved, no container, no GPU.
**Provenance:** the dafoam supervisor's ruling of 2026-08-28 — *SO-1b does not launch as
frozen; the route is a new item whose registered input is SO-1aR's grade JSON.* That
ruling is implemented here and is not re-opened.

**STAGE 1 ONLY.** This document freezes the SO-1bR **precondition instruments** and their
verdict. It does **not** freeze a chain driver or an arm launcher, and it does not claim
to — see §12, which is the section to read before believing this item is ready to run.

---

## 1. THE ROOT CAUSE, ONE SENTENCE, MEASURED FROM DISK

**A frozen dependency check whose glob cannot match the artefact that now satisfies it in
substance.**

SO-1b's chain driver evaluates its dependency on SO-1a inside an inline heredoc
(`so1b_chain_driver.sh:102-138`) that globs `SO1a_grade_*.json` under SO-1a's run root.
On **2026-08-28T02:31:50Z** that branch fired for real and closed the item at rc = 7,
zero core-minutes, with the reading recorded in `curriculum_SO1b/G_SO1A.20260828T023149Z.txt`:

> `REFUSE no_gates.G5_PATCHED in=SO1a_grade_20260828T023132Z.json`

**That was the no-launch branch WORKING.** The 317-byte `SO1a_grade_20260828T023132Z.json`
genuinely carries no `gates.G5_PATCHED`.

**What changed:** SO-1a's successor SO-1aR produced
`SO1aR_grade_20260828T171830Z.json`, which **does** carry `gates.G5_PATCHED`, reading
`PASS` on both the objective gradient and the constraint gradient. **The precondition is
satisfied in SUBSTANCE.** It remains unsatisfiable in FORM: the literal `_` after `SO1a`
in the frozen pattern forbids a match against `SO1aR_grade_*.json`.

**Not argued — EXECUTED.** `so1br_precondition.py:frozen_glob_can_see()` runs the frozen
driver's own glob against the run root and reports what it matched. Unit **U14**:

> pattern `SO1a_grade_*.json` matched `['SO1a_grade_20260828T023132Z.json']`;
> `can_see_registered_input = False`.

Relaunching SO-1b unchanged therefore fires the same branch into a **guaranteed outcome**.

### 1a. THE REPAIR THAT IS FORBIDDEN, NAMED SO IT IS NOT QUIETLY TAKEN

Copying or renaming SO-1aR's grade JSON to `SO1a_grade_*.json` would make a **successor's**
verdict masquerade as the **original's** inside a preserved artefact set. That is evidence
tampering however well intentioned. It is not done here, and the preserved root is proved
unchanged by md5 before and after every recorded execution (§8).

## 2. THE FORWARD-AD QUESTION, ANSWERED BEFORE THE FREEZE — NOT AFTER

AV2RG measured on 2026-08-30 that DAFoam's **forward-AD primal does not converge** on this
case at these settings: 20 FAD readings, zero graded, item `BLOCKED`. If SO-1bR depended
anywhere on a forward-AD reference **it would block the same way**, and freezing a
guaranteed block would be the same defect this item exists to correct.

**ANSWER: SO-1bR HAS NO FORWARD-AD DEPENDENCY ANYWHERE.** Measured four ways, and unit
**U46** runs the scan rather than restating it:

| channel | reading |
|---|---|
| Derivative mode, both instruments | `prob.setup(mode="rev")` — **REVERSE**, at `so1b_of.py:261` and `so1b_runScript.py:183`. No `mode="fwd"` anywhere |
| Token scan over the whole instrument set | **0 hits** for `forwardAD`, `useAD`, `adMode`, `runMode`, `complexify`, `dFdWSeed`, `seedVec`, `mode="fwd"` across `so1b_of.py`, `so1b_runScript.py`, `so1b_grade.py`, `so1b_run_arm.sh`, `so1b_chain_driver.sh` |
| The gradient channels actually graded | the **discrete adjoint** (`adjEqnOption` GMRES, `so1b_runScript.py:69`) against a **central-difference** table, `(f(x+h) − f(x−h)) / 2h` at `so1b_of.py:567` |
| The one place forward AD could have entered | `G6`, the dot-product / duality test — already **`NOT MEASURED` and NEVER COMPOSED** in the frozen grader (`so1b_grade.py:1185-1187`), which names AV-2's forward-AD failure as the reason |

**The frozen grader had already closed this door before AV2RG measured it.** `G6` is named
and excluded from composition, so no SO-1bR verdict can depend on it. **SO-1bR may be
frozen.**

## 3. `shape[6]` — WHAT IT MEANS FOR SO-1bR'S CLAIMS, STATED BEFORE ANY RUN

`shape[6]`, the leading-edge FFD combo mode, is now fingered by three independent
instruments as the worst component on this case. **It IS in the registered component set**
(`so1b_grade.py:193`, driven as unit **U43**), so this must be argued, not assumed away.

**What is measured, per toolchain row:**

| source | row | reading on `shape[6]` |
|---|---|---|
| SO-1aR grade, `G5_SHIPPED.G5_CD` | SHIPPED | **637.7570 %, SIGN-FLIPPED** — `GATE FAIL` |
| SO-1aR grade, `G5_SHIPPED.G5c_CL` | SHIPPED | **19.8033 %** — `GATE FAIL` |
| SO-1aR grade, `G5_PATCHED.G5_CD` | PATCHED | **0.6992 %** — `PASS` |
| SO-1aR grade, `G5_PATCHED.G5c_CL` | PATCHED | **0.0876 %** — `PASS` |
| `A_stepsize_study.md` (2026-07-28) | SHIPPED, np = 2 | *"wrong sign and unstable across nearly the whole range"*, **82.7 %** of the squared-error contribution; *"there is no step at which idx6 is a trustworthy estimate"* |

**THE ARGUMENT.** The `shape[6]` pathology is a **SHIPPED-toolchain artefact**, not an
intrinsic property of the case: the PATCHED row measures the same component on the same
mesh at the same steps at **0.6992 %**, three orders better and with no sign flip. That is
precisely what the two-row structure exists to separate, and it is why SO-1bR's
precondition keys on the PATCHED row.

**THE HONEST LIMITS, REGISTERED HERE BECAUSE THEY WILL NOT BE ADMISSIBLE LATER:**

1. **The step study is not a statement about the registered steps.** Its two hard failures
   are at `h = 5e-2` and `h = 1e-1`; the registered `shape` steps are `1e-2 / 1e-3 / 1e-4`,
   all inside the range it recorded as `ok`. It is also at **np = 2**, while every SO-1b arm
   is np = 1.
2. **SO-1a measured at the BASELINE; SO-1b measures at the OPTIMUM.** The optimum is a
   different geometry and the leading edge has moved. **Nothing here licenses assuming the
   PATCHED plateau at the baseline survives to the optimum.** The frozen grader already
   handles the failure mode without a new clause: a component whose middle step does not
   plateau within `PLATEAU_TOL_PCT = 10 %` is not graded, and `MIN_GRADED = 3` of five keeps
   the row gradeable if `shape[6]` drops out. **REGISTERED PREDICTION P-S6:** `shape[6]`
   plateaus at the optimum on the PATCHED row. Scored HIT/MISS, never adjusted.
3. **A SHIPPED row that fails at the optimum is the expected finding, not a defect** — the
   same shape SO-1a P5 predicted in writing and then measured.

## 4. ⚠ A CORRECTION TO THE ASSIGNING BRIEF, MADE BEFORE THE FREEZE

The brief states the shipped failure is *"localised to `shape[6]`"*. **Measured against the
artefact, that is true of the sign flip and of the dominant magnitude, and it is not the
whole failure.**

* `G5_SHIPPED.G5_CD` fails band D on **TWO** components: `shape[6]` at 637.7570 %
  (sign-flipped) **and `shape[0]` at 11.9330 %** (no sign flip). 3 of 5 pass.
* `G5_SHIPPED.G5c_CL` fails band D on **one**: `shape[6]` at 19.8033 %. 4 of 5 pass.
* On the PATCHED row `shape[0]` reads **0.0124 %** on CD — so `shape[0]` is a
  **shipped-only** failure too, and the localisation claim should read *"the sign flip is
  localised to `shape[6]`; the band-D failure set on CD is `{shape[0], shape[6]}`"*.

`A_stepsize_study.md` independently flags `idx0`, `idx1` and `idx6`, which corroborates the
two-component reading. The corrected set is what `G-PROV` carries downstream (§5).

## 5. G-PROV — THE TRAVELLING SHIPPED `GATE FAIL`, ENFORCED IN CODE

SO-1bR's precondition keys on the **PATCHED** row while the upstream **ITEM** verdict is
`GATE FAIL`. Building a downstream rung on the PASS row of a `GATE FAIL` item **is
legitimate** — the two-row structure exists precisely so the patched row can carry work the
shipped row cannot. **But the shipped `GATE FAIL` must travel with every downstream claim
SO-1bR makes.**

**A REQUIREMENT IN PROSE HAS NO CALL SITES** (L-405's general form). It is therefore
enforced by `so1br_precondition.py:require_travelling_provenance()`, which is the **only**
exit from the comparator (`so1br_grade.py:emit()`), and which **REFUSES** unless:

1. the structured `upstream_provenance` block is present in the output;
2. its SHIPPED row status is present **and reads exactly `GATE FAIL`**;
3. it carries the SHIPPED **per-gate detail** — verdict, aggregate, `n_pass/n_graded`,
   sign flips, band D and band E, the worst component and the full band-D failure list —
   because the row word alone invites a reader to assume a marginal miss, and **it was not
   marginal**;
4. a human-readable `verdict_line` is present and **contains the literal bytes
   `GATE FAIL`**; and
5. `verdict_line` is **byte-identical** to the bytes the module composed for it.

**Clause 5 is not decoration.** On 2026-08-30 this lab lost the words `GATE FAIL` from
`docs/LAB_STATE.md` — its only handoff channel between sessions — because an unquoted
heredoc command-substituted a backticked token to nothing (`e779bdc7`), and a sibling
defect ate a backticked `Queue:` line from a charter (L-403). The remedy landed as
`scripts/append_block.py` (L-405): **compare the landed bytes against the intended bytes.**
This item's whole subject is a `GATE FAIL` that must survive travel, so the same comparison
is made on the item's own output. Units **U24** and **U25** drive both halves.

**RULE 1 IS RESPECTED AND NO NEW VERDICT WORD IS COINED.** `verdict` stays exactly one of
the six and is never decorated. The provenance travels in a separate mandatory field and in
`verdict_line`, which is a **row description**, not a verdict word — the construction the
verification supervisor ruled legitimate for SO-1aR's split verdict at `db0b0124`. A word
outside the fixed vocabulary refuses (**U27**).

**THE REGISTERED SENTENCE**, composed in Python and never by a shell:

> `SO1bR <VERDICT> -- RESTS ON THE PATCHED ROW OF CURRICULUM-SO1aR, WHOSE ITEM VERDICT IS
> GATE FAIL AND WHOSE SHIPPED ROW IS GATE FAIL: G5_CD GATE FAIL 3/5 aggregate 40.4814% with
> 1 sign flip(s), G5c_CL GATE FAIL 4/5 aggregate 4.3270%, worst component shape[6] at
> 637.7570% sign_flip=True.  THE SHIPPED TOOLCHAIN FAILED THE GRADIENT THIS RESULT RESTS ON.`

**STRUCTURAL REQUIREMENT OF THE RECORD, registered here:** any `RESULTS.md`, table or board
row that quotes an SO-1bR verdict must carry that sentence or the block it is composed from.
An SO-1bR record that omits it is **not a record of this item**.

## 6. G-C5R — THE `trapFpe` ANSWER FOR `so1b_grade.py`, AND THE REPAIR

**MEASURED, NOT SUSPECTED. `so1b_grade.py` DOES carry the bare substring scan.**

* `so1b_grade.py:131-133` lists `"Floating point exception"` in `FATAL_TOKENS`.
* `so1b_grade.py:420-423` tests it with a **whole-file substring scan**, `t in text`.
* `so1b_grade.py:490` builds the C5 haystack for a **SCRIPT** arm as the arm log **plus the
  artefact**, and the MESH arm's artefact is `checkMesh.log` (`so1b_grade.py:116`).
* OpenFOAM's own banner — `trapFpe: Floating point exception trapping enabled
  (FOAM_SIGFPE).` — stands at **line 18** of SO-1a's `MESH/checkMesh.log`
  (md5 `22aa9cfa6725eb904123aefaebf63cfd`).

**SO-1b's MESH arm runs the same `checkMesh` on the same tutorial, so this is a CERTAIN
refusal, not a possible one.** Unit **U30** executes the frozen predicate on those real
bytes and it returns `['Floating point exception']` — the defect, run rather than described.
SO-1a already paid: five clean arms and 9.416 core-min of intact physics returned
`NOT A RESULT`.

**THE REPAIR IS ADOPTED, NOT REINVENTED**, from `curriculum_SO1aR/so1ar_grade.py`
(`REAL_BANNER_LINE` at :285, the reasoning at :192-231, `fatal_token_sites` at :498). Its
four load-bearing properties are preserved and each is driven:

| property | why it matters | unit |
|---|---|---|
| **The token stays.** What is removed is the whole-file substring scan | deleting the token is the blinding this repair must not do | U34 |
| **Line by line, with one narrow benign exclusion** (`^\s*trapFpe:\s`) | a banner on line 18 can never suppress a crash on line 400 | U31, U35 |
| **`^` anchoring is NOT the fix and is deliberately not adopted** | OpenMPI's real crash line `mpirun noticed that process rank 2 exited on signal 8 (Floating point exception).` is **not line-initial**; `^Floating point exception` would **miss** it. An over-narrow exclusion costs a false refusal; an over-narrow positive anchor costs a **missed crash** | U32 |
| **`Foam::sigFpe::sigHandler` added as an EXTRA positive token** | strengthens detection; a crash whose shell line never reaches the log is still caught by its stack trace | U33 |

**Honest labelling:** the OpenMPI line and the `sigFpe` stack line used in U32/U33 are
**realistic PLANTED lines, not captured ones**, and are labelled so in the source. The
`trapFpe` banner in U29–U31 and U35 **is real, read from the preserved run root**, and is
cross-checked against SO-1aR's byte-identical frozen fixture on a second channel (U28).

## 7. HOW IT RE-GRADES — IT RE-IMPLEMENTS NO GATE

`so1br_grade.py` imports SO-1b's **own frozen comparator**, proves the file on disk is
byte-identical to the committed blob **by md5 and by git blob sha**, **rebinds exactly ONE
name**, and runs the **frozen `grade()`**. Every band, threshold, composition rule, planted
control and refusal clause that decides a verdict is **literally the frozen code, unedited
on disk**.

| frozen comparator | md5 | HEAD blob | names rebound |
|---|---|---|---|
| `curriculum_SO1b/so1b_grade.py` | `88157ca3c04798750e97b87ca3d02a15` | `f7ba5f7b5d405f8d4d6dbc82bb538397ac8dff09` | **`fatal_tokens_in`** (1) |

* **The rebind is audited, not asserted.** Every callable in the imported module is
  fingerprinted before and after; the set whose identity moved must be **exactly**
  `("fatal_tokens_in",)` or the run refuses (**U39**), and an unregistered rebind is driven
  failing (**U40**).
* **The frozen `FATAL_TOKENS` tuple is NOT rebound.** The repaired closure reads the frozen
  tuple from the module and adds the extra positive token locally, so the frozen constant
  table is provably untouched.
* **25 gate-deciding constants are read before and after and must not move** — the bands,
  the plateau tolerance, `MIN_GRADED`, `TB_MAX_PASSING`, the component and step sets, the
  caps, the ceiling, the digests, the `.so` md5s, the cpuset, the prediction table and the
  frozen unit count (**U42**: 25 checked, 0 moved).
* **Refusals raise through the frozen module's own `refuse()`**, so a refusal from the
  repaired path is shaped exactly like the refusal that instrument would itself have raised
  (**U41**: the raised type is `so1b_grade.Refusal`).
* The repaired closure keeps the frozen return type, so the frozen `g_completion`'s C5
  clause — its condition, its message and its verdict — still decides.

## 8. BIRTH REQUIREMENT — BOTH DIRECTIONS, REAL PATH, AND THE MUST-FLAG DIRECTION IS THE POINT

A repaired precondition's entire risk is that it **launders a genuine absence into a
proceed**, so the must-flag direction is the point. Every plant travels the **real** pinned
artefact bytes, the **real** adopted reader and the **real** frozen grader. **Mutations are
written to scratch copies; the preserved root is never written**, and its md5s are read from
the disk before and after (a run root is not in git, so a git-based check is blind to it).

| direction | plant | required | unit |
|---|---|---|---|
| MUST-NOT-flag | none — the real pinned artefact | `PROCEED`, both channels agree, both gradients PASS | U03–U05 |
| **MUST-FLAG** | the registered input **ABSENT** | REFUSE `registered_input_absent` | U06 |
| **MUST-FLAG** | the registered input's **md5 MOVED** by one byte | REFUSE `registered_input_md5_moved` | U07 |
| **MUST-FLAG** | `gates.G5_PATCHED` **ABSENT** — the exact shape that closed SO-1b | REFUSE `no_gates.G5_PATCHED` | U08 |
| **MUST-FLAG** | `rows.PATCHED` **ABSENT** | REFUSE — never silently proceed, never fall back to the other channel | U09 |
| **MUST-FLAG** | the two channels made to **disagree** | REFUSE `channel_disagreement` | U10 |
| **MUST-FLAG**, wrong-but-present | `G5_CD.verdict = "GATE FAIL"`, well-formed | decision `REFUSE` — **a frozen clause fires, not a parse error** | U11 |
| **MUST-FLAG**, wrong-but-present | `G5c_CL.verdict = "GATE FAIL"`, well-formed | decision `REFUSE` — the **constraint** gradient is graded as an equal | U12 |
| **MUST-FLAG** | the input made unparseable | REFUSE `registered_input_unreadable` — an unreadable dependency is not a licence to proceed | U13 |
| **MUST-FLAG** | `rows.SHIPPED` **STRIPPED** | REFUSE `shipped_row_status_absent` | U20 |
| **MUST-FLAG** | `gates.G5_SHIPPED` **STRIPPED** | REFUSE `gates.G5_SHIPPED_absent` | U21 |
| **MUST-FLAG** | `rows.SHIPPED` **laundered to `PASS`** | REFUSE `shipped_row_status_not_the_registered_word` | U22 |
| **MUST-FLAG** | a verdict emitted with **no provenance block** | REFUSE `verdict_without_upstream_provenance` | U23 |
| **MUST-FLAG** | `GATE FAIL` deleted from `verdict_line` — the unquoted-heredoc shape | REFUSE `provenance_token_lost_from_verdict_line` | U24 |
| **MUST-FLAG** | `verdict_line` bytes altered while the token survives | REFUSE `verdict_line_bytes_differ_from_the_intended_bytes` | U25 |
| MUST-NOT-flag | a well-formed emit | passes, verdict unchanged | U26 |
| **MUST-FLAG** | a verdict word outside the fixed vocabulary | REFUSE | U27 |
| **MUST-FLAG** | an **unregistered** name rebound in the frozen module | REFUSE `REBIND_AUDIT` | U40 |

**Frozen unit count `EXPECTED_UNITS = 47`, written into `so1br_grade.py` BEFORE its first
execution.** The selftest must pass under `python3` **and** `python3 -O`, with
`__pycache__` **cleared first** and `sys.dont_write_bytecode = True` set **above any
import** in both files — a stale `.pyc` inverts mutation tests and `PYTHONDONTWRITEBYTECODE`
does not cure it. **Zero `assert` statements** in either file, counted by `ast` and driven
(U44, U45), so `-O` cannot strip a check. Evidence: `so1br_selftest_evidence.txt`,
**47/47 under both interpreters, zero stray bytecode**.

## 9. INSTRUMENT TABLE — EXISTENCE ASSERTED BEFORE ANY MD5

Every file this item's comparator and driver entry point **execute, import, read or scan**.
**Existence is asserted first**: on 2026-08-30 a sibling item's section-7 table passed
8-of-8 md5 agreement while the script implementing its aggregate gate **had never existed
in any commit**, and a launched run had to be stopped over it.

| role | path | EXISTS | md5 | bytes |
|---|---|---|---|---|
| EXECUTED / IMPORTED | `cases/dafoam/ladder-a/A1/curriculum_SO1bR/so1br_grade.py` | **yes** | `9736ca91c9c111877f86dc048b38e929` | 37704 |
| EXECUTED / IMPORTED | `cases/dafoam/ladder-a/A1/curriculum_SO1bR/so1br_precondition.py` | **yes** | `447eaada4a896fc5f8b0f4ced4cb2af8` | 22928 |
| IMPORTED AT RUNTIME (frozen predecessor) | `cases/dafoam/ladder-a/A1/curriculum_SO1b/so1b_grade.py` | **yes** | `88157ca3c04798750e97b87ca3d02a15` | 98745 |
| READ AS DATA (the registered input) | `/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/SO1aR_grade_20260828T171830Z.json` | **yes** | `194c0440b8e36e8044795449c7df7edb` | 49743 |
| READ AS DATA (real C5 bytes) | `/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/MESH/checkMesh.log` | **yes** | `22aa9cfa6725eb904123aefaebf63cfd` | 3568 |
| READ AS DATA (second channel on the same bytes) | `cases/dafoam/ladder-a/A1/curriculum_SO1aR/so1ar_fixture_REAL_SO1a_MESH_checkMesh.log` | **yes** | `22aa9cfa6725eb904123aefaebf63cfd` | 3568 |
| SCANNED (U46, forward-AD) | `cases/dafoam/ladder-a/A1/curriculum_SO1b/so1b_of.py` | **yes** | `0f14244bee5fafc698e80060782a7606` | 30885 |
| SCANNED (U46, forward-AD) | `cases/dafoam/ladder-a/A1/curriculum_SO1b/so1b_runScript.py` | **yes** | `0557da51f6f179f6de865144343c499f` | 9657 |
| SCANNED (U46, forward-AD) | `cases/dafoam/ladder-a/A1/curriculum_SO1b/so1b_run_arm.sh` | **yes** | `e8b48ee0940a08e5170490da679a6b0c` | 32826 |
| SCANNED (U46, forward-AD) | `cases/dafoam/ladder-a/A1/curriculum_SO1b/so1b_chain_driver.sh` | **yes** | `0d1180dea70d82794856598a644f8fe9` | 18537 |

**FILES A STAGE-2 RUN WOULD NEED, EXISTENCE CHECKED FIRST — AND THEY DO NOT EXIST:**

| path | EXISTS |
|---|---|
| `cases/dafoam/ladder-a/A1/curriculum_SO1bR/so1br_chain_driver.sh` | **NO** |
| `cases/dafoam/ladder-a/A1/curriculum_SO1bR/so1br_run_arm.sh` | **NO** |

**No md5 is registered for a file that does not exist.** See §12.

The grading path is fixed at this commit; before any recorded execution each instrument is
hashed against the committed blob and the run refuses on a mismatch.

## 10. WHAT SO-1bR MAY NOT CONCLUDE

* **Nothing about the physics, the mesh, the solver or an optimum.** No solver ran. Stage 1
  grades a **precondition and its provenance**, and nothing else.
* **No new gate, threshold, band, cap or label.** All are SO-1b's own frozen values, checked
  unmoved across the rebind.
* **Nothing about SO-1a's verdict.** SO-1a's item verdict remains `GATE FAIL` and is not
  re-opened, re-graded or softened here. It is **carried**, which is the opposite.
* **Nothing about `shape[6]` at the optimum.** §3 registers a prediction; it does not
  measure one.
* **`G6` stays `NOT MEASURED`** and is never composed. AV2RG's `BLOCKED` forward-AD reading
  is a fact about a channel this item does not use.
* **A `REFUSE` that stays `REFUSE` is a result and is reported as one.**

**Honest disclosure** (as at `curriculum_D18R_P7/PREREGISTRATION.md` §4 and
`curriculum_AVWC/PREREGISTRATION.md` §8): the instruments were exercised during development,
so this is **not an outcome-blind freeze and does not claim to be**. What the freeze buys is
the registered input and its md5 pin, the precondition semantics, the G-PROV enforcement
clauses, the rebind set, the refusal set, the unit count and the both-directions controls —
all fixed and committed before the recorded execution.

## 11. COST (rule 12; `COMPUTE_BUDGET_CHARTER.md` §5)

**Solver compute: ZERO core-minutes.** No mesh, no solve, no container, no GPU. W3 is live
(driver pid 1280304, cpuset 1) and is not disturbed; `verification/queue/` is not touched.

**Stage 1 is instrument-only, so the estimate carries a CACHE-STATE TERM** — this family
measured a 20.1× cold/warm page-cache spread (C-212) and then missed again by 0.213× (C-214)
for want of one.

| | |
|---|---|
| Sizing basis — **FILE COUNT** | **11 named files** read, imported or scanned (§9). No directory walk runs at Stage 1: `manifest()` is Stage-2 machinery and `grade_root()` refuses with no root |
| Sizing basis — **COPY COUNT** | **13 scratch copies** written (12 mutated JSONs at ≈ 50 KB, 1 md5-moved copy) |
| Cache-state term, cold | 11 files at ≈ 1.0 s / 1,000 files ≈ **0.011 s** |
| Cache-state term, warm | 11 files at ≈ 0.15 s / 1,000 files ≈ **0.002 s** |
| **MEASURED cold/warm spread on this item** | **2.0×** — 0.22 s cold (first pass after `__pycache__` clear) against 0.11 s warm, three warm repeats all 0.11 s |
| Attribution of that spread | **NOT page cache.** The file-count term is ≈ 5 % of the cold pass; the dominant term is interpreter start plus `exec_module` of a 98,745-byte frozen comparator. **This item's spread is 2.0× and not C-212's 20.1× because C-212 manifested ≈ 750-file roots — two orders more files.** Stated so the next estimator sizes on file count and does not copy 2.0× forward |
| Registered estimate | **0.60 core-min**, ranks = 1 (two graded passes plus the supervisor's own freeze-verification re-runs, at cold cache) |
| Cap | **3.00 core-min.** An overrun **stops the item**; it does not get a new budget |
| Spent at this freeze (measured, from the recorded battery) | **≈ 0.03 core-min** — 2 graded passes at 0.22 s and 0.11 s, 3 warm repeats at 0.11 s, 2 driver-entry runs, ranks = 1 |
| Rate | **$0.0513 / core-h**, c7a.4xlarge, owner-stated 2026-08-21/22 |
| Dollars, estimate | **$0.000513 — DERIVED, NOT MEASURED** |
| `cost_basis` | **REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5) |
| Disk | ≈ 700 KB transient in the session scratchpad, deleted by the selftest. **No record here cites a scratch path** (L-186) |

**STAGE 2 IS NOT COSTED BY THIS DOCUMENT.** For shape only, SO-1b's **own** registration
(freeze commit `ea9ef8b6`) carried **20.2 core-min point / 115.0 core-min ceiling / band
[11.0, 58.0] / $0.016758 point, derived**. Those figures are **INHERITED AND NOT RE-DERIVED
BY THIS LANE**, and a Stage-2 registration owes its own costing against its own instruments.

A calibration row is owed in `docs/COST_CALIBRATION.md` at completion, with its id
**re-derived from the tail as the maximum existing number in the committing shell
invocation** (rule 11).

## 12. STAGE 2 IS NOT FROZEN HERE — WHAT IS OWED, AND WHAT IS NOT CLAIMED DONE

**This is the section to read before believing SO-1bR is ready to run.**

SO-1b never created a run root: its chain aborted at rc = 7 **before** staging. So SO-1bR is
not a re-grade of a preserved root — a chain must actually execute for there to be anything
to grade. That chain needs two files **which do not exist** (§9):

* `so1br_chain_driver.sh`, derived from `so1b_chain_driver.sh` (267 lines) with the
  registered deltas: `G-SO1A` replaced by an invocation of the **md5-pinned file**
  `so1br_precondition.py`; `BASE` → `CURRICULUM-SO1bR-…`; `GRADER` → `so1br_grade.py` and
  its md5; the grade output name.
* `so1br_run_arm.sh`, derived from `so1b_run_arm.sh` (577 lines): `ITEM=SO1bR`,
  `REGISTERED_BASE`, the `PREREG` path and its manifest-tag check, and the container name
  prefix. `so1b_run_arm.sh` **cannot be adopted byte-identically** — it would write
  `ITEM=SO1b` into SO-1bR's ledger (a provenance lie) and would assert **SO-1b's**
  pre-registration manifest rather than this one. The grader-side names
  (`.so1b_age_datum`, `so1b_O.json`, `so1b_E.json`) **must be kept**, because they are
  frozen constants of `so1b_grade.py`.

**WHY THEY ARE NOT IN THIS FREEZE.** ≈ 844 lines of derived shell that **cannot be executed
here** (zero solver compute, and the chain needs containers) would be exactly the unverified
surface §9's warning is about: a section-7 table full of md5s for code no one has run. The
honest object is a Stage-2 registration whose instruments can be driven before they are
frozen.

**WHAT STAGE 1 BUYS FOR STAGE 2, AND IT IS NOT NOTHING.** The single new decision in the
whole chain — the precondition — is **one file, md5-pinned, driven end to end on the real
artefact through 27 units**, and the driver invokes it as that file rather than as an inline
heredoc. The heredoc form is what SO-1b used and it is untestable by construction.

**REGISTERED STAGE-1 OUTCOME**, before the supervisor's clearance and before any Stage-2
work: `G-SO1AR` on the pinned input reads **`PROCEED`** — `G5_CD = PASS`, `G5c_CL = PASS`,
`rows.PATCHED = PASS` on both channels, upstream item verdict `GATE FAIL`, upstream
`rows.SHIPPED = GATE FAIL`. Recorded in `so1br_selftest_evidence.txt`.

## 13. RULE-2 CONDITION — the run directory that does not exist, and how it was checked

Checked at this freeze, 2026-08-30, **by running the commands, not by recalling them**:

* `ls -d /home/ubuntu/certonomous-runs/CURRICULUM-SO1b*` → **`No such file or directory`,
  rc = 2, ZERO entries.** This covers both `CURRICULUM-SO1b-a1-naca0012-dragmin-opt` (the
  root SO-1b would have created) and any `CURRICULUM-SO1bR-*`.
* **The check is proved able to see a non-empty answer** — a zero from a reader not shown
  able to see a non-zero is not evidence (rule 3). The same command with the same shape,
  `ls -d /home/ubuntu/certonomous-runs/*SO1*`, returns **one** entry:
  `CURRICULUM-SO1a-a1-naca0012-dragmin-gradient`. The glob works; the SO-1b roots are absent.
* `cases/dafoam/ladder-a/A1/curriculum_SO1bR/` contained **nothing** before this lane, and
  now contains only `so1br_precondition.py`, `so1br_grade.py`,
  `so1br_selftest_evidence.txt` and this document. **No `SO1bR_grade_*.json` and no
  `RESULTS.md` exists.**
* **The instrument register itself is the proof for Stage 2:** the two files a Stage-2 run
  would need do not exist (§9), so no Stage-2 compute can have occurred.

**Amendments before first compute are legal and must state the condition and how it was
checked** — this section is that statement.

## 14. WHAT LANDS, AND WHAT DOES NOT

**Lands from this lane:** `so1br_precondition.py`, `so1br_grade.py`,
`so1br_selftest_evidence.txt` and this document, in
`cases/dafoam/ladder-a/A1/curriculum_SO1bR/`.

**Does not land from this lane:**

* **Nothing is enqueued, and NO QUEUE ENTRY IS DRAFTED — deliberately.**
  `verification/queue/dafoam/README.md` requires `launch_cmd` as an argv list and
  `prereg_commit` as a full 40-hex sha. **Stage 2 has no driver to name** (§9, §12), so any
  Stage-2 entry would point `launch_cmd` at a file that does not exist — precisely the
  defect that stopped a launched sibling run on 2026-08-30. **Stage 1 has already been
  executed**, so there is no pending Stage-1 launch either; its reproduction command is
  `python3 so1br_grade.py --selftest` from this directory, ranks = 1, and it is recorded
  here rather than filed as a proposal. **An entry is owed when, and only when, a Stage-2
  driver exists and can be driven.** The supervisor holds the pre-compute gate in any case:
  reading the comparator personally and confirming the freeze commit are their checks, not
  this lane's, and they are not delegable.
* **Nothing is executed.** No chain, no arm, no container.
* **No edit to any frozen file** — `so1b_grade.py`, `so1b_chain_driver.sh`,
  `so1b_run_arm.sh`, `so1a_grade.py`, `so1ar_grade.py` and every SO-1b/SO-1a/SO-1aR record
  are untouched, and the two preserved artefacts read are proved unmoved by md5 (rule 6).
* **`curriculum_SO1a/` was not touched** — another lane is writing its `RESULTS.md`.
  **W3's files and run root were not touched** — W3 is live.
* **No SO-1aR grade JSON was copied, renamed, edited or moved** (§1a).
* **Nothing is sent, filed, uploaded, registered, posted or commented outside this box**
  (rule 7). **SUBMISSIONS ARE PARKED.**
