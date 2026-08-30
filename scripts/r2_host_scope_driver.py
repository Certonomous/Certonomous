#!/usr/bin/env python3
"""R2 -- THE QUEUE-VALIDATOR HOST-SCOPE REPAIR DRIVER.

Registration : verification/campaign/R2_QUEUE_HOST_SCOPE_REPAIR_PREREGISTRATION.md
Specification: docs/standards/QUEUE_ENTRY_HOST_SCOPE.md, frozen at
               ed77957c4e56cd12e1d5d0c620b218805bd4306b

WHAT THIS PROGRAM WILL NOT DO
  * It will not grade without --prereg-commit, and it VERIFIES that sha by hashing the
    registration on disk against its committed blob (rule 2; reference implementation
    cases/F26_RINGLEB/grade_f26d.py:419-431).
  * It will not grade until the two repairs its controls exist to measure are ACTUALLY
    PRESENT in the production instruments.  H1-H14 are all statements about a repaired
    `validate()`; run against the unrepaired one they would be measuring the defect and
    reporting it as a control vector.  The driver detects the repair and, if it is
    absent, prints BLOCKED, names the precondition and exits 2.  It does not degrade.
  * It will not grade until its BIRTH CONTROL has been driven -- the entry H9/H10 read
    must have been WRITTEN BY queue_runner.launch() and carry the `_launch` and
    `_field_classes` keys only :522/:526-535 add.  A hand-composed entry dict is a
    schema the producer never emitted and is REFUSED (Sanaa 2026-08-28T17:01Z).
  * It will not touch anything under verification/queue/.  Every control runs in a
    tempfile tree of PRODUCTION'S SHAPE, <scratch>/.../verification/queue/<team>/.
  * It will not restart, signal or race the live `queue_runner.py --daemon`.
  * It carries ZERO assert statements and refuses under `python3 -O` (L-332).
"""

import argparse
import ast
import hashlib
import importlib.util
import inspect
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

PREREG = "verification/campaign/R2_QUEUE_HOST_SCOPE_REPAIR_PREREGISTRATION.md"
SPEC = "docs/standards/QUEUE_ENTRY_HOST_SCOPE.md"
SPEC_COMMIT = "ed77957c4e56cd12e1d5d0c620b218805bd4306b"
FREEZE_COMMIT = "f7da1a24ca8c730d5c49a7ea429840c43378bf1e"

VALIDATOR = os.path.join(REPO, "scripts", "queue_entry_check.py")
RUNNER = os.path.join(REPO, "scripts", "queue_runner.py")
QUEUE_ROOT = os.path.join(REPO, "verification", "queue")
RUN_ROOT = os.path.join(REPO, "verification", "runs", "TOOLING_REPAIRS",
                        "R2_QUEUE_HOST_SCOPE_2026-08-28")

CAP_CORE_MIN = 1.2000
EST_CORE_MIN = 0.8100
RANKS = 1
CAP_WALL_S = CAP_CORE_MIN * 60.0 / RANKS      # 72.0 s

SHIPPED = [os.path.join(HERE, "r2_host_scope_driver.py")]


class Refusal(Exception):
    pass


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def _git(args):
    return subprocess.run(["git"] + list(args), cwd=REPO, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True)


def blob_sha1(path):
    data = io.open(path, "rb").read()
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def verify_freeze(commit, relpath):
    out = _git(["rev-parse", "%s:%s" % (commit, relpath)])
    if out.returncode != 0:
        raise Refusal("FREEZE: %s:%s does not resolve -- %s"
                      % (commit, relpath, out.stderr.strip()))
    want = out.stdout.strip()
    disk = os.path.join(REPO, relpath)
    if not os.path.isfile(disk):
        raise Refusal("FREEZE: %s is not on disk" % disk)
    got = blob_sha1(disk)
    if got != want:
        raise Refusal("FREEZE: %s on disk (blob %s) is NOT the committed blob %s at %s."
                      % (relpath, got[:12], want[:12], commit))
    return want


def sha256_file(p):
    h = hashlib.sha256()
    with io.open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_tree(root):
    out = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d != "__pycache__"]
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            out[os.path.relpath(p, REPO)] = sha256_file(p)
    return out


def ast_assert_census(paths):
    out = {}
    for p in paths:
        tree = ast.parse(io.open(p, encoding="utf-8").read())
        out[os.path.basename(p)] = sum(1 for n in ast.walk(tree)
                                       if isinstance(n, ast.Assert))
    return out


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# THE REPAIR DETECTORS -- each shown able to report BOTH answers
# ---------------------------------------------------------------------------

