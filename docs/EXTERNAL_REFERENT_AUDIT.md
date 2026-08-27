# External-referent audit — every load-bearing verification, classified by what it was checked against

Docket **B6**, opened and executed 2026-08-11 by session `64b13819`. The rule is
**L-74**:

> A check written with the same helpers as the thing it checks proves only
> transcription fidelity. Any load-bearing verification names its **EXTERNAL
> referent** — a published value, an exact theory, an independent
> implementation — or **declares that it has none.**

This document classifies. It does not repair. Nothing below was fixed as it was
found, because a sweep that repairs as it goes destroys its own baseline.

**The headline, stated before the method so it cannot hide behind it.** Three
things, in order of how much they should change anyone's behaviour:

1. **The corpus is in substantially better shape than L-74 implies.** Every
   clean instance of L-74's failure mode I found in the gradient work had
   **already been found and retracted by this lab** before B6 was opened (§5.3).
   The lab's charter separates gates from references, and its most visible gate
   table already implements the "declares it has none" clause (§6).
2. **The real defect class is not self-referential checking — it is
   transmission loss.** Of the **seven** live findings, **four** have a correct
   referent declaration somewhere in the repo that **does not travel with the
   number** to where a reader meets it, and a fifth arguably does (§10). Two of
   the seven reach the camera. Only two — §4.1 and §4.2 — are genuine gaps
   where no correct declaration exists anywhere.
3. **My own instrument was wrong in the direction that flatters the finding.**
   A lexical screen reported 62.3% UNDECLARED; adjudication showed most of that
   bucket is either not a verification or a declaration the screen could not
   see (§3). **That number is reported as an artifact and not promoted**, and
   the screen was frozen rather than tuned further — tuning a classifier against
   its own calibration cases is L-74 wearing the auditor's badge.

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
parameter was solved for by requiring the check to pass cannot fail** — and the
fitting step is quoted above from the sibling document, not inferred by me.

It is a transcription-fidelity check, and a worthwhile one: it proves the parse
is reading the field the objective read. It is not evidence that the convention
is the right loss.

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

**The lab has already caught one of these, in the same file family.**
`demo-output/website/campaign/NOT_PASSING_REGISTER.md`, Group 4, on the
NACA0012 wing:

> **The reference is also unbuilt.** `cd: 0.009` in
> `models/curriculum/naca0012_wing/reference.yaml` was hand-set in the initial
> commit and has never been touched; `tolerance: 0.30` is hand-picked prose
> ("band is generous"); `confidence: medium`.

Three files in `models/curriculum/*/reference.yaml` from commit `5336dd57`;
**two are now known to carry hand-set numbers.** `ahmed_25` is the third, and carries no provenance note either way
(executed: `git log --follow` returns the single import commit `5336dd57`;
`/usr/bin/grep -iE "table|figure|page|extracted|digitis|hand-set"` over that
file returns no provenance line). That is why this is ranked rather than waved
through — not because the citation is suspect, but because the population it
came from has a measured base rate.

### 4.4 RANK 4 — F6b Gate V: "reproduces the known answer" loses its distributor in transit

**Travel: 12+ tracked documents.**

`demo-output/website/campaign/F6b_ERCOFTAC_RESULTS.md:12-18` grades
*"Gate V (verification of our own pipeline): PASS"* at **0.043%** against
*"the benchmark's shipped-mesh value of **7.6439**"*.

Two things are true and neither is stated in the file that carries the verdict:

1. **The referent is the benchmark's own RANS baseline field**, not the
   ERCOFTAC/Breuer LES and not the Rapp & Manhart experiment — those supply
   Gate **P**, which FAILs. Gate V compares the lab's k-ω SST against a
   third-party k-ω SST.
2. **The distributor is not named in that file** (executed:
   `/usr/bin/grep -cE "McConkey|rmcconke|closure-challenge-benchmark"` over
   `F6b_ERCOFTAC_RESULTS.md` returns **0**). The
   provenance lives one document back, in
   `demo-output/website/dafoam/f6b_periodic_hills/F6b_periodic_hills.md:33-34`.

The restatements then compress it further:

- `CHALLENGE_SLATE_2026-08.md:29` — *"verification PASS (0.043% vs shipped grid)"*
- `CASES_FAMILY_SUPERVISION_GUIDELINES.md:24` — *"(our pipeline reproduces the
  known answer on our own mesh: PASS at 0.043%)"*
- `SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md:10` — *"Verified on our own
  mesh (0.043% agreement with the shipped grid), so the failure is the model's,
  not ours."*

**"The known answer" is another RANS code's answer.** The gate is a legitimate
and well-chosen pipeline verification — and the header
*"Gate V (verification of our own pipeline)"* says so. **Classification:
EXTERNAL-BENCHMARK-DISTRIBUTION at the source, UNDECLARED as to distributor,
and the travelling phrasing invites a stronger reading than the gate supports.**

### 4.5 RANK 5 — the Ahmed ±15% band reads as the reference's own scatter

`demo-output/website/mega-batch/F10_3D_VISCOUS_FAMILY.md` grades the 25° row
*"inside band — VALIDATED"* against *"the citable reference — Ahmed, Ramm &
Faltin 1984, SAE 840300, Cd 0.285 ± 15%"*.

**The ±15% is the lab's own `tolerance: 0.15` from
`models/curriculum/ahmed_25/reference.yaml`, not scatter reported by the 1984
paper.** The same yaml separately carries `cd_range: [0.27, 0.30]`, and the
graded value **0.32284 is inside the lab's ±15% and outside the reference
file's own `cd_range`.**

Written as *"the citable reference … Cd 0.285 ± 15%"*, the band reads as though
it arrived with the citation. **Classification: UNDECLARED** — the value is
external, the band is a lab gate, and the sentence does not separate them. (The
same document declares its *other* gates' provenance carefully, including
`"reused rather than invented"` and `"not a separately invented number"` — so
this is an isolated slip, not a pattern.)

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

