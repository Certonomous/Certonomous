# Ladder V — independent grade of rungs V5 and V8 after their blocker repairs

**Date:** 2026-08-15. **Grader:** a non-author agent, dispatched to measure, not to repair.
**HEAD at grade time:** `ec92cc55`. **Nothing sent, uploaded or registered.** No solver run,
no scoring call — **the ledger stands at 6** — and the scoring pin `deb91557` was not moved.
This pass changed no file other than this document and `docs/DOCKET.md`.

**Verdicts, up front, so they can be argued with before the evidence is read:**

| rung | verdict |
|---|---|
| **V5** — QCR provenance, leg 3 | **FAIL.** Two grounds, both taken from the chief's own frame ruling |
| **V8** — claims-language audit of the cover email + description document | **PASS WITH RESIDUALS** (three, named in §7) |
| the chief's V5 frame ruling `3af7bd2b` itself | **OUTCOME SURVIVES; THREE OF ITS SUPPORTING ARGUMENTS DO NOT** (§4) |

---

## 1. Independence, and why it cannot be proved from this repository

R-ISOLATE part 3 requires a grader who did not write the work. On this box that is not
demonstrable by the means a reader would reach for first, and saying so is part of the grade:

- **Git authorship cannot discriminate.** Every commit in this repository carries the same
  `Ubuntu <ubuntu@ip-172-31-43-247…>` identity — 1,165 of 1,165 since 2026-08-01. The author
  field separates no two agents on this machine.
- **Session start cannot discriminate either.** This session container has been open since
  2026-08-04, which is before every commit I must be clear of. "The session predates the
  work" is available to an author as much as to a grader.

**What does discriminate: when this task first entered the agent-thread transcript.** The
dispatch reached me at **2026-08-15T19:26:49Z** (`date -u`, run as the first command of the
pass). Every commit I must be clear of is earlier by a wide margin:

| commit | committed | ahead of my dispatch by |
|---|---|---|
| `f8c889cc` — V8's prior grade | 2026-08-14T23:55:56Z | 19 h 31 m |
| `d80649f9` — V8's cover-email repair | 2026-08-15T00:17:46Z | 19 h 09 m |
| `650c1e04` — D88/D89 filing | 2026-08-15T00:18:07Z | 19 h 09 m |
| `3af7bd2b` — the chief's V5 frame ruling | 2026-08-15T02:24:57Z | 17 h 02 m |
| `e639796e` — V5's generator repair | 2026-08-15T02:50:57Z | 16 h 36 m |
| `85090c53` | 2026-08-15T02:52:35Z | 16 h 34 m |
| `b4604fc1` | 2026-08-15T02:53:58Z | 16 h 33 m |
| `eadcd112` — the ratio-interval measurement | 2026-08-15T03:06:04Z | 16 h 21 m |

**This evidence is untracked and per-machine.** It lives in an agent-thread transcript that
is not in the repository and not in any artifact this repository ships. **No reader of this
repository can re-derive it** — a reader can confirm the commit timestamps and nothing else.
That asymmetry is the whole of docket **D130**, and this grade is another instance of it
rather than a solution to it. A reader who declines to take the transcript on trust should
read this grade as *an* execution, correct or not on its own evidence, and not as *an
independent* one.

