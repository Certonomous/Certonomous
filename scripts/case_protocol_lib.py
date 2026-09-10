#!/usr/bin/env python3
"""Shared machinery for THE CASE PROTOCOL stages 1-4.

This is the FIRST INSTANCE of the protocol (case: ONERA M6) and is written to be
reused by every later case, so nothing in this file names M6.

Design rules taken from the lab constitution and repeated here because a reader of
this file must not have to go and look them up:

  * rule 3  -- a zero from a reader not shown able to see a non-zero is not
               evidence.  Every reader in this file that can return "nothing wrong"
               has a `plant_*` twin that drives a KNOWN perturbation through the
               SAME code path, and the caller REFUSES if the twin comes back clean.
  * rule 4  -- a run is done only if rc==0 AND an `End` line AND last time ==
               endTime AND fields present AND every field newer than the case's own
               0/<field>.  `completion_report()` returns all clauses; it never
               degrades a missing clause into a pass.
  * rule 12 -- core-minutes = wall_s * ranks / 60.  Dollars are DERIVED.
  * rule 16 -- functions here return structured state, never printed transcripts.

Nothing in this file launches compute.  Stage scripts do that.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import numpy as np
except ImportError:  # pragma: no cover - numpy is present on this box
    np = None


# --------------------------------------------------------------------------
# 0.  Refusal.  A stage NEVER degrades; it refuses with a named reason.
# --------------------------------------------------------------------------

class Refusal(Exception):
    """Raised when a check cannot be performed honestly.

    A Refusal is NOT a failing check.  A failing check is a red the stage knows how
    to act on.  A Refusal means the instrument itself is not trustworthy, and the
    only legal response is to stop.  Distinguishing the two is the whole reason
    this is a separate exception type rather than a boolean.
    """

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"REFUSE[{code}]: {detail}")


def refuse(code: str, detail: str) -> "Refusal":
    raise Refusal(code, detail)


# --------------------------------------------------------------------------
# 1.  Hashing and birth certificates.
# --------------------------------------------------------------------------

def sha256_file(path: os.PathLike | str, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_tree(root: os.PathLike | str, patterns: Sequence[str]) -> Dict[str, str]:
    """Hash every file under `root` matching any of `patterns` (glob, relative).

    Returns an ordered {relative_path: sha256} map.  Order is sorted so the digest
    of the map is reproducible.
    """
    root = Path(root)
    out: Dict[str, str] = {}
    for pat in patterns:
        for p in sorted(root.glob(pat)):
            if p.is_file():
                out[str(p.relative_to(root))] = sha256_file(p)
    return dict(sorted(out.items()))


def digest_of_map(m: Dict[str, str]) -> str:
    payload = json.dumps(m, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(payload)


# --- THE BINDING SCHEMA -----------------------------------------------------
# `<case>/<level>/BIRTH_CERTIFICATE.json` and `<case>/FREEZE_MANIFEST.json` are
# fixed by VERIFICATION_CHARTER v1.75 (f49d3e42) sections 2bd.1 / 2be, relayed as
# binding by the cfd-supervisor.  These emitters exist so no stage can invent a
# variant of the shape the freeze hook reads.  A field that cannot be produced
# honestly is emitted as null WITH a reason -- verification would rather see a
# null than a number read from the wrong file.

def n_cells_from_checkmesh(log_path: os.PathLike | str) -> Tuple[Optional[int], str]:
    """Read nCells from a checkMesh log, and return HOW it was read.

    This function exists because of a measured defect: `len(parse_owner(case))`
    was used as a cell count in a frozen comparator and was 4.01x wrong, because
    `polyMesh/owner` holds one entry per FACE.  A cell count that reaches a
    refinement ratio -- and therefore an observed order and every GCI derived from
    it -- is read from something that counts CELLS and names where it read it.

    Returns (n_cells_or_None, source_string).  Never guesses.
    """
    p = Path(log_path)
    if not p.is_file():
        return None, f"ABSENT: {p} does not exist; no cell-counting source available"
    txt = p.read_text(errors="replace")
    m = re.search(r"^\s*cells:\s*(\d+)\s*$", txt, re.M)
    if not m:
        return None, f"UNREADABLE: {p} has no 'cells: N' line; refusing to substitute another count"
    return int(m.group(1)), f"checkMesh stdout: cells: {m.group(1)} ({p})"


def mesh_manifest(mesh_dir: os.PathLike | str) -> Tuple[Dict[str, str], str]:
    """{path: sha256} over the level's polyMesh, plus the sha256 of that manifest."""
    root = Path(mesh_dir)
    man = {}
    for f in sorted(root.rglob("*")):
        if f.is_file():
            man[str(f.relative_to(root))] = sha256_file(f)
    if not man:
        refuse("MESH_MANIFEST_EMPTY", f"{root}: no files to hash")
    return man, digest_of_map(man)


def bbox_of(points: "np.ndarray") -> Dict[str, List[float]]:
    return {"min": [float(v) for v in points.min(axis=0)],
            "max": [float(v) for v in points.max(axis=0)]}


