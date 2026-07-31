# 4G — TMR ladder: what the "insane mesh aspect ratio" actually is

**Date:** 2026-07-30
**Host:** c7a.4xlarge, 16 vCPU. OpenFOAM 2606, native (`/usr/bin/openfoam2606`).
**Status:** Diagnosis complete. Aspect ratio is cleared as a solution defect in every
case tested. A **different, real defect** — the bump-in-channel rungs are not converged —
was found underneath it, quantified, and left open with its cause unidentified.
**Full figures:** `4G_tmr_mesh_aspect_ratio.json`. **Logs:** `4G_runs/`.

The brief was: stop and understand the mesh problem before advancing the ladder.
The ladder was not advanced. This document explains why that was the right call, and
what it cost.

---

## Headline

1. **The number is real, and it is not a spanwise artifact.** My first hypothesis —
   that a one-cell-thick 2D mesh inflates checkMesh's aspect ratio through the
   artificial unit span — is **wrong**, and I read OpenFOAM's own source to find out.
   The span is explicitly excluded. The reported number is genuine *in-plane* stretching.
2. **NASA's own reference grids fail the same check by 20 to 30 million.** The
   TMR-distributed NACA0012 C-grids — the grids CFL3D and FUN3D use to produce the
   reference values this whole ladder is graded against — report max aspect ratio
   **20,650,841 / 26,446,227 / 29,899,837** across their three rungs, and "Failed 4 mesh
   checks". Within 1 chord of the airfoil the coarse grid's max aspect ratio is **87.6**.
   The millions live 271 to 476 chords downstream, in the wake cut.
3. **"Worsens under refinement" is what NASA's own grids do.** 20.65M → 26.45M → 29.90M,
   monotonically. That signature therefore cannot, by itself, indicate a defect anywhere —
   including in the pyHyp generator finding that motivated this investigation.
4. **It is a metric problem, not a solution problem.** In every case tested. And where a
   real defect *did* co-locate with the highest-aspect-ratio cells, I cut the aspect ratio
   by 4.4x and the defect did not move.
5. **The actual defect on the "next rung" is convergence, not mesh quality.** All three
   bump-in-channel rungs stopped at their iteration cap with residuals 200-400x over
   target. Extending 4000 → 30000 iterations moves Cd by **−0.197%**, and it is still
   moving. The `cd_tail_spread` metric used to certify the ladder reads 4.6e-8 on that
   same run — roughly 4000x smaller than the real drift.

---

## 1. Where "insane mesh aspect ratio" is actually documented

The word "insane" appears nowhere in the repository; it is the owner's note. The numbers
behind it are in the checkMesh logs of every TMR rung
(`demo-output/website/tmr/runs/*/log.checkMesh`), and the largest of them is quoted in
`demo-output/website/tmr/C4_naca0012_closure.md:81` — *"max aspect ratio 26,446,226.94 on
1,822 cells … Failed 1 mesh checks."*

Every rung in the ladder fails the check:

| case | cells | max aspect ratio |
|---|---|---|
| flat plate coarse / medium / fine | 816 / 3264 / 13056 | 74,041 / 69,043 / 66,643 |
| bump coarse / medium / fine / finer | 3520 / 14080 / 56320 / 225280 | 2,136,801 / 2,192,933 / 2,218,683 / 2,230,929 |
| NACA (NASA grid) coarse / medium | 3584 / 14336 | 20,650,841 / 26,446,227 |

So the answer to "which case" is: **all of them**, spanning five orders of magnitude —
which is itself the first clue that one label is being applied to three different things.

I regenerated the flat-plate and bump meshes from `sdk/workflows/tmr_verification.py` and
re-converted NASA's grids from `models/tmr/naca0012/grids/*.p3dfmt`. Every recorded value
above reproduced **exactly** (e.g. 74041.01706, 2136801.242, 20650841.43, 26446226.94), so
the rebuilds are faithful and everything below rests on measurement, not inference.

---

