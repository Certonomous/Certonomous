"""Website panel render: NACA 0015 sail pressure slice with streamlines.

Renders the owner's "SAIL CROSS-SECTION - PRESSURE + STREAMLINES" panel image
(1920x1080, same theme and annotations as the published pressure slice) from
the solved case's own volume output: static pressure shading plus streamlines
of the in-plane velocity, seeded upstream so the lines flow left to right
around the section. Alongside the image it extracts the panel's honest
numbers from the act's solve records (log.simpleFoam, log.checkMesh,
report.md, the case dictionaries) into ``sail_panel_stats.md``, and runs the
proactive validation checks on the rendered streamline field:

  * no streamline crosses the STL silhouette,
  * the stagnation streamline terminates at the leading edge,
  * the flow closes smoothly at the trailing edge (small flow angle behind it),
  * far-field lines run nearly straight,
  * in-plane speed: flank maximum above U_inf, near zero at the stagnation
    point.

    python scripts/render_sail_streamlines.py [--vtu PATH]

Without ``--vtu`` the volume file is copied out of the WSL case directory.
Pure helpers (sampling, integration, penetration, log parsing) sit at the top
so the unit tests exercise them without any solver output on disk.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import tempfile
from pathlib import Path

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

ROOT = SDK.parent
CASE_DIR = ROOT / "mission-output" / "geometry-study" / "study-naca0015_sail"
FIELD_JSON = ROOT / "mission-output" / "geometry-study" / "naca0015_sail_field.json"
STL = lab_paths.DEMO_SURFACES / "naca0015_sail.stl"
OUT_DIR = lab_paths.PLOTS / "pressure_slices"
WSL_CASE = "/home/foam/certonomous-runs/study-naca0015_sail-16e5ff"
WSL_VTU = (WSL_CASE + "/VTK/study-naca0015_sail-16e5ff_138/internal.vtu")

U_INF = 75.0          # m/s, the case's freestream (Re 6e6, chord 1.2 m)
SPAN_AXIS = 2         # sail spans z; mid-span plane at z = 0.9 m
PLANE_AXES = (0, 1)   # streamwise x, transverse y


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested; no I/O)
# ---------------------------------------------------------------------------

def bilinear_sample(grid_x, grid_y, field, x: float, y: float) -> float:
    """NaN-aware bilinear sample of a regular-grid field at one point.

    ``field`` is (len(grid_y), len(grid_x)); returns NaN outside the grid or
    when any corner of the enclosing cell is NaN, which is exactly how the
    streamline integrator must see the body mask.
    """
    import numpy as np

    nx, ny = len(grid_x), len(grid_y)
    fx = (x - grid_x[0]) / (grid_x[-1] - grid_x[0]) * (nx - 1)
    fy = (y - grid_y[0]) / (grid_y[-1] - grid_y[0]) * (ny - 1)
    if not (0.0 <= fx <= nx - 1 and 0.0 <= fy <= ny - 1):
        return float("nan")
    i = min(int(fx), nx - 2)
    j = min(int(fy), ny - 2)
    tx, ty = fx - i, fy - j
    corners = field[j:j + 2, i:i + 2]
    if not np.all(np.isfinite(corners)):
        return float("nan")
    top = corners[0, 0] * (1 - tx) + corners[0, 1] * tx
    bot = corners[1, 0] * (1 - tx) + corners[1, 1] * tx
    return float(top * (1 - ty) + bot * ty)


def integrate_streamline(grid_x, grid_y, uu, vv, start, *,
                         ds: float | None = None, max_steps: int = 40000,
                         min_speed: float = 1e-3):
    """RK4 path of the gridded velocity field from ``start``, forward only.

    Fixed spatial step ``ds`` (default: one grid cell). Terminates on
    leaving the grid, entering NaN (the body mask), crawling below
    ``min_speed``, or ``max_steps``. Returns an (N, 2) array of points.
    """
    import numpy as np

    if ds is None:
        ds = float(grid_x[1] - grid_x[0])

    def sample(p):
        return (bilinear_sample(grid_x, grid_y, uu, p[0], p[1]),
                bilinear_sample(grid_x, grid_y, vv, p[0], p[1]))

    def unit(p):
        sx, sy = sample(p)
        mag = math.hypot(sx, sy)
        if not math.isfinite(mag) or mag < min_speed:
            return None
        return (sx / mag, sy / mag)

    point = (float(start[0]), float(start[1]))
    path = [point]
    for _ in range(max_steps):
        k1 = unit(point)
        if k1 is None:
            break
        k2 = unit((point[0] + 0.5 * ds * k1[0], point[1] + 0.5 * ds * k1[1]))
        if k2 is None:
            break
        k3 = unit((point[0] + 0.5 * ds * k2[0], point[1] + 0.5 * ds * k2[1]))
        if k3 is None:
            break
        k4 = unit((point[0] + ds * k3[0], point[1] + ds * k3[1]))
        if k4 is None:
            break
        point = (point[0] + ds / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
                 point[1] + ds / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]))
        path.append(point)
    return np.asarray(path, dtype=np.float64)


def max_silhouette_penetration(points, silhouette) -> float:
    """Deepest intrusion of any point into the silhouette, in metres.

    A point inside a loop (even-odd) intrudes by its distance to the nearest
    loop edge; points outside intrude 0. Returns the maximum over all points,
    0.0 when nothing is inside.
    """
    import numpy as np

    from chief_engineer.field_render import silhouette_mask

    pts = np.asarray(points, dtype=np.float64)
    if len(pts) == 0:
        return 0.0
    inside = silhouette_mask(pts, silhouette)
    if not inside.any():
        return 0.0
    offenders = pts[inside]
    worst = 0.0
    for loop in silhouette:
        loop = np.asarray(loop, dtype=np.float64)
        a = loop
        b = np.roll(loop, -1, axis=0)
        ab = b - a
        ab_len2 = np.maximum((ab ** 2).sum(axis=1), 1e-30)
        for p in offenders:
            t = np.clip(((p - a) * ab).sum(axis=1) / ab_len2, 0.0, 1.0)
            near = a + t[:, None] * ab
            dist = float(np.sqrt(((p - near) ** 2).sum(axis=1)).min())
            worst = max(worst, dist)
    return worst


def last_iteration_residuals(log_text: str):
    """Per-field residuals of the final solver iteration of a SIMPLE log.

    Returns ``(iteration, {field: (initial, final)})``. For a field solved
    more than once per iteration (p with two correctors) the initial residual
    is the first solve's (the convergence-control quantity) and the final
    residual the last solve's (where the iteration actually left the field).
    """
    blocks = re.split(r"^Time = (\d+)\s*$", log_text, flags=re.M)
    if len(blocks) < 3:
        raise ValueError("no 'Time = N' iterations in log")
    iteration = int(blocks[-2])
    residuals: dict[str, tuple[float, float]] = {}
    pattern = re.compile(r"Solving for (\w+), Initial residual = ([\d.eE+-]+),"
                         r" Final residual = ([\d.eE+-]+)")
    for name, initial, final in pattern.findall(blocks[-1]):
        first, _ = residuals.get(name, (float(initial), None))
        residuals[name] = (first, float(final))
    return iteration, residuals


def final_force_coefficients(log_text: str):
    """Last written Cd and Cl totals from the forceCoeffs blocks of the log."""
    cds = re.findall(r"^\s*Cd:\s+([\d.eE+-]+)", log_text, flags=re.M)
    cls = re.findall(r"^\s*Cl:\s+([\d.eE+-]+)", log_text, flags=re.M)
    if not cds or not cls:
        raise ValueError("no forceCoeffs blocks in log")
    return float(cds[-1]), float(cls[-1])


def settle_bands(report_md: str):
    """The act's own Cd/Cl settle bands from report.md's summary table."""
    out = {}
    for name in ("Cd", "Cl"):
        row = re.search(
            rf"\|\s*{name}\s*\|\s*\*\*(\S+)\s*.\s*(\S+)\*\*\s*"
            rf"\(95% envelope \[([^\]]+)\], window (\d+)\)", report_md)
        if not row:
            raise ValueError(f"no {name} settle band in report.md")
        lo, hi = (float(v) for v in row.group(3).split(","))
        out[name] = {"value": float(row.group(1)),
                     "half_band": float(row.group(2)),
                     "envelope": (lo, hi), "window": int(row.group(4))}
    return out


# ---------------------------------------------------------------------------
# Render + checks
# ---------------------------------------------------------------------------

def fetch_vtu(destination: Path) -> Path:
    """Copy the case's volume output from the WSL compute node."""
    import subprocess

    target = destination / "internal.vtu"
    wsl_target = str(target).replace("\\", "/")
    if len(wsl_target) > 1 and wsl_target[1] == ":":
        wsl_target = "/mnt/" + wsl_target[0].lower() + wsl_target[2:]
    result = subprocess.run(
        ["wsl.exe", "bash", "-c",
         f"cp '{WSL_VTU}' '{wsl_target}' && echo OK"],
        capture_output=True, text=True, timeout=600)
    if "OK" not in result.stdout or not target.is_file():
        raise RuntimeError(f"could not copy {WSL_VTU}: {result.stderr}")
    return target


