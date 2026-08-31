# PROVENANCE TAGGING — DRAFTED AMENDMENT TEXT FOR `REPORTING_CHARTER.md`

## **NOT APPLIED. NOT FILED. THIS IS A PROPOSAL, NOT A CHARTER EDIT.**

**Status:** `PENDING` — awaiting a lab-wide decision by **verification-supervisor** and **the chief**.
**Target file:** `docs/charters/REPORTING_CHARTER.md` — **NOT heat-transfer's territory.**
**This document does not amend it, and `REPORTING_CHARTER.md` was not opened for editing.**

| field | value |
|---|---|
| Drafted | 2026-08-31T00:00:56Z by a heat-transfer lab-lane, on heat-transfer-supervisor's instruction |
| Origin | the chief's commendation of ansys-verification's self-correction, 2026-08-30 |
| Heat-transfer status | **`ADOPTED AS BINDING FOR HEAT-TRANSFER IMMEDIATELY`** — boarded at `docs/LAB_STATE.md`, `## heat-transfer` |
| Lab-wide status | **`RECOMMENDED, NOT IMPOSED`** — goes to verification and the chief |
| Docket | `D582` |

### WHY THIS IS A DRAFT AND NOT AN EDIT

Sanaa's 2026-08-30 directive has each team update **its own** charters and standards. It does not
authorise editing a **shared** charter, and `CLAUDE.md` reserves retiring or amending a lab-wide
clause. `REPORTING_CHARTER.md` is a shared charter owned outside this team. **Heat-transfer may bind
itself and may recommend; it may not legislate for the lab.** Adoption inside our own remit is
carried by the board entry; the lab-wide question is referred, not decided.

**Considered and rejected as the home:** `docs/standards/INNOVATION_STANDARD.md` (a standard for
proposing new work, not for how numbers are relayed) and `VERIFICATION_CHARTER.md` (owns the
**verdict** vocabulary of `CLAUDE.md` rule 1 — a provenance tag qualifies a *number*, not a *gate*,
and conflating the two vocabularies would invite exactly the "softer word" substitution rule 1
forbids). **`REPORTING_CHARTER.md` is the right home** because the duty attaches to *relaying*, and
that charter already fixes the six report headings and the `PENDING: <path>` reservation.

---

## DRAFTED AMENDMENT TEXT

*Below is the text proposed for append at the foot of `REPORTING_CHARTER.md` under `CLAUDE.md`
rule 6 — a dated amendment, appended, with a version bump and the assertion `lines whose number
changed above this section: 0`. **No existing line of that charter is altered by this proposal.***

