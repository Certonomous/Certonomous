# Ladder V — rung V15: the ladder's own text re-enters the claims table

**Rung V15 (A15). Executed 2026-08-10 (clock; see §1.1). Owner: an agent that wrote none
of the text below and has never written to the closure line.**

Brief: **any text written during the ladder — by any pass, including fix passes and
including the chief — must pass V8's claims table before the ladder goes green.**
Otherwise the fix pass is the last unverified writer and the ladder certifies everything
except its own output.

**I produced none of the text audited here.** Not Pass 1, not Pass 2, not Pass 3, not the
chief's citation note, not the Pass-4 dispatch. I have made no edit to any file audited
below. **Scoring calls made by this rung: ZERO; the ledger stands at 6.** Every check is
static, arithmetic, or a re-read of an artifact already on disk. **Nothing was sent.**

---

## 0. FRAME, STATED BEFORE ANY COUNT

Every count in this document is worthless without its frame. Here they are, first.

- **"ladder text"** means: lines *added or modified* by a commit in `c8031a03..HEAD`
  that touches the round-5 submission package or one of its claim-bearing surfaces.
  It is derived from `git log`/`git diff`, not from any pass's own summary of what it
  wrote. Commits in the range that touch neither are enumerated and then set aside with
  the reason (§1.2).
- **"claim"** means a sentence asserting a quantity, a date, a count, a rank, or a
  compliance fact. Prose that only reasons is out of scope.
- **"FAIL"** means I could demonstrate the failure by running something or displaying a
  byte. Where I could only argue, the row says INCOMPLETE or OBSERVATION.
- **"surface"** means a file, not a document family. `benchmarks.json` and
  `wall/wall.json` are two surfaces even though they carry the same string.

**Reach, proved before any absence is reported.** All sweeps below use `/bin/grep`
directly — never the ignore-honouring wrapper — with `--exclude-dir=.git`, and
enumerate tracked files via `git ls-files -z | xargs -0`. Compressed logs were not in
scope for this rung (no claim below rests on a log); had they been, `zgrep` would apply.
**Every negative carries a positive control**, seeded into a scratch file and confirmed
to fire, recorded inline at the row that depends on it.

**What this frame structurally cannot contain.** It cannot see text written into
untracked working trees by the six agents live in this repo right now; the corpus moved
under me during execution (HEAD advanced from `8ef715c1` to `e844eb0b` while I was
reading, and one peer commit — `fc212c5a` — landed a finding that overlaps mine, see
§4.1). It cannot see anything a pass wrote and did not commit. It cannot adjudicate
whether an artifact is *itself* right; it can only ask whether the sentence matches it.

---

## 1. THE TEXT SET, DERIVED MECHANICALLY

### 1.1 A clock audit, run before any date is used

```
$ date -u
Mon Aug 10 21:14:26 UTC 2026
```

**Today is 2026-08-10.** Every commit in the ladder range carries a `2026-08-10`
committer date. This matters immediately and is finding **F2** below.

### 1.2 The commit set

Derived from `git log --format='%H %ci %s' c8031a03..HEAD` plus `--name-only`. The
dispatch's list was **incomplete by five commits** and correct in everything it did name.

**IN SCOPE — commits that wrote ladder text onto the package or its surfaces:**

