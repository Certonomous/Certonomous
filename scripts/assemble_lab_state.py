#!/usr/bin/env python3
"""assemble_lab_state.py -- assemble docs/LAB_STATE.md from per-team sources.

THE V-119 BOARD-SOURCE CUTOVER (owner-approved 2026-09-10).  The resume board
docs/LAB_STATE.md was one ~41k-line monolith that all six teams wrote to
concurrently; the shared file bloated into 13k-token megalines and every write
staged the WHOLE file, so a commit could sweep another team's in-flight edit.
After the cutover each team's section is its OWN source file under
docs/lab_state/, and docs/LAB_STATE.md is a GENERATED artifact = a banner + the
byte concatenation of the sources in sorted-filename order.

Sources are ONLY files matching docs/lab_state/[0-9][0-9]_*.md (a strict numeric
prefix fixes the assembly order and excludes README/design docs living alongside):

    00_preamble.md   10_closure.md   20_dafoam.md   30_heat-transfer.md
    40_cfd.md        50_verification.md   60_ansys-verification.md

WRITE PROTOCOL (the point of the cutover): a team edits ONLY its own source, runs
this script, and commits BOTH its source and docs/LAB_STATE.md under the rule-10
private-index protocol.  Because each team commits only its own source, no team's
committed work can be clobbered; docs/LAB_STATE.md is derived and self-heals on the
next assembly.

ASSEMBLY IS PURE BYTE CONCATENATION -- no separators are inserted, so
split_lab_state.py is an exact inverse: concat(sources) reproduces the pre-cutover
board byte-for-byte (the losslessness proof), and the only delta the cutover makes
to docs/LAB_STATE.md is the one-line BANNER prepended at the top.

Modes:
  (default)     write docs/LAB_STATE.md = BANNER + concat(sources)
  --stdout      write the assembled bytes to stdout instead of the file
  --no-banner   assemble WITHOUT the banner (used by the losslessness round-trip:
                concat(sources) must equal the pre-cutover board byte-for-byte)
  --check       assemble fresh and compare to the on-disk docs/LAB_STATE.md;
                exit 2 if they differ (a team edited its source but forgot to
                reassemble, or edited the generated file directly)
  --selftest    planted-content readback in a throwaway tempdir; exit 3 if the
                plant does not fire

Exit codes: 0 ok / 2 refuse (no sources, or --check drift) / 3 selftest plant
did not fire (main only).

This file is diff-read by the verification-supervisor before its output is
believed (SUPERVISION §3 check 1); it writes nothing outside docs/LAB_STATE.md
(default mode) or its own scratch fixture tree (--selftest).
"""

from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
import tempfile

EXIT_OK, EXIT_REFUSE, EXIT_VIOLATION = 0, 2, 3

# The single-line generated banner (bytes) + one blank line.  split_lab_state.py
# strips exactly this leading block so the sources never accumulate banners.
BANNER = (
    b"<!-- GENERATED FILE -- edit your team's source docs/lab_state/<NN>_<team>.md, "
    b"then run scripts/assemble_lab_state.py and commit BOTH (rule-10 private-index). "
    b"Do NOT edit docs/LAB_STATE.md directly. "
    b"Design: docs/LAB_STATE_CUTOVER_DESIGN.md -->\n\n"
)

SRC_GLOB = os.path.join("docs", "lab_state", "[0-9][0-9]_*.md")
OUT_RELPATH = os.path.join("docs", "LAB_STATE.md")


def repo_default() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def source_files(repo: str) -> list[str]:
    """The per-team source files, in sorted-filename (== assembly) order.  Only
    the strict [0-9][0-9]_*.md pattern; README/design docs are excluded."""
    return sorted(glob.glob(os.path.join(repo, SRC_GLOB)))


def assemble_bytes(repo: str, banner: bool = True) -> bytes:
    files = source_files(repo)
    if not files:
        raise FileNotFoundError(f"no sources match {os.path.join(repo, SRC_GLOB)}")
    body = b"".join(_read_bytes(f) for f in files)
    return (BANNER + body) if banner else body


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def run_check(repo: str) -> tuple[int, str]:
    out = os.path.join(repo, OUT_RELPATH)
    if not os.path.exists(out):
        return EXIT_REFUSE, f"REFUSE: {OUT_RELPATH} does not exist to check against"
    try:
        fresh = assemble_bytes(repo, banner=True)
    except FileNotFoundError as e:
        return EXIT_REFUSE, f"REFUSE: {e}"
    on_disk = _read_bytes(out)
    if fresh == on_disk:
        n = len(source_files(repo))
        return EXIT_OK, f"CHECK OK: {OUT_RELPATH} == fresh assembly of {n} sources ({len(on_disk)} bytes)"
    return EXIT_REFUSE, (
        f"REFUSE: {OUT_RELPATH} DRIFTED from its sources "
        f"(on-disk {len(on_disk)} bytes != fresh {len(fresh)} bytes) -- "
        f"a source was edited without reassembling, or the generated file was edited directly"
    )


