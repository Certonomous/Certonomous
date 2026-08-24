# The lab coverage matrix — one row per case, three columns, one tier

**Owner:** verification team. **Status: DRAFT, IN CONSTRUCTION — not yet a lab
record.** Rows are landing as they are audited; a row is not in this matrix until
this team has spot-checked its load-bearing evidence itself. Until this line is
struck, no other document may cite a tier from this file.

**Created** 2026-08-24 by the verification supervisor, at the chief's dispatch, as
the consolidation-week deliverable.

---

## 0. Provenance of the brief — read this before the rubric

**The three-column rubric and the five tier words below are the CHIEF'S
RECONSTRUCTION of Sanaa's directive. They are NOT her verbatim words, and this
document does not represent them as such.** The chief stated the reconstruction in
those terms when dispatching the work. Sanaa has not ruled on the rubric, and if
she reads it differently the rubric changes and every tier in this file is
re-derived from the same evidence — which is why each row carries its evidence and
not only its tier.

This matters more than a footnote. The whole point of the matrix is that a reader
can check it. A rubric whose provenance is fuzzy produces tiers nobody can audit,
and the tier is the only thing most readers will carry away.

---

## 1. The rubric, stated once and applied uniformly

| column | what it asks | scores green ONLY when |
| --- | --- | --- |
| **V** — code verification | Is the CODE verified against something with a known answer? | there is an **exact solution**, a **manufactured solution**, or a **correlation**, and the case was compared against it |
| **G** — grid convergence | Is the DISCRETISATION error quantified? | there is a **CONVERGING Roache triple**, with **GCI at Fs = 1.25** and an **observed order p**. Per CLAUDE.md rule 5, a triple that is DIVERGENT, STAGNANT, OSCILLATORY or EXACT is not G, and a GCI is never quoted when the three values are not monotone |
| **P** — validation | Is the RESULT compared against the world? | against a **public primary source**, with the **pre-registration ON DISK** |

**Tiers — exactly these five words, no synonyms:**

| tier | assigned when |
| --- | --- |
| **HOLDS** | V and G and P all green, under frozen pre-registrations |
| **GATE REACHED** | missing exactly one of V / G / P — **and the row names which** |
| **SURVEYED** | breadth evidence, ungated |
| **NOT HELD** | an honest FAIL, or a blocker |
| **NEVER RUN** | no solver has run in this class |

### 1.1 A vocabulary collision this matrix must not create

**`GATE REACHED` appears in two different vocabularies in this lab and they mean
different things.** In CLAUDE.md rule 1 and `VERIFICATION_CHARTER.md` §2 it is a
**gate VERDICT**: the gate was reached and the claim it serves is not thereby
established. Here it is a **matrix TIER**: the row is missing one of V / G / P.

A row can carry the verdict `PASS` and the tier **GATE REACHED** at the same time,
and that is not a contradiction — it means the gate that was armed passed, and the
matrix is recording that a different column was never armed at all. The dafoam
contribution flagged this collision independently (§0.1 of its file) and it is
recorded here because a reader who conflates the two columns will read this matrix
as saying the opposite of what it says.

**Every row below therefore prints the gate VERDICT and the matrix TIER as two
separate cells.** Where a row's tier is GATE REACHED, the missing letter is named
in the cell. A tier cell that says only "GATE REACHED" without naming the missing
letter is a defect in this file, not a row.

---

## 2. Why the family contributions could not be transcribed — the rubric divergence

Four families were asked for `MATRIX_CONTRIBUTION.md` rows. Three exist.
**Each of the three defined V, G and P differently, and differently from the
chief's rubric above.** Their tiers are therefore **claims scored on another
scale**, and transcribing them would have produced a matrix whose tier column
meant a different thing in every block of rows.

| family | file | its V | its G | its P |
| --- | --- | --- | --- | --- |
| closure | `cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md` (tracked, `a42fd634`) | a verification instrument **demonstrated able to fail** — planted-zero, identity test, independent re-derivation | a **pre-registered NUMERIC gate that could have failed**, frozen by sha before the run | a **pre-registered PREDICTION**, made before the run and graded |
| dafoam | `cases/dafoam/MATRIX_CONTRIBUTION.md` (**untracked on disk**) | the **finite-difference-versus-adjoint check** (`DAFOAM_CHARTER.md` §9) | *(not a column; the family prints a lab-verdict column and a matrix-tier column instead)* | *(as above)* |
| heat-transfer | `docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` (**untracked on disk**) | **a converged Roache triple with an observed order** | a **pre-registered gate with a threshold**, and what it returned | the reference **ON DISK and title-page verified** |

