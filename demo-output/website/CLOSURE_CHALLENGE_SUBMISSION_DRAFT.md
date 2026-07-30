# Closure Challenge — submission policy, eligibility verdict, compliance audit, and draft package

**Status: RECOMMENDATION ONLY. Nothing has been submitted, no account created, no
one contacted.** Katie's standing instruction is that nothing goes to the challenge
without her proofreading it first. This document exists to be proofread.

Prepared 2026-07-30. Roadmap section 4B: "Must find out closure benchmark
challenge's policies and determine whether Certonomous can submit their result."

---

## 1. Which challenge this is, precisely

**The Closure Challenge — a benchmark task for machine learning in turbulence
modelling.** Steward: Ryley McConkey (MIT).

| Artifact | Location | Verified |
| --- | --- | --- |
| Rules + leaderboard (authoritative) | `https://github.com/rmcconke/closure-challenge-benchmark` | Live README fetched 2026-07-30; **identical** to our local clone at commit `deb9155` |
| Evaluation source | `https://github.com/rmcconke/closure-challenge` | local clone `1c4e22c8` |
| PyPI package | `closure-challenge` | `pip install closure-challenge` |
| Preprint | `https://arxiv.org/abs/2603.28884`, DOI `10.48550/arXiv.2603.28884` | submitted 2026-03-30, CC BY 4.0 |

The README states it, not the paper, is authoritative: *"We now have an arXiv
preprint for the challenge. However, **this page is the main source of up-to-date
information**."*

**Freshness check.** The GitHub API reports `pushed_at: 2026-05-04T18:33:35Z` and the
current HEAD is `deb9155 add wang submission` (2026-05-04) — the same commit our local
clone sits on. The rules quoted below and the four-entry leaderboard are current as of
today. The evaluation repo's last push was `2026-03-26`.

---

## 2. The rules, in the operative wording

Every quote below is verbatim from the benchmark README at `deb9155`, re-verified
against the live page today.

### 2.1 Who may enter

**There is no eligibility clause of any kind.** Not in the benchmark README, not in
the evaluation package README, not in the arXiv preprint. The only participation
language is inclusive:

> "If you have questions or suggestions as this challenge is developed, please open an
> issue in this repo. **This is a community effort!**"

> "This is an **ongoing** challenge. It is not associated with any particular
> conference or event."

No academic affiliation is required, no fee, no registration, no account, no
institutional sponsorship. **This is an absence of a restriction, reported as an
absence** — the documents do not say "companies may enter"; they say nothing about
who may enter at all.

### 2.2 The one strict rule

> "The only strict rule in this challenge is:
>
> It is **strictly forbidden** to train or validate on any data from the **test
> cases** in the table below. The purpose of this benchmark is to provide an honest
> evaluation and comparison between various ML techniques in turbulence modelling. If
> you are found to have **trained** or **validated** on any of the test cases, your
> submission will be automatically withdrawn, and a note will be made on the
> leaderboard."

The preprint states the same rule more tersely (Section 2, *Challenge task and
rules*): *"The only strict rule with this challenge is: it is forbidden to train or
validate on any of the test cases."* It adds the permission: *"You can train on
similar flows to the test cases (for example, different parametric variations of the
periodic hills case)."*

The evaluation package README repeats it as a closing reminder:

> "**Reminder: DO NOT *train* or *validate* on any of these cases. In other words, you
> cannot use them during training in any way. This violates the challenge rules.**"

**The eight test cases** (`closure_challenge.case_names()`): `alpha_15_13929_4048`,
`alpha_15_13929_2024`, `alpha_05_4071_4048`, `alpha_05_4071_2024`, `AR_1_Ret_360`,
`AR_3_Ret_360`, `AR_14_Ret_180`, `NASA_2DWMH`.

The sanction is stated and it is severe: automatic withdrawal plus a permanent note on
the leaderboard.

### 2.3 Everything else is unrestricted

> "**You are free to use your own input features, base turbulence model, data
> assimilation technique, etc.** We have relaxed these rules based on community
> feedback."

> "Other than this strict requirement, **you are free to use your own
> training/validation data**."

> "The benchmark task is to **predict the flow field** for a series of test cases
> given a specified training and validation dataset, as well as a given CFD mesh.
> **All other decisions are left to the submitter.**"

The train/validation split in the README table is explicitly labelled *"(suggested)"*.
Only the **Test** column is binding.

### 2.4 Submission format and mechanism

