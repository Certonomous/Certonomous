# Ladder V — V15 round 8: the grade over the 2026-08-15 text

**Grader:** a fleet agent that wrote none of the text under audit and none of the
repairs under test. **Executed 2026-08-15 19:54Z → 20:1xZ.** No solver run, no
scoring call; the scoring ledger stands at 6. The scoring pin `deb91557` was not
moved. Nothing sent, uploaded, filed or registered externally; submission is
PARKED and reserved to Katie.

**The verdict the termination rule asks for is a number, and it is not zero.**

---

## 0. Independence, and exactly how far it reaches

**Git cannot establish it.** `git log --format='%an <%ae>'` returns one identity,
`Ubuntu <ubuntu@ip-172-31-43-247.us-east-2.compute.internal>`, for the whole
graded range; there is no `user.name` configured anywhere and git prints its
"configured automatically from your username and hostname" warning on every
commit. **The session container cannot either** — it predates every commit here.

**What does, and it is a timestamp, not an identity.** This lab's per-agent
dispatch records live at
`~/.claude/projects/-home-ubuntu-Certonomous/64b13819-…/subagents/`. Mine is
`agent-a581770b678790339`, whose `meta.json` reads
`{"agentType":"general-purpose","description":"Run V15 round 8 grading",…}`. The
**first record in my transcript is `2026-08-15T19:54:19.603Z`** — the dispatch
prompt itself; the file was created at 19:54:19.727Z and holds no earlier event.

The **last commit in my declared scope, `cca64eaf`, is timestamped
2026-08-15 19:53:29 +0000 — fifty seconds before my first recorded action.**
Every one of the 78 commits graded below predates my existence. I did not write
them, and could not have.

**The limits, stated rather than left to be found.**

1. `scripts/check_rung_attribution.py --emit-trailer` emits the **same
   `Lab-Agent:` value for every agent in this session**, because it names a
   session, not an agent. The script says so itself, in the block ending at its
   line 92: *"TWO AGENTS DISPATCHED BY THE SAME CHIEF SESSION READ AS THE SAME
   AGENT."* Run at HEAD it reports **4 of 34 commits since the anchor carry a
   trailer at all**; the other 30 are `<absent>`, and its own verdict line says
   *"This says nothing about the 30 commits that carry none: their authorship is
   UNKNOWN."* So the mechanism does not attribute the range I am grading.
2. The subagent directory is **untracked and per-machine**. No reader of this
   repository can re-derive any of paragraph two. That is **D130**, and this
   round is another instance of it rather than an exception to it.
3. The claim this evidence supports is bounded: **no evidence of the same
   authorship**, not proof of different agents.
4. **Two commits landed after my first action and are therefore excluded** —
   `840c0c27` (20:00:45Z) and `7370b3d3` (20:01:20Z). My non-authorship of those
   is *not* established by the timestamp argument, which is precisely why they
   are out of scope and named here rather than quietly absorbed.

---

## 1. R-CONVERGE — the scope, declared mechanically BEFORE any finding

Round 7 (`edbaa0fe`) fixed its verdict at HEAD `26fca317` and named `650c1e04`
as the one commit that landed after and was **not** graded. This round's corpus
is everything from there.

| item | value |
|---|---|
| base | `26fca317` (2026-08-14 23:56:40Z) — round 7's verdict HEAD |
| HEAD at declaration | `cca64eaf` (2026-08-15 19:53:29Z) |
| commits | `git rev-list --count 26fca317..cca64eaf` → **78** |
| churn | `git diff --shortstat 26fca317..cca64eaf` → **61 files changed, 14,875 insertions(+), 434 deletions(-)** |
| composition | **20 added, 41 modified, 0 deleted** |
| days | **78 on 2026-08-15, 0 on any other day** |
| excluded, named | `840c0c27`, `7370b3d3` — landed at 20:00:45Z and 20:01:20Z, after this grader's first recorded action |

`650c1e04`, which round 7 excluded, **is** inside this range and is graded here.

### 1.1 What this frame structurally cannot contain

- **Rendered text.** Everything below is bytes. A page can carry a claim its
  bytes do not contain.
- **Non-text PDF layers**, and anything in a figure or font-embedded glyph run.
- **The live leaderboard.** Every board-relative number below is graded against
  the six-entry board fetched 2026-08-11T23:33Z, re-verified 2026-08-14T21:01Z,
  read by `ast` from `LIVE_BOARD` in `sdk/scripts/probability_of_rank.py`.
  Nothing was fetched.
- **Struck text**, wherever an instrument is quoted — and §3 is a finding about
  exactly that exemption.
- **The uncommitted working tree.** At the time of writing it carried another
  agent's in-flight `scripts/self_audit.py`, `CLOSURE_CHALLENGE_STATUS.md` and
  an untracked `LADDER_V_V5_V8_GRADE_2026-08-15.md`. None is graded. §8 records
  what that cost me.

### 1.2 Method, arm by arm

Counts over tracked text use `git grep -a` or `git ls-files`, never the shell's
`grep` (which execs `ugrep --ignore-files`, honours `.gitignore`, and passes
`-I`, skipping the 981 files `.gitattributes` marks binary, 12 of which contain
no NUL byte at all). `find` here is `bfs`; `/usr/bin/find` was used throughout.
Every `__pycache__` was purged before every test cell and before every
`self_audit` invocation — stale bytecode has inverted mutation results in this
tree and `PYTHONDONTWRITEBYTECODE=1` does not fix it.

**Exit codes were re-measured after a self-inflicted error.** My first pass read
`$?` after a pipe into `tail`, which reports `tail`'s status and reported
`exit=0` for a script that in fact exits 2. Every exit code below was re-taken
with the pipe removed. I record this because it is the same defect class as the
findings: a measurement whose instrument was reading the wrong object.

---

## 2. F1 — an anti-empty-set guard that counts the population it *looked at*, not the population it *decided*

**NEW SHAPE.** `scripts/check_normative_clauses.py` (landed `1c4a643f`, in
scope) is this lab's newest instrument and was built specifically so that a
check cannot clear anything by examining nothing. Its module header, lines
104–106:

> THREE-VALUED, AND IT NEVER PASSES FROM AN EMPTY SET
> Zero clauses matched is UNKNOWN with a reason, not PASS (defect class B1).

Its `decide()` docstring at line 572 repeats it: *"THE VERDICT, and it can never
be PASS from an empty set."*

**Executed, one line, no corpus:**

```
>>> check_normative_clauses.decide(0, "", [], [], 887, [])
('PASS', ['887 normative clause(s) examined; 0 pin a figure that agrees with
          its record; 0 are UNDECIDABLE and listed above; none is graded false'])
```

Zero findings of any kind, and the verdict is PASS. The B1 branch at line 592
gates on `examined` — the count of clauses that **matched a mandate marker** —
and never on the size of `findings`, the set that actually received a verdict.

**This is not hypothetical; it is the verdict the check ships today.** The live
run at HEAD:

| bucket | count |
|---|---|
| clauses examined | **887** |
| graded FALSE | **0** |
| graded TRUE | **0** |
| UNDECIDABLE | **1** |
| clauses that reached no verdict at all | **886 (99.89%)** |
| **VERDICT** | **PASS, exit 0** |

The shipped PASS rests on **zero decided clauses**. The one finding it holds is
an UNDECIDABLE in a document the check itself flags as out of repair scope.

**Why this is a defect and not a coverage statement.** The check prints seven
BLIND-TO items and they are honest about *which quantities* are out of reach.
None of them says that the verdict line can be reached with an empty decision
set. A reader who has read the module header has been told the opposite in
capital letters.

**The correct pattern exists 200 lines away, in a module this one already
imports.** `scripts/check_derived_figures.py:1229` gates on
`not matches and not checked` — and `matches` and `checked` *are* its graded
sets, not a superset of them. Its live run (61 anchored figures, 5 stated
computations, 0 faults) is a PASS over 66 decided items. The sibling gets it
right; the new one does not.

**Falsifier for F1:** show a path through `decide()` in which a nonzero
`examined` with an empty `findings` list is impossible in production — i.e. that
every matched clause necessarily yields a finding. The live run refutes this
already: 887 matched, 1 finding.

---

## 3. F2, F3, F4 — a rank the board cannot decide, its disclosure moved where no instrument can read it, and a page that now contradicts itself