| commit | UTC | author-role | files touched (package/surfaces only) |
|---|---|---|---|
| `636c0b91` | 20:51:41 | Pass 3 (cold) | `campaign/LADDER_V_PASS3_COLD_2026-08-11.md` (+467) |
| `c1187949` | 20:52:44 | **chief** | `docs/PRODUCT_LIST.md` — Pass-3 entry **+ the P(rank 1) reversal ruling** |
| `5a21b4fd` | 20:55:37 | Pass 1 | `campaign/LADDER_V_PASS1_2026-08-11.md` (new) |
| `e59ae644` | 20:56:41 | **chief** | `LESSONS.md` (L-53), `docs/PRODUCT_LIST.md` (**the date correction**) |
| `4ec0ade5` | 20:58:42 | Pass 1 | `LADDER_V_PASS1` |
| `97eb51d2` | 21:01:12 | Pass 1 | `LADDER_V_PASS1` (re-run pre-registration) |
| `92562841` | 21:01:57 | Pass 2 | 12 files — see §1.3 |
| `bbe0e4db` | 21:03:20 | **chief** | `docs/PRODUCT_LIST.md` — Pass-2 entry |
| `9fea8481` | 21:07:11 | Pass 1 | `LADDER_V_PASS1` (re-run result) |
| `2ef8ae3b` | 21:08:17 | **chief** | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` — the citation fix |
| `a4b9f70c` | 21:08:35 | **chief** | `LESSONS.md` (L-54, about this ladder's coordination defect) |
| `8ef715c1` | 21:11:27 | **Katie** | `campaign/LADDER_V_TRIPLE_VERIFICATION.md` — Pass 4 / V14 / V15 |

**Corrections to the dispatch's list, in order of importance:**

1. **`8ef715c1` is missing and it is the one I was told to read first.** The Pass-4
   dispatch is itself an edit to `LADDER_V_TRIPLE_VERIFICATION.md`, which is **row 8 of
   the audited claim-bearing surface list** in `PROBABILITY_OF_RANK` §7. Two different
   authors wrote into that file during the ladder — Pass 2's V8 amendment at 21:01 and
   Katie's V14/V15 at 21:11 — and the dispatch's list names neither as an edit to a
   claim-bearing surface. The rung that says "any text written during the ladder" omitted
   the commit that created the rung.
2. **`c1187949` is missing, and it carries a ruling, not a summary.** The chief's
   PRODUCT_LIST entry at 20:52 is where the P(rank 1) internal-only gate is reversed
   ("*the cold agent computed 0.674 from public data*"). Pass 2 then executes that
   reversal at 21:01. The ruling's own text is ladder text and is claim-bearing.
3. **`e59ae644` is missing, and it is the ladder's own self-correction on dates** —
   the fix whose failure to travel is finding F2.
4. **`bbe0e4db` and `a4b9f70c` are missing** — the chief's Pass-2 PRODUCT_LIST entry and
   L-54. Both make quantitative claims (§4.6).
5. **Nothing in the dispatch's list was misattributed.** `636c0b91` is Pass 3;
   `5a21b4fd`/`4ec0ade5`/`97eb51d2`/`9fea8481` are all Pass 1; `92562841` is Pass 2;
   `2ef8ae3b` is the chief's. All confirmed by `--name-only` and by commit body.

**IN RANGE, DELIBERATELY OUT OF SCOPE** — enumerated so the exclusion is a decision and
not an oversight. None touches the submission package, any of the 16 claim-bearing
surfaces, or any closure artifact: `cb686975`, `0462b45b` (launcher exec bits),
`73bb3836` (`sdk/chief_engineer/exec_bits.py`), `093a4b37` (L-55 / fleet audit), and the
eleven commits `975d4098`…`e844eb0b` that landed **during this rung's execution**
(memory architecture, instrument integrity, monitor standard). One of those,
`fc212c5a`, independently reproduces part of finding F2 and is credited there rather
than claimed here.

### 1.3 The text, by volume

`git diff --numstat`, package and surfaces only:

| file | +lines | author |
|---|---|---|
| `campaign/LADDER_V_PASS1_2026-08-11.md` | 872 | Pass 1 |
| `campaign/LADDER_V_PASS3_COLD_2026-08-11.md` | 467 | Pass 3 |
| `campaign/LADDER_V_PASS2_2026-08-11.md` | 436 | Pass 2 |
| **`closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md`** | **349** | **Pass 2 — the largest block of new OUTWARD prose** |
| `docs/PRODUCT_LIST.md` (closure entries only) | ~95 | chief |
| `campaign/PROBABILITY_OF_RANK_2026-08-10.md` | 109 / −6 | Pass 2 |
| `closure_challenge_submission_round5/README.md` | 93 | Pass 2 |
| `LESSONS.md` (L-53, L-54) | ~75 | chief |
| `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` | 48 / −3 | Pass 2 (banner) + chief (citations) |
| `campaign/LADDER_V_TRIPLE_VERIFICATION.md` | 40 / −3 | Pass 2 + Katie |
| `CLOSURE_CHALLENGE_PRIOR_ART.md` | 25 | Pass 2 |
| `closure.html` | 7 / −4 | Pass 2 |
| `sdk/scripts/closure_round5_qcr_forward.py` | 7 / −2 | Pass 2 |
| `sdk/scripts/build_benchmarks.py` | 6 / −1 | Pass 2 |
| `benchmarks.html` | 3 / −1 | Pass 2 |
| `benchmarks.json`, `wall/wall.json` | 1 / −1 each | Pass 2 |

**≈2,630 added lines of ladder text, of which 442 (DESCRIPTION_DOCUMENT + README) are
outward — text intended to leave the lab.** The outward 442 get the strictest reading.

---

## 2. THE CLAIMS TABLE OVER LADDER TEXT

Every quantitative sentence → the named artifact → verdict.
**Result: 4 FAIL, 5 INCOMPLETE, 3 OBSERVATION, 21 PASS.**

### 2a. `DESCRIPTION_DOCUMENT.md` — the outward document (Pass 2)

| # | claim, and where | named artifact | verdict |
|---|---|---|---|
| **T1** | §5: overall **0.056647**, per case 0.0501 / 0.1011 / 0.0461 / 0.0719 / 0.0455 / 0.0400 / 0.0353 / 0.0632; eval pkg `1c4e22c8`, benchmark `deb91557` | `closure_challenge_round5_qcr.json` → `official_test_harness_result` | **PASS.** All eight match `round5_per_case` exactly; `round5_overall_full` = 0.056647191704213645. Independently re-scored by Pass 3 |
| **T2** | §5: floor **0.1036**; §1 8 files 1000×3 headerless | same JSON; `MANIFEST.json` | **PASS** |
| **T3** | §3.1: declined rows 0.0461 / 0.0719 **are the supplied RANS field** | JSON `rans_identity_floor_per_case` = 0.0461 / 0.0719, identical | **PASS — and the identity is the proof, not an assertion** |
| **T4** | §3.1: on those two the supplied baseline **beats all four** published entries | JSON `per_case_published_at_deb91557` | **PASS.** 0.0461 vs best-other 0.0569; 0.0719 vs best-other 0.0760 |
| **T5** | §3.2: best-on-board **4 of 8**, *two of which are the baseline rows*; the count belonging to our model is **2 of 8** | same block: four `1 of 5` rows, two of them `alpha_05_4071_*` | **PASS. Banned-list item cleared** — the count is stated with its organiser-baseline qualification, in the same sentence, unhedged |
| **T6** | §2: duct scores land **within 0.0004** of Wu & Zhang's on all three | board vs `round5_per_case_full` | **PASS.** Δ = 0.00003 / 0.00008 / 0.00034 |
| **T7** | §3.3b: round-4 duct scores **0.0811 / 0.0775 / 0.0325**, quoted verbatim from the rule freeze | `campaign/R5_RULE_FREEZE.md` @ `0bade54a`, line 11 | **PASS — quote is verbatim at the frozen commit**, checked with `git show 0bade54a:` rather than the working copy |
| **T8** | §3.3b: the whole **−0.0088** move | JSON `delta_vs_round4` = −0.0088 (`_full` −0.008784) | **PASS** |
| **T9** | §3.3b: gate thresholds V1 ≤ 0.70, V2 *r* ≥ 0.85; **measured 0.4770 / 0.9284** | `campaign/R5_PREREGISTRATION.md` §V1/V2 and the round-5 JSON `pre_registration` | **PASS** |
| **T10** | §3.3b / §3.4: AR_14 **0.0325 → 0.0353**, tie lost, not reverted | JSON round4 0.0324698 → round5 0.035338619 (+0.0028688) | **PASS** |
| **T11** | §3.3b: **no `*_LES` file** in any of the three test-duct run dirs, both `AR_7` arms have them | filesystem, verified by Pass 3 and Pass 2 independently | **PASS — and the `AR_7` presence is the positive control that makes the absence a measurement** |
| **T12** | §3.7: continuity table — corrected hills **~10%**, `NASA_2DWMH` **0.66%**, declined rows untouched | `closure_challenge_stability_physicality_audit.md`: `div_over_grad_scale_corrected` 0.1046 / 0.0967 / 0.006637; declined ratio 1.000 | **PASS** |
| **T13** | §3.7: **the 3 ducts (round 5) = 5.3×10⁻⁴ – 8.5×10⁻⁴**, improved **27–63×** | `closure_challenge_round5_qcr_forward.json`, via `R5_PREREGISTRATION.md` §6 | **PASS.** Measured 8.5e-4 / 5.3e-4 / 5.4e-4; improvements 27× / 58× / 63× |
| **T14** | §3.7, next sentence: ***"We state the measured number rather than 'satisfies continuity by construction': 5.8×10⁻⁴ is not machine zero."*** | same JSON | **FAIL — F1. 5.8×10⁻⁴ is `AR_7_Ret_180_qcr`, the VALIDATION duct, which is not in the submission.** The three submitted ducts measure 8.5e-4 / 5.3e-4 / 5.4e-4. See §3 |
| **T15** | §3.8: seed bound **0.002419**; margin **0.0028863**; **covers 84%** | `closure_challenge_stability_physicality_audit.md` §1 (`S_bound` = 0.002419); Pass 3's re-score | **PASS.** 0.002419 / 0.0028863 = 0.8381. Pass 2 explicitly checked that 84% requires the *unrounded* bound — correct, and the document states both unrounded |
| **T16** | §5: **P(rank 1) = 68%**, 67.6% at B = 400,000; MC 67.5–67.8%; LOO 38–91%; **double bootstrap 95% = 2–100%** | `campaign/PROBABILITY_OF_RANK_2026-08-10.md` §1 | **PASS on the standing rank rule.** The figure never appears without its interval; the interval that dominates (2–100%) is given the emphasis; the "*68% sounds settled and eight cases do not support settled*" sentence is present in the outward text |
| **T17** | §5: undecided pairs **named** — Reissmann (t = −0.495), Wu & Zhang (t = −0.953); Liu 98.7% and Montoya 99.8% decided; token `not statistically decided` present | `PROBABILITY_OF_RANK` §1 pairwise table | **PASS.** Margins 0.0029 / 0.0058 / 0.0170 / 0.0212 and P(we lead) 69.4 / 84.7 / 98.7 / 99.8 all match |
| **T18** | §5: "*the point estimate is 68%*" — but the bootstrap's Reissmann input is **0.059525**, the number this same section declares *"not a number you publish"* and replaces with **0.0595338** | `PROBABILITY_OF_RANK` §4 ("Inputs") vs `DESCRIPTION_DOCUMENT` §5 | **INCOMPLETE — F4.** The margin was recomputed on the corrected basis; the probability was not, and the document does not say so. Numerically negligible (9×10⁻⁶); rhetorically not, in a document whose entire posture is precision about precision |
| **T19** | §5: standing **two cases wide**; delete `alpha_15_13929_2024` → rank 2; delete `NASA_2DWMH` → **P(rank 1) 91%**; `AR_1`/`AR_3` ties at 0.00003 / 0.00008; dispersion **five times** the margin; 4 wins / 4 losses vs Reissmann; 7 of 8 vs Liu and Montoya; effective *n* **nearer 3 than 8** | `PROBABILITY_OF_RANK` §2/§3/§4 | **PASS.** LOO table gives 91.1%; per-case win/loss recomputed from the board block: 4–4 vs Reissmann, 7–1 vs Liu, 7–1 vs Montoya |
| **T20** | §5 omits the seed sensitivity that moves P(rank 1) **52% → 81%**, which the internal record calls *"the correct internal sentence"* | `PROBABILITY_OF_RANK` §2 | **INCOMPLETE — F5.** §3.8 gives the seed *bound* and its 84% coverage of the margin, so the fact is not hidden; but the single most alarming derived number in the internal record does not travel, in a document that argues withholding a computable figure "only looks concealed". The same argument applies here and is not made |
| **T21** | §4: prediction byte-identical across rounds 3–5, written **16 hours before** the Buchanan paper is first mentioned and **three days before** it was read in full | `fe121af2` 2026-07-31T06:53Z; `92840d8c` 2026-07-31T23:13Z; `15530f97` 2026-08-02T05:30Z | **FAIL on "three days" — F3.** 16 h is exact (16:20:00). The full-read gap is **1 day 22 h 37 m** — under two days. Verified by `git log -1 --format=%ci` on all three, differenced in Python |
| **T22** | §4: `grep` for Buchanan artifacts returns **zero hits in executable files**; only coefficient is `Ccr1 = 0.3` | `CLOSURE_CHALLENGE_PRIOR_ART.md` §2.4; Pass 1 V5 @ `303247bb`; Pass 3 | **PASS** |
| **T23** | §4: "***No sentence in this package presents confidence-gated correction as novel***" | banned list, §7.4 | **PASS. Banned-list item cleared.** Sweep of the closure line for `novel*`: every occurrence is `is not novel` or the prohibition itself |
| **T24** | §3.3b closing: "*It does not prohibit reading your own preview scores — the benchmark ships the test ground truth and instructs submitters to preview*" | **none named** | **INCOMPLETE — F6.** The claim is TRUE — benchmark README @ `deb91557` line 98: *"You can preview what your score will be using the benchmark dataset's python package"*, and line 21 *"All other decisions are left to the submitter."* But this is the single most exculpatory factual sentence in the disclosure and it cites nothing. Every other load-bearing claim in the document names its source |
| **T25** | §3.3a: RidgeCV alpha **0.7499**, threshold **0.1263**, gate decisions **0.1503 / 0.1525 → apply, 0.0420 / 0.0034 → decline**, AUC 1.0 on 4 of 4 | `closure_challenge_trained_entry_round3_gated.json`; echoed at `apply_closure_ph_gate.py:170` | **INCOMPLETE.** All values verified — but `closure_challenge_trained_entry_round3_gated.json` is **not in the document's own sources footer**, which lists six files and omits the one that supports disclosure 3a |
| **T26** | §3.9: **six** distinct prediction sets scored; self-imposed, **not** benchmark compliance; Blum & Hardt arXiv:1502.04585 | the ledger; benchmark README (silent on any limit) | **PASS. This is the reverse of the C5 defect and it is stated correctly** |
| **T27** | §6: "*Not an official rank. Not submitted*"; §5 "*a local scoring and not an official placement*" | banned list | **PASS. Banned-list item cleared — no official-rank language.** Sweep of both new package files: 5 hits, all disclaimers or a true statement about the published board |
| **T28** | header + status block: "***Written 2026-08-11 by Ladder V Pass 2***" | the clock | **FAIL — F2.** `date -u` = 2026-08-10. See §4.1 |

### 2b. `README.md` — the new outward package file (Pass 2)

| # | claim | artifact | verdict |
|---|---|---|---|
| **T29** | expected result **`0.056647191704213645`**; per case ×8; benchmark `deb91557…`, scorer `1c4e22c8…`, two separate repos | round-5 JSON; Pass 3's independent cold reproduction | **PASS** |
| **T30** | version note: `__init__.py` says 0.2.1, `pyproject.toml` at the pin says 0.3.1 | the pinned checkout | **PASS**, and it is the install hazard Pass 3 hit firsthand |
| **T31** | hashes frozen at `e865076b` **before** the scoring call at `07a7fe9e`, **12m 59s** later; 5 of 8 byte-identical to round 4 | `MANIFEST.json`, pre-registration §3, `filecmp` | **PASS**; the integrity command was executed verbatim by its author, 8/8 OK — a package instruction that has never been run is a guess, and this one was run |
| **T32** | "*These three are the only rows an outside reader cannot re-derive from public inputs*" | Pass 3's cold reproduction | **PASS — and it is a concession, correctly placed in a README** |
| **T33** | "*Written 2026-08-11 by Ladder V Pass 2*" | the clock | **FAIL — F2** |

### 2c. Ladder-written text on the four external web surfaces (Pass 2)

| # | claim | artifact | verdict |
|---|---|---|---|
| **T34** | `benchmarks.html` hero tile, `benchmarks.json`, `wall/wall.json`, `build_benchmarks.py`: 4 of 8 **+ the organiser-baseline qualification**, naming both cases | §0f; JSON board block | **PASS. Banned-list item cleared on all four**, and the generator was re-verified key-by-key against both JSONs so the literal cannot drift back |
| **T35** | the same four surfaces make a **rank claim** ("Rank 1 of 5 scored locally") and carry the token, but carry **no P(rank 1) and no interval** | the V8 amendment adopted **in the same commit** | **INCOMPLETE — F7.** Under the rule this commit adopts, a rank claim must carry the figure with its interval. Pass 2 names this in §6 and classes it "*a follow-on item and not a defect of this sweep*". The rule binds **surfaces**, and this pass **edited these surfaces**. See §4.3 |
| **T36** | `closure.html` prior-art rewrite: identify (Ling & Templeton 2015, Wu et al. 2017) vs control (Steiner 2022, Buchanan 2025), named separately | the 2026-08-05 correction `d84b649f`; the `.tex` which had it right | **PASS — the struck sentence is gone and the mandated split is verbatim.** This is the ladder's single best outward fix |
| **T37** | `closure_round5_qcr_forward.py` docstring: ledger scoped to its own run, cumulative **six** stated | the ledger | **PASS** — the fix is correct; its date stamp is F2 |

### 2d. The chief's citation fix, `2ef8ae3b` — audited as a writer like any other

The commit body claims: *"Anchors re-verified against HEAD twice by the rung that owns
them."* Verified against the code, not accepted.

| # | claim | verification | verdict |
|---|---|---|---|
| **T38** | `_load_ground_truth_U` at **128** and **228** | `/bin/grep -n` on `sdk/scripts/apply_closure_ph_gate.py`: line 128 inside `for case in gate._PH_TRAIN:  # 21 cases, train only` (126); line 228 inside `for c in ph._PH_TRAIN:` (225) | **PASS — both anchors correct at HEAD** |
| **T39** | test loop at **178**, `# no U_LES read` at **179**; body citation corrected to **178–180** | read directly: `for case in ph._PH_TEST:` at 178; `_load_rans_fields(...)  # no U_LES read` at 179; `build_features` at 180 | **PASS** |
| **T40** | executable assertions at **84–86** | `closure_baseline_error_gate.py:84–86` = the three `assert` statements | **PASS** |
| **T41** | "**Ladder V rung A3 re-verified every anchor against HEAD twice**" | `LADDER_V_PASS1_2026-08-11.md`: A3 is Pass 1's label for V3; anchors derived at lines 282–284 in the first run and re-derived at 751–760 in the pre-registered re-run (`9fea8481`) | **PASS — "twice" is literally true and the rung named exists.** The note does not overclaim |
| **T42** | "*shifted by a docstring fix **on 2026-07-30*** that moved the code without moving the reference" | `git log -- sdk/scripts/apply_closure_ph_gate.py`: three commits ever; the shift is `fe121af2`, **2026-07-31 06:53:00 +0000**. `git show` confirms it is the §4.4 docstring fix, −4/+17 = **+13**, matching 115→128, 215→228, 165–167→178–180 | **FAIL — F8. The date is wrong by one day** in a note whose entire subject is stale references. Everything else in the note is exact |

