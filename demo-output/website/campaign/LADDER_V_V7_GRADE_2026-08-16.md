# Ladder V rung V7 — grade of the `D328` repair, by a non-author of both the ruling and the repair

**Frame pinned in argv: `d0e90c3f`** (the `D328` repair commit). HEAD had advanced to
`371be610` during the pass; ancestry was confirmed (`git merge-base --is-ancestor d0e90c3f
371be610` returned true) and the three files this grade turns on were compared byte for byte
across the two frames — `sdk/scripts/closure_criterion_on_test_features.py`,
`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md` and
`demo-output/website/closure_challenge_criterion_test_case_table.json` were **identical at both**
(sha256 of each blob equal), so the move did not touch what was graded. The two intervening
commits (`97a0418e`, `371be610`) touched `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` and
`docs/DOCKET.md` only.

**No scoring call was made by this pass. The ledger was not touched and stood at 6.**

---

## VERDICT: `FAIL`

Not because the repair was wrong — **both repaired instances were verified correct** — but
because V7's conjunct says **`all`**, and at `d0e90c3f` **three further in-class count claims
stood unreconciled**, all of them the same sentence `:248` generates, on surfaces the repair's
re-sweep could not reach.

---

## 1. The criterion, quoted from where it was found

Located by search rather than by an inherited citation, at
`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md:336` (frame `d0e90c3f`), inside
the PASS 2 block:

> **V7. Kill the two known defects and prove it**: the false docstring sentence corrected (and a
> grep for any other count claims about scoring calls, all reconciled against actual call sites);
> the submittable artifact assembled to the accepted format …

**`all` is the criterion's own word. There is no tense clause and no era clause**, and the grep is
unqualified as to directory — it says *"any other count claims"*, not *any other count claims in
`sdk/`*.

## 2. Both repaired instances — tested, and both correct

| instance | how tested | result |
|---|---|---|
| `sdk/scripts/closure_criterion_on_test_features.py:10` | detector over the file blob at `d0e90c3f` | **RECONCILED** — era anchor and live count both inside the claim's own sentence-plus-parenthetical scope |
| `:248` | **AST-rendered**, then detected on the rendered string | **RECONCILED** — same |

`:248` could not be graded from source: the claim is split across f-string concatenation
(`… a further "` / `f"official scoring call …`), and the joiner between `further` and `official`
contains `"` and `f`, which no `[-\s]` gap can cross. Reading it required the rendered form. The
escaping was **read back rather than assumed**: the literal `"a 5th"` was present in the rendered
text at offset 2303 and **no backslash survived into it**.

Rendered text, as it travels into output:

> Zero cases warrant a further official scoring call on this evidence ("a 5th" as this
> round-3-era script was written; the cumulative count is six after round 5's 2026-08-07 call, so
> the next one would be the 7th).

The docstring's year count over lines 1–14 was confirmed moved to **1** (and to 1 over `D284`'s
narrower 1–12 window as well). The treatment matches
`sdk/scripts/export_closure_submission_csvs.py:31` and `sdk/scripts/closure_round4_manifest.py:137`
as claimed — matched, not invented.

## 3. What the repair's re-sweep could not see

`D328` recorded the class as **re-swept "over 258 tracked `sdk/` files"**. The criterion's grep is
not scoped to `sdk/`. The sentence `:248` exists to emit lands in
`demo-output/website/closure_challenge_criterion_test_case_table.json` — the generator names that
path at its own line 78 — and that path is **outside the re-swept set by construction**. The
finding that made `:248` the more serious of the two, in `D328`'s own words, is that **it travels
into output**; the output it travelled into was not examined.

### The three unreconciled instances standing at `d0e90c3f`

All three name a **5th** against a ledger of **6**; the next call would be the **7th**. Off by two
— the identical arithmetic `D310` ruled on.

1. **`demo-output/website/closure_challenge_criterion_test_case_table.json:126`**, at JSON path
   `/verdict/statement`: *"… Zero cases warrant a 5th official scoring call on this evidence."*
   The only era anchor in the file (`generated_at`, `2026-07-29`) sat at **line 2, 124 lines
   away**, in a different structural scope — which is the same "anchor sits in a different
   paragraph" measurement `D310` made against `:10`.
2. **`demo-output/website/ACTIVE_RESEARCH.md:880`**: *"**Zero cases warrant a 5th official scoring
   call on this evidence** -- the criterion changes nothing about the current entry."* This sat
   under the heading **`### Where we actually stand`** (line 705) — a section stating where the
   ledger stands, which is precisely `D310`'s second category.
3. **`demo-output/website/CLOSURE_CHALLENGE_STATUS.md:389`**: *"**Zero cases warrant a 5th official
   scoring call on this evidence** — a negative result, reported as such, costing nothing to have
   checked."* Under `## 0d`, no date in the header, no anchor in scope.

