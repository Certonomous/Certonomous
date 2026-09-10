# R4b-Ib — §2j.2 SELF-BIRTH OUTCOME, 2026-09-10

**HEADLINE: `GATE REACHED`.** B1–B5 all `PASS`; the real-record D4 control
`PASS` on both limbs. **§2j.2 is DISCHARGED.**

Run by a closure `lab-lane` on the closure-supervisor's dispatch, as the
registered **first post-freeze action** of the item
(`INSTRUMENT_BUILD_PREREGISTRATION_R4b_Ib.md` §7.2, §9). The lane edited no
frozen file, launched no solver, signalled no process it did not itself start,
and re-ran nothing.

| | |
|---|---|
| item | **R4b-Ib** |
| freeze commit | `2f94d743` |
| frozen instrument | `cases/RANS_LES_closure_models/R4b_pair_control/R4b_Ib/grade_r4b_ib.py` |
| instrument sha256 | `7bae9164000af4dff18794eeaa40a28c2d6c5ef79eaa59bf7aab75db50a53992` |
| run root | `/home/ubuntu/closure-data/r4b_ib_birth/` |
| interpreter | CPython 3.12.3, `sys.flags.optimize = 0` |
| UTC | limb 1 `2026-09-10T03:49:32Z`→`03:50:17Z`; limb 2 `03:51:16Z` |

---

## 1. GRADING-PATH VERIFICATION, BEFORE ANY COMPUTE (standing rule 2)

Performed in a single shell invocation before the instrument was invoked. The
frozen file **is** the file that ran:

| file | disk sha256 | vs |
|---|---|---|
| `R4b_Ib/grade_r4b_ib.py` | `7bae9164…a53992` | **MATCH** vs the committed blob at `2f94d743` |
| `R4b_Ib/INSTRUMENT_BUILD_PREREGISTRATION_R4b_Ib.md` | `27f9269f…f030cc8` | **MATCH** vs the committed blob at `2f94d743` |
| `grade_r4b.py` (imported parent) | `0e2554ae…34ca96` | **MATCH** vs the §4 pin |
| `select_control.py` | `50d9622d…7f290f` | **MATCH** vs the §4 pin |
| `build_r4b_cases.py` | `b45ddd8e…c11e82d7` | **MATCH** vs the §4 pin |
| `INSTRUMENT_BUILD_PREREGISTRATION.md` (§5 criteria source) | `7a80553c…01c289f9` | **MATCH** vs the §4 pin |
| `run_r4b.sh` (driven as a subprocess) | `f915bfed…62e853cf9` | **MATCH** vs §4 |

All seven **re-hashed after** both limbs: **unchanged**. The parent was imported
unmodified; the instrument's own `PINNED-INSTRUMENT` refusal did not fire.

**Pre-compute condition at launch** (§2): `/home/ubuntu/closure-data/r4b_ib_birth/`
**absent**, `test -e` rc=1 [MEASURED]. That root now exists, so **R4b-Ib's gates
are CLOSED** from `2026-09-10T03:49:32Z`, by the reasoning that closed R4b-I's.

---

## 2. LIMB 1 — `--birth-only` (rc=0)

Birth record `/home/ubuntu/closure-data/r4b_ib_birth/r4b_ib_instrument_birth.json`,
`record_sha256 = e0683f358efbff5cb5761e4a81ba771f556a3a44761fea679a02d7e6df3110b0`.

| gate | verdict | the measurement behind it |
|---|---|---|
| **B1** existence + refusals | **`PASS`** | 4 of 4 instruments present; **12 of 12** registered refusals fired, each exit 2 under **both** `python3` and `python3 -O`; `any_assertion_error = False`; selftests rc=0 |
| **B2** birth of the comparator | **`PASS`** | **6 of 6** G0 controls born two-sided (G0a–G0f all `PASS`, `born = True`); `pending = {}`; `not_born_gates = []` — §3.2's carve-out did **not** fire |
| **B3** birth of `select_control.py` | **`PASS`** | G0a `PASS`, G0e `PASS` through the selector's **own** reader; grid **12 of 12** values evaluated and reported; the instrument's self-report agreed with the registered-list aggregation (`B3-AGGREGATION-DISAGREES` did not fire) |
| **B4** birth of `build_r4b_cases.py` | **`PASS`** | all **4 of 4** refusals fired (`MODEL_ABSENT`, `MODEL_HASH`, `COVERAGE_ABSENT`, `CASE_TREE_EXISTS`); `term_order_n4` `PASS` (the `n in (1,2,3)` assert fires at the new call site on `n = 4`, standing rule 14); `set_libs_both_shapes` `PASS`; `positive_build` `PASS` — one real tree at `/home/ubuntu/closure-data/r4b_ib_birth/cases/alpha_125/pair`, over the real `R4_sparta_build/COVERAGE.md` |
| **B5** birth of `run_r4b.sh` | **`PASS`** | all **5 of 5** registered clauses `PASS`, and the clause set proved **equal** to the registered required list |

