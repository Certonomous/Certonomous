"""Field-to-display correspondence under decimation (field_render).

The bug these tests pin down: ``_package`` decimates large meshes by vertex
clustering, but the field values used to be sampled by stride — index i of the
source values painted onto display face i, which has no geometric meaning after
clustering. On the NACA 0015 sail (31,748 solved faces -> 13,835 display faces)
the painted body rendered as salt-and-pepper noise.

Two bars, both enforced here:

* decimated bodies: each display face must carry the mean of exactly the
  source faces that merged into it (exact synthetic check);
* non-decimated bodies (motorbike, B-52): the pipeline must stay
  byte-identical — the on-camera look is frozen (golden payload check).
"""

import base64
import json
import math
import struct
import tempfile
import unittest
from pathlib import Path

from chief_engineer.field_render import (_attach_field, _package_painted,
                                         _patch_cell_values, _read_patch,
                                         CP_FIELD_NAME, cp_bound_report,
                                         load_field_surface)
from chief_engineer.geometry import _package


def _b64(fmt: str, data) -> str:
    """One VTK XML binary DataArray body: UInt64 byte-count header + payload."""
    payload = struct.pack(f"<{len(data)}{fmt}", *data)
    return base64.b64encode(struct.pack("<Q", len(payload)) + payload).decode()


def _write_vtp(path, n: int, point_values, cell_values=None) -> None:
    """Write an ``n`` by ``n`` quad sheet as a foamToVTK-dialect .vtp patch.

    Same wire format ``_read_patch`` parses off a real ``foamToVTK
    -surfaceFields`` patch: base64 binary DataArrays with a UInt64 byte-count
    header, quads in Polys (so the reader's fan triangulation runs), and the
    field in PointData (so its per-point to per-face averaging runs too).
    ``cell_values`` adds the CellData array a real patch also carries, one
    value per quad; pass None to emit a file with no CellData at all.
    """
    points = []
    for i in range(n):
        for j in range(n):
            points.extend([i / (n - 1.0), j / (n - 1.0), 0.0])
    connectivity, offsets = [], []
    for i in range(n - 1):
        for j in range(n - 1):
            v = i * n + j
            connectivity.extend([v, v + 1, v + n + 1, v + n])
            offsets.append(len(connectivity))
    n_quads = len(offsets)
    cell_block = ""
    if cell_values is not None:
        cell_block = ("<CellData><DataArray type='Float64' Name='p' "
                      f"format='binary'>{_b64('d', list(cell_values))}"
                      "</DataArray></CellData>\n")
    Path(path).write_text(
        "<?xml version='1.0'?>\n"
        "<VTKFile type='PolyData' version='1.0' byte_order='LittleEndian' "
        "header_type='UInt64'>\n<PolyData>\n"
        f"<Piece NumberOfPoints='{n * n}' NumberOfPolys='{n_quads}'>\n"
        "<Points><DataArray type='Float64' Name='Points' "
        "NumberOfComponents='3' format='binary'>"
        f"{_b64('d', points)}</DataArray></Points>\n"
        "<Polys><DataArray type='Int64' Name='connectivity' format='binary'>"
        f"{_b64('q', connectivity)}</DataArray>"
        "<DataArray type='Int64' Name='offsets' format='binary'>"
        f"{_b64('q', offsets)}</DataArray></Polys>\n"
        "<PointData><DataArray type='Float64' Name='p' format='binary'>"
        f"{_b64('d', list(point_values))}</DataArray></PointData>\n"
        f"{cell_block}"
        "</Piece>\n</PolyData>\n</VTKFile>\n", encoding="utf-8")


