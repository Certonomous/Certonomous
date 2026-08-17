# Ladder V, rung V7 — the FOURTH non-author grade

**Verdict: `FAIL`.** Graded 2026-08-17 at frame `8cefb4e9` pinned in argv, by a
non-author of the ruling, of every repair, and of all three prior grades. The
grader wrote no part of what is graded and repaired nothing.

---

## 1. The criterion, quoted from source

`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md:335-338`, read at
the graded frame:

> **V7. Kill the two known defects and prove it**: the false docstring sentence
> corrected (and a grep for any other count claims about scoring calls, all
> reconciled against actual call sites); the submittable artifact assembled to
> the accepted format (1000×3, no header, one of the two accepted layouts,
> verified against an accepted submission in submissions/).

**`all` is the criterion's own word.** There is no tense clause, no era clause,
no authorship clause and no directory qualifier in it. Three grades have now
failed this rung, and each failure was a CLASS BOUNDARY rather than a missed
pattern: an era clause (`D310`), a directory scope (`D330`), word adjacency
(`D334`). **This grade found a fourth, of the same shape.**

## 2. The verdict cell was not altered by the repair

Cell 2 of the V7 row was extracted by splitting the row on ` | ` at five
frames and compared as a string. It is **byte-identical** at `ec58538c` (the
second grade, the last pass entitled to write it), `63702c5d`, `353191c7` (the
third repair) and `8cefb4e9` (the repair graded here). Both repairs recorded
themselves in cell 3 and left the verdict at `FAIL`, exactly as each said it
would. That obligation was met.

## 3. My own recogniser, built from the claim class rather than from theirs

A grader who re-runs the filter under test inherits its boundary. The three
defeated filters share one structural property: the in-class test demanded a
RELATIONSHIP between the count token and a class word — a tense, a path, a
`[-\s]{1,20}` joiner — and the defect lived where that relationship did not
hold. So this instrument **tests no relationship at stage 1**. It anchors at
EVERY count token and takes a raw CHARACTER WINDOW around it (−90/+160). A
window has no grammar, so no compound form, no all-time quantifier, no
intervening verb and no table-cell boundary can fall outside it.

| stage | what it does |
|---|---|
| 0 | file pre-filter: bytes hold one of `call`, `scoring`, `scored`, `prediction set`, `ledger` |
| 1 | recogniser: a count token with a class ROOT inside the character window |
| 2 | in-class filter, applied **ON TOP** and never folded in; every survivor READ |

`ledger` is carried as both a pre-filter literal and a class root, which is
**wider than the repair's vocabulary** — its in-class test required
`scoring`/`official`/`prediction set`/`call`.

**Superset, machine-checked by `assert_superset()` on every invocation:** every
class ROOT literally contains a pre-filter literal, so a file holding a
recogniser hit necessarily holds a pre-filter literal; and every control probe
is asserted to be admitted by the pre-filter, by the recogniser AND by the
in-class predicate, so an arm cannot silently admit what stage 1 never offered.

**Two flats, unioned**: one dehyphenates soft wraps (`scor-\ning` → `scoring`),
one only collapses whitespace (`four-\ncalls` → `four-calls`). Neither alone is
sufficient. All blanking is offset-preserving — strike spans first and tracked,
then continuation prefixes (`>`, `> >`, list markers), then emphasis (`**`, `*`,
backticks, `<b>`, `<em>`); **never `~`**, which is the strike marker, and
**never `_`**, which is a word character in the very keys being read
(`scoring_call_limit_note`). Quoting is always from unmodified text.

**Every `.py` was read a second time THROUGH THE AST in rendered form**, and —
going beyond the repair — **every `.json` was read again through the parser**,
so escape sequences are resolved rather than matched around.

### 3.1 The instrument was reported BROKEN by its own controls twice, before it was trusted

1. The all-time control form *"We have made 5 calls in total on this benchmark."*
   was **REJECTED by my own stage 2**, which required
   `scoring|official|prediction set|ledger|scored` in the window
   unconditionally. **My filter carried the exact `D334` hole.** The veto was
   made conditional: it fires only when nothing else ties the count to the
   ledger.