**Verdict on the chief's fix: the edit is correct and the "twice" claim survives
verification. One date is wrong.** The claim I was asked to distrust held; the claim
nobody flagged did not.

### 2e. Pass 2's own report — where its claims table graded itself

| # | claim | verification | verdict |
|---|---|---|---|
| **T43** | **C9 PASS:** "*Swept the corpus for `comfortab*`: **every occurrence in the closure line is the prohibition***" | `/bin/grep -rniI "comfortab" --exclude-dir=.git .` — **positive control seeded and fired.** `campaign/PROBABILITY_OF_RANK_2026-08-10.md:151` reads *"Larger and **more comfortable** than the Reissmann comparison"* — a comfort descriptor applied to a margin, in the closure line, in a file this pass edited. `CLOSURE_RANK1_CAMPAIGN.md:341` is a second | **FAIL — F9.** The narrow banned-list item (no *comfortable AR_14 lead*) is genuinely clear. The **sentence offered as the evidence for it is false**, and a positive control on the sweep would have shown it. `git log -S` puts the sentence at `b2aa6887`, 2026-08-10 16:00 — **pre-ladder**, so it is not ladder-authored; the false claim about it is |
| **T44** | **C13 PASS on all 16 claim-bearing surfaces** — each names the pairs and carries the token | re-swept: 20 files carry the token (16 claim-bearing + 3 ladder records + 1 untracked `.aux`); the 16 do name both pairs | **INCOMPLETE — F7 again.** C13 grades 16 surfaces PASS against the rank rule **two rows before C14 withdraws that rule's external half**. Six of the 16 fail the amended version. The table does not re-grade them |
| **T45** | invariant 3 restated as "**no surface carries the figure without its interval**" and reported holding | swept every figure-bearing surface for an interval, regex `2.{1,3}100%\|38.{1,3}91\|26.{1,3}94\|double bootstrap`, **positive control fired**: `campaign/CHALLENGE_SLATE_2026-08.md:37` carries *"P(rank 1) = 68%"* with **no interval**, and still says *"internal only"* | **FAIL — F10.** The prohibition the ladder adopted — *"a bare 68% is a worse claim than none"* — is violated by a live tracked surface at the moment of adoption, and the sweep that reported the invariant holding measured the opposite direction (externals lacking the figure), never this one |
| **T46** | `dist/certonomous-demo.zip` ships `site/closure.html` and `site/benchmarks.html` carrying **0.0654 and 0.0676**, zero caveats, zero sweep token | opened the tracked zip: `closure.html` contains 0.0654 **and** 0.0676; `benchmarks.html` contains 0.0676 (not 0.0654); neither contains 0.0566 or the token | **PASS on substance, OBSERVATION on "zero caveats"** — the bundled `closure.html` does say *"UNSUBMITTED · NO RANK"* and *"hold no rank"*. Zero **sweep token** is exactly right; "zero caveats" overstates. The finding stands and the bundle is still stale |
| **T47** | "*One defect this pass created and then caught*" — the figure typed into a sentence forbidding it, removed before commit | `/bin/grep` of the committed draft: the figure appears at line 521 **because the amended rule now requires it there**, not as a leak | **PASS — the self-report is honest and the artifact agrees** |

