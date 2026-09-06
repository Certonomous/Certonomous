#!/usr/bin/env python3
"""Completion monitor for Ling (2016) TBNN GPU **arm 2**. Blocker B4.

THIS IS A MONITOR. IT IS NOT PART OF THE GRADING PATH.
====================================================================
It grades nothing, scores nothing, and computes no quantity a verdict could
rest on. It is **not** on the frozen grading-path sha table
(`arm2/PREREGISTRATION.md` §9, which fixes `train_gpu_ling_v2.py`,
`score_gpu_ling_v2.py`, `run_all_gpu_v2.sh` and `dataset.npz`). Adding this
file therefore requires **no amendment** to the frozen pre-registration --
precisely because it can never touch a verdict:

  * it emits no verdict-vocabulary token as its own state (asserted at import,
    `_assert_states_disjoint_from_verdicts()`, and again in `--selftest`);
  * it reads artefacts and reports which ones exist and what they say; it
    derives no gate quantity, no error, no ratio and no cost;
  * it claims **no cost figure**. It records timestamps only. Idle minutes and
    dollars are derivable afterwards, by subtraction, by a human -- see
    "TIMESTAMPS ARE THE POINT" below. The monitor never does that arithmetic.

If a future edit makes this file compute something a verdict could rest on,
that edit is out of scope for this file and belongs in the frozen comparator
under the amendment rules -- stop and escalate instead.

WHY THIS EXISTS -- THE MEASURED COST OF NOT HAVING IT
====================================================================
Arm 1's GPU node idled **7 h 52 m 47 s = 7.88 GPU-h ~= $6.34 derived** after
its batch completed at 08:03:58Z, because the overnight session limit killed
the whole agent fleet and no agent survived to observe completion
(`gpu/RESULTS.md` D-2; ledger C-16/C-19; L-268; `arm2/LAUNCH_CHECKLIST.md` B4
and its STATUS CORRECTION of 2026-09-06). Arm 2's `--shutdown` closes the tail
only if the driver reaches its shutdown stage; a BLOCKED, refused or crashed
run still writes `out/COMPLETE.json` through the driver's `finally` path, and a
**failed halt** is visible only by reading `out/shutdown_attempt.json` on a node
that is still up.

DESIGN, AND WHY EACH PIECE IS THE WAY IT IS
====================================================================
1. IT RUNS ON THE LAB BOX AND POLLS THE NODE OVER SSH.
   A monitor living on the GPU node dies with the node at the very moment it
   most needs to observe -- the driver's self-shutdown. So the observer is off
   the observed machine.

2. IT SURVIVES THE DEATH OF THE AGENT THAT STARTED IT.
   `--detach` re-execs this script under `setsid`, through a generated POSIX
   wrapper. **`setsid <cmd>` returns 0 for every outcome**, so the real exit
   status is captured INSIDE the wrapper (`rc=$?` on the line after the monitor
   returns, appended to `watch_arm2.rc`) and never around the `setsid` line.
   The parent's success check is likewise NOT the `setsid` return code: the
   parent verifies by reading the pidfile the monitor itself wrote and probing
   that pid with signal 0.

3. IT READS NAMED ARTEFACTS, NEVER A GLOB.
   Every node-side path is a literal entry in `NODE_ARTEFACTS`. A glob has no
   defined "last" member and this box's `grep`/`ls` return members in an order
   that is not the one a reader assumes. `_assert_no_globs()` refuses at import
   if a metacharacter ever appears in that table, and `--selftest` asserts the
   built remote command contains each named path verbatim.

4. FOUR DECISION STATES, NEVER COLLAPSED.
     COMPLETE               -- completion marker present AND parseable.
     FAILED-HALT            -- node reachable AND `out/shutdown_attempt.json`
                               present past the halt grace. The driver tried to
                               power the node off and did not. THE MONEY-BURNING
                               STATE; it is the loudest thing this file emits.
     GONE-AFTER-COMPLETE    -- node unreachable, completion marker observed on
                               an earlier poll. CONSISTENT WITH a successful
                               self-shutdown. Not proof of one.
     GONE-WITHOUT-COMPLETE  -- node unreachable, completion never observed.
                               AMBIGUOUS. An instance can vanish for reasons
                               that are not success (spot reclaim, console stop,
                               network partition, host failure).
   plus one non-decision label:
     IN-PROGRESS            -- node reachable, nothing conclusive yet. This is
                               the "no conclusion" label, not a fifth verdict.

   **NODE ABSENCE IS NOT EVIDENCE OF COMPLETION.** That inference is the trap,
   and it is made structurally unwriteable here:
     (a) `ever_completed` is set in exactly one place, `_observe_completion()`,
         which requires `reachable is True` and a parsed marker object;
     (b) the unreachable branch of `classify()` returns a value looked up in the
         two-entry frozen map `_GONE_BY_EVER_COMPLETED`, whose value set is
         asserted at import not to contain `COMPLETE`;
     (c) `classify()` re-asserts `state != COMPLETE` on every unreachable
         return before handing the value back;
     (d) the status file's `completion_observed` is defined as
         `completion_first_observed_utc is not None` and nothing else, and
         GONE-WITHOUT-COMPLETE carries the explicit field
         `"is_completion": false`.

5. TIMESTAMPS ARE THE POINT.
   Arm 1's $6.34 was measurable only because timestamps existed. The status
   file records, each set once and never moved:
     `first_poll_utc`, `completion_first_observed_utc`,
     `unreachable_first_utc`, `shutdown_attempt_first_seen_utc`,
   plus per-poll `last_poll_utc` and a flap-visible
   `unreachable_current_since_utc` (which resets when the node answers again).
   Idle is then a subtraction anyone can do afterwards. The monitor does not do
   it and quotes no dollars.

6. LOCAL OUTPUTS, OUTSIDE GIT, UNDER THE LAUNCHER'S OWN LOCAL ROOT
   `/home/ubuntu/closure-data/tbnn_gpu/arm2/` (`run_all_gpu_v2.sh:31`):
     `watch_arm2_status.json` -- the handoff; rewritten ATOMICALLY (temp file in
                                 the same directory, fsync, `os.replace`) so a
                                 reader never sees a half-file;
     `watch_arm2_completion.log` -- append-only, one line per poll;
     `watch_arm2.pid` / `watch_arm2_wrapper.pid` / `watch_arm2.rc` /
     `watch_arm2.out` -- detach bookkeeping.
   The scratchpad is not a handoff channel (L-186) and nothing here writes to it.

7. SAFE WITH NO NODE UP -- which is today's state (the GPU is off for AWS
   capacity reasons). An unreachable host yields GONE-WITHOUT-COMPLETE and the
   monitor keeps polling. It does not crash and it does not conclude.

8. `--interval` (default 60 s), `--once` for a single poll.

USAGE
====================================================================
    python3 watch_arm2_completion.py --once
    python3 watch_arm2_completion.py --detach            # prints the pid
    python3 watch_arm2_completion.py --selftest          # hermetic, no ssh
    cat /home/ubuntu/closure-data/tbnn_gpu/arm2/watch_arm2_status.json

Exit codes: 0 normal / selftest all arms pass; 1 selftest arm failed;
2 refusal (bad configuration).
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timedelta, timezone

# --------------------------------------------------------------------------
# Fixed configuration -- node side taken from run_all_gpu_v2.sh and the driver
# --------------------------------------------------------------------------

GPU_HOST = "gpu1"                       # ~/.ssh/config alias (run_all_gpu_v2.sh:27)
REMOTE_DIR = "$HOME/r_ling_gpu/arm2"    # launcher's RDIR '~/r_ling_gpu/arm2' (:28)
LOCAL_ROOT = "/home/ubuntu/closure-data/tbnn_gpu/arm2"   # launcher's LOCAL_ROOT (:31)

STATUS_NAME = "watch_arm2_status.json"
LOG_NAME = "watch_arm2_completion.log"
PID_NAME = "watch_arm2.pid"
WRAPPER_PID_NAME = "watch_arm2_wrapper.pid"
WRAPPER_NAME = "watch_arm2_wrapper.sh"
RC_NAME = "watch_arm2.rc"
DETACH_OUT_NAME = "watch_arm2.out"

# NAMED artefacts. Never a glob (rule: a glob has no defined last member).
# Paths are relative to REMOTE_DIR. `out/` is the driver's --out directory, so
# spend.json and the status files live under it (train_gpu_ling_v2.py:234, :212);
# driver.log is written by the launcher's nohup redirect at RDIR level (:63).
# `spend.json` is ALSO named at RDIR level because the checklist/brief names it
# there; both are explicit names, neither is a wildcard.
NODE_ARTEFACTS = (
    "out/COMPLETE.json",
    "out/shutdown_attempt.json",
    "out/status_p0.json",
    "out/spend.json",
    "spend.json",
    "driver.log",
)
COMPLETE_KEY = "out/COMPLETE.json"
SHUTDOWN_ATTEMPT_KEY = "out/shutdown_attempt.json"
STATUS_P0_KEY = "out/status_p0.json"

# driver.log is a growing text file; only its tail is fetched. It is context for
# a human, never an input to any decision this file makes.
TAIL_ONLY = {"driver.log"}
TAIL_BYTES = 4000

# --------------------------------------------------------------------------
# States
# --------------------------------------------------------------------------

STATE_COMPLETE = "COMPLETE"
STATE_FAILED_HALT = "FAILED-HALT"
STATE_GONE_AFTER_COMPLETE = "GONE-AFTER-COMPLETE"
STATE_GONE_WITHOUT_COMPLETE = "GONE-WITHOUT-COMPLETE"
STATE_IN_PROGRESS = "IN-PROGRESS"

ALL_STATES = frozenset({
    STATE_COMPLETE, STATE_FAILED_HALT, STATE_GONE_AFTER_COMPLETE,
    STATE_GONE_WITHOUT_COMPLETE, STATE_IN_PROGRESS,
})

# The lab's verdict vocabulary (CLAUDE.md rule 1). This monitor emits NONE of
# these as its own state -- that is what "it grades nothing" means mechanically.
# (It may ECHO the driver's own `final_state`, e.g. "BLOCKED", from inside
# COMPLETE.json; that is the driver's field, quoted, not this file's verdict.)
VERDICT_VOCABULARY = frozenset({
    "PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING",
})

# The ONLY route from "node unreachable" to a state. Its values are asserted
# below never to include COMPLETE: that is what makes
# "node absent implies complete" unwriteable rather than merely un-written.
_GONE_BY_EVER_COMPLETED = {
    True: STATE_GONE_AFTER_COMPLETE,
    False: STATE_GONE_WITHOUT_COMPLETE,
}

# A halt takes a bounded time. `shutdown -h now` on a Linux node completes far
# inside this. Declaring FAILED-HALT the instant the intent file appears would
# raise a false alarm during every normal successful shutdown, because
# COMPLETE.json and shutdown_attempt.json are both written BEFORE the machine
# goes down (train_gpu_ling_v2.py:937-962). The grace DELAYS the alarm by a
# bounded, recorded interval; it never suppresses it, and the observation time
# is recorded from the first sighting regardless. `--halt-grace 0` restores the
# literal "present and reachable => FAILED-HALT" rule.
DEFAULT_HALT_GRACE_S = 300
DEFAULT_INTERVAL_S = 60
DEFAULT_SSH_TIMEOUT_S = 20

BEGIN_MARK = "BEGIN_PROBE"
END_MARK = "END_PROBE"

STATUS_SCHEMA = "watch_arm2_status/1"


def _assert_states_disjoint_from_verdicts():
    overlap = ALL_STATES & VERDICT_VOCABULARY
    if overlap:
        raise AssertionError(
            "monitor state names collide with the lab verdict vocabulary: %r "
            "-- this file grades nothing and must never emit a verdict token"
            % sorted(overlap))


def _assert_absence_cannot_mean_complete():
    if STATE_COMPLETE in set(_GONE_BY_EVER_COMPLETED.values()):
        raise AssertionError(
            "the unreachable branch can reach COMPLETE -- node absence would be "
            "readable as completion. Refusing to load.")
    if set(_GONE_BY_EVER_COMPLETED) != {True, False}:
        raise AssertionError("the unreachable branch is not total over ever_completed")


def _assert_no_globs():
    bad = [p for p in NODE_ARTEFACTS if any(c in p for c in "*?[]")]
    if bad:
        raise AssertionError(
            "NODE_ARTEFACTS contains a glob: %r -- every artefact is NAMED" % bad)


_assert_states_disjoint_from_verdicts()
_assert_absence_cannot_mean_complete()
_assert_no_globs()


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def parse_json_text(text):
    """Parse, never raise. Returns (obj_or_None, error_or_None).

    A torn write is real: the driver writes COMPLETE.json with a plain open()
    (train_gpu_ling_v2.py:937), NOT the tmp+replace it uses for status/spend, so
    a poll can land mid-write. An unparseable marker is NOT completion; it is a
    parse error and the monitor keeps polling.
    """
    if text is None:
        return None, None
    try:
        return json.loads(text), None
    except Exception as exc:
        return None, "%s: %s" % (type(exc).__name__, exc)


# --------------------------------------------------------------------------
# The node probe -- substitutable, so the selftest drives the real code paths
# --------------------------------------------------------------------------

class ProbeResult(object):
    """What one look at the node returned.

    `reachable` is True only if the probe saw BOTH framing markers come back.
    `files` maps each NAMED artefact to its text, or None if absent.
    """

    __slots__ = ("reachable", "files", "error", "hostname", "node_utc",
                 "driver_running", "raw_len")

    def __init__(self, reachable, files=None, error=None, hostname=None,
                 node_utc=None, driver_running=None, raw_len=0):
        self.reachable = bool(reachable)
        self.files = dict(files or {})
        self.error = error
        self.hostname = hostname
        self.node_utc = node_utc
        self.driver_running = driver_running   # True / False / None(unknown)
        self.raw_len = raw_len

    def text(self, key):
        return self.files.get(key)

    def present(self, key):
        return self.files.get(key) is not None


def build_remote_script(remote_dir=REMOTE_DIR, artefacts=NODE_ARTEFACTS,
                        tail_bytes=TAIL_BYTES):
    """The POSIX sh run on the node. Every artefact appears by NAME.

    Framing: BEGIN_PROBE ... END_PROBE. Reachability is decided by the markers,
    not by ssh's exit code -- ssh returns the REMOTE command's status, so a
    remote non-zero and a network failure are otherwise indistinguishable.
    Contents are base64'd so no file byte can forge a framing line.
    """
    lines = [
        "R=%s" % remote_dir,          # unquoted on purpose: the node expands $HOME
        "printf '%s\\n'" % BEGIN_MARK,
        "printf 'HOSTNAME %s\\n' \"$(hostname 2>/dev/null || echo unknown)\"",
        "printf 'NODE_UTC %s\\n' \"$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo unknown)\"",
        ('if [ -f "$R/driver.pid" ] && kill -0 "$(cat "$R/driver.pid" 2>/dev/null)" '
         '2>/dev/null; then printf \'DRIVER running\\n\'; '
         'else printf \'DRIVER not_running\\n\'; fi'),
    ]
    for rel in artefacts:
        q = shlex.quote(rel)
        reader = ('tail -c %d "$R"/%s' % (tail_bytes, q)) if rel in TAIL_ONLY \
            else ('cat "$R"/%s' % q)
        lines.append(
            'if [ -f "$R"/%s ]; then '
            "printf 'FILE %s %%s\\n' \"$(%s | base64 | tr -d '\\n')\"; "
            "else printf 'MISSING %s\\n'; fi" % (q, rel, reader, rel))
    lines.append("printf '%s\\n'" % END_MARK)
    return "\n".join(lines)


def parse_probe_output(stdout, artefacts=NODE_ARTEFACTS):
    """Turn one probe's stdout into a ProbeResult. Never raises."""
    if BEGIN_MARK not in stdout or END_MARK not in stdout:
        return ProbeResult(False, error="probe framing incomplete "
                                        "(BEGIN_PROBE/END_PROBE not both seen)",
                           raw_len=len(stdout))
    files = {k: None for k in artefacts}
    hostname = node_utc = None
    driver_running = None
    for line in stdout.splitlines():
        if line.startswith("HOSTNAME "):
            hostname = line[len("HOSTNAME "):].strip() or None
        elif line.startswith("NODE_UTC "):
            node_utc = line[len("NODE_UTC "):].strip() or None
        elif line.startswith("DRIVER "):
            tok = line[len("DRIVER "):].strip()
            driver_running = True if tok == "running" else (
                False if tok == "not_running" else None)
        elif line.startswith("FILE "):
            rest = line[len("FILE "):]
            name, _, b64 = rest.partition(" ")
            if name in files:
                try:
                    files[name] = base64.b64decode(b64.strip() or "").decode(
                        "utf-8", "replace")
                except Exception:
                    files[name] = None
        elif line.startswith("MISSING "):
            name = line[len("MISSING "):].strip()
            if name in files:
                files[name] = None
    return ProbeResult(True, files=files, hostname=hostname, node_utc=node_utc,
                       driver_running=driver_running, raw_len=len(stdout))