> "You must submit your predictions on the test dataset in **CSV format**."
>
> "1. Save your interpolated predictions in CSV format under the respective
> directories in the `test` subdirectory of the benchmark dataset. [...]
> 2. You can preview what your score will be using the benchmark dataset's python
> package.
> 3. Send your `test` subdirectory to Ryley McConkey: rmcconke@mit.edu . **Also
> include a list of all authors, and any relevant references** (e.g., papers, github
> repos, etc.)
> 4. The benchmark steward (currently, Ryley McConkey) will evaluate your predictions,
> and update the leaderboard accordingly."

Confirmed from the four accepted submissions in `submissions/`: each case file is
**1000 rows × 3 columns** (Ux, Uy, Uz), comma-delimited, **no header**. Two accepted
layouts exist in the repo — flat `{case}.csv` (wu, montoya, wang) and
`{case}/predictions.csv` (reissmann).

### 2.5 Cadence, submission count, scoring-call limit, deadline

> "Submissions are accepted anytime!"

**There is no submission limit, no scoring-call limit, and no deadline stated
anywhere.** There cannot be a scoring-call limit in the technical sense: the
evaluation package ships the test ground truth locally as
`src/closure_challenge/data/ground_truth_test.npz`, and the README *instructs*
submitters to preview their score with it. `evaluate_by_case()` — per-case test scores
— is a documented, first-class public function of the package.

> **This matters for how we describe ourselves.** Certonomous's "four official scoring
> calls, ever" is a **self-imposed discipline, stricter than the benchmark requires**.
> It is not compliance with a rule. Any public statement of ours must not imply the
> benchmark rations scoring calls, because it does not.

### 2.6 Disclosure, reproducibility, authorship

The only stated requirement is *"a list of all authors, and any relevant references."*
There is **no** required description document, no reproducibility mandate, no code
release requirement, no pre-registration.

In practice the steward links each leaderboard row to whatever the submitter provided:
a notebook (reissmann → `score_eval.ipynb`), a PDF description document (wu →
`description_document.pdf`), an arXiv paper (liu → `arxiv.org/abs/2509.17189`), or a
journal DOI (montoya → `10.1007/s10494-025-00661-8`). The reissmann submission's
`reissman_info.txt` is an informal plain-text note listing method references. **The
disclosure bar is low and informal.** Nothing stops us from exceeding it, and §5
argues we must.

The leaderboard column is headed **"Authors"** and all four current rows are personal
names, not organisations.

### 2.7 Licensing and data-use terms — the genuinely unresolved area

**Report this as unresolved. It cannot be settled from public sources.**

| Asset | Stated licence | How verified |
| --- | --- | --- |
| Benchmark repo (rules, data, submissions) | **None.** GitHub API `license: null` | API call, 2026-07-30 |
| Evaluation package | **MIT**, per `pyproject.toml` (`license = {text = "MIT"}`, OSI MIT classifier) | local clone `1c4e22c8` |
| Evaluation *repo* on GitHub | **None.** API `license: null` | API call — inconsistent with the package metadata above |
| arXiv preprint | **CC BY 4.0** | arXiv abstract page |
| PH training data (`xiaoh/para-database-for-PIML`) — **the source of our 21 training cases** | **None.** API `license: null` | API call |
| Duct DNS (vinuesalab.com/duct) | No terms stated on the page; four papers listed for citation | page fetch |
| ERCOFTAC KB Wiki | **"Content is available under CC BY 4.0 (AI/ML-training & TDM reserved)"** — ML training expressly reserved | page fetch of DNS 1-6 |

**The ERCOFTAC reservation does not bite on us, and that is a checkable claim, not a
convenient one.** ERCOFTAC supplies only the challenge's *3D* cases (wing-body
junction DNS 1-6, Ahmed body case082). Those are not among the eight test cases and
are not in the train/validation table. Our pipeline trains on the 21+4 parametric
periodic-hill cases (xiaoh), the four `Ret_180` ducts (Vinuesa), CBFS and PH_Breuer
(NASA TMR). **No ERCOFTAC-derived data enters our model.**

What remains genuinely ambiguous: a commercial entity has **no explicit grant of
rights** to train on the benchmark's redistributed data, because neither the benchmark
repo nor the primary PH training dataset carries any licence at all. Mitigating, and
substantial: a submission consists of *our predicted velocity vectors on the
organisers' evaluation points*, which is not redistribution of anyone's source
dataset. This lowers the practical risk a long way but does not make the grant exist.
**Flagging rather than resolving optimistically.**

