# B-52 eighth rung — pre-registration

**Written 2026-08-07 ~20:35 UTC, before any eighth-rung mesh exists.** No
blockMesh has been run, no cell count exists, no Cd exists. Proposal:
`b52-eighth-rung-with-the-alternative-preregistered` (approved under Katie's
blanket approval 2026-08-05, slate rank 2), which makes docket item
`agp-1dec50b65c2f` launchable.

## 1. What is already known at the time of writing, stated so the record
cannot be accused of following the answer

The proposal pre-registered its mechanism hypothesis on 2026-08-05 (commit
9ee82a35), before any surface measurement existed: *the recipe scales the
background blockMesh divisions while holding `near_body_shell_level` 2 and
`max_cell_level` 4, so surface resolution may be flat while total cells
nearly double, and a ladder whose refinement does not reach the integration
surface cannot produce an observed order.*

In the course of locating the seven rung meshes for this session (before this
document was written), the aircraft-patch (`body`) surface **face counts**
were read from each rung's own retained `log.checkMesh` / `polyMesh/boundary`:
931, 1825, 6098, 7533, 9395, 11621, 13688 at 40,656 / 107,489 / 135,779 /
193,880 / 255,358 / 330,950 / 441,057 total cells. That exposure is declared
here rather than hidden. What has NOT been computed at the time of writing:
any surface cell **size** (min or mean), any per-rung area, and any scaling
fit of faces against cells. The verdict on the mechanism hypothesis is
declared below as arithmetic on numbers not yet computed, with the decision
rule fixed first.

## 2. Verdict 1 (zero compute) — decision rule, fixed now

For each rung: `body` patch face count n_f, patch area A (exact from the
retained meshes; the three unretained early meshes share the identical
`b52.stl`, so A is taken from the retained meshes' measured area), mean
surface face size sqrt(A/n_f), and min face size where the mesh is retained.

Uniform refinement at fixed relative levels predicts n_f ∝ N^(2/3) (N = total
cells). Decision rule on the valid family (135,779 → 441,057 cells, the five
same-recipe rungs): fit the exponent b in n_f ∝ N^b.

- **b < 1/3**: surface resolution is flat-or-near-flat while cells double —
  the proposal's mechanism is REAL and is the primary result.
- **b in [0.55, 0.80]**: the recipe DOES refine the surface like uniform
  refinement — the mechanism hypothesis is REFUTED for the cost of reading
  six meshes, and the eighth rung's number stands on its own.
- between: partial refinement, reported as measured, with the mean-size trend
  deciding whether the surface h actually falls rung over rung.

## 3. Verdict 2 (the rung) — pre-registered before meshing

**Mesh:** same recipe, `system/` copied verbatim from
`/home/ubuntu/certonomous-runs/study-b52-rung7-uq` with only `blockMeshDict`
changed: background divisions (55 49 82) → **(69 62 103)** (each scaled by
2^(1/3) = 1.2599, rounded), targeting roughly 880,000 cells. Note stated in
advance: this is a **cell-count doubling**, h-ratio ≈ 1.26 vs rung 7, a
deliberate departure from the family's constant r ≈ 1.09 — the proposal
prices the doubling explicitly, and the Eca–Hoekstra fit does not require
constant r. The achieved count is measured, not chosen; it will be recorded
whatever it is.

**Solve:** 2 MPI ranks, hierarchical n (2 1 1), potentialFoam -writephi
initialisation, 300 iterations, kOmegaSST, magUInf 100 — every setting
identical to rung 7 by verbatim copy. Native openfoam2606, exactly as every
prior rung ran (the box currently carries one unrelated container; this run
uses 2 cores, matching the fleet-budget cap).

**Cost, estimated before the fact:** rung 7 measured 12.14 core-min total at
441,057 cells; doubling cells at fixed iterations predicts **≈24–25 core-min
against the docket's 20** — the overrun is the iteration-count term the
proposal's own cost_basis names as unpriced. Measured cost is reported
whatever it is.

**Prediction, and the repeat-bet trap named:** rung 7 pre-registered "Cd
rises again" and scored FALSE (it fell, −0.004055, the largest increment in
the family). A second monotonicity bet would learn nothing from a second
miss. The measured mesh-construction noise floor is 1.91e-3
(`W3_MESH_NOISE_FLOOR_RESULTS.md`: rung7 vs rung7b, 53× the iterative noise).
**Predicted: Cd(≈880k) lands inside the valid family's existing span
[0.0472, 0.0523], the refit through `uq.eca_hoekstra_band(dim=3)` stays
`monotone: false`, `conclusive: false`, no observed order is fitted, and the
eighth rung neither rescues nor worsens the ladder — the ladder's scatter is
mesh-construction noise, not a converging or diverging sequence.**
Pre-registered alternative: if Cd lands OUTSIDE that span, the ladder is
still travelling and the divergence outruns the noise floor — a different
and stronger finding, reported as written. Either way `conclusive` is
recorded as it falls, not clamped, and `uq.reportable_band` is read rather
than `band_abs` (rung 7's G5, carried forward).

**Settle gate (rung 7's G2, carried forward):** final-window 2σ on the Cd
history below 5% of |Cd| and below 10% of the new increment; if it fails,
the rung is not ladder evidence and the failure is the finding.

*Nothing below this line existed when blockMesh was launched.*
