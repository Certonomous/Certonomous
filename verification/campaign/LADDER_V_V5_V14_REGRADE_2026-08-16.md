# Ladder V — re-grade of rungs V5 and V14 after their blockers were repaired

**Date: 2026-08-16 (executed 2026-08-15T23:49Z → 2026-08-16T00:2xZ).**
**Grader: agent `a28ea07a5fc08e4df`, dispatched "Re-grade V5 and V14 after repairs".**
**Anchor: HEAD at the time of measurement; every count below is dated because the corpus moved
under three concurrent agents while this was written.**

Everything in this document was produced by running something. Where a prior record and my
measurement disagree, both numbers are printed and neither is presumed correct because of who
wrote it.

---

## 0. INDEPENDENCE — established against the dispatch record, and it does not travel

**Git cannot establish this and I do not cite it.** One identity authors ~1,741 of 1,876 commits,
auto-configured from username and hostname; the session container has been open since 2026-08-04.
**`scripts/check_rung_attribution.py` is NOT cited here** — it has emitted exactly one identity
across its whole deployed life, and run with a closing commit against a graded one it returns
`VERDICT: AUTHOR` for everyone (D173). It names a *session*, not an agent.

The evidence is the per-agent dispatch record at
`~/.claude/projects/-home-ubuntu-Certonomous/64b13819-…/subagents/`, which holds one transcript and
one `meta.json` per agent.

| agent | description (from `meta.json`) | first action | last action |
|---|---|---|---|
| **`a28ea07a5fc08e4df`** — **this grader** | *"Re-grade V5 and V14 after repairs"* | **2026-08-15T23:49:57.896Z** | (open) |
| `aed16d18a7ed2007a` | *"Close V5's enumeration and out-of-frame surfaces"* | 2026-08-15T20:09:49.028Z | 2026-08-15T20:25:10.244Z |
| `a44c131fd8e084307` | *"Widen the denominator pattern, repair ninth claim"* | 2026-08-15T22:06:32.455Z | 2026-08-15T23:48:29.968Z |

Against the commit timestamps I must be clear of:

| commit | authored | my first record | clear by |
|---|---|---|---|
| `f956e348` V5 enumeration | 2026-08-15T20:23:09Z | 23:49:57Z | 3 h 26 m |
| `d12cafd8` D167–D169 | 2026-08-15T20:23:31Z | 23:49:57Z | 3 h 26 m |
| `e65137cd` V5 frame on the face | 2026-08-15T20:24:08Z | 23:49:57Z | 3 h 25 m |
| `1aa90081` V14 docket rows | 2026-08-15T23:00:18Z | 23:49:57Z | 49 m |
| `f4c531cb` V14 widening | 2026-08-15T23:02:24Z | 23:49:57Z | 47 m |
| `49b36e57` V14 mutant restore | 2026-08-15T23:42:40Z | 23:49:57Z | 7 m |

**My first action postdates every one of the six commits, and it postdates the LAST action of both
authoring agents** (20:25:10Z and 23:48:29Z). I could not have authored any of them, and I did not
read either agent's transcript.

**THIS EVIDENCE IS UNTRACKED AND PER-MACHINE. No reader of the repository can re-derive it (D130).**
The `subagents/` directory is not in the repo, is not backed up into it, and does not survive the
machine. A reader who clones this repository has exactly the git history, which — as stated above —
proves nothing about authorship. This grade's independence claim is therefore **verifiable here and
now, and unverifiable by anyone else later.** That is a defect of the lab's record-keeping, not a
hedge, and the honest thing is to print it rather than let the table above look stronger than it is.

---

## 1. DECLARED SCOPE (R-CONVERGE)

**In scope:** rung **V5** graded against its frame ruling `3af7bd2b` and its three amendments
(`25777f57`, `78eb5530`, and the enumeration `f956e348`/`e65137cd` that the ruling required); rung
**V14** graded against the denominator ruling `9b9951a1` and the widening `f4c531cb`. Both rungs'
*rulings* are graded as well as the rungs, because both rulings instruct that they be measured and
not inherited.

