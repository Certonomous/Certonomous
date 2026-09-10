#!/usr/bin/env python3
"""RC4 propagation RUNNER -- the producer that satisfies section 8's clauses 1-3,
and the campaign wall accumulator section 9 registers as its binding control.

Registration: cases/RANS_LES_closure_models/RC4_kaandorp_propagation_repair/
PREREGISTRATION.md -- section 8 (strict completion, clauses 1, 2, 3 and 5),
section 9 / 9.2 (ranks = 1, the per-solve `timeout 3600`, and the campaign-level
wall accumulator that stops the campaign at 21,000 wall s), section 10 (the
anti-gaming register: model, formulation and ranks FIXED), section 11 (this
module's registered job and refusals) and AMENDMENT A2 (which registers it).

WHY THIS MODULE EXISTS -- the defect it closes
----------------------------------------------
RC4's section 8 clauses 1-3 are delegated to `r4_lib.solve_complete`, which
requires a file named `rc` in the case directory and a log named `log.solve`
(r4_lib.py:495, :508-512).  RC4 registered NO RUNNER, so the only producer
available was the predecessor's `Kaandorp2020_TBRF/aposteriori/run_lane.py`,
which writes `log.run` and keeps the return code in `results.json` only
(run_lane.py:157-158).  Measured on the 31 preserved cases of that producer:
a file named `rc` present 0 of 31, a log named `log.solve` present 0 of 31, and
`rc4_score.completion` SATISFIABLE on 0 of 31.  Reader control: the identical
readers find `rc` present 60 of 60 and `log.solve` 60 of 60 on the sibling
population `/home/ubuntu/closure-data/r4/aposteriori`, so those zeros are REAL
absences and not a blind reader.

A completion clause no real producer can satisfy is not strict, it is BROKEN,
and it drives the completion count to zero independently of physics
(`docs/closure/CLAUSE_SATISFIABILITY_AUDIT.md`, finding B; the same shape as the
R5D defect at `grade_r5d.py:296`).  This module is the STRICTER of the two
repairs: the clause is left exactly as registered, and the PRODUCER is made to
emit what the clause reads.  Nothing in section 8 is weakened, and no bar moves.

WHAT IT WRITES, AND WHY EACH CHANNEL IS THERE
---------------------------------------------
    <case>/log.solve   the solver's stdout+stderr, under the name section 8's
                       clause 5 reader and `r4_lib.solve_complete` both use
    <case>/rc          the solver's REAL exit status, captured by the shell at
                       the moment of exit (`echo $? > rc`), never inferred from
                       a parent process -- L-`setsid parent returns zero`: a
                       wrapper's own return code is 0 for every outcome, so the
                       recorded rc is read back FROM DISK and refused if absent

THE ACCUMULATOR IS THE BINDING CONTROL (section 9.2), AND IT NOW EXISTS
----------------------------------------------------------------------
Section 9.2 registers "a campaign-level wall accumulator that stops the campaign
at 21,000 wall s at ranks 1 (= 350 core-min), checked before each solve
launches", and states why: "9 solves plus an extraction at 3,600 s of per-solve
timeout would otherwise permit 36,000 s."  `build_rc4_cases.CAMPAIGN_WALL_CAP_S`
carried that number as a module constant with NO CODE READING IT.  A registered
cost control that nothing enforces is not a control.  Here it is enforced two
ways, both strictly inside the registered figures:

  * the effective per-solve timeout is `min(3600, cap - spent)`, so the campaign
    can never exceed 21,000 wall s even if every solve runs to its timeout;
  * a launch with no remaining budget REFUSES.  Rule 12: an overrun stops the
    run, it does not get a new budget.

The ledger is a file under the run root, so it accumulates ACROSS process
invocations -- an accumulator that lives only inside one process caps nothing.

REGISTERED REFUSALS (AMENDMENT A2), every one a sys.exit(2), never an assert:
  * RC4 DRAFT/UNFROZEN,
  * an unregistered case tag or configuration,
  * a case directory absent,
  * `log.solve` or `rc` already present -- a runner never overwrites a previous
    run's own record, because that is how an old answer gets re-dated,
  * the wall ledger unreadable or not a number,
  * no remaining campaign wall budget,
  * `log.solve` absent, or zero bytes, after the solve,
  * `rc` absent after the solve, or not an integer -- a missing exit status is
    NOT `rc = 0` (standing rule 3 applied to the return-code channel),
  * this module's channel names disagreeing with the ones the grader reads.

The last is the guard that would have caught this whole defect class: it refuses
if `LOG_NAME` here is not `rc4_score.LOG_NAME`, and if `RC_NAME` here is not the
name `r4_lib.solve_complete` actually opens.  Producer and reader are checked
against each other in code, not in prose.

A NON-ZERO EXIT IS RECORDED, NOT HIDDEN.  The runner does not refuse on
`rc != 0`; it writes the real code and returns.  Section 8 clause 1 then makes
the row NOT A RESULT at grading, which is where that decision belongs.

NO ast.Assert CARRIES ANY REFUSAL, GUARD, CONTROL OR GATE (section 6.1, L-332 /
D476 section 31.3).  `--selftest` parses this file and requires zero, and is
green under `python3` AND `python3 -O`.

NOTHING IS LAUNCHED WHILE THE REGISTRATION IS DRAFT.  Every entry point calls
`build_rc4_cases.refuse_if_unfrozen()` first.

NO RC2 MODULE IS IMPORTED, CALLED, EDITED OR EXTENDED (section 11).  No file
under `Kaandorp2020_TBRF/aposteriori/` is edited; `run_lane.py` was READ for its
invocation form and is RE-IMPLEMENTED here, which section 6.1 requires anyway
since its guards at :153 and :273 are `assert` statements that `python3 -O`
deletes.
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)
COMMON = os.path.join(CLOSURE, "_common")
R4 = os.path.join(CLOSURE, "R4_sparta_build")
for _p in (HERE, COMMON, R4):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import r4_lib                                                # noqa: E402
import build_rc4_cases as B                                  # noqa: E402
import rc4_extract_R as EX                                   # noqa: E402
import rc4_score as S                                        # noqa: E402

# ---- the channels.  These names are the whole point of this module, and they
# are cross-checked against the reader in `check_channel_names()`.
LOG_NAME = "log.solve"
RC_NAME = "rc"

SOLVER = "simpleFoam"                 # section 10, FIXED; no new solver written
FOAM = "source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1"
LEDGER = "_campaign_wall.json"        # under the run root, so it survives exits

# A real preserved simpleFoam log written by this box, for the selftest's
# real-producer measurement.  ONE NAMED ARTIFACT -- never a glob (grep on this
# box is ugrep and a glob has no defined last member).
REAL_CASE = ("/home/ubuntu/closure-data/aposteriori/kaandorp/"
             "AR_1_Ret_360__TRUTHR")
REAL_LOG = os.path.join(REAL_CASE, "log.run")
REAL_TIME = "788"


def refuse(msg):
    sys.stderr.write("RC4 REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


# --------------------------------------------------------- channel agreement
def check_channel_names():
    """PRODUCER AND READER, CHECKED AGAINST EACH OTHER IN CODE.

    Finding B existed because the log name and the return-code channel this
    runner writes were never compared with the ones the grader opens.  Prose
    cannot hold that invariant; this can.  `RC_NAME` is checked against the
    literal `r4_lib.solve_complete` actually opens, read out of its source.
    """
    if LOG_NAME != S.LOG_NAME:
        refuse("channel drift: this runner writes " + repr(LOG_NAME)
               + " but rc4_score.completion reads " + repr(S.LOG_NAME)
               + ".  This is finding B's exact shape and it is refused here")
    src = open(os.path.abspath(r4_lib.__file__)).read()
    fn = src[src.index("def solve_complete("):]
    fn = fn[:fn.index("\ndef ") if "\ndef " in fn else len(fn)]
    if 'os.path.join(case, "' + LOG_NAME + '")' not in fn:
        refuse("channel drift: r4_lib.solve_complete does not open a log named "
               + repr(LOG_NAME) + "; section 8 clauses 1-3 would be unsatisfiable "
               "by this runner's output")
    if 'os.path.join(case, "' + RC_NAME + '")' not in fn:
        refuse("channel drift: r4_lib.solve_complete does not open a return-code "
               "file named " + repr(RC_NAME) + "; section 8 clause 1 would be "
               "unsatisfiable by this runner's output")
    return {"log_name": LOG_NAME, "rc_name": RC_NAME,
            "grader": "r4_lib.solve_complete + rc4_score.completion",
            "agree": True}


# ------------------------------------------------- the campaign accumulator
def ledger_path(root=B.ROOT):
    return os.path.join(root, LEDGER)


def read_spent(root=B.ROOT):
    """Wall seconds already spent by this campaign, read from disk."""
    p = ledger_path(root)
    if not os.path.exists(p):
        return 0.0, {"entries": []}
    try:
        d = json.load(open(p))
    except Exception as e:                                   # noqa: BLE001
        refuse("the campaign wall ledger " + p + " is unreadable (" + str(e)
               + "); section 9.2's binding control cannot be evaluated and no "
                 "solve may launch on an unknown spend")
    tot = d.get("wall_s_total")
    if not isinstance(tot, (int, float)) or tot < 0:
        refuse("the campaign wall ledger " + p + " carries wall_s_total = "
               + repr(tot) + ", which is not a non-negative number; section "
               "9.2's binding control cannot be evaluated")
    return float(tot), d


def book(root, tag, cfg, wall_s, kind="solve"):
    """Append one spend to the ledger, and write it back to disk."""
    spent, d = read_spent(root)
    d.setdefault("entries", []).append(
        {"tag": tag, "config": cfg, "kind": kind, "wall_s": float(wall_s),
         "ranks": B.RANKS, "core_minutes": float(wall_s) * B.RANKS / 60.0,
         "when": time.strftime("%Y-%m-%dT%H:%M:%S")})
    d["wall_s_total"] = spent + float(wall_s)
    d["core_minutes_total"] = d["wall_s_total"] * B.RANKS / 60.0
    d["cap_wall_s"] = B.CAMPAIGN_WALL_CAP_S
    d["cap_core_minutes"] = B.CAMPAIGN_WALL_CAP_S * B.RANKS / 60.0
    os.makedirs(root, exist_ok=True)
    json.dump(d, open(ledger_path(root), "w"), indent=1)
    return d


def budget_or_refuse(root=B.ROOT, label=""):
    """Section 9.2, checked BEFORE the launch.  Returns the effective timeout.

    The effective timeout is `min(3600, cap - spent)`, so the campaign cannot
    exceed the registered 21,000 wall s even if every solve runs to its limit.
    Neither registered figure is widened; both bind.
    """
    spent, _ = read_spent(root)
    remaining = B.CAMPAIGN_WALL_CAP_S - spent
    if remaining <= 0:
        refuse("section 9.2 campaign wall accumulator: %.1f of the registered "
               "%d wall s (= %.1f of %.1f core-min at ranks %d) is already "
               "spent, so %s does not launch.  Standing rule 12: an overrun "
               "STOPS the campaign; it does not get a new budget"
               % (spent, B.CAMPAIGN_WALL_CAP_S, spent * B.RANKS / 60.0,
                  B.CAMPAIGN_WALL_CAP_S * B.RANKS / 60.0, B.RANKS,
                  label or "the next solve"))
    eff = min(float(B.PER_SOLVE_TIMEOUT_S), float(remaining))
    return {"spent_wall_s": spent, "remaining_wall_s": remaining,
            "effective_timeout_s": int(eff),
            "per_solve_timeout_s": B.PER_SOLVE_TIMEOUT_S,
            "cap_wall_s": B.CAMPAIGN_WALL_CAP_S}


# ------------------------------------------------------------- the invocation
def solver_command(case, timeout_s, program=None):
    """The one shell invocation.  Serial, ranks = 1 (section 9, section 10).

    `program` is injectable so `--selftest` can drive REAL processes -- a real
    replay of a real preserved simpleFoam log, and a real non-zero exit -- and
    measure THIS RUNNER'S recording contract without launching a solve against
    an unfrozen registration.  The redirect, the timeout and the `echo $? > rc`
    are the runner's and are never substituted.
    """
    prog = program if program is not None else (SOLVER + " -case .")
    return (FOAM + "; cd " + case + " && timeout " + str(int(timeout_s)) + " "
            + prog + " > " + LOG_NAME + " 2>&1; echo $? > " + RC_NAME)


def verify_record(case):
    """THE RECORDED CHANNELS, READ BACK FROM DISK.  Returns the raw rc text.

    The wrapper's own return code is deliberately NOT used: a wrapper returns 0
    for every outcome, so a return code that is not on disk is not a
    measurement.  Standing rule 3 applied to the return-code channel -- a zero
    from a channel not shown able to carry a non-zero is not evidence, and a
    MISSING rc is not `rc = 0`.

    Driven directly by `--selftest` in all four failing directions and in the
    passing one, so each refusal is exercised by the guard it names.
    """
    log, rcf = os.path.join(case, LOG_NAME), os.path.join(case, RC_NAME)
    if not os.path.exists(log):
        refuse("the solve wrote no " + LOG_NAME + " in " + case
               + "; section 8 clauses 2, 3 and 5 have nothing to read")
    if os.path.getsize(log) == 0:
        refuse(LOG_NAME + " in " + case + " is ZERO BYTES; a solve that "
               "printed nothing did not run, and an empty log is not a clean one")
    if not os.path.exists(rcf):
        refuse("the solve recorded NO EXIT STATUS at " + rcf
               + ".  A missing rc is not rc = 0 -- standing rule 3 applied to "
                 "the return-code channel: a zero from a channel not shown able "
                 "to carry a non-zero is not evidence")
    raw = open(rcf).read().strip()
    if not re.fullmatch(r"-?[0-9]+", raw):
        refuse("the recorded exit status in " + rcf + " is " + repr(raw)
               + ", which is not an integer; section 8 clause 1 cannot be "
                 "evaluated on it")
    return raw


def run_solve(case, tag=None, cfg=None, root=B.ROOT, check_freeze=True,
              _program=None):
    """Run one propagation solve and RECORD IT so section 8 can read it.

    Returns a record.  REFUSES on every condition A2 registers.
    """
    if check_freeze:
        B.refuse_if_unfrozen()
    check_channel_names()
    if tag is not None and tag not in B.CASES:
        refuse("unregistered case tag: " + str(tag) + " (registered: "
               + ", ".join(sorted(B.CASES)) + ")")
    if cfg is not None and cfg not in B.CONFIGS:
        refuse("unregistered configuration: " + str(cfg) + " (registered: "
               + ", ".join(B.CONFIGS) + ")")
    if not os.path.isdir(case):
        refuse("no case directory to run: " + str(case))
    log, rcf = os.path.join(case, LOG_NAME), os.path.join(case, RC_NAME)
    for p in (log, rcf):
        if os.path.exists(p):
            refuse("the case already carries its own run record at " + p
                   + "; a runner never overwrites one, because that is how an "
                     "old answer gets re-dated past section 8's age guard")
    bud = budget_or_refuse(root, label=str(tag) + "/" + str(cfg))

    t0 = time.time()
    subprocess.run(solver_command(case, bud["effective_timeout_s"], _program),
                   shell=True, executable="/bin/bash")
    wall = round(time.time() - t0, 1)

    raw = verify_record(case)
    book(root, tag, cfg, wall, kind="solve")
    rec = {"case": case, "tag": tag, "config": cfg, "rc": raw,
           "rc_is_zero": raw == "0", "wall_s": wall, "ranks": B.RANKS,
           "core_minutes": wall * B.RANKS / 60.0,
           "log": log, "log_bytes": os.path.getsize(log),
           "budget": bud, "solver": SOLVER if _program is None else "_program",
           "effective_timeout_s": bud["effective_timeout_s"]}
    print("[run] %-14s %-5s rc=%-4s wall=%.1fs (%.2f core-min, ranks %d); "
          "campaign spend now %.1f of %d wall s"
          % (str(tag), str(cfg), raw, wall, rec["core_minutes"], B.RANKS,
             read_spent(root)[0], B.CAMPAIGN_WALL_CAP_S))
    return rec


def run_campaign(root=B.ROOT, tags=None, out_path=None):
    """Run every registered configuration, in the registered order.

    P-1 runs FIRST (section 5), and refuses to let a case be PROPAGATED whose
    extraction cannot reproduce the `k` it came from -- so a T-bR row can never
    be launched on an inadmissible `R`.
    """
    B.refuse_if_unfrozen()
    check_channel_names()
    tags = sorted(tags or B.CASES)
    for t in tags:
        if t not in B.CASES:
            refuse("unregistered case tag: " + str(t))
    pm1 = EX.p1_gate(tags, propagating=set(tags))
    out = {"p_minus_1": pm1, "runs": [], "root": root}
    for tag in tags:
        for cfg in B.CONFIGS:                # N, T-b, T-bR -- registered order
            case = os.path.join(root, tag, cfg)
            if not os.path.isdir(case):
                refuse("section 3's configuration " + cfg + " for " + tag
                       + " has not been built: " + case
                       + ".  build_rc4_cases.py builds it; the runner does not")
            out["runs"].append(run_solve(case, tag, cfg, root,
                                         check_freeze=False))
    spent, ledger = read_spent(root)
    out["campaign_wall_s"] = spent
    out["campaign_core_minutes"] = spent * B.RANKS / 60.0
    out["registered_estimate_core_minutes"] = 140
    out["registered_cap_core_minutes"] = B.CAMPAIGN_WALL_CAP_S * B.RANKS / 60.0
    out["ledger"] = ledger
    if out_path:
        json.dump(out, open(out_path, "w"), indent=1, default=str)
    print("[campaign] %d runs, %.1f wall s = %.2f core-min against a registered "
          "estimate of 140 and a registered cap of %.1f core-min"
          % (len(out["runs"]), spent, out["campaign_core_minutes"],
             out["registered_cap_core_minutes"]))
    return out


# ---------------------------------------------------------------- selftest
def _fires(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except SystemExit as e:
        return int(e.code or 0) == 2
    return False


def _real_producer_case(dst):
    """Assemble a case from the REAL preserved artifacts of one real solve.

    Every byte of the fields is what `simpleFoam` wrote on this box, copied with
    `copy2` so the REAL mtimes carry over and section 8's clause-6 age guard is
    measured against real timestamps rather than synthetic ones.  `log.solve`
    and `rc` are NOT copied: the runner has to produce them, which is the whole
    thing under test.
    """
    os.makedirs(os.path.join(dst, "system"), exist_ok=True)
    shutil.copy2(os.path.join(REAL_CASE, "system", "controlDict"),
                 os.path.join(dst, "system", "controlDict"))
    for sub in ("0", REAL_TIME):
        s, d = os.path.join(REAL_CASE, sub), os.path.join(dst, sub)
        os.makedirs(d, exist_ok=True)
        for f in sorted(os.listdir(s)):
            p = os.path.join(s, f)
            if os.path.isfile(p):
                shutil.copy2(p, os.path.join(d, f))
    return dst


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    note("this runner's channel names agree with the grader's, checked in code",
         check_channel_names()["agree"])
    note("the channel guard FIRES on a log-name drift",
         _fires(_drift_probe, "log.run", RC_NAME))
    note("the channel guard FIRES on a return-code-name drift",
         _fires(_drift_probe, LOG_NAME, "returncode"))
    note("every entry point REFUSES while RC4 is DRAFT/UNFROZEN",
         _fires(B.refuse_if_unfrozen))

    tmp = tempfile.mkdtemp(prefix="rc4_run_selftest_")
    try:
        root = os.path.join(tmp, "root")
        os.makedirs(root)

        # ---- THE REAL-PRODUCER MEASUREMENT, both directions.
        if os.path.exists(REAL_LOG) and os.path.isdir(
                os.path.join(REAL_CASE, REAL_TIME)):
            case = _real_producer_case(os.path.join(root, "REPLAY"))
            rec = run_solve(case, None, None, root, check_freeze=False,
                            _program="cat " + REAL_LOG)
            note("the runner records a REAL process's exit status on disk, "
                 "read back rather than inferred",
                 rec["rc"] == "0" and rec["log_bytes"] == os.path.getsize(
                     REAL_LOG),
                 "rc=%s, %d bytes of real simpleFoam log" % (rec["rc"],
                                                             rec["log_bytes"]))
            okc, reason, info = S.completion(case)
            note("SATISFIED DIRECTION: section 8 clauses 1-6 PASS on this "
                 "runner's output over a REAL simpleFoam log's bytes and REAL "
                 "field mtimes -- the clause finding B measured 0 of 31 on",
                 okc, reason + "; n_exec=%s n_time=%s"
                 % (info.get("n_execution_time"), info.get("n_time_steps")))

            # ---- UNSATISFIED DIRECTION, one channel scrubbed at a time.
            def scrubbed(mutate, label):
                d = os.path.join(root, "SCRUB_" + label)
                shutil.copytree(case, d, symlinks=True)
                mutate(d)
                o, r, _ = S.completion(d)
                return (not o), r

            p, r = scrubbed(lambda d: os.remove(os.path.join(d, RC_NAME)), "rc")
            note("UNSATISFIED DIRECTION: removing the recorded rc makes "
                 "completion FAIL, naming the rc channel", p and "rc" in r, r)
            p, r = scrubbed(lambda d: open(os.path.join(d, RC_NAME), "w")
                            .write("136\n"), "sigfpe")
            note("UNSATISFIED DIRECTION: a recorded rc=136 (SIGFPE) makes "
                 "completion FAIL rather than being smoothed over", p, r)
            p, r = scrubbed(lambda d: os.rename(
                os.path.join(d, LOG_NAME), os.path.join(d, "log.run")), "logname")
            note("UNSATISFIED DIRECTION: renaming log.solve to the "
                 "predecessor's log.run makes completion FAIL -- the log name "
                 "is load-bearing, which is finding B's second limb", p, r)
            p, r = scrubbed(lambda d: os.remove(
                os.path.join(d, REAL_TIME, B.KDEFICIT)), "nokd")
            note("UNSATISFIED DIRECTION: removing kDeficit makes clause 4 FAIL",
                 p and B.KDEFICIT in r, r)
            p, r = scrubbed(lambda d: os.remove(
                os.path.join(d, REAL_TIME, "phi")), "nophi")
            note("UNSATISFIED DIRECTION: removing phi makes clause 4 FAIL",
                 p and "phi" in r, r)

            def age(d):
                t0 = os.path.getmtime(os.path.join(d, "0", "U"))
                for f in B.REQUIRED_FIELDS:
                    q = os.path.join(d, REAL_TIME, f)
                    os.utime(q, (t0 - 60, t0 - 60))
            p, r = scrubbed(age, "age")
            note("UNSATISFIED DIRECTION: back-dating the fields behind 0/U "
                 "makes clause 6's AGE GUARD FIRE", p and "AGE GUARD" in r, r)

            def cut_exec(d):
                q = os.path.join(d, LOG_NAME)
                t = open(q, errors="replace").read()
                open(q, "w").write(t.replace("ExecutionTime", "XxecutionTime", 40))
            p, r = scrubbed(cut_exec, "exec")
            note("UNSATISFIED DIRECTION: scrubbing 40 ExecutionTime lines from "
                 "the real log makes clause 5 FAIL", p and "clause 5" in r, r)

            # ---- the runner refuses to overwrite its own record
            note("the runner REFUSES a case that already carries log.solve/rc",
                 _fires(run_solve, case, None, None, root, False,
                        "cat " + REAL_LOG))

            # ---- a REAL non-zero exit from a REAL process, recorded faithfully
            c2 = _real_producer_case(os.path.join(root, "REALFAIL"))
            r2 = run_solve(c2, None, None, root, check_freeze=False,
                           _program="sh -c 'echo FOAM FATAL ERROR; exit 42'")
            o2, rr2, _ = S.completion(c2)
            note("a REAL non-zero exit is recorded as rc=42, not hidden, and "
                 "completion FAILS on it", r2["rc"] == "42" and not o2, rr2)

            # ---- the timeout channel is real, not decorative, AND the
            # accumulator's shrink actually reaches the launched process: this
            # root is booked to 1 wall s of remaining budget, so the effective
            # timeout is 1 s and a 5 s program is killed by it.
            troot = os.path.join(tmp, "tmoroot")
            os.makedirs(troot)
            book(troot, None, None, B.CAMPAIGN_WALL_CAP_S - 1.0)
            c3 = _real_producer_case(os.path.join(troot, "TIMEOUT"))
            r3 = run_solve(c3, None, None, troot, check_freeze=False,
                           _program="sh -c 'echo starting; sleep 5'")
            note("the SHRUNK budget reaches the launched process: 1 wall s "
                 "remaining gives a 1 s effective timeout, the 5 s program is "
                 "KILLED, rc=124 is recorded and completion FAILS on it",
                 r3["effective_timeout_s"] == 1 and r3["rc"] == "124"
                 and not S.completion(c3)[0],
                 "timeout %ds, rc=%s, wall %.1fs"
                 % (r3["effective_timeout_s"], r3["rc"], r3["wall_s"]))
        else:
            note("the real preserved producer artifacts are on disk for the "
                 "real-producer measurement", False, REAL_LOG)

        # ---- the runner's own refusals
        note("the runner REFUSES an absent case directory",
             _fires(run_solve, os.path.join(tmp, "nope"), None, None, root,
                    False))
        note("the runner REFUSES an unregistered case tag",
             _fires(run_solve, os.path.join(tmp, "nope"), "NOT_A_CASE", "N",
                    root, False))
        note("the runner REFUSES an unregistered configuration",
             _fires(run_solve, os.path.join(tmp, "nope"), "AR_1_Ret_360",
                    "T-bRR", root, False))
        cz = os.path.join(root, "ZEROLOG")
        os.makedirs(cz)
        note("the runner REFUSES a zero-byte log.solve -- a solve that printed "
             "nothing did not run",
             _fires(run_solve, cz, None, None, root, False, "true"))

        # ---- verify_record, driven DIRECTLY in every direction, so each
        # refusal is exercised by the guard that carries it rather than by a
        # different guard that happens to fire first.
        vr = os.path.join(tmp, "vr")
        os.makedirs(vr)
        note("verify_record REFUSES when there is no log at all",
             _fires(verify_record, vr))
        open(os.path.join(vr, LOG_NAME), "w").write("")
        note("verify_record REFUSES a zero-byte log", _fires(verify_record, vr))
        open(os.path.join(vr, LOG_NAME), "w").write("Time = 1\nEnd\n")
        note("verify_record REFUSES when NO EXIT STATUS reached disk -- a "
             "missing rc is not rc = 0", _fires(verify_record, vr))
        open(os.path.join(vr, RC_NAME), "w").write("killed\n")
        note("verify_record REFUSES an exit status that is not an integer",
             _fires(verify_record, vr))
        open(os.path.join(vr, RC_NAME), "w").write("0\n")
        note("verify_record PASSES a complete record and returns the raw rc",
             verify_record(vr) == "0")

        # ---- section 9.2's accumulator
        r2root = os.path.join(tmp, "acct")
        os.makedirs(r2root)
        b0 = budget_or_refuse(r2root)
        note("a fresh campaign gets the registered per-solve timeout, not more",
             b0["effective_timeout_s"] == B.PER_SOLVE_TIMEOUT_S
             and b0["cap_wall_s"] == B.CAMPAIGN_WALL_CAP_S,
             "timeout %ds, cap %ds" % (b0["effective_timeout_s"],
                                       b0["cap_wall_s"]))
        book(r2root, "AR_1_Ret_360", "N", B.CAMPAIGN_WALL_CAP_S - 100.0)
        b1 = budget_or_refuse(r2root)
        note("with 100 wall s left the effective timeout SHRINKS to 100, so "
             "the campaign cannot exceed the registered 21,000 wall s",
             b1["effective_timeout_s"] == 100, "%ds"
             % b1["effective_timeout_s"])
        book(r2root, "AR_1_Ret_360", "T-b", 100.0)
        note("with the registered cap reached the accumulator REFUSES the next "
             "launch (rule 12: an overrun stops the campaign)",
             _fires(budget_or_refuse, r2root))
        spent, led = read_spent(r2root)
        note("the ledger persists ACROSS process invocations and totals in "
             "core-minutes at ranks 1",
             spent == float(B.CAMPAIGN_WALL_CAP_S)
             and abs(led["core_minutes_total"]
                     - B.CAMPAIGN_WALL_CAP_S / 60.0) < 1e-9,
             "%.1f wall s = %.1f core-min" % (spent, led["core_minutes_total"]))
        bad = os.path.join(tmp, "badledger")
        os.makedirs(bad)
        open(ledger_path(bad), "w").write("{not json")
        note("an unreadable ledger REFUSES rather than defaulting to zero spend",
             _fires(read_spent, bad))
        bad2 = os.path.join(tmp, "badledger2")
        os.makedirs(bad2)
        json.dump({"wall_s_total": "lots"}, open(ledger_path(bad2), "w"))
        note("a ledger whose total is not a number REFUSES",
             _fires(read_spent, bad2))

        note("run_campaign REFUSES a configuration that was never built",
             _fires(run_campaign, os.path.join(tmp, "unbuilt")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(n) for n, _, _ in ok)
    for name, passed, detail in ok:
        print(("  %-" + str(width) + "s  %s%s")
              % (name, "PASS" if passed else "FAIL",
                 ("   [" + detail + "]") if detail else ""))
    bad_names = [n for n, p, _ in ok if not p]
    if bad_names:
        sys.stderr.write("SELFTEST FAILED: " + "; ".join(bad_names) + "\n")
        raise SystemExit(1)
    print("rc4_run selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def _drift_probe(log_name, rc_name):
    """Drive check_channel_names with drifted names, to show it FIRES."""
    global LOG_NAME, RC_NAME
    keep = (LOG_NAME, RC_NAME)
    LOG_NAME, RC_NAME = log_name, rc_name
    try:
        return check_channel_names()
    finally:
        LOG_NAME, RC_NAME = keep


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--run-campaign" in argv:
        run_campaign()
        return 0
    if "--run" in argv:
        i = argv.index("--run")
        if len(argv) < i + 3:
            refuse("usage: rc4_run.py --run <case tag> <config>")
        tag, cfg = argv[i + 1], argv[i + 2]
        B.refuse_if_unfrozen()
        print(json.dumps(run_solve(os.path.join(B.ROOT, tag, cfg), tag, cfg),
                         indent=1, default=str))
        return 0
    sys.stderr.write("usage: rc4_run.py --selftest | --run <tag> <config> | "
                     "--run-campaign\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
