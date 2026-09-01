# ACT A (motor in duct) — GUI CONTENT SPECIFICATION

**Status: DRAFT FOR HEAT-TRANSFER SUPERVISOR APPROVAL. Nothing here has reached a
screen. The verification lines and the certificate block in §5 REQUIRE the
supervisor's approval before capture.**

Authority: Sanaa's six GUI fixes for the jet-flap act, `etc/sessions/2026-09-01T1900Z_sanaa_jf1_gui_fixes.md`
(commit `85d52954`), which she states apply to the motor and battery acts too;
and her convergence-prerequisite doctrine,
`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`
(commit `f4c8e466`), which fixes what this act may CLAIM.

Division of labour: the cfd team owns the SHARED MACHINERY (panel sequencing,
header wiring, the small-multiple monitor component, the Report/Conclusion tab
structure) and everything under `sdk/`. This document is ACT-SIDE CONTENT only.
Where a fix needs a machinery change, it is named here as a **cfd dependency**
and not made.

The act module is `/home/ubuntu/Certonomous/sdk/workflows/motor_thermal_act.py`
(registered as `motor-thermal`). Read, not edited, in preparing this spec.

---

## 0. THE ACT IN ONE PARAGRAPH, SO THE CONTENT BELOW IS CHECKABLE

Sixteen steady conjugate operating points — four dissipated powers (80, 155,
230, 305 W) by four duct airspeeds (10, 20, 30, 40 m/s) — solved with
`chtMultiRegionSimpleFoam` on ONE mesh level of **39,680 cells over 3 regions**
(35,200 fluid, 1,120 housing, 3,360 core), axisymmetric over a 5-degree wedge.
Cell counts read from
`/home/ubuntu/Certonomous/verification/runs/T-family/T23_runs/T23_T24_MESH_FACTS.json`
(`cells.total`, `regions.n`), which records them as identical across all 16
cases by sha256 of `constant/<region>/polyMesh/points` over all 48 region-case
pairs.

---

## 1. PANEL SEQUENCE: GEOMETRY → MESH → FIELDS, NOTHING ELSE

Sanaa: *"Geometry panel shows geometry, then the mesh, then fields — nothing
else."*

| Panel stage | Exact artifact, absolute path | Notes |
|---|---|---|
| **Geometry** (renders on load) | `/home/ubuntu/Certonomous/sdk/geometry/t23_solved_geometry.stl` | sha256 `d2864232dbf6d87a89c7a2dab4fdf232bc61eae405cb35a174f364d24a935cc9`, 90,084 bytes, 1,800 facets. This is the SERVED copy — the one the control-room server resolves — and §2 governs it. |
| Geometry, part labels | `/home/ubuntu/Certonomous/verification/runs/T-family/T23_runs/display_surface/t23_solved_geometry_parts.json` | Six parts in `part_order`: duct, centrebody_upstream, housing_heated, centrebody_downstream, inlet_truncation_cap, outlet_truncation_cap. The STL's 2-byte facet attribute is the part index. |
| **Mesh** (replaces the tessellation) | `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actA/actA_mesh_boundary_layer.pdf` (and `.png`, `.svg`) | Rendered title *"Computational mesh at the cooled surface, three zooms"*; the innermost zoom is a 30 mm window carrying 2,806 cells. |
| Mesh, the numbers beside it | `/home/ubuntu/Certonomous/verification/runs/T-family/T23_runs/T23_T24_MESH_FACTS.json` | 39,680 cells / 3 regions. Wall-unit table comes from `T23_GRADE.json` → `<case>.yplus`, already wired at `motor_thermal_act.py` `mesh_plan()`. |
| **Fields** | `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actA/actA_temperature_field.png` then `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actA/actA_velocity_field.png` | The two `Results.fields` entries. Underlying cell data: `figures_actA/actA_field_cells.csv` and `figures_actA/actA_field_render_data.json`. |

**Nothing else in this panel.** The following are RESULTS-beat artifacts and must
NOT appear in the geometry/mesh/fields panel: `actA_map_table.pdf`,
`actA_envelope.pdf`, `actA_radial_profile.pdf`, `actA_monitor_replay.pdf`,
`actA_airspeed_thumbnails.png`, `actA_assumptions.pdf`, `actA_assumption_beat.pdf`.

### ⚠ ONE HONESTY CONSTRAINT ON THE MESH PANEL THAT THE JET FLAP DOES NOT HAVE

`T23_T24_MESH_FACTS.json` records `mesher.derived_from_an_STL: false`, with the
note *"The solved mesh is a parametric structured wedge. It is NOT built from
any surface file, so meshing an uploaded STL with snappyHexMesh would NOT
reproduce it."*

The jet-flap act meshes its surface. **Act A does not.** The mesh panel must
therefore not animate "meshing the uploaded STL", and no caption may imply the
displayed grid was cut from the displayed surface. The truthful transition
sentence, screen-safe:

> The grid is built directly from the case's own dimensions as a structured
> wedge, not cut from the surface file.

---

## 2. THE STL RENDERS ON LOAD AND MUST BE THE SOLVED GEOMETRY

### 2.1 What I actually measured — the defect is REAL but NOT where the brief placed it

The brief records this as a live defect in Act A. **Measured, it is not a defect
in the demo-mode act.** `motor_thermal_act.py` already:

- declares `SERVED_STL = SERVED_GEOMETRY_DIR / "t23_solved_geometry.stl"` (line 89),
- runs the surface generator's own geometry guard over the SERVED copy
  (`measured_surface()`, lines 310–327), which refuses a strut, a nose, a tail
  or a wrong axial extent,
- asserts the served copy is **byte-identical** to the generated one
  (`_assert_served_copy_is_current()`, lines 330–350).

And the served file is correct today:

```
d2864232…  sdk/geometry/t23_solved_geometry.stl
d2864232…  verification/runs/T-family/T23_runs/display_surface/t23_solved_geometry.stl
```

**Reported plainly: the demo-mode Act A path is clean. I could not reproduce the
defect as stated.**

### 2.2 What IS live, and it is the same class of defect

The retired body is still on disk at **two paths with one digest**, and a fix
naming one leaves the other standing:

| Path | sha256 | bytes |
|---|---|---|
| `/home/ubuntu/Certonomous/sdk/geometry/motor_in_duct.stl` | `131aab8e17242415364d2f1147a76cfbdc7fe5f48287a0996c2318249857db5f` | 314,484 |
| `/home/ubuntu/Certonomous/cases/demo-surfaces/motor_in_duct.stl` | `131aab8e17242415364d2f1147a76cfbdc7fe5f48287a0996c2318249857db5f` | 314,484 |

Retired in our own manifest,
`verification/runs/T-family/T23_runs/display_surface/t23_solved_geometry_parts.json`,
key `retires`, reason recorded there verbatim: *"dimensioned from
F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md, a different case; 0.200 m axial
against the solved 0.750 m; three unsolved struts; nose and tail the solve does
not have."*

**And `/home/ubuntu/Certonomous/cases/demo-surfaces/generate_demo_stls.py`
regenerates it**, so deleting the files without fixing the generator restores
the defect on the next run of that script.

Three live reachability paths, measured:

1. **The geometry API resolves by NAME out of `sdk/geometry/`.** `demo_mode.py`
   lines 130–136 record that `server.py` resolves a named geometry and lands an
   upload at `HERE.parent / "geometry"`. Any route that names
   `motor_in_duct.stl` therefore renders the retired body.
2. **Stale mission-state replays do exactly that — in THREE logs, not two.**
   All 783 `*.events.jsonl` files under
   `/home/ubuntu/Certonomous/sdk/chief-engineer-runs/mission-state/` were parsed
   deterministically this session (JSON per line, not by text search — a `grep`
   sweep over the same directory returned an inconsistent subset, which is the
   ugrep ignore/race behaviour of L-`grep-honours-ignore-files` and is why this
   was enumerated in Python instead). Exactly three logs emit `geometry.ready`
   pointing at the retired body:

   | Log | `mission.routed` intent | `geometry.ready` label |
   |---|---|---|
   | `m-5c2ad641e8d8.events.jsonl` | `geometry-study` | `Motor in duct` |
   | `m-b7d49b915bc2.events.jsonl` | `geometry-study` | `Motor in duct` |
   | **`m-942be0f630b7.events.jsonl`** | **`thermal-display`** | **`reference body: Motor in duct`** |

   All three carry `"url": "/api/geometry?name=motor_in_duct.stl"`.

3. **The third one is the dangerous one, and it is a THERMAL route.**
   `m-942be0f630b7` is not a geometry study. Its intent is `thermal-display`,
   its own rationale reading *"Reading this as a thermal question about a body
   this lab has already run. No solver starts and no new number is produced: I
   will put the screens up from that run's…"*. **It is a thermal mission serving
   the retired geometry under the label "reference body".** That is the defect as
   originally briefed, found at last on this route rather than in the demo-mode
   act. A fix that quarantines only the two `geometry-study` logs leaves this one
   standing — the same "one path fixed, the other still there" pattern as the two
   STL copies, one level up.

   The two `geometry-study` logs are additionally a non-thermal run: an *assumed*
   100 m/s freestream, 445,436 cells, 300 iterations, C_d 3.389 — incompressible
   external aero. See §5.3, where this becomes a certificate problem.

