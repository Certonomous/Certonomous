# External-referent audit — every load-bearing verification, classified by what it was checked against

Docket **B6**, opened and executed 2026-08-11 by session `64b13819`. The rule is
**L-74**:

> A check written with the same helpers as the thing it checks proves only
> transcription fidelity. Any load-bearing verification names its **EXTERNAL
> referent** — a published value, an exact theory, an independent
> implementation — or **declares that it has none.**

This document classifies. It does not repair. Nothing below was fixed as it was
found, because a sweep that repairs as it goes destroys its own baseline.

**The headline, stated before the method so it cannot hide behind it:** the
corpus is in **substantially better shape than L-74 implies**, and the largest
single result of this audit is a *negative* one — the lexical instrument I built
to find undeclared verifications was **wrong in the direction that flatters the
finding**, and I measured that rather than shipping it. The real defects are
few, specific, and named in §4 and §5. Two of them reach the camera.

---

## 1. Controls, reported first — both directions

A classifier calibrated on one side ships inverted. Both directions were run
before any population number was taken.

### 1.1 Positive control — a verification provable as EXTERNAL, classified EXTERNAL

**The claim.** `demo-output/website/dafoam/ladder-b/S1_WITH_PRIORS_PREREGISTRATION.md`
§1 re-verifies the CBFS inlet premise, reporting the benchmark's inlet as
**150 faces, Ux min→max 0.202035889 → 1.00537467, Ux mean 0.9149216132**.

**Why the referent is external, established by provenance and not by my reading:**

| check | executed | result |
| --- | --- | --- |
| Referent file is third-party | `git -C /home/ubuntu/closure-challenge-benchmark remote -v` | `github.com/rmcconke/closure-challenge-benchmark.git` |
| Authored outside the lab | `git log -1 --format='%an <%ae> %ad' -- data/CBFS/0/U` | `Ryley <rmcconke@uwaterloo.ca> Mon May 4 14:33:33 2026` |
| Not locally modified | `git status --porcelain data/CBFS/0/U` | clean |
| Value independently recomputed | my own parser, written for this audit, over `data/CBFS/0/U` | **150 faces, mean 0.9149216132, min 0.202035889, max 1.00537467** |

The last row matters: the recomputation used an implementation I wrote, not the
lab's, and it reproduced every digit. This referent is external **twice over** —
a file distributed by an outside party, read by an implementation outside the
lab's stack.

**Classifier verdict: EXTERNAL.** Correct.

### 1.2 Negative control — a verification provable as SELF-REFERENTIAL, classified SELF-REFERENTIAL

**The claim.** `demo-output/website/dafoam/ladder-b/S1_CBFS_REINVERSION_PREREGISTRATION.md:170`:

> *(varianceU cross-check: Σ/(3N) reproduces the printed objective to 13 digits)*

**Why it is self-referential, established mechanically rather than by taste.**
The divisor `3N` is not an independent fact brought to the comparison — it was
**fitted to the printed value in the first place**, in the sibling document
`S1_WITH_PRIORS_PREREGISTRATION.md:96`:

> Σ&#124;U−UData&#124;² = 961.1569839 over 21,000 cells; dividing by 3N = 63,000
> gives 1.525646e-02 against the recorded `varianceU` of 1.5256460061195715e-02.
> So DAFoam's `variance` DAFunction normalizes by **component count × cell count**

The convention was **inferred from** the printed number; the later cross-check
then re-applies that convention and recovers the printed number. **A check whose
parameter was solved for by requiring the check to pass cannot fail.** It is a
transcription-fidelity check, and a worthwhile one — it proves the parse is
reading the field the objective read. It is not evidence that the convention is
the right loss.