def write_birth_certificate(out_path: os.PathLike | str, *, case: str, level: str,
                            n_cells: Optional[int], n_cells_source: str,
                            n_faces: Optional[int], n_points: Optional[int],
                            bbox: Optional[Dict[str, List[float]]], h_ref: Optional[float],
                            refinement_ratio_vs_next_coarser: Optional[float],
                            geometry_source_file: Optional[str], geometry_sha256: Optional[str],
                            geometry_gate: Dict[str, Any],
                            generator_script: str, generator_blob_sha: str,
                            generator_argv: List[str], generator_rc: Optional[int],
                            manifest: Dict[str, str], manifest_sha256: str,
                            notes: Optional[List[str]] = None) -> str:
    """Emit BIRTH_CERTIFICATE.json in the binding shape.  Returns its sha256."""
    doc = {
        "case": case,
        "level": level,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mesh": {
            "n_cells": n_cells,
            "n_cells_source": n_cells_source,
            "n_faces": n_faces,
            "n_points": n_points,
            "bbox": bbox,
            "h_ref": h_ref,
            "refinement_ratio_vs_next_coarser": refinement_ratio_vs_next_coarser,
        },
        "geometry": {
            "source_file": geometry_source_file,
            "sha256": geometry_sha256,
            "geometry_gate": geometry_gate,
        },
        "generator": {
            "script": generator_script,
            "blob_sha": generator_blob_sha,
            "argv": list(generator_argv),
            "rc": generator_rc,
        },
        "mesh_manifest_sha256": manifest_sha256,
        "mesh_manifest": manifest,
    }
    if notes:
        doc["notes"] = list(notes)
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=2, sort_keys=False) + "\n")
    return sha256_file(p)


def verify_birth(cert_path: os.PathLike | str, mesh_dir: os.PathLike | str) -> Tuple[bool, List[str]]:
    """Re-hash the level's mesh files and compare against its birth certificate.

    A False here means the mesh on disk is NOT the mesh the certificate describes.
    `renumberMesh -overwrite` is the documented way that happens on this box, and it
    happens silently, which is the reason this check exists at all.
    """
    doc = json.loads(Path(cert_path).read_text())
    want = doc.get("mesh_manifest") or {}
    root = Path(mesh_dir)
    complaints: List[str] = []
    for rel, wsha in want.items():
        f = root / rel
        if not f.is_file():
            complaints.append(f"MISSING {rel}")
            continue
        got = sha256_file(f)
        if got != wsha:
            complaints.append(f"MUTATED {rel} born={wsha[:12]} now={got[:12]}")
    extra = set()
    for f in root.rglob("*"):
        if f.is_file() and str(f.relative_to(root)) not in want:
            extra.add(str(f.relative_to(root)))
    for e in sorted(extra):
        complaints.append(f"UNCERTIFIED FILE PRESENT {e}")
    return (not complaints), complaints


def write_freeze_manifest(out_path: os.PathLike | str, *, case: str, registration_path: str,
                          registration_blob: Optional[str], freeze_commit: Optional[str],
                          pins: List[Dict[str, str]], invocations: List[Dict[str, Any]],
                          guards: List[Dict[str, Any]], gates: List[Dict[str, Any]],
                          solver_tolerance: Any, tightest_gate: Any,
                          tolerance_strictly_tighter: bool, cost_block: Dict[str, Any],
                          blockage: Any, budget_gate: str,
                          extra: Optional[Dict[str, Any]] = None) -> str:
    """Emit FREEZE_MANIFEST.json -- the file the freeze hook actually reads.

    Two shapes here are load-bearing and are enforced rather than documented:
      * every pin path is REPO-RELATIVE.  A bare filename resolves as repo-relative
        anyway and then reports PIN-ABSENT while the file sits present and clean.
      * every invocation argv is a LIST, never a shell string, so a missing flag
        shows up as a diff rather than needing a parse.  A pinned comparator invoked
        with a flag missing is an UNPINNED grading path; that is how R1b died.
    Ancestry is deliberately NOT computed here -- the hook derives it from
    `freeze_commit` plus each pin's blob.
    """
    for pin in pins:
        pth = pin.get("path", "")
        if pth.startswith("/") or "/" not in pth:
            refuse("PIN_PATH_NOT_REPO_RELATIVE",
                   f"pin path {pth!r} must be repo-relative with a directory component")
        if pin.get("role") not in {"comparator", "reference", "registered_set",
                                   "launcher", "manifest", "other"}:
            refuse("PIN_ROLE_INVALID", f"pin {pth!r} has role {pin.get('role')!r}")
    for inv in invocations:
        if not isinstance(inv.get("argv"), list):
            refuse("INVOCATION_ARGV_NOT_LIST",
                   f"invocation {inv.get('name')!r} argv must be a list, not a shell string")
    for g in guards:
        if g.get("armed") not in {"unconditional", "by_data"}:
            refuse("GUARD_ARMED_INVALID", f"guard {g.get('name')!r} armed={g.get('armed')!r}")
        # A pin proves a file unchanged.  It does NOT prove the guard inside it is
        # awake.  A manifest can name the guard, name the pin, and have the field
        # inside that pin be null -- a sleeping check one level below the one the
        # clause was written to catch.  So every guard also reports whether its
        # arming datum is PRESENT in the pinned blob, and what its value is.
        if "arming_datum_present" not in g:
            refuse("GUARD_ARMING_UNREPORTED",
                   f"guard {g.get('name')!r} must report arming_datum_present; "
                   "a guard whose arming datum was never looked for is not an armed guard")
        g.setdefault("arming_value", None)
    doc = {
        "case": case,
        "registration_path": registration_path,
        "registration_blob": registration_blob,
        "freeze_commit": freeze_commit,
        "pins": pins,
        "invocations": invocations,
        "guards": guards,
        "gates": gates,
        "solver_tolerance": solver_tolerance,
        "tightest_gate": tightest_gate,
        "tolerance_strictly_tighter": bool(tolerance_strictly_tighter),
        "cost": cost_block,
        "blockage": blockage,
        "budget_gate": budget_gate,
    }
    if extra:
        doc.update(extra)
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=2, sort_keys=False) + "\n")
    return sha256_file(p)