# --------------------------------------------------------------------------
# selftest -- planted-content readback (rule 3)
# --------------------------------------------------------------------------
def selftest() -> bool:
    print("=" * 78)
    print("PLANTED-CONTENT READBACK -- assemble is the exact inverse of split.")
    print("A readback that cannot distinguish a mutated source is worthless.")
    print("=" * 78)
    me = os.path.abspath(__file__)
    tmp = tempfile.mkdtemp(prefix="assemble_lab_state_plant_")
    ok = True

    def result(label: str, good: bool):
        nonlocal ok
        ok = ok and good
        print(f"  {label:56s} {'PASS' if good else 'FAIL'}")

    try:
        srcdir = os.path.join(tmp, "docs", "lab_state")
        os.makedirs(srcdir)
        sentinels = {
            "00_preamble.md": b"PREAMBLE-SENTINEL-alpha\n# board\n",
            "10_closure.md": b"## closure\nCLOSURE-SENTINEL-beta\n",
            "20_dafoam.md": b"## dafoam\nDAFOAM-SENTINEL-gamma\n",
        }
        for name, content in sentinels.items():
            with open(os.path.join(srcdir, name), "wb") as f:
                f.write(content)
        expected_body = b"".join(sentinels[n] for n in sorted(sentinels))

        # ARM 1: --no-banner assembly == byte concatenation of the sources
        got = subprocess.run(
            [sys.executable, me, "--repo", tmp, "--no-banner", "--stdout"],
            capture_output=True)
        result("ARM1 --no-banner == concat(sources)", got.stdout == expected_body)

        # ARM 2: default assembly == BANNER + concat, and every sentinel survives
        got = subprocess.run(
            [sys.executable, me, "--repo", tmp, "--stdout"], capture_output=True)
        arm2 = (got.stdout == BANNER + expected_body
                and all(s in got.stdout for s in
                        (b"PREAMBLE-SENTINEL-alpha", b"CLOSURE-SENTINEL-beta",
                         b"DAFOAM-SENTINEL-gamma")))
        result("ARM2 default == BANNER+concat, all sentinels present", arm2)

        # ARM 3 (load-bearing): mutate one source -> the readback MUST change
        with open(os.path.join(srcdir, "20_dafoam.md"), "wb") as f:
            f.write(b"## dafoam\nDAFOAM-SENTINEL-MUTATED\n")
        got2 = subprocess.run(
            [sys.executable, me, "--repo", tmp, "--no-banner", "--stdout"],
            capture_output=True)
        result("ARM3 a mutated source flips the readback (load-bearing)",
               got2.stdout != expected_body and b"DAFOAM-SENTINEL-MUTATED" in got2.stdout)

        # ARM 4: --check flips RED when the generated file drifts, GREEN when in sync
        out = os.path.join(tmp, "docs", "LAB_STATE.md")
        # write an in-sync generated file, then --check must be GREEN (exit 0)
        subprocess.run([sys.executable, me, "--repo", tmp], check=False)  # writes docs/LAB_STATE.md
        green = subprocess.run([sys.executable, me, "--repo", tmp, "--check"],
                               capture_output=True)
        # now corrupt the generated file -> --check must be RED (exit 2)
        with open(out, "ab") as f:
            f.write(b"HAND-EDITED-DRIFT\n")
        red = subprocess.run([sys.executable, me, "--repo", tmp, "--check"],
                             capture_output=True)
        result("ARM4 --check GREEN in-sync (0) / RED on drift (2)",
               green.returncode == EXIT_OK and red.returncode == EXIT_REFUSE)

        # ARM 5: no sources -> REFUSE (fail-closed, never a silent empty board)
        empty = os.path.join(tmp, "empty")
        os.makedirs(os.path.join(empty, "docs", "lab_state"))
        none = subprocess.run([sys.executable, me, "--repo", empty, "--stdout"],
                              capture_output=True)
        result("ARM5 no sources -> REFUSE (exit 2)", none.returncode == EXIT_REFUSE)

        print("=" * 78)
        print("SELFTEST: PASS" if ok else "SELFTEST: FAIL")
        print("=" * 78)
        return ok
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=repo_default(), help="repo root (default: two levels up)")
    ap.add_argument("--stdout", action="store_true", help="write assembled bytes to stdout")
    ap.add_argument("--no-banner", action="store_true", help="assemble without the banner")
    ap.add_argument("--check", action="store_true",
                    help="compare a fresh assembly to on-disk docs/LAB_STATE.md; exit 2 on drift")
    ap.add_argument("--selftest", action="store_true", help="planted-content readback; exit 3 if it does not fire")
    args = ap.parse_args(argv)

    if args.selftest:
        return EXIT_OK if selftest() else EXIT_VIOLATION

    if args.check:
        code, line = run_check(args.repo)
        print(line, file=sys.stderr)
        return code

    try:
        data = assemble_bytes(args.repo, banner=not args.no_banner)
    except FileNotFoundError as e:
        print(f"REFUSE: {e}", file=sys.stderr)
        return EXIT_REFUSE

    if args.stdout:
        sys.stdout.buffer.write(data)
        return EXIT_OK

    out = os.path.join(args.repo, OUT_RELPATH)
    with open(out, "wb") as f:
        f.write(data)
    print(f"wrote {OUT_RELPATH} ({len(data)} bytes) from {len(source_files(args.repo))} sources",
          file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
