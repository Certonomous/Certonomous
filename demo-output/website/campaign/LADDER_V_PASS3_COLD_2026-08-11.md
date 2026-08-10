# Ladder V, Pass 3 — cold reproduction and skeptic's report on the round-5 Closure Challenge submission package

**Owner: Pass-3 (A11 cold reproduction + A12 skeptic's report).**
**Frame: outside reviewer, no prior contact with this lab's closure-challenge work.**
**Written 2026-08-10 (work performed 2026-08-10 UTC on this box).**

> **Filename date note, added 2026-08-10 by the V15 corrections pass (finding F2).**
> This file is named `LADDER_V_PASS3_COLD_2026-08-11.md` and was written on
> **2026-08-10**. The filename is deliberately NOT renamed — committed reports cite
> this path. Read it as a label, not a date.

---

## 0. Frame — what I read, and what I deliberately did not

This report is worth exactly as much as the discipline behind it, so the discipline
goes first.

**What I treated as the package** (the only lab-authored material I opened as a
primary source):

| Artifact | Path |
| --- | --- |
| The submission directory | `demo-output/website/closure_challenge_submission_round5/` (`MANIFEST.json` + `test/*.csv` ×8) |
| The description document | `demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` |
| The cover material | §5.4 of that document (the draft cover email) — it is not a separate file |

**What I opened only because the package points at it, by name, as the evidence for a
claim it makes:**

- `demo-output/website/closure_challenge_round5_qcr.json` (MANIFEST: `"reproduces"`)
- `demo-output/website/closure_challenge_round5_qcr_forward.json` (named in the model provenance)
- `campaign/R5_PREREGISTRATION.md`, `campaign/R5_RULE_FREEZE.md` (MANIFEST: `prediction_source`)
- `sdk/scripts/closure_round5_qcr_forward.py`, `closure_round5_points_order_check.py` (MANIFEST)
- `demo-output/website/closure_challenge_submission_round4/MANIFEST.json` (MANIFEST: hash assertion)
- `demo-output/website/closure_challenge_seed_sensitivity.json` (draft §5.3 item 9)
- `sdk/openfoam/qcr/kOmegaSSTQCR/*` (named as the untrained model, library commit `303247bb`)
- `/home/ubuntu/certonomous-runs/w3-qcr-rank1/` (named in the cost ledger of the round-5 JSON)

**Third-party material** (not the lab's): the benchmark clone
`/home/ubuntu/closure-challenge-benchmark` @ `deb91557` and the evaluation package
clone `/home/ubuntu/closure-challenge-pkg` @ `1c4e22c8`.

**What I deliberately did not open, and would not have had:**
`CLOSURE_CHALLENGE_STATUS.md` (a status file, and the authority the package cites for
its best-on-board count), `campaign/PROBABILITY_OF_RANK_2026-08-10.md`,
`CLOSURE_RANK1_CAMPAIGN.md`, `W3_QCR_DUCT_FALSIFIER.md`, `CAMPAIGN_STATUS.md`, any
`LADDER_V_*` rung report, any supervision review, and `closure.html`. Where I needed a
number that lives in one of those, I computed it myself or recorded a defect. In one
place (§4, W2) I computed independently a quantity the lab holds internally, and the
two agree — that agreement is stated below as a *check*, not as a citation, because I
never read their file.

**No new predictions were generated.** The benchmark's own unmodified scorer was run
offline against the package's frozen CSVs. Where I re-derived a shipped CSV, I did so
from a frozen field already on disk — no solver was launched, and no scoring call
against the lab's ledger is implied by anything here.

---

## 1. A11 — cold reproduction

Fresh working directory, package copied in, nothing from the repo on the path except
what is listed above.

### 1.1 Does the artifact exist where the package says it does?

**Yes, in every case, with one caveat.** All twenty-one paths named by `MANIFEST.json`,
by the round-5 JSON and by the draft's round-5 addendum resolve on this box. The caveat
is that none of them is *inside* the submission directory, and the description document
still carries `Reference: [repository or write-up URL — Katie to fill]` — so on receipt
none of them resolves for the recipient. That is defect **D4**, not a missing file.

### 1.2 Integrity of the eight CSVs

```
SHA-256 vs MANIFEST.json .......... 8 / 8 MATCH
shape 1000 x 3 .................... 8 / 8
all finite ........................ 8 / 8
header / delimiter as declared .... 8 / 8
```

The five non-duct files hash-match the round-4 manifest **and** the round-4 directory on
disk; the three duct files differ from round 4, exactly as claimed.

### 1.3 The score, reproduced

Scorer: `closure_challenge.eval.evaluate_from_csv_by_case` at commit `1c4e22c8`,
working tree clean, unmodified.

| case | my cold re-score | MANIFEST |
| --- | --- | --- |
| `alpha_15_13929_4048` | 0.0501052950 | 0.0501 |
| `alpha_15_13929_2024` | 0.1011121820 | 0.1011 |
| `alpha_05_4071_4048` | 0.0461077914 | 0.0461 |
| `alpha_05_4071_2024` | 0.0718629324 | 0.0719 |
| `AR_1_Ret_360` | 0.0454704448 | 0.0455 |
| `AR_3_Ret_360` | 0.0399821563 | 0.0400 |
| `AR_14_Ret_180` | 0.0353386190 | 0.0353 |
| `NASA_2DWMH` | 0.0631981126 | 0.0632 |
| **overall** | **0.056647191704213645** | 0.056647191704213645 |

**Bit-identical on the full-precision overall.** Every per-case full-precision value in
`closure_challenge_round5_qcr.json` also matches to the last digit printed.

### 1.4 Is the scoring harness being driven correctly?

Three independent checks, none of which the package asked me to run:

1. **Evaluation-point ordering.** `closure_challenge.dataset_utils.evaluation_points(case)`
   and the benchmark's shipped `data/evaluation_points/{case}_points.csv` — the file the
   forward script actually used — agree to **`max|diff| = 0.000e+00` on all eight cases**.
   The row order of the submitted CSVs is therefore the row order the metric compares
   against. This is the failure mode that would silently destroy a submission and it is
   clean.
2. **Leaderboard re-scoring.** All four accepted submissions re-score on this harness to
   their published four-decimal values: Reissmann 0.059534→0.0595, Wu & Zhang
   0.062423→0.0624, Liu et al. 0.073708→0.0737, Montoya et al. 0.077868→0.0779.
   **4 / 4.** The harness is the same one the board was built with.
3. **RANS-identity floor.** Interpolating the benchmark's own supplied converged k-ω SST
   field onto the evaluation points for all eight cases and scoring it gives
   **0.1036346675** — the package's 0.1036, reproduced independently, including the three
   duct floors (0.128819 / 0.124322 / 0.059029) that were not in my starting material.

### 1.5 Re-derivation of the predictions themselves

| cases | re-derived? | result |
| --- | --- | --- |
| `AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180` | **yes**, from the converged QCR fields in the named run tree | **max abs deviation 0.000e+00** on all three — the shipped CSVs are exactly `NearestNDInterpolator(C, U)(points)` of those fields |
| `alpha_05_4071_4048`, `alpha_05_4071_2024` | **yes**, from the benchmark's own supplied RANS solve | max abs deviation **4.99e-10** = the CSV's `%.10g` write precision. The two "declined" rows *are* the untouched baseline, as disclosed |
| `alpha_15_13929_4048`, `alpha_15_13929_2024`, `NASA_2DWMH` | **no** — see D8 | shown *not* to be the baseline (baseline scores 0.1320 / 0.2049 / 0.0621 against shipped 0.0501 / 0.1011 / 0.0632), so they are a genuine model output; but the model is not reproducible from the package |

Convergence claims verified by grepping the arms' own logs: all three test-duct QCR arms
carry `SIMPLE solution converged in {N} iterations` at the exact iteration count the
record states, and each is inside its pre-registered cap.

### 1.6 Is the correction untrained?

`sdk/openfoam/qcr/kOmegaSSTQCR/kOmegaSSTQCR.C` constructs `Ccr1_` with default `0.3`
and `readIfPresent` from the coefficient dict. **No `Ccr1` entry exists in any case
dictionary in the run tree** (grepped all five arms). The value used is therefore the
compiled default, which the header documents as `c_r = 0.3 (Spalart 2000, untrained)`.
The term is constitutive-only; `RASModel kOmegaSSTQCR` and the library `libs(...)` line
are the only turbulence-side edits. **The QCR half of the entry is untrained in the
strict sense, verified in code and dictionaries rather than taken on trust.**

### 1.7 Is any test data touching the method?

Checked directly, not read off prose:

- `find` over the entire round-5 run tree returns `U_LES`, `k_LES`, `tauij_LES` **only**
  under `AR_7_Ret_180_sst/0/` and `AR_7_Ret_180_qcr/0/` — the benchmark's own *suggested
  validation* duct. **No LES field of any kind exists in any of the three test-duct run
  directories**, although the benchmark ships one for each of them.
- The forward script reads test-case coordinates from
  `data/evaluation_points/{case}_points.csv` — plain coordinate CSVs — and never opens
  the truth dict at all. It then stubs `score`, `score_from_csv`, `evaluate_by_case`,
  `evaluate_from_csv_by_case`, `evaluate_individual_case`, `_velocity_field`,
  `_ground_truth`, `_load_csv_predictions` and `evaluation_points`, and proves the guard
  armed by catching its own refusal before continuing.
- The one untracked file in the benchmark clone is `scripts/rans_identity_baseline.py`,
  lab-authored — which the description document discloses at §7.2. Nothing else in either
  third-party clone is modified.

**Verdict on A11: the scoring is legitimate and I reproduced it cold, to the last bit of
the overall.** The three duct predictions reproduce exactly from a frozen field; two more
reproduce as the supplied baseline; three do not reproduce at all and cannot be made to
(D8).

---

## 2. Ranked package defects — every question I had to answer from outside the package

Ranked by how hard each would have stopped a reviewer who had only what the package
contains.

### D1 — BLOCKING. The package never says where the benchmark or the scorer is, or how to install it.

`MANIFEST.json` names two commit hashes and no repository. I located
`/home/ubuntu/closure-challenge-benchmark` and `/home/ubuntu/closure-challenge-pkg` by
filesystem search. The URLs exist in the description document's §1 table, so a reviewer
who is sent *both* pieces is covered — but the benchmark's own instruction is "send your
`test` subdirectory," and the `test/` subdirectory plus its manifest contain no URL, no
`pip` line and no path. **Question I had to answer from outside: "which checkout, and
where?"** Fix: one `harness.repos` block in `MANIFEST.json` with both clone URLs beside
the hashes they already carry.

### D2 — BLOCKING. The cover material is stale by two rounds and would be sent wrong.

The draft cover email (§5.4) has subject line **"overall 0.0654"** and states 0.0654 in
the body. §5.1 says the CSVs to send are at `closure_challenge_submission/test/` — the
**round-3** directory. §5.2's claims table gives round-4 per-case values (0.0811 / 0.0775
/ 0.0325). Only the §10 addendum, 400 lines further down, carries round 5. A recipient
reading front-to-back gets a headline number wrong by 0.0088, a directory name that is
not the one attached, and three per-case values that contradict the attached CSVs.
**Question I had to answer from outside: "which of these three mutually inconsistent
scores is the entry?"** I resolved it only because I could hash the CSVs against three
manifests. The steward cannot.

### D3 — BLOCKING. The description document does not exist.

§5.1 item 3 requires "a description document (following wu's precedent)"; §5.3 specifies
its mandatory contents in nine items; **no file implements it.** What exists is an
internal audit document containing a specification for a document. This is precisely the
class of defect the package itself found and closed for the CSVs at §4.5 ("there is no
submittable artifact") — the same finding one level up, uncaught. **Question from
outside: "what is the description document, and is this file it?"**

### D4 — HIGH. Every provenance pointer dangles on receipt.

`MANIFEST.json` sources its central claims to `campaign/R5_PREREGISTRATION.md @ e865076b`,
`campaign/R5_RULE_FREEZE.md @ 0bade54a`, `sdk/scripts/closure_round5_qcr_forward.py`,
`sdk/scripts/closure_round5_points_order_check.py`, the round-4 manifest and
`closure_challenge_round5_qcr.json`. None is inside the submission directory; all are
repo-relative; the repository URL slot in the cover email is still `[Katie to fill]`.
Result: on receipt, **the untrained claim, the test-blind claim, the all-or-none claim
and the ordering check are all unverifiable.** I could check every one of them only
because I had the repo. Fix: either ship the rule freeze, the pre-registration and the
two scripts inside the submission directory, or fill the reference URL — the second is
one line and strictly better.

### D5 — HIGH. The mandatory disclosure list (§5.3) is written against round 4 and is now wrong in the entry's own favour.

- **Item 8, continuity.** States volume-weighted RMS `∇·U` of "2.3–3.4% on the three
  ducts." Round 5's ducts are converged SIMPLE solves; the measured `rms div(U) /
  rms |gradU|` is **5.3e-4 to 8.5e-4**. The disclosure now overstates a defect that has
  largely gone away — the rare case of a stale disclosure being unfair to the entrant.
  Its replacement should not overcorrect: the forward script's docstring says the QCR
  fields "satisfy continuity by construction," and 8.5e-4 / 5.3e-4 / 5.4e-4 are not
  machine zero. *[Corrected 2026-08-10 by the V15 corrections pass, finding F1: this
  sentence originally cited 5.8e-4, which is `/arms/AR_7_Ret_180_qcr` — the validation
  duct, not a submitted case. The three submitted ducts are AR_1_Ret_360, AR_3_Ret_360,
  AR_14_Ret_180.]* (The SST
  arm's 7e-17 is not the counter-example it looks like: that solve is exactly
  unidirectional, so its divergence is zero for a reason unrelated to convergence
  quality.) State the measured number, not "by construction."
- **Item 6 / §7.1, the duct feature degeneracy and the `Re_y` extrapolation failure.**
  Describes an ML duct model that is no longer in the entry at all.
- **Item 9, seed sensitivity.** Anchors the 0.0024 bound to "the 0.0030 gap to rank 2."
  The operative comparison is now a **0.00289 margin over rank 1**. The qualifier is
  still correct and is now *more* load-bearing, not less.

**Question from outside: "which of these nine disclosures still describe the attached
files?"** Answer: 1, 2, 3, 4, 5 and 7 do; 6, 8 and 9 do not.

### D6 — MEDIUM. "Reissmann's published 0.059525" is not published, and is not what a re-score gives.

The README publishes **0.0595**, four decimals. `0.059525` is the arithmetic mean of
Reissmann's eight *rounded* per-case values. A full-precision re-score of Reissmann's own
submitted CSVs on the same harness gives **0.0595338**. So the stated margin `0.002878` is
a hybrid — the entry's unrounded overall against a reconstruction from rounded numbers —
and the like-for-like margin is **0.0028863**. The error is small and it runs *against*
the entry (the package understates its own margin by 8e-6, which is to its credit), but
the word "published" is wrong and the figure is not reproducible from the source it names.
**Question from outside: "where does 0.059525 come from?"** — I had to reverse-engineer it.

### D7 — MEDIUM. The package's authorities for two of its claims are internal files that do not travel.

§10 instructs that the cover email cite "§0f of `CLOSURE_CHALLENGE_STATUS.md`" for the
best-on-board count of 4 of 8; the round-5 JSON sources its rank companion to
`campaign/PROBABILITY_OF_RANK_2026-08-10.md`; the rule freeze sources its gate thresholds
to `W3_QCR_DUCT_FALSIFIER.md` §3 and its plan of record to `CLOSURE_RANK1_CAMPAIGN.md`
§5. None ships. A submission must not instruct its own cover letter to cite a file the
recipient will never see. (I did not read any of these; I verified the 4-of-8 count
directly against the published board instead, and it is correct.)

### D8 — MEDIUM. Three of the eight predictions are irreproducible by anyone outside the lab.

`alpha_15_13929_4048`, `alpha_15_13929_2024` and `NASA_2DWMH` come from a trained
`HistGradientBoostingRegressor`. The package ships no model file, no training script
reference in the manifest, no hyperparameters, no seed and no reproduction instruction —
the manifest says only "round-2 trained correction, unchanged" and "round-1 PH model."
Those three files carry the entry's two largest per-case wins. I proved they are not the
baseline; I could not prove they are what the package says they are. Contrast the three
duct files, which I re-derived to **exactly zero deviation**. **The untrained third of
the entry is fully reproducible and the trained third is not** — which is the reverse of
the way the package's confidence is distributed.

### D9 — LOW, but a genuine reproduction hazard. Following §1's own install advice can score you on a different metric.

§1 offers `pip install closure-challenge` as a route to the scorer. The pinned commit
`1c4e22c8` is the one that introduced "vector magnitude metric, mean over cases" and the
package still self-reports `__version__ = '0.2.1'`. A reviewer who pip-installs gets an
unpinned version whose own version string cannot be used to tell whether it is the right
metric revision. The manifest documents the trap; the description document offers the
route that walks into it. Say "clone at `1c4e22c8`," not "pip install."

### D10 — LOW. The package does not name itself.

Nothing inside `closure_challenge_submission_round5/` states its own repo path, and the
directory does not live where a reader following the campaign trail would look for it
(`demo-output/website/`, not `demo-output/website/campaign/`). Cosmetic, but it cost me a
search before anything else could start.

### D11 — LOW, disclosed. No authors.

`MANIFEST.json` credits "the round-5 scoring agent." The cover email has `[NAMES — Katie
to fill]`. The benchmark's one procedural requirement is an author list. Flagged in the
package as outstanding item 6 and correctly owned; recorded here only so the count of
things blocking a send is complete.

---

## 3. A12 — the skeptic's report

Three points, in the voice of a reviewer who has just read the package once and is
inclined to disbelieve it. Not softened, not pre-rebutted. The answer beside each is the
**best answer the package itself supports** — and where it supports none, that is said.

---

### W1. "You chose the ducts because the answer key told you that was where you were losing, and you chose QCR because the entry above you already publishes good duct numbers with it. Your pre-registration freezes the last degree of freedom, after the one that mattered had already been spent — and your disclosure list doesn't mention any of it."

**The answer the package supports — and it is strong, up to a point.**

`R5_RULE_FREEZE.md` opens by conceding the charge in the lab's own words: *"we already
know the round-4 test-duct scores (0.0811 / 0.0775 / 0.0325), and any protocol that lets
those numbers choose between the QCR field and the existing ML field is test-truth-informed
model selection. Every degree of freedom in that choice is therefore closed here, in
writing, before any new number exists."* It then closes them, and I verified each closure
against something other than the prose:

- **All-or-none across all three test ducts**, decided by `AR_7_Ret_180` alone — the
  benchmark's own *suggested validation* duct, not a test case.
- **`Ccr1 = 0.3` frozen before any solve**, Spalart's published constant. Verified: the
  compiled default is 0.3 and no case dictionary overrides it.
- **Gate thresholds (V1 ≤ 0.70, V2 r ≥ 0.85, V3 converged) set from training ducts**,
  before the validation arms ran. Measured 0.4770 / 0.9284 / both converged.
- **Convergence caps fixed per case in advance**; all arms converged on `residualControl`
  well inside them.
- **The `AR_14_Ret_180` loss accepted in advance, in writing**, with the reason stated:
  keeping ML on AR_14 while switching the other two is exactly the per-case selection the
  rule exists to forbid. **The loss then happened** — 0.0325 → 0.0353, the nominal
  best-on-board tie gone — **and was not reverted.** A pre-registration that never costs
  anything is decoration; this one cost something and was honoured.
- **No test ground truth was reachable.** No `*_LES` file exists in any of the three
  test-duct run directories, though the benchmark ships one for each; both AR_7 arms have
  them, which is where they belong.

And the rule as written prohibits training or validating on test-case *data*. That did not
happen. It does not prohibit reading your own preview scores — the benchmark ships the
test ground truth in the package and instructs submitters to preview.

**Where the package supports no answer at all.** §5.3, the mandatory disclosure list, and
§5.4, the cover email, disclose the round-2 → decline-gate leakage and say nothing about
round 5. The largest single change in the entry — the whole −0.0088 move, and the entire
reason there is a rank claim — was selected in full knowledge of per-case test outcomes,
and there is no disclosure item for it. The lab wrote the concession down in a file that
does not travel with the submission, and left it out of the file that does. **That is
self-inflicted exposure: the honest sentence already exists, in the lab's own words, and
is being withheld by an oversight rather than a decision.** A reviewer who finds
`R5_RULE_FREEZE.md` after reading a disclosure list that omitted it will discount
everything else the list says.

---

### W2. "Your margin is 0.0029. Your own measured seed uncertainty on the model behind three of your eight files is 0.0024. Delete one case and you are rank 2. This is a point estimate wearing a crown."

**The answer the package supports — the honesty, but not the claim.**

§10 already says the lead is not statistically decided, that the standing is two cases
wide, that `alpha_15_13929_2024` alone supplies more than the whole margin and
`NASA_2DWMH` alone costs more than it, and that `AR_1_Ret_360` and `AR_3_Ret_360` are ties
below published precision. All of that is true and I confirmed it independently:

- Case-level bootstrap over the eight scored cases on the frozen CSVs, B = 200,000:
  **P(rank 1) = 0.674.**
- Leave-one-case-out: **drop `alpha_15_13929_2024` and the entry falls to rank 2**
  (0.05030 vs 0.04891). Every other single deletion keeps rank 1.
- Paired per-case differences: **t = 0.50 vs Reissmann, t = 0.96 vs Wu & Zhang** on eight
  cases. Not decided. The leads over Liu et al. and Montoya et al. are.
- `closure_challenge_seed_sensitivity.json` bounds the round-1 PH model's
  overall-equivalent spread at **0.002419 — 84% of the 0.0028863 margin** — and that model
  still produces three of the eight shipped CSVs, including the one case the standing
  rests on.

So the defensible sentence is: *the point estimate is rank 1; on eight cases the ordering
against Reissmann and Wu & Zhang is not resolved; the ordering against Liu and Montoya
is.* The package says close to this already.

**Where the package is exposed anyway.** It computed a quantified P(rank 1) and ruled it
**internal-only**, keeping the number out of the outward artifact while the outward
artifact continues to assert "rank 1 of 5, locally." I never read that internal file — and
I got 0.674 from the shipped CSVs and the public leaderboard in about a minute. **Any
reviewer can.** The withholding therefore buys nothing and costs the one thing the entry
is trading on. If a steward later learns a probability was computed and deliberately
stripped from the outward draft, "we described it qualitatively" will not survive the
sentence in the JSON that says *"INTERNAL ONLY; the figure never appears in an external
claim."*

**Recommendation, and it is the cheapest thing in this report:** put the number in the
external text. "Rank 1 on the point estimate; P(rank 1) ≈ 0.67 by a case-level bootstrap
over eight cases" is a *stronger* claim than "rank 1," because it is the one a competent
reader will believe.

---

### W3. "Half of what you submitted is not your method, and the part that is your method makes things worse on the one case you took it outside its training family. You are not entering a closure model; you are entering a well-chosen file-selection strategy."

**The decomposition, measured, all of it reproducible from the package plus the public
benchmark.** Floor = submit the supplied RANS field unchanged everywhere = **0.1036347**.

| component | cases | contribution to overall |
| --- | --- | --- |
| trained PH ML correction | `alpha_15_13929_4048`, `alpha_15_13929_2024` | **−0.0232** |
| untrained QCR2000 forward solves | 3 ducts | **−0.0239** |
| trained ML on the hump | `NASA_2DWMH` | **+0.00014** (worse than doing nothing: 0.063198 vs baseline 0.062061) |
| the organisers' own file, byte-for-byte | `alpha_05_4071_4048`, `alpha_05_4071_2024` | **0** |
| | | **= 0.056647** |

Three of the eight predictions are the entrant's machine learning. Three are a published
constitutive term any OpenFOAM user can switch on, with a constant that was not fitted.
Two are the file every entrant is handed for free — I confirmed byte-equivalence to the
supplied solve at 4.99e-10, the CSV's own write precision.

**The answer the package supports, and it is better than the charge.** All of this is
disclosed, and disclosed harder than a reviewer would have found it. §8.2 carries the
attribution table and states in the lab's voice that 0.0461 and 0.0719 *"are properties of
a file every entrant is handed for free, and anyone submitting it unchanged scores exactly
the same."* §8.3 identifies the free 0.00014 available by reverting the hump and
**refuses it**, because singling out that case requires knowing its test score — the third
such refusal on the record, after the 0.0066 shortcut of §4.2 and the AR_14 regression.
§10 states plainly that the ducts are "no longer an ML correction at all."

And there is a finding here the steward may value more than the rank, which I verified
independently rather than inherit: **on exactly the two test cases the train-only decline
gate withheld the correction, the supplied baseline beats all four published entries**
(0.046108 against a best published 0.0569; 0.071863 against a best published 0.0760). A
rule fitted on 21 training cases and validated on 4 non-test cases identified, blind, the
two flows on which every published method in the field damages the answer. That is a
result about the benchmark, and it does not depend on the entry's own score at all.

**Where the package supports no answer.** Nothing in it claims the entry demonstrates a
learned closure that beats the board — correctly, because it does not. **But a leaderboard
row carries a name and a number and nothing else.** §4.7 identified exactly this asymmetry
for the two baseline rows and called it the highest-priority disclosure item; the same
asymmetry now applies to three more rows produced by an off-the-shelf published term, and
the disclosure list was never extended to cover them. **A row reading "Certonomous —
0.0566 — rank 1" attributes to a method five of eight predictions that method did not
make.** The package has no plan for that sentence. It should: one line in the cover email,
of the form *"three of our eight predictions are an untrained QCR2000 forward solve and
two are your own baseline unchanged; only three are our model,"* converts the worst
discoverable fact about this entry into its most credible one.

---

## 4. Bottom line

**Reproduced: yes, cold, to the last bit.** Overall 0.056647191704213645, per-case
matching the manifest exactly; 8/8 hashes; ordering verified against the scorer's own
evaluation points at zero difference; all four published entrants re-scoring to their
board values; the RANS floor reproducing at 0.1036347; the three duct CSVs re-derived at
exactly zero deviation from the frozen converged fields; the two declined CSVs re-derived
as the supplied baseline at write precision; the untrained constant confirmed in the
compiled default and absent from every case dictionary; no test-case LES field anywhere in
the run tree.

**The scoring is legitimate and the method is what it says it is.** The exposure is not in
the numbers. It is that the package's *outward* layer — the cover email, the disclosure
list, the description document that does not yet exist — is two rounds behind the payload
it now carries, and that the three strongest honest sentences the lab has already written
(the round-5 leakage concession, the quantified P(rank 1), the five-of-eight attribution)
all live in files that do not travel with the submission.

Four fixes, in order of return: **D2** (update §5.1/§5.2/§5.4 to round 5), **D3** (write
the description document), **D5** (rewrite disclosure items 6, 8, 9 against the round-5
payload and add the round-5 route-selection disclosure from W1), **D4** (fill the
reference URL, or ship the rule freeze inside `test/`'s parent). None requires a scoring
call. None requires new compute. All four are writing.

---

*Pass-3 owner, Ladder V — outside-reviewer frame, cold reproduction 2026-08-10/11.
No package file, record, ledger or score was modified by this pass. No scoring call was
made against the lab's ledger; the benchmark's scorer was run offline against frozen
CSVs, which the tasking permits and which generates no new prediction.*
