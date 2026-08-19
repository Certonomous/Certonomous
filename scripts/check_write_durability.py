#!/usr/bin/env python3
"""
Find case dictionaries whose only scheduled field write is at endTime.

WHY THIS IS AN INSTRUMENT AND NOT A STYLE PREFERENCE.  On 2026-08-19 the two
K0cG square-cavity cases reached 85 % and 60 % of their registered endTime and
produced NOTHING measurable, because writeInterval equalled endTime and the host
went down before the single scheduled write.  The cost of that dictionary line
is not the fraction of the run that remained; it is the fraction that had
already been paid for.  See LESSONS.md L-140.

The trade is asymmetric with no crossover.  Checkpointing costs a bounded,
measurable amount of disk and is pure input/output -- it cannot enter the
discretisation, the schemes, the relaxation or the stopping criterion, and it
cannot move a solution value.  A single write risks the whole run.

WHAT IS AND IS NOT EXPOSED.  A case that has ALREADY written a non-zero time
directory is not exposed: its fields are on disk and rewriting its controlDict
would change nothing.  Only a case that has not yet produced a field is at risk,
so those two populations are reported separately and only the second can fail
the check.

WHAT THIS CHECK CANNOT SEE, stated because a check that overstates its reach is
worse than none:
  * whether a checkpointed run is CONVERGED.  Durability and convergence are
    graded differently; a checkpoint preserves a measurable state, never a
    converged one.
  * whether the function objects already persist the graded quantity.  They
    often persist a MONITOR instead -- K0cG's surviving series was the
    area-normal integral of the molecular temperature gradient, which is not
    the graded Nusselt row, because that row needs the alphaEff factor read
    from a written alphat field.
  * writeControl values other than timeStep.  For runTime, adjustable,
    clockTime and cpuTime the interval is not in the same units as endTime and
    the equality test would be meaningless, so those are reported UNJUDGED
    rather than guessed at.
  * anything about a builder that has not yet been run.  Builders are scanned
    separately and only reported, never failed: a frozen builder belonging to a
    rung that has already reported is not edited retroactively.

Exit: 0 clean, 3 at least one unrun case has a single scheduled write,
      2 refusal.
"""
import argparse
import os
import re
import shutil
import sys
import tempfile

EXIT_OK, EXIT_REFUSE, EXIT_VIOLATION = 0, 2, 3

TIME_DIR = re.compile(r"^[0-9]+(\.[0-9]+)?$")


def refuse(msg):
    print(msg)
    sys.exit(EXIT_REFUSE)


def entry(text, key):
    """Last value of a top-level controlDict entry, or None."""
    m = re.findall(r"^\s*%s\s+([^;]+);" % re.escape(key), text, re.M)
    return m[-1].strip() if m else None