I worked in the **main checkout**, not a worktree, deliberately: two of the four measurement
arms below are gitignored trees and an out-of-repo run tree, which a worktree does not carry
(R-ISOLATE part 1's caveat). Evidence-file counts are printed before every finding drawn from
them.

## 2. Declared scope (R-CONVERGE)

**V5, graded against the chief's ruling at `3af7bd2b`, which fixes the frame as:** every
surface a future build or edit can change, plus the generators that write them; frozen
artifacts and third-party signed reports out of frame **only when enumerated on the rung's
face, each with its sha256 and a dated refusal ground**. I graded **leg 3 only** (the
Spalart-citation criterion). Legs 1 and 2 — in-house history, zero fitted parameters — were
not re-executed this pass and are inherited as PASS from `LADDER_V_PASS1_2026-08-11.md` §A5;
that is stated as an inheritance, not as a measurement.

**V8, graded on its own criterion:** the claims-language audit of **the cover email
(`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §5.4) and the description document
(`closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`)** — every quantitative
sentence maps to a named artifact. I re-derived G1, G2, G3 and the §5.3 item 9 binding rule,
and re-measured F4 from the prior round.

**Out of scope, and therefore filed rather than appended:** anything about the ruling's
supporting arguments (§4 states them; the docket rows carry them), and F4, which lives in
neither of V8's two named artifacts (§7 explains the call).

## 3. Method — four arms, and which arm every count came from

`__pycache__` was purged tree-wide before every cell (stale bytecode has inverted mutation
results in this lab, and `PYTHONDONTWRITEBYTECODE=1` does not fix it).

| arm | enumerator | size measured this pass | reached |
|---|---|---|---|
| **tracked** | `git grep -a` (**not** `-I`, and **not** the shell's `grep`, which is `ugrep --ignore-files` and passes `-I` too) | 20,688 files | yes |
| **untracked** | `git ls-files --others --exclude-standard` | **5** files | yes, zero hits |
| **gitignored** | `git ls-files --others --ignored --exclude-standard -z \| xargs -0 /usr/bin/grep -aIlF -f <patterns>` | **37,242** files | yes, ~7 s |
| **run tree** | `/usr/bin/find /home/ubuntu/certonomous-runs/ -type f -print0 \| xargs -0 …` (`find` is `bfs` here) | **132,049** files | yes, with a positive control |

**Positive control for the run-tree arm, because a silent zero over an out-of-repo tree is
the exact fail-open shape R-ISOLATE warns about.** A file reading *"the untrained QCR2000
forward solve"* was seeded at `/home/ubuntu/certonomous-runs/A1-simplec-off/__probe_v5.txt`,
the identical sweep returned it, and the probe was removed (`ls` confirms absence). The
zero below is therefore a measurement and not a blind spot.

**Result of the QCR sweep on the three non-tracked arms:** untracked **0**; run tree **0**;
gitignored **3** files, all under `dist/` — `site/benchmarks.html` (3 Spalart), `site/closure.html`
(3 Spalart), and **`snapshot/lab_stats.json` (0 Spalart)**.

---

## 4. THE RULING ITSELF, GRADED FIRST

Under §2 of R-ISOLATE the chief's record is never the presumed-correct side of a conflict,
and the ruling flags itself for grading. **Its operative outcome — generators are in frame;
an unenumerated exclusion is a gap — I find correct, and I grade V5 by it below.** Three of
the arguments holding it up do not survive execution.

### 4a. The W-2 citation points the other way

The ruling rejects the literal "no exclusions" reading because *"a criterion no execution can
satisfy is not a high standard, it is an unfalsifiable one, and this lab has already ruled
that a gate whose verdict is fixed by construction is not a gate (W-2)."*

**An unsatisfiable criterion is not unfalsifiable. It is permanently falsified.** Falsifiability
is the capacity to be shown false; a criterion that is always false is maximally falsifiable.
And W-2, read at its own source (`agenda/NEW_DIRECTIONS_2026-08-14.md` §4, *"the identity
test"*), is about the opposite shape: a gate whose **stated failure mode cannot occur** — the
`+0.9742` correlation whose null sat pinned at `+1.0000`, the closed form whose value is fixed
by construction, the zero-zero pairs that were always going to cost nothing. Every canonical
W-2 example is a gate guaranteed to **pass**. A gate guaranteed to **fail** launders nothing
and hides nothing; it simply never opens.

The outcome is still defensible — on the ground the ruling did not state, that a gate which
can never open blocks the send permanently and so decides by exhaustion rather than by
evidence. **The conclusion stands on a different argument than the one written.** Filed
**D153**.

### 4b. The premise for rejecting the literal reading is contradicted five paragraphs later, inside the same ruling

The stated ground is *"two of its surfaces are frozen artifacts that may never take a
revision."* Five paragraphs down, the same ruling establishes that
`campaign/QCR_ACTIVITY_CHECK_2026-08-08.md` **was amended at `fe612d03`, 20 hours after
signing**. And L-44, quoted in Pass 1's own record, is explicit: *"a frozen artifact **may
take a dated addendum** and **may never take a revision**"* — with `9a21d65c` cited as having
done exactly that and `cf6a0477` as having correctly refused the other.

Re-measured here, by execution rather than by reading:

| refused surface | commits | worktree sha256 (16) | == `git show HEAD:` | Spalart |
|---|---|---|---|---|
| `closure_challenge_submission_round5/MANIFEST.json` | `07a7fe9e` @ 2026-08-07T20:51:51Z, **never amended** | `58f4f5a5437e4e7b` | yes | **0** |
| `closure_challenge_round5_qcr_forward.json` | `e865076b` @ 2026-08-07T20:38:52Z, **never amended** | `7e6c0d855d0063e1` | yes | **0** |
| `campaign/QCR_ACTIVITY_CHECK_2026-08-08.md` | `1a14e90b` @ 2026-08-08T02:18:29Z **and `fe612d03` @ 2026-08-08T22:25:35Z** | `1f6b36cc39c66efd` | yes | **0** |
| `campaign/LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` | `49f71b8c` @ 2026-08-08T02:08:13Z, never amended | `2d270213c07f030b` | yes | **0** |

**The refused count is four, and the ruling is right that it is four.** But "may never take a
revision" is not a property of all four: one of them took a dated additive amendment 20 hours
after it was signed, three days before it was refused on the ground that it could not be
touched. A Spalart attribution is exactly the shape of edit L-44 permits — a dated addendum
below the frozen text.

There **is** a sound impossibility argument for `MANIFEST.json` specifically: A2's tamper
chain rests on its single-commit, never-amended history, and an addendum would end that
property at a cost the citation does not repay. **The ruling did not make that argument.** It
asserted a general impossibility that its own body falsifies for one of the four surfaces and
that L-44 falsifies in principle for all of them. Filed **D154**.

### 4c. The three-surface claim is right about reach and wrong about mechanism, and mechanism is the ruling's own point

The ruling states that `sdk/scripts/build_benchmarks.py:106` *"writes the same unattributed
untrained claim into `benchmarks.json`, `wall/wall.json` and
`dist/certonomous-demo/snapshot/lab_stats.json`."*

Executed: `build_benchmarks.py::main()` writes **`benchmarks.json` and `benchmarks.png`, and
nothing else** (line 348). `wall/wall.json` is written by `sdk/scripts/build_wall.py`, and
`lab_stats.json` by the bundle snapshot; both obtain the sentence **second-hand**, through
`sdk/chief_engineer/lab_stats.py::research_programs()`, which reads
`closure_challenge.our_entry` back out of `benchmarks.json` (line 334ff). `lab_stats.py`'s own
literal, `_NO_ENTRY_YET`, is the pre-entry text and carries no QCR claim, so it is **not** a
fourth generator — checked, because a comment there says the two literals "must be kept in
sync" and that is the shape a fourth generator would wear.

The reach is correct. The mechanism is not, and it matters here more than usual, because the
ruling's own instructive point about `e071075d` is *"it asked whether anything writes that
**file**, not whether anything writes that **sentence**."* A one-generator / two-derived
relationship described as a three-way write is the same conflation one level up — and it is
precisely why the repair could land cleanly on two surfaces and leave the third looking like
an oversight when it is in fact a different owner's rebuild. Filed **D152**.

---

## 5. V5 — **FAIL**

### 5a. What the repair did achieve, verified by execution and not by reading

`build_benchmarks.py:107` now reads *"…whose one coefficient Ccr1 = 0.3 is Spalart (2000)'s
published constant, adopted untrained and overridden nowhere."*

**"Regenerated, not hand-edited" — tested without writing to the tree.** The generator's
module-level `_CLOSURE` was parsed out by AST (`ast.literal_eval`, no import, no file write)
and its `our_entry` string compared byte-for-byte against every string in the two JSON
surfaces containing `untrained QCR`:

| surface | key | Spalart in the same string | byte-equal to the generator's constant |
|---|---|---|---|
| `demo-output/website/benchmarks.json` | `/closure_challenge/our_entry` | **yes** | **True** |
| `demo-output/website/wall/wall.json` | `/counters/research/closure/our_entry` | **yes** | **True** |

Both surfaces carry the generator's exact 3,172-character string. A hand-edit would have to
have reproduced it to the byte. **B3 is repaired.**

**The guard runs and passes:** `sdk/tests/test_untrained_qcr_attribution.py` — 4 passed,
`__pycache__` purged first. **Its reach, reported as a fact about the guard and not about the
text:** it opens `build_benchmarks.py` and the two JSON surfaces named above, and **nothing
else**. It does not open the third generator. One generator of three is instrumented.

### 5b. Ground 1 for FAIL — the exclusions are not on the rung's face

The ruling: *"Frozen artifacts and third-party signed reports are OUT OF FRAME — but only
when **enumerated on this rung's face, each with its sha256 and a dated refusal ground.** An
unenumerated exclusion is not a frame, it is a gap."*

**V5's face is `LADDER_V_TRIPLE_VERIFICATION.md` lines 30–76.** It contains no enumeration,
no sha256, and no dated refusal ground for any surface. The four refusals are described in
`LADDER_V_PASS1_2026-08-11.md` §A5 and re-checked in `LADDER_V_V5_GRADE_2026-08-15.md` §5 —
neither of which is the rung's face — and even there they carry commit anchors rather than
sha256. The ledger row at `LADDER_V_TRIPLE_VERIFICATION.md:588` still says *"three"*.

Nothing added the enumeration between the ruling (`3af7bd2b`, 02:24:57Z) and this grade
(19:26Z onward). **By the ruling's own sentence, V5 has four gaps, not four exclusions.**

**Falsifier for ground 1:** put on V5's face, in `LADDER_V_TRIPLE_VERIFICATION.md`, a table of
the four surfaces above with the full sha256 of each and a dated ground for each — and for
`QCR_ACTIVITY_CHECK_2026-08-08.md` a ground that survives `fe612d03`, since *"left to its
owner, it may not be touched"* does not. If that table exists and each row's hash matches
`git show HEAD:<path> | sha256sum`, this ground clears.

### 5c. Ground 2 for FAIL — surfaces in frame, carrying the claim, citing nobody, enumerated nowhere

Tracked arm, `git grep -a` over 20,688 files. **47 tracked files** carry the untrained-QCR
claim; **15 of them contain zero occurrences of "Spalart"**. Classified by hand, every one
opened:

**In frame and unenumerated — these are the finding:**

| surface | sites | what it says | why it is in frame |
|---|---|---|---|
| **`docs/PRODUCT_LIST.md`** | **:63, :136, :608, :655** | *"the ducts (untrained QCR2000: AR_1 0.0811→0.0455 …)"*, *"untrained-QCR proven structurally"* ×2, *"where the same untrained QCR was decisive"* | **A tracked, editable, non-frozen product surface — and it lies outside every V5 sweep frame ever executed.** Pass 1 leg 3's frame was 920 files under `demo-output/website/`; `docs/` was never in it. This is new. |
| `demo-output/website/CLOSURE_EVALUATION_PROTOCOL.md:391` | 1 | *"Round 5 replaced all three with an untrained QCR2000 forward solve"* | inside Pass 1's frame, among its "28 that do not cite", classified as a passing mention. It is not: it is the load-bearing claim about **our** model. |
| `sdk/scripts/closure_eval_battery/build_master_table.py:246, :371` | 2 | *"round 5 (untrained QCR2000 duct forward solve, the sixth pre-registered scoring call)"* | **the third generator** (D128), confirmed present at both line numbers |
| `demo-output/website/closure_eval/closure_eval_master_table.md:20` and `.json:84` | 2 | the same sentence, emitted | its two **tracked** outputs, zero Spalart in either |
| `dist/certonomous-demo/snapshot/lab_stats.json` | — | the claim, **0 Spalart** | gitignored arm; derived-at-build from `benchmarks.json`, so it takes the repair on the next bundle rebuild, which is the owner's |

**Out of frame on inspection, and named so the exclusion is argued rather than assumed:**
`CLOSURE_METHODS_COMPARISON.md:216` and `closure_challenge_C2_error_decomposition.md:255`
describe **Wu & Zhang's** SST-QCRC, not ours (`PRODUCT_LIST.md:351` likewise);
`V16_GRADE_HELDOUT_SETS.py:70,101` and `test_rank_claim_surfaces.py:584` are **held-out guard
corpora**, where the uncited sentence is the test datum and editing it destroys the control;
`LADDER_V_RUNGS_V2_V7_V10`, `LADDER_V_V6_V10_V14_CLOSURE`, `LADDER_V_V8_REVERIFICATION_2026-08-11`,
`V15_ROUND5_NUMBER_RECONCILIATION` and `reports/MORNING_REPORT_2026-08-07.md` are dated
ladder reports, which the ladder's own termination rule holds do not travel.

**So the rung does not pass even on the ruling's narrowest honest reading.** The ruling said
V5 stays open *on B3*. B3 is repaired and the rung is still open, on a surface class the
ruling did not reach — `docs/PRODUCT_LIST.md`, which no V5 sweep has ever looked at, in a
directory outside `demo-output/website/`.

**Falsifier for ground 2:** name Spalart (2000) with the year in the sentence at
`CLOSURE_EVALUATION_PROTOCOL.md:391` and at the four `PRODUCT_LIST.md` sites; repair
`build_master_table.py:246,371` and re-run the eval battery so its two tracked outputs
regenerate; then re-run the tracked sweep of §5c. If it returns zero in-frame files carrying
the claim about our own model with zero Spalart, and §5b's table is on the face, V5 passes.

**Reported, not edited.** Seven agents are working concurrently; `PRODUCT_LIST.md` and
`CLOSURE_EVALUATION_PROTOCOL.md` are live surfaces, and a grader editing the thing it grades
is the defect R-ISOLATE part 3 exists to prevent.

---

## 6. V8 — G1, G2, G3 and the binding rule, re-derived

### 6a. G1 — re-derived from the primary artifacts, not read

`demo-output/website/closure_challenge_seed_sensitivity.json` →
`spreads.overall_equivalent_S_bound` = **0.002419121853891026** (read by walking the JSON, not
by grep). `campaign/BOARD_RESCORE_2026-08-14.md` §3.1 → Yang **0.058013**, our margin
**0.001365**, on the **six-entry** board retrieved **2026-08-11T23:33Z** and re-verified
unchanged **2026-08-14T21:01Z**.

```
0.002419121853891026 / 0.001365 = 1.7722504424110082  →  177.23%,  i.e. 177%
```

**The bound exceeds the margin by 77%. It does not cover 84% of it.** And the 84% is
accounted for rather than merely denied: `0.002419121853891026 / 0.002878 = 0.8406` — the
four-entry board's margin over Reissmann. The old figure was arithmetically right about a
board that no longer exists.

**I used `0.001365` and did not write `0.0013658…`** — those digits exceed what a six-decimal
printing of Yang's overall supports (D104/D127).

**The `eadcd112` interval, confirmed rather than inherited.** On the margin interval the
board's 4-dp printings imply, `[0.0013153, 0.0014028]`, I recomputed the endpoints myself:
`0.002419121853891026 / 0.0014028 = 1.7245` and `/ 0.0013153 = 1.8392` — **[172.45%, 183.92%]**,
which does not span 100%. The conclusion is robust to the board's own printing precision.

**All three sites clear:**

| site | state at HEAD |
|---|---|
| `SUBMISSION_DRAFT.md` §5.2 (:742–791) | struck, replaced, with the reversal stated as a reversal |
| `SUBMISSION_DRAFT.md` §5.3 item 9 (:964–1004) | struck, figure **and** rule (§6d) |
| `SUBMISSION_DRAFT.md` §5.4 — **the cover email** (:1130–1136) | struck; states 177%, the derivation, and the adverse-load consequence: overall **0.059047** against Yang's 0.058013, *"the lead is gone"* |

**G1 CLEARS.**

### 6b. G2 — one letter, two answers

The prior round found the cover email stating a margin live at :1115 and striking the same
figure seven lines below at :1124. At HEAD the opening clause reads
`~~by 0.0029 over Reissmann, Fang and Sandberg~~ **by 0.001365 over Yang, at 0.058013**` —
struck at both sites — and the letter now says so in its own words: *"was struck only here and
left standing there until 2026-08-15, so this letter gave two answers to one question for four
days; both are now struck."* The repair discloses its own four-day window rather than closing
it silently. **G2 CLEARS.**

### 6c. G3 — the commit anchor

`DESCRIPTION_DOCUMENT.md:374` is struck — *"~~On the published board at `deb91557` our 0.056647
is the best overall number~~"* — under a note headed **"STRUCK 2026-08-15 — a commit anchor is
not a board"**, which states why (`deb91557` has four entrants and scores but does not rank),
notes that the sentence sat *above* the recomputation box whose scope rule reads *"anything
below not struck is live"* so the box never reached it, and restates the claim in the
document's own idiom: six-entry board, retrieved 2026-08-11T23:33Z, re-verified 2026-08-14T21:01Z,
0.001365 below Yang, not statistically decided. **G3 CLEARS.**

### 6d. The binding rule now fixes a form, not a figure — **and this is the best thing in the repair**

§5.3 item 9's old clause — *"No document in this package may quote the margin without this
qualifier"* — ordered every document to carry a figure whose direction of argument had already
reversed. It is replaced by a **triple**: (1) the margin, (2) the entrant it is over, named,
(3) the board, **by entrant count and retrieval date** — with *"a commit anchor is not an
admissible board identifier"* stated explicitly, the same requirement extended to the seed
bound expressed as a fraction of the margin, and an instruction that the figures are
regenerable and must not be retyped.

**This is a form, and a form does not go stale when the board moves.** The replacement is
correct and it is the structurally right kind of fix. Its one gap is §7 residual R2.

### 6e. F4, re-measured from the bytes

The certification at `SUBMISSION_DRAFT.md:613–618` reads: *"**Its thirty body lines are
byte-identical** — every row of the ten-row defect table, including the round-4 numbers it
indicts — but its heading was replaced and demoted `##` → `###` … the blank line that closed
the blockquote became `>`."*

Measured, not read. The kept banner was extracted from `git show e87650db^:` (lines 554–584)
and from HEAD, aligned index by index, and compared byte-for-byte:

- block = **1 heading + 30 body lines** at both revisions;
- heading differs (declared);
- closing blank → `>` (declared);
- **one body line differs, at index 20** — the `§5.4, §5.2 | no rank claim of any kind` row,
  which **is a row of the ten-row defect table**. Inserted at `2cec44ee` (2026-08-12T18:05:51Z):
  `*(figures as recorded at this banner's date against the four-entry board; the rule's live
  figures are 50% and 0–97% on the six-entry board — see §10's re-correction of 2026-08-12)*`.

**Three of 32 lines differ, not two** — independently reproducing the prior round's count, by
a different extraction. **The sentence "its thirty body lines are byte-identical" is false at
HEAD, and so is the clause "every row of the ten-row defect table".** No commit since
`f8c889cc` has touched it. **F4 is NOT repaired.**

---

## 7. V8 verdict — **PASS WITH RESIDUALS**, and why F4 is a residual rather than a blocker

V8's criterion names **two artifacts**: the cover email and the description document. G1, G2
and G3 all live in them, and all three clear on re-derivation. **F4's false sentence lives in
neither** — it is in §5's banner preamble of the draft, a document that does not travel — so
under R-CONVERGE it is a finding outside the declared scope, and R-CONVERGE says such a
finding is filed, not appended to the rung. **I am naming it as a residual anyway**, because
a false certification of byte-identity is the same defect class §4.4 exists for, and burying
it in the docket would be the letter of the rule against its purpose. A grader who reads V8's
criterion as covering the whole draft should read this verdict as FAIL on F4; I state the
reasoning so the disagreement is about the scope and not about the bytes.

| # | residual | falsifier |
|---|---|---|
| **R1** | `SUBMISSION_DRAFT.md:613–614` certifies thirty byte-identical body lines *"every row of the ten-row defect table"*; one row differs, edited at `2cec44ee` from inside the block the sentence certifies | correct the certification to *twenty-nine of thirty*, naming row 22 and `2cec44ee`; then re-run the aligned byte diff of §6e and get one declared difference per stated exception |
| **R2** | `SUBMISSION_DRAFT.md:666` states *"the 0.002419 seed bound covers **84%**"* live and unstruck, with no entrant and no board — **inside the kept 2026-08-10 banner**. It is true of the four-entry board it was written for, and it breaches the §5.3 replacement triple, which has **no dated-record carve-out** | either add the carve-out to the triple (*"a block explicitly dated and kept as a record satisfies (3) by its own date"*) or strike :666 with a forward pointer to §5.2. Falsifier: re-read §5.3 item 9 and :666 and find they agree |
| **R3** | **No instrument enforces the triple**, and the one instrument nearest it disagrees with the rule as written — `check_derived_figures.py`'s own control **NEG-4, "84% inside a kept dated banner", asserts `fired=False` by design** | implement D106's dated-context discriminator; falsifier is a guard that faults :666 under the rule-as-written and does not fault the §5.2 corrected text |

**Falsifier for the V8 verdict as a whole:** re-derive the ratio from
`closure_challenge_seed_sensitivity.json` → `spreads.overall_equivalent_S_bound` and
`BOARD_RESCORE_2026-08-14.md` §3.1 and get anything other than 177% on the 0.001365 basis; or
find a surviving live, unstruck, undated *"covers 84%"* in the cover email or the description
document. Either falsifies this PASS.

---

## 8. What the instruments could not tell me

Every count below is **a fact about the guard, not about the text**.

- **`board_placement_faults` has no arithmetic predicate.** Measured on `git show HEAD:scripts/self_audit.py`
  (the working tree copy is dirty under another agent's edit, so HEAD was used and is named):
  the function body is 8,058 characters and contains **zero** occurrences of `%`, `ratio`,
  `float(`, `Decimal` or `decimal`. It cannot evaluate 84% against 177% because it cannot
  evaluate. Confirms **D88** by execution.
- **It cannot fault a sentence about Yang in the shipping configuration.** `Yang` appears
  **once** in the entire 200 kB file, inside a comment. There is no live Yang datum for the
  guard to compare an ordinal against. Confirms **D89**.
- **The strike-marker skip (D85)** is real but does not live in this function — its body
  contains no `~~`, `<s>`, `struck` or `strike` token, so the adjudication happens in a helper.
  I did not trace it further: that is depth 3 and **R-DEPTH files it rather than executes it**.
- **`check_derived_figures.py` PASSES at HEAD** — 61 anchored figure quotations, 5 stated
  computations, all four positive controls fired and all nine negatives held. **Its own printed
  blind spot #1 is decisive here**: *"84% of a four-entry margin and any other 84% are one
  string."* Blind spot #2 is *"an error below half an ulp of the last digit written."* **This
  guard's PASS is not evidence that R2 is acceptable** — it is evidence that the guard was
  built to permit it.
- **The V5 guard instruments one generator of three.** `test_untrained_qcr_attribution.py`
  opens `build_benchmarks.py`, `benchmarks.json` and `wall/wall.json`. `build_master_table.py`
  is unguarded, so D128 has no instrument at all.
- **`_best_on_board_faults` (D129) and the run-tree 84%-phrase sweep were not completed by me.**
  The gitignored arm returned **zero** hits for the phrase; the run-tree phrase sweep was still
  running when this document was written, under contention with another agent's concurrent
  sweep of the same 132,049 files. **I am recording it as UNMEASURED rather than as zero**, and
  the QCR sweep over that same tree — which did complete, with a positive control — is the only
  run-tree result in this grade.

## 9. Docket rows filed

`docs/DOCKET.md` was diffed against `git show HEAD:docs/DOCKET.md` and was **clean** before
this write; no other agent's rows are carried. Highest existing ID re-checked immediately
before allocation: **D151**. Filed: **D152** (§4c), **D153** (§4a), **D154** (§4b),
**D155** (§7 R2/R3).

## 10. Summary

**V5 FAILS** — not on its repair, which is sound and verified byte-for-byte, but on the
frame the ruling itself defines: the four exclusions are not enumerated on the rung's face
with sha256 and dated grounds, and `docs/PRODUCT_LIST.md` carries the untrained claim about
our own model at four sites with zero Spalart, in a directory no V5 sweep has ever entered.

**V8 PASSES WITH THREE RESIDUALS** — G1's reversal is real and correctly propagated to all
three sites including the cover email, G2 and G3 clear, and the binding rule now fixes a form
rather than a figure, which is the repair that will still be right the next time the board
moves.

**The ruling survives in outcome and loses three of its arguments**, which is the deliverable
the brief said would be worth more than a rung verdict, and I think it is.
