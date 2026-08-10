# Ladder V, Pass 2 — adversarial audit of the round-5 Closure Challenge entry

**Rungs V6, V7, V8, V9, V10. Executed 2026-08-10. Owner: the Pass-2 adversarial agent.**

> **Filename date note, added 2026-08-10 by the V15 corrections pass (finding F2).**
> This file is named `LADDER_V_PASS2_2026-08-11.md` and was written on **2026-08-10**
> (`date -u`; every commit of it carries a 2026-08-10 committer date). The filename is
> deliberately NOT renamed — committed reports cite this path. Read it as a label.

Brief: **assume the entry is wrong until it is defended.** I produced none of the
work below — not the pre-registration, not the solves, not the scoring call, not
the surfaces. I verified nothing I produced. Pass 1 (re-derivation,
`LADDER_V_RUNGS_V1_V3_V4_V5_2026-08-08.md`) and Pass 3 (cold reproduction,
`LADDER_V_PASS3_COLD_2026-08-11.md`) ran under other agents; I did not do their
rungs, and where I cite their measurements I say so.

**Scoring calls made by this pass: ZERO. The ledger stands at 6, unchanged.**
Every check below is static or arithmetic over numbers already on disk.
**Nothing was sent, emailed, uploaded or filed.** The submission package was
assembled and verified locally and stops there.

---

## 0. Frame, stated before any count

Three counts appear below and each is worthless without its frame, so here they
are:

- **"16 surfaces"** means: files in this repository containing the literal string
  `not statistically decided` **that make or assert a rank claim**. It excludes
  verification records that merely quote the rule. The raw grep returns more, and
  went from 16 to 17 *while this pass was running* because Pass 3 filed its
  report. See §5.
- **"count claims about scoring calls"** means: any sentence anywhere in code or
  records asserting *how many* scoring calls or distinct prediction sets this lab
  has made. It is not a search for the word "scoring".
- **"defects"** means findings I could demonstrate by running something or by
  displaying a byte, not findings I could argue for.

**A null result is a claim about my instrument before it is a claim about the
world.** Every negative below carries a positive control: I broke the thing on
purpose and confirmed the check noticed. Where I could not run a positive
control, I say the check is unverified rather than clean.

---

## 1. VERDICTS

| Rung | Verdict | One-line reason |
|---|---|---|
| **V6** — §4 compliance audit re-run against ROUND 5 | **PASS on the rule, FAIL on currency** | No rule violation anywhere, and the QCR path is the cleanest thing in the entry — but 3 of 9 findings do not describe round 5, and a live audit guard was failing the wall for being correct |
| **V7** — kill the two known defects | **PASS on both, and the count is three not two** | Defect (a) fixed and still true at the call sites; defect (b) artifact verified 8/8 with a positive control; **two further stale count claims found and fixed**; the chief's third blocking defect (no description document) discharged by writing one |
| **V8** — claims table, banned list, rank-claim rule | **FAIL — 8 failing claims** | The cover email would have announced **0.0654** over an attachment scoring **0.056647**; the round-5 leakage was undisclosed; four external surfaces claimed best-on-board 4 of 8 with no mention that two of the four are the organisers' own file |
| **V9** — prior-art completeness | **FAIL then FIXED** | `closure.html` shipped the **struck** sentence, crediting Ling & Templeton and Wu et al. with a control mechanism they never reported — to a readership that includes two of the benchmark's own authors. Firewall discharged as a dated fact |
| **V10** — cross-surface number sweep | **FAIL then PARTIALLY FIXED** | The sweep-count check is retired as unsound; the tracked shipping bundle `dist/certonomous-demo.zip` is a **round-3/4 fossil** and is reported, not fixed |

**Overall: the entry's substance survived every attack I could mount. Its
paperwork did not.** Nothing I found is a rule violation, nothing is a
withdrawal risk, and the score is real — Pass 3 reproduced it bit-for-bit. What
failed is the layer between the work and the reader, and it failed in the one
direction that matters: **the package would have been sent wrong.**

---

## 2. RUNG V6 — the §4 compliance audit, re-run against round 5

