# R4b-Ib — THE SUCCESSOR INSTRUMENT BUILD, REGISTERED AS A CAPPED WORK ITEM

**Status: DRAFT. NOT FROZEN, NOT COMMITTED, NO COMPUTE RUN.**
This document and `grade_r4b_ib.py` must land in **ONE commit**, because standing
rule 2 fixes the grading path at the pre-registration commit. **That commit is the
closure supervisor's**, not this lane's.

| | |
|---|---|
| item | **R4b-Ib** |
| supersedes | **R4b-I** — gates CLOSED by first compute; `grade_r4b.py` frozen and unedited |
| instrument | `cases/RANS_LES_closure_models/R4b_pair_control/R4b_Ib/grade_r4b_ib.py` |
| criteria source | `cases/RANS_LES_closure_models/R4b_pair_control/INSTRUMENT_BUILD_PREREGISTRATION.md` §5, sha256 `7a80553cc36a7462baf35c770a10807e0c3ca7c51ddc038dc6b9c23201c289f9` |
| run root | `/home/ubuntu/closure-data/r4b_ib_birth/` |
| estimate | **12.0 core-minutes** |
| hard cap | **40.0 core-minutes** |

---

## 1. WHY THIS ITEM EXISTS, AND WHAT IT IS NOT

### 1.1 The ruling this item implements

The closure supervisor ruled that the `_dev/` compute under
`/home/ubuntu/closure-data/r4b_instruments/` — written 2026-08-28T17:39:12Z to
17:43:16Z, ~11.2 MB, **including a GRADED B3 birth record reading `PASS`** — **IS
FIRST COMPUTE for R4b-I**. R4b-I's gates are therefore CLOSED under standing rule 2
and `grade_r4b.py` **may not be edited**.

The reason is on the drafters' own terms, not on judgment:
`QUEUE_ENTRY_DRAFT.json:19` names the instrument root's **non-existence** as its own
pre-compute condition (`test -e` returned rc=1 at 2026-08-28T17:20:38Z), and that
condition is now **false on disk**. A registration that names its own pre-compute
test is bound when that test fails. The counter-argument that a `_dev/` prefix and
a self-applied label (`NOT A REGISTERED ARTEFACT`) exempt the compute was declined:
**a label an author applies to their own artefact cannot decide whether a rule binds
them**, or any freeze becomes evadable by naming.

**The route is therefore a SUCCESSOR INSTRUMENT, exactly as G1 → G1b.** Not a §2d.1
repair exception, not an amendment to `grade_r4b.py`.

### 1.2 What this item is NOT

1. **It is not a re-opening of the ruling.** R4b-I's verdict history stands as it is.
2. **It does not move any band, threshold, cap, label or gate criterion.** Every one
   is taken **verbatim** from R4b-I's frozen §5, cited by section below. Where this
   lane found itself with discretion over a criterion, it stopped and reported
   rather than choosing — no criterion in this document was authored here.
3. **It does not touch R4b-I's frozen files.** `grade_r4b.py`, `run_r4b.sh`,
   `select_control.py`, `build_r4b_cases.py` and R4b-I's registration are re-used
   **by import and by path, unmodified and hash-pinned**. Re-hashed
   2026-08-31T15:07:28Z: all five unchanged.
4. **It does not touch R4b-I's instrument root.** `/home/ubuntu/closure-data/r4b_instruments/`
   holds the evidence the ruling rests on. `guard_ib_root()` refuses any write there
   (`R4b-I-ROOT-GUARD`).
5. **It does not move R4b's solve arm.** That arm stays **`BLOCKED`** on Sanaa's
   direction on the increment. `/home/ubuntu/closure-data/r4b/` must remain absent
   and this item re-asserts that, verbatim from `grade_r4b.py:694-698`.
6. **It authorises no submission.** Standing rule 7: submissions are PARKED.

---

## 2. THE PRE-COMPUTE CONDITION, AND HOW IT WAS CHECKED