class SshNodeProbe(object):
    """The real probe. One ssh per poll, BatchMode so it can never block on a
    password prompt. Any failure -- refused, timed out, DNS, host down -- is
    reported as UNREACHABLE with the reason recorded, never as an exception and
    never as completion."""

    def __init__(self, host=GPU_HOST, remote_dir=REMOTE_DIR,
                 timeout_s=DEFAULT_SSH_TIMEOUT_S, artefacts=NODE_ARTEFACTS):
        self.host = host
        self.remote_dir = remote_dir
        self.timeout_s = timeout_s
        self.artefacts = tuple(artefacts)

    def command(self):
        return [
            "ssh", "-n",
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ConnectTimeout=%d" % max(5, int(self.timeout_s // 2)),
            "-o", "ServerAliveInterval=5",
            "-o", "ServerAliveCountMax=2",
            self.host, "sh", "-s",
        ]

    def script(self):
        return build_remote_script(self.remote_dir, self.artefacts)

    def __call__(self):
        try:
            proc = subprocess.run(
                self.command(), input=self.script(), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, timeout=self.timeout_s)
        except subprocess.TimeoutExpired:
            return ProbeResult(False, error="ssh timeout after %ss" % self.timeout_s)
        except Exception as exc:
            return ProbeResult(False, error="ssh failed: %s: %s"
                                            % (type(exc).__name__, exc))
        res = parse_probe_output(proc.stdout, self.artefacts)
        if not res.reachable:
            err = (proc.stderr or "").strip().splitlines()
            res.error = "ssh rc=%d; %s; %s" % (
                proc.returncode, res.error or "no framing",
                err[-1] if err else "no stderr")
        return res


