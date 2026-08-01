# HLPW6 test case 1, coarsest committee grid: feasibility probe

Item: `hlpw6-testcase1-coarse-grid-entry`, approved, 3,600 core-min as filed,
36% of the approved backlog. Probe run 2026-08-01, 04:28Z to 04:51Z, on the lab
box (16 vCPU, 30.6 GiB, `MemTotal` 31,379.5 MiB).

**Headline: memory is not the wall, and it is not close. The real grid was
imported, decomposed and solved on this machine at a peak of 4.55 GiB against
30.6 GiB available, a headroom factor of 6.7. The case can run here.**

**What actually blocked it was that no import path existed**, and after that,
numerical robustness on a grid built for node-centred codes. Both are now
measured, and one of them is fixed.

Every number below is from a run recorded in `measurements.jsonl` in this
directory, with the raw solver logs at
`/home/ubuntu/certonomous-runs/hlpw6-memory-probe/logs/`.

---

## 1. What the case actually is

The docket record cites "High-Lift Prediction Workshop 6 grid statistics for
the HeldenMesh family, coarsest level 2661338 cells". That citation is exactly
right, and it is now verified against the grid file itself rather than against
a page.

Grid `H6C1_RANS_3a`, family R.1.TC1.01, described on the workshop grids page as
"generated using HeldenMesh, using traditional Fixed Grid methodology ... the
Helden Series 03 grids". Seven levels are published, `3a` through `3g`; `3a` is
the coarsest.

Downloaded 2026-08-01T04:34:57Z to 04:34:58Z (one second, 51 MB) from the
workshop's public object store. **No account, no registration and no
participant identifier was needed or created** — an anonymous HTTPS GET. Only
the grid and its boundary-condition map were fetched. No organiser was
contacted, no distribution list joined, no repository touched.

| | |
|---|---|
| archive | `h6c1_rans_3a_1.b8.ugrid.tar.gz`, 51,011,399 bytes |
| sha256 | `2fbce6cae220e592e098f34e0c62fb54e96e1fd2cf03d458862a7ef1454fd9cd` |
| unpacked | `h6c1_rans_3a_1.b8.ugrid`, 89,187,516 bytes, dated 2026-02-09 |
| boundary map | `h6c1_rans_3a_1.mapbc`, 4,758 bytes, 73 tagged patches |

Parsed from the file's own header, and cross-checked by recomputing the total
file length from the header counts (89,187,516 bytes predicted, 89,187,516
actual, exact):

| quantity | value |
|---|---|
| nodes | 1,156,796 |
| tetrahedra | 436,961 |
| pyramids | 341,341 |
| prisms | 1,883,036 |
| hexahedra | 0 |
| **cells** | **2,661,338** |
| boundary triangles | 145,614 |
| boundary quads | 4,175 |
| internal faces | 6,359,970 |
| **total faces** | **6,509,759** (2.446 per cell) |

It is a mixed prism/pyramid/tet unstructured grid — 71% prisms, i.e. a
boundary-layer grid with a tet farfield. The 73 boundary tags carry the
geometry apart: `WING_UPPER`, `WING`, `WING_TE`, `WING_TIP`, `SLAT`,
`SLAT_UPPER`, `SLAT_TE`, `SLAT_BRACKETS`, `FLAP`, `FLAP_UPPER`, `FLAP_TE`,
`FLAP_COVE` (all AFLR3 code 4000, viscous wall), `POS` (code 6662, symmetry
plane), and `Box` (code 5050, farfield). Mesh units are inches; the domain is a
6,000 inch cube with the symmetry plane at y = 0.

**No adjoint is involved.** Test case 1 asks for forces and surface quantities
at fixed angles of attack. It is a primal-only sweep. This matters below.

## 2. What the estimate was priced on, and the two errors in it

The filed `cost_basis` reads: "Rung A6 converged 579072 cells in 38.4 core-min
for 1000 iterations, which is 6.6e-5 core-min per cell per 1000 iterations ...
Memory is the genuine risk and is not established".

