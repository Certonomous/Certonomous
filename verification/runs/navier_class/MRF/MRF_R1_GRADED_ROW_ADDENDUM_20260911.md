# ADDENDUM 1 — 2026-09-11 — to `MRF_R1_GRADED_ROW.json`

**THE VERDICT DOES NOT CHANGE.** `MRF_R1` remains **`NOT A RESULT`**, value
`Np = 4.452990835457764`, triple `DIVERGENT`, observed order `p = -5.231143303181195`,
**no GCI quoted**. Nothing in the graded row is re-opened, and the graded JSON is
**not edited**: it is a frozen graded artifact and this addendum sits beside it
(CLAUDE.md rule 6; rule 2's "changes land only as dated addenda").

## What is wrong with it

`MRF_R1_GRADED_ROW.json`'s `why` field reads, in full:

> finest triple ('coarse', 'medium', 'fine') is DIVERGENT at dim = 3, observed order
> -5.2311; the value, every triple and every order are printed beside it, and **NO GCI
> is quoted because the three values are not monotone**

**The clause after "because" is FALSE, and the row's own fields say so.** The same
JSON carries `"monotone": true`. Recomputed here from the row's own `levels`, in the
invocation that emits this sentence — quantity: monotonicity of the three `Np` values
across the grid triple, coarse → medium → fine:

| level | cells | `Np` |
|---|---:|---:|
| coarse | 154,715 | 4.238028963558982 |
| medium | 448,972 | 4.268044558222370 |
| fine | 1,273,803 | 4.452990835457764 |

The sequence is **strictly increasing**, so it **is** monotone. The stated reason for
withholding the GCI is therefore not the operative one.

## Why the behaviour was nevertheless correct

**The safety behaviour and the stated reason came apart; only the reason was wrong.**
A GCI must not be quoted beside a triple that is not `CONVERGING` (CLAUDE.md rule 5).
This triple is `DIVERGENT` with an observed order of `-5.2311`, and **that** — not
monotonicity — is the operative reason no GCI appears. The grader withheld the GCI,
which is what rule 5 requires; it then explained the withholding with a condition that
did not hold. **No number that was printed is wrong, and no number that should have
been printed is missing.**

## Mechanism, and its repair

The sentence was not composed for this row. It came from
`scripts/roache_triple.py:629-632`, where `"the three values are not monotone"` was
the **`else` limb of a two-way branch over a six-state vocabulary** — so every
non-degenerate `NOT A RESULT` state reached for it, monotone or not.
**Repaired at `a7b3846d8`** (2026-09-11T16:43Z): one function now writes the reason a
GCI is withheld, and **a state it has not been taught REFUSES rather than reaching for
the reassuring sentence**. `MRF_R1` was graded *before* that repair and so carries the
pre-repair text.

## The reading worth keeping

**A false explanation attached to a correct action is harder to catch than a wrong
answer, because the artifact looks internally complete.** This one survived grading,
landing and a cost row. It was caught only by reading the `why` string against the
`monotone` field in the *same* file — two fields of one artifact contradicting each
other. **A record that explains itself should be checked against its own data, not
only against the world.**

## Scope

- **Applies to:** `verification/runs/navier_class/MRF/MRF_R1_GRADED_ROW.json`, field `why`.
- **Does NOT apply to:** any gate, threshold, cap or label; the verdict; any value,
  triple, order or state; the rule-12 cost row for `MRF_R1`.
- **Related:** the malformed id on that cost row is corrected separately by
  `C-20260911T182625.621992Z-1ad8d1fb` (commit `a7ec53b65`); that is an id defect and
  is unrelated to this one.
