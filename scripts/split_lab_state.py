#!/usr/bin/env python3
"""split_lab_state.py -- split the monolith docs/LAB_STATE.md into per-team sources.

The one-shot MIGRATION half of the V-119 board-source cutover (owner-approved
2026-09-10); the exact inverse of scripts/assemble_lab_state.py.  Splitting the
current board at its six team headers and concatenating the pieces reproduces the
board BYTE-FOR-BYTE -- that identity is asserted here and is the losslessness proof.

It reads docs/LAB_STATE.md (stripping a leading generated BANNER if present, so it
is idempotent on an already-assembled board), splits at the SIX EXACT team headers
(an allowlist -- never at an arbitrary '## ', of which the preamble and sections
have many), and writes the sources:

    00_preamble.md   (everything before '## closure' -- the title + CHIEF directives)
    10_closure.md    20_dafoam.md   30_heat-transfer.md
    40_cfd.md        50_verification.md   60_ansys-verification.md

REFUSES (exit 2) if any team header is missing, appears more than once, or the
headers are out of order, or if the reconstruction identity concat(sources)==input
fails -- it never writes a partial/lossy split.

Usage:
  split_lab_state.py [--repo R] [--out-dir D] [--selftest]
    default --out-dir is <repo>/docs/lab_state/ .  Point --out-dir at a scratch dir
    to split WITHOUT touching the live tree (the Phase-1 round-trip does exactly this).

Exit codes: 0 ok / 2 refuse / 3 selftest plant did not fire (main only).

Diff-read by the verification-supervisor before its output is believed
(SUPERVISION §3 check 1); writes only under --out-dir.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile

EXIT_OK, EXIT_REFUSE, EXIT_VIOLATION = 0, 2, 3

# import the banner + assembler so the two halves cannot drift apart
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble_lab_state import BANNER, OUT_RELPATH  # noqa: E402

# (team-header-bytes, source-filename) in canonical order.
TEAMS: list[tuple[bytes, str]] = [
    (b"## closure", "10_closure.md"),
    (b"## dafoam", "20_dafoam.md"),
    (b"## heat-transfer", "30_heat-transfer.md"),
    (b"## cfd", "40_cfd.md"),
    (b"## verification", "50_verification.md"),
    (b"## ansys-verification", "60_ansys-verification.md"),
]
PREAMBLE_NAME = "00_preamble.md"


def repo_default() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _strip_banner(data: bytes) -> bytes:
    return data[len(BANNER):] if data.startswith(BANNER) else data


def split_bytes(data: bytes) -> tuple[list[tuple[str, bytes]], str | None]:
    """Return ([(filename, bytes), ...] for preamble + 6 teams, error_or_None).
    The pieces concatenate back to `data` (after banner strip) exactly."""
    data = _strip_banner(data)
    lines = data.splitlines(keepends=True)

    # locate each team header line (exact whole-line match, allowlist only)
    idx: list[int] = []
    for header, _name in TEAMS:
        hits = [i for i, ln in enumerate(lines) if ln.rstrip(b"\r\n") == header]
        if len(hits) == 0:
            return [], f"team header {header.decode()!r} not found"
        if len(hits) > 1:
            return [], f"team header {header.decode()!r} appears {len(hits)} times (must be exactly once)"
        idx.append(hits[0])

    if idx != sorted(idx):
        return [], f"team headers out of canonical order: line indices {idx}"

    pieces: list[tuple[str, bytes]] = []
    pieces.append((PREAMBLE_NAME, b"".join(lines[:idx[0]])))
    for k, (_h, name) in enumerate(TEAMS):
        start = idx[k]
        end = idx[k + 1] if k + 1 < len(TEAMS) else len(lines)
        pieces.append((name, b"".join(lines[start:end])))

    # RECONSTRUCTION IDENTITY -- the losslessness guarantee, asserted not assumed
    if b"".join(b for _n, b in pieces) != data:
        return [], "reconstruction identity failed: concat(sources) != input (banner-stripped)"
    return pieces, None


def run_split(repo: str, out_dir: str) -> tuple[int, str]:
    src = os.path.join(repo, OUT_RELPATH)
    if not os.path.exists(src):
        return EXIT_REFUSE, f"REFUSE: {OUT_RELPATH} not found under {repo}"
    with open(src, "rb") as f:
        data = f.read()
    pieces, err = split_bytes(data)
    if err:
        return EXIT_REFUSE, f"REFUSE: {err}"
    os.makedirs(out_dir, exist_ok=True)
    for name, content in pieces:
        with open(os.path.join(out_dir, name), "wb") as f:
            f.write(content)
    total = sum(len(b) for _n, b in pieces)
    return EXIT_OK, (f"wrote {len(pieces)} sources to {out_dir} "
                     f"({total} bytes; concat==input verified)")


# --------------------------------------------------------------------------
# selftest -- the reconstruction identity, both a good board and a broken one
# --------------------------------------------------------------------------
def selftest() -> bool:
    print("=" * 78)
    print("SPLIT SELFTEST -- reconstruction identity + refusal on a malformed board.")
    print("=" * 78)
    ok = True

    def result(label: str, good: bool):
        nonlocal ok
        ok = ok and good
        print(f"  {label:56s} {'PASS' if good else 'FAIL'}")

    # a synthetic well-formed monolith (preamble + 6 team sections, with decoy '## ')
    good = (b"# LAB_STATE\n## CHIEF directives\n## not-a-team decoy\n"
            b"## closure\nc-body\n### sub\n"
            b"## dafoam\nd-body\n"
            b"## heat-transfer\nh-body\n"
            b"## cfd\nf-body\n"
            b"## verification\nv-body\n## another decoy inside\n"
            b"## ansys-verification\na-body\n")
    pieces, err = split_bytes(good)
    result("ARM1 well-formed board splits (no error)", err is None)
    if pieces:
        recon = b"".join(b for _n, b in pieces)
        result("ARM2 concat(sources) == input (lossless)", recon == good)
        names = [n for n, _b in pieces]
        result("ARM3 seven pieces, canonical names",
               names == ["00_preamble.md", "10_closure.md", "20_dafoam.md",
                         "30_heat-transfer.md", "40_cfd.md", "50_verification.md",
                         "60_ansys-verification.md"])
        pre = dict(pieces)["00_preamble.md"]
        result("ARM4 decoy '## ' stays inside its section (preamble keeps its decoy)",
               b"## not-a-team decoy" in pre and b"c-body" not in pre)

    # banner idempotency: a board that already carries the banner strips it
    pieces2, err2 = split_bytes(BANNER + good)
    result("ARM5 leading BANNER stripped (idempotent)",
           err2 is None and b"".join(b for _n, b in pieces2) == good)

    # RED: a missing team header refuses
    missing = good.replace(b"## cfd\nf-body\n", b"")
    _p, err3 = split_bytes(missing)
    result("ARM6 missing team header -> REFUSE", err3 is not None)

    # RED: a duplicated team header refuses
    dup = good + b"## closure\nsecond one\n"
    _p, err4 = split_bytes(dup)
    result("ARM7 duplicated team header -> REFUSE", err4 is not None)

    print("=" * 78)
    print("SELFTEST: PASS" if ok else "SELFTEST: FAIL")
    print("=" * 78)
    return ok


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=repo_default())
    ap.add_argument("--out-dir", default=None,
                    help="where to write sources (default <repo>/docs/lab_state/)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return EXIT_OK if selftest() else EXIT_VIOLATION

    out_dir = args.out_dir or os.path.join(args.repo, "docs", "lab_state")
    code, line = run_split(args.repo, out_dir)
    print(line, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
