# The exposure map — which of tonight's conclusions rest on a sweep that cannot see them

**2026-08-16. Zero solver core-min, zero scoring calls; the ledger stood at 6 and was not touched.
Nothing was sent, posted, registered or created. NOTHING WAS RE-GRADED HERE.** This pass is an
author of the V10 closure, the agenda finalization, the four-call costing and the rulings record, so
it produces the map and routes every exposed item to a non-author. It takes no verdict.

---

## 0. The withdrawal that occasioned this, recorded first

**CHIEF RULING 5 (implement EIG recommendation 1) IS WITHDRAWN, 2026-08-16.** It was issued on the
measured ground *ρ = +0.197 at p = 0.035 against the gain table's +0.12 (n.s.)* — a significant
ranking against a non-significant one. **The number is not reproducible, and the withdrawal is on
that ground alone.** Measured: `git show 99015d92 --name-only` returns exactly two paths, a prose
record and a proposal file; **no dataset, no scorer and no ground truth were ever committed**, and
the per-item delivered-value grade the statistic correlates against exists in no artifact in the
tree. §3's populations `n = 2/35/7/26/44` are the **hand** tiers that §6's mechanical rule replaced
to remove hindsight, matching only at ρ +0.70; **the mechanical rule's own populations were never
published**, and a faithful reconstruction run here returns A3 n=2 (agreeing) but **A n=15 against
35** and **B n=13 against 7**, with no way to determine whether that is the reconstruction's defect
or the expected divergence. The cohort has also moved, **114 → 118** `done` items.

**The operative sentence: the action is not cheap; it is unverifiable, which is worse.**

**What would unblock it** — released here as a finding, not queued as work: (a) the two tests in
`sdk/tests/test_agenda.py` that encode the incumbent as their specification would have to be
released or changed with it; (b) **either** the mechanical rule as code **or** the V grades would
have to be recovered. Both (b) routes run only through the lookback agent or a re-run, because its
grading step was a judgement that was never written down.

**AND IT IS NOT A TASK QUEUED AGAINST `agenda.py`.** An un-implementable recommendation whose
evidence was never committed is **a finding about the lookback**, not work anyone is avoiding. It
should not sit on a list looking like a chore. `sdk/chief_engineer/agenda.py` was not modified.

---

## 1. The organising principle, because it decides the whole ranking

**A blind sweep endangers claims of ABSENCE, never claims of PRESENCE.** A sweep that cannot see a
class can only *miss*; it cannot manufacture a defect. So:

* **A `FAIL` is not exposed by a blind recogniser.** It rests on something the instrument *found*.
  Tonight's `FAIL`s — V5, V10, V12, V15, V16 — are safe from this failure mode, whatever else is
  true of them.
* **A `PASS`, a "clean", a "zero hits", a "no third instance", a "complete enumeration" IS exposed**,
  because each asserts that nothing more is there, and the instrument's blind class is exactly the
  region where "nothing more is there" was never tested.

There is one exception in the other direction, and it fired tonight: an instrument with **no model
of use-versus-mention** can produce a *false positive*, which is how a strike hazard was reported on
the ladder's governance file and refuted by its own author (`faa02f80`).

---

## 2. The five sweeps, with what each detects and what it is blind to by construction

| sweep | corpus actually reached | detects | **blind by construction** |
|---|---|---|---|
| **V10 closure** `c2cd83bf` (mine) | 19 files across the 5 enumerated surfaces; whole-file, strike-blanked, all patterns `\s+` | 8 four-entry literals, 14 ordinal/phrase/markup classes; 136 raw → 89 live, all adjudicated | **a stale CHARACTERISATION carrying no stale number** — the reopen's finding; also everything off the 5 surfaces, and `dist/` |
| **V10 repair** `fe54ec0a` | 18 files, 5 surfaces | same literal set, strike-blanked; controls incl. a live positive on the pre-repair tree | its **first cut used literal spaces** and returned 7 on the file whose heading wraps — self-caught, 7→8; residual `PRODUCT_LIST.md:1811` reported not repaired |
| **V12 grade** `b4596cb4` | **one file**, whole-file, wrap-safe, 17 strike spans blanked | 10 stale-literal/ordinal classes + board-comparative claims, closed by enumeration | **every other surface** — proved by D251, where the failing sentence had already travelled unstruck to two more files; untracked `dist/`; non-numeric staleness |
| **board-identification costing** D245 `fdfc3eba` | 474 tracked `.md`/`.html` at a pinned commit; 1,884 sites | whether a board claim *identifies* its board, in 5 classes | `.json`/`.py`/`.tex`/`.pdf`/`dist/`; **the TRUTH of any claim**, only its identification; ±10% on the meta split; and the **live tree** — `74848c6c` shipped "three sites are held" 94 seconds after a peer repaired two |
| **certification / sweep-shape audit** D242/D243 `6097856c` | 28 ladder records, 15,902 lines, read in full; 1 PDF rendered | certification read-extent; unread remainder **for class (b) only** | class-(d) reach is unboundable *in principle*; non-literal staleness; the **other 67 tracked PDFs**; and **its own literal-space patterns**, corrected at D244 |