### 2f. Pass 1, Pass 3, and the chief's PRODUCT_LIST / LESSONS entries

| # | claim | verification | verdict |
|---|---|---|---|
| **T48** | Pass 1: "*Line numbers have NOT shifted since 2026-08-08*"; A3 leg (c) **FAIL**, citations still stale by +13 | file history shows no change to the script since `fe121af2`; the citations were stale at the moment Pass 1 wrote it | **PASS. Pass 1 called its own assigned fix un-made and graded itself FAIL for it** |
| **T49** | Pass 3: P(rank 1) = **0.674** at B = 200,000 | its own bootstrap; internal doc gives 0.676 at B = 400,000, MC interval 67.5–67.8% | **OBSERVATION.** The two are consistent within Monte Carlo noise, but **two different figures now circulate in ladder text** — the outward document says 67.6%, the V8 amendment and PRODUCT_LIST both say "0.674 … the figure" — and no document reconciles them. Harmless arithmetically; a reader who checks both finds an unexplained difference |
| **T50** | chief, PRODUCT_LIST: baseline beats all four on the two declined cases, **0.046108 vs 0.0569; 0.071863 vs 0.0760** | board block | **PASS** |
| **T51** | chief, PRODUCT_LIST: trained ML on the hump *"measurably WORSE than doing nothing (**+0.00014**)"* | Pass 3 §: 0.063198 vs 0.062061 = **+0.001137 on the case**, ÷8 = **+0.000142 on the overall** | **OBSERVATION — the number is right and its unit is unstated.** Pass 3's own table gives both; the PRODUCT_LIST paraphrase gives only the overall-equivalent beside a case name |
| **T52** | chief, `LESSONS.md` L-53: V10 wrote the sentence at 02:08:13, V5 committed its sweep at **02:21** — thirteen minutes | `git log -S` cited in the entry | **PASS — and this is the lesson that generated this rung** |
| **T53** | Katie, `8ef715c1`: V14/V15 added; "*the send gate: all 15 rungs green (13 original + V14/V15)*" | the ledger table lists V1–V13 | **PASS** |