Standing rule 2 requires the condition to be **stated and checked**, naming the run
directory that does not exist. R4b-I's own registration is the reason that clause is
written this way, and this item does not repeat its mistake.

| condition | measured |
|---|---|
| `/home/ubuntu/closure-data/r4b_ib_birth/` — R4b-Ib's run root — **does not exist** | `test -e` returned **rc=1** at **2026-08-31T15:07:28Z** [MEASURED] |
| `/home/ubuntu/closure-data/r4b/` — R4b's SOLVE root — **does not exist** | `test -e` returned **rc=1** at **2026-08-31T15:07:28Z** [MEASURED] |
| `/home/ubuntu/closure-data/r4b_instruments/` — R4b-I's root — **unchanged since R4b-I's `_dev` compute** | `find -newermt 2026-08-28T18:00:00` returned **no rows**; `du -sh` = **19M** at 2026-08-31T15:07:28Z [MEASURED] |

**No compute for this item has been run.** The only execution to date is
`grade_r4b_ib.py --selftest`, which grades **no gate**, writes **no birth record**,
reads **no producer artefact**, and wrote nothing outside a session scratch
directory. It is authoring verification, not a gate reading. Its numbers appear in
§9 labelled as such.

**Registered, so it cannot be argued after the fact:** the moment
`/home/ubuntu/closure-data/r4b_ib_birth/` exists, this item's gates are CLOSED, by
exactly the reasoning that closed R4b-I's. Amendments are legal only while that
`test -e` returns rc=1.

---

## 3. THE FOUR REPAIRS, AND NOTHING ELSE

All four move in the **strictly stricter** direction; that is what makes them
legitimate in a successor rather than a rewrite. Line numbers in `grade_r4b.py` were
re-verified against the frozen file at sha256 `0e2554ae…` on 2026-08-31 [MEASURED].

### D1 — an absent `MODEL.json` is a traceback, not a refusal

`grade_r4b.py:478` reads `m = json.load(open(model_json))` with **no exists-check and
no `require()`**. With an absent `MODEL.json` it raises `FileNotFoundError` → uncaught
traceback → **exit 1**: not a refusal, not a verdict in the vocabulary. It sits
**after** `os.makedirs` at `:477`, so it leaves a **partial write** and **no birth
record** (`write_birth_record` is at `:1037`, downstream).

**Repair:** `require_readable_file()` / `require_readable_json()` — named refusals,
**exit 2**, run **before the first consumer** and therefore before `:477`'s
`makedirs`. Absent, empty, non-file and unparseable-JSON are four separate refusals.

**Disclosed honestly:** `:478` itself is inside the frozen file and stays unguarded.
The repair is a **precondition at the call site**, which is the only form available
to a successor forbidden to edit its parent. A path that vanished between the
precondition and `:478` would still traceback; that window is microseconds and no
process of this lab writes into it, but it is a real residual and is named here
rather than discovered later.

### D2 — the registered headline is not computable

`:734` declares `gate_set=["B1","B2","B3","B4","B5"]`. `:750` builds the record with
`B1=b1, B2=b2, B5=b5` **only**. **There is no `b3` or `b4` variable in the file**
(re-verified: a name search for `b3`/`b4` returns no rows). `gate_set` is inert
metadata consumed nowhere. `:1038` decides the verdict on **three** gates and `:1047`
returns `0 if all(x=="PASS" for x in v)`.

**Consequence, and it is the serious one:** R4b-I's registered headline — §5.6's
"B1–B5 all PASS → `GATE REACHED`" — **is not computable**, and a run returns **rc=0
looking like the registered result**.

**Repair:** `b3_selector()` and `b4_builder()` actually grade B3 and B4 against §5's
frozen criteria and enter them in the record; `headline()` computes §5.6's mapping
table, every row.

### D3 — B5 certifies a runner it never ran

`:663` `if case_dir and os.path.isdir(case_dir):` **silently skips** B5's drive
demonstration when no `--built-case` is passed, and B5 **still aggregates to PASS**.
That is a §2j birth-requirement violation: a control with **no limb at all**.