# --------------------------------------------------------------------------
# 2.  OpenFOAM ASCII polyMesh reader.
#
#     Deliberately NOT a general OpenFOAM parser.  It reads exactly what the
#     protocol's resolution gate and BC-closure audit need, refuses on anything
#     it does not understand, and never guesses a format.
# --------------------------------------------------------------------------

_HDR_END = re.compile(rb"//\s*(?:\*[ \t]*)+//")


def _open_maybe_gz(path: Path) -> bytes:
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as fh:
            return fh.read()
    return path.read_bytes()


def _resolve(path_no_gz: Path) -> Path:
    if path_no_gz.is_file():
        return path_no_gz
    gz = Path(str(path_no_gz) + ".gz")
    if gz.is_file():
        return gz
    refuse("MESH_FILE_ABSENT", f"neither {path_no_gz} nor {gz} exists")


def _strip_header(raw: bytes) -> bytes:
    """Return the body after the FoamFile header banner.

    Refuses on a binary-format file rather than silently producing nonsense --
    reading a binary owner list as ASCII yields a plausible-looking small number,
    which is exactly the kind of quiet wrong answer rule 3 exists to stop.
    """
    m = re.search(rb"format\s+(\w+)\s*;", raw[:4096])
    if m and m.group(1) != b"ascii":
        refuse("MESH_FORMAT_BINARY",
               f"polyMesh file is format={m.group(1).decode()}; this reader is ASCII-only "
               "and will not guess")
    # The FIRST banner is the header terminator.  Taking the LAST match is wrong and
    # fails silently on short files: `boundary` is ~1 KiB and its closing
    # `// **** //` also matches, so a last-match read strips the entire body and
    # then reports "zero patches" -- a plausible-looking empty answer.
    m2 = _HDR_END.search(raw[:8192])
    if not m2:
        refuse("MESH_HEADER_UNPARSED", "no FoamFile banner terminator found in first 8 KiB")
    return raw[m2.end():]


def read_scalar_list(path: Path) -> "np.ndarray":
    """Read `N ( v v v ... )` of ints/floats into a numpy array."""
    body = _strip_header(_open_maybe_gz(_resolve(path)))
    i = body.find(b"(")
    if i < 0:
        refuse("MESH_LIST_UNPARSED", f"{path}: no '(' after header")
    count_txt = body[:i].strip()
    try:
        n = int(count_txt.split()[-1])
    except Exception:
        refuse("MESH_LIST_UNPARSED", f"{path}: cannot read element count from {count_txt[:40]!r}")
    j = body.rfind(b")")
    arr = np.fromstring(body[i + 1:j], sep=" ") if hasattr(np, "fromstring") else None
    if arr is None or arr.size != n:
        arr = np.array(body[i + 1:j].split(), dtype=np.float64)
    if arr.size != n:
        refuse("MESH_LIST_COUNT", f"{path}: header says {n} entries, body has {arr.size}")
    return arr


def read_vector_list(path: Path) -> "np.ndarray":
    """Read `N ( (x y z) (x y z) ... )` into an (N,3) array."""
    body = _strip_header(_open_maybe_gz(_resolve(path)))
    i = body.find(b"(")
    n = int(body[:i].strip().split()[-1])
    j = body.rfind(b")")
    inner = body[i + 1:j].replace(b"(", b" ").replace(b")", b" ")
    arr = np.array(inner.split(), dtype=np.float64)
    if arr.size != 3 * n:
        refuse("MESH_LIST_COUNT", f"{path}: header says {n} vectors, body has {arr.size/3:g}")
    return arr.reshape(n, 3)


def read_face_list(path: Path) -> Tuple["np.ndarray", "np.ndarray"]:
    """Read `N ( 4(a b c d) 3(a b c) ... )`.

    Returns (flat_vertex_indices, offsets) with offsets of length N+1, i.e. face k
    is flat[offsets[k]:offsets[k+1]].  Faces on this box are mixed 3/4-gon at the
    wing tip cap, so a fixed-width read would be wrong.
    """
    body = _strip_header(_open_maybe_gz(_resolve(path)))
    i = body.find(b"(")
    n = int(body[:i].strip().split()[-1])
    j = body.rfind(b")")
    inner = body[i + 1:j]
    # "4(a b c d)" -> "4 a b c d"
    toks = np.array(inner.replace(b"(", b" ").replace(b")", b" ").split(), dtype=np.int64)
    offsets = np.zeros(n + 1, dtype=np.int64)
    flat = np.empty(toks.size - n, dtype=np.int64)
    pos = 0
    out = 0
    for k in range(n):
        m = int(toks[pos]); pos += 1
        flat[out:out + m] = toks[pos:pos + m]
        pos += m
        out += m
        offsets[k + 1] = out
    if pos != toks.size:
        refuse("MESH_FACE_TRAILING", f"{path}: {toks.size - pos} unconsumed tokens after {n} faces")
    return flat[:out], offsets