The record is honest about the shared implementation in its own words
(same line's sentence): *"Audit arithmetic identical to the failed run's
coverage audit"*.

**Classifier verdict: SELF-REFERENTIAL.** Correct, and caught via the record's
own disclosure.

**Both directions pass. The classifier is not inverted.**

---

## 2. How the population was derived — mechanically, with frames

Hand enumeration has failed twice in this repo. Nothing below is hand-picked.

**Frame, stated beside every count.** `git ls-files '*.md'` → **367 tracked
markdown files**, repo root, at commit `df4d4cbe`. Tracked-only: it reaches
tracked-but-gitignored files that `grep -r` here does not, and it does **not**
reach the run archives outside the repo at `/home/ubuntu/certonomous-runs/`
(L-75). Where a claim's referent lives outside the repo, I checked it directly
with `/usr/bin/grep` and `git` against those trees and said so.

**Unit.** The markdown **section** (heading-delimited), not the line. A
line-local first attempt reported 81.2% undeclared and was **discarded** — it
mis-framed the question, because a referent is named in the surrounding
paragraph, not on the verdict line. That first number appears nowhere in this
document's conclusions.

**Population rule.** A section qualifies as a verification if it carries either
(a) one of the Verification Charter's fixed verdict tokens — `PASS`,
`GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `VALIDATED`,
`SOLVER-BACKED`, `RESEARCH MODEL`, `UNCONVERGED` — **together with a number**,
or (b) a verification verb (`verified against`, `confirmed by`,
`validated against`, `cross-checked`, `checked against`, `reproduces`,
`graded against`, `compared against`, `re-measured`).

**Result: 1,549 verification sections across 297 of the 367 documents**, out of
4,844 sections total.

**Blast radius, also mechanical.** For each section, `travel` = the largest
number of distinct tracked documents that carry any of that section's
distinctive numeric literals (≥3 decimal places). A conclusion in 29 documents
outranks one in a working note.

**Why the charter made this derivable at all.** The lab already separates the
two axes, in `docs/charters/VERIFICATION_CHARTER.md` §2: *"A gate is a criterion
the lab sets… A reference is an external number the result is compared against.
A published experiment, a benchmark case, a correlation, an exact solution."*
L-74's question is, in the lab's own vocabulary, *"does the reference column
hold a reference?"* — and the charter's canonical gate-table shape carries a
`reference` column by construction.

---

## 3. The instrument's own error, measured — and why the raw screen number is not the headline

I built a lexical screen over the 1,549 sections: an EXTERNAL vocabulary
(citations, report numbers, URLs, named authors, exact-theory names, upstream
provenance idiom) and a SELF-REFERENTIAL vocabulary (`same parser`,
`identical arithmetic`, `our own …`, `its own tolerance`, `scored locally`).

**Screen output (frame: 367 tracked `*.md`, section unit, commit `df4d4cbe`):**

| bucket | sections | share |
| --- | ---: | ---: |
| EXTERNAL | 408 | 26.3% |
| SELF-REFERENTIAL | 83 | 5.4% |
| BOTH | 93 | 6.0% |
| **UNDECLARED (screen)** | **965** | **62.3%** |

**That 62.3% is not the finding, and publishing it as one would repeat the
defect this audit exists to catch.** I adjudicated a random sample of the
screen's UNDECLARED bucket by reading (n = 14, seed fixed). Of 14:

- **7 were not load-bearing verifications at all** — literature-reading notes,
  charter prose, recommendation lists, document preambles. The population rule
  over-collects.
- **3 carried a referent the screen missed.** The clearest:
  `demo-output/website/campaign/LADDER_V_PASS3_COLD_2026-08-11.md:86` declares
  *"Scorer: `closure_challenge.eval.evaluate_from_csv_by_case` at commit
  `1c4e22c8`, working tree clean, unmodified"* — a commit-pinned external
  provenance declaration, scored UNDECLARED by my screen.
- **4 were genuinely undeclared load-bearing verifications.**

Scaling 4/14 onto 965 gives roughly **280 truly-undeclared load-bearing
verifications, with a 95% interval of about 90–560** on n = 14. That interval is
wide and I am not going to narrow it by assertion; a larger adjudicated sample
is the named next step (§7).

**I stopped tuning the screen deliberately.** Each miss I found tempted another
vocabulary patch, and after three rounds the screen was being fitted to its own
calibration cases — which is L-74's failure mode wearing my badge. The screen is
frozen at the version reported above and is presented as **a lower bound on
EXTERNAL, not a measurement of UNDECLARED.**

**The reason the screen failed in this specific direction is itself the most
useful methodological finding here:** this lab declares provenance in a rich,
varied, *non-formulaic* idiom — *"the benchmark's own unmodified scorer"*,
*"at eval package commit `1c4e22c8`"*, *"our figure, not one the benchmark
publishes"*, *"a local scoring, not an official placement"*, *"(own run)"*,
*"fetched live 2026-07-28, on disk"*. No keyword list anticipates that, and its
existence is evidence of a corpus that mostly does the right thing in prose
rather than in a field.

---

## 4. The UNDECLARED bucket, ranked by blast radius

Adjudicated by reading, highest travel first. These are the places a reader
forms a false belief.

### 4.1 RANK 1 — the cylinder Strouhal gate: an external name over an unattributed constant

**Travel: 6 documents, and it is act 1 on the camera surface.**

`demo-output/website/campaign/NINE_ACT_GATE_TABLE.md:3` grades act 1 as:

> | Cylinder vortex shedding, Re 100 | Strouhal vs Roshko-Williamson correlation | 0.1590 | 0.1578 | 0.77% | PASS |

The reference column names **Roshko and Williamson** — two real, citable
authors. The number 0.1590 comes from `sdk/workflows/_exact_theory.py:253-260`:

```
def roshko_strouhal(reynolds: float) -> float:
    """St = 0.198 (1 - 19.7/Re), the Roshko/Williamson subcritical, laminar,
    periodic vortex-shedding correlation, the exact form this lab's Re=100-180
    cylinder family already gated against (mega-batch Family 1)."""
    return 0.198 * (1 - 19.7 / reynolds)
```

**The stated warrant for the constants is internal**: *"the exact form this
lab's Re=100-180 cylinder family already gated against"*.
`demo-output/website/campaign/F5a_cylinder_reynolds_ladder.md:73-75` attributes
it further inward — *"(the exact form given in this task's gate)"*, i.e. to the
task prompt.

**And the repo's own citation gives a different formula.**
`sdk/workflows/cylinder_vortex_shedding.py:22-24` cites Roshko (1954), NACA
Report 1191, as `St ~ 0.212(1 - 21.2/Re)`. Executed arithmetic at Re = 100:

| form | source in repo | St at Re=100 | deviation of the measured 0.1578 |
| --- | --- | ---: | ---: |
| `0.198(1 − 19.7/Re)` | used by the gate; **no paper cited** | 0.158994 | **0.75% → PASS** |
| `0.212(1 − 21.2/Re)` | cited to NACA Report 1191 | 0.167056 | **5.54%** |

**Classification: UNDECLARED, and it reads as EXTERNAL.** The gate's referent is
named after published authors while its actual constants are traceable, in the
repo's own words, to a prior lab gate and a task prompt. Both forms are quoted
in the cylinder literature for *different* Reynolds ranges, so which one governs
Re = 100 is a question for the source document, not for me — that is filed
(§8, D-B6-1), not ruled on here. What is settled by executed arithmetic is that
**the repo contains two mutually inconsistent versions of its own cited
reference, and the gate passes against the unattributed one.**

### 4.2 RANK 2 — the Ahmed body reference value has a paper but no extraction record

**Travel: 5 documents, including the camera surface.**

`models/curriculum/ahmed_25/reference.yaml:4` holds `cd: 0.285` with
`source: "Ahmed, Ramm & Faltin 1984, SAE 840300"` — a uniquely identified, real
published work. **But no record anywhere states which table, figure or page
0.285 was taken from, or how.** `git log --follow` on that file returns a single
commit, `5336dd57`, the initial import.

The reason this is ranked rather than waved through is a **sibling file from the
same commit**: `models/curriculum/naca4412_wing/reference.yaml:29-31` records
that its own previous value *"was a hand-set estimate entered directly in this
file with no computation and no supporting script behind it (see git history,
commit 5336dd5)"*. One file in that batch was caught being a hand-set estimate
wearing a citation. `ahmed_25` received no equivalent provenance note either
way.

**Classification: UNDECLARED as to extraction.** The paper is external and
resolvable; the *number's* route from paper to file is not recorded. Note the
lab's own downstream record already treats the yaml as the origin —
`W3_AHMED_PREREGISTRATION.md:32-40` calls it the *"single source of truth"*.

### 4.3 RANK 3 — the closure-score cluster: undeclared in the satellites, declared in the canon

**Travel: 29 documents — the widest-travelling number in the corpus.**

The screen flagged 21 sections carrying `0.0654` / `0.056647` / `0.0455` as
UNDECLARED. **On adjudication this is largely a false alarm, and the correction
is worth recording as loudly as a defect would be.** The canonical documents
declare the referent thoroughly and with commit pins:

- `demo-output/website/CLOSURE_CHALLENGE_STATUS.md:525-531` — *"scored locally
  … through the benchmark's own unmodified scorer … This is a **local scoring,
  not an official leaderboard placement** — nothing has been submitted, and if
  the steward's own scoring differs from ours, the steward's number is the
  number."*
- `closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md:264-272` — the
  0.1036 floor declared as *"our figure, not one the benchmark publishes"*.
- `closure_challenge_submission_round5/README.md:24-44` — a from-scratch
  re-derivation recipe for a recipient, under *"Nothing below requires anything
  from the submitting lab's repository"*.

Verified independently: both external repos are **clean and unmodified** —
`closure-challenge-pkg` at `1c4e22c8` (tag `v0.3.1`,
`github.com/rmcconke/closure-challenge.git`) with an empty `git status
--porcelain`, and `closure-challenge-benchmark` at `deb91557` clean but for one
untracked lab-authored *non-scorer* script. **No lab copy or reimplementation of
the scorer exists** (`find . -name 'eval.py'` → nothing).

**The residual, and it is real:** the declaration does **not travel with the
number**. A reader meeting `0.056647` in a `LADDER_V` pass table, in
`ACTIVE_RESEARCH.md`'s body, or in `PRODUCT_LIST.md` gets the figure without the
"local scoring, not an official placement" clause that the canonical documents
attach to it. The chief has already ruled the *rank-1* companion clauses
mandatory on every surface (`ACTIVE_RESEARCH.md`, update 2026-08-10). **The
referent declaration has no equivalent travelling rule.**

**Classification: EXTERNAL in fact and in the canon; UNDECLARED at the
restatement sites.**

---

## 5. SELF-REFERENTIAL read as EXTERNAL — the bucket L-74 was written about

### 5.1 The CRM wing-body `VALIDATED` chip is a code-to-code reproduction, and the camera surface does not say so

**Travel: 5 documents. Filmed.**

`NINE_ACT_GATE_TABLE.md:11` grades:

> | CRM wing-body | Drag vs DAFoam CRM_Wing tutorial, Cd 0.02090 +/-2% | 0.0209 | 0.020901 | +0.007% | VALIDATED |

The referent is **another CFD code's own documentation** — not a physical
experiment. `sdk/workflows/crm_wingbody.py:43-47` sets
`GATE_SOURCE = "the DAFoam project's own published CRM wing tutorial
documentation"`, `PUBLISHED_CD = 0.02090`.

**The ladder record handles this exactly right.**
`demo-output/website/dafoam/ladder-a/A6_crm_wingbody.md:154-159` states the
code-to-code nature and refuses the tempting experimental comparison:

> **This is essentially an exact reproduction of the tutorial's own stated
> result** … It is **not** evidence about DPW-VI wing-body drag-prediction
> accuracy — no such claim is made.

and at `:131-136` declines the AIAA DPW-VI scatter band as *"exactly the kind of
invented/mismatched comparison this task forbids."* That is model behaviour.

**The defect is downstream of it.** `FILMING_COMMANDS.md:108-117` restates the
nine expected results as a flat list:

```
6. Cd 0.3041 vs 0.285 published, 6.7%, tier SOLVER-BACKED
7. Separation 0.6544 vs 0.665 (-1.6%), reattachment 1.2534 vs 1.100 (+13.9%), tier VALIDATED
8. Cd 0.020901 vs 0.02090, +0.007%, tier VALIDATED
```

Rows 6 and 7 are experimental referents. **Row 8 drops "DAFoam tutorial"
entirely** and sits in the same list, same format, same `VALIDATED` chip — so
the tightest number on the page (`+0.007%`) reads as the lab's best agreement
with a published *measurement*, when it is agreement with another solver's
documented output. Row 1 loses "Roshko-Williamson"; row 7 loses "NASA".

**Classification: SELF-REFERENTIAL-CLASS (code-to-code) READ AS EXTERNAL, at the
highest-consequence surface in the repo.** The `A6` record declares it; the act
code, the transcript, the gate table and the filming list do not.

Two documents restate the gate table verbatim and **do** preserve the wording
`Drag vs DAFoam CRM_Wing tutorial` — `campaign/reports/MORNING_REPORT_2026-08-04.md:70-73`
and `MORNING_REPORT_2026-08-07.md:72-75` — as does `docs/PRODUCT_LIST.md:191`.
The loss is specific to the hand-written filming list.

### 5.2 The finite-difference gradient checks share a primal solver with the thing they check

Across the DAFoam ladder, adjoint gradients are graded against finite-difference
gradients — e.g. `demo-output/website/dafoam/DEFECT_REACH_decomposition_cases.md:283`
tabulates `analytic (simple 3x1x1, new)` against `FD (own run)`.

An FD gradient and an adjoint gradient computed by the **same solver on the same
primal** agree wherever the primal is wrong together. This is the L-74 shape
precisely: two components of one system agreeing, with no third party. It is
still a strong check — it discriminates against adjoint-assembly and
linearisation errors, which is what it is used for — but it is **not**
independent of the primal.

The records label the FD arm honestly as `(own run)`. **What is not stated
anywhere I found is the shared-primal limitation itself.**

**Classification: SELF-REFERENTIAL, partially declared** (the arm is named as
the lab's own; the shared dependency is not characterised).

---

## 6. EXTERNAL — the count, and the examples worth copying

**408 sections screen as EXTERNAL with no self-referential marker, plus 93
carrying both** (frame: 367 tracked `*.md`, section unit, commit `df4d4cbe`).
Because §3 established the screen **under**-detects external declarations, treat
408 as a floor.

Several are better than the rule requires and should be the templates:

**`demo-output/website/campaign/F3_runs/exact_theory.py:253-296` — the best
verification in the repo.** It validates the lab's oblique-shock relations to
6 significant figures against NASA GRC's published wedge validation page (URL
cited, five numbers quoted), then finds the *reference itself* internally
inconsistent for the cone case — the page's "Theory" row violates
stagnation-temperature conservation — and re-anchors onto the same page's
grid-converged multi-code CFD table instead, saying so. **It detects an erratum
in its own external referent using an independent physical invariant.** That is
the standard L-74's repair example set.

**`demo-output/website/dafoam/f6a_nasa_hump/F6a_nasa_hump.md:103-112`** — the
NASA hump referent: live URL, the quoted sentence the numbers came from, the
fetch date, the site's relocation noted, and the `.dat` files on disk and
tracked. *"fetched directly, not recalled from memory."*

**`demo-output/website/campaign/F12_runs/reference/decode_tape.py:21-25`** —
declares the provenance *chain*: *"This is therefore a DIGITISED TRANSCRIPTION
of AGARD AR-138, not the AR-138 document itself, made by the original
experiment's AGARD evaluator."*

**`demo-output/website/campaign/LADDER_V_PASS3_COLD_2026-08-11.md:127-131`** —
a genuine external calibration of an instrument: all four accepted leaderboard
submissions re-scored on the lab's harness reproduce their **published**
four-decimal values, 4/4. That is a positive control against numbers the lab did
not produce.

### The `ONERA M6` row — a verification that correctly declares it has none

`NINE_ACT_GATE_TABLE.md:10` grades M6 as `UNCONVERGED`, reference *"Primal
residual vs its own tolerance (intended gate, Cp at 7 spanwise stations vs AGARD
AR-138, NOT evaluated)"*. `scripts/gate_table.py:224-226` builds that string
programmatically.

The row's referent **is** the thing being checked, checking itself — and the row
**says so**, names the external gate that was not reached, and refuses to
substitute the nearer gate it did manage to compute. **This is L-74's "or
declares that it has none" clause, already implemented, in the highest-visibility
table in the repo.** It is the single best piece of evidence that this lab does
not need L-74 explained to it.

---

## 7. My own audit's referent — stated honestly

**This audit is itself a load-bearing verification, and the rule covers it.**

**For the two controls (§1), my referent is EXTERNAL and I can name it:** third-party
git provenance (`remote -v`, `log --author`, `status --porcelain` on two repos I
do not control) and a recomputation of `0.9149216132` with a parser I wrote for
this audit. Those are checkable facts about the world, not readings.

**For the population and the bucket sizes (§2, §3, §6), my referent is my own
lexical screen — an instrument I wrote, measured, and found wanting.** Its error
rate is reported (§3) from an adjudicated sample rather than assumed. It is
**SELF-REFERENTIAL with a measured error rate**, and I have not claimed
otherwise: that is why §3 refuses to promote 62.3% to a headline.

**For the classifications in §4 and §5, my referent is my reading of the
record**, supported where possible by executed checks — the Strouhal arithmetic
in §4.1 was run, the closure repos' cleanliness in §4.3 was run, the CRM
tutorial's absence of `0.02090` was searched for and not found. **Where I only
read and judged, that is SELF-REFERENTIAL and I am declaring it here rather than
dressing it as an instrument.**

**R-DEPTH.** This document is an instrument checking instruments checking
claims — depth 2, the cap. **I have not audited my own auditor**, and the
obvious next move (a second classifier to grade this one) is filed as out of
scope rather than executed.

---

## 8. What I did not reach — the named frontier

An honest partial with a stated frontier beats a thin complete sweep. Not
reached:

1. **The remaining ~950 screened-UNDECLARED sections below travel-rank ~26.**
   I adjudicated 14 at random plus the top of the blast-radius ranking. The
   `travel = 0` tail (560 sections — numbers appearing in one document only) is
   almost entirely working notes and is the lowest-value region, but it is
   **unadjudicated, not cleared**.
2. **Non-markdown records.** The population is tracked `*.md`. Verification
   claims also live in `*.json` act records, transcripts under `mission-output/`,
   and Python docstrings. The SDK's `source` keys were enumerated (182 across
   tracked `*.py` excluding `dist/`, of which ~150 are unrelated OpenFOAM
   `topoSet` sources) but the JSON surfaces were not swept.
