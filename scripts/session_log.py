#!/usr/bin/env python3
"""Session-start telemetry for the team harness.

Every session start, and every attempt to form teams, appends ONE json object to

    /home/ubuntu/harness-state/sessions/YYYY-MM.jsonl

so that when formation breaks -- or quietly does not happen -- there is a record
to read afterwards instead of a memory to argue about. The log lives outside the
repository on purpose: it is high-churn operational data that every concurrent
session writes, and committing it would collide constantly. It lives under
/home/ubuntu/harness-state/ rather than a scratchpad because scratchpads get
wiped (L-186) and this must outlive the session that wrote it.

  session_log.py hook          # hook entry: read the SessionStart payload on
                               # stdin, append a record, print the session banner
  session_log.py event NAME [--detail TEXT] [--ok|--fail]
                               # record a formation attempt/result from a skill
  session_log.py show [-n N]   # print the last N records, human-readable
  session_log.py show --json [-n N]

NOTHING here may break a session start. Every path is wrapped: on any failure the
banner still prints and the exit code is still 0. A telemetry bug that stops the
lab from opening would be worse than the blindness it fixes.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGDIR = "/home/ubuntu/harness-state/sessions"
BANNER = "TEAMS NOT FORMED — run /form-teams"


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def logpath():
    return os.path.join(LOGDIR, datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m") + ".jsonl")


def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=REPO)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as exc:
        return -1, "", str(exc)


def append(rec):
    try:
        os.makedirs(LOGDIR, exist_ok=True)
        with open(logpath(), "a") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False


# --------------------------------------------------------------------------
# probes -- each returns a small dict and NEVER raises
# --------------------------------------------------------------------------

def probe_git():
    out = {}
    rc, sha, _ = run(["git", "rev-parse", "HEAD"])
    out["head"] = sha[:12] if rc == 0 else None
    rc, sub, _ = run(["git", "log", "-1", "--format=%s"])
    out["head_subject"] = sub[:120] if rc == 0 else None
    rc, staged, _ = run(["git", "diff", "--cached", "--name-only"])
    out["staged_count"] = len(staged.splitlines()) if rc == 0 else None
    rc, dels, _ = run(["git", "diff", "--cached", "--name-status",
                       "--diff-filter=D"])
    out["staged_deletions"] = len(dels.splitlines()) if rc == 0 else None
    return out


def probe_agents():
    d = os.path.join(REPO, ".claude", "agents")
    try:
        names = sorted(f[:-3] for f in os.listdir(d) if f.endswith(".md"))
    except Exception:
        names = []
    return {"agent_files": names, "agent_file_count": len(names)}


def probe_board():
    """Per-team freshness stamps, read from HEAD -- not the worktree.

    The shared-board rule (chief, 2026-08-22) is that no team writes the worktree
    copy of docs/LAB_STATE.md: every board commit rebuilds from
    `git show $H:docs/LAB_STATE.md` and stages its own section by cacheinfo. The
    worktree copy is therefore nobody's output and drifts behind HEAD by design, so
    logging it would record a file no team maintains. `board_source` says which was
    read, because a record that does not name its source cannot be audited later.
    """
    import re
    out = {"sections": {}}
    rc, text, _ = run(["git", "show", "HEAD:docs/LAB_STATE.md"], timeout=15)
    if rc == 0 and text:
        out["board_source"] = "HEAD"
        out["board_present"] = True
    else:
        p = os.path.join(REPO, "docs", "LAB_STATE.md")
        out["board_source"] = "worktree (HEAD unavailable)"
        out["board_present"] = os.path.exists(p)
        if not out["board_present"]:
            return out
        try:
            text = open(p).read()
        except Exception as exc:
            out["board_error"] = str(exc)
            return out
    try:
        out["board_lines"] = len(text.splitlines())
        parts = re.split(r"^## (.+)$", text, flags=re.M)
        # Tolerant of any trailing prose after `by <who>` -- see
        # scripts/check_harness.py --selftest for the cases this must accept.
        stamp_re = re.compile(
            r"^\*\*Section last written:\*\*[ \t]*(?P<when>\S+?)"
            r"(?:[ \t]+by[ \t]+(?P<who>.*))?[ \t]*$", re.M)
        for i in range(1, len(parts), 2):
            head, body = parts[i].strip(), parts[i + 1]
            if head.startswith("CHIEF"):
                continue
            m = stamp_re.search(body)
            out["sections"][head] = {
                "stamp": m.group("when").rstrip(".") if m else None,
                "by": (m.group("who") or "").strip().rstrip(".").strip() if m else None,
            }
    except Exception as exc:
        out["board_error"] = str(exc)
    return out


def probe_harness():
    rc, so, _ = run([sys.executable, os.path.join(REPO, "scripts",
                                                  "check_harness.py")], timeout=45)
    return {
        "check_harness_exit": rc,
        "check_harness_fails": so.count("\n  FAIL "),
        "check_harness_warns": so.count("\n  WARN "),
        "check_harness_stale": [l.split()[1] for l in so.splitlines()
                                if l.startswith("  WARN") and "STALE" in l],
    }


def probe_solvers():
    """Scan /proc directly. `ps -o comm` truncates at 15 chars, so
    'buoyantBoussinesqSimpleFoam' arrives as 'buoyantBoussine' and matching on
    it silently reports ZERO solvers while twelve are running -- which is exactly
    the class of blind instrument this lab refuses (a reader not shown able to
    see a non-zero). Measured: the first version of this probe did that."""
    jobs = []
    try:
        pids = [d for d in os.listdir("/proc") if d.isdigit()]
    except Exception:
        return {"solvers": [], "solver_count": 0, "solver_probe_error": "no /proc"}
    for pid in pids:
        try:
            with open("/proc/%s/cmdline" % pid, "rb") as fh:
                argv = fh.read().split(b"\0")
            if not argv or not argv[0]:
                continue
            exe = os.path.basename(argv[0].decode("utf-8", "replace"))
            low = exe.lower()
            if not (low.endswith("foam") or low.startswith("dafoam")):
                continue
            try:
                cwd = os.readlink("/proc/%s/cwd" % pid)
            except Exception:
                cwd = None
            with open("/proc/%s/stat" % pid) as fh:
                utime = int(fh.read().split()[13])
            jobs.append({"pid": int(pid), "bin": exe, "cwd": cwd,
                         "cpu_seconds": utime // os.sysconf("SC_CLK_TCK")})
        except Exception:
            continue
    jobs.sort(key=lambda j: j["pid"])
    return {"solvers": jobs, "solver_count": len(jobs)}


# --------------------------------------------------------------------------

def cmd_hook(args):
    """SessionStart entry point. Prints the banner; logging is best-effort."""
    source = "unknown"
    sid = None
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read()
            if raw.strip():
                payload = json.loads(raw)
                source = payload.get("source") or payload.get("hook_event_name") or "unknown"
                sid = payload.get("session_id")
    except Exception:
        pass

    rec = {"ts": now(), "event": "session_start", "source": source,
           "session_id": sid, "cwd": REPO}
    for probe in (probe_git, probe_agents, probe_board, probe_harness, probe_solvers):
        try:
            rec.update(probe())
        except Exception as exc:
            rec.setdefault("probe_errors", []).append("%s: %s" % (probe.__name__, exc))
    written = append(rec)

    # ---- the banner the session actually sees ----
    board = os.path.join(REPO, "docs", "LAB_STATE.md")
    try:
        with open(board) as fh:
            for i, line in enumerate(fh):
                if i >= 40:
                    break
                sys.stdout.write(line)
    except Exception:
        print("docs/LAB_STATE.md NOT FOUND — the handoff channel is missing.")

    print()
    stale = rec.get("check_harness_stale") or []
    fails = rec.get("check_harness_fails")
    bits = ["agents on disk: %d" % rec.get("agent_file_count", 0),
            "solvers live: %d" % rec.get("solver_count", 0)]
    if fails:
        bits.append("harness FAILS: %d" % fails)
    if stale:
        bits.append("stale sections: %s" % ",".join(stale))
    if rec.get("staged_deletions"):
        bits.append("index staged deletions: %d" % rec["staged_deletions"])
    print("[harness] %s" % " | ".join(bits))
    print("[harness] session log: %s%s" % (logpath(), "" if written else " (WRITE FAILED)"))
    print(BANNER)
    return 0


def cmd_event(args):
    rec = {"ts": now(), "event": args.name, "detail": args.detail,
           "ok": (None if args.ok is None else bool(args.ok))}
    rec.update(probe_git())
    rec.update(probe_agents())
    ok = append(rec)
    print("recorded %s -> %s%s" % (args.name, logpath(), "" if ok else " (WRITE FAILED)"))
    return 0


def cmd_show(args):
    try:
        files = sorted(os.listdir(LOGDIR))
    except Exception:
        print("no session log yet at %s" % LOGDIR)
        return 0
    # ONLY the month logs. A plain `*.jsonl` glob also swallowed the archived
    # `2026-08.selftest.jsonl` and replayed build-time test records as live session
    # traffic -- which is the log lying about the thing it exists to witness.
    import re as _re
    month = _re.compile(r"^\d{4}-\d{2}\.jsonl$")
    lines = []
    for f in files:
        if month.match(f):
            with open(os.path.join(LOGDIR, f)) as fh:
                lines += fh.readlines()
    lines = lines[-args.n:]
    if args.json:
        for l in lines:
            sys.stdout.write(l)
        return 0
    if not lines:
        print("session log is empty")
        return 0
    for l in lines:
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("event") == "session_start":
            secs = r.get("sections") or {}
            unowned = [k for k, v in secs.items()
                       if v.get("by") and "FIRST FILL" in str(v.get("by"))]
            print("%s  START  src=%-8s head=%-12s agents=%d solvers=%d "
                  "harness_exit=%s stale=%s unowned=%s"
                  % (r["ts"], r.get("source"), r.get("head"),
                     r.get("agent_file_count", 0), r.get("solver_count", 0),
                     r.get("check_harness_exit"),
                     ",".join(r.get("check_harness_stale") or []) or "-",
                     ",".join(unowned) or "-"))
        else:
            flag = {True: "OK", False: "FAIL", None: "--"}[r.get("ok")]
            print("%s  %-6s %-4s head=%-12s %s"
                  % (r["ts"], r.get("event", "?").upper()[:6], flag,
                     r.get("head"), (r.get("detail") or "")[:90]))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("hook")
    e = sub.add_parser("event")
    e.add_argument("name")
    e.add_argument("--detail", default="")
    e.add_argument("--ok", dest="ok", action="store_const", const=True, default=None)
    e.add_argument("--fail", dest="ok", action="store_const", const=False)
    s = sub.add_parser("show")
    s.add_argument("-n", type=int, default=20)
    s.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        if args.cmd == "hook":
            return cmd_hook(args)
        if args.cmd == "event":
            return cmd_event(args)
        if args.cmd == "show":
            return cmd_show(args)
        ap.print_help()
        return 0
    except Exception as exc:                      # never break a session start
        if args.cmd == "hook":
            print(BANNER)
            print("[harness] telemetry failed: %s" % exc)
            return 0
        raise


if __name__ == "__main__":
    sys.exit(main())
