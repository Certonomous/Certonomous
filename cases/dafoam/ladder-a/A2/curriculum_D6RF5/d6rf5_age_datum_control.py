#!/usr/bin/env python3
"""D6RF5 -- THE CONTROL ON THE AGE-DATUM STAGING GUARD.

WHY THIS FILE EXISTS
====================
`W3S` was killed by its age-staging guard, and **zero of that item's 53 controls
exercised the age-staging guard at all**.  The guard that decided the run had no
control in its own instrument, so a `53/53` green suite said nothing about it.
This file is that missing control for `D6RF5`, and it is written to be able to
FAIL: `--drive` runs it against a DELIBERATELY DEFECTIVE launcher and REQUIRES
the refusal.  A control that has never been shown to fail is not a control
(`CLAUDE.md` rule 3).

WHAT IT GUARDS, AND WHAT IT DOES NOT
====================================
It guards ONE line -- the production of the age datum in `d6rf5_run_arm.sh` --
and the two call sites that consume it.  It is **not** a solver check and
**nothing here is a result about the A2 wing**: every input is a file this
script creates, and it burns 0.000 solver core-minutes.

THE LINE IS EXTRACTED FROM THE LAUNCHER, NOT COPIED INTO HERE
============================================================
`datum_command()` reads `d6rf5_run_arm.sh` and pulls out its actual
`AGE_DATUM=$(stat -c '...' ...)` line, ASSERTING that exactly one such line
exists.  A control that carried its own copy of the command would keep passing
after the launcher drifted -- which is precisely how a guard goes stale without
anybody noticing.  If the launcher changes, this control changes with it or
refuses.

THE FOUR ROWS
=============
Rows are driven on REAL mtimes set with nanosecond `os.utime`, never on a
synthetic pair.  (`d6rf5_grade_drive.py` writes its fixture datum as
`now - 100.0`; a 100-SECOND gap cannot see a defect whose window is at most
1.000 s wide, which is why that drive stayed green over this defect.)

  A  sentinel + 1 ns                -> truth NEWER.  Reported as a RESOLUTION
                                       MEASUREMENT: the consumers read `float`
                                       seconds, and a double at epoch magnitude
                                       cannot hold 1 ns.  This row measures the
                                       real floor rather than asserting one.
  A' sentinel + (measured epsilon)  -> truth NEWER  -> guard must ACCEPT.
  B  sentinel - 300 ms, SAME whole  -> truth OLDER  -> guard must REFUSE.
     second as the sentinel            THIS IS THE DISCRIMINATING ROW.
  C  rows A'/B against the DEFECTIVE launcher -> row B must FLIP to ACCEPT and
     this control must REFUSE.

DIRECTION.  `D6RF5`'s defect is FAIL-**OPEN**, not fail-closed.  `stat -c '%Y'`
floors the datum EARLIER than the sentinel; both consumers accept on
`mt > datum`; so a product written in the same second as `0/U` but GENUINELY
OLDER was accepted as this arm's.  (W3S's was the other way round -- a generated
`controlDict` 121 ms newer than its sentinel was wrongly REFUSED.  Same floor,
opposite sense, because the sense is set by the operator and by which side is
truncated, never by the floor alone.)

CLASS.  Every artefact the two consumers guard is **STAGED/GENERATED** -- the
six `REGISTERED_PRODUCTS["P_conv"]` JSON files written by Python wrappers, and
C3's `SCALED_OUT`/`HISTORY`, written by the frozen extractor.  None is
solver-produced.  That is the class that can actually be bitten.

Usage:
    python3 d6rf5_age_datum_control.py            # the four rows
    python3 d6rf5_age_datum_control.py --drive    # + the defective-launcher drive
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LAUNCHER = os.path.join(HERE, "d6rf5_run_arm.sh")

# The launcher's own line, matched not reproduced.
DATUM_LINE = re.compile(r'^AGE_DATUM=\$\(stat -c \'([^\']+)\' "\$AGE_SRC"\)$', re.M)


class Refusal(RuntimeError):
    pass


def datum_command(launcher=LAUNCHER):
    """Return the launcher's `stat` FORMAT, asserting there is exactly one
    production site.  Two sites would mean a repair could land on one of them."""
    with open(launcher, encoding="utf-8") as fh:
        src = fh.read()
    hits = DATUM_LINE.findall(src)
    if len(hits) != 1:
        raise Refusal(
            "the age-datum production line is not unique in %s: %d matches %r. "
            "This control drives the launcher's OWN line; it cannot drive an "
            "ambiguous one." % (launcher, len(hits), hits))
    return hits[0]


def produce_datum(fmt, sentinel, work):
    """Run the launcher's own command, serialise it the way the launcher does
    (`echo > .d4_age_datum`), and READ IT BACK OFF DISK with `float()` exactly
    as `d6rf5_grade.py` does.  The floor this control hunts crosses a FILE
    BOUNDARY, so a control that kept the value in memory would not see it."""
    out = subprocess.run(["stat", "-c", fmt, sentinel],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise Refusal("stat -c %r failed on %s: %s" % (fmt, sentinel, out.stderr.strip()))
    raw_from_stat = out.stdout.strip()
    datum_file = os.path.join(work, ".d4_age_datum")
    with open(datum_file, "w") as fh:                      # the launcher's `echo >`
        fh.write(raw_from_stat + "\n")
    with open(datum_file) as fh:                           # READ BACK OFF DISK
        raw = fh.read().strip()
    return raw, float(raw)


def accepts(product, datum):
    """THE PREDICATE BOTH CONSUMERS USE, verbatim in sense: `d6rf5_grade.py`
    (`age_pass = age_pass and mt > datum`) and `d6rf5_endpoint_physical.py`
    (`if mt <= age_datum: refuse(...)`).  TRUE means ACCEPT."""
    return os.stat(product).st_mtime > datum


def float_epsilon(work, sentinel_ns, datum):
    """MEASURE the smallest offset the consumers' path can actually resolve --
    ON THE REAL CHAIN, by creating real files and asking the real predicate.

    THE FIRST VERSION OF THIS FUNCTION MEASURED THE WRONG QUANTITY and the
    control caught it on the REPAIRED launcher, which is the whole reason to
    write a control that can fail.  It compared `(sentinel_ns + d)/1e9` against
    `sentinel_ns/1e9` and answered 128 ns.  But that is not the comparison the
    guard makes.  The guard compares `os.stat(product).st_mtime` against a
    `float()` of a DECIMAL STRING that has been through `stat -c '%.9Y'`, a
    file, and back.  Those two roundings are not the same rounding, so the
    proxy was optimistic and a genuinely-newer product 128 ns out was still
    REFUSED.  This version searches over REAL files against the REAL datum.

    A double holds ~15-16 significant digits and an epoch needs 10 before the
    point, so the residual is sub-microsecond, NOT the nanoseconds the kernel
    stores.  The repair is therefore ~1e6x tighter than 1.000 s and NOT exact,
    and that sentence is now a measurement rather than a hope."""
    lo, hi = 1, 10 ** 9                    # 1 ns .. 1 s
    probe = os.path.join(work, ".epsilon_probe")
    def resolved(d):
        with open(probe, "w") as fh:
            fh.write("x")
        os.utime(probe, ns=(sentinel_ns + d, sentinel_ns + d))
        return os.stat(probe).st_mtime > datum
    if not resolved(hi):
        raise Refusal("even a product 1.000 s NEWER than the sentinel is not "
                      "resolved as newer -- the datum is not this sentinel's")
    while lo < hi:                          # monotone in d: binary search is valid
        mid = (lo + hi) // 2
        if resolved(mid):
            hi = mid
        else:
            lo = mid + 1
    os.remove(probe)
    return lo


def build(tmp):
    """A real tree: a sentinel with a LARGE fractional part, so a product 300 ms
    EARLIER still falls inside the same whole second and the truncated and exact
    predicates genuinely disagree there."""
    work = os.path.join(tmp, "work")
    os.makedirs(work)
    sentinel = os.path.join(work, "U")
    with open(sentinel, "w") as fh:
        fh.write("sentinel\n")
    st = os.stat(sentinel)
    sent_ns = (st.st_mtime_ns // 10 ** 9) * 10 ** 9 + 900_000_000   # ...s.900000000
    os.utime(sentinel, ns=(sent_ns, sent_ns))
    return work, sentinel, sent_ns


def product(work, name, mtime_ns):
    p = os.path.join(work, name)
    with open(p, "w") as fh:
        fh.write("{}\n")
    os.utime(p, ns=(mtime_ns, mtime_ns))
    return p


def rows(launcher=LAUNCHER, tmp=None, verbose=True):
    fmt = datum_command(launcher)
    tmp = tmp or tempfile.mkdtemp(prefix="d6rf5_age_control_")
    work, sentinel, sent_ns = build(tmp)
    raw, datum = produce_datum(fmt, sentinel, work)
    eps_ns = float_epsilon(work, sent_ns, datum)

    p_ns = product(work, "row_A_plus_1ns.json", sent_ns + 1)
    p_eps = product(work, "row_Aprime_plus_eps.json", sent_ns + eps_ns)
    p_old = product(work, "row_B_same_second_older.json", sent_ns - 300_000_000)

    out = {
        "launcher": launcher, "stat_format": fmt,
        "datum_raw_on_disk": raw, "datum_float": datum,
        "sentinel_ns": sent_ns, "float_epsilon_ns": eps_ns,
        "datum_has_fraction": "." in raw,
        "row_A_1ns_resolved": accepts(p_ns, datum),
        "row_Aprime_eps_accepted": accepts(p_eps, datum),
        "row_B_older_accepted": accepts(p_old, datum),
        "row_B_margin_s": os.stat(p_old).st_mtime - datum,
    }
    if verbose:
        print("  launcher            : %s" % launcher)
        print("  stat format IN USE  : %r  (extracted from the launcher, not copied)" % fmt)
        print("  datum on disk       : %r   fractional part present = %s"
              % (raw, out["datum_has_fraction"]))
        print("  sentinel            : %d ns (…%09d)" % (sent_ns, sent_ns % 10 ** 9))
        print("  float epsilon HERE  : %d ns   <- MEASURED, the residual after repair" % eps_ns)
        print("  ROW A   +1 ns       : resolved as newer = %s   (a double at epoch "
              "magnitude cannot hold 1 ns; this row MEASURES that, it does not assert it)"
              % out["row_A_1ns_resolved"])
        print("  ROW A'  +%d ns      : ACCEPTED = %s   (must be True: a genuinely "
              "newer product is still caught)" % (eps_ns, out["row_Aprime_eps_accepted"]))
        print("  ROW B   -300 ms     : ACCEPTED = %s   margin %+.6f s   (must be "
              "False: same whole second, GENUINELY OLDER)"
              % (out["row_B_older_accepted"], out["row_B_margin_s"]))
    return out


def check(launcher=LAUNCHER, tmp=None, verbose=True):
    """Raise Refusal unless the guard discriminates in BOTH directions."""
    r = rows(launcher, tmp, verbose)
    bad = []
    if not r["datum_has_fraction"]:
        bad.append("the datum on disk carries NO fractional part -- it is floored "
                   "to the whole second (raw=%r)" % r["datum_raw_on_disk"])
    if not r["row_Aprime_eps_accepted"]:
        bad.append("ROW A' FAILED: a product %d ns NEWER than the sentinel was "
                   "REFUSED -- the repair over-tightened and would refuse real work"
                   % r["float_epsilon_ns"])
    if r["row_B_older_accepted"]:
        bad.append("ROW B FAILED: a product 300 ms OLDER than the sentinel, in the "
                   "SAME whole second, was ACCEPTED (margin %+.6f s) -- the guard is "
                   "FAIL-OPEN over a window up to 1.000 s and every artefact it "
                   "guards is STAGED/GENERATED" % r["row_B_margin_s"])
    if bad:
        raise Refusal("AGE-DATUM CONTROL REFUSES:\n    - " + "\n    - ".join(bad))
    return r


def drive(tmp=None):
    """THE DISCRIMINATOR (`§2p.3(e)`): the control must FAIL on the DEFECTIVE
    launcher and PASS on the repaired one -- driven, not argued.  The defective
    launcher is the repaired one with `%.9Y` put back to `%Y` and the
    fractional-part assertion removed, so the ONLY thing that differs is the
    defect itself."""
    tmp = tmp or tempfile.mkdtemp(prefix="d6rf5_age_drive_")
    with open(LAUNCHER, encoding="utf-8") as fh:
        src = fh.read()
    mutated, n = DATUM_LINE.subn(
        'AGE_DATUM=$(stat -c \'%Y\' "$AGE_SRC")', src)
    if n != 1:
        raise Refusal("the defect could not be reintroduced at exactly one site "
                      "(%d) -- an unmutated 'defective' file would PASS and the "
                      "drive would report a discrimination it never made" % n)
    if mutated == src:
        raise Refusal("the mutation changed NOTHING -- the launcher is already "
                      "defective, or the pattern no longer matches")
    bad = os.path.join(tmp, "d6rf5_run_arm_DEFECTIVE.sh")
    with open(bad, "w") as fh:
        fh.write(mutated)

    print("\n--- ROW C  THE DEFECTIVE LAUNCHER (`%.9Y` -> `%Y`, one site, nothing else)")
    try:
        check(bad, os.path.join(tmp, "bad"), verbose=True)
    except Refusal as e:
        print("  CONTROL REFUSED, AS REQUIRED:\n    %s" % str(e).replace("\n", "\n    "))
    else:
        raise Refusal(
            "THE CONTROL PASSED ON THE DEFECTIVE LAUNCHER.  It cannot discriminate "
            "the defect it was written for, so its pass on the repaired file is "
            "not evidence the repair is right (this is exactly what W3S's 53/53 "
            "measured).  THIS DRIVE FAILS.")

    print("\n--- ROW D  THE REPAIRED LAUNCHER (the committed file)")
    check(LAUNCHER, os.path.join(tmp, "good"), verbose=True)
    print("  CONTROL PASSED on the repaired launcher.")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--drive", action="store_true",
                    help="also drive the control against a DEFECTIVE launcher")
    a = ap.parse_args(argv)
    print("D6RF5 AGE-DATUM CONTROL -- 0.000 SOLVER CORE-MIN, NOTHING HERE IS A "
          "RESULT ABOUT THE A2 WING")
    try:
        if a.drive:
            drive()
        else:
            print("\n--- the four rows, on the committed launcher")
            check()
            print("  CONTROL PASSED.")
    except Refusal as e:
        print("REFUSED: %s" % e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
