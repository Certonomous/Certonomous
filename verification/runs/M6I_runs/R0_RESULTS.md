# M6I — R0 RESULTS: Gate A, mesh admission

**Case `M6I`. Rung `R0`. Graded 2026-09-01 by a cfd lane, on the cfd supervisor's release of
Gate A.** Registration frozen at `73148a9c`, AMENDMENT 1 at `cb0bfd25`, AMENDMENT 2 at
`1d5832b1`, all pre-compute.

# VERDICT: **`GATE FAIL`**

**The registered ladder built exactly as designed and does not clear `MESH_STANDARD.md` §3.1.**

**NO SOLVER HAS RUN.** Gate G was not attempted and is `PENDING`. The release covered meshing
and mesh inspection only.

---

## 1. The ladder, as built

**One generator call, then two coarsenings** — `verification/runs/M6I_runs/build_m6i_ladder.sh`.
The generator is invoked **once**, so no generator parameter can fail to scale with the ladder
(`L-430`). The coarsener removes every other node.

| level | PLOT3D `i×j×k` nodes | cells | ranks | `checkMesh` log |
|---|---|---|---|---|
| **L1** fine | 81 × 129 × 97 | **983,040** | 1 | `L1/log.checkMesh` |
| **L2** medium | 41 × 65 × 49 | **122,880** | 1 | `L2/log.checkMesh` |
| **L3** coarse | 21 × 33 × 25 | **15,360** | 1 | `L3/log.checkMesh` |

**Exactly the registered counts of §3.** Two deviations from the published demo namelist, **both
registered in §3 before compute**: `target_y_plus` 1.0 → 0.25, and the three count parameters
doubled (`nnodes_cylinder_input` 32→64, `nr_gs` 8→16, `nre` 64→128). **Measured relationship,
not assumed:** the generator ties the chordwise count to `nr_gs` as `i_cells = 5·nr_gs`, so
doubling the counts doubles every direction. Everything else is the published namelist verbatim,
including `target_reynolds_number = 14.6e6` on the sharp-TE root chord.

## 2. Similarity — **PASS**, on both clauses

| check | measured | threshold | verdict |
|---|---|---|---|
| cell-count ratio L2/L3 | **8.00000000** | `r³` | **PASS** |
| cell-count ratio L1/L2 | **8.00000000** | `r³` | **PASS** |
| clause (i) exact integer `cells_fine == 8 × cells_mid` | **True** | AMENDMENT 1 | **PASS** |
| clause (ii) float band | within `8.0000 ± 0.0001` | §4 | **PASS** |

**`r = 2.000000` in every direction, exact on integers.** The family is geometrically similar in
§0's sense and that is not where it fails.

## 3. Mesh quality — **GATE FAIL**

| level | cells | internal faces | **max non-orthogonality** | severe (>70°) | **severe fraction** | **max skewness** | max aspect ratio |
|---|---|---|---|---|---|---|---|
| L3 | 15,360 | 44,832 | **87.6620°** | 3,686 | **8.2218 %** | 2.7750 | 1,243.59 |
| L2 | 122,880 | 363,648 | **86.4646°** | 24,774 | **6.8126 %** | **8.3014** | 873.82 |
| L1 | 983,040 | 2,929,152 | **87.7462°** | 191,794 | **6.5478 %** | **5.1116** | 1,578.62 |

**Failures against the registered thresholds:**

- **max non-orthogonality > 70° on ALL THREE levels** — over by **17.66 / 16.46 / 17.75°**
- **max skewness > 4 on L2 and L1** — **8.3014** and **5.1116**

---

## 4. A CORRECTION TO SOMETHING THIS LANE RELAYED UPWARD, AND IT MATTERS MORE THAN THE VERDICT

**On the demo family this lane reported the maximum as FALLING with refinement** —
88.9306 → 88.3866 → 86.5861° — **and used that as evidence that the obstruction is a
resolution artefact rather than `N-C6`'s structural defect.** That reading was relayed to the
supervisor and was carried into `N-C6`'s dated addendum.

**ON THE REGISTERED PRODUCTION LADDER THE MAXIMUM DOES NOT FALL.**

> **87.6620 → 86.4646 → 87.7462° (coarse → medium → fine). NON-MONOTONE, and essentially
> FLAT at ≈ 87° across a 64× increase in cell count.**

**A maximum that does not move under 64× refinement is a floor.** It is not `N-C6`'s *rising*
signature, and this record does not claim it is. **But it is much closer to "converging to the
defect" than the falling series this lane reported from the demo family**, and the earlier
inference was drawn from a three-point series on a **different, cruder** namelist. **The
strength of that claim does not survive this measurement and the claim is withdrawn to what the
data supports:** the maximum is **flat**, not falling.

**The severe FRACTION does fall, and only just:** **8.2218 → 6.8126 → 6.5478 %**, a factor of
**1.26 across a 64× cell increase**. It is **plateauing near 6.5 %, not vanishing.** For
comparison, `N-C6`'s butterfly caps rose **10.7×** over a **1.31×** cell increase. **Neither
series is the other, and this one is not converging away.**

**What the demo family and the production ladder agree on** is that both fail the gate by
16–19°, so the direction argument never determined the verdict. **It determined how informative
the failure is, and it is less informative than this lane said.**

## 5. Where the bad faces are — near-field, not far-field

Measured on L2 from the `nonOrthoFaces` set written by `checkMesh -writeSets`, in a domain
extending to **`R_outer` = 100 root chords**:

| statistic | radius from the root leading edge (root chord = 1) |
|---|---|
| minimum | 0.087 |
| median | **1.966** |
| 99th percentile | 2.096 |
| **maximum** | **2.275** |
| within `r < 2.0` | 15,346 of 24,774 (**61.94 %**) |
| **within `r < 5.0`** | **24,774 of 24,774 (100.00 %)** |

