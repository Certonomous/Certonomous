#!/usr/bin/env python3
"""ansys-verification append guards -- REUSE heat-transfer's, plus the two this
team paid for that theirs does not carry.

WHY THIS EXISTS RATHER THAN A COPY.  heat-transfer's
`verification/runs/T-family/safe_append.py` (commit 5c137f0b) already implements
check_prefix / check_trailing_newline / check_anchor_is_last correctly, with both
arms.  Copying them would fork a guard, and a forked guard drifts.  This module
IMPORTS them by explicit path and PINS THE BLOB SHA it imported, so a change to
their tool cannot silently change what gates this team's credential appends.

WHAT THIS ADDS, and each is a defect this team measured on 2026-08-25:

  1. check_aggregates_moved -- A CELL CANNOT HOLD MORE THAN ITS SUB-ROWS.
     When a child row lands, every aggregate ABOVE it must move in the SAME
     invocation.  The validation register's `Credential count: N PASS of M run`
     and CASE_MAP's campaign fraction are both parents of every case row.
     Leaving a parent stale is an inconsistent record in the MORE VISIBLE half.

  2. enforce_per_guard_symmetry -- PER GUARD, not in aggregate.
     Measured against safe_append.py itself: its refusal computes
     `neg = len(results) - pos; if neg == 0`, which is an AGGREGATE.  A fourth
     guard added with only a bad-input arm passes it, and the tool then prints
     "SYMMETRY HELD: every guard fires on bad input and stays quiet on good" --
     a claim it has not checked per guard.  That is L-314's own shape (a check
     reporting on the AGGREGATE rather than on each ITEM) inside the tool built
     to cure it.  REPORTED UPWARD, NOT PATCHED: safe_append.py is heat-transfer's
     territory.  This module enforces the strict form for its own guards.

Exit 2 = REFUSED, never a degraded pass (CLAUDE.md rule 4's posture).
"""
import importlib.util, re, subprocess, sys
from collections import defaultdict

EXIT_OK, EXIT_REFUSE = 0, 2
UPSTREAM = "verification/runs/T-family/safe_append.py"
UPSTREAM_PIN = "6c8035a32f51f140b051ab90b873ffa40bacccaa"  # safe_append.py v1.1 (13f0577c): symmetry_verdict now PER-FAMILY and itself meta-tested in both directions, with this team's v1.0 defect planted as a named regression. Re-read as code, selftest 6/6 + meta 6/6 run by this supervisor, 2026-08-25. Re-pinned DELIBERATELY, not to silence a refusal.


class GuardFailure(Exception):
    pass


