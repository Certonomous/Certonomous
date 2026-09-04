# M6F pre-registration — THE LAB'S ONERA M6 THREE-DIRECTION GRID FAMILY

> ## ⚠ STATUS: **UNFROZEN DRAFT. NOT A FREEZE. NO COMPUTE IS AUTHORISED BY THIS FILE.**
>
> Drafted by a `lab-lane` of the cfd team, 2026-09-04. **The freeze — check 4 of
> `SUPERVISION_CHARTER.md` §3 — is the cfd supervisor's personally and has NOT happened.**
> Until it does, this document is amendable under rule 2's pre-compute clause, and the
> condition for that clause is stated and was checked: **`verification/runs/M6F_runs`
> and `cases/onera_m6_family` DID NOT EXIST at the moment of drafting** (both confirmed
> absent, 2026-09-04 ~15:20Z).
>
> **No solver has been launched by this lane. No file under
> `/home/ubuntu/certonomous-runs/` was written; it was read only.**

---

## 0. WHY THIS EXISTS — SANAA'S ORDER, VERBATIM AND AT ITS SOURCE

`etc/sessions/2026-09-04T1500Z_sanaa_m6_route_ruling.md`, committed at `70d12a46`
(subject line verified; the file is the commit's only content, 35 insertions):

> M6SR launches now on the committee family; the third-direction family builds
> in parallel as the standing capability. Both inside the $1,000 ladder
> envelope. First physics I want to see: M6 surface Cp at the AGARD span
> stations against tunnel data, with the family band.

**The design constraint taken from her words is "standing capability, not a one-off mesh."**
This registration therefore registers a **family**, not a grid: five levels from one
generator, with an identity proof that is re-runnable and a refusal set a launcher must
honour.

**⚠ The "Context (chief's reading)" beneath her blockquote in that file is a reading and is
NOT quoted here as instruction.** Where this document needs the chief's reading it says so.

---

## 0.1 🔴 A PREMISE CORRECTION, RECORDED BECAUSE IT WAS PROPAGATING

A prior pass reported that **"the blunt-TE route was shut by the cfd supervisor's ruling of
2026-09-01."** **That is false, and the source says the opposite.**

`verification/campaign/M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md:468`, verbatim:

> **Three separate facts say the blunt-TE route is open and none of them is a measurement
> that it works.**

and the same paragraph closes:

> **None of this has been attempted and no claim is made that it will clear the gate.**

**There was no ruling to overrule. The route is OPEN and UNATTEMPTED.** The cfd supervisor
ruled it explicitly open on 2026-09-04. **This registration inherits that document's refusal
to claim the route works, and repeats it: nothing below asserts that either repair succeeds.**

---

## 1. WHAT IS ALREADY ON DISK — MEASURED BY THIS LANE, NOT INHERITED

A genuine three-direction family **already exists on this box**: `verification/runs/M6I_runs/mesh/`,
the `wing_strct` family, five levels, from the NASA `hcf_wing` + `hcf_coarsening` generator
(both present and executable: ELF x86-64, `hcf_wing` 325,216 B, `hcf_coarsening` 389,672 B).

**Every figure in this section was re-measured by this lane from the named artifact. None is
relayed.**

### 1.1 Block dimensions — from the `.nmf` sidecars

| level | IDIM | **JDIM (wall-normal)** | KDIM | artifact |
|---|---|---|---|---|
| L1 | 81 | **129** | 97 | `M6I_runs/mesh/wing_strct.1.nmf` |
| L2 | 41 | **65** | 49 | `wing_strct.2.nmf` |
| L3 | 21 | **33** | 25 | `wing_strct.3.nmf` |
| L4 | 11 | **17** | 13 | `wing_strct.4.nmf` |
| L5 | 6 | **9** | 7 | `wing_strct.5.nmf` |

**Every index direction halves at every one of the four steps.** The `(n−1)` ratios are
**exactly 2.000 in all three directions at all four steps** — no direction is held fixed.

**The wall-normal direction is `J`, and this is mechanical, not inferred from the numbers.**
The `.nmf` places `viscous_solid` on block face **5** and `farfield` on face **6** — the
J-min and J-max faces — and the generator namelist sets `nre = 128` ("# of Elements in the
radial direction (from wing to farfield)"), giving `JDIM = nre + 1 = 129`. **The wall-normal
count is the halving parameter.** This is precisely what pyHyp cannot do at any usable ratio.

### 1.2 Cell counts and the refinement ratio — from the `.lb8.ugrid` binaries

**⚠ THE FILES ARE LITTLE-ENDIAN RAW-C.** A big-endian read of the same L1 header returns
`(-2128736512, -1073741824, 1080754176, 0, 0, 3145728, 13635072)` — an implied file size of
**−46,142,642,148 B** against an actual **55,691,572 B**. **That mis-read is the planted
control for this section: the reader is shown able to reject the wrong byte order, so its
acceptance of the right one is evidence** (rule 3).

**⚠ A CORRECTION TO HOW THIS FAMILY MUST BE COUNTED, WHICH A PRIOR PASS DID NOT STATE.**
The volume cell count is **hexes + prisms**. The prisms are the degenerate cells on the
collapsed pole axis. **Counting hexes alone gives ratios 8.103 / 8.211 / 8.444 / 9.000 — NOT
8 — and would look like a broken family.** The correct totals:

| level | hexes | prisms | **total cells** | ratio to next | **r** |
|---|---|---|---|---|---|
| L1 | 970,752 | 12,288 | **983,040** | — | — |
| L2 | 119,808 | 3,072 | **122,880** | **8.000000** | **2.000000** |
| L3 | 14,592 | 768 | **15,360** | **8.000000** | **2.000000** |
| L4 | 1,728 | 192 | **1,920** | **8.000000** | **2.000000** |
| L5 | 192 | 48 | **240** | **8.000000** | **2.000000** |

**Cross-check, independent of the binary:** `(IDIM−1)(JDIM−1)(KDIM−1)` from the `.nmf`
reproduces **all five totals exactly** — 983,040 / 122,880 / 15,360 / 1,920 / 240. Two
independent readers, one binary and one text, agree to the unit.

**Third, independent corroboration — average element volume**, from
`M6I_runs/mesh/wing_strct_heff_vol.txt` (the generator's own output, neither of the above
readers):

| step | Ave(element vol) ratio | implied `r` = cube root |
|---|---|---|
| L2/L1 | 7.9806 | **1.9984** |
| L3/L2 | 7.9224 | 1.9935 |
| L4/L3 | 7.6917 | 1.9739 |
| L5/L4 | 6.8005 | 1.8932 |

**A family refined in only two of three directions would give `r_vol` = 4 and a cube root of
1.587.** The measured 1.998 at the fine end is not consistent with 1.587 by any margin.
⚠ **The degradation toward the coarse end (1.893 at L5/L4) is stated, not hidden**: average
volume is a distributional statistic and drifts as the coarse levels stop resolving the
boundary layer. **The exact `8.000000` on cell COUNT is the load-bearing figure; the `heff`
column is corroboration and is labelled as such.**

### 1.3 Patch-count reconciliation — measured from the `.ugrid` BC tag arrays

**⚠ A SECOND CORRECTION TO AN INHERITED FIGURE.** The reconciliation
`7,680 + 7,680 + 12,288 = 27,648` is **L1's alone**. It is **NOT** "27,648 on all three
levels" — the surface counts fall by 4× per level, exactly as surface counts must.

| level | tag 4000 (wall) | tag 6662 (symmetry) | tag 5050 (farfield) | **total** | OpenFOAM `defaultFaces` nFaces |
|---|---|---|---|---|---|
| L1 | 7,584 quad + 96 tri = **7,680** | **12,288** | 7,584 quad + 96 tri = **7,680** | **27,648** | **27,648** ✓ |
| L2 | 1,872 + 48 = **1,920** | **3,072** | 1,872 + 48 = **1,920** | **6,912** | **6,912** ✓ |
| L3 | 456 + 24 = **480** | **768** | 456 + 24 = **480** | **1,728** | **1,728** ✓ |
| L4 | 108 + 12 = **120** | **192** | 108 + 12 = **120** | **432** | not imported |
| L5 | 24 + 6 = **30** | **48** | 24 + 6 = **30** | **108** | not imported |

**The reconciliation holds exactly at every level, and the tri/quad split — which the
inherited figure did not carry — is resolved here.** The right-hand column is read from
`M6I_runs/L{1,2,3}/constant/polyMesh/boundary`; the total the sidecars predict is the total
OpenFOAM holds, to the face, on all three imported levels.

---

## 2. THE FOUR REGISTERED DEFECTS

### 2.1 D-ILLPOSED — the import as it sits is ill-posed. **Repairable, not intrinsic.**

All three imported levels carry **exactly one patch, `defaultFaces`, `type wall`** — the
closed-all-wall-box signature that is Sanaa's own surviving blocking class. `plot3dToFoam`
discarded the boundary conditions; **the `.mapbc` and `.ugrid` sidecars still hold them**, and
§1.3 proves they reconcile to the face.

**The repair: re-import from `.lb8.ugrid` + `.mapbc` through `cases/committee-grids/ugrid_to_foam.py`.**
That converter maps `4000 → wall`, `6660–6669 → symmetry`, else `patch` (its `foam_type()`,
:26–32) — which covers `6662` and `5050` as required. **It already carries an endianness
guard built by a byte-budget identity rather than a heuristic, and its own docstring names
`M6I_runs/mesh/wing_strct.{3,4,5}.lb8.ugrid` as the files that broke the previous heuristic**
(:59–70). **The converter is already hardened on these exact files.**

⚠ **NOT VERIFIED BY THIS LANE:** that the converter runs to completion on these five grids.
It has never been pointed at them. That is stage `B3` and is a prediction, not a fact.

### 2.2 D-PATCHNAME — a patch-NAME trap, and a worse BC-TYPE trap beneath it

**The name trap, confirmed:** `wing_strct.1.mapbc` names patches **lowercase**
`wing / symmetry / farfield`; levels **2–5** name them **uppercase**
`WING3D / SYMMETRY / FARFIELD`. A three-level driver gets different patch names on L1.

**🔴 A SECOND TRAP THIS LANE FOUND, WHICH IS WORSE AND WAS NOT IN THE BRIEF.** The `.nmf`
sidecars disagree on the boundary **TYPE**, not merely the name:

| level | `.nmf` face-4 type | `.mapbc` code | agree? |
|---|---|---|---|
| **L1** | **`symmetry_y`** | 6662 (symmetry) | **yes** |
| L2 | **`back_pressure`** | 6662 (symmetry) | **NO** |
| L3 | **`back_pressure`** | 6662 (symmetry) | **NO** |
| L4 | **`back_pressure`** | 6662 (symmetry) | **NO** |
| L5 | **`back_pressure`** | 6662 (symmetry) | **NO** |

**On four of five levels the two sidecars for the SAME grid disagree about whether a face is
a symmetry plane or a pressure outlet.** A symmetry plane misread as a back-pressure outlet
on the root plane of a half-wing is a physics error, not a bookkeeping one — it would leak
the wing root.

**REGISTERED REFUSAL `R-PATCH` (below) covers both traps.** ⚠ **This lane does NOT rule which
sidecar is right.** The `.mapbc` is self-consistent across L2–L5 and is the file the
converter reads; the `.nmf` is the generator's own topology map. **Which one is authoritative
is UNRESOLVED and is stage `B3`'s first question.**

### 2.3 D-REYNOLDS — the `y⁺` target's Reynolds convention

**Measured from the namelist actually on disk**, `M6I_runs/mesh/input.nml`:

- `target_reynolds_number = 14.6e6` — its own inline comment: *"Target Reynolds number based
  on the root chord (=1.0 in the grid)."*
- `target_y_plus = 0.25`

**REGISTERED CONVENTION: `Re = 14.6e6` on the SHARP ROOT CHORD. This is the mesh's convention
and it is NOT AGARD's.** AGARD AR-138 case 2308 carries `REC = 11.72e6` **on the MAC**. The
two reconcile: `14.6e6 × (0.64607 / 0.810491) = 11.64e6` against `11.72e6` — **0.7 %**.

> **THE REGISTERED HAZARD, STATED SO A SOLVE CANNOT MAKE IT SILENTLY: a solve that used
> `14.6e6` on the MAC would be wrong by 25 %.** The registered solve state uses **AGARD's
> `Re = 11.72e6` on the MAC**; `14.6e6` appears ONLY as the mesh generator's `y⁺` input and
> never as a flow condition. Any case file carrying `14.6e6` as a flow Reynolds number is a
> **`GATE FAIL` on `Gate A`**, not a warning.

### 2.4 🔴 D-MISSING-IGES — a recorded artifact that is not on the box

`M6I_IMPORT_GEOMETRY_VERIFICATION_2026-09-01.md` §1.2 records `AileM6_with_thick_TE.igs` as
**"held on this box, 150,903 B."**

**A controlled whole-box sweep by this lane finds NO such file.** `find / -xdev` for
`*.igs`/`*.iges` returns **exactly 2 files**, both OpenCascade sample data
(`/usr/share/opencascade/data/iges/{bearing,hammer}.iges`); `-iname '*AileM6*'` returns
nothing. **The sweep carries a live positive control in two forms**: it found two real IGES
files (so it can see the extension), and a planted lookup for a known file
(`M6I_runs/mesh/wing_strct.1.mapbc`) returned that file (so it can see that directory).
**A zero from this reader is evidence.**

**This is the third instance of this failure mode on this box**, after AGARD Table B1-1's
machine copy. **Registered as a missing dependency.**

> **RULED: NOTHING IN THIS REGISTRATION DEPENDS ON THAT FILE, AND NOTHING MAY BE BUILT THAT
> DOES WITHOUT SAYING SO.** The blunt-TE geometry this family needs is available from **two
> other sources that this lane confirmed present** (§3.1), so the missing IGES is a recorded
> defect, not a blocker.

---

## 3. THE TWO REPAIRS — REGISTERED AS FALSIFIABLE PREDICTIONS

> ### ⚠ NEITHER REPAIR IS ASSERTED TO WORK.
> Both are **cheap, untested predictions with a stated falsifier**. The source document
> refuses twice to claim the route clears the gate (§0.1), and **this registration holds that
> line.** A prediction that fails is a **`GATE FAIL`** recorded as a finding, not a defect in
> this document.

### 3.1 REPAIR 1 — the sharp trailing edge. **The arithmetic is EXACT and this lane proved it.**

**⚠ `om6_wing_section_sharp.dat` is SINGLE-COLUMN with a count header `63`, then 126 values
(63 `x`, then 63 `y`).** A two-column parser returns **ZERO rows** — the C19 defect exactly.
**That wrong parser is run as this section's planted control and its zero is shown**, so the
correct parse is evidence and not an assumption.

**The finding, which is stronger than "drop a point":** this lane compared all 63 section
points against the AGARD Table B1-1 machine copy now on the box,
`models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat` (72 rows, two-column,
1,512 B, dated 2026-09-03 23:02).

> **62 of the 63 points are EXACT AGARD Table B1-1 rows, to all seven printed figures.
> Exactly ONE is not: `(1.0055000, 0.0000000)` — the appended sharpening point.**
>
> **`sharp[−2]` is `(1.0000000, 0.0007052)`, which IS AGARD's own final row, identically.**

| quantity | as shipped | after dropping the appended point | AGARD B1-1 |
|---|---|---|---|
| TE ordinate | 0.0000000 | **0.0007052** | **0.0007052** |
| mirrored `t_TE/c` | 0.0000000 | **0.0014104** | **0.0014104** |
| **chord** | **1.0055000** | **1.0000000** | 1.0000000 |

**A SECOND DEFECT THE ARITHMETIC EXPOSES, NOT PREVIOUSLY RECORDED: the shipped section's
chord is 1.0055, not 1.0 — a 0.55 % chord extension.** The sharpening did not merely close
the trailing edge; it lengthened the aerofoil. **Every `x/c` abscissa in a `Cp` plot from
this geometry, and every chord-based Reynolds number, inherits that 0.55 %.**

⚠ **AND AN UNRESOLVED QUESTION THIS LANE WILL NOT GUESS AT.** The namelist notes state
*"Root chord will be normalized as 1.0 for any input airfoil data."* **Whether the generator
normalises by `max(x)` — and therefore whether the shipped grid is AGARD scaled by 0.99453
with a distorted aft region, or AGARD with a 0.55 % tail — is NOT DETERMINED by this lane and
is a `B0` question.**

**The 10 AGARD rows the sharp file discards are `x/c` = 0.9662, 0.9732, 0.9792, 0.9843,
0.9885, 0.9921, 0.9952, 0.9978** (plus one LE and one mid-chord row) — **eight of the ten sit
in the aft 3.4 %, exactly the region that governs trailing-edge `Cp`.**

**REGISTERED PREDICTION `P1`** — two variants, `P1b` preferred because it costs the same:

- **`P1a` (minimal):** regenerate from the 62-point section with the appended point removed.
- **`P1b` (preferred):** regenerate from **all 72 AGARD Table B1-1 rows**, restoring the eight
  discarded aft rows. Same generator, same cost, strictly more aft resolution.

> **`P1` PREDICTS:** the regenerated family's root section has **`t_TE/c` = 0.0014104 ± 1e-7**
> and **chord = 1.0000000 ± 1e-7**, measured on the emitted surface, not on the input file.
>
> **`P1` IS FALSIFIED IF:** the generator refuses a blunt section; **or** it silently
> re-sharpens; **or** the emitted `t_TE/c` differs from 0.0014104 by more than 1e-7; **or**
> the emitted grid dimensions change from §1.1 (which would break the family, not fix the
> geometry).

**COST: 0.1667 core-min, MEASURED** — `M6I_runs/COST.tsv`, `generate` 1 wall s (0.0167) +
`coarsen` 9 wall s (0.1500), 1 rank. **This is a measured re-run of a stage that has already
run on this box at these dimensions.**

**WHY THIS MATTERS MORE THAN IT LOOKS.** M6SR's `Gate P` is graded on **`x/c ≤ 0.90`**, with
*"the rear 10 % plotted and reported, never graded"* — **because that family is sharp-TE
while AGARD is blunt.** **If `P1` holds, this family is the only one the lab has that could
grade the rear 10 %.** ⚠ **That is a consequence of `P1`, not a claim that `P1` holds.**

### 3.2 REPAIR 2 — the 87° non-orthogonality is on a namelist that is NOT the production one

**Measured by this lane from the `checkMesh` logs of the existing import:**

| level | max non-orthogonality | **faces > 70°** | fraction of cells | `checkMesh` closing line |
|---|---|---|---|---|
| L1 | **87.7462°** | **191,794** | 19.5 % | *"Non-orthogonality check OK."* |
| L2 | **86.4646°** | **24,774** | 20.2 % | *"Non-orthogonality check OK."* |
| L3 | **87.6620°** | **3,686** | 24.0 % | *"Non-orthogonality check OK."* |

> 🔴 **A REGISTERED TRAP IN THE TOOL ITSELF. `checkMesh` prints "Non-orthogonality check OK."
> on a mesh with 191,794 faces above 70°.** A launcher that gates on `checkMesh`'s closing
> line — or on the string `Mesh OK` — **admits this mesh.** See refusal `R-NONORTHO`.

**🔴 A CORRECTION TO THE BRIEF THIS LANE IS OBLIGED TO MAKE.** The brief states the 87° is
"on the DEMO namelist." **The namelist on disk is neither the demo nor the production one.**
Measured against `M6I` §5.3/§5.5's published figures:

| parameter | demo (§5.3) | **on disk** | production `input.nml_wing_strct_2_stt` |
|---|---|---|---|
| `nnodes_cylinder_input` | 32 | **64** | 320 |
| `nre` | 64 | **128** | 448 |
| `nr_gs` | 8 | **16** | 64 |
| `target_y_plus` | 1.0 | **0.25** | 0.5 |
| `stretching_tanh_towards_lete` | 4.5 | **4.5** | **1.0** |

**The 87.75° was measured on a lab-modified variant at 2× the demo's counts, with `y⁺` driven
to 0.25 — and with `stretching_tanh_towards_lete` still at 4.5.** That last parameter is,
per `M6I` §5.5 verbatim, *"precisely the parameter that controls clustering into the leading
and trailing edges, where the severe faces sit."* The same section states: *"Whether the
production grid clears 70° is UNKNOWN and is the first thing the ladder must measure."*

**REGISTERED PREDICTION `P2`:** regenerate the family with `stretching_tanh_towards_lete`
**4.5 → 1.0**, all other parameters held at the on-disk values, and measure max
non-orthogonality with `checkMesh` on all five levels.

> **`P2` PREDICTS:** max non-orthogonality **falls** relative to the 87.75° / 86.46° / 87.66°
> baseline of the table above, on all three of L1/L2/L3.
>
> **`P2`'s GATE:** `MESH_STANDARD.md`'s 70° criterion, applied to the **measured maximum**,
> never to `checkMesh`'s closing line.
>
> **`P2` IS FALSIFIED IF:** max non-orthogonality does not fall, **or** falls but stays
> above 70°, **or** the grid dimensions change from §1.1.

⚠ **`P2` PREDICTS A DIRECTION, NOT A VALUE. This lane does NOT predict that 70° is cleared,
and the source document explicitly declines to.** A fall to 78° falsifies nothing about the
mechanism and still **fails the gate** — both outcomes are recorded.

⚠ **A SECOND, INDEPENDENT REASON `P2` MAY NOT SUFFICE, REGISTERED SO IT IS NOT A SURPRISE.**
The severe-face **fraction** is 19.5 % / 20.2 % / 24.0 % — it barely moves with refinement, so
the severe faces are a **persistent topological feature**, most plausibly the collapsed pole
axis (the `pole` BC on face 3, and the 12,288 prisms at L1). **If the severe faces are on the
pole and not the LE/TE, `stretching_tanh_towards_lete` cannot reach them and `P2` fails for a
reason that has nothing to do with clustering.** `B4` must therefore report **WHERE** the
severe faces are, not only how many.

**🔴 `N-C6` IS DECLINED, EXPLICITLY.** `M6I` R0 §4 declined the `N-C6` mechanism because the
maximum is **flat, not rising**, which is not `N-C6`'s signature. This lane's own measurement
reproduces that flatness (87.75 / 86.46 / 87.66 across a 64× cell range — no trend).
**`N-C6` is not claimed here.**

**COST: 0.1667 core-min, MEASURED** — same basis as `P1`; the grid dimensions are unchanged,
so the generator's measured runtime carries over.

---

## 4. GATES, THRESHOLDS, CAPS, LABELS

**The verdict vocabulary is `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
`BLOCKED` / `PENDING` and nothing else.**

### Gate F — FAMILY IDENTITY. Graded before anything else. Cap **1.0 core-min** (`B5`).

| # | threshold | label if met | label if not |
|---|---|---|---|
| F1 | five levels emitted, dims exactly as §1.1 | `PASS` | `GATE FAIL` |
| F2 | total cells (hex+prism) exactly 983,040 / 122,880 / 15,360 / 1,920 / 240 | `PASS` | `GATE FAIL` |
| F3 | cell ratio **8.000000** and `r` **2.000000** at all four steps, exact | `PASS` | `GATE FAIL` |
| F4 | `(n−1)` ratio **exactly 2** in **all three** index directions at all four steps | `PASS` | `GATE FAIL` |
| F5 | every level a `sha256` of its own points array, all five distinct, all recorded | `PASS` | `GATE FAIL` |
| F6 | little-endian planted control refuses the big-endian read | `PASS` | **`NOT A RESULT`** — an unproven reader grades nothing |

**`F6` failing makes `F1`–`F5` `NOT A RESULT`, not `GATE FAIL`.** A reader not shown able to
see the wrong answer has not been shown able to see the right one (rule 3).

### Gate GF — GEOMETRY FIDELITY. Graded **BEFORE any solve**. Cap **1.0 core-min** (`B0`).

| # | threshold | label |
|---|---|---|
| GF1 | emitted root section `t_TE/c` = **0.0014104 ± 1e-7** | `PASS` / `GATE FAIL` (**this is `P1`**) |
| GF2 | emitted root chord = **1.0000000 ± 1e-7** | `PASS` / `GATE FAIL` |
| GF3 | emitted root section max │Δz│/c against the 72 AGARD rows, **REPORTED, ungraded** | value + interval |
| GF4 | LE sweep **30.0°**, residual reported | `PASS` / `GATE FAIL` |
| GF5 | two-column control parser on the section file returns **ZERO** | `PASS` / **`NOT A RESULT`** |

**`GF3` is REPORTED AND NOT GRADED, deliberately.** No threshold on it is defensible before
the value exists, and inventing one after would be the exact thing rule 2 exists to prevent.

### Gate Q — MESH QUALITY. Cap **1.0 core-min** (`B4`).

| # | threshold | label |
|---|---|---|
| Q1 | max non-orthogonality **< 70°** on L1, L2, L3, from the **measured maximum** | `PASS` / `GATE FAIL` (**this is `P2`'s gate**) |
| Q2 | max non-orthogonality **falls** from 87.7462 / 86.4646 / 87.6620 | `PASS` / `GATE FAIL` (**this is `P2`'s direction**) |
| Q3 | **location** of the severe faces — pole vs LE/TE — **REPORTED, ungraded** | census |
| Q4 | max skewness, reported against `MESH_STANDARD.md` | `PASS` / `GATE FAIL` |
| Q5 | exactly **three** patches per level, `wall` + `symmetry` + `patch`, counts per §1.3 | `PASS` / `GATE FAIL` |

**`Q1` and `Q2` are separate on purpose.** `Q2` `PASS` with `Q1` `GATE FAIL` is the outcome
in which the mechanism is real and insufficient — the most informative result available and
the one most likely to be blurred if the two were merged.

### Gate P — SURFACE `Cp` AT THE AGARD SPAN STATIONS. **SANAA'S DELIVERABLE.** Cap in `B7`.

`Cp` at the seven published sections — **`2y/b` = 0.20, 0.44, 0.65, 0.80, 0.90, 0.96, 0.99**
(`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.txt:13729`) — against
the tunnel data, **with the family band on every station**.

| band channel | value | status |
|---|---|---|
| numerical (mesh) | **`GCI_fine`** from the L1/L2/L3 triple, `Fs = 1.25` | **`PENDING` — measured only if Gate G is `CONVERGING`** |
| reference accuracy | **`ΔCp = ±0.02`** at `M∞ = 0.84`, AR-138 B1-4 §6.1 | published |
| read-off | **ZERO** — machine-readable at a pinned hash | claimed and defensible |

**Grading extent is conditional on `GF1`, and this is the registration's single most important
conditional:**

- **`GF1` `PASS`** (blunt TE achieved) → **`Gate P` is graded over the FULL chord, `x/c ≤ 1.0`.**
- **`GF1` `GATE FAIL`** (still sharp) → **`Gate P` is graded on `x/c ≤ 0.90` only**, the rear
  10 % plotted and reported and **never graded**, exactly as M6SR does — because a sharp-TE
  geometry compared to blunt-TE tunnel data measures our own geometry error and calls it
  validation.

**`Gate P` sits behind `Gate G`. A `PASS` on a family that is not `CONVERGING` is
`NOT A RESULT`.**

### Gate G — GRID BEHAVIOUR. Cap **0** (host arithmetic, in `B7`).

**Roache triple gating, unmodified (rule 5).** Any level not iteratively converged or not
plateaued → **`NOT A RESULT`**. Triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` →
**`NOT A RESULT`**, with the value and both triples printed beside it. `CONVERGING` → `PASS`
inside the pre-registered band, else `GATE FAIL`. **GCI at `Fs = 1.25`, and never quoted when
the three values are not monotone.**

> **⚠ THE ONE THING THIS FAMILY IS FOR, STATED PLAINLY.** This is the only M6 family on the
> box whose refinement is **three-directional including wall-normal** (§1.1). **Its `Gate G`
> band is therefore a true discretisation-uncertainty estimate, not a lower bound.** M6SR's
> band is a **surface-refinement sensitivity band and a LOWER BOUND**, and every M6SR figure
> says so. **Nothing here relabels M6SR's bound, and nothing here is a band until `Gate G`
> returns `CONVERGING`.**

---

## 5. REGISTERED REFUSALS — WHAT A LAUNCHER MUST STOP ON

Per M6SR §7 point 5. **Each is a refusal, not a warning. `BLOCKED`, not a degraded run.**

| id | condition | why |
|---|---|---|
| **`R-PATCH`** | patch **names** differ across levels, **or** any level's `.nmf` face type disagrees with its `.mapbc` code | §2.2 — L1 is lowercase and L2–L5 uppercase; L2–L5's `.nmf` says `back_pressure` where `.mapbc` says `symmetry` |
| **`R-NONORTHO`** | the quality gate reads `checkMesh`'s closing line or the string `Mesh OK` instead of the **measured maximum** | §3.2 — `checkMesh` prints "OK" at 87.75° with 191,794 severe faces |
| **`R-ENDIAN`** | the `.ugrid` reader accepts a byte order not proven by the total-byte-budget identity | §1.2 — a big-endian read of these files implies a negative file size |
| **`R-2COL`** | a two-column parser is pointed at `om6_wing_section_sharp.dat` | §3.1 — it returns zero rows silently; the C19 defect class |
| **`R-HEXONLY`** | cell count taken as hexes alone | §1.2 — gives 8.103/8.211/8.444/9.000, not 8 |
| **`R-RE`** | any case file carrying `14.6e6` as a **flow** Reynolds number | §2.3 — 25 % error on the MAC |
| **`R-DEFAULTFACES`** | any level presenting a single `defaultFaces` wall patch | §2.1 — the ill-posed closed-box class |
| **`R-IGES`** | any step depending on `AileM6_with_thick_TE.igs` | §2.4 — it is not on this box |
| **`R-SUBSTITUTE`** | a level sourced from a different generator than the other four | inherited from M6SR §1.5's standing prohibition — it breaks the one property the family exists to have |

---

## 6. COST — FROM MEASURED RATES, STAGED SO A FAILED PREDICTION COSTS NOTHING

**Unit: core-minutes** (wall s × ranks ÷ 60). **Dollars are DERIVED, NOT MEASURED**, at
`c7a.4xlarge` **$0.0513/core-h**, owner-stated 2026-08-21/22. The box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure here is
**reported-by-owner and derived.**

**Rate basis, each with its honesty label:**

| rate | value | basis |
|---|---|---|
| generator + coarsener | **0.1667 core-min per full 5-level build** | **MEASURED on this exact family at these exact dimensions** — `M6I_runs/COST.tsv`, 1 + 9 wall s, 1 rank |
| `ugrid_to_foam` | **4.4455 s/invocation + 8.0669e-6 s/cell** | **MEASURED**, two-point fit through `cases/committee-grids/logs/DPW5_hex_convert.log` (638,976 cells, 9.6 s) and `DPW5_hybrid_convert.log` (2,981,888 cells, 28.5 s). ⚠ **The per-invocation intercept is 4.4 s and dominates every level below ~550k cells — a prior estimate that omitted it under-costed this stage by ~5×.** |
| `checkMesh` | **0.0892 core-min/Mcell** | **MEASURED on this family** — `M6I_runs/COST.tsv`, 0.1000 core-min over 1.12128 Mcell. ⚠ RUNG0b's cross-lab figure is **0.0661**, i.e. *lower*; **the higher, family-native figure is registered.** |
| solve | **3.40e-8 core-min/cell/iteration** | **MEASURED on this exact geometry and solver class** — `A3-onera-m6-transonic/run_model_run3.log`, 399,360 cells, recorded at `M6I_PREREGISTRATION.md:698`. Same basis M6SR registered. |

**Iteration schedule 3,000 / 4,000 / 5,000 at L3 / L2 / L1** — mirrored from M6SR so the two
families' costs are comparable.

### THE REGISTERED COST TABLE

**STAGE 1 — BUILD AND ADMISSION. Runs first. Cheap. Both predictions are decided here.**

| step | what | est. core-min | **cap** | derived $ at cap | ranks |
|---|---|---|---|---|---|
| `B0` | `Gate GF` — section geometry vs the 72 AGARD rows, + control `GF5` | **0.05** | **1.0** | $0.00086 | serial |
| `B1` | **`P1`** — regenerate 5 levels from the blunt AGARD section | **0.17** | **1.0** | $0.00086 | serial |
| `B2` | **`P2`** — regenerate 5 levels with `stretching_tanh_towards_lete` 4.5 → 1.0 | **0.17** | **1.0** | $0.00086 | serial |
| `B3` | `ugrid_to_foam` import, 5 levels × 2 variants (repairs `R-DEFAULTFACES`) | **1.05** | **3.2** | $0.00274 | serial |
| `B4` | `Gate Q` — `checkMesh` 5 levels × 2 variants + severe-face location census | **0.20** | **1.0** | $0.00086 | serial |
| `B5` | `Gate F` — family identity proof + planted endianness control | **0.02** | **1.0** | $0.00086 | serial |
| | **STAGE 1 TOTAL** | **1.66** | **8.2** | **$0.00701** | |

**STAGE 2 — SOLVES. CONDITIONAL. Not launched unless `Gate F` and `Gate Q` return `PASS`.**

| step | what | est. core-min | **cap** | derived $ at cap | ranks / decomposition |
|---|---|---|---|---|---|
| `B6a` | solve L3, 15,360 cells × 3,000 it | **1.57** | **4.8** | $0.00410 | `hierarchical (4 1 1)` |
| `B6b` | solve L2, 122,880 cells × 4,000 it | **16.71** | **50.2** | $0.04292 | `hierarchical (8 1 1)` |
| `B6c` | solve L1, 983,040 cells × 5,000 it, **incl. a named ×2.0 superlinear allowance** | **334.23** | **1,002.7** | $0.85731 | `hierarchical (16 1 1)` |
| `B7` | grade — `Gate G` Roache triple → `Gate P`. Host arithmetic. | **0.02** | **2.0** | $0.00171 | serial |
| | **STAGE 2 TOTAL** | **352.53** | **1,059.7** | **$0.90604** | |
| | **ALL-IN** | **≈ 354.19** | **1,067.9** | **≈ $0.9131 DERIVED** | |

**`est ≤ cap` holds on every one of the ten rows** — checked by arithmetic, not by eye.

**THE ×2.0 SUPERLINEAR ALLOWANCE ON `B6c`, NAMED NOT BURIED.** The 3.40e-8 rate's basis is a
399,360-cell mesh. `B6b` (122,880) and `B6a` (15,360) extrapolate **downward** — the safe
direction. `B6c` (983,040) extrapolates **upward by 2.46×**. M6SR applied ×2.0 for a **4×**
extrapolation; **the same ×2.0 is applied here for a smaller extrapolation, so this allowance
is strictly more conservative than the one already registered.** ⚠ **The mechanism (working
set outgrowing cache) is INFERRED, not instrumented. No PMU counter is collected and none is
claimed.**

### 6.1 THE COMPARISON SANAA'S ORDER ASKS FOR

| | M6SR (committee family) | **M6F (this family)** |
|---|---|---|
| est. core-min | 615.24 | **354.19** |
| cap core-min | 1,903.0 | **1,067.9** |
| derived $ at cap | $1.6270 | **$0.9131** |
| refinement directions | **surface only (2 of 3)** | **all three, incl. wall-normal** |
| band meaning | **LOWER BOUND** on discretisation uncertainty | **a true band, if `Gate G` is `CONVERGING`** |

**M6F is cheaper than M6SR by 261.05 core-min estimated and 835.1 core-min at cap, and it is
the one of the two that can produce a true three-direction band.** Both sit inside the $1,000
envelope with the two together at **$2.54 DERIVED at cap**, which is 0.25 % of it.

### 6.2 ⚠ THE CALIBRATION WARNING THAT ATTACHES TO EVERY MESHING ROW ABOVE

**The only calibration datum this lab holds for `hcf` meshing is M6I R0's
actual/predicted = 0.0064 — the estimate was 157× HIGH** (`M6I_runs/R0_RESULTS.md:159–160`).

**Stated rather than silently trusted:** the meshing rows `B1`, `B2`, `B4` rest on rates
measured *from that same under-run*, so they are **more likely conservative than optimistic**,
and their caps are correspondingly generous relative to any real risk. **The row that carries
the actual risk is `B6c`, whose rate comes from a different campaign and a 2.46× cell-count
extrapolation.** A rule-12 calibration row for every completed stage is filed to
`docs/COST_CALIBRATION.md` at completion, stating the ratio and attributing the gap.

---

## 7. WHAT THIS REGISTRATION CANNOT DELIVER, STATED BEFORE IT IS ASKED

1. **It cannot promise `Cp` over the full chord.** That depends entirely on `GF1`/`P1`, which
   is untested. **If `P1` fails, this family grades `x/c ≤ 0.90` exactly as M6SR does**, and
   the rear 10 % is plotted, never graded.
2. **It cannot promise a `Gate G` band at all.** A non-`CONVERGING` triple is `NOT A RESULT`
   (rule 5), and no amount of correct meshing forces convergence.
3. **It cannot promise the mesh is admissible.** `Q1` is `P2`, and `P2` is untested. **If the
   severe faces are on the pole axis rather than the LE/TE, `P2` cannot help** (§3.2), and the
   family is `BLOCKED` on mesh quality at a cost of 1.66 core-min — which is the entire point
   of staging.
4. **It resolves nothing about which `.nmf`/`.mapbc` sidecar is authoritative** (§2.2). That
   is `B3`'s first question and is `UNRESOLVED` here.
5. **It does not determine whether the generator renormalises the chord** (§3.1). `B0`.
6. **`AileM6_with_thick_TE.igs` remains missing** (§2.4) and nothing here depends on it.

---

## 8. THE GRADING PATH — IT EXISTS, AND IT ALREADY REFUSES

**Rule 2 fixes the grading path at the pre-registration commit.** Two graders are committed
with this document and every figure in §1 and §3.1 is reproducible from them:

| script | grades | current verdict on the artifacts as they stand |
|---|---|---|
| `scripts/verify_m6_family_identity.py` | `Gate F` (F1–F4, F6) and refusals `R-ENDIAN`, `R-HEXONLY`, `R-PATCH` | **`BLOCKED`, rc=2 — `R-PATCH` FIRES** |
| `scripts/verify_m6_section_against_agard.py` | `Gate GF` input-file limb, refusal `R-2COL` | **`PASS`, rc=0** |

> **THE REFUSALS ARE NOT HYPOTHETICAL. `R-PATCH` fires TODAY, on the family as it sits**, on
> both limbs: L1's lowercase names against L2–L5's uppercase, and the `.nmf`/`.mapbc`
> disagreement on four of five levels. **A launcher wired to this grader stops before it
> spends a core-minute.**

**Both graders were run under `python3 -O` and their verdicts are unchanged** (identity rc=2,
section rc=0). **Every guard is a `Refusal` exception, never an `assert`** — `-O` deletes
assert statements, and a comparator whose entire guard set vanishes under an interpreter flag
is a rubber stamp. Both planted controls are live: the identity grader is shown rejecting the
big-endian read, the section grader is shown returning zero rows from the two-column parser,
and **each refuses to grade anything if its own control fails** (`NOT A RESULT`, not a
degraded pass).

**On freeze, the two scripts are hashed against their committed blobs, and the run verifies
the frozen file IS the file that ran.**

---

## 9. AMENDMENT RECORD

*(none — this document has never been frozen and no compute has run against it)*
