# Standards intake ruling — `docs/standards/High_order_grid_convergence.pdf`

**Date:** 2026-08-25. **Author:** heat-transfer supervisor.
**Trigger:** Sanaa, byte-exact: *"II/ heat transfer I just scpd the book into
Certonomous/docs/standards so the team can go ahead and read it"*.

**Status: DISCLOSURE AND ASSESSMENT ONLY. This document freezes nothing,
amends nothing, and moves no gate, threshold, band, cap or label.** Zero
compute.

---

## 1. Rule 15 — title-page verification, and the filename is NOT the document

**Verified by reading the title page, not by filename, path or file type.**

| field | value |
|---|---|
| **Filename on disk** | `docs/standards/High_order_grid_convergence.pdf` |
| **Actual title** | *High-order accurate, low numerical diffusion methods for aerodynamics* |
| **Author** | John A. Ekaterinaris, FORTH/IACM, Heraklion, Crete |
| **Venue** | *Progress in Aerospace Sciences* **41 (2005) 192–300**, Elsevier |
| **DOI** | `10.1016/j.paerosci.2005.03.003` |
| **Pages** | **109**, matching 192–300 exactly |
| **Landed** | 2026-08-25T15:59:56Z, 6 595 897 B |

**THE FILENAME IS MISLEADING AND THE DIFFERENCE IS NOT COSMETIC.**
`High_order_grid_convergence` names a topic — grid convergence — that **is not
this document's subject**. This is a **review of high-order spatial
discretizations** (ENO/WENO, compact finite difference, discontinuous Galerkin,
spectral volume) for vortex-dominated and separated aerodynamic flows. **A
record citing this file by its filename would attribute to it a subject it does
not have.** This is exactly the failure rule 15 exists to prevent.

## 2. THE DOCUMENT IS COMPLETE — and I nearly recorded that it was truncated

**`file -b` reports `PDF document, version 1.7, 10 page(s)`. That is WRONG.**
`pdfinfo` reports **`Pages: 109`**, the extracted text carries **109 page
boundaries**, the running head reads `192–300` on every page (= 109 pages), and
the last page ends mid-bibliography at reference [272]. **The document is
complete.**

**Recorded against myself:** on the `file` reading I formed the hypothesis that
the PDF was a 10-page excerpt of a 109-page review and was one step from writing
it down. **The file-type tool was the unreliable instrument — which is rule 15's
exact claim, encountered while applying rule 15.** The rule says never verify by
file type; the trap is that a file-type tool answers instantly and confidently.
**Two independent instruments (`pdfinfo`, and counting page boundaries in the
extracted text) were needed to settle a question one instrument had already
answered wrongly.**

## 3. What it contains, measured rather than characterised

Term counts over the full extracted text (314 234 non-whitespace characters):

| term | count |
|---|---|
| `Richardson` | **0** |
| `GCI` | **0** |
| `grid refinement` | **0** |
| `mesh refinement` | **0** |
| `design order` | **0** |
| `manufactured` (solution) | **0** |
| `grid convergence` | **4** |
| `convergence rate` | 5 |
| `order of accuracy` | 55 |

**The four `grid convergence` hits are one figure and one reference title.**
Fig. 97 plots the L2 norm of computed pressure for second-, fourth- and
sixth-order (P1/P3/P5) discontinuous-Galerkin solutions on triangular elements,
against an exact result, and the text's claim is that *"all solutions achieve
the expected order of accuracy"*. Reference [117] is Sjogreen & Yee, *Grid
convergence of high order methods for multiscale complex unsteady viscous
compressible flows* — **a citation, not content.**

**The 55 `order of accuracy` hits are the DESIGN order of a scheme**, not an
**observed** order fitted from a grid triple. **Those are two different
quantities and this lab grades on the second.**

## 4. RULING — IT IS NOT A GRID-CONVERGENCE STANDARD, AND THERE IS NO CONFLICT TO RECONCILE

