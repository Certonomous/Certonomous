#!/usr/bin/env python3
"""Mint birth certificates for meshes the 2026-08-08 audit found CHECKED but
never CERTIFIED.

WHY THIS EXISTS. The audit marked 105 meshes `CERTIFIED (pre-existing
record)`, and a later coverage check found all 105 carry a `log.checkMesh`
and **zero** carry a `birth_certificate.json`. The evidence exists; the
artifact never did. `mesh_certificate.certificate_admits()` requires the file,
a `points_sha256` that matches the mesh actually present, and an accepted
verdict -- so all 105 were quarantined from new work, which is exactly what
happened unprompted to two M6 members and two retrofit ladders. The word in
the audit named an artifact nobody had written.

WHAT THIS DOES NOT DO. It does not re-judge a mesh. The audit's BORN CLEAN
findings stand; this writes the artifact its own evidence already supports.

THE CROSS-CHECK IS THE POINT. A retrospective certificate is weaker than one
minted at creation: the log was found later, and nothing inherently binds it
to the points file on disk now. So every mint must pass BOTH:

  * the log parses to a real checkMesh record (a cell count, a verdict);
  * the log's cell count equals the mesh's OWN `nCells`, read from the
    polyMesh `owner` header.

The second is what stops a certificate drifting onto a different mesh -- the
failure mode the hash binding exists to prevent, reappearing in the act of
back-filling it. A mesh that fails either is REPORTED, never papered over: the
tally of exceptions is the real result of this pass.

Usage:
    python3 scripts/mint_retrospective_certificates.py            # dry run
    python3 scripts/mint_retrospective_certificates.py --write
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "sdk"))
from chief_engineer import mesh_certificate  # noqa: E402

AUDIT = (REPO / "demo-output" / "website" / "campaign"
         / "MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md")
MARK = "CERTIFIED (pre-existing record)"
ROOTS = (Path("/home/ubuntu/certonomous-runs"), Path("/home/ubuntu"))

# Both spellings the audit uses: `log.checkMesh` and `<tag>_checkMesh.log`.
_EVIDENCE = re.compile(r"\(([^()]*(?:log\.checkMesh|checkMesh\.log|"
                       r"[A-Za-z0-9_]*_checkMesh\.log))")
_NCELLS = re.compile(r"nCells:\s*(\d+)")


def audit_rows() -> list[tuple[str, str | None]]:
    rows = []
    for line in AUDIT.read_text(errors="replace").splitlines():
        if MARK not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        hit = _EVIDENCE.search(cells[3])
        rows.append((cells[0].strip("`"), hit.group(1) if hit else None))
    return rows


def resolve(rel: str | None) -> Path | None:
    if not rel:
        return None
    for root in ROOTS:
        candidate = root / rel
        if candidate.exists():
            return candidate
    return None


def mesh_ncells(polymesh: Path) -> int | None:
    """The mesh's OWN cell count, from the polyMesh `owner` header note."""
    for name in ("owner", "owner.gz"):
        path = polymesh / name
        if not path.exists():
            continue
        try:
            if name.endswith(".gz"):
                import gzip
                head = gzip.open(path, "rt", errors="replace").read(2000)
            else:
                head = path.read_text(errors="replace")[:2000]
        except OSError:
            return None
        hit = _NCELLS.search(head)
        return int(hit.group(1)) if hit else None
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="actually write certificates (default: dry run)")
    args = ap.parse_args()

    classes: dict[str, list[str]] = {}

    def record(kind: str, detail: str) -> None:
        classes.setdefault(kind, []).append(detail)

    for mesh_rel, log_rel in audit_rows():
        polymesh = resolve(mesh_rel)
        log_path = resolve(log_rel)
        if polymesh is None:
            record("mesh directory absent", f"{mesh_rel}")
            continue
        if log_path is None:
            record("checkMesh log not on disk", f"{mesh_rel} (cited {log_rel})")
            continue
        existing = mesh_certificate.read_certificate(polymesh.parent)
        if existing is not None:
            record("already certified (left alone)", mesh_rel)
            continue
        text = log_path.read_text(errors="replace")
        parsed = mesh_certificate.parse_check_log(text)
        if not parsed.get("cells"):
            record("log does not parse to a checkMesh record",
                   f"{mesh_rel} (from {log_rel})")
            continue
        own = mesh_ncells(polymesh)
        if own is None:
            record("mesh states no cell count of its own", mesh_rel)
            continue
        if own != parsed["cells"]:
            record("CROSS-CHECK FAILED: log describes a different mesh",
                   f"{mesh_rel}: mesh has {own} cells, "
                   f"{log_rel} reports {parsed['cells']}")
            continue
        if mesh_certificate.points_sha256(polymesh) is None:
            record("no points file to hash-bind", mesh_rel)
            continue
        verdict = parsed.get("verdict")
        if verdict not in mesh_certificate.ACCEPTED_VERDICTS:
            # The audit classed this row CERTIFIED, and the log the audit
            # itself cites parses to hard errors under the audit's OWN verdict
            # rule. That is a discrepancy for the audit's owner to rule on,
            # not for this pass to settle by writing a file: minting a
            # `broken` certificate would quarantine another family's mesh on
            # the strength of a parser. Not minting changes nothing -- an
            # absent certificate already quarantines it -- so the conservative
            # action and the honest one are the same action here.
            record(f"DISCREPANCY: audit says CERTIFIED, its own cited log "
                   f"parses {verdict}",
                   f"{mesh_rel}: {', '.join(parsed.get('hard_errors') or [])}"
                   f" (log {log_rel})")
            continue
        if not args.write:
            record(f"WOULD MINT ({verdict})", mesh_rel)
            continue
        cert = mesh_certificate.write_certificate(
            polymesh.parent, check_log_text=text,
            generator=f"retrospective mint from {log_rel}; "
                      f"MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md row",
            provenance=mesh_certificate.PROVENANCE_RETROSPECTIVE,
            evidence={
                "check_log": str(log_path),
                "check_log_mtime": datetime.fromtimestamp(
                    log_path.stat().st_mtime, timezone.utc
                ).isoformat(timespec="seconds"),
                "points_mtime": datetime.fromtimestamp(
                    (polymesh / "points").stat().st_mtime, timezone.utc
                ).isoformat(timespec="seconds")
                if (polymesh / "points").exists() else None,
                "cell_count_cross_check": {
                    "mesh_own_nCells": own, "log_cells": parsed["cells"],
                    "agree": True},
                "audit": "MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md",
            })
        record("MINTED" if cert else "write_certificate declined", mesh_rel)

    total = sum(len(v) for v in classes.values())
    print(f"{'WROTE' if args.write else 'DRY RUN'} over {total} audit rows\n")
    for kind in sorted(classes):
        rows = classes[kind]
        print(f"{len(rows):4d}  {kind}")
        if "FAIL" in kind or "DISCREPANCY" in kind or "absent" in kind or "not on disk" in kind \
                or "does not parse" in kind or "declined" in kind \
                or "no points" in kind or "no cell count" in kind:
            for r in rows:
                print(f"        - {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
