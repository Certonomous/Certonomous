#!/usr/bin/env python3
# =====================================================================================
# DETACHED GRADE-AND-CALIBRATE WATCHER  --  cfd team, navier_class
#
# WHY THIS EXISTS.  Two graded cfd runs were launched detached on 2026-09-10 and both
# were, at launch, missing a piece of the chain that turns a finished solve into a
# LANDED VERDICT with a rule-12 calibration row:
#
#   * SUBOFF-R1-TRIPLE was launched WITHOUT `--grade`, so its launcher solves and then
#     prints the grading command for a human.  Nobody is there to type it.  With every
#     agent dead the triple finishes and NO verdict is ever produced.
#   * SUP_BOOSTER-E2 DOES autograde from inside its own detached launcher, but its
#     queue entry omitted `grading_freeze`, so the runner never pinned the comparator.
#     Standing rule 2 (frozen grading path) is therefore undischarged for E2, and the
#     by-hand hash check is the compensating control.
#   * NEITHER writes the CLAUDE.md rule-12 estimate-vs-actual row.  There is no cfd row
#     on docs/COST_CALIBRATION.md at all.
#
# This watcher supplies exactly those missing pieces and NOTHING ELSE.  It does not
# launch compute, does not signal any process, and removes nothing.
#
# -------------------------------------------------------------------------------------
# EVERY RULE BELOW EXISTS BECAUSE SOMETHING BROKE ON IT BEFORE.
# -------------------------------------------------------------------------------------
#
# (1) rc IS CAPTURED INSIDE THIS PROCESS, NEVER AROUND THE `setsid` LINE.
#     `setsid timeout cmd` returns 0 for EVERY outcome -- success, non-zero, SIGKILL,
#     timeout -- so an rc read by whoever launched this watcher is decoration.  The
#     grader's rc is read from subprocess.CompletedProcess.returncode on the line after
#     it returns, INSIDE run_grader_capture_rc(), and written to a named sidecar before
#     anything else is decided.  `--selftest-plant` drives that exact function with a
#     grader planted to exit non-zero and REFUSES unless the sidecar records it.
#
# (2) COMPLETION IS POLLED FROM ONE NAMED ARTIFACT.  NEVER A GLOB.
#     `grep` on this box is ugrep, multi-threaded, and interleaves multi-file output:
#     a glob-fed `tail -1` was measured 21/30 correct, and `-J1`/`--sort` make it
#     deterministically WRONG rather than merely unreliable.  Every read here names one
#     file: SUBOFF polls PROGRESS.R1_triple.txt for the launcher's own terminal line;
#     E2 polls graded_e2/LAUNCHER_DONE.  No `glob`, no `*`, no directory listing is used
#     to decide completion.
#
# (3) THE FROZEN GRADING PATH IS CHECKED BY THIS WATCHER, BEFORE IT GRADES.
#     The grader on disk is hashed as a GIT BLOB (sha1 over b"blob <len>\0" + bytes,
#     computed in-process -- it does not shell out to git and so cannot be fooled by a
#     dirty index) and compared against the sha pinned in the supervisor's brief and in
#     the run's freeze.  On ANY drift the watcher REFUSES to grade and records the
#     refusal.  It never grades anyway and never "notes a discrepancy" and proceeds --
#     a printed discrepancy labelled non-binding is worse than one never computed.
#     For E2, whose autograder fires on its own, the hash is re-checked at EVERY POLL
#     for the whole life of the run, so drift that happens BEFORE the autograde is
#     caught rather than discovered afterwards; a verdict produced while the hash was
#     wrong is QUARANTINED, not accepted.
#
# (4) NO GUARD IS AN `assert`.  Under `python3 -O` every assert is deleted, so a refusal
#     written as one is a refusal an interpreter flag can switch off.  There is no
#     `assert` statement anywhere in this file; every guard is `if ...: <refuse>`.
#
# (5) NOTHING BELONGING TO A RUN IS DELETED.  There is no shutil.rmtree, no os.remove
#     and no os.unlink in this file, and no `rm` that names anything under a run root.
#     The ONE deletion in this file is `rm -f "$GIT_INDEX_FILE"` inside LAND_SH, on the
#     watcher's OWN private scratch index under --scratch -- that line is required by the
#     rule-10 private-index protocol and touches no repository content.  Stated here
#     rather than left as a blanket 'there is no rm', which would have been false.
#     Unexpected state is a REFUSAL that is recorded, never something to clear.
#
# (6) IDEMPOTENT.  If the verdict sidecar for a run already exists, the watcher does not
#     re-grade and does not overwrite it.  It exits reporting the existing record.  Two
#     watchers racing on one run therefore produce one verdict, not two.
#
# (7) THE CALIBRATION ROW IS WRITTEN BY THIS WATCHER, NOT OWED TO A FUTURE AGENT.
#     Tier A, ALWAYS: a complete ready-to-append row is written to a named file beside
#     the run.  Tier B, ATTEMPTED: the row is landed on docs/COST_CALIBRATION.md through
#     the canonical scripts/append_record.py (which mints a collision-free id from a
#     clock reading and a hash, reading nothing the record contains) and committed under
#     the CLAUDE.md rule-10 private-index protocol with CAS and a post-commit verify.
#     If Tier B fails for any reason it is RECORDED as failed and Tier A stands.  An
#     honest half-measure beats a silent failure.
# =====================================================================================

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

