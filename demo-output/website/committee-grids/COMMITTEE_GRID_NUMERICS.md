# Do committee grids defeat this lab's numerics? Measured on two workshops

Probe run 2026-08-01, 07:43Z onwards, on the lab box (16 vCPU, 30.6 GiB), while
otherwise idle. Every number below comes from a log in
`/home/ubuntu/certonomous-runs/dpw5-committee-probe/logs/`, or from the earlier
HLPW6 probe's logs at `/home/ubuntu/certonomous-runs/hlpw6-memory-probe/logs/`.
Raw per-run instrumentation is in `measurements.jsonl` beside those logs.

---

## 0. The question

`demo-output/website/hlpw6/FEASIBILITY_PROBE.md` established that the HLPW6
committee high-lift grid imports and fits in memory here, and that default
second-order numerics **diverge** on it: 14 clean iterations, then the GAMG
pressure solve at its ceiling, continuity error to 3.6e9, and a divide-by-zero
at iteration 16. Only a first-order configuration completed, which is not a
defensible workshop submission.

That left one question gating everything the new importer unlocks:

> **Do committee grids generally defeat this lab's cell-centred numerics, or was
> that one grid unusually hostile?**

This probe answers it on a second, independent committee grid — different
workshop, different mesh generator, different geometry, different flow regime —
and, because that grid ships in three element topologies built on **one shared
node distribution**, it also isolates *why*.

## 1. The second grid, and why this one

**AIAA Drag Prediction Workshop 5, `unstructured_grids.REV01`, level L1.T**,
downloaded 2026-08-01T07:52:57Z to 07:53:01Z (4 s, 153 MB total) by anonymous
HTTPS GET from the workshop's public NASA Langley mirror. No account, no
participant identifier, no organiser contacted, nothing registered.

| file | bytes | sha256 |
|---|---:|---|
| `L1.T.rev01.p3d.hex.r8.ugrid` | 37,131,204 | `89d3c18f9cff94161b755651d6abeccd1a0384e5454dcccfffcf166a808d4214` |
| `L1.T.rev01.p3d.prism.r8.ugrid` | 47,674,308 | `1ab10ddce71ea4f13ad1e70419d180f4f6212540c1ee24314fa36a0343f4761c` |
| `L1.T.rev01.p3d.hybrid.r8.ugrid` | 68,244,420 | `2c412518a1a87d3ce767541dc60d67ba1d6d74b061d7cfd230cb6d3aee744b3c` |

Source: `https://dpw.larc.nasa.gov/DPW5/unstructured_grids.REV01/`.

The grids carry no boundary-condition file. The directory's own `readme` states
the packaging and the patch semantics — "big endian Fortran unformatted with
64-bit floating point ... 18 boundary patches, patches 1-8 are y-symmetry,
patches 9-13 are solid wall, patches 14-18 are far-field" — and all three files
carry exactly tags 1 to 18, so `dpw5_L1T.mapbc` is that readme transcribed and
nothing more. It was checked rather than trusted (`inspect_ugrid.py`): tags 1-8
have every node at y = 0 exactly; tags 9-13 bound a body spanning x 92.5 to
2562.9, y 0 to 1159.9, z 91.0 to 343.2 inches; tags 14-18 bound the full
±30,000-inch domain. A semi-span of 1,159.9 in and a body 2,470 in long identify
this as the Common Research Model wing-body at the scale DPW publishes it, and
fix the mesh units as inches and the axes as x streamwise, y spanwise, z
vertical. The meshes were then scaled by 0.0254 to metres
(`logs/DPW5_*_transform.log`).

Three things made this the right second grid rather than merely the next one:

1. **The lab has a reference to grade against.** DPW5's geometry is the NASA
   Common Research Model wing-body, and Ladder A6
   (`demo-output/website/dafoam/ladder-a/A6_crm_wingbody.md`) is this lab's own
   converged CRM primal at M = 0.850 on a **self-generated** 579,072-cell mesh.
   Same geometry family, same Mach, one mesh from a committee and one from this
   lab's own pipeline. That is the three-way comparison the brief asked for, and
   the third leg is measured here rather than quoted (section 2).