**Error 1, in the forecast rather than the docket.** `BACKLOG_FORECAST.md` says
"The scaling is linear-in-cells from an *incompressible* run applied to a
compressible one." That has it backwards. A6 ran `DARhoSimpleCFoam` — the
compressible transonic solver — at M = 0.850, on a 579,072-cell CRM wing
(`demo-output/website/dafoam/ladder-a/A6_crm_wingbody.md`, sections 1 and 2).
The workshop case is the low-speed one, at M = 0.20. The forecast's stated
mechanism for distrusting the number does not exist.

**Error 2, and it is the one that mattered.** Both the docket text and the
forecast reach for `ADJOINT_MEMORY_ENVELOPE.json` — DAFoam succeeding at 63,920
cells and failing at 99,840 — as "independent evidence that this is
optimistic". That envelope is entirely about the **adjoint**, and its own
structural cause is stated in the same file: OpenMDAO's reverse-mode sweep
building a mesh-sized `d[residuals]/d[vol_coords]` Jacobian block. **Test case 1
runs no adjoint.** A primal RANS solve stores fields and one matrix, not a
mesh-sized Jacobian. The envelope has no bearing on this item, and treating it
as a bound on this item is what made a routine 2.7M-cell primal look like it
might be infeasible.

The brief's warning was right, and in an even stronger form than posed: not
only were the adjoint failures a linear-solver breakdown rather than a memory
ceiling, they were failures of a solve mode this item never enters.

## 3. The blocker nobody had priced: there was no way to read the grid

The committee publishes these grids in AFLR3 `b8.ugrid` (with a `usm3d` variant
of the boundary map). OpenFOAM v2606 as installed here ships converters for
Fluent, Gambit, STAR, Ansys, CFX4, netgen, kiva and Plot3D. It ships **no
reader for AFLR3 UGRID and none for CGNS** (checked directly against
`$FOAM_APPBIN`). There was no path from the workshop's grid store into this
lab's solver at all. That, not memory, is what would have stopped the item on
day one, and no line of the estimate mentions it.

`ugrid_to_foam.py` in this directory is that missing path, written from the
format layout. Two things about how it was built are worth recording, because
they are the difference between a converter that works and one that silently
produces a wrong mesh:

* **Face orientation is decided geometrically**, outward from each owner cell's
  centroid, rather than from an assumed node-ordering convention.
* **The result is asserted against the file's own declared boundary list.**
  Every face computed to lie on the boundary must appear in the boundary faces
  the file itself declares, and the counts must match exactly.

That assertion earned its place immediately. The documented AFLR3 pyramid
ordering was wrong as applied: the first attempt produced 1,505,250 boundary
triangles where the file declares 145,614, and the assertion refused it rather
than handing OpenFOAM a corrupt mesh. Testing every node of each pyramid for
which one leaves the other four coplanar showed the apex is local node 2, not
node 5, for 336,700 of 341,341 pyramids, with a median coplanarity margin of
44x; the base winds (0,3,4,1). With that convention the boundary count is
exact: **145,614 triangles and 4,175 quads, matching the file, 149,789 total.**

Conversion cost, 2026-08-01T04:41:51Z: **30.8 s wall, peak 2,058 MiB.**

`checkMesh` on the result, 04:43:23Z, peak 1,389 MiB:

```
    cells:            2661338          Boundary definition OK.
    faces:            6509759          Cell to face addressing OK.
    internal faces:   6359970          Point usage OK.
    prisms 1883036  pyramids 341341    Upper triangular ordering OK.
    tetrahedra 436961                  Face vertices OK.
    Min volume = 2.9688178e-12         Number of regions: 1 (OK).
```

Every topology check passes and every cell volume is positive. The import is
correct.

`checkMesh` fails two **quality** checks, and these are the seed of section 5:
max aspect ratio 2,286 on 23 cells, max skewness 9.97 on 68 faces, and above
all **maximum non-orthogonality 89.98 degrees with 1,256,565 severely
non-orthogonal faces** — a fifth of the mesh. For comparison, A6's mesh ran at
max non-orthogonality 70.4 and average 18.9. These grids are built for
node-centred solvers; OpenFOAM's cell-centred finite volume method reads them
as very poor.

## 4. The memory measurement