**Out of scope, and FILED rather than acted on:** every other rung; the correctness of any claim
that is not an untrained-QCR attribution (V5) or a board ordinal / denominator / best-on-board count
(V14); the contents of `dist/`, `demo-output/website/latex/`, `LAPTOP_SHOOT.md`, `motorbike-video/`,
`.autostop-hold` and `scripts/self_audit.py`, all of which were **read and never written**.

No solver was run. No scoring call was made; the ledger stands at 6. `deb91557` was not moved.
Nothing was sent, uploaded, filed or registered. `__pycache__` was purged tree-wide before every
measurement cell.

---

## 2. THE FOUR ARMS, RE-DERIVED — not inherited

`__pycache__` purged before each. Claim pattern `untrained[- ]QCR`, the same one the enumeration
used, so the numbers are comparable.

| arm | method | files | claim files | zero-Spalart |
|---|---|---|---|---|
| **tracked** | `git ls-files`, then `git grep -al -aE` (**`-a`, not `-I`** — plain `-I` skips ~1,476 files marked binary, 11 of which contain no NUL byte) | **20,709** @ 23:53Z | **47** | **13** |
| **untracked** | `git ls-files --others --exclude-standard` | **1** (`.autostop-hold`) | 0 | 0 |
| **gitignored** | `git ls-files --others --ignored --exclude-standard -z \| xargs -0 grep -alE` | **37,254** | **3** | 1 |
| **run tree** | `/usr/bin/find /home/ubuntu/certonomous-runs/ -type f -print0`, **enumerated once**, NUL bytes counted (`-size -2M`/`+2M` are **not** complementary and cannot be used to partition) | **132,050** / 66 GB | **1** | — |

**The run-tree arm carried a seeded positive control** (`__probe_v5_grade_a28ea.txt`, containing the
claim string). It was the **only** hit in 132,050 files across a 9-minute grep, and it has been
removed and confirmed absent. **The control fired, so the zero is a measurement and not a silence.**

**Reconciliation with the enumeration's own figures, which were taken at 20:14Z/20:22Z, before the
repairs committed at 20:23:09Z.** It reported 20,698 tracked / 47 claim files / **15** zero-Spalart.
I get 20,709 / 47 / **13**. The two files repaired at `f956e348` — `docs/PRODUCT_LIST.md` and
`demo-output/website/CLOSURE_EVALUATION_PROTOCOL.md` — now carry Spalart and drop out: **15 − 2 = 13,
exactly.** The tracked file count moved by 11 because concurrent agents committed between the two
reads. The gitignored and run-tree arms reproduce to the file.

**The three gitignored hits are all under `dist/`**: `site/benchmarks.html` (3 Spalart),
`site/closure.html` (3), and `snapshot/lab_stats.json` (**0**). `lab_stats.json` is derived at build
from `build_benchmarks.py`, whose literal **is** repaired (`:115-117` names Spalart (2000) beside
`Ccr1 = 0.3`), and it picks the repair up only on a rebuild. That is the owner's and I did not touch
it.

---

## 3. V5 — GRADED AGAINST THE RULING AND ITS THREE AMENDMENTS

### 3.1 The enumeration reproduces exactly

All four sha256s on the rung's face were recomputed on the worktree and against
`git show HEAD:<path> | sha256sum`. **All four match, byte for byte.** The commit histories
reproduce: one commit each for the two JSONs and for `LADDER_V_RUNGS_V2_V7_V10`, and
`1a14e90b` + `fe612d03` for `QCR_ACTIVITY_CHECK`. All four carry **zero** occurrences of "Spalart".

### 3.2 The two withdrawals hold, and I would have made them independently

**"Left to its owner" is a routing rule, not a frame exclusion.** This is correct and the argument is
the right one: a refusal must name a property of the *surface*, not of a *person*. `fe612d03`
falsifies the stated ground for `QCR_ACTIVITY_CHECK` by execution — it appended a dated section
wholly below the signed text, 20 h 07 m after signing and three days before the refusal was written.
Refusal 4 rests on the identical sentence and cannot survive its sibling's fall.