def as_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def classify(path):
    """Classify one system/controlDict.  Returns a dict, never raises."""
    try:
        with open(path, "r", errors="replace") as fh:
            text = fh.read()
    except OSError as e:
        return dict(path=path, state="UNREADABLE", detail=str(e))

    wc = entry(text, "writeControl")
    wi = as_float(entry(text, "writeInterval"))
    et = as_float(entry(text, "endTime"))
    stop = entry(text, "stopAt")
    rec = dict(path=path, writeControl=wc, writeInterval=wi, endTime=et,
               purgeWrite=entry(text, "purgeWrite"))

    if wc is None or wi is None or et is None:
        rec["state"] = "INCOMPLETE"
        return rec
    if wc != "timeStep":
        rec["state"] = "UNJUDGED"
        rec["detail"] = "writeControl %s: interval not in endTime units" % wc
        return rec
    if stop is not None and stop != "endTime":
        rec["state"] = "UNJUDGED"
        rec["detail"] = "stopAt %s: endTime is not the stopping criterion" % stop
        return rec
    if wi <= 0:
        rec["state"] = "INCOMPLETE"
        return rec
    if et <= 0:
        # endTime 0 runs no iteration, so there is no progress to lose.  Caught
        # by W2_sparta_runs/cbfs_ic1, an initial-condition case that the
        # wi >= et test flagged vacuously.
        rec["state"] = "UNJUDGED"
        rec["detail"] = "endTime %g: the case performs no iteration" % et
        return rec

    rec["scheduled_writes"] = int(et // wi)
    rec["state"] = "SINGLE_WRITE" if wi >= et else "CHECKPOINTED"
    return rec


def written_fields(case_dir):
    """Count time directories other than 0 that exist on disk."""
    try:
        names = os.listdir(case_dir)
    except OSError:
        return 0
    return sum(1 for n in names
               if TIME_DIR.fullmatch(n) and float(n) != 0.0
               and os.path.isdir(os.path.join(case_dir, n)))


def scan_cases(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        if os.path.basename(dirpath) != "system":
            continue
        if "controlDict" not in filenames:
            continue
        rec = classify(os.path.join(dirpath, "controlDict"))
        case = os.path.dirname(dirpath)
        rec["case"] = os.path.relpath(case, root)
        rec["written_time_dirs"] = written_fields(case)
        out.append(rec)
    return out


BUILDER = re.compile(r"^build_cases.*\.(py|sh)$")


def scan_builders(root):
    """Report builders that emit a writeInterval tied to endTime.

    REPORTED, NEVER FAILED.  A builder frozen with a rung that has already
    reported is not edited after the fact; the point of listing it is that the
    NEXT rung copied from it inherits the default.
    """
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        for fn in filenames:
            if not BUILDER.fullmatch(fn):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, "r", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            vals = re.findall(r"writeInterval\s+([^;\n]+)", text)
            vals = [v.strip() for v in vals]
            # a templated interval naming the end time reproduces the hazard
            tied = [v for v in vals if re.search(r"\{[^}]*end[^}]*\}", v)]
            if tied:
                hits.append((os.path.relpath(p, root), tied))
    return hits


def report(root, show_all):
    cases = scan_cases(root)
    single = [c for c in cases if c["state"] == "SINGLE_WRITE"]
    exposed = [c for c in single if c["written_time_dirs"] == 0]
    settled = [c for c in single if c["written_time_dirs"] > 0]
    checkp = [c for c in cases if c["state"] == "CHECKPOINTED"]
    unjudged = [c for c in cases if c["state"] == "UNJUDGED"]
    other = [c for c in cases if c["state"] in ("INCOMPLETE", "UNREADABLE")]

    print("scanned %d case dictionaries under %s" % (len(cases), root))
    print("  CHECKPOINTED  %4d" % len(checkp))
    print("  SINGLE_WRITE  %4d   (%d already hold fields, %d do not)"
          % (len(single), len(settled), len(exposed)))
    print("  UNJUDGED      %4d   (writeControl or stopAt makes the test moot)"
          % len(unjudged))
    print("  INCOMPLETE    %4d" % len(other))

    if exposed:
        print("\nEXPOSED -- a single scheduled write and no field on disk:")
        for c in sorted(exposed, key=lambda r: r["case"]):
            print("  endTime %-9g writeInterval %-9g  %s"
                  % (c["endTime"], c["writeInterval"], c["case"]))
    if show_all and settled:
        print("\nNOT EXPOSED -- single write, but the fields were written:")
        for c in sorted(settled, key=lambda r: r["case"]):
            print("  %d time dir(s)  %s" % (c["written_time_dirs"], c["case"]))

    builders = scan_builders(root)
    if builders:
        print("\nBUILDERS emitting an endTime-tied writeInterval "
              "(reported, not failed):")
        for p, vals in sorted(builders):
            print("  %-70s %s" % (p, ", ".join(vals)))
        print("  A rung copied from any of these inherits the single write.")
    return exposed


def _plant(tmp, name, control, interval, end, timedirs):
    case = os.path.join(tmp, name)
    os.makedirs(os.path.join(case, "system"))
    for t in timedirs:
        os.makedirs(os.path.join(case, t))
    with open(os.path.join(case, "system", "controlDict"), "w") as fh:
        fh.write("startFrom latestTime;\nstopAt endTime;\n"
                 "endTime %s;\nwriteControl %s;\nwriteInterval %s;\n"
                 "purgeWrite 0;\n" % (end, control, interval))
    return case


def selftest():
    """Plant every shape the classifier claims to separate and read it back."""
    tmp = tempfile.mkdtemp(prefix="wdur_selftest_")
    ok = True
    try:
        want = [
            ("single_unrun",   "timeStep", 40000, 40000, ["0"],
             "SINGLE_WRITE", 0),
            ("single_settled", "timeStep", 40000, 40000, ["0", "40000"],
             "SINGLE_WRITE", 1),
            ("checkpointed",   "timeStep", 2000, 40000, ["0"],
             "CHECKPOINTED", 0),
            ("interval_over",  "timeStep", 50000, 40000, ["0"],
             "SINGLE_WRITE", 0),
            ("runtime_ctl",    "runTime", 40000, 40000, ["0"],
             "UNJUDGED", 0),
            # endTime 0 iterates nothing; flagging it was a false positive
            ("zero_endtime",   "timeStep", 1, 0, ["0"],
             "UNJUDGED", 0),
        ]
        for name, ctl, wi, et, tds, state, nwritten in want:
            _plant(tmp, name, ctl, wi, et, tds)
        recs = {r["case"]: r for r in scan_cases(tmp)}
        for name, ctl, wi, et, tds, state, nwritten in want:
            r = recs.get(name)
            if r is None:
                print("  FAIL %-16s not found by the scan" % name)
                ok = False
                continue
            good = (r["state"] == state
                    and r["written_time_dirs"] == nwritten)
            print("  %-4s %-16s state=%-13s written=%d (want %s, %d)"
                  % ("ok" if good else "FAIL", name, r["state"],
                     r["written_time_dirs"], state, nwritten))
            ok = ok and good

        # a tree with no case at all must scan clean, not crash
        empty = tempfile.mkdtemp(prefix="wdur_empty_")
        try:
            n = len(scan_cases(empty))
            print("  %-4s %-16s %d cases in an empty tree (want 0)"
                  % ("ok" if n == 0 else "FAIL", "empty_tree", n))
            ok = ok and n == 0
        finally:
            shutil.rmtree(empty, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest %s" % ("PASSED" if ok else "FAILED"))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--all", action="store_true",
                    help="also list single-write cases that already hold fields")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(EXIT_OK if selftest() else EXIT_VIOLATION)

    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        refuse("REFUSE: %s is not a directory" % root)

    exposed = report(root, a.all)
    if exposed:
        print("\n%d unrun case(s) would lose everything to one interruption."
              % len(exposed))
        sys.exit(EXIT_VIOLATION)
    print("\nno unrun case has a single scheduled write.")
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
