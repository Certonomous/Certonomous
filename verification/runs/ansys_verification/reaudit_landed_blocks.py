#!/usr/bin/env python3
"""PERIODIC CONTENT-EXTENT RE-AUDIT of this team's landed blocks against HEAD.

WHY THIS EXISTS, and why it is NOT another guard.  Every guard in the
private-index protocol is WRITE-TIME: the anchor assert, the byte-prefix proof,
the heading-list check, the unchanged-tree guard.  A post-commit verify on paths
and line counts is STRUCTURALLY BLIND to displacement, because THE DAMAGE LANDS
IN SOMEBODY ELSE'S COMMIT, NOT IN YOURS.  Measured 2026-08-25: this team's
L-314 Addendum 2 was committed correctly inside L-314 and verified at the time,
and a later repair reinserted a peer's heading AHEAD of it, orphaning it inside
another team's lesson.  Every write-time guard had passed.

The remedy, from the cfd team and adopted here: compare THIS TEAM'S OWN COMMITTED
BYTES against HEAD, periodically.  A landed block must be an IDENTICAL PREFIX of
the same block at HEAD -- growth only, nothing displaced.

METHOD NOTE, paid for the same day: compare BYTES, not characters.  A block of
6,165 characters is 6,191 bytes when it holds 13 em-dashes, and reporting the
character count as a byte count manufactures a 26-byte discrepancy out of
identical content.  And an extent defined "to the next heading" is not the same
extent as "to EOF": a block that was last when it landed gains a trailing blank
line once a successor arrives, so compare PREFIXES, never sizes.

usage: reaudit_landed_blocks.py [--selftest]
"""
import subprocess, sys, re, hashlib

REPO = "/home/ubuntu/Certonomous"
EXIT_OK, EXIT_REFUSE = 0, 2

# file, block-opener regex, ids this team landed
TARGETS = [
    ("docs/LESSONS.md",            r"^## (L-\d+)\b",
     ["L-308", "L-312", "L-313", "L-314", "L-316", "L-317", "L-318"]),  # post-renumber ids (06f3578e)
    ("docs/NUMERICS_KNOWLEDGE.md", r"^#+ *(N-AV\d+)\b",
     ["N-AV1","N-AV2","N-AV3","N-AV4","N-AV5","N-AV6","N-AV7","N-AV8","N-AV9"]),
]
# single-row ledgers: the row IS the block
ROWS = [
    ("docs/COST_CALIBRATION.md", r"^\| \*{0,2}(C-\d+)\*{0,2} \|", ["C-45","C-47","C-51"]),
]

def sh(a): return subprocess.check_output(a, cwd=REPO, text=True)

def first_commit_with(path, ident, opener):
    """Earliest commit whose blob contains this block opener."""
    revs = sh(["git","log","--format=%H","--reverse","--",path]).split()
    pat = re.compile(opener, re.M)
    for r in revs:
        try: t = sh(["git","show",f"{r}:{path}"])
        except subprocess.CalledProcessError: continue
        if any(m.group(1)==ident for m in pat.finditer(t)): return r
    return None

def extract(rev, path, opener, ident):
    t = sh(["git","show",f"{rev}:{path}"])
    ms = list(re.compile(opener, re.M).finditer(t))
    for i,m in enumerate(ms):
        if m.group(1)==ident:
            end = ms[i+1].start() if i+1<len(ms) else len(t)
            return t[m.start():end]
    return None

# ids REASSIGNED by the 06f3578e renumber: pin to the commit that landed them
# under their CURRENT id, or the audit compares two different lessons that merely
# share a number.  An id that changes meaning is a CITATION HAZARD, not just a
# bookkeeping detail -- every record citing the old number now points elsewhere.
LANDED = {"L-316": "06f3578e", "L-317": "06f3578e", "L-318": "06f3578e"}


def audit():
    bad, checked = [], 0
    for path, opener, idents in TARGETS + ROWS:
        for ident in idents:
            src = LANDED.get(ident) or first_commit_with(path, ident, opener)
            if src is None:
                bad.append((ident, path, "NOT FOUND in any commit")); continue
            a = extract(src, path, opener, ident)
            b = extract("HEAD", path, opener, ident)
            checked += 1
            if b is None:
                bad.append((ident, path, f"MISSING at HEAD (landed {src[:8]})")); continue
            ab, bb = a.encode(), b.encode()          # BYTES, never characters
            if not bb.startswith(ab.rstrip(b"\n")):
                bad.append((ident, path,
                    f"DISPLACED or ALTERED: landed {src[:8]} ({len(ab)}B, "
                    f"sha {hashlib.sha256(ab).hexdigest()[:12]}) is not a prefix at HEAD "
                    f"({len(bb)}B, sha {hashlib.sha256(bb).hexdigest()[:12]})"))
            else:
                print(f"  OK   {ident:8} {path.split('/')[-1]:28} landed {src[:8]} "
                      f"{len(ab):6}B -> HEAD {len(bb):6}B (prefix holds)")
    print(f"\n  {checked} landed block(s) re-audited against HEAD")
    if bad:
        for i,p,w in bad: print(f"  REFUSED  {i} in {p}: {w}")
        return EXIT_REFUSE
    print("  ALL LANDED BLOCKS INTACT: each is an identical byte-prefix at HEAD")
    return EXIT_OK

def selftest():
    """Both arms, per L-314 and its Addendum 2: each must fail FOR ITS OWN REASON."""
    res=[]
    def arm(name, got, want, kind):
        res.append((got==want, name, kind, f"got {got!r}"))
    base=b"## L-1 title\nbody\n"
    arm("prefix/GOOD", (base+b"more\n").startswith(base.rstrip(b"\n")), True, "GOOD-input")
    arm("prefix/BAD-altered", b"## L-1 TITLE\nbody\nmore\n".startswith(base.rstrip(b"\n")), False, "BAD-input")
    arm("prefix/BAD-truncated", b"## L-1 tit".startswith(base.rstrip(b"\n")), False, "BAD-input")
    # the measured char-vs-byte trap
    s="a—b"
    arm("bytes-not-chars/GOOD", len(s.encode())!=len(s), True, "GOOD-input")
    arm("bytes-not-chars/BAD", len(s)==len(s.encode()), False, "BAD-input")
    w=max(len(n) for _,n,_,_ in res)
    for ok,n,k,note in res: print(f"  {'PASS' if ok else 'FAIL':4}  {n:<{w}}  {k:<10} {note}")
    fams={}
    for _,n,k,_ in res: fams.setdefault(n.split("/")[0],set()).add(k)
    miss=[f for f,ks in fams.items() if {"GOOD-input","BAD-input"}-ks]
    if miss: print(f"  REFUSED: no both-arm coverage for {miss}"); return EXIT_REFUSE
    if any(not ok for ok,_,_,_ in res): print("  REFUSED: an arm failed"); return EXIT_REFUSE
    print("  SYMMETRY HELD PER GUARD")
    return EXIT_OK

if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else audit())