The existing audit (`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §4) predates QCR
entirely. Every finding gets a round-5 verdict.

| § | finding, as written | ROUND-5 VERDICT | evidence |
|---|---|---|---|
| 4.1 | the one strict rule: not violated | **HOLDS** — and now covers less ground, because 3 of 8 rows are forward solves with no fit at all | Ground-truth reads occur only inside `for case in gate._PH_TRAIN` (line 128) and `for c in ph._PH_TRAIN` (line 228); test loop at 178–180 is annotated `# no U_LES read`; asserts at `closure_baseline_error_gate.py:84–86`. Executed live by Pass 1 (V3), re-read statically here |
| 4.1 | *its line citations* | **STALE — reported, not edited** | The audit still cites lines 115 / 165–167 / 215. The body shifted +13 at `fe121af2`. Pass 1 re-anchored them in its own report and declined to edit Katie's package; I make the same call and record it twice so it is not lost a third time |
| 4.2 | the refused 0.0675 shortcut | **HOLDS, unchanged** | Round 5 changed no PH row |
| 4.3 | residual soft adaptive leakage (round 2) | **HOLDS — and is now INCOMPLETE, which is worse than stale** | Round 5 introduced a *second, larger* instance and §4.3 does not mention it. See §4, claim C7 |
| 4.4 | DEFECT 1, the false docstring | **RESOLVED and still true** | Docstring lines 37–53 state one *new* prediction set and four invocations; call sites verified at 218–219 (floor) and 301–302 (entry). Four invocations, two sets, one new — exactly as described |
| 4.5 | DEFECT 2, no submittable artifact | **RESOLVED for round 5** | 8 files, 1000×3, headerless, finite, flat layout, 8/8 SHA-256 match. See §3(b) |
| 4.6 | version label understates the metric revision | **HOLDS, and is discharged in the package** | `MANIFEST.json` carries `eval_package_version_string_note`; the new package README states it as an install hazard, because Pass 3 found that following the old advice can score you on a different metric |
| 4.7 | two of five best-on-board rows are the organisers' baseline | **HOLDS, count changed 5→4 of 8, and the disclosure was MISSING from four external surfaces** | Fixed — see §4, claim C4 |
| 4.7 | *the asymmetry argument* | **NEVER EXTENDED to the three QCR rows** | §4.7 reasons about credit for the *declined* rows. The same asymmetry now applies to the QCR rows: they are a published 25-year-old term any entrant may run, and the entry above us already runs it. Written into the new description document, §2 table and §6 |
| 4.8 | leaderboard position is current | **DATED, NOT RE-VERIFIED — and I did not verify it** | The claim rests on a local clone frozen at `deb91557` (2026-05-04, three months old). Re-verification needs a network read of the upstream README. I did not perform one: the frozen commit is load-bearing for V1 and V2, and this pass was instructed to touch nothing outward. **Every position claim in the corpus is dated to `deb91557`, which is the mitigation §4.8 itself prescribes** — so the claim is honest, but "current" is not a word this pass can certify |
| 4.9 | summary table | **SUPERSEDED** | Two of its eight rows now read wrong: "four official scoring calls" is six, "best on five of eight" is four of eight |

### 2b. QCR gets its own compliance line — the three questions, answered

| question | verdict | how I know, rather than who told me |
|---|---|---|
| **Used at solve time only?** | **YES** | `kOmegaSSTQCR` is an in-PDE constitutive term inside a converged SIMPLE solve. There is no post-hoc step: `closure_round5_qcr_forward.py` reads a converged `U`, interpolates to the evaluation points, and writes. No correction is added after the solve |
| **Touched any test data?** | **NO GROUND TRUTH — and this is the strongest single fact in the entry** | (i) Filesystem proof: `*_LES` truth files exist in **both** `AR_7_Ret_180` arms and in **none** of `AR_1_Ret_360_qcr`, `AR_3_Ret_360_qcr`, `AR_14_Ret_180_qcr`, though the benchmark ships one for each. **AR_7 having them is the positive control** — it proves my finder works, so the absence in the test arms is a measurement and not a blind spot. (ii) The script arms raising stubs over all nine scoring/truth entry points *and proves the guard is armed* by calling `score_from_csv` and catching the refusal before continuing. (iii) Evaluation coordinates come from the benchmark's shipped `data/evaluation_points/{case}_points.csv`, plain coordinate CSVs — the truth dict is never opened. (iv) The gate was decided on `AR_7_Ret_180`, which the benchmark README lists as the DUCT **validation (suggested)** case; the three test ducts are its Test column. Test *meshes* are used, which the task requires |
| **Zero fitted parameters?** | **YES** | The only coefficient is `Ccr1 = 0.3`, Spalart (2000)'s published constant. Pass 1 (V5) proved authorship in-house at `303247bb` with a matching `.so` hash; Pass 3 verified the compiled default is 0.3 with no case-dictionary override |
| **Stated in the description?** | **WAS NOT — there was no description.** Now yes | See §3(c) |

### 2c. A live audit guard was failing the wall for being CORRECT

Not in the brief, found by grepping for count claims, and the most dangerous
single thing in this pass because it is a *guard*.

`scripts/self_audit.py::check_closure_entry_of_record` was pinned to the
**round-3** entry file. Run live, before any edit:

```
FAIL — 'our_score: wall says 0.0566, the entry of record scores 0.0676'
```

**The wall was right and the auditor was wrong.** A guard that cries wolf is
worse than no guard, because the cheapest way to silence it is to "fix" the
surface that was correct — and the surface it was pointing at is the public
credentials wall. It also carried two stale count claims *inside its own error
messages*: "the record documents four official calls (floor, round 1, round 2,
round 3)" (it is six) and "round 3 records five of eight" (round 5 records four).

