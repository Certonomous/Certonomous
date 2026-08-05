"""The mid-span pressure-field slice (field_render + geometry_study wiring).

Pure-function coverage for the volume-slice extraction on synthetic tetra/hex
clouds with a known field, a register check on every string the figure places
on camera, and the report-payload wiring that lands the plot clickable in the
lab report next to the coefficient plots. Nothing here needs OpenFOAM or WSL;
the .vtu fixtures are written byte-for-byte in the same inline-base64 binary
format foamToVTK produces.
"""
from __future__ import annotations

import base64
import re
import struct
import tempfile
import unittest
from pathlib import Path

import numpy as np

from chief_engineer.field_render import (SLICE_GRID_SHAPE,
                                         SLICE_HALF_THICKNESS_FRACTION,
                                         SLICE_TITLE, cell_centres,
                                         load_surface_mesh, pick_slice,
                                         read_volume_field,
                                         render_pressure_slice,
                                         render_slice_figure,
                                         surface_cross_section)
from workflows import geometry_study as gs

SDK = Path(__file__).resolve().parents[1]

# The same register the acts hold on camera: no em dash, no arrow, none of
# the retired vocabulary, on any string the figure renders.
_BANNED = re.compile(
    r"\u2014|\u2192|\b(demo|stored|saved|cached|recorded|pre-computed|"
    r"real solves?)\b", re.IGNORECASE)


# --------------------------------------------------------------------------
# Synthetic fixtures
# --------------------------------------------------------------------------

def _hex_grid(nx: int, ny: int, nz: int, d: float = 1.0):
    """A structured hex cloud with a known per-cell field (the x centre)."""
    def pid(i, j, k):
        return (i * (ny + 1) + j) * (nz + 1) + k

    points: list[float] = []
    for i in range(nx + 1):
        for j in range(ny + 1):
            for k in range(nz + 1):
                points += [i * d, j * d, k * d]
    conn: list[int] = []
    offsets: list[int] = []
    values: list[float] = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                conn += [pid(i, j, k), pid(i + 1, j, k),
                         pid(i + 1, j + 1, k), pid(i, j + 1, k),
                         pid(i, j, k + 1), pid(i + 1, j, k + 1),
                         pid(i + 1, j + 1, k + 1), pid(i, j + 1, k + 1)]
                offsets.append(len(conn))
                values.append((i + 0.5) * d)
    return points, conn, offsets, values


def _binary_array(name: str, vtk_type: str, flat, ncomp: int | None = None) -> str:
    """One inline-base64 DataArray in foamToVTK's UInt64-header wire format."""
    fmt = {"Float32": "f", "Int32": "i", "UInt8": "B"}[vtk_type]
    payload = struct.pack(f"<{len(flat)}{fmt}", *flat)
    encoded = base64.b64encode(struct.pack("<Q", len(payload)) + payload).decode()
    extra = f" NumberOfComponents='{ncomp}'" if ncomp else ""
    return (f"<DataArray type='{vtk_type}' Name='{name}'{extra} "
            f"format='binary'>{encoded}</DataArray>")


def _write_vtu(path: Path, points, conn, offsets, values) -> None:
    cells = len(offsets)
    body = (
        "<?xml version='1.0'?>\n"
        "<VTKFile type='UnstructuredGrid' version='0.1' "
        "byte_order='LittleEndian' header_type='UInt64'>\n"
        "<UnstructuredGrid>\n"
        f"<Piece NumberOfPoints='{len(points) // 3}' NumberOfCells='{cells}'>\n"
        "<Points>\n" + _binary_array("Points", "Float32", points, ncomp=3)
        + "\n</Points>\n<Cells>\n"
        + _binary_array("connectivity", "Int32", conn) + "\n"
        + _binary_array("offsets", "Int32", offsets) + "\n"
        + _binary_array("types", "UInt8", [12] * cells)
        + "\n</Cells>\n<CellData>\n"
        + _binary_array("p", "Float32", values)
        + "\n</CellData>\n</Piece>\n</UnstructuredGrid>\n</VTKFile>\n")
    path.write_text(body, encoding="ascii")