**The container ground for the two JSONs holds, and it is the correct form of the argument.** L-44's
dated addendum needs a region below the freeze line. A Markdown record has one; **a JSON object has
no "below"** — text after the closing brace is not JSON, and a new key is a byte inserted inside the
frozen structure, which is a revision. I checked the cost is real rather than rhetorical: the
citation the round-5 package needs **is** in the package, at the sibling
`closure_challenge_round5_qcr.json`, `model.provenance` — *"Spalart QCR2000, Int. J. Heat Fluid Flow
21(3) 252-263 (2000), published constant adopted untrained"*. The refusal costs the package nothing.

### 3.3 The repairs are real, but the face's coordinates have already gone stale

The five repairs are present at HEAD and each names Spalart with the year **in the same sentence** as
the claim. Measured with the guard's own `_QCR` / `_CITED` regexes and its own sentence splitter,
applied file-wide: **`PRODUCT_LIST.md` 17 QCR-naming sentences, 13 unattributed** (the face says
17 → 13 — reproduces); **`CLOSURE_EVALUATION_PROTOCOL.md` 1 → 0** (reproduces). I opened all 13
survivors: none carries an untrained claim about our own model.

**RESIDUAL.** The face records the repairs at `PRODUCT_LIST.md:63,136,608,655` and
`CLOSURE_EVALUATION_PROTOCOL.md:391`. At HEAD they are at **`:63, :138, :610, :659`** and **`:392`** —
concurrent commits inserted lines above them within minutes of the enumeration being written. The
sites are real and the wording is right; the *coordinates* on the rung's face no longer resolve. A
face that pins line numbers in a corpus this concurrent will be stale before it is read.

### 3.4 What still blocks the rung — measured, not inherited

| # | surface | the claim | Spalart | in frame because |
|---|---|---|---|---|
| **1** | `sdk/scripts/closure_eval_battery/build_master_table.py` `:246`, `:371` | *"round 5 (untrained QCR2000 duct forward solve, …)"* | **0** | **it is a generator** — the ruling's frame is *"every surface a future build or edit can change, **plus the generators that write them**"* |
| **2** | `demo-output/website/closure_eval/closure_eval_master_table.md:20` | same sentence, emitted | **0** | tracked output of (1) |
| **3** | `demo-output/website/closure_eval/closure_eval_master_table.json:84` | same sentence, emitted | **0** | tracked output of (1) |
| **4** | `demo-output/website/campaign/LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md:121` | *"duct gains from the **untrained** QCR2000 term (nothing fitted)"* | **0** | a **withdrawn exclusion**, returned to frame by the enumeration itself |

Item (1) is decisive. The ruling `3af7bd2b` kept V5 open on **generator 1** with the words *"a
generator is the most load-bearing surface there is — it manufactures new copies after every
repair"*. Generator 1 is now repaired. **Generator 3 is not, and it is the same defect on the same
rung.** Item (4) is a site under *both* the literal predicate and the narrowed one: it is the
load-bearing claim about **our** model.

### 3.5 A frame hole the enumeration did not find, and no arm of the sweep can

**`demo-output/website/closure_challenge_round5_qcr_forward.json` makes the untrained claim about our
own model — as `"Ccr1": 0.3,` `"trained": false` — and matches NEITHER the sweep pattern
`untrained[- ]QCR` NOR the guard's `_QCR` + sentence predicate.** It carries zero occurrences of the
string "untrained". Every arm of the four-arm sweep is blind to it, and the only reason it appears in
the record at all is that a 2026-08-11 pass had already listed it as a refusal for an unrelated
reason.

This does not change its exclusion — the container ground holds for it. It changes what the frame's
reach claim is worth. **The face states "the two frozen JSONs" are among the 15 zero-Spalart claim
files. Only `MANIFEST.json` is; `forward.json` is not in the matched set at all.** A claim expressed
as JSON structure rather than as English prose is invisible to the whole instrument, and the rung's
frame is one surface wider than any of its four arms can see.

### 3.6 Six exclusions on the face carry no sha256 and no dated ground

The ruling's requirement is flat: exclusions are valid *"only when enumerated on this rung's face,
each with its sha256 and a dated refusal ground. An unenumerated exclusion is not a frame, it is a
gap."* The face enumerates **four**. Its classification paragraph then excludes **six more** in prose:
two Wu & Zhang surfaces plus `PRODUCT_LIST.md:351`, two held-out guard corpora, and four dated
records — **none with a hash, none with a dated refusal.**