2. **It is genuinely independent of HLPW6.** Different workshop (DPW vs HLPW),
   different generator, different geometry (transport cruise wing-body vs
   three-element high lift), different regime.

3. **It is a controlled experiment in its own right.** The committee published
   the *same* 660,177-node point distribution as hexes, as prisms, and as a
   tet/prism hybrid. Geometry, boundary layer and node placement are held fixed;
   only element topology varies. Anything that changes between them is caused by
   topology alone.

DPW6 was examined first and rejected on measured grounds, not guessed ones: its
coarsest published unstructured level is 20,657,615 cells (Boeing cell-centred
`T`, header read by HTTP range request), and NASA GeoLab's coarsest is
83,598,506 cells after merging. Against the measured memory law from the HLPW6
probe (1.585e-3 MiB/cell + 872 MiB at 14 ranks) the smaller of those needs about
33 GiB on a 30.6 GiB box. DPW6 is out of reach here; DPW5 L1.T is not.

### The importer needed extending, and now reads four packagings

DPW5 ships `.r8.ugrid`: **Fortran unformatted with record-length markers**,
where HLPW6 ships `.b8.ugrid`, a raw C stream, and DPW6's GeoLab family ships
little-endian `.lb8.ugrid`. `ugrid_to_foam.py` read only the last of those.
It now sniffs the layout from the first four bytes — a Fortran file opens with
a record marker whose value is exactly 28, the size of the seven-integer header
record, and nothing else can be 28 there — and settles endianness from header
self-consistency. For Fortran files it additionally asserts that the bulk
record's declared length equals the byte budget the header implies, which is a
free check on the entire header. The `.b8` path is byte-for-byte unchanged.

## 2. Mesh metrics, five grids, one tool, one machine

All five rows are `checkMesh` from OpenFOAM v2606 run on this box today. The A6
row was **re-measured** rather than quoted (`logs/A6ref_checkMesh.log`), and it
reproduces the figures in the A6 write-up exactly.

| grid | origin | cells | faces | max non-orth | **avg non-orth** | severe >70 deg | **% of faces** | max skew | max AR |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **A6 CRM wing** | **generated here, pyHyp extrusion** | 579,072 | 1,751,888 | **70.45** | **18.93** | **1** | **0.00006%** | 3.32 | 309 |
| DPW5 L1.T hex | committee, structured-derived | 638,976 | 1,937,920 | 89.71 | 23.71 | 11,506 | 0.59% | 14.06 | 14,427 |
| DPW5 L1.T prism | committee, same nodes | 1,277,952 | 3,229,184 | 89.94 | 33.57 | 216,336 | 6.70% | 6.32 | 7,488 |
| **HLPW6 3a** | **committee, HeldenMesh** | 2,661,338 | 6,509,759 | 89.98 | 42.24 | 1,256,565 | 19.30% | 9.97 | 2,286 |
| **DPW5 L1.T hybrid** | **committee, same nodes, tets** | 2,981,888 | 6,216,192 | 90.00 | 51.85 | 1,810,108 | **29.12%** | 6.32 | 7,488 |

Sources: `logs/A6ref_checkMesh.log`, `logs/DPW5_{hex,prism,hybrid}_checkMesh.log`
(07:59Z), and `hlpw6-memory-probe/logs/HLPW6_checkMesh.log` (04:43Z).

Three readings, and the second is the one that matters:

* **The lab's own grid is not merely better, it is in a different category.**
  A6 has *one* severely non-orthogonal face in 1.75 million; it is the only mesh
  of the five that `checkMesh` calls "Mesh OK" outright. Every committee grid
  here has tens of thousands to millions of severe faces. The house maximum of
  70.4 is not a coincidence — it is what a pyHyp hyperbolic extrusion off a
  structured surface produces, and until the HLPW6 import existed it was the
  only kind of volume mesh this lab had ever fed its solver.

