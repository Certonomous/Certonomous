# Ladder V, rung V7 — FIFTH GRADE, by a non-author

**Frame pinned in argv:** `678a69ab15ddc29da7e4b7f9690fdc8931617831`
**Graded:** 2026-08-17
**Standing of the grader:** non-author of the ruling, of every repair, and of
all four prior grades. `R-ISOLATE` applied. Nothing was repaired by this pass;
no scoring call was made by this pass.
**Measurement environment:** a clean detached worktree at the pinned frame, not
the live checkout. The live checkout's index carried a peer's staged work at
grade time (see §11); measuring dirty would have attributed it to this pass.

---

## VERDICT

# PASS

Both conjuncts of V7 were tested. The count-claim conjunct was reconciled at
every site the instrument returned; the artifact conjunct was re-measured from
the files rather than from a record of them.

---

## 1. The criterion, quoted from source

`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md:335-338`, read at
the pinned frame:

```
- **V7. Kill the two known defects and prove it**: the false docstring sentence corrected (and a
  grep for any other count claims about scoring calls, all reconciled against actual call sites);
  the submittable artifact assembled to the accepted format (1000×3, no header, one of the two
  accepted layouts, verified against an accepted submission in submissions/).
```

`all` was the criterion's own word. The clause carried **no tense clause, no era
clause, and no directory qualifier on the grep**. The scoring ledger stood at
**6** (chief-authorised): a live sentence naming a 5th was off by two, because
the next would have been the 7th.

## 2. The rule applied, from D310

**Authorship of the call decided the treatment.**

* A surface **recording the call it itself made** kept a bare ordinal —
  `apply_closure_ph_gate.py` ("4th"), `closure_round4_duct_rescale.py` ("#5").
* A surface **stating where the ledger stood** required **era scope plus the
  live count**. A document-level date alone had been rejected as insufficient
  three times before this pass.

## 3. The recogniser — built from the claim class, not from any prior grade

Each of the four prior failures was a **class boundary that excluded the defect
by construction**: an era clause; a directory scope (`sdk/` only); word
adjacency (`four-calls-ever`); a joiner pattern that a verb phrase
(`ledger stands at 5`) could not satisfy. A recogniser assembled from any of
those shapes would have inherited its blind spot, so none was reused.

**Stage 1 tested no relationship at all.**

1. Struck spans (`~~…~~`) were blanked **offset-preserving** first, so that a
   retracted claim did not fire while every reported offset still indexed the
   real file.
2. An anchor was placed on **every count token** — digit cardinal, digit
   ordinal (`5th`), number word, ordinal word, any case.
3. A **raw character window** of ±240 characters was taken around each anchor.
4. The window had to contain a **class root** (`scoring`, `scored`, `score`,
   `ledger`, `call`). `ledger` was carried as a class root and tested **only
   inside the window**.

A raw window has no grammar. It therefore has **no joiner boundary, no
adjacency requirement, no clause scope, no sentence boundary and no line
boundary** — the four shapes that killed the four prior grades cannot exist
inside it.

The in-class filter was kept **strictly on top** of this recogniser and was
never folded into it.

### 3.1 The recogniser was tested against the known sites before it was trusted

A filter that cannot re-find a site already known will not find one that is not.

| | result |
|---|---|
| known sites probed (every site repaired at `d0e90c3f`, `353191c7`, `8cefb4e9`, `6aedfcc9`, plus the four standing exemplars) | **21** |
| re-found by stage 1 | **21 / 21** |
| re-found by the in-class filter | **21 / 21** |

## 4. Corpus arm, and why it was drawn that way

**The whole repository at the pinned frame — 13,815 tracked paths, no directory
scope of any kind.** The criterion's grep was unqualified as to directory, and a
directory scope was precisely what sank the second grade. `dist/`,
`demo-output/website/latex/`, `motorbike-video/` and `LAPTOP_SHOOT.md` are
standing **write** prohibitions; they were **read** by this pass, because a
grader who does not look cannot certify.

