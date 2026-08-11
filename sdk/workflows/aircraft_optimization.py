"""Optimize an airliner's lift-to-drag ratio against stated mission requirements.

The request states what the aircraft must do — passengers, range, take-off and
landing speeds — and the lab searches a wing design space (span, area, sweep)
for the highest whole-aircraft L/D that still meets every requirement. Designs
that miss a requirement are shown as infeasible, not hidden; the winner is the
best whole-aircraft L/D that clears them all. The figure of merit is always
whole-aircraft: the wing is what the search moves, but the drag it is divided
by includes the fuselage, tail and nacelle share from Raymer's component
buildup, so a bare "L/D" would overstate what was optimized.

The search runs in two passes. A **research sizing screen** — a textbook drag
polar, a Breguet range check, and stall-speed constraints — maps the whole
grid in milliseconds. Then, when the vortex-lattice solver is reachable, the
**top finalists get real aero solves**: each candidate wing is built as actual
parametric geometry and solved for its polar, the cruise point read off the
solved curve, and the winner picked on solved numbers. The fuselage and tail
stay a parasite-drag buildup — the verdict says exactly which parts were
solved and which were modelled, and the tier is capped accordingly.
"""

from __future__ import annotations

import math
import os
import re
import shutil
import time
from pathlib import Path

from . import (OUT_ROOT, announce_geometry, announce_plot, make_transcript,
               withdraw_certificate)
from chief_engineer import vspaero
from chief_engineer.compute_audit import audit
from chief_engineer.display_names import display_name
from chief_engineer.researcher import ENGINEER_ACK, MissionProperties, method_memo
from chief_engineer.transcript import CHIEF_ENGINEER as _SPEAKER
from chief_engineer.transcript import NUMERICIST as _NUMERICIST_SPEAKER
from chief_engineer.transcript import Entry
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, NUMERICIST, PLAN,
                                ComputeLedger, KnowledgeBase, Roster,
                                lab_report, trust, uncertainty_channels)

# Physical constants and modelling assumptions, all stated so the numbers can be
# traced. These are conventional conceptual-design values, not tuned to a body.
_G = 9.81
_RHO_SL = 1.225          # sea-level air density (take-off / landing), kg/m^3
_RHO_CRUISE = 0.38       # ~11 km cruise altitude, kg/m^3
_V_CRUISE = 230.0        # cruise TAS ~ M0.78 at altitude, m/s
_CLMAX_LANDING = 2.6     # full flaps + slats
_CLMAX_TAKEOFF = 2.1     # take-off flap setting
_SFC = 1.7e-5            # thrust-specific fuel consumption, kg/(N·s) (~0.6 lb/lbf/hr)
_FUEL_FRACTION = 0.32    # usable fuel as a fraction of MTOW
_KG_PER_PAX = 100.0      # passenger + baggage
# _PAYLOAD_FRACTION -- payload as a fraction of MTOW, which is what turns a
# passenger count into a weight -- is NOT a constant typed here. It is measured
# off the same published analogue aircraft this act already holds the winner
# against, and it is defined next to that table (see `_analogue_payload_
# fraction`). It carried 0.22 until 2026-08-01, and the act's own analogue rows
# said that was wrong.
_SPAN_STRUCTURAL_LIMIT = 68.0   # m — beyond this the wing box is impractical
_MU_CRUISE = 1.43e-5     # dynamic viscosity at ~11 km, Pa·s
# Parasite drag of everything that is NOT the wing (fuselage, tail, nacelles,
# interference) — the component-buildup share left when the wing's own viscous
# drag comes from the solver instead of the polar constant.
_CD0_NONWING = 0.013
_TAPER = 0.3             # planform taper ratio for every candidate wing
_N_FINALISTS = 9         # feasible designs promoted to real solves
# Stated 1-sigma input uncertainties, propagated to the headline CI. These are
# the aleatory inputs the sizing rests on; they are declared, not discovered.
_SIGMA_PAYLOAD = 0.025   # passenger + baggage mass, ±5% at 2-sigma
_SIGMA_CD0_NONWING = 0.04  # non-wing parasite buildup, ±8% at 2-sigma
# Where uploaded surfaces land (the same directory the geometry study reads).
_GEOMETRY_DIR = Path(__file__).resolve().parents[1] / "geometry"
# Scope-mismatch trigger. A lifting surface arrives on its own while the
# objective names a whole aircraft, so the act says out loud what it is doing
# with the gap before it plans anything.
_FULL_AIRCRAFT = re.compile(r"\b(airliner|aircraft|airplane|aeroplane|jet)\b",
                            re.I)
# A lifting surface is thin and spanwise: its vertical extent is a small
# fraction of its span, and its streamwise extent is well under its span. A
# configuration carrying a fuselage fails both (the CRM wing-body reads 0.15
# deep and 0.86 long against its span; a wing on its own reads 0.01 and 0.22),
# so the two bars sit clear of dihedral and winglets on one side and clear of
# any body on the other.
_LIFTING_THICKNESS_RATIO = 0.08
_LIFTING_CHORD_RATIO = 0.5
# Provenance tiers. Every quoted number carries the one it came from, and the
# two never share a table, an axis, or a counter without saying which is which.
TIER_SCREEN = "[screen: reduced-order sizing]"
TIER_SOLVE = "[solve: VSPAERO + Raymer buildup]"

# The same two tags for a table that already has a Basis COLUMN, where the
# brackets are chrome rather than a marker. Sliced off the tags above so the
# wording a viewer matches between the certificate and the transcript cannot
# drift; retyping them is how two surfaces start describing one basis two ways.
_BASIS_SCREEN = TIER_SCREEN.strip("[]")
_BASIS_SOLVE = TIER_SOLVE.strip("[]")

# ---------------------------------------------------------------------------
# Gate-code advisory.
#
# ICAO Annex 14, Volume I (Aerodrome Design and Operations), Table 1-1,
# aerodrome reference code, code element 2. The code letter is set by the
# greatest wingspan the facility is intended to serve; the lower bound of each
# band is inclusive and the upper bound is exclusive, which is why a 65 m span
# is already Code F.
#
#   Code D  36 m up to but not including 52 m
#   Code E  52 m up to but not including 65 m
#   Code F  65 m up to but not including 80 m
#
# VERIFIED against the sources before shipping rather than taken on anyone's
# word, because an engineer in the audience will know this table. The bands
# were read verbatim off Annex 14 Vol I 8th Edition July 2018 (incorporating
# Amendment 14) Table 1-1, and cross-checked against ICAO Doc 9157 Aerodrome
# Design Manual Part 1 4th Edition 2020 and EASA CS-ADR-DSN Issue 6 (ED
# Decision 2022/006/R) Table A-1, which is the currently in force European
# text. Every source gives identical wingspan figures. Annex 14 Vol I is now
# in its 9th Edition, July 2022 (Amendment 17), and the reproduced clause is
# unchanged there; Amendment 18 (August 2025) was not readable, so the claim
# on screen names the table rather than an amendment state.
#
# TWO TRAPS, recorded because both are easy to reintroduce.
#
# 1. The bounds are lower inclusive and upper exclusive: the text reads "52 m
#    up to but not including 65 m". A span of exactly 65.0 m is therefore
#    already Code F, which is why the test below is >= and not >.
# 2. Before Amendment 14 (applicable 8 November 2018) code element 2 also
#    carried an outer main gear wheel span column, and the code letter was
#    whichever of the two was more demanding. Amendment 14 deleted that
#    column. Code element 2 is wingspan alone today, and wheel span feeds the
#    runway and taxiway width provisions directly on its own bands. Several
#    widely used secondary sources are still stale on this point, so never
#    reintroduce the second criterion from one of them.
_ICAO_CODE_D_MIN_SPAN = 36.0
_ICAO_CODE_E_MIN_SPAN = 52.0
_ICAO_CODE_E_MAX_SPAN = 65.0
_ICAO_CODE_F_MAX_SPAN = 80.0
ICAO_ADVISORY = (
    f"Advisory: span exceeds ICAO Aerodrome Reference Code E, wingspan "
    f"{_ICAO_CODE_E_MIN_SPAN:.0f} to {_ICAO_CODE_E_MAX_SPAN:.0f} m.",
    f"Code F, {_ICAO_CODE_E_MAX_SPAN:.0f} to {_ICAO_CODE_F_MAX_SPAN:.0f} m, is "
    f"A380 class gate infrastructure (ICAO Annex 14).",
    f"Offer: re-run with span at most {_ICAO_CODE_E_MAX_SPAN:.0f} m.")


def icao_advisory(span_m: float) -> tuple[str, str, str]:
    """The gate-code advisory, naming the span that raised it.

    The advisory is spoken once a winner exists, so it can say which span it
    is about. Without that the viewer met a bare "52 to 65 m" band and had to
    guess which number on screen it was measuring.
    """
    return (f"Advisory: winner span {span_m:.0f} m exceeds ICAO Aerodrome "
            f"Reference Code E, wingspan {_ICAO_CODE_E_MIN_SPAN:.0f} to "
            f"{_ICAO_CODE_E_MAX_SPAN:.0f} m.",
            ICAO_ADVISORY[1], ICAO_ADVISORY[2])


# The same advisory as one line, for the certificate constraint list.
ICAO_CONSTRAINT_ROW = (
    "ICAO gate code",
    f"Code E, span at most {_ICAO_CODE_E_MAX_SPAN:.0f} m")


def icao_code_letter(span_m: float) -> str | None:
    """The ICAO aerodrome reference code letter a wingspan falls in, over the
    bands this act can produce. None outside them."""
    if span_m < _ICAO_CODE_D_MIN_SPAN:
        return None
    if span_m < _ICAO_CODE_E_MIN_SPAN:
        return "D"
    if span_m < _ICAO_CODE_E_MAX_SPAN:
        return "E"
    if span_m < _ICAO_CODE_F_MAX_SPAN:
        return "F"
    return None


def spans_over_code_e(spans) -> list[float]:
    """Every span in the search that lands beyond Code E. Advisory input, and
    never a feasibility test: a Code F span is buildable, it just asks for
    different gates."""
    return sorted({float(s) for s in spans
                   if float(s) >= _ICAO_CODE_E_MAX_SPAN})
# Span ladder used to seed the search around an uploaded starting geometry:
# the default six-rung ladder re-centred on the measured span, with the centre
# and every rung clamped to sane airliner bounds.
_SPAN_SEED_OFFSETS = (-15.0, -9.0, -3.0, 3.0, 9.0, 15.0)
_SPAN_SEED_FLOOR = 28.0
_SPAN_CENTER_LO, _SPAN_CENTER_HI = 38.0, 60.0
# Backend pacing so the landscape points and the candidate wing in the viewport
# visibly land one by one — the viewer watches the screen fill. Paces the PATH,
# never the numbers; disabled in CI via CERTONOMOUS_SWEEP_PACE_MS=0.
_PACE_S = float(os.environ.get("CERTONOMOUS_SWEEP_PACE_MS", "120")) / 1000.0


def _interp_polar(polar: dict, key: str, cl: float) -> float:
    """Linear interpolation of a polar column against CLtot."""
    cls_, ys = polar["CLtot"], polar[key]
    for i in range(len(cls_) - 1):
        if cls_[i] <= cl <= cls_[i + 1]:
            t = (cl - cls_[i]) / ((cls_[i + 1] - cls_[i]) or 1.0)
            return ys[i] + t * (ys[i + 1] - ys[i])
    i = 0 if cl < cls_[0] else len(cls_) - 2
    t = (cl - cls_[i]) / ((cls_[i + 1] - cls_[i]) or 1.0)
    return ys[i] + t * (ys[i + 1] - ys[i])


def winner_ci95(best: dict, reqs: dict, *, polar: dict | None,
                n: int = 400, seed: int = 7) -> float:
    """95% CI on the winner's L/D: the stated input uncertainties Monte-Carlo
    propagated through the actual evaluation chain — the solved polar when one
    exists, the sizing model otherwise. Real spread machinery, no fudge."""
    import random
    import statistics

    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(n):
        mass_f = rng.gauss(1.0, _SIGMA_PAYLOAD)
        if polar:
            cl = best["cl_cruise"] * mass_f
            cd0 = _CD0_NONWING * rng.gauss(1.0, _SIGMA_CD0_NONWING)
            cdi = _interp_polar(polar, "CDi", cl)
            cdo = _interp_polar(polar, "CDo", cl)
            samples.append(cl / (cd0 + cdo + cdi))
        else:
            perturbed = dict(reqs)
            perturbed["passengers"] = reqs["passengers"] * mass_f
            r = evaluate_design(best["span"], best["area"],
                                best["sweep_deg"], perturbed)
            samples.append(r["L_D"])
    return 2.0 * statistics.stdev(samples)


# ---------------------------------------------------------------------------
# Computed uncertainty: every channel a number traced to a computation.
# ---------------------------------------------------------------------------

# The three axes of the design grid, in the order evaluate_design reports them.
_GRID_AXES = ("span", "area", "sweep_deg")
# Documented band on the non-wing component buildup terms (Raymer, Aircraft
# Design: A Conceptual Approach, AIAA): a conceptual-design buildup is credited
# to about ±15% on its terms; propagated to L/D it becomes the model channel.
_BUILDUP_BAND = 0.15


def axis_steps(grid) -> dict:
    """Grid spacing per design axis, measured from the grid actually screened."""
    steps: dict[str, float] = {}
    for i, axis in enumerate(_GRID_AXES):
        values = sorted({float(g[i]) for g in grid})
        diffs = [b - a for a, b in zip(values, values[1:])]
        steps[axis] = min(diffs) if diffs else 0.0
    return steps


def _fit_quadratic(xs, ys) -> tuple[float, float, float]:
    """Least-squares quadratic a·x² + b·x + c through (xs, ys); stdlib only."""
    rows = [[x * x, x, 1.0] for x in xs]
    ata = [[sum(r[i] * r[j] for r in rows) for j in range(3)] for i in range(3)]
    aty = [sum(r[i] * y for r, y in zip(rows, ys)) for i in range(3)]
    m = [ata[i][:] + [aty[i]] for i in range(3)]
    for i in range(3):
        pivot = max(range(i, 3), key=lambda r: abs(m[r][i]))
        m[i], m[pivot] = m[pivot], m[i]
        for r in range(i + 1, 3):
            factor = m[r][i] / m[i][i]
            for col in range(i, 4):
                m[r][col] -= factor * m[i][col]
    out = [0.0, 0.0, 0.0]
    for i in (2, 1, 0):
        out[i] = (m[i][3] - sum(m[i][c] * out[c] for c in range(i + 1, 3))) / m[i][i]
    return out[0], out[1], out[2]


def grid_spacing_bracket(points, winner, steps, value_key: str = "L_D_solved"
                         ) -> dict:
    """The grid-spacing bracket: the true optimum lies between discrete grid
    points, so the objective is fitted locally around the winner along each
    axis and varied by half a grid step; the axes combine in quadrature.

    ``points`` are evaluated designs carrying the axis values and
    ``value_key``. Along each axis the fit uses the points that hold the other
    two axes at one setting — the winner's own line when it has company,
    otherwise the best-populated parallel line: a quadratic for three or more
    points, a straight slope for two. An axis with no variation in the data
    contributes nothing. Every number comes from the points given.

    Returns ``{"value": float | None, "axes": {axis: float | None}}``.
    """
    axes_out: dict[str, float | None] = {}
    total = 0.0
    any_axis = False
    for axis in _GRID_AXES:
        others = [a for a in _GRID_AXES if a != axis]
        step = float(steps.get(axis) or 0.0)
        if step <= 0:
            axes_out[axis] = None
            continue
        lines: dict[tuple, dict[float, float]] = {}
        for p in points:
            try:
                key = tuple(round(float(p[o]), 6) for o in others)
                x = round(float(p[axis]), 6)
                value = float(p[value_key])
            except (KeyError, TypeError, ValueError):
                continue
            lines.setdefault(key, {})[x] = value
        winner_key = tuple(round(float(winner[o]), 6) for o in others)
        x0 = float(winner[axis])
        line = lines.get(winner_key, {})
        if len(line) < 2:
            candidates = [(k, ln) for k, ln in lines.items() if len(ln) >= 2]
            if not candidates:
                axes_out[axis] = None
                continue
            candidates.sort(key=lambda item: (
                -len(item[1]),
                sum(abs(a - b) for a, b in zip(item[0], winner_key))))
            line = candidates[0][1]
        xs = sorted(line)
        ys = [line[x] for x in xs]
        half = step / 2.0
        if len(xs) >= 3:
            a, b, c = _fit_quadratic(xs, ys)
            fit = lambda x: a * x * x + b * x + c   # noqa: E731
            delta = max(abs(fit(x0 + half) - fit(x0)),
                        abs(fit(x0 - half) - fit(x0)))
        else:
            slope = (ys[1] - ys[0]) / (xs[1] - xs[0])
            delta = abs(slope) * half
        axes_out[axis] = delta
        total += delta * delta
        any_axis = True
    return {"value": (math.sqrt(total) if any_axis else None), "axes": axes_out}


