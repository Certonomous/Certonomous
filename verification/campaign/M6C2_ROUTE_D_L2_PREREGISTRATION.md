# M6C2 ROUTE (d) **L2** — SUCCESSOR RUNG, PRE-REGISTERED BEFORE COMPUTE

**Status: FROZEN BEFORE FIRST COMPUTE.** `verification/runs/M6C2_runs/ROUTE_D/L2/` **does
not exist** at this commit; the launcher tests for it and refuses if it does.

**This is a NEW RUNG, not an addendum to `M6C2_ROUTE_D_SNAPPY_PREREGISTRATION.md`
(`dc7f4cfd`).** That document registered **one level deliberately**, and its gates closed
at first compute. **An addendum cannot add a test.** So L2 is registered here, on its own,
in advance, and `dc7f4cfd` is left exactly as it stands.

---

## 1. WHY L2 IS THE RUN THAT DECIDES THIS

**Route (c) died at L2.** Its L1 reported **zero** over-gate faces; its L2 reported
**1,019**, with **99.41 % of them beyond r ≥ 2.0 m**.

**Route (d) L1 is PASS** — max non-orthogonality **48.884828** against a gate of 70, zero
severely non-orthogonal faces (`e9e6174d`). **That is exactly the evidentiary position
route (c) occupied before it was refuted.** Until route (d) is built at L2, we have
reproduced the precise state that misled this lab once already, and any confidence in
route (d) is confidence in a coarsest-level pass.

## 2. THE GATE — COPIED **VERBATIM** FROM `dc7f4cfd` §4, DELIBERATELY UNCHANGED

| # | quantity | gate | note |
|---|---|---|---|
| §3.1 | max non-orthogonality | **≤ 70°** hard | warning band 65–70 reported, not fatal |
| §3.2 | max skewness | **≤ 4** hard | **boundary faces INCLUDED** |
| §3.3 | max aspect ratio | **advisory at 1000** | **NEVER a lone rejection** |

Additionally fatal: **any negative-volume cell**, **any illegal face**, **a non-closed
mesh**.

**Copying the threshold verbatim is the point.** The L1↔L2 comparison means something only
if the threshold is identical at both levels, and a gate transcribed unchanged from a
document frozen before L1 ran cannot have been chosen to fit L2's answer.

**Concave cells remain OUTSIDE the gate at L2, exactly as at L1** — not because they do not
matter, but because changing the gate set between the two levels would destroy the
comparison. L1's 1,362 concave cells are reported in `e9e6174d` and L2's count will be
reported the same way. **Whether concave cells should be gated at all is a
`MESH_STANDARD` question, raised on two independent families now (route (d) L1 and
SUBOFF L2), and it is not settled inside this rung.**

## 3. WHAT L2 IS — A UNIFORM REFINEMENT BY EXACTLY 2, IN CELL LAYERS

**L2 = L1 with the background block doubled in every direction and EVERY refinement level
left unchanged.**

| | L1 | **L2** |
|---|---|---|
| background block | 66 × 32 × 64 | **132 × 64 × 128** |
| background cells | 135,168 | **1,081,344** |
| background cell size | 0.5 m | **0.25 m** |
| surface refinement | `(3 4)`, nose/crown/cap_nose `(4 5)` | **identical** |
| feature level | 4 | **identical** |
| `nearWing` region | level 2 | **identical** |
| domain extent | x[−13,20] y[0,16] z[−16,16] | **identical** |

Because snappy's refinement levels are **relative to the background cell**, halving the
background halves the cell size **everywhere** — far field and surface alike. **The
refinement ratio is therefore exactly r = 2.000 in cell layers, uniform across the
domain.** Nothing else changes: same STL, same `meshQualityDict` at OpenFOAM's untouched
defaults, same `snapControls`, `addLayers false`.

## 4. THE PREDICTION, STATED NUMERICALLY BEFORE THE BUILD

**Route (d) rests on the claim that route (c)'s defect was the MARCHING, not the body.**
Under route (d) the far field is undistorted background hexahedra, and **uniformly
refining hexahedra yields hexahedra** — there is no extrusion to accumulate distortion.

**I predict:**

