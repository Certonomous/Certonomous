# Ladder V — rung V5 (QCR provenance) graded for closure, 2026-08-15

**Verdict: FAIL — V5 does not close this round.** Not a regression: nothing that was
verified has come undone, and the two gaps the ledger carried as open are genuinely
closed. V5 fails because the two gaps were never the rung's criterion, the criterion
itself has never been settled by a ruling, and a mechanical derivation of the surface
set finds four sites carrying the untrained claim that no pass has ever counted.

Graded by the independent measurer under **R-ISOLATE**. Executed, not read: every
statement below was re-derived at the tree, and where a prior record is quoted it is
quoted in order to be checked, not in order to be inherited.

---

## 0. Independence, and why the repository cannot establish it

I wrote none of `e071075d`, `514876b0` (the gap-closing commits, 2026-08-11) or
`0b0041b1` (the records repair, 2026-08-15) that wrote the paragraph under grade.

**The git author field cannot show this.** All three commits carry
`Ubuntu <ubuntu@ip-172-31-43-247.us-east-2.compute.internal>`, as does every commit on
this box, committer field included. Author metadata does not discriminate between agents
here and no grader should offer it as proof.

**Provenance by dispatch clock instead, and the first form of it fails.** The obvious
argument — "my session opened after the commit landed" — does **not** work for
`0b0041b1`. The session container I run inside (`64b13819-…`) has been open since
**2026-08-04T14:54:48Z**; its scratchpad directory was created 2026-08-14T20:26:01Z. Both
precede `0b0041b1` at **2026-08-15T01:40:43Z**. Session-level timestamps clear me of the
2026-08-11 commits and of nothing else.

**What does establish it** is the agent-thread dispatch record, which is out of the
repository: this grading task first appears in the session transcript at
**2026-08-15T02:09:39.041Z**, and my first tool call ran at 02:09:44Z — **28 minutes 56
seconds after `0b0041b1` was committed**, and 4 days after `e071075d`/`514876b0`. My
thread did not exist when any of the three were authored.

**The finding that generalises.** Rung independence in this lab is not verifiable from
the repository at all. It is verifiable only from `~/.claude/projects/…jsonl` dispatch
timestamps, which are untracked, unbacked-up, per-machine, and trivially outlived by the
records that cite them. Every "graded by a non-author" claim in the ladder rests on
evidence that no reader of the repository can check. That is a structural weakness of
R-ISOLATE as currently practised, not of any particular grade.

---

## 1. Declared scope (R-CONVERGE)

**IN SCOPE:**

1. V5's closing condition **as written** in `campaign/LADDER_V_TRIPLE_VERIFICATION.md`
   lines 30–33, and whether that condition is met at HEAD.
2. The two claimed closures (`benchmarks.html`, `CLOSURE_CHALLENGE_STATUS.md`) confirmed
   by execution at the current tree, and the ancestry of both commits.
3. **Mechanical derivation of the full surface set** for leg 3 — every site making the
   untrained claim — across all three arms of the corpus, whole repository, not the
   `demo-output/website/` frame prior passes used.
4. Re-check of V5's refused surfaces for stale refusals.
5. Whether the records repair at `0b0041b1` overstated the closure.

**OUT OF SCOPE, findings FILED as docket rows rather than appended to the rung:**

- **V5 legs 1 and 2** (in-house `git log --follow` history; the structural untrained
  proof). Not re-executed. I inherit them from `LADDER_V_PASS1_2026-08-11.md` §A5 and say
  so — they are not part of this grade's evidence and this grade does not strengthen them.
- `dist/` bundle currency beyond the V5 claim specifically. **D112(i) and D118 own it**;
  I measured only whether the V5 correction reached the shipped copies.
- Every other rung. Every other item in GREEN REQUIRES.
- The six corrections that have not travelled — the repair itself marks these
  not-re-measured and they stay that way here.

**No solver run, no scoring call, no send, nothing filed or registered. The scoring pin
`deb91557` was not touched.** No test cell was executed, so the stale-bytecode rule did
not arise; the one `python3` invocation in this grade reads a JSON file and imports
nothing from the tree. No `__pycache__` was created or consumed.

---