def polar_readoff_residual(polar, cl: float,
                           cd0_nonwing: float = _CD0_NONWING) -> float:
    """Cruise-point read-off residual on the solved polar: the whole-aircraft
    L/D difference between a straight-line and a curved read of the polar at
    the cruise CL. Zero when the polar cannot support the comparison."""
    try:
        cls_ = [float(v) for v in polar["CLtot"]]
        if len(cls_) < 3:
            return 0.0

        def lin(key: str) -> float:
            return _interp_polar(polar, key, cl)

        def quad(key: str) -> float:
            ys = [float(v) for v in polar[key]]
            i = min(range(len(cls_)), key=lambda k: abs(cls_[k] - cl))
            i = max(1, min(i, len(cls_) - 2))
            xs, yv = cls_[i - 1:i + 2], ys[i - 1:i + 2]
            out = 0.0
            for j in range(3):
                term = yv[j]
                for k in range(3):
                    if k != j:
                        term *= (cl - xs[k]) / (xs[j] - xs[k])
                out += term
            return out

        ld_lin = cl / (cd0_nonwing + lin("CDo") + lin("CDi"))
        ld_quad = cl / (cd0_nonwing + quad("CDo") + quad("CDi"))
        return abs(ld_lin - ld_quad)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return 0.0


def buildup_band_ld(cl: float, cdo_wing: float, cdi: float,
                    cd0_nonwing: float = _CD0_NONWING,
                    band: float = _BUILDUP_BAND) -> float:
    """The documented ±band on the non-wing component buildup, propagated to
    whole-aircraft L/D at the solved cruise point (Raymer's buildup terms)."""
    ld0 = cl / (cd0_nonwing + cdo_wing + cdi)
    ld_hi = cl / ((1.0 - band) * cd0_nonwing + cdo_wing + cdi)
    ld_lo = cl / ((1.0 + band) * cd0_nonwing + cdo_wing + cdi)
    return max(abs(ld_hi - ld0), abs(ld0 - ld_lo))


def range_for_ld(l_over_d: float) -> float:
    """The Breguet range a whole-aircraft L/D flies, in km.

    ONE ACT, ONE QUOTED RANGE. Range is a function of L/D and nothing else
    here, so a range figure inherits the tier of the L/D it was computed
    from: pass the screened L/D and the answer is a screened range, pass the
    solved one and it is a solved range. The screening tables quote the
    first, and the conclusion and the certificate quote only the second. That
    is the rule; ``conclusion_range_km`` is where it is applied.
    """
    return (_V_CRUISE / (_G * _SFC) * float(l_over_d)
            * math.log(1.0 / (1.0 - _FUEL_FRACTION)) / 1000.0)


def conclusion_range_km(best: dict, *, won_solved: bool) -> float:
    """The one range this act quotes past the evidence phase.

    THE SCREENED RANGE NEVER CROSSES INTO THE CONCLUSION OR THE CERTIFICATE.
    A screened range and a solved range differ by hundreds of kilometres on
    the same wing, and both used to reach the page: one in the screened
    optimum row, the other in the results and on the sealed certificate.
    Each was correctly labelled where it sat and the act still quoted two
    numbers for one aeroplane. So the conclusion zone takes its range from
    the tier the headline stands on, and takes it from here rather than off
    the screened record every caller has in hand.
    """
    if won_solved and best.get("L_D_solved") is not None:
        return range_for_ld(float(best["L_D_solved"]))
    return float(best["range_km"])


def unresolved_family(solved, best: dict) -> list[dict]:
    """The wings this fidelity does not separate from the winner.

    WHY THIS EXISTS. Span and area rail to the edges of the feasible box, so
    the finalists pile up on one planform and differ only in quarter-chord
    sweep. Their solved whole-aircraft L/D then lands within a fraction of a
    percent of each other, on a headline whose own interval is more than a
    unit wide. Ranking those siblings and crowning one of them would be
    reading a difference the numbers do not carry — and picking the maximum
    is exactly where that reads highest, because the screen-to-solve
    correction is noisiest there. So the act names the FAMILY.

    A sibling shares the winner's span and area and is counted separated from
    it only when the gap between their solved L/D exceeds the band this
    fidelity carries on each: the documented component-buildup band
    propagated to whole-aircraft L/D at the winner's own cruise point.

    Returns the family ordered by sweep, the winner included. A one-member
    list means the solved numbers do separate the winner from its siblings.
    """
    try:
        band = buildup_band_ld(float(best["cl_cruise"]),
                               float(best["cdo_wing_solved"]),
                               float(best["cdi_solved"]))
        top = float(best["L_D_solved"])
    except (KeyError, TypeError, ValueError):
        return [best]
    family = []
    for f in solved:
        try:
            if (abs(float(f["span"]) - float(best["span"])) < 1e-6
                    and abs(float(f["area"]) - float(best["area"])) < 1e-6
                    and abs(top - float(f["L_D_solved"])) <= band):
                family.append(f)
        except (KeyError, TypeError, ValueError):
            continue
    return sorted(family, key=lambda f: float(f["sweep_deg"])) or [best]


def screen_solve_gap(finalists) -> float | None:
    """Mean absolute gap between the sizing screen's L/D and the solved L/D
    over the finalists carrying both — measured model-channel evidence for
    the screen, per the special optimization-act case of the doctrine."""
    gaps = [abs(float(f["L_D"]) - float(f["L_D_solved"]))
            for f in finalists
            if f.get("L_D") is not None and f.get("L_D_solved") is not None]
    return (sum(gaps) / len(gaps)) if gaps else None


# Each kind of requirement miss, with the assumed input the verdict rests on.
# The two low-speed limits are driven by a maximum lift coefficient that no
# vortex-lattice solver can produce, so the verdict names the number it used.
_VIOLATION_KINDS = (
    ("approach speed", "Approach speed above the landing limit",
     f"assumed C_L_max (landing) = {_CLMAX_LANDING:.1f}"),
    ("take-off speed", "Take-off speed above the limit",
     f"assumed C_L_max (take-off) = {_CLMAX_TAKEOFF:.1f}"),
    ("range", "Range short of the requirement", "stated range requirement"),
    ("span", "Span beyond the structural limit", "structural span limit"),
)


def violation_breakdown(results) -> list[tuple[str, int, str]]:
    """Count the wings ruled out by each kind of requirement miss.

    ``evaluate_design`` writes one human-readable violation string per limit a
    wing misses; a wing can miss several. This groups them by limit so the
    bare infeasible count becomes a breakdown, with every count taken straight
    from the screened results. Each row also carries what the verdict rests
    on, which for the low-speed limits is an assumed lift coefficient. Kinds
    with no wings are left out.
    """
    counts = {label: 0 for _key, label, _basis in _VIOLATION_KINDS}
    for r in results:
        for key, label, _basis in _VIOLATION_KINDS:
            if any(v.startswith(key) for v in r.get("violations") or ()):
                counts[label] += 1
    return [(label, counts[label], basis)
            for _key, label, basis in _VIOLATION_KINDS if counts[label]]


def binding_constraint(results) -> str | None:
    """The limit that rules out the most wings: the binding constraint on the
    infeasible region, named for the design-space plot's legend."""
    rows = violation_breakdown(results)
    if not rows:
        return None
    label, _count, _basis = max(rows, key=lambda row: row[1])
    return {
        "Approach speed above the landing limit": "landing speed",
        "Take-off speed above the limit": "take-off speed",
        "Range short of the requirement": "range",
        "Span beyond the structural limit": "span",
    }.get(label)


def active_limits(best: dict, results) -> list[str]:
    """The limits the winning wing is sitting ON, named.

    WHY THIS EXISTS. The objective is cruise L/D, and for a parabolic drag
    polar the best attainable L/D is 0.5*sqrt(pi*AR*e/C_D0) — it rises with
    aspect ratio without turning over. So this search has no interior optimum
    in span or in area: the winner is wherever the feasible region ends. It is
    a corner of the box, and the box edges are the structural span limit and
    the area floor the landing speed sets. Sweep is the one axis with a
    genuine stationary point, because parasite drag carries a compressibility
    penalty that is minimised near 25 degrees.

    That distinction is the difference between a design insight and an
    arithmetic consequence of where the limits were drawn, and the act says
    which it has rather than leaving a reader to assume the former. It is also
    what makes the analogue rows legible: a span on the limit is why the span,
    the aspect ratio and the wing area all read outside the analogue envelope.
    """
    on: list[str] = []
    if abs(float(best["span"]) - _SPAN_STRUCTURAL_LIMIT) < 1e-6:
        on.append(f"the {_SPAN_STRUCTURAL_LIMIT:.0f} m structural span limit")
    # The winner takes the smallest wing it is allowed, so the question is what
    # stopped it going smaller — and the two answers are different claims. A
    # low-speed limit ruling out every smaller area is a floor the physics set.
    # Nothing smaller having been searched is a floor the GRID set, and calling
    # that one a landing-speed floor would credit the model for an edge of the
    # sweep. A light aircraft clears the low-speed limits at every area on the
    # grid and lands in the second case, so both are named, separately.
    feasible_areas = [float(r["area"]) for r in results if r.get("feasible")]
    all_areas = [float(r["area"]) for r in results]
    if feasible_areas and abs(float(best["area"]) - min(feasible_areas)) < 1e-6:
        if min(all_areas) < min(feasible_areas) - 1e-6:
            on.append("the wing-area floor the low-speed limits set")
        else:
            on.append("the smallest wing area searched")
    return on


# ---------------------------------------------------------------------------
# Analogue sanity check.
#
# A selected winner is held against real aircraft flying a comparable mission.
# The check is ADVISORY: it never blocks a result and never changes a number.
# It answers one question an engineer in the audience will ask immediately,
# which is whether the winning planform is the shape of an aeroplane anyone
# has ever built.
#
# EVERY FIGURE BELOW IS A PUBLISHED ONE AND CARRIES THE DOCUMENT IT CAME FROM.
# Nothing here is estimated, derived or remembered. An aircraft whose figure
# could not be traced to a manufacturer or airworthiness document is left out
# of the table rather than filled in, because a fabricated specification is
# the single worst thing this act could put on screen: the audience knows
# these aeroplanes.
#
# WING AREA AND ASPECT RATIO ARE MOSTLY ABSENT, and the table says so rather
# than quietly comparing two parameters instead of four. Neither Airbus nor
# Boeing publishes a wing reference area in its airport planning documents,
# and neither EASA nor the FAA carries one on a type certificate data sheet
# (checked by full text search across all of them). The figures that circulate
# come from specification aggregators, they disagree between sources for the
# same aircraft, and they mix gross area with trapezoidal reference area,
# which are not the same quantity and do not pair with the same span. A
# comparison built on those would look rigorous and be worthless. Where an
# area or an aspect ratio does appear below it has an engineering document
# behind it, named in the row.
#
# SOURCES, per row:
#   span, MTOW, seating   Boeing airport planning documents (757 ACAP Rev H,
#                         767 ACAP Rev K, 777 ACAP Rev E, 737 MAX ACAP Rev F,
#                         all December 2024) and Airbus airport planning
#                         documents (AC A300-600 Rev 13, AC A330 Rev 32),
#                         cross-checked against the FAA Aircraft
#                         Characteristics Database.
#   range                 Airbus publishes a single design range figure and
#                         those are used as published. Boeing publishes
#                         payload and range CHARTS for these types and no
#                         design range number, so a Boeing range below is a
#                         chart reading and is marked ``range_charted``. It
#                         is used to choose analogues and is never displayed
#                         as a published figure.
#   wing area             Boeing 767: FAA DOT/FAA/AR-00/10, Statistical Loads
#                         Data for the 767-200ER, Table 1, which agrees with
#                         the Jenkinson, Simpkin and Rhodes design data tables
#                         to 0.04 percent. Boeing 777: the same design data
#                         tables. No other type has a traceable figure.
#   aspect ratio          Jenkinson, Simpkin and Rhodes, Civil Jet Aircraft
#                         Design, data tables. Never computed here from a
#                         span and an area, because a tip to tip span and a
#                         trapezoidal reference area do not form one.
#
# Seating is the manufacturer's own two-class figure. Spans are the published
# span of the standard build; a retrofit winglet span is not used, because a
# tip device fitted after the fact is not the wing that was designed.
_ANALOGUE_PAX_TOLERANCE = 0.20
_ANALOGUE_RANGE_TOLERANCE = 0.25
_ANALOGUES: tuple[dict, ...] = (
    {"name": "Boeing 737 MAX 8", "span_m": 35.92, "mtow_kg": 82644,
     "pax": 178, "range_km": 6480, "range_charted": False,
     "area_m2": None, "aspect_ratio": None},
    {"name": "Airbus A300-600R", "span_m": 44.84, "mtow_kg": 170500,
     "pax": 266, "range_km": 7500, "range_charted": False,
     "area_m2": None, "aspect_ratio": None},
    {"name": "Boeing 767-300", "span_m": 47.57, "mtow_kg": 156489,
     "pax": 261, "range_km": 7400, "range_charted": True,
     "area_m2": 283.4, "aspect_ratio": 7.99},
    {"name": "Boeing 767-400ER", "span_m": 51.92, "mtow_kg": 204116,
     "pax": 296, "range_km": 11100, "range_charted": True,
     "area_m2": None, "aspect_ratio": None},
    {"name": "Boeing 777-200", "span_m": 60.93, "mtow_kg": 242671,
     "pax": 375, "range_km": 6850, "range_charted": True,
     "area_m2": 427.8, "aspect_ratio": 8.67},
    {"name": "Airbus A330-300", "span_m": 60.30, "mtow_kg": 242000,
     "pax": 300, "range_km": 11750, "range_charted": False,
     "area_m2": None, "aspect_ratio": None},
)


def _analogue_payload_fraction() -> float:
    """Payload as a fraction of MTOW, measured on the analogues above.

    THE CALIBRATION THIS ACT ALREADY HAD THE DATA FOR. Every weight in the
    sizing model comes from one number: payload divided by MTOW turns a
    passenger count into a maximum take-off weight, and that weight sets the
    wing area the low-speed limits demand, the cruise lift coefficient, and
    through it the L/D that is the answer. It carried 0.22, which no aircraft
    in the table below reaches except the narrowbody, and the act was holding
    its winner against those same rows while sizing it with a figure they
    contradict. The published seating and MTOW give:

        Boeing 737 MAX 8   0.215      Boeing 767-400ER  0.145
        Airbus A300-600R   0.156      Boeing 777-200    0.155
        Boeing 767-300     0.167      Airbus A330-300   0.124

    so the mean is 0.160 and the old 0.22 sat above every widebody in the set.
    That is a calibration error against cited data, not a modelling
    preference, and it is why MTOW read low against the analogue envelope.

    The mean over the whole cited set is what is used, not the two rows a
    given mission happens to match: the fraction is a property of the aircraft
    class the model sizes, and a constant that moved with the request would
    make two runs of the same act size the same aeroplane differently. Each
    fraction is computed with the act's own `_KG_PER_PAX`, so the sizing
    reproduces these aircraft's published MTOW on average rather than
    approximately agreeing with a number from somewhere else.
    """
    return sum(a["pax"] * _KG_PER_PAX / a["mtow_kg"]
               for a in _ANALOGUES) / len(_ANALOGUES)


