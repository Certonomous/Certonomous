# D7 mesh admission measurement — and the ruling on whether D7 inherits cfd's F1 finding

**Date:** 2026-08-25. **Lane:** dafoam `lab-lane`, curriculum item D7.
**Status of D7 itself at the time of this measurement:** NO COMPUTE. No arm directory, no
container, no solver log. This document is a *mesh* measurement, taken before launch, and it
grades nothing about the adjoint.

## 0. Why this measurement was ordered

The cfd team's F1 lane committed at `ed726454` that of **38 ONERA M6 mesh variants, not one
clears the 70° max-non-orthogonality admission gate of `docs/standards/MESH_STANDARD.md` §3.1**;
that the floor is **81.5834°**, **dial-invariant** across every meshing parameter they swept; and
that the maximum is **not at the trailing edge** but at the **outermost wall-normal (farfield)
cell** — their `worst_nonortho.py` localises it to `z0_tail_lo, i=0, j=31/31, k=19/19`, centroid
`(1.134134, -13.850016, 1.166844)`, at `|y| = 13.85` of a `16.118` farfield radius.

D7 runs on the A3 rung-2 mesh. **"Different provenance" is an inference, and 81.58° at the
outermost farfield cell could be a topology property of any M6 grid with a far-field boundary,
not a property of one script.** The dafoam-supervisor therefore ordered the mesh MEASURED, not
argued from records — and specifically refused to accept "A3 rungs 1–2 both PASS" as a substitute,
that being evidence about the adjoint and not about the mesh quality gate.

## 1. What was measured, and how

`checkMesh` from `dafoam-idwarp-rot:v1` (image id `2927768a16ac`, OpenFOAM v2506) was run on a
**scratch copy** of the staged base case — the staged case at
`/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/base/` was not written to.

Localisation of the maximum used `checkMesh -writeFields "(nonOrthoAngle)"` together with
`postProcess -func writeCellCentres`, read back from the written field files on disk.

### 1a. Two controls gate the localisation, and it refuses (exit 2) if either fails

**Planted-zero control (`CLAUDE.md` rule 3).** `PLANT = 999.987654` was written into cell 7777 of
a *copy* of the `nonOrthoAngle` field on disk, the copy re-read through the same parser, and the
plant required to come back. **PASS** — the reader saw `999.987654` where it had held
`17.5531983305529`, and the neighbouring cell was verified unchanged, so the plant did not corrupt
the parse. A zero from a reader not shown able to see a non-zero is not evidence, and this reader
was shown.

**Cross-instrument control.** The maximum of the field read from disk must reproduce `checkMesh`'s
own printed maximum. **PASS to 0.00e+00 degrees** — field max `61.49354914`, printed max
`61.49354914`. The localisation is therefore reading the same quantity `checkMesh` gated on, not a
lookalike.

## 2. The measured numbers

| quantity | measured | `MESH_STANDARD` §3.1 hard gate | result |
|---|---|---|---|
| cells | **42,120** | — | **CONFIRMS the pre-registration's registered 42,120** |
| max non-orthogonality | **61.4935°** | ≤ 70° | **CLEARS, by 8.5°** |
| max skewness | **1.9169** | — | `checkMesh` reports OK |
| max aspect ratio | **608.21** | — | `checkMesh` reports OK |
| `checkMesh` overall | **`Mesh OK.`** | — | no hard errors, no warnings |
| cells above 70° | **0** | — | — |
| cells above 65° | **0** | — | — |

Cell types: **42,120 hexahedra, 0 of every other type.** 3 patches — `wing` (1,560 faces),
`inout` (1,560), `sym` (1,836). Boundary definition OK, topology OK, 1 region.

Domain: bounding box `(-10.1655, -11.6992, 0)` to `(12.6881, 11.6998, 11.2746)`; outermost
cell-centre radius in the `x`–`y` plane **11.0246**.

### 2a. WHERE the maximum is — the question that decides the ruling

| | cfd's F1 mesh (`ed726454`) | **D7's mesh (this measurement)** |
|---|---|---|
| max non-orthogonality | **81.5834°** (best of 38) | **61.4935°** |
| location of the max | **outermost wall-normal cell**, `\|y\|=13.85` of `R=16.118` — **86 % of R** | **cell 11795, centroid `(0.858664, -0.021303, 1.193633)`, radius `0.8589` — 7.79 % of R** |
| worst region | the farfield | **the wing surface, trailing-edge region** (`\|y\| = 0.021`) |
| farfield quality | worst in the mesh | **max `7.5610°`, mean `3.3991°` over the 250 cells with `r > 0.95 R`** |

**The two meshes are not merely different in magnitude — they are inverted in structure.** In
cfd's mesh the farfield is the worst place in the grid. In D7's mesh the farfield is very nearly
the *best* place in the grid: 7.56° maximum, an order of magnitude below the wing-surface
maximum, and 74° below their farfield figure. The top ten worst cells in D7's mesh all sit between
7.5 % and 8.0 % of the domain radius, in symmetric ± pairs about `y = 0` — the signature of a
trailing-edge closure, not a farfield block.

