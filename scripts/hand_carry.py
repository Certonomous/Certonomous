#!/usr/bin/env python3
"""The trees `git mv` will not move, derived -- then carried and CHECKED.

THE DEFECT CLASS
================
`git mv` moves a directory by renaming it, so gitignored siblings travel with
it.  But a directory holding NO TRACKED FILE AT ALL is not under version
control as far as `git mv` is concerned: the command fails, and MOVE_MAP
section 9 records that the failure has already gone unseen once because the
mover redirected stderr and because `git mv` with several sources aborts all of
them when one fails.

The consequence is silent and it is the shape of the whole hazard.  The rule
set of MOVE_MAP section 2 was built by classifying TRACKED PATHS.  A directory
with no tracked path is therefore invisible to it -- it does not appear in any
rule, it is not in the 13,084, and nothing in the plan says it should move.
Meanwhile the path CONSTANT that names it is a plain string in a `.py` or `.sh`
file, and the mechanical prefix rewrite of section 4.3 moves it happily.  So
the constant points at the new tree and the 1.51 GB is still sitting in the old
one, and no `git status`, no suite run and no file count will say so.

`demo-output/website/solve_registry/` -- 300 files, 1.51 GB, named by
`dispatch_queue.py:63`, `check_convergence_sweep.py:62`,
`contention_audit.py:55` and `launch_solve.sh:21` -- is the instance that
stranded the reverted attempt.  MOVE_MAP section 9 also records `**/surfaces/`
going the same way.

WHY THIS MODULE DERIVES THE SET INSTEAD OF LISTING IT
=====================================================
A hand-written checklist of dark trees is exactly as good as the moment it was
written.  Two of the four trees this module finds are NOT in the MOVE_MAP's
list, and one of them is created by the plan's own ordering:

  * `campaign/THERMAL_K0_runs/` matches R20's `*_runs` pattern, so the plan
    says it moves -- and it holds zero tracked files, so `git mv` will abort
    on it.  A rule naming a tree it cannot move.
  * `campaign/MESH_AUDIT_runs/` is tracked TODAY -- 78 files, every one a
    `*.log.checkMesh` solver-utility log.  Batch 2 untracks that class.  The
    moment batch 2 lands, this directory goes dark, and batch 7's `git mv`
    of it fails.  Nothing in the tree says so until it happens.

So the census is re-derived from the live tree at every invocation, and
`derive` is the mode you run before believing anything below it.
Evidence: `test_a_gitignored_only_tree_under_a_split_parent_is_hand_carry`,
`test_batch_2_untracking_creates_a_new_hand_carry`, and the two must-not-match
controls `test_the_must_not_match_control_a_tracked_tree_is_not_hand_carry` and
`test_a_dark_subtree_under_a_clean_directory_move_rides_along`, without which a
derivation that called everything stranded would satisfy the first two.

WHAT THE VERIFICATION IS FOR
============================
A hand-carry nobody checks is how 1.51 GB goes missing.  `carry` measures the
source immediately before the move -- file count, byte total, and the sorted
set of relative paths -- and afterwards asserts that the SOURCE IS GONE and the
DESTINATION HOLDS EXACTLY THAT SET.  A count alone is not enough: two trees can
share a count and differ in every file.

It also re-measures against the plan's own figures and ABORTS on any drift,
because these trees are live.  `THERMAL_K0_runs` was measured at 387 files and
again, ten minutes later, at 362.  A carry of a tree a solver is writing into
is a carry whose "after" count is not evidence of anything.
Evidence: `test_the_carry_itself_reddens_when_the_move_does_not_land_it_all`,
`test_the_after_check_reddens_when_the_destination_is_short`,
`test_the_after_check_reddens_when_the_bytes_differ`,
`test_the_after_check_reddens_when_the_path_set_differs`,
`test_the_after_check_reddens_when_the_source_is_recreated_with_files`,
`test_a_tree_that_changed_since_the_plan_is_refused`,
`test_a_tree_that_gained_a_tracked_file_is_refused`, and the clean-path control
`test_a_clean_carry_moves_the_tree_and_verifies_it`.

USAGE
    python3 scripts/hand_carry.py derive
    python3 scripts/hand_carry.py plan  --manifest <file>
    python3 scripts/hand_carry.py carry --manifest <file> [--only NAME ...]
    python3 scripts/hand_carry.py verify --manifest <file>

`derive`, `plan` and `verify` never write inside the repository.  `carry` is
the only mode that moves anything, and it refuses without a manifest written by
`plan`, so the inverse list exists before the batch starts (MOVE_MAP section 9:
"A batch without its inverse list does not start").

This module takes a required positional argument and calls `shutil.move`, so
`scripts/lab_check.py` classifies it `requires-arguments` and, failing that,
`writes-to-tree`.  It is never run by the suite.  Both are deliberate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# `lab_paths` binds its `REPO` at import from the environment.  Loading it by
# file location, rather than by `import`, means it is re-executed every time
# THIS module is loaded -- so a test that rebinds `LAB_REPO` to a synthetic
# tree gets a `lab_paths` bound to that tree, not the one `sys.modules` cached
# from the first call.  A carry harness that could only ever be exercised
# against the live repository is a harness nobody runs.
_LP_SPEC = importlib.util.spec_from_file_location(
    "lab_paths_for_hand_carry", Path(__file__).resolve().parent / "lab_paths.py")
lab_paths = importlib.util.module_from_spec(_LP_SPEC)
_LP_SPEC.loader.exec_module(lab_paths)

REPO = lab_paths.REPO
PASS, FAIL, UNKNOWN = 0, 1, 3

#: A tree written to more recently than this is live, and a carry of it cannot
#: be verified by count.  Overridable, never silently.
QUIET_SECONDS = 300


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

def tracked_paths() -> list[str]:
    cp = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z"],
                        capture_output=True)
    if cp.returncode:
        raise SystemExit("git ls-files failed: "
                         + cp.stderr.decode("utf-8", "replace"))
    return [p.decode("utf-8", "surrogateescape")
            for p in cp.stdout.split(b"\0") if p]


def measure(abs_dir: Path) -> dict:
    """Files, bytes, newest mtime and the exact relative-path set.

    The path set is what makes the after-check evidence.  Two trees can share a
    file count and a byte total and have nothing else in common.
    Evidence: `test_the_after_check_reddens_when_the_path_set_differs`, which
    preserves both the count and the byte total and swaps two names.
    """
    rels: list[str] = []
    nbytes = 0
    newest = 0.0
    for dp, _dns, fns in os.walk(abs_dir):
        for fn in fns:
            fp = Path(dp) / fn
            try:
                st = fp.lstat()
            except OSError:
                continue
            rels.append(str(fp.relative_to(abs_dir)))
            nbytes += st.st_size
            newest = max(newest, st.st_mtime)
    rels.sort()
    digest = hashlib.sha256("\n".join(rels).encode("utf-8",
                                                   "surrogateescape")).hexdigest()
    return {"files": len(rels), "bytes": nbytes, "newest_mtime": newest,
            "path_sha256": digest}


# ---------------------------------------------------------------------------
# Derivation
# ---------------------------------------------------------------------------

def maximal_dark_trees(tracked: list[str]) -> list[str]:
    """Every directory holding files on disk but no tracked file beneath it.

    Maximal only: a directory whose ancestor is also dark is subsumed, because
    carrying the ancestor carries it.
    """
    tracked_dirs = set()
    for p in tracked:
        parts = p.split("/")
        for i in range(len(parts) - 1):
            tracked_dirs.add("/".join(parts[: i + 1]))
    tracked_dirs.add("")

    nfiles: dict[str, int] = {}
    lit: dict[str, bool] = {}
    for dirpath, dirnames, filenames in os.walk(REPO, topdown=False,
                                                followlinks=False):
        rel = os.path.relpath(dirpath, REPO)
        rel = "" if rel == "." else rel
        if rel == ".git" or rel.startswith(".git/"):
            dirnames[:] = []
            continue
        n = len(filenames)
        for dn in dirnames:
            child = f"{rel}/{dn}" if rel else dn
            if child == ".git":
                continue
            n += nfiles.get(child, 0)
        nfiles[rel] = n
        on = rel in tracked_dirs
        if not on:
            for dn in dirnames:
                child = f"{rel}/{dn}" if rel else dn
                if lit.get(child):
                    on = True
                    break
        lit[rel] = on

    dark = {r for r, on in lit.items() if not on and nfiles.get(r, 0) > 0}
    out = []
    for d in dark:
        parts = d.split("/")
        if not any("/".join(parts[:i + 1]) in dark for i in range(len(parts) - 1)):
            out.append(d)
    return sorted(out)


def _clean_directory_move(a: str, tracked: list[str], memo: dict) -> bool:
    """Would `git mv <a> <redirect(a)>` land every tracked file under `a`
    exactly where the map says it goes?

    If yes, `a` is a directory the mover renames as one unit, and every dark
    tree beneath it rides along on the rename.  If the tracked files under `a`
    split across destinations -- `demo-output/website/campaign/` is the case
    that matters, R20 and R21 both live there -- then `a` is never renamed as a
    unit and nothing beneath it rides anywhere.
    Evidence: `test_a_dark_subtree_under_a_clean_directory_move_rides_along`
    and `test_a_gitignored_only_tree_under_a_split_parent_is_hand_carry`.
    """
    if a in memo:
        return memo[a]
    dst = lab_paths.redirect(a)
    if dst is None:
        memo[a] = False
        return False
    ok = False
    for p in tracked:
        if p == a or p.startswith(a + "/"):
            ok = True
            if lab_paths.redirect(p) != dst + p[len(a):]:
                memo[a] = False
                return False
    memo[a] = ok
    return ok


def derive(tracked: list[str] | None = None) -> dict:
    """The carry set, the ride-along set, and the trees that stay put."""
    tracked = tracked if tracked is not None else tracked_paths()
    memo: dict[str, bool] = {}
    carry, rides, stays = [], [], []
    for d in maximal_dark_trees(tracked):
        dst = lab_paths.redirect(d)
        m = measure(REPO / d)
        row = {"source": d, "dest": dst, **m}
        if dst is None:
            row["why"] = "no rule maps it; it stays where it is"
            stays.append(row)
            continue
        parts = d.split("/")
        carrier = None
        for i in range(len(parts) - 1):
            a = "/".join(parts[: i + 1])
            if _clean_directory_move(a, tracked, memo) \
                    and lab_paths.redirect(a) + d[len(a):] == dst:
                carrier = a
                break
        if carrier is not None:
            row["carried_by"] = carrier
            row["why"] = (f"rides along on `git mv {carrier}` -- ONLY if that "
                          f"move is made at directory granularity")
            rides.append(row)
        else:
            row["why"] = ("no ancestor is renamed as a unit, so `git mv` never "
                          "reaches it: HAND-CARRY")
            carry.append(row)
    carry.sort(key=lambda r: -r["bytes"])
    rides.sort(key=lambda r: -r["bytes"])
    stays.sort(key=lambda r: -r["bytes"])
    return {"carry": carry, "rides_along": rides, "stays": stays,
            "tracked": len(tracked)}


def batch2_survivors(tracked: list[str]) -> list[str]:
    """The tracked set as it will stand after batch 2's untracking.

    MOVE_MAP section 7.2's classes: `system/`, `constant/` and `0/` are case
    dictionaries and initial conditions -- source, they stay -- as are the
    prose and result suffixes.  Everything else inside a run tree is solver
    output and goes.  This is a PROJECTION, not the batch's own list; it exists
    to answer one question (which move sources lose their last tracked file),
    and it is deliberately generous about what stays so that the answer errs
    towards reporting fewer hazards than exist rather than more.
    """
    stay_ext = (".json", ".py", ".sh", ".md", ".png", ".stl", ".obj", ".csv",
                ".html", ".pdf", ".txt", ".yaml", ".yml", ".ps1", ".jsonl")
    src_seg = {"system", "constant", "0"}

    def in_run_tree(p: str) -> bool:
        for s in p.split("/")[:-1]:
            if (s.endswith(("_runs", "_work")) or s == "work"
                    or s.startswith(("logs_", "processor"))
                    or s in ("postProcessing", "dynamicCode")
                    or s.replace(".", "").isdigit()):
                return True
        return False

    def stays(p: str) -> bool:
        return any(s in src_seg for s in p.split("/")[:-1]) \
            or p.endswith(stay_ext)

    return [p for p in tracked if not (in_run_tree(p) and not stays(p))]


def project_after_untracking(tracked: list[str]) -> list[dict]:
    """Hand-carry trees that batch 2's untracking CREATES.

    Re-runs the same derivation against the projected post-batch-2 tracked set
    and reports what is in that carry set and not in today's.  Applying the
    same carrier logic is the whole point: a directory going dark is harmless
    when an ancestor is still renamed as a unit, and reporting those would bury
    the four that matter under seven hundred that do not.

    `campaign/MESH_AUDIT_runs/` is the instance.  Its 78 tracked files are
    every one a `*.log.checkMesh` solver-utility log, so batch 2 takes all of
    them; from that moment R20's `git mv` of it aborts.  Nothing in the tree
    says so until batch 7 runs.
    Evidence: `test_batch_2_untracking_creates_a_new_hand_carry` and its
    must-not-match control `test_the_must_not_match_control_for_the_projection`,
    which holds a run tree whose tracked files are case dictionaries and
    asserts nothing fires.
    """
    survivors = batch2_survivors(tracked)
    now = {r["source"] for r in derive(tracked)["carry"]}
    later = derive(survivors)["carry"]
    out = []
    for r in later:
        if r["source"] in now:
            continue
        r = dict(r)
        r["tracked_now"] = sum(1 for p in tracked
                               if p == r["source"] or p.startswith(r["source"] + "/"))
        out.append(r)
    return out


# ---------------------------------------------------------------------------
# Plan / carry / verify
# ---------------------------------------------------------------------------

def build_plan(quiet_seconds: int) -> dict:
    d = derive()
    now = time.time()
    items = []
    for row in d["carry"]:
        row = dict(row)
        row["live"] = (now - row["newest_mtime"]) < quiet_seconds
        row["inverse"] = f"mv {row['dest']} {row['source']}"
        items.append(row)
    return {
        "anchor": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                                 capture_output=True, text=True).stdout.strip(),
        "measured_at": now,
        "quiet_seconds": quiet_seconds,
        "items": items,
        "rides_along_count": len(d["rides_along"]),
        "rides_along_bytes": sum(r["bytes"] for r in d["rides_along"]),
        "stays": d["stays"],
        "gitignore_repoint": gitignore_repoint(items),
    }


def gitignore_repoint(items: list[dict]) -> list[str]:
    """Ignore patterns that name a carried tree by its OLD path.

    A carried tree whose ignore rule is not re-pointed stops being ignored the
    moment it lands, and 300 files of solver log become untracked noise that
    the next `git add` sweeps in.  `.gitignore:38` is
    `demo-output/website/solve_registry/`; `**/surfaces/` is path-independent
    and needs nothing.  Reported, never edited: `.gitignore` is not this
    module's to write.
    Evidence: `test_gitignore_patterns_naming_a_carried_tree_are_reported`,
    whose fixture carries both a pattern that must be rewritten and one that
    must be left alone.
    """
    gi = REPO / ".gitignore"
    if not gi.exists():
        return []
    out = []
    for n, line in enumerate(gi.read_text().splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        body = s[1:] if s.startswith("!") else s
        for it in items:
            if body.rstrip("/").lstrip("/").startswith(it["source"]):
                out.append(f".gitignore:{n}: {s}  ->  "
                           f"{s.replace(it['source'], it['dest'])}")
    return out


def carry(plan: dict, only: list[str], quiet_seconds: int) -> int:
    rc = PASS
    for it in plan["items"]:
        name = it["source"]
        if only and not any(o in name for o in only):
            continue
        src, dst = REPO / it["source"], REPO / it["dest"]
        print(f"\n--- {it['source']}  ->  {it['dest']}")

        if not src.is_dir():
            print(f"  FAIL: source is not a directory (already carried?)")
            rc = FAIL
            continue

        # Re-derive darkness at the instant of the move.  A tree that has
        # gained a tracked file since `plan` ran must go by `git mv`, not by
        # hand, or the index and the disk disagree.
        cp = subprocess.run(["git", "-C", str(REPO), "ls-files", "--", it["source"]],
                            capture_output=True, text=True)
        if cp.stdout.strip():
            n = len(cp.stdout.strip().splitlines())
            print(f"  FAIL: {n} tracked file(s) appeared under this tree since "
                  f"the plan was written. `git mv` now works and MUST be used; "
                  f"a hand `mv` would leave the index pointing at the old path.")
            rc = FAIL
            continue

        before = measure(src)
        drift = [k for k in ("files", "bytes", "path_sha256")
                 if before[k] != it[k]]
        if drift:
            print(f"  FAIL: the tree changed since the plan was written "
                  f"({', '.join(drift)}): plan {it['files']}f/{it['bytes']}B, "
                  f"now {before['files']}f/{before['bytes']}B. This tree is "
                  f"live; a carry of it cannot be verified by count. Re-run "
                  f"`plan` and carry it in a quiet window.")
            rc = FAIL
            continue
        age = time.time() - before["newest_mtime"]
        if age < quiet_seconds:
            print(f"  FAIL: written {age:.0f}s ago, inside the {quiet_seconds}s "
                  f"quiet window. Stop the writer or pass --quiet-seconds 0 "
                  f"and state why.")
            rc = FAIL
            continue
        if dst.exists():
            print(f"  FAIL: destination already exists; refusing to merge.")
            rc = FAIL
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        print(f"  measured {before['files']} files, {before['bytes']} bytes")
        print(f"  mv {src} {dst}")
        shutil.move(str(src), str(dst))

        # ---- the check the whole module exists for --------------------------
        after = measure(dst)
        ok = True
        if src.exists():
            leftover = measure(src)
            if leftover["files"]:
                print(f"  FAIL: source still holds {leftover['files']} file(s) "
                      f"/ {leftover['bytes']} bytes after the move")
                ok = False
            else:
                print(f"  note: source directory was recreated (empty) -- a "
                      f"writer is live against the old path")
        for k in ("files", "bytes", "path_sha256"):
            if after[k] != before[k]:
                print(f"  FAIL: destination {k} is {after[k]!r}, "
                      f"expected {before[k]!r}")
                ok = False
        if ok:
            print(f"  OK: destination holds {after['files']} files, "
                  f"{after['bytes']} bytes, path set matches "
                  f"({after['path_sha256'][:12]})")
        else:
            rc = FAIL
        it["carried"] = ok
        it["after"] = after
    return rc


def verify(plan: dict) -> int:
    rc = PASS
    for it in plan["items"]:
        src, dst = REPO / it["source"], REPO / it["dest"]
        if not dst.exists():
            print(f"NOT CARRIED  {it['source']}")
            continue
        after = measure(dst)
        bad = [k for k in ("files", "bytes", "path_sha256") if after[k] != it[k]]
        srcn = measure(src)["files"] if src.exists() else 0
        if bad or srcn:
            print(f"FAIL  {it['dest']}: mismatch on {bad or '-'}; "
                  f"source still holds {srcn} file(s)")
            rc = FAIL
        else:
            print(f"OK    {it['dest']}  {after['files']}f {after['bytes']}B")
    return rc


# ---------------------------------------------------------------------------

def _table(rows, title):
    print(f"\n=== {title} ({len(rows)} tree(s), "
          f"{sum(r['files'] for r in rows)} files, "
          f"{sum(r['bytes'] for r in rows)} bytes) ===")
    for r in rows:
        print(f"  {r['bytes']:>13,}B  {r['files']:>6} f  {r['source']}")
        print(f"                        -> {r['dest']}   [{r['why']}]")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=("derive", "plan", "carry", "verify"))
    ap.add_argument("--manifest", help="where the plan is written/read")
    ap.add_argument("--only", nargs="*", default=[],
                    help="carry only the trees whose path contains these")
    ap.add_argument("--quiet-seconds", type=int, default=QUIET_SECONDS)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.mode == "derive":
        tracked = tracked_paths()
        d = derive(tracked)
        proj = project_after_untracking(tracked)
        if args.json:
            print(json.dumps({**d, "dark_after_batch2": proj}, indent=1))
            return PASS
        _table(d["carry"], "HAND-CARRY -- git mv will never reach these")
        _table(d["rides_along"],
               "RIDES ALONG -- carried by an ancestor's directory rename ONLY")
        _table(d["stays"], "STAYS PUT -- no rule maps these")
        print(f"\n=== GOES DARK AFTER BATCH 2's UNTRACKING ({len(proj)}) ===")
        for r in proj:
            print(f"  {r['bytes']:>13,}B  {r['files']:>6} f  {r['source']}"
                  f"  (tracked now: {r['tracked_now']}, all untracked by "
                  f"batch 2)  -> {r['dest']}")
        print("\nThese are move sources whose LAST tracked file batch 2 removes."
              "\nEither carry them by hand after batch 2, or exclude their"
              "\nsurviving files from the untracking until after their move"
              "\nbatch has run. Doing neither aborts that batch's `git mv`.")
        return PASS

    if args.mode == "plan":
        if not args.manifest:
            print("plan needs --manifest")
            return UNKNOWN
        p = build_plan(args.quiet_seconds)
        Path(args.manifest).write_text(json.dumps(p, indent=1))
        print(f"anchor {p['anchor']}")
        print(f"{len(p['items'])} tree(s) to hand-carry, "
              f"{sum(i['files'] for i in p['items'])} files, "
              f"{sum(i['bytes'] for i in p['items'])} bytes")
        for i in p["items"]:
            live = "  *** LIVE, do not carry yet ***" if i["live"] else ""
            print(f"  {i['source']} -> {i['dest']}  "
                  f"({i['files']}f {i['bytes']}B){live}")
        print("\nINVERSE LIST (run these to undo, before any `git reset`):")
        for i in p["items"]:
            print(f"  {i['inverse']}")
        if p["gitignore_repoint"]:
            print("\n.gitignore patterns that name a carried tree by its OLD "
                  "path.\nRe-point them in the same commit or the tree stops "
                  "being ignored:")
            for line in p["gitignore_repoint"]:
                print("  " + line)
        print(f"\n{p['rides_along_count']} further dark tree(s) "
              f"({p['rides_along_bytes']} bytes) ride along on directory "
              f"renames.\nThey are carried ONLY if every `git mv` is made "
              f"against the DIRECTORY,\nnever file-by-file. That is batch "
              f"4-7's invariant.")
        print(f"\nwrote {args.manifest}")
        return PASS

    if not args.manifest or not Path(args.manifest).exists():
        print(f"{args.mode} needs a --manifest written by `plan`")
        return UNKNOWN
    plan = json.loads(Path(args.manifest).read_text())
    if args.mode == "verify":
        return verify(plan)

    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    if head != plan["anchor"]:
        print(f"NOTE: HEAD moved since the plan ({plan['anchor'][:8]} -> "
              f"{head[:8]}). The measurements are re-checked per tree below.")
    rc = carry(plan, args.only, args.quiet_seconds)
    Path(args.manifest).write_text(json.dumps(plan, indent=1))
    print(f"\n{'PASS' if rc == PASS else 'FAIL'}: manifest updated at "
          f"{args.manifest}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
