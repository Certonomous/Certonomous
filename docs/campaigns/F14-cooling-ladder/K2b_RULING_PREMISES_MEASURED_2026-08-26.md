# K2b — **THE RULING WAS NOT EXECUTED. ALL THREE OF ITS STATED PREMISES FAIL ON MEASUREMENT.**

**Written by a `lab-lane` under `heat-transfer-supervisor`, 2026-08-26. ZERO COMPUTE —
no solver launched; every number is read from files already on disk.** **NOTHING IS
STRUCK, NO VERDICT IS CHANGED, NO DOCUMENT IS AMENDED BY THIS FILE.** Nothing has been
sent, filed, submitted, uploaded, registered or posted outside this box (`CLAUDE.md`
rule 7).

---

## 0. What was ordered, and what this lane did instead

A ruling was issued to strike two `PASS` rows in
`docs/campaigns/F14-cooling-ladder/K2b_PILOT_RESULTS.md` to `NOT A RESULT`, and to add a
statement of the document's ungated tier. **This lane was instructed to confirm the
ledger containment itself rather than take it on authority. It did — and the check
falsified the premise it was sent to confirm, and then two more.**

**The ruling is referred back unexecuted.** The supervisor may re-issue it on corrected
facts; a lane may not execute a verdict change whose every stated ground it has just
measured to be false.

## 1. PREMISE 1 — *"No K2b row appears in the three ledgers at all — zero verdict words in any of the three."* **FALSE in its literal form; TRUE in substance.**

Measured, with an absence control (L-337): each search was first shown able to see a
rung name in the same file, so a zero would have been evidence.

| ledger | K2b hits | control hits (`K0b`/`T1b`/`K0c`) | file lines |
|---|---:|---:|---:|
| `docs/VALIDATION_INVENTORY.md` | **2** | 23 | 926 |
| `docs/COVERAGE_MATRIX.md` | **1** | 51 | 2,188 |
| `docs/THERMAL_CAPABILITY_STATE.md` | **1** | 17 | 339 |

**K2b reaches all three ledgers.** What it says there:

- **`VALIDATION_INVENTORY.md:247`** — a `K2b pilot` row, gate column **`none`**, status
  column **`"it is a capability case in the K0a/K0b sense, never a result"`**.
- `VALIDATION_INVENTORY.md:657` — a **monitor-defect** row about signature S13 as found
  in K2b. A finding about an instrument, not a K2b verdict.
- **`COVERAGE_MATRIX.md:858`** — *"Two rows that cannot be tiered at all: K2bU and
  K2bU3 carry a pre-registration, tracked case inputs and tracked comparators, and no
  results record and no sub-row… NEVER RUN cannot be separated from
  completed-but-unfiled from HEAD."*
- **`THERMAL_CAPABILITY_STATE.md:38`** — *"K2b, K2e, KV1 | rack-row module, Boussinesq
  limit, heat-balance path | internal | capability and limit rungs, **not gates against
  experiment**"*.

> **THE OPERATIVE FACT SURVIVES AND THE STATED ONE DOES NOT. No K2b row carries a gate
> verdict word in any ledger, so NO CREDENTIAL IS AT RISK. But the ledgers are not
> silent about K2b — they already record it, correctly, as explicitly ungated.**

**This matters beyond pedantry, because the escalation trigger was written against the
literal form.** The ruling reserved to Sanaa any finding of this shape that *"does reach
one"* of the ledgers, as D389-class. **It reaches three.** Whether reaching them *as
explicitly-ungated capability rows* still keeps the finding inside a supervisor's
authority is **the supervisor's call and Sanaa's, and this lane does not take it** — it
is named so that the trigger is evaluated on the true reading rather than the assumed
one.

## 2. PREMISE 2 — *"the document nowhere states that it is ungated pilot work… I searched it for a self-description as ungated, SURVEYED, or carrying no gate: zero hits."* **FALSE.**

**The document states it at line 30, in a blockquote, in its opening section**, carried
unchanged from `K2a_RACK_ROW_MODULE_SPEC.md` §6:

> *It exists to shake down the BC coupling, the monitor wiring and the heat-balance path
> at ~1/15 the cost before the 3D module burns anything, and **it is a capability case
> in the K0a/K0b sense — never a result.***

And immediately below, at lines 32–34: *"**Nothing below is a validation of anything.**
No number here is compared against a measurement of a real facility, because no such
comparison is in scope — that is K2c's gate, and K2c has not run."*

**Why the search missed it, and it is the fourth instance in twenty-four hours:**

| search term, as stated in the ruling | hits |
|---|---:|
| `ungated` | **0** |
| `SURVEYED` | **0** |
| `no gate` | **0** |
| **`never a result`** — the lab's own phrase, which the document actually uses | **1**, at line 30 |
| **`capability case`** | **1**, at line 30 |

