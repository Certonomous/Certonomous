# Ladder V — rung V15, ROUND 4: is round 3's output clean?

**Owner: an agent that wrote none of the text below, has never written to the closure
line, and did not participate in rounds 1, 2 or 3, nor in any correction pass they
audited.** I produced none of the text audited here and made no edit to any file below.
**Scoring calls made by this rung: ZERO; the ledger stands at 6.** Every check is static,
arithmetic, or a re-read of an artifact on disk. **Nothing was sent.** Read-only except
this file.

Round 1 (`LADDER_V_V15_LADDER_TEXT_CLAIMS.md`, `6afe15e3`) found ten failures. Round 2
(`LADDER_V_V15_ROUND2.md`, `c1ebfb4f`) found six. Round 3 then fixed those six and wrote
more text doing so. The termination rule (`LADDER_V_TRIPLE_VERIFICATION.md`
§"WHEN THE LADDER IS GREEN", `5bffb476`) says the ladder is green at a **fixed point**: a
fix round that introduces **no new failures in its own output — not "few", not "only
cosmetic ones". Zero.** This document is the measurement of that.

---

## 0. FRAME, STATED BEFORE ANY COUNT

### 0.1 Clock audit, run before any date is used

```
$ date -u
Tue Aug 11 01:02:28 UTC 2026      (frame frozen; HEAD pinned)
Tue Aug 11 01:23:30 UTC 2026      (frame re-read at close; it had moved — see §0.2)
```

**Today is 2026-08-11.** This document is legitimately dated 2026-08-11.

### 0.2 The frame is timestamped because the corpus moved under me — twice, in one hour

**Frame frozen at HEAD = `d7d51974` (2026-08-11 00:35:08 UTC), read at 01:02:28 UTC.**
**Every count, verdict and absence claim below is measured at `d7d51974` unless the row
says otherwise.**

The frame moved during execution and I caught it doing so. At 01:15 a routine
`git show HEAD:` returned a `.tex` that did not match what I had read minutes earlier;
the LaTeX agent had committed at 01:07:15 and 01:09:25. **Every `.tex` measurement in this
report was re-taken against `d7d51974` explicitly after that discovery.** By the close read
at 01:23:30, **eleven** commits had landed beyond my frame:

| commit | UTC | what it does to this report's findings |
|---|---|---|
| `5fa933ee` `e2fb6883` `45b3be0f` `ae6254cf` | 01:07–01:10 | close the `.tex`'s withdrawn-rule and bare-figure sites — surface (4) of round 3's six |
| `ce0b14be` `1b840196` `1c68466d` `9e6fc374` | 01:18–01:21 | unrelated (F6b pre-registration, cold-start test, L-58, checklist) |
| `b90a3ce4` | 01:19:09 | closes `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md` — surface (1) |
| `d160a562` | 01:19:56 | closes `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1184` — surface (3) |
| `64f052c9` | 01:20:53 | closes the approved proposal JSON by supersession note — surface (6) |

**This frame will move again before this document is read.** Finding **R2** below is about
a record that was stale at my frame; by 01:23 it is staler, for the good reason that the
surfaces it lists are being closed. The finding is about the record, not the surfaces.

### 0.3 Definitions

- **"round-3 text"** = lines added or modified, in `249b611c..d7d51974`, by a commit that
  touches the round-5 submission package, one of the 16 claim-bearing surfaces, a closure
  artifact, or a rule this ladder enforces. Derived from `git log --name-only` /
  `git show`, never from a pass's own summary. **Commit bodies are in scope** — round 1
  audited the chief's commit body at `2ef8ae3b`, so the precedent is set.
- **"claim"** = a sentence asserting a quantity, a date, a count, a rank, or a compliance
  fact. Prose that only reasons is out of scope.
- **"FAIL"** = I can demonstrate it by running something or displaying a byte. Where I
  could only argue: OBSERVATION.
- **"surface"** = a file, not a document family.

### 0.4 Reach, proved before any absence is reported

All text sweeps use **`/bin/grep` directly**, never the ignore-honouring wrapper, or
`git grep` at an explicit revision. Historical states are read with `git show <rev>:<path>`,
never the working copy. JSON is parsed with `json.load` and walked structurally, not
grepped.

**The line-bounded-grep trap named in `f2e16a47` is honoured, not merely cited.** Both
sweeps below on which an absence claim rests use a **character-offset, whitespace-collapsed,
tag-stripped, accent-folded** instrument that cannot produce a false absence on wrapped or
tag-split text. Both carry a **positive control planted in a scratch buffer outside the
repository** (I am read-only; nothing was seeded into the corpus), and both carry a
**negative control** so a false-positive instrument would also be caught:

| sweep | positive control | result |
|---|---|---|
| withdrawn-rule surface derivation (§3.2) | restriction + figure, wrapped over 5 lines and split by `<b>`/`<span>` tags | **FIRED** |
| " (negative) | figure with interval, no restriction word | **silent — correct** |
| struck prior-art sentence absence (§3, R6 row) | the struck sentence planted, wrapped over 5 lines, split by `<b>`/`<i>` | **both discriminating fragments FOUND**; the line-bounded literal returns **ZERO on the same buffer** |
| `comfortab` sweep (§3.5) | *"…lead of 0.00003 is a comfortable win over Reissmann"* in a scratch file | **FIRED** |

**A fragment shared by a defect and its fix is evidence of neither.** The absence sweep
therefore scores only the two **discriminating** fragments (`controls where a data-driven
correction is allowed to act`, `has been published repeatedly`) and reports the four
author-name fragments separately, because the corrected two-part split legitimately
contains them.

### 0.5 What this frame structurally cannot contain

It cannot see uncommitted text; it cannot see the eleven commits after 01:02:28 except as
enumerated in §0.2; it cannot adjudicate whether an artifact is *itself* right, only whether
a sentence matches it. It did not re-run the scorer, the bootstrap, `build_master_table.py`
or the bundle builder — where a row inherits a measurement rather than takes one, it says so.

---

## 1. THE TRUE COMMIT SET, AND THE CORRECTIONS TO THE DISPATCH

`git log --format='%H|%ci|%s' --name-only 249b611c..d7d51974` returns **18 commits.**
`249b611c` is round 2's own pinned frame; everything at or before it was round 2's subject,
not round 3's output.

### 1.1 IN SCOPE — round 3's output

