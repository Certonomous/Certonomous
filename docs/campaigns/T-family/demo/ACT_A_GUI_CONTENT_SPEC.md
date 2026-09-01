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

| # | Stage (`STAGES`) | Current `BANNERS` value | **Header string Act A must show** |
|---|---|---|---|
| 1 | `prompt` | `forming team` | `Forming the team` |
| 2 | `restatement` | `planning` | `Planning` |
| 3 | `assumption` | `planning` | `Planning` |
| 4 | `geometry` | `fleet at work` | `Fleet at work` |
| 5 | `meshing` | `meshing` | `Meshing` |
| 6 | `feasibility` | `feasibility` | `Feasibility` |
| 7 | `solving` | `solving` | `Solving, point N of 16` |
| 8 | `gates` | `solving` | `Checking` |
| 9 | `results` | `results` | `Report` |

**cfd dependency D-A7:** rows 8 and 9 do not exist in the machinery. `BANNERS`
maps `gates` → `"solving"` and `results` → `"results"`; Sanaa asked for
`Checking` and `Report`. That is a change to `sdk/workflows/demo_mode.py`,
which is cfd's file. We specify the strings; we do not make the change.

**cfd dependency D-A8:** `Solving, point N of 16` needs a live point index.
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
> 3. **NEW — the honest negative.** A three-grid refinement study was run for
>    this body and did not settle: the temperatures moved with the grid too
>    slowly for the study to support an error bar, so no numerical uncertainty
>    is quoted on any row here, and none is drawn.
> 4. No rig or wind tunnel data exists for this configuration, so the
>    temperatures are shown as solved and no agreement with measurement is
>    claimed. *(already exists in the act, unchanged.)*

**Line 3 is the one that needs the supervisor's eye.** It states a run happened
and returned nothing usable — an honest negative, publishable — without using
`NOT A RESULT` on screen, without quoting the observed order as if it were a
result, and without implying a band exists. It must NOT be softened to "a grid
study is in progress": T23G is closed and graded; T23G2 is the one not yet run.

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
> No certificate number is assigned to this run.

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
