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
| Preprint | `https://arxiv.org/abs/2603.28884`, DOI `10.48550/arXiv.2603.28884` | submitted 2026-03-30, CC BY 4.0. **Full text retrieved and read 2026-08-02** (`arxiv.org/html/2603.28884v1`, HTTP 200) — see §2.2 and §9 |

The README states it, not the paper, is authoritative: *"We now have an arXiv
preprint for the challenge. However, **this page is the main source of up-to-date
information**."*

> **STOP — SUPERSEDED 2026-08-11. THE BOARD MOVED AND THIS PACKAGE HAS NOT BEEN
> REWRITTEN FOR IT.** Fetched live 2026-08-11T23:33Z by two independent routes, the
> leaderboard carries **six** entries, not four, and a **new leader: Yang, 0.0580**
> (`campaign/BOARD_MOVED_2026-08-11.md`). Three things below are now false as
> written, and are struck in place rather than smoothed:
> **(1)** the board is six-deep and our margin over Yang is **0.001365**, not
> 0.002878 over Reissmann; **(2)** P(rank 1) is **50%** with a 95% interval of
> **0–97%**, and **four** comparisons are not statistically decided — Yang
> (t = −0.19), Reissmann (−0.50), Wu & Zhang (−0.95) and Tian, Buchanan, Hickel &
> Dwight (−1.03) — where two were before; **(3)** best-on-board is **2 of 8** and
> **both survivors are the organisers' own baseline rows, so the count belonging to
> our model is ZERO of 8.** Sources:
> `campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md`. **Submissions remain
> PARKED and reserved to Katie; nothing here has been sent.**

~~**Freshness check.** The GitHub API reports `pushed_at: 2026-05-04T18:33:35Z` and the
current HEAD is `deb9155 add wang submission` (2026-05-04) — the same commit our local
clone sits on. The rules quoted below and the four-entry leaderboard are current as of
today.~~ **Struck 2026-08-11: `git ls-remote origin HEAD` now returns `d572d40c`, not
`deb91557`. The upstream HEAD moved and the board moved with it.** The freshness check
above was sound on its own date; what it lacked was an expiry, and re-running it costs
one `git ls-remote` — which reads the remote without moving the clone or the frozen pin.
The evaluation repo's last push was `2026-03-26`.

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

> **VERIFIED 2026-08-02. The flag below is cleared and the quotation stands.**
> Both sentences were retrieved from the preprint itself and matched verbatim,
> character for character. They are in **Section 2.1, *Test cases***, a
> subsection of Section 2 *Challenge task and rules* — the earlier attribution
> to "Section 2" was correct but coarser than it needed to be.
>
> **Source:** `https://arxiv.org/html/2603.28884v1`, HTTP 200, retrieved
> 2026-08-02 05:14 UTC, full text held at
> `/tmp/.../scratchpad/arxiv_2603.28884.{html,txt}` for the length of that
> session. In the paper's own order the two sentences are adjacent and run:
> *"The test cases cannot be used in any way at training time. You can train on
> similar flows to the test cases (for example, different parametric variations
> of the periodic hills case). More details of the provided datasets are given
> in Section 3."*
>
> The permission the compliance argument leans on **exists and is granted in
> the words we attributed to it.** The earlier finding — that neither sentence
> is anywhere in the benchmark clone, the evaluation package or this repository
> — was correct and remains correct; the sentences are in the preprint, and no
> copy of the preprint was on this machine until now. The flag was raised for
> the right reason and is retired on evidence rather than on patience.

The preprint states the same rule more tersely (Section 2.1, *Test cases*, under
Section 2 *Challenge task and rules*): *"The only strict rule with this challenge
is: it is forbidden to train or validate on any of the test cases."* It adds the
permission: *"You can train on similar flows to the test cases (for example,
different parametric variations of the periodic hills case)."*

> **A discrepancy in the preprint, found while verifying the above, and it cuts
> the other way.** The preprint's own Section 2.1 list of the four periodic-hill
> test cases gives **α = 1.5 for all four** — its LaTeX source carries
> `\alpha=1.5` four times. The benchmark's authoritative case names give
> **α = 0.5** for two of them: `alpha_05_4071_4048` and `alpha_05_4071_2024`,
> consistent with the README's own suggested-validation names
> `alpha_05_10071_*` and `alpha_15_7929_*`, which fix the naming convention
> beyond doubt. **The preprint misstates α on two of the four PH test cases.**
>
> Nothing in our entry depends on it — the eight CSVs are keyed by
> `closure_challenge.case_names()`, not by the preprint's geometry table — but
> it is a concrete instance of the README's own warning that *"this page is the
> main source of up-to-date information"*, and it is the reason no rule in this
> document is sourced to the preprint where the README states the same thing.

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
> calls, ever" *(as this round-3-era finding was written; the cumulative count is six
> after round 5's 2026-08-07 call -- the ledger stood at six as of frame `c143d4c0`)*
> is a **self-imposed discipline, stricter than the benchmark requires**.
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

> ## 📌 CURRENCY BLOCK — §4 WAS WRITTEN AGAINST ROUND 3 AND THE ENTRY OF RECORD IS ROUND 5
>
> *Added 2026-08-11 by the Ladder V rung V6 currency pass. **Nothing in §4.1–§4.9 below is
> rewritten or deleted** — every finding was true of the entry it audited, and a finding
> that has since been resolved or superseded is worth more with its resolution beside it
> than edited away. Each of the nine gets an explicit round-5 verdict here, and the
> untrained duct path gets the compliance line it never had. V6's earlier verdict was
> **PASS ON THE RULE, FAIL ON CURRENCY** (`campaign/LADDER_V_PASS2_2026-08-11.md` §2); this
> block is what the currency half was failing for.*
>
> **The entry of record is round 5**, scored 2026-08-07 at commit `07a7fe9e`:
> **0.056647191704213645** overall (`closure_challenge_round5_qcr.json`,
> `official_test_harness_result`). §4 audits round 3 (0.0676). Round 5 differs from round
> 4 in the **three duct rows only** — verified here with `filecmp` over the two submission
> directories: `NASA_2DWMH` and all four `alpha_*` CSVs are byte-identical to round 4,
> `AR_1_Ret_360`, `AR_3_Ret_360` and `AR_14_Ret_180` are not.
>
> ### Every §4 finding, with its round-5 verdict
>
> **ROW-BY-ROW RE-CHECK AGAINST THE SECTIONS, 2026-08-15.** Every row below was compared
> against the section it summarises, not only against the evidence it cites, because a block
> that went stale in one row is the kind of thing that went stale in others. Result: **eleven
> rows, one stale — §4.8, repaired above.** Ten of the eleven are byte-identical to what
> `472f9f92` wrote (sha256 of each line, HEAD against `git show 472f9f92:`), the eleventh being
> §4.7, corrected 2026-08-12. Byte-identity is not the finding, though — §4.8 was byte-identical
> *and* wrong, and §4.1–§4.6 and §4.9 are byte-identical *and* still right, re-executed at HEAD:
> the six code anchors, the `filecmp` split (five CSVs identical, the three ducts not), the eight
> CSVs at 1000×3 with `bb8d61fb…` on `AR_1_Ret_360.csv`, `R5_RULE_FREEZE.md` line 11 at `0bade54a`,
> the four call sites, and `MANIFEST.json:37` / `README.md:52–54`. §4.7's four external surfaces
> were re-read too and all four still carry the organiser-baseline qualification in the same
> sentence as the count. **A row can go stale without anyone editing it**, which is why the test
> here is the section and the world, not the diff.
>
> | § | the finding as written | ROUND-5 VERDICT | verified how, at HEAD |
> |---|---|---|---|
> | **4.1** | the one strict rule: not violated | **HOLDS, over less ground.** Round 5's three duct rows are converged forward solves with **no fit at all**, so the fitted machinery now reaches 5 of 8 rows: two corrected hills, `NASA_2DWMH`, and two rows the gate declined | Read at HEAD, not inherited: ground-truth reads at `apply_closure_ph_gate.py:128` (inside `for case in gate._PH_TRAIN:  # 21 cases, train only`, line 126) and `:228` (inside `for c in ph._PH_TRAIN:`, line 225); the test loop at `:178` calls `_load_rans_fields` at `:179` annotated `# no U_LES read`; the three executable assertions at `closure_baseline_error_gate.py:84–86` |
> | **4.1** *(citations)* | *the line numbers* | **RESOLVED, and the fix is on this page.** 115 / 215 / 165–167 → 128 / 228 / 178–180 | The currency note directly below; all three re-read at HEAD above |
> | **4.2** | the refused 0.0675 shortcut | **HOLDS, untouched.** Round 5 changed no PH row, so the refusal it describes is still the operative decision | The four `alpha_*` CSVs are byte-identical between the round-4 and round-5 packages (`filecmp`), and `round5_per_case` equals `round4_per_case` on all four |
> | **4.3** | residual soft adaptive leakage (round 2) | **HOLDS AND IS INCOMPLETE, which is worse than stale.** Round 5 introduced a **second, larger** instance that §4.3 cannot mention because it postdates it: the round-5 route was chosen while the per-case round-4 duct scores were known | `campaign/R5_RULE_FREEZE.md` at the frozen commit `0bade54a`, line 11: *"we already know the round-4 test-duct scores (0.0811 / 0.0775 / 0.0325)"* — read with `git show` at the commit, not from the mutable file. **Closed outward** as disclosure 3b of `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md` |
> | **4.4** | DEFECT 1, the false docstring | **RESOLVED AND STILL TRUE — the row below is MOOT and stays for the record.** §4.9 still lists it as *"DEFECT — false as written. Fix before sending"*; it was fixed on 2026-07-30 and the fix holds at HEAD | Docstring lines 37–53 state one *new* prediction set, the unit being counted, and **four** invocations; the call sites are exactly four, at `:218–219` (floor) and `:301–302` (entry). Two prediction sets, one new |
> | **4.5** | DEFECT 2, no submittable artifact | **RESOLVED FOR ROUND 5 — the §4.9 row is MOOT and stays for the record.** §4.5's own resolution block describes the **round-3** CSVs; the round-5 package is a different set of files and is verified separately | All eight `closure_challenge_submission_round5/test/*.csv` re-read here: **1000 rows × 3 columns, comma-delimited, no header** (no alphabetic character outside the `e` of scientific notation). `AR_1_Ret_360.csv` hashes to `bb8d61fb…`, the value Pass 1 traced end-to-end in V4 |
> | **4.6** | version label understates the metric revision | **HOLDS, and is now DISCHARGED where it travels.** The recommendation was to cite the commit hash rather than the version string; the round-5 package does both, and states it as an install hazard rather than a footnote | `closure_challenge_submission_round5/MANIFEST.json:37` `eval_package_version_string_note`; `README.md:52–54` |
> | **4.7** | two of five best-on-board rows are the organisers' baseline | **HOLDS; the COUNT WAS STALE TWICE and the DISCLOSURE is now discharged.** The heading said *"two of five"*; ~~round 5 records **four of eight**, two of which are the declined baseline rows~~ *(struck 2026-08-12: that correction was itself measured against the four-entry board and was falsified within the day)*. Against the live six-entry board the count is **2 of 8, both of them the declined baseline rows, so the count belonging to our own model is ZERO of 8**. The substance — that the exposure is asymmetric and belongs in the outward material — is unchanged and is now met | The four external surfaces (`benchmarks.html`, `benchmarks.json`, `wall/wall.json`, `build_benchmarks.py`) carry the organiser-baseline qualification in the same sentence as the count; `scripts/self_audit.py` no longer holds a copy of the count — it re-derives it from the board in `sdk/scripts/probability_of_rank.py` and fails the wall if the stated count disagrees or travels without the baseline disclosure |
> | **4.7** *(asymmetry)* | *the argument itself* | **EXTENDED to the three QCR rows, which §4.7 could not have reasoned about.** The same asymmetry applies to a published 25-year-old term any entrant may run, and which the entry above ours already runs | `DESCRIPTION_DOCUMENT.md` §2 table and §6 |
> | **4.8** | leaderboard position is current | **FALSIFIED 2026-08-11 — AND THIS ROW WAS THE STALE HALF OF THIS DOCUMENT FOR FOUR DAYS. CORRECTED 2026-08-15.** ~~HOLDS ON ITS OWN TERMS, AND "CURRENT" IS NOT CERTIFIED HERE. The board is read from a clone frozen at `deb91557` (2026-05-04). §4.8's own mitigation is to date the claim wherever it appears, and every position claim in the corpus is dated to that commit — so the claim is honest, and re-verifying it needs a network read this pass did not perform.~~ **Struck 2026-08-15: the network read this row said was not performed WAS performed, on 2026-08-11, and it falsified the section this row grades.** The read that produced the current verdict: **two independent live fetches on 2026-08-11** — the rendered GitHub project page and `raw.githubusercontent.com/rmcconke/closure-challenge-benchmark/main/README.md` — recorded in `campaign/BOARD_MOVED_2026-08-11.md`, **added at commit `9cb2a20a`**, and carried into §4.8's own heading **at commit `5c9c63fb`**; re-verified unchanged by a read-only fetch at **2026-08-14T21:01Z**, recorded in `campaign/BOARD_RESCORE_2026-08-14.md`. **The board that read was made against, identified as §5.3's binding rule requires — by ENTRANT COUNT and RETRIEVAL DATE, never by a commit:** the **six**-entry board retrieved **2026-08-11T23:33Z**, re-verified unchanged **2026-08-14T21:01Z**. `deb91557` is not an admissible identifier for it: that is the frozen **four**-entry scoring clone, and it scores but does not rank. What the row got wrong is not the caution — it is that the caution had already been overtaken: the difference between *"we have not checked"* and *"we checked and it changed"* is the whole of what an external reviewer wants from this block. The `0.0676` in §4.8's worked example is round 3 and is the number §4.8 was written about | §4.8 itself, 212 lines below in this same file, headed `~~VERIFIED~~ **FALSIFIED 2026-08-11**` since `5c9c63fb`. Board re-read at HEAD 2026-08-15 from two committed records that were not consulted through one another: `LIVE_BOARD` in `sdk/scripts/probability_of_rank.py` (six entrants; `fetched` = `2026-08-11T23:33Z`), read by AST rather than imported, and `sdk/scripts/probability_of_rank_record.json` (`frame.entries` = 6, same `fetched`). ~~The pin is stated on every surface carrying the rank claim; no network read was made~~ — struck 2026-08-15 with the verdict it was offered in support of |
> | **4.9** | the summary table | **SUPERSEDED, and kept.** Its two DEFECT rows are both discharged (§4.4, §4.5) and it predates round 5 entirely, so it summarises an audit of an entry that is no longer the entry. It is left standing because it is the summary *of that audit*; **this block is the summary of where those findings now stand** | Row-by-row against §4.4 and §4.5's own resolution blocks and the round-5 package files listed above |
>
> ### The untrained duct path — its own compliance line, every question answered
>
> *V6 poses three (used at solve time only? touched no test data? stated in the
> description?); the fourth is the one that makes "untrained" mean anything, so it is
> asked here too.*
>
> | question | verdict | how this pass knows, rather than who told it |
> |---|---|---|
> | **Used at solve time only?** | **YES.** `kOmegaSSTQCR` is an **in-PDE constitutive term**: `tau_ij,QCR = tau_ij − Ccr1 [O_ik tau_jk + O_jk tau_ik]`, applied inside a converged SIMPLE solve. There is no post-hoc step to audit, because there is no post-hoc step | `sdk/openfoam/qcr/kOmegaSSTQCR/kOmegaSSTQCR.C:60` and `.H:14`; `closure_round5_qcr_forward.py` asserts `SIMPLE solution converged in {t} iterations` in each arm's log and then writes the duct CSVs **from the converged fields**, interpolated to the benchmark's own evaluation points |
> | **Touched any test data?** | **NO GROUND TRUTH, and the absence is a measurement rather than a blind spot.** Counted directly in the run tree: `AR_1_Ret_360_qcr`, `AR_3_Ret_360_qcr` and `AR_14_Ret_180_qcr` hold **0** `*_LES*` files each; `AR_7_Ret_180_qcr` and `AR_7_Ret_180_sst` hold **3 each**. `AR_7_Ret_180` is the benchmark's suggested DUCT **validation** case, and its two arms are the **positive control** — they prove the finder works, so the zeros are real | `find /home/ubuntu/certonomous-runs/w3-qcr-rank1/*/ -name "*_LES*"`, run by this pass |
> | **Zero fitted parameters?** | **YES.** The only coefficient is `Ccr1 = 0.3`, Spalart (2000)'s published constant, compiled in as the default and **overridden nowhere** | `kOmegaSSTQCR.C:91–99` — `getOrAddToDict("Ccr1", coeffDict_, 0.3)`; a grep for `Ccr1` across every `constant/` dictionary in the round-5 run tree returns **nothing**, so no case raises it |
> | **Stated in the description?** | **WAS NOT — there was no description document. Now YES**, and it is stated as a *concession*: the term is published, it is not ours, and the entry above ours already runs one | `DESCRIPTION_DOCUMENT.md` §2 (row: *"a converged forward solve of the **untrained** QCR2000 constitutive term — it is a 25-year-old published model, not ours"*), §3 (`Ccr1 = 0.3` frozen before any solve), §6 |
>
> **Nothing in this block changes a §4 verdict on the rule.** The audit's central finding —
> that the one strict rule is not violated — survives round 5 and covers a **smaller**
> fitted surface than it did, because three of the eight rows are now produced by a
> published term with nothing in it to fit.