def _clustered_fixture():
    """A synthetic mesh whose decimation outcome is known exactly.

    Anchor vertices stretch the bounding box to 56 units so ``_cluster`` at the
    initial resolution of 56 uses a grid cell of exactly 1.0. Every "cluster"
    is a group of near-coincident vertices (jitter well inside one cell) at a
    distinct cell centre, so the source->display vertex merge is fully
    predictable: cluster corners A, B, C, D become one display vertex each.

    Source faces:
      * three triangles over (A, B, C) with values 1, 2, 3  -> display mean 2
      * five triangles over (B, C, D) with values 10..50    -> display mean 30
      * one degenerate triangle entirely inside A, value 999 -> must vanish

    With max_faces=3 the 9 source faces trigger decimation, the resolution
    search breaks on its first iteration (2 display faces is within the
    0.45..1.35 band of 3), and no stride-drop follows.
    """
    centres = {"A": (2.5, 2.5, 0.5), "B": (10.5, 2.5, 0.5),
               "C": (2.5, 10.5, 0.5), "D": (10.5, 10.5, 0.5)}
    vertices = [[0.0, 0.0, 0.0], [56.0, 0.0, 0.0]]  # bbox anchors, unused
    faces, values = [], []

    def tri(corners, value, jitter):
        base = len(vertices)
        for k, corner in enumerate(corners):
            x, y, z = centres[corner]
            vertices.append([x + jitter + 0.003 * k, y + jitter, z])
        faces.append([base, base + 1, base + 2])
        values.append(value)

    for i, value in enumerate((1.0, 2.0, 3.0)):
        tri(("A", "B", "C"), value, jitter=0.01 * i)
    for i, value in enumerate((10.0, 20.0, 30.0, 40.0, 50.0)):
        tri(("B", "C", "D"), value, jitter=0.01 * i)
    tri(("A", "A", "A"), 999.0, jitter=0.02)  # degenerate: collapses to a point
    return vertices, faces, values


class DecimatedAggregationTests(unittest.TestCase):
    def test_display_faces_carry_the_mean_of_their_source_faces(self):
        vertices, faces, values = _clustered_fixture()
        payload, display_values = _package_painted(
            vertices, faces, values, 3, "synthetic")
        self.assertEqual(payload["triangles_total"], 9)
        self.assertEqual(payload["triangles_shown"], 2)
        # Exact aggregation: mean(1,2,3) and mean(10..50); the degenerate
        # 999-valued face collapsed to a point and must not poison either.
        self.assertEqual(display_values, [2.0, 30.0])

    def test_decimated_geometry_is_byte_identical_to_package(self):
        # Drift guard: the value-tracking path mirrors geometry._package's
        # clustering step for step. If the decimation in geometry.py ever
        # changes, this fails loudly instead of silently mis-painting.
        vertices, faces, values = [], [], []
        for i in range(40):
            for j in range(40):
                a, b = i / 39.0, j / 39.0
                vertices.append([a, b, 0.3 * math.sin(5 * a) * math.cos(4 * b)])
        for i in range(39):
            for j in range(39):
                v = i * 40 + j
                faces.append([v, v + 1, v + 41])
                faces.append([v, v + 41, v + 40])
                values.extend([float(v), float(v) + 0.5])
        max_faces = 400
        self.assertGreater(len(faces), max_faces)  # decimation must trigger
        payload, display_values = _package_painted(
            vertices, faces, values, max_faces, "sheet")
        self.assertEqual(payload, _package(vertices, faces, max_faces, "sheet"))
        self.assertEqual(len(display_values), len(payload["faces"]))
        # Values are a smooth ramp over the grid, so every display mean must
        # stay inside the source range — a stride-sampled list would too, but
        # combined with the exact test above this pins the mapping.
        self.assertTrue(all(0.0 <= v <= max(values) for v in display_values))

    def test_decimation_without_values_still_packages(self):
        vertices, faces, _ = _clustered_fixture()
        payload, display_values = _package_painted(vertices, faces, [], 3, "s")
        self.assertEqual(display_values, [])
        self.assertEqual(payload, _package(vertices, faces, 3, "s"))
        _attach_field(payload, display_values, "p")
        self.assertIsNone(payload["field"])


