#!/usr/bin/env python3
"""Replay scripts/check_commit_size.py over a FROZEN window of real commits.

WHY THIS FILE EXISTS -- WHICH IS THE POINT OF IT
------------------------------------------------
The false-positive measurement is what every amendment to the commit-size guard
is argued from. AMENDMENT 2 of docs/standards/COMMIT_SIZE_GUARD.md classified
the LOGS clause at 0 TRUE / 14 FALSE on 200 real commits, and AMENDMENT 3 --
Sanaa's ruling, approved at 8ed55f26 -- rests entirely on that number.

THE HARNESS THAT PRODUCED IT WAS NEVER FILED. It lived in the scratchpad, and
the scratchpad is temp-only and is wiped (CLAUDE.md rule 13, L-186: a draft
another agent must read lives under the case directory it belongs to, and a
repository document never cites a scratch path). Nothing under scripts/ so much
as referenced check_commit_size. So the next amendment had to RECONSTRUCT the
instrument from one line of prose -- COMMIT_SIZE_GUARD.md:137, "one process
over one frozen commit list" -- and then prove the reconstruction by
reproducing the recorded row exactly before it was allowed to report a new one.

That reconstruction was done on 2026-08-27 for AMENDMENT 3. THIS FILE IS THAT
RECONSTRUCTION, FILED, so that nobody does the work a third time and so that a
boarded rate can be re-derived by running one command.

A measurement whose instrument is not on disk is not reproducible, whatever the
number says.

WHAT IT MEASURES, AND WHAT IT REFUSES TO DO
-------------------------------------------
It replays each commit in the window against its FIRST PARENT through the
guard's own git adapter and its own evaluate(), in ONE process over ONE frozen
list, and reports the refusal rate and the per-clause split. It never writes to
git, never touches an index, and never edits the guard: it LOADS the guard, by
preference from a COMMITTED BLOB, so a boarded number is provably produced by
shipped code and not by a dirty worktree.

The LOGS split is counted from raw fnmatch on basenames, deliberately NOT
through the guard's is_log_path(), so that "0 LOGS firings" can be read against
"how many log paths were actually there" instead of being a tautology.

EXIT CODES
    0   the sweep ran (or the selftest passed)
    2   the selftest failed, or the frozen window no longer resolves
    1   usage error

USAGE
    python3 scripts/sweep_commit_size_guard.py                    # frozen window, guard at HEAD
    python3 scripts/sweep_commit_size_guard.py --guard-blob abe1a634
    python3 scripts/sweep_commit_size_guard.py --window <sha> --depth 200
    python3 scripts/sweep_commit_size_guard.py --selftest
"""
import sys

# `python3 -O` refusal AT ENTRY, for the same reason the guard carries one: this
# file produces a MEASURED NUMBER, and under -O every assert in the toolchain
# vanishes (L-332). This module is executed, never imported.
if not __debug__:
    sys.stderr.write(
        "REFUSED: sweep_commit_size_guard.py must not run under `python3 -O` or "
        "PYTHONOPTIMIZE. Re-run under plain `python3`.\n")
    sys.exit(2)

import ast
import json
import fnmatch
import argparse
import importlib.util
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

GUARD_PATH = "scripts/check_commit_size.py"

# ---------------------------------------------------------------------------
# THE FROZEN WINDOW, NAMED IN THE FILE so the recorded row is reproducible by
# running one command with no arguments.
#
# It is the 200 commits ending at db2c7f9a -- the last commit named in
# AMENDMENT 2 (1)'s LOGS classification table -- which falls at depth exactly
# 200 from 94ceebe7. The window was CHOSEN by that property and then PROVEN:
# replaying the pre-AMENDMENT-3 guard blob over it reproduces the "after
# AMENDMENT 1" row of COMMIT_SIZE_GUARD.md:139-142 exactly, 200 / 185 / 15 /
# 7.5 %, LOGS 14 COUNT 5 BYTES 3 EMPTY 1 ATTEMPT 0. That reproduction is the
# only evidence the window is the right one, and it is why resolve_window()
# REFUSES rather than drifting if the endpoints stop matching.
# ---------------------------------------------------------------------------
WINDOW_NEWEST = "94ceebe7"
WINDOW_OLDEST = "db2c7f9a"
WINDOW_DEPTH = 200