* **HLPW6 was not unusually hostile. It was mid-range.** DPW5's hybrid grid is
  *worse* on both measures that matter: 29.12% of faces severely non-orthogonal
  against HLPW6's 19.30%, and average non-orthogonality 51.85 against 42.24.
  Two committee grids from two different workshops, and the second one is the
  harder of the pair.

* **The hostility is created by element topology, not by the point
  distribution.** The three DPW5 rows share one set of 660,177 nodes. Rendered
  as hexes: 0.59% severe. As prisms: 6.70%. As tets and prisms: 29.12%. The
  committee did not place its points badly; it decomposed them into the elements
  a node-centred solver wants, and a cell-centred finite-volume method reads
  that decomposition as near-degenerate.

### It is non-orthogonality specifically, not "bad mesh" generally

Worth separating, because the three quality metrics do not agree with each
other and only one of them tracks what the solver does (section 3):

* **Aspect ratio does not order these grids.** DPW5 hex has the worst maximum
  aspect ratio of all five, 14,427, nearly seven times HLPW6's 2,286.
* **Skewness does not order them either.** DPW5 hex again has the worst maximum
  skewness, 14.06, against HLPW6's 9.97.
* **Non-orthogonality does**, and it is the only one that does.

So "the committee grids are bad meshes" is too coarse a statement to be useful.
The grid with the worst cells by two of the three standard measures is the one
that solves; the ordering that matters is by non-orthogonality alone.

### The import is sound, and here is why that is not an assumption

Three independent conversions of the same physical domain agree on **total
volume to 1.1e-5 relative** (6.64141e13 vs 6.64148e13 vs 6.64148e13 cubic
inches). All topology checks pass on all three: boundary definition, cell-to-face
addressing, point usage, upper-triangular ordering, face vertices, single
region. Every computed boundary face was asserted against the file's own
declared boundary list and the counts matched exactly (41,984 / 68,608 / 78,848).

`checkMesh` does report a small number of face pyramids as incorrectly oriented
— 35 on hex, 12 on prism and hybrid — and that was checked rather than waved
past, because a wrong node-ordering convention in a converter is exactly the
kind of defect that hides there. `locate_bad_faces.py` places all 35: they are
**all quadrilaterals, they occur in coincident pairs at identical face centres,
and they cluster on the fuselage centreline at x = 65.1 m and around the wing
tip at y = 22-24 m.** They coincide with `checkMesh`'s own note of "96
neighbouring cells with multiple inbetween faces". That is the signature of
collapsed block edges in the published multiblock grid — genuine zero-thickness
slivers in the source data — not of a converter defect, which would hit an
entire element class systematically rather than 35 faces in 1,937,920.

## 3. The solve: second order, one configuration, four grids

Every run in this section uses **the identical numerics that diverged on
HLPW6** — `simpleFoam`, `bounded Gauss linearUpwind grad(U)` convection,
`cellLimited Gauss linear 1` gradient, `limited corrected 0.33` Laplacian and
surface-normal gradient, GAMG/GaussSeidel pressure, SIMPLEC with p 0.3 and
U 0.5, **zero non-orthogonal correctors**, kOmegaSST, 14 ranks. The fluid is
HLPW6's own (nu = 1.46e-5, U = 68.06 m/s). Only the grid changes.

| grid | avg non-orth | % severe faces | iterations reached | exit | how it ended |
|---|---:|---:|---:|---:|---|
| DPW5 hex | 23.71 | 0.59% | **200 of 200** | **0** | **ran to completion, Ux residual 1.0 -> 1.4e-5** |
| DPW5 prism | 33.57 | 6.70% | 143 | 136 | converged to 2.3e-5 by iteration 26, then climbed away and died |
| HLPW6 3a | 42.24 | 19.30% | 16 | 136 | 14 clean iterations, then died |
| DPW5 hybrid | 51.85 | 29.12% | 11 | 136 | died |

