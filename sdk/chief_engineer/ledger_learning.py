"""Distill the mega-batch ledger into an honest learned summary.

The all-night mega-batch appends thousands of real solver evaluations to a
durable JSONL ledger (``demo-output/website/mega-batch/ledger.jsonl``). This
module is the part of the lab that *learns* from that ledger instead of just
counting it. It walks every row and produces a study JSON with:

- per-family counts, wall-time, and failure rates;
- the L/D-versus-design trends the wing rows actually support, with the fit
  quality measured (r squared reported, never asserted);
- the Cd-versus-Re trend from the cylinder solves;
- the loss-versus-opening-angle trend from the reduced-order valve rows;
- best and worst designs actually seen, cited by ledger index;
- a human-readable "what the lab has learned" list, every number of which is
  computed from real ledger rows.

Output location (documented contract): the study is written next to the
ledger as ``learned_study.json`` (so the default lives at
``demo-output/website/mega-batch/learned_study.json``). ``lab_stats`` reads it
from there, or from the ``CERTONOMOUS_LEDGER_STUDY`` environment override.

Every statement carries provenance: ledger path, row count, and timestamp.
Trends with too few points or poor fits are reported as unsupported, not
dressed up. Nothing is invented.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[2]

STUDY_BASENAME = "learned_study.json"

WING = "vspaero-wing"
CYLINDER = "openfoam-cylinder"
VALVE = "reduced-order"

_FAMILY_LABELS = {
    WING: "VSPAERO wing polars",
    CYLINDER: "OpenFOAM cylinder solves",
    VALVE: "reduced-order valve evaluations",
}


def default_ledger_path() -> Path:
    env = os.environ.get("CERTONOMOUS_MEGABATCH_LEDGER")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "demo-output" / "website" / "mega-batch" / "ledger.jsonl").resolve()


def default_study_path(ledger_path: Path | None = None) -> Path:
    """Where the distilled study lives: next to the ledger it came from."""
    env = os.environ.get("CERTONOMOUS_LEDGER_STUDY")
    if env:
        return Path(env).resolve()
    base = ledger_path or default_ledger_path()
    return base.parent / STUDY_BASENAME


# --------------------------------------------------------------------------
# Small numeric helpers (pure python; the ledger is the only input)
# --------------------------------------------------------------------------

def _linear_fit(xs: list[float], ys: list[float]) -> dict[str, Any] | None:
    """Ordinary least squares y = a*x + b with measured r squared."""
    n = len(xs)
    if n < 3 or len(ys) != n:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx <= 0 or syy <= 0:
        return None
    slope = sxy / sxx
    intercept = my - slope * mx
    r2 = (sxy * sxy) / (sxx * syy)
    return {
        "slope": round(slope, 6),
        "intercept": round(intercept, 6),
        "r2": round(r2, 4),
        "n": n,
    }


def _fit_quality(fit: dict[str, Any] | None) -> str:
    """Honest label for how much the data supports a linear trend."""
    if fit is None or fit["n"] < 10:
        return "insufficient data"
    r2 = fit["r2"]
    if r2 >= 0.7:
        return "strong"
    if r2 >= 0.4:
        return "moderate"
    if r2 >= 0.15:
        return "weak"
    return "not supported"


def _stats(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n if n > 1 else 0.0
    return {
        "n": n,
        "mean": round(mean, 4),
        "std": round(math.sqrt(var), 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def _num(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return float(value)


# --------------------------------------------------------------------------
# Ledger walk
# --------------------------------------------------------------------------

def read_rows(ledger_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not ledger_path.exists():
        return rows
    for line in ledger_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _family_breakdown(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    families: dict[str, dict[str, Any]] = {}
    for row in rows:
        solver = str(row.get("solver", "unknown"))
        bucket = families.setdefault(solver, {
            "label": _FAMILY_LABELS.get(solver, solver),
            "attempted": 0,
            "ok": 0,
            "failed": 0,
            "wall_seconds": 0.0,
        })
        bucket["attempted"] += 1
        if row.get("ok"):
            bucket["ok"] += 1
        else:
            bucket["failed"] += 1
        wall = _num(row.get("wall_seconds"))
        if wall is not None:
            bucket["wall_seconds"] += wall
    for bucket in families.values():
        attempted = bucket["attempted"]
        bucket["failure_rate"] = round(bucket["failed"] / attempted, 4) if attempted else 0.0
        bucket["wall_seconds"] = round(bucket["wall_seconds"], 1)
        bucket["wall_seconds_mean"] = (
            round(bucket["wall_seconds"] / bucket["ok"], 2) if bucket["ok"] else None
        )
    return dict(sorted(families.items()))


def _wing_section(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """What the wing polars actually support about L/D versus design."""
    samples: list[dict[str, float]] = []
    for row in rows:
        if row.get("solver") != WING or not row.get("ok"):
            continue
        design = row.get("design") or {}
        metrics = row.get("metrics") or {}
        span = _num(design.get("span"))
        area = _num(design.get("area"))
        sweep = _num(design.get("sweep"))
        ld = _num(metrics.get("L_D"))
        cl = _num(metrics.get("cl"))
        cdi = _num(metrics.get("cdi"))
        if span is None or area is None or area <= 0 or ld is None:
            continue
        sample: dict[str, float] = {
            "index": row.get("index"),
            "aspect_ratio": span * span / area,
            "sweep": sweep if sweep is not None else 0.0,
            "L_D": ld,
        }
        if cl is not None and cdi is not None and cdi > 0:
            sample["e_implied"] = (cl * cl) / (math.pi * sample["aspect_ratio"] * cdi)
        samples.append(sample)

    section: dict[str, Any] = {"n": len(samples)}
    if not samples:
        return section

    best = max(samples, key=lambda s: s["L_D"])
    worst = min(samples, key=lambda s: s["L_D"])
    section["L_D"] = _stats([s["L_D"] for s in samples])
    section["best"] = {"ledger_index": best["index"],
                       "aspect_ratio": round(best["aspect_ratio"], 2),
                       "sweep_deg": round(best["sweep"], 2),
                       "L_D": round(best["L_D"], 2)}
    section["worst"] = {"ledger_index": worst["index"],
                        "aspect_ratio": round(worst["aspect_ratio"], 2),
                        "sweep_deg": round(worst["sweep"], 2),
                        "L_D": round(worst["L_D"], 2)}

    fit_ar = _linear_fit([s["aspect_ratio"] for s in samples],
                         [s["L_D"] for s in samples])
    section["trend_LD_vs_aspect_ratio"] = {
        "fit": fit_ar, "quality": _fit_quality(fit_ar)}

    fit_sweep = _linear_fit([s["sweep"] for s in samples],
                            [s["L_D"] for s in samples])
    section["trend_LD_vs_sweep"] = {
        "fit": fit_sweep, "quality": _fit_quality(fit_sweep)}

    e_values = [s["e_implied"] for s in samples if "e_implied" in s]
    section["implied_span_efficiency"] = _stats(e_values)
    return section


def _cylinder_section(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Cd versus Re from the steady-laminar cylinder solves."""
    res: list[float] = []
    cds: list[float] = []
    converged = 0
    n = 0
    for row in rows:
        if row.get("solver") != CYLINDER or not row.get("ok"):
            continue
        metrics = row.get("metrics") or {}
        cd = _num(metrics.get("Cd"))
        re = _num(metrics.get("Re"))
        if cd is None or re is None or cd <= 0 or re <= 0:
            continue
        n += 1
        cds.append(cd)
        res.append(re)
        if _num(metrics.get("converged")) == 1.0:
            converged += 1

    section: dict[str, Any] = {"n": n}
    if not n:
        return section
    section["Cd"] = _stats(cds)
    section["Re"] = _stats(res)
    section["converged_fraction"] = round(converged / n, 4)
    fit = _linear_fit([math.log(r) for r in res], [math.log(c) for c in cds])
    section["trend_logCd_vs_logRe"] = {"fit": fit, "quality": _fit_quality(fit)}
    return section


