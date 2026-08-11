# Ladder V — rung V8 re-verification, 2026-08-11

**Verdict: V8 FAILS — 3 failing claims, 2 minor, on current state.**

Owner: an agent that wrote none of the graded text. Grading is against primary
artifacts only; where the rewrite's own report is cited it is cited as a *claim under
test*, never as evidence.

---

## 0. FRAME, stated before any count

| item | value |
|---|---|
| clock at start of this pass | **2026-08-11 02:13:15 UTC** (`date -u`, run before anything else) |
| repository HEAD when graded | `174e52bd` (2026-08-11 02:12:46 +0000) |
| working tree | clean except `sdk/.filming-keepalive` (M) and three untracked `campaign/F6b_runs/log.*` — none in the graded set |
| graded surfaces | `demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` **§5 banner + §5.1–§5.4** (lines 552–962; the only cover email in the tree), `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md` (374 lines), `closure_challenge_submission_round5/README.md` (93 lines) |
| state of graded files | draft at `e87650db` (2026-08-11 01:37:19Z), description document at `fdb1ec5c` (01:41:00Z), README at `9477a2ed` (2026-08-10 21:35Z) |
| tooling | `/bin/grep` throughout, never the ignore-honouring wrapper |

**What this frame structurally cannot contain.** Three files. It does not reach
`closure.html`, `benchmarks.*`, `wall/`, `dist/certonomous-demo.zip`, `docs/PRODUCT_LIST.md`,
`latex/closure_challenge_report.tex`, or §1–§4 and §6–§10 of the submission draft. Those
are V10's and V14's rungs. A defect on any of them is invisible to this pass, and one
adjacent finding I tripped over in §10 is recorded in §6 below rather than silently kept.

### Instruments, and the positive control for each

1. **Independent re-score.** The benchmark's own unmodified scorer, loaded from
   `/home/ubuntu/closure-challenge-pkg/src` by `sys.path` (no `pip install`, no edit),
   `git log -1` = `1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162`; dataset at
   `/home/ubuntu/closure-challenge-benchmark`, `git log -1` =
   `deb91557184af3cb95f5190494ec52d8f2c6a0d1`. **Positive control:** the same instrument,
   in the same run, returned `0.056647191704213645` for the package's own `test/`
   directory and reproduced all four published board overalls to the README's four
   decimals. An instrument that returns the known answer on known inputs is not
   returning silence.
2. **Wrapped-token detector** (for `not statistically decided`): per-line count
   `/bin/grep -c` compared against whole-text count `tr '\n' ' ' | /bin/grep -o | wc -l`.
   **Positive control:** a scratch file containing one occurrence broken across a newline
   and one clean occurrence returned **1 per-line vs 2 whole-text**. The instrument can
   see a wrap. On all three graded files the two counts are **equal**, so the absence of
   a wrap is a measured absence, not an untested one.
3. **Banner-verbatim check:** byte `diff` of the kept banner against
   `git show e87650db^:…CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`. `diff` cannot report
   "identical" for differing bytes; its exit code was read.
4. **Package integrity:** SHA-256 of each shipped CSV recomputed and compared to
   `MANIFEST.json` — **8 of 8 match**; row/column shape read off disk — **8 × (1000 × 3)**.

---

## 1. THE VERDICT

**V8 FAILS.** The rewritten cover email is a large improvement and closes all six defects
it set out to close — each verified closed, not merely edited (§2). It fails on three
claims, one of which is in the document that leaves the building:

| # | failure | where | severity |
|---|---|---|---|
| **F1** | **Wu & Zhang called "the rank-3 entry."** The published board at `deb91557` — the board the same document cites — lists them at **rank 2**. Rank 3 is Liu, Wang, Zhao & Xiao. The lab's own source record for this exact sentence (`closure_challenge_round5_qcr.json` → `qcr_vs_rank2_duct_consistency`) says *"The **rank-2** entry (Wu & Zhang) runs SST-QCRC…"* | `DESCRIPTION_DOCUMENT.md:54` — **travels with the entry** | **BLOCKING** |
| **F2** | **A live defect flagged in a file that no longer has it.** Two sentences assert that `DESCRIPTION_DOCUMENT.md` §5 prints the misrounded `0.0595338` and *"owes a one-digit correction there."* It was corrected by `fdb1ec5c` at 01:41Z, four minutes after the sentences were written. The travelling document now reads `0.0595335` in both places | draft `:576–578` (discharge banner) and `:677–679` (§5.2) | HIGH |
| **F3** | **"Reissmann's four published CSV directories."** Reissmann's submission is **eight** case directories, each holding one `predictions.csv`; the re-score that produced `0.05953352830400628` necessarily read all eight — I reproduced it that way. `fdb1ec5c`'s own commit message says "eight", so the lab's records disagree with each other | draft `:571` (discharge banner) | MEDIUM |
| **F4** | **"Kept verbatim" is true of the table and false of the headline.** The 2026-08-10 banner's own heading — *"⛔ BLOCKING BANNER — §5 IS ROUND-4 TEXT AND MUST NOT BE SENT AS IT STANDS"* — was replaced by *"⛔ THE BANNER AS WRITTEN 2026-08-10, KEPT AS THE RECORD"* and demoted `##` → `###`. **Everything else, including the entire ten-row defect table, is byte-identical** | draft `:582` | LOW |
| **F5** | **One number attributed to a plural set.** *"A like-for-like full-precision re-score of **the accepted submissions** … gives 0.0595335"* — that is Reissmann's value alone. The four accepted submissions re-score to 0.0595335 / 0.0624234 / 0.0737080 / 0.0778678 | `DESCRIPTION_DOCUMENT.md:278–279` | LOW |

**F1 is why this is a FAIL rather than a PASS with notes.** It is in the travelling
document, addressed to the steward who maintains the board it misstates; it is wrong in
the direction that flatters us; and because "rank 3" is only true in a five-way list that
inserts our *unsubmitted* entry at the top, it is also a rank claim for ourselves made in
§2 — carrying no P(rank 1), no interval, and no not-decided pairs, three sections before
the ones that do. Under the V8 amendment of 2026-08-10 a placement stated without those is
a rung failure on its own.

---

## 2. THE SIX DEFECTS THE REWRITE CLAIMS TO HAVE CLOSED — verified closed, not edited

Each re-derived from a primary artifact. None of these verdicts was taken from the
rewriter's report.

| defect | what the text now says | primary artifact | closed? |
|---|---|---|---|
| the score | subject line and body: **0.056647**; §5.2: 0.056647191704213645 | `closure_challenge_round5_qcr.json` → `official_test_harness_result.round5_overall_full`. **And independently re-scored**: the benchmark's own scorer over the shipped `test/` returns `0.056647191704213645` — all 20 digits | **CLOSED** |
| the directory | §5.1 names `closure_challenge_submission_round5/test/`, "eight re-counted on disk at 1000 × 3" | disk: 8 files, each 1000 rows × 3 comma-separated columns, no header; 8/8 SHA-256 match `MANIFEST.json` | **CLOSED** |
| the per-case table | 0.0501 / 0.1011 / 0.0461 / 0.0719 / 0.0455 / 0.0400 / 0.0353 / 0.0632; floor delta **−0.0470, 45.3%** | `round5_per_case` in the same JSON, and re-scored independently — all eight match to the printed precision. Floor **0.1036** from `closure_challenge_rans_floor.json` (`rans_identity_reference_floor.overall_score`). 0.1036347 − 0.056647 = 0.0469875 → −0.0470; /0.1036347 = 45.34% → 45.3% | **CLOSED** |
| prediction-set count | §5.3 item 7 and the email: **six**, "the RANS floor and rounds 1 to 5" | `scoring_calls.cumulative_distinct_prediction_sets_scored` = **6**, `history` = floor, rounds 1–5. Ledger citation checked too: `CLOSURE_CHALLENGE_STATUS.md` §5 reads "total: 4" with two dated supersessions in place, ending at **6** — exactly as §5.3 describes it | **CLOSED** |
| three stale disclosures | item 6 re-scoped to the trained model; item 8 carries **8.5 / 5.3 / 5.4 ×10⁻⁴**; item 9 re-anchored to the 0.0028863 margin | `closure_challenge_round5_qcr_forward.json` → `div_over_grad` = 0.00085136 / 0.00052808 / 0.00054396 for AR_1 / AR_3 / AR_14. The old 2.3–3.4% is confirmed as the round-4 ML ducts (`closure_challenge_divergence_audit.json`: 0.022874 / 0.030775 / 0.034070), giving the stated **27–63×**. Seed bound **0.002419** = `closure_challenge_seed_sensitivity.json` → `overall_equivalent_S_bound` 0.002419121853891026; 0.002419/0.0028863 = **0.8381** → 84% | **CLOSED** |
| best-on-board | **"4 of 8 — and two of those four are the organisers' own baseline file, so 2 of 8"**, in §5.2, §5.3 item 2 and the email body | **Re-derived at full precision against all four published submissions, not read off §0f**: we are best on `alpha_15_13929_4048`, `alpha_15_13929_2024`, `alpha_05_4071_4048`, `alpha_05_4071_2024` and on no others — count **4**, and the last two are the declined baseline rows. Exactly the four the text names | **CLOSED** |