| arm | files |
|---|---|
| tracked at the pinned frame | 13,815 |
| skipped as binary (a NUL byte present) | 1,107 |
| pruned as root-free | 10,529 |
| deep-scanned | 2,179 |

Two prunes were applied for speed. **Neither was a scope reduction, and each was
machine-checked on every run:**

* **Root-free prune.** A file containing no class root anywhere cannot contain a
  window that contains one. Machine check: *pruned files containing a class root
  = **0***.
* **Interval reformulation.** An anchor passes iff a root occurrence overlaps its
  window, so the token scan was run only inside the union of expanded root
  neighbourhoods. Machine check against the naive whole-file scan on all 1,963
  files under 400 kB: *divergences = **0***.

  This check earned its place. Its first run reported **2 divergent files**: the
  regions had been padded by `W+Lmax` on the left but only `W` on the right, so a
  token whose window reached a root far to its **left** could start inside a
  region and end past its right edge and be dropped. The padding was corrected
  and the sweep re-run to zero divergence. An unchecked optimisation would have
  silently narrowed the arm.

### 4.1 The binary skip was proven not to hide a site

Fifteen binary files carried a class root. Each was opened and tested directly:
**every one carried a single incidental substring (`call` or `score`) and zero
occurrences of any scoring-call phrase and zero occurrences of `ledger`.**

`dist/certonomous-demo.zip` was unpacked and read rather than assumed. Three of
its 103 entries carried a scoring-call phrase, and all three stated the **live**
count — "6 scoring calls", "Six scoring calls, ever", "six pre-registered
scoring calls". **No defect inside the bundle.**

## 5. Superset claim, and its machine check

**Claimed:** the stage-1 hit set is a **superset** of the hit set of every prior
grade's recogniser shape, so no site any of them could have found can be missed
here.

Each of the four shapes was re-implemented and run over the deep-scanned corpus,
and each match's count token was looked up in the stage-1 set:

| prior shape | matches | **not** in the stage-1 set |
|---|---|---|
| G1 — count + call noun, era clause excluded | 322 | **0** |
| G2 — count + call noun (the `sdk/`-scoped pattern) | 218 | **0** |
| G3 — count token immediately adjacent to the class noun | 159 | **0** |
| G4 — `[-\s]{1,20}` joiner only, no verb phrases | 276 | **0** |

## 6. Controls, each with a dark twin

**Hosts were selected by a rootless probe**, and the probe was **the dark twin
itself** — the plant with its class root deleted and every count token left at
the same relative offset. A host was accepted only where that probe stayed
silent.

This correction was forced by a measurement. An earlier probe used a *different*
rootless sentence, whose single count token sat at a different relative offset. A
host passed that probe and the dark twin then **fired** on its `4`, because a
character window reaches into neighbouring lines and the plant was sitting on
ambient text. A probe whose anchors are not co-located with the real plant's
anchors does not clear a neighbourhood.

| control | result |
|---|---|
| hosts offered | 755 |
| hosts accepted by the rootless probe | 6 |
| positives planted (12 forms × 6 hosts) | 72 |
| positives that fired | **72 / 72** |
| dark twins (root deleted) that stayed silent | **6 / 6** |

The 12 planted forms included one shaped like each boundary that killed a prior
grade — era clause, out-of-`sdk/` placement, `four-calls-ever` compound,
`ledger stands at 5` verb phrase — plus number words, ordinal words, digit
ordinals, a line-split claim, a parenthetical claim, a cross-sentence root, and a
root separated from its count by 200 characters. **Every one fired.** With the
dark twins silent, that is recognition, not proximity.

## 7. Triage, and the four expected instrument defects

| stage | count |
|---|---|
| stage-1 anchors | 78,615 |
| windows carrying `scoring`/`scored`/`score`/`ledger` | 28,375 |
| passing the grammar-free scoring-call designator | 15,871 |
| distinct (file, block) pairs | 2,267 |
| blocks carrying a tight scoring-call phrase and unreconciled **in block** | 291 |
| of those, a stale value within 120 characters of the tight phrase | **104** |
| **read individually and ruled** | **104 / 104** |