| # | commit | UTC | author-role | what it wrote | dispatch |
|---|---|---|---|---|---|
| 1 | `656c09c9` | 00:11:36 | round 3 | `benchmarks.html`, `benchmarks.json`, `wall/wall.json`, `build_benchmarks.py`, `self_audit.py` — closes round 1's F7 / round 2's N2 | ✔ named |
| 2 | `63009dd3` | 00:14:28 | round 3 | `LADDER_V_PASS2` C9 — the F9 evidence correction | ✔ named |
| 3 | `39d22bab` | 00:15:10 | **chief** | `LESSONS.md` L-56 + a 29-line `PRODUCT_LIST` entry of the round-2 verdict | ✘ **MISSED** |
| 4 | `472f9f92` | 00:18:18 | round 3 | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` — the 51-line V6 currency block | ✔ named |
| 5 | `d9552d73` | 00:22:34 | round 3 | `closure_challenge_round5_qcr.json` — N1 | ✔ named |
| 6 | `171b1241` | 00:23:36 | round 3 | `LADDER_V_V6_V10_V14_CLOSURE.md` (new, 452 lines) | ✔ named |
| 7 | `37049247` | 00:24:50 | **chief** | `PRODUCT_LIST` — 26-line entry recording the V6/V10/V14 verdicts | ✘ **MISSED** |
| 8 | `07af6f02` | 00:27:19 | round 3 | `PRODUCT_LIST` — N3, the 73/44 correction | ✔ named |
| 9 | `2b251689` | 00:27:32 | round 3 | `dist/certonomous-demo.zip` rebuilt | ✔ named |
| 10 | `8ce7cedd` | 00:27:40 | round 3 | `PRODUCT_LIST` — N4, the re-pointed citation | ✔ named |
| 11 | `35c59035` | 00:29:12 | round 3 | `DESCRIPTION_DOCUMENT.md` §5 — N5, **the only outward edit this round** | ✔ named |
| 12 | `f2e16a47` | 00:30:53 | round 3 | `CASES_FAMILY_SUPERVISION_GUIDELINES.md` §9 — the absence-instrument rule | ✔ named |
| 13 | `4e719a6b` | 00:31:17 | round 3 | `PRODUCT_LIST` — N6, the `.tex` frame correction | ✔ named |
| 14 | `7cd558b1` | 00:31:20 | round 3 | `BUNDLE_REBUILD_2026-08-10.md` addendum — the absence re-verification | ✔ named |
| 15 | `afe1af99` | 00:32:11 | **chief** | `PRODUCT_LIST` +59/−1 — see **R1** | ✔ named |
| 16 | `935f0f52` | 00:33:04 | round 3 | `PRODUCT_LIST` — the provenance note — see **R1** | ✔ named |
| 17 | `d7d51974` | 00:35:08 | **chief** | `LESSONS.md` L-57, `CAPABILITY_STRATEGY.md`, `PRODUCT_LIST` | ✔ named |

### 1.2 BOUNDARY — round 2's own output, in range, not round 3's

| # | commit | UTC | note |
|---|---|---|---|
| 18 | `c1ebfb4f` | 00:13:57 | `LADDER_V_V15_ROUND2.md` (new, 549 lines) — **the round-2 report itself.** In range and unnamed by the dispatch. Excluded from the claims table as the *previous* round's output rather than round 3's, and because the termination rule exempts the ladder's own reports from *reopening* the ladder. Named here so the exclusion is a decision, not a gap. |

### 1.3 Corrections to the dispatch, in order of importance

1. **SIX of the dispatch's twenty-one commits are MISATTRIBUTED, and they are the largest
   block it names.** `dc13f1cc`, `5af41163`, `4381d634`, `a3a4ab3a`, `79f4529c` and
   `249b611c` are listed as "the V6/V10/V14 closure commits" in round 3's scope. **All six
   are at or before `249b611c`, which is round 2's own pinned frame, and all six were
   already audited by round 2** — they are rows **P29–P43** of `LADDER_V_V15_ROUND2.md`
   §2f, where round 2 itself flagged them as the block the *round-2* dispatch had missed.
   Auditing them again as round 3's output would have double-counted six commits' worth of
   PASSes into round 4's result and inflated the trend. **This is the first time a dispatch
   error has run in the direction of making the round look cleaner rather than shorter.**
2. **`39d22bab` and `37049247` are missing, and both are the chief's own `PRODUCT_LIST`
   entries.** Together they add 55 lines of quantitative claims to a claim-bearing surface —
   the round-2 verdict record and the V6/V10/V14 verdict record. **This is the third
   consecutive round in which the dispatch omitted the chief's own `PRODUCT_LIST` entry**:
   round 1 §1.2 items 2–4 (`c1187949`, `e59ae644`, `bbe0e4db`, `a4b9f70c`), round 2 item 3
   (`94733c2d`), round 4 here. L-56, written at `39d22bab` — one of the two commits missed —
   diagnoses the omission of *rule-creating* commits. **The recurring omission is not the
   rule commit; it is the chief's own changelog entry, and L-56 does not name that class.**
3. **`c1ebfb4f` is missing** — the boundary. Not a scope error (see §1.2), but the dispatch
   names neither the round-2 report nor `249b611c` as the range's lower bound, which is why
   the six misattributions in (1) were possible.
4. **Nothing the dispatch named within `249b611c..d7d51974` was misattributed by author or
   content.** All twelve in-range named commits verified by `--name-only` and body.
5. **"And anything since": eleven commits, §0.2.** Four of them close surfaces this report
   ranks as open at its frame. They are out of frame and are not credited to round 3.

**Net.** All 21 commits the dispatch names exist. **12 are correctly in round 3's output;
6 fall outside the audited range and were round 2's subject; 3 are the bundle/absence
commits, correctly named.** Against that, **2 in-range commits were missed** (`39d22bab`,
`37049247`, both the chief's own) and **1 boundary commit was unnamed** (`c1ebfb4f`).

---

## 2. THE CLAIMS TABLE OVER ROUND 3's TEXT

Every quantitative sentence → the named artifact → verdict.
**Result: 7 FAIL, 3 OBSERVATION, 38 PASS.**

### 2a. N1 — the withdrawn-rule replacement in the primary artifact (`d9552d73`)

| # | claim | artifact / method | verdict |
|---|---|---|---|
| **Q1** | the JSON still parses after the edit | `json.load` on `demo-output/website/closure_challenge_round5_qcr.json` | **PASS** |
| **Q2** | `INTERNAL ONLY` now occurs **zero** times in it | raw byte count: 0 case-sensitive, 0 case-insensitive | **PASS** |
| **Q3** | *"the dated 2026-08-07 block above is untouched"* | **structural** diff of the parsed object between `d9552d73^` and `d9552d73`, walking every key: **exactly one value differs**, `/leaderboard_comparison_dated_2026_08_07/rank_companion_2026_08_10`. `source`, `caveat`, `overall`, `our_rank_overall`, `per_case_published_at_deb91557`, `best_on_board_count`, `qcr_vs_rank2_duct_consistency` all byte-identical | **PASS — and the structural walk is the right instrument, because a value nested under a key I did not guess still reports** |
| **Q4** | the replacement is *"the wording already committed at `1db6fc3c`… transposed into this file's ASCII/percent house style"* | compared to the three chief-owned records: SUPERSEDED marker, WITHDRAWN, TRAVELS, the interval prohibition and the not-decided-pairs prohibition all present and semantically identical; ASCII transposition consistent throughout the string | **PASS on content** |
| **Q5** | the replacement's **placement** | the removed sentence stood between *"…52 to 81 percent."* and *"Source: campaign/…"*. The replacement is appended **after** the Source citation, so the string now reads *"Source: campaign/PROBABILITY_OF_RANK_2026-08-10.md - SUPERSEDED 2026-08-10 - the internal-only restriction was WITHDRAWN…"* | **OBSERVATION — R8.** See §4 |
| **Q6** | *"both occurrences of the figure sit in the same sentence as the interval"* | 2 occurrences of `68 percent`; the first is followed in the same sentence by *"cannot pin it tighter than 2-100 percent at 95 percent"*; the second is inside the supersession clause which states the interval | **PASS** |
| **Q7** | *"No generator emits this file"* | `closure_round5_qcr_forward.py` writes `*_forward.json`; no tracked generator writes `closure_challenge_round5_qcr.json` | **PASS** |
| **Q8** | *"`self_audit.check_closure_entry_of_record` still returns PASS"* | not re-executed by this rung — running the audit script is not a read-only act on a live wall. **Inherited** | **OBSERVATION — stated, not verified** |

### 2b. N1's derivation — 14 surfaces, 6 asserting (`afe1af99`'s `PRODUCT_LIST` entry)

| # | claim | verification | verdict |
|---|---|---|---|
| **Q9** | *"**Fourteen surfaces** carry a statement of the rule"* | Independently re-derived (§3.2) with my own structural instrument over 20,504 tracked files + 90 zip members: **20 non-log candidate surfaces at a 400-character window, 25 at 1,200.** Neither is 14. At the round's *own stated* 400-character window my instrument **misses the surface the round ranks first** | **FAIL — R3.** See §4 |
| **Q10** | *"**Eight** are correctly superseded, struck or quoted"* | the eight named are real and correctly dispositioned — but my sweep finds the rule statement also in `LADDER_V_PASS2`, `LADDER_V_PASS3_COLD`, `LADDER_V_PASS1`, `LADDER_V_V15_LADDER_TEXT_CLAIMS` and `LADDER_V_V15_ROUND2`, none of which are in the 14, while two other ladder documents are | **FAIL — R3.** The inclusion rule for ladder reports is unstated and inconsistent |
| **Q11** | *"**Six** still assert it in the present tense"*, enumerated (1)–(6) | At the frame `d7d51974`, **four** assert. Items **(2)** `PRODUCT_LIST:60–61` and **(5)** `CAPABILITY_STRATEGY:83` were both superseded by **`d7d51974`, the same author's next commit, 2 m 57 s later, and (2) is in the same file as the list.** Read at `d7d51974`: (2) now carries `~~The number is INTERNAL…~~ **[SUPERSEDED 2026-08-10…]**`; (5) now carries a ten-line chief note | **FAIL — R2.** See §4 |
| **Q12** | item (1) `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md:108–110` still asserts | read at frame: *"**The figure is INTERNAL:** internal surfaces carry it, public surfaces in `dist/` carry the qualitative clause only"* at 108–110 | **PASS — exact, line numbers correct** |
| **Q13** | item (3) `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1184–1191` asserts, *"while line 575 of the same file states the withdrawal correctly, so the draft contradicts itself"* | read at frame: 1184–1191 is the *"Wording note, deliberate"* keeping the figure out *"because it is internal by its own gate"*; line 575 states the withdrawal | **PASS — both line ranges exact and the contradiction is real** |
| **Q14** | item (4) *"`report.tex:243` and **`:287`**"* state the withdrawn rule | at frame, `:243` = *"400,000 case-level bootstrap resamples; **internal figure** — see the caution below"* ✓. **`:287` is not the caution** — it is `\textbf{P(rank 1) = 68\%};`, a **figure** site already counted among the nine bare ones. The caution (*"That figure is an **internal one** — … not to be quoted outside it"*) is at **`:289`** | **FAIL — R7.** See §4 |
| **Q15** | item (6) the approved proposal JSON, *"four fields (`objective`, `rationale`, `sequencing`, `gate`)"*, and *"a rewrite under an unchanged `decided_at` would forge the record"* | parsed: all four fields carry it (`objective` *"kept strictly internal and never attached to any submission"*; `rationale` *"filed explicitly as internal only"*; `sequencing` *"INTERNAL ONLY: …"*; `gate` *"The number is internal and marked so; publishing it externally … is outside this item"*). `decided_at` = `2026-08-10T00:00:00Z`, `status` approved | **PASS — and the refusal to rewrite is the right call** |
| **Q16** | *"**Five of the six** were found by a search that did not know how the sentence is spelled"* (dispatch reading: five were invisible to earlier sweeps because they do not use the documents' words) | Tested at `4e719a6b`, the revision immediately before the claim was written. A **case-insensitive** grep for the documents' own phrasings returns: `never appears in an external claim` → **`docs/PRODUCT_LIST.md`** (item 2); `internal only` → **`docs/CAPABILITY_STRATEGY.md`** (item 5) **and the proposal JSON** (item 6). **Three of the six were findable by the documents' own words.** Only (1), (3) and (4) were genuinely invisible to phrase search | **FAIL — R4.** See §4 |

### 2c. N2 — the four external surfaces (`656c09c9`), and its verification (`afe1af99`)

| # | claim | verification at frame `d7d51974` | verdict |
|---|---|---|---|
| **Q17** | all four now carry `P(rank 1) = 68%` **and** `2–100% at 95%` | `benchmarks.html` 4 figure / 2 interval; `benchmarks.json` 2 / 1; `wall/wall.json` 2 / 1; `build_benchmarks.py` 2 / 1 | **PASS** |
| **Q18** | *"the figure never appears without its interval on any of the four"* | every occurrence read **in context**, not counted: `benchmarks.html` has two blocks (a `<p>` at 68–70 and the KPI footnote at 88), each pairing figure and interval — **and the 68–70 block is wrapped across three lines, so a line-bounded check would have reported the interval missing.** The three others carry a single companion string in which figure and interval are 90 characters apart | **PASS — verified with an offset-based read for exactly the reason `f2e16a47` gives** |
| **Q19** | the not-decided pairs *"were already present and are unchanged"* | token `not statistically decided` present once on each of the four; Reissmann and Wu & Zhang named; Liu and Montoya stated as decided | **PASS** |
| **Q20** | *"the two JSONs were rewritten FROM the literal… `our_entry` in both files is byte-equal to `build_benchmarks._CLOSURE`"* | `benchmarks.json` and `wall/wall.json` `our_entry` strings are byte-identical to each other and to the generator's concatenated literal | **PASS — the fix is in the generator, not beside it** |
| **Q21** | the `self_audit` guard: *"fails the wall if `our_entry` says rank 1 without P(rank 1), without a 2-100% interval, or without the sweep token"*, with four positive controls | code read at `scripts/self_audit.py`: the guard is present, gated on `\brank 1\b`, checks all three, and the interval regex `2\s*[-–]\s*100\s*%` accepts both dash forms. The four controls are **inherited, not re-run** | **PASS on the code; the control run is inherited** |
| **Q22** | `afe1af99`: *"Round 2's zeros were correct at the revision it pinned"* | at `249b611c` all four surfaces carry `rank 1 of 5` and zero occurrences of the figure or interval | **PASS — round 2 is correctly exonerated rather than quietly overwritten** |
| **Q23** | `656c09c9`: **ONE NEW FAILURE THIS COMMIT CAUSES**, reported not absorbed — bundle drift on `benchmarks.html` | the commit body states it, names the second pre-existing drift (`head_engineer.py` at `1471b8f3`), refuses the rebuild with the ring-fence reason, and names the owner | **PASS — and this is the termination rule's intended behaviour: a fix round declaring the failure it created** |

### 2d. N3 — the date-count correction (`07af6f02`)

| # | claim | verification | verdict |
|---|---|---|---|
| **Q24** | *"`git grep -oI "2026-08-11"` at `8cc6bf70` returns **73 in 19 files**"* | measured: **73 occurrences, 19 files.** Exact | **PASS** |
| **Q25** | *"the per-file breakdown sums to 73 (22 + 11 + 8 + 8 + 4 + 3 + 3 + 2 + 2 + 1×10)"* | measured per-file **occurrence** counts (not line counts): 22 / 11 / 8 / 8 / 4 / 3 / 3 / 2 / 2 and ten singles. **Exact, and the distinction between occurrence-count and line-count is what makes it exact** | **PASS** |
| **Q26** | *"73 − 29 = 44 references"* and *"73 − 29 + 3 = 47, and 47 in 10 files is exactly what the corpus carries at `9477a2ed` … and holds unchanged through `4381d634`"* | measured: `9477a2ed` = **47 in 10**; `4381d634` = **47 in 10** | **PASS — both revisions exact** |
| **Q27** | the frame note: *"round 2 stated the reconciliation as '47 at HEAD' with HEAD = `249b611c`. At `249b611c` the corpus holds **51 in 14 files**; the four extra are the one-line round-5 notes that landed at 00:05–00:06… 51 − 4 = 47"* | measured: `249b611c` = **51 in 14**. The four named files each gained exactly one occurrence between `9477a2ed` and `249b611c` | **PASS — and correcting the *label* on a correct arithmetic is the most careful row in round 3's output** |
| **Q28** | *"9477a2ed's commit body carries the same two numbers and cannot be edited, so the correction is placed in the entry that repeats them"* | the body does carry 74/45; the correction is a dated bracketed note in `PRODUCT_LIST`, not a silent replacement | **PASS** |

### 2e. N4 — the re-pointed citation (`8ce7cedd`)

| # | claim | verification | verdict |
|---|---|---|---|
| **Q29** | `MANIFEST.json` has no changed-list; its keys are the thirteen listed; `AR_7` occurs 0 times | parsed: keys exactly as listed; `raw.count('AR_7')` = **0** | **PASS — key list exact** |
| **Q30** | the changed-list is `closure_challenge_round5_qcr_forward.json` `/what_ships`, `changed` = the three ducts, `unchanged` = the five non-duct cases, `AR_7_Ret_180` in neither | parsed: `changed` = `[AR_14_Ret_180, AR_1_Ret_360, AR_3_Ret_360]`, `unchanged` = the five. `AR_7` in neither | **PASS** |
| **Q31** | *"ls of `…round5/test/` giving exactly 8 CSVs, none `AR_7*`"* | 8 CSVs, none `AR_7*` | **PASS** |
| **Q32** | *"`/bin/grep -nIE "changed.list\|manifest's own"` over `git ls-files` finds it nowhere else… the other five hits are the two V15 reports and this file's own round-2 findings entry, all quoting it as the defect, plus one unrelated use"* | re-swept: no surviving assertion of the false citation outside quotations of it | **PASS** |
| **Q33** | *"the sentence still says 'two independent ways' because there still are two"* | both proofs re-run here independently (Q30, Q31) | **PASS — the claim was never in doubt and the fix is to the citation only, correctly** |

### 2f. N5 — the outward seed paragraph (`35c59035`) — the round's only outward edit

| # | claim | verification | verdict |
|---|---|---|---|
| **Q34** | *"the bootstrap loaded **0.0024**"*; `PROBABILITY_OF_RANK` §2's loaded overalls are 0.059047 / 0.054247 and *"0.056647191704213645 ± 0.0024 reproduces both to six decimals"* | 0.056647191704213645 + 0.0024 = **0.059047**; − 0.0024 = **0.054247**. `PROBABILITY_OF_RANK:189` and `:191` carry exactly those two | **PASS — exact** |
| **Q35** | *"0.002419 would give 0.059066 and 0.054228, which the table does not carry"* | computed: **0.059066 / 0.054228**; neither appears in the table | **PASS — the falsification is stated and it holds** |
| **Q36** | *"§8's own 0.002419 is CORRECT and is left alone — it traces to `closure_challenge_seed_sensitivity.json` `overall_equivalent_S_bound` = **0.002419121853891026** and to `closure_challenge_stability_physicality_audit.md` line 146"* | parsed: `/spreads/overall_equivalent_S_bound` = **0.002419121853891026**. Audit **line 146** = `| Overall-equivalent \`S_bound\` | **0.002419** |` | **PASS — both anchors exact, including the line number** |
| **Q37** | *"the fix names both numbers rather than replacing one with the other"* — is that **accurate**? | the committed sentence names 0.002419 as the bound and 0.0024 as what the bootstrap ran with, and states what the rounded value reproduces | **PASS on accuracy** |
| **Q38** | — is that **clear**? | The clause reads *"the truth-free seed bound of §8 (0.002419, loaded at **0.0024** — that rounded value is what the bootstrap was actually run with, and the overalls it produces are 0.056647 ± 0.0024 exactly), loaded adversely onto the three seed-dependent cases…"*. **"Loaded" now carries two different senses eleven words apart** — *loaded at* (a numeric value) and *loaded adversely onto* (a direction applied to cases) — and a three-line parenthetical separates the subject from its verb | **OBSERVATION — R9.** See §4. No new ambiguity of *fact*; a new ambiguity of *reading*, in the outward document |
| **Q39** | the secondary point — the row sits in a table headed "interval" and a one-seed scenario range is not an interval — *"Still open and NOT fixed here, because it is a presentation decision"* | the commit body states this, with the reason and the owner | **PASS — a round that knows what it must not fix** |

