#!/usr/bin/env python3
"""V-119 MIGRATION -- cut docs/LAB_STATE.md into one file per writer, and REFUSE
unless the cut is byte-identical to the committed board.

Spec: docs/BOARD_MIGRATION_PROPOSAL.md, sections 2, 3, 4 and 4.1. Direction
approved by Sanaa 2026-09-03 ruling 5 and again this session ("V-119 approved");
the mechanics below are that document's, not this file's inventions.

What it does
  1. reads the board from `git show <rev>:docs/LAB_STATE.md` -- the COMMITTED
     blob, never the worktree (CLAUDE.md rule 10 / L-223: the shared worktree
     copy carries other teams' uncommitted section edits);
  2. enumerates every `## ` heading from that blob -- NO hardcoded team list, so
     an eighth team appearing on the board cannot be silently dropped;
  3. cuts each section with the PRODUCTION splitter's own `split(text, team)`
     from scripts/lab_state_section.py -- imported, not reimplemented. Proposal
     s4: "the bytes are cut by the same code the lab has been trusting to cut
     them for two weeks" (VERIFICATION_CHARTER s2p.3(d): a control that drives a
     COPY of the guarded logic tests nothing);
  4. emits the preamble -- everything before the first `## `, which has no
     heading and therefore no owner -- as the generator's header template
     docs/LAB_STATE_HEADER.md (proposal s4);
  5. emits FLAT docs/LAB_STATE_<TEAM>.md files (proposal s6 Q2 recommendation:
     flat needs no filing-rule amendment; check_filing.py's UPPER_SNAKE_MD
     regex `^[A-Z0-9][A-Z0-9_-]*\\.md$` admits the hyphen in HEAT-TRANSFER);
  6. THE ABORT CONDITION, which is the whole evidentiary content of this script:
     header + every section in ORIGINAL ORDER, encoded utf-8, is compared
     byte-for-byte against the raw bytes of `git show <rev>:<path>`. A mismatch
     writes NOTHING and exits non-zero. Proposal s4: "Non-zero cmp aborts the
     migration."

--plant-corrupt is the PLANTED NEGATIVE CONTROL (charter s2o): it flips one byte
of one section IN MEMORY, after the cut and before the comparison, and so drives
the production abort path with a known-bad input. A byte-identity check that has
only ever been shown to pass is not evidence.

Empty input is a REFUSAL (proposal s3, limb `s2p.2`): zero sections found means
the reader is broken or the board is empty, and emitting nothing quietly is the
worst output this tool can produce.

WHAT THIS SCRIPT DOES NOT DO, deliberately:
  - it never writes docs/LAB_STATE.md and never commits. The caller does the
    private-index sequence, the CAS and the post-commit verify (CLAUDE.md r10).
  - proposal s4.1: the split is by LINE BOUNDARY and it does not adjudicate the
    disputed second `UPDATE V-33`/`V-34` pair near the `## ansys-verification`
    boundary. --report-disputed prints which file that pair lands in and how many
    lines it is, so the migration commit message can NAME it. A migration is not
    a venue for deciding whose record something is.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_state_section import split  # PRODUCTION splitter -- proposal s4

HEADER_NAME = "LAB_STATE_HEADER.md"
FILENAME_OK = re.compile(r"^[A-Z0-9][A-Z0-9_-]*$")


def committed_bytes(repo: str, rev: str, path: str) -> bytes:
    """The COMMITTED blob, raw. Never the worktree."""
    return subprocess.check_output(["git", "-C", repo, "show", f"{rev}:{path}"])


def headings(text: str) -> list[str]:
    """Every `## ` heading, in file order, as the EXACT string split() must match.

    split() matches `^## {re.escape(team)}\\s*$`, so the token handed to it is the
    heading text with trailing whitespace stripped -- including chief's
    `CHIEF - standing directives in force`, which is a heading, not a bare word.
    """
    return [m.group(1).rstrip() for m in re.finditer(r"^## (.*?)[ \t]*$", text, flags=re.M)]


def team_key(heading: str) -> str:
    """Filename token for a heading.

    The board's chief section is `## CHIEF -- standing directives in force`; the
    proposal names its file docs/LAB_STATE_CHIEF.md. So the key is the heading
    truncated at the first em/en-dash separator, uppercased, hyphen preserved
    (proposal s2 lists LAB_STATE_HEAT_TRANSFER.md with an underscore; this build
    preserves the roster's own hyphen -- see the REPORTED DIVERGENCE note in the
    lane report. Both forms satisfy check_filing.py R2).
    """
    key = re.split(r"\s+[—–-]\s+", heading, maxsplit=1)[0].strip()
    key = key.upper().replace(" ", "_")
    if not FILENAME_OK.match(key):
        raise SystemExit(
            f"REFUSED: heading `## {heading}` yields filename token {key!r}, which is not "
            f"UPPER_SNAKE per check_filing.py R2 -- refusing to invent a name")
    return key


def cut(blob_text: str):
    """Cut every section with the production splitter. Returns (header, [(heading, key, text)])."""
    heads = headings(blob_text)
    if not heads:
        raise SystemExit("REFUSED: zero `## ` sections found in the committed board -- "
                         "empty input is a refusal, never an empty emission (proposal s3, s2p.2)")
    header = split(blob_text, heads[0])[0]
    out = []
    seen = set()
    for h in heads:
        key = team_key(h)
        if key in seen:
            raise SystemExit(f"REFUSED: two sections map to the same file token {key!r}")
        seen.add(key)
        out.append((h, key, split(blob_text, h)[1]))
    return header, out


def identity(raw: bytes, header: str, sections) -> tuple[bool, bytes]:
    rebuilt = (header + "".join(s[2] for s in sections)).encode("utf-8")
    return rebuilt == raw, rebuilt


def find_disputed(header: str, sections):
    """Proposal s4.1 -- locate the second `UPDATE V-33`/`V-34` pair, report, never rule."""
    pat = re.compile(r"^(#+)[ \t]+.*\bUPDATE V-3[34]\b.*$", flags=re.M)
    hits = []
    for name, text in [(HEADER_NAME, header)] + [(f"LAB_STATE_{k}.md", t) for _, k, t in sections]:
        lines = text.splitlines(True)
        starts = [(text[:m.start()].count("\n"), len(m.group(1)), m.group(0).strip())
                  for m in pat.finditer(text)]
        heads = [i for i, ln in enumerate(lines) if re.match(r"^#+[ \t]", ln)]
        for ln, lvl, title in starts:
            nxt = next((h for h in heads if h > ln), len(lines))
            hits.append((name, ln + 1, nxt - ln, title))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description="V-119 board migration -- cut, prove byte-identity, emit.")
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--path", default="docs/LAB_STATE.md")
    ap.add_argument("--outdir", default=None,
                    help="where the per-team files go; default <repo>/docs. Use a scratch dir to test.")
    ap.add_argument("--write", action="store_true",
                    help="actually emit files. WITHOUT THIS THE SCRIPT IS A DRY RUN.")
    ap.add_argument("--dry-run", action="store_true", help="explicit no-op default; kept for symmetry")
    ap.add_argument("--plant-corrupt", action="store_true",
                    help="PLANTED NEGATIVE CONTROL: flip one byte of one section in memory and prove the abort fires")
    ap.add_argument("--report-disputed", action="store_true",
                    help="proposal s4.1: name where the disputed UPDATE V-33/V-34 blocks landed")
    a = ap.parse_args()

    raw = committed_bytes(a.repo, a.rev, a.path)
    text = raw.decode("utf-8")
    header, sections = cut(text)

    print(f"lab_state_split.py -- V-119 migration, spec docs/BOARD_MIGRATION_PROPOSAL.md")
    print(f"  source           : {a.rev}:{a.path}  ({len(raw)} bytes, {text.count(chr(10))} newlines)")
    print(f"  splitter         : lab_state_section.split(text, team)  [PRODUCTION, imported]")
    print(f"  sections found   : {len(sections)}  (enumerated from the file, not hardcoded)")
    print(f"  header template  : {HEADER_NAME}  {len(header.encode('utf-8'))} bytes, "
          f"{header.count(chr(10))} lines  (no `## ` heading -- no owner, proposal s4)")
    for h, k, t in sections:
        print(f"    ## {h[:44]:<44} -> LAB_STATE_{k}.md  "
              f"{len(t.encode('utf-8')):>8} bytes  {t.count(chr(10)):>6} lines")

    if a.plant_corrupt:
        h, k, t = sections[0]
        i = len(t) // 2
        bad = t[:i] + ("X" if t[i] != "X" else "Y") + t[i + 1:]
        sections = [(h, k, bad)] + sections[1:]
        print(f"  PLANTED          : one byte flipped in LAB_STATE_{k}.md at offset {i} "
              f"({t[i]!r} -> {bad[i]!r}) -- the abort MUST fire")

    ok, rebuilt = identity(raw, header, sections)
    print("  BYTE IDENTITY    : header + %d sections, original order" % len(sections))
    print(f"    committed blob : {len(raw)} bytes  sha256 {hashlib.sha256(raw).hexdigest()[:16]}")
    print(f"    rebuilt        : {len(rebuilt)} bytes  sha256 {hashlib.sha256(rebuilt).hexdigest()[:16]}")
    print(f"    delta          : {len(rebuilt) - len(raw):+d} bytes")
    if not ok:
        d = next((i for i in range(min(len(raw), len(rebuilt))) if raw[i] != rebuilt[i]), min(len(raw), len(rebuilt)))
        print(f"    first differing byte offset: {d}")
        print("VERDICT: ABORTED -- the cut is NOT byte-identical to the committed board.")
        print("NOTHING WRITTEN. A migration that cannot show it moved nothing is not finished "
              "(proposal s4, charter s2p.6.2).")
        return 3
    print("    result         : IDENTICAL (0 differing bytes)")

    if a.report_disputed:
        print("  DISPUTED PAIR (proposal s4.1 -- REPORTED, NOT ADJUDICATED):")
        hits = find_disputed(header, sections)
        if not hits:
            print("    no `UPDATE V-33`/`V-34` heading matched")
        for name, ln, span, title in hits:
            print(f"    {name}  line {ln}  {span} lines  |  {title[:90]}")

    outdir = a.outdir or os.path.join(a.repo, "docs")
    if not a.write:
        print(f"  --dry-run (default): nothing written. Would emit {len(sections) + 1} files under {outdir}")
        print("VERDICT: OK -- byte-identity PROVEN, no files written. Pass --write to emit.")
        return 0

    os.makedirs(outdir, exist_ok=True)
    paths = []
    for name, body in [(HEADER_NAME, header)] + [(f"LAB_STATE_{k}.md", t) for _, k, t in sections]:
        p = os.path.join(outdir, name)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(body)
        paths.append(p)
        print(f"  written          : {p}")
    print("VERDICT: OK -- %d files written, byte-identity proven BEFORE the write." % len(paths))
    print("CANNOT SEE: any commit. The private-index sequence, the CAS and the post-commit verify "
          "remain the caller's (CLAUDE.md rule 10). The disputed V-33/V-34 pair must be NAMED in "
          "the commit message and adjudicated separately (proposal s4.1).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
