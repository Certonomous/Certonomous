# CURRICULUM SO-3D-R — THE SUCCESSOR TO SO-3D, BECAUSE ITS PLANT-B WAS DEGENERATE ON ITS OWN ANCHORS. PRE-REGISTRATION, STAGE 1 (FROZEN)

**Version 1.0. FROZEN.** Dated **2026-09-03**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.

**Nothing in this item is filed, sent, emailed, uploaded, registered, posted or commented outside this box, now or on completion** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

**NOT LAUNCHED. NOT ENQUEUED. ZERO SOLVER CORE-MINUTES HAVE BEEN SPENT BY THE LANE THAT WROTE IT.** This document is a `CLAUDE.md` rule-2 freeze. The pre-compute gate is the `dafoam-supervisor`'s personal check (`SUPERVISION_CHARTER.md` §3 check 4) and is **not** discharged here. Check 1 on the changed scoring is likewise his.

**Every decision below is `[lab-attributed]`.** `CLAUDE.md` rule 9: no agent message is Sanaa's consent.

**Why this is a bespoke frozen document and not the 10-line template form.** Sanaa's template-speed prereg is for **standard** cases. This item is neither standard nor uncontested: it exists because a **frozen registration contained a control that could not discriminate**, and the successor's whole evidentiary content is the argument for why one scoring level is degenerate and another is not. That argument cannot be carried by a template, and it is the thing a reader must be able to check.

---

## 0. THE NAME

> **ID-NAMESPACE CHECK, run rather than recalled, 2026-09-03T21:0Z.** `git grep -lE 'SO3DR|SO-3DR'` over `cases/`, `docs/`, `verification/` and `scripts/` returned **0** files. `cases/dafoam/ladder-a/A2/curriculum_SO3DR` **ABSENT**. `/home/ubuntu/certonomous-runs/CURRICULUM-SO3DR-a2-wing-multipoint-rootcause` **ABSENT**. `verification/queue/` carried **0** rows matching `so3dr`. **0** containers matching `so3dr`.

`R` is this lab's standing suffix for a rerun of a named item — `SO1aR`, `SO1bR`, `SO2MR`, `SO3aR`, `D6R`, `D12R`, `D19R`. **`SO3DR` = SO-3D, re-run.** It does not mint a new ladder letter and does not spend a name Sanaa assigned to something else.

---

## 1. WHY THIS ITEM EXISTS — THE FINDING, WHICH IS ABOUT A FROZEN DOCUMENT AND NOT ABOUT AN INSTRUMENT

**SO-3D ran on 2026-09-03 and returned `NOT A RESULT`** (`../curriculum_SO3D/RESULTS.md`, `STATUS.SO3D`, rc=2, 0.0392 core-min). Its plant control refused at PLANT-B and, by §6 ordering rule 1, every other gate was `NOT A RESULT`. That verdict stands and is not reopened by this document.

**The first account of the refusal was incomplete, and the second half is the finding.**

SO-3D's PLANT-B acceptance predicate demanded that the plant's two anchors fall in **two distinct scenarios**. `curriculum_SO3D/PREREGISTRATION.md` §7 (frozen line 146) does not require that:

> *"The per-scenario failure counts move by **exactly −1** in the scenario owning the deleted banner and **exactly +1** in the scenario owning the inserted one, and the total is unchanged at **671**. Any other movement refuses."*

**Both anchors are owned by `cl04`** — measured: the delete site (line 200205) sits in record 200024–200292 at AoA 0.9304417657, the insert site (line 100261) in record 100085–100355 at AoA 0.5780466691, and both attribute to `cl04`. So the frozen expectation reads *"−1 in cl04 and +1 in cl04"*, which **nets to zero in every scenario**. **A reader implementing the freeze literally would have PASSED.**

### ⚠ AND THAT PASS WOULD HAVE BEEN VACUOUS. THE DEGENERACY, MEASURED

| reader | per-scenario move | total |
|---|---|---|
| **correct attributor** | `{cl04: 0, cl05: 0, cl06: 0}` | 671 → 671 |
| **totally blind** — attributes no banner to any scenario | `{cl04: 0, cl05: 0, cl06: 0}` | 671 → 671 |

**Byte-for-byte identical.** Counting banners needs no attribution, so the total is unchanged either way, and a blind reader's per-scenario vector is all zeros before and after. **On the anchors the freeze deterministically selects, PLANT-B cannot distinguish a correct attributor from a reader that attributes nothing** — and because the anchors are content-addressed (*first* banner at or after line 200000, *first* `End` at or after line 100000) it is that way **in every possible invocation, forever**.