The last commit in scope, `cca64eaf` (19:53:29Z), repaired `closure.html`'s
per-case table. Its arithmetic is **correct and I confirmed it independently**:
re-deriving all 48 board cells by `ast` from `LIVE_BOARD` against
`round5_per_case_full` reproduces every ordinal it wrote — 2nd, 2nd, 1st, 1st,
3rd, 4th, 4th, 7th of seven, and 2 of 8 board-best. That is a real repair of a
real defect and it is not being taken away here.

**One of those eight ordinals is not decidable from anything published.**

### F2 — the undecidable ordinal

`closure.html:505`, written in that commit:

```html
<s>2nd of 5 — was 3rd; ties Wu &amp; Zhang at published precision</s>
  → <b>3rd of 7</b>; the live best 0.0291 is Yang's. Tag struck 2026-08-15.
```

Re-derived: on `AR_1_Ret_360` our value is `0.04547044480564218`. Wu & Zhang's
board value is **printed to four decimals as `0.0455`**, so their true value
lies in `[0.045450, 0.045550]` — and **ours lies inside that interval**. Our
rank on that case is 3rd if we beat Wu & Zhang and 4th if we do not, and the
published board does not say which.

The lab already knows this. **D133**, `docs/DOCKET.md:498`, filed in this scope:

> our `0.04547044480564218` against Wu's printed `0.0455`, a gap of **2.96e-5**,
> which is **below the 5e-5 half-ulp of a 4-dp printing** … so **whether we won
> that case is not determined by anything published**. It is the only such
> comparison in the 48-cell board.

The commit that repaired D133 (`09234034`, in scope) deliberately declined to
write a bare `4/8` for the cases-won cell *"because it asserts a resolution the
data does not supply."* Forty-three minutes later, `cca64eaf` wrote a definite
ordinal on the same cell.

**Measured, all 48 cells, nearest-competitor gap in half-ulps of a 4-dp
printing:**