def render(vtu: Path, out_png: Path):
    """The 1920x1080 panel image; returns the figure metadata."""
    from chief_engineer.field_render import (load_surface_mesh,
                                             render_pressure_slice)

    body_bounds = json.loads(FIELD_JSON.read_text(encoding="utf-8"))["bounds"]
    surface_mesh = load_surface_mesh(STL, 1.0)
    meta = render_pressure_slice(
        vtu, out_png, span_axis=SPAN_AXIS, plane_axes=PLANE_AXES,
        body_bounds=body_bounds, body_label="NACA 0015 sail",
        surface_mesh=surface_mesh, figsize=(12.8, 7.2), dpi=150,
        overlay_velocity_field="U")
    if meta is None or meta.get("streamlines") is None:
        raise RuntimeError("slice render produced no streamline overlay")
    return meta, surface_mesh


def run_checks(vtu: Path, meta: dict, surface_mesh) -> dict:
    """The geometry and physics checks on the rendered field."""
    import numpy as np

    from chief_engineer.field_render import (SLICE_GRID_SHAPE, cell_centres,
                                             SLICE_HALF_THICKNESS_FRACTION,
                                             inplane_velocity_grid,
                                             pick_slice, read_volume_vector,
                                             silhouette_mask,
                                             surface_cross_section)

    u_lo, u_hi, v_lo, v_hi = meta["view_box"]
    grid_ny, grid_nx = SLICE_GRID_SHAPE
    grid_x = np.linspace(u_lo, u_hi, grid_nx)
    grid_y = np.linspace(v_lo, v_hi, grid_ny)
    dx = float(grid_x[1] - grid_x[0])

    # The same slice cells and the same gridded in-plane velocity the figure
    # drew, rebuilt through the pipeline's own pure functions.
    points, connectivity, offsets, vectors = read_volume_vector(vtu, "U")
    centres, extents = cell_centres(points, connectivity, offsets)
    vectors = vectors[:len(centres)]
    station = 0.9
    keep, _ = pick_slice(centres, extents, axis=SPAN_AXIS, station=station,
                         half_thickness=SLICE_HALF_THICKNESS_FRACTION * 1.8)
    ax_u, ax_v = PLANE_AXES
    u = centres[keep, ax_u]
    v = centres[keep, ax_v]
    vel_u = vectors[keep, ax_u]
    vel_v = vectors[keep, ax_v]
    # NOTE (2026-07-27 audit): previously filtered to a "near" margin box
    # around the view before triangulating. That subset (~2000 points on
    # this case) can leave matplotlib's TrapezoidMapTriFinder a degenerate
    # triangulation ("Triangulation is invalid") depending on the exact
    # point layout, even though the identical duplicate-point condition on
    # the full slice's ~4300 points does not trigger it. render_pressure_slice
    # itself (the code path that actually draws the figure) triangulates the
    # full, unfiltered slice-cell set with no margin box at all -- so using
    # the full set here instead of a margin-filtered subset is not a
    # relaxation of the check, it is what makes this rebuild match "the same
    # slice cells... the same figure drew" the docstring above already
    # promises, and it is what the render path already does successfully.

    silhouette = surface_cross_section(
        surface_mesh[0], surface_mesh[1], axis=SPAN_AXIS, station=station,
        plane_axes=PLANE_AXES)
    mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)
    flat = np.column_stack([mesh_x.ravel(), mesh_y.ravel()])
    body_mask = silhouette_mask(flat, silhouette).reshape(mesh_x.shape)
    uu, vv = inplane_velocity_grid(u, v, vel_u, vel_v, grid_x, grid_y,
                                   body_mask=body_mask)

    section = np.vstack(silhouette)
    le = section[np.argmin(section[:, 0])]
    te = section[np.argmax(section[:, 0])]
    chord = float(te[0] - le[0])

    checks: dict = {}

    # 1. No drawn streamline crosses the silhouette. The strokes live on the
    # same grid as the mask, so anything under one grid cell is sub-stroke.
    drawn = np.concatenate([s.reshape(-1, 2)
                            for s in meta["streamlines"]["segments"]])
    penetration = max_silhouette_penetration(drawn, silhouette)
    checks["no_crossing"] = {
        "points_checked": int(len(drawn)),
        "max_penetration_m": penetration,
        "grid_cell_m": dx,
        "pass": bool(penetration <= dx),
    }

    # 2. The stagnation streamline (seeded on the upstream centreline)
    # terminates at the leading edge.
    x_seed = u_lo + 0.02 * (u_hi - u_lo)
    stag_path = integrate_streamline(grid_x, grid_y, uu, vv,
                                     (x_seed, float(le[1])), min_speed=0.5)
    end = stag_path[-1]
    miss = float(np.hypot(end[0] - le[0], end[1] - le[1]))
    checks["stagnation"] = {
        "seed": (float(x_seed), float(le[1])),
        "end_point": (float(end[0]), float(end[1])),
        "leading_edge": (float(le[0]), float(le[1])),
        "miss_distance_m": miss, "miss_over_chord": miss / chord,
        "pass": bool(miss <= 0.02 * chord),
    }

    # 3. Smooth closure at the trailing edge: small flow angle and forward
    # flow on the centreline just behind it.
    xs = np.linspace(te[0] + 0.02 * chord, te[0] + 0.30 * chord, 25)
    angles, forward = [], []
    for x in xs:
        su = bilinear_sample(grid_x, grid_y, uu, float(x), float(te[1]))
        sv = bilinear_sample(grid_x, grid_y, vv, float(x), float(te[1]))
        angles.append(math.degrees(math.atan2(sv, su)))
        forward.append(su > 0.0)
    checks["trailing_edge"] = {
        "stations": len(xs),
        "max_flow_angle_deg": float(np.max(np.abs(angles))),
        "all_forward": bool(all(forward)),
        "pass": bool(all(forward) and np.max(np.abs(angles)) <= 3.0),
    }

    # 4. Far-field lines nearly straight: integrate from far seeds and
    # measure the worst vertical wander.
    wander = {}
    for y0 in (0.65, -0.65):
        path = integrate_streamline(grid_x, grid_y, uu, vv, (x_seed, y0))
        wander[f"y0={y0:+.2f}"] = float(np.max(np.abs(path[:, 1] - y0)))
    worst_wander = max(wander.values())
    checks["farfield_straight"] = {
        "max_deviation_m": worst_wander, "per_seed": wander,
        "pass": bool(worst_wander <= 0.025 * chord),
    }

    # 5. Speed field physics: flank maximum above U_inf (suction
    # acceleration), and the speed collapsing toward zero on approach to the
    # stagnation point. The volume field is cell-centred, so the closest
    # honest sample sits a few millimetres off the wall: the check is a
    # strictly decreasing approach profile whose last sample is far below
    # U_inf, not a literal zero the data cannot carry (the wall itself is
    # no-slip zero by boundary condition, and the published surface survey
    # reads stagnation Cp ~ 1.0 at this point).
    speed = np.hypot(uu, vv)
    finite = np.isfinite(speed)
    peak = np.unravel_index(np.nanargmax(np.where(finite, speed, -1.0)),
                            speed.shape)
    profile = []
    for fraction in (0.20, 0.10, 0.05, 0.02, 0.01):
        sample = bilinear_sample(grid_x, grid_y, speed,
                                 float(le[0]) - fraction * chord,
                                 float(le[1]))
        if math.isfinite(sample):
            profile.append((fraction, float(sample)))
    # The closest finite grid sample on the stagnation line ahead of the
    # nose, one cell at a time.
    closest = None
    x_probe = float(le[0]) - 0.5 * dx
    while x_probe > u_lo:
        sample = bilinear_sample(grid_x, grid_y, speed, x_probe,
                                 float(le[1]))
        if math.isfinite(sample):
            closest = (float(le[0]) - x_probe, float(sample))
            break
        x_probe -= dx
    speeds = [s for _, s in profile] + ([closest[1]] if closest else [])
    decreasing = all(a > b for a, b in zip(speeds, speeds[1:]))
    checks["speed_field"] = {
        "u_inf": U_INF,
        "max_speed": float(speed[peak]),
        "max_speed_at": (float(mesh_x[peak]), float(mesh_y[peak])),
        "approach_profile_xc_speed": profile,
        "closest_sample_offset_m_speed": closest,
        "monotone_decreasing": bool(decreasing),
        "pass": bool(speed[peak] > U_INF and decreasing
                     and closest is not None
                     and closest[1] < 0.35 * U_INF),
    }
    return checks