I opened all six and the grounds are substantively right:
`CLOSURE_METHODS_COMPARISON.md:216` sits under the heading *"### 2.2 Wu & Zhang — rank 2, 0.0624
(SST-QCRC)"* and quotes their own description document; `closure_challenge_C2_error_decomposition.md:255`'s
*"the entry adds an untrained QCR2000 … term"* is the **rank-2** entry, established three bullets
above. Neither is a claim about our model.

But two of the six are **live, editable source files** — `campaign/V16_GRADE_HELDOUT_SETS.py` and
`sdk/tests/test_rank_claim_surfaces.py` — excluded on a real ground (*the uncited sentence is the
test datum*) that is nonetheless argued only in prose. Under the ruling's own literal test those are
gaps. **RESIDUAL, not a blocker**, because the narrowed predicate independently disposes of most of
the six and because naming them here is the repair the ruling asks for.

### 3.7 GRADE OF THE PREDICATE NARROWING — **legitimate, with two defects named**

The narrowing (`78eb5530`): *V5's site is where the untrained claim about **our own model** is made,
not every place the string QCR appears.*

**I tried to falsify it and could not.** The falsifier the ruling names is *a surface naming QCR
without the untrained claim, where a reader would be misled by the absence of attribution.* My
closest candidate is `PRODUCT_LIST.md:462` — *"QCR2000 built as a turbulence-model class (~180 lines,
no rebuild)"* — where "built" could be read as origination. I do not think it survives: V5's own
clause 1 asks for *"`git log --follow` on the QCR implementation proving in-house history"*, so the
rung explicitly wants us to claim the *implementation*, and the sentence claims exactly that. **No
clean instance produced. The predicate stands.**

**DEFECT 1 — the textual argument does not hold.** The ruling says *"the rung states its own purpose
in the same sentence as its criterion."* The rung reads: *"confirm zero fitted parameters anywhere in
the duct path (the 'untrained' claim is load-bearing — prove it by showing there is nothing that
could be fitted)**;** Spalart (2000) cited wherever QCR is named."* The parenthetical attaches to the
**zero-fitted-parameters** clause and is separated from the citation clause by a semicolon. It is the
same sentence and a different clause. The citation clause reads flatly, without a purpose rider.
**The narrowing does not follow from the rung's text; it stands on discrimination alone**, which is
the ruling's other and better argument.

**DEFECT 2 — the sequencing is the shape this ruling rejected the two-site reading for.** `78eb5530`
landed at 20:26:20Z. `f956e348` landed at 20:23:09Z — **3 m 11 s earlier** — and had just measured 13
unattributed QCR sentences in `PRODUCT_LIST.md` and declined to repair them *"because the predicate
question in (b) is unruled."* The ruling then made **exactly those 13** not-sites. The two-site
reading was rejected because *"a criterion that narrows by being copied is the bar moving under the
measurement"*; this criterion narrowed three minutes after the cost of not narrowing was measured and
reported by the pass that would have paid it.

**WHY IT SURVIVES BOTH DEFECTS.** The ruling's three self-tests are (a) stated on the face with its
reason, (b) before the next grade, (c) discriminates rather than shrinks. It passes (a) and (b)
plainly. **I tested (c) by execution and it passes: under the narrowed predicate, four in-frame sites
survive and V5 still FAILS.** A narrowing that does not save the rung it narrows is not a narrowing
bought to reach a verdict. It is also the narrowing that forced the enumeration that **cost** the
rung two exclusions. Net, it made the criterion sharper and the rung harder.

### 3.8 **VERDICT — V5: FAIL**

**What blocks it:** the third generator `sdk/scripts/closure_eval_battery/build_master_table.py:246,371`
and its two tracked outputs, and the withdrawn exclusion
`campaign/LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md:121`. Four in-frame tracked surfaces make the
untrained claim about our own model with zero Spalart, and one of them is a generator.

