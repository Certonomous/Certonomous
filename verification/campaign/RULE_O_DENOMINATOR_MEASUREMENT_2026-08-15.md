# Rule O, measured — what a denominator rule would cost and catch in V14

**Measured 2026-08-15, 21:02–22:3xZ (clock audited with `date -u` before any date was written).**
No solver run, no scoring call — **the ledger stands at 6**. Nothing sent, uploaded, filed or
registered; the scoring pin `deb91557` was not moved. `dist/`, `demo-output/website/latex/`,
`LAPTOP_SHOOT.md`, `motorbike-video/`, `scripts/self_audit.py`,
`scripts/check_derived_figures.py`, `scripts/check_normative_clauses.py`,
`docs/USING_THIS_LAB.md` and other agents' in-flight files were **read and never written**.

**THIS DOCUMENT DOES NOT RULE AND DOES NOT CHANGE V14'S CRITERION.** It answers one question
with numbers, for a chief who has to decide: *if V14's criterion were extended to cover the
class it currently cannot reach, what would that extension catch, and what would it cost?*
The instrument is `RULE_O_DENOMINATOR_MEASUREMENT_2026-08-15.py`, beside this file. It is not
wired into `scripts/self_audit.py`, is not a gate, and nothing calls it.

---

## 0. The gap being measured, stated in the criterion's own terms

V14 demands *"a repo-wide search for **every score literal** … plus **every prior-art sentence
fragment**"*. Its executed rules are **S** (our scores), **B** (the board's 54 published
values), **R** (the four derived margins and bounds) and **P** (the prior-art fragment). Every
one of those families is a **number that names a score**.

The V12/V13/V14 grade at `9c2734f8` found eight live four-entry claims in the tracked shipping
archive and showed that the majority of them are **not score literals**. `2nd of 5`,
`3rd of 5`, `5 of 8 → 4 of 8` are **ordinals and counts about ourselves**: their digits are
positions and tallies, and no rule V14 names derives them. That is D151's denominator gap, at
the level of the criterion rather than at the level of the sweep. A sweep fully faithful to
this criterion cannot see them.

**Rule O, the candidate measured here:**

> Every **ordinal placement** and every **count-of-N claim**, about **any** entrant including
> ourselves, graded against values derived from **the board's own length and the per-case
> values** — never against a literal list.

Two match families, disjoint by construction:

| | family | shape | why V14 cannot reach it |
|---|---|---|---|
| **O1** | ordinal placement | `<n>[st\|nd\|rd\|th] of <m>`, the word `rank` **optional** | not a score literal; and `check_rank_claim_values`'s `_VALUE_BOARD_SIZE` *requires* the token `rank`, so `2nd of 5` is invisible to it too |
| **O2** | count out of N | `<k> of eight\|8` — best-on-board, cases-won | not a score literal |

**Everything Rule O grades against is derived at run time**, from `LIVE_BOARD` in
`sdk/scripts/probability_of_rank.py` read by `ast.literal_eval` (**never imported**) and from
`closure_challenge_round5_qcr.json` → `round5_per_case_full`. No admissible value is typed
into the instrument. Derived today:

- board **6 entrants**, `fetched` `2026-08-11T23:33Z`; **7** positions counting our row
- our overall `0.056647191704213645` → **rank 1 of 7**
- per-case ranks of 7: `alpha_15_13929_4048` **2**, `alpha_15_13929_2024` **2**,
  `alpha_05_4071_4048` **1**, `alpha_05_4071_2024` **1**, `AR_1_Ret_360` **3**,
  `AR_3_Ret_360` **4**, `AR_14_Ret_180` **4**, `NASA_2DWMH` **7**
- best-on-board **2 of 8**, belonging to our model **0 of 8**
- pairwise cases-won against the six entrants: **{1, 3, 4, 5, 7}**

---

## 1. THE FRAME, re-measured rather than inherited