# Recorded rows, so a re-run can be compared against what was boarded.
RECORDED = {
    "v1.2 (before AMENDMENT 3)": (200, 185, 15, {"LOGS": 14, "COUNT": 5, "BYTES": 3,
                                                 "EMPTY": 1, "ATTEMPT": 0}),
    "v1.3 (after AMENDMENT 3)": (200, 194, 6, {"LOGS": 0, "COUNT": 5, "BYTES": 3,
                                               "EMPTY": 1, "ATTEMPT": 0}),
}

# The one commit whose full answer has been measured by hand and can therefore
# serve as a planted control: 05241ab2, the archetype that sized the thresholds.
# 172 paths added/modified, 276,949,823 added bytes, 28 log paths ALL under
# verification/runs/. It refuses BYTES + COUNT under every guard version; under
# v1.2 it ALSO refused LOGS, and AMENDMENT 3's whole basis is that that firing
# was the false one.
PLANT_SHA = "05241ab2"
PLANT_EXPECT = {"BYTES", "COUNT"}

CLAUSES = ("LOGS", "COUNT", "BYTES", "EMPTY", "ATTEMPT")


class SweepRefusal(Exception):
    """A condition that must stop the instrument under ANY interpreter flag."""


def _git(args, cwd):
    return subprocess.run(["git", "-C", str(cwd)] + args, capture_output=True, text=True)


def repo_root():
    out = _git(["rev-parse", "--show-toplevel"], Path(__file__).resolve().parent)
    if out.returncode != 0:
        raise SweepRefusal("REPO-ROOT: not inside a git repository")
    return Path(out.stdout.strip())


def load_guard(root, rev):
    """Load the guard MODULE, by preference out of a committed object.

    A boarded number must be produced by code that is IN THE REPOSITORY, not by
    whatever happened to be in the worktree when somebody ran a sweep. `rev` may
    name a blob directly or any commit-ish, in which case <rev>:GUARD_PATH is
    taken. Returns (module, description-of-what-was-loaded)."""
    kind = _git(["cat-file", "-t", rev], root)
    if kind.returncode == 0 and kind.stdout.strip() == "blob":
        spec_arg, blob = ["cat-file", "-p", rev], rev
    else:
        blob_out = _git(["rev-parse", "%s:%s" % (rev, GUARD_PATH)], root)
        if blob_out.returncode != 0:
            raise SweepRefusal("GUARD-BLOB: cannot resolve %s:%s -- %s"
                               % (rev, GUARD_PATH, blob_out.stderr.strip()))
        blob = blob_out.stdout.strip()
        spec_arg = ["cat-file", "-p", blob]
    src = _git(spec_arg, root)
    if src.returncode != 0 or not src.stdout:
        raise SweepRefusal("GUARD-BLOB: %s read back empty" % blob)
    tmp = Path(tempfile.mkdtemp(prefix="sweep_guard_")) / "guard_under_test.py"
    tmp.write_text(src.stdout)
    spec = importlib.util.spec_from_file_location("guard_under_test", tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, "%s (blob %s, %d bytes)" % (rev, blob[:12], len(src.stdout))


def resolve_window(root, newest, depth, expect_oldest):
    out = _git(["log", "--format=%H", "-n", str(depth), newest], root)
    if out.returncode != 0:
        raise SweepRefusal("WINDOW: cannot resolve %s -- %s" % (newest, out.stderr.strip()))
    shas = [l.strip() for l in out.stdout.splitlines() if l.strip()]
    if len(shas) != depth:
        raise SweepRefusal("WINDOW: %s yielded %d commits, expected %d. The frozen "
                           "window no longer resolves; a sweep over a DIFFERENT "
                           "sample must not be reported as this one."
                           % (newest, len(shas), depth))
    if expect_oldest and not shas[-1].startswith(expect_oldest):
        raise SweepRefusal(
            "WINDOW: depth %d from %s ends at %s, not the recorded %s. History has "
            "moved under the frozen window. REFUSING rather than silently sweeping "
            "a different 200 -- that substitution is exactly what makes a boarded "
            "rate unreproducible." % (depth, newest, shas[-1][:8], expect_oldest))
    return shas


def raw_log_paths(guard, live):
    """Log-pattern matches counted WITHOUT the guard's is_log_path(), so that a
    zero LOGS count can be read against how many log paths were actually there.
    A zero from a reader not shown able to see a non-zero is not evidence."""
    return [c.path for c in live
            if any(fnmatch.fnmatchcase(c.path.rsplit("/", 1)[-1], pat)
                   for pat in guard.LOG_BASENAME_PATTERNS)]


def sweep(guard, root, shas):
    rows = []
    for sha in shas:
        meta = guard.commit_meta_from_sha(sha, root)
        changes = guard.changes_from_trees(sha + "^", sha, root)
        texts = guard.manifest_texts_from_tree(changes, sha, root)
        findings, _ = guard.evaluate(changes, texts, guard.CLEAN, meta)
        live = [c for c in changes if c.status in ("A", "M")]
        logs = raw_log_paths(guard, live)
        rows.append({
            "sha": sha[:8],
            "clauses": sorted({f.split(":", 1)[0] for f in findings}),
            "n_live": len(live),
            "added_bytes": sum(guard.added_bytes_of(c) for c in live),
            "log_paths": len(logs),
            "log_paths_in_runtree": sum(1 for p in logs
                                        if p.startswith(guard.RUN_TREE_PREFIX)),
        })
    return rows


def summarise(rows):
    refused = sum(1 for r in rows if r["clauses"])
    split = Counter(c for r in rows for c in r["clauses"])
    return {
        "commits": len(rows),
        "accepted": len(rows) - refused,
        "refused": refused,
        "rate_pct": round(100.0 * refused / len(rows), 1) if rows else 0.0,
        "clauses": {c: split.get(c, 0) for c in CLAUSES},
        "log_paths_total": sum(r["log_paths"] for r in rows),
        "log_paths_in_runtree": sum(r["log_paths_in_runtree"] for r in rows),
    }


def clause_mismatch(expected, got):
    """The comparison used by the planted control -- FACTORED OUT ON PURPOSE, so
    the selftest can feed it a wrong expectation and prove it says so. A checker
    never shown returning a mismatch is not known to be checking."""
    missing = sorted(set(expected) - set(got))
    if missing:
        return "expected %s, missing %s (got %s)" % (sorted(expected), missing, sorted(got))
    return None


def print_summary(s, what, label):
    print("guard under test: %s" % what)
    print("window: %s" % label)
    print("commits %d  accepted %d  refused %d  rate %.1f %%"
          % (s["commits"], s["accepted"], s["refused"], s["rate_pct"]))
    print("clauses: " + "  ".join("%s %d" % (c, s["clauses"][c]) for c in CLAUSES))
    print("log-pattern paths added/modified across the window: %d, of which %d under "
          "%s and %d outside"
          % (s["log_paths_total"], s["log_paths_in_runtree"], "verification/runs/",
             s["log_paths_total"] - s["log_paths_in_runtree"]))
    for name, (n, acc, ref, split) in RECORDED.items():
        if (s["commits"], s["accepted"], s["refused"]) == (n, acc, ref) and s["clauses"] == split:
            print("MATCHES THE RECORDED ROW FOR %s (COMMIT_SIZE_GUARD.md)" % name)


def count_assert_nodes(source):
    return sum(1 for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert))


