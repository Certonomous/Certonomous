# D12R2-W2R — THE CONTINGENCY-WINDOW EXPERIMENT, RE-REGISTERED AFTER W2 BLOCKED

**Version 1.0. FROZEN.** Dated **2026-08-26**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

> **THE PREDICTIONS ARE NOT RE-DERIVED. `P1`–`P4` ARE CITED UNCHANGED FROM `W2_PREREGISTRATION.md`
> §3.2, FROZEN AT `90edbf27`.** W2 produced **zero graded output**, so there is nothing new to
> derive them from — and re-deriving a prediction after a failed attempt is how a prediction stops
> being one. **This document changes the LAUNCHER and nothing else.**

---

## 1. W2 = `BLOCKED`, AND WHAT IT COST

Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2-cylinder-unsteady`, stamp
`20260826T044529Z_3246133`, **preserved byte-for-byte as evidence and not deleted.**

**3 stages completed clean** (S0 mesh `nCells=2450`, S1a, S1b — all `rc=0`), **1.2 core-min spent**,
then at S2a:

    AGGREGATE_MEMORY_CAP peers=24.0 GiB + mine=8 GiB = 32.0 GiB vs physical 30.6440 GiB
    REFUSE: AGGREGATE memory caps 32.0 GiB EXCEED physical 30.6440 GiB.
    STAGE=S2a BLOCKED by the aggregate cap assert -- NOT LAUNCHED
    ABORT: S2a has no t=3.0 directory for FIELD_B

**A SECOND peer container appeared** — peers went `12.0 → 24.0` GiB — and the guard registered
hours earlier **refused, exactly as designed.** The first two stages record `peers=12.0`; the third
records `24.0`. **The guard was right and the run is `BLOCKED`.**

## 2. THE TWO DEFECTS THIS RE-REGISTRATION CARRIES

### 2.1 `W2-DEF-1` — **THE GUARD REINTRODUCED THE DEFECT IT WAS WRITTEN TO ANSWER**

The aggregate guard wrote a **ledger line and no manifest row**: 4 `STAGE=` lines against 3 rows.

> **THAT IS `D12R2-DEF-2` EXACTLY — a stage that ran and left no row — REINTRODUCED BY THE REPAIR
> WRITTEN TO SATISFY THE RULING THAT AROSE FROM `D12R2-DEF-2`.** Written, demonstrated, committed
> and fired in production **inside two hours.**

**AND THE GATE BUILT FOR THAT CLASS CAUGHT IT, ON THE FIRST RUN, BY NAME:**

    G12R-0b -> REFUSAL: the manifest and the ledger DISAGREE about which stages ran.
    In the ledger but NOT the manifest: S2a. manifest=3 rows, ledger=4 STAGE= lines.
    A stage that ran and left no row is UNGRADED AND SILENT.

**The cause is one line.** `d12y_w2_stage_and_run.sh:298` returns `9` **before** the blocked-row
write, while the **pre-existing** `MemAvailable` block two lines below **always got this right**
(`:301` writes `{"name":…,"blocked":true,…}` before returning `8`). **The new guard did not copy
the old one.**

> **THE LESSON, AND IT IS NOT THE ONE I EXPECTED TO LEARN TODAY: A GUARD THAT REFUSES MUST LEAVE
> THE SAME TRACE IN BOTH ARTIFACTS, OR IT MANUFACTURES THE SILENCE IT EXISTS TO PREVENT.** Knowing
> a defect class by name, having just written the gate for it, and having demonstrated that gate
> against thirteen scenarios, **was not sufficient to stop me writing a fresh instance of it.**

**HONEST BOUNDING OF THE IMPACT, because it would be easy to overstate:** no verdict was ever at
risk. `G12R-0b` refuses a 3-row manifest on the **registered count of 33** regardless of the
name mismatch, and `plan()` filters `blocked` rows before the binding gate. **The defect degraded
the DIAGNOSTIC, not the verdict** — but the diagnostic is precisely what makes a partial run
legible, which is why it is repaired rather than noted.

### 2.2 `W2-DEF-2` — **THE GUARD THREW AWAY A TWO-HOUR RUN OVER A SIXTY-SECOND CONDITION**

The second peer container **no longer exists**; the box is back to `peers=12.0` GiB. **A transient
condition discarded a run priced at 121.35 core-min after 1.2 had been spent.**

> **REFUSING TO LAUNCH INTO AN OVER-COMMITTED BOX IS CORRECT AND IS NOT WEAKENED HERE. Discarding
> the run rather than waiting for the condition to clear is a separate decision, and it was the
> wrong one.**

## 3. THE REGISTERED CHANGES — TWO, AND ONLY TWO

| # | change | why it does not weaken the guard |
|---|---|---|
| **1** | the aggregate guard **writes a `blocked` manifest row before returning**, carrying `"blocked_by":"aggregate_cap"` | it adds a record; it changes no threshold |
| **2** | the guard **waits, bounded, for the condition to clear** — `AGG_WAIT_MAX_S = 1200` (20 min), `AGG_WAIT_POLL_S = 30`, both **registered** — and **BLOCKS if it does not** | **it never launches into an over-committed box.** The refusal threshold (`Σ caps ≤ MemTotal`) is **byte-identical**. A genuinely over-subscribed box still **BLOCKS** rather than hanging, because the wait is bounded. |

**BOTH ARE DEMONSTRATED AGAINST THE LIVE BOX, BEFORE THIS DOCUMENT WAS FROZEN:**

- **Leg 1** — at the registered 8 GiB cap: **CLEARS immediately**, no wait.
- **Leg 2** — planted at 20 GiB with a 10 s bounded wait: **polls, then BLOCKS** at the limit.
  It neither launched nor hung.
- **Leg 3** — planted refusal: the manifest row **IS** written —
  `{"name":"S2a","blocked":true,"blocked_by":"aggregate_cap","memavail_GiB":17.0}`.

**A guard shown able to pass, to wait, and to refuse is a guard; one shown only to refuse is not.**

## 4. UNCHANGED, AND DELIBERATELY SO

**`P1`–`P4` and the falsifier, cited verbatim from `90edbf27` §3.2–§3.3, NOT re-derived:**

| # | prediction | value |
|---|---|---|
| **P1** | W2R's S2b is bit-identical, so `δ_window(900)` reproduces exactly | **`9.879556064e-04`** |
| **P2** | `\|g\|` at `W = 900` | **`1.0304158599180422` ± 30 %** |
| **P3** | **PRIMARY, BINARY: `h_min(900) > h_max`, STILL NO ADMISSIBLE FD STEP** | `admissible: false` |
| **P4** | point `h_min(900)` | **`9.587931e-02`** (1.9176×), band `[7.375e-02, 1.370e-01]` |

> **P3 IS FALSIFIED IF AND ONLY IF `|g|` AT `W = 900` EXCEEDS `1.9759`.**

Also unchanged: `W_STEPS = 900` (**registered at `f9c8b9c8`, before any of this data — §2 of the
W2 document on why it is not a chosen window**), `MEM_LIMIT = 8g`, `CPUSET_CPUS = 12`,
`MEMAVAIL_FLOOR_GIB = 14.0` (**not lowered**), `CAP_CORE_MIN = 600.0`, S2b at **2400** samples
(the saturation result), and `EXPECTED_STAGE_ROWS_PHASE1 = 33`.

**THE COMPARATOR IS BYTE-UNCHANGED** — `d12y_grade.py` md5 `33f7a006e15dce2988a63b2e937cf07b`,
the same instrument that graded `W = 300` and that **caught `W2-DEF-1`**. `d12y_run_script.py`
md5 `2790c39a09cd458d5a3263d7f1811da5`, unchanged through four items.
`d12y_w2r_stage_and_run.sh` md5 `736aa849b4aa91c77d41b061bf4d10f9`; the W2 launcher is **CITED
AND UNEDITED**.

## 5. THE AMENDMENT CONDITION

> **`/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady` DOES NOT EXIST.**

**`test -e` returned false at 2026-08-26T04:51:04Z**, immediately before this document was written. The launcher
**refuses with exit 6** if it exists at phase 1. After the first container, gates are **CLOSED**.

## 6. COST

**121.35 core-min predicted, unchanged** — the stage graph and window are identical, so the W2
estimate carries over without re-derivation. Guard `CAP_CORE_MIN = 600.0`. Derived **$0.1038**,
**REPORTED-BY-OWNER, DERIVED, NOT MEASURED**.

**W2's 1.2 core-min is WASTE**, named separately (`COMPUTE_BUDGET_CHARTER.md` §6) and **never
absorbed into any ratio**. **$0.0010 derived.** **What it bought: `W2-DEF-1`, `W2-DEF-2`, and a
production demonstration that `G12R-0b` catches a silent stage on real artifacts it was not
rehearsed against.**

## 7. CARRIED FORWARD, AND NOT DROPPED

The `W = 300` results are **recorded, NOT imported**; a repeat is corroboration and a departure is
a finding. **`St ≈ 0.5273` from the re-measured period is a RESOLUTION ARTIFACT on a 2,450-cell
2D URANS mesh and is NEVER quoted as a Strouhal number** — reproducing the prior to −0.16 % makes
it a **reproducible artifact**, not a measurement. **No grid family, so rule 5 has no row and NO
GCI IS QUOTED.** **`G12R-6` runs only if `P3` MISSES**; if `P3` hits, no adjoint-versus-FD
comparison is bought.

---

## ADDENDUM 1 — 2026-08-26T16:31:46Z. `d12y_grade.py` `G12R-0b`: AN ABSENT LEDGER IS BOOKKEEPING, NOT A VOID — THE REGISTERED COUNT STILL REFUSES (Sanaa's universal rule, `d4d0c29d`, L-342)

**Version 1.1. This addendum ALTERS NO GATE, THRESHOLD, CAP OR LABEL. Lines whose number changed above this section: 0.** Approved as a pre-registered amendment by dafoam-supervisor, ruling [lab-attributed] 2026-08-26, condition **C4**, driven in the selftest under plain `python3` and `-O`. **Condition at this addendum:** W2R is RUNNING (`STATUS.W2R_phase2` in this directory; stages `d12y_S2b`/`S3*` live on cpu 12 today); **nothing has been graded** under either version.

### A1.1 What changes, and what does not

`G12R-0b` (`g0b_manifest_ledger_binding`) had FOUR refusals. **Three are unchanged**: a present ledger with zero `STAGE=` lines (rule 3 — the reader must be shown able to see a stage); a present ledger that DISAGREES with the manifest (the D12R2-DEF-2 / W2-DEF-1 catch); duplicate or nameless manifest rows. **One is split**: when the ledger — a host-side `tee -a`, `d12y_w2r_stage_and_run.sh:240` — is ABSENT:

| manifest rows vs `EXPECTED_STAGE_ROWS_PHASE1 = 33` (frozen) | before | now |
|---|---|---|
| **≠ 33** | REFUSE | **REFUSE** (C4: *"the registered-count check REMAINS A REFUSAL when the ledger is absent"*), citing both numbers |
| **= 33** | REFUSE | **`NOT_MEASURED`** for the binding limb only, `count_vs_registered: MATCH`, reason stated; the grade proceeds on the manifest's physics keys (`REQUIRED_ROW_KEYS`: `rc`, `oomkilled`, `end_line_present`, `last_time`, `endTime`, cold/age) and each stage's own log and JSON under `G12R-0` |

`memavail_GiB` was already tolerant of absence (refuses only when PRESENT and below the 14.0 floor) and is untouched.

### A1.2 Driven

`U-16d` now carries: **leg 3** — absent ledger, 33 rows → `verdict == NOT_MEASURED`, `count_vs_registered == MATCH`, `n_rows == 33`; **leg 3b** — absent ledger, 32 rows (S0 dropped) → REFUSES, and the refusal text cites **33** and **32**. Legs 2, 4, 5 unchanged. Selftest: **82 registered, 82 in the list, 82 returned a result, 0 failures**, identical under `-O`; `ast.Assert` **0**. Diff against the frozen blob `3a76c8283b30`: **37 insertions, 7 deletions**, hunks only in `g0b_manifest_ledger_binding` and `selftest`.

### A1.3 The struck line

**§4's "THE COMPARATOR IS BYTE-UNCHANGED — `d12y_grade.py` md5 `33f7a006e15dce2988a63b2e937cf07b`" is STRUCK, not rewritten.** At this addendum `d12y_grade.py` is md5 `02a9ab62fc26d963886ecd0ee97457ef`, blob `aecceb4e874eb6d306fb273d7408e762718c87a2`, and that is the grading path for W2R. `d12y_run_script.py` and `d12y_w2r_stage_and_run.sh` are unchanged.
