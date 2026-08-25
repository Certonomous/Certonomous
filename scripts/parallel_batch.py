#!/usr/bin/env python3
"""Parallel batch runner for small cases, with four guards and a runaway hold.

WHY THIS EXISTS.  Sanaa ruled on 2026-08-25 that case execution is scheduled to
80-90 % core utilisation at all times, that small cases run in parallel batches,
and that the framing is "what else can start", not "what may start".  Rigor is
unchanged.  This runner is the mechanism for the throughput half of that ruling,
and its guards are the mechanism for the rigor half.

THE CAP IS A RUNAWAY GUARD, NOT A BUDGET GATE.  Sanaa ruled the same day, in her
own session turn, relayed to this lane by cfd-supervisor and quoted there
verbatim: *"I want the three teams to forget about cost constraints for now ...
no team stops anything in the name of saving compute."*  So this runner does NOT
kill a job for going over its core-minute cap.  It **reports and holds**: the
breach is stamped into the job's record and into every contention sample from
that moment, the job KEEPS RUNNING, and the supervisor decides -- extend by a
dated amendment because the work is sound, or stop it because it is genuinely
stuck, diverging or looping.

    DISCLOSED TENSION, because it must not be discovered later as a surprise.
    CLAUDE.md rule 12 as written says an overrun STOPS THE RUN and does not get
    a new budget.  The behaviour here departs from that sentence on the strength
    of the directive above.  THIS FILE DOES NOT EDIT CLAUDE.md AND THIS LANE DID
    NOT TREAT THE RELAY AS CONSENT TO EDIT IT (standing rule 9).  The departure
    is implemented, labelled, and put in front of the supervisor as a diff.
    ``--cap-action kill`` restores the literal rule-12 behaviour for any caller
    who wants it, and the kill path is still exercised by ``--selftest``.

    COSTING IS UNCHANGED.  She lifted the constraint, not the measurement.  Every
    job still carries a cap, every core-minute is still measured and written to
    disk, and the estimate-versus-actual row still lands in
    ``docs/COST_CALIBRATION.md`` at completion.

THE RUNAWAY CEILING IS BOX PROTECTION, NOT BUDGET.  A job that has passed
``runaway_multiple`` times its cap is stopped, and the record says so in those
words.  This is not a cost gate: the box is shared -- at the time of writing the
heat-transfer family had three ``buoyantBoussinesq*`` solvers live and the dafoam
family had container work live on the same 16 cores -- and a job in an infinite
loop takes down three other teams' runs.  Pass ``--runaway-multiple 0`` to
disable it and let a job run without any ceiling at all.

THE FOUR GUARDS

1. CORE SELECTION AND PINNING.  Per-core busy fraction is measured from
   ``/proc/stat`` over a probe window; cores above ``--core-busy-max`` are
   treated as SOMEBODY ELSE'S and are not offered; each job is pinned with
   ``taskset -c`` to as many of the remainder as it has ranks.  CONCURRENCY IS
   BOUNDED BY CORES AND MEMORY, NOT BY A NUMBER -- ``--jobs 0`` (the default)
   means "as many as the free cores allow".  If fewer cores are free than the
   caller asked for, the batch NARROWS AND SAYS SO; it does not oversubscribe.
   THE MASK IS SET IN THE CHILD, BEFORE EXEC (``os.sched_setaffinity`` inside
   ``preexec_fn``); ``taskset -c`` stays on the argv as a redundant second
   application that also makes the pinning visible in ``ps``.  Pinning is then
   VERIFIED by reading the kernel's own ``/proc/<pid>/status``
   ``Cpus_allowed_list`` and requiring it to EQUAL the cores asked for: a
   pinning never shown to bind is not a pinning (standing rule 3, applied to a
   control rather than to a zero).  A job still alive whose mask never narrows
   is REFUSED and stopped, never run unpinned.

   DEFECT REPAIRED 2026-08-25, recorded because what failed was the CONTROL,
   not the mechanism.  The read-back originally sampled ``Cpus_allowed_list``
   once, the instant ``Popen`` returned, and read ``0-15`` on every job:
   ``Popen`` returns after the fork, before the affinity syscall has
   necessarily landed, so the check reported UNPINNED on a batch that was in
   fact pinned.  ``--selftest`` caught it at 19/20 and it is fixed at the
   source -- in the child, before exec -- not by loosening the assertion.

2. THE CORE-MINUTE CAP, as report-and-hold, above.

3. MEMORY GUARD.  ``MemAvailable`` is read from ``/proc/meminfo`` immediately
   before each launch.  A job whose ``mem_estimate_gb`` would push availability
   below ``mem_floor_gb`` IS NOT LAUNCHED.  It is retried while memory might
   free up, for at most ``mem_wait_s``; after that it is ``BLOCKED``, which is a
   verdict in the fixed vocabulary and is not a failure of the job.  The wait has
   a deadline because a guard that hangs is the guard taking the box down by a
   different route.

4. CONTENTION IS MEASURED AND DISCLOSED, NEVER ASSUMED.  Sanaa's ruling is that
   measured contention is acceptable AND DISCLOSED.  A contention file carries
   ``/proc/loadavg`` and ``MemAvailable`` at start, at every sample interval, and
   at end, so the disclosure cites a file rather than a recollection.

5. THE FRESH-CASE LAUNCH GUARD.  A job that names ``foam_case`` is REFUSED when
   that case already holds ``0/`` or any numeric time directory.  CLAUDE.md
   rule 4's age guard dates a run by requiring every field at ``endTime`` to be
   NEWER than the case's own ``0/`` field; a pre-existing ``0/`` or time
   directory destroys that dating before the solver even starts.  This is a
   LAUNCH guard in the launcher and it neither replaces nor weakens any
   completion criterion -- rule 4's completion clauses stay entirely in the
   per-campaign comparators, unchanged.  ``allow_existing_times: true``
   bypasses it and is for a deliberate restart, with the reason stated in the
   job spec.

   TWO USAGE CONSTRAINTS ON GUARD 5, stated so neither is discovered later.
   (a) IT READS THE CASE ROOT ONLY.  A DECOMPOSED case keeps its time
   directories under ``processor*/``, which this guard does not walk.  In
   practice the root ``0/`` still trips it, so a decomposed case is covered
   INCIDENTALLY rather than by design -- do NOT "optimise away" the root ``0/``
   check on the grounds that decomposed cases are covered, because that is the
   only thing covering them.
   (b) IT WANTS THE RUN DIRECTORY, NOT A PRE-POPULATED TEMPLATE.  Any case
   carrying ``0/`` trips it, and a template always carries ``0/``.  Point
   ``foam_case`` at the FRESH directory the solver will write into.  A caller
   who reaches for ``allow_existing_times: true`` to quiet the guard has
   pointed it at the wrong directory, and the guard becomes decorative.

EVERY NUMBER THIS RUNNER REPORTS IS READ BACK FROM DISK.  The per-case record is
written to ``<cwd>/batch_record.json`` and the batch summary is built by
RE-READING those files, never from the in-memory state that wrote them.
``--selftest`` proves it by MUTATING a record on disk after the job finished and
requiring the summary to carry the mutated value: a read-back that cannot see a
change it was not told about is not a read-back.

SUBPROCESSES ARE PUT IN THEIR OWN SESSION (``start_new_session=True``).  A
foreground solver launched from a tool call gets SIGTERMed when the tool call
ends; a session leader survives, and the whole group can still be signalled as
one if the runaway ceiling fires.

EXIT CODES, one per verdict, because conflating them is how a caller turns a
run that produced no number into a run that produced a failing one.

    0  PASS          every job completed rc 0, none blocked, none stopped.
    1  GATE FAIL     RESERVED AND UNREACHABLE FROM THIS RUNNER.  A gate failure
                     means a value was evaluated and MISSED its band, and this
                     runner never evaluates a value -- it reports whether the
                     JOBS RAN.  Bands are the comparator's business.  The code
                     is kept defined so nothing silently reuses it.
    2  REFUSE        the runner could not establish the conditions it needs (no
                     free core, unreadable manifest, a record that will not read
                     back, a pinning that never bound, a case that already holds
                     0/).  It REFUSES rather than degrades (rule 4's posture).
    3  NOT A RESULT  at least one job exited nonzero, or the runaway ceiling
                     stopped it.  NO VALUE EXISTS to compare against anything.
    4  BLOCKED       at least one job was never launched (the memory guard, or
                     the batch ended before it was reached).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import threading
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

EXIT_OK, EXIT_GATE_FAIL, EXIT_REFUSE = 0, 1, 2
EXIT_NOT_A_RESULT, EXIT_BLOCKED = 3, 4

# Standing rule 3's planted perturbation, the same constant the lab's Roache
# instrument uses (scripts/roache_triple.py PLANT, ported from T3:81).  Used
# here only in --selftest, to prove the disk read-back can see a change.
PLANT = 1.234e-03

DEFAULT_MEM_FLOOR_GB = 6.0
DEFAULT_CORE_BUSY_MAX = 0.50
DEFAULT_SAMPLE_INTERVAL_S = 30.0
DEFAULT_KILL_GRACE_S = 10.0
DEFAULT_CORE_PROBE_S = 3.0
DEFAULT_MEM_WAIT_S = 300.0
DEFAULT_RUNAWAY_MULTIPLE = 10.0

RECORD_NAME = "batch_record.json"

STATE_DONE = "DONE"          # the process exited on its own; see rc
STATE_STOPPED = "STOPPED"    # the runaway ceiling fired (box protection)
STATE_BLOCKED = "BLOCKED"    # never launched; the memory guard refused it
STATE_PENDING = "PENDING"    # queued, batch ended before it was reached

CAP_ACTION_HOLD = "hold"     # report-and-hold: the 2026-08-25 directive
CAP_ACTION_KILL = "kill"     # the literal CLAUDE.md rule-12 behaviour


class Refuse(Exception):
    """Conditions the runner needs and does not have.  CLI turns it into exit 2."""


def _utc():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# box readings -- one function each, used by BOTH the guards and the record, so
# a guard and its own disclosure can never disagree about what the box said
# ---------------------------------------------------------------------------
def mem_available_gb() -> float:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return float(line.split()[1]) / (1024.0 * 1024.0)
    raise Refuse("/proc/meminfo has no MemAvailable line; the memory guard "
                 "cannot be evaluated and an unevaluated guard is not a passed one")


def loadavg() -> tuple[float, float, float]:
    a, b, c = Path("/proc/loadavg").read_text().split()[:3]
    return float(a), float(b), float(c)


def _cpu_jiffies() -> dict[int, tuple[int, int]]:
    out = {}
    for line in Path("/proc/stat").read_text().splitlines():
        m = re.match(r"cpu(\d+)\s+(.*)", line)
        if not m:
            continue
        vals = [int(x) for x in m.group(2).split()]
        idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
        out[int(m.group(1))] = (sum(vals) - idle, sum(vals))
    return out


def core_busy_fractions(probe_s: float = DEFAULT_CORE_PROBE_S) -> dict[int, float]:
    """Busy fraction per core over ``probe_s``.  This is how the runner tells ITS
    cores from ANOTHER TEAM'S: a core already running somebody's solver reads
    near 1.0 and is not offered."""
    a = _cpu_jiffies()
    time.sleep(probe_s)
    b = _cpu_jiffies()
    out = {}
    for core in sorted(a):
        db, dt = b[core][0] - a[core][0], b[core][1] - a[core][1]
        out[core] = (db / dt) if dt > 0 else 1.0
    return out


def pick_cores(want: int, busy_max: float, probe_s: float
               ) -> tuple[list[int], dict[int, float]]:
    """The ``want`` least-busy cores at or below ``busy_max``.  ``want <= 0``
    means every free core -- concurrency bounded by the box, not by a number.
    Returns fewer than asked for on a loaded box, and the caller DISCLOSES the
    narrowing rather than oversubscribing."""
    frac = core_busy_fractions(probe_s)
    free = sorted((c for c, f in frac.items() if f <= busy_max), key=lambda c: frac[c])
    if not free:
        raise Refuse(f"no core is at or below the busy threshold {busy_max:.2f}; "
                     f"measured {sorted(round(v, 3) for v in frac.values())[:6]}... "
                     "-- the box belongs to somebody else right now and this "
                     "batch does not start")
    return (free if want <= 0 else free[:want]), frac


def parse_cpu_list(s: str) -> set[int]:
    """``Cpus_allowed_list`` syntax -- ``0-3,8,12-13`` -- as a set of ints."""
    out: set[int] = set()
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out


TIME_DIR_RE = re.compile(r"^\d+(\.\d+)?([eE][+-]?\d+)?$")


def existing_time_dirs(case: Path) -> list[str]:
    """Directory names under ``case`` that OpenFOAM would read as a time,
    ``0`` included.  The fresh-case launch guard reads this."""
    if not case.is_dir():
        return []
    return sorted((p.name for p in case.iterdir()
                   if p.is_dir() and TIME_DIR_RE.match(p.name)),
                  key=lambda n: (float(n), n))


def cpus_allowed(pid: int) -> str | None:
    """``Cpus_allowed_list`` for a live pid: the kernel's own statement of what
    the pinning actually did.  None when the process is already gone."""
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("Cpus_allowed_list:"):
                return line.split(":", 1)[1].strip()
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return None
    return None


def verify_pinning(pid: int, cores: list[int], timeout_s: float = 2.0,
                   poll_s: float = 0.005) -> tuple[str | None, bool]:
    """Require the KERNEL to agree that ``pid`` is pinned to exactly ``cores``.

    Returns ``(mask_string, verified)``.  ``verified`` is False when the process
    exited before the mask could be read -- honest, not fatal; the caller writes
    that on the record rather than claiming a pinning it never saw."""
    want = set(cores)
    deadline = time.monotonic() + timeout_s
    last = None
    while time.monotonic() < deadline:
        got = cpus_allowed(pid)
        if got is None:
            return last, False
        last = got
        if parse_cpu_list(got) == want:
            return got, True
        time.sleep(poll_s)
    return last, False


def _preexec(cores: list[int]):
    """Set the affinity mask in the CHILD, before exec.  If the syscall fails,
    the exception propagates out of ``Popen`` and the launch fails LOUDLY
    instead of quietly running unpinned."""
    def _f():
        os.sched_setaffinity(0, cores)
    return _f


# ---------------------------------------------------------------------------
# the record -- ONE constructor, so every branch writes the SAME key set.
# scripts/check_grader_self_blindness.py probe A: two dict assignments to one
# container with different key sets is the L-322 shape, and it has already cost
# this lab a graded run.
# ---------------------------------------------------------------------------
RECORD_KEYS = ("name", "cwd", "argv", "log", "ranks", "cores", "cpus_allowed",
               "cpus_allowed_verified", "foam_case",
               "core_minute_cap", "cap_action", "cap_exceeded",
               "cap_exceeded_utc", "cap_exceeded_at_core_minutes",
               "runaway_multiple", "stopped_on_runaway", "mem_estimate_gb",
               "state", "rc", "wall_s", "core_minutes", "started_utc",
               "finished_utc", "note")


def make_record(**kw):
    missing = [k for k in RECORD_KEYS if k not in kw]
    extra = [k for k in kw if k not in RECORD_KEYS]
    assert not missing and not extra, f"record schema drift: -{missing} +{extra}"
    return dict(kw)


def blank_record(job, state, note):
    """A record for a job that never ran.  SAME KEY SET as a finished one -- the
    L-322 defect is a PENDING branch that omits a key the summary then reads."""
    return make_record(
        name=job.name, cwd=str(job.cwd), argv=list(job.argv), log=job.log,
        ranks=job.ranks, cores=None, cpus_allowed=None,
        cpus_allowed_verified=False,
        foam_case=(str(job.foam_case) if job.foam_case else None),
        core_minute_cap=job.cap, cap_action=job.cap_action, cap_exceeded=False,
        cap_exceeded_utc=None, cap_exceeded_at_core_minutes=None,
        runaway_multiple=job.runaway_multiple, stopped_on_runaway=False,
        mem_estimate_gb=job.mem_gb, state=state, rc=None, wall_s=0.0,
        core_minutes=0.0, started_utc=None, finished_utc=_utc(), note=note)


def write_record(cwd: Path, rec: dict) -> Path:
    p = Path(cwd) / RECORD_NAME
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return p


def read_record(cwd: Path) -> dict:
    """THE read path.  The summary uses only this; nothing is carried over from
    the in-memory state that wrote it."""
    p = Path(cwd) / RECORD_NAME
    if not p.is_file():
        raise Refuse(f"no {RECORD_NAME} at {p}: a job whose record is not on "
                     "disk is not a completed job")
    doc = json.loads(p.read_text())
    missing = [k for k in RECORD_KEYS if k not in doc]
    if missing:
        raise Refuse(f"{p} is missing {missing}; it does not read back and the "
                     "summary refuses rather than reporting a partial row")
    return doc


# ---------------------------------------------------------------------------
# contention -- measured, per batch, and disclosed
# ---------------------------------------------------------------------------
class Contention:
    def __init__(self, path: Path, batch: str):
        self.path = Path(path)
        self.doc = {"batch": batch, "samples": [],
                    "note": "load averages are BOX-WIDE: other teams' solvers are "
                            "in them by design, which is what makes this a "
                            "contention measurement rather than a self-report"}

    def sample(self, tag: str, running: list[str], held: list[str] | None = None):
        l1, l5, l15 = loadavg()
        self.doc["samples"].append(
            {"tag": tag, "utc": _utc(), "load1": l1, "load5": l5, "load15": l15,
             "mem_available_gb": round(mem_available_gb(), 3),
             "n_running_this_batch": len(running), "running": sorted(running),
             "held_over_cap": sorted(held or [])})
        self.flush()

    def flush(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.doc, indent=2) + "\n")


def contention_summary(doc: dict, n_cores_total: int) -> dict:
    """Contention as a measured percentage, with the samples it came from still
    on disk beside it.

    The figure is the excess of the box-wide 1-minute load over the core count
    this batch itself is using, as a fraction of the total core count -- i.e. how
    much of the box OTHER work held while these jobs ran.  It over-estimates when
    other teams are loaded but idle and under-estimates when they are blocked on
    I/O.  Stated so a reader can discount it rather than take it on faith.
    """
    s = [x for x in doc.get("samples", []) if x.get("tag") != "batch_start"]
    if not s:
        return {"samples": 0, "load1_mean": None, "load1_max": None,
                "contention_pct": None, "mem_available_gb_min": None}
    loads = [x["load1"] for x in s]
    ext = [max(0.0, l - x["n_running_this_batch"]) for l, x in zip(loads, s)]
    return {"samples": len(s),
            "load1_mean": round(sum(loads) / len(loads), 3),
            "load1_max": round(max(loads), 3),
            "contention_pct": round(100.0 * (sum(ext) / len(ext)) / n_cores_total, 2),
            "mem_available_gb_min": round(min(x["mem_available_gb"] for x in s), 3)}


# ---------------------------------------------------------------------------
class Job:
    def __init__(self, spec: dict, defaults: dict | None = None):
        d = defaults or {}
        for key in ("name", "cwd", "argv"):
            if key not in spec:
                raise Refuse(f"job spec has no {key!r}: {spec}")
        self.name = str(spec["name"])
        self.cwd = Path(spec["cwd"]).resolve()
        self.argv = [str(a) for a in spec["argv"]]
        self.log = str(spec.get("log", f"log.{self.name}"))
        self.ranks = int(spec.get("ranks", 1))
        if self.ranks < 1:
            raise Refuse(f"job {self.name!r} has ranks {self.ranks} < 1")
        self.cap = float(spec.get("core_minute_cap", 0.0))
        if self.cap <= 0.0:
            raise Refuse(
                f"job {self.name!r} has no positive core_minute_cap. Costing is "
                "UNCHANGED by the 2026-08-25 directive -- the cap is now a "
                "runaway guard rather than a budget gate, but a run with no "
                "costing at all is still disqualified (CLAUDE.md rule 12).")
        self.mem_gb = float(spec.get("mem_estimate_gb", 0.5))
        fc = spec.get("foam_case")
        self.foam_case = None if fc in (None, "") else (
            Path(str(fc)) if str(fc).startswith("/") else self.cwd / str(fc))
        self.allow_existing_times = bool(spec.get("allow_existing_times", False))
        self.cap_action = str(spec.get("cap_action", d.get("cap_action",
                                                           CAP_ACTION_HOLD)))
        if self.cap_action not in (CAP_ACTION_HOLD, CAP_ACTION_KILL):
            raise Refuse(f"cap_action must be {CAP_ACTION_HOLD!r} or "
                         f"{CAP_ACTION_KILL!r}, got {self.cap_action!r}")
        self.runaway_multiple = float(spec.get("runaway_multiple",
                                               d.get("runaway_multiple",
                                                     DEFAULT_RUNAWAY_MULTIPLE)))
        self.proc = None
        self.cores: list[int] | None = None
        self.cpus_allowed = None
        self.cpus_allowed_verified = False
        self.t0 = None
        self.started_utc = None
        self.cap_exceeded = False
        self.cap_exceeded_utc = None
        self.cap_exceeded_at = None
        self.stopped_on_runaway = False
        self.note = ""
        self.blocked_attempts = 0
        self.blocked_since = None

    def core_minutes(self, now=None) -> float:
        if self.t0 is None:
            return 0.0
        return ((now if now is not None else time.monotonic()) - self.t0) \
            * self.ranks / 60.0


def run_batch(manifest: dict, *, concurrency: int, mem_floor_gb: float,
              core_busy_max: float, sample_interval_s: float,
              kill_grace_s: float, core_probe_s: float, summary_path: Path,
              mem_wait_s: float = DEFAULT_MEM_WAIT_S, defaults: dict | None = None,
              log=print) -> dict:
    batch = str(manifest.get("batch", "batch"))
    jobs = [Job(s, defaults) for s in manifest["jobs"]]
    if not jobs:
        raise Refuse("manifest has no jobs")

    max_ranks = max(j.ranks for j in jobs)
    want_cores = 0 if concurrency <= 0 else concurrency * max_ranks
    cores, frac = pick_cores(want_cores, core_busy_max, core_probe_s)
    n_cores_total = len(frac)
    if len(cores) < max_ranks:
        raise Refuse(f"the widest job needs {max_ranks} cores and only "
                     f"{len(cores)} are free at busy <= {core_busy_max:.2f}")
    narrowed = want_cores > 0 and len(cores) < want_cores
    if narrowed or concurrency <= 0:
        log(f"[{batch}] cores offered: {cores} "
            f"({len(cores)} of {n_cores_total} on the box, busy <= "
            f"{core_busy_max:.2f}). Concurrency is bounded by cores and memory, "
            "not by a number; any narrowing is disclosed, not absorbed.")

    cont_path = Path(summary_path).parent / f"{batch}_contention.json"
    cont = Contention(cont_path, batch)
    cont.doc.update(cores_offered=cores, cores_on_box=n_cores_total,
                    mem_floor_gb=mem_floor_gb,
                    core_busy_fraction_at_start={str(k): round(v, 4)
                                                 for k, v in sorted(frac.items())})
    cont.sample("batch_start", [])

    free_cores = list(cores)
    queue = list(jobs)
    blocked: list[Job] = []
    live: list[Job] = []
    last_sample = time.monotonic()

    while queue or live:
        # ---- guard 3: memory, checked immediately before each launch --------
        while queue:
            job = queue[0]
            if len(free_cores) < job.ranks:
                break
            avail = mem_available_gb()
            if avail - job.mem_gb < mem_floor_gb:
                job.blocked_attempts += 1
                if job.blocked_since is None:
                    job.blocked_since = time.monotonic()
                waited = time.monotonic() - job.blocked_since
                job.note = (f"memory guard: MemAvailable {avail:.2f} GB minus "
                            f"estimate {job.mem_gb:.2f} GB would fall below the "
                            f"{mem_floor_gb:.2f} GB floor "
                            f"({job.blocked_attempts} attempts over {waited:.0f} s)")
                if waited >= mem_wait_s:
                    blocked.append(queue.pop(0))
                    continue
                break
            queue.pop(0)
            mine = [free_cores.pop(0) for _ in range(job.ranks)]
            _launch(job, mine, cont, batch, log)
            live.append(job)

        if not live:
            if queue:
                time.sleep(min(1.0, sample_interval_s))
                continue
            break

        time.sleep(0.5)
        now = time.monotonic()
        held = [j.name for j in live if j.cap_exceeded]

        # ---- guard 4: contention sampling -----------------------------------
        if now - last_sample >= sample_interval_s:
            cont.sample("periodic", [j.name for j in live], held)
            last_sample = now

        # ---- guard 2: the cap, as report-and-hold ---------------------------
        for job in list(live):
            rc = job.proc.poll()
            if rc is None:
                cm = job.core_minutes(now)
                if cm > job.cap and not job.cap_exceeded:
                    job.cap_exceeded = True
                    job.cap_exceeded_utc = _utc()
                    job.cap_exceeded_at = round(cm, 4)
                    job.note = (f"CAP EXCEEDED at {cm:.3f} core-min against a "
                                f"{job.cap:.3f} core-min cap. cap_action="
                                f"{job.cap_action}.")
                    if job.cap_action == CAP_ACTION_HOLD:
                        log(f"[{batch}] {job.name}: CAP EXCEEDED at {cm:.3f} "
                            f"core-min (cap {job.cap:.3f}). REPORTING AND "
                            "HOLDING -- the job keeps running and the supervisor "
                            "decides whether to extend it by amendment or stop "
                            "it. This is not a kill (Sanaa 2026-08-25).")
                        # write the breach to disk NOW: a hold nobody can see is
                        # not a report
                        write_record(job.cwd, _live_record(job, None, now,
                                                           "HELD-OVER-CAP"))
                    else:
                        log(f"[{batch}] {job.name}: CAP EXCEEDED at {cm:.3f} "
                            f"core-min -- cap_action=kill, stopping the run.")
                        _stop(job, kill_grace_s)
                        job.stopped_on_runaway = True
                        rc = job.proc.poll()
                if (rc is None and job.runaway_multiple > 0
                        and cm > job.cap * job.runaway_multiple):
                    log(f"[{batch}] {job.name}: RUNAWAY CEILING at {cm:.3f} "
                        f"core-min ({job.runaway_multiple:g}x the "
                        f"{job.cap:.3f} cap) -- stopping. This is BOX "
                        "PROTECTION, not a budget gate: the box is shared and a "
                        "looping job takes down other teams' runs.")
                    _stop(job, kill_grace_s)
                    job.stopped_on_runaway = True
                    job.note += (f" RUNAWAY CEILING fired at {cm:.3f} core-min "
                                 f"({job.runaway_multiple:g}x cap); stopped for "
                                 "box protection, not for budget.")
                    rc = job.proc.poll()
                if rc is None:
                    continue
            _finish(job, rc, cont, batch, log)
            live.remove(job)
            free_cores.extend(job.cores)

    for job in blocked + queue:
        note = job.note or "never reached before the batch ended"
        write_record(job.cwd, blank_record(job, STATE_BLOCKED, note))
        log(f"[{batch}] {job.name}: BLOCKED -- {note}")

    cont.sample("batch_end", [])

    # ---- the summary is built by RE-READING the records from disk ----------
    rows = [read_record(j.cwd) for j in jobs]
    summary = {
        "batch": batch, "finished_utc": _utc(),
        "cores_offered": cores, "cores_on_box": n_cores_total,
        "concurrency_asked": concurrency, "cores_used": len(cores),
        "narrowed_for_contention": narrowed, "mem_floor_gb": mem_floor_gb,
        "core_minutes_total": round(sum(r["core_minutes"] or 0.0 for r in rows), 4),
        "cap_exceeded_names": sorted(r["name"] for r in rows if r["cap_exceeded"]),
        "contention": contention_summary(cont.doc, n_cores_total),
        "contention_artifact": str(cont_path),
        "rows": rows,
        "read_back_from": [str(Path(j.cwd) / RECORD_NAME) for j in jobs],
    }
    Path(summary_path).parent.mkdir(parents=True, exist_ok=True)
    Path(summary_path).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def _live_record(job, rc, now, state):
    wall = now - job.t0
    return make_record(
        name=job.name, cwd=str(job.cwd), argv=list(job.argv), log=job.log,
        ranks=job.ranks, cores=list(job.cores), cpus_allowed=job.cpus_allowed,
        cpus_allowed_verified=job.cpus_allowed_verified,
        foam_case=(str(job.foam_case) if job.foam_case else None),
        core_minute_cap=job.cap, cap_action=job.cap_action,
        cap_exceeded=job.cap_exceeded, cap_exceeded_utc=job.cap_exceeded_utc,
        cap_exceeded_at_core_minutes=job.cap_exceeded_at,
        runaway_multiple=job.runaway_multiple,
        stopped_on_runaway=job.stopped_on_runaway, mem_estimate_gb=job.mem_gb,
        state=state, rc=rc, wall_s=round(wall, 3),
        core_minutes=round(wall * job.ranks / 60.0, 4),
        started_utc=job.started_utc, finished_utc=_utc(), note=job.note)


def _launch(job: Job, cores: list[int], cont: Contention, batch: str, log):
    # ---- guard 5: the fresh-case launch guard (CLAUDE.md rule 4) -----------
    if job.foam_case is not None and not job.allow_existing_times:
        stale = existing_time_dirs(job.foam_case)
        if stale:
            raise Refuse(
                f"job {job.name!r}: OpenFOAM case {job.foam_case} ALREADY HOLDS "
                f"time directories {stale}. CLAUDE.md rule 4's guard refuses a "
                "case where 0/ or a time directory already exists: the age "
                "guard dates a run by requiring every field at endTime to be "
                "NEWER than the case's own 0/ field, and a pre-existing 0/ "
                "destroys that dating before the solver starts. Set "
                "allow_existing_times: true, with the reason stated in the job "
                "spec, only for a deliberate restart.")
    if threading.active_count() != 1:
        raise Refuse(
            f"{threading.active_count()} threads are live in this process; "
            "child-side sched_setaffinity via preexec_fn is only safe "
            "single-threaded, and the launcher refuses rather than pinning "
            "unreliably.")
    job.cwd.mkdir(parents=True, exist_ok=True)
    argv = ["taskset", "-c", ",".join(str(c) for c in cores), *job.argv]
    job.cores = list(cores)
    job.t0 = time.monotonic()
    job.started_utc = _utc()
    with (job.cwd / job.log).open("w") as fh:
        job.proc = subprocess.Popen(argv, cwd=str(job.cwd), stdout=fh,
                                    stderr=subprocess.STDOUT,
                                    start_new_session=True,
                                    preexec_fn=_preexec(cores))
    job.cpus_allowed, job.cpus_allowed_verified = verify_pinning(
        job.proc.pid, cores)
    if not job.cpus_allowed_verified and job.proc.poll() is None:
        seen = job.cpus_allowed
        pid = job.proc.pid
        _stop(job, 5.0)
        raise Refuse(
            f"job {job.name!r}: the kernel does not confirm the pinning. Asked "
            f"for cores {cores}; /proc/{pid}/status Cpus_allowed_list read "
            f"{seen!r} and never narrowed within the poll window. A pinning "
            "never shown to bind is not a pinning, so the job is STOPPED "
            "rather than run unpinned.")
    cont.sample(f"launch:{job.name}", [job.name])
    log(f"[{batch}] {job.name}: launched on core(s) {cores} "
        f"(Cpus_allowed_list={job.cpus_allowed}, kernel-verified="
        f"{job.cpus_allowed_verified}) ranks={job.ranks} "
        f"cap {job.cap:.3f} core-min, cap_action={job.cap_action}")


def _stop(job: Job, grace_s: float):
    try:
        os.killpg(os.getpgid(job.proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return
    deadline = time.monotonic() + grace_s
    while time.monotonic() < deadline:
        if job.proc.poll() is not None:
            return
        time.sleep(0.2)
    try:
        os.killpg(os.getpgid(job.proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        job.proc.wait(timeout=grace_s)
    except subprocess.TimeoutExpired:
        pass


def _finish(job: Job, rc: int, cont: Contention, batch: str, log):
    state = STATE_STOPPED if job.stopped_on_runaway else STATE_DONE
    rec = _live_record(job, rc, time.monotonic(), state)
    write_record(job.cwd, rec)
    cont.sample(f"finish:{job.name}", [])
    log(f"[{batch}] {job.name}: {state} rc={rc} wall={rec['wall_s']:.1f}s "
        f"core-min={rec['core_minutes']:.3f} (cap {job.cap:.3f}"
        + (", CAP EXCEEDED" if job.cap_exceeded else "") + ")")


def summary_verdict(summary: dict) -> str:
    """A runner verdict in the fixed vocabulary.  It says whether the JOBS RAN,
    and nothing whatever about whether their numbers are right -- that is the
    comparator's business and this runner has no opinion on it.

    A CRASH AND A RUNAWAY STOP ARE ``NOT A RESULT``, NEVER ``GATE FAIL``.
    Corrected 2026-08-25 on cfd-supervisor's ruling, and the reasoning is worth
    keeping because the original code got it backwards in the ONE direction the
    lab forbids.

    ``GATE FAIL`` asserts that a gate WAS evaluated and the value MISSED its
    band.  A job that crashed, or that the runaway ceiling stopped, produced NO
    VALUE to miss with.  Labelling it ``GATE FAIL`` promotes an execution
    failure into an evaluated gate failure -- a STRONGER and more
    informative-sounding claim than the evidence supports.  Standing rule 5
    fixes the direction of travel: the gate may turn a PASS or a GATE FAIL
    *into* ``NOT A RESULT``, NEVER the reverse.  The original mapping ran the
    reverse.

    It would also have put this instrument at odds with cfd's own graded
    records: F12 rung 1, DPW8_V2 L4 arm A and F4 all closed ``NOT A RESULT`` on
    exactly this ground -- the run did not complete, so there is no number.

    NOTE: a job that merely EXCEEDED its cap and finished is not a failure here.
    Under the 2026-08-25 directive the cap is a runaway guard, so the breach is
    reported (``cap_exceeded_names``) for the supervisor to rule on, and does not
    by itself change this verdict at all.

    ``GATE FAIL`` is unreachable from this function BY DESIGN and that is not an
    omission: this runner has no bands, so it can never be the thing that
    decides a value missed one."""
    rows = summary["rows"]
    if any(r["state"] == STATE_BLOCKED for r in rows):
        return "BLOCKED"
    if any(r["state"] == STATE_STOPPED for r in rows):
        return "NOT A RESULT"
    if any(r["rc"] != 0 for r in rows):
        return "NOT A RESULT"
    return "PASS"


VERDICT_EXIT = {"PASS": EXIT_OK, "GATE FAIL": EXIT_GATE_FAIL,
                "NOT A RESULT": EXIT_NOT_A_RESULT, "BLOCKED": EXIT_BLOCKED}


# ---------------------------------------------------------------------------
# selftest -- every guard shown able to FIRE and able to stay QUIET
# ---------------------------------------------------------------------------
_CHECKS = []


def _check(name, ok, detail=""):
    _CHECKS.append((name, bool(ok)))
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


def _quiet(*_a, **_k):
    return None


def selftest() -> int:
    root = Path(tempfile.mkdtemp(prefix="parallel_batch_selftest_"))
    try:
        # (i) a plain batch: three trivial jobs, records read back from disk
        jobs = [{"name": f"j{i}", "cwd": str(root / "plain" / f"j{i}"),
                 "argv": ["sh", "-c", "sleep 1; echo hi"],
                 "core_minute_cap": 5.0, "mem_estimate_gb": 0.01}
                for i in range(3)]
        s = run_batch({"batch": "plain", "jobs": jobs}, concurrency=3,
                      mem_floor_gb=0.1, core_busy_max=0.99, sample_interval_s=1.0,
                      kill_grace_s=2.0, core_probe_s=0.5, mem_wait_s=2.0,
                      summary_path=root / "plain" / "summary.json", log=_quiet)
        _check("three trivial jobs all rc 0", all(r["rc"] == 0 for r in s["rows"]))
        _check("runner verdict PASS", summary_verdict(s) == "PASS", summary_verdict(s))
        _check("core-minutes recorded and positive",
               all(r["core_minutes"] > 0 for r in s["rows"]),
               str([r["core_minutes"] for r in s["rows"]]))

        # (ii) guard 1 SHOWN TO BIND -- the kernel agrees each job was pinned
        pinned = [r["cpus_allowed"] for r in s["rows"]]
        _check("guard 1: kernel confirms one-core pinning per job",
               all(p is not None and len(parse_cpu_list(p)) == 1 for p in pinned),
               f"Cpus_allowed_list = {pinned}")
        _check("guard 1: the pinning is KERNEL-VERIFIED, not assumed",
               all(r["cpus_allowed_verified"] for r in s["rows"]),
               "verify_pinning polls /proc/<pid>/status until the mask EQUALS "
               "the requested cores; one sample at Popen-return raced the "
               "affinity syscall and read 0-15")
        _check("guard 1: each job got a DIFFERENT core (no oversubscription)",
               len(set(pinned)) == len(pinned), f"{pinned}")

        # (iii) guard 4 wrote a contention file with real load averages
        cdoc = json.loads(Path(s["contention_artifact"]).read_text())
        _check("guard 4: contention file carries load-average samples",
               len(cdoc["samples"]) >= 2 and all("load1" in x for x in cdoc["samples"]),
               f"{len(cdoc['samples'])} samples")
        _check("guard 4: contention percentage computed and disclosed",
               s["contention"]["contention_pct"] is not None,
               f"{s['contention']['contention_pct']} % over "
               f"{s['contention']['samples']} samples")

        # (iv) guard 2 REPORTS-AND-HOLDS: over cap, still running, breach on disk
        d = root / "held" / "slow"
        s2 = run_batch({"batch": "held", "jobs": [
            {"name": "slow", "cwd": str(d), "argv": ["sh", "-c", "sleep 4"],
             "core_minute_cap": 1.0 / 60.0, "mem_estimate_gb": 0.01,
             "cap_action": CAP_ACTION_HOLD, "runaway_multiple": 0}]},
            concurrency=1, mem_floor_gb=0.1, core_busy_max=0.99,
            sample_interval_s=0.5, kill_grace_s=2.0, core_probe_s=0.5,
            mem_wait_s=2.0, summary_path=root / "held" / "summary.json", log=_quiet)
        r = s2["rows"][0]
        _check("guard 2 FIRES: the cap breach is detected and stamped",
               r["cap_exceeded"] and r["cap_exceeded_utc"] is not None,
               f"exceeded at {r['cap_exceeded_at_core_minutes']} core-min "
               f"vs cap {r['core_minute_cap']:.4f}")
        _check("guard 2 HOLDS: the job was NOT killed and ran to completion",
               r["state"] == STATE_DONE and r["rc"] == 0
               and not r["stopped_on_runaway"],
               f"state={r['state']} rc={r['rc']} wall={r['wall_s']}s -- "
               "report-and-hold, per Sanaa 2026-08-25")
        _check("guard 2 HOLD: a cap breach alone is not a GATE FAIL",
               summary_verdict(s2) == "PASS"
               and s2["cap_exceeded_names"] == ["slow"],
               f"verdict={summary_verdict(s2)} exceeded={s2['cap_exceeded_names']}")

        # (v) the literal rule-12 path still works when a caller asks for it
        d = root / "killed" / "slow"
        s2b = run_batch({"batch": "killed", "jobs": [
            {"name": "slow", "cwd": str(d), "argv": ["sh", "-c", "sleep 600"],
             "core_minute_cap": 1.0 / 60.0, "mem_estimate_gb": 0.01,
             "cap_action": CAP_ACTION_KILL, "runaway_multiple": 0}]},
            concurrency=1, mem_floor_gb=0.1, core_busy_max=0.99,
            sample_interval_s=0.5, kill_grace_s=2.0, core_probe_s=0.5,
            mem_wait_s=2.0, summary_path=root / "killed" / "summary.json", log=_quiet)
        rb = s2b["rows"][0]
        _check("cap_action=kill still stops the run (literal CLAUDE.md rule 12)",
               rb["stopped_on_runaway"] and rb["state"] == STATE_STOPPED
               and rb["wall_s"] < 30.0,
               f"state={rb['state']} wall={rb['wall_s']}s")

        # (vi) the runaway ceiling fires -- box protection, not budget
        d = root / "runaway" / "loop"
        s2c = run_batch({"batch": "runaway", "jobs": [
            {"name": "loop", "cwd": str(d), "argv": ["sh", "-c", "sleep 600"],
             "core_minute_cap": 0.5 / 60.0, "mem_estimate_gb": 0.01,
             "cap_action": CAP_ACTION_HOLD, "runaway_multiple": 4.0}]},
            concurrency=1, mem_floor_gb=0.1, core_busy_max=0.99,
            sample_interval_s=0.5, kill_grace_s=2.0, core_probe_s=0.5,
            mem_wait_s=2.0, summary_path=root / "runaway" / "summary.json", log=_quiet)
        rc_ = s2c["rows"][0]
        _check("runaway ceiling FIRES at the registered multiple",
               rc_["stopped_on_runaway"] and rc_["state"] == STATE_STOPPED
               and rc_["cap_exceeded"] and rc_["wall_s"] < 60.0,
               f"stopped at {rc_['core_minutes']} core-min, ceiling "
               f"{rc_['runaway_multiple']}x{rc_['core_minute_cap']:.5f}")
        _check("runaway ceiling stays QUIET when disabled (runaway_multiple 0)",
               not r["stopped_on_runaway"], "the held job above ran to completion")

        # (vi-a) THE VERDICT VOCABULARY.  A crash and a runaway stop are
        # NOT A RESULT, never GATE FAIL: no gate was evaluated, so no value
        # exists to have missed a band.  Standing rule 5 permits a gate to turn
        # a PASS or GATE FAIL *into* NOT A RESULT and NEVER the reverse; the
        # original mapping ran the reverse and this is the corrected branch.
        # Each check below is paired with a MUTATION control that flips the one
        # field the branch keys on, so the check is shown able to give the
        # OTHER answer.  A check that cannot change its mind is not a check.
        d = root / "crash" / "boom"
        s_cr = run_batch({"batch": "crash", "jobs": [
            {"name": "boom", "cwd": str(d), "argv": ["sh", "-c", "exit 7"],
             "core_minute_cap": 1.0, "mem_estimate_gb": 0.01}]},
            concurrency=1, mem_floor_gb=0.1, core_busy_max=0.99,
            sample_interval_s=0.5, kill_grace_s=2.0, core_probe_s=0.5,
            mem_wait_s=2.0, summary_path=root / "crash" / "summary.json",
            log=_quiet)
        _check("a nonzero rc is NOT A RESULT, never GATE FAIL",
               s_cr["rows"][0]["rc"] == 7
               and summary_verdict(s_cr) == "NOT A RESULT",
               f"rc={s_cr['rows'][0]['rc']} verdict={summary_verdict(s_cr)} -- "
               "a crashed job produced no value to miss a band with")
        mut = json.loads(json.dumps(s_cr))
        mut["rows"][0]["rc"] = 0
        _check("MUTATION: the rc branch flips to PASS when rc becomes 0",
               summary_verdict(mut) == "PASS",
               f"mutated rc 7 -> 0, verdict {summary_verdict(s_cr)!r} -> "
               f"{summary_verdict(mut)!r}: the branch reads rc, it is not a "
               "constant")
        _check("a runaway stop is NOT A RESULT, never GATE FAIL",
               s2c["rows"][0]["state"] == STATE_STOPPED
               and summary_verdict(s2c) == "NOT A RESULT",
               f"state={s2c['rows'][0]['state']} "
               f"verdict={summary_verdict(s2c)} -- the ceiling stopped it, so "
               "no gate was ever evaluated")
        mut2 = json.loads(json.dumps(s2c))
        mut2["rows"][0]["state"] = STATE_DONE
        mut2["rows"][0]["rc"] = 0
        _check("MUTATION: the STOPPED branch flips to PASS when the state does",
               summary_verdict(mut2) == "PASS",
               f"mutated STOPPED -> DONE, verdict {summary_verdict(s2c)!r} -> "
               f"{summary_verdict(mut2)!r}")
        _check("GATE FAIL is UNREACHABLE from this runner, by design",
               all(summary_verdict(x) != "GATE FAIL"
                   for x in (s, s2, s2b, s2c, s_cr, mut, mut2)),
               "the runner has no bands, so it can never be the thing that "
               "decides a value missed one -- that is the comparator's business")
        _check("every verdict maps to a DISTINCT exit code",
               len(set(VERDICT_EXIT.values())) == len(VERDICT_EXIT)
               and VERDICT_EXIT["PASS"] == EXIT_OK
               and VERDICT_EXIT["NOT A RESULT"] == EXIT_NOT_A_RESULT
               and VERDICT_EXIT["BLOCKED"] == EXIT_BLOCKED
               and EXIT_REFUSE not in VERDICT_EXIT.values(),
               f"{VERDICT_EXIT} -- a caller that conflates BLOCKED, NOT A "
               "RESULT and GATE FAIL into one code cannot tell a run that "
               "never started from one that produced a wrong number")

        # (vi-b) guard 5 FIRES: a case that already holds 0/ is not launched
        (root / "fresh" / "case" / "0").mkdir(parents=True)
        fired = None
        try:
            run_batch({"batch": "fresh", "jobs": [
                {"name": "stale", "cwd": str(root / "fresh"),
                 "argv": ["sh", "-c", "true"], "foam_case": "case",
                 "core_minute_cap": 1.0, "mem_estimate_gb": 0.01}]},
                concurrency=1, mem_floor_gb=0.1, core_busy_max=0.99,
                sample_interval_s=0.5, kill_grace_s=2.0, core_probe_s=0.5,
                mem_wait_s=2.0, summary_path=root / "fresh" / "summary.json",
                log=_quiet)
        except Refuse as exc:
            fired = str(exc)
        _check("guard 5 FIRES: a case that already holds 0/ is REFUSED",
               fired is not None and "'0'" in (fired or ""),
               "CLAUDE.md rule 4's age guard is destroyed by a pre-existing 0/")
        # and it sees a NON-ZERO time directory too, not only the literal 0/
        (root / "fresh2" / "case" / "0.5").mkdir(parents=True)
        fired2 = None
        try:
            run_batch({"batch": "fresh2", "jobs": [
                {"name": "stale2", "cwd": str(root / "fresh2"),
                 "argv": ["sh", "-c", "true"], "foam_case": "case",
                 "core_minute_cap": 1.0, "mem_estimate_gb": 0.01}]},
                concurrency=1, mem_floor_gb=0.1, core_busy_max=0.99,
                sample_interval_s=0.5, kill_grace_s=2.0, core_probe_s=0.5,
                mem_wait_s=2.0, summary_path=root / "fresh2" / "summary.json",
                log=_quiet)
        except Refuse as exc:
            fired2 = str(exc)
        _check("guard 5 sees a non-zero time dir, not only 0/",
               fired2 is not None and "0.5" in (fired2 or ""),
               "a guard that matches only the literal string 0 is not the guard")
        # (vi-c) guard 5 stays QUIET on a genuinely fresh case
        (root / "clean" / "case").mkdir(parents=True)
        sq = run_batch({"batch": "clean", "jobs": [
            {"name": "fresh", "cwd": str(root / "clean"),
             "argv": ["sh", "-c", "sleep 1"], "foam_case": "case",
             "core_minute_cap": 1.0, "mem_estimate_gb": 0.01}]},
            concurrency=1, mem_floor_gb=0.1, core_busy_max=0.99,
            sample_interval_s=0.5, kill_grace_s=2.0, core_probe_s=0.5,
            mem_wait_s=2.0, summary_path=root / "clean" / "summary.json",
            log=_quiet)
        _check("guard 5 stays QUIET on a case with no time directory",
               sq["rows"][0]["rc"] == 0
               and sq["rows"][0]["foam_case"] is not None,
               f"foam_case recorded as {sq['rows'][0]['foam_case']}")
        # (vi-d) the bypass exists, is explicit, and works
        sb = run_batch({"batch": "restart", "jobs": [
            {"name": "restart", "cwd": str(root / "fresh"),
             "argv": ["sh", "-c", "sleep 1"], "foam_case": "case",
             "allow_existing_times": True,
             "core_minute_cap": 1.0, "mem_estimate_gb": 0.01}]},
            concurrency=1, mem_floor_gb=0.1, core_busy_max=0.99,
            sample_interval_s=0.5, kill_grace_s=2.0, core_probe_s=0.5,
            mem_wait_s=2.0, summary_path=root / "fresh" / "summary2.json",
            log=_quiet)
        _check("guard 5 bypass is explicit and works (deliberate restart)",
               sb["rows"][0]["rc"] == 0,
               "allow_existing_times: true, reason stated in the job spec")

        # (vii) guard 3 FIRES: an impossible floor blocks the launch entirely
        d = root / "mem" / "big"
        s3 = run_batch({"batch": "mem", "jobs": [
            {"name": "big", "cwd": str(d), "argv": ["sh", "-c", "echo ran > RAN"],
             "core_minute_cap": 1.0, "mem_estimate_gb": 1.0}]},
            concurrency=1, mem_floor_gb=1.0e9, core_busy_max=0.99,
            sample_interval_s=0.5, kill_grace_s=2.0, core_probe_s=0.5,
            mem_wait_s=1.0, summary_path=root / "mem" / "summary.json", log=_quiet)
        r3 = s3["rows"][0]
        _check("guard 3 FIRES: job never launched under an impossible floor",
               r3["state"] == STATE_BLOCKED and not (d / "RAN").exists(),
               f"state={r3['state']}")
        _check("guard 3: a blocked batch reports BLOCKED, not GATE FAIL",
               summary_verdict(s3) == "BLOCKED", summary_verdict(s3))
        _check("guard 3 stays QUIET at a floor the box can meet",
               all(x["state"] == STATE_DONE for x in s["rows"]))
        _check("guard 3's blocked record has the FULL key set (L-322 shape)",
               set(r3) == set(RECORD_KEYS),
               "a PENDING/BLOCKED branch that omits a key the summary reads is "
               "the defect check_grader_self_blindness probe A hunts")

        # (viii) THE READ-BACK CONTROL (standing rule 3).  Mutate a record ON
        # DISK after the job finished; the reader must see the change.  Every
        # core-minute figure this runner reports rests on this read path.
        target = Path(s["rows"][0]["cwd"])
        doc = json.loads((target / RECORD_NAME).read_text())
        before = doc["core_minutes"]
        doc["core_minutes"] = before + PLANT
        (target / RECORD_NAME).write_text(json.dumps(doc, indent=2, sort_keys=True))
        seen = read_record(target)["core_minutes"]
        _check("read-back control: the reader SEES a plant made on disk",
               abs((seen - before) - PLANT) < 1e-12,
               f"planted {PLANT}, reader saw {seen - before:.6g}")

        # (ix) the read path REFUSES rather than degrading when a record vanishes
        (target / RECORD_NAME).unlink()
        try:
            read_record(target)
            _check("read path REFUSES on a missing record", False, "it did not refuse")
        except Refuse:
            _check("read path REFUSES on a missing record", True,
                   "exit 2, not a partial row")

        # (x) a job with no cap is refused outright -- costing is UNCHANGED
        try:
            Job({"name": "x", "cwd": str(root), "argv": ["true"]})
            _check("a job with no core-minute cap is REFUSED", False, "accepted")
        except Refuse:
            _check("a job with no core-minute cap is REFUSED", True,
                   "costing survives the lifted budget constraint")

        # (xi) concurrency 0 means 'as many as the free cores allow'
        jobs = [{"name": f"a{i}", "cwd": str(root / "auto" / f"a{i}"),
                 "argv": ["sh", "-c", "sleep 1"], "core_minute_cap": 5.0,
                 "mem_estimate_gb": 0.01} for i in range(2)]
        s4 = run_batch({"batch": "auto", "jobs": jobs}, concurrency=0,
                       mem_floor_gb=0.1, core_busy_max=0.99, sample_interval_s=1.0,
                       kill_grace_s=2.0, core_probe_s=0.5, mem_wait_s=2.0,
                       summary_path=root / "auto" / "summary.json", log=_quiet)
        _check("concurrency 0 takes every free core, not a fixed 8-12",
               s4["cores_used"] >= 2 and summary_verdict(s4) == "PASS",
               f"{s4['cores_used']} cores of {s4['cores_on_box']} on the box")

    finally:
        shutil.rmtree(root, ignore_errors=True)

    bad = [n for n, ok in _CHECKS if not ok]
    print(f"\n  {len(_CHECKS) - len(bad)}/{len(_CHECKS)} checks passed"
          + ("" if not bad else f"   FAILED: {bad}"))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("manifest", nargs="?", help="JSON manifest of jobs")
    ap.add_argument("--jobs", type=int, default=0,
                    help="max concurrent cases; 0 (default) = as many as the "
                         "free cores allow. Concurrency is bounded by cores and "
                         "memory, not by a number.")
    ap.add_argument("--mem-floor-gb", type=float, default=DEFAULT_MEM_FLOOR_GB)
    ap.add_argument("--core-busy-max", type=float, default=DEFAULT_CORE_BUSY_MAX)
    ap.add_argument("--sample-interval-s", type=float, default=DEFAULT_SAMPLE_INTERVAL_S)
    ap.add_argument("--kill-grace-s", type=float, default=DEFAULT_KILL_GRACE_S)
    ap.add_argument("--core-probe-s", type=float, default=DEFAULT_CORE_PROBE_S)
    ap.add_argument("--mem-wait-s", type=float, default=DEFAULT_MEM_WAIT_S)
    ap.add_argument("--cap-action", choices=(CAP_ACTION_HOLD, CAP_ACTION_KILL),
                    default=CAP_ACTION_HOLD,
                    help="hold (default): report the breach and keep running, "
                         "supervisor decides. kill: the literal CLAUDE.md rule-12 "
                         "behaviour.")
    ap.add_argument("--runaway-multiple", type=float, default=DEFAULT_RUNAWAY_MULTIPLE,
                    help="stop a job past this multiple of its cap. BOX "
                         "PROTECTION, not budget. 0 disables.")
    ap.add_argument("--summary", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    if not a.manifest:
        ap.error("a manifest is required unless --selftest")
    try:
        manifest = json.loads(Path(a.manifest).read_text())
        summary_path = Path(a.summary or Path(a.manifest).with_suffix(".summary.json"))
        s = run_batch(
            manifest,
            concurrency=int(manifest.get("jobs_concurrent", a.jobs)),
            mem_floor_gb=float(manifest.get("mem_floor_gb", a.mem_floor_gb)),
            core_busy_max=a.core_busy_max,
            sample_interval_s=float(manifest.get("sample_interval_s",
                                                 a.sample_interval_s)),
            kill_grace_s=a.kill_grace_s, core_probe_s=a.core_probe_s,
            mem_wait_s=a.mem_wait_s, summary_path=summary_path,
            defaults={"cap_action": manifest.get("cap_action", a.cap_action),
                      "runaway_multiple": manifest.get("runaway_multiple",
                                                       a.runaway_multiple)})
    except Refuse as exc:
        print(f"REFUSE: {exc}", file=sys.stderr)
        return EXIT_REFUSE
    v = summary_verdict(s)
    print(f"\n{s['batch']}: {v}   {s['core_minutes_total']:.3f} core-min total, "
          f"contention {s['contention']['contention_pct']} % measured over "
          f"{s['contention']['samples']} samples")
    if s["cap_exceeded_names"]:
        print(f"  CAP EXCEEDED (held, not killed -- supervisor decides): "
              f"{s['cap_exceeded_names']}")
    print(f"  summary: {summary_path}\n  contention: {s['contention_artifact']}")
    if v not in VERDICT_EXIT:
        print(f"REFUSE: verdict {v!r} is not in the fixed vocabulary",
              file=sys.stderr)
        return EXIT_REFUSE
    return VERDICT_EXIT[v]


if __name__ == "__main__":
    sys.exit(main())
