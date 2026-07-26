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

import json
import math
import unittest

from chief_engineer.field_render import _attach_field, _package_painted
from chief_engineer.geometry import _package


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
        # 20 and 30, normalised to 0 and 1. Any change to this JSON changes
        # the frozen rendering of every non-decimated body.
        golden = {
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
        vertices = golden["vertices"]
        faces = [[0, 1, 2], [1, 3, 2]]
        point_pressure = [10.0, 20.0, 30.0, 40.0]
        face_values = [sum(point_pressure[i] for i in f) / 3.0 for f in faces]
        payload, display_values = _package_painted(
            vertices, faces, face_values, 30000, "surface")
        _attach_field(payload, display_values, "p")
        self.assertEqual(json.dumps(payload, sort_keys=True),
                         json.dumps(golden, sort_keys=True))

    def test_percentile_normalisation_unchanged(self):
        # The 2/98 percentile clip and 4-decimal rounding, hand-computed.
        payload = {"faces": [[0, 1, 2]] * 4}
        _attach_field(payload, [10.0, 20.0, 30.0, 40.0], "p")
        self.assertEqual(payload["field"]["values"], [0.0, 0.3333, 0.6667, 1.0])
        self.assertEqual(payload["field"]["min"], 10.0)
        self.assertEqual(payload["field"]["max"], 40.0)


if __name__ == "__main__":
    unittest.main()