def read_boundary(path: Path) -> Dict[str, Dict[str, Any]]:
    """Parse constant/polyMesh/boundary into {name: {type,nFaces,startFace,...}}."""
    txt = _strip_header(_open_maybe_gz(_resolve(path))).decode("utf-8", "replace")
    i = txt.find("(")
    j = txt.rfind(")")
    body = txt[i + 1:j]
    out: Dict[str, Dict[str, Any]] = {}
    for m in re.finditer(r"([A-Za-z_][\w.\-]*)\s*\{([^{}]*)\}", body):
        name, blk = m.group(1), m.group(2)
        d: Dict[str, Any] = {}
        for km in re.finditer(r"(\w+)\s+([^;]+);", blk):
            k, v = km.group(1), km.group(2).strip()
            d[k] = int(v) if re.fullmatch(r"\d+", v) else v
        out[name] = d
    if not out:
        refuse("MESH_BOUNDARY_EMPTY", f"{path}: parsed zero patches")
    return out


@dataclass
class MeshRead:
    root: Path
    points: "np.ndarray"
    face_flat: "np.ndarray"
    face_off: "np.ndarray"
    owner: "np.ndarray"
    neighbour: "np.ndarray"
    boundary: Dict[str, Dict[str, Any]]

    @property
    def nfaces(self) -> int:
        return int(self.face_off.size - 1)

    @property
    def ncells(self) -> int:
        return int(max(self.owner.max(), self.neighbour.max() if self.neighbour.size else -1)) + 1


def read_polymesh(mesh_dir: os.PathLike | str) -> MeshRead:
    d = Path(mesh_dir)
    pts = read_vector_list(d / "points")
    flat, off = read_face_list(d / "faces")
    own = read_scalar_list(d / "owner").astype(np.int64)
    nei = read_scalar_list(d / "neighbour").astype(np.int64)
    bnd = read_boundary(d / "boundary")
    if own.size != off.size - 1:
        refuse("MESH_OWNER_MISMATCH",
               f"{d}: owner has {own.size} entries, faces has {off.size-1}")
    return MeshRead(d, pts, flat, off, own, nei, bnd)


def face_centres_and_areas(mesh: MeshRead, faces: Iterable[int]) -> Tuple["np.ndarray", "np.ndarray"]:
    """Centroid and area vector for the given face indices, by fan triangulation.

    This is OpenFOAM's own algorithm (fan about the average of the vertices), not a
    vertex mean -- a vertex mean is wrong for the high-stretch quads at a wing
    trailing edge, which is precisely where this protocol's first case fails.
    """
    faces = list(faces)
    C = np.zeros((len(faces), 3))
    S = np.zeros((len(faces), 3))
    P = mesh.points
    for idx, f in enumerate(faces):
        v = P[mesh.face_flat[mesh.face_off[f]:mesh.face_off[f + 1]]]
        n = v.shape[0]
        if n == 3:
            C[idx] = v.mean(axis=0)
            S[idx] = 0.5 * np.cross(v[1] - v[0], v[2] - v[0])
            continue
        ctr = v.mean(axis=0)
        a_sum = np.zeros(3)
        c_sum = np.zeros(3)
        amag = 0.0
        for k in range(n):
            t1 = v[k]
            t2 = v[(k + 1) % n]
            a = 0.5 * np.cross(t2 - t1, ctr - t1)
            m = np.linalg.norm(a)
            c = (t1 + t2 + ctr) / 3.0
            a_sum += a
            c_sum += m * c
            amag += m
        S[idx] = a_sum
        C[idx] = c_sum / amag if amag > 0 else ctr
    return C, S


def cell_faces(mesh: MeshRead, only: Optional[Iterable[int]] = None) -> Dict[int, List[int]]:
    """cell -> [face ids].

    `only` restricts the map to the named cells.  That matters at scale: the fine
    level of a three-level family has millions of cells and tens of millions of
    faces, and a full Python dict of those is gigabytes for a question that only
    ever asks about the one layer of cells touching a wall.
    """
    cf: Dict[int, List[int]] = {}
    if only is None:
        for f, c in enumerate(mesh.owner):
            cf.setdefault(int(c), []).append(f)
        for f, c in enumerate(mesh.neighbour):
            cf.setdefault(int(c), []).append(f)
        return cf
    wanted = np.fromiter(set(int(c) for c in only), dtype=np.int64)
    for arr in (mesh.owner, mesh.neighbour):
        hit = np.nonzero(np.isin(arr, wanted))[0]
        for f in hit:
            cf.setdefault(int(arr[f]), []).append(int(f))
    return cf


@dataclass
class WallSpacing:
    patch: str
    nfaces: int
    y1_min: float
    y1_mean: float
    y1_max: float
    y1_median: float
    method: str


def first_cell_height(mesh: MeshRead, patch: str) -> WallSpacing:
    """Wall-normal height of the first cell off `patch`, per face.

    Method, stated because the number is only as good as its definition: for each
    boundary face of the patch, take the owner cell, take that cell's centroid as
    the area-weighted mean of its own face centroids, and report
        y1 = 2 * | (Ccell - Cface) . nhat |
    where nhat is the unit face normal.  For a hexahedral boundary-layer cell this
    is the cell height to within the cell's own non-orthogonality, and it is the
    quantity a y+ estimate needs.  It is NOT the wall distance of the cell centre;
    that is y1/2.
    """
    if patch not in mesh.boundary:
        refuse("PATCH_ABSENT", f"patch {patch!r} not in {sorted(mesh.boundary)}")
    p = mesh.boundary[patch]
    start, n = int(p["startFace"]), int(p["nFaces"])
    bfaces = list(range(start, start + n))
    Cb, Sb = face_centres_and_areas(mesh, bfaces)
    nhat = Sb / np.linalg.norm(Sb, axis=1, keepdims=True)

    owners = [int(mesh.owner[f]) for f in bfaces]
    cf = cell_faces(mesh, only=owners)
    y1 = np.zeros(n)
    for i, f in enumerate(bfaces):
        c = int(mesh.owner[f])
        fl = cf[c]
        Cf, Sf = face_centres_and_areas(mesh, fl)
        w = np.linalg.norm(Sf, axis=1)
        ccell = (Cf * w[:, None]).sum(axis=0) / w.sum()
        y1[i] = 2.0 * abs(float(np.dot(ccell - Cb[i], nhat[i])))
    return WallSpacing(patch, n, float(y1.min()), float(y1.mean()), float(y1.max()),
                       float(np.median(y1)),
                       "2*|(Ccell-Cface).nhat|, Ccell = area-weighted mean of the cell's face centroids")