| arm | reach | measured today |
|---|---|---|
| **1 — tracked** | `git ls-files` | **20,702** paths; **18,975** decode as UTF-8 under 4 MB |
| **2 — untracked** | `git ls-files --others --exclude-standard` | **1** (`.autostop-hold`). The grade counted 3; the other two were other agents' in-flight test files and have since been committed. |
| **3 — gitignored** | `git ls-files --others --ignored --exclude-standard` | **37,242** |
| **4 — run tree** | `/usr/bin/find /home/ubuntu/certonomous-runs/ -type f -print0` | **132,049**, counted by NUL bytes on **one** enumeration |
| **containers** | `dist/certonomous-demo.zip` `zipfile`-decoded | 90 members, **78** decode as UTF-8 under 4 MB |
| **containers** | `pdftotext` over tracked PDFs | **50** PDFs, **50** non-empty extracts, 0 extraction failures |

**The run tree was NOT banded, and that is deliberate.** The grade records that
`find -size -2M` and `-size +2M` are **not complementary** — GNU `find` rounds up, so the
4,418 files that round to exactly 2 M fall through both, and a banded partition reported
96.7% coverage as complete. **A single `-print0` enumeration cannot have that hole**, and its
NUL count is **132,049**, equal to the grade's independently obtained total. Reconciliation
is by construction rather than by addition.

**Tool identity, proved not assumed.** `type grep` and `type find` both return *is a
function* in this shell — the wrappers are `ugrep --ignore-files` and `bfs`. Every count
above used `/usr/bin/grep` (**GNU grep 3.11**) and `/usr/bin/find` (**GNU findutils 4.9.0**).
`__pycache__` was purged before the first cell. Containers were **decoded**, never
byte-grepped.

**How PDF claims were read.** `\sout{}` is strike-and-**keep**, so a withdrawn figure sits in
the text layer of a correctly repaired report exactly as in a stale one, and no PDF verdict
below rests on an extract. Every PDF claim reported as LIVE was **rendered to PNG with
`pdftoppm` and read visually** — page 1 at 150 dpi and page 14 at 130 dpi of
`demo-output/website/latex/closure_challenge_report.pdf`. §4 says what was seen.

---

## 2. THE MEASUREMENT

Two configurations, so the cost of each gate is separable. **WIDE/BARE** is the naive
candidate: board-context gate including the bare words `rank`, `placement`, `overall`, and no
strike handling at all. **NARROW/MASKED** is the fair candidate: a context gate that names
the closure challenge specifically, plus a strike mask (`~~…~~`, `\sout{}`, `<s>`, `<del>`)
and a left-operand decline for `X → Y` corrections. `WIDE ⊃ NARROW` by construction.

| arm | cfg | hits | **admitted** | **faulted** | LIVE AND WRONG | CORRECT DATED HISTORY | MISREAD | **false-positive rate** |
|---|---|---|---|---|---|---|---|---|
| **shipping archive** (78 members) | narrow/masked | 31 | **24** | **7** | **6** | 0 | 1 | **1/7 = 14.3%** |
| shipping archive | wide/bare | 37 | 27 | 10 | 6 | 1 | 3 | 4/10 = 40.0% |
| **tracked PDFs** (50) | narrow/masked | — | — | **12** | **5** | 0 | 7 | **7/12 = 58.3%** |
| **tracked** (18,975) | narrow/masked | 897 | **476** | **393** | **0 of 40 sampled** | 4 of 40 | 36 of 40 | **40/40 = 100% on the sample; ≥ 92.5% at 95%** |
| tracked | wide/bare | 1,257 | 592 | 616 | — | — | — | (larger, not sampled separately) |
| **gitignored** (35,723 decoded) | wide/bare | 7,713 | 28 | **7,685** | 6 | 1 | **7,678** | **99.9%** |
| gitignored | narrow/masked | 3,490 | 25 | **3,465** | 6 | 0 | **3,459** | **99.8%** |
| **run tree** (132,049) | narrow/masked | **0** | 0 | **0** | 0 | 0 | 0 | — |
| run tree | wide/bare | 1 | 0 | **1** | 0 | 0 | 1 | 1/1 = 100% |
| **untracked** (5 at run time) | narrow/masked | 62 | 19 | **42** | **0** | 12 | 30 | **42/42 = 100%** |

**The untracked arm faults this measurement.** All 42 of its faults are in
`RULE_O_DENOMINATOR_MEASUREMENT_2026-08-15.md` and `.py` — the document you are reading and
the instrument that produced it, both of which quote `2nd of 5`, `3rd of 5` and `rank 1 of 5`
in order to report them. **Zero are a live claim.** The arm also demonstrates a frame hazard
worth recording plainly: the untracked set was **1 file** when §1 measured the frame and
**5** when this arm ran, because this pass created two of them. A frame measured before the
sweep and a frame measured during it are different frames, and the difference here is the
sweeper's own output. The gitignored arm's 6 true faults are the extracted bundle
`dist/certonomous-demo/site/closure.html`, which mirrors the zip and is the same six lines
already counted there — **not six additional defects.**

