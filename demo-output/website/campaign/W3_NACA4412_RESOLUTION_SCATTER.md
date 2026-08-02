# W3 — the NACA 4412's mesh-construction scatter, at three resolutions

**Meshed and solved 2026-08-02 10:22–11:1x UTC.** Serves docket item
`agp-d392641d60f4`, re-scoped on 2026-08-02 to *"find a resolution at which the
NACA 4412 finite wing's drag can be stated with a mesh-construction scatter
smaller than its acceptance band."*

Drivers: `sdk/scripts/naca4412_layered_replicates.py --refinement N`, which
imports `naca4412_credential_repair.py` rather than copying it, and
`sdk/scripts/naca4412_resolution_scatter.py`, which reads the cases and prices
them. Cases:
`/home/ubuntu/certonomous-runs/w3-naca4412-layered-replicates/{A,B,C,E}` and
`.../r3/{A,B,C,E}`, `.../r5/{A,B,C,E}`.

---

## 1. What the previous run left open

`W3_NACA4412_LAYERED_REPLICATES.md` rebuilt the **graded** rung at four
background blockMesh division triples and found the verdict reproducible and
the value not: `NOT VALIDATED` on all four meshes, but a drag range of **12.74%
of the mean — 1.69 times the entire half-width** of the ±9.56% band the
credential is graded against. Its closing line was that the honest next step is
a replicate family at a resolution where the scatter is small enough to state a
verdict, priced from one mesh first.

**That is one rung. A scatter measured at one resolution cannot say which
resolution to use.** This runs the *same four triples* at the rungs either side:
refinement 3 (`medium`) and refinement 5 (`finer`), which are the credential
ladder's own neighbouring rungs (`naca4412_credential_repair.RUNGS`), so nothing
about the recipe is invented.

## 2. Method, and what is held fixed

Identical in every respect except the `blockMeshDict` hex division triple and
the refinement level: geometry, layer sizing read from the STL, flow condition,
solver settings, **4 MPI ranks, scotch**. `D = (35 58 20)` is excluded at every
rung and that is a result, not an omission — `locationInMesh` sits at the span
centre and lands exactly on a block-face plane whenever the span division count
is even, so `snappyHexMesh` rejects the recipe's own seed point. That is a
property of the background divisions, so it holds at every refinement.

Reference, from `models/curriculum/naca4412_wing/reference.yaml` as repaired on
2026-08-01 (commit `d45f3090`): **Cd 0.015696, band ±9.56% → [0.014195,
0.017197]**, half-width **1.5005 × 10⁻³**.

**Pricing was done the way the item asked.** One mesh at the new resolution
first: replicate B at refinement 5 was built and solved alone, and measured
**32.6 core-min** — 934.2 s of serial meshing plus 255.53 s of solve at 4 ranks.
Only then were the other three launched.

## 3. Both controls hold

* **Refinement 3.** A at (33 60 20) reproduces the stored `medium` rung's
  **263,359 cells exactly** and its drag to **2.6 × 10⁻⁴ relative**
  (0.024484346 against the stored 0.024478020).
* **Refinement 5.** A at (33 60 20) reproduces the stored `finer` rung's
  **1,849,113 cells exactly**, its max non-orthogonality to **every printed
  digit** (74.962218) and its average to every printed digit (9.4399).

The recipe is deterministic at both new rungs, as it was at the graded one.

## 4. Results

**Twelve meshes, three rungs, four triples each. All twelve converged.**

### 4.1 Refinement 3 (`medium`)

| tag | divisions | cells | Cd | dev. | Cl | max non-ortho | core-min |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **A** (control) | (33 60 20) | 263 359 | 0.024484346 | +55.99% | 0.252088 | 58.374 | 2.83 |
| B | (34 59 21) | 249 616 | 0.025620072 | +63.23% | 0.264071 | 62.391 | 2.35 |
| C | (32 61 21) | 232 615 | 0.025963946 | +65.42% | 0.262541 | 57.556 | 2.20 |
| E | (34 60 21) | 253 044 | 0.025554960 | +62.81% | 0.263815 | 60.801 | 2.46 |

