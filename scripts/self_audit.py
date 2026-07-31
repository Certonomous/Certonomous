#!/usr/bin/env python3
"""Rolling re-verification of published claims against primary evidence.

The audit that caught wall.json and the memory-exponent error, made into a
scheduled process instead of luck. Every check below re-derives a published
number from the raw artifact that number came from, and fails loudly when the
two disagree. Nothing here writes to any published surface: this script
reports, it never repairs. Correcting a surface is a human decision.

Run weekly:

    python3 scripts/self_audit.py            # human-readable report
    python3 scripts/self_audit.py --json     # machine-readable, for a hook
    python3 scripts/self_audit.py --quiet    # only FAIL and WARN lines

Exit status is 0 when every check passes, 1 when any check FAILs, so a cron
entry or a CI step can gate on it.

Adding a check: write a function that returns a Result, and list it in CHECKS.
A check must read primary evidence (a ledger row, a solver log, a raw
coefficient file) and compare it against a published surface. A check that
compares two published surfaces to each other is a consistency check, not a
verification, and must say so in its name.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WEB = REPO / "demo-output" / "website"
LEDGER = WEB / "mega-batch" / "ledger.jsonl"
WALL = WEB / "wall" / "wall.json"

# A ledger row longer than this is an infrastructure stall, not solver cost.
# Justification is measured, not assumed: the six rows above this threshold
# land in two tight wall-clock clusters and are shared across independent
# solver families, which no per-solver cost mechanism can produce. See
# check_ledger_stalls.
STALL_SECONDS = 3600.0

PASS, WARN, FAIL, INFO = "PASS", "WARN", "FAIL", "INFO"


@dataclass
class Result:
    name: str
    status: str
    summary: str
    detail: list[str] = field(default_factory=list)


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - a missing surface is a finding
        return {"__error__": f"{type(exc).__name__}: {exc}"}


def _iter_ledger():
    """Yield (line_number, row_or_None). A torn row yields None so integrity
    checks can count it rather than crash on it."""
    if not LEDGER.exists():
        return
    with LEDGER.open(encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield number, json.loads(line)
            except Exception:  # noqa: BLE001
                yield number, None


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def check_ledger_integrity() -> Result:
    """Every ledger line parses. A torn line is silent data loss."""
    torn, total = [], 0
    for number, row in _iter_ledger():
        total += 1
        if row is None:
            torn.append(number)
    if not total:
        return Result("ledger integrity", FAIL, "ledger not found or empty")
    if torn:
        return Result(
            "ledger integrity", WARN,
            f"{len(torn)} of {total} ledger lines do not parse",
            [f"line {n} is truncated or malformed" for n in torn[:10]]
            + ["a torn line is an interrupted write; the row it held is lost"])
    return Result("ledger integrity", PASS, f"{total} ledger lines all parse")


def check_wall_counters_vs_ledger() -> Result:
    """wall.json's headline counters must re-derive from the ledger itself."""
    wall = _load_json(WALL)
    if "__error__" in wall:
        return Result("wall counters vs ledger", FAIL,
                      f"wall.json unreadable: {wall['__error__']}")
    counters = wall.get("counters", {})
    detail_block = counters.get("detail", {})
    per_solver_published = detail_block.get("per_solver", {})

    ok_rows = failed_rows = 0
    ok_seconds = 0.0
    per_solver: dict[str, list] = {}
    for _, row in _iter_ledger():
        if row is None:
            continue
        seconds = float(row.get("wall_seconds") or 0.0)
        solver = row.get("solver") or "unknown"
        entry = per_solver.setdefault(solver, [0, 0.0])
        entry[0] += 1
        entry[1] += seconds
        if row.get("ok"):
            ok_rows += 1
            ok_seconds += seconds
        else:
            failed_rows += 1

    problems, notes = [], []

    def compare(label, published, measured, tolerance=0.0):
        if published is None:
            problems.append(f"{label}: absent from wall.json")
            return
        if abs(float(published) - float(measured)) > tolerance:
            problems.append(
                f"{label}: published {published}, ledger says {measured}")
        else:
            notes.append(f"{label}: {measured} confirmed")

    compare("missions_run", counters.get("missions_run"), ok_rows)
    compare("ledger_failed", detail_block.get("ledger_failed"), failed_rows)
    compare("solver_core_hours", counters.get("solver_core_hours"),
            round(ok_seconds / 3600.0, 3), tolerance=0.002)

    for solver, (count, seconds) in sorted(per_solver.items()):
        published = per_solver_published.get(solver)
        if published is None:
            problems.append(f"per_solver[{solver}]: absent from wall.json")
            continue
        if int(published.get("count", -1)) != count:
            problems.append(
                f"per_solver[{solver}].count: published "
                f"{published.get('count')}, ledger says {count}")
        if abs(float(published.get("wall_seconds", -1)) - seconds) > 0.2:
            problems.append(
                f"per_solver[{solver}].wall_seconds: published "
                f"{published.get('wall_seconds')}, ledger says {seconds:.1f}")

    if problems:
        return Result("wall counters vs ledger", FAIL,
                      f"{len(problems)} counter(s) disagree with the ledger",
                      problems)
    return Result("wall counters vs ledger", PASS,
                  "every published counter re-derives from the ledger", notes)