**Repair:** `B5-DRIVE-ABSENT`, a refusal (exit 2). Structurally, B5 is additionally
handed **B4's own freshly built case tree**, so the limb cannot go missing by
omission.

### D4 — aggregation over whatever happens to be there

`:681` `sub = [v["verdict"] for v in rep.values() if isinstance(v, dict)]` aggregates
over **whatever dicts happen to be in `rep`**, not over a registered list, and
`all()` over a short or empty set returns **True**. This is D2's defect at a smaller
scale, and it is the structural one.

**Repair, written ONCE and used three times:** `aggregate_required(mapping, required,
code, what)` aggregates over an **explicit registered list of required names** and
**REFUSES (exit 2) if any required name is MISSING**. **A missing gate is a refusal,
never a silent omission.** Every value must also be in the fixed vocabulary. Used
for:

| use | registered required list |
|---|---|
| the B-gate set | `B1 B2 B3 B4 B5` |
| B5's sub-report | `capacity non_pgrep_path skip_if_complete never_kills drive_with_noop_solver` |
| B3's parts | `G0a G0e grid` |
| B4's parts | four refusals + `term_order_n4` + `set_libs_both_shapes` + `positive_build` |

For B5 the clause set is additionally proven **equal** to the registered list before
aggregating, so the recomputation is identical to `:682`'s on every reachable input
**plus a refusal path** — it can refuse or agree, never invent a `PASS`.

---

## 4. WHAT IS PRESERVED, UNCHANGED, BY IMPORT

`grade_r4b_ib.py` **imports the frozen `grade_r4b.py`** and re-uses it. B1's and B2's
criteria are therefore not "copied" — they are the **same code object** and cannot
have drifted. The parent and its three siblings are **pinned by sha256** and the
successor refuses (`PINNED-INSTRUMENT`) if any has moved.

| pinned file | sha256 |
|---|---|
| `grade_r4b.py` | `0e2554ae00e486c75a8529f07e77a974c388913d96d1839d0bc8d601cd34ca96` |
| `select_control.py` | `50d9622d95a26bc02b72c8af19f025934e1313570433ac95107387594f7f290f` |
| `build_r4b_cases.py` | `b45ddd8e7f2a02fef286623f396f41f82223563262580fa18e84cf37c11e82d7` |
| `INSTRUMENT_BUILD_PREREGISTRATION.md` | `7a80553cc36a7462baf35c770a10807e0c3ca7c51ddc038dc6b9c23201c289f9` |

`run_r4b.sh` (`f915bfed…`) is driven as a subprocess by the imported `b5_runner` at
its frozen path.

Preserved and verified:

* **The fatal channel keeps the NARROW `Foam::sigFpe::sigHandler` form**
  (`grade_r4b.py:840`), because `grade()` is imported unmodified. **Never the broad
  substring** — OpenFOAM writes `trapFpe: Floating point exception trapping enabled
  (FOAM_SIGFPE).` at **line 18 of every log**, so the broad form fired on **63 of 70**
  real logs, **57 with a clean `End` line**. It is a constant, not a detector (L-396,
  D548), and it cost G1 its entire **127.08 core-min** verdict. The successor's
  selftest proves the broad substring appears on **no executable line** of its own
  source — docstring lines excluded mechanically via AST, not by eye — and carries a
  **planted control** proving that sweep can see a planted executable use.
* **Verdict vocabulary FIXED**: `PASS` / `GATE REACHED` / `GATE FAIL` /
  `NOT A RESULT` / `BLOCKED` / `PENDING`. No synonyms. `aggregate_required` refuses a
  value outside it.
* **Aggregation is ONE-WAY**: a gate may only pull the item verdict **down**.
  `both_halves_guard()` can turn a `PASS` into `GATE FAIL` and never the reverse, and
  never lifts a `PENDING`.
* **ZERO `ast.Assert` nodes** (L-332: `python -O` erases `assert`, so a refusal
  written as one silently vanishes). Verified by parsing the AST, both inside the
  selftest and independently: **0** [MEASURED].