**FALSIFIER.** Name Spalart (2000) with the year in the same sentence at `build_master_table.py:246`
and `:371`, re-run the eval battery so `closure_eval_master_table.md` and `.json` carry it, and add
an L-44 dated addendum to `LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` by its owner. Then re-run the four
arms with the positive control: if the tracked arm returns **zero** in-frame zero-Spalart surfaces
carrying the untrained claim about our own model, this FAIL is wrong and V5 passes. **A single
counterexample — one in-frame tracked surface I have classified out that a reader classifies in —
also falsifies the *reasoning* here, independently of the verdict.**

---

## 4. V14 — GRADED AGAINST THE DENOMINATOR RULING

### 4.1 The widening is what it says it is

`_VALUE_BOARD_SIZE` at `scripts/self_audit.py` now reads
`(?:\brank[ \-]?(?P<n>…)|\b(?P<o>\d{1,3})(?:st|nd|rd|th)\b\*{0,2})\s+of\s+\*{0,2}(?P<v>…)\b(?![.,]\d)`.
The `rank` branch is character-for-character unchanged; the `(?P<o>…)` alternative is the whole
widening; `(?![.,]\d)` is the decimal fix. Read at HEAD, not at the commit message.

### 4.2 Measured cost, re-run at 2026-08-16T00:08Z

| measure | widening pass reported (23:02Z) | **this grade (00:08Z)** |
|---|---|---|
| value faults | 26 | **28** |
| **travelling (the GATING arm)** | **3** | **3** |
| lab records (reported, not gated) | 23 | **25** |
| matched-and-not-graded, each with its reason | 117 | **118** |
| rank claims found | 498 | **503** |
| tracked paths considered / opened | 20,708 / — | **20,713 / 20,526** (90 archive members) |
| **false positives on the travelling arm** | **0 of 3** | **0 of 3** |

The +2 on the lab-record arm is `campaign/RULE_O_DENOMINATOR_MEASUREMENT_2026-08-15.md:241` and
`docs/DOCKET.md:570` — the D199 row and its write-up, both committed **after** the widening was
measured. The instrument faulted the record of its own measurement. That is correct behaviour and it
is why the gate is travelling-scoped.

**The travelling arm reproduces exactly at 3, and all three are in
`dist/certonomous-demo.zip!certonomous-demo/site/closure.html` — `:341` (`3rd of 5`), `:502`
(`rank 1 of 5`), `:503` (`comparable`).**

### 4.3 THE FINDING THAT DECIDES THE RUNG — the three travelling faults are a stale build

`dist/certonomous-demo.zip` was built **2026-08-14T21:16:50Z**. The tracked source of that member,
`demo-output/website/closure.html`, was last committed **2026-08-15T19:53:29Z**. Read at HEAD:

- **`:353-358`** — *"…and the tie is gone.* **[struck]** *the case falls to 3rd of 5, and our
  best-on-board count drops 5 of 8 → 4 of 8* **[/struck]** *— struck 2026-08-15: both of those were
  four-entry-board figures … duct places **4th of 7**, and the best-on-board count is **2 of 8**."*
- **`:586`** — *"holds no official rank — **rank 1 of 7 entrants**"*, with **`:590-593`** carrying the
  old *"rank 1 of 5 … comparable to its margin"* struck, dated 2026-08-15, and corrected to
  **177% of the margin**.
- **`benchmarks.html:148`** — *"the seed uncertainty is **larger** than the margin, **not comparable**
  to it"*, against Yang, naming the six-entry board and both retrieval dates.

**Every live four-entry claim the ruling said stands is repaired at its tracked source. All three
travelling faults are artefacts of a bundle built before the corrections landed.** The residual is a
rebuild of `dist/`, which is the owner's and which this grade may not perform.

### 4.4 REFUTATION 1 — verified by my own execution, and two of its three numbers corrected

The ruling states `check_rank_claim_values` misses this class *"for exactly one reason"*. **It does
not survive.** Running `_VALUE_BOARD_SIZE` and `_in_board_context` over the archive member:

| member line | match | `_in_board_context` | nearest `_RANK_BOARD` word |
|---|---|---|---|
| `:341` | `3rd of 5` | **True** | 18 chars (`board`) — **faults** |
| `:434` | `2nd of 5` | **False** | **1,219** chars (`board`) |
| `:435` | `3rd of 5` | **False** | **1,443** chars (`board`) |
| `:436` | `3rd of 5` | **False** | **1,319** chars (`leaderboard`) |
| `:502` | `rank 1 of 5` | True | 34 chars — faults |

