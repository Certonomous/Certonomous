# CRM / DPW REFERENCE AVAILABILITY — THE ONE TABLE, AND WHAT IT ACTUALLY CONTAINS

**Status: FINDING. NOT a pre-registration. NOT a band. It registers NOTHING and gates NOTHING.**
**Owner: shared by `cfd` (CRM wing-alone, `SOLVE_L2`) and `dafoam` (CRM wing-body, `D8G`).**
**Written 2026-09-12 by a cfd `lab-lane` so that the two teams cite ONE table and neither
writes a second.**

---

## 0. WHY THIS FILE EXISTS AND WHY IT IS NOT THE BAND

Sanaa's 2026-09-12 run instruction, byte-exact from
`docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md`, requires for both CRM cases:

> *"band registered before grading: CL, CD, CM at Mach 0.85, CL = 0.5, against NTF/Ames data
> with the DPW scatter as the honest tolerance"*

and, in the launch rules of the same directive:

> *"reference and band for the graded quantity (**external reference for validation cases, not
> an internal anchor**)"*

**This lane went to register that band and could not, and the reason is a fact about the box,
not a judgement about the instruction.** What follows is the evidence. Every source below was
read at its title page (rule 15), never accepted from a filename, a manifest or a hash.

---

## 1. THE ONE PAPER ON THIS BOX THAT NAMES NTF AND AMES — AND IT DOES NOT CARRY THE DATA

| field | value |
|---|---|
| file | `docs/papers/benchmark_test_cases/vassberg_2008_nasa_common_research_model.pdf` (+ `.txt` sidecar) |
| title page read (rule 15) | **AIAA 2008-6919**, *"Development of a Common Research Model for Applied CFD Validation Studies"* |
| authors | J. C. Vassberg, M. A. DeHaan (Boeing); **S. M. Rivers, R. A. Wahls (NASA Langley)** |
| what it is | the CRM **geometry-definition** paper |

**It is the right paper and it is verified. It still cannot supply the band, and it says so
itself.** From its own abstract, on disk at `:24-28`:

> *"Detailed aerodynamic performance data has been generated for this model; however, this
> information is presented in such a manner as to **not bias CFD predictions** planned for the
> fourth AIAA CFD Drag Prediction Workshop, which incorporates this common research model into
> its blind test cases."*

and at `:383-384`:

> *"Currently, the **NTF test is planned** for the 2nd quarter of calendar year 2009 with the
> **Ames 11-foot test to occur** in the first half of government fiscal year 2010."*

**The tunnel entries were in the FUTURE when this paper was written.** It describes the test
matrix, the facilities and the instrumentation. It reports **no measured CL, CD or CM**. Its
force data is *deliberately withheld* because DPW4 was a blind exercise.

**There is no other NTF or Ames source on this box.** A repository-wide search for `NTF`
across all Markdown returns four files: this finding's two inputs (`docs/DPW-CRM-SCOPING.md`,
`verification/campaign/DPW8_AEPW4_SCOPING.md`), Sanaa's directive itself, and
`CHALLENGE_SLATE_2026-08.md`. **None is a data source; all four are scoping prose.** A search
of `docs/papers/**` for `rivers`, `tinoco`, `dpw` returns only
`sansica_2025_dpw8_aepw4_buffet_workinggroup.pdf`, which is a **DPW8/AEPW4 buffet working-group
paper**, not a DPW-VI drag database.

---

## 2. THE SCATTER NUMBERS THAT ARE IN THE REPOSITORY — AND WHY THEY CANNOT BE USED AS THEY STAND

`docs/DPW-CRM-SCOPING.md` carries the only scatter figures the lab holds:

| figure it states | line |
|---|---|
| median reported drag **257 counts** (Cd 0.0257) at L2 coarse | `:53` |
| participant **IQR ±4–5 counts, band 252–262 counts** | `:56` |
| standard deviation 3.7–5.1 counts | `:57` |
| *"realistic success = predicting drag within 250–264 counts"* | `:69` |

**THREE DEFECTS, EACH ON ITS OWN SUFFICIENT TO BAR THE FIGURES FROM A GATE.**

**(a) The same file states the tunnel data is unavailable.** At `:49-50`, in its own words:

> *"The published experimental drag at the DPW design point ... **is cited in the DPW papers
> but held proprietary by NASA for the ongoing workshop**; DPW publishes CFD results relative
> to experiment with anonymized participant codes."*

A document cannot supply an NTF band on one line and record that NTF data is withheld on
another. **Its own line `:49` refutes any reading of it as the tunnel reference.**

**(b) The citation fails rule 15, and fails it conspicuously.** At `:374` the file names its
*"primary source for scatter & median Cd"* as a **`pmc.ncbi.nlm.nih.gov` (PubMed Central)
URL**. PubMed Central is a **biomedical** archive. **No corresponding paper exists anywhere
under `docs/papers/`**, so no title page can be read, and rule 15 admits no substitute for
one. **These numbers are UNVERIFIED and are recorded here as unverified, not repaired and not
quietly dropped.**

**(c) THE CONFIGURATION IS WRONG FOR BOTH OF OUR CASES, AND THIS ONE IS PHYSICS.**
257 counts is **DPW-VI full wing-body at full scale**. The lab has already ruled on exactly
this, twice, before today and against its own interest:

- `cases/dafoam/ladder-a/A6_crm_wingbody.md:131` — *"**No comparison is made against the AIAA
  DPW-VI wing-body scatter band** (257 drag counts) ... that figure is for the **full
  wing-body configuration at full-scale**"*.
- `verification/credibility/REFERENCE_TIER_STANDARD.md:§3`, the A6 row — reference tier
  **`code-verified`**, reference *"DAFoam's OWN tutorial baseline CD 0.02090 (**wing-ALONE**)"*,
  caveat **`DISAVOWAL REQUIRED`: "NOT experiment/workshop-validated; NO DPW-VI comparison"**.

**Three distinct configurations are in play and they do not share a drag band:**

| # | configuration | whose case | representative CD on this box |
|---|---|---|---|
| 1 | CRM **wing-alone** | **cfd** — `verification/runs/CRM_WINGALONE_runs/SOLVE_L2` | (none yet; run died at iteration 1012 at the 17:36Z reboot) |
| 2 | CRM **wing-body** | **dafoam** — `D8G` | 0.02090143421526141 (A6, tutorial baseline) |
| 3 | DPW-VI **full wing-body**, full scale | neither | 0.0257 (the 257 counts) |

**A wing-alone CD compared to a wing-body band differs by the entire fuselage drag
contribution.** Quoting one against the other would not be a loose band; it would be a
category error wearing a tolerance.

---

## 3. THE STATE OF THE BAND, IN THE FIXED VOCABULARY

**`BLOCKED`** — for **both** CRM wing-alone (cfd) and CRM wing-body / D8G (dafoam), on the
**same single cause**: no external CL/CD/CM reference for the CRM at M = 0.85, CL = 0.5
exists on this box, for either configuration.

**This is one block, not two.** Neither team is waiting on the other, and neither should write
a second table. **This file is the citable one.**

**What `BLOCKED` does NOT mean here:**

- It does **not** stop a solve. The primals are admissible, registered and may run; they
  simply cannot be **graded against a tunnel band** until one exists.
- It does **not** license an internal anchor as a substitute. Sanaa's item 10 forecloses that
  in her own words — *"external reference for validation cases, not an internal anchor"* — and
  the reference-tier standard would refuse the page (`check_reference_tier.py`, over-claim
  limb) if a `code-verified` case were shown as tunnel-validated.
- It does **not** license grading against the 257-count figure with a wider tolerance. Widening
  a band to cover a configuration mismatch is the post-hoc match Sanaa's instruction names and
  rejects.

---

## 4. WHAT WOULD UNBLOCK IT — NAMED PRECISELY, SO NOBODY RE-DERIVES THIS

Any **one** of the following, filed to `docs/papers/<topic>/author_year_identifier.pdf` **with
its `.txt` sidecar** (`FILING_CHARTER`) and **title-page verified** (rule 15):

1. **Rivers & Dittberner**, *"Experimental Investigations of the NASA Common Research Model"*
   (AIAA 2010-4218 / 2011-3508 / J. Aircraft 51(4) 2014) — **the NTF and Ames 11-ft force and
   moment database for the CRM wing-body.** This is the direct answer for **D8G**.
2. **The DPW-VI summary paper** (Tinoco et al., *"Summary of Data from the Sixth AIAA CFD Drag
   Prediction Workshop: CRM Cases"*, AIAA 2017-1208 / J. Aircraft 55(4) 2018) — supplies the
   **participant scatter** as a statistic with a readable title page, replacing the unverified
   PubMed citation.
3. **A CRM wing-alone reference**, if one is to exist at all. **This lane could not establish
   that a wing-alone CRM tunnel entry exists**, and says so rather than assuming one does. If
   it does not, the honest outcome for the **cfd** case is permanent: wing-alone is graded on
   **verification** limbs (the frozen §7 gates: iterative convergence, force plateau, y+,
   residual floor) and carries a standing `DISAVOWAL` that no tunnel comparison is available
   for its configuration. **That is a finding, not a failure**, and it is better stated now
   than discovered at grading time.

**Acquisition is not performed by any agent from this box. SUBMISSIONS AND OUTBOUND CONTACT
ARE PARKED (rule 7).** This section names what is needed; the fetch is Sanaa's call.

---

## 5. WHAT THIS LANE DID NOT VERIFY

- **Whether a CRM wing-alone tunnel entry exists in the literature at all.** Not resolvable
  from this box's paper store. Marked UNKNOWN above rather than guessed in either direction.
- **The AIAA numbers in §4** are stated as acquisition targets from this lane's knowledge of
  the literature. **They are NOT title-verified — no such file is on this box — and none of
  them may be cited as a reference until one is filed and read.** They are a shopping list,
  and are labelled as one precisely so that a later reader does not mistake §4 for evidence.
- **No claim is made about D8G's own registration**, which is dafoam's to hold. This file
  supplies the shared reference finding; it does not register anything on dafoam's behalf.

*Filed by a cfd `lab-lane`, 2026-09-12, at the cfd-supervisor's direction, explicitly to keep
cfd and dafoam on one cited table. It registers no gate, no threshold, no cap and no label.
Submissions parked. No agent's message is Sanaa's consent.*