### 4.2 Refinement 4 (`fine`, the graded rung) — as published

| tag | divisions | cells | Cd | dev. | Cl | max non-ortho | core-min |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **A** (control, published) | (33 60 20) | 645 251 | 0.018262714 | +16.35% | 0.209554 | 64.990 | 6.41 |
| B | (34 59 21) | 652 249 | 0.020787415 | +32.44% | 0.246219 | 64.958 | 6.20 |
| C | (32 61 21) | 653 090 | 0.019911782 | +26.86% | 0.242685 | 74.962 | 10.44 |
| E | (34 60 21) | 666 878 | 0.020803581 | +32.54% | 0.246325 | 64.977 | 6.55 |

### 4.3 Refinement 5 (`finer`)

| tag | divisions | cells | Cd | dev. | Cl | max non-ortho | severe faces | core-min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **A** (control) | (33 60 20) | **1 849 113** ✓ | 0.018326259 | +16.76% | 0.250142 | 74.962218 | 797 | 43.65 |
| B | (34 59 21) | 1 884 231 | 0.018601869 | +18.51% | 0.249255 | 74.984444 | 494 | 32.61 |
| C | (32 61 21) | 1 795 256 | 0.017832422 | **+13.61%** | 0.237303 | 74.975650 | 1 853 | 38.27 |
| E | (34 60 21) | 1 882 576 | 0.018446974 | +17.53% | 0.248732 | 74.893881 | 593 | 39.74 |

A reproduces the stored `finer` rung's **1 849 113 cells**, its drag to
**5.7 × 10⁻⁵ relative** (0.018326259 against the stored 0.018327307), its max
non-orthogonality and average to every printed digit, and even its **797**
severely non-orthogonal faces.

### 4.4 The answer

| rung | cells | **Cd scatter** | **÷ band half-width** | Cl scatter | cost |
| --- | --- | --- | --- | --- | --- |
| 3 | 232 615 – 263 359 | 5.82% | 0.99 | 4.60% | 9.8 core-min |
| **4 (graded)** | 645 251 – 666 878 | **12.74%** | **1.69** | 15.57% | 29.6 |
| **5** | 1 795 256 – 1 884 231 | **4.20%** | **0.51** | 5.21% | 154.3 |

**Refinement 5 is a resolution at which this body's drag can be stated.** The
mesh-construction range is **4.20% of the mean — 0.51 times the band's
half-width**, against 1.69 times at the graded rung. Stated as the item asked:

> **Cd = 0.018302 ± 0.000385** (half-range over four independently constructed
> meshes at 1.79–1.88 M cells), **+16.6% from the reference 0.015696**, with all
> four outside the ±9.56% band.

Three further readings, each against a number this lab already published.

* **The scatter is not monotone in refinement, and the graded rung is the worst
  of the three.** 5.82% → 12.74% → 4.20%. Nobody could have picked the graded
  rung's scatter out of a one-rung measurement, and refining *once* from the
  medium rung made reproducibility worse before it made it better.
* **The verdict survives everywhere. Twelve of twelve meshes are outside the
  band, all on the same side**, +13.61% to +65.42%. `NOT VALIDATED` is now
  reproducible across mesh construction *and* across a 7.9-fold change in cell
  count. What moves is where outside: +56…+65% at r3, +16…+33% at r4,
  +13.6…+18.5% at r5, tightening toward roughly +16%.
* **The published triple stops being an extremum.** At refinement 4 the
  published mesh was the **minimum** of its family (the most favourable of the
  four) and on the NACA 0012 it was the **maximum**. At refinement 5 the same
  triple sits **second of four** — interior, 0.13% from the family mean. That is
  what leaving the regime where a single draw decides the answer looks like.

## 5. Mesh quality across the three rungs, read on the new gate

`w3-a-gate-that-returns-two-values` replaced the mesh-quality gate the same day.
This family is the cleanest evidence for why, and it was free:

