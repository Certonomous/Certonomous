# NASA TMR "3D ONERA M6 Wing" — WHAT NASA ACTUALLY PUBLISHES, AND WHERE OUR GRIDS CAME FROM

**cfd M6 lane, 2026-09-12.** Retrieved into the box under Sanaa's ~21:25Z ruling
(*"stop fighting the mesher and import a grid"*). **Nothing leaves the box** (`CLAUDE.md`
rule 8). Verified **by content**, never by filename, file type or hash alone (rule 15).

## 1. 🔴 NASA PUBLISHES A GENERATOR, NOT PRE-BUILT PLOT3D GRIDS

The 21:25Z instruction anticipated *"structured grids in Plot3D and CGNS, several levels"*
available as downloadable files. **They do not exist.** The NASA Turbulence Modeling
Resource large-files page lists **exactly one** artifact for the 3D ONERA M6 Wing case
(`Onerawingnumerics_val`):

**`wing_release_072319.zip`** — 125,194 bytes,
`sha256 b8005774fff3bcf2c86958af16cfb4c6d2329b7832a821446aa143f682d75819`,
retrieved 2026-09-12 from
`https://www.nasa.gov/wp-content/uploads/2026/04/wing-release-072319.zip`
(`https://turbmodels.larc.nasa.gov/onerawingnumerics_grids.html` now 301-redirects to the
nasa.gov Turbulence Modeling Resource pages).

**Its 13 members, listed from the archive itself:**

| member | bytes | what it is |
|---|---|---|
| `hcf_wing_v5p0.f90` | 356,409 | the grid **generator**, Fortran source |
| `hcf_coarsening_v3p9.f90` | 425,788 | the **coarsener**, Fortran source |
| `om6_wing_section_sharp.dat` | 1,267 | the ONERA M6 section, sharp trailing edge |
| `input.nml_strct`, `input.nml_tetra` | 3,584 each | sample namelists, structured / tetrahedral |
| `input_coarsen.nml_strct`, `…_tetra` | 402 each | coarsener namelists |
| `input.nml_naca0012_{round,blunt}` | 4,614 each | the NACA 0012 cases |
| `input_coarsen.nml_naca0012_{round,blunt}` | 442 each | ditto |
| `readme_release.txt` | 4,379 | build instructions |

**Not one grid file among them.** `readme_release.txt` opens, in its own words,
*"Wing-grid generator instruction."* and proceeds to `gfortran -O2 -o hcf_wing
hcf_wing_v5p0.f90`. **It is a source distribution you compile and run.**

## 2. 🔴 SO THE FAMILY ALREADY ON DISK *IS* THE NASA GRID FAMILY — PROVED BY BYTE IDENTITY

`verification/runs/M6I_runs/{L1,L2,L3}` were built 2026-09-01 by
`build_m6i_ladder.sh` from `hcf_wing` and `hcf_coarsening` out of
`wing_release_072319`. That was asserted in the build script's header; **it is now proved
against the archive NASA serves today**:

| file | release sha256 | our copy | |
|---|---|---|---|
| `om6_wing_section_sharp.dat` | `0a60e747a0a7b747cc52b7937c4f1e347e66f04e51a9e61bd5eb2bbe3d90eebc` | same | **IDENTICAL** |
| `input_coarsen.nml_strct` | `09f1b2fdc37fad2d0d385dd834e3933d5e9f64336a9e0dffbf5eddea487f70fd` | same | **IDENTICAL** |

And our `mesh/input.nml` differs from the release's `input.nml_strct` in **exactly the
deviations R0 registered before compute, and in nothing else** — the full diff is five
lines: `target_y_plus 1.0 → 0.25`; `nnodes_cylinder_input 32 → 64`; `nr_gs 8 → 16`;
`nre 64 → 128`; and `generate_su2grid_file T → F` (an output-format toggle that writes no
grid we use). **Every geometric and topological parameter — `tr`, `beta`, `b`, `R_outer`,
`airfoil_data_file`, `stretching_tanh_towards_lete`, `wing_side`, `root_le_x`,
`target_reynolds_number` — is the published namelist verbatim.**

## 3. WHAT THIS MEANS FOR THE INSTRUCTION

**The import track and the solve track are the same track, and there is no second grid to
fetch.** The M6I levels are the output of NASA's own released generator run on NASA's own
released section data with NASA's own released namelist, deviating only in resolution
(counts doubled) and near-wall spacing (`y+` target), both registered before compute at
`73148a9c` and graded at R0.

**This does not lift R0's `GATE FAIL` on mesh admission.** The 86–88° non-orthogonality is
**the published topology's**, not this lab's construction — which is why Sanaa's two-tier
ruling (quality **disclosed**, not gated) is the right instrument for it, and why the
defect's **location** (93 % of it outboard of η = 0.96, ADDENDUM 1 §A1.4) decides what a
band miss would mean.

**What is NOT claimed here:** that the binaries in `mesh/` were compiled from these exact
`.f90` sources. They were copied in as executables on 2026-09-01 from a release directory no
longer on disk, and a stripped binary cannot be hashed back to its source. The identity
above is over the **data and namelist** files, which is what determines the geometry, plus
the generator's own logged parameter echo. Recompiling `hcf_wing_v5p0.f90` and regenerating
the family bit-for-bit is a named, unperformed check.

**Artifacts:** `wing_release_072319.zip` and the extracted `wing_release_072319/` beside
this file. Retrieval only — **SUBMISSIONS PARKED**, nothing sent anywhere.