# --------------------------------------------------------------------------
# 3.  Resolution from physics.  Turns a wall spacing into a y+ and a verdict.
# --------------------------------------------------------------------------

def flat_plate_yplus(y1: float, rho: float, U: float, mu: float, x: float) -> float:
    """y+ of the FIRST CELL CENTRE (y1/2) from the 1/7-power flat-plate law.

    Cf = 0.0576 Re_x^{-1/5} is the classical turbulent flat-plate local skin
    friction; it is an ESTIMATE, valid to maybe +-20% on a wing, and it is used
    here only to answer a question whose answer is three orders of magnitude wide.
    """
    Re_x = rho * U * x / mu
    cf = 0.0576 * Re_x ** -0.2
    tau_w = 0.5 * cf * rho * U * U
    u_tau = (tau_w / rho) ** 0.5
    return (y1 / 2.0) * u_tau * rho / mu


@dataclass
class ResolutionVerdict:
    y1_mean: float
    y1_min: float
    yplus_mean: float
    yplus_min: float
    regime: str          # WALL_RESOLVED | WALL_FUNCTION_VALID | OUT_OF_MODEL_VALIDITY
    admissible: bool
    reason: str


def classify_resolution(ws: WallSpacing, rho: float, U: float, mu: float, x_ref: float,
                        wall_treatment: str) -> ResolutionVerdict:
    """Decide whether the near-wall discretisation can carry the chosen closure.

    Thresholds are model validity, not taste:
      * a low-Re / wall-resolved integration needs the first cell centre inside the
        viscous sublayer, y+ <~ 1 (5 at the absolute outside).
      * a standard log-law wall function needs the first cell centre in the
        logarithmic layer, 30 <~ y+ <~ 300.  Above ~300 the first cell centre is in
        the wake region, where the log law it is inverting does not hold, and the
        wall shear it returns is not a modelling approximation -- it is wrong.
    """
    yp = flat_plate_yplus(ws.y1_mean, rho, U, mu, x_ref)
    yp_min = flat_plate_yplus(ws.y1_min, rho, U, mu, x_ref)
    if wall_treatment == "resolved":
        ok = yp <= 5.0
        regime = "WALL_RESOLVED" if yp <= 1.0 else ("WALL_RESOLVED_MARGINAL" if ok else "OUT_OF_MODEL_VALIDITY")
        why = f"resolved integration wants y+<=1 (<=5 marginal); estimate {yp:.3g}"
    elif wall_treatment == "wallfunction":
        ok = 20.0 <= yp <= 300.0
        if yp < 20.0:
            regime, why = "OUT_OF_MODEL_VALIDITY", f"y+ {yp:.3g} below the log layer"
        elif yp > 300.0:
            regime, why = "OUT_OF_MODEL_VALIDITY", (
                f"y+ {yp:.3g} puts the first cell centre in the wake region; the log law "
                "being inverted does not hold there")
        else:
            regime, why = "WALL_FUNCTION_VALID", f"y+ {yp:.3g} inside the log layer"
    else:
        refuse("WALL_TREATMENT_UNKNOWN", f"{wall_treatment!r} is not resolved|wallfunction")
    return ResolutionVerdict(ws.y1_mean, ws.y1_min, yp, yp_min, regime, bool(ok), why)


# --------------------------------------------------------------------------
# 4.  Class defaults.  A missing entry is REGISTERED and NEVER WAITS.
# --------------------------------------------------------------------------

CLASS_DEFAULTS_PATH = "docs/CASE_CLASS_DEFAULTS.json"


def lookup_class_default(repo: Path, case_class: str, key: str, first_use_value: Any,
                         rationale: str, journal: List[Dict[str, Any]]) -> Any:
    """Return the knowledge-base value for (case_class, key).

    If the knowledge base has no entry, this does NOT block.  It returns
    `first_use_value`, appends a `class default, first use` row to `journal`, and
    the stage writes the journal into the registration.  A missing entry is a thing
    to record, not a thing to wait for.
    """
    p = repo / CLASS_DEFAULTS_PATH
    db = json.loads(p.read_text()) if p.is_file() else {}
    entry = db.get(case_class, {}).get(key)
    if entry is None:
        journal.append({
            "case_class": case_class, "key": key, "value": first_use_value,
            "status": "class default, first use", "rationale": rationale,
            "knowledge_base": str(p), "kb_present": p.is_file(),
        })
        return first_use_value
    journal.append({
        "case_class": case_class, "key": key, "value": entry.get("value", entry),
        "status": "from knowledge base", "rationale": entry.get("rationale", ""),
        "knowledge_base": str(p), "kb_present": True,
    })
    return entry.get("value", entry)


# --------------------------------------------------------------------------
# 5.  The T23G2Rn2 rule: solver tolerance STRICTLY TIGHTER than any gate.
# --------------------------------------------------------------------------