### The four generators of a blind class, hardest to notice last

1. **Corpus definition** — the file never entered the set. `PROSE_GLOBS = ("*.md", "*.html")` in two
   standing instruments put every tracked `.tex` and all 50 `.pdf` outside every frame; `dist/` is
   **untracked**, so no `git grep` route in this lab reaches it (D252); `.gitattributes` marks ~1,476
   files binary and `git grep -I` skips them. **A silent zero at the level of the corpus, with no
   sweep involved and no control able to expose it.**
2. **Recogniser vocabulary** — what the instrument knows is a subset of what the corpus uses: the
   stale-literal list (D272), the strike syntaxes (D254, where the stripper knew three and the depth
   probe two), literal spaces against wrapped text (D244), code spans (D268).
3. **Wrong invariant** — the instrument measures something *adjacent* to the property. Strike
   **balance** instead of strike **placement**: a document at depth 0 still had two markers escape
   their code spans and blank **1,595 bytes** of its own evidence column (`67ce2bd2`).
4. **Wrong widening** — the fix that reaches the arm without grading its claim class. Adding `*.pdf`
   took the clause checker to 476 files at zero new faults and returned **PASS on the very artifact
   D243 had shown carries `rank 1 of 5`**. Measured and **rejected**: *a green frame over the defect
   that motivated it is worse than an admitted gap, because a gap is visible and a green frame is not.*

### And one distinction that no record has yet named, which is where the ranking below comes from

**A positive control proves REACHABILITY or RECOGNITION, and these are not the same thing.**

A control that plants **the target strings themselves** and confirms they fire proves the recogniser
can recognise the claim. A control that fires on **an unrelated common token** proves only that the
instrument could open and read the files. Both are called "the control fired, so the zero is a
measurement" — and only the first entitles that sentence.

---

## 3. The exposed conclusions, ranked. **Each routed to a non-author; none re-graded here.**

