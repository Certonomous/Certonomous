#!/usr/bin/env python3
"""Monitor-standard replay: S10 (a,b,c) and S12, as written, against the F8
S10-class specimen -- the `phase6_mrf_pfinit` run that diverged to 1e99 N.m
behind a 1.4e-8 Ux residual (F8_MRF_HAND2001_GATE.md section 12).

Executes proposal `f8-s10-replay-of-the-mrf-limit-cycle` (approved
2026-08-07). Zero compute: reads archived logs and histories only, and calls
the lab's own detector functions from `sdk/chief_engineer/log_signatures.py`
verbatim -- no reinterpretation, no threshold changes. Also replays the same
rules against the original `phase6_mrf` limit-cycle history for contrast.

Writes replay_result.json beside this script.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# NOT `parents[5]`, and this is a defect class rather than a typo: a
# repository root derived by COUNTING segments up from a path under a
# MOVING tree points somewhere else the moment the tree moves.  MOVE_MAP
# batch 7 made this file ONE SEGMENT SHALLOWER, so `parents[5]` went from
# the repository root to `/home/ubuntu`.  There is no path literal in the
# expression, so no prefix rewrite and no grep for `demo-output` reaches it
# -- the same class cost `sdk/tests/test_a2_shape.py:28` a green comparison
# over ten synthetic bodies at batch 6.  DERIVED BY SEARCHING for the
# marker, so the answer no longer depends on this file's depth.
REPO = next((_p for _p in Path(__file__).resolve().parents
            if (_p / "scripts" / "lab_paths.py").is_file()), None)
if REPO is None:
    raise RuntimeError(
        "cannot locate scripts/lab_paths.py above %s; refusing to "
        "guess a repository root" % __file__)
sys.path.insert(0, str(REPO / "sdk"))

from chief_engineer.log_signatures import (  # noqa: E402
    UNSETTLED_MIN_ITERATIONS,
    classify_bound_line,
    detect_ceiling_clip,
    detect_normalisation_collapse,
    detect_residual_norm_contradiction,
    detect_unsettled_stop,
)

F8 = REPO / "demo-output/website/campaign/F8_runs"
RES_RE = re.compile(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)")


def parse_log(path: Path) -> dict:
    """Per-field initial-residual series, bound-line classification, nan/fpe."""
    residuals: dict[str, list[float]] = {}
    seen_this_step: set[str] = set()
    bounds = {"floor": 0, "ceiling": 0, "fields": set()}
    ceiling_findings = []
    nan_lines = fpe_lines = 0
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("Time = "):
            seen_this_step = set()
            continue
        m = RES_RE.search(line)
        if m and m.group(1) not in seen_this_step:
            residuals.setdefault(m.group(1), []).append(float(m.group(2)))
            seen_this_step.add(m.group(1))
        b = classify_bound_line(line)
        if b:
            bounds[b["direction"]] += 1
            bounds["fields"].add(b["field"])
            c = detect_ceiling_clip(line)
            if c:
                ceiling_findings.append(c)
        low = line.lower()
        if "solving for" in low and "nan" in low:
            nan_lines += 1
        if "sigfpe" in low and "handler" in low:
            fpe_lines += 1
    bounds["fields"] = sorted(bounds["fields"])
    return dict(residuals=residuals, bounds=bounds,
                ceiling_findings=ceiling_findings,
                nan_solver_lines=nan_lines, fpe_handler_lines=fpe_lines)


def moment_series(run: Path) -> list[tuple[float, float]]:
    rows: list[tuple[float, float]] = []
    for dat in sorted(run.glob("postProcessing/bladeForces/*/moment.dat"),
                      key=lambda p: float(p.parent.name)):
        for line in dat.read_text(errors="replace").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            t, mx = float(parts[0]), float(parts[1])
            if not rows or t > rows[-1][0]:
                rows.append((t, mx))
    return rows


def replay(run_name: str, log_name: str = "log.simpleFoam") -> dict:
    run = F8 / run_name
    parsed = parse_log(run / log_name)
    out: dict = {"run": run_name}

    # ---- S10a ceiling clip: verbatim detector over every log line (done in
    # parse_log via detect_ceiling_clip).
    out["S10a_ceiling_clip"] = {
        "fires": bool(parsed["ceiling_findings"]),
        "findings": parsed["ceiling_findings"][:3],
        "bound_lines_floor": parsed["bounds"]["floor"],
        "bound_lines_ceiling": parsed["bounds"]["ceiling"],
        "bound_fields": parsed["bounds"]["fields"],
    }

    # ---- S10b normalisation collapse: per field, peers = all other fields.
    s10b = {}
    for field, series in parsed["residuals"].items():
        peers = [v for f, s in parsed["residuals"].items() if f != field
                 for v in s]
        finding = detect_normalisation_collapse(series, peer_residuals=peers)
        s10b[field] = {
            "fires": finding is not None,
            "min_residual": min(series),
            "iterations": len(series),
            "finding": finding,
        }
    out["S10b_normalisation_collapse"] = s10b

    # ---- S10c residual norm contradiction: needs an unnormalised end-of-run
    # norm block, which simpleFoam does not print. Detector called on the
    # empty mapping the log actually provides.
    out["S10c_residual_norm_contradiction"] = {
        "fires": detect_residual_norm_contradiction({}) is not None,
        "note": "simpleFoam prints no unnormalised residual-norm block; the "
                "branch's required input does not exist in this log",
    }

    # ---- S12 unsettled stop on the monitored quantity (blade moment Mx).
    series = [mx for _, mx in moment_series(run)]
    finding = detect_unsettled_stop(series, quantity="Mx",
                                    stop_reason="endTime")
    out["S12_unsettled_stop_on_Mx"] = {
        "fires": finding is not None,
        "samples": len(series),
        "min_iterations_required": UNSETTLED_MIN_ITERATIONS,
        "first": series[0] if series else None,
        "last": series[-1] if series else None,
        "finding": finding,
    }
    # counterfactual: S12's own window arithmetic with the length floor
    # removed, computed explicitly so the record shows WHICH clause fails.
    if finding is None and len(series) >= 20:
        import chief_engineer.log_signatures as ls
        w = ls.unsettled_window(len(series))
        tail = series[-w:]
        half = w // 2
        drift = (sum(tail[half:]) / len(tail[half:])
                 - sum(tail[:half]) / len(tail[:half]))
        scale = abs(sum(tail) / len(tail))
        steps = [b - a for a, b in zip(tail, tail[1:]) if b != a]
        forward = sum(1 for s in steps if (s > 0.0) == (drift > 0.0))
        out["S12_counterfactual_no_length_floor"] = {
            "window": w,
            "rel_drift": drift / scale if scale else None,
            "rel_drift_tol": ls.UNSETTLED_REL_DRIFT,
            "monotone": forward / len(steps) if steps else None,
            "monotone_min": ls.UNSETTLED_MONOTONE_MIN,
            "would_fire": bool(scale and abs(drift / scale)
                               >= ls.UNSETTLED_REL_DRIFT
                               and steps and forward / len(steps)
                               >= ls.UNSETTLED_MONOTONE_MIN),
        }
    out["nan_solver_lines"] = parsed["nan_solver_lines"]
    out["fpe_handler_lines"] = parsed["fpe_handler_lines"]
    out["final_initial_residuals"] = {
        f: s[-1] for f, s in parsed["residuals"].items()}
    return out


def main() -> None:
    result = {
        "specimen": replay("phase6_mrf_pfinit"),
        "limit_cycle_for_contrast": replay("phase6_mrf"),
        "s12_corpus_note": (
            "sdk/scripts/replay_s12_unsettled_stop.py builds its corpus from "
            "rglob('coefficient.dat') only; forces-object moment.dat/"
            "force.dat histories never enter the archive-replay rail"),
    }
    path = Path(__file__).parent / "replay_result.json"
    path.write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1)[:4000])


if __name__ == "__main__":
    main()
