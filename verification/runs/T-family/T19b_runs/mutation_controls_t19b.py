#!/usr/bin/env python3
"""T19b MUTATION CONTROLS -- proof that every NEW limb CAN FAIL.

A limb that cannot fail is exactly the defect T19b exists to repair
(analyse_t19.py:691-694 was green because nothing had been marked DONE), so a
green selftest is not evidence about the successor until each new limb has been
shown to go red on a source that carries the defect it detects.

Each control builds a SANDBOX that mirrors the repository's directory depth --

    <scratch>/mutroot/scripts                      -> symlink to the real scripts/
    <scratch>/mutroot/verification/runs/T-family/T19_runs   -> symlink to the real T19_runs
    <scratch>/mutroot/verification/runs/T-family/T19b_runs/ -> the MUTATED instrument

-- so the mutant computes the same PARENT, REPO and sha256 pins as the real
file and differs from it in exactly one planted string.  __pycache__ is removed
and PYTHONDONTWRITEBYTECODE is set in the child, because stale bytecode has
inverted mutation tests in this lab before.

rc is captured directly from Popen.returncode, never through a pipeline.

usage: mutation_controls_t19b.py
exit 0 = every control behaved as registered; 1 = at least one did not.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TFAM = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ANALYSE = os.path.join(HERE, "analyse_t19b.py")
BUILD = os.path.join(HERE, "build_t19b.py")


def sandbox(instrument_src, mutated_text, basename):
    """Returns (tmproot, path to the mutated instrument)."""
    tmp = tempfile.mkdtemp(prefix="t19b_mut_")
    tf = os.path.join(tmp, "mutroot", "verification", "runs", "T-family")
    os.makedirs(os.path.join(tf, "T19b_runs"))
    os.symlink(os.path.join(REPO, "scripts"), os.path.join(tmp, "mutroot", "scripts"))
    os.symlink(os.path.join(TFAM, "T19_runs"), os.path.join(tf, "T19_runs"))
    dst = os.path.join(tf, "T19b_runs", basename)
    with open(dst, "w") as fh:
        fh.write(mutated_text)
    return tmp, dst


def drive(path):
    """rc straight off the process object -- never through a pipe."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for d in (os.path.dirname(path), HERE):
        pc = os.path.join(d, "__pycache__")
        if os.path.isdir(pc):
            shutil.rmtree(pc, ignore_errors=True)
    p = subprocess.Popen([sys.executable, path, "--selftest"], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, env=env)
    out, _ = p.communicate()
    return p.returncode, out


def mutate(src_path, old, new, count=1):
    txt = open(src_path).read()
    n = txt.count(old)
    if n != count:
        raise SystemExit("MUTATION ANCHOR NOT UNIQUE: %r occurs %d times in %s, expected %d"
                         % (old[:60], n, src_path, count))
    return txt.replace(old, new, count)


CONTROLS = []


def control(name, instrument, basename, old, new, want_labels, why):
    CONTROLS.append((name, instrument, basename, old, new, want_labels, why))


# ---------------------------------------------------------------- M1 (builder)
control(
    "M1  builder: residualControl planted BACK into fv_solution",
    BUILD, "build_t19b.py",
    '        "}\\n"\n        "relaxationFactors',
    '        "    residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }\\n"\n'
    '        "}\\n"\n        "relaxationFactors',
    ["emits NO residualControl block"],
    "the one substantive repair is undone; the limb that reads the built fvSolution off disk "
    "must go red, or it was never checking anything")

# -------------------------------------------------------------- M2 (S8d, HERE)
control(
    "M2  comparator: T19's `grade(HERE, ...)` restored inside the limb set",
    ANALYSE, "analyse_t19b.py",
    "    fired, wrote, ncases = False, True, 0\n",
    "    fired, wrote, ncases = False, True, 0\n"
    "    try:\n        grade(HERE, os.path.join(tempfile.gettempdir(), 't19_never.json'), reg)\n"
    "    except SystemExit:\n        pass\n",
    ["`HERE` references inside the selftest functions"],
    "the exact parent defect is put back; the source-level detector must see it")

# ------------------------------------------------- M3 (S8b, run-root watcher)
control(
    "M3  comparator: a limb READS the run root (os.listdir)",
    ANALYSE, "analyse_t19b.py",
    "    fired, wrote, ncases = False, True, 0\n",
    "    fired, wrote, ncases = False, True, 0\n"
    "    _ = os.listdir(run_root)\n",
    ["NO limb read, listed or stat-ed the run root"],
    "a live-run-tree read through a route the watcher covers must be recorded")