Logs: `logs/{hex,prism,hybrid}_base_incompressible_a2.11_solve.log`, and
`hlpw6-memory-probe/logs/HLPW6_solve_np14_incomp.log` for the HLPW6 row.

**The answer to the gating question is that committee grids generally defeat
this configuration, and HLPW6 was not the outlier — it was the middle of the
range.** The DPW5 hybrid grid, from a different workshop, a different generator
and a different geometry, died *sooner* than HLPW6 did, at iteration 11 rather
than 16.

### The failure is one mechanism, and it is the same one every time

| | HLPW6 3a, 04:46:32Z | DPW5 hybrid, 08:06Z | DPW5 prism, 08:22Z |
|---|---|---|---|
| GAMG pressure solve hits its 1,000-iteration ceiling | yes | yes, iterations 9 and 10 | yes, 7 times |
| continuity error blows up | 3.6e9 | 5.6e9 | 6.9e14 |
| force coefficients reach order | 1e20 | 1e15 | 1e31 |
| dies in | `Foam::divide(Field<double>&, const double&, const UList<double>&)` | the same symbol | the same symbol |
| exit code | 136, signal 8 | 136, signal 8 | 136, signal 8 |
| peak memory at death | 4,887 MiB | 4,870 MiB | 2,866 MiB |

**None of these is a resource failure.** The largest peak across all three is
4,887 MiB against 31,379 MiB of host memory, and the lowest `MemAvailable`
observed during any of them was 21,670 MiB — over 21 GiB free at the moment of
the crash. The box is not the limit; the discretisation is.

### It is a dose-response, not a cliff

The three DPW5 rows share one node distribution, so the only thing varying
across them is element topology — and the outcome varies monotonically with
non-orthogonality, on both the average and the severe-face fraction, with the
HLPW6 grid landing exactly where its metrics say it should:

```
avg non-orth   23.71     33.57        42.24        51.85
% severe        0.59%     6.70%       19.30%       29.12%
iterations       200       143           16           11
                 ---       ---          ---          ---
               survives   slow         fast         fastest
                        divergence   divergence   divergence
```

That the HLPW6 grid, which shares nothing with DPW5 but the fact of being a
committee grid, slots into the ordering between prism and hybrid is the
strongest evidence here that non-orthogonality is the mechanism rather than a
correlate of one. **The threshold on this configuration sits between an average
of 23.7 degrees and 33.6 degrees**, which places every unstructured committee
grid measured so far on the wrong side of it, and both of this lab's own
self-generated meshes comfortably on the right side.

### What that already implies about reach, before any fix

DPW5 publishes each of its six levels in all three topologies, so the finding
above is directly actionable: it says *which family* to take, not merely that
committee grids are hard. Cell counts below are from each file's own header,
read by HTTP range request without downloading the files
(`logs/DPW5_size_survey.log`, 08:31Z); the predicted peak applies the HLPW6
probe's measured memory law, 1.585e-3 MiB per cell plus 872 MiB at 14 ranks.

| level | hex cells | predicted peak | prism cells | hybrid (tet) cells |
|---|---:|---:|---:|---:|
| L1.T | 638,976 | 1,884 MiB (**1,986 measured**) | 1,277,952 | 2,981,888 |
| L2.C | 2,156,544 | 4,290 MiB | 4,313,088 | 10,063,872 |
| L3.M | 5,111,808 | 8,974 MiB | 10,223,616 | 24,068,096 |
| L4.F | 17,252,352 | 28,216 MiB | 34,504,704 | 80,990,208 |
| L5.X | 40,894,464 | 65,689 MiB | 81,788,928 | 192,544,768 |
| L6.S | 138,018,816 | 219,631 MiB | — | — |

