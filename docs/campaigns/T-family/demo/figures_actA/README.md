# Act A screen data products — what each file is, and every artifact it came from

**Prepared by a heat-transfer `lab-lane` at the heat-transfer-supervisor's
dispatch, 2026-09-01.** These are DATA PRODUCTS for the Act A screens of
`etc/sessions/2026-09-01T0032Z_sanaa_thermal_acts_full_spec.md` (commit
`a3793b8f`). **Nothing here was solved.** Every number is read from a field, a
mesh or a monitor file that was already on disk when this directory was
created. **No solver was launched, no case was written to, and no `.tex` sheet
was touched.**

This directory is deliberately separate from
`docs/campaigns/T-family/demo/figures/`, which another lane owns for Act C.
Nothing here reads or writes anything in that directory.

---

## 1. THE FILES

| file | what it is |
|---|---|
| `actA_map_table.{pdf,svg}` | the sixteen-point peak-temperature map: a shaded grid with an unclipped colour bar carrying its printed min and max, above the sixteen rows with units and the uncertainty column |
| `actA_map_table.csv` | the same sixteen rows, machine-readable |
| `actA_envelope.{pdf,svg}` | peak temperature against airspeed, one curve per power, the 200 °C limit line labelled, the safe region shaded, and the margin to the limit drawn at the hottest solved point |
| `actA_envelope.csv` | the sixteen points plus the two limit levels |
| `actA_radial_profile.{pdf,svg}` | radial temperature cut through the hottest solid cell, four panels, three material regions annotated with their measured slopes |
| `actA_radial_profile.csv` | every cell of that cut: region, radius in mm, temperature in °C — plus the near-wall air at all four airspeeds |
| `actA_monitor_replay.{pdf,svg}` | sixteen tiles, one per operating point, replayed from each run's own monitor file |
| `actA_monitor_replay.csv` | all 1600 monitor samples (16 cases × 100 samples) |
| `actA_assumption_beat.{pdf,svg}` | hand model against the coupled solve: absolute temperatures, the overprediction factor, and the power headroom the solved rise implies at 20 m/s |
| `actA_assumption_beat.csv` | the four airspeeds with both closures and both factors |
| `actA_screen_data.json` | everything above in one file, so a mission can re-render without re-deriving |
| `make_act_a_screens.py` | the build. Re-run it from this directory; it rewrites every file above |
| `mesh_reader_actA.py` | the cell-centre reader the radial profile needs, with its own planted-zero control |

---

## 2. SOURCE ARTIFACTS, BY PATH

### 2.1 The sixteen solved cases

Peak temperature is read from each case's own end-time housing temperature
field, by the **frozen comparator's own reader** (`read_Q1`, imported, not
copied):

| point | field read |
|---|---|
| 80 W, 10/20/30/40 m/s | `verification/runs/T-family/T24_runs/T24_P080_U{10,20,30,40}/10000/housing/T` |
| 155 W, 10/20/30/40 m/s | `verification/runs/T-family/T24_runs/T24_P155_U{10,20,30,40}/10000/housing/T` |
| 230 W, 10/20/30/40 m/s | `verification/runs/T-family/T24_runs/T24_P230_U{10,20,30,40}/10000/housing/T` |
| 305 W, 10/20/30/40 m/s | `verification/runs/T-family/T23_runs/T23_P305_U{10,20,30,40}/10000/housing/T` |

Completion markers, sixteen:
`verification/runs/T-family/T24_runs/DONE.T24_P{080,155,230}_U{10,20,30,40}` and
`verification/runs/T-family/T23_runs/DONE.T23_P305_U{10,20,30,40}`.

### 2.2 The parsing that was reused rather than re-implemented

- `verification/runs/T-family/T24_runs/analyse_t24.py` — imported by path.
  `read_Q1`, `internal_window`, `patch_value_window`, `_foam_list`,
  `patch_face_areas`, `plant_Q1`, `planted_zero_control` and the plant
  magnitude `PLANT = 1.234e-03 K` all come from it. Nothing it already does is
  re-implemented here.
- `verification/runs/T-family/T23_runs/analyse_t23.py` — read before writing any
  reader; its `read_Q1` / `read_Q2` / plant structure is the same and the T24
  file is the one imported, so one code path serves all sixteen points.
- `scripts/roache_triple.py` — the origin of `PLANT`, reached through the
  comparator's own import, never redefined here.

### 2.3 The mesh, for the radial profile

Real computational mesh, never an STL tessellation. Cell centres are computed
from each case's own `polyMesh` by the OpenFOAM decomposition:

- `verification/runs/T-family/T23_runs/T23_P305_U10/constant/{core,housing,fluid}/polyMesh/{points,faces,owner,neighbour,boundary}`
- and the same paths under `T23_P305_U{20,30,40}` for the near-wall air curves.

