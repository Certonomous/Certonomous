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
                *, dim: int = 3) -> dict[str, Any]:
    """Observed order and discretization band from a 3-level ladder.

    ``cells`` are the mesh cell counts coarse-to-fine; ``values`` the solution
    functional on each mesh in the same order. Representative mesh size is
    h_i = (1/N_i)^(1/dim). With three meshes the least-squares fit of
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
                "conclusive": False,
                "dim": int(dim)}
    (n1, f1), (n2, f2), (n3, f3) = distinct[-3:]
    if not (n1 < n2 < n3):
        raise ValueError("cell counts must increase coarse to fine")
    h1, h2, h3 = ((1.0 / n) ** (1.0 / float(dim)) for n in (n1, n2, n3))
    r21 = h2 / h3       # fine pair ratio (>1)
    r32 = h1 / h2
    e21 = f3 - f2       # fine-mesh change
    e32 = f2 - f1
    # Record which dimensionality produced h, for the same reason
    # eca_hoekstra_band does: cell counts cannot reveal a ladder's
    # dimensionality, so the default is an assumption, and an assumption a
    # study file does not carry is one no audit can check. A 2D ladder fitted
    # with the cube root has its observed order stretched by exactly 1.5,
    # which is enough to push a credible fit out of the credible window.
    result: dict[str, Any] = {
        "cells": [n1, n2, n3], "values": [f1, f2, f3],
        "h": [h1, h2, h3], "dim": int(dim),
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
    # Guards per commit e4b0ff1 (eca_hoekstra_band): monotone plus an
    # observed order inside the credible window is not sufficient for
    # "asymptotic" -- the 2026-07-27 B-52 near-miss was monotone with
    # p = 2.25 (inside this window too) yet a human rejected it because its
    # Cd increments GROW with refinement and its Richardson extrapolation
    # lands far outside the whole measured range. Both checks are shared
    # with eca_hoekstra_band via _asymptotic_guard so the two certifiers
    # cannot drift apart on what counts as asymptotic. They only gate the
    # case that would otherwise be certified (clean); an order already
    # outside the window is already non-conclusive below and is not
    # double-penalized.
    asymptotic_note: str | None = None
    phi0: float | None = None
    if clean:
        all_values = [v for _, v in distinct]
        shrinking, extrapolation_ok, phi0 = _asymptotic_guard(
            f1, f2, f3, e21, e32, r21, p, all_values)
        if not shrinking or not extrapolation_ok:
            clean = False
            asymptotic_note = (LADDER_GROWING_INCREMENT_NOTE if not shrinking
                              else LADDER_DIVERGENT_EXTRAPOLATION_NOTE)
    if clean:
        gci = 1.25 * abs(e21) / (r21 ** p - 1.0)
        gci_middle = gci * r21 ** p
        method = (f"3-mesh ladder (r = {r21:.2f}), observed order "
                  f"p = {p:.2f}; GCI band, Fs = 1.25")
    else:
        # Same conservative fallback the non-monotone branch above already
        # uses (factor-3 on the full observed-values range): a guard
        # failure never gets its own, different band formula.
        gci = 3.0 * (max(values) - min(values))
        gci_middle = gci
        method = asymptotic_note or (
            f"3-mesh ladder, observed order p = {p:.2f} outside the "
            f"credible range; conservative factor-3 band")
    result.update({
        "observed_order": round(p, 3),
        "band_abs": gci,
        "band_abs_middle": gci_middle,
        "monotone": True,
        "method": method,
        "conclusive": clean,
        "richardson_extrapolated": phi0,
    })
    return result


ORDER_CLAMP_NOTE = "observed order limited to the theoretical range"
NON_MONOTONE_NOTE = ("rungs not monotone; conservative band, largest spread "
                     "times 1.25")
GROWING_INCREMENT_NOTE = (
    "successive Cd increments GROW with refinement instead of shrinking; "
    "ladder not in the asymptotic range, conservative band, largest spread "
    "times 1.25")
DIVERGENT_EXTRAPOLATION_NOTE = (
    "Richardson-extrapolated value falls outside the measured range; ladder "
    "not in the asymptotic range, conservative band, largest spread times "
    "1.25")

# Tolerance for the extrapolation-sanity guard, as a fraction of the
# measured ladder's range width (max - min of the three rungs used in the
# fit). The Richardson value must land within [lo - tol, hi + tol] or the
# fit is rejected as a divergence signal, not a limit.
#
# Calibrated against the two fixtures on hand:
#   - TMR flat plate (816/3264/13056/52224 cells): shrinking increments,
#     Richardson value 0.0028724 sits ~8.5% of the range width above the
#     top of the measured range [0.0026687, 0.0028564] -- a good,
#     genuinely-converging ladder that must still be accepted.
#   - B-52 (193880/255358/330950 cells): Richardson value 0.0648 sits
#     ~247% of the range width above the top of [0.047196, 0.052275] -- a
#     ladder a human rejected as not asymptotic.
# 0.15 (15% of the range width) clears the good case with roughly 1.8x
# margin to spare while remaining more than an order of magnitude below
# the bad case, so the guard is not a knife's edge on the one fixture that
# must pass.
EXTRAPOLATION_TOL_FRAC = 0.15

# ladder_band's own conservative-fallback convention is factor-3 on the
# observed range (not eca_hoekstra_band's factor-1.25), so its guard-failure
# notes say so rather than reusing GROWING_INCREMENT_NOTE /
# DIVERGENT_EXTRAPOLATION_NOTE verbatim (those hardcode "times 1.25").
LADDER_GROWING_INCREMENT_NOTE = (
    "successive increments GROW with refinement instead of shrinking; "
    "ladder not in the asymptotic range, conservative factor-3 band")
LADDER_DIVERGENT_EXTRAPOLATION_NOTE = (
    "Richardson-extrapolated value falls outside the measured range; "
    "ladder not in the asymptotic range, conservative factor-3 band")


def _asymptotic_guard(f1: float, f2: float, f3: float, e21: float,
                      e32: float, r21: float, p: float,
                      all_values: Sequence[float],
                      ) -> tuple[bool, bool, float | None]:
    """Shared increment-trend and extrapolation-sanity guard math.

    Used by both eca_hoekstra_band and ladder_band so the two grid-
    convergence certifiers can never drift apart on what counts as
    "asymptotic" (commit e4b0ff1's fix, extended to ladder_band). Returns
    (shrinking, extrapolation_ok, richardson_extrapolated); each caller keeps
    its own conservative-fallback band formula and method text.
    """
    shrinking = abs(e21) < abs(e32)
    phi0 = f3 + e21 / (r21 ** p - 1.0) if r21 ** p != 1.0 else None
    range_lo, range_hi = min(all_values), max(all_values)
    tol = EXTRAPOLATION_TOL_FRAC * (range_hi - range_lo)
    extrapolation_ok = (phi0 is not None
                       and (range_lo - tol) <= phi0 <= (range_hi + tol))
    return shrinking, extrapolation_ok, phi0


def eca_hoekstra_band(cells: Sequence[float], values: Sequence[float],
                      *, p_lo: float = 0.5, p_hi: float = 2.5,
                      fs: float = 1.25, dim: int = 3) -> dict[str, Any]:
    """In-mission numerical-uncertainty band from a 3-mesh study.

    The act's live grid-refinement procedure (Eca and Hoekstra 2014,
    least-squares / GCI practice): representative size h = (1/N)^(1/dim), the
    observed order solved from the standard implicit relation, and the band
    Fs * |e21| / (r21^p - 1) on the fine mesh. Guards, per Katie's spec:

    - the observed order used for the band is clamped to [p_lo, p_hi]; a
      clamped study says ORDER_CLAMP_NOTE rather than quoting a silly p;
    - a non-monotone triplet falls back to a conservative band of
      max spread * 1.25 and says NON_MONOTONE_NOTE plainly;
    - fewer than three DISTINCT cell counts is no study at all: band None,
      the caller must refuse to report one (the B-52 degenerate-rung lesson).

    Monotone is necessary but not sufficient for "asymptotic", per the B-52
    ladder that a human rejected on inspection even though it was monotone
    and its p landed inside [p_lo, p_hi] (the 2026-07-27 near-miss: a
    193880/255358/330950 triple with p = 2.25). Two more guards, both of
    which DOWNGRADE the verdict to not-conclusive (never a mere warning,
    because these bands feed live mission channels) and fall back to the
    same conservative spread * 1.25 band as the non-monotone case:

    - increment trend: a converging ladder's successive Cd increments must
      SHRINK on refinement (|e21| < |e32|); growing increments mean the
      solution is moving away, not settling, however clean p looks
      (GROWING_INCREMENT_NOTE);
    - extrapolation sanity: the Richardson-extrapolated value phi0 must land
      within EXTRAPOLATION_TOL_FRAC of the ladder's own measured range; an
      extrapolation outside the data it was fitted from is a divergence
      signal, not a limit (DIVERGENT_EXTRAPOLATION_NOTE).

    A ladder that fails either guard never has its band silently widened or
    narrowed by the fit that failed; the conservative fallback band stands.
    """
    distinct: list[tuple[float, float]] = []
    for c, v in zip(cells, values):
        if not distinct or float(c) != distinct[-1][0]:
            distinct.append((float(c), float(v)))
    if len(distinct) < 3:
        return {"cells": [c for c, _ in distinct],
                "values": [v for _, v in distinct],
                "observed_order": None, "order_used": None, "clamped": False,
                "band_abs": None, "monotone": None, "conclusive": False,
                "method": DEGENERATE}
    (n1, f1), (n2, f2), (n3, f3) = distinct[-3:]
    if not (n1 < n2 < n3):
        raise ValueError("cell counts must increase coarse to fine")
    h1, h2, h3 = ((1.0 / n) ** (1.0 / float(dim)) for n in (n1, n2, n3))
    r21 = h2 / h3
    r32 = h1 / h2
    e21 = f3 - f2
    e32 = f2 - f1
    # Record which dimensionality produced h. This is a DEFAULT, not a
    # detection: cell counts alone cannot tell a 2D ladder from a 3D one, so a
    # 2D case that does not pass dim=2 is silently fitted with the cube root
    # and its observed order comes out scaled by log(2)/log(4**(1/3)), about
    # 1.5. A true 1.6 prints as 2.4 and is then rejected for being outside the
    # credible window, which is the wrong verdict for the wrong reason.
    #
    # Writing dim into the result does not fix a miscalled caller, but it puts
    # the assumption in the study file where an audit can see it, instead of
    # leaving it inferable only from the source.
    result: dict[str, Any] = {"cells": [n1, n2, n3], "values": [f1, f2, f3],
                              "dim": int(dim)}
    if (e21 * e32) <= 0.0:
        spread = max(f1, f2, f3) - min(f1, f2, f3)
        result.update({
            "observed_order": None, "order_used": None, "clamped": False,
            "band_abs": 1.25 * spread, "monotone": False, "conclusive": False,
            "method": NON_MONOTONE_NOTE})
        return result
    p = abs(math.log(abs(e32 / e21))) / math.log(r21)
    for _ in range(50):
        q = math.log((r21 ** p - 1.0) / (r32 ** p - 1.0)) if r21 != r32 else 0.0
        p_new = abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
        if abs(p_new - p) < 1e-10:
            p = p_new
            break
        p = p_new
    # Guard 1 (increment trend): a converging ladder's successive Cd
    # increments must SHRINK on refinement. |e21| is the finer-pair change,
    # |e32| the coarser-pair change; |e21| >= |e32| means the solution is
    # moving away, not settling, no matter how clean p looks.
    # Guard 2 (extrapolation sanity): the Richardson-extrapolated value must
    # land at or very near the measured range of the ladder. An
    # extrapolation that lands outside the data it was fitted from is a
    # divergence signal, not a limit. "The ladder" is every distinct rung
    # this call was given, not only the three used for the local fit -- a
    # coarser rung that was dropped for the order solve is still measured
    # data, and folding it in only ever makes this guard MORE permissive.
    all_values = [v for _, v in distinct]
    shrinking, extrapolation_ok, phi0 = _asymptotic_guard(
        f1, f2, f3, e21, e32, r21, p, all_values)
    clamped = not (p_lo <= p <= p_hi)
    # These two guards only gate the case that would otherwise be certified
    # "conclusive": an order p already outside [p_lo, p_hi] is clamped and
    # marked not-conclusive by that mechanism regardless, so a ladder run
    # off the credible-order rails (e.g. a manufactured sub-0.5-order decay)
    # is not double-penalized here; the guards exist to catch the ladder
    # that looks clean -- monotone, p inside the window -- yet is still not
    # asymptotic, which is exactly what the order-window check alone misses.
    if not clamped and (not shrinking or not extrapolation_ok):
        # The conservative fallback band, matching the non-monotone
        # branch's convention: largest spread of the fit triple times 1.25.
        spread = max(f1, f2, f3) - min(f1, f2, f3)
        result.update({
            "observed_order": round(p, 3), "order_used": None,
            "clamped": False, "band_abs": 1.25 * spread, "monotone": True,
            "conclusive": False, "asymptotic": False,
            "richardson_extrapolated": phi0,
            "method": (GROWING_INCREMENT_NOTE if not shrinking
                      else DIVERGENT_EXTRAPOLATION_NOTE)})
        return result
    p_used = min(max(p, p_lo), p_hi)
    band = fs * abs(e21) / (r21 ** p_used - 1.0)
    # No method jargon on any surface this string can reach (doctrine: GCI
    # stays internal; the Eca and Hoekstra citation is the allowed name).
    method = (f"3-mesh study (r = {r21:.2f}), observed order p = {p:.2f}; "
              f"least-squares fit with safety factor {fs:g} "
              f"(Eca and Hoekstra 2014)")
    if clamped:
        method += f"; {ORDER_CLAMP_NOTE} (band uses p = {p_used:.1f})"
    result.update({
        "observed_order": round(p, 3), "order_used": round(p_used, 3),
        "clamped": clamped, "band_abs": band, "monotone": True,
        "conclusive": not clamped, "method": method,
        "asymptotic": True, "richardson_extrapolated": phi0})
    return result


def reportable_band(band: dict[str, Any] | None) -> float | None:
    """The band, but only when the ladder earned the right to state one.

    WHY THIS EXISTS. ``eca_hoekstra_band`` returns a ``band_abs`` whether or
    not it also sets ``conclusive``: on a failed ladder that number is a
    deliberately conservative fallback, not a measured uncertainty. Five acts
    independently read ``band_abs``, trusted it, and printed it on sealed
    certificates captioned "95% confidence interval". One of them was quoting
    15% of its own value; another was quoting a band that rounds to zero at
    its display precision.

    Five authors making the same mistake is a fact about the return shape, not
    about the authors. So the safe read gets its own name, and a caller that
    wants the fallback has to reach past this and say so.
    """
    if not band:
        return None
    if not band.get("conclusive"):
        return None
    return band.get("band_abs")


def not_conclusive_reason(band: dict[str, Any] | None) -> str | None:
    """Why this ladder cannot state a band, in one clause. None if it can.

    The ``method`` string is not usable for this: on a clamped ladder it ends
    "(band uses p = 0.5)", which contradicts an act that is declining to
    report a band at all.
    """
    if not band or band.get("conclusive"):
        return None
    if band.get("monotone") is False:
        return "the three rungs do not move one way under refinement"
    p = band.get("observed_order")
    if band.get("clamped") and p is not None:
        return (f"the observed order p = {p} falls outside the credible "
                f"range 0.5 to 2.5")
    note = band.get("asymptotic_note") or band.get("method") or ""
    if "increment" in note:
        return "successive increments grow with refinement"
    if "extrapolat" in note:
        return ("the value the ladder extrapolates to falls outside the range "
                "it measured")
    if p is not None:
        return (f"the observed order p = {p} falls outside the credible "
                f"range 0.5 to 2.5")
    return "the ladder is not in the asymptotic range"


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


TRANSFER_METHOD = ("estimated from the lab's validation history "
                   "(transferred; screening estimate)")


def transferred_model_band(value: float | None,
                           exclude: str | None = None) -> dict[str, Any] | None:
    """Model-form band transferred from the lab's own measured spread history.

    Doctrine fallback (UNCERTAINTY-DOCTRINE, model channel b): a body with no
    direct closure study borrows a conservative pool statistic from the
    stored studies that carry BOTH a measured model spread and the working
    value it was measured against. Each donor contributes its measured
    relative spread; the transferred statistic is mean + 1 sigma over the
    pool (never below the largest member), scaled by this mission's own
    value. Every number in the pool was measured; nothing is invented here.

    Returns None when the mission has no working value or the pool is empty —
    the caller must then leave the channel honestly unquantified.
    """
    if not value:
        return None
    pool: dict[str, float] = {}
    try:
        paths = sorted(STUDIES_DIR.glob("*.json"))
    except OSError:
        return None
    for path in paths:
        body = path.stem
        if exclude and body == exclude:
            continue
        study = load_study(body)
        if not study:
            continue
        model = study.get("model") or {}
        band = model.get("band_abs")
        working = (study.get("numerical") or {}).get("value_working")
        if band is None or not working:
            continue
        pool[body] = abs(float(band)) / abs(float(working))
    if not pool:
        return None
    rels = list(pool.values())
    mean = sum(rels) / len(rels)
    if len(rels) > 1:
        sigma = math.sqrt(sum((r - mean) ** 2 for r in rels) / (len(rels) - 1))
    else:
        sigma = 0.0
    rel = max(mean + sigma, max(rels))
    return {"band_abs": rel * abs(float(value)),
            "band_rel": round(rel, 5),
            "method": TRANSFER_METHOD,
            "members": {k: round(v, 5) for k, v in pool.items()},
            "screening_estimate": True,
            "transferred": True}


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
    "provenance": [...], "levels": [...]}. A fingerprint mismatch yields
    pending (Q4): the numerical channel must then say "study pending", never
    a stale band. ``levels`` carries the matching study's rung records so a
    channel note can state cell counts without reaching for study internals.
    """
    study = load_study(body)
    if not study:
        return {"numerical": None, "model": None, "pending": True,
                "provenance": [], "levels": []}
    match = study.get("fingerprint") == fingerprint
    numerical = study.get("numerical") if match else None
    # The model spread is tied to the same fingerprint discipline.
    model = study.get("model") if match else None
    return {
        "numerical": numerical,
        "model": model,
        "pending": not match,
        "provenance": study.get("provenance", []) if match else [],
        "levels": study.get("levels", []) if match else [],
    }
