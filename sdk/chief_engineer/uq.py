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

DIM_UNSTATED = (
    "refinement ladder refused: the dimensionality that sets the "
    "representative mesh size is unstated. Pass dim=2 or dim=3. Cell counts "
    "cannot reveal it, so it is an assumption on every fit, and the wrong one "
    "scales every observed order by exactly 1.5, which is enough to admit a "
    "ladder that should be rejected or reject one that should be admitted.")


def _require_dim(dim: int | None) -> int:
    """A ladder must state the dimensionality its representative size came from.

    The preflight, per VERIFICATION_CHARTER section 3: an unstated
    dimensionality is refused rather than defaulted. The old ``dim = 3``
    default was silent, so a two-dimensional case that forgot to say so was
    fitted with the cube root and had its observed order stretched by exactly
    1.5; the cylinder vortex-shedding ladder was declined on a p of 3.63 that
    is 2.42 when fitted on its own mesh. Refusing costs one keyword at every
    call site and removes the whole failure mode.
    """
    if dim is None:
        raise ValueError(DIM_UNSTATED)
    dim = int(dim)
    if dim not in (1, 2, 3):
        raise ValueError(f"dim must be 1, 2 or 3; got {dim}")
    return dim


# --------------------------------------------------------------------------
# Which guard held a verdict (Q1)
# --------------------------------------------------------------------------
#
# WHY THIS EXISTS. On 2026-07-30 the cylinder vortex-shedding ladder was
# declined for an observed order of 3.63, outside the credible window. Fitted
# on its own two-dimensional mesh that order is 2.42, inside it. The act is
# still declined -- its extrapolated Strouhal number overshoots the range it
# measured, and that guard does not depend on dimensionality at all -- so the
# verdict never moved and the stated reason was wrong for a day.
#
# ``not_conclusive_reason`` DERIVES a reason by reading the method string back.
# A derived reason is always current, which is exactly the problem: change the
# arithmetic and the sentence silently reassigns itself to whichever guard
# happens to be failing now, with nothing on the record to say the stated
# reason moved. So the fit records which guards it actually evaluated and how
# each came out, at the time it ran. A verdict that survives on a different
# guard than the one it stated then becomes a visible disagreement between two
# stored facts instead of an invisible substitution.
GUARD_DISTINCT_RUNGS = "distinct_rungs"
GUARD_MONOTONE = "monotone"
GUARD_ORDER_WINDOW = "order_window"
GUARD_INCREMENT_TREND = "increment_trend"
GUARD_EXTRAPOLATION = "extrapolation_sanity"
# The structural guard: the levels are not meshes at all, so no fit on them is
# a discretization band and nothing here may be read as one.
#
# WHY IT EXISTS. The aortic-valve study stored `conclusive: True` as a
# hardcoded literal, and it was the only stored study whose band reached a live
# surface: `reportable_band` returned 76.5 Pa for it and None for all eight
# genuine ladders. Its three "levels" are k = 3/5/9 segments of a half-sine
# ejection waveform evaluated in closed form on a reduced-order orifice model.
# No mesh, no solver, no fit, no guard. The number measures how finely a
# waveform was chopped, and it sat in the slot a grid-convergence band sits in.
# A record that cannot pass a guard must still be able to NAME the one that
# excludes it, otherwise the only way to decline it is to say nothing.
GUARD_NOT_A_DISCRETIZATION_LADDER = "not_a_discretization_ladder"

# Precedence: the order in which a failing guard is chosen as THE stated
# reason. Cheapest and most structural first, so the sentence names the
# earliest thing that is wrong with the ladder.
GUARD_PRECEDENCE = (GUARD_NOT_A_DISCRETIZATION_LADDER, GUARD_DISTINCT_RUNGS,
                    GUARD_MONOTONE, GUARD_ORDER_WINDOW,
                    GUARD_INCREMENT_TREND, GUARD_EXTRAPOLATION)