2. The polarity control returned **1 and 1** where it had to return 2 and 1,
   because it was measured AFTER the value test, which discards the live-count
   clause by construction. Polarity is a question about scope granularity, not
   class membership; it is now measured at the tie level.

## 4. The adjacency test, run against my own filter BEFORE trusting it on anything unknown

Against the **pre-repair blobs at `353191c7`** — testing at HEAD, where they are
already repaired, would prove nothing about detection:

| site | with my arms | without them |
|---|---|---|
| `sdk/scripts/export_closure_submission_csvs.py:440` | **FOUND** | MISS |
| `demo-output/website/closure_challenge_submission/MANIFEST.json:9` | **FOUND** | MISS |
| `demo-output/website/CLOSURE_METHOD_PRIORITY_REVIEW.md:258` | **FOUND** | MISS |
| `demo-output/website/closure_challenge_submission_round4/MANIFEST.json:9` | **FOUND** | FOUND |

**4 of 4 re-found; 3 of 4 miss without the arms** — the same conclusion the
repair reported, reached independently. *A filter that cannot re-find a site you
already know about will not find the one you do not.*

**The first version of this test passed 4 of 4 and was WRONG.** It matched by
line proximity (±6), and two of the four "FOUND" results were hits on a date
token `07` and on a CSV count `eight` seven lines away from the claim. The test
now requires the hit to carry the claim's own count VALUE and the claim phrase
to lie inside the span the recogniser actually saw. **A control that can be
satisfied by an accident is not a control**, and this one was satisfied by one.

## 5. Corpus arm, stated so it can be faulted

