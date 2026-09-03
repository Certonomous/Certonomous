#!/usr/bin/env python3
"""Fleet safety ceiling -- THE EVALUATOR AND THE DRY-RUN REPORT. IT CANNOT KILL.

WHAT THIS FILE IS, AND WHAT IT DELIBERATELY IS NOT
--------------------------------------------------
Sanaa's ruling of 2026-09-03 ~21:00Z (etc/sessions/2026-09-03T2100Z_sanaa_launch_rule.md)
keeps ONE hard structural stop:

    "a fleet-wide safety ceiling on any single run (e.g. 3x its registered cost cap, or
     the box's remaining budget, whichever is smaller) ... at the ceiling the monitor stops
     the run gracefully regardless of residual trend ... something must be structurally
     guaranteed to stop a run"

This file implements the QUESTION -- which runs are at or over that ceiling -- and NOTHING
ELSE. It contains no `kill`, no `killpg`, no `signal`, and no subprocess that could send
one. Search it: the words are absent by design, not by accident.

THAT SEPARATION IS THE POINT. A ceiling has two halves: deciding who is over it, and acting
on them. The deciding half can be built, selftested and run against production TODAY with
zero risk to anybody's solve. The acting half kills other teams' running work and, per
docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md section 6, is pre-registered to require a
mutation-controlled selftest battery that does not yet exist. Building the safe half first
and reporting what it sees is how the dangerous half earns its evidence.

RULE 3 IS LOAD-BEARING HERE AND IS NOT DECORATION
--------------------------------------------------
The report this file exists to produce is "nothing is over the ceiling" -- A ZERO. A zero
from a reader not shown able to see a non-zero is not evidence (CLAUDE.md rule 3), and this
lab filed L-466 today about exactly that failure. So `--dry-run` ALWAYS runs the planted
control first, in the same invocation, over a synthetic queue holding a known over-ceiling
entry, and REFUSES to print the live table at all if the reader cannot see the plant.

WHAT IT WILL NOT INHERIT
------------------------
scripts/queue_runner.py:698 retires a watch on `status.exists()` WITHOUT PARSING THE FILE.
A STATUS written by the launcher on a REFUSAL -- `launcher_rc=2`, as in the three rows at
verification/runs/T-family/T10aR2_runs/LAUNCH_RECORD.md:9-11 -- therefore retires the watch
on a run that never started. This file PARSES the STATUS, and independently asks the kernel
whether `_launch.sid` still names a live session. A file existing is not an answer.

THE SECOND TERM OF SANAA'S min() IS UNCOMPUTABLE ON THIS BOX
------------------------------------------------------------
COMPUTE_BUDGET_CHARTER section 5: the instance cannot read its own billing, and there is no
spend policy, cap or dollar figure anywhere in this repository. docs/COST_CALIBRATION.md is
an actual-versus-predicted CALIBRATION ledger and is not a remaining-budget ledger. So the
budget term is reported UNAVAILABLE -- NOT EVALUATED and is NEVER silently resolved:
defaulting it to 0 would put every run instantly over the ceiling, defaulting it to infinity
would silently delete half of Sanaa's rule, and both are the same failure -- a reader
reporting a number it could not read.

USAGE
    python3 scripts/fleet_safety_ceiling.py --dry-run
    python3 scripts/fleet_safety_ceiling.py --selftest
Exit 0 = evaluated, and no live entry is at or over its ceiling.
     1 = REFUSED (the planted control failed, or a selftest arm was wrong).
     4 = evaluated, and at least one live entry IS at or over its ceiling.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path("/home/ubuntu/Certonomous")
QUEUE_ROOT = REPO / "verification" / "queue"

# The multiplier Sanaa named. 3x the REGISTERED CAP -- never the estimate. section 5 of
# RUNNER_CAP_ENFORCEMENT_CLAUSE forbids inferring an unstated cap and acting on it, and
# Sanaa was explicit the ceiling sits "far above the estimate, not the estimate itself".
CEILING_MULTIPLIER = 3.0

# Mirrors queue_runner.ARCHIVED_RE: a record retired by a later launch of the same case_id.
ARCHIVED_RE = re.compile(r"\.\d{8}T\d{6}Z\.json$")

TEAMS = ("cfd", "heat-transfer", "closure", "dafoam", "verification", "ansys-verification")


class Refused(Exception):
    """A control did not behave as pre-registered. Never downgraded to a warning."""


def live_sids() -> set[int]:
    """Session ids the KERNEL says exist. Not a file's opinion about a process."""
    out = subprocess.run(["ps", "-eo", "sid="], capture_output=True, text=True).stdout
    return {int(x) for x in out.split() if x.isdigit()}


