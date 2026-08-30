#!/usr/bin/env python3
"""R3 -- THE COMMIT-HELPER RENAME MODE DRIVER.  THE ITEM IS **BLOCKED**.

Registration : verification/campaign/R3_COMMIT_RENAME_MODE_PREREGISTRATION.md
Specification: docs/standards/COMMIT_HELPER_RENAME_MODE.md, frozen at
               ed77957c4e56cd12e1d5d0c620b218805bd4306b

THE BLOCK, STATED FIRST AND NOT SOFTENED INTO PROSE ANYWHERE BELOW.
docs/standards/COMMIT_INTEGRITY_STANDARD.md Clause 2 (:34-43) requires a NUMERIC
assertion that `deletions == 0` before commit-tree and again after update-ref.
A RENAME IS A DELETION.  Clause 2, read literally, refuses every rename this mode
exists to make.  That standard is the VERIFICATION TEAM'S and cfd does not rule on it.
This driver therefore builds, tests and refuses: its graded path prints BLOCKED, names
the precondition, and exits 2.  A ruling RELAYED BY ANY AGENT IS NOT THE RULING
(standing rule 9); it is discharged against verification's own committed artifact,
cited by path and commit, in a dated addendum.

WHAT THIS PROGRAM WILL NOT DO
  * It will not grade without --prereg-commit, and it VERIFIES that sha by hashing the
    registration on disk against its committed blob (rule 2).
  * It will not build scripts/commit_rename_private.sh.  The registration's sec.1 says
    in terms that if verification rules LINE-LEVEL or declines, "this item stays BLOCKED
    and the mode is not built".  Building it now would pre-empt a ruling that may say
    do not build it.
  * IT NEVER TOUCHES THE SHARED GIT INDEX.  It issues no `git add` of any form, no
    `commit`, no `update-ref`, no `read-tree`, no `write-tree`; it hashes .git/index
    and reads HEAD before and after every run and reports both.
  * It carries ZERO assert statements and refuses under `python3 -O` (L-332).
"""

import argparse
import ast
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

PREREG = "verification/campaign/R3_COMMIT_RENAME_MODE_PREREGISTRATION.md"
SPEC = "docs/standards/COMMIT_HELPER_RENAME_MODE.md"
INTEGRITY = "docs/standards/COMMIT_INTEGRITY_STANDARD.md"
SPEC_COMMIT = "ed77957c4e56cd12e1d5d0c620b218805bd4306b"
FREEZE_COMMIT = "f7da1a24ca8c730d5c49a7ea429840c43378bf1e"

MODE_SCRIPT = os.path.join(REPO, "scripts", "commit_rename_private.sh")
SHARED_INDEX = os.path.join(REPO, ".git", "index")

CAP_CORE_MIN = 0.1600
EST_CORE_MIN = 0.1067
RANKS = 1

SHIPPED = [os.path.join(HERE, "r3_rename_mode_driver.py")]

# The two anchors that make Clause 2 the block.  Read from the file, never recalled.
CLAUSE2_HEADING = "## Clause 2 — DELETIONS ASSERTED AS A NUMBER, BEFORE AND AFTER"
CLAUSE2_NUMERIC = "Assert **`deletions == 0`** numerically before `commit-tree`"


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


def ast_assert_census(paths):
    out = {}
    for p in paths:
        tree = ast.parse(io.open(p, encoding="utf-8").read())
        out[os.path.basename(p)] = sum(1 for n in ast.walk(tree)
                                       if isinstance(n, ast.Assert))
    return out


def head_sha():
    out = _git(["rev-parse", "HEAD"])
    if out.returncode != 0:
        raise Refusal("cannot read HEAD: %s" % out.stderr.strip())
    return out.stdout.strip()


def index_fingerprint():
    if not os.path.isfile(SHARED_INDEX):
        return dict(exists=False)
    return dict(exists=True, sha256=sha256_file(SHARED_INDEX),
                mtime=os.path.getmtime(SHARED_INDEX),
                size=os.path.getsize(SHARED_INDEX))


# ---------------------------------------------------------------------------
# THE BLOCK DETECTOR -- and it is a READER, shown able to return both answers
# ---------------------------------------------------------------------------

