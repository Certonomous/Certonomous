"""Regenerate all pressure-slice PNG images from the corrected pipeline.

Regenerates the four core pressure-slice images for the website:
  - motorBike.png (study-motorBike)
  - b52.png (study-b52)
  - naca0015_sail.png (study-naca0015_sail)
  - naca4412_wing.png (study-naca4412_wing)

Plus the streamlines variant:
  - naca0015_sail_streamlines.png

Each slice is rendered from the case's own volume output (internal.vtu),
extracted via foamToVTK. The corrected pipeline in field_render includes:
  - Decimation-correspondence fix (faces map correctly after clustering)
  - Cell-centred pressure reading (undecimated physical extremes)
  - Cp bound checking (reports mesh-degeneracy slivers)
  - Exact STL silhouette (smooth cross-section outline)

Call with --cases to point to where mission-output/geometry-study cases live.

    python scripts/regenerate_pressure_slices.py
    python scripts/regenerate_pressure_slices.py --cases /path/to/mission-output/geometry-study

By default reads from ~/Certonomous/mission-output/geometry-study.
"""

from __future__ import annotations

import argparse
import json
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

REPO = SDK.parent
DEFAULT_CASES = REPO / "mission-output" / "geometry-study"
DEFAULT_OUT_DEMO = lab_paths.PLOTS / "pressure_slices"
DEFAULT_OUT_MISSION = REPO / "mission-output" / "geometry-study"

# Configuration for each body's pressure-slice render
# (case_dir, out_png, span_axis, plane_axes, body_label, surface_file, has_streamlines)
BODIES = {
    "motorBike": {
        "case": "study-motorBike",
        "case_field_json": "motorBike_field.json",
        "span_axis": 1,
        "plane_axes": (0, 2),
        "body_label": "Motorbike at 20 m/s",
        "surface_file": None,  # foamToVTK extracts from case
        "surface_scale": 1.0,
    },
    "b52": {
        "case": "study-b52",
        "case_field_json": "b52_field.json",
        "span_axis": 0,
        "plane_axes": (2, 1),
        "body_label": "B-52 fuselage at 100 m/s",
        "surface_file": None,
        "surface_scale": 1.0,
    },
    "naca0015_sail": {
        "case": "study-naca0015_sail",
        "case_field_json": "naca0015_sail_field.json",
        "span_axis": 2,
        "plane_axes": (0, 1),
        "body_label": "NACA 0015 sail",
        "surface_file": REPO / "demo-surfaces" / "naca0015_sail.stl",
        "surface_scale": 1.0,
    },
    "naca4412_wing": {
        "case": "study-naca4412_wing",
        "case_field_json": "naca4412_wing_field.json",
        "span_axis": 1,
        "plane_axes": (0, 2),
        "body_label": "NACA 4412 wing",
        "surface_file": REPO / "demo-surfaces" / "naca4412_wing.stl",
        "surface_scale": 1.0,
    },
}


def get_body_bounds(field_json_path: Path) -> dict | None:
    """Extract bounds from the body's _field.json for slice framing."""
    try:
        data = json.loads(field_json_path.read_text(encoding="utf-8"))
        return data.get("bounds")
    except (OSError, ValueError):
        return None


def render_one_slice(case_dir: Path, out_png: Path, config: dict, wsl_prefix,
                     run_prefix_openfoam: str) -> tuple[bool, str]:
    """Render one pressure-slice PNG from a case's internal.vtu.

    Returns (success, message): whether render succeeded and a summary.
    Calls extract_pressure_slice which fetches VTU from the case and renders.
    """
    from chief_engineer.field_render import extract_pressure_slice

    # Check case exists
    if not case_dir.is_dir():
        return False, f"Case directory not found: {case_dir}"

    # Get body bounds for framing (optional; used if available)
    field_json = case_dir / config["case_field_json"]
    body_bounds = get_body_bounds(field_json)

    surface_path = config.get("surface_file")
    if surface_path and not surface_path.exists():
        surface_path = None

    # Call the extraction and rendering pipeline
    try:
        slice_png = extract_pressure_slice(
            str(case_dir), out_png,
            wsl_prefix + ([run_prefix_openfoam] if run_prefix_openfoam else []),
            span_axis=int(config["span_axis"]),
            plane_axes=tuple(config["plane_axes"]),
            body_bounds=body_bounds,
            body_label=config["body_label"],
            surface_path=surface_path if surface_path else None,
            surface_scale=float(config.get("surface_scale", 1.0)))
        if slice_png:
            return True, f"Rendered to {slice_png}"
        else:
            return False, "extract_pressure_slice returned None (likely no VTU data)"
    except Exception as e:
        return False, f"Render failed: {e}"


