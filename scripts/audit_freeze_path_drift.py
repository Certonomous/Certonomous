#!/usr/bin/env python3
"""
audit_freeze_path_drift.py -- does a pre-registration's freeze survive a rename?

WHY THIS EXISTS
---------------
CLAUDE.md rule 2 makes a pre-registration's evidentiary content its FREEZE: the
gate could not have been chosen to fit the answer, and that is proved by hashing
the frozen file against the blob committed at the freeze commit.  The proof is
normally written

    git show <freeze_commit>:<current_path>   vs   git show HEAD:<current_path>

and that form has TWO failure edges, both observed in this repository:

  (a) FALSE ALARM.  If the file was ADDED at one path and later MOVED, the
      CURRENT path does not resolve at the FREEZE commit.  git returns nothing;
      md5 of nothing is d41d8cd98f00b204e9800998ecf8427e.  A perfectly good
      freeze reads as unprovable and a real result gets discarded or re-run.
      Observed: verification/campaign/DMR_PREREGISTRATION.md, added as
      demo-output/website/campaign/DMR_PREREGISTRATION.md at 74797a57 and moved
      by the MOVE_MAP batch a1fbe127.  Blob a08ee245... is identical at the
      freeze commit, at HEAD and on disk.

  (b) FALSE COMFORT, which is worse.  A checker that compares the two reads
      WITHOUT asserting each is non-empty compares two empty strings and calls
      them EQUAL.  That is a freeze check that PASSES on a file which did not
      exist at the freeze commit at all.

METHOD -- TWO INDEPENDENT MECHANISMS, ON PURPOSE
------------------------------------------------
L-427's addendum: a check must be able to fail for a reason its author did not
already know, and a check derived from the thing it checks has been pre-agreed
with it.  So the add-path is derived TWICE, by mechanisms that share no code
path inside git:

  MECHANISM A -- `git log --follow` on the single target path.  git's own
      rename heuristic, applied per file, walking backwards.
  MECHANISM B -- a forward replay of the WHOLE history.  One pass of
      `git log --reverse --raw -M` over every commit, maintaining a
      path -> identity map: A creates an identity, R moves it, D kills it, M
      appends a blob.  Nothing per-file, nothing backwards, no --follow.

Rows where A and B disagree are printed as DISAGREE and are the interesting
output, not noise.

RULE 3 -- PLANTED CONTROL
-------------------------
--selftest builds a throwaway repository (in a tempdir, never the shared
worktree) containing a file that WAS renamed and a file that was NOT, plus a
blob that changed after its add and one that did not, and asserts the detector
classifies each correctly under BOTH mechanisms.  If the detector cannot see a
planted rename it REFUSES (exit 2) rather than report a clean sweep.

Exit: 0 audit ran, 2 refusal (selftest failed, or not a git repo).
"""
import argparse
import collections
import os
import re
import subprocess
import sys

EXIT_OK, EXIT_REFUSE = 0, 2
EMPTY_MD5 = "d41d8cd98f00b204e9800998ecf8427e"

# lines rule 2 forbids moving after first compute
GATE_LINE = re.compile(
    r"(gate|threshold|cap|label|budget|core[- ]min|PASS if|FAIL if|criterion)",
    re.I)


def git(repo, *args, binary=False):
    r = subprocess.run(["git", "-C", repo] + list(args),
                       capture_output=True, text=not binary)
    return r.returncode, (r.stdout if binary else r.stdout.rstrip("\n")), r.stderr


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# ---------------------------------------------------------------------------
# MECHANISM A -- git log --follow, per file, backwards
# ---------------------------------------------------------------------------
def mech_a(repo, path):
    """(add_commit, add_path, n_commits) from git's own per-file rename walk."""
    rc, out, _ = git(repo, "log", "--follow", "--format=@@%H",
                     "--name-status", "--", path)
    if rc != 0 or not out.strip():
        return None, None, 0
    commits, blocks, cur = [], [], None
    for line in out.splitlines():
        if line.startswith("@@"):
            cur = line[2:]
            commits.append(cur)
            blocks.append((cur, []))
        elif line.strip() and blocks:
            blocks[-1][1].append(line)
    add_commit, add_path = None, None
    # the OLDEST block is the birth; its name-status says at which path
    for sha, lines in reversed(blocks):
        if not lines:
            continue
        f = lines[0].split("\t")
        if f[0].startswith("A"):
            add_commit, add_path = sha, f[1]
        elif f[0].startswith(("R", "C")) and len(f) >= 3:
            # oldest visible event is a rename: --follow stopped at the rename,
            # the true birth is at the OLD path
            add_commit, add_path = sha, f[1]
        else:
            add_commit, add_path = sha, f[-1]
        break
    return add_commit, add_path, len(commits)