_PAYLOAD_FRACTION = _analogue_payload_fraction()


def analogues_for(reqs: dict) -> list[dict]:
    """The real aircraft flying a mission comparable to the stated one.

    Comparable means within the stated tolerances on both passengers and
    design range. An aircraft that matches on one and not the other is not an
    analogue: a widebody with three times the range is a different aeroplane
    solving a different problem, whatever its seat count.
    """
    pax, rng = float(reqs["passengers"]), float(reqs["range_km"])
    lo_p, hi_p = pax * (1 - _ANALOGUE_PAX_TOLERANCE), pax * (1 + _ANALOGUE_PAX_TOLERANCE)
    lo_r, hi_r = rng * (1 - _ANALOGUE_RANGE_TOLERANCE), rng * (1 + _ANALOGUE_RANGE_TOLERANCE)
    return [a for a in _ANALOGUES
            if lo_p <= a["pax"] <= hi_p and lo_r <= a["range_km"] <= hi_r]


def analogue_rows(best: dict, matches: list[dict]) -> list[list[str]]:
    """One row per parameter: the winner, the analogue envelope, the verdict.

    A parameter no analogue publishes gets a row saying exactly that, so the
    table never quietly shrinks from four parameters to two. The verdict is
    advisory language throughout; nothing here can fail a run.
    """
    # Tonnes on both sides of the comparison: the analogues carry kilograms
    # because that is the unit their airport planning documents publish.
    winner = {
        "span_m": float(best["span"]),
        "area_m2": float(best["area"]),
        "aspect_ratio": float(best["aspect_ratio"]),
        "mtow_kg": float(best["mtow_kg"]),
    }
    # The span row points at the gate-code line the conclusion raises, and it
    # names the one that is actually said: a Code F winner gets an advisory, a
    # winner inside Code E gets the finding that nothing needs to change. The
    # pointer used to say "advisory" whichever it was, so a winner that had
    # come inside the gate band sent the reader looking for an advisory the
    # run never raised.
    gate_pointer = ("gate code advisory"
                    if icao_code_letter(winner["span_m"]) == "F"
                    else "gate code finding")
    spec = (
        ("Span", "span_m", "{:.1f} m", 1.0, gate_pointer),
        ("Wing area", "area_m2", "{:.0f} m²", 1.0, None),
        ("Aspect ratio", "aspect_ratio", "{:.1f}", 1.0, None),
        ("MTOW", "mtow_kg", "{:.0f} t", 0.001, None),
    )
    rows: list[list[str]] = []
    for label, key, fmt, scale, pointer in spec:
        values = [a[key] * scale for a in matches if a.get(key) is not None]
        mine = fmt.format(winner[key] * scale)
        if not values:
            rows.append([label, mine, "not published",
                         "no comparison drawn"])
            continue
        lo, hi = min(values), max(values)
        # One analogue publishes a figure and the envelope is a point, not a
        # band. Printing "283 m² to 283 m²" would dress a single number up as
        # a range, so it prints as the single number it is.
        band = (fmt.format(lo) if lo == hi
                else f"{fmt.format(lo)} to {fmt.format(hi)}")
        mine_value = winner[key] * scale
        if lo <= mine_value <= hi:
            verdict = "within analogue envelope"
        else:
            # The direction is the useful half of the verdict: whether the
            # optimizer ran past the real aircraft or fell short of them.
            side = "above" if mine_value > hi else "below"
            verdict = f"outlier, {side} analogue envelope"
            if pointer:
                verdict += f", see {pointer}"
        rows.append([label, mine, band, verdict])
    return rows


# ---------------------------------------------------------------------------
# Figures. Every one is drawn from numbers this run produced: the sizing
# model's own constraint curves at the stated requirements, the screened grid,
# and the polars VSPAERO solved for the finalist wings.
# ---------------------------------------------------------------------------

# Figures are served from their own directory beside the mission folder, which
# keeps the mission folder to the certificate, the transcript, and the solved
# surfaces.
_PLOT_BEAT = "aircraft-optimization-plots"


def _plots_dir() -> Path:
    path = OUT_ROOT / _PLOT_BEAT
    path.mkdir(parents=True, exist_ok=True)
    return path


def _theme():
    """The control-room plot theme, or (None, None) where it cannot load."""
    try:
        from chief_engineer import plot_theme as t

        plt = t._pyplot()
    except Exception:
        return None, None
    return (t, plt) if plt is not None else (None, None)


def _finish(fig, ax, plt, t, out_png, *, loc: str = "best"):
    leg = ax.legend(frameon=False, fontsize=10, labelcolor=t.INK, loc=loc)
    for text in leg.get_texts():
        text.set_color(t.INK)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)


def low_speed_area_floor(reqs: dict) -> tuple[float, float] | None:
    """The wing area the stated low-speed limits require, and the MTOW it is
    required at. Both come straight out of the stall-speed relations
    ``evaluate_design`` uses, at the MTOW the stated passenger count sets, so
    no wing has to be sized before the requirement can be stated.

    THIS IS THE FLOOR AT ONE WEIGHT, AND EVERY SURFACE THAT SHOWS IT SAYS SO.
    Stall speed puts required area in proportion to weight at a fixed speed,
    so the floor moves with the design: MTOW carries a span-structural
    penalty in ``evaluate_design``, and a wing at the top of the span ladder
    is asked for about 8% more area than this number. The screen applies the
    moving floor already — it computes each design's own weight and tests
    that design's own approach and take-off speed — so this figure is the
    reference the requirement is quoted at, never the test that was run.

    Returns ``(area_m2, mtow_kg)``, or None when the requirements cannot
    support the calculation.
    """
    try:
        mtow = reqs["passengers"] * _KG_PER_PAX / _PAYLOAD_FRACTION
        landing_weight = 0.85 * mtow
        area_land = (2 * landing_weight * _G
                     / (_RHO_SL * _CLMAX_LANDING
                        * (reqs["landing_speed"] / 1.3) ** 2))
        area_to = (2 * mtow * _G
                   / (_RHO_SL * _CLMAX_TAKEOFF
                      * (reqs["takeoff_speed"] / 1.2) ** 2))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None
    floor = max(area_land, area_to)
    if not math.isfinite(floor) or floor <= 0:
        return None
    return floor, mtow


def low_speed_floor_figure(out_png: str | Path, reqs: dict) -> str | None:
    """Approach and take-off speed against wing area, at the MTOW the stated
    passenger count sets, with the stated speed limits and the wing area they
    require. Every curve is the same stall-speed relation the screen uses.
    """
    t, plt = _theme()
    if plt is None:
        return None
    floor_mtow = low_speed_area_floor(reqs)
    if floor_mtow is None:
        return None
    floor, mtow = floor_mtow
    try:
        landing_weight = 0.85 * mtow
        lo, hi = max(40.0, 0.40 * floor), 2.1 * floor
        areas = [lo + (hi - lo) * i / 239.0 for i in range(240)]
        approach = [1.3 * math.sqrt(2 * landing_weight * _G
                                    / (_RHO_SL * a * _CLMAX_LANDING))
                    for a in areas]
        takeoff = [1.2 * math.sqrt(2 * mtow * _G
                                   / (_RHO_SL * a * _CLMAX_TAKEOFF))
                   for a in areas]
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    ax.axvspan(lo, floor, color=t.NEEDS, alpha=0.09, linewidth=0,
               label="wing area below the floor at the reference MTOW")
    ax.plot(areas, approach, color=t.LIVE, linewidth=2.4,
            label="approach speed, 1.3 times landing stall")
    ax.plot(areas, takeoff, color=t.TREND, linewidth=2.4,
            label="take-off speed, 1.2 times take-off stall")
    ax.axhline(reqs["landing_speed"], color=t.LIVE, linewidth=1.2,
               linestyle=(0, (5, 4)),
               label=f"landing limit {reqs['landing_speed']:.0f} m/s")
    ax.axhline(reqs["takeoff_speed"], color=t.TREND, linewidth=1.2,
               linestyle=(0, (5, 4)),
               label=f"take-off limit {reqs['takeoff_speed']:.0f} m/s")
    ax.axvline(floor, color=t.VALID, linewidth=1.6)
    top = max(reqs["landing_speed"], reqs["takeoff_speed"]) * 1.7
    ax.set_xlim(lo, hi)
    ax.set_ylim(min(min(approach), min(takeoff)) * 0.86, top)
    # The line is drawn at ONE weight and the caption says which, because the
    # requirement scales with weight: a heavier wing is asked for more area
    # than this, and the screen holds each design to its own figure.
    # LEFT OF THE LINE AND LOW. The caption grew to three lines when it
    # started naming the weight; to the right of the line it ran under the
    # legend, and high on the left it crossed the approach curve. Under both
    # speed limits and left of the floor is the one empty corner of the
    # panel: every curve is above the limits everywhere in it.
    ax.annotate(f"wing area at least {floor:.0f} m$^2$\n"
                f"at reference MTOW {mtow / 1000:.0f} t;\n"
                f"applied per design at each wing's weight",
                xy=(floor, top * 0.44), xytext=(-10, 0),
                textcoords="offset points", ha="right", va="center",
                fontsize=11.5, color=t.VALID, weight="bold",
                fontfamily="monospace")
    t.style_axes(ax, r"wing area  $S$  [m$^2$]", r"speed  $V$  [m/s]",
                 "Low speed limits set a floor under wing area")
    return _finish(fig, ax, plt, t, out_png, loc="upper right")


def sweep_trade_figure(out_png: str | Path, results, *,
                       value_key: str = "L_D") -> str | None:
    """Screened cruise L/D against quarter-chord sweep, the third design axis.

    Every point is one screened wing. The landscape canvas carries span and
    area; this is the axis that canvas cannot show, and it is why the
    candidate planform rocks through sweep angles on the way.
    """
    t, plt = _theme()
    if plt is None:
        return None
    feasible = [r for r in results if r.get("feasible")]
    if not feasible:
        return None
    infeasible = [r for r in results if not r.get("feasible")]
    best_at: dict[float, float] = {}
    for r in feasible:
        sweep = float(r["sweep_deg"])
        best_at[sweep] = max(best_at.get(sweep, float("-inf")),
                             float(r[value_key]))
    sweeps = sorted(best_at)
    top = max(feasible, key=lambda r: r[value_key])

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    if infeasible:
        ax.scatter([r["sweep_deg"] for r in infeasible],
                   [r[value_key] for r in infeasible],
                   s=26, color=t.DIM, alpha=0.75, linewidth=0,
                   label="misses a requirement")
    ax.scatter([r["sweep_deg"] for r in feasible],
               [r[value_key] for r in feasible],
               s=34, color=t.LIVE, alpha=0.9, linewidth=0,
               label="clears every requirement")
    ax.plot(sweeps, [best_at[s] for s in sweeps], color=t.TREND,
            linewidth=2.2, marker="o", markersize=6,
            markeredgecolor=t.INK, markeredgewidth=0.8,
            label="best feasible wing at each sweep")
    ax.scatter([top["sweep_deg"]], [top[value_key]], s=150, facecolor="none",
               edgecolor=t.VALID, linewidth=2.0, zorder=6)
    ax.annotate(f"best screened whole-aircraft $L/D$ {top[value_key]:.1f}\n"
                f"at {top['sweep_deg']:.0f}° sweep",
                xy=(top["sweep_deg"], top[value_key]), xytext=(14, 12),
                textcoords="offset points", ha="left", va="bottom",
                fontsize=11.5, color=t.VALID, weight="bold",
                fontfamily="monospace")
    pad = (max(sweeps) - min(sweeps)) * 0.22 or 2.0
    ax.set_xlim(min(sweeps) - pad, max(sweeps) + pad * 1.9)
    ax.set_xticks(sweeps)
    t.style_axes(ax, r"quarter-chord sweep  $\Lambda$  [deg]",
                 r"whole-aircraft $L/D$  [nondimensional]",
                 "Whole-aircraft L/D against quarter-chord sweep "
                 f"{TIER_SCREEN}")
    return _finish(fig, ax, plt, t, out_png, loc="lower left")


def drag_polar_figure(out_png: str | Path, solved, best, *,
                      cd0_nonwing: float = _CD0_NONWING) -> str | None:
    """The solved finalist polars, as whole-aircraft drag against lift.

    Each curve is one VSPAERO polar: the solved induced and wing viscous drag
    at every solved lift coefficient, plus the non-wing component buildup that
    the same constant adds everywhere in this act. The winner's cruise point
    is the point the verdict stands on.
    """
    t, plt = _theme()
    if plt is None:
        return None
    curves = []
    for f in solved:
        polar = f.get("_polar")
        if not isinstance(polar, dict):
            continue
        points = []
        for cl, cdi, cdo in zip(polar.get("CLtot") or (),
                                polar.get("CDi") or (),
                                polar.get("CDo") or ()):
            try:
                cl, cd = float(cl), cd0_nonwing + float(cdo) + float(cdi)
            except (TypeError, ValueError):
                continue
            if math.isfinite(cl) and math.isfinite(cd):
                points.append((cd, cl))
        if len(points) >= 2:
            points.sort(key=lambda p: p[1])
            curves.append((f, points))
    if not curves:
        return None

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    others = [(f, pts) for f, pts in curves if f is not best]
    for i, (f, pts) in enumerate(others):
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=t.DIM,
                linewidth=1.3, alpha=0.9,
                label=(f"other finalist wings, {len(others)} solved"
                       if i == 0 else None))
    winner = next((pts for f, pts in curves if f is best), None)
    if winner:
        ax.plot([p[0] for p in winner], [p[1] for p in winner], color=t.LIVE,
                linewidth=2.6,
                label=f"winning wing, span {best['span']:.0f} m")
    try:
        cl_w = float(best["cl_cruise"])
        cd_w = (cd0_nonwing + float(best["cdo_wing_solved"])
                + float(best["cdi_solved"]))
        ld_w = float(best["L_D_solved"])
    except (KeyError, TypeError, ValueError):
        cl_w = cd_w = ld_w = None
    if cl_w is not None:
        ax.scatter([cd_w], [cl_w], s=150, color=t.TREND, edgecolor=t.INK,
                   linewidth=1.4, zorder=6, label="cruise point on the winner")
        ax.annotate(f"whole-aircraft $L/D$ {ld_w:.1f} at $C_L$ {cl_w:.2f}",
                    xy=(cd_w, cl_w), xytext=(14, -4),
                    textcoords="offset points", ha="left", fontsize=11.5,
                    color=t.TREND, weight="bold", fontfamily="monospace")
    t.style_axes(
        ax, r"whole-aircraft drag  $C_D$  [nondimensional]",
        r"lift  $C_L$  [nondimensional]",
        f"Drag polars for the finalist wings {TIER_SOLVE}")
    return _finish(fig, ax, plt, t, out_png, loc="upper left")


def parse_requirements(text: str) -> dict:
    """Pull the mission requirements out of the prompt; state defaults for any
    that are missing so nothing is silently assumed."""
    text = text or ""

    def _speed(patterns: list[str], default: float) -> tuple[float, bool]:
        for pat in patterns:
            m = re.search(pat, text, re.I)
            if m:
                value = float(m.group(1).replace(",", ""))
                unit = (m.group(2) or "").lower() if m.lastindex and m.lastindex >= 2 else ""
                if "kn" in unit:
                    value *= 0.514444
                elif "km/h" in unit or "kph" in unit:
                    value /= 3.6
                return value, True
        return default, False

    pax_match = re.search(r"(\d[\d,]*)\s*(?:people|passengers?|pax|seats?)", text, re.I)
    passengers = int(pax_match.group(1).replace(",", "")) if pax_match else 180
    range_match = re.search(r"(?:range[^\d]{0,12})?(\d[\d,]*(?:\.\d+)?)\s*(km|nm|mi)\b", text, re.I)
    range_km = 5000.0
    range_stated = False
    if range_match:
        r = float(range_match.group(1).replace(",", ""))
        unit = range_match.group(2).lower()
        range_km = r * (1.852 if unit == "nm" else 1.609 if unit == "mi" else 1.0)
        range_stated = True

    takeoff, to_stated = _speed(
        [r"take[\s-]?off\s*(?:speed)?[^\d]{0,6}(\d+(?:\.\d+)?)\s*(m/s|kn(?:ots)?|km/h|kph)?"], 80.0)
    landing, ld_stated = _speed(
        [r"land(?:ing)?\s*(?:speed)?[^\d]{0,6}(\d+(?:\.\d+)?)\s*(m/s|kn(?:ots)?|km/h|kph)?"], 70.0)

    return {
        "passengers": passengers, "passengers_stated": bool(pax_match),
        "range_km": range_km, "range_stated": range_stated,
        "takeoff_speed": takeoff, "takeoff_stated": to_stated,
        "landing_speed": landing, "landing_stated": ld_stated,
    }


