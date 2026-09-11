# CRM-WING-ALONE FLOW RUNG — the §10A successor. **SOLVER ADMISSION ON L2.**

**Status: DRAFT, NOT FROZEN. NO COMPUTE HAS RUN UNDER IT.** It is committed so that it exists
before compute (rule 2), not because it is finished. **It is not a launch authorisation** —
cfd-supervisor rules on the launch separately, against the disk at that moment.

Predecessor: `CRM_WINGALONE_PREREGISTRATION.md`, frozen `d2629d326`, blob
`1fa5fb725e6298d99dc4ab2207f55f11e575b285`, Amendment 1 signed `cbacda6b3`. Verified by this lane:
the first 37,613 bytes of the current file hash to that blob and **no commit touches it after
`cbacda6b3`.**

---

## 0. 🔴 WHAT THE MESH RUNG'S OUTCOME DID TO THIS ONE — READ THIS BEFORE §9B IS QUOTED AT IT

§9B of the predecessor recommended that O3 be *"a grid-convergence gate ALONE — an observed order
and a GCI on a self-consistent QoI, which needs no external dataset and is exactly what an
r = 2.000000 nested triple is for."* **That recommendation was written BEFORE the ladder was graded,
and grading it has taken the option away.**

| level | mesh verdict (committed `GATE_TABLE.md`) | usable for a triple? |
|---|---|---|
| L1 | **`GATE FAIL`** G-M4, min quality −0.05046 at layer 3 → **`BLOCKED`** | **NO** |
| L2 | **`PASS` on all five gates** (G-M1 68.2589, inside the 65–70 warning band) | yes |
| L3 | **`GATE FAIL`** G-M1, 79.3672 > 70 | **NO** |

🔴 **ONE ADMISSIBLE MESH IS NOT A TRIPLE. NO OBSERVED ORDER AND NO GCI MAY BE REGISTERED, COMPUTED
OR QUOTED UNDER THIS DOCUMENT.** The family's own triple is `NOT A RESULT` in the committed record,
and a Richardson quantity computed across meshes the lab has refused would be a number with no
standing dressed as a verification result.

**The refinement ratio, stated in CELL LAYERS as the standard requires, for the record and not for
use:** volume cells 144,768 / 1,158,144 / 9,265,152 → ratio **8.000000 twice** → **linear
r = 2.000000 twice, UNIFORM**, so the simple Richardson form *would* apply with no Celik unequal-`r`
machinery **if the meshes were admissible. They are not.** The ratio is not the obstacle; the gates are.

**Consequence, accepted rather than worked around: this rung is a SOLVER-ADMISSION rung, not a
grid-convergence rung.** A convergence study needs a new family that clears all five mesh gates at
three levels, and that is a separate mesh rung which does not exist.

---

## 1. SCOPE

**One solve, on L2 only.** L2 is the only level that cleared all five mesh gates.
🔴 **L1 IS NEVER THE SOLVE MESH. It is `BLOCKED`.** Written here explicitly so it is not
re-litigated: an instruction to "run the coarsest level" was issued on 2026-09-11 and refused,
because the coarsest level is the one member of the family the committed record declares
inadmissible.

**Not registered here:** any grid-convergence claim, any observed order, any GCI, any comparison to
an external dataset.

---

## 2. 🔴 PRECONDITION P1 — THE MESH HAS NO USABLE BOUNDARY PATCHES. NOTHING CAN SOLVE ON IT TODAY.

Measured by this lane on the committed L2 mesh:

> `constant/polyMesh/boundary` contains **exactly ONE patch: `defaultFaces`, type `wall`,
> nFaces 36,416** — and `log.plot3dToFoam` records *"Found 36416 undefined faces in mesh; adding to
> default patch defaultFaces"*.

**Plot3D carries no boundary-condition information, so the wing surface, the far field and the root
symmetry plane are all one `wall` patch.** A solver run on this mesh would treat the far field as a
no-slip wall and the symmetry plane as a wall. **This is not a tuning problem; the mesh is
structurally unusable for CFD as converted, and no mesh-quality gate detects it** — G-M1, G-M2 and
G-M3 all PASSED on this mesh.

