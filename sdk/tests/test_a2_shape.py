"""The A2 shape replay must stay a replay, at true scale, on a fixed camera.

These guard the ways the viewport payload could quietly stop telling the
truth: a field value landing on the wrong triangle, iteration 0 drifting off
the baseline it is supposed to reproduce exactly, a colour window that
rescales per frame, a display that amplifies a shape, or a camera hint that
mirrors a body or changes what every other act already renders.

SCOPE NOTE, so nobody reads more into a green run than is there. These
exercise the workflow and the payloads it writes, in process. They do NOT
exercise the control room's JavaScript, and they are not a substitute for
``scripts/verify_warm_replay.sh``. That script drives the running server,
which caches workflow modules in ``sys.modules`` for the life of the process:
an IDENTICAL result from it only covers the code the server had loaded when
it started. After any change to this act it must be re-run following a server
restart before its result means anything about the new code.
"""
import json
import math

import pytest

from workflows import _a2_shape

doc = _a2_shape.load()
pytestmark = pytest.mark.skipif(doc is None,
                                reason="A2_shape_frames.json not on this host")
# NOT `_LADDER.parents[3]`, AND THE REASON IS A DEFECT CLASS RATHER THAN A
# TYPO. This was `_a2_shape._LADDER.parents[3] / "sdk"` -- a repository root
# derived by counting segments UP from a path constant. `_LADDER` is
# `lab_paths.DAFOAM / "ladder-a"`, and MOVE_MAP batch 6 (R22) moved `DAFOAM`
# from `demo-output/website/dafoam` to `cases/dafoam`, which is TWO SEGMENTS
# SHALLOWER: `parents[3]` went from the repository root to its parent
# directory, and `_SDK` began pointing at `/home/ubuntu/sdk`, which does not
# exist. A path literal is visible to a prefix rewrite; a DEPTH ASSUMPTION
# about a moving path is not, and no grep for the old prefix would have found
# this line.
#
# What it cost is the more interesting half.
# `test_control_room_keeps_the_old_defaults_verbatim` failed loudly on the
# missing file, but `test_hint_free_payloads_are_untouched_by_the_hint` glob-ed
# an absent directory, got nothing, and went on asserting its projection
# identity over the ten SYNTHETIC bodies it builds itself -- a green comparison
# of no real geometry at all. The only thing that caught it was that test's own
# `assert len(bodies) > 20` floor, which read 10. That floor is why this is a
# finding and not a silent pass, and it is left exactly as it is.
_SDK = _a2_shape.lab_paths.SDK


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
    # baseline + gradient + a whole-wing and a close-up copy of each frame
    assert len(names) == 2 * len(doc["frames"]) + 2

    windows = set()
    for key, name in names.items():
        payload = json.loads((tmp_path / name).read_text())
        n_verts, n_faces = len(payload["vertices"]), len(payload["faces"])
        assert max(max(f) for f in payload["faces"]) < n_verts
        if not key.startswith("near"):
            assert n_faces == 2 * doc["n_quad_faces"]
        field = payload.get("field")
        if key == "baseline":
            assert field is None
            continue
        # One value per DRAWN triangle, in both passes: the artifact stores one
        # per solver quad, and each quad's pair of triangles must carry its own
        # face's value.
        assert len(field["values"]) == n_faces
        assert all(0.0 <= v <= 1.0 for v in field["values"])
        if key != "gradient":
            windows.add((field["color_min"], field["color_max"]))

    # One fixed, zero-centred window across every frame of BOTH passes. A
    # per-frame rescale would make a wing that has barely moved look finished;
    # a differing window would make the close-up incomparable to the wide shot.
    assert len(windows) == 1
    lo, hi = windows.pop()
    assert lo == -hi


def test_true_scale_is_the_only_scale(tmp_path):
    """No surface this module writes is amplified, anywhere, by anything."""
    final = doc["frames"][-1]
    verts = _a2_shape.frame_vertices(doc, final)
    worst = max(max(abs(a - b) for a, b in zip(v, w))
                for v, w in zip(verts, doc["base_vertices"]))
    assert worst * 1000.0 <= final["max_disp_mm"] + 1e-3
    assert doc["_no_exaggeration"].startswith("Every coordinate")

    # Every vertex written for the close-up is a vertex of the true-scale
    # surface, unchanged: that beat is a zoom, not a stretch.
    names = _a2_shape.write_surfaces(doc, tmp_path)
    near = json.loads((tmp_path / names["near47"]).read_text())
    exact = {tuple(v) for v in verts}
    assert all(tuple(v) in exact for v in near["vertices"])


