#!/usr/bin/env python3
"""PLANTED FIXTURE for `age_truncation_census.py` -- CLAUDE.md rule 3.

This module is DATA, not a library.  It emits thirteen small source files into a
directory: EIGHT POSITIVES, each a different route to a floored timestamp, and
SIX NEGATIVES that must NOT be flagged.  The census refuses to report anything
until it has emitted these, read them back off disk, and scored 8/8 and 0/6.

WHY EIGHT AND SIX, AND WHY THESE.  `pos2` and `pos5` are here because the census
MISSED THEM on its first run.  They are the pure read-back idiom -- the floor is
on the READ and the only thing marking the value as a timestamp is the NAME IT IS
BOUND TO -- and that idiom turned out to be 22 of the real sites in this family.
The negatives are here because a census that manufactures defects is worse than
one that misses them: `neg1`/`neg2`/`neg3` are the CORRECT full-precision forms,
`neg4` is a wall-clock deadline loop that is not a file-age guard at all, and
`neg5` is a ROUND rather than a floor -- which does not move a datum earlier and
therefore does not relax a guard.
"""
import os

POSITIVES = {
    # (1) the floor inline on the datum
    "pos1.py": """import os
def g(f, ref):
    datum = int(os.path.getmtime(ref))
    return os.path.getmtime(f) > datum
""",
    # (2) READ-BACK.  The census MISSED THIS ON ITS FIRST RUN.  The floor happened
    #     upstream, possibly in another file; only the NAME says it is a timestamp.
    "pos2.py": """import os
def g(f, p):
    datum = int(open(p).read().strip())
    return os.path.getmtime(f) > datum
""",
    # (3) math.floor rather than int
    "pos3.py": """import os, math
def g(f, ref):
    d = math.floor(os.path.getmtime(ref))
    return os.path.getmtime(f) >= d
""",
    # (4) BOTH sides floored
    "pos4.py": """import os
def g(f, ref):
    return int(os.path.getmtime(f)) < int(os.path.getmtime(ref))
""",
    # (5) the WRITE/READ pair, floor at serialisation.  ALSO MISSED ON THE FIRST RUN.
    "pos5.py": """import os
def w(p, ref):
    open(p, "w").write("%d\\n" % os.path.getmtime(ref))
def g(f, p):
    datum = int(open(p).read().strip())
    return os.path.getmtime(f) <= datum
""",
    # (8) st_mtime through int()
    "pos8.py": """import os
class C:
    def chk(self, f, ref):
        datum = int(os.stat(ref).st_mtime)
        return os.stat(f).st_mtime > datum
""",
}

POSITIVES_SH = {
    # (6) the W3S launcher's own pre-repair shape
    "pos6.sh": """AGE_DATUM=$(stat -c '%Y' "$SENTINEL")
find "$D" -type f -newermt "@$AGE_DATUM"
""",
    # (7) both sides through `stat -c %Y`
    "pos7.sh": """AGE_DATUM=$(stat -c '%Y' "$SENTINEL")
M=$(stat -c '%Y' "$F")
[ "$M" -le "$AGE_DATUM" ] || exit 5
""",
}

NEGATIVES = {
    # the CORRECT form: full precision on both sides
    "neg1.py": """import os
def g(f, ref):
    t0 = os.path.getmtime(ref)
    return os.path.getmtime(f) > t0
""",
    # st_mtime_ns is integer NANOSECONDS -- the MOST precise form, not a truncation.
    # An earlier census read this as a floor and was wrong.
    "neg2.py": """import os
def g(f, ref):
    return os.stat(f).st_mtime_ns > os.stat(ref).st_mtime_ns
""",
    # a wall-clock DEADLINE, not a file-age guard
    "neg4.py": """import time
def wait(deadline):
    while time.time() < int(deadline):
        pass
""",
    # a ROUND is not a FLOOR: it does not move the datum earlier, so it does not
    # relax the guard.  Flagging it would misstate the mechanism.
    "neg5.py": """import os
def g(f, ref):
    return round(os.path.getmtime(f)) > os.path.getmtime(ref)
""",
    # THE SHAPE THAT PRODUCED FAILURE 1(b).  Two functions, each with a local
    # `mt`.  The FIRST floors it; the SECOND is clean, full precision on both
    # sides.  A census that resolves names MODULE-WIDE gives the second `mt` the
    # first one's provenance and flags a correct guard -- which is exactly how
    # `analyse_f28.py`, a clean file, was accused of six truncations.
    "neg6.py": """import os
def stamp(ref):
    mt = int(os.path.getmtime(ref))
    return mt
def guard(f, ref):
    mt = os.path.getmtime(f)
    t0 = os.path.getmtime(ref)
    return mt > t0
""",
}

NEGATIVES_SH = {
    # the repair: full-precision comparison against the sentinel FILE
    "neg3.sh": """find "$D" -type f -newer "$SENTINEL"
""",
}


def emit(d):
    """Write the fixture to `d`.  Returns (positive_names, negative_names)."""
    os.makedirs(d, exist_ok=True)
    for name, src in list(POSITIVES.items()) + list(POSITIVES_SH.items()) + \
            list(NEGATIVES.items()) + list(NEGATIVES_SH.items()):
        with open(os.path.join(d, name), "w") as fh:
            fh.write(src)
    pos = sorted(list(POSITIVES) + list(POSITIVES_SH))
    neg = sorted(list(NEGATIVES) + list(NEGATIVES_SH))
    return pos, neg