1. **The r ≥ 2.0 m defect fraction STAYS LOW — below 10 %** (L1: 3.45 %). It does **not**
   climb toward route (c)'s 99.41 %.
2. **Max non-orthogonality stays below 65** — OpenFOAM's own default limit, which is
   **stricter than the §3.1 gate of 70** (L1: 48.884828).
3. **Severely non-orthogonal faces remain 0** (L1: 0).
4. **Concave cells roughly scale with cell count**, i.e. of order 10⁴ rather than 10³
   (L1: 1,362 in 152,399 cells = 0.89 %); **the FRACTION stays near 1 %.**

**WHAT WOULD FALSIFY ROUTE (d), stated so the outcome space is partitioned:**

- **r ≥ 2.0 m defect fraction > 50 %** → the far-field mechanism reproduces, and route
  (d)'s premise is refuted exactly as route (c)'s was.
- **max non-orthogonality > 70** → `GATE FAIL`; route (d) does not survive refinement, and
  L1's PASS was the coarsest-level artifact route (c) taught us to distrust.

**If either fires, route (d) is answered in the negative and NO L3 IS BUILT** — the same
discipline that stopped route (c) at L2 rather than building an L3 to confirm what was
already known.

## 5. LABELS, COMPLETION RULE, AND THE PLANT — INHERITED UNCHANGED

**`PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` exactly as defined in `dc7f4cfd` §5**;
the completion rule of `dc7f4cfd` §6 (rc captured **inside** the wrapper, `End` line per
stage, `constant/polyMesh` complete, `checkMesh` run to completion); and the **plant** of
§7 — the reader refused unless shown able to report a known over-gate value.

**The grading path is `grade_route_d.py`, frozen at `2b9f4581` BEFORE L1 ran, reused
UNMODIFIED and hashed against that blob before it grades L2.** A grader that predates both
levels cannot have been shaped by either.

**`checkMesh -allTopology -allGeometry` again** — more checks than the gate requires, so
anything the gate does not cover is still surfaced rather than hidden.

## 6. COMPUTE (rule 12) — NOW ANCHORED ON THIS CASE, NOT ANOTHER ONE

L1 **measured**: **0.73 core-min for 152,399 cells** = **4.79e-06 core-min per cell**.
(For context, `MRF_R2` measured 4.4e-06 core-min/cell on a 2,418,780-cell build — the two
agree to within 9 %.)

L2 delivers ~1.08 M background cells plus refinement; at ~1.25 M cells total:

| stage | ranks | **est. core-min** |
|---|---:|---:|
| `blockMesh` + `surfaceFeatureExtract` | 1 | ~0.3 |
| `snappyHexMesh` (~1.25 M cells @ 4.79e-06) | 1 | ~6.0 |
| `checkMesh -allTopology -allGeometry` | 1 | ~1.5 |
| **total** | | **~7.8 core-min** |

**Derived ≈ \$0.0067** at \$0.0513/core-h — **derived, not measured**.

**CAP: 30 core-min.** Beyond that the build **STOPS** and is reported at the core-minutes
spent.

**The cap is tighter than L1's 60 precisely because the anchor is better.** L1's estimate
missed by **16× in the over-direction** — I sized it from a ~1.0 M-cell target that the
refinement did not deliver, a **misprediction of delivered cell count, not contention.**
That error is corrected here by anchoring on L1's own measured cost per cell and by
predicting the delivered cell count from the background count, which is known exactly in
advance rather than guessed.

**Disk:** free is re-read immediately before launch; the build does not start below
20 GiB. (508 GiB free at registration; the floor is retained anyway — a floor that is
only present when it binds is not a floor.)

## 7. WHAT AN L2 PASS WOULD AND WOULD NOT ESTABLISH

A PASS at L2 would establish that route (d)'s admissibility **survives one uniform
refinement by a factor of 2** — the single thing route (c) failed to do. **It would not
establish grid convergence of any solution, nor admissibility at any resolution beyond
L2**, and **`M6C1` stays `BLOCKED`, route (c) stays `TERMINATED`, and M6 §A1.3 stays
`FALSIFIED` regardless of the outcome here.**

---

*Frozen 2026-09-11, before `ROUTE_D/L2/` exists. Submissions parked.*
