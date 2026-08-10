# Note to the chief — the gain table's priority order is inverted against outcomes

**2026-08-10. One page. A finding, not an amendment — the charter is not edited here.**

Requested under chief ruling 7 of 2026-08-10. Evidence base:
`campaign/EIG_RANKING_LOOKBACK_2026-08-10.md`, all 114 closed docket items graded
0–3 on what they delivered. Zero solver core-min.

---

## The table, and what it delivered

`_GAIN_POINTS` in `sdk/chief_engineer/agenda.py` (charter §Axis A) assigns each
proposal a score by `source_kind`. Graded against delivered value:

| source_kind | gain points | rank the table gives it | n | **mean delivered V** | rank the record gives it |
|---|---|---|---|---|---|
| `challenge` | **4.0** | **1st** | 4 | **2.00** | **7th (last)** |
| `measurement` | 3.0 | 2nd = | 24 | 2.38 | 4th |
| `gate` | 3.0 | 2nd = | 25 | **2.64** | **1st** |
| `capability` | 2.0 | 4th = | 17 | 2.41 | 2nd |
| `ledger` | 2.0 | 4th = | 11 | 2.36 | 5th |
| `reading` | 2.0 | 4th = | 13 | 2.31 | 6th |
| `report` | **1.0** | **7th (last)** | 19 | 2.21 | **5th** |

*(`inbox` has no closed items in the cohort. One item carries no `source_kind` and
scored V = 3.)*

**Spearman ρ between gain points and delivered value across the 114 items:
+0.118, p = 0.21.** The table does not predict what its own docket delivered.

## The two inversions worth your ruling

1. **`challenge` is scored highest and delivered least.** The kind the table exists
   to prioritise sits last on outcomes.
2. **`report` is scored lowest and out-delivered `challenge`.** 1.0 point against
   4.0, and 2.21 against 2.00.

## The case against over-reading this — stated before the case for it

- **n = 4 for `challenge`**, which is thin, and it is the *only* thin cell.
- **Two of those four are duplicate filings of the same rung.**
  `w5-sparta-is-still-the-cheapest-real-result` and
  `w5-sparta-frozen-rans-is-the-unblock` both closed by pointing at the same
  existing SpaRTA record and both spent zero of their 60 core-minute budgets. They
  graded V = 1 each. Dropping both lifts `challenge` to a mean of 3.00 on n = 2 —
  which would put it *first*, not last.
- **So inversion 1 is not robust.** With n = 2 either way, `challenge` is
  unmeasurable in this cohort, and I am not asking you to rule that it is
  mis-scored. What the two duplicates *do* establish is separate and firmer: the
  highest-scored kind on the table is the one where duplicate filings survived to
  execution, which is the duplicate-check proposal's argument, not the gain table's.
- **Inversion 2 does survive.** `report` at n = 19 is the third-largest cell and
  needs no caveat: the lowest-scored kind delivered more than the mean of the whole
  `capability`/`ledger`/`reading` tier that outscores it 2-to-1.

## What is robust across the whole table

- **`gate` at 3.0 is correctly placed** — highest mean V (2.64) on the largest cell
  (n = 25). The one part of the table the record endorses.
- **The 2.0 tier is undifferentiated in reality.** `capability` 2.41, `ledger` 2.36,
  `reading` 2.31 — a spread of 0.10 across 41 items. The table is right that they
  are equal; it is the *level* that is wrong, since `capability` at 2.0 outperforms
  `measurement` at 3.0.
- **The table takes only four distinct values across 114 items**, so it cannot
  order most of the docket at all. This is the same structural weakness that
  produced the recorded 2026-08-05 failure (24 of 55 proposals on a silent default).

## What I recommend you consider, and what I do not

**Do not** re-point the numbers on this cohort. Fitting seven weights to 114 graded
outcomes, graded by one agent, is exactly the in-sample move the lab refuses
elsewhere, and inversion 1 — the one that looks most dramatic — dissolves on n = 2.

**Do** consider whether `report` at 1.0 is defensible at all given `report`
out-delivered two kinds scored above it, and whether `measurement` at 3.0 above
`capability` at 2.0 survives its own evidence (2.38 against 2.41).

**The structural point matters more than any weight.** A four-valued table over a
263-item docket is not a ranking, and the already-filed numerator proposal
(`eig-bits-as-a-ranking-input-mechanically-scored`) adds a term computed from what
each proposal *pre-declares* rather than what it is *called* — which is the thing
the record does predict (ρ = +0.197 mechanically scored, p = 0.035, top-20
precision 0.70 against the table's 0.35).

## Limits of this note

Outcomes were graded by one agent from each item's own `outcome` field, with no
independent check. The grading is hindsight by construction. Under random ±1
perturbation of 15% of the grades, the EIG-numerator result holds on 99.0% of 2,000
draws; **no equivalent robustness was run on the per-kind means in the table above**,
and the per-kind cells are small enough (4 to 25) that they deserve one before any
amendment is drafted. That check is cheap and I will run it on request.

Provenance: `campaign/EIG_RANKING_LOOKBACK_2026-08-10.md` §2, §4;
`agenda/docket.json`; `sdk/chief_engineer/agenda.py` `_GAIN_POINTS`;
`docs/charters/GOALS_AND_PROPOSALS_CHARTER.md` §Axis A. Charter unedited.