The brief was to be adversarial and to prefer finding a problem now over a withdrawal
later. Findings are ordered worst-first. **Two defects were found. Neither is a rule
violation; both must be fixed before anything is sent.**

### 4.1 The one strict rule: NOT VIOLATED — verified in code, not taken on trust

> **Citation currency note, 2026-08-10 (chief, personally).** The three line numbers in
> this subsection were corrected from 115 / 215 / 165–167 to **128 / 228 / 178–180**. The
> CLAIMS were and remain true — only the citations had gone stale, shifted by a docstring
> fix at `fe121af2` on **2026-07-31** that moved the code without moving the reference to
> it. [Date corrected 2026-08-10: this note first said 2026-07-30 — a wrong date inside a
> note about stale references, found by Ladder V rung V15, which verified the anchors
> against the code rather than accepting my claim that they had been re-verified.] Ladder V rung
> A3 re-verified every anchor against HEAD twice (`_load_ground_truth_U` at 128 and 228,
> the test loop at 178 with its `# no U_LES read` annotation at 179), and the executable
> assertions cited below are at 84–86 and were run live with three firing negative
> controls. Corrected by the chief rather than by a verification pass: three consecutive
> passes each declined this edit on the defensible ground that the send package is
> Katie's, and the aggregate of three defensible declines was a stale citation surviving
> all three. That is a coordination defect, not an oversight, and its owner cannot be a
> verifier.

I audited `sdk/scripts/apply_closure_ph_gate.py` and
`sdk/scripts/closure_baseline_error_gate.py` line by line rather than relying on the
prose in `CLOSURE_CHALLENGE_STATUS.md`.

- Ground-truth reads (`_load_ground_truth_U`) occur at line 128 inside
  `for case in gate._PH_TRAIN` (21 training cases) and at line 228 inside
  `for c in ph._PH_TRAIN` (same 21). **Both loops are over training cases only.**
- The test-case loop (lines 178–180) calls `ph._load_rans_fields` only, annotated
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

**But it must be fixed.** The ledger's "four official scoring calls" *(as this
round-3-era finding was written; the cumulative count is six after round 5's
2026-08-07 call -- the ledger stood at six as of frame `c143d4c0`)* counts *distinct
prediction sets scored*, which is a defensible and meaningful unit. The docstring
states something stronger and demonstrably false. An entry whose entire credibility
rests on precise self-accounting cannot ship with a sentence a reviewer can falsify by
reading forty lines further down the same file. **Correct the docstring to state the
unit being counted, before submission.**

> **RESOLVED 2026-07-30.** The docstring now states that exactly one *new* prediction
> set is scored, that this is the 4th official call under the unit the ledger has
> always counted (distinct prediction sets), and — explicitly — that the run makes
> **four** `closure_challenge` invocations, naming the two at STAGE 3 that re-score
> the already-counted RANS-identity floor as a harness check and the two at STAGE 4
> that score the entry. It further records that the benchmark imposes **no**
> scoring-call limit and that the ledger discipline must never be described as
> compliance with one. Nothing about the code's behaviour changed; only the sentence
> describing it, which is the point.

### 4.5 DEFECT 2 — there is no submittable artifact

**No prediction CSV has ever been written.** Searched the repository and the filesystem:
the only files matching the required names belong to other entrants
(`closure-challenge-benchmark/submissions/{wu,montoya,wang}`) and the package's own test
fixtures. `apply_closure_ph_gate.py` contains no CSV-writing code at all — the entry of
record exists as an in-memory `predictions` dict and a JSON of *scores*.

**The entry of record is currently a number, not a submission.** Producing the eight
CSVs requires re-running the pipeline with a CSV dump added.

**This does not require a fifth scoring call** *("a fifth" as this round-3-era finding
was written on 2026-07-29; the cumulative count is six after round 5's 2026-08-07 call,
so the next one would be the 7th -- the ledger stood at six as of frame `c143d4c0`)*
**, and must not be allowed to become one.**
Recommendation: add CSV output and run with the `score()`/`evaluate_by_case()` calls
disabled, then verify the files are 1000×3 by inspection alone. The scores are already
recorded; re-deriving them buys nothing.

> **RESOLVED 2026-07-30. The eight CSVs now exist**, at
> `demo-output/website/closure_challenge_submission/test/{case}.csv`, written by
> `sdk/scripts/export_closure_submission_csvs.py` (69.7 s, 2-core cap), alongside a
> `MANIFEST.json` carrying a SHA-256 per file.
>
> **Scoring calls consumed: zero — enforced in code, not promised in prose.** The
> script does not merely omit the calls. Before any pipeline work it replaces
> `score`, `score_from_csv`, `evaluate_by_case`, `evaluate_from_csv_by_case`,
> `evaluate_individual_case`, `_velocity_field`, `_ground_truth` and
> `_load_csv_predictions` with raising stubs across the `closure_challenge`,
> `dataset_utils` and `eval` namespaces, then **proves the guard is armed** by
> calling `score()` and catching the refusal before continuing. If a future edit
> reintroduces a scoring call, the script dies rather than quietly spending one.
>
> `evaluation_points()` *is* still called and is **not** a scoring call: it returns
> `_ground_truth()[case]['coords']` only and never touches `['U']`. Interpolating
> onto those points is what the benchmark task requires. No test-case ground-truth
> velocity was reachable from that process at all.
>
> **Verified without scoring, on quantities that owe nothing to test truth:** both
> harness commits, the refit alpha (0.7499) and threshold (0.1263), the top-3
> screened feature names, all four gate decisions with their predicted baseline
> errors, and the per-case prediction source — **8 of 8 checks pass**, so these CSVs
> are the round-3 entry of record and not some near neighbour of it. Each file was
> re-read from disk and confirmed 1000×3, finite, comma-delimited, header-free
> (the only alphabetic character anywhere in the eight files is the `e` of
> scientific notation), with round-trip error below 5e-8.
>
> **One further check worth its cost.** The mean velocity magnitude of our field on
> each case sits *inside the band spanned by all four accepted submissions* on all
> eight cases (e.g. `AR_3_Ret_360`: ours 41.13, against 39.43–41.92 across
> wu/montoya/wang/reissmann). That would catch a point-ordering, column-ordering or
> units blunder — the failure modes that would silently wreck a submission — and it
> costs no scoring call.
>
> The recorded **0.0676 was not recomputed**. It is carried across from the round-3
> record unchanged, exactly as §5.2 states.

### 4.6 Version label understates the metric revision

`closure.html` and the round-3 JSON both record the evaluation package as **v0.2.1**.
At the pinned commit `1c4e22c8`, `pyproject.toml` declares `version = "0.3.1"` and the
commit message reads *"v0.3.1: vector magnitude metric, mean over cases"* — no trailing
period; an earlier revision of this document put one inside the quotation marks, which
is corrected here. Verified 2026-08-02 against the local clone: commit
`1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162`, dated Thu 26 Mar 2026 14:19:03 -0400, and
it is the only commit in that repository's history mentioning the metric change.
Upstream
simply never bumped `__version__` in `__init__.py`; our record faithfully reports what
the package reports itself as. **Nothing is wrong with the score** — but "v0.2.1"
names an older metric revision than the code actually used. **Cite the commit hash
`1c4e22c8`, which is unambiguous, and drop or footnote the version string.**

### 4.7 The reputational exposure: ~~two of five~~ **two of eight, and both of them,** "best on board" rows are the organisers' own baseline

> **COUNT CORRECTED 2026-08-12; the superseded figures are struck above and in the
> index row, not deleted.** The heading was written against the five-entry board of
> 2026-05-04 and read *"two of five"*; the round-5 correction that replaced it read
> *"four of eight"*. Both are now false. Against the **live six-entry board** fetched
> 2026-08-11T23:33Z we are best on **2 of the 8** cases — `alpha_05_4071_4048` and
> `alpha_05_4071_2024`, the two the section is about — because both `alpha_15` hills
> went to Tian, Buchanan, Hickel & Dwight. **Both of the two survivors are the
> declined baseline rows, so the count belonging to our own model is ZERO of 8, and
> the exposure this section describes is no longer a fraction of our wins but all of
> them.** Derived, not typed: `sdk/scripts/probability_of_rank.py` holds the board and
> `scripts/self_audit.py` re-derives the count from it case by case, so this paragraph
> goes red rather than stale the next time the board moves. The standing figures that
> travel with it are P(rank 1) = **50%**, interval **0–97% at 95%**, six-entry board;
> the leads over Yang, Reissmann, Wu & Zhang and Tian/Buchanan/Hickel/Dwight are **not
> statistically decided**.

On `alpha_05_4071_4048` (0.0461) and `alpha_05_4071_2024` (0.0719) our submitted
prediction *is the unmodified RANS solve* — the gate declined, correctly, and we report
the baseline. Those two values beat every published ML entry on those cases.

**Not a rule violation.** Submitting an uncorrected field is a legitimate prediction,
and the gate deciding to withhold is the method working.

> **STALE CITATION, CORRECTED 2026-08-02.** This paragraph used to say that
> `closure.html` states the point without hedging, and quoted it as *"It is not our
> model outperforming anyone"*. **That sentence is no longer on the page.** §8.2
> rewrote the section on 2026-08-01 and the quotation went stale with it; searched
> 2026-08-02 and it returns nothing. The page now says it harder, and this is its
> current wording, read off `closure.html` today: *"0.0461 and 0.0719 are therefore
> not our numbers. They are properties of a file every entrant is handed for free,
> and anyone submitting it unchanged scores exactly the same."* The two rows carry
> the tag `BASELINE, NOT OUR MODEL`. **Nothing about the substance changed; a
> citation to our own live surface went stale when we improved the surface**, which
> is the failure mode this audit exists to catch, found inside the document that
> raises it.

**But the exposure is real and it is asymmetric.** If a leaderboard row credits
Certonomous with the best score on two cases and a reader later works out those are the
organisers' own baseline fields, the discovery is far more damaging than the
disclosure. **This belongs in the submission email itself, not only on our website.**
Highest-priority disclosure item.

### 4.8 Leaderboard position is current — ~~VERIFIED~~ **FALSIFIED 2026-08-11**

~~Verified today against the live README: the four-entry board is unchanged since
2026-05-04.~~ **Struck 2026-08-11: the board is now SIX entries deep with a new leader
(Yang, 0.0580), verified by two independent live fetches.** 0.0676 would sit between
rank 3 (0.0624) and rank 4 (0.0641). The challenge
is ongoing with no deadline, so this can change without notice — the claim should be
dated wherever it appears. **It said so, and it was right, and no check was scheduled
to act on it. The section that predicted this failure is the section that suffered it:
a warning without an owner and a period is a comment, not a control.**

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