# --------------------------------------------------------------------------
# Classification -- the four states, and the guard that keeps them four
# --------------------------------------------------------------------------

def classify(reachable, complete_readable, shutdown_attempt_present,
             ever_completed, halt_pending_s, halt_grace_s):
    """Return exactly one member of ALL_STATES.

    The unreachable branch cannot reach COMPLETE: it indexes a frozen two-entry
    map whose value set is asserted at import to exclude it, and the result is
    re-asserted here. Node absence is therefore not writeable as completion.
    """
    if not reachable:
        state = _GONE_BY_EVER_COMPLETED[bool(ever_completed)]
        if state == STATE_COMPLETE:
            raise AssertionError(
                "node absence was about to be reported as completion -- refusing")
        return state
    if shutdown_attempt_present and halt_pending_s is not None \
            and halt_pending_s >= halt_grace_s:
        return STATE_FAILED_HALT
    if complete_readable:
        return STATE_COMPLETE
    return STATE_IN_PROGRESS


# --------------------------------------------------------------------------
# The monitor
# --------------------------------------------------------------------------

class Monitor(object):
    def __init__(self, probe, local_root=LOCAL_ROOT,
                 halt_grace_s=DEFAULT_HALT_GRACE_S, now_fn=utc_now,
                 status_name=STATUS_NAME, log_name=LOG_NAME):
        self.probe = probe
        self.root = local_root
        self.halt_grace_s = int(halt_grace_s)
        self.now_fn = now_fn
        self.status_path = os.path.join(local_root, status_name)
        self.log_path = os.path.join(local_root, log_name)
        os.makedirs(local_root, exist_ok=True)
        self.state = self._load_prior()
        self.last_tmp_path = None      # inspected by the atomic-write arm

    # ---- persistence -----------------------------------------------------
    def _load_prior(self):
        """Memory across monitor restarts. A restarted monitor must not forget
        that completion was observed, or a later disappearance would downgrade
        from GONE-AFTER-COMPLETE to the ambiguous GONE-WITHOUT-COMPLETE."""
        blank = {
            "schema": STATUS_SCHEMA,
            "first_poll_utc": None,
            "last_poll_utc": None,
            "poll_count": 0,
            "completion_first_observed_utc": None,
            "unreachable_first_utc": None,
            "unreachable_current_since_utc": None,
            "shutdown_attempt_first_seen_utc": None,
            "reachable_last_utc": None,
        }
        try:
            with open(self.status_path) as fh:
                prior = json.load(fh)
        except Exception:
            return blank
        if not isinstance(prior, dict):
            return blank
        for k in blank:
            if k in prior:
                blank[k] = prior[k]
        return blank

    def _write_status_atomic(self, record):
        """Temp file in the SAME directory, fsync, os.replace. A reader never
        sees a half-file, and never sees the temp name under the status name."""
        d = os.path.dirname(self.status_path) or "."
        fd, tmp = tempfile.mkstemp(prefix=".watch_arm2_status.", suffix=".tmp", dir=d)
        self.last_tmp_path = tmp
        try:
            with os.fdopen(fd, "w") as fh:
                json.dump(record, fh, indent=1, sort_keys=False)
                fh.write("\n")
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, self.status_path)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def _append_log(self, record):
        line = "%s %-22s reachable=%s complete_observed=%s driver=%s %s\n" % (
            record["last_poll_utc"], record["state"],
            record["reachable"], record["completion_observed"],
            record["driver_running"],
            json.dumps({k: record[k] for k in
                        ("alerts", "artefacts_present", "probe_error")},
                       sort_keys=True))
        with open(self.log_path, "a") as fh:
            fh.write(line)
            fh.flush()

    # ---- the one place completion is ever observed -----------------------
    def _observe_completion(self, reachable, marker_obj, now):
        """Sets completion memory. Requires a REACHABLE probe and a PARSED
        marker object. There is no other writer of
        `completion_first_observed_utc` in this file."""
        if not reachable or marker_obj is None:
            return False
        if self.state["completion_first_observed_utc"] is None:
            self.state["completion_first_observed_utc"] = fmt(now)
        return True

    # ---- one poll --------------------------------------------------------
    def poll_once(self):
        now = self.now_fn()
        try:
            res = self.probe()
        except Exception as exc:              # a probe must never kill the monitor
            res = ProbeResult(False, error="probe raised %s: %s"
                                           % (type(exc).__name__, exc))
        if not isinstance(res, ProbeResult):
            res = ProbeResult(False, error="probe returned %r, not a ProbeResult"
                                           % type(res).__name__)

        st = self.state
        if st["first_poll_utc"] is None:
            st["first_poll_utc"] = fmt(now)
        st["last_poll_utc"] = fmt(now)
        st["poll_count"] = int(st.get("poll_count") or 0) + 1

        # --- reachability bookkeeping (timestamps are the point) ----------
        if res.reachable:
            st["reachable_last_utc"] = fmt(now)
            st["unreachable_current_since_utc"] = None
        else:
            if st["unreachable_first_utc"] is None:
                st["unreachable_first_utc"] = fmt(now)
            if st["unreachable_current_since_utc"] is None:
                st["unreachable_current_since_utc"] = fmt(now)

        # --- artefacts, each read by NAME ---------------------------------
        marker_text = res.text(COMPLETE_KEY) if res.reachable else None
        marker_obj, marker_err = parse_json_text(marker_text)
        complete_readable = bool(res.reachable and marker_obj is not None)
        self._observe_completion(res.reachable, marker_obj, now)

        p0_obj, p0_err = parse_json_text(
            res.text(STATUS_P0_KEY) if res.reachable else None)
        att_obj, att_err = parse_json_text(
            res.text(SHUTDOWN_ATTEMPT_KEY) if res.reachable else None)
        att_present = bool(res.reachable and res.present(SHUTDOWN_ATTEMPT_KEY))
        spend_obj, _ = parse_json_text(
            (res.text("out/spend.json") or res.text("spend.json"))
            if res.reachable else None)

        if att_present and st["shutdown_attempt_first_seen_utc"] is None:
            st["shutdown_attempt_first_seen_utc"] = fmt(now)
        halt_pending_s = None
        if att_present:
            seen = parse_utc(st["shutdown_attempt_first_seen_utc"])
            halt_pending_s = (now - seen).total_seconds() if seen else 0.0

        ever_completed = st["completion_first_observed_utc"] is not None
        state = classify(res.reachable, complete_readable, att_present,
                         ever_completed, halt_pending_s, self.halt_grace_s)
        if state not in ALL_STATES:
            raise AssertionError("classify returned an unknown state %r" % state)

        # --- alerts: loud, and separate from the state --------------------
        alerts = []
        if state == STATE_FAILED_HALT:
            alerts.append(
                "FAILED-HALT: the node is REACHABLE with out/shutdown_attempt.json "
                "present for %.0fs (grace %ds). The driver tried to power it off "
                "and did not. THE NODE IS BILLING. Report to the supervisor for a "
                "stop request to Sanaa; do not retry blind."
                % (halt_pending_s or 0.0, self.halt_grace_s))
            if isinstance(att_obj, dict) and att_obj.get("allowed") is False:
                alerts.append(
                    "shutdown_attempt.allowed=false: the driver's hostname/CUDA "
                    "guard REFUSED the halt (reason field: %r). The node is up by "
                    "the guard's design, not by a failed shutdown call -- but it "
                    "is still up and still billing."
                    % (att_obj.get("refused") or att_obj.get("reason")))
        if state == STATE_COMPLETE and att_present:
            alerts.append(
                "halt pending: shutdown_attempt.json seen at %s, node still up "
                "%.0fs later; FAILED-HALT fires at %ds."
                % (st["shutdown_attempt_first_seen_utc"], halt_pending_s or 0.0,
                   self.halt_grace_s))
        if state == STATE_GONE_WITHOUT_COMPLETE:
            alerts.append(
                "AMBIGUOUS: the node is unreachable and NO completion marker was "
                "ever observed. This is NOT completion. An instance can vanish "
                "without finishing.")
        if res.reachable and res.driver_running is False and not complete_readable:
            alerts.append(
                "the node is up, no completion marker, and driver.pid is not "
                "alive -- the driver died without reaching its finally path. "
                "The node is billing.")
        if isinstance(marker_obj, dict) and marker_obj.get("final_state"):
            alerts.append("driver final_state (its field, quoted, not a monitor "
                          "verdict): %r" % marker_obj["final_state"])
        if marker_err:
            alerts.append("out/COMPLETE.json present but NOT parseable (%s) -- "
                          "treated as NOT complete; still polling." % marker_err)

        record = {
            "schema": STATUS_SCHEMA,
            "monitor": "watch_arm2_completion.py",
            "monitor_is_a_grader": False,
            "on_frozen_grading_path": False,
            "state": state,
            "state_meanings": {
                STATE_COMPLETE: "completion marker present and parseable",
                STATE_FAILED_HALT: "reachable + shutdown_attempt.json past grace; "
                                   "the node is up and billing",
                STATE_GONE_AFTER_COMPLETE: "unreachable, completion observed "
                                           "earlier; CONSISTENT WITH self-shutdown, "
                                           "not proof of it",
                STATE_GONE_WITHOUT_COMPLETE: "unreachable, completion NEVER "
                                             "observed; AMBIGUOUS, never completion",
                STATE_IN_PROGRESS: "reachable, nothing conclusive yet",
            }[state],
            "is_completion": state == STATE_COMPLETE,
            "reachable": res.reachable,
            "probe_error": res.error,
            "node_hostname": res.hostname,
            "node_utc": res.node_utc,
            "driver_running": res.driver_running,
            "completion_observed": ever_completed,
            "completion_first_observed_utc": st["completion_first_observed_utc"],
            "completion_marker": marker_obj,
            "completion_marker_parse_error": marker_err,
            "shutdown_attempt_present": att_present,
            "shutdown_attempt_first_seen_utc": st["shutdown_attempt_first_seen_utc"],
            "shutdown_attempt": att_obj,
            "shutdown_attempt_parse_error": att_err,
            "halt_pending_seconds": halt_pending_s,
            "halt_grace_seconds": self.halt_grace_s,
            "status_p0": p0_obj,
            "status_p0_parse_error": p0_err,
            "spend": spend_obj,
            "first_poll_utc": st["first_poll_utc"],
            "last_poll_utc": st["last_poll_utc"],
            "poll_count": st["poll_count"],
            "reachable_last_utc": st["reachable_last_utc"],
            "unreachable_first_utc": st["unreachable_first_utc"],
            "unreachable_current_since_utc": st["unreachable_current_since_utc"],
            "artefacts_named": list(NODE_ARTEFACTS),
            "artefacts_present": sorted(
                k for k in NODE_ARTEFACTS if res.present(k)) if res.reachable else [],
            "alerts": alerts,
            "cost_note": ("This monitor claims NO cost figure. It records "
                          "timestamps only; idle intervals are derivable by "
                          "subtraction afterwards (arm 1: 7 h 52 m 47 s = 7.88 "
                          "GPU-h ~= $6.34 derived, gpu/RESULTS.md D-2)."),
            "monitor_pid": os.getpid(),
        }
        self._write_status_atomic(record)
        self._append_log(record)
        return record

    def run(self, interval_s=DEFAULT_INTERVAL_S, max_polls=None,
            sleep_fn=time.sleep):
        self._stop = False

        def _stop(signum, _frame):
            self._stop = True

        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                signal.signal(sig, _stop)
            except (ValueError, OSError):
                pass                    # not the main thread; nothing to install
        n = 0
        while not self._stop:
            rec = self.poll_once()
            n += 1
            print("[watch-arm2] %s %s%s" % (
                rec["last_poll_utc"], rec["state"],
                (" | " + " | ".join(rec["alerts"])) if rec["alerts"] else ""),
                flush=True)
            if max_polls is not None and n >= max_polls:
                break
            # A terminal state does NOT stop the monitor: a node can come back,
            # and GONE-WITHOUT-COMPLETE in particular must keep looking.
            slept = 0.0
            while slept < interval_s and not self._stop:
                step = min(1.0, interval_s - slept)
                sleep_fn(step)
                slept += step
        return 0


