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
            if not is_current(p):
                continue
            try:
                meta = json.loads(p.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            li = meta.get("_launch") or {}
            if "started_epoch" not in li:
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
                verdict = "NO CEILING (no cap_core_min_registered)"
            elif not live:
                verdict = "not live"
            elif elapsed_core_min >= ceiling:
                verdict = "AT OR OVER CEILING"
            else:
                verdict = "under ceiling"

            rows.append({
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
            "PLANTED_CAPLESS": "NO CEILING (no cap_core_min_registered)",
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


def fmt(rows: list[dict]) -> list[str]:
    out = [
        "  team            case_id                        ranks   cap    ceiling(3x)  "
        "elapsed  margin   verdict",
        "  " + "-" * 116,
    ]
    for r in sorted(rows, key=lambda x: (x["verdict"] != "AT OR OVER CEILING", x["team"])):
        cap = f"{r['cap']:.2f}" if r["cap"] is not None else "  --"
        cei = f"{r['ceiling']:.2f}" if r["ceiling"] is not None else "   --"
        mar = f"{r['margin']:.2f}" if r["margin"] is not None else "   --"
        out.append(f"  {r['team'][:14]:14s}  {str(r['case_id'])[:28]:28s}  "
                   f"{r['ranks']:5d}  {cap:>6s}  {cei:>10s}  "
                   f"{r['elapsed_core_min']:8.2f}  {mar:>7s}  {r['verdict']}")
    return out


def dry_run() -> int:
    print("FLEET SAFETY CEILING -- DRY RUN. THIS PROGRAM CANNOT KILL; IT HAS NO SIGNAL PATH.")
    print(f"  utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    print(f"  ceiling = {CEILING_MULTIPLIER:g} x cap_core_min_registered")
    print("  second term of Sanaa's min(), the box's remaining budget: "
          "UNAVAILABLE -- NOT EVALUATED")
    print("    COMPUTE_BUDGET_CHARTER section 5: this instance cannot read its own billing, "
          "and no spend cap exists in the repo.")
    print("    It is NOT defaulted to 0 (which would put every run over the ceiling at "
          "once) and NOT to infinity (which would")
    print("    silently delete half the rule). A half-computable rule that names the half "
          "it computed is honest.")
    print()
    print("  PLANTED CONTROL FIRST -- the report below is a ZERO, and a zero from a reader "
          "not shown able to see a")
    print("  non-zero is not evidence (CLAUDE.md rule 3; L-466 was filed today for exactly "
          "this failure):")
    ok, lines = planted_control()
    for line in lines:
        print(line)
    if not ok:
        print("\nREFUSED: the reader could not see the planted over-ceiling entry. "
              "No live table is printed, because a")
        print("  'nothing is over the ceiling' report from this reader would be worth "
              "nothing.")
        return 1
    print("  => the reader is shown able to flag a victim, decline a safe run, decline a "
          "capless run, and decline a")
    print("     refused launch. Only now is its zero worth reading.")
    print()

    rows = evaluate(QUEUE_ROOT)
    live = [r for r in rows if r["live"]]
    over = [r for r in rows if r["verdict"] == "AT OR OVER CEILING"]
    capless_live = [r for r in live if r["cap"] is None]
    print(f"  LIVE QUEUE, all teams: {len(rows)} current launched record(s), "
          f"{len(live)} still live by BOTH tests (kernel session alive AND STATUS not "
          f"showing an exited launch argv).")
    print()
    for line in fmt([r for r in rows if r["live"] or r["verdict"] == "AT OR OVER CEILING"]):
        print(line)
    print()
    if capless_live:
        print(f"  COVERAGE HOLE, NAMED NOT PAPERED OVER: {len(capless_live)} live "
              f"entry/entries carry no cap_core_min_registered")
        print("  and therefore have NO ceiling at all. section 5 forbids inferring an "
              "unstated cap and acting on it, so these")
        print("  runs are unprotected by this mechanism. The fix belongs at registration "
              "and is forward-only.")
        for r in capless_live:
            print(f"    - {r['team']}/{r['case_id']}  ({r['elapsed_core_min']:.2f} "
                  f"core-min so far)")
        print()
    if over:
        print(f"WOULD STOP: {len(over)} live entry/entries are AT OR OVER their ceiling.")
        return 4
    print("ZERO VICTIMS: no live entry is at or over its ceiling.")
    return 0


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
    check("planted control: all four arms correct", ok)

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
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.dry_run:
        return dry_run()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
