#!/usr/bin/env python3
"""Replay the grandfathered monitor rules S1 to S6 against the log archive.

WHY THIS EXISTS. `docs/standards/MONITOR_STANDARD.md` section 3.1 records that
seven of eleven monitor rules have never been replayed against the archive, and
six of those seven shipped with the monitor before the reading program, so they
never met the intake requirement that a detection rule states its fire count
before adoption. S8, S9 and S10 were each measured before adoption and each is
defensible. S7 was adopted on reasoning and fires on two thirds of the lab's
completed steady work. This script closes the gap for S1 to S6 by measuring
them the same way S10 was measured: over the whole archive, not a sample.

WHAT IT MEASURES. Two passes over every archived solver log.

  Pass A, ungated. `LogMonitor(novel=True)` reads every line. S1 (fpe), S2
  (nan), S3 (residual spike) and S4 (bounding) need nothing from the case, so
  their counts are complete. S5 (first-seen warning) fires on novelty by
  construction, so its count over an archive of already-solved work is not a
  false-positive rate; what the sweep can say about it is how many DISTINCT
  warning shapes the archive holds, which bounds how much a novel run can be
  asked to read. That number is reported and labelled as what it is.

  Added 2026-08-01, after the first run of this script found that two of the
  six rules could not be described accurately: S4 and S5 are now measured on
  what a reader would act on rather than on a raw fire count.

  S4 is reported per EPISODE -- one per field per log, with the span of the
  clipping and a severity -- and the retired "first ten percent of iterations"
  ladder is replayed alongside the one in force, so the two are comparable in
  the same artifact. S5's whole vocabulary is listed, not just counted: the
  first run of this script found it was two keys over 449 logs and that both
  were artefacts of the key rather than facts about the logs.

  Pass B, gated. S6 (residual stall) stays off without the `residualControl`
  target the solve was aiming for. The standard records that the archived logs
  do not carry that target. They do not, but a large minority of them sit
  beside the case that produced them, and that case's `system/fvSolution`
  does. Pass B recovers the target where it is recoverable and replays S6 on
  exactly those logs, bracketed between the tightest and the loosest target
  the case declares, since `LogMonitor` takes one target and a case declares
  one per field.

  The tightest target is the upper bound on firing: a field is only in scope
  while it is above target, so the tighter the target the longer S6 is
  entitled to speak. The loosest is the lower bound. A rule whose two bounds
  agree is measured; one whose bounds straddle a decision is not, and says so.

NO COMPUTE. Every number here comes from a file already on disk.

  python3 sdk/scripts/replay_monitor_rules.py [--out PATH] [--limit N]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sdk"))

from chief_engineer.head_engineer import LogMonitor  # noqa: E402
from chief_engineer.log_signatures import normalise_log_key  # noqa: E402

# The same root the S10 archive sweep uses (sdk/tests/test_log_signatures.py,
# ArchiveSweepTests), so the corpora of the two measurements are comparable.
ARCHIVE_ROOT = REPO / "demo-output"

#: An OpenFOAM APPLICATION RUN writes an `Exec   :` line in its startup
#: banner. Dictionary and field files carry the same FoamFile banner but never
#: that line, so this distinguishes a RUN LOG from the rest of a case.
_EXEC_BANNER = b"Exec   :"


def run_logs(root: Path) -> list[Path]:
    """Every OpenFOAM run log under ``root``, DERIVED FROM CONTENT.

    This used to be ``root.rglob("*.log")``. OpenFOAM writes ``log.<app>``,
    so the corpus behind six adopted rules was selected by a filename
    accident: 449 files at the last run, against 1,375 real run logs.
    Section 3.1 makes a replay the gate on adoption, and that gate was
    discharged against 28% of the evidence.

    **The fix is not a wider glob.** A list of patterns is the same defect
    with more entries (L-49): matching ``*.log`` AND ``log.*`` together still
    misses 96 real run logs in this archive -- ``logMeshCheck.txt``,
    ``A5_logMeshGeneration.txt``, ``A4_coarse_log.checkMesh``. So the corpus
    is derived from what the solver actually WROTE, the same principle as
    deriving a gate from the case's own dictionaries: a file is a run log
    when it announces itself as one.

    Binary files are skipped by a NUL test rather than by extension, so no
    naming rule participates in the selection at any point.
    """
    found: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            head = path.open("rb").read(4096)
        except OSError:
            continue
        if b"\x00" in head:
            continue
        if head.startswith(_EXEC_BANNER) or b"\n" + _EXEC_BANNER in head:
            found.append(path)
    return sorted(found)


RESIDUAL_LINE = re.compile(r"Solving for \w+,.*Initial residual =")
COURANT_LINE = re.compile(r"Courant Number mean:")

RESIDUAL_CONTROL = re.compile(r"residualControl\s*\{([^}]*)\}", re.S)
CONTROL_ENTRY = re.compile(r"^\s*(?:\"?)([A-Za-z][\w.\"|()]*)(?:\"?)\s+"
                           r"([0-9.eE+-]+)\s*;", re.M)

# S1 to S6 in the anomaly kinds LogMonitor raises.
RULE_KINDS = {
    "S1": "fpe",
    "S2": "nan",
    "S3": "residual-spike",
    "S4": "bounding",
    "S5": "novel-warning",
    "S6": "residual-stall",
}


def case_targets(log: Path) -> tuple[dict[str, float], Path | None]:
    """The residualControl targets of the case that wrote this log, if the
    case is archived beside it. Returns ({field: target}, fvSolution path)."""
    for candidate in (log.parent / "system" / "fvSolution",
                      log.parent / "case" / "system" / "fvSolution",
                      log.parent.parent / "system" / "fvSolution",
                      log.parent.parent / "case" / "system" / "fvSolution"):
        if not candidate.exists():
            continue
        try:
            text = candidate.read_text(errors="replace")
        except OSError:
            return {}, None
        block = RESIDUAL_CONTROL.search(text)
        if not block:
            return {}, candidate
        targets: dict[str, float] = {}
        for field, value in CONTROL_ENTRY.findall(block.group(1)):
            if field in ("relTol", "tolerance", "maxIter"):
                continue
            try:
                targets[field.strip('"')] = float(value)
            except ValueError:
                continue
        return targets, candidate
    return {}, None


def classify(log: Path) -> tuple[bool, bool]:
    """(has residual lines, is transient) without holding the file in memory."""
    residuals = transient = False
    with open(log, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not residuals and RESIDUAL_LINE.search(line):
                residuals = True
            if not transient and COURANT_LINE.search(line):
                transient = True
            if residuals and transient:
                break
    return residuals, transient


def replay(log: Path, *, residual_target: float | None = None) -> dict:
    monitor = LogMonitor(novel=True, residual_target=residual_target)
    step = log.name
    with open(log, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            monitor.feed(step, line)
    summary = monitor.summary()
    kinds = Counter(a.kind for a in monitor.anomalies)
    fatal = Counter(a.kind for a in monitor.anomalies
                    if a.kind in ("nan", "fpe") or a.severity == "fatal")
    # S5's vocabulary. The key is the monitor's own, so the replay measures
    # what the rule actually does rather than a re-implementation of it.
    warnings = {normalise_log_key(obs) for obs in monitor.novel_observations}
    return {"kinds": kinds, "fatal": fatal, "warning_shapes": warnings,
            "bounding": summary["bounding"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(
        REPO / "demo-output" / "website" / "monitor" / "replay_s1_s6.json"))
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    logs = run_logs(ARCHIVE_ROOT)
    if args.limit:
        logs = logs[:args.limit]
    started = time.time()

    corpus = {"all": 0, "with_residuals": 0, "steady": 0, "transient": 0,
              "no_residuals": 0}
    fires: dict[str, set[str]] = {kind: set() for kind in RULE_KINDS.values()}
    fatals: dict[str, set[str]] = {kind: set() for kind in RULE_KINDS.values()}
    hits: dict[str, Counter] = {kind: Counter() for kind in RULE_KINDS.values()}
    warning_shapes: Counter = Counter()
    steady_logs: list[Path] = []
    # S4, graded per episode rather than counted per line.
    s4_logs: Counter = Counter()
    s4_episodes: Counter = Counter()
    s4_documented_window: Counter = Counter()
    s4_examples: dict[str, list[dict]] = {"flag": [], "watch": [], "ungraded": []}

    for index, log in enumerate(logs, 1):
        corpus["all"] += 1
        residuals, transient = classify(log)
        if not residuals:
            corpus["no_residuals"] += 1
        else:
            corpus["with_residuals"] += 1
            corpus["transient" if transient else "steady"] += 1
            if not transient:
                steady_logs.append(log)
        result = replay(log)
        warning_shapes.update(result["warning_shapes"])
        rel_log = str(log.relative_to(REPO))
        if result["bounding"]:
            # A log's grade is its worst episode: one field still clipped at
            # the end is enough, and a log with nothing gradeable is ungraded
            # rather than quietly counted as clean.
            grades = {ep["severity"] or "ungraded" for ep in result["bounding"]}
            worst = ("flag" if "flag" in grades
                     else "watch" if "watch" in grades else "ungraded")
            s4_logs[worst] += 1
            for episode in result["bounding"]:
                grade = episode["severity"] or "ungraded"
                s4_episodes[grade] += 1
                if episode["graded"]:
                    s4_documented_window[
                        "flag" if episode["past_documented_startup_window"]
                        else "watch"] += 1
                if len(s4_examples[grade]) < 5:
                    s4_examples[grade].append({"log": rel_log, **episode})
        for kind, count in result["kinds"].items():
            if kind not in fires:
                continue
            fires[kind].add(str(log.relative_to(REPO)))
            hits[kind][str(log.relative_to(REPO))] = count
        for kind in result["fatal"]:
            if kind in fatals:
                fatals[kind].add(str(log.relative_to(REPO)))
        if index % 25 == 0:
            print(f"  pass A {index}/{len(logs)} "
                  f"({time.time() - started:.0f}s)", file=sys.stderr)

    # Pass B: S6, on the steady logs whose case is archived beside them.
    gated = {"steady_logs": len(steady_logs), "with_targets": 0,
             "tight_fires": [], "loose_fires": [], "targets": {}}
    for log in steady_logs:
        targets, source = case_targets(log)
        if not targets:
            continue
        gated["with_targets"] += 1
        rel = str(log.relative_to(REPO))
        gated["targets"][rel] = {
            "fvSolution": str(source.relative_to(REPO)) if source else None,
            "per_field": targets}
        for bound, target in (("tight_fires", min(targets.values())),
                              ("loose_fires", max(targets.values()))):
            result = replay(log, residual_target=target)
            if result["kinds"].get("residual-stall"):
                gated[bound].append(rel)

    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "archive_root": str(ARCHIVE_ROOT.relative_to(REPO)),
        "corpus": corpus,
        "elapsed_s": round(time.time() - started, 1),
        "rules": {},
        "distinct_warning_shapes": len(warning_shapes),
        # S5's whole vocabulary, listed rather than counted. Before the repair
        # this was two keys over 449 logs and both were defects of the key: the
        # unsplit multi-line banner, and a normaliser with no digit requirement
        # that rewrote allowSystemOperations to allowSyst#mOp#rations.
        "s5_vocabulary": [{"key": key, "logs": count}
                          for key, count in warning_shapes.most_common()],
        # S4 graded per episode. ``documented_window`` replays the ladder the
        # standard carried until this run -- WATCH inside the first ten percent
        # of iterations, FLAG past it -- so the two can be compared directly.
        "s4": {
            "logs_by_grade": dict(s4_logs),
            "episodes_by_grade": dict(s4_episodes),
            "documented_window_episodes": dict(s4_documented_window),
            "examples": s4_examples,
        },
        "gated_s6": {k: v for k, v in gated.items() if k != "targets"},
        "s6_target_sources": gated["targets"],
    }
    for rule, kind in RULE_KINDS.items():
        report["rules"][rule] = {
            "kind": kind,
            "logs_fired": len(fires[kind]),
            "logs_fatal": len(fatals[kind]),
            "total_findings": int(sum(hits[kind].values())),
            "examples": sorted(fires[kind])[:5],
        }
    report["rules"]["S6"].update({
        "logs_fired": len(gated["tight_fires"]),
        "logs_fatal": 0,
        "bracket": {"tightest_target": len(gated["tight_fires"]),
                    "loosest_target": len(gated["loose_fires"]),
                    "corpus": gated["with_targets"]},
        "examples": sorted(gated["tight_fires"])[:5],
    })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items()
                      if k != "s6_target_sources"}, indent=2))
    print(f"\nwrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