* **The `-O` selftest pair** (`grade_r4b.py:471-472`) is inside the imported
  `b1_existence_and_refusals`, unchanged; and `grade_r4b_ib.py --selftest` itself is
  required to pass under **both** `python3` and `python3 -O`.
* **No process-termination verb.** Proven mechanically over the successor's own
  bytes, with a planted positive control, tolerating exactly one token — the frozen
  B5 clause **name** `never_kills`, which the required-list must be able to name.

---

## 5. THE GATES — copied VERBATIM from R4b-I §5

**No criterion below was authored by this item.** Each is R4b-I's frozen text; the
citation is the authority and this document is a transcription. Where a criterion
was ambiguous the lane stopped and reported rather than resolving it.

### 5.0 The birth requirement (R4b-I §5.0)

Sanaa's rule, canonised 2026-08-28, verbatim:

> *"rule 3's question — 'was this reader ever shown able to see a non-zero through the
> real code path?' — is now the birth requirement for every reader/comparator: no
> instrument grades anything until that answer is yes, demonstrated."*

**Every birth demonstration is TWO-SIDED**: the **positive** half — the instrument
must **SEE** the plant, through the real reader, from a real file on disk; and the
**negative** half — the instrument must **NOT flag** an unperturbed copy of the same
real file through the same path. A demonstration carrying only the positive half
certifies nothing about false positives. **Both halves are graded.**

### B1 — EXISTENCE AND REFUSAL (R4b-I §5, B1)

> All **four** instruments exist at their registered paths, are importable /
> executable, and **every registered refusal in §2.2 fires**, each exercised by a
> planted condition on a real artefact, each returning **exit 2** and **not** an
> `AssertionError`. Each refusal is additionally re-run under `python3 -O` and must
> still fire.
>
> **`PASS` requires 4 of 4 instruments present and 100 % of registered refusals
> firing under both `python3` and `python3 -O`. Anything less is `GATE FAIL`.**

*Graded by the imported `b1_existence_and_refusals`, unmodified. The instrument count
stays **four**: `grade_r4b_ib.py` is not added to that set, because changing "4 of 4"
would be moving a criterion.*

### B2 — THE BIRTH OF THE COMPARATOR (R4b-I §5, B2)

> All **six** of R4b §5's G0 controls — G0a, G0b, G0c, G0d, G0e, G0f — demonstrated
> **two-sided** through the comparator's own real code path, on real producer
> artefacts named in §3.2.
>
> * G0a–G0d: `PLANT = 1.234e-03` planted into a **scratch copy of a real OpenFOAM
>   field**, recovered through the real reader. The bar is
>   `r4_lib.planted_zero_reader_check`'s, re-used unmodified:
>   `max(1e-12, 8·eps·max|field|)`, **and** the median recovery matching the plant to
>   `1e-9` relative.
> * G0e: a cell forced to a known non-realisable anisotropy (a barycentric coordinate
>   driven to `-1e-3`). **The violating count must rise by EXACTLY one** — not "by at
>   least one", which a routine that flags everything also satisfies — and must **not**
>   rise on the unperturbed copy.
> * G0f: `NASA_2DWMH` placed inside a list handed to `assert_no_test_case`, which must
>   raise; and a list without it, on which it must **not** raise.
>
> **`PASS` requires 6 of 6 controls demonstrated, both halves each. Anything less is
> `GATE FAIL`**, except where §3.2's registered carve-out applies, in which case that
> control is `PENDING: <path>` and the comparator is recorded NOT BORN **for the
> specific gate that control serves** and must refuse to grade it.

*Graded by the imported `field_control`, `realisability_control` and
`zero_shot_control`, unmodified. All four real producer artefacts were confirmed
present on 2026-08-31 [MEASURED], so the carve-out is not expected to fire — but it
is registered and `headline()` implements its row.*

### B3 — THE BIRTH OF `select_control.py` (R4b-I §5, B3) — **NEWLY GRADED (D2)**