| triple | r3 max | r4 max | r5 max |
| --- | --- | --- | --- |
| (33 60 20) | 58.374353 | 64.989619 | 74.962218 |
| (34 59 21) | 62.390692 | 64.958100 | 74.984444 |
| (32 61 21) | 57.556267 | 74.962443 | 74.975650 |
| (34 60 21) | 60.801266 | 64.976520 | 74.893881 |
| **spread** | **4.834°** | 10.004° (bimodal) | **0.091°** |

Read the spreads. At refinement 3 no mesh presses its constraint and four
meshes read four numbers across **4.83°** — a measurement. At refinement 5 the
same four agree to **0.091°** while their cell counts differ by 5% and their
drag by several percent: that is four meshes reporting
`relaxed { maxNonOrtho 75 }`, not four meshes that happen to be equally
non-orthogonal. Refinement 4 is the mixed case, three against the strict 65 and
one against the relaxed 75, and the lab's 70° gate splits that column 3–1 on
which branch `snappyHexMesh` ended on.

**And the layer coverage the credential blamed on one mesh is a property of the
rung.** The stored `finer` rung's record names its 58.3% of target layer
thickness as a defect of that mesh. Every refinement-5 replicate reads
**57.2–60.2%**, achieving about 6 of 12 layers, against 94.2–94.5% at
refinements 3 and 4. The rung under-resolves layers on every mesh built at it.

## 6. Cost, measured on CPU

Meshing is serial; the solve holds 4 ranks. `decomposePar`, `reconstructPar`,
`blockMesh` and `checkMesh` are not in the totals below (OpenFOAM's utility logs
do not print `ExecutionTime` here); measured from the driver's own timestamps
they are ~65 s per refinement-5 replicate, about 2% of it, and the same omission
is in the published refinement-4 figure so the columns are comparable.

| | r3 | r4 (published) | r5 |
| --- | --- | --- | --- |
| ranks | 4, scotch | 4, scotch | 4, scotch |
| cells per rank | 58 153 – 65 839 | 161 312 – 166 719 | 448 814 – 471 057 |
| **family total, CPU basis** | **9.84 core-min** | **29.61** | **154.26** |
| per replicate | 2.20 – 2.83 | 6.20 – 10.44 | 32.61 – 43.65 |

The refinement-4 column is this harness reading the published cases, and it
returns **29.61** against the record's published **29.608** — the harness is
validated against a number the lab published before it existed.

**The one-mesh price undershot, and it undershot for a reason the record already
names.** The item said to price from one mesh at the new resolution first. That
was done: B measured **32.61 core-min**, predicting **130.4** for a family of
four. The family cost **154.26**, a **1.18×** overrun *on a measured basis* —
outside the 1.051× the lab's measured-basis pairs had never exceeded. The cause
is not the solve, which came in at 233.78–334.81 s across the four. It is the
meshing: `snappyHexMesh` reported **934.2 s (B), 1045.0 s (E), 1058.1 s (C) and
1683.84 s (A)**, a 1.80× spread, with the control triple needing **51
layer-addition iterations against B's 25** on the identical recipe.

**So the rule needs a clause.** A single mesh prices a rung only where meshing
cost is not itself construction-sensitive. On this body it is, it was already
measured to be (4.7× at refinement 4), and a one-mesh price should carry the
family's own known meshing spread rather than be multiplied by n.

## 7. What this does to the item

* **The item's question is answered: refinement 5.** Scatter 0.51× the band
  half-width, against 1.69× at the rung the credential is graded from.
* **It is answered at 5.2× the graded rung's cost** — 154.3 core-min against
  29.6 — for a rung with 2.9× the cells, because meshing is superlinear and now
  dominates: 60% of the refinement-5 bill is serial `snappyHexMesh`.
* **The verdict does not change and now cannot be blamed on one mesh.**
  `NOT VALIDATED` holds on twelve meshes across three resolutions.
* **What remains open is the gap itself, not its reproducibility.** The ladder is
  converging on Cd ≈ 0.0183 against a derived reference of 0.015696. That +16.6%
  is now a stable, reproducible property of this setup, which makes it a
  question about the setup or the reference rather than about the mesh — and
  the refinement-5 rung resolves only **6 of 12** prism layers (57.2–60.2% of
  target thickness) on every replicate, which is the next thing to look at.
