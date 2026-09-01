"""Geometry admission: decide whether an uploaded surface can be run at all.

WHY THIS EXISTS
---------------
An earlier reading of an uploaded wing reported "span 0.12 m, chord 1.0 m,
thickness 3.0 m" and the act then presented numbers belonging to a different
wing. The three numbers were produced by :func:`_a2_shape.dimensions`, which
assigns roles to axes by a FIXED convention (x chordwise, y thickness, z span)
and states that convention in its own docstring as something "every surface in
this act shares". The uploaded surface did not share it: it used the ordinary
aerospace convention (x chord, y span, z thickness). The file was correct. The
reading was not.

Two rules follow, and this module is built on both.

1. A CHECK THAT ASSUMES AN AXIS CONVENTION CANNOT DETECT AN AXIS-CONVENTION
   ERROR. Every refusal below is computed on the extents SORTED by size, so
   no refusal can be produced or avoided by permuting the axes. Axis ROLES are
   discovered from the shape itself and reported; they are never assumed.

2. NOTHING IS EVER SUBSTITUTED IN SILENCE. This module returns a decision and
   a reason. When it refuses, the caller stops. When it admits, the caller
   runs the surface it was given. There is no third path in which the caller
   proceeds with a different body.

The refusals are deliberately narrow. Refusing a valid file in confident
English is a worse failure than the one this module was written to prevent,
because the customer cannot tell a wrong refusal from a right one and has no
way to argue with it.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Thresholds. Each is a physical statement, not a tuned number.
# ---------------------------------------------------------------------------

# A lifting surface is thin against its own chord. Real aerofoils run 6-24 %
# thickness-to-chord; a very thick strut or a wind-turbine root reaches ~40 %.
# Half the chord is past anything that generates lift as an aerofoil, so a
# surface thicker than this is a body, not a wing. Generous on purpose: the
# job here is to refuse the impossible, not to police the unusual.
MAX_THICKNESS_TO_CHORD = 0.50

# Larger than any aircraft ever built (the widest wingspan is ~117 m) and
# larger than any wind-turbine blade (~110 m). A surface bigger than this in
# metres is almost always a millimetre export read as metres.
MAX_PLAUSIBLE_EXTENT_M = 200.0

# Smaller than a centimetre overall is not a surface anyone means to solve.
MIN_PLAUSIBLE_EXTENT_M = 0.01

# Below this the surface has no thickness at all: a sheet, not a closed body.
MIN_THICKNESS_FRACTION = 1e-6

# Bins used when discovering which axis is chord and which is span.
_PROFILE_BINS = 24

# A chordwise sweep closes to near-nothing at the leading and trailing edges.
# A spanwise sweep is at full thickness at the root. This separates them.
_END_CLOSURE_FRACTION = 0.45


class Surface:
    """The measurements an admission decision is allowed to use."""

    def __init__(self, path, vertices, faces):
        self.path = str(path)
        self.n_vertices = len(vertices)
        self.n_faces = len(faces)
        self.lo = [min(v[i] for v in vertices) for i in range(3)]
        self.hi = [max(v[i] for v in vertices) for i in range(3)]
        self.extents = [self.hi[i] - self.lo[i] for i in range(3)]
        # Axis indices ordered small -> large. Every threshold below is
        # expressed against THIS, never against x/y/z, so that no decision can
        # be changed by permuting the axes of the file.
        self.by_size = sorted(range(3), key=lambda i: self.extents[i])
        self._vertices = vertices

    @property
    def smallest(self) -> float:
        return self.extents[self.by_size[0]]

    @property
    def middle(self) -> float:
        return self.extents[self.by_size[1]]

    @property
    def largest(self) -> float:
        return self.extents[self.by_size[2]]

    def thickness_profile(self, along: int, across: int) -> list[float]:
        """Extent along `across`, measured in bins stepping along `along`.

        This is the shape of the body seen edge-on. Swept along the chord it
        is an aerofoil: nearly nothing at the leading and trailing edges, a
        maximum in between. Swept along the span it is the planform seen from
        the front: full thickness at the root, closing only at the tip.
        """
        lo, hi = self.lo[along], self.hi[along]
        width = (hi - lo) or 1.0
        bins: list[list[float]] = [[] for _ in range(_PROFILE_BINS)]
        for v in self._vertices:
            k = int((v[along] - lo) / width * _PROFILE_BINS)
            bins[min(max(k, 0), _PROFILE_BINS - 1)].append(v[across])
        return [(max(b) - min(b)) if len(b) > 1 else 0.0 for b in bins]


def _read(path) -> Surface | None:
    """Read a surface file, or None when it cannot be read as one."""
    try:
        from chief_engineer.geometry import load_surface
        payload = load_surface(str(path), max_faces=10 ** 9)
        vertices, faces = payload["vertices"], payload["faces"]
    except Exception:
        try:
            vertices, faces = _read_stl_fallback(Path(path))
        except Exception:
            return None
    if not vertices or not faces:
        return None
    return Surface(path, vertices, faces)


def _read_stl_fallback(path: Path):
    """Binary or ASCII STL, with no dependency on the SDK being importable."""
    import struct
    raw = path.read_bytes()
    if len(raw) >= 84:
        n = struct.unpack_from("<I", raw, 80)[0]
        if 84 + 50 * n == len(raw):
            verts, faces = [], []
            off = 84
            for _ in range(n):
                v = struct.unpack_from("<12f", raw, off)
                base = len(verts)
                verts.extend([list(v[3:6]), list(v[6:9]), list(v[9:12])])
                faces.append([base, base + 1, base + 2])
                off += 50
            return verts, faces
    verts, faces, cur = [], [], []
    for line in raw.decode("ascii", "replace").splitlines():
        s = line.split()
        if s and s[0] == "vertex":
            cur.append([float(x) for x in s[1:4]])
        elif s and s[0] == "endfacet":
            if len(cur) == 3:
                base = len(verts)
                verts.extend(cur)
                faces.append([base, base + 1, base + 2])
            cur = []
    return verts, faces


def discover_axes(surf: Surface) -> dict:
    """Which axis carries the chord, which the span, which the thickness.

    Measured from the body, never assumed. The thinnest direction is the
    thickness -- that much is true of any lifting surface however it is
    oriented. The other two are told apart by sweeping the body along each and
    watching how the thickness behaves: an aerofoil closes at BOTH ends of the
    chord, whereas along the span the root is at full thickness.
    """
    t_axis = surf.by_size[0]
    a, b = surf.by_size[1], surf.by_size[2]
    t_max = surf.extents[t_axis] or 1.0

    def end_closure(axis: int) -> float:
        """How much of full thickness survives at the more open of the two ends."""
        prof = surf.thickness_profile(axis, t_axis)
        return max(prof[0], prof[-1]) / t_max

    close_a, close_b = end_closure(a), end_closure(b)
    # The chord is the axis that closes down harder at its ends.
    chord_axis, span_axis = (a, b) if close_a < close_b else (b, a)
    names = "XYZ"
    return {
        "chord_axis": chord_axis, "span_axis": span_axis,
        "thickness_axis": t_axis,
        "chord_m": surf.extents[chord_axis],
        "span_m": surf.extents[span_axis],
        "thickness_m": surf.extents[t_axis],
        "convention": (f"chord along {names[chord_axis]}, "
                       f"span along {names[span_axis]}, "
                       f"thickness along {names[t_axis]}"),
        "end_closure": {names[a]: close_a, names[b]: close_b},
        "confident": abs(close_a - close_b) > 0.10,
    }


def admit(path) -> dict:
    """Decide whether this surface can be run, and say why in plain English.

    Returns a dict with ``admitted`` (bool), ``reason`` (customer-facing
    sentence, empty when admitted), ``remedy`` (what to do about it) and the
    measurements the decision was taken on. It never returns a substitute
    geometry and it never returns a decision it did not compute.
    """
    surf = _read(path)
    name = Path(str(path)).name
    if surf is None:
        return {"admitted": False, "path": str(path), "code": "UNREADABLE",
                "reason": f"I could not read {name} as a surface.",
                "remedy": "Re-export it as a binary STL or an OBJ and send it "
                          "again.",
                "measurements": None, "axes": None}

    m = {"largest_m": surf.largest, "middle_m": surf.middle,
         "smallest_m": surf.smallest, "faces": surf.n_faces}

    def refuse(code, reason, remedy):
        return {"admitted": False, "path": str(path), "code": code,
                "reason": reason, "remedy": remedy, "measurements": m,
                "axes": None}

    # --- 1. Nothing there at all -------------------------------------------
    if surf.largest <= 0:
        return refuse(
            "DEGENERATE",
            f"{name} has no size in any direction, so there is nothing to "
            f"solve around.",
            "Check the export: the surface appears to be a single point.")

    # --- 2. A sheet with no thickness --------------------------------------
    if surf.smallest / surf.largest < MIN_THICKNESS_FRACTION:
        return refuse(
            "NO_THICKNESS",
            f"{name} is a flat sheet: it has no thickness at all, so it has "
            f"no inside and no outside and I cannot mesh a flow around it.",
            "Export the wing as a closed solid surface rather than a "
            "mid-surface or a single skin.")

    # --- 3. Scale. Sorted extents, so axis order cannot mask a units error --
    if surf.largest > MAX_PLAUSIBLE_EXTENT_M:
        return refuse(
            "TOO_LARGE",
            f"{name} measures {surf.largest:,.0f} m across its longest "
            f"direction, which is larger than any aircraft ever built. I read "
            f"the file in metres, so this is almost certainly a millimetre "
            f"export.",
            f"Re-export in metres. If the shape is right, dividing by 1000 "
            f"gives a {surf.largest / 1000.0:,.3g} m body, which is a "
            f"believable size.")

    if surf.largest < MIN_PLAUSIBLE_EXTENT_M:
        return refuse(
            "TOO_SMALL",
            f"{name} measures {surf.largest:.4g} m across its longest "
            f"direction -- under a centimetre overall. I read the file in "
            f"metres, so this is almost certainly a scale error.",
            "Re-export in metres at the size you want solved.")

    # --- 4. Too thick to be a lifting surface ------------------------------
    # Computed on the two smallest extents, so it holds whatever the axis
    # order is. This is the check the original defect needed and did not have.
    ratio = surf.smallest / (surf.middle or 1.0)
    if ratio > MAX_THICKNESS_TO_CHORD:
        return refuse(
            "NOT_A_LIFTING_SURFACE",
            f"{name} is {surf.smallest:.3g} m thick against a "
            f"{surf.middle:.3g} m chord -- {ratio * 100:.0f}% thickness. A "
            f"wing is thin against its chord; nothing above about 40% works "
            f"as an aerofoil. This is a body, not a lifting surface.",
            "If you meant to send a wing, check that the export is the wing "
            "alone. If you meant to send a fuselage or a fairing, say so and "
            "I will set the case up as a bluff body instead.")

    # --- Admitted. Say what was understood, and on what evidence. ----------
    axes = discover_axes(surf)
    return {"admitted": True, "path": str(path), "code": "ADMITTED",
            "reason": "", "remedy": "", "measurements": m, "axes": axes}


def sentences(decision: dict) -> list[str]:
    """The admission beat, as lines a customer reads. No internal vocabulary."""
    if not decision["admitted"]:
        return [decision["reason"], decision["remedy"],
                "I have not run anything and I have not substituted another "
                "shape."]
    a = decision["axes"]
    lines = [
        f"Surface read: {a['chord_m']:.3g} m chord, {a['span_m']:.3g} m span, "
        f"{a['thickness_m']:.3g} m maximum thickness -- "
        f"{a['thickness_m'] / a['chord_m'] * 100:.1f}% of chord.",
        f"I worked the orientation out from the shape itself: "
        f"{a['convention']}.",
    ]
    if not a["confident"]:
        lines.append(
            "Chord and span are close enough here that I would rather you "
            "confirmed which is which before I spend anything.")
    return lines


def agrees_with(path, convention: tuple[int, int, int]) -> dict:
    """Does this file use the axis roles some downstream tool assumes?

    ``convention`` is ``(chord_axis, span_axis, thickness_axis)``. This is the
    question the original defect never asked. A caller that assumes a fixed
    convention must ask it before measuring, and must re-orient or stop when
    the answer is no -- it must never measure anyway and report the result as
    the file's dimensions.
    """
    decision = admit(path)
    if not decision["admitted"]:
        return {"agrees": False, "decision": decision, "found": None}
    a = decision["axes"]
    found = (a["chord_axis"], a["span_axis"], a["thickness_axis"])
    names = "XYZ"
    return {
        "agrees": found == tuple(convention),
        "found": found,
        "found_convention": a["convention"],
        "expected_convention": (
            f"chord along {names[convention[0]]}, "
            f"span along {names[convention[1]]}, "
            f"thickness along {names[convention[2]]}"),
        "decision": decision,
    }