def validator_repair_state(path):
    """Is the host-scope repair present in this queue_entry_check.py?

    The repair is defined by QUEUE_ENTRY_HOST_SCOPE.md sec.5.1 as a POSITIONAL,
    REQUIRED `unevaluated` parameter on validate() -- never a default of None, which
    is the silent skip the spec exists to forbid.  So the signature IS the detector.
    """
    mod = _load(path, "qec_probe_%d" % os.getpid())
    if not hasattr(mod, "validate"):
        return dict(present=False, why="no validate() in %s" % path)
    sig = inspect.signature(mod.validate)
    p = sig.parameters.get("unevaluated")
    if p is None:
        return dict(present=False, signature=str(sig),
                    why=("validate() has no `unevaluated` parameter. The NOT EVALUATED "
                         "channel does not exist, so every host-sensitive clause this "
                         "item narrows would be narrowed SILENTLY -- a skipped clause "
                         "indistinguishable from a passed one, which is the exact "
                         "confusion QUEUE_ENTRY_HOST_SCOPE.md sec.5 exists to prevent."))
    if p.default is not inspect.Parameter.empty:
        return dict(present=False, signature=str(sig),
                    why=("`unevaluated` carries a default (%r). Spec sec.5.1: it is "
                         "NEVER given a default -- a caller that cannot receive the "
                         "not-evaluated report must raise TypeError at the call."
                         % (p.default,)))
    if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                      inspect.Parameter.POSITIONAL_ONLY):
        return dict(present=False, signature=str(sig),
                    why="`unevaluated` is %s, not positional" % p.kind)
    return dict(present=True, signature=str(sig))


def runner_repair_state(path):
    """Is the sec.5.4 permitted edit present in this queue_runner.py?

    STATIC, and declared static: this reads the source text of the two permitted edits
    (an `unevaluated` sink handed to validate(), and the NOT-EVALUATED emission loop
    immediately after).  It is NOT a behavioural check and is not dressed as one.
    """
    src = io.open(path, encoding="utf-8").read()
    has_sink = "qec.validate(entry, REPO, path, " in src
    has_loop = "NOT-EVALUATED" in src
    if has_sink and has_loop:
        return dict(present=True, kind="STATIC source check")
    return dict(present=False, kind="STATIC source check",
                sink_arg_at_validate_call=has_sink, not_evaluated_emission=has_loop,
                why=("QUEUE_ENTRY_HOST_SCOPE.md sec.5.4 permits EXACTLY two edits to "
                     "queue_runner.py: an `unevaluated` sink list handed to validate() "
                     "at :702, and a loop emitting one NOT-EVALUATED log line per "
                     "element immediately after. Neither is present."))


def birth_readiness(validator_path, runner_path):
    """BR-1's producer/reader wiring, checked before any control may claim a result.

    The producer is queue_runner.launch(): :515 launched_dir, :517 dst, :520
    shutil.move, :536 dst.write_text of entry + _launch (:522) + _field_classes
    (:526-535).  The reader is queue_entry_check.validate() reached through tick() at
    :702.  If the producer no longer writes those keys, or the reader is no longer
    reached from tick(), then H9/H10 would be reading something other than production
    and the control vector would be about the control, not about the code.
    """
    src = io.open(runner_path, encoding="utf-8").read()
    missing = [k for k in ('meta["_launch"]', 'meta["_field_classes"]',
                           "dst.write_text(", "shutil.move(",
                           "qec.validate(entry, REPO, path")
               if k not in src]
    if missing:
        return dict(ready=False, missing=missing,
                    why=("THE PRODUCER OR THE READER HAS MOVED. BR-1 requires that the "
                         "entry H9/H10 operate on was written by queue_runner.launch() "
                         "and carries the _launch and _field_classes keys only "
                         ":522/:526-535 add, and that validate() is reached through "
                         "tick(). A hand-composed entry lacking them is refused: it is "
                         "a schema the producer never emitted."))
    return dict(ready=True,
                producer="queue_runner.py::launch() :515/:517/:520/:522/:526-535/:536",
                reader="queue_entry_check.validate() via queue_runner.py::tick() :702")


# ---------------------------------------------------------------------------
# THE DRIVER'S OWN CONTROLS
# ---------------------------------------------------------------------------