**Both halves of the account are true and neither cancels the other.** The lane wrote a predicate stricter than the freeze — a real divergence and a real defect, and the lane's. **That divergence is the only reason a vacuous control did not quietly pass.** A defect that fails safe is still a defect; a rescue that came from a defect is still a rescue.

**This is the ninth unsatisfiable-by-construction condition this family has met, and the first in a FROZEN REGISTRATION rather than in an instrument.** That is a harder class, because a frozen document cannot be repaired — only succeeded. Hence this item.

**Named ancestor.** It is the family's own S-40 lesson from the other side — *a control that happens to test the one symbol the defect preserves is worse than no control* — here as a control whose **passing signature is indistinguishable from total blindness**.

---

## 2. WHAT CHANGES, AND WHAT MAY NOT

**SUCCESSOR, NOT AMENDMENT.** SO-3D has had first compute, so `CLAUDE.md` rule 2 closes its gates. **`../curriculum_SO3D/so3d_replay.py` is NOT edited, NOT moved and NOT re-pinned** — re-hashed at freeze and still `60af48e4e3debb536141eb3f5c66409b`, 1000 lines, the value SO-3D's AMENDMENT 1 pinned. This item stages its **own** copy with a new pin. Precedent: D6 → D6R → D6RF → D6RF2; A1WR → A1WRT.

### 2.1 The one substantive change

> **PLANT-B IS SCORED AT THE RECORD LEVEL, KEYED ON A SHIFT-INVARIANT RECORD ORDINAL. The per-scenario vector is COMPUTED AND REPORTED BESIDE IT, AND IS NEVER WHAT IS SCORED.**

**This is not "finer". It is what makes the control non-degenerate**, and that is the argument:

| reader | record-level signature | can it name the owning scenarios? |
|---|---|---|
| correct attributor | `{ordinal 368: +1, ordinal 739: −1}` | **yes — `cl04`, `cl04`** |
| totally blind | the same two ordinal deltas | **NO — it can name none** |

Ordinals need no attribution, so a blind reader still sees the deltas. **The clause a blind reader fails is the requirement that BOTH owning scenarios be NAMED.** Registered predicate, in full: *exactly one record ordinal at −1, exactly one at +1, no other record moving, **both owning scenarios named**, and the total unchanged at 671.*

**Why the key is the ordinal and not the line number.** PLANT-B deletes one line and inserts one line, so **absolute line numbers shift between the unplanted and planted copies**. SO-3D's per-record view was keyed on `start_line` and would have compared two *different* records. The ordinal — the k-th `^Time = 1$` in file order — is invariant, because the plant inserts and deletes only a `Primal solution failed!` line, matching neither `^Time = 1$` nor `Running Primal Solver`. **Measured: 977 records before, 977 after, ordinals stable, and `start_line` moved for a non-zero number of records** — the last fact is what disqualifies the obvious key. `Running Primal Solver NNN` is carried **beside** the ordinal as a corroborating label and is deliberately **not** the key: measured, 977 records carry only **773 distinct ids**, so it is not unique. A drift in that label across the plant **refuses**.

### 2.2 Two disclosure repairs

1. **The plant report is written INCREMENTALLY**, so each control's outcome is a fact on disk. SO-3D wrote its report only after all three plants passed, so when it refused at PLANT-B, PLANT-A's pass survived nowhere and had to be **deduced from source ordering** — evidence of a weaker kind. A plant not yet reached is written as **`NOT RUN`**, never absent and never `PASS`.
2. **The refusal and BLOCKED paths write their artifact into the RUN ROOT as well as the case directory.** SO-3D created its run root and left it empty, so a reader arriving there could not tell a refusal from a run that never started.

### 2.3 ⚠ WHAT MAY NOT CHANGE — THE ANCHORS, ABSOLUTELY

> **`PLANT_A_FROM_LINE = 200000`, `PLANT_B_DELETE_FROM_LINE = 200000`, `PLANT_B_INSERT_AFTER_END_FROM_LINE = 100000`, `PLANT_C_FROM_LINE = 150000` ARE CARRIED ACROSS UNCHANGED AND MAY NOT BE MOVED.**

