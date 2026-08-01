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
entry or a CI step can gate on it. The weekly schedule is one line and it is
not installed by this file, because installing a timer is a change to the box
and belongs to whoever owns the box:

    0 6 * * 1 cd /home/ubuntu/Certonomous && python3 scripts/self_audit.py \
        > demo-output/website/audit/self_audit_$(date +\\%Y\\%m\\%d).txt 2>&1

WHAT THIS IS AND IS NOT. It is a review aid. It names what it found and the
reason the check exists, and a human decides. It never edits a surface, and it
never will: a script that quietly corrects the record is a script that can
quietly corrupt it, and the whole point of the exercise is that a published
number changed only where somebody chose to change it.

TUNING. False positives are cheap and false negatives are not, and every
check here is tuned on that asymmetry. A false positive costs one reading. A
false negative costs a published number that nobody rechecks, which is how
every defect this file looks for got onto a surface in the first place. So a
check that is unsure reports, and says why it is unsure.

Adding a check: write a function that returns a Result, and list it in CHECKS.
A check must read primary evidence (a ledger row, a solver log, a raw
coefficient file) and compare it against a published surface. A check that
compares two published surfaces to each other is a consistency check, not a
verification, and must say so in its name.

The checks below fall into two rounds. The first ten came from the audit that
caught `wall.json` and the memory exponent. The second ten, added 2026-07-31,
each encode a defect that was caught once by hand, by somebody looking at
something else: a gate table row whose cited transcript no longer supports it,
a credential wall that would change on rebuild, a generator holding published
numbers as hard-coded constants, an FD grade against a retired band, a
statistical caption on a value no statistical procedure produced, a caller
trusting a band its own flag calls non-conclusive, a worker fleet declared on
a path that dispatches nothing, and a governed threshold restated as a literal.