**Fixed**: re-pinned to `closure_challenge_round5_qcr.json`; the score comparison
now happens at the wall's own published precision, because the wall publishes
0.0566 and the record now carries 0.056647191704213645 and an exact-equality test
fails a correct wall for rounding; both count claims corrected; and a **new**
check added that fails the wall if it states best-on-board 4 of 8 without the
baseline disclosure.

**Four positive controls, all fired** (each injected into a copy of the wall,
then reverted byte-for-byte):

| injected fault | detected? |
|---|---|
| `our_score` → 0.0676 | **YES** |
| "four of the eight" → "five of the eight" | **YES** |
| "six pre-registered scoring calls" → "in a single scoring call" | **YES** |
| baseline disclosure clause stripped | **YES — on the second attempt** |

The fourth is worth recording as a finding about method rather than about the
code. My first version of that check used `best.{0,30}four of the eight` and the
control **did not fire**: the real sentence has 34 characters between the two
anchors. Had I not run the control I would have reported a passing check that
could never fail. **This is why negatives get controls.**

---

## 3. RUNG V7 — the known defects, killed and proven

### (a) The scoring-call count claims — full reconciliation

Ledger: **6 cumulative** distinct prediction sets scored (floor, rounds 1–5).
Frame: I grepped code *and* records for any assertion of a count, not for the
word "scoring".

| site | claim | reconciliation | action |
|---|---|---|---|
| `apply_closure_ph_gate.py:37–53` | 4th call, four invocations, two sets | **TRUE of round 3 and correctly scoped.** Call sites verified: `score`/`evaluate_by_case` on the floor at 218–219, on the entry at 301–302 | none — this is the original defect, and it is properly dead |
| `closure_round4_duct_rescale.py:38–40` | "official call #5" | true of round 4, scoped | none |
| `closure_criterion_on_test_features.py:10, 47, 96, 221, 272` | "a 5th official call", "round-2 single official call" | historical/round-3 tense; asserts nothing about the current count | none |
| `closure_round4_manifest.py:135` | "five … as of this round-4 manifest" | already scoped by rung V7 on 2026-08-08 | none |
| `export_closure_submission_csvs.py:25` | round-3 quote, dated | already scoped 2026-08-08 | none |
| `build_benchmarks.py:19–21, 94–108` | "six pre-registered scoring calls", 0.0566 | correct since 2026-08-08 | none |
| `test_mega_batch.py:247` | "the sixth pre-registered scoring call" | consistent | none |
| **`closure_round5_qcr_forward.py:26–28`** | **"the ledger stays at 5 distinct prediction sets scored"** | **TRUE of its own run, FALSE as standing text.** The 2026-08-08 pass reconciled this as "true: that script made no call" and left it. Adversarially that is the wrong test: the sentence is in the present tense with no date on it, which is the *exact defect shape* of the original §4.4 docstring and of the "five … ever" claim that the same pass did fix two files away. Inconsistent treatment of one defect class | **FIXED** — scoped to the script's own run, with the current cumulative six stated |
| **`scripts/self_audit.py:309`** | **"the record documents four official calls"** | **FALSE as standing text** — and it is inside the error message of a live guard, so it would have mis-directed whoever acted on it | **FIXED** |
| **`scripts/self_audit.py:313`** | **"round 3 records five of eight"** | **FALSE** — round 5 records four of eight | **FIXED** |

**Verdict: the original defect is dead and stayed dead; two further live false
count claims are now dead too.**

### (b) The submittable artifact, verified against an accepted submission

Benchmark checkout `/home/ubuntu/closure-challenge-benchmark` @ `deb91557`
(`git log -1` confirmed). Two accepted layouts exist: flat `{case}.csv` (wu,
montoya, wang) and per-case `{case}/predictions.csv` (reissmann). Ours is flat —
an accepted layout, and the one the eval loader expects.

Measured on disk, all eight files:

- **8 files, 1000 rows × 3 columns, comma-delimited, no header** (first row
  float-parses), **all values finite**;
- **8 of 8 SHA-256 match `MANIFEST.json`**, which matches the pre-registration
  §3 table frozen at `e865076b` **before** the scoring call at `07a7fe9e`;
- the five non-duct CSVs are **byte-identical to round 4** (`filecmp`), and the
  three duct CSVs are **not** — exactly the split the record claims;
- **magnitude band check, extended to round 5's three new duct files** (the
  earlier check covered round 3): mean velocity magnitude sits **inside** the
  band spanned by all four accepted submissions on all three ducts —
  `AR_1` 35.36 ∈ [33.77, 35.73], `AR_3` 41.55 ∈ [39.43, 41.92],
  `AR_14` 21.95 ∈ [21.74, 22.18].