### 2.3 The swap, specified precisely

**Act-side (ours, and already satisfied — to be held, not changed):** Act A is
driven only through the registered `motor-thermal` demo-mode act, whose served
surface is `sdk/geometry/t23_solved_geometry.stl` and whose two guards above
must remain in force. No capture of Act A may use the legacy `geometry-study`
route.

**cfd dependencies (theirs — `sdk/` and `cases/` are outside our scope):**

- **D-A1** Remove or quarantine `/home/ubuntu/Certonomous/sdk/geometry/motor_in_duct.stl`.
- **D-A2** Remove or quarantine `/home/ubuntu/Certonomous/cases/demo-surfaces/motor_in_duct.stl`.
- **D-A3** Fix `/home/ubuntu/Certonomous/cases/demo-surfaces/generate_demo_stls.py` so it
  no longer regenerates the retired body. **D-A1 and D-A2 without D-A3 are not a fix.**
- **D-A4** Quarantine or gate **all THREE** stale mission-state event logs named
  in the §2.2 item 2 table — `m-5c2ad641e8d8`, `m-b7d49b915bc2` **and
  `m-942be0f630b7`** — so none can be replayed into a capture. **The third is the
  `thermal-display` one and is the one most likely to be reached from a thermal
  prompt; a fix naming only the two `geometry-study` logs is not a fix.**
- **D-A5** Correct `/home/ubuntu/Certonomous/cases/demo-surfaces/README.md` line 12,
  which still labels `motor_in_duct.stl` as *"DEMO STANDARD v2 Act A — motor in
  duct"*. That label sends the next reader straight back to the retired body and
  is now false: Act A's surface is `t23_solved_geometry.stl`.
- **D-A6** Note, no action required for capture:
  `/home/ubuntu/Certonomous/models/curriculum/uq-studies/motor_in_duct.json`
  declares `"body": "motor_in_duct"` with missions `motor_in_duct-rung-coarse`,
  `-rung-medium` and `-production`. That is the same non-thermal geometry-study
  family that produced the stale mission-state logs, and it is a UQ curriculum
  entry rather than a display path — but it is the reason those missions exist,
  and it should not be re-run into `mission-output/` before D-A1..D-A4 land.

A repository-wide sweep for `motor_in_duct` this session returned exactly these
paths plus the two STLs, the retiring manifest, the surface generator, three
`PROPOSED_*_NOTE.md` drafts, `docs/LAB_STATE.md` and
`etc/sessions/2026-09-01T0320Z_sanaa_actA_geometry_screen.md`. **The only code
that WRITES the retired body is `generate_demo_stls.py` (D-A3).**

A one-line check that D-A1..D-A3 held, for whoever does the work:

```
sha256sum sdk/geometry/*.stl cases/demo-surfaces/*.stl | grep -c 131aab8e   # must be 0
```

---

## 3. HEADER STATUS LIVE, REAL VALUES NOT FIXED

### 3.1 Stage strings, in order, for Act A

The contract's `demo_mode.STAGES` (9 stages) and `demo_mode.BANNERS` (7 banner
states) are the machinery. Sanaa's requested header sequence maps onto them as
follows. **Act A's solving stage sweeps SIXTEEN points, not five**, so the
counter reads to 16.

**⚠ SUPERSEDED BY THE SHOOTING PROTOCOL (`cfcf766f`), Screen 2.** Her stage list
is fixed and has **seven** entries, including one this spec previously lacked
entirely — **`Reading the geometry`**. The mapping below is now hers, not ours;
`Fleet at work` and `Feasibility` are NOT stage names on her list and must not
appear in the header.

| # | **Header string Act A must show (Sanaa's Screen 2, verbatim order)** | Underlying `STAGES` entries |
|---|---|---|
| 1 | `Forming the team` | `prompt` |
| 2 | **`Reading the geometry`** | `geometry` |
| 3 | `Planning` | `restatement`, `assumption` |
| 4 | `Meshing` | `meshing` |
| 5 | `Solving (n of 16)` | `feasibility`, `solving` |
| 6 | `Checking` | `gates` |
| 7 | `Report` | `results` |

Her wording is `Solving (n of N)`; for Act A, N = 16.

**Note the reordering this forces.** Her sequence reads the geometry at stage 2,
*before* planning. The contract's `STAGES` order is
prompt → restatement → assumption → geometry → …, i.e. geometry at position 4,
*after* planning. **The header must follow her order.** Whether the underlying
stage walk is reordered to match, or the header maps onto it as above, is cfd's
call — but the header must never show `Planning` while the geometry panel is
what the viewer is looking at (her Screen 2: "match what is on screen").

**cfd dependency D-A7:** `Reading the geometry`, `Checking` and `Report` do not
exist in the machinery. `BANNERS` maps `geometry` → `"fleet at work"`,
`gates` → `"solving"` and `results` → `"results"`. All three strings are a
change to `sdk/workflows/demo_mode.py`, which is cfd's file. We specify the
strings; we do not make the change.

**cfd dependency D-A8:** `Solving (n of 16)` needs a live point index.
`SolveReplay.sweep_points` is already `len(solved_points())` = 16
(`motor_thermal_act.py` line 592), so the denominator has a real source; the
numerator N is a machinery counter.

### 3.2 The four header fields — where each real value comes from

| Field | Real source | Verdict |
|---|---|---|
| **agents** | `MotorThermalAct.agent_census()`, `motor_thermal_act.py` lines 758–761, consumed by the sequencer at `sdk/workflows/demo_sequencer.py:353`. Per stage: prompt 1, restatement 2, assumption 3, geometry 3, meshing 4, feasibility 4, solving 6, gates 3, results 0. | **REAL SOURCE — display it**, stepping with the stage. |
| **human touchpoints** | I searched `demo_mode.py`, `demo_sequencer.py` and `sdk/chief_engineer/server.py` for `touchpoint` / `human_touch`: **no match anywhere.** The only defensible count is a derived one — the number of stages requiring human input, which for this act is **1** (the `prompt`). | **NO LIVE SOURCE.** Either display the derived `1` labelled as *"points where a person was asked: 1"*, or do not display the field. **A live-looking counter must not be shown.** |
| **cycle** | Searched the same three files for `"cycle"`: **no match.** | **NO REAL SOURCE — MUST NOT BE DISPLAYED.** |
| **workers** | `sdk/chief_engineer/server.py:376` — `workers = int((query.get("workers") or ["8"])[0])`. This is a caller-supplied query parameter with a hardcoded default of **8**. It measures nothing about the act. | **NO REAL SOURCE for a header field — MUST NOT BE DISPLAYED.** Showing it displays the literal default 8 as if it were telemetry, which is the exact "fixed value" Sanaa is objecting to. |

A true alternative to `workers`, if a compute-shaped number is wanted: the act's
rank count is **1**, read from each solver log's `nProcs` header
(`motor_thermal_act.py::ranks`), and `campaign_cost()` refuses if the sixteen
points disagree. Label it *"ranks: 1"*, not "workers".

---

## 4. SMALL MULTIPLES — THE SIXTEEN-POINT MAP

Act A's analogue of the jet flap's five sweep points is the **sixteen-point
map**: 16 monitor traces side by side, advancing together, so the map completes
in one pass instead of sixteen sequential clips.

### 4.1 Layout — 4 × 4, which the physics already gives us

The sweep is a product of two variables, so the tiles are a grid, not a strip:

- **rows = dissipated power**, 4 rows: 80, 155, 230, 305 W (top row hottest,
  305 W, so the eye lands on the governing case first);
- **columns = duct airspeed**, 4 columns: 10, 20, 30, 40 m/s (left to right,
  cooling increasing rightward).

Each tile is therefore identified by its (row, column) position and needs no
per-tile legend.

### 4.2 Quantity per tile

**Hottest point in the housing wall, in °C, against solver iteration** — one
trace per tile, advancing in step across all 16.

Source per tile, live: `<case>/postProcessing/housing/housing_T/0/fieldMinMax.dat`,
column `max`. This is already the second `SeriesSpec` in
`motor_thermal_act.py::solve_replay()` (lines 593–595), so the component needs
no new reader. The 16 case directories are discovered by
`motor_thermal_act.py::solved_points()` across
`/home/ubuntu/Certonomous/verification/runs/T-family/T23_runs/` and
`/home/ubuntu/Certonomous/verification/runs/T-family/T24_runs/`.