def _box_mesh(lo, hi):
    """A closed axis-aligned box as (vertices (8,3), triangles (12,3))."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    verts = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                      [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]],
                     dtype=float)
    quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (2, 3, 7, 6), (1, 2, 6, 5), (3, 0, 4, 7)]
    faces = []
    for a, b, c, d in quads:
        faces.append([a, b, c])
        faces.append([a, c, d])
    return verts, np.array(faces)


def _write_cube_stl(path: Path, lo=(0, 0, 0), hi=(1, 1, 1)) -> None:
    verts, faces = _box_mesh(lo, hi)
    lines = ["solid cube"]
    for tri in faces:
        lines.append(" facet normal 0 0 0")
        lines.append("  outer loop")
        for index in tri:
            x, y, z = verts[index]
            lines.append(f"   vertex {x} {y} {z}")
        lines.append("  endloop")
        lines.append(" endfacet")
    lines.append("endsolid cube")
    path.write_text("\n".join(lines), encoding="ascii")


def _shoelace(loop) -> float:
    loop = np.asarray(loop)
    x, y = loop[:, 0], loop[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


# --------------------------------------------------------------------------
# Cell geometry from raw arrays
# --------------------------------------------------------------------------

class CellCentreTests(unittest.TestCase):
    def test_hex_grid_centres_and_extents_are_exact(self):
        points, conn, offsets, _ = _hex_grid(3, 2, 2, d=0.5)
        centres, extents = cell_centres(
            np.asarray(points).reshape(-1, 3), conn, offsets)
        self.assertEqual(len(centres), 3 * 2 * 2)
        # First cell spans (0..0.5)^3: centre at 0.25 each way, extent 0.5.
        np.testing.assert_allclose(centres[0], [0.25, 0.25, 0.25])
        np.testing.assert_allclose(extents, 0.5)
        # Last cell of the x row: centre x = (2 + 0.5) * 0.5.
        np.testing.assert_allclose(centres[-1], [1.25, 0.75, 0.75])

    def test_tetra_cell_is_handled_by_the_same_path(self):
        # A single tetra appended after one hex: mixed cloud, mixed arity.
        points, conn, offsets, _ = _hex_grid(1, 1, 1, d=1.0)
        base = len(points) // 3
        points = points + [3.0, 0.0, 0.0, 4.0, 0.0, 0.0,
                           3.0, 1.0, 0.0, 3.0, 0.0, 1.0]
        conn = conn + [base, base + 1, base + 2, base + 3]
        offsets = offsets + [offsets[-1] + 4]
        centres, extents = cell_centres(
            np.asarray(points).reshape(-1, 3), conn, offsets)
        self.assertEqual(len(centres), 2)
        np.testing.assert_allclose(centres[1], [3.25, 0.25, 0.25])
        np.testing.assert_allclose(extents[1], 1.0)

    def test_empty_arrays_do_not_blow_up(self):
        centres, extents = cell_centres(np.zeros((0, 3)), [], [])
        self.assertEqual(len(centres), 0)
        self.assertEqual(len(extents), 0)


# --------------------------------------------------------------------------
# Slab selection: one cell layer, coarse far field included, widening
# --------------------------------------------------------------------------

class PickSliceTests(unittest.TestCase):
    def test_plane_picks_exactly_one_layer_of_a_fine_grid(self):
        points, conn, offsets, values = _hex_grid(4, 3, 5, d=0.1)
        centres, extents = cell_centres(
            np.asarray(points).reshape(-1, 3), conn, offsets)
        keep, used = pick_slice(centres, extents, axis=2, station=0.24,
                                half_thickness=0.01, min_cells=1)
        # The z = 0.24 plane crosses the k = 2 layer only: 4 * 3 cells.
        self.assertEqual(keep.size, 12)
        np.testing.assert_allclose(centres[keep, 2], 0.25)
        self.assertEqual(used, 0.0)
        # The known field survives selection untouched.
        picked = np.asarray(values, dtype=float)[keep]
        np.testing.assert_allclose(sorted(set(picked.tolist())),
                                   [0.05, 0.15, 0.25, 0.35])

    def test_fine_layers_never_stack_but_coarse_cells_still_reach(self):
        # Two stacked fine layers and one big far-field cell, by hand: the
        # station plane sits in the first fine layer; the second fine layer
        # must stay out (stacked layers checkerboard the triangulation) and
        # the coarse cell must come in because the plane crosses its volume.
        centres = np.array([[0.0, 0.0, 0.005], [0.1, 0.0, 0.005],
                            [0.0, 0.0, 0.015], [0.1, 0.0, 0.015],
                            [0.5, 0.0, 0.045]])
        extents = np.array([[0.01] * 3, [0.01] * 3, [0.01] * 3, [0.01] * 3,
                            [0.1, 0.1, 0.1]])
        keep, used = pick_slice(centres, extents, axis=2, station=0.004,
                                half_thickness=0.05, min_cells=1)
        self.assertEqual(sorted(keep.tolist()), [0, 1, 4])
        self.assertEqual(used, 0.0)

    def test_starved_cut_widens_instead_of_returning_nothing(self):
        # A coarse held case whose cells all sit away from the station: the
        # slab doubles until it reaches them, so an older case still yields
        # a picture rather than silently nothing.
        points, conn, offsets, _ = _hex_grid(2, 2, 2, d=0.1)
        centres, extents = cell_centres(
            np.asarray(points).reshape(-1, 3), conn, offsets)
        keep, used = pick_slice(centres, extents, axis=2, station=0.5,
                                half_thickness=0.1, min_cells=1)
        self.assertGreater(keep.size, 0)
        self.assertGreater(used, 0.0)

    def test_nominal_slab_is_two_percent_of_span(self):
        self.assertEqual(SLICE_HALF_THICKNESS_FRACTION, 0.01)


# --------------------------------------------------------------------------
# Exact silhouette: the body surface cut by the slice plane
# --------------------------------------------------------------------------

class SurfaceCrossSectionTests(unittest.TestCase):
    def test_cube_section_is_one_closed_unit_square(self):
        verts, faces = _box_mesh((0, 0, 0), (1, 1, 1))
        loops = surface_cross_section(verts, faces, axis=2, station=0.4,
                                      plane_axes=(0, 1))
        self.assertEqual(len(loops), 1)
        loop = loops[0]
        # Eight crossing triangles chain into one closed ring whose area and
        # bounds are the exact unit square, whatever the point count.
        self.assertGreaterEqual(len(loop), 4)
        self.assertAlmostEqual(_shoelace(loop), 1.0, places=9)
        np.testing.assert_allclose(loop.min(axis=0), [0.0, 0.0], atol=1e-9)
        np.testing.assert_allclose(loop.max(axis=0), [1.0, 1.0], atol=1e-9)

    def test_two_bodies_give_two_loops(self):
        va, fa = _box_mesh((0, 0, 0), (1, 1, 1))
        vb, fb = _box_mesh((3, 0, 0), (4, 2, 1))
        verts = np.vstack([va, vb])
        faces = np.vstack([fa, fb + len(va)])
        loops = surface_cross_section(verts, faces, axis=2, station=0.5,
                                      plane_axes=(0, 1))
        self.assertEqual(len(loops), 2)
        areas = sorted(_shoelace(loop) for loop in loops)
        self.assertAlmostEqual(areas[0], 1.0, places=9)
        self.assertAlmostEqual(areas[1], 2.0, places=9)

    def test_plane_missing_the_body_gives_no_loops(self):
        verts, faces = _box_mesh((0, 0, 0), (1, 1, 1))
        self.assertEqual(surface_cross_section(verts, faces, axis=2,
                                               station=5.0,
                                               plane_axes=(0, 1)), [])

    def test_synthetic_stl_round_trip_with_case_scale(self):
        # The loader applies the case build's uniform scale, so the section
        # lands in solved-case coordinates (the B-52 path).
        with tempfile.TemporaryDirectory() as tmp:
            stl = Path(tmp) / "cube.stl"
            _write_cube_stl(stl)
            mesh = load_surface_mesh(stl, scale=2.0)
        self.assertIsNotNone(mesh)
        verts, faces = mesh
        self.assertEqual(len(faces), 12)
        loops = surface_cross_section(verts, faces, axis=2, station=1.0,
                                      plane_axes=(0, 1))
        self.assertEqual(len(loops), 1)
        self.assertAlmostEqual(_shoelace(loops[0]), 4.0, places=9)


# --------------------------------------------------------------------------
# The .vtu reader on a synthetic file in foamToVTK's own wire format
# --------------------------------------------------------------------------

class ReadVolumeTests(unittest.TestCase):
    def test_round_trip_through_the_inline_base64_format(self):
        points, conn, offsets, values = _hex_grid(2, 1, 1, d=1.0)
        with tempfile.TemporaryDirectory() as tmp:
            vtu = Path(tmp) / "internal.vtu"
            _write_vtu(vtu, points, conn, offsets, values)
            volume = read_volume_field(vtu, "p")
        self.assertIsNotNone(volume)
        got_points, got_conn, got_offsets, got_values = volume
        np.testing.assert_allclose(
            got_points, np.asarray(points).reshape(-1, 3))
        np.testing.assert_array_equal(got_conn, conn)
        np.testing.assert_array_equal(got_offsets, offsets)
        np.testing.assert_allclose(got_values, values)

    def test_missing_field_returns_none(self):
        points, conn, offsets, values = _hex_grid(1, 1, 1)
        with tempfile.TemporaryDirectory() as tmp:
            vtu = Path(tmp) / "internal.vtu"
            _write_vtu(vtu, points, conn, offsets, values)
            self.assertIsNone(read_volume_field(vtu, "does_not_exist"))


# --------------------------------------------------------------------------
# Rendering: the figure lands, and every string on it holds the register
# --------------------------------------------------------------------------

class RenderTests(unittest.TestCase):
    def _figure_strings(self, meta):
        return [meta["title"], meta["xlabel"], meta["ylabel"],
                meta["colorbar"], meta["note"], meta["annotation"]]

    def test_end_to_end_from_synthetic_volume_file(self):
        points, conn, offsets, values = _hex_grid(6, 1, 6, d=0.1)
        with tempfile.TemporaryDirectory() as tmp:
            vtu = Path(tmp) / "internal.vtu"
            _write_vtu(vtu, points, conn, offsets, values)
            out = Path(tmp) / "slice.png"
            meta = render_pressure_slice(vtu, out, span_axis=1,
                                         plane_axes=(0, 2),
                                         body_label="synthetic block")
            self.assertIsNotNone(meta)
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 10_000)
        # The annotated key value is the true field maximum: x centre 0.55.
        self.assertAlmostEqual(meta["stagnation"], 0.55, places=5)
        self.assertTrue(meta["title"].startswith(SLICE_TITLE))
        # Smoothness proxy: the field was resampled onto the fine regular
        # grid and shaded continuously, not contoured on raw slice cells.
        self.assertEqual(meta["renderer"], "smooth-grid")
        self.assertEqual(meta["grid_shape"], SLICE_GRID_SHAPE)

    def test_exact_silhouette_rides_the_render_when_a_surface_is_given(self):
        points, conn, offsets, values = _hex_grid(6, 1, 6, d=0.1)
        surface = _box_mesh((0.2, -1.0, 0.2), (0.4, 1.0, 0.4))
        with tempfile.TemporaryDirectory() as tmp:
            vtu = Path(tmp) / "internal.vtu"
            _write_vtu(vtu, points, conn, offsets, values)
            out = Path(tmp) / "slice.png"
            meta = render_pressure_slice(vtu, out, span_axis=1,
                                         plane_axes=(0, 2),
                                         body_label="synthetic block",
                                         surface_mesh=surface)
            self.assertIsNotNone(meta)
            self.assertTrue(out.exists())
        # The silhouette came from the surface mesh cut, not the volume.
        self.assertEqual(meta["silhouette_loops"], 1)

    def test_every_figure_string_holds_the_register(self):
        rng = np.random.default_rng(7)
        u = rng.uniform(0, 1, 300)
        v = rng.uniform(0, 1, 300)
        values = u - 0.5
        footprint = np.full(300, 0.12)
        with tempfile.TemporaryDirectory() as tmp:
            meta = render_slice_figure(
                u, v, values, footprint, Path(tmp) / "fig.png",
                xlabel="x  [m]", ylabel="z  [m]", body_label="test body",
                station_note="Slice: y = 0.00 m, the cell layer crossing "
                             "the plane.")
        self.assertIsNotNone(meta)
        for text in self._figure_strings(meta):
            hit = _BANNED.search(text)
            self.assertIsNone(hit, f"register break {hit and hit.group(0)!r} "
                                   f"in figure text: {text!r}")
        self.assertIn("m^2/s^2", meta["colorbar"].replace("\\mathrm{m^2/s^2}",
                                                          "m^2/s^2"))

    def test_too_few_points_returns_none_not_a_broken_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            meta = render_slice_figure(
                [0.0], [0.0], [1.0], [0.1], Path(tmp) / "fig.png",
                xlabel="x  [m]", ylabel="z  [m]")
        self.assertIsNone(meta)


# --------------------------------------------------------------------------
# Report payload: the slice plot rides the report manifest like C_d / C_L
# --------------------------------------------------------------------------

class ReportPayloadTests(unittest.TestCase):
    def test_manifest_entry_shape_matches_the_coefficient_plots(self):
        entry = gs.pressure_slice_entry(
            Path("anywhere") / "naca4412_wing_pressure_slice.png")
        self.assertEqual(entry, {
            "title": SLICE_TITLE,
            "file": "naca4412_wing_pressure_slice.png",
            "url": "/api/plot/geometry-study/naca4412_wing_pressure_slice.png",
        })

    def test_solved_run_report_carries_the_slice_plot(self):
        # The fixture solved run in miniature: the act appends the entry to
        # the same report_plots list that becomes report_doc["plots"], so the
        # memo's figure strip shows the slice next to the coefficient plots.
        report_plots = [{"title": "Drag history with envelope",
                         "file": "Cd_envelope.png",
                         "url": "/api/plot/geometry-study/Cd_envelope.png"}]
        entry = gs.pressure_slice_entry("b52_pressure_slice.png")
        report_plots.append(entry)
        report_doc = {"plots": report_plots}
        self.assertIn(entry, report_doc["plots"])
        self.assertEqual(report_doc["plots"][-1]["title"], SLICE_TITLE)

    def test_act_no_longer_draws_the_slice_and_keeps_the_restore_path(self):
        # The mid-span slice was cut from the act on purpose (commit
        # 74ae8976): the flat cut competed with the painted body directly
        # above it for the same attention and read as the weaker picture. The
        # act must state that the omission is deliberate, must not carry the
        # old wiring, and must keep the one-call restore path:
        # `extract_pressure_slice` stays in the field-render module and the
        # volume output is still written.
        source = (SDK / "workflows" / "geometry_study.py").read_text(
            encoding="utf-8")
        self.assertIn("deliberately not drawn", source)
        self.assertIn("extract_pressure_slice", source)
        self.assertNotIn("slice_png", source)
        # Warm replays render from the held case; an absent plot must skip
        # silently, so the act never narrates a missing one: no
        # slice-specific apology string exists.
        self.assertNotIn("no pressure slice", source.lower())

    def test_unfamiliar_and_familiar_paths_carry_the_body_axes(self):
        source = (SDK / "workflows" / "geometry_study.py").read_text(
            encoding="utf-8")
        self.assertIn('"span_axis": geometry["span_axis"]', source)
        self.assertIn('report.update({"streamwise_axis": 0, "span_axis": 1',
                      source)


if __name__ == "__main__":
    unittest.main()