# --------------------------------------------------------------------------
# Detach -- rc captured INSIDE the wrapper, never around the setsid line
# --------------------------------------------------------------------------

WRAPPER_TEMPLATE = """#!/bin/sh
# GENERATED by watch_arm2_completion.py --detach. Do not edit; regenerate.
#
# `setsid <cmd>` exits 0 for EVERY outcome of <cmd> (lab lesson: "setsid parent
# returns zero"). The real exit status is therefore captured HERE, INSIDE the
# detached wrapper, on the line after the monitor returns -- never around the
# setsid invocation in the parent.
echo $$ > {wrapper_pid}
{python} {script} {args} >> {outlog} 2>&1
rc=$?
printf '%s rc=%d pid_wrapper=%s\\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$rc" "$$" >> {rcfile}
exit $rc
"""


def detach(argv_rest, local_root=LOCAL_ROOT, python=None, script=None):
    """Re-exec this script detached; return (pid, wrapper_path) or (None, path).

    Success is NOT judged by setsid's return code -- it cannot be. It is judged
    by reading the pidfile the monitor itself writes on startup and probing that
    pid with signal 0.
    """
    os.makedirs(local_root, exist_ok=True)
    python = python or sys.executable or "/usr/bin/python3"
    script = script or os.path.abspath(__file__)
    wrapper = os.path.join(local_root, WRAPPER_NAME)
    pidfile = os.path.join(local_root, PID_NAME)
    body = WRAPPER_TEMPLATE.format(
        wrapper_pid=shlex.quote(os.path.join(local_root, WRAPPER_PID_NAME)),
        python=shlex.quote(python),
        script=shlex.quote(script),
        args=" ".join(shlex.quote(a) for a in argv_rest),
        outlog=shlex.quote(os.path.join(local_root, DETACH_OUT_NAME)),
        rcfile=shlex.quote(os.path.join(local_root, RC_NAME)),
    )
    with open(wrapper, "w") as fh:
        fh.write(body)
    os.chmod(wrapper, 0o755)

    try:
        os.unlink(pidfile)              # so a stale pid cannot be read as this one
    except OSError:
        pass

    subprocess.Popen(
        ["setsid", "/bin/sh", wrapper],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True)
    # Deliberately NOT checking the Popen return code: setsid's 0 means nothing.

    deadline = time.time() + 15.0
    while time.time() < deadline:
        try:
            with open(pidfile) as fh:
                pid = int(fh.read().strip())
            os.kill(pid, 0)             # proves the monitor is alive, not setsid's rc
            return pid, wrapper
        except Exception:
            time.sleep(0.25)
    return None, wrapper