### 2g. N6 — the `.tex` frame correction (`4e719a6b`)

| # | claim | verification at frame | verdict |
|---|---|---|---|
| **Q40** | *"carries the figure at **12 sites**: 61, 78, 203, 237, 259-260, 265, 287, 648, 699, 717, 768, 786"* | measured at `d7d51974`: `68\%` at **61, 78, 203, 237, 260, 265, 287, 648, 699, 717, 768, 786** — **12, all exact** (the `259-260` span carries the literal on 260) | **PASS** |
| **Q41** | *"an interval at exactly one place, 259–260"* | line 260: *"a double bootstrap gives 26--94\% at the 68\% level and **2--100\% at 95\%**"* | **PASS** |
| **Q42** | *"Nine sites carry the figure with no interval in local context — 61, 78, 203, 237, 287, 699, 717, 768, 786"* | nine named; 260 is the interval site and 265 *"is adjacent and inherits it"*. **9 + 1 + 1 = 11 of 12. Line 648 is enumerated in the twelve and appears in neither category** | **FAIL (minor) — R7.** One site of twelve is unaccounted for in a list whose purpose is to route an owner |
| **Q43** | *"two sites additionally state the rule the chief WITHDREW: **243** … and **287**"* | 243 exact; **287 is a figure site, not the caution — the caution is 289** | **FAIL — R7** |
| **Q44** | *"this ladder recorded the per-claim reading in its own words at `LADDER_V_PASS2_2026-08-11.md:338`"* | line 338 reads *"its owner should confirm every one of the twelve now carries the interval, which is the new requirement"* | **PASS — verbatim, correct line** |
| **Q45** | *"the entry now states which reading its result used instead of asserting a compliance fact without one"* | the committed entry declares its true frame: **per-SURFACE, over tracked `.md`/`.html`/`.py`** | **PASS — this is the correct repair of round 2's N6 and it does not repeat it** |
| **Q46** | *"the outward `DESCRIPTION_DOCUMENT.md` is compliant at all six of its sites — four flagged by the window are false positives"* | re-checked: every figure occurrence in the outward document sits within the interval table's reach or immediately above the *"somewhere between a coin flip and near-certain"* sentence | **PASS** |
| **Q47** | *"The `.tex` is not this pass's file to edit and is not edited"* | no commit in range touches the `.tex`. **The routing worked: the `.tex`'s owner closed it at `5fa933ee`/`e2fb6883`/`45b3be0f`/`ae6254cf`, 01:07–01:10 — out of frame** | **PASS — and the record-based routing is vindicated within 36 minutes** |

