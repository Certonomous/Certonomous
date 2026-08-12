# Closure Challenge — submission requirements, measured against the round-5 package

**SUBMISSION IS PARKED. Nothing has been sent, emailed, filed, uploaded, or
registered. Every send is Katie's personally.** This document records what a
first send WOULD require and measures the lab's package against it. Written
2026-08-12 at repo HEAD `5c9c63fb`.

---

## 1. Provenance of the source, stated first because it matters

The submission procedure below comes from **the challenge's own GitHub README as
pasted by Katie on 2026-08-12 from the live page**. The fleet did not fetch it;
no network read of the upstream repo was made for this document.

**Cross-check, executed 2026-08-12:** the pinned local clone of the benchmark at
commit `deb91557` (2026-05-04) carries the same submission instructions at
`README.md` lines 92–100, matching Katie's paste on every operative sentence
(the four numbered steps, the steward email, "Submissions are accepted
anytime!", and the strict rule). So although the upstream HEAD has moved since
the pin (`d572d40c`, six-row leaderboard —
`campaign/BOARD_MOVED_2026-08-11.md`), **the submission procedure itself is
unchanged between the pinned commit and the live page Katie pasted.** Two
independent sources, one live and one pinned, agree.

One naming note: Katie's paste lists the hump test case as "NASAHUMP". The
canonical machine name is **`NASA_2DWMH`** — that is the directory name in the
benchmark's `data/`, the file name in `data/evaluation_points/`
(`NASA_2DWMH_points.csv`), and the file name used by all four accepted
submissions archived in the pinned clone. The lab's CSV uses `NASA_2DWMH.csv`,
which is correct.

## 2. The submission procedure, as now known

Verbatim from the README (Katie's paste, confirmed against the pinned clone at
`deb91557`):

1. *"Save your interpolated predictions in CSV format under the respective
   directories in the `test` subdirectory of the benchmark dataset. You can
   easily get the evaluation points using the python package for the challenge.
   These points are also provided for convenience under
   `data/evaluation_points`."*
2. *"You can preview what your score will be using the benchmark dataset's
   python package."*
3. *"Send your `test` subdirectory to Ryley McConkey: rmcconke@mit.edu . Also
   include a list of all authors, and any relevant references (e.g., papers,
   github repos, etc.)"*
4. *"The benchmark steward (currently, Ryley McConkey) will evaluate your
   predictions, and update the leaderboard accordingly."*

Plus: *"Submissions are accepted anytime!"* and the strict rule: *"It is
strictly forbidden to train or validate on any data from the test cases… If you
are found to have trained or validated on any of the test cases, your submission
will be automatically withdrawn, and a note will be made on the leaderboard."*

**The "respective directories" ambiguity, resolved by execution rather than by
reading.** Step 1's wording could mean per-case subdirectories. Two measurements
settle what is actually accepted:

- The scorer's own loader (`_load_csv_predictions` in
  `closure_challenge/eval.py` at the pinned scorer commit `1c4e22c8`) reads
  **flat `{case}.csv` files in a single folder** — `folder / f"{case}.csv"` for
  each case in `case_names()`.
- Of the four accepted submissions archived in the pinned benchmark clone,
  **three (wu, montoya, wang) are flat `{case}.csv`** files; one (reissmann)
  uses per-case directories each holding a `predictions.csv`. Both layouts were
  accepted and scored.

The lab's package uses the flat layout — the one the scorer's code path reads
directly and the one three of four accepted entrants used.

## 3. Docket D31 — the eight submission-policy questions, audited against the paste

D31 (`docs/DOCKET.md`, filed 2026-08-11 at `281a6dc9`) recorded that five of the
eight submission-policy questions have no answer in any open source. The eight
are enumerated in `campaign/CLOSURE_STAGE1_AND_C2_STATUS.md` §4 (rows 1–8).
Audited one by one against Katie's 2026-08-12 paste:

| # | Question | Verdict | Basis |
|---|---|---|---|
| 1 | Registration required? | **ANSWERED — none.** | The pasted procedure has no registration step anywhere, and *"Submissions are accepted anytime!"* Already VERIFIED 2026-08-11 with a passed negative control; the paste re-confirms. |
| 2 | Attribution — what accompanies the send? | **ANSWERED.** | *"Send your `test` subdirectory to Ryley McConkey: rmcconke@mit.edu . Also include a list of all authors, and any relevant references (e.g., papers, github repos, etc.)"* |
| 3 | Entries per team? | **STILL OPEN.** | The paste says nothing about entry counts. No limit stated, and no statement that multiple are allowed — exactly as D31(a) recorded. |
| 4 | Corrected resubmission after scoring? | **STILL OPEN** as a rule. | *"Submissions are accepted anytime!"* is a deadline statement, not a resubmission policy; reading it as one would be overclaim. Practice evidence (steward re-scored entries in place at `44540c8f`) remains practice, not rule — D31(b) stands. |
| 5 | Must hyperparameter tuning be disclosed? | **STILL OPEN.** | The paste's relaxed-rules sentence (*"You are free to use your own input features, base turbulence model, data assimilation technique, etc."*) broadens what is permitted; it says nothing about what must be disclosed. D31(c) stands. |
| 6 | Licence on submitted predictions and code? | **STILL OPEN.** | The paste contains no licence language. D31(d) stands. |
| 7 | The strict rule — what exactly is forbidden, with what penalty? | **ANSWERED.** | Verbatim in the paste: training or validating on test-case data → automatic withdrawal plus a leaderboard note. |
| 8 | Deadline? | **ANSWERED — none.** | *"Submissions are accepted anytime!"* |