Re-selecting them so the plant lands in two different scenarios would be **tuning the experiment until the control passes** — choosing the plant site to fit the answer, the same family as choosing a threshold to fit a result. What changes is the **scoring level**, which is the thing the predecessor's freeze under-specified. Also carried across unchanged: **every gate, threshold, prediction, plant definition, cap and label** — §5 P1–P4, §6's five gates, §7's three plant definitions, §8's null criterion, §11's 12 core-min cap and 0.0 solver cap, and the AoA attribution rule and G-SO3D-1 in-scope whitelist registered in SO-3D's AMENDMENT 1.

---

## 3. THE GATES — IDENTICAL TO SO-3D, RESTATED SO THIS DOCUMENT STANDS ALONE

| gate | question | artifact | PASS | GATE FAIL |
|---|---|---|---|---|
| **G-SO3D-P** | **PLANT CONTROL.** Does the reader see deliberately planted failures? | `so3dr_plant_report.json` | all three plants detected exactly as registered | any plant missed or mis-located |
| **G-SO3D-1** | channel: value or flag? | `so3dr_replay.json` → `nonfinite_census` | P1 holds (in-scope count == 0) ⇒ H1 stands | count ≥ 1 ⇒ H1 refuted, H6 revived; names file, line and token |
| **G-SO3D-2** | dose-response in CL target | → `per_scenario` | P2 holds (strict monotone) | not monotone ⇒ H2 refuted |
| **G-SO3D-3** | multipoint-specific vs case-specific | → `per_scenario`, `controls` | P3 holds (`min(r) ≥ 0.1111`) | `min(r) < 0.1111` |
| **G-SO3D-4** | single-scenario poisoning of the sum | → `cutback_coupling` | P4 holds (≥ 0.90) | < 0.90 |

**Ordering, unchanged and not negotiable.** G-SO3D-P is scored **first**; if it does not PASS the reader **exits 2** and every other gate is **`NOT A RESULT`**. A missing or truncated log is **`NOT A RESULT`, never a zero**. `NOT A RESULT` can only replace a `PASS` or a `GATE FAIL`, never the reverse.

**§8's null criterion is carried unchanged**, including its second path: *if the plant control fails, the rung is `NOT A RESULT` in its entirety and the reader itself is the finding.* **No remedy is proposed by this document.**

---

## 4. THE GATE WALK — WHAT MAKES EACH FIRE AND WHAT MAKES IT REFUSE

**Every line below was driven by execution in `so3dr_replay_selftest.py`, in both directions, under both interpreters.**

| gate / guard | FIRES when | REFUSES / NOT A RESULT when |
|---|---|---|
| **PLANT-A** | census moves +1 exactly, at the planted line → PASS | any other delta or location → exit 2 (driven by blinding the census whitelist) |
| **PLANT-B** *(the change)* | exactly one ordinal +1, one −1, no other record moves, **both owners named**, total 671 → PASS — **including when both owners are the SAME scenario**, which is where SO-3D refused | owners cannot be named → exit 2 (driven by an attributor that names nothing); record count changes across the plant → exit 2; `Running Primal Solver` labels drift → exit 2; wrong total → exit 2 |
| **PLANT-C** | exactly one record flips failed→converged, and it is the target → PASS | no flip or a second record moves → exit 2 (driven by blinding the tolerance reader) |
| **G-SO3D-1** | in-scope count 0 → PASS; ≥ 1 → GATE FAIL naming file, line, token | window asserted against the file's own length |
| **G-SO3D-2 / -3** | monotone / `min(r) ≥ 0.1111` → PASS, else GATE FAIL | **NOT A RESULT** if any scenario has zero attributed starts — an undefined rate is not a rate that passes |
| **G-SO3D-4** | fraction ≥ 0.90 → PASS, else GATE FAIL | **NOT A RESULT** on zero cutbacks — 0/0 is never 1.0 |
| **log integrity** | four logs present, non-empty, sha256 recorded | absent or 0-byte → NOT A RESULT, never a zero |
| **run-root guard** | root absent → proceeds | root present → refuses; archive by `mv`, never delete |
| **originals untouched** | sha256 unchanged after the plant pass | any original moved → NOT A RESULT |
| **cost cap** | 12 core-min reached → **BLOCKED**, exit 3, nothing below it scored | — |
| **solver cap** | 0 solver core-min by construction — no container, no MPI job, no OpenFOAM process | any solver launch under this id is out of registration |