Replay-ready pre-extracted copy (already rendered as the static
`actA_monitor_replay.pdf`, titled *"Housing temperature monitors, sixteen
runs"*): `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actA/actA_monitor_replay.csv`.

A second bank of 16 residual tiles may reuse the third `SeriesSpec`
(`log.solve`, `p_rgh` residual) on the same grid, shown after the temperature
bank rather than beside it — 32 simultaneous tiles is past legibility.

### 4.3 Axis treatment, so 16 tiles stay legible

- **One shared y-range across all 16 tiles**, so tile-to-tile height is
  comparable at a glance. Range from the recorded map colour range,
  `figures_actA/actA_screen_data.json` → `map_colour_range_degC`; the solved
  housing peaks span roughly 24.7 °C (80 W, 40 m/s) to 107.7 °C (305 W, 10 m/s)
  per `envelope.series_degC`.
- **Y tick labels on the leftmost column only**; y gridlines on all tiles.
- **X tick labels on the bottom row only**; shared x-axis = solver iteration.
- **One y-axis title for the whole block**, `Hottest housing temperature [°C]`,
  placed once at the left, not repeated 16 times.
- **The 200 °C limit line is NOT drawn on these tiles.** Every solved point sits
  far below it (worst margin 92.3 K, `envelope.worst_margin_K`); a limit line
  16 times over compresses every trace into the bottom of its tile and shows
  nothing. The margin belongs on `actA_envelope.pdf`, where it already is.
- **Row and column headers once each** — powers down the left, airspeeds along
  the top — not a 16-entry legend.
- Tiles that have already settled hold their final value rather than clearing,
  so the block reads as a map filling in.

---

## 5. THE ACT ENDS IN A REPORT

Five blocks, with Conclusion and Report tabs populated. Nothing ends on a table.

### 5.1 Results table — EXISTS, and its uncertainty column stays empty

`motor_thermal_act.py::results()` already builds Table `motor_thermal_map`,
16 rows, headers: Power W | Airspeed m/s | Hottest core °C | Hottest housing °C |
Rise above inlet K | Margin to the 200 °C limit K | **Uncertainty**.

The Uncertainty cell is the literal string `"not available"` on all 16 rows
(line 671). The backing record agrees: `actA_screen_data.json` →
`map_rows[*].numerical_uncertainty` =
*"not available - single grid, no grid-refinement error estimate"*.

**⛔ This column stays empty. It is empty by Sanaa's own ruling and by rule 5,
not by oversight.** See §5.2. No band, no GCI, no ± may be added to this table.

### 5.2 ⛔ VERIFICATION LINE — DRAFT, REQUIRES SUPERVISOR APPROVAL

Sanaa's jet-flap verification line is a POSITIVE claim (*"total lift within 4%
of the published jet-flap curve"*). **Act A has no such claim available.** What
we have, measured:

- **T23G is `NOT A RESULT` on all three graded quantities**
  (`docs/campaigns/T-family/T23G_RESULTS.md`, §3 verdict table): observed orders
  **0.3796, 0.3766, 0.3744**, all three triples **`STAGNANT`**, so `CLAUDE.md`
  rule 5 makes them `NOT A RESULT` whatever the value says.
- **No GCI is quoted, and that is not an omission** — rule 5 forbids a GCI beside
  a non-`CONVERGING` triple (`T23G_RESULTS.md` line 102).
- **T23G2 has not run.** Its pre-registration exists at
  `/home/ubuntu/Certonomous/docs/campaigns/T-family/T23G2_PREREGISTRATION.md`;
  there is no `T23G2_runs` directory.
- What DID pass: **G-REPRO**, at exactly `0.000e+00 K` against a ≤1e-06 K
  threshold (`T23G_RESULTS.md` §5), and **nine planted-zero controls**
  (3 quantities × 3 levels), every one `PASSED` at a 1e-06 K floor, on real
  fields (§3).

The internal verdict vocabulary never reaches a screen (contract R5), so these
are translated into plain words.

**Drafted verification lines for Act A — for the supervisor's approval:**

> 1. Reproduced from the fields on disk: **5** values re-read against the record
>    fixed before the runs started, agreeing to better than **3.7e-05 K**.
>    *(counts and residual are read LIVE by the act from `actA_screen_data.json`
>    → `len(anchor_checks)` = 5 and
>    `statements_of_fact.anchor_check_largest_residual_K` = 3.736100001106024e-05;
>    verified against the record this session. This line already exists in the
>    act and is unchanged — the figures above are what it will render.)*
> 2. Instrument check: **4** readers each detected a planted **1.234e-03 K**
>    perturbation, so a zero from any of them would have been a reading and not
>    a blind spot. *(already exists in the act, unchanged; counts verified —
>    `len(planted_zero_controls)` = 4, `planted_K` = 0.001234.)*
> 3. **RE-DRAFTED UNDER SCREEN 8 — see §5.2a.** Every temperature here came from
>    a single mesh, so no band is drawn on any row yet. The grid convergence
>    study for this case is running; the band lands in your inbox with the
>    certificate.
> 4. No rig or wind tunnel data exists for this configuration, so the
>    temperatures are shown as solved and no agreement with measurement is
>    claimed. *(already exists in the act, unchanged.)*

### 5.2a ⛔ SCREEN 8 AND THE ONE THING THAT COULD MAKE THIS ACT LIE

Her **Screen 8** is binding: *"The platform always runs it; the demo shows it as
done or as automatically underway, never as absent."* Act A cannot show it as
done — T23G is `NOT A RESULT` and T23G2 has not run — so Act A takes the
"automatically underway" form, which is what §5.2 line 3 and the §5.3 closing
line now say.

**⚠ THAT LINE IS NOT TRUE TODAY, AND SAYING IT WOULD BE THE WORST THING IN THIS
SPEC.** Measured this session:

- `verification/runs/T-family/T23G2_runs/` — **does not exist.**
- No T23G2 entry in `verification/queue/heat-transfer/` or its `launched/`.
- What DOES exist: the committed pre-registration
  `docs/campaigns/T-family/T23G2_PREREGISTRATION.md` and the builder
  `docs/campaigns/T-family/build_t23g2.py` (44,788 bytes, mtime 16:59).

So the study is **prepared and not launched.** The sentence *"The grid
convergence study for this case is running"* is a statement about the present,
and it is currently false.

**There is exactly one honest way to earn it: launch T23G2 before capture.**
That is heat-transfer's own work and the supervisor's call, and Sanaa's own
convergence doctrine (`f4c8e466` §7) already orders it — *"convergence studies
launch in parallel on every case named above, starting now."* Her §1 names the
motor explicitly.

**Until it is launched, Act A must not carry the line.** This is flagged as a
BLOCKING pre-capture item, not a drafting preference. The two lawful states are:

| State | What Screen 8 may say |
|---|---|
| T23G2 launched and running | *"The grid convergence study for this case is running; the band lands in your inbox with the certificate."* — her form, honest |
| T23G2 not launched | **Act A is not ready to shoot.** Do not substitute a softer sentence; launch the study. |

### ⛔ CURRENT STATE: DRAFTED, HELD, **PENDING LAUNCH CONFIRMATION**

**The Screen 8 sentence is written and is NOT cleared for publication.** It
appears in §5.2 line 3, in the §5.3 certificate block's closing line, and in the
§9.5 re-drafted conclusion. **All three occurrences are held.**

A T23G2 launch has been authorised by the coordinating lane, with the check-1
read of `build_t23g2.py` discharged against blob `d8207e1e`. **Authorisation is
not launch, and launch is not confirmation.** This lane runs no compute and did
not launch it.

**The release condition, and it is a measurement, not a message.** The line
becomes publishable only when the motor lane's launch is confirmed by pids and
advancing logs. The check a capture operator can run:

    ls -d /home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs/     # must exist
    find /home/ubuntu/Certonomous/verification/runs/T-family/T23G2_runs -name 'log.*' -mmin -10   # must be non-empty

**An authorisation relayed in a message is not evidence that a solver is
running.** Until a run tree exists with logs advancing, Screen 8 stays held and
Act A stays unshootable. Whoever clears it should record the confirming reading
here, beside this paragraph, rather than deleting the hold.

#### CONFIRMING READING — taken 2026-09-01 ~18:40Z, by this lane, read-only

The launch has landed. Measured directly, not relayed:

- `verification/runs/T-family/T23G2_runs/` **exists** (mtime 18:39Z).
- **Three levels present**: `T23G2_L1`, `T23G2_L2`, `T23G2_L3`, all mtime 18:40Z
  — the three geometrically similar meshes the convergence doctrine requires.
- **Six logs, all written within the preceding ten minutes**: `log.blockMesh`
  and `log.splitMeshRegions` on each of the three levels.
- The check-1 blob is confirmed: `git rev-parse HEAD:docs/campaigns/T-family/build_t23g2.py`
  = `d8207e1e6d220b3f075826b305948f40d80e2b0b`, matching the read that was
  discharged.

**State, stated precisely rather than favourably: MESHING IS COMPLETE ON ALL
THREE LEVELS; THE SOLVE HAS NOT STARTED.** There is no `log.solve` on any level
yet, and no queue entry under `verification/queue/heat-transfer/`.

**What this licenses.** The study is genuinely underway — three levels built
inside ten minutes is unambiguous activity, and the release condition above
(a run tree with logs advancing) is met. Her Screen 8 sentence *"The grid
convergence study for this case is running"* is **true as of this reading**.

**What it does not license.** Nothing about the *result*. No band exists, no
observed order exists, and none may be quoted or previewed. The uncertainty
column stays empty exactly as §5.1 requires until the three levels solve and
grade `CONVERGING`. **If the solve does not start, this reading goes stale the
same way §9.7's did** — re-derive it immediately before capture rather than
trusting this paragraph.

**Why the earlier draft was withdrawn.** The version first committed here said a
refinement study *"was run… and did not settle."* That is true, and it is a good
sentence for a lab record — but it narrates the current state of the lab, which
her preamble bans outright (*"Nothing narrates the current state of the lab"*),
and it shows the study as effectively absent, which Screen 8 bans. **The
withdrawal is a presentation change, not a retreat from the finding:** T23G's
`NOT A RESULT` verdict stands unaltered in `T23G_RESULTS.md`, the uncertainty
column still carries no invented number, and nothing here claims a band exists.
What changed is that the screen now points forward to the study that will
produce the band instead of backward to the one that failed.

**What must NEVER appear on an Act A screen:**
- any ± , band, GCI, or uncertainty figure on the sixteen-row table;
- the number 0.375 presented as a measured order of convergence supporting
  anything;
- the words "grid converged", "grid independent", or "mesh independent";
- any claim of agreement with measurement, published data, or a correlation
  (the hand correlation is shown as being *corrected*, at 3.5× too high — that
  is the assumption beat, not a validation).

### 5.3 ⛔ CERTIFICATE BLOCK — DRAFT, REQUIRES SUPERVISOR APPROVAL

**Only a PASS is a credential. Act A does not have one.**

Two measured hazards make this more than a wording question:

1. **The existing certificate machinery launders tiers.**
   `/home/ubuntu/Certonomous/sdk/chief_engineer/certificate.py` lines 49–50 and
   73–74 alias `TREND ONLY` → `SOLVER-BACKED` and
   `REFERENCE REGIME MISMATCH` → `SOLVER-BACKED`. A weak input becomes a
   confident badge on output. **`build_certificate_v2` must not be wired to Act A.**
2. **TWO certificates for "motor in duct" already exist on disk, and both are
   for the wrong run.** The same deterministic scan of all 783 mission-state
   logs (§2.2) found two `certificate.ready` events, not one:

   | Log | `certificate_no` | tier | `mission_id` |
   |---|---|---|---|
   | `m-5c2ad641e8d8.events.jsonl` | **C-2026-7101** | `SOLVER-BACKED` | `geometry-study-motor_in_duct` |
   | `m-b7d49b915bc2.events.jsonl` | **C-2026-3012** | `SOLVER-BACKED` | `geometry-study-motor_in_duct` |

   Both certify the 445,436-cell incompressible aero run of §2.2, **not** the
   conjugate thermal solve. Both write to
   `/home/ubuntu/Certonomous/mission-output/geometry-study/certificate.pdf`.

   **And that path is keyed by INTENT, not by body — it is last-writer-wins
   across different geometries.** The file sitting there now (10,806 bytes,
   mtime 2026-09-01 04:45Z) is **neither** of the two above. Read this session,
   it carries:

   > Certificate No. **C-2026-7890** · Fidelity: **SOLVER-BACKED** ·
   > Mission **geometry-study-airfoil_blown_slot**

   That is the **jet-flap** body. Three different geometries — `motor_in_duct`
   twice and `airfoil_blown_slot` once — have written a certificate to that one
   path, each overwriting the last.

   **Consequence for Act A:** a report surface that resolves "the geometry-study
   certificate" would today display a SOLVER-BACKED credential for the jet flap
   underneath the motor act. The certificate at that path cannot be identified by
   body without opening it, and its number is no guide to what it certifies.
   This is a second, independent reason the §5.3 refusal block must be rendered
   from an explicit "not issued" state and must never resolve a certificate by
   mission or intent name.

   **Worth flagging beyond this act:** the same last-writer-wins path affects any
   act whose output lands under `mission-output/<intent>/`, which is cfd's
   territory rather than ours — raised, not actioned.

**Proposed refusal form — the block says what was and was not established:**

> **CERTIFICATE — NOT ISSUED**
>
> This result is not certified. A certificate is issued only when a gate set
> before the run was met, and this act does not have one.
>
> **What was established:**
> • Sixteen operating points solved to completion on one grid, every point
>   checked against that grid before a temperature was read.
> • Every value on this sheet was re-read from the stored fields and matched the
>   record written before the runs started.
> • Every instrument used here was shown able to detect a planted signal, so its
>   readings are readings and not blind spots.
> • Air mass through the duct balances in against out.
>
> **What was NOT established:**
> • How much of each temperature is grid error. The refinement study for this
>   body did not settle, so no error bar exists for any row.
> • Agreement with any measurement. No rig or wind-tunnel data exists for this
>   configuration.
> • Anything outside a steady state: warm-up time and response to a load change
>   are not represented.
>
> The grid convergence study for this case is running. The band lands in your
> inbox with the certificate.

**⚠ RE-DRAFTED UNDER THE SHOOTING PROTOCOL (`cfcf766f`).** Two changes from the
version first committed here:

1. **The word "tier" is on her never-list**, so the block names none. It did not
   before either, but the prohibition is now explicit and the check is recorded.
2. **The closing line no longer says "No certificate number is assigned."**
   "ids" is on the never-list, and — more importantly — her **Screen 8** forbids
   showing the convergence study as absent. The closing line is now her own
   "lands in your inbox" form. **This is subject to §5.2a: it is honest only once
   T23G2 is actually launched.**

**Design rule for the machinery, to hand to cfd:** the certificate slot must
render this block from an explicit "not issued" state, and must have **no code
path that fills a tier, a badge colour or a certificate number when the act
supplies none**. A slot labelled "certificate" that defaults to anything is the
defect.

### 5.4 Limitations box — EXISTS, unchanged

Five entries already in `motor_thermal_act.py::results()` lines 737–749: single
grid so no discretisation error bar; axisymmetric 5-degree wedge; radiation off
in all three regions; each point a separate steady state; turbulent transport
modelled not resolved. All five are physics limitations, not software excuses.
Backing figure: `figures_actA/actA_assumptions.pdf`.

### 5.5 Cost line — MEASURED, and NOT divided by 5

Measured this session, read-only, from the sixteen `log.solve` files
(closing `ClockTime`, never `ExecutionTime`; `nProcs` from each log header):

| Quantity | Value | Basis |
|---|---|---|
| Points | 16 | `solved_points()` over T23_runs + T24_runs |
| Ranks | 1 (identical across all 16) | `nProcs` line of each `log.solve` |
| Wall time, summed | 34,727.0 s | closing `ClockTime` of each log |
| **Actual compute** | **578.78 core-minutes** | **measured** |
| Registered estimate | 483.6 core-minutes | summed over the 16 records in `verification/queue/heat-transfer/launched/` |
| **Ratio actual/predicted** | **1.20** | rule 12 calibration |
| Dollars | **$0.4949** | **DERIVED, NOT MEASURED**, at $0.0513/core-h, `cost_basis = REPORTED-BY-OWNER` |

**Screen line, proposed:**

> Compute used: 578.8 processor-minutes against a 483.6 forecast, 1.20 times the
> forecast. At this machine's recorded rate that is about $0.49, derived rather
> than measured.

**⚠ THE /5 IS NOT APPLIED HERE. See §7.**

### 5.6 Conclusion tab vs Report tab

- **Report tab** carries, in order: the sixteen-row results table (§5.1), the
  four verification lines (§5.2), the limitations box (§5.4), the cost line
  (§5.5), the certificate-not-issued block (§5.3).
- **Conclusion tab** carries the engineering answer in plain words, and must
  itself end on a sentence, not a table. Proposed, drafted from measured values
  (`envelope.worst_margin_K` = 92.322478961 K at the worst point, 305 W /
  10 m/s, computed on the core):

> Across the whole range asked for, the motor stays clear of its 200 °C limit.
> The worst case is the highest power at the lowest airspeed, and even there the
> hottest point in the core sits 92 K below the limit. The quick hand estimate
> that prompted this study put the housing 3.4 times hotter than the coupled
> solve found, measured as temperature rise above the incoming air at 305 W and
> 20 m/s. What this study cannot yet tell you is how much
> of that 92 K is grid error, because the refinement study for this body has not
> settled — that is the next run, not a caveat on this one.

---

## 6. FIGURE STANDARD — AUDIT OF EVERY ACT A FIGURE

Method: `pdftotext` over every figure PDF; first rendered line taken as the
in-figure title and word-counted; full text scanned case-insensitively for
`prelimin|draft|provisional|WIP`; generator source inspected where a table was
suspected.

**Banner result: `Preliminary` appears on ZERO of the ten Act A figures.** That
clause of fix 6 is already satisfied — reported as measured, not assumed.

| Figure (all under `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actA/`) | In-figure title (words) | Defect | Fix |
|---|---|---|---|
| `actA_temperature_field.pdf` / `.png` | "Temperature field, 305 W" (4) | none | **compliant** |
| `actA_velocity_field.pdf` / `.png` | "Air speed, 305 W" (4) | none | **compliant** |
| `actA_envelope.pdf` | "Peak core temperature against airspeed" (5) | none | **compliant** |
| `actA_radial_profile.pdf` | "Radial temperature through the hottest cell" (6) | none | **compliant** |
| `actA_monitor_replay.pdf` | "Housing temperature monitors, sixteen runs" (5) | none | **compliant** — and this is the static form of the §4 small multiples |
| `actA_mesh_boundary_layer.pdf` / `.png` | "Computational mesh at the cooled surface, three zooms" (8) | none | **compliant** |
| `actA_airspeed_thumbnails.pdf` / `.png` | "Temperature at four cooling airspeeds, 305 W" (7) | none | **compliant** |
| `actA_assumption_beat.pdf` | "Hand estimate versus coupled solve, 305 W" (7) | none on the standard | **compliant** |
| **`actA_map_table.pdf`** | "Peak core temperature, 16 operating points" (6) | **TABLE INSIDE A FIGURE.** `figures_actA/make_act_a_screens.py::fig_map_table` draws an `imshow` heatmap at **line 478** AND a full `ax2.table(cellText=body, colLabels=head, …)` at **line 518** in the same figure. This is precisely Sanaa's jet-flap defect ("move the measured-values table out of the pressure figure into the sheet"). | **Split it.** Keep the 4×4 `imshow` map as the figure; delete the `ax2.table` sub-axes; the measured values move to the sheet, where they already exist as the §5.1 results table and as `figures_actA/actA_map_table.csv`. |
| `actA_assumptions.pdf` | "What this result assumes" (4) | Not a measured-values table, so it does not trip her rule literally — it is a prose panel of four headed caveats. But it **duplicates the §5.4 limitations box**. | **No change required for capture.** Recommend the sheet carry the limitations box as text and this figure be shown only if the caveats are not otherwise on screen, so a viewer is not read the same four caveats twice. |

**One figure requires a change: `actA_map_table.pdf`.** Everything else in Act A
meets the standard as it stands.

Note the machinery already enforces the act-level side of this standard:
`demo_mode.Figure.__post_init__` refuses a title over 10 words, a caption over
20 words, or a caption containing a newline. What it does NOT see is the text
rendered *inside* the PDF by matplotlib — which is where the `actA_map_table`
defect lives, and why this audit read the rendered artifacts rather than the
act's `Figure(...)` declarations.

---

## 7. ⚠ COST-LINE DESK ITEM — RAISED, NOT APPLIED

Sanaa wrote: *"also change the 117.5 core minute mention to 117.5/5 ( i ran this
on my station after moving dafoam linear solves to gpu and this is the speedup i
have so we can already show that instead)"*.