> **L-337, A FOURTH TIME, AND ON A FOURTH AXIS — VOCABULARY.** The three recorded
> instances were wrong on **source** (`git ls-files`), **place** (two of three registered
> homes) and **key** (rung-named directories). This one is wrong on the **words**: the
> sweep searched for the vocabulary the searcher expected instead of the vocabulary the
> corpus uses, and returned a confident zero.
>
> **The absence control would have caught it exactly as it caught the others** — a
> search of this file for a string known to be in it returns 44 hits, so the instrument
> was live and the zero was about the query, not the document.

**Consequence: the ruling's remedy is already in the record.** The `SURVEYED`-equivalent
statement it ordered added is present in the document at line 30 **and** carried into
`VALIDATION_INVENTORY.md:247` in the same words. **There is nothing to add.**

## 3. PREMISE 3 — *"five `PASS` rows across three cases"* as gate verdicts. **MISCHARACTERISED.**

The five `PASS` tokens are **not gate verdicts asserting that a case is valid.** They are
**cells in criterion-comparison tables**, and the document's own argument is that the
criterion producing them is broken.

| line | what the `PASS` actually is |
|---|---|
| 175 | a **heat-balance auditor exit** for `K2bP_under` at 5,000 iterations (`0.1272 %` against a governed `0.5 %`), in a table whose other five rows read `FAIL` |
| 300 | an **S13 monitor score** for `K2bP_coarse` on `T_in` — with the row directly beneath it scoring `FAIL` on `T_return`, in the same case |
| 305 | `K2bP_fine` — **already written `PASS` → REFUSED (§11)` in the document itself** |
| 352–353 | a table captioned *"the disagreement runs the other way too"*, built so that `K2bP_coarse` reads `PASS`/`FAIL` and `K2bP_under` reads `FAIL`/`PASS` — **a deliberate counterexample pair** |

**§11 is titled *"The S13 repair — a criterion that scored perfectly on a field that never
moved."*** Its subject is the `0.00000 %` at line 305: `T_in` sat at exactly the supply
temperature 289.000 K because the cold aisle was never reached, moving *"1 unit in the
last place of a ten-significant-figure print across 400 iterations"*, while the heat
balance was `2.6632 %` out. The document diagnoses this as **a defect in the standing
criterion, repaired lab-wide**, and `VALIDATION_INVENTORY.md:657` carries that defect as
a monitor finding.

> **THESE `PASS` TOKENS ARE THE SUBJECT OF THE FINDING, NOT CLAIMS THE DOCUMENT IS
> MAKING. Striking them to `NOT A RESULT` for want of a pre-registration would
> re-label the evidence in an argument as though it were the argument's conclusion —
> and at line 305 it would overwrite a refusal the document had already issued
> against itself.**

**A quote-and-strike that replaced `PASS → REFUSED (§11)` with `NOT A RESULT` would make
the record worse**, because it would delete the visible fact that this rung caught its
own defect and repaired a lab-wide criterion because of it. **That self-catch is the
rung's most transferable product.**

## 4. THE CHRONOLOGY, RECORDED SO IT IS NOT RE-OPENED — and this part of the ruling STANDS

`verification/campaign/THERMAL_K0_PREREGISTRATION.md:10-11` reads: *"Authorized compute:
K0a and K0b only. K2b, the rack-row module and any turbulent SST case are explicitly NOT
authorized and were not run."*

Both K2b pre-registrations are stamped **"Written 2026-08-18 BEFORE any diagnostic
solver ran"** / **"BEFORE any 3D transient ran"** — **the day after** K0's, which is
dated 2026-08-17.

> **K0's clause scoped K0's OWN compute and was truthful when written. K2b was
> separately registered the next day, prediction-first, with its own stated
> authorisations (45 core-minutes on the 2D module; ~11 core-minutes for the 3D check).
> THERE IS NO RULE-2 BREACH IN THAT SEQUENCE, and the K0 clause is NOT a live
> prohibition on K2b.**
>
> **Reading a campaign's honest self-limitation as a standing lab-wide prohibition would
> make every scope clause a liability** — it would punish exactly the documents that were
> most careful about their own boundaries.

**This is recorded here so that a reader finding that sentence cold does not raise it a
third time.**

## 5. What IS still open, and it is not what the ruling addressed

**The per-case registration coverage question stands and is NOT resolved by this file.**
Sixteen `K2b*` case names exist; the two pre-registrations name `K2bP_under` (and `K2b`
generically). **Whether the other cases are described by class inside those documents —
which a pre-registration is entitled to do — has not been determined**, and *"the name
does not appear"* is not *"the case is unregistered"*. That distinction is the whole of
L-337 and this lane will not breach it either.

**That is a real open item.** It is the supervisor's, and if resolving it would move
anything in a ledger it is Sanaa's.

## 6. Cost

**Zero core-minutes.** File reads and greps on the login box. `docs/COST_CALIBRATION.md`
gains no row: there is no compute to calibrate.

---

> **NOTHING WAS STRUCK. NO VERDICT MOVED. NO DOCUMENT WAS AMENDED. NO CASE DIRECTORY WAS
> TOUCHED, NO COMPUTE WAS RE-RUN, AND NO OTHER RUNG WAS REACHED.**