def _guard_record(guards: dict[str, bool]) -> dict[str, Any]:
    """The stored guard facts: what was evaluated, what failed, what is stated.

    ``guards`` carries ONLY the guards this fit actually evaluated. A guard
    that never ran is absent, not False: a non-monotone ladder never fits an
    order, so it has no opinion on the order window, and recording one would
    be inventing a fact.
    """
    failed = [name for name in GUARD_PRECEDENCE if guards.get(name) is False]
    return {"guards": dict(guards), "guards_failed": failed,
            "not_conclusive_guard": failed[0] if failed else None}


def guards_holding(band: dict[str, Any] | None) -> list[str]:
    """Every guard that independently holds this ladder back. [] if none do.

    More than one entry means the verdict does not rest on the stated reason
    alone: correcting the guard that is named would not move it.
    """
    if not band:
        return []
    return list(band.get("guards_failed") or [])


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

LADDER_ORDER_WINDOW = (0.5, 4.0)


def ladder_band(cells: Sequence[float], values: Sequence[float],
                *, dim: int | None = None) -> dict[str, Any]:
    """Observed order and discretization band from a 3-level ladder.

    ``cells`` are the mesh cell counts coarse-to-fine; ``values`` the solution
    functional on each mesh in the same order. Representative mesh size is
    h_i = (1/N_i)^(1/dim). With three meshes the least-squares fit of
    phi = phi0 + a h^p reduces to the classical observed-order solve; the band
    is the GCI on the fine mesh with Fs = 1.25 when the ladder is clean
    (monotone, 0.5 <= p <= 4), and the conservative fallback otherwise
    (Eça and Hoekstra 2014 practice).

    More than three rungs may be passed; the finest three distinct ones are
    fitted. Everything downstream of the fit -- the conservative fallback
    band and the asymptotic guards -- is then computed over THOSE THREE and
    no others, so handing this function a longer ladder cannot change the
    verdict or the width it reports for a fit it did not change.

    ``dim`` is required, not defaulted: see ``_require_dim``.
    """
    dim = _require_dim(dim)
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
                "dim": dim,
                "order_window": list(LADDER_ORDER_WINDOW),
                **_guard_record({GUARD_DISTINCT_RUNGS: False})}
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
        "h": [h1, h2, h3], "dim": dim,
        "order_window": list(LADDER_ORDER_WINDOW),
    }
    monotone = (e21 * e32) > 0.0
    if not monotone or e21 == 0.0:
        # Non-monotone (or flat) ladder: the honest sentence plus a
        # conservative band from the observed range, factor 3 (E&H fallback).
        # The range is the FIT TRIPLE's range, not every rung handed in; see
        # _fit_range below for why the two must be the same three rungs.
        spread = max(f1, f2, f3) - min(f1, f2, f3)
        result.update({
            "observed_order": None,
            "band_abs": 3.0 * spread if spread else 0.0,
            "monotone": monotone,
            "method": INCONCLUSIVE,
            "conclusive": False,
            # No order was fitted, so the order-window, increment-trend and
            # extrapolation guards were never evaluated and are absent rather
            # than recorded as passing.
            **_guard_record({GUARD_DISTINCT_RUNGS: True,
                             GUARD_MONOTONE: False}),
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
    #
    # EVERY GUARD IS EVALUATED, ALWAYS. The verdict below is unchanged -- a
    # ladder outside the order window is still declined on the order window
    # and is still not double-penalized -- but the guards that did not decide
    # it are now run and recorded anyway. Short-circuiting them left a record
    # that named one reason and said nothing about the others, which is how a
    # verdict can quietly change the guard it rests on while the sentence
    # stays put.
    in_window = LADDER_ORDER_WINDOW[0] <= p <= LADDER_ORDER_WINDOW[1]
    shrinking, extrapolation_ok, phi0 = _asymptotic_guard(
        f1, f2, f3, e21, e32, r21, p)
    asymptotic_note: str | None = None
    if in_window and (not shrinking or not extrapolation_ok):
        asymptotic_note = (LADDER_GROWING_INCREMENT_NOTE if not shrinking
                          else LADDER_DIVERGENT_EXTRAPOLATION_NOTE)
    clean = in_window and shrinking and extrapolation_ok
    if clean:
        gci = 1.25 * abs(e21) / (r21 ** p - 1.0)
        gci_middle = gci * r21 ** p
        method = (f"3-mesh ladder (r = {r21:.2f}), observed order "
                  f"p = {p:.2f}; GCI band, Fs = 1.25")
    else:
        # Same conservative fallback the non-monotone branch above already
        # uses (factor-3 on the fit triple's range): a guard failure never
        # gets its own, different band formula.
        gci = 3.0 * (max(f1, f2, f3) - min(f1, f2, f3))
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
        **_guard_record({GUARD_DISTINCT_RUNGS: True, GUARD_MONOTONE: True,
                         GUARD_ORDER_WINDOW: in_window,
                         GUARD_INCREMENT_TREND: shrinking,
                         GUARD_EXTRAPOLATION: extrapolation_ok}),
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
# measured range width of THE THREE RUNGS THE ORDER WAS FITTED FROM. The
# Richardson value must land within [lo - tol, hi + tol] or the fit is
# rejected as a divergence signal, not a limit.
#
# RECALIBRATED 2026-07-31, and the reason is the whole point of this
# constant's scope. The original calibration read its "good case" off a
# FOUR-rung call (816/3264/13056/52224) whose fit only ever used the last
# three of those rungs. The coarse 816 rung widened the range the guard
# measured against without ever entering the fit, so the same fit came back
# conclusive on four rungs and not-conclusive on three:
#   - 3264/13056/52224, handed as three rungs: Richardson 0.00287237 sits
#     21.16% of the range width (7.5269e-5) above the top of
#     [0.00278117, 0.00285644] -> DECLINED;
#   - the same three rungs handed with 816 in front: the same Richardson
#     value, now 8.48% of a 1.87747e-4 range width -> CERTIFIED at a band
#     of 1.99087e-5, 0.70% of the drag.
# A certifier must not answer two ways to one fit, so the guard now measures
# against the fit triple only, and the calibration is re-read on three-rung
# fixtures:
#   - TMR flat plate finest triple (13056/52224/208896 cells, 2026-07-31):
#     shrinking increments, Richardson 0.00286698 sits 11.58% of the range
#     width (2.93299e-5) above the top of [0.00283425, 0.00286358] -- the
#     one genuinely-converging ladder in this corpus, which must be
#     accepted;
#   - B-52 (193880/255358/330950 cells): Richardson 0.0648 sits 246.6% of
#     the range width (0.005079) above the top of [0.047196, 0.052275] -- a
#     ladder a human rejected as not asymptotic.
# 0.15 still clears the good case, but by 1.30x rather than the 1.77x the
# four-rung reading claimed, and it stays a factor of 16 below the bad
# case. The margin is thinner than advertised and that is a measured fact
# about this fixture, not a reason to move the constant: raising the
# tolerance to restore the old-looking margin would be tuning the gate to
# the answer. If a future ladder lands between 11.6% and 15% this number
# needs re-deriving from more than two fixtures, not nudging.
#
# SWEPT 2026-08-01, and the sweep found the thin case is not hypothetical.
# Every stored ladder in this tree was re-verdicted under both guard scopes,
# at every prefix call shape a caller could make: 15 call shapes over 12
# ladders (10 curriculum studies in models/curriculum/uq-studies, plus the
# TMR flat plate and bump). Two results, both worth having:
#
#   1. NO curriculum ladder's verdict was decided by the rung count. The
#      only curriculum record fitted from a >3-rung call is b52, and it is
#      declined either way -- though not by the same margin: 247.43% of the
#      fit triple's range against 93.96% of all six handed rungs, a 2.6x
#      difference in the stated excess on a record that is on the website.
#      So the mechanism is live on real data even where the verdict holds.
#   2. The recalibration above was read off Cd ONLY, and the same ladder's
#      SKIN FRICTION carries the identical flip that Cd does, unmentioned
#      until now. cf_097 at 3264/13056/52224, handed as three rungs:
#      Richardson 0.00271594 sits 27.28% above the top of its fit-triple
#      range -> DECLINED; the same three handed with 816 in front: 11.38%
#      -> would have been CERTIFIED under the old scope. Two functionals,
#      one ladder, one call shape, two flips.
#
# And the cf_097 finest triple (13056/52224/208896) sits at 13.67%, which is
# INSIDE the 11.6%-to-15% band this comment says needs re-deriving. It
# clears 0.15 by 1.10x, not the 1.30x measured on Cd. That is a second
# accepted fixture and it is thinner than the first, so the honest reading
# is that the good-case margin on this corpus is 1.10x. The constant is
# still not moved -- moving it now would be tuning the gate to the fixture
# that squeaked through -- but nobody should quote 1.30x as the margin.
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
                      ) -> tuple[bool, bool, float | None]:
    """Shared increment-trend and extrapolation-sanity guard math.

    Used by both eca_hoekstra_band and ladder_band so the two grid-
    convergence certifiers can never drift apart on what counts as
    "asymptotic" (commit e4b0ff1's fix, extended to ladder_band). Returns
    (shrinking, extrapolation_ok, richardson_extrapolated); each caller keeps
    its own conservative-fallback band formula and method text.

    THE RANGE IS THE FIT TRIPLE'S RANGE. ``f1, f2, f3`` are exactly the three
    rungs the observed order was solved from, and nothing else is allowed in.
    This used to take every distinct rung the caller passed, on the reasoning
    that a dropped coarse rung is still measured data; the effect was that the
    same fit came back conclusive or not conclusive depending on how many
    extra rungs the caller happened to hand over, because each one widened the
    range the tolerance is a fraction of (see EXTRAPOLATION_TOL_FRAC for the
    flat-plate pair that measured it). A verdict that changes with the call
    shape is not a measurement of the ladder.
    """
    shrinking = abs(e21) < abs(e32)
    phi0 = f3 + e21 / (r21 ** p - 1.0) if r21 ** p != 1.0 else None
    range_lo, range_hi = min(f1, f2, f3), max(f1, f2, f3)
    tol = EXTRAPOLATION_TOL_FRAC * (range_hi - range_lo)
    extrapolation_ok = (phi0 is not None
                       and (range_lo - tol) <= phi0 <= (range_hi + tol))
    return shrinking, extrapolation_ok, phi0


def eca_hoekstra_band(cells: Sequence[float], values: Sequence[float],
                      *, p_lo: float = 0.5, p_hi: float = 2.5,
                      fs: float = 1.25,
                      dim: int | None = None) -> dict[str, Any]:
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
      within EXTRAPOLATION_TOL_FRAC of the measured range OF THE FIT TRIPLE;
      an extrapolation outside the data it was fitted from is a divergence
      signal, not a limit (DIVERGENT_EXTRAPOLATION_NOTE).

    A ladder that fails either guard never has its band silently widened or
    narrowed by the fit that failed; the conservative fallback band stands.

    More than three rungs may be passed and the finest three distinct ones
    are fitted, but the guard tolerance and the fallback band are measured
    over those three alone. Extra rungs change which triple is fitted; they
    never change the verdict on a triple.

    ``dim`` is required, not defaulted: see ``_require_dim``.
    """
    dim = _require_dim(dim)
    distinct: list[tuple[float, float]] = []
    for c, v in zip(cells, values):
        if not distinct or float(c) != distinct[-1][0]:
            distinct.append((float(c), float(v)))
    if len(distinct) < 3:
        return {"cells": [c for c, _ in distinct],
                "values": [v for _, v in distinct],
                "observed_order": None, "order_used": None, "clamped": False,
                "band_abs": None, "monotone": None, "conclusive": False,
                "method": DEGENERATE, "dim": dim,
                "order_window": [p_lo, p_hi],
                **_guard_record({GUARD_DISTINCT_RUNGS: False})}
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
                              "dim": dim, "order_window": [p_lo, p_hi]}
    if (e21 * e32) <= 0.0:
        spread = max(f1, f2, f3) - min(f1, f2, f3)
        result.update({
            "observed_order": None, "order_used": None, "clamped": False,
            "band_abs": 1.25 * spread, "monotone": False, "conclusive": False,
            "method": NON_MONOTONE_NOTE,
            # No order was fitted, so the three guards downstream of the fit
            # were never evaluated; absent, not passing.
            **_guard_record({GUARD_DISTINCT_RUNGS: True,
                             GUARD_MONOTONE: False})})
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
    # divergence signal, not a limit. "The data it was fitted from" is the
    # three rungs of the fit and nothing else: folding in the coarser rungs
    # the order solve dropped only ever makes this guard MORE permissive,
    # which is exactly how the flat plate's 3264/13056/52224 fit came back
    # declined on a three-rung call and certified at 1.99087e-5 on a
    # four-rung one.
    shrinking, extrapolation_ok, phi0 = _asymptotic_guard(
        f1, f2, f3, e21, e32, r21, p)
    clamped = not (p_lo <= p <= p_hi)
    # WHICH GUARD HELD THIS VERDICT. All four post-fit guards are evaluated
    # on every fit and all four outcomes are recorded, whichever one the
    # verdict is stated on. The branch below is unchanged: an order p already
    # outside [p_lo, p_hi] is clamped and not-conclusive by that mechanism
    # regardless, so a ladder run off the credible-order rails is still not
    # double-penalized, and the increment-trend and extrapolation guards still
    # only DECIDE the case that would otherwise be certified. What changes is
    # that a clamped ladder no longer records `asymptotic: True` without
    # having asked, and a reader can see that the cylinder vortex ladder is
    # held by the extrapolation guard whether its order is fitted at 3.63 or
    # at 2.42 -- so correcting the order does not silently move the reason.
    guards = {GUARD_DISTINCT_RUNGS: True, GUARD_MONOTONE: True,
              GUARD_ORDER_WINDOW: not clamped,
              GUARD_INCREMENT_TREND: shrinking,
              GUARD_EXTRAPOLATION: extrapolation_ok}
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
                      else DIVERGENT_EXTRAPOLATION_NOTE),
            **_guard_record(guards)})
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
        # `asymptotic` is now what the guards actually said, not what the
        # branch assumed. A clamped ladder used to reach here and record
        # `asymptotic: True` having never run either guard; the cylinder
        # vortex ladder fitted at dim=3 did exactly that while its
        # extrapolated Strouhal number sat outside the range it measured.
        "asymptotic": bool(shrinking and extrapolation_ok),
        "richardson_extrapolated": phi0,
        **_guard_record(guards)})
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


def _spoken(x: float, places: int = 3) -> str:
    """A number for a camera surface, with a negative sign spelled out.

    A leading "-" is a dash on a surface that is read aloud, and the house rule
    keeps dashes off those. "minus 13.733" is also what a person says.
    """
    return (f"minus {abs(x):.{places}f}" if x < 0 else f"{x:.{places}f}")


def impossible_extrapolation(band: dict[str, Any] | None, *, quantity: str,
                             why: str, floor: float | None = None,
                             ceiling: float | None = None,
                             unit: str | None = None,
                             places: int = 3) -> str | None:
    """The clause for a ladder extrapolating outside what the quantity can be.

    WHY THIS EXISTS. ``extrapolation_sanity`` asks a statistical question: did
    the Richardson value land near the range the rungs measured? It cannot ask
    the physical one, because this module does not know what any functional
    means. The supersonic wedge ladder extrapolates its shock angle to
    minus 13.733 degrees. That is not a wide band or a soft convergence signal,
    it is a value no flow can produce, and it is a strictly stronger statement
    than "the observed order is outside the credible window" -- an order can be
    argued about, a negative shock angle cannot. So it leads the sentence
    (see ``not_conclusive_reason``), and the act that knows the physics is the
    one that supplies it.

    ``quantity`` names the functional ("the shock angle"). ``why`` is the
    clause that lands straight after the value and states the physics in the
    act's own words ("which is not a shock angle any flow can have"); it is a
    continuation, not a sentence, so the whole reason still reads as one
    sentence when other guards are named beside it. ``floor`` / ``ceiling``
    are the domain bounds. Returns None when the extrapolated value is inside
    the domain, when there is no extrapolated value, or when no bound was
    given: silence is the default, so a caller that knows nothing about its
    quantity's domain says nothing about it.
    """
    if not band:
        return None
    phi0 = band.get("richardson_extrapolated")
    if phi0 is None:
        return None
    phi0 = float(phi0)
    if not ((floor is not None and phi0 < float(floor))
            or (ceiling is not None and phi0 > float(ceiling))):
        return None
    unit_txt = f" {unit}" if unit else ""
    return (f"{quantity} the ladder extrapolates to is "
            f"{_spoken(phi0, places)}{unit_txt}, {why}")


# How many guards hold a ladder, said in words rather than digits.
_COUNT_WORD = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def _join_clauses(clauses: Sequence[str]) -> str:
    """Join reason clauses so the sentence reads as one sentence."""
    if len(clauses) == 1:
        return clauses[0]
    return ", ".join(clauses[:-1]) + ", and " + clauses[-1]


def guards_holding_note(band: dict[str, Any] | None) -> str | None:
    """One sentence when more than one guard independently holds a ladder.

    None when a single guard holds it, which is the case the stated reason
    already covers completely.
    """
    failed = guards_holding(band)
    if len(failed) < 2:
        return None
    word = _COUNT_WORD.get(len(failed), str(len(failed)))
    each = ("either one" if len(failed) == 2 else "any one of them")
    return (f"{word.capitalize()} guards hold this ladder back independently, "
            f"so correcting {each} alone would not move the verdict")


def guard_clause(guard: str, band: dict[str, Any] | None = None) -> str:
    """The one clause that names a guard, on camera."""
    band = band or {}
    if guard == GUARD_NOT_A_DISCRETIZATION_LADDER:
        return ("the levels are not meshes, so this is not a discretization "
                "band")
    if guard == GUARD_DISTINCT_RUNGS:
        return "the refinement knob did not give three different meshes"
    if guard == GUARD_MONOTONE:
        return "the three rungs do not move one way under refinement"
    if guard == GUARD_ORDER_WINDOW:
        lo, hi = (band.get("order_window") or (0.5, 2.5))
        p = band.get("observed_order")
        return (f"the observed order p = {p} falls outside the credible "
                f"range {lo:g} to {hi:g}")
    if guard == GUARD_INCREMENT_TREND:
        return "successive increments grow with refinement"
    if guard == GUARD_EXTRAPOLATION:
        return ("the value the ladder extrapolates to falls outside the range "
                "it measured")
    return "the ladder is not in the asymptotic range"


def not_conclusive_reason(band: dict[str, Any] | None, *,
                          impossible: str | None = None) -> str | None:
    """Why this ladder cannot state a band. None if it can.

    The ``method`` string is not usable for this: on a clamped ladder it ends
    "(band uses p = 0.5)", which contradicts an act that is declining to
    report a band at all.

    THE GUARDS THE FIT RECORDED WIN, AND ALL OF THEM ARE NAMED. When the band
    carries a guard record the clause names the guards that guard record says
    failed, because those are the guards that held the verdict at the time the
    fit ran. Re-deriving the reason from the stored numbers looks equivalent
    and is not: it silently reassigns the sentence whenever the arithmetic
    moves underneath it, which is exactly how the cylinder vortex-shedding
    ladder spent a day declined for an order outside the window when the guard
    actually holding it was the extrapolation check.

    NAMING ONLY THE FIRST ONE WAS ITS OWN DEFECT. This used to return
    ``not_conclusive_guard`` alone, which is the earliest failure in
    ``GUARD_PRECEDENCE`` and not necessarily the decisive one. The supersonic
    wedge act said its ladder failed on an observed order of 0.035, so a
    reader would reasonably conclude a better order would settle it; the same
    ladder also fails ``extrapolation_sanity``, at a shock angle of
    minus 13.733 degrees, and no order would have rescued that. A sentence
    that states one true unimportant reason in place of a true decisive one is
    worse than a sentence that states both. Six ladders in this corpus fail
    more than one guard.

    ``impossible`` is the clause from :func:`impossible_extrapolation`, when
    the caller knows its quantity's physical domain. It LEADS the sentence and
    it replaces the generic extrapolation clause, because "this value cannot
    exist" outranks every other guard here: an order outside a window is a
    judgement about a fit, an impossible extrapolated value is a fact about the
    world. :func:`guards_holding_note` is the companion sentence that says the
    verdict does not rest on any one of these alone.

    The derivation below stays only for records written before the guard record
    existed, and for those it is a best effort, not a fact.
    """
    if not band or band.get("conclusive"):
        return None
    failed = guards_holding(band)
    if failed:
        clauses = [impossible] if impossible else []
        clauses += [guard_clause(g, band) for g in failed
                    if not (impossible and g == GUARD_EXTRAPOLATION)]
        return _join_clauses(clauses)
    guard = band.get("not_conclusive_guard")
    if guard:
        return _join_clauses(([impossible] if impossible else [])
                             + [guard_clause(guard, band)])

    def _legacy() -> str:
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
            return ("the value the ladder extrapolates to falls outside the "
                    "range it measured")
        if p is not None:
            return (f"the observed order p = {p} falls outside the credible "
                    f"range 0.5 to 2.5")
        return "the ladder is not in the asymptotic range"

    if impossible:
        return _join_clauses([impossible, _legacy()])
    return _legacy()


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

    EVERY BUDGET NAMES ITS LARGEST TERM, and this returns it rather than
    leaving each caller to eyeball the map. Multifidelity fusion cut the race
    estimator's standard error by a factor of 33, from 0.02832 to 0.00086 L/D,
    and the budget that came out of it showed the estimator was by then not the
    largest contributor by two orders of magnitude. Any further work on the
    estimator would have been effort spent on the term that had already stopped
    mattering, and a budget that does not rank its own terms invites exactly
    that. `largest` is None when nothing is quantified.

    A MISSING TERM IS NOT A SMALL TERM. `largest` ranks only what was measured,
    so it is reported next to `missing` and never instead of it: a budget whose
    largest quantified term is 0.0017 and whose model-form term was never
    measured has not established that 0.0017 is its largest term at all. The
    share is a share of the total that was computed, which is a total over the
    quantified channels alone.
    """
    parts = {
        "input": input_2sigma, "numerical": numerical_abs, "model": model_abs,
    }
    quantified = {k: float(v) for k, v in parts.items() if v is not None}
    combined = math.sqrt(sum(v * v for v in quantified.values())) if quantified else None
    largest = None
    if quantified:
        term = max(quantified, key=lambda k: abs(quantified[k]))
        largest = {"term": term, "value": quantified[term],
                   "share_of_quantified_total": (
                       round(abs(quantified[term]) / combined, 5)
                       if combined else None),
                   "ranks_only_what_was_measured": True}
    return {"combined_95": combined, "contributions": quantified,
            "missing": [k for k, v in parts.items() if v is None],
            "largest": largest}


# --------------------------------------------------------------------------
# Study records (Q1/Q4)
# --------------------------------------------------------------------------

# Keys a stored study's `numerical` block deliberately does NOT carry from
# the fit, and why. Every other key the fit produces is copied wholesale.
#
# WHY A NAMED LIST. Every study writer used to build `numerical` from a
# hand-typed list of keys. A hand-typed list drops whatever the fit learns to
# say next, silently, and a record that omits what it was not told to keep
# looks complete -- which is worse than one that never had the field. When
# `ladder_band` and `eca_hoekstra_band` began recording the dimensionality
# their band was fitted with, not one stored study picked it up, because both
# writers were copying a list written before the field existed. So the writers
# now copy the fit and this constant names the exclusions out loud; a new key
# arrives in every study by default, and leaving one out is a decision
# somebody has to write down here.
STUDY_NUMERICAL_DROPS = {
    # The rungs themselves live in the study's `levels` block, which carries
    # cell counts, functionals, wall times and mission ids per rung. Copying
    # them into `numerical` too would give one record two versions of the
    # same three numbers with nothing deciding which is authoritative.
    "cells": "carried per rung in the study's levels block",
    "values": "carried per rung in the study's levels block",
    "h": "derivable from cells and dim; not a measurement",
}


def study_numerical(band: dict[str, Any], **extra: Any) -> dict[str, Any]:
    """The `numerical` block of a stored study: the fit, wholesale, plus extra.

    ``extra`` carries what the fit cannot know -- the working value the band is
    relative to, a band_rel, a method suffix a runner appends. It is applied
    last, so a runner may override a fit key deliberately and visibly.
    """
    numerical = {k: v for k, v in band.items() if k not in STUDY_NUMERICAL_DROPS}
    numerical["dropped_from_fit"] = sorted(
        k for k in STUDY_NUMERICAL_DROPS if k in band)
    numerical.update(extra)
    return numerical


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