One check here does NOT compare a published number to its evidence, and says
so rather than pretending otherwise: `check_bundle_drift` compares the shipped
laptop bundle to the tree it was built from. It is a consistency check between
two copies of the same code, in the sense the paragraph above defines, and it
earns its place because the bundle is the only copy of this code that leaves
the box and it went 32 commits behind with nothing noticing.
"""

from __future__ import annotations

import argparse
import ast
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


# --------------------------------------------------------------------------
# Round 2 checks, added 2026-07-31 under well W7.
#
# Each one is here because the defect it looks for was found once, by hand, by
# somebody who was looking at something else. The tuning rule for all of them
# is the asymmetry the certificate fix was tuned on: a false positive costs a
# reading, a false negative costs a published number nobody rechecks. So they
# are noisy on purpose, they name what they found and why, and none of them
# edits anything.
# --------------------------------------------------------------------------

MISSION = REPO / "mission-output"
CAMPAIGN = WEB / "campaign"
GATE_TABLE = CAMPAIGN / "NINE_ACT_GATE_TABLE.md"
ACTIVE = WEB / "ACTIVE_RESEARCH.md"
REGISTER = CAMPAIGN / "NOT_PASSING_REGISTER.md"
RESULTS = REPO / "models" / "curriculum" / "results"


def _md_rows(path: Path) -> list[list[str]]:
    """Cells of every pipe-delimited markdown row in a file, separators out."""
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= {"-", ":"} and c for c in cells):
            continue
        rows.append(cells)
    return rows


def check_gate_table_vs_transcripts() -> Result:
    """The published gate table must re-derive from the act transcripts.

    `gate_table.py` is the generator and the act transcript is its source of
    truth. If the published table and a fresh generation disagree, one of three
    things is true and all three are findings: the table was hand-edited, an
    act changed its output and the row is now unsupported, or the generator
    can no longer read an act it cites. This check does not say which. It says
    they disagree, and where.
    """
    if not GATE_TABLE.exists():
        return Result("gate table vs transcripts", FAIL,
                      "the published nine-act gate table is missing")
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        import gate_table  # noqa: PLC0415 - imported here so a broken
        generated = gate_table.rows()  # generator is a finding, not a crash
    except Exception as exc:  # noqa: BLE001
        return Result("gate table vs transcripts", FAIL,
                      f"the generator could not run: {type(exc).__name__}: {exc}")

    published = {}
    for cells in _md_rows(GATE_TABLE):
        if len(cells) >= 7 and cells[0] not in ("act",):
            published[cells[0]] = cells

    problems, pending = [], []
    for row in generated:
        case = row["case"]
        if case not in published:
            problems.append(f"{case}: generated but not published")
            continue
        pub = published[case]
        fields = (("reference", pub[2]), ("measured", pub[3]),
                  ("deviation", pub[4]), ("verdict", pub[5]))
        for key, published_value in fields:
            fresh = str(row[key])
            if fresh == PENDING_TOKEN and published_value != PENDING_TOKEN:
                pending.append(
                    f"{case}: published {key} is {published_value!r} but the "
                    f"generator now reads PENDING from "
                    f"{row['source']}; the cited artifact no longer supports "
                    f"the row as written")
                break
            if fresh != PENDING_TOKEN and fresh != published_value:
                problems.append(
                    f"{case}: {key} published {published_value!r}, "
                    f"re-derived {fresh!r} from {row['source']}")
    for case in published:
        if case not in {r["case"] for r in generated}:
            problems.append(f"{case}: published but the generator emits no such row")

    text = GATE_TABLE.read_text(encoding="utf-8", errors="replace")
    graded = sum(1 for r in generated
                 if str(r["verdict"]) != PENDING_TOKEN)
    claim = re.search(r"(\d+) of (\d+) acts have run; (\d+) carry a graded number",
                      text)
    if claim and int(claim.group(3)) != graded:
        problems.append(
            f"footer claims {claim.group(3)} graded rows; the generator "
            f"produces {graded}")

    if problems or pending:
        return Result("gate table vs transcripts", FAIL,
                      f"{len(problems) + len(pending)} row(s) do not re-derive "
                      f"from the artifact they cite", pending + problems)
    return Result("gate table vs transcripts", PASS,
                  f"all {len(generated)} rows re-derive from their cited "
                  f"transcript")


PENDING_TOKEN = "PENDING"


def check_wall_credentials_vs_results() -> Result:
    """Every credential on the wall must re-derive from its own result file.

    The join is positional and undocumented on the wall itself: a credential
    named `ahmed_25` is backed by `models/curriculum/results/ahmed_25.json`.
    That file is the primary evidence; `wall.json` is a build product of it.
    The wall is rebuilt by hand, so it can drift, and nothing else notices.
    """
    wall = _load_json(WALL)
    creds = wall.get("credentials") if isinstance(wall, dict) else None
    if not creds:
        return Result("wall credentials vs results", FAIL,
                      "wall.json carries no credentials array")
    sys.path.insert(0, str(REPO / "sdk"))
    try:
        from chief_engineer import lab  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        return Result("wall credentials vs results", WARN,
                      f"cannot import the re-derivation used by the wall "
                      f"builder: {type(exc).__name__}: {exc}")
    # The stored result file is the as-run archive. The wall displays what
    # `displayed_credential` makes of it today: the finest anchored rung, the
    # current grading rules. Comparing the wall against the raw tier would
    # flag every re-grade as a defect, so the comparison is against the same
    # re-derivation the builder performs. What this catches is drift: a wall
    # that would change if it were rebuilt right now.
    problems, checked = [], 0
    for cred in creds:
        name = cred.get("name")
        source = RESULTS / f"{name}.json"
        if not source.exists():
            problems.append(f"{name}: no result file at "
                            f"models/curriculum/results/{name}.json")
            continue
        raw = _load_json(source)
        checked += 1
        try:
            shown = lab.displayed_credential(raw)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{name}: re-derivation raised "
                            f"{type(exc).__name__}: {exc}")
            continue
        for wall_key, shown_key in (("tier", "tier"),
                                    ("measured", "on_reference_basis"),
                                    ("envelope", "envelope"),
                                    ("reason", "reason")):
            if wall_key not in cred or shown_key not in shown:
                continue
            if str(cred[wall_key]) != str(shown[shown_key]):
                problems.append(
                    f"{name}: wall {wall_key} is {cred[wall_key]!r}; a rebuild "
                    f"from models/curriculum/results/{name}.json would write "
                    f"{shown[shown_key]!r}")
        try:
            compared = float(raw.get("cd_compared"))
            reference = float(raw.get("reference_cd"))
            recomputed = abs(compared - reference) / abs(reference)
            stated = float(raw.get("relative_error"))
            if abs(recomputed - stated) > 5e-3:
                problems.append(
                    f"{name}: result file states relative_error {stated}, "
                    f"recomputed {recomputed:.4f} from its own cd_compared "
                    f"and reference_cd")
        except (TypeError, ValueError):
            problems.append(f"{name}: a compared value is not a number")
    if problems:
        return Result("wall credentials vs results", FAIL,
                      f"{len(problems)} credential field(s) do not re-derive",
                      problems)
    return Result("wall credentials vs results", PASS,
                  f"all {checked} credentials re-derive from their result file")


def check_benchmarks_vs_closure_record() -> Result:
    """`benchmarks.json` and its generator's hard-coded block must agree.

    This is the defect that would have overwritten a corrected card in
    silence. `sdk/scripts/build_benchmarks.py` holds the closure numbers as a
    module-level dict rather than reading them from the scored artifacts, so a
    hand-correction to `benchmarks.json` survives exactly until the next
    regeneration. The generator's own docstring says KEEP THIS IN SYNC. That
    instruction is a check waiting to be written, so here it is.
    """
    published = _load_json(WEB / "benchmarks.json")
    block = published.get("closure_challenge", {}) if isinstance(published, dict) else {}
    generator = REPO / "sdk" / "scripts" / "build_benchmarks.py"
    if not block:
        return Result("benchmarks vs closure record", FAIL,
                      "benchmarks.json carries no closure_challenge block")
    if not generator.exists():
        return Result("benchmarks vs closure record", WARN,
                      "the benchmarks generator is not on disk")
    problems = []
    try:
        tree = ast.parse(generator.read_text(encoding="utf-8"))
        constants = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                    isinstance(node.targets[0], ast.Name):
                try:
                    constants[node.targets[0].id] = ast.literal_eval(node.value)
                except Exception:  # noqa: BLE001
                    continue
        hard_coded = constants.get("_CLOSURE")
        if hard_coded is None:
            problems.append("_CLOSURE not found in the generator; the sync "
                            "rule this check enforces may have moved")
        else:
            for key in sorted(set(block) | set(hard_coded)):
                if block.get(key) != hard_coded.get(key):
                    problems.append(
                        f"{key}: published {block.get(key)!r}, the generator "
                        f"would write {hard_coded.get(key)!r}")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"could not read the generator: {type(exc).__name__}: {exc}")

    # And the published block against the scored artifacts themselves.
    entry = _load_json(WEB / "closure_challenge_trained_entry_round3_gated.json")
    harness = entry.get("official_test_harness_result", {}) if isinstance(entry, dict) else {}
    scored = harness.get("overall") or harness.get("overall_score")
    if scored is not None and block.get("our_score") is not None:
        if abs(float(scored) - float(block["our_score"])) > 1e-9:
            problems.append(
                f"our_score: benchmarks.json says {block['our_score']}, the "
                f"round-3 gated entry's own harness result is {scored}")
    if problems:
        return Result("benchmarks vs closure record", FAIL,
                      f"{len(problems)} closure field(s) disagree with the "
                      f"artifact or would regress on the next build", problems)
    return Result("benchmarks vs closure record", PASS,
                  "the published closure block matches the generator and the "
                  "scored entry of record")


_GRADE_WORDS = ("PASS", "CONDITIONAL", "FAIL")


def _fd_grade(percent: float, sign_flip: bool) -> str:
    """The current standard, verification charter section 7. One place."""
    if sign_flip or percent > 15.0:
        return "FAIL"
    if percent > 5.0:
        return "CONDITIONAL"
    return "PASS"


def check_fd_grades_current_standard() -> Result:
    """Every published FD grade is recomputed against the current standard.

    The retired band was "1 to 12 percent is normal". A row still graded
    against it reads as a pass and is not one. Charter clause: grades are
    recomputed every time a table is regenerated, and a row carrying a retired
    grade is a defect.
    """
    surfaces = [ACTIVE]
    surfaces += sorted(WEB.rglob("*.md"))
    seen, problems, ungraded = set(), [], []
    percent = re.compile(r"\*\*([\d.]+)%\*\*")
    for doc in surfaces:
        if doc in seen or any(p in {"work", "processor0"} for p in doc.parts):
            continue
        seen.add(doc)
        lines = doc.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines, 1):
            if not line.startswith("|") or "%" not in line:
                continue
            if "wrt" not in line and "derivative" not in line and "FD" not in line:
                continue
            found = percent.search(line)
            if not found:
                continue
            value = float(found.group(1))
            sign_flip = "sign flip" in line.lower()
            stated = [w for w in _GRADE_WORDS
                      if re.search(rf"\*\*{w}\*\*", line)]
            expected = _fd_grade(value, sign_flip)
            where = f"{doc.relative_to(REPO)}:{number}"
            if not stated:
                ungraded.append(f"{where}: {value}% carries no grade")
                continue
            if stated[0] != expected:
                problems.append(
                    f"{where}: graded {stated[0]} at {value}%"
                    f"{' with a sign flip' if sign_flip else ''}; the current "
                    f"standard grades it {expected}. Row reads: {line.strip()}")
    if problems:
        return Result("FD grades vs current standard", FAIL,
                      f"{len(problems)} FD row(s) carry a grade the current "
                      f"standard does not give", problems + ungraded[:5])
    return Result("FD grades vs current standard", PASS,
                  f"no published FD grade disagrees with the current standard",
                  ungraded[:10])


def _looks_like_interval(text: str) -> bool:
    """Deliberately conservative, and the same shape the certificate uses.

    One signed number with an optional unit, anchored end to end. Anything
    with prose in it is not an interval. A false positive here would let a
    fabricated confidence interval past; a false negative only costs a real
    interval a flag.
    """
    return bool(re.fullmatch(
        r"\s*[+-]?\s*(?:±|\+/-|\+-)?\s*\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
        r"\s*[A-Za-z%/°]{0,12}\s*", text or ""))


def check_statistical_labels() -> Result:
    """A statistical caption may only sit on a value a procedure produced.

    Two surfaces. The code that prints the caption, wherever a copy of it
    lives, must gate it on an interval test; an ungated copy in a bundle or a
    snapshot will seal fabricated intervals exactly as the tracked copy used
    to. And any transcript line carrying the caption must carry an interval
    next to it.
    """
    problems, checked = [], 0
    caption = "95% confidence interval"
    for source in sorted(REPO.rglob("certificate.py")):
        if "__pycache__" in source.parts:
            continue
        text = source.read_text(encoding="utf-8", errors="replace")
        if caption not in text:
            continue
        checked += 1
        if "_looks_like_interval" not in text:
            problems.append(
                f"{source.relative_to(REPO)} prints {caption!r} with no "
                f"interval test in the file; every envelope it is handed "
                f"becomes a statistical claim")
    for transcript in sorted(MISSION.glob("*/transcript.*")):
        checked += 1
        for number, line in enumerate(
                transcript.read_text(encoding="utf-8",
                                     errors="replace").splitlines(), 1):
            low = line.lower()
            if "confidence interval" not in low:
                continue
            if any(word in low for word in
                   ("no 95", "not a confidence", "no confidence",
                    "point estimate", "declin", "is not an interval")):
                continue
            if "±" in line or "+-" in line or "+/-" in line:
                continue
            problems.append(
                f"{transcript.relative_to(REPO)}:{number} says confidence "
                f"interval with no interval on the line: {line.strip()[:120]}")
    if problems:
        return Result("statistical labels", FAIL,
                      f"{len(problems)} statistical label(s) sit on something "
                      f"that is not an interval", problems)
    return Result("statistical labels", PASS,
                  f"{checked} caption site(s) and transcripts carry no "
                  f"unearned confidence interval")


def _py_sources() -> list[Path]:
    out = []
    for root in ("sdk/workflows", "sdk/chief_engineer"):
        base = REPO / root
        if base.exists():
            out += [p for p in sorted(base.rglob("*.py"))
                    if "__pycache__" not in p.parts]
    return out


def check_nonconclusive_band_readers() -> Result:
    """A caller reading `band_abs` must also read `conclusive`.

    `eca_hoekstra_band` returns a conservative fallback band even when it sets
    `conclusive` False. Five independent authors read the number and printed
    it. That is a fact about the return shape, so the check is on the shape:
    a function that calls the ladder fit, reads `band_abs` off it, and never
    mentions `conclusive` or `reportable_band` is the same defect again.

    Scoped to callers of the fit rather than to every reader of a key named
    `band_abs`, because other producers use the same key for bands that carry
    no conclusiveness flag at all, and flagging those would be noise with no
    defect behind it. `uq.py` itself is exempt: it owns the return shape.
    """
    problems, checked = [], 0
    for source in _py_sources():
        if source.name == "uq.py":
            continue
        text = source.read_text(encoding="utf-8", errors="replace")
        if "band_abs" not in text or "eca_hoekstra_band" not in text:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError as exc:
            problems.append(f"{source.relative_to(REPO)} does not parse: {exc}")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            body = ast.get_source_segment(text, node) or ""
            if "band_abs" not in body or "eca_hoekstra_band(" not in body:
                continue
            checked += 1
            if "conclusive" in body or "reportable_band" in body:
                continue
            problems.append(
                f"{source.relative_to(REPO)}:{node.lineno} {node.name}() fits "
                f"a refinement ladder, reads band_abs off it and never reads "
                f"conclusive; on a failed ladder that number is a fallback, "
                f"not a measured uncertainty")
    if problems:
        return Result("non-conclusive band readers", FAIL,
                      f"{len(problems)} reader(s) trust a band without its flag",
                      problems)
    return Result("non-conclusive band readers", PASS,
                  f"all {checked} band_abs readers also read the flag")


# The channel a `combine_expanded` keyword contributes, and the keyword the
# display record uses for the same channel. Two names for one thing is exactly
# how a term ends up in a total that the table beside it does not show.
_COMBINE_TO_CHANNEL = {"input_2sigma": "input", "numerical_abs": "numerical",
                       "model_abs": "model"}
_DISPLAY_KEYWORD = {"input": "input_2sigma", "numerical": "numerical",
                    "model": "model"}
# The shared channel builder, and the module that owns it. An act calling it
# displays whatever that builder declares, so the declaration is read from
# there rather than treated as unknown.
_SHARED_BUILDER = ("certificate_channels", "sdk/workflows/geometry_study.py")


def _declared_channels(text: str) -> dict[str, bool] | None:
    """Which channels an `uncertainty_channels` call in this source shows as
    quantified. None when the source makes no such call."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    shown: dict[str, bool] = {}
    seen = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node.func, "id", getattr(node.func, "attr", "")) != \
                "uncertainty_channels":
            continue
        seen = True
        for keyword in node.keywords:
            for channel, display in _DISPLAY_KEYWORD.items():
                if keyword.arg != display:
                    continue
                quantified = not (isinstance(keyword.value, ast.Constant)
                                  and keyword.value.value is None)
                # Any call that quantifies the channel counts: an act with
                # two call sites shows the channel if either one carries a
                # figure.
                shown[channel] = shown.get(channel, False) or quantified
    return shown if seen else None