> ## ✅ DISCHARGED 2026-08-11 — §5.1–§5.4 REWRITTEN AGAINST ROUND 5. STILL NOT SENT.
>
> *§5.1, §5.2, §5.3 and §5.4 were rewritten on 2026-08-11 against the round-5
> payload, every number re-verified against a primary artifact rather than against
> a sibling document — which is how the round-4 text went stale in the first place.
> The banner below is kept **as the record of what was found**, and the word
> *verbatim* is retired here because it was one line too strong. ~~**Its thirty body
> lines are byte-identical** — every row of the ten-row defect table, including the
> round-4 numbers it indicts —~~ ***(struck 2026-08-17: twenty-nine of the thirty
> were, and nine of the defect table's ten rows were; one row — the seventh — was
> edited at `2cec44ee` after this sentence was written at `b65bdf01`. Re-certified
> line by line immediately below.)*** but **its heading was replaced and demoted `##` →
> `###`**, that heading being the one line which described the text underneath it,
> and that text is no longer what it described; the blank line that closed the
> blockquote became `>` so the closure table joins it. Row-by-row closure follows
> the table.*
>
> **RE-CERTIFIED 2026-08-17 AT FRAME `101079fd`. THE STRUCK CLAIM WAS TRUE WHEN IT
> WAS WRITTEN AND WAS FALSIFIED THE NEXT DAY, AND NAMING WHICH LINE IS THE WHOLE
> POINT OF IT.** The struck clause landed at `b65bdf01` (2026-08-11 02:42:53Z). The
> measurement was an aligned 32-line byte comparison of the banner block below
> against `e87650db^` (`514876b0`), each side anchored on its own heading line
> rather than on a line number, index 0 being that heading and indices 1–30 the
> thirty body lines the clause spoke about:
>
> - **3 of the 32 block lines differed at `101079fd`** — block indices **0, 21 and
>   31**. **29 of 32 matched byte for byte**, and of the **thirty body lines, 29
>   matched and one did not.**
> - **Two of the three were declared, and both declarations were left standing above**: index 0,
>   the heading replaced and demoted `##` → `###`; index 31, the blank line that
>   closed the blockquote, which became `>`.
> - **The third was not declared, and it was a row of the ten-row defect table.** At
>   `101079fd` that table's header sat at index 13, its separator at index 14 and its
>   ten data rows at indices 15–24. The undeclared line was **index 21, the seventh
>   of those ten rows** — the row whose first cell reads `§5.4, §5.2`. **9 of the 10
>   rows were byte-identical, not 10.**
>
> **What `2cec44ee` (2026-08-12 18:05:51Z) did to index 21.** Walking every commit
> that touched this file between `e87650db^` and `101079fd`, it was the only one that
> moved any block line other than 0 and 31, and no later commit touched index 21
> again. Its edit was a **pure insertion of 186 bytes** — the row went from 579 bytes
> to 765 — with **nothing deleted and nothing reworded**: immediately after that
> row's clause `**and must now carry P(rank 1) = 68% with its 2–100% interval**` it
> inserted the dated scope note `*(figures as recorded at this banner's date against
> the four-entry board; the rule's live figures are 50% and 0–97% on the six-entry
> board — see §10's re-correction of 2026-08-12)*`. Every other byte of the row was
> carried across unchanged.
>
> **Why the certification was corrected and index 21 was NOT restored.** That row did
> not narrate, it **mandated** — *"must now carry P(rank 1) = 68% with its 2–100%
> interval"* — and the six-entry board fetched 2026-08-11T23:33Z
> (`campaign/BOARD_MOVED_2026-08-11.md`) falsified both of those figures, so a reader
> obeying the row as it stood would have written a superseded probability into §5.2
> and §5.4. That was the claim-generator shape `scripts/check_normative_clauses.py`
> was built against (docket `D119`); at `101079fd` that instrument's own BLIND-TO
> census named a mandate pinning a four-entry `P(rank 1)` as its live uncaught
> instance. Restoring index 21 to its `e87650db^` bytes would have reinstated an
> un-scoped four-entry mandate inside a package held open for proofreading, and would
> have deleted a dated repair, against `W-4`. **The false thing was the certification,
> not the edit**, so the certification was corrected and the banner's bytes were left
> as `2cec44ee` left them.
>
> **What let this survive three re-verifications, recorded so the shape is not
> re-learned.** `2cec44ee`'s own commit message declared its edits to §10 and to two
> rows of the closure table *below* this banner and named no edit to the banner
> itself; and the sentence the edit falsified sat four lines *above* the row it
> changed, inside a paragraph whose announced subject was the rewrite of §5.1–§5.4
> rather than the banner's bytes. Nothing on the page joined the edit to the claim
> about it, and at `101079fd` no instrument in this lab took a byte-identity
> ASSERTION as its unit — `scripts/check_summary_consistency.py`, the one check built
> around a byte-identical block, records in its own header that byte-identity decides
> nothing in either direction and that it never looks at a diff. So this claim was
> re-derived only by whoever chose to re-derive it: three graders did, on
> 2026-08-14, 2026-08-15 and 2026-08-17, and none left an executable behind that
> would have re-measured it for the next reader. Filed as `D339`.
>
> **What has NOT changed: nothing is sent.** §5.6 items 6 and 7 are Katie's and
> remain OUTSTANDING, and they are the send block. This rewrite makes the package
> honest; it does not make it dispatched, and dispatch is reserved to Katie.
>
> **One correction carried into §5.2 rather than propagated silently.** The last
> row of the table below states the like-for-like re-score of Reissmann as
> `0.0595338` and the margin as `0.0028863`. **Those two do not subtract** against
> our 0.056647191704213645 — they disagree by 3×10⁻⁷. Re-running the benchmark's
> own scorer over Reissmann's eight published CSV directories at eval package commit
> `1c4e22c8` (a competitor's public files; **not** a scoring call on our
> predictions, so the ledger stands at 6) gives **0.05953352830400628**, i.e.
> **0.0595335**, and a margin of **0.00288634**. **The margin `0.0028863` is
> correct; the transcribed `0.0595338` is the misrounded one.** The same misrounded
> `0.0595338` was printed in `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`
> §5. **That correction has landed: `fdb1ec5c`, 2026-08-11 01:41:00Z, four minutes
> after this paragraph was written.** The travelling document now reads `0.0595335`
> at both sites and contains no occurrence of `0.0595338` — checked on the file
> itself, 2026-08-11, not on a sibling's report of it.
>
> ---
>
> ### ⛔ THE BANNER AS WRITTEN 2026-08-10, KEPT AS THE RECORD
>
> *Added by Ladder V Pass 2 (rung V8), 2026-08-10. Nothing below was rewritten; a
> banner was added so that the mismatch is impossible to proofread past. The
> claims table with per-sentence verdicts is in
> `campaign/LADDER_V_PASS2_2026-08-11.md`.*
>
> **§5.1–§5.6 were written on 2026-07-30 against round 3 and patched to round 4 on
> 2026-07-31. §10 replaced the payload with the round-5 CSVs but did not rewrite
> §5.** The result is a package whose *attachment* and whose *cover letter*
> disagree, which is the single worst defect this ladder could find, because it is
> the one a proofreader is least likely to see:
>
> | § | says | payload actually is | verdict |
> |---|---|---|---|
> | §5.4 subject line + body | *"overall 0.0654"* | the eight round-5 CSVs score **0.056647** | **FAIL — the email would announce a score that is not the attachment's score.** The steward would rescore, get a different number than the letter claims, and the first impression of an entry built entirely on precise self-accounting would be an arithmetic contradiction |
> | §5.1 item 1 | CSVs at `closure_challenge_submission/test/` | round 5 ships from `closure_challenge_submission_round5/test/` (§10) | **FAIL — wrong directory** |
> | §5.2 claims table | 0.0654 / per-case round-4 row / "improvement −0.0382, 36.9%" | round 5: 0.056647, ducts 0.0455 / 0.0400 / 0.0353, improvement **−0.0470, 45.3% below the 0.1036 floor** | **FAIL — every row stale** |
> | §5.3 item 7 | *"four distinct prediction sets scored"* | **six** (floor, rounds 1–5) | **FAIL — a scoring-call count claim, the exact defect class §4.4 exists for** |
> | §5.3 item 2 + §5.4 item 2 | the two baseline rows, correct | still correct, but §10 requires the best-on-board count stated as **4 of 8**, not 5 | **INCOMPLETE — §10's instruction is unexecuted** |
> | §5.1 item 3 | *"a description document … containing §5.3 and §5.4"* | **no such document exists anywhere in the repository** | **FAIL — §5.3 is a specification of what a description document must disclose; it is not one.** Searched the tree: the only description document present is `docs/papers/wu_zhang_sst_qcrc_challenge_description.pdf`, a *competitor's*, held as the format precedent |
> | §5.4, §5.2 | no rank claim of any kind | round 5 is rank 1 scored locally | **the V8 rank-claim rule is therefore not yet engaged here** — but the moment a round-5 number is written into either, the rank claim arrives with it and must carry the qualitative clause containing the literal string `not statistically decided`, **and must now carry P(rank 1) = 68% with its 2–100% interval** *(figures as recorded at this banner's date against the four-entry board; the rule's live figures are 50% and 0–97% on the six-entry board — see §10's re-correction of 2026-08-12)* (chief ruling 2026-08-10 withdrew the internal-only gate on that figure: Pass 3 recomputed it from public data in a minute, so withholding it buys nothing and only looks concealed) |
> | §5.3 | discloses the round-2 leakage only | the **round-5** route was chosen while the per-case test scores were known | **FAIL, and this is the worst finding in the package.** `campaign/R5_RULE_FREEZE.md` concedes it in the lab's own words and then closes every remaining degree of freedom — that sentence is the entry's best asset and it lives in a file that does not travel. Discharged by the description document written at `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`, disclosure 3b |
> | §5.3 items 6, 8, 9 | round-4 disclosures | item 6 describes an ML duct model no longer in the entry; item 8 overstates the continuity defect (round-5 ducts measure 5.3e-4–8.5e-4, not 2.3–3.4%); item 9 anchors the seed bound to the wrong comparison | **FAIL — 3 of 9 disclosures no longer describe the attached files** (Pass 3, D5). Item 8 is the rare stale disclosure that is *unfair to the entrant* |
> | §5.2 | *"Reissmann's published 0.059525"* | the README publishes **0.0595**; 0.059525 is the mean of eight *rounded* per-case values; a like-for-like re-score gives **0.0595338** | **FAIL on the word "published"** — the figure is not reproducible from the source it names. Like-for-like margin **0.0028863**, against which the 0.002419 seed bound covers **84%** (Pass 3, D6) |
>
> **Nothing here is a rule violation and nothing here is new work** — it is §10's
> own instruction list, unexecuted, plus one thing §10 did not notice (the missing
> description document). **Rewriting §5 is not this pass's call**: it is Katie's
> package, and items 6 and 7 of §5.6 are hers. This banner exists so that no one
> can reach §5.4, find it clean prose, and send it.
>
> ---
>
> ### Where each row above is now closed (2026-08-11)
>
> | banner row | closure |
> |---|---|
> | §5.4 announced 0.0654 | §5.4 now states **0.056647**, in the subject line and the body, from `closure_challenge_round5_qcr.json` → `official_test_harness_result.round5_overall_full` |
> | §5.1 named the round-3 directory | §5.1 now names `closure_challenge_submission_round5/test/`, the eight files re-counted on disk at 1000 × 3 |
> | §5.2 claims table round-4 | rebuilt from the round-5 record: overall, all eight per-case values, and the floor delta **−0.0470, 45.3%** |
> | §5.3 item 7 said "four" | now **six**, sourced to `CLOSURE_CHALLENGE_STATUS.md` §5's twice-superseded ledger entry |
> | §5.3 item 2 / §5.4 item 2 best-on-board | ~~both now say **4 of 8, two of which are the organisers' own baseline file, so 2 of 8 is ours** — and neither states the count without that clause~~ *(true when this closure was recorded on 2026-08-11, falsified by the six-entry board fetched later the same day; struck 2026-08-12 — §5.3 item 2 now carries the six-entry correction: **2 of 8, both baseline, model's own ZERO of 8**)* |
> | §5.3 items 6, 8, 9 | item 6 re-scoped to the trained model only; item 8 now carries the measured **5.3–8.5×10⁻⁴** ducts; item 9 re-anchored to the 0.0028863 margin |
> | §5.3 disclosed round-2 leakage only | new item **3b** carries the round-5 concession in the lab's own words, quoted from `campaign/R5_RULE_FREEZE.md` @ `0bade54a`, and the cover email now leads with it |
> | rank claim rule | ~~§5.2 and §5.4 both carry **P(rank 1) = 68%**, its **2–100% at 95%** interval, and the named undecided pairs, with the sweep token intact on one line~~ *(true when recorded 2026-08-11, falsified by the six-entry recomputation later that day; struck 2026-08-12 — §5.2 now carries **P(rank 1) = 50%, 0–97% at 95%**, the six-entry board, and the FOUR undecided pairs, with the 68%/2–100% figures struck where they stood)* |
> | "published 0.059525" | replaced; §5.2 records the re-scored value, the margin, and which of the two was misrounded |

### 5.1 What would be sent

*Rewritten 2026-08-11 against the round-5 payload. Path and file counts checked on
disk, not inherited from the round-3 text this replaces.*

1. A `test/` directory containing eight files, 1000 rows × 3 columns, comma-delimited,
   no header: `alpha_15_13929_4048.csv`, `alpha_15_13929_2024.csv`,
   `alpha_05_4071_4048.csv`, `alpha_05_4071_2024.csv`, `AR_1_Ret_360.csv`,
   `AR_3_Ret_360.csv`, `AR_14_Ret_180.csv`, `NASA_2DWMH.csv`. **The round-5 payload
   is the one that ships**, at
   `demo-output/website/closure_challenge_submission_round5/test/` (§10) — *not*
   the round-3 directory this line used to name. All eight re-counted on disk at
   1000 × 3. Layout is the flat `{case}.csv` form used by wu, montoya and wang,
   which is also what the evaluation package's own CSV loader expects.