### 1. `V9` — prior-art completeness, still carrying **PASS**. *Highest exposure tonight.*
The ledger's own words: *"both discriminating fragments, `controls where a data-driven correction is
allowed to act` and `has been published repeatedly`, return **ZERO** hits, **with the positive
control `Closure` firing in 7 members**. **The control fired, so the zero is a measurement.**"*

`Closure` is a token unrelated to the prior-art claim. **Its firing proves the pass could decompress
and read 90 archive members. It does not prove the recogniser would fire on the claim in any form
other than those two exact literal strings.** What was measured is the absence of two literals; what
was concluded is the absence of a claim. If the sentence was **reworded** rather than removed, both
fragments miss and the control still fires — and that this happens here is not hypothetical: the V10
reopen's v1 instrument returned a **false zero** on a known case because *"the tie **is** lost"* and
*"the tie **was** lost"* share no 5-gram. **One inflected verb was enough.**
This rung has already flipped once on a measurement question — its own row records the previous
finding as *"wrong for five days"*.
**Route: a non-author of V9 and of the D227 entitlement pass. Ask only: does the struck prior-art
sentence survive in paraphrase anywhere in the 90 members, under a recogniser built from the
claim's meaning rather than two of its literal substrings?**

### 2. `V7` — known defects killed, still carrying **PASS**, and it is the least-instrumented PASS on the ladder.
Its whole ledger entry is *"**PASS** — three, not the two we knew | YES — two more stale generator
strings found later."* It rests on a **literal generator-string** search, it has **no grade document**
in the state table, it dates to 2026-08-10, and **it has already been amended twice by later
discoveries** — which is the signature of a recogniser whose vocabulary was smaller than its corpus.
Generator strings are exactly the class where a paraphrase or a regenerated template defeats a
literal.
**Route: a non-author, with a derived rather than listed stale set — the method the V10 reopen
proved (compute the class from the data; do not maintain a list of it).**

### 3. The rule-(2) shipping result, **"33 → 10"** (`dc9d9364`, D255) — exposed to being *read as* clearing what it excludes.
The measurement is sound and its author flagged the limit twice, in the row and in the commit. The
exposure is that a "33 → 10" headline travels and the exclusion does not: **`dist/` and
`demo-output/website/latex/` are outside its corpus, so the stale 40-page PDF carrying `rank 1 of 5`
and `P(rank 1) = 68%` is NOT covered by that result.** It also self-reported a **30% instrument
false-positive rate** on that tier.
**Route: the owner of `latex/` for the rebuild; and whoever next cites "33 → 10" must carry the
exclusion in the same sentence.**

### 4. The **67 tracked PDFs never rendered**, plus 18 gitignored ones — an open frame gap, not a finding.
D243 rendered one PDF and found live four-entry claims on its front page. Its own limit: *"Cannot
see: the other 67 tracked PDFs, which were not rendered."* Every one is invisible to `git grep -I`
by `.gitattributes`, and text-layer extraction is **one-sided** — `\sout{}` is strike-and-keep, so
only the *absence of every post-repair token* is decisive.
**Route: the holder of `scripts/check_pdf_surfaces.py`. This is a frame gap with a known method, not
a research question.**

### 5. `V13` — close-out, carrying **PASS** with four findings.
Not sweep-shaped in the same way, but its own ledger row records **two of its statements as false by
execution for nineteen hours**, which is the same failure mode one level up: a close-out asserts
completeness over a set nobody re-enumerated.
**Route: a non-author, to re-enumerate rather than re-read.**

### 6. My own `V10` closure `c2cd83bf` — **already reopened; listed for completeness, and one measurement volunteered.**
The reopen is correct and I am not revising the grade document to look better in hindsight. Two
things belong in this map. First, the **89 adjudicated hits rest on the same recogniser as the miss**,
so they are 89 hits of the kind it could see — its zeros were real but of the wrong quantity.
Second, **I tested my own instrument for the code-span class that produced tonight's false positive**
(a `~~` inside backticks read as markup): `ACTIVE_RESEARCH.md` carries **3** such occurrences.
Measured end to end, the live hit count is **17 under both models**, and the 100 bytes that differ
are a region my instrument blanked **correctly** — my quick code-span-aware alternative was the worse
model, not the better one. **So the class is real, it is present on a surface I cleared, and its
measured effect on my result was zero.** That is stated in both directions because a self-check that
only reports exoneration is not a check.
**Route: already with the reopen's author; no further action requested.**

### 7. `V12`'s grade — a `FAIL`, so not exposed in the false-clean direction; its **enumeration** is.
Its verdict is safe (§1). But clause (i) was *closed by enumeration* over **one file**, and D251
proves that same sentence had already travelled unstruck to two other surfaces. **A single-file
enumeration cannot close a cross-surface clause**, and the finding that proves it is already filed.
**Route: whoever re-runs V12 cross-surface, not the grade's author.**

### 8. The D245 costing — cleared nothing, so nothing rests on it; **but a ruling was built on it.**
Its ±10% error bar and its pivotal modelling choice (treating `rank 3 of 5`-style ordinals as *not*
identifying a board, which **moves 217 sites** if ruled the other way) are inputs to the D238 ruling.
**Route: the chief, as an input to that ruling, not as a defect.**

---

## 4. What this map is itself blind to

Stated because the whole document argues that an unstated frame is the defect.

* **It reads records, not surfaces.** It establishes what each sweep's *record says* it did. Where a
  record misdescribes its own instrument, this map inherits the error — and D244 measured exactly
  that: **15 of 28 grading records mention wrapping at all, and NOT ONE declares the property of its
  own sweep pattern.**
* **It cannot rank by how much falsehood is actually out there**, only by how much of the claim class
  each instrument could not have seen. A blind spot over a clean region costs nothing, and this map
  cannot tell those apart without the re-runs it routes.
* **Two of tonight's sweeps were run by this pass**, and its self-assessment of them is worth exactly
  what a self-assessment is worth, which is why every item above routes to a non-author.
* `dist/`, `demo-output/website/latex/`, `motorbike-video/` and `LAPTOP_SHOOT.md` were not opened.

**Compliance.** No solver runs, no scoring calls; ledger at 6, untouched. Nothing sent, posted,
registered, emailed or created. `deb91557` was not moved. `docket.json` was not written. No rung was
graded or re-graded. No file on a peer's hold list was edited — `sdk/tests/` was read, never written.