def parse_status(p: Path) -> dict:
    """Parse a STATUS file rather than merely noting that it exists.

    THE DEFECT THIS AVOIDS, named because it is live in the tree: queue_runner.py:698 does
    `if status.exists(): ... continue`. The launcher writes a STATUS on a REFUSAL too --
    `launcher_rc=2` -- so the existing predicate retires a watch on a run that NEVER
    STARTED. `launcher_rc` is the exit status of the launch argv and is NEVER the solver's
    rc, even at 0; the T-family graders read it precisely to refuse it as one
    (verification/runs/T-family/T25R_MODULE_runs/mark_done_t25R.py:214).
    """
    try:
        text = p.read_text()
    except OSError:
        return {}
    out = {}
    for tok in text.split():
        if "=" in tok:
            k, _, v = tok.partition("=")
            out[k] = v
    return out


def is_current(p: Path) -> bool:
    return not ARCHIVED_RE.search(p.name)


def evaluate(queue_root: Path, now: float | None = None,
             sids: set[int] | None = None) -> list[dict]:
    """Read every current launched record and judge it against its own ceiling.

    Pure w.r.t. the world except the filesystem and `ps`, both injectable, so the planted
    control and the selftest drive the SAME code path the live report drives.
    """
    t_now = time.time() if now is None else float(now)
    sids = live_sids() if sids is None else sids
    rows: list[dict] = []
    for team in TEAMS:
        d = queue_root / team / "launched"
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.json")):
            # EVERY RECORD PRODUCES A ROW. An entry this loop cannot evaluate is RECORDED
            # as NOT EVALUATED WITH THE REASON -- never dropped. Omission is the bug:
            # docs/FAIL_OPEN_GATE_AUDIT.md section 28's operational test is "can this code
            # path distinguish 'the check ran and found nothing' from 'the check did not
            # run'?", and a silently skipped record makes those two the same silence.
            # The `except: continue` this replaces was face 1 of that taxonomy -- a
            # swallowed refusal -- sitting inside the very tool written to answer it.
            base = {"team": team, "record": str(p), "case_id": p.stem, "evaluated": False,
                    "reason": None, "ranks": None, "cap": None, "ceiling": None,
                    "elapsed_core_min": None, "margin": None, "sid": None,
                    "sid_live": None, "status_seen": None, "launcher_rc": None,
                    "finished_argv": None, "live": False, "verdict": None}
            if not is_current(p):
                rows.append({**base, "reason": "archived by a later launch of this case_id",
                             "verdict": "NOT EVALUATED (archived, not under watch)"})
                continue
            try:
                meta = json.loads(p.read_text())
            except (OSError, json.JSONDecodeError) as e:
                rows.append({**base,
                             "reason": f"record unreadable: {type(e).__name__}: {e}",
                             "verdict": "NOT A RESULT (record unreadable -- this entry was "
                                        "NOT evaluated and is NOT known to be safe)"})
                continue
            li = meta.get("_launch") or {}
            if "started_epoch" not in li:
                rows.append({**base, "case_id": meta.get("case_id", p.stem),
                             "reason": "_launch.started_epoch absent",
                             "verdict": "NOT EVALUATED (no started_epoch to measure from)"})
                continue
            sid = li.get("sid")
            sid_live = isinstance(sid, int) and sid in sids

            status_path = Path(li.get("status_file", "/nonexistent"))
            st = parse_status(status_path) if status_path.exists() else {}
            launcher_rc = st.get("launcher_rc")

            # `launcher_rc` IS RECORDED AND IS NEVER USED TO RETIRE A ROW. This is a
            # correction to THIS FILE's own first draft, made after it got the live box
            # wrong, and it is the whole reason the dry run is run before anything is armed.
            #
            # MEASURED 2026-09-03T18:44Z on heat-transfer's T3d_R_fx: STATUS reads
            # `launcher_rc=0 end=2026-09-03T18:03:38Z`, the record is stamped
            # `status_seen_utc` -- and the run is VERY MUCH ALIVE: session 339965 holds 11
            # processes, `mpirun -np 8` plus eight buoyantBoussinesqSimpleFoam ranks under a
            # 122445 s timeout. The launch ARGV exited at 18:03:38; THE SOLVE DID NOT.
            #
            # The STATUS file says so itself, in the note the launcher writes into it:
            # "exit-status-of-the-launch-argv-NOT-the-solver-rc". The T-family graders read
            # `launcher_rc` precisely to REFUSE it as a solver rc
            # (verification/runs/T-family/T25R_MODULE_runs/mark_done_t25R.py:214). A first
            # draft of this file treated it as a completion signal anyway and so declared a
            # live 8-rank solve dead -- the same wrong answer queue_runner.py:698 reaches by
            # a different route.
            #
            # SO THE KERNEL IS THE ONLY LIVENESS AUTHORITY HERE. A ceiling that asks a file
            # whether a process is running protects nothing, and -- once armed -- would just
            # as happily act on a row whose real state it never checked.
            finished_argv = bool(st) and "launcher_rc" in st

            ranks = max(1, int(meta.get("ranks", 1) or 1))
            elapsed_s = t_now - float(li["started_epoch"])
            elapsed_core_min = elapsed_s / 60.0 * ranks

            cap = meta.get("cap_core_min_registered")
            has_cap = (isinstance(cap, (int, float)) and not isinstance(cap, bool)
                       and cap > 0)
            ceiling = CEILING_MULTIPLIER * float(cap) if has_cap else None

            # A run is a CANDIDATE for the ceiling only if the KERNEL still has its
            # session. Nothing a file says can promote or demote that fact.
            live = sid_live

            if not has_cap:
                verdict = ("NOT A RESULT (no cap_core_min_registered: no ceiling is "
                           "computable, so this entry is UNPROTECTED -- not safe)")
            elif not live:
                verdict = "not live"
            elif elapsed_core_min >= ceiling:
                verdict = "AT OR OVER CEILING"
            else:
                verdict = "under ceiling"

            rows.append({
                **base, "evaluated": True,
                "reason": "evaluated against 3x cap_core_min_registered",
                "team": team, "case_id": meta.get("case_id", p.stem), "record": str(p),
                "ranks": ranks, "cap": cap if has_cap else None, "ceiling": ceiling,
                "elapsed_core_min": elapsed_core_min,
                "margin": (ceiling - elapsed_core_min) if ceiling is not None else None,
                "sid": sid, "sid_live": sid_live, "status_seen": bool(st),
                "launcher_rc": launcher_rc, "finished_argv": finished_argv,
                "live": live, "verdict": verdict,
            })
    return rows