**Every severe face lies within 2.275 root chords of the root leading edge** — the wing and tip
region — and **none is in the far field.** The wing tip sits at `r ≈ 1.70` and the tip trailing
edge at `r ≈ 2.3`.

## 6. The published topology contains collapsed lines, measured

`plot3dToFoam` merges coincident nodes at 1e-15, and the count is the collapse:

| level | PLOT3D nodes | polyMesh points | **merged** | fraction |
|---|---|---|---|---|
| L3 | 17,325 | 15,873 | **1,452** | 8.38 % |
| L2 | 130,585 | 124,865 | **5,720** | 4.38 % |
| L1 | 1,013,553 | 990,849 | **22,704** | 2.24 % |

**A collapsed line is a geometric singularity**, and `F13` failed for a related reason. **This is
the publisher's own O-grid topology, not a construction of this lab's**, and the collapse is
where a very thin first cell — the `y⁺ = 0.25` target gives aspect ratios of 874–1,579 — meets a
degenerate edge. **This record does not claim the collapse is the mechanism**; it records the
measurement beside the failure and stops there.

## 7. A FOURTH INSTANCE OF THE `checkMesh` VERDICT DEFECT — the first across a whole registered ladder

**`checkMesh`'s closing line does not mention non-orthogonality on ANY level**, at 86–88°
against a 70° gate:

| level | max non-orthogonality | `checkMesh` closing line | which checks it actually counted |
|---|---|---|---|
| L3 | **87.6620°** | `Failed 1 mesh checks.` | aspect ratio (1,243.59), 8 cells |
| L2 | **86.4646°** | `Failed 1 mesh checks.` | skewness (8.30139), 1 face |
| L1 | **87.7462°** | `Failed 2 mesh checks.` | aspect ratio (1,578.62, 1,200 cells) + skewness |

**Not one of those counts includes the 70° breach.** `MESH_STANDARD.md` §14.1 records a pair
both printing `Non-orthogonality check OK.`; §14.3 a pair whose closing lines run
anti-correlated with the gate; this lane's demo L3 printed `Mesh OK.` at 88.9306°. **This is the
first instance across all three levels of a real registered ladder**, and the gate was read off
the reported maximum on every level, exactly as §14 requires. **A ladder graded on the closing
line would have reported three aspect-ratio-and-skewness problems and missed a 17.75° gate
breach.**

## 8. COST — rule 12

**Unit: core-minutes. Dollars DERIVED at $0.0513/core-h, c7a.4xlarge, reported-by-owner —
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).**

Measured per stage into `verification/runs/M6I_runs/COST.tsv` by the build script itself:

| stage | wall s | ranks | core-min |
|---|---|---|---|
| generate (one call, 983,040 cells) | 1 | 1 | 0.0167 |
| coarsen (4 levels) | 9 | 1 | 0.1500 |
| PLOT3D→ASCII ×3 | 1 | 1 | 0.0167 |
| `plot3dToFoam` ×3 | 6 | 1 | 0.1000 |
| `checkMesh` ×3 | 6 | 1 | 0.1000 |
| **TOTAL** | **23** | 1 | **0.3833** |

**Estimate vs actual:** registered R0 estimate **60 core-min**, cap **180 core-min**; actual
**0.3833 core-min**. **Ratio actual/predicted = 0.0064** — the estimate was **157× high**.
**$0.00033 derived** against $0.05 estimated. **Well inside the cap; no overrun.**

**Attribution: misprediction, not contention.** R0 was costed by analogy with `F13`'s 19.3
core-min mesh-build estimate and rounded up for a 983,040-cell level. **The published generator
is far faster than any mesher this lab has costed**: it writes a structured grid analytically
rather than iterating a snapping/refinement loop. `plot3dToFoam` and `checkMesh` on ~1M cells
cost 5 s each. **Waste, named separately: 0 core-min.** One earlier partial run of the build
script exited at the OpenFOAM `source` line under `set -u` after producing the grids; it cost
**10 core-s** and is **included in neither figure above** — it is named here rather than
absorbed. Load at build time: 1-minute average **5.77 on 16 cores**, single rank, `nice -n 15`.

**A calibration row is filed to `docs/COST_CALIBRATION.md`.**

## 9. What is NOT claimed

1. **No solver has run. Gate G is `PENDING` — not failed, not attempted.**
2. **The namelist was NOT tuned to clear the gate**, and will not be under this registration.
   Tuning a generator until it passes is how a gate becomes decoration.
3. **No mechanism is claimed for the 87° floor.** The collapsed lines (§6) and the near-field
   concentration (§5) are measurements placed beside the failure, not an explanation of it.
4. **`N-C6` is not invoked as the cause.** Its signature is a *rising* maximum; this one is
   flat. §4 says what the data supports and no more.
5. **The AGARD-faithful blunt-TE route stays shut**, per the supervisor's ruling of 2026-09-01.

## 10. ARTIFACTS

- `verification/runs/M6I_runs/{L1,L2,L3}/log.checkMesh` — the three graded logs
- `verification/runs/M6I_runs/{L1,L2,L3}/log.plot3dToFoam` — the merge counts of §6
- `verification/runs/M6I_runs/mesh/log.hcf_wing`, `log.hcf_coarsening` — the one generator call
  and the coarsener's own nesting assertions
- `verification/runs/M6I_runs/COST.tsv` — the per-stage timings of §8
- `verification/runs/M6I_runs/build_m6i_ladder.sh` — the build, reproducible
- `verification/runs/M6I_runs/analyse_m6i.py` — the comparator; `selftest` exits 0, `gateA`
  exits 1 on this ladder