def check_channel_totals_use_one_rule() -> Result:
    """A reported total is the one combination rule, over the channels shown.

    Two halves, and the doctrine states both.

    (a) An act that quantifies two or more V&V-20 channels reports a total,
        and computes it through `combine_expanded` rather than inventing its
        own arithmetic. Eleven acts route through that call today; the check
        is here so the twelfth does too.

    (b) A term may not be in the total that the channel table reports
        unquantified. That is `combine_expanded`'s own contract, in its own
        docstring: the combined band is never presented without the channel
        table one level down. A total wider than the channels displayed is a
        difference the viewer has no way to account for, and unquantified
        means nobody measured it, not zero.

    This is a consistency check between two surfaces of the same act, not a
    re-derivation from primary evidence, and it is named that way.
    """
    problems, checked = [], 0
    shared_text = (REPO / _SHARED_BUILDER[1]).read_text(
        encoding="utf-8", errors="replace") \
        if (REPO / _SHARED_BUILDER[1]).exists() else ""
    shared_declared = _declared_channels(shared_text) or {}
    for source in _py_sources():
        if source.name == "uq.py" or "workflows" not in source.parts:
            continue
        text = source.read_text(encoding="utf-8", errors="replace")
        if "uncertainty_channels(" not in text and \
                f"{_SHARED_BUILDER[0]}(" not in text:
            continue
        declared = _declared_channels(text)
        if declared is None:
            # The act uses the shared builder, so it displays what the
            # builder declares.
            if f"{_SHARED_BUILDER[0]}(" not in text:
                continue
            declared = dict(shared_declared)
        checked += 1
        rel = source.relative_to(REPO)
        quantified = sorted(k for k, v in declared.items() if v)
        combines = "combine_expanded" in text
        if len(quantified) >= 2 and not combines:
            problems.append(
                f"{rel} quantifies {len(quantified)} channels "
                f"({', '.join(quantified)}) and reports no combined band "
                f"through the one rule")
        if not combines:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if getattr(node.func, "id",
                       getattr(node.func, "attr", "")) != "combine_expanded":
                continue
            for keyword in node.keywords:
                channel = _COMBINE_TO_CHANNEL.get(keyword.arg or "")
                if channel is None:
                    continue
                contributes = not (isinstance(keyword.value, ast.Constant)
                                   and keyword.value.value is None)
                if contributes and not declared.get(channel, False):
                    problems.append(
                        f"{rel}:{node.lineno} puts the {channel} channel in "
                        f"the total while the act's own channel table reports "
                        f"it unquantified; the total is wider than the "
                        f"breakdown it is shown beside")
    if problems:
        return Result("channel totals vs the one rule", FAIL,
                      f"{len(problems)} total(s) do not match the channels "
                      f"they are shown with", problems)
    return Result("channel totals vs the one rule", PASS,
                  f"all {checked} channel-reporting act(s) combine through "
                  f"the one rule over the channels they display")