**Three consecutive levels of the DPW5 hex family — L1.T, L2.C and L3.M, at
0.64M, 2.16M and 5.11M cells — fit on this box with room to spare, and the
first of them has now been solved at second order here.** Three levels is the
minimum for a Richardson-extrapolated grid-convergence study, which is the
thing DPW asks for. That is a materially different sentence from anything this
lab has been able to say about committee grids before today.

The measured L1.T peak, 1,986 MiB against 1,884 predicted, is 5% above the law
rather than below it — the opposite sign to HLPW6's 11% shortfall, and
consistent with a pure hex mesh carrying 3.0 internal faces per cell where the
HLPW6 grid carries 2.44.

## 4. Diagnosis: what actually breaks, and in what order

### The instability is present from the first pressure solve

Two runs, identical in every respect except the grid. Column 3 is the
`time step continuity errors : sum local` printed by the solver itself.

| iteration | DPW5 hex, GAMG p iterations | hex continuity | DPW5 hybrid, GAMG p iterations | hybrid continuity |
|---:|---:|---:|---:|---:|
| 1 | 29 | 5.0e-08 | **339** | 5.1e-08 |
| 2 | — | 2.0e-06 | 115 | 2.0e-06 |
| 5 | — | 1.3e-06 | 252 | 6.7e-06 |
| 6 | — | 1.5e-06 | 171 | **4.7e-04** |
| 7 | — | 1.4e-06 | 389 | 1.6e-02 |
| 8 | — | 1.4e-06 | 269 | 1.40 |
| 9 | — | 1.2e-06 | **1000** | 4.5e+04 |
| 10 | — | 1.3e-06 | **1000** | 5.6e+09 |
| 11 | — | 1.2e-06 | — | dies |
| 200 | 28 | **3.6e-08** | — | — |

Two things are visible here that no summary statistic shows.

**The pressure matrix is already ill-conditioned before anything has gone
wrong.** On the very first iteration, with both runs at an identical continuity
error of 5e-8 and an identical uniform initial field, GAMG needs 29 iterations
on the hex mesh and **339** on the hybrid one. Nothing has diverged yet; the
discretisation of the same physical domain is simply an order of magnitude
harder to invert when the cells are tets.

**The divergence is geometric, not sudden.** The hybrid continuity error
multiplies by roughly 30 to 100 every iteration from iteration 5 onward:
6.7e-6, 4.7e-4, 1.6e-2, 1.40, 4.5e4, 5.6e9. There is no single event to catch
and no iteration at which a limiter could intervene. The hex run, on identical
physics and boundary conditions, holds flat at 1.3e-6 for two hundred
iterations and then falls to 3.6e-8.

So the failure is not a blow-up that better limiting would contain. It is an
amplification factor greater than one in the outer SIMPLE loop.

### Sixteen configurations on the hostile grid, and what each one was a bet on

Each row below is the HLPW6 baseline with one named thing moved, except where
the row says otherwise. Every one was predicted before it was run
(`PREDICTIONS.md`, timestamped, with the falsifications recorded as they
landed). All are `simpleFoam`, DPW5 hybrid, 14 ranks, alpha 2.11, 120
iterations requested. 120 is not an invented bar — it is the exact length of
the HLPW6 hardened run, the only committee-grid solve this lab has ever
completed.