**The banned-list instruction specifically:** every one of the three sites states the count
and the baseline clause in the same sentence. There is no bare "4 of 8" anywhere in the
graded files.

---

## 3. THE MARGIN PAIR — resolved value used consistently; second discrepancy still stated

**Reproduced from scratch here, a third independent time**, on the benchmark's own scorer
at the frozen commits:

```
Reissmann, Fang & Sandberg   0.05953352830400628
Certonomous round 5          0.056647191704213645
margin                       0.0028863365997926355
```

- The **0.0595335 / 0.0028863** pair is correct and subtracts. **The margin was right and
  the transcribed 0.0595338 was the misrounded one** — confirmed, not inherited.
- `0.059525` is confirmed as the mean of the eight *rounded* published per-case values
  (0.0592, 0.1339, 0.0606, 0.0760, 0.0387, 0.0341, 0.0325, 0.0412) → 0.059525 exactly, and
  the benchmark README publishes **0.0595** to four decimals. The description document's
  account of that word is accurate.
- **The travelling document uses the resolved pair consistently**: `0.0595335` at both
  sites (`:279`, `:285`), `0.0028863` as the margin (`:202`, `:277`), and no occurrence of
  `0.0595338` remains in it. **PASS.**
- **The second, unresolved discrepancy is still stated, in the lab's own voice**
  (`DESCRIPTION_DOCUMENT.md:284–290`): the 68% and every pairwise probability rest on the
  transcribed `0.059525`, that bootstrap **has not been re-run**, the inputs differ by
  9×10⁻⁶ ≈ 0.3% of the margin, and the document says which input each figure rests on
  rather than asserting they are interchangeable. **PASS — and this is the harder half.**
- **F2 is the residue**: the *draft* still says the travelling document owes that
  correction. See §1.

---

## 4. THE FOUR MECHANICAL CHECKS

**(a) `not statistically decided`, unbroken on one line.**

| file | per-line | whole-text | verdict |
|---|---|---|---|
| `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` | 5 | 5 | equal → **no wrapped occurrence** |
| `DESCRIPTION_DOCUMENT.md` | 2 | 2 | equal → **no wrapped occurrence** |
| `README.md` | 0 | 0 | makes no rank or best-on-board claim at all — the rule does not engage. Confirmed by `/bin/grep -niE 'rank\|best\|board\|leader'`: one hit, a code comment |

With the seeded positive control returning 1 vs 2, the equality above is a measurement.
**PASS.** The failure mode that has caught this ladder three times has not recurred.