def check_declared_fleet_vs_work() -> Result:
    """A fleet declared on a restored path is a fleet the run never used.

    The hump act called `set_workers(ranks)` inside its warm-solve branch,
    where the mesh and the solve are both restored from cache and nothing is
    dispatched. The declaration reaches the worker numeral and the spend line,
    so it is a claim about the run. This finds the shape: a non-zero worker
    declaration inside a branch whose condition is a cache restore.
    """
    problems, branches = [], 0
    for source in _py_sources():
        text = source.read_text(encoding="utf-8", errors="replace")
        if "set_workers" not in text:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            test = (ast.get_source_segment(text, node.test) or "").lower()
            if not any(word in test for word in ("warm", "cached", "restore")):
                continue
            branches += 1
            # Body only. The `else` of a warm-path branch is the cold path,
            # where the fleet is real and the declaration is correct.
            inner_nodes = [n for stmt in node.body for n in ast.walk(stmt)]
            for inner in inner_nodes:
                if not isinstance(inner, ast.Call):
                    continue
                func = inner.func
                if not (isinstance(func, ast.Attribute)
                        and func.attr == "set_workers"):
                    continue
                if not inner.args:
                    continue
                first = inner.args[0]
                if isinstance(first, ast.Constant) and first.value == 0:
                    continue
                problems.append(
                    f"{source.relative_to(REPO)}:{inner.lineno} declares "
                    f"workers inside a restored-path branch "
                    f"({test.strip()[:60]}); the run dispatches nothing there")
    if problems:
        return Result("declared fleet vs work", FAIL,
                      f"{len(problems)} worker declaration(s) on a path that "
                      f"runs no parallel work", problems)
    return Result("declared fleet vs work", PASS,
                  f"no worker declaration on any of {branches} restored-path "
                  f"branches")


# Governed thresholds and the parameter names that must not restate them as
# literals. The monitor held its own 20.0 for five days after the approved
# constant moved to 10.0, and every caller taking the default judged on a
# threshold nobody approved.
GOVERNED_THRESHOLDS = {
    "flag_multiple": ("sdk/chief_engineer/log_signatures.py", "FLAG_MULTIPLE"),
    "fatal_multiple": ("sdk/chief_engineer/log_signatures.py", "FATAL_MULTIPLE"),
}


def check_restated_thresholds() -> Result:
    """A governed threshold restated as a literal is a defect at review.

    Whether or not it currently agrees with its source. On the day it stops
    agreeing, nothing announces it.
    """
    problems, pinned = [], 0
    for source in _py_sources():
        text = source.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            args = node.args
            names = [a.arg for a in args.args + args.kwonlyargs]
            defaults = ([None] * (len(args.args) - len(args.defaults))
                        + list(args.defaults) + list(args.kw_defaults))
            for name, default in zip(names, defaults):
                if name not in GOVERNED_THRESHOLDS or default is None:
                    continue
                governed_file, governed_name = GOVERNED_THRESHOLDS[name]
                if isinstance(default, ast.Name):
                    pinned += 1
                    continue
                if isinstance(default, ast.Constant) and isinstance(
                        default.value, (int, float)):
                    problems.append(
                        f"{source.relative_to(REPO)}:{node.lineno} "
                        f"{node.name}() restates {name} as the literal "
                        f"{default.value}; the governed value is "
                        f"{governed_name} in {governed_file}")
    if problems:
        return Result("restated thresholds", FAIL,
                      f"{len(problems)} governed threshold(s) restated as a "
                      f"literal", problems)
    return Result("restated thresholds", PASS,
                  f"{pinned} threshold default(s) read the governed constant")


def check_register_group_counts() -> Result:
    """The failure register's declared counts must match its own entries.

    A miscount is not cosmetic here. The register is the lab's inventory of
    what did not work, and a group that says five and holds four has lost an
    entry without anybody noticing.
    """
    if not REGISTER.exists():
        return Result("register group counts", FAIL,
                      "NOT_PASSING_REGISTER.md is missing")
    lines = REGISTER.read_text(encoding="utf-8", errors="replace").splitlines()
    groups, current, entries = [], None, 0
    declared = None
    for line in lines:
        if line.startswith("## GROUP"):
            if current is not None:
                groups.append((current, declared, entries))
            current, declared, entries = line[3:].strip(), None, 0
        elif line.startswith("## ") and current is not None:
            groups.append((current, declared, entries))
            current, declared, entries = None, None, 0
        elif current is not None:
            found = re.match(r"\*\*Count:\s*(\d+)\s*cases?\*\*", line.strip())
            if found:
                declared = int(found.group(1))
            elif line.startswith("### "):
                entries += 1
    if current is not None:
        groups.append((current, declared, entries))
    problems = []
    for name, count, actual in groups:
        if count is None:
            problems.append(f"{name}: declares no count")
        elif count != actual:
            problems.append(f"{name}: declares {count}, holds {actual} entries")
    total_declared = None
    for cells in _md_rows(REGISTER):
        if cells and cells[0].strip().upper().startswith("**TOTAL"):
            digits = re.search(r"(\d+)", cells[1] if len(cells) > 1 else "")
            if digits:
                total_declared = int(digits.group(1))
    total_actual = sum(a for _, _, a in groups)
    if total_declared is not None and total_declared != total_actual:
        problems.append(f"summary total declares {total_declared}, the groups "
                        f"hold {total_actual}")
    if problems:
        return Result("register group counts", WARN,
                      f"{len(problems)} count(s) in the failure register do "
                      f"not match its own entries",
                      problems + ["counted by heading; one entry can cover "
                                  "several cases, so a mismatch is a reading, "
                                  "not automatically an error"])
    return Result("register group counts", PASS,
                  f"{len(groups)} groups, {total_actual} entries, every count "
                  f"agrees")


