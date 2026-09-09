# Reference-Tier Credibility Standard

**Status:** working-tree draft (verification lab-lane). The supervisor diff-reads, plant-drives and commits.
**Provenance:** Sanaa 2026-09-09 (direct). *Every completed 3D case classified by its reference
strength BEFORE any page shows it; nothing shown above its true tier; make it a GATE binding the
demo and credential pages.*
**Instruments:** `verification/credibility/reference_tier_registry.json` (the frozen evidentiary
content), `scripts/check_reference_tier.py` (the gate).

---

## 0. Why this exists, and what it is NOT

A fidelity chip, a geometric building-block tier and a *reference tier* are three different things.
`validation_tiers.json` already places every case on the **geometric building-block axis**
(UNIT PROBLEM -> BENCHMARK CASE -> SUBSYSTEM CASE -> COMPLETE SYSTEM: how complete the geometry is).
That axis says nothing about **how strong the reference the result was actually graded against is** --
a "COMPLETE SYSTEM" case can have been checked against nothing but another code, and a "UNIT PROBLEM"
can carry an exact analytic answer. This standard adds the **reference-strength axis** and makes it a
gate. It grades *what a page is allowed to CLAIM*, not the physics of the solve.

This standard is scoped to **completed 3D cases**. 2D / axisymmetric cases are excluded by dimension
(section 4) and may never appear in a 3D listing.

---

## 1. The five reference tiers (strongest to weakest)

Ordinal rank in brackets; a page may show a case AT or BELOW its registered tier, never above.

- **experiment-validated (4)** -- validated against EXPERIMENTAL data; every deviation DISCLOSED.
  *Shown as:* "validated against <named experiment>", deviations stated. The disclosed-deviation
  caveat is mandatory where one exists.
- **bounded-agreement (3)** -- agrees within an EXPLICITLY-STATED quantitative band vs a named
  reference. *Shown as:* the comparison **always carries its band** (e.g. `+/-15%` / `[lo, hi]`).
  An experiment comparison shown for such a case **without** its band is a violation.
- **code-verified (2)** -- reproduces a CODE reference only (another solver, a tutorial baseline).
  *Shown as:* "reproduces <the code reference>", with an explicit **disavowal** that it is NOT
  experiment-validated. **NEVER** shown as experiment-validated.
- **method-verified (1)** -- internal verification only, no external reference (adjoint FD-verified /
  primal-converged / bug-find). *Shown as:* "self-consistency, not validation" / "no wind-tunnel data";
  the time-box or bug-find is stated. Carries the same disavowal as code-verified.
- **not-applicable-dimension (0)** -- 2D / axisymmetric. **EXCLUDED** from any 3D listing.

---

## 2. The ordering / gate rule (binding on demo pages and credential entries)

> No demo page or register entry shows a case ABOVE its true tier; a bounded-agreement case always
> shows its band; a caveated case always shows its caveat; an excluded case never appears in a 3D
> listing.

Operationally the gate (`check_reference_tier.py`) **REFUSES (exit 2)** on any of:

1. **Over-claim** -- a case shown with an asserted, non-negated claim of a tier ordinally ABOVE its
   registered tier (e.g. a code-verified case shown as validated against wind-tunnel/workshop data).
2. **Bounded-agreement without its band** -- a bounded-agreement case shown with an experiment
   comparison but without its explicit band string in the same window.
3. **Missing required caveat** -- an experiment-validated case with a mandatory caveat shown without
   it (A3 shock-offset), or a code-/method-verified case shown with an un-negated experiment token
   and no disavowal.
4. **Dimension leak** -- an excluded 2D/axisymmetric id inside a 3D listing (heading or inline list).
5. **Registry drift (fail-closed)** -- a completed 3D case is not fully classified in the frozen
   registry; an unclassified case may not be shown.

The gate can only turn a claim INTO a refusal; it never softens a violation to a pass. Verdict
vocabulary only (PASS / GATE FAIL / NOT A RESULT / BLOCKED / PENDING). A refusal is reported as
`GATE FAIL` with `case_id`, `path:line`, claimed tier, registered tier and the offending/missing token.

The registry is **sha-frozen before grading** (rule 2): the tier of each case is fixed before any page
is scanned, so a page cannot select the tier that flatters it. A planted-zero control (rule 3) drives
the scanner RED before any clean pass is emitted -- a zero from a blind scanner is not evidence.

---

## 3. Applied tier table -- the six completed 3D cases

Each tier VERIFIED at source (L-144), not taken from a provisional label; every source line was read.