3. **`/home/ubuntu/certonomous-runs/`** — the out-of-repo run archives. Checked
   for the specific claims in §1 and §4.3; not swept as a population.
4. **The `V16` grading line and `scripts/self_audit.py`** — a peer agent is live
   in a worktree on those. Untouched by instruction.
5. **Whether `0.198(1−19.7/Re)` or `0.212(1−21.2/Re)` is the correct Roshko form
   at Re = 100.** Settling it needs NACA Report 1191 itself. Filed, not ruled.

---

## 9. Filed to the docket, section D (R-CONVERGE — real, outside this scope)

- **D-B6-1.** The cylinder Strouhal correlation exists in the repo in two
  mutually inconsistent forms (`0.198(1−19.7/Re)` used by the gate;
  `0.212(1−21.2/Re)` cited to NACA Report 1191), differing by 5.1% at Re = 100.
  The gate passes against the unattributed form. Resolving which form the source
  document supports at this Reynolds number is a literature task, not a
  classification task.
- **D-B6-2.** `sdk/workflows/mega_batch.py:366` duplicates the Strouhal
  correlation inline (`0.198 * (1.0 - 19.7 / reynolds)`) despite
  `cylinder_vortex_shedding.py:58-62` stating the correlation is *"deliberately
  not duplicated here: two copies of one correlation is how a gate silently
  drifts"*. Two copies now exist.
