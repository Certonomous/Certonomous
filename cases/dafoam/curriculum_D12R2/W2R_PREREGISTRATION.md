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