---

## 3. Eligibility verdict

### Can Certonomous submit? **Yes — on the rules as written, with two things to ask first.**

| Question | Verdict | The rule it rests on |
| --- | --- | --- |
| May a company enter? | **Yes.** No eligibility clause exists in any of the three documents. Participation is framed as open ("This is a community effort!") | §2.1 — absence of restriction |
| Must we be academics / have a paper? | **No.** The only stated requirement is authors + "any relevant references (e.g., papers, github repos, etc.)" | §2.4, §2.6 |
| Is registration or an account needed? | **No.** Submission is an email with a directory attached | §2.4 |
| Is there a deadline we might miss? | **No.** "Submissions are accepted anytime!" | §2.5 |
| Have we used up a submission allowance? | **No such allowance exists.** No submission or scoring limit is stated | §2.5 |
| Does our method qualify? | **Yes.** Post-hoc velocity-field correction is permitted: "You are free to use your own input features, base turbulence model, data assimilation technique, etc." and "All other decisions are left to the submitter" | §2.3 |
| Do we violate the one strict rule? | **No** — see the audit in §4, which checks the code rather than the prose | §2.2 |

### The two genuine ambiguities, and who resolves each

1. **Author line for a company.** The leaderboard column is "Authors" and every
   current row is personal names. Whether Certonomous may appear as the credited
   entity, or must credit named individuals with Certonomous as affiliation, is not
   addressed anywhere. **Recommendation: submit under named individuals with
   Certonomous as the affiliation, and ask the steward whether a company name on the
   row is acceptable.** Do not assume the more flattering reading.
2. **Data-use rights for commercial training.** §2.7. Unresolvable from public
   sources — the relevant repositories carry no licence.

**Who to ask, when Katie decides to ask:** Ryley McConkey, `rmcconke@mit.edu` (named
as steward in the submission instructions), or a public issue on
`rmcconke/closure-challenge-benchmark` — the README invites exactly this: *"If you
have questions or suggestions as this challenge is developed, please open an issue in
this repo."* A public issue also creates a citable record of having asked. **Not
contacted. Katie's call.**

---

## 4. Adversarial compliance audit of the entry of record

The brief was to be adversarial and to prefer finding a problem now over a withdrawal
later. Findings are ordered worst-first. **Two defects were found. Neither is a rule
violation; both must be fixed before anything is sent.**

### 4.1 The one strict rule: NOT VIOLATED — verified in code, not taken on trust

I audited `sdk/scripts/apply_closure_ph_gate.py` and
`sdk/scripts/closure_baseline_error_gate.py` line by line rather than relying on the
prose in `CLOSURE_CHALLENGE_STATUS.md`.

- Ground-truth reads (`_load_ground_truth_U`) occur at line 115 inside
  `for case in gate._PH_TRAIN` (21 training cases) and at line 215 inside
  `for c in ph._PH_TRAIN` (same 21). **Both loops are over training cases only.**
- The test-case loop (lines 165–167) calls `ph._load_rans_fields` only, annotated
  `# no U_LES read`. Features for the four PH test cases are built from the RANS field
  and mesh alone.
- `closure_baseline_error_gate.py` enforces the split with executable assertions, not
  comments: `assert len(_PH_TRAIN) == 21 and len(_PH_VAL) == 4`, `assert not
  (set(_PH_TRAIN) & set(_PH_VAL))`, `assert not ((set(_PH_TRAIN) | set(_PH_VAL)) &
  set(_PH_TEST))`. The test list is imported *solely* to assert non-intersection.
- The 21/4 split matches the benchmark's own suggested split exactly. The four
  validation cases used (`alpha_05_10071_*`, `alpha_15_7929_*`) are the README's
  suggested validation cases and are **not** test cases. The gate never saw a test case
  during fitting or validation.
- Using the *test meshes* is not merely permitted but required: the task is "predict
  the flow field [...] given [...] a given CFD mesh."

**Verdict: the gate fitted on 21 and checked against 4 is clean.** It is the single
strongest part of the entry.

### 4.2 The refused shortcut: correctly refused

Switching the correction off on three named cases would have scored 0.0675. Knowing
*which* three required reading round-2's per-case test scores. That is per-case model
selection on test outcomes — "validating on the test cases" in the ordinary ML sense,
and squarely what the rule exists to prevent. **The refusal was correct and it is the
most defensible decision in the record.** The honest route cost 0.0001.