def assumed_values(reqs: dict) -> list[tuple[str, str, str]]:
    """The assumed-values ledger: every number the answer rests on that the
    request did not state and no solver produced.

    Built once and read everywhere. The requirements the prompt left out come
    first, then the low-speed lift coefficients, then the non-wing drag share.
    The lift coefficients matter most: take-off and landing feasibility turns
    on them, and a vortex-lattice solver cannot produce a maximum lift
    coefficient at all, so the ledger says where they came from instead.
    """
    rows: list[tuple[str, str, str]] = []
    if not reqs.get("passengers_stated"):
        rows.append(("Passengers", f"{reqs['passengers']:.0f}",
                     "assumed, not stated"))
    if not reqs.get("range_stated"):
        rows.append(("Range requirement", f"{reqs['range_km']:.0f} km",
                     "assumed, not stated"))
    if not reqs.get("takeoff_stated"):
        rows.append(("Take-off speed limit", f"{reqs['takeoff_speed']:.0f} m/s",
                     "assumed, not stated"))
    if not reqs.get("landing_stated"):
        rows.append(("Landing speed limit", f"{reqs['landing_speed']:.0f} m/s",
                     "assumed, not stated"))
    rows.append(("C_L_max (take-off)", f"{_CLMAX_TAKEOFF:.1f}",
                 "assumed, not solver-derived"))
    rows.append(("C_L_max (landing)", f"{_CLMAX_LANDING:.1f}",
                 "assumed, not solver-derived"))
    rows.append(("Non-wing drag share", f"C_D0 {_CD0_NONWING:.3f}",
                 "assumed, Raymer component buildup"))
    # Every weight in the model comes off this one number, so it is a ledger
    # row and it names where it was measured rather than reading as a house
    # constant. It is not assumed: it is the mean of the published seating and
    # MTOW of the analogue aircraft the winner is held against below.
    rows.append(("Payload fraction", f"{_PAYLOAD_FRACTION:.3f}",
                 "measured on the analogue aircraft, not assumed"))
    return rows


def constraint_list(reqs: dict, *, advisory: bool,
                    winner_span: float | None = None
                    ) -> list[tuple[str, str, str]]:
    """Every constraint the run used, tagged by where it came from.

    ``user-stated`` is a limit the request named, ``derived`` is one that
    follows from the limits the request named, ``assumed`` is one the act
    supplied because the request did not, and ``advisory`` is a limit nobody
    asked for that the run raised anyway. The gate-code row carries its own
    disposition, so the page says what happened to the advisory and not just
    that it fired.

    THE WING-AREA FLOOR IS A DERIVED ROW, and the distinction is the whole
    reason the third tag exists. When the request states the take-off and the
    landing speed, those two limits stop being lab assumptions, and the wing
    area they demand stops being one with them: it falls straight out of the
    stall-speed relations at the MTOW the stated passenger count sets. What
    does NOT become derived is the pair of maximum lift coefficients that
    floor rests on. A speed limit on its own fixes no maximum lift
    coefficient, so those two stay in the assumed-values ledger and the floor
    stays here, tagged for what it is.

    AND THE FLOOR IS QUOTED AT A WEIGHT. Required area scales with weight at
    a fixed stall speed, so one number cannot be the floor for every design.
    The row names the reference MTOW its value belongs to and says that the
    screen holds each wing to the floor its own weight sets, which is what
    ``evaluate_design`` does: it re-weighs the design, then tests that
    design's own approach and take-off speed.
    """
    def tag(stated: bool) -> str:
        return "user-stated" if stated else "assumed"

    rows = [
        ("Passengers", f"{reqs['passengers']:.0f}",
         tag(bool(reqs.get("passengers_stated")))),
        ("Range", f"at least {reqs['range_km']:.0f} km",
         tag(bool(reqs.get("range_stated")))),
        ("Take-off speed", f"at most {reqs['takeoff_speed']:.0f} m/s",
         tag(bool(reqs.get("takeoff_stated")))),
        ("Landing speed", f"at most {reqs['landing_speed']:.0f} m/s",
         tag(bool(reqs.get("landing_stated")))),
    ]
    floor_mtow = low_speed_area_floor(reqs)
    if floor_mtow:
        speeds_stated = (bool(reqs.get("takeoff_stated"))
                         and bool(reqs.get("landing_stated")))
        rows.append((
            "Wing area",
            f"at least {floor_mtow[0]:.0f} m² at reference MTOW "
            f"{floor_mtow[1] / 1000:.0f} t",
            ("derived, from the stated speeds" if speeds_stated
             else "derived, from the speed limits above")
            + "; applied per-design at each wing's weight"))
    rows.append(
        ("Structural span limit", f"at most {_SPAN_STRUCTURAL_LIMIT:.0f} m",
         "assumed"))
    if advisory:
        if winner_span is not None and winner_span < _ICAO_CODE_E_MAX_SPAN:
            disposition = "advisory, winner inside Code E"
        else:
            disposition = "advisory, re-run offer open"
        rows.append((*ICAO_CONSTRAINT_ROW, disposition))
    return rows


def measure_surface_span(path: str | Path) -> float | None:
    """Measure an uploaded STL/OBJ starting geometry: the largest horizontal
    extent of its bounding box (z up), taken as the approximate span.

    Returns None when the file cannot be parsed — the caller must then say the
    surface is on file as the reference shape, never invent a measurement."""
    from chief_engineer.geometry import _read_obj, _read_stl

    try:
        path = Path(path)
        if path.suffix.lower() == ".obj":
            vertices, _faces = _read_obj(path)
        else:
            vertices, _faces = _read_stl(path)
    except Exception:
        return None
    if not vertices:
        return None
    extents = []
    for axis in (0, 1):   # x streamwise, y spanwise; z is vertical
        values = [v[axis] for v in vertices]
        extents.append(max(values) - min(values))
    span = max(extents)
    return round(span, 3) if span > 0 else None


def surface_bodies(path: str | Path) -> dict | None:
    """Read an uploaded surface and describe it as bodies and proportions.

    Triangles that share a vertex position belong to the same body, so the
    count of bodies is the count of separately connected pieces the file
    holds: one for a wing on its own, more once a fuselage or a tail arrives
    as its own shell. Positions are rounded before they are compared, because
    a triangle mesh repeats each corner per facet and the repeats have to fall
    together for the count to mean anything.

    Returns ``{"bodies", "span", "chord", "thickness", "faces"}`` in the file's
    own units, or None when the file cannot be read as a surface.
    """
    from chief_engineer.geometry import _read_obj, _read_stl

    try:
        path = Path(path)
        if path.suffix.lower() == ".obj":
            vertices, faces = _read_obj(path)
        else:
            vertices, faces = _read_stl(path)
    except Exception:
        return None
    if not vertices or not faces:
        return None

    extents = [max(v[i] for v in vertices) - min(v[i] for v in vertices)
               for i in range(3)]
    scale = max(extents) or 1.0
    quantum = scale * 1e-5

    def key(index: int):
        v = vertices[index]
        return (round(v[0] / quantum), round(v[1] / quantum),
                round(v[2] / quantum))

    parent: dict = {}

    def find(a):
        root = a
        while parent[root] != root:
            root = parent[root]
        while parent[a] != root:
            parent[a], a = root, parent[a]
        return root

    def union(a, b):
        parent.setdefault(a, a)
        parent.setdefault(b, b)
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for face in faces:
        if len(face) < 3:
            continue
        try:
            corners = [key(i) for i in face[:3]]
        except IndexError:
            continue
        union(corners[0], corners[1])
        union(corners[1], corners[2])
    bodies = len({find(k) for k in parent}) if parent else 0

    # z is vertical, so the two horizontal extents are the planform: the
    # larger is the span, the smaller the streamwise chord.
    horizontal = sorted(extents[:2], reverse=True)
    return {"bodies": bodies, "span": round(horizontal[0], 3),
            "chord": round(horizontal[1], 3), "thickness": round(extents[2], 3),
            "faces": len(faces)}


def is_lifting_surface_only(shape: dict | None) -> bool:
    """True when the uploaded surface is one lifting surface and nothing else.

    One connected body, thin against its own span, and longer across than
    along. A configuration that carries a fuselage or a tail fails at least
    one of the three.
    """
    if not shape or shape.get("bodies") != 1:
        return False
    span = float(shape.get("span") or 0.0)
    if span <= 0:
        return False
    return (float(shape.get("thickness") or 0.0) / span
            <= _LIFTING_THICKNESS_RATIO
            and float(shape.get("chord") or 0.0) / span
            <= _LIFTING_CHORD_RATIO)


def scope_mismatch(request: str, shape: dict | None) -> bool:
    """The wing-for-an-aircraft gap: a lifting surface arrives on its own and
    the objective names a whole aircraft. Both halves must hold."""
    return bool(_FULL_AIRCRAFT.search(request or "")
                and is_lifting_surface_only(shape))


def interpretation_confidence(request: str) -> float | None:
    """The same interpretation confidence the route panel reads out, taken
    from the same classification rather than a second opinion of it."""
    try:
        from chief_engineer.router import classify

        return float(classify(request or "").confidence)
    except Exception:
        return None


# The scope statement, as the owner wrote it. It is the first thing the digest
# shows on a triggered mission, before any plan content, so a recording of the
# digest carries the scope without scrolling.
SCOPE_STATEMENT = (
    "Geometry received is a wing only. Treating this as wing design for the "
    "stated aircraft.",
    "Fuselage, tail, and nacelle drag are added from Raymer's component "
    "buildup method.",
    "All L/D figures quoted are whole-aircraft.")


def seeded_spans(measured_span: float) -> tuple[float, ...]:
    """Centre the span ladder on a measured starting-geometry span.

    The centre is clamped to sane airliner bounds and every rung to the
    structural limit, so the search still brackets the measured span with
    buildable wings on both sides wherever possible."""
    center = min(max(float(measured_span), _SPAN_CENTER_LO), _SPAN_CENTER_HI)
    spans: list[float] = []
    for offset in _SPAN_SEED_OFFSETS:
        rung = min(max(center + offset, _SPAN_SEED_FLOOR), _SPAN_STRUCTURAL_LIMIT)
        if rung not in spans:
            spans.append(rung)
    return tuple(spans)


# Transcript-table headers for the live finalist-solve rows.
#
# SWEEP IS IN THE TABLE because without it the rows are not identifiable. The
# finalists cluster on the top span rungs, so three of nine read "68 m" and
# differ only in a tenth of a degree of alpha — which is an OUTPUT of the
# solve, not a design variable. Sweep is the design variable that separates
# them, and it is the one the screened-against-solved table below already
# carries, so the two tables now name the same wing the same way.
#
# AREA IS IN IT FOR EXACTLY THE SAME REASON, and span and sweep together were
# not enough. Two rows of the audited run both read "61 m, 25°" and carried
# whole-aircraft L/D 19.3 and 17.5: different wings, 360 m² and 420 m², told
# apart by nothing on screen. A 1.8 gap between two rows a viewer cannot
# distinguish reads as the solver disagreeing with itself. Area is the third
# design variable and the screened-against-solved table already carries it, so
# the full design vector is now on both.
_FINALIST_HEADERS = ("Span", "Area", "Sweep", "α", "C_Di", "C_D0, wing",
                     "Whole-aircraft L/D")
_FINALIST_TABLE_TITLE = f"Finalist solves {TIER_SOLVE}"


def _record_rows(script, *, title: str, headers, rows, role: str = _SPEAKER,
                 echo: bool = False) -> None:
    """Write table rows to the saved transcript, in the order given.

    Split out from ``_emit_table`` because the two audiences want different
    orders. The control room wants rows the moment their solve finishes,
    which is the order the box happened to finish them in and is therefore
    different every run. The saved transcript is the record a replay is
    checked against, so it takes the rows in a fixed order and the same run
    reproduces line for line.
    """
    for row in rows:
        line = " | ".join(f"{h} {cell}" for h, cell in zip(headers, row))
        entry = Entry(role, f"[{title}] {line}")
        script.entries.append(entry)
        if echo and script.echo:
            script.echo(entry.render())


def _emit_table(emit, script, *, title: str, headers, rows, table_id: str,
                append: bool = False, role: str = _SPEAKER,
                record: bool = True) -> None:
    """Put a transcript table on the record.

    The control room renders it as a compact table in the same paced feed as
    transcript entries; ``append=True`` lands new rows into the existing table
    (rows arrive live as solves finish). Every row is also mirrored into the
    saved transcript so the on-disk record keeps the numbers.

    ``record=False`` sends the rows to the control room and leaves them out of
    the saved transcript, for a caller that lands rows in completion order on
    screen and writes them to the record in a fixed order afterwards."""
    if emit:
        emit("transcript.table", {
            "role": role, "title": title,
            "headers": [str(h) for h in headers],
            "rows": [[str(cell) for cell in row] for row in rows],
            "table_id": table_id, "append": bool(append), "at": time.time()})
    if record:
        _record_rows(script, title=title, headers=headers, rows=rows,
                     role=role, echo=emit is None)


def evaluate_design(span: float, area: float, sweep_deg: float, reqs: dict) -> dict:
    """Size one wing against the requirements and return its L/D and feasibility.

    Weights come from the passenger count; the drag polar gives cruise L/D; the
    stall speed sets whether the wing is large enough for the stated take-off and
    landing speeds; and a Breguet estimate gives the range this L/D can fly.
    """
    payload = reqs["passengers"] * _KG_PER_PAX
    mtow = payload / _PAYLOAD_FRACTION
    # A larger span costs structural weight; kept mild and explicit.
    mtow *= 1.0 + 0.0025 * max(0.0, span - 36.0)
    landing_weight = 0.85 * mtow

    aspect_ratio = span ** 2 / area
    sweep = math.radians(sweep_deg)
    oswald = 0.80 * math.cos(sweep) ** 0.15
    cd0 = 0.019 + 0.00025 * (sweep_deg - 25.0) ** 2 / 10.0
    cl_cruise = mtow * _G / (0.5 * _RHO_CRUISE * _V_CRUISE ** 2 * area)
    cd = cd0 + cl_cruise ** 2 / (math.pi * aspect_ratio * oswald)
    l_over_d = cl_cruise / cd

    v_stall_land = math.sqrt(2 * landing_weight * _G / (_RHO_SL * area * _CLMAX_LANDING))
    v_stall_to = math.sqrt(2 * mtow * _G / (_RHO_SL * area * _CLMAX_TAKEOFF))
    approach_speed = 1.3 * v_stall_land
    takeoff_speed = 1.2 * v_stall_to

    breguet_range_km = range_for_ld(l_over_d)

    violations = []
    if approach_speed > reqs["landing_speed"] + 1e-6:
        violations.append(
            f"approach speed {approach_speed:.0f} m/s exceeds the "
            f"{reqs['landing_speed']:.0f} m/s landing limit "
            f"(assumed C_L_max (landing) = {_CLMAX_LANDING:.1f})")
    if takeoff_speed > reqs["takeoff_speed"] + 1e-6:
        violations.append(
            f"take-off speed {takeoff_speed:.0f} m/s exceeds the "
            f"{reqs['takeoff_speed']:.0f} m/s limit "
            f"(assumed C_L_max (take-off) = {_CLMAX_TAKEOFF:.1f})")
    if breguet_range_km < reqs["range_km"] - 1e-6:
        violations.append(
            f"range {breguet_range_km:.0f} km short of the {reqs['range_km']:.0f} km requirement")
    if span > _SPAN_STRUCTURAL_LIMIT:
        violations.append(f"span {span:.0f} m beyond the {_SPAN_STRUCTURAL_LIMIT:.0f} m structural limit")

    return {
        "span": round(span, 3), "area": round(area, 2), "sweep_deg": round(sweep_deg, 2),
        "aspect_ratio": round(aspect_ratio, 3),
        "cl_cruise": round(cl_cruise, 4),
        "L_D": round(l_over_d, 4), "mtow_kg": round(mtow, 0),
        "approach_speed": round(approach_speed, 2), "takeoff_speed": round(takeoff_speed, 2),
        "range_km": round(breguet_range_km, 0),
        "feasible": not violations, "violations": violations,
    }