def _plant(tmp: Path, now: float) -> Path:
    """A synthetic queue holding one entry the reader MUST flag and three it must not.

    The over-ceiling plant is given a LIVE sid -- this process's own session -- because a
    dead sid would let the reader pass the control by declining every row for the wrong
    reason. The plant has to be a genreader victim, not merely a row.
    """
    import os
    my_sid = os.getsid(0)
    root = tmp / "queue"
    d = root / "cfd" / "launched"
    d.mkdir(parents=True)

    def rec(name, cap, ranks, age_min, sid, status_text=None):
        sf = tmp / f"STATUS.{name}"
        if status_text is not None:
            sf.write_text(status_text)
        (d / f"{name}.json").write_text(json.dumps({
            "case_id": name, "team": "cfd", "ranks": ranks,
            "cost_core_min_estimate": 1.0,
            **({"cap_core_min_registered": cap} if cap is not None else {}),
            "cwd": str(tmp),
            "_launch": {"utc": "2026-09-03T00:00:00Z", "pid": sid, "sid": sid,
                        "status_file": str(sf),
                        "started_epoch": now - age_min * 60},
        }))

    # 10 core-min cap -> ceiling 30 core-min. 40 min x 1 rank = 40 core-min: OVER.
    rec("PLANTED_OVER_CEILING", 10.0, 1, 40, my_sid)
    # same cap, 20 core-min elapsed: UNDER.
    rec("PLANTED_UNDER_CEILING", 10.0, 1, 20, my_sid)
    # no cap at all: NO CEILING, never flagged however long it runs.
    rec("PLANTED_CAPLESS", None, 1, 400, my_sid)
    # over on the clock, STATUS says the launch argv REFUSED (launcher_rc=2), and the
    # session is DEAD. Not live, and the kernel is what says so.
    rec("PLANTED_REFUSED_LAUNCH", 10.0, 1, 40, 4_194_301,
        status_text="launcher_rc=2 end=2026-09-03T00:00:01Z note=refused\n")
    # THE T3d SHAPE, measured live on 2026-09-03: STATUS carries launcher_rc=0 -- the
    # launch ARGV exited -- while the SOLVE runs on in a live session. It MUST be flagged.
    # This is the arm that would have caught this file's own first-draft defect, and it is
    # the arm queue_runner.py:698 fails.
    rec("PLANTED_ARGV_EXITED_SOLVE_ALIVE", 10.0, 1, 40, my_sid,
        status_text="launcher_rc=0 end=2026-09-03T00:00:01Z "
                    "note=exit-status-of-the-launch-argv-NOT-the-solver-rc\n")
    return root