### 2h. F9's evidence correction (`63009dd3`)

| # | claim | verification | verdict |
|---|---|---|---|
| **Q48** | *"Four are the prohibition"* — `round4_duct.json:88`, `CLOSURE_CHALLENGE_STATUS.md:394`, `:639`, `report.tex:864`; *"a fifth, `LADDER_V_TRIPLE_VERIFICATION.md:46`, restates the banned-list rule"*; *"The remaining ten are ordinary uses"* — total 15 | Re-swept at `63009dd3`. All fifteen named hits verified in place **except one line number (Q50)** — and **`demo-output/website/ACTIVE_RESEARCH.md:611`** reads *"a nominal lead that must **not be reported as a comfortable win**"*: **a fifth prohibition, in the closure line, on a claim-bearing surface, absent from the enumeration** | **FAIL — R5.** The set is 16, not 15 |
| **Q49** | *"76 hit lines tree-wide, 59 under `demo-output/website`, 15 in the closure line"*, frame declared as *"the whole working tree"* | measured at the nearest committed revision `63009dd3`: **77 tree-wide, 63 under `demo-output/website`**. The declared frame is a **superset** of tracked files, so it cannot return **fewer** hits than tracked-only | **FAIL — R5** |
| **Q50** | *"`CLOSURE_RANK1_CAMPAIGN.md:341` calls an assumption 'the comfortable reading'"* | at `63009dd3`, **line 341 is blank**; the sentence is at **line 374**. **Round 2's observation O3 had already reported the +33 shift caused by `5af41163`'s banner and given the corrected number** | **FAIL — R5.** A stale citation the previous round had already handed over corrected |
| **Q51** | the verdict itself: *"no surface describes the AR_14 lead, or any lead, as a comfortable **win**"*; C9 stays PASS with the false clause struck rather than deleted | the narrowed claim holds across all 16 hits, including `ACTIVE_RESEARCH:611`, which is a prohibition and not a win claim. The strike-through treatment matches C6's | **PASS — the verdict is right, the disposition is right, and the round correctly refused to change a PASS to hide a bad sentence** |
| **Q52** | *"Positive control, which the original sweep did not carry"* — seeded, returned, deleted, `git status` clean | control text reproduced here and fires; `git status` at my frame shows only `sdk/.filming-keepalive` | **PASS** |
| **Q53** | commit body arithmetic: *"15 in the closure line… FOUR are the prohibition… Ten are ordinary uses"* | 4 + 10 = **14 ≠ 15**. The in-file note reconciles it with the fifth (`TRIPLE_VERIFICATION:46`); the commit body drops it | **OBSERVATION — the body under-describes its own file, harmlessly** |

### 2i. The absence re-verification (`f2e16a47`, `7cd558b1`) and the bundle (`2b251689`)

| # | claim | verification | verdict |
|---|---|---|---|
| **Q54** | *"the line-bounded `grep` used in all three prior passes returned **ZERO** on a planted file that demonstrably contains the sentence"* | **Independently reproduced.** I planted the struck sentence into a scratch buffer, wrapped over 5 lines and split by `<b>`/`<i>`: literal substring search returns **zero**; my normalised search returns **both discriminating fragments** | **PASS — the finding is real and I can make it happen on demand** |
| **Q55** | *"the core defect is genuinely ABSENT"* from the shipped bundle | **Independently re-verified** with the wrap-proof instrument, positive control firing: **0 hits** for `controls where a data-driven correction is allowed to act` and `has been published repeatedly` across **all 82 text members** of the committed zip at the frame | **PASS — V10's absence claim stands on evidence that cannot fake a zero** |
| **Q56** | *"the four author fragments that DO appear are the corrected two-part split"* | `Steiner, Dwight and Viré` and `Wu, Wang, Xiao and Ling` present in the bundled `closure.html`; the shipped paragraph credits the control mechanism separately and says Ling & Templeton *"control nothing"* | **PASS** |
| **Q57** | *"**A fragment shared by the defect and its fix is evidence of neither**"* — recorded as a flaw in the round's own fragment design | the rule is correct, is now `CASES_FAMILY_SUPERVISION_GUIDELINES.md` §9 item 4, and I adopted it in §0.4 of this document | **PASS — the strongest single piece of method in round 3's output** |
| **Q58** | *"**Bundle-wide sweep: 78 text files, 23 binary skipped**"* | 78 + 23 = **101 files.** The committed zip at the frame holds **90 non-directory members** (103 entries including 13 directories). Splits measured three ways: **82 text / 8 binary** by null-byte test; **69 / 21** by extension. **No classification yields 78/23** | **FAIL — R6.** See §4 |
| **Q59** | `2b251689`: *"the shipped bundle absorbs the two files it was behind — `benchmarks.html`… and `head_engineer.py`"* | sha256 of the bundled members vs the tree at the frame: `certonomous-demo/site/benchmarks.html` **bb97cb306901 = bb97cb306901**; `certonomous-demo/sdk/chief_engineer/head_engineer.py` **544b9737023e = 544b9737023e**. The bundled `benchmarks.html` carries `P(rank 1)` **and** the interval | **PASS — byte-identical, verified by opening the committed archive rather than by inference** |
| **Q60** | `2b251689`: *"drift check PASS at 56 of 56 byte-for-byte"*, *"served and read over HTTP"* | not re-run: rebuilding or serving is not a read-only act. **Inherited.** The two members the claim turns on are verified above | **OBSERVATION — inherited, and the row says so** |
| **Q61** | `2b251689`: the bundled `closure.html` still carries 0.0654 / 0.0676 | true at the frame — and correctly so: the page's history section is round-scoped, it also carries 0.0566 and the sweep token | **PASS — no stale-claim finding here** |

