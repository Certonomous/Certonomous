#!/usr/bin/env python3
"""ACT A DISPLAY SURFACE -- the T23/T24 solved body, as a binary STL.

WHY THIS FILE EXISTS.  Sanaa's directive
`etc/sessions/2026-09-01T0320Z_sanaa_actA_geometry_screen.md` item (1) orders the
Act A upload surface REGENERATED FROM THE SOLVED GEOMETRY "so the uploaded file
IS the solved body", and the earlier directive
`etc/sessions/2026-09-01T0310Z_sanaa_actA_figure_header_standard.md` makes that a
precondition for the screen sentence "16 operating points solved on this
geometry, 39,680 cells" being TRUE.

The retired file `cases/demo-surfaces/motor_in_duct.stl` is NOT that body.  It is
dimensioned from `verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md`,
a DIFFERENT (cfd-team) case, and its own 80-byte header says so:
    "ACT A motor-in-duct display surface (F28 D=0.25 L=0.2 Dhub=0.075)"
Measured differences against the solved case, all from the binary triangles:
    axial extent      0.200 m   vs the solved 0.750 m               (3.75x)
    centrebody        ellipsoidal nose + tail cone, 0.125 m body
                      vs the solved CONSTANT-RADIUS tube over the whole extent
    three radial struts, 96 triangles, at 0/120/240 deg, x 0.0825..0.1125 m
                      -- geometry that was NEVER SOLVED
Radii DID match: duct inner 0.125 m, centrebody outer 0.0375 m.

EVERY GEOMETRIC CONSTANT BELOW IS IMPORTED FROM THE CASE'S OWN BUILD SCRIPT,
never retyped.  `build_t23.py` is the file that generated `system/blockMeshDict`,
which `blockMesh` turned into the mesh that was solved on.  If a constant moves
there, this surface moves with it, and `--check` refuses a stale STL.

WHAT IS DRAWN, AND WHAT IS NOT.

  DRAWN, each one an exact surface of the solved domain:
    duct            cylindrical shell at r = R_DUCT, z = Z0..Z3.  The solved
                    duct wall is a ZERO-THICKNESS boundary (patch `duct_wall`),
                    so this shell has no thickness.  The retired file's 5 mm
                    duct wall was a declared display invention; it is gone.
    centrebody      cylindrical shell at r = R_O, z = Z0..Z3, in THREE named
                    axial parts so the heated section can be coloured without
                    inventing anything:
                      centrebody_upstream    z = Z0..Z1  (adiabatic wall)
                      housing_heated         z = Z1..Z2  (the conjugate housing;
                                                          this is the heated
                                                          0.125 m section)
                      centrebody_downstream  z = Z2..Z3  (adiabatic wall)
    inlet_cap /     flat discs closing the centrebody tube at z = Z0 and z = Z3.
    outlet_cap      DISCLOSED: these are the DOMAIN TRUNCATION PLANES, not
                    physical faces.  The solved centrebody is a wall that runs
                    to the inlet and outlet planes and is cut by them.  They are
                    drawn only so the STL is a closed solid.

  NOT DRAWN, each one deliberately:
    nose and tail   The solved body HAS NONE.  `build_t23.py` lines 12-18 declare
                    their removal as a scope limit of the case: "The nose and
                    tail cones of directive 3.2 are REMOVED.  The centrebody is a
                    constant-radius r_o = 0.0375 m tube over the whole axial
                    extent."  Sanaa's 03:20Z wording asks for "nose and tail";
                    that is her memory of her OWN directive 3.2, which the build
                    departed from and said so.  Drawing them would recreate the
                    exact defect this file repairs.  She can have them only by
                    ordering a new solve.  DISCLOSED, not silently omitted.
    struts          Never solved.  The solve is axisymmetric; a strut is not.
    shaft bore      R_BORE = 0.006 m is an INTERNAL boundary of the core region
                    (patch `core_bore`), z = Z1..Z2 only.  It is invisible from
                    outside a closed surface and is not drawn here.  It IS real
                    and it appears in the cross-section mesh view.
    housing wall    R_I = 0.0335 m is the housing/core interface, internal.

AXISYMMETRY.  The solve is a 5-degree wedge.  A 360-degree revolve is the honest
display of an axisymmetric solve PROVIDED THE AXISYMMETRY IS STATED, and the
screen must state it.  The revolve resolution NSEG is a DISPLAY CHOICE and is
recorded in the STL header and the manifest; it is not the solved azimuthal
discretisation, which is one cell.

AXIS CONVENTION.  The surface is written in THE SOLVED CASE'S OWN COORDINATES:
axial = +z, origin at the housing leading edge, so z runs -0.250 .. +0.500.  The
retired file used x as the axial direction.  `--axis x` emits a rotated variant
for a renderer that requires it; the rotation is a rigid body transform and
changes no dimension.

Deterministic.  numpy only.  No downloads.  ZERO SOLVER COMPUTE: this script
never invokes a mesher or a solver.

Modes:
    (default)    write the STL and the part manifest, then run --check on it
    --check      geometry guard only: measure the STL on disk against the
                 imported constants and REFUSE (exit 2) on any mismatch
    --selftest   plant a known perturbation into a scratch copy and assert the
                 guard SEES it (CLAUDE.md standing rule 3), then restore
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import shutil
import struct
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD_T23 = os.path.abspath(os.path.join(HERE, "..", "T23_P305_U10", "build_t23.py"))
STL_NAME = "t23_solved_geometry.stl"
MANIFEST_NAME = "t23_solved_geometry_parts.json"

EXIT_OK, EXIT_NOTCLEAN, EXIT_REFUSE = 0, 1, 2

#: Display choice, NOT a solved quantity.  Recorded in the header and manifest.
NSEG = 180

#: Guard tolerance.  Vertices are written as float32, whose relative resolution
#: near 0.125 m is ~1e-8 m; 1e-6 m is comfortably above the write quantum and
#: far below every dimension the guard distinguishes (the smallest is the 4 mm
#: wall, and the smallest DRAWN feature is the 0.0375 m centrebody radius).
TOL_M = 1.0e-6


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------------------------------------------------------------------------
# THE CONSTANTS.  IMPORTED FROM THE CASE THAT WAS SOLVED, NEVER RETYPED.
# --------------------------------------------------------------------------

def load_case_constants(path=BUILD_T23):
    """Import `build_t23.py` and take its geometry constants.

    `build_t23.py` guards its own side effects behind `if __name__ ==
    "__main__"`, so importing it writes nothing and runs no utility.  That is
    ASSERTED here rather than assumed: bytecode writing is disabled for the
    duration (otherwise the import drops a `__pycache__` into somebody else's
    case directory, which is itself an unwanted write), and the case
    directory's file listing plus the build script's own digest are compared
    across the import.  A solve directory that gained or lost a file because
    this display script imported something is a defect, not a nuisance.
    """
    if not os.path.isfile(path):
        refuse("no %s -- the solved case's geometry definition is the ONLY "
               "source for this surface and it is not on disk" % path)
    case_dir = os.path.dirname(path)

    def snapshot():
        return (sorted(os.listdir(case_dir)),
                hashlib.sha256(open(path, "rb").read()).hexdigest())

    before = snapshot()
    saved = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("_t23_build_readonly", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = saved
    after = snapshot()
    if before[0] != after[0]:
        refuse("importing %s changed the case directory listing (added %r, "
               "removed %r) -- the import was supposed to write nothing"
               % (path, sorted(set(after[0]) - set(before[0])),
                  sorted(set(before[0]) - set(after[0]))))
    if before[1] != after[1]:
        refuse("importing %s changed the build script itself" % path)

    need = ("D_DUCT", "R_DUCT", "R_O", "R_I", "WALL_T", "R_BORE", "L_HOUS",
            "Z0", "Z1", "Z2", "Z3", "WEDGE_TOTAL_DEG",
            "NR_BL_IN", "GR_BL_IN", "NR_MID", "GR_MID", "NR_BL_OUT",
            "GR_BL_OUT", "NR_HOUS", "NR_CORE", "NZ_UP", "NZ_MID", "NZ_DOWN",
            "R3", "R4", "R5")
    missing = [k for k in need if not hasattr(mod, k)]
    if missing:
        refuse("%s no longer defines %s -- this surface is generated from that "
               "file's constants and cannot be generated without them"
               % (path, ", ".join(missing)))
    c = {k: getattr(mod, k) for k in need}

    # Internal consistency of the imported set.  A constant that has drifted
    # out of agreement with its own derivation is a defect in the case, and
    # this surface must not paper over it.
    def eq(a, b):
        return abs(float(a) - float(b)) < 1e-12

    if not eq(c["R_DUCT"], c["D_DUCT"] / 2.0):
        refuse("R_DUCT %.12g is not D_DUCT/2 = %.12g"
               % (c["R_DUCT"], c["D_DUCT"] / 2.0))
    if not eq(c["R_I"], c["R_O"] - c["WALL_T"]):
        refuse("R_I %.12g is not R_O - WALL_T = %.12g"
               % (c["R_I"], c["R_O"] - c["WALL_T"]))
    if not eq(c["L_HOUS"], c["Z2"] - c["Z1"]):
        refuse("L_HOUS %.12g is not Z2 - Z1 = %.12g"
               % (c["L_HOUS"], c["Z2"] - c["Z1"]))
    if not eq(c["R5"], c["R_DUCT"]):
        refuse("R5 %.12g is not R_DUCT %.12g" % (c["R5"], c["R_DUCT"]))
    if not (c["Z0"] < c["Z1"] < c["Z2"] < c["Z3"]):
        refuse("axial stations are not increasing: %r"
               % [c["Z0"], c["Z1"], c["Z2"], c["Z3"]])
    if not (0.0 < c["R_BORE"] < c["R_I"] < c["R_O"] < c["R_DUCT"]):
        refuse("radial stations are not increasing: %r"
               % [c["R_BORE"], c["R_I"], c["R_O"], c["R_DUCT"]])
    return c


# --------------------------------------------------------------------------
# PRIMITIVES.  Exact surfaces of revolution; one axial division is exact for a
# cylinder, so nothing is approximated except the azimuthal discretisation.
# --------------------------------------------------------------------------

def _ring(r, z, nseg):
    th = np.linspace(0.0, 2.0 * math.pi, nseg + 1)
    return np.column_stack([r * np.cos(th), r * np.sin(th), np.full(nseg + 1, float(z))])


def cylinder_shell(r, z0, z1, nseg, outward=True):
    """Cylindrical shell, normals +r (outward) or -r."""
    A, B = _ring(r, z0, nseg), _ring(r, z1, nseg)
    tris = []
    for i in range(nseg):
        if outward:
            tris.append((A[i], A[i + 1], B[i + 1]))
            tris.append((A[i], B[i + 1], B[i]))
        else:
            tris.append((A[i], B[i + 1], A[i + 1]))
            tris.append((A[i], B[i], B[i + 1]))
    return tris


def disc(r, z, nseg, plus_z):
    """Flat disc of radius r at z, as a fan from the axis."""
    A = _ring(r, z, nseg)
    c = np.array([0.0, 0.0, float(z)])
    tris = []
    for i in range(nseg):
        tris.append((c, A[i], A[i + 1]) if plus_z else (c, A[i + 1], A[i]))
    return tris


# --------------------------------------------------------------------------
# THE SURFACE
# --------------------------------------------------------------------------

def build_parts(c, nseg=NSEG):
    """-> ordered list of (part_name, triangles).  Order is the STL order and
    is what the manifest's index ranges refer to."""
    R_DUCT, R_O = c["R_DUCT"], c["R_O"]
    Z0, Z1, Z2, Z3 = c["Z0"], c["Z1"], c["Z2"], c["Z3"]
    return [
        # The duct wall bounds the fluid from OUTSIDE, so its normal into the
        # fluid points toward the axis.  It is drawn with normals AWAY from the
        # axis so a viewer outside the duct sees a lit tube rather than a
        # back-face.  Zero thickness either way -- the solved wall has none.
        ("duct", cylinder_shell(R_DUCT, Z0, Z3, nseg, outward=True)),
        ("centrebody_upstream", cylinder_shell(R_O, Z0, Z1, nseg, outward=True)),
        ("housing_heated", cylinder_shell(R_O, Z1, Z2, nseg, outward=True)),
        ("centrebody_downstream", cylinder_shell(R_O, Z2, Z3, nseg, outward=True)),
        ("inlet_truncation_cap", disc(R_O, Z0, nseg, plus_z=False)),
        ("outlet_truncation_cap", disc(R_O, Z3, nseg, plus_z=True)),
    ]


