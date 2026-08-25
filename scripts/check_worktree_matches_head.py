#!/usr/bin/env python3
"""Fire when a TRACKED record on disk is not the record that is in HEAD.

WHY THIS EXISTS, and it is not hygiene. Under the private-index protocol a
commit can be built from a base read out of git -- `git show HEAD:<path>`, append,
`git hash-object -w`, `git update-index --cacheinfo` -- and that path writes the
COMMIT and never the WORKTREE FILE. Rule 10's mandated post-commit verify is
`git diff HEAD~1 HEAD --stat`, which grades the commit and is SILENT ABOUT THE
DISK. So an append can land in HEAD and never land on disk, and nothing in the
protocol notices.

The consequence is not a tidiness problem, because rule 6 makes an appended dated
amendment the ONLY lawful way a frozen document changes. If amendments reliably
fail to reach the disk, then RULE 6'S MECHANISM IS SILENTLY BROKEN FOR EVERY
READER WHO DOES NOT USE `git show`. Measured on this repository 2026-08-25 at
HEAD `59c3d8f6`: `docs/charters/ANSYS_VERIFICATION_CHARTER.md` on disk stopped at
v1.2 and was missing FOUR appended amendments (373 lines); the disk copy of
`verification/campaign/F11_CONVERSION_PREREGISTRATION.md` was missing AMENDMENT 2
ENTIRELY -- the amendment that WITHDRAWS a "Sanaa's directive, verbatim"
attribution. A lane grading against that worktree copy would have graded against
withdrawn text and would have had no way to know.

PRIOR ART, because this instrument is not the discovery. The mechanism is
`docs/LESSONS.md` L-253 (2026-08-23, verification): "a private-index protocol that
never writes the worktree makes the worktree stale BY DESIGN -- and it selectively
destroys the work of exactly the teams that follow it." L-307 adds that the gap is
NON-STATIONARY -- its size AND DIRECTION move within minutes -- and names the valid
manual instrument: "a direct `diff` of `git show HEAD:<path>` against the worktree
file". What did not exist until this script is a REPEATABLE SWEEP of that
comparison with a graded classification and planted controls. That, and only that,
is what is new here.

--------------------------------------------------------------------------------
THE CLASSIFICATION, and why the distinction is the whole point

    MATCH       disk bytes == HEAD blob bytes.
    BEHIND      disk is a STRICT PREFIX of the HEAD blob (shorter, and every byte
                it has agrees). This is the append-that-never-landed signature.
    AHEAD       the HEAD blob is a strict prefix of disk (longer, agrees on the
                common part). Somebody's UNCOMMITTED work in progress.
    DIVERGENT   neither is a prefix of the other. The two copies have genuinely
                different content.
    ABSENT      tracked in HEAD, not on disk.
    UNREADABLE  on disk and could not be read. REFUSED, never reported MATCH.

BEHIND IS THE ONLY CLASS THAT IS SAFE TO REPAIR, and the reason is provable per
file rather than asserted: A STRICT PREFIX CARRIES NO INFORMATION THAT IS NOT
ALREADY IN HEAD. If the disk content is byte-for-byte the first N bytes of the
HEAD blob, then writing the HEAD blob over it destroys nothing -- there is no
unique local content to lose. That proof is what makes the write a RESTORE and
not a revert, and it is why rule 10's "inspected, never reverted" is satisfied
rather than bent. AHEAD and DIVERGENT carry bytes that exist nowhere else; they
are somebody's live uncommitted work and this script never proposes touching them.

--------------------------------------------------------------------------------
WHAT THIS CHECK CANNOT SEE. Stated here and printed beside every verdict, because
L-307's second half is that a passing planted control proves an instrument can see
what it measures and proves NOTHING about what it does not measure.

  * WHY a file is BEHIND. The classification is a byte relation. It does not
    distinguish an append that never reached the worktree from a truncation, an
    interrupted write, or a partial copy. All three are strict prefixes.
  * WHETHER A REPAIR IS WANTED. BEHIND says restoring loses no bytes. It does not
    say the HEAD content is correct, and it is not a licence to repair another
    team's file -- ownership is a charter question, not a byte question.
  * ANY FILE THAT IS NOT TRACKED .md UNDER THE SWEPT PATHS. Untracked drafts,
    non-markdown records, and paths outside `verification/` and `docs/` are
    invisible here. A clean report is not a clean repository.
  * THE INSTANT AFTER IT RAN. L-307: the gap is non-stationary. Every line of
    output carries the sha and the UTC stamp it was measured at, and is void
    without them.
  * WHETHER HEAD IS RIGHT. This compares two copies. It never grades content.

--------------------------------------------------------------------------------
WHY THE TRACKED SET COMES FROM `git ls-tree -r HEAD` AND NEVER `git ls-files`

`git ls-files` consults the SHARED INDEX, which in this repository is a snapshot
frozen at its last load event and decays as HEAD moves (D486, L-294, L-307).
Measured 2026-08-25 on this box: `git ls-tree -r HEAD -- verification docs` listed
565 tracked `.md` while `git ls-files` listed 464 -- THE INDEX HID 101 TRACKED
FILES, 18% of the population, from any sweep that asked it. An instrument for
worktree staleness that enumerated via the index would be blind to exactly the
files most likely to be stale. Likewise nothing here consults `git status` or
`git diff HEAD`; both read the index and neither is an instrument in this repo.

--------------------------------------------------------------------------------
THIS SCRIPT GATES NOTHING. `D480` puts the rule-10 base-from-git amendment on
Sanaa's desk and states that wiring such instruments into `check_harness` or any
gate is NOT authorized ahead of her ruling. Default exit is 0 (report only).
`--strict` is opt-in for an operator who has asked for it. A REFUSAL (exit 2) is
not a gate: it is the instrument declining to report a reading it could not take.

    python3 scripts/check_worktree_matches_head.py            # report, exit 0
    python3 scripts/check_worktree_matches_head.py --strict    # exit 1 on non-MATCH
    python3 scripts/check_worktree_matches_head.py --tsv       # machine rows
    python3 scripts/check_worktree_matches_head.py --show-all  # include MATCH rows
    python3 scripts/check_worktree_matches_head.py --selftest  # controls + mutants

EXIT CODES
    0  swept, nothing refused (findings may still be reported)
    1  --strict and at least one non-MATCH finding
    2  REFUSED: an UNREADABLE file, or git would not answer
    3  --selftest failed
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time

DEFAULT_PATHS = ("verification", "docs")
SUFFIX = ".md"

KINDS = ("MATCH", "BEHIND", "AHEAD", "DIVERGENT", "ABSENT", "UNREADABLE")
REFUSAL_KINDS = ("UNREADABLE",)

CANNOT_SEE = [
    "WHY a file is BEHIND (append-never-landed, truncation and partial write are",
    "  all strict prefixes and are not distinguished here)",
    "whether a repair is WANTED, or whose file it is to repair",
    "anything untracked, non-.md, or outside the swept paths",
    "the instant after this ran -- the gap is non-stationary (L-307); this",
    "  reading is void without the sha and stamp printed above",
    "whether HEAD is CORRECT -- this compares two copies, it never grades content",
]


# ---------------------------------------------------------------------------
# the classifier. Kept small and pure so the mutation harness can target it.
# ---------------------------------------------------------------------------
def classify(disk, blob):
    """Return the byte relation between the worktree bytes and the HEAD blob."""
    if disk == blob:
        return "MATCH"
    if len(disk) < len(blob):
        if blob[: len(disk)] == disk:  # MUTANT_ANCHOR_PREFIX_BEHIND
            return "BEHIND"  # MUTANT_ANCHOR_LABEL_BEHIND
        return "DIVERGENT"
    if len(disk) > len(blob):
        if disk[: len(blob)] == blob:  # MUTANT_ANCHOR_PREFIX_AHEAD
            return "AHEAD"  # MUTANT_ANCHOR_LABEL_AHEAD
        return "DIVERGENT"
    return "DIVERGENT"  # same length, different bytes


# ---------------------------------------------------------------------------
# git plumbing. HEAD is captured ONCE by the caller and threaded through, so a
# peer moving HEAD mid-sweep cannot silently split the reading (L-223, L-307).
# ---------------------------------------------------------------------------
def git(root, *args):
    env = dict(os.environ)
    env.pop("GIT_INDEX_FILE", None)  # never consult a private or shared index
    return subprocess.run(
        ["git", "-C", root, *args], capture_output=True, env=env
    )


def git_text(root, *args):
    p = git(root, *args)
    if p.returncode != 0:
        raise RuntimeError(
            "git %s failed rc=%d: %s"
            % (" ".join(args), p.returncode, p.stderr.decode("utf-8", "replace").strip())
        )
    return p.stdout.decode("utf-8", "replace")


def tracked_md(root, head, paths):
    """The tracked set, from the COMMIT TREE. Never `git ls-files` -- see header."""
    out = git_text(root, "ls-tree", "-r", "--name-only", head, "--", *paths)
    return sorted(f for f in out.split("\n") if f.endswith(SUFFIX))


def sweep(root, head, paths):
    rows = []
    for rel in tracked_md(root, head, paths):
        p = git(root, "cat-file", "blob", "%s:%s" % (head, rel))
        if p.returncode != 0:
            rows.append((rel, "UNREADABLE", -1, -1, "HEAD blob would not read"))
            continue
        blob = p.stdout
        full = os.path.join(root, rel)
        if not os.path.exists(full):
            rows.append((rel, "ABSENT", -1, len(blob), "tracked in HEAD, not on disk"))
            continue
        try:
            with open(full, "rb") as fh:
                disk = fh.read()
        except Exception as exc:  # noqa: BLE001 - any read failure is a refusal
            rows.append(
                (rel, "UNREADABLE", -1, len(blob), "%s: %s" % (type(exc).__name__, exc))
            )
            continue
        kind = classify(disk, blob)
        rows.append((rel, kind, len(disk), len(blob), ""))
    return rows


# ---------------------------------------------------------------------------
# selftest: planted VALUE controls, then MUTATION controls on this same file.
# ---------------------------------------------------------------------------
CONTROLS = {
    # name: (committed bytes, worktree bytes or None to delete, expected kind)
    "c_match": (b"alpha\nbeta\n", b"alpha\nbeta\n", "MATCH"),
    "c_behind": (b"alpha\nbeta\ngamma\n", b"alpha\nbeta\n", "BEHIND"),
    "c_behind_empty": (b"alpha\n", b"", "BEHIND"),
    "c_ahead": (b"alpha\n", b"alpha\nbeta\n", "AHEAD"),
    "c_divergent_shorter": (b"alpha\nbeta\ngamma\n", b"alpha\nZETA\n", "DIVERGENT"),
    "c_divergent_longer": (b"alpha\n", b"ZETA\nbeta\n", "DIVERGENT"),
    "c_divergent_samelen": (b"alpha\n", b"alphb\n", "DIVERGENT"),
    "c_absent": (b"alpha\n", None, "ABSENT"),
}
UNREADABLE_CONTROL = "c_unreadable"

# Everything from this sentinel down is the mutation TABLE, not mutable code.
# The selftest confines its substitutions to the region ABOVE this line, because
# the table quotes every anchor verbatim and would otherwise match twice.
MUTANT_TABLE_SENTINEL = "MUTANTS = {"

MUTANTS = {
    # name: (substitution, {control: expected kind under the mutant})
    "M1_behind_labelled_ahead": (
        ('return "BEHIND"  # MUTANT_ANCHOR_LABEL_BEHIND', 'return "AHEAD"'),
        {"c_behind": "AHEAD", "c_behind_empty": "AHEAD"},
    ),
    "M2_prefix_test_removed_behind": (
        ("if blob[: len(disk)] == disk:  # MUTANT_ANCHOR_PREFIX_BEHIND", "if True:"),
        {"c_divergent_shorter": "BEHIND"},
    ),
    "M3_prefix_test_removed_ahead": (
        ("if disk[: len(blob)] == blob:  # MUTANT_ANCHOR_PREFIX_AHEAD", "if True:"),
        {"c_divergent_longer": "AHEAD"},
    ),
    "M4_fail_open_on_unreadable": (
        ('rows.append(\n                (rel, "UNREADABLE", -1, len(blob), "%s: %s" % (type(exc).__name__, exc))\n            )',
         'rows.append((rel, "MATCH", -1, len(blob), "MUTANT fail-open"))'),
        {UNREADABLE_CONTROL: "MATCH"},
    ),
}


def _clear_pycache(root):
    """Stale bytecode inverts mutation tests, and PYTHONDONTWRITEBYTECODE does
    NOT fix it -- the cache must be DELETED between control runs."""
    for dirpath, dirnames, _ in os.walk(root):
        for d in list(dirnames):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(dirpath, d), ignore_errors=True)
                dirnames.remove(d)


def _build_control_repo(root):
    # RULE 10. The `git add -A` below is lawful ONLY because `root` is a throwaway
    # temp repo. Nothing used to say so, and a refactor that hoisted this helper
    # would turn it into a directory sweep of the SHARED tree (L-12, twice).
    #
    # THIS IS A `raise` AND NOT AN `assert`, AND THAT IS THE WHOLE POINT.
    # `python3 -O` and PYTHONOPTIMIZE REMOVE every `assert`, and a stripped assert
    # leaves NO TRACE -- the function simply proceeds. Measured on this box against
    # this guard's exact former shape: normal mode rc=1 AssertionError (refused);
    # `python3 -O` rc=0, "PROCEEDED TO add -A on /home/ubuntu/Certonomous"; and
    # PYTHONOPTIMIZE=1 identically. A refusal that protects the shared tree must
    # survive every interpreter flag, so it raises. `_o_flag_control()` below runs
    # THIS path under `-O` so the property is measured and not merely asserted in
    # a comment. Standing for cfd's instruments: an `assert` may carry an invariant
    # whose violation is a programming error, NEVER a refusal, guard, control or gate.
    _r = os.path.realpath(root)
    _inside_tempdir = _r.startswith(os.path.realpath(tempfile.gettempdir()) + os.sep)
    _not_the_repo_root = _r != os.path.realpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    )
    if not (_inside_tempdir and _not_the_repo_root):
        raise RuntimeError(
            "_build_control_repo runs `git add -A`: root must be a throwaway temp repo "
            "and must not be the Certonomous root; refusing %s" % _r
        )
    env = dict(os.environ)
    env.pop("GIT_INDEX_FILE", None)
    env.update(
        GIT_AUTHOR_NAME="selftest",
        GIT_AUTHOR_EMAIL="selftest@localhost",
        GIT_COMMITTER_NAME="selftest",
        GIT_COMMITTER_EMAIL="selftest@localhost",
    )

    def g(*a):
        p = subprocess.run(["git", "-C", root, *a], capture_output=True, env=env)
        if p.returncode != 0:
            raise RuntimeError("control repo git %s: %s" % (a, p.stderr))
        return p.stdout.decode()

    g("init", "-q", "-b", "main")
    d = os.path.join(root, "docs")
    os.makedirs(d, exist_ok=True)
    for name, (committed, _, _) in CONTROLS.items():
        with open(os.path.join(d, name + SUFFIX), "wb") as fh:
            fh.write(committed)
    with open(os.path.join(d, UNREADABLE_CONTROL + SUFFIX), "wb") as fh:
        fh.write(b"unreadable control\n")
    g("add", "-A", "docs")  # a throwaway control repo, not the shared index
    g("commit", "-q", "-m", "controls")
    # now perturb the WORKTREE only
    for name, (_, worktree, _) in CONTROLS.items():
        path = os.path.join(d, name + SUFFIX)
        if worktree is None:
            os.remove(path)
        else:
            with open(path, "wb") as fh:
                fh.write(worktree)
    # an UNREADABLE that does not depend on uid: replace the file with a directory,
    # so open() raises IsADirectoryError even for root.
    up = os.path.join(d, UNREADABLE_CONTROL + SUFFIX)
    os.remove(up)
    os.mkdir(up)
    return g("rev-parse", "HEAD").strip()


def _o_flag_control(script_path, tmp):
    """Drive `_build_control_repo`'s refusal path under `python3 -O`.

    WHY THIS EXISTS. An `assert`-based guard passes every normal-mode test and is
    DELETED by `-O`, leaving no trace: the function just proceeds. No test written
    in normal mode can see that, which is exactly how the assert form of this
    guard survived review. Only running the interpreter WITH the flag can.

    EVERY PROBE DRIVES A SACRIFICIAL COPY of this module inside a temp tree, and
    each sets TMPDIR so the clause under test is the one that fires. So even a
    FULLY STRIPPED guard cannot reach the shared repository -- the control cannot
    cause the catastrophe it is testing for.
    """
    base = os.path.join(tmp, "oflag")
    projroot = os.path.join(base, "proj")
    os.makedirs(os.path.join(projroot, "scripts"), exist_ok=True)
    copy = os.path.join(projroot, "scripts", os.path.basename(script_path))
    shutil.copy(script_path, copy)
    elsewhere = os.path.join(base, "tmpelsewhere")
    outside = os.path.join(base, "outside", "repo")
    lawful = os.path.join(base, "lawful_repo")
    for d in (elsewhere, outside, lawful):
        os.makedirs(d, exist_ok=True)

    drive = os.path.join(base, "drive.py")
    with open(drive, "w", encoding="utf-8") as fh:
        fh.write(
            "import importlib.util, sys\n"
            "spec = importlib.util.spec_from_file_location('c', sys.argv[1])\n"
            "m = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(m)\n"
            "try:\n"
            "    m._build_control_repo(sys.argv[2])\n"
            "    print('PROCEEDED')\n"
            "except RuntimeError:\n"
            "    print('REFUSED')\n"
        )

    # (label, TMPDIR for the child, root handed to the guard, required answer)
    probes = [
        ("clause 1: root outside gettempdir()", elsewhere, outside, "REFUSED"),
        ("clause 2: root IS the module's repo root", base, projroot, "REFUSED"),
        ("positive: a lawful throwaway temp repo", base, lawful, "PROCEEDED"),
    ]
    ok = True
    for label, tmpdir, root, want in probes:
        env = dict(os.environ)
        env["TMPDIR"] = tmpdir
        env.pop("GIT_INDEX_FILE", None)
        env.pop("PYTHONOPTIMIZE", None)
        p = subprocess.run(
            [sys.executable, "-O", drive, copy, root], capture_output=True, env=env
        )
        out = p.stdout.decode().strip().splitlines()
        have = out[-1] if out else "<no output: %s>" % p.stderr.decode().strip()[-60:]
        good = have == want
        ok = ok and good
        print("  %s %-42s want=%-10s got=%s" % ("ok  " if good else "FAIL", label, want, have))
    return ok


def _run_variant(script_path, repo, head, workdir):
    _clear_pycache(workdir)
    p = subprocess.run(
        [sys.executable, script_path, "--root", repo, "--paths", "docs",
         "--at", head, "--tsv", "--show-all"],
        capture_output=True,
    )
    got = {}
    for line in p.stdout.decode("utf-8", "replace").split("\n"):
        if not line.startswith("ROW\t"):
            continue
        _, kind, _dl, _bl, rel = line.split("\t", 4)
        got[os.path.basename(rel)[: -len(SUFFIX)]] = kind
    return got, p.returncode


def selftest():
    ok = True
    tmp = tempfile.mkdtemp(prefix="cwmh_selftest_")
    try:
        repo = os.path.join(tmp, "repo")
        os.makedirs(repo)
        head = _build_control_repo(repo)
        me = os.path.abspath(__file__)

        print("PLANTED VALUE CONTROLS (pristine classifier)")
        got, rc = _run_variant(me, repo, head, tmp)
        expected = {n: k for n, (_, _, k) in CONTROLS.items()}
        expected[UNREADABLE_CONTROL] = "UNREADABLE"
        for name in sorted(expected):
            want, have = expected[name], got.get(name, "<missing>")
            mark = "ok  " if want == have else "FAIL"
            if want != have:
                ok = False
            print("  %s %-24s want=%-10s got=%s" % (mark, name, want, have))
        if rc != 2:
            ok = False
            print("  FAIL an UNREADABLE control must REFUSE (exit 2); got exit %d" % rc)
        else:
            print("  ok   refusal: UNREADABLE forced exit 2 rather than degrading")

        print()
        print("MUTATION CONTROLS -- each mutant must make the controls FLIP.")
        print("(a control that cannot fail is not a control)")
        src = open(me, "r", encoding="utf-8").read()
        # The mutation TABLE quotes the anchors verbatim, so a whole-file search
        # finds each anchor twice. Confine substitution to the CODE region above
        # the table; a hit count != 1 there is a genuine anchor failure and is a
        # selftest FAILURE, never a silent skip.
        cut = src.index(MUTANT_TABLE_SENTINEL)
        code, tail = src[:cut], src[cut:]
        for mname in sorted(MUTANTS):
            (old, new), flips = MUTANTS[mname]
            if code.count(old) != 1:
                ok = False
                print("  FAIL %-32s anchor not unique in code region (%d hits)"
                      % (mname, code.count(old)))
                continue
            mdir = os.path.join(tmp, mname)
            os.makedirs(mdir, exist_ok=True)
            mpath = os.path.join(mdir, "mutant.py")
            with open(mpath, "w", encoding="utf-8") as fh:
                fh.write(code.replace(old, new, 1) + tail)
            mgot, _mrc = _run_variant(mpath, repo, head, tmp)
            for cname, want_mut in flips.items():
                have = mgot.get(cname, "<missing>")
                pristine = expected[cname]
                flipped = have == want_mut and have != pristine
                if not flipped:
                    ok = False
                print("  %s %-32s %-22s pristine=%-10s mutant=%-10s"
                      % ("ok  " if flipped else "FAIL", mname, cname, pristine, have))

        print()
        print("INTERPRETER-FLAG CONTROL -- the `add -A` guard must refuse under `python3 -O`.")
        print("(`assert` is REMOVED by -O; a guard that vanishes under a flag is not a guard)")
        if not _o_flag_control(me, tmp):
            ok = False

        print()
        print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
        return 0 if ok else 3
    finally:
        # the UNREADABLE control is a directory; rmtree handles it
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Compare tracked .md on disk against the HEAD blob."
    )
    ap.add_argument("--root", default=".", help="repository root to sweep")
    ap.add_argument("--paths", nargs="*", default=list(DEFAULT_PATHS))
    ap.add_argument("--at", default=None, help="grade against this commit (default HEAD)")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any non-MATCH")
    ap.add_argument("--tsv", action="store_true", help="machine rows")
    ap.add_argument("--show-all", action="store_true", help="include MATCH rows")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    root = os.path.abspath(args.root)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        head = args.at or git_text(root, "rev-parse", "HEAD").strip()
        rows = sweep(root, head, args.paths)
        head_after = git_text(root, "rev-parse", "HEAD").strip()
    except RuntimeError as exc:
        print("REFUSED: %s" % exc)
        return 2

    counts = {k: 0 for k in KINDS}
    for _rel, kind, _dl, _bl, _n in rows:
        counts[kind] = counts.get(kind, 0) + 1

    if args.tsv:
        for rel, kind, dl, bl, note in rows:
            if kind == "MATCH" and not args.show_all:
                continue
            print("ROW\t%s\t%d\t%d\t%s" % (kind, dl, bl, rel))
    else:
        print("worktree-vs-HEAD, tracked %s under: %s" % (SUFFIX, " ".join(args.paths)))
        print("  measured at %s   HEAD %s" % (stamp, head))
        if args.at is None and head_after != head:
            print("  *** HEAD MOVED DURING THE SWEEP (now %s) -- this reading is"
                  " SPLIT ACROSS TWO TREES; re-run before quoting it" % head_after)
        print("  population %d   %s" % (
            len(rows),
            "  ".join("%s=%d" % (k, counts[k]) for k in KINDS if counts[k]),
        ))
        print()
        for rel, kind, dl, bl, note in sorted(rows, key=lambda r: (r[1], r[0])):
            if kind == "MATCH" and not args.show_all:
                continue
            extra = ("  %s" % note) if note else ""
            print("  %-10s disk=%8s head=%8s  %s%s"
                  % (kind, dl if dl >= 0 else "-", bl if bl >= 0 else "-", rel, extra))
        if counts.get("BEHIND"):
            print()
            print("  BEHIND is a STRICT PREFIX: the disk copy carries no byte that is")
            print("  not already in HEAD, so restoring the HEAD blob over it destroys")
            print("  nothing. That proof is per file and is what makes the write a")
            print("  RESTORE, not a revert. AHEAD and DIVERGENT carry bytes that exist")
            print("  nowhere else -- they are live uncommitted work; do not touch them.")
        print()
        print("  CANNOT SEE:")
        for line in CANNOT_SEE:
            print("    %s%s" % ("" if line.startswith("  ") else "- ", line))
        print()
        print("  This script GATES NOTHING (D480: wiring is Sanaa's ruling, not an"
              " agent's).")

    refused = sum(counts.get(k, 0) for k in REFUSAL_KINDS)
    if refused:
        if not args.tsv:
            print("\nREFUSED: %d file(s) UNREADABLE -- reported as UNREADABLE, never"
                  " as MATCH." % refused)
        return 2
    if args.strict and any(counts.get(k, 0) for k in KINDS if k != "MATCH"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
