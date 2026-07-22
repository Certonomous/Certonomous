"""Parametric idealized three-leaflet aortic valve, open configuration.

A screening geometry the lab owns outright — no clinical data, no anatomy, just
an axisymmetric root tube with three planar leaflets whose tilt is set by a
single design parameter: the LEAFLET OPENING ANGLE.  The angle controls how far
the three leaflets swing off the wall toward the axis, and therefore the size of
the central orifice the flow squeezes through.

    opening_angle -> 90 deg : leaflets flat against the wall, orifice ~ full bore
    opening_angle -> small  : leaflets swung inward, orifice pinched

The effective orifice area is the geometric quantity the internal-flow physics
turns on, so it is computed here from the same parameter that builds the mesh
and exported alongside the STL.  Nothing here makes an experimental claim; the
reference file marks it "screening geometry — no experimental tier claims".

Pure numpy + the curriculum's hand-written binary-STL writer — no new deps.

    python generate_valve.py            # write the default angle sweep
    python generate_valve.py --list     # list the angles without writing
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
# Reuse the curriculum's proven STL writer / topology check.
sys.path.insert(0, str(_HERE.parent))
from generate import write_stl  # noqa: E402

# Idealized adult aortic-root scale (metres). These set the geometry only; the
# flow rates come from the physiological waveform module, not from here.
ROOT_RADIUS = 0.0115          # ~23 mm annulus diameter
ROOT_LENGTH = 0.030           # a short straight root segment
N_LEAFLETS = 3
_WALL_SEGMENTS = 24           # circumferential resolution of the root tube

# The angle sweep the screening study explores (degrees off the wall toward the
# axis; larger = more open).
DEFAULT_ANGLES = (35.0, 50.0, 65.0, 80.0)


def effective_orifice_area(opening_angle_deg: float,
                           root_radius: float = ROOT_RADIUS) -> float:
    """Central open area (m^2) the flow passes, as a function of opening angle.

    The three leaflets each reach from the wall toward the axis; the free edge
    sits at radius ``root_radius * sin(theta)``.  At 90 deg the leaflets lie on
    the wall and the orifice is the full bore; as the angle closes the central
    opening shrinks with sin(theta)^2.  This is the reduced geometric measure
    the pressure-loss model consumes.
    """
    theta = math.radians(max(1.0, min(90.0, opening_angle_deg)))
    orifice_radius = root_radius * math.sin(theta)
    return math.pi * orifice_radius ** 2


def _ring(z: float, radius: float, n: int) -> np.ndarray:
    ang = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    return np.stack([radius * np.cos(ang), radius * np.sin(ang),
                     np.full(n, z)], axis=1)


def build_valve(opening_angle_deg: float):
    """Return (vertices, faces) for the root tube plus three tilted leaflets."""
    n = _WALL_SEGMENTS
    verts: list[np.ndarray] = []
    faces: list[tuple[int, int, int]] = []

    # --- root tube wall (a short cylinder, open ends) ---
    inlet = _ring(0.0, ROOT_RADIUS, n)
    outlet = _ring(ROOT_LENGTH, ROOT_RADIUS, n)
    base_in = 0
    verts.append(inlet); base_out = n
    verts.append(outlet)
    for i in range(n):
        j = (i + 1) % n
        faces.append((base_in + i, base_in + j, base_out + j))
        faces.append((base_in + i, base_out + j, base_out + i))

    # --- three leaflets: planar quads hinged on the wall at the outflow ring,
    #     tilted toward the axis so their free edge sits at the orifice radius ---
    theta = math.radians(max(1.0, min(90.0, opening_angle_deg)))
    orifice_r = ROOT_RADIUS * math.sin(theta)
    hinge_z = ROOT_LENGTH
    free_z = ROOT_LENGTH - ROOT_RADIUS * math.cos(theta) * 0.6  # swing upstream
    sector = 2.0 * math.pi / N_LEAFLETS
    for k in range(N_LEAFLETS):
        a0 = k * sector + 0.06
        a1 = (k + 1) * sector - 0.06
        # two hinge points on the wall, two free points near the axis
        h0 = np.array([ROOT_RADIUS * math.cos(a0), ROOT_RADIUS * math.sin(a0), hinge_z])
        h1 = np.array([ROOT_RADIUS * math.cos(a1), ROOT_RADIUS * math.sin(a1), hinge_z])
        am = 0.5 * (a0 + a1)
        f0 = np.array([orifice_r * math.cos(am), orifice_r * math.sin(am), free_z])
        idx = len(verts_flat(verts))
        for p in (h0, h1, f0):
            verts.append(p.reshape(1, 3))
        faces.append((idx, idx + 1, idx + 2))

    V = verts_flat(verts)
    F = np.asarray(faces, dtype=np.int64)
    return V, F


def verts_flat(chunks) -> np.ndarray:
    return np.concatenate([c.reshape(-1, 3) for c in chunks], axis=0)


def angle_name(opening_angle_deg: float) -> str:
    return f"valve_{int(round(opening_angle_deg)):02d}"


def write_valve(opening_angle_deg: float, root: Path | None = None) -> Path:
    root = root or _HERE
    V, F = build_valve(opening_angle_deg)
    name = angle_name(opening_angle_deg)
    return write_stl(root / f"{name}.stl", V, F, name=name)


def geometry_table(angles=DEFAULT_ANGLES) -> dict:
    """Angle -> {orifice_area_m2, orifice_radius_m}; the physics reads this."""
    table = {}
    for a in angles:
        table[f"{a:g}"] = {
            "opening_angle_deg": float(a),
            "orifice_area_m2": effective_orifice_area(a),
            "orifice_radius_m": ROOT_RADIUS * math.sin(math.radians(a)),
        }
    return table


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--list" in argv:
        for a in DEFAULT_ANGLES:
            print(f"{angle_name(a)}  opening {a:g} deg  "
                  f"orifice {effective_orifice_area(a)*1e6:.1f} mm^2")
        return 0
    for a in DEFAULT_ANGLES:
        path = write_valve(a)
        print("wrote", path.name, f"(orifice {effective_orifice_area(a)*1e6:.1f} mm^2)")
    (_HERE / "orifice_table.json").write_text(json.dumps(geometry_table(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
