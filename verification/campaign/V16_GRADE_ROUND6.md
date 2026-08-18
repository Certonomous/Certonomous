# V16 — grade round 6

**Grader:** an agent that wrote none of this code.
**Subject:** commit `72609a04`, which is also repo `HEAD`.
**Board:** read from the benchmark README pin — Reissmann 1, Wu 2, Liu 3, Montoya 4.
**Suite:** `sdk/tests/test_rank_claim_surfaces.py` — **92 passed** in 462.64 s at `72609a04`.
**Probes:** all executable, at `campaign/V16_GRADE_ROUND6_PROBES.py`; assembled at import so
neither that file nor this one contains a placement the guard can match (docket D4).

## Subject assertion

`git merge-base --is-ancestor 72609a04 HEAD` → **ANCESTRY OK**, and the content check —
`git diff 72609a04 HEAD -- scripts/self_audit.py sdk/tests/test_rank_claim_surfaces.py
campaign/V16_GRADE_ROUND5_PROBES.py` — is **empty**. `git rev-parse HEAD` is
`72609a04e9523d1c8670704dfb0ec98a0e6d380a`: the subject *is* the checkout, not merely an
ancestor of it. Not in a worktree, by the supervisor's stated departure from R-ISOLATE.

## The author's claim, recomputed first

`V16_GRADE_ROUND5_PROBES.py` run against the live guard: **0 of 20 disagree**, with all twelve
drift entries present — the twelve that had to start passing did, and the eight controls held.
The author's headline reproduces exactly. Everything below is what execution found beyond it.

## Verdicts on the five declared items

| Item | Round 5 | Round 6 |
|------|---------|---------|
| **E1** skip-is-not-agreement | CLOSED | **CLOSED** (unchanged code) |
| **E2** linear-algebra homonym discriminator | NOT CLOSED | **NOT CLOSED** |
| **E3** rule B's recompute | CLOSED | **CLOSED** (unchanged code) |
| **E4** sentence-boundary bind | NOT CLOSED | **CLOSED for the declared defect**, with a regression filed |
| **L-76** absolute sweep | CLOSED | **NOT CLOSED** — re-opened by this round's own added lines |

### E1, E3 — CLOSED, by content rather than by re-execution

Round 5 closed both by execution. This round did not change the code they were closed against:
`check_board_placement_words`, `_place_unnamed`, `_place_reach_sentence`, `_place_family_count`,
`board_placement_faults` and `_published_board` are **byte-identical** between `1393b8b4` and
`72609a04` (compared by extracting each function body from `git show` at both SHAs). The whole
`self_audit.py` diff falls inside `_placements`, `_place_linalg_subject` and the placement
constants. Re-executing a mutation matrix over unchanged code would have tested this round's
`git show`, not this round's work.

### E2 — NOT CLOSED

The fourth discriminator fixes the four shapes round 5 filed and breaks on a fifth. The stated
rule is *the head of the grammatical subject*; the implementation reaches that head through two
word lists, and both have edges that fall in the **false FAULT** direction — the expensive one,
since a rule-A fault on a travelling surface is FAIL severity.

Seven probes, `E2 *` in the probe file, all wanting **silent** and all observed **FAULT**:

| shape | why it inverts |
|---|---|
| reduced relative clause ×3 | English drops the relativizer in an object relative. With no `_PLACE_POSTMOD` marker in the clause, no cut is made, and the later-noun tie-break resolves to the entrant, who follows the head. The round-5 shape the repair fixed becomes a false fault again when **one word is deleted from it**. |
| head noun off `_PLACE_LINALG_NEAR` ×3 | The clause cuts correctly, and the head then contains no listed object, so the discriminator declines to mute and the entrant in the postmodifier binds. |
| coordinated subject ×1 | Both conjuncts are objects; the entrant appears only as a genitive determiner inside the second. Resolves to whichever sits later, which is the entrant. |

Six controls hold, including the round-5 shape **with** its relativizer, a head noun that *is* on
the list, the fronted-modifier case, and a plain wrong placement that must still fault — so this
is not a wedged guard.

**The author's stated cost is understated, and this was the specific claim to test.** The comment
says the heuristic *"has three known blind spots, none of which is a false FAULT"*. Executed, the
first (head noun on neither list) and the third (coordination) **both produce false FAULTs**;
only the second, the fronted modifier, behaves as declared. The reduced relative is a fourth
blind spot and is not on the list at all.

These seven are **not** regressions: `1393b8b4` faults all seven too. What the round changed is
the claim made about them.

### E4 — CLOSED for the declared defect; a regression filed

The declared defect is closed on execution: all six shapes that bound across a full stop are
silent, and **both** over-fix controls hold — the guard still binds with no boundary and still
binds in the sentence after a stop. Appending a constant instead of a real character is the right
shape of fix and it works.

The constant is unconditionally uppercase, so it closes the boundary after **every** full stop
plus space — including one that ends an abbreviation rather than a sentence. Old vs new in one
invocation, `__pycache__` cleared first: an abbreviation followed directly by a bare ordinal, and
by an ordinal-plus-noun, **faulted at `1393b8b4` and are silent at `72609a04`**. Both are real
wrong placements, now missed. The direction is the cheap one — a missed fault, not a false one —
but the comment that makes the trade states *"the character's identity was never doing any
work"*, and on this class it was doing exactly one job: separating an abbreviation-final period
from a sentence-final one. Filed as **docket D24**.

### The subject-NP fallback — a new false-FAULT class, introduced by this round

The fallback's comment states: *"This cannot reach across a sentence: the phrase is cut at
`_PLACE_CLAUSE` first."* `_PLACE_CLAUSE` is `[.!?;:]`, and the surface's whitespace is collapsed
before any of this runs. So what the fallback cannot cross is a **punctuation mark**, not a
sentence — and a markdown heading, a list item and a table cell each end without one. This
corpus is markdown.