**P1 is a gated precondition, not a chore.** Before any solve:
1. `defaultFaces` is split **by geometry**, not by face index, into `wing` (wall), `farfield` and
   `symmetry`.
2. **Predicted face counts, registered BEFORE the split so the split can be graded against them:**
   wing **11,136**, farfield **11,136**, remainder **14,144** of 36,416. *(Surface cells are 11,136;
   the inner and outer k-layers each carry one face per surface cell.)* **A split that does not
   reproduce 11,136 / 11,136 / 14,144 is `NOT A RESULT` and is investigated, not adjusted.**
3. **Geometric assertion, because face counts alone can be right for the wrong reason:** every
   `wing` face centre must lie within **|r| ≤ 4.3 mesh-units** of the body axis and every `farfield`
   face centre beyond **|r| ≥ 80 mesh-units**. Measured extents: wing tip y = 3.7666681523, farfield
   half-extent 84.8928.
4. **A planted control:** the splitter is first run with one known face relabelled and must report
   the mismatch, or its clean result is not evidence (rule 3).

**Until P1 passes, this rung is `BLOCKED` and no solver is launched.**

---

## 3. O1 — FLOW CONDITION. **A LAB CHOICE, AND LABELLED AS ONE.**

**There is no inherited condition and this document does not pretend otherwise.** §9B of the
predecessor established that **no wing-alone CRM force or `Cp` dataset exists on this box**;
Vassberg's design point is **Rn = 40 × 10⁶ for the wing/BODY**, and DPW's common condition is
**Re = 5 × 10⁶**, also wing-body. **Neither is a wing-alone anchor and neither is cited as one.**

| | registered value | basis |
|---|---|---|
| M∞ | **0.85** | **LAB CHOICE** — the CRM's design Mach, so the case is recognisably the CRM |
| Re, on `Cref` | **5 × 10⁶** | **LAB CHOICE** — DPW's common value, chosen for tractability, **explicitly NOT a validation anchor** |
| α | **2.0°, FIXED** | **LAB CHOICE** — a fixed angle, deliberately not a CL target, which needs an outer loop and is not costed here |
| `Cref` | **7.005320 m** | Vassberg Table 1, title-page verified in the predecessor |
| `Sref` | **383.6896 m²** | Table 1 row 1 — **NOT the 576,000 in² trap-wing area of row 2** |
| MRC | **(33.677860, 11.906250, 4.519930) m** | Table 1 |

🔴 **THE UNIT TRAP, AND IT IS SHARPER THAN THE PREDECESSOR STATED.** The mesh is in mesh-units with
**1 mesh-unit = 6.976368 m**. Therefore **`Cref` = 1.004150 mesh-units — NOT 1.0, and wrong by
0.415 %.** A reader who assumes unit chord because the number is close to one introduces a silent
0.415 % error into every coefficient. **Any script consuming this mesh asserts the unit system
against 6.976368 m before using any reference quantity**, per the predecessor's §8 rule 5, and
mesh-quality screens cannot catch a units error because they are scale-invariant.

## 4. O2 — SOLVER

**`rhoSimpleFoam`**, steady compressible RANS, **k-ω SST**, since M∞ = 0.85 is transonic and an
incompressible solver would be wrong by construction. **The predecessor's §1 rules that
`CRM_M085`'s solver ruling is NOT inherited**, so this is a fresh choice and is registered as one.

## 5. O3 — QoI: **REPORTED, NOT GATED**

`Cl`, `Cd`, `Cm` on `Sref` and `Cref` about the MRC. 🔴 **NO THRESHOLD BAND IS REGISTERED, because
no wing-alone reference data exists on this box (§9B).** Inventing a band would repeat `CRM_M085`'s
error of grading against nothing. **The QoI is reported with its iteration history; it is not a gate
and no `PASS` may rest on it.**

## 6. O4 — **NO ORDER BAND IS REGISTERED, AND THAT IS A FINDING, NOT AN OMISSION**

A `p` and a GCI need three admissible meshes. **This family has one.** So:
- **No `p ∈ [1.3, 2.5]`.** That band appears **in no standard and no charter**;
  **`docs/standards/MESH_STANDARD.md` HAS NO §9**, and the number 1.3 is **Celik's floor on the
  refinement RATIO, not a band on the observed ORDER** — a quantity confusion caught once already
  and not repeated here.