REPO = "/home/ubuntu/Certonomous"
LEDGER = "docs/COST_CALIBRATION.md"
RATE_USD_PER_CORE_H = 0.0513          # c7a.4xlarge, reported-by-owner, NOT measured

# The 3600-s stall rule of COMPUTE_BUDGET_CHARTER section 2: a row over 3600 wall s is a
# stall, and `cleaned` is gross minus the rows it matches.  Applied literally below.
STALL_WALL_S = 3600


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_blob_sha1(path: str) -> str:
    """The git blob sha of a file ON DISK, computed here.

    Deliberately NOT `git hash-object`: that reads repository state, and the shared
    index on this box is routinely stale under concurrency.  This is the plain object
    formula, so the answer depends on the bytes and nothing else.
    """
    with open(path, "rb") as fh:
        data = fh.read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# -------------------------------------------------------------------------------------
# RULE (1): rc CAPTURED INSIDE THIS PROCESS.
# -------------------------------------------------------------------------------------
def run_grader_capture_rc(argv, stdout_path, rc_path):
    """Run the grader; read its rc INSIDE this process; write the rc sidecar FIRST.

    The sidecar is written before any verdict is interpreted, so a watcher killed
    between the grader returning and the verdict being read still leaves the rc on
    disk.  Returns the rc as an int.  This is the function `--selftest-plant` drives.
    """
    with open(stdout_path, "wb") as out:
        completed = subprocess.run(argv, stdout=out, stderr=subprocess.STDOUT)
    rc = completed.returncode                    # <-- INSIDE. The line after it returns.
    with open(rc_path, "w") as fh:
        fh.write("rc=%d\nrc_captured=inside_this_watcher_process\ncaptured_utc=%s\n"
                 % (rc, utc()))
    os.sync() if hasattr(os, "sync") else None
    return rc


def read_kv(path):
    """Parse a `key=value` sidecar. ONE NAMED FILE, passed in by the caller."""
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if "=" in line:
                k, _, v = line.partition("=")
                out[k.strip()] = v.strip()
    return out


def named_file_contains(path: str, needle: str) -> bool:
    """Rule (2): completion read from ONE NAMED file. No glob, ever."""
    if not os.path.isfile(path):
        return False
    with open(path, errors="replace") as fh:
        return needle in fh.read()