def write_pidfile(local_root=LOCAL_ROOT):
    os.makedirs(local_root, exist_ok=True)
    p = os.path.join(local_root, PID_NAME)
    with open(p, "w") as fh:
        fh.write("%d\n" % os.getpid())
    return p


# ==========================================================================
# SELFTEST -- hermetic. No ssh, no network. The probe is substituted.
# ==========================================================================

PLANT_VALUE = 1.234e-03          # the lab's planted-perturbation constant
PLANT_KEY = "planted_control_value"
PLANT_STATE = "PLANTED-FINAL-STATE-7f3a"


class FakeProbe(object):
    """Substituted node. `reachable` and `files` are set by the arm."""

    def __init__(self, reachable=True, files=None, driver_running=True,
                 hostname="gpu1", raise_exc=None):
        self.reachable = reachable
        self.files = dict(files or {})
        self.driver_running = driver_running
        self.hostname = hostname
        self.raise_exc = raise_exc
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.raise_exc is not None:
            raise self.raise_exc
        if not self.reachable:
            return ProbeResult(False, error="fake: host down")
        files = {k: None for k in NODE_ARTEFACTS}
        files.update(self.files)
        return ProbeResult(True, files=files, hostname=self.hostname,
                           node_utc="2026-09-06T00:00:00Z",
                           driver_running=self.driver_running)


class FakeClock(object):
    def __init__(self, start="2026-09-06T12:00:00Z"):
        self.t = parse_utc(start)

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t = self.t + timedelta(seconds=seconds)
        return self.t


def _complete_json(final_state="DONE", plant=False, extra=None):
    rec = {
        "utc": "2026-09-06T12:00:00Z",
        "final_state": final_state,
        "exit_code": 0,
        "reason": "",
        "spend_total_hours": 10.7054,
        "stages": ["g0", "p0", "arma2_tbnn", "arma2_mlp"],
        "shutdown_requested": True,
    }
    if plant:
        rec[PLANT_KEY] = PLANT_VALUE
        rec["final_state"] = PLANT_STATE
    rec.update(extra or {})
    return json.dumps(rec, indent=1)


def _read_status(root):
    with open(os.path.join(root, STATUS_NAME)) as fh:
        return json.load(fh)


