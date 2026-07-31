"""Surface geometry for the control-room viewport.

The viewport shows the mission's actual geometry.  Real surfaces arrive as OBJ
or STL (binary or ASCII) — the airplane will land here exactly as the
motorBike does — and parametric cases generate their surface from the design
variables the mission is optimizing.

Meshes are decimated server-side before they reach the browser: a 132k-vertex
motorBike is 10 MB of text that no canvas needs in order to draw a readable
wireframe.  Decimation keeps whole triangles and remaps only the vertices they
reference, so the silhouette survives while the payload drops by ~30x.
"""

from __future__ import annotations

import math
import re
import struct
from pathlib import Path
from typing import Any

DEFAULT_MAX_FACES = 9000


def load_surface(path: str | Path, *, max_faces: int = DEFAULT_MAX_FACES) -> dict[str, Any]:
    """Read an OBJ or STL surface and return a decimated wireframe payload."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".obj":
        vertices, faces = _read_obj(path)
    elif suffix == ".stl":
        vertices, faces = _read_stl(path)
    else:
        raise ValueError(f"unsupported surface format: {suffix!r}")
    if not vertices or not faces:
        raise ValueError(f"{path.name} contains no drawable surface")
    return _package(vertices, faces, max_faces, path.stem)


def _read_obj(path: Path) -> tuple[list[list[float]], list[list[int]]]:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    with path.open("r", errors="replace") as stream:
        for line in stream:
            if line.startswith("v "):
                parts = line.split()
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith("f "):
                indices = []
                for token in line.split()[1:]:
                    raw = token.split("/")[0]
                    if not raw:
                        continue
                    index = int(raw)
                    # OBJ indices are 1-based; negatives count back from the end.
                    indices.append(index - 1 if index > 0 else len(vertices) + index)
                if len(indices) >= 3:
                    # Fan-triangulate polygons so the viewport only handles triangles.
                    for k in range(1, len(indices) - 1):
                        faces.append([indices[0], indices[k], indices[k + 1]])
    return vertices, faces


def _read_stl(path: Path) -> tuple[list[list[float]], list[list[int]]]:
    data = path.read_bytes()
    if _looks_ascii(data):
        return _read_stl_ascii(data.decode("ascii", errors="replace"))
    return _read_stl_binary(data)


def _looks_ascii(data: bytes) -> bool:
    head = data[:256].lstrip().lower()
    if not head.startswith(b"solid"):
        return False
    # A binary STL may still begin with "solid" in its 80-byte header; the
    # declared triangle count is the reliable discriminator.
    if len(data) >= 84:
        count = struct.unpack("<I", data[80:84])[0]
        if len(data) == 84 + count * 50:
            return False
    return b"facet" in data[:2048].lower()


def _read_stl_ascii(text: str) -> tuple[list[list[float]], list[list[int]]]:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    current: list[int] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("vertex"):
            parts = stripped.split()
            vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            current.append(len(vertices) - 1)
        elif stripped.startswith("endfacet"):
            if len(current) >= 3:
                faces.append(current[:3])
            current = []
    return vertices, faces


def _read_stl_binary(data: bytes) -> tuple[list[list[float]], list[list[int]]]:
    if len(data) < 84:
        raise ValueError("STL file is too short to be valid")
    count = struct.unpack("<I", data[80:84])[0]
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    offset = 84
    for _ in range(count):
        if offset + 50 > len(data):
            break
        values = struct.unpack_from("<12f", data, offset)
        base = len(vertices)
        vertices.append(list(values[3:6]))
        vertices.append(list(values[6:9]))
        vertices.append(list(values[9:12]))
        faces.append([base, base + 1, base + 2])
        offset += 50
    return vertices, faces


def _cluster(vertices, faces, resolution: int):
    """Vertex-cluster decimation: snap to a grid, then rebuild the triangles.

    Dropping every Nth triangle would keep isolated slivers that no longer
    touch each other — filled, they read as confetti rather than a surface.
    Clustering merges nearby vertices instead, so the reduced mesh stays
    connected and the shape survives.
    """
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    low = (min(xs), min(ys), min(zs))
    high = (max(xs), max(ys), max(zs))
    size = max(high[i] - low[i] for i in range(3)) or 1.0
    cell = size / max(1, resolution)

    cells: dict[tuple[int, int, int], int] = {}
    sums: list[list[float]] = []
    counts: list[int] = []
    owner: list[int] = []
    for vertex in vertices:
        key = tuple(int((vertex[i] - low[i]) // cell) for i in range(3))
        index = cells.get(key)
        if index is None:
            index = len(sums)
            cells[key] = index
            sums.append([0.0, 0.0, 0.0])
            counts.append(0)
        for i in range(3):
            sums[index][i] += vertex[i]
        counts[index] += 1
        owner.append(index)

    out_vertices = [[sums[i][k] / counts[i] for k in range(3)] for i in range(len(sums))]
    seen: set[tuple[int, int, int]] = set()
    out_faces: list[list[int]] = []
    for face in faces:
        if len(face) < 3:
            continue
        try:
            mapped = [owner[face[0]], owner[face[1]], owner[face[2]]]
        except IndexError:
            continue
        # A triangle whose corners collapsed into the same cell has no area.
        if mapped[0] == mapped[1] or mapped[1] == mapped[2] or mapped[0] == mapped[2]:
            continue
        key = tuple(sorted(mapped))
        if key in seen:
            continue
        seen.add(key)
        out_faces.append(mapped)
    return out_vertices, out_faces


def _package(vertices, faces, max_faces: int, name: str) -> dict[str, Any]:
    total = len(faces)
    out_vertices, out_faces = vertices, faces
    if total > max_faces:
        # Search a grid resolution that lands near the target triangle count.
        resolution = 56
        for _ in range(6):
            out_vertices, out_faces = _cluster(vertices, faces, resolution)
            if len(out_faces) > max_faces * 1.35:
                resolution = max(8, int(resolution * 0.78))
            elif len(out_faces) < max_faces * 0.45:
                resolution = int(resolution * 1.3)
            else:
                break
        # Only drop whole triangles if clustering still overshoots.
        if len(out_faces) > max_faces:
            keep = max(1, math.ceil(len(out_faces) / max_faces))
            out_faces = out_faces[::keep]

    xs = [v[0] for v in out_vertices] or [0.0]
    ys = [v[1] for v in out_vertices] or [0.0]
    zs = [v[2] for v in out_vertices] or [0.0]
    return {
        "name": name,
        "vertices": [[round(c, 5) for c in v] for v in out_vertices],
        "faces": out_faces,
        "triangles_total": total,
        "triangles_shown": len(out_faces),
        "bounds": {"min": [min(xs), min(ys), min(zs)],
                   "max": [max(xs), max(ys), max(zs)]},
    }


def wing_surface(span: float, area: float, *, sweep_deg: float = 27.5,
                 taper: float = 0.3, n_chord: int = 9,
                 n_span: int = 17) -> dict[str, Any]:
    """Generate the parametric wing a design candidate actually is.

    A symmetric tapered planform swept at the quarter chord, with a parabolic
    thickness distribution so the viewport shows a body, not a sheet. The
    planform is exact — root and tip chord follow from span, area, and taper —
    because the point of drawing candidates is that their differences are real.
    """
    span = max(float(span), 1e-3)
    area = max(float(area), 1e-3)
    taper = min(max(float(taper), 0.05), 1.0)
    semi = span / 2.0
    root_chord = 2.0 * area / (span * (1.0 + taper))
    tip_chord = taper * root_chord
    tan_sweep = math.tan(math.radians(sweep_deg))

    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    stations = [semi * (2.0 * i / (n_span - 1) - 1.0) for i in range(n_span)]
    for y in stations:
        eta = abs(y) / semi
        chord = root_chord + (tip_chord - root_chord) * eta
        # Sweep the quarter-chord line; x runs streamwise, z is vertical.
        x_quarter = abs(y) * tan_sweep
        x_le = x_quarter - 0.25 * chord
        for j in range(n_chord):
            xc = j / (n_chord - 1)
            x = x_le + xc * chord
            thickness = 0.10 * chord * 4.0 * xc * (1.0 - xc)
            vertices.append([x, y, thickness / 2.0])
            vertices.append([x, y, -thickness / 2.0])
    per_station = 2 * n_chord
    for i in range(n_span - 1):
        base_a, base_b = i * per_station, (i + 1) * per_station
        for j in range(n_chord - 1):
            for offset in (0, 1):   # upper surface, then lower
                a = base_a + 2 * j + offset
                b = base_b + 2 * j + offset
                c = base_b + 2 * (j + 1) + offset
                d = base_a + 2 * (j + 1) + offset
                faces.append([a, b, c])
                faces.append([a, c, d])

    xs = [v[0] for v in vertices]
    zs = [v[2] for v in vertices]
    return {
        "name": f"wing span={span:.3g} m area={area:.3g} m2",
        "vertices": [[round(c, 5) for c in v] for v in vertices],
        "faces": faces,
        "triangles_total": len(faces),
        "triangles_shown": len(faces),
        "bounds": {"min": [min(xs), -semi, min(zs)],
                   "max": [max(xs), semi, max(zs)]},
    }


def valve_surface(opening_angle_deg: float, *, root_radius: float = 0.0115,
                  root_length: float = 0.030, n_leaflets: int = 3,
                  wall_segments: int = 48, n_u: int = 7,
                  n_v: int = 9) -> dict[str, Any]:
    """Generate the parametric three-leaflet valve a candidate angle actually is.

    An idealized engineering rendering — honestly parametric, no anatomy. A short
    root tube carries three leaflet petals hinged on the wall at the outlet; the
    leaflet opening angle sets how far each petal swings inward toward the axis
    and upstream, which fixes the central orifice the flow squeezes through:

        orifice radius = root_radius * sin(theta)

    the same geometric measure the pressure-loss physics consumes, so the picture
    and the number move together. Larger angle → leaflets lie back toward the
    wall → wider orifice; smaller angle → petals pinch the centre. The flow axis
    runs along +x so the viewport shows the tri-leaflet face at a three-quarter
    view, exactly as a wing candidate does.
    """
    theta = math.radians(min(max(float(opening_angle_deg), 1.0), 90.0))
    R = float(root_radius)
    L = float(root_length)
    # The free-edge radius follows sin(theta) so the orifice still opens and
    # pinches monotonically with the angle, but a rendering scale keeps a visible
    # leaflet band even at full open (a real leaflet is never a zero-width sliver)
    # — the picture stays legible without breaking the honest parametrisation.
    orifice_r = R * math.sin(theta) * 0.80
    # How far the free edge swings upstream off the outlet plane: wide open
    # swings little, pinched swings deep upstream — with a small floor so the
    # three leaflets read as three even when the valve is nearly open.
    depth = R * (math.cos(theta) * 0.85 + 0.14)

    vertices: list[list[float]] = []
    faces: list[list[int]] = []

    # --- root tube wall: two rings joined into a short open cylinder ---
    for seg in range(wall_segments):
        ang = 2.0 * math.pi * seg / wall_segments
        y, z = R * math.cos(ang), R * math.sin(ang)
        vertices.append([0.0, y, z])
        vertices.append([L, y, z])
    for seg in range(wall_segments):
        a = 2 * seg
        b = 2 * ((seg + 1) % wall_segments)
        faces.append([a, a + 1, b + 1])
        faces.append([a, b + 1, b])

    # --- three leaflet petals ---
    hinge_half = math.radians(52.0)   # angular half-width at the hinge (leaves a gap)
    for k in range(n_leaflets):
        phi = 2.0 * math.pi * k / n_leaflets
        base = len(vertices)
        for iu in range(n_u + 1):
            u = iu / n_u                      # 0 hinge (wall) → 1 free edge (orifice)
            r = R + (orifice_r - R) * u
            x = L - depth * math.sin(u * math.pi / 2.0)
            width = hinge_half * (1.0 - 0.55 * u)   # petal narrows toward the axis
            for iv in range(n_v + 1):
                v = -1.0 + 2.0 * iv / n_v
                ang = phi + v * width
                # A mild belly so the petal reads as a curved leaflet, not a flat fin.
                belly = 0.12 * R * math.sin(u * math.pi) * (1.0 - v * v)
                vertices.append([x - belly, r * math.cos(ang), r * math.sin(ang)])
        stride = n_v + 1
        for iu in range(n_u):
            for iv in range(n_v):
                a = base + iu * stride + iv
                b = base + (iu + 1) * stride + iv
                faces.append([a, b, b + 1])
                faces.append([a, b + 1, a + 1])

    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    return {
        "name": f"valve opening={opening_angle_deg:g}° orifice={orifice_r*1e3:.1f} mm r",
        "vertices": [[round(c, 6) for c in v] for v in vertices],
        "faces": faces,
        "triangles_total": len(faces),
        "triangles_shown": len(faces),
        "bounds": {"min": [min(xs), min(ys), min(zs)],
                   "max": [max(xs), max(ys), max(zs)]},
    }


def cylinder_surface(diameter: float = 1.0, *, span: float = 2.0,
                     segments: int = 64) -> dict[str, Any]:
    """Generate the parametric cylinder a 2D mission is actually solving."""
    radius = max(diameter, 1e-6) / 2.0
    half = span / 2.0
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    for index in range(segments):
        angle = 2 * math.pi * index / segments
        x, y = radius * math.cos(angle), radius * math.sin(angle)
        vertices.append([x, y, -half])
        vertices.append([x, y, half])
    for index in range(segments):
        a = 2 * index
        b = 2 * ((index + 1) % segments)
        faces.append([a, a + 1, b + 1])
        faces.append([a, b + 1, b])
    return {
        "name": f"cylinder D={diameter:.3g} m",
        "vertices": [[round(c, 5) for c in v] for v in vertices],
        "faces": faces,
        "triangles_total": len(faces),
        "triangles_shown": len(faces),
        "bounds": {"min": [-radius, -radius, -half], "max": [radius, radius, half]},
    }


def available_surfaces(root: str | Path) -> list[str]:
    root = Path(root)
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir()
                  if p.suffix.lower() in {".obj", ".stl"})


# --------------------------------------------------------------------------
# Section measurement, and the lift prior that reads it
# --------------------------------------------------------------------------
# ``_a2_shape.identify`` measures a received surface's three overall extents
# against a known body, so a file arriving under the right name carrying a
# different body disagrees on the measurement rather than on the label. This
# is the same idea taken one step inward: the extents say how big a wing is,
# and these say what SECTION it is — how much camber it carries, where the
# camber peaks, how thick it is, and whether the file has a built-in
# incidence relative to its own axes.
#
# Both numbers are needed together because a lift curve can be shifted by
# either one. A cambered section lifts at zero angle; so does a symmetric
# section mounted at an incidence the sweep does not count. Measuring only
# one of them cannot tell those two apart.

# A four-digit NACA writes its maximum camber as the first digit, in percent
# of chord, so "00xx" is exactly zero camber. Nothing measured off a
# triangulated surface is exactly zero, so a section counts as symmetric when
# its measured camber is under this fraction of chord: 0.1% of chord is an
# order of magnitude below the 1% that the smallest non-zero four-digit digit
# would carry, and comfortably above STL round-off.
SYMMETRIC_CAMBER_MAX = 0.001
# The same allowance in degrees for a built-in incidence.
ZERO_INCIDENCE_MAX_DEG = 0.05
# How much lift coefficient counts as "no lift" at a zero-angle reference.
# A vortex-lattice solve of a genuinely symmetric wing at true zero incidence
# returns machine-zero circulation; anything at the second decimal place is a
# section or a reference, not arithmetic.
ZERO_LIFT_CL_MAX = 0.01


def section_measurement(vertices, faces, *, span_frac: float = 0.5,
                        stations: int = 60) -> dict[str, Any] | None:
    """Measure one spanwise section of a wing surface.

    Cuts the triangulation at a plane a fraction of the way out the span and
    reads the outline it produces: leading and trailing edge, camber line
    about the chord line joining them, maximum thickness, and the incidence
    the file was written with. Axes are inferred from the body itself —
    largest extent is span, smallest is thickness — so no caller has to
    declare a convention and no surface is measured on the wrong axis.

    Returns None when the plane produces no usable outline, so a caller can
    say the section could not be read rather than report a shape it never
    measured. Nothing here is fitted: every value is read off the surface's
    own points.
    """
    if not vertices or not faces:
        return None
    extents = [max(v[a] for v in vertices) - min(v[a] for v in vertices)
               for a in range(3)]
    order = sorted(range(3), key=lambda a: extents[a])
    thick_a, chord_a, span_a = order
    lo = min(v[span_a] for v in vertices)
    hi = max(v[span_a] for v in vertices)
    plane = lo + (hi - lo) * float(span_frac)

    points: list[tuple[float, float]] = []
    for tri in faces:
        corners = [vertices[i] for i in tri]
        for u, w in ((0, 1), (1, 2), (2, 0)):
            a, b = corners[u], corners[w]
            sa, sb = a[span_a], b[span_a]
            if (sa - plane) * (sb - plane) > 0 or sa == sb:
                continue
            t = (plane - sa) / (sb - sa)
            points.append((a[chord_a] + t * (b[chord_a] - a[chord_a]),
                           a[thick_a] + t * (b[thick_a] - a[thick_a])))
    if len(points) < 8:
        return None

    xs = [p[0] for p in points]
    x_le, x_te = min(xs), max(xs)
    chord = x_te - x_le
    if chord <= 0:
        return None
    near = 0.002 * chord
    at_le = [p[1] for p in points if p[0] - x_le <= near]
    at_te = [p[1] for p in points if x_te - p[0] <= near]
    y_le = sum(at_le) / len(at_le)
    y_te = sum(at_te) / len(at_te)

    # The chord line is the leading-edge-to-trailing-edge line of THIS file,
    # so camber is measured about the section's own chord and the incidence
    # of that chord line is reported separately instead of leaking into it.
    def on_chord(fraction: float) -> float:
        return y_le + (y_te - y_le) * fraction

    # Upper and lower surface are separated by the chord line rather than by
    # binning, because a coarse export can put its upper and lower points at
    # different chordwise stations and a bin would then hold one surface only.
    # A point sitting ON the chord line belongs to both, which is what keeps a
    # closed leading and trailing edge on both curves.
    on_line = 1e-6 * chord
    upper: list[tuple[float, float]] = []
    lower: list[tuple[float, float]] = []
    for x, y in points:
        deviation = y - on_chord((x - x_le) / chord)
        if abs(deviation) <= on_line:
            upper.append((x, deviation))
            lower.append((x, deviation))
        elif deviation > 0:
            upper.append((x, deviation))
        else:
            lower.append((x, deviation))
    if len(upper) < 3 or len(lower) < 3:
        return None
    upper.sort()
    lower.sort()

    def interpolate(curve: list[tuple[float, float]], x: float) -> float:
        if x <= curve[0][0]:
            return curve[0][1]
        if x >= curve[-1][0]:
            return curve[-1][1]
        for i in range(1, len(curve)):
            if curve[i][0] >= x:
                x0, y0 = curve[i - 1]
                x1, y1 = curve[i]
                if x1 == x0:
                    return y1
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return curve[-1][1]

    # Only where BOTH curves carry their own points. Reading a camber line
    # past the end of one of them would be reading the clamp, not the surface.
    x_from = max(upper[0][0], lower[0][0])
    x_to = min(upper[-1][0], lower[-1][0])
    if x_to <= x_from:
        return None

    camber_max, camber_at, thick_max, thick_at = 0.0, 0.0, 0.0, 0.0
    for i in range(1, stations):
        x = x_from + (x_to - x_from) * i / stations
        fraction = (x - x_le) / chord
        up, down = interpolate(upper, x), interpolate(lower, x)
        camber = (up + down) / 2.0
        if abs(camber) > abs(camber_max):
            camber_max, camber_at = camber, fraction
        if up - down > thick_max:
            thick_max, thick_at = up - down, fraction

    return {
        "span_fraction": float(span_frac),
        "chord": chord,
        # Positive incidence is nose up: the leading edge above the trailing
        # edge in the file's own axes.
        "incidence_deg": math.degrees(math.atan2(y_le - y_te, chord)),
        "max_camber_frac_chord": camber_max / chord,
        "max_camber_at_x_over_c": camber_at,
        "max_thickness_frac_chord": thick_max / chord,
        "max_thickness_at_x_over_c": thick_at,
        "symmetric": (abs(camber_max / chord) <= SYMMETRIC_CAMBER_MAX),
    }


def measure_section(path: str | Path, *, span_frac: float = 0.5
                    ) -> dict[str, Any] | None:
    """:func:`section_measurement` straight off a surface file on disk.

    No decimation: a merged vertex moves a camber line, and the camber line is
    the measurement.
    """
    try:
        payload = load_surface(path, max_faces=10 ** 9)
    except (OSError, ValueError):
        return None
    return section_measurement(payload["vertices"], payload["faces"],
                               span_frac=span_frac)


def declares_symmetric_section(name: str) -> bool | None:
    """Whether a body's NAME declares a symmetric section.

    True for a four-digit NACA whose first digit is zero (NACA 0012, 0015),
    False for one that declares camber (NACA 4412), None when the name makes
    no section claim at all and there is nothing to hold it to.
    """
    match = re.search(r"naca[\s_-]*(\d{4})\b", str(name or ""), re.IGNORECASE)
    if not match:
        return None
    return match.group(1)[0] == "0"


def zero_lift_report(*, name: str, alpha_deg: float, cl: float,
                     camber_frac_chord: float | None = None,
                     incidence_deg: float | None = None,
                     cl_tolerance: float = ZERO_LIFT_CL_MAX,
                     camber_tolerance: float = SYMMETRIC_CAMBER_MAX,
                     incidence_tolerance: float = ZERO_INCIDENCE_MAX_DEG
                     ) -> dict[str, Any] | None:
    """Check a solved lift against what the section it is named for permits.

    The prior is the oldest one in thin-airfoil theory and it has no free
    parameters: a section with no camber has no circulation at zero
    incidence, so a body presented as a symmetric section must read zero lift
    at its own zero-angle reference. Non-zero lift there means one of exactly
    two things, and the report says which is available to distinguish them:
    the section carries camber, or the angle is being measured from an axis
    that is not the chord line.

    Same shape as :func:`~chief_engineer.field_render.cp_bound_report`: it
    never alters a measured value, it returns a disclosure. ``name`` is what
    the body is about to be CALLED on screen, because the contradiction a
    viewer sees is between the label and the curve.

    Returns None when nothing claims symmetry — neither the name nor a camber
    measurement — since then there is no prior to check, and when the angle
    is not the zero-angle reference.
    """
    if abs(float(alpha_deg)) > 1e-9:
        return None
    declared = declares_symmetric_section(name)
    measured_symmetric = (None if camber_frac_chord is None
                          else abs(float(camber_frac_chord)) <= camber_tolerance)
    if not declared and not measured_symmetric:
        return None

    lifting = abs(float(cl)) > cl_tolerance
    offset = (incidence_deg is not None
              and abs(float(incidence_deg)) > incidence_tolerance)
    report: dict[str, Any] = {
        "name": name,
        "alpha_deg": float(alpha_deg),
        "cl": float(cl),
        "cl_tolerance": cl_tolerance,
        "declared_symmetric": declared,
        "measured_camber_frac_chord": camber_frac_chord,
        "measured_symmetric": measured_symmetric,
        "incidence_deg": incidence_deg,
        "incidence_offset": offset,
        # The headline flag. False means the lift on screen cannot belong to
        # the section the label names.
        "consistent": not lifting,
    }
    if lifting:
        if measured_symmetric is False:
            cause = (f"the section measures {100 * abs(camber_frac_chord):.2f}% "
                     f"camber, so the body is cambered and the name is wrong")
            short = (f"measures {100 * abs(camber_frac_chord):.2f}% camber, so "
                     f"the name is wrong")
        elif offset:
            cause = (f"the section measures symmetric but the file carries "
                     f"{incidence_deg:+.2f}° of built-in incidence, so the "
                     f"angle is not measured from the chord line")
            short = (f"carries {incidence_deg:+.2f}° of built-in incidence, so "
                     f"α is not off the chord line")
        elif measured_symmetric:
            cause = ("the section measures symmetric and carries no built-in "
                     "incidence, so the lift cannot belong to this surface")
            short = "measures symmetric at zero incidence, so this curve is "\
                    "not its"
        else:
            cause = ("no section measurement accompanies the name, so either "
                     "the body is cambered or the angle reference is offset")
            short = "is unmeasured, so either it is cambered or α is offset"
        report["caveat"] = (
            f"{name} is presented as a symmetric section, which carries no "
            f"lift at its own zero-angle reference, but the solved lift "
            f"coefficient at α = {float(alpha_deg):g}° is {float(cl):.4f}: "
            f"{cause}. State the section that produced the curve, or state "
            f"the reference the angle is measured from; do not present this "
            f"curve under this name.")
        # The same finding at camera length. The caveat above is the record;
        # this is the sentence a narrator can actually say.
        report["headline"] = (f"{name} is named symmetric but lifts "
                              f"{abs(float(cl)):.3f} at α = 0°. It {short}.")
    return report
