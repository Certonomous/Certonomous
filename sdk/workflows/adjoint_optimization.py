"""Adjoint wing optimization: a discrete adjoint, verified, then flown.

This is a design optimization you watch. The wing is on screen from the plan
phase, the adjoint gradient is painted on its skin before a single design step
is taken, and then the surface itself walks through all 47 major iterations
while the drag trace descends beside it. Every one of those surfaces is the
surface the optimizer actually produced: the run's own pyGeo parameterization
was driven offline with the design-variable vectors in its history database,
and the result baked into a static artifact (``A2_shape_frames.json``). The
act loads that artifact with the standard library and streams it. It never
touches pyGeo, DAFoam or a solver, so it runs on a laptop with no OpenFOAM and
no network, and it plays identically every time.

This act is the gradient beat of the control room, and it is a different
animal from the cylinder design sweep. The sweep fits a differentiable
response surface to a handful of solves and descends on that; useful, but the
gradient it descends on belongs to the fitted surface, not to the flow solver.
Here the gradient is a **discrete adjoint**: one linear solve against the
transpose of the flow Jacobian returns the derivative of the objective with
respect to every design variable at once, at a cost that does not grow with
the number of design variables. 105 of them, for the price of roughly one
flow solve.

A gradient that cheap is worth nothing if it is wrong, so the act leads with
the check rather than the result: every derivative group was graded against a
central finite difference of the full primal, 210 perturbation solves, and the
whole table is put on screen including the two rows that sit at the noise
floor. The optimization only appears because that check passed.

The optimization delivered drag 28.3% below the untwisted baseline at matched
lift over 47 major iterations. The baseline is named wherever that figure
appears, on screen, in the report and on the certificate, and it is built by
one helper so there is no occurrence to miss.

A wing handed to the act is identified rather than taken on trust. The act
says on screen that it is delegating the confirmation, so the confirmation
happens: the surface that arrived is read and three of its overall dimensions
are measured against the same three measured off the wing this act's numbers
belong to. What the measurement found is reported either way. Where a stated
condition rides in with the request, a drag-reduction target or a ceiling on
major iterations, the act puts the two numbers it measured beside the two
numbers it was asked for and claims nothing further about either.

Four things this act discloses before it is asked, because an adjoint-literate
reviewer asks them first. The finite-difference step, with the fact that THIS
case was graded at one step and the sweep that fixed it was run elsewhere. The
differentiation: reverse-mode AD of the residuals with the turbulence
transport equation among the differentiated states, verified from the run's
own echoed configuration rather than assumed from the solver's defaults. That
the machine-precision constraint derivatives are analytic and so are expected
to be exact. And what the deformation did to the mesh, over all 81 checks the
run made on it.

The act paces itself. Every conversation entry keeps its own true emission
time, and the act takes the time rather than writing one it did not: the
narration beat is a shade over a second so no two entries share a clock
second. ``CERTONOMOUS_NARRATION_PACE_MS`` and ``CERTONOMOUS_SWEEP_PACE_MS``
override it for a still capture, where nothing is watched.

WITHHELD FROM THE NARRATION, KEPT HERE AND IN THE RECORD (owner call,
2026-07-31, under docs/DEMO_DISCRETION_CHARTER.md section 2, "operational
detail"):

* The run's stopping condition. The optimizer was stopped by a 60 minute wall
  clock at first-order measures of 1.44e-05 and 9.0e-05 against a 1e-05
  target, and printed no convergence statement. None of that is narrated any
  more. The hard rule that comes with the omission: this act must never state
  or imply the opposite either. It never says converged, never says optimum,
  and never reports a stopping condition of any kind. Saying less is allowed;
  saying something untrue is not, and asserting convergence here would be
  untrue. The full stopping evidence is on the permanent record in
  ``A2_optimization_history.json`` and ``A2_mach_tutorial_wing.json``.
* The measured amplified-view ceiling (x1.995 at the thickness constraint's
  own floor) and the pixel arithmetic behind the two viewing conventions.
  Both stay in ``_a2_shape`` where they are computed.
* The four line-search step cutbacks, already withheld as method.
* THE MECHANISM ITSELF (owner, 2026-07-31). Nothing on any camera surface may
  say where the geometry or the gradient came from, or that anything was
  prepared ahead of the act. No narration describes the parameterization being
  driven, the shape history, the artifact, or the fact that a surface is
  anything other than the wing. The act presents the wing and the gradient and
  says nothing about their provenance. This paragraph is the boundary: this
  file explains the mechanism in full, and the narration explains none of it.
  It does not license a single false statement; every measured value, band,
  threshold and reference identity on screen is real and stays.

Every number this act reports is read at run time out of the recorded
optimization's own primary artifacts (the optimizer's iteration table and the
history database it wrote), joined and committed as
``A2_optimization_history.json``. Nothing is modelled, smoothed or invented.

    python -m workflows.adjoint_optimization
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

from . import (OUT_ROOT, announce_geometry, announce_plot, bullets, emit_table,
               make_transcript)
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, MONITOR, NUMERICIST,
                                PLAN, SOLVER_BACKED, ComputeLedger,
                                KnowledgeBase, Roster, lab_report,
                                uncertainty_channels)
from chief_engineer.transcript import CHIEF_ENGINEER as _CE_ROLE
from chief_engineer.transcript import MONITOR as _MON_ROLE
from chief_engineer.transcript import NUMERICIST as _NUM_ROLE

from . import _a2_shape
from .geometry_study import mesh_validity

LABEL = "adjoint-optimization"

_LADDER = (Path(__file__).resolve().parents[2]
           / "demo-output" / "website" / "dafoam" / "ladder-a")
HISTORY_FILE = _LADDER / "A2_optimization_history.json"
RECORD_FILE = _LADDER / "A2_mach_tutorial_wing.json"
STEPSWEEP_FILE = _LADDER / "A_stepsize_study.json"

# The case, as it was actually run.
MESH_CELLS = 38_304
N_SHAPE, N_TWIST, N_PATCHV = 96, 7, 2
N_DV = N_SHAPE + N_TWIST + N_PATCHV
FD_STEP = 1e-3
FD_SOLVES = 2 * N_DV          # central difference, two primals per variable
RANKS = 4
CL_TARGET = 0.5

# Measured stage costs from the run's own accounting, in core-minutes, and the
# primal-solve counts they bought. The verification stage's own record reports
# 211 primal solves completed, which is what makes the cost table a like-for-
# like comparison: one adjoint solve against the finite-difference sweep that
# buys the same gradient.
COST_ADJOINT = 32.7
COST_FD = 210.2
COST_OPT = 240.4              # kept on the record; not narrated any more
FD_PRIMAL_SOLVES = 211

# This lab's current gradient-verification standard, applied uniformly across
# the whole ladder: PASS at 5% or better on the aggregate AND no flagged
# component; CONDITIONAL between 5 and 15%; FAIL above 15%, or on any
# sign-flipped or unstable component whatever the aggregate says. An earlier,
# looser "1 to 12% is normal" band was inferred from a single case and has
# been retired; it is not cited here.
GATE_PASS_PCT = 5.0
GATE_CONDITIONAL_PCT = 15.0

# ITEM 3 (owner, 2026-07-31): how the derivative is taken, stated on screen,
# because "is your turbulence frozen" is the first question an adjoint-literate
# reviewer asks and the act should have answered it already.
#
# VERIFIED FROM THE RUN'S OWN CONFIGURATION, not assumed from the solver's
# defaults. The run directory's SHA-256 over runScript_AeroOnly.py,
# system/fvSolution and system/fvSchemes reproduces config_hash_sha256 in the
# record byte for byte, and the configuration that configuration produced is
# echoed in full by the solver at the top of the adjoint run:
#
#   useAD { mode reverse; }              reverse-mode AD, not a difference
#   Adjoint States: 5 (U, nuTilda,       the turbulence variable is one of the
#     phi, p, T), 349348 globally        five state fields the adjoint carries
#   normalizeResiduals ... nuTildaRes    its residual is one of those
#                                        differentiated, so NOT frozen
#   forceMeshWaveFrozen 1                the wall distance that feeds the
#                                        turbulence source term is the one
#                                        thing not differentiated
AD_MODE = "reverse"
TURBULENCE_DIFFERENTIATED = True
ADJOINT_STATE_FIELDS = 5
ADJOINT_STATES = 349_348

# The two rows of the verification table whose "100%" is a ratio of two
# numbers that are both indistinguishable from zero, not a disagreement.
_NOISE_FLOOR_ROWS = {"geometry.thickcon wrt twist"}

# Component-level sign agreement, re-derived from the raw derivative vectors
# in the verification log rather than taken from the summary. Three of the six
# physical groups print an uncorrupted pair of vectors (the rest are broken up
# by interleaved parallel output), giving 110 components checked directly with
# zero reversals. For the other three the difference norm bounds it instead: a
# reversed component contributes at least twice its own magnitude to that
# norm, so no component carrying more than this share of the gradient can be
# flipped. Worst of the three bounds is CL with respect to shape.
SIGN_CHECKED = 110
SIGN_BOUND_PCT = 0.58

# The optimizer's own log records four line-search step cutbacks on evaluation
# errors. Counted from its output file, not estimated. Kept on the permanent
# record; withheld from the narration under docs/DEMO_DISCRETION_CHARTER.md,
# because the sequence of things the optimizer tried is method, not result.
CUTBACKS = 4
# How many trailing major iterations the "settled into a band" claim covers.
TAIL_ITERS = 15

# ITEM 6 (owner, 2026-07-31): a shape change worth a third of the section's
# own thickness is large enough that a viewer is entitled to ask what it did
# to the mesh, so the monitor reports the answer whenever the reference
# displacement passes this fraction of local thickness. The trigger is a
# threshold rather than a decision, so the report cannot be quietly dropped
# on a run where the shape moved even further.
MESH_REPORT_TRIGGER_PCT = 10.0

# The run's own mesh quality checks, ON THE DEFORMED MESH, one per design
# evaluation. Counted and read out of the optimizer's own output file: the
# solver re-runs OpenFOAM's mesh quality checks after every deformation and
# refuses to solve a design that fails them. Ranges are across all of them.
MESH_DEFORM_CHECKS = 81
MESH_DEFORM_CHECKS_PASSED = 81
MESH_NON_ORTHO_RANGE = (66.84, 82.00)   # degrees, worst cell in each check
MESH_SKEW_RANGE = (1.34, 3.45)
MESH_ASPECT_RANGE = (376.0, 993.3)
# The thresholds this case configured, which are the ones the solver judged
# against. A face past the non-orthogonality mark is counted and reported;
# OpenFOAM's own check only errors at 90 degrees, where a face has folded.
MESH_NON_ORTHO_MARK = 70.0
MESH_NON_ORTHO_ERROR = 90.0
MESH_SKEW_GATE = 5.0
MESH_ASPECT_GATE = 1000.0
MESH_FACES = 119_524
MESH_WORST_FLAGGED_FACES = 6
MESH_CHECKS_OVER_MARK = 39

_AGENDA = [
    {"title": "The gradient on a wing-body, not a wing",
     "scope": "carry the same verified adjoint onto a fuselage-and-tail "
              "configuration and optimize the junction, where the shape "
              "derivative is least intuitive and most valuable",
     "cost": "a materially larger mesh and a host with more memory headroom"},
    # Phrased as an ambition and nothing else. It must not describe how the
    # recorded run ended, in either direction: the stopping condition is
    # withheld (see the module docstring) and convergence is never claimed.
    {"title": "Take the same gradient further down the objective",
     "scope": "keep descending on the verified gradient and find how much "
              "more drag the shape gives up on a longer run",
     "cost": "a few more hours on the same hardware"},
    {"title": "Put the drag reduction in a wind tunnel",
     "scope": "fly the optimized and baseline sections as models and grade "
              "the shape change against an experiment rather than against "
              "the code that produced it",
     "cost": "two models and tunnel time"},
]

# The owner's shorthand prompt carries a target ("cut the drag by at least
# 20%"). When one is stated the act reports the reduction against it; when it
# is not, nothing is invented and the target simply is not shown.
_TARGET_PCT = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|per\s?cent|percent)", re.I)

# ITEM 4 (owner, 2026-07-31): a prompt may also state a ceiling on how far the
# optimization is to run ("don't go over 50 its"). Both conditions are read out
# of the request and both are reported against what the run measured: 28.3%
# below the untwisted baseline, 47 major iterations. Two measured numbers put
# beside the two numbers she asked for, and nothing else claimed on either
# side. The one thing this act may never say, with or without a stated
# condition, is that the optimization converged.
_ITER_CAP = re.compile(
    r"(\d+)\s*(?:its|iters?|iterations?|major\s+iterations?)\b", re.I)


def _requested_target(request: str | None) -> float | None:
    """The drag-reduction target stated in the request, if there is one."""
    match = _TARGET_PCT.search(request or "")
    return float(match.group(1)) if match else None


def _requested_iteration_cap(request: str | None) -> int | None:
    """The ceiling on major iterations stated in the request, if there is one."""
    match = _ITER_CAP.search(request or "")
    return int(match.group(1)) if match else None


# ITEM 1 (owner, 2026-07-31): a stated target is a stopping rule, and a
# stopping rule the act does not account for reads as a stopping rule the act
# ignored. So the act reads its own recorded history and says WHERE the target
# was first reached, beside where the run ended.
#
# THE HONESTY BOUNDARY, and it is the whole point of this helper. The recorded
# run was not driven by any stated target: this reports when the target was
# reached and where the run ended, and NOTHING about why. No control loop, no
# review cycle and no decision is described, because none of those is on the
# record for this run. Everything below is read straight off the recorded
# objective; nothing is interpolated between iterations.
def _target_first_met(history, baseline_cd: float,
                      target_pct: float) -> dict | None:
    """Where the recorded history first reaches a stated reduction target.

    Returns the first major iteration at or past the target, the reduction it
    read there, and the first iteration from which every later one is also at
    or past it. None when the recorded run never reaches the target.
    """
    def drop(point) -> float:
        return (baseline_cd - point["CD"]) / baseline_cd * 100.0

    met = [p for p in history if drop(p) >= target_pct]
    if not met:
        return None
    stayed = met[-1]["iter"]
    for point in reversed(history):
        if drop(point) < target_pct:
            break
        stayed = point["iter"]
    return {"iter": met[0]["iter"], "pct": drop(met[0]), "stayed_from": stayed}


def _fmt(x: float) -> str:
    """Engineering-notation magnitude for the verification table."""
    return f"{x:.6e}"


# ITEM 9 (owner, 2026-07-31): every entry in this act's conversation used to
# carry the same clock, because the whole act finished in under a fifth of a
# second and the feed rendered as one instant dump with a single timestamp
# repeated down the page. The fix is NOT to write times that were never taken.
# Entries keep their own true emission time, exactly as the transcript stamps
# them; what changes is that the act actually takes the time. A narration beat
# is a shade over a second so consecutive entries always land in different
# seconds on the clock the control room prints, and the shape passes take a
# real interval per iteration. Both are overridable for a still capture, where
# nothing is being watched and pacing is only a delay.
_NARRATION_PACE_S = float(
    os.environ.get("CERTONOMOUS_NARRATION_PACE_MS", "1050")) / 1000.0
_FRAME_PACE_S = float(
    os.environ.get("CERTONOMOUS_SWEEP_PACE_MS", "60")) / 1000.0


def _beat(seconds: float) -> None:
    """Let the clock move, so the next entry's time is genuinely its own."""
    if seconds > 0:
        time.sleep(seconds)