- **D-B6-3.** No provenance note records how `cd: 0.285` was extracted from SAE
  840300 into `models/curriculum/ahmed_25/reference.yaml`, while a sibling file
  from the same import commit was found to have carried a hand-set estimate.
- **D-B6-4.** The closure entry's referent declaration ("local scoring, not an
  official placement", "the benchmark's own unmodified scorer at `1c4e22c8`")
  does not travel with the number to restatement sites, though the chief has
  already made the *rank-1* companion clauses mandatory on every surface. A
  parallel travelling rule for the referent does not exist.
- **D-B6-5.** The lab's provenance-declaration idiom is rich and non-formulaic,
  which is why no keyword screen classifies this corpus reliably (§3). If
  referent declaration is ever to be machine-checkable, it needs a *field*, not
  prose — e.g. the Verification Charter §2 gate table's `reference` column made
  mandatory. Only **12 tables** in the whole tracked markdown corpus currently
  carry a `reference` column header (frame: `git ls-files '*.md'`, 367 files).

---

## 10. The verdict, plainly

**L-74 describes a real failure mode and this corpus mostly does not exhibit
it.** The lab separates gates from references in its charter, implements the
"declares it has none" clause in its most visible table, cites URLs with fetch
dates, pins external scorers to commit hashes, refuses mismatched comparisons by
name, and has at least one verification that caught an erratum *in its own
external reference*.

The defects that remain are **not** a culture of self-referential checking. They
are **transmission losses**: a correctly-declared referent in a ladder record
that is dropped when the number is restated on a filming list (§5.1), a
correctly-declared local scoring that travels without its clause (§4.3), and one
gate whose external name outran its attributed constants (§4.1).

**Two of these reach the camera.** That is where the value of this audit is, and
it is a much smaller and more actionable finding than the 62.3% my own
instrument first offered me.
