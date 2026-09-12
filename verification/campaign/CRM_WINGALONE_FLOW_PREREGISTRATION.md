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

---

## 10. FREEZE BLOCK — **PREPARED BY THE LANE, SIGNATURE FIELD DELIBERATELY BLANK**

🔴 **THIS DOCUMENT IS NOT YET FROZEN. It becomes frozen when cfd-supervisor signs the row below,
and not before.**

**Why the lane did not sign it.** `CLAUDE.md:240` — *"the four §3 checks are done **personally and
may never be delegated** … pre-registration **committed** before compute. A relayed check is a
summary, not a check."* **Verifying that a pre-registration is committed before compute is check 4,
and it is the supervisor's own.** A lane that signs it has converted the check into a relay, which
is the one thing the rule names. **The instruction to "freeze it" was an instruction to prepare the
freeze; the attestation itself is not transferable.**

### 10.1 Conditions verified BY THE LANE, each with a live control

| condition | state | control that makes it evidence |
|---|---|---|
| `verification/runs/CRM_WINGALONE_FLOW_runs` | **ABSENT** | the same `test -d` was first shown to SEE `verification/runs/CRM_WINGALONE_runs`, which exists |
| predecessor frozen blob | first 37,613 bytes hash **`1fa5fb725e6298d99dc4ab2207f55f11e575b285`** | identical to `git rev-parse d2629d326:<path>`; **0 commits touch it after `cbacda6b3`** |
| this draft, as committed | `8527228a9`, 193 lines | committed **before** any compute under it |
| L2 patch state | **one patch, `defaultFaces`, wall, 36,416 faces** | read from `constant/polyMesh/boundary`; corroborated by `log.plot3dToFoam`'s own *"Found 36416 undefined faces"* |

**No compute has run under this document.** P1 is compute and is held until the row below is signed.

### 10.2 The signature row

| field | value |
|---|---|
| frozen by | **cfd-supervisor, PERSONALLY, 2026-09-11T23:28:03Z — check 4 performed by me, not relayed** |
| freeze commit sha | *the commit that carries the signature* |
| grading path fixed at | **P1: `split_patches.py` graded against §2's counts predicted in advance; the solve: `checkMesh`, solver residual logs and force history, read by printed values, never by rc** |
| date | *to be filled at signature* |

### 10.3 🔴 WHAT THIS FREEZE WILL NOT CERTIFY, STAMPED IN ADVANCE

- **It does not certify that P1 will succeed.** §2's 11,136 / 11,136 / 14,144 is **arithmetic from the
  surface cell count, not a measurement.** If the split returns other numbers that is a finding to
  investigate, **never a licence to adjust the prediction to fit.**
- **It does not certify `split_patches.py`.** That instrument is subject to **check 1 — the
  supervisor's own read, as a diff — and no number it produces is believed before that.**
- **It certifies no flow result.** No solve has run and none is authorised by this freeze.

### 10.4 CHECK 1 PERFORMED PERSONALLY BY cfd-supervisor — `split_patches.py` IS **NOT** CLEARED

**The freeze below is signed. P1 REMAINS HELD, on check 1, not on check 4.**

I read `verification/runs/CRM_WINGALONE_runs/P1/split_patches.py` in full, as source, myself.
Three parts are sound and stay: the classifier band (faces are split at r > 40 while the
assertions demand wing <= 4.3 and farfield >= 80, so anything landing in the 4.3-80 gap FAILS
rather than being silently absorbed); the refusals on a missing `defaultFaces` and on
`nFaces != 36416`; and the registered counts as named constants a later reader can see were moved.

🔴 **THE PLANTED CONTROL IS A NO-OP AND MUST BE REBUILT BEFORE P1 RUNS.** As written it does this:

    tampered = list(labels); tampered[victim] = "wing"
    detected = any(tampered.count(k) != EXPECT[k] for k in EXPECT)

It relabels an entry in a **copy of the output list** and then counts that list. **It never
re-runs `classify()`.** So it tests that changing one element of a list changes its tally --
arithmetic, not a reader. **`detected` is true for every possible input:** if the real counts
match, flipping one farfield to wing makes 11137/11135 and differs; if they already mismatch, it
differs anyway. **A control that cannot return the other answer proves nothing**, and this one
would have printed *"CONTROL PASSED -> the comparison above is evidence, not a blind read"* over a
test that exercised no part of the instrument under test.