**The honest headline: the paste re-confirms the three questions that were
already answered and answers NONE of the five open ones.** D31's count stands
unchanged — five of eight (entries per team, resubmission, hyperparameter
disclosure, licence, and whether a company may occupy the Authors row — the
Authors-row question being the unresolved half of #2) remain steward questions,
answerable only by asking, and asking is an external interaction reserved to
Katie. What DID change today: the procedure itself moved from
"reconstructed from a pinned clone" to "confirmed against the live page by
Katie's own read", which is a provenance upgrade, not a policy answer.

## 4. Readiness checklist for a first send, measured 2026-08-12

The entry package is at
`demo-output/website/closure_challenge_submission_round5/` (DESCRIPTION_DOCUMENT.md,
MANIFEST.json, README.md, `test/`).

### 4.1 What the steward asks for, item by item

| Steward asks | Lab has? | Path | Verified how (all executed 2026-08-12) |
|---|---|---|---|
| The `test` subdirectory of CSV predictions, one per test case | **YES** | `demo-output/website/closure_challenge_submission_round5/test/` | 8 files present; names exactly match the 8 basenames in the benchmark's `data/evaluation_points/`: `alpha_15_13929_4048`, `alpha_15_13929_2024`, `alpha_05_4071_4048`, `alpha_05_4071_2024`, `AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180`, `NASA_2DWMH` |
| CSV format the scorer can read | **YES** | same | Each file: **1000 rows × 3 columns**, comma-delimited, **zero alphabetic characters** (headerless; counted by grep over every file). The evaluation-points files are likewise 1000×3, so row counts match the demanded points. Layout matches the scorer's loader (`{case}.csv`, flat) and the majority accepted practice (§2) |
| Integrity of the files | **YES** | `MANIFEST.json` | `sha256sum -c` against MANIFEST.json: **8 of 8 OK**. The same hashes are frozen in `campaign/R5_PREREGISTRATION.md` §3 (committed before the scoring call, per that record) |
| "A list of all authors" | **NO — Katie's decision** | `DESCRIPTION_DOCUMENT.md` line 5 | Field reads `[KATIE TO FILL — named individuals with affiliation, or the company …]`. No value has been invented. Note: whether a company may be the author is open question #2/(e) above |
| "Any relevant references (e.g., papers, github repos, etc.)" | **PARTIAL — Katie's decision** | `DESCRIPTION_DOCUMENT.md` line 9 | Field reads `[KATIE TO FILL — repository or write-up URL]`. The document body already carries dated method citations (e.g. Spalart 2000 for `Ccr1 = 0.3`) and the challenge's own citation block is known (arXiv 2603.28884); what is missing is the lab's OWN reference URL, which requires a decision about what, if anything, is made public |
| A description of the method | **YES, exceeds requirement** | `DESCRIPTION_DOCUMENT.md` | Not demanded by the README, but accepted practice includes it (wu's archived submission ships `description_document.pdf`). Ours is markdown; whether to convert to PDF is a presentation choice, not a gap |

### 4.2 The measured gap list — everything standing between the lab and a sendable package

1. **Authors list: EMPTY, Katie-only.** Blocking by construction — the README
   requires it and the field is a placeholder.
2. **Reference URL: EMPTY, Katie-only.** Blocking for the same reason, and it
   drags a second decision behind it (what the URL points at).
3. **Five policy questions remain open** (§3), four of which D31 marks as
   binding a first send. None can be closed from documents; all are steward
   questions reserved to Katie.
4. **No structural gap in the `test/` subdirectory.** Names, row counts, column
   counts, headerlessness, hashes, and layout all verified by execution today.
   This is the part of the package that is DONE.
5. **The recorded score is carried, not recomputed.** The package README states
   `0.056647191704213645` from the round-5 scoring call (the ledger stands at 6
   official scoring calls; none was made today and none is proposed). Any rank
   statement must be re-anchored against the live six-row board at send time —
   the board Katie pasted has Yang at 0.0580 at rank 1; the lab's recorded
   number is lower, and NOTHING about that is a claim of placement, because
   nothing has been submitted.

## 5. Authors and references — whose call

The steward's step 3 requires an authors list and references. The package
deliberately carries `[KATIE TO FILL]` in both fields, and this document
re-states why: **who is credited (named individuals, the company, or both) and
what the lab points to publicly are Katie's decisions, not the fleet's.** The
open question of whether a company name is acceptable on the Authors row (§3,
question 2/(e)) is itself one of the steward questions only Katie may ask.

## 6. The compliance question that actually matters

The one strict rule carries the one severe penalty: **automatic withdrawal plus
a public note on the leaderboard.** This is the highest-stakes claim in the
package, so here is where the evidence actually sits, with its strengths and its
thin spots stated plainly.

**Where the evidence sits:**

- **The package's own disclosure**:
  `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md` §3a (adaptive
  leakage rounds 1–3), §3b (round-5 duct targeting, disclosed at full
  strength), §5 (train/val/test disjointness enforced by executable assertions,
  21/4 split = the benchmark's own suggested split, test list imported solely to
  assert non-intersection).
- **The adversarial code audit of 2026-07-30** (recorded in
  `ACTIVE_RESEARCH.md`, "Adversarial compliance audit"): ground-truth reads in
  `apply_closure_ph_gate.py` occur only inside loops over the 21 training cases;
  the test-case loop loads RANS fields only.
- **Coverage of that audit over the round-5 bytes, verified by execution
  2026-08-12**: the five non-duct CSVs in the round-5 package are
  **byte-identical** (`cmp`, 10 of 10 comparisons) to the round-3 and round-4
  copies — i.e. the exact bytes the audited pipeline produced are the exact
  bytes that would be sent.
- **The three new duct CSVs**: untrained QCR forward solves (`Ccr1 = 0.3`
  frozen before any solve at `0bade54a`; nothing fitted). The R5 record's claim
  that test truth was absent from the run trees was **re-verified by execution
  today**: `find … -name "*_LES*"` over
  `/home/ubuntu/certonomous-runs/w3-qcr-rank1/` returns LES truth files ONLY in
  the two `AR_7` validation arms (where they belong — AR_7 is the suggested
  validation duct, not a test case) and **zero** in the three test-duct arms.

**The honest thin spot, named rather than smoothed over.** The letter of the
rule — no training or validating on test-case data — is respected, and the
evidence above is executable, not testimonial. But §3b of the description
document admits, in the lab's own pre-registered words, that the round-5 duct
work was *targeted* because preview scores had shown the ducts were where the
entry was losing. Previewing is explicitly instructed by the README (step 2),
so this is not a rule violation — the same README that forbids training on test
data tells submitters to preview their score. It is, however, **a judgment the
steward gets to make with full information, and the package's defence is that
it hands the steward that information rather than hoping it goes unnoticed**.
The freeze (`R5_RULE_FREEZE.md` at `0bade54a`) closed every degree of freedom in
writing before any round-5 number existed, the AR_14 regression it caused was
accepted and not reverted, and the document says of its own defence: "We think
the freeze is a good answer. We do not think it is a complete one."

**What has NOT been verified and is stated as such:** no independent third party
has audited the compliance chain; the audit of 2026-07-30 is the lab reading its
own code, adversarially but internally. If a stronger warrant is wanted before
a first send, an external re-derivation of the five trained-case CSVs from the
committed train-only pipeline would be the check — it has not been done by
anyone outside the fleet, and this document does not claim otherwise.

## 7. The single biggest risk to a first send

Not format (verified clean), not eligibility (no clause anywhere restricts who
may enter), not the score (recorded through the benchmark's own unmodified
harness). **It is the steward's reading of the disclosed adaptive-selection
history under a rule whose written scope it does not violate** — §6's thin
spot. The penalty regime is binary and public: withdrawal plus a note. The
package's position is maximal disclosure before the fact; the residual risk is
that the steward weighs the round-2-preview-driven gate and the round-5 duct
targeting as against the spirit of the rule even though the letter is met and
the README itself instructs previewing. That judgment cannot be pre-empted from
documents — it is precisely the kind of question (§3, open items) that only the
steward can answer, and asking him is Katie's alone.