Three probes, `FB across *`, each binding an ordinal to an entrant named in the **previous
structural unit**, at gaps of 65, 69 and 54 characters against a `_PLACE_BIND` of 40 — so the
ordinary bind is not what fires. All three are **silent at `1393b8b4` and FAULT at `72609a04`**:
this is a regression the round introduced, not an inherited defect. Four controls hold: the same
gap with a full stop present is silent, the same with a semicolon is silent, and both round-5
false negatives the fallback was added for still fault — so the finding is not a demand to delete
it.

### L-76 — NOT CLOSED, re-opened by this round's added lines

L-76 sweeps the rung's **added lines** for absolutes asserting a safety the code does not have.
Round 5 swept the lines standing at `1393b8b4` and found none; that verdict was correct for that
line set. This round added ~143 lines to `scripts/self_audit.py`, and three of the absolutes in
them are falsified by the executions above:

| absolute, in the round's own added lines | executed verdict |
|---|---|
| "three known blind spots, **none of which is a false FAULT**" | false — two of the three are |
| the fallback "**cannot reach across a sentence**" | false — three markdown shapes cross one |
| "the character's identity **was never doing any work**" | false — it separated abbreviation periods from sentence periods |

Each is in the overclaim direction, which is the direction L-76 exists to catch. The item does
not close at this SHA.

## Round 5's causal story, checked

The author corrected round 5 on *why* the two E2 false negatives were silent, writing that both
*"stay silent with the linear-algebra discriminator answering correctly"* and that *"distance was
not what muted them."* Executed against `1393b8b4` — the build round 5 graded —
`_place_linalg_subject` returns **True** for both shapes, which is the `continue` that discards
the placement **before the bind loop is ever reached**. At the graded build the discriminator was
what muted them, exactly as round 5 said; the correction is true only of the repaired build,
where the discriminator now returns False and `_PLACE_BIND` takes over. **The previous grader's
causal story was right and the correction is wrong** — though the repair it justifies is needed
regardless, which the same execution confirms.

The two figures in that correction **do** reproduce: the entrant sits **69 and 73** characters
from the ordinal measured from the name's *first* character, which is the governing frame, since
`_PLACE_BIND` slices `left[-40:]` and the whole match must fit inside it. Measured end-to-start
the gaps are 62 and 66; the author used the right frame.

## Calibration — every finding here is latent, checked independently

The author's corpus claim was not read, it was recomputed. Both modules were loaded side by side
(`72609a04` and `1393b8b4`, the older one with `REPO`/`_BOARD_PIN` repointed so it reads the same
board — asserted equal before the sweep) and `board_placement_faults` was run over every tracked
path with **Python's** open, UTF-8, ≤ 4 MB — not the shell's `grep`, which is `ugrep
--ignore-files`:

- **20,591** tracked paths, **18,874** opened;
- rule-A faults: **1** old, **1** new. Rule-B faults: **1** old, **1** new;
- **surfaces whose fault list changed old → new: 0.**

So the author's "0 surfaces changed verdict" reproduces, and the fallback regression found above is
latent too. The live guard at `72609a04` is **WARN**, *"every travelling surface agrees with the
board; 2 lab record placement(s) do not"* — both in `docs/INSTRUMENT_INTEGRITY_LEDGER.md`, the
known quotations of docket D3, and consistent with the sweep's 1 + 1. **No published figure moves
on any finding in this grade.** Latent is not harmless: each finding falsifies a written claim
about the guard, and three of them are in the false-FAULT direction, which is FAIL severity on a
travelling surface.

## R-VALUE

| finding | material or residual | why |
|---|---|---|
| E2, seven false-FAULT shapes | **material** | Deleting one word from a shape the repair fixed restores a FAIL-severity false fault on ordinary English; a reader told the discriminator is anchored to the grammatical subject would revise. |
| The blind-spot claim is false | **material** | The claim was the round's own statement of what it knowingly kept; two of three items on it are the expensive direction. |
| Fallback crosses unpunctuated boundaries | **material** | A new false-FAULT class **introduced by the round under grade**, in the shape the corpus is mostly written in. |
| L-76 re-opened | **material** | The three absolutes are the written record itself. |
| E4 abbreviation regression | **material, secondary** | A behaviour regression from the previous round that the author's own controls did not detect; alone it would be a residual, since the direction is silent. |
| Causal correction is wrong | **residual** | Changes what a reader believes about a comment's provenance, not about what the guard does; the repair it justifies is correct. Docket **D22**. |

Four material findings, so this round did **not** return only belief-neutral findings and the
R-VALUE counter does not reach two. **V16 does not close on this round.**

This is not "a grader who can only ever find more". Two of the four are things the round itself
put into the tree: a regression it introduced and three absolutes it wrote. The E2 finding is the
one the rung has now seen four times, and the honest summary is that a word-list stand-in for a
parse will keep producing a fifth sentence — which is a reason to **change the shape of the
claim** rather than the shape of the heuristic. What would close E2 next round is not a fifth
discriminator: it is either a real parse, or a stated precision figure beside the four recall
figures (docket D20) with the false-FAULT classes enumerated honestly, so the guard stops
claiming a discriminator it does not implement.

## Docket filings

Highest existing ID in section D checked before picking: **D21**.

- **D22** — a comment's stated cause for a repair contradicted by executing the build it describes.
- **D23** — whitespace collapse makes markdown structure invisible to every clause-boundary rule
  in the guard, so "cannot cross a sentence" means "cannot cross `[.!?;:]`".
- **D24** — the boundary probe cannot distinguish an abbreviation-final period from a
  sentence-final one, in either the old or the new form.