Noted and **not** counted: `CLOSURE_CHALLENGE_STATUS.md:378` carries the same claim inside a
blockquote and the discriminator returned `MENTION (the claim itself is set off: blockquote)`. It
was left on the mention side rather than argued across.

### Why the "it is a frozen dated record" defence does not reach these

It is the defence `D310` destroyed, and the corpus answers it twice over:

- The reconciling treatment **does not rewrite the historical claim**. It quotes the original
  ordinal and adds the scope beside it — *"'a 5th' as this round-3-era script was written; the
  cumulative count is six"*. Byte-intact history and reconciliation are not in tension; the
  corpus's own form was built to satisfy both.
- The JSON already carries an **appended-correction mechanism** in active use:
  `verdict.statement_correction_2026_08_02` corrected a different false clause of the very same
  statement while leaving the statement byte-intact, on the stated ground that *"records are not
  rewritten here"*. A surface that can carry one appended correction can carry another.
- The lab's own standard for **this exact sentence** was written at
  `CLOSURE_CHALLENGE_STATUS.md:380-385`: the 2026-08-02 withdrawal was applied to the JSON **and**
  to the generator *"so that the sentence is not left standing on a surface this one does not
  reach."* `D328` applied the count reconciliation to the generator alone.

## 4. Independent class re-sweep — measured, not inherited

Run at `d0e90c3f` over blobs read through one `git cat-file --batch`, never the working tree.

| scope | files read | past file pre-filter | recogniser (superset) | in class | survivors before adjudication |
|---|---|---|---|---|---|
| `sdk/` only | 303 | 173 | 111 | 46 | 40 |
| whole tracked corpus | 19286 | 2062 | 887 | 385 | 309 |

Restricting the survivors to the **V7 class proper** — a claim naming an *ordinal position* in the
ledger, as against a script stating its own non-call — left **85** to read. All 85 were read.

`D328`'s **7 survivors were tested rather than inherited, and all seven were confirmed out of
class**, on the grounds `D328` gave: `closure_decline_gate_audit.py:40`,
`closure_duct_feature_degeneracy.py:57`, `build_master_table.py:29` and `:213`,
`closure_round5_qcr_forward.py:236` each state a script's **own non-call**;
`train_closure_extended_correction.py:416` describes **the call it itself makes** and is `D310`'s
positive example of the rule, not a violation; and
`sdk/tests/fixtures/absolute_claims_labelled_second_instance.json:746` is a **labelled test
fixture** quoting the first of those as sample data, out of class twice over. **The disagreement
with `D328` is not about these seven. It is about the three surfaces its scope excluded.**