def planted_control(now: float | None = None) -> tuple[bool, list[str]]:
    """Show the reader able to see a NON-ZERO before any zero it reports is believed."""
    t_now = time.time() if now is None else now
    lines: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ceiling_control_") as td:
        tmp = Path(td)
        root = _plant(tmp, t_now)
        rows = {r["case_id"]: r for r in evaluate(root, now=t_now)}
        expect = {
            "PLANTED_OVER_CEILING": "AT OR OVER CEILING",
            "PLANTED_UNDER_CEILING": "under ceiling",
            "PLANTED_CAPLESS": ("NOT A RESULT (no cap_core_min_registered: no ceiling "
                                "is computable, so this entry is UNPROTECTED -- not safe)"),
            "PLANTED_REFUSED_LAUNCH": "not live",
            "PLANTED_ARGV_EXITED_SOLVE_ALIVE": "AT OR OVER CEILING",
        }
        ok = True
        for name, want in expect.items():
            got = rows.get(name, {}).get("verdict", "<not read at all>")
            good = (got == want)
            ok = ok and good
            lines.append(f"    [{'ok     ' if good else 'REFUSED'}] {name:24s} "
                         f"expected {want!r}, got {got!r}")
        return ok, lines


def check_ceiling(rows: list[dict]) -> list[dict]:
    """THE CEILING CHECK ITSELF. Kept as a named entry in CHECKS, not inlined, so that a
    control can REMOVE IT FROM THE CALLER and watch the same planted entry sail through.

    That removal is the only thing that proves the caller actually invokes it.
    docs/FAIL_OPEN_GATE_AUDIT.md section 28: every planted-value control this lab has run
    proves the INSTRUMENT can fail; "NOT ONE of them proves the CALLER ever invoked it."
    """
    return [r for r in rows if r["verdict"] == "AT OR OVER CEILING"]


