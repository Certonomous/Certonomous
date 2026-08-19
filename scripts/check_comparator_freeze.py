#!/usr/bin/env python3
"""
Enforce VERIFICATION_CHARTER.md 2d: the comparator is frozen before its cases
can answer it.

The rule is enforceable because both sides of the comparison are on disk and
neither is written by the party being audited:

  * when the comparator was last committed   -- git
  * when the run tree's first case finished  -- the completion markers

A comparator whose last commit PRECEDES the earliest completion marker was
frozen by construction.  One committed after is not, and the charter requires a
dated disclosure naming what was added, when, what was readable at that moment,
and which findings rest on it.

WHAT THIS CHECK CANNOT SEE, stated because a check that overstates its reach is
worse than none:
  * whether a post-marker edit touched the grading path or was purely additive.
    2d permits the second WITH a disclosure and forbids the first outright.
    This check finds the timestamp; a human reads the diff.
  * whether a disclosure exists.  It reports the fact and leaves the reading.
  * anything about a tree with no completion markers.
  * a comparator that was never committed at all -- reported separately as
    UNCOMMITTED, which is a different and worse condition than late.

Exit: 0 clean, 3 at least one LATE or UNCOMMITTED or MODIFIED, 2 refusal.
"""
import argparse
import datetime as dt
import hashlib
import os
import re
import subprocess
import sys

EXIT_OK, EXIT_REFUSE, EXIT_VIOLATION = 0, 2, 3
MARKER_UTC = re.compile(r"^finished_utc=(.+)$", re.M)


def refuse(msg):
    print(msg)
    sys.exit(EXIT_REFUSE)


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo] + list(args),
                       capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def parse_utc(s):
    s = s.strip().replace("Z", "+00:00")
    try:
        d = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def earliest_marker(tree):
    """(time, name).  Prefers the marker's OWN finished_utc over its mtime,
    because mtime is a property of the filesystem and finished_utc is a
    property of the run."""
    best = None
    for f in sorted(os.listdir(tree)):
        if not f.startswith("DONE."):
            continue
        p = os.path.join(tree, f)
        t = None
        try:
            m = MARKER_UTC.search(open(p, errors="replace").read())
            if m:
                t = parse_utc(m.group(1))
        except OSError:
            pass
        if t is None:
            t = dt.datetime.fromtimestamp(os.path.getmtime(p), dt.timezone.utc)
        if best is None or t < best[0]:
            best = (t, f)
    return best


def check_tree(repo, tree):
    rel = os.path.relpath(tree, repo)
    comparators = sorted(f for f in os.listdir(tree)
                         if f.startswith("analyse_") and f.endswith(".py"))
    mk = earliest_marker(tree)
    if not comparators or mk is None:
        return None
    out = []
    for c in comparators:
        relc = os.path.join(rel, c)
        rc, iso, _ = git(repo, "log", "-1", "--format=%cI", "--", relc)
        # FIRST commit as well as last, because "did not exist in any commit
        # when the first case finished" and "existed, then was amended" are
        # different conditions and only the first is 2d's core violation.
        # --follow so a rename does not read as a birth.
        _, hist, _ = git(repo, "log", "--follow", "--format=%cI", "--", relc)
        first_iso = hist.splitlines()[-1] if hist.strip() else ""
        rc2, blob, _ = git(repo, "rev-parse", f"HEAD:{relc}")
        row = dict(tree=rel, comparator=c, first_marker=mk[1],
                   first_marker_utc=mk[0].isoformat())
        if rc != 0 or not iso:
            row.update(status="UNCOMMITTED", committed_utc=None,
                       note="the comparator is in no commit")
            out.append(row)
            continue
        ct = parse_utc(iso)
        row["committed_utc"] = ct.isoformat()
        row["margin_seconds"] = (mk[0] - ct).total_seconds()
        # is the file that ran the file that was frozen?
        modified = None
        if rc2 == 0:
            # INDEX-INDEPENDENT ON PURPOSE.  `git status` and `git diff HEAD`
            # both consult the index, and this repository's shared index has
            # been observed stale enough to report tracked files as deleted
            # while they sit on disk.  Comparing the worktree bytes against the
            # HEAD BLOB asks git only for content, which no index can distort.
            disk = hashlib.sha256(open(os.path.join(tree, c), "rb").read()).hexdigest()
            r = subprocess.run(["git", "-C", repo, "cat-file", "blob", blob],
                               capture_output=True)
            if r.returncode == 0:
                modified = hashlib.sha256(r.stdout).hexdigest() != disk
                row["worktree_differs_from_HEAD"] = modified
        ft = parse_utc(first_iso) if first_iso else None
        row["first_committed_utc"] = ft.isoformat() if ft else None
        if ct < mk[0]:
            row["status"] = "MODIFIED_AFTER_COMMIT" if modified else "FROZEN"
        elif ft is not None and ft < mk[0]:
            # existed in a commit before the run finished its first case, and
            # was touched again afterwards.  W-4 corrections to a published
            # rung live here and 2d's boundary clause exempts them, so this is
            # reported as its own state rather than folded into a violation.
            row["status"] = "AMENDED_AFTER"
        else:
            row["status"] = "UNFROZEN"
        out.append(row)
    return out