**THE CAP IS NOT SHORT.** SO-3D measured a full pass — read, census, record parse, coupling, sha256 — over the 222,223-line D6 log at **0.49 s wall at ranks 1**, and its own aborted invocation spent **0.0392 core-min** reaching PLANT-B on the 264,607-line D6R log. The cap is **720 wall s**. It can fire — both directions are driven — but it is not expected to bind.

**⚠ AND THE 6 core-min POINT ESTIMATE IS CARRIED FORWARD KNOWN-HIGH.** SO-3D's calibration row (`C-20260903T210144.295494Z-75297022`) attributes a ~153× over-prediction to misprediction. **The estimate is NOT revised here**, because a successor that quietly re-costs its predecessor's registration loses the comparison the calibration ledger exists to make. It is carried **unchanged and flagged**, and this item's completion row will state the ratio against it and against SO-3D's partial actual.

---

## 5. NO `assert` CARRIES ANYTHING, AND THE GUARDS ARE DRIVEN UNDER BOTH INTERPRETERS

**Neither `so3dr_replay.py` nor `so3dr_replay_selftest.py` contains a single `assert` statement** — proved by counting `ast.Assert` nodes in both parse trees, not by grepping.

| interpreter | `__debug__` | controls | PASS | FAIL | NOT RUN |
|---|---|---|---|---|---|
| `python3` | `True` | **54** | **54** | 0 | **0** |
| `python3 -O` | `False` | **54** | **54** | 0 | **0** |

Verdict columns **byte-identical**, diffed by execution; the `__debug__` line differs, so the two are demonstrably different interpreters. Capture: `so3dr_replay_selftest_evidence.txt`.

**Eight of the 54 controls are new and exist only for this successor**, including the two that carry its argument:

- **`DEGENERACY-PROOF`** — evaluates the predecessor's **literally frozen** per-scenario expectation for a correct reader and for a totally blind one on the same bytes, and passes only if the two are **indistinguishable**. It proves the finding of §1 rather than asserting it.
- **`PLANTB-BLIND`** — the successor's record-level predicate **does** separate them: a reader that can name no owning scenario refuses, even though it still sees both ordinal deltas.
- `PLANTB-SAMESCEN`, `PLANTB-COUNT`, `PLANTB-RPSDRIFT`, `PLANT-INCREMENTAL`, `NOTRUN-NOT-PASS`, `ORDINAL-INVARIANT`.

---

## 6. TWO DEFECTS THE SELFTEST FOUND IN THIS SUCCESSOR, BOTH THE LANE'S OWN

Recorded because a guard suite that never caught anything is not evidence the instrument is sound.

1. **A control that was passing FOR THE WRONG REASON.** The blind-reader controls simulated blindness by squeezing `AOA_MATCH_ABS_TOL` to `1e-30`. In the synthetic fixture the AoA is printed **identically** on both sides, so the gap is exactly `0.0` and **no tolerance can exclude it** — the reader was never blinded. The inherited `GATE-P-ATTRIB` control was therefore refusing because its insertion anchor landed in the **PRETRIM** record, not because attribution was broken. Blinding is now explicit: `attribute_aoa` is replaced by one that names nothing. **A control that passes for a reason other than the one it claims is a control that is not testing what it says.**
2. **A guarantee that lived in the caller.** The `NOT RUN` filling of unreached plants was done in `main`'s emitter, so any *other* caller received a snapshot with plants simply **absent** — and an absent plant reads as nothing rather than as `NOT RUN`. It now lives inside `score_plant_control`'s own flush. **A guarantee that depends on the caller is not a guarantee.** Caught by this file's own `PLANT-INCREMENTAL` control.

---

## 7. COST, CAP AND STOP RULE (`CLAUDE.md` rule 12)

**Stage 1 buys ZERO solver core-minutes.** No container, no MPI job, no OpenFOAM process. Single-process host post-processing over four log files, `np = 1`.