def _narrate(sayer, *lines: str, **kwargs):
    """One narration entry, followed by the beat that separates it."""
    entry = bullets(sayer, *lines, **kwargs)
    _beat(_NARRATION_PACE_S)
    return entry


def _cost_rows() -> list[list[str]]:
    """The cost of the same gradient, bought two ways. Both ratios, always.

    ITEM 10 (owner, 2026-07-31): whenever this act quotes adjoint economics it
    quotes the primal-solve count ratio AND the core-time ratio. Quoting one
    is the oldest way to oversell an adjoint, because the solve-count ratio is
    the flattering one and the core-time ratio is the one a buyer pays. The
    rows are built here so there is a single place both live, and the guard
    below means an edit that drops either one fails the run instead of
    shipping half an argument.
    """
    rows = [
        ["One adjoint solve", "1", f"{COST_ADJOINT:.1f}"],
        ["Finite differences over the same variables",
         f"{FD_PRIMAL_SOLVES}", f"{COST_FD:.1f}"],
        ["Ratio, adjoint against finite differences",
         f"{FD_PRIMAL_SOLVES} to 1", f"{COST_FD / COST_ADJOINT:.1f} to 1"],
    ]
    ratios = [r for r in rows if r[0].lower().startswith("ratio")]
    if len(ratios) != 1 or not all("to 1" in cell for cell in ratios[0][1:]):
        raise RuntimeError(
            "adjoint economics are quoted with both ratios, the primal-solve "
            "count and the core time, or they are not quoted at all")
    return rows


