#!/usr/bin/env python3
"""REFUSE a y+ reading that is identically zero on every patch.

WHY THIS EXISTS.  On OpenFOAM v2606 build _481094f-20260618 the generic
``postProcess -func yPlus`` returns ``min = 0, max = 0, average = 0`` on EVERY
patch, exits 0 and prints ``End``, while ``<solver> -postProcess -func yPlus``
on the SAME case, same time and same fields returns a real field.  Measured
independently three times in this lab:

  * 2026-09-03, heat-transfer, verification/runs/T-family/T5_runs/
    YPLUS_RECOVERABILITY_2026-09-03/README.md  (paired live control, 0 core-min)
  * 2026-09-12, cfd, verification/campaign/DRIVAER_SOLVED_YPLUS_2026-09-12.md
    (52/52 patches zero on both arms; caught by a CRM positive control)
  * 2026-09-13, cfd, 53/53 patch readings zero across two different solvers

The canonical minimal reproduction is already on disk and needs no rebuild:
/home/ubuntu/certonomous-runs/validation-scratch/motorBike/log.yPlus, 68/68 zero.

MECHANISM -- TWO ROUTES, BOTH REAL, AND THE LAB'S OWN RECORDS DISAGREED UNTIL A
CONTROL SEPARATED THEM:
  (a) the generic ``postProcess`` binary does not construct the solver's
      turbulence model, so no wall function exists to report its y+;
  (b) a model whose wall treatment has no y+ of its own (nutLowReWallFunction)
      prints zero even under the solver spelling -- see the comment at
      verification/runs/F14-cooling-ladder/K0cT_runs/analyse_k0ct.py:541.
Route (a) is the operative one for wall-function cases: a CRM case that HAS wall
functions still returned zero under the generic binary, which route (b) cannot
explain.

THIS IS NOT AN UPSTREAM DEFECT REPORT.  Whether (a) is a bug or documented
behaviour of ``postProcess`` has NOT been researched.  Nothing here is filed,
sent or reported outside this box (standing rule 7).

WHAT THIS MODULE IS FOR.  CLAUDE.md rule 3: a zero from a reader not shown able
to see a non-zero is not evidence.  This guard is the reader-side half of that.
It REFUSES (raises) rather than degrading, and it never returns a softened
verdict -- the caller decides what to do with the refusal, but it cannot get a
number out of this module that the module believes is fabricated.
"""
import os
import re

__all__ = ["YPlusReaderBlind", "parse_yplus_log", "assert_yplus_reader_not_blind"]

# "    patch hull y+ : min = 0.28644688, max = 342.84922, average = 50.095863"
_PATCH_RE = re.compile(
    r"^\s*patch\s+(\S+)\s+y\+\s*:\s*min\s*=\s*(\S+?),\s*max\s*=\s*(\S+?),"
    r"\s*average\s*=\s*(\S+?)\s*$")
# "Exec   : postProcess -func yPlus -time 2000"          <- generic, the blind one
# "Exec   : simpleFoam -postProcess -func yPlus -time 2000"  <- solver spelling
_EXEC_RE = re.compile(r"^Exec\s*:\s*(\S+)(.*)$")


class YPlusReaderBlind(Exception):
    """The y+ reader produced no evidence.  Never caught to substitute a default."""


def parse_yplus_log(path):
    """Return (readings, exec_binary, exec_args).

    readings is a list of (patch, y_min, y_max, y_avg).  Raises YPlusReaderBlind
    if the file holds no patch line at all -- a reader that read nothing is as
    blind as one that read zero, and silently returning [] would let a caller
    conclude 'no wall patches, gate not applicable'.
    """
    if not os.path.isfile(path):
        raise YPlusReaderBlind("no such y+ log: %s" % path)
    readings, binary, args = [], None, ""
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            m = _EXEC_RE.match(line)
            if m and binary is None:
                binary, args = os.path.basename(m.group(1)), m.group(2)
            m = _PATCH_RE.match(line)
            if m:
                readings.append((m.group(1), float(m.group(2)),
                                 float(m.group(3)), float(m.group(4))))
    if not readings:
        raise YPlusReaderBlind(
            "%s: no 'patch <name> y+ : min = ... ' line found. The reader "
            "produced NO reading; an empty result is not 'no wall patches'."
            % path)
    return readings, binary, args


def assert_yplus_reader_not_blind(readings, source="<unknown>", binary=None,
                                  args=""):
    """REFUSE unless this reading is admissible evidence.  Returns None or raises.

    Two independent refusals, deliberately not folded into one:

    1. ALL-ZERO.  Every patch reporting max == 0.0 exactly is the defect's
       signature.  A physically zero y+ everywhere would need identically zero
       wall shear on every wall, which no solved case has; and even if it did,
       refusing is correct -- the caller must then say so explicitly rather than
       have a gate read a fabricated zero.

    2. SPELLING.  If the log names the generic ``postProcess`` binary, refuse
       even when the numbers are non-zero.  This is the stronger check and it
       fires BEFORE the numbers are looked at, because a reader that happens to
       return non-zero from a blind invocation is worse than one that returns
       zero: it cannot be spotted by its output.
    """
    if binary is not None and binary == "postProcess":
        raise YPlusReaderBlind(
            "%s: produced by the GENERIC 'postProcess%s'. That binary does not "
            "construct the solver's turbulence model and reports y+ = 0 on every "
            "patch. Re-run as '<solver> -postProcess -func yPlus' on the same "
            "case, time and fields." % (source, args))
    n_zero_max = sum(1 for _, _, ymax, _ in readings if ymax == 0.0)
    if n_zero_max == len(readings):
        raise YPlusReaderBlind(
            "%s: y+ max == 0 on ALL %d patch readings. A zero from a reader not "
            "shown able to see a non-zero is not evidence (CLAUDE.md rule 3). "
            "Drive the same reader against a case with known non-zero y+ before "
            "believing any zero it returns." % (source, len(readings)))
    return None