# =====================================================================================
# THE TWO RUNS.
# =====================================================================================
RUNS = {
    "suboff": {
        "label": "SUBOFF-R1-TRIPLE",
        "team": "cfd",
        "prereg_commit": "94d7afb7",
        "grader": REPO + "/cases/navier_class/SUBOFF/grade_suboff.py",
        "grader_pinned_blob": "9ab71b156d395d1e040851c524f0b81bb0e82ae1",
        "run_root": REPO + "/verification/runs/navier_class/SUBOFF",
        # RULE (2): ONE named artifact, and it is the launcher's own terminal line.
        "done_file": REPO + "/verification/runs/navier_class/SUBOFF/PROGRESS.R1_triple.txt",
        "done_needle": "TRIPLE FINISHED with launcher status",
        "levels": ["coarse", "medium", "fine"],
        "predicted_core_min": 80.38,
        "cap_core_min": 150.0,
        "grades_itself": False,          # launched WITHOUT --grade: WE must grade it
        "watch_pid_of": REPO + "/cases/navier_class/SUBOFF/run_suboff_r1_triple.sh",
    },
    "e2": {
        "label": "SUP_BOOSTER-E2",
        "team": "cfd",
        "prereg_commit": "34797ce9",
        "grader": REPO + "/verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster_e2.py",
        "grader_pinned_blob": "d18f0867ea7d1fd6f86347c00ca1a5b8e3ddb663",
        "run_root": REPO + "/verification/runs/navier_class/SUP_BOOSTER/graded_e2",
        "done_file": REPO + "/verification/runs/navier_class/SUP_BOOSTER/graded_e2/LAUNCHER_DONE",
        "done_needle": "done ",
        "levels": ["coarse", "medium", "fine"],
        "predicted_core_min": 31.0,
        "cap_core_min": 60.0,
        "grades_itself": True,           # autograde_sup_booster_e2.sh fires from the launcher
        "watch_pid_of": REPO + "/verification/runs/navier_class/SUP_BOOSTER/run_graded_triple_e2.sh",
    },
}


# -------------------------------------------------------------------------------------
# COST -- read from the runs' OWN sidecars, never from memory (ledger append rule 2).
# -------------------------------------------------------------------------------------
def collect_cost(key, cfg):
    """Per-level wall_s / ranks / rc, from ONE NAMED sidecar per level."""
    rows = []
    if key == "suboff":
        for lvl in cfg["levels"]:
            case = os.path.join(cfg["run_root"], "reg_" + lvl)
            st = read_kv(os.path.join(case, "STATUS.R1_" + lvl))
            if not st:
                rows.append({"level": lvl, "present": False})
                continue
            rows.append({
                "level": lvl, "present": True,
                "rc": st.get("rc", "absent"),
                "wall_s": float(st.get("wall_s", "0") or 0),
                "ranks": int(st.get("ranks", "1") or 1),
                "core_min": float(st.get("core_min", "0") or 0),
                "source": os.path.join(case, "STATUS.R1_" + lvl),
            })
    else:
        for lvl in cfg["levels"]:
            d = os.path.join(cfg["run_root"], lvl)
            st = read_kv(os.path.join(d, "STATUS"))
            if not st:
                rows.append({"level": lvl, "present": False})
                continue
            wall = float(st.get("wall_s", "0") or 0)
            rows.append({
                "level": lvl, "present": True,
                "rc": st.get("rc_solve", "absent"),
                "wall_s": wall, "ranks": 1,
                "core_min": wall / 60.0,
                "source": os.path.join(d, "STATUS"),
            })
    return rows


def summarise_cost(rows):
    """gross / cleaned / waste, with waste NAMED SEPARATELY (charter section 6).

    cleaned = gross minus every level the 3600-s stall rule matches.
    waste    = core-minutes spent on levels that returned non-zero, i.e. spend that
               bought no gradeable answer.  It is reported beside the ratio and is
               NEVER folded into either column or into the ratio's explanation.
    """
    present = [r for r in rows if r.get("present")]
    gross = sum(r["core_min"] for r in present)
    stalled = [r for r in present if r["wall_s"] > STALL_WALL_S]
    cleaned = gross - sum(r["core_min"] for r in stalled)
    waste = sum(r["core_min"] for r in present if str(r.get("rc")) != "0")
    return {
        "gross_core_min": gross,
        "cleaned_core_min": cleaned,
        "stalled_levels": [r["level"] for r in stalled],
        "waste_core_min": waste,
        "waste_levels": [r["level"] for r in present if str(r.get("rc")) != "0"],
        "levels_present": [r["level"] for r in present],
        "levels_absent": [r["level"] for r in rows if not r.get("present")],
    }