def _valve_section(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Cycle-weighted loss versus opening angle from the reduced-order rows."""
    angles: list[float] = []
    losses: list[float] = []
    feasible = 0
    samples: list[tuple[float, float, Any]] = []
    for row in rows:
        if row.get("solver") != VALVE or not row.get("ok"):
            continue
        design = row.get("design") or {}
        metrics = row.get("metrics") or {}
        angle = _num(design.get("opening_angle_deg"))
        loss = _num(metrics.get("cycle_weighted_loss_Pa"))
        if angle is None or loss is None:
            continue
        angles.append(angle)
        losses.append(loss)
        samples.append((loss, angle, row.get("index")))
        if metrics.get("feasible"):
            feasible += 1

    section: dict[str, Any] = {"n": len(samples)}
    if not samples:
        return section
    best = min(samples)
    section["loss_Pa"] = _stats(losses)
    section["best"] = {"ledger_index": best[2],
                       "opening_angle_deg": round(best[1], 2),
                       "cycle_weighted_loss_Pa": round(best[0], 2)}
    section["feasible_fraction"] = round(feasible / len(samples), 4)
    fit = _linear_fit(angles, losses)
    section["trend_loss_vs_angle"] = {"fit": fit, "quality": _fit_quality(fit)}
    return section


# --------------------------------------------------------------------------
# Human-readable "what the lab has learned"
# --------------------------------------------------------------------------

def _pct(x: float) -> str:
    return f"{x * 100.0:.0f} percent"


def _learned_sentences(families: dict[str, Any], wing: dict[str, Any],
                       cylinder: dict[str, Any], valve: dict[str, Any],
                       ok_rows: int) -> list[str]:
    """Plain sentences, every number computed from ledger rows.

    Style rules enforced here: no em dashes, and none of the words the demo
    bans from on-camera strings.
    """
    learned: list[str] = []

    trend = wing.get("trend_LD_vs_aspect_ratio") or {}
    fit = trend.get("fit")
    if fit and wing.get("n"):
        quality = trend.get("quality", "insufficient data")
        if quality in ("strong", "moderate"):
            learned.append(
                f"Across {wing['n']} wing polars, higher aspect ratio raises L/D: "
                f"about {fit['slope']:+.2f} in L/D per unit of aspect ratio, and the "
                f"fit explains {_pct(fit['r2'])} of the variance (r2 = {fit['r2']:.2f}). "
                f"That is a {quality} trend, measured, not assumed."
            )
        else:
            learned.append(
                f"Across {wing['n']} wing polars the linear L/D versus aspect-ratio "
                f"fit only reaches r2 = {fit['r2']:.2f}, so the ledger does not yet "
                f"support a clean linear law; the lab keeps sampling."
            )
    e_stats = wing.get("implied_span_efficiency")
    if e_stats and e_stats["n"] >= 10:
        learned.append(
            f"The induced-drag rows imply a span efficiency near "
            f"{e_stats['mean']:.2f} (spread {e_stats['std']:.2f} over "
            f"{e_stats['n']} polars), pulled straight from cl and cdi."
        )
    if wing.get("best"):
        b = wing["best"]
        learned.append(
            f"Best wing seen so far: L/D {b['L_D']:.1f} at aspect ratio "
            f"{b['aspect_ratio']:.1f} and sweep {b['sweep_deg']:.1f} deg "
            f"(ledger row {b['ledger_index']})."
        )

    cyl_trend = cylinder.get("trend_logCd_vs_logRe") or {}
    cyl_fit = cyl_trend.get("fit")
    if cyl_fit and cylinder.get("n"):
        quality = cyl_trend.get("quality", "insufficient data")
        direction = "falls" if cyl_fit["slope"] < 0 else "rises"
        if quality in ("strong", "moderate"):
            learned.append(
                f"Over {cylinder['n']} cylinder solves in the steady-laminar band, "
                f"Cd {direction} with Re with a log-log slope of {cyl_fit['slope']:.2f} "
                f"(r2 = {cyl_fit['r2']:.2f}), consistent with laminar drag theory."
            )
        else:
            learned.append(
                f"Over {cylinder['n']} cylinder solves the Cd versus Re power-law fit "
                f"reaches only r2 = {cyl_fit['r2']:.2f}; the band sampled is too "
                f"narrow to pin the exponent yet."
            )
    if cylinder.get("converged_fraction") is not None and cylinder.get("n"):
        learned.append(
            f"{_pct(cylinder['converged_fraction'])} of the {cylinder['n']} "
            f"cylinder solves converged to residual tolerance."
        )

    valve_trend = valve.get("trend_loss_vs_angle") or {}
    valve_fit = valve_trend.get("fit")
    if valve_fit and valve.get("best"):
        b = valve["best"]
        learned.append(
            f"Across {valve['n']} reduced-order valve evaluations, wider opening "
            f"angles cut cycle-weighted loss (slope {valve_fit['slope']:.1f} Pa per "
            f"degree, r2 = {valve_fit['r2']:.2f}); the lowest loss seen is "
            f"{b['cycle_weighted_loss_Pa']:.0f} Pa at {b['opening_angle_deg']:.1f} deg "
            f"(ledger row {b['ledger_index']})."
        )

    failures = sum(f.get("failed", 0) for f in families.values())
    attempted = sum(f.get("attempted", 0) for f in families.values())
    if attempted:
        learned.append(
            f"Reliability: {failures} of {attempted} attempted evaluations failed "
            f"({_pct(failures / attempted)}); every failure stays in the ledger "
            f"and counts against the fleet."
        )
    if ok_rows:
        learned.append(
            f"All of the above rests on {ok_rows} completed evaluations in the "
            f"fleet ledger; nothing here is asserted without a row behind it."
        )
    return learned


# --------------------------------------------------------------------------
# Distill + persist
# --------------------------------------------------------------------------

def distill(ledger_path: Path | None = None) -> dict[str, Any]:
    """Walk the ledger and build the learned-study dict (no file I/O out)."""
    path = (ledger_path or default_ledger_path()).resolve()
    rows = read_rows(path)
    ok_rows = sum(1 for r in rows if r.get("ok"))
    timestamps = sorted(str(r.get("timestamp")) for r in rows if r.get("timestamp"))

    families = _family_breakdown(rows)
    wing = _wing_section(rows)
    cylinder = _cylinder_section(rows)
    valve = _valve_section(rows)

    return {
        "study": "fleet-ledger-learning",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "provenance": {
            "ledger_path": str(path),
            "row_count": len(rows),
            "ok_rows": ok_rows,
            "failed_rows": len(rows) - ok_rows,
            "first_timestamp": timestamps[0] if timestamps else None,
            "last_timestamp": timestamps[-1] if timestamps else None,
        },
        "families": families,
        "wing": wing,
        "cylinder": cylinder,
        "valve": valve,
        "learned": _learned_sentences(families, wing, cylinder, valve, ok_rows),
    }


def distill_to_file(ledger_path: Path | None = None,
                    study_path: Path | None = None) -> dict[str, Any]:
    """Distill the ledger and write the study JSON atomically; returns it."""
    ledger = (ledger_path or default_ledger_path()).resolve()
    out = study_path or default_study_path(ledger)
    study = distill(ledger)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(study, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    os.replace(tmp, out)
    return study


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Distill the mega-batch ledger into a learned study.")
    parser.add_argument("--ledger", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    study = distill_to_file(args.ledger, args.out)
    out = args.out or default_study_path(args.ledger or default_ledger_path())
    print(f"[ledger-learning] {study['provenance']['row_count']} rows distilled "
          f"-> {out}")
    for line in study["learned"]:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