---

## 3. THE DISCLOSURE SECTION — §3.3b, judged on its own terms

This is the entry's most important admission, its newest outward text, and the reason the
rung exists. Two questions were put to me.

### 3.1 Does every quantitative sentence in it map to an artifact?

**Yes, with one exception, and the exception is next door in §3.7.**

§3.3b itself is clean: the round-4 duct scores are a verbatim quote from
`R5_RULE_FREEZE.md` at the frozen commit `0bade54a` (T7, checked with `git show` against
the commit, not the working copy — the point of a frozen artifact is defeated by reading
the mutable file); −0.0088 is the JSON's own `delta_vs_round4` (T8); 0.4770 / 0.9284 are
the pre-registration's (T9); the AR_14 loss is the JSON's (T10); the truth-file absence
carries its own positive control (T11). `Ccr1 = 0.3` is Spalart's, proved in-house by
Pass 1 and independently by Pass 3.

**The one unattributed load-bearing sentence in §3.3b is exculpatory** (F6/T24): *"It
does not prohibit reading your own preview scores — the benchmark ships the test ground
truth and instructs submitters to preview."* It is **true** — I read the benchmark README
at `deb91557`, line 98 — but it is the only claim in the section that carries no pointer,
and it is precisely the claim a hostile reader will want to check. Every other sentence in
the document names its source. **The disclosure's defence is the one part of it that is
not cited.**