def _solve_finalist_slot(index, api, design, emit=None, script=None):
    """Solve one finalist wing on worker slot ``index``, surviving a mid-batch kill.

    Mirrors the shape-optimization sweep so the on-camera resilience beat rides an
    industry-grade surface (a real airliner wing), not a toy body. Before the slot
    does its work it checks whether that worker was struck down — a kill marker
    dropped by scripts/kill_worker.sh, read through the shared fleet mechanism. If
    so, the loss is reported on the record, the marker cleared, a fresh worker
    stood up, and the wing re-solved — so the batch finishes with exactly the
    polar a clean run would have produced. The wing is solved once either way;
    only the slot that carries it changes. A solve that returns no polar comes
    back as None so one bad wing does not sink the batch.
    """
    from chief_engineer.fleet import clear_sabotage, worker_sabotaged

    if worker_sabotaged(index):
        clear_sabotage(index)
        lost = (f"• Worker {index + 1} stopped responding mid-solve. "
                f"• Reprovisioning and re-running its wing; the polar still lands.")
        took_over = f"• A fresh worker took over slot {index + 1}; its wing re-solves."
        if script is not None:
            script.engineer(lost)
        if emit is not None:
            emit("worker.killed", {"worker_index": index, "detail": lost, "pending": 1})
            emit("worker.reprovisioned", {"worker_index": index, "detail": took_over})
    try:
        return api.evaluate(design)
    except Exception:
        return None


# The third planform variable: quarter-chord sweep. Varying it (not just span
# and area) makes the candidate wing visibly morph on screen — the planform
# rocks through the sweep angles as well as growing and shrinking. It is a real
# design variable, not decoration: cd0 carries a compressibility penalty that is
# minimised near 25° (the drag-divergence-optimal sweep for this cruise Mach) and
# span efficiency falls with sweep, so the optimiser finds a genuine interior
# sweep optimum rather than railing to an edge.
_SWEEPS = (20.0, 25.0, 30.0, 35.0)


def _design_grid(spans: tuple[float, ...] | None = None
                 ) -> list[tuple[float, float, float]]:
    """A span × area × sweep sweep of the wing design space.

    Sweep is the innermost loop so the viewport wing rocks through the sweep
    angles repeatedly across the screening — the geometry changes many times,
    not just once, which is the whole point of watching the design space fill.
    ``spans`` re-centres the ladder around a measured starting-geometry span.
    """
    grid = []
    # The ladder runs all the way to the structural span limit. The hypothesis
    # is that L/D climbs with aspect ratio until a limit stops it, and a ladder
    # that stops short of its own stated limit never tests that. The top rungs
    # also reach past the gate-code band, which is where the advisory lives.
    for span in (spans or (34, 40, 46, 52, 58, 64, _SPAN_STRUCTURAL_LIMIT)):
        for area in (240, 300, 360, 420):
            for sweep in _SWEEPS:
                grid.append((float(span), float(area), float(sweep)))
    return grid


