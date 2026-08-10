# S6 wiring pre-registration

**Written 2026-08-10, BEFORE any wiring code exists.** Filed by the
Infrastructure/Standards family under the chief's ruling of the same date,
which approved wiring S6 (residual stall) into `HeadEngineer` on two named
conditions and required this pre-registration as a third. No line of the
wiring is written when this file is committed; the commit ordering is the
evidence.

## 1. What is being wired, and what is not

**S6 only.** S8 (Courant excursion) **stays unwired** until it has its own
replay on the corrected corpus. "S6 approved" does not cover S8, and this
sentence exists so nobody reads it that way.

S6 currently cannot fire on any production run: it returns early without a
`residual_target`, and `HeadEngineer.__init__` has no parameter by which one
could be supplied (`MONITOR_STANDARD.md` v1.5 correction).

## 2. The two conditions, as mechanisms

**Condition 1 — the target comes from the case's OWN residual controls.**
`HeadEngineer` builds the case it runs, so the recovery reads that case's own
`system/fvSolution`, never "whichever `fvSolution` sits nearest". This is the
same derive-from-what-configures-the-run principle that fixed the replay
corpus itself.

**Condition 2 — the sentinel class is excluded BY CONSTRUCTION, not by a
threshold.** A declared `residualControl` target at or below **that field's
own linear-solver `tolerance`** is unreachable in principle: the outer
residual cannot be driven below what the inner solve resolves. Both numbers
are declared by the same file, so the exclusion is a relation the case states
about itself, with no magic constant anywhere.

Validated on the corrected corpus (1,375 run logs, 222 gated) **before**
adoption, which is what section 3.1 asks for:

| class | logs | fire | rate | of which the `1e-15` sentinel |
|---|---|---|---|---|
| target ≤ field's own solver tolerance (**excluded**) | 135 | 134 | 99% | **135 of 135** |
| target > tolerance (**gated**) | 81 | 35 | **43%** | 0 |
| tolerance unreadable (**not gated**, fail open) | 6 | 6 | 100% | 0 |

The discriminator is exact: it captures every sentinel and nothing else. The
motivating case states it in its own text — `p 1e-15;//1e-4;`, a real target
commented out and replaced with an unreachable one to force a run to its
iteration cap — and its solver tolerance for `p` is `1e-12`.

## 3. The predictions this arm is scored against

Recorded before the wiring exists, and **the family spread separately**,
because a single global number hides it in both directions.

- **Primary: the post-wiring fire rate on `HeadEngineer` runs is 48%,
  ±15 percentage points.** The campaign family is the nearest analogue to what
  `HeadEngineer` runs (geometry studies, the Ahmed act, the NASA hump act, the
  UQ studies); the whole-corpus rate of 43% is the fallback expectation.
- **Family spread predicted, and it is the finding rather than the headline:**
  campaign **48%** (16/33), dafoam **92%** (12/13), mega-batch **20%** (7/35).
  A rate that is uniform across families after wiring would itself be a
  result — it would mean the recovery logic is not seeing what the replay saw.
- **Sentinel exclusion: 0 gated runs whose target is at or below its own
  solver tolerance.** Any such run reaching the gate is a defect in the
  exclusion, not a fire.
- **Fail-open count stated, never silent:** runs whose tolerance cannot be
  read are NOT gated, and the count is reported rather than folded into
  either class.

**If the post-wiring rate lands outside the prediction, that is a result about
the recovery logic and is reported as one** — not adjusted away, and not
retro-fitted with a reason. The bar is fixed here and now.

## 4. What would refute the wiring

- A gated run whose target is at or below its own solver tolerance (condition
  2 breached).
- A target recovered from a `fvSolution` that is not the running case's
  (condition 1 breached).
- A fire rate outside 48% ± 15pp with no identified cause in the recovery
  logic.

Any of these means S6 comes back out, and the standard says so rather than the
rate being renegotiated.
