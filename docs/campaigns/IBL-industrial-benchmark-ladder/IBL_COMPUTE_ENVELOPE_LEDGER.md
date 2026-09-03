# IBL — COMPUTE ENVELOPE LEDGER

**The spend ledger for Sanaa's industrial benchmark ladder, Rungs 0–3. Envelope: $1,000.**

**THIS IS A LEDGER, NOT A REPORT. IT ACCUMULATES. NO AGENT REWRITES IT.**
A row, once written, is never edited. A correction is a **new row** carrying `corrects:` and the
id of the row it corrects, exactly as `docs/COST_CALIBRATION.md` does it. Rows are appended in
chronological order of the spend, never re-sorted.

**Authority.** Sanaa's [SANAA-DIRECT] of 2026-09-03 ~18:00Z,
`etc/sessions/2026-09-03T1800Z_sanaa_compute_envelope.md`, quoted verbatim:

> 1. The per-case dollar approval loop is abolished. I set one standing envelope: $1,000 for the
> benchmark ladder (Rungs 0–3), spendable without returning to me. Nothing inside it ever waits on
> a cost approval again.
> 2. What does not change: every run still registers its cost estimate before launch, still carries
> a hard per-run cap (set by the team at ~3× its own estimate, not by me), still reports
> predicted-vs-actual, and still names waste. **The estimate is an instrument, not a permission
> slip.**
> 3. Node sizing: rent the node the grid needs — CRM fine-grid class means 64–128 core spot
> instances; never crop a grid to a box. Saturation scheduling applies as always.
> 4. Escalation to me only for: a single run projected over $150, the envelope reaching 80%, or a
> rerun of something that already failed twice (the no-blind-retries rule at scale). However before
> escalating this to me check that you didn't make bugs/ errors in how you estimated this exceedance

---

## 1. THE THREE ESCALATION TRIGGERS, IN THE LAB'S OWN UNIT

Escalation goes to Sanaa and **only** for these three. Each is stated in core-minutes as well as
dollars so that no reader has to convert anything, and **each is preceded by the escalating agent's
own arithmetic self-check** — her explicit instruction, and it is aimed at the class of error that
registered a cost basis of `3.362e-06` when the measured value was `3.3560e-08`, because the
`ExecutionTime` prints were 100 iterations apart.

| trigger | dollars | core-minutes at the on-box rate |
|---|---|---|
| a single run **projected** over $150 | **$150** | **175,439 core-min** |
| the envelope reaching **80 %** | **$800** | **935,673 core-min** |
| a **third** attempt of something that already failed twice | — | — |
| *(the envelope itself, for scale)* | $1,000 | 1,169,591 core-min |

**THE SELF-CHECK IS PART OF THE TRIGGER, NOT A COURTESY.** Before any of the three is escalated,
the escalating agent re-derives the number **from the artifact, not from this ledger and not from a
board**, and states in the escalation which artifact it re-read. **An escalation built on an
un-rechecked exponent is worse than no escalation.**

---

## 2. THE RATE, AND WHY EVERY DOLLAR HERE SAYS `DERIVED`

**The unit is core-minutes.** Dollars are **DERIVED, NOT MEASURED** — rule 12 and
`COMPUTE_BUDGET_CHARTER.md` §5: **the box cannot read its own billing.** No dollar in this file is a
billing figure, and none may ever be described as one.

| rate | value | source | status |
|---|---|---|---|
| on-box `c7a.4xlarge` | **$0.0513 / core-h** | owner-stated 2026-08-21/22; corroborated at `Xiao2016_EnKF/PREREGISTRATION.md:197` | **citable** |
| any rented instance | — | **must be read from the console** | **`BLOCKED-ON-PRICE` until read** |

**NO RENTED PRICE MAY EVER BE QUOTED FROM RECALL** (rule 12, and board 47 says the same).

### 2.1 ⚠ A STRUCTURAL DEFECT IN THE ENVELOPE'S MEASURABILITY, SURFACED RATHER THAN PAPERED OVER

**The envelope is denominated in DOLLARS. Rented spend cannot be converted to dollars from this
box.** So a ledger that carried only a dollar column would report a **false low** running total
every time the ladder rented a node — and the 80 % trigger, which is the whole point of the ledger,
would silently fail to fire. **This is exactly the shape of a planted-zero failure (rule 3): a total
that reads low because the reader cannot see part of the population.**