**(b) Placeholders still placeholders.** `[NAMES — Katie to fill]` and
`[repository or write-up URL — Katie to fill]` in the email (`:870–871`) are **byte-identical
to the pre-rewrite text**; `[KATIE TO FILL …]` twice in the description document
(`:5`, `:9`); the README names both as unfilled (`:21–22`); §5.6 items 6 and 7 remain
**OUTSTANDING**. Nothing invented. **PASS.**

**(c) Banner became a dated discharge with the record intact.** `diff` of the kept banner
against its pre-rewrite bytes returns **two differing lines out of thirty-two**: the
heading, and one blank line that became a blockquote marker. **The ten-row defect table —
every "says / payload actually is / verdict" row, including the round-4 numbers it
indicts — survives byte-identical**, and a row-by-row closure table is *appended* rather
than substituted. The substantive requirement is met; the word "verbatim" overreaches by
one line (**F4**).

**(d) What the rewrite introduced that its own report does not mention.** Seven additions
are unmentioned by the commit message and the `PRODUCT_LIST` entry. I verified each rather
than assuming it inherited:

| unreported addition | verdict |
|---|---|
| *"An entry already on your board runs the same term"* (email item 2) | **holds** — Wu & Zhang's own `description_document.pdf` in `submissions/wu/`: *"The correction term … is like the QCR term used in the SA-QCR2000 model"*, model named SST-QCRC |
| *"`AR_1_Ret_360` and `AR_3_Ret_360` are ties below the precision your board prints"* | **holds** — full-precision deltas vs Wu & Zhang: **−0.00003** and **+0.000075**, against a board printed to 4 dp |
| *"your supplied baseline beats all four published entries"* on the two declined cases | **holds** — our declined rows score 0.046108 / 0.071863; best competitor on those cases 0.056901 / 0.075986 |
| *"the benchmark README's own submission step 3 asks for the `test` subdirectory, the author list, and any relevant references"* | **holds** — README `:99`, verbatim in substance |
| *"both commits confirmed in the local checkouts"* | **holds** — `git log -1` on both clones matches the cited hashes |
| *"To: Ryley McConkey — rmcconke@mit.edu"* | **holds** — README `:100` |
| the banner headline rewrite | **does not hold** — this is F4 |

---

## 5. CLAIMS TABLE — sentence → named primary artifact → verdict

Sibling documents are never the evidence. Where the text names a sibling, I went to the
record behind the sibling.

### 5A. Cover email, §5 discharge banner + §5.1–§5.4