**EVERY TRACKED FILE at the pinned frame — 20,764**, generators and artifacts
swept together. Not `sdk/` (327 files at this frame, `D330`'s boundary), not an
era slice (`D310`'s), and not word adjacency (`D334`'s). The criterion's grep is
unqualified as to directory, tense and word order, so the arm is unqualified in
all three. 35 tracked blobs do not decode as UTF-8 and are named as unread.

**Sweep: 20,764 files → 2,184 past the file pre-filter → 53,268 recogniser hits
→ 8,641 in class → 3,823 distinct reading cores → ALL READ.**

**HEAD moved during the pass**, from the pinned frame `8cefb4e9` to `52cdf6dd`
(five commits, front-facing-document work). **Ancestry was confirmed** — the
graded frame is an ancestor of the landing frame — and the grade stands at the
pinned frame. A **DELTA ARM** was swept over the **9 paths modified** between
the two frames: **43 in-class positions, ALL READ, NOTHING NEW IN CLASS** (they
are section numbers, item numbers, ledger-row counts and *"the chief's call"*).
The 12 other changed paths were deletions. **Every blob this grade rests on was
asserted IDENTICAL across both frames** — the three findings, the four repaired
sites, `closure_round5_qcr_forward.py`, `docs/DOCKET.md` and this ladder
document.

**The reading unit** is the 200 characters centred on the count token, deduped;
the sentence-plus-parenthetical scope is retained separately and is where
anchoring is judged, so nothing about reconciliation is decided from the short
unit. Docket and ladder rows are single markdown table lines thousands of
characters long, which is why the sentence is not the reading unit: 2,152
distinct sentences came to 8.3M characters.

## 6. Controls — kind DERIVED, never declared

`scripts/control_kind.py` classified the ledger **`RECOGNITION`** from the
evidence: **8 mutually independent forms, ALL FOUND**, and **4 negative forms
correctly rejected**.

| planted form | class it probes | fired |
|---|---|---|
| `Whether to spend a 5th official scoring call is the coordinator's call.` | ordinal position | yes |
| `The record shows four official scoring calls, ever, on this benchmark.` | cardinal ledger total | yes |
| `The lab's four-calls-ever ledger is a self-imposed discipline.` | **compound**, count abutting a bare `call` | yes |
| `We have made 5 calls in total on this benchmark.` | **all-time quantifier** | yes |
| `This would be the fifth scoring call the lab has spent.` | spelled ordinal | yes |
| `Our ledger stands at three official scor-\ning calls.` | hyphen-wrapped noun | yes |
| `Our five-call ledger is stricter than the rules require.` | digit + hyphenated compound | yes |
| `Two distinct prediction sets scored, cumulative.` | ledger vocabulary, no `scoring` adjacent | yes |

Negatives correctly rejected: `We reviewed 5 call sites in the harness.` ·
`The runner batches two calls per request.` · `The API made 4 tool calls during
that turn.` · `There are seven callbacks registered in the call graph.` — two of
them aimed squarely at the arms, so the arms are shown not to be merely loose.

Every form planted **BY LINE INDEX** onto a line whose **neighbourhood was
pre-checked to carry zero baseline signal**, and read back **BY SLICING AT THAT
INDEX** with `readback == payload` and `readback.encode() == payload.encode()`
asserted on every plant. The multi-line wrapped form occupies its own lines at
the same index and is read back by slicing exactly that many; the readback
assertion **caught the first attempt**, which planted it as one line.

- **Struck negative control, run BOTH ways on one sentence: unstruck 1, struck 0.**
- **Polarity control: 2 clause scopes against 1 sentence scope**, on one sentence
  carrying a stale count in one clause and the live count in the other — a
  sentence-scoped detector merges them and the live count then reads as
  reconciling the stale clause, which CERTIFIES THE DEFECT. The single-polarity
  control returned **1 and 1** and is therefore not relied on alone.
- **Anchor test given SENTENCE-PLUS-PARENTHETICAL scope**: under it a correctly
  repaired sentence reads `(era=True, live=True)`; **under clause scope the same
  sentence reads unreconciled**, because clause scope cuts at `(` and era
  anchors are routinely parentheticals. Measured both ways, not asserted.

Control file `demo-output/website/CLOSURE_CHALLENGE_STATUS.md`, baseline 72,
planted at line index 20.

## 7. The four repaired sites — all four verified CORRECT

1. **`sdk/scripts/export_closure_submission_csvs.py:440`** — graded **THROUGH
   THE AST in rendered form**, not from source. The rendered constant reads
   `The lab's scoring-call ledger ("four-calls-ever" as this round-3-era script
   was written; the cumulative count is six after round 5's 2026-08-07 call, so
   the next one would be the 7th)`. Era-scope **True**, live count **True**,
   next-call arithmetic **True**, the escaping **read back rather than assumed**
   (the literal `"four-calls-ever"` is present) and **NO SURVIVING BACKSLASH**.
   Its line-31 twin still carries the canonical treatment.
2. **`demo-output/website/closure_challenge_submission/MANIFEST.json:9`** — see §8.
3. **`demo-output/website/CLOSURE_METHOD_PRIORITY_REVIEW.md:258-260`** — the era
   scope and the live count sit inside the claim's own sentence.
4. **`demo-output/website/closure_challenge_submission_round4/MANIFEST.json:9`** — see §8.

**Nothing in this grade was repaired. A grader may not repair what he grades.**

## 8. RULING 1 — STRUCTURAL adjacency, for both manifests. I agree with the third grade, on a re-tested ground

My own detector reports **both manifests unreconciled** (`era=True, live=False`
on `scoring_call_limit_note`), exactly as `D334` predicted it would. **I override
my own detector and rule STRUCTURAL, in writing, rather than letting a tool
decide it silently.**

The third grade's ground was that JSON has no sentences and that its line breaks
are a `json.dumps(indent=2)` artifact. **That was re-tested rather than
inherited, by re-serializing the identical parsed document:**

| serialization | correction key, line distance | `generated_at`, line distance |
|---|---|---|
| `indent=2` (as committed) | **1** | 7 |
| `indent=4` | 1 | 7 |
| `indent=8` | 1 | 7 |
| `indent=None` | **0** | **0** |

A metric that returns 1-against-7 at one pretty-printer setting and 0-against-0
at another is **not a measurement of the document**. Meanwhile the structural
relation — *is the correction the immediately following sibling key of the note,
in the same object?* — returns **True at every serialization, in both files**.
The invariant is structural; the textual distance is the artifact. The third
grade was right, and it is right for a reason that survives being checked.

On the merits the correction wins under **either** reading: it is the
immediately adjacent sibling key **1 line away**, against the only other era
anchor **7 lines away** in a different position of the same object.

## 9. RULING 2 — the imported correction mechanism is CORRECT for these manifests

Measured first, in both files, by parsing the prior frame's blob and comparing
values rather than by reading the file:

- `scoring_call_limit_note` **BYTE-INTACT** in both (string equal and bytes equal).
- **The eight CSV digests untouched** in both (8 of 8).
- **Zero other keys changed**; exactly one key added, the correction.
- The correction carries era scope, the live count and the next-call arithmetic.
- `scoring_calls_made_by_this_run: 0` in both.
- **Neither manifest's own sha256 appears anywhere in the tracked corpus — 0
  occurrences each, re-measured here.**

**The import is right, and the alternative is worse.** Inventing a second
correction form would leave the corpus with two mechanisms for one job, which is
a defect class this lab has already filed against itself. The mechanism is
**named as imported inside the key's own body** with its source artifact cited,
so no reader is left inferring provenance. The "delivered package artifact"
worry does not survive measurement: the thing a manifest exists to assert is the
eight digests, and they are untouched; nothing in the corpus asserts a freeze on
the manifest's own bytes; the submissions are **PARKED**, so no external party
holds a copy to diverge from; and no historical text was rewritten.

**One residual, FILED and not a ground of this verdict.** The generator
`export_closure_submission_csvs.py:440` now emits a `scoring_call_limit_note`
whose text differs from the artifact's byte-intact note, and emits no correction
key; re-running it would overwrite the manifest and drop the correction. This is
the identical shape already sustained for the criterion-table pair at the third
grade, both surfaces are reconciled at this frame, and it is not a count-claim
defect. It is recorded so that whoever regenerates that package knows.

## 10. RULING 3 — the record defect is correctly repaired

- **`D330` ruled no such thing.** Its disposition cell, read at the graded
  frame, is an express **referral**: *"chief (whether a delivered,
  hash-asserted package artifact of a superseded round … is in class or is
  legitimately frozen; **FILED, NOT APPENDED**)"*.