**The fix, and it is why every row carries two totals.** A row whose rate is `BLOCKED-ON-PRICE`
contributes its **work** to the ledger immediately and its **dollars** are held. The running figures
are therefore always **two numbers**:

- **`SETTLED $`** — the cumulative derived dollars of every row whose rate is citable.
- **`UNPRICED BACKLOG`** — the work of every `BLOCKED-ON-PRICE` row, in instance-hours and
  core-hours, **not** converted.

**THE 80 % LINE IS READ OFF `SETTLED $` PLUS A STATED WORST CASE FOR THE BACKLOG, NEVER OFF
`SETTLED $` ALONE.** When a console price arrives, the backlog row is settled by a **new** row
carrying `corrects:`, never by editing the original.

---

## 3. ROW SCHEMA — every field, every row, no optional columns

| field | meaning |
|---|---|
| `id` | `E-<UTC timestamp>-<8 hex>`, allocated at append |
| `date_utc` | from `date -u` **on this box at append time**, never copied from a brief |
| `rung` / `branch` | `RUNG0` … `RUNG3`; branch label |
| `run_id` | the run directory the spend belongs to, absolute path |
| `work` | **core-minutes** (wall s × ranks ÷ 60) for on-box; **instance-hours × vCPU** and **instance-hours** for rentals |
| `rate` | the number used |
| `rate_source` | `on-box-owner-stated` \| `console-read` \| **`BLOCKED-ON-PRICE`** |
| `derived_usd` | **DERIVED, NOT MEASURED**; literally `BLOCKED-ON-PRICE` where the rate is |
| `estimate` | the pre-registered estimate for this run, in core-minutes |
| `cap` | the pre-registered hard cap (~3× the estimate) |
| `ratio` | actual / predicted |
| `waste` | **named separately, never absorbed into `ratio`** (`COMPUTE_BUDGET_CHARTER.md` §6). A row over 3,600 wall s is a **stall** |
| `SETTLED $` | **running cumulative** of settled derived dollars |
| `REMAINING of $1,000` | **carried in every row so the 80 % line needs no arithmetic from the reader** |
| `UNPRICED BACKLOG` | running instance-hours whose price is not yet read |
| `corrects` | id of the row this row corrects, or blank |

---

## 4. THE LEDGER

**Opening balance: $1,000.00. Rows begin below.**

| id | date_utc | rung / branch | run_id | work | rate | rate_source | derived_usd | est | cap | ratio | waste | **SETTLED $** | **REMAINING of $1,000** | UNPRICED BACKLOG | corrects |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| — | 2026-09-03 | — | *(opening balance — no spend)* | 0 core-min | — | — | $0.0000 | — | — | — | — | **$0.0000** | **$1,000.0000** | 0 instance-h | — |
| E-20260903T165248.577394Z-1964eadd | 2026-09-03 | **RUNG1** / `R1-M0` admission probe, on the branch-(a2) coarse level | `/home/ubuntu/Certonomous/verification/runs/RUNG1_M6_runs/M0_pyhyp_admission` (attempt 2, the run that produced the measurement); attempt 1 preserved at `.../M0_ATTEMPT1_ABORTED_missing_fvSchemes` | **1.1000 core-min** total charged = 0.1833 measured (attempt 2, 11 wall s × 1 rank ÷ 60) + 0.9167 waste (attempt 1, 55 wall s × 1 rank ÷ 60) | $0.0513 / core-h | `on-box-owner-stated` | **$0.0009405 DERIVED, NOT MEASURED** (attempt 2 alone $0.000157; waste $0.000784) | 2.0 core-min | 6.0 core-min | **0.092×** (0.1833 / 2.0) — waste is NOT absorbed into this ratio, per `COMPUTE_BUDGET_CHARTER.md` §6 | **0.9167 core-min = $0.000784 DERIVED.** Attempt 1's `checkMesh` aborted on a missing `system/fvSchemes` — a DRIVER defect of this lane's, not a mesh finding; the grid it built was valid and it produced no number. No stall: longest row 55 wall s against the 3,600-s rule | **$0.0009** | **$999.9991** | 0 instance-h | — |

