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

WHAT EACH CHECK IS ACTUALLY TESTING, and why the distinction is not pedantry.
`check_wall_credentials_vs_results` re-derives every credential through
`lab.displayed_credential`, which is the same function `sdk/scripts/
build_wall.py` calls to write the card in the first place. A defect inside
that function is therefore identical on both sides of the comparison and reads
as agreement. That is not hypothetical: on 2026-08-01 the Ahmed 25 degree row
published its value on frontal area and its envelope on planform, understating
the band by the whole 3.586 area ratio, and this check reported PASS before the
fix and PASS after it. The check is worth having -- it measures drift between a
surface and the code that writes it, and the wall is rebuilt by hand -- but
drift is not correctness, and a check nobody can fail should be visible as one.

So every check now declares, in `BASIS` below, what it tests, what it catches
and what it is blind to, and `check_every_check_states_its_basis` enforces the
declaration: a GENERATOR check must name the function it shares with the
producer, and that function must actually appear in both files. The basis rides
on every report line and in the JSON, so a PASS says which kind of PASS it is.
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
        if row.get("ok"):
            # The published per_solver block counts SUCCEEDED rows only —
            # lab_stats.ledger_summary builds it from ok_rows — so the check
            # must too. Until 2026-08-01 this accumulator ran over every row
            # and the check failed on all 91 not-ok rows every time, on three
            # solvers, while each published figure was in fact exact.
            entry = per_solver.setdefault(solver, [0, 0.0])
            entry[0] += 1
            entry[1] += seconds
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
    # The entry of record is ROUND 5 since 2026-08-07 (commit 07a7fe9e). This
    # check was pinned to the round-3 file and so failed the wall for being
    # CORRECT: it reported "wall says 0.0566, the entry of record scores 0.0676".
    # Re-pinned by Ladder V Pass 2 (V6/V10, 2026-08-10). When a later round
    # lands, repoint this file and the counts below in the same commit --
    # a guard that cries wolf is worse than no guard, because the cheapest way
    # to silence it is to "fix" the surface that was right.
    entry = _load_json(WEB / "closure_challenge_round5_qcr.json")
    if "__error__" in entry:
        return Result("closure entry of record", WARN,
                      "round-5 entry file not readable; cannot verify the wall")

    published_score = closure.get("our_score")
    published_text = str(closure.get("our_entry") or "")

    # The entry of record's own overall score, from its own file.
    current = None
    for key in ("round5_overall", "overall", "round3_gated_overall", "gated_overall"):
        if isinstance(entry.get(key), (int, float)):
            current = float(entry[key])
            break
    if current is None:
        stack = [entry]
        while stack and current is None:
            node = stack.pop()
            if isinstance(node, dict):
                for key, value in node.items():
                    if key.endswith("overall") and isinstance(value, (int, float)) \
                            and "round2" not in key and "round4" not in key \
                            and "floor" not in key:
                        current = float(value)
                        break
                    if isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(node, list):
                stack.extend(node)

    problems = []
    if current is not None and published_score is not None:
        # The wall publishes the score at its own precision (4 dp since round 5,
        # where the record carries full float precision). Compare at the wall's
        # precision: quoting 0.0566 for 0.056647191704213645 is quoting it, and
        # an exact-equality test here would fail the wall for rounding.
        dp = len(str(published_score).split(".")[-1]) if "." in str(published_score) else 0
        if abs(round(current, dp) - float(published_score)) > 10 ** -(dp + 3):
            problems.append(
                f"our_score: wall says {published_score}, the entry of record "
                f"scores {current} (compared at the wall's {dp} dp)")
    if re.search(r"\ba single\b.{0,40}scoring call", published_text, re.I):
        problems.append(
            "our_entry claims a single scoring call; the record documents six "
            "official calls (floor, rounds 1-5) -- the unit being counted is "
            "DISTINCT PREDICTION SETS SCORED, and the benchmark imposes no "
            "scoring-call limit of any kind")
    if re.search(r"\b(three|five) of the eight\b", published_text, re.I):
        problems.append(
            "our_entry quotes a stale best-on-board count; round 5 records "
            "four of eight (the AR_14 tie was lost, priced in writing)")
    if re.search(r"best.{0,60}\bfour of the eight\b", published_text, re.I) \
            and "belongs to the baseline" not in published_text:
        problems.append(
            "our_entry states best-on-board 4 of 8 without the disclosure that "
            "two of those four rows are the organisers' own unmodified RANS "
            "field (SUBMISSION_DRAFT sec 4.7, the highest-priority disclosure)")
    # A rank claim on the wall must carry its companion: the probability that
    # the placement survives case resampling, AND the interval, AND the pairs
    # that are not decided. Ladder V rung V8 as amended 2026-08-10 -- "a bare
    # 68% is a worse claim than none, because 68% sounds settled and eight
    # cases do not support settled". This guard exists because rung V15 found
    # the four external surfaces (this text among them) edited by the very
    # commit that adopted the rule and left non-compliant with it: a rule that
    # binds surfaces needs a check that reads a surface.
    if re.search(r"\brank 1\b", published_text, re.I):
        missing = []
        if "P(rank 1)" not in published_text:
            missing.append("P(rank 1)")
        if not re.search(r"2\s*[-–]\s*100\s*%", published_text):
            missing.append("its 2-100% at 95% interval")
        if "not statistically decided" not in published_text:
            missing.append("the sweep token 'not statistically decided'")
        if missing:
            problems.append(
                "our_entry makes a rank claim without " + ", ".join(missing)
                + " (Ladder V rung V8 as amended 2026-08-10; source "
                "campaign/PROBABILITY_OF_RANK_2026-08-10.md)")
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

    TWO THINGS THE BAR DOES NOT TEST, measured 2026-08-01 against the ledger
    (`demo-output/website/mega-batch/COST_SCALING.md`) and now stated on the
    report itself, so nobody reads a streak as more than it is.

    1. **A streak measures the spread of the family, not the skill of the
       forecast.** On a family whose cost barely varies, predicting its own
       median clears the bar. `vspaero-wing` clears it 6,457 times in a row
       with a fitted law of R2 0.0002 that is 45 times worse than that median.
       A streak is necessary and it is not sufficient.
    2. **A family that mixes rank counts is not one cost population.** The
       third pair below is an 8-rank run sitting beside two serial ones, and a
       streak counted across the mixture counts two different quantities.
    """
    lines = []
    # THE DOCKET'S OWN PAIRS, read from disk. Until 2026-08-02 this check read
    # nothing at all: its whole evidence was the three tuples below, typed into
    # this file, so it could not fail on a wrong pair and it could not see that
    # completed items were recording their own measured cost in prose nothing
    # parsed. `scripts/cost_calibration.py` reads `measured_core_min` off every
    # completed proposal, each carrying a `measured_basis` that quotes the
    # sentence in that item's outcome the figure came from.
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        import cost_calibration  # noqa: PLC0415
        state = cost_calibration.analyse()
    except Exception as exc:  # noqa: BLE001 - a broken reader is a finding
        state = {"n": 0, "error": f"{type(exc).__name__}: {exc}"}
    if state.get("error"):
        lines.append(f"could not read the docket pairs: {state['error']}")
    elif state["n"]:
        whole = state["all"]
        lines.append(
            f"DOCKET PAIRS: {state['n']} completed item(s) record both an "
            f"estimate and a measured cost; {state['est_total']:g} core-min "
            f"estimated against {state['measured_total']:g} measured, "
            f"aggregate ratio {state['aggregate_ratio']}")
        lines.append(
            f"the 3x planning multiplier brackets {whole['inside_the_3x_band']}"
            f" of {whole['n']}; {whole['within_20_percent']} land within 20 "
            f"percent; {whole['needed_no_solver_at_all']} spent EXACTLY ZERO "
            f"because the work needed no solver, which no multiplier fixes")
        for label, key in (("basis begins 'measured'",
                            "basis_names_a_measurement"),
                           ("basis is a forecast", "basis_is_a_forecast")):
            cut = state.get(key)
            if cut:
                lines.append(
                    f"{label}: {cut['n']} pair(s), worst over-run "
                    f"{cut['worst_overrun']}x, median {cut['median_ratio']}, "
                    f"{cut['inside_the_3x_band']} inside the 3x band")
        lines.append(
            "over-runs on record: " + ", ".join(
                f"{r['ratio']}x {r['id']} ({r['basis_kind']})"
                for r in state["overruns"]) or "none")
        lines.append(
            f"{len(state['gaps'])} completed item(s) with an estimate record "
            f"no readable measured cost, each naming why "
            f"(scripts/cost_calibration.py)")

    # (family, rung, predicted seconds, measured seconds, evidence)
    # STILL TRANSCRIBED, and labelled. These three are per-solver-family
    # forecasts in seconds rather than per-item core-minutes, so they are not
    # on the docket in the shape above; they stay here until the F5a ladder
    # records them where something can read them.
    pairs = [
        ("pimpleFoam unsteady cylinder", "Re 2000", 3715.0, 3965.11,
         "F5a ladder, cost model D13"),
        ("pimpleFoam unsteady cylinder", "Re 3900", 6390.0, 10899.4,
         "F5a ladder, cost model outcome"),
        ("pimpleFoam unsteady cylinder", "Re 1000 3D pilot, 8 ranks",
         64800.0, 44102.0, "F5a ladder, 8-rank optimistic row 18 h"),
    ]
    families: dict[str, list] = {}
    lines.append("TRANSCRIBED, per-solver-family, still typed into this file:")
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
    lines.append(
        "the bar is necessary and not sufficient: on the ledger, vspaero-wing "
        "clears three-in-a-row 6457 times with a law of R2 0.0002 that is 45x "
        "worse than predicting its own median, and the 8-rank pair above sits "
        "in a family with two serial ones (demo-output/website/mega-batch/"
        "COST_SCALING.md)")
    docket_pairs = state.get("n", 0)
    return Result("cost predictions vs measured", INFO,
                  f"{docket_pairs} measured-versus-estimated pair(s) read off "
                  f"the docket, plus {len(pairs)} transcribed into this file "
                  f"across {len(families)} solver family", lines)


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


# Where the source-shape checks look. THE DEFECT THIS LIST GREW FOR: it held
# only the two package directories, so every runner under `sdk/scripts/` and
# every tool under `scripts/` -- including this file -- was outside the reach
# of checks written to find defects that live in exactly that kind of code.
# Measured when the list was widened, 2026-08-02:
# `sdk/scripts/run_uq_studies.py:b52_fourth_rung()` fits a refinement ladder,
# reads `band_abs` off it and never reads `conclusive`, on the one ladder in
# this corpus whose band IS the non-monotone fallback. That is the precise
# defect `check_nonconclusive_band_readers` exists for, in the file that
# WRITES the studies, and the check had never opened it.
_PY_ROOTS = ("sdk/workflows", "sdk/chief_engineer", "sdk/scripts", "scripts")


def _py_sources() -> list[Path]:
    out: list[Path] = []
    for root in _PY_ROOTS:
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


def check_stored_fits_reproduce_their_values() -> Result:
    """A stored study's numbers must equal what its own rungs still produce.

    THE GAP THIS CLOSES. `check_studies_carry_what_the_fit_records` compares
    KEY SETS: it asks whether a study carries every field the fit emits, and
    never asks whether the values under those keys are the values the fit
    emits. A writer that stored a stale band, a hand-typed verdict, or a number
    from a rung it later replaced passes that check with a full field set. The
    aortic-valve study is the standing example: its `conclusive: True` was a
    typed literal, not anything a guard produced, and no field-presence check
    can see the difference between a literal and a computed value.

    THE CHECK. Refit each study from the rungs it stores under `levels[]`,
    through the same fit whose method string it records, and compare value by
    value. Zero compute: `levels` already holds every cell count and functional
    the fit reads.

    WHAT IT CATCHES AND WHAT IT DOES NOT. It catches the record writer -- a
    stored number that the fit would not produce from the study's own rungs
    today. It shares `chief_engineer.uq` with the code that wrote those
    numbers, so it is blind to a defect inside the fit itself: a wrong band
    computed one way and stored, then recomputed the same wrong way, agrees.
    That limit is declared in BASIS and is the whole point of declaring it.
    """
    try:
        uq = _uq_module()
    except Exception as exc:  # noqa: BLE001
        return Result("stored fits reproduce their values", WARN,
                      f"cannot import the fit: {type(exc).__name__}: {exc}")
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
    problems, notes, checked, compared = [], [], 0, 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            problems.append(f"{path.name}: does not parse")
            continue
        numerical = study.get("numerical") or {}
        if not numerical:
            continue
        rungs = _study_rungs(study)
        own = _own_fit(uq, study)
        if own is None:
            # Named, not skipped in silence: a record whose stored numbers no
            # current fit reproduces is the record this check most wants to
            # read, and it is exactly the one it cannot.
            notes.append(
                f"{path.stem}: stores {rungs} rung(s) and NO CURRENT FIT "
                f"reproduces its stored method string "
                f"{str(numerical.get('method') or '')[:60]!r}, so none of its "
                f"values can be checked against its own evidence; remedy: "
                f"establish which producer wrote this block, and whether that "
                f"producer still exists, before any number here is believed "
                f"or rewritten; NO COMPUTE to find out"
                + ("" if rungs >= 3 else ", and it stores no usable rungs"))
            continue
        checked += 1
        drops = set(uq.STUDY_NUMERICAL_DROPS)
        for key in sorted(set(own) & set(numerical)):
            if key in drops:
                continue
            stored, fresh = numerical[key], own[key]
            compared += 1
            if isinstance(stored, (int, float)) and isinstance(
                    fresh, (int, float)) and not isinstance(stored, bool) \
                    and not isinstance(fresh, bool):
                scale = max(1.0, abs(float(fresh)))
                if abs(float(stored) - float(fresh)) <= 1e-9 * scale:
                    continue
            elif stored == fresh:
                continue
            problems.append(
                f"{path.stem}: numerical[{key}] is stored as {stored!r}; "
                f"refitting this study's own {rungs} rungs through "
                f"{own.get('method', '')[:40]!r} produces {fresh!r}. "
                + REMEDY_REFIT.format(n=rungs))
    if problems:
        return Result("stored fits reproduce their values", FAIL,
                      f"{len(problems)} stored value(s) are not what this "
                      f"study's own rungs produce", problems + notes)
    if notes:
        return Result("stored fits reproduce their values", WARN,
                      f"all {compared} value(s) across {checked} refittable "
                      f"study(s) reproduce; {len(notes)} study(s) cannot be "
                      f"refitted at all and are unchecked", notes)
    return Result("stored fits reproduce their values", PASS,
                  f"all {compared} stored value(s) across {checked} study(s) "
                  f"reproduce from the study's own rungs")


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


# The two remedies this lab has already accepted for a whitelisting writer,
# both in-tree, so the check can name a precedent rather than a preference.
#   copy wholesale:  uq.study_numerical  -- {k: v for k, v in band.items()
#                    if k not in STUDY_NUMERICAL_DROPS}, plus dropped_from_fit
#   name the drops:  lab.credential_card -- CREDENTIAL_NOT_ON_CARD, each key
#                    with the reason it is not on the card
_DROP_DECLARATIONS = ("DROPS", "NOT_ON", "dropped_from", "dropped_keys",
                      "excluded_keys")


def _whitelist_source(node) -> str | None:
    """`src.get("k")` or `src["k"]` -> "src". Anything else -> None."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "get" \
            and isinstance(node.func.value, ast.Name) and node.args \
            and isinstance(node.args[0], ast.Constant) \
            and isinstance(node.args[0].value, str):
        return node.func.value.id
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
            and isinstance(node.slice, ast.Constant) \
            and isinstance(node.slice.value, str):
        return node.value.id
    return None