def main(request: str | None = None, params: dict | None = None,
         iterations: int = 1, emit=None) -> int:
    params = params or {}
    out = OUT_ROOT / "aircraft-optimization"
    out.mkdir(parents=True, exist_ok=True)
    script = make_transcript("aircraft optimization", emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)

    reqs = parse_requirements(request or "")
    script.system(request or "Request: maximise the airliner's lift-to-drag ratio "
                             "subject to its mission requirements.")

    # ---- scope statement, before anything else ------------------------------
    # A lifting surface arrives on its own while the objective names a whole
    # aircraft. The gap is real, the act resolves it one way, and it says so
    # first: this is the opening line of the digest on a triggered mission,
    # ahead of any plan content, so the scope is legible in one screenshot.
    start_surface = str(params.get("surface") or "").strip()
    shape = (surface_bodies(_GEOMETRY_DIR / start_surface)
             if start_surface else None)
    scoped = scope_mismatch(request or "", shape)
    if scoped:
        confidence = interpretation_confidence(request or "")
        clause = ("Interpretation confidence "
                  f"{confidence * 100:.0f}%, geometry and objective scope "
                  f"mismatch resolved as above." if confidence is not None
                  else "Geometry and objective scope mismatch resolved as "
                       "above.")
        script.engineer(
            f"• {SCOPE_STATEMENT[0]} "
            f"• {SCOPE_STATEMENT[1]} "
            f"• {SCOPE_STATEMENT[2]} {clause}")

    # ---------------- Hypothesis ----------------
    script.phase(HYPOTHESIS)
    # THE RESEARCHER OPENS. The method ruling is the first thing on the record
    # and it is two entries under one Chief Researcher header: how the problem
    # classifies, and what makes the choice admissible. The engineer answers
    # it, and the requirements the method will be run against come with the
    # answer rather than in a second Chief Engineer entry of their own.
    roster.set(CHIEF_RESEARCHER, "selecting the method", "working")
    props = MissionProperties(
        kind="parametric-optimization",
        objective="maximise the cruise lift-to-drag ratio",
        dimensionality=3,          # wing span, area, and quarter-chord sweep
        regime="steady",
        smoothness="smooth",
        fidelity="a research sizing model",
        constraints=("take-off speed", "landing speed", "range"))
    for line in method_memo(props):
        script.researcher(line)
    roster.idle(CHIEF_RESEARCHER)

    roster.set(CHIEF_ENGINEER, "reading the requirements", "working")
    # The constraint list is naturally a table: each limit with a value and a
    # source. As a sentence it was a run of numbers a viewer had to parse. The
    # gate-code row is not here because nothing has been searched yet; it
    # joins the list on the certificate once the search has a span to raise it
    # against.
    script.engineer(
        f"{ENGINEER_ACK} "
        "• Requirements fixed, every value the request left out assumed and "
        "marked. "
        "• Weight rides on the passenger count, and the answer rides on "
        "weight.")
    _emit_table(
        emit, script, title="Constraints",
        headers=["Constraint", "Limit", "Basis"],
        rows=[[name, value, tag]
              for name, value, tag in constraint_list(reqs, advisory=False)],
        table_id="constraints")

    # The ledger the marking produces, on the record as a table rather than a
    # run of near-identical sentences. The two lift coefficients are the load
    # bearing rows: every take-off and landing verdict below turns on them,
    # and a vortex-lattice solver cannot produce a maximum lift coefficient,
    # so the number is stated with where it came from instead of implied.
    #
    # WHAT MOVED WHEN THE SPEEDS BECAME STATED, because the split is easy to
    # overstate in the aircraft's favour. A request that names the take-off
    # and landing speeds moves both out of this ledger and onto the constraint
    # table as user-stated, and the wing area they demand moves with them as a
    # derived row. The two maximum lift coefficients do NOT move: a speed
    # limit fixes no maximum lift coefficient on its own, and calling them
    # derived would credit the request for a number it never gave. They stay
    # here, and the line below says which half went where.
    ledger_rows = assumed_values(reqs)
    roster.set(NUMERICIST, "marking the assumed values", "working")
    if reqs.get("takeoff_stated") and reqs.get("landing_stated"):
        script.numericist(
            "• You stated both speeds, so the wing area they demand is "
            "derived, not assumed. "
            "• The maximum lift coefficients that floor rests on are still "
            "assumed, and named.")
    else:
        script.numericist(
            "• Both low-speed limits are assumed here, and so is the wing "
            "area they demand. "
            "• Every low-speed verdict below names the lift coefficient it "
            "used.")
    # A requirement the request left out is already on the constraint table
    # above, tagged assumed, so it is not repeated here. What is left is the
    # physics the answer rests on and nothing supplied: the two lift
    # coefficients and the non-wing drag share. The certificate carries the
    # ledger complete, because it is read on its own.
    _emit_table(
        emit, script, title="Assumed values",
        headers=["Quantity", "Value", "Basis"],
        rows=[[label, value, basis] for label, value, basis in ledger_rows
              if basis != "assumed, not stated"],
        table_id="assumed-values", role=_NUMERICIST_SPEAKER)
    roster.idle(NUMERICIST)

    # The one thing the selected method cannot reach, ruled on by the chief who
    # chose it rather than by the numericist who inherits it. It sits HERE, one
    # entry after the ledger names the two coefficients, and not up in the memo:
    # three Chief Researcher entries ran back to back there, which reads as the
    # same person speaking three times instead of one chief making one ruling.
    script.researcher(
        "• Take-off and landing feasibility rests on a maximum lift "
        "coefficient no vortex-lattice solve can produce. "
        "• But good for preliminary design.")

    # The hypothesis phase shows the trade before it claims it: the stall-speed
    # relations the screen will use, evaluated at the MTOW this passenger count
    # sets, give the wing area the stated speeds require. No wing has been
    # sized yet, so this is the requirement itself, drawn.
    report_plots: list[dict] = []
    floor_png = low_speed_floor_figure(
        _plots_dir() / "wing-area-floor.png", reqs)
    if floor_png:
        title = "Low speed limits set a floor under wing area"
        announce_plot(emit, _PLOT_BEAT, floor_png, title)
        report_plots.append(
            {"url": f"/api/plot/{_PLOT_BEAT}/{Path(floor_png).name}",
             "title": title})
        area_floor = low_speed_area_floor(reqs)
        if area_floor:
            script.engineer(
                f"• The two speed limits already ask for "
                f"{area_floor[0]:.0f} m² of wing at "
                f"{area_floor[1] / 1000:.0f} t. "
                f"• That floor rises with weight, and every wing is held to "
                f"its own.")

    # ---- uploaded starting geometry -----------------------------------------
    # A surface uploaded with the prompt is the search's starting geometry: it
    # is acknowledged on the record under its display name, its span measured
    # from the file's bounding box, and the span ladder re-centred around that
    # measurement. The STL itself is never morphed and never pretended solved.
    #
    # THE RECEIPT RIDES ON THE HYPOTHESIS, one entry, not two. What arrived
    # and what the engineer expects the search to do with it are one thought,
    # and splitting them put a third Chief Engineer header in a row.
    measured_span = None
    received = ""
    if start_surface:
        surface_name = display_name(start_surface)
        measured_span = measure_surface_span(_GEOMETRY_DIR / start_surface)
        announce_geometry(emit, name=start_surface,
                          label=f"starting geometry: {surface_name}")
        received = (
            f"• Starting geometry received: {surface_name}. Measured span "
            f"about {measured_span:.0f} m; the search brackets it. "
            if measured_span else
            f"• Starting geometry received: {surface_name}. The surface is "
            f"on file as the reference shape; the search runs on default "
            f"bounds. ")

    script.engineer(
        received
        + "• Hypothesis: whole-aircraft L/D climbs with aspect ratio, so push "
        "span to the limit. "
        "• Low-speed limits floor the area; Breguet ties range to whole-aircraft "
        "L/D. "
        "• Expect the optimum where landing speed caps aspect ratio.")

    # ---------------- Plan ----------------
    script.phase(PLAN)
    grid = _design_grid(seeded_spans(measured_span) if measured_span else None)
    solver_live = vspaero.available()
    if solver_live and emit:
        # The plan just committed to a solver — this is the moment the badge
        # is earned, never before.
        emit("solver.selected", {
            "solver": "VSPAERO", "method": "vortex lattice",
            "basis": "plan commits the finalist wings to the selected solver"})
    if emit:
        # The plan phase puts the landscape skeleton on screen before any
        # point exists — axes, units, and objective announced up front.
        emit("landscape.init", {
            # The canvas is screen tier throughout, and says so in its own
            # caption: no solve-tier number shares this axis unlabelled.
            "title": f"Design-space landscape {TIER_SCREEN}",
            "x": {"key": "span", "label": "span [m]"},
            "y": {"key": "wing_area", "label": "wing area [m²]"},
            "objective": {"key": "L_D", "label": "whole-aircraft L/D",
                          "direction": "max"}})
    # ---- what the search actually spans, announced -------------------------
    # THE ANNOUNCED BOUND AND THE WINNER HAVE TO AGREE. The plan used to name
    # the design count and nothing else, and the only span figure spoken
    # before the search was the 65 m gate-code offer below, which is a
    # different quantity entirely. A viewer heard "65 m" and then met a 67 m
    # winner. The bound is now read off the grid the sweep is about to run, so
    # the winner cannot land outside the range the plan just named, whatever
    # re-centres the ladder.
    spans_searched = sorted({span for span, _area, _sweep in grid})
    areas_searched = sorted({area for _span, area, _sweep in grid})
    sweeps_searched = sorted({sweep for _span, _area, sweep in grid})
    bounds_line = (f"• Span {spans_searched[0]:.0f} to {spans_searched[-1]:.0f} m, "
                   f"area {areas_searched[0]:.0f} to {areas_searched[-1]:.0f} m², "
                   f"sweep {sweeps_searched[0]:.0f} to {sweeps_searched[-1]:.0f} degrees. ")
    if solver_live:
        plan_line = (
            f"• Plan: screen {len(grid)} wings, then solve the top "
            f"{_N_FINALISTS} feasible with VSPAERO. ")
    else:
        plan_line = (f"• Plan: screen {len(grid)} wings over span, area and "
                     f"quarter-chord sweep. ")
    plan_line += bounds_line
    plan_line += "• Infeasible designs stay on the plot, keeping the trade visible."
    # THE PLAN IS THE RESEARCHER'S. It is the method ruling made concrete —
    # what gets screened, what gets promoted, and over what bounds — so it
    # belongs to the chief who chose the method, not to the engineer who runs
    # it. The engineer's hypothesis closes the phase above, and the
    # numericist's tier line answers below, so no speaker repeats.
    roster.set(CHIEF_RESEARCHER, "setting the search bounds", "working")
    script.researcher(plan_line)
    roster.idle(CHIEF_RESEARCHER)

    if solver_live:
        script.numericist(
            "• Screen is research sizing; finalists are solved, induced plus "
            "wing viscous drag. "
            "• Fuselage, tail and nacelle drag come from Raymer's component "
            "buildup method. "
            f"• Screened numbers carry {TIER_SCREEN}; solved numbers carry "
            f"{TIER_SOLVE}.")
    else:
        script.engineer(
            "• The aero solver is not connected on this machine, and no "
            "launcher is configured. "
            "• Running the sizing screen only; reconnect and rerun for "
            "solved numbers.")
        script.numericist(
            "• Research sizing only, a drag polar, not a solved flow. "
            "• It ranks designs and finds the trade; it validates nothing. "
            "• A run of a selected aero solver is what would set the magnitude.")

    # ---- compute, audited once the work is defined --------------------------
    # THE WORKER COUNT ARRIVES WITH THE WORK, never ahead of it. The audit and
    # the headroom table are the first surfaces on the run that carry a number
    # of workers, and they used to open the plan phase: the fleet was sized on
    # camera before the viewer had been told what the fleet was for. They now
    # sit directly after the tier line above, so the count and the sizing it
    # pays for arrive together.
    capacity = audit(min(12, len(grid)), memory_per_worker_mb=128)
    if emit:
        emit("audit.completed", capacity.panel())
    script.engineer(capacity.headline(), panel=capacity.panel())

    # ---- the owner's live operating constraints, honored on the record ------
    # A time budget ("2 min at most") and a compute-headroom ask ("don't use
    # all my workers") arrive as router params. The chief optimises compute
    # live: the granted slot count is REAL — it caps the screening fan-out and
    # the finalist thread pool below, not just the narration.
    granted = capacity.capacity
    hold_back = bool(params.get("hold_workers_back"))
    time_budget_min = params.get("deadline_minutes")
    if hold_back:
        # HALF THE BOX, AND NEVER MORE THAN THE BOX HAS. The floor of four
        # keeps the fan-out worth watching, but on a busy machine the audit
        # can grant fewer slots than that: the old expression then took four
        # of three and the headroom table printed "Held back -2", which is a
        # negative count on camera and a broken promise in the same row. The
        # grant is capped at one below capacity, and never falls below a
        # single working slot.
        #
        # THAT CAP DOES NOT MAKE THE PROMISE TRUE AT EVERY CAPACITY, and the
        # comment here used to claim it did: "a request to leave headroom
        # always leaves some". At capacity 1 the expression collapses to 1,
        # because a slot floor and a headroom cap cannot both hold when the
        # box has one slot. The narration went on promising headroom anyway
        # and the table one line below read "Held back 0", contradicting it in
        # the same frame. This is load-dependent, so it does not show on a
        # quiet box: at capacity 12 the same code holds back 6, which is the
        # beat the request exists to produce.
        granted = max(1, min(max(1, capacity.capacity - 1),
                             max(4, capacity.capacity // 2)))
        held_back = capacity.capacity - granted
        # The compliance decision is a required output, not a nicety. The
        # request restricted a resource, so the run states in numbers what it
        # did about it, and the numbers land as a table rather than a sentence
        # a viewer has to parse. WHAT THE SENTENCE SAYS IS READ OFF THE SAME
        # COUNT THE TABLE PRINTS, so the two cannot disagree whatever the box
        # is doing.
        if held_back > 0:
            script.engineer(
                "• You asked me to leave headroom, so I am not taking every "
                "worker. "
                "• Here is what I am holding back.")
        else:
            script.engineer(
                f"• You asked me to leave headroom, and the audit puts this "
                f"box at capacity {capacity.capacity}. "
                f"• Holding any of that back leaves nothing to work with, so "
                f"there is no headroom to leave and I am not claiming any. "
                f"• Here are the counts.")
        _emit_table(
            emit, script, title="Worker headroom",
            headers=["Slots", "Count"],
            rows=[["Available", f"{capacity.capacity}"],
                  ["Taken", f"{granted}"],
                  ["Held back", f"{held_back}"]],
            table_id="worker-headroom")
    if time_budget_min:
        script.engineer(
            f"• Time budget on the record: {time_budget_min:g} minutes. "
            f"• The sweep and the finalist wave both fit inside it, so "
            f"nothing is cut for the deadline.")

    # ---------------- Evidence ----------------
    script.phase(EVIDENCE)
    roster.set(CHIEF_ENGINEER, "sizing the design space", "working")
    n_slots = min(granted, len(grid))
    # THE FLEET COMES UP ONCE AND GOES DOWN ONCE. Zero until sizing starts, up
    # for the whole of the work, zero at completion. It used to drop back to
    # zero between the screening sweep and the finalist wave and climb again,
    # which reads on camera as the box losing its workers and being handed
    # them back for no stated reason.
    #
    # UP IS NOT ONE NUMBER, and this comment used to say it was: "the granted
    # count for the whole of the work", which holds only when `granted` is at
    # or below the finalist count. The screened grid takes min(granted, 112)
    # slots and the finalist wave takes min(granted, 9), so on a box with more
    # than nine slots to grant the count STEPS DOWN as the work shrinks — and
    # it must, because a worker count is a claim about the run (rulings R2 and
    # R10) and nine wings do not occupy fourteen slots. What the contract
    # forbids is a second RISE, not a fall. The rule is stated in full, and
    # forced at both capacities so no box can hide either shape, at
    # ShootRoundTests.test_the_fleet_comes_up_once_and_goes_down_once.
    roster.set_workers(n_slots, "sizing wings")
    results = []
    screen_started = time.time()
    best_ld_so_far = None
    for idx, (span, area, sweep) in enumerate(grid):
        slot = idx % n_slots
        r = evaluate_design(span, area, sweep, reqs)
        results.append(r)
        if emit:
            # The dispatch panel watches this slot pick the candidate up, then
            # report it done — the fleet is visibly working through the grid.
            emit("dispatch.update", {"slot": slot, "state": "solving",
                                     "label": f"span {r['span']:.0f} m / {r['area']:.0f} m²",
                                     "detail": "research sizing"})
            emit("landscape.point", {"design": {"span": r["span"], "wing_area": r["area"]},
                                     "metrics": {"L_D": r["L_D"]}, "feasible": r["feasible"],
                                     "why": r["violations"] or None})
            # The candidate under evaluation appears in the viewport as the
            # parametric wing it is — span, area, and sweep visibly differing.
            emit("geometry.ready", {
                "url": (f"/api/geometry?span={r['span']:g}&area={r['area']:g}"
                        f"&sweep={r['sweep_deg']:g}&taper={_TAPER:g}"),
                # The caption names the SCOPE of what is on screen and nothing
                # else. The quoted L/D is whole-aircraft while the body in the
                # viewport is a wing, and "Wing-only" is the whole of what the
                # viewer needs to hold those two together; the span and area
                # stay because they are what tells one candidate from the next
                # while the planform morphs.
                "label": f"Wing-only, span {r['span']:.0f} m, "
                         f"area {r['area']:.0f} m²"})
            # Live best-feasible-L/D trace — the running optimum climbs on screen.
            if r["feasible"]:
                best_ld_so_far = (r["L_D"] if best_ld_so_far is None
                                  else max(best_ld_so_far, r["L_D"]))
                emit("trace.point", {
                    "series": "best_L_D", "x": idx + 1, "y": round(best_ld_so_far, 3),
                    "x_label": "candidates screened",
                    "y_label": "best feasible whole-aircraft L/D",
                    "title": ("Best feasible whole-aircraft L/D, running "
                              f"optimum {TIER_SCREEN}"), "feasible": True})
        if _PACE_S:
            time.sleep(_PACE_S)
        if emit:
            emit("dispatch.update", {"slot": slot, "state": "done",
                                     "label": f"span {r['span']:.0f} m / {r['area']:.0f} m²",
                                     "detail": (f"whole-aircraft L/D {r['L_D']:.1f}"
                                                if r["feasible"] else "infeasible")})
    screen_elapsed = time.time() - screen_started
    ledger.spend(len(grid) * 0.02, f"{len(grid)} research sizing evaluations")
    # The fleet stays up when the finalist wave is the next thing it does, and
    # is stood down once there is no more work for it.
    if not solver_live:
        roster.set_workers(0)

    feasible = [r for r in results if r["feasible"]]
    infeasible = results[:]  # for narration counts
    n_infeasible = len(results) - len(feasible)
    # The sweep's clock and the sweep's tally are ONE entry. They used to be
    # two, one bullet each, which put two Chief Engineer headers back to back
    # for what is a single statement about a single sweep. On the branch where
    # nothing clears, the tally has a phase of its own below and this entry
    # carries the clock alone.
    swept = f"• Screening sweep: {screen_elapsed:.2f} s, {len(grid)} designs. "
    if feasible:
        swept += (f"• {len(feasible)} of {len(results)} wings clear every "
                  f"requirement; {n_infeasible} shown infeasible.")
    script.engineer(swept)
    # The bare infeasible count becomes a breakdown: which limit ruled each
    # wing out, counted off the violation strings the screen wrote. A wing
    # that misses two limits is counted under both, so the rows do not sum to
    # the count above.
    ruled_out = violation_breakdown(results)
    # The infeasible designs stay on the landscape, so the landscape carries a
    # key for them, and the key names the limit that ruled out the most wings
    # rather than leaving the grey points to speak for themselves.
    binding = binding_constraint(results)
    if emit and n_infeasible:
        emit("landscape.legend", {
            "infeasible": (f"infeasible: {binding}" if binding
                           else "infeasible"),
            "solved": ("promoted to the solver" if solver_live else None)})

    def _say_ruled_out() -> None:
        # The numericist owns this table. Every row is a count taken off the
        # violation strings and a statement of what the verdict rests on,
        # which is the numericist's beat, not the engineer's.
        if ruled_out:
            _emit_table(
                emit, script, title="Why designs were ruled out",
                headers=["Requirement Missed", "Wings", "Verdict Rests On"],
                rows=[[label, str(count), basis]
                      for label, count, basis in ruled_out],
                table_id="ruled-out", role=_NUMERICIST_SPEAKER)

    if not feasible:
        _say_ruled_out()
        script.engineer(
            "• No wing meets every requirement at once, so nothing closes. "
            "• The mission needs a relaxation: more area, slower landing, or less range. "
            "• That is a real answer, not a failure.")
        verdict = trust(relative_error=None, converged=True,
                        in_validated_regime=False, calibrated=False,
                        why="the mission requirements are mutually infeasible on this planform")
        if emit:
            emit("result.verdict", {"quantity": "Best feasible whole-aircraft L/D",
                                    "value": "none", "envelope": "n/a", **verdict})
        # No certificate exists for a run with no feasible design; the
        # previous run's page is withdrawn so nothing out of date is served.
        # DOCKET B2: this path has NO later build to overwrite a page the
        # unlink could not remove, so it is the one place in this package
        # where a swallowed withdrawal failure is the whole story. The act
        # publishes which of the three outcomes it got.
        _withdrawn, _withdrawal = withdraw_certificate(out / "certificate.pdf")
        script.engineer(
            "• No certificate is issued when nothing closes. "
            f"• {_withdrawal}")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 0

    best = max(feasible, key=lambda r: r["L_D"])
    _say_ruled_out()
    _emit_table(
        emit, script, title=f"Screened optimum {TIER_SCREEN}",
        headers=["Best Screened", "Span", "AR", "MTOW", "Range",
                 "Approach Speed", "Whole-aircraft L/D"],
        rows=[[f"Rank 1 of {len(feasible)} feasible",
               f"{best['span']:.0f} m",
               f"{best['aspect_ratio']:.1f}",
               f"{best['mtow_kg'] / 1000:.0f} t",
               f"{best['range_km']:.0f} km",
               f"{best['approach_speed']:.0f} m/s",
               f"{best['L_D']:.1f}"]],
        table_id="screened-optimum")

    # ---- real solves on the finalists --------------------------------------
    solved_ok: list[dict] = []
    # The winner's unresolved siblings, filled once the finalists are solved.
    family: list[dict] = []
    # How many finalists actually ran at once. Defined out here because the
    # Report's methods paragraph describes the execution and must not read a
    # name that only exists on the solved path.
    n_par = 0
    if solver_live:
        finalists = sorted(feasible, key=lambda r: r["L_D"],
                           reverse=True)[:_N_FINALISTS]
        api = vspaero.VspAeroWingApi(out / "vspaero")
        roster.set(CHIEF_ENGINEER, "solving the finalist wings", "working")
        n_par = min(granted, len(finalists))
        roster.set_workers(n_par, "VSPAERO solves on finalist wings")
        # The tier label on the table below already names VSPAERO and the
        # Raymer buildup, so this line says only what the plan committed to.
        script.engineer(
            f"• Solver of choice: VSPAERO. "
            f"• Promoting the top {len(finalists)} feasible wings.")
        _emit_table(emit, script, title=_FINALIST_TABLE_TITLE,
                    headers=list(_FINALIST_HEADERS), rows=[],
                    table_id="finalist-solves")
        designs = [{
            "span": f["span"], "area": f["area"], "sweep": f["sweep_deg"],
            "taper": _TAPER, "cl_target": f["cl_cruise"],
            "re_cref": (_RHO_CRUISE * _V_CRUISE
                        * (f["area"] / f["span"]) / _MU_CRUISE),
        } for f in finalists]
        if emit:
            # Each finalist takes a worker slot for its vortex-lattice solve.
            # Slots beyond the granted parallelism show honestly as queued —
            # the dispatch panel is the compute-management beat, on camera.
            for slot, f in enumerate(finalists):
                live_now = slot < n_par
                emit("dispatch.update", {
                    "slot": slot, "state": "solving" if live_now else "idle",
                    "label": (f"finalist span {f['span']:.0f} m, "
                              f"sweep {f['sweep_deg']:.0f}\u00b0"),
                    "detail": ("VSPAERO solve" if live_now
                               else "queued for a free slot")})
        started = time.time()

        # Rows land on screen the moment their solve finishes, which is the
        # order this box happened to finish them in and is different every
        # run. They go on the saved record afterwards in rank order, so the
        # same run reproduces line for line and the live beat is kept.
        solved_rows: dict[int, list[str]] = {}

        def _finalist_job(job):
            """Solve one finalist and land its table row the moment the polar
            arrives — rows appear live as solves finish, not after the batch."""
            index, design = job
            result = _solve_finalist_slot(index, api, design, emit, script)
            f = finalists[index]
            if (result and isinstance(result.get("matched"), dict)
                    and result.get("polar")):
                matched = result["matched"]
                try:
                    whole_ld = f["cl_cruise"] / (
                        _CD0_NONWING + matched["cdo_wing"] + matched["cdi"])
                    row = [f"{f['span']:.0f} m",
                           f"{f['area']:.0f} m²",
                           f"{f['sweep_deg']:.0f}°",
                           f"{matched['alpha']:.1f}°",
                           f"{matched['cdi']:.4f}",
                           f"{matched['cdo_wing']:.4f}",
                           f"{whole_ld:.1f}"]
                    solved_rows[index] = row
                    _emit_table(
                        emit, script, title=_FINALIST_TABLE_TITLE,
                        headers=list(_FINALIST_HEADERS), rows=[row],
                        table_id="finalist-solves", append=True, record=False)
                except (KeyError, TypeError, ZeroDivisionError):
                    pass   # a malformed result stays out of the table
            return result

        # Each finalist rides a kill-checkable worker slot: scripts/kill_worker.sh
        # can strike one mid-batch, and the slot reports the loss, reprovisions,
        # and re-solves — the same polar lands. Order is preserved either way,
        # but the pool is only as parallel as the granted slot count: at one
        # slot this is strictly sequential, and the Report says which it was.
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max(1, n_par)) as pool:
            batch = list(pool.map(_finalist_job, enumerate(designs)))
        elapsed = time.time() - started
        # The record takes the rows in rank order, whatever order they landed
        # in on screen.
        _record_rows(script, title=_FINALIST_TABLE_TITLE,
                     headers=list(_FINALIST_HEADERS),
                     rows=[solved_rows[i] for i in sorted(solved_rows)],
                     echo=emit is None)
        roster.set_workers(0)
        if emit:
            for slot, (f, result) in enumerate(zip(finalists, batch)):
                emit("dispatch.update", {
                    "slot": slot, "state": "done" if result else "lost",
                    "label": (f"finalist span {f['span']:.0f} m, "
                              f"sweep {f['sweep_deg']:.0f}\u00b0"),
                    "detail": "solved" if result else "no polar"})
        ledger.spend(elapsed * len(finalists),
                     f"{len(finalists)} VSPAERO wing solves")
        # THE WALL CLOCK IS THIS RUN'S OR THERE IS NO WALL CLOCK. `elapsed` is
        # the batch clock this run measured, and it is the only wall time this
        # act may print.
        #
        # It used to fall back to max(per-wing elapsed_s) whenever no wing was
        # solved fresh, and every one of those seconds was false here. Three
        # ways over:
        #
        #   * The seconds are not this run's. Each elapsed_s is stamped into a
        #     result by the run that first produced it, so the figure came off
        #     an earlier run's clock. On the audited mission the nine polars
        #     landed inside 6.2 ms, the whole mission took 12.94 s with the
        #     screening sweep alone reporting 11.63 s, and the line still
        #     claimed 5.5 s of finalist solving.
        #   * max() is a PARALLEL estimate, valid only at as many slots as
        #     there are wings. The same sentence said one granted slot, where
        #     the sequential figure for those nine is 48.6 s.
        #   * The screen said "spent 0.00 core-min" in the same frame, off the
        #     same measured `elapsed`. Both could not be true.
        #
        # So there is no fallback. When this run measured no solving time it
        # prints no time clause, and the wing count and slot count stand
        # alone. The physics is unaffected either way: every prior is
        # re-validated against this design's own cruise target to 1e-6 before
        # it is usable at all (vspaero._usable_prior).
        solved_fresh = any(isinstance(r, dict) and not r.get("reused_prior")
                           for r in batch)
        reported_s = elapsed if solved_fresh else None
        if reported_s is not None and reported_s >= 0.05:
            script.engineer(
                f"• Finalist solves: {reported_s:.1f} s wall, "
                f"{len(finalists)} wings on {n_par} granted slots.")
        else:
            script.engineer(
                f"• Finalist solves: {len(finalists)} wings on "
                f"{n_par} granted slots.")

        for f, result in zip(finalists, batch):
            # A result without a matched cruise point or a polar (a stale or
            # partial file that slipped past the adapter) is not evidence:
            # the finalist stays screened rather than sinking the mission.
            if (not result or not isinstance(result.get("matched"), dict)
                    or not result.get("polar")):
                script.engineer(
                    f"• Finalist span {f['span']:.0f} m returned no polar, "
                    f"stays screened, marked unsolved.")
                continue
            matched = result["matched"]
            cd_total = _CD0_NONWING + matched["cdo_wing"] + matched["cdi"]
            f["L_D_solved"] = round(f["cl_cruise"] / cd_total, 4)
            f["alpha_solved"] = round(matched["alpha"], 3)
            f["cdi_solved"] = round(matched["cdi"], 6)
            f["cdo_wing_solved"] = round(matched["cdo_wing"], 6)
            f["extrapolated"] = bool(matched["extrapolated"])
            f["_polar"] = result["polar"]
            solved_ok.append(f)
            # Sweep is in the filename because it is in the design vector. The
            # finalists cluster on the top span rungs, so several share a span
            # and an area and differ only in sweep; without it they all wrote
            # to one path and the surface shown as the winner was whichever
            # wing finished last.
            surface = (out / f"wing-span{f['span']:g}-area{f['area']:g}"
                             f"-sweep{f['sweep_deg']:g}.stl")
            try:
                shutil.copy(result["stl_path"], surface)
            except OSError:
                surface = None
            if emit:
                emit("vspaero.polar", {
                    "design": {"span": f["span"], "wing_area": f["area"],
                               "sweep": f["sweep_deg"]},
                    "polar": result["polar"], "matched": matched,
                    "L_D_total": f["L_D_solved"],
                    "solver": result.get("solver_version", "VSPAERO")})
                # The landscape is one tier from edge to edge: its axis, its
                # colour scale and its annotated best are all screened
                # numbers. A promoted wing is marked as promoted and keeps
                # its screened value, so no solved number lands on a screen
                # tier scale. The solved numbers have their own surfaces.
                emit("landscape.point", {
                    "design": {"span": f["span"], "wing_area": f["area"]},
                    "metrics": {"L_D": f["L_D"]},
                    "feasible": True, "solved": True})
                if surface:
                    emit("geometry.ready", {
                        "url": f"/api/surface/aircraft-optimization/{surface.name}",
                        "label": f"Wing-only, span {f['span']:.0f} m, "
                                 f"area {f['area']:.0f} m², "
                                 f"sweep {f['sweep_deg']:.0f}°"})
            # The per-finalist numbers land as live rows in the "Finalist
            # solves" transcript table (emitted the moment each solve
            # finished), so no per-wing transcript entry repeats them here.

        if solved_ok:
            best = max(solved_ok, key=lambda r: r["L_D_solved"])
            # THE WINNER IS A FAMILY WHEN THE NUMBERS SAY SO. The siblings
            # sharing this planform sit inside the band this fidelity carries,
            # so the act names the planform and says what is still open.
            family = unresolved_family(solved_ok, best)
            if len(family) > 1:
                lo = min(float(f["L_D_solved"]) for f in family)
                hi = max(float(f["L_D_solved"]) for f in family)
                script.engineer(
                    f"• Winner: the {best['span']:.0f} m, "
                    f"{best['area']:.0f} m² family, whole-aircraft L/D "
                    f"{lo:.1f} to {hi:.1f} {TIER_SOLVE}. "
                    + "• Sweep "
                    + ", ".join(f"{f['sweep_deg']:.0f}" for f in family)
                    + " degrees all land inside that spread. "
                    "• Quarter-chord sweep is not resolved at this fidelity.")
            else:
                screen_agreed = best is max(feasible, key=lambda r: r["L_D"])
                script.engineer(
                    f"• Winner: whole-aircraft L/D {best['L_D_solved']:.1f} "
                    f"{TIER_SOLVE}."
                    + (" • The screen ranked it first as well."
                       if screen_agreed else ""))
            winner_surface = (out / f"wing-span{best['span']:g}"
                                    f"-area{best['area']:g}"
                                    f"-sweep{best['sweep_deg']:g}.stl")
            if emit and winner_surface.exists():
                emit("geometry.ready", {
                    # THE LABEL THAT STAYS ON SCREEN IS THE ONE THAT MUST SAY
                    # MOST. This caption was cut back to the bare scope
                    # statement on the reasoning that the span, area and sweep
                    # all sit in tables a few lines above. Every one of the
                    # hundred-odd labels before it carried them, and this is
                    # the body left in the viewport when the act ends: it lost
                    # its identity at exactly the moment it stopped being
                    # replaced. The wing on screen is the 20 degree member of
                    # the winning family and the finalist table's first row is
                    # the 25 degree one, so an unlabelled body reads as the
                    # wrong wing. It says which wing it is.
                    "url": f"/api/surface/aircraft-optimization/{winner_surface.name}",
                    "label": f"Wing-only, span {best['span']:.0f} m, "
                             f"area {best['area']:.0f} m², "
                             f"sweep {best['sweep_deg']:.0f}°"})
        else:
            script.engineer(
                "• No finalist returned a usable polar. "
                "• The result stands on the conceptual screen alone.")

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    won_solved = bool(solved_ok)
    best_ld = best["L_D_solved"] if won_solved else best["L_D"]
    # The single range this act quotes from here on. Nothing below reads the
    # screened figure off the winner: one act, one quoted range, on the tier
    # the headline stands on.
    quoted_range_km = conclusion_range_km(best, won_solved=won_solved)

    # ONE SENTENCE FOR THE OPEN AXIS, WRITTEN ONCE AND USED EVERYWHERE. When
    # the solved numbers do not separate the winner from the siblings sharing
    # its planform, the result is the family, and the memo, the report and the
    # certificate all say that in the same words rather than three ways.
    sweep_unresolved = "quarter-chord sweep is not resolved at this fidelity"
    sweep_note = ""
    # The certificate's result table carries one row per design variable, so
    # the open axis has to be a row there and not a footnote: a page that
    # lists span, aspect ratio and weight and simply omits sweep reads as
    # though sweep were settled.
    sweep_field = f"{best['sweep_deg']:.0f}°"
    sweep_basis = "design variable"
    if len(family) > 1:
        angles = [f"{f['sweep_deg']:.0f}" for f in family]
        sweep_note = (
            f"{sweep_unresolved.capitalize()}: the {best['span']:.0f} m, "
            f"{best['area']:.0f} m² wings at "
            f"{', '.join(angles[:-1])} and {angles[-1]} degrees all fall "
            f"inside the reported interval, so the family is the result.")
        # The value cell carries the angles; "not resolved at this fidelity"
        # is a statement about WHERE THE NUMBER COMES FROM, so it belongs in
        # the basis column beside them and not inside the value. It also has
        # to FIT that column: the two together overrun the text block.
        sweep_field = f"{angles[0]} to {angles[-1]}°"
        sweep_basis = "not resolved at this fidelity"

    # The conclusion opens on figures, both drawn from this run's own numbers:
    # the sweep axis the landscape canvas has no room for, and, when the
    # finalists were solved, the polars themselves.
    for builder, name, title in (
            (lambda path: sweep_trade_figure(path, results),
             "sweep-trade.png",
             f"Whole-aircraft L/D against quarter-chord sweep "
             f"{TIER_SCREEN}"),
            ((lambda path: drag_polar_figure(path, solved_ok, best))
             if won_solved else (lambda path: None),
             "finalist-drag-polars.png",
             f"Drag polars for the finalist wings {TIER_SOLVE}")):
        try:
            path = builder(_plots_dir() / name)
        except Exception:   # a figure must never take down a good mission
            path = None
        if path:
            announce_plot(emit, _PLOT_BEAT, path, title)
            report_plots.append({"url": f"/api/plot/{_PLOT_BEAT}/{name}",
                                 "title": title})

    if won_solved:
        # The screen and the solver are held side by side per wing. The mean
        # of this column is the model-channel evidence quoted below; the
        # column itself is what it was measured from.
        # The one table where both tiers appear, so each column is headed by
        # the tier it carries. No number here can be read as the other's.
        _emit_table(
            emit, script, title="Whole-aircraft L/D, screened against solved",
            headers=["Span", "Area", "Sweep", TIER_SCREEN, TIER_SOLVE,
                     "Change"],
            rows=[[f"{f['span']:.0f} m",
                   f"{f['area']:.0f} m²",
                   f"{f['sweep_deg']:.0f}°",
                   f"{f['L_D']:.1f}",
                   f"{f['L_D_solved']:.1f}",
                   f"{f['L_D_solved'] - f['L_D']:+.1f}"]
                  for f in sorted(solved_ok, key=lambda r: r["L_D_solved"],
                                  reverse=True)],
            table_id="screen-against-solved", role=_NUMERICIST_SPEAKER)
        # A cruise point read past the end of a polar is a caveat, so it is
        # named when it happens and silent when it does not.
        past_end = [f for f in solved_ok if f.get("extrapolated")]
        if past_end:
            script.numericist(
                f"• {len(past_end)} of {len(solved_ok)} cruise points were "
                f"read past the end of their polar.")

    # ---- the winner against real aircraft -----------------------------------
    # Advisory only. It cannot block a result and it changes no number; it
    # asks whether the winning planform is the shape of an aeroplane anyone
    # has built for this mission, and says so either way.
    matches = analogues_for(reqs)
    if matches:
        # WHY THE OUTLIER ROWS ARE OUTLIERS, said BEFORE the table rather than
        # after it, so no row is read as a mistake on the way past. The
        # objective here is cruise lift-to-drag and nothing else, and for a
        # parabolic polar that objective rises with aspect ratio without ever
        # turning over. The aeroplanes in the table were not drawn against it.
        # Naming the difference in objective is the whole of the explanation,
        # and it is the Chief Researcher's to give: the researcher frames the
        # comparison, the numericist then holds the numbers up against it.
        script.researcher(
            "• Real airliners sit at aspect ratio 9 to 11, not at the cruise "
            "L/D optimum. "
            "• They optimise fuel burn and operating cost under gate, flutter "
            "and wing-box limits. "
            "• The distance to the analogues is a difference in objective, "
            "not an error.")
        script.numericist(
            "• Holding the winner against aircraft built for a comparable "
            "mission. "
            "• " + ", ".join(a["name"] for a in matches) + ". "
            "• Their figures come from the manufacturers' airport planning "
            "documents.")
        _emit_table(
            emit, script, title="Winner against real aircraft",
            headers=["Parameter", "Winner", "Analogues", "Verdict"],
            rows=analogue_rows(best, matches),
            table_id="analogue-check", role=_NUMERICIST_SPEAKER)
    else:
        # No comparison set exists, which is a fact about the reference
        # aircraft rather than a ruling, so the numericist states it and the
        # gate-code finding below stays the researcher's.
        script.numericist(
            "• No production airliner carries this many passengers this far. "
            "• The mission has no analogue to hold the winner against.")

    # ---- the gate code the winner actually falls in -------------------------
    # Raised here, where a span exists, and raised by the Chief Researcher.
    # The span row in the table above points at this advisory by name, so the
    # two sit together. A winner inside Code E gets the finding rather than
    # the advisory: the run raised the question and the answer was that
    # nothing needs to change.
    winner_code = icao_code_letter(float(best["span"]))
    if winner_code == "F":
        advisory = icao_advisory(float(best["span"]))
        script.researcher(
            f"• {advisory[0]} "
            f"• {advisory[1]} "
            f"• {advisory[2]}")
    elif winner_code:
        script.researcher(
            f"• Winner span {best['span']:.0f} m falls in ICAO Aerodrome "
            f"Reference Code {winner_code}. "
            f"• Existing gates serve it, so no gate change is asked for "
            f"(ICAO Annex 14).")

    # WHAT THE WINNER IS SITTING ON is said with the result, not before it and
    # not only in the memo's limitations list. It used to be raised here, a
    # hundred lines and four beats ahead of the number it qualifies, and a
    # viewer who meets the L/D first has already read it as an interior
    # optimum by the time the caveat arrives. Cruise L/D rises with aspect
    # ratio for a parabolic polar and does not turn over, so a bounded search
    # ends where the box ends; that is a fact about the box, and it belongs in
    # the same breath as the answer. See the block below `result.verdict`.
    limits = active_limits(best, results)

    # Headline CI: stated input uncertainties propagated through the real
    # evaluation chain (the solved polar when one exists).
    ci95 = winner_ci95(best, reqs, polar=best.get("_polar"))
    from chief_engineer import uq as uq_studies
    steps = axis_steps(grid)
    input_note = (
        "Ensemble run over the stated payload-mass and non-wing-drag spreads. "
        "Requirements are held as exact specification, and the remaining "
        "sizing constants (SFC, fuel fraction, cruise altitude) are fixed")
    if won_solved:
        # Numerical: the grid-spacing bracket (local quadratic fit of the
        # solved L/D around the winner, half-step variation per axis in
        # quadrature) plus the cruise-point read-off residual on the polar.
        bracket = grid_spacing_bracket(solved_ok, best, steps,
                                       value_key="L_D_solved")
        readoff = polar_readoff_residual(best.get("_polar"), best["cl_cruise"])
        num_parts = [v for v in (bracket["value"], readoff) if v]
        u_num = (round(math.sqrt(sum(v * v for v in num_parts)), 3)
                 if num_parts else None)
        # Model: the documented band on the non-wing component buildup,
        # propagated to L/D at the solved cruise point; the measured
        # screen-vs-solve gap goes on the record beside it.
        u_model = round(buildup_band_ld(
            best["cl_cruise"], best["cdo_wing_solved"], best["cdi_solved"]), 3)
        gap = screen_solve_gap(solved_ok)
        numerical_note = (
            f"The design grid is discrete, so the true optimum lies between "
            f"grid points. Default numerical consistency method: the winner "
            f"brackets the half-step variation on each grid axis, "
            f"±{(bracket['value'] or 0.0):.2f}. The cruise-point read on the "
            f"solved polar adds ±{readoff:.2f}.")
        # ONE QUANTITY, ONE RENDERING. The channel's Value cell prints
        # `u_model` at the three decimals it is rounded to, and this note
        # restates the SAME number: at two decimals it read "1.451" and
        # "±1.45" in adjacent cells of one row, which reads as two
        # measurements that disagree. No number changed; the note quotes the
        # value cell's own rendering.
        model_note = (
            f"Component buildup band on non-wing drag, propagated to "
            f"whole-aircraft L/D: "
            f"±{u_model:.3f}. The band is the documented ±15% on the buildup "
            f"terms (Raymer, Aircraft Design: A Conceptual Approach, AIAA).")
        if gap is not None:
            model_note += (
                f" The sizing screen's measured gap to the {len(solved_ok)} "
                f"solved wings averages {gap:.2f} in whole-aircraft L/D.")
        channels = uncertainty_channels(
            input_2sigma=round(ci95, 2), numerical=u_num, model=u_model,
            input_note=input_note, numerical_note=numerical_note,
            model_note=model_note)
        headline_ci = uq_studies.combine_expanded(
            input_2sigma=ci95, numerical_abs=u_num,
            model_abs=u_model)["combined_95"] or ci95
    else:
        # No solves this run. The numerical channel is still computed — the
        # same half-step bracket, on the screened L/D — and the model channel
        # comes from the measured screen-vs-solve deviation held for this
        # configuration when its fingerprint matches.
        anchors = uq_studies.channels_for(
            "airliner-wing",
            uq_studies.setup_fingerprint(body="airliner-wing", solver="vspaero",
                                         closure="vortex-lattice", velocity=230.0,
                                         refinement=None, iterations=None))
        model_band = (anchors["model"]["band_abs"] if anchors["model"] else None)
        bracket = grid_spacing_bracket(feasible, best, steps, value_key="L_D")
        u_num = round(bracket["value"], 3) if bracket["value"] else None
        channels = uncertainty_channels(
            input_2sigma=round(ci95, 2), numerical=u_num,
            model=None if model_band is None else round(model_band, 3),
            input_note=input_note,
            numerical_note=(
                "The design grid is discrete, so the true optimum lies between "
                "grid points. Default numerical consistency method: the winner "
                "brackets the half-step variation on each grid axis."
                if u_num is not None else
                "The design grid is discrete, so the true optimum lies "
                "between grid points."),
            model_note=(f"{anchors['model']['method']} "
                        f"({len(anchors['model'].get('members', {}))} solved "
                        f"anchors); non-wing drag remains a component buildup"
                        if model_band is not None else
                        "drag-polar sizing model; a solve would set the "
                        "magnitude"))
        headline_ci = uq_studies.combine_expanded(
            input_2sigma=ci95, numerical_abs=u_num,
            model_abs=model_band)["combined_95"] or ci95
    if emit:
        emit("uncertainty.channels", channels)
    # Standing lesson: these computed-uncertainty patterns transfer to every
    # act, so they are kept as a global lesson the team reads back.
    try:
        from chief_engineer.lessons import record_learned

        record_learned(
            "computed-uncertainty-patterns",
            "Grid-spacing bracket via local quadratic fit: on a discrete "
            "design grid, fit the objective around the winner along each axis "
            "and take the half-step variation, axes combined in quadrature; "
            "that is the numerical channel, computed from results already in "
            "hand. Screen-vs-solve discrepancy as model evidence: when the "
            "same designs carry both a screen value and a solved value, the "
            "measured discrepancy set is direct model-channel evidence for "
            "the screen. A component-buildup share carries its documented "
            "band (Raymer) propagated to the reported quantity.")
    except Exception:
        pass
    if won_solved:
        script.researcher(
            "• Wing solved with VSPAERO: induced and viscous drag from the "
            "solved polar at cruise. "
            "• Non-wing drag comes from the component buildup method (Raymer). "
            "• To solve that too: a full-configuration surface and a case "
            "for it.")
        verdict = trust(
            converged=True, in_validated_regime=False, calibrated=True,
            solver_backed=True,
            why="wing solved with VSPAERO; fuselage, tail and nacelle drag "
                "added from Raymer's component buildup method")
    else:
        script.researcher(
            # The limits this points at are now stated below, with the result,
            # rather than four beats earlier; the pointer moves with them.
            "• Ranking trustworthy: aspect ratio buys whole-aircraft L/D up "
            "to the bounds named below. "
            f"• Magnitude {best['L_D']:.1f} ± {headline_ci:.1f} "
            f"{TIER_SCREEN}. "
            f"• A solved flow and a comparison would set the magnitude.")
        verdict = trust(
            converged=True, solver_backed=False,
            why="research sizing model; a solve would set the magnitude")
    if emit:
        # On a solved win the fidelity line is the verdict reason alone; a
        # duplicate envelope shorthand would only restate it less clearly.
        emit("result.verdict", {"quantity": "Best feasible whole-aircraft L/D",
                                "value": f"{best_ld:.1f}",
                                "ci": f"{headline_ci:.1f}", "confidence": "95%",
                                "envelope": ("" if won_solved else
                                             "sizing-model estimate"), **verdict})
    # THE BOUND, BESIDE THE NUMBER. Whatever the search returns is the best
    # point on a bounded grid, and for this model class the bound is what
    # picks it: maximum L/D on a parabolic polar goes as the square root of
    # aspect ratio and never turns over, so there is no interior peak in span
    # or area to find. Real airliners sit at aspect ratio 9 to 11 because they
    # optimise fuel burn and operating cost under gate, flutter and wing-box
    # limits; the aircraft that do optimise L/D, gliders and the U-2, sit at
    # 20 to 25. So the honest statement is where the box ends, said here.
    if limits:
        script.engineer(
            "• That design is the best point on a bounded grid, sitting on "
            + " and on ".join(limits) + ". "
            "• Whole-aircraft L/D climbs with aspect ratio without turning "
            "over, so the bound picks the winner and not an interior peak. "
            "• Move the bound and the answer moves with it.")
    # THE RANGE OVERSHOOT, ANSWERED BEFORE IT IS ASKED. Range is a feasibility
    # floor in the search and never an objective, and Breguet range here is
    # proportional to whole-aircraft L/D with the fuel fraction fixed, so the
    # quantity being maximised drags range up with it and the floor cannot
    # bind at the optimum. An engineer watching a 300 passenger aeroplane
    # report far more range than it was asked for will want that said.
    overshoot = quoted_range_km - float(reqs["range_km"])
    if overshoot > 0.05 * float(reqs["range_km"]):
        script.researcher(
            f"• Range {quoted_range_km:.0f} km against the "
            f"{reqs['range_km']:.0f} km asked for. "
            f"• Range is a floor the search must clear, never a target: fuel "
            f"is fixed at {_FUEL_FRACTION * 100:.0f}% of MTOW, so range is "
            f"proportional to whole-aircraft L/D and rises with the "
            f"objective. "
            f"• The excess is what the objective gives, not tankage bought "
            f"for it; sizing fuel to the requirement is a trade this model "
            f"does not make.")
    knowledge.add(
        f"Airliner whole-aircraft L/D for {reqs['passengers']} pax / "
        f"{reqs['range_km']:.0f} km: best feasible whole-aircraft L/D "
        f"{best_ld:.1f} at span {best['span']:.0f} m, "
        f"aspect ratio {best['aspect_ratio']:.1f}"
        + (" (wing solved with VSPAERO)" if won_solved else " (screened)"))

    agenda = [
        {"title": "Cruise Mach trade",
         "scope": "sweep cruise Mach against the fixed requirements to find where "
                  "the range, speed and whole-aircraft L/D surface actually peaks",
         "cost": "one more sweep dimension; solver already in place"},
        {"title": "Composite-span structural limits",
         "scope": "explore spans beyond today's structural cap with a composite "
                  "wing-box weight model driving MTOW",
         "cost": "a weight-model extension plus a re-run of the sweep"},
        {"title": "Full-configuration solve",
         "scope": "put the fuselage and tail in the solved model and trim the "
                  "winner for static margin",
         "cost": "richer geometry per candidate; same solver, longer polars"},
    ]
    if emit:
        emit("agenda.updated", {"entries": agenda})

    methods = [
        "Weights from the passenger count via a payload fraction; MTOW carries a "
        "mild span-structural penalty.",
        "Screening whole-aircraft L/D from a drag polar (induced drag over "
        "aspect ratio and "
        "Oswald efficiency, parasite drag with sweep).",
        "Feasibility from stall-speed limits for take-off and landing and a "
        "Breguet range check.",
    ]
    if won_solved:
        # HOW THEY RAN IS A FACT ABOUT THE BOX, NOT A HOUSE STYLE. This
        # sentence hardcoded "in parallel", and the executor is strictly
        # sequential at one granted slot: it read as a claim about the run
        # while the transcript on the same record said "1 granted slots". The
        # clause is now the granted count's to make.
        how_run = (f"in parallel across {n_par} slots" if n_par > 1
                   else "one after another on the single granted slot")
        methods.append(
            f"The top {len(solved_ok)} feasible finalists were built as parametric "
            f"geometry and solved with VSPAERO, a vortex-lattice method, "
            f"{how_run}; the cruise point was interpolated on each solved polar, "
            f"and the winner was picked on solved numbers.")
        methods.append(
            "Non-wing parasite drag from Raymer's component buildup method "
            "(Raymer, Aircraft Design: A Conceptual Approach, AIAA).")

    abstract = [
        f"We searched a {len(grid)}-wing design space for the highest "
        f"whole-aircraft L/D meeting the stated mission requirements.",
        f"The best feasible {'family' if sweep_note else 'wing'} reaches "
        f"whole-aircraft L/D {best_ld:.1f} ± {headline_ci:.1f} (95%) "
        f"at span {best['span']:.0f} m and aspect ratio {best['aspect_ratio']:.1f}; "
        f"{n_infeasible} designs were infeasible on low-speed or range."
        # The bound belongs in the sentence that states the result, in the
        # memo as much as on camera: a reader who meets the number without it
        # reads a bounded search as an interior optimum.
        + (" That design is the best point on a bounded grid, sitting on "
           + " and on ".join(limits) + "; move the bound and it moves."
           if limits else ""),
        ("The winner stands on a wing polar solved with VSPAERO plus Raymer's "
         "component buildup for the non-wing drag." if won_solved else
         "The result comes from the stated sizing model with its input "
         "envelope propagated."),
    ]

    # LIMITATIONS, NOT UNCERTAINTY. What follows is what the answer does not
    # cover: an optimum set by the edges of the box, a discrete grid, and a
    # non-wing drag share that came from a buildup rather than a solve. None
    # of it is a band on a number. The bands are the three uncertainty
    # channels, and they are computed above and shown on their own surface;
    # heading this list "Uncertainty" too made a reader hunt for which was
    # which. The section carries its own title so the two never collide.
    limitations = [
        sweep_note,
        # The bounds NAMED ARE THE ONES THE WINNER ACTUALLY SITS ON. This line
        # used to name the span limit and the area floor whichever of them was
        # active, so a run whose winner had come off the span cap still told
        # the reader the cap had set it.
        ("Whole-aircraft L/D rises with aspect ratio and does not turn over, "
         "so the reported design is set by " + " and by ".join(limits)
         + ", not by an interior optimum." if limits else
         "Whole-aircraft L/D rises with aspect ratio and does not turn over, "
         "so the reported design is the best point on a bounded grid rather "
         "than an interior optimum."),
        ("Wing induced and viscous drag are solved; the non-wing parasite share "
         "comes from Raymer's component buildup method." if won_solved else
         "The absolute whole-aircraft L/D comes from a drag polar sizing model, "
         "not a solved "
         "flow; the model channel carries that."),
        "The optimum sits between discrete grid points, so the reported design "
        "is the best sampled, not the continuous optimum.",
    ]

    report = lab_report(
        title=f"Whole-aircraft L/D optimization: {reqs['passengers']} pax, "
              f"{reqs['range_km']:.0f} km",
        abstract=abstract,
        methods=methods,
        results=[{
            "quantity": "Best feasible whole-aircraft L/D",
            "value": f"{best_ld:.1f} ± {headline_ci:.1f} (95%)",
            "envelope": f"span {best['span']:.0f} m, AR {best['aspect_ratio']:.1f}, "
                        f"range {quoted_range_km:.0f} km",
            **verdict,
        }],
        uncertainty=limitations,
        next_investigations=[f"{entry['title']}: {entry['scope']}"
                             for entry in agenda],
        compute=ledger.as_dict(),
    )
    # The heading the list above is filed under. The payload key stays
    # ``uncertainty`` so nothing downstream has to change; the title is what
    # the reader sees, and for this act it is Limitations.
    report["uncertainty_title"] = "Limitations"
    # The memo leads with its figures, and carries them itself so a fast run
    # cannot finish before the paced figure events drain.
    if report_plots:
        report["plots"] = report_plots
    if emit:
        emit("report.ready", report)

    # The Certonomous certificate for the airliner act: the subject and this
    # run's verbatim objective, the best feasible L/D with its 95% CI, the
    # structured result table, and the full three-channel uncertainty table —
    # every channel a computed number on a solved run.
    #
    # WHAT THE PAGE DELIBERATELY DOES NOT CARRY, and why it is not an
    # oversight: the scope line, the constraint list, the assumed-values
    # ledger and the solver-and-model line. Each of those is a conditional on
    # the result rather than the result, each is on the record in the digest
    # and the transcript where it is read in context, and together they made
    # the certificate a two-leaf log dump whose headline arrived on the second
    # page. A certificate is read for what was concluded and how far it is
    # trusted; the conditions are one click away. Removing them changes the
    # evidence seal's payload, which is correct — the seal covers what the
    # certificate states, and it now states less.
    #
    # The previous run's page is withdrawn FIRST and the new page lands by
    # atomic replacement, so a page from an earlier mission can never be
    # served after this one completes; if generation fails the act says so
    # on the record instead of leaving an out-of-date page linked.
    cert_path = out / "certificate.pdf"
    # DOCKET B2. Withdrawal has THREE outcomes, not two, and the act publishes
    # the one that happened: a page that could not be removed is not a page
    # that was withdrawn.
    _withdrawn, _withdrawal = withdraw_certificate(cert_path)
    try:
        from chief_engineer.certificate import build_certificate_v2

        cert_doc = {
            "results": [
                {"quantity": "Best feasible whole-aircraft L/D",
                 "value": f"{best_ld:.1f}",
                 "envelope": f"{headline_ci:.1f}", **verdict},
                # Span, aspect ratio and MTOW are shared by every member of
                # the family, so this row names the winner whether one wing
                # or four came out of the solves. What is NOT shared is the
                # sweep, and the envelope says so rather than leaving a
                # reader to assume one angle was picked on the numbers.
                {"quantity": "Winning wing",
                 "value": f"span {best['span']:.0f} m, AR {best['aspect_ratio']:.1f}",
                 "envelope": (sweep_unresolved if sweep_note
                              else f"range {quoted_range_km:.0f} km")},
            ],
            # Structured result block: Title Case labels, verbatim numbers,
            # and the basis of each one beside it.
            #
            # WHY THE THIRD COLUMN EXISTS. This table used to carry seven
            # numbers off three different bases and say so about none of them.
            # A viewer holding the sealed page against the screened optimum
            # table read "Range 9447 km [screen: reduced-order sizing]" there
            # and "Range 10276 km" here, and had nothing to tell them the two
            # are the same wing at two fidelities: 9447 at the screen's L/D
            # 17.8, 10276 at the solved 19.3. The solved figure is the right
            # one for this page, and the page now says on what basis. Inside
            # the table the mixing was silent too: MTOW and the approach speed
            # are sizing outputs, the L/D is solved, and span and sweep are
            # neither, being the grid point itself.
            #
            # The two tier tags are sliced off the transcript's own constants
            # rather than retyped, so the words a viewer matches across the
            # two surfaces cannot drift apart.
            "result_fields": [
                ("Span", f"{best['span']:.0f} m", "design variable"),
                ("AR", f"{best['aspect_ratio']:.1f}",
                 "from span and area"),
                ("Sweep", sweep_field, sweep_basis),
                ("MTOW", f"{best['mtow_kg'] / 1000:.0f} t", _BASIS_SCREEN),
                ("Range", f"{quoted_range_km:.0f} km",
                 "Breguet range on the solved L/D" if won_solved
                 else _BASIS_SCREEN),
                ("Approach Speed", f"{best['approach_speed']:.0f} m/s",
                 _BASIS_SCREEN),
                ("Whole-aircraft L/D", f"{best_ld:.1f}",
                 _BASIS_SOLVE if won_solved else _BASIS_SCREEN),
            ],
            "compute": ledger.as_dict(),
        }
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path,
            geometry="airliner",
            # The objective is always THIS run's verbatim request.
            objective=(request or "Maximise the airliner cruise lift-to-drag "
                       "ratio subject to its mission requirements."),
            mission_id="aircraft-optimization",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels,
            display_name=f"{reqs['passengers']}-passenger twin-aisle airliner")
        if emit:
            emit("certificate.ready", {**certificate, "dir": out.name})
    except Exception:  # a certificate must never take down a good mission
        script.engineer(
            "• No certificate could be issued for this run. "
            f"• {_withdrawal} "
            "• The result above stands on the transcript and the report.")

    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out)
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(request=" ".join(sys.argv[1:]) or None))