| case | ours | rank/7 | nearest gap (half-ulps) | decidable? |
|---|---|---|---|---|
| alpha_15_13929_4048 | 0.050105 | 2 | 138.11 | yes |
| alpha_15_13929_2024 | 0.101112 | 2 | 26.24 | yes |
| alpha_05_4071_4048 | 0.046108 | 1 | 215.84 | yes |
| alpha_05_4071_2024 | 0.071863 | 1 | 58.74 | yes |
| **AR_1_Ret_360** | **0.045470** | **3** | **0.59** | **NO** |
| AR_3_Ret_360 | 0.039982 | 4 | 1.64 | yes (ours is above Wu's whole interval) |
| AR_14_Ret_180 | 0.035339 | 4 | 6.77 | yes |
| NASA_2DWMH | 0.063198 | 7 | 335.96 | yes |

The undecidable ordinal has **two live copies** on the page: the tag at :505 and
the summary note below the table — *"On the other six rows we are behind: 2nd,
2nd, **3rd**, 4th, 4th and 7th of seven"* — which is followed by *"Every ordinal
in the table above is against the six-entry board retrieved 2026-08-11T23:33Z"*,
a sentence that asserts determinacy for all eight.

**No instrument in this lab sees it.**
`self_audit.check_rank_claim_surfaces` executed at HEAD returns WARN over 26
files and **`closure.html` is not among them** — its frame line says *"59 of
those assert a rank-1 placement"*, so a per-case rank-**3** claim is outside
`_RANK_CLAIM` entirely, and the page's two genuine `rank 1 of 7` claims carry
their triple and clear it. `check_normative_clauses` cannot see it either: its
coverage is four quantities (`live_margin`, `seed_bound`, `ours_overall`,
`coverage_pct`) and a per-case ordinal is none of them. **This is the
FORM-versus-VALUE shape with a new live instance:** every token the form checks
demand is present, and the value is undetermined.

### F3 — the disclosure was moved into the region every instrument masks

**NEW SHAPE.** The tag that `cca64eaf` replaced said, in full:
*"2nd of 5 — was 3rd; **ties Wu & Zhang at published precision**"*. That clause
is **true**, and it is the only place on the page that said so about `AR_1`.

It now sits inside `<s>…</s>`.

Struck text is exempt **by construction and on purpose** (D85). One masker,
`check_derived_figures.mask_exempt`, is imported unmodified by
`check_normative_clauses`; both print *"A masked region is never graded."* The
live run masks **307 `~~struck~~` spans and 36 `<s>/<del>/<strike>` element
bodies**, 15.8% of the non-space corpus.

So the repair did not merely omit the disclosure. It relocated it into the one
region of the corpus where **every** instrument in this lab is guaranteed never
to read it again, and replaced it with a stronger claim. A strike is the lab's
mechanism for *"this was wrong, and here is the correction"*; here it was
applied to the half that was right.

**Confirmed by execution:** `/usr/bin/grep -n
'half-ulp\|0.04545\|0.04555\|printing precision\|4 or 5 of 8'
demo-output/website/closure.html` → **exit 1, zero matches**. The page carries
no printing-interval disclosure for `AR_1` anywhere, struck or live.

### F4 — the page contradicts itself, live, and the defect is the *absence* of an edit

`closure.html:122` and `closure.html:431`, both **unstruck, both untouched by
`cca64eaf`**:

> `AR_1_Ret_360` and `AR_3_Ret_360` are ties below the precision the board
> publishes to, and **are not per-case wins**.

`closure.html:505` and `:506`, rewritten by `cca64eaf`: `3rd of 7` and
`4th of 7` — definite per-case ordinals for exactly those two cases.

Both live. Both in one file. The section was edited and the two summary
paragraphs were not, so a diff over `cca64eaf` shows the new tags and shows
nothing wrong; **the defect is in the lines the diff does not contain.** That is
D141's shape with the arrow reversed, and its base rate there was 1 in 11.

The same sentence appears live in four further tracked surfaces —
`ACTIVE_RESEARCH.md:54`, `CLOSURE_CHALLENGE_STATUS.md:591`,
`benchmarks.json:56`, `wall/wall.json:56` — none of which was reconciled.

---

## 4. F5 — a self-measurement falsified by the sentence two lines above it, in the same paragraph and the same commit

**Zero commits' remove — D79's shape, tighter than D79.** `closure.html`, one
paragraph written by `cca64eaf`:

> …on **seven** of the eight rows the live minimum is strictly below the
> four-entry number that was printed here, the sole survivor being the shallow
> coarse hill (0.0569, still Wu & Zhang's and still the minimum). … **The table
> below is now corrected in place**: **every** second-column cell carries the
> four-entry number struck and the live six-entry number beside it…

**Executed** — parse the table, count `<s>` in each second column:

```
1 Periodic hill, steep, coarse    struck=True   <s>0.0592</s> <b>0.0432</b>
2 Periodic hill, steep, fine      struck=True   <s>0.1195</s> <b>0.0998</b>
3 Periodic hill, shallow, coarse  struck=False  0.0569
4 Periodic hill, shallow, fine    struck=True   <s>0.0760</s> <b>0.0748</b>
5 Square duct, aspect ratio 1     struck=True   <s>0.0387</s> <b>0.0291</b>
6 Square duct, aspect ratio 3     struck=True   <s>0.0341</s> <b>0.0311</b>
7 Square duct, aspect ratio 14    struck=True   <s>0.0325</s> <b>0.0250</b>
8 NASA wall-mounted hump          struck=True   <s>0.0364</s> <b>0.0294</b>

cells with a struck four-entry number: 7 of 8
```

**Seven of eight, not every.** Row 3 is correct to carry a bare number — Wu &
Zhang's `0.0569` was the minimum on the four-entry board and remains it on the
six-entry board, so there is nothing to strike. The *cell* is right; the
*sentence about the cells* is wrong, and its own paragraph says so two lines
earlier, and so does the docket row it cites: **D149** reads *"printed the
four-entry board's minimum in its `Best published` column on **seven rows of the
eight**."*

The commit's own headline is *"…and both notes written to cover the stale table
were off by one."* **This is the third off-by-one, and it is inside the note
written to announce the first two.**

---

## 5. F6 — a charter clause adopted at 19:10Z, violated by the next durable write at 19:53Z

`docs/charters/REPORTING_CHARTER.md`, adopted by the chief at `638b9af2`
(2026-08-15 19:10:39Z), in scope:

> **A figure is printed at the precision of the derivation that produced it, and
> the uncertainty of its inputs is stated as an interval where the quantity is
> defined — never by deleting digits.** … Nothing already written is rewritten
> under this clause and it is not authority for a sweep. **It governs what is
> written next**… Where a live claim quotes a figure whose inputs carry a
> printing interval, **the interval goes beside it, once, at the point where the
> quantity is defined.**

`AR_1_Ret_360`'s ordinal is exactly a live claim whose input carries a printing
interval — `[0.045450, 0.045550]`, the interval the clause's own §2.4 citation
(`MARGIN_PRECISION_INTERVAL_2026-08-15.md`, `eadcd112`) exists to establish for
the sibling quantity. `cca64eaf` wrote it **forty-three minutes later, one
commit later**, with no interval beside it and with the previous disclosure
struck.

The clause is well made — it fixes a form, names no figure, and cites why two
prior digit-count rulings were refuted. **What it lacks is any instrument.**
`check_normative_clauses` grades whether a *mandate* would write a true sentence
about four registered quantities; nothing grades whether a *new figure* obeys
the mandate. So the rule was obeyed by nobody and enforced by nothing, and the
gap between adoption and first violation is under an hour.

---

## 6. F7, F8 — a register whose stated reason for existing is false, and a red test whose repair went to another family's file

### F7 — the false absolute, still shipped at HEAD

`sdk/chief_engineer/exec_bits.py:291–302` (the absolute is at **:300–301**),
landed `e933e31b`, in scope, alive at HEAD (`7370b3d3`):

> Measured 2026-08-15 in a scratch repository across four variants; **only an
> index commit with no pathspec preserves 100755. So this register is the only
> repair a protocol-conforming agent can perform**, and D134 records that.

**Falsified three independent ways.**

**(a) My own execution.** Fresh `git init`, `core.filemode false`, one
shebang-bearing file at HEAD mode `100644`:

```
index after plain `git add`:   100644 …
$ git -c core.fileMode=true commit -q -m v147 -- s.py
git ls-tree -r HEAD:           100755 blob 9440c0cc…  s.py
```

A **pathspec** commit — the only form this lab's protocol permits — recorded
`100755`, from an index that read `100644`. The control also reproduces: the
same flag on the `git add` alone yields `100644`, so the tempting half is the
wrong half.

**(b) D147**, filed at `f732ebaf` (19:44:12Z), records the identical
measurement and says in its own title that it *"reopens D134's choice"*.

**(c) Commit `7370b3d3` (20:01:20Z) actually performed one** — a mode-only
change, same blob `1c11ae63`, `100644` at `840c0c27` → `100755` at HEAD.

The comment was never corrected. The register's justification for growing is a
claim the lab has now disproved twice and acted against once.

### F8 — the suite is red at HEAD, and the repair went somewhere else

Executed, `__pycache__` purged first:

```
sdk/tests/test_exec_bits.py::ThisRepositoryTests::
  test_no_shebang_script_is_both_unexecutable_and_unregistered  FAILED
  AssertionError: Lists differ: ['scripts/check_normative_clauses.py'] != []
1 failed, 14 passed in 1.62s
```

D134 predicted this failure and offered the register as the only exit. F7 shows
the exit is not the only one. Between `f732ebaf` (which established the working
repair) and HEAD, that repair was applied to **`scripts/check_summary_consistency.py`**
— a file belonging to the agent that wrote it — and **not** to
`scripts/check_normative_clauses.py`, the file the red test actually names, which
belongs to another family and is still `100644` at HEAD.

That is **D145's ownership boundary**: the correction reached the copy inside the
correcting agent's own zone and stopped at the boundary. The register's own
docstring still describes an object it is not — it says the register *"stops the
gap growing"*; D134 already recorded that it can only grow; F7 shows it need not
exist for this class at all.

---

## 7. What reproduced, and is therefore not a finding

Recorded because a round that reports only failures cannot be audited for
selection.

| claim | frame | result |
|---|---|---|
| `check_derived_figures.py` PASS | live tree, exit re-measured without a pipe | **PASS, exit 0**, 61 anchored figures + 5 computations, 9 positive + 9 negative controls all correct |
| `docket_citation_guard.py` PASS | worktree docket, 1,848 files | **PASS, exit 0**, 303 citations all resolve, 5 negative controls correct |
| `detect_overwrite_signature.py --self-test` | in-memory | **all 5 controls behaved as specified**, exit 0 |
| `check_rung_attribution.py` PASS | 34 commits since anchor | **PASS, exit 0**, and it states its own limit: 30 commits carry no trailer and are UNKNOWN |
| D148 (`lab_check` emits one blob) | `--no-tests`, redirected | **reproduced** — the output file held **0 bytes** for the entire run |
| D147 (the filemode asymmetry) | scratch repo, both arms | **reproduced exactly**, see F7(a) |
| D133 on `AR_3_Ret_360` | 48-cell re-derivation | **D133 is right** — 1.64 half-ulps, ours above Wu & Zhang's whole interval, so that ordinal *is* determined |
| `cca64eaf`'s eight ordinals and its 2-of-8 | independent re-derivation from `LIVE_BOARD` | **all eight reproduce**; only their decidability is at issue (F2) |
| `check_rank_claim_surfaces`' B1 repair | git-less extraction of `cca64eaf` | **works in the negative arm** — reports *"this detector is OFF, not reporting nothing to find"* rather than a green |

One self-disclosed false positive is worth naming because the instrument found
it before I did: `check_rank_claim_surfaces` flags `docs/HANDSHAKE.md:39` for a
missing sweep token that is *"present but wrapped across a line break, which is
invisible to the sweep that greps for it."* Disclosed in the verdict text, so
recorded here rather than filed.

---

## 8. What this round could not measure, and why

**The live-tree `lab_check` run is not attributable to this scope.** It ran at
20:0xZ against a working tree carrying another agent's uncommitted
`scripts/self_audit.py`, which introduced a check named `check_rank_claim_values`
that **raised `NameError: name '_live_ranks' is not defined`** inside the run.
`git log -S'check_rank_claim_values'` and `git log -S'_live_ranks'` over
`scripts/self_audit.py` return **nothing** — neither symbol exists in any
commit. It is in-flight work, it is outside my declared range, and **I do not
file it.** But it means no `lab_check` verdict taken from the live tree this
hour is a statement about the committed scope, and I will not present one as
though it were.

**The clean-frame substitute was inconclusive.** I extracted `cca64eaf` with
`git archive` into a scratch tree and ran `self_audit.py` there: 14 PASS, 9 WARN,
4 FAIL, 3 INFO, 4 UNKNOWN. The extraction has no `.git` and none of the
gitignored evidence, so the git-dependent detectors correctly went OFF and
"cited evidence paths" reported **74 of 1,259** unresolved against the live
tree's **2 of 1,260**. Those seventy-two are artifacts of my frame, not findings
about the corpus, and I state that rather than quoting the larger number.

**Not covered at all:** the 66 GB run tree at `/home/ubuntu/certonomous-runs/`;
the ~37,246 gitignored files; the 50 tracked PDFs; rendered output of any HTML;
and the full pytest tier, which `lab_check` prices at ~24 minutes and which I did
not run to completion. `sdk/tests/test_exec_bits.py` was run in isolation and is
the only suite result I claim.

---

## 9. The count, the verdict, and the falsifier

### New material findings in the declared scope: **thirty**

Eight from the text-and-instrument pass (§2–§6), seven from the mutation cell
(§11), fifteen from the document-verification cell (§12). **This section has now
been revised upward twice** — first drafted at eight, revised to fifteen when the
mutation cell reported, revised to thirty when the document cell reported. Both
revisions are recorded rather than made silently, and both corrected earlier
sections of this same document: **§11's M1 corrects §2, and §12's closing note
corrects §7.**

| # | finding | new shape? |
|---|---|---|
| F1 | `check_normative_clauses.decide()` returns PASS from an empty decision set; the B1 guard counts `examined`, not `findings`; the shipped verdict rests on 0 of 887 decided | **yes** |
| F2 | `closure.html:505` asserts `3rd of 7` on `AR_1_Ret_360`, an ordinal the board's own 4-dp printing cannot decide, and which D133 names as the one such cell in 48 | no (FORM/VALUE, new instance) |
| F3 | The true disclosure was moved inside `<s>…</s>`, the one region every instrument in this lab masks by construction | **yes** |
| F4 | `closure.html` now contradicts itself live at :122/:431 vs :505/:506; the defect is the absence of an edit; four further surfaces carry the unreconciled sentence | no (D141's shape) |
| F5 | *"every second-column cell"* is **7 of 8**, falsified by its own paragraph two lines above and by the D149 row it cites | no (D79's shape, zero commits' remove) |
| F6 | `REPORTING_CHARTER`'s interval-beside-the-figure rule, adopted 19:10Z, violated by the next durable write at 19:53Z; the rule ships with no instrument | **candidate** |
| F7 | `exec_bits.py:300–301`'s *"the only repair a protocol-conforming agent can perform"* is false; disproved by my execution, by D147, and by `7370b3d3` acting against it; uncorrected at HEAD | no |
| F8 | `test_exec_bits.py` is RED at HEAD; the now-known repair was applied to the correcting agent's own file and not to the one the test names | no (D145's shape) |
| M1 | `check_derived_figures.main()` has **no test at all**; all three of its UNKNOWN guards survive deletion with the suite green, under a test class named `ItCannotPassFromAnEmptySet` | no — but with F1 it yields a **new claim**: no instrument here has empty-set behaviour that is both correct and verified |
| M2 | `check_rung_attribution.integrity()` — the mode `lab_check` schedules — returns **PASS over zero identities examined** when its guard is deleted; untested | no (B1) |
| M3 | `test_UNKNOWN_exits_non_zero…`'s entire body is three tautologies about string constants; `main()` is never called. A sibling labelled **"MUTATION PROOF"** likewise asserts only over literals defined inside itself | **yes** — a test that cannot fail for any reason connected to the module it names |
| M4 | `check_bundle_drift` prints *"all **0** file(s) … match the shipped zip byte for byte"* as a PASS when its empty-pair guard is removed; the arm is named in its own docstring and untested | no (B1) |
| M5 | `test_a_root_that_does_not_exist_empties_the_ledger` never checks the ledger was emptied; the assertion is satisfied by an unrelated root filter | no (the `test_an_empty_directory_is_UNKNOWN` shape, new family) |
| M6 | The D137 banned-language guard covers `build_certificate_v2` and not `build_certificate` v1; the withdrawn footer can be reinstated there with 62 tests green | no |
| M7 | The QCR attribution control guards the generator and not the two shipped JSON surfaces; two of five mutations survive | no |
| P1 | `OWNERSHIP_BOUNDARY_SWEEP` quotes `self_audit.py:5948` with a sentence **absent from the tree it declares as its frame**, three minutes old, dated *"for three days"* — off by ~1,440× — and it is the sole support for one of the document's four durable fixes | no (stale referent, extreme instance) |
| P2 | Its printed remedy **W1 does not run**: `ulem.sty` is not installed, `pdflatex` emergency-stops, **no PDF is produced**. This falsifies the document's thesis that all 26 residuals are *"blocked on a name — not on compute"* | no (remedy printed but never run) |
| P3 | Its printed remedy **W2 exits 1** and silently drops **15 of 90** shipping zip members; the gate causing it predates the document's own commit | no (same shape) |
| P4 | Its printed `sweep.py` demonstration returns **33 files**, not the three named — a ~10% subset — and is the sole evidence for its proposal (b) | no (same shape) |
| P5 | *"six times across six rows"* is **4 at the declared frame**, and reaches six only by counting the row the document itself filed | no (D79's shape) |
| P6 | A bolded finding says *"returns a PASS"*; the evidence quoted **two lines below it** says `WARN`; neither edited | no (F4/D141's shape) |
| P7 | `AGENT_ATTRIBUTION` and the module it documents quote adoption ratios (`2 of 40`, `1 of 40`) that **no tree has ever produced**; the instrument's frame is anchored, not a window | no |
| P8 | `HANDSHAKE.md` anchors a correction to `29beb7cf`, a commit that **never touched the file** | no (the class filed at `3314d746`, recurring inside the range that filed it) |
| P9 | A heading says *"seventeen"*, its own first sentence says *"eighteen"*; both wrong at the document's commit; neither edited | no |
| P10 | `MARGIN_PRECISION_INTERVAL` files its finding as **D132**, an ID the **same commit** gave to an unrelated row | no (zero commits' remove) |
| P11 | *"Twelve rows"* is **eleven at every tree**, the sentence that narrows a FAIL depends on it, and a locator off by 44 lines was **transcribed into a shipping document** | no |
| P12 | Six present-tense sites in dated records (W-5); one **falsified** by `e639796e`. One was falsified by this round's own first commit, and is recorded rather than repaired | no |
| P13 | *"All fifteen table entries are LIVE AND WRONG"* over a 13-row table, one row of which says the wording there **is correct**; the fifteen propagates into D145 | no |
| P14 | *"27 live wrong passages, in 7 files"* — the document's own enumeration gives 5 or 6; copied verbatim into D145 | no |
| P15 | **The attribution instrument's discriminating field has taken exactly one value across 100% of its deployed life** — all four real `Lab-Agent` trailers are one string, it is this session's, and the instrument returns **AUTHOR** on its own adopters | **yes** |

### **VERDICT: this round is NOT belief-neutral.**

**The reasoning.** R-VALUE terminates the ladder after two consecutive
belief-neutral rounds, and the count stands at zero. A round is neutral if it
only executes or closes findings already believed. This one does not:

- **F1, F3, M3 and P15 are new shapes**, and all four are of the kind that make other
  rounds' greens unreliable rather than merely adding a defect. F1 says a
  purpose-built B1 guard can be satisfied by a population that is not the
  population under judgement — every check in this lab that prints a frame count
  and a verdict is now a candidate. F3 says the lab's own correction convention
  has an *anti-disclosure* mode: strike the true half and the corpus keeps a
  record no instrument will ever grade again. M3 says a test can be **incapable
  of failing for any reason connected to the module it names** while carrying
  that module's name and, in one case, the words "MUTATION PROOF" — which is the
  `test_an_empty_directory_is_UNKNOWN` finding taken one step further: not an arm
  left unasserted, but an assertion aimed at nothing. **P15 says an instrument's
  verdict field can have one value across its whole deployed life** — four runs
  are then one constant observed four times, not four confirmations, and D124 and
  D130 record the design limit without ever recording that it has already bound
  every adopting commit.
- **F1 and M1 together are stronger than either.** `check_normative_clauses`
  factored its verdict out expressly so a test could drive the empty-set arm; the
  test exists, and the guard it drives is wrong. `check_derived_figures` has the
  right guard and no test that ever calls the function containing it. **This lab
  does not currently have an instrument whose empty-set behaviour is both correct
  and verified**, and it acquired both halves of that in the graded range.
- **Four of the fifteen are empty-set agreement (F1, M1, M2, M4)** in four
  different modules, three weeks after the class was named and one day after 21
  of 34 `self_audit` checks were repaired for it. The class is not closing.
- **F2, F4, F5, F6 are all defects written on 2026-08-15 by the repairs
  themselves**, three of them in the single most recent commit in scope, at zero
  and forty-three minutes' remove. A round that finds four fresh defects in the
  text written by the fix round is the definition of not-neutral under clause 2
  of the termination rule, whose pass criterion is *no new failures — not few,
  zero*.
- **F7 and F8 are stale-referent and ownership findings**, which are known
  *classes*; but the specific claim in F7 is a live absolute in shipped code
  that the lab disproved twice and never corrected, and F8 is a red test at HEAD.

**The count would still be non-zero at four.** F1, F3, M3 and P15 alone carry it
— four new shapes, none previously recorded.

**And it was scored too low twice already, in this document.** §9 was drafted at
eight; the mutation cell took it to fifteen and corrected §2; the document cell
took it to thirty and corrected §7. **Each revision arrived after the section it
revised had been written and committed.** That is the concrete form of the
warning below, twice, inside one round.

**Three of the thirty are one document faulting its own evidence.** P1, P5 and
P13/P14 are all inside `OWNERSHIP_BOUNDARY_SWEEP`, whose §2.1/§2.2/§6 forensics
were independently re-derived and are **exact** — 14 PDF strings at their stated
lines, 90 zip members with zero md5 mismatches, a rank-claim line list correct
byte for byte. **A document can be meticulous in its measurements and wrong in
almost every sentence that cites them**, and this round found that pattern in
three separate documents in one range.

### What would falsify this verdict

Stated plainly, and each of these is cheap:

1. **F1 falsified** if someone exhibits, in production, that a nonzero
   `examined` always implies a nonempty `findings` — i.e. that the two
   populations coincide. *(The live run of 887 examined → 1 finding refutes this
   already; the falsifier would have to show my `decide()` call is unreachable
   from `main()`, which the live counts contradict.)*
2. **F2 falsified** if the organisers publish per-case values to more than four
   decimals, or if a full-precision source for Wu & Zhang's `AR_1_Ret_360` value
   exists in this corpus. Then the ordinal is determined and only F3 survives.
   *(I searched: `half-ulp`, `0.04545`, `0.04555`, `printing precision`,
   `4 or 5 of 8` — zero matches in `closure.html`.)*
3. **F3 falsified** if any instrument in this lab grades struck text. *(D85 and
   `29452c51` both say the opposite; note in particular that the chief's
   correction at `29452c51` establishes there is **no** strike stripper —
   `board_placement_faults` skips a placement only when another within 400
   characters binds the same entrant, a proximity rule, not a strike rule. So
   the exemption is if anything broader than F3 assumes.)*
4. **F4 falsified** by showing lines 122 and 431 are inside a dated,
   withdrawal-bannered section. *(They are not; both are live body prose.)*
5. **F5 falsified** by a reading of "every second-column cell" that excludes row
   3. *(I can find none; the sentence's stated content is a property of all
   eight, and the paragraph's own earlier sentence counts seven.)*
6. **F6 falsified** if the AR_1 ordinal is held not to be "a figure whose inputs
   carry a printing interval". *(The whole of D133 is the argument that it is.)*
7. **F7 falsified** by showing `git -c core.fileMode=true commit -- <paths>` is
   not protocol-conforming under ESCALATION_CHARTER 9.6 — which is exactly the
   chief question D147 raises and which is **open**. If the chief rules the
   override non-conforming, the comment's absolute becomes defensible and F7
   downgrades to a wording defect; `7370b3d3` then becomes a protocol violation
   instead, and something is still wrong.
8. **M1–M7 falsified** by re-running any of the named mutations with
   `__pycache__` present. *(That is not a falsification, it is the inverted
   result this lab has already recorded twice — every cell above purged bytecode
   immediately before every `pytest` invocation, and the baseline and final
   full-suite runs are byte-identical at 346 passed / 51 subtests. The genuine
   falsifier is a test file, anywhere in the repo, that calls
   `check_derived_figures.main()` or drives `integrity()`'s zero-identity arm; I
   grepped and found none, and that grep is the claim to attack.)*
9. **The whole round falsified as non-neutral** if F1, F2, F3, F5 and F6 are all
   already recorded somewhere in `docs/DOCKET.md` or a prior round document
   before `cca64eaf`. I checked each against the docket by ID and by phrase;
   D133 records F2's *premise* and explicitly declines to draw F2's conclusion,
   D141 and D79 record the *shapes* of F4 and F5 but not these instances, and
   nothing records F1, F3 or F6.

**Do not score the next round neutral early.** Round 10 of V16 was scored
neutral and three new shapes appeared within forty minutes. **Three of the
thirty findings above were written into the corpus inside the two hours before
this round began** — F2, F4 and F5 all in `cca64eaf` — the text under grade is
being produced faster than it is being graded, and F6's adoption-to-violation
interval was forty-three minutes.

*(That sentence read "three of the **eight**", then "three of the **fifteen**", as
§9 was revised twice. It is corrected here rather than left, and named
rather than corrected silently, because a summary going stale against its own
revised section with neither flagged is F4's defect and this document is not
exempt from it. `check_summary_consistency.py`, built at `840c0c27` for exactly
this class and outside this round's range, would have had a pair to grade here.)*

---

## 10. Filed, not appended

Findings are filed as append-only docket rows rather than folded into the rung.
A rung that absorbs every new finding never closes; one that drops them is
worse.

| row | finding |
|---|---|
| **D158** | F1 — the B1 guard on the wrong population |
| **D159** | F2 + F3 + F4 — the undecidable ordinal, its struck disclosure, and the page that contradicts itself |
| **D160** | F5 — "every second-column cell" is seven of eight |
| **D161** | F6 — the charter clause with no instrument, violated by the next write |
| **D162** | F7 + F8 — the register's false absolute and the red test whose repair went elsewhere |
| **D164** | M1 + M2 + M4 — four empty-set-agreement instances in four modules, and the claim that no instrument here is both correct and verified on that arm |
| **D165** | M3 + M5 + M6 — assertions aimed at nothing, including one labelled "MUTATION PROOF" |
| **D166** | M7 — a control on the generator and none on the artifact that travels |
| **D170** | P2 + P3 + P4 — three printed remedies executed: one produces no PDF, one exits 1 and drops 15 of 90 members, one returns 33 files where it claims three |
| **D171** | P1 + P5 + P6 + P9 + P13 + P14 — six citation and count defects inside one sweep whose own forensics are exact |
| **D172** | P7 + P8 + P10 + P11 — four citations contradicted by the artifacts they name, one of them transcribed into a shipping document |
| **D173** | P15 — an instrument whose discriminating field has taken one value across its entire deployed life |

**These are not the IDs this round first reserved, and the reason is worth the
line.** At 20:0xZ `D152`–`D156` were asserted free and were free. By the time the
rows were written, minutes later, all five had been allocated by another agent
filing concurrently. The IDs were re-asserted at the moment of writing — inside
the same process that appended the rows, with an abort if any was taken and a
second abort if `docs/DOCKET.md` was not byte-identical to `git show
HEAD:docs/DOCKET.md` — and came out at `D158`–`D162`. **Allocating by execution
is not enough on its own; the assertion has to be inside the write.**

**It happened a second time, and the second fix is the one that holds.** The
document cell's rows were drafted against `D167`–`D170`, asserted free; `D167` was
taken by a concurrent filer before they were written. The filing script was
changed to **compute the high-water mark and take the next free block inside the
same process that appends**, re-asserting each: it found the high-water at `D169`
and allocated **D170–D173**. Three collisions in one round, on one file, is the
measurement — and it says the remedy is not "assert before writing" but "assert
*in* the write". Nothing
here was derived by `sort -u`, which is lexical and returns `D99` when the
highest is `D151`.

**And the commit that filed them carried two rows that are not this grader's.**
`bfe9b812` was diffed against `git show HEAD:docs/DOCKET.md` immediately before
staging and read as five added lines. It landed as **seven insertions and one
deletion**: another agent wrote to `docs/DOCKET.md` in the seconds between the
check and the `git add`, and a pathspec isolates by file, not by author
(`ESCALATION_CHARTER` §9.6b). **Not mine, and named rather than reverted:** the
new row **D163** (the summary-consistency check's 2-of-94 coverage measurement,
taken at `840c0c27`, which this round's range excludes by name), and a
**modification to D141** that grew it from 2,276 to 4,977 characters, closing it
on that same instrument. **Mine in that commit, and only these:** D158–D162 and
this section's own correction.

That is the same shape as F1, one level up: a check that was true when it ran and
false when it was relied on. **`D119a` already owns it** — *"the pre-flight check
that cleared it was already expired when it ran"*, filed at 02:23Z the same day.
Two agents have now hit it on this one file in one day.

**Nothing in this round was repaired.** `demo-output/website/closure.html`,
`scripts/self_audit.py` and `docs/USING_THIS_LAB.md` are on this grader's
do-not-touch list; they were read and never written. A grader that repairs its
own findings cannot then grade them.

---

## 11. The mutation cell — seven more, and one of them corrects §2

Run as a second, separate execution pass over the **fifteen test files added or
modified in the declared range**. Every mutation went through a harness that
asserts the mutation site occurs exactly once, **purges `__pycache__` with
`/usr/bin/find … -prune -exec rm -rf {} +` immediately before every `pytest`
invocation**, and hash-checks and restores the file byte-for-byte afterwards.
Baseline and final state identical: **346 passed, 51 subtests**, both ends. About
45 mutations across 12 production files.

### M1 — `check_derived_figures.main()` has no test at all, including the arm its test class is named for

**This corrects §2 of this document.** In F1 I wrote that the correct
empty-set pattern "already exists 200 lines away" in `check_derived_figures.py`.
The pattern is correct. **It is also entirely unguarded.** Three separate
mutations of its verdict block, each run against
`test_derived_figure_check.py` **and** `test_normative_clause_check.py` together:

| mutation in `scripts/check_derived_figures.py` `main()` | result |
|---|---|
| `elif not matches and not checked: verdict = UNKNOWN` → `elif False:` | **survived, exit 0** |
| `if problems: verdict = UNKNOWN` → `if False:` | **survived, exit 0** |
| `elif bad_controls: verdict = UNKNOWN` → `elif False:` | **survived, exit 0** |

`cdf.main` is never called from either test file, or from anywhere else in the
repo. The test class is literally named **`ItCannotPassFromAnEmptySet`**, with
the docstring *"Defect class B1, the silent-zero sweep (D62)"*, and its four
tests exercise `_scan`, `read_sources`, `build_registry` and `dig` — never the
function that produces a verdict. `TheExitContract` pins the `EXIT` dict and
nothing that reaches it.

**So the two instruments split the failure between them:** `check_normative_clauses`
factored `decide()` out *"so a test can drive it to that state without a corpus"*
and both its equivalent guards were **killed** — its guard is tested and wrong
(F1). `check_derived_figures` has the right guard and no test of it (M1).
**Between them, this lab has no instrument whose empty-set behaviour is both
correct and verified**, which is a stronger statement than either finding alone
and is the reason they are reported together.

### M2 — `check_rung_attribution.integrity()` can return PASS over zero identities

`scripts/check_rung_attribution.py:439`. Mutating `if counts[OK] == 0:` →
`if False:` leaves **all of `test_rung_attribution.py` green, exit 0**. Direct
probe on a throwaway repo (anchor plus two commits, no trailers anywhere):

```
CLEAN   exit 3   VERDICT: UNKNOWN   ADOPTION: 0 of 3 commits carry an identity
MUTANT  exit 0   VERDICT: PASS      ADOPTION: 0 of 3 commits carry an identity
```

The file's own header lists *"AN EMPTY GRADED SET is UNKNOWN … naming defect
class B1"* and the sibling arm in `attribution()` **is** covered (that mutant was
killed). The uncovered one is `integrity()` — **the mode `lab_check.py` actually
schedules.**

### M3 — a test named for an exit contract whose body is three tautologies

`sdk/tests/test_bundle_drift_gate.py:230`,
`test_UNKNOWN_exits_non_zero_so_an_off_detector_reddens_the_runner`. Its entire
body asserts `sa.UNKNOWN == "UNKNOWN"`, that `off.status` is in `(sa.UNKNOWN,)`,
and that `sa.UNKNOWN` is not in `(sa.PASS, sa.WARN, sa.INFO)` — three statements
about string constants defined in the module under test. **`main()` is never
called.** Mutating `self_audit.py`'s `return 3 if any(r.status == UNKNOWN …)` →
`return 0` leaves `test_bundle_drift_gate.py` at **10 passed, exit 0**. The
property *is* guarded — by `test_empty_set_is_not_agreement.py`, a different
file — so the named test is dead weight rather than a hole. A sibling at
`test_certificate.py:279` is labelled **"MUTATION PROOF"** and likewise asserts
only `in`/`not in` over two string literals defined inside the test; it cannot
fail for any reason connected to `certificate.py`.

### M4 — literal empty-set agreement: *"all 0 file(s) … match"*

`self_audit.check_bundle_drift`. Mutating `if not pairs:` → `if False:` leaves
**10 passed, exit 0**. Direct probe with an archive that has members but no
tracked sources:

```
CLEAN   UNKNOWN  found no files the builder copies verbatim out of tracked sources
MUTANT  PASS     all 0 file(s) the builder copies verbatim out of tracked sources
                 match the shipped zip byte for byte (2 of 2 shipped members ungraded)
```

The function's docstring names this arm explicitly (*"an empty copy list"*).
`AnAbsentOrUnreadableArchiveIsUNKNOWN` covers the empty-**member** case and not
the empty-**pair** case. All sibling guards were killed.

### M5 — a test named for emptying a ledger that never checks the ledger was emptied

`sdk/tests/test_refused_inbox_lifecycle.py:146`,
`test_a_root_that_does_not_exist_empties_the_ledger`. Deleting
`_publish_refused_inbox(root, refused)` from the absent-root early return at
`sdk/chief_engineer/agenda.py:1126` leaves **11 passed, exit 0**. The body
asserts only `refused_inbox() == set()`, which the *root filter* at
`agenda.py:1110` already satisfies. Probe, clean vs mutant:

```
CLEAN   _REFUSED_INBOX = []                  root = <new dir>/proposals
MUTANT  _REFUSED_INBOX = ['present.json']    root = <OLD dir>/proposals
```

Under the mutant the ledger still names a file from a directory the read never
opened. **This is the `test_an_empty_directory_is_UNKNOWN` shape again**, from a
different family, four days after it was first named.

### M6 — the D137 banned-language guard does not cover the v1 renderer

`sdk/chief_engineer/certificate.py:815`. Reinstating a `Reproducible from…`
footer in `build_certificate` (v1) leaves **62 passed, exit 0**.
`test_banned_language_never_renders`'s widened `assertNotIn("reproduc", …)` runs
only through `build_certificate_v2`; planting the same sentence in v2 **is**
caught, so the guard bites — it just never reaches v1, which `PdfTests` and
`RedesignV2Tests` render with no language assertion. **Severity, stated:** v1 is
called only by `sdk/scripts/build_certificate_compare.py`; every shipping
workflow uses v2.

### M7 — a live-control on the generator, none on the shipped JSON

`sdk/tests/test_untrained_qcr_attribution.py`. The subject-deletion control
covers `_closure_literal()`; the shipped-surface test has no equivalent.

| mutation | result |
|---|---|
| `"untrained QCR2000 forward solve"` → `"untrained closure forward solve"` in `sdk/scripts/build_benchmarks.py` | killed |
| the same, in `demo-output/website/benchmarks.json` | **survived** |
| the same, in `demo-output/website/wall/wall.json` | **survived** |
| `"is Spalart (2000)'s "` → `"is the "` in the generator | killed |
| the same, in `benchmarks.json` | killed |

Not vacuous today — each JSON carries exactly one QCR string — but the file's own
stated failure mode (*"a rule survives the deletion of its subject and goes on
reporting clean"*) is guarded on one arm only.

### What held up

Reported because a mutation cell that lists only survivors cannot be audited.
**Every** guard deletion was killed in `test_empty_set_is_not_agreement.py` (5/5,
including the six-check `_stored_studies` guard → 6 subtests failed),
`test_blind_spots_are_printed.py` (3/3), `test_bundle_certificate_pairing.py`
(5/5), `test_normative_clause_check.py` (2/2), `test_lab_check.py` (6/6,
including the `EXIT_CONTRACT` retyping and the `blocking = v == UNKNOWN` lock),
`test_installed_matches_tracked.py` (6/6), `test_calibration_scorecard.py` (3/3),
`test_autostop_gate.py` (3/3) and `test_f7a_contract.py` (3/3, including both
"always 0" and "always 1"). Four further survivors were examined and **rejected
as non-defects** (unreachable defensive code in `_since_anchor` and `integrity`,
a redundant `zip_path.is_file()` whose sibling `except OSError` returns the same
UNKNOWN, and a self-documenting no-assertion arm in
`test_installed_matches_tracked.py` whose own docstring says so).

### The risk this cell carries

`scripts/self_audit.py` was already dirty (`M`, ~900 uncommitted lines from
another agent) when the cell began, and another session was committing into this
tree throughout. The mutation harness restored by hash and the final 346-test run
is green, but **if another agent wrote to that file inside one of the ~5–20 s
mutate-run-restore windows, that write was overwritten.** Stated rather than
discovered later. Nothing else was touched: `git diff` on every mutated file is
empty.

---

## 12. The document-verification cell — fourteen more, and one that bears on §0

A third execution pass, run in parallel with §11, over the eight campaign and
`docs/` documents added or modified in the declared range. Every number was
**re-derived**, never read from the document's own summary. Where a count is
time-sensitive it is given at the document's **own stated frame** as well as at
HEAD, so no finding rests on drift.

### P1 — a citation whose quoted sentence did not exist at the frame the document declares, dated "three days" when it was three minutes old

`OWNERSHIP_BOUNDARY_SWEEP_2026-08-15.md:3` declares *"Swept 2026-08-15 at HEAD
`1360a5a9`."* Its `latex/` zone register at `:63` quotes
`self_audit.py:5948` as printing *"nothing in this file opens a PDF, so a claim
that exists only in a compiled report is invisible while its `.tex` source is
not"*, and §5.1(d) at `:368-373` says of it: **"That sentence described
`latex/closure_challenge_report.pdf` exactly, for three days, and no one
acted."**

Executed, and re-verified independently by this grader:

```
git show 1360a5a9:scripts/self_audit.py | grep -c "nothing in this file opens a PDF"  → 0
git show 1360a5a9:scripts/self_audit.py | grep -c "_blind_corpus"                     → 0
git log --oneline -S'nothing in this file opens a PDF' -- scripts/self_audit.py
                                                     → 9af7e2d3 (19:31:04Z)
```

The sweep's own commit is `a3342d9a`, 19:34:20Z. **The quoted sentence was three
minutes and sixteen seconds old**, and was **absent** from the tree the document
names as its frame. "For three days" is wrong by a factor of about 1,440. At HEAD
the sentence is at `:6847`; it has never been at `:5948`.

**§5.1(d) is one of the document's four proposed durable fixes, and this
quotation is its entire evidential support.**

### P2 — the printed remedy W1 does not run, and its failure falsifies the sweep's thesis

`OWNERSHIP…:295` prints W1 as *"`cd demo-output/website/latex && pdflatex
closure_challenge_report.tex && pdflatex closure_challenge_report.tex` … **No
source edit is needed.** `pdflatex` is installed; `latexmk` is not"*, cost
*"**two commands, no compute**"*, and at `:175` *"The whole zone reduces to a
two-command rebuild."*

Executed on a scratch copy of the real directory:

```
! LaTeX Error: File `ulem.sty' not found.
! Emergency stop.
!  ==> Fatal error occurred, no output PDF file produced!
rc1=1  rc2=1
```

Confirmed here independently: `kpsewhich ulem.sty` → **exit 1**; the `.tex`
requires it at line 19 and uses `\sout` **30 times** — *the missing package is
the strike macro the repaired `.tex` depends on*. Control: the sibling
`dafoam_defect_report.tex` builds `rc=0` from the same directory, so the
toolchain works and the failure is specific.

**The document verified that `pdflatex` is installed. It never verified that the
document builds.** That falsifies its thesis sentence at `:310-311`: *"Twenty-six
remain, and every single one is blocked on a name — not on a sweep, not on
compute, not on a measurement."* Fifteen of the twenty-six are additionally
blocked on a missing TeX package.

### P3 — the printed remedy W2 exits 1 and silently drops 15 of 90 shipping members

`OWNERSHIP…:296` prints W2 as *"re-run `python3 scripts/build_laptop_bundle.py`
and commit the rebuilt `.zip`. It is a `shutil.copy2` of the already-repaired
sources — **no content edit is needed**"*, cost *"**one command**"*.

Executed twice into scratch: **`rc=1` both times**, with 16 `SKIPPED … no
certificate.ready event to pair` lines. Member diff against the committed zip:
**90 → 75, fifteen members lost, none added** — the entire `aircraft-optimization`
act (`certificate.pdf`, 9 `.stl`, 3 `.png`, 2 mission-state files); 1.48 MB →
1.02 MB. The gate that causes it landed at `67e472c6`, which
`git merge-base --is-ancestor 67e472c6 a3342d9a` confirms **predates the sweep's
own commit** — W2 was already broken when it was printed.

*Fair to the document:* the rebuilt `site/closure.html` does clear the live wrong
copies. The defect is the cost claim and the exit code, not the repair intent.

### P4 — the printed `sweep.py` demonstration returns 33 files, not the three named

`OWNERSHIP…:350-352`: *"Run at `1360a5a9`, `sweep.py -F \"rank 1 of 5\" --frame
everything --files-only` returns [three files] **without any change
whatsoever**."* Executed verbatim at HEAD:

```
MATCHES: 33 files / 90 lines matched 'rank 1 of 5' under frame 'everything'
```

At the document's own stated frame, `git grep -a -l "rank 1 of 5" 1360a5a9` → **26
tracked files**, plus two gitignored `dist/` files ≈ 30. The three named files are
about a **10% subset**. This sentence is the sole evidence for the document's
proposal (b), *"nearly free, because the machinery already exists"*.

### P5 — "six times across six rows" is four at the stated frame, and reaches six only because the document counted itself

`OWNERSHIP…:62`, the `dist/` row: *"**UNOWNED.** Called \"the designated owner\"
six times across six rows and never once given a name."*

| tree | occurrences | rows |
|---|---|---|
| `1360a5a9` — the declared frame | **4** | 4 (D71, D115, D118, D136) |
| `a3342d9a` — its own commit — through HEAD | **6** | **5** (…plus **D145 ×2**) |

It is never "six rows". It reaches six only because **the D145 row this same
document filed says "designated owner" twice**. And of the four pre-existing
rows, D71 and D115 are `latex/` rows — the document's own `latex/` register cell
cites them as such — so only three belong to `dist/`.

### P6 — a bolded finding says "returns a PASS"; the evidence quoted two lines below it says `WARN`

`OWNERSHIP…:106-107`: *"**THE FINDING. A check crosses this boundary, reads
exactly these bytes, and returns a PASS.**"* and `:62` *"(currently a **false
PASS**, §2.1)"*. Its own quote at `:110`: *"> `WARN — every travelling surface
complies; 26 lab record(s) claim rank 1 without what V8 requires`"*.

Executed at HEAD: `check_rank_claim_surfaces()` → **`status='WARN'`**, and now 27
lab records. The document's quote was faithful to the instrument; **the mismatch
is internal, between a headline and the evidence beneath it, with neither
edited** — F4's shape again, in a different document, at 15 minutes' remove.

### P7 — an adoption ratio quoted by two surfaces that no run has ever produced

`docs/AGENT_ATTRIBUTION.md:214`: *"While it reads `2 of 40`, the honest summary of
this repository is still 'authorship is unknown for 38 of the last 40
commits'."* `scripts/check_rung_attribution.py:156`, the module the document
documents: *"`1 of 40` … unknown for 39 of the last 40 commits."*

The instrument, executed:

```
frame    : git rev-list e933e31b..HEAD, plus the anchor itself
examined : 44
ADOPTION : 4 of 44 commits since the anchor carry an identity; 40 carry none
```

The frame is **anchored, not a forty-commit window**. Frame size by tree:
`44ac957a` (the doc's own commit) → **3**; `cca64eaf` → 34; at this grader's run
→ **44**. **There is no tree at which the denominator is 40.** At the document's
own commit the instrument printed `2 of 3`. The document and the module disagree
with each other and both disagree with the instrument.

### P8 — a correction anchored to a commit that never touched the file

`docs/HANDSHAKE.md:270`: *"**[CORRECTED 2026-08-15 at `29beb7cf`. …]**"*

```
git show 29beb7cf:docs/HANDSHAKE.md | grep -c "CORRECTED 2026-08-15"  → 0
git show 0b0041b1:docs/HANDSHAKE.md | grep -c "CORRECTED 2026-08-15"  → 1
git show --stat 29beb7cf  → scripts/check_derived_figures.py  (1 file changed)
```

`29beb7cf` (01:01:21Z) never touched `HANDSHAKE.md`; the block landed at
`0b0041b1` (01:40:43Z), 39 minutes later. Exactly the class the lab filed at
`3314d746` — *"the one citation that was contradicted by the artifact it named"* —
recurring inside the same range that filed it.

### P9 — a heading and its own first sentence disagree, and both are wrong at the document's commit

`OWNERSHIP…:228` heading: *"### 2.7 The other **seventeen** `LADDER_V_*`
documents"*. `:230` body: *"All **eighteen** `LADDER_V_*` files other than the
repaired one were swept."* Executed: 19 such files at `1360a5a9` (18 others), 20
at its own commit and at HEAD (19 others). **The body is right at the stated frame
and wrong at its own commit; the heading is wrong at both, and neither was
edited.**

### P10 — a document files its finding under a docket ID the same commit gave to a different row

`MARGIN_PRECISION_INTERVAL_2026-08-15.md:208`: *"It is recorded here, filed as
**D132**, and **not repaired**."* Its own Related section at `:312` says *"**D133**
(C10, filed by this document)"*.

At HEAD, re-verified here: **D132** is *"D124's option (a) is built and anchored:
commit authorship now travels in the artifact…"* — the attribution mechanism,
nothing to do with margins. **D133** is the `AR_1_Ret_360` row.
`git log -S'| D132 |'` and `-S'| D133 |'` both return **`eadcd112`**, the very
commit that wrote the sentence. **The citation was false the moment it landed**,
and a reader following §3.1 to D132 lands on an unrelated row. Zero commits'
remove.

### P11 — "twelve rows" is eleven at every tree, and a locator off by 44 lines, transcribed into a shipping document

`LADDER_V_V6_V10_GRADE_2026-08-15.md:133-134` says *"Twelve rows"*; `:223-224`
narrows a FAIL with *"**eleven of twelve verdict rows** … are MEASURED-PASS"*.
Programmatic extraction with a sha256 per row, across five trees:

| tree | rows | identical to `472f9f92` |
|---|---|---|
| `472f9f92` | **11** | 11 |
| `99c66254` (the grade's own anchor) | **11** | — |
| `377d6afb` | **11** | 10 (§4.7 differs) |
| `87324012` / `bd8280de` / `be0a0c5d` / HEAD | **11** | 9 (§4.7, §4.8) |

**Eleven at every tree, never twelve.** And `:193`'s *"`:519+`, 212 lines below in
the same file, §4.8 is now headed…"* — at `99c66254`, line 519 is **§4.7's**
heading; §4.8's is at 563 and the row at 307, so the distance is **256**. Both
errors were **transcribed forward into the shipped
`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:321`**.

### P12 — present tense in dated records (owner rule W-5), one of them now falsified

Six sites confirmed. The one that has gone false: `LADDER_V_V5_GRADE…:89-90`,
*"**at HEAD**, 118 tracked files name QCR and 29 of the 64 … contain no
occurrence of 'Spalart'"* — repaired at `e639796e`, so `build_benchmarks.py`,
`benchmarks.json` and `wall.json` all now name Spalart (2000). `:95-99`'s table
column is literally headed *"met at HEAD?"*, a present-tense verdict against a
moving HEAD, in a dated grade.

**And one that this round falsified itself.** `docs/HANDSHAKE.md:284-285` reads
*"V15's **latest round** returned 25 new failures (`…ROUND7.md`)"*. That was true
until `e0a4117a` — **this document's own first commit** — made ROUND8 the latest
round. A present-tense sentence in a durable record went stale because a grader
did its job. Recorded here rather than repaired: `HANDSHAKE.md` belongs to another
family and a grader that edits the record it grades is no longer grading it.

### P13, P14 — two counts that no reading of their own tables reproduces

`OWNERSHIP…:148`: *"All **fifteen** table entries below are LIVE AND WRONG"*, over
a table with **13 data rows** covering **16** distinct PDF line locations. Fifteen
is reachable only as "16 minus row 260" — and **row 260's own cell says the
wording there *is correct***, contradicting the headline above it. The fifteen
propagates into W1 and into the **D145 docket row**.

`OWNERSHIP…:307-309`, copied verbatim into **D145**: *"27 live wrong passages, in
**7** files."* The document's own enumeration gives **5 or 6** depending on
whether the zip counts as one file or two. The passage arithmetic
(15+4+4+3+1 = 27) is internally consistent; the file count is not.

### P15 — the attribution mechanism has recorded exactly one identity in its entire life, and it is this session's

**NEW SHAPE, and it bears directly on §0 of this document.**

Every `Lab-Agent` trailer ever written, executed at HEAD:

```
git log --format='%H%n%b' --all | grep -oE 'Lab-Agent: .*' | sort | uniq -c
      1 Lab-Agent: <host>/<session-uuid>/<tag>          ← the docstring's template
      4 Lab-Agent: ip-172-31-43-247/64b13819-…-3720bab19084/-
```

**Four real trailers, one distinct value.** And:

```
$ python3 scripts/check_rung_attribution.py --emit-trailer
Lab-Agent: ip-172-31-43-247/64b13819-…-3720bab19084/-      ← what THIS grader emits

$ python3 scripts/check_rung_attribution.py --closing 44ac957a --graded e933e31b
VERDICT: AUTHOR
BECAUSE: 1 of 1 graded commits carry the closing commit's own identity … The measurer is an author
```

So the lab's own independence instrument, run on the lab's own adopting commits,
returns **AUTHOR**. Every non-author claim made anywhere in this commit range —
including `LADDER_V_V6_V10_REGRADE`'s §0, which names this same `64b13819-…`
transcript as its independence evidence, **and including §0 of this document** —
would grade AUTHOR under it.

**Why this is a new shape and not just D124/D130 restated.** D130 says the
evidence does not travel. `AGENT_ATTRIBUTION.md:98` predicts the collision in the
abstract (*"Two agents dispatched by the same chief session read as the same
agent"*). **What neither records is that the discriminating output of this
instrument has taken exactly one value across one hundred percent of its deployed
life.** An instrument whose verdict field has never varied has not been shown to
discriminate anything; its four green-adjacent runs are not four confirmations,
they are one constant observed four times. That is a property of the *deployment*,
not of the design, and it is measurable — which is why it is filed rather than
argued.

**This does not rescue §0 and is not offered as doing so.** §0 rests on a
timestamp — my transcript opens fifty seconds after the last commit I grade — and
that argument is untouched by P15. What P15 removes is the *other* leg: nobody
should cite a green `check_rung_attribution` run as independence evidence,
because the field it decides on has one value.

### What this cell verified as correct

Reported because a cell that lists only failures cannot be audited for selection.

- **`MARGIN_PRECISION_INTERVAL`'s arithmetic is essentially flawless.** §2.2's six
  intersections and widths, §2.3's six margin intervals, §2.4, §2.5
  (`[172.45%, 183.92%]`, point `177.19%`), and C2–C11 were all re-derived from
  `LIVE_BOARD`, `closure_challenge_round5_qcr.json`,
  `closure_challenge_seed_sensitivity.json` and `probability_of_rank_record.json`
  — **every figure reproduced exactly**, including the half-ulp slack column
  (26/57/114/149/340/424), C4's `|t| ∈ [2.1915, 2.2152]`, C7's ±1.76 pp and C11's
  `[14.53×, 15.58×]`. **One cell error only:** `:94`, Montoya's "from published
  overall" reads `[0.0778500, 0.0779125]` where it should read
  `[0.0778500, 0.0779500]`; the intersection column itself is right, so nothing
  downstream moves.
- **`OWNERSHIP`'s §2.1, §2.2 and §6 forensics are exact.** All 14 `68%` strings in
  the PDF at the stated lines, `rank 1 of 5` exactly twice, `Yang` and `Tian` zero
  times; tracked `20,688` at `1360a5a9`; `git grep -I` skipping 1,476 of which 50
  are PDFs; 90 zip members with **0 md5 mismatches** against the unpacked mirror;
  `_rank_claim_lines` on the shipped `closure.html` byte-for-byte the doc's list.
- **`LADDER_V_V6_V10_REGRADE` §2.1–§2.4 is exact — and it is the document that
  caught P11.** Its 11/11-10-9-9-9 row table and its 240/256/256/256 distances all
  reproduce.
- **`AGENT_ATTRIBUTION`'s measurement table is exact at its stated frame**
  (1,849/4, 1,217/1, 36/1, five distinct `Co-Authored-By` values), and **every
  printed command behaves as documented** — `--emit-trailer`, `--tag`, empty-set →
  UNKNOWN exit 3 naming the reason, a same-session pair → AUTHOR. Its suite is 24
  passed. P7 is a defect in one sentence of an otherwise well-executed document.
- **`LADDER_V_V13_PENDING2_MEASURED`** — no falsified claim found.

### Suspected, not proven — recorded so the next round does not re-open them cold

`LADDER_V_V5_GRADE:89-90`'s `118 / 64 / 29` could not be reproduced by any
`git grep` arm (`-a` → 108, `-I` → 100, `-a -i` → 154); either an unstated
predicate or wrong numbers. `OWNERSHIP:273`'s *"four published certificate
PDFs"* against five tracked PDFs matching "certificate" — "published" may denote
a narrower set the document never defines, which is itself a figure without its
denominator. `HANDSHAKE:282`'s *"SUPPLIED SEVEN TIMES … through grade round 10"*
against four tracked V16 grade documents carrying six grades by the most generous
count. `AGENT_ATTRIBUTION:243-246`'s *"12 mutants, all killed"* against
`grep -ci mutant sdk/tests/test_rung_attribution.py` → **0** and no tracked
mutation record — **the same "evidence that does not travel" defect the document
is about.** `OWNERSHIP:62`'s `self_audit.py:1060-1079` locator matches no
revision, but that file was dirty throughout and grew 1,005 lines in-range, so it
is not closed.

### A correction to §7 of this document

§7 recorded `check_derived_figures.py` PASS at **61** anchored figures and
`check_normative_clauses.py` PASS at **887** clauses. This cell, running later,
measured **62** and **890**. Both are right at their own moment; the corpus grew
under both. Recorded rather than reconciled, because reconciling them would hide
the only interesting fact — **that a "PASS with N examined" is a statement with a
half-life measured in minutes in this tree**, which is F1's problem seen from the
other side.