The records label the FD arm honestly as `(own run)`. The shared-primal
limitation is **named in four places and absent in the original gates**:

- `PROOF.md:917-940` names it decisively, and it is the move that refutes a
  hypothesis: *"FD and the adjoint are, provably, differentiating the **exact
  same** frozen-`yWall` discrete function throughout this entire
  investigation"*, so the omitted term *"cannot be 'the right size and sign to
  close the gaps,' **because the two quantities being compared (Jan and Jfd)
  already, identically, both exclude it.**"*
- `W5_GRADIENT_REGRADE.md:622-624` names it as the reason a control was invalid
  (§5.3 below).
- `VERIFICATION_A4_mechanism_supervisor_sweep.md:121-126` turns it into a
  *positive* argument: *"the FD column is computed per run inside each arm's own
  `check_totals` … An adjoint that were the exact adjoint of an equivalent
  parallel discretization would match its own FD. It does not."*
- **Not named** in the original A1 gate (`PROOF.md` §8/§8.2), the original A5
  gate, the A2 rows, the sail rows, or in `DAFOAM_CASE_STATUS.md`'s per-case
  summaries — where the FD is treated as "the true derivative".

**Classification: SELF-REFERENTIAL, declared late rather than at the gate.** The
understanding exists in this lab and is sharp; it reached the diagnostic
documents and not the verdict lines.

### 5.3 The lab has already found L-74's exact failure mode in its own gradient work — and it is the best evidence in this audit

This is not a defect I found. **It is a defect the lab found, wrote up, and
propagated a retraction for**, and it is L-74's shape so precisely that it
deserves to be read beside the lesson.

**The circular acceptance band.** Ladder A2's gradients were graded against a
1–12% band. That band came from the lab's own A1 measurement.
`W5_GRADIENT_REGRADE.md:195-196` and `:478-480`:

> **A1's 1.67% is the calibration A2 was graded against, and it has now been
> measured to be almost entirely the defect.**

> the "1–12% normal band for this problem class" that `A2_mach_tutorial_wing.md:44`
> was graded against **was not a property of the problem class at all.** It was
> one upstream bug, measured four times.

**A tolerance calibrated from the lab's own runs, applied to grade the lab's own
runs, encoded an upstream defect as the definition of "normal" — and every
subsequent gate that passed inside it agreed with the bug.** That is L-74's
"two implementations that share a defect agree perfectly", with a *band* in the
role of the second implementation.

**The invalid invariance control.** `W5_GRADIENT_REGRADE.md:622-631` retracts a
control on the same grounds:

> **SUPERSEDED 2026-08-02 — it *is* the FD, and "unchanged between the runs" was
> the wrong test.** The FD cannot change between the runs: the primal never sees
> a `warpDeriv` patch. What was never done was re-measuring it.

A control that **could not have failed** was read as evidence that the FD was
sound. The record keeps the wrong text in place — *"The paragraphs above … are
kept as written and are wrong"* — and leaves the residual discrepancy open.

**The random-seed clearance.** `A5_ubend_internal.md:978-990` overturns two
earlier clearances of `warpDeriv` because *"every `mesh.warpDeriv` test ever run
on A5 … seeded the dot-product identity with an ARBITRARY RANDOM vector"*, and
`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md:323-329` generalises it:

> **a random-seed dot-product test of `warpDeriv` does not clear it.** It
> measures whether the error is large in a generic direction. What determines
> whether the error reaches a real gradient is whether the error's location
> overlaps the objective's own `dF/dXv` sensitivity field.

The repair was to capture *"the literal vector the framework passes"* — i.e. to
replace a referent the lab chose with one the system supplies. And
`ROOTCAUSE_getRotationMatrix3d.md:207-209` notes the same trap **in upstream's
own verification tool**: `verifyWarpDeriv(..., randomSeed=314)`.

**The claimed referent that does not contain the numbers.**
`VERIFICATION_A4_mechanism_supervisor_sweep.md:22-27` — *"the record cites
`d_crossres.log` for numbers that log visibly contradicts"*, the tabulated
values being offline sign-corrected recomputations. And `:73-79`, a use of an
instrument the lab had already discredited: *"**That is the discredited
instrument, used without saying so.** … The confound stays closed; **the record
should have flagged the instrument.**"*

**Classification: four SELF-REFERENTIAL-READ-AS-EXTERNAL instances, all four
already found and retracted by the lab, before this audit existed.**

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

**`ROOTCAUSE_getRotationMatrix3d.md` / `UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` —
the L-74 gold standard, met and exceeded.** L-74's own repair example was a rule
*"read out of OpenFOAM's own source and cited to file and line."* This pair does
exactly that, at length, for IDWarp: the guard at `src/utils/vectorUtils.f90:44`
and `:58` quoted verbatim **including upstream's own explanatory comment**, the
Tapenade reverse at `src/adjoint/outputReverse/vectorUtils_b.f90:123-128` quoted
as generated Fortran, plus `kd_tree.F90`, `getElementProps_b.f90`,
`tests/test_USMesh.py:86`, `UnstructuredMesh.py:460` and the Tapenade makefile.
Three further properties put it above the bar:

- **The source is version-pinned by hash** — *"md5-identical to the `v2.6.2`
  tag … tag commit `647fd8fc2c06fc61b31cc07a7b63ffd4fbaf65ce`"*, with the
  container digest recorded.
- **The re-verification deliberately used none of the lab's tooling** —
  *"no Fortran driver, no IDWarp build, no DAFoam. Every source citation was
  read back out of the `v2.6.2` tag; the corrected derivative was re-derived and
  tested in an independent transcription."*
- **The referent is a five-year-old open upstream bug report** —
  `github.com/mdolab/idwarp/issues/57`, reproduced end-to-end on *"IDWarp's own
  test mesh, IDWarp's own options, IDWarp's own displacement, checked by
  IDWarp's own `verifyWarpDeriv`"*, with the residual 216%→210% discrepancy
  against the issue's pasted output stated rather than smoothed.