# ---------------------------------------------------------------------------
# MECHANISM B -- forward replay of the whole history, no --follow anywhere
# ---------------------------------------------------------------------------
def replay(repo, rename_score="50", detect_renames=True):
    """path -> identity record, built by walking every commit oldest-first.

    detect_renames=False is the ADVERSARIAL control: with git's rename
    detection off the replay must LOSE every rename, which proves the AGREE
    rows are being produced by rename detection and not by the walk agreeing
    with itself."""
    ropt = (f"--find-renames={rename_score}%" if detect_renames
            else "--no-renames")
    rc, out, err = git(repo, "log", "--reverse", "--topo-order", "--root",
                       ropt, "--raw", "--no-abbrev", "--format=@@%H %cI")
    if rc != 0:
        refuse("git log replay failed: " + err[:200])
    alive = {}
    events = collections.defaultdict(list)
    sha = iso = None
    n_commits = 0
    for line in out.splitlines():
        if line.startswith("@@"):
            sha, iso = line[2:].split(" ", 1)
            n_commits += 1
            continue
        if not line.startswith(":"):
            continue
        # :100644 100644 <pre> <post> <STATUS>\t<path>[\t<path2>]
        meta, _, rest = line.partition("\t")
        parts = meta.split()
        if len(parts) < 5:
            continue
        pre, post, status = parts[2], parts[3], parts[4]
        names = rest.split("\t")
        if status.startswith("R") or status.startswith("C"):
            if len(names) < 2:
                continue
            old, new = names[0], names[1]
            if status.startswith("R"):
                rec = alive.pop(old, None)
                if rec is None:            # rename of something we never saw born
                    rec = dict(add_commit=sha, add_iso=iso, add_path=old,
                               add_blob=pre, blobs=[], orphan_rename=True)
                rec.setdefault("renames", []).append((sha, iso, old, new))
                if post != pre:
                    rec["blobs"].append((sha, iso, post, "R-with-edit"))
                alive[new] = rec
                events[new].append(("R", sha, old, new))
            else:                          # copy: a NEW identity is born
                alive[new] = dict(add_commit=sha, add_iso=iso, add_path=new,
                                  add_blob=post, blobs=[], copied_from=old)
                events[new].append(("C", sha, old, new))
        elif status.startswith("A"):
            p = names[0]
            alive[p] = dict(add_commit=sha, add_iso=iso, add_path=p,
                            add_blob=post, blobs=[])
            events[p].append(("A", sha, p, p))
        elif status.startswith("D"):
            p = names[0]
            rec = alive.pop(p, None)
            if rec is not None:
                rec["deleted_at"] = sha
            events[p].append(("D", sha, p, p))
        elif status.startswith("M") or status.startswith("T"):
            p = names[0]
            rec = alive.get(p)
            if rec is None:
                rec = dict(add_commit=sha, add_iso=iso, add_path=p,
                           add_blob=pre, blobs=[], orphan_modify=True)
                alive[p] = rec
            rec["blobs"].append((sha, iso, post, "M"))
            events[p].append(("M", sha, p, p))
    return alive, events, n_commits


# ---------------------------------------------------------------------------
# the audit
# ---------------------------------------------------------------------------
def gate_lines(text):
    return [l.rstrip() for l in text.splitlines() if GATE_LINE.search(l)]


