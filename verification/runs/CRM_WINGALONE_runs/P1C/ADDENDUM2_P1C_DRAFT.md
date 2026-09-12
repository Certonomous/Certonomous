# DRAFT — ADDENDUM 2 to `CRM_WINGALONE_FLOW_PREREGISTRATION.md` — ARM **P1C**

**NOT SIGNED. NOT COMMITTED. cfd-supervisor holds check 4.**
**APPEND TO THE `HEAD` BLOB, NOT THE WORKTREE COPY** — the worktree file is 236 lines against
HEAD's 384 and would destroy ADDENDUM 1 on write-back.

## A2.1 THE FINDING — THE INSTRUMENT MEASURED A DIFFERENT QUANTITY FROM THE ONE §2 REGISTERS

§2 clause 3 registers, verbatim: *"every `wing` face centre must lie within **|r| ≤ 4.3
mesh-units** of the body axis and every `farfield` face centre beyond **|r| ≥ 80 mesh-units**."*

`split_patches_p1b.classify()` computes `r = sqrt(cx²+cy²+cz²)` — **distance from the ORIGIN**, for
BOTH clauses. For the farfield clause that is right. **For the wing clause it is the wrong
quantity**, and on a 30°-swept planform the two diverge exactly at the tip trailing edge, where x and
y are large together.

## A2.2 THE FACES ARE LEGITIMATE WING FACES — DECIDED FROM THE GEOMETRY

| measurement | value |
|---|---|
| max wing \|r\| from ORIGIN | **4.9810** (the P1B `GATE FAIL`) |
| max wing distance from the BODY AXIS, `sqrt(y²+z²)` | **3.7809** |
| min farfield \|r\| from origin | **80.4423** |
| `classify()`'s own wing/farfield split | `r > 40.0` |
| separation, in the quantity `classify()` actually splits on | **16.1×**, and **no face lies between 4.9810 and 80.4423** |
| wing patch bounding box | x [0.0104, 3.2471] y [0.0125, 3.7666] z [−0.1997, 0.3460] |

The 3,374 exceeding faces are **contiguous at the tip trailing edge** (y ≥ 3.1724 against a tip at
y = 3.7666681523), lie **inside the wing's own bounding box**, and sit **16.1× away from the nearest
farfield face**. They are wing.

**THE CONDITION UNDER WHICH 4.3 WOULD HAVE BEEN LEFT ALONE AND THE CLASSIFIER FIXED INSTEAD:** any
exceeding face approaching the 40.0 classifier boundary, or lying outside the wing bounding box, or
the exceedances being scattered across the patch rather than tip-localised. **Measured: none holds.**
Had any held, the split would have been mixing farfield into wing and the gate would stand.

## A2.3 THE FIX — THE QUANTITY IS CORRECTED, **NO THRESHOLD IS MOVED**

- **Wing assertion** computes `sqrt(y²+z²)`, distance from the body axis, as §2's text says.
  **Threshold stays 4.3. UNCHANGED.**
- **Farfield assertion** unchanged: `|r|` from origin **≥ 80**. It passed (80.4423) and its quantity
  is the one §2's text gives it.
- **`classify()` UNCHANGED.** Its `r > 40.0` origin-distance split is correct and has 16.1×
  separation. Distance from the body axis must **NOT** be used to classify: min farfield
  body-axis distance is **0.9015** (a farfield face directly up/downstream sits near the axis), so
  that quantity does not separate the patches and would break the split.

**No gate, threshold, cap or label is altered by this addendum.** It corrects an instrument to
compute the gate that is already frozen.

## A2.4 PREDICTION FOR P1C — AND IT IS **NOT A BLIND ONE**, STATED SO

symmetry **14,144**, wing **11,136**, farfield **11,136**, max wing body-axis distance **≤ 4.3**,
min farfield \|r\| **≥ 80**.

🔴 **THE WING FIGURE IS ALREADY MEASURED AT 3.7809** by a diagnostic that changed no gate. **P1C is
therefore a CONFIRMATION under the corrected instrument, not a discovery, and this prediction is not
blind.** Recorded here rather than presented as foresight it does not have.

## A2.5 WHAT IS AUTHORISED

**Authorised after check 4:** one run of `P1C/split_patches_p1c.py` on L2, graded against §2's
unchanged counts and unchanged thresholds; **and the WRITE of the three patches into
`constant/polyMesh/boundary`**, which A1.6 did not authorise and which no arm has yet performed —
the mesh still carries exactly one `defaultFaces` patch.

**NOT authorised and NOT altered:** §2's counts and thresholds; §7's gates and their registered
order; the solver rung; any flow result; any grid-convergence claim.

*Drafted by a cfd `lab-lane`. Submissions parked. No agent's message is Sanaa's consent.*