- The chief's three grounds were **re-measured, not inherited**:
  `scoring_calls_made_by_this_run: 0` (confirmed in both manifests); the
  generator `closure_round4_manifest.py` carries the era treatment and
  `49f71b8c` is confirmed to have touched that file; and **neither manifest's
  own sha256 appears anywhere in the tracked corpus, 0 occurrences each**.
- The correction is **struck and kept in BOTH places** — `docs/DOCKET.md` at
  `D333` and the V7 rung row — with the markers `CORRECTED 2026-08-17`,
  `RULED NO SUCH THING` and the anchor `353191c7` present in both.

Recording a referral as a ruling in a durable record is itself a defect, and it
was named as such by its own author. That is the right disposition.

`docs/DOCKET.md:223` (`D30`) **stays unrepaired**, and this grader agrees on both
grounds: the phrase sits in quotation marks as the **object** of a claim about
its register rather than as an assertion of the count, and a filed finding's
body is another author's row.

---

## 11. WHY THE RUNG STILL FAILS — a FOURTH class boundary, and the same generator/artifact split for the fourth time

**Three surfaces stood in class and unreconciled at the graded frame.**

### 11.1 The boundary

Every prior in-class filter, `D334`'s two new arms included, joined the count
token to a class noun with `[-\s]{1,20}` — **whitespace and hyphens only**.
A VERB PHRASE is neither. `D334` named this hole in its own blind-spot list —
*"claims whose count token and noun are separated by more than a `[-\s]{1,20}`
joiner"* — and did not close it. Machine-checked, site by site:

| site | adjacency-joiner filter (`D310`/`D330`/`D334` shape) | character window |
|---|---|---|
| `R5_PREREGISTRATION.md:7` | **MISSES** | **FINDS** |
| `R5_RULE_FREEZE.md:122` | **MISSES** | **FINDS** |
| `CLOSURE_METHODS_COMPARISON.md:325` | FINDS | FINDS |

The same predicate finds the sites `D334` did repair, so the disagreement is a
property of these sentences and not of a broken control.

### 11.2 The sites

**(a) `demo-output/website/campaign/R5_PREREGISTRATION.md:7`** — *"The
scoring-call ledger stands at 5, where round 4 left it."* Present tense, in the
document's opening bold block. Against a live 6; the next call would be the 7th.
The file is 205 lines and carries **zero** occurrences of `cumulative`, of `six`,
or of the 2026-08-07 call. Its own sha256 appears **nowhere** in the tracked
corpus (0 occurrences), so no freeze is asserted on its bytes; it is cited by
COMMIT anchor `e865076b`, and a commit anchor is not disturbed by a later edit.

**(b) `demo-output/website/campaign/R5_RULE_FREEZE.md:122`** — *"the
scoring-call ledger stays at 5 in this session."* The file is 124 lines and
carries **zero** occurrences of `cumulative` or `six`. Own sha256: **0
occurrences** in the tracked corpus.

**(c) `demo-output/website/CLOSURE_METHODS_COMPARISON.md:325`** — *"| Scoring-call
ledger | **yes, 5 calls, self-imposed** |"*, the lab's own column in the
five-entrant comparison. **Stated at its weakest**: the column header reads
**"Us (round 4)"**, which is a genuine era scope and a structural one, and this
grade has just ruled structural scope valid in §8. But the corpus treatment is
era-scope **plus the live count**, and no `six` appears in the sentence, the row,
or the file. This site was **reachable by `D334`'s own compound arm** and is not
named in its record.

### 11.3 The decisive measurement is not tense and not novelty — it is that the lab already applied the fix to this session's THIRD surface, under this rung

`sdk/scripts/closure_round5_qcr_forward.py:26-33` — the script of the **same
round-5 session**, governed by the very rule freeze at (b) — carried the same
claim and reads, at the graded frame:

> as of THIS SCRIPT'S RUN (2026-08-07, before the call) the ledger stood at 5
> distinct prediction sets scored. **Scoped to its own run because the standing
> count has since moved**: the supervisor's designated scoring agent made the
> round-5 call later the same day and **the cumulative ledger is now SIX**
> (floor, rounds 1-5). Nothing in this file made or makes a call; **only the
> sentence describing the ledger needed a date on it.** (Ladder V rung V7,
> re-run under Pass 2, 2026-08-10.)

It says **`Ladder V rung V7`** in its own text. The corpus cites it as the
cleanest treatment of this exact sentence. **The script was reached; the two
prose documents of the same session were not** — `R5_PREREGISTRATION.md` was
last touched at `9a21d65c` and `R5_RULE_FREEZE.md` at `0bade54a`, neither a V7
repair. This is verbatim the standard the lab wrote for itself at
`CLOSURE_CHALLENGE_STATUS.md:380-385` and which `D330` quoted: the withdrawal
was applied to the JSON **and** the generator *"so that the sentence is not left
standing on a surface this one does not reach"*. It is the fourth consecutive
failure of the same kind.

### 11.4 Every exemption that could reach these sites was tested and does not

- **Authorship (`D310`).** Both documents made **zero** scoring calls and both
  say so in their own words — *"No scoring call has been made in producing
  anything below"*, *"The one call … belongs to the supervisor, not to the
  session that wrote this"*, *"HARD STOP before scoring"*. This is the chief's
  own `scoring_calls_made_by_this_run` test, which ruled the round-4 manifest IN
  class on exactly this ground.
- **Era scope.** A document-level date does not reconcile: the corpus rejected
  that for `export_closure_submission_csvs.py` and, in the repair now under
  grade, for `CLOSURE_METHOD_PRIORITY_REVIEW.md:258`, whose own document header
  is dated 2026-08-05. The treatment is era scope **plus the live count**, and
  neither R5 document carries the live count anywhere in it.