2. An author list with affiliation — **Katie's to fill; not invented anywhere in
   this package** (§5.6 item 6). The benchmark README's own submission step 3 asks
   for the `test` subdirectory, the author list, and any relevant references.
3. **The description document**, which now exists rather than being specified: it is
   written, at `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`, and it
   is what §5.3 below specifies. `MANIFEST.json` (SHA-256 of all eight files, both
   harness commits) and `README.md` (how to score them from scratch) sit beside it
   in the same directory and travel with it.

### 5.2 Claims the package makes

*Rebuilt 2026-08-11 from the round-5 record. Every row below was read out of a
primary artifact — the round-5 JSON, the benchmark's own README, or the scorer
itself — and none of it was copied from a sibling document.*

| Claim | Value | Source |
| --- | --- | --- |
| Overall score | **0.056647** (0.056647191704213645) | `closure_challenge_round5_qcr.json` → `official_test_harness_result.round5_overall_full` |
| Per-case | 0.0501 / 0.1011 / 0.0461 / 0.0719 / 0.0455 / 0.0400 / 0.0353 / 0.0632 | same file, `round5_per_case` |
| RANS-identity floor, our harness | **0.1036** (0.1036347 on cold re-derivation) | our figure, not one the benchmark publishes — §7.2 stands |
| Improvement over floor | **−0.0470, 45.3% below** | derived from the two rows above |
| Superseded round-4 entry | 0.0654, ducts 0.0811 / 0.0775 / 0.0325 | `closure_challenge_trained_entry_round4_duct.json`; round 5 moved it by −0.0088 |
| What is actually ours | **3 of the 8 predictions.** 2 are the supplied baseline unchanged; 3 are an untrained QCR2000 forward solve | §10; `DESCRIPTION_DOCUMENT.md` §2 |
| Best on published board | ~~4 of 8, two of them baseline, so 2 of 8 ours~~ **2 of 8 against the live six-entry board — and BOTH are the organisers' own baseline file, so ZERO of 8 belong to our model.** Both `alpha_15` hills lost to Tian, Buchanan, Hickel & Dwight | `campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md` §3a; re-derived case by case against the six published entries |
| Standing | 0.056647 is the lowest overall on the **live six-entry** board fetched 2026-08-11 (our own scoring is at `deb91557`, which scores but does not rank), **scored locally by us — not an official placement.** P(rank 1) = **50%**, interval **0–97% at 95%**; the leads over **Yang, Reissmann, Wu & Zhang, and Tian/Buchanan/Hickel/Dwight** are **not statistically decided**, the leads over Liu (98.7%) and Montoya (99.8%) are. ~~P(rank 1) = 68%, 2–100%, two undecided pairs~~ — struck, four-entry board | `campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md` |
| Margin over the published rank-1 entry | **0.001365** over **Yang** (0.058013), the leader on the live board. ~~0.0028863 over Reissmann, Fang & Sandberg~~ — Reissmann is now rank 2 on the live board, while on the frozen scoring pin `deb91557` Reissmann is rank 1 of four | live board fetched 2026-08-11T23:33Z |
| Scored with | benchmark's own unmodified scorer, eval package commit `1c4e22c8`, benchmark commit `deb91557` | `harness_check`; both commits confirmed in the local checkouts |

**The margin pair, resolved rather than inherited.** The README publishes **0.0595**
to four decimals; `0.059525`, which earlier drafts of ours called "published", is the
mean of eight *rounded* per-case values and is not a number anyone published. A
like-for-like full-precision re-score of Reissmann's own eight submitted CSVs on the
same harness gives **0.05953352830400628**. Against our 0.056647191704213645 that is a
margin of **0.00288634 → 0.0028863**. The value `0.0595338` quoted in the §5 banner
above — and, until `fdb1ec5c` (2026-08-11 01:41:00Z), in `DESCRIPTION_DOCUMENT.md` §5 —
is a transcription slip in the seventh decimal: **it does not subtract to the margin
printed beside it**, and the correct pair is **0.0595335 / 0.0028863**. **The
travelling document was corrected at `fdb1ec5c` and now reads `0.0595335` at both of
its sites**, checked on that file rather than on a report of it. ~~The 0.002419 seed
bound covers 84% of that margin either way (0.8380).~~ *This re-score touched a competitor's public files only;
the lab's scoring-call ledger stands at 6, unchanged.*

> **STRUCK 2026-08-15 — AND THE CONCLUSION REVERSES, IT DOES NOT WEAKEN.** The
> 0.0028863 above is a margin over **Reissmann, Fang & Sandberg**, who are no longer
> the entry immediately ahead of us. The board gained two entrants at
> **2026-08-11T23:33Z**; on the **six-entry** board retrieved at that timestamp and
> re-verified unchanged by read-only fetch at **2026-08-14T21:01Z**, the entry
> immediately ahead of ours is **Yang, at 0.058013**, and our locally scored
> 0.056647191704213645 sits **0.001365** below it. ~~sits **0.0013658082957863568**
> below it. Re-derived at full precision from the lab's own committed sources~~ —
> **CORRECTED 2026-08-15 (docket D104): the seventeen digits were spurious and the
> phrase that vouched for them was the worse defect.** `0.0013658082957863568` is
> exactly `0.058013 − 0.056647191704213645` in IEEE double, but **0.058013 is the
> six-decimal PRINTING** of Yang's overall in `campaign/BOARD_RESCORE_2026-08-14.md`
> §3.1, not a measurement to seventeen places — so every digit after the sixth is an
> artifact of the subtraction, not evidence. The lab's own record holds
> `probability_of_rank_record.json` → `pairwise.Yang.margin =
> −0.0013653082957863563`, from the full eight-case mean 0.0580125; the two differ in
> the seventh significant figure, which is precisely the range the spurious digits
> pretended to resolve. **"Re-derived at full precision" was false as written**: the
> subtraction was carried out at full precision, the *input* was not, and that phrase
> is what made the digits credible. **This document indicts this exact class 120 lines
> above** — §"The margin `0.0028863` is correct; the transcribed `0.0595338` is the
> misrounded one" at `:618` — and then committed it. The margin supported by the
> stated basis is **0.001365** (four significant figures), and the conclusion is
> untouched: 0.002419121853891026 over the full-mean margin is **177.2%**, over the
> six-decimal margin **177.1%**, over the rounded 0.001365 **177.2%** — **all three
> bases give 177%**. Derived from —
> `closure_challenge_seed_sensitivity.json` → `overall_equivalent_S_bound` =
> **0.002419121853891026**, and the scores in
> `campaign/BOARD_RESCORE_2026-08-14.md` §3.1 — the ratio is
> **0.002419121853891026 / 0.001365 = 1.772**, i.e. **177%**, not 84% *(D104,
> 2026-08-15: the denominator was written as `0.0013658082957863568`; against the
> record's `pairwise.Yang.margin` 0.0013653082957863563 the ratio is 1.7719 and
> against the six-decimal basis 1.7712 — **177% on every basis**, so the correction
> is to the digits and not to the conclusion)*.
> **The bound does not cover part of the margin. It exceeds the margin by 77%.**
> Loaded adversely onto the three seed-dependent cases our overall becomes
> **0.059047**, *above* 0.058013, and the point lead is lost outright
> (`campaign/BOARD_RESCORE_2026-08-14.md` §3.4; at the unrounded bound the adverse
> overall is 0.0590663, further above). **There is no weaker restatement of the old
> sentence that this evidence supports** — a bound covering most of a margin is a
> qualification on a standing that survives it, and this standing does not survive
> the bound. Falsified by the board move of 2026-08-11T23:33Z; withdrawn in the
> travelling document at commit `cc906ec9`
> (`closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md` §8) and **not
> carried to this draft until now**, which is the defect this note exists to record
> as much as the arithmetic is.

**A second pair that must not be smoothed together.** The 0.0028863 margin rests on
the re-scored 0.0595335. The P(rank 1) — struck 68% and live 50% alike — and every
pairwise probability with it come from a
bootstrap whose Reissmann input is the transcribed 0.059525, and **that bootstrap has
not been re-run on the re-scored basis** — the two inputs differ by 9×10⁻⁶, about 0.3%
of the margin. We state which input each figure rests on rather than asserting they
are interchangeable.

**No number here is adjusted, rounded favourably, or restated to fit a rule.** If the
steward's own scoring differs from ours, the steward's number is the number.

### 5.3 What the description document must disclose — non-negotiable

> *Updated 2026-08-11 to describe the round-5 payload. **This list is a
> specification, and it is now executed**: the document that satisfies it is
> `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`, which is what
> travels. Where that document and this list differ in wording, that document is
> the artifact and this list is the requirement it must meet. Items 2, 6, 7, 8 and
> 9 below were round-4 text and are corrected here; item **3b** is new and is the
> one the package was most exposed on.*

1. **Method class.** Post-hoc velocity-field correction: target `delta_U = U_LES −
   U_RANS` per cell, `HistGradientBoostingRegressor` ×3 on 7 features (Pope's 5 scalar
   invariants, `Re_y`, `tke_ratio`), applied once to a converged RANS field as
   post-processing. **It does not modify the turbulence model and nothing is
   re-solved.** This is a materially weaker claim than the FIML/TBNN/SpaRTA family it
   is being ranked against, and saying so is the point.
   **The method class is not ours, and the description document must cite its prior**
   *(added 2026-08-05, mandatory per the method-priority review
   `CLOSURE_METHOD_PRIORITY_REVIEW.md` §5 row C1, commit `d84b649f`)*: learned
   local-error correction of a cheap CFD solve, applied without re-solving, is
   published — **Hanna, Dinh, Youngblood & Bolotnov**, *Coarse-Grid Computational
   Fluid Dynamic (CG-CFD) Error Prediction using Machine Learning*, **arXiv:1710.09105
   (2017)**; journal version *Progress in Nuclear Energy* **118** (2019) 103140, DOI
   10.1016/j.pnucene.2019.103140. **[READ IN FULL 2026-08-05**, arXiv text at
   `docs/papers/hanna_dinh_youngblood_bolotnov_1710.09105.pdf`; the journal version is
   **METADATA ONLY**.**]** State the delta in the same sentence as the citation: their
   surrogate corrects **grid-coarsening error** in a coarse-grid no-model
   Navier–Stokes solve of a lid-driven cubic cavity, from cell-Reynolds-number and
   velocity-derivative features; ours corrects **closure error** in a converged k-ω SST
   solve of separated and secondary flows, from Pope invariants. Their abstract's
   sentence — a surrogate trained to predict the cheap solve's local errors as a
   function of its own local features — is our method statement with two words swapped,
   and a referee who knows the nuclear-thermal-hydraulics ML literature will recognise
   it on sight. The statistical ancestor, cited as lineage only: **Kennedy & O'Hagan**,
   *Bayesian Calibration of Computer Models*, **J. R. Statist. Soc. B 63(3) (2001)
   425–464** — **[METADATA ONLY**, not read here; do not quote it.**]** What survives
   and should be said in the same breath: within the data-driven RANS-closure
   literature swept (27 searches, 13 counted negatives), no other post-hoc
   *velocity-field* correction was located — every located correction re-enters the
   equations. **The class is established; the application to turbulence closure is
   ours.**
   **And the choice of target has a published argument for it**: **Wu, Xiao, Sun &
   Wang**, *RANS equations with explicit data-driven Reynolds stress closure can be
   ill-conditioned*, **J. Fluid Mech. 869 (2019) 553–586**, arXiv:1803.05581
   **[ABSTRACT READ]** — propagating a learned stress correction through the RANS
   equations is a published conditioning hazard (the arXiv record's own summary: stress
   errors below 0.5% amplifying to velocity errors up to 35%, quoted at that tier and
   not read off the paper's tables), which correcting velocity directly sidesteps.
   Every re-solving entrant above us has to survive it. **This argument defends the
   method class; it does not touch disclosure 8 below and must never be used to soften
   it.**
2. **Two cases are uncorrected baseline, and the best-on-board count never travels
   without that fact.** State outright that on `alpha_05_4071_4048` and
   `alpha_05_4071_2024` the submitted field is the unmodified RANS solve, that the
   gate declined there, and that any leaderboard-best status on those two cases is
   the baseline's, not our model's (§4.7). ~~**Round-5 correction:** the count is
   **4 of 8**, not 5 — `AR_14_Ret_180`'s 0.00003 nominal tie was lost when it went
   0.0325 → 0.0353 (§10) — and **it may not be stated without saying in the same
   breath that two of the four are the organisers' own baseline file, so the count
   belonging to our model is 2 of 8.** Verified case by case against the four
   published submissions on 2026-08-11, not inherited: we are best on
   `alpha_15_13929_4048`, `alpha_15_13929_2024`, `alpha_05_4071_4048` and
   `alpha_05_4071_2024`, the last two being the declined baseline rows.~~
   *(Struck 2026-08-12: that correction was verified against the FOUR published
   submissions and the board moved hours later the same day.)* **Six-entry
   correction (board fetched 2026-08-11T23:33Z):** the count is **2 of 8** —
   both `alpha_15` hills lost to Tian, Buchanan, Hickel & Dwight — and both
   survivors are the organisers' own unmodified RANS baseline through the
   decline gate, so **the count belonging to our model is ZERO of 8, and the
   2-of-8 figure may not be stated without that zero-of-8 disclosure in the
   same breath.** Verified case by case against the six published submissions
   (`campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md` §3a): we are best
   only on `alpha_05_4071_4048` and `alpha_05_4071_2024`, both declined
   baseline rows.
3. **The full adaptive-leakage history**, in our own words before anyone asks: that
   round 2's per-case preview scores motivated building the gate; that the gate's
   parameters come only from 21 training cases; that it was validated on 4 non-test
   validation cases at AUC 1.0 before ever being pointed at a test case; and that a
   0.0675 shortcut requiring per-case selection on test outcomes was identified and
   refused, at a cost of 0.0001 (§4.2, §4.3).

   > **3b. THE ROUND-5 LEAKAGE — added 2026-08-11, and it was missing from every
   > earlier draft of this package.** Rounds 1–3 are not the whole story and the
   > list read for ten days as though they were. **The round-5 route was chosen
   > while we already knew the per-case test scores.** It must be disclosed in the
   > lab's own words, written before any round-5 number existed
   > (`campaign/R5_RULE_FREEZE.md` @ `0bade54a`):
   >
   > > *"we already know the round-4 test-duct scores (0.0811 / 0.0775 / 0.0325),
   > > and any protocol that lets those numbers choose between the QCR field and
   > > the existing ML field is test-truth-informed model selection. Every degree of
   > > freedom in that choice is therefore closed here, in writing, before any new
   > > number exists."*
   >
   > **The admission comes first and the mitigations come after it, never instead
   > of it.** The whole −0.0088 move, and the entire reason there is a standing
   > claim at all, was selected in knowledge of per-case test outcomes. What was
   > then closed in writing before any solve: all-or-none across the three ducts,
   > decided on `AR_7_Ret_180` — the benchmark's own suggested validation duct —
   > alone; `Ccr1 = 0.3` frozen, Spalart's published constant, no case-dictionary
   > override; gate thresholds set from training ducts before the validation arms
   > ran (measured 0.4770 / 0.9284 / both converged); the `AR_14_Ret_180` loss
   > accepted in advance in writing, and then incurred and not reverted; and no
   > test-case LES field reachable anywhere in the run tree. **None of that cancels
   > the sentence above and none of it may be offered as cancelling it.**
4. **Train/val/test discipline**, with the executable assertions cited (§4.1).
5. **The NASA hump regression of +0.0011 was not reverted**, because reverting after
   seeing the per-case result would itself be selection on test outcomes.
6. **Known limitations of the trained model** *(re-scoped 2026-08-11: this item used
   to describe a duct model that is no longer in the entry)*: two of seven features
   (`I3_S3`, `I4_W2S`) are algebraically identically zero across the entire duct
   family, so the **trained** model is structurally blind there — a negative result
   we found and would rather publish than have inferred from our duct scores. **It no
   longer bears on the submitted duct rows, because those are forward solves of an
   untrained term — but it is *why* they are**, and the disclosure is kept for that
   reason rather than dropped as obsolete.
7. **Scoring-call count, correctly framed**: **six distinct prediction sets scored,
   ever** — the RANS-identity floor and rounds 1 through 5 — as a self-imposed
   discipline, **explicitly not** compliance with any benchmark limit, since none
   exists and the benchmark instructs submitters to preview their score (§2.5).
   *(Corrected 2026-08-11 from "four", which was the round-3 figure and had survived
   two entries of record. The ledger, twice superseded and both supersessions on the
   record, is at `CLOSURE_CHALLENGE_STATUS.md` §5; the sixth call is the round-5 one
   in `closure_challenge_round5_qcr.json`.)*
   **Priced in the literature's own words** *(added 2026-08-05, method-priority review
   §2.3)*: the hazard the ledger addresses is adaptive overfitting of a holdout under
   repeated queries, named in **Blum & Hardt**, *The Ladder: A Reliable Leaderboard for
   Machine Learning Competitions*, **arXiv:1502.04585 (2015); ICML 2015, PMLR 37**
   **[ABSTRACT READ]**, whose abstract calls rate-limited re-submission one of the
   "poorly understood heuristics" the field resorts to. **Our ledger is that
   heuristic, applied by the submitter to itself** — harm reduction, not a guarantee,
   and it belongs beside disclosure 3 above rather than as a claim of rigour. The
   freeze-before-results half has an established venue too: the **NeurIPS Workshop on
   Pre-registration in Machine Learning**, PMLR **148** (2020) and **181** (2021)
   **[METADATA ONLY]**. What we did not find is another entrant imposing either on
   itself, unasked, on a benchmark that imposes none, and publishing the ledger — a
   disclosure practice, claimed as one and not as a method.
