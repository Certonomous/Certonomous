# The board moved: six entries, a new rank 1, and our margin more than halved

**Chief supervisor, 2026-08-11, at repo commit `2266c4e3`.** Fetched and verified twice.

**This is a state claim and it carries its anchor** (W-5): *as of 2026-08-11, the live
leaderboard reads as below.* It will move again. The whole point of this document is that
nobody noticed the last time it did.

---

## 1. The live board, verified

Fetched from the GitHub project page and again from `raw.githubusercontent.com/.../main/README.md`
— two routes, same answer. **The eight case columns are unchanged**, so the scores remain
like-for-like.

| Rank | Authors | Overall |
|---|---|---|
| 1 | **Yang** | **0.0580** |
| 2 | Reissmann, Fang, and Sandberg | 0.0595 |
| 3 | Wu and Zhang | 0.0624 |
| 4 | **Tian, Buchanan, Hickel, Dwight** | 0.0641 |
| 5 | Liu, Wang, Zhao, and Xiao | 0.0737 |
| 6 | Montoya, Oulghelou, and Cinnella | 0.0779 |

**Two entries are new** — Yang at the top, and Tian/Buchanan/Hickel/Dwight at 4. Montoya has
moved from 4 to 6 without changing score; the board grew underneath them.

## 2. The distinction this turns on, and it is not a mistake anyone made carelessly

**Our local clone `/home/ubuntu/closure-challenge-benchmark` is pinned at `deb9155`, dated
2026-05-04.** That pin is **correct and must not be moved**: rung V1 requires the benchmark at
a frozen commit so the 8-case scores recompute identically, and a moving scoring reference
would make every reproduction meaningless.

**But the frozen clone is not the rank oracle.** It scores; it does not rank. Those are two
different objects that live in the same file, and the README we froze for the first purpose
was silently serving as the source for the second. **A pin that is right for reproducibility
is wrong for standing**, and nothing in the record said which use each was for.

## 3. What this changes

**The rank-1 claim survives on the number.** Our 0.056647 is below 0.0580; lower is better.

**The margin does not.** Against the old leader (Reissmann, 0.0595) it was **0.002853**.
Against Yang it is **0.001353** — **less than half.** And the lab's own record already holds
that the lead over Reissmann was *not statistically decided*: paired per-case t = −0.495,
dispersion 5× the margin, 4 of 8 cases won. **A margin under half of an undecided one is, a
fortiori, undecided.** Nothing about that conclusion needs recomputing to be directionally
certain — though the figure itself does.

**`P(rank 1) = 68%` is stale.** It was computed by a 400k case-level bootstrap over a
**four**-entry board. There are six, and the new leader sits 0.0014 away. That figure is the
**mandatory caveat carried across nine files** wherever rank is claimed — so nine surfaces
now carry a number computed against a board that no longer exists.

**The V16 guard's board pin is stale, one screen above where seven rounds were spent.** The
guard validates placement sentences against `reissmann 1, wu 2, liu 3, montoya 4`. Live,
Montoya is **6**. So the guard would now **fault a correct sentence** saying so, and **pass**
a sentence saying Montoya is 4, which is no longer true. Seven grade rounds refined how the
guard reads a sentence; none asked whether the board it compares against was current. That is
L-39 exactly — verdicts age silently — and it is the same defect class the rung exists to
police, sitting one level up from the rung.

**A prior-art fact changed under the entry.** `CLOSURE_CHALLENGE_PRIOR_ART.md` §2.4 records
that **Tyler Buchanan and Richard Dwight are co-authors of the Closure Challenge paper
itself**, and flags it as mattering *"for how the entry is written."* They now hold a scored
board entry at rank 4. Nothing about that is improper on an open benchmark — but it is a fact
the entry's prior-art section and the Buchanan-coefficients firewall were written without.

## 4. What must NOT be done in response

- **Do not move the frozen scoring pin.** V1 depends on it. If a rank check needs the live
  board, it fetches the live board and says so.
- **Do not re-run the bootstrap and quietly replace 68%.** The figure is load-bearing across
  nine files, and a number replaced without its frame is how this corpus drifts. Recompute it
  **against the six-entry board, with the frame stated**, and move all nine together — that
  lockstep requirement is already recorded as the highest-risk duplication in the corpus.
- **Nothing is sent, filed or registered.** Submissions are PARKED and reserved to Katie.
  This document reports a change in the world, not a response to it.

## 5. The generalisable finding

**A record that is correctly frozen for one purpose becomes silently wrong when read for
another.** The clone is not stale — it is *pinned*, deliberately, for a reason that is still
valid. Nothing was neglected. The defect is that one artifact served two purposes and only
one of them wanted a frozen answer, and no sentence anywhere said which.

**The check that would have caught it costs one fetch**: compare the live board against the
pin, on a schedule, and alarm on any difference. That the lab spent seven grade rounds
perfecting how a guard reads a placement sentence, while the board underneath it changed
without anyone looking, is the argument for spending the next hour on freshness rather than
on precision.

## Related

- `demo-output/website/campaign/PROBABILITY_OF_RANK_2026-08-10.md` — the 68% figure and its home.
- `demo-output/website/CLOSURE_CHALLENGE_PRIOR_ART.md` §2.4 — the Buchanan/Dwight co-authorship note.
- `scripts/self_audit.py` — `check_board_placement_words` and its board pin.
- `LESSONS.md` L-39 (verdicts age silently), L-75 (frames), L-79 (quoted figures rot).