**The run tree is clean, and the prefilter that establishes it is a proved superset.** All
132,049 files were scanned by `/usr/bin/grep -aE` in two passes whose union covers every
string either family can match — the O1 shape (`<token> of <token>`, asterisks allowed) and
the O2 shape (`of [the] eight|8`) — yielding **480 candidate files**, over which Rule O was
run in full. Narrow/masked returns **zero hits**. The naive wide/bare configuration returns
exactly one fault, `A3-rung2-n28-tpc1/fd3_run.log:880` — *"FD3 select shape: argmax|g| index
**115 of 120**"*, a finite-difference gradient index — which is a misread and the only one.
**V14's arm 4 is clean under Rule O as well as under score literals, and extending the
criterion would not change that.**

**The gitignored arm is one sentence shape repeated 7,671 times.**
`sdk/chief-engineer-runs/mission-state/*.events.jsonl` — 158 mission transcripts, each
carrying *"Major iteration **N of 47**, C_d 0.021…"* for every adjoint iteration — supplies
**7,671 of the 7,685 faults, 99.8%**, and not one of them is a claim about any leaderboard.
The remaining 14 are the extracted bundle `dist/certonomous-demo/site/`, which mirrors the zip
exactly and contributes the same 8 lines §2.1 lists, and four aircraft-optimisation
transcripts. **A rule whose repo-wide output is 99.8% one progress counter is not a search;
it is a denial of service on the reader.**

**Every classification in the LIVE AND WRONG / CORRECT DATED HISTORY / MISREAD columns is a
hand reading, not the script's heuristic.** The script carries an automatic classifier; it was
measured against the hand reading on the shipping archive and **disagreed on 5 of 7**, so its
output is not used for any number in this table. That is stated because a measurement whose
own labels are machine-generated by the thing being measured is not a measurement.

### 2.1 The shipping archive, every fault classified by hand

| member : line | quote | class | why |
|---|---|---|---|
| `site/closure.html:341` | `3rd of 5` | **LIVE AND WRONG** | `AR_14_Ret_180` is **4th of 7** on the live board; the denominator is a four-entry artifact |
| `site/closure.html:434` | `2nd of 5` | **LIVE AND WRONG** | `AR_1_Ret_360` is **3rd of 7** |
| `site/closure.html:435` | `3rd of 5` | **LIVE AND WRONG** | `AR_3_Ret_360` is **4th of 7** |
| `site/closure.html:436` | `3rd of 5` | **LIVE AND WRONG** | `AR_14_Ret_180` is **4th of 7** |
| `site/closure.html:502` | `rank 1 of 5` | **LIVE AND WRONG** | rank **1 of 7**; this is the one instance the sweep of record named (D112) |
| `site/closure.html:426` | `six of the eight` | **LIVE AND WRONG**, and **not on the grade's list of eight** | see §3.2 |
| `site/closure.html:234` | `4 of 4, blind` | MISREAD | the decline gate's four correct decisions; no board, no denominator of ours |

### 2.2 The tracked arm, 40 faults drawn at random and read by hand

Random sample, seed `20260815`, from the 393 faults of the narrow/masked configuration.
**Zero of the forty are a live wrong claim.** Four are correct dated history; thirty-six are
misreads. Rule-of-three: with 0 true positives in 40, the true-positive rate is **at most
7.5% at 95% confidence**, so the false-positive rate on this arm is **at least 92.5%**.

The misreads fall into five recurring shapes, and they are the cost:

1. **Unrelated denominators.** `31 of 47` and `42 of 47` adjoint major iterations in
   `sdk/tests/fixtures/control_room_adjoint_stream.jsonl` (48 faults from that one file),
   `rank 178 of 180` docket position, `257 of 1,635 logs`, `30 of 34` self-audit checks,
   `98 of 600` core-min, `2 of 4` mesh boundaries, `2 of 10` papers, `7 of 7` features.