def audit(repo, targets, alive, verbose=False):
    rows = []
    for rel in targets:
        rc_h, head_blob, _ = git(repo, "rev-parse", f"HEAD:{rel}")
        head_blob = head_blob if rc_h == 0 else None
        a_commit, a_path, a_n = mech_a(repo, rel)
        b = alive.get(rel)
        b_commit = b["add_commit"] if b else None
        b_path = b["add_path"] if b else None
        b_addblob = b["add_blob"] if b else None
        renamed_b = bool(b and b.get("renames"))
        row = dict(path=rel, head_blob=head_blob,
                   a_commit=a_commit, a_path=a_path, a_ncommits=a_n,
                   b_commit=b_commit, b_path=b_path, b_add_blob=b_addblob,
                   b_renames=(b.get("renames") if b else None),
                   b_nblobchanges=len(b["blobs"]) if b else None,
                   b_orphan=bool(b and (b.get("orphan_rename")
                                        or b.get("orphan_modify"))),
                   b_copied=(b.get("copied_from") if b else None))
        # ---- does the CURRENT path resolve at the ADD commit? ---------------
        # this is the exact read that produced the empty md5
        probe_commit = b_commit or a_commit
        if probe_commit:
            rcp, _, _ = git(repo, "rev-parse", f"{probe_commit}:{rel}")
            row["current_path_resolves_at_add"] = (rcp == 0)
        else:
            row["current_path_resolves_at_add"] = None
        row["exposed"] = (b_path is not None and b_path != rel) or renamed_b
        row["blob_changed"] = (b_addblob is not None and head_blob is not None
                               and b_addblob != head_blob)
        # ---- agreement ------------------------------------------------------
        if a_commit is None or b_commit is None:
            row["agree"] = "INCOMPLETE"
        elif a_commit == b_commit and a_path == b_path:
            row["agree"] = "AGREE"
        elif a_commit == b_commit:
            row["agree"] = "DISAGREE-PATH"
        else:
            row["agree"] = "DISAGREE-COMMIT"
        rows.append(row)
    return rows


def blob_delta_report(repo, rel, add_blob, head_blob):
    """What moved between the add blob and HEAD, in rule-2 terms."""
    _, a, _ = git(repo, "cat-file", "blob", add_blob)
    _, h, _ = git(repo, "cat-file", "blob", head_blob)
    al, hl = a.splitlines(), h.splitlines()
    appended_only = len(hl) >= len(al) and hl[:len(al)] == al
    ag, hg = gate_lines(a), gate_lines(h)
    moved = [g for g in ag if g not in hg]
    added = [g for g in hg if g not in ag]
    return dict(add_lines=len(al), head_lines=len(hl),
                appended_only=appended_only,
                gate_lines_add=len(ag), gate_lines_head=len(hg),
                gate_lines_lost=moved, gate_lines_new=added)