@dataclass
class ToleranceCheck:
    gate_name: str
    gate_tolerance: float
    solver_tolerances: Dict[str, float]
    worst_field: str
    worst_value: float
    margin_decades: float
    ok: bool
    reason: str


def check_tolerance_strictly_tighter(gate_name: str, gate_tolerance: float,
                                     solver_tolerances: Dict[str, float],
                                     min_decades: float = 1.0) -> ToleranceCheck:
    """Refuse a configuration whose linear-solver floor can manufacture the gate.

    The failure this prevents is specific and has a name in this lab (T23G2Rn2): if
    the linear solver stops at 1e-6 and the gate asks whether a quantity moved by
    less than 1e-6, then the gate is measuring the solver's stopping criterion and
    not the physics, and it will pass for a reason that has nothing to do with the
    answer.  `min_decades` is how much clear air the gate must have.
    """
    worst_f = max(solver_tolerances, key=lambda k: solver_tolerances[k])
    worst = solver_tolerances[worst_f]
    import math
    margin = math.log10(gate_tolerance / worst) if worst > 0 else float("inf")
    ok = margin >= min_decades
    return ToleranceCheck(
        gate_name, gate_tolerance, dict(solver_tolerances), worst_f, worst, margin, ok,
        (f"loosest solver tolerance {worst_f}={worst:g} vs gate {gate_tolerance:g}: "
         f"{margin:.2f} decades of clear air, need {min_decades:g}"))


# --------------------------------------------------------------------------
# 6.  Rule-4 completion.  All clauses or nothing.
# --------------------------------------------------------------------------

@dataclass
class CompletionReport:
    case: str
    rc: Optional[int]
    rc_source: str
    has_end: bool
    last_time: Optional[str]
    end_time: Optional[str]
    time_matches: bool
    fields_required: List[str]
    fields_present: List[str]
    fields_missing: List[str]
    age_guard_pass: Optional[bool]
    age_guard_detail: List[str]
    complete: bool
    failed_clauses: List[str]


def completion_report(case_dir: os.PathLike | str, log_path: os.PathLike | str,
                      required_fields: Sequence[str], rc_path: Optional[os.PathLike | str],
                      end_time: Optional[str] = None) -> CompletionReport:
    """Evaluate every clause of the strict completion rule and report all of them.

    Deliberately returns every clause rather than short-circuiting: a caller that
    only learns 'not complete' cannot tell a crashed solver from a missing field
    from a stale directory, and the triage difference matters.
    """
    case = Path(case_dir)
    failed: List[str] = []

    rc: Optional[int] = None
    rc_source = "ABSENT"
    if rc_path and Path(rc_path).is_file():
        m = re.search(r"RC\s*=\s*(-?\d+)", Path(rc_path).read_text())
        if m:
            rc, rc_source = int(m.group(1)), str(rc_path)
    if rc != 0:
        failed.append(f"rc={rc!r} (source {rc_source})")

    log = Path(log_path)
    logtxt = log.read_text(errors="replace") if log.is_file() else ""
    has_end = bool(re.search(r"^End\s*$", logtxt, re.M))
    if not has_end:
        failed.append("no End line")

    if end_time is None:
        cd = case / "system" / "controlDict"
        if cd.is_file():
            m = re.search(r"^\s*endTime\s+([0-9.eE+\-]+)\s*;", cd.read_text(), re.M)
            end_time = m.group(1) if m else None

    times = []
    for d in case.iterdir() if case.is_dir() else []:
        if d.is_dir() and re.fullmatch(r"\d+(\.\d+)?", d.name):
            times.append(d.name)
    last_time = max(times, key=float) if times else None
    time_matches = (last_time is not None and end_time is not None
                    and abs(float(last_time) - float(end_time)) < 1e-9)
    if not time_matches:
        failed.append(f"last time {last_time!r} != endTime {end_time!r}")

    present, missing = [], []
    tdir = case / last_time if last_time else None
    for f in required_fields:
        if tdir and ((tdir / f).is_file() or (tdir / (f + ".gz")).is_file()):
            present.append(f)
        else:
            missing.append(f)
    if missing:
        failed.append(f"fields missing at last time: {missing}")

    # Age guard: every field at endTime must be NEWER than the case's own 0/<field>.
    # 0/T is touched last at launch, so it dates the run allowed to produce the answer.
    age_pass: Optional[bool] = None
    age_detail: List[str] = []
    zero_ref = None
    for cand in ("T", "U", "p"):
        for nm in (case / "0" / cand, case / "0" / (cand + ".gz")):
            if nm.is_file():
                zero_ref = nm
                break
        if zero_ref:
            break
    if zero_ref is None:
        age_detail.append("no 0/T|0/U|0/p to date the launch; age guard NOT EVALUABLE")
    elif tdir is None:
        age_detail.append("no time directory; age guard NOT EVALUABLE")
    else:
        t0 = zero_ref.stat().st_mtime
        age_pass = True
        for f in present:
            nm = tdir / f
            if not nm.is_file():
                nm = tdir / (f + ".gz")
            dt = nm.stat().st_mtime - t0
            if dt <= 0:
                age_pass = False
                age_detail.append(f"{last_time}/{f} is {-dt:.0f}s OLDER than {zero_ref.name}")
        if age_pass:
            age_detail.append(f"all {len(present)} fields newer than {zero_ref} (ref mtime {t0:.0f})")
    if age_pass is not True:
        failed.append("age guard: " + ("; ".join(age_detail) or "not evaluable"))

    return CompletionReport(str(case), rc, rc_source, has_end, last_time, end_time,
                            time_matches, list(required_fields), present, missing,
                            age_pass, age_detail, not failed, failed)