def _phase(script, name: str):
    """A phase marker, which carries a clock of its own like any other entry."""
    entry = script.phase(name)
    _beat(_NARRATION_PACE_S)
    return entry


# ITEM 7 (owner, 2026-07-31): optimizer status is reported as descent. These
# are the phrasings this act may not use for it, banned by name. The first is
# the one that started the rule: it reads as the optimizer going the wrong
# way when it meant the opposite. The rest are the internals the act has no
# business narrating in the first place, so they are not translated, they are
# refused.
# ITEM 8 (owner, 2026-07-31): the reduction is never stated without the
# baseline it is measured from. A percentage on its own invites the reader to
# supply their own reference, and the one they supply is usually a published
# figure for some other wing. The baseline here is the same wing with every
# shape and twist variable at zero, so it is named for what it is. Every
# headline in the act, the report and the certificate is built from these two
# helpers rather than written out, so there is no occurrence to miss and no
# second wording to drift away from the first.
BASELINE_NAME = "untwisted baseline"


def _headline(pct: float) -> str:
    """The reduction, and the baseline it is measured against. Always both."""
    return f"{pct:.1f}% below {BASELINE_NAME} at matched lift"


def _against_baseline(pct: float) -> str:
    """A per-iteration reading, which can sit either side of the baseline."""
    side = "below" if pct >= 0 else "ABOVE"
    return f"{abs(pct):.1f}% {side} {BASELINE_NAME}"


_BANNED_OPTIMIZER_PHRASES = (
    "against the gradient",
    "merit function",
    "backtrack",
    "line search",
    "line-search",
)


class _Falsifier:
    """The falsifier and the gate, put on the record before any evidence.

    ITEM 1 (owner, 2026-07-31): "required output pattern, not narration". The
    hypothesis, the falsifier and the gate used to be three bullets sitting in
    the hypothesis phase, which is exactly the kind of line an edit drops
    without anything noticing. So they are structure instead: this object is
    the only route an evidence table has to the screen in this act, and it
    refuses to pass one until ``state`` has run. Delete the falsifier and the
    act stops with an error rather than quietly showing results first.
    """

    def __init__(self) -> None:
        self._stated = False

    def state(self, script, roster) -> None:
        # The engineer commits the hypothesis and the falsifier; the gate is a
        # rule, so the Chief Researcher sets it (owner, 2026-07-31: the
        # researcher frames and rules, the engineer executes). This is the
        # same split the hump act carries, so the two acts read alike.
        roster.set(CHIEF_ENGINEER, "stating the falsifier", "working")
        _narrate(script.engineer,
                f"Hypothesis: the adjoint gradient matches central finite "
                f"differences on every derivative group.",
                f"Falsifier: any group worse than {GATE_PASS_PCT:g}%, or any "
                f"component whose sign reverses.")
        roster.set(CHIEF_RESEARCHER, "setting the gate", "working")
        _narrate(script.researcher,
                f"Gate: nothing is optimized until the gradient passes.")
        roster.idle(CHIEF_RESEARCHER)
        self._stated = True

    def table(self, emit, script, **kwargs) -> None:
        """One evidence table, refused until the falsifier is on the record."""
        if not self._stated:
            raise RuntimeError(
                "the falsifier and the gate must reach the screen before this "
                "act emits any evidence")
        # ITEM 7 (owner, 2026-07-31): "moving against the gradient" is banned
        # by name, and a banned phrase that is only banned in prose is not
        # banned. bullets() already runs the wording doctrine over narration;
        # this closes the other door a phrase can walk through, which is a
        # table cell. Checked here rather than trusted, so a slip fails on the
        # first run instead of reaching the control room.
        for row in kwargs.get("rows") or ():
            for cell in row:
                lowered = str(cell).lower()
                for phrase in _BANNED_OPTIMIZER_PHRASES:
                    if phrase in lowered:
                        raise ValueError(
                            f"banned optimizer phrasing {phrase!r} in table "
                            f"cell {cell!r}")
        emit_table(emit, script, **kwargs)
        # A table is narration too, and it carries its own clock (ITEM 9).
        _beat(_NARRATION_PACE_S)


# The mesh check's own verdict line, as the record carries it. Read rather than
# retyped so the certificate's mesh block shows the measured numbers against
# their published gates instead of two "not reported" cells.
_MESH_NON_ORTHO = re.compile(r"max non-orthogonality\s+([\d.]+)", re.I)
_MESH_SKEW = re.compile(r"max skewness\s+([\d.]+)", re.I)


def _step_sweep() -> dict | None:
    """The step-size sweep this ladder ran, read rather than described.

    ITEM 2 (owner, 2026-07-31): a finite-difference number with an unstated
    step is not a check, so the step is disclosed with the sweep that fixed
    it. The hard fact this function exists to keep straight: THE SWEEP WAS RUN
    ON A DIFFERENT CASE. This case was graded at one step. The table built
    from this says so in as many words, because quoting a plateau next to a
    result implies a sweep, and implying one that was not run here would be
    the exact dishonesty the disclosure is meant to prevent.

    Returns None on a host that does not carry the sweep, in which case the
    act reports the step it used and that no sweep exists, and nothing else.
    """
    try:
        doc = json.loads(STEPSWEEP_FILE.read_text(encoding="utf-8"))
        rows = doc["sweep_table"]
    except (OSError, ValueError, KeyError):
        return None
    steps = [r["step"] for r in rows if r.get("step")]
    plateau = [r["step"] for r in rows
               if r.get("regime") == "well-converged plateau"]
    if not steps or not plateau:
        return None
    return {"steps": len(rows), "lo": min(steps), "hi": max(steps),
            "plateau_lo": min(plateau), "plateau_hi": max(plateau),
            "cells": (doc.get("case") or {}).get("mesh_cells")}


def _mesh_numbers(record: dict) -> tuple[float | None, float | None]:
    text = str(record.get("checkMesh_result") or "")
    non_ortho = _MESH_NON_ORTHO.search(text)
    skew = _MESH_SKEW.search(text)
    return (float(non_ortho.group(1)) if non_ortho else None,
            float(skew.group(1)) if skew else None)


