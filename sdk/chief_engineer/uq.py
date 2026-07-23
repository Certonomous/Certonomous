"""Quantified uncertainty studies: discretization ladders, closure spreads,
and the combined expanded uncertainty.

A study is a stored, provenance-carrying record produced by REAL solves (a
3-mesh refinement ladder, a same-mesh closure trio) or by real evaluations of
the actual models (sizing-vs-anchor deviations, correlation families). The
channels a mission displays come from the stored study that matches its setup
fingerprint; a mission whose fingerprint has no study says "study pending"
rather than reusing a stale band.

Honesty rails (hard rules, tested):
- every channel value carries its method label;
- an inter-closure spread is a screening estimate, never a bound;
- channels never upgrade a fidelity chip to VALIDATED (experiment gates that);
- a ladder that does not converge to an observed order reports
  "refinement study inconclusive: non-monotone convergence" with the
  conservative fallback band, that sentence, not a fake number.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Iterable, Sequence

STUDIES_DIR = (Path(__file__).resolve().parents[2]
               / "models" / "curriculum" / "uq-studies")

INCONCLUSIVE = "refinement study inconclusive: non-monotone convergence"
DEGENERATE = ("refinement study inconclusive: refinement parameter did not "
              "change the mesh between rungs")


# --------------------------------------------------------------------------
# Setup fingerprint (Q4)
# --------------------------------------------------------------------------

def setup_fingerprint(*, body: str, solver: str, closure: str,
                      velocity: float | None = None,
                      reynolds: float | None = None,
                      refinement: int | float | None = None,
                      iterations: int | None = None) -> str:
    """Stable hash of everything that makes a stored band transferable."""
    payload = json.dumps({
        "body": str(body).lower(), "solver": str(solver).lower(),
        "closure": str(closure).lower(),
        "velocity": None if velocity is None else round(float(velocity), 6),
        "reynolds": None if reynolds is None else f"{float(reynolds):.3e}",
        "refinement": refinement,
        "iterations": iterations,
    }, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# Discretization ladder math (Q1)
# --------------------------------------------------------------------------

def ladder_band(cells: Sequence[float], values: Sequence[float],
                ) -> dict[str, Any]:
    """Observed order and discretization band from a 3-level ladder.

    ``cells`` are the mesh cell counts coarse-to-fine; ``values`` the solution
    functional on each mesh in the same order. Representative mesh size is
    h_i = (1/N_i)^(1/3). With three meshes the least-squares fit of
    phi = phi0 + a h^p reduces to the classical observed-order solve; the band
    is the GCI on the fine mesh with Fs = 1.25 when the ladder is clean
    (monotone, 0.5 <= p <= 4), and the conservative fallback otherwise
    (Eça and Hoekstra 2014 practice).
    """
    # Collapse rungs whose meshes came out identical (a refinement knob at
    # its floor); a ladder needs three DISTINCT levels to fit an order.
    distinct: list[tuple[float, float]] = []
    for c, v in zip(cells, values):
        if not distinct or float(c) != distinct[-1][0]:
            distinct.append((float(c), float(v)))
    if len(distinct) < 3:
        vals = [v for _, v in distinct] or [0.0]
        spread = max(vals) - min(vals)
        return {"cells": [c for c, _ in distinct],
                "values": vals, "h": None,
                "observed_order": None,
                "band_abs": 3.0 * spread,
                "monotone": None,
                "method": DEGENERATE,
                "conclusive": False}
    (n1, f1), (n2, f2), (n3, f3) = distinct[-3:]
    if not (n1 < n2 < n3):
        raise ValueError("cell counts must increase coarse to fine")
    h1, h2, h3 = ((1.0 / n) ** (1.0 / 3.0) for n in (n1, n2, n3))
    r21 = h2 / h3       # fine pair ratio (>1)
    r32 = h1 / h2
    e21 = f3 - f2       # fine-mesh change
    e32 = f2 - f1
    result: dict[str, Any] = {
        "cells": [n1, n2, n3], "values": [f1, f2, f3],
        "h": [h1, h2, h3],
    }
    monotone = (e21 * e32) > 0.0
    if not monotone or e21 == 0.0:
        # Non-monotone (or flat) ladder: the honest sentence plus a
        # conservative band from the observed range, factor 3 (E&H fallback).
        spread = max(values) - min(values)
        result.update({
            "observed_order": None,
            "band_abs": 3.0 * spread if spread else 0.0,
            "monotone": monotone,
            "method": INCONCLUSIVE,
            "conclusive": False,
        })
        return result
    # Observed order for (possibly) non-constant ratio, fixed-point iteration
    # on the standard implicit relation; constant-ratio ladders converge in one.
    p = abs(math.log(abs(e32 / e21))) / math.log(r21)
    for _ in range(50):
        q = math.log((r21 ** p - 1.0) / (r32 ** p - 1.0)) if r21 != r32 else 0.0
        p_new = abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
        if abs(p_new - p) < 1e-10:
            p = p_new
            break
        p = p_new
    clean = 0.5 <= p <= 4.0
    if clean:
        gci = 1.25 * abs(e21) / (r21 ** p - 1.0)
        gci_middle = gci * r21 ** p
        method = (f"3-mesh ladder (r = {r21:.2f}), observed order "
                  f"p = {p:.2f}; GCI band, Fs = 1.25")
    else:
        gci = 3.0 * (max(values) - min(values))
        gci_middle = gci
        method = (f"3-mesh ladder, observed order p = {p:.2f} outside the "
                  f"credible range; conservative factor-3 band")
    result.update({
        "observed_order": round(p, 3),
        "band_abs": gci,
        "band_abs_middle": gci_middle,
        "monotone": True,
        "method": method,
        "conclusive": clean,
    })
    return result


# --------------------------------------------------------------------------
# Closure / family spreads (Q2)
# --------------------------------------------------------------------------

def spread_estimate(values: dict[str, float], *, label: str) -> dict[str, Any]:
    """Half-range spread across a set of same-question evaluations.

    ``label`` names the family ("inter-closure spread (screening estimate)",
    "correlation-family spread", "model-form vs solver anchors"). The spread
    is a screening estimate by construction and is stored with that word; it
    is never presented as a bound.
    """
    if len(values) < 2:
        raise ValueError("a spread needs at least two members")
    vals = list(values.values())
    half_range = (max(vals) - min(vals)) / 2.0
    return {
        "members": {k: float(v) for k, v in values.items()},
        "band_abs": half_range,
        "method": label,
        "screening_estimate": True,
    }


# --------------------------------------------------------------------------
# Combination (Q3)
# --------------------------------------------------------------------------

def combine_expanded(*, input_2sigma: float | None,
                     numerical_abs: float | None,
                     model_abs: float | None) -> dict[str, Any]:
    """Combined expanded uncertainty: RSS of the quantified channels at 95%.

    Channels that are not quantified simply do not contribute; the caller must
    still show the breakdown (the combined band is never presented without the
    channel table one level down).
    """
    parts = {
        "input": input_2sigma, "numerical": numerical_abs, "model": model_abs,
    }
    quantified = {k: float(v) for k, v in parts.items() if v is not None}
    combined = math.sqrt(sum(v * v for v in quantified.values())) if quantified else None
    return {"combined_95": combined, "contributions": quantified,
            "missing": [k for k, v in parts.items() if v is None]}


# --------------------------------------------------------------------------
# Study records (Q1/Q4)
# --------------------------------------------------------------------------

def study_path(body: str) -> Path:
    STUDIES_DIR.mkdir(parents=True, exist_ok=True)
    return STUDIES_DIR / f"{body}.json"


def save_study(body: str, study: dict[str, Any]) -> Path:
    study = dict(study)
    study.setdefault("body", body)
    study["updated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    path = study_path(body)
    staging = path.with_suffix(".json.tmp")
    staging.write_text(json.dumps(study, indent=2), encoding="utf-8")
    staging.replace(path)
    return path


def load_study(body: str) -> dict[str, Any] | None:
    path = study_path(body)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def channels_for(body: str, fingerprint: str) -> dict[str, Any]:
    """The channel values a mission may display for this body + setup.

    Returns {"numerical": {...}|None, "model": {...}|None, "pending": bool,
    "provenance": [...]}. A fingerprint mismatch yields pending (Q4): the
    numerical channel must then say "study pending", never a stale band.
    """
    study = load_study(body)
    if not study:
        return {"numerical": None, "model": None, "pending": True,
                "provenance": []}
    match = study.get("fingerprint") == fingerprint
    numerical = study.get("numerical") if match else None
    # The model spread is tied to the same fingerprint discipline.
    model = study.get("model") if match else None
    return {
        "numerical": numerical,
        "model": model,
        "pending": not match,
        "provenance": study.get("provenance", []) if match else [],
    }