def check_record_writers_name_their_drops() -> Result:
    """A writer that whitelists keys drops what it was not told to keep.

    THE DEFECT. `eca_hoekstra_band` began recording the dimensionality its
    band was fitted with, and not one stored study picked the field up -- not
    because the studies predate it, but because both study writers built the
    `numerical` block from a hand-typed list of keys. A hand-typed list keeps
    working when the producer learns to record something new, and drops the
    new field on every record it writes, in silence. A record that omits what
    it was not told to keep looks complete, which is worse than one that never
    had the field: nothing on the file says a field is missing rather than
    absent. Both study writers are fixed; the shape is not confined to them.

    THE CHECK, and what it is honestly measuring. It finds the SHAPE: a dict
    literal four or more of whose values are `src.get("k")` or `src["k"]` from
    one source. That shape is the precondition for the defect, not the defect
    -- a writer whose source has exactly the keys it copies is fine, and this
    cannot tell the difference statically. So it separates the one case where
    the author demonstrably cannot know the key set, which is a source that
    arrives as a PARAMETER, from the case where the source was built a few
    lines up, and it reports rather than failing.

    THE BAR, from the charter clause this encodes: a record writer either
    copies what it is given or names the keys it drops. Both remedies have a
    precedent in this tree, and either clears the finding: iterate the
    source's `.items()`, or declare the exclusions in a named constant. A
    writer doing neither is one upstream field away from the study defect.
    """
    findings, local, cleared = [], [], []
    for source in _py_sources():
        text = source.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            body = ast.get_source_segment(text, function) or ""
            parameters = {a.arg for a in function.args.posonlyargs
                          + function.args.args + function.args.kwonlyargs}
            for node in ast.walk(function):
                if not isinstance(node, ast.Dict):
                    continue
                counts: dict[str, int] = {}
                for value in node.values:
                    name = _whitelist_source(value)
                    if name:
                        counts[name] = counts.get(name, 0) + 1
                if not counts:
                    continue
                var, copied = max(counts.items(), key=lambda kv: kv[1])
                if copied < 4:
                    continue
                where = (f"{source.relative_to(REPO)}:{node.lineno} "
                         f"{function.name}() builds a record from {var!r} "
                         f"with {copied} hand-typed keys")
                if f"{var}.items()" in body:
                    cleared.append(f"{where}; also copies {var}.items()")
                elif any(word in body for word in _DROP_DECLARATIONS):
                    cleared.append(f"{where}; names its drops")
                elif var in parameters:
                    findings.append(
                        where + f", and {var!r} is a PARAMETER, so this "
                        f"function cannot see what its caller put in it. "
                        f"Remedy, either one: copy {var}.items() minus a named "
                        f"drop set, as uq.study_numerical does, or declare the "
                        f"exclusions in a constant, as lab.CREDENTIAL_NOT_ON_"
                        f"CARD does; NO COMPUTE")
                else:
                    local.append(where + f", and {var!r} is built in the same "
                                 f"function, so the author can see its keys")
    detail = findings + [
        f"{len(local)} more site(s) have the same shape on a locally built "
        f"source, which is the weaker case and is listed for the census:"] + \
        local[:10] + [
        f"{len(cleared)} site(s) already copy wholesale or name their drops"]
    if findings:
        return Result("record writers name their drops", WARN,
                      f"{len(findings)} writer(s) whitelist keys off a source "
                      f"they receive as a parameter and declare no drops",
                      detail)
    return Result("record writers name their drops", PASS,
                  f"no writer whitelists keys off a parameter without saying "
                  f"what it leaves out; {len(cleared)} declare their handling",
                  detail)