### 4.3 The residual soft leakage — real, already disclosed, and the thing a reviewer will press on

The lab's own record states it plainly (round-3 JSON,
`leakage_statement.motivation_provenance_stated_for_the_reviewer`): *"The gate's
MOTIVATION came from round 2's official call — we knew those cases were worse than
doing nothing because the test harness told us. That is soft, adaptive leakage, and it
is real."*

**Adversarial reading:** across rounds, test feedback influenced which machinery got
built and deployed. Researcher degrees of freedom were exercised with knowledge of test
outcomes. A strict reviewer can call that validating on the test set.

**The defence, and it is a good one:**
- The rule prohibits *training or validating on* test-case data. The gate's every
  parameter — screened features, RidgeCV alpha, standardisation, coefficients, the
  0.1263 threshold — derives from 21 training cases and was reproduced byte-for-byte
  from train-only data before touching test features (`matches_c1_recorded_values:
  true`, alpha 0.7499, threshold 0.1263).
- The gate is a deterministic train-only function. Seeing round-2's scores changed
  *when* it was applied, not *what* it outputs. Its four test decisions
  (0.1503, 0.1525 → apply; 0.0420, 0.0034 → decline) would have been identical had
  round 2 never been scored.
- It was validated for generalisation on **non-test** data first — AUC 1.0, 4 of 4 —
  and only then applied.
- Most importantly: **the benchmark itself sanctions per-case test previewing.** It
  ships the ground truth in the package, instructs submitters to "preview what your
  score will be," and exposes `evaluate_by_case()` as public API. An interpretation
  under which observing per-case preview scores is itself a violation would make the
  benchmark's own documented workflow a violation.

**Verdict: not a violation of the rule as written. Residual risk: low but non-zero,
and it is interpretive rather than factual.** It must be disclosed in the cover
material — the record's own instinct here is right, that a reviewer should *find* it
written down rather than discover it.

### 4.4 DEFECT 1 — a false sentence in a file the disclosure relies on

`sdk/scripts/apply_closure_ph_gate.py`, docstring line 37:

> "Exactly ONE closure_challenge.score()/evaluate_by_case() call is made, on the final
> 8-case predictions dict."

**This is not what the code does.** The same run calls `score(floor_predictions)` and
`evaluate_by_case(floor_predictions)` at lines 205–206, then `score(predictions)` and
`evaluate_by_case(predictions)` at lines 288–289 — **four invocations, two prediction
sets.**

**Substantively harmless:** the extra pair re-scores the RANS-identity floor, an
unmodified baseline already scored as ledger call #1, reproducing 0.1036 as a harness
check. It conveys no new information and cannot tune anything.

**But it must be fixed.** The ledger's "four official scoring calls" counts *distinct
prediction sets scored*, which is a defensible and meaningful unit. The docstring
states something stronger and demonstrably false. An entry whose entire credibility
rests on precise self-accounting cannot ship with a sentence a reviewer can falsify by
reading forty lines further down the same file. **Correct the docstring to state the
unit being counted, before submission.**

### 4.5 DEFECT 2 — there is no submittable artifact

**No prediction CSV has ever been written.** Searched the repository and the filesystem:
the only files matching the required names belong to other entrants
(`closure-challenge-benchmark/submissions/{wu,montoya,wang}`) and the package's own test
fixtures. `apply_closure_ph_gate.py` contains no CSV-writing code at all — the entry of
record exists as an in-memory `predictions` dict and a JSON of *scores*.

**The entry of record is currently a number, not a submission.** Producing the eight
CSVs requires re-running the pipeline with a CSV dump added.

**This does not require a fifth scoring call, and must not be allowed to become one.**
Recommendation: add CSV output and run with the `score()`/`evaluate_by_case()` calls
disabled, then verify the files are 1000×3 by inspection alone. The scores are already
recorded; re-deriving them buys nothing.

### 4.6 Version label understates the metric revision

`closure.html` and the round-3 JSON both record the evaluation package as **v0.2.1**.
At the pinned commit `1c4e22c8`, `pyproject.toml` declares `version = "0.3.1"` and the
commit message reads *"v0.3.1: vector magnitude metric, mean over cases."* Upstream
simply never bumped `__version__` in `__init__.py`; our record faithfully reports what
the package reports itself as. **Nothing is wrong with the score** — but "v0.2.1"
names an older metric revision than the code actually used. **Cite the commit hash
`1c4e22c8`, which is unambiguous, and drop or footnote the version string.**