8. **The submitted corrected fields do not satisfy continuity, and the departure is
   measured** *(added 2026-08-05, pre-registered consequence of audit finding G2)*:
   volume-weighted RMS `∇·U` rises from the operator floor (0.1–0.5% of the
   velocity-gradient scale on the hills; machine zero on the ducts) to **~10% on the
   two corrected hill cases and 0.66% on the hump** — every other entrant re-solves
   the governing equations and gets `∇·U ≈ 0` by construction. The two declined cases
   inherit the baseline's physicality untouched.
   **Round-5 correction, 2026-08-11, and it runs *in the entry's favour*:** this item
   used to say **2.3–3.4% on the three ducts**, which was the round-4 ML ducts. The
   submitted round-5 ducts are converged SIMPLE solves and measure
   **8.5×10⁻⁴ (`AR_1_Ret_360`), 5.3×10⁻⁴ (`AR_3_Ret_360`), 5.4×10⁻⁴
   (`AR_14_Ret_180`)** — a 27–63× improvement on the fields they replace. **State the
   measured numbers, not "satisfies continuity by construction": none of those three
   is machine zero.** A stale disclosure that overstates our own defect is still a
   false sentence, and it is corrected for that reason and not because it flattered
   us to correct it. Numbers and operator validation:
   `closure_challenge_stability_physicality_audit.md` §2,
   `closure_challenge_divergence_audit.json`,
   `closure_challenge_round5_qcr_forward.json`.