CHECKS = {"ceiling": check_ceiling}


def fmt(rows: list[dict]) -> list[str]:
    """Rows are EVIDENCE OF EVALUATION, not evidence of quiet.

    Each printed row says what the ceiling READ (the cap), what it COMPUTED (3x), what it
    MEASURED (core-minutes) and the MARGIN -- so a reader can tell an entry that was
    checked and found safe from an entry that was never checked. A table that showed only
    survivors would be face 2 of the audit wearing a ceiling's clothes.
    """
    out = [
        "  ev  team            case_id                        ranks       cap  "
        "ceiling(3x)   elapsed    margin  verdict",
        "  " + "-" * 124,
    ]
    for r in sorted(rows, key=lambda x: (x["verdict"] != "AT OR OVER CEILING",
                                         not x["evaluated"], x["team"] or "")):
        cap = f"{r['cap']:.2f}" if r["cap"] is not None else "--"
        cei = f"{r['ceiling']:.2f}" if r["ceiling"] is not None else "--"
        ela = f"{r['elapsed_core_min']:.2f}" if r["elapsed_core_min"] is not None else "--"
        mar = f"{r['margin']:.2f}" if r["margin"] is not None else "--"
        ev = "RAN" if r["evaluated"] else "---"
        out.append(f"  {ev:3s} {(r['team'] or '')[:14]:14s}  {str(r['case_id'])[:28]:28s}  "
                   f"{str(r['ranks'] or '--'):>5s}  {cap:>8s}  {cei:>11s}  {ela:>8s}  "
                   f"{mar:>8s}  {r['verdict']}")
    return out


