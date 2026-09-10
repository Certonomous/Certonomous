#!/usr/bin/env python3
"""CASE PROTOCOL stage 2 - INSTRUMENT CHECK, generalised and reusable.

The rule (Sanaa, CASE PROTOCOL stage 2):

    "INSTRUMENT CHECK - every grading reader must detect a planted
     perturbation THROUGH THE REAL PATH or the case fails closed."

THROUGH THE REAL PATH is the load-bearing phrase and it is the whole point of
this file.  A plant that reaches the reader through a test shortcut certifies
the shortcut, not production.  Two live instances were measured in this lab on
2026-09-10, both with GREEN selftests:

  * scripts/check_filing.py's selftest plants a spaced filename and then
    `git add -A`s it (:395-396 region) BEFORE checking - so it exercises the
    TRACKED code path, while the real run's blind spot is the UNTRACKED one
    (D593).
  * scripts/mark_done_k0h.py's clause-7 selftest drives launch_guard()
    DIRECTLY rather than through any launcher, so it passes green over ZERO
    call sites (D598 section 8).

Both were about the code and not about the world.  So:

  THIS CHECK NEVER IMPORTS THE READER.  It writes the perturbation onto the
  artifact ON DISK and invokes the reader as a SUBPROCESS through its real
  command line (argv), exactly as production invokes it.  Importing an
  internal function and calling it is the precise shortcut this check exists
  to detect; a reader that can see the plant in-process but not through its
  CLI is reported NOT-DETECTED, because the CLI is what grades cases.

Outcomes - three, and they are never merged:

  DETECTED      the reader's output changed when the artifact changed   -> 0
  NOT-DETECTED  output identical across the plant; FAILS CLOSED         -> 1
  COULD-NOT-RUN reader/artifact missing, reader errored for an unrelated
                reason, the plant could not be made to land, or the
                reader is not output-stable; REFUSE, and NOT reported as
                either of the other two                                 -> 2
  RESTORE FAILED the artifact was not put back byte-for-byte            -> 3

A check reporting no violations over a population it could not evaluate has
not passed; it has not run (VERIFICATION_CHARTER section 2c).  COULD-NOT-RUN
exists so that distinction survives contact with a script.

DOUBLE CONTROL - this check is itself an instrument, so it is controlled too.
Arm STABILITY runs the reader twice on the UNPLANTED artifact and requires
byte-identical output.  A reader whose output drifts run-to-run (timestamps,
PIDs, hash seeds, wall clock) would show "DETECTED" for any plant at all,
which is a false pass.  Instability is COULD-NOT-RUN, never DETECTED.
(--scrub can mask a known-volatile pattern; a scrub is applied identically to
the clean and planted outputs, so it can only ever hide a delta and push the
verdict toward NOT-DETECTED - the fail-closed direction.)

RESTORE - the artifact is backed up (bytes + sha256) before the plant and
restored in a finally block whether or not the check passed, and the restore
is VERIFIED by re-hashing in the same invocation.  A check that corrupts the
case it audits is worse than no check, so a failed restore dominates every
other outcome, prints the surviving backup path, and exits 3.

NO BARE `assert` ANYWHERE - `python3 -O` strips them (D594/L-332).  Every
condition is `if not cond: sys.exit(...)` or an explicit recorded failure.
`--selftest` is required to give the same exit code under python3 and
python3 -O.

SCOPE - this script wires itself into NOTHING.  No hook, no pre-commit, no
check_harness registration.  Adding a lab gate is Sanaa's decision (D539);
she ordered the stage-2 check, so this script may exit non-zero on its own
subject and on nothing else.

USAGE
    check_instrument_detects_plant.py --reader <script> --artifact <file>
        [--reader-arg ARG ...] [--case DIR] [--plant-mode auto|numeric|append]
        [--plant-value FLOAT] [--plant-line N] [--scrub REGEX ...]
        [--timeout SEC] [--json OUT]
    check_instrument_detects_plant.py --selftest

    {artifact} and {case} in a --reader-arg are substituted.  With no
    --reader-arg at all, the artifact path is passed as the single argument.
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

EXIT_DETECTED = 0
EXIT_NOT_DETECTED = 1
EXIT_COULD_NOT_RUN = 2
EXIT_RESTORE_FAILED = 3

DEFAULT_PLANT = 1.234e-03          # the T3 constant, carried across on purpose
DEFAULT_TIMEOUT = 900.0


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def scrub_text(text, patterns):
    for p in patterns:
        text = re.sub(p, "<scrubbed>", text)
    return text


def short(s, n=70):
    s = s.replace("\n", "\\n")
    return s if len(s) <= n else s[: n - 3] + "..."


# ---------------------------------------------------------------------------
# the production entry point - subprocess, never import
# ---------------------------------------------------------------------------
def build_argv(reader, reader_args, artifact, case, no_args=False):
    """The command line production uses.  A .py reader is run with the SAME
    interpreter that is running this check, so `python3 -O` propagates.
    Some lab readers take no arguments at all and locate their case tree
    relative to their own __file__; --no-args covers that entry point."""
    subs = {"{artifact}": artifact, "{case}": case or ""}
    args = []
    for a in reader_args:
        for k, v in subs.items():
            a = a.replace(k, v)
        args.append(a)
    if not args and not no_args:
        args = [artifact]
    if reader.endswith(".py"):
        return [sys.executable] + [reader] + args
    return [reader] + args


def run_reader(argv, timeout, cwd):
    """Invoke the reader through its real CLI.  Returns a dict; never raises
    for a reader-side failure - the caller decides what a failure means."""
    try:
        p = subprocess.run(argv, cwd=cwd, timeout=timeout,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.TimeoutExpired:
        return dict(ran=False, why="reader timed out after %.0f s" % timeout,
                    rc=None, out="", err="")
    except OSError as e:
        return dict(ran=False, why="could not execute the reader: %s" % e,
                    rc=None, out="", err="")
    return dict(ran=True, why=None, rc=p.returncode,
                out=p.stdout.decode("utf-8", "replace"),
                err=p.stderr.decode("utf-8", "replace"))


def fingerprint(res, scrubs):
    return (res["rc"],
            scrub_text(res["out"], scrubs),
            scrub_text(res["err"], scrubs))


def describe_delta(fa, fb):
    """A short, human-readable statement of what changed between two reader
    fingerprints.  Goes into the stage-6 status line."""
    bits = []
    if fa[0] != fb[0]:
        bits.append("rc %s->%s" % (fa[0], fb[0]))
    for name, i in (("stdout", 1), ("stderr", 2)):
        if fa[i] != fb[i]:
            a, b = fa[i].split("\n"), fb[i].split("\n")
            first = None
            for line in difflib.unified_diff(a, b, n=0, lineterm=""):
                if line.startswith("@@"):
                    first = line.strip()
                    break
            bits.append("%s %dB->%dB%s" % (name, len(fa[i]), len(fb[i]),
                                           " " + first if first else ""))
    return "; ".join(bits) if bits else "identical"


# ---------------------------------------------------------------------------
# the plant - onto the artifact on disk, then read back off disk
# ---------------------------------------------------------------------------
class PlantError(Exception):
    pass


def _numeric_line_indices(lines, forced):
    if forced is not None:
        return [forced - 1]
    out = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s:
            continue
        try:
            float(s)
        except ValueError:
            continue
        out.append(i)
    return out


def plant_numeric(path, value, forced_line):
    """Add `value` to the first bare-numeric line of the artifact IN PLACE,
    then read the file back OFF DISK and prove the plant landed.  `expected`
    is the change the plant CAN produce in float - fl(old+v)-old - which is
    what a correct reader can recover (T10a's refinement of the T3 control)."""
    raw = open(path, "rb").read().decode("utf-8", "replace")
    lines = raw.split("\n")
    cands = _numeric_line_indices(lines, forced_line)
    if not cands:
        raise PlantError("no bare-numeric line to plant into")
    idx = cands[0]
    try:
        old = float(lines[idx].strip())
    except ValueError:
        raise PlantError("line %d is not numeric" % (idx + 1))
    new = old + value
    expected = new - old
    if not (expected > 0.0):
        raise PlantError("plant %r is swallowed at value %r (fl(old+p)==old)"
                         % (value, old))
    lines[idx] = repr(new)
    open(path, "wb").write("\n".join(lines).encode("utf-8"))
    back = open(path, "rb").read().decode("utf-8", "replace").split("\n")
    try:
        got = float(back[idx].strip())
    except (IndexError, ValueError):
        raise PlantError("the plant did not survive the write at line %d"
                         % (idx + 1))
    if got - old != expected:
        raise PlantError("the plant did not land: %r -> %r (expected delta %r)"
                         % (old, got, expected))
    return dict(mode="numeric", line=idx + 1, old=old, new=got,
                planted=value, expected=expected)


def plant_append(path, value):
    """Append a marker line.  For artifacts with no numeric field of their
    own; verified by reading the file back off disk."""
    raw = open(path, "rb").read()
    marker = ("\nPLANTED_PERTURBATION %r\n" % value).encode("utf-8")
    open(path, "wb").write(raw + marker)
    back = open(path, "rb").read()
    if not back.endswith(marker):
        raise PlantError("the appended plant did not survive the write")
    if len(back) - len(raw) != len(marker):
        raise PlantError("appended plant changed the file by the wrong length")
    return dict(mode="append", line=None, old=None, new=None,
                planted=value, expected=len(marker))


def apply_plant(path, mode, value, forced_line):
    if mode == "numeric":
        return plant_numeric(path, value, forced_line)
    if mode == "append":
        return plant_append(path, value)
    try:
        return plant_numeric(path, value, forced_line)
    except PlantError:
        return plant_append(path, value)


# ---------------------------------------------------------------------------
# the check
# ---------------------------------------------------------------------------
def check(reader, artifact, reader_args, case=None, plant_mode="auto",
          plant_value=DEFAULT_PLANT, plant_line=None, scrubs=(),
          timeout=DEFAULT_TIMEOUT, cwd=None, quiet=False, no_args=False,
          clean_rc=0, save_outputs=None):
    """Returns a result dict.  Never raises for a subject-side failure."""
    scrubs = list(scrubs)
    R = dict(reader=reader, artifact=artifact, verdict=None, arms={},
             delta="", restore="NOT-REACHED", exit=None, why=None)

    def say(msg):
        if not quiet:
            print(msg, flush=True)

    def keep(tag, res):
        """Retain the reader's own output so a later auditor can read what
        the instrument saw, not merely the verdict about it."""
        if not save_outputs:
            return
        os.makedirs(save_outputs, exist_ok=True)
        for stream in ("out", "err"):
            with open(os.path.join(save_outputs,
                                   "%s.%s.txt" % (tag, stream)), "w") as fh:
                fh.write(res.get(stream) or "")
        R.setdefault("saved_outputs", []).append(
            os.path.join(save_outputs, tag + ".out.txt"))

    # ---- preconditions: anything wrong here is COULD-NOT-RUN, never a FAIL
    if not os.path.isfile(reader):
        R.update(verdict="COULD-NOT-RUN", why="reader not found: %s" % reader,
                 restore="NOT-NEEDED", exit=EXIT_COULD_NOT_RUN)
        return R
    if not os.path.isfile(artifact):
        R.update(verdict="COULD-NOT-RUN",
                 why="artifact not found: %s" % artifact,
                 restore="NOT-NEEDED", exit=EXIT_COULD_NOT_RUN)
        return R
    if os.path.islink(artifact):
        R.update(verdict="COULD-NOT-RUN",
                 why="artifact is a symlink; refusing to write through it",
                 restore="NOT-NEEDED", exit=EXIT_COULD_NOT_RUN)
        return R
    if os.sep + ".git" + os.sep in os.path.abspath(artifact) + os.sep:
        R.update(verdict="COULD-NOT-RUN",
                 why="artifact is inside a .git directory; refusing",
                 restore="NOT-NEEDED", exit=EXIT_COULD_NOT_RUN)
        return R

    argv = build_argv(reader, reader_args, artifact, case, no_args=no_args)
    R["argv"] = argv
    say("reader command line (production entry point, subprocess - never an "
        "import):\n  " + " ".join(argv))

    # ---- backup, outside the case tree, with a hash
    original = open(artifact, "rb").read()
    sha_before = sha256_bytes(original)
    st = os.stat(artifact)
    times_before = (st.st_atime_ns, st.st_mtime_ns)
    bkdir = tempfile.mkdtemp(prefix="instrcheck_")
    backup = os.path.join(bkdir, os.path.basename(artifact) + ".orig")
    open(backup, "wb").write(original)
    R["sha_before"] = sha_before
    R["backup"] = backup
    R["mtime_before_ns"] = times_before[1]

    planted_info = None
    try:
        # ---- ARM 1: DOUBLE CONTROL - stability with NOTHING planted --------
        say("\nARM STABILITY (double control): the reader must be output-"
            "stable with nothing planted")
        c1 = run_reader(argv, timeout, cwd)
        if not c1["ran"]:
            R["arms"]["STABILITY"] = dict(result="COULD-NOT-RUN", why=c1["why"])
            R.update(verdict="COULD-NOT-RUN", why=c1["why"],
                     exit=EXIT_COULD_NOT_RUN)
            return R
        if c1["rc"] != clean_rc:
            # A grader that exits non-zero BY DESIGN (GATE FAIL is exit 1 in
            # several lab comparators) is auditable, but the auditor must
            # declare that expected code with --clean-rc.  Anything else on
            # the unplanted artifact is an unrelated failure and refuses:
            # rc alone cannot tell a graded FAIL from a crash.
            why = ("the reader exited %s on the UNPLANTED artifact, expected "
                   "%s (declare a by-design non-zero code with --clean-rc); "
                   "this is an unrelated failure, not a detection result: %s"
                   % (c1["rc"], clean_rc, short(c1["err"] or c1["out"])))
            R["arms"]["STABILITY"] = dict(result="COULD-NOT-RUN", why=why)
            R.update(verdict="COULD-NOT-RUN", why=why, exit=EXIT_COULD_NOT_RUN)
            return R
        keep("clean1", c1)
        c2 = run_reader(argv, timeout, cwd)
        if not c2["ran"]:
            R["arms"]["STABILITY"] = dict(result="COULD-NOT-RUN", why=c2["why"])
            R.update(verdict="COULD-NOT-RUN", why=c2["why"],
                     exit=EXIT_COULD_NOT_RUN)
            return R
        keep("clean2", c2)
        f1, f2 = fingerprint(c1, scrubs), fingerprint(c2, scrubs)
        if f1 != f2:
            why = ("the reader is NOT output-stable on the unplanted "
                   "artifact (%s); any plant would look DETECTED, so this "
                   "instrument cannot be evaluated" % describe_delta(f1, f2))
            R["arms"]["STABILITY"] = dict(result="UNSTABLE", why=why,
                                          delta=describe_delta(f1, f2))
            R.update(verdict="COULD-NOT-RUN", why=why, exit=EXIT_COULD_NOT_RUN)
            return R
        R["arms"]["STABILITY"] = dict(result="STABLE",
                                      bytes=len(f1[1]) + len(f1[2]), rc=f1[0])
        say("  STABLE: two clean runs byte-identical (rc=%s, %d B of output)"
            % (f1[0], len(f1[1]) + len(f1[2])))

        # ---- ARM 2: PLANT on disk, reader through its real CLI -------------
        say("\nARM PLANT: perturbation written onto the artifact on disk, "
            "read back off disk, reader re-run through the same CLI")
        try:
            planted_info = apply_plant(artifact, plant_mode, plant_value,
                                       plant_line)
        except PlantError as e:
            why = "the plant could not be made to land: %s" % e
            R["arms"]["PLANT"] = dict(result="COULD-NOT-RUN", why=why)
            R.update(verdict="COULD-NOT-RUN", why=why, exit=EXIT_COULD_NOT_RUN)
            return R
        except OSError as e:
            why = "the artifact is not writable: %s" % e
            R["arms"]["PLANT"] = dict(result="COULD-NOT-RUN", why=why)
            R.update(verdict="COULD-NOT-RUN", why=why, exit=EXIT_COULD_NOT_RUN)
            return R
        R["plant"] = planted_info
        sha_planted = sha256_file(artifact)
        if sha_planted == sha_before:
            why = "the artifact hash did not change under the plant"
            R["arms"]["PLANT"] = dict(result="COULD-NOT-RUN", why=why)
            R.update(verdict="COULD-NOT-RUN", why=why, exit=EXIT_COULD_NOT_RUN)
            return R
        say("  plant landed: %s" % json.dumps(planted_info, default=repr))
        say("  artifact sha %s -> %s" % (sha_before[:12], sha_planted[:12]))

        pr = run_reader(argv, timeout, cwd)
        if not pr["ran"]:
            why = "reader could not be re-run under the plant: %s" % pr["why"]
            R["arms"]["PLANT"] = dict(result="COULD-NOT-RUN", why=why)
            R.update(verdict="COULD-NOT-RUN", why=why, exit=EXIT_COULD_NOT_RUN)
            return R
        keep("planted", pr)
        fp = fingerprint(pr, scrubs)
        delta = describe_delta(f1, fp)
        R["delta"] = delta
        if fp != f1:
            R["arms"]["PLANT"] = dict(result="DETECTED", delta=delta,
                                      rc_clean=f1[0], rc_planted=fp[0])
            R.update(verdict="DETECTED", exit=EXIT_DETECTED)
            say("  DETECTED: %s" % delta)
        else:
            R["arms"]["PLANT"] = dict(result="NOT-DETECTED", delta="identical",
                                      rc_clean=f1[0], rc_planted=fp[0])
            R.update(verdict="NOT-DETECTED", exit=EXIT_NOT_DETECTED,
                     why=("the reader's output is byte-identical with the "
                          "perturbation on disk; it cannot see the artifact "
                          "through its production entry point"))
            say("  NOT-DETECTED: output byte-identical with the plant on disk")
        return R

    finally:
        # ---- restore, byte-for-byte, verified by hash, in this invocation --
        try:
            open(artifact, "wb").write(original)
            # mtime as well as bytes: OpenFOAM completion guards date a run by
            # the field's mtime against the case's own 0/T (the age guard), so
            # an audit must not re-date the artifact it audits.
            os.utime(artifact, ns=times_before)
            sha_after = sha256_file(artifact)
            mtime_after = os.stat(artifact).st_mtime_ns
            R["mtime_after_ns"] = mtime_after
            if sha_after == sha_before and mtime_after == times_before[1]:
                R["restore"] = "OK"
                R["sha_after"] = sha_after
                say("\nRESTORE OK: %s back to sha %s, mtime_ns %d"
                    % (artifact, sha_after[:12], mtime_after))
                shutil.rmtree(bkdir, ignore_errors=True)
            else:
                R["restore"] = "FAILED"
                R["sha_after"] = sha_after
                R["exit"] = EXIT_RESTORE_FAILED
                say("\nRESTORE FAILED: %s is sha %s (expected %s), mtime_ns "
                    "%d (expected %d). The untouched original is kept at %s"
                    % (artifact, sha_after[:12], sha_before[:12],
                       mtime_after, times_before[1], backup))
        except OSError as e:
            R["restore"] = "FAILED"
            R["exit"] = EXIT_RESTORE_FAILED
            say("\nRESTORE FAILED (%s). The untouched original is kept at %s"
                % (e, backup))


def status_line(R):
    return ("STAGE2 INSTRUMENT %s reader=%s artifact=%s delta=%s"
            % (R["verdict"], os.path.basename(R["reader"]),
               R["artifact"], short(R["delta"] or (R["why"] or "-"), 90)))


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------
TOY_HONEST = '''#!/usr/bin/env python3
"""Toy production reader that genuinely reads the artifact."""
import sys


def _nums(path):
    out = []
    for tok in open(path).read().split():
        try:
            out.append(float(tok))
        except ValueError:
            pass
    return out


def main():
    v = _nums(sys.argv[1])
    print("n %d" % len(v))
    print("sum %.17g" % sum(v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

TOY_CONSTANT = '''#!/usr/bin/env python3
"""Toy reader that IGNORES the artifact and prints a constant.
This is the check_filing.py shape: green, and about the code not the world."""
import sys


def main():
    print("n 3")
    print("sum 6")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

TOY_SHORTCUT = '''#!/usr/bin/env python3
"""THE SHORTCUT TRAP.  detect() genuinely reads the artifact, so an
in-process caller sees the plant.  The CLI - what production runs - ignores
the artifact entirely and prints a constant.  This is the mark_done_k0h.py
clause-7 shape: a selftest driving the function passes green over zero call
sites."""
import sys


def detect(path):
    out = []
    for tok in open(path).read().split():
        try:
            out.append(float(tok))
        except ValueError:
            pass
    return sum(out)


def main():
    print("sum 6")          # the CLI never calls detect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

TOY_UNSTABLE = '''#!/usr/bin/env python3
"""Toy reader whose output drifts run to run.  Any plant would look
DETECTED against it - the false pass the double control exists to catch."""
import os
import sys
import time


def main():
    open(sys.argv[1]).read()
    print("nonce %d-%d" % (os.getpid(), time.time_ns()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

TOY_ERRORS = '''#!/usr/bin/env python3
"""Toy reader that fails for a reason unrelated to the plant."""
import sys


def main():
    sys.stderr.write("cannot open the mesh: unrelated failure\\n")
    return 3


if __name__ == "__main__":
    sys.exit(main())
'''

ARTIFACT_TEXT = "1.0\n2.0\n3.0\n"


def selftest():
    """Every arm plus the trap, plus a restore check after each arm.
    No bare assert anywhere: failures are recorded and counted."""
    fails = []
    n = [0]

    def t(name, cond, note=""):
        n[0] += 1
        ok = bool(cond)
        print("  [%s] %s%s" % ("ok" if ok else "FAIL", name,
                               ("  -- " + note) if note and not ok else ""))
        if not ok:
            fails.append(name)

    root = tempfile.mkdtemp(prefix="instrcheck_selftest_")
    print("check_instrument_detects_plant.py --selftest")
    print("scratch: %s" % root)
    print("optimisation level: %s (python3 -O strips bare asserts; this "
          "selftest uses none)" % ("-O" if not __debug__ else "none"))
    try:
        readers = {}
        for name, src in (("toy_honest.py", TOY_HONEST),
                          ("toy_constant.py", TOY_CONSTANT),
                          ("toy_shortcut.py", TOY_SHORTCUT),
                          ("toy_unstable.py", TOY_UNSTABLE),
                          ("toy_errors.py", TOY_ERRORS)):
            p = os.path.join(root, name)
            open(p, "w").write(src)
            os.chmod(p, 0o755)
            readers[name] = p

        art = os.path.join(root, "artifact.dat")

        def fresh_artifact():
            open(art, "w").write(ARTIFACT_TEXT)
            return sha256_file(art)

        # ---- POSITIVE ------------------------------------------------------
        print("\n(1) POSITIVE: a reader that genuinely reads the artifact")
        sha0 = fresh_artifact()
        R = check(readers["toy_honest.py"], art, [], quiet=True)
        t("honest reader -> DETECTED", R["verdict"] == "DETECTED",
          str(R.get("verdict")) + " " + str(R.get("why")))
        t("honest reader -> exit 0", R["exit"] == EXIT_DETECTED, str(R["exit"]))
        t("STABILITY arm reported STABLE",
          R["arms"].get("STABILITY", {}).get("result") == "STABLE")
        t("delta is non-empty and names stdout", "stdout" in (R["delta"] or ""),
          repr(R.get("delta")))
        t("restore verified OK", R["restore"] == "OK", str(R["restore"]))
        t("artifact hash unchanged after arm 1", sha256_file(art) == sha0)
        t("artifact mtime restored too (the age guard dates runs by mtime)",
          R.get("mtime_after_ns") == R.get("mtime_before_ns"),
          "%s != %s" % (R.get("mtime_after_ns"), R.get("mtime_before_ns")))

        # ---- NEGATIVE - the arm that matters -------------------------------
        print("\n(2) NEGATIVE (the check_filing.py shape): a reader that "
              "ignores the artifact and prints a constant")
        sha0 = fresh_artifact()
        R = check(readers["toy_constant.py"], art, [], quiet=True)
        t("constant reader -> NOT-DETECTED", R["verdict"] == "NOT-DETECTED",
          str(R.get("verdict")))
        t("constant reader -> non-zero exit", R["exit"] != 0, str(R["exit"]))
        t("constant reader -> exit is exactly NOT-DETECTED (1)",
          R["exit"] == EXIT_NOT_DETECTED, str(R["exit"]))
        t("NOT-DETECTED is not reported as COULD-NOT-RUN",
          R["exit"] != EXIT_COULD_NOT_RUN)
        t("restore verified OK", R["restore"] == "OK", str(R["restore"]))
        t("artifact hash unchanged after arm 2", sha256_file(art) == sha0)

        # ---- THE SHORTCUT TRAP ---------------------------------------------
        print("\n(3) SHORTCUT TRAP (the mark_done_k0h.py shape): detect() sees "
              "the plant in-process; the CLI does not")
        sha0 = fresh_artifact()
        # demonstrate that an IMPORTING check would have said DETECTED
        probe = os.path.join(root, "probe_copy.dat")
        shutil.copy(art, probe)
        pre = subprocess.run(
            [sys.executable, "-c",
             "import importlib.util,sys;"
             "s=importlib.util.spec_from_file_location('sc',sys.argv[1]);"
             "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
             "print(m.detect(sys.argv[2]))",
             readers["toy_shortcut.py"], probe],
            stdout=subprocess.PIPE).stdout.decode().strip()
        with open(probe, "w") as fh:
            fh.write("1.00123400\n2.0\n3.0\n")
        post = subprocess.run(
            [sys.executable, "-c",
             "import importlib.util,sys;"
             "s=importlib.util.spec_from_file_location('sc',sys.argv[1]);"
             "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
             "print(m.detect(sys.argv[2]))",
             readers["toy_shortcut.py"], probe],
            stdout=subprocess.PIPE).stdout.decode().strip()
        t("in-process detect() DOES see a plant (so the trap is real)",
          pre != post, "%r == %r" % (pre, post))
        R = check(readers["toy_shortcut.py"], art, [], quiet=True)
        t("through the CLI -> NOT-DETECTED", R["verdict"] == "NOT-DETECTED",
          str(R.get("verdict")))
        t("shortcut reader -> exit 1", R["exit"] == EXIT_NOT_DETECTED,
          str(R["exit"]))
        t("the check never imported the reader (argv is a subprocess call)",
          R["argv"][0] == sys.executable
          and R["argv"][1] == readers["toy_shortcut.py"], str(R.get("argv")))
        t("restore verified OK", R["restore"] == "OK", str(R["restore"]))
        t("artifact hash unchanged after arm 3", sha256_file(art) == sha0)

        # ---- DOUBLE CONTROL: an unstable reader ----------------------------
        print("\n(4) DOUBLE CONTROL: a reader whose output drifts must be "
              "COULD-NOT-RUN, never DETECTED")
        sha0 = fresh_artifact()
        R = check(readers["toy_unstable.py"], art, [], quiet=True)
        t("unstable reader -> COULD-NOT-RUN",
          R["verdict"] == "COULD-NOT-RUN", str(R.get("verdict")))
        t("unstable reader is NOT reported DETECTED",
          R["verdict"] != "DETECTED")
        t("STABILITY arm named it UNSTABLE",
          R["arms"].get("STABILITY", {}).get("result") == "UNSTABLE",
          str(R["arms"]))
        t("unstable reader -> exit 2", R["exit"] == EXIT_COULD_NOT_RUN,
          str(R["exit"]))
        t("artifact hash unchanged after arm 4", sha256_file(art) == sha0)

        # ---- COULD-NOT-RUN: missing reader ---------------------------------
        print("\n(5) COULD-NOT-RUN: reader path absent, artifact absent, "
              "reader errors for an unrelated reason")
        sha0 = fresh_artifact()
        R = check(os.path.join(root, "no_such_reader.py"), art, [], quiet=True)
        t("missing reader -> COULD-NOT-RUN", R["verdict"] == "COULD-NOT-RUN",
          str(R.get("verdict")))
        t("missing reader -> exit 2 (distinct from NOT-DETECTED 1)",
          R["exit"] == EXIT_COULD_NOT_RUN and EXIT_COULD_NOT_RUN
          != EXIT_NOT_DETECTED, str(R["exit"]))
        R = check(readers["toy_honest.py"], os.path.join(root, "no_such.dat"),
                  [], quiet=True)
        t("missing artifact -> COULD-NOT-RUN exit 2",
          R["verdict"] == "COULD-NOT-RUN" and R["exit"] == EXIT_COULD_NOT_RUN)
        R = check(readers["toy_errors.py"], art, [], quiet=True)
        t("reader erroring on the CLEAN artifact -> COULD-NOT-RUN",
          R["verdict"] == "COULD-NOT-RUN", str(R.get("verdict")))
        t("unrelated error is not reported as NOT-DETECTED",
          R["verdict"] != "NOT-DETECTED")
        t("artifact hash unchanged after arm 5", sha256_file(art) == sha0)

        # ---- by-design non-zero rc, and --no-args --------------------------
        print("\n(5b) a grader that exits non-zero BY DESIGN, and a reader "
              "invoked with no arguments at all")
        sha0 = fresh_artifact()
        R = check(readers["toy_errors.py"], art, [], quiet=True, clean_rc=3)
        t("declared clean-rc 3 gets past the refusal and is graded",
          R["verdict"] in ("DETECTED", "NOT-DETECTED"), str(R.get("verdict")))
        t("a rc-3 reader that ignores the artifact is NOT-DETECTED",
          R["verdict"] == "NOT-DETECTED", str(R.get("verdict")))
        t("an UNDECLARED rc-3 reader is still COULD-NOT-RUN",
          check(readers["toy_errors.py"], art, [], quiet=True)["verdict"]
          == "COULD-NOT-RUN")
        R = check(readers["toy_constant.py"], art, [], quiet=True,
                  no_args=True)
        t("--no-args passes no argument at all",
          len(R["argv"]) == 2 and R["argv"][1] == readers["toy_constant.py"],
          str(R.get("argv")))
        t("artifact hash unchanged after arm 5b", sha256_file(art) == sha0)

        # ---- RESTORE under a reader that MUTATES the artifact --------------
        print("\n(6) RESTORE: the artifact is put back byte-for-byte even "
              "when the plant path is exercised repeatedly")
        sha0 = fresh_artifact()
        mt0 = os.stat(art).st_mtime_ns
        for _ in range(3):
            check(readers["toy_honest.py"], art, [], quiet=True)
        t("hash still identical after three planted runs",
          sha256_file(art) == sha0, sha256_file(art))
        t("mtime still identical after three planted runs",
          os.stat(art).st_mtime_ns == mt0)
        t("artifact bytes still identical",
          open(art).read() == ARTIFACT_TEXT)

        # ---- retained outputs ----------------------------------------------
        print("\n(6b) --save-outputs retains what the reader itself printed")
        sha0 = fresh_artifact()
        odir = os.path.join(root, "kept")
        R = check(readers["toy_honest.py"], art, [], quiet=True,
                  save_outputs=odir)
        kept = sorted(os.listdir(odir)) if os.path.isdir(odir) else []
        t("clean and planted outputs both retained",
          "clean1.out.txt" in kept and "clean2.out.txt" in kept
          and "planted.out.txt" in kept, str(kept))
        t("the retained planted output differs from the retained clean one",
          open(os.path.join(odir, "planted.out.txt")).read()
          != open(os.path.join(odir, "clean1.out.txt")).read())
        t("artifact hash unchanged after arm 6b", sha256_file(art) == sha0)

        # ---- status line ---------------------------------------------------
        print("\n(7) status line for stage 6")
        sha0 = fresh_artifact()
        R = check(readers["toy_honest.py"], art, [], quiet=True)
        sl = status_line(R)
        print("  " + sl)
        t("status line starts with STAGE2 INSTRUMENT",
          sl.startswith("STAGE2 INSTRUMENT "))
        t("status line carries the verdict, reader, artifact and delta",
          " DETECTED " in sl and "reader=toy_honest.py" in sl
          and "artifact=" in sl and "delta=" in sl, sl)

        # ---- no bare asserts in this file ----------------------------------
        print("\n(8) no bare `assert` in this file (python3 -O strips them, "
              "D594/L-332)")
        import ast
        src = open(os.path.abspath(__file__), "rb").read().decode("utf-8")
        n_assert = sum(1 for node in ast.walk(ast.parse(src))
                       if isinstance(node, ast.Assert))
        t("ast.Assert node count == 0", n_assert == 0, "found %d" % n_assert)

    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("\n%d checks, %d failed" % (n[0], len(fails)))
    if fails:
        print("FAILED: " + "; ".join(fails))
        return 1
    print("SELFTEST PASS")
    return 0


# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="CASE PROTOCOL stage 2 instrument check: a grading reader "
                    "must detect a planted perturbation through its real CLI.")
    ap.add_argument("--reader", help="path to the grading reader script")
    ap.add_argument("--artifact", help="the file on disk the reader consumes")
    ap.add_argument("--reader-arg", action="append", default=[],
                    help="argument for the reader's CLI; {artifact} and "
                         "{case} are substituted. Repeatable. Default: the "
                         "artifact path as the single argument.")
    ap.add_argument("--case", default=None, help="case directory, for {case}")
    ap.add_argument("--plant-mode", default="auto",
                    choices=["auto", "numeric", "append"])
    ap.add_argument("--plant-value", type=float, default=DEFAULT_PLANT)
    ap.add_argument("--plant-line", type=int, default=None,
                    help="1-based line to plant into (numeric mode)")
    ap.add_argument("--scrub", action="append", default=[],
                    help="regex masked in BOTH clean and planted output")
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    ap.add_argument("--no-args", action="store_true",
                    help="invoke the reader with NO arguments (readers that "
                         "locate their case relative to their own __file__)")
    ap.add_argument("--clean-rc", type=int, default=0,
                    help="exit code the reader returns by design on the "
                         "unplanted artifact (default 0). Any other code on "
                         "the clean run is COULD-NOT-RUN.")
    ap.add_argument("--cwd", default=None,
                    help="working directory for the reader subprocess")
    ap.add_argument("--save-outputs", default=None,
                    help="directory to retain the reader's own stdout/stderr "
                         "for the clean and planted runs")
    ap.add_argument("--json", default=None, help="write the result dict here")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    if not a.reader or not a.artifact:
        print("REFUSE: --reader and --artifact are both required "
              "(or use --selftest)")
        return EXIT_COULD_NOT_RUN

    R = check(a.reader, a.artifact, a.reader_arg, case=a.case,
              plant_mode=a.plant_mode, plant_value=a.plant_value,
              plant_line=a.plant_line, scrubs=a.scrub, timeout=a.timeout,
              cwd=a.cwd, no_args=a.no_args, clean_rc=a.clean_rc,
              save_outputs=a.save_outputs)
    print("\nRESTORE %s" % R["restore"])
    print(status_line(R))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(R, fh, indent=2, default=repr)
    return R["exit"]


if __name__ == "__main__":
    sys.exit(main())