9. **One-seed training uncertainty, measured** *(added 2026-08-05, audit finding
   G1)*: the PH model behind three predictions is seed-dependent (327,600 cells >
   sklearn's 200k binning subsample). Across 8 seeds the validation-proxied
   overall-equivalent spread is ~0.0003; a truth-free bound at the test points cannot
   exclude **0.002419**. **Round-5 correction, 2026-08-11:** this item used to anchor
   that bound to "the 0.0030 gap to rank 2", which no longer exists. ~~The operative
   comparison is the **0.0028863 margin over Reissmann, Fang & Sandberg**, of which
   the seed bound covers **84%** (0.002419 / 0.0028863 = 0.838 — the 84% figure is
   correct only with the *unrounded* bound, so both are stated unrounded).~~ The
   three duct predictions
   carry zero seed variance, since nothing in them was trained. ~~**No document in this
   package may quote the margin without this qualifier**~~
   (`closure_challenge_seed_sensitivity.json`).

   > **STRUCK 2026-08-15, BOTH THE FIGURE AND THE RULE, AND THE RULE IS THE MORE
   > IMPORTANT OF THE TWO.** The struck text named a superseded comparison "the
   > operative" one and then bound the whole package to it — *"no document in this
   > package may quote the margin without this qualifier"* — so for four days this
   > item **mandated that every document quote a figure whose direction of argument
   > had already reversed.** A corrected number under that rule would have gone stale
   > the next time the board moved, which is why the rule is replaced and not merely
   > re-pointed.
   >
   > **The figure.** Reissmann, Fang & Sandberg are no longer the entry immediately
   > ahead of us. On the **six-entry** board retrieved **2026-08-11T23:33Z** and
   > re-verified unchanged by read-only fetch at **2026-08-14T21:01Z**, the entry
   > immediately ahead is **Yang, at 0.058013**, and our margin is
   > **0.001365**. ~~our margin is **0.0013658082957863568**~~ — **CORRECTED
   > 2026-08-15 (docket D104): 0.058013 is the six-decimal PRINTING of Yang's
   > overall, so the digits past the sixth were an artifact of the subtraction and
   > not a measurement; the record holds `pairwise.Yang.margin =
   > −0.0013653082957863563` and the stated basis supports four significant
   > figures.** The seed bound of **0.002419121853891026** is
   > therefore **1.77 × that margin — 177%, not 84%** *(177.2% on the full-mean
   > margin, 177.1% on the six-decimal one — the conclusion does not depend on which)*.
   > It does not cover part of
   > the margin; **it exceeds it.** Loaded adversely on the three seed-dependent
   > cases our overall becomes **0.059047**, above 0.058013, and the point lead is
   > lost. The old conclusion — a seed bound sitting inside a margin that survives it
   > — **does not survive, and is not restated in weaker words, because there is no
   > weaker form of it the evidence supports.** Sources, both committed and both
   > re-read for this correction: `closure_challenge_seed_sensitivity.json` →
   > `overall_equivalent_S_bound`; `campaign/BOARD_RESCORE_2026-08-14.md` §3.1 and
   > §3.4. Withdrawn in the travelling document at commit `cc906ec9`
   > (`closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md` §8).
   >
   > **THE REPLACEMENT BINDING RULE, stated so that it cannot silently go stale.**
   > A margin is a claim about a board at a moment, and a "qualifier" is not a board.
   > So: **no document in this package may quote the margin except as a triple —
   > (1) the margin, (2) the entrant it is a margin over, named, and (3) the board it
   > is measured against, given by ENTRANT COUNT and RETRIEVAL DATE.** As of this
   > writing that reads: *0.001365 over Yang, on the six-entry board retrieved
   > 2026-08-11T23:33Z and re-verified unchanged 2026-08-14T21:01Z.* A commit anchor
   > is **not** an admissible board identifier for a margin: `deb91557` is the frozen
   > four-entry scoring clone, and it scores but does not rank. The same triple is
   > required of the seed bound stated as a fraction of the margin, since that
   > fraction inherits the margin's board. **The figures are regenerable and should
   > not be retyped from here**: recompute them from
   > `campaign/BOARD_RESCORE_2026-08-14.md` §3.1, and if the retrieval date on the
   > face of a sentence is older than the newest board retrieval the lab holds, the
   > sentence is unverified until re-derived — that staleness is now visible on the
   > sentence itself rather than resting on a reader remembering which board was
   > meant. **No instrument enforces this** (docket D85): a strike-and-keep marker
   > adjudicates the very placement it corrects away from
   > `board_placement_faults`, so this rule is enforced by re-derivation and review,
   > not by the guard.

### 5.4 Draft cover email — DRAFT, NOT SENT

> *Rewritten 2026-08-11 against the round-5 payload. Every figure below was read
> from a primary artifact. It is deliberately shorter and plainer than the
> description document: the document is where the exhaustive numbers belong, and
> the email's job is to let a busy steward know what he has been handed and decide
> whether to trust it. **Nothing is sent. §5.6 items 6 and 7 are Katie's.***

> **To:** Ryley McConkey — rmcconke@mit.edu
> **Subject:** Closure Challenge submission — Certonomous (overall 0.056647, our own scoring)
>
> Dear Dr McConkey,
>
> Attached is a `test/` directory with predictions for the eight test cases, in the
> CSV format the README asks for — 1000 × 3, no header, one file per case. A
> description document is attached with it, along with a manifest giving the SHA-256
> of every file and instructions for scoring them from scratch.
>
> Authors: [NAMES — Katie to fill]. Affiliation: Certonomous.
> Reference: [repository or write-up URL — Katie to fill].
>
> **The score.** Through your unmodified scorer — evaluation package commit
> `1c4e22c8`, benchmark commit `deb91557` — the eight files come to **0.056647**
> overall. For a reference point we also scored the supplied RANS fields unchanged
> on the same harness and got **0.1036**; that floor is our own figure, not one the
> benchmark publishes. **This is our local scoring and not a placement. If your
> scoring differs from ours, your number is the number.**
>
> **Five of the eight predictions are not our model.** We would rather say so up
> front than have you work it out:
>
> 1. On `alpha_05_4071_4048` and `alpha_05_4071_2024` the submitted field **is your
>    baseline RANS solve, byte for byte** — verified, not asserted. A decline gate,
>    fitted on 21 training cases and validated on 4 held-out validation cases and
>    never on a test case, judged that correcting them would make them worse and
>    withheld the correction. Anyone submitting your file unchanged scores exactly
>    what we score there, so the credit is the baseline's and not ours.
> 2. On the three ducts the submitted field is a converged forward solve of
>    **QCR2000 with `Ccr1 = 0.3`** — Spalart's published constant, untrained,
>    nothing fitted to anything. An entry already on your board runs the same term.
> 3. Only `alpha_15_13929_4048`, `alpha_15_13929_2024` and `NASA_2DWMH` come from a
>    model of ours: a post-hoc correction to the velocity field of an
>    already-converged RANS solve. It does not modify the turbulence model and
>    nothing is re-solved with the correction folded in — a materially weaker claim
>    than most of the board's, and it is the only claim we are making. We claim no
>    novelty for the decline gate either; classifiers on RANS-only inputs, and their
>    use to control where a correction is applied, are both published work, two of
>    this benchmark's own authors among them.
>
>
> **[REDRAFT REQUIRED BEFORE SENDING — 2026-08-11.]** ~~Our entry is the best number
> on your published board on **4 of the 8 cases — and two of those four are the two
> baseline rows above**, so the count that belongs to our model is 2 of 8.~~ On the
> board as it stands on 2026-08-11 this reads: *our entry is the best number on your
> published board on **2 of the 8 cases**, and **both of those two are the baseline
> rows above** — so **no case on your board is led by our model.** Our overall is
> still the lowest on the board, which is to say this entry wins on consistency
> rather than on any peak, and we would rather say that than let the count imply
> otherwise.*
>
> **The thing we would most want a reviewer to have.** The round-5 change was chosen
> while we already knew our per-case test scores. In the words we used to ourselves
> before any new number existed:
>
> > *"we already know the round-4 test-duct scores (0.0811 / 0.0775 / 0.0325), and
> > any protocol that lets those numbers choose between the QCR field and the
> > existing ML field is test-truth-informed model selection."*
>
> Plainly: we knew the ducts were where we were losing because your harness had told
> us, and that is why the ducts were the target. That is soft, adaptive leakage and
> it is real. Nothing we did afterwards cancels it and we do not offer anything as
> cancelling it. What we did do was close every remaining degree of freedom in
> writing before any solve — the term ships on all three ducts or none, decided on
> `AR_7_Ret_180`, your own suggested validation duct, alone; the constant frozen; the
> thresholds set from training ducts first; and the risk to `AR_14_Ret_180` accepted
> in advance. That case then did regress, 0.0325 → 0.0353, and we left it. The
> description document sets all of this out, together with the same admission for
> round 2, where per-case preview scores are what motivated building the decline gate
> at all, and a variant scoring 0.0675 that we identified and refused because
> selecting it meant choosing cases by their test outcomes.
>
> Six distinct prediction sets have ever been scored — the RANS floor and rounds 1
> to 5. That is a discipline we imposed on ourselves and explicitly not compliance
> with a limit; the benchmark sets none and tells submitters to preview.
>
> **On where that leaves us.** On these eight cases 0.056647 is the lowest overall
> on your board as we retrieved it — the **six-entry** board of **2026-08-11T23:33Z**,
> re-verified unchanged by a read-only fetch at **2026-08-14T21:01Z** — ~~by 0.0029
> over Reissmann, Fang and Sandberg~~ **by 0.001365 over Yang, at 0.058013.** That
> is our own scoring, run locally against the frozen benchmark commit `deb91557`,
> which scores but does not rank; it is not a placement on your board and we do not
> claim one. We
> bootstrapped what the lead is worth rather than leave you to: **P(rank 1) = 50.2%,
> with a 95% interval of 0–97%** — eight cases cannot pin it tighter than that, and 50%
> on its own would sound far more settled than it is. The leads over Yang, Reissmann,
> Wu & Zhang, and Tian, Buchanan, Hickel & Dwight are
> **not statistically decided**; the leads over Liu and over Montoya are, at 98.7%
> and 99.8%. *(~~68%, 2–100%, by 0.0029 over Reissmann~~ — struck 2026-08-11: that
> was the four-entry board. **The 0.0029-over-Reissmann figure opening this paragraph
> was struck only here and left standing there until 2026-08-15, so this letter gave
> two answers to one question for four days; both are now struck and the live figure
> is the 0.001365 over Yang above.**)*
>
> **And our own seed uncertainty takes that lead away rather than qualifying it.**
> ~~Our own measured one-seed training uncertainty on the three cases that
> are our model is 0.002419, which covers 84% of that margin~~ — **struck 2026-08-15:
> that arithmetic was done against a margin over Reissmann on a four-entry board, and
> against the margin that is actually in play it inverts.** 0.002419 is **177%** of
> the 0.001365 above (0.002419 / 0.001365 = 1.77), not 84% of it. Load it adversely
> onto the three cases it applies to and our overall is **0.059047**, above 0.058013
> — the lead is gone. So we are not offering you a lead with an uncertainty attached
> to it: **on this evidence the difference between our number and 0.058013 is not
> distinguishable from the single training seed we happened to draw, and we are not
> claiming our method beats Yang's, or Reissmann's, or Wu and Zhang's, or Tian,
> Buchanan, Hickel and Dwight's.** What we do claim is narrower and we would rather
> claim it plainly: the two comparisons that are decided, against Liu (98.7%) and
> against Montoya (99.8%), and consistency across eight cases rather than a peak on
> any of them. `AR_1_Ret_360` and
> `AR_3_Ret_360` are ties below the precision your board prints rather than per-case
> wins. All of it is reproducible
> from the attached files and your own board in about a minute, which is why we would
> rather compute it for you than have it computed against us.
>
> **One finding that does not depend on our score at all**, and may be worth more to
> you than our entry is: on exactly the two cases our train-only gate declined, your
> supplied baseline beats all four published entries. Every entrant so far has made
> those two cases worse by touching them. We report that as a property of the
> benchmark.
>
> Two questions, if you have a moment:
>
> - The leaderboard credits "Authors." Is a company name acceptable on a row, or do
>   you prefer named individuals with affiliation?
> - Neither the benchmark repository nor the `para-database-for-PIML` dataset carries
>   a licence file. Are there terms of use we should be aware of for a commercial
>   entity training on this data? We redistribute no source data.
>
> With thanks for the benchmark itself, which is the part of this that took the most
> work,
>
> [SIGN-OFF — Katie]

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

1. ~~Fix the docstring in `apply_closure_ph_gate.py` (§4.4).~~ **DONE 2026-07-30.**
2. ~~Generate the eight CSVs **without** a new scoring call (§4.5).~~ **DONE
   2026-07-30, zero scoring calls, enforced in code.**
3. ~~Correct the eval-package version label to the commit hash (§4.6).~~ **DONE** in
   the submission manifest, which cites package commit `1c4e22c8` and benchmark
   commit `deb91557` and records why the `0.2.1` string is not the metric revision.
   *Note for Katie:* if the description document or `closure.html` is to quote a
   version at all, quote the commit hash.
4. ~~Verify or delete the two preprint sentences flagged in §2.2, which were
   attributed to a source no copy of which was on this machine.~~ **DONE
   2026-08-02. Verified verbatim, quotation upheld, section reference sharpened
   to §2.1** — §2.2 and §9.
5. ~~Audit *every* quotation in this document, not only the flagged one.~~ **DONE
   2026-08-02. 28 quotations, all resolved or classified; two defects found and
   fixed** (a stale citation to our own page in §4.7, a punctuation mark added
   inside a quoted commit message in §4.6) — §9.
6. **Katie fills the author names and the reference URL.** — OUTSTANDING
7. **Katie proofreads and approves.** Nothing moves before this. — OUTSTANDING

**Items 1–5 were the lab's to clear and are cleared. Items 6 and 7 are Katie's, and
nothing about this package moves without them.** As of 2026-08-02 the only thing
between this package and the steward is Katie.

---

## 7. ADDENDUM 2026-07-31 — four things that change this document

Everything in §1–§6 above was written on 2026-07-30 against the round-3 entry. Four
findings from 2026-07-31 supersede parts of it. **Read this section before the rest.**

### 7.1 The entry of record is now 0.0654, not 0.0676

A duct-only change (round 4, `sdk/scripts/closure_round4_duct_rescale.py`) took the
entry from 0.0676 to **0.0654**. The five non-duct CSVs were **copied, not regenerated**,
and all five were hash-verified against the round-3 `MANIFEST.json`, so the entire delta
is attributable to the duct family and the decline gate's behaviour is untouched.

*(Board identifier added 2026-08-16: every "of 5" ordinal in this table is against the
**four**-entry clone frozen at benchmark commit `deb91557` (2026-05-04) — four entrants
plus us — which **scores but does not rank**. On the **six**-entry board retrieved
**2026-08-11T23:33Z** and re-verified unchanged **2026-08-14T21:01Z** there are seven rows
counting ours, and the round-5 duct standings are 3rd, 4th and 4th of 7. This table is
kept as round-3/round-4 history and is not the entry of record.)*

| case | round 3 *(ordinals: four-entry `deb91557` frame)* | round 4 *(same frame; live board six-entry, retrieved 2026-08-11T23:33Z)* |
| --- | --- | --- |
| `AR_1_Ret_360` | 0.0919 (last of 5, four-entry board) | **0.0811** (3rd of 5, four-entry board) |
| `AR_3_Ret_360` | 0.0862 (4th of 5, four-entry board) | **0.0775** (3rd of 5, four-entry board) |
| `AR_14_Ret_180` | 0.0303 (best) | **0.0325** (still best, by 0.00003) |

Two consequences must be disclosed, not buried:

- **`AR_14_Ret_180` regressed by +0.0022 and was not reverted**, for the same reason the
  NASA hump's +0.0011 was not: choosing per-case between two models after reading their
  per-case test scores is selection on test outcomes. The fix was frozen on validation
  evidence and applied to all three ducts or none.
- **The `AR_14_Ret_180` ~~best-on-board margin~~ margin over Reissmann collapsed from 0.0022 to
  0.00003** against a published four-decimal value. *(Characterisation struck 2026-08-16 and the
  board identified inside this item: `best-on-board` was true only of the **four**-entry
  `deb91557` frame, in which Yang does not appear. On the **six**-entry board retrieved
  **2026-08-11T23:33Z**, re-verified unchanged **2026-08-14T21:01Z**, this case's best is Yang's
  **0.0250** — so round 4's `0.0325` stood **2 of 7**, tied with Reissmann for **second**, and
  round 5's `0.035339` stands **4 of 7**. The margin over Reissmann is real on either board;
  only the word `best` was not.)* It is a nominal lead, not a meaningful one. §5.3 must say
  so; describing it as a win would be misleading.

New disclosure item for §5.3, and it replaces item 6 outright: the published duct
diagnosis was **wrong**. `I3_S3` and `I4_W2S` are indeed algebraically zero on every
duct — that is reproduced — but they are equally zero on `AR_14_Ret_180`, the duct we
~~score best on~~ **trail by least on**. The mechanism that actually discriminates is that
`Re_y` reaches 1.85× and 2.07× its trained maximum on the two ducts we trail most and 0.90×
on the one we trail least, and *(characterisation struck 2026-08-16 and the board identified
inside this paragraph, to agree with §8.1's already-corrected copy of this same sentence:
`score best on` and `win` were true only of the **four**-entry `deb91557` board. On the
**six**-entry board retrieved **2026-08-11T23:33Z**, re-verified unchanged
**2026-08-14T21:01Z**, `AR_14_Ret_180`'s best is Yang's **0.0250**, so round 3's `0.0303`
stood **2 of 7** and round 5's `0.035339` stands **4 of 7** — we win no duct on the live
board.)*
a gradient-boosted tree cannot extrapolate. Full record:
`closure_challenge_duct_reynolds_transfer.json`. **The fix is validated for no-harm on
every held-out set the rules permit and is NOT proven to close the deficit** — no legal
test of Reynolds transfer at a doubled velocity scale exists in this benchmark.

### 7.2 The 0.1036 floor is our own number, with no external corroboration

`/home/ubuntu/closure-challenge-benchmark/scripts/rans_identity_baseline.py` in the
benchmark clone is **untracked** — it was authored by this lab, not shipped by the
benchmark. (Path corrected 2026-08-14 at `13b965dd`: this read
~~`scripts/rans_identity_baseline.py`~~, which is repo-rooted in shape and resolves in
neither root of this repository — it names a file in the third-party clone, and is now
written with the root it lives in. The file, and this paragraph's claim about it, did not
move.) The benchmark README quotes no
RANS-identity baseline anywhere. 0.1036 reproduces exactly and is honestly derived, but
**any wording implying the floor is the benchmark's own published figure is false and
must be corrected before sending.**

### 7.3 "We are last on the ducts" was never true

The lab's working belief, repeated in internal notes, was that it was last on the board
across the duct family. Re-derived from the harness: at round 3 it was last on
`AR_1_Ret_360` only, 4th of 5 on `AR_3_Ret_360`, and ~~**best on board**~~ **1 of 5 on the
four-entry board** on `AR_14_Ret_180`. *(Characterisation struck 2026-08-16 and the board
identified inside this paragraph: every ordinal in the sentence above, `4th of 5` included, is
against the **four**-entry `deb91557` board. On the **six**-entry board retrieved
**2026-08-11T23:33Z**, re-verified unchanged **2026-08-14T21:01Z**, round 3's `0.0303` on
`AR_14_Ret_180` stands **2 of 7**, behind Yang's **0.0250** — it was never best on the live
board.)* It was also last on `NASA_2DWMH`, which the belief never mentioned.
After round 4 the lab is last on **NASA_2DWMH alone**.

### 7.4 The decline gate is not novel, and the nearest prior art is by the challenge's own authors

Full review: `CLOSURE_CHALLENGE_PRIOR_ART.md`. ~~A classifier reading only the uncorrected
solve and controlling where a data-driven correction may act is established prior art —
Ling & Templeton (2015), Wu, Wang, Xiao & Ling (2017), Steiner, Dwight & Viré (2022),
Buchanan, Lăcătuş, West & Dwight (2025).~~

**Correction 2026-08-05 — the struck sentence rolls two established things into one and
credits two of the four with a mechanism they did not report** (method-priority review
`CLOSURE_METHOD_PRIORITY_REVIEW.md` §4.2, commit `d84b649f`; `CLOSURE_CHALLENGE_PRIOR_ART.md`
§2.1 had it right all along). Read it as two claims, and the description document must
carry it split:

> Classifiers on RANS-only inputs that ***identify*** where the baseline is unreliable
> are established — **Ling & Templeton (2015)**, whose abstract classifies RANS results
> point by point as high or low uncertainty and controls nothing, and **Wu, Wang, Xiao &
> Ling (2017)**, an *a priori* confidence measure. ***Using such a classifier to control
> where a data-driven correction is fitted and applied*** is established separately —
> **Steiner, Dwight & Viré (2022)** and **Buchanan, Lăcătuş, West & Dwight (2025)**.

Everything §7.4 goes on to say is unaffected, and the split makes our position more
defensible rather than less: it shows we know which paper did which thing.

**Tyler Buchanan and Richard Dwight are
co-authors of the Closure Challenge paper itself**; Dwight also co-wrote Steiner et al.
and SpaRTA.

**Mandatory for §5.3, as a new item:** the description document must cite this prior art
and must claim only what survives it — that the gate acts on a whole case rather than a
cell, that it is trained to predict the *baseline's* error rather than distribution
shift, and that its "off" state means submitting the uncorrected field. **Any sentence
presenting confidence-gated correction as novel must be struck.** None currently exists
on `closure.html`, which was checked; the risk is that one gets written.

> **UPDATE 2026-08-02 — the nearest prior art has now been read in full, and it moves
> one thing from "should disclose" to "must not do".** Buchanan, Lăcătuş, West & Dwight
> 2025 was cited here from its abstract because the Computers & Fluids full text is
> paywalled. It is open on arXiv at `2504.06758` and nobody had fetched it. Read end to
> end; full note at `CLOSURE_CHALLENGE_PRIOR_ART.md` §2.4.
>
> **The three distinctions above all survive, and can now be stated against read wording
> rather than inferred.** Their RITA classifier selects *regions inside a case* from
> local ratios of the baseline's own k-equation terms (§2.2: ϕ_{P_k/D_k} = |D_k| /
> (|P_k| + |D_k|), shear layers below 0.55); ours selects *whole cases* from a fit to the
> baseline's error; and their "off" means unmodified SST **in that region of a corrected
> solve**, where ours means the uncorrected field **is the submission** for that case.
>
> **The new constraint.** Their §2.4 and Table 2 give the training set as three 2D
> separated flows: **the NASA wall-mounted hump** (Re_h = 9.3×10⁵, 5.1×10⁴ cells), the
> periodic hill, and the curved backward-facing step. The hump is one of our eight scored
> test cases. Nothing about that is improper on their side — it is their own work in
> their own venue and no challenge rule reaches it. **But their published model
> coefficients (their Appendix D) are off limits to this entry.** Borrowing them,
> warm-starting from them, or calibrating anything of ours against that model's hump
> behaviour would make our submission *indirectly* trained on a test case. That is a
> route we would otherwise have had every reason to take, since it is the best-matched
> prior art we have found, and it is written down here **before** anyone feels the pull
> of it rather than after.