def _uq_module():
    sys.path.insert(0, str(REPO / "sdk"))
    from chief_engineer import uq  # noqa: PLC0415
    return uq


# Two fixtures, chosen so the union of their keys covers every branch of the
# fit a stored study can land in: one ladder that certifies and one that is
# declined. Both are synthetic and neither is published anywhere; they exist
# only to ask the fit what it currently emits.
#
# THE UNION IS A CEILING, NOT THE REQUIREMENT. Both fixtures are monotone, so
# both reach the branch that fits an order and the union carries
# `asymptotic` and `richardson_extrapolated`. A non-monotone ladder never
# fits an order, and its fit deliberately does NOT record those two -- a guard
# that never ran is absent, not False. Measuring every study against the union
# therefore demands fields the study's own fit refuses to invent. So the union
# is only the fallback, used when a record cannot be refitted; a record that
# stores its rungs is measured against what ITS OWN fit emits (`_own_fit`).
_FIT_FIXTURES = (
    # phi = 0.42 + 0.05 h^2 on an 8x-per-rung 3D ladder: certifies at p = 2.
    ([10000, 80000, 640000], [1.22, 0.62, 0.47], 3),
    # The cylinder vortex-shedding rungs: declined, and by two guards at once.
    ([2496, 5032, 8640], [0.1245, 0.1490, 0.1578], 3),
)

# What it costs to fix each of the two faults below, stated where the fault is
# reported. THE DEFECT THIS REPLACES: both checks reported a missing field and
# said repairing it was "a decision about compute", which readers priced as a
# re-run of the study. It is not. A stored study carries its own rungs under
# `levels`, with cell counts and functionals; the fit is arithmetic on those,
# so it can be recomputed from the record in place for nothing. Of the eight
# fitted studies in this corpus, seven store their rungs and one does not, and
# only that one needs a solve. A remedy quoted an order of magnitude too high
# is a reason not to do the work, so the price now travels with the fault.
REMEDY_REFIT = ("remedy: refit in place from the {n} rungs this study already "
                "stores under levels[], through uq.study_numerical; NO COMPUTE")
REMEDY_NO_RUNGS = ("remedy: this record stores no rungs, so nothing here can "
                   "be recomputed from it; NEEDS COMPUTE (re-run the ladder) "
                   "or the record must be marked unverifiable or withdrawn")


def _own_fit(uq, study):
    """Re-run the fit that produced this study, from the study's own rungs.

    Returns the fit dict, or None when the record cannot be refitted -- either
    it stores no usable rungs, or no current fit reproduces the method string
    it has on file, which means the stored numbers came from something other
    than the code running today. Spends no compute: `levels` already holds
    every cell count and functional the fit reads.
    """
    numerical = study.get("numerical") or {}
    levels = study.get("levels")
    if not isinstance(levels, list) or len(levels) < 3:
        return None
    try:
        cells = [float(level["cells"]) for level in levels]
        values = [float(level["cd"]) for level in levels]
    except (KeyError, TypeError, ValueError):
        return None
    # Monotonicity picks the branch, and monotonicity does not depend on dim,
    # so a study that has not yet recorded its dim can be read at 3 without
    # changing which fields its fit emits.
    dim = numerical.get("dim") or 3
    for fit_fn in (uq.eca_hoekstra_band, uq.ladder_band):
        try:
            fit = fit_fn(cells, values, dim=int(dim))
        except Exception:  # noqa: BLE001 - a fit that raises is not the one
            continue
        if fit.get("method") == numerical.get("method"):
            return fit
    return None


def _study_rungs(study) -> int:
    levels = study.get("levels")
    return len(levels) if isinstance(levels, list) else 0


# Why a study is out of scope for the two study checks below, in the study's
# own terms. THE DEFECT THIS REPLACES: both checks narrowed to refinement fits
# with a bare `continue`, so a record they could not read simply was not in the
# report -- not as a pass, not as a fault, not at all. Two of the ten stored
# studies were invisible that way, and one of them was aortic-valve, whose
# `conclusive: True` was a hardcoded literal and whose band was the only one in
# the corpus reaching a live certificate. The record that cannot be checked
# against its own evidence was the record the checks could not see, and an
# unauditable record is indistinguishable from a clean one. So every stored
# study is now either checked or named here with the reason, and the count of
# each rides on every verdict line.
def _out_of_scope(study) -> str | None:
    """The reason this study is not a refinement fit, or None if it is one."""
    numerical = study.get("numerical") or {}
    if not numerical:
        return "no numerical block at all; nothing here states a fitted band"
    if "conclusive" not in numerical:
        return ("its numerical block records no `conclusive` verdict, so no "
                "fit ever adjudicated it")
    if "observed_order" not in numerical:
        kind = numerical.get("channel_kind")
        method = str(numerical.get("method") or "").split(";")[0].strip()
        what = f"{kind}" if kind else "not produced by a refinement fit"
        return (f"its numerical block records no `observed_order`, so it did "
                f"not come out of a refinement fit: {what}"
                + (f" ({method})" if method else ""))
    return None