**It bears on convergence criteria, mesh standards and grid-ladder design
only distantly.** It registers **no** convergence criterion, **no** mesh quality
gate, **no** refinement ratio, **no** safety factor and **no** ladder design
rule. **Nothing in it conflicts with any frozen artifact of this team**, and in
particular nothing in it would have changed:

- **`T1b_L4_AMENDMENT.md`** — its plateau criterion (spread above `0.2 x band`
  across the 60/70/80 D stations), its iterative-convergence criterion
  (relative change above `1e-6` of the range between the last two checkpoints),
  its evaluation order, or its bands (2.84 / 3.89 / 5.33 / 5.75 %);
- **K0d**, which is FROZEN, ARMED AND UNFIRED.

**AND IT COULD NOT HAVE, EVEN IF IT DID.** A standard that arrives after a
freeze **does not retroactively amend it**. Had this document carried a
conflicting criterion, the disposition would be a **disclosure on the record and
an input to the NEXT pre-registration** — never an edit to a frozen one. That
disposition is stated here so it is on record as the rule, not improvised later
against a document that happens to conflict.

## 5. THE ONE SUBSTANTIVE POINT OF CONTACT — carried forward, binding on nothing

**Its central theme is that a scheme's DESIGN order is realised only under the
conditions the scheme requires**, and its verification practice is to check that
a computed solution attains the expected order **against an exact solution**.

Two consequences worth carrying, **neither of which changes a frozen artifact**:

1. **It is a code-verification practice, and it scores `V`.** Checking a
   computed order against an **exact** solution is verification against
   mathematics, not against the world. **This is consistent with — and mildly
   corroborative of — the rubric ruling now on Sanaa's desk**, that an exact
   analytic solution supplies `V` and never `P`. **It is not offered as an
   argument for that ruling; the ruling is hers to make.**
2. **An observed order far above a scheme's design order is a TELL, not a
   triumph** — and this family has produced several. `p = 4.304464` on T3's
   second-order scheme was found this week to be an artifact of a ladder that is
   **not geometrically similar**; K0b's orders are fitted across an
   **iteration-count fork of ~8x the grid step**. **The lab had that diagnostic
   in hand and did not read it.** A prior of the form *"an observed order well
   clear of the design order indicts the ladder before it credits the method"*
   is a reasonable thing to register in a FUTURE pre-registration. **It is
   registered nowhere today and gates nothing.**

## 6. FILING — an observation, REFERRED and not acted on

**The file is a PAPER sitting in `docs/standards/`.** `FILING_CHARTER.md` places
papers at `docs/papers/<topic>/author_year_identifier.pdf` **with a matching
`.txt` sidecar**; `docs/standards/` holds standards documents.
**SANAA PLACED THIS FILE HERSELF AND IT IS NOT MOVED, RENAMED OR COPIED BY THIS
TEAM.** Two things are merely recorded:

- **No `.txt` sidecar exists for it**, so it is invisible to every repository
  grep. This team was bitten by exactly that shape yesterday — a sidecar of 281
  bytes and **zero characters of text** that a record claimed had been OCR'd.
- **`scripts/check_filing.py` R9-SIDECAR-MISSING does not reach
  `docs/standards/`**, so no check would have raised this. `scripts/` is not
  this team's territory: **REFERRED, not fixed** — and this is the second
  referral this team has made against R9 in two days.

## 7. What this document does NOT establish

- It does **not** establish that any thermal verdict, band, tier or order is
  right or wrong. **No verdict moves.**
- It does **not** establish that the lab should adopt high-order schemes; that
  is a direction question and is not this team's to decide.
- The assessment above rests on **term counts and four read passages**, not on a
  reading of all 109 pages. **Stated as its own limitation:** a criterion buried
  in a passage not surfaced by those terms would have been missed. The terms
  chosen are the ones this lab's gates are actually written in
  (`Richardson`, `GCI`, refinement, design order, manufactured solutions), and
  **all five of those return zero.**