### 7.5 Everything in §4.1–§4.6 still holds

The in-sample gate passes (0 failures, 6 benign review lines, all read). All eight
round-3 CSVs remain 1000×3, finite, header-free, and SHA-256-matched to their manifest.
All four accepted submissions re-score to their published leaderboard values exactly on
this harness, per-case and overall, which is the strongest available evidence the
harness is being driven correctly.

---

## 8. ADDENDUM 2026-08-01 — the duct claim re-derived, the declining rows re-described, and a third refusal

Three tasks were carried this session: verify the duct-input claim against the data
rather than inherit it; establish what the decline gate actually does on the two cases
we "win" by declining and whether our description of them survives scrutiny; and improve
the score honestly if it could be done. **Zero official scoring calls were made. The
entry of record is unchanged at 0.0654 and no number in it moved.**

### 8.1 The duct-input claim: VERIFIED, and worse than we published

Record: `closure_challenge_duct_feature_degeneracy.json`, produced by
`sdk/scripts/closure_duct_feature_degeneracy.py`. Measured on all eight duct cases (4
training, 1 validation, 3 test), from the RANS field and mesh only; ground truth read
for the four suggested training ducts alone, asserted in code.

**The zeros reproduce.** `I3_S3` and `I4_W2S` are zero on every duct, expressed as
*relative* residuals so the verdict does not rest on a raw magnitude — worst case
2.8×10⁻¹⁵ against `I1^1.5`.

**Two identities we had never recorded also hold.** `I2_W2 = −I1_S2` **bit-exactly**
(residual 0.0 on all eight cases) and `I5_W2S2 = −I1_S2²/2` to 3.5×10⁻¹⁶.
**Five of the seven features carry one independent degree of freedom on a duct, not
five.** The effective input dimension is 3, or 4 once round 4's `d/d_max` is added.
Disclosure item 6 of §5.3 — already replaced once by §7.1 — understates the defect and
must be restated at this size.

**The mechanism, which we had not identified.** The baseline k-ω SST duct solve is
*exactly unidirectional*: maximum transverse |U| is ~10⁻¹⁵ against O(10) streamwise,
because a linear eddy-viscosity closure generates no secondary flow in a straight duct.
`gradU` is then a rank-one pure-shear tensor and every invariant of it reduces to a
function of one shear magnitude. **The degeneracy is a property of the baseline we are
correcting, not of duct geometry** — the DNS duct field does carry secondary flow.
Control: on the four periodic-hill test cases the same four residuals run from
2.5×10⁻³ to 9.1×10⁻¹, so nothing is degenerate there and the test is not vacuous.

**The causal half stays refuted, now independently.** The identities hold in identical
measure on `AR_14_Ret_180`, the duct the entry ~~scores best on the board on~~ **trails by
least on**. *(Characterisation struck 2026-08-16 and the board identified inside this
paragraph: `best on the board` was true only of the **four**-entry `deb91557` board. On the
**six**-entry board retrieved **2026-08-11T23:33Z**, re-verified unchanged
**2026-08-14T21:01Z**, this case's best is Yang's **0.0250**, so round 5's `0.035339` stands
**4 of 7**.)* This
reconfirms §7.1 rather than inheriting it.

**A hypothesis of our own, tested and killed.** Every feature is an O(3) invariant of
`gradU`, or a wall distance — all invariant under the y↔z swap that maps the square
duct's evaluation quadrant onto itself. Any `f(features)` must therefore emit the same
vector at a point and its mirror while the truth swaps two components, which looked like
a hard error floor built in by construction. Measured on `AR_1_Ret_180`: the unreachable
component is **0.012% of the correction's energy** (0.0012 in scaled-MAE units against a
0.107 floor), because the true field respects the same symmetry the features do.
**Refuted, and shipped refuted.**

**What binds instead is transfer, and the feature set is not the constraint in-family.**
A k-NN conditional-variance bound on the four training ducts puts the reachable error at
0.011–0.027 against floors of 0.069–0.107. Inside the trained Reynolds number these
features retain ample information. The binding constraint remains the one §7.1 found:
`Re_y` reaches 1.85× and 2.07× its trained maximum on the two ducts we trail and 0.90×
on the one we do not, and no legal test of Reynolds transfer at a doubled velocity scale
exists inside this benchmark.

### 8.2 The two declining rows: what the gate does, and why "best on board" had to go

Record: `closure_challenge_decline_gate_audit.json`, produced by
`sdk/scripts/closure_decline_gate_audit.py`. Zero scoring calls; no test ground truth
read; all scores carried across from the round-4 record rather than recomputed.

**What the gate does: it emits no prediction at all.** The submitted field on both
declined cases was re-derived independently from the benchmark's own supplied k-ω SST
field and mesh, interpolated to the 1000 evaluation points, and diffed against the
shipped CSV: **maximum deviation 5.0×10⁻¹⁰, which is the CSV's own `%.10g` write
precision.** The same test on the two periodic-hill cases the gate *applied* to returns a
deviation of 12% of the local velocity scale, so the test discriminates and is not
vacuously true.

**"Best on board" is not defensible as a headline, and the count of five was worse.**
0.0461 and 0.0719 are properties of a file the organisers hand every entrant. Anyone
submitting it unchanged scores identically. Those values rank *the baseline* above the
field; they do not rank *us* above anyone. The honest count of the eight cases is:

| Attribution | Count | Cases |
| --- | --- | --- |
| Our model, clear lead | **2** | `alpha_15_13929_4048`, `alpha_15_13929_2024` |
| Our model, nominal lead only (0.00003) | 1 | `AR_14_Ret_180` |
| **The baseline led; the gate withheld our model** | **2** | `alpha_05_4071_4048`, `alpha_05_4071_2024` |
| Behind | 3 | `AR_1_Ret_360`, `AR_3_Ret_360`, `NASA_2DWMH` |

**What *is* defensible, and it is a better finding than the one it replaces.** Crossing
the recorded per-case floor against the published per-case leaderboard: **on exactly two
of the eight test cases the uncorrected baseline beats all ~~four~~ **six** published
entries — and they are exactly the two the gate declined.** *(Count corrected 2026-08-16:
"four" was the entrant count of the board frozen at `deb91557`; the live board retrieved
2026-08-11T23:33Z and re-verified unchanged 2026-08-14T21:01Z carries **six** entrants,
seven rows counting ours. Re-derived against it, the finding holds on both cases —
0.0461 against a best published 0.0569 and 0.0719 against Yang's 0.0748 — so the
correction widens the claim rather than weakening it.)* The gate chose them from 21 training cases,
validated on 4 non-test cases, having never seen a test case. **The claim is about the
selection, not the score:** a train-only rule identified, blind, the two flows on which
every published method in the field damages the answer. That is also a finding about the
benchmark that the steward may value more than our own number, and §5.4's cover email now
says so.

**Action taken.** `closure.html`'s headline KPI ("5 of 8 test cases where we lead"), its
per-case table and its tags were rewritten; the two rows are now marked "BASELINE, NOT
OUR MODEL", an uncorrected column was added so a reader can check the attribution
themselves, and the page states in its own voice that the previous wording was true
arithmetic and misleading attribution. **§4.7 called this the highest-priority disclosure
item; it is now stated in the body of the page rather than in a note beneath it.**

**One further false sentence found and fixed.** The page's scoring-call KPI read *"the
benchmark's answers were never used to tune"*, which contradicts our own disclosed record
that round 2's per-case scores motivated building the gate (§4.3). It now states that no
parameter was ever fitted to a test score but that one score did change what we built
next. The footer's `v0.2.1` was also replaced by the commit hash, closing §5.6 item 3 on
the public page as well as in the manifest.

### 8.3 Improving the score: one improvement was available and is refused

On `NASA_2DWMH` our correction is **worse than not correcting**: 0.0632 against a floor
of 0.0621. Submitting the untouched solve there is one file copy and breaks no benchmark
rule. **It is worth about 0.00014 overall** — 0.06543 → 0.06529, arithmetic on our own
recorded per-case values, *not* a new scoring call, and not enough to change our position
against any entrant.

**We are not taking it.** The only reason to single out that one case is that the
benchmark told us its score. Choosing what to submit case by case from the answer key is
precisely what the one strict rule exists to prevent, and it is the same objection that
left the 0.0066 of §4.2 and the `AR_14_Ret_180` regression of §7.1 standing.
**This is the third such refusal on the record and the smallest of the three.** It is
stated on `closure.html` in the lab's own voice rather than left in this file.

No other honest improvement was attempted. *(Board identifier added 2026-08-16: "the best
published entry" and "the gap to rank 1" in this sentence are the **four**-entry
`deb91557` frame in which it was written. On the **six**-entry board retrieved
**2026-08-11T23:33Z**, re-verified **2026-08-14T21:01Z**, seven rows counting ours, we hold
rank 1 of 7 by 0.001365 over Yang, and the duct leader is Yang at 0.0291 / 0.0311 /
0.0250.)* The remaining gap lives in the ducts —
matching the best published entry on the two aspect ratios we trail is worth about 0.011,
more than the entire gap to rank 1 — and every move now visible there is either
contaminated by knowledge of per-case test outcomes or needs evidence this benchmark
cannot supply. A follow-on has been filed to the docket instead
(`closure-duct-tensor-basis-carrier`): the scalar-invariant feature set is provably
three-dimensional on a duct, whereas the tensor basis is not — measured on two duct
training cases, the second basis tensor carries 1.87–2.36× the norm of the first, with
71% of its magnitude and 91% of the third tensor's in the transverse block that generates
secondary flow. That is a specific structural argument for the duct family belonging to a
tensor-basis ansatz, and the machinery to build one was measured working on this hardware
earlier the same day.

### 8.4 What this does not change

The entry of record, its score, its CSVs and its hashes are untouched. The in-sample gate
passes (0 failures; 6 benign review lines, all read). Nothing was submitted, no account
created, no one contacted. Items 4 and 5 of §5.6 remain Katie's and remain outstanding.

---

## 6. What was not done, deliberately

Nothing was submitted. No account was created. No one was contacted — not the steward,
not by email, not via a GitHub issue. No score or claim was altered. Where public
sources do not establish a rule (commercial data-use rights, company author lines),
this document says so rather than inferring a convenient answer.

---

## 9. ADDENDUM 2026-08-02 — every quotation in this document, checked as a set

`w5-audit-every-citation-in-the-submission-draft`. **Zero compute. Zero scoring
calls. No number in the entry moved.** This is the document written to be read by
someone outside this lab, and until today nothing had checked its quotations as a
set — only the one an agent happened to trip over while reading for another purpose.

**Method, so the result can be re-run rather than believed.** Every blockquote run
and every inline `"…"` of 25 characters or more was extracted mechanically from this
file, each normalised for Unicode form, curly quotes, dashes, markdown emphasis and
punctuation, then matched as a substring against the normalised text of every
candidate source on disk: the benchmark clone README at `deb91557`, the evaluation
package README and `pyproject.toml` at `1c4e22c8`,
`sdk/scripts/apply_closure_ph_gate.py`, the round-3 JSON, `closure.html`, and — for
the first time — the full text of the preprint. Anything that failed the automatic
match was resolved by hand and is accounted for below. The script is at
`/tmp/.../scratchpad/audit_quotes.py` for the length of that session; it is
twenty lines of matching and is described here in enough detail to rebuild.

### 9.1 Result

The audit was run twice: once on the document as found (**28 quotations, 15 matched
automatically, 13 to be resolved by hand**), and again after the corrections below
(**30 quotations, 17 matched automatically**, the two added being the preprint
sentences now quoted in their own right). The second run's automatic matches break
down as: **benchmark README 14, preprint 3, evaluation package README 1,
`apply_closure_ph_gate.py` 1.**

The 13 that no machine match could settle are all accounted for, and none of them is
an unsourced claim:

| Class | Count | Verdict |
| --- | --- | --- |
| Our own editorial blockquotes — flags, resolution notes, the draft cover email | 6 | Not citations of anything |
| Quotations of a defect we then fixed, correctly failing to match the fixed file | 3 | **Correct as written** — §9.2 |
| Quotations of our own pages or of git metadata, needing a source the matcher was not given | 3 | **2 defects found, both fixed** |
| Web-only source with no on-disk copy | 1 | **Marked as such** — §9.3 |

**Two defects found, both in citations of sources the lab controls, and neither in a
citation of the benchmark.** That is worth stating in that direction: the quotations
most likely to be wrong were not the organisers' rules, which were transcribed
carefully because they were known to matter. They were our own surfaces, quoted from
memory of what they used to say.

1. **§4.7 quoted `closure.html` as saying *"It is not our model outperforming
   anyone"*. The page has not said that since 2026-08-01**, when §8.2 rewrote the
   section and said it harder. Corrected in place, with the current wording read off
   the page today and quoted instead. **A citation to a live surface goes stale the
   moment the surface improves, and nothing in this lab was watching for that.**
2. **§4.6 quoted the evaluation package's commit message with a full stop the commit
   does not have.** Corrected, and the commit is now cited by its full hash
   `1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162` and its date rather than by its
   abbreviation. A trailing period is a trivial thing to get wrong and a trivial
   thing for a reader to check, which is exactly what makes it worth fixing in a
   document whose credibility rests on precise self-accounting.