class NonDecimatedFrozenPipelineTests(unittest.TestCase):
    """Bodies under the threshold: the validated on-camera look is frozen."""

    def test_payload_defers_to_package_and_values_pass_through(self):
        vertices = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0],
                    [1.0, 1.0, 0.0]]
        faces = [[0, 1, 2], [1, 3, 2]]
        values = [15.0, 30.0]
        payload, display_values = _package_painted(
            vertices, faces, values, 30000, "surface")
        self.assertEqual(payload, _package(vertices, faces, 30000, "surface"))
        self.assertEqual(display_values, values)

    def test_golden_payload_matches_pre_fix_output(self):
        # Byte-for-byte golden captured from the pre-fix pipeline for a
        # two-triangle body with point pressures (10, 20, 30, 40): face means
        # 20 and 30, normalised to 0 and 1. Any change to a value in this JSON
        # changes the frozen rendering of every non-decimated body.
        #
        # ``quantity`` was added when the pressure/Cp toggle landed. It is a
        # descriptor, not a rendered quantity: nothing that draws reads it,
        # and on the default path it always reads "pressure". The two
        # assertions below keep that honest — the whole payload is pinned,
        # AND every key the renderer actually consumes is pinned separately
        # against the pre-toggle golden, so no future addition can smuggle a
        # changed value in behind a new key.
        drawn = {
            "bounds": {"max": [1.0, 1.0, 0.0], "min": [0.0, 0.0, 0.0]},
            "faces": [[0, 1, 2], [1, 3, 2]],
            "field": {"color_max": 30.0, "color_min": 20.0,
                      "display_max": 30.0, "display_min": 20.0,
                      "max": 30.0, "min": 20.0, "name": "p",
                      "values": [0.0, 1.0]},
            "name": "surface",
            "triangles_shown": 2, "triangles_total": 2,
            "vertices": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                         [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]],
        }
        golden = dict(drawn, field=dict(drawn["field"], quantity="pressure"))
        vertices = drawn["vertices"]
        faces = [[0, 1, 2], [1, 3, 2]]
        point_pressure = [10.0, 20.0, 30.0, 40.0]
        face_values = [sum(point_pressure[i] for i in f) / 3.0 for f in faces]
        payload, display_values = _package_painted(
            vertices, faces, face_values, 30000, "surface")
        _attach_field(payload, display_values, "p")
        self.assertEqual(json.dumps(payload, sort_keys=True),
                         json.dumps(golden, sort_keys=True))
        rendered = dict(payload, field={k: v for k, v in payload["field"].items()
                                        if k != "quantity"})
        self.assertEqual(json.dumps(rendered, sort_keys=True),
                         json.dumps(drawn, sort_keys=True))

    def test_percentile_normalisation_unchanged(self):
        # The 2/98 percentile clip and 4-decimal rounding, hand-computed.
        payload = {"faces": [[0, 1, 2]] * 4}
        _attach_field(payload, [10.0, 20.0, 30.0, 40.0], "p")
        self.assertEqual(payload["field"]["values"], [0.0, 0.3333, 0.6667, 1.0])
        self.assertEqual(payload["field"]["min"], 10.0)
        self.assertEqual(payload["field"]["max"], 40.0)