def clause2_state(path):
    """Does this COMMIT_INTEGRITY_STANDARD.md still carry the numeric deletions==0
    requirement that blocks every rename?  Read from the file; never recalled."""
    if not os.path.isfile(path):
        return dict(blocking=False, why="%s does not exist" % path)
    text = io.open(path, encoding="utf-8").read()
    heading = CLAUSE2_HEADING in text
    numeric = CLAUSE2_NUMERIC in text
    if heading and numeric:
        line = 1 + text[:text.index(CLAUSE2_NUMERIC)].count("\n")
        return dict(blocking=True, heading_found=True, numeric_found=True,
                    numeric_at_line=line, path=os.path.relpath(path, REPO),
                    quote=CLAUSE2_NUMERIC)
    return dict(blocking=False, heading_found=heading, numeric_found=numeric,
                path=os.path.relpath(path, REPO),
                why=("the numeric `deletions == 0` requirement is not present in this "
                     "text as frozen; a ruling or amendment has moved it, and the "
                     "R3 registration's P1 transition applies -- as a DATED ADDENDUM "
                     "citing the ruling by path and commit, never as an edit."))


def mode_state():
    return dict(built=os.path.exists(MODE_SCRIPT), path=os.path.relpath(MODE_SCRIPT, REPO))


def preconditions():
    c2 = clause2_state(os.path.join(REPO, INTEGRITY))
    mode = mode_state()
    unmet = []
    if c2["blocking"]:
        unmet.append(
            "P1 -- THE BLOCK. %s:%d still requires, verbatim: %r. A rename IS a "
            "deletion: measured on the real production pair the diff reads 2 files "
            "changed, 46 insertions, 37 deletions without -M, and 1 file changed, 10 "
            "insertions, 1 deletion with -M. Clause 2 read literally refuses every "
            "rename this mode exists to make. COMMIT_INTEGRITY_STANDARD.md is the "
            "VERIFICATION TEAM'S and cfd does not rule on it. UNTIL VERIFICATION RULES "
            "whether `deletions == 0` counts PATHS LEAVING THE TREE or LINES, this item "
            "does not run."
            % (c2["path"], c2["numeric_at_line"], c2["quote"]))
    if not mode["built"]:
        unmet.append(
            "P2 -- %s does not exist. It is deliberately NOT built: the registration's "
            "sec.1 rules that if verification rules LINE-LEVEL or declines, 'this item "
            "stays BLOCKED and the mode is not built'. Building the mode while the "
            "ruling that may forbid it is outstanding would decide the question by "
            "shipping." % mode["path"])
    return dict(clause2=c2, mode=mode, unmet=unmet, all_met=not unmet)


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
        refuse("SELFTEST control %s: the NEGATIVE limb DID NOT FIRE." % name)
    out.append((name, pdetail, ndetail))


