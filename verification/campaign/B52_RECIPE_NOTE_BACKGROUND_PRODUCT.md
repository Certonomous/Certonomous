# B-52 recipe note — the background-cell product does NOT control the delivered cell count

**Written 2026-08-10 on chief ruling (2) of the entry-4 outcome, commit
`1a0e9a37`:** the G1 refusal in `B52_RUNG6_REPLICATE_RESULTS.md` §4 is a finding
in its own right and belongs where a future mesh author will meet it.

**Read this before choosing a `blockMeshDict` division triple for any
snappyHexMesh ladder rung or replicate in this lab.**

---

## The rule of thumb that does not work

The natural way to pick a division triple for a target resolution — and the way
this arm's pre-registration picked one — is to hold the **background-cell
product** `nx · ny · nz` near constant, on the reasoning that the background
lattice sets the cell budget and snappy scales from it.

**Measured on four draws of one recipe at one rung, it does not:**

| draw | divisions | product | product Δ | **delivered cells** | **cells Δ** | cells / product |
| --- | --- | --- | --- | --- | --- | --- |
| finer2 (rung 6) | (51 45 75) | 172 125 | — | 330 950 | — | **1.9227** |
| 6b | (52 44 76) | 173 888 | +1.02% | 335 305 | +1.32% | **1.9283** |
| **6c attempt 1** | **(50 46 75)** | **172 500** | **+0.22%** | **352 596** | **+6.54%** | **2.0440** |
| 6c attempt 2 | (52 45 74) | 173 160 | +0.60% | 333 217 | +0.68% | **1.9243** |

**The draw with the product closest to the original delivered the cell count
furthest from it.** (50 46 75) is +0.22% in product — the best match of any
candidate, which is exactly why the pre-registration named it — and +6.54% in
delivered cells, six and a half times its own product error and three times
outside the ±2.0% admission band. It was refused by G1 before any solver
launched.

## What the numbers actually say

**The cells-per-background-cell ratio is piecewise constant with a step, not a
slope.** Three of the four draws agree to **0.3%** (1.9227, 1.9243, 1.9283).
The fourth jumps **+6.3%** to 2.0440. There is no smooth trend to interpolate;
there is a plateau and a step off it.

**The rung-7 pair looked well controlled by luck, not by design.** The
`W3_MESH_NOISE_FLOOR_RESULTS.md` replicate that the whole 1.91 × 10⁻³ floor rests
on — rung 7 (55 49 82) → 441 057 vs rung 7b (56 48 83) → 441 079, famously
"22 cells apart, 0.005%" — got there by **two roughly 1% errors cancelling**:
the product rose +0.96% while the cells-per-product ratio fell −0.94%
(1.9958 → 1.9770). Neither was controlled. The pair was not evidence that the
generator repeats itself; it was one draw of a coin that happened to land twice
the same way.

## The mechanism — stated as a hypothesis, because four points do not prove one

The distinguishing feature of the outlier is that it is the only draw with
`ny = 46`, and the only one where the background cell is strictly shortest in y:

| draw | dx | dy | dz | shortest edge |
| --- | --- | --- | --- | --- |
| finer2 | 6.551 | 6.467 | 6.467 | 6.467 (dy = dz) |
| 6b | 6.425 | 6.614 | 6.382 | 6.382 (dz) |
| **6c #1** | 6.682 | **6.326** | 6.467 | **6.326 (dy, alone)** |
| 6c #2 | 6.425 | 6.467 | 6.554 | 6.425 (dx) |

(Domain 334.124 × 291.000 × 485.000; recipe `nearBody` shell level 2, surface
levels (3 4), so the refined cell at level *L* is the background cell halved
*L* times.)

**Hypothesis:** the count is dominated by the surface-refined cells, whose size
comes from the background cell **edges**, not from the background cell **count**.
A draw that shrinks one edge enough to pull an extra layer of cells inside the
`nearBody` refinement shell adds that layer all at once, which is a step.

**It is a hypothesis and it is not established here.** Against it: the shortest
edge shrinks by 1.32% on 6b and 0.65% on 6c #2, and the cells rise by 1.32% and
0.68% — a clean 1:1 — but shrinks by 2.18% on 6c #1 and the cells rise 6.54%, a
ratio of 3. So "shortest edge" predicts three of four draws and fails on the one
that matters. **The step is measured; its cause is not.**

**The cheap test that would settle it**, if anyone needs the mechanism: mesh
(50 45 75), (50 46 76) and (51 46 75) and read `log.snappyHexMesh`'s
castellation cell counts per refinement level. Three meshes, no solves, ≈3.3
core-min at this rung. Nobody needs to run it to use the rule below.

## The rule that does work

1. **Do not choose a replicate or rung by matching the background product.** It
   is not the control variable, and matching it well can miss the delivered
   count badly.
2. **Mesh first, read the achieved cell count from `log.checkMesh`, and admit or
   re-draw against a stated band — before any solver launches.** This is exactly
   what gate G1 of `B52_RUNG6_REPLICATE_PREREGISTRATION.md` §6 does, and it is
   the only thing in this note that is guaranteed to work regardless of which
   mechanism is right. A re-draw at that stage is experiment design, not tuning:
   meshing produces a cell count, not a force, so no result exists to tune
   toward (the rung-7 attempt-1/attempt-2 precedent).
3. **Budget for the re-draw.** One in two draws missed a ±2.0% band here. At
   ~1.1 core-min per rung-6 mesh that is cheap; at rung 8 (836 136 cells, 3.15
   core-min) it is less so, and at a rung where meshing is the expensive part it
   should be priced into the arm up front rather than discovered.
4. **Never report two draws as "the same resolution" on the strength of their
   divisions.** Report the delivered cell counts. Rung 7 and rung 7b are 0.005%
   apart in cells and that fact had to be *measured*; it could not have been
   predicted from (55 49 82) and (56 48 83).

## Where this came from

| | |
| --- | --- |
| arm | `B52_RUNG6_REPLICATE_RESULTS.md` §4 (G1), pre-registration `5c6825c7`, results `e40eceb3` |
| chief ruling | entry 4 outcome, `SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`, commit `1a0e9a37`, ruling (2) |
| the rung-7 pair | `W3_MESH_NOISE_FLOOR_RESULTS.md` §4 |
| division triples and delivered counts | each case's own `log.checkMesh`; certificates in `B52_RUNG6_REPLICATE_runs/` |