**Positive control on that last check**, because a band test that always passes
is not a test: rolling our own columns by one on `AR_1_Ret_360` moves the primary
column mean from 35.36 to −0.079 and is **DETECTED on all three columns**. The
instrument sees a column swap.

**One honest imperfection, reported rather than buried.** Two *transverse*
column means sit fractionally outside the entrants' spread — `AR_1` column 2 by
2×10⁻⁵ and `AR_14` column 3 by 7.5×10⁻⁴, on quantities of order 10⁻². These are
secondary-flow components on which independent solves legitimately differ, and
they are three orders of magnitude smaller than the 35-unit displacement a real
column error produces. Not a format defect; recorded so nobody rediscovers it and
thinks it was hidden.

### (c) The third blocking defect — the description document did not exist

§5.1 of the package says it would contain *"a description document (following
wu's precedent), containing §5.3 and §5.4"*. **§5.3 is a specification of what a
description document must disclose. It is not one.** I searched the tree: the
only description document present is
`docs/papers/wu_zhang_sst_qcrc_challenge_description.pdf` — a **competitor's**,
held as the format precedent. This is the same defect class the package closed
one level down for the CSVs in July ("the entry of record is currently a number,
not a submission"), recurring one level up.

**Discharged**: `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`
now exists and carries every §5.3 disclosure updated to round 5, the round-5
leakage disclosure at full strength (§4, C7), the split prior art verbatim, the
Buchanan firewall as a dated fact, the probability figure with its interval, and
the two steward questions.

**Also discharged**, from Pass 3's D1/D4/D10:
`closure_challenge_submission_round5/README.md` — names the package, gives both
repository URLs with both pinned commits, the install-hazard note, the expected
score to full precision, and a working integrity command. **I executed that
command verbatim as written: 8 of 8 OK.** A package instruction that has never
been run is a guess.

### Hand-off block — what needs Katie, with nothing invented

| item | where | status |
|---|---|---|
| Author names + affiliation form | `DESCRIPTION_DOCUMENT.md` header | `[KATIE TO FILL]` — and the question of whether a company name is acceptable is question 1 to the steward |
| Reference / repository URL | `DESCRIPTION_DOCUMENT.md` header | `[KATIE TO FILL]` |
| Rewrite of §5.2 / §5.3 / §5.4 in the draft | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` | **NOT DONE — Katie's package.** Blocking banner added instead; the new description document supersedes §5.3 in substance |
| §5.6 items 6 and 7 | the draft | OUTSTANDING, as they have been since 2026-08-02 |

---

## 4. RUNG V8 — the claims table

Every quantitative sentence in the cover material → the named artifact that
supports it → verdict. **8 FAIL, 3 INCOMPLETE, 6 PASS.**

| # | claim, and where it is made | named artifact | verdict |
|---|---|---|---|
| **C1** | §5.4 cover email, subject line and body: **"overall 0.0654"** | `closure_challenge_trained_entry_round4_duct.json` — **the round-4 entry** | **FAIL, and this is the worst finding in the pass.** The attachment is the round-5 CSVs, which score **0.056647**. The email would have announced a number that is not the attachment's number. The steward rescores, gets a different figure than the letter claims, and the first impression of an entry built entirely on precise self-accounting is an arithmetic contradiction — self-inflicted, from an unexecuted instruction in §10 |
| **C2** | §5.1: CSVs at `closure_challenge_submission/test/` | the round-**3** directory | **FAIL — wrong directory.** Round 5 ships from `closure_challenge_submission_round5/test/` |
| **C3** | §5.2: per-case row, "improvement −0.0382, 36.9% below floor" | round-4 record | **FAIL — every row stale.** Round 5: ducts 0.0455 / 0.0400 / 0.0353, improvement **−0.0470, 45.3%** below the 0.1036 floor (verified: 0.1036 → 0.056647) |
| **C4** | **"Best result on the public board on four of the eight test cases"** — `benchmarks.json`, `wall/wall.json`, `build_benchmarks.py`, and a **hero KPI tile** on `benchmarks.html` reading *"4 of 8 — better than every published entry"* | §0f of `CLOSURE_CHALLENGE_STATUS.md` | **FAIL on the banned list — a best-on-board count leaning on organiser-baseline rows.** Two of the four (`alpha_05_4071_4048`, `alpha_05_4071_2024`) **are the organisers' own unmodified RANS field**. §4.7 calls this the highest-priority disclosure and says the exposure is *asymmetric* — discovery is far more damaging than disclosure. It was on none of the four surfaces. **FIXED on all four**, generator and both JSONs re-verified key-by-key in sync |
| **C5** | §5.3 item 7: **"four distinct prediction sets scored"** | the ledger | **FAIL — six.** A scoring-call count claim in the disclosure list: the exact defect class §4.4 exists for, surviving in the document that raises it |
| **C6** | §5.3 items 6, 8, 9 | round-4 records | **FAIL — 3 of 9 disclosures do not describe the attached files** (Pass 3, D5). Item 6 describes an ML duct model no longer in the entry; item 8 states `∇·U` of 2.3–3.4% on the ducts when the round-5 measured `rms div/rms grad` is **5.3×10⁻⁴ – 8.5×10⁻⁴** (an overstatement *against* the entrant); item 9 anchors the seed bound to "the 0.0030 gap to rank 2" when the operative comparison is a 0.00289 margin over rank 1. All three corrected in the new description document — and item 7 there states the **measured** numbers rather than "satisfies continuity by construction", because 8.5 / 5.3 / 5.4 ×10⁻⁴ are not machine zero. *[Corrected 2026-08-10 by the V15 corrections pass, finding F1: this row originally read "because 5.8×10⁻⁴ is not machine zero". 5.8×10⁻⁴ is `/arms/AR_7_Ret_180_qcr` in `closure_challenge_round5_qcr_forward.json` — the validation-gate duct, which is not in the submission (`what_ships/changed` = AR_1_Ret_360, AR_3_Ret_360, AR_14_Ret_180). The submitted three measure 0.00085136 / 0.00052808 / 0.00054396.]* |
| **C7** | §5.3 discloses the round-2 leakage **only** | `campaign/R5_RULE_FREEZE.md` @ `0bade54a` | **FAIL — the most serious disclosure gap in the package.** The round-5 route was chosen **while the per-case test scores were known**: the whole −0.0088 move, and the entire reason a rank claim exists, was selected in knowledge of test outcomes. `R5_RULE_FREEZE.md` concedes it in the lab's own words — *"we already know the round-4 test-duct scores … Every degree of freedom in that choice is therefore closed here, in writing, before any new number exists"* — and then closes them. **That sentence is the entry's single best asset and it lives in a file that does not travel.** A reviewer who finds it after reading a disclosure list that omitted it discounts everything else the list says. **FIXED**: written into `DESCRIPTION_DOCUMENT.md` as disclosure 3b, at full strength, with the mitigations listed *after* the admission and explicitly not offered as cancelling it |
| **C8** | §5.2 / §0f: **"Reissmann's published 0.059525"** | the benchmark README | **FAIL on the word "published".** The README publishes **0.0595**, four decimals. 0.059525 is the mean of eight *rounded* per-case values — not a number anyone published, and not reproducible from the source it names. Pass 3's like-for-like full-precision re-score gives **0.0595338**, margin **0.0028863**. The error runs *against* the entry by 8×10⁻⁶. Corrected and explained in the new description document, §5 |
| **C9** | AR_14 lead of 0.00003 | round-4 record | **PASS.** Swept the corpus for "comfortab*": every occurrence in the closure line is the **prohibition** ("must not be reported as a comfortable win"). No surface claims a comfortable AR_14 lead. §0f, `PRODUCT_LIST` §4B and `ACTIVE_RESEARCH` all record the tie as **lost** |
| **C10** | any novelty claim on gated correction | §7.4 | **PASS.** No surface claims it. The only occurrences of "novel" are `is not novel` and the prohibition itself |
| **C11** | official-rank language | — | **PASS, and the corpus is disciplined about it.** 24 hits swept; every one is a *disclaimer* ("local scoring, not an official placement"). `closure.html` states it hardest: *"holds no official rank"*. One hit reads "leaderboard rank 1" of **Reissmann**, which is a true statement about the published board and is on the audited false-positive list |
| **C12** | soft-adaptive-leakage disclosure in the lab's own words | round-3 JSON `leakage_statement` | **PASS for rounds 1–3** — the verbatim *"That is soft, adaptive leakage, and it is real"* is carried. **See C7 for round 5** |
| **C13** | rank claim carries P(rank 1), interval, and named not-decided pairs | `campaign/PROBABILITY_OF_RANK_2026-08-10.md` | **PASS on all 16 claim-bearing surfaces.** Each names Reissmann and Wu & Zhang as undecided (t = −0.495, −0.953) and Liu and Montoya as decided (98.7%, 99.8%); each carries the literal token |
| **C14** | the internal/external split on the figure | chief ruling | **WITHDRAWN 2026-08-10, and the reversal is right.** Pass 3 computed **0.674 from public data in about a minute**. A figure an outsider reproduces trivially is not protected by being withheld — it only looks concealed, to exactly the reader the disclosure strategy exists to convince. **The figure now travels with the entry.** Recorded in `PROBABILITY_OF_RANK` (banner + amended propagation rule), `LADDER_V_TRIPLE_VERIFICATION` (V8 amendment) and the new description document. **One new prohibition replaces the split: no surface may state the figure without its interval** — a bare 68% is a worse claim than none, because 68% sounds settled and 2–100% is what eight cases support |
| **C15** | §4.7's asymmetry argument | §4.7 | **INCOMPLETE — never extended to the three QCR rows.** §4.7 reasons about credit for the *declined* rows only. The same asymmetry now applies to the ducts: a published 25-year-old term any entrant may run, which the entry above us already runs, and whose scores land within 0.0004 of theirs. Written into the description document's §2 table and §6 |
| **C16** | the seed bound against the margin | `closure_challenge_stability_physicality_audit.md` §1 | **INCOMPLETE → now quantified.** Against the like-for-like margin the bound of **0.002419 covers 84%** (0.002419 / 0.0028863 = 0.838). I verified this arithmetic rather than inheriting it: with the *rounded* 0.0024 it computes to 83.1–83.4%, so the 84% figure is correct **only** with the unrounded bound, and the description document states both unrounded |
| **C17** | *(an asset, not a defect)* on the two declined cases the supplied baseline beats **all four** published entries | §0f, independently verified by Pass 3 | **PASS, and it should be stated as what it is.** This is a finding about the benchmark — every entrant made those two cases worse by touching them — and it does not depend on our score at all. It is stated in the description document as a property of the benchmark, deliberately *not* folded into our result |

### One defect this pass created and then caught

Writing the blocking banner into the submission draft, I typed the probability
figure into a sentence *forbidding* the probability figure in that document. My
own leak sweep caught it on the next pass and it was removed before any commit.
Recorded because it argues for the mechanism: the rule was violated by the person
writing the rule down, inside the act of writing it down, and only a mechanical
check noticed. *(The chief's reversal has since made the figure publishable
anyway — but the sequence stands as evidence about the check, not about the
number.)*

---

## 5. RUNG V9 — prior-art completeness

### (a) The identify-vs-control split — FAIL on the external page, now fixed

The 2026-08-05 correction (`d84b649f`) struck a sentence for *"rolling two
established things into one and crediting two of the four with a mechanism they
did not report"*, and mandated the split wording. **`closure.html` was still
shipping the struck sentence**, nearly verbatim:

> *"A classifier that reads only the uncorrected solve **and controls where** a
> data-driven correction is allowed to act has been published repeatedly — Ling
> and Templeton in 2015, Wu, Wang, Xiao and Ling in 2017, Steiner… Buchanan…"*

Ling & Templeton control nothing — they classify point by point. Wu et al. is an
*a priori* confidence measure. **The page credited both with a mechanism neither
reported, to a readership that includes two of this benchmark's own authors.**
The `.tex` had carried the split correctly since `d84b649f`; the public page had
not. Ten months of "we checked our prior art properly" resting on a sentence that
misattributes it.

**FIXED**: `closure.html` now carries the split verbatim — *identify* (Ling &
Templeton 2015, Wu et al. 2017) and *control* (Steiner et al. 2022, Buchanan et
al. 2025) — named separately. Carried into the new description document, §4.

### (b) The Buchanan firewall, discharged as a compliance FACT

§7.4 states a **prohibition**, written before the pull was felt. It had never
been discharged as a *fact*. Now it is, in `CLOSURE_CHALLENGE_PRIOR_ART.md` §2.4,
**as a chronology**, because chronology is the only form of this claim that cannot
be argued with:

| fact | evidence |
|---|---|
| the shipped `NASA_2DWMH` prediction is byte-identical across rounds 3, 4 and 5 | `filecmp` against round 4: identical; §0f records Δ = 0 |
| it was written **before** the paper was mentioned in this repository at all | CSV last moved at `fe121af2` (2026-07-31T06:53Z); first commit anywhere containing `2504.06758` is `92840d8c` (2026-07-31T23:13Z) — **16 h later**, and abstract-only |
| it was written **three days before** the paper was read in full | full text read at `15530f97` (2026-08-02T05:30Z), whose subject line records the outcome: *"reading it closes a route rather than opening one"* |
| no Appendix-D coefficient or artifact exists in any executable file | `grep -rniE "buchanan\|RITA\|2504\.06758\|lacatus"` returns **zero hits in executable files**; the three apparent code hits are substring matches inside *autho**rita**tive* |
| the round-5 duct change carries nothing from it | the only new coefficient is `Ccr1 = 0.3`, Spalart's published constant (Pass 1, V5, `303247bb`) |

### (c) The warm-start check — one use found, and it is disclosed rather than denied

`closure_challenge_C6_hump_decision.md` **does** cite that paper on the hump — for
the hump's Reynolds number (Re_h = 9.3×10⁵, their §2.4 / Table 2).

Adversarially examined and reported rather than waved off: this is a **property
of the benchmark's own test case**, not a coefficient and not an output of their
model; it was used to argue that CBFS is *not* a close donor, i.e. to **close**
Route B, which was then withdrawn; and nothing from it entered any submitted
field, because the hump prediction it concerned is the same bytes it was three
days before the paper was opened. **Verdict: the firewall holds, and it holds by
date rather than by assurance.**

---

## 6. RUNG V10 — cross-surface number sweep

Numbers checked on every surface: 0.0566 / 0.056647; rank 1 of 5 **scored
locally** at `deb91557`; six scoring calls; AR_14 tie **lost**; best-on-board
**4 of 8** *and its baseline qualification*; seed bound vs margin; untrained QCR.

| surface | verdict |
|---|---|
| `closure.html` | **FAIL → FIXED** — numbers were consistent, but the **prior-art paragraph** shipped the struck misattribution (§5a) |
| `benchmarks.html` | **FAIL → FIXED** — hero KPI *"4 of 8 · better than every published entry"* with no baseline qualification |
| `benchmarks.json`, `wall/wall.json` | **FAIL → FIXED** — same bare count in `our_entry` |
| `sdk/scripts/build_benchmarks.py` | **FAIL → FIXED** — the generator's literal, fixed in the same commit per its own KEEP-IN-SYNC rule; **re-verified key-by-key that the literal reproduces the on-disk `benchmarks.json` block exactly, and that `wall.json`'s string is identical** |
| `ACTIVE_RESEARCH.md` | **PASS** — round-5 current, token and figure present. One observation, not a fail: line 612's *"Best-on-board 5 of 8, unchanged"* sits inside the round-4 block, which line 594 correctly marks superseded by round 5 |
| `CLOSURE_CHALLENGE_STATUS.md` §0f | **PASS** — the most complete surface in the corpus |
| `wall/wall.html` | **PASS** — renders `wall.json`, no literal of its own |
| `docs/PRODUCT_LIST.md` (**READ-ONLY — chief-owned, not edited**) | **PASS, and better than at last report.** Round-5 current, token, figure, AR_14 correction, and it already carries the baseline disclosure. **Both stale notes reported by the 2026-08-08 sweep have been cleared.** One trivial observation: §4B cites `b2aa6887` for the propagation while `PROBABILITY_OF_RANK` §7 cites `a57d8d3b`; both are defensible (source-of-ruling vs this-file's-edit) and **no action is requested** |
| `latex/closure_challenge_report.tex` (owner: its Opus writer — NOT EDITED) | **PASS on numbers and prior art**, and it carried the identify/control split correctly while the public page did not. **One risk raised, not fixed:** its own commit message calls it *"the closure line written down for an outsider"* and it prints the probability figure at twelve sites. Under the old gate that was a standing hazard; under the 2026-08-10 reversal it is no longer a breach — but its owner should confirm every one of the twelve now carries the interval, which is the new requirement |
| **`dist/certonomous-demo.zip`** (**TRACKED, and it ships**) | **FAIL — reported, NOT fixed.** The tracked bundle, committed `c83c7240` on 2026-08-01, contains `site/closure.html` and `site/benchmarks.html` carrying **0.0654 and 0.0676**, zero caveats, zero sweep token. `dist/certonomous-demo/` is gitignored, so the `.zip` is the artifact of record. The propagation rule says *"anything shipping in `dist/`"* — this is literally that, and **no V10 surface list has ever included it.** Rebuilding a demo bundle is not this pass's call; **raised to the chief** |
| `closure_challenge_submission_round5/` | **FAIL → FIXED** — package had no README and no description document (§3c). Both now exist; the README's integrity command was executed verbatim, 8/8 OK |

### The sweep-count check is unsound and is retired

The brief expected 15 files. **The raw grep returned 16 at the start of this
sweep and 17 before it finished.**

- **16th**: `latex/closure_challenge_report.tex`, tokened at `15f2921a`
  (2026-08-10T16:23:32Z) — **21 minutes after** `a57d8d3b`, the commit
  `PROBABILITY_OF_RANK` §7 cites as the last propagation. §7 lists the `.tex`
  under *"routed elsewhere"*; its owner then did the work, and the table was
  already one short when it was written down. **A routed surface is not an
  excluded surface — it is a surface whose owner differs.**
- **17th**: `campaign/LADDER_V_PASS3_COLD_2026-08-11.md`, written by a
  concurrently-running pass while this sweep was in progress. This report makes 18.

**A check of the form "the count must equal N" now fails every time the ladder
does its job.** Replaced, in `PROBABILITY_OF_RANK` §7, with the invariant the
count was always a proxy for:

1. no claim-bearing surface makes a rank claim without the token — **all 16
   re-read, not counted: holds**;
2. no file carries the token where "rank 1" does not mean our standing — the 14
   audited false positives stay untokened: **holds**;
3. ~~no external surface carries the figure~~ → **no surface carries the figure
   without its interval** (the 2026-08-10 reversal).

Measured before the reversal and kept as the record of the gate's final state:
the six external surfaces carried the token and **zero** instances of the figure;
the ten internal ones carried both. Under the new rule those six are
*under*-disclosed rather than correctly gated, which is a follow-on item and not a
defect of this sweep. **Positive control on the leak detector**: a seeded copy of
`closure.html` with the figure appended was **DETECTED**.

---

## 7. Everything this pass changed

| file | change |
|---|---|
| `demo-output/website/closure.html` | prior-art paragraph rewritten to the mandated identify-vs-control split (**V9**) |
| `demo-output/website/benchmarks.html` | hero KPI tile "4 of 8" gains the organiser-baseline qualification (**V8 C4**) |
| `demo-output/website/benchmarks.json` | same qualification in `our_entry` |
| `demo-output/website/wall/wall.json` | same qualification in `our_entry` |
| `sdk/scripts/build_benchmarks.py` | same in the `_CLOSURE` literal; re-verified key-by-key against both JSONs |
| `scripts/self_audit.py` | closure guard re-pinned round 3 → round 5; precision-aware score comparison; two stale count claims fixed; new baseline-disclosure check; four positive controls pass |
| `sdk/scripts/closure_round5_qcr_forward.py` | "the ledger stays at 5" scoped to its own run; cumulative six stated |
| `demo-output/website/CLOSURE_CHALLENGE_PRIOR_ART.md` | §2.4 gains the firewall discharged as a dated compliance fact, plus the one disclosed use |
| `demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` | blocking banner at §5 — **no claim of Katie's rewritten**, the mismatch made impossible to proofread past |
| `demo-output/website/campaign/PROBABILITY_OF_RANK_2026-08-10.md` | internal-only gate withdrawn (banner + amended propagation rule); §7 count corrected 15 → 16 with the `.tex` and its history; bare-integer check retired for the three invariants |
| `demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md` | V8 amendment recording the withdrawal of the internal/external split |
| **`…/closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`** | **NEW** — the package's missing required artifact |
| **`…/closure_challenge_submission_round5/README.md`** | **NEW** — where the benchmark and scorer are, how to install and score, integrity command (executed, 8/8 OK) |
| `demo-output/website/campaign/LADDER_V_PASS2_2026-08-11.md` | this report |

**Not touched, deliberately:** `docs/PRODUCT_LIST.md` (chief's, read-only for this
rung), `latex/closure_challenge_report.tex` (its Opus writer's),
`dist/certonomous-demo.zip` (raised, not rebuilt), the frozen `R5_*`
pre-registrations and rule freeze (editing them would falsify the chain V2
passed on), everything in `/home/ubuntu/closure-challenge-benchmark`, all
historical round-1–4 JSONs, and **the scorer, which was never invoked**.

---

## 8. What this pass could not do, stated as limits rather than omitted

- **§4.8's "position is current" is not certified.** It rests on a clone frozen
  three months ago. Certifying it needs a network read; this pass was instructed
  to touch nothing outward and the frozen commit is load-bearing for V1/V2.
- **`.tex` and `PRODUCT_LIST` were audited, not edited** — other owners.
- **The cover email was not rewritten** — Katie's, and items 6 and 7 of §5.6 are
  hers. It is banner-blocked instead.
- **I did not re-score anything**, including the like-for-like Reissmann re-score
  behind claim C8. That number is Pass 3's measurement, cited as theirs; I
  verified only the arithmetic that follows from it (margin 0.0028863, seed bound
  covering 84%), and I checked that the 84% requires the unrounded 0.002419
  before repeating it.

---

## 9. The one-paragraph verdict

**The entry is defensible and the paperwork was not.** I attacked the rule
compliance and it held everywhere — the leakage assertions, the train-only gate,
the untrained duct term, the frozen rule that cost a real tie and was honoured
when it did. I attacked the artifact and it is correctly formed, hash-matched,
and inside every sanity band with a positive control to prove the band can
fail. What broke was everything between the work and the reader: a cover letter
two rounds stale that would have announced the wrong score over the right files,
a required description document that did not exist, the largest leakage in the
entry's history disclosed only in a file that does not travel, a best-on-board
count on four public surfaces that quietly leaned on the organisers' own
baseline, a prior-art sentence on the public page crediting two papers with a
mechanism they never reported, and a live audit guard failing the wall for being
correct. **Nine of those are now fixed; three are reported to their owners; two
await Katie.** The send gate stays shut.

---

**Signed: the Ladder V Pass-2 owner (adversarial), 2026-08-10.**
Rungs V6, V7, V8, V9, V10 executed. Zero scoring calls; ledger unchanged at 6.
Nothing was sent.