> G0a and G0e demonstrated two-sided through **`select_control.py`'s own** reader, not
> through the comparator's; plus the selector run over the full frozen 12-value grid,
> producing a feasibility result at **every** grid value — the registration requires
> all twelve reported, so a selector that silently short-circuits is visible.
>
> **`PASS` requires both controls two-sided AND 12 of 12 grid values evaluated and
> reported. Anything less is `GATE FAIL`.**
>
> **Registered and NOT graded here:** the *value* of `xi*`. R4b's prediction P1
> (`xi* ∈ [0.02, 0.20]`, point `0.10`) belongs to R4b's registration and is graded
> there. This item reports the demonstration value beside the gate, labelled
> `reported, not graded`, and **no verdict of this item turns on it.**

### B4 — THE BIRTH OF `build_r4b_cases.py` (R4b-I §5, B4) — **NEWLY GRADED (D2)**

> **Negative half:** all four registered refusals fire — no `MODEL.json`; a
> `MODEL.json` whose hash differs from the committed blob; a missing `COVERAGE.md`; an
> existing case tree. Each exit 2, each under `-O` too.
>
> **Positive half, and it must be REAL:** with all four preconditions met, the builder
> builds **one real case tree** by calling `build_aposteriori.build()` unmodified, into
> this item's run root. Verified on that tree:
> * the `n in (1,2,3)` assert is present **at the new call site** and fires when handed
>   `n = 4` (standing rule 14 — a lesson is not applied until **every** call site
>   asserts it);
> * `set_libs` is verified on **both** real shapes, because a bare `str.replace` is a
>   silent no-op on one of them and the run then returns the **baseline** field, which
>   looks like a physical answer: **(i)** a hill case, which carries **no `libs` line
>   at all**, and **(ii)** a duct case, which carries one naming a library that does
>   not exist on this machine. After `set_libs`, the library name must be **present**
>   in both, asserted by `set_libs` itself.
>
> **`PASS` requires 4 of 4 refusals AND the positive build with both `set_libs` shapes
> and the `n` assert verified. Anything less is `GATE FAIL`.**

### B5 — THE BIRTH OF `run_r4b.sh` (R4b-I §5, B5)

> * **Pre-launch capacity check, two-sided:** it must **see** a real busy box (a
>   planted, real background process it is required to count) and must **not** refuse
>   on a quiet box. **It must not rely on `pgrep` alone** — fleet agents are invisible
>   to it (L-41) — so the check reads run-directory mtimes and the docket as well, and
>   the demonstration confirms the non-`pgrep` path fires by itself.
> * **Skip-if-complete, two-sided:** it must **skip** a real complete case
>   (`/home/ubuntu/closure-data/r4/aposteriori/PHLL10595/ceiling/`) and must **not**
>   skip a real incomplete one.
> * **It must never kill a running solver**, verified by inspection of the diff, not by
>   running a kill.
>
> **`PASS` requires all three, both halves each. Anything less is `GATE FAIL`.**

> **REGISTERED LIMITATION, carried forward unchanged.** B5 exercises `run_r4b.sh` with
> its solver invocation replaced by a registered no-op. **No `simpleFoam` is launched
> by this item.** Therefore **B5 does NOT establish that `run_r4b.sh` can drive
> `simpleFoam`**, and this item may not be read as having established it.

### 5.6 Verdict mapping and the item's headline (R4b-I §5.6, verbatim)

| condition | verdict |
|---|---|
| B1–B5 all `PASS` | **`GATE REACHED`** — the four instruments exist, are frozen by sha, and every reader in them has been shown able to see a non-zero through the real production path. R4b's solve arm becomes **registrable**, and remains **`BLOCKED`** on Sanaa's direction. |
| any B-gate `GATE FAIL` | **`GATE FAIL`** — the instrument is repaired, the demonstration re-run, and the repair costed inside the same cap. **The cap does not move.** R4b stays `PENDING`. |
| a control's real artefact absent, per §3.2's carve-out | that control **`PENDING: <path>`**; the instrument **NOT BORN** for the gate it serves and refuses to grade it; the item's headline is `GATE FAIL` unless the carve-out is the only shortfall, in which case it is **`GATE REACHED (PARTIAL)`** with the not-born gate named. |
| the 40.0 core-min cap is reached | **`BLOCKED`** — the run stops and reports. An overrun stops the run; it does not get a new budget (standing rule 12). |
| not yet started | **`PENDING`** |

