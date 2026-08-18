# Ladder V — V7 ruled by a non-author: the judgement does not hold, and the rung fails on its own criterion

**Ruling: the two sentences are the SAME SHAPE and got OPPOSITE treatments. `D284`'s inconsistency is
real. V7: `FAIL`.**

The peer who filed `D284` measured the inconsistency and deliberately did not rule on it. This is
the ruling. It is made against V7's criterion **as written**, and it does not rest on tense, on
era-scoping, or on any distinction the criterion does not contain — because the decisive evidence is
that **the lab applied the fix to a same-era sibling of the sentence it left alone.**

**Independence.** This grader wrote none of V7, none of `49f71b8c`, none of either script, and none
of `D284`. Independence rests on the untracked dispatch record, not git authorship (D130).

---

## 1. V7's declared criterion, quoted from its face

`LADDER_V_TRIPLE_VERIFICATION.md:335-336`:

> **V7. Kill the two known defects and prove it**: the false docstring sentence corrected (**and a
> grep for any other count claims about scoring calls, all reconciled against actual call sites**);
> the submittable artifact assembled to the accepted format…

Two conjuncts. The second is the one at issue and it is unusually explicit about its class: **"any
other count claims about scoring calls"**, and the test is **"all reconciled against actual call
sites."**

**The criterion contains no tense clause, no era clause, and no historical-prose exemption.** A
sentence naming a number of scoring calls is inside the class by the criterion's own words, and the
test it must pass is reconciliation against the actual count.

**The actual count, read from the record rather than recalled:**
`closure_challenge_round5_qcr.json` → `scoring_calls.cumulative_distinct_prediction_sets_scored`
= **6**, history *"floor, round 1, round 2, round 3, round 4, round 5"*. **The next call would be the
7th.**

---

## 2. The two sentences, measured side by side

| | **A — FIXED** `closure_round4_manifest.py:135` | **B — LEFT** `closure_criterion_on_test_features.py:10` |
|---|---|---|
| text | *"The lab's ledger (five distinct prediction sets scored **as of this round-4 manifest; six after round 5's 2026-08-07 call**) is a self-imposed discipline…"* | *"Whether to spend **a 5th official scoring call** on anything this table shows **is** explicitly the coordinator's decision, not this script's."* |
| states a scoring-call count | yes | yes |
| tense | present (*"is"*) | **present** (*"is"*) |
| year or date in the sentence | **yes, after the fix** | **no** |
| year anywhere in the docstring | n/a | **none** — `grep -cE "20[0-9]{2}"` over lines 1–12 returns **0** |
| era anchor in its own paragraph | **yes, after the fix** | **no** — the *"round-3 gated entry"* anchor sits in paragraph 1 and scopes what the TABLE describes; the claim is in paragraph 2, which names no round |
| does the script make the call it names | no | **no** — its own docstring: *"no `closure_challenge.score()/evaluate_by_case()` call is made"* |
| reconciled against actual call sites | **yes** | **no — off by two.** Names a 5th; 6 were made; the next is the 7th |
| last changed | fixed at `49f71b8c`, 2026-08-08T02:08:13Z | sentence unchanged since `09d0afc1`, **2026-07-29**; file since 2026-08-02 |

**Both were false at the same instant.** The 6th call landed at `e865076b`, 2026-08-07T20:38:52Z. The
pass that fixed A landed at `49f71b8c`, 2026-08-08T02:08:13Z — **5 hours 29 minutes later**. At that
moment B had already been wrong for the same 5h29m. This is not the world moving after delivery: **one
pass, one instant, two sentences of the same class, opposite treatments.**

**And there are TWO instances in B's file, not one.** `D284` names `:10`. The sweep also returns
`:248`, inside an emitted JSON verdict string: *"Zero cases warrant a **5th official scoring call** on
this evidence."* That one travels into a written record rather than staying in a docstring.

---

## 3. The measurement that decides it: a same-era sibling got the fix

The defence recorded for B is *"historical tense"* — a round-3-era script describing a round-3-era
deliberation. **The corpus refutes that defence directly.**

`sdk/scripts/export_closure_submission_csvs.py:31-33`, at HEAD:

> *"The lab's scoring-call ledger (**"four official scoring calls, ever" as this round-3-era script
> was written; the cumulative count is six after round 5's 2026-08-07 call**) is a SELF-IMPOSED
> discipline…"*