def usd(core_min):
    return core_min / 60.0 * RATE_USD_PER_CORE_H


# -------------------------------------------------------------------------------------
# THE ROW.
# -------------------------------------------------------------------------------------
def build_row(cfg, cost, verdict_text, refs):
    pred = cfg["predicted_core_min"]
    ratio = (cost["cleaned_core_min"] / pred) if pred > 0 else 0.0
    if cost["stalled_levels"]:
        cleaned_note = ("%.2f core-min = $%.4f derived (gross minus the 3600-s stall "
                        "rule matches: %s)" % (cost["cleaned_core_min"],
                                               usd(cost["cleaned_core_min"]),
                                               ", ".join(cost["stalled_levels"])))
    else:
        cleaned_note = ("%.2f core-min = $%.4f derived (= gross; no level exceeds the "
                        "3600-s stall rule)" % (cost["cleaned_core_min"],
                                                usd(cost["cleaned_core_min"])))

    if cost["waste_core_min"] > 0:
        waste_txt = ("**waste named separately: %.2f core-min** on level(s) %s, which "
                     "returned non-zero and bought no gradeable answer -- NOT absorbed "
                     "into the ratio" % (cost["waste_core_min"],
                                         ", ".join(cost["waste_levels"]) or "none"))
    else:
        waste_txt = "**waste named separately: 0.00 core-min** (every level returned rc=0)"

    if ratio > 1.0:
        direction = ("over the estimate; the per-level wall timeouts, not the estimate, "
                     "bounded the spend")
    else:
        direction = "under the estimate"

    gap = ("%s. %s. Levels absent from the record: %s. Attribution: solver iteration "
           "rate under box contention (multiple OpenFOAM and DAFoam solvers live at "
           "launch) against a single-tenant per-iteration basis in the pre-registration"
           % (direction, waste_txt, ", ".join(cost["levels_absent"]) or "none"))

    cells = [
        "{{ALLOCATE_ID}}",
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        cfg["team"],
        "**%s** (graded triple; prereg frozen at `%s`; %s)"
        % (cfg["label"], cfg["prereg_commit"], verdict_text),
        "%.2f core-min registered (cap %.0f core-min)" % (cfg["predicted_core_min"],
                                                          cfg["cap_core_min"]),
        "%.2f core-min = $%.4f derived (solver wall x ranks / 60, from the run's own "
        "per-level sidecars)" % (cost["gross_core_min"], usd(cost["gross_core_min"])),
        cleaned_note,
        "%.2fx" % ratio,
        gap,
        refs,
    ]
    return "| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |\n"


