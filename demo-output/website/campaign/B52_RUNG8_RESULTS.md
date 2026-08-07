# B-52 eighth rung — results, against the pre-registration

Pre-registration: `B52_RUNG8_PREREGISTRATION.md` (commit 48cfedfb, before any
eighth-rung mesh existed). Case:
`/home/ubuntu/certonomous-runs/study-b52-rung8-uq`, built verbatim from
rung 7 (`b52.stl` md5 `c27eec6c710f0a937ec8cfe84aec2cfe`, identical) with only
`blockMeshDict` changed: (55 49 82) → (69 62 103). Run 2026-08-07, native
openfoam2606, 2 MPI ranks hierarchical n (2 1 1), 300 iterations, exactly as
rungs 5–7.

## Verdict 1 (zero compute): the surface-resolution hypothesis is REFUTED

The proposal pre-registered (2026-08-05, commit 9ee82a35, before any face
count was read) that the recipe might hold surface resolution flat while the
background scales — which would have explained seven non-monotone rungs as a
ladder that never refines its integration surface. Measured, per the
pre-registered decision rule (fit b in n_faces ∝ N^b on the valid family;
flat means b < 1/3, uniform-like means b in [0.55, 0.80]):

| rung | total cells N | `body` faces n_f | mean surface size (m) | min size (m) |
| --- | --- | --- | --- | --- |
| coarse* | 40,656 | 931 | 1.390 | not retained |
| medium* | 107,489 | 1,825 | 0.993 | not retained |
| intermediate | 135,779 | 6,098 | 0.543 | not retained |
| production | 193,880 | 7,533 | 0.489 | not retained |
| fine-uq | 255,358 | 9,395 | 0.436 (exact: patch area 1786.2 m²) | 0.100 |
| finer2 | 330,950 | 11,621 | 0.395 (1816.0 m²) | 0.045 |
| rung7 | 441,057 | 13,688 | 0.365 (1819.0 m²) | 0.059 |
| rung8 | 836,136 | 21,270 | 0.292 | — |

\* different recipe (shell level 1), outside the valid family, shown for
completeness. Unretained meshes' mean size uses the retained meshes' measured
patch area (~1800 m², identical STL); face counts are from each rung's own
retained `log.checkMesh`.

**Fitted exponent on the valid family: b = 0.707** (pairwise 0.593, 0.802,
0.820, 0.570), inside the pre-registered uniform-refinement window
[0.55, 0.80] and nowhere near the flat-surface branch (b < 1/3). Rung 8
continues the trend (b = 0.688 vs rung 7). Mean surface size falls
monotonically, 0.543 → 0.292 m across the family. **The recipe does refine
where the drag is integrated.** The mechanism offered for the seven-rung
non-monotonicity is refuted for the cost of reading the meshes, and the
non-monotonicity keeps its other, already-measured explanation: a
mesh-construction noise floor of 1.91e-3 in Cd, 53× the iterative noise
(`W3_MESH_NOISE_FLOOR_RESULTS.md`).

## Verdict 2: the rung, against the pre-registered prediction

- Achieved mesh: **836,136 cells** (target ~880k; achieved is measured, not
  chosen), h-ratio 1.238 vs rung 7. checkMesh: Mesh OK, max
  non-orthogonality 57.55 (rung 7: 64.64), max skewness 3.948 (3.535). One
  topology note, recorded: the `body` patch reads "multiply connected
  (shared edge)" where rungs 5–7 read "ok (closed singly connected)" —
  checkMesh still passes the mesh; noted as a deviation, not silently
  dropped.
- Solve: 300 iterations, no "SIMPLE solution converged" (as every rung
  before it); settle gate G2 **passes** — final-60 2σ = 9.23e-6 = 0.019% of
  |Cd| (cap 5%) and 3.32% of the increment (cap 10%); halves drift −6.8e-6.
- **Cd(836,136) = 0.047942443** (final-60 mean, the family's convention).
- Increment vs rung 7: **−0.000278** — the smallest increment the valid
  family has ever produced, and **15% of the measured mesh-construction
  noise floor** (1.91e-3).

**Scoring the pre-registered prediction, clause by clause:**

1. *"Cd lands inside the valid family's span [0.0472, 0.0523]"* — **TRUE**
   (0.04794). The pre-registered alternative (Cd escaping the span,
   divergence outrunning the noise floor) is refuted.
2. *"the refit stays monotone: false"* — **FALSE as written.** The fit takes
   the finest three (330,950 / 441,057 / 836,136 = 0.052275 / 0.048220 /
   0.047942), and that triple is monotone decreasing with shrinking
   increments. The six-rung sequence as a whole remains non-monotone.
3. *"conclusive: false, no observed order"* — **TRUE in verdict, with a
   twist**: an order was fitted and it is absurd — p = 28.7, far outside
   the [0.5, 2.5] window — so the `order_window` guard downgrades the study
   and no order is used. Recorded exactly as it fell, not clamped by hand:

```
observed_order 28.675, order_used 2.5, clamped true,
monotone true, increment_trend true, extrapolation_sanity true,
order_window FALSE  ->  conclusive: false, not_conclusive_guard: order_window
band_abs 4.931e-4 (fallback at p=2.5), reportable_band: None
```

**What the honest read is:** an increment ratio built from a −2.78e-4 step
that sits far below the 1.91e-3 mesh-noise floor is a ratio of noise, and a
noise ratio produces exactly this signature — a "monotone" triple with an
unphysical p = 28.7. The prediction's core claim — **the ladder is
mesh-construction noise, not a converging or diverging sequence** — is what
the rung measured; its sub-clause about the monotone flag was wrong because
noise happened to fall in one direction across the finest triple, which is
the same lesson at smaller scale. Per rung 7's G5 (carried forward),
`uq.reportable_band` returns **None** and no band is quoted.

## What this closes and what it opens

`agp-1dec50b65c2f` asked for an eighth rung as settling evidence. Delivered:
the rung, settled by its own gate, landing within noise of rung 7; the
surface-resolution alternative measured and refuted; and the ladder's
verdict unchanged — `conclusive: false`, no reportable band, now held by
`order_window` instead of `monotone`. Two independent measurements
(`W3_MESH_NOISE_FLOOR_RESULTS.md` and this rung) now agree that the family's
scatter is mesh-construction noise at the ~2e-3 level, so a ninth rung on
this recipe would buy another noise sample, not an order. The conservative
band (largest spread × 1.25) remains the only honest uncertainty statement
for this family.

## Cost, measured

| phase | wall | cores | core-min |
| --- | --- | --- | --- |
| surfaceFeatureExtract + blockMesh + snappyHexMesh + checkMesh | 189 s | 1 | 3.15 |
| potentialFoam + decomposePar | ~10 s | 1 | 0.17 |
| simpleFoam, 300 iterations | 473 s clock | 2 | 15.77 |
| **total** | | | **19.1 vs est_core_min 20** |

The pre-registration predicted 24–25 core-min (linear scaling from rung 7);
measured came in under the docket's 20 because snappyHexMesh and simpleFoam
both scaled sublinearly on this doubling. Recorded as measured.