**That is a round-3-era script — B's own era — and it names an even older count, four.** It was given
*exactly* A's treatment: the era made explicit **inside the sentence**, and the live count appended.
So "round-3-era prose is historical and needs no scoping" is not a rule this lab follows. It is a
rule applied to B and to nothing else of its kind.

### The rule the corpus actually follows, read off five sites

Sweeping V7's own class across the tree produces a coherent distinction, and it is not tense:

* **A script describing the call IT ITSELF makes keeps a bare ordinal** — a record of an action
  performed. `apply_closure_ph_gate.py`: *"That is the 4th official scoring call … (after the floor,
  round 1, and round 2)"*. `closure_round4_duct_rescale.py`: *"official call #5"*. Correct as written
  and correctly left alone.
* **A script stating WHERE THE LEDGER STANDS gets era-scope plus the live count** — the manifest
  (A), `export_closure_submission_csvs.py` (C), and `closure_round5_qcr_forward.py`, which is the
  cleanest of all: *"as of THIS SCRIPT'S RUN (2026-08-07, before the call) the ledger stood at 5
  distinct prediction sets scored. **Scoped to its own run because…**"*

**B is in the second category and cannot be in the first, because B makes no call at all.** It does
not record a call; it states what the *next* call would be, which is a claim about the ledger's
standing. It did not get the second category's treatment. **That is the inconsistency, and it is not
a matter of judgement about tense — it is the lab's own practice applied unevenly to two members of
one class.**

---

## 4. The instrument: a recognition control, and a pre-filter that provably supersets

**A literal generator-string search is exactly what V7's original pass did**, so repeating it would
repeat its blindness. The recogniser matches the class — a number adjacent to a scoring-call noun
phrase, in either order — with every gap bounded by characters rather than by `\w+` token
repetition, **because `\w` cannot cross a hyphen**; that is the defect that returned `BROKEN` on the
peer's own V7 sweep at *"pre-registered"*, and it is the defect my V9 recogniser had at
*"data-driven"*.

**Control kind: `RECOGNITION`, derived by `scripts/control_kind.py` and not declared.** Six mutually
independent planted forms, all found — `a 5th official scoring call`; `the fifth scoring call`;
`five distinct prediction sets scored`; `scoring calls made to date: 4`; a form **wrapped across a
line break** (`a 5th official scoring\ncall on anything this table shows`); `the ledger stands at six
scoring calls`; `seven scoring-call budget` (hyphenated). **Two negative forms correctly rejected** —
*"a fifth place finish in the race"*, *"five cases were scored by the harness"* — so the pattern is
not merely loose.

### `\s+` does not reach a wrap across a blockquote prefix, and my first pass had this wrong twice

**`>` is not whitespace.** A clause wrapping as `` are `not `` / `` > statistically decided`; `` has a
newline **and a `>`** between the words, so a literal space misses it and **`\s+` misses it too**.
Measured elsewhere in this lab on `LADDER_V_PASS3_COLD_2026-08-11.md:465`, where a sweep reported a
clause absent at a site that states it plainly. This corpus is largely blockquoted rulings, so the
exposure is wide.

**Repaired here by stripping line-continuation prefixes FOR DETECTION ONLY** — leading `>`, nested
`> >`, list markers, heading marks — never altering quoted text or offsets. **The repair's own
control**, planted and read back:

| planted form | `\s+` only | prefix-stripped |
|---|---|---|
| `> Whether to spend a 5th official scoring` / `> call on anything…` | **MISSED** | found |
| `> > the ledger stands at six scoring` / `> > calls, ever` | **MISSED** | found |
| `- five distinct prediction` / `  sets scored to date` | found | found |

**And it corrected my pre-filter, which was not the superset I claimed.** The first pass filtered on
`scoring|prediction[ -]sets?|\bcalls?\b` and kept **568** paths. `prediction[ -]sets?` is a **two-word
phrase**, so a blockquote wrap between `prediction` and `sets` would defeat the filter itself — the
silent-zero shape one level up from the sweep. **Corrected to single tokens only,
`scoring|prediction|calls?`, which a wrap cannot split**, and the filter now keeps **937 paths, 369
more than the claim I first published.**