**No other word is used.** `GATE REACHED (PARTIAL)` is R4b-I's registered composite
headline label, reproduced verbatim from the table above; it is kept in the
`headline` channel and never enters the per-gate vocabulary channel, which stays the
fixed six. Every row is implemented in `headline()` and every row is exercised by the
selftest.

### 5.7 The registered falsifier (R4b-I §5.7, verbatim)

> **If any one of the four instruments cannot be given a two-sided birth demonstration
> on a real producer artefact, this item has found that R4b's instrument set is not
> buildable as specified**, and that is a finding about the specification, reported as
> such — not a reason to lower the bar.

---

## 6. THE NAMED LIMITATION THIS ITEM MUST DISCLOSE

**B3's and B4's outcomes have already been seen by this instrument's author.**

`/home/ubuntu/closure-data/r4b_instruments/_dev/birth_select_control.json` is a
complete B3 record reading `"verdict": "PASS"`, and `_dev/cases/build_manifest.json`
is B4-shaped. The successor is therefore being wired to two gates whose outcome its
author has observed. **Stating this is the point; hiding it would be the defect.**

This is admissible for exactly one reason, and only that reason: **B3's and B4's
criteria are frozen verbatim in R4b-I §5 and this item has ZERO discretion over
them.** They were transcribed in §5 above, not chosen. Nothing in the criteria was
tuned, relaxed or reordered after seeing `_dev`.

Registered controls on that exposure:

1. **No `_dev` verdict is copied.** `grade_r4b_ib.py` re-runs B3 and B4 **from
   scratch** into `/home/ubuntu/closure-data/r4b_ib_birth/` and reaches its own
   answer. It reads nothing from `_dev`.
2. **`_dev`'s `xi* = 0.05` is NOT A RESULT and is never quoted as one** — not in this
   document, not in the birth record, not in any report. The instrument's
   `xi_star_note` field says so in the record itself.
3. **R4b-I §4.3's conservative rule stands**: the demonstration `MODEL.json` may
   **not** be promoted to R4b's registered `MODEL.json`; R4b §14 commit 2 requires a
   fresh run. `select_control.py` is invoked with `--demonstration` so the output
   carries that provenance as its first key.
4. **The B3 self-report must agree** with the successor's own registered-list
   aggregation, or the run **refuses** (`B3-AGGREGATION-DISAGREES`). An instrument and
   its grader disagreeing about the instrument's own birth is a refusal, not a
   verdict.

---

## 7. §2j — THE SUCCESSOR'S OWN BIRTH REQUIREMENT

`grade_r4b_ib.py` is itself an instrument, so it needs its **own** birth
demonstration, **both limbs**, as an **artefact on disk** (§2j.3), written to
`/home/ubuntu/closure-data/r4b_ib_birth/`.

### 7.1 The D4 control, which is the whole point of the successor

`--d4-control` runs two limbs against a birth record:

* **negative limb** — a record with **one required gate removed** must **REFUSE**
  (exit 2). Run once **per required gate**, all five.
* **positive limb** — the **intact** record must **PROCEED** to a verdict.

A control carrying only the positive limb certifies nothing: a function that never
refuses passes it.

### 7.2 §2j.2 — who WROTE the bytes the control reads (L-402)

**This is the clause that has to be answered honestly, and the answer is split.**

| limb | producer of the bytes | status |
|---|---|---|
| the **structural** D4 control inside `--selftest` | **this instrument's own test harness** | **§2j.2 NOT MET.** Disclosed, not waived. |
| the **real-record** D4 control, `--d4-control` on the birth record written by `--birth-only` | **`grade_r4b_ib.py`'s own `--birth-only` run, over real producer artefacts** — a real `bijDelta`, a real `U`, a real `grad(U)`, the real `run_r4b.sh`, the real `select_control.py` | **§2j.2 MET** once run. |