- **No `GCI < 3 %`.** It exists nowhere as a gate, and `VERIFICATION_CHARTER` §2bz records GCI of
  **129.33 %, 109.88 % and 71.70 % on rows that PASSED** because the percentage divides by a small
  `f_fine`. **If a GCI is ever registered for this geometry it states ABSOLUTE or RELATIVE
  explicitly, at Fs = 1.25, and is never quoted off non-monotone values.**

## 7. THE GATES THAT **CAN** FIRE ON ONE MESH — and they are the whole verdict

These need no second mesh and no external dataset.

| # | gate | threshold | verdict if breached |
|---|---|---|---|
| **G-S1** | initial residuals for `Ux Uy Uz e p k omega` | **all ≤ 1e-4** | `GATE FAIL` |
| **G-S2** | force plateau: max \|ΔCd\| over the **last 500 iterations**, expressed in drag counts | **≤ 1.0 count** | `GATE FAIL` |
| **G-S3** | realizability: **no negative `k`, `omega` or absolute temperature at any cell, any written time** | zero occurrences | `GATE FAIL` |
| **G-S4** | completion rule (rule 4), all clauses incl. the age guard | all hold | `NOT A RESULT` |

**G-S3's zero is planted:** the reader is first shown a field with a known negative inserted and must
report it, or its zero is refused (rule 3). **A zero from a reader not shown able to see a non-zero
is not evidence**, and this rung has already produced one such zero tonight in a different instrument.

## 8. O5 — COST, IN CORE-MINUTES, BEFORE IT RUNS

**Anchor, and its weakness stated:** the only steady-RANS anchor on this box is MRF R2 fine —
**2,418,780 cells**, still running after 5 h on 6 ranks. **It is a different solver
(`simpleFoam`, incompressible) on a different geometry**, so it bounds nothing tightly and is
labelled a weak anchor rather than hidden inside a point estimate.

| stage | ranks | est. wall s | **est. core-min** |
|---|---:|---:|---:|
| P1 patch split + verification | 1 | ~300 | **5** |
| `decomposePar` | 1 | ~120 | **2** |
| `rhoSimpleFoam`, 1.16 M cells, ~4,000 iterations | 4 | ~10,800 | **720** |
| `checkMesh` + post | 1 | ~120 | **2** |
| **total** | | | **~729 core-min** |

**Derived ≈ \$0.62** at \$0.0513/core-h — **DERIVED, NOT MEASURED**; this box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER` §5).

**CAP: 1,500 core-min.** ~2× the estimate, because the anchor is a different solver on a different
body. **An overrun STOPS the run; it does not get a new budget.**

**DISK, and this is the binding constraint tonight, not the cost.** A 1.16 M-cell compressible run
writing 8 fields at `writeInterval` costs roughly **0.25 GB per written time**. **Free space is
re-read IMMEDIATELY BEFORE LAUNCH and this rung does not start below 15 GiB**, and never while
another rung's single-shot final write is pending — **MRF fine needs 0.61 GiB at once and has no
partial-progress fallback; its 8,000 iterations are not this rung's to spend.**

## 9. WHAT THIS LANE HAS NOT VERIFIED

- **No solve has run.** Every number in §8 is an estimate against a weak, cross-solver anchor.
- **P1 has not been performed.** The predicted 11,136 / 11,136 / 14,144 split is arithmetic from the
  surface cell count, **not a measurement**, and is registered so that it can be graded rather than
  adjusted afterwards.
- **L2's mesh carries 170,728 cells with determinant < 0.001 and 20 face-tet errors** (committed
  `GATE_TABLE.md`). These are **not** registered mesh gates and L2 passed all five that are — but
  they are stated here because they bear on whether a transonic solve will converge, and a later
  reader should not discover them in a residual plot.
- **No claim is made that M∞ = 0.85 will converge on this mesh.** That is what G-S1 and G-S2 are for.

---

*Drafted 2026-09-11, pre-compute. Submissions parked; nothing here is sent, filed or registered
outside this box.*