**What the pre-filter provably supersets, restated so it is checkable:** every alternative in the
recogniser's `CALLNP` noun phrase — `(official )?scoring[-\s]calls?`, `scoring[-\s]call \w+`,
`prediction sets? scored`, `calls? (made|scored|spent|used)`, `distinct prediction sets?` — contains
the **single token** `scoring`, or `prediction`, or `call`. Single tokens are the load-bearing part:
a wrap can split a phrase but not a word. **So no text the recogniser could match can fail the
filter.**

Blobs were read through **one `git cat-file --batch`** rather than one subprocess per file, after a
per-file version timed out twice. Strike spans blanked in place, offsets preserved.

**Result at HEAD: 694 claims in 132 files** (the first pass under-reported this as 637 in 130,
because of the narrow pre-filter). **The prefix-strip moved the corpus count 693 → 694 and gained
zero files** — that movement is the repair's control on real text rather than on a plant. The one
claim it revealed is in `campaign/LADDER_V_PASS2_2026-08-11.md`, inside **V7's own verification
record** (*"RUNG V7 … (a) The scoring-call count claims — full reconciliation Ledger: 6 cumulative …
Frame: I grepped code **and** records"*). It is a **mention**, not a new defect.

**The ruling's own evidence did not move under either normaliser** —
`closure_criterion_on_test_features.py` **4 hits both ways**, `closure_round4_manifest.py` **3 both
ways**, `export_closure_submission_csvs.py` **11 both ways** — so §2 and §3 stand unchanged, and the
verdict does not rest on the corrected figures.

---

## 5. The rung's citation is also about the wrong class

The ledger row reads, in full: *"**PASS** — three, not the two we knew | YES — two more stale
generator strings found later."* The peer measured those two: they concerned **best-on-board counts
and QCR attribution**, not scoring-call counts. **V7's declared class is scoring-call count claims.**
So the row's vindication is drawn from a different class than the one V7 was written to close, which
bears on what the rung is cited for. **The ruling above does not rest on this** — it rests on §3 —
but it is why the rung's PASS has looked better supported than it is.

---

## 6. Verdict

**V7: `FAIL`, 2026-08-16.**

V7's second conjunct required *"a grep for any other count claims about scoring calls, **all**
reconciled against actual call sites."* At the pass, and still at HEAD,
`sdk/scripts/closure_criterion_on_test_features.py` carried **two** unreconciled scoring-call count
claims, at `:10` and `:248`, each naming a 5th call when six had been made. They were not missed —
they were seen and waved through on a ground the lab does not apply to their same-era sibling.
**"All reconciled" was not met, and the word is the criterion's own.**

**What would close it.** Give `:10` and `:248` the treatment `export_closure_submission_csvs.py:31`
already carries — era-scope inside the sentence plus the live count — e.g. *"a 5th official scoring
call as this round-3-era table was written; the ledger stood at 6 after round 5's 2026-08-07 call, so
the next would be the 7th."* A writing task; no scoring call, no compute. **This grader did not make
it: a grader may not repair what he grades.**

**`PASS WITH RESIDUALS` is not a legal label** and was not used; it was withdrawn lab-wide at
`7c44cbe2`.

---

## 7. What this instrument still cannot see

* **Counts written without a scoring-call noun phrase** — *"the ledger stands at five"* with the unit
  established two paragraphs earlier would be missed; the recogniser needs the noun phrase in the
  window.
* **Counts stated only as digits in structured data** — a bare `"cumulative": 5` in JSON is caught
  only when a neighbouring key names the unit.
* **Counts in images, PDFs and the shipped archive** — not in frame here; `dist/` and
  `demo-output/website/latex/` were excluded by instruction.
* **Use versus mention.** Of the 694 claims, many are records *quoting* a count in order to correct
  it — including the single claim the blockquote repair revealed. They were separated by reading,
  which does not scale; the discriminator at `79e52dfa` is what a future pass should call, as `D286`
  already records.
* **Wraps across prefixes I did not enumerate.** The strip covers `>`, `> >`, list markers and
  heading marks. A wrap across a table pipe, a code-fence gutter, or an HTML tag between the words
  would still be missed, and I have not measured whether any exists.

---

*Non-author ruling on rung V7, in response to `D284`. Nothing graded here was repaired. No scoring
call was made and the ledger stands at 6; no solver was launched; nothing was submitted, uploaded,
registered or sent.*