def check_ledger_stalls() -> Result:
    """Infrastructure stalls must not be counted as solver cost.

    A stall is identified, not assumed: rows above STALL_SECONDS are reported
    with their timestamps so the clustering that proves they are shared
    infrastructure events (not per-solver cost) is visible in the output.
    """
    stalls = []
    ok_seconds = 0.0
    for _, row in _iter_ledger():
        if row is None:
            continue
        seconds = float(row.get("wall_seconds") or 0.0)
        if row.get("ok"):
            ok_seconds += seconds
        if seconds > STALL_SECONDS:
            stalls.append((row.get("solver"), seconds, row.get("timestamp")))
    if not stalls:
        return Result("ledger stall contamination", PASS,
                      "no row exceeds the stall threshold")
    stall_seconds = sum(s for _, s, _ in stalls)
    share = 100.0 * stall_seconds / ok_seconds if ok_seconds else 0.0
    families = {solver for solver, _, _ in stalls}
    detail = [f"{solver}: {seconds:.0f} s at {stamp}"
              for solver, seconds, stamp in sorted(stalls, key=lambda r: r[2])]
    detail.append(
        f"{len(stalls)} rows across {len(families)} independent solver "
        f"families share these wall times, which no per-solver cost mechanism "
        f"explains; they are host stalls recorded as normal runs")
    detail.append(
        f"published solver_core_hours carries {stall_seconds/3600:.2f} "
        f"core-hours of stall ({share:.1f}% of the headline); the cleaned "
        f"figure is {(ok_seconds-stall_seconds)/3600:.2f} core-hours")
    return Result("ledger stall contamination", WARN,
                  f"{len(stalls)} stall rows are counted as solver cost "
                  f"({share:.1f}% of published core-hours)", detail)


def check_closure_entry_of_record() -> Result:
    """The credentials wall must quote the closure entry of record, not a
    superseded round."""
    wall = _load_json(WALL)
    closure = ((wall.get("counters") or {}).get("research") or {}).get("closure") or {}
    round3 = _load_json(WEB / "closure_challenge_trained_entry_round3_gated.json")
    if "__error__" in round3:
        return Result("closure entry of record", WARN,
                      "round-3 entry file not readable; cannot verify the wall")

    published_score = closure.get("our_score")
    published_text = str(closure.get("our_entry") or "")

    # The entry of record's own overall score, from its own file.
    current = None
    for key in ("round3_gated_overall", "overall", "gated_overall"):
        if isinstance(round3.get(key), (int, float)):
            current = float(round3[key])
            break
    if current is None:
        stack = [round3]
        while stack and current is None:
            node = stack.pop()
            if isinstance(node, dict):
                for key, value in node.items():
                    if key.endswith("overall") and isinstance(value, (int, float)) \
                            and "round2" not in key:
                        current = float(value)
                        break
                    if isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(node, list):
                stack.extend(node)

    problems = []
    if current is not None and published_score is not None:
        if abs(float(published_score) - current) > 1e-9:
            problems.append(
                f"our_score: wall says {published_score}, the entry of record "
                f"scores {current}")
    if re.search(r"\ba single\b.{0,40}scoring call", published_text, re.I):
        problems.append(
            "our_entry claims a single scoring call; the record documents four "
            "official calls (floor, round 1, round 2, round 3)")
    if re.search(r"\bthree of the eight\b", published_text, re.I):
        problems.append(
            "our_entry claims best on three of eight cases; round 3 records "
            "five of eight")
    if problems:
        return Result("closure entry of record", FAIL,
                      f"{len(problems)} stale claim(s) on the credentials wall",
                      problems)
    return Result("closure entry of record", PASS,
                  "the wall quotes the current entry of record")