def test_closeup_camera_is_a_proper_rotation_and_is_pinned(tmp_path):
    """The hint may turn the body to face the camera. It may never mirror it."""
    axes = _a2_shape.CLOSEUP_VIEW["axes"]
    assert sorted(axes) == [0, 1, 2]
    basis = [[1 if axes[r] == c else 0 for c in range(3)] for r in range(3)]
    det = sum(basis[0][i] * (basis[1][(i + 1) % 3] * basis[2][(i + 2) % 3]
                             - basis[1][(i + 2) % 3] * basis[2][(i + 1) % 3])
              for i in range(3))
    assert det == 1, "an odd permutation would mirror the wing"
    # Pinned, not inferred: this wing's ~12% thickness ratio sits on the
    # viewport's own 0.12 planform threshold, so an inferred camera flips
    # partway through the morph as the section thickens.
    assert isinstance(_a2_shape.CLOSEUP_VIEW["flat"], bool)

    names = _a2_shape.write_surfaces(doc, tmp_path)
    for key, name in names.items():
        payload = json.loads((tmp_path / name).read_text())
        if key.startswith("near"):
            assert payload["view"] == _a2_shape.CLOSEUP_VIEW
        else:
            # The whole-wing pass opts out, so it renders on exactly the path
            # it rendered on before the hint existed.
            assert "view" not in payload


# --------------------------------------------------------------------------
# The camera hint must be ADDITIVE. What follows is a port of the two decision
# points the hint touches in control_room.html's drawGeometry, so a payload
# WITHOUT a hint can be shown to project to identical numbers either way.
_EVEN = {"0,1,2", "1,2,0", "2,0,1"}


def _project(verts, view, use_hint):
    if use_hint and view and isinstance(view.get("axes"), list) \
            and len(view["axes"]) == 3 \
            and ",".join(map(str, view["axes"])) in _EVEN:
        p = view["axes"]
        verts = [[v[p[0]], v[p[1]], v[p[2]]] for v in verts]
    lo = [min(v[i] for v in verts) for i in range(3)]
    hi = [max(v[i] for v in verts) for i in range(3)]
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    span = max(hi[i] - lo[i] for i in range(3)) or 1
    if use_hint and view and isinstance(view.get("flat"), bool):
        flat = view["flat"]
    else:
        flat = (hi[2] - lo[2]) < 0.12 * span
    cos_a, sin_a = math.cos(0.42), math.sin(0.42)
    out = []
    for v in verts:
        x, y, z = v[1] - c[1], v[2] - c[2], v[0] - c[0]
        if flat:
            t = y
            y = -z * 0.85 + t * 0.4
            z = t * 0.85 + z * 0.4
        zr = z * cos_a - x * sin_a
        out.append((z * sin_a + x * cos_a, y * 0.92 - zr * 0.28, zr))
    return out, flat


def test_hint_free_payloads_are_untouched_by_the_hint():
    """Every body the other acts draw must project to identical numbers."""
    from chief_engineer.geometry import (cylinder_surface, load_surface,
                                         valve_surface, wing_surface)

    bodies = []
    for path in sorted((_SDK / "geometry").glob("*")):
        if path.suffix.lower() in (".stl", ".obj"):
            bodies.append(load_surface(path)["vertices"])
    for span in (28, 40, 52):
        for area in (220, 380):
            bodies.append(wing_surface(span, area, sweep_deg=27.5)["vertices"])
    for angle in (0, 45, 87.5):
        bodies.append(valve_surface(angle)["vertices"])
    bodies.append(cylinder_surface(1.0)["vertices"])
    assert len(bodies) > 20

    for verts in bodies:
        assert _project(verts, None, False) == _project(verts, None, True)


def test_control_room_keeps_the_old_defaults_verbatim():
    """The fallbacks must stay literally what they were before the hint."""
    source = (_SDK / "chief_engineer" / "control_room.html").read_text(
        encoding="utf-8")
    assert ": (hi[2]-lo[2]) < 0.12 * span;" in source
    assert ("const verts = perm ? m.verts.map(v => "
            "[v[perm[0]], v[perm[1]], v[perm[2]]]) : m.verts;") in source
    assert "const EVEN_AXES = { '0,1,2': 1, '1,2,0': 1, '2,0,1': 1 };" in source


def test_closeup_camera_never_snaps_mid_morph(tmp_path):
    """One camera from the first frame to the last, whatever the shape does."""
    names = _a2_shape.write_surfaces(doc, tmp_path)
    seen = set()
    for frame in doc["frames"]:
        payload = json.loads(
            (tmp_path / names[f"near{frame['iter']}"]).read_text())
        seen.add(_project(payload["vertices"], payload["view"], True)[1])
    assert seen == {_a2_shape.CLOSEUP_VIEW["flat"]}


def test_sections_cut_the_real_surface():
    """A plane cut must return closed-ish outlines, not a handful of strays."""
    verts = [list(v) for v in doc["base_vertices"]]
    for z in _a2_shape.SECTION_Z:
        segs = _a2_shape.slice_at(doc, verts, z)
        assert len(segs) > 40, (z, len(segs))