def selftest():
    """Planted shapes that must fire, and shapes that must survive."""
    import tempfile, shutil
    ok = True
    tmp = tempfile.mkdtemp()
    try:
        repo = os.path.join(tmp, "r")
        os.makedirs(os.path.join(repo, "t"))
        subprocess.run(["git", "init", "-q", repo], check=True)
        subprocess.run(["git", "-C", repo, "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", repo, "config", "user.name", "t"], check=True)
        tree = os.path.join(repo, "t")

        def commit(msg, when):
            env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
            subprocess.run(["git", "-C", repo, "add", "-A"], check=True, env=env)
            subprocess.run(["git", "-C", repo, "commit", "-q", "-m", msg],
                           check=True, env=env)

        # FROZEN: comparator committed before the marker
        open(os.path.join(tree, "analyse_x.py"), "w").write("# v1\n")
        commit("c", "2026-01-01T00:00:00+00:00")
        open(os.path.join(tree, "DONE.a"), "w").write("finished_utc=2026-01-02T00:00:00Z\n")
        r = check_tree(repo, tree)
        if not r or r[0]["status"] != "FROZEN":
            print(f"  SELFTEST FAIL: expected FROZEN, got {r and r[0]['status']}"); ok = False
        else:
            print("  planted FROZEN      -> FROZEN      OK")

        # AMENDED_AFTER: existed before the marker, touched again afterwards.
        # This is W-4 territory and 2d's boundary clause exempts it, so it must
        # NOT be classified as a violation.
        open(os.path.join(tree, "analyse_x.py"), "w").write("# v2\n")
        commit("c2", "2026-01-03T00:00:00+00:00")
        r = check_tree(repo, tree)
        if not r or r[0]["status"] != "AMENDED_AFTER":
            print(f"  SELFTEST FAIL: expected AMENDED_AFTER, got {r and r[0]['status']}"); ok = False
        else:
            print("  planted AMENDED     -> AMENDED     OK")

        # UNFROZEN: the comparator is in NO commit until after the first case
        # finished.  This is 2d's core violation and must be separated from the
        # amendment case above, which is why both are planted.
        os.makedirs(os.path.join(repo, "t3"))
        t3 = os.path.join(repo, "t3")
        open(os.path.join(t3, "DONE.a"), "w").write("finished_utc=2026-02-01T00:00:00Z\n")
        commit("marker only", "2026-02-01T00:00:00+00:00")
        open(os.path.join(t3, "analyse_z.py"), "w").write("# born late\n")
        commit("comparator after the fact", "2026-02-02T00:00:00+00:00")
        r = check_tree(repo, t3)
        if not r or r[0]["status"] != "UNFROZEN":
            print(f"  SELFTEST FAIL: expected UNFROZEN, got {r and r[0]['status']}"); ok = False
        else:
            print("  planted UNFROZEN    -> UNFROZEN    OK")

        # MODIFIED: frozen commit but the worktree file has drifted
        open(os.path.join(tree, "DONE.a"), "w").write("finished_utc=2026-01-04T00:00:00Z\n")
        open(os.path.join(tree, "analyse_x.py"), "a").write("# drift\n")
        r = check_tree(repo, tree)
        if not r or r[0]["status"] != "MODIFIED_AFTER_COMMIT":
            print(f"  SELFTEST FAIL: expected MODIFIED_AFTER_COMMIT, got {r and r[0]['status']}"); ok = False
        else:
            print("  planted MODIFIED    -> MODIFIED    OK")

        # must SURVIVE: a tree with no markers is not this check's business
        os.makedirs(os.path.join(repo, "t2"))
        open(os.path.join(repo, "t2", "analyse_y.py"), "w").write("# y\n")
        commit("c3", "2026-01-05T00:00:00+00:00")
        if check_tree(repo, os.path.join(repo, "t2")) is not None:
            print("  SELFTEST FAIL: a marker-less tree should be skipped"); ok = False
        else:
            print("  negative: no markers-> skipped     OK")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        print("SELFTEST -- planted shapes that must fire, and one that must not")
        sys.exit(EXIT_OK if selftest() else EXIT_VIOLATION)

    repo = os.path.abspath(a.repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        refuse(f"REFUSE: {repo} is not a git repository")

    rows = []
    for dp, dn, fn in os.walk(os.path.join(repo, "verification")):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__")]
        r = check_tree(repo, dp)
        if r:
            rows.extend(r)

    print("COMPARATOR FREEZE -- VERIFICATION_CHARTER.md 2d")
    print("=" * 100)
    if not rows:
        print("  no run tree carries both a comparator and a completion marker.")
        print("ZERO VERDICT: NOT_A_MEASUREMENT -- nothing was in scope")
        sys.exit(EXIT_OK)
    bad = 0
    order = {"UNCOMMITTED": 0, "UNFROZEN": 1, "MODIFIED_AFTER_COMMIT": 2,
             "AMENDED_AFTER": 3, "FROZEN": 4}
    for r in sorted(rows, key=lambda x: (order.get(x["status"], 9), x["tree"])):
        marg = r.get("margin_seconds")
        m = f"{marg:+.0f}s" if marg is not None else "-"
        flag = "" if r["status"] in ("FROZEN", "AMENDED_AFTER") else "   <-- "
        print(f"  {r['status']:22s} {r['tree']}/{r['comparator']}")
        print(f"      first commit {r.get('first_committed_utc')}   last commit "
              f"{r.get('committed_utc')}")
        print(f"      first marker {r['first_marker_utc']} ({r['first_marker']})"
              f"   margin(last) {m}{flag}")
        if r["status"] in ("UNFROZEN", "UNCOMMITTED", "MODIFIED_AFTER_COMMIT"):
            bad += 1
    print("-" * 100)
    n_amend = sum(1 for r in rows if r["status"] == "AMENDED_AFTER")
    print(f"  {len(rows)} comparator(s) in scope, {bad} violating, "
          f"{n_amend} amended after the first marker (W-4 territory, not 2d)")
    print("CANNOT SEE: whether a late edit touched the grading path or was "
          "purely additive; whether a disclosure exists; any tree with no markers.")
    if bad:
        print("VERDICT: FAIL")
        sys.exit(EXIT_VIOLATION)
    print("ZERO VERDICT: ZERO_IS_A_MEASUREMENT -- every comparator in scope "
          "was committed before its first case finished")
    print("VERDICT: PASS")
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
