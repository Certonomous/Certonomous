"""The A2 shape replay must stay a replay, and stay at true scale.

These guard the three ways the viewport payload could quietly stop telling the
truth: a field value landing on the wrong triangle, iteration 0 drifting off
the baseline it is supposed to reproduce exactly, and a colour window that
rescales per frame (which would make a wing that has barely moved look
finished).
"""
import json

import pytest

from workflows import _a2_shape

doc = _a2_shape.load()
pytestmark = pytest.mark.skipif(doc is None,
                                reason="A2_shape_frames.json not on this host")


def test_artifact_declares_its_own_checks():
    checks = doc["_checks"]
    assert checks["major_iterations_unmatched"] == 0
    assert checks["major_iterations_matched"] == len(doc["frames"]) == 48
    # The FFD map has to be linear in the shape variables for the gradient to
    # be pushed onto the skin exactly rather than approximately.
    assert checks["ffd_shape_map_linearity_residual"] < 1e-9


def test_first_frame_reproduces_the_baseline():
    """Iteration 0 is the undeformed wing. If it is not, this is not a replay."""
    assert _a2_shape.frame_vertices(doc, doc["frames"][0]) == \
        [list(v) for v in doc["base_vertices"]]
    assert doc["frames"][0]["max_disp_mm"] == 0.0


def test_every_payload_is_well_formed(tmp_path):
    names = _a2_shape.write_surfaces(doc, tmp_path)
    assert len(names) == len(doc["frames"]) + 2      # baseline + gradient

    windows = set()
    for key, name in names.items():
        payload = json.loads((tmp_path / name).read_text())
        n_verts, n_faces = len(payload["vertices"]), len(payload["faces"])
        assert n_faces == 2 * doc["n_quad_faces"]
        assert max(max(f) for f in payload["faces"]) < n_verts
        field = payload.get("field")
        if key == "baseline":
            assert field is None
            continue
        # One value per DRAWN triangle: the artifact stores one per solver
        # quad, and each quad's pair of triangles must carry its own value.
        assert len(field["values"]) == n_faces
        assert all(0.0 <= v <= 1.0 for v in field["values"])
        if key != "gradient":
            windows.add((field["color_min"], field["color_max"]))

    # One fixed, zero-centred window across every frame of the morph.
    assert len(windows) == 1
    lo, hi = windows.pop()
    assert lo == -hi


def test_nothing_is_exaggerated():
    """The frames are the recorded surfaces, not amplified copies of them."""
    final = doc["frames"][-1]
    verts = _a2_shape.frame_vertices(doc, final)
    worst = max(max(abs(a - b) for a, b in zip(v, w))
                for v, w in zip(verts, doc["base_vertices"]))
    # Consistent with the displacement the artifact reports, to rounding.
    assert worst * 1000.0 <= final["max_disp_mm"] + 1e-3
    assert doc["_no_exaggeration"].startswith("Every coordinate")


def test_sections_cut_the_real_surface():
    """A plane cut must return closed-ish outlines, not a handful of strays."""
    verts = [list(v) for v in doc["base_vertices"]]
    for z in _a2_shape.SECTION_Z:
        segs = _a2_shape.slice_at(doc, verts, z)
        assert len(segs) > 40, (z, len(segs))