**Measured scope of that instruction.** `117.5` occurs in this repository only
in jet-flap mission-state records — e.g.
`sdk/chief-engineer-runs/mission-state/m-4c4efcd5433c.events.jsonl` sequences
1266 and 1281, which carry *"Solved 5 sweep points, 40,000 iterations, at a cost
of 117.5 core minutes"* beside `Solver: OpenFOAM simpleFoam, steady
incompressible turbulent flow over a wing section with a blown trailing-edge
slot`. **It appears nowhere in Act A or Act C.** Her 117.5 → 23.5 instruction is
unambiguous FOR THE JET FLAP and is not touched by this spec.

**Why /5 is not applied to Act A.** Her measured basis is *DAFoam linear solves
moved to GPU on her own station*. Act A runs `chtMultiRegionSimpleFoam` on CPU,
on this box, at 1 rank, with no GPU port and no such measurement. Dividing
578.78 by 5 would claim a 5× speedup we have not measured, on a solver it was
not measured on, on hardware that does not have it. `COMPUTE_BUDGET_CHARTER` §5
and rule 12 both forbid calling that measured.

**Desk item, as I would put it to Sanaa (91 words):**

> Your 117.5 → 23.5 change is done for the jet flap. Before we extend it: the 5×
> you measured was DAFoam linear solves moved to GPU on your station. The motor
> and battery acts run chtMultiRegionFoam and buoyantBoussinesqSimpleFoam on CPU
> on this box, with no GPU port and no speedup measured on either. Dividing their
> cost lines by 5 would claim a speedup on a solver it was never measured on. Do
> you intend the /5 basis to extend to the thermal acts, or should they show
> their measured CPU cost — 578.8 and 19.8 core-minutes?

---

## 8. ASSETS THAT MUST EXIST AND DO NOT

| Asset | Path it must occupy | Why |
|---|---|---|
| Act A small-multiple replay component | cfd-owned, under `sdk/` | §4 specifies the content; the 16-tile component itself is shared machinery |
| `Checking` / `Report` banner strings | `sdk/workflows/demo_mode.py` `BANNERS` | §3.1 dependency D-A7 |
| Live sweep-point index for `Solving, point N of 16` | cfd-owned | §3.1 dependency D-A8 |
| Certificate "not issued" render path | cfd-owned | §5.3; must have no defaulting tier |
| T23G2 run tree | `verification/runs/T-family/T23G2_runs/` | **DOES NOT EXIST.** Pre-registration is committed at `docs/campaigns/T-family/T23G2_PREREGISTRATION.md`; until this runs and grades `CONVERGING`, §5.1's uncertainty column stays empty. |
| Corrected `actA_map_table.pdf` (heatmap only, table removed) | `docs/campaigns/T-family/demo/figures_actA/actA_map_table.pdf` | §6; requires an edit to `make_act_a_screens.py::fig_map_table` and a re-render |

**Not missing, confirmed present:** the solved STL, its parts manifest, the mesh
facts, all sixteen solver logs, all sixteen launched cost records, the monitor
series for all 16 tiles, and nine of the ten figures.

---

# 9. SHOOTING-PROTOCOL COMPLIANCE (`cfcf766f`, 2026-09-01 ~20:30Z)

Binding for every act. Supersedes conflicting presentation details in §1–§8
above; where a section was superseded it is marked in place rather than deleted.

## 9.1 ⚡ THE MOTOR BEAT — "the thermal-resistance estimate shown first, then corrected by the coupled solve; envelope with the 200 C line"

We have both halves and they are currently in the **wrong relationship**.

**What is wrong today.** `MotorThermalAct.assumption()` is stage 3 of the
contract walk, and it already delivers the *correction* — its `finding` field
states *"the quick estimate is 3.4 times too high"* — **before the coupled solve
has run on screen.** The estimate is therefore never on screen in its own right;
it arrives already demolished. The beat's whole content is the gap between the
two numbers, and a gap cannot land if the viewer never held the first number
alone.

**Screen A — THE ESTIMATE, ALONE (before the solve).** Shown as the answer an
engineer would reach for, stated with confidence, no hedging, no foreshadowing
of the correction.

| Quantity | Value | Source |
|---|---|---|
| Method | one-dimensional thermal resistance, duct correlation | `figures_actA/actA_screen_data.json` → `assumption_beat.duct_factor` |
| Housing temperature, predicted | **197.3 °C** | `T23_GRADE.json` → `T23_P305_U20.predicted_DB_degC` |
| Predicted rise above inlet air | **182.4 K** | derived: 197.3 − 14.9 °C inlet |
| Limit | **200 °C** | `actA_screen_data.json` → `envelope.limit_degC` |
| Margin on this estimate | **2.7 K** | derived |

The line that makes it land, present tense because it is what the team is doing:

> The hand estimate puts the housing at 197.3 °C against a 200 °C limit. On this
> number the design is marginal, and that is the answer an engineer gets in
> thirty seconds.

**Screen B — THE COUPLED SOLVE CORRECTS IT (after the solve).** Past tense,
because it is a result.

| Quantity | Value | Source |
|---|---|---|
| Peak housing temperature, solved | **69.0 °C** | `actA_screen_data.json` → `assumption_beat.solved_degC["20"]` |
| Solved rise above inlet air | **54.2 K** | `assumption_beat.solved_rise_at_20ms_K` |
| Inlet air | **14.9 °C** | derived: peak − rise; not typed anywhere, so a changed inlet cannot strand a constant |
| **Overshoot factor** | **3.4×** on temperature rise | `T23_GRADE.json` → `DB_over_solved`, cross-checked in `_correlation_rises()` |
| Operating point | 305 W, 20 m/s | `PRIMARY` |

> The coupled solve found the housing at 69.0 °C. Measured as rise above the
> incoming air, the hand estimate ran 3.4 times hot — 182 K predicted against
> 54 K solved. The design was never marginal.

**Both sides are named on screen.** A bare "3.4 times" invites pairing with
whichever number is largest in view, and the largest number on this act belongs
to a different operating point and a different solid. The act's own docstring
already insists on this and the requirement is retained.

**Screen C — THE ENVELOPE, carrying the 200 °C line.**
`docs/campaigns/T-family/demo/figures_actA/actA_envelope.pdf`, rendered title
*"Peak core temperature against airspeed"*, four curves (80, 155, 230, 305 W),
the **200 °C limit line** and the 120 °C design isotherm both already drawn, and
the worst margin annotated at **+92.3 K** (305 W, 10 m/s). No change required to
the figure — only its placement, which is third in this beat.

**Ordering dependency (cfd):** the correction must be sequenced after the
solving screen. Whether `assumption()` is split into a pre-solve estimate and a
post-solve correction, or the correction is relocated into `results()`, is
cfd's call. **The content and both numbers are fixed here.**

## 9.2 SCREEN 3 — ACKNOWLEDGEMENT (mandatory, and NEW for Act A)

One-sentence restatement plus a geometry table with **extent, reference lengths,
features found**, and confidence stated. Act A had no such table; this is
genuinely new.

Restatement (already exists, `Restatement.restatement`): *"Solve 16 operating
points, 4 dissipated powers by 4 duct airspeeds, and report the hottest solid
temperature and its margin to the limit at each."*

**Geometry table — every value from the parts manifest
`verification/runs/T-family/T23_runs/display_surface/t23_solved_geometry_parts.json`
→ `geometry_m`:**

| Quantity | Value |
|---|---|
| Axial extent | 0.750 m |
| Duct inner radius | 0.125 m |
| Motor body outer radius | 0.0375 m |
| Housing inner radius | 0.0335 m |
| Housing wall thickness | 0.004 m |
| Heated section length | 0.125 m |

**Features found — name what the geometry ACTUALLY has.** Her example list is
"slot, channels, housing, tip"; for the motor the true features, from
`part_order`, are:

> **a heated housing** (the 0.125 m heated section), **a duct** around it, and
> **a centrebody** running the full length upstream and downstream of the
> housing.

**⛔ And the features it does NOT have must not be listed:** no nose, no tail,
no struts. The manifest's `declared_omissions` records that the retired surface
carried three struts and nose/tail cones that were never solved. Screen 3 is
exactly where a plausible-sounding feature list would reintroduce them.

**Confidence statement**, and it is genuinely strong here:

> Confidence: high. The body is axisymmetric and fully dimensioned, and the mesh
> was confirmed identical across all sixteen cases before any temperature was
> read.

*(Backing: `geometry_guard.result` — "all 16 cases byte-identical in fluid,
housing and core — 48 of 48 region-case pairs".)*

## 9.3 SCREEN 4 — EXPERT DISCUSSION (mandatory; we carry most of it under other names)

Her three named roles, in her order. **Aligning our naming to hers**: our
existing content lives in `mesh_plan`, `gates` and `Results.limitations` and is
re-labelled, not rewritten.

**Lead Researcher — physics identified; closure chosen and why (class, known limits):**

> The physics is conjugate heat transfer: a heated core, its housing wall and
> the cooling air are solved together rather than separately, so the metal and
> the air set each other's temperature. The closure is k-omega SST, resolved to
> the wall rather than bridged with a wall function. It is a two-equation
> eddy-viscosity model — it carries that class's known limit, which is that
> turbulent transport is modelled rather than resolved, and the heat the air
> carries away carries that model's error.

*(Closure name is READ, `actA_screen_data.json` → `solver.turbulence_model`,
never typed — the act already does this.)*

**Lead Engineer — mesh type and target resolution; solver named:**

> A structured wedge mesh of 39,680 cells over three regions — 35,200 in the
> air, 1,120 in the housing, 3,360 in the core. Wall layers are resolved, not
> modelled: the near-wall spacing holds the wall unit below one against the
> heated housing. The solver is OpenFOAM chtMultiRegionSimpleFoam.

*(Cells from `T23_T24_MESH_FACTS.json`; wall units from `T23_GRADE.json.yplus`,
four surfaces, already tabulated by `mesh_plan()`; solver name cross-checked
between the log header and the case dictionary by `solver_name()`.)*

**Lead Numericist — schemes, tolerances, and the checks that will run:**

> Steady, so no time step. The checks that will run are set before the solve:
> every reader is driven with a known planted signal and must detect it, the air
> mass through the duct must balance in against out, and every value on the
> results table is re-read from the stored fields against the record written
> before the runs started.

*(All three already exist: `gates()` planted table — 4 readers, planted
1.234e-03 K; `gates()` conservation table; and the 5 anchor checks agreeing to
3.7e-05 K.)*

**Assumptions table — USER-DEFINED vs LAB-DEFINED, every quantity with a value
and a unit.** New as a split table; the content exists in
`actA_screen_data.json` → `assumptions` and in `figures_actA/actA_assumptions.pdf`.

| Source | Quantity | Value | Unit |
|---|---|---|---|
| USER-DEFINED | Dissipated power, swept | 80, 155, 230, 305 | W |
| USER-DEFINED | Duct airspeed, swept | 10, 20, 30, 40 | m/s |
| USER-DEFINED | Temperature limit | 200 | °C |
| LAB-DEFINED | Core conductivity | 40 | W/m·K |
| LAB-DEFINED | Housing conductivity | 167 | W/m·K |
| LAB-DEFINED | Air conductivity | 0.026 | W/m·K |
| LAB-DEFINED | Design isotherm | 120 | °C |
| LAB-DEFINED | Closure | k-omega SST, wall-resolved | — |
| LAB-DEFINED | Symmetry | axisymmetric, 5-degree wedge | deg |
| LAB-DEFINED | Radiation | off in all three regions | — |

**The one user-assumption correction beat** is §9.1, and it belongs on this
screen only as the *estimate* half; the correction half waits for the solve.

## 9.4 ⛔ NEVER-LIST AUDIT — PER-OCCURRENCE, WITH RESOLUTION

Her list: *prior runs, replay, agreements, paths, ids, tiers, "not recorded",
"no solver", "already finished"*. Physics facts stay and are phrased as the
platform's next automatic step.

### 9.4.1 The "not recorded" occurrences — the table asked for

**Correction to the brief I was given: it is not four occurrences.** The literal
string `"not recorded in this bundle"` occurs 4 times, but the banned phrase
`"not recorded"` occurs at **13 sites across two files**, and one of the two
files is Act A's own act module, which the brief did not mention.

`sdk/workflows/thermal_display.py` (cfd's file):

| Line | Quantity reported unrecorded | Fires? | Value exists on disk? | Resolution | Exact replacement string |
|---|---|---|---|---|---|
| 274 | `NOT_RECORDED` constant | — | — | (a) rename | `NOT_RECORDED = "the platform records this automatically"` — or delete once 362/396/527/659-664 are fixed |
| 362 | joined descriptor parts | conditional | n/a | (b) | `"the platform names this on the next pass"` |
| 396 | magnitude whose unit is missing | conditional | n/a | (b) | `f"{mag}, unit added on the next pass"` |
| **454** | **source case** | no — `common` is non-empty | **yes** | **(a), but NOT verbatim** | ⛔ the recorded value is a **filesystem path** and "paths" is itself on the never-list. Use words: `"Sixteen operating points, four powers by four airspeeds"` |
| **455** | **reader** | **YES, unconditional** | **yes** | **(a)** | `"Peak core temperature is the maximum of T over the core; peak housing temperature is the maximum of T over the housing."` (from `actA_screen_data.json` → `reader`, with the script names and paths stripped) |
| **458** | **mesh cell count** | **YES, unconditional** | **yes — 39,680** | **(a)** | `39680` (an integer, rendered by the existing `:,` formatter at 661 as `39,680`) |
| **459** | **geometry guard** | **YES, unconditional** | **yes** | **(a)** | `"All sixteen cases were confirmed identical in the air, the housing and the core before any temperature was read."` |
| 527 | uncertainty envelope reason | conditional | yes | (a) | the Screen 8 line: `"The grid convergence study for this case is running."` |
| 659–664 | table fallbacks for the four above | conditional | yes | (a) | once 454–459 carry values, these fallbacks are unreachable; replace the literal anyway with `"the platform adds this automatically"` |

**Three of them — 455, 458, 459 — are UNCONDITIONAL and reach the screen on
every render.** 454 is conditional and does not currently fire. All four have
their values on disk, so **resolution (a) applies to all four**, which is the
honest fix and the one that makes the screen better rather than quieter.

`sdk/workflows/motor_thermal_act.py` (cfd's file — **not in the brief, found in
this audit**):

| Line | Quantity | Fires? | Value exists? | Resolution | Replacement |
|---|---|---|---|---|---|
| 138 | `_cell()` fallback for any missing table value | conditional | varies | (b) | `"the platform adds this automatically"` |
| 550–551 | wall-unit row on the **mesh resolution table** (Screen 5) — three cells per row | **not today** | **yes** | (a) | dead on current data: `T23_GRADE.json.yplus` carries all four keys (`duct_wall`, `centrebody_up`, `centrebody_down`, `fluid_to_housing`), so the branch never fires. **Still must be changed** — it is one missing key away from putting a banned string on the resolution table Screen 5 requires. |

### 9.4.2 The two other strings I was asked to re-check — both are worse than flagged

Read in context at `thermal_display.py:790–810`, this is the **`thermal-display`
route — the same route as `m-942be0f630b7`, which §2.2 shows serving the retired
body.** Its engineer narration is a cluster of violations, not two strings:

| Rendered text | Never-list term |
|---|---|
| "a body this lab has **already run**" | prior runs / already finished |
| "**No solver starts** on this request" | **"no solver"** — explicit |
| "no new number is produced: **the screens come from that run's own fields**" | replay |
| "**Reference body received**… The screens below come **from the run that landed for this body, not from the uploaded file**, and the uploaded file is **neither meshed nor solved** by this act" | replay + prior runs |

**This is not a wording problem, it is a route problem.** Her preamble is
*"Nothing narrates the current state of the lab"*, and this narration exists
solely to narrate it. It also directly contradicts **Screen 1** ("The user's
uploaded STL renders immediately") by announcing that the uploaded file is not
used. **Recommendation: Act A must not be shot through the `thermal-display`
route at all** — it is shot through the registered `motor-thermal` demo-mode
act, which narrates none of this. Rewriting these four sentences would leave a
route whose entire purpose is the thing the protocol forbids.

### 9.4.3 The rest of the never-list on the Act A surface

| Site | Term | Finding |
|---|---|---|
| `motor_thermal_act.py:391` | **ids** | `run_id=PRIMARY.name` emits `T23_P305_U20`. Must not reach a screen. |
| `motor_thermal_act.py:400` | **ids + replay** | `presentation_of="presentation of run T23_P305_U20"` — an id *and* replay framing. Must not reach a screen. |
| `motor_thermal_act.py:734` | **agreements** | *"no **agreement** with measurement is claimed"*. **Resolved cleanly:** her rule explicitly preserves this as a physics fact and gives the wording — *"no measured data for this configuration"*. **Replacement:** `"There is no measured data for this configuration, so the temperatures are shown as solved."` |
| `figures_actA/actA_monitor_replay.pdf` | replay | filename only; the rendered title is *"Housing temperature monitors, sixteen runs"* and is clean. **Never display the filename** — "paths" is banned anyway. |
| §5.2 line 4, my own draft | **agreements** | same fix as line 734; re-drafted below. |

**Re-drafted §5.2 line 4:** *"There is no measured data for this configuration,
so the temperatures are shown as solved."*

## 9.5 TENSE PASS — past tense for results is RESTORED

Re-read every line drafted in §5 and §9 under the restored rule
(present/progressive while running, **past tense for results**):

| Line | Verdict |
|---|---|
| §9.1 Screen A ("The hand estimate **puts** the housing at 197.3 °C") | present — correct, it is what the team is doing before the solve |
| §9.1 Screen B ("The coupled solve **found**… the estimate **ran** 3.4 times hot… the design **was** never marginal") | past — correct, these are results |
| §5.2 line 1 ("**Reproduced** from the fields on disk… **agreeing** to better than 3.7e-05 K") | past — correct |
| §5.2 line 2 ("four readers each **detected** a planted perturbation") | past — correct |
| §5.2 line 3 ("Every temperature here **came** from a single mesh… the study **is running**") | past for the result, present for the ongoing study — correct |
| §5.6 Conclusion ("the motor **stays** clear… the hottest point **sits** 92 K below") | ⚠ **present tense on results — FIX** |
| §5.3 certificate block ("**was** established / **was NOT** established") | past — correct |

**Re-drafted §5.6 Conclusion, past tense on every result:**

> Across the whole range asked for, the motor stayed clear of its 200 °C limit.
> The worst case was the highest power at the lowest airspeed, and even there
> the hottest point in the core sat 92 K below the limit. The hand estimate that
> prompted this study ran 3.4 times hot, measured as temperature rise above the
> incoming air. Every number here came from a single mesh; the grid convergence
> study for this case is running, and the band lands in your inbox with the
> certificate.

*(The final clause is subject to §5.2a — it is honest only once T23G2 is
launched.)*

## 9.6 THE PATCH, PREPARED IN OUR TERRITORY

`thermal_display.py` and `motor_thermal_act.py` are **cfd's files and are not
edited by us.** The changes of §9.4.1 are specified here as **cfd dependency
D-A9**, to be applied by cfd, with every replacement string given verbatim in
the tables above and every value's source named.

**D-A9 acceptance check**, for whoever applies it:

    grep -c 'not recorded' sdk/workflows/thermal_display.py sdk/workflows/motor_thermal_act.py   # must be 0 in both

**D-A10:** Act A is shot through the registered `motor-thermal` act only; the
`thermal-display` route is not used for capture (§9.4.2).

## 9.7 A CLAIM THAT WAS TRUE WHEN MADE AND STALE WHEN RELAYED — BOTH RECORDED

**This entry was itself corrected, and the correction is the more useful record.**

I was told that `sdk/workflows/motor_thermal_act.py` and
`sdk/geometry/t23_solved_geometry.stl` *"DO exist on disk now (mtime 15:37) but
are NOT tracked at HEAD"*, that the Act A patch was *"left uncommitted"* and is
*"NOT recoverable"*, and that committing them should be named a cfd dependency.

**Measured when I received it: all three of `motor_thermal_act.py`,
`t23_solved_geometry.stl` and `thermal_display.py` are TRACKED at HEAD and CLEAN
against it** — `git cat-file -e HEAD:<path>` succeeds and
`git diff --quiet HEAD -- <path>` reports no difference for each.

**But the claim was TRUE when it was made, and the provenance matters more than
the contradiction.** The timeline, verified:

| Time | Event |
|---|---|
| ~15:37Z | The Act A patch is applied to the working tree and left untracked |
| ~18:12Z | The claim is measured: `git rev-parse HEAD:sdk/workflows/motor_thermal_act.py` returns *"exists on disk, but not in 'HEAD'"*. **Untracked. The claim is correct.** |
| **18:24:30Z** | **cfd commits `873e41505e122f4ef62c2b0f856f668fab8256f5`** — *"LANDS HEAT-TRANSFER'S APPLIED ACT A PATCH BEFORE IT IS LOST — 969 LINES SAT UNTRACKED FOR THREE HOURS, ONE `git clean` FROM GONE"*. `git show --name-status` confirms status **`A`** for both files: 764 lines of `motor_thermal_act.py` and 90,084 bytes of the STL, 969 insertions across 3 files. |
| ~20:40Z | I measure. Both tracked and clean. **My reading is also correct.** |

So the warning was real, the risk was real (one `git clean` from losing 969
lines), it was acted on, and **the INSTRUCTION derived from it went stale inside
twelve minutes.** Neither reading was wrong; they were taken on either side of a
commit.

**The operative conclusion is unchanged and is the one to act on: no cfd
dependency is recorded, because there is nothing to commit.** Checklist item 1 is
satisfied **at HEAD**, not merely in a working tree. A lane acting on the
withdrawn instruction would stage files already at HEAD.

**The lesson this belongs to, and it is not a wording quibble.** On a tree this
fast, any claim about another team's files decays in minutes. **Re-derive at the
point of USE, not the point of discovery.** This is the same class as the lab's
standing `git status` staleness note and as the two grep sweeps in §2.2 that
returned different subsets minutes apart. A successor reading this file should
see both readings and the commit between them, not a verdict that one party was
careless.

### 9.7a A SECOND AND DIFFERENT FAILURE MODE, RECORDED THE SAME DAY

A reviewer went to verify the §5.2a Screen 8 clearance and their check reported
**"L1: NO DIR, L2: NO DIR, L3: NO DIR"** — a clean, confident negative. The
directories are `T23G2_L1`, `T23G2_L2`, `T23G2_L3` and they were all present.
**The check had guessed the naming convention and then confirmed its own guess
rather than the disk.** Reported, it would have called a true clearance false.

**This is NOT the stale-reading failure of §9.7.** Nothing decayed; the query was
never capable of returning the thing it was looking for. It is instead
**`CLAUDE.md` rule 3 — the planted-zero rule — applied to a shell check rather
than to a field reader.** A zero from a reader not shown able to see a non-zero
is not evidence, and *a "not found" from a query not shown able to find
something is not evidence either.*

**The generalisation this file adopts:**

> A negative result is two claims, not one: a claim about the world, and a claim
> that the query could have seen the world. Establish the second before
> reporting the first — list the parent directory, or run the check against a
> path known to exist.

Applied here: every "does not exist" in this specification — T23G2's absence in
§5.2a before the launch, the missing renders in §8, the absent `.foam` file in
§10.4 — was taken by listing the **parent** directory and reading what was
actually there, not by testing a constructed path. That is why §5.2a could say
"no run tree" and then, twenty minutes later, name three levels by their real
directory names.

## 9.8 THE NINE-BOX SHOOTING CHECKLIST, FOR ACT A

| # | Item | State |
|---|---|---|
| 1 | STL is the solved geometry and renders on load | **[x]** `t23_solved_geometry.stl`, sha256 `d2864232…`, tracked and clean at HEAD, guarded by a shape check and a byte-identity check. §2 records the separate retired-body hazard, which is a different question. |
| 2 | Header stages advance and match what is on screen | **[ ]** blocked on D-A7/D-A8. Three of her seven strings — `Reading the geometry`, `Checking`, `Report` — do not exist in the machinery, and her order puts geometry before planning while the contract puts it after. |
| 3 | Expert discussion present, assumptions table present | **[ ]** content drafted in §9.2–§9.3; the acknowledgement geometry table and the USER/LAB assumptions split are **new** and not yet built. |
| 4 | Mesh shown as real cells; resolution table present | **[x]** `actA_mesh_boundary_layer.pdf` (three zooms, 2,806 cells in the 30 mm window) and the four-surface wall-unit table from `mesh_plan()`. ⚠ carries the latent `"not recorded"` branch of §9.4.1. |
| 5 | Sweep/multipoint monitors as small multiples on one screen | **[ ]** §4 specifies the 4×4 sixteen-tile layout concretely; the component is cfd's and not built. |
| 6 | Results table, compute line, conclusion | **[x]** sixteen-row table, cost line 578.8 against 483.6 forecast, conclusion re-drafted in past tense at §9.5. |
| 7 | Report tab populated: plots to the figure standard, summary, next steps | **[~]** nine of ten figures compliant; **`actA_map_table.pdf` carries a table inside the figure** and must be split (§6). "Next steps" is new and is the T23G2 study. |
| 8 | Convergence study shown done, or the "lands in your inbox" line | **[ ] ⛔ BLOCKING** — the line is drafted but **T23G2 is not launched**, so it is currently false. §5.2a. |
| 9 | Zero forbidden language on any screen | **[ ]** 13 `"not recorded"` sites across two files (§9.4.1); the `thermal-display` narration cluster (§9.4.2); ids at `motor_thermal_act.py:391,400`; "agreement" at `:734`. |

**Two boxes are blocking and neither is a drafting problem:** box 8 needs T23G2
launched, and box 9 needs D-A9 applied.

---

# 10. PARAVIEW RENDERING (SANAA-DIRECT `2026-09-01T2110Z`, canvas retired)

> *"Going forward all acts use paraview. Never that trashy canvas you were using
> before"* — Sanaa, verbatim.

Every act's **geometry, mesh and field** visuals are ParaView-rendered from the
real case files. The in-browser canvas is retired as a visual source. **cfd owns
the viewport display pipe; heat-transfer owns Act A's render scripts.**

**Scripts are NOT built here.** This section states what must be rendered, from
which real artifact, and what the scripts will need, so the work can be placed.

## 10.1 Toolchain — verified on this box, not assumed

| Tool | Path | Version |
|---|---|---|
| `pvbatch` | `/usr/bin/pvbatch` | **ParaView 5.11.2** |
| `pvpython` | `/usr/bin/pvpython` | 5.11.2 |
| `xvfb-run` | `/usr/bin/xvfb-run` | present |

Headless recipe: `xvfb-run -a pvbatch <script>.py`. Pin 5.11.2 in every script
header — a render that changes with the reader version is not reproducible.

## 10.2 The source case is ParaView-ready — measured

`verification/runs/T-family/T23_runs/T23_P305_U20` carries:

- **Three region meshes**, each complete:
  `constant/{fluid,housing,core}/polyMesh/` with `points`, `faces`, `owner`,
  `neighbour`, `boundary`, `cellZones`, `faceZones`.
- **A converged time directory `10000/`** with the fields:

| Region | Fields at `10000/` |
|---|---|
| `fluid` | `T U alphat k nut omega p p_rgh phi rho` |
| `housing` | `T p` |
| `core` | `T p` |

- The age guard holds: `10000/fluid/T` (2026-08-31 18:04:21Z) is newer than
  `0/fluid/T` (17:34:07Z).

**Everything Screens 1, 5 and 6 need is on disk in solved form.** No field has
to be reconstructed and nothing is rendered from an extract.

## 10.3 What must be rendered, per screen

| Screen | Render | Source, absolute |
|---|---|---|
| **1 — Geometry** | The solved body, rotating or static, on load | `/home/ubuntu/Certonomous/sdk/geometry/t23_solved_geometry.stl` (sha256 `d2864232…`), part colouring from `…/display_surface/t23_solved_geometry_parts.json` `part_order` |
| **4/5 — Mesh, REAL CELLS** | The wedge mesh drawn cell by cell, all three regions, with the wall-layer zoom against the heated housing | `…/T23_P305_U20/constant/{fluid,housing,core}/polyMesh/` — **rendered as actual cells (Surface With Edges), not as a tessellated stand-in** |
| **6 — Fields, temperature** | `T` across all three regions together — the conjugate story: core hottest, gradient through the housing wall, plume in the air | `…/T23_P305_U20/10000/{core,housing,fluid}/T` |
| **6 — Fields, velocity** | `U` in the fluid, showing acceleration over the housing | `…/T23_P305_U20/10000/fluid/U` |
| **6 — Airspeed comparison** | The same body at 10, 20, 30, 40 m/s | `T23_runs/T23_P305_U{10,20,30,40}/10000/*/T` — one render per case, identical camera and identical colour range |

## 10.4 What the render scripts need — the list to hand to whoever builds them

1. **A `.foam` entry point, which DOES NOT EXIST.** ParaView's OpenFOAM reader
   opens a case through a `<name>.foam` file in the case directory. Measured:
   there is **no `.foam` file in `T23_P305_U20`** (checked by listing the case
   directory, not by testing a guessed path — §9.7a).
   ⚠ **Do not `touch` one into the completed run tree.** These are graded cases
   under the completion rule; writing into them invites exactly the "is this
   artifact still the one that ran" question the age guard exists to answer.
   **Required approach: the render script materialises a scratch case — symlink
   `constant/`, `system/` and the needed time directory into a scratch dir and
   create the `.foam` there.** The run tree stays read-only.
2. **Multi-region reading.** The reader must load all three regions and render
   them together for the conjugate temperature view; a single-region render
   tells the wrong story (the whole point is that metal and air set each other's
   temperature).
3. **⛔ THE AXISYMMETRY DECLARATION, which is the honesty trap in this section.**
   The solve is **one cell over a 5-degree wedge**. A ParaView render that
   rotationally extrudes it into a full 360-degree body is showing geometry that
   was never solved. The parts manifest already treats this correctly for the
   STL, declaring `revolve_segments_DISPLAY_CHOICE: 180` and requiring that
   *"the axisymmetry must be stated wherever this surface is shown"*.
   **The same rule binds every ParaView render**: either show the wedge as
   solved, or extrude it and **state on the screen that the body is
   axisymmetric and the revolve is a display choice.** Silently extruding is the
   same class of defect as the retired body in §2.
4. **Colour ranges are READ, never chosen per render.** From
   `figures_actA/actA_screen_data.json` → `map_colour_range_degC` and
   `map_colour_range_housing_degC`. The four airspeed renders must share one
   range or the comparison is meaningless.
5. **Determinism**: fixed camera position, fixed image size, fixed colour map,
   pinned version. Two runs of the script must produce identical images.
6. **Figure standard applies to rendered stills too** (§6): title ≤10 words, one
   caption line, **no table inside the image**, and the colour bar carries
   numeric ticks and the unit only — min and max appear there and nowhere else.
7. **Progressive reveal by frame sequencing**, per the chief's reading of the
   directive: stills or frame sequences, since the viewport no longer draws.

## 10.5 Scope — what ParaView replaces and what it does NOT

Her directive names **geometry, mesh and field** visuals. It does not name line
plots. **Proposed split, flagged for the supervisor's confirmation:**

| Figure | Disposition |
|---|---|
| `actA_temperature_field.png` | **→ ParaView** (field) |
| `actA_velocity_field.png` | **→ ParaView** (field) |
| `actA_mesh_boundary_layer.png` | **→ ParaView** (mesh, real cells — and Screen 5 requires real cells, which strengthens this) |
| `actA_airspeed_thumbnails.png` | **→ ParaView** (four field renders) |
| `actA_envelope.pdf` | stays matplotlib — an x-y plot with the 200 °C line |
| `actA_radial_profile.pdf` | stays matplotlib — an x-y profile |
| `actA_monitor_replay.pdf` | stays matplotlib — settling traces |
| `actA_map_table.pdf` | stays matplotlib — heatmap (and §6's table still must come out) |
| `actA_assumptions.pdf`, `actA_assumption_beat.pdf` | stay matplotlib — text and bar panels |

Rendering an x-y convergence trace in ParaView would be a worse figure, not a
more compliant one. **If the supervisor reads her "all acts use paraview" as
covering plots too, this table changes and the four ParaView items become
eleven** — raised rather than assumed.

## 10.6 New dependency

**D-A11 (ours, heat-transfer):** write Act A's ParaView render scripts to the
above, filed under
`/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/render_actA_paraview/`.
**Not built in this pass** — the requirements above are the handoff.

**D-A12 (cfd):** the viewport display pipe consumes ParaView stills/sequences
rather than drawing on the retired canvas.