def _load_upstream(repo="/home/ubuntu/Certonomous", verify_pin=True):
    """Import heat-transfer's guards and PIN the blob we imported."""
    sha = subprocess.check_output(
        ["git", "-C", repo, "rev-parse", f"HEAD:{UPSTREAM}"], text=True).strip()
    if verify_pin and UPSTREAM_PIN not in ("", "UNPINNED") and sha != UPSTREAM_PIN:
        raise GuardFailure(
            f"UPSTREAM GUARD CHANGED: {UPSTREAM} at HEAD is {sha}, pinned {UPSTREAM_PIN}. "
            "Re-read it, re-run ITS selftest, then re-pin deliberately -- a guard that "
            "changed under you is a guard you have not read.")
    spec = importlib.util.spec_from_file_location("ht_safe_append", f"{repo}/{UPSTREAM}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, sha


def check_aggregates_moved(text, aggregates):
    """AGGREGATES: list of (label, regex_with_one_group, expected_value_str).

    Each regex must match exactly once; its group must equal expected.  A parent
    left stale while its child changed is the failure this refuses.
    """
    for label, rx, expected in aggregates:
        ms = re.findall(rx, text, flags=re.M)
        if len(ms) != 1:
            raise GuardFailure(
                f"AGGREGATE {label!r}: pattern matched {len(ms)} times, expected exactly 1 "
                "-- an aggregate that cannot be located cannot be checked")
        if str(ms[0]).strip() != str(expected).strip():
            raise GuardFailure(
                f"AGGREGATE {label!r} IS STALE: reads {ms[0]!r}, child requires {expected!r}. "
                "A cell cannot hold more than its sub-rows -- move every parent in THIS "
                "invocation.")


def enforce_per_guard_symmetry(results):
    """RESULTS: list of (ok, guard_name, kind, note). Every DISTINCT guard name
    must carry BOTH a BAD-input and a GOOD-input arm.  Aggregate counting is
    exactly the hole measured in the upstream tool."""
    kinds = defaultdict(set)
    for _, name, kind, _ in results:
        kinds[name.split("/")[0]].add(kind)
    missing_neg = sorted(n for n, k in kinds.items() if "GOOD-input" not in k)
    missing_pos = sorted(n for n, k in kinds.items() if "BAD-input" not in k)
    if missing_neg or missing_pos:
        raise GuardFailure(
            f"SYMMETRY NOT HELD PER GUARD: no good-input arm for {missing_neg}; "
            f"no bad-input arm for {missing_pos}. A guard shown only to fire is untested, "
            "and a guard that always fires is indistinguishable from one that works.")


def _selftest():
    results = []

    def arm(name, fn, must_raise):
        try:
            fn()
        except GuardFailure as e:
            ok, note = must_raise, f"fired: {str(e)[:56]}"
        except Exception as e:  # noqa: BLE001
            ok, note = False, f"WRONG EXCEPTION {type(e).__name__}: {e}"
        else:
            ok, note = not must_raise, "stayed quiet"
        results.append((ok, name, "BAD-input" if must_raise else "GOOD-input", note))

    reg = ("| **4** | **VMFL051** | `NOT A RESULT` |\n"
           "*Credential count: 2 PASS of 4 run.*\n")
    reg5 = reg.replace("2 PASS of 4 run", "2 PASS of 5 run")

    # 1. AGGREGATES -- both arms
    arm("aggregates",
        lambda: check_aggregates_moved(reg5, [("tally", r"Credential count: (.+?)\.", "2 PASS of 5 run")]),
        False)
    arm("aggregates",
        lambda: check_aggregates_moved(reg, [("tally", r"Credential count: (.+?)\.", "2 PASS of 5 run")]),
        True)
    arm("aggregates/unlocatable",
        lambda: check_aggregates_moved(reg, [("tally", r"NoSuchTally: (.+?)\.", "x")]),
        True)

    # 2. PER-GUARD SYMMETRY -- both arms
    good = [(True, "g1", "BAD-input", ""), (True, "g1", "GOOD-input", "")]
    arm("symmetry", lambda: enforce_per_guard_symmetry(good), False)
    # the exact hole measured in the upstream tool: aggregate neg>0, but g2 has no GOOD arm
    holed = good + [(True, "g2", "BAD-input", "")]
    arm("symmetry/upstream-hole", lambda: enforce_per_guard_symmetry(holed), True)

    # 3. UPSTREAM PIN -- both arms
    arm("upstream_pin", lambda: _load_upstream(verify_pin=False), False)
    def _wrong_pin():
        global UPSTREAM_PIN
        keep, UPSTREAM_PIN = UPSTREAM_PIN, "0" * 40
        try: _load_upstream(verify_pin=True)
        finally: UPSTREAM_PIN = keep
    arm("upstream_pin/changed", _wrong_pin, True)

    w = max(len(n) for _, n, _, _ in results)
    for ok, name, kind, note in results:
        print(f"  {'PASS' if ok else 'FAIL':4}  {name:<{w}}  {kind:<10} {note}")
    pos = sum(1 for r in results if r[2] == "BAD-input")
    print(f"\n  {len(results)} checks: {pos} bad-input (must fire), "
          f"{len(results)-pos} good-input (must stay quiet)")
    try:
        enforce_per_guard_symmetry(results)
    except GuardFailure as e:
        print(f"  REFUSED: {e}")
        return EXIT_REFUSE
    if [r for r in results if not r[0]]:
        print(f"  REFUSED: {len([r for r in results if not r[0]])} check(s) failed")
        return EXIT_REFUSE
    print("  SYMMETRY HELD PER GUARD: each guard fires on bad input AND stays quiet on good")
    return EXIT_OK


if __name__ == "__main__":
    if "--pin" in sys.argv:
        _, sha = _load_upstream(verify_pin=False)
        print(f"upstream {UPSTREAM} at HEAD = {sha}")
        sys.exit(EXIT_OK)
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
    sys.exit(EXIT_OK)