## 3. Why they differ — the mesh's own birth certificate

`constant/birth_certificate.json` in the staged case records the generator:

```
"generator": "pyHyp (genWingMesh.py, N=28 layers, 3x-coarsened M6 surface)"
"created_at": "2026-08-10T14:54:06+00:00"
"cells": 42120, "verdict": "clean"
"max_non_orthogonality": 61.49354913677975
"max_skewness": 1.916854554279592, "max_aspect_ratio": 608.214865637278
```

**The birth certificate's three quality figures are reproduced by this lane's independent
`checkMesh` run to every printed digit.** The certificate was not taken on trust; it was
confirmed.

**pyHyp is a hyperbolic marching extruder.** It grows the volume grid outward from the surface
mesh one layer at a time, and near-orthogonality of each new layer is a *constraint of the
marching scheme itself* — so grid quality tends to **improve** with distance from the wall, which
is exactly the 7.56° farfield figure measured above. cfd's F1 variants are built by
`cases/F1_onera_m6/make_blockmesh_f1.py` — a multi-block `blockMesh` butterfly with named blocks
(`z0_tail_lo`, tip-fill blocks), whose outer blocks are filled by **algebraic / transfinite
interpolation between block edges**. In that construction the outer block's corner constraints
have nothing to relax against as the block grows, and the distortion accumulates **outward**.

**This is a mechanistic explanation, and it is offered as one — an inference from generator class,
not a measurement of cfd's code.** What is measured is the pair of localisations in §2a, and they
are what the ruling rests on.

## 4. RULING

**D7 does NOT inherit cfd's F1 finding.** D7's mesh clears the 70° admission gate on measurement,
with zero cells above it, and fails nowhere; its maximum is at the wing trailing edge, not the
farfield, and its farfield is the cleanest region in the grid. The gate was neither widened nor
waived — widening or retiring a gate threshold is reserved and is not a lane's call — because
nothing needed waiving.

**D7 is CLEAR to proceed on mesh-admission grounds.** This says nothing about any other D7 gate.

## 5. FOR THE CFD TEAM — a passing M6 mesh exists on this box, and where it came from

This is the part the dafoam-supervisor directed be committed for cfd to read, because their sweep
concluded a passing M6 mesh was not reachable.

**It is reachable, and one has been sitting on this box since 2026-08-10.**

* **The mesh:** `/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/base/constant/polyMesh/`
  (staged by copy from `/home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1`). 42,120 hex cells,
  **61.4935°** max non-orthogonality, `Mesh OK`.
* **The generator:** **pyHyp 2.6.1**, confirmed importable in `dafoam-idwarp-rot:v1` at
  `.../site-packages/pyhyp/__init__.py`. It is **already installed on this box** — no procurement
  is needed.
* **The driver script:** `genWingMesh.py`, present at `/home/ubuntu/dafoam-tutorials/Onera_M6_Wing/genWingMesh.py`
  and in several `certonomous-runs` trees including `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-probe80k/`.

**The suggested reading of their own result, offered and not imposed** — cross-family arbitration
is not a lane's call and cfd owns `MESH_STANDARD` and their own sweep:

> Their measured **dial-invariance is real and this measurement does not contradict it.** No
> `blockMesh` dial moved the floor because, on this evidence, the floor is a property of the
> **generator class** — algebraic block interpolation to a far-field boundary — and not of any
> dial within it. A sweep over dials cannot reach a floor set by the construction the dials live
> inside. The 38-variant sweep is not wasted work; it is what establishes that the fix has to be a
> different generator, and this document names one that is installed and has already produced a
> clearing mesh.

**Not claimed, and named as unverified:** this lane did **not** run cfd's `make_blockmesh_f1.py`,
did not re-measure any of their 38 variants, and did not verify their 81.5834° independently.
Their numbers are taken from their commit message as their measurement. The comparison in §2a is
between **their reported figure** and **this lane's own measurement**, and is labelled that way.
Whether pyHyp can be driven to produce a mesh meeting cfd's *other* requirements — their target
cell count, their `y+`, their FFD or their campaign's topology needs — is **not measured here and
is not asserted**.

## 6. Artifacts

| artifact | path |
|---|---|
| the mesh measured | `/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/base/constant/polyMesh/` |
| birth certificate | `/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/base/constant/birth_certificate.json` |
| cfd's sweep | commit `ed726454`, `cases/F1_onera_m6/` |

`checkMesh` was run on a scratch copy and the scratch copy is temporary: **the reproduction
command is the durable artifact**, not the scratch tree, and no repository document cites a
scratch path (`CLAUDE.md` rule 13). To reproduce, copy the staged `base/` elsewhere and run
`checkMesh -constant` in `dafoam-idwarp-rot:v1`; the three figures in §2 are in the birth
certificate for comparison.

**Cost of this measurement:** `checkMesh` and `postProcess` are serial and each returned in well
under one minute of wall time at np=1. Charged at **≈ 3 core-minutes gross**, np=1, three
container invocations. Derived dollar cost at the recorded $0.0513/core-h is **≈ $0.0026** —
**derived, not measured**; the box cannot read its own billing.