`_RANK_WINDOW = 300`. The three sibling confirmed-true bare ordinals are **4 to 5 times** outside it.
**The pattern is not why they miss; a second gate is.** The refutation is confirmed.

**Two of its three numbers differ from D206's** (1,224 / 1,448 / 1,319 vs my 1,219 / 1,443 / 1,319).
The gap is a measurement convention — D206 appears to measure to the board word's *start*, I measure
to its *nearest edge*, and `board` is 5 characters. The substance is identical and the conclusion is
untouched. Printed because a number on a rung's face should be reproducible or explained.

**The widening agent's refusal to widen `_RANK_WINDOW` was correct.** The constant is shared with
`check_rank_claim_surfaces`; a 5× expansion bought to make a control pass is the tuning the ruling
forbids.

### 4.5 REFUTATION 2 — verified

`demo-output/website/closure.html:426` at HEAD is a sentence about the margin over Yang and the
per-case spread. It does not carry the claim. **The claim is at `:482`, inside a strike element**
(the tags are described here and never written — this corpus's masker has no parser and an unmatched
closer reaches backwards to the nearest dangling opener), **struck 2026-08-15**, and corrected at
`:488` — *"Its count was wrong: it is **seven** of the eight rows, not six"* — and at `:490` against
the six-entry board retrieved 2026-08-11T23:33Z and re-verified 2026-08-14T21:01Z. **`426` is the
line number inside the archive member**, where the same sentence ends `</p>` and is not struck.
Confirmed.

### 4.6 REFUTATION 3 — re-derived from the primary sources, and it is exact

From `LIVE_BOARD` read by AST out of `sdk/scripts/probability_of_rank.py` and
`round5_per_case_full` out of `closure_challenge_round5_qcr.json`, head to head over the eight cases:

| entrant | cases we win |
|---|---|
| Liu, Wang, Zhao & Xiao | 7 |
| Montoya, Oulghelou & Cinnella | 7 |
| Wu & Zhang | 5 |
| Tian, Buchanan, Hickel & Dwight | 5 |
| Yang (**leader**) | **4** |
| Reissmann, Fang & Sandberg | **4** |

Cases-won multiset **{4, 4, 5, 5, 7, 7}**. Best-on-board **2**, earned (ours after the decline gate)
**0**. **Admissible union = {0, 2, 4, 5, 7} — five of the nine integers 0…8, not seven.** D199's
union does not reproduce. Confirmed exactly.

### 4.7 GRADE OF THE "HUMAN READING" CONCESSION — **NOT legitimate. This is the rung being excused.**

The ruling says `:342`'s `5 of 8 → 4 of 8` is *"**structurally unreachable** by any board arithmetic,
because `4` is simultaneously the withdrawn best-on-board count and the correct cases-won count
against the leader. That one needs a human reading."*

**Three findings, each executed.**

**(i) The arithmetic already reaches this exact quantity and this exact wrong value, at eleven
tracked sites.** `_BEST_COUNT` faults `best-on-board 4 of eight` in `CLOSURE_CHALLENGE_STATUS.md:756`,
`agenda/docket.json:4450`, `LADDER_V_PASS2_2026-08-11.md:79`, `LADDER_V_PASS3_COLD_2026-08-11.md:265`,
`LADDER_V_V13_CLOSEOUT.md:44`, `LADDER_V_V15_LADDER_TEXT_CLAIMS.md:155`, and — decisively —
**`campaign/LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md:120`, whose sentence is `best-on-board 4 of 8 (was
5)`: the identical claim, the identical digits, in Markdown.** Each is graded against the derived
`2 of 8` and each faults. If `4 of 8` needed a human reading, none of these eleven could have been
decided by a rule, and all eleven were.

