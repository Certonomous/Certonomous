# Demo surfaces

One-stop folder for the live demo. Browse here when clicking "Load a surface
(STL / OBJ)" in the GUI.

| File | What it is for |
|---|---|
| `motorBike.obj` | Act 2 motorcycle CFD |
| `b52.stl` | Act 2 B-52 CFD |
| `naca4412_wing.stl` | Act 2b validated wing, and the race act |
| `naca0012_wing.stl` | spare validated body |
| `motor_in_duct.stl` | DEMO STANDARD v2 Act A — motor in duct |
| `airfoil_blown_slot.stl` | DEMO STANDARD v2 Act B — blown slot / jet flap |
| `battery_module_8cell.stl` | DEMO STANDARD v2 Act C — 8-cell battery module |

These are copies of the staged surfaces in `sdk/geometry`. The originals there
are load-bearing for the backend's named-body resolver, so do not move or edit
them.

**The three Act surfaces are DISPLAY / UPLOAD surfaces for the demo, not
meshing inputs** — nothing is meshed or solved from them, and no gate cites
them. They are written by `generate_demo_stls.py` (deterministic, numpy only,
no downloads), which prints for each file its triangle count, its bounding box,
and a closed-shell edge-parity count that must read 0. Registered dimensions
are carried where they exist and every departure is marked as a display choice
in that script's header: Act A takes `D` = 0.25 m, `L` = 0.8 D = 0.200 m and
`D_hub` = 0.3 D = 0.075 m from the F28 pre-registration; Act B takes `c` = 1.0 m
and the blunt base `h` = 5.0 mm (`h/c` = 0.005) from the JF1 pre-registration;
Act C takes the eight 100 mm x 30 mm cells and their 3 mm channels from the
Case-4 directive, whose registered case is 2D at unit depth — **the 120 mm cell
height here is a display extrusion and is not registered.**