## 2. What checkMesh's aspect ratio actually measures — a refuted hypothesis first

These are all one-cell-thick 2D meshes with `empty` front/back patches. The obvious
hypothesis is that checkMesh divides a span of 1.0 by a first-cell height of 5e-6 and
reports a meaningless 2e5. **That hypothesis is wrong**, and it is recorded here as
refuted because it is the first thing anyone will reach for.

From OpenFOAM's own source
(`/usr/lib/openfoam/openfoam2606/src/OpenFOAM/meshes/primitiveMesh/primitiveMeshCheck/primitiveMeshTools.C`,
`cellClosedness`, ~lines 705-727):

```cpp
for (direction dir = 0; dir < vector::nComponents; dir++)
{
    if (meshD[dir] == 1)          // <-- ONLY non-empty directions
    {
        minCmpt = min(minCmpt, sumMagClosed[celli][dir]);
        maxCmpt = max(maxCmpt, sumMagClosed[celli][dir]);
    }
}
scalar aspectRatio = maxCmpt/(minCmpt + ROOTVSMALL);
if (nDims == 3) { ...additionally max'd with (1/6)*cmptSum(sumMagClosed)/pow(v, 2.0/3.0); }
```

`meshD` is `geometricD()` (passed at `polyMeshCheck.C:751`), which is `-1` in an `empty`
direction. **The span is excluded from the loop.** checkMesh confirms this in its own
output: `Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)`.

So on these meshes the reported aspect ratio is the pure in-plane ratio of the two
directional face-area sums — for a wall-aligned hex, `dx/dy`. The numbers are real cell
stretching. They are not an artifact of the 2D convention.

**One consequence matters for the rest of this document:** the pyHyp meshes report
`3 geometric directions (1 1 1)`, so they take the `nDims == 3` branch, which uses a
*different formula* and *includes the span*. **pyHyp aspect ratios and TMR aspect ratios
are not the same quantity and cannot be compared numerically.**

---

## 3. Where the bad cells are — the distinction that settles it

High aspect ratio at a wall is normal and necessary. "Insane" has to mean something else.
So I wrote out checkMesh's `aspectRatio` field with cell centres and looked.

### Flat plate — the worst cell is on the wall, and it is fine

| cells | max AR | location | wall distance |
|---|---|---|---|
| 816 | 74,041 | x = 1.830, y = 2.29e-06 | 2.29e-06 |
| 3,264 | 69,043 | x = 1.913, y = 1.26e-06 | 1.26e-06 |
| 13,056 | 66,643 | x = 1.956, y = 6.62e-07 | 6.62e-07 |
| 52,224 | 65,468 | x = 1.978, y = 3.39e-07 | *new this session* |
| 208,896 | 64,887 | x = 1.989, y = 1.72e-07 | *new this session* |

The worst cell is the first wall-normal cell near the downstream end of the 2m plate,
where streamwise spacing has stretched. That is exactly where a wall-resolved grid *should*
put its most stretched cell. Non-orthogonality is **0** and skewness is at machine
precision (3e-15). And the aspect ratio **improves monotonically under refinement**,
converging toward ~64,500 — the scale-invariant signature of a family with fixed gradings.

This case agrees with CFL3D to **+0.2931%** on the matched grid and converges cleanly in
482-2846 iterations. There is nothing wrong here at all.

### Bump — the worst cells are not on the wall

| cells | max AR | location | distance to nearest wall |
|---|---|---|---|
| 3,520 | 2,136,801 | x = ±21.2 / −19.7 | **19.67** |
| 14,080 | 2,192,933 | x = 23.6 | **22.08** |
| 56,320 | 2,218,683 | x = 25.0 | **23.47** |

The bump wall is only `x ∈ [0, 1.5]`. These cells sit 20-25 units away on the
**symmetry-plane extensions**, where the wall-normal grading (needed for y+<1 on the bump)
is applied even though there is no boundary layer to resolve. They are extremely thin and
extremely long, in uniform undisturbed flow.