class ReportedPhysicalRangeRegressionTests(unittest.TestCase):
    """The understated-peak-pressure bug: pinned so it cannot silently return.

    Every published pressure-painted body (NACA 4412 wing, motorbike, B-52)
    reported a Cp_max far below the solver's own value because two stages
    diluted or clipped the peak and then the diluted/clipped number was
    written into the JSON as if it were the field's physical extreme:
    vertex-clustering decimation averages a sharp stagnation peak into its
    cooler neighbours, and the 2nd/98th percentile colour clip drops the
    real extreme outright. The reported ``min``/``max`` must always equal the
    true range of the UNDECIMATED, UNCLIPPED input data, to a tight
    tolerance, regardless of which branch (decimated or not) is taken and
    regardless of what the colour map clips to for display.
    """

    def test_decimated_body_reports_the_undiluted_extreme(self):
        # A large sheet (3,042 faces, well above max_faces=400 so clustering
        # triggers) that is otherwise flat, with a single stagnation-like
        # spike planted on one interior face and a single suction-like spike
        # on another. Each extreme is 1 face in 3,042 (0.03%), so clustering
        # blends both away completely: measured, the decimated display values
        # come back dead flat at 1.0. That is the wing's own failure mode
        # (0.6% of its faces carried the peak) reproduced in miniature, and
        # it means this test genuinely distinguishes a reported range taken
        # from the undecimated source from one taken from the display faces.
        vertices, faces, values = [], [], []
        for i in range(40):
            for j in range(40):
                vertices.append([i / 39.0, j / 39.0, 0.0])
        for i in range(39):
            for j in range(39):
                v = i * 40 + j
                faces.append([v, v + 1, v + 41])
                faces.append([v, v + 41, v + 40])
                values.extend([1.0, 1.0])
        values[0] = 1000.0       # the stagnation-like peak
        values[1000] = -1000.0   # the suction-like peak
        max_faces = 400
        self.assertGreater(len(faces), max_faces)  # decimation must trigger

        payload, display_values = _package_painted(
            vertices, faces, values, max_faces, "sheet")
        # This is exactly what load_field_surface computes: the physical
        # range from the UNDECIMATED per-face list, before clustering ever
        # sees it.
        physical_range = (min(values), max(values))
        _attach_field(payload, display_values, "p", physical_range=physical_range)

        field = payload["field"]
        # The reported physical range must equal the true range of the input
        # data to a tight tolerance. This is the assertion the bug violated.
        self.assertAlmostEqual(field["min"], min(values), places=9)
        self.assertAlmostEqual(field["max"], max(values), places=9)
        self.assertAlmostEqual(field["min"], -1000.0, places=9)
        self.assertAlmostEqual(field["max"], 1000.0, places=9)
        # The decimated display values cannot produce this range on their
        # own: proof the reported range truly bypassed clustering rather
        # than surviving it by coincidence.
        self.assertGreater(min(display_values), -1000.0 + 1.0)
        self.assertLess(max(display_values), 1000.0 - 1.0)
        # The colour range is a distinct, clipped window: never mistakeable
        # for the physical one, and nowhere near the true extremes.
        self.assertLess(field["color_max"], field["max"])
        self.assertGreater(field["color_min"], field["min"])
        self.assertNotEqual(
            (field["color_min"], field["color_max"]),
            (field["min"], field["max"]))

    def test_load_field_surface_reports_the_true_range_of_its_input(self):
        # End to end through the public entry point, on a real .vtp written
        # in the same binary VTK XML dialect foamToVTK emits: the reported
        # min/max must equal the true extremes of the per-face values the
        # reader derived, to a tight tolerance, even though the body is far
        # over max_faces and every stage downstream of the read dilutes or
        # clips them.
        with tempfile.TemporaryDirectory() as tmp:
            vtp = Path(tmp) / "body.vtp"
            n = 40
            point_values = [1.0] * (n * n)
            point_values[0] = 3000.0      # a lone stagnation-like point
            point_values[n * n - 1] = -3000.0
            _write_vtp(vtp, n, point_values)

            _, faces, face_values = _read_patch(vtp, "p")
            self.assertEqual(len(face_values), len(faces))
            true_lo, true_hi = min(face_values), max(face_values)
            self.assertGreater(true_hi, 900.0)   # the peak survived the read
            self.assertLess(true_lo, -900.0)

            payload = load_field_surface(vtp, field="p", max_faces=400,
                                         name="body")
            self.assertGreater(payload["triangles_total"], 400)
            self.assertLess(payload["triangles_shown"],
                            payload["triangles_total"])  # decimation ran
            field = payload["field"]
            self.assertAlmostEqual(field["min"], true_lo, places=9)
            self.assertAlmostEqual(field["max"], true_hi, places=9)
            # And the colour window is still the clipped, display-only one.
            self.assertLess(field["color_max"], field["max"])
            self.assertGreater(field["color_min"], field["min"])

    def test_reported_range_prefers_the_solver_own_wall_cell_values(self):
        # foamToVTK writes the wall field twice: per point (which the display
        # path interpolates to face centres, smooth but lossy at a peak) and
        # per cell (the finite-volume wall values the solver actually wrote).
        # The reported physics must come from the cell array. Measured on the
        # NACA 4412 wing the two disagree by Cp 0.8897 against 0.8503, so
        # reading the wrong one silently understates every published peak.
        with tempfile.TemporaryDirectory() as tmp:
            vtp = Path(tmp) / "body.vtp"
            n = 40
            n_quads = (n - 1) * (n - 1)
            point_values = [1.0] * (n * n)
            cell_values = [1.0] * n_quads
            cell_values[0] = 500.0     # the solver's own peak, one wall face
            cell_values[7] = -500.0
            _write_vtp(vtp, n, point_values, cell_values=cell_values)

            # The nodal path alone cannot see either extreme: it is flat.
            _, faces, nodal = _read_patch(vtp, "p")
            self.assertEqual(min(nodal), 1.0)
            self.assertEqual(max(nodal), 1.0)
            self.assertEqual(_patch_cell_values(vtp, "p"), cell_values)

            payload = load_field_surface(vtp, field="p", max_faces=400,
                                         name="body")
            field = payload["field"]
            self.assertAlmostEqual(field["min"], -500.0, places=9)
            self.assertAlmostEqual(field["max"], 500.0, places=9)

    def test_reported_range_falls_back_to_nodal_without_cell_data(self):
        # A patch file with no CellData at all (an older foamToVTK write):
        # the reported range is still a true, unclipped extreme, taken from
        # the nodal-derived per-face values, never from the colour clip.
        with tempfile.TemporaryDirectory() as tmp:
            vtp = Path(tmp) / "body.vtp"
            n = 40
            point_values = [1.0] * (n * n)
            point_values[0] = 3000.0
            _write_vtp(vtp, n, point_values, cell_values=None)

            self.assertIsNone(_patch_cell_values(vtp, "p"))
            _, faces, nodal = _read_patch(vtp, "p")
            payload = load_field_surface(vtp, field="p", max_faces=400,
                                         name="body")
            field = payload["field"]
            self.assertAlmostEqual(field["min"], min(nodal), places=9)
            self.assertAlmostEqual(field["max"], max(nodal), places=9)
            self.assertGreater(field["max"], 900.0)

    def test_attach_field_falls_back_to_its_own_values_when_undecimated(self):
        # A caller with no separate undecimated source (e.g. a body below
        # the decimation threshold, where face_values already ARE the
        # undecimated per-face data) still gets the true min/max of what it
        # passed, not the percentile-clipped window.
        values = [5.0, -50.0, 7.0, 8.0, 40.0]
        payload = {"faces": [[0, 1, 2]] * len(values)}
        _attach_field(payload, values, "p")
        self.assertEqual(payload["field"]["min"], -50.0)
        self.assertEqual(payload["field"]["max"], 40.0)


