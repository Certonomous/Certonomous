#!/usr/bin/env python3
"""ONE skew model, both directions, so two checks cannot fight.

Two instruments in this lab compare a hand-written in-record timestamp against a
machine timestamp, and they look in OPPOSITE directions:

  STALE direction   `scripts/check_harness.py` freshness gate -- is a board
                    section OLDER than the work it describes? Its fallback path
                    compares a hand-typed stamp against a territory commit and
                    allows the stamp to be up to STALE_TOLERANCE_S seconds EARLY
                    before calling it stale. That tolerance was paid for by
                    `bd3edfe8` (2026-08-22T21:00:24Z), which graded freshness
                    against a hand-typed clock and called every correct team
                    stale: a section stamped 20:55Z whose commit landed at
                    20:56:27 read as older than its own territory.

  AHEAD direction   `scripts/check_stamp_vs_commit.py` -- is a stamp written
                    AHEAD of the wall clock, i.e. LATER than the committer date
                    of the commit that introduced the line carrying it? That is
                    the second face of the same `bd3edfe8` defect class, and it
                    fired three times on 2026-08-23 (closure's board, the
                    verification board's 21:35/21:40Z stamps, and the D473
                    docket row).

The two numbers are DIFFERENT because the two mechanisms are different, and that
difference is the whole reason this module exists rather than one constant:

  * STALE_TOLERANCE_S = 600 s is a DISPLAY-RESOLUTION allowance on a FALLBACK
    path. It is the chief's number, kept exactly as specified in bd3edfe8, and
    this module does not redefine it -- it IMPORTS it from check_harness.py,
    which remains its single definition. If that import ever fails this module
    REFUSES rather than inventing a second 600.

  * FORWARD_TOLERANCE_S = 60 s is a MECHANISM BOUND, not a taste. Only one
    mechanism can put an honest stamp after its own committer date: the writer
    reads `date -u`, then rounds the minute UP when typing (clock says 20:04:54,
    stamp reads 20:05Z). The read must precede the commit, so the stamp can lead
    the committer date by AT MOST the rounding, and rounding up to the next whole
    minute is bounded by 60 s. Note that the slow-CAS-retry story runs the OTHER
    way: a retry re-runs `commit-tree` and pushes the committer date LATER, which
    makes the delta more negative, never more positive. 60 s is therefore an
    upper bound on the benign class, not a guess at one.

MEASURED, 2026-08-24, over the added corpus lines of the last 300 commits
(`git log -n 300`, added lines only, so the introducing commit is exact and no
blame heuristic enters): 400 UTC-marked stamps graded, 76 with a positive delta.
The benign cluster is 4 rows at +6, +6, +49, +49 s -- all minute-rounding, all
inside 60 s. The next value up is +70 s, and every row from +70 s upward falls
either in the 2026-08-22/23 window the board has itself disclosed as
estimated-rather-than-read stamps, or in the future-intent (ETA) class this
model excludes by cue rather than by tolerance. There is no benign row between
60 s and 70 s to split, so the mechanism bound and the data agree.

Both constants are exposed here so that `check_harness.py` can adopt this module
later without either number moving. Until it does, the stale tolerance has
exactly one definition (in check_harness.py) and the forward tolerance has
exactly one definition (here).
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


class SkewModelUnavailable(RuntimeError):
    """The stale tolerance could not be read from its single definition.

    Raised rather than defaulted. A default here would be a SECOND definition of
    the number, which is the exact failure this module exists to prevent.
    """


def _stale_tolerance():
    try:
        import check_harness
    except Exception as exc:                       # pragma: no cover - refusal path
        raise SkewModelUnavailable(
            "cannot import scripts/check_harness.py to read STAMP_TOLERANCE_S: %s. "
            "REFUSING to substitute a second copy of the stale tolerance -- repair "
            "the import so the two checks share one skew model." % exc)
    try:
        return int(check_harness.STAMP_TOLERANCE_S)
    except AttributeError:
        raise SkewModelUnavailable(
            "scripts/check_harness.py no longer defines STAMP_TOLERANCE_S. The skew "
            "model has moved; REFUSING to invent a replacement value. Repair this "
            "import (or move the constant into this module and have check_harness "
            "import it back) so the two checks cannot fight.")


#: Stale direction, seconds. Imported, never redefined -- see module docstring.
STALE_TOLERANCE_S = _stale_tolerance()

#: Ahead direction, seconds. Mechanism bound (minute-rounding), see docstring.
FORWARD_TOLERANCE_S = 60


def ahead_verdict(stamp_t, commit_t):
    """Is this stamp written AHEAD of the commit that introduced its line?

    Pure function of two epochs, so the planted controls exercise it without a
    repository. Returns ``(status, delta_seconds)`` with status ``"ahead"`` or
    ``"ok"``; delta is ``stamp - committer_date``, positive when the stamp leads.

    The comparison is STRICTLY greater than the tolerance: a stamp exactly
    FORWARD_TOLERANCE_S seconds ahead is the extreme of the benign
    minute-rounding class and is not a fire.
    """
    delta = stamp_t - commit_t
    if delta > FORWARD_TOLERANCE_S:
        return "ahead", delta
    return "ok", delta


def stale_verdict(stamp_t, work_t):
    """Mirror of the check_harness.py fallback, in this module's vocabulary.

    Provided so the stale side of the model is readable here beside the ahead
    side. `check_harness.py` still owns the live freshness decision; this is not
    a second implementation of that gate, it is the same comparison exposed for
    inspection and for the shared selftest.
    """
    if stamp_t >= work_t - STALE_TOLERANCE_S:
        return "ok", stamp_t - work_t
    return "stale", stamp_t - work_t


if __name__ == "__main__":
    print("skew model, one source of truth for two directions")
    print("  STALE_TOLERANCE_S   = %d s  (imported from check_harness.py)"
          % STALE_TOLERANCE_S)
    print("  FORWARD_TOLERANCE_S = %d s  (mechanism bound, measured 2026-08-24)"
          % FORWARD_TOLERANCE_S)