**REQUIRED FIX:** plant in the **INPUT**, not the output -- perturb one face's coordinates in
`coords` so that face genuinely belongs to a different class, **re-run `classify()` on it**, and
require the classifier to report the new class. Then restore and re-run clean. **The control must
be shown able to FAIL**: demonstrate it refusing when the plant is deliberately not applied.

**This is the same defect the lab hit three times tonight in other costumes** -- a reader not shown
able to see a non-zero, a durability checker that answers "ignored" to everything, an fd sweep
whose control proved only that it followed symlinks. **The gap is always between "my control
passed" and "my control exercised the thing being measured."**

---

## ADDENDUM 1 — 2026-09-12 — **ARM P1B REGISTERED. A NEW SYMMETRY TOLERANCE, ON A PLATEAU RE-DERIVED FROM THE MESH. P1's `GATE FAIL` IS STRUCK BUT STANDS LEGIBLE AND IS NOT REHABILITATED.**

**lines whose number changed above this section: 0.** No gate, threshold, cap, band or label above
this line is altered. §2's registered counts **11,136 / 11,136 / 14,144** are untouched; §2's
geometric assertions **|r| ≤ 4.3** and **|r| ≥ 80** are untouched; §3–§9 are untouched; the §10.2
signature and the §10.4 check-1 finding are untouched.

**Authorised by the cfd-supervisor's ruling of 2026-09-12, under its four stated conditions.**
**No compute has run under THIS addendum: the corrected split is NOT re-run until check 4 on this
commit is discharged.**

### A1.1 🔴 CONDITION 1 — P1's `GATE FAIL` IS STRUCK, PRESENT AND LEGIBLE

~~P1, arm 1, `Y_SYMM_TOL = 1e-9`: symmetry 13,312 against a registered 14,144; wing 11,908 against
11,136; farfield 11,196 against 11,136; max wing |r| 38.3271 against ≤ 4.3; min farfield |r| 40.9425
against ≥ 80. **`GATE FAIL`.**~~

**That result is STRUCK, not deleted, and it is NOT described as wrong.** It is a true fact about
that mesh under the tolerance as frozen. **P1 reported honestly against the instrument it was given;
the instrument's tolerance was the defect.** The struck text stays because a reader who cannot see
the original cannot audit the correction.

**P1B DOES NOT INHERIT P1's IDENTITY.** It is a separate arm, separately registered, separately
graded, in its own directory `verification/runs/CRM_WINGALONE_runs/P1B/`.

### A1.2 CONDITION 3 — THE FALSIFIER, WRITTEN **BEFORE** THE MEASUREMENT

**`verification/runs/CRM_WINGALONE_runs/P1B/PREDICTION_BEFORE_SWEEP.md`, written 2026-09-12T02:05:36Z,
sha256 `eee81c3bf1932dbc21dad39dea84282bf47acec11aa0c6c91adaea058dd04e56`, BEFORE `band_sweep.py` was
executed even once.** It names three results, any one of which leaves `Y_SYMM_TOL = 1e-9` exactly
where it is:

- **A — NO PLATEAU.** A count creeping monotonically with the band has no natural stopping point;
  every tolerance is then a choice, 1e-9 is as defensible as any, and P1's `GATE FAIL` stands as a
  real geometric finding that the root plane is not planar.
- **B — A PLATEAU AT THE WRONG COUNT.** Flat at anything other than 14,144 means the tolerance story
  and the independent block-topology prediction **disagree**; the action is to investigate, never to
  move the tolerance.
- **C — A PLATEAU TOO COARSE TO BE PHYSICAL.** A displacement comparable to a near-wall cell rather
  than round-off makes a `symmetryPlane` BC ill-posed, and the repair is the mesh, not the tolerance.

### A1.3 THE RE-DERIVATION — FROM THE POLYMESH, NOT FROM P2's TABLE

**A tolerance registered on a cited table is a tolerance registered on somebody's summary.**
`P1B/band_sweep.py` re-reads `L2/foam/constant/polyMesh` (patch `defaultFaces`, nFaces 36,416,
startFace 3,456,224) and re-derives the sweep independently. Full output: `P1B/log.band_sweep_L2`.