def check_studies_carry_what_the_fit_records() -> Result:
    """A stored study must carry every field its own fit produces.

    THE DEFECT. Both study writers built the `numerical` block from a
    hand-typed list of keys. A hand-typed list keeps working when the fit
    learns to record something new, and drops the new field on every study it
    writes, in silence. When `eca_hoekstra_band` began recording the
    dimensionality its band was fitted with, not one stored study picked it up
    -- not because they predate the field, but because nothing was copying it.
    A record that omits what it was not told to keep looks complete, which is
    worse than one that never had the field: nothing on the file says a field
    is missing rather than absent.

    THE CHECK. Ask the fit what it emits today, subtract the exclusions the
    writers name out loud (`uq.STUDY_NUMERICAL_DROPS`), and read every stored
    study's `numerical` block for the remainder. A study written by an older
    writer is reported, not repaired -- this file never writes.

    WHAT "the fit emits today" MEANS PER STUDY. Preferably, the study's own
    fit re-run from the study's own stored rungs (`_own_fit`): a non-monotone
    ladder's fit never evaluates the post-order guards, so demanding
    `richardson_extrapolated` of it would be demanding an invented number.
    Only a record that cannot be refitted falls back to the union over the
    fixtures, which is a ceiling rather than the requirement.

    AND WHAT IT COSTS. Each fault now names its own remedy and whether that
    remedy needs compute. This check used to say only that repair "is a
    decision about compute", which read as a re-run of the study; for every
    record that stores its rungs the repair is arithmetic on data already on
    disk, and pricing it as a solve is how a cheap fix goes undone.

    This compares a published record against a re-derivation from the code
    that produces it, which is a verification of the record, not a
    surface-to-surface consistency check.
    """
    try:
        uq = _uq_module()
    except Exception as exc:  # noqa: BLE001
        return Result("studies carry what the fit records", WARN,
                      f"cannot import the fit: {type(exc).__name__}: {exc}")
    expected: set[str] = set()
    for cells, values, dim in _FIT_FIXTURES:
        for fit in (uq.eca_hoekstra_band, uq.ladder_band):
            try:
                expected |= set(fit(cells, values, dim=dim))
            except Exception as exc:  # noqa: BLE001
                return Result("studies carry what the fit records", FAIL,
                              f"{fit.__name__} raised on a fixture: "
                              f"{type(exc).__name__}: {exc}")
    expected -= set(uq.STUDY_NUMERICAL_DROPS)
    expected -= {"band_abs_middle"}   # a runner-chosen alternative to band_abs
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
    problems, notes, skipped, checked = [], [], [], 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            problems.append(f"{path.name}: does not parse")
            continue
        numerical = study.get("numerical") or {}
        # Only blocks that came out of a refinement fit are in scope. Every
        # branch of both fits sets `observed_order`, even when it sets it to
        # None, and no other producer does; the valve's quadrature convergence
        # of a reduced-order model is a different shape and is not measured
        # against this one. Scoping on the method text instead would silently
        # exempt exactly the declined ladders this check most needs to read,
        # because a guard-failure method string does not mention a mesh.
        #
        # OUT OF SCOPE IS NOT INVISIBLE. Anything this check cannot read is
        # named, with the reason, on the same report.
        reason = _out_of_scope(study)
        if reason:
            skipped.append(f"{path.stem}: SKIPPED, not in scope for this "
                           f"check -- {reason}")
            continue
        checked += 1
        rungs = _study_rungs(study)
        own = _own_fit(uq, study)
        if own is not None:
            want = (set(own) - set(uq.STUDY_NUMERICAL_DROPS)
                    - {"band_abs_middle"})
            remedy = REMEDY_REFIT.format(n=rungs)
        else:
            want = expected
            if rungs >= 3:
                # It stores rungs, and still cannot be refitted. That is a
                # sharper finding than a missing field: the stored method
                # string is one no fit running today produces.
                notes.append(
                    f"{path.stem}: stores {rungs} rungs but no current fit "
                    f"reproduces its stored method string, so its numbers "
                    f"were not produced by the fit running today; measured "
                    f"against the fixture ceiling instead")
                remedy = ("remedy: establish which producer wrote this block "
                          "before refitting it; NO COMPUTE to find out")
            else:
                remedy = REMEDY_NO_RUNGS
        missing = sorted(want - set(numerical))
        if missing:
            problems.append(
                f"{path.stem}: numerical block is missing "
                f"{', '.join(missing)}; its own fit records "
                f"{len(want)} field(s) and this study carries "
                f"{len(want) - len(missing)}. {remedy}")
    scope = (f"{checked} of {checked + len(skipped)} stored study(s) in "
             f"scope, {len(skipped)} named as skipped")
    if problems:
        needs_compute = sum(1 for p in problems if "NEEDS COMPUTE" in p)
        return Result("studies carry what the fit records", FAIL,
                      f"{len(problems)} stored study(s) omit a field their "
                      f"own fit produces; {len(problems) - needs_compute} are "
                      f"refittable in place at no compute, {needs_compute} "
                      f"need a solve; {scope}", problems + notes + skipped)
    if notes:
        return Result("studies carry what the fit records", INFO,
                      f"all {checked} fitted study(s) carry every field their "
                      f"own fit records; {len(notes)} could not be refitted; "
                      f"{scope}", notes + skipped)
    return Result("studies carry what the fit records", PASS,
                  f"all {checked} fitted study(s) carry every field their own "
                  f"fit records; {scope}", skipped)


def check_declined_ladders_name_their_guard() -> Result:
    """A declined ladder must record WHICH guard held it, not only a sentence.

    THE DEFECT. The cylinder vortex-shedding ladder was declined for an
    observed order of 3.646, outside the credible window. Fitted on its own
    two-dimensional mesh that order is 2.430, inside it. The act stayed
    declined, because its extrapolated Strouhal number overshoots the range it
    measured and that guard does not depend on dimensionality at all. So the
    verdict never moved and the stated reason was wrong for a day, and nothing
    on the record could show it: `uq.not_conclusive_reason` DERIVES the
    sentence, so it silently reassigned itself when the arithmetic changed.

    THE CHECK. Every declined ladder in a stored study must carry
    `not_conclusive_guard` and a `guards` map, and the guard it names must be
    one the map actually records as failing. A verdict resting on more than
    one guard is reported as INFO, not a fault: it is the case where fixing
    the stated reason would not move the verdict, and somebody should know.

    AND WHAT IT COSTS. A ladder that stores its rungs can have its guard map
    recomputed from them in place, for nothing; only a record with no rungs
    behind it needs a solve. The remedy and its price are stated on each
    fault, because this check's first report was read as calling for eight
    re-runs when seven of the eight needed no compute at all.
    """
    try:
        uq = _uq_module()
    except Exception as exc:  # noqa: BLE001
        return Result("declined ladders name their guard", WARN,
                      f"cannot import the fit: {type(exc).__name__}: {exc}")
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
    problems, notes, skipped, checked = [], [], [], 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            problems.append(f"{path.name}: does not parse")
            continue
        numerical = study.get("numerical") or {}
        # SCOPE. A record that declines itself must name the guard that
        # declined it. That requirement does not depend on the record having
        # come out of a mesh fit, so the `observed_order` gate that used to sit
        # here is gone: it excluded the aortic-valve study, which is exactly
        # the record that most needed reading, since its verdict was a typed
        # literal rather than anything a guard produced. Everything out of
        # scope is named below with its reason instead of vanishing.
        if not numerical:
            skipped.append(f"{path.stem}: SKIPPED, not in scope for this "
                           f"check -- no numerical block at all, so there is "
                           f"no verdict here to decline")
            continue
        if "conclusive" not in numerical:
            skipped.append(f"{path.stem}: SKIPPED, not in scope for this "
                           f"check -- its numerical block records no "
                           f"`conclusive` verdict, so nothing adjudicated it "
                           f"either way")
            continue
        if numerical.get("conclusive") is not False:
            skipped.append(f"{path.stem}: SKIPPED, not in scope for this "
                           f"check -- conclusive is "
                           f"{numerical.get('conclusive')!r}, not a decline, "
                           f"so no guard is holding it")
            continue
        checked += 1
        rungs = _study_rungs(study)
        remedy = (REMEDY_REFIT.format(n=rungs) if rungs >= 3
                  else REMEDY_NO_RUNGS)
        guard = numerical.get("not_conclusive_guard")
        guards = numerical.get("guards")
        if not guard or not isinstance(guards, dict):
            problems.append(
                f"{path.stem}: declined, and the record does not say which "
                f"guard held it; the reason on any surface showing this "
                f"study is derived from the numbers as they stand today, not "
                f"the guard that fired when the fit ran. {remedy}")
            continue
        if guards.get(guard) is not False:
            problems.append(
                f"{path.stem}: states guard {guard!r} but its own guard map "
                f"records that guard as {guards.get(guard)!r}. {remedy}")
            continue
        held = [k for k, v in guards.items() if v is False]
        if len(held) > 1:
            notes.append(
                f"{path.stem}: declined on {guard!r} and would stay declined "
                f"on {', '.join(sorted(set(held) - {guard}))}")
    scope = (f"{checked} of {checked + len(skipped)} stored study(s) in "
             f"scope, {len(skipped)} named as skipped")
    if problems:
        needs_compute = sum(1 for p in problems if "NEEDS COMPUTE" in p)
        return Result("declined ladders name their guard", FAIL,
                      f"{len(problems)} declined ladder(s) do not record the "
                      f"guard that held them; "
                      f"{len(problems) - needs_compute} are refittable in "
                      f"place at no compute, {needs_compute} need a solve; "
                      f"{scope}", problems + notes + skipped)
    if notes:
        return Result("declined ladders name their guard", INFO,
                      f"all {checked} declined ladder(s) name their guard; "
                      f"{len(notes)} rest on more than one; {scope}",
                      notes + skipped)
    return Result("declined ladders name their guard", PASS,
                  f"all {checked} declined ladder(s) name the guard that held "
                  f"them; {scope}", skipped)