| variant | what was changed | iterations of 120 | exit | outcome |
|---|---|---:|---:|---|
| `base` | -- (reference) | 11 | 136 | diverged, signal 8 |
| `nonorth2` | nNonOrthogonalCorrectors 0 -> 2 | 11 | 136 | diverged, signal 8 |
| `nonorth6` | nNonOrthogonalCorrectors 0 -> 6 | 11 | 136 | diverged, signal 8 |
| `uncorr` | snGrad/laplacian -> uncorrected | 11 | 136 | diverged, signal 8 |
| `limlin` | div(phi,U) -> limitedLinear 1 | 12 | 136 | diverged, signal 8 |
| `linupV` | div(phi,U) -> linearUpwindV | 12 | 136 | diverged, signal 8 |
| `combo` | three axes at once | 11 | 136 | diverged, signal 8 |
| `prod` | limitedLinear, 2 correctors, limited 0.25, p 0.2 / U 0.4 | 13 | 136 | diverged, signal 8 |
| `pcg` | p solver -> PCG | 11 | 136 | diverged, signal 8 |
| `pcap` | GAMG -> DICGaussSeidel, maxIter 100 | 11 | 136 | diverged, signal 8 |
| `potinit` | potentialFoam pre-step | 7 | 136 | diverged, signal 8 |
| `potprod` | potentialFoam + limitedLinear + 2 correctors | 9 | 136 | diverged, signal 8 |
| `base_sa` | turbulence model | 16 | 136 | diverged, signal 8 |
| `slow` | p 0.3 -> 0.1, U 0.5 -> 0.3 | 13 | 136 | diverged, signal 8 |
| `crawl` | p 0.05, U 0.2 | 16 | 136 | diverged, signal 8 |
| `crawl3` | p 0.02, U 0.1, limitedLinear, capped p | 8 | None | stopped (rc None) |
| `upwind1` **(first order)** | div(phi,U) -> upwind | 11 | 136 | diverged, signal 8 |

Table generated by `ladder_table.py` directly from the solver logs, so no
number in it passes through a transcription step.

**Nothing works.** Not the corrector count, at 0, 2 or 6. Not removing the
non-orthogonal correction altogether. Not three different convection schemes.
Not a different pressure solver, or a capped one. Not a different turbulence
model. Not a potential-flow initial field. Not any combination of them. And —
the result that settles the question — **not first-order convection either**.

That last row deserves separating, because it is the one that changes what the
lab can target. First-order upwind is what rescued HLPW6: the hardened run
completed 120 iterations there, exit 0. On the DPW5 hybrid grid it dies at
iteration 11 like everything else. **This grid is past the point where giving up
second-order accuracy buys anything.**

### Relaxation buys iterations, not stability

The relaxation axis is the one worth separating from the others, because
relaxation is the only knob here that costs no accuracy — it changes the path
to the answer, not the answer. If a second-order run could be crawled to
convergence, that would be a defensible result, merely an expensive one.

It cannot. Cutting relaxation from p 0.3 / U 0.5 to p 0.05 / U 0.2 delays the
onset of growth by about three iterations and changes nothing else. The
continuity error under `crawl`:

```
iteration   1      5        7        9        11      13       15
          5.0e-8 1.3e-6  2.8e-6  2.8e-4  2.0e-1  1.8e+2  1.3e+20
```

Same geometric blow-up, same factor of 30 to 100 per iteration once it starts,
five iterations later. The amplification factor of the outer loop is greater
than one and relaxation does not reduce it below one; it only lowers the
starting point of an exponential that still grows.

### What the failures rule out

Taken together the ladder is more useful for what it excludes than for what it
found:

* **Not the linear solver.** GAMG, GAMG capped at 100 iterations with
  DICGaussSeidel, and PCG/DIC all fail identically.
* **Not the convection discretisation.** Second-order reconstruction, TVD
  face-limiting, vector-limited upwinding and plain first-order upwind all fail
  identically.
* **Not the non-orthogonal correction.** Applying it zero, two or six times, and
  removing it entirely, all fail identically.
* **Not the turbulence model.** k-omega SST and Spalart-Allmaras both fail,
  despite the crash being reported inside the turbulence model — which confirms
  the turbulence model is where the NaN surfaces, not where it starts.
* **Not the initial condition.** A converged divergence-free potential-flow
  start (`potentialFoam` exit 0, continuity error 1.6e-5) fails *sooner*, at
  iteration 7.
* **Not relaxation.**

What remains is the thing every one of these shares: a cell-centred
finite-volume discretisation evaluated on faces where the line joining the two
cell centres is nearly parallel to the face itself. On this grid that describes
1.8 million faces out of 6.2 million.