Measured with a sampler (`memwatch.py`, 0.2 s interval) over the whole process
tree, reporting both the peak of the summed resident set and the sum of each
process's own high-water mark, plus the minimum `MemAvailable` on the host.

### The real grid, on this box

| stage | UTC | wall s | peak RSS MiB | sum VmHWM MiB | min MemAvailable MiB |
|---|---|---|---|---|---|
| grid import | 04:41:51 | 30.8 | 1,938 | 2,058 | 23,778 |
| `checkMesh` | 04:43:23 | 15.3 | 1,357 | 1,389 | 23,293 |
| `decomposePar`, 14 ranks | 04:44:03 | 12.9 | 1,285 | 1,290 | 23,563 |
| `simpleFoam`, 14 ranks, 120 iterations | 04:50:45 | 182.6 | 4,421 | **4,548** | 25,319 |

**Peak across every stage of the real case: 4,548 MiB, against 31,379 MiB of
host memory. The case uses 14.5% of this machine.** The solve never came within
20 GiB of the ceiling; `MemAvailable` bottomed at 25.3 GiB with the solver
running.

### The scaling law behind it

Because a single point is exactly the kind of basis this lab has been burned by,
the per-cell cost was measured as a slope over a four-rung structured ladder at
334,647 / 673,920 / 1,320,300 / 2,664,180 cells, same solver stack, same 14
ranks (rungs P1 to P4 and C1 to C4 in `measurements.jsonl`):

| cells | incompressible np14 MiB | compressible np14 MiB |
|---|---|---|
| 334,647 | 1,402 | 1,594 |
| 673,920 | 1,944 | — |
| 1,320,300 | 2,967 | 3,239 |
| 2,664,180 | 5,094 | 5,503 |

Linear fit, incompressible: **1.585e-3 MiB per cell, plus 872 MiB fixed**.
Compressible: 1.678e-3 MiB per cell plus 1,033 MiB.

A structured hex mesh carries 3.0 internal faces per cell, the most of any
element type; this workshop grid carries 2.446. At equal cell count the ladder
is therefore an upper bound on the real grid, and it behaved like one: the law
predicts 5,091 MiB at 2.66M cells, the real grid measured 4,548, which is 11%
below — the direction and roughly the magnitude the face ratio implies.

**Extrapolating the same measured slope, and holding 6 GiB back for the rest of
the box, this machine reaches roughly 15M cells structured or about 17M cells at
this grid's face ratio, at 14 ranks.** The workshop's coarsest grid is not near
any memory limit on this hardware. Several finer levels of the same family would
also fit.

## 5. Which limit actually binds

Not memory. Two other things bind, and both were hit.

**The compressible path aborts in the thermophysical model.** `rhoSimpleFoam`
at these conditions ran two clean SIMPLE iterations and died inside iteration 3
with a floating point exception raised in `libfluidThermophysicalModels.so`,
04:45:04Z, exit 136, `logs/HLPW6_solve_np14.log`. Peak memory at the point of
death was 4,973 MiB, so this is not a resource failure. It was not retried with
a temperature limiter; that is the obvious next move and it is untested.

**The incompressible path diverges under default numerics.** `simpleFoam` at
alpha 10 ran 14 iterations at falling residuals, then at iteration 15 the GAMG
pressure solve hit its 1,000-iteration ceiling without converging (initial
residual 0.0178, final 0.00933), continuity error jumped to 3.6e9, the reported
force coefficients went to order 1e20, and iteration 16 died with a floating
point exception in `Foam::divide(Field<double>&, const double&, const
UList<double>&)` — a division by zero in the turbulence model. 04:46:32Z, exit
136, `logs/HLPW6_solve_np14_incomp.log`. Peak memory 4,887 MiB. Again not a
resource failure.

That is the 1,256,565 severely non-orthogonal faces asserting themselves, and it
is the genuine technical risk in this item.

**It is survivable.** One hardened configuration — two non-orthogonal
correctors, first-order upwind convection, `DICGaussSeidel` smoothing with the
pressure solve capped at 100 iterations, and relaxation cut to p 0.2 and U 0.3 —
ran **120 iterations to completion, exit code 0**, at 04:50:45Z
(`logs/HLPW6_solve_hardened.log`). The Ux initial residual fell from 1.0 to
1.2e-6 and the force coefficients settled to smooth order-one values
(Cl 1.42, Cd 0.31 at the arbitrary reference area of 1 m², so the magnitudes
are not yet meaningful, but they are finite and evolving smoothly).