def check_order_window_declines_state_their_dimensionality() -> Result:
    """VERIFICATION_CHARTER section 3.1 rule 3, which had no checker.

    THE RULE. A ladder declined for an observed order outside the credible
    window must have its dimensionality checked before the decline is
    believed, because that is the one verdict the dimensionality assumption
    can fabricate. Changing `dim` divides every observed order by exactly 1.5
    and leaves a conclusive band and the extrapolated value untouched, so the
    assumption cannot corrupt a number; it can only wrongly admit or wrongly
    reject a ladder. Rules 1 and 2 of that section already have checkers
    (`uq.ladder_band` raises on an unstated `dim`, and the field-set check
    above reads `dim` off every stored study). Rule 3 had none.

    THE CHECK, two parts, both zero compute.

    1. A study declined with `order_window` among its failing guards must
       carry a `dimensionality` block whose `dim` agrees with the one its fit
       used, established from the case files rather than from the body's name,
       with at least one piece of evidence named.
    2. The same ladder is refit from its own stored rungs at the OTHER
       dimensionality, and the report says whether `order_window` would flip
       and whether the verdict would move with it. A flip that changes no
       verdict is the ordinary case and is INFO; a flip that would make the
       ladder conclusive is the case the charter exists to catch, and is a
       fault, because a published decline would then rest on an assumption
       rather than on the measurements.
    """
    try:
        uq = _uq_module()
    except Exception as exc:  # noqa: BLE001
        return Result("order-window declines state their dimensionality", WARN,
                      f"cannot import the fit: {type(exc).__name__}: {exc}")
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
    problems, notes, checked = [], [], 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            continue
        numerical = study.get("numerical") or {}
        guards = numerical.get("guards")
        if numerical.get("conclusive") is not False or not isinstance(
                guards, dict) or guards.get("order_window") is not False:
            continue
        checked += 1
        block = study.get("dimensionality")
        if not isinstance(block, dict) or not block.get("evidence"):
            problems.append(
                f"{path.stem}: declined on order_window and states no "
                f"dimensionality evidence, so the one verdict this "
                f"assumption can fabricate rests on an unrecorded assumption; "
                f"remedy: read the out-of-plane boundary types off this "
                f"body's own archived case and record them; NO COMPUTE")
            continue
        if block.get("dim") != numerical.get("dim"):
            problems.append(
                f"{path.stem}: its dimensionality block says "
                f"{block.get('dim')!r} and its fit used "
                f"{numerical.get('dim')!r}")
            continue
        rungs = _study_rungs(study)
        if rungs < 3:
            notes.append(f"{path.stem}: stores {rungs} rungs, so the other "
                         f"dimensionality cannot be read from this record")
            continue
        levels = study["levels"]
        try:
            cells = [float(level["cells"]) for level in levels]
            values = [float(level["cd"]) for level in levels]
        except (KeyError, TypeError, ValueError):
            notes.append(f"{path.stem}: rungs are not readable as cells and "
                         f"values")
            continue
        dim = int(numerical.get("dim") or 3)
        other = 2 if dim == 3 else 3
        try:
            alt = uq.eca_hoekstra_band(cells, values, dim=other)
        except Exception as exc:  # noqa: BLE001
            notes.append(f"{path.stem}: refit at dim={other} raised "
                         f"{type(exc).__name__}")
            continue
        flips = (alt.get("guards") or {}).get("order_window") is True
        conclusive = bool(alt.get("conclusive"))
        line = (f"{path.stem}: p = {numerical.get('observed_order')} at "
                f"dim={dim}, {alt.get('observed_order')} at dim={other}; "
                f"order_window {'would pass' if flips else 'still fails'} "
                f"there, verdict "
                f"{'would become conclusive' if conclusive else 'does not move'}")
        if flips and conclusive:
            problems.append(line + "; the decline rests on the "
                            "dimensionality alone and the mesh has to settle "
                            "it; NO COMPUTE")
        else:
            notes.append(line)
    if problems:
        return Result("order-window declines state their dimensionality", FAIL,
                      f"{len(problems)} of {checked} order-window decline(s) "
                      f"cannot be believed as they stand", problems + notes)
    if not checked:
        return Result("order-window declines state their dimensionality", PASS,
                      "no stored ladder is declined on order_window")
    return Result("order-window declines state their dimensionality", INFO,
                  f"all {checked} order-window decline(s) name the "
                  f"dimensionality their fit used and hold at the other one",
                  notes)