The replacement quotation in §4.7 was itself checked the same way rather than pasted
on trust: the sentence now quoted there matches `closure.html` exactly after tag
stripping and entity decoding. Neither defect changed a number, a rule, a score or a
verdict; both changed a sentence describing one, which is the whole of the point.

### 9.2 The two that correctly do not resolve

§4.4 quotes the old `apply_closure_ph_gate.py` docstring — *"Exactly ONE
`closure_challenge.score()`/`evaluate_by_case()` call is made, on the final 8-case
predictions dict"* — as the defect it reports. That sentence is **gone** from the
file, which is the point; the audit confirmed both that it is gone and that the
replacement says what §4.4's resolution note claims it says, at line 37 onward:
*"Exactly ONE \*new\* prediction set is scored"*, followed by the explicit statement
that the run makes four `closure_challenge` invocations and by the note that the
benchmark imposes no scoring-call limit. §8.2 likewise quotes `closure.html`'s
retired KPI *"5 of 8 test cases where we lead"*, verified absent from the page today.
**A quotation that no longer resolves is a defect only when the document claims it
still stands.**

### 9.3 The one that cannot be resolved on this box, said so rather than dropped

§2.7's ERCOFTAC Knowledge Base line — *"Content is available under CC BY 4.0
(AI/ML-training & TDM reserved)"* — was read off a web page on 2026-07-30 and no
copy of that page is on disk. It is left standing, sourced to the page fetch, and
labelled here as web-only. It is also the one line in §2.7 that does not bear on our
compliance: §2.7 already establishes that no ERCOFTAC-derived data enters our model.

### 9.4 What this closes and what it does not

**Closes:** the flagged permission in §2.2 is verified verbatim and the flag is
retired on evidence. Every remaining quotation in this document either resolves to a
file this box holds, or is our own words, or is labelled web-only. **No sentence in
this document is now attributed to a source nobody here has read.**

**Does not close:** an audit run once is a snapshot. Two of the 28 quotations went
stale between 2026-07-30 and 2026-08-02 because the lab improved the pages they cite,
and both were ours. **Any further edit to `closure.html` can restale a citation in
here, and nothing checks that automatically.** Re-run this audit at the moment Katie
approves, not before — the value of the check is in being the last thing done.

---

## 10. ADDENDUM 2026-08-07 — this package now carries the round-5 entry: 0.0566, locally rank 1 of 7 (six-entry board retrieved 2026-08-11T23:33Z, re-verified 2026-08-14T21:01Z)

*(Board identifier added 2026-08-16: "locally rank 1" is **rank 1 of 7** against the
**six**-entry board retrieved **2026-08-11T23:33Z** and re-verified unchanged
**2026-08-14T21:01Z**, seven rows counting ours, by a margin of 0.001365 over Yang against
a seed bound 177% of that margin. It is a local scoring, not an official placement.)*

Everything above describes the round-3/round-4 entries. On 2026-08-07 the
pre-registered round-5 scoring call (the lab's 6th cumulative) was made and
**accepted: the entry of record is now round 5, overall 0.0566** —
~~**rank 1 of 5 scored locally at benchmark commit `deb91557`**~~ *(struck
2026-08-12: "of 5" was the four-entry board plus us. Fetched 2026-08-11T23:33Z
the live board carries **six** entries — point **rank 1 of 7 entrants counting
us**, and the margin is 0.001365 over the new leader **Yang**, not 0.002878 over
Reissmann; the `deb91557` pin scores, it does not rank)* (0.056647 vs
Reissmann's **transcribed** 0.059525 — the board publishes 0.0595 to four
decimals and a like-for-like full-precision re-score gives 0.0595335; see §5.2).
Local scoring, not an official placement; if the steward's own scoring differs
from ours, the steward's number is the number (§5's rule, unchanged).
**P(rank 1) = 50%**, and eight cases cannot pin that tighter than
**0–97% at 95%** (`campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md`, six-entry
board fetched live 2026-08-11). ~~P(rank 1) = 68%, 2–100% at 95%~~ — struck the same
day: four-entry board, no longer exists.

**And the lead is not statistically decided** against any of the four nearest entries.
Our **0.001365** margin over **Yang** sits against a per-case spread **fifteen** times
larger; our 0.002878 over
Reissmann sits against a per-case spread five times larger, so on a different set
of eight cases the ordering could reverse; the same is true of Wu
and Zhang and of Tian, Buchanan, Hickel & Dwight. The margins over Liu and Montoya do survive that test. ~~The standing is
two cases wide~~ **The standing is three deletions wide** *(struck 2026-08-12:
"two cases wide" was the four-entry board; on the six-entry board deleting any
one of `alpha_15_13929_4048`, `alpha_15_13929_2024` or `alpha_05_4071_4048`
costs the point rank — to 2, 3 and 2 respectively)* — on the eight-case mean, `alpha_15_13929_2024` alone supplies more
than the whole margin, and `NASA_2DWMH` alone costs more than it. `AR_1_Ret_360`
and `AR_3_Ret_360` are ties below the precision the board publishes to, and are
not per-case wins.

> **Wording note — CORRECTED 2026-08-11, RE-CORRECTED 2026-08-12. What stood
> here was stale, and this document contradicted itself about the same figure in
> two places — and then the correction itself went stale the same day it was
> written.**
>
> *(Re-correction note, 2026-08-12. This block was written on 2026-08-11 before
> the six-entry board fetch at 23:33Z that same day
> (`campaign/BOARD_MOVED_2026-08-11.md`). Until 2026-08-12 its closing "rule that
> now governs" paragraph stated the four-entry figures — 68%, 67.6%, 2–100%, a
> two-pair not-decided list — as current, twenty lines below this same section's
> live 50% / 0–97% figures. A block titled CORRECTED carrying superseded values
> is worse than an uncorrected one, because its title invites trust. Per L-76 the
> stale figures are struck below where they stand, each with its six-entry value
> beside it; verified by re-running `sdk/scripts/probability_of_rank.py` on
> 2026-08-12, which matches `campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md`
> to the digit.)*
>
> ~~**Wording note, deliberate (chief ruling 2026-08-10).** This paragraph is the
> EXTERNAL wording and carries no probability figure, even though this document
> lives internally. It is a draft of an outward artifact, and the quantified
> posterior behind these sentences is internal by its own gate — so the number is
> kept out of the draft *now*, rather than left for someone to remember to strip
> on the day it is sent. The quantified version lives in
> `campaign/PROBABILITY_OF_RANK_2026-08-10.md` and does not travel with this
> package.~~
>
> **The two passages that disagreed, and which one was right.** The struck note
> above said the figure is internal by its own gate and does not travel with this
> package. The Ladder V banner in §5 of this same document — the §5.4/§5.2 row of
> its table — says the opposite: that a round-5 rank claim "**must now carry
> P(rank 1) = 68% with its 2–100% interval**", because the chief withdrew the
> internal-only gate. **The §5 row is the one that is right** — right on the
> RULE, that the figure travels with the entry; the figures inside that quoted
> sentence are the four-entry board's, struck and recomputed in the rule
> paragraph below *(note added 2026-08-12)*. Both were written
> on 2026-08-10; the withdrawal came later that same day, after Ladder V's
> cold-reproduction pass recomputed the figure as **0.674 from public data — the
> published board plus our own eight CSVs — in about a minute**, with no access to
> the internal document. A figure an outsider reproduces trivially is not
> protected by being withheld; withholding it buys nothing and only looks
> concealed, to precisely the reader this package's disclosure strategy exists to
> convince. The struck note was never re-read against the ruling that overtook it.
>
> **The rule that now governs every rank claim in this package.** The figure
> **TRAVELS with the entry**. Any rank claim here — internal or outward, including
> the paragraph above — carries **P(rank 1) = ~~68%~~ 50%** (~~67.6%~~ **50.2%**
> over 400,000 case-level bootstrap resamples; struck 2026-08-12, the struck
> values were the four-entry board's) **together with its interval**:
> ~~**2–100% at 95%**~~ **0–97% at 95%** by double bootstrap, because eight cases
> cannot pin it tighter. It also carries the
> not-decided pairs: ~~the leads over Reissmann and Wu & Zhang~~ **four leads —
> over Yang (the leader, t = −0.19), Reissmann, Wu & Zhang, and Tian, Buchanan,
> Hickel & Dwight —** are
> **not statistically decided** *(struck 2026-08-12: the two-pair list was the
> four-entry board's)*, while the leads over Liu and Montoya are decided (98.7%
> and 99.8%). The one prohibition that replaced the withdrawn split: **no surface may
> state the figure without its interval** — and, since the board moved on
> 2026-08-11, **without its board**: a probability quoted against a board that no
> longer exists is exactly what this block carried for a day — a bare ~~68%~~ 50%
> is a worse claim than no
> figure at all, because a bare probability sounds settled and eight cases do not
> support settled.
>
> **What this correction did NOT do, and whose call that was.** As written on
> 2026-08-10 this block left the §10 paragraph above carrying the qualitative
> clause only, with no figure: rewriting the package's outward prose was judged the
> package owner's decision, not the correction's, and the paragraph was flagged as
> owing the figure rather than quietly left looking compliant.
> **Closed 2026-08-11 by the V8 fix round**, which added **P(rank 1) = 68%** and the
> **2–100% at 95%** interval to that paragraph *(historical: those were the
> figures the fix round added; hours later the same day the six-entry fetch
> superseded them both, and the paragraph above now carries 50% / 0–97% with the
> 68% struck where it stood — note added 2026-08-12)*. The deferral is kept above rather
> than deleted, so the record still shows who declined the edit and who made it;
> what is *not* kept is a live sentence saying the paragraph still owes a figure it
> now carries. Sources: `campaign/PROBABILITY_OF_RANK_2026-08-10.md` (head banner;
> superseded four-entry computation, kept); `campaign/LADDER_V_TRIPLE_VERIFICATION.md`
> (V8 amendment, 2026-08-10; its figures repaired to the six-entry board
> 2026-08-12); live derivation `campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md`,
> reproduced by `sdk/scripts/probability_of_rank.py` re-run 2026-08-12.

What changed in the package's payload:

- **The 8 CSVs to send are now
  `demo-output/website/closure_challenge_submission_round5/test/`** (hashes
  in that directory's `MANIFEST.json`). The five non-duct CSVs are
  byte-identical to the round-3/4 submissions, so every disclosure above
  about the PH gate and the NASA prediction stands as written.
- **The three duct predictions are no longer an ML correction at all.** They
  are converged forward solves of the untrained QCR2000 constitutive term
  (`kOmegaSSTQCR`, `Ccr1 = 0.3`, Spalart 2000's published constant, nothing
  fitted to anything), applied all-or-none under a rule frozen at
  `0bade54a` before any solve and passed on the benchmark's own suggested
  validation duct. §5.3's leakage-disclosure story gets *simpler* for the
  ducts: there is no trained duct model left in the entry to disclose.
- **One disclosure must be updated, not softened**: `AR_14_Ret_180`
  regressed 0.0325 → 0.0353 and its 0.00003 nominal ~~best-on-board tie~~ **tie
  for second** is lost *(characterisation struck 2026-08-16 and the board identified
  inside this item: the tie was against the **four**-entry `deb91557` board, in which
  Yang does not appear, and the best-on-board reading was true only there; on the
  **six**-entry board retrieved **2026-08-11T23:33Z**, re-verified unchanged
  **2026-08-14T21:01Z**, this case's best is Yang's **0.0250**, so round 4's `0.0325`
  stood **2 of 7** tied with Reissmann and round 5's `0.035339` stands **4 of 7**)*
  — the pre-registration accepted that risk in writing before the
  score existed, and the regression is reported, not reverted. ~~Best-on-board
  is now **4 of 8**, not 5 of 8; §5.3 and the cover email's item 2 must say
  4 and cite §0f of `CLOSURE_CHALLENGE_STATUS.md`.~~ *(Struck 2026-08-12:
  4 of 8 was the four-entry board. Against the six-entry board fetched
  2026-08-11T23:33Z, best-on-board is **2 of 8** — both `alpha_15` hills lost
  to Tian, Buchanan, Hickel & Dwight — and both survivors are the organisers'
  own unmodified RANS baseline passed through the decline gate, so **the
  model's own count is ZERO of 8**. §5.3 and the cover email's item 2 must
  state the 2-of-8 count only WITH that zero-of-8 disclosure — a bare 2-of-8
  is itself a defect — matching this document's own §5.2 table, and cite
  `campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md` §3a.)*
- Full round-5 record: `closure_challenge_round5_qcr.json`;
  pre-registration `campaign/R5_PREREGISTRATION.md` (@ `e865076b`).

**Items 6 and 7 of §5.6 remain OUTSTANDING and remain Katie's.** Nothing
moves without them. Per §9.4, re-run the quotation audit at the moment of
approval — this addendum itself restales any quoted position claims above
(0.0654, "5 of 8", rank 3), all of which are now historical.


---

## Paper-library forwarding note — appended 2026-08-18

**Nothing above this line was edited.** The `docs/papers/` paths cited above were
correct when the sentences carrying them were written. Commit `5c0d2483`
(2026-08-18) refiled the paper library into topic subdirectories and renamed most
of its files, and `4323d7e3` lowercased two of the new names afterwards. Those
citations were left exactly as they stood, because each records where a file was
at the moment its statement was made; rewriting one would have changed what this
record says happened.

Each pair below was resolved by **git blob identity** — the old path's blob hash
matched to the path carrying the identical hash — and not by name similarity, and
each destination was then confirmed against the filesystem at commit `4323d7e3`.

| as cited above | the same bytes, as of `4323d7e3` |
| --- | --- |
| `docs/papers/hanna_dinh_youngblood_bolotnov_1710.09105.pdf` | `docs/papers/data_driven_rans/hanna_dinh_youngblood_bolotnov_1710.09105.pdf` |
| `docs/papers/wu_zhang_sst_qcrc_challenge_description.pdf` | `docs/papers/data_driven_rans/wu_zhang_sst_qcrc_challenge_description.pdf` |

The whole 87-path table was appended to `docs/papers/README.md` in the same
commit. `python3 scripts/check_paper_citations.py` re-derives the rows above and
exits non-zero if any destination stops resolving.