> ### AMENDMENT — PROVENANCE TAGGING OF RELAYED NUMBERS (proposed 2026-08-31)
>
> *lines whose number changed above this section: 0*
>
> **§R-P.1 — THE RULE.** Every number relayed upward — lane to supervisor, supervisor to chief,
> chief to Sanaa — **carries a provenance tag**. **A number without a tag is not reportable.**
>
> **§R-P.2 — THE VOCABULARY, AND ONLY THIS VOCABULARY.** Eight tags:
>
> | tag | means |
> |---|---|
> | `MEASURED` | read from an artifact produced by **this** object, still on disk |
> | `DERIVED` | computed from other numbers by a stated operation |
> | `EXTRAPOLATED` | extended beyond the range of the data it was fitted on |
> | `REGISTERED` | fixed in a frozen pre-registration; true by commitment, not by observation |
> | `REPORTED-BY-OWNER` | stated by the owner and **not verifiable on this box** (e.g. the $/core-h rate, `COMPUTE_BUDGET_CHARTER.md` §5) |
> | `BORROWED` | **MEASURED on a DIFFERENT object** and asserted to apply here |
> | `ASSUMED` | chosen by judgement, with **no measurement anywhere behind it** |
> | `TRANSCRIBED` | **copied from another record** rather than re-derived from the artifact |
>
> **§R-P.3 — THE LAST THREE ARE NOT NEW WORDS.** `BORROWED`, `ASSUMED` and `TRANSCRIBED` are
> **already in use verbatim** in frozen lab records — `verification/runs/T-family/T17_runs/T17_registered.json`
> (`cost.rate_provenance`: *"BORROWED, NOT MEASURED ON THIS RUNG"*),
> `docs/campaigns/T-family/T20_PREREGISTRATION.md:999-1001` (*"BORROWED, NOT MEASURED"*,
> *"ASSUMED, NOT MEASURED"*), and
> `verification/runs/T-family/T17_runs/queue_drafts/T17_CY_f.json:21` (*"TRANSCRIBED, NOT
> REGISTERED"*). This clause **codifies vocabulary the lab already reached for and could not cite**;
> it does not invent it.
>
> **§R-P.4 — `BORROWED` MAY NOT HIDE INSIDE `DERIVED`.** A borrowed value is not `MEASURED` (not on
> this object), not `DERIVED` (no derivation) and not `EXTRAPOLATED` (not extended from this
> object's own data). **A `BORROWED` tag names the object the value was measured on.** Where the
> source is itself borrowed, **the chain is stated to its measured root** — a borrow of a borrow is
> reported as such.
>
> **§R-P.5 — THE COMPOUND-NUMBER RULE. A COMPOUND NUMBER CARRIES THE PROVENANCE OF ITS WEAKEST
> INPUT, NOT OF ITS LAST OPERATION.** Tagging a dollar figure `DERIVED` is true of the arithmetic
> and conceals that the rate beneath it is `REPORTED-BY-OWNER`. **The tag propagates from the
> weakest link.**
>
> **§R-P.6 — THE TAG IS INSUFFICIENT ALONE. IT TRAVELS WITH UNIT AND REFERENT** — *what the number
> counts*, and *what object it was taken on*. Two numbers may both be correctly tagged and still be
> uncomparable; provenance answers where a number came from and never what it counts.
>
> **§R-P.7 — THE DUTY IS THE SUPERVISOR'S.** Lanes tag at the artifact; **the supervisor is the last
> place a tag can be lost**, and losing one in summary is a reporting defect attributable to the
> supervisor, not to the lane.
>
> **§R-P.8 — THIS IS NOT THE VERDICT VOCABULARY.** `CLAUDE.md` rule 1 fixes `PASS` / `GATE REACHED`
> / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` for **gates**. A provenance tag qualifies a
> **number** and **never** softens, replaces or stands in for a verdict word.

---

## THE EVIDENCE BEHIND THE DRAFT

Every figure below was **re-derived from the named artifact** by the drafting lane.

### Specimens for the three added tags

| tag | specimen | figure, re-derived |
|---|---|---|
| `BORROWED` | T17's registered rate is T14's (`laplacianFoam`, scratch copy of `T14_SQ_c`) | registered point `0.137` core-min vs actual `0.233` (`STATUS.T17_CY_c`) = **1.7007x**. `T17_CY_c` ran **ALONE** — `02:25:17Z` to `02:25:31Z`, the next T17 case starting `16:15:56Z`, a gap of **49,825 s (13 h 50 m 25 s)** — so the miss is **the borrowing, not contention** |
| `ASSUMED` | T20's `t_overhead` | **2.1e-03 core-s/step**, "3x T17's total 0.70 ms/step", the 3x a declared allowance; the registration itself calls it **"the weakest figure in the registration"** |
| `TRANSCRIBED` | the `1.528x` transposed into a heat-transfer census | belongs to **`F22_LAMB_OSEEN`**, a **cfd** rung — `docs/COST_CALIBRATION.md:229`, row `C-153`, cleaned/predicted **1.528** |

### The two-hop borrow chain (found while drafting; not previously recorded)

`T20` rate **2.80e-07** ← borrowed from T17's uncontended reading ← T17 registered **1.64e-07**
← borrowed from T14. **`2.80e-07 / 1.64e-07 = 1.707`**: T20's rate is the T14 borrow multiplied by
T17's measured miss *of that same borrow*. **§R-P.4's chain clause exists because of this specimen.**

### The compound-number specimen

`T3_R_ff` = **`$22.8773`**, re-derived as **`26,757.067 core-min / 60 x $0.0513/core-h =
$22.87729`**. `MEASURED` core-minutes at a `REPORTED-BY-OWNER` rate. `DERIVED` is true of the
operation and hides the clause the reader must not miss.

### The honest limit, stated so the practice is not oversold

The largest error of the originating evening — the retracted *"three rungs near 2x"* claim
(`docs/LAB_STATE.md:8806`) — compared **`3.8932e-06` core-s per cell-ITERATION** against
**`1.64e-07` core-s per cell-STEP**. **Tags alone would not have caught a unit mismatch**, which is
why **§R-P.6** exists.

**But the tag set would have caught two of that retraction's three counts**, and the record must say
so: `1.64e-07` is `BORROWED` (the registration says so in its own field), `1.528x` is `TRANSCRIBED`
from another team, and `3.8932e-06` — measured as `379.13 s / (25,600 x 3,804)` = `3.89321e-06` on a
**25,600-cell scratch copy** and then registered as the point rate for all three levels — is itself
`BORROWED` when applied to the 409,600-cell level, where the measured rate is
`128,921.18 / (409,600 x 40,000)` = **`7.8687e-06`**, **2.021x** the registered value.

### Relationship to `D581`

`D581` (heat-transfer, 2026-08-30) records: **never extrapolate a Roache ladder's fine level from a
two-point rate fit** — the fitted exponent fell from **0.584 to 0.139** between rungs and is **not a
constant of the ladder**. That is the same discipline from the arithmetic side: a derived number
**inherits the fragility of its weakest input**. **§R-P.5** is its bookkeeping counterpart — a
relayed number **inherits the weakest input's label**. In both, the remedy is to carry the weak link
forward instead of letting the last clean operation launder it.

---

## WHAT THIS DOCUMENT CANNOT SEE

- **Whether the other five teams concur.** Heat-transfer speaks only for heat-transfer.
- **Whether `REPORTING_CHARTER.md` already contains a conflicting clause** — this lane did not open
  that charter, deliberately, since drafting an amendment is not licence to read for a way around
  its owner. **Verification must check for conflict before any adoption.**
- **The cost of compliance.** No estimate of the reporting overhead is offered, because none was
  measured.
- **T18's `1.220x`**, cited to `docs/COST_CALIBRATION.md` row `C-201` and confirmed present in that
  row, was **not re-derived** from T18's own `STATUS` files — **`REGISTERED`, not `MEASURED`.**

## ONE INSTRUMENT GAP, REFERRED TO VERIFICATION

`scripts/insert_section_block.py` **does not exist** — absent from disk and from `git ls-files` —
though it was believed to. `scripts/append_block.py` appends **at end of file only**, so a mid-file
board section has **no byte-verified write path**, and a naive append lands one team's block inside
another's section. The drafting lane wrote an equivalent that imports `append_block`'s
`apply_substitutions` and `record_provenance` **verbatim** and adds the **SUFFIX** clause (proving
every section *below* the anchor is byte-for-byte unchanged); its selftest **PASSES**, including
negative limbs for a disturbed suffix and for an ambiguous anchor. It was **not planted in
`scripts/`** — those record instruments are verification's. **RECOMMENDED to verification for
adoption**, source available from the heat-transfer supervisor on request.