def report(queue_root: Path, checks: dict | None = None,
           now: float | None = None, sids: set[int] | None = None,
           echo: bool = True, sidecar: Path | None = None) -> tuple[int, list[str]]:
    """THE REAL CALLER. dry_run() and every control drive THIS, never evaluate() directly.

    Returns (exit_code, lines). Exit codes are in the module docstring; 5 is new and is the
    whole point of section 28: THE CHECK DID NOT RUN, which is NOT A RESULT and is never a
    quiet pass.
    """
    checks = CHECKS if checks is None else checks
    out: list[str] = []
    rows = evaluate(queue_root, now=now, sids=sids)

    n_eval = sum(1 for r in rows if r["evaluated"])
    n_not = len(rows) - n_eval
    live = [r for r in rows if r["live"]]
    unreadable = [r for r in rows if r["verdict"].startswith("NOT A RESULT (record")]
    capless_live = [r for r in rows if r["live"] and r["cap"] is None]

    out.append(f"  RECORDS SEEN: {len(rows)}   EVALUATED: {n_eval}   "
               f"NOT EVALUATED: {n_not}   LIVE: {len(live)}")
    out.append("  (an entry the ceiling did not evaluate is RECORDED with its reason, "
               "never omitted -- omission is the bug)")
    out.append("")

    # THE CALLER-SIDE TEST, asked before any finding is reported.
    if "ceiling" not in checks:
        out.append("NOT A RESULT: THE CEILING CHECK DID NOT RUN.")
        out.append("  No entry was judged against any ceiling, so 'nothing exceeded its "
                   "ceiling' would be an UNINTERPRETABLE zero.")
        out.append("  docs/FAIL_OPEN_GATE_AUDIT.md section 28: a blocked, refused, skipped "
                   "or unrun measurement is NOT A RESULT --")
        out.append("  never absence-of-failure, never a silent PASS, never a closed question.")
        if echo:
            for line in out:
                print(line)
        return 5, out

    findings = checks["ceiling"](rows)

    for line in fmt([r for r in rows if r["live"] or not r["evaluated"]
                     or r["verdict"] == "AT OR OVER CEILING"][:60]):
        out.append(line)
    out.append("")

    if unreadable:
        out.append(f"  {len(unreadable)} record(s) were UNREADABLE and are NOT known to be "
                   f"safe -- they are NOT A RESULT, not a pass:")
        for r in unreadable:
            out.append(f"    - {r['record']}: {r['reason']}")
        out.append("")
    if capless_live:
        out.append(f"  COVERAGE HOLE, STATED AT RUNTIME AND PER ENTRY: {len(capless_live)} "
                   f"LIVE entry/entries carry no cap_core_min_registered.")
        out.append("  section 5 of RUNNER_CAP_ENFORCEMENT_CLAUSE forbids inferring an "
                   "unstated cap and acting on it, so no ceiling")
        out.append("  is computable for them. Each is NOT A RESULT and UNPROTECTED -- it is "
                   "NOT 'under the ceiling'.")
        for r in capless_live:
            out.append(f"    - NOT A RESULT: {r['team']}/{r['case_id']} "
                       f"({r['elapsed_core_min']:.2f} core-min so far, no ceiling computable)")
        out.append("")

    if sidecar is not None:
        try:
            sidecar.write_text(json.dumps(
                {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                 "multiplier": CEILING_MULTIPLIER,
                 "budget_term": "UNAVAILABLE -- NOT EVALUATED",
                 "checks_run": sorted(checks), "records": len(rows),
                 "evaluated": n_eval, "not_evaluated": n_not, "live": len(live),
                 "findings": [r["case_id"] for r in findings],
                 "rows": rows}, indent=1, default=str))
            out.append(f"  per-entry evaluation record written: {sidecar}")
            out.append("")
        except OSError as e:
            out.append(f"  WARNING: could not write the evaluation record: {e}")

    if findings:
        out.append(f"WOULD STOP: {len(findings)} live entry/entries are AT OR OVER their "
                   f"ceiling.")
        rc = 4
    else:
        out.append(f"ZERO VICTIMS: the ceiling check RAN over {n_eval} evaluated record(s) "
                   f"and found none at or over its ceiling.")
        out.append("  This is a result, not a silence: the per-row RAN column and the "
                   "sidecar name every entry it judged.")
        rc = 0
    if echo:
        for line in out:
            print(line)
    return rc, out