And `ROOTCAUSE_getRotationMatrix3d.md:636-643` states the claim **against
itself**: at the exact evaluation point the AD is the correct derivative of the
code as written, and an FD taken inside the ~1.5e-08 rad flat spot agrees with
it to every digit — so the whole finding depends on the FD step lying outside
that ball, and *"any filing should pre-empt the response"*.

**`F9_pulsatile_valve.md` §9.7 — the best "declares it has none" sentence in the
corpus:**

> So: **F9 is verified in part and validated against nothing.** Every gate in §3
> to §6b is verification or internal consistency. That is a respectable position
> for a screening replacement and it is not the same sentence as "a real, gated
> family", and the record should not let a reader slide between them.

§9.7 also tabulates three candidate external references and why each is
unusable, and marks the two textbook referents used without citation as
*"not as validation references"*.

**`F11_lid_driven_cavity_ladder.md:306-321` — the referent typed correctly
against the lab's own interest.** Ghia, Ghia & Shin (1982) is cited to DOI and
table, its open-access status checked *"before choosing this case (not after)"*
(`is_oa: false`), the values taken from **two independently hosted secondary
transcriptions cross-checked against each other** rather than the primary PDF —
and then, in a section headed *"this is VERIFICATION, not VALIDATION"*:

> Ghia, Ghia & Shin (1982) is **itself a numerical solution** … **This gate is
> therefore a code-to-code VERIFICATION** … and not a physical VALIDATION.

That is exactly the declaration §5.1's CRM row is missing.

**`B2_duct_baseline.md:38-47`** — reproduction against *"the paper authors' own
case files"*, run on a **different OpenFOAM lineage** (ESI v2606 vs the
authors' OpenFOAM-7): *"we are not inferring a baseline setup from a paper's
text, we are re-running the authors' own case files on our own solver."* The
scorer self-check beside it is declared as a self-check, and the absence of a
paper-side figure is declared: *"stated plainly rather than invented."*

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

**For the classifications in §4, §5 and §6, my referent is my reading of the
record**, supported where possible by executed checks — the Strouhal arithmetic
in §4.1 was run, the closure repos' cleanliness in §4.3 was run, the CRM
tutorial's absence of `0.02090` was searched for and not found. **Where I only
read and judged, that is SELF-REFERENTIAL and I am declaring it here rather than
dressing it as an instrument.**

**Disclosure on how the evidence was gathered.** Four subagents collected quoted
evidence in parallel — the nine acts, the closure challenge, the DAFoam ladder,
the campaign F-series — each instructed to quote verbatim with file and line and
**not to classify**. Every classification in this document is mine. The quotes
were spot-checked, not re-derived wholesale: I independently re-executed the
Strouhal arithmetic, the two closure repos' provenance, and the benchmark `0/U`
recomputation, and I read the nine-act table, the charter, `PASS3_COLD` §1.3-1.4
and both S1 control sections directly. **The remaining quotations are relayed,
and a relayed quotation is a weaker referent than one I read.** Anything in §4
or §5 that would drive a repair should be re-read at source first.

**One structural limit of a four-agent fan-out, named because it is this
audit's own version of the defect it hunts:** four readers each looking at their
own slice will not see a referent named in *another* slice's document unless
their territories happen to overlap.
§4.4 is exactly that shape — the F6b distributor is named one document away from
the verdict — and I caught it only because two agents' territories overlapped
there. **A cross-document referent-resolution pass was not run.** See §8.

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
6. **A cross-document referent-resolution pass.** My screen is section-local and
   my agents were slice-local. Neither can tell "no referent named" from
   "referent named in the document next door" — which is precisely the §4.3 and
   §4.4 pattern. **This is the single highest-value follow-on**, and it is
   cheap: resolve each verification's numbers to every document carrying them,
   and ask whether *any* of them names the referent. Zero compute.
7. **The F7 dam-break digitisation.** `F7_marine_free_surface.md` grades against
   Martin & Moyce (1952) *"digitised twice independently from Fig. 7 of
   arXiv:2108.08769"* — the primary is not open-access, so the referent is a
   lab pixel-reading of a third party's figure, cross-checked **only against the
   lab's own second digitisation**. The record declares the route and its
   uncertainty. Whether a self-cross-checked digitisation counts as external is
   a real question I did not settle.
8. **`sdk/tests/` — 1,000+ assertions.** A test asserting the behaviour of lab
   code is self-referential by construction and legitimately so. I did not
   classify them and do not think a bare count would mean anything; the
   interesting subset is tests that assert a *physical* or *published* value,
   and that subset was not extracted.

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
- **D-B6-5.** `models/curriculum/*/reference.yaml`: of three reference files
  from commit `5336dd57`, **two are now known to carry hand-set numbers**
  (`naca4412_wing`, recorded in the file itself; `naca0012_wing`, recorded in
  `NOT_PASSING_REGISTER.md` Group 4). `ahmed_25`'s `cd: 0.285` carries no
  provenance note either way (`git log --follow` → one import commit), and it is the reference behind a filmed act.
- **D-B6-6.** `F10_3D_VISCOUS_FAMILY.md` writes the Ahmed gate as *"the citable
  reference — Ahmed, Ramm & Faltin 1984, SAE 840300, Cd 0.285 ± 15%"*. The
  ±15% is the lab's own `tolerance: 0.15`, not the paper's scatter, and the
  graded 0.32284 sits outside the same yaml's own `cd_range: [0.27, 0.30]`.
