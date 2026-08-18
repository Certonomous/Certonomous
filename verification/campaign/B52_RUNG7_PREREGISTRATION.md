# B-52 seventh rung — pre-registration

**Written 2026-08-02 05:23 UTC, after meshing (checkMesh 05:21:15 UTC) and
before the solver was launched (05:23:19 UTC).** The mesh exists and its cell count is stated below;
**no drag coefficient has been computed on it.** Meshing produces a cell
count, not a force, so fixing the refinement ratio at this point is experiment
design, not tuning.

Item: `agp-880b4f92bdc5`, "Add a 7th refinement rung to the B-52
Stratofortress-class airframe grid ladder", `est_core_min` 20.0, approved
2026-07-31T22:18:09Z.

---

## 1. What this rung is and is not

It is **not** an attempt to make the B-52 ladder converge. The record already
establishes that it does not:

* the ladder's valid family (`models/curriculum/uq-studies/b52.json`,
  `recipe_audit`) is 135 779 / 193 880 / 255 358 / 330 950 cells at Cd
  0.049053 / 0.047196 / 0.049573 / 0.052275;
* successive increments are −0.001857, +0.002377, +0.002702 — they **grow**
  with refinement, which is the opposite of asymptotic behaviour, and
  `increment_trend` and `extrapolation_sanity` both fail;
* iterative error was ruled out as the cause: `b52.json` `iterative_audit`,
  measured 2026-07-31T14:20:00Z from each rung's own
  `postProcessing/forceCoeffs1/0/coefficient.dat`, gives final-window 2σ of
  1.07 × 10⁻⁵ (fine-uq) and 2.25 × 10⁻⁶ (finer2) against a 2.702 × 10⁻³
  increment — two to three orders of magnitude below what it would have to
  explain.

So this rung **measures how much further the divergence runs**, and whether it
runs at a constant rate. That is the honest description of the experiment. A
seventh rung cannot rescue a ladder whose increments grow; it can say whether
the growth continues, flattens, or turns.

## 2. The mesh, and the one knob that moved

Recipe held fixed at the production/fine-uq/finer2 recipe: `nearBody`
refinement-shell level 2 (max overall cell level 4), `refinementSurfaces`
`body { level (3 4); }`, `b52.eMesh` feature level 3, kOmegaSST, magUInf 100,
`lRef` 48.5, `Aref` 600.598, `rhoInf` 1.225, 300 iterations. The case was
copied verbatim from `/home/ubuntu/certonomous-runs/study-b52-finer2-uq`
(`constant/triSurface/b52.stl` md5 `c27eec6c710f0a937ec8cfe84aec2cfe`,
identical to finer2's), and the pristine `0.orig` fields were taken from
`/home/ubuntu/certonomous-runs/study-b52-030bc9/0.orig` after checking that
its `k`, `p`, `nut` and `omega` are byte-identical to finer2's pre-solve `0/`
copies. **Only the background blockMesh division triple differs.**

| attempt | divisions | cells (checkMesh, measured) | h-ratio vs finer2 | mismatch vs family r = 1.0904 | mesh |
| --- | --- | --- | --- | --- | --- |
| 1 | (57 50 84) | **467 287** | 1.1221 | 2.91% | OK, max skewness 3.911 |
| 2 (**used**) | (55 49 82) | **441 057** | 1.1006 | **0.94%** | OK, max skew 3.535, max non-orth 64.641 |

Attempt 1 was re-meshed for the same reason R4 re-meshed its c3: the snappy
cascade is nonlinear in the background density, so the achieved ratio is
measured rather than chosen, and 2.91% is outside the ≤3% the lab's own
constant-ratio work holds itself to while 0.94% is comfortably inside it. **No
Cd existed on either mesh when the decision was made**, and both counts are
recorded here. Attempt 1's `log.checkMesh` was overwritten by the re-mesh
(`mesh.sh` clears `log.*`); its count 467 287 was read from that log at
05:19:32 UTC and is reproducible by setting the divisions back to (57 50 84).

Mesh quality is not drifting with refinement: max non-orthogonality 64.641
here against finer2's 64.647 and fine-uq's 57.716; max skewness 3.535 against
3.999 and 3.966. So a quality cliff is not available as an explanation for
whatever this rung reports.

**Rank count: 2 MPI ranks, hierarchical `n (2 1 1)`, identical to fine-uq and
finer2** — `system/decomposeParDict` copied unchanged from finer2. This is
deliberate and it costs wall-clock on an idle 16-core box. The two increments
that carry the divergence signal end on rungs solved at 2 ranks; decomposition
perturbs a steady SIMPLE solve at the linear-solver tolerance level, so a
rung-varying rank count would put a decomposition artefact directly into the
increment this rung exists to measure. **220 529 cells per rank.**

## 3. Cost, estimated before the fact

Meshing, measured: 77 s wall for attempt 2 (05:20:00 → 05:21:15, single core)
plus 119 s for attempt 1 = **3.3 core-minutes**, both at 1 core.

Solve, estimated: finer2 ran simpleFoam in 285 s wall on 2 ranks (04:29:50 →
04:34:35, `driver.log`) = 9.50 core-minutes at 330 950 cells. Holding
iterations at 300 and scaling linearly by cells (× 1.3327) predicts **380 s
wall, 12.7 core-minutes at 2 ranks**. With meshing and the serial
potentialFoam/decomposePar steps the item is predicted at **≈16.5
core-minutes against `est_core_min` 20.0.** Measured cost is reported whatever
it turns out to be.

## 4. Gates, fixed now

**G1 — constant ratio.** Achieved h-ratio within 3% of the family's 1.0904.
*Already met at 0.94% (§2). Recorded before solving so it cannot be claimed
after.*

**G2 — the rung is settled.** Final-window 2σ on the Cd history must be below
5% of |Cd| (the ceiling `run_uq_studies.b52_fourth_rung` applies before it
will store a rung) **and** below 10% of the new increment. The second is the
one that matters: fine-uq and finer2 were settled to 1.07 × 10⁻⁵ and
2.25 × 10⁻⁶ at the same fixed 300 iterations, and whether a 33% larger mesh is
still settled at a cap that never moved with cell count is exactly the defect
`w5-tmr-iteration-caps-are-guesses-not-measurements` names. **If G2 fails the
rung is not ladder evidence and will not be stored as one** — the failure is
then the finding, and it is a finding about the fixed cap, not about the flow.

**G3 — the question.** Refit `uq.eca_hoekstra_band(dim=3)` on the valid
family extended to five rungs (135 779 / 193 880 / 255 358 / 330 950 /
441 057). The fit takes the finest three, so it will read
255 358 / 330 950 / 441 057.

**G4 — falsifiable prediction, on the record before the solve.**
The last two increments are +0.002377 and +0.002702, a growth factor of 1.137
per rung at r ≈ 1.09. If the divergence continues at that rate the next
increment is ≈ +0.00307 and **Cd(441 057) ≈ 0.0553**.

**Predicted: Cd rises again, to between 0.0535 and 0.0575, and the third
successive increment is larger than +0.002702.** If Cd instead falls, or the
increment shrinks, the divergence is not a constant-rate one and the ladder
has a turning point between 330 950 and 441 057 cells — which would be a
different finding and a more interesting one. **Either outcome is reported as
written; neither is a failure.**

**G5 — what will NOT be claimed.** Whatever this rung reads, the ladder will
not be called conclusive or asymptotic on the strength of one more rung, and
`uq.reportable_band` will be read rather than `band_abs`. A fifth rung in a
family whose increments grow does not earn an order.

*Nothing below this line existed when the solver was launched.*
