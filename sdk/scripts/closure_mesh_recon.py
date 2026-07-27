"""Mesh-geometry reconstruction utilities for the closure-challenge benchmark.

Built to fill in fields the benchmark does NOT ship for the DUCT and
NASA_2DWMH test-case families (gradU everywhere; wall distance for DUCT
only -- NASA_2DWMH already ships walldist). Everything here is computed
from the raw OpenFOAM mesh (points/faces/owner/neighbour/boundary) and the
RANS solution fields that ARE shipped (U, plus boundary-condition metadata
read from the same field file). No ground truth (U_LES) is used by any
function in this module.

Algorithms are the standard OpenFOAM primitive-mesh geometry formulas
(face centroid/area by triangle-fan decomposition from an estimated face
centre; cell centroid/volume by pyramidal decomposition from an estimated
cell centre) and a standard Green-Gauss cell-gradient reconstruction with:
  - linear (distance-weighted) interpolation for internal faces,
  - exact boundary values read from the field file for fixedValue patches,
  - vector reflection for symmetry patches,
  - zero for noSlip patches,
  - owner-value (zero-gradient) for zeroGradient/empty patches,
  - one-to-one index correspondence + 50/50 averaging for cyclic patches
    (valid for plain "cyclic" patches, which by construction store faces
    in matched order -- this is NOT used for cyclicAMI).

Geometry correctness is checked, not assumed: reconstruct_cell_centres_vols
is validated against the benchmark's own shipped C/V fields wherever they
exist (see validate_closure_mesh_recon.py), and the Green-Gauss gradient is
validated against the benchmark's own shipped gradU on a periodic-hills
case that ships it.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Raw OpenFOAM ASCII mesh parsing (points / faces / owner / neighbour /
# boundary). Deliberately independent of Ofpp's FoamMesh so we get full
# control of boundary metadata (neighbourPatch for cyclic patches, which
# Ofpp's Boundary namedtuple does not expose).
# ---------------------------------------------------------------------------

def _strip_foam_header(text: str) -> str:
    # Drop C++ style /* ... */ header block and // comments.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//.*", "", text)
    return text


def _parse_list_block(text: str, start_idx: int):
    """Given text and an index right after a count integer, parse the
    following '(' ... ')' list of whitespace-separated tokens per line
    (either plain ints, or '(a b c)' point/face tuples). Returns
    (raw_inner_text, end_idx)."""
    i = text.index("(", start_idx)
    depth = 0
    j = i
    while True:
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return text[i + 1:j], j + 1


def read_points(case_dir: Path) -> np.ndarray:
    text = _strip_foam_header((case_dir / "constant" / "polyMesh" / "points").read_text())
    m = re.search(r"(\d+)\s*\(", text)
    n = int(m.group(1))
    inner, _ = _parse_list_block(text, m.end(1))
    vals = re.findall(r"\(([^()]*)\)", inner)
    pts = np.array([[float(x) for x in v.split()] for v in vals], dtype=np.float64)
    assert pts.shape == (n, 3), f"points parse mismatch: expected {n}, got {pts.shape}"
    return pts


def read_faces(case_dir: Path) -> list[list[int]]:
    text = _strip_foam_header((case_dir / "constant" / "polyMesh" / "faces").read_text())
    m = re.search(r"(\d+)\s*\(", text)
    n = int(m.group(1))
    inner, _ = _parse_list_block(text, m.end(1))
    # Each face is "count(v0 v1 v2 ...)"
    faces = []
    for mm in re.finditer(r"(\d+)\(([^()]*)\)", inner):
        idxs = [int(x) for x in mm.group(2).split()]
        assert len(idxs) == int(mm.group(1))
        faces.append(idxs)
    assert len(faces) == n, f"faces parse mismatch: expected {n}, got {len(faces)}"
    return faces


def read_int_list(path: Path) -> np.ndarray:
    text = _strip_foam_header(path.read_text())
    m = re.search(r"(\d+)\s*\(", text)
    n = int(m.group(1))
    inner, _ = _parse_list_block(text, m.end(1))
    vals = np.array([int(x) for x in inner.split()], dtype=np.int64)
    assert vals.shape[0] == n, f"{path}: expected {n}, got {vals.shape[0]}"
    return vals


def read_owner(case_dir: Path) -> np.ndarray:
    return read_int_list(case_dir / "constant" / "polyMesh" / "owner")


def read_neighbour(case_dir: Path) -> np.ndarray:
    return read_int_list(case_dir / "constant" / "polyMesh" / "neighbour")


def read_boundary(case_dir: Path) -> dict:
    """Returns {patch_name: {"type":..., "nFaces":..., "startFace":...,
    "neighbourPatch": str|None}}"""
    text = _strip_foam_header((case_dir / "constant" / "polyMesh" / "boundary").read_text())
    m = re.search(r"(\d+)\s*\(", text)
    inner, _ = _parse_list_block(text, m.end(1))
    patches = {}
    # Each patch block: name { key value; ... }
    for mm in re.finditer(r"(\w+)\s*\{([^{}]*)\}", inner):
        name = mm.group(1)
        body = mm.group(2)
        d = {}
        for line in body.split(";"):
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                d[parts[0]] = parts[1].strip()
        patches[name] = {
            "type": d.get("type"),
            "nFaces": int(d["nFaces"]),
            "startFace": int(d["startFace"]),
            "neighbourPatch": d.get("neighbourPatch"),
        }
    return patches


class Mesh:
    def __init__(self, case_dir: Path):
        self.case_dir = Path(case_dir)
        self.points = read_points(self.case_dir)
        self.faces = read_faces(self.case_dir)
        self.owner = read_owner(self.case_dir)
        self.neighbour = read_neighbour(self.case_dir)
        self.boundary = read_boundary(self.case_dir)
        self.num_face = len(self.faces)
        self.num_inner_face = self.neighbour.shape[0]
        self.num_cell = int(max(self.owner.max(), self.neighbour.max())) + 1
        self.face_centres, self.face_areas = _face_centres_areas(self.points, self.faces)


def _face_centres_areas(points: np.ndarray, faces: list[list[int]]):
    """Standard OpenFOAM triangle-fan face centroid/area-vector algorithm."""
    nf = len(faces)
    centres = np.zeros((nf, 3))
    areas = np.zeros((nf, 3))
    for fi, f in enumerate(faces):
        pts = points[f]
        n = len(f)
        f_centre_est = pts.mean(axis=0)
        if n == 3:
            # Planar triangle: exact, no fan decomposition ambiguity.
            v1 = pts[1] - pts[0]
            v2 = pts[2] - pts[0]
            a = 0.5 * np.cross(v1, v2)
            areas[fi] = a
            centres[fi] = pts.mean(axis=0)
            continue
        sumA = 0.0
        sumAc = np.zeros(3)
        sumN = np.zeros(3)
        for i in range(n):
            p1 = pts[i]
            p2 = pts[(i + 1) % n]
            n_tri = np.cross(p2 - p1, f_centre_est - p1)
            a_tri = np.linalg.norm(n_tri)
            c_tri = (p1 + p2 + f_centre_est) / 3.0
            sumN += n_tri
            sumA += a_tri
            sumAc += a_tri * c_tri
        if sumA > 1e-300:
            centres[fi] = sumAc / sumA
        else:
            centres[fi] = f_centre_est
        areas[fi] = 0.5 * sumN
    return centres, areas


def reconstruct_cell_centres_vols(mesh: Mesh):
    """Standard OpenFOAM pyramidal-decomposition cell centroid/volume
    algorithm, built from face_centres/face_areas. Independent of any
    shipped C/V field -- validate against shipped C/V where available."""
    nc = mesh.num_cell
    # cEst = mean of face centres touching each cell (owner + neighbour)
    sum_c = np.zeros((nc, 3))
    cnt = np.zeros(nc)
    np.add.at(sum_c, mesh.owner, mesh.face_centres)
    np.add.at(cnt, mesh.owner, 1.0)
    nbr = mesh.neighbour
    np.add.at(sum_c, nbr, mesh.face_centres[: mesh.num_inner_face])
    np.add.at(cnt, nbr, 1.0)
    c_est = sum_c / cnt[:, None]

    cell_vol = np.zeros(nc)
    cell_ctr = np.zeros((nc, 3))

    # Owner contribution (all faces): Sf points owner->neighbour (outward
    # from owner), so pyr3vol uses +Sf.
    Sf = mesh.face_areas
    Cf = mesh.face_centres
    owner = mesh.owner
    pyr3vol_o = np.einsum("ij,ij->i", Sf, Cf - c_est[owner])
    pc_o = 0.75 * Cf + 0.25 * c_est[owner]
    np.add.at(cell_vol, owner, pyr3vol_o)
    np.add.at(cell_ctr, owner, pyr3vol_o[:, None] * pc_o)

    # Neighbour contribution (internal faces only): outward from neighbour
    # is -Sf.
    ni = mesh.num_inner_face
    pyr3vol_n = -np.einsum("ij,ij->i", Sf[:ni], Cf[:ni] - c_est[nbr])
    pc_n = 0.75 * Cf[:ni] + 0.25 * c_est[nbr]
    np.add.at(cell_vol, nbr, pyr3vol_n)
    np.add.at(cell_ctr, nbr, pyr3vol_n[:, None] * pc_n)

    cell_ctr = cell_ctr / cell_vol[:, None]
    cell_vol = cell_vol / 3.0
    return cell_ctr, cell_vol


# ---------------------------------------------------------------------------
# Boundary-field parsing for a vector field file (U): returns, per patch,
# either an (nFaces,3) explicit value array (fixedValue) or None (meaning
# "derive from owner cell / neighbour cell per boundary-condition type").
# ---------------------------------------------------------------------------

def read_vector_boundary_field(field_path: Path, patch_names: list[str]) -> dict:
    text = (field_path).read_text()
    # Isolate the boundaryField { ... } block (last top-level brace block).
    idx = text.index("boundaryField")
    body_start = text.index("{", idx) + 1
    depth = 1
    j = body_start
    while depth > 0:
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
        j += 1
    body = text[body_start:j - 1]

    out = {}
    for name in patch_names:
        m = re.search(rf"\b{re.escape(name)}\s*\{{", body)
        if not m:
            out[name] = {"type": None, "value": None}
            continue
        start = m.end()
        depth = 1
        k = start
        while depth > 0:
            if body[k] == "{":
                depth += 1
            elif body[k] == "}":
                depth -= 1
            k += 1
        patch_body = body[start:k - 1]
        tm = re.search(r"type\s+(\w+)\s*;", patch_body)
        ptype = tm.group(1) if tm else None
        vm = re.search(r"value\s+uniform\s*\(([^)]*)\)\s*;", patch_body)
        if vm:
            val = np.array([float(x) for x in vm.group(1).split()])
            out[name] = {"type": ptype, "value": val, "uniform": True}
            continue
        vm2 = re.search(r"value\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\(", patch_body)
        if vm2:
            cnt = int(vm2.group(1))
            inner, _ = _parse_list_block(patch_body, vm2.end(1))
            vecs = re.findall(r"\(([^()]*)\)", inner)
            arr = np.array([[float(x) for x in v.split()] for v in vecs])
            assert arr.shape[0] == cnt
            out[name] = {"type": ptype, "value": arr, "uniform": False}
            continue
        out[name] = {"type": ptype, "value": None, "uniform": None}
    return out


# ---------------------------------------------------------------------------
# Green-Gauss cell gradient of a vector field U, using mesh geometry + the
# field's own boundary-condition metadata. Returns (n_cell, 9) in OpenFOAM's
# native ordering (xx xy xz yx yy yz zx zy zz), i.e. component (i,j) =
# d(U_i)/d(x_j) -- identical convention consumed by build_features() in
# train_closure_periodic_hill_correction.py.
# ---------------------------------------------------------------------------

def green_gauss_grad_u(mesh: Mesh, U: np.ndarray, C: np.ndarray, V: np.ndarray,
                        u_boundary: dict) -> np.ndarray:
    nc = mesh.num_cell
    ni = mesh.num_inner_face
    owner = mesh.owner
    nbr = mesh.neighbour
    Cf = mesh.face_centres
    Sf = mesh.face_areas

    grad = np.zeros((nc, 3, 3))

    # ---- internal faces: linear (distance-fraction) interpolation -------
    CO = C[owner[:ni]]
    CN = C[nbr]
    d_on = CN - CO
    denom = np.einsum("ij,ij->i", d_on, d_on)
    denom = np.where(denom < 1e-300, 1e-300, denom)
    t = np.einsum("ij,ij->i", Cf[:ni] - CO, d_on) / denom
    t = np.clip(t, 0.0, 1.0)
    Uf_internal = U[owner[:ni]] + t[:, None] * (U[nbr] - U[owner[:ni]])

    contrib_o = Uf_internal[:, :, None] * Sf[:ni, None, :]
    np.add.at(grad, owner[:ni], contrib_o)
    np.add.at(grad, nbr, -contrib_o)

    # ---- boundary faces: per-patch treatment -----------------------------
    for name, meta in mesh.boundary.items():
        start = meta["startFace"]
        n = meta["nFaces"]
        face_ids = np.arange(start, start + n)
        own = owner[face_ids]
        bmeta = u_boundary.get(name, {"type": None, "value": None})
        btype = bmeta.get("type")
        Sf_b = Sf[face_ids]
        Cf_b = Cf[face_ids]

        if btype == "cyclic":
            npatch = meta["neighbourPatch"]
            nmeta = mesh.boundary[npatch]
            nstart = nmeta["startFace"]
            nface_ids = np.arange(nstart, nstart + n)
            nown = owner[nface_ids]
            Uf = 0.5 * (U[own] + U[nown])
        elif btype == "noSlip":
            Uf = np.zeros((n, 3))
        elif btype in ("fixedValue",):
            val = bmeta.get("value")
            if val is None:
                Uf = U[own]
            elif bmeta.get("uniform"):
                Uf = np.broadcast_to(val, (n, 3))
            else:
                Uf = val
        elif btype == "symmetry" or meta.get("type") == "symmetry":
            nhat = Sf_b / np.linalg.norm(Sf_b, axis=1, keepdims=True)
            Uo = U[own]
            Uf = Uo - 2.0 * np.einsum("ij,ij->i", Uo, nhat)[:, None] * nhat
        else:
            # zeroGradient, empty, calculated, or unknown: owner value.
            # (empty-patch pairs cancel exactly in the Green-Gauss sum
            # since Sf_front = -Sf_back with equal owner value.)
            Uf = U[own]

        contrib = Uf[:, :, None] * Sf_b[:, None, :]
        np.add.at(grad, own, contrib)

    grad = grad / V[:, None, None]
    # Empirically validated against the benchmark's own shipped gradU
    # (see validate_closure_mesh_recon.py check 2): the file's own storage
    # convention is the TRANSPOSE of the textbook (1/V)*sum(Uf (x) Sf)
    # Green-Gauss formula used above (transpose-corrected correlation
    # 0.9999 vs -0.009 untransposed, on a periodic-hills training case).
    # Transpose here so this function's output matches the shipped
    # convention exactly (component (i,j) = d(U_i)/d(x_j), consumed by
    # build_features() in train_closure_periodic_hill_correction.py).
    grad = np.transpose(grad, (0, 2, 1))
    return grad.reshape(nc, 9)


def compute_wall_distance(mesh: Mesh, C: np.ndarray, wall_patch_names: list[str]) -> np.ndarray:
    """Nearest-neighbour distance from each cell centre to the nearest
    wall-patch FACE CENTRE (a standard, simple approximation to true
    normal wall distance; accurate wherever the near-wall cell layer is
    thin relative to wall-patch face spacing, which holds for these
    boundary-layer-resolving meshes)."""
    from scipy.spatial import cKDTree
    wall_face_ids = []
    for name in wall_patch_names:
        meta = mesh.boundary[name]
        wall_face_ids.extend(range(meta["startFace"], meta["startFace"] + meta["nFaces"]))
    wall_face_ids = np.array(wall_face_ids)
    wall_pts = mesh.face_centres[wall_face_ids]
    tree = cKDTree(wall_pts)
    dist, _ = tree.query(C, k=1)
    return dist