**G2's selftest PASSED while its defect was live** because its synthetic log fixture
did not carry the `trapFpe:` banner that every real log carries — the synthetic
fixture was **cleaner than any log the solver has ever produced**. That is precisely
why the structural limb is **not** accepted as discharging §2j here.

**REGISTERED, and it is a gate, not an aspiration:** the real-record D4 control is the
**first post-freeze action** of this item, run immediately after `--birth-only`, and
its artefact is `/home/ubuntu/closure-data/r4b_ib_birth/d4_control.json`. **If it does
not `PASS`, R4b-Ib is `GATE FAIL`** regardless of what B1–B5 read, because the
instrument that graded them has not been born.

### 7.3 Per-fixture provenance, registered in advance

| fixture the demonstration reads | who WROTE the bytes |
|---|---|
| `/home/ubuntu/closure-data/r4/frozen/AR_10_Ret_180/1654/bijDelta` (G0a, G0b) | the frozen extraction, `kCorrectiveFrozenFoam` |
| `/home/ubuntu/closure-data/r4/aposteriori/PHLL10595/ceiling/3513/U` (G0c) | the propagation solver, `simpleFoam` / `kOmegaSSTCorrected` |
| `/home/ubuntu/closure-data/r5c/frozen/CBFS13700/354/grad(U)` (G0d) | `OpenFOAM postProcess -func 'grad(U)'` |
| `R4_sparta_build/COVERAGE.md`, 23,577 bytes, 2026-08-23, sha256 `e3417ea6…` (B4) | the frozen `make_coverage.py` chain (`f8c40810…`), the FS2/FS5 discharge — **not** `_dev`'s development fixture, which says of itself "NOT A REGISTERED ARTEFACT" |
| the real complete / incomplete cases `PHLL10595/ceiling` and `PHLL10595/discovered` (B5) | the real producer's own `rc`, `wall_seconds` and written time `3513` |
| the planted busy-box process (B5 capacity) | a real copy of `/bin/sleep`, really running, started and stopped by the demonstration itself |

All six confirmed present on 2026-08-31 [MEASURED].

---

## 8. COST

**Unit: core-minutes** (wall s × ranks ÷ 60), ranks = **1**. No solver, no `mpirun`,
no `decomposePar`, no propagation — every core-minute is `numpy` and shell.

**Basis:** R4b-I §7.3 registered **12.0 core-min estimate** and a **40.0 core-min hard
cap** [REGISTERED]. R4b-Ib's per-pass work is R4b-I's per-pass work: §7.3's clean-pass
line of **3.16 core-min** already contained B3 (**1.20**) and B4 (**0.67**), which
R4b-I costed but never graded. The successor adds only the D4 real-record control
(pure in-memory aggregation over an existing record, sub-second) and the parent hash
pin (four `sha256` reads, ~200 kB).

| line | core-min | basis |
|---|---|---|
| one clean pass of the birth suite | 3.16 | R4b-I §7.3, unchanged [REGISTERED] |
| development multiplier ×3 | 9.48 | R4b-I §7.3, unchanged [REGISTERED] |
| slack for repeated hash sweeps and `-O` re-runs | 2.52 | R4b-I §7.3, unchanged [REGISTERED] |
| D4 real-record control + parent pin | < 0.05 | in-memory aggregation; 4 file hashes [DERIVED] |

> **REGISTERED ESTIMATE: `12.0` core-minutes** = `0.200` core-h = **`$0.01026`**
> — **[DERIVED], NOT MEASURED.**
>
> **REGISTERED HARD CAP: `40.0` core-minutes** = `0.667` core-h = **`$0.03420`**
> — **[DERIVED], NOT MEASURED.** **The cap is R4b-I's, copied verbatim; it does not
> move.**
>
> **If accumulated spend reaches the cap the lane STOPS and reports `BLOCKED`. An
> overrun stops the run; it does not get a new budget** (standing rule 12).