**(ii) The real obstruction is a newline in a character class, and I proved it.** `_BEST_COUNT` is
`\bbest\b[^.\n]{0,80}?\b(…)\s+of\s+(?:the\s+)?(?:eight|8)\b`. In the archive member the sentence wraps:
`…and our best-on-board count` ends line 341, `drops <b>5 of 8 → 4 of 8</b>` begins line 342. The gap
between `best` and the count is **25 characters — comfortably inside the 80-character budget** — but
it contains a `\n`, which `[^.\n]` excludes. Executed: the pattern **does not** match the shipped
fragment, and **does** match the identical text with the newline replaced by a space. **That is a
line break, not board arithmetic.**

**(iii) The ambiguity argument fails on its own terms.** It treats the claim as a bare `4 of 8`. The
sentence is not bare — it says *"our **best-on-board count** drops"*, naming its own quantity — and
`_BEST_COUNT` binds on that noun phrase rather than on a loose ordinal. That is precisely the
"grade only what the sentence names" design the **same commit** used to justify grading the bare
branch's denominator and not its numerator. The ruling applied the principle in one place and
abandoned it in the other.

**So the concession is wrong, and it is the class of wrongness that matters most: an instrument
defect described as an impossibility.** `_in_board_context`'s 300-character window (refutation 1) and
`_BEST_COUNT`'s `[^.\n]` class are the same failure — a constant calibrated on flowing Markdown,
applied to wrapped HTML. Refutation 1 was correctly filed as a measurable gap with its distances.
This one was written into a ruling as a property of the world.

**Mitigating, and stated so the finding is not oversold:** the claim `:342` excuses is **already
struck and corrected at its tracked source** (§4.3). The concession cost the corpus nothing. It is
wrong as reasoning and it should not stand on the rung's face.

### 4.8 The instruments cannot confirm this rung — reported as facts about the guards

- **`board_placement_faults`** on the shipping member: **0 rule-A faults, 0 rule-B faults.** It found
  four placements; **three have no named published entrant** (`who is None → continue`) and the fourth
  (`Wu`, `rank-2`) agrees with the pin. **D151 confirmed by execution: rule A binds ordinals to named
  published entrants and is structurally incapable of faulting a claim about *our own* placement.**
  It has no arithmetic predicate (D88); `_PLACE_ADJUDICATED = 400` and the skip additionally requires
  the *same* entrant be named (D85); and it masks nothing — I passed raw archive text and the strikes
  were never stripped (**there is no strike stripper**, `29452c51`).
- **`check_rank_claim_surfaces`**: returns **WARN**. Its frame line confirms it opens the archive
  (*"plus the members of 1 shipping archive(s)"*, 90 members). Its 33 detail items name **not one
  `dist/certonomous-demo.zip!` path.** It names none of the live claims in the archive it opened.
- **Neither instrument's silence is evidence.** Every V14 conclusion above rests on re-derivation:
  the board read by AST, the per-case values read from the entry of record, the regexes executed
  against the archive bytes.

### 4.9 What the frame structurally cannot contain — the rung requires this be stated

Taken from the check's own docstring and confirmed against its frame line: anything not UTF-8
(**every compiled PDF**, and `latex/closure_challenge_report.pdf` is this corpus's largest single
concentration of withdrawn claims); untracked files; files over 4 MB; render-time text; claims
outside `_RANK_CLAIM`'s vocabulary; claims with no number at all. **No PDF claim is graded in this
document.** PDFs cannot be read from a text extract — `\sout{}` is strike-and-keep, so an extract
shows a withdrawn claim as live text — and rendering to PNG was outside the time this grade had. That
is a stated blind spot, not a clean result.

### 4.10 **VERDICT — V14: PASS WITH RESIDUALS**

The rung's criterion is a **method** test: a repo-wide mechanical search, proving its own reach and
stating what its frame cannot contain, failing *"if its method is a list rather than a search."* Under
the ruling (reach repo-wide, gating travelling-scoped) the method now satisfies that: 20,713 tracked
paths plus 90 archive members considered mechanically, 503 rank claims found, blind spots enumerated
in the instrument itself, **0 false positives on the gating arm**, and every claim it was built to
catch repaired at source.

**RESIDUALS, each named:**

1. **The shipping bundle is stale.** `dist/certonomous-demo.zip` (2026-08-14T21:16Z) ships three true
   travelling faults at member `closure.html:341, :502, :503`, all corrected on the tracked source.
   **Repair is a rebuild; it is the owner's.**