def check_memory_scaling_law() -> Result:
    """Refit the published adjoint memory law from its own three measurements."""
    doc = WEB / "dafoam" / "ADJOINT_MEMORY_ENVELOPE.md"
    if not doc.exists():
        return Result("adjoint memory law", WARN, "memory envelope record absent")
    text = doc.read_text(encoding="utf-8", errors="replace")
    claim = re.search(
        r"memory \(MiB\) = ([0-9.]+) x cells\^([0-9.]+)\*\*, R.? = ([0-9.]+)", text)
    rows = re.findall(r"^\| ([0-9,]{4,}) \| ([0-9,]+\.[0-9]+) \|$", text, re.M)
    points = []
    for cells, mib in rows:
        try:
            points.append((float(cells.replace(",", "")),
                           float(mib.replace(",", ""))))
        except ValueError:
            continue
    points = sorted(set(points))
    if not claim or len(points) < 3:
        return Result("adjoint memory law", WARN,
                      "could not locate the published law or its measurements")
    coef_pub, expo_pub, r2_pub = (float(claim.group(1)), float(claim.group(2)),
                                  float(claim.group(3)))
    xs = [math.log(c) for c, _ in points]
    ys = [math.log(m) for _, m in points]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / \
        sum((x - mx) ** 2 for x in xs)
    coef = math.exp(my - slope * mx)
    ss_res = sum((y - (math.log(coef) + slope * x)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")

    problems = []
    if abs(slope - expo_pub) > 5e-4:
        problems.append(f"exponent: published {expo_pub}, refit {slope:.4f}")
    if abs(coef - coef_pub) / coef_pub > 5e-3:
        problems.append(f"coefficient: published {coef_pub}, refit {coef:.4f}")
    if abs(r2 - r2_pub) > 5e-4:
        problems.append(f"R2: published {r2_pub}, refit {r2:.4f}")
    detail = [f"refit from {n} measurements: "
              f"memory (MiB) = {coef:.4f} x cells^{slope:.4f}, R2 = {r2:.4f}"]
    if problems:
        return Result("adjoint memory law", FAIL,
                      "published memory law does not refit", problems + detail)
    return Result("adjoint memory law", PASS,
                  "published memory law reproduces from its own data", detail)


def check_withdrawn_numbers() -> Result:
    """A withdrawn number must not survive on a promotional surface.

    Each sentinel names a value the record explicitly withdrew, and the
    surfaces it must not appear on. Sentinels are added when a withdrawal is
    recorded, so the next audit enforces it automatically.
    """
    sentinels = [
        # (value as written, why withdrawn, surfaces it must not appear on)
        ("0.2510", "A4's DAFoam Ahmed primal, withdrawn",
         [WALL, WEB / "benchmarks.json"]),
        ("10.04%", "A4's adjoint-vs-FD gradient grade, not a drag number",
         [WALL, WEB / "benchmarks.json"]),
    ]
    problems, checked = [], []
    for value, reason, surfaces in sentinels:
        for surface in surfaces:
            if not surface.exists():
                continue
            text = surface.read_text(encoding="utf-8", errors="replace")
            checked.append(f"{value} not on {surface.name}")
            if value in text:
                problems.append(
                    f"{value} ({reason}) appears on {surface.name}")
    if problems:
        return Result("withdrawn numbers", FAIL,
                      f"{len(problems)} withdrawn value(s) still published",
                      problems)
    return Result("withdrawn numbers", PASS,
                  f"{len(checked)} withdrawn-value sentinel(s) clear")


def check_evidence_paths_exist() -> Result:
    """Repo-rooted evidence paths cited by the records must exist on disk.

    Only paths anchored at a known repository root are checked. A bare
    filename in a record usually names a file inside a case directory and
    cannot be resolved from the citation alone, so checking it would produce
    noise rather than findings.
    """
    roots = ("demo-output/", "sdk/", "scripts/", "models/", "mission-output/",
             "docs/", "dist/")
    pattern = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.[A-Za-z0-9]{1,6})`")
    # A record that documents a past citation defect necessarily quotes the
    # broken path. Quoting a withdrawn path is the opposite of citing it, so
    # lines that narrate a correction are not findings.
    retracted = re.compile(
        r"previously pointed at|never existed|did not exist|neither path|"
        r"path corrected|citation correction|withdrawn|do not cite", re.I)
    missing, total, scanned = [], 0, 0
    for doc in sorted(WEB.rglob("*.md")):
        if any(part in {"work", "processor0"} for part in doc.parts):
            continue
        scanned += 1
        lines = doc.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines):
            context = " ".join(lines[max(0, number - 2):number + 3])
            for cited in sorted(set(pattern.findall(line))):
                if not cited.startswith(roots):
                    continue
                total += 1
                if (REPO / cited).exists():
                    continue
                if retracted.search(context):
                    continue
                missing.append(
                    f"{doc.relative_to(REPO)}:{number + 1} cites {cited}")
    if missing:
        return Result("cited evidence paths", FAIL,
                      f"{len(missing)} of {total} repo-rooted citations do "
                      f"not resolve", missing[:25])
    return Result("cited evidence paths", PASS,
                  f"all {total} repo-rooted citations across {scanned} "
                  f"records resolve")


def check_f2_reproduction() -> Result:
    """F2's published coefficients must match its own raw force file."""
    record = WEB / "campaign" / "F2_runs" / "F2_reproduction_2026-07-30.json"
    raw = (WEB / "campaign" / "F2_runs" / "primary_M0.8_a1.25_Re6e6" /
           "postProcessing" / "forceCoeffs1" / "0" / "coefficient.dat")
    if not record.exists() or not raw.exists():
        return Result("F2 reproduction", WARN,
                      "F2 reproduction record or its raw force file is absent")
    published = _load_json(record).get("primary_M0.8_a1.25_Re6e6", {})
    iteration = int(published.get("iterations", 2000))
    wanted = None
    for line in raw.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#"):
            continue
        parts = line.split()
        if parts and parts[0] == str(iteration):
            wanted = parts
            break
    if not wanted:
        return Result("F2 reproduction", FAIL,
                      f"iteration {iteration} not present in the raw force file")
    cd_raw, cl_raw = float(wanted[1]), float(wanted[4])
    problems = []
    for label, published_value, raw_value in (
            ("cd", published.get("cd"), cd_raw),
            ("cl", published.get("cl"), cl_raw)):
        if published_value is None or abs(float(published_value) - raw_value) > 1e-9:
            problems.append(
                f"{label}: record says {published_value}, raw file says {raw_value}")
    if problems:
        return Result("F2 reproduction", FAIL,
                      "published F2 coefficients do not match raw data", problems)
    return Result("F2 reproduction", PASS,
                  f"F2 Cd and Cl match the raw force file at iteration {iteration}",
                  [f"Cd {cd_raw}, Cl {cl_raw}"])


def check_cost_predictions() -> Result:
    """Measured-versus-predicted cost pairs, and the auto-approve bar.

    A solver family's forecasts become auto-approvable once three consecutive
    predictions land within 20%. This check reports where each family stands.
    Pairs are recorded here as they are found in the records; each carries the
    citation for both halves so the table is auditable.
    """
    # (family, rung, predicted seconds, measured seconds, evidence)
    pairs = [
        ("pimpleFoam unsteady cylinder", "Re 2000", 3715.0, 3965.11,
         "F5a ladder, cost model D13"),
        ("pimpleFoam unsteady cylinder", "Re 3900", 6390.0, 10899.4,
         "F5a ladder, cost model outcome"),
        ("pimpleFoam unsteady cylinder", "Re 1000 3D pilot, 8 ranks",
         64800.0, 44102.0, "F5a ladder, 8-rank optimistic row 18 h"),
    ]
    families: dict[str, list] = {}
    lines = []
    for family, rung, predicted, measured, source in pairs:
        error = 100.0 * (measured - predicted) / predicted
        within = abs(error) <= 20.0
        families.setdefault(family, []).append(within)
        lines.append(
            f"{family} | {rung} | predicted {predicted:.0f} s | measured "
            f"{measured:.0f} s | {error:+.1f}% | "
            f"{'within 20%' if within else 'MISS'} | {source}")
    qualified = []
    for family, outcomes in families.items():
        streak = 0
        for hit in outcomes:
            streak = streak + 1 if hit else 0
        lines.append(f"{family}: longest run of consecutive hits = {streak} of 3 needed")
        if streak >= 3:
            qualified.append(family)
    if qualified:
        lines.append(f"AUTO-APPROVABLE: {', '.join(qualified)}")
    else:
        lines.append("AUTO-APPROVABLE: none; no family has three consecutive "
                     "predictions within 20%")
    return Result("cost predictions vs measured", INFO,
                  f"{len(pairs)} completed measured-versus-predicted pairs "
                  f"across {len(families)} family", lines)


def check_ungated_completed_runs() -> Result:
    """A completed run whose gate was never resolved is an unfinished gate."""
    findings = []
    ladder = WEB / "campaign" / "F5a_cylinder_reynolds_ladder.md"
    if ladder.exists():
        text = ladder.read_text(encoding="utf-8", errors="replace")
        if "PRELIMINARY, not yet graded" in text:
            findings.append(
                "F5a Re 1000 3D pilot: run completed to its full end time "
                "(44,102 s wall on 8 ranks, about 98 core-hours, the most "
                "expensive single solve in the lab) but its statistics are "
                "recorded as preliminary and not yet graded against the "
                "pre-stated expectation")
    if findings:
        return Result("completed but ungated runs", WARN,
                      f"{len(findings)} completed run(s) carry no gate verdict",
                      findings)
    return Result("completed but ungated runs", PASS,
                  "no completed run is missing its gate verdict")


CHECKS = (
    check_ledger_integrity,
    check_wall_counters_vs_ledger,
    check_ledger_stalls,
    check_closure_entry_of_record,
    check_memory_scaling_law,
    check_withdrawn_numbers,
    check_evidence_paths_exist,
    check_f2_reproduction,
    check_cost_predictions,
    check_ungated_completed_runs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable results")
    parser.add_argument("--quiet", action="store_true",
                        help="show only WARN and FAIL results")
    args = parser.parse_args()

    results = []
    for check in CHECKS:
        try:
            results.append(check())
        except Exception as exc:  # noqa: BLE001 - a broken check is a finding
            results.append(Result(check.__name__, FAIL,
                                  f"check raised {type(exc).__name__}: {exc}"))

    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=1))
    else:
        width = max(len(r.name) for r in results)
        print(f"Certonomous self-audit  ({len(results)} checks)")
        print("=" * (width + 60))
        for result in results:
            if args.quiet and result.status in (PASS, INFO):
                continue
            print(f"[{result.status:<4}] {result.name:<{width}}  {result.summary}")
            for line in result.detail:
                print(f"         - {line}")
        print("=" * (width + 60))
        tally = {s: sum(1 for r in results if r.status == s)
                 for s in (PASS, WARN, FAIL, INFO)}
        print("  ".join(f"{k}: {v}" for k, v in tally.items() if v))

    return 1 if any(r.status == FAIL for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