**And the failure is in §3.7, the disclosure next door** (F1/T14). §3.7 tabulates the
three submitted ducts at 5.3×10⁻⁴ – 8.5×10⁻⁴ — correct — and then, in bold, offers **5.8×10⁻⁴**
as "*the measured number*" the document is being honest by stating. `closure_challenge_round5_qcr_forward.json`
labels its arms:

```
/arms/AR_7_Ret_180_qcr   div_over_grad = 0.00057983   ← the 5.8e-4
/arms/AR_1_Ret_360_qcr   div_over_grad = 0.00085136
/arms/AR_3_Ret_360_qcr   div_over_grad = 0.00052808
/arms/AR_14_Ret_180_qcr  div_over_grad = 0.00054396
```

**`AR_7_Ret_180` is the validation duct. It is not in the submission.** The number
offered as the measured non-solenoidality of the submitted duct fields belongs to a case
the reader will not receive, and it **understates the worst submitted duct (8.5×10⁻⁴) by
32%** — i.e. it errs in the direction that flatters the entry, inside the paragraph whose
whole rhetorical purpose is to refuse flattery. The sentence one line above it already
gives the correct range, so the document contradicts itself within four lines. Pass 2
carried the same number into its own claims table at C6, so the error is in two ladder
documents.

### 3.2 Does it admit before it mitigates, or do the mitigations do the admission's work?

**It admits first, and cleanly. This is the strongest piece of writing the ladder
produced.** The structure is:

1. *"This is the disclosure a reviewer is most entitled to, and it was missing from every
   earlier draft of this package."* — the concession about the concession, first.
2. The lab's own words, quoted, from before any round-5 number existed.
3. *"**we knew the ducts were where we were losing, because the harness had told us, and
   that knowledge is why the ducts were the target.** The whole −0.0088 move, and the
   entire reason there is a rank claim at all, was selected in knowledge of per-case test
   outcomes."*
4. *"**No mitigation below cancels that sentence, and none is offered as cancelling it.**"*
5. **Then** the five mitigations, under the heading *"What was then closed, in writing,
   before any solve"* — including the one that cost a real result (AR_14) and was honoured
   anyway.
6. *"We think the freeze is a good answer. We do not think it is a complete one, and we
   would rather you weighed it than found it."*

The admission is in plain language, unhedged, before any defence; the mitigations are
explicitly pre-disclaimed as not doing the admission's work; and the strongest mitigation
is one that *cost* the entry something. **A reader who reads only the bold sentences of
§3.3b comes away with the concession, not the defence** — which is the operational test.

**Two reservations, neither fatal:**

- **The closing paragraph gives the last word to a rules argument.** *"The rule as written
  prohibits training or validating on test-case data. That did not happen. It does not
  prohibit reading your own preview scores…"* is placed **after** both the admission and
  the mitigations. It is pulled back by the two sentences that follow it, so the section
  ends balanced rather than exculpatory — but the one sentence in §3.3b that reads as
  lawyering is also the one sentence with no citation (F6). Fix the citation and the
  lawyering reads as fact instead.
- **The section is disclosure "3b" in a numbered list.** The document's own text calls it
  *"the largest single change in the entry"* and *"the disclosure a reviewer is most
  entitled to"*. It is disclosure number four of nine, at line 109 of 349, sharing a
  number with 3a. Nothing is buried — but the numbering ranks it below "best-on-board
  count" (3.2), which is not the judgement the prose makes.

**Verdict on §3.3b: it passes, and it passes on the hard criterion.** The disclosure does
not bury its concession under its defences. The defect that touches it is F1, in the
neighbouring disclosure, and F1 is serious for a different reason: it is a number that
runs *for* the entry inside the section whose credibility depends on numbers never doing
that.

---

## 4. FAILURES, RANKED

### F1 — BLOCKING. A validation-case measurement is presented as the submitted files' measurement, in the outward document

`DESCRIPTION_DOCUMENT.md` §3.7. **5.8×10⁻⁴ is `AR_7_Ret_180_qcr`**, not any submitted
duct. Submitted values are 8.5 / 5.3 / 5.4 ×10⁻⁴. The error understates the worst
submitted case by 32% and runs in the entry's favour. It contradicts the table four lines
above it, and it is repeated in `LADDER_V_PASS2_2026-08-11.md` C6.
**Why it ranks first:** it is in the outward package, in a disclosure, in the flattering
direction, in the one document written specifically so that a reviewer would not have to
take the lab's word for anything. Owner: the Pass-2 author. Artifact:
`closure_challenge_round5_qcr_forward.json` `/arms/*/div_over_grad`.
*Reported, not fixed.*

### F2 — BLOCKING. Nine closure surfaces, including both new outward package files, are dated one day into the future