### 2j. V6 (`472f9f92`) — every anchor re-derived by this rung, not inherited

| # | claim | verification at frame | verdict |
|---|---|---|---|
| **Q62** | ground-truth reads at `apply_closure_ph_gate.py:128` and `:228`, both inside `_PH_TRAIN` loops (126, 225) | 126 = `for case in gate._PH_TRAIN:  # 21 cases, train only`; 128 = `_load_ground_truth_U`. 225 = `for c in ph._PH_TRAIN:`; 228 = `_load_ground_truth_U` | **PASS — exact** |
| **Q63** | test loop at `:178`, `_load_rans_fields` at `:179` annotated `# no U_LES read` | verbatim at both lines | **PASS** |
| **Q64** | three executable assertions at `closure_baseline_error_gate.py:84–86` | three `assert` statements on train/val/test disjointness and the 21/4 counts | **PASS** |
| **Q65** | *"4.4's four call sites counted at 218-219 and 301-302"* | `score(floor_predictions)` / `evaluate_by_case(floor_predictions)` at 218–219; `score(predictions)` / `evaluate_by_case(predictions)` at 301–302 | **PASS — four, exact** |
| **Q66** | 4.6's discharge at `MANIFEST.json:37` and `README.md:52–54` | MANIFEST line 37 = `eval_package_version_string_note`, stating 0.2.1 vs 0.3.1 and *"Cite the commit hash, not the version string"*; README 52–54 the same in prose | **PASS — both line anchors exact** |
| **Q67** | all eight round-5 CSVs are 1000×3, and `AR_1_Ret_360.csv` hashes to `bb8d61fb…` | parsed all eight: **1000 rows × 3 columns each**; `AR_1_Ret_360.csv` sha256 = **bb8d61fbbf…** | **PASS — matches the value Pass 1 traced end-to-end in V4** |
| **Q68** | `Ccr1 = 0.3` compiled as the default at `kOmegaSSTQCR.C:91–99`; the QCR term is in-PDE at `:60` | 60 = `-Ccr1_*symm((O & taul) - (taul & O))`; 91–99 = `getOrAddToDict("Ccr1", this->coeffDict_, 0.3)` | **PASS — both exact** |
| **Q69** | the untrained-path compliance line's positive control: 0 `*_LES*` in the three test-duct arms, **3 each in both `AR_7_Ret_180` arms** | run-tree counts not re-run by this rung (the run tree is outside the repository). **Inherited** — but the design is right: the control is what makes the three zeros a measurement | **OBSERVATION — inherited, and it is the correct instrument** |
| **Q70** | *"Nothing in §4.1–§4.9 is rewritten or deleted"*; two findings marked MOOT with reasons; 4.9 left standing as the summary of that audit | the diff is **+51 / −0**, appended as a block above §4 | **PASS — additive, verified by the diff's own shape** |

### 2k. The chief's own commits (`39d22bab`, `37049247`, `afe1af99`, `935f0f52`, `d7d51974`)

| # | claim | verification | verdict |
|---|---|---|---|
| **Q71** | L-56 (`39d22bab`): the dispatch omitted the rule-creating commit in **both** rounds 1 and 2 | round 1 §1.2.1 and round 2 §1.3.1 both record it; both instances verified against the two dispatches | **PASS — accurate, and volunteering it is the right instinct** |
| **Q72** | `39d22bab` `PRODUCT_LIST`: *"Round 1 found ten failures, round 2 finds six, none blocking, and only one touches the outward package"* | round 2's §5 table: N1–N6, N5 the only outward one | **PASS** |
| **Q73** | `37049247`: *"V10 FAIL — one surface… `dist/certonomous-demo.zip` is two files behind"* and *"My round is not a fixed point — it introduced one new failure, stated first not last"* | `656c09c9`'s own body declares it; `2b251689` then closes it | **PASS — a fix round reporting the failure it created, at the top** |
| **Q74** | `37049247`: *"A concurrent audit rung graded this pass's first six commits while it worked: **every row passed**"* | I cannot identify the rung or its record within the frame; no report in range grades six round-3 commits | **OBSERVATION — unverifiable within this frame; stated without a named artifact, in a claims-table culture that names artifacts** |
| **Q75** | `935f0f52`: *"`afe1af99`… Its diff is 59 insertions to `docs/PRODUCT_LIST.md`, and **all 59** are round 3's N1-derivation and N2-verification paragraphs"* | hunk-by-hunk: `@@ -2130,0 +2131,27 @@` **+27**; `@@ -2133 +2160,7 @@` **+7 −1**; `@@ -2171,0 +2205,25 @@` **+25**. Total +59 −1 ✓. **But the third hunk (+25) is the section headed `### 2026-08-11 — the three prior zeros were UNSOUND, and the sentence is genuinely absent anyway` — which is exactly what `afe1af99`'s commit message describes.** Round 3's swept-up work is **34 of 59**, not 59 | **FAIL — R1.** See §4 |
| **Q76** | `d7d51974` L-57: *"the diff contained **59 lines** of a concurrent agent's uncommitted work in that same file"* and *"**the commit's message does not describe its own diff**"* | same measurement: 34 of 59. The message describes 25 of its 59 added lines — under half, but not none | **FAIL — R1** |
| **Q77** | L-57's rule: *"a pathspec commit answers 'which files am I committing?' and says nothing about 'who else wrote in them'… Reading your own diff before committing is the check; the pathspec is only the scope"* | correct as stated, and the corollary about high-traffic files is exactly right | **PASS — the lesson is sound; only its measurement of the incident is wrong** |
| **Q78** | `d7d51974` `CAPABILITY_STRATEGY:83`: *"a rung's derivation found **six** surfaces still asserting the old rule and traced them here"* | past tense about the derivation, so defensible in isolation — **but the same commit closes two of the six and the entry listing them is not updated (R2)** | **OBSERVATION, rolled into R2** |
| **Q79** | `d7d51974` `PRODUCT_LIST:60–61`: the strike-through + `[SUPERSEDED 2026-08-10: …]` block, ending *"— and no surface, internal or outward, may print 'rank 1' without it"* | the replacement carries the interval `(2-100% at 95%)` and the not-decided-pairs requirement, and **broadens** the old internal-only clause into a universal obligation. Accurate against the V8 amendment | **PASS — struck rather than deleted, dated, and stronger than what it replaced** |

### 2l. Banned-list enforcement over round 3's text

