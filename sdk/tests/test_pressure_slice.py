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

from chief_engineer.field_render import (SLICE_HALF_THICKNESS_FRACTION,
                                         SLICE_TITLE, cell_centres,
                                         pick_slice, read_volume_field,
                                         render_pressure_slice,
                                         render_slice_figure)
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

    def test_act_wiring_announces_and_records_the_slice(self):
        source = (SDK / "workflows" / "geometry_study.py").read_text(
            encoding="utf-8")
        self.assertIn("extract_pressure_slice", source)
        self.assertIn('announce_plot(emit, "geometry-study", slice_png, '
                      'entry["title"])', source)
        self.assertIn("report_plots.append(entry)", source)
        # Warm replays render from the held case; an absent volume output
        # (older caches) must skip silently, so the act never narrates a
        # missing plot: no slice-specific apology string exists.
        self.assertNotIn("no pressure slice", source.lower())

    def test_unfamiliar_and_familiar_paths_carry_the_body_axes(self):
        source = (SDK / "workflows" / "geometry_study.py").read_text(
            encoding="utf-8")
        self.assertIn('"span_axis": geometry["span_axis"]', source)
        self.assertIn('report.update({"streamwise_axis": 0, "span_axis": 1',
                      source)


if __name__ == "__main__":
    unittest.main()