def check_campaign_json_citations() -> Result:
    """Machine-readable citations in the campaign records must resolve.

    The markdown citation check covers backticked paths in prose. The JSON
    companions carry theirs as fields, and nothing looked at those.
    """
    interesting = {"report", "report_json", "artifact", "log", "evidence",
                   "ledger", "source_file", "primary_evidence"}
    missing, total = [], 0

    def walk(node, path, where):
        nonlocal total
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else key, where)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]", where)
        elif isinstance(node, str):
            leaf = path.rsplit(".", 1)[-1].split("[")[0]
            if leaf not in interesting or "/" not in node:
                return
            # An `evidence` field is sometimes a sentence that happens to
            # contain a slash. A citation is path-shaped: no whitespace, and
            # it ends in a file extension or a directory.
            if re.search(r"\s", node) or not re.search(
                    r"(\.[A-Za-z0-9]{1,6}|/)$", node):
                return
            candidate = node.lstrip("/")
            if node.startswith("/"):
                candidate = node
                resolved = Path(candidate)
            else:
                resolved = REPO / candidate
            total += 1
            if not resolved.exists():
                missing.append(f"{where}: {path} cites {node}")

    for source in sorted(CAMPAIGN.glob("*.json")):
        walk(_load_json(source), "", source.relative_to(REPO))
    if missing:
        return Result("campaign json citations", FAIL,
                      f"{len(missing)} of {total} machine-readable citations "
                      f"do not resolve", missing[:25])
    return Result("campaign json citations", PASS,
                  f"all {total} machine-readable campaign citations resolve")


# The three sets of files the laptop bundle copies VERBATIM out of this tree,
# each as (label, source directory, bundle directory, glob). Everything else in
# the bundle is derived at build time -- the recorded missions, the artifacts
# those recordings point at, and the credentials and lab-stats snapshot, which
# are deliberately computed with the whole repo present because copying their
# small inputs gets them wrong in the direction that CLAIMS MORE. Comparing a
# derived file against the tree would report drift on every build, so this
# check compares only what is supposed to be a copy.
_BUNDLE_VERBATIM = (
    ("control room", Path("sdk/chief_engineer"), Path("sdk/chief_engineer"),
     "**/*"),
    ("launcher", Path("scripts/laptop_bundle"), Path("."), "*"),
)
# The static pages, which move from demo-output/website into site/ and are the
# one set whose bundle path is not its repo path.
_BUNDLE_PAGES = (
    ("closure.html", Path("demo-output/website/closure.html"),
     Path("site/closure.html")),
    ("benchmarks.html", Path("demo-output/website/benchmarks.html"),
     Path("site/benchmarks.html")),
    ("wall.html", Path("demo-output/website/wall/wall.html"),
     Path("site/wall/wall.html")),
)
_BUNDLE_SKIP = ("__pycache__", ".pyc")


def _bundle_pairs() -> list[tuple[str, Path, Path]]:
    """(label, source, bundle) for every file the builder copies verbatim."""
    pairs: list[tuple[str, Path, Path]] = []
    for label, src_dir, dst_dir, pattern in _BUNDLE_VERBATIM:
        root = REPO / src_dir
        if not root.is_dir():
            continue
        for src in sorted(root.glob(pattern)):
            if not src.is_file():
                continue
            rel = src.relative_to(root)
            if any(part in str(rel) for part in _BUNDLE_SKIP):
                continue
            pairs.append((label, src, REPO / "dist" / "certonomous-demo"
                          / dst_dir / rel))
    for label, src, dst in _BUNDLE_PAGES:
        if (REPO / src).is_file():
            pairs.append((f"page {label}", REPO / src,
                          REPO / "dist" / "certonomous-demo" / dst))
    return pairs


def check_bundle_drift() -> Result:
    """The shipped bundle must not fall behind the tree it was built from.

    WHY THIS EXISTS. The laptop bundle is the artifact people actually run: it
    is the backup console for the shoot, and it is the only copy of this code
    that leaves the box. It went 32 commits behind without anything noticing.
    Twenty-one modules and the control room had drifted, one module was absent
    from the bundle entirely, and it shipped a certificate that captioned any
    envelope a 95 percent confidence interval long after that was fixed here.
    None of it was detected. The one bug that did surface was found by hand, by
    somebody on a different errand.

    This compares bytes, not dates. A module whose mtime moved but whose
    content did not is not drift, and a module edited in place on the same
    second is. Only the files the builder copies VERBATIM are compared; the
    recorded missions and the credentials snapshot are derived at build time
    and would report drift on every build if they were included.

    A file missing from the bundle FAILs on its own, per this check's gate: an
    absent module is worse than a stale one, because a stale module still
    answers and an absent one takes a page down with an import error.
    """
    bundle = REPO / "dist" / "certonomous-demo"
    if not bundle.is_dir():
        return Result("bundle drift vs tree", WARN,
                      "no bundle at dist/certonomous-demo to compare",
                      ["build it with scripts/build_laptop_bundle.py, or "
                       "record that the lab no longer ships one"])
    pairs = _bundle_pairs()
    if not pairs:
        return Result("bundle drift vs tree", WARN,
                      "found no files the builder copies verbatim; the "
                      "builder's copy list and this check have diverged")
    missing, differs = [], []
    for label, src, dst in pairs:
        rel = src.relative_to(REPO)
        if not dst.is_file():
            missing.append(f"{label}: {rel} is ABSENT from the bundle")
            continue
        if src.read_bytes() != dst.read_bytes():
            differs.append(f"{label}: {rel} differs from the shipped copy")
    stale = [p for _, _, p in pairs]
    extra = []
    for shipped in sorted((bundle / "sdk" / "chief_engineer").rglob("*")):
        if not shipped.is_file() or any(
                part in str(shipped) for part in _BUNDLE_SKIP):
            continue
        if shipped not in stale:
            extra.append(f"control room: {shipped.relative_to(bundle)} is "
                         f"shipped and is not in the tree")
    detail = missing + differs + extra
    if missing or differs:
        return Result("bundle drift vs tree", FAIL,
                      f"{len(missing)} file(s) missing from the bundle and "
                      f"{len(differs)} behind the tree, of {len(pairs)} "
                      f"copied verbatim", detail[:30])
    if extra:
        return Result("bundle drift vs tree", WARN,
                      f"all {len(pairs)} copied file(s) match, and "
                      f"{len(extra)} shipped file(s) no longer exist in the "
                      f"tree", extra[:15])
    return Result("bundle drift vs tree", PASS,
                  f"all {len(pairs)} file(s) the builder copies verbatim "
                  f"match the tree byte for byte")


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
    check_gate_table_vs_transcripts,
    check_wall_credentials_vs_results,
    check_benchmarks_vs_closure_record,
    check_fd_grades_current_standard,
    check_statistical_labels,
    check_nonconclusive_band_readers,
    check_channel_totals_use_one_rule,
    check_declared_fleet_vs_work,
    check_restated_thresholds,
    check_register_group_counts,
    check_campaign_json_citations,
    check_studies_carry_what_the_fit_records,
    check_declined_ladders_name_their_guard,
    check_order_window_declines_state_their_dimensionality,
    check_bundle_drift,
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