def rotate_to_x_axial(tris):
    """Rigid rotation taking +z to +x.  Changes no dimension."""
    R = np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]])
    return [tuple(R @ np.asarray(v, float) for v in t) for t in tris]


def write_binary_stl(path, parts, header, attr_by_part=True):
    """Write the STL.  The 2-byte attribute of each facet carries the PART
    INDEX, so a renderer can colour the heated section without a second file.
    Degenerate facets are refused, not dropped: a dropped facet would break the
    manifest's index ranges, which are the only thing tying a triangle to a part.
    """
    tris, ranges, k = [], {}, 0
    attrs = []
    for pi, (name, pt) in enumerate(parts):
        ranges[name] = [k, k + len(pt)]          # [first, end) half-open
        tris.extend(pt)
        attrs.extend([pi] * len(pt))
        k += len(pt)

    tri = np.asarray([[list(v) for v in t] for t in tris], dtype=float)
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    mag = np.linalg.norm(nrm, axis=1)
    bad = int((mag <= 1e-14).sum())
    if bad:
        refuse("%d degenerate facets -- dropping them would silently break the "
               "part index ranges in the manifest" % bad)
    nrm = nrm / mag[:, None]

    n = len(tri)
    with open(path, "wb") as fh:
        fh.write(header.encode("ascii", "replace")[:80].ljust(80, b" "))
        fh.write(struct.pack("<I", n))
        rec = np.zeros(n, dtype=np.dtype([("v", "<f4", (12,)), ("a", "<u2")]))
        rec["v"][:, 0:3] = nrm
        rec["v"][:, 3:12] = tri.reshape(n, 9)
        if attr_by_part:
            rec["a"] = np.asarray(attrs, dtype="<u2")
        fh.write(rec.tobytes())
    return n, ranges