## 2. The closing condition, read as written — and it is ambiguous

`campaign/LADDER_V_TRIPLE_VERIFICATION.md:30–33`, the pre-registered text, in full:

> **V5. QCR provenance**: `git log --follow` on the QCR implementation proving in-house
> history; confirm zero fitted parameters anywhere in the duct path (the "untrained" claim
> is load-bearing — prove it by showing there is nothing that could be fitted);
> **Spalart (2000) cited wherever QCR is named.**

**Leg 3 is "wherever QCR is named."** Not "wherever the untrained claim is made." The
distinction is not academic: at HEAD, **118 tracked files name QCR** and **29 of the 64
that also carry untrained-claim vocabulary contain no occurrence of "Spalart"** (§4).
Under the literal condition, leg 3 does not hold and is not close to holding.

Three different criteria are live in the records, and each narrows the one before it:

| # | criterion | where it is stated | met at HEAD? |
|---|---|---|---|
| C1 | Spalart cited **wherever QCR is named** | the ladder itself, `:32–33` | **NO** |
| C2 | Spalart cited wherever a surface carries the **load-bearing untrained / nothing-fitted claim about OUR model** | `LADDER_V_PASS1_2026-08-11.md` §A5 leg 3, which adopted it after finding C1 failed | **NO** (§4) |
| C3 | Spalart cited at **the two sites the close-out named** | `LADDER_V_V13_CLOSEOUT.md` §7 item 9 → the ledger's GREEN REQUIRES → `0b0041b1` | **YES** (§3) |

**No ruling ever chose between them.** `LADDER_V_PASS1_2026-08-11.md:486–487` closes leg 3
with *"**Chief ruling requested** on (a) the frame, and (b) who fixes the public page and
the frozen artifacts."* The chief's addendum (`e59ae644`, in the same file at 571–657)
issues **Ruling 1** (the pre-registration file's freeze) and **Ruling 2** (the stale §4.1
citations) — and never answers (a). A repository-wide search for a ruling settling V5's
frame returns nothing.

So the narrowing from C1 to C3 happened by **transcription**, not by adjudication: Pass 1
named five gaps; the V13 close-out's item 9 listed two of them; the ledger's GREEN
REQUIRES copied the close-out; the records repair verified what the ledger named. Each
step is individually defensible and the composition silently dropped three exceptions and
the chief's explicit refusal to upgrade the rung.

**That the condition is ambiguous is itself a finding of this grade**, and it is the
first thing that has to be settled before any grader can return PASS. It is not mine to
settle: I am the measurer.

---

## 3. What is verified true (executed at the current tree)

**Both closures confirmed.** Read at HEAD, not from any commit message:

| site | text at HEAD | verdict |
|---|---|---|
| `demo-output/website/benchmarks.html:124–127` | *"the untrained QCR2000 physics term — its one coefficient `Ccr1 = 0.3` is **Spalart (2000)**'s published constant, nothing fitted to anything"* | **closed** |
| `demo-output/website/benchmarks.html:145–147` | *"replaced outright by the untrained QCR2000 constitutive term — **Spalart (2000)**, run at its published `Ccr1 = 0.3` and overridden nowhere"* | **closed** |
| `demo-output/website/CLOSURE_CHALLENGE_STATUS.md:448–449` | *"`Ccr1 = 0.3` — **Spalart (2000)**'s published constant, not ours; nothing fitted to anything"* | **closed**, and it carries "nothing fitted to anything" in the same sentence as the repair states |
| `demo-output/website/CLOSURE_CHALLENGE_STATUS.md:1008–1009` | *"physics instead of a fit: the untrained QCR2000 constitutive term of **Spalart (2000)**, run at his published `Ccr1 = 0.3`"* | **closed** |

*Note on the anchors: the repair cites `:126`/`:146` and `:449`/`:1009`. Line-anchored
citations into a wrapped paragraph name one line of a sentence that spans several; the
claim sentences begin at 124 and 145, and 448 and 1008. The repair's anchors land inside
the correct sentences. Recorded because a later reader opening `:126` alone sees a
fragment.*

**Ancestry, re-derived with `git merge-base --is-ancestor` at HEAD:** `e071075d` **YES**,
`514876b0` **YES**, `0b0041b1` **YES**.