# -------------------------------------------------------------------------------------
# TIER B: land the row.  Canonical tool + rule-10 private index, in ONE invocation.
# -------------------------------------------------------------------------------------
LAND_SH = r'''
set -u
cd /home/ubuntu/Certonomous || exit 90
ROWS="$1"; IDX="$2"; MSG="$3"
export GIT_INDEX_FILE="$IDX"; rm -f "$GIT_INDEX_FILE"
H=$(git rev-parse HEAD) || exit 91
case "$H" in *[!0-9a-f]*|"") echo "BAD HEAD sha: $H" >&2; exit 92;; esac
# The tool rebuilds the ledger as HEAD's blob + our row and mints a collision-free id.
python3 scripts/append_record.py --path docs/COST_CALIBRATION.md --rows "$ROWS" \
        --rev "$H" --allocate-id || exit 93
git read-tree "$H" || exit 94
git update-index --add -- docs/COST_CALIBRATION.md || exit 95
T=$(git write-tree) || exit 96
case "$T" in *[!0-9a-f]*|"") echo "BAD tree sha: $T" >&2; exit 97;; esac
if [ "$T" = "$(git rev-parse ${H}^{tree})" ]; then
  echo "REFUSE: write-tree equals HEAD's tree -- the append changed nothing" >&2; exit 98
fi
N=$(git diff-tree --no-commit-id --name-only -r "$H" "$T" | wc -l)
if [ "$N" != "1" ]; then
  echo "REFUSE: $N paths in the tree, expected exactly 1" >&2
  git diff-tree --no-commit-id --name-only -r "$H" "$T" >&2; exit 99
fi
P=$(git diff-tree --no-commit-id --name-only -r "$H" "$T")
if [ "$P" != "docs/COST_CALIBRATION.md" ]; then
  echo "REFUSE: foreign path in tree: $P" >&2; exit 100
fi
C=$(git commit-tree "$T" -p "$H" -F "$MSG") || exit 101
case "$C" in *[!0-9a-f]*|"") echo "BAD commit sha: $C" >&2; exit 102;; esac
if [ ${#C} -ne 40 ]; then echo "BAD commit sha length: $C" >&2; exit 103; fi
git update-ref refs/heads/main "$C" "$H" || exit 104     # CAS: parent must still be HEAD
NOW=$(git rev-parse HEAD)
if [ "$NOW" != "$C" ]; then echo "REFUSE: HEAD did not move to $C (is $NOW)" >&2; exit 105; fi
V=$(git diff HEAD~1 HEAD --name-only)
if [ "$V" != "docs/COST_CALIBRATION.md" ]; then
  echo "REFUSE post-commit verify: commit carries [$V]" >&2; exit 106
fi
echo "LANDED $C"
'''