2. **The labelled test corpus doing its job.** `sdk/tests/fixtures/absolute_claims_labelled.json`,
   `sdk/tests/test_rank_claim_surfaces.py`, `sdk/tests/test_rank_claim_values.py` carry the
   withdrawn sentences **on purpose**. Faulting them is faulting the control.
3. **The guard's own source.** `scripts/self_audit.py:1437` and `:1724` are faulted for the
   `rank 1 of 5` inside their own explanatory comments — and one of those comments says, in
   terms, that this is the trap.
4. **Correct live per-case ordinals.** `4th of 7`, `5 of 7`, `2 of 7`, `5th of 7` are the
   **right** answers on the live board, faulted because the window names no case alias Rule O
   recognises so it grades a per-case ordinal against the overall placement.
5. **Correct reporting of the defect.** `docs/P33_CROSS_SURFACE_SWEEP.md`,
   `OWNERSHIP_BOUNDARY_SWEEP_2026-08-15.md`, `LADDER_V_V6_V10_GRADE_2026-08-15.md` and this
   lab's grades **quote** `rank 1 of 5` in order to report it. Use-vs-mention, at scale.

### 2.3 Two defects found in Rule O itself, by measurement rather than by review

Recorded because they are the reason the numbers above are what they are, and because both
are defect classes this lab has already paid for once.

- **`duct` has no word boundary, and `product` contains it.** The first draft's context gate
  fired on DAFoam adjoint work across the run tree — `compute_jacvec_product`,
  `calcJacTVecProduct` — and Rule O faulted `43 of 60 sampled diagonal indices` and
  `one of four constants` against the closure board's length. **Five faults, none of them a
  claim about any leaderboard.** This is the V14 grade's own `68%`-matching-`1.68%` defect,
  reproduced inside the instrument built to measure that class. Fixed to `\bducts?\b`; the run
  tree then returns what §2 records.
- **O1 swallowed O2's spans.** `4 of 8` matches both families, and with O1 first every
  best-on-board count was graded as a *placement* — so the instrument reported `2 of 8`, the
  **correct current count**, as a wrong denominator. Fixed by running O2 first and making the
  families disjoint on overlapping spans.

A third is **not** fixed and is reported as a limit: the **frozen-pin decline**. `deb91557`
scores and does not rank, so a claim bound to it is a claim about a different board and Rule O
declines it. On page 1 of `closure_challenge_report.pdf` the sentence is *"the best overall
number on the board as published at benchmark commit `deb91557` — **rank 1 of 5**, scored
locally"*: the pin sits eleven characters from the ordinal, so the decline fires, and Rule O
**misses the single most prominent instance of the class in the corpus**. Narrowing the
decline window to ±100 characters recovered the correct `rank 1 of 7` sentences on the shipped
pages but does not recover this one. **A decline is a false negative that does not appear in
any false-positive rate**, which is precisely why it is written here.

---

## 3. WHAT RULE O WOULD HAVE CAUGHT OF THE EIGHT — AND WHAT IT STILL MISSES

### 3.1 Against the grade's eight

| # | shipped claim | Rule O | note |
|---|---|---|---|
| 1 | `closure.html:341` `3rd of 5` | **CAUGHT** | never named by the sweep of record |
| 2 | `closure.html:342` `5 of 8 → 4 of 8` | **MISSED** | see §3.3 — this is the deep one |
| 3 | `closure.html:411` `comparable to the 0.0029 margin` | out of scope | a **score literal**; V14's Rule R already derives `0.0029`. Its survival is an execution gap in the sweep, not a definitional one. |
| 4 | `closure.html:434` `2nd of 5` | **CAUGHT** | never named |
| 5 | `closure.html:435` `3rd of 5` | **CAUGHT** | never named |
| 6 | `closure.html:436` `3rd of 5` | **CAUGHT** | never named |
| 7 | `closure.html:502-503` `rank 1 of 5 … comparable to its margin` | **CAUGHT** (ordinal half) | the `comparable` half is not Rule O's family; this is the one instance the sweep named |
| 8 | `benchmarks.html:148-149` `0.0029 margin … comparable size (0.0024)` | out of scope | **score literals**; Rule R derives both. Execution gap. |

