#!/usr/bin/env python3
"""ONE-TIME MIGRATION: split docs/LAB_STATE.md into the per-team sources it will be
merged back from. Lossless, and the losslessness is MACHINE-CHECKED, not claimed.

Sanaa's PLUMBING FREEZE directive, 2026-08-31: "Boards become per-team files (one
writer each), merged into the lab board by a nightly tool -- no shared-file splicing
by agents, ever."

WHAT LOSSLESS MEANS HERE, precisely, because a vaguer claim is worthless:

    concat(docs/lab_state/chief.md, closure.md, dafoam.md, heat-transfer.md,
           cfd.md, verification.md, ansys-verification.md)
        ==  the whole of the source board, byte for byte,
            including its preamble, every blank line and its trailing newline.

Not "the same sections". Not "the same content". The same BYTES, in the same order,
with nothing added between them. The merged board is that concatenation with the
generated-file header prepended, so:

    merged  ==  HEADER + original_board_bytes                  (at migration time)

which is checked by --verify below and is the strongest form the claim can take:
the merger reproduces the board it was migrated from, exactly, plus a header that
says it is generated.

THIS SCRIPT NEVER WRITES docs/LAB_STATE.md AND NEVER DELETES IT. The board is the
only handoff channel between sessions (L-186) and six supervisors are writing it.
Migration is additive; cutover is a separate, human, later act.
"""

import argparse
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_state_sources as M  # noqa: E402

H2_LINE = re.compile(rb"^## .*$", re.M)
NL = b"\n"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def cut(raw):
    """Split the board bytes at every line-anchored '## '.

    Returns [(heading_text, section_bytes), ...] with the PROLOGUE carried as the
    first element under heading None. Every byte of `raw` lands in exactly one
    element; that is asserted before returning, not assumed.
    """
    marks = [(m.start(), m.group().decode("utf-8")) for m in H2_LINE.finditer(raw)]
    if not marks:
        raise SystemExit("REFUSE: no '## ' heading in the source board")
    out = []
    if marks[0][0] > 0:
        out.append((None, raw[: marks[0][0]]))
    for i, (start, head) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(raw)
        out.append((head, raw[start:end]))
    assert b"".join(s for _, s in out) == raw, "cut() lost bytes"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default=os.path.join(M.REPO, M.BOARD_REL),
                    help="the board to split (default: the worktree copy)")
    ap.add_argument("--out-dir", default=os.path.join(M.REPO, M.SRC_DIR_REL))
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing source files (a RE-SPLIT at cutover time)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    raw = open(a.board, "rb").read()
    print(f"source board : {a.board}")
    print(f"  bytes      : {len(raw)}")
    print(f"  sha256     : {sha(raw)}")

    parts = cut(raw)
    heads = [h for h, _ in parts]
    print(f"  '## ' heads : {len([h for h in heads if h])}")

    expected = M.order()
    # prologue + chief section fuse into chief.md; the six teams follow, in order.
    if heads[0] is not None:
        raise SystemExit("REFUSE: the board starts with a '## ' heading; no preamble "
                         "to give the chief's file")
    if heads[1] != M.CHIEF_HEADING:
        raise SystemExit(f"REFUSE: first section is {heads[1]!r}, expected "
                         f"{M.CHIEF_HEADING!r}")
    got_teams = heads[2:]
    want_teams = [h for _, _, h in expected[1:]]
    if got_teams != want_teams:
        raise SystemExit(f"REFUSE: team sections/order differ.\n  found : {got_teams}\n"
                         f"  want  : {want_teams}")

    files = [(expected[0][0], parts[0][1] + parts[1][1])]
    for i, (stem, _o, _h) in enumerate(expected[1:]):
        files.append((stem, parts[2 + i][1]))

    # --- the losslessness assertion, before anything is written -------------
    concat = b"".join(b for _, b in files)
    ok = concat == raw
    print("\nLOSSLESS SPLIT CHECK (in memory, before any write)")
    print(f"  concat bytes : {len(concat)}   source bytes : {len(raw)}"
          f"   delta {len(concat) - len(raw)}")
    print(f"  concat sha   : {sha(concat)}")
    print(f"  source sha   : {sha(raw)}")
    print(f"  byte-for-byte identical : {ok}")
    if not ok:
        raise SystemExit("REFUSE: split is NOT lossless; nothing written")

    print("\nper-file")
    for stem, b in files:
        print(f"  {stem+'.md':<26} {len(b):>9} bytes  {sha(b)[:16]}  "
              f"{b.count(NL):>6} lines")

    # --- THE MERGER'S OWN VALIDATOR, IN MEMORY, BEFORE ANY WRITE.
    # This check used to run AFTER the files were written, which meant that
    # splitting an input the merger would reject -- a MERGED board, for instance,
    # whose header carries the generated marker -- exited non-zero having already
    # left seven files on disk. Measured 2026-08-31: rc 1 with 7 files written.
    # A refusal that has already written is not a refusal.
    print("\nMERGER VALIDATION (in memory, before any write)")
    mem = dict(files)
    for stem, _o, head in expected:
        try:
            w = M.validate(stem, head, mem[stem], f"<in-memory {stem}.md>")
            print(f"  {stem+'.md':<26} OK" + (f"   warn: {w}" if w else ""))
        except M.Malformed as e:
            raise SystemExit(f"REFUSE: this board does not split into sources the "
                             f"merger would accept, so NOTHING WAS WRITTEN: {e}")

    if a.dry_run:
        print("\n--dry-run: nothing written")
        return 0

    os.makedirs(a.out_dir, exist_ok=True)
    existing = [s for s, _ in files
                if os.path.exists(os.path.join(a.out_dir, s + ".md"))]
    if existing and not a.force:
        raise SystemExit(f"REFUSE: sources already exist ({existing}); pass --force "
                         f"only if you mean to re-split over them")

    for stem, b in files:
        p = os.path.join(a.out_dir, stem + ".md")
        tmp = p + ".tmp"
        with open(tmp, "wb") as f:
            f.write(b)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, p)

    # --- read BACK from disk and re-assert. The in-memory check above proves the
    # arithmetic; this one proves the FILES ON DISK are the thing that was proved.
    back = b"".join(open(os.path.join(a.out_dir, s + ".md"), "rb").read()
                    for s, _ in files)
    print("\nLOSSLESS SPLIT CHECK (re-read from disk)")
    print(f"  disk concat bytes : {len(back)}   source bytes : {len(raw)}")
    print(f"  disk concat sha   : {sha(back)}")
    print(f"  byte-for-byte identical : {back == raw}")
    if back != raw:
        raise SystemExit("REFUSE: files on disk do not reproduce the board")

    # --- and re-run the validator against the bytes ON DISK. The in-memory pass
    # above is what decides whether to write; this one proves the FILES THAT EXIST
    # are the ones that were graded, so a migration cannot hand the merger something
    # it will refuse tonight.
    print("\nMERGER VALIDATION of the written sources (re-read from disk)")
    for stem, _o, head in expected:
        p = os.path.join(a.out_dir, stem + ".md")
        try:
            w = M.validate(stem, head, open(p, "rb").read(), p)
            print(f"  {stem+'.md':<26} OK" + (f"   warn: {w}" if w else ""))
        except M.Malformed as e:
            raise SystemExit(f"REFUSE: written source fails the merger's validator: {e}")

    print(f"\nboard NOT modified: {a.board} untouched, {len(raw)} bytes, sha {sha(raw)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