| # | rule | sweep (all with `/bin/grep` or offset-based instruments; controls in §0.4) | verdict |
|---|---|---|---|
| **Q80** | **no novelty claim on gated correction** | round 3 wrote no novelty claim; the outward document's two `novel` occurrences are unchanged and are both prohibitions | **PASS** |
| **Q81** | **no "comfortable" margin claim** | 16 `comfortab` sites in the closure line at the frame; five are prohibitions (including `ACTIVE_RESEARCH:611`), the rest are training-regime, concessions, a refusal, and a prior-art verdict. **No surface claims a comfortable AR_14 lead or a comfortable win.** `PROBABILITY_OF_RANK:151` remains pre-ladder (`b2aa6887`) and round 3 did not touch it | **PASS on the banned item** (the *enumeration* defect is R5, not a banned-list breach) |
| **Q82** | **no best-on-board count leaning on organiser-baseline rows without saying so** | all four external surfaces carry *"four of the eight test cases — but two of those four (`alpha_05_4071_4048`, `alpha_05_4071_2024`) are the organisers' own unmodified RANS field"* **in the same sentence**; `656c09c9` did not weaken it and `self_audit` fails the wall if it drifts | **PASS** |
| **Q83** | **no official-rank language** | every occurrence in round 3's new text is a disclaimer (*"a local scoring, not an official placement"*) | **PASS** |
| **Q84** | **leakage disclosure in the lab's own words** | §3.3b untouched by round 3; the `R5_RULE_FREEZE` quotation, the admission-before-mitigation order, and *"No mitigation below cancels that sentence"* all intact. `472f9f92` re-quotes the freeze **at the frozen commit `0bade54a` with `git show`**, not from the mutable file | **PASS** |
| **Q85** | **every rank claim carries the figure WITH its interval and the not-decided pairs** | round 3 wrote rank-bearing text on exactly four surfaces (`656c09c9`) and each carries figure + interval + both pairs, verified in context (Q17–Q19). Every other new note routes to `CLOSURE_CHALLENGE_STATUS` §0f rather than restating a claim. **No bare figure was written this round** | **PASS — the strictest banned-list item is clean on new text** |
| **Q86** | **date discipline** (round 1's F2 class) | every round-3 note is dated `2026-08-11` and every round-3 commit is on `2026-08-11`. **F2 did not recur** | **PASS** |

---

## 3. THE FIVE DIRECTED CHECKS, ANSWERED DIRECTLY

**3.1 — The withdrawn-rule replacement in `closure_challenge_round5_qcr.json`.**
Accurate (Q4), the JSON parses (Q1), `INTERNAL ONLY` is gone (Q2), and the dated 2026-08-07
block is untouched — proved by a **structural walk of the parsed object**, which found
exactly one differing value out of the whole file (Q3). One reservation, **R8**: the
supersession was appended *after* the `Source:` citation rather than placed where the
restriction stood, so the string now reads *"Source: `…PROBABILITY_OF_RANK…` - SUPERSEDED
2026-08-10 - …"*. On first reading the marker attaches to the source document. The clause
that follows disambiguates it, and the three chief-owned records do it the other way round.

**3.2 — "14 surfaces, 6 still asserting", re-derived independently.**
Method of my own choosing, deliberately not a phrase search: a **character-offset**
co-occurrence of a restriction predicate (`internal[- ]*only|\binternal\b|not to be
quoted|never appears in an external|withheld|confidential`) with a figure referent
(`P(rank 1)|rank-1 probab|68\s*(%|\\%|percent)|0.67x|posterior over`) inside a sliding
window, over text that has been **tag-stripped and whitespace-collapsed first** so that a
statement split across lines or by markup still reports. Positive and negative controls in
§0.4. Corpus: **20,504 tracked files** (1,464 binary skipped) **plus all 90 members of
`dist/certonomous-demo.zip`, opened rather than inferred.**

**I do not get 14.** At the round's own stated **400-character** window I get **20**
non-log candidate surfaces — **and I miss `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md`, the
surface the round ranks first**, because its restriction sits ~500 normalised characters
from the nearest figure referent. At **1,200 characters** I get **25**. The zip contributes
**zero** — the shipped bundle carries no restriction-near-figure statement, which is a real
and reassuring result.

Two structural problems follow. First, **the count is a function of an undeclared window
parameter**, and at the declared parameter it does not even contain its own top-ranked
item. Second, **the inclusion rule for ladder reports is unstated and inconsistent**: the 14
counts `LADDER_V_TRIPLE_VERIFICATION` and `LADDER_V_V14_SURFACE_DISCOVERY` in, while my
sweep shows `LADDER_V_PASS1`, `LADDER_V_PASS2`, `LADDER_V_PASS3_COLD`,
`LADDER_V_V15_LADDER_TEXT_CLAIMS` and `LADDER_V_V15_ROUND2` also carry the statement and
are out. That is finding **R3**. The **six**, separately, is finding **R2**.

**Testing "five of the six do not use the documents' words."** Measured at `4e719a6b`, the
revision immediately before the claim was written. A **case-insensitive** grep for the
documents' own phrasings returns item **(2)** on `never appears in an external claim`, and
items **(5)** and **(6)** on `internal only`. **Three of the six were findable by the
documents' own spelling.** Only (1), (3) and (4) were genuinely invisible to phrase search.
The stated diagnosis — *"a rule withdrawn at its statement was never swept at its origin"* —
is established for those three. For (2), (5) and (6) the correct diagnosis is different and
less flattering: **the earlier sweeps' frames never included `PRODUCT_LIST`'s live standing
item, `CAPABILITY_STRATEGY`, or the proposals directory at all.** That is finding **R4**.

**3.3 — The corrected counts (73/44) and the re-pointed citation.**
Both **verified from primary artifacts and both exact.** 73 occurrences in 19 files at
`8cc6bf70`; the per-file breakdown `22+11+8+8+4+3+3+2+2+1×10` reproduces to the unit;
73 − 29 = 44; the reconciliation 73 − 29 + 3 = 47 holds at `9477a2ed` and at `4381d634`;
and the frame note re-labelling round 2's "47 at HEAD" is itself correct (51 in 14 at
`249b611c`, minus the four late round-5 notes). The re-pointed citation is correct in both
directions: `MANIFEST.json` genuinely has no changed-list and contains `AR_7` zero times;
`/what_ships` genuinely does. **This is the cleanest block in round 3's output.**

**3.4 — The outward seed correction naming two numbers.**
**Accurate** — every element verified (Q34–Q36), including that 0.002419 would produce
overalls the internal table does not carry, which is the falsification that makes the claim
knowledge rather than assertion. **Clear enough not to mislead, but less clear than what it
replaced**: it re-uses the verb *"loaded"* in two senses within one clause and inserts a
three-line parenthetical between subject and verb. It does **not** create a new ambiguity of
fact — the bound is unambiguously 0.002419 and the bootstrap input unambiguously 0.0024.
Recorded as **R9**, an observation and not a failure, and it is a presentation matter for
the document's owner, exactly as the round said of the table heading.

**3.5 — The chief's own commits.**
`d7d51974`'s substantive edits both verify: the `PRODUCT_LIST:60–61` supersession is
accurate and broadens the rule (Q79), and L-57's stated rule is correct and its supervisor
corollary is exactly right (Q77). **But L-57 and `935f0f52` both misstate the incident they
exist to record: 34 of `afe1af99`'s 59 added lines are round 3's; the other 25 are the
committing pass's own on-message section.** That is **R1**, and it is the same shape round 1
found in the chief's `2ef8ae3b` note (substance right, one measurement wrong) and round 2
found in `1db6fc3c` (claim right, artifact wrongly named). **Third round, third instance,
same author, same class: the record of a correction being less exact than the correction.**
`afe1af99` itself is audited as a writer: its N1/N2 content is round 3's and is separately
graded above; its own +25-line section (Q54–Q57) is sound; **its body under-describes its
diff, which is the defect `935f0f52` and L-57 exist to record, and they over-describe it.**

---

## 4. NEW FAILURES IN ROUND 3's OUTPUT, RANKED

None is blocking. **None is an accuracy defect in the outward package.** All seven are in
the record layer, and three of the seven are in text written specifically to record a defect
accurately.

### R1 — MAJOR. The provenance record of the sweep-up defect overstates it by 74%, in both commits written to record it

`935f0f52`: *"Its diff is 59 insertions… and **all 59** are round 3's N1-derivation and
N2-verification paragraphs."* `d7d51974` L-57: *"the diff contained **59 lines** of a
concurrent agent's uncommitted work in that same file"*, and *"**the commit's message does
not describe its own diff.**"*

Measured hunk by hunk on `afe1af99`:

| hunk | added | whose |
|---|---|---|
| `@@ -2130,0 +2131,27 @@` | +27 | round 3's N1 derivation |
| `@@ -2133 +2160,7 @@` | +7 −1 | round 3's N2 verification |
| `@@ -2171,0 +2205,25 @@` | **+25** | **the committing pass's own** `### 2026-08-11 — the three prior zeros were UNSOUND, and the sentence is genuinely absent anyway` |

**34 of 59, not 59.** The 25-line third hunk is precisely what `afe1af99`'s subject line
describes (*"The three prior zeros were unsound and the sentence is absent anyway"*), so the
commit's message describes **25 of its 59 added lines** — under half, but not none. The
accurate statement is *"does not describe all of its diff"*, and the accurate figure is 34.

**Why it ranks first:** these two commits exist for no purpose other than to state the
incident correctly, because history cannot be rewritten and the record is the only remedy
available. A provenance note that overstates the sweep-up by 74% mis-attributes 25 lines of
one agent's work to another — the exact error class it was written to prevent, inverted.
It is also now in `LESSONS.md` as a permanent lesson, where it will be cited by future
passes. **Owner: the chief (both commits).** *Reported, not fixed.*

### R2 — MAJOR. The list of surfaces still asserting the withdrawn rule was made stale by its own author's next commit, three minutes later, in the same file

`docs/PRODUCT_LIST.md` (`afe1af99`): *"**Six still assert it in the present tense**, all
outside this pass's ownership and therefore reported, not rewritten"*, enumerated (1)–(6).

At my frame `d7d51974` — **the very next commit, +2 m 57 s** — item **(2)**
`docs/PRODUCT_LIST.md:60–61` and item **(5)** `docs/CAPABILITY_STRATEGY.md:83` are both
superseded, by that commit. Item (2) is **in the same file as the list**, twelve hundred
lines above it. **Four assert; the record says six.**