- **"R5 is frozen; §2b forbids repairing a recorded gate."** Read at
  `CLOSURE_THREE_STRANDS_2026-08-15.md:356`, §2b governs **recorded gates and
  verdicts** — pre-registered acceptance criteria that must not be rewritten
  after the fact. A prose sentence about the scoring-call ledger is neither, the
  corpus treatment appends beside rather than rewriting, and the same session's
  script received that treatment under this rung.
- **Session scope**, for (b) alone. `closure_round5_qcr_forward.py` originally
  read *"This script makes none … the ledger stays at 5"*; the 2026-08-08 pass
  ruled it *"none — correct"* and **Pass 2 overruled that on 2026-08-10** as
  *"TRUE of its own run, FALSE as standing text"* and repaired it. The lab has
  already decided this exact question, on this exact verb, against the
  session-scope defence.

### 11.5 What was tested and is NOT a defect

- **The two frozen entry-of-record JSONs and their generators** —
  `closure_challenge_trained_entry_round3_gated.json` (`…calls_this_lab_has_made…: 4`,
  whose list's last item reads *"4: round-3, **this run**"*) and
  `closure_challenge_trained_entry_round4_duct.json` (`this_run: 1,
  cumulative_distinct_prediction_sets_scored: 5`). Each records the cumulative
  count as of and INCLUDING its own call, by the run that made it. **`this_run: 1`
  against the manifests' `0` is the chief's own line, and it falls the other
  way here.** Out of class on `D310`'s authorship ground.
- `CLOSURE_CHALLENGE_STATUS.md:1139` — *"Official scoring calls made, total: 4"*
  is followed in the same bullet by **two dated supersessions ending at 6**, the
  file's own established convention; `LADDER_V_V8_REVERIFICATION` inspected
  exactly this and marked it CLOSED. My sentence-scope detector split the
  assertion from its supersession because they are separate sentences; that is a
  detector artifact and is recorded as one.
- `CLOSURE_CHALLENGE_STATUS.md:523` and `ACTIVE_RESEARCH.md:680` — *"this was 1
  new official scoring call — the 5th cumulative"* records the ordinal position
  of one specific past call, which was and remains true.
- `closure_challenge_submission_round4/MANIFEST.json:76` — *"official call #5"*
  as provenance of the round-4 entry, true and `D310`'s named positive form.

---

## 12. What this grade cannot see, stated so the next grader has it

- **A fifth class boundary.** Four passes have now each been failed by one, and
  the honest prediction is that a fifth exists. A character window has no
  grammar, which closes the joiner family; it does not close **cross-sentence**
  claims, where the unit is established in one sentence and the count asserted
  in another beyond the window.
- Claims carrying **no count token at all** — *"the ledger has not moved since
  round 4"* names no number and is invisible to every instrument here.
- **35 tracked blobs that do not decode as UTF-8**, and untracked files.
- Whether the three sites in §11.2 exhaust the joiner family, or only the part a
  200-character window reaches.
- **No filter here can certify its own completeness.** The window was chosen
  because a grader found the previous hole, not because it proved it had none.

---

**Compliance.** No scoring call was made and none was authorised. **The ledger
was not touched and stood at 6.** No solver was run, nothing was sent,
registered or submitted; submissions remained PARKED. Nothing under `dist/`,
`demo-output/website/latex/`, `motorbike-video/` or `LAPTOP_SHOOT.md` was
touched, and nothing was moved. `__pycache__` was purged tree-wide before every
measurement. **Nothing graded here was repaired.**

*Known and not this grade's: `docket_citation_guard.py` reported FAIL on two
pre-existing unresolved citations (`D188`, a documented gap; `D901`, a test
fixture) in files this repair did not touch.*

Signed: the fourth non-author grade of rung V7, 2026-08-17, frame `8cefb4e9`.
Owed next: **repair of the three sites in §11.2 by a non-author of this grade.**