# ---------------------------------------------------------------------------
# RULE 3 -- planted control
# ---------------------------------------------------------------------------
def selftest():
    import tempfile, shutil
    ok = True
    tmp = tempfile.mkdtemp(prefix="freeze_audit_selftest_")

    def check(label, got, want):
        nonlocal ok
        if got != want:
            print(f"  PLANT FAIL: {label}: expected {want!r}, got {got!r}")
            ok = False
        else:
            print(f"  {label:52s} -> {want!r}  SEEN")

    try:
        repo = os.path.join(tmp, "r")
        os.makedirs(os.path.join(repo, "old_home"))
        os.makedirs(os.path.join(repo, "verification", "campaign"))
        subprocess.run(["git", "init", "-q", repo], check=True)
        subprocess.run(["git", "-C", repo, "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", repo, "config", "user.name", "t"], check=True)

        def commit(msg):
            # throwaway repository in a tempdir -- NOT the shared worktree
            subprocess.run(["git", "-C", repo, "add", "-A"], check=True)
            subprocess.run(["git", "-C", repo, "commit", "-q", "-m", msg], check=True)

        body = ("# PREREG\n" + "gate: q < 0.05\n" + "cap: 400 core-minutes\n"
                + "label: GATE REACHED if met\n" + "filler\n" * 40)
        # PLANT 1 -- renamed, blob NEVER changed.  Must read exposed, unchanged.
        open(os.path.join(repo, "old_home", "MOVED_PREREGISTRATION.md"),
             "w").write(body)
        # PLANT 2 -- never renamed, blob never changed
        open(os.path.join(repo, "verification", "campaign",
                          "STAY_PREREGISTRATION.md"), "w").write(body)
        # PLANT 3 -- never renamed, blob CHANGED by a lawful append
        open(os.path.join(repo, "verification", "campaign",
                          "APPEND_PREREGISTRATION.md"), "w").write(body)
        # PLANT 4 -- never renamed, blob CHANGED inside the frozen body
        open(os.path.join(repo, "verification", "campaign",
                          "EDIT_PREREGISTRATION.md"), "w").write(body)
        commit("births")
        birth = git(repo, "rev-parse", "HEAD")[1]

        subprocess.run(["git", "-C", repo, "mv",
                        "old_home/MOVED_PREREGISTRATION.md",
                        "verification/campaign/MOVED_PREREGISTRATION.md"],
                       check=True)
        commit("MOVE_MAP batch")
        with open(os.path.join(repo, "verification", "campaign",
                               "APPEND_PREREGISTRATION.md"), "a") as f:
            f.write("\n## ADDENDUM 2026-09-01\nno gate is altered\n")
        p4 = os.path.join(repo, "verification", "campaign",
                          "EDIT_PREREGISTRATION.md")
        # read FULLY before opening for write -- open(p,"w") truncates, and
        # doing both in one expression silently audits an empty file
        p4_old = open(p4).read()
        open(p4, "w").write(p4_old.replace("gate: q < 0.05", "gate: q < 0.20"))
        commit("addendum and an in-body edit")

        alive, events, n = replay(repo)
        targets = sorted(
            os.path.join("verification", "campaign", f)
            for f in os.listdir(os.path.join(repo, "verification", "campaign")))
        rows = {r["path"]: r for r in audit(repo, targets, alive)}

        moved = rows["verification/campaign/MOVED_PREREGISTRATION.md"]
        stay = rows["verification/campaign/STAY_PREREGISTRATION.md"]
        app = rows["verification/campaign/APPEND_PREREGISTRATION.md"]
        edit = rows["verification/campaign/EDIT_PREREGISTRATION.md"]

        check("PLANT 1 renamed file is EXPOSED", moved["exposed"], True)
        check("PLANT 1 add path is the OLD path", moved["b_path"],
              "old_home/MOVED_PREREGISTRATION.md")
        check("PLANT 1 add commit is the birth", moved["b_commit"], birth)
        check("PLANT 1 blob unchanged across the move",
              moved["blob_changed"], False)
        check("PLANT 1 current path does NOT resolve at add",
              moved["current_path_resolves_at_add"], False)
        check("PLANT 1 both mechanisms agree", moved["agree"], "AGREE")
        check("PLANT 2 un-renamed file is NOT exposed", stay["exposed"], False)
        check("PLANT 2 current path DOES resolve at add",
              stay["current_path_resolves_at_add"], True)
        check("PLANT 2 both mechanisms agree", stay["agree"], "AGREE")
        check("PLANT 3 appended blob reads CHANGED", app["blob_changed"], True)
        check("PLANT 4 edited blob reads CHANGED", edit["blob_changed"], True)

        d3 = blob_delta_report(repo, app["path"], app["b_add_blob"],
                               app["head_blob"])
        d4 = blob_delta_report(repo, edit["path"], edit["b_add_blob"],
                               edit["head_blob"])
        check("PLANT 3 append classified append-only",
              d3["appended_only"], True)
        check("PLANT 3 append loses no gate line",
              d3["gate_lines_lost"], [])
        check("PLANT 4 in-body edit NOT append-only",
              d4["appended_only"], False)
        check("PLANT 4 in-body edit loses a gate line",
              d4["gate_lines_lost"], ["gate: q < 0.05"])

        # ---- the FALSE-COMFORT construction, proved here ------------------
        # the naive freeze read on the renamed file: both sides empty, EQUAL
        rc1, l, _ = git(repo, "show",
                        f"{birth}:verification/campaign/MOVED_PREREGISTRATION.md")
        rc2, r2, _ = git(repo, "show",
                         f"{birth}:verification/campaign/NEVER_EXISTED.md")
        check("naive read of a renamed file at freeze is EMPTY", l, "")
        check("naive read of a file that never existed is EMPTY", r2, "")
        check("two empty reads compare EQUAL (edge b, constructed)",
              l == r2, True)

        # ---- ADVERSARIAL CONTROL: the detector must be able to FAIL --------
        # a rename the detector is BLINDED to must not read clean.  Rename
        # detection is turned fully off; PLANT 1 must then stop reading AGREE.
        alive_blind, _, _ = replay(repo, detect_renames=False)
        blind = audit(repo, [moved["path"]], alive_blind)[0]
        if blind["b_path"] == "old_home/MOVED_PREREGISTRATION.md":
            print("  PLANT FAIL: blinded control is NOT adverse -- the "
                  "detector saw the rename with rename detection disabled")
            ok = False
        else:
            print(f"  {'ADVERSARIAL blinded replay loses the rename':52s} "
                  f"-> {blind['b_path']!r}  SEEN")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return ok


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--dir", default="verification/campaign")
    ap.add_argument("--pattern", default="prereg")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--count-only", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        print("PLANTED CONTROL -- rule 3: a reader not shown able to see a "
              "non-zero is not evidence")
        if not selftest():
            refuse("planted control failed -- this detector REFUSES rather "
                   "than report a clean sweep")
        print("PLANTED CONTROL: all plants seen")
        sys.exit(EXIT_OK)

    repo = os.path.abspath(a.repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        refuse(f"{repo} is not a git repository")

    pat = re.compile(a.pattern, re.I)
    base = os.path.join(repo, a.dir)
    if not os.path.isdir(base):
        refuse(f"{a.dir} is not a directory")
    targets = sorted(os.path.join(a.dir, f) for f in os.listdir(base)
                     if pat.search(f) and os.path.isfile(os.path.join(base, f)))
    if not targets:
        print(f"ZERO VERDICT: NOT_A_MEASUREMENT -- no file under {a.dir} "
              f"matched /{a.pattern}/i")
        sys.exit(EXIT_OK)

    alive, events, n_commits = replay(repo)
    rows = audit(repo, targets, alive)

    print("FREEZE PATH-DRIFT AUDIT -- CLAUDE.md rule 2 (freeze) and rule 6 "
          "(frozen files are never edited)")
    print(f"population: {len(targets)} file(s) under {a.dir}/ matching "
          f"/{a.pattern}/i;  replay walked {n_commits} commits")
    print(f"empty-read md5 (the false signal): {EMPTY_MD5}")
    print("=" * 100)

    exposed = [r for r in rows if r["exposed"]]
    changed = [r for r in rows if r["blob_changed"]]
    disagree = [r for r in rows if r["agree"].startswith("DISAGREE")
                or r["agree"] == "INCOMPLETE"]
    unresolvable = [r for r in rows if r["current_path_resolves_at_add"] is False]

    print(f"\nEXPOSED -- add path differs from current path ({len(exposed)}):")
    for r in sorted(exposed, key=lambda x: x["path"]):
        print(f"  {os.path.basename(r['path'])}")
        print(f"      added at   {r['b_path']}  ({(r['b_commit'] or '')[:8]})")
        print(f"      now at     {r['path']}")
        print(f"      add blob   {(r['b_add_blob'] or '-')[:40]}")
        print(f"      HEAD blob  {(r['head_blob'] or '-')[:40]}   "
              f"blob_changed={r['blob_changed']}")
        print(f"      current path resolves at add commit: "
              f"{r['current_path_resolves_at_add']}   mechanisms: {r['agree']}")
        for (sha, iso, old, new) in (r["b_renames"] or []):
            print(f"      rename {sha[:8]} {iso[:10]}  {old} -> {new}")

    print(f"\nBLOB CHANGED after the add commit ({len(changed)}):")
    for r in sorted(changed, key=lambda x: x["path"]):
        d = blob_delta_report(repo, r["path"], r["b_add_blob"], r["head_blob"])
        verdict = ("APPEND-ONLY (consistent with a lawful dated addendum)"
                   if d["appended_only"] and not d["gate_lines_lost"]
                   else "BODY EDIT (gate/threshold/cap/label lines moved)"
                   if d["gate_lines_lost"]
                   else "BODY EDIT (frozen body rewritten, no gate line lost)")
        print(f"  {os.path.basename(r['path'])}  "
              f"{d['add_lines']} -> {d['head_lines']} lines, "
              f"{r['b_nblobchanges']} post-add blob change(s)")
        print(f"      {verdict}")
        for g in d["gate_lines_lost"][:6]:
            print(f"      LOST  {g[:110]}")
        for g in d["gate_lines_new"][:6]:
            print(f"      NEW   {g[:110]}")

    print(f"\nMECHANISM DISAGREEMENT ({len(disagree)}) -- A=git log --follow, "
          f"B=whole-history forward replay:")
    for r in sorted(disagree, key=lambda x: x["path"]):
        print(f"  {r['agree']:16s} {os.path.basename(r['path'])}")
        print(f"      A: {(r['a_commit'] or '-')[:8]}  {r['a_path']}")
        print(f"      B: {(r['b_commit'] or '-')[:8]}  {r['b_path']}")

    print("-" * 100)
    print(f"  {len(rows)} audited | {len(exposed)} exposed (add path != current) "
          f"| {len(unresolvable)} whose current path does NOT resolve at their "
          f"add commit | {len(changed)} blob-changed | {len(disagree)} "
          f"mechanism disagreements")
    if not exposed and not changed:
        print("ZERO VERDICT: ZERO_IS_A_MEASUREMENT -- the same detector saw "
              "every planted rename and planted edit under --selftest")
    print("CANNOT SEE: whether a rename git scored below threshold happened at "
          "all; a file added on a merge commit only; whether an append that "
          "moves no gate line is dated and lawful in substance -- a human "
          "reads the addendum.")
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