def dry_run(sidecar: Path | None = None) -> int:
    print("FLEET SAFETY CEILING -- DRY RUN. THIS PROGRAM CANNOT KILL; IT HAS NO SIGNAL PATH.")
    print(f"  utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    print(f"  ceiling = {CEILING_MULTIPLIER:g} x cap_core_min_registered")
    print("  second term of Sanaa's min(), the box's remaining budget: "
          "UNAVAILABLE -- NOT EVALUATED")
    print("    COMPUTE_BUDGET_CHARTER section 5: this instance cannot read its own billing, "
          "and no spend cap exists in the repo.")
    print("    A RECORDED STATE, not an absent one. NOT defaulted to 0 (every run instantly "
          "over the ceiling) and NOT to")
    print("    infinity (half the rule silently deleted); both are the same failure, a "
          "reader reporting a number it could not read.")
    print()
    print("  PLANTED CONTROLS FIRST. Two of them, because there are two questions:")
    print("    (a) CAN the instrument fire?      -- the planted-value control (rule 3)")
    print("    (b) DID the caller invoke it?     -- the caller-side control "
          "(FAIL_OPEN_GATE_AUDIT section 28)")
    ok, lines = planted_control()
    for line in lines:
        print(line)
    ok2, lines2 = caller_side_control()
    for line in lines2:
        print(line)
    if not (ok and ok2):
        print("\nREFUSED: a control failed. No live table is printed, because a report from "
              "this reader would be worth nothing.")
        return 1
    print("  => the instrument can fire, AND the caller demonstrably invokes it. Only now "
          "is its zero worth reading.")
    print()
    rc, _ = report(QUEUE_ROOT, sidecar=sidecar)
    return rc


def caller_side_control(now: float | None = None) -> tuple[bool, list[str]]:
    """PLANT THE RUN, NOT ONLY THE VALUE.

    A planted over-ceiling entry is driven through report() -- THE REAL CALLER, the same
    function dry_run() uses -- twice: once with the ceiling in CHECKS, once with CHECKS
    emptied. The pair proves the caller actually invokes the check, which no planted value
    can prove.

    The second arm's REQUIRED answer is not "the entry passes" but "NOT A RESULT: the
    ceiling check did not run". A caller that reported ZERO VICTIMS with no check in it
    would be the exact defect section 28 names.
    """
    t_now = time.time() if now is None else now
    lines: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ceiling_caller_") as td:
        tmp = Path(td)
        root = _plant(tmp, t_now)
        rc_with, out_with = report(root, checks=CHECKS, now=t_now, echo=False)
        rc_without, out_without = report(root, checks={}, now=t_now, echo=False)
        a = (rc_with == 4 and any("WOULD STOP" in l for l in out_with))
        b = (rc_without == 5 and any("THE CEILING CHECK DID NOT RUN" in l
                                     for l in out_without))
        c = not any("ZERO VICTIMS" in l for l in out_without)
        lines.append(f"    [{'ok     ' if a else 'REFUSED'}] caller WITH the ceiling check: "
                     f"rc={rc_with}, planted over-ceiling entry CAUGHT")
        lines.append(f"    [{'ok     ' if b else 'REFUSED'}] caller WITHOUT it: rc={rc_without}, "
                     f"reports NOT A RESULT -- the check did not run")
        lines.append(f"    [{'ok     ' if c else 'REFUSED'}] and it does NOT report ZERO "
                     f"VICTIMS over a check that never ran")
        return (a and b and c), lines


def selftest() -> int:
    """Arms driven on synthetic clocks and synthetic queues. No box, no solver, no wait."""
    print("SELFTEST of the ceiling evaluator")
    bad = 0
    now = 1_000_000.0

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal bad
        print(f"  [{'ok     ' if cond else 'REFUSED'}] {label}")
        if detail:
            print(f"            {detail}")
        if not cond:
            bad += 1

    ok, lines = planted_control(now=now)
    for line in lines:
        print(line)
    check("planted-VALUE control: can the instrument fire? (rule 3)", ok)

    ok2, lines2 = caller_side_control(now=now)
    for line in lines2:
        print(line)
    check("planted-RUN control: does the CALLER invoke it? "
          "(FAIL_OPEN_GATE_AUDIT section 28)", ok2)

    # THE MUTATION CONTROL. A selftest that only shows the evaluator flagging its plant
    # cannot tell a working evaluator from one that flags EVERYTHING. section 6 of
    # RUNNER_CAP_ENFORCEMENT_CLAUSE pre-registers exactly this discipline: "a selftest that
    # only shows the kill working cannot detect a runner that kills everything."
    with tempfile.TemporaryDirectory(prefix="ceiling_mut_") as td:
        tmp = Path(td)
        root = _plant(tmp, now)
        rows = {r["case_id"]: r for r in evaluate(root, now=now)}
        n_flagged = sum(1 for r in rows.values() if r["verdict"] == "AT OR OVER CEILING")
        check("MUTATION CONTROL: exactly TWO of the five plants are flagged, not all five",
              n_flagged == 2,
              f"flagged {n_flagged}; an evaluator that flags everything would say 5 here")

        # ranks multiply the spend: the SAME wall time on 8 ranks crosses a ceiling the
        # 1-rank row sits under. If this arm fails, core-minutes are being read as wall
        # minutes, which is CLAUDE.md rule 12's unit error.
        d = root / "cfd" / "launched"
        rec = json.loads((d / "PLANTED_UNDER_CEILING.json").read_text())
        rec["ranks"] = 8
        rec["case_id"] = "PLANTED_RANKS"
        (d / "PLANTED_RANKS.json").write_text(json.dumps(rec))
        rows2 = {r["case_id"]: r for r in evaluate(root, now=now)}
        check("core-minutes are wall x ranks: 20 wall-min on 8 ranks (160 core-min) "
              "crosses a 30 core-min ceiling",
              rows2["PLANTED_RANKS"]["verdict"] == "AT OR OVER CEILING",
              f"got {rows2['PLANTED_RANKS']['verdict']!r}, "
              f"elapsed {rows2['PLANTED_RANKS']['elapsed_core_min']:.1f} core-min")

        # A dead sid must retire a row even with no STATUS at all -- the kernel's answer
        # stands on its own.
        rec2 = json.loads((d / "PLANTED_OVER_CEILING.json").read_text())
        rec2["case_id"] = "PLANTED_DEADSID"
        rec2["_launch"]["sid"] = 4_194_301
        (d / "PLANTED_DEADSID.json").write_text(json.dumps(rec2))
        rows3 = {r["case_id"]: r for r in evaluate(root, now=now, sids=set())}
        check("a dead session retires a row even with no STATUS file",
              rows3["PLANTED_DEADSID"]["verdict"] == "not live")

        # THE ONE THAT MATTERS FOR THE RULING: an EMPTY STATUS file must NOT retire a live
        # over-ceiling run. queue_runner.py:698's existence-only predicate WOULD retire it.
        import os
        empty = tmp / "STATUS.EMPTY"
        empty.write_text("")
        rec3 = json.loads((d / "PLANTED_OVER_CEILING.json").read_text())
        rec3["case_id"] = "PLANTED_EMPTY_STATUS"
        rec3["_launch"]["status_file"] = str(empty)
        rec3["_launch"]["sid"] = os.getsid(0)
        (d / "PLANTED_EMPTY_STATUS.json").write_text(json.dumps(rec3))
        rows4 = {r["case_id"]: r for r in evaluate(root, now=now)}
        check("an EMPTY STATUS file does NOT retire a live over-ceiling run "
              "(queue_runner.py:698 would have)",
              rows4["PLANTED_EMPTY_STATUS"]["verdict"] == "AT OR OVER CEILING",
              f"got {rows4['PLANTED_EMPTY_STATUS']['verdict']!r}")

    with tempfile.TemporaryDirectory(prefix="ceiling_unread_") as td:
        tmp = Path(td)
        root = _plant(tmp, now)
        broken = root / "cfd" / "launched" / "PLANTED_UNREADABLE.json"
        broken.write_text("{ this is not json")
        rws = {r["case_id"]: r for r in evaluate(root, now=now)}
        r = rws.get("PLANTED_UNREADABLE", {})
        check("an UNREADABLE record is reported as NOT A RESULT, not silently dropped",
              bool(r) and r.get("verdict", "").startswith("NOT A RESULT (record"),
              f"got {r.get('verdict', '<row absent entirely -- the old code dropped it>')!r}")
        rc, out = report(root, now=now, echo=False)
        check("and the caller SURFACES it rather than reporting a clean sweep over it",
              any("UNREADABLE" in l for l in out))

    src = Path(__file__).read_text()
    for forbidden in ("killpg", "SIGTERM", "SIGKILL", "os.kill"):
        check(f"this file contains no {forbidden} path",
              forbidden not in src.split('"""')[-1] and src.count(forbidden) <= 2,
              "mentions in the header prose are allowed; a call site is not")

    if bad:
        print(f"\nREFUSED: {bad} arm(s) wrong")
        return 1
    print("\nAll arms behaved as pre-registered.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sidecar", default=None,
                    help="write the per-entry evaluation record here as JSON")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.dry_run:
        sc = Path(args.sidecar) if args.sidecar else None
        return dry_run(sidecar=sc)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