`date -u` reads **2026-08-10**; every ladder commit carries 2026-08-10; and the following
assert **2026-08-11** as the date of their own writing:

| surface | text | outward? |
|---|---|---|
| `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md:11` | "*Written 2026-08-11 by Ladder V Pass 2*" | **YES — travels with the entry** |
| `closure_challenge_submission_round5/README.md:5` | "*Written 2026-08-11 by Ladder V Pass 2*" | **YES — travels with the entry** |
| `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:502` | "*Added by Ladder V Pass 2 (rung V8), 2026-08-11*" | the send draft |
| `CLOSURE_CHALLENGE_PRIOR_ART.md:192` | "*Ladder V Pass 2, rung V9, 2026-08-11*" | no |
| `campaign/LADDER_V_TRIPLE_VERIFICATION.md:59` | "*V8 amendment, 2026-08-11*" | no |
| `campaign/PROBABILITY_OF_RANK_2026-08-10.md:3` | "*chief ruling, 2026-08-11*" | no |
| `sdk/scripts/closure_round5_qcr_forward.py:32` | "*re-run under Pass 2, 2026-08-11*" | no |
| `scripts/self_audit.py:275` | "*Ladder V Pass 2 (V6/V10, 2026-08-11)*" | no |
| three filenames: `LADDER_V_PASS{1,2,3}_*_2026-08-11.md` | a date used as a sort key | no |

**This is not a new discovery and I do not claim it as one.** The chief caught the class
at `e59ae644` (20:56) and corrected `docs/PRODUCT_LIST.md` in place; a peer agent
independently measured its scope at `fc212c5a` (21:15) and reported *twelve* tracked
files. **What is new here is that the peer's twelve does not include the two documents
that leave the lab.** My own enumeration — `git ls-files -z | xargs -0 /bin/grep -lI
"2026-08-11"` — returns **17** tracked files, of which some carry the string legitimately
as a quotation of the corrected error (`PRODUCT_LIST`, `MEMORY_ARCHITECTURE`).

**Why it ranks second:** the ladder found the defect, wrote the lesson, fixed one file,
and shipped it in the package anyway. That is L-53's exact shape — a fix that does not
travel — occurring inside the ladder built to stop it. A future-dated cover document is
also the first thing a hostile reader notices and the cheapest thing to disbelieve.
*Reported, not fixed — several of these files have live owners.*

### F3 — MAJOR. "Three days before" is one day twenty-two hours

`DESCRIPTION_DOCUMENT.md` §4, the Buchanan firewall — the entry's compliance chronology,
the claim the document itself says is proof *"chronological rather than an assurance"*.

```
CSV written    fe121af2  2026-07-31 06:53:00 +0000
first mention  92840d8c  2026-07-31 23:13:49 +0000   → 16 h 20 m   ✓ "16 hours"
read in full   15530f97  2026-08-02 05:30:22 +0000   → 1 d 22 h 37 m   ✗ "three days"
```

The 16-hour half is exact. The three-day half overstates the gap by ~55%, and it
overstates it **in the direction that makes the firewall look safer**. It originates in
`LADDER_V_PASS2_2026-08-11.md` §5(b), which cites the right commit and the right
timestamp and then does the arithmetic wrong; the outward document inherited it verbatim.
Two days is still a decisive gap — the claim survives being stated correctly, which is why
stating it incorrectly is gratuitous. *Reported, not fixed.*

### F4 — MAJOR. The probability and the margin rest on different values of the same opponent's score

`DESCRIPTION_DOCUMENT.md` §5 corrects "Reissmann's published 0.059525" to a like-for-like
**0.0595338** and uses it for the margin (0.0028863). The **68% and every pairwise
probability beside it** come from `PROBABILITY_OF_RANK`, whose §4 states its input as the
transcribed **0.059525**. The bootstrap was not re-run on the corrected basis and the
document does not say so. Numerically 9×10⁻⁶ — but the section's whole claim on the
reader is that it is careful about exactly this kind of thing, and it silently is not, in
the paragraph where it says so. *Reported, not fixed.*

### F5 — MAJOR. The seed sensitivity does not travel, and the ladder's own argument says it should

The internal record's sharpest derived number — *"a seed draw the lab did not control
moves P(rank 1) from 52% to 81%"*, which it calls the correct internal sentence — is
absent from the outward document. §3.8 gives the bound and its 84% coverage, so nothing is
concealed. But the ladder reversed the internal-only gate on 68% on the argument that a
computable figure withheld *"only looks concealed"*, and 52–81% is computable from the
same public inputs by the same route. **The reversal's own logic was applied to one figure
and not to its neighbour.** *Reported, not fixed.*

### F6 — MODERATE. The disclosure's only uncited sentence is its defence

`DESCRIPTION_DOCUMENT.md` §3.3b, the "does not prohibit reading your own preview scores"
clause. True (benchmark README @ `deb91557`, line 98; line 21) and uncited, in a document
that cites everything else. *Reported, not fixed.* Adding "(benchmark README §Submission,
`deb91557`)" would close it.

### F7 — MODERATE. Four external surfaces were edited by this ladder and left non-compliant with the rule the same commit adopted

`benchmarks.html`, `benchmarks.json`, `wall/wall.json`, `build_benchmarks.py` each make a
rank claim, carry the token, and carry **no P(rank 1) and no interval**. Commit `92562841`
both adopts *"any rank claim, internal or external, carries P(rank 1) and its interval"*
and edits all four without applying it. Pass 2 names the gap in §6 and classifies it *"a
follow-on item and not a defect of this sweep"*, and C13 grades all 16 surfaces PASS two
rows before C14 withdraws the rule those 16 were graded against.

**The classification is where I disagree with Pass 2, and it is the V15 question
exactly:** the rule binds surfaces, and these are surfaces this pass wrote to. A pass that
edits a surface after a rule changes is that surface's most recent author. *Reported, not
fixed.*