2. **`_in_board_context`'s 300-character window** leaves three confirmed-true bare ordinals unfaulted
   at 1,219 / 1,443 / 1,319 characters. Correctly not widened. Open for the owner of both checks.
3. **`_BEST_COUNT`'s `[^.\n]` class** cannot cross a line break, which is the sole reason `:342` is
   unreached (§4.7). Not a rung defect; an instrument defect currently recorded on the rung's face as
   an impossibility.
4. **`_BEST_COUNT` carries the same `\b`-after-digits shape** on `(?:eight|8)\b`, so `of 8.5` would
   match. No instance in this corpus. Reported by the widening pass and still open.
5. **D208's confirmed execution gap on `0.0029` at `closure.html:411`** produced no fault in my run.
   (`benchmarks.html:148` is repaired at source.)
6. **The PDF arm is unmeasured** (§4.9).

**FALSIFIER.** Rebuild `dist/certonomous-demo.zip` from the current tracked site and re-run
`check_rank_claim_values`. **If the travelling arm does not go to zero, or if any *tracked* travelling
surface faults, this PASS is wrong and V14 is FAIL.** Equally: **a grader who reads V14's gate as
"no travelling fault may stand, whatever its cause" should read this rung as FAIL until the rebuild** —
I have named the residual precisely so that disagreement is a one-step check and not a matter of
opinion.

### 4.11 GRADE OF THE DENOMINATOR RULING — **legitimate, and it survives its own falsifier**

**Reach repo-wide, gating travelling-scoped: supported by my own measurement.** 3 travelling faults
with **0 false positives**, against 25 lab-record faults which are overwhelmingly *correct dated
records* — `LADDER_V_PASS2`, `LADDER_V_PASS3_COLD`, `LADDER_V_V13_CLOSEOUT` and
`LADDER_V_RUNGS_V2_V7_V10` recording the four-entry board as it stood when they were written. Repo-wide
*gating* would fault the lab's own history and its instruments' comments. It is not stricter; it is
unusable. Confirmed.

**Its stated falsifier is NOT triggered:** *"a travelling surface whose correct claim this predicate
faults."* All three travelling faults are true of the live board. The ruling stands.

**Two of its subsidiary claims do not:** *"exactly one reason"* (§4.4, refuted — a second gate blocks
three of the four claims the widening was bought to catch) and *"structurally unreachable … needs a
human reading"* (§4.7, refuted — a newline in a character class). **The ruling's core holds; two of
its arguments were wrong; the widening agent found the first and disclosed it in the same commit that
executed the ruling, which is the behaviour the ruling asked for.**

---

## 5. SUMMARY

| rung | verdict | what decides it |
|---|---|---|
| **V5** | **FAIL** | the third generator `build_master_table.py:246,371`, its two tracked outputs, and `LADDER_V_RUNGS_V2_V7_V10:121` — four in-frame surfaces claiming untrained QCR about our own model with zero Spalart |
| **V14** | **PASS WITH RESIDUALS** (6, named in §4.10) | the search is mechanical, reaches repo-wide, states its blind spots, and gates at 0 false positives; every claim is repaired at source; the three travelling faults are a `dist/` bundle built before the corrections |

| ruling | grade |
|---|---|
| V5's predicate narrowing (`78eb5530`) | **legitimate** — its textual argument fails and its sequencing is the shape it condemned, but it discriminates, it is stated with its falsifier, I could not falsify it, and it does not save the rung |
| V14's human-reading concession (`9b9951a1`) | **NOT legitimate** — the rung being excused; the same rule faults the same value at eleven sites and the obstruction is a line break |
| V14's reach/gating split (`9b9951a1`) | **legitimate** — re-measured, 0 false positives on the gating arm, falsifier not triggered |

**Docket: D222, D223, D224.**

---

*No solver run. No scoring call; ledger at 6. `deb91557` not moved. Nothing sent — submissions are
PARKED. `dist/`, `demo-output/website/latex/`, `scripts/self_audit.py`, `docs/USING_THIS_LAB.md`,
`LAPTOP_SHOOT.md`, `motorbike-video/` and `.autostop-hold` were read and never written. The run-tree
probe was seeded, fired, and removed.*