The other 78 ordinal-position survivors resolved into four out-of-class groups, each read:
records whose count is **already correct at six**; records describing **their own call** with a
bare ordinal (`apply_closure_ph_gate.py:38` "4th", `closure_round4_duct_rescale.py:38` "#5",
`CLOSURE_CHALLENGE_STATUS.md:516` round 4's own 5th with its era scope in the same sentence);
**grading records quoting a claim in order to fault it**; and
`closure_challenge_R5_ALPHA05_REGIME_PREREGISTRATION.md:62`, a dated, explicitly counterfactual
pre-registration of a route its own section heading records as one that *"will not run"*.

`demo-output/website/closure_challenge_submission_round4/MANIFEST.json:9` carried *"five distinct
prediction sets scored, ever"* while its generator `closure_round4_manifest.py:137` had been given
the era treatment at `49f71b8c` — the same generator/artifact split. It was adjudicated **out of
class** as a delivered, hash-asserted package artifact of a superseded round whose integrity
depends on byte-stability, and is **filed, not appended**.

## 5. What the pre-filter provably supersets

Two filters, applied one **on top of** the other rather than folded together, so the superset
property stays auditable:

- **Recogniser (`CALLNP`)** — an ordinal/count token, a `[-\s]{1,20}` joiner, up to three filler
  words, then a noun phrase. **Every alternative of that noun phrase contains `scoring`,
  `prediction set`, or `call`**, and this was **machine-checked at every run** by
  `assert_superset()`, not asserted in prose. The bare `call`/`calls` alternatives were kept
  deliberately loose — they also match *Claude call*, *call site*, *per-call*, *function call* —
  because that looseness is what makes the superset provable.
- **In-class filter**, applied to the recogniser's output: a genuine count token, plus a noun
  phrase drawn from the narrower `scoring call` / `official call` / `prediction set(s) scored`
  list.
- **File-level pre-filter**: the char-gapped disjunction of exactly `scoring`, `prediction set`,
  `call`. Since every in-class noun phrase contains one of those three literals, **a file it
  rejects cannot contain an in-class hit**. It is char-gapped for the same reason the noun phrase
  is — a hyphen-split wrap would otherwise hide a whole file.

## 6. Controls — readbacks, and kind proven from evidence

Planted **by line index** into a scratchpad copy of `CLOSURE_CHALLENGE_STATUS.md` and read back
**by slicing at that index**, with `readback == payload` and `readback.encode() ==
payload.encode()` asserted on every plant. The plant line was **pre-checked to contribute zero
hits at baseline** (line index 2), so a plant could actually move the count — the failure mode
that silently voided two controls earlier in the evening.

Baseline 13 hits. All six positive forms fired at 14:

| form | fired |
|---|---|
| `a 5th official scoring call` | yes |
| `the fifth scoring call` | yes |
| `four prediction sets scored` (ledger phrasing) | yes |
| hyphen-split across a wrap (`scor-\ning`) | yes |
| emphasis-split (`**5th official scoring** call`) | yes |
| blockquote wrap (`> … 5th official scoring` / `> call …`) | yes |

Two negative forms were correctly rejected. **Struck negative control at zero gain**, run both
ways on the same sentence: **unstruck gain 1, struck gain 0**.

**Kind: `RECOGNITION`**, *derived* by `scripts/control_kind.py` from the evidence and never typed
as a label — *"6 mutually independent forms in the vocabulary of 'official scoring-call counts',
all found; 2 negative form(s) correctly rejected"*.

**The instrument was twice reported BROKEN by its own controls before it was trusted**, and both
times the control was right:

1. The hyphen-split form was missed, because the noun `scoring` itself was split (`scor-\ning`)
   and `\w` cannot cross a hyphen. Fixed by bounding **every gap inside a word** by characters,
   not only the gaps between words — and the in-class filter had to be char-gapped too, or the
   hit was recognised and then silently dropped from the class one step later.
2. The ledger-phrasing form was missed, because a plain leftmost-match `finditer` let the
   superset's looser ordinals swallow the start of a phrase and **block the tighter in-class match
   behind them** — `Only four prediction sets scored` matched at `Only`, failed the count-token
   test, and the real claim at `four` was never offered. Fixed by anchoring a candidate at every
   ordinal position and deduping by end offset.

Both were caught only because `control_kind.py` refuses to promote a control that did not fire,
and both would have produced a false zero.

**Polarity control**, one sentence carrying two clauses of opposite polarity — *"This warrants a
5th official scoring call, **not** a 6th official scoring call."* — returned **2 distinct clause
scopes where the sentence scope returned 1**, with `neg` separating `False`/`True` across them. The
single-polarity control returned 1 and 1: it **passes both detectors and would have certified the
defect**, so it was not relied on alone.

**Anchoring control**, run separately because the two scopes are not the same instrument: on the
repaired sentence, whose era anchor is written as a **parenthetical**, sentence-plus-parenthetical
scope returned `anchored=True, live=True` while **clause scope returned `era=False`** — reproducing
exactly the defect `D328` hit when its anchor test inherited clause scope and reported its own
repair as unreconciled. Clause scope cuts at `(`; era anchors are routinely parentheticals.

All blanking was **offset-preserving** — markers overwritten with spaces in place, same length,
newlines untouched — with strike spans blanked **first** and tracked, then continuation prefixes,
then emphasis (never `~`, never `_`). Every quotation and offset in this document was taken from
the **unmodified** original.

`scripts/use_mention_discriminator.py` was used with the **claim span supplied**, never guessed.
**No `CANNOT_TELL` was promoted to `ASSERT`.** Where the instrument returned `CANNOT_TELL` or a
`MENTION` driven by bold emphasis rather than attribution, the finding was hand-adjudicated with
written grounds, above, and the verdict does not depend on any such promotion: instance 1 — the
emitted JSON — carries the grade on its own.

## 7. The struck row clause on V7

Confirmed at `d0e90c3f`, and **correct on both counts**:

- The strike sits on the clause *"`sdk/scripts/closure_criterion_on_test_features.py` carries TWO
  unreconciled ones"* inside the row's **evidence** cell, and is labelled in place —
  *"struck 2026-08-16: BOTH REPAIRED, and this strike records a REPAIR, NOT A GRADE"*, with
  *"THE VERDICT CELL IS DELIBERATELY LEFT AT `FAIL`"* stated in the same parenthesis.
- **The verdict cell was not altered.** It read
  `~~**PASS** — three, not the two we knew~~ **→ `FAIL`, 2026-08-16, ruled by a non-author**` at
  `41ec5a8b`, at `d0e90c3f`, and unchanged at `371be610`.

Striking it was right: had that clause been left standing after the two repairs it would itself
have become the stale-claim class V7 exists to catch.

## 8. Not repaired here

**A grader may not repair what he grades.** The three instances at §3 were left exactly as found.
They are the repair owed to V7 by a non-author of this grade.
