#!/usr/bin/env python3
"""Score this lab's compute forecasts against what the runs actually cost.

WHY THIS EXISTS. `docs/CAPABILITY_STRATEGY.md` §4 proposes a rule:

    Cost model v2: per-family scaling laws with confidence bands;
    forecasts auto-approve when 3-for-3 within 20%.

That rule needs a scorecard, and a scorecard needs pairs — an estimate and the
measured cost of the same work. This script builds those pairs from the proposal
corpus and reports the hit rate. It is deliberately a GENERATOR rather than a
document: a calibration figure quoted into prose is stale the next time a run
finishes, which is L-79.

    python3 scripts/calibration_scorecard.py           # human-readable, stamped
    python3 scripts/calibration_scorecard.py --json    # for a doc build or a test

WHAT IT MEASURED ON ITS FIRST RUN, and the finding is about the record rather
than about anyone's estimating: **the pairs are almost all missing.** 19
proposals are marked `done`; 3 carry `measured_core_min`. So sixteen closed
pieces of work recorded no actual cost, and several of those costs are known and
written down elsewhere — the S1 inversion's 335.98 core-min and the
objective-repair run's 424.80 both sit in campaign records that the proposal file
never learned about. The number exists; the loop was never closed.

The consequence is the point: **§4's auto-approve rule cannot run at all**, not
because forecasting is hard but because the lab does not write the outturn back
to the thing that forecast it. A rule that cannot be evaluated reads exactly like
a rule that is being followed.

This script does not fix that. It measures it, and it says how far from
runnable the rule is, so the gap is a number instead of an impression.

FRAME. `demo-output/website/agenda/proposals/*.json`, every file, no filter. Not
`grep -r`: in this environment `grep` execs `ugrep --ignore-files` and honours
`.gitignore` (L-75). Pairs come only from files carrying BOTH `est_core_min` and
`measured_core_min` — a pair reconstructed by hand from a campaign record would
be a different measurement and is not made here.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROPOSALS = REPO / "demo-output/website/agenda/proposals"

#: §4's bar. A forecast counts as a hit when |measured - est| / measured <= this.
TOLERANCE = 0.20

#: §4 asks for three consecutive hits before forecasts auto-approve.
CONSECUTIVE_HITS_REQUIRED = 3


def _head() -> tuple[str, bool]:
    def run(*a: str) -> str:
        return subprocess.run(a, cwd=REPO, capture_output=True, text=True).stdout
    return (run("git", "rev-parse", "--short", "HEAD").strip() or "UNKNOWN",
            bool(run("git", "status", "--porcelain").strip()))


def load() -> tuple[list[dict], list[str]]:
    """Every proposal, plus the ones that would not parse.

    Unparseable files are RETURNED, not skipped. A scorecard that silently drops
    the files it cannot read reports a clean rate over the subset that happened
    to be well-formed -- the fail-open shape this lab keeps finding in its own
    instruments.
    """
    records, broken = [], []
    for path in sorted(PROPOSALS.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            broken.append(f"{path.name}: {type(exc).__name__}: {exc}")
            continue
        data["_file"] = path.name
        records.append(data)
    return records, broken


def score(records: list[dict]) -> dict:
    done = [r for r in records if r.get("status") == "done"]
    pairs, unpaired = [], []
    for r in done:
        est, meas = r.get("est_core_min"), r.get("measured_core_min")
        if est in (None, "") or meas in (None, ""):
            unpaired.append(r["_file"][:-5])
            continue
        est, meas = float(est), float(meas)
        # Error is relative to the MEASURED cost, not the estimate: the question
        # a budget holder asks is "how wrong was the forecast about what this
        # actually took", and dividing by the estimate flatters a low guess.
        err = abs(meas - est) / meas if meas else float("inf")
        pairs.append({"id": r["_file"][:-5], "est": est, "measured": meas,
                      "rel_error": err, "hit": err <= TOLERANCE})
    hits = [p for p in pairs if p["hit"]]
    return {
        "proposals": len(records),
        "done": len(done),
        "pairs": pairs,
        "unpaired_done": unpaired,
        "hit_rate": (len(hits) / len(pairs)) if pairs else None,
        "rule_runnable": len(pairs) >= CONSECUTIVE_HITS_REQUIRED,
        "rule_satisfied": len(pairs) >= CONSECUTIVE_HITS_REQUIRED
                          and all(p["hit"] for p in pairs[-CONSECUTIVE_HITS_REQUIRED:]),
    }


def collect() -> dict:
    records, broken = load()
    out = score(records)
    sha, dirty = _head()
    out["commit"] = sha
    out["working_tree_dirty"] = dirty
    out["unparseable"] = broken
    out["frame"] = ("demo-output/website/agenda/proposals/*.json, every file, "
                    "no filter; pairs require BOTH est_core_min and "
                    "measured_core_min on the same record")
    return out


def _emit(d: dict) -> None:
    print(f"CALIBRATION SCORECARD at {d['commit']}"
          f"{' +dirty working tree' if d['working_tree_dirty'] else ''}")
    print(f"FRAME: {d['frame']}")
    print()
    print(f"proposals {d['proposals']}  ·  done {d['done']}  ·  "
          f"scoreable pairs {len(d['pairs'])}")
    if d["unparseable"]:
        print(f"UNPARSEABLE ({len(d['unparseable'])}) -- counted, not skipped:")
        for b in d["unparseable"]:
            print(f"   {b}")
    print()
    if not d["pairs"]:
        print("NO PAIRS. The rule cannot be evaluated at all.")
    else:
        for p in d["pairs"]:
            mark = "HIT " if p["hit"] else "MISS"
            print(f"  {mark}  est {p['est']:>8.4g} → measured {p['measured']:>8.4g}"
                  f"   {p['rel_error']*100:5.1f}% off   {p['id']}")
        rate = d["hit_rate"]
        print(f"\n  hit rate within {int(TOLERANCE*100)}%: "
              f"{sum(p['hit'] for p in d['pairs'])} of {len(d['pairs'])}"
              f"  ({rate*100:.0f}%)")
    print()
    print(f"CAPABILITY_STRATEGY §4's rule ({CONSECUTIVE_HITS_REQUIRED}-for-"
          f"{CONSECUTIVE_HITS_REQUIRED} within {int(TOLERANCE*100)}%):")
    print(f"  runnable at all : {d['rule_runnable']}")
    print(f"  satisfied       : {d['rule_satisfied']}")
    print()
    n = len(d["unpaired_done"])
    print(f"THE BINDING CONSTRAINT IS THE RECORD, NOT THE FORECASTING.")
    print(f"  {n} proposal(s) are marked done and carry NO measured cost.")
    print(f"  Each is a scoreable pair the lab ran, paid for, and did not write down:")
    for u in d["unpaired_done"]:
        print(f"     {u}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)
    data = collect()
    if args.json:
        json.dump(data, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        _emit(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