**Rule O catches 5 of the 8, and 4 of those 5 have never been named by any sweep.** Two of the
three it does not catch (**3** and **8**) are inside V14's *existing* Rules S/B/R and did not
need a new family at all — which sharpens the chief's question: part of V14-1 is an execution
failure that no criterion change repairs.

### 3.2 A ninth live claim, found by Rule O, not on the grade's list

`dist/certonomous-demo.zip!certonomous-demo/site/closure.html:426`:

> *"…the table below compares against the **four**-entry board and has not been re-derived
> against the six; against the six, the 'best published' column would be lower on **six of the
> eight rows**."*

Re-derived here cell by cell — four-entry best (Reissmann, Wu & Zhang, Liu, Montoya) against
six-entry best, on all eight cases:

| case | best of four | best of six | lower? |
|---|---|---|---|
| `alpha_15_13929_4048` | 0.0592 | **0.0432** | yes |
| `alpha_15_13929_2024` | 0.1195 | **0.0998** | yes |
| `alpha_05_4071_4048` | 0.0569 | 0.0569 | **no** |
| `alpha_05_4071_2024` | 0.0760 | **0.0748** | yes |
| `AR_1_Ret_360` | 0.0387 | **0.0291** | yes |
| `AR_3_Ret_360` | 0.0341 | **0.0311** | yes |
| `AR_14_Ret_180` | 0.0325 | **0.0250** | yes |
| `NASA_2DWMH` | 0.0364 | **0.0294** | yes |

**Seven of the eight rows, not six.** The tracked source has already been corrected — the
repaired `demo-output/website/closure.html:482-488` strikes it and says *"its count was wrong:
it is **seven** of the eight rows, not six"* — and the **shipping archive still carries the
live wrong sentence**, because the zip is six files stale. So V14-1's finding is **nine**, not
eight, and the ninth is again a count-of-N and again outside every family V14 names.
**`check_rank_claim_values` does not name it either**, in any register: its 23 faults do not
include it and neither does its 95-entry ungraded list, so it is not a declined passage — it
is one the instrument never reached.
**Reported, not repaired**: `dist/` has a designated owner and this pass measures.

### 3.3 What Rule O still misses, and why it is not fixable by tuning

**`5 of 8 → 4 of 8` at `closure.html:342` survives Rule O**, and the reason is structural
rather than a gate setting. Rule O derives the admissible counts-out-of-eight from the board:
best-on-board **2**, belonging to our model **0**, and pairwise cases-won **{1, 3, 4, 5, 7}**.
The union is **{0, 1, 2, 3, 4, 5, 7}** — seven of the nine integers a count-of-eight can take.
`4 of 8` is simultaneously the **withdrawn** best-on-board count *and* the **correct**
cases-won count against Yang, and `5 of 8` is the correct cases-won count against Wu & Zhang
and Tian. **No arithmetic over the board can separate them**, because the surface does not say
which quantity it means. O2's contribution to the catch is therefore **zero on this archive**:
every count-of-eight it graded was admitted, and the two faults it did raise (`six of the
eight`, `4 of 4`) are the one it got right for the wrong reason and one misread. **The entire
5-of-8 catch above comes from O1, the ordinal arm.**

Also still missing, unchanged from the grade's own §4.5: rendered text, PDF figure and font
layers, the 955 PNGs, semantic variants sharing no searched fragment, and any claim carrying
no number at all.

---

## 4. THE COMPILED PDF — read visually, because an extract cannot decide it

`demo-output/website/latex/closure_challenge_report.pdf` is a **second travelling surface**
of the same class, and D91/D148 already carry it. It is re-confirmed here **by rendering**,
not by extraction, because that is the only reading a strike-and-keep report admits:

- **Page 1, 150 dpi.** The status box and the abstract carry, in **bold upright type with no
  rule through any of it**, *"**rank 1 of 5, scored locally**"*, *"**P(rank 1) = 68%**"* and
  *"eight cases cannot pin that tighter than **2−100% at 95%**"*. Nothing on that page is
  struck.
- **Page 14, 130 dpi.** Table 4's Attribution column reads *"2nd of 5; ties rank 2 at
  published precision"*, *"3rd of 5, within published-precision noise of rank 2"*, *"3rd of 5;
  the 0.00003 lead was priced and lost"*, and the Overall row reads *"rank 1 of 5, scored
  locally; P 68% (2–100% at 95%)"*. The caption above it repeats **P(rank 1) = 68%**. **None
  of it is struck.** §3.5's prose on the same page reads *"the best score on the public board
  on **four of eight** cases"*.