> ~~**NO SPEND HAS BEEN CHARGED TO THIS ENVELOPE. The ladder has not launched.**~~
>
> **STRUCK 2026-09-03 by the row above, which is this envelope's first spend.** The original
> sentence is struck rather than deleted, per rule 6 — a superseded statement in a ledger is
> struck on its own face, never rewritten out of existence. **The ladder has launched: `R1-M0`
> ran at 16:50Z and charged 1.1000 core-min = $0.0009405 DERIVED.** The table row, not this
> prose, is the record.

*(Historical note, and deliberately NOT a row: `verification/runs/M6I_runs/` and
`verification/runs/M6S_runs/` were spent BEFORE this envelope existed — M6I R0's actual
**0.3833 core-min** is already calibrated at `docs/COST_CALIBRATION.md`
row `C-20260901T173329.123480Z-d483e031`. **Retro-charging pre-existing spend to a new envelope
would make the envelope's own baseline unauditable**, so it is not done, and this note exists so
that the absence is a decision on the record rather than an oversight.)*

---

## 5. THE TWO NODE-SIZING RULES — DIFFERENT JOBS, AND THEY MUST NOT BE AVERAGED

Sanaa ruled twice on the same day about renting, ~30 minutes apart, and **the two rulings are not in
conflict: they govern different job classes.** Written out here so no future lane has to re-derive
it, and so nobody splits the difference.

| job class | ruling | her words | why |
|---|---|---|---|
| **SERIAL CONVERTER / IMPORT** (`ugrid_to_foam.py`) | rent for **MEMORY**, at the **smallest core count that fits it** | *"do not rent 16 vCPU for a serial converter — take the smallest instance that fits memory. Parallelizing the converter is approved only if conversion becomes recurring; one-off imports don't justify it"* (~17:30Z) | the converter is **serial**. Cores it cannot use are the 94 %-waste finding: 16.4 core-min of work against ~263 billed |
| **FINE-GRID SOLVE** (CRM class and up) | rent for **CORES**, **64–128 core spot instances** | *"rent the node the grid needs — CRM fine-grid class means 64–128 core spot instances; never crop a grid to a box"* (~18:00Z) | the **grid** sets the requirement, and a solve uses every core |

**Rentals draw from THIS envelope. There is not a second ledger.**

### 5.1 What "never crop a grid to a box" retires, and what it does not

Board 47 recorded *"on-box gate stays 10 Mcells"* and *"DPW5 L4.F hybrid at 80.99 Mcells cannot be
imported here at all."*

> **Both remain TRUE AS FACTS ABOUT THIS BOX. Both are RETIRED AS LIMITS ON AMBITION.**
> A grid is never reduced to fit this machine. Any estimate that used the 10-Mcell ceiling as a
> *scope constraint* is re-derived without it; any estimate that used it as a *statement about
> where a job can run* stands.

**Measured memory basis for sizing an import rental** (re-verified from the three converter rows in
`cases/committee-grids/measurements.jsonl`, `sum_vmhwm_mib` 1013.8 / 1166.9 / 2519.3 at 0.638976 /
1.277952 / 2.981888 Mcell): **≈ 467 MiB + 674 MiB/Mcell**, against board 47's four-grid
**495 + 632**. Agreement ~7 %; **this is a re-verification on three of four points — the fourth was
not located** — so the **larger** slope is used for sizing. **Solver memory is a different quantity
and this model must NOT be transplanted to it.**

---

## 6. WHAT THIS LEDGER DOES NOT DO

1. **It is not an approval instrument.** Sanaa abolished the per-case approval loop. Nothing inside
   the envelope waits on anyone. **The estimate is an instrument, not a permission slip.**
2. **It does not replace `docs/COST_CALIBRATION.md`.** That ledger answers *was our estimate any
   good?* (rule 12's estimate-versus-actual, filed at every process completion). This one answers
   *how much of the $1,000 is left?* **A completed rung files a row in BOTH.**
3. **It carries no billing figure.** Every dollar in it is derived at a stated rate.
4. **It does not track spend outside Rungs 0–3.** The envelope is a **ladder** budget, not a
   lab-wide one.