The claim's own qualifier is what makes this a failure rather than a race: *"all outside
this pass's ownership and therefore reported, not rewritten"* is false of two of the six at
the frame, because the chief owned and rewrote them. And L-57, committed in the same breath,
is a lesson about **reading your own diff before committing a shared, high-traffic file** —
`d7d51974` touched `PRODUCT_LIST` and did not read the list its own edit invalidated.

By 01:23:30 all four remaining surfaces are closed out of frame (§0.2), so the record now
says six where zero assert. **This is round 1's F2 shape — a fix that does not travel —
inside a correction to a finding about rule statements that did not travel.**
*Reported, not fixed.*

### R3 — MAJOR. "Fourteen surfaces" is not reproducible, and at its own stated window the instrument misses its own top-ranked surface

`afe1af99`: *"the surface set was re-derived structurally — (restriction predicate) within
**400 characters** of (a referent for the figure)… **Fourteen surfaces** carry a statement
of the rule. **Eight** are correctly superseded, struck or quoted."*

Independently re-derived (§3.2) over 20,504 tracked files plus all 90 zip members, with
positive and negative controls: **20 non-log candidate surfaces at 400 characters, 25 at
1,200.** Neither is 14, and **at 400 characters the instrument does not return
`CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md` — item (1), the surface the round ranks first** —
because the restriction sits roughly 500 normalised characters from the nearest figure
referent. A derivation whose stated parameter excludes its own headline result is not
reproducible from its own description.

Second, **the frame's treatment of ladder reports is unstated and inconsistent**: the 14
includes `LADDER_V_TRIPLE_VERIFICATION` and `LADDER_V_V14_SURFACE_DISCOVERY` but excludes
`LADDER_V_PASS1/PASS2/PASS3_COLD` and both prior V15 reports, all of which carry the
statement. Under one rule the count is lower; under the other it is higher; no rule is given.

**This matters more than the arithmetic**: the whole point of replacing a phrase grep with a
structural derivation was to produce a number an auditor could reproduce. **The count that
was supposed to end the phrase-miss problem cannot be re-derived from its own stated method.**
*Reported, not fixed.*

### R4 — MODERATE. "Five of the six do not use the documents' words" is false for three of the six

`afe1af99`: *"**Five of the six** were found by a search that did not know how the sentence
is spelled."*

At `4e719a6b`, the revision immediately before this was written, a **case-insensitive**
grep for the documents' own phrasings returns:

| pattern | returns |
|---|---|
| `never appears in an external claim` | `docs/PRODUCT_LIST.md` — **item (2)** |
| `internal only` | `docs/CAPABILITY_STRATEGY.md` — **item (5)**; the proposal JSON — **item (6)** |

Only items (1), (3) and (4) were invisible to phrase search. For (2), (5) and (6) the
diagnosis *"a rule withdrawn at its statement was never swept at its origin"* does not apply;
the correct one is that **earlier sweeps never covered `PRODUCT_LIST`'s live standing item,
`CAPABILITY_STRATEGY`, or the proposals directory at all** — a frame defect, not a spelling
defect. The round diagnosed its own miss as cleverness-of-the-corpus when half of it was
narrowness-of-the-frame, and the corrective lesson written into `CAPABILITY_STRATEGY:83`
teaches the wrong half. *Reported, not fixed.*

### R5 — MODERATE. The F9 evidence correction is itself an incomplete enumeration, carries a stale line number the previous round had already corrected, and its frame counts do not reproduce

`63009dd3` exists **because C9's stated evidence was a false sweep claim.** Three defects in
its replacement:

1. **The enumeration is 16, not 15.** `demo-output/website/ACTIVE_RESEARCH.md:611` reads
   *"a nominal lead that must **not be reported as a comfortable win**"* — a **fifth**
   prohibition, in the closure line, on a claim-bearing surface, absent from the list of
   four prohibitions + one rule-restatement + ten ordinary uses.
2. **A stale citation the previous round had already handed over corrected.** The note cites
   `CLOSURE_RANK1_CAMPAIGN.md:341`; at `63009dd3` line 341 is **blank** and the sentence is
   at **374**. Round 2's observation **O3** reported the +33 shift *and gave 374*,
   explicitly *"recorded so a round 3 does not inherit it."* It was inherited.
3. **The frame counts do not reproduce.** Claimed *"76 hit lines tree-wide, 59 under
   `demo-output/website`"* over *"the whole working tree"*; measured at the nearest committed
   revision, **77 and 63**. A working-tree frame is a **superset** of tracked files and
   therefore cannot return fewer hits than tracked-only, so the declared frame is not the
   frame that ran.

**The verdict C9 carries is right** (Q51) and the strike-rather-than-delete disposition is
right. But a correction issued for imprecise sweep evidence should not ship imprecise sweep
evidence. *Reported, not fixed.*

### R6 — MODERATE. The bundle absence report's file counts do not reproduce under any classification

`7cd558b1`: *"**Bundle-wide sweep: 78 text files, 23 binary skipped**, core-defect hits 0."*
78 + 23 = **101**. The committed zip at the frame holds **90 non-directory members** (103
entries including 13 directory entries). Measured splits: **82 / 8** by null-byte test;
**69 / 21** by extension. **None is 78 / 23.**

**The result the sentence reports is correct** — I re-verified the zero independently with a
wrap-proof instrument and a planted control (Q54–Q55). The defect is that a report whose
entire thesis is *"a zero is only knowledge if you can say what it was measured over"*
states a corpus size that does not match the corpus. *Reported, not fixed.*

### R7 — MODERATE. The `.tex` routing citations are wrong in the entry written to route them

`4e719a6b` / `afe1af99` route the `.tex`'s owner by line number. At the frame:

- *"two sites additionally state the rule the chief WITHDREW: 243 and **287**"* — 243 is
  exact; **287 is a figure site**, already counted among the nine bare ones. The caution
  (*"That figure is an **internal one** — … not to be quoted outside it"*) is at **289**.
- The twelve figure sites are exact, but the accounting is `1 interval (260) + 1 inheriting
  (265) + 9 bare = 11`. **Line 648 appears in the twelve and in neither category.**

The routing nonetheless worked: the `.tex`'s owner closed every one of these out of frame at
01:07–01:10 (§0.2). **The failure is that an entry written so an owner could be routed *from
the record rather than from a message* sends him to one wrong line and silently drops
another.** *Reported, not fixed.*

### R8 — MINOR. The withdrawn-rule replacement is grafted onto the source citation

`closure_challenge_round5_qcr.json`, `rank_companion_2026_08_10`, now ends:

> *"…The 0.0024 seed bound moves P(rank 1) from 52 to 81 percent. **Source:
> campaign/PROBABILITY_OF_RANK_2026-08-10.md - SUPERSEDED 2026-08-10 -** the internal-only
> restriction was WITHDRAWN by chief ruling…"*

The removed sentence stood **before** `Source:`; the replacement was appended **after** it,
so the SUPERSEDED marker sits adjacent to a filename and reads, for one clause, as though
the source document were superseded. The following clause resolves it, and the three
chief-owned records place the marker where the restriction stood. **Substance correct (Q4);
placement introduces a readable-as-wrong sentence in the artifact the outward document names
as its source.** *Reported, not fixed.*

### R9 — OBSERVATION. The seed correction is accurate but reads worse than what it replaced

`DESCRIPTION_DOCUMENT.md` §5 (Q38): *"loaded at 0.0024"* and *"loaded adversely onto the
three seed-dependent cases"* eleven words apart, with a three-line parenthetical between
subject and verb. No ambiguity of fact. A presentation matter for the document's owner, of
the same kind the round itself correctly declined to decide about the table heading.

### Lesser observations, not ranked

- **O1.** `37049247`: *"A concurrent audit rung graded this pass's first six commits while it
  worked: every row passed"* names no rung and no record, and I could not identify either
  within the frame (Q74).
- **O2.** `63009dd3`'s commit body says 15 in the closure line and then accounts for 4 + 10;
  the in-file note reconciles it with the fifth, the body does not (Q53).
- **O3.** Three claims are **inherited rather than verified** by this rung and say so:
  `self_audit`'s PASS (Q8), the `56 of 56` drift check and the HTTP read (Q60), and the
  run-tree `*_LES*` counts (Q69). Round 3's own two inheritance disclosures were correct.
- **O4.** The dispatch omitted the chief's own `PRODUCT_LIST` entry for the **third
  consecutive round** (§1.3.2). L-56, written in one of the two missed commits, names the
  rule-creating-commit class and not this one.

---

## 5. WHAT ROUND 3 GOT RIGHT, STATED AT THE SAME STRENGTH

Of **48** verifiable claims in round 3's output, **38 pass**, and several are better than the
correction required:

- **N3 is exact to the unit and then goes further.** 73 in 19 files, the per-file breakdown
  summing to 73, 73 − 29 = 44, and the reconciliation holding at two separate revisions —
  and it **corrected the label on round 2's arithmetic** (51 in 14 at `249b611c`, minus four
  late notes = 47) rather than disputing the arithmetic. That is the most careful thing any
  round has done to a predecessor's finding.