Read down that table: **closure's V is an instrument-integrity test, dafoam's V is
a gradient consistency check, and heat-transfer's V is grid convergence — which is
the chief's G, not the chief's V.** None of the three is the chief's V (exact
solution, manufactured solution, or correlation). Under the chief's rubric,
heat-transfer's V-green rows are G-green rows, and their V column is unfilled.

**Consequence, stated plainly because it is the single most important sentence in
this file:** a family's `HOLDS` is not this matrix's `HOLDS`. Every tier in section
3 was **re-derived by the verification team from the underlying artifacts**, not
lifted. Where a re-derived tier is weaker than the family's claimed tier, the row
says so and names the evidence, so the family can contest it against the same
artifacts.

Two of the three families anticipated exactly this and said so in their own files —
dafoam's §0.2 states its mapping is "this lane's proposal and the verification
supervisor may replace it", and heat-transfer's §0.2 defines its tiers "so they are
liftable". That is the right instinct and it is why the re-scoring is cheap.

### 2.1 Contribution files that are ON DISK BUT UNCOMMITTED

`cases/dafoam/MATRIX_CONTRIBUTION.md` (414 lines) and
`docs/campaigns/T-family/MATRIX_CONTRIBUTION.md` (730 lines) were written by lanes
that were killed by the session usage limit at ~20:50Z on 2026-08-24. **Both files
survived on disk and are untracked.** They were reported upward as lost; they are
not lost. They are their families' to commit, not this team's — this file cites
them by path and quotes them, and does not commit another team's work.

---

## 3. The matrix

**ROWS PENDING AUDIT.** Nothing is entered here until this team has checked the
row's load-bearing evidence against the artifacts. A HOLDS row that turns out to
be GATE REACHED is worse than one honestly labelled, because this file is what the
week's credibility rests on.

---

## 4. The two standing facts, under test

`docs/inventory/2026-08-24/LAB_INVENTORY.md` §7 asserts two structural facts about
the lab. The chief asked that they be **tested by this matrix rather than assumed**.
Both are under audit; neither is confirmed or refuted in this draft.

1. **"No converging Roache triple exists outside the thermal family."**
   Under test. A lead that may refute it: `VERIFICATION_CHARTER.md` §3.4 calls the
   **2D flat plate** "the lab's best verification result" and states it is the first
   family the Eca-Hoekstra certifier declares **conclusive**, on the finest triple,
   on both functionals — Cd at observed order **1.634**, reportable band
   **4.244e-6** (**0.148 %** of the value). The flat plate is not thermal. The
   open question is whether an **Eca-Hoekstra certifier verdict is the same
   instrument as a Roache triple with a GCI at Fs = 1.25**; they are not obviously
   the same, and the answer decides the fact.
   The same section records a second thing that bears on the G column: the flat
   plate's **band is earned and quotable while its observed order is still
   rising** (Cd 1.0833 → 1.2587 → 1.6344; Cf 1.0315 → 1.1110 → 1.5281), so the
   ladder is **not demonstrated asymptotic**. Whether an unsettled order still
   scores G is a ruling this file must make explicitly rather than by default.

2. **"No 3D PASS against experiment with a pre-registration on disk exists at all."**
   Under test.

If the matrix confirms either, that is a finding, not an embarrassment — it is the
kind of structural fact a lab can only state once it has counted.

---

## 5. What this file is not

- It is **not** the Certonomous Verification Manual. That document is
  **SEQUENCED BEHIND this matrix and deliberately held** by the chief; it draws
  only on rows this matrix has confirmed **HOLDS**, by this team's own spot-check.
  Drafting it from claimed rows is the failure mode it is sequenced to avoid.
- It is **not** a compute record. Costs live in `docs/COST_CALIBRATION.md`.
- It does **not** commit or edit another team's files.
