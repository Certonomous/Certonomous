"""Mesh birth certificates (Verification Charter v1.5 section 9, mechanics).

Born clean or it does not enter. The 2026-08-08 archive sweep
(``demo-output/website/campaign/MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md``)
found 178 unique reachable meshes and exactly one born broken -- the A3
vcoarse pyHyp mesh, which entered a case three times under reconstruction
because nothing at entry asked for its certificate. The structural gap was
the mesh caches: bare ``polyMesh`` with no quality record, feeding 400+ run
directories, even where the generating workflow HAD run checkMesh -- the
reading was transient (L-40: the switch that ran must be provable from the
artifact).

The certificate is ``birth_certificate.json`` beside the ``polyMesh``
directory it certifies, hash-bound to it through the sha256 of the points
file so a certificate cannot drift onto a different mesh. Cache layers write
it at save, require it at lookup (a cache entry without a matching-hash
certificate is NOT cached -- the charter's quarantine, and the one-time cost
of the rule is that pre-rule cache entries re-mesh once and re-enter
certified), and carry it into the case at restore.

Verdict basis, the audit's own: hard checkMesh errors -- negative volumes,
wrong-oriented face pyramids, non-orthogonality errors, skewness errors,
flagged aspect ratio -- make a mesh ``broken``. ``-allGeometry`` advisories
(concave cells, small determinant, low-quality decomposition tets, small
interpolation weights) appear on nearly every accepted mesh in the lab's
pre-existing certificates and do not indict one.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CERTIFICATE_NAME = "birth_certificate.json"

#: Verdicts that let a mesh enter. "clean" is a checkMesh run with no hard
#: error; "flagged" is the high-aspect-ratio-only signature the audit
#: recorded on the lab's own certified NASA-grid family (advisory at entry,
#: per Mesh Standard 3.3: aspect ratio is never a lone rejection).
ACCEPTED_VERDICTS = ("clean", "flagged")

# The audit's hard-error patterns, checkMesh's own wording.
_HARD_ERRORS: tuple[tuple[str, re.Pattern], ...] = (
    ("negative-volume cells",
     re.compile(r"\*\*\*Zero or negative cell volume")),
    ("wrong-oriented face pyramids",
     re.compile(r"\*\*\*Error in face pyramids")),
    ("non-orthogonality errors",
     re.compile(r"\*\*\*Number of non-orthogonality errors")),
    ("skewness errors",
     re.compile(r"\*\*\*Max skewness")),
)
_FLAGGED_ASPECT = re.compile(r"\*\*\*High aspect ratio cells found")


def parse_check_log(text: str) -> dict[str, Any]:
    """The certificate payload read out of a checkMesh log's text.

    Returns verdict plus the quality numbers the certificate carries. The
    verdict is ``broken`` on any hard error, ``flagged`` when the only hard
    finding is the aspect-ratio flag (the audit's TMR/NASA-grid signature),
    ``clean`` otherwise.
    """
    stats: dict[str, Any] = {}
    for pattern, key in (
        (r"cells:\s+(\d+)", "cells"),
        (r"Max aspect ratio[:=\s]+([0-9.eE+-]+)", "max_aspect_ratio"),
        (r"non-orthogonality Max:\s*([0-9.eE+-]+)", "max_non_orthogonality"),
        (r"Max skewness =\s*([0-9.eE+-]+)", "max_skewness"),
    ):
        hit = re.search(pattern, text)
        if hit:
            value = float(hit.group(1))
            stats[key] = int(value) if key == "cells" else value
    errors = [name for name, pattern in _HARD_ERRORS if pattern.search(text)]
    flagged = bool(_FLAGGED_ASPECT.search(text))
    if errors or (flagged and stats.get("max_aspect_ratio", 0) > 1e6):
        # A flagged aspect ratio in the pyHyp-pathology range (the specimen
        # reads 2.08e95) is a hard error; the NASA-grid family's flag sits
        # at 6.6e4 to 7.4e4 and stays a flag.
        verdict = "broken"
        if flagged:
            errors.append("flagged aspect ratio")
    elif flagged:
        verdict = "flagged"
    else:
        verdict = "clean"
    stats["verdict"] = verdict
    stats["hard_errors"] = errors
    return stats


def points_sha256(polymesh_dir: Path) -> str | None:
    """sha256 of the mesh's points file (plain or gzipped spelling), the
    hash that binds a certificate to exactly one mesh."""
    for name in ("points", "points.gz"):
        path = Path(polymesh_dir) / name
        if path.exists():
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1 << 20), b""):
                    digest.update(chunk)
            return digest.hexdigest()
    return None


def write_certificate(mesh_root: Path, *, check_log_text: str | None = None,
                      stats: dict[str, Any] | None = None,
                      generator: str | None = None) -> dict[str, Any] | None:
    """Write ``birth_certificate.json`` beside ``mesh_root``'s polyMesh.

    The payload comes from ``check_log_text`` (a checkMesh log, parsed with
    the audit's verdict rule) or a pre-parsed ``stats`` dict carrying at
    least a truthy quality reading. With neither, no certificate is written
    and None is returned: a certificate is a record of a check that ran,
    never an assertion invented at save time.
    """
    mesh_root = Path(mesh_root)
    digest = points_sha256(mesh_root / "polyMesh")
    if digest is None:
        return None
    if check_log_text is not None:
        payload = parse_check_log(check_log_text)
    elif stats:
        payload = dict(stats)
        if "verdict" not in payload:
            ok = bool(payload.get("mesh_ok"))
            payload["verdict"] = "clean" if ok else "broken"
    else:
        return None
    if payload.get("cells") in (None, 0):
        # Every real checkMesh log states its cell count. A payload without
        # one is a failed or absent check, and a failed check must never
        # mint a clean certificate.
        return None
    certificate = {
        "points_sha256": digest,
        "verdict": payload.get("verdict"),
        "cells": payload.get("cells"),
        "max_aspect_ratio": payload.get("max_aspect_ratio"),
        "max_non_orthogonality": payload.get("max_non_orthogonality"),
        "max_skewness": payload.get("max_skewness"),
        "hard_errors": payload.get("hard_errors", []),
        "generator": generator,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (mesh_root / CERTIFICATE_NAME).write_text(
        json.dumps(certificate, indent=1), encoding="utf-8")
    return certificate


def read_certificate(mesh_root: Path) -> dict[str, Any] | None:
    path = Path(mesh_root) / CERTIFICATE_NAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def certificate_admits(mesh_root: Path) -> tuple[bool, str]:
    """Whether the mesh under ``mesh_root`` may enter a case.

    True only when a certificate exists, its hash matches the points file
    that is actually there, and its verdict is in ``ACCEPTED_VERDICTS``.
    The reason string states which condition failed, so a refusal is a
    stated finding rather than a silent miss.
    """
    certificate = read_certificate(mesh_root)
    if certificate is None:
        return False, ("no birth certificate beside the mesh; quarantined "
                       "until checkMesh is run and attached (Verification "
                       "Charter v1.5 section 9)")
    digest = points_sha256(Path(mesh_root) / "polyMesh")
    if digest is None:
        return False, "no points file under the mesh directory"
    if certificate.get("points_sha256") != digest:
        return False, ("certificate hash does not match the mesh beside it; "
                       "the certificate belongs to a different mesh")
    verdict = str(certificate.get("verdict") or "")
    if verdict not in ACCEPTED_VERDICTS:
        errors = ", ".join(certificate.get("hard_errors") or []) or "unstated"
        return False, (f"born {verdict or 'unverified'}: {errors}; the mesh "
                       f"does not enter (charter section 9)")
    return True, verdict