# --------------------------------------------------------------------------
# 7.  Cost, in core-minutes.  Dollars are DERIVED and say so.
# --------------------------------------------------------------------------

RATE_USD_PER_CORE_HOUR = 0.0513  # c7a.4xlarge, owner-stated 2026-08-21/22


@dataclass
class Cost:
    wall_s: float
    ranks: int
    core_min: float
    usd_derived: float
    basis: str

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def cost(wall_s: float, ranks: int, basis: str) -> Cost:
    cm = wall_s * ranks / 60.0
    return Cost(wall_s, ranks, cm, cm / 60.0 * RATE_USD_PER_CORE_HOUR,
                basis + " | USD DERIVED at $0.0513/core-h, reported-by-owner, NOT measured "
                        "(this box cannot read its own billing)")


# --------------------------------------------------------------------------
# 8.  Memory capacity.  Measured, drained-ceiling aware.
# --------------------------------------------------------------------------

@dataclass
class MemoryState:
    mem_total_gib: float
    mem_available_gib: float
    anon_rss_gib: float
    drained_ceiling_gib: float
    detail: str


def memory_state(kernel_unreclaimable_gib: float = 0.38) -> MemoryState:
    """MemAvailable now, plus the DRAINED ceiling.

    MemTotal is not the ceiling and MemAvailable is not it either: MemAvailable
    moves as other lanes' solvers come and go, and MemTotal ignores the footprint
    that never drains.  The drained ceiling is MemTotal minus the anonymous RSS
    that survives every solver exiting, minus kernel unreclaimable.
    """
    mi = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        k, _, v = line.partition(":")
        mi[k.strip()] = float(v.strip().split()[0]) / 1048576.0  # kB -> GiB
    anon = 0.0
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            st = (p / "status").read_text()
        except OSError:
            continue
        m = re.search(r"^RssAnon:\s+(\d+) kB", st, re.M)
        if m:
            anon += int(m.group(1)) / 1048576.0
    ceiling = mi["MemTotal"] - anon - kernel_unreclaimable_gib
    return MemoryState(mi["MemTotal"], mi["MemAvailable"], anon, ceiling,
                       f"MemTotal {mi['MemTotal']:.2f} - anonRSS {anon:.2f} - "
                       f"kernel unreclaimable {kernel_unreclaimable_gib:.2f} GiB")


def peak_rss_of(cmd: Sequence[str], cwd: Optional[str] = None,
                env: Optional[Dict[str, str]] = None,
                timeout: Optional[float] = None) -> Tuple[int, float, float]:
    """Run `cmd`, return (rc, peak_rss_gib, wall_s).

    rc is read FROM THE PROCESS -- Popen.returncode -- never from a wrapper's own
    exit status.  `setsid timeout cmd` exits 0 for every outcome, which is how a
    crash gets recorded as a pass on this box; this function does not go near that
    pattern.
    """
    import resource
    t0 = time.time()
    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    try:
        p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        p.communicate()
        return 124, 0.0, time.time() - t0
    after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    peak_kb = max(after, before)
    return p.returncode, peak_kb / 1048576.0, time.time() - t0


# --------------------------------------------------------------------------
# 9.  Planted controls (rule 3).
# --------------------------------------------------------------------------

def planted_control(reader: Callable[[], Any], plant: Callable[[], None],
                    unplant: Callable[[], None], sees_it: Callable[[Any], bool],
                    label: str) -> Dict[str, Any]:
    """Prove a reader can see a non-zero BEFORE trusting its zero.

    `reader` is the REAL reader on the REAL path.  `plant` drives a known
    perturbation into the artifact the reader reads.  If the reader comes back
    clean with the perturbation in place, the reader is blind and this REFUSES --
    it does not report the clean read.
    """
    clean_before = reader()
    plant()
    try:
        planted = reader()
    finally:
        unplant()
    clean_after = reader()
    if not sees_it(planted):
        refuse("PLANT_NOT_SEEN",
               f"{label}: reader did not see the planted perturbation; its zero is not evidence")
    return {
        "label": label,
        "reader_saw_plant": True,
        "clean_before": clean_before,
        "clean_after": clean_after,
        "restored": clean_before == clean_after,
    }


# --------------------------------------------------------------------------
# 10.  OpenFOAM invocation.
# --------------------------------------------------------------------------

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"


def foam_cmd(argv: Sequence[str], case: os.PathLike | str) -> List[str]:
    """Wrap an OpenFOAM utility so the environment is sourced IN THE SAME shell.

    Sourcing in one bash call and running in the next does not work on this box.

    EVERY PATH IS MADE ABSOLUTE FIRST, and that is not tidiness.  The wrapper `cd`s
    into the case before running, so a RELATIVE path in argv is resolved against the
    new working directory and silently doubles:

        cd 'verification/runs/X/L2/case' && checkMesh -case 'verification/runs/X/L2/case'
        -> cannot open root directory ".../L2/case/verification/runs/X/L2"

    which surfaces as a plain rc=1 in a fifth of a second.  A checkMesh that "failed"
    on a 4.6M-cell mesh in 0.22 s never read the mesh at all, and a stage that
    recorded that as a mesh defect would be reporting a red about the wrong thing.
    """
    cabs = str(Path(case).resolve())
    # ONLY the value of -case is absolutised, and nothing else.  The first attempt at
    # this fix absolutised every argv element containing a separator, which broke
    # `foamDictionary system/controlDict`: that path is relative TO THE CASE and was
    # being resolved against the calling process's working directory instead.  One
    # over-broad repair turned three green checks red.  Everything except -case is a
    # case-relative path by OpenFOAM convention and is passed through untouched.
    fixed = []
    take_next = False
    for a in argv:
        s_a = str(a)
        if take_next:
            p_a = Path(s_a)
            fixed.append(s_a if p_a.is_absolute() else str(p_a.resolve()))
            take_next = False
            continue
        fixed.append(s_a)
        if s_a == "-case":
            take_next = True
    inner = " ".join(f"'{a}'" for a in fixed)
    return ["bash", "-lc", f"source {FOAM_BASHRC} '' >/dev/null 2>&1 && cd '{cabs}' && {inner}"]