- **D-B6-7.** The FD-vs-adjoint shared-primal limitation is stated sharply in
  four DAFoam diagnostic documents (`PROOF.md` §12,
  `W5_GRADIENT_REGRADE.md:622`, `VERIFICATION_A4:121`) and **absent from the
  gate lines themselves** (`PROOF.md` §8/§8.2, the A5 FD-verification section,
  `DAFOAM_CASE_STATUS.md`'s per-case summaries), where the FD is called "the
  true derivative".
- **D-B6-8.** The lab's provenance-declaration idiom is rich and non-formulaic,
  which is why no keyword screen classifies this corpus reliably (§3). If
  referent declaration is ever to be machine-checkable, it needs a *field*, not
  prose — e.g. the Verification Charter §2 gate table's `reference` column made
  mandatory. Only **12 tables** in the whole tracked markdown corpus currently
  carry a `reference` column header (frame: `git ls-files '*.md'`, 367 files).

---

## 10. The verdict, plainly

**L-74 describes a real failure mode and this corpus mostly does not exhibit
it.** The lab separates gates from references in its own charter, implements the
"declares it has none" clause in its most visible table (§6, ONERA M6) and in
its plainest sentence (*"F9 is verified in part and validated against
nothing"*), cites URLs with fetch dates and open-access status checked *before*
case selection, pins external scorers and upstream source to commit hashes,
re-verifies an upstream bug using none of its own tooling, refuses mismatched
comparisons by name, distinguishes code-to-code verification from physical
validation in so many words, and has a verification that **caught an erratum in
its own external reference** using an independent physical invariant.

**The strongest evidence is §5.3, and it is not mine.** Every clean instance of
L-74's failure mode I found in the gradient work — a tolerance band calibrated
from the lab's own defective run and then used to grade against it, a control
that could not have failed, a random-seed test that could not discriminate, a
cited log that does not contain the numbers — **had already been found,
retracted and propagated by this lab before B6 was opened.** A corpus that
detects this class unaided does not have a culture problem with it.

What remains is **not** self-referential checking. It is **transmission loss**:

| where | the referent is | what the reader meets |
| --- | --- | --- |
| §4.1 cylinder St | an unattributed constant | "Roshko-Williamson correlation" |
| §5.1 CRM `VALIDATED` | another solver's tutorial docs | a bare `Cd 0.020901 vs 0.02090` beside two experimental rows |
| §4.3 closure score | the organisers' unmodified scorer, declared in the canon | the number, without its clause |
| §4.4 F6b Gate V | a third-party RANS baseline | "reproduces the known answer" |
| §4.5 Ahmed band | the lab's own `tolerance: 0.15` | "SAE 840300, Cd 0.285 ± 15%" |
| §5.2 FD gates | an FD sharing the adjoint's primal | "the true derivative" |
| §4.2 Ahmed 0.285 | SAE 840300, extraction route unrecorded | a citation that reads as fully sourced |

**In four of these seven a correct declaration exists elsewhere in the repo and
does not travel with the number; §4.5 arguably makes five, since the band is
recorded as `tolerance: 0.15` in the yaml but nowhere in prose. The remaining
two — §4.1 and §4.2 — are not transmission losses: no correct declaration
exists anywhere, which makes them the harder pair.**

Transmission loss is a different problem from L-74 and it has a different fix.
L-74 asks an author to *know* their referent, and on this evidence this corpus
does. What it lacks is a rule that the referent travels **with** the figure —
which the lab has already built once, for the rank-1 companion clauses, and has
not generalised. That rule would close four of the seven, and possibly five.

**§4.1 and §4.2 are the pair that rule would not touch**, because there is
nothing correct to propagate: a gate constant with no cited source, and a
citation with no recorded extraction. They are the two that need a document
fetched, not a sentence copied.

**Two of these reach the camera** (§4.1 act 1, §5.1 act 9). That is where the
value of this audit is, and it is a far smaller, far more actionable finding
than the 62.3% my own instrument first offered me — which is the result I would
have shipped had I not been required to control it in both directions.

---

## 11. RE-RUN, 2026-08-23 — the population re-derived, one finding closed, and this audit's own screen is not on disk

**Lines whose number changed above this section: 0.** Appended at the foot;
nothing above was edited (rule 6). §10's verdict stands as dated.

**Sweep date:** 2026-08-23, 19:45–20:30 UTC. **Executor:** `lab-lane`,
verification team. **This section classifies and records. It repairs nothing**,
per §0's rule, and it re-grades no verdict of any team.
**Compute: zero core-minutes.**

### 11.1 Control first — the section unit reproduces exactly, the bucket screen cannot be re-derived at all

§2's population rule is stated precisely enough to re-implement, so it was, and
run against the **audit's own commit `df4d4cbe`** before any current number was
taken.

| quantity | published §2/§3 | re-derived at `df4d4cbe` |
|---|---|---|
| tracked `*.md` | 367 | **368** |
| **sections total** | 4,844 | **4,844 — exact** |
| verification sections | 1,549 | see below |

**The section unit is confirmed to the unit.** A heading-delimited split of the
368 files returns **4,844**, the published figure on the nose — so the frame and
the sectioning of this re-implementation are the audit's own, and any
disagreement below is about the *qualification rule*, not about the population it
is applied to.

**The qualification rule as written does not return 1,549.** §2 says a section
qualifies if it carries *"one of the … fixed verdict tokens … together with a
number, or … a verification verb"*. Implemented literally — tokens
case-**sensitive**, as the charter writes them — that selects **1,008**. Eight
readings were tried:

| reading | sections |
|---|---|
| tokens case-sensitive substring + number, or verb (**the rule as written**) | 1,008 |
| tokens case-sensitive `\b`-bounded + number, or verb | 941 |
| tokens case-sensitive + a ≥3-decimal number, or verb | 750 |
| verbs only | 564 |
| tokens case-sensitive + number only | 567 |
| **tokens case-INSENSITIVE `\b`-bounded + number, or verb** | **1,567** |
| tokens case-insensitive `\b`-bounded alone, or verb | 1,573 |
| tokens case-insensitive substring alone | 1,554 |

**The published 1,549 is matched by no reading, and bracketed closely by one:**
case-insensitive word-bounded tokens **together with a number**, or a
verification verb, gives **1,567 — Δ18, 1.2%**. That is almost certainly the
screen that ran, and §2 simply does not state case-sensitivity. Under the
case-**sensitive** reading the same rule is off by 35%.

**And the residual 18 cannot be closed, because the instrument is not in the
repository.** §3 says *"the screen is frozen at the version reported above"* —
but frozen where? `git ls-files` carries no referent-screen script; `scripts/`
holds `sweep.py`, `fail_open_scan.py` and `withdrawal_sweep.py` and nothing that
implements this classifier. **Consequence, stated plainly: §3's four bucket
figures — EXTERNAL 408 / 26.3%, SELF-REFERENTIAL 83 / 5.4%, BOTH 93 / 6.0%,
UNDECLARED 965 / 62.3% — cannot be re-derived by anyone, now or later.** Neither
can the 4-of-14 adjudication that scales onto 280 (90–560). This is the
`LEDGER_HEADLINE_AUDIT.md` §4.1 defect in this document — *"its citation … points
into an uncommitted tree"* — and it is the sharper form of it, because here the
instrument was never committed at all. **Recorded against this audit, not against
the corpus it audits.** §3's own instinct was right and insufficient: it
published the number as an artifact and declined to promote it, but a figure
nobody can re-run is not an artifact either.

### 11.2 The population as it now stands, so the next re-run can diff it

Frame: `git ls-files '*.md'`, section unit, the 1,567-reading of §2's rule.
HEAD moved `c7dc6add` → `890bfa7f` while this ran.

| quantity | 2026-08-11 (`df4d4cbe`) | 2026-08-23 |
|---|---|---|
| tracked `*.md` | 367 | **635** |
| sections total | 4,844 | **9,497** |
| **verification sections** | 1,549 | **3,152** |
| documents carrying at least one | 297 | **552** |
| tables whose **header row** carries a `reference` column (D-B6-8's metric) | 12 | **76, across 55 documents** |

**Material added since 2026-08-11 and still tracked at HEAD: 173 documents,
2,632 sections, 892 verification sections** — 304 `.md` were added in the window
and 131 of them have since been moved or removed by the MOVE_MAP
reorganisation, which is why the added-and-surviving figure is the one quoted.
**None of the 892 was adjudicated by reading.** They are counted here so the next
re-run has a denominator; a classification of them is the named next rung and is
**not** performed. Absence of a finding against those 892 is a statement about
this re-run's depth.

**D-B6-8 has moved 6.3×, 12 → 76 header rows.** The docket item asked for the
`reference` column to become mandatory so referent declaration is
machine-checkable; the column has spread widely without a rule requiring it. That
is progress on the mechanism and says nothing about whether the cells are filled
correctly, which was not checked.

### 11.3 §4.1 — RANK 1 IS SETTLED, and settled the way this audit asked

The cylinder Strouhal finding — *"an external name over an unattributed
constant"* — was actioned on **2026-08-18** and the record is
`docs/DOCKET.md` D12. What was done:

- **NACA Report 1191 was obtained and retained**, at
  `docs/papers/roshko_1954_naca_tr_1191.{pdf,txt}`, SHA-256
  `7f395ab8ba11f21007dc6f7a84504a2c7ce542c2ed54674d07540ce21db008b4`, 28 pages,
  **title-page verified** (L-144), from NTRS `19930092207`.
- **The verdict is NOT SUPPORTED.** The report's printed page 11 gives
  `S = 0.212(1 − 21.2/R)` for `50 < R < 150`, so Re = 100 is in the stable range
  and that form governs. The form the gate evaluates — `0.198(1 − 19.7/Re)` —
  occurs in the report **in no range**.
- **The zero was planted.** `grep -c '0\.198\|19\.7'` on the retained text
  returns **0**; positive control `grep -c '21\.2\|0\.212'` on the same file
  returns **8**. A reader-blindness explanation (a dead text layer) is excluded
  by that control, exactly as constitution rule 3 requires.
- **A third defect surfaced:** the NTRS link at
  `cylinder_vortex_shedding.py:22` resolves to NACA Report **828** (cantilever
  beam bending), not Roshko.
- **It was NOT re-graded and NOT re-attributed**, on the stated ground that each
  is a verdict change and each is the owner's. What landed instead is that the
  nine-act table now carries the referent, its class and the band on **every**
  row, and act 1's cell states its constants occur in no cited source.

**This is §10's harder pair reduced to one.** §10 said §4.1 and §4.2 *"need a
document fetched, not a sentence copied"*; the document was fetched, and the
answer was that the referent does not support the number. The docket row **stays
OPEN** because settlement requires the regrade nobody below the owner may make —
which is the correct place for it to stop.

**§4.2 (the Ahmed 0.285 extraction record) was not re-checked** and no claim is
made about it here. **§5.1 (the CRM `VALIDATED` chip) is recorded as still live**
at `docs/DOCKET.md` D14, which carries no resolution marker; that is a read of
the docket row, not a re-derivation of the finding.

### 11.4 A NEW finding of this audit's own class: cited referents that are not on disk

L-74's question is *what was this checked against*. A referent that HEAD
advertises and the disk does not hold fails that question in the most literal
way, and `git status --porcelain` reports **10 tracked paths deleted in the
working tree and not committed**. Two groups matter:

**(a) `docs/campaigns/F14-cooling-ladder/K1_STANDING_THERMAL_CHECKS.md` — tracked,
absent from the worktree, and cited by five documents:** `docs/LESSONS.md`,
`docs/campaigns/F14-cooling-ladder/K0c_RESULTS.md`,
`K2a_RACK_ROW_MODULE_SPEC.md`, that campaign's `README.md`, and
`verification/campaign/MOVE_MAP_BATCH0_RULINGS_2026-08-17.md`. A reader following
any of those five to the standing thermal checks finds nothing on disk.

**(b) Eight planted-control artifacts under `K2b_runs/`:**
`K2bP_C3_plant/HEATBALANCE_{400,800}.{json,txt}` and
`K2bP_C3b_noplant/HEATBALANCE_{400,800}.{json,txt}` — tracked, absent from the
worktree. `HEATBALANCE_{1000..5000}` survive in both twins. **The missing four
iterations are exactly the ones backing `docs/DOCKET.md` D381's published
recovery figures — 155.55 W at 400 and 315.57 W at 800** — and D381 is *"left
standing rather than rewritten, per this file's append-only rule"*, so a reader
who follows the superseded row to its artifact finds nothing.

**The likeliest explanation is disclosed in the corpus itself and is benign**:
D390 records that *"`heat_balance.py` audits invoked against time directories
that did not exist yet left `HEATBALANCE_<t>.txt` reports carrying no ledger,
**which were cleared and re-run rather than committed**"*. So this is very
probably that deliberate clearing — **and the clearing was never committed**,
which leaves HEAD advertising artifacts the disk does not hold.

**Inspected and NOT reverted** (constitution rule 10); the index is the chief's
call. Recorded as a finding for the owning team, with the note that the bytes are
still recoverable from HEAD and that this is therefore a filing defect, not a
lost measurement.

### 11.5 What this re-run did not reach

1. **None of the 892 new verification sections was adjudicated by reading.** The
   population is counted; the classification is not attempted. This is the
   largest thing not reached.
2. **§3's screen was not rebuilt.** It could not be: its vocabulary lists are not
   in the repository (§11.1). Rebuilding it from the prose description would be
   a *different* instrument reporting under this document's numbers, which is the
   error §3 stopped itself from committing.
3. **§4.2, §4.3, §4.4, §4.5, §5.2 and §5.3 were not re-checked.** §5.1 was read
   from its docket row only. Six of the seven live findings therefore carry no
   2026-08-23 status.
4. **§8's named frontier is untouched**, and §9's docket items other than D-B6-8
   and D12 were not re-derived.
5. Per §2.7's principle in the sibling sweep audit, **this section is now part of
   the corpus it classifies**: it carries verdict tokens and numbers and will
   qualify as a verification section in the next re-run's denominator.

---

## 12. THE SCREEN IS IN THE REPOSITORY, 2026-08-24 — §11's population producer recovered, controlled and committed; §3's bucket screen is still not, and was deliberately not rebuilt

**Lines whose number changed above this section: 0.** Appended at the foot;
nothing above was edited (rule 6). §10's and §11's verdicts stand as dated.

**Stamp:** 2026-08-24T17:50:45Z (`date -u`, taken in the writing invocation).
**Executor:** `lab-lane`, verification team. **Compute: zero solver core-minutes.**
**This section repairs an instrument and records numbers beside the ones already
published. It re-grades no verdict of any team and strikes nothing.**

### 12.1 The defect, restated against this document

§11.1 recorded, against this audit rather than the corpus, that §3's four bucket
figures *"cannot be re-derived by anyone, now or later"* because the screen that
produced them was never committed. **§11 then shipped with the same defect.**
Commit `e3f3b521` changed exactly one file — this one, 186 insertions, 0
deletions — and carried no producer. So §11.2's population table quoted five
figures whose instrument was, on the day the finding against §3 was published,
itself already outside git.

### 12.2 The §11 screen was RECOVERED, not rebuilt

Three artifacts from the sweep's own session survived on this box, timestamped
inside §11's stated 19:45–20:30 UTC window. They are named here by filename
only: they sat in a session temp directory, and a repository document does not
cite a scratch path (rule 13).

| artifact | mtime (UTC) | what it implements |
|---|---|---|
| `referent_pop.py` | 2026-08-23 19:47:25 | §2's rule with **case-sensitive** tokens — §11.1's 1,008 row |
| `ref_j.py` | 2026-08-23 19:49:03 | §2's rule with **case-insensitive, word-bounded** tokens — §11.1's 1,567 row, the frame §11.2 declares it used |
| `ref_j.py.per.json` | 2026-08-23 19:49 | that run's own per-file output |

`referent_pop.py`'s docstring quotes its two vocabulary lists from this file at
`:117-122`, and the surviving per-file JSON **sums to 892 verification sections
across 151 documents** — which is exactly §11.2's published *"892 verification
sections"* for the material added since 2026-08-11. The recovered scripts are
the instrument that ran, corroborated by their own surviving output and, in
§12.4, by an exact re-derivation of four published figures.

**Recovery, not reconstruction, is what makes this a repair rather than a new
instrument** — and it was luck. The producer of a published table survived for
one day in a directory this lab has wiped three times (L-186). §12.3 is the part
that stops it mattering next time.

### 12.3 What was committed, and how it refuses

**`scripts/referent_population_screen.py`** — the recovered logic, both readings
in one instrument, framed on **a named revision's blobs rather than on
`git ls-files` and the worktree**, so the same command returns the same numbers
at any later date. `scripts/check_filing.py` raises no violation naming it (28
violations stand elsewhere in the corpus, all pre-existing and none this file's).

**Planted control, constitution rule 3 — 17 checks, run before any population
number is taken.** Seven known sections are written to disk, hashed into the
object database, and read back **through the same blob reader and the same
predicates that produce the figures**. Four plants must qualify, three must not,
and one — a lowercase verdict token — must be classified *differently* by the two
readings, which is the only way a screen whose two readings were secretly one
code path can be caught. The script exits 2 and prints no numbers if any plant
misses its bucket.

**The control was shown able to refuse.** Seven mutants, each a way this screen
could be quietly wrong; all seven exit 2:

| mutation | the plant that caught it |
|---|---|
| `re.IGNORECASE` dropped from the token regex | plant 3, under `ci_wb` |
| the two readings aliased (`strict` given `ci_wb`'s test) | plant 3, under `strict` |
| the verification-verb clause disabled | plant 1 |
| the "together with a number" requirement dropped | plant 5 |
| heading regex narrowed to `^#{4,6}\s` | plant splits into 1 section, not 7 |
| header/body offset shifted by one row | the matched row is plant 7's body cell |
| the table-separator test disabled | two rows match, not one |

A weaker first version of this control let two of those seven through, and both
survivors were repaired before commit: the reference-column check now asserts
**which** header row matched rather than how many, and the plant carries a
trailing sentence so that no planted table row is the last line of the file —
where an off-by-one could never be reached. The control writes one unreferenced
loose blob per run (`git hash-object -w`); it touches no ref and no index.

### 12.4 Re-run — §11.1's four figures reproduce EXACTLY

At the audit's own commit `df4d4cbe`, blob frame:

| quantity | §11.1 published | committed screen, 2026-08-24 |
|---|---|---|
| tracked `*.md` | 368 | **368 — exact** |
| sections total | 4,844 | **4,844 — exact** |
| verification sections, case-sensitive reading | 1,008 | **1,008 — exact** |
| verification sections, case-insensitive word-bounded | 1,567 | **1,567 — exact** |

**Four for four.** This is the evidence that the committed instrument is the
2026-08-23 instrument's behaviour and not a fresh screen reporting under this
document's numbers — the error §11.5 item 2 refused to commit, and the reason
§3's buckets are still not rebuilt below.

### 12.5 §11.2's population table does NOT reproduce, and the cause is the frame

| quantity | §11.2 published (2026-08-23) | committed screen at `890bfa7f` | committed screen at `45995a5e` (today) |
|---|---|---|---|
| tracked `*.md` | 635 | **678** | **736** |
| sections total | 9,497 | **10,228** | **11674** |
| verification sections (case-insensitive reading) | 3,152 | **3,421** | **4002** |
| verification sections (case-sensitive reading) | not published | **2,474** | **3003** |
| documents carrying at least one | 552 | **593** | **650** |
| tables whose header row carries a `reference` column | 76, across 55 documents | **81, across 58** | **85, across 62** |

`890bfa7f` is the commit §11.2 names as the HEAD its sweep ran up to, so the two
middle columns are the same corpus read two ways, and every published figure is
**low**.

**The cause is measured, not inferred.** §11.2's frame is `git ls-files '*.md'`
plus `open()` on the worktree — the **shared index**, which this lab established
on 2026-08-23 (D486) decays by construction. Measured live in the invocation that
wrote this section, at `45995a5e`: `git ls-files '*.md'` returns **701**
while that revision's tree carries **736** markdown files, of which
**736** are present on disk — so **35 tracked markdown files
exist, are committed, and are simply not listed by the command §11.2 framed on**.
A screen framed that way reads a smaller corpus than the repository holds, and
reads a *different* smaller corpus every time the index decays differently.

**§11.2's five figures are therefore not re-derivable at any later date, by
construction, and no re-run will ever match them.** They are **not struck**: they
were honestly taken, they are correctly labelled as of their date, and §11.2's
stated purpose — *"so the next re-run can diff it"* — is served by recording the
revision-framed row beside them rather than by rewriting them. From this section
forward the revision-framed figures are the ones a diff should be taken against,
because they are the only ones that can be recomputed.

### 12.6 What is still unreproducible, and was deliberately left so

1. **§3's four bucket figures — EXTERNAL 408 / 26.3%, SELF-REFERENTIAL 83 /
   5.4%, BOTH 93 / 6.0%, UNDECLARED 965 / 62.3% — remain unreproducible, and the
   4-of-14 adjudication scaling onto 280 (90–560) with them.** The two vocabulary
   lists exist in no commit and on no disk searched here; the recovered scripts
   implement the §2 population rule only and contain no bucket classifier.
   **They were not rebuilt from the prose, on purpose**: §11.5 item 2 rules that
   doing so *"would be a different instrument reporting under this document's
   numbers"*, and §12.4 is what a genuine re-derivation looks like by contrast.
   The committed screen's docstring carries that scope limit so no later reader
   mistakes it for §3's producer.
2. **D-B6-8's published `12` reference-column header rows does not reproduce
   either.** The committed screen counts **29 across 23 documents** at
   `df4d4cbe`. That figure came from the same uncommitted 2026-08-11 instrument,
   so **nothing follows about which is right** — the two are not known to be
   counting the same thing, and no claim is made that D-B6-8 was wrong. What is
   now on record is a definition anyone can run: the row immediately above a
   `|---|` separator, any cell of which contains `reference`, case-insensitively.
   §11.2's "6.3× growth" reading of that metric rests on two instruments and is
   left standing as its authors took it, uncorroborated.

### 12.7 What this section did not reach

1. **No section was adjudicated by reading.** §11.5 item 1's 892 unadjudicated
   verification sections are still unadjudicated, and the population has grown
   since. This section repairs an instrument; it classifies nothing.
2. **§4.2, §4.3, §4.4, §4.5, §5.1, §5.2 and §5.3 carry no 2026-08-24 status.**
3. **§11.4's ten deleted-in-worktree referents were not re-checked** and no claim
   is made about whether they have since been landed or restored.
4. Per §11.5 item 5, **this section is now part of the corpus it counts** and
   will appear in the next re-run's denominator.

---

## 13. DATED SECTION, 2026-08-27 — THE MACHINE DOCKET: MY FINDING WAS A DUPLICATE OF **D516**, THE LEVER IS **NOT** DEAD, AND THE REAL RESIDUE IS **FOUR LIVE POINTERS D516 DID NOT SWEEP** — ONE OF THEM IN A CHARTER I AMENDED THE SAME AFTERNOON

**Appended at the foot; nothing above edited. `Lines whose number changed above this
section: 0`, proved by a byte-prefix check against the HEAD blob in the same invocation
that wrote this section. Routed to this team by the chief after this supervisor reported
`demo-output/website/agenda/docket.json` as "named in `CLAUDE.md` and not on disk".**

### 13.1 THE FINDING WAS ALREADY DOCKETED, AND SAYING SO IS THE FIRST OBLIGATION

**`docs/DOCKET.md` D516 (measured 2026-08-25 by a chief-routed bookkeeping lane) records
this exact defect**, names the same dead path, dates the move to 2026-08-18, identifies
the successor as `research/agenda/docket.json`, refuses a D-row mirror on the merits, and
places the one-line `CLAUDE.md` correction on Sanaa's desk because **no agent edits
`CLAUDE.md`**. **My report added nothing to it and should have found it first.**

**This is the third time today the answer was "the lab already knew, in writing"** — after
`07313b68`'s commit subject naming its own defect, and `analyse_t1b_L4.py:144-151`'s frozen
selftest asserting the verdict the record contradicted. **The recurring failure in this lab
is not missing knowledge; it is knowledge that is recorded and not consulted**, and this
audit has now supplied its own instance.

### 13.2 THE DEAD-LEVER QUESTION, ASKED AND ANSWERED **NO** — measured by running it

`scripts/check_docket_surface_agreement.py:11` names the dead path in its **docstring**, so
the obvious hypothesis is a checker reading an absent input and passing vacuously — the
`FAIL_OPEN_GATE_AUDIT` shape. **Executed rather than reasoned about: it resolves its path at
runtime through `lab_paths.AGENDA` (`:81`, `:95`, `:286`), loads the successor, reports 75
shared ids and 245 one-sided, and returns `VERDICT: PASS`, rc 0.** **The lever is alive; only
its self-documentation is stale.** A negative result, recorded because an unrecorded negative
gets re-investigated.

### 13.3 A NAIVE PARSE OF MINE, CAUGHT BEFORE IT WAS REPORTED

Checking D516's "264 proposals", this supervisor's first read of the successor returned
**"records: 2"**, which read as a contradiction of the docket row. **It was a naive parse:**
the file is a dict of two keys — `generated_at` and `proposals`, the latter a list of
**264**. **D516's number is right and mine was an artefact of the reader.** Recorded because
the alternative was reporting a false contradiction against a peer's measurement, and because
it is `VERIFICATION_CHARTER` **v1.13** working one commit after it was written: *derive the
pattern from the artefact, never from the claim.*

### 13.4 WHAT IS ACTUALLY NEW — D516 REPAIRED THE CONSTITUTION'S ROW AND SWEPT NO OTHERS

D516 names **one** live pointer, `CLAUDE.md:279`. A census of every tracked citation of the
dead path finds **five live pointers plus one stale docstring.** The rest of the ~50 hits are
**historical records** — MOVE_MAP execution logs, morning reports, campaign records — which
cite the old path *as it then was* and are correct as history. **The distinction is the
finding: a raw count of citations is not a count of defects, and sweeping on the string alone
would have "repaired" dozens of correct historical records.**

| live pointer | what it tells a reader | owner |
|---|---|---|
| `CLAUDE.md:279` | the machine docket's location | **Sanaa's alone** — D516's item, on her desk |
| `docs/MEMORY_ARCHITECTURE.md:80` | *"Costed queue snapshot — **AUTHORITATIVE FOR `status`**"* | **the worst of the five** — it asserts authority for the field D218 measured 45.3 % disagreement on |
| `docs/MEMORY_ARCHITECTURE.md:425-426` | an **executable** one-liner (`json.load(open(...))`) and a `stat` | both now **throw**; a copy-pasteable command that cannot run |
| `docs/charters/ESCALATION_CHARTER.md:91` | where escalations go | charter owner |
| `docs/charters/REPORTING_CHARTER.md:118` | the **`## 5. REFILLED QUEUE`** section's `Source:` artifact | **see §13.5** |
| `scripts/check_docket_surface_agreement.py:11` | docstring only; runtime is correct (§13.2) | cosmetic, but it is an instrument's own description |

### 13.5 DISCLOSED AGAINST THIS TEAM: I AMENDED THAT CHARTER TODAY AND DID NOT NOTICE

`docs/charters/REPORTING_CHARTER.md:118` names the dead path as the source artifact for the
morning report's **Refilled queue** section. **This supervisor amended that same file at
`4a8ab0d7` this afternoon** — adding headline metrics whose §2 clause 1 states that *"a value
carries how it was obtained"* — **without noticing that a section of the same document points
its `Source:` line at a file that has not existed for nine days.** §2 rule 7 of that charter
says *"a cited artifact that is not on disk is a finding inside the report."* **The charter
that mandates that check contains an instance of what it forbids.**

### 13.6 RECOMMENDATION — one sweep, not six edits, and NOTHING IS EDITED HERE

**Nothing in this section is repaired by this team.** `CLAUDE.md` is Sanaa's; the other
pointers sit in files with their own owners, and a pointer repair inside a charter is a
**dated amendment**, not an in-line edit (rule 6). Recommended:

1. **`CLAUDE.md:279` — Sanaa's one-line re-point**, exactly as D516 already proposed and
   already has on her desk. **This section adds no new ask there.**
2. **The other four live pointers are re-pointed by their owners as dated amendments**, each
   naming `research/agenda/docket.json` and stating that the artifact is **dormant, not
   rotten** (D516 §3: `generated_at` 2026-08-08, idle because the research-wells workflow is
   idle; any repair is to **run the generator**, never to hand-edit the JSON).
3. **THE STANDING RECOMMENDATION, which is the only genuinely new lab-level ask:
   A REORGANISATION THAT MOVES A TRACKED ARTIFACT RE-POINTS ITS LIVE CITERS IN THE SAME
   COMMIT, OR FILES THE UNSWEPT LIST.** This lab has now recorded the same class **three
   times** — `D408` (the paper-library move re-pointed nothing, three dead paper paths),
   `D516` (this one), and this section's four survivors of D516's own repair. **The repeat
   is the evidence: a move is measured for what it would destroy — `0869284e`'s subject
   boasts of "measuring the 18 files a flat merge would destroy" — and never for what it
   would leave pointing at nothing.** **A move is code-coupled and document-coupled; only the
   first is ever measured.** *Recommended to the chief for Sanaa; not adopted, and this team
   creates no gate on it — a checker that refuses is hers (D539).*