Rate `$0.0513/core-h`, c7a.4xlarge — **[REPORTED-BY-OWNER]**, 2026-08-21/22. The box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure
above is **derived, not measured**. `grade_r4b_ib.py` measures its own core-minutes
from wall time and writes them into the birth record's `cost` block, and
`headline()` returns **`BLOCKED`** at the cap **ahead of** any gate verdict.

**Estimate-versus-actual calibration is owed at completion** (standing rule 12,
Sanaa's 2026-08-23 directive) as a row in `docs/COST_CALIBRATION.md`: ratio
actual/predicted, with the gap attributed and waste named separately.

---

## 9. WHAT HAS BEEN RUN, AND WHAT HAS NOT

**Run** — authoring verification only, no gate graded, nothing written outside a
session scratch directory:

| check | result |
|---|---|
| `grade_r4b_ib.py --selftest` under `python3` | **48/48, rc=0** [MEASURED] |
| `grade_r4b_ib.py --selftest` under `python3 -O` | **48/48, rc=0** [MEASURED] |
| `ast.Assert` nodes in `grade_r4b_ib.py`, parsed independently | **0** [MEASURED] |
| the four frozen instruments + R4b-I's registration, re-hashed after all work | **all five unchanged** [MEASURED] |
| `/home/ubuntu/closure-data/r4b_instruments/` written to | **no** — `find -newermt` empty, `du` 19M unchanged [MEASURED] |

**NOT run, and deliberately so:** `--birth-only` and `--d4-control`. Running either
before this document is committed would create first compute ahead of the freeze —
**the identical defect that closed R4b-I** — and would make
`/home/ubuntu/closure-data/r4b_ib_birth/` exist, falsifying §2's own pre-compute
condition. They are the first two actions **after** the freeze commit, in that order.

---

## 10. DEPARTURES AND OPEN QUESTIONS FOR THE SUPERVISOR

These are flagged, not decided. A lane does not resolve them.

1. **The successor is a wrapper, not a copy.** Importing the frozen parent makes
   "no band moved" mechanically true for B1 and B2 rather than a claim to be
   audited, and keeps the diff small enough to read. It also makes the successor
   depend on the parent's bytes — mitigated by the sha256 pin, which is a **new
   refusal** and therefore, strictly, a fifth change beyond the four authorised
   repairs. It moves no band, threshold, cap or label. **The supervisor should rule
   on whether the pin is in scope.**
2. **`R4b-I-ROOT-GUARD` is likewise a new refusal**, added to protect the evidence
   the ruling rests on. Same question, same answer requested.
3. **D1's residual window** (§3) — the frozen `:478` stays unguarded and only a
   call-site precondition protects it. Disclosed, not fixed, because fixing it would
   require editing a frozen file.
4. **§2j.2 is discharged only by the post-freeze real-record control** (§7.2). Until
   `--d4-control` has run on a real birth record, the successor's own birth is
   **`PENDING`**, and this document says so rather than letting a green selftest
   stand in for it.
5. **R4b-I's `_dev` compute is left exactly where it is.** No cleanup, no move, no
   relabelling. It is evidence.

---

## 11. FILES

| path | what |
|---|---|
| `cases/RANS_LES_closure_models/R4b_pair_control/R4b_Ib/grade_r4b_ib.py` | the successor instrument |
| `cases/RANS_LES_closure_models/R4b_pair_control/R4b_Ib/INSTRUMENT_BUILD_PREREGISTRATION_R4b_Ib.md` | this document |
| `/home/ubuntu/closure-data/r4b_ib_birth/r4b_ib_instrument_birth.json` | the birth record, **after** the freeze |
| `/home/ubuntu/closure-data/r4b_ib_birth/d4_control.json` | the real-record D4 control artefact, **after** the freeze |

**Both repository files land in ONE commit** (standing rule 2 fixes the grading path
at the pre-registration commit). **That commit is the closure supervisor's.** This
lane has committed nothing and staged nothing.
