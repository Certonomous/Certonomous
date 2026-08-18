# The Ahmed 25° ladder's turn — WITHDRAWN as a feature

**Chief ruling, 2026-08-10, recorded at `8f5bf878`.** Canonical record of the
withdrawal and every disposition applied under it. Sites carry dated pointers
here; **no original text is deleted**, and `R4_PREREGISTRATION.md` — a frozen
artifact — is not edited at all.

---

## 1. The ruling, and what decided it

> **The Ahmed 25° ladder's turn — the +8.895 × 10⁻⁴ increment from c3 (254 911
> cells) to c4 (454 691) — is WITHDRAWN as a FEATURE.**

**What decided it is not the branch.** The pre-registered discriminator returned
**B3 (broad scatter)** at `R = 0.324` against a 0.28 bar — a near miss at the
14.6th percentile of the null, reported as a near miss rather than resolved.
The ruling does not rest on it.

**It rests on the fact that needs no branch:**

| | |
| --- | --- |
| `s_c3` over all four draws | 2.769 × 10⁻³ |
| **`s_c3` with the most extreme draw REMOVED** | **8.972 × 10⁻⁴** |
| the c3 → c4 increment the turn consists of | 8.895 × 10⁻⁴ |
| **ratio** | **1.01×** |

**Even after removing the suspected outlier, the scatter at the rung the turn is
measured *from* equals the whole turn.** The turn is unreadable from single draws
in either direction.

**And the withdrawal is robust to which draw you exclude** — the sensitivity
analysis is what makes it safe:

| basis | re-estimated increment | vs published |
| --- | --- | --- |
| all four draws | **−8.907 × 10⁻⁴** | −1.001× — **sign inverts** |
| excluding the extreme draw | **+4.445 × 10⁻⁴** | +0.500× — **halves** |

There is no choice of exclusion under which the published +8.895 × 10⁻⁴ survives
intact. That is why n = 4 was enough here where n = 2 was not.

**The four draws** (all `residualControl` met, all certificates `clean`, all
within 1.5% of c3's cell count):

| draw | divisions | cells | Cd |
| --- | --- | --- | --- |
| c3s4 | (100 21 59) | 254 211 | 0.073943978 |
| **c3 (published)** | (98 21 59) | 254 911 | **0.073992743** |
| c3s3 | (99 21 60) | 255 991 | 0.075521791 |
| c3b | (99 21 58) | 251 113 | 0.079827008 |

## 2. The sentence that keeps its wording and now argues the opposite

**Chief's explicit instruction, applied verbatim in `R4_ASYMPTOTIC_RESULTS.md`
§4:** *"Not one unlucky mesh"* **keeps its wording**, because it is literally
true — and its defence has inverted.

It was written to argue: *the turn is not the fault of a single unlucky mesh,
therefore the turn is real.* Four draws at c3 say **the premise holds and the
conclusion does not.**

> **The defence fails not because one mesh was unlucky, but because NO SINGLE
> DRAW CARRIES THE INCREMENT.**

Showing that c4 and c4b agree cannot establish a turn when the rung the turn is
measured *from* moves by more than the turn itself. The original evidence was
gathered at the turn's **upper** end; its **lower** end was a single draw until
2026-08-10. A reader who meets that sentence now meets its inversion beside it.

## 3. Dispositions applied

| site | applied as |
| --- | --- |
| `R4_ASYMPTOTIC_RESULTS.md` §3 (*"the ladder is non-monotone"*) | dated withdrawal before the conclusion; original retained |
| `R4_ASYMPTOTIC_RESULTS.md` §4 (*"Not one unlucky mesh"*) | **wording kept**, inversion stated above it (§2) |
| `R4_ASYMPTOTIC_RESULTS.md` §4 caveat (`4f73e0af`) | superseded: it said *n = 2 of a planned 4*; it is now n = 4 of 4 |
| `W1_AHMED_LADDER_DISPOSITION.md` (*"The fourth rung turns around"*) | dated withdrawal |
| `ahmed_25.json` | `turn_withdrawn_2026_08_10` block with the four draws and both re-estimates; serialisation verified before rewriting |
| `W3_WING_VALID_FAMILY_RESULTS.md` Ahmed row (*"turns"*) | withdrawn — **both bodies that table called "turns" are now withdrawn** |
| `B52_RUNG7_RESULTS.md` | its own 2026-08-10 caveat said *"the Ahmed half is NOT withdrawn"* — superseded the same day |
| `scripts/add_proposals_r4.py` | generator header extended, so a regeneration cannot reintroduce withdrawn text |
| **`R4_PREREGISTRATION.md`** | **NOT EDITED — frozen artifact.** Its `253×` correction already lives on the live record (`88efa816`) |

**One prediction scored, in the lab's favour.**
`W3_WING_VALID_FAMILY_RESULTS.md` wrote, nine days early: *"the B-52's turn at
441 057 cells and the Ahmed 25°'s at 454 691 sit in the same band… It should be
[replicated], before the B-52's oscillation is treated as physics."* **It was
right, the replicates were eventually run, and both turns are now withdrawn.**
That paragraph is marked SCORED rather than left to look like a coincidence.

## 4. What the withdrawal does NOT reach

- **The Ahmed Cd values are not wrong.** Four draws, all converged, all
  certified. What is withdrawn is the *feature* read from their differences.
- **The ladder's verdict is unchanged**: `conclusive: false`, `monotone: false`,
  no order. It is better founded, not different.
- **Not the bistability hypothesis.** `R = 0.324` leans toward outlier structure
  and Cl moved with Cd, but B3 fired and n = 4 cannot separate the two.
  Distinguishing them needs field inspection, not more draws — and is not
  proposed here.
- **Not `ahmed_35`, nor any other body.** Two geometries have already behaved two
  ways in this lab.
- **Not c5.** Its refusal (unconverged, 2σ = 6.26% of value) stands on its own
  rule and is untouched.
- **A separate record-integrity gap, flagged not fixed:** `ahmed_25.json`'s
  stored `levels[]` are the OLD three-rung study (finest 79 439 cells). The
  five-rung constant-ratio ladder this withdrawal concerns lives only in
  `R4_ASYMPTOTIC_RESULTS.md` and was never merged into the stored study.

## 5. The count that now matters

With this ruling, **both** ladders this lab ever described as turning are
withdrawn — and every replicate family it has ever measured has returned a
material finding:

| family | what the replicates found |
| --- | --- |
| B-52 | the published turn was `max(rung 6) − min(rung 7)` of eight draws — **withdrawn** |
| NACA 0012 | the published mesh is the family **maximum** at +1.35σ; 3 of 4 draws land inside the band the row failed |
| NACA 4412 | construction scatter 5.82 / 12.74 / 4.20% of the mean, non-monotone, worst at the graded rung |
| **Ahmed 25°** | the increment **inverts or halves** depending on which draw is excluded — **withdrawn** |

**Four for four. The check has never once come back clean.** That is the
argument carried into the archive replay for
`w3-no-ladder-feature-without-draw-scatter`.