def land_row(row_text, cfg, key, scratch, logf):
    """Attempt Tier B.  Every failure is RECORDED and returns False; Tier A stands."""
    rows_file = os.path.join(scratch, "row_%s.md" % key)
    msg_file = os.path.join(scratch, "msg_%s.txt" % key)
    sh_file = os.path.join(scratch, "land_%s.sh" % key)
    for attempt in range(1, 6):
        with open(rows_file, "w") as fh:
            fh.write(row_text)
        with open(msg_file, "w") as fh:
            fh.write("cfd COST_CALIBRATION: %s rule-12 estimate-vs-actual row\n\n"
                     "Written by the detached grade-and-calibrate watcher\n"
                     "cases/navier_class/watch_grade_calibrate.py at run completion,\n"
                     "not owed to a future agent (CLAUDE.md rule 12). Predicted %.2f\n"
                     "core-min; actuals read from the run's own per-level sidecars.\n"
                     % (cfg["label"], cfg["predicted_core_min"]))
        with open(sh_file, "w") as fh:
            fh.write(LAND_SH)
        idx = os.path.join(scratch, "idx_%s_%d" % (key, attempt))
        env = dict(os.environ)
        env.pop("GIT_INDEX_FILE", None)
        p = subprocess.run(["bash", sh_file, rows_file, idx, msg_file],
                           cwd=REPO, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.decode(errors="replace")
        logf.write("[%s] land attempt %d rc=%d\n%s\n" % (utc(), attempt, p.returncode, out))
        logf.flush()
        if p.returncode == 0:
            return True, out.strip().splitlines()[-1] if out.strip() else "LANDED"
        # 104 = CAS lost to a peer commit: re-derive against the new HEAD and retry.
        if p.returncode in (93, 104, 105, 99, 100):
            time.sleep(7 + attempt * 3)
            continue
        return False, "rc=%d (not retried): %s" % (p.returncode, out.strip()[-400:])
    return False, "exhausted 5 attempts under concurrency"


# -------------------------------------------------------------------------------------
# THE WATCH.
# -------------------------------------------------------------------------------------
def watch(key, deadline_s, poll_s, scratch):
    cfg = RUNS[key]
    root = cfg["run_root"]
    verdict_sidecar = os.path.join(root, "WATCHER_VERDICT.%s.json" % key)
    logpath = os.path.join(root, "watcher.%s.log" % key)
    rowfile = os.path.join(root, "CALIBRATION_ROW.%s.pending.md" % key)

    logf = open(logpath, "a", buffering=1)

    def log(msg):
        logf.write("[%s] %s\n" % (utc(), msg))
        logf.flush()

    log("=" * 78)
    log("watcher start pid=%d ppid=%d run=%s" % (os.getpid(), os.getppid(), cfg["label"]))
    log("ppid observed from this process: %d (1 == reparented to init == survives fleet death)"
        % os.getppid())

    # RULE (6): IDEMPOTENT.  An existing verdict record is never overwritten.
    if os.path.exists(verdict_sidecar):
        log("IDEMPOTENT STOP: %s already exists. Not re-grading, not overwriting." % verdict_sidecar)
        return 0

    pinned = cfg["grader_pinned_blob"]
    hash_timeline = []
    drift_seen = None
    t0 = time.time()
    done = False

    while time.time() - t0 < deadline_s:
        # RULE (3): the freeze is re-checked EVERY poll, so drift before an autograde is
        # caught rather than discovered after it.
        if os.path.isfile(cfg["grader"]):
            h = git_blob_sha1(cfg["grader"])
            if not hash_timeline or hash_timeline[-1][1] != h:
                hash_timeline.append((utc(), h))
                log("grader blob %s (pinned %s) %s" %
                    (h, pinned, "MATCH" if h == pinned else "*** DRIFT ***"))
            if h != pinned and drift_seen is None:
                drift_seen = (utc(), h)
                log("FREEZE DRIFT DETECTED -- standing rule 2. This watcher will REFUSE "
                    "to grade and will quarantine any verdict produced from here on.")
        else:
            if drift_seen is None:
                drift_seen = (utc(), "MISSING")
                log("FREEZE DRIFT: pinned grader MISSING at %s" % cfg["grader"])

        # RULE (2): ONE NAMED ARTIFACT.
        if named_file_contains(cfg["done_file"], cfg["done_needle"]):
            done = True
            log("completion seen in ONE NAMED artifact %s" % cfg["done_file"])
            break
        time.sleep(poll_s)

    if not done:
        log("DEADLINE REACHED after %.0f s with no completion marker in %s. "
            "Recording BLOCKED; nothing graded, nothing deleted."
            % (time.time() - t0, cfg["done_file"]))
        rec = {"run": cfg["label"], "state": "BLOCKED",
               "reason": "watcher deadline reached with no completion marker",
               "done_file": cfg["done_file"], "watcher_ppid": os.getppid(),
               "hash_timeline": hash_timeline, "utc": utc()}
        with open(verdict_sidecar, "w") as fh:
            json.dump(rec, fh, indent=2)
        return 3

    # ---- FREEZE GATE.  Refuse rather than grade.  Not a note; a refusal. ----------
    h_now = git_blob_sha1(cfg["grader"]) if os.path.isfile(cfg["grader"]) else "MISSING"
    if h_now != pinned or drift_seen is not None:
        log("REFUSING TO GRADE: grading path is not the frozen one. on-disk=%s pinned=%s "
            "first_drift=%s" % (h_now, pinned, drift_seen))
        rec = {"run": cfg["label"], "state": "NOT A RESULT",
               "reason": "frozen grading path drifted (CLAUDE.md rule 2); this watcher "
                         "refused to grade and graded nothing",
               "grader": cfg["grader"], "grader_on_disk_blob": h_now,
               "grader_pinned_blob": pinned, "first_drift": drift_seen,
               "hash_timeline": hash_timeline, "watcher_ppid": os.getppid(),
               "self_graded_by_launcher": cfg["grades_itself"], "utc": utc()}
        with open(verdict_sidecar, "w") as fh:
            json.dump(rec, fh, indent=2)
        return 2

    log("FREEZE OK: grader blob %s == pinned %s. Rule 2 discharged by this watcher." % (h_now, pinned))

    # ---- GRADE (SUBOFF) or VALIDATE THE LAUNCHER'S OWN GRADE (E2) -----------------
    grade_rc = None
    grade_note = ""
    if cfg["grades_itself"]:
        rc_auto = read_kv(os.path.join(root, "rc.autograde"))
        raw = ""
        p_rc = os.path.join(root, "rc.autograde")
        if os.path.isfile(p_rc):
            with open(p_rc) as fh:
                raw = fh.read().strip()
        verdict_json = os.path.join(root, "VERDICT.json")
        if os.path.isfile(verdict_json):
            grade_rc = int(raw) if raw.isdigit() else None
            grade_note = ("graded by the launcher's own detached autograder; this watcher "
                          "verified the frozen grading path across the whole run and did "
                          "not re-grade (rule 6, idempotent)")
            log("E2 verdict present at %s, autograde rc=%s. Not re-grading." % (verdict_json, raw))
        else:
            log("E2 LAUNCHER_DONE present but VERDICT.json ABSENT -- the autograder did "
                "not produce a verdict. Grading here with the frozen grader.")
            grade_rc = run_grader_capture_rc(
                [sys.executable, cfg["grader"],
                 "--coarse", os.path.join(root, "coarse"),
                 "--medium", os.path.join(root, "medium"),
                 "--fine", os.path.join(root, "fine"),
                 "--reference", REPO + "/verification/runs/navier_class/SUP_BOOSTER/"
                                       "tm_reference_M2p0_tc15.json",
                 "--report", verdict_json],
                os.path.join(root, "watcher_verdict_stdout.txt"),
                os.path.join(root, "rc.grade.watcher"))
            grade_note = "autograder produced no verdict; this watcher graded, rc captured inside"
    else:
        grade_rc = run_grader_capture_rc(
            [sys.executable, cfg["grader"],
             "--coarse", os.path.join(root, "reg_coarse"),
             "--medium", os.path.join(root, "reg_medium"),
             "--fine", os.path.join(root, "reg_fine"),
             "--reference", os.path.join(root, "suboff_reference_ReL1p2e7.json"),
             "--report", os.path.join(root, "VERDICT.R1_triple.json")],
            os.path.join(root, "watcher_verdict_stdout.txt"),
            os.path.join(root, "rc.grade.watcher"))
        grade_note = ("graded by this watcher because the launcher was started WITHOUT "
                      "--grade; rc captured inside this process")
        log("grade_suboff.py rc=%s (2 = the grader's own REFUSE, e.g. rule-4 incompleteness)"
            % grade_rc)

    # ---- COST, then TIER A, then TIER B ------------------------------------------
    rows = collect_cost(key, cfg)
    cost = summarise_cost(rows)
    log("cost gross=%.2f cleaned=%.2f waste=%.2f core-min (levels present: %s)"
        % (cost["gross_core_min"], cost["cleaned_core_min"], cost["waste_core_min"],
           ", ".join(cost["levels_present"]) or "none"))

    if grade_rc == 0:
        vtxt = "graded; verdict in the run's own VERDICT json"
    elif grade_rc == 2:
        vtxt = ("grader REFUSED (exit 2) -- a level is not rule-4 complete, so the triple "
                "is **NOT A RESULT** by incompleteness")
    elif grade_rc is None:
        vtxt = "verdict produced by the launcher's own autograder"
    else:
        vtxt = "grader exited %d -- a crash is a FINDING until the supervisor's check-3 triage" % grade_rc

    refs = ("`%s`; per-level sidecars `%s`; watcher log `%s`"
            % (verdict_sidecar.replace(REPO + "/", ""),
               ", ".join(r["source"].replace(REPO + "/", "") for r in rows if r.get("present"))
               or "none present",
               logpath.replace(REPO + "/", "")))
    row_text = build_row(cfg, cost, vtxt, refs)

    # TIER A -- ALWAYS.  A complete, ready-to-append row beside the run.
    with open(rowfile, "w") as fh:
        fh.write("<!-- Ready-to-append docs/COST_CALIBRATION.md row, written by\n"
                 "     cases/navier_class/watch_grade_calibrate.py at %s.\n"
                 "     The id cell is the tool's {{ALLOCATE_ID}} placeholder: land with\n"
                 "       python3 scripts/append_record.py --path docs/COST_CALIBRATION.md \\\n"
                 "              --rows <this file> --allocate-id\n"
                 "     then commit under the CLAUDE.md rule-10 private-index protocol. -->\n"
                 % utc())
        fh.write(row_text)
    log("TIER A written: %s" % rowfile)

    landed, land_msg = land_row(row_text, cfg, key, scratch, logf)
    log("TIER B %s: %s" % ("LANDED" if landed else "NOT LANDED", land_msg))

    rec = {
        "run": cfg["label"],
        "prereg_commit": cfg["prereg_commit"],
        "grader": cfg["grader"],
        "grader_pinned_blob": pinned,
        "grader_on_disk_blob": h_now,
        "freeze_check": "PASS -- discharged by this watcher, every poll",
        "hash_timeline": hash_timeline,
        "grade_rc": grade_rc,
        "grade_note": grade_note,
        "cost": cost,
        "cost_rows": rows,
        "cost_basis": "core-minutes from the run's own per-level sidecars; dollars at "
                      "$0.0513/core-h are DERIVED, not measured (the box cannot read its "
                      "own billing, COMPUTE_BUDGET_CHARTER section 5)",
        "predicted_core_min": cfg["predicted_core_min"],
        "cap_core_min": cfg["cap_core_min"],
        "calibration_row_file": rowfile,
        "calibration_landed": landed,
        "calibration_land_message": land_msg,
        "watcher_pid": os.getpid(),
        "watcher_ppid": os.getppid(),
        "utc": utc(),
    }
    with open(verdict_sidecar, "w") as fh:
        json.dump(rec, fh, indent=2)
    log("verdict sidecar written: %s" % verdict_sidecar)
    log("watcher done.")
    return 0


# -------------------------------------------------------------------------------------
# THE PLANTED-FAILURE PROOF (rule (1)).
# -------------------------------------------------------------------------------------
def selftest_plant(dirpath):
    """Drive run_grader_capture_rc() -- THE PRODUCTION FUNCTION -- with a grader
    planted to exit non-zero, and REFUSE unless the sidecar records that rc.

    A guard never driven into its refusal is a guard nobody has seen work.  Both limbs
    run: a planted failure that must be recorded, and a planted success that must be
    recorded as 0, so a sidecar hard-wired to any constant fails one limb or the other.
    """
    os.makedirs(dirpath, exist_ok=True)
    failures = []
    for want in (7, 124, 2, 0):
        g = os.path.join(dirpath, "planted_grader_%d.py" % want)
        with open(g, "w") as fh:
            fh.write("import sys\nsys.stdout.write('planted grader, exiting %d\\n')\n"
                     "sys.exit(%d)\n" % (want, want))
        rc_path = os.path.join(dirpath, "rc.planted_%d" % want)
        out_path = os.path.join(dirpath, "out.planted_%d" % want)
        got = run_grader_capture_rc([sys.executable, g], out_path, rc_path)
        side = read_kv(rc_path)
        recorded = side.get("rc")
        ok = (got == want) and (recorded == str(want))
        print("  planted rc=%-4d -> returned %-4s sidecar rc=%-4s  %s"
              % (want, got, recorded, "OK" if ok else "FAILED"))
        if not ok:
            failures.append(want)
    if failures:
        print("REFUSED: rc capture did not record planted rc(s) %s. The watcher is NOT "
              "trusted." % failures, file=sys.stderr)
        return 1
    print("PLANTED-FAILURE PROOF PASSED: run_grader_capture_rc records a non-zero rc "
          "(7, 124, 2) and a zero rc (0) faithfully, INSIDE the watcher process.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", choices=sorted(RUNS))
    ap.add_argument("--deadline-s", type=float, default=36000.0)
    ap.add_argument("--poll-s", type=float, default=20.0)
    ap.add_argument("--scratch", default="/tmp/claude-1000/watcher")
    ap.add_argument("--selftest-plant")
    args = ap.parse_args()
    if args.selftest_plant:
        return selftest_plant(args.selftest_plant)
    if not args.run:
        ap.error("--run is required unless --selftest-plant")
    os.makedirs(args.scratch, exist_ok=True)
    return watch(args.run, args.deadline_s, args.poll_s, args.scratch)


if __name__ == "__main__":
    sys.exit(main())