- **N4 and N5 are both closed against primary artifacts, with falsifications.** N5 does not
  merely assert that the bootstrap used 0.0024; it computes what 0.002419 *would* have
  produced and shows the table does not carry it.
- **N2 is genuinely closed and the fix is in the generator.** Both JSONs were rewritten
  **from** `build_benchmarks._CLOSURE`, not beside it, and `self_audit` gained a guard that
  fails the wall on a bare rank claim — *a rule that binds surfaces got a check that reads a
  surface*, with negative controls so it cannot fire on text carrying no rank claim.
- **`656c09c9` declared the failure it created, first, and refused the tempting fix.** It
  named the bundle drift it caused, named the second drift it did not cause, and refused to
  rebuild `dist/` because the archive was ring-fenced and a rebuild would have shipped
  another family's unverified change. **A round that knows what it must not fix.**
- **`f2e16a47` §9 is the best method this ladder has produced.** *An absence claim needs an
  instrument that cannot produce a false absence and a positive control proving it* — and
  the demonstration is a planted file on which the **old** instrument returns zero, which
  converts three prior verifications from "unconfirmed" to "unsound". I reproduced it
  independently and adopted the rule for this document's own sweeps (§0.4).
- **"A fragment shared by a defect and its fix is evidence of neither"** was found by the
  author of the flawed fragment set, in his own work, and written into the standard.
- **The absence result itself survives independent re-measurement.** Zero core-defect hits
  across all 82 text members of the committed archive, with my own control firing.
- **V6 is re-derived, not inherited.** Every anchor I re-checked — 126/128, 178/179,
  225/228, 84–86, 218–219/301–302, MANIFEST:37, README:52–54, `kOmegaSSTQCR.C:60` and
  91–99, eight CSVs at 1000×3, `AR_1` at `bb8d61fb…` — is **exact**, and the block is
  additive (+51/−0): nothing rewritten, two findings marked MOOT with their reasons, the
  stale summary left standing because it is the summary *of that audit*.
- **Round 3 refused three fixes with reasons** — the `.tex` (not its file), the approved
  proposal (a rewrite under an unchanged `decided_at` would forge the record), and the
  interval-table heading (a presentation decision needing the owner) — and **the `.tex`
  refusal was vindicated within 36 minutes** by its actual owner closing it.
- **The banned list is clean on new text, including the strictest item.** The only rank
  claims round 3 wrote carry the figure, the interval and both undecided pairs. No bare
  figure entered the corpus this round.
- **F2 did not recur**, in either direction.

---

## 6. THE TREND ACROSS FOUR ROUNDS

| round | frame | failures | blocking | in the outward package | character |
|---|---|---|---|---|---|
| 1 | `c8031a03..8ef715c1` | **10** | 2 | 3 (F1, F2×2, F3) | wrong numbers and a future date **in the entry** |
| 2 | `6afe15e3..249b611c` | **6** | 0 | 1 (N5, a precision label) | the record of the corrections |
| 3 | round 3's own self-report | 1 (declared) | 0 | 0 | the failure it created, declared first |
| **4** | `249b611c..d7d51974` | **7** | **0** | **0** | **the record of the record — three of seven are in text written to record a defect accurately** |

**The count stopped falling: 10 → 6 → 7.** But the count is the least informative column.
Two things did keep improving, monotonically:

- **Severity.** Blocking: 2 → 0 → 0. **Outward-package accuracy defects: 3 → 1 → 0.** Round
  3 introduced **no wrong number, no wrong date and no bare figure anywhere a reader outside
  this lab would meet one.** That is the first round of which this is true.
- **Method.** Round 1 caught a bad sweep; round 2 caught a sweep declaring a frame it did not
  cover; round 3 **built the instrument that makes those catchable** and applied it to its
  own prior work, converting three passing verifications into unsound ones on its own
  initiative. Round 4's own absence claims rest on round 3's rule.

**What replaced the old failure mode is a new and narrower one.** Every one of R1–R7 is a
*description of a correction* that is less exact than the correction it describes:

| finding | the work | the description of the work |
|---|---|---|
| R1 | the provenance is real and unfixable except by record | 59 lines claimed, 34 measured |
| R2 | two surfaces genuinely superseded | the list of six not updated |
| R3 | the structural derivation is the right method | its parameter excludes its own top result |
| R4 | five surfaces genuinely traced | three were findable by phrase search |
| R5 | the C9 verdict is right and the strike is right | 16 hits enumerated as 15, one line stale, frame counts unreproducible |
| R6 | the absence is real and independently confirmed | the corpus size does not match the corpus |
| R7 | the routing worked within 36 minutes | it named one wrong line and dropped another |

**This is a real convergence in one dimension and a plateau in the other.** The entry is
getting cleaner and the *bookkeeping about the cleaning* is not. Round 1's diagnosis —
*"the fix for a class is where that class reappears"* — now applies one level up: the class
has moved from the claims to the changelog.

---

## 7. VERDICT — HAS THE LOOP REACHED THE FIXED POINT?

# NO.

The termination rule requires that a re-run of V8/V10/V14/V15 over the previous fix round's
text introduce **no new failures — not "few", not "only cosmetic ones". Zero.**

**Seven new failures are in round 3's own output**, measured at `d7d51974`, frame frozen
2026-08-11 01:02:28 UTC:

| # | severity | one line |
|---|---|---|
| **R1** | MAJOR | the provenance note and L-57 both say 59 lines of another agent's work; 34 of the 59 are, and 25 are the committing pass's own on-message section |
| **R2** | MAJOR | "six still assert" was falsified by the same author's next commit 2 m 57 s later, which closed two of them — one of them in the same file as the list |
| **R3** | MAJOR | "fourteen surfaces" is not reproducible; at the round's own stated 400-character window the instrument misses the surface the round ranks first |
| **R4** | MODERATE | "five of the six do not use the documents' words" — three of the six are returned by a case-insensitive grep for the documents' own words |
| **R5** | MODERATE | the F9 evidence correction enumerates 16 hits as 15, cites a line the previous round had already corrected, and declares a frame that cannot yield its own counts |
| **R6** | MODERATE | "78 text files, 23 binary skipped" = 101; the archive holds 90 members, splitting 82/8 or 69/21 |
| **R7** | MODERATE | the `.tex` routing entry sends its owner to a wrong line and drops one of its own twelve sites |

**This is the rule working, not the rule failing** — and it is working in the direction the
rule was written for. Round 3 is the first round to put **nothing** wrong into the outward
package, to write **no** bare rank claim, and to build the instrument that makes absence
claims checkable at all. If the fixed point were defined on the entry, the entry is at it.

**It is not defined on the entry. It is defined on the round's own output, and round 3's
output has seven demonstrable defects in it.** Three of them are in text written for the
sole purpose of recording a defect accurately, which is the worst place for them to be,
because that text is what every future round will read as ground truth. **R1 in particular is
now a numbered lesson in `LESSONS.md` and will be cited.**

**There will be a round 5.** Its scope is R1–R9 plus anything the ladder writes closing them,
plus the eleven out-of-frame commits at §0.2 — four of which close surfaces this round
reported as open — and it must be run by an agent that wrote none of it.

**What round 5 should be told, because round 4 learned it the hard way:**

1. **Re-take every measurement against your pinned revision after any surprise.** My frame
   moved at 01:07 and I only noticed because a `git show HEAD:` disagreed with a read I had
   taken four minutes earlier. Every `.tex` number in this report was re-measured against
   `d7d51974` explicitly afterwards. **`git show HEAD:` is not a pinned read.**
2. **Check the dispatch's list for commits that are *before* the range, not only for ones
   that are missing from it.** Six of the twenty-one named here were round 2's subject, and
   auditing them would have inflated round 4's PASS count by six commits' worth.
3. **A count derived from a window is a claim about the window.** State the parameter, and
   test it against your own top-ranked result before you publish the count.

**One thing this rung cannot certify.** I verified round 3's text against its named
artifacts. I did not re-verify the artifacts, did not re-run the scorer, the bootstrap,
`build_master_table.py`, the bundle builder or `self_audit.py`, and did not audit uncommitted
work or anything after 01:02:28 UTC beyond enumerating it. Where I read a measurement rather
than took one, the row says so (Q8, Q60, Q69).

---

**Signed: the Ladder V rung V15 round-4 owner, 2026-08-11 01:02:28 UTC frame (clock read
01:02:28 and re-read 01:23:30).**
Zero scoring calls; ledger unchanged at 6. Nothing was sent, emailed, uploaded or filed.
Read-only except this file. No file audited above was edited by this rung.
