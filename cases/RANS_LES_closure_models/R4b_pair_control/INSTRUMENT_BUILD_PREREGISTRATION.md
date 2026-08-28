# R4b-I — THE R4b INSTRUMENT BUILD, REGISTERED AS A CAPPED WORK ITEM

**Rung:** `R4b-I` (the instrument build for `R4b_pair_control`)
**Team:** closure
**Status:** `prereg_commit: PENDING_SUPERVISOR_FREEZE`. The gates, thresholds,
cap and label below are **drafted and not yet closed**; the freeze is the closure
supervisor's act, performed personally under `SUPERVISION_CHARTER.md` §3 check 4,
and it is a commit whose message carries the sha256 of this document. Nothing has
been staged into any run root, no queue entry has been filed, and **no compute has
been spent producing this file — 0.0 core-minutes, no solver, no fit, no
propagation, no run directory created.** Standing rule 2 closes these gates at the
freeze; before it, amendments are legal and must state the condition and how it
was checked (§11).
**Drafted:** 2026-08-28, by a closure lab-lane on the closure supervisor's dispatch.

**Nothing here has been sent, filed, uploaded, registered, posted or commented**
(standing rule 7). This document is not in `verification/queue/` and this lane did
not put it there.

---

## 0. WHY THIS ITEM EXISTS, AND WHAT IT IS NOT

### 0.1 The rule that makes it a queue item

Sanaa amended FREEZE-AHEAD on 2026-08-28. Her words, verbatim
(`etc/sessions/2026-08-28T1701Z_sanaa_directives_control_regrade_freezeahead.md`,
directive 3):

> *"Queue depth 0 is a rule violation with an honest cause — so fix the rule, not
> the teams: when the nearest candidates are blocked on findings, the
> finding-repairs are the queue: they're frozen, capped, schedulable work items
> like any case. Amendment: 'Freeze-ahead counts repair-registrations; a team
> blocked on findings freezes the repairs and runs them — queue depth 0 with open
> findings is impossible by definition.'"*

Closure's `R4b_pair_control` is the canonical instance. It has stood at `PENDING`
because **four named instruments do not exist**. Under the amendment, **building
those four instruments IS the queue item**, and it is frozen, capped and costed
here like any case.

### 0.2 What this item is NOT, said before anything else

* **It is not R4b.** It runs no propagation, grades no closure model, and engages
  `CLOSURE_MODELLING_CHARTER.md` §2 not at all. It produces no `b_ij`, no
  velocity claim and no realisability verdict about any model.
* **It does not register `xi*`.** `select_control.py` is *run* here, in
  DEMONSTRATION mode, into a separate run root, and the `MODEL.json` it writes is
  stamped `DEMONSTRATION — NOT THE REGISTERED MODEL` (§4.3). The registered model
  artefact of R4b is written under R4b's own pre-registration, at commit 2 of that
  document's §14, and not here.
* **It does not authorise R4b's solve arm.** §7 costs that arm and explicitly
  does **not** release it. Its release needs a separate act and a decision that is
  not a lane's (§1).
* **It is not a repair of a frozen file.** Nothing under
  `R4_sparta_build/`, `_common/` or any existing `PREREGISTRATION.md` is edited.
  Ten instruments are **re-used by path and sha256, unmodified** (§3.1).

---

## 1. THE DECISION THIS ITEM DOES NOT MAKE, AND WHO OWNS IT

**This is the load-bearing honesty clause of the document.** The brief that
commissioned this registration asked, correctly, whether R4b can be registered as
one item. It cannot, and the reason is a decision, not a gap in the work.

`R4b_pair_control/PREREGISTRATION.md` §0.2 concedes it in its own words:

> *"This is the lab's ranking applied to Sanaa's ruling. It is not her choice of
> increment and it does not claim to be. `docs/LAB_STATE.md` (read at HEAD)
> records 'R5/A′ direction after R5C's GATE FAIL (`R5_DECISION_MEMO.md`)' as still
> on Sanaa's desk. She may overturn this increment, substitute another, or stop
> the line."*

The board agrees and has agreed for four days: `docs/LAB_STATE.md:2619` records
R4b as *"Still needs **Sanaa's direction on the increment** — its own §0.2 concedes
it is the lab's ranking, not her choice"*, and `:2844` lists as still owed *"her
direction on the increment itself"*.

**Therefore the split, registered:**

| arm | what it needs | who owns it | state |
|---|---|---|---|
| **R4b-I — the instrument build (THIS ITEM)** | nothing that is not on disk today | the closure supervisor, by freezing this file | **registrable now** |
| **R4b — the 12-case propagation and grading** | Sanaa's direction on whether `A′` is the increment | **Sanaa, and no agent at any level** | **BLOCKED**, and this file does not move it |

Registering the solve as a build step would be pretending a blocked decision is a
schedulable task. It is not registered here. **A smaller honest item is registered
instead**, and it is the item that unblocks everything downstream: whatever
increment Sanaa directs, a comparator that has never been shown able to see a
non-zero cannot grade it.

**A second, smaller decision is also NOT a lane's** and is named so it is not
absorbed: whether `select_control.py`'s demonstration output may later be promoted
to R4b's registered `MODEL.json`, or whether that file must be produced by a fresh
run under R4b's own frozen prereg. §4.3 registers the conservative answer — a
fresh run — and flags the alternative as the supervisor's to rule.

---

## 2. THE FOUR INSTRUMENTS, WHAT EACH MUST DO, AND THE ORDER

### 2.1 The measured absence, established today and not inherited

Re-established by this lane on **2026-08-28**, not taken from the board:

| file | on disk (box-wide `find`) | tracked in git | ever added on any ref |
|---|---|---|---|
| `select_control.py` | **ABSENT** (0 hits) | no | **no** |
| `build_r4b_cases.py` | **ABSENT** (0 hits) | no | **no** |
| `run_r4b.sh` | **ABSENT** (0 hits) | no | **no** |
| `grade_r4b.py` | **ABSENT** (0 hits) | no | **no** |
| `MODEL.md` (this directory) | **ABSENT** | no | no |
| `MODEL.json` (this directory) | **ABSENT** | no | no |
| `COVERAGE.md` (this directory) | **ABSENT** | no | no |
| `PREREGISTRATION.md` (this directory) | **PRESENT**, 1,361 lines, 76,470 bytes | **UNTRACKED** | **no** |

The `find` searched `/home/ubuntu` at unbounded depth excluding `.git`; the git
question was asked of `git log --all --diff-filter=A --name-only` over every ref.
**Both readers were shown able to return a non-zero on known-positive ground
truth before their zeros were believed** (standing rule 3, applied to a
documentary search): the same `find` invocation returns
`R4_sparta_build/r4_lib.py` and this directory's own `PREREGISTRATION.md`; the
same git pipeline returns **30** additions for `R4_sparta_build`; `git ls-files`
returns **30** tracked files for that sibling directory. A sweep that returns zero
without a positive control is measuring its own pattern, not the disk.

**`R4b` must not be confused with** `/home/ubuntu/certonomous-runs/w3-naca0012_wing-family/r4b`
and `.../w3-naca4412_wing-family/r4b`, which are wing-mesh refinement levels of a
different family and are unrelated. This item touches neither.

### 2.2 What each instrument must do

Each specification below is **quoted or derived from the R4b pre-registration
already on disk** (§3.4, §3.5, §5 G0, §9) — this item implements a specification
that exists; it does not invent one.

| instrument | what it must do | its registered refusals |
|---|---|---|
| **`select_control.py`** | Compute `xi*` by R4b §3.4: the **largest** value on the frozen 12-value grid `{0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30, 0.50, 0.70, 1.00}` at which `b_total = b_lin + xi·b^Delta` is realisable at `tol = 1e-6` on **every** fitted cell of **all 12** training cases, with `max_cell ||b_total||_F <= sqrt(2/3)`. Mask = R4's fit mask, re-used unmodified (`fs3_select.py:89-90`, 172,106 of 172,171 cells). Realisability = `_common/of_read.realisability_violation`, re-used unmodified. Writes `MODEL.md` / `MODEL.json` carrying `xi*`, the full grid, the feasibility result at **every** grid value, and the binding case and cell. | exit 2 if no reader control passes; **`BLOCKED`, never `xi* = 0`**, if no grid value is feasible (R4b §3.4, §7 F4); exit 2 if it is asked to select on anything but realisability |
| **`build_r4b_cases.py`** | Build the 12 propagation cases by calling `build_aposteriori.build()` **unmodified** with the `xi`-scaled term sets. Re-assert `n in (1,2,3)` **at the new call site** (standing rule 14 — `kOmegaSSTSparta` reads T1/T2/T3 only and would silently evaluate an `n = 4` term as T3). Use `r4_lib.set_libs`, which inserts-or-replaces **and then asserts the library name is present** (L-221/L-222). | **exit 2** unless `MODEL.json` exists, carries a `frozen_at` timestamp, and **hashes equal to the committed blob**; exit 2 without a present `COVERAGE.md`; exit 2 over an existing case tree |
| **`run_r4b.sh`** | Drive the 12 cases: R4b §11's pre-launch capacity check (**which does not trust `pgrep` alone** — fleet agents are invisible to it, L-41), `JOBS=2`, `nice -n 10`, skip-if-complete, **never kill a running solver**. Record `wall_seconds` per case for the calibration duty. | refuses to start when the box is busier than the registered concurrency limit; refuses to re-run a case already complete under R4b §4.2 |
| **`grade_r4b.py`** | The comparator. Grade G0–G7 **as R4b §5 writes them**; re-hash every re-used instrument and every re-used artefact and **refuse on any mismatch**; apply the strict completion rule with its age guard (standing rule 4); write `artefacts/r4b_grading.json`. **Emit only the six-word vocabulary** (standing rule 1). | **exit 2** on any G0 control failing → the run is `NOT A RESULT` and the lane stops; exit 2 on any instrument hash mismatch; **exit 2 rather than degrade** on an incomplete run; **no refusal may be an `assert`** (L-332), since `-O` would erase it |

### 2.3 THE ORDER, AND IT IS PART OF THE REGISTRATION

Two orders bind, and they are different things. Both are registered here because
`build_r4b_cases.py` **refuses** unless the model files precede it — that is a
mechanically enforced dependency, not an implementation preference.

**ORDER A — the RUNTIME freeze order that the instruments must IMPLEMENT**
(R4b §3.5, quoted): `select_control.py` runs and writes `MODEL.md`/`MODEL.json`
→ those two are **committed** → *only then* may `build_r4b_cases.py` run, and it
refuses (exit 2) unless `MODEL.json` exists, carries `frozen_at`, and hashes equal
to the committed blob. **No propagation case can be built before the control value
is on the record.** R4b §9 adds a fourth precondition: a **present `COVERAGE.md`**
(the FS2/FS5 discharge). This order is a property the instruments must *enforce*,
and B4 (§5) grades whether they do.

**ORDER B — the AUTHORING order of this item**, because a birth demonstration can
only run on artefacts that already exist:

| step | what is written / run | why it must come here |
|---|---|---|
| **A0** | `COVERAGE.md` for R4b, **regenerated by the existing frozen `make_coverage.py`** (`f8c40810…`, unmodified) | it is a *precondition* of `build_r4b_cases.py`, so it must exist before B4's positive half can fire at all |
| **A1** | `select_control.py` | it is the only new instrument whose inputs are all already on disk (R4's frozen fields); it depends on none of the other three |
| **A2** | **B3 — the birth of `select_control.py`** (§5) | it must be shown able to see a non-zero **before** its output is believed, and its total-`b` array is the artefact G0e plants into |
| **A3** | `build_r4b_cases.py` | its refusal set is defined against `MODEL.json`, which A2 has now produced in demonstration form |
| **A4** | **B4 — the birth of `build_r4b_cases.py`** (§5) | both halves: four refusals must fire, and one real case tree must actually build |
| **A5** | `run_r4b.sh` | it drives the trees A4 built; skip-if-complete needs a real complete case to skip |
| **A6** | **B5 — the birth of `run_r4b.sh`** (§5), with the registered solver substitution and its disclosed limitation | |
| **A7** | `grade_r4b.py` | it re-hashes and drives all three others, so it is written last |
| **A8** | **B1 and B2 — existence/refusal sweep, and the birth of the comparator** (§5) | B2 is the item's headline gate |

**A departure from ORDER B is a departure and is recorded as one** (§10). A
departure from ORDER A is a defect in the instrument and is a `GATE FAIL` at B4.

---

## 3. SUBSTRATE — every artefact this item reads already exists, and was hashed today

### 3.1 The ten re-used instruments, re-hashed by this lane on 2026-08-28

`disk` measured today. The first seven match `R4b/PREREGISTRATION.md` §9's
recorded table **exactly**; the last three the draft left as *"(re-hashed at
freeze)"* and are supplied here.

