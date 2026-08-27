#!/usr/bin/env python3
"""F26D -- grade the Ringleb DISCRIMINATING ARM against its frozen registration.

Registered by PREREGISTRATION_F26D_2026-08-27.md. THIS GRADES A DIAGNOSTIC, NOT A
LADDER. It cannot unblock or rescope F26_RINGLEB, which stays BLOCKED, and it
emits no PASS/GATE FAIL on any physical quantity because the arm measures none.

WHAT IT READS, AND WHAT IT REFUSES TO COMPUTE
---------------------------------------------
The observable is N*, the coarsest registered level at which an arm FAILS. It is
a COMPLETION property: it needs no exact solution, no error norm, and NO
RICHARDSON EXTRAPOLATION. This file does not import roache_triple, computes no
observed order and reports no GCI -- so the known absence of a minimum-r guard in
scripts/roache_triple.py (verification's to fix, not this arm's) cannot reach any
number here. The ladder's r = 2 exactly, and no claim depends on it.

A level COMPLETES iff ALL of: rc == 0; an `End` line; last written time ==
endTime; and the count of `ExecutionTime` lines == endTime. Anything else FAILS.
That is CLAUDE.md standing rule 4 read for a SIMPLE run whose time axis is the
iteration index.

THE PLANTED CONTROL (standing rule 3), IN BOTH DIRECTIONS, THROUGH THE REAL
READER AND OFF DISK: a COMPLETING case is written to disk, mutated to carry an
abort signature, re-read by classify_dir() and required to flip to FAILED; and a
FAILING case is written, mutated to carry a completion signature, re-read and
required to flip to COMPLETED. A reader shown able to return only one answer is
not evidence, and one direction alone would leave the other unshown.

Zero `assert` (L-332); every refusal is a raise or sys.exit; refuses under
`python3 -O` at entry, before any work.

EXIT CODES
    0   graded (a reading was produced), or the selftest passed
    2   NOT A RESULT / refusal / selftest failure
    1   usage error
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: grade_f26d.py must not run under `python3 -O` or "
                     "PYTHONOPTIMIZE. Re-run under plain `python3`.\n")
    sys.exit(2)

import os
import re
import ast
import json
import hashlib
import argparse
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PREREG = "cases/F26_RINGLEB/PREREGISTRATION_F26D_2026-08-27.md"
ARMS = ("A0", "AV", "AM")
LEVELS = ("L1", "L2", "L3", "L4")
CELLS = {"L1": 96, "L2": 384, "L3": 1536, "L4": 6144}
END_TIME = 4000
# Pre-registration section 4.3: A0 must complete L1 and L2 and FAIL at L3.
A0_MUST_COMPLETE = ("L1", "L2")
A0_MUST_FAIL_AT = "L3"


class Refusal(Exception):
    """A condition that must stop the instrument under ANY interpreter flag."""


def _git(args, cwd):
    if args and args[0] not in ("cat-file", "rev-parse", "ls-tree"):
        raise Refusal("GIT-READ-ONLY: %r is not in the read-only allowlist" % args[0])
    return subprocess.run(["git", "-C", cwd] + args, capture_output=True, text=True)


# ---------------------------------------------------------------------------
# THE READER. Pure text/rc in, verdict out, so the planted control can drive it.
# ---------------------------------------------------------------------------

def classify_text(rc, text):
    """Standing rule 4 for a SIMPLE run whose time axis is the iteration index."""
    why = []
    if rc is None:
        return "FAILED", ["no RC.txt"]
    if rc != 0:
        why.append("rc=%d%s" % (rc, {136: " (SIGFPE)", 134: " (FOAM abort)"}.get(rc, "")))
    if "\nEnd\n" not in ("\n" + text + "\n"):
        why.append("no End line")
    times = [float(m.group(1)) for m in re.finditer(r"^Time = ([0-9.eE+-]+)", text, re.M)]
    last = times[-1] if times else None
    if last is None or abs(last - END_TIME) > 1e-9:
        why.append("last time %s != endTime %d" % (last, END_TIME))
    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    if n_exec != END_TIME:
        why.append("ExecutionTime count %d != %d" % (n_exec, END_TIME))
    if re.search(r"negative initial temperature|Negative initial temperature", text):
        why.append("negative temperature")
    return ("COMPLETED", []) if not why else ("FAILED", why)


def classify_dir(d):
    """Read rc and log OFF DISK and classify. The planted control drives THIS."""
    rcp, logp = os.path.join(d, "RC.txt"), os.path.join(d, "log.solve")
    rc = None
    if os.path.exists(rcp):
        raw = open(rcp).read().strip()
        rc = int(raw) if re.fullmatch(r"-?\d+", raw) else None
    text = open(logp).read() if os.path.exists(logp) else ""
    if not os.path.exists(logp):
        return "FAILED", ["no log.solve"]
    return classify_text(rc, text)


def threshold(states):
    """N* = the coarsest registered level that FAILED, else NONE."""
    for lv in LEVELS:
        if states.get(lv, ("FAILED", ["absent"]))[0] == "FAILED":
            return lv
    return "NONE"


def reading(nstar):
    """The pre-registration section 4.2 table, fixed before compute."""
    a0, av, am = nstar["A0"], nstar["AV"], nstar["AM"]
    av_fixed, am_fixed = av == "NONE", am == "NONE"
    if av_fixed and not am_fixed:
        return ("C_mu carries it", "Zero viscosity carries the failure. Curvature and Mach "
                "are neither necessary nor sufficient.")
    if am_fixed and not av_fixed:
        return ("{C_kappa OR C_M} carries it", "Curvature and/or Mach carries it; zero "
                "viscosity does not. NOT separated further -- see pre-registration section 5; "
                "the section 5.1 secondary reading may be consulted but cannot carry this alone.")
    if av_fixed and am_fixed:
        return ("AMBIGUOUS", "Both probes are sufficient repairs and neither is shown "
                "necessary. NO CANDIDATE IS ELIMINATED. Reported as ambiguous, not resolved.")
    return ("NONE of the three", "Neither viscosity nor the geometry/Mach band changes the "
            "threshold. The cause lies in the solver, boundary treatment or scheme -- a FOURTH "
            "candidate this arm did not register. A decisive negative.")


# ---------------------------------------------------------------------------

def count_assert_nodes(src):
    return sum(1 for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Assert))


COMPLETING = ("Starting time loop\n\n"
              + "".join("Time = %d\n\nExecutionTime = %.2f s\n\n" % (i, i * 0.01)
                        for i in range(1, END_TIME + 1))
              + "End\n")
FAILING = ("Starting time loop\n\n"
           + "".join("Time = %d\n\nExecutionTime = %.2f s\n\n" % (i, i * 0.01)
                     for i in range(1, 795))
           + "Foam::sigFpe::sigHandler(int)\n")


def _write_case(d, rc, text):
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "RC.txt"), "w").write("%d\n" % rc)
    open(os.path.join(d, "log.solve"), "w").write(text)


def selftest():
    problems, lines = [], []
    src = open(os.path.abspath(__file__)).read()

    n = count_assert_nodes(src)
    if n:
        problems.append("G1 FAILED: %d assert node(s); -O deletes them (L-332)." % n)
    else:
        lines.append("G1: zero `assert` nodes in this comparator (L-332).")
    if count_assert_nodes("def f(x):\n    assert x\n    return x\n") != 1:
        problems.append("G1 CONTROL FAILED: the ast counter could not see a planted assert.")
    else:
        lines.append("G1 CONTROL FIRED: the counter saw 1 planted assert, so the zero is a reading.")

    with tempfile.TemporaryDirectory() as td:
        # G2 -- the reader reads a genuine COMPLETING case off disk as COMPLETED.
        good = os.path.join(td, "good")
        _write_case(good, 0, COMPLETING)
        s, why = classify_dir(good)
        if s != "COMPLETED":
            problems.append("G2 FAILED: a complete case read as %s (%s)." % (s, why))
        else:
            lines.append("G2: a complete case (rc 0, End, last time 4000, 4000 ExecutionTime "
                         "lines) reads off disk as COMPLETED.")

        # G3 -- PLANT, DIRECTION ONE: mutate the COMPLETING case on disk to carry an
        # abort signature; the SAME reader must flip it to FAILED.
        _write_case(good, 136, FAILING)
        s2, why2 = classify_dir(good)
        if s2 != "FAILED":
            problems.append("G3 PLANT DID NOT FLIP: a case mutated to rc=136 with a truncated "
                            "log still read COMPLETED. The reader cannot see a failure, so "
                            "every COMPLETED it returns is worthless.")
        else:
            lines.append("G3 PLANT FLIPPED (direction 1, completing -> failing): the mutated "
                         "case read FAILED off disk via the same reader, reasons %s." % why2)

        # G4 -- PLANT, DIRECTION TWO: mutate a FAILING case to carry a completion
        # signature; the SAME reader must flip it to COMPLETED. Without this, a
        # reader hard-wired to FAILED would pass G3 and be undetectable.
        bad = os.path.join(td, "bad")
        _write_case(bad, 136, FAILING)
        s3, _ = classify_dir(bad)
        _write_case(bad, 0, COMPLETING)
        s4, why4 = classify_dir(bad)
        if s3 != "FAILED":
            problems.append("G4 FAILED: the failing case did not read FAILED to begin with.")
        elif s4 != "COMPLETED":
            problems.append("G4 PLANT DID NOT FLIP: a case mutated to a complete log and rc 0 "
                            "still read FAILED (%s). A reader that cannot return COMPLETED "
                            "makes every FAILED it returns worthless too." % why4)
        else:
            lines.append("G4 PLANT FLIPPED (direction 2, failing -> completing): the mutated "
                         "case read COMPLETED off disk via the same reader. BOTH directions "
                         "are now shown, so neither verdict is a stuck reading.")

        # G5 -- each clause of the completion rule is separately load-bearing.
        for label, rc, text in (
                ("rc", 136, COMPLETING),
                ("End line", 0, COMPLETING.replace("End\n", "")),
                ("last time", 0, COMPLETING.replace("Time = 4000\n", "Time = 3999\n")),
                ("negative T", 0, COMPLETING + "negative initial temperature\n")):
            d = os.path.join(td, "c_" + label.replace(" ", "_"))
            _write_case(d, rc, text)
            st, _ = classify_dir(d)
            if st != "FAILED":
                problems.append("G5 FAILED: breaking the %r clause alone still read COMPLETED, "
                                "so that clause is not load-bearing." % label)
        if not any(p.startswith("G5") for p in problems):
            lines.append("G5 CONTROL FIRED: breaking each of rc / End line / last time / "
                         "negative-T ALONE flips the verdict to FAILED, so no clause of the "
                         "completion rule is decorative.")

    # G6 -- the section 4.2 table is total and each row is reachable.
    cases = {("NONE", "L3"): "C_mu carries it",
             ("L3", "NONE"): "{C_kappa OR C_M} carries it",
             ("NONE", "NONE"): "AMBIGUOUS",
             ("L3", "L3"): "NONE of the three"}
    for (av, am), want in cases.items():
        got, _ = reading({"A0": "L3", "AV": av, "AM": am})
        if got != want:
            problems.append("G6 FAILED: AV=%s AM=%s read as %r, registered %r." % (av, am, got, want))
    if not any(p.startswith("G6") for p in problems):
        lines.append("G6 CONTROL FIRED: all four rows of the pre-registered section 4.2 table "
                     "are reachable and each returns its registered reading.")

    # G7 -- no Richardson machinery is REACHABLE. Mechanical, from the AST, not
    # textual: a first draft of this control grepped the source and failed on its
    # OWN DOCSTRING, which says in prose that no extrapolation is performed. Prose
    # about an absence must not be able to fail a check for that absence.
    tree = ast.parse(src)
    imported, names = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(al.name for al in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
        elif isinstance(node, ast.Name):
            names.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            names.add(node.attr.lower())
    hits = sorted({x for x in imported | names
                   if "roache" in x.lower() or "gci" in x.lower() or "richardson" in x.lower()})
    probe = ast.parse("import roache_triple\nz = gci_of(a)\n")
    probe_hits = {n.names[0].name for n in ast.walk(probe) if isinstance(n, ast.Import)} | \
                 {n.id for n in ast.walk(probe) if isinstance(n, ast.Name)}
    if not any("roache" in h or "gci" in h for h in probe_hits):
        problems.append("G7 CONTROL FAILED: the AST reader could not see PLANTED roache/gci "
                        "references in a synthetic source, so its zero below means nothing.")
    elif hits:
        problems.append("G7 FAILED: Richardson/GCI machinery is reachable in CODE: %s" % hits)
    else:
        lines.append("G7 CONTROL FIRED: %d imports and %d identifiers read out of the AST; NONE "
                     "names roache, gci or richardson, and the reader was shown able to see them "
                     "planted in a synthetic source. No extrapolation is performed, so the "
                     "missing minimum-r guard in scripts/roache_triple.py cannot reach any number "
                     "here." % (len(imported), len(names)))

    for l in lines:
        print("  " + l)
    if problems:
        print("")
        for p in problems:
            print("  " + p)
        print("\nGRADER SELFTEST FAILED: %d control(s) did not behave." % len(problems))
        return 2
    print("\nGRADER SELFTEST PASS: %d controls fired, each shown able to fail." % len(lines))
    return 0


def verify_freeze(prereg_commit, root):
    """Rule 2: the frozen file that ran must BE the committed blob."""
    out = _git(["rev-parse", "%s:%s" % (prereg_commit, PREREG)], root)
    if out.returncode != 0:
        raise Refusal("FREEZE: %s:%s does not resolve -- %s" % (prereg_commit, PREREG, out.stderr.strip()))
    want = out.stdout.strip()
    disk = open(os.path.join(root, PREREG), "rb").read()
    got = hashlib.sha1(b"blob %d\x00" % len(disk) + disk).hexdigest()
    if got != want:
        raise Refusal("FREEZE: the pre-registration on disk (blob %s) is NOT the committed blob "
                      "%s at %s. The grading path is fixed at the pre-registration commit."
                      % (got[:12], want[:12], prereg_commit))
    return want


def main(argv):
    ap = argparse.ArgumentParser(description="Grade the F26D discriminating arm. Diagnostic, not a ladder.")
    ap.add_argument("--run-root", default="/home/ubuntu/Certonomous/verification/runs/F26D_runs")
    ap.add_argument("--prereg-commit")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()

    if count_assert_nodes(open(os.path.abspath(__file__)).read()):
        print("REFUSED (instrument): assert node present; -O would delete it (L-332).")
        return 2
    root = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    if a.prereg_commit:
        blob = verify_freeze(a.prereg_commit, root)
        print("FREEZE VERIFIED: %s on disk == committed blob %s at %s" % (PREREG, blob[:12], a.prereg_commit))

    states, nstar = {}, {}
    for arm in ARMS:
        states[arm] = {}
        for lv in LEVELS:
            d = os.path.join(a.run_root, arm, lv)
            states[arm][lv] = classify_dir(d) if os.path.isdir(d) else ("FAILED", ["absent"])
        nstar[arm] = threshold(states[arm])

    # Section 4.3 -- A0 is the reference and its behaviour is a refusal condition.
    a0 = states["A0"]
    bad = [lv for lv in A0_MUST_COMPLETE if a0[lv][0] != "COMPLETED"]
    print("arm N*: " + "  ".join("%s=%s" % (k, nstar[k]) for k in ARMS))
    for arm in ARMS:
        for lv in LEVELS:
            st, why = states[arm][lv]
            print("    %s %s (%5d cells): %s%s" % (arm, lv, CELLS[lv], st,
                                                   "" if st == "COMPLETED" else "  <- " + "; ".join(why)))
    if bad:
        print("NOT A RESULT: pre-registration section 4.3 requires A0 to COMPLETE %s; it did not "
              "complete %s. The reference the probe arms are read against has moved."
              % (list(A0_MUST_COMPLETE), bad))
        return 2
    if a0[A0_MUST_FAIL_AT][0] != "FAILED":
        print("NOT A RESULT: pre-registration section 4.3 requires A0 to FAIL at %s; it "
              "COMPLETED. The prior threshold measurement (600-864 cells) is contradicted and "
              "AV/AM would be compared against nothing." % A0_MUST_FAIL_AT)
        return 2

    verdict, why = reading(nstar)
    print("GATE REACHED -- reading: %s" % verdict)
    print("    %s" % why)
    print("    F26_RINGLEB REMAINS BLOCKED. This arm is a diagnostic, not a ladder; it does not "
          "rescope F26 and the rescope cost is NOT established.")
    if a.json:
        print(json.dumps({"nstar": nstar, "reading": verdict, "detail": why,
                          "states": {k: {l: v[0] for l, v in s.items()} for k, s in states.items()}},
                         indent=1))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        print("REFUSED: %s" % exc)
        sys.exit(2)