# A rung's stored precision matters only through one number: how much the
# extrapolation multiplies the finest increment. Below this the rounding is
# irrelevant however coarse; above it, the digits the record kept decide the
# answer. Not a tuned constant -- it is the point at which a half-unit in the
# last stored decimal starts to reach the band, and the check computes that
# reach per study rather than assuming it.
_ROUNDING_SHARE_OF_BAND = 0.10


def check_stored_rungs_carry_solved_precision() -> Result:
    """A refit reads what was solved, not what a table printed.

    THE DEFECT, measured. The supersonic wedge ladder was extrapolated twice
    from the same three rungs. Fitted on the values as the act's ladder table
    PRINTS them, at three decimals -- 47.588 / 46.123 / 44.693 -- the
    extrapolated shock angle is -13.733 degrees. Fitted on what the act
    solved -- 47.58767882153372 / 46.12330850878531 / 44.692792746510406 --
    it is -15.753. Two point zero two degrees apart, and the whole difference
    is rounding. Both readings are on the record and neither is withdrawn
    (demo-output/website/campaign/W3_2D_LADDER_REFIT.md section 4a).

    THE MECHANISM, which is why this is a rule and not a caution. At an
    observed order near zero the Richardson extrapolation amplifies the finest
    increment by a large factor -- 42.25 on that ladder. Whatever error the
    stored rungs carry is multiplied by the same factor. So the worse a ladder
    behaves, the more its refit depends on precision nobody thinks about, and
    a document is the one source that has already thrown that precision away.
    The cone, diamond and vortex-shedding orders moved in the third decimal
    the same way and changed no verdict; the wedge moved two degrees.

    THE CHECK, zero compute, from each study's own stored rungs. Compute the
    amplification the study's own extrapolation applies, and the reach of half
    a unit in the last decimal its rungs are stored to. Report where that
    reach exceeds a tenth of the study's own band, because that is the point
    at which the record's precision, rather than its measurements, is deciding
    the number. A study whose rungs are stored at full solved precision passes
    at any amplification, which is the behaviour to keep.
    """
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
    problems, notes, checked = [], [], 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            continue
        numerical = study.get("numerical") or {}
        phi0 = numerical.get("richardson_extrapolated")
        band = numerical.get("band_abs")
        levels = study.get("levels")
        if phi0 is None or not band or not isinstance(levels, list) \
                or len(levels) < 3:
            continue
        try:
            rows = sorted((l for l in levels if "cells" in l and "cd" in l),
                          key=lambda l: float(l["cells"]))[-3:]
            values = [float(r["cd"]) for r in rows]
        except (TypeError, ValueError):
            continue
        if len(values) < 3:
            continue
        checked += 1
        increment = abs(values[-1] - values[-2])
        if not increment:
            notes.append(f"{path.stem}: the finest two rungs are equal, so no "
                         f"amplification is defined")
            continue
        amplification = abs(float(phi0) - values[-1]) / increment
        # Decimals the record actually kept, per rung, from the stored text.
        decimals = min(len(repr(v).split(".")[-1]) for v in values)
        reach = amplification * 0.5 * (10.0 ** -decimals)
        share = reach / abs(float(band))
        line = (f"{path.stem}: extrapolation amplifies the finest increment "
                f"by {amplification:.2f}x; rungs stored to {decimals} "
                f"decimals, so half a unit in the last one reaches "
                f"{reach:.3g}, which is {share * 100:.4f} percent of the "
                f"study's own band of {float(band):.4g}")
        if share > _ROUNDING_SHARE_OF_BAND:
            problems.append(
                line + ". The precision this record kept, not its "
                "measurements, is deciding the extrapolated value; remedy: "
                "restore the rungs from the solve that produced them -- the "
                "forces file, not any table -- and refit; NO COMPUTE")
        else:
            notes.append(line)
    if problems:
        return Result("stored rungs carry solved precision", FAIL,
                      f"{len(problems)} of {checked} extrapolating ladder(s) "
                      f"are decided by their stored precision", problems + notes)
    return Result("stored rungs carry solved precision", PASS,
                  f"all {checked} extrapolating ladder(s) store rungs precise "
                  f"enough that rounding reaches under "
                  f"{_ROUNDING_SHARE_OF_BAND * 100:g} percent of their own "
                  f"band", notes)