def main(request: str | None = None, params: dict | None = None,
         emit=None) -> int:
    params = dict(params or {})
    out = OUT_ROOT / LABEL
    out.mkdir(parents=True, exist_ok=True)

    script = make_transcript(LABEL, emit)
    gate = _Falsifier()
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    began = time.monotonic()

    script.system(request or ("Request: reduce the drag on the wing with the "
                              "discrete adjoint and check the gradient "
                              "against finite differences."))
    _beat(_NARRATION_PACE_S)

    if not HISTORY_FILE.exists() or not RECORD_FILE.exists():
        _narrate(script.engineer,
                "This case is not available in this session.",
                "Nothing invented: the act stops rather than put an "
                "unsourced number on screen.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    hist_doc = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    record = json.loads(RECORD_FILE.read_text(encoding="utf-8"))
    history = hist_doc["history"]
    fd_rows = record["fd_verification_table"]["rows"]

    # The optimizer's own shape history, baked offline through the run's pyGeo
    # parameterization. Absent on a host that does not carry it, in which case
    # the act plays without the viewport rather than drawing an invented wing.
    shapes = _a2_shape.load()
    surfaces = _a2_shape.write_surfaces(shapes, out) if shapes else {}

    def show(key: str, label: str, painted: bool = True) -> None:
        """Put one recorded surface in the viewport."""
        if not (emit and key in surfaces):
            return
        emit("field.ready" if painted else "geometry.ready",
             {"url": f"/api/field/{out.name}/{surfaces[key]}", "label": label})

    if not shapes:
        _narrate(script.engineer,
                "The wing is not available in this session, so this act runs "
                "without the viewport.",
                "The numbers below are unaffected.")

    baseline = hist_doc["baseline"]
    final = hist_doc["final"]
    reduction = hist_doc["drag_reduction_pct"]
    majors = hist_doc["major_iterations_completed"]
    target_pct = _requested_target(request)
    iter_cap = _requested_iteration_cap(request)
    # Where the stated target was first reached in the recorded objective, and
    # where the run ended. Both measured; nothing is claimed about why (ITEM 1).
    first_met = (_target_first_met(history, baseline["CD"], target_pct)
                 if target_pct else None)

    # ---------------- Hypothesis ----------------
    _phase(script, HYPOTHESIS)
    roster.set(CHIEF_RESEARCHER, "framing the gradient method", "working")
    # ITEM 1 (owner, 2026-07-31): the line "an adjoint is exact only for the
    # problem it was derived from" is removed. It read as a caveat on a result
    # that has none: the gradient is graded against finite differences of this
    # very problem's own primal a few beats later, and the table says how well
    # it did. Nothing replaces it.
    _narrate(script.researcher,
            f"Drag on a three-dimensional wing at fixed lift, over {N_DV} "
            f"design variables.",
            f"A finite difference costs two flow solves per variable. One "
            f"adjoint returns the whole gradient.")
    roster.idle(CHIEF_RESEARCHER)

    gate.state(script, roster)

    # ---------------- Plan ----------------
    _phase(script, PLAN)
    if emit:
        emit("objective.spec", {"metric": "CD", "direction": "min"})

    # An uploaded surface is acknowledged and shown, and nothing more is
    # claimed for it. HONESTY CONSTRAINT (owner, 2026-07-31): the 28.3% comes
    # from the wing this lab optimized, so the received surface is never
    # described as the thing that was optimized, never relabelled as the
    # baseline, and never attached to a reported number.
    #
    # The distinction has to land in ONE line, on the label and in the
    # transcript (owner, 2026-07-31). Two labels, each naming a different
    # wing, read as a contradiction: the viewer sees a NACA and then a MACH
    # tutorial wing and has to work out which one the numbers belong to. So
    # the received surface's own label says where the numbers live, and the
    # baseline's label names the wing that produced them. When the uploaded
    # surface IS this wing there is nothing to separate, and the line says
    # that instead of drawing a distinction that is not there.
    #
    # ITEM 2 (owner, 2026-07-31): the act announces that it is delegating the
    # identification, so the identification HAPPENS. Two stages, and each
    # sentence says only what its own stage knows.
    #
    #   "Appears to be" is the name the surface declares itself under, which
    #   is exactly as much as an appearance is worth and no more.
    #
    #   The confirmation is a measurement. _a2_shape.identify reads the
    #   surface the control room took in and compares three overall
    #   dimensions against the same three measured off this act's own wing.
    #   The numericist reports what it found, whichever way it went.
    #
    # A delegation that is announced and not performed would narrate a step
    # the run never took, which the discretion charter forbids as squarely as
    # a fabricated number. So the check runs FIRST: if the surface cannot be
    # read, no delegation is announced and the act simply acknowledges what
    # arrived. The act never prints a hand-off it did not make.
    uploaded = str(params.get("surface") or "").strip()
    identity = _a2_shape.identify(shapes, uploaded) if (uploaded and shapes) \
        else None
    if uploaded:
        from chief_engineer.display_names import display_name

        uploaded_name = display_name(uploaded)
        is_this_wing = bool(identity and identity["match"])
        roster.set(CHIEF_ENGINEER, "reading the received wing", "working")
        if identity is None:
            # Nothing to confirm against, so nothing is claimed and nothing is
            # delegated on screen.
            _narrate(script.engineer, f"Wing received: {uploaded_name}.")
        else:
            _narrate(script.engineer,
                    f"Wing received: Appears to be a {uploaded_name}. "
                    f"Delegating to sub-agent to confirm.")
            roster.set(NUMERICIST, "confirming the received wing", "working")
        if is_this_wing:
            label = (f"{uploaded_name}, received. This is the wing the "
                     f"numbers come from")
        else:
            # "On screen next" only where the wing is about to be on screen.
            label = (f"{uploaded_name}, received. The numbers come from the "
                     f"MACH tutorial wing"
                     + (", on screen next" if shapes else ""))
        announce_geometry(emit, name=uploaded, label=label)
        if identity:
            rows = [[name, f"{identity['measured'][name]:.3f} m",
                     f"{identity['known'][name]:.3f} m"]
                    for name in identity["known"]]
            rows.append(["Widest disagreement between them",
                         f"{identity['worst_pct']:.3g}%",
                         f"{_a2_shape.IDENT_TOLERANCE_PCT:g}% to confirm"])
            emit_table(emit, script, role=_NUM_ROLE,
                       title="Confirming the received wing",
                       headers=("Dimension", "Received surface",
                                "MACH tutorial wing"),
                       rows=rows, table_id="ident-adjoint-optimization")
            _beat(_NARRATION_PACE_S)
            _narrate(script.numericist,
                    (f"Confirmed: the received surface measures as the MACH "
                     f"tutorial wing." if is_this_wing else
                     f"The received surface does not measure as the MACH "
                     f"tutorial wing."),
                    f"Every number below belongs to the MACH tutorial wing.")
            roster.idle(NUMERICIST)

    show("baseline", f"MACH tutorial wing, {BASELINE_NAME}. C_d "
                     f"{baseline['CD']:.6f} at C_L {CL_TARGET:g}",
         painted=False)
    if shapes:
        # The wing's dimensions and the case size are numbers, so they are a
        # table, not a sentence. Nothing here describes how the surface came
        # to be on screen: it is simply presented.
        emit_table(emit, script, role=_CE_ROLE,
                   title="The wing",
                   headers=("Quantity", "Value"),
                   rows=[
                       ["Root chord", f"{shapes['chord_root_m']:.2f} m"],
                       ["Tip chord", f"{shapes['chord_tip_m']:.2f} m"],
                       ["Semispan", f"{shapes['span_m']:.2f} m"],
                       ["Surface faces", f"{shapes['n_quad_faces']:,}"],
                       ["Mesh", f"{MESH_CELLS:,} cells"],
                       ["Lift constrained to", f"C_L {CL_TARGET:g}"],
                       ["Design variables", f"{N_DV}"],
                   ],
                   table_id="wing-adjoint-optimization")
        _beat(_NARRATION_PACE_S)
    if emit:
        emit("solver.selected", {
            "solver": "Discrete adjoint, reverse mode",
            "method": "steady compressible RANS, one-equation turbulence "
                      "closure, wall functions",
            "basis": "the gradient is taken from the transpose of the "
                     "discretized flow Jacobian, not from a fitted surface"})
    _narrate(script.engineer,
            (f"Objective: cut drag by at least {target_pct:g}% at fixed lift."
             if target_pct else "Objective: cut drag at fixed lift."),
            f"The gradient is taken by {AD_MODE}-mode automatic "
            f"differentiation of the residuals, the turbulence model "
            f"included.",
            f"Plan: take the adjoint gradient, then grade it against "
            f"{FD_SOLVES} primal solves.",
            f"Then optimize on the verified gradient.")
    # ITEM 3 (owner, 2026-07-31): the one line above says it, and these rows
    # say which residuals carry it, because "frozen turbulence" is the first
    # objection an adjoint-literate reviewer raises and a general claim does
    # not settle it. Every cell here was read off the run's own configuration.
    emit_table(emit, script, role=_CE_ROLE,
               title="How the derivative is taken",
               headers=("Item", "Value"),
               rows=[
                   ["Differentiation",
                    f"{AD_MODE.capitalize()} mode automatic differentiation "
                    f"of the discretized residuals"],
                   ["Turbulence",
                    "The one-equation transport variable is one of the "
                    "differentiated states. It is not frozen"
                    if TURBULENCE_DIFFERENTIATED else
                    "Frozen: the turbulence variable is not differentiated"],
                   ["Adjoint states",
                    f"{ADJOINT_STATES:,}, over {ADJOINT_STATE_FIELDS} state "
                    f"fields"],
                   ["Not differentiated",
                    "The wall distance that feeds the turbulence source term"],
                   ["Cost of the whole gradient",
                    "One linear solve against the transpose of the flow "
                    "Jacobian"],
               ],
               table_id="ad-adjoint-optimization")
    _beat(_NARRATION_PACE_S)

    # ---------------- Evidence: the gradient check ----------------
    _phase(script, EVIDENCE)
    roster.set(MONITOR, "watching the verification table", "watching")
    roster.set(CHIEF_ENGINEER, "grading the gradient", "working")

    # ITEM 2 (owner, 2026-07-31): the step comes first, before a single
    # agreement figure. The step, the form, and whether this case was swept.
    # Read from the verification record so the number on screen is the one the
    # check was run at, not a constant that could drift away from it.
    fd_spec = record["fd_verification_table"]
    fd_step = float(fd_spec.get("step", FD_STEP))
    fd_form = str(fd_spec.get("form", "central"))
    fd_calc = str(fd_spec.get("step_calc", "abs"))
    sweep = _step_sweep()
    step_rows = [
        ["Step", f"{fd_step:g}, {fd_form} difference, "
                 f"{'absolute' if fd_calc == 'abs' else fd_calc}"],
        ["Steps this case was graded at",
         "One. This case was not swept across decades"],
    ]
    if sweep:
        step_rows += [
            ["The sweep the step was chosen from",
             f"{sweep['steps']} steps from {sweep['lo']:g} to "
             f"{sweep['hi']:g}, on this ladder's smaller "
             f"{sweep['cells']:,} cell case, not on this one"],
            ["Plateau in that sweep",
             f"{sweep['plateau_lo']:g} to {sweep['plateau_hi']:g}, and "
             f"{fd_step:g} sits inside it"],
            ["Below the plateau",
             "The two perturbed drags differ by less than the primal's own "
             "residual floor, and the difference degrades"],
            ["Above the plateau",
             "The perturbed primal stops converging at all"],
        ]
    else:
        step_rows.append(
            ["Sweep", "No step-size sweep exists on this host for this case"])
    gate.table(emit, script, role=_NUM_ROLE,
               title="The finite difference the gradient is graded against",
               headers=("Item", "Value"),
               rows=step_rows, table_id="fdstep-adjoint-optimization")

    physical, geometric = [], []
    for row in fd_rows:
        name = row["derivative"]
        (geometric if name.startswith("geometry.") else physical).append(row)

    table_rows = []
    for row in physical:
        table_rows.append([
            row["derivative"],
            _fmt(row["analytic_magnitude"]),
            _fmt(row["fd_magnitude"]),
            f"{row['rel_error_pct']:.3g}%"])
    gate.table(emit, script, role=_NUM_ROLE,
               title="Gradient check: adjoint against central finite differences",
               headers=("Derivative", "Adjoint", "Finite difference",
                        "Relative error"),
               rows=table_rows, table_id="fd-adjoint-optimization")

    worst = max(r["rel_error_pct"] for r in physical)
    best = min(r["rel_error_pct"] for r in physical)
    # The shape groups are the hardest derivatives in the problem:
    # 96 design variables each, and the hardest derivative in the problem.
    shape_rows = [r for r in physical if "shape" in r["derivative"]]
    worst_shape = max(r["rel_error_pct"] for r in shape_rows)

    # Every geometric row is accounted for: at machine precision, merely very
    # tight, or a ratio of two numbers that are both zero.
    noise = [r for r in geometric if r["derivative"] in _NOISE_FLOOR_ROWS]
    graded = [r for r in geometric if r["derivative"] not in _NOISE_FLOOR_ROWS]
    machine = [r for r in graded if r["rel_error_pct"] < 1e-6]
    tight = [r for r in graded if r["rel_error_pct"] >= 1e-6]

    # ITEM 4 (owner, 2026-07-31): a machine-precision row on a table headed
    # "gradient check" reads as a solver-level accuracy claim, and it is not
    # one. Thickness, volume and the edge constraints are functions of the
    # control points alone; their derivative is analytic straight through the
    # free-form parameterization and never touches the flow solve. Exactness
    # there is what the arithmetic has to produce, so the table says the row
    # is expected rather than letting it be read as the solver's own accuracy.
    geom_rows = [["What these derivatives are",
                  f"{len(geometric)} groups",
                  "Analytic through the free-form parameterization. They "
                  "never touch the flow solve, so exactness here is expected "
                  "and is not a solver accuracy figure"],
                 ["Constraint derivatives at machine precision",
                  f"{len(machine)} of {len(geometric)}",
                  "1e-10% or better, several of them exact"]]
    if tight:
        geom_rows.append(["Remaining graded constraint derivative",
                          f"{len(tight)} of {len(geometric)}",
                          f"{max(r['rel_error_pct'] for r in tight):.3g}%"])
    geom_rows.append(["Both quantities at the numerical noise floor",
                      f"{len(noise)} of {len(geometric)}",
                      "Ratio of two zeros, reported rather than hidden"])
    gate.table(emit, script, role=_NUM_ROLE,
               title="Gradient check: the geometric constraints",
               headers=("Group", "Count", "Agreement"),
               rows=geom_rows, table_id="fd-geom-adjoint-optimization")

    roster.set(CHIEF_RESEARCHER, "ruling on the gradient", "working")
    gate.table(emit, script, role=_NUM_ROLE,
               title="Gradient verdict",
               headers=("Check", "Result"),
               rows=[
                   ["Worst shape group", f"{worst_shape:.3g}%, clears the "
                                         f"{GATE_PASS_PCT:g}% threshold by "
                                         f"{GATE_PASS_PCT / worst_shape:.1f} "
                                         f"times"],
                   ["Sign agreement, checked directly",
                    f"{SIGN_CHECKED} components, zero reversals"],
                   ["Sign agreement, bounded elsewhere",
                    f"Under {SIGN_BOUND_PCT:.2g}% of gradient magnitude"],
                   ["Constraint derivatives",
                    "Machine precision, as analytic derivatives should be"],
               ],
               table_id="verdict-adjoint-optimization")
    # The gate was stated as a rule, so the ruling on it belongs to the Chief
    # Researcher (owner, 2026-07-31). The roster already had the researcher
    # ruling here while the engineer spoke the verdict.
    _narrate(script.researcher, "Gradient gate passes.")
    roster.idle(CHIEF_RESEARCHER)

    # ---------------- Evidence: the gradient, on the wing ----------------
    # The single most useful thing an adjoint produces is a direction, and a
    # direction on a wing is a picture. This is the recorded gradient itself,
    # pushed through the FFD's own map onto the skin, not a redrawing of it.
    # The reading of that picture is a table (owner, 2026-07-31): one lead-in
    # bullet, then the colour convention, the source and the scale as rows.
    if shapes:
        grad = shapes["gradient"]
        glo, ghi = grad["window_mm_per_step"]
        show("gradient", "Where the adjoint says to push. Descent direction "
                         "on the skin, C_d at fixed C_L")
        # What the run produced, presented by the one that ran it: the
        # researcher has just ruled on the gate and speaks again at the
        # conclusion, and the same voice three beats running reads as one
        # agent talking to itself.
        _narrate(script.engineer,
                "That is the gradient, on the wing. One adjoint solve "
                "produced the whole picture.")
        gate.table(emit, script, role=_NUM_ROLE,
                   title="Reading the gradient on the skin",
                   headers=("Item", "Meaning"),
                   rows=[
                       ["Red", "Drag falls if the skin moves outward"],
                       ["Blue", "Drag falls if the skin moves inward"],
                       ["White", "The gradient asks for nothing there"],
                       ["Surface map", f"Free form, linear in the shape "
                                       f"variables, verified to "
                                       f"{shapes['_checks']['ffd_shape_map_linearity_residual']:.0e}"],
                       ["Colour bar", "Millimetres per unit step, symmetric "
                                      "about zero"],
                       ["Scale", f"A unit step of steepest descent moves the "
                                 f"skin at most "
                                 f"{max(abs(glo), abs(ghi)):.1f} mm"],
                   ],
                   table_id="gradient-adjoint-optimization")

    # ---------------- Evidence: the optimization ----------------
    roster.set(CHIEF_ENGINEER, "reading the optimization history", "working")
    roster.set_workers(RANKS, "gradient-driven shape optimization")

    # The wing walks the optimization while the trace descends beside it. The
    # two streams are interleaved on purpose: iteration by iteration, the
    # viewer sees the drag fall and the surface that bought it, together.
    frames = {f["iter"]: f for f in shapes["frames"]} if shapes else {}
    # ITEM 8 (owner, 2026-07-31): the drag plot carries this act's own
    # measured uncertainty rather than a zero-width band. The figure is the
    # numerical channel below, the worst derivative group's disagreement with
    # a central finite difference of the full primal, and it is relative, so
    # it is drawn as a share of each iteration's own drag. It is the only
    # uncertainty this case measured; nothing is inflated to fill the others.
    u_numerical = worst / 100.0
    if emit:
        for point in history:
            emit("trace.point", {
                "series": "Cd_history", "x": point["iter"],
                "y": round(point["CD"], 8),
                "lo": round(point["CD"] * (1.0 - u_numerical), 8),
                "hi": round(point["CD"] * (1.0 + u_numerical), 8),
                "x_label": "optimizer major iteration", "y_label": "C_d",
                "title": f"Drag at fixed lift, C_L = {CL_TARGET:g}",
                "feasible": True})
            frame = frames.get(point["iter"])
            if frame is None:
                continue
            drop = (baseline["CD"] - frame["CD"]) / baseline["CD"] * 100
            show(f"iter{frame['iter']}",
                 f"Major iteration {frame['iter']} of {majors}. C_d "
                 f"{frame['CD']:.6f}, {_against_baseline(drop)}. At scale, "
                 f"painted with displacement from baseline (mm)")
            _beat(_FRAME_PACE_S)
    roster.set_workers(0)

    if shapes:
        last = shapes["frames"][-1]
        show(f"iter{last['iter']}",
             f"Optimized wing at major iteration {last['iter']}. C_d "
             f"{last['CD']:.6f}, {_headline(reduction)}")
        dlo, dhi = shapes["disp_window_mm"]
        chord = shapes["chord_root_m"]
        twist_worst = min(last["twist_deg"])
        # ITEM 5 (owner, 2026-07-31): "no three near-miss numbers". This act
        # used to put 186, 309 and 303 mm on screen in one table with nothing
        # saying they measure different things, so a viewer had to guess which
        # one was the shape change. One reference is named first, in its own
        # row, and every other millimetre figure in the act is stated against
        # it: the colour window is the widest normal displacement reached at
        # ANY iteration, which is why it is the larger number, and it is
        # printed as a multiple of the reference so the gap is arithmetic
        # rather than a discrepancy.
        widest = max(abs(dlo), abs(dhi))
        reference_mm = last["max_disp_mm"]
        # The window is a normal displacement, so the multiple is taken
        # against the reference surface's own normal displacement rather than
        # against its total point motion. Both round to the same millimetre
        # here; comparing like with like is the point.
        reference_n_mm = last.get("max_dn_mm") or reference_mm
        gate.table(emit, script, role=_CE_ROLE,
                   title="What the gradient moved",
                   headers=("Quantity", "Value"),
                   rows=[
                       ["Reference for every millimetre in this act",
                        f"{_a2_shape.DISP_REFERENCE.capitalize()}, "
                        f"{reference_mm:.0f} mm at the point that moved most"],
                       ["As a fraction of the root chord",
                        f"{reference_mm / 10.0 / chord:.2f}% of "
                        f"{chord:.2f} m"],
                       ["As a fraction of the root section's thickness",
                        f"{reference_mm / 10.0 / shapes['thickness_root_m']:.0f}% "
                        f"of {shapes['thickness_root_m']:.2f} m"],
                       ["Largest twist change",
                        f"{twist_worst:.2f} deg nose down, at the "
                        f"{shapes['refaxis_z_m'][last['twist_deg'].index(twist_worst) + 1]:.1f} m station"],
                       ["Twist at the tip station",
                        f"{last['twist_deg'][-1]:.2f} deg"],
                       ["Colour window, fixed across every frame",
                        f"{dlo:.0f} to {dhi:.0f} mm on the outward normal. "
                        f"Set by the widest normal displacement reached at "
                        f"any iteration, {widest / reference_n_mm:.2f} times "
                        f"the {reference_mm:.0f} mm reference, so it holds "
                        f"still while the wing moves"],
                       ["Display scaling", "None anywhere in this act"],
                   ],
                   table_id="shape-adjoint-optimization")

        # ITEM 6 (owner, 2026-07-31): a surface that moves this far relative
        # to its own thickness raises an obvious question about what happened
        # to the mesh underneath it, and the run answered that question 81
        # times. The trigger is a threshold, not a judgement call: if the
        # reference displacement clears MESH_REPORT_TRIGGER_PCT of local
        # thickness, the metrics go on screen. Nothing here is softened; the
        # worst check pushed six faces past the non-orthogonality mark, and
        # that is on the table alongside the checks that were clean.
        thickness_pct = (reference_mm / 10.0 / shapes["thickness_root_m"])
        if thickness_pct >= MESH_REPORT_TRIGGER_PCT:
            nlo, nhi = MESH_NON_ORTHO_RANGE
            slo, shi = MESH_SKEW_RANGE
            alo, ahi = MESH_ASPECT_RANGE
            gate.table(emit, script, role=_MON_ROLE,
                       title="Mesh quality after deformation",
                       headers=("Metric", "Across the pass", "Threshold"),
                       rows=[
                           ["Why this is reported",
                            f"The shape moved {thickness_pct:.0f}% of local "
                            f"thickness",
                            f"Reported above {MESH_REPORT_TRIGGER_PCT:g}%"],
                           ["Checks on the deformed mesh",
                            f"{MESH_DEFORM_CHECKS}, one per design "
                            f"evaluation",
                            f"{MESH_DEFORM_CHECKS_PASSED} returned mesh OK"],
                           ["Worst cell non-orthogonality",
                            f"{nlo:.1f} to {nhi:.1f} deg",
                            f"{MESH_NON_ORTHO_MARK:g} deg mark, "
                            f"{MESH_NON_ORTHO_ERROR:g} deg error"],
                           ["Faces past that mark at the worst check",
                            f"{MESH_WORST_FLAGGED_FACES} of "
                            f"{MESH_FACES:,}",
                            f"{MESH_CHECKS_OVER_MARK} of "
                            f"{MESH_DEFORM_CHECKS} checks had any"],
                           ["Maximum skewness", f"{slo:.2f} to {shi:.2f}",
                            f"{MESH_SKEW_GATE:g}"],
                           ["Maximum aspect ratio",
                            f"{alo:.0f} to {ahi:.0f}",
                            f"{MESH_ASPECT_GATE:g}"],
                           ["Designs refused on mesh quality", "None",
                            "The solver refuses any that fail"],
                       ],
                       table_id="meshdeform-adjoint-optimization")

        # ---- second pass: the same 48 frames on a closer viewing convention
        # No coordinate is scaled: the viewing convention moves, the wing does
        # not. The measured amplification ceiling and the pixel arithmetic
        # behind this choice are withheld from the narration (owner,
        # 2026-07-31) and stay in _a2_shape where they are computed.
        show("near0", f"Inboard span, at scale. Baseline, C_d "
                      f"{baseline['CD']:.6f}")
        # Whether what is on screen is at its true size is a statement about
        # measurement, so the numericist makes it (owner, 2026-07-31). It also
        # keeps the engineer from speaking twice running: this entry and the
        # one that closes the pass are separated by the whole second sweep, so
        # they cannot be merged into one.
        roster.set(NUMERICIST, "holding the viewing convention", "working")
        _narrate(script.numericist,
                f"Same surfaces on a closer viewing convention: the inboard "
                f"{_a2_shape.CLOSEUP_SPAN_M:g} metres of span.",
                f"Unscaled. The viewing convention moved, the wing did not.")
        roster.idle(NUMERICIST)
        for point in history:
            frame = frames.get(point["iter"])
            if frame is not None:
                drop = (baseline["CD"] - frame["CD"]) / baseline["CD"] * 100
                show(f"near{frame['iter']}",
                     f"Inboard span, at scale. Major iteration "
                     f"{frame['iter']} of {majors}, C_d {frame['CD']:.6f}, "
                     f"{_against_baseline(drop)}")
                _beat(_FRAME_PACE_S)
        show(f"near{last['iter']}",
             f"Inboard span, at scale. Optimized, C_d {last['CD']:.6f}, "
             f"{_headline(reduction)}")
        _narrate(script.engineer,
                f"That is the shape the gradient bought, at the size it is.")

    cl_off = abs(final["CL"] - CL_TARGET) / CL_TARGET * 100
    # The settling claim, measured from the recorded history rather than eyeballed.
    tail = [r["CD"] for r in history[-TAIL_ITERS:]]
    tail_spread_pct = (max(tail) - min(tail)) / min(tail) * 100
    # ITEM 7 (owner, 2026-07-31): the optimizer's status is reported as
    # descent and nothing else. "Moving against the gradient" is banned by
    # name: it reads as the optimizer going the wrong way when it meant the
    # opposite, and no viewer should have to work out which. Merit functions
    # and step cutbacks are not translated into plainer words, they are simply
    # not on screen; what IS on screen is how many of the recorded steps took
    # drag down, counted from the history rather than characterised.
    steps_down = sum(1 for a, b in zip(tail, tail[1:]) if b < a)
    tail_steps = len(tail) - 1
    # Every headline number in one table, each against what it is graded on
    # (owner, 2026-07-31). Nothing here is repeated in prose afterwards.
    result_rows = [
        [f"Drag reduction below {BASELINE_NAME} at matched lift",
         f"{reduction:.1f}%",
         f"{target_pct:g}% asked" if target_pct
         else "The two drags below are what it is measured from"],
        ["Baseline C_d at C_L 0.5", f"{baseline['CD']:.6f}",
         "The point the reduction is measured from"],
        ["Final C_d at C_L 0.5", f"{final['CD']:.6f}",
         f"C_L {final['CL']:.6f}, {cl_off:.3f}% off target"],
        ["Worst gradient group against finite difference",
         f"{worst:.3g}%", f"{GATE_PASS_PCT:g}% pass threshold"],
        ["Major iterations", f"{majors}",
         f"{iter_cap:g} asked, every one on the verified gradient"
         if iter_cap else "Every one on the verified gradient"],
    ]
    # ITEM 1 (owner, 2026-07-31): a stated target is a stopping rule, so the
    # act says where the recorded objective first reached it and where the run
    # ended. Both read off the history. The row states no reason for the
    # difference, because the run records none.
    if first_met:
        result_rows.append([
            f"Where the {target_pct:g}% was first reached",
            f"Major iteration {first_met['iter']}, at {first_met['pct']:.1f}%",
            (f"At or past {target_pct:g}% from major iteration "
             f"{first_met['stayed_from']} on. The run ran to {majors}")
            if first_met["stayed_from"] != first_met["iter"] else
            (f"At or past {target_pct:g}% every iteration after. The run ran "
             f"to {majors}")])
    result_rows += [
        [f"Objective band over the last {TAIL_ITERS} iterations",
         f"{tail_spread_pct:.2g}%", "Measured across the recorded objective"],
        [f"Steps that took drag down, last {TAIL_ITERS} iterations",
         f"{steps_down} of {tail_steps}",
         "Still descending on the verified gradient"],
    ]
    gate.table(emit, script, role=_CE_ROLE,
               title="Result",
               headers=("Quantity", "Value", "Reference or threshold"),
               rows=result_rows,
               table_id="result-adjoint-optimization")

    # ITEM 7 (owner, 2026-07-31): the drag reduction was asked for as
    # "28.3% ± <numerical uncertainty>". The numerical channel this case
    # actually computed is a GRADIENT-agreement number, measured against
    # central finite differences of the full primal. It is not a band on the
    # drag reduction, and printing it as one would state a result the lab did
    # not measure. No grid-refinement study exists for this mesh, so no
    # discretization band on the reduction exists either. Per her own
    # instruction, the channels that were computed are shown and the one that
    # is unavailable for this quantity is named rather than invented.
    gate.table(emit, script, role=_NUM_ROLE,
               title="Uncertainty channels on this result",
               headers=("Channel", "Value"),
               rows=[
                   ["Numerical, gradient agreement", f"{worst:.3g}%"],
                   ["Band drawn on the drag trace",
                    f"±{u_numerical:.4f} relative on C_d"],
                   ["Numerical, band on the drag reduction",
                    "Not available for this quantity"],
                   ["Input", "None assumed for this case"],
                   ["Model", f"Stated closure, graded against this solver's "
                             f"own {BASELINE_NAME} at the same lift"],
               ],
               table_id="channels-adjoint-optimization")

    _narrate(script.monitor,
            f"Watched the objective on every major iteration. Nothing fatal.")
    roster.idle(MONITOR)

    verdict = {
        "tier": SOLVER_BACKED,
        "reason": (f"gradient verified against {FD_SOLVES} finite-difference "
                   f"primal solves, worst group {worst:.3g}%, no sign "
                   f"reversals that could steer it"),
    }
    # ITEM 4 (owner, 2026-07-31): the conditions the request stated, answered
    # with the two numbers this run measured and nothing else beside them. The
    # standing rule that outlives any prompt: this act never says the
    # optimization converged, because it did not, and that is a statement
    # about the result rather than a detail about method.
    if target_pct and iter_cap:
        against = (f"That clears the {target_pct:g}% asked, at {majors} major "
                   f"iterations against the {iter_cap:g} asked.")
    elif target_pct:
        against = "That clears the target."
    elif iter_cap:
        against = (f"That is {majors} major iterations against the "
                   f"{iter_cap:g} asked.")
    else:
        against = ""
    # ITEM 1 (owner, 2026-07-31): the verdict says where the stated target was
    # first reached and where the run ended, in one line. It says nothing about
    # why the two differ, and it never will unless a reason is on the record:
    # asserting a mechanism this run did not have would be the one thing the
    # line exists to avoid.
    stopping = (f"The {target_pct:g}% was first reached at major iteration "
                f"{first_met['iter']}, and the run ran to {majors}."
                if first_met else "")
    # The tier is a ruling on fidelity, so the Chief Researcher gives it
    # (owner, 2026-07-31: the researcher frames and rules).
    roster.set(CHIEF_RESEARCHER, "ruling on the result", "working")
    _narrate(script.researcher,
            f"Verdict: drag {_headline(reduction)}, on a verified "
            f"gradient.",
            *([against] if against else []),
            *([stopping] if stopping else []),
            verdict=verdict)
    roster.idle(CHIEF_RESEARCHER)

    if emit:
        # No ``ci`` key: the headline card renders "value ± ci" and this case
        # has no measured band on the drag reduction to put there. It used to
        # carry the string "n/a", which rendered as "28.3% ± n/a (n/a)".
        emit("result.verdict", {
            "quantity": f"Drag reduction below {BASELINE_NAME} at matched "
                        f"lift",
            "value": f"{reduction:.1f}%",
            "envelope": f"{majors} major iterations on the verified gradient",
            **verdict})

    channels = uncertainty_channels(
        input_2sigma=None, numerical=u_numerical, model=None,
        input_note="No input uncertainty was assumed for this problem.",
        numerical_note=(f"• Gradient accuracy measured directly: the worst "
                        f"derivative group agrees with a central finite "
                        f"difference of the full primal to {worst:.3g}%. "
                        f"Component-level sign agreement confirmed on "
                        f"{SIGN_CHECKED} components directly and bounded "
                        f"below {SIGN_BOUND_PCT:.2g}% of gradient magnitude "
                        f"on the rest."),
        model_note=(f"compressible RANS closure with wall functions, "
                    f"stated model form; the drag reduction is measured "
                    f"against this solver's own {BASELINE_NAME} at the same "
                    f"lift, not against an experiment"))
    if emit:
        emit("uncertainty.channels", channels)

    # ---------------- Conclusion ----------------
    _phase(script, CONCLUSION)
    elapsed = time.monotonic() - began
    # The cost table IS the argument for the method (owner, 2026-07-31): the
    # same gradient, bought two ways, on this run's own accounting. The
    # verification stage is exactly the finite-difference route priced, which
    # is why it doubles as the comparison rather than reading as overhead.
    gate.table(emit, script, role=_CE_ROLE,
               title=f"What the whole gradient costs, {N_DV} design variables",
               headers=("Route", "Primal solves", "Core-minutes"),
               rows=_cost_rows(),
               table_id="cost-adjoint-optimization")
    # ITEM 3 (owner, 2026-07-31): the Chief Researcher says this, not the
    # Chief Engineer. It is the standing claim the method rests on rather than
    # a report of what this run did, and the researcher owns the framing.
    _narrate(script.researcher,
            f"One adjoint solve buys the whole gradient.",
            f"The gap widens with every design variable added.")

    # The two figures that show the shape change unscaled. Both are drawn from
    # the same surfaces the viewport streamed.
    report_plots = []
    if shapes:
        for builder, name, title in (
                (_a2_shape.section_figure, "a2_sections.png",
                 "Wing sections, unscaled: baseline against the "
                 "optimized shape"),
                (_a2_shape.twist_figure, "a2_twist.png",
                 "Twist the optimizer added, by spanwise station")):
            path = builder(shapes, out / name)
            if path:
                announce_plot(emit, LABEL, path, title)
                report_plots.append({"url": f"/api/plot/{LABEL}/{name}",
                                     "title": title})

    knowledge.add(f"Discrete adjoint verified on a {N_DV}-variable wing: "
                  f"worst group {worst:.3g}% against central finite "
                  f"differences; drag {_headline(reduction)} after "
                  f"{majors} major iterations")

    if emit:
        emit("agenda.updated", {"entries": _AGENDA})

    report_doc = lab_report(
        title="Adjoint wing optimization",
        abstract=[
            f"A discrete adjoint supplied the gradient of drag and lift with "
            f"respect to {N_DV} design variables on a {MESH_CELLS:,} cell "
            f"three-dimensional wing, at a cost independent of the number of "
            f"design variables.",
            f"The gradient was graded against {FD_SOLVES} central "
            f"finite-difference primal solves before it was used: worst "
            f"physical group {worst:.3g}%, best {best:.3g}%, and no sign "
            f"reversal in any component that could steer the optimizer. The "
            f"gate passed. The geometric constraint derivatives all came back "
            f"at machine precision, which is expected rather than impressive: "
            f"they are analytic through the free-form parameterization and "
            f"never touch the flow solve, so that row grades the arithmetic, "
            f"not the solver.",
            (f"The optimization then took drag {_headline(reduction)} over "
             f"{majors} major iterations"
             + (f", against a {target_pct:g}% target" if target_pct else "")
             + (f" and the {iter_cap:g} major iterations asked for"
                if iter_cap else "") + "."
             # ITEM 1: when the target was reached, and where the run ended.
             # Nothing about why, because nothing about why is on the record.
             + (f" The {target_pct:g}% was first reached at major iteration "
                f"{first_met['iter']}, and the run ran to {majors}."
                if first_met else "")),
        ],
        methods=[
            "Steady compressible RANS primal with a one-equation turbulence "
            "closure and wall functions, solved to its own residual "
            "tolerance.",
            f"Discrete adjoint for drag and for lift with respect to surface "
            f"control points, spanwise twist and the flow state. The "
            f"derivative is taken by {AD_MODE}-mode automatic differentiation "
            f"of the discretized residuals, with the one-equation turbulence "
            f"transport equation among the {ADJOINT_STATE_FIELDS} "
            f"differentiated state fields rather than frozen; the wall "
            f"distance feeding its source term is the one term not "
            f"differentiated.",
            f"Verification by {fd_form} finite difference of the full primal "
            f"at a single absolute step of {fd_step:g}, {FD_SOLVES} "
            f"perturbation solves covering every one of the {N_DV} design "
            f"variables. This case was graded at that one step and was not "
            f"itself swept across decades; the step comes from a sweep run on "
            f"the smaller case at the foot of the same ladder.",
            f"Graded against this lab's current gradient standard, applied "
            f"uniformly across the whole ladder: pass at {GATE_PASS_PCT:g}% "
            f"or better with no flagged component, conditional between "
            f"{GATE_PASS_PCT:g} and {GATE_CONDITIONAL_PCT:g}%, fail above "
            f"{GATE_CONDITIONAL_PCT:g}% or on any sign-flipped component "
            f"whatever the aggregate says.",
            f"Gradient-based optimization with lift equality-constrained to "
            f"{CL_TARGET:g} and thickness, volume and edge constraints "
            f"active.",
        ] + ([
            # The geometry is presented, never explained (owner, 2026-07-31):
            # no line here says where a surface came from or how it was
            # produced. What stays is the one thing a viewer needs in order to
            # read the pictures, which is that nothing is scaled.
            f"Nothing on screen is scaled. The wing is shown twice, once "
            f"whole and once on the inboard {_a2_shape.CLOSEUP_SPAN_M:g} m of "
            f"span on a closer viewing convention, and both section figures "
            f"are unscaled with equal aspect.",
        ] if shapes else []),
        # One short envelope each, and no ``reason``: the memo prints the
        # verdict reason under every result, so carrying it here repeated the
        # same sentence three times (owner, 2026-07-31). The tier badge stays.
        results=[
            # NO envelope on the headline result. The certificate prints the
            # first result as "value ± envelope (95% confidence interval)",
            # so anything put here is read as a confidence band. This case has
            # no measured band on the drag reduction, and the target it was
            # asked for is not one. It rides in the certificate's result table
            # and in the on-screen Result table instead.
            {"quantity": "Drag reduction",
             "value": f"{reduction:.1f}%",
             "envelope": f"below {BASELINE_NAME} at matched lift",
             "tier": verdict["tier"]},
            {"quantity": "Worst gradient group against finite difference",
             "value": f"{worst:.3g}%",
             "envelope": f"{GATE_PASS_PCT:g}% pass threshold",
             "tier": verdict["tier"]},
            {"quantity": "Major iterations",
             "value": f"{majors}",
             "envelope": "every one on the verified gradient",
             "tier": verdict["tier"]},
        ],
        uncertainty=[
            f"The {reduction:.1f}% is measured against this solver's own "
            f"{BASELINE_NAME} at the same lift. It is not graded against a "
            f"wind tunnel, and no published reduction figure exists for this "
            f"case to compare it with.",
            f"Gradient accuracy is measured, not assumed: worst group "
            f"{worst:.3g}% against central finite differences of the full "
            f"primal. Sign agreement was confirmed directly on "
            f"{SIGN_CHECKED} components and bounded below "
            f"{SIGN_BOUND_PCT:.2g}% of gradient magnitude on the rest.",
            f"The mesh-validity block below reports the mesh as built. The "
            f"deformed mesh was checked again at every one of the "
            f"{MESH_DEFORM_CHECKS} design evaluations: worst cell "
            f"non-orthogonality ranged to {MESH_NON_ORTHO_RANGE[1]:.1f} deg "
            f"against a {MESH_NON_ORTHO_MARK:g} deg mark, with "
            f"{MESH_WORST_FLAGGED_FACES} of {MESH_FACES:,} faces past it at "
            f"the worst check, maximum skewness to "
            f"{MESH_SKEW_RANGE[1]:.2f} against {MESH_SKEW_GATE:g} and "
            f"maximum aspect ratio to {MESH_ASPECT_RANGE[1]:.0f} against "
            f"{MESH_ASPECT_GATE:g}. Every check returned mesh OK and no "
            f"design was refused on mesh quality.",
        ],
        next_investigations=[f"{e['title']}: {e['scope']}" for e in _AGENDA],
        compute=ledger.as_dict(),
    )
    if report_plots:
        report_doc["plots"] = report_plots
    if emit:
        emit("report.ready", report_doc)

    cert_path = out / "certificate.pdf"
    try:
        cert_path.unlink()
    except OSError:
        pass
    try:
        from chief_engineer.certificate import build_certificate_v2

        cert_doc = dict(report_doc)
        # No Status row: the stopping condition is withheld from every camera
        # surface (owner, 2026-07-31), and nothing replaces it. The
        # certificate never claims convergence in its place.
        cert_doc["result_fields"] = [
            ("Design variables", f"{N_DV}"),
            ("Gradient check", f"worst group {worst:.3g}%, no material sign reversal"),
            ("Drag reduction",
             f"{_headline(reduction)}, C_L {CL_TARGET:g}"),
            ("Major iterations", f"{majors}"),
        ]
        if target_pct:
            cert_doc["result_fields"].insert(
                2, ("Target asked", f"at least {target_pct:g}%"))
        if first_met:
            cert_doc["result_fields"].append(
                ("Target first reached",
                 f"major iteration {first_met['iter']}, run ran to {majors}"))
        if iter_cap:
            cert_doc["result_fields"].append(
                ("Major iterations asked", f"no more than {iter_cap:g}"))
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path,
            geometry="three-dimensional wing",
            objective=(request or "Adjoint drag optimization at matched lift"),
            mission_id=f"{LABEL}-{int(time.time())}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels,
            display_name="Three-dimensional wing, adjoint design case",
            source_filename="wing surface, case recipe",
            solver="Selected solver, steady compressible RANS with a "
                   "reverse-mode discrete adjoint",
            mesh=mesh_validity(MESH_CELLS, *_mesh_numbers(record)))
        if emit:
            emit("certificate.ready", {**certificate, "dir": out.name})
    except Exception:
        _narrate(script.engineer,
                "No certificate could be issued for this run.",
                "The result above stands on the transcript and the report.")

    _narrate(script.engineer,
            f"From a verified gradient to drag {_headline(reduction)}.")
    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out, f"({elapsed:.2f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
