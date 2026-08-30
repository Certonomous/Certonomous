#!/usr/bin/env python3
"""VR6 -- the UNTRACKED LAUNCH RECORD.

Frozen gate: verification/campaign/VR6_PREREGISTRATION.md.

WHAT IS AT RISK
---------------
A queue record's `_launch` block (pid, sid, utc, status_file, started_epoch) is
the artifact proving that a FROZEN PRE-REGISTRATION WAS ACTUALLY EXECUTED --
VERIFICATION_CHARTER section 9's evidence record.  A `_launch` block that
exists only as an untracked file on one box's working tree is evidence with no
committed trace: it is one `rm` from gone, it is invisible to anybody reading
the repository at HEAD, and no later audit can reconstruct it.  This item
measures how much of that evidence is in that state.

THE ONLY INDEX-IMMUNE COMPARISON, AND WHY NOTHING ELSE IS USED
---------------------------------------------------------------
`git status`, `git diff`, `git diff HEAD` and `git ls-files` all consult the
SHARED INDEX.  On this box the shared index currently stages hundreds of
differences of which the great majority are BYTE-IDENTICAL to HEAD on disk
(verification, 2026-08-30: 431 staged differences, 394 deletions and 37
modifications, 372 byte-identical to HEAD).  All four of those instruments
therefore MISREPORT here, and they misreport STABLY -- rerunning them does not
help.  This file uses exactly two git reads and no others:

    git rev-parse HEAD:<repo-relative-path>   -> the blob at HEAD, or rc!=0
    git hash-object <path>                    -> the blob of the bytes on disk

Neither touches the index.  Tracked content, where it is needed, is read with
`git show HEAD:<path>` and never `git show :<path>` (the latter is the index).
`_git()` below enforces the read-only subcommand allowlist, so the restriction
is a refusal rather than a convention.

THE CONTROL (standing rule 3)
------------------------------
A zero from a reader not shown able to see a non-zero is not evidence, so the
tracked/untracked reader is required to return BOTH answers IN THE SAME
INVOCATION before any count below is believed: a path proven present at HEAD
must read TRACKED, and a file planted on disk at a path absent from HEAD must
read UNTRACKED.  A third limb plants bytes that are BYTE-IDENTICAL to a
tracked blob at an untracked path and requires UNTRACKED anyway -- a reader
that answered by content rather than by path-at-HEAD would pass the first two
limbs and fail this one.

EXIT CODES
----------
    0   PASS         -- controls behaved; no untracked record carries a
                        `_launch` block, and LAUNCH_LOG.tsv is tracked at HEAD
    1   GATE FAIL    -- execution evidence exists only as untracked files
    2   NOT A RESULT -- a control limb misbehaved
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
QUEUE_ROOT = REPO / "verification" / "queue"
LAUNCH_LOG = QUEUE_ROOT / "LAUNCH_LOG.tsv"

# queue_runner.py:122 -- an archived record is excluded exactly as the runner
# excludes it, so this corpus is the runner's own notion of a CURRENT record.
ARCHIVED_RE = re.compile(r"\.\d{4}-\d{2}-\d{2}T\d{6}Z(\.\d+)?\.json$")

# Read-only, INDEX-FREE git. `status`, `diff`, `ls-files`, `add` and every other
# subcommand are refused here rather than merely avoided by habit.
GIT_ALLOW = {"rev-parse", "hash-object", "show"}


def _git(args, want_bytes=False):
    if args[0] not in GIT_ALLOW:
        raise RuntimeError("VR6 refuses git subcommand %r: only %s are index-free "
                           "reads" % (args[0], sorted(GIT_ALLOW)))
    p = subprocess.run(["git"] + args, cwd=str(REPO),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        return None
    return p.stdout if want_bytes else p.stdout.decode().strip()


# --------------------------------------------------------------------------
# THE READER -- the single door.  Live scan and every control limb enter here.
# --------------------------------------------------------------------------
def classify(path):
    """TRACKED_IDENTICAL / TRACKED_DIFFERS / UNTRACKED for one path on disk.

    The question asked is `does this PATH resolve to a blob at HEAD` -- never
    `do these BYTES exist somewhere in history`, which is the misreading limb
    P3 below is planted to catch."""
    try:
        rel = Path(path).resolve().relative_to(REPO).as_posix()
    except ValueError:
        return "UNTRACKED", None, None      # outside the repo: not at HEAD
    head = _git(["rev-parse", "HEAD:" + rel])
    disk = _git(["hash-object", str(path)])
    if head is None:
        return "UNTRACKED", None, disk
    return ("TRACKED_IDENTICAL" if head == disk else "TRACKED_DIFFERS"), head, disk


def read_corpus(queue_root):
    """Every CURRENT queue record under `queue_root`, from disk, with the two
    facts this item gates on: which team owns it and whether it carries a
    `_launch` block."""
    out = []
    for p in sorted(queue_root.rglob("*.json")):
        if ARCHIVED_RE.search(p.name):
            continue
        try:
            d = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        rel = p.relative_to(queue_root).parts
        team = rel[0] if len(rel) > 1 else "(root)"
        state = "launched" if "launched" in rel else ("held" if "held" in rel else "queued")
        out.append(dict(path=p, team=team, state=state,
                        case_id=d.get("case_id"),
                        launched=isinstance(d.get("_launch"), dict),
                        utc=(d.get("_launch") or {}).get("utc")))
    return out


# --------------------------------------------------------------------------
# CONTROLS
# --------------------------------------------------------------------------
def controls():
    """Four limbs.  The reader must return BOTH answers in this one invocation."""
    ok = True
    tmp = None
    try:
        # P1 (+, TRACKED): a path proven to resolve to a blob at HEAD.
        known = "scripts/queue_runner.py"
        blob = _git(["rev-parse", "HEAD:" + known])
        if not blob:
            print("  CONTROL P1 FAIL: %s does not resolve at HEAD, so the TRACKED "
                  "limb has no anchor" % known)
            return False
        s1, h1, _ = classify(REPO / known)
        if s1.startswith("TRACKED") and h1 == blob:
            print("  control P1 +: %s -> %s, HEAD blob %s  (reader CAN see a "
                  "non-zero)" % (known, s1, blob[:12]))
        else:
            print("  CONTROL P1 FAIL: known-tracked path read as %s" % s1)
            ok = False

        # P2 (-, UNTRACKED): a file planted at a path absent from HEAD.
        tmp = Path(tempfile.mkdtemp(dir=str(REPO / "verification" / "credibility"),
                                    prefix=".vr6_control_"))
        p2 = tmp / "planted_absent.json"
        p2.write_text(json.dumps(dict(case_id="VR6_PLANT", cwd="/planted")) + "\n")
        if _git(["rev-parse", "HEAD:" + p2.resolve().relative_to(REPO).as_posix()]):
            print("  CONTROL P2 FAIL: the planted path unexpectedly EXISTS at HEAD")
            ok = False
        s2, h2, _ = classify(p2)
        if s2 == "UNTRACKED" and h2 is None:
            print("  control P2 -: freshly planted path -> UNTRACKED  (reader CAN "
                  "see a zero)")
        else:
            print("  CONTROL P2 FAIL: planted-absent path read as %s" % s2)
            ok = False

        # P3 (-, CONTENT-BLIND): bytes byte-identical to a TRACKED blob, planted
        # at an UNTRACKED path.  A reader answering by content passes P1 and P2
        # and fails here.
        content = _git(["show", "HEAD:" + known], want_bytes=True)
        p3 = tmp / "planted_identical_bytes.py"
        p3.write_bytes(content)
        s3, _, d3 = classify(p3)
        if s3 == "UNTRACKED" and d3 == blob:
            print("  control P3 -: bytes IDENTICAL to the tracked blob %s planted at "
                  "an untracked path -> UNTRACKED  (reader keys on PATH-at-HEAD, not "
                  "on content)" % blob[:12])
        else:
            print("  CONTROL P3 FAIL: content-identical plant read as %s (disk blob "
                  "%s vs HEAD blob %s)" % (s3, (d3 or "")[:12], blob[:12]))
            ok = False

        # P4: the `_launch` detector must separate a launch-bearing record from a
        # never-run draft, read back from disk through the real corpus reader.
        q = tmp / "q" / "planted" / "launched"
        q.mkdir(parents=True)
        (q / "WITH.json").write_text(json.dumps(dict(
            case_id="WITH", cwd="/p",
            _launch=dict(utc="2026-01-01T00:00:00Z", pid=1, sid=1,
                         status_file="/p/STATUS.WITH", started_epoch=0.0))) + "\n")
        (q / "WITHOUT.json").write_text(json.dumps(dict(case_id="WITHOUT", cwd="/p")) + "\n")
        got = read_corpus(tmp / "q")
        flag = {e["case_id"]: e["launched"] for e in got}
        if flag == {"WITH": True, "WITHOUT": False}:
            print("  control P4 +/-: planted records -> WITH=_launch present, "
                  "WITHOUT=absent  (both answers from the real corpus reader)")
        else:
            print("  CONTROL P4 FAIL: _launch detector gave %r" % flag)
            ok = False
        return ok
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)


def main():
    print("VR6 -- untracked launch record "
          "(frozen: verification/campaign/VR6_PREREGISTRATION.md)")
    print("  repo=%s" % REPO)
    print("  INSTRUMENTS: `git rev-parse HEAD:<path>` vs `git hash-object <path>` "
          "ONLY. No status, no diff, no ls-files -- the shared index misreports "
          "on this box and does so stably.")

    print("CONTROLS (rule 3 -- the reader must return BOTH answers in this "
          "invocation):")
    if not controls():
        print("VERDICT: NOT A RESULT -- a control limb misbehaved")
        return 2

    entries = read_corpus(QUEUE_ROOT)
    for e in entries:
        e["git"], e["head"], e["disk"] = classify(e["path"])

    teams = sorted({e["team"] for e in entries})
    print("QUEUE RECORDS, per team (on disk / tracked at HEAD / untracked / "
          "untracked AND carrying a _launch block):")
    print("    %-22s %6s %8s %10s %12s" % ("team", "disk", "tracked", "untracked", "untr+_launch"))
    tot = [0, 0, 0, 0]
    risk = []
    for tm in teams:
        es = [e for e in entries if e["team"] == tm]
        tr = [e for e in es if e["git"].startswith("TRACKED")]
        un = [e for e in es if e["git"] == "UNTRACKED"]
        ul = [e for e in un if e["launched"]]
        risk += ul
        tot = [tot[0] + len(es), tot[1] + len(tr), tot[2] + len(un), tot[3] + len(ul)]
        print("    %-22s %6d %8d %10d %12d" % (tm, len(es), len(tr), len(un), len(ul)))
    print("    %-22s %6d %8d %10d %12d" % ("TOTAL", *tot))

    diff = [e for e in entries if e["git"] == "TRACKED_DIFFERS"]
    print("    tracked at HEAD but DIFFERING on disk: %d  (reported, NEVER GATED -- "
          "an uncommitted edit is somebody's unfinished work, not a defect)" % len(diff))

    st = [e for e in entries if e["git"] == "UNTRACKED" and not e["launched"]]
    print("    untracked WITHOUT a _launch block: %d  (never-run drafts; these are "
          "queue depth, not lost evidence)" % len(st))

    lg, lg_head, _ = classify(LAUNCH_LOG)
    rows = 0
    if LAUNCH_LOG.exists():
        rows = sum(1 for ln in LAUNCH_LOG.read_text().splitlines() if ln.strip())
    print("LAUNCH LOG %s: %s, %d launch rows"
          % (LAUNCH_LOG.relative_to(REPO), lg, rows))

    if risk:
        print("EVERY UNTRACKED _launch BLOCK -- execution evidence with no committed trace:")
        for e in sorted(risk, key=lambda e: (e["team"], str(e["path"]))):
            print("    %-22s %-34s %s  %s"
                  % (e["team"], e["case_id"] or "(no case_id)",
                     e["utc"] or "(no utc)", e["path"].relative_to(REPO)))

    bad_log = lg == "UNTRACKED"
    if risk or bad_log:
        print("VERDICT: GATE FAIL -- %d _launch block(s) proving a frozen "
              "pre-registration was executed exist ONLY as untracked files%s. This is "
              "a FINDING ABOUT THE EVIDENCE RECORD, not a failure of the runs "
              "themselves: no verdict is withdrawn by this item, and the remedy is to "
              "COMMIT the records, never to delete them. The staged deletions of the "
              "pre-launch copies are RENAMES the index recorded as deletions -- they "
              "are NOT fossils and must not be committed as deletions."
              % (len(risk),
                 ", and LAUNCH_LOG.tsv (%d rows) is itself untracked at HEAD" % rows
                 if bad_log else ""))
        return 1
    print("VERDICT: PASS -- every _launch block on disk is tracked at HEAD and "
          "LAUNCH_LOG.tsv is tracked (%d rows)" % rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