### 4.7 The reputational exposure: two of five "best on board" rows are the organisers' own baseline

On `alpha_05_4071_4048` (0.0461) and `alpha_05_4071_2024` (0.0719) our submitted
prediction *is the unmodified RANS solve* — the gate declined, correctly, and we report
the baseline. Those two values beat every published ML entry on those cases.

**Not a rule violation.** Submitting an uncorrected field is a legitimate prediction,
and the gate deciding to withhold is the method working. `closure.html` already states
this without hedging ("It is not our model outperforming anyone").

**But the exposure is real and it is asymmetric.** If a leaderboard row credits
Certonomous with the best score on two cases and a reader later works out those are the
organisers' own baseline fields, the discovery is far more damaging than the
disclosure. **This belongs in the submission email itself, not only on our website.**
Highest-priority disclosure item.

### 4.8 Leaderboard position is current

Verified today against the live README: the four-entry board is unchanged since
2026-05-04. 0.0676 would sit between rank 2 (0.0624) and rank 3 (0.0737). The challenge
is ongoing with no deadline, so this can change without notice — the claim should be
dated wherever it appears.

### 4.9 Summary

| Item | Finding |
| --- | --- |
| The one strict rule | **Not violated** — verified in code |
| Gate fitted on 21, checked on 4 | **Clean** — matches the benchmark's own suggested split |
| Refused 0.0675 shortcut | **Correctly refused** |
| Adaptive leakage across rounds | **Not a violation as written**; low residual interpretive risk; must be disclosed |
| Docstring scoring-call claim | **DEFECT — false as written.** Fix before sending |
| Submittable CSVs | **DEFECT — do not exist.** Generate without a new scoring call |
| Eval package version label | Understates metric revision; cite the commit hash |
| Two raw-RANS "best on board" rows | Legitimate; **must be disclosed in the email** |

**Nothing found rises to a withdrawal risk under the rule as written.**

---

## 5. Draft submission package — FOR PROOFREADING, NOT FOR SENDING

### 5.1 What would be sent

1. A `test/` directory containing eight files, 1000 rows × 3 columns, comma-delimited,
   no header: `alpha_15_13929_4048.csv`, `alpha_15_13929_2024.csv`,
   `alpha_05_4071_4048.csv`, `alpha_05_4071_2024.csv`, `AR_1_Ret_360.csv`,
   `AR_3_Ret_360.csv`, `AR_14_Ret_180.csv`, `NASA_2DWMH.csv`. **These do not yet
   exist** (§4.5).