def _both(name, positive, negative, out):
    try:
        pdetail = positive()
    except Exception as e:                                        # noqa: BLE001
        refuse("SELFTEST control %s: the POSITIVE limb failed (%s: %s)."
               % (name, type(e).__name__, e))
    fired = False
    try:
        negative()
    except Exception as e:                                        # noqa: BLE001
        fired, ndetail = True, "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:90])
    if not fired:
        refuse("SELFTEST control %s: the NEGATIVE limb DID NOT FIRE. The check accepted "
               "an input it must refuse; it is measuring nothing." % name)
    out.append((name, pdetail, ndetail))


REPAIRED_STUB = '''
def validate(entry, root, entry_path, unevaluated, checks=None, require_binding=False):
    return []
'''

UNREPAIRED_STUB = '''
def validate(entry, root, entry_path, checks=None, require_binding=False):
    return []
'''

DEFAULTED_STUB = '''
def validate(entry, root, entry_path, unevaluated=None, checks=None,
             require_binding=False):
    return []
'''


def _stub(tmp, name, body):
    p = os.path.join(tmp, name)
    io.open(p, "w", encoding="utf-8").write(body)
    return p


def selftest():
    out = []

    def e1p():
        return "prereg blob %s at %s" % (verify_freeze(FREEZE_COMMIT, PREREG)[:12],
                                         FREEZE_COMMIT[:12])

    def e1n():
        verify_freeze(FREEZE_COMMIT, "verification/campaign/__no_such_file__.md")
    _both("E1-PREREG-SHA", e1p, e1n, out)

    def e1bp():
        return "blob_sha1 reader -> %s" % blob_sha1(os.path.join(REPO, PREREG))[:12]

    def e1bn():
        tmp = tempfile.mkdtemp(prefix="e1bn_")
        try:
            p = os.path.join(tmp, "m.md")
            io.open(p, "wb").write(io.open(os.path.join(REPO, PREREG), "rb").read() + b"x")
            want = _git(["rev-parse", "%s:%s" % (FREEZE_COMMIT, PREREG)]).stdout.strip()
            if blob_sha1(p) == want:
                raise Refusal("READER BLIND: a one-byte change produced the same blob")
            raise Refusal("PLANTED ONE-BYTE CHANGE SEEN: %s != %s"
                          % (blob_sha1(p)[:12], want[:12]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("E1b-SHA-SEES-1BYTE", e1bp, e1bn, out)

    def e2p():
        return "spec blob %s at %s" % (verify_freeze(SPEC_COMMIT, SPEC)[:12],
                                       SPEC_COMMIT[:12])

    def e2n():
        verify_freeze("0" * 40, SPEC)
    _both("E2-SPEC-FREEZE", e2p, e2n, out)

    # E3 -- the repair detector, shown to return BOTH answers on planted signatures.
    def e3p():
        tmp = tempfile.mkdtemp(prefix="e3p_")
        try:
            st = validator_repair_state(_stub(tmp, "qec_ok.py", REPAIRED_STUB))
            if not st["present"]:
                raise Refusal("DETECTOR BLIND to a REPAIRED signature: %r" % st)
            return "detector says PRESENT on a planted repaired signature"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def e3n():
        tmp = tempfile.mkdtemp(prefix="e3n_")
        try:
            a = validator_repair_state(_stub(tmp, "qec_bad.py", UNREPAIRED_STUB))
            b = validator_repair_state(_stub(tmp, "qec_def.py", DEFAULTED_STUB))
            if a["present"] or b["present"]:
                raise Refusal("DETECTOR BLIND: it accepted an unrepaired (%r) or a "
                              "None-defaulted (%r) signature" % (a, b))
            raise Refusal("PLANTED DEFECTS SEEN: unrepaired and None-defaulted "
                          "signatures both reported ABSENT")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("E3-VALIDATOR-DETECTOR", e3p, e3n, out)

    # E4 -- the runner-edit detector, same discipline.
    def e4p():
        tmp = tempfile.mkdtemp(prefix="e4p_")
        try:
            p = _stub(tmp, "qr_ok.py",
                      'x = qec.validate(entry, REPO, path, unevaluated)\n'
                      'log("NOT-EVALUATED %s" % u)\n')
            st = runner_repair_state(p)
            if not st["present"]:
                raise Refusal("DETECTOR BLIND to a planted repaired runner: %r" % st)
            return "detector says PRESENT on a planted repaired runner"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def e4n():
        tmp = tempfile.mkdtemp(prefix="e4n_")
        try:
            p = _stub(tmp, "qr_bad.py", "x = qec.validate(entry, REPO, path)\n")
            st = runner_repair_state(p)
            if st["present"]:
                raise Refusal("DETECTOR BLIND: accepted an unrepaired runner")
            raise Refusal("PLANTED DEFECT SEEN: unrepaired runner reported ABSENT")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("E4-RUNNER-DETECTOR", e4p, e4n, out)

    # E5 -- the birth-readiness reader, shown able to see a producer that moved.
    def e5p():
        st = birth_readiness(VALIDATOR, RUNNER)
        if not st["ready"]:
            raise Refusal("BIRTH WIRING BROKEN in production: %r" % st)
        return "producer and reader both located in the production runner"

    def e5n():
        tmp = tempfile.mkdtemp(prefix="e5n_")
        try:
            p = _stub(tmp, "qr_moved.py", "# a runner with no launch() at all\n")
            st = birth_readiness(VALIDATOR, p)
            if st["ready"]:
                raise Refusal("READER BLIND: a runner with no producer reported ready")
            raise Refusal("PLANTED MOVE SEEN: missing %r" % st["missing"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("E5-BIRTH-READINESS", e5p, e5n, out)

    # E6 -- the AST census, shown able to see a planted assert.
    def e6p():
        c = ast_assert_census(SHIPPED)
        if sum(c.values()) != 0:
            raise Refusal("shipped path carries %d ast.Assert node(s): %r"
                          % (sum(c.values()), c))
        return "0 ast.Assert over %d shipped file(s)" % len(c)

    def e6n():
        tmp = tempfile.mkdtemp(prefix="e6n_")
        try:
            p = _stub(tmp, "planted.py", "def f(x):\n    assert x\n")
            c = ast_assert_census([p])
            if sum(c.values()) != 1:
                raise Refusal("CENSUS BLIND: planted 1, saw %d" % sum(c.values()))
            raise Refusal("PLANTED ASSERT SEEN: %r" % c)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("E6-AST-CENSUS", e6p, e6n, out)

    # E7 -- flag proof, driven as a real subprocess in both directions.
    def e7p():
        p = subprocess.run([sys.executable, __file__, "--probe"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if p.returncode != 0:
            raise Refusal("probe without -O returned rc %d" % p.returncode)
        return "no -O: rc 0"

    def e7n():
        p = subprocess.run([sys.executable, "-O", __file__, "--probe"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if p.returncode != 2:
            raise Refusal("-O returned rc %d, want 2" % p.returncode)
        raise Refusal("-O CORRECTLY REFUSED with rc 2")
    _both("E7-FLAG-PROOF", e7p, e7n, out)

    # E8 -- the queue-invariance reader, shown able to see a planted byte.
    def e8p():
        s = sha256_tree(QUEUE_ROOT)
        if not s:
            raise Refusal("the queue tree hashed to nothing")
        return "%d files under verification/queue/ hashed" % len(s)

    def e8n():
        tmp = tempfile.mkdtemp(prefix="e8n_")
        try:
            a = os.path.join(tmp, "f")
            io.open(a, "w").write("one")
            h = sha256_file(a)
            io.open(a, "w").write("onf")
            if sha256_file(a) == h:
                raise Refusal("HASHER BLIND")
            raise Refusal("PLANTED BYTE SEEN: %s -> %s" % (h[:12], sha256_file(a)[:12]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("E8-QUEUE-INVARIANCE", e8p, e8n, out)

    # E9 -- the precondition gate itself: BLOCKED when absent, admits when present.
    def e9p():
        tmp = tempfile.mkdtemp(prefix="e9p_")
        try:
            v = _stub(tmp, "qec_ok.py", REPAIRED_STUB)
            r = _stub(tmp, "qr_ok.py",
                      'x = qec.validate(entry, REPO, path, unevaluated)\n'
                      'log("NOT-EVALUATED %s" % u)\n'
                      'meta["_launch"] = 1\nmeta["_field_classes"] = 2\n'
                      'dst.write_text(x)\nshutil.move(a, b)\n')
            state = preconditions(v, r)
            if not state["all_met"]:
                raise Refusal("gate refused a fully repaired pair: %r" % state)
            return "gate ADMITS a fully repaired pair"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def e9n():
        state = preconditions(VALIDATOR, RUNNER)
        if state["all_met"]:
            raise Refusal("gate ADMITTED the production pair -- but the repair is "
                          "supposed to be absent; re-read the finding, not the gate")
        raise Refusal("PRODUCTION PAIR CORRECTLY BLOCKED: %s"
                      % "; ".join(state["unmet"]))
    _both("E9-PRECONDITION-GATE", e9p, e9n, out)

    print("R2 DRIVER SELFTEST -- controls fired, each in BOTH directions")
    print("=" * 78)
    for name, p, n in out:
        print("  %-24s POSITIVE %s" % (name, p))
        print("  %-24s NEGATIVE fired: %s" % ("", n))
    print("=" * 78)
    print("%d controls fired, each shown able to fail" % len(out))
    print("assert census over the shipped path: %s" % json.dumps(ast_assert_census(SHIPPED)))
    print("__debug__ = %s (this run is NOT under -O)" % __debug__)
    return 0


def preconditions(validator_path, runner_path):
    v = validator_repair_state(validator_path)
    r = runner_repair_state(runner_path)
    b = birth_readiness(validator_path, runner_path)
    unmet = []
    if not v["present"]:
        unmet.append("P-VALIDATOR: %s" % v.get("why", "repair absent"))
    if not r["present"]:
        unmet.append("P-RUNNER: %s" % r.get("why", "permitted edits absent"))
    if not b["ready"]:
        unmet.append("P-BIRTH: %s" % b.get("why", "producer/reader wiring moved"))
    return dict(validator=v, runner=r, birth=b, unmet=unmet, all_met=not unmet)


def grade(freeze_commit):
    t0 = time.time()
    prereg_blob = verify_freeze(freeze_commit, PREREG)
    spec_blob = verify_freeze(SPEC_COMMIT, SPEC)
    state = preconditions(VALIDATOR, RUNNER)
    if not state["all_met"]:
        sys.stderr.write(
            "\nBLOCKED\n"
            "=======\n"
            "R2's enqueue preconditions are NOT met at launch, so nothing is graded.\n"
            "R2_QUEUE_HOST_SCOPE_REPAIR_PREREGISTRATION.md sec.8 clause 1.\n\n")
        for u in state["unmet"]:
            sys.stderr.write("  UNMET  %s\n\n" % u)
        sys.stderr.write(
            "H1-H14 are every one of them statements about a REPAIRED validate().\n"
            "Driven against the unrepaired one they would measure the defect and\n"
            "report it as a control vector -- a well-formed wrong answer, which is\n"
            "exactly the instrument class this lab keeps finding. Refused, not\n"
            "degraded (rule 4).\n\n"
            "WHAT LIFTS IT: the two permitted edits of QUEUE_ENTRY_HOST_SCOPE.md\n"
            "sec.5.4 land in scripts/queue_runner.py and the sec.5.1 signature lands\n"
            "in scripts/queue_entry_check.py, and the cfd-supervisor reads BOTH as\n"
            "DIFFS personally -- SUPERVISION_CHARTER.md sec.3 check 1, which may\n"
            "never be delegated and which this driver does not discharge.\n"
            "prereg blob %s verified at %s; spec blob %s verified at %s.\n"
            % (prereg_blob[:12], freeze_commit[:12], spec_blob[:12], SPEC_COMMIT[:12]))
        return 2
    refuse("the repaired pair is present but the H1-H14 battery is NOT SHIPPED by this "
           "driver. It was deliberately not written blind: a gate that has never been "
           "executed is discovered by the first correct repair it rejects "
           "(verification, 2026-08-28). The battery is written and DRIVEN against the "
           "landed repair, under this same registration, before any H row is reported.")


def main(argv=None):
    if not __debug__:
        sys.stderr.write(
            "REFUSED: running under `python3 -O`, which deletes every assert statement. "
            "This program carries none by design, but a harness that RUNS under -O "
            "invites one to be added later and silently removed (L-332).\n")
        return 2
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--prereg-commit", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--preconditions", action="store_true",
                    help="report the enqueue-precondition state and exit")
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args(argv)

    if a.probe:
        print("probe: __debug__=%s" % __debug__)
        return 0
    if a.selftest:
        return selftest()
    try:
        if a.preconditions:
            print(json.dumps(preconditions(VALIDATOR, RUNNER), indent=2, default=str))
            return 0 if preconditions(VALIDATOR, RUNNER)["all_met"] else 2
        if not a.prereg_commit:
            refuse("--prereg-commit is required. This driver does not grade without the "
                   "sha of the pre-registration's adding commit, and it VERIFIES that "
                   "sha by hashing %s on disk against its committed blob (rule 2)."
                   % PREREG)
        if a.prereg_commit != FREEZE_COMMIT:
            refuse("--prereg-commit %s is not this item's freeze commit %s"
                   % (a.prereg_commit, FREEZE_COMMIT))
        return grade(a.prereg_commit)
    except Refusal as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