def selftest():
    root = repo_root()
    problems, lines = [], []
    src = Path(__file__).read_text()

    # S1 -- this harness carries no assert, and the counter is shown able to
    # see one. Same discipline as the guard: under -O an assert is deleted.
    n = count_assert_nodes(src)
    if n:
        problems.append("S1 FAILED: %d assert(s) in this harness; -O deletes them (L-332)." % n)
    else:
        lines.append("S1: zero `assert` nodes in this harness (L-332).")
    if count_assert_nodes("def f(x):\n    assert x\n    return x\n") != 1:
        problems.append("S1 CONTROL FAILED: the ast counter could not see a planted "
                        "assert, so its zero above means nothing.")
    else:
        lines.append("S1 CONTROL FIRED: the counter saw 1 planted assert in a synthetic "
                     "source, so the zero above is a reading.")

    # S2 -- the frozen window still resolves to the recorded endpoints.
    try:
        shas = resolve_window(root, WINDOW_NEWEST, WINDOW_DEPTH, WINDOW_OLDEST)
        lines.append("S2: the frozen window resolves -- %d commits, %s -> %s, endpoints "
                     "as recorded." % (len(shas), shas[0][:8], shas[-1][:8]))
    except SweepRefusal as exc:
        problems.append("S2 FAILED: %s" % exc)
        shas = []

    # S3 -- window drift is REFUSED, not absorbed. Shown live by asking for a
    # depth whose endpoint cannot be the recorded one.
    try:
        resolve_window(root, WINDOW_NEWEST, WINDOW_DEPTH - 1, WINDOW_OLDEST)
        problems.append("S3 FAILED: a window ending one commit short was ACCEPTED. "
                        "Drift must refuse, or a boarded rate is unreproducible.")
    except SweepRefusal:
        lines.append("S3 CONTROL FIRED: a window whose endpoint is not the recorded one "
                     "REFUSES, so this harness cannot silently sweep a different 200.")

    # S4 -- PLANTED CONTROL on a commit whose answer is measured, driven from a
    # COMMITTED blob so what is checked is what shipped.
    guard, what = load_guard(root, "HEAD")
    rows = sweep(guard, root, [_git(["rev-parse", PLANT_SHA], root).stdout.strip()])
    got = rows[0]["clauses"]
    bad = clause_mismatch(PLANT_EXPECT, got)
    if bad:
        problems.append("S4 PLANTED CONTROL FAILED (%s): %s. This commit is the "
                        "measurement that sized the guard's thresholds; if the harness "
                        "cannot reproduce its clause set, no rate it reports is "
                        "believable." % (PLANT_SHA, bad))
    else:
        era = ("v1.2, pre-AMENDMENT 3" if "LOGS" in got else "v1.3+, AMENDMENT 3 in force")
        lines.append("S4 PLANTED CONTROL FIRED (%s, %d paths, %d added bytes, %d log "
                     "paths of which %d under verification/runs/): refused %s -- "
                     "BYTES+COUNT as measured. LOGS %s, i.e. the guard under test is %s."
                     % (PLANT_SHA, rows[0]["n_live"], rows[0]["added_bytes"],
                        rows[0]["log_paths"], rows[0]["log_paths_in_runtree"],
                        got, "present" if "LOGS" in got else "absent", era))

    # S5 -- and the checker used by S4 is SHOWN ABLE TO REPORT A WRONG ANSWER AS
    # WRONG. Without this, S4 passing would prove nothing about S4.
    if clause_mismatch({"EMPTY"}, got) is None:
        problems.append("S5 FAILED: clause_mismatch() accepted a deliberately WRONG "
                        "expectation. The comparison S4 relies on is blind, so S4's "
                        "pass is not a reading.")
    else:
        lines.append("S5 CONTROL FIRED: fed the WRONG expectation {'EMPTY'} for %s, the "
                     "same comparison S4 uses reported a mismatch -- so S4 is a check "
                     "and not a rubber stamp." % PLANT_SHA)

    lines.append("guard loaded for the planted control: %s" % what)
    for l in lines:
        print("  " + l)
    if problems:
        print("")
        for p in problems:
            print("  " + p)
        print("\nSWEEP-HARNESS SELFTEST FAILED: %d control(s) did not behave." % len(problems))
        return 2
    print("\nSWEEP-HARNESS SELFTEST PASS: %d controls fired, each shown able to fail."
          % len(lines))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=(
        "Replay the commit-size guard over a frozen window of real commits and "
        "report its refusal rate and clause split. Never writes to git."))
    ap.add_argument("--guard-blob", default="HEAD", metavar="REV",
                    help="blob sha, or any commit-ish whose %s is taken (default HEAD). "
                         "Drive BOTH sides of a before/after from committed objects."
                         % GUARD_PATH)
    ap.add_argument("--window", default=WINDOW_NEWEST, metavar="SHA",
                    help="newest commit of the window (default the frozen %s)" % WINDOW_NEWEST)
    ap.add_argument("--depth", type=int, default=WINDOW_DEPTH,
                    help="commits in the window (default %d)" % WINDOW_DEPTH)
    ap.add_argument("--json", action="store_true", help="machine-readable rows + summary")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    root = repo_root()
    frozen = (a.window == WINDOW_NEWEST and a.depth == WINDOW_DEPTH)
    shas = resolve_window(root, a.window, a.depth, WINDOW_OLDEST if frozen else None)
    guard, what = load_guard(root, a.guard_blob)
    rows = sweep(guard, root, shas)
    s = summarise(rows)
    label = ("FROZEN %s -> %s, depth %d" % (WINDOW_NEWEST, WINDOW_OLDEST, WINDOW_DEPTH)
             if frozen else
             "AD HOC %s, depth %d -- NOT the frozen window, not comparable to the "
             "recorded rows" % (a.window[:8], a.depth))
    if a.json:
        print(json.dumps({"guard": what, "window": label,
                          "summary": s, "rows": rows}, indent=1))
        return 0
    print_summary(s, what, label)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except SweepRefusal as exc:
        print("REFUSED: %s" % exc)
        sys.exit(2)