**The staleness mechanism reproduces.** `e071075d` at 2026-08-11T01:36:17Z, `514876b0` at
01:36:30Z, against the ledger table's own `d06edc62` at 01:25:33Z. Eleven minutes, exactly
as the repair states. The repair is right about the mechanism and right about the
direction of the error.

**Both gap-closing commits did their generator check first**, which is the part of them
worth keeping: `e071075d` established that nothing writes `benchmarks.html`
(`build_benchmarks.py` writes `benchmarks.json` and `.png`, not the page), and `514876b0`
that nothing writes `CLOSURE_CHALLENGE_STATUS.md`. Both re-confirmed here — and §5 is what
that same discipline finds when it is pointed at the *machine-readable* twin of the page.

**No stale copy of either fixed file exists anywhere in the corpus.** Swept across all
three arms (§4): `CLOSURE_CHALLENGE_STATUS.md` exists once. `benchmarks.html` exists
twice — the tracked source and `dist/certonomous-demo/site/benchmarks.html`, which is
**gitignored** and **does carry the citation** (3 Spalart occurrences, both claim sites
attributed; rebuilt 2026-08-12T16:31Z, after `e071075d`). On this correction the fix
travelled to the ignored arm. Recorded as a positive result, because it is the arm where
this lab has been bitten repeatedly.

---

## 4. The surface set, derived mechanically — frames and arms

**Frames stated.** This shell's `grep` is a function wrapping `ugrep --ignore-files`,
which honours `.gitignore` and sees roughly a quarter of the tree; its `find` is `bfs`.
Every measurement below used `git grep`, `/usr/bin/grep`, and `git ls-files`. Nothing in
this section was measured with the shell's own `grep` or `find`.

**Three arms, each enumerated by the only instrument that reaches it:**

| arm | enumerator | size at sweep time | re-measured 35 min later |
|---|---|---|---|
| tracked | `git grep`, `git ls-files` | — | 20,679 files |
| untracked, not ignored | `git ls-files --others --exclude-standard` | 3 files | 4 files |
| **gitignored** | `git ls-files --others --ignored --exclude-standard` + `/usr/bin/grep` | **37,242 files** | 37,255 files |

*Both columns are given because four agents are working concurrently and the corpus moved
under the sweep. Every classification below is against the tree as it stood during the
sweep; the drift is in files no arm's query matched.*

**Frame control, executed.** `git grep -lI untrained -- dist/` returns **nothing**;
`git grep -lI --untracked untrained -- dist/` returns **nothing**;
`/usr/bin/grep -rlI untrained dist/` returns **three files**. The third arm is real,
non-empty on this exact query, and invisible to both git-native instruments. My arm-3
method returned `dist/certonomous-demo/site/benchmarks.html` — a file neither other arm
can see — which is the positive control for the method.