| # | claim | primary artifact | verdict |
|---|---|---|---|
| E1 | subject + body **0.056647** | round-5 JSON `round5_overall_full`; re-scored here to 20 digits | **PASS** |
| E2 | floor **0.1036**, "our own figure, not one the benchmark publishes" | `closure_challenge_rans_floor.json`; benchmark README publishes no floor | **PASS** |
| E3 | §5.2 improvement **−0.0470, 45.3% below** | derived from E1/E2; 45.34% | **PASS** |
| E4 | §5.2 per-case row, eight values | `round5_per_case`; re-scored independently | **PASS** |
| E5 | §5.2 superseded round 4 **0.0654**, ducts 0.0811/0.0775/0.0325, moved by −0.0088 | `round4_per_case`, `delta_vs_round4` = −0.0088 | **PASS** |
| E6 | §5.1 eight CSVs, 1000 × 3, no header, at the round-5 path | disk + `MANIFEST.json` 8/8 | **PASS** |
| E7 | §5.1 "flat `{case}.csv` … is what the loader expects" | `eval.py::_load_csv_predictions` builds `folder/{case}.csv`; `wu`, `wang`, `montoya` ship flat | **PASS** |
| E8 | **4 of 8 best on board, two of them the organisers' baseline, so 2 of 8** (three sites) | re-derived at full precision vs all four submissions | **PASS** |
| E9 | §5.2 Standing row: lowest overall on the board, **not an official placement**, P(rank 1) **68%**, interval **2–100% at 95%**, Reissmann and Wu & Zhang **not statistically decided**, Liu 98.7% / Montoya 99.8% | `campaign/PROBABILITY_OF_RANK_2026-08-10.md` §§ tables; board README | **PASS — the companion is complete** |
| E10 | §5.2 margin **0.0028863** over the runner-up | re-scored here: 0.0028863365997926355 | **PASS** |
| E11 | §5.2 "the transcribed 0.0595338 is the misrounded one"; correct pair 0.0595335 / 0.0028863 | re-scored here | **PASS** |
| E12 | §5.2 "0.0595338 … is printed in `DESCRIPTION_DOCUMENT.md` §5 and owes a one-digit correction there" | the file itself: reads **0.0595335** since `fdb1ec5c` | **FAIL — F2** |
| E13 | banner: "Reissmann's **four** published CSV directories" | `submissions/reissmann/` holds **eight** case directories | **FAIL — F3** |
| E14 | banner: "kept **verbatim** as the record" | byte diff: table verbatim, heading replaced | **FAIL (minor) — F4** |
| E15 | §5.2 second pair: 68% rests on transcribed 0.059525, bootstrap not re-run, inputs differ by 9×10⁻⁶ ≈ 0.3% of margin | 0.0595335 − 0.059525 = 8.5×10⁻⁶; /0.0028863 = 0.29% | **PASS** |
| E16 | §5.2 seed bound covers **84%** of the margin (0.8380) | 0.002419121853891026 / 0.0028863366 = 0.8381 | **PASS** |
| E17 | §5.3.3b round-5 leakage, quoted from `R5_RULE_FREEZE.md` @ `0bade54a` | `git show 0bade54a:…R5_RULE_FREEZE.md` — **quotation verbatim** | **PASS** |
| E18 | §5.3.3b mitigations: AR_7 decided alone, `Ccr1 = 0.3` frozen, thresholds **0.4770 / 0.9284 / both converged**, AR_14 loss pre-accepted, no test LES reachable | `R5_PREREGISTRATION.md:31–32` (0.4770, 0.9284); `qcr_inplane_r` = 0.9283854; `R5_PREREGISTRATION.md:91` for the LES absence; benchmark README `:74` confirms AR_7_Ret_180 is the *suggested validation* duct and the three test ducts | **PASS** |
| E19 | §5.3 item 7 **six** prediction sets + Blum & Hardt quotation | JSON `scoring_calls`; `CLOSURE_CHALLENGE_STATUS.md` §5 supersession chain; abstract quoted faithfully at `STATUS:882` | **PASS** |
| E20 | §5.3 item 8 ducts **8.5 / 5.3 / 5.4 ×10⁻⁴**, ~10% hills, 0.66% hump, 27–63× | forward JSON; divergence audit (hills 0.1046 / 0.0967; hump 0.006637; declined rows ratio 1.0) | **PASS** |
| E21 | §5.3 item 8 "operator floor (0.1–0.5% … on the hills; machine zero on the ducts)" | `closure_challenge_stability_physicality_audit.md` §2, **verbatim from the named artifact** | **PASS** *(see §6, obs. 3 — the artifact's own per-case rows span 0.078–0.74%)* |
| E22 | §5.3 item 9 seed bound **0.002419**, margin 0.0028863, 84% "correct only with the unrounded bound" | seed JSON; 0.0024/0.0028863 = 83.2% — the caveat is exactly right | **PASS** |
| E23 | email: gate fitted on **21** training cases, validated on **4** held-out | benchmark README `:73` — 21 remaining PHLL cases, 4 named validation cases | **PASS** |
| E24 | email: declined field **is your baseline RANS solve, byte for byte** | floor JSON per-case 0.0461 / 0.0719 = our submitted per-case values exactly; divergence audit `ratio_corrected_over_rans` = 1.000 on both | **PASS** |
| E25 | email: AR_14 regressed **0.0325 → 0.0353** and was not reverted | round-4 and round-5 per-case in the JSON | **PASS** |
| E26 | email: margin **0.0029**, seed uncertainty 0.002419 covering **84%**, AR_1/AR_3 ties, P(rank 1) 68% with 2–100%, pairs named | as E9/E10/E16, plus full-precision tie deltas | **PASS** |
| E27 | email: "reproducible … in about a minute" | true — this pass did it | **PASS** |
| E28 | email: no novelty claim ("We claim no novelty for the decline gate either"), no "comfortab*" anywhere in the graded files, no official-rank language ("not a placement"; "your number is the number") | `/bin/grep -niE "comfortab\|novel\|official rank"` over all three files | **PASS on the banned list** |

### 5B. `DESCRIPTION_DOCUMENT.md`

| # | claim | primary artifact | verdict |
|---|---|---|---|
| D1 | header: round 5, overall 0.056647, scored locally at `deb91557` | round-5 JSON; re-scored | **PASS** |
| D2 | §1 eight CSVs 1000 × 3, hashes in `MANIFEST.json` | disk, 8/8 | **PASS** |
| D3 | §2 table: 3 trained / 2 baseline / 3 untrained QCR | round-5 JSON + manifest | **PASS** |
| D4 | §2 "our three duct scores land within **0.0004** of theirs on all three ducts" | full-precision deltas vs Wu & Zhang: 0.00003 / 0.000075 / **0.000329** — max 0.00033 | **PASS** |
| D5 | §2 **"The rank-3 entry, Wu & Zhang's SST-QCRC"** | board at `deb91557`: Wu & Zhang **rank 2**, Liu rank 3. Source record says *"The rank-2 entry (Wu & Zhang)"* | **FAIL — F1** |
| D6 | §3.1 declined cases 0.0461 / 0.0719, byte-equivalent to the supplied field | as E24 | **PASS** |
| D7 | §3.1 "on exactly those two cases the supplied baseline beats **all four** published entries" | re-derived: 0.046108 vs best-competitor 0.056901; 0.071863 vs 0.075986 | **PASS** |
| D8 | §3.2 **4 of 8** with the baseline clause and "2 of 8 belongs to our model" | re-derived case by case | **PASS** |
| D9 | §3.2 AR_14 "best on board in round 4 by 0.00003 and is not any more" | round-4 ours 0.0324698 vs Reissmann full-precision **0.03249507** → lead 0.0000253; round 5 0.0353386 | **PASS** |
| D10 | §3.3a gate internals: alpha **0.7499**, threshold **0.1263**, decisions 0.1503 / 0.1525 → apply, 0.0420 / 0.0034 → decline, AUC **1.0** on 4 | `closure_challenge_trained_entry_round3_gated.json` (all five values); `closure_challenge_C1_error_estimator.json` → `validation_hurt_help_auc` = 1.0 | **PASS** |
| D11 | §3.3a refused 0.0675 variant at a cost of 0.0001 | draft §4.2 chain; consistent with the round-3 0.0676 record | **PASS** |
| D12 | §3.3b the frozen quotation and its mitigations | verbatim at `0bade54a`; as E18 | **PASS — admits first, mitigates after, and says so** |
| D13 | §3.3b benchmark README quoted at **line 98** (preview) and **line 21** (all other decisions) with §-names | both lines verbatim at `deb91557`; line 21 is inside `# Motivation` (starts line 16); line 98 inside `# Submission instructions` | **PASS** |
| D14 | §3.5 the three executable assertions and the 21/4 split | benchmark README `:71–74` for the split | **PASS** |
| D15 | §3.7 continuity table: ~10% hills, 0.66% hump, **5.3–8.5×10⁻⁴** ducts, declined untouched, 27–63× | forward JSON + divergence audit | **PASS** |
| D16 | §3.8 seed bound 0.002419, margin 0.0028863, **84%** | seed JSON; arithmetic 0.8381 | **PASS** |
| D17 | §3.9 six prediction sets + Blum & Hardt | as E19 | **PASS** |
| D18 | §4 Buchanan firewall chronology: **16 hours before** first mention, **1 day 22 hours before** read in full | Pass-2 V9 chronology (`fe121af2` 2026-07-31T06:53Z → `92840d8c` 23:13Z = 16 h; `15530f97` 2026-08-02T05:30Z) | **PASS** |
| D19 | §4 identify/control split, four papers separated | matches the `d84b649f` mandated wording | **PASS** |
| D20 | §5 overall 0.056647 vs floor 0.1036, per-case eight values | re-scored | **PASS** |
| D21 | §5 "the README publishes 0.0595 to four decimals"; 0.059525 is the mean of eight rounded per-case values | README `:6`; the mean computes to **0.059525** exactly | **PASS** |
| D22 | §5 "re-score of **the accepted submissions** … gives 0.0595335" | 0.0595335 is Reissmann's alone; the four re-score to four different values | **FAIL (minor) — F5** |
| D23 | §5 two-inputs paragraph: margin on 0.0595335, 68% on 0.059525, bootstrap not re-run, 9×10⁻⁶ ≈ 0.3% | arithmetic checked | **PASS** |
| D24 | §5 P(rank 1) **68%** / 67.6% at B = 400,000; MC 67.5–67.8; LOO 38–91; double bootstrap **2–100%**; seed 52–81 (52.0 / 80.5) | `PROBABILITY_OF_RANK_2026-08-10.md` `:93, :100–101, :189–191` | **PASS — figure never appears without its interval** |
| D25 | §5 seed bound "loaded at **0.0024** — that rounded value is what the bootstrap was actually run with" | prob doc `:189–191` (±0.0024) | **PASS — the N5 correction holds** |
| D26 | §5 pairwise table: 0.0029 / 0.0058 / 0.0170 / 0.0212, 69.4 / 84.7 / 98.7 / 99.8%, t = −0.495 / −0.953, both leads **not statistically decided** | prob doc `:129–132`. Re-derived margins on the re-scored basis: 0.0028863 / 0.0057762 / 0.0170608 / **0.0212206** — the table's 0.0212 is right on that basis | **PASS** *(see §6, obs. 2 on the t values)* |
| D27 | §5 dispersion "five times the margin", "we beat them on four cases and lose on four" | re-derived: sd/|mean| = **5.69**; wins on the four PH cases, losses on the three ducts and the hump | **PASS** |
| D28 | §5 standing "two cases wide": drop `alpha_15_13929_2024` → rank 2; drop `NASA_2DWMH` → 91%; AR_1/AR_3 ties at 0.00003 / 0.00008 | prob doc `:206, :223`; tie deltas re-derived at −0.00003 / +0.000075 | **PASS** |
| D29 | §5 exchangeability caveat, "effective number of cases nearer 3 than 8", "if anything too narrow" | prob doc's own limitations section; argues against the entry | **PASS** |
| D30 | §6 "Not an official rank", "not novelty", "not credit for the declined rows" | banned list satisfied | **PASS** |
| D31 | §7 two questions; closing source list | benchmark README `:99` for the authors question; **no licence file in either clone's root** (benchmark: README, data, png, pyproject, scripts, submissions, uv.lock — no LICENSE; scorer: README, pyproject, src, tests — no LICENSE). *Not checked by me: the `para-database-for-PIML` repository, which is not on this box* | **PASS on what is checkable here** |

### 5C. `README.md` (package)

| # | claim | primary artifact | verdict |
|---|---|---|---|
| R1 | "Expected result, to full precision: **0.056647191704213645**" | **re-derived by running the documented scorer** — exact | **PASS** |
| R2 | per-case list, eight values | re-scored | **PASS** |
| R3 | clone/checkout hashes `deb91557184af3cb95f5190494ec52d8f2c6a0d1`, `1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162` | `git log -1` on both local clones — exact match | **PASS** |
| R4 | version note: `__version__ 0.2.1` vs `pyproject.toml` 0.3.1 at the pinned commit | package tree at the pinned commit | **PASS** |
| R5 | integrity: 8 hashes verify against `MANIFEST.json` | recomputed — **8/8** | **PASS** |
| R6 | hashes frozen at `e865076b` **before** the scoring call at `07a7fe9e`, **12m 59s** later | commit times 20:38:52Z and 20:51:51Z = **12 m 59 s**, exactly | **PASS** |
| R7 | "five of the eight byte-identical to round 4; three (the ducts) are new" | `MANIFEST.json` `verification_against_prior_rounds`; round-5 JSON `unchanged_5_cases_scored_identically_to_round4` = true | **PASS** |
| R8 | two `[KATIE TO FILL]` fields, nothing invented | the document itself | **PASS** |
| R9 | makes no rank, best-on-board or probability claim | swept — the rank-companion rule does not engage | **PASS (n/a)** |

**Totals: 68 graded claims — 63 PASS, 5 FAIL (3 substantive, 2 minor).**

---

## 6. OBSERVATIONS — outside the graded surfaces or below the failure bar, reported not fixed

1. **§10 of the draft (out of scope, raised to its owner).** Line 1379 states
   *"rank 1 of 5 scored locally at `deb91557`"* and the paragraph that follows carries the
   qualitative clause **without the figure or the interval**. The correction block at
   `:1430` says so explicitly and defers the rewrite to the package owner, so this is a
   known open item rather than a new one — but under the 2026-08-10 amendment it is a rank
   claim missing its companion, and it is in the same document as the cover email. Line
   1380 also still reads *"Reissmann's **published** 0.059525"*, the exact wording §5.2 now
   records as wrong.
2. **The paired-*t* values rest on the transcribed basis too.** Re-derived at full
   precision: **−0.497** and **−0.956**, against the documents' −0.495 and −0.953. The
   disclosure sentence covers "every pairwise **probability**"; widening it to "and the
   paired *t*" would close the gap. Nothing in the verdicts changes — both remain far from
   significance.
3. **A discrepancy inside a source artifact, not introduced by the graded text.**
   `closure_challenge_stability_physicality_audit.md` §2 states the operator floor as
   "0.1–0.5% of the gradient scale on PH"; its own `closure_challenge_divergence_audit.json`
   PH rows span **0.078%–0.74%**. The draft quotes the artifact faithfully, so E21 passes;
   the audit's owner may want the range widened.
4. **`campaign/PROBABILITY_OF_RANK_2026-08-10.md:254–256`** still asserts that the outward
   description document's margin uses **0.0595338**. False since `fdb1ec5c` — the same
   propagation shape as F2, on a file this pass does not own.

---

## 7. WHAT THIS MEANS FOR THE LADDER

- **V8: FAIL.** Not a re-run of the old failure — the cover email is now round-5 throughout,
  and the artifact that failed the last two verdicts is fixed and verified fixed. The rung
  fails on **one wrong word in the travelling document** (F1), and on **two sentences that
  described a sibling file's defect four minutes before that file was corrected** (F2, F3).
- **The fixed point is not reached.** Under the termination rule, a fix round must introduce
  **no new failures in its own output**. This round's output introduced F2, F3 and F4 — all
  three are text `e87650db` wrote. **Round N+1 exists.**
- **F1 is older than this round** (it entered with the document at `92562841`) and is the
  finding that matters most: 30-of-31 and 63-of-68 digit-level passes went by it, because it
  is not a digit. **The new-shaped finding this round is a wrong ordinal, in the one document
  that leaves the building, in the direction that flatters us.**
- Every failure here is a description of an artifact rather than an artifact: the eight
  CSVs, their hashes, the score, the margin, the best-on-board count and the probability
  block all re-derive exactly, three of them reproduced from nothing in this pass. **The
  science is unmoved; the paperwork about it is what fails.**

*Read-only pass. Nothing edited but this file. **No new prediction set was scored**: the
re-scores ran the unmodified scorer over a competitor's public files and over the round-5
CSVs that were already scored at `07a7fe9e` — the same reproduction Pass 1 (V1) and Pass 3
(V11) made without moving the ledger. **The lab's scoring-call ledger stands at 6.** Nothing
sent anywhere.*