**Item verdict `PASS`; headline `GATE REACHED`** — computed by `headline()` over
§5.6's mapping table, the row "B1–B5 all `PASS`".

### 2.1 B5 in detail — the two-sided capacity check

* **Positive half:** a real background process (a copy of `/bin/sleep`, argv
  `[…/r4bBirthDemoNotASolverFoam, 20]`) was started **by the demonstration
  itself** and the check **counted it**: foreign-solver count **19 → 20**, and
  the planted process was **matched by name** in the reading.
* **Negative half:** the check did **not** refuse — registered concurrency
  resolved to **1**, not `BLOCKED`, so `B5-CAPACITY-NEG` did not fire.
* **Non-`pgrep` path fires by itself** (L-41): with the sweep disabled the check
  still produced a reading from **11** run-directories touched, **9** docket
  in-flight rows and **29** recent commits — solver count reported 0 and the
  reading stood anyway.
* **Skip-if-complete, two-sided:** skipped the real complete case
  `…/PHLL10595/ceiling` (rc=0, "COMPLETE complete (converged)") and did **not**
  skip the real incomplete `…/PHLL10595/discovered` (rc=1, "INCOMPLETE rc=136").
* **Never kills:** verified mechanically over the script's own bytes **with a
  planted positive control** that the sweep can see a planted kill verb. **No
  kill was run.**

**Box condition at launch, recorded because the busy half depends on it:**
`load1 = 23.47` on 16 vCPU — genuinely oversubscribed. The demonstration
nevertheless satisfied **both** halves.

### 2.2 THE REGISTERED LIMITATION, CARRIED FORWARD UNCHANGED

> **B5 exercises `run_r4b.sh` with its solver invocation replaced by a
> registered no-op.** The drive limb ran with `solver = /bin/true` (recorded in
> the birth record as "REGISTERED NO-OP; no simpleFoam was launched"), rc=0,
> case `alpha_125`, config `pair`, wall-seconds file written. **No `simpleFoam`
> was launched by this item. B5 therefore does NOT establish that `run_r4b.sh`
> can drive `simpleFoam`, and this item may not be read as having established
> it.**

### 2.3 REPORTED, NOT GRADED

B3's demonstration `xi* = 0.05` is **`reported, not graded`**. R4b's prediction
P1 belongs to R4b's registration and is graded there; **no verdict of this item
turns on it**, and R4b-I's `_dev` value remains **`NOT A RESULT`** and is not
quoted as one.

---

## 3. LIMB 2 — `--d4-control` ON THE REAL RECORD (rc=0)

Artefact `/home/ubuntu/closure-data/r4b_ib_birth/d4_control.json`, run against
the birth record limb 1 wrote — **not** a test-harness fixture.

* **Negative limb `PASS`:** each of the five required gates removed in turn;
  **all five refused, exit 2**, with the registered `B-GATE-SET` message. A
  missing gate is a refusal, never a silent omission.
* **Positive limb `PASS`:** the intact record **proceeded** to a verdict, `PASS`
  over `{B1…B5}`.
* `both_halves = True`; control verdict **`PASS`**.