| Case | Reference tier | Reference (source) | Required caveat / band | Evidence (path:line) |
|---|---|---|---|---|
| **A3** ONERA M6 | **experiment-validated** | Schmitt & Charpin, AGARD-AR-138 (1979) transonic wind-tunnel Cp campaign | **SHOCK-OFFSET caveat REQUIRED**: CFD shock aft of experiment at 6/7 span stations by 0.02-0.10 x/c; Cp RMS 0.049-0.114 | `cases/dafoam/ladder-a/A3_onera_m6.md:74-75, :114-135`; `cases/dafoam/ladder-a/LADDER_A_STATUS.md:32` (row 8, primal GATE REACHED, CD 0.0229955633492643) |
| **A4** Ahmed body | **bounded-agreement** | Ahmed, Ramm & Faltin 1984 (SAE 840300), Cd 0.285 | **BAND REQUIRED**: +/-15% => [0.2423, 0.3278] on frontal-area Cd (act 0.3041, 6.7% off, inside; 'solver-backed, not validated'; primal 0.2510 WITHDRAWN) | `cases/dafoam/ladder-a/A4_ahmed_body.md:15, :156-165, :186`; `verification/campaign/AHMED_BODY_RECONCILIATION.md:26-27, :82, :85` |
| **A6** CRM | **code-verified** | DAFoam's OWN tutorial baseline CD 0.02090 (wing-ALONE, CRM_Wing) | **DISAVOWAL REQUIRED**: NOT experiment/workshop-validated; NO DPW-VI comparison; exact tutorial reproduction, no accuracy claim | `cases/dafoam/ladder-a/A6_crm_wingbody.md:131, :138-159`; `cases/dafoam/ladder-a/LADDER_A_STATUS.md:47` (row 23, GATE REACHED, CD 0.02090143421526141) |
| **A2** MACH tutorial wing | **method-verified** | NONE external; internal FD verification of the adjoint gradient | **DISAVOWAL REQUIRED**: FD PASS (1.71%); opt TIME-BOXED 60 min, 47/~100 majors, NOT converged (opt run graded NOT A RESULT); 'self-consistency, not validation' | `cases/dafoam/ladder-a/A2_mach_tutorial_wing.md:63, :67, :104`; `cases/dafoam/ladder-a/LADDER_A_STATUS.md:27, :29` (rows 3 PASS, 5 opt NOT A RESULT) |
| **A5** U-bend | **method-verified** | NONE external (bug-find); weak PRIMAL-only code ref (tutorial CPL0 5.5% off, no band) | **DISAVOWAL REQUIRED**: adjoint-vs-FD 46.6% BUG-FIND (shipped GATE FAIL 46.84%, 2 sign flips; patched 2.77% PASS); half-model | `cases/dafoam/ladder-a/A5_ubend_internal.md:123, :158-159, :233-236`; `cases/dafoam/ladder-a/LADDER_A_STATUS.md:43, :44` (rows 19 GATE FAIL, 20 patched PASS) |
| **naca0015_sail_coarse** | **method-verified** | NONE external compared; internal FD gradient verification only | **DISAVOWAL REQUIRED**: primal converged (CD 0.033031, CL 0.180995); adjoint completed; FD PASS 4.52% shipped -> 0.0246% patched | `cases/dafoam/DAFOAM_CASE_STATUS.md:144-150`; `verification/credibility/validation_tiers.json` (case naca0015_sail) |

**6th-case identity:** the 6th completed 3D case is **`naca0015_sail_coarse`** (pre-ladder
`work_sail`), identified at source. A1 NACA0012 is **2D** and is therefore an **exclusion**, not the
6th. **PENDING Sanaa's confirmation** of the 6th case's identity.

---

## 4. Exclusions -- not-applicable-dimension (NEVER in a 3D listing)

| Case | Why excluded | Evidence (path:line) |
|---|---|---|
| **A1** NACA0012 (incompressible) | 2D single-cell-spanwise section, 4,032 cells | `cases/dafoam/ladder-a/A1_naca0012_incompressible.md:155`; `cases/dafoam/DAFOAM_CASE_STATUS.md:45`; `docs/dafoam/demo/ACT_D_reference_wing_sheet.tex:24` |
| **T23** | 2D/axisymmetric 5-deg wedge motor | `docs/campaigns/T-family/T23G2R_PREREGISTRATION.md:104` |
| **T24** | 2-D axisymmetric 5-deg wedge (electronics) | `docs/campaigns/T-family/T24_RESULTS.md:46`; `docs/campaigns/T-family/T24_PREREGISTRATION.md:168, :997-998` |
| **11 Ansys VM passes** (`VMFL*`) | all 2D / planar / axisymmetric verification cases; register makes no 3D claim | `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` (VMFL* rows; zero '3D'/'three-dimensional') |

---

## 5. Known limits (disclosed, per the gate's design)

- The gate's tier-of-a-page-claim is a **heuristic on prose**: a tier above method-verified is only
  read as CLAIMED when an assertion cue ("graded against", "validated against", "reproduces", ...)
  co-occurs with a reference token and is NOT negated. A generic description of what a reference body
  is does not, by itself, assert that our result was validated -- this is what keeps honest disavowals
  ("no wind-tunnel data", "self-consistency, not validation") from reading as claims.
- Windows are block/paragraph-scoped (one JSON object's strings for `.json`): a caveat in a distant
  block does not excuse a claim here, on purpose.
- SOURCE vs rendered-face divergence is possible on `.tex`; source-only hits are reported as doubt,
  not absence.
- **The registry, not the scanner, is the authority on each case's tier.** The scanner only checks
  pages against the frozen registry.

---

## 6. Live-tree note (2026-09-09)

At authoring, one credibility RECORD overstates its reference basis and the gate correctly REFUSES on
it: `verification/credibility/validation_tiers.json` case `crm_wingbody`, `basis` = "A full transport
configuration, graded against a published workshop campaign." A6/CRM is **code-verified** against
DAFoam's own tutorial baseline (wing-alone) and makes NO workshop/experiment comparison. The minimal
truthful correction is drafted for the supervisor's review; the file's `validation_tier` field is the
**geometric** axis (a different axis) and is handled separately. No customer-facing DISPLAY surface
currently shows any of the six 3D cases above its true reference tier.