Rule O over the extract raised **12 faults across 50 PDFs**, of which **5 are live and wrong
and all 5 are in this one file**; the other 7 are misreads (`4 of 4 correct` decisions,
`28 of 29` cases, `eight of ten`, `7 of 7` features, `three of 200` in an unrelated paper, and
a parse error on *"a gap to rank 2 of 0.0030"*). **FP rate 58.3%.** The page-1 instance is a
**false negative** for the frozen-pin reason of §2.3.

---

## 5. THE COST STATEMENT — what the measurement supports, and what it does not

**IT SUPPORTS THIS.** On the arm that matters — surfaces that **travel** — Rule O is
accurate and it finds what no sweep of record has found. On the shipping archive it faults 7
and **6 are true**, a false-positive rate of **14.3%**; on the compiled report PDF it finds 5
live four-entry claims. It catches **5 of the 8** shipped claims the V14 grade names, **4 of
which have never been named by any sweep**, and it found a **ninth** the grade did not have.
The class it reaches is exactly the class V14's Rules S, B and R structurally cannot reach.

**IT DOES NOT SUPPORT RUNNING RULE O OVER THE LAB RECORD.** On the tracked arm Rule O faults
**393** passages, and in a random sample of 40 read by hand **not one is a live wrong claim**
— 4 are correct dated history and 36 are misreads. **The false-positive rate on that arm is at
least 92.5% at 95% confidence.** A rule that fires 393 times to find nothing is worse than the
74%-false-positive checker this lab already carries, and comparable to
`check_rank_claim_values`'s own ≥ 78.3%, measured here. One tracked file's 48 faults are all adjoint
iteration counters, and on the gitignored arm **7,671 of 7,685 faults are the same counter**.
It would fault the labelled test corpus that exists to carry withdrawn text, and it would
fault the guards' own explanatory comments. **A rule in that state does not get installed; it
gets ignored, and an ignored gate is a fail-open gate with a green light on it.**

**THE SPLIT IS THE FINDING, AND IT IS NOT A COINCIDENCE.** The same split is measured in §6 on the
instrument that exists: `check_rank_claim_values`, run here from its `HEAD` source, faults 23
and is wrong on **at least 18 of them — ≥ 78.3% overall — and on 0 of the 2 that travel**.
Rule O measures **≥ 92.5% internal** and **14.3% travelling**.
Two independently built instruments in the same class agree that the denominator predicate is
usable **only** where the surfaces travel. **What the measurement supports is a rule scoped to
travelling surfaces. It does not support a repo-wide one, and it does not support a
repo-wide one with a better strike mask** — the strike mask was measured and it moves the
tracked arm from 616 faults to 393, which is not the difference between unusable and usable.

**WHAT IT DOES NOT DECIDE.** Whether V14's criterion should be extended at all is Katie's, and
whether a travelling-only scope satisfies *"a repo-wide search … across tracked files, built
artifacts, and shipping archives"* is a real tension this measurement does not resolve: the
criterion's own words ask for repo-wide reach, and the measurement says repo-wide reach is
where the rule stops working. That tension is the ruling.

---

## 6. DOES THE EXISTING INSTRUMENT SUFFICE?

`check_rank_claim_values` (`847b4492`, `scripts/self_audit.py`) already implements most of
Rule O and was **not** rebuilt here. Read at `HEAD`, its RULE V1 grades the denominator of a
rank claim against `facts["entries"] + 1`; its RULE V2 grades the best-on-board count against
the derived `best` and `earned`; it carries a third-party arm added for D151 explicitly so
the predicate is built once for ours and theirs; it is three-valued and will not PASS from an
empty set; and it **does** open the shipping archive.

