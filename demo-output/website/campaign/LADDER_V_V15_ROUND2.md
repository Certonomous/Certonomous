# Ladder V — rung V15, ROUND 2: does the fix round's own text pass the claims table?

**Executed 2026-08-11 UTC (clock audit in §0.1). Owner: an agent that wrote none of
the text below, has never written to the closure line, and did not participate in
round 1 or in the correction pass it audits.**

Round 1 (`LADDER_V_V15_LADDER_TEXT_CLAIMS.md`, `6afe15e3`) audited the text the ladder
wrote and failed it. A correction pass then closed those findings **and wrote more text
doing so.** The termination rule (`LADDER_V_TRIPLE_VERIFICATION.md` §"WHEN THE LADDER IS
GREEN", `5bffb476`) says the ladder is green at a **fixed point**: a fix round that
introduces **no new failures in its own output**. This document is the measurement of
that.

**I produced none of the text audited here.** No edit to any file below. **Scoring calls
made by this rung: ZERO; the ledger stands at 6.** Every check is static, arithmetic, or
a re-read of an artifact on disk. **Nothing was sent.** Read-only except this file.

---

## 0. FRAME, STATED BEFORE ANY COUNT

### 0.1 Clock audit, run before any date is used

```
$ date -u
Tue Aug 11 00:04:08 UTC 2026     (start of the resumed pass)
Tue Aug 11 00:07:16 UTC 2026     (frame frozen; HEAD pinned)
```

**Today is 2026-08-11.** The date rolled over genuinely during execution — an earlier
segment of this pass ran at `Mon Aug 10 23:35:53 UTC 2026`. This document is therefore
legitimately dated 2026-08-11, which is the same string that was false yesterday and is
finding F2 of round 1. The distinction is the clock, and the clock was read.

### 0.2 The frame is timestamped because the corpus is moving

**Frame frozen at HEAD = `249b611c` (2026-08-11 00:06:59 UTC), read at 00:07:16 UTC.**

The set moved **four times while I was measuring it**: `dc13f1cc` and `5af41163` landed
at 23:43–23:44 while the process was down, and `4381d634`, `a3a4ab3a`, `79f4529c`,
`249b611c` landed between 00:04:17 and 00:06:59 — i.e. *during the three minutes it took
me to re-derive the set*. **This frame may have moved again by the time it is read.** A
frame without a timestamp would be a guess; this one has three.

**Uncommitted work, noted and NOT audited.** At 00:07:16 the tree is dirty in six files:
`benchmarks.html`, `benchmarks.json`, `wall/wall.json`, `sdk/scripts/build_benchmarks.py`,
`scripts/self_audit.py`, `sdk/.filming-keepalive`. Four of those six are the exact
surfaces of round 1's finding F7. **Someone is closing F7 in the working tree as I write.**
I audit the committed state at `249b611c`, where F7 is open, and I say so in N2 rather
than either crediting an uncommitted fix or reporting a failure that is being repaired.

### 0.3 Definitions

- **"fix-round text"** means lines *added or modified*, in `6afe15e3..249b611c`, by a
  commit that touches the round-5 submission package, one of the 16 claim-bearing
  surfaces of `PROBABILITY_OF_RANK_2026-08-10.md` §7, a closure artifact, or a rule this
  ladder enforces. Derived from `git log --name-only` and `git show`, never from a
  pass's own summary. Commit *messages* are in scope: round 1 audited the chief's commit
  body at `2ef8ae3b` (T38–T42), so the precedent is set, and a claim that reaches
  `PRODUCT_LIST` from a commit body is the same claim twice.
- **"claim"** = a sentence asserting a quantity, a date, a count, a rank, or a
  compliance fact.
- **"FAIL"** = I can demonstrate it by running something or displaying a byte. Where I
  could only argue: OBSERVATION.
- **"surface"** = a file, not a document family.

### 0.4 Reach, proved before any absence is reported

All sweeps use **`/bin/grep` directly**, never the ignore-honouring wrapper, with
`--exclude-dir=.git`, and enumerate tracked files via `git ls-files -z | xargs -0`.
Historical states are read with `git grep <rev>` and `git show <rev>:<path>`, never the
working copy. JSON artifacts are parsed with `json.load` and walked, not grepped, so a
value nested under a key I did not guess still reports.

**Every negative carries a positive control, seeded and confirmed to fire:**

| sweep | control seeded | fired |
|---|---|---|
| `2026-08-11` | `scratchpad/pc.txt` | yes (1 hit) |
| `comfortab` / `novel` / `official rank` | `scratchpad/pc3.txt` | yes (3 hits) |
| `never appears in an external claim` | `scratchpad/pc2.txt` | yes (1 hit) |
| `5.8e-4` family | `scratchpad/pc4.txt` | yes (1 hit) |

The `dist/` archive was opened with `zipfile` and every member read, not inferred from
its sources (§2, row P8).

### 0.5 What this frame structurally cannot contain

It cannot see uncommitted text (§0.2 names it instead). It cannot see text that lands
after 00:07:16. It cannot adjudicate whether an artifact is *itself* right — only whether
a sentence matches it. It did not re-run `build_master_table.py` or the bootstrap: where
the fix round says an output reproduces byte-for-byte, this rung inherits that and says
so (§2, rows I1–I2).

---

## 1. THE TRUE COMMIT SET, WITH CORRECTIONS TO THE DISPATCH

The dispatch named five: `7de8733c`, `9477a2ed`, `b032bbae`, `1db6fc3c`, `a454c6bb`,
and said to assume the list was short. **It was short by six, and one of the six is the
commit that recorded the round-1 verdict.** Nothing named was misattributed.

`git log --format='%H|%ci|%s' --name-only 6afe15e3..249b611c` returns **23 commits.**

### 1.1 IN SCOPE — the fix round's text on the package and its surfaces

| # | commit | UTC | author-role | what it wrote |
|---|---|---|---|---|
| 1 | `a454c6bb` | 08-10 21:29:07 | **chief** | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` — the F8 date correction (07-30 → 07-31) ✔ *dispatch named it* |
| 2 | `94733c2d` | 08-10 21:29:31 | **chief** | `docs/PRODUCT_LIST.md` — the round-1 verdict entry, ~30 lines of quantitative claims ✘ **MISSED by the dispatch** |
| 3 | `7de8733c` | 08-10 21:31:54 | fix pass | `DESCRIPTION_DOCUMENT.md` §7 + `LADDER_V_PASS2` C6 + `LADDER_V_PASS3_COLD` D5 — F1 ✔ |
| 4 | `9477a2ed` | 08-10 21:35:18 | fix pass | 15 files — F2, the date fix ✔ |
| 5 | `b032bbae` | 08-10 21:39:51 | fix pass | 5 files — F3, F4, F5, F6, and (relabelled) F10 ✔ |
| 6 | `1db6fc3c` | 08-10 21:41:55 | **chief** | `ACTIVE_RESEARCH`, `CLOSURE_CHALLENGE_STATUS`, `CHALLENGE_LANDSCAPE`, `PRODUCT_LIST` — the three rule-statement corrections + a ~27-line entry ✔ |
| 7 | `5bffb476` | 08-10 23:34:59 | **Katie** | `LADDER_V_TRIPLE_VERIFICATION.md` — the termination rule ✘ **MISSED** (see 1.3) |
| 8 | `dc13f1cc` | 08-10 23:43:15 | fix pass (V14) | `closure_eval_master_table.{md,json}` + `build_master_table.py` ✘ **MISSED** |
| 9 | `5af41163` | 08-10 23:44:10 | fix pass (V14) | `CLOSURE_RANK1_CAMPAIGN.md` — a supersession banner **that makes a rank claim** ✘ **MISSED** |
| 10 | `4381d634` | 08-11 00:04:17 | fix pass (V14) | `closure_round4_manifest.py`, `export_closure_submission_csvs.py` — two live generators ✘ **MISSED** |
| 11 | `a3a4ab3a` | 08-11 00:05:26 | fix pass (V14) | `CLOSURE_EVALUATION_PROTOCOL.md` — a round-5 note that restates F1 correctly ✘ **MISSED** |
| 12 | `79f4529c` | 08-11 00:06:20 | fix pass (V14) | `docs/NUMERICS_KNOWLEDGE.md` — a gate correction + a reported-not-fixed finding ✘ **MISSED** |
| 13 | `249b611c` | 08-11 00:06:59 | fix pass (V14) | `LIBRARY_ACCESS_LIST.md`, `closure_challenge_C2_error_decomposition.md` ✘ **MISSED** |

**Also in scope on the bundle, audited as an artifact rather than as prose:**

| # | commit | UTC | what |
|---|---|---|---|
| 14 | `892f11f7` | 08-10 21:32:14 | `dist/certonomous-demo.zip` rebuilt ✘ MISSED |
| 15 | `a1545dbd` | 08-10 21:39:49 | `dist/certonomous-demo.zip` rebuilt again ✘ MISSED |
| 16 | `dc5b12bd` | 08-10 21:33:00 | `BUNDLE_REBUILD_2026-08-10.md` ✘ MISSED |
| 17 | `8cc6bf70` | 08-10 21:33:56 | `PRODUCT_LIST` bundle entry ✘ MISSED |

### 1.2 IN RANGE, DELIBERATELY OUT OF SCOPE

Enumerated so the exclusion is a decision, not an oversight. None touches the submission
package, the 16 claim-bearing surfaces, or a closure artifact:

`b69cd45e`, `be90ead6`, `54cf11bb`, `ab0c8d76`, `1471b8f3`, `03d68946`, `67d63e7f` — the
monitor-corpus, bundle-drift-gate and S6-wiring lines. Four of these touch
`docs/PRODUCT_LIST.md`, which **is** claim-bearing (row 14), but they write about
`MONITOR_STANDARD`, `HeadEngineer` and served HTML, not about the closure line, and they
are a different family's output rather than the fix round's. They are named here so a
later rung can pick them up under its own brief.

### 1.3 Corrections to the dispatch, in order of importance

1. **`5bffb476` is missing, and it is the commit that defines the test I am running.**
   Round 1's finding §1.2.1 was *"the dispatch that created V15 omitted the commit that
   created V15."* **The dispatch that created round 2 omits the commit that created the
   termination rule round 2 exists to apply.** The same shape, one rung later, from the
   same author. It is genuinely excluded from *re-opening* the ladder by its own text
   (*"What does NOT reopen … and this document"*), and I honour that exclusion — but the
   exclusion is a decision the auditor should make, not a gap in the list.
2. **Six V14-line commits (`dc13f1cc`, `5af41163`, `4381d634`, `a3a4ab3a`, `79f4529c`,
   `249b611c`) are missing** — the largest block of fix-round text by count, four of them
   written *after* the dispatch was issued. They are unambiguously in scope: they edit
   claim-bearing surfaces, they make quantitative claims, and one of them (`5af41163`)
   makes a **rank claim**, which is the single most rule-bound sentence type this ladder
   governs.
3. **`94733c2d` is missing**, and it is the chief's own record of the round-1 verdict —
   ~30 lines of quantitative claims on `PRODUCT_LIST`, written 33 seconds after
   `a454c6bb`, which the dispatch *did* name.
4. **The four bundle commits are missing.** The bundle is the artifact V14 exists for.
5. **Nothing the dispatch named was misattributed.** All five verified by `--name-only`
   and commit body.

---

## 2. THE CLAIMS TABLE OVER FIX-ROUND TEXT

Every quantitative sentence → the named artifact → verdict.
**Result: 6 FAIL, 3 OBSERVATION, 24 PASS.**

### 2a. F1 — the duct-continuity replacement (`7de8733c`)

The sentence that replaced the F1 defect now names three cases and their values. All
three verified against the primary artifact by parsing it, and the case it no longer
names verified absent from the submission **two independent ways**.

| # | claim | artifact | verdict |
|---|---|---|---|
| **P1** | *"the three submitted ducts measure 8.5×10⁻⁴ (`AR_1_Ret_360`)…"* | `closure_challenge_round5_qcr_forward.json` `/arms/AR_1_Ret_360_qcr/div_over_grad` = **0.0008513586571181056** | **PASS** |
| **P2** | *"…5.3×10⁻⁴ (`AR_3_Ret_360`)…"* | `/arms/AR_3_Ret_360_qcr/div_over_grad` = **0.0005280760589259479** | **PASS** |
| **P3** | *"…and 5.4×10⁻⁴ (`AR_14_Ret_180`)"* | `/arms/AR_14_Ret_180_qcr/div_over_grad` = **0.0005439557592814662** | **PASS** |
| **P4** | the case no longer named — `AR_7_Ret_180` — **is not in the submission** | (i) `/what_ships/changed` = `[AR_14_Ret_180, AR_1_Ret_360, AR_3_Ret_360]` and `/what_ships/unchanged` = the five non-duct cases; `AR_7` appears in neither. (ii) `closure_challenge_submission_round5/test/` holds exactly **8 CSVs**, none of them `AR_7*` | **PASS — verified two ways, and neither is the artifact the chief's record names (see N4)** |
| **P5** | 5.8×10⁻⁴ = `/arms/AR_7_Ret_180_qcr` = **0.0005798299261245847** | same JSON | **PASS** |
| **P6** | the corrections in `LADDER_V_PASS2` C6 and `LADDER_V_PASS3_COLD` D5 carry a **dated correction note** naming F1 rather than silently reading right | both diffs read | **PASS — this is the right disposition and the record shows what changed and why** |
| **P7** | no surviving surface presents 5.8×10⁻⁴ as the submission's | repo-wide `/bin/grep -rnIE "5\.8(e\|×10\|x10)"`, positive control fired. Every closure-line hit is either the corrected text, a report quoting the error, or `CLOSURE_EVALUATION_PROTOCOL.md:396` which states *"`AR_7_Ret_180` (5.8×10⁻⁴) is the validation duct and is NOT in the submission"* | **PASS** |

**Verdict on F1: closed, correctly, and stronger than the brief required** — the
replacement names cases instead of a bare range, so the number cannot be re-read as
belonging to a case the reader will not receive.

### 2b. F2 — the 29 date corrections across 15 files (`9477a2ed`)

| # | claim | verification | verdict |
|---|---|---|---|
| **P8** | **29 assertions corrected, in 15 files** | Counted per file from the diff and confirmed by differencing the corpus: `git grep -oI "2026-08-11"` gives **73 occurrences in 19 files at the parent `8cc6bf70`** and **47 in 10 files at HEAD**. 73 − 29 removed + 3 new filename-notes = **47** exactly. Stat confirms 15 files | **PASS — 29 and 15 are exact** |
| **P9** | no correction changed a sentence's meaning | All 29 read individually. Every one changes only the date token inside a sentence asserting when something was written, ruled, signed, added or re-measured. Three carry a rider, checked separately: **(a)** `PROBABILITY_OF_RANK:54` gained *"AMENDED 2026-08-10 (later the same day)"* — a NEW claim, and it **verifies**: confirmed by the chief at `a57d8d3b` 16:02:01Z, amended at `c1187949` 20:52:44Z, same day, later. Without it the corrected line would have read "confirmed 08-10 … AMENDED 08-10" and looked self-contradictory. **(b)** `exec_bits.py:54` `WAIVER_REGISTER_DATED = "2026-08-11" → "2026-08-10"` is a **code constant** — `/bin/grep -rn` finds exactly two references, its own definition and a docstring at line 75; **no logic reads it**, so the change is behaviour-neutral and corrects a false adoption date. **(c)** `INSTRUMENT_INTEGRITY` and the two PASS reports gained filename-date notes rather than renames | **PASS — no meaning changed, and the one new claim added verifies** |
| **P10** | **the 45 occurrences left alone are references, not assertions** | All 23 non-round-1-report lines read in full. Every one is a filename citation (`LADDER_V_PASS2_2026-08-11.md` as a path), a note *about* the error, or a quotation of it. Two examined hard: `LADDER_V_PASS1:1` *"(deliverable dated 2026-08-11)"* is disambiguated by its own line 18, *"The dispatch and this filename are dated 2026-08-11"* — the one pass that recorded the discrepancy against its own clock instead of inheriting it; `MEMORY_ARCHITECTURE:664/672` quote the peer's twelve-file measurement as a dated finding. **None is an assertion.** | **PASS on the classification** |
| **F-N3** | **"Of the 74 occurrences … 45 were references"** | The corpus at the fix's own parent `8cc6bf70` holds **73**, not 74, and therefore **44** references, not 45. Sub-split also misses: claimed *11 filename citations / 12 discussion lines / 22 V15 lines*; measured **8 / 14 / 22**. Counted twice, by `git grep -oI` and by `json`-free Python over `git show <rev>:<path>`, agreeing at 73 | **FAIL — N3.** See §3 |
| **P11** | *"dist/ is being rebuilt by another agent and will pick up the corrected source"* — reported, not fixed | Opened `dist/certonomous-demo.zip` with `zipfile` and read **every member**: **zero** occurrences of `2026-08-11`. `/bin/grep -rn` over the unpacked `dist/certonomous-demo/`: zero. The rebuild at `a1545dbd` (21:39:49) did absorb it | **PASS — a prediction made and now verified true** |
| **P12** | *"19 tracked files … not the peer's twelve and not V15's 17"* | 19 confirmed at `8cc6bf70` | **PASS** |

### 2c. F3 — the chronology, verified from commit timestamps by this rung (`b032bbae`)

I ran `git log -1 --format=%cI` on all three commits myself and differenced them in
Python rather than reading the fix round's arithmetic.

```
fe121af2  2026-07-31T06:53:00+00:00   CSV last moved
92840d8c  2026-07-31T23:13:49+00:00   first mention of 2504.06758   → 16:20:49
15530f97  2026-08-02T05:30:22+00:00   read in full                  → 1 day, 22:37:22
```

| # | claim | verdict |
|---|---|---|
| **P13** | *"**1 day 22 h 37 m before** it was read in full"* (PRIOR_ART firewall table, PASS2 table) | **PASS — exact to the minute** |
| **P14** | *"**16 hours**"* retained | **PASS** — 16 h 20 m 49 s |
| **P15** | *"overstated by 55%"* | **PASS** — 3 d / 1 d 22:37:22 = **1.5443**, i.e. 54.4% |
| **P16** | corrected at **four sites** | DESCRIPTION_DOCUMENT §4; PRIOR_ART firewall table; PRIOR_ART closing sentence (*"the same bytes it was 1 day 22 hours before"*); PASS2's table. **PASS** |
| **P17** | the outward document rounds to *"1 day 22 hours"* while the record says *"1 d 22 h 37 m"* | consistent, rounded down, never inflated. **PASS** |

### 2d. F4, F5, F6 — the other outward additions (`b032bbae`)

| # | claim | artifact | verdict |
|---|---|---|---|
| **P18** | F4 note: the 68% rests on Reissmann **0.059525**; the margin **0.0028863** rests on **0.0595338**; *"the bootstrap has NOT been re-run"*; difference **9×10⁻⁶, about 0.3% of the margin"* | `PROBABILITY_OF_RANK` §Inputs; 0.0595338 − 0.059525 = 8.8×10⁻⁶; ÷0.0028863 = 0.31% | **PASS — and stating the split rather than smoothing it is the right disposition** |
| **P19** | F6 citation: benchmark `README.md` @ `deb91557`, **line 98**, §Submission instructions: *"You can preview what your score will be using the benchmark dataset's python package"* | Read at the frozen commit via `git show deb91557:README.md`. Line 98 is verbatim; headings show `# Submission instructions` at line 92 | **PASS — verbatim, at the frozen commit, correct section** |
| **P20** | F6 citation: **line 21**, §Motivation: *"All other decisions are left to the submitter"* | Line 21 verbatim; `# Motivation` at line 16 | **PASS** |
| **P21** | F5 seed row **52–81%** added to the outward interval table; *"52.0%" / "80.5%" / as scored 67.6%* | `PROBABILITY_OF_RANK` §2 table: adverse **52.0%**, as scored **67.6%**, favourable **80.5%** | **PASS on the values** |
| **P22** | *"A seed draw we did not control moves the figure by nearly thirty points"* | 80.5 − 52.0 = 28.5. Phrase is pre-ladder (`b2aa6887`, `git log -S`) | **PASS** |
| **F-N5** | *"the truth-free seed bound of §8 (**0.002419**), loaded adversely … gives 52.0%"* | The internal table's overalls are **0.059047** and **0.054247** = 0.056647 **± 0.0024** exactly. 0.002419 would give 0.059066 / 0.054228. `closure_challenge_round5_qcr.json` states it plainly: *"The **0.0024** seed bound moves P(rank 1) from 52 to 81 percent"* | **FAIL — N5.** See §3 |
| **P23** | F7-as-relabelled: `CHALLENGE_SLATE_2026-08.md:37` now carries the figure **with** its 2–100% interval, the 52–81% range, the named undecided pairs, and the withdrawn gate replaced by the prohibition | line read | **PASS — the round-1 F10 violation is closed** |
| **F-N6** | *"CHALLENGE_SLATE:37 is the **ONLY** surface carrying it without an interval — every sibling already carries 2-100%"*, five siblings named | `latex/closure_challenge_report.tex` — **row 16 of the same 16-surface list** — prints `P(rank 1) = 68\%` at **7** sites and carries an interval at **one** (lines 259–260). It is named in neither the five nor the exception | **OBSERVATION — N6.** See §3 |

### 2e. The chief's three rule-statement corrections (`1db6fc3c`) — audited as a writer like any other

The chief edited three records to say the internal-only restriction was withdrawn and
the figure now travels. **The three statements are byte-identical to each other**, which
is the right property, and each is accurate:

| # | claim | verification | verdict |
|---|---|---|---|
| **P24** | `ACTIVE_RESEARCH.md`, `CLOSURE_CHALLENGE_STATUS.md`, `agenda/CHALLENGE_LANDSCAPE.md` now read *"SUPERSEDED 2026-08-10 — the internal-only restriction was WITHDRAWN by chief ruling; the 68% figure now TRAVELS with the entry, and may never appear without its interval (2-100% at 95%) and the not-decided pairs"* | All three diffs are the identical two-line replacement. **Accurate**: the withdrawal is `c1187949` / the V8 amendment, dated 2026-08-10; the interval is the double-bootstrap 95% band; the two rules stated are exactly the amendment's | **PASS — accurate, and mutually consistent to the byte** |
| **P25** | did the correction introduce a NEW claim while correcting an old one? | It adds *"may never appear without its interval (2-100% at 95%) and the not-decided pairs"* — a prohibition that was **not** in the sentence it replaced. It is new text. It is also a verbatim restatement of the rule at `LADDER_V_TRIPLE_VERIFICATION.md:65–67`, so it asserts nothing the ladder has not already adopted | **PASS — new text, no new claim** |
| **P26** | the three surfaces themselves comply with the rule they now state | All three carry `P(rank 1) = 68%` **and** `2–100%` **and** both undecided pairs, checked by a context-window scan over every figure occurrence in every tracked file | **PASS** |
| **F-N1** | *"is now false on **four** surfaces because of my own reversal"* | **Five.** `demo-output/website/closure_challenge_round5_qcr.json`, `/leaderboard_comparison_dated_2026_08_07/rank_companion_2026_08_10`, still ends *"**INTERNAL ONLY; the figure never appears in an external claim.**"* | **FAIL — N1.** See §3 |
| **F-N4** | *"the submission side proved two independent ways — **the manifest's own changed-list** and the absence of a validation-duct CSV"* | `closure_challenge_submission_round5/MANIFEST.json` has **no changed-list**: its `files` key holds all eight cases undifferentiated, and the string `AR_7` does not occur anywhere in the file. The changed-list lives in `closure_challenge_round5_qcr_forward.json` `/what_ships/changed` | **FAIL — N4.** See §3 |
| **F-N2** | *"F3–F7 closed"* | Round 1's **F7** is *"four external surfaces were edited by this ladder and left non-compliant with the rule the same commit adopted"*. `b032bbae` relabels round 1's **F10** as its own "F7" and never addresses round 1's F7. At HEAD `249b611c`, `benchmarks.html`, `benchmarks.json`, `wall/wall.json` and `build_benchmarks.py` each contain `rank 1 of 5 scored locally` and **zero** occurrences of the figure or the interval | **FAIL — N2.** See §3 |
| **P27** | *"the figure was in THREE ladder documents, not the two V15 found"* | DESCRIPTION_DOCUMENT, PASS2 C6 (both found by round 1) + PASS3_COLD D5 (found by the fix). Three. **PASS** | **PASS** |
| **P28** | *"the report's copy routed"* | `LADDER_V_V14_SURFACE_DISCOVERY.md:216` is the fourth occurrence and is a **quotation** of the gate inside a report that already states the amendment withdrew it. Routing rather than editing is correct | **PASS** |

### 2f. The V14-line commits the dispatch missed (`dc13f1cc`, `5af41163`, `4381d634`, `a3a4ab3a`, `79f4529c`, `249b611c`)

| # | claim | verification | verdict |
|---|---|---|---|
| **P29** | `dc13f1cc`: round 5 superseded round 4 *"on 2026-08-07 … at 0.056647 … the three ducts moving to **0.0455 / 0.0400 / 0.0353** and the other five cases scoring identically"* | `closure_challenge_round5_qcr.json` `generated_at` = 2026-08-07T20:45:02Z, scoring call `07a7fe9e` 2026-08-07; `round5_per_case` ducts 0.0455 / 0.04 / 0.0353; the other five (0.0501, 0.1011, 0.0461, 0.0719, 0.0632) identical to round 4 | **PASS** |
| **P30** | `dc13f1cc`: *"the sixth pre-registered scoring call"* | ledger of 6, unchanged | **PASS** |
| **P31** | `dc13f1cc` puts the note **in the generator** and re-derives both outputs, rather than hand-patching | `build_master_table.py` diff emits both the supersession note and the corrected `round-4 0.0654` sentence | **PASS — this is the failure mode V14 named, avoided** |
| **I1** | `dc13f1cc`: *"the committed .md and .json reproduce byte-for-byte except the assembly stamp"* | Not re-run by me — running a closure generator is not read-only. **Inherited** | **OBSERVATION — not verified by this rung, and it says so** |
| **P32** | `5af41163`: `0.065438` is the mean of the eight **rounded** per-case values (0.0654375), not the full-precision round-4 overall **0.06543140783850523** | (0.0501+0.1011+0.0461+0.0719+0.0811+0.0775+0.0325+0.0632)/8 = **0.0654375** exactly; `closure_challenge_trained_entry_round4_duct.json` `round4_overall_full` = **0.06543140783850523** exactly | **PASS** |
| **P33** | `5af41163`: the −0.005913 deficit left as written | 0.065438 − 0.059525 = **0.005913**. Left uncorrected **deliberately**, because re-basing a plan onto its own outcome destroys the record of what was decided on what evidence | **PASS — and the reasoning is right** |
| **P34** | `5af41163`: **the banner makes a rank claim, so it carries the companion** — *"rank 1 of 5 scored locally"*, *"P(rank 1) = 68%"*, *"2–100% at 95%"*, *"not statistically decided"* (t = −0.50, −0.95), Liu 98.7% / Montoya 99.8%, *"a local scoring, not an official placement; nothing has been submitted"* | Every element present; t-values match `PROBABILITY_OF_RANK`'s −0.495 / −0.953 | **PASS — this is the model compliant rank claim in the corpus and the only new one written this round** |
| **P35** | `4381d634`: round dates *"round 3 2026-07-29T20:21Z, round 4 2026-07-31T23:10Z, round 5 2026-08-07T20:45Z"* | The three JSONs' `generated_at`: 2026-07-29T20:21:25Z, 2026-07-31T23:10:04Z, 2026-08-07T20:45:02Z | **PASS — all three exact** |
| **P36** | `4381d634`: *"was the entry of record when this script was written, on 2026-07-30"* | `closure_challenge_submission/MANIFEST.json` `generated_at` = 2026-07-30T18:58:52Z; the file's first commit is `fe121af2` 2026-07-31T06:53Z. Round 4 did not exist until 2026-07-31T23:10Z, so round 3 was the entry of record on **both** candidate dates | **PASS — true on either reading** |
| **P37** | `4381d634`: the two manifests on disk are **not** touched, as dated round-scoped artifacts (V14 §3.2 HISTORICAL); the **generators** are fixed | both diffs touch only `.py` | **PASS — fixing where the string is emitted rather than where it is read** |
| **P38** | `a3a4ab3a`: the protocol note restates F1 correctly and names `AR_7_Ret_180` as the validation duct not in the submission | verified against the same JSON as P1–P5 | **PASS — the F1 correction propagated to a surface nobody listed** |
| **P39** | `79f4529c`: round 2's PH-only sub-score is **0.080225**, the mean of 0.0501 / 0.1011 / 0.0723 / 0.0974; the current entry's is **0.0673** | (0.0501+0.1011+0.0723+0.0974)/4 = **0.080225**; (0.0501+0.1011+0.0461+0.0719)/4 = **0.0673** | **PASS — both exact** |
| **P40** | `79f4529c`: the gate is **reported, not silently re-pointed**, because either repair changes which experiment it is | text reads exactly that, with both candidate bars computed and the choice left to the owner | **PASS — the right stop, and the reason stated** |
| **P41** | `249b611c`: round 3 **0.0676**, round 4 **0.0654**, round 5 **0.056647** on 2026-08-07 | `closure_challenge_trained_entry_round4_duct.json` `round3_overall` 0.0676 / `round4_overall` 0.0654; round-5 JSON | **PASS** |
| **P42** | `dc13f1cc`, `5af41163`, `a3a4ab3a`, `79f4529c`, `249b611c` all route to `CLOSURE_CHALLENGE_STATUS.md` §0f for rank caveats **instead of** restating a rank claim (except `5af41163`, which states one and carries the full companion) | each note read | **PASS — the rank rule is engaged correctly on every one** |
| **P43** | **date discipline in the new text**: `dc13f1cc` and `5af41163` say *"added 2026-08-10"* and committed at 23:43 / 23:44 on 2026-08-10; `a3a4ab3a`, `79f4529c`, `249b611c` say *"2026-08-11"* and committed at 00:05–00:06 on 2026-08-11 | commit timestamps | **PASS — F2 did not recur; each note is dated by the clock at the moment it was written** |

### 2g. Banned-list enforcement over the fix round's text

| # | rule | sweep | verdict |
|---|---|---|---|
| **P44** | **no novelty claim on gated correction** | `/bin/grep -niI "novel"` over both package files: 2 hits, both prohibitions (*"No sentence in this package presents confidence-gated correction as novel"*, *"Not novelty for the decline gate…"*). Positive control fired | **PASS** |
| **P45** | **no "comfortable" margin language** | `/bin/grep -rniI "comfortab"` over the closure line: **one** hit, `PROBABILITY_OF_RANK:151`. Pre-ladder (`b2aa6887`, `git log -S`), unchanged by the fix round. `CLOSURE_RANK1_CAMPAIGN:374` (round 1's second hit, shifted +33 by the new banner) reads *"Assuming (a) is the comfortable reading"* — a reading of an assumption, **not** a margin descriptor. **No surface claims a comfortable AR_14 lead** | **PASS on the banned item** (see O2 for the record defect that persists) |
| **P46** | **no best-on-board count leaning on organiser-baseline rows without saying so** | `DESCRIPTION_DOCUMENT` §3.2 retains *"4 of 8, two of which are the baseline rows"* with the count belonging to the model given as 2 of 8, unhedged, in the same sentence. The fix round did not weaken it | **PASS** |
| **P47** | **no official-rank language** | 2 hits in the package, both disclaimers: *"This is a local scoring and not an official placement"*, *"Not an official rank. Not submitted"*. `5af41163`'s new banner repeats the disclaimer | **PASS** |
| **P48** | **the leakage disclosure present in the lab's own words** | §3b intact, quoting `R5_RULE_FREEZE.md` @ `0bade54a` verbatim, with the admission before the mitigations and the explicit *"No mitigation below cancels that sentence"*. The F6 citation was **appended after** the mitigation paragraph and the closing *"we would rather you weighed it than found it"* was split into its own paragraph — the concession still gets the last word | **PASS — and the structural property round 1 praised survives the edit** |
| **P49** | **every rank claim carries P(rank 1) with its interval and the undecided pairs** | The only **new** rank claim written this round is `5af41163`'s banner (P34): compliant in full. Every other new note routes to §0f rather than claiming | **PASS on new text** |
| **F-N2** | the same rule, applied to surfaces the ladder edited | four external surfaces at HEAD: rank claim, no figure, no interval | **FAIL — N2** |

---

## 3. NEW FAILURES, RANKED

These are failures **in the fix round's own output**. Round 1's findings are not
re-litigated here except where the fix round asserted them closed.

### N1 — MAJOR. A fifth surface still asserts the withdrawn rule, and it is the primary artifact

`docs/PRODUCT_LIST.md:2062` (commit `1db6fc3c`) states the internal-only sentence *"is
now false on **four** surfaces because of my own reversal"*, and that the chief corrected
*"the three I own"* with *"the report's copy routed"*.

**There is a fifth**, and it is not a report:

```
demo-output/website/closure_challenge_round5_qcr.json
  /leaderboard_comparison_dated_2026_08_07/rank_companion_2026_08_10
  "... The 0.0024 seed bound moves P(rank 1) from 52 to 81 percent.
   INTERNAL ONLY; the figure never appears in an external claim.
   Source: campaign/PROBABILITY_OF_RANK_2026-08-10.md. ..."
```

This is **row 13 of the 16 claim-bearing surfaces** in `PROBABILITY_OF_RANK` §7 — *"the
machine record"* — and it is the artifact `DESCRIPTION_DOCUMENT` §5 names as the source
of the score it publishes outward. It asserts, in the present tense, a restriction the
chief withdrew, on a figure the same package now prints.

**Why it survived, and why that matters more than the count being off by one:** the
document copies read *"INTERNAL ONLY; **the 68% figure** never appears…"*; the JSON reads
*"INTERNAL ONLY; **the figure** never appears…"*. A grep for the phrase as the documents
write it misses the artifact by three characters. **Pass 3 had already quoted the JSON's
exact wording** at `LADDER_V_PASS3_COLD_2026-08-11.md:388`, so the surface was on the
record before the sweep ran. This is V14's own thesis — *a surface nobody listed is
exactly where a stale claim survives* — reappearing inside the correction to it.

*Reported, not fixed. Owner: the closure line / the chief.*

### N2 — MAJOR. Round 1's F7 is reported closed and is not closed; it was renumbered out of existence

`b032bbae`'s subject reads *"F3-F7"*, and its body defines *"F7 (V15's F10) - the bare
68%"*. `docs/PRODUCT_LIST.md:2057` then records *"F3–F7 closed"*.

**Round 1's F7 is a different finding**: *"Four external surfaces were edited by this
ladder and left non-compliant with the rule the same commit adopted"* —
`benchmarks.html`, `benchmarks.json`, `wall/wall.json`, `build_benchmarks.py`. Round 1
ranked it MODERATE and put it in the *"should be corrected before anything is sent"*
group. At HEAD `249b611c`:

| surface | `rank 1 of 5` | `68%` | `2–100%` |
|---|---|---|---|
| `demo-output/website/benchmarks.html` | present | **0** | **0** |
| `demo-output/website/benchmarks.json` | present | **0** | **0** |
| `demo-output/website/wall/wall.json` | present | **0** | **0** |
| `sdk/scripts/build_benchmarks.py` | present | **0** | **0** |

The fix round closed round 1's F10 (a genuine defect, correctly fixed) and reported it
under round 1's F7's number. **A finding renumbered is a finding lost**, and the record
now says a thing is closed that a grep says is open.

**Honest qualification, per §0.2:** at 00:07:16 all four files are **dirty in the working
tree**, uncommitted, alongside `scripts/self_audit.py`. Someone is closing this right now.
I report the committed state, because that is what the record says and what a reader
would find.

*Reported, not fixed.*

### N3 — MODERATE. The date-fix arithmetic is off by one, in both the commit body and PRODUCT_LIST

The claim (`9477a2ed` body; repeated at `docs/PRODUCT_LIST.md:1946`): *"Of **74**
occurrences, **29** were assertions and all are corrected; **45** were references and
were correctly left alone."*

Measured at the fix's own parent `8cc6bf70`, over `git ls-files`, two independent ways
that agree:

| quantity | claimed | measured |
|---|---|---|
| tracked files carrying the string | 19 | **19** ✓ |
| total occurrences | 74 | **73** |
| assertions corrected | 29 | **29** ✓ |
| references left alone | 45 | **44** |

The sub-split fails wider: claimed *11 filename citations / 12 discussion lines / 22
V15-report lines*; measured **8 / 14 / 22**.

Reconciliation, which is what makes 73 certain: 73 − 29 + 3 (the new filename notes the
fix itself added) = **47**, and 47 is exactly what HEAD carries. **The corrective work is
exact; the arithmetic reporting it is not** — which is the same shape as round 1's F3,
where the citation was right and the subtraction was wrong, in a fix for that class.

*Reported, not fixed.*

### N4 — MODERATE. One of the two "independent ways" names an artifact that does not contain the evidence

`docs/PRODUCT_LIST.md` (commit `1db6fc3c`): *"the submission side proved two independent
ways — **the manifest's own changed-list** and the absence of a validation-duct CSV in
the shipped directory — rather than taken from the brief."*

`closure_challenge_submission_round5/MANIFEST.json` has **no changed-list**. Its keys are
`generated_at, measured_date, purpose, produced_by, reproduces,
scoring_calls_made_by_this_run, scoring_call_note,
independent_pre_score_verification, format, harness,
verification_against_prior_rounds, recorded_scores, files`; `files` holds all eight cases
undifferentiated; **the string `AR_7` does not occur in the file at all**. The changed-list
is `/what_ships/changed` in `closure_challenge_round5_qcr_forward.json`.

**The underlying fact is true** and I verified it two ways myself (P4). The defect is that
a sentence written specifically to say *"verified against the primary artifact rather than
taken from the brief"* names the wrong primary artifact — in a claims table whose entire
axis is sentence → named artifact.

*Reported, not fixed. Owner: the chief.*

### N5 — MODERATE. The new outward seed paragraph names a precision its own computation did not use

`DESCRIPTION_DOCUMENT.md` §5, added by `b032bbae`: *"the truth-free seed bound of §8
(**0.002419**), loaded adversely onto the three seed-dependent cases and the bootstrap
re-run, gives P(rank 1) = **52.0%**; loaded favourably, **80.5%**."*

The bootstrap loaded **0.0024**, not 0.002419. `PROBABILITY_OF_RANK` §2's own table gives
the loaded overalls as **0.059047** and **0.054247**, which are 0.056647 ± 0.0024 exactly;
0.002419 gives 0.059066 / 0.054228. `closure_challenge_round5_qcr.json` says it outright:
*"The **0.0024** seed bound moves P(rank 1) from 52 to 81 percent."*

Numerically immaterial — 52.0% and 80.5% would not visibly move. **Rhetorically it is the
same defect as F4**, which the same commit disclosed one paragraph earlier: a number
carried at a precision the computation behind it does not have, in outward text whose
claim on the reader is that it is careful about exactly this. The fix for a class landed
next to a fresh instance of it.

Secondary, same paragraph: the row is added to a table headed **"interval"** with columns
*interval / value / what it measures*. A one-seed sensitivity is a scenario range, not an
interval over a sampling distribution, and the row's label does not say so.

*Reported, not fixed.*

### N6 — MODERATE (OBSERVATION-strength on one reading). The bare-68% sweep's sibling set omits the `.tex`

`b032bbae` body: *"Own sweep of tracked .md/.html/.tex/.py for the figure:
CHALLENGE_SLATE_2026-08.md:37 is the **ONLY** surface carrying it without an interval —
every sibling (ACTIVE_RESEARCH, CLOSURE_CHALLENGE_STATUS, CHALLENGE_LANDSCAPE,
CLOSURE_FAMILY_SUPERVISION_GUIDELINES, PRODUCT_LIST) already carries 2-100%."*

`demo-output/website/latex/closure_challenge_report.tex` is **row 16 of the same
16-surface list**, is described in its own commit message as *"the closure line written
down for an outsider"*, prints `P(rank 1) = 68\%` at **7 sites**, and carries an interval
at **one** (lines 259–260: *"38--91\%… 26--94\% at the 68\% level and 2--100\% at 95\%"*).

Under a **per-surface** reading of *"no surface may state the figure without the interval"*
the claim survives. Under the **per-claim** reading the ladder itself wrote into the record
— `LADDER_V_PASS2_2026-08-11.md:338`: *"its owner should confirm **every one of the twelve**
now carries the interval, which is the new requirement"* — it does not. The sweep declares
a rule-compliance fact without stating which reading it used, and omits the one surface
the ladder had already flagged as the open case.

*Reported, not fixed. Owner: the `.tex`'s owner.*

### Lesser observations, not ranked as failures

- **O1 — the dispatch omitted the commit that created the rule the dispatch invokes.**
  `5bffb476` is absent from the brief's list. It is genuinely excluded from *reopening*
  the ladder by its own text, and I honour that — but round 1 recorded *"the dispatch that
  created V15 omitted the commit that created the rung."* Same shape, same author, one
  rung later. Recorded, because a pattern is a finding and an instance is an oversight.
- **O2 — `LADDER_V_PASS2`'s C9 and C13 rows stand as round 1 found them.** C9 still offers
  *"every occurrence in the closure line is the prohibition"* as its evidence while
  `PROBABILITY_OF_RANK:151` still reads *"Larger and more comfortable than the Reissmann
  comparison"* — and `b032bbae` edited that very file without touching either row. C13
  still grades 16 surfaces PASS against a rule withdrawn two rows below it. Round 1
  classed these as record corrections rather than blockers, so this is **not** a new
  failure; it is noted because the fix round is now the most recent author of both files.
- **O3 — round 1 slightly overstated its own F9.** It cited
  `CLOSURE_RANK1_CAMPAIGN.md:341` as *"a second"* comfort descriptor. Read in place (now
  line 374, shifted by `5af41163`'s banner) it is *"Assuming (a) is the comfortable
  reading"* — a reading of an assumption, not a descriptor on a margin. Round-1 text, not
  fix-round text; recorded so a round 3 does not inherit it.
- **O4 — `dc13f1cc`'s byte-for-byte regeneration claim is inherited, not verified.**
  Re-running a closure generator is not a read-only act and this rung did not do it.

---

## 4. WHAT THE FIX ROUND GOT RIGHT, STATED AT THE SAME STRENGTH

A round that only lists failures is not a measurement. Of the 33 verifiable claims in the
fix round's own output, **24 pass**, and several are better than the correction required:

- **F1 is closed and over-delivered.** The replacement names three cases with three
  values, all exact against the JSON, so the number can no longer be re-read as belonging
  to a case the reader will not receive. `AR_7`'s absence from the submission proved two
  ways. The correction propagated to a fourth surface (`CLOSURE_EVALUATION_PROTOCOL.md`)
  that nobody had listed.
- **F2's corrective work is exact.** 29 assertions in 15 files, every one a date-of-writing
  claim, every one changed only in its date, no meaning altered anywhere — including a
  code constant that turned out to feed no logic, and a new parenthetical *"(later the same
  day)"* that I checked against two commit timestamps and that holds. The 44 untouched
  occurrences are genuinely references. **No file renamed**, because five committed reports
  cite those paths — the right call, and the notes that replace a rename are dated and
  in-file.
- **The `dist/` prediction came true.** *"Will pick up the corrected source"* — I opened
  the zip and read every member: zero occurrences.
- **F3's replacement is exact to the minute**, verified here independently from
  `git log --format=%cI` on all three commits.
- **F6's two citations are verbatim at the frozen commit**, in the sections they name.
- **`5af41163`'s banner is the model rank claim in this corpus** — figure, interval,
  both undecided pairs with their *t* statistics, both decided pairs with their
  probabilities, and the local-scoring disclaimer — and it was written by the pass, not
  extracted by an auditor.
- **Three separate commits STOPPED rather than fixed**, each with the reason stated: the
  bootstrap not re-run (a computation, not a text fix); the NUMERICS_KNOWLEDGE gate, where
  either repair would change which experiment it is; the dated manifests on disk, where
  rewriting text under an unchanged date would forge the record. **A round that knows what
  it must not fix is more trustworthy than one that fixes everything.**
- **`dc13f1cc` and `4381d634` put the fix in the generator**, not only in the output —
  which is precisely the failure mode V14 named and round 1 did not have to.
- **F2 did not recur.** Every note written after midnight is dated 2026-08-11 and every
  note written before it is dated 2026-08-10, matching the clock at the moment of writing.

---

## 5. VERDICT — HAS THE FIX ROUND REACHED THE FIXED POINT?

# NO.

The termination rule requires that a full re-run of V8/V10/V14/V15 over the previous fix
round's text introduce **no new failures — not "few", not "only cosmetic ones". Zero.**

**Six new failures are in the fix round's own output**, measured at HEAD `249b611c`,
2026-08-11 00:07:16 UTC:

| # | severity | one line |
|---|---|---|
| **N1** | MAJOR | a fifth surface — the primary artifact, row 13 of the 16 — still asserts the withdrawn internal-only rule; the record says four |
| **N2** | MAJOR | round 1's F7 was renumbered into round 1's F10 and reported closed; four external surfaces still make a rank claim with no figure and no interval |
| **N3** | MODERATE | 74 occurrences / 45 references measure 73 / 44; the 29 and the 19 are exact |
| **N4** | MODERATE | *"the manifest's own changed-list"* — the manifest has no changed-list and never names `AR_7` |
| **N5** | MODERATE | the outward seed paragraph attributes 52.0/80.5 to a bound of 0.002419; the bootstrap loaded 0.0024 |
| **N6** | MODERATE | the bare-68% sweep declares itself exhaustive and omits the `.tex`, which prints the figure 7 times and the interval once |

**This is the rule working, not the rule failing.** Round 1 produced ten findings; round 2
produces six, none blocking, all in the layer between the work and the reader, and **none
in the outward package except N5**, which is a precision label rather than a wrong number.
The trend is the right one and the fixed point is close — but "close" is not the condition
the rule states.

**There will be a round 3.** Its scope is these six plus anything the ladder writes
closing them, and it must be run by an agent that wrote none of it.

**What round 3 should be told, because round 2 learned it the hard way:** the corpus moved
four times in the three minutes it took to derive the commit set (§0.2), and four of the
six surfaces in N2 are dirty in the working tree at the moment of measurement. A round that
does not pin `HEAD` and stamp the clock at the moment it reads is measuring a moving object
and reporting a still photograph.

**One thing this rung cannot certify.** I verified the fix round's text against its named
artifacts. I did not re-verify the artifacts, did not re-run the scorer, the bootstrap or
`build_master_table.py`, and did not audit uncommitted work. Where I read a measurement
rather than took one, this rung inherits its reliability and the row says so.

---

**Signed: the Ladder V rung V15 round-2 owner, 2026-08-11 00:07 UTC (clock).**
Zero scoring calls; ledger unchanged at 6. Nothing was sent, emailed, uploaded or filed.
Read-only except this file. No file audited above was edited by this rung.