def check_ladder_rungs_share_one_recipe() -> Result:
    """VERIFICATION_CHARTER section 3.2 rule 3, which had no checker.

    THE RULE. "A recipe audit precedes an order... read the refinement level
    from each rung's own dictionary and refuse a triple that does not share
    one." An order fitted across a change of mesh recipe is fitted across a
    change of EXPERIMENT and is not a discretization order at all. The second
    NACA 4412 ladder reported p = 10.467 that way. Section 3.1's rule about
    dimensionality has a checker and section 3.2's does not, so an order
    fitted across two recipes reaches a report with nothing objecting.

    WHY THE ORDER WINDOW DOES NOT COVER IT. The 4412's 10.467 is refused by
    `order_window`, so the verdict is right. The reason is wrong, and a right
    verdict resting on the wrong reason moves the moment the arithmetic does:
    an order of 2.3 fitted across the same recipe change would pass the window
    and be just as meaningless.

    THE CHECK, zero compute, from the rungs and the audit block already stored.
    A study's `recipe_audit.valid_family_cells` names the rungs that DO share
    one recipe. `eca_hoekstra_band` fits the finest three distinct cell counts
    it is handed. So the fit triple must be a subset of the valid family, and
    a study that carries no recipe audit at all cannot be known either way.

    TWO SEVERITIES, and the difference is whether the lab knows. A study whose
    own `recipe_audit` records the finding is a known, recorded matter that is
    reported and not escalated -- several defer explicitly to the open ruling
    on what a record should say when a body has no usable ladder. A study that
    fits across recipes with nothing on its record saying so, or that publishes
    an order with no recipe audit at all, is the case this check exists for.
    """
    studies = sorted((REPO / "models" / "curriculum" / "uq-studies")
                     .glob("*.json"))
    problems, known, skipped, checked = [], [], [], 0
    for path in studies:
        study = _load_json(path)
        if not isinstance(study, dict):
            continue
        numerical = study.get("numerical") or {}
        if "observed_order" not in numerical:
            skipped.append(
                f"{path.stem}: SKIPPED, not in scope -- its numerical block "
                f"records no `observed_order`, so no refinement fit produced "
                f"it and there is no order here to be fitted across anything")
            continue
        checked += 1
        audit = study.get("recipe_audit")
        cells = []
        for level in study.get("levels") or []:
            try:
                value = int(level["cells"])
            except (KeyError, TypeError, ValueError):
                continue
            if value not in cells:
                cells.append(value)
        triple = sorted(cells)[-3:]
        if not isinstance(audit, dict) or not audit.get("finding"):
            order = numerical.get("observed_order")
            what = (f"publishes an observed order of {order!r}" if order
                    is not None else
                    "compares its rungs through a refinement fit that "
                    "declined to fit an order, and its fallback band is "
                    "still a comparison of those rungs")
            problems.append(
                f"{path.stem}: {what} and carries NO recipe "
                f"audit, so nothing on this record says whether its rungs "
                f"share one refinement recipe; remedy: read the refinement "
                f"level off each rung's own system/snappyHexMeshDict, as "
                f"b52.json and four others already do; NO COMPUTE")
            continue
        family = audit.get("valid_family_cells")
        if not isinstance(family, list) or not family:
            problems.append(
                f"{path.stem}: has a recipe audit with no "
                f"`valid_family_cells`, so the finding cannot be checked "
                f"against the rungs the fit used; NO COMPUTE to add it")
            continue
        outside = [c for c in triple if c not in set(int(f) for f in family)]
        if not outside:
            continue
        line = (f"{path.stem}: the fit triple {triple} includes "
                f"{outside}, which this study's OWN recipe audit excludes "
                f"from the family that shares one recipe ({sorted(family)}); "
                f"its observed order of {numerical.get('observed_order')!r} is "
                f"fitted across a change of experiment")
        # A record that states the finding itself is a known matter, not a
        # silent one, and several defer explicitly to an open ruling.
        acknowledged = any(
            str(audit.get(key) or "").strip()
            for key in ("numerical_block_untouched", "what_this_body_needs"))
        (known if acknowledged else problems).append(
            line + (". The record states this and names what the body needs, "
                    "so it is reported, not escalated"
                    if acknowledged else
                    ". Nothing on the record says so; NO COMPUTE to say it"))
    scope = (f"{checked} of {checked + len(skipped)} stored study(s) in "
             f"scope, {len(skipped)} named as skipped")
    if problems:
        return Result("ladder rungs share one recipe", FAIL,
                      f"{len(problems)} fitted ladder(s) publish an order "
                      f"with no recipe audit, or across recipes their record "
                      f"does not mention; {len(known)} more do so and say so; "
                      f"{scope}", problems + known + skipped)
    if known:
        return Result("ladder rungs share one recipe", WARN,
                      f"{len(known)} fitted ladder(s) fit across a recipe "
                      f"change that their own record names; {scope}",
                      known + skipped)
    return Result("ladder rungs share one recipe", PASS,
                  f"all {checked} fitted ladder(s) fit inside a family their "
                  f"own recipe audit calls comparable; {scope}", skipped)


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
        # FAIL, not WARN (2026-08-10). An absent bundle does not mean "nothing
        # to report" -- it means THIS DETECTOR IS OFF, for the one artifact
        # that leaves this box. The bundle shipped ten days stale while this
        # check named the stale pages by name; the failure mode a missing
        # bundle adds on top is silence read as success, which is the class
        # closed everywhere else in this tree the same day (L-45).
        return Result("bundle drift vs tree", FAIL,
                      "NO BUNDLE at dist/certonomous-demo: the drift detector "
                      "for the shipped artifact is OFF, not merely uninformative",
                      ["nothing is being checked against the tree while this "
                       "directory is absent -- a stale zip beside it would "
                       "report clean",
                       "build it with scripts/build_laptop_bundle.py --zip, or "
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


_RUNG_SHAPED = re.compile(
    r"\brung\b|\bladder\b|refinement|grid[\s-]convergence|finest grid", re.I)
_ITERATION_TERM = re.compile(
    r"\biterat|\bsteps?\b|\bsweeps?\b|endTime|time step", re.I)


def check_rung_estimates_state_their_iterations() -> Result:
    """A refinement rung priced by its cells alone is priced by half.

    THE DEFECT. The flat plate's finest rung came in at 1.48x its estimate and
    the entire overrun was settling: it was asked for 15,000 iterations, read
    1.05 percent above its settled value with the coefficient still falling,
    and took 36,000. Its cells were estimated correctly. Nothing in the
    estimate asked how long that grid takes to settle.

    WHY THE OMISSION IS THE EXPENSIVE HALF, measured rather than asserted. On
    this lab's own ledger (`demo-output/website/mega-batch/COST_SCALING.md`),
    wall time carries an exponent of essentially one on iterations in both
    families that record them, 1.156 on time steps and 1.026 on SIMPLE
    iterations, while the within-family cell exponents are small because cells
    barely vary inside a family. The term that overruns is the term nobody
    writes down.

    THE CHECK. Every compute proposal on the docket whose objective or
    rationale is rung-shaped must have a `cost_basis` that names an iteration,
    step or sweep count. This never blocks a proposal: it counts them, so the
    gap is a number on a report rather than a surprise on a run.
    """
    docket = _load_json(REPO / "demo-output" / "website" / "agenda"
                        / "docket.json")
    proposals = (docket.get("proposals") if isinstance(docket, dict)
                 else docket) or []
    if not isinstance(proposals, list):
        return Result("rung estimates state their iterations", WARN,
                      "the docket did not parse as a list of proposals")
    rung, silent = [], []
    for proposal in proposals:
        if not isinstance(proposal, dict) or not proposal.get("est_core_min"):
            continue
        text = f"{proposal.get('objective', '')} {proposal.get('rationale', '')}"
        if not _RUNG_SHAPED.search(text):
            continue
        rung.append(proposal)
        if not _ITERATION_TERM.search(str(proposal.get("cost_basis") or "")):
            silent.append(proposal)
    if not rung:
        return Result("rung estimates state their iterations", PASS,
                      "no rung-shaped compute proposal is on the docket")
    live = [p for p in silent if p.get("status") in ("proposed", "approved")]
    detail = [f"{p.get('id')}: {p.get('status')}, {p.get('est_core_min')} "
              f"core-min, basis prices the grid only"
              for p in sorted(live, key=lambda p: -float(
                  p.get("est_core_min") or 0))[:12]]
    detail.append(
        f"{len(silent)} of {len(rung)} rung-shaped compute proposal(s) name no "
        f"iteration count; {len(live)} of those are still proposed or approved")
    if live:
        return Result("rung estimates state their iterations", WARN,
                      f"{len(live)} unstarted rung estimate(s) price the grid "
                      f"and not the settling", detail)
    return Result("rung estimates state their iterations", PASS,
                  f"every unstarted rung estimate names an iteration count; "
                  f"{len(rung)} rung-shaped proposal(s) read", detail)


# --------------------------------------------------------------------------
# What each check is actually testing
# --------------------------------------------------------------------------
#
# THE DEFECT THIS EXISTS FOR. A check that re-derives a published number
# through the same function that published it cannot fail on a defect inside
# that function: the error is identical on both sides and reads as agreement.
# `check_wall_credentials_vs_results` is built that way, and it reported PASS
# on both sides of a real defect (the Ahmed 25 degree row's value on frontal
# area and its envelope on planform, a factor of 3.586 apart, 2026-08-01).
# Such a check is still worth running -- it measures whether a hand-rebuilt
# surface has fallen behind its generator -- but it answers a different
# question from the one its PASS line appears to answer, and the reader has no
# way to tell which without reading the source.
#
# So every check declares which of the five it is, what it catches, and what
# it is blind to. The declaration is not a comment: for a GENERATOR check it
# names the symbol shared with the producer and the producer's file, and
# `check_every_check_states_its_basis` verifies that the symbol really does
# appear in both. A coupling that is removed, or one that is added and not
# declared, is then a finding rather than a comment nobody reread.

EVIDENCE = "EVIDENCE"
GENERATOR = "GENERATOR"
PROPERTY = "PROPERTY"
SURFACE = "SURFACE"
TRANSCRIBED = "TRANSCRIBED"
META = "META"

BASIS_MEANING = {
    EVIDENCE: ("re-derives a published number from a primary artifact, by "
               "arithmetic this file performs itself; a defect in the "
               "producing code shows up as a disagreement"),
    GENERATOR: ("compares a published surface against the code that wrote it; "
                "catches drift between the two and is BLIND to any defect "
                "inside the shared code, which both sides carry equally"),
    PROPERTY: ("asserts a property of a record, a surface or a source file; "
               "nothing is re-derived, so there is no shared derivation to "
               "hide in, and equally no number is confirmed"),
    SURFACE: ("compares two published surfaces, or two copies of one file, to "
              "each other; neither is primary evidence for the other"),
    TRANSCRIBED: ("the evidence is typed into this file as a constant; the "
                  "check cannot fail on a wrong value, only on arithmetic "
                  "over its own constants"),
    META: "a check on this file rather than on the lab's records",
}

# name -> (basis, catches, blind_to, shared)
# `shared` is (symbol, file that also uses it) for a GENERATOR check, else None.
BASIS: dict[str, tuple[str, str, str, tuple[str, str] | None]] = {
    "check_ledger_integrity": (
        PROPERTY, "an interrupted write that left a line unparseable",
        "a row that parses and is wrong; nothing here reads the values", None),
    "check_wall_counters_vs_ledger": (
        EVIDENCE,
        "a published counter that no longer sums out of the ledger; the sums "
        "are accumulated in this function, row by row, not obtained from "
        "lab_stats.ledger_summary which built the published block",
        "the DEFINITION of what counts, which was copied here from the "
        "generator by hand (succeeded rows only). If that convention is the "
        "wrong one, both sides are wrong together and this agrees", None),
    "check_ledger_stalls": (
        EVIDENCE,
        "rows whose wall time no per-solver cost mechanism explains, read "
        "straight off the ledger and reported with their timestamps",
        "whether STALL_SECONDS is the right cut; the threshold is declared "
        "here and is not derived from anything", None),
    "check_closure_entry_of_record": (
        EVIDENCE,
        "a wall score that disagrees with the entry file of record, which "
        "this check opens and searches itself",
        "whether the file it opens is the entry of record; that name is "
        "hard-coded here", None),
    "check_memory_scaling_law": (
        EVIDENCE,
        "a published power law that does not refit from its own tabulated "
        "measurements; the ordinary least squares is done in this function",
        "the measurements themselves, which are read from the SAME document "
        "that states the law. A mistyped MiB figure refits to the mistyped "
        "law and passes. Nothing here reaches the solver logs those three "
        "numbers came from", None),
    "check_withdrawn_numbers": (
        PROPERTY, "a withdrawn value still present verbatim on a promotional "
                  "surface",
        "the same value written any other way: 0.251 for 0.2510, or a "
        "recomputed near-neighbour", None),
    "check_evidence_paths_exist": (
        PROPERTY, "a repo-rooted citation with no file behind it",
        "a path that exists and holds something other than the evidence "
        "claimed for it", None),
    "check_f2_reproduction": (
        EVIDENCE,
        "a published coefficient that does not match the raw force file, "
        "which this check parses itself; this is the shape the others are "
        "measured against",
        "whether that raw file is the run the record names", None),
    "check_cost_predictions": (
        EVIDENCE,
        "the measured-versus-estimated pairs recorded on the docket, read "
        "from `measured_core_min` on every completed item, each carrying a "
        "`measured_basis` that quotes the sentence in that item's own outcome "
        "the figure came from. Until 2026-08-02 this check read nothing at "
        "all: its whole evidence was three tuples typed into this file",
        "the three per-solver-family pairs that are STILL transcribed here, "
        "and the correctness of a `measured_core_min` field itself, which is "
        "read from an outcome by hand and quoted rather than re-derived from "
        "a solver log", None),
    "check_ungated_completed_runs": (
        PROPERTY,
        "a completed run whose record still carries the not-yet-graded marker",
        "an ungated run whose record does not carry that marker; the check "
        "knows one string on one file", None),
    "check_gate_table_vs_transcripts": (
        GENERATOR,
        "a published row the generator would no longer write: hand-edited, "
        "or resting on a transcript that has stopped supporting it",
        "a misparse inside gate_table.py. The published table is that "
        "generator's own output pasted into markdown, so a transcript read "
        "wrongly is read wrongly on both sides and agrees",
        ("gate_table", "scripts/gate_table.py")),
    "check_wall_credentials_vs_results": (
        GENERATOR,
        "wall.json having fallen behind the builder: a card that would change "
        "if the wall were rebuilt right now. One arm IS independent -- "
        "relative_error is recomputed here from the result file's own "
        "cd_compared and reference_cd",
        "any defect inside displayed_credential, which is the function that "
        "wrote the card. This is the check the finding was filed on: it "
        "reported PASS on both sides of the Ahmed 25 degree area-basis "
        "defect, before the fix and after it",
        ("displayed_credential", "sdk/scripts/build_wall.py")),
    "check_benchmarks_vs_closure_record": (
        EVIDENCE,
        "two things: the published block regressing on the next build (that "
        "half is GENERATOR, against the generator's own _CLOSURE constant), "
        "and our_score disagreeing with the round-3 entry's own harness "
        "result, which this check reads from the scored artifact",
        "a closure field that is not our_score and is wrong in the artifact "
        "and in the constant alike", None),
    "check_fd_grades_current_standard": (
        PROPERTY,
        "a published FD row whose grade word is not the one the current "
        "standard gives for the percentage printed beside it",
        "the percentage itself, which is read off the published row and never "
        "recomputed from FD data. A wrong percentage carrying its own correct "
        "grade passes. And `_fd_grade` restates verification charter section "
        "7 as literals in this file, which is the very shape "
        "check_restated_thresholds calls a defect elsewhere", None),
    "check_statistical_labels": (
        PROPERTY,
        "a caption-printing site with no interval test in it, and a "
        "transcript line claiming an interval with no interval on it",
        "an interval that is present, well-formed and fabricated", None),
    "check_nonconclusive_band_readers": (
        PROPERTY,
        "a function that fits a ladder, reads band_abs and never reads the "
        "conclusiveness flag, by parsing the source",
        "a caller that mentions the flag and ignores it; the test is textual "
        "presence, not use", None),
    "check_channel_totals_use_one_rule": (
        SURFACE,
        "a combined band containing a channel the same act's own table "
        "reports unquantified",
        "whether either the total or the table is right; it only makes them "
        "agree with each other. Already self-declared in its docstring", None),
    "check_declared_fleet_vs_work": (
        PROPERTY,
        "a non-zero worker declaration inside a branch whose condition is a "
        "cache restore",
        "a fleet overstated on a cold path, where the declaration is inside "
        "no branch this check recognises", None),
    "check_restated_thresholds": (
        PROPERTY,
        "a governed threshold restated as a literal default, whether or not "
        "it currently agrees with its source",
        "a threshold this file does not know is governed. _PY_ROOTS now "
        "covers scripts/ and sdk/scripts/ as well, so this file IS scanned, "
        "but GOVERNED_THRESHOLDS names only two constants by parameter name. "
        "_fd_grade restates verification charter section 7 as the literals "
        "15.0 and 5.0 in positional code rather than as a defaulted parameter, "
        "and STALL_SECONDS is declared here with no governed source at all; "
        "neither is reachable by a check keyed on parameter defaults", None),
    "check_register_group_counts": (
        SURFACE,
        "a register group whose declared count disagrees with the headings "
        "under it, in the same file",
        "an entry that is missing from the register altogether; both numbers "
        "come from the register", None),
    "check_campaign_json_citations": (
        PROPERTY, "a machine-readable citation with no file behind it",
        "a citation pointing at a file that exists and is not the evidence",
        None),
    "check_studies_carry_what_the_fit_records": (
        EVIDENCE,
        "a record writer that whitelists keys and has dropped a field the fit "
        "learned to emit; the writer and the fit are different code paths, so "
        "the comparison is real",
        "every VALUE. It compares key sets only. A stale or hand-typed number "
        "under a present key passes -- which is what "
        "check_stored_fits_reproduce_their_values now reads",
        None),
    "check_stored_fits_reproduce_their_values": (
        EVIDENCE,
        "a stored value the study's own rungs no longer produce: a stale "
        "band, a hand-typed verdict, a number from a rung later replaced. The "
        "record writer and the fit are different code paths",
        "a defect inside the fit itself. The same uq module computed the "
        "stored numbers and recomputes them here, so a band computed wrongly "
        "and recomputed the same way agrees. It is also blind to any study "
        "whose method string no current fit reproduces, and those are named "
        "on the report rather than skipped",
        ("eca_hoekstra_band", "sdk/chief_engineer/uq.py")),
    "check_declined_ladders_name_their_guard": (
        SURFACE,
        "a record whose named guard disagrees with its own guard map, and a "
        "decline that records no guard at all",
        "whether the guard map is right. Both fields were written by the same "
        "writer from the same fit, so this asks only that the record agrees "
        "with itself; it never refits to confirm the map", None),
    "check_record_writers_name_their_drops": (
        PROPERTY,
        "the code shape that makes the defect possible: a dict built from one "
        "source by four or more hand-typed keys, where the source arrives as "
        "a parameter so the author cannot see its key set",
        "whether any such writer is actually dropping a field today. The "
        "shape is the precondition, not the defect: a whitelist whose source "
        "has exactly the keys it copies is correct, and nothing static "
        "distinguishes the two. It is also blind to a writer that reads its "
        "source through anything other than .get(literal) or [literal]",
        None),
    "check_stored_rungs_carry_solved_precision": (
        EVIDENCE,
        "a stored ladder whose extrapolated value is decided by the number of "
        "decimals the record kept rather than by what was solved, computed "
        "from the study's own rungs, its own extrapolation and its own band",
        "a rung stored at full precision that is nonetheless the WRONG value, "
        "and any refit that happens outside a stored study -- the wedge case "
        "this encodes lives in a campaign document, not in this corpus, so "
        "the check would not have caught the defect that motivated it. It "
        "guards the corpus going forward and says so", None),
    "check_ladder_rungs_share_one_recipe": (
        EVIDENCE,
        "an observed order fitted across a change of mesh recipe, by reading "
        "the fit triple off the study's own rungs and the comparable family "
        "off its own recipe audit. These are two independent records: the "
        "rungs come from the solves, the family from each rung's meshing "
        "dictionary, and neither is derived from the other",
        "a study with no recipe audit, which it reports as a fault rather "
        "than passing; and the correctness of a recipe audit itself, which is "
        "read off snappyHexMeshDict by hand and not re-derived here", None),
    "check_order_window_declines_state_their_dimensionality": (
        EVIDENCE,
        "a decline that rests on the dimensionality assumption alone, by "
        "refitting the ladder from its own stored rungs at the other dim",
        "a defect inside eca_hoekstra_band, shared with the code that wrote "
        "the stored order. It also prints the STORED order beside a REFIT "
        "one, so the two columns do not come from the same place",
        ("eca_hoekstra_band", "sdk/chief_engineer/uq.py")),
    "check_bundle_drift": (
        SURFACE,
        "a shipped file that is absent from the bundle or behind the tree, by "
        "byte comparison",
        "whether the tree is right; a defect copied faithfully into the "
        "bundle is a match. Already self-declared in the module docstring",
        None),
    "check_rung_estimates_state_their_iterations": (
        PROPERTY,
        "a rung-shaped compute proposal whose cost_basis names no iteration, "
        "step or sweep count",
        "whether a stated iteration count is the right one, and whether the "
        "estimate built on it is any good", None),
    "check_every_finding_prices_its_remedy": (
        META, "a check that ships without a stated remedy and price",
        "whether a stated price is correct", None),
    "check_every_check_states_its_basis": (
        META,
        "a check that ships without declaring what it tests, and a GENERATOR "
        "declaration naming a coupling that is no longer there",
        "a check that declares EVIDENCE and is in fact coupled through a "
        "symbol it does not name; the declaration is enforced where it is "
        "made, not discovered from scratch", None),
}


def check_every_check_states_its_basis() -> Result:
    """Every check declares what it tests, and a declared coupling is real.

    THE DEFECT. `check_wall_credentials_vs_results` re-derives each credential
    through `lab.displayed_credential`, the same function `build_wall.py` calls
    to write the card. Its PASS means the wall has not drifted from its
    builder. It does not mean the card is right, and it read PASS on both
    sides of the Ahmed 25 degree area-basis defect. Nothing on the report said
    which kind of PASS it was.

    THE CHECK, three parts. Every check in CHECKS carries a BASIS entry and
    every BASIS entry names a live check. Every GENERATOR entry names the
    symbol it shares with the producer, and that symbol must actually appear
    both in this file and in the producer's file -- so a coupling that is
    removed, or a declaration that was never true, is a finding rather than a
    stale comment. And the tally of how many checks are blind to a defect in
    the code they check rides on the verdict line, because that number is the
    honest summary of what this audit can and cannot see.
    """
    names = {check.__name__ for check in CHECKS}
    missing = sorted(n for n in names if n not in BASIS)
    stale = sorted(n for n in BASIS if n not in names)
    problems = [f"{n}: does not declare what it tests" for n in missing]
    problems += [f"{n}: declares a basis and is not a check any more"
                 for n in stale]

    own_text = Path(__file__).read_text(encoding="utf-8", errors="replace")
    for name in sorted(set(BASIS) & names):
        basis, catches, blind, shared = BASIS[name]
        if basis not in BASIS_MEANING:
            problems.append(f"{name}: declares unknown basis {basis!r}")
        if not catches or not blind:
            problems.append(f"{name}: names no catch or no blind spot; a "
                            f"check with no stated blind spot has not been "
                            f"read for one")
        if basis == GENERATOR and not shared:
            problems.append(
                f"{name}: declares GENERATOR and names no shared symbol; the "
                f"whole content of that declaration is which function both "
                f"sides go through")
        if not shared:
            continue
        symbol, producer = shared
        if symbol not in own_text:
            problems.append(
                f"{name}: declares it shares {symbol!r} with {producer}, and "
                f"{symbol!r} does not appear in this file")
        path = REPO / producer
        if not path.exists():
            problems.append(f"{name}: names producer {producer}, which is not "
                            f"on disk")
        elif symbol not in path.read_text(encoding="utf-8", errors="replace"):
            problems.append(
                f"{name}: declares it shares {symbol!r} with {producer}, and "
                f"{producer} no longer mentions it; either the coupling is "
                f"gone and this check is now independent, or it moved")

    counted: dict[str, list[str]] = {}
    for name in sorted(set(BASIS) & names):
        counted.setdefault(BASIS[name][0], []).append(name)
    detail = [f"{basis}: {len(rows)} check(s) -- {BASIS_MEANING[basis]}"
              for basis, rows in sorted(counted.items())
              if basis in BASIS_MEANING]
    coupled = sorted(counted.get(GENERATOR, []) + counted.get(TRANSCRIBED, []))
    detail.append(
        f"{len(coupled)} of {len(names)} check(s) cannot fail on a defect "
        f"inside the code or the constants they check: "
        f"{', '.join(coupled) or 'none'}")
    detail.append(
        f"{len(counted.get(EVIDENCE, []))} check(s) re-derive a published "
        f"number from a primary artifact by arithmetic performed here")
    if problems:
        return Result("every check states its basis", FAIL,
                      f"{len(problems)} declaration(s) are missing or no "
                      f"longer true", problems + detail)
    return Result("every check states its basis", PASS,
                  f"all {len(names)} check(s) declare what they test and "
                  f"every declared coupling is still real", detail)


# --------------------------------------------------------------------------
# What clearing each finding costs
# --------------------------------------------------------------------------
#
# THE DEFECT THIS EXISTS FOR. This audit reported that eight stored studies
# could only be cleared by re-running them. Seven could be refitted in place
# from rungs already on disk, for nothing. The work sat undone for two days
# because the report priced it as eight solves. **A remedy priced an order of
# magnitude too high is a reason not to do the work**, and a finding that does
# not say what clearing it costs is asking the reader to guess.
#
# Two checks already carried their price per fault (`REMEDY_REFIT` and
# `REMEDY_NO_RUNGS` above, which vary per record). Everything else carried
# none. This table is the rest: one entry per check, `(remedy, needs_compute,
# basis)`, printed under any WARN or FAIL and carried in the JSON output.
#
# `needs_compute` is the honest question, not the comfortable one. It is True
# only when clearing the finding requires a solver to run. Re-deriving a
# published number from an artifact already on disk is arithmetic, however
# many rows it reads.
REMEDIES: dict[str, tuple[str, bool, str]] = {
    "check_ledger_integrity": (
        "the torn row's bytes are gone and nothing re-derives them; record "
        "the loss and keep the count on the report rather than closing it",
        False, "an interrupted write; there is nothing to recompute"),
    "check_wall_counters_vs_ledger": (
        "republish the wall counters from the ledger through the builder that "
        "reads it, sdk/scripts/build_wall.py",
        False, "arithmetic over rows already on disk"),
    "check_ledger_stalls": (
        "publish the cleaned figure beside the gross one and mark the stall "
        "rows in the ledger as host stalls",
        False, "the rows are identified; the fix is a label and a subtraction"),
    "check_closure_entry_of_record": (
        "repoint the wall at the entry file of record",
        False, "both numbers are on disk"),
    "check_memory_scaling_law": (
        "refit the law from its own stored measurements",
        False, "three measurements, already recorded"),
    "check_withdrawn_numbers": (
        "restore the sentinel, or withdraw the number again and say why",
        False, "an edit to a record"),
    "check_evidence_paths_exist": (
        "restore the cited file, or correct the citation to the file that "
        "carries the evidence",
        False, "deciding which of the two is right needs no run"),
    "check_f2_reproduction": (
        "re-derive the coefficients from the raw force file the record cites",
        False, "the force file is retained; that was L-27's whole point"),
    "check_cost_predictions": (
        "price an unstarted item from the fitted laws in "
        "demo-output/website/mega-batch/COST_SCALING.md, then check it against "
        "the run",
        True, "recording a pair from an outcome already written is a record "
              "edit and needs no solver; extending the record with a NEW pair "
              "needs the run, and the fit it is checked against is done"),
    "check_ungated_completed_runs": (
        "grade the completed run against its pre-stated expectation from the "
        "statistics it already wrote",
        False, "the run finished; the grading reads its output"),
    "check_gate_table_vs_transcripts": (
        "re-derive the verdict from the transcript, or correct the published "
        "verdict to what the transcript supports",
        False, "the transcript is on disk"),
    "check_wall_credentials_vs_results": (
        "rebuild each credential from its own result file through the "
        "builder, and take the downgrades that fall out",
        False, "re-derivation, not re-measurement"),
    "check_benchmarks_vs_closure_record": (
        "regenerate the published block from the scored entry of record",
        False, "both files exist"),
    "check_fd_grades_current_standard": (
        "regrade from the stored FD tables against the current standard",
        False, "the tables are retained"),
    "check_statistical_labels": (
        "correct the caption; no value moves",
        False, "a display-layer edit"),
    "check_nonconclusive_band_readers": (
        "read the non-conclusive flag at the call site that reads the band",
        False, "a code edit"),
    "check_channel_totals_use_one_rule": (
        "make the total match the channel table it is shown beside, either by "
        "quantifying the input channel or by leaving it out of the total; "
        "which way is Katie's call",
        False, "making the two agree is arithmetic. Quantifying the input "
               "channel properly is a sweep and is a separate item"),
    "check_declared_fleet_vs_work": (
        "show no fleet on a path that dispatches nothing, or make the path do "
        "the work it displays; C-3 in PROPOSALS_OPEN.md puts both to Katie",
        False, "the first option is a code edit. The second costs the demo "
               "its warm replay time, which is wall clock on camera rather "
               "than solver cost"),
    "check_restated_thresholds": (
        "read the governed constant instead of restating its value",
        False, "a code edit"),
    "check_register_group_counts": (
        "recount the entries under each heading and correct the declared "
        "totals",
        False, "counting headings in one file"),
    "check_campaign_json_citations": (
        "restore the cited artifact or repoint the citation",
        False, "a record edit"),
    "check_studies_carry_what_the_fit_records": (
        "per fault, and the per-fault price is already printed with it: refit "
        "in place from the rungs the study stores, or, for a record with no "
        "rungs, re-run the ladder or mark the record unverifiable",
        False, "seven of the eight faults this check has ever raised were "
               "refittable in place; only a record storing no rungs needs a "
               "solve, and that case says so on its own line"),
    "check_declined_ladders_name_their_guard": (
        "recompute the guard map from the rungs the study stores, through "
        "uq.study_numerical",
        False, "same rungs, same arithmetic"),
    "check_order_window_declines_state_their_dimensionality": (
        "read the out-of-plane boundary types off the body's own archived "
        "case and record them on the study",
        False, "reading a boundary file and a checkMesh log"),
    "check_rung_estimates_state_their_iterations": (
        "state the iteration count each rung estimate assumes and the evidence "
        "for it, or record that the ladder stores no iterations so the figure "
        "prices the grid alone",
        False, "the settling curves are in the logs those rungs already "
               "wrote; reading them is not a solve"),
    "check_bundle_drift": (
        "rebuild the bundle from the tree and verify by rendering from inside "
        "it rather than by diffing",
        False, "a copy, and a render"),
    "check_record_writers_name_their_drops": (
        "at each site, either copy the source's .items() minus a named drop "
        "set, as uq.study_numerical does, or declare the exclusions in a "
        "constant with a reason per key, as lab.CREDENTIAL_NOT_ON_CARD does",
        False, "a code edit per site; no number moves and no run is needed"),
    "check_stored_rungs_carry_solved_precision": (
        "restore the rungs from the artifact the solve wrote, a forces file "
        "or a coefficient file, never a rendered table, and refit in place",
        False, "the solved values are on disk; the refit is arithmetic"),
    "check_ladder_rungs_share_one_recipe": (
        "read the refinement level off each rung's own "
        "system/snappyHexMeshDict and record which rungs share one recipe, as "
        "five studies already do; then either refit on a family that shares "
        "one, or record that this body has no usable ladder and say what it "
        "would need",
        False, "reading a meshing dictionary per rung; the R4 precedent shows "
               "BUILDING a valid family costs 6.2 core-minutes at 4 ranks, "
               "and that is a separate item"),
    "check_stored_fits_reproduce_their_values": (
        "refit the study in place from the rungs it already stores under "
        "levels[], through uq.study_numerical, and write back what the fit "
        "produces; for a record no current fit reproduces, establish which "
        "producer wrote it before touching a number",
        False, "the rungs are on disk; the fit is arithmetic on them"),
    "check_every_check_states_its_basis": (
        "declare in BASIS what the new check tests, what it catches and what "
        "it is blind to; for a GENERATOR check, name the symbol it shares "
        "with the producer",
        False, "reading the check that was just written"),
    "check_every_finding_prices_its_remedy": (
        "add the missing check to REMEDIES with its remedy and whether that "
        "remedy needs compute",
        False, "writing down a price nobody had written down"),
}


def check_every_finding_prices_its_remedy() -> Result:
    """Every check in this file states what clearing its findings costs.

    A finding without a price is a finding the reader has to price, and the
    reader guesses high. This audit has already lost two days that way. So the
    table above is required to cover every check, and a new check that lands
    without an entry fails here rather than shipping a finding nobody can
    weigh.
    """
    missing = [check.__name__ for check in CHECKS
               if check.__name__ not in REMEDIES]
    stale = [name for name in REMEDIES
             if name not in {check.__name__ for check in CHECKS}]
    detail = [f"{name}: no remedy and no price" for name in missing]
    detail += [f"{name}: priced here but is not a check any more"
               for name in stale]
    needs = sorted(name for name, (_, compute, _) in REMEDIES.items()
                   if compute)
    detail.append(f"{len(REMEDIES) - len(needs)} of {len(REMEDIES)} check(s) "
                  f"clear at no compute; the {len(needs)} that need a solver: "
                  f"{', '.join(needs) or 'none'}")
    if missing or stale:
        return Result("every finding prices its remedy", FAIL,
                      f"{len(missing)} check(s) state no remedy and "
                      f"{len(stale)} priced entry(s) name no check", detail)
    return Result("every finding prices its remedy", PASS,
                  f"all {len(CHECKS)} check(s) state what clearing their "
                  f"findings costs", detail)


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
    check_stored_fits_reproduce_their_values,
    check_stored_rungs_carry_solved_precision,
    check_ladder_rungs_share_one_recipe,
    check_record_writers_name_their_drops,
    check_declined_ladders_name_their_guard,
    check_order_window_declines_state_their_dimensionality,
    check_bundle_drift,
    check_rung_estimates_state_their_iterations,
    check_every_finding_prices_its_remedy,
    check_every_check_states_its_basis,
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

    priced = []
    for check, result in zip(CHECKS, results):
        entry = REMEDIES.get(check.__name__)
        row = asdict(result)
        if entry:
            remedy, needs_compute, basis = entry
            row["remedy"] = remedy
            row["remedy_needs_compute"] = needs_compute
            row["remedy_basis"] = basis
        declared = BASIS.get(check.__name__)
        if declared:
            tests, catches, blind, shared = declared
            row["tests"] = tests
            row["catches"] = catches
            row["blind_to"] = blind
            row["shares_with_producer"] = (
                f"{shared[0]} in {shared[1]}" if shared else None)
        priced.append(row)

    if args.json:
        print(json.dumps(priced, indent=1))
    else:
        width = max(len(r.name) for r in results)
        print(f"Certonomous self-audit  ({len(results)} checks)")
        print("=" * (width + 60))
        for check, result in zip(CHECKS, results):
            if args.quiet and result.status in (PASS, INFO):
                continue
            declared = BASIS.get(check.__name__)
            tests = declared[0] if declared else "UNDECLARED"
            print(f"[{result.status:<4}] {result.name:<{width}}  "
                  f"{result.summary}")
            print(f"         tests: {tests}")
            for line in result.detail:
                print(f"         - {line}")
            # A GENERATOR or TRANSCRIBED verdict states its blind spot on
            # EVERY status, not only on a failure. The point of the
            # declaration is that a PASS from a check nobody can fail should
            # read as one.
            if declared and (declared[0] in (GENERATOR, TRANSCRIBED)
                             or declared[3]):
                print(f"         BLIND TO: {declared[2]}")
                if declared[3]:
                    print(f"         shares {declared[3][0]} with "
                          f"{declared[3][1]}")
            entry = REMEDIES.get(check.__name__)
            if entry and result.status in (WARN, FAIL):
                remedy, needs_compute, basis = entry
                price = "NEEDS COMPUTE" if needs_compute else "NO COMPUTE"
                print(f"         remedy ({price}): {remedy}")
                print(f"         remedy basis: {basis}")
        print("=" * (width + 60))
        tally = {s: sum(1 for r in results if r.status == s)
                 for s in (PASS, WARN, FAIL, INFO)}
        print("  ".join(f"{k}: {v}" for k, v in tally.items() if v))
        kinds: dict[str, int] = {}
        for check in CHECKS:
            declared = BASIS.get(check.__name__)
            kinds[declared[0] if declared else "UNDECLARED"] = \
                kinds.get(declared[0] if declared else "UNDECLARED", 0) + 1
        print("what these checks test:  "
              + "  ".join(f"{k}: {v}" for k, v in sorted(kinds.items())))

    return 1 if any(r.status == FAIL for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