def _selftest(verbose=True):
    import shutil
    arms = []

    def arm(name):
        def deco(fn):
            arms.append((name, fn))
            return fn
        return deco

    # ---------------- 1 ----------------
    @arm("1  POSITIVE: marker present -> COMPLETE, and it is WRITTEN to the status file")
    def a1(root):
        clk = FakeClock()
        m = Monitor(FakeProbe(files={COMPLETE_KEY: _complete_json()}),
                    local_root=root, now_fn=clk)
        rec = m.poll_once()
        assert rec["state"] == STATE_COMPLETE, rec["state"]
        on_disk = _read_status(root)
        assert on_disk["state"] == STATE_COMPLETE, on_disk["state"]
        assert on_disk["completion_observed"] is True
        assert on_disk["completion_first_observed_utc"] == "2026-09-06T12:00:00Z"

    # ---------------- 2 ----------------
    @arm("2  PAIRED (same writer, same file): no marker -> NOT complete, "
         "then the SAME writer is shown able to write COMPLETE")
    def a2(root):
        clk = FakeClock()
        probe = FakeProbe(files={})                      # nothing on the node
        m = Monitor(probe, local_root=root, now_fn=clk)
        rec_a = m.poll_once()
        assert rec_a["state"] != STATE_COMPLETE, rec_a["state"]
        assert rec_a["state"] == STATE_IN_PROGRESS, rec_a["state"]
        assert _read_status(root)["completion_observed"] is False
        assert _read_status(root)["is_completion"] is False
        # SAME monitor object, SAME status path: the marker appears.
        clk.advance(60)
        probe.files[COMPLETE_KEY] = _complete_json()
        rec_b = m.poll_once()
        assert rec_b["state"] == STATE_COMPLETE, rec_b["state"]
        d = _read_status(root)
        assert d["state"] == STATE_COMPLETE
        assert d["completion_observed"] is True
        # the refusal in poll A is evidence precisely because poll B, through the
        # same writer and the same file, did report completion.

    # ---------------- 3 ----------------
    @arm("3  UNREACHABLE + never completed -> GONE-WITHOUT-COMPLETE, asserted NOT COMPLETE")
    def a3(root):
        clk = FakeClock()
        m = Monitor(FakeProbe(reachable=False), local_root=root, now_fn=clk)
        rec = m.poll_once()
        assert rec["state"] == STATE_GONE_WITHOUT_COMPLETE, rec["state"]
        assert rec["state"] != STATE_COMPLETE
        assert rec["is_completion"] is False
        assert rec["completion_observed"] is False
        assert rec["completion_first_observed_utc"] is None
        d = _read_status(root)
        assert d["state"] == STATE_GONE_WITHOUT_COMPLETE
        assert d["is_completion"] is False
        assert d["completion_first_observed_utc"] is None
        assert any("NOT completion" in a for a in d["alerts"])
        assert d["unreachable_first_utc"] == "2026-09-06T12:00:00Z"

    # ---------------- 4 ----------------
    @arm("4  UNREACHABLE + previously completed -> GONE-AFTER-COMPLETE")
    def a4(root):
        clk = FakeClock()
        probe = FakeProbe(files={COMPLETE_KEY: _complete_json()})
        m = Monitor(probe, local_root=root, now_fn=clk)
        assert m.poll_once()["state"] == STATE_COMPLETE
        clk.advance(120)
        probe.reachable = False
        rec = m.poll_once()
        assert rec["state"] == STATE_GONE_AFTER_COMPLETE, rec["state"]
        assert rec["state"] != STATE_COMPLETE
        assert rec["is_completion"] is False          # consistent-with, not proof
        assert rec["completion_first_observed_utc"] == "2026-09-06T12:00:00Z"
        assert rec["unreachable_first_utc"] == "2026-09-06T12:02:00Z"

    # ---------------- 5 ----------------
    @arm("5  REACHABLE + shutdown_attempt.json past grace -> FAILED-HALT, loudest")
    def a5(root):
        clk = FakeClock()
        probe = FakeProbe(files={
            COMPLETE_KEY: _complete_json(),
            SHUTDOWN_ATTEMPT_KEY: json.dumps({"utc": "2026-09-06T12:00:00Z",
                                              "hostname": "gpu1", "cuda": True,
                                              "allowed": True, "rc": None}),
        })
        m = Monitor(probe, local_root=root, halt_grace_s=300, now_fn=clk)
        first = m.poll_once()
        assert first["state"] == STATE_COMPLETE, first["state"]   # inside grace
        clk.advance(301)
        rec = m.poll_once()
        assert rec["state"] == STATE_FAILED_HALT, rec["state"]
        assert rec["halt_pending_seconds"] >= 300
        d = _read_status(root)
        assert d["state"] == STATE_FAILED_HALT
        assert any("FAILED-HALT" in a and "BILLING" in a for a in d["alerts"])
        # and with grace 0 it fires on the first sighting
        root0 = os.path.join(root, "grace0")
        m0 = Monitor(probe, local_root=root0, halt_grace_s=0, now_fn=FakeClock())
        assert m0.poll_once()["state"] == STATE_FAILED_HALT

    # ---------------- 6 ----------------
    @arm("6  HALT GRACE: reachable + attempt inside grace -> COMPLETE with halt "
         "pending recorded (the alarm is delayed, never suppressed)")
    def a6(root):
        clk = FakeClock()
        probe = FakeProbe(files={
            COMPLETE_KEY: _complete_json(),
            SHUTDOWN_ATTEMPT_KEY: json.dumps({"allowed": True}),
        })
        m = Monitor(probe, local_root=root, halt_grace_s=300, now_fn=clk)
        rec = m.poll_once()
        assert rec["state"] == STATE_COMPLETE, rec["state"]
        assert rec["shutdown_attempt_present"] is True
        assert rec["shutdown_attempt_first_seen_utc"] == "2026-09-06T12:00:00Z"
        assert any("halt pending" in a for a in rec["alerts"])
        # the sighting time is recorded from the FIRST sighting, so nothing is
        # lost by the delay
        clk.advance(400)
        rec2 = m.poll_once()
        assert rec2["state"] == STATE_FAILED_HALT
        assert rec2["shutdown_attempt_first_seen_utc"] == "2026-09-06T12:00:00Z"

    # ---------------- 7 ----------------
    @arm("7  PLANTED-VALUE CONTROL: plant 1.234e-03 in COMPLETE.json, read it "
         "back off the status file through the real parse path; twin without "
         "the plant does NOT show it")
    def a7(root):
        clk = FakeClock()
        m = Monitor(FakeProbe(files={COMPLETE_KEY: _complete_json(plant=True)}),
                    local_root=root, now_fn=clk)
        m.poll_once()
        d = _read_status(root)
        marker = d["completion_marker"]
        assert marker is not None, "reader saw no marker at all"
        assert PLANT_KEY in marker, "the reader could not see the planted key"
        assert marker[PLANT_KEY] == PLANT_VALUE, (
            "reader saw %r, planted %r" % (marker.get(PLANT_KEY), PLANT_VALUE))
        assert marker["final_state"] == PLANT_STATE
        assert any(PLANT_STATE in a for a in d["alerts"]), \
            "the planted final_state did not reach the alert channel"
        # NEGATIVE TWIN: the same reader, no plant -> the plant is genuinely absent,
        # so the positive above is a reading and not a fabrication.
        root2 = os.path.join(root, "noplant")
        m2 = Monitor(FakeProbe(files={COMPLETE_KEY: _complete_json(plant=False)}),
                     local_root=root2, now_fn=FakeClock())
        m2.poll_once()
        d2 = _read_status(root2)
        assert d2["completion_marker"] is not None
        assert PLANT_KEY not in d2["completion_marker"]
        assert d2["state"] == STATE_COMPLETE      # still a real completion read

    # ---------------- 8 ----------------
    @arm("8  TORN MARKER: COMPLETE.json present but unparseable -> NOT complete, "
         "no crash, parse error recorded")
    def a8(root):
        clk = FakeClock()
        m = Monitor(FakeProbe(files={COMPLETE_KEY: '{"utc": "2026-09-0'}),
                    local_root=root, now_fn=clk)
        rec = m.poll_once()
        assert rec["state"] != STATE_COMPLETE, rec["state"]
        assert rec["state"] == STATE_IN_PROGRESS
        assert rec["completion_observed"] is False
        assert rec["completion_marker_parse_error"]
        assert any("NOT parseable" in a for a in rec["alerts"])

    # ---------------- 9 ----------------
    @arm("9  PROBE RAISES: an exploding probe is unreachable, not a crash")
    def a9(root):
        clk = FakeClock()
        m = Monitor(FakeProbe(raise_exc=OSError("network is unreachable")),
                    local_root=root, now_fn=clk)
        rec = m.poll_once()
        assert rec["state"] == STATE_GONE_WITHOUT_COMPLETE, rec["state"]
        assert rec["reachable"] is False
        assert "network is unreachable" in (rec["probe_error"] or "")

    # ---------------- 10 ---------------
    @arm("10 ATOMIC STATUS WRITE: temp file in the same dir, renamed, no residue, "
         "parseable after every poll")
    def a10(root):
        clk = FakeClock()
        probe = FakeProbe(files={})
        m = Monitor(probe, local_root=root, now_fn=clk)
        for i in range(3):
            clk.advance(60)
            probe.files[COMPLETE_KEY] = _complete_json() if i == 2 else None
            m.poll_once()
            assert m.last_tmp_path is not None
            assert os.path.dirname(m.last_tmp_path) == os.path.abspath(root), \
                "temp file is not in the status file's own directory"
            assert not os.path.exists(m.last_tmp_path), "temp file left behind"
            _read_status(root)                      # parses => never a half-file
        leftovers = [f for f in os.listdir(root) if f.endswith(".tmp")]
        assert not leftovers, leftovers

    # ---------------- 11 ---------------
    @arm("11 TIMESTAMPS: first_poll / completion-first-observed / "
         "unreachable-first are each set ONCE and never moved; a flap is visible")
    def a11(root):
        clk = FakeClock()
        probe = FakeProbe(files={})
        m = Monitor(probe, local_root=root, now_fn=clk)
        m.poll_once()                                        # t0 reachable
        t0 = "2026-09-06T12:00:00Z"
        clk.advance(60); probe.reachable = False
        m.poll_once()                                        # t1 unreachable
        clk.advance(60); probe.reachable = True
        probe.files[COMPLETE_KEY] = _complete_json()
        m.poll_once()                                        # t2 back + complete
        clk.advance(60)
        m.poll_once()                                        # t3 still complete
        clk.advance(60); probe.reachable = False
        rec = m.poll_once()                                  # t4 gone again
        assert rec["first_poll_utc"] == t0
        assert rec["unreachable_first_utc"] == "2026-09-06T12:01:00Z"
        assert rec["completion_first_observed_utc"] == "2026-09-06T12:02:00Z"
        assert rec["unreachable_current_since_utc"] == "2026-09-06T12:04:00Z"
        assert rec["reachable_last_utc"] == "2026-09-06T12:03:00Z"
        assert rec["state"] == STATE_GONE_AFTER_COMPLETE
        assert rec["poll_count"] == 5

    # ---------------- 12 ---------------
    @arm("12 NO COST CLAIM: the status record quotes no dollars and no idle total")
    def a12(root):
        m = Monitor(FakeProbe(files={COMPLETE_KEY: _complete_json()}),
                    local_root=root, now_fn=FakeClock())
        rec = m.poll_once()
        banned = ("idle_hours", "idle_minutes", "idle_seconds", "cost_usd",
                  "usd", "dollars", "gpu_hours_idle", "wasted_hours")
        for k in banned:
            assert k not in rec, "the monitor claimed a cost figure: %s" % k
        assert "cost_note" in rec and "NO cost figure" in rec["cost_note"]

    # ---------------- 13 ---------------
    @arm("13 NAMED ARTEFACTS, NO GLOB: every path appears verbatim in the remote "
         "command and no wildcard appears in the artefact table")
    def a13(root):
        script = build_remote_script()
        for rel in NODE_ARTEFACTS:
            assert rel in script, "artefact not named in the remote command: %s" % rel
        for rel in NODE_ARTEFACTS:
            assert not any(c in rel for c in "*?[]"), rel
        assert BEGIN_MARK in script and END_MARK in script
        # framing decides reachability, not ssh's rc
        assert parse_probe_output("").reachable is False
        assert parse_probe_output("BEGIN_PROBE\n").reachable is False
        # and a real round trip through the parser, base64 and all
        payload = _complete_json(plant=True)
        b64 = base64.b64encode(payload.encode()).decode()
        out = ("BEGIN_PROBE\nHOSTNAME gpu1\nNODE_UTC 2026-09-06T12:00:00Z\n"
               "DRIVER not_running\nFILE %s %s\nMISSING %s\nEND_PROBE\n"
               % (COMPLETE_KEY, b64, SHUTDOWN_ATTEMPT_KEY))
        pr = parse_probe_output(out)
        assert pr.reachable and pr.driver_running is False
        assert json.loads(pr.text(COMPLETE_KEY))[PLANT_KEY] == PLANT_VALUE
        assert pr.present(SHUTDOWN_ATTEMPT_KEY) is False

    # ---------------- 14 ---------------
    @arm("14 NOT A GRADER: monitor states are disjoint from the verdict vocabulary")
    def a14(root):
        _assert_states_disjoint_from_verdicts()
        _assert_absence_cannot_mean_complete()
        _assert_no_globs()
        # a driver that ended BLOCKED is echoed as the DRIVER's field; the
        # monitor's own state is still COMPLETE, not the verdict token
        m = Monitor(FakeProbe(files={COMPLETE_KEY: _complete_json("BLOCKED")}),
                    local_root=root, now_fn=FakeClock())
        rec = m.poll_once()
        assert rec["state"] == STATE_COMPLETE
        assert rec["state"] not in VERDICT_VOCABULARY
        assert rec["completion_marker"]["final_state"] == "BLOCKED"
        assert rec["monitor_is_a_grader"] is False
        assert rec["on_frozen_grading_path"] is False

    # ---------------- 15 ---------------
    @arm("15 RESTART MEMORY: a fresh Monitor over the same status file still "
         "knows completion was observed")
    def a15(root):
        clk = FakeClock()
        probe = FakeProbe(files={COMPLETE_KEY: _complete_json()})
        m1 = Monitor(probe, local_root=root, now_fn=clk)
        assert m1.poll_once()["state"] == STATE_COMPLETE
        del m1
        clk.advance(300)
        probe.reachable = False
        m2 = Monitor(probe, local_root=root, now_fn=clk)      # fresh object
        rec = m2.poll_once()
        assert rec["state"] == STATE_GONE_AFTER_COMPLETE, rec["state"]
        assert rec["completion_first_observed_utc"] == "2026-09-06T12:00:00Z"

    # ---------------- 16 ---------------
    @arm("16 DETACH WRAPPER: rc is captured INSIDE the wrapper, after the monitor "
         "line, never around setsid")
    def a16(root):
        wrapper_src = WRAPPER_TEMPLATE.format(
            wrapper_pid="/x/wp", python="/x/py", script="/x/s.py", args="--once",
            outlog="/x/out", rcfile="/x/rc")
        # EXECUTABLE lines only -- the wrapper's comment explains setsid, and a
        # bare substring test would flag the explanation. (This arm's first
        # version did exactly that and failed; the instrument was wrong, not the
        # wrapper.)
        code = [l.strip() for l in wrapper_src.splitlines()
                if l.strip() and not l.strip().startswith("#")]
        rc_i = next(i for i, l in enumerate(code) if l.startswith("rc=$?"))
        run_i = next(i for i, l in enumerate(code) if l.startswith("/x/py"))
        assert rc_i == run_i + 1, "rc=$? does not immediately follow the monitor line"
        assert not any("setsid" in l for l in code), \
            "setsid is EXECUTED inside the wrapper -- rc would be its 0, not the " \
            "monitor's: %r" % [l for l in code if "setsid" in l]
        assert '"$rc"' in wrapper_src and "exit $rc" in wrapper_src

        # The check must be shown to REJECT a wrong wrapper, or it proves
        # nothing about the right one.
        def _check(src):
            c = [l.strip() for l in src.splitlines()
                 if l.strip() and not l.strip().startswith("#")]
            if any("setsid" in l for l in c):
                raise AssertionError("setsid executed inside the wrapper")
            i_rc = next((i for i, l in enumerate(c) if l.startswith("rc=$?")), -1)
            i_run = next((i for i, l in enumerate(c) if l.startswith("/x/py")), -2)
            if i_rc != i_run + 1:
                raise AssertionError("rc=$? not immediately after the monitor line")
            return True

        assert _check(wrapper_src) is True                 # the real one passes
        for bad in (wrapper_src.replace("/x/py", "setsid /x/py"),      # rc = setsid's
                    wrapper_src.replace("rc=$?", "true\nrc=$?")):      # rc = true's
            try:
                _check(bad)
            except AssertionError:
                pass
            else:
                raise AssertionError("the wrapper check accepted a wrapper that "
                                     "would capture the wrong rc: %r" % bad)
        # and the wrapper the real detach path writes is executable and identical
        # in shape (generated without launching anything)
        os.makedirs(root, exist_ok=True)
        body = WRAPPER_TEMPLATE.format(
            wrapper_pid=shlex.quote(os.path.join(root, WRAPPER_PID_NAME)),
            python=shlex.quote("/usr/bin/python3"),
            script=shlex.quote("/x/s.py"), args="--once",
            outlog=shlex.quote(os.path.join(root, DETACH_OUT_NAME)),
            rcfile=shlex.quote(os.path.join(root, RC_NAME)))
        p = os.path.join(root, WRAPPER_NAME)
        with open(p, "w") as fh:
            fh.write(body)
        os.chmod(p, 0o755)
        assert os.access(p, os.X_OK)
        # Exercise the wrapper for real with a command that FAILS (rc 7), in BOTH
        # setsid invocation modes, and prove the wrapper records 7 either way.
        #
        # MEASURED HERE, and the reason the inside-capture is load-bearing:
        # `setsid` FORKS only when its caller is already a session/process-group
        # leader; otherwise it setsid()s and execs in place, so the rc passes
        # through. `detach()` uses Popen(start_new_session=True), which makes the
        # child a leader BEFORE exec -- so detach's setsid ALWAYS forks and its
        # parent ALWAYS returns 0 regardless of outcome. That is the trap, and
        # this arm reproduces it rather than assuming it.
        fake = os.path.join(root, "fails.sh")
        with open(fake, "w") as fh:
            fh.write("#!/bin/sh\nexit 7\n")
        os.chmod(fake, 0o755)

        def _run_wrapper(tag, new_session):
            rcfile = os.path.join(root, "%s.rc" % tag)
            body_x = WRAPPER_TEMPLATE.format(
                wrapper_pid=shlex.quote(os.path.join(root, "%s.pid" % tag)),
                python=shlex.quote("/bin/sh"), script=shlex.quote(fake), args="",
                outlog=shlex.quote(os.path.join(root, "%s.out" % tag)),
                rcfile=shlex.quote(rcfile))
            px = os.path.join(root, "%s.sh" % tag)
            with open(px, "w") as fh:
                fh.write(body_x)
            outer = subprocess.run(["setsid", "/bin/sh", px],
                                   start_new_session=new_session).returncode
            for _ in range(80):
                if os.path.exists(rcfile):
                    break
                time.sleep(0.05)
            with open(rcfile) as fh:
                return outer, fh.read()

        # (a) detach()'s own form: caller is a session leader -> setsid forks.
        outer_fork, rec_fork = _run_wrapper("wfork", True)
        assert "rc=7" in rec_fork, "wrapper recorded %r, expected rc=7" % rec_fork
        assert outer_fork == 0, (
            "premise of the whole detach design failed: with "
            "start_new_session=True setsid returned %d, expected 0" % outer_fork)
        # ^ THE PAIRING: setsid said 0 while the true status was 7. An rc taken
        #   around the setsid line would have reported success for a failure.

        # (b) the exec-in-place form, recorded for completeness: rc passes
        #     through, so the outer code is right SOMETIMES -- which is exactly
        #     why it may never be relied on.
        outer_exec, rec_exec = _run_wrapper("wexec", False)
        assert "rc=7" in rec_exec, "wrapper recorded %r, expected rc=7" % rec_exec
        assert outer_exec == 7, (
            "expected exec-in-place setsid to pass rc through, got %d" % outer_exec)
        # The wrapper's inside-capture is correct in BOTH modes; the outer code
        # is correct in only one, and detach() is in the other.

    # ---------------- 17 ---------------
    @arm("17 MUTATION (state logic disabled): arms 3 and 5 must now FAIL")
    def a17(root):
        this = sys.modules[__name__]
        real = this.classify

        def collapsed(reachable, complete_readable, shutdown_attempt_present,
                      ever_completed, halt_pending_s, halt_grace_s):
            # the two defects this file exists to prevent, in one mutant:
            #   (i) node absence read as completion;
            #  (ii) a failed halt not distinguished from a normal one.
            return STATE_COMPLETE

        results = {}
        this.classify = collapsed
        try:
            for name, fn in (("arm3", a3), ("arm5", a5)):
                d = os.path.join(root, "mut_" + name)
                os.makedirs(d, exist_ok=True)
                try:
                    fn(d)
                    results[name] = "PASSED"
                except AssertionError as exc:
                    results[name] = "FAILED: %s" % (str(exc)[:60],)
                except Exception as exc:
                    results[name] = "FAILED(%s): %s" % (type(exc).__name__,
                                                        str(exc)[:60])
        finally:
            this.classify = real
        assert results["arm3"].startswith("FAILED"), (
            "arm 3 still passed with the state logic disabled -- it does not bind: %s"
            % results["arm3"])
        assert results["arm5"].startswith("FAILED"), (
            "arm 5 still passed with the state logic disabled -- it does not bind: %s"
            % results["arm5"])
        # and with the real logic restored, both pass again
        for name, fn in (("arm3", a3), ("arm5", a5)):
            d = os.path.join(root, "restored_" + name)
            os.makedirs(d, exist_ok=True)
            fn(d)

    # ---------------- 18 ---------------
    @arm("18 MUTATION (completion memory from absence): the ambiguous arm must FAIL")
    def a18(root):
        this = sys.modules[__name__]
        real = Monitor._observe_completion

        def leaky(self, reachable, marker_obj, now):
            # the exact forbidden inference: a vanished node counts as completed
            if self.state["completion_first_observed_utc"] is None:
                self.state["completion_first_observed_utc"] = fmt(now)
            return True

        Monitor._observe_completion = leaky
        try:
            d = os.path.join(root, "mut")
            os.makedirs(d, exist_ok=True)
            failed = False
            try:
                a3(d)
            except AssertionError:
                failed = True
            assert failed, ("arm 3 passed while absence was being recorded as "
                            "completion -- the ambiguity guard does not bind")
        finally:
            Monitor._observe_completion = real
        d2 = os.path.join(root, "restored")
        os.makedirs(d2, exist_ok=True)
        a3(d2)

    # ---- run them --------------------------------------------------------
    base = tempfile.mkdtemp(prefix="watch_arm2_selftest_")
    passed, failed = 0, []
    try:
        for i, (name, fn) in enumerate(arms, 1):
            d = os.path.join(base, "arm%02d" % i)
            os.makedirs(d, exist_ok=True)
            try:
                fn(d)
                passed += 1
                if verbose:
                    print("  PASS  %s" % name)
            except Exception:
                failed.append(name)
                if verbose:
                    print("  FAIL  %s" % name)
                    print(textwrap_indent(traceback.format_exc(), "        "))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("\n[selftest] %d arms, %d passed, %d failed" % (len(arms), passed,
                                                          len(failed)))
    for f in failed:
        print("[selftest] FAILED ARM: %s" % f)
    return 0 if not failed else 1