| field | value |
|---|---|
| unit | **core-minutes** = wall s × ranks ÷ 60 |
| ranks | **1** (host post-processing; **no container, no queue entry**) |
| **predicted cost** | **6 core-min** point, **3–10** bracket — **CARRIED FORWARD UNCHANGED AND KNOWN-HIGH** from SO-3D §11, deliberately not revised (§4). **A PREDICTION, NOT A MEASUREMENT.** |
| **registered cap** | **12 core-min** |
| **stop rule** | at 12 core-min the reader **stops**; an overrun does not receive a new budget. A rung stopped at the cap is **`BLOCKED`** on cost, **not** `GATE FAIL`, and no gate below it is scored |
| solver core-min | **0**, capped at **0**. Any solver launch under this item id is out of registration |
| **cost basis** | **MEASURED at completion** — wall seconds × 1 rank ÷ 60, captured **inside** the detached wrapper (`setsid` returns 0 for every outcome of what it wraps), recorded in `STATUS.SO3DR` and `so3dr_replay.json` |
| dollars | **DERIVED, NOT MEASURED, REPORTED-BY-OWNER.** At $0.0513/core-h (owner-stated 2026-08-21/22): 12 core-min cap = **$0.01026**. The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| pre-authorisation | under $25, inside the standing pre-authorisation. **A blanket is not a per-item read** (rule 9): the item is costed here on its own terms |
| **rule-12 calibration** | on completion, predicted against measured with the ratio and its attribution, as a row in `docs/COST_CALIBRATION.md`, **naming SO-3D's row as the one it continues**. A completion report without it is incomplete |

---

## 8. THE GRADING PATH

| file | role | md5 | lines |
|---|---|---|---|
| `so3dr_replay.py` | **the reader** — the grading path | `007328fe6777b23d6d81a1a7e8fedcd0` | **1136** |
| `so3dr_replay_selftest.py` | guard suite, 54 controls, both directions | `a05557a21e3fea28de1b08ab43832738` | **904** |
| `so3dr_run_replay.sh` | launcher: hashes the reader against its committed blob, then invokes it, rc captured **inside** | `33eb3b814c54efaf7f7ae8cdb20ad081` | **98** |
| `so3dr_replay_DELTAS_from_so3d.diff` | the successor's every departure from the predecessor, as a diff | — | 357 |
| `so3dr_replay_selftest_evidence.txt` | both interpreters' capture | — | 134 |

**Frozen artifact names**, fixed now so a later file cannot be substituted: `so3dr_replay.py`, `so3dr_replay.json`, `so3dr_plant_report.json`, `RESULTS.md`. All under this case directory. **No repository document produced by this item may cite a scratchpad path** (`CLAUDE.md` rule 13).

**The reader is committed WITH this freeze**, so the §12-shaped gap SO-3D carried does not recur: there is no pre-compute condition left open, and the launcher verifies the frozen file **is** the file that ran by hashing it against its committed blob before invoking it.

> **RUN ROOT CHECKED BY EXECUTION, 2026-09-03, in the freezing invocation:** `/home/ubuntu/certonomous-runs/CURRICULUM-SO3DR-a2-wing-multipoint-rootcause` — **ABSENT**. `verification/queue/` — **0** rows matching `so3dr`. **0** containers. `so3dr_replay.json`, `so3dr_plant_report.json`, `RESULTS.md` — **all ABSENT**. **No compute has occurred under this item.**

---

## 9. WHAT IS NOT FROZEN HERE, AND WHAT THIS ITEM DOES NOT CLAIM

- **Stage 2** (the instrumented per-trial-point probe carrying the mesh-quality trace Stage 1 provably cannot supply) and **Stage 3** (the incompressible transfer test) remain **unfrozen**, exactly as SO-3D §10 left them.
- **No remedy at all** is registered, proposed or implied: no tolerance change, no solver change, no `max_iter` change, no restart strategy, no multipoint reformulation.
- **SO-3D's verdict is not reopened.** `NOT A RESULT` stands as SO-3D's verdict, and this item does not re-grade, convert or edit it.
- **It establishes nothing about the multipoint pathology** until it runs. H1–H7 stand exactly where SO-3D §4 left them.
- **Toolchain row** (`DAFOAM_CHARTER.md` §6): every log replayed here was produced on the **PATCHED** row — image `dafoam-idwarp-rot:v1`, digest `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`, `IDWARP_SO_MD5 85f59e87253e0a71a813f64ca6e4c425`. **There is no shipped row for the multipoint pathology and this rung does not manufacture one.**

## 10. FREEZE STATEMENT

This document is **FROZEN** at the commit that introduces it, together with its reader. After first compute its gates are closed; anything further lands as a dated addendum that cannot alter a gate, threshold, cap or label, and originals are struck rather than rewritten.

**FREEZE ONLY. NOT ENQUEUED. NO QUEUE ENTRY. NOT LAUNCHED. ZERO SOLVER CORE-MINUTES. SUBMISSIONS PARKED.**