**The verdict is that the case runs here — but the configuration that runs is
first-order in convection, which is not a defensible workshop submission.** A
second-order entry is both more expensive and less robust than the run
measured. Closing that gap is the real open work on this item, and it is a
numerics problem, not a hardware problem.

## 6. The corrected estimate

Measured, 2026-08-01T04:50:45Z: **120 SIMPLE iterations in 182.63 s wall on 14
ranks = 42.61 core-min, i.e. 0.355 core-min per iteration** at 2,661,338 cells.

Per cell per 1000 iterations that is **1.334e-4 core-min**, against the filed
basis of 6.6e-5. The filed rate is **2.02x optimistic** — but the cause is not
cell count. It is rank count and grid type: A6 ran 4 ranks on a structured
extruded mesh, this runs 14 ranks on an unstructured one, and parallel
efficiency on this box is poor.

That last effect is large enough to state separately, because it changes what
the number even means. At 2,664,180 cells on the structured ladder:

| ranks | s per iteration | core-min per iteration | relative |
|---|---|---|---|
| 1 | 13.37 | 0.223 | 1.00 |
| 14 | 2.13 | 0.498 | 2.23 |

**Fourteen ranks buys 6.3x the wall speed for 2.23x the core-minutes.** Parallel
efficiency is about 45%, which is unsurprising for a memory-bandwidth-bound
segregated solver on 16 vCPU. So the core-minute price of this item is not a
property of the item; it is a property of how it is scheduled.

Carrying the docket's own assumption of 3,000 iterations per angle across the
six specified angles, 18,000 iterations:

| configuration | core-min | wall time |
|---|---|---|
| **14 ranks, measured rate** | **6,390** | **7.6 h** |
| 1 rank, measured rate | 4,014 | 67 h |
| filed estimate | 3,600 | not stated |

**The corrected figure is 6,390 core-min at 14 ranks, 1.78x the filed 3,600.**

Two caveats belong on that number rather than buried under it. The measured rate
came from a first-order run, and a second-order entry would be dearer. And **the
iteration count is still nobody's measurement** — 3,000 per angle is the
docket's assumption, carried forward unchanged. This is precisely the defect
that overran `tmr-flatplate-finest-grids` by 1.48x: the grid was priced and the
iterations were not. For a high-lift configuration at the upper angles, where
steady RANS commonly refuses to settle at all and limit-cycles instead, 3,000 is
optimistic. The item should not be treated as bounded until one angle is run to
its own convergence.

## 7. What this means for the item and the five behind it

1. **The feasibility question is answered: yes.** Peak 4.55 GiB of 30.6 GiB,
   measured on the real grid on this machine. The "memory is not established"
   clause in the filed basis is now established, and it was never the risk. The
   item does not need new hardware and never did.

2. **The memory objection should be struck from the forecast**, along with the
   claim that A6 was incompressible and the citation of the adjoint envelope
   against a primal-only item.

3. **The item is still underpriced, by 1.78x rather than by an unknown factor**,
   and the residual uncertainty has moved from memory to iteration count.

4. **The five items ranked behind it are unblocked.** They were sequenced behind
   an unresolved feasibility question on 36% of the backlog, and that question
   is resolved. Nothing about them depended on the answer being yes.

5. **The reusable asset is the import path.** Every published HLPW, DPW and
   AEPW committee grid ships in this format or CGNS, and this lab could not read
   any of them an hour ago. `ugrid_to_foam.py` is validated against a 2.66M-cell
   production grid to an exact boundary-face match. That is worth more than this
   one item.

6. **Open, and honestly open**: the compressible thermo abort is untested
   against a temperature limiter; no second-order configuration has been shown
   to survive this grid's non-orthogonality; no angle has been run to
   convergence; and nothing here says the result would place well. This probe
   establishes that the case can run on this machine and what it costs. It does
   not establish that it is worth Katie approving an approach.