class CpStagnationBoundFlagTests(unittest.TestCase):
    """The reported physical range is disclosed, never corrected.

    The motorbike's true wall maximum is Cp 1.119 on a single sliver face in
    the front brake-disc gap. That value is what the solver wrote and it must
    keep being reported, but Cp cannot exceed 1 in incompressible flow, so a
    consumer displaying it unqualified would put a physically impossible
    number on screen. These tests pin the disclosure: the value stays, and a
    flag alongside it says the bound is broken, by how many faces, and what
    the highest admissible value is instead.
    """

    def test_violating_field_is_flagged_without_altering_the_extreme(self):
        q = 200.0
        # 1 face over the bound, 3 in suction-outlier territory, 996 ordinary.
        values = [(-30.0) for _ in range(996)]
        values += [-500.0, -450.0, -410.0]     # Cp -2.50, -2.25, -2.05
        values += [223.855]                    # Cp 1.1193, the sliver face
        values[0] = 198.37                     # Cp 0.9918, the real peak
        report = cp_bound_report(values, q=q)

        self.assertFalse(report["within_stagnation_bound"])
        self.assertEqual(report["faces"], 1000)
        self.assertAlmostEqual(report["max"], 223.855 / q, places=6)
        self.assertEqual(report["over_bound"]["count"], 1)
        self.assertAlmostEqual(report["over_bound"]["fraction"], 0.001, places=9)
        self.assertAlmostEqual(report["over_bound"]["extreme_cp"],
                               223.855 / q, places=6)
        # The consumer's "robust but still physical" option.
        self.assertAlmostEqual(report["over_bound"]["max_cp_within_bound"],
                               198.37 / q, places=6)
        # The low end is an outlier count, NOT a violation: Cp has no hard
        # lower bound, and the report must not imply one.
        self.assertEqual(report["suction_outliers"]["count"], 3)
        self.assertIn("no hard lower bound", report["suction_outliers"]["note"])
        self.assertNotIn("violation", report["suction_outliers"]["note"].lower()
                         .replace("not a bound violation", ""))
        self.assertIn("caveat", report)
        self.assertIn("mesh quality", report["caveat"])

    def test_clean_field_is_flagged_as_within_bound(self):
        # The wing and the B-52: every wall face admissible, so the flag says
        # so, no caveat is emitted, and the suction counter stays empty.
        q = 112.5
        values = [-119.632, 100.0875, 5.0, -40.0]   # Cp -1.063 .. 0.890
        report = cp_bound_report(values, q=q)
        self.assertTrue(report["within_stagnation_bound"])
        self.assertEqual(report["over_bound"]["count"], 0)
        self.assertIsNone(report["over_bound"]["extreme_cp"])
        self.assertAlmostEqual(report["over_bound"]["max_cp_within_bound"],
                               100.0875 / q, places=6)
        self.assertEqual(report["suction_outliers"]["count"], 0)
        self.assertNotIn("caveat", report)
        # Cp -1.063 is perfectly physical and must not be counted anywhere.
        self.assertLess(report["min"], -1.0)

    def test_p_inf_is_subtracted_and_recorded(self):
        # Cross-validation against a number this lab derived by a completely
        # separate route. `validation_numbers.json` records the NACA 4412
        # wing's global_max_cp as 0.8892004618710941, computed by the
        # standalone validation script from its own wall survey. Feeding this
        # function the exact solver wall maximum out of the .vtp CellData
        # (100.08747863769531 m2/s2), the measured p_inf and q reproduces
        # that constant bit for bit, which is what makes the CellData path
        # trustworthy as the source of reported physics.
        wall_max = 100.08747863769531
        p_inf = 0.05242667719721794
        report = cp_bound_report([wall_max], q=112.5, p_inf=p_inf)
        self.assertEqual(report["max"], 0.8892004618710941)
        self.assertEqual(report["p_inf"], p_inf)
        self.assertEqual(report["q_kinematic"], 112.5)
        self.assertTrue(report["within_stagnation_bound"])

    def test_report_is_none_without_a_dynamic_pressure(self):
        # Cp is undefined without q, so the block is absent rather than
        # guessed. No silent q = 1 fallback.
        self.assertIsNone(cp_bound_report([1.0, 2.0], q=None))
        self.assertIsNone(cp_bound_report([1.0, 2.0], q=0.0))
        self.assertIsNone(cp_bound_report([], q=200.0))

    def test_load_field_surface_attaches_and_omits_the_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            vtp = Path(tmp) / "body.vtp"
            n = 40
            n_quads = (n - 1) * (n - 1)
            cell_values = [-30.0] * n_quads
            cell_values[0] = 223.855      # Cp 1.1193 at q 200: over the bound
            cell_values[1] = 198.37       # Cp 0.9918: the real peak
            _write_vtp(vtp, n, [1.0] * (n * n), cell_values=cell_values)

            # Without q: no cp block, and the payload is otherwise unchanged.
            plain = load_field_surface(vtp, field="p", max_faces=400, name="b")
            self.assertNotIn("cp", plain["field"])

            flagged = load_field_surface(vtp, field="p", max_faces=400,
                                         name="b", q_kinematic=200.0)
            cp = flagged["field"]["cp"]
            self.assertFalse(cp["within_stagnation_bound"])
            self.assertEqual(cp["over_bound"]["count"], 1)
            self.assertEqual(cp["faces"], n_quads)
            # The disclosure did not touch the reported physical range.
            self.assertEqual(flagged["field"]["min"], plain["field"]["min"])
            self.assertEqual(flagged["field"]["max"], plain["field"]["max"])
            self.assertAlmostEqual(flagged["field"]["max"], 223.855, places=6)
            # And the flag describes the same population the range came from.
            self.assertAlmostEqual(cp["max"], flagged["field"]["max"] / 200.0,
                                   places=9)