**Within the bump wall band `x ∈ [0, 1.5]`, the max aspect ratio is 4,714.** That is the
number that describes the mesh where the answer is computed.

The two numbers move in *opposite directions* under refinement, which is precisely why only
one of them looks alarming:

| rung | global max AR | max AR in the bump wall band |
|---|---|---|
| coarse | 2,136,801 | 4,714 |
| medium | 2,192,933 | 4,416 |
| fine | 2,218,683 | 4,274 |

The global maximum creeps up toward an asymptote near 2.24e6 (deltas +56,132, +25,750,
+12,246 — halving each step: a family property, not a refinement pathology), while the wall
band, the part that matters, **improves**.

### NASA's own grids — the decisive comparison

The brief noted TMR's reference grids are published, so we can compare against what TMR
itself uses. We hold all three (`models/tmr/naca0012/grids/`). I converted them with the
same pipeline and measured them with the same tool:

| NASA grid | cells | max AR | radius of worst cell | **max AR within 1 chord** |
|---|---|---|---|---|
| 113x33 | 3,584 | **20,650,841** | 414 chords | **87.6** |
| 225x65 | 14,336 | **26,446,227** | 453 chords | **241.1** |
| 449x129 | 57,344 | **29,899,837** | 476 chords | **2,555.5** |

Every cell with AR > 1e6 sits at radius ≥ 22 chords; all six cells above 1e7 sit between
271 and 414 chords. The farfield extends to 569 chords. The grid also reports 1,002 /
4,004 / 15,906 cells with small determinant and max non-orthogonality 85.7°, and
**"Failed 4 mesh checks."**

This is NASA Langley's own reference-grade grid, the one used to produce the CFL3D and
FUN3D numbers this ladder is graded against. It fails OpenFOAM's mesh checks
comprehensively. The near field, where the forces come from, is pristine.

**The conclusion is not that our meshes are fine because NASA's are equally bad. It is
that OpenFOAM's aspect-ratio criterion, with its default advisory threshold of 1000, does
not measure what it is being read as measuring on wall-resolved external-aerodynamics
grids.** `docs/standards/MESH_STANDARD.md` §3.3 already reached this conclusion from the
flat-plate numbers — *"a hard aspect-ratio gate at 1000 would reject every reference-grade
wall-resolved RANS grid the lab owns"* — and this session extends that calibration by
three orders of magnitude, onto TMR's own published grids.

---

## 4. Does it worsen under refinement? Yes — on NASA's grids too

This was the specific link to the pyHyp generator finding, so it deserves a direct answer.