| instrument | path (relative to `cases/RANS_LES_closure_models/`) | sha256, measured 2026-08-28 | vs §9 |
|---|---|---|---|
| registry, builders, `assert_no_test_case`, `frozen_complete`, `run_complete`, `planted_zero_reader_check`, `set_libs` | `R4_sparta_build/r4_lib.py` | `23f37c0c2f296bc82e2dd48aeb68ac5baaffa25d8beb3c119430eadcbcf81fe0` | **matches** |
| propagation case builder | `R4_sparta_build/build_aposteriori.py` | `7c1150c5aad67252aeb1fbacf945809bce7bb386b0cbb7dfbdeaacbcce77e4dd` | **matches** |
| a-priori scorer | `R4_sparta_build/score_apriori.py` | `b034c9ef6214ba9c56f11f0145e29a96928320e9693ff73fe3e9e9dc26b04da2` | **matches** |
| a-posteriori scorer | `R4_sparta_build/score_aposteriori.py` | `6dc3cce2ce00f7d3d7bbda45f528bea6c9023a528babad19ed09f9ec21aa099c` | **matches** |
| FS3 selection (mask source, **not re-run**) | `R4_sparta_build/fs3_select.py` | `287e03d9f2c7b477a79a45f70ca6b18c4284969cff05b5b3786158d4b51e02e4` | **matches** |
| coverage generator, FS2/FS5 | `R4_sparta_build/make_coverage.py` | `f8c40810349c1caf5d633797d4e8d3f703a5a6b53de11c9f8b49010f82a6adb6` | **matches** |
| solver/Python cross-check (IC1) | `R4_sparta_build/ic1_check.py` | `342ac8ce735c6035e9e770abfa73e8b72eaace2a0d94a25e4ac8d1ac7e7282a0` | **matches** |
| field reader, barycentric realisability, structured gradients | `_common/of_read.py` | `4263001cf8ad58b3671e22b8b12b72de926c6638416c7d9711aa9f0cd31705c8` | supplied |
| reattachment / secondary-flow instruments | `_common/sst_baseline_metrics.py` | `7d78aebc222daa60fdb644d744e6f2d90d83337a84e665ea8f435dac341080ed` | supplied |
| the train-mean baseline (G1's bar) | `_common/trainmean_baseline.json` | `eb6378a403c923b238c984a16df193674d05857c78e38918cfe3ded8ff566f00` | supplied |

`r4_lib.py` carries the five functions this item leans on, at
`:69 assert_no_test_case`, `:94 set_libs`, `:224 run_complete`,
`:272 frozen_complete`, `:432 planted_zero_reader_check` — read, not assumed.

**All ten are re-used unmodified. This item edits none of them.** `grade_r4b.py`
re-hashes all ten at grading and refuses on any mismatch.

### 3.2 The REAL producer artefacts the birth demonstrations must travel

Sanaa's canonized requirement, verbatim (2026-08-28):

> *"A planted control must travel the real production path — written by the real
> producer's code, read through the real reader — and prove the instrument sees a
> non-zero the same way reality would deliver one. A control that empties the
> tuple it tests, or writes a schema the producer never emits, tests nothing and
> certifies blindness."*

**Every plant in §5 therefore goes into a scratch copy of a REAL file written by
the real producer**, and is read back by the real reader. No synthetic string, no
hand-authored field header, no constructed array standing in for an OpenFOAM
field. The artefacts exist today, measured 2026-08-28:

| control | real artefact class | count on disk | one named instance |
|---|---|---|---|
| G0a, G0b | `bijDelta`, written by the frozen extraction | **573** | `/home/ubuntu/closure-data/r4/frozen/AR_10_Ret_180/1654/bijDelta` |
| G0c | `U`, written by the propagation solver | present in every case | `/home/ubuntu/closure-data/r4/aposteriori/PHLL10595/ceiling/3513/` |
| G0d | `grad(U)`, written by the real `postProcess` | **68** | `/home/ubuntu/closure-data/r5c/frozen/CBFS13700/354/grad(U)` |
| G0e | total-`b` array, produced by `select_control.py` itself in step A1 | produced at A1 | (written into this item's run root) |
| G0f | a case-name list handed to `assert_no_test_case` | n/a — a guard, not a field | `NASA_2DWMH` |

R4 has already round-tripped this pattern once and left the evidence:
`/home/ubuntu/closure-data/r4/_plant/` holds a 1,533,690-byte `bijDelta` and a
790,521-byte `U` — real producer output, copied for planting. **This item copies;
it never plants into an original.**

**G0d's carve-out, registered in advance and not needed today.** If at birth time
the real artefact a control needs does **not** exist, that control is recorded
`PENDING: <path>`, the instrument is recorded **NOT BORN** for the gate that
control serves, and `grade_r4b.py` **must refuse to grade that gate**. It is
registered now so it can never be used later to soften a `GATE FAIL`. For G0d the
artefact **does** exist (68 instances, verified 2026-08-28), so the carve-out is
not expected to fire.

### 3.3 The run roots, and why they must be two

| root | state, measured 2026-08-28T17:20:38Z | belongs to |
|---|---|---|
| `/home/ubuntu/closure-data/r4b_instruments/` | **ABSENT** (`test -e` rc = 1) | **this item** |
| `/home/ubuntu/closure-data/r4b/` | **ABSENT** (`test -e` rc = 1) | R4b's solve arm (its §14) |

**This is not cosmetic.** R4b's own pre-registration is pre-compute, and its
pre-compute condition is that `/home/ubuntu/closure-data/r4b/` does not exist. If
this item wrote there, it would destroy that condition and close R4b's amendment
window before Sanaa has ruled on the increment. **This item writes only under
`/home/ubuntu/closure-data/r4b_instruments/` and never under
`/home/ubuntu/closure-data/r4b/`.** `grade_r4b.py --birth-only` asserts the second
root is absent before it begins, and exits 2 if it is not.

---

## 4. WHAT IS WRITTEN, WHERE, AND WHAT IS DELIBERATELY NOT COMMITTED

### 4.1 Files this item creates

| file | location | committed? |
|---|---|---|
| `select_control.py` | this directory | yes, at §9 commit I-2 |
| `build_r4b_cases.py` | this directory | yes, at §9 commit I-2 |
| `run_r4b.sh` | this directory | yes, at §9 commit I-2 |
| `grade_r4b.py` | this directory | yes, at §9 commit I-2 |
| `COVERAGE.md` | this directory | yes, at §9 commit I-2 |
| `artefacts/r4b_instrument_birth.json` | this directory | yes, at §9 commit I-3 |
| `INSTRUMENT_BUILD_RESULTS.md` | this directory | yes, at §9 commit I-3 |
| case trees, planted scratch copies, demonstration `MODEL.json`, `MaxRSS` records | `/home/ubuntu/closure-data/r4b_instruments/` | **no — bulk data is never committed**; paths listed in the results record |

### 4.2 What is NOT touched

`R4b_pair_control/PREREGISTRATION.md` (the solve registration) is **not edited**,
not amended and not struck. `R4_sparta_build/`, `R5C_omega_repair/`, `_common/`
and `scripts/` are **not edited**. `G2_grid_triple_duct/` **is computing** and is
read-only to this item. `/home/ubuntu/closure-data/` is read-only to this item
outside its own new root.

### 4.3 The demonstration `MODEL.json` is NOT the registered model

`select_control.py`'s demonstration run writes to
`/home/ubuntu/closure-data/r4b_instruments/MODEL.json`, **not** to this directory,
and its first key is:

```
"provenance": "DEMONSTRATION — NOT THE REGISTERED MODEL. Written by R4b-I's
               birth demonstration under INSTRUMENT_BUILD_PREREGISTRATION.md.
               R4b's registered MODEL.json is produced by a fresh run under
               R4b/PREREGISTRATION.md section 14 commit 2, after Sanaa has
               directed the increment."
```

**Registered, conservatively:** the demonstration output may **not** be promoted
to R4b's registered `MODEL.json`. R4b's §14 commit 2 requires a fresh run. Whether
that conservatism is necessary — whether a demonstration run of a frozen,
deterministic selector may stand as the registered selection — is a question for
the closure supervisor, and it is flagged in §12 rather than decided here.

---

## 5. THE GATES — registered now, before any instrument is written

Verdict vocabulary: `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
`BLOCKED` / `PENDING`, and nothing else (standing rule 1). **Every gate below can
fail.** A quantity reported without a bar is named `reported, not graded` and is
not called a gate.

### 5.0 THE BIRTH REQUIREMENT, which governs every gate below

Sanaa's companion rule, canonized 2026-08-28, verbatim:

> *"rule 3's question — 'was this reader ever shown able to see a non-zero through
> the real code path?' — is now the birth requirement for every reader/comparator:
> no instrument grades anything until that answer is yes, demonstrated."*

**Registered consequence, and it is the whole point of this item:**
**`grade_r4b.py` may not grade anything — not one gate of R4b's G0–G7 — until it
has returned a non-zero through the real code path on a real producer artefact,
and that demonstration is on the record.** A comparator that has never returned a
non-zero through the real path is **NOT BORN** and its zeros are not evidence.
`grade_r4b.py` enforces this on itself: it reads
`artefacts/r4b_instrument_birth.json`, verifies the birth record's own hash, and
**exits 2** if any control it needs is not recorded born.

**Every birth demonstration is TWO-SIDED.** One side is not enough:

* the **positive** half — the instrument **must SEE** the plant, recovering it
  through the real reader from a real file on disk; and
* the **negative** half — the instrument **must NOT flag** an unperturbed copy of
  the same real file through the same path.

A demonstration carrying only the positive half certifies nothing about false
positives; only the negative half separates a working reader from one that flags
everything. Both halves are graded.

### B1 — EXISTENCE AND REFUSAL

> All **four** instruments exist at their registered paths, are importable /
> executable, and **every registered refusal in §2.2 fires**, each exercised by a
> planted condition on a real artefact, each returning **exit 2** and **not** an
> `AssertionError` (L-332: no refusal may be an `assert`, since `python -O`
> erases it). Each refusal is additionally re-run under `python3 -O` and must
> still fire.
>
> **`PASS` requires 4 of 4 instruments present and 100 % of registered refusals
> firing under both `python3` and `python3 -O`. Anything less is `GATE FAIL`.**

### B2 — THE BIRTH OF `grade_r4b.py`, the comparator

> All **six** of R4b §5's G0 controls — G0a, G0b, G0c, G0d, G0e, G0f —
> demonstrated **two-sided** through the comparator's own real code path, on real
> producer artefacts named in §3.2.
>
> * G0a–G0d: `PLANT = 1.234e-03` planted into a **scratch copy of a real
>   OpenFOAM field**, recovered through the real reader. The bar is
>   `r4_lib.planted_zero_reader_check`'s, re-used unmodified:
>   `max(1e-12, 8·eps·max|field|)`, **and** the median recovery matching the
>   plant to `1e-9` relative. It is magnitude-aware for the reason R4 recorded as
>   departure D-9 — an absolute `1e-12` bar refused a demonstrably correct reader
>   on a field reaching `2.8e+06`.
> * G0e: a cell forced to a known non-realisable anisotropy (a barycentric
>   coordinate driven to `-1e-3`). **The violating count must rise by EXACTLY
>   one** — not "by at least one", which a routine that flags everything also
>   satisfies — and must **not** rise on the unperturbed copy.
> * G0f: `NASA_2DWMH` placed inside a list handed to `assert_no_test_case`, which
>   must raise; and a list without it, on which it must **not** raise.
>
> **`PASS` requires 6 of 6 controls demonstrated, both halves each. Anything less
> is `GATE FAIL` and `grade_r4b.py` is NOT BORN**, except where §3.2's registered
> carve-out applies, in which case that control is `PENDING: <path>` and the
> comparator is recorded NOT BORN **for the specific gate that control serves**
> and must refuse to grade it.

**This gate is the item's reason for existing.** R4b §5's own words: *"A
violating-fraction of `0.0000` is exactly the kind of zero rule 3 exists for:
without a planted non-realisable cell, a broken barycentric routine and a
perfectly realisable model return the same number."*

### B3 — THE BIRTH OF `select_control.py`

> G0a and G0e demonstrated two-sided through **`select_control.py`'s own** reader,
> not through the comparator's; plus the selector run over the full frozen
> 12-value grid, producing a feasibility result at **every** grid value — the
> registration requires all twelve reported, so a selector that silently
> short-circuits is visible.
>
> **`PASS` requires both controls two-sided AND 12 of 12 grid values evaluated
> and reported. Anything less is `GATE FAIL`.**
>
> **Registered and NOT graded here:** the *value* of `xi*`. R4b's prediction P1
> (`xi* ∈ [0.02, 0.20]`, point `0.10`) belongs to R4b's registration and is graded
> there. This item reports the demonstration value beside the gate, labelled
> `reported, not graded`, and **no verdict of this item turns on it.** Grading it
> here would be this item pre-empting a decision that is Sanaa's (§1).

### B4 — THE BIRTH OF `build_r4b_cases.py`

> **Negative half:** all four registered refusals fire — no `MODEL.json`; a
> `MODEL.json` whose hash differs from the committed blob; a missing `COVERAGE.md`;
> an existing case tree. Each exit 2, each under `-O` too.
>
> **Positive half, and it must be REAL:** with all four preconditions met, the
> builder builds **one real case tree** by calling `build_aposteriori.build()`
> unmodified, into this item's run root. Verified on that tree:
> * the `n in (1,2,3)` assert is present **at the new call site** and fires when
>   handed `n = 4` (standing rule 14 — a lesson is not applied until **every**
>   call site asserts it);
> * `set_libs` is verified on **both** real shapes, because a bare `str.replace`
>   is a silent no-op on one of them and the run then returns the **baseline**
>   field, which looks like a physical answer: **(i)** a hill case, which carries
>   **no `libs` line at all**, and **(ii)** a duct case, which carries one naming
>   a library that does not exist on this machine. After `set_libs`, the library
>   name must be **present** in both, asserted by `set_libs` itself.
>
> **`PASS` requires 4 of 4 refusals AND the positive build with both `set_libs`
> shapes and the `n` assert verified. Anything less is `GATE FAIL`.**

### B5 — THE BIRTH OF `run_r4b.sh`, and its registered limitation

> * **Pre-launch capacity check, two-sided:** it must **see** a real busy box (a
>   planted, real background process it is required to count) and must **not**
>   refuse on a quiet box. **It must not rely on `pgrep` alone** — fleet agents
>   are invisible to it (L-41) — so the check reads run-directory mtimes and the
>   docket as well, and the demonstration confirms the non-`pgrep` path fires by
>   itself.
> * **Skip-if-complete, two-sided:** it must **skip** a real complete case
>   (`/home/ubuntu/closure-data/r4/aposteriori/PHLL10595/ceiling/`, which carries
>   the real producer's own `rc`, `wall_seconds` and written time `3513`) and must
>   **not** skip a real incomplete one.
> * **It must never kill a running solver**, verified by inspection of the diff,
>   not by running a kill.
>
> **`PASS` requires all three, both halves each. Anything less is `GATE FAIL`.**

> **REGISTERED LIMITATION, disclosed in advance, not discovered later.** B5
> exercises `run_r4b.sh` with its solver invocation replaced by a registered
> no-op. **No `simpleFoam` is launched by this item.** Therefore **B5 does NOT
> establish that `run_r4b.sh` can drive `simpleFoam`**, and this item may not be
> read as having established it. The fail-fast for that is R4b's own first
> propagation case, under R4b's registration, after Sanaa has directed the
> increment. Stating this after the fact would have been a departure; stating it
> here makes it a boundary.

### 5.6 Verdict mapping, and the item's headline

| condition | verdict |
|---|---|
| B1–B5 all `PASS` | **`GATE REACHED`** — the four instruments exist, are frozen by sha, and every reader in them has been shown able to see a non-zero through the real production path. R4b's solve arm becomes **registrable**, and remains **`BLOCKED`** on Sanaa's direction (§1). |
| any B-gate `GATE FAIL` | **`GATE FAIL`** — the instrument is repaired, the demonstration re-run, and the repair costed inside the same cap. **The cap does not move.** R4b stays `PENDING`. |
| a control's real artefact absent, per §3.2's carve-out | that control **`PENDING: <path>`**; the instrument **NOT BORN** for the gate it serves and refuses to grade it; the item's headline is `GATE FAIL` unless the carve-out is the only shortfall, in which case it is `GATE REACHED (PARTIAL)` with the not-born gate named. |
| the 40.0 core-min cap is reached | **`BLOCKED`** — the run stops and reports. An overrun stops the run; it does not get a new budget (standing rule 12). |
| not yet started | **`PENDING`** |

**No other word is used.** In particular a demonstration that "mostly" worked, a
reader that "probably" sees the plant, or an instrument "expected" to be born is
**`GATE FAIL`**. Honesty is carried by the value and the label, never by an
adjective.

### 5.7 The registered falsifier

**If any one of the four instruments cannot be given a two-sided birth
demonstration on a real producer artefact, this item has found that R4b's
instrument set is not buildable as specified**, and that is a finding about the
specification, reported as such — not a reason to lower the bar.

---

## 6. WHAT THIS ITEM WOULD AND WOULD NOT ESTABLISH

**WOULD establish:**
1. That the four named instruments **exist**, at named paths, frozen by sha256.
2. That **every reader in them has returned a non-zero through the real
   production path**, on artefacts written by the real producer's own code —
   Sanaa's birth requirement, discharged and on the record.
3. That every registered refusal **fires**, including under `python3 -O`.
4. That `build_r4b_cases.py` **mechanically enforces** R4b §3.5's freeze order, so
   no propagation case can be built before the control value is on the record.
5. That `set_libs` behaves correctly on **both** real `libs` shapes in the corpus
   — the failure that would otherwise return a baseline field looking like physics.

**WOULD NOT establish, and must not be read as establishing:**
1. **Any physics.** No closure model is scored, no `b_ij` predicted, no velocity
   claim made, no realisability verdict reached about any model.
2. **That `run_r4b.sh` can drive `simpleFoam`** — §5's B5 limitation, registered.
3. **That `xi*` is any particular value.** The demonstration value is
   `reported, not graded` (§5 B3).
4. **That `A′` is the right increment.** That is Sanaa's (§1). A born comparator
   is equally necessary whatever she directs.
5. **That R4b will converge, propagate, or pass any of its own gates.** This item
   builds the instrument; it does not anticipate the reading.
6. **That the instruments are correct.** A born reader is a reader shown able to
   see a non-zero. It is not a proven-correct reader. Birth is a floor, not a
   ceiling — and the supervisor's §3 check-1 diff of each of the four scripts is
   the separate, non-delegable act that this gate does not replace.

---

## 7. COST — the instrument build and the solve, separated, and the reason they are separated

### 7.1 Unit, rate and the honesty label

**Unit: core-minutes** = `wall_seconds × ranks ÷ 60` (standing rule 12). **All work
here is serial, `ranks = 1`**, so core-minutes equal wall-minutes. Rate
**`$0.0513` per core-hour**, c7a.4xlarge, **owner-stated 2026-08-21/22 —
reported-by-owner, NOT measured**: this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). **Every dollar figure below is DERIVED, NOT
MEASURED**, and is labelled so wherever it appears.

**`cost_basis`: DERIVED, NOT MEASURED.**

### 7.2 Why the two components are registered apart

Writing four scripts costs **zero core-minutes of compute** — it is lane time, not
machine time. The solves those scripts drive cost **real** core-minutes. Registered
as one undifferentiated number, the 189 core-minutes of propagation would swallow
the 12 core-minutes of instrument work and neither would be recoverable at
calibration. **They are registered apart, capped apart, and released apart.** The
`docs/COST_CALIBRATION.md` row at completion (§8) carries them as two lines.

### 7.3 COMPONENT A — THE INSTRUMENT BUILD (this item, and the only thing this file authorises)

**Authoring compute: 0.00 core-minutes.** No solver, no `mpirun`, no
`decomposePar`, no `processor*` directory, no propagation. Every core-minute below
is `numpy` and shell.

**Measured anchor, and there is only one that matters:** `make_coverage.py`
measured **30.6 core-seconds** for **two SVD sweeps over the same 172,106 cells**
this item's selector reads (cited at `R4b/PREREGISTRATION.md:975-977`). One
barycentric-plus-norm pass over that mask is taken at **15 core-seconds** from that
anchor. Everything below derives from it or from file sizes measured today.

| line | basis | core-min |
|---|---|---|
| B2, G0a–G0d — four planted round trips on **real** fields | 1,533,690-byte `bijDelta` and 790,521-byte `U` measured today; `of_read` parse at 5 core-s each | **0.33** |
| B2, G0e — two-sided realisability over 172,106 cells | 15 core-s per pass × 3 (plant, re-read, negative half) = 45 core-s | **0.75** |
| B2, G0f — zero-shot guard, both halves | sub-second | **0.02** |
| B3 — `select_control.py` demonstration, 12 grid values | R4b §10.2 line (1) registers this at `0.020 core-h`, itself 2.4× the `make_coverage` anchor | **1.20** |
| B4 — four refusals (5 core-s each) + one real case tree built | `build_aposteriori.build()`, no solve | **0.67** |
| B5 — capacity check, skip-if-complete; **no solver** | ≤ 10 core-s | **0.17** |
| B1 — sha256 sweep, 10 re-used + 4 new instruments | ~200 kB hashed | **0.02** |
| **one clean pass of the whole birth suite** | | **3.16** |
| registered development multiplier **×3** — first draft, one repair, one clean confirmation; a birth demonstration that succeeds on the first attempt is the exception, not the plan | | **9.48** |
| slack for repeated hash sweeps and `-O` re-runs | | **2.52** |

> **REGISTERED INSTRUMENT-BUILD ESTIMATE: `12.0` core-minutes** = `0.200` core-h
> = **`$0.01026` — DERIVED, NOT MEASURED.**
>
> **REGISTERED INSTRUMENT-BUILD HARD CAP: `40.0` core-minutes** = `0.667` core-h
> = **`$0.03420` — DERIVED, NOT MEASURED.** That is **3.33×** the estimate.
>
> **If accumulated spend reaches the cap, the lane STOPS and reports `BLOCKED`.
> An overrun stops the run; it does not get a new budget** (standing rule 12).
> The cap is generous against the estimate on purpose: the risk in a birth
> demonstration is **iteration count**, not per-pass cost, and 40.0 core-min buys
> roughly **twelve** clean passes.

**Reduction clause, registered:** if accumulated spend reaches **20.0 core-min**
(50 % of cap) with any B-gate ungraded, the `-O` re-runs of already-passing
refusals are dropped, and the reduction is reported as a departure. **The cap does
not move.**

### 7.4 COMPONENT B — THE SOLVE ARM (costed for the record; **NOT authorised here**)

Carried forward from `R4b/PREREGISTRATION.md` §10.2 and §10.3 and **converted to
core-minutes**, the lab's unit. **This file does not release any of it.**

| line | core-h (as registered in the R4b draft) | **core-min** | $ DERIVED |
|---|---|---|---|
| control selection, `xi*` | 0.020 | 1.20 | 0.00103 |
| a-priori scoring, G1 | 0.005 | 0.30 | 0.00026 |
| **pair-control propagation sweep, 12 cases** | **3.108** | **186.48** | 0.15944 |
| `postProcess -func 'grad(U)'` for G4 | 0.012 | 0.72 | 0.00062 |
| a-posteriori scoring + grading | 0.005 | 0.30 | 0.00026 |
| **GRADED-ARM ESTIMATE** | **3.150** | **189.0** | **$0.16160** |
| diagnostic contingency (`R`-only sweep, reported not graded) | 1.733 | 103.98 | 0.08890 |
| **ESTIMATE WITH CONTINGENCY** | **4.883** | **292.98** | **$0.25050** |
| **HARD CAP** | **8.000** | **480.0** | **$0.41040** |
| floor, if every propagation dies in 5–18 iterations as R4's did | 0.094 | 5.64 | $0.00482 |

**The cap ratios check out as the draft states them:** `8.000 / 4.883 = 1.638`
("1.64×") and `8.000 / 3.150 = 2.540` ("2.54×").

**Corroboration of the basis, traced by this lane rather than inherited.** The
`3.108 core-h` propagation line rests on R4's measured 12-case sweep of
**`11,176 s`**, and that figure **is on disk** — `docs/closure/R5_DECISION_MEMO.md:97-98`
states *"one converged propagation solve, mean over the 12 CEILING runs,
`11,176 s / 12 / 3600` = 0.259 core-h"* and *"one 12-case single-configuration
sweep (CEILING), `11,176 s / 3600` = 3.104 core-h"*. It is **not** in
`R4_sparta_build/RESULTS.md` (searched, with the reader shown able to see a
positive: the same grep returns 10 hits for `core-h` in that file). **A rounding
note, in the conservative direction:** `11,176 / 12 / 3600 = 0.25870` core-h; the
draft rounds to `0.259` and multiplies by 12 to get `3.108`, where the memo's own
un-rounded figure is `3.104`. The difference is `+0.004 core-h`, registered
**upward**, and it is noted rather than corrected because the draft's arithmetic
is internally consistent and rounding upward is the safe direction for a cap.

### 7.5 The two caps are NOT summed

**This item's cap is `40.0` core-minutes and that is the only ceiling this file
sets.** The solve arm's `480.0` core-minutes is released by a separate act, on
Sanaa's direction on the increment (§1). If both ever run, the combined ceiling is
`520.0` core-minutes = `8.667` core-h = **`$0.4446` DERIVED** — stated so a reader
can see the total, **not** registered as this item's cap. A blanket is not a
per-item read (standing rule 9), and neither is a sum.

Both figures sit far under $25 and inside `CLOSURE_MODELLING_CHARTER.md` §18's 487
pre-authorised core-hours — this item's cap is **0.14 %** of that ceiling. **The
cost is registered here regardless**, because a proposal with no cost is
disqualified (standing rule 12).

---

## 8. `memory_floor_gb` — an ALLOWANCE, and it says so

**Derived, not measured.** The selector holds the fit mask's 172,106 cells as
`float64` symmetric 3×3 tensors: `172,106 × 9 × 8 B = 12.4 MB` per tensor field.
With `b_lin`, `b^Delta`, `b_total`, `S`, `Omega`, `tau` and numpy working copies —
roughly ten such fields at 3× transient overhead — the arithmetic gives **≈ 0.4 GB**.

**Registered: `1.0` GB**, roughly **2.5×** the derived estimate.

**This lane measured no `MaxRSS`.** `make_coverage.py`'s own footprint over the
same mask was **not** measured and is not claimed. No solver is launched by this
item, so no `simpleFoam` footprint is involved at all. The birth run captures real
`MaxRSS` with `/usr/bin/time -v` into
`/home/ubuntu/closure-data/r4b_instruments/mem_time.txt`, which converts this
allowance into a reading for the next pre-registration.

---

## 9. WHAT IS COMMITTED, AND WHEN

| commit | contents | when |
|---|---|---|
| **I-1** | **this file, ALONE**, with its sha256 in the commit message | **before** any instrument of this item is written |
| **I-2** | `select_control.py`, `build_r4b_cases.py`, `run_r4b.sh`, `grade_r4b.py`, `COVERAGE.md`, each with its sha256 in the message | after authoring, **before** the birth demonstrations are graded |
| **I-3** | `artefacts/r4b_instrument_birth.json`, `INSTRUMENT_BUILD_RESULTS.md` with the verdict, departures, the estimate-vs-actual comparison, and the `docs/COST_CALIBRATION.md` row | after grading |

**The grading path is fixed at commit I-1** (standing rule 2). Before grading, the
four instruments are hashed against their committed blobs to verify the frozen
files **are** the files that ran; the comparator refuses on any mismatch.

**Commits use the private-index protocol** of standing rule 10 — never a bare
`git commit`, never `git add -A` or `git add .`, never the shared index, HEAD
captured **once** per shell invocation for `read-tree`, the assertion and `-p`,
the commit sha asserted against a sha regex **before** `update-ref` and HEAD
asserted moved **after** (L-382, the empty-sha CAS trap), and the post-commit
`git diff HEAD~1 HEAD --stat` verify, which is not optional (L-223). Docket and
lesson numbers are re-derived from the **tail** at commit time — the **maximum
existing number**, never a count (standing rule 11) — and
`scripts/check_docket_reconciliation.py` runs **before** the docket is edited.

**Estimate-versus-actual calibration is owed at completion** (standing rule 12,
Sanaa's 2026-08-23 directive). The row in `docs/COST_CALIBRATION.md` states the
registered estimate (`12.0` core-min), the actual in core-minutes from the birth
run's own `wall_seconds`, the **ratio actual/predicted**, the gap attributed to
contention / misprediction / waste with **waste separately named and never
absorbed into the ratio**, and the dollar figure **derived at `$0.0513/core-h` and
labelled derived, not measured**. It carries the instrument-build and solve
components on **separate lines** (§7.2). **A completion report without that
comparison is incomplete and the lane is not done.**

**Nothing is sent.** No submission, no upload, no registration, no post, no
comment (standing rule 7). **Bulk data is not committed**; it lives at
`/home/ubuntu/closure-data/r4b_instruments/` and its paths are listed in the
results record.

---

## 10. DEPARTURES

**Empty at freeze. Nothing has been run.**

*(Departures are appended here, each dated, each with the measurement that forced
it, at the time it happens — never in a later addendum, which is the shape R4
recorded as its D-14.)*

---

## 11. THE AMENDMENT RULE, AND THE PRE-COMPUTE CONDITION

**Before first compute**, an amendment to this file is legal and **must state the
condition and how it was checked** — naming the run directory that does not exist,
with the `test -e` reading and its timestamp (standing rule 2;
`VERIFICATION_CHARTER.md` §2b). The version is bumped and the amendment is appended
**at the foot** with `lines whose number changed above this section: 0`.

**The pre-compute condition for this item, checked and timestamped:**
`/home/ubuntu/closure-data/r4b_instruments/` does **not exist** — `test -e`
returned **rc = 1** at **2026-08-28T17:20:38Z** — and holds **0.0 core-minutes**.
`/home/ubuntu/closure-data/r4b/` also does not exist (`test -e` rc = 1, same
timestamp), and this item must leave it that way (§3.3).

**After first compute, gates are closed.** Changes land only as dated addenda that
cannot alter a gate, a threshold, a cap or a label; originals are struck, never
rewritten (standing rule 6).

---

## 12. WHAT THIS REGISTRATION CANNOT SEE, AND WHAT IS NOT A LANE'S TO DECIDE

**Cannot see:**
1. **Whether the four instruments are writable as specified.** R4b §3.4, §3.5, §5
   and §9 specify them; no line of any of them exists. A specification that reads
   cleanly can still be unimplementable, and §5.7 registers that outcome as a
   finding rather than a licence to lower a bar.
2. **How many development iterations the birth demonstrations will take.** The ×3
   multiplier in §7.3 is a registered assumption, not a measurement, and it is the
   single largest source of cost risk in this item.
3. **Whether `run_r4b.sh` can drive `simpleFoam`** — §5 B5's registered limitation.
4. **The `MaxRSS` of anything** — §8.
5. **Whether R4b's own gates will ever fire**, since the increment is not directed.

**Not a lane's to decide — referred, with the owner named:**

| decision | owner | why it is not a lane's |
|---|---|---|
| **Whether `A′` is the R4b increment at all** | **Sanaa** | R4b §0.2 concedes it is the lab's ranking, not her choice; `docs/LAB_STATE.md:2619`, `:2844` record it as still on her desk. Registering the solve as a build step would launder a blocked decision into a task. |
| **Whether `select_control.py`'s demonstration `MODEL.json` may be promoted to R4b's registered model**, or must be re-run under R4b's own freeze | **the closure supervisor** | it is a question about what a freeze means, not about arithmetic. §4.3 registers the conservative answer (re-run) so the item is safe either way. |
| **Whether this item's `GATE REACHED` is sufficient to file R4b's queue entry**, or whether Sanaa's direction must land first | **the closure supervisor**, escalating to **Sanaa** | §1's split says the solve is `BLOCKED`; whether a born instrument set changes that is a supervision call. |
| **Freezing this file** — check 4 | **the closure supervisor, personally** | `SUPERVISION_CHARTER.md` §3; a relayed check is a summary, not a check, and this lane has not performed it and does not claim to. |

---

## 13. FILES

| file | role |
|---|---|
| `INSTRUMENT_BUILD_PREREGISTRATION.md` | **this document** — the registration of the instrument build |
| `PREREGISTRATION.md` | R4b's **solve** registration, untracked, `NO COMPUTE AUTHORISED`, **not edited by this item** |
| `QUEUE_ENTRY_DRAFT.json` | this item's queue entry, unvalidatable until the supervisor freezes and until the four instruments exist |
| `select_control.py` | to be written (A1); computes `xi*` by R4b §3.4 |
| `build_r4b_cases.py` | to be written (A3); builds the 12 cases, enforces R4b §3.5's freeze order |
| `run_r4b.sh` | to be written (A5); drives them |
| `grade_r4b.py` | to be written (A7); the comparator, and it may not grade until born |
| `COVERAGE.md` | to be regenerated (A0) by the frozen `make_coverage.py`, unmodified |
| `artefacts/r4b_instrument_birth.json` | the birth record `grade_r4b.py` reads and verifies before it grades anything |

---

*Drafted 2026-08-28 by a closure lab-lane. Zero compute spent. Not committed, not
filed, not enqueued. `SUPERVISION_CHARTER.md` §3 check 4 has NOT been performed on
this document by anyone, and this lane is not entitled to perform it.*