**ITS FALSE-POSITIVE RATE WAS MEASURED HERE BY EXECUTION, NOT TAKEN ON REPORT.** The
dispatch that commissioned this work cites *"77% overall, 0% on the travelling arm"*; the
lab's own record says the opposite about what is written down — that the check *"states no
false-positive rate and names no held-out reach set in its verdict, its BASIS or its build
commit."* Neither is treated as the presumed-correct side. `check_rank_claim_values` was
**run from the `HEAD` source** (extracted with `git show HEAD:scripts/self_audit.py` into a
scratch tree, because the working copy carries another agent's in-flight edits) over the
current corpus:

> **FAIL — 23 value faults: 2 on surfaces that TRAVEL, 21 on lab records.** Frame:
> 20,706 tracked paths considered, 20,509 opened including 90 archive members, 1,420 decoded
> and mentioning `rank` or `overall`, 485 rank claims found, 95 passages matched a rule and
> were declined with a reason.

Both travelling faults are true: `dist/certonomous-demo.zip!site/closure.html:502`
(`rank 1 of 5`) and `:503` (`comparable`, where the bound is `[177.12%, 178.82%]` of the
margin). **Travelling-arm false positives: 0 of 2.** Of the 21 lab-record faults, read by
hand, **at most 3** are live wrong claims; **7 are correct dated history** (two
`agenda/docket.json` fields explicitly headed *"DENOMINATOR SUPERSEDED … left byte-identical
as this item's dated record"*, the `.tex`'s correctly `\sout{}`-struck `4 of 8`, and three
dated pass checklists) and **11 are use-vs-mention**, including the check's own source at
`scripts/self_audit.py:1205`, this measurement's own docket row at `docs/DOCKET.md:570`, and
the V12 repair's quotation of the shipped defect it is repairing. **Overall false-positive
rate ≥ 78.3% (18 of 23) on the most generous reading of the three; 0% on the travelling
arm.** That corroborates the dispatch's 77% by independent execution, and it reproduces
Rule O's split in a second, independently built instrument.

**It does not suffice for this class, for three measured reasons, and one of them is small:**

1. **`_VALUE_BOARD_SIZE` requires the literal token `rank`.** Its pattern is
   `\brank[ \-]?(?P<n>…)\s+of\s+…`. `2nd of 5`, `3rd of 5` and *"the case falls to 3rd of 5"*
   carry no such token, so **four of the five claims Rule O caught are outside its regex** —
   not outside its arithmetic, which is correct and would grade them right. **This is a
   one-line widening of one pattern, not a new instrument**, and it is the single highest-value
   change the measurement identifies.
2. **`_BEST_COUNT` requires the word `best` within 80 characters.** It would reach
   `5 of 8 → 4 of 8` on that ground and decline the left operand correctly — but §3.3 shows
   the arithmetic cannot fault the right operand anyway, so widening it buys nothing here.
3. **Its 4 MB cap and UTF-8-only decode exclude the compiled PDFs**, where §4 finds five live
   claims. Its own docstring says so: *"anything that is not UTF-8 (every compiled PDF here,
   and `latex/closure_challenge_report.pdf` is the corpus's largest single concentration of
   withdrawn claims)"*. **The instrument names its own blind spot and the blind spot is where
   the claims are.**

**So: reuse, do not rebuild.** The measurement supports widening one regex in an instrument
that already has the right arithmetic, the right scoping and the right three-valued verdict —
**not** adding a second checker. Rule O as a standalone rule is the *measurement*; it is not
the recommendation, and it is not installed.

---

## 7. WHAT THIS MEASUREMENT CANNOT TELL A CHIEF

1. **Whether the tracked-arm false-positive rate is exactly 100%.** It is 40/40 on a random
   sample; the bound is ≥ 92.5% at 95%. The remaining 353 faults were not read by hand.
2. **Whether the classification boundary between MISREAD and CORRECT DATED HISTORY is the
   right one.** Both are false positives and the totals do not depend on it, but the shapes in
   §2.2 do.
3. **Anything about rendered pages, PNG contents, or PDF figure layers.** §3.3.
4. **Whether the strike mask is right.** It blanks `~~…~~`, `\sout{}`, `<s>`, `<del>` on
   character spans. It has no parser, and a claim struck by a dated banner three paragraphs
   above reads as live to it.
5. **Whether extending V14's criterion is the right response at all.** Two of the eight
   shipped claims were inside V14's *existing* rules and shipped anyway. A criterion change
   does not repair an execution gap.

*Measured by a non-author of V14's criterion, of the V12/V13/V14 grade, and of the shipped
pages. Zero solver runs, zero scoring calls, **ledger 6**. Nothing sent, uploaded, filed or
registered; the scoring pin was not moved. `dist/` and `demo-output/website/latex/` were read
and never written.*