### F8 — MODERATE. The chief's citation note has a wrong date

`2ef8ae3b` says the shift came from *"a docstring fix on **2026-07-30**"*. It is
`fe121af2`, **2026-07-31 06:53:00 +0000** — the file has three commits in its entire
history and this is the only one that could have caused a +13 shift (`git show` confirms
−4/+17 in the §4.4 docstring). **The note's substantive claims all verify** (T38–T41,
including the "twice", which is literally true). The date does not, in a note whose
subject is references that went stale. *Reported, not fixed — the chief's file.*

### F9 — MODERATE. Claim C9's supporting sweep result is false

`LADDER_V_PASS2_2026-08-11.md` C9: *"every occurrence in the closure line is the
prohibition."* `/bin/grep -rniI "comfortab"` (positive control seeded and fired) returns
`PROBABILITY_OF_RANK_2026-08-10.md:151` — *"Larger and more comfortable than the Reissmann
comparison"* — a comfort descriptor on a margin, in the closure line, in a file this pass
edited in the same commit. `CLOSURE_RANK1_CAMPAIGN.md:341` is a second.

**The banned-list item itself is clear**: no surface claims a comfortable AR_14 lead, and
`git log -S` puts the offending sentence at `b2aa6887` (2026-08-10 16:00), **before** the
ladder. So the verdict is right and its stated evidence is wrong — which is worse than a
wrong verdict with honest evidence, because it is the shape that survives review. This
pass ran positive controls on four other negatives and caught a broken regex by doing so
(§2c of its report). It did not run one here. *Reported, not fixed.*

### F10 — MODERATE. The prohibition the ladder adopted is violated by a live surface at the moment of adoption

`campaign/CHALLENGE_SLATE_2026-08.md:37` carries *"P(rank 1) = 68%"* with **no interval**
and still says *"internal only"*. The ladder's new rule: *"no surface may state the figure
without the interval — a bare 68% is a worse claim than none."* Pass 2's restated
invariant 3 is reported as holding; the measurement behind that report ran in the opposite
direction (externals that lack the figure), and never asked which surfaces carry the
figure bare. The file predates the ladder (`7f4c2657`, 16:49) so it is not ladder text —
but **it is the first thing the ladder's own new rule should have caught, and the ladder's
own sweep reported the rule holding.** *Reported, not fixed.*

### Lesser observations (not ranked as failures)

- **T49.** Two figures for the same quantity circulate in ladder text — 67.6% (outward
  document) and 0.674 (V8 amendment, PRODUCT_LIST, both calling it "the figure"). Within
  Monte Carlo noise at their respective B, and no document says so.
- **T25.** `closure_challenge_trained_entry_round3_gated.json` supports disclosure 3a and
  is absent from the outward document's own sources footer.
- **T46.** "Zero caveats" on the `dist/` bundle overstates — the bundled `closure.html`
  does carry *"UNSUBMITTED · NO RANK"*. Zero **sweep token** is exact, and the bundle is
  still round-3/4 and still tracked and still shipping.
- **T51.** *"+0.00014"* is the overall-equivalent of a +0.0011 case regression; the unit
  is not stated where it is quoted.
- **§1.2.1.** The dispatch that created V15 omitted the commit that created V15.

---

## 5. VERDICT — IS THE LADDER'S OWN OUTPUT CLEAN ENOUGH FOR THE LADDER TO GO GREEN?

**NO. V15 FAILS. Two blocking defects sit in the text the ladder itself wrote, and both
are in documents that leave the lab.**

The ladder's substantive work is not in question and this rung did not attack it. The
score is real and reproduced bit-for-bit by a cold agent. The prior-art split is fixed on
the public page. The best-on-board qualification is now on all four external surfaces with
the generator re-verified. Nine of Pass 2's findings were fixed with positive controls.
**And the disclosure section — the thing V15 was told to look hardest at — is the best
writing in the package: it admits before it mitigates, it disclaims its own mitigations,
and its strongest mitigation is one that cost the entry a result.**

But the rung's premise was that a verification campaign is where new unverified claims are
born, and it is right:

- **F1** puts a validation case's number in the submitted files' row, in the flattering
  direction, in a disclosure, in the outward package.
- **F2** dates both outward package documents one day into the future, on a defect the
  ladder itself diagnosed, wrote a lesson about, and fixed in exactly one file forty
  minutes before shipping the package that still has it.
- **F3** overstates a compliance chronology by 55%, in the direction that flatters, in a
  claim the document offers as proof-by-chronology.
- **F7** shows the ladder writing to four external surfaces and leaving them
  non-compliant with the rule it adopted in the same commit — and then classifying that as
  someone else's item.
- **F9** and **F10** are the same failure at one remove: the ladder's own compliance
  claims about the banned list and its new prohibition are, in two places, not what the
  greps say.

**None of these is a rule violation, none is a withdrawal risk, and none touches the
science.** Every one of them is in the layer between the work and the reader — which is
precisely where Pass 2 said the entry was weakest, and it turns out to be where the
verification of that finding was weakest too. **L-53's lesson was that the fix for a class
is where that class reappears. The claims-table pass produced text that fails the claims
table.**

**F1 and F2 must be corrected before the ladder goes green.** F3, F4, F5, F6, F7 should be
corrected before anything is sent. F8, F9 and F10 are corrections to the record and to the
sweeps, not to the entry.

**One thing this rung cannot certify:** I verified the ladder's text against its named
artifacts. I did not re-verify the artifacts. Where Pass 1, Pass 2 and Pass 3 measured
something and I read their measurement, this rung inherits their reliability and says so.

---

**Signed: the Ladder V rung V15 owner, 2026-08-10 (clock).**
Zero scoring calls; ledger unchanged at 6. Nothing was sent, emailed, uploaded or filed.
Read-only except this file. No file audited above was edited by this rung.
