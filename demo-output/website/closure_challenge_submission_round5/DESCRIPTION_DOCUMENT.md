# Certonomous — Closure Challenge submission, description document

**Round 5 entry · overall 0.056647 · scored locally at benchmark commit `deb91557`**

**Authors:** `[KATIE TO FILL — named individuals with affiliation, or the company
name if the steward accepts one; this is one of the two open questions in the
cover letter]`
**Affiliation:** Certonomous
**Reference:** `[KATIE TO FILL — repository or write-up URL]`

> **Status of this document.** DRAFT, NOT SENT. Written 2026-08-10 by Ladder V
> Pass 2 to discharge package defect D3 (Pass 3, cold reproduction: *"the
> description document does not exist"*). Submissions are PARKED by standing
> instruction. Two fields above need Katie and are marked; **no value in them has
> been invented.** Nothing in this document may be sent until §5.6 items 6 and 7
> of `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` are cleared by Katie.

---

## 1. What is attached

Eight CSV files in `test/`, one per test case, 1000 rows × 3 columns
(`Ux, Uy, Uz` at the benchmark's own evaluation points), comma-delimited, **no
header**, all values finite. This is the flat `{case}.csv` layout used by the
accepted `wu`, `montoya` and `wang` submissions, and it is what the evaluation
package's own CSV loader expects.

SHA-256 for all eight files, together with the harness commits, are in
`MANIFEST.json` beside this document. `README.md` beside it says how to score
them from scratch.

## 2. Method, in one paragraph, and it is a weaker claim than most of the board

The entry is **not one method**. It is two, plus a decision rule, and the
honest description of it is:

| cases | what was submitted | is it "our model"? |
|---|---|---|
| `alpha_15_13929_4048`, `alpha_15_13929_2024`, `NASA_2DWMH` (3) | a trained post-hoc velocity-field correction | yes |
| `alpha_05_4071_4048`, `alpha_05_4071_2024` (2) | **the supplied RANS field, unmodified** — a train-only gate declined to correct them | **no** |
| `AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180` (3) | a converged forward solve of the **untrained** QCR2000 constitutive term | it is a 25-year-old published model, not ours |

**The trained part.** Target `delta_U = U_LES − U_RANS` per cell;
`HistGradientBoostingRegressor` ×3 on 7 features (Pope's 5 scalar invariants,
`Re_y`, `tke_ratio`); applied once to an already-converged RANS field as
post-processing. **It does not modify the turbulence model and nothing is
re-solved with the correction folded in.** That is a materially weaker claim than
the FIML / TBNN / SpaRTA family it is being ranked against, and saying so is the
point.

**The duct part.** `kOmegaSSTQCR` with `Ccr1 = 0.3` — Spalart (2000)'s published
constant, **nothing fitted to anything** — solved forward to convergence on
`residualControl`. It has no training range, which is exactly why it was chosen
(see disclosure 3b). The rank-2 entry, Wu & Zhang's SST-QCRC, carries the same
term; our three duct scores land within 0.0004 of theirs on all three ducts,
from independent solves. **The duct signal is the QCR term, not us.**

## 3. Disclosures

These are stated because we would rather a reviewer *find* them written down
than *discover* them.

### 1. Two of the eight predictions are the organisers' own unmodified field

On `alpha_05_4071_4048` (0.0461) and `alpha_05_4071_2024` (0.0719) the submitted
field **is the supplied RANS solve**, byte-equivalent to it, which we verified
rather than asserted. A decline gate — fitted on 21 training cases, validated on
4 held-out validation cases, never on a test case — determined that correcting
them would make them worse, and withheld the correction.

**Where those rows score well, the credit belongs to the baseline, not to our
model.** They are properties of a file every entrant is handed for free, and
anyone submitting it unchanged scores exactly the same. We ask that they not be
read as our result.

**And a finding about the benchmark that does not depend on our score at all,
which may be of more interest to you than our entry is:** on exactly those two
cases, the supplied baseline beats **all four** published entries. Every entrant
made those two cases worse by touching them. We report that as a property of the
benchmark, independently verified by a cold reproduction, and not as a result of
ours.

### 2. Best-on-board count, stated with its own qualification

> **SUPERSEDED 2026-08-11 — the board gained two entries and this count fell with
> it.** Against the **six**-entry board fetched live 2026-08-11 the count is
> **2 of the 8**, not 4: both `alpha_15` hills were lost to Tian, Buchanan, Hickel
> & Dwight (0.0432 and 0.0998 against our 0.0501 and 0.1011). **And the two that
> survive are exactly the two baseline rows**, so **the count that belongs to our
> model is now ZERO of 8** — our model is best on no single case. The overall is a
> mean and not a count of wins, so 0.056647 is still the lowest number on the
> board; this entry wins on consistency, not on peaks, and that is how it should be
> described. The original text is kept below, struck, because the change in the
> board is itself disclosable.

~~Our round-5 entry is the best number on the published board on **4 of the 8**
cases — and **two of those four are the baseline rows above**. The count that
belongs to our model is therefore **2 of 8**, not 4.~~ `AR_14_Ret_180` was best on
board in round 4 by 0.00003 and **is not any more** (see disclosure 4).

### 3a. Adaptive leakage across rounds 1–3, in full

Round 2's per-case preview scores motivated building the decline gate: we knew
which cases the correction was hurting because the test harness told us. **That
is soft, adaptive leakage, and it is real.** What follows it is the defence and
not a denial:

- Every parameter of the gate — screened features, RidgeCV alpha 0.7499,
  standardisation, coefficients, the 0.1263 threshold — derives from the 21
  training cases, and was reproduced byte-for-byte from train-only data.
- The gate is a deterministic train-only function. Seeing round-2's scores
  changed *when* it was applied, not *what* it outputs. Its four test decisions
  (0.1503, 0.1525 → apply; 0.0420, 0.0034 → decline) would have been identical
  had round 2 never been scored.
- It was validated for generalisation on non-test data first (AUC 1.0, 4 of 4)
  and only then applied.
- A variant scoring 0.0675 was identified and **refused**, because selecting it
  required choosing cases by their test outcomes. The honest route cost 0.0001.

### 3b. Adaptive leakage in ROUND 5 — the largest single change in the entry

**This is the disclosure a reviewer is most entitled to, and it was missing from
every earlier draft of this package.** Stated at full strength, in the words the
lab used to itself before any round-5 number existed
(`campaign/R5_RULE_FREEZE.md`, commit `0bade54a`):

> *"we already know the round-4 test-duct scores (0.0811 / 0.0775 / 0.0325), and
> any protocol that lets those numbers choose between the QCR field and the
> existing ML field is test-truth-informed model selection. Every degree of
> freedom in that choice is therefore closed here, in writing, before any new
> number exists."*

Plainly: **we knew the ducts were where we were losing, because the harness had
told us, and that knowledge is why the ducts were the target.** The whole
−0.0088 move, and the entire reason there is a rank claim at all, was selected
in knowledge of per-case test outcomes. No mitigation below cancels that
sentence, and none is offered as cancelling it.

What was then closed, in writing, before any solve:

- **All-or-none.** QCR ships on all three test ducts or none, decided by
  `AR_7_Ret_180` alone — the benchmark's **own suggested validation duct**, not a
  test case.
- **`Ccr1 = 0.3` frozen before any solve**, Spalart's published constant; no case
  dictionary overrides it.
- **Gate thresholds set from training ducts before the validation arms ran**
  (V1 ratio ≤ 0.70, V2 in-plane *r* ≥ 0.85, V3 converged on `residualControl`);
  measured 0.4770 / 0.9284 / both converged.
- **The `AR_14_Ret_180` loss accepted in advance, in writing**, with its reason:
  keeping ML on AR_14 while switching the other two is exactly the per-case
  selection the rule exists to forbid. **The loss then happened** — 0.0325 →
  0.0353, the best-on-board tie gone — **and was not reverted.**
- **No test ground truth was reachable.** No `*_LES` file exists in any of the
  three test-duct run directories, though the benchmark ships one for each; both
  `AR_7` arms have them, which is where they belong.

The rule as written prohibits training or validating on test-case *data*. That
did not happen. It does not prohibit reading your own preview scores — the
benchmark ships the test ground truth and instructs submitters to preview
(benchmark `README.md` at commit `deb91557`, §Submission instructions, line 98:
*"You can preview what your score will be using the benchmark dataset's python
package"*; and §Motivation, line 21: *"All other decisions are left to the
submitter"*).

**We think the freeze is a good answer. We do not think it is a complete one, and
we would rather you weighed it than found it.**

### 4. The `AR_14_Ret_180` regression was not reverted

`AR_14_Ret_180` went 0.0325 → 0.0353 (+0.0029) in round 5 and its 0.00003
best-on-board tie is lost. It is reported, not reverted, for the reason in 3b.
The round-2 `NASA_2DWMH` regression of +0.0011 was handled the same way.

### 5. Train / validation / test discipline

Enforced by executable assertions, not comments —
`assert len(_PH_TRAIN) == 21 and len(_PH_VAL) == 4`,
`assert not (set(_PH_TRAIN) & set(_PH_VAL))`,
`assert not ((set(_PH_TRAIN) | set(_PH_VAL)) & set(_PH_TEST))`. The test list is
imported **solely** to assert non-intersection. The 21/4 split is the
benchmark's own suggested split. Test *meshes* are used, which the task requires.

### 6. Known structural limitation of the trained model

Two of its seven features (`I3_S3`, `I4_W2S`) are algebraically identically zero
across the entire duct family, so the trained model is structurally blind there.
We would rather publish that than have it inferred from our duct scores. *(It no
longer bears on the submitted duct rows, which are forward solves — but it is why
they are.)*

### 7. Continuity of the submitted fields, measured

The corrected fields do not satisfy continuity, and every entrant who re-solves
the governing equations gets `∇·U ≈ 0` by construction. Measured, per family:

| rows | volume-weighted RMS `∇·U` / RMS `|∇U|` |
|---|---|
| the 2 corrected hill cases | ~10% |
| `NASA_2DWMH` | 0.66% |
| **the 3 ducts (round 5)** | **5.3×10⁻⁴ – 8.5×10⁻⁴** |
| the 2 declined cases | the baseline's own, untouched |

The ducts improved by 27–63× against the fields they replace, because they are
now converged SIMPLE solves. **We state the measured numbers rather than "satisfies
continuity by construction": the three submitted ducts measure 8.5×10⁻⁴
(`AR_1_Ret_360`), 5.3×10⁻⁴ (`AR_3_Ret_360`) and 5.4×10⁻⁴ (`AR_14_Ret_180`), and
none of those is machine zero.**

### 8. One-seed training uncertainty, and it is comparable to the whole margin

The trained model behind `alpha_15_13929_4048`, `alpha_15_13929_2024` and
`NASA_2DWMH` was fitted at a single seed. The truth-free bound on the overall is
**0.002419**. Our margin over Reissmann, Fang & Sandberg — rank 1 on the
published board — is **0.0028863**. **The seed bound
covers 84% of the margin.** The three duct predictions carry zero seed variance,
since nothing in them was trained.

### 9. Scoring-call ledger, correctly framed

**Six distinct prediction sets scored, ever** (RANS-identity floor, rounds 1–5).
This is a **self-imposed** discipline and **explicitly not** compliance with any
benchmark limit, because none exists — the benchmark instructs submitters to
preview their scores. The hazard it addresses is adaptive overfitting of a
holdout under repeated queries (Blum & Hardt, *The Ladder*, arXiv:1502.04585,
ICML 2015), whose own abstract calls rate-limited re-submission one of the
"poorly understood heuristics" the field resorts to. **Ours is that heuristic,
applied by the submitter to itself: harm reduction, not a guarantee.**

## 4. Prior art — the method class is not ours, and the gate is not our invention

**The post-hoc correction class is published.** Learned local-error correction of
a cheap CFD solve, applied without re-solving: **Hanna, Dinh, Youngblood &
Bolotnov**, *Coarse-Grid CFD Error Prediction using Machine Learning*,
arXiv:1710.09105 (2017); *Progress in Nuclear Energy* **118** (2019) 103140. The
delta, in the same breath: their surrogate corrects **grid-coarsening** error in a
coarse-grid no-model solve of a lid-driven cavity, from cell-Reynolds-number and
velocity-derivative features; ours corrects **closure** error in a converged k-ω
SST solve, from Pope invariants. Statistical ancestor, as lineage only: **Kennedy
& O'Hagan**, *JRSS B* **63**(3) (2001) 425–464.

**The decline gate is two established things, and we name them separately rather
than roll them into one.**

> Classifiers on RANS-only inputs that ***identify*** where the baseline is
> unreliable are established — **Ling & Templeton (2015)**, which classifies RANS
> results point by point as high or low uncertainty and controls nothing, and
> **Wu, Wang, Xiao & Ling (2017)**, an *a priori* confidence measure. ***Using
> such a classifier to control where a data-driven correction is fitted and
> applied*** is established separately — **Steiner, Dwight & Viré (2022)** and
> **Buchanan, Lăcătuş, West & Dwight (2025)**.

**Two of those authors wrote this benchmark.** What is left to us is narrow and we
state it that way: our gate decides for a **whole case** rather than a region,
it is trained to predict the **baseline's error** rather than distribution shift,
and its "off" state means **the uncorrected field is the submission**. This is a
recombination with a modification, not a new method class. **No sentence in this
package presents confidence-gated correction as novel.**

**A compliance fact you are entitled to, stated unprompted.** Buchanan et al.
(2025) train on the **NASA wall-mounted hump**, which is one of your scored test
cases. That is their own work in their own venue and no rule reaches it — but it
means their published coefficients are off limits to us, because borrowing or
calibrating against them would make our entry *indirectly* trained on a test case.
**We did not use them, and the proof is chronological rather than an assurance:**
our `NASA_2DWMH` prediction is byte-identical across rounds 3, 4 and 5 and was
written on 2026-07-31, **16 hours before** that paper is first mentioned anywhere
in our repository and **1 day 22 hours before** it was read in full. No coefficient or
artifact of that model exists in any executable file we hold.

**And the duct term carries the same honesty:** Spalart published QCR2000 in 2000,
and an entry already on your board runs the same term.

## 5. The score, and what it is worth

**Overall 0.056647**, through the benchmark's own unmodified scorer at eval
package commit `1c4e22c8`, benchmark commit `deb91557`, computed by us on our own
machine. Against a **0.1036** baseline obtained by submitting the supplied RANS
fields unchanged, computed by us on the same harness — that floor is our figure,
not one the benchmark publishes.

Per case: 0.0501 / 0.1011 / 0.0461 / 0.0719 / 0.0455 / 0.0400 / 0.0353 / 0.0632.

**This is a local scoring and not an official placement. Nothing has been
submitted, and if your scoring differs from ours, your number is the number.**

### What the standing is actually worth, quantified

On the published board at `deb91557` our 0.056647 is the best overall number, by
**0.0028863** over Reissmann, Fang & Sandberg. *(A note on that figure: the README
publishes 0.0595 to four decimals. A like-for-like full-precision re-score of
Reissmann, Fang & Sandberg's own eight submitted CSVs on the same harness gives
0.0595335 — that entrant's value alone, not a figure for the accepted
submissions as a set — and it is what the margin above uses. Earlier drafts of
ours quoted a "published 0.059525", which is the mean of eight rounded per-case
values and is not a number you publish — the error was small and ran against us,
but the word was wrong.)*

**Two values of that score are in play in this section, and we would rather say
so than have you find it.** The margin above uses the re-scored **0.0595335**.
The 68% below, and every pairwise probability in the table with it, come from a
bootstrap whose Reissmann input is the transcribed **0.059525**; that bootstrap
has not been re-run on the re-scored basis, so we do not assert those figures are
unchanged — we state which input each rests on. The two inputs differ by
9×10⁻⁶, about 0.3% of the margin.

> **RECOMPUTED 2026-08-11 AGAINST A SIX-ENTRY BOARD. Every figure in the rest of
> this section is struck and kept.** The figures below were computed against the
> **four**-entry board; fetched live on 2026-08-11 the board carries **six**
> entries and a new leader, **Yang at 0.0580**, and our margin over Yang is
> **0.001365**, not 0.002878. Recomputed by the same method (the script reproduces
> the four-entry figures exactly when the two new rows are removed):
> **P(rank 1) = 50%** — 50.2% over 400,000 resamples — which eight cases pin no
> tighter than **0–97% at 95%**, leave-one-case-out **31.7–78.5%**, one-seed
> sensitivity **34–65%** *(and its adverse leg puts us second, which it did not
> before)*. **Four comparisons are now not statistically decided, not two**, and
> one of them is the leader: Yang (t = −0.19), Reissmann (t = −0.50), Wu & Zhang
> (t = −0.95), Tian/Buchanan/Hickel/Dwight (t = −1.03). Liu and Montoya remain
> decided. Full derivation: `campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md`.

~~**P(rank 1) = 68%**~~ — 67.6% over 400,000 case-level bootstrap resamples of the
eight test cases, **against the four-entry board — see the box above**. **And the
interval that matters is not the Monte Carlo one:**

| interval | value *(four-entry board — superseded)* | what it measures |
|---|---|---|
| Monte Carlo (B = 400,000) | ~~67.5–67.8%~~ | only that the resampling ran long enough |
| leave-one-case-out (8 refits) | ~~38–91%~~ | how much of the 68% one case is carrying |
| double bootstrap, 95% | ~~**2–100%**~~ | what an eight-case sample can actually pin down |
| one-seed sensitivity | ~~**52–81%**~~ | what the seed we did not control is worth |

**On that last row, because it is the sharpest number we hold and withholding a
computable figure only looks concealed:** the truth-free seed bound of §8
(0.002419, loaded at **0.0024** — that rounded value is what the bootstrap was
actually run with, and the overalls it produces are 0.056647 ± 0.0024 exactly),
loaded adversely onto the three seed-dependent cases and the bootstrap re-run,
gives P(rank 1) = **52.0%**; loaded favourably, **80.5%**; as scored, 67.6%. **A seed draw we did not control moves the figure by nearly
thirty points.** It is derived from the same public inputs by the same route as
the 68%, so it travels with it.

**The honest reading: the point estimate is 68%, and eight cases cannot resolve it
better than "somewhere between a coin flip and near-certain".** We state the
figure with that interval attached, always, because 68% on its own sounds settled
and eight cases do not support settled.

**Which comparisons are decided, by name:**

| opponent | our margin | P(we lead) | paired *t* (n = 8) | verdict |
|---|---|---|---|---|
| **Yang** *(added 2026-08-11 — the new leader)* | **0.0014** | **57.8%** | **−0.189** | **not statistically decided** |
| Reissmann, Fang & Sandberg | 0.0029 | 69.4% | −0.495 | **not statistically decided** |
| Wu & Zhang | 0.0058 | 84.7% | −0.953 | **not statistically decided** |
| **Tian, Buchanan, Hickel & Dwight** *(added 2026-08-11)* | **0.0075** | **86.0%** | **−1.033** | **not statistically decided** |
| Liu, Wang, Zhao & Xiao | 0.0170 | 98.7% | −2.203 | decided on method |
| Montoya, Oulghelou & Cinnella | 0.0212 | 99.8% | −2.912 | decided on method |

**Against Yang the per-case dispersion is fifteen times the margin** and we beat
them on four cases and lose four — the least decided comparison in the table, and
it is the one that sits between us and first place.

Against Reissmann the per-case dispersion is **five times the margin**; we beat
them on four cases and lose on four. Against Liu and Montoya we win 7 of 8, and
those two comparisons survive resampling and are worth believing.

**The standing is two cases wide.** `alpha_15_13929_2024` alone supplies more than
the entire margin; delete it and we are rank 2 on the point score. `NASA_2DWMH` —
our only last-place case — alone costs more than the margin; delete it and P(rank
1) is 91%. **`AR_1_Ret_360` and `AR_3_Ret_360` are ties below the precision the
board publishes to** (0.00003 and 0.00008) and must not be read as per-case wins
or losses either way.

**The bootstrap's own assumption, against us.** It resamples cases as if they were
exchangeable. Four periodic-hill cases, three ducts and one hump are not eight
draws from one population: the three ducts moved together under a single
constitutive change and carry zero seed variance; the hill cases and the hump
share one trained model and one seed. The effective number of independent cases
is **nearer 3 than 8**, so the interval above is if anything too *narrow*.

**Everything in this section is reproducible from the attached CSVs and your own
published board.** We have not withheld the figure, because it takes a minute to
compute and withholding it would only look like concealment.

## 6. What we are not claiming

- Not an official rank. Not submitted until this package is.
- Not that our method beats Reissmann's or Wu & Zhang's — on these eight cases we
  scored lower, and a different eight could reverse it.
- Not novelty for the decline gate, or for the post-hoc correction class, or for
  QCR2000.
- Not credit for the two declined rows, or for the three duct rows beyond having
  chosen to run a published term and having frozen the choice before solving.

## 7. Two questions for the steward

1. The leaderboard credits "Authors." Is a company name acceptable on a row, or do
   you prefer named individuals with affiliation?
2. Neither this repository nor the `para-database-for-PIML` dataset carries a
   licence file. Are there terms of use we should be aware of for a commercial
   entity training on this data? We redistribute no source data.

---

*Sources for every number above, in the submitting lab's own records:
`closure_challenge_round5_qcr.json` (the entry of record and the one scoring
call), `campaign/R5_PREREGISTRATION.md` @ `e865076b`, `campaign/R5_RULE_FREEZE.md`
@ `0bade54a`, `closure_challenge_stability_physicality_audit.md` (seed and
continuity), `campaign/PROBABILITY_OF_RANK_2026-08-10.md` (the bootstrap),
`CLOSURE_CHALLENGE_PRIOR_ART.md` (the literature review and the firewall).
None of these files ships with the submission; every number they support is
restated in full above so that this document stands alone.*