# ------------------------------- M4 (S8c, falsification-specimen watcher)
control(
    "M4  comparator: a limb READS the falsification specimen under T19_runs",
    ANALYSE, "analyse_t19b.py",
    "    fired, wrote, ncases = False, True, 0\n",
    "    fired, wrote, ncases = False, True, 0\n"
    "    _ = os.path.isfile(os.path.join(PARENT, 'P_q_c', '828', 'T'))\n",
    ["NO limb read anything under T19_runs"],
    "P_q_c/828 is EVIDENCE, preserved and never read by an instrument; the second watcher must "
    "catch a read of it even though the two pinned parent instruments are allowed")

# ---------------------------------------------- M5 (rule 3: the planted zero)
control(
    "M5  comparator: the watcher is BLINDED (_note made a no-op)",
    ANALYSE, "analyse_t19b.py",
    "    def _note(self, p):\n        if self._in:\n            return\n",
    "    def _note(self, p):\n        return\n        if self._in:\n            return\n",
    ["PLANTED CONTROL (rule 3)"],
    "rule 3 in its pure form: a blinded watcher still reports ZERO reads, so the PLANTED control "
    "is the only thing standing between that zero and a false green -- it must fire")

# ------------------------------------------------------- M6 (S8a, invariance)
control(
    "M6  comparator: a limb's OUTCOME made to depend on the run root's state",
    ANALYSE, "analyse_t19b.py",
    "    fired, wrote, ncases = False, True, 0\n",
    "    fired, wrote, ncases = False, True, 0\n"
    "    probe.append(('RUNROOT_DEPENDENT', os.stat(run_root).st_nlink))\n",
    ["S8a INVARIANCE"],
    "os.stat is DELIBERATELY outside the watcher's seven routes, so this mutant is invisible to "
    "S8b and S8c: it isolates S8a and proves the byte-identity comparison is itself live")


def main():
    print("T19b MUTATION CONTROLS -- each new limb driven on a source carrying the defect it detects")
    print("baseline first, so a red mutant cannot be a red baseline:")
    ok_all = True
    rows = []
    for path, nm in ((BUILD, "build_t19b.py"), (ANALYSE, "analyse_t19b.py")):
        rc, out = drive(path)
        good = (rc == 0 and "SELFTEST PASS (0 failed)" in out)
        print("  [%s] BASELINE %-18s rc=%d  %s"
              % ("ok " if good else "FAIL", nm, rc,
                 (re.findall(r"SELFTEST .*", out) or ["<no summary>"])[-1]))
        ok_all &= good
        rows.append(("BASELINE " + nm, rc, good))

    for name, instrument, basename, old, new, want_labels, why in CONTROLS:
        txt = mutate(instrument, old, new)
        tmp, dst = sandbox(instrument, txt, basename)
        try:
            rc, out = drive(dst)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        red = [line for line in out.splitlines() if re.match(r"\s*\[FAIL\]", line)]
        summary = (re.findall(r"SELFTEST .*", out) or ["<no summary>"])[-1]
        # THE REGISTERED EXPECTATION, and it is deliberately specific: rc = 1, a
        # FAIL summary, and the limb that goes red is THE NAMED ONE.  "the
        # selftest failed" is not enough -- a mutant that reddened some other
        # limb would prove nothing about the limb under test.
        named = all(any(lbl in line for line in red) for lbl in want_labels)
        good = (rc == 1) and ("SELFTEST FAIL" in summary) and named
        print("  [%s] %-62s rc=%d  %s" % ("ok " if good else "FAIL", name, rc, summary))
        print("       expected to trip: %s" % ", ".join(want_labels))
        print("       why: %s" % why)
        if not good:
            print("       ---- mutant output tail ----")
            print("\n".join(out.strip().splitlines()[-12:]))
        ok_all &= good
        rows.append((name, rc, good))

    n_bad = sum(1 for _, _, g in rows if not g)
    print("MUTATION CONTROLS %s (%d of %d behaved as registered)"
          % ("PASS" if not n_bad else "FAIL", len(rows) - n_bad, len(rows)))
    return 0 if not n_bad else 1


if __name__ == "__main__":
    sys.exit(main())