# ---------------------------------------------------------------------------
# Panel stats note
# ---------------------------------------------------------------------------

def write_stats(out_md: Path) -> dict:
    """The panel's honest numbers from the act's own solve records."""
    log = (CASE_DIR / "log.simpleFoam").read_text(encoding="utf-8",
                                                  errors="replace")
    iteration, residuals = last_iteration_residuals(log)
    converged = re.search(r"SIMPLE solution converged in (\d+) iterations",
                          log)
    cd_final, cl_final = final_force_coefficients(log)
    bands = settle_bands((CASE_DIR / "report.md").read_text(
        encoding="utf-8", errors="replace"))
    cells = int(re.search(r"cells:\s+(\d+)", (CASE_DIR / "log.checkMesh")
                          .read_text(errors="replace")).group(1))
    model = re.search(r"RASModel\s+(\w+);", (CASE_DIR / "case" / "constant" /
                      "turbulenceProperties").read_text(errors="replace"))
    budget = re.search(r"endTime\s+(\d+);", (CASE_DIR / "case" / "system" /
                       "controlDict").read_text(errors="replace"))

    log_rel = "mission-output/geometry-study/study-naca0015_sail/log.simpleFoam"
    mesh_rel = "mission-output/geometry-study/study-naca0015_sail/log.checkMesh"
    report_rel = "mission-output/geometry-study/study-naca0015_sail/report.md"
    case_rel = "mission-output/geometry-study/study-naca0015_sail/case"
    wsl_note = (f"(the act's copy of the WSL case {WSL_CASE}, "
                "postProcessing/forceCoeffs1/0/coefficient.dat)")

    def sci(x: float) -> str:
        return f"{x:.2e}"

    lines = [
        "# Sail panel stats: study-naca0015_sail (solved record)",
        "",
        "Internal note for transcribing onto the website panel. The NUMBERS",
        "go on the panel; the source paths below are internal only and must",
        "never appear in the website text itself.",
        "",
        "| Quantity | Value | Source |",
        "|---|---|---|",
        f"| Convergence | iteration {iteration} of a {budget.group(1)} "
        f"budget (\"SIMPLE solution converged in {converged.group(1)} "
        f"iterations\") | {log_rel} |",
    ]
    order = ["p", "Ux", "Uy", "Uz", "k", "omega"]
    for name in order:
        if name not in residuals:
            continue
        initial, final = residuals[name]
        lines.append(
            f"| {name} residual, last iteration | initial {sci(initial)}, "
            f"final {sci(final)} | {log_rel}, Time = {iteration} block |")
    lines += [
        f"| Residual convergence criterion | initial residuals below 1e-4 "
        f"for all fields (p, U, k, omega) | {case_rel}/system/fvSolution, "
        "residualControl |",
        f"| Cd (solved) | {bands['Cd']['value']} +/- "
        f"{bands['Cd']['half_band']} (95% envelope "
        f"[{bands['Cd']['envelope'][0]}, {bands['Cd']['envelope'][1]}], "
        f"settle window {bands['Cd']['window']}; final sample "
        f"{cd_final:.8f}) | {report_rel}; {log_rel} {wsl_note} |",
        f"| Cl (solved) | {bands['Cl']['value']} +/- "
        f"{bands['Cl']['half_band']} (95% envelope "
        f"[{bands['Cl']['envelope'][0]}, {bands['Cl']['envelope'][1]}], "
        f"settle window {bands['Cl']['window']}; final sample "
        f"{cl_final:.8f}) | {report_rel}; {log_rel} {wsl_note} |",
        f"| Mesh cells | {cells:,} | {mesh_rel} |",
        f"| Turbulence model | {model.group(1)} | "
        f"{case_rel}/constant/turbulenceProperties |",
        f"| Freestream | U_inf = {U_INF} m/s, chord 1.2 m, Re 6.0e6 | "
        f"{case_rel}/0/U; scripts/run_sail_study.py |",
        "",
        "Footer line for the panel: "
        f"\"AUTO-MESH - K-OMEGA SST - {cells:,} CELLS\".",
        "",
        "Notes: residuals are the solver's own linear-solver report at the",
        "final iteration; \"initial\" is the quantity the convergence",
        "control (1e-4) acts on, \"final\" is where the last sweep left the",
        "field. For p (two correctors per iteration) the initial residual",
        "is the first solve's and the final residual the last solve's.",
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"iteration": iteration, "residuals": residuals,
            "cd_final": cd_final, "cl_final": cl_final, "bands": bands,
            "cells": cells, "model": model.group(1)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Render the sail pressure+streamlines panel and its "
                    "stats note, then validate the streamline field.")
    parser.add_argument("--vtu", type=Path, default=None,
                        help="local copy of the case's internal.vtu "
                             "(default: copy it out of the WSL case)")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    vtu = args.vtu or fetch_vtu(Path(tempfile.mkdtemp()))

    out_png = args.out_dir / "naca0015_sail_streamlines.png"
    meta, surface_mesh = render(vtu, out_png)
    print(f"rendered: {meta['path']}")

    checks = run_checks(vtu, meta, surface_mesh)
    for name, result in checks.items():
        verdict = "PASS" if result.pop("pass") else "FAIL"
        print(f"check {name}: {verdict} "
              f"{json.dumps(result, default=str)}")

    stats = write_stats(args.out_dir / "sail_panel_stats.md")
    print(f"stats: {args.out_dir / 'sail_panel_stats.md'} "
          f"(iteration {stats['iteration']}, {stats['cells']:,} cells, "
          f"{stats['model']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