| band on max\|y\| | root-plane faces | max\|y\| in band |
|---:|---:|---:|
| 1e-9 … 1e-7 | **13,312** | 0.000000e+00 |
| 1e-6 | 13,728 | 4.416540e-07 |
| **1e-5** | **14,144** | **9.491133e-06** |
| **1e-4 … 1e0** | **14,144** | **9.491133e-06** |
| 1e+1 | 14,231 | 3.766668e+00 |
| 1e+2 | 14,296 | 8.514650e+01 |

**All three pre-written predictions hold, and the plateau is BROADER than P2 reported — SIX decades
(1e-5 to 1e0), not four.** The plateau max\|y\| reproduces P2's **9.491133e-06** to seven significant
figures by an independent reader. **A, B and C are each refuted:** the plateau exists and is flat over
six decades (¬A); it sits at exactly 14,144, the block-topology prediction (¬B); and 9.491133e-06
mesh-units × 6.976368 m = **6.6214e-05 m = 0.0662 mm**, round-off scale and orders below any near-wall
cell (¬C).

### A1.4 CONDITION 2 — THE REGISTERED VALUE AND ITS DERIVATION

> **`Y_SYMM_TOL` for arm P1B = `1.0e-3` mesh-units.**

**Derivation, from the gap the sweep measures and not from the count it produces:** the largest
root-plane displacement is **9.491133e-06** and the smallest non-root-plane \|y\| is **3.766668**
— a gap spanning a factor of **396,862**. The registered value sits **105.4× above** the last
root-plane face and **3,767× below** the first contaminant. **Both margins are stated so a reader can
see the value is not perched near either edge.** *(The gap's geometric centre is 5.979e-03; 1.0e-3 is
chosen instead because it is the value P2 named, so two independent records agree on one literal, and
its margins are already three orders on both sides.)*

**What makes this a measurement and not a fit** — the supervisor's ruling, adopted here: **P2 could
have come out the other way and once did.** Its 0.48 m non-planarity alarm was raised and then
**withdrawn on evidence**. An instrument that has demonstrably produced an alarming answer and
retracted it on further evidence is not an instrument bent toward a wanted verdict.

### A1.5 🔴 A DEFECT IN THIS LANE'S OWN PLANT, CAUGHT BY ITS OWN CONTROL, RECORDED BECAUSE IT IS THE LESSON

**`band_sweep.py`'s first planted control REFUSED, and it was right to.** It displaced ONE root-plane
face's vertices and required exactly that face to leave the tighter band. **On a conformal mesh the
vertices are SHARED**: the plant moved **six** faces out of the 1e-5 band and **three** out of 1e-3,
and rotated neighbours enough to move the \|n_y\| candidate count by 3 — so the discrimination control
fired and the instrument exited 2 rather than reporting a count.

**A plant whose blast radius is not known cannot have a predicted response, so it cannot
discriminate.** The repair is a **rigid y-translation of all 36,418 vertices**, whose response is
exactly predictable: bands below the displacement must empty, bands above must recover the clean
count, and — because a translation rotates nothing — **the candidate count must be bit-unchanged**.
Measured: 1e-5 band **14,144 → 0**; 1e-3 band **14,144 → 14,144**; candidates **14,296 → 14,296**;
restored exactly. **The refusal is kept in the record: it is the control working, not a false start.**

### A1.6 WHAT IS AUTHORISED, AND WHAT IS NOT

**Authorised by this addendum, AFTER check 4 on the commit carrying it:** one run of the corrected
splitter on L2 as arm **P1B**, at `Y_SYMM_TOL = 1.0e-3`, graded against §2's **unchanged**
11,136 / 11,136 / 14,144 and §2's **unchanged** \|r\| assertions.

**NOT authorised and NOT altered:** §2's counts and radius gates; the solver rung; any flow result;
any grid-convergence claim. **A P1B pass does not make P1 pass, and does not by itself authorise the
solve** — §7's gates are untouched and are reached in their registered order.

**PREDICTION FOR P1B, REGISTERED HERE BEFORE IT RUNS:** symmetry **14,144**, wing **11,136**,
farfield **11,136**, max wing \|r\| **≤ 4.3**, min farfield \|r\| **≥ 80**. **If the counts come right
and the radius assertions still fail, that is a finding about the classifier's radius band and NOT a
licence to move it** — the radius gates are frozen and this addendum cannot alter them.

*Arm P1B registered 2026-09-12 by a cfd `lab-lane` under the cfd-supervisor's ruling. Submissions
parked. No agent's message is Sanaa's consent.*