**Stage 2 never reused stage 1's window.** It read the **block** — the
paragraph, the enclosing JSON object, or the enclosing docstring. That mattered
concretely: in `closure_challenge_criterion_test_case_table.json` the claim and
its reconciliation sat **1,666 characters apart**, far outside any stage-1
window. An instrument that re-used the stage-1 window would have reported the
lab's own repair as unreconciled.

**Date tokens** (`2026-08-07` → `7`) and **round ordinals** (`round-3` → `3`)
were blanked before the stale-value test rather than dropped as anchors, so they
could not masquerade as counts while remaining visible as window context.

**Polysemy** was as expected. The corpus carries compute, cost, core-min,
mega-batch, fleet, integrity, agenda and backlog ledgers, and `ledger.txt` /
`ledger.csv` / `ledger.jsonl` files. The 686 blocks whose only designator was a
bare `ledger` were censused; the 55 that also carried closure-challenge scope
were read individually and were **entirely** polysemy, use/mention inside repair
and grade records, or correct live statements ("Ledger unchanged at 6", "the 6th
cumulative", "cumulative six stated").

### 7.1 How the 104 resolved

None was an unreconciled standing count claim. They fell into:

* **Event records keeping a bare ordinal, out of class on `D310`'s authorship
  ground** — `apply_closure_ph_gate.py` ("4th", and the
  `official_scoring_calls_this_lab_has_made_on_this_benchmark: 4` key it emits),
  `closure_round4_duct_rescale.py` ("official call #5", and its emitted
  `cumulative_distinct_prediction_sets_scored: 5`), the two entry-of-record JSONs
  those two scripts wrote, and `ACTIVE_RESEARCH.md`'s per-round chain (4th, 5th,
  6th — one entry per round, each recording that round's own call).
* **Reconciled in block, missed only by a conservative marker regex** — e.g.
  `CLOSURE_CHALLENGE_STATUS.md:1139` "Official scoring calls made, total: 4",
  followed **in the same bullet** by two dated supersessions ending at
  "cumulative distinct prediction sets scored: **6** (floor, rounds 1–5)".
* **Use/mention** — grade documents, rulings, repair tables and audit rows
  quoting the defective strings in order to record them, and the two
  `use_mention_control_set.json` fixtures whose gold label is literally
  `MENTION`.
* **Per-run counts that were true** — "zero scoring calls", "no scoring call is
  made", "this run: 1".
* **Not the class at all** — counts of entrants, of CSV files, of G-items, of
  submission rules.

Two were close enough to record as considered rather than dropped:

* `docs/charters/RESULT_PRIORITY_CHARTER.md:151` — *"claimed a single scoring
  call where four were made, and claimed best on three of eight cases where
  round 3 records five of eight."* **No prior grade named this site.** It was
  ruled **out of class**: it is the narrative record of a specific past incident,
  anchored in its own sentence three times over (the round-3 overalls 0.0741 and
  0.0676, and the explicit "round 3"), and it is **true of the moment it names** —
  four calls had been made at round 3. It states where the ledger stood at a
  described event, not where the ledger stands. That is the same side of the line
  the lab already put `ACTIVE_RESEARCH.md`'s per-round chain on.
* `CLOSURE_FAMILY_SUPERVISION_REVIEW_2026-08-07.md:77` — F2's finding row,
  *"STATUS §5's scoring-call ledger stops at 5 calls."* Out of class as a filed
  finding's body describing another surface's defect, and reconciled in the same
  block regardless, which names the 6th call two lines later.

## 8. The two frozen surfaces — ruled PER FILE, and why

`bcad2bbc` holds that **a criterion may not require more than the maximum
permitted action on the surface it grades.** On a signed or frozen record `L-44`
forbids revision. The maximum permitted action there is therefore **a dated
addendum below the freeze line**, and the criterion is graded **per file**.

**A per-sentence or per-block reading is VOID on these two surfaces**, and not as
a matter of leniency but of structure: an addendum below a freeze line
*structurally cannot* reconcile per sentence, because the sentence it scopes is
above the freeze line and the addendum is below it. In
`R5_PREREGISTRATION.md` the claim sits at **line 7** and the addendum at
**lines 207–216** — about 200 lines apart, outside any window any instrument
would use. `6aedfcc9` measured the trap directly (per sentence 1→1; per file
1→0), and `bcad2bbc` measured the same trap at 7-before/7-after on a different
frozen pre-registration.

**This pass reproduced that signature on its own instrument**, and reports it as
expected behaviour rather than as a finding:

| reading | sites reconciled |
|---|---|
| per block, all 21 sites | **19 / 21** |
| per file, all 21 sites | **21 / 21** |
| **governing** (per file on the two frozen surfaces, per block elsewhere) | **21 / 21** |

The only two per-block misses were **exactly** the two frozen surfaces. No other
site depended on the per-file reading.

Both addenda supplied the `D310` treatment in full: era scope
(*"was true as of this file's commit (2026-08-07, `e865076b`, before the call)"*;
*"was true of the session that wrote this file (committed 2026-08-05 at
`0bade54a`)"*) **plus** the live count (*"the cumulative ledger is now SIX"*)
**plus** the next ordinal (*"the next call would be the 7th"*).

### 8.1 Append-only verified, not accepted on report

The frozen bytes were compared against the repaired files directly:

| file | frozen at | frozen bytes | repaired bytes | exact byte prefix | lines removed or altered inside the frozen prefix |
|---|---|---|---|---|---|
| `R5_PREREGISTRATION.md` | `e865076b` | 11,520 | 12,559 | **yes** | **0** |
| `R5_RULE_FREEZE.md` | `0bade54a` | 6,352 | 7,101 | **yes** | **0** |

17 and 11 lines were appended respectively. Every frozen line compared equal
index-for-index. **No frozen clause was touched.**

## 9. The manifests, key by key against the prior frame's parsed blob

Both `MANIFEST.json` files were parsed at `8cefb4e9^` and at the pinned frame and
compared key by key, not by diff:

| check | `closure_challenge_submission` | `closure_challenge_submission_round4` |
|---|---|---|
| keys before → after | 16 → 17 | 16 → 17 |
| keys removed | **0** | **0** |
| pre-existing keys whose value moved | **0** | **0** |
| order of pre-existing keys preserved | **yes** | **yes** |
| `scoring_call_limit_note` byte-intact (sha256 compared) | **yes** | **yes** |
| the eight CSV digests under `files` | **8 / 8 untouched** | **8 / 8 untouched** |
| sibling keys added | **1** | **1** |

The added key was `scoring_call_limit_note_correction_2026_08_17` in both, at
**position 8, immediately following `scoring_call_limit_note`**.

The two notes carried *different* defective shapes — `"four-calls-ever"` (the
compound that hid the third grade's boundary) and `"the ledger (five distinct
prediction sets scored, ever)"` (a parenthetical). Both were reconciled by the
appended sibling.

## 10. Structural versus textual adjacency in the JSON sites — ruled, not left to a tool

**This pass AGREES with the third and fourth grades, and re-tested the ground
rather than inheriting it.**

JSON has no sentences, and its line breaks are an artifact of a
`json.dumps(indent=…)` setting. A measurement that changes under a pretty-printer
flag is not a measurement of the document. Re-serialising each file at
`indent=2`, `4`, `8` and `None`:

| file | line gap at indent 2 / 4 / 8 / None | char gap at indent 2 / 4 / 8 / None |
|---|---|---|
| `closure_challenge_criterion_test_case_table.json` | 2 / 2 / 2 / **0** | 1666 / 1674 / 1690 / 1658 |
| `closure_challenge_submission/MANIFEST.json` | 1 / 1 / 1 / **0** | 326 / 328 / 332 / 324 |
| `…_round4/MANIFEST.json` | 1 / 1 / 1 / **0** | 355 / 357 / 361 / 353 |

Textual adjacency **collapsed to zero** at `indent=None`, and even the raw
character gap moved with the indent setting. **Both textual measures are
functions of a serializer flag.** What did not move under any of the four
settings was *same object, sibling key*. The sibling order was identical in every
serialization.

The reconciliations were therefore ruled **structurally adjacent and valid**.

One refinement is recorded, because this pass measured it and it does not change
the ruling: in `closure_challenge_criterion_test_case_table.json` the
reconciliation is **not** the immediately-following sibling — `verdict.statement`
is followed by `statement_correction_2026_08_02` and only then by
`statement_correction_2026_08_17`. The intervening sibling is itself a prior
correction of **the same key**, appended by the same mechanism. The invariant
that survives re-serialization is *same object, sibling key, naming the corrected
key explicitly*, and the 2026-08-17 correction does name its target in its first
clause ("COUNT RECONCILIATION of the ordinal in the statement's closing
sentence"). A stack of dated corrections on one key is the lab's own established
form, not a gap.

## 11. The verdict cell was not altered by the repairs

The V7 rung row's verdict cell was extracted as a string and hashed at four
frames. Everything the repairs wrote into the rung row was a repair record in the
evidence cell, not a verdict.

| frame | verdict-cell length | sha256 (first 20) |
|---|---|---|
| `3e04991c` (fourth grade) | 494 | `fdcfbd052253971bfe53` |
| `8cefb4e9` | 258 | `f575991c6be2e11c391a` |
| `6aedfcc9` | 494 | `fdcfbd052253971bfe53` |
| `678a69ab` (pinned) | 494 | `fdcfbd052253971bfe53` |

**Byte-identical across every repair since the fourth grade.** It read `FAIL`
until this ruling. (`8cefb4e9` predates the fourth grade's own cell write, which
is why it is shorter.)

## 12. The second conjunct — the submittable artifact

Re-measured from the files, not from a record of them. Three assembled
submissions, eight CSVs each:

| directory | files | rows | cols | header | layout |
|---|---|---|---|---|---|
| `closure_challenge_submission` | 8 | 1000 | 3 | none | flat `test/` |
| `closure_challenge_submission_round4` | 8 | 1000 | 3 | none | flat `test/` |
| `closure_challenge_submission_round5` | 8 | 1000 | 3 | none | flat `test/` |

Every first row parsed as three floats, so no header row was present in any of
the 24 files. The manifests record the accepted-layout precedent
(`matches accepted submissions wu, montoya and wang at benchmark commit
deb91557`). The `submissions/` directory named by the criterion sits in the
benchmark clone, outside this repository and outside this pass's write scope.

## 13. Out of scope, and filed rather than appended

* `docs/DOCKET.md:223` (`D30`) stayed unrepaired, as three graders had already
  agreed: the phrase sits in quotation marks as the **object** of a claim about
  its register, and a filed finding's body is another author's row. This pass
  re-read it and concurred. **Nothing was appended to it.**
* `/home/ubuntu/Certonomous_closure_challenge` was read-only and not this pass's.
  Whether the frozen addenda propagate there remained an open owner decision and
  was not touched.
* **A peer's staged work was live in the shared index at grade time** and was
  left exactly as found. It staged a reversion of the `6aedfcc9` repairs — the
  two frozen addenda removed, `CLOSURE_METHODS_COMPARISON.md:325` returned to
  `"yes, 5 calls, self-imposed"`, the docket rows dropped and the fourth grade's
  record staged for deletion. The working tree was byte-identical to `HEAD` for
  every one of those paths, so the reversion existed **only in the index**. It is
  recorded here as an observation for the chief, not as a finding against V7, and
  **it was neither committed, reverted, nor otherwise disturbed by this pass.**
  This grade was built through a private index for exactly that reason.
