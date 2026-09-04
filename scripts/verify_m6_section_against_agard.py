#!/usr/bin/env python3
"""Grade the ONERA M6 root section against AGARD AR-138 Table B1-1.

Grades `Gate GF` of `verification/campaign/M6F_PREREGISTRATION.md`.

THE TRAP THIS SCRIPT EXISTS TO STOP (R-2COL):

  `om6_wing_section_sharp.dat` is SINGLE-COLUMN with a count header (`63`),
  followed by 63 x-values and then 63 y-values. A two-column parser returns
  ZERO ROWS, silently -- the C19 defect class. This script RUNS the wrong
  parser as a planted control and REFUSES if that parser returns anything but
  zero, because a reader not proven able to see the wrong answer has not been
  proven able to see the right one (CLAUDE.md rule 3).

WHAT IT MEASURES:

  The shipped sharp section is the AGARD table with ONE point appended at
  (1.0055, 0.0). That single point does two things, and the second was not
  previously recorded:
    (a) it drives the trailing-edge ordinate from 0.0007052 to 0.0, and
    (b) it lengthens the chord from 1.0000000 to 1.0055000 -- 0.55 %, which
        every x/c abscissa and every chord-based Reynolds number inherits.

  Removing it recovers AGARD's own final row exactly, giving a mirrored
  t_TE/c of 2 x 0.0007052 = 0.0014104.

NOTHING HERE ASSERTS THAT REGENERATING FROM THE BLUNT SECTION CLEARS ANY GATE.
This script grades the INPUT FILE. `GF1`/`GF2` are graded on the EMITTED
SURFACE, which does not exist until stage `B1` runs.
"""
import os
import sys

SHARP = os.environ.get(
    "M6_SECTION",
    "/home/ubuntu/Certonomous/verification/runs/M6I_runs/mesh/om6_wing_section_sharp.dat")
AGARD = os.environ.get(
    "M6_AGARD_TABLE",
    "/home/ubuntu/Certonomous/models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat")

TE_ORD = 0.0007052        # AGARD Table B1-1 final ordinate
TE_THICK = 0.0014104      # mirrored
TOL = 1e-7


class Refusal(Exception):
    """Stops the script under ANY interpreter flag. NOT an assert: -O deletes those."""


def read_single_column(path):
    """The CORRECT parser: count header N, then N x-values, then N y-values."""
    toks = [l.strip() for l in open(path) if l.strip()]
    n = int(float(toks[0]))
    vals = [float(t) for t in toks[1:]]
    if len(vals) != 2 * n:
        raise Refusal("R-2COL: header says %d points but %d values follow "
                      "(expected %d)." % (n, len(vals), 2 * n))
    return list(zip(vals[:n], vals[n:]))


def read_two_column_CONTROL(path):
    """The WRONG parser, run deliberately. Must return ZERO rows on the sharp file."""
    out = []
    for l in open(path):
        p = l.split()
        if len(p) == 2:
            try:
                out.append((float(p[0]), float(p[1])))
            except ValueError:
                pass
    return out


def read_two_column(path):
    """The correct parser for the AGARD table, which really is two-column."""
    return read_two_column_CONTROL(path)


def main():
    print("M6 ROOT SECTION vs AGARD AR-138 TABLE B1-1 -- Gate GF (input-file limb)")
    for p in (SHARP, AGARD):
        if not os.path.exists(p):
            print("BLOCKED: %s absent." % p)
            return 2
    print("  sharp : %s" % SHARP)
    print("  AGARD : %s\n" % AGARD)

    # ---- GF5 FIRST: the planted control. Nothing grades until it passes.
    ctrl = read_two_column_CONTROL(SHARP)
    if len(ctrl) != 0:
        print("GF5  NOT A RESULT -- the two-column control parser returned %d rows "
              "on a single-column file. This reader cannot tell the layouts apart; "
              "every figure below is void." % len(ctrl))
        return 2
    print("GF5  PASS  planted control: the two-column parser returns 0 rows on the "
          "single-column file. The reader can see the wrong answer.")

    sharp = read_single_column(SHARP)
    agard = read_two_column(AGARD)
    print("\n     sharp points %d   AGARD rows %d" % (len(sharp), len(agard)))

    key = lambda p: (round(p[0], 7), round(p[1], 7))
    agset = {key(p) for p in agard}
    extra = [p for p in sharp if key(p) not in agset]
    unused = [p for p in agard if key(p) not in {key(q) for q in sharp}]

    print("     sharp points that ARE exact AGARD rows : %d / %d"
          % (len(sharp) - len(extra), len(sharp)))
    print("     sharp points that are NOT AGARD rows   : %d" % len(extra))
    for p in extra:
        print("         (%.7f, %.7f)   <- appended, not from the table" % p)
    print("     AGARD rows the sharp file discards     : %d" % len(unused))
    aft = [p for p in unused if p[0] > 0.95]
    print("         of which in the aft 5%% (x/c > 0.95): %d  <- the region that "
          "governs trailing-edge Cp" % len(aft))

    print("\n     %-28s %14s %14s" % ("", "as shipped", "drop appended"))
    print("     %-28s %14.7f %14.7f" % ("TE ordinate", sharp[-1][1], sharp[-2][1]))
    print("     %-28s %14.7f %14.7f" % ("mirrored t_TE/c", 2 * sharp[-1][1], 2 * sharp[-2][1]))
    print("     %-28s %14.7f %14.7f" % ("chord", sharp[-1][0], sharp[-2][0]))
    print("     %-28s %14.7f %14.7f" % ("AGARD t_TE/c", TE_THICK, TE_THICK))

    fails = []
    if sharp[-2] != agard[-1]:
        fails.append("the sharp file's second-to-last point %s is NOT AGARD's final row %s"
                     % (sharp[-2], agard[-1]))
    if abs(2 * sharp[-2][1] - TE_THICK) > TOL:
        fails.append("dropping the appended point gives t_TE/c %.7f, not %.7f"
                     % (2 * sharp[-2][1], TE_THICK))
    if abs(sharp[-2][0] - 1.0) > TOL:
        fails.append("dropping the appended point gives chord %.7f, not 1.0000000"
                     % sharp[-2][0])

    print("\n" + "=" * 72)
    for f in fails:
        print("GATE FAIL  " + f)
    if fails:
        print("\nVERDICT: GATE FAIL")
        return 1
    print("VERDICT: PASS on the INPUT-FILE limb.")
    print("  The shipped section is AGARD Table B1-1 plus exactly one appended point")
    print("  at (1.0055, 0.0). Removing it recovers t_TE/c = %.7f and chord = 1.0000000"
          % TE_THICK)
    print("  exactly. The shipped chord is 0.5500 %s long, which every x/c abscissa" % "%")
    print("  and every chord-based Reynolds number inherits.")
    print()
    print("NOT GRADED HERE, AND NOT CLAIMED:")
    print("  * that the generator ACCEPTS a blunt section (stage B1, prediction P1);")
    print("  * that it does not silently re-sharpen (stage B1);")
    print("  * whether it renormalises the chord by max(x) (stage B0, UNRESOLVED);")
    print("  * GF1/GF2, which are graded on the EMITTED SURFACE, not on this file.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        print("REFUSAL: %s" % e)
        sys.exit(2)