def read_binary_stl(path):
    """-> (header_bytes, ntri, vertices (3N,3) float64, attrs (N,) int)."""
    if not os.path.isfile(path):
        refuse("no %s" % path)
    b = open(path, "rb").read()
    if len(b) < 84:
        refuse("%s is %d bytes -- shorter than a binary STL header" % (path, len(b)))
    n = struct.unpack("<I", b[80:84])[0]
    want = 84 + 50 * n
    if len(b) != want:
        refuse("%s claims %d facets, which needs %d bytes; the file is %d"
               % (path, n, want, len(b)))
    arr = np.frombuffer(b, dtype=np.uint8, count=50 * n, offset=84).reshape(n, 50)
    f = arr[:, :48].copy().view("<f4").reshape(n, 12).astype(float)
    attrs = arr[:, 48:50].copy().view("<u2").reshape(n).astype(int)
    return b[:80], n, f[:, 3:12].reshape(n * 3, 3), attrs


# --------------------------------------------------------------------------
# THE GEOMETRY GUARD.  Same refusal discipline as the rest of the T-family:
# it REFUSES (exit 2) rather than degrading, and it is not waived on absence.
# --------------------------------------------------------------------------

def check_surface(path, c, manifest_path=None, axis="z"):
    """Measure the STL on disk against the imported case constants.

    REFUSES on any mismatch.  Returns the measured table on success.
    """
    hdr, n, V, attrs = read_binary_stl(path)

    if axis == "x":
        V = V[:, [2, 1, 0]] * np.array([1.0, 1.0, -1.0])   # undo rotate_to_x_axial

    ax = V[:, 2]
    rad = np.hypot(V[:, 0], V[:, 1])

    Z0, Z3 = c["Z0"], c["Z3"]
    R_O, R_DUCT = c["R_O"], c["R_DUCT"]
    bad = []

    def near(got, want, what):
        if abs(got - want) > TOL_M:
            bad.append("%s = %.9f m, registered %.9f m, difference %.3e m"
                       % (what, got, want, got - want))

    near(float(ax.min()), Z0, "axial minimum")
    near(float(ax.max()), Z3, "axial maximum")
    near(float(ax.max() - ax.min()), Z3 - Z0, "axial extent")
    near(float(rad.max()), R_DUCT, "maximum radius (duct inner wall)")

    # THREE VERTEX POPULATIONS, and every vertex must belong to one of them.
    # Anything else is geometry that was not solved.
    #   on_duct   r = R_DUCT                      the duct wall
    #   on_body   r = R_O                         the centrebody wall
    #   in_cap    r < R_O AND z is Z0 or Z3       the truncation discs
    on_duct = np.abs(rad - R_DUCT) <= TOL_M
    on_body = np.abs(rad - R_O) <= TOL_M
    at_end = (np.abs(ax - Z0) <= TOL_M) | (np.abs(ax - Z3) <= TOL_M)
    in_cap = (rad < R_O - TOL_M) & at_end

    stray = ~(on_duct | on_body | in_cap)
    if int(stray.sum()):
        rs, zs = rad[stray], ax[stray]
        bad.append("%d vertices are on NEITHER the duct (r = %.4f) NOR the "
                   "centrebody (r = %.4f) NOR a truncation cap: r in "
                   "[%.6f, %.6f], z in [%.6f, %.6f]. The solved annulus is "
                   "EMPTY and the solved centrebody is a CONSTANT-RADIUS tube "
                   "(build_t23.py lines 12-18), so this is geometry that was "
                   "never solved -- a strut, a nose or a tail."
                   % (int(stray.sum()), R_DUCT, R_O,
                      float(rs.min()), float(rs.max()),
                      float(zs.min()), float(zs.max())))

    # Named tests for the two specific falsehoods the retired surface carried,
    # so a failure message says which one rather than only "stray vertices".
    between = (rad > R_O + TOL_M) & (rad < R_DUCT - TOL_M)
    if int(between.sum()):
        bad.append("%d vertices lie strictly between the centrebody (%.4f m) "
                   "and the duct (%.4f m) -- the STRUT signature; the retired "
                   "surface carried 96 such facets at 0/120/240 degrees"
                   % (int(between.sum()), R_O, R_DUCT))
    interior = (ax > Z0 + TOL_M) & (ax < Z3 - TOL_M)
    tapered = interior & (rad < R_O - TOL_M)
    if int(tapered.sum()):
        bad.append("%d vertices sit inside the centrebody radius at an "
                   "INTERIOR axial station (r down to %.6f m at z = %.6f) -- "
                   "the NOSE/TAIL-CONE signature; the solved centrebody does "
                   "not taper"
                   % (int(tapered.sum()), float(rad[tapered].min()),
                      float(ax[tapered][int(np.argmin(rad[tapered]))])))

    # Both walls must span the FULL axial extent, end to end.
    body = rad[on_body]
    if int(on_duct.sum()) == 0:
        bad.append("no vertices at r = R_DUCT -- the guard cannot see the duct "
                   "and does NOT waive the check on absence")
    else:
        near(float(ax[on_duct].min()), Z0, "duct axial minimum")
        near(float(ax[on_duct].max()), Z3, "duct axial maximum")
    if int(on_body.sum()) == 0:
        bad.append("no vertices at r = R_O -- the guard cannot see the "
                   "centrebody and does NOT waive the check on absence")
    else:
        near(float(ax[on_body].min()), Z0, "centrebody axial minimum")
        near(float(ax[on_body].max()), Z3, "centrebody axial maximum")

    # Manifest agreement, when one is present.
    manifest = None
    if manifest_path and os.path.isfile(manifest_path):
        manifest = json.load(open(manifest_path))
        if manifest.get("n_facets") != n:
            bad.append("manifest says %r facets, the STL holds %d"
                       % (manifest.get("n_facets"), n))
        hz = manifest.get("parts", {}).get("housing_heated")
        if not hz:
            bad.append("manifest has no housing_heated part")
        else:
            lo, hi = hz
            hax = V[:, 2].reshape(n, 3)[lo:hi]
            near(float(hax.min()), c["Z1"], "heated section axial start")
            near(float(hax.max()), c["Z2"], "heated section axial end")
            near(float(hax.max() - hax.min()), c["L_HOUS"], "heated section length")

    if bad:
        refuse("%s IS NOT THE SOLVED GEOMETRY:\n    - %s"
               % (path, "\n    - ".join(bad)))

    return {
        "path": os.path.abspath(path),
        "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
        "header": hdr.decode("ascii", "replace").rstrip(),
        "n_facets": int(n),
        "axial_extent_m": [float(ax.min()), float(ax.max())],
        "axial_length_m": float(ax.max() - ax.min()),
        "duct_inner_radius_m": float(rad.max()),
        "centrebody_outer_radius_m": float(body.max()) if body.size else None,
        "vertices_on_duct": int(on_duct.sum()),
        "vertices_on_centrebody": int(on_body.sum()),
        "vertices_on_truncation_caps": int(in_cap.sum()),
        "stray_vertices": int(stray.sum()),
        "vertices_between_centrebody_and_duct": int(between.sum()),
        "manifest": manifest_path if manifest else None,
    }


