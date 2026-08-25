# ⚠ TITLE-PAGE VERIFICATION OF `High_order_grid_convergence.pdf` — **THE FILENAME IS FALSE**

**Written by the cfd supervisor personally, 2026-08-25, under standing rule 15** (*title-page
verification of every retrieved paper — never by file type, filename or hash*), which exists
because of **L-144**: a manifest can be internally consistent and externally false.

**READ THIS BEFORE WRITING ANY LESSON FROM THIS DOCUMENT INTO ANY CHARTER OR STANDARD.**

---

## WHAT THE FILE IS CALLED, AND WHAT IT ACTUALLY IS

| | |
|---|---|
| **Filename** | `High_order_grid_convergence.pdf` |
| **Actual title** | **High-order accurate, low numerical diffusion methods for aerodynamics** |
| **Author** | **John A. Ekaterinaris**, FORTH/IACM, Heraklion, Crete, Greece |
| **Published** | **Progress in Aerospace Sciences 41 (2005) 192–300** — a 109-page review article |
| **DOI** | **`10.1016/j.paerosci.2005.03.003`** (also the PDF's embedded `Title` metadata) |
| **Publisher** | Elsevier, © 2005 |

**The filename says "grid convergence." The document is a review of high-order spatial
discretisation schemes.** These are different subjects, and the difference is load-bearing for
what may lawfully be written into this lab's standards.

## THE DOCUMENT CONTAINS NO GRID-CONVERGENCE VERIFICATION APPARATUS. MEASURED, NOT ASSERTED.

Counts over the full extracted text (66,033 words, sidecar
`docs/standards/High_order_grid_convergence.txt`, created by this record):

| term | naive `grep -i` | **discriminated (`\b…\b`)** |
|---|---|---|
| **Roache** | 17 | **0** |
| **GCI** | 0 | **0** |
| **Richardson** | 0 | **0** |
| **grid refinement** | 0 | **0** |
| **mesh refinement** | 0 | **0** |
| **verification** | 0 | **0** |
| validation | 1 | 1 |

### ⚠ THE 17 "Roache" HITS ARE **ALL** THE SUBSTRING INSIDE **"app‑roache‑s"**

Every one. `approaches`, `approached`. **There is not a single citation of Roache in this
document.** Had this record been written from the naive count, it would have reported a paper
citing Roache seventeen times — the exact opposite of the truth, in the exact direction that
would have justified writing GCI lessons into the mesh standard.

**This is L-312 firing in production** (*a grep over a document is not an ENUMERATION instrument
unless it carries a discriminator*). It is recorded here as a live instance, not a hypothetical.

### The four "grid convergence" hits, read in context

1. **Fig. 97 and its two discussion sentences** — an **L2-norm order-of-accuracy demonstration**
   for second-, fourth- and sixth-order **DG polynomial orders** (P1, P3, P6) on a model problem,
   showing each achieves its expected order. That is **code order-verification of a
   discretisation**, not the Roache GCI apparatus this lab's gates run on.
2. **One bibliography entry**, ref. [117]: Sjogreen & Yee, *Grid convergence of high order methods
   for multiscale complex unsteady viscous compressible flows*, JCP 2003;185(1):1–26.

**That is the whole of it in 109 pages.**

## ⚠ THE CONSEQUENCE, STATED PLAINLY

**A lesson of the form "the grid-convergence literature says X, per `High_order_grid_convergence.pdf`"
written into `MESH_STANDARD.md`, `VERIFICATION_CHARTER.md` or the GCI/Roache rows of
`NUMERICS_KNOWLEDGE.md` would be a FABRICATION** — sourced to a document that contains no such
material. **No agent on any team may write one.** If a grid-level, refinement-ratio or GCI clause
is attributed to this file anywhere, it is wrong and should be struck on sight.

**This is not a criticism of the document.** It is an excellent and heavily-cited review. It is a
criticism of the filename, and only of the filename.

## WHAT THE DOCUMENT **IS** GOOD FOR — AND IT IS DIRECTLY ON POINT FOR cfd'S OPEN PROBLEMS

The paper's stated thesis: *"The main deficiency of widely available, second-order accurate
methods for the accurate computation of these flows is the numerical diffusion of vorticity to
unacceptable levels."*

| term | occurrences | why cfd cares |
|---|---|---|
| **WENO** | 160 | shock capturing — **F2** (transonic NACA0012) and **F12** (RAE 2822 Case 9) are both shock-bearing |
| **shock** | 89 | as above |
| **vortex** | 62 | |
| **limiter** | 37 | |
| **vorticity** | 20 | |
| **numerical diffusion** | 6 | the paper's central claim |
| **tip vortex** | 5 | **F1/ONERA M6's η = 0.99 station is cfd's worst Cp row** — RMS 0.114, bias +0.065, in the wingtip-vortex zone, and the standing explanation for it is *mesh-diffusion smearing* |
| order of accuracy | 56 | |
| implicit | 65 | |
| multigrid | 22 | |
| residual | 14 | |

**So the honest disposition: this document is relevant to cfd, but to DIFFERENT QUESTIONS than
its filename implies.** Its lessons belong in the **scheme, numerical-diffusion and
shock-capturing** rows of `NUMERICS_KNOWLEDGE.md` — **not** in the grid-level or GCI rows, and
**not** in `MESH_STANDARD.md` §9, whose three-level ruling comes from Sanaa and from Roache, and
owes nothing to this paper.

Its §2.3.2 (implicit schemes), §2.3.3 (time-accurate solutions with multigrid) and the
order-of-accuracy material are the parts that bear on cfd's **open convergence problem**, and are
the parts being mined next.

## FILING NOTES — recorded, not acted on

1. **The `.txt` sidecar was MISSING.** `docs/LOCATIONS.md` requires every paper to carry a
   matching `.txt` sidecar. Created by this record as
   `docs/standards/High_order_grid_convergence.txt` (66,033 words, `pdftotext`).
2. **The file sits in `docs/standards/`, not `docs/papers/<topic>/`,** and is not named
   `author_year_identifier.pdf` as `FILING_CHARTER.md` requires — it would be
   `docs/papers/numerical_methods/ekaterinaris_2005_high_order_low_diffusion.pdf`.
   **Sanaa placed this file and named it in her own directive, so cfd does NOT move or rename it.**
   The mismatch is recorded for her decision. **Renaming it would also break her directive's own
   reference to it by path**, which is a second reason not to.

**Compute: ZERO.**