def read_old_cp_values(image_path: Path) -> dict | None:
    """Extract Cp statistics from the old validation JSON if it exists."""
    validation_json = image_path.parent / "validation" / f"{image_path.stem}_validation_numbers.json"
    if not validation_json.exists():
        return None
    try:
        data = json.loads(validation_json.read_text(encoding="utf-8"))
        invariants = data.get("invariants", {})
        return {
            "cp_max": invariants.get("cp_max"),
            "cp_min": min(invariants.get("suction_regions", {}).values())
            if invariants.get("suction_regions") else None,
        }
    except (OSError, ValueError):
        return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate pressure-slice images from the corrected pipeline.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES,
                        help=f"Path to mission-output/geometry-study (default: {DEFAULT_CASES})")
    parser.add_argument("--out-demo", type=Path, default=DEFAULT_OUT_DEMO,
                        help=f"Output directory for demo images (default: {DEFAULT_OUT_DEMO})")
    parser.add_argument("--out-mission", type=Path, default=DEFAULT_OUT_MISSION,
                        help=f"Output directory for mission images (default: {DEFAULT_OUT_MISSION})")
    parser.add_argument("--all", action="store_true",
                        help="Regenerate all images (default: just report status)")
    args = parser.parse_args(argv)

    # Check configuration
    if not args.cases.is_dir():
        print(f"ERROR: Cases directory not found: {args.cases}", file=sys.stderr)
        return 1

    args.out_demo.mkdir(parents=True, exist_ok=True)
    args.out_mission.mkdir(parents=True, exist_ok=True)

    # WSL/OpenFOAM invocation (from workflows/__init__.py)
    wsl_prefix = ["wsl", "-d", "Ubuntu", "-u", "foam", "--"]
    run_prefix_openfoam = "openfoam2606"

    print("=" * 70)
    print("PRESSURE-SLICE REGENERATION STATUS")
    print("=" * 70)
    print()
    print(f"Cases root: {args.cases}")
    print(f"Demo output: {args.out_demo}")
    print(f"Mission output: {args.out_mission}")
    print()
    print("Corrected pipeline features:")
    print("  ✓ Decimation-correspondence fix (faces map correctly after clustering)")
    print("  ✓ Cell-centred pressure reading (physical extremes undecimated)")
    print("  ✓ Cp bound checking (reports degenerate sliver cells)")
    print("  ✓ Exact STL silhouette (smooth cross-section outline)")
    print()

    summary = {}
    for body_name, config in BODIES.items():
        case_dir = args.cases / config["case"]
        demo_png = args.out_demo / f"{body_name}.png"
        mission_png = args.out_mission / f"{body_name}_pressure_slice.png"

        print(f"\n{body_name.upper()}")
        print("-" * 70)

        # Report old values
        old_cp = read_old_cp_values(demo_png)
        if old_cp:
            print(f"  Previous:  Cp_max = {old_cp['cp_max']:.4f}, "
                  f"Cp_min = {old_cp['cp_min']:.4f}")
        else:
            print(f"  Previous:  [no validation data found]")

        if not case_dir.is_dir():
            print(f"  Status:    SKIP (case directory not found at {case_dir})")
            summary[body_name] = "skip_no_case"
            continue

        if not args.all:
            print(f"  Status:    READY (--all not specified; no regeneration performed)")
            print(f"  Command:   python scripts/regenerate_pressure_slices.py --all")
            summary[body_name] = "ready_for_regen"
            continue

        # Actually regenerate
        success, msg = render_one_slice(case_dir, demo_png, config, wsl_prefix,
                                        run_prefix_openfoam)
        if success:
            print(f"  Status:    SUCCESS")
            print(f"  Output:    {demo_png}")
            summary[body_name] = "regenerated"
            # Also copy to mission output if different
            if demo_png != mission_png:
                try:
                    mission_png.write_bytes(demo_png.read_bytes())
                    print(f"  Copied:    {mission_png}")
                except Exception as e:
                    print(f"  Copy failed: {e}")
        else:
            print(f"  Status:    FAILED")
            print(f"  Error:     {msg}")
            summary[body_name] = "failed"

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, status in summary.items():
        icon = "✓" if "regenerated" in status else \
               "!" if "failed" in status else \
               "○" if "ready" in status else "✗"
        print(f"  {icon} {name:20s}: {status}")

    success_count = sum(1 for s in summary.values() if "regenerated" in s)
    if success_count == 0 and not args.all:
        print()
        print("To regenerate all images (requires access to case VTU files):")
        print(f"  python scripts/regenerate_pressure_slices.py --all")
        return 0

    if success_count > 0:
        print()
        print("Regenerated images are ready for validation checks:")
        print(f"  python sdk/scripts/validate_pressure_fields.py")
        print(f"  python sdk/scripts/validate_motorbike_pressure.py")
        return 0

    return 1 if any("failed" in s for s in summary.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