**§2j.2 (who WROTE the bytes the control reads, L-402) is DISCHARGED.** The
bytes were written by `grade_r4b_ib.py`'s own `--birth-only` run over real
producer artefacts — a real `bijDelta`, a real `U`, a real `grad(U)`, the real
`run_r4b.sh`, the real `select_control.py`. §7.2's split stands as registered:
the **structural** D4 control inside `--selftest` does **not** discharge §2j.2
(its bytes are the instrument's own test harness) — that shortfall remains
**disclosed, not waived**, and this record does not lean on it.

---

## 4. GUARDS — WHAT WAS NOT TOUCHED

| assertion | measured after the run |
|---|---|
| R4b-I's evidence root `/home/ubuntu/closure-data/r4b_instruments/` unchanged | **19M**, and **0** files newer than the launch time |
| R4b's solve root `/home/ubuntu/closure-data/r4b/` still absent | **ABSENT** — the solve arm stays **`BLOCKED`** on Sanaa's direction |
| every frozen file byte-identical after the run | **7 of 7 unchanged** (§1 table) |
| any process signalled that this item did not start | **none** — the only `terminate()` on the path acts on the `Popen` object the demonstration itself created (the `/bin/sleep` copy) |

---

## 5. COST — ESTIMATE VERSUS ACTUAL (standing rule 12; Sanaa 2026-08-23)

**Unit: core-minutes** = wall s × ranks ÷ 60, **ranks = 1**. No solver, no
`mpirun`, no `decomposePar`.

| limb | wall s | core-min |
|---|---|---|
| `--birth-only` | 44.507 | **0.7418** |
| `--d4-control` | 0.216 | **0.0036** |
| **item total** | **44.723** | **0.7454** |

The instrument's own self-measurement in the record's `cost` block reads
**0.737 core-min** (its clock starts inside `main()`, so it excludes interpreter
start-up and import); the **0.7454** figure above is the outer wall-clock
measurement and is the one used for calibration. `cap_reached = false`.

The pre-compute freeze verification (seven `sha256sum` reads plus the source
inspection) was **not separately instrumented**; it was a few wall-seconds of
shell, bounded well under 0.2 core-min. It is named rather than folded in.

| figure | value |
|---|---|
| registered estimate | **12.0 core-min** = 0.200 core-h = **$0.01026 DERIVED, NOT MEASURED** |
| registered hard cap | **40.0 core-min** = 0.667 core-h = **$0.03420 DERIVED, NOT MEASURED** |
| **measured actual** | **0.7454 core-min** = 0.012423 core-h = **$0.000637 DERIVED, NOT MEASURED** |
| **ratio actual / estimate** | **0.062** |
| **ratio actual / cap** | **0.019** |
| gross vs cleaned | **gross = cleaned = 0.7454**; no row near the §2 3600-s stall rule |
| **waste** | **0.000 core-min**, named separately per `COMPUTE_BUDGET_CHARTER` §6 — no re-run, no crash, no refusal, no cap fire |

Rate **$0.0513/core-h**, c7a.4xlarge — **[REPORTED-BY-OWNER]** 2026-08-21/22.
The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so every
dollar figure here is **derived, not measured**.

### 5.1 Gap attribution

**MISPREDICTION — a budget-scope mismatch, not contention and not waste.**

1. **The 12.0 estimate is a BUILD-AND-DEMONSTRATE budget; this was the
   demonstration alone.** §8's lines are clean pass **3.16** + development
   multiplier ×3 (**9.48**) + slack for repeated hash sweeps and `-O` re-runs
   (**2.52**). The 9.48 and the 2.52 were consumed **before the freeze**, in the
   authoring session §9 records (`--selftest` under both `python3` and
   `python3 -O`). A post-freeze demonstration run can only ever spend the
   clean-pass line.
2. **Even the clean-pass line over-predicts by 4.2×**: 3.16 registered against
   0.7454 measured.
3. **NOT contention.** `load1 = 23.47` on 16 vCPU at launch — the box was
   oversubscribed, which pushes an actual **up**, not down. The under-run
   happened **despite** contention, so contention explains none of the gap.
4. **NOT a stopped run.** rc=0 on both limbs, every registered clause graded,
   cap untouched at 1.9 %.

### 5.2 CALIBRATION LESSON

**Price an instrument-birth suite in two separate budgets.** A pure
`numpy`-and-shell birth suite with no solver — 12 refusal exercises under
`python3` and `python3 -O`, six two-sided field controls, a 12-value selector
grid, one real case build and a no-op runner drive — costs **~0.75 core-min per
clean pass**, not 3.16. The **development multiplier belongs to the authoring
item and is spent before the freeze**; budgeting the post-freeze demonstration
at the build-and-demonstrate total over-predicts it by ~16×. Budget a
post-freeze self-birth demonstration at the clean-pass line only, and set the
clean-pass line for a solverless suite at ~1 core-min.

> **Ledger row NOT YET LANDED.** The `docs/COST_CALIBRATION.md` row is drafted
> from this section but is **held for the closure-supervisor's go**, per the
> lane's dispatch. Landing it uses `scripts/append_record.py` under the rule-10
> private-index protocol.

---

## 6. VERDICT, IN THE REGISTERED VOCABULARY

**`GATE REACHED`** — §5.6 row 1, B1–B5 all `PASS`, computed by `headline()`.

* The 40.0 core-min cap was **not** reached (0.7454), so the `BLOCKED` row did
  not fire.
* No B-gate read `GATE FAIL`, so the `GATE FAIL` row did not fire.
* No control was `PENDING`, so §3.2's carve-out and the composite headline label
  `GATE REACHED (PARTIAL)` did **not** fire. That label remains a headline-channel
  label only and appears in no per-gate cell.
* **§2j.2: DISCHARGED**, by §3's real-record control.

**What this verdict does NOT say.** It does not establish that `run_r4b.sh` can
drive `simpleFoam` (§2.2). It does not grade `xi*` (§2.3). It does not move
R4b's solve arm, which stays **`BLOCKED`** on Sanaa's direction and whose root
remains absent. It authorises **no submission** — standing rule 7, submissions
are PARKED.

Per §5.6 row 1, R4b's solve arm is now **registrable**.

---

## 7. FILES

| path | what |
|---|---|
| `/home/ubuntu/closure-data/r4b_ib_birth/r4b_ib_instrument_birth.json` | the birth record (`record_sha256 e0683f35…3110b0`) |
| `/home/ubuntu/closure-data/r4b_ib_birth/d4_control.json` | the real-record D4 control artefact |
| `/home/ubuntu/closure-data/r4b_ib_birth/cases/alpha_125/pair/` | B4's real built case tree |
| `/home/ubuntu/closure-data/r4b_ib_birth/birth/` | the per-instrument birth scratch (B1, B5 fresh run dir, selector, builder) |