def state_line(stage: str, check: str, result: str, **numbers: Any) -> str:
    """One machine-greppable line.  Stages print these and nothing else (rule 16)."""
    nums = " ".join(f"{k}={v}" for k, v in numbers.items())
    return f"[{stage}] {check}: {result}" + (f" | {nums}" if nums else "")


def convex_hull_2d(pts: "np.ndarray") -> "np.ndarray":
    """Monotone-chain convex hull of an (N,2) point set, counter-clockwise.

    Written out rather than imported so the geometry gate has no optional
    dependency: a gate that is skipped when scipy is missing is not a gate.
    """
    p = np.unique(pts, axis=0)
    p = p[np.lexsort((p[:, 1], p[:, 0]))]
    if p.shape[0] <= 2:
        return p

    def half(q):
        st = []
        for x in q:
            while len(st) >= 2:
                a, b = st[-2], st[-1]
                if (b[0] - a[0]) * (x[1] - a[1]) - (b[1] - a[1]) * (x[0] - a[0]) <= 0:
                    st.pop()
                else:
                    break
            st.append(x)
        return st

    lower = half(p)
    upper = half(p[::-1])
    return np.array(lower[:-1] + upper[:-1])


def straight_edge_sweep(span: "np.ndarray", chord: "np.ndarray", side: str,
                        span_lo: float, span_hi: float) -> Tuple[Optional[float], Dict[str, Any]]:
    """Sweep angle of a STRAIGHT leading or trailing edge, from the convex hull.

    WHY THE HULL AND NOT SPANWISE BANDING.  The obvious estimator -- bin by span,
    take min (or max) chordwise coordinate per bin, fit a line -- is sampling
    sensitive, and on this protocol's first case it was sensitive enough to matter:
    it returned 30.00 deg on the medium level, 29.92 on the fine, and 26.35 on the
    coarse, and so REFUSED the coarse level of a grid family for a reason that was
    about the estimator rather than about the mesh.  Inside a band of width dz the
    true edge moves by dz*tan(sweep), so a per-band extremum is biased by up to that
    amount, and the bias depends on where points happen to fall rather than on how
    many there are.  A gate that systematically fails coarse grids cannot be used on
    a grid-convergence family at all.

    The hull is immune to this.  An extreme point is extreme at any density, so for
    a straight edge the hull chain between root and tip is the edge itself, and the
    estimate is exact on a coarse mesh and on a fine one alike.

    Returns (sweep_degrees, diagnostics).  `side` is "leading" (minimum chordwise)
    or "trailing" (maximum chordwise).
    """
    m = (span >= span_lo) & (span <= span_hi)
    if m.sum() < 4:
        return None, {"reason": f"only {int(m.sum())} points in the span window"}
    q = np.column_stack([span[m], chord[m]])
    hull = convex_hull_2d(q)
    if hull.shape[0] < 3:
        return None, {"reason": "degenerate hull"}
    cx = float(hull[:, 1].mean())
    n = hull.shape[0]
    best = None
    for i in range(n):
        p0, p1 = hull[i], hull[(i + 1) % n]
        dz, dx = p1[0] - p0[0], p1[1] - p0[1]
        length = float(np.hypot(dz, dx))
        mid_chord = 0.5 * (p0[1] + p1[1])
        on_side = (mid_chord < cx) if side == "leading" else (mid_chord > cx)
        if not on_side or abs(dz) < 1e-9:
            continue
        if best is None or length > best[0]:
            best = (length, p0, p1, dz, dx)
    if best is None:
        return None, {"reason": f"no hull edge on the {side} side spanning in the span direction"}
    length, p0, p1, dz, dx = best
    sweep = float(np.degrees(np.arctan(dx / dz)))
    # how much of the point cloud actually lies ON this edge -- an edge that only two
    # points touch is a corner, not an edge, and the sweep read off it is meaningless.
    d = np.abs((q[:, 1] - p0[1]) * dz - (q[:, 0] - p0[0]) * dx) / length
    on_edge = int((d < float(np.hypot(dz, dx)) * 1e-3).sum())
    return sweep, {
        "hull_vertices": int(n),
        "edge_length_m": length,
        "edge_endpoints": [[float(p0[0]), float(p0[1])], [float(p1[0]), float(p1[1])]],
        "points_on_edge": on_edge,
        "span_window_m": [span_lo, span_hi],
        "method": ("longest convex-hull edge on the chosen side. An extreme point is extreme at "
                   "any mesh density, so for a STRAIGHT edge this is exact on a coarse mesh and "
                   "on a fine one alike -- which is the whole requirement for a gate that has to "
                   "judge every level of a grid family by the same standard."),
    }