Geometry that names the material regions:
`verification/runs/T-family/T23_runs/T23_P305_U10/build_t23.py` lines 32-70 —
shaft bore 6 mm, rotor core to 33.5 mm, aluminium housing wall 33.5-37.5 mm,
air annulus 37.5-125 mm; 24 / 8 / 110 radial cells.

### 2.4 The monitors

`verification/runs/T-family/<rung>_runs/<case>/postProcessing/housing/housing_T/0/fieldMinMax.dat`
for all sixteen cases — the run's own function-object output, written every 100
iterations during the solve, 100 samples per case. **Replayed unchanged; not
regenerated and not simulated.**

### 2.5 The narrative records the figures agree with

- `docs/campaigns/T-family/CASE3_MAP_RESULTS.md` — §1 the sixteen values, §2.1
  the +96.3922 K margin, §2.2 the extrapolated crossing powers, §4 the
  single-mesh-level statement.
- `docs/campaigns/T-family/T23_RESULTS.md` — §1.2 the hand model's absolute
  predictions (lines 77-82), §2 the overprediction factors (lines 104-109).
- Grading outputs, cited but not re-graded here:
  `verification/runs/T-family/T24_runs/gate_t24.json`,
  `verification/runs/T-family/T23_runs/T23_GRADE.json`,
  `verification/runs/T-family/T23_runs/T23_GRADE.txt`.

---

## 3. THE UNCERTAINTY COLUMN IS HONESTLY EMPTY, AND THIS IS WHY

`CASE3_MAP_RESULTS.md` §4, in bold, frozen before compute at
`T24_PREREGISTRATION.md` §0.3:

> ALL SIXTEEN POINTS OF THIS MAP RAN AT MESH LEVEL L1 AND ONLY L1. THE MAP IS
> NOT GRID-CONVERGED. THERE IS NO DISCRETISATION ERROR BAR ON ANY POINT OF IT,
> AND NONE CAN BE CONSTRUCTED FROM WHAT WAS RUN.

