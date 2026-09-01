# Act A ParaView renders — D-A11

ParaView-rendered geometry, mesh and field visuals for the motor-in-duct act,
from the real graded case files. Under SANAA-DIRECT 2026-09-01 ~21:10Z
(`etc/sessions/2026-09-01T2110Z_sanaa_paraview_everywhere.md`): every act's
geometry, mesh and field visuals are ParaView-rendered and the in-browser canvas
is retired as a visual source.

Requirements and per-screen content: `../ACT_A_GUI_CONTENT_SPEC.md` §10.

## Run

    xvfb-run -a pvbatch render_actA_fields.py          # Screen 6
    xvfb-run -a pvbatch selftest_render_actA.py        # the guards, both arms

ParaView **5.11.2**, pinned and asserted at start-up.

## Files

| File | What |
|---|---|
| `_actA_render_common.py` | scratch-case materialisation, the guards, camera framing, colour ranges |
| `render_actA_fields.py` | Screen 6 — temperature across all three regions, and air speed |
| `selftest_render_actA.py` | drives every guard to refuse **and** proves the renderer still draws |

## The three things this machinery refuses to do

**1. It never writes into a graded run tree.** Not a `.foam` file, not a symlink,
not a temp file. These cases are under the strict completion rule and its age
guard. `materialise_region()` builds a scratch case of symlinks and puts the
`.foam` there; `assert_run_tree_untouched()` fingerprints the case directory
before and after and refuses if it moved.

**2. It refuses the wrong mesh, and this is a real bug, caught here.** A `.foam`
placed beside the case reads the **top-level `constant/polyMesh` — the pre-split
39,680-cell mesh of all three regions combined** — and offers the fluid field
names beside it. It renders. It looks entirely plausible. The per-region scratch
layout gives each region its own mesh, and every reader asserts its cell count
against `T23_T24_MESH_FACTS.json`: 35,200 fluid, 1,120 housing, 3,360 core.

**3. It refuses an empty, tiny or stale image.** A render that silently produces
a blank frame is the visual form of a false zero.

## Cross-checks against the graded record

The renders were checked against numbers this family had already graded, from
independent artifacts:

| Read by ParaView | Recorded elsewhere | Agrees |
|---|---|---|
| housing max **342.160 K** | `T23_GRADE.json` Q1 = 342.1598289320 K | to 6 s.f. |
| core max **346.266 K** = 73.1 °C | map table peak core, 305 W / 20 m/s = 73.1 °C | yes |
| measured field range **14.8 to 73.1 °C** | inlet air 14.9 °C, peak core 73.1 °C | yes |

## Two facts about this geometry that the scripts encode

**The axis convention is measured, not assumed.** From the mesh bounds:
`x` is the five-degree **wedge thickness** (±0.0055 m), `y` is the **radius**
(0.006–0.125 m), `z` is the **axis** (−0.25–0.5 m). The solved plane is the
**y–z** plane, viewed along `x`. An earlier version of `frame_axial_plane()`
assumed radius on `x` and looked along `−y` — straight through the radial
direction — and rendered the wedge edge-on as a hairline. It was not obviously
broken at a glance, which is the dangerous kind.

**Colour ranges for a FIELD are measured, not taken from the map record.**
`map_colour_range_degC` spans 24.7–107.7 °C, which is the range of the sixteen
**peak** values. Painting a whole field on it clamps the ~15 °C cooling air to
the bottom colour and renders a black body. `field_range_degC()` measures the
range across every region and every case in the set instead; passing the four
airspeed cases together is what makes them honestly comparable.

## Axisymmetry — declared, never silent

The solve is one cell over a five-degree wedge. There are two declarations and
**the one used must describe the picture actually drawn**:

- `AXISYMMETRY_PLANE_LINE` — for a view of the solved plane. No extrusion.
- `AXISYMMETRY_REVOLVE_LINE` — for a body revolved for legibility.

Extrusion is permitted; silent extrusion is not. Stamping the revolve sentence
on a plane view would be false in the other direction — claiming a display
choice that was not made.

## The self-test carries both arms, and why

`selftest_render_actA.py` drives every guard with an input it must reject **and**
renders a real picture from the real case, asserting it is non-blank and
non-flat. A refusal-only sweep would pass perfectly on a module that could not
draw anything at all — a negative is two claims, about the world and about the
query (spec §9.7a).

It has already earned its place twice:

- `save_screenshot(None, …)` raised ParaView's own `ValueError` before reaching
  the missing-file check, so that guard **looked tested and was not**. The check
  is now `verify_written_image()`, driven directly.
- A mutation run disabling the real cell-count guard left the wrong-mesh check
  **still passing** — because that check called `refuse` itself rather than
  going through `open_region`. A control derived from the thing it controls is
  not a control. It is now labelled a demonstration, and the real guard is
  driven separately by making the recorded expectation disagree with the disk.

Mutation-verified: clean `rc=0`; guard disabled → `rc=2` with an `ASLEEP` line;
restored → `rc=0`.

## Known wrinkle

ParaView 5.11.2 under xvfb tears its GLX context down after the interpreter
finishes and the process dies with `GLXBadContext` or `SIGSEGV` — **after** every
check has run and the verdict is printed. The self-test therefore ends in
`os._exit(rc)` with `rc` the verdict it computed, so the teardown cannot
overwrite a real result. Triaged, not waved through: outputs are verified
complete (PNG `IEND` present, 1600×900, ~180 distinct colours) before exit.

## Not built yet

- `render_actA_geometry.py` — Screen 1, the solved STL on load.
- `render_actA_mesh.py` — Screens 4/5, the real cells with the wall-layer zoom.
- The four-airspeed comparison set, which must call `field_range_degC()` with
  all four cases at once so they share one measured scale.

Rendered output lands in `out/` and is not committed; regenerate with the
commands above.
