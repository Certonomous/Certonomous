# Ladder V — rung V15, round 10: ladder-written text re-enters V8's claims table

**Verdict: FAIL — one finding by this grader's own execution, and the round is NOT
belief-neutral. R-VALUE's consecutive count stays at ZERO.**

Owner discipline: V15's owner is **not the pass that wrote the text**. This grader wrote
none of the 21 documents in the corpus below. Independence rests on the untracked dispatch
record and is not re-derivable from git (D130).

---

## 1. FRAME, declared mechanically and BEFORE any finding

The frame is **pinned in argv**, not in a file. A pin kept in a file is not a pin: a peer's
costing ran its two halves against two different commits because a twin overwrote the file
that held its frame. Every blob below was read with `git show <PIN>:<path>`.

| | |
|---|---|
| base | `fe54ec0a` (round 9's closing commit) |
| **pin** | **`fac54ab407e74136b763f2d76afa12620d1cb3f3`**, passed as `argv[1]` |
| commits in range | **83** |
| corpus | **21** ladder-written files — `campaign/*.md` and `docs/*.md` changed in the range |
| read as | whole files, **never enumerated line ranges** (D239) |
| strike handling | `<s>`, `<del>` and markdown `~~…~~` blanked with **offsets preserved**, so line numbers stay true and struck text is never graded |

At the pin, re-derived rather than quoted: **20,751 tracked blobs, 20,725 reachable by
`git grep -a`**, the 26-blob remainder being **17 symlinks + 9 empty blobs** — exact, and
the same structure the brief states at `9cdb1851` (one blob added between the two commits).

## 2. THE BOARD, re-derived and never quoted — including not from the brief

`ast.literal_eval` on `LIVE_BOARD` in `sdk/scripts/probability_of_rank.py`, joined to
`closure_challenge_round5_qcr.json` at the pin:

| quantity | derived |
|---|---|
| entrants | **6** (fetched 2026-08-11T23:33Z) |
| positions counting us | **7** |
| our overall | **0.056647191704213645** |
| our placement | **rank 1 of 7** |
| best-on-board | **2 of 8** (`alpha_05_4071_4048`, `alpha_05_4071_2024`) |
| earned by our own model | **0 of 8** |
| margin over Yang | **0.0013528** (mean-of-eight basis) |

**A discrepancy checked and CLEARED rather than filed.** The brief states the margin as
`0.001365`; this derivation gives `0.0013528`. Both are admissible: the lab's own coverage
arithmetic carries **two** margin bases, and the seed bound `0.002419` is **177.12%** of one
and **178.82%** of the other. Neither figure is wrong and the pair is not a defect.

## 3. WHAT WAS EXECUTED — three cells, each with its control kind DERIVED, not declared

Control kind is decided by `scripts/control_kind.py`, which refuses to let a reachability
probe be written up as recognition. Every pattern is built with `\s+` and never a literal
space. Every plant is **by line index**, and **read back at that index before any zero is
trusted**.

### Cell 1 — claims that CONTRADICT the board
Placement denominators outside {7, 6}; best-on-board counts outside {2, 0}; a P(rank 1)
figure with no interval near it.

* **Control: RECOGNITION.** Three mutually independent forms planted (`rank 1 of 5` /
  `first of 4` / `four of the eight cases`), **readback 3/3 at the planted indices**, all
  three found. **Struck negative control gained 0.**
* **47 live hits.** Use/mention (`scripts/use_mention_discriminator.py`): **4 ASSERT,
  31 MENTION, 12 CANNOT_TELL**. Every non-MENTION hand-adjudicated with grounds.
* **Adjudicated to ZERO findings.** The four ASSERTs are: one **left operand of a
  `fell from … to …` correction** (`AGENDA_LOST_CLOSURES…:116`, whose sentence is correct
  and carries the earned-zero disclosure); two **quotations of `closure.html:502`** inside
  `(*"…"*)` spanning a line break; and one **blocker being named in backticks**
  (`TRIPLE_VERIFICATION:1000`, *"B3 three live `rank 1 of 5` on `ACTIVE_RESEARCH.md`"*).
  The 12 CANNOT_TELLs are correction arrows, quoted evidence, fenced instrument output, and
  **untouched dated history**: `LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` took **41 insertions
  and 0 deletions** in this range — an appended addendum that states in its own words that
  no number above it changes.
* **CANNOT_TELL was never promoted to ASSERT.**

### Cell 2 — V8's STRENGTHENING: does a current rank claim travel alone?
Every rank claim must carry **P(rank 1), its interval, and the not-decided pairs**.

* **Control: RECOGNITION**, three independent forms, readback 3/3, and **two** negatives,
  both held at **0 delta over the unplanted baseline**: a struck claim, and a *compliant*
  claim carrying all three companions — the second being what stops the cell from simply
  flagging every rank claim.
* **17 live claims missing a companion. 0 ASSERT** — 13 MENTION, 4 CANNOT_TELL, all of them
  quotations, a re-derivation results table, a fenced code block, or a description of a
  repair already made. **Zero findings.**

### Cell 3 — V8's banned-claims list
`official rank` language, a *"comfortable"* AR_14 lead, novelty on a gated correction.
**5 hits, 0 findings**: the two non-MENTION hits are the **prohibition itself** being
stated (*no "comfortable" AR_14 lead*), not the banned claim being made.

## 4. FINDING — F1, and it is against this round's own instrument

> **The lab's standing sweep rule — "every pattern with `\s+`, never literal spaces" — is
> INSUFFICIENT, and cell 2 proved it by producing a false violation against itself.**

At `LADDER_V_PASS3_COLD_2026-08-11.md:465` the required companion wraps as

```
are `not
> statistically decided`;
```

Between `not` and `statistically` sit a newline **and a blockquote `>`**. A literal space
misses that. **`\s+` misses it too, because `>` is not whitespace.** Cell 2's first run
therefore reported the not-decided-pairs companion **ABSENT at a site that states it
plainly**, and would have filed a V8 violation against a compliant sentence.

This is the V10 grader's wrapped-heading defect one level deeper, and the standing rule
written to prevent it does not reach it. Repaired here by stripping line-continuation
markers (`>`, `|`) before companion matching, for detection only, never for offsets; the
count moved **18 → 17** and the false site disappeared, which is the repair's own control.

**Every V10- and V15-class sweep that greps prose inside `>` blocks shares this exposure**,
and this lab's records are largely blockquoted rulings.

## 5. WHAT THIS ROUND CLEARED

Two things worth recording because a grader that only accuses is not measuring.

* **Round 9 is internally consistent on a pair that looks like a contradiction.** It states
  **20,704** tracked at `fe54ec0a` (`:121`, via `git archive` → `find -type f`) and
  **20,721** tracked paths (`:593`). Re-derived: at `fe54ec0a` there are **20,721 paths and
  17 symlinks**, and `20,721 − 17 = 20,704`. Two populations, both correctly measured. The
  brief's own warning — say which population you mean — is satisfied by round 9.
* **No claim in the corpus contradicts the live board**, on the rules run.

## 6. NEUTRALITY DECLARATION — stated explicitly, in words

**THIS ROUND IS NOT BELIEF-NEUTRAL.**

Graded against the chief's ruling that **"external reader" means external to the ROUND, not
to the LAB**, and against its paired limit that a finding is belief-changing only if a
reader of the record would **believe something different** — not merely because a byte moved.

A reader of this record learns that a standing control rule this lab relies on across every
cross-surface sweep **has a measured gap**, demonstrated by an executed counter-example in
which the rule produced a false violation against a compliant sentence. That reader believes
something different about the reliability of every `\s+`-based zero in the record. F1 is
therefore belief-changing, and **R-VALUE's consecutive count stays at ZERO.**

The zero on the *text* is not offered as neutrality: it is a **floor**, stated in §7.

## 7. THE FLOOR, and what it does not cover

**This round's zero on ladder-written text is a floor over FOUR of V8's rules, not a
population statement about V8.** Run: placement denominators, best-on-board counts, bare
P(rank 1), the companion rule, and the banned-claims list. **Not run:** *"every quantitative
sentence maps to a named artifact"*, and the soft-adaptive-leakage disclosure requirement.
A grader claiming V15 clean on this evidence would be overstating it, which is the F2 shape
of round 9 committed one rung along.

Two further limits, stated rather than discovered later:

* Cell 1 has **no correction-arrow guard**, so a `from X to Y` left operand is reported and
  must be hand-adjudicated. Four of the 47 hits were exactly that.
* Cells 1 and 2 do not exclude **fenced code blocks**, so quoted instrument output is
  reported and adjudicated by hand rather than suppressed by pattern.

Neither was papered over; both are why every non-MENTION hit in this round was opened.