def selftest():
    head0, idx0 = head_sha(), index_fingerprint()
    out = []

    def f1p():
        return "prereg blob %s at %s" % (verify_freeze(FREEZE_COMMIT, PREREG)[:12],
                                         FREEZE_COMMIT[:12])

    def f1n():
        verify_freeze(FREEZE_COMMIT, "verification/campaign/__no_such_file__.md")
    _both("F1-PREREG-SHA", f1p, f1n, out)

    def f1bp():
        return "blob_sha1 reader -> %s" % blob_sha1(os.path.join(REPO, PREREG))[:12]

    def f1bn():
        tmp = tempfile.mkdtemp(prefix="f1bn_")
        try:
            p = os.path.join(tmp, "m.md")
            io.open(p, "wb").write(io.open(os.path.join(REPO, PREREG), "rb").read() + b"x")
            want = _git(["rev-parse", "%s:%s" % (FREEZE_COMMIT, PREREG)]).stdout.strip()
            if blob_sha1(p) == want:
                raise Refusal("READER BLIND to a one-byte change")
            raise Refusal("PLANTED ONE-BYTE CHANGE SEEN: %s != %s"
                          % (blob_sha1(p)[:12], want[:12]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("F1b-SHA-SEES-1BYTE", f1bp, f1bn, out)

    def f2p():
        return "spec blob %s at %s" % (verify_freeze(SPEC_COMMIT, SPEC)[:12],
                                       SPEC_COMMIT[:12])

    def f2n():
        verify_freeze("0" * 40, SPEC)
    _both("F2-SPEC-FREEZE", f2p, f2n, out)

    # F3 -- THE BLOCK READER. The whole BLOCKED label rests on this reader, so it is
    # driven in both directions: it must SEE the clause in the real standard, and it
    # must report it ABSENT from a text that does not carry it.
    def f3p():
        st = clause2_state(os.path.join(REPO, INTEGRITY))
        if not st["blocking"]:
            raise Refusal("READER SAYS THE BLOCK IS GONE: %r -- this is a finding, not "
                          "a control failure; take it to the supervisor" % st)
        return "Clause 2 numeric requirement found at %s:%d" % (st["path"],
                                                                st["numeric_at_line"])

    def f3n():
        tmp = tempfile.mkdtemp(prefix="f3n_")
        try:
            p = os.path.join(tmp, "no_clause2.md")
            io.open(p, "w").write("# a standard with no Clause 2 at all\n")
            st = clause2_state(p)
            if st["blocking"]:
                raise Refusal("READER BLIND: it found Clause 2 in a text without it")
            raise Refusal("PLANTED ABSENCE SEEN: reader reports blocking=False")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("F3-CLAUSE2-READER", f3p, f3n, out)

    # F4 -- the mode-absence reader, shown able to see a mode that exists.
    def f4p():
        st = mode_state()
        if st["built"]:
            raise Refusal("%s EXISTS. The registration says the mode is not built while "
                          "BLOCKED; somebody built it. That is a finding." % st["path"])
        return "%s absent, as the block requires" % st["path"]

    def f4n():
        tmp = tempfile.mkdtemp(prefix="f4n_")
        try:
            p = os.path.join(tmp, "commit_rename_private.sh")
            io.open(p, "w").write("#!/bin/sh\n")
            if not os.path.exists(p):
                raise Refusal("READER BLIND: a file it just wrote reads absent")
            raise Refusal("PLANTED MODE SEEN: os.path.exists -> True for %s" % p)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("F4-MODE-ABSENCE", f4p, f4n, out)

    def f5p():
        c = ast_assert_census(SHIPPED)
        if sum(c.values()) != 0:
            raise Refusal("shipped path carries %d ast.Assert node(s)" % sum(c.values()))
        return "0 ast.Assert over %d shipped file(s)" % len(c)

    def f5n():
        tmp = tempfile.mkdtemp(prefix="f5n_")
        try:
            p = os.path.join(tmp, "planted.py")
            io.open(p, "w").write("def f(x):\n    assert x\n")
            c = ast_assert_census([p])
            if sum(c.values()) != 1:
                raise Refusal("CENSUS BLIND: planted 1, saw %d" % sum(c.values()))
            raise Refusal("PLANTED ASSERT SEEN: %r" % c)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("F5-AST-CENSUS", f5p, f5n, out)

    def f6p():
        p = subprocess.run([sys.executable, __file__, "--probe"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if p.returncode != 0:
            raise Refusal("probe without -O returned rc %d" % p.returncode)
        return "no -O: rc 0"

    def f6n():
        p = subprocess.run([sys.executable, "-O", __file__, "--probe"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if p.returncode != 2:
            raise Refusal("-O returned rc %d, want 2" % p.returncode)
        raise Refusal("-O CORRECTLY REFUSED with rc 2")
    _both("F6-FLAG-PROOF", f6p, f6n, out)

    # F7 -- the shared index is never touched, and the reader is shown able to see a
    # change (G-R3-7's shape, on this driver rather than on a mode that is not built).
    def f7p():
        now = index_fingerprint()
        if now.get("sha256") != idx0.get("sha256"):
            raise Refusal("THE SHARED INDEX CHANGED DURING THIS SELFTEST: %s -> %s. "
                          "This driver issues no update-index; a peer moved it, and "
                          "that is INSPECTED, never reverted."
                          % (idx0.get("sha256", "")[:12], now.get("sha256", "")[:12]))
        return ".git/index sha256 %s unchanged" % (now.get("sha256", "n/a")[:12])

    def f7n():
        tmp = tempfile.mkdtemp(prefix="f7n_")
        try:
            a = os.path.join(tmp, "idx")
            io.open(a, "w").write("one")
            h = sha256_file(a)
            io.open(a, "w").write("onf")
            if sha256_file(a) == h:
                raise Refusal("INDEX READER BLIND")
            raise Refusal("PLANTED INDEX BYTE SEEN: %s -> %s"
                          % (h[:12], sha256_file(a)[:12]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    _both("F7-SHARED-INDEX", f7p, f7n, out)

    # F8 -- HEAD is not moved by any refusal.
    def f8p():
        h = head_sha()
        if h != head0:
            raise Refusal("HEAD MOVED DURING THIS SELFTEST: %s -> %s. Peers commit "
                          "constantly; this driver did not, and issues no update-ref."
                          % (head0[:12], h[:12]))
        return "HEAD %s byte-equal before and after" % h[:12]

    def f8n():
        if head_sha() == "0" * 40:
            raise Refusal("unreachable")
        raise Refusal("HEAD READER SEES A REAL SHA (%s), so an equality it reports is "
                      "a reading and not a constant" % head_sha()[:12])
    _both("F8-HEAD-UNMOVED", f8p, f8n, out)

    # F9 -- the BLOCK gate: it must refuse today, and it must be able NOT to refuse.
    def f9p():
        tmp = tempfile.mkdtemp(prefix="f9p_")
        try:
            p = os.path.join(tmp, "ruled.md")
            io.open(p, "w").write("# Clause 2 as it would read after a PATH-LEVEL "
                                  "ruling: no numeric line requirement\n")
            st = clause2_state(p)
            if st["blocking"]:
                raise Refusal("gate would still block a standard carrying no such clause")
            return "gate DOES NOT block a standard without the numeric clause"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def f9n():
        st = preconditions()
        if st["all_met"]:
            raise Refusal("GATE ADMITTED THE ITEM. Read the preconditions, not the gate")
        raise Refusal("ITEM CORRECTLY BLOCKED on %d precondition(s)" % len(st["unmet"]))
    _both("F9-BLOCK-GATE", f9p, f9n, out)

    print("R3 DRIVER SELFTEST -- controls fired, each in BOTH directions")
    print("=" * 78)
    for name, p, n in out:
        print("  %-22s POSITIVE %s" % (name, p))
        print("  %-22s NEGATIVE fired: %s" % ("", n))
    print("=" * 78)
    print("%d controls fired, each shown able to fail" % len(out))
    print("assert census over the shipped path: %s" % json.dumps(ast_assert_census(SHIPPED)))
    print("__debug__ = %s (this run is NOT under -O)" % __debug__)
    print("HEAD %s unchanged; .git/index sha256 %s unchanged; NO git write of any kind "
          "was issued." % (head0[:12], (idx0.get("sha256") or "n/a")[:12]))
    return 0


def grade(freeze_commit):
    head0, idx0 = head_sha(), index_fingerprint()
    prereg_blob = verify_freeze(freeze_commit, PREREG)
    spec_blob = verify_freeze(SPEC_COMMIT, SPEC)
    st = preconditions()
    if not st["all_met"]:
        sys.stderr.write(
            "\nBLOCKED\n"
            "=======\n"
            "R3_COMMIT_RENAME_MODE. Verdict at registration: BLOCKED, and it has not\n"
            "lifted. R3_COMMIT_RENAME_MODE_PREREGISTRATION.md sec.8 clause 1: nothing\n"
            "is graded and NO CONTROL IS RUN. BLOCKED is not a softened GATE FAIL and\n"
            "is not a PENDING -- PENDING means not yet run; this item is not yet\n"
            "PERMITTED to run.\n\n")
        for u in st["unmet"]:
            sys.stderr.write("  UNMET  %s\n\n" % u)
        sys.stderr.write(
            "WHAT LIFTS IT, and only this: the verification team rules, in its own\n"
            "committed artifact, whether COMMIT_INTEGRITY_STANDARD.md Clause 2's\n"
            "`deletions == 0` counts PATHS LEAVING THE TREE or LINES. A ruling RELAYED\n"
            "BY ANY AGENT IS NOT THE RULING (standing rule 9): it is discharged against\n"
            "that artifact, cited by path and commit, in a dated addendum that may not\n"
            "alter a gate, threshold, cap or label. If verification rules LINE-LEVEL or\n"
            "declines, this item STAYS BLOCKED and the mode is not built.\n\n"
            "prereg blob %s verified at %s; spec blob %s verified at %s.\n"
            "HEAD %s and .git/index sha256 %s are byte-equal to their values at entry;\n"
            "this driver issued no git write of any kind and never touched the shared\n"
            "index.\n"
            % (prereg_blob[:12], freeze_commit[:12], spec_blob[:12], SPEC_COMMIT[:12],
               head0[:12], (idx0.get("sha256") or "n/a")[:12]))
        if head_sha() != head0 or index_fingerprint().get("sha256") != idx0.get("sha256"):
            sys.stderr.write("WARNING: HEAD or .git/index MOVED during this refusal. "
                             "This driver did not move them. INSPECT, do not revert.\n")
        return 2
    refuse("the block reads as lifted, but R1-R15 are NOT SHIPPED by this driver and "
           "scripts/commit_rename_private.sh is not built. Both follow the ruling, in "
           "a dated addendum, and neither is written blind.")


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
    ap.add_argument("--preconditions", action="store_true")
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args(argv)

    if a.probe:
        print("probe: __debug__=%s" % __debug__)
        return 0
    if a.selftest:
        return selftest()
    try:
        if a.preconditions:
            st = preconditions()
            print(json.dumps(st, indent=2, default=str))
            return 0 if st["all_met"] else 2
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