class PressureCoefficientToggleTests(unittest.TestCase):
    """Pressure and Cp are two settings of one switch, not a migration."""

    def _body(self, tmp):
        vtp = Path(tmp) / "body.vtp"
        n = 12
        n_quads = (n - 1) * (n - 1)
        cells = [-30.0] * n_quads
        cells[0] = 150.0
        _write_vtp(vtp, n, [1.0] * (n * n), cell_values=cells)
        return vtp

    def test_pressure_is_the_default_and_says_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = load_field_surface(self._body(tmp), field="p",
                                         max_faces=400, name="b")
            self.assertEqual(payload["field"]["quantity"], "pressure")
            self.assertEqual(payload["field"]["name"], "p")

    def test_cp_is_selectable_and_rescales_every_reported_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            vtp = self._body(tmp)
            q, p_inf = 200.0, 10.0
            pressure = load_field_surface(vtp, field="p", max_faces=400,
                                          name="b", q_kinematic=q,
                                          p_inf=p_inf)
            coefficient = load_field_surface(vtp, field="p", max_faces=400,
                                             name="b", q_kinematic=q,
                                             p_inf=p_inf, as_cp=True)
            self.assertEqual(coefficient["field"]["quantity"], "cp")
            self.assertEqual(coefficient["field"]["name"], CP_FIELD_NAME)
            # The physical extremes are the same measurement in the other unit.
            for key in ("min", "max"):
                self.assertAlmostEqual(coefficient["field"][key],
                                       (pressure["field"][key] - p_inf) / q,
                                       places=12)
            # The picture itself is identical: an affine map cannot move a
            # face's place in the normalised colour range.
            self.assertEqual(coefficient["field"]["values"],
                             pressure["field"]["values"])
            # And the bound check is graded on the pressures either way.
            self.assertEqual(coefficient["field"]["cp"],
                             pressure["field"]["cp"])

    def test_cp_without_a_usable_q_falls_back_to_pressure(self):
        # Not an error and not a warning: Cp is undefined without a positive
        # q, so the pressure is drawn and the payload says which it is. A
        # caller narrating the picture reads that key instead of assuming.
        with tempfile.TemporaryDirectory() as tmp:
            vtp = self._body(tmp)
            for q in (None, 0.0, -5.0):
                payload = load_field_surface(vtp, field="p", max_faces=400,
                                             name="b", q_kinematic=q,
                                             as_cp=True)
                self.assertEqual(payload["field"]["quantity"], "pressure")
                self.assertEqual(payload["field"]["name"], "p")
                self.assertAlmostEqual(payload["field"]["max"], 150.0,
                                       places=6)

    def test_the_camera_hint_is_carried_only_when_given(self):
        with tempfile.TemporaryDirectory() as tmp:
            vtp = self._body(tmp)
            self.assertNotIn("view", load_field_surface(vtp, field="p",
                                                        max_faces=400,
                                                        name="b"))
            hinted = load_field_surface(vtp, field="p", max_faces=400,
                                        name="b", view={"flat": False})
            self.assertEqual(hinted["view"], {"flat": False})


if __name__ == "__main__":
    unittest.main()