| family | trend across rungs | direction |
|---|---|---|
| flat plate (blockMesh) | 74,041 → 64,887 | **improves** |
| bump (blockMesh) | 2.14M → 2.23M | converging to asymptote |
| **NASA TMR NACA0012 (NASA's own)** | **20.65M → 26.45M → 29.90M** | **worsens** |
| pyHyp NACA0012 (DAFoam) | 97.9 → 167.5 | worsens |

NASA's reference grids worsen under refinement, monotonically, on the same metric and in
the same direction as the pyHyp generator. The mechanism is not mysterious: refinement
halves the wall-normal and wake-cut spacing while the farfield stays at ~500 chords, so
the ratio of the longest cell to the thinnest must grow.

**Therefore "max aspect ratio worsens under refinement" is a normal property of a
wall-resolved grid family with a fixed farfield extent, and cannot by itself be read as a
generator defect.** That is the honest resolution, and it applies to the pyHyp finding as
much as to ours.

---

## 5. Is this the pyHyp generator finding? No — verified, not assumed

The brief said to verify rather than assume. I re-measured both pyHyp meshes directly.

The generator finding's own measurement **reproduces exactly**: 97.87218721638968 →
167.4971796573039, with the global-max cell at the blunt trailing edge (x ≈ 1.0) in both,
just as it states. That finding is sound on its own terms.

But it is not the same problem as the TMR ladder's:

| | pyHyp finding | TMR "insane" aspect ratio |
|---|---|---|
| generator | pyHyp hyperbolic extrusion | blockMesh; NASA's own plot3d grids |
| mesh dimensionality | **3D** `(1 1 1)` | **2D** empty-patched |
| formula branch | volume-based, **includes span** | in-plane only, **excludes span** |
| magnitude | 98 → 167 | 74,000 → 30,000,000 |
| worst-cell location | blunt trailing edge | far field / wake cut |
| **checkMesh verdict** | **`OK` — passes** | **`***High aspect ratio` — fails** |
| farfield extent | ~16 chords | ~500 chords (NASA) |

The pyHyp meshes **pass** the check that every TMR mesh fails, by a wide margin, and their
numbers are not even computed by the same formula. The dominant reason the magnitudes
differ is domain extent: 16 chords versus 500.

**Verdict: the generator finding is real and independently confirmed, but it is not the
cause of, or the same phenomenon as, the aspect ratio the owner flagged on the TMR
ladder.** No generator fix is load-bearing for this ladder — the meshes pyHyp builds are
not in it.

**The generator fix itself was not attempted, and this is a gap, not a completion.**
pyHyp is not installed on this host (`import pyhyp` → `ModuleNotFoundError`), so the
`epsE`/`epsI`/`volSmoothIter` scaling ablation that the finding proposes as its concrete
next step could not be run. It remains open.

### On the link to the gradient defect

`PROOF.md` §19.2 already tested aspect ratio as a discriminator for the gradient-accuracy
defect and returned a null result — the flagged station grew ×1.577 while a clean control
station grew ×1.975, i.e. the control grew *more*. I did not re-tread it. This session adds
one independent reason to doubt the link rather than revive it: the refinement-worsening
signature is exhibited by NASA's own reference grids, so it is too generic to discriminate
anything. **The null result stands, and nothing here upgrades it.**

---

## 6. The defect that is actually there: the bump rungs are not converged

Diagnosing the aspect ratio meant reading the bump logs, which surfaced something worse —
already on the register (`NOT_PASSING_REGISTER.md:546-553`) but never investigated.

Confirmed against the cases' own logs (L-22): **none** of the three bump rungs prints
`SIMPLE solution converged`. All three stop at their iteration cap. At bump-fine's exit:

| field | final initial-residual | target | over by |
|---|---|---|---|
| Ux | 2.0438e-06 | 1e-08 | 204x |
| k | 4.1759e-06 | 1e-08 | 418x |
| p | 3.6696e-07 | 1e-06 | **meets target** |

For contrast, all three flat-plate rungs converge properly (482 / 966 / 2846 iterations).

### It is not a short budget

The register proposes extending the iteration budget. I measured that. Running bump-coarse
to **30,000** iterations:

| | 4,000 iters | 30,000 iters |
|---|---|---|
| Ux residual | 5.2696e-06 | 1.2307e-06 |
| k residual | 3.9801e-06 | 6.6507e-07 |

Still descending, but at a rate implying **~2.5e7 iterations** to reach 1e-8. The proposed
fix is not viable, and that is now measured rather than assumed.

### What it costs the published number

| iteration | Cd |
|---|---|
| 4,000 | 0.0034430187 ← **the published bump-coarse value** |
| 9,000 | 0.0034395519 |
| 20,000 | 0.0034369768 |
| 30,000 | 0.0034362512 |

A **−0.197%** drift, still descending. The 4000-iteration value reproduces
`bump_sst.json`'s 0.0034430186567 exactly, so this is the same quantity.

**The `cd_tail_spread` metric that certifies the ladder reads 4.556e-08 over the last 1000
iterations of that same 30,000-iteration run** — about 4000x smaller than the accumulated
drift. It measures the drift *rate* over a short window, not the distance still to travel,
and on a slowly-creeping solution it reads as convergence when there is none.

This matters for the public claim. The fine rung's headline is Cd 0.003567 vs CFL3D
0.003607, **−1.126%**. The drift direction is downward and our value is already *below*
CFL3D, so further convergence moves it **away** from the reference, not toward it.

---

## 7. Testing whether aspect ratio caused it — a negative result

The residual is not spread evenly. Using `solverInfo` with `writeResidualFields` on a
faithful rebuild of bump-coarse at t=4000:

| field | max residual at | aspect ratio there | fraction of |residual| outside the bump region |
|---|---|---|---|
| Ux | x = 2.687, y = 2.5e-06 | 132,200 | **81.4%** |
| k | x = 3.594 | 167,300 | 72.2% |
| omega | x = 2.167 | 54,960 | 79.8% |
| p (meets its target) | x = 1.869, y = 0.018 | **37** | 59.9% |

The three fields that miss their target concentrate their residual in high-aspect-ratio
near-wake cells; the one field that meets its target has its maximum on ordinary cells of
aspect ratio 19-51. That is a suggestive correlation, and it would have been easy to report
it as a mechanism.

So I tested it. **One variable changed:** the downstream block's streamwise cell count
`nx_down` 12 → 48, with the total expansion ratio recomputed (455.85 → 100.58) so the first
downstream cell stays byte-identical at 0.0234375. Same wall spacing, same y-grading, same
upstream block, same schemes, same relaxation. 3520 → 4960 cells.

It did what it was supposed to do to the mesh:

| band | original | variant | |
|---|---|---|---|
| upstream far field, x < −5 | 2,136,801 | 2,136,801 | unchanged (untouched) |
| **bump wall, 0 ≤ x ≤ 1.5** | **4,714** | **4,714** | **unchanged (untouched)** |
| near wake, 1.5 < x < 10 | 702,000 | 160,200 | **4.4x better** |
| far wake, x > 10 | 2,136,801 | 471,500 | 4.5x better |

And it did nothing for the convergence. Both meshes were run to 30,000 iterations:

| iteration | original Ux | variant Ux | original k | variant k |
|---|---|---|---|---|
| 9,000 | 3.009e-06 | 4.061e-06 | 1.879e-06 | 2.068e-06 |
| 9,800 | 2.826e-06 | 3.817e-06 | 1.731e-06 | 1.915e-06 |
| **30,000** | **1.231e-06** | **1.606e-06** | **6.651e-07** | **8.702e-07** |

**The variant is slower at every matched iteration, not faster.** Neither converged. And it
did not reduce the drift either — the quantity that actually contaminates the published
number:

| | Cd drift, 4,000 → 30,000 |
|---|---|
| original (`nx_down` = 12) | **−0.19656%** |
| variant (`nx_down` = 48) | **−0.20656%** |

Essentially identical. Cutting near-wake aspect ratio by 4.4x changed neither the
convergence rate nor the drift.

**Result: negative.** The residual lives in those cells because that is where the wake is
developing, not because the cells are stretched. The correlation was not causation, and
aspect ratio is cleared as the cause of both the bump convergence stall and the Cd drift.
**The cause remains unidentified.** I am not guessing at it here.

One small genuine finding fell out of the control: at 30,000 iterations the variant's Cd is
**+0.065%** above the original's. So downstream streamwise resolution does have a real, if
small, effect on bump Cd — about a third of the convergence drift, and a grid sensitivity
the three-rung ladder does not currently account for.

This is recorded as a negative result to the same standard as the existing
aspect-ratio-as-discriminator null result in `PROOF.md` §19.2.

---

## 8. Did the ladder advance? No — and here is the honest accounting

Bump-in-channel, the "next rung" in the owner's note, was **already measured on three
rungs** before this session (`bump_sst.json`, generated 2026-07-25). What this session
established is that those three rungs are not converged and carry a measured drift. That is
a repair, not a new rung, and repairing it needs a cause I do not yet have.

Advancing to a fourth bump rung or to NACA0012 attempt-2 on top of an unconverged ladder
would have manufactured exactly the kind of number the owner's note was written to prevent.
A refinement ladder whose rungs are not converged cannot support a grid-convergence claim —
and the bump's observed order of **0.545** (against CFL3D's 3.095 on the same rungs) and
its **−11.2%** pressure-drag deviation are consistent with that.