# --------------------------------------------------------------------------
# THE PLANTED CONTROL (CLAUDE.md standing rule 3).  A guard not shown able to
# see a wrong surface is not evidence that the surface is right.
# --------------------------------------------------------------------------

def selftest(stl_path, c, manifest_path):
    """Plant four known defects, one per falsehood the retired file carried,
    and assert the guard REFUSES each.  Then assert the clean file passes."""
    hdr, n, V, attrs = read_binary_stl(stl_path)
    raw = open(stl_path, "rb").read()
    ok = True

    def report(label, passed, detail=""):
        nonlocal ok
        ok = ok and passed
        print("  %-46s %s%s" % (label, "PASS" if passed else "FAIL",
                                (" -- " + detail) if detail else ""))

    def guard_refuses(mutate, label):
        """Write a mutated copy to scratch and assert check_surface exits 2."""
        d = tempfile.mkdtemp(prefix="t23_surface_plant_")
        try:
            p = os.path.join(d, "planted.stl")
            open(p, "wb").write(mutate(bytearray(raw)))
            pid = os.fork()
            if pid == 0:
                sys.stdout = open(os.devnull, "w")
                try:
                    check_surface(p, c)
                except SystemExit as e:
                    os._exit(int(e.code or 0))
                os._exit(0)
            _, status = os.waitpid(pid, 0)
            rc = os.WEXITSTATUS(status)
            report(label, rc == EXIT_REFUSE, "guard exit %d, wanted %d"
                   % (rc, EXIT_REFUSE))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    print("PLANTED CONTROL on the geometry guard (CLAUDE.md standing rule 3).")
    print("Each plant is written BY BYTE OFFSET into a scratch copy; nothing "
          "is located by value and the real file is never opened for writing.\n")

    def _vert_off(facet, vert, comp):
        # 84 + 50*facet + 12 (normal) + 12*vert + 4*comp
        return 84 + 50 * facet + 12 + 12 * vert + 4 * comp

    # PLANT 1 -- THE RETIRED FILE'S ACTUAL DEFECT: the axial extent shortened
    # from the solved 0.750 m to 0.200 m.  Every z is rescaled about Z0, by
    # byte offset, because moving a single most-downstream vertex would leave
    # the other NSEG vertices at Z3 and the maximum would not move -- a plant
    # the guard could not see is not a control, it is a false green.
    Z0c, Z3c = c["Z0"], c["Z3"]
    k1 = 0.200 / (Z3c - Z0c)

    def p1(bb):
        for fi in range(n):
            for vi in range(3):
                o = _vert_off(fi, vi, 2)
                z = struct.unpack_from("<f", bb, o)[0]
                struct.pack_into("<f", bb, o, float(Z0c + (z - Z0c) * k1))
        return bytes(bb)
    guard_refuses(p1, "plant 1: axial extent 0.750 -> 0.200 m")

    # PLANT 2 -- a strut vertex, mid-annulus.  Takes a duct vertex inward to
    # the midpoint between centrebody and duct: the retired file's signature.
    duct_j = int(np.argmax(np.hypot(V[:, 0], V[:, 1])))
    fac2, vtx2 = duct_j // 3, duct_j % 3
    r_mid = 0.5 * (c["R_O"] + c["R_DUCT"])
    th2 = math.atan2(V[duct_j, 1], V[duct_j, 0])

    def p2(bb):
        struct.pack_into("<f", bb, _vert_off(fac2, vtx2, 0), float(r_mid * math.cos(th2)))
        struct.pack_into("<f", bb, _vert_off(fac2, vtx2, 1), float(r_mid * math.sin(th2)))
        return bytes(bb)
    guard_refuses(p2, "plant 2: one vertex mid-annulus (strut signature)")

    # PLANT 3 -- a nose cone.  Pull one centrebody vertex off the caps inward,
    # which is exactly what an ellipsoidal nose does.
    ax_v = V[:, 2]
    rad_v = np.hypot(V[:, 0], V[:, 1])
    cand = np.where((ax_v > c["Z0"] + 1e-6) & (ax_v < c["Z3"] - 1e-6)
                    & (rad_v < 0.5 * (c["R_O"] + c["R_DUCT"])))[0]
    if cand.size == 0:
        report("plant 3: centrebody taper (nose cone)", False,
               "no centrebody vertex available to plant into")
    else:
        k3 = int(cand[0])
        fac3, vtx3 = k3 // 3, k3 % 3
        th3 = math.atan2(V[k3, 1], V[k3, 0])
        r3 = 0.5 * c["R_O"]

        def p3(bb):
            struct.pack_into("<f", bb, _vert_off(fac3, vtx3, 0), float(r3 * math.cos(th3)))
            struct.pack_into("<f", bb, _vert_off(fac3, vtx3, 1), float(r3 * math.sin(th3)))
            return bytes(bb)
        guard_refuses(p3, "plant 3: centrebody taper (nose cone)")

    # PLANT 4 -- duct radius wrong by 1 mm, which is 250x the guard tolerance
    # and 0.8% of the radius: the kind of error a units slip makes.
    def p4(bb):
        struct.pack_into("<f", bb, _vert_off(fac2, vtx2, 0),
                         float((c["R_DUCT"] + 0.001) * math.cos(th2)))
        struct.pack_into("<f", bb, _vert_off(fac2, vtx2, 1),
                         float((c["R_DUCT"] + 0.001) * math.sin(th2)))
        return bytes(bb)
    guard_refuses(p4, "plant 4: duct radius +1 mm")

    # NEGATIVE ARM -- the untouched file must PASS.  A guard that refuses
    # everything is not a guard.
    pid = os.fork()
    if pid == 0:
        sys.stdout = open(os.devnull, "w")
        try:
            check_surface(stl_path, c, manifest_path)
        except SystemExit as e:
            os._exit(int(e.code or 0))
        os._exit(0)
    _, status = os.waitpid(pid, 0)
    report("negative arm: the clean surface PASSES", os.WEXITSTATUS(status) == 0)

    # The real file must be byte-identical afterwards.
    report("the real STL is unchanged by the control",
           hashlib.sha256(open(stl_path, "rb").read()).hexdigest()
           == hashlib.sha256(raw).hexdigest())
    return ok


# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="geometry guard only; write nothing")
    ap.add_argument("--selftest", action="store_true",
                    help="plant known defects and assert the guard sees them")
    ap.add_argument("--axis", choices=("z", "x"), default="z",
                    help="axial direction of the written surface "
                         "(default z, the solved case's own convention)")
    ap.add_argument("--nseg", type=int, default=NSEG,
                    help="azimuthal segments in the revolve (DISPLAY CHOICE)")
    ap.add_argument("--out", default=None, help="output STL path")
    a = ap.parse_args(argv)

    c = load_case_constants()
    out = a.out or os.path.join(HERE, STL_NAME)
    man = os.path.join(os.path.dirname(os.path.abspath(out)), MANIFEST_NAME)

    print("T23/T24 SOLVED GEOMETRY -- display surface")
    print("constants imported from %s\n" % BUILD_T23)
    print("  duct inner radius        R_DUCT   = %.6f m" % c["R_DUCT"])
    print("  centrebody outer radius  R_O      = %.6f m" % c["R_O"])
    print("  housing inner radius     R_I      = %.6f m  (wall %.4f m)"
          % (c["R_I"], c["WALL_T"]))
    print("  shaft bore               R_BORE   = %.6f m  (internal, not drawn)"
          % c["R_BORE"])
    print("  axial stations Z0..Z3             = %.3f %.3f %.3f %.3f m"
          % (c["Z0"], c["Z1"], c["Z2"], c["Z3"]))
    print("  axial extent                      = %.3f m" % (c["Z3"] - c["Z0"]))
    print("  heated (conjugate) section        = %.3f m, z = %.3f .. %.3f"
          % (c["L_HOUS"], c["Z1"], c["Z2"]))
    print("  solve is a %.1f-degree wedge; this surface is a 360-degree revolve\n"
          % c["WEDGE_TOTAL_DEG"])

    if a.check or a.selftest:
        if a.selftest:
            good = selftest(out, c, man)
            print("\nSELFTEST %s" % ("PASS" if good else "FAIL"))
            return EXIT_OK if good else EXIT_NOTCLEAN
        m = check_surface(out, c, man, axis=a.axis)
        print("GEOMETRY GUARD: PASS")
        print(json.dumps(m, indent=2))
        return EXIT_OK

    parts = build_parts(c, a.nseg)
    if a.axis == "x":
        parts = [(k, rotate_to_x_axial(t)) for k, t in parts]

    header = ("T23/T24 solved geometry, 360deg revolve of the %.1fdeg wedge; "
              "axial %.3f m, r_duct %.4f, r_body %.4f; nseg %d"
              % (c["WEDGE_TOTAL_DEG"], c["Z3"] - c["Z0"], c["R_DUCT"],
                 c["R_O"], a.nseg))
    n, ranges = write_binary_stl(out, parts, header)

    manifest = {
        "surface": os.path.basename(out),
        "generated_by": os.path.abspath(__file__),
        "constants_from": BUILD_T23,
        "solved_cases": 16,
        "case_families": ["T23 (4 points)", "T24 (12 points)"],
        "axis_convention": ("axial = +%s; origin at the housing leading edge"
                            % a.axis),
        "n_facets": int(n),
        "revolve_segments_DISPLAY_CHOICE": int(a.nseg),
        "solved_azimuthal_discretisation": ("one cell over a %.1f-degree wedge; "
                                            "the solve is axisymmetric"
                                            % c["WEDGE_TOTAL_DEG"]),
        "facet_attribute_meaning": "the 2-byte STL attribute is the part index "
                                   "into `part_order`",
        "part_order": [k for k, _ in parts],
        "parts": ranges,
        "geometry_m": {
            "duct_inner_radius": c["R_DUCT"],
            "centrebody_outer_radius": c["R_O"],
            "housing_inner_radius": c["R_I"],
            "housing_wall_thickness": c["WALL_T"],
            "shaft_bore_radius_INTERNAL_not_drawn": c["R_BORE"],
            "axial_stations_Z0_Z3": [c["Z0"], c["Z1"], c["Z2"], c["Z3"]],
            "axial_extent": c["Z3"] - c["Z0"],
            "heated_section_length": c["L_HOUS"],
        },
        "declared_display_choices": [
            "360-degree revolve of an axisymmetric 5-degree wedge solve; the "
            "axisymmetry must be stated wherever this surface is shown",
            "azimuthal revolve resolution (%d segments) is a display choice and "
            "is not the solved azimuthal discretisation" % a.nseg,
            "the flat discs at z = %.3f and z = %.3f are the DOMAIN TRUNCATION "
            "PLANES at inlet and outlet, drawn only so the centrebody is a "
            "closed solid; they are not physical faces"
            % (c["Z0"], c["Z3"]),
        ],
        "declared_omissions": [
            "no nose and no tail: build_t23.py lines 12-18 REMOVE the nose and "
            "tail cones of the owner's directive 3.2 and declare the "
            "centrebody a constant-radius tube over the whole axial extent. "
            "Drawing them would show geometry that was never solved.",
            "no struts: the retired surface carried three radial struts (96 "
            "facets, 0/120/240 degrees) that were never solved and that are "
            "inconsistent with an axisymmetric solve",
            "the %.3f m shaft bore is an internal boundary of the core region "
            "over z = %.3f..%.3f only; it is not visible on a closed external "
            "surface and appears in the cross-section mesh view instead"
            % (c["R_BORE"], c["Z1"], c["Z2"]),
            "the duct wall has ZERO THICKNESS because the solved duct wall is a "
            "boundary condition with no thickness; the retired surface's 5 mm "
            "duct wall was a declared display invention",
        ],
        "retires": {
            "path": "cases/demo-surfaces/motor_in_duct.stl",
            "sha256": "131aab8e17242415364d2f1147a76cfbdc7fe5f48287a0996c2318249857db5f",
            "reason": "dimensioned from F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md, "
                      "a different case; 0.200 m axial against the solved 0.750 m; "
                      "three unsolved struts; nose and tail the solve does not have",
        },
    }
    with open(man, "w") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    print("wrote %s  (%d facets)" % (out, n))
    print("wrote %s" % man)
    for k, (lo, hi) in ranges.items():
        print("    %-24s facets [%5d, %5d)" % (k, lo, hi))
    print()
    m = check_surface(out, c, man, axis=a.axis)
    print("GEOMETRY GUARD: PASS")
    print("  sha256 %s" % m["sha256"])
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