So the map table's uncertainty column reads **`not available - single grid, no
grid-refinement error estimate`** on all sixteen rows. It does **not** read
`0`, it does not read a borrowed figure from another campaign, and it does not
read an interpolated one. The cell text is deliberately `not available` rather
than `none`, because `none` can be misread as *zero uncertainty*.

**What the envelope plot draws instead.** The spec asks the envelope screen for
an "uncertainty margin". There is no numerical uncertainty to draw, so the
envelope draws the **MARGIN TO THE 200 °C LIMIT** — a real measured temperature
difference, `+96.3922 K` at the hottest solved point — and labels it *margin to
the limit* in the figure, with a caption saying in terms that it is not a
numerical error bar. **That substitution is deliberate and is recorded here so
nobody has to reverse-engineer it.**

---

## 4. THE THREE RADIAL SLOPES — WHAT IS ACTUALLY THERE

The spec's A6.2 asks for a radial profile with three annotated slopes. Measured
at the axial station holding the hottest solid cell (z = 124.554 mm), at 305 W
and 10 m/s:

| region | radial span | temperature drop | mean slope | straight-line fit |
|---|---:|---:|---:|---:|
| rotor core | 6.583 – 32.899 mm | 3.9122 K | **−0.1500 K/mm** | R² = 0.9525 |
| housing wall | 33.718 – 37.215 mm | 0.1014 K | **−0.0290 K/mm** | R² = 0.9990 |
| cooling air | 37.476 – 124.866 mm | 86.9514 K | **−0.3221 K/mm** | R² = 0.2901 |

**Three distinct regions exist and their three mean slopes are distinct — but
only one of the three is a straight line.** The housing wall is straight to
four decimals. The rotor core carries a volumetric heat source and is curved;
the cooling air carries a thermal boundary layer and is strongly curved,
running from **−146.0 K/mm at the housing surface** to **0.0000 K/mm in the
free stream**. The figure prints the region-mean slope, the R² beside it, and
the words *"a single slope here is a region average, not a local gradient"* on
the two curved panels. **Nothing was segmented to manufacture three straight
lines that are not in the data.**

---

## 5. THE MONITOR TILES — WHAT WAS TILED, AND ONE HONEST OFFSET

Each tile is the run's own `fieldMinMax` output on the housing region: the
**maximum** and **minimum** temperature in that solid, sampled every 100
iterations, 100 samples to iteration 10000. The band between the two traces is
shaded. **These are the solver's own numbers, replayed.**

**One definitional offset, stated rather than smoothed.** The monitor scans the
housing cells **and its bounding faces**; the map table's peak scans the
**internal cells only**. At the hottest point the monitor settles at
**103.6228 °C** against the table's **103.6078 °C** — an offset of
**0.0150 K**. This was verified at source, not inferred: the extra 0.0150 K is
the maximum of the `housing_to_core` interface `value` list in
`T23_P305_U10/10000/housing/T`, which reads exactly 103.622845 °C. Both numbers
are correct readings of the same solution and the figure's footer says so.

---

## 6. THE ASSUMPTION BEAT — DIRECTION OF THE TREND

Measured, at 305 W, from `T23_RESULTS.md` lines 104-109 and reproduced against
this lane's own re-read of the sixteen fields:

| airspeed | duct closure, model rise / solved rise | flat-plate closure |
|---:|---:|---:|
| 10 m/s | **3.541** | **2.031** |
| 20 m/s | 3.369 | 1.947 |
| 30 m/s | 3.280 | 1.911 |
| 40 m/s | **3.235** | **1.896** |

> **THE OVERPREDICTION SHRINKS AS AIRSPEED RISES. THE LARGEST ERROR IS AT THE
> LOWEST AIRSPEED.** The figure states the direction and the four numbers.

**NO PHYSICAL MECHANISM FOR THE TREND IS PRINTED ANYWHERE**, in the figure or
in this file, because **no record on disk states one**. `T23_RESULTS.md` §2
records that the lumped model overpredicts by 1.90× to 3.54× beyond the 1.763×
spread between its own two closures, and it records that this falsifies the
level-selection instrument. It offers no mechanism for the trend across
airspeed, so neither does this directory. A plausible story is not a
measurement.

**The equivalent-power reading, verified.** At 20 m/s the solved rise is
**54.1598 K** at 305 W. Scaling that linearly in power gives **592.2 W** to
reach 120 °C and **1042.7 W** to reach 200 °C — matching the 592 W / 1043 W in
`CASE3_MAP_RESULTS.md` §2.2. **Both figures are EXTRAPOLATIONS**: the highest
power solved anywhere for this case is 305 W, and the figure labels both bars
`EXTRAPOLATED` on their faces.

---

## 7. PLANTED-ZERO CONTROLS — `CLAUDE.md` rule 3

Three distinct readers were built or reused, and **each was shown able to see a
known perturbation before any of its output was believed.** The plant magnitude
is `1.234e-03 K`, imported from `scripts/roache_triple.py` through the frozen
comparator and never redefined.

| reader | control | result |
|---|---|---|
| peak-temperature field reader | the frozen comparator's own `planted_zero_control`, all nine clauses | planted 1.234000e-03 K, read **1.234000e-03 K**; detection floor **1e-06 K**; one cell planted |
| radial-profile reader | `mesh_reader_actA.planted_profile_control` — plant into one internal cell by line index, require the perturbation to reappear at exactly one radius | planted 1.234000e-03 K, read **1.234000e-03 K** at r = 0.035717 m, **exactly 1** sample perturbed |
| monitor-trace reader | `make_act_a_screens.planted_monitor_control` — plant into the maximum column of one row by line index | planted 1.234000e-03 K, read **1.234000e-03 K**, **exactly 1** sample perturbed |

Every control **copies to scratch first and checks afterwards that the case file
is byte-identical**; none writes into a case directory. A reader that could not
see the plant would **refuse at exit 2**, not degrade.

**Anchor reproduction.** The build re-derives all sixteen values from the fields
and refuses to continue unless the five known anchors reproduce to 1e-4 °C:
38.1374 / 29.0795 / 25.5462 / 23.5897 °C at 80 W and 103.6078 °C at 305 W,
10 m/s. **All five matched.**

---

## 8. WHAT THIS DIRECTORY DOES NOT CONTAIN

- **No verdict.** Nothing here grades anything; the grading artifacts of §2.5
  hold the verdicts and are not restated in any figure.
- **No numerical uncertainty**, for the reason in §3.
- **No temperature or velocity field images** (the spec's A6.1) and **no mesh
  or boundary-layer zoom** (A3) — those need a field renderer this directory
  does not build, and they are named here as a gap rather than approximated.
- **No cost figures.** The estimate-versus-actual calibration for these runs is
  already filed at `docs/COST_CALIBRATION.md`, rows
  `C-20260831T183346.079343Z-d971eca8` and
  `C-20260831T210913.811885Z-2663ea60`; this directory adds no compute and so
  produces no new calibration row.
- **Nothing is sent.** `CLAUDE.md` rules 7 and 8: submissions are PARKED and
  this repository is permanently private. These files stay in it.

**One note for whoever wires the mission.** `actA_screen_data.json` carries a
`source_field` path per row for audit. Those paths are provenance, not screen
content: **do not render them.** Everything intended for a screen is in the
CSVs and in the plotted arrays.