**NACA0012 attempt-2 was time-boxed to zero solve time and not attempted.** The reason is
on the record rather than in my judgement: `C4_naca0012_closure.md` measured the transient
route at 11,700-30,300 core-minutes for a single rung against a 480 core-minute budget, and
lesson **P1 "Control before doubt"** (`LESSONS.md:230-241`) already refuted the mesh-quality
explanation for it. This session independently confirms P1's refutation from the other
direction: the coarse grid that produces the project's one trustworthy NACA0012 number has
max aspect ratio 20.65M and fails four mesh checks, so failing those checks plainly does not
prevent a good answer.

What was produced instead, all mesh-metric only, no solves:

- two **new flat-plate rungs** measured (52,224 and 208,896 cells) — extending the
  `MESH_STANDARD.md` §3.3 calibration table from 3 rungs to 5
- the **449x129 NASA grid** converted and measured for the first time
- the pyHyp cross-check, the residual localisation, the 30,000-iteration drift measurement,
  and the wake-refinement experiment

---

## 9. What remains open

1. **The bump convergence stall.** Real, quantified, cause unidentified. Aspect ratio ruled
   out by direct experiment. This is the load-bearing blocker for the bump rung.
2. **The published bump numbers.** `bump_sst.json` and the `wall.json` research card quote
   Cd 0.003567 vs CFL3D 0.003607 as a clean 1.1% agreement. That number carries an
   un-quantified convergence error of at least 0.2%, in the direction that worsens the
   agreement. It should not be quoted as clean until repaired. *(Not edited this session —
   changing a published claim is the owner's call, not mine.)*
3. **The pyHyp smoothing ablation.** Unrun; pyHyp is not installed here.
4. **`MESH_STANDARD.md` §3.3.** Its aspect-ratio calibration cites only the flat-plate
   numbers (max 74,041) and justifies them purely as wall-normal boundary-layer anisotropy.
   It does not cover the bump (2.2e6) or NASA's reference grids (2-3e7), and it does not
   record that the 2D and 3D formula branches produce non-comparable numbers — which is
   what makes a pyHyp "167" and a TMR "20 million" look like the same metric when they are
   not. *(Flagged, not edited — it is a standards document.)*

---

## Provenance

Every number above is reproducible from `4G_runs/`:

- `flatplate/log.checkMesh.{coarse,medium,fine,finer,finest}` — five-rung flat-plate metrics
- `bump/log.checkMesh.{coarse,medium,fine}` — bump metrics
- `bump/log.simpleFoam.coarse_residualfields.gz` — the `solverInfo` residual-field run
- `nasa/log.checkMesh.{coarse,medium,fine}`, `nasa/log.plot3d.*` — NASA's own grids, converted and measured
- `pyhyp/log.checkMesh.{coarse,refined}` — the generator cross-check
- `bump_wake_variant/{blockMeshDict,log.checkMesh}` — the negative-result experiment's exact mesh
- `probe_aspect_ratio.py` — the field-reading probe used for all location analysis

Pre-existing evidence cited, not re-derived: `demo-output/website/tmr/runs/*/log.checkMesh`,
`demo-output/website/tmr/{bump_sst,flatplate_sst}.json`,
`demo-output/website/tmr/C4_naca0012_closure.md`,
`demo-output/website/dafoam/GENERATOR_FINDING_pyhyp_aspect_ratio.md`,
`demo-output/website/dafoam/PROOF.md` §19.2,
`demo-output/website/campaign/NOT_PASSING_REGISTER.md:546-553`,
`docs/standards/MESH_STANDARD.md` §3.3, `LESSONS.md` P1 and L-22.