**Second control, planted decoy.** A file containing the full claim string was written
into `dist/`, found by the untracked-arm instrument, and removed. Confirmed absent after.
(It landed in arm 2 rather than arm 3 — `.gitignore` does not match that path — which is
itself worth knowing: `dist/` is *not* uniformly ignored, so an arm-2-only sweep can pick
up some `dist/` files and miss others. Arm 3's own control is the paragraph above.)

**Derivation, not a check of four handed line numbers.** Candidate pool = files that name
QCR (`\bQCR\b|kOmegaSSTQCR|QCR2000|SA-QCR`) **and** carry untrained-claim vocabulary
(`untrained|nothing fitted|Ccr1|"trained": false`), then partitioned on whether the file
contains "Spalart" at all:

| arm | names QCR | candidates | **candidates with no Spalart** |
|---|---|---|---|
| tracked | 118 | 64 | **29** |
| untracked | 0 | 0 | 0 |
| gitignored | 11 | 5 | 5 (see below) |

All 29 tracked and all 5 ignored were opened and classified by reading the matching lines.

**Correctly excluded** (the class Pass 1 also excluded, re-derived independently here):

- **Someone else's model.** `CLOSURE_METHODS_COMPARISON.md:216` and
  `closure_challenge_C2_error_decomposition.md:255` describe **Wu & Zhang's** SST-QCRC and
  its `c_r = 0.3`. Not our claim.
- **Quotation and test fixture.** `V16_GRADE.md`, `V15_ROUND5_NUMBER_RECONCILIATION.md`,
  `V16_AUTHOR_HELDOUT_SET.py`, `V16_GRADE_HELDOUT_SETS.py`,
  `sdk/tests/test_rank_claim_surfaces.py` — all quoting the Wu & Zhang sentence as guard
  input.
- **Meta-reference.** `LADDER_V_V13_PENDING2_MEASURED_2026-08-15.md`,
  `LADDER_V_V15_ROUND4.md`, `LADDER_V_V8_REVERIFICATION_2026-08-11.md` — these discuss
  *the untrained-path compliance line* rather than asserting the claim.
- **Unrelated idiom.** `dafoam/ladder-b/S1_*`, `sdk/scripts/fit_cost_scaling.py`,
  `sdk/tests/test_pope_basis.py` — "nothing fitted" used of positive controls and cost
  curves, no QCR content.
- **Machine artifacts.** `log.simpleFoam` files, `solve_registry/*.log`, VTK binaries,
  `closure_challenge_report.aux`/`.toc` (LaTeX byproducts of a `.tex` that carries 4
  Spalart citations and is out-of-touch by dispatch).
- **`sdk/openfoam/qcr/kOmegaSSTQCR/kOmegaSSTQCR.C`.** Contains the `0.3` literal but no
  prose claim; the attribution lives in its own header, `kOmegaSSTQCR.H:11` — *"c_r = 0.3
  (Spalart 2000, untrained)"* — and `:20`, `:61`. The compilation unit is attributed.
  Verified rather than inherited, because the 08-08 record cites the pair as ".C/.H" and a
  reader checking only the `.C` would find nothing.
- **`docs/PRODUCT_LIST.md`** — 7 untrained-QCR mentions, no Spalart. Explicitly declared
  outside the rung's scope by the 08-08 pass and never brought back in. Flagged, not
  counted; whoever settles the frame should decide it deliberately rather than by omission.

**UNMET SITES — carrying the untrained claim about our own model, no attribution, never
counted by any V5 execution:**

| # | surface | arm | what it says | why it counts |
|---|---|---|---|---|
| **U1** | `sdk/scripts/build_benchmarks.py:106` | tracked | `"…round-5 untrained QCR2000 forward solve on the ducts…"` inside the `our_entry` string | **the generator.** `e071075d` correctly checked that nothing generates `benchmarks.html` — and the string it did not look at is the one this script emits |
| **U2** | `demo-output/website/benchmarks.json` (`/closure_challenge/our_entry`) | tracked | same string, written by U1 at `build_benchmarks.py:346` | the **machine-readable twin of the page that was fixed**, on the same public surface |
| **U3** | `demo-output/website/wall/wall.json:56` | tracked | same string, via `lab_stats.research_programs()` → `build_wall.py:333` | third copy, shipped |
| **U4** | `dist/certonomous-demo/snapshot/lab_stats.json` | **gitignored** | same string | fourth copy, in the arm no git instrument reaches |
| **U5** | `campaign/LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md:121` | tracked | *"duct gains from the **untrained** QCR2000 term (nothing fitted)."* | the **exact load-bearing phrase**, zero Spalart in the file. Refused by the 08-08 pass as another agent's signed report and then **never carried forward into the 08-11 five** |

**U1–U4 are one defect with four faces**, and the shape is the one this lab keeps being
bitten by: a hand-fix landed on the HTML page while the generator that writes the same
sentence into three shipped JSON surfaces was never opened. The next
`build_benchmarks.py` run rewrites `benchmarks.json` with the unattributed claim
regardless of what any page says. **A correction to an output that a generator will
rewrite is not a correction** — which is `e071075d`'s own stated principle, applied one
file to its left.

**U5 raises the refused count from three to four.** The ledger's repaired paragraph says
*"The three surfaces V5 correctly refused — two frozen artifacts and another agent's
signed report."* There are four refusals across V5's two executions: the 08-08 pass
refused `LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` for the identical reason, and the 08-11
re-run's table does not carry it.

---

## 5. The refused surfaces, re-checked

A refusal is a judgement and goes stale like any other. Each was re-measured, not read.

| surface | refusal ground | state at HEAD | verdict |
|---|---|---|---|
| `closure_challenge_submission_round5/MANIFEST.json` | frozen artifact; A2's chain rests on immutability | **single commit `07a7fe9e`, 2026-08-07T20:51:51Z, never amended.** Worktree sha256 `58f4f5a5…` identical to `git show HEAD:` | **refusal HOLDS** |
| `closure_challenge_round5_qcr_forward.json` | frozen artifact | **single commit `e865076b`, 2026-08-07T20:38:52Z, never amended.** Worktree sha256 `7e6c0d85…` identical to HEAD | **refusal HOLDS** |
| `campaign/QCR_ACTIVITY_CHECK_2026-08-08.md` | *"another verification agent's signed report, left to its owner"* | **TWO commits.** `1a14e90b` (2026-08-08T02:18:29Z) signed it; **`fe612d03` (2026-08-08T22:25:35Z) amended it** with a dated additive addendum — *"the hills SST control leg gets its registry log line"* — 20 hours later and **three days before the refusal was written** | **refusal's GROUND is stale** |
| `campaign/LADDER_V_RUNGS_V2_V7_V10_2026-08-08.md` | signed report of another verification agent (08-08 pass) | single commit `49f71b8c`, never amended | **refusal HOLDS on its ground** — but it was dropped from the count (U5) |

**On `QCR_ACTIVITY_CHECK_2026-08-08.md`.** The refusal is not wrong to decline the edit —
a grader should not edit another agent's report and neither should a verification pass.
But its **stated reason** does not survive contact with the file's own history: the file
had already accepted, from a subsequent audit pass, precisely the class of change V5
would have made — a dated, additive, below-the-line note that touches nothing above it.
"Left to its owner" describes a file that is closed to others. This one is not.
`fe612d03` is the counterexample, and it predates the refusal.

Note also that this surface is a gap under **C1 only**: it carries 27 QCR mentions and
**zero occurrences of "untrained"**, so under C2 it is not a claim site at all. Which
of the two it is depends entirely on the frame ruling that was requested and never issued.

**Both frozen refusals hold permanently, and that is the structural point:** under C1,
V5 can **never** reach a plain PASS, because two of its five exceptions sit on artifacts
that may take a dated addendum but may never take a revision (L-44), and a `"trained":
false` JSON field cannot carry a citation without being revised. Closing V5 therefore
requires a **frame ruling**, not more edits. That is the single most useful thing this
grade has to hand back.

---

## 6. Did the records repair overstate the closure?

**Its narrow claim is true, and I reproduce it exactly.** Both gaps closed on 2026-08-11;
both commits are ancestors of HEAD; all four sites name Spalart (2000) beside
`Ccr1 = 0.3` at HEAD; `:449` carries "nothing fitted to anything" in the same sentence;
the eleven-minute mechanism is exact. The struck *"2 gaps still open"* was **correctly
struck**, and the repair is right that the ledger had been reading worse-than-true for
four days in the direction least likely to be checked. That was worth fixing and it was
fixed well.

**Two things in it are overstated:**

1. **"were never gaps."** The repaired paragraph says the three refused surfaces *"were
   never gaps and remain refused."* `LADDER_V_PASS1_2026-08-11.md` §A5 names all five in a
   table headed *"five load-bearing gaps"*, and the chief's addendum held V5 at PASS WITH
   EXCEPTIONS on the express ground that *"five surfaces carrying the load-bearing
   untrained claim without naming whose constant it is, one of them public, is a real
   exception."* They were gaps. They were **refused**, which is a different thing, and the
   refusals were correct. Recasting a refusal as a non-gap converts an open exception into
   a settled one by wording.

2. **"V5 now looks closeable."** This measures against the two-gap list rather than
   against the rung's criterion. V5's verdict of record is **PASS WITH EXCEPTIONS with the
   chief declining to upgrade it**, and closing two of five exceptions does not convert
   that to PASS — least of all when the remaining three include two that can never be
   closed under the criterion as literally written, and when the count itself is four
   rather than three (U5).

**What the repair could not have known**, and what it therefore is not blamed for: U1–U4.
Those needed a mechanical derivation of the surface set over three arms, which is what the
repair correctly declined to do and correctly handed to a non-author instead.

---

## 7. Verdict

### FAIL — V5 does not close this round.

**What blocks it, in the order it must be cleared:**

- **B1 — the closing condition is unsettled.** Three criteria (C1/C2/C3) are live in the
  records; Pass 1 formally requested a chief ruling on the frame; the addendum answered
  two other questions and never answered that one. A rung cannot be graded green against
  a criterion nobody has adjudicated. **Owner: chief.**
- **B2 — the exceptions the verdict of record rests on are still open.** V5 is PASS WITH
  EXCEPTIONS with the chief expressly declining to upgrade, on five surfaces. Two closed.
  Three remain, and the true count is four (U5). Under C1 two of them are permanently
  unclosable, so B2 cannot be cleared by editing — only by B1.
- **B3 — the surface set was never complete.** U1–U5 above: one generator, three shipped
  JSON copies, one signed report, all carrying the untrained claim about our own model
  with no attribution, none ever counted by any V5 execution. Filed as **D121** and
  **D122**; not repaired here. *(Filed first as D119/D120 — a concurrent agent claimed
  both numbers in `docs/DOCKET.md` in the ninety seconds between my ID re-check and my
  append. Renumbered rather than renamed theirs; theirs are untouched and named in this
  grade's commit message. Recorded because "re-check the highest ID immediately before
  writing" is not sufficient under four concurrent agents — the collision window is the
  write itself. And the collision ran both ways: `769a83f0`, that agent's own pathspec
  commit filing its D119/D120, landed after my rows were already in the worktree and
  **carried D121 and D122 into history under its message**, so this grade's docket rows
  are anchored at another agent's commit rather than at `7ea96c0f`. Nothing was lost and
  nothing was overwritten; both of us named what we did not write. A pathspec commit takes
  the whole worktree state of a shared file, and under concurrency that means the commit
  that anchors a row is not reliably the commit whose message describes it.)*

**What would falsify this verdict — stated so it can be overturned rather than argued
with:**

1. **A chief ruling that fixes V5's frame at C3** — the two named sites, explicitly, with
   the frozen artifacts and the signed reports ruled out of frame and `build_benchmarks.py`
   and the three JSON surfaces ruled either in or out by name. Under C3 as ruled, §3 is
   the whole grade and **V5 passes**. B1 and B2 fall together; only U1–U4 would need a
   naming decision. This is the cheapest falsifier and I expect it to be the right one.
2. **Evidence that U1–U4 are not claim sites** — e.g. that the `our_entry` enumeration is
   a model *name* rather than an untrained *assertion*, ruled explicitly rather than
   assumed. That would clear B3 but leave B1 and B2.
3. **A record I did not find showing the frame was ruled on.** I searched the campaign
   corpus for a ruling on V5's frame and found none; a pointer to one overturns B1
   immediately.
4. **A defect in my sweep.** Its frames and controls are in §4 and can be re-executed
   verbatim. If the candidate predicate misses a claim shape — a surface saying "no
   training" or "no data was used" without the token `untrained` — the unmet set is
   larger, not smaller, and the verdict hardens rather than falls.

**What this grade does not touch, restated so it cannot be read as covered:** V5's legs 1
and 2 are inherited, not re-executed. I did not repair anything, so I remain a
non-author of every surface graded here and this grade needs no onward confirmation on
that count. `dist/` was not rebuilt or edited; the one file I wrote into it (the §4 decoy)
was removed and its absence confirmed.

---

*Anchors: gap closures `e071075d`, `514876b0` (2026-08-11); records repair `0b0041b1`,
`29beb7cf` (2026-08-15); V5's own records `LADDER_V_RUNGS_V1_V3_V4_V5_2026-08-08.md`
(`9a21d65c`) and `LADDER_V_PASS1_2026-08-11.md` (`5a21b4fd`, addendum `e59ae644`); the
two-gap narrowing at `LADDER_V_V13_CLOSEOUT.md` §7 item 9. Docket rows D121, D122.*