def textwrap_indent(s, pad):
    return "".join(pad + line for line in io.StringIO(s).readlines())


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(
        description="Arm-2 completion monitor (B4). A MONITOR: grades nothing, "
                    "not on the frozen grading path.")
    ap.add_argument("--selftest", action="store_true",
                    help="hermetic selftest; no ssh, no network")
    ap.add_argument("--detach", action="store_true",
                    help="re-exec detached under setsid and print the pid")
    ap.add_argument("--once", action="store_true", help="one poll, then exit")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S,
                    help="seconds between polls (default %d)" % DEFAULT_INTERVAL_S)
    ap.add_argument("--halt-grace", type=float, default=DEFAULT_HALT_GRACE_S,
                    help="seconds a reachable node may keep shutdown_attempt.json "
                         "before FAILED-HALT fires (default %d; 0 = fire on first "
                         "sighting)" % DEFAULT_HALT_GRACE_S)
    ap.add_argument("--host", default=GPU_HOST)
    ap.add_argument("--remote-dir", default=REMOTE_DIR)
    ap.add_argument("--local-root", default=LOCAL_ROOT)
    ap.add_argument("--ssh-timeout", type=float, default=DEFAULT_SSH_TIMEOUT_S)
    ap.add_argument("--max-polls", type=int, default=None)
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    if args.detach:
        rest = [a for a in argv if a != "--detach"]
        if "--once" not in rest and "--interval" not in " ".join(rest):
            rest += ["--interval", str(args.interval)]
        pid, wrapper = detach(rest, local_root=args.local_root)
        if pid is None:
            print("[watch-arm2] DETACH FAILED: no live pid appeared in %s within "
                  "15s. setsid's own return code proves nothing, so this is the "
                  "only honest verdict available. Wrapper: %s ; check %s"
                  % (os.path.join(args.local_root, PID_NAME), wrapper,
                     os.path.join(args.local_root, DETACH_OUT_NAME)))
            return 2
        print("[watch-arm2] detached pid %d (verified alive by signal 0, NOT by "
              "setsid's return code)" % pid)
        print("[watch-arm2] pidfile  %s" % os.path.join(args.local_root, PID_NAME))
        print("[watch-arm2] wrapper  %s (rc captured inside it -> %s)"
              % (wrapper, os.path.join(args.local_root, RC_NAME)))
        print("[watch-arm2] status   %s" % os.path.join(args.local_root, STATUS_NAME))
        print("[watch-arm2] log      %s" % os.path.join(args.local_root, LOG_NAME))
        print("[watch-arm2] stop it with: kill %d" % pid)
        return 0

    write_pidfile(args.local_root)
    probe = SshNodeProbe(host=args.host, remote_dir=args.remote_dir,
                         timeout_s=args.ssh_timeout)
    mon = Monitor(probe, local_root=args.local_root,
                  halt_grace_s=args.halt_grace)
    if args.once:
        rec = mon.poll_once()
        print("[watch-arm2] %s %s" % (rec["last_poll_utc"], rec["state"]))
        for a in rec["alerts"]:
            print("[watch-arm2]   ! %s" % a)
        print("[watch-arm2] status %s" % mon.status_path)
        return 0
    return mon.run(interval_s=args.interval, max_polls=args.max_polls)


if __name__ == "__main__":
    sys.exit(main())