2. An author list with affiliation.
3. A description document (following wu's precedent), containing §5.3 and §5.4 below.

### 5.2 Claims the package makes

| Claim | Value | Source |
| --- | --- | --- |
| Overall score | **0.0676** | `closure_challenge_trained_entry_round3_gated.json`, `official_test_harness_result.round3_gated_overall` |
| RANS-identity floor, our harness | **0.1036** | same record, reproduced in-run |
| Improvement over floor | **−0.0360, 34.7% below** | derived |
| Per-case | 0.0501 / 0.1011 / 0.0461 / 0.0719 / 0.0919 / 0.0862 / 0.0303 / 0.0632 | same record |
| Scored with | benchmark's own unmodified scorer, package commit `1c4e22c8`, benchmark commit `deb91557` | `harness_check` |

**No number here is adjusted, rounded favourably, or restated to fit a rule.** If the
steward's own scoring differs from ours, the steward's number is the number.

### 5.3 What the description document must disclose — non-negotiable

1. **Method class.** Post-hoc velocity-field correction: target `delta_U = U_LES −
   U_RANS` per cell, `HistGradientBoostingRegressor` ×3 on 7 features (Pope's 5 scalar
   invariants, `Re_y`, `tke_ratio`), applied once to a converged RANS field as
   post-processing. **It does not modify the turbulence model and nothing is
   re-solved.** This is a materially weaker claim than the FIML/TBNN/SpaRTA family it
   is being ranked against, and saying so is the point.
2. **Two cases are uncorrected baseline.** State outright that on
   `alpha_05_4071_4048` and `alpha_05_4071_2024` the submitted field is the unmodified
   RANS solve, that the gate declined there, and that any leaderboard-best status on
   those two cases is the baseline's, not our model's (§4.7).
3. **The full adaptive-leakage history**, in our own words before anyone asks: that
   round 2's per-case preview scores motivated building the gate; that the gate's
   parameters come only from 21 training cases; that it was validated on 4 non-test
   validation cases at AUC 1.0 before ever being pointed at a test case; and that a
   0.0675 shortcut requiring per-case selection on test outcomes was identified and
   refused, at a cost of 0.0001 (§4.2, §4.3).
4. **Train/val/test discipline**, with the executable assertions cited (§4.1).
5. **The NASA hump regression of +0.0011 was not reverted**, because reverting after
   seeing the per-case result would itself be selection on test outcomes.
6. **Known limitations**: two of seven features (`I3_S3`, `I4_W2S`) are algebraically
   identically zero across the entire duct family, so the model is structurally blind
   on those cases — a negative result we found and would rather publish than have
   inferred from our duct scores.
7. **Scoring-call count, correctly framed**: four distinct prediction sets scored, as a
   self-imposed discipline, **explicitly not** compliance with any benchmark limit,
   since none exists (§2.5).

### 5.4 Draft cover email — DRAFT, NOT SENT

> **To:** rmcconke@mit.edu
> **Subject:** Closure Challenge submission — Certonomous (overall 0.0676)
>
> Dear Dr McConkey,
>
> Please find attached a `test/` directory with predictions for the eight test cases,
> in the CSV format described in the benchmark README.
>
> Authors: [NAMES — Katie to fill]. Affiliation: Certonomous.
> Reference: [repository or write-up URL — Katie to fill].
>
> Our overall score under the benchmark's unmodified scorer (package commit
> `1c4e22c8`, benchmark commit `deb91557`) is **0.0676**, against a RANS-identity
> floor of 0.1036 reproduced on the same harness.
>
> Three things we would rather state up front than have found:
>
> 1. Our method is a **post-hoc velocity-field correction** applied to an already
>    converged RANS solution. It does not modify the turbulence model and nothing is
>    re-solved with the correction folded in.
> 2. On `alpha_05_4071_4048` and `alpha_05_4071_2024`, our submitted field **is the
>    unmodified baseline RANS solve.** A decline gate — fitted on 21 training cases,
>    validated on 4 held-out validation cases, never on a test case — determined that
>    correcting those cases would make them worse, and withheld the correction. Where
>    those entries score well, the credit belongs to the baseline, not to our model.
> 3. The attached description document sets out our full disclosure, including the
>    fact that the *motivation* for building that gate came from observing our own
>    per-case preview scores in an earlier round, and that we identified and declined a
>    variant that would have scored 0.0675 because selecting it required choosing cases
>    by their test outcomes.
>
> Two questions, if you have a moment:
>
> - The leaderboard credits "Authors." Is a company name acceptable on a row, or do you
>   prefer named individuals with affiliation?
> - Neither the benchmark repository nor the `para-database-for-PIML` dataset carries a
>   licence file. Are there terms of use we should be aware of for a commercial entity
>   training on this data?
>
> [SIGN-OFF]

### 5.5 Risks, stated plainly

| Risk | Severity | Mitigation |
| --- | --- | --- |
| A reviewer reads the cross-round adaptive leakage as validating on test | **Low–moderate** | Disclose first and in full (§5.3.3). The rule as written is not breached |
| The two raw-RANS leaderboard-best rows are discovered rather than disclosed | **Moderate reputational** | Put it in the email itself, item 2 |
| Steward's rescoring differs from ours | Low | We used the unmodified scorer at a pinned commit; publish the hashes |
| Commercial data-use rights are absent | **Unresolved** | Ask in the email; note we redistribute no source data |
| The false docstring is found | Low but avoidable | Fix before sending (§4.4) |
| Rank shifts before the steward processes it | Low | No deadline; date every position claim |
| Position claim goes stale on our website | Low | Re-verify the leaderboard when Katie approves |

### 5.6 Required before anything is sent

1. Fix the docstring in `apply_closure_ph_gate.py` (§4.4).
2. Generate the eight CSVs **without** a new scoring call (§4.5).
3. Correct the eval-package version label to the commit hash (§4.6).
4. Katie fills the author names and the reference URL.
5. **Katie proofreads and approves.** Nothing moves before this.

---

## 6. What was not done, deliberately

Nothing was submitted. No account was created. No one was contacted — not the steward,
not by email, not via a GitHub issue. No score or claim was altered. Where public
sources do not establish a rule (commercial data-use rights, company author lines),
this document says so rather than inferring a convenient answer.
