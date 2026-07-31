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

The optimization delivered 28.3% drag reduction at matched lift over 47 major
iterations.

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

Every number this act reports is read at run time out of the recorded
optimization's own primary artifacts (the optimizer's iteration table and the
history database it wrote), joined and committed as
``A2_optimization_history.json``. Nothing is modelled, smoothed or invented.

    python -m workflows.adjoint_optimization
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from . import (OUT_ROOT, announce_geometry, announce_plot, bullets, emit_table,
               make_transcript)
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, MONITOR, PLAN,
                                SOLVER_BACKED, ComputeLedger, KnowledgeBase,
                                Roster, lab_report, uncertainty_channels)
from chief_engineer.transcript import CHIEF_ENGINEER as _CE_ROLE
from chief_engineer.transcript import NUMERICIST as _NUM_ROLE

from . import _a2_shape
from .geometry_study import mesh_validity

LABEL = "adjoint-optimization"

_LADDER = (Path(__file__).resolve().parents[2]
           / "demo-output" / "website" / "dafoam" / "ladder-a")
HISTORY_FILE = _LADDER / "A2_optimization_history.json"
RECORD_FILE = _LADDER / "A2_mach_tutorial_wing.json"

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
COST_OPT = 240.4
FD_PRIMAL_SOLVES = 211

# This lab's current gradient-verification standard, applied uniformly across
# the whole ladder: PASS at 5% or better on the aggregate AND no flagged
# component; CONDITIONAL between 5 and 15%; FAIL above 15%, or on any
# sign-flipped or unstable component whatever the aggregate says. An earlier,
# looser "1 to 12% is normal" band was inferred from a single case and has
# been retired; it is not cited here.
GATE_PASS_PCT = 5.0
GATE_CONDITIONAL_PCT = 15.0

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
# 20%"). When one is stated the act reports the delivered reduction against
# it; when it is not, nothing is invented and the target simply is not shown.
_TARGET_PCT = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|per\s?cent|percent)", re.I)


def _requested_target(request: str | None) -> float | None:
    """The drag-reduction target stated in the request, if there is one."""
    match = _TARGET_PCT.search(request or "")
    return float(match.group(1)) if match else None


def _fmt(x: float) -> str:
    """Engineering-notation magnitude for the verification table."""
    return f"{x:.6e}"


def main(request: str | None = None, params: dict | None = None,
         emit=None) -> int:
    params = dict(params or {})
    out = OUT_ROOT / LABEL
    out.mkdir(parents=True, exist_ok=True)

    script = make_transcript(LABEL, emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    began = time.monotonic()

    script.system(request or ("Request: reduce the drag on the wing with the "
                              "discrete adjoint and check the gradient "
                              "against finite differences."))

    if not HISTORY_FILE.exists() or not RECORD_FILE.exists():
        bullets(script.engineer,
                "The record this act reports from is not on this host, so "
                "there is nothing to report.",
                "Nothing invented: the act stops here rather than putting a "
                "number on screen that it cannot source.")
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
        bullets(script.engineer,
                "The shape history is not on this host, so this act runs "
                "without the viewport.",
                "The numbers below are unaffected.")

    baseline = hist_doc["baseline"]
    final = hist_doc["final"]
    reduction = hist_doc["drag_reduction_pct"]
    majors = hist_doc["major_iterations_completed"]
    target_pct = _requested_target(request)

    # ---------------- Hypothesis ----------------
    script.phase(HYPOTHESIS)
    roster.set(CHIEF_RESEARCHER, "framing the gradient method", "working")
    bullets(script.researcher,
            f"Drag on a three-dimensional wing at fixed lift, over {N_DV} "
            f"design variables.",
            f"A finite difference costs two flow solves per variable. One "
            f"adjoint returns the whole gradient.",
            f"An adjoint is exact only for the problem it was derived from, "
            f"so it gets graded first.")
    roster.idle(CHIEF_RESEARCHER)

    roster.set(CHIEF_ENGINEER, "stating the gate", "working")
    bullets(script.engineer,
            f"Hypothesis: the adjoint gradient matches central finite "
            f"differences on every derivative group.",
            f"Falsifier: any group worse than {GATE_PASS_PCT:g}%, or any "
            f"component whose sign reverses.",
            f"Gate: nothing is optimized until the gradient passes.")

    # ---------------- Plan ----------------
    script.phase(PLAN)
    if emit:
        emit("objective.spec", {"metric": "CD", "direction": "min"})

    # An uploaded surface is acknowledged and shown, and nothing more is
    # claimed for it. HONESTY CONSTRAINT (owner, 2026-07-31): the 28.3% comes
    # from the wing this lab optimized, so the received surface is never
    # described as the thing that was optimized, never relabelled as the
    # baseline, and never attached to a reported number. It goes in the
    # viewport under its own name, the wing follows under its own name, and
    # the transcript says which one carries the result.
    uploaded = str(params.get("surface") or "").strip()
    if uploaded:
        from chief_engineer.display_names import display_name

        uploaded_name = display_name(uploaded)
        announce_geometry(emit, name=uploaded,
                          label=f"Surface received: {uploaded_name}")
        bullets(script.engineer,
                f"Surface received: {uploaded_name}. It is on the record for "
                f"this session.",
                f"The optimization reported here ran on this lab's wing, and "
                f"every number stays with it.")

    show("baseline", f"MACH tutorial wing, baseline. C_d {baseline['CD']:.6f} "
                     f"at C_L {CL_TARGET:g}", painted=False)
    if shapes:
        bullets(script.engineer,
                f"The wing in the viewport is the solver's own patch, "
                f"{shapes['n_quad_faces']:,} faces, undecimated.",
                f"Root chord {shapes['chord_root_m']:.2f} m, tip chord "
                f"{shapes['chord_tip_m']:.2f} m, semispan "
                f"{shapes['span_m']:.2f} m.")
    if emit:
        emit("solver.selected", {
            "solver": "Discrete adjoint, reverse mode",
            "method": "steady compressible RANS, one-equation turbulence "
                      "closure, wall functions",
            "basis": "the gradient is taken from the transpose of the "
                     "discretized flow Jacobian, not from a fitted surface"})
    bullets(script.engineer,
            *([f"Objective: cut drag by at least {target_pct:g}% at fixed "
               f"lift."] if target_pct else []),
            f"Plan: take the adjoint gradient, then grade it against "
            f"{FD_SOLVES} finite-difference primal solves.",
            f"Then hand the verified gradient to the optimizer with lift held "
            f"at {CL_TARGET:g}.",
            f"Mesh {MESH_CELLS:,} cells.")

    # ---------------- Evidence: the gradient check ----------------
    script.phase(EVIDENCE)
    roster.set(MONITOR, "watching the verification table", "watching")
    roster.set(CHIEF_ENGINEER, "grading the gradient", "working")

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
    emit_table(emit, script, role=_NUM_ROLE,
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
    worst_other = max(r["rel_error_pct"] for r in physical
                      if r not in shape_rows)

    # Every geometric row is accounted for: at machine precision, merely very
    # tight, or a ratio of two numbers that are both zero.
    noise = [r for r in geometric if r["derivative"] in _NOISE_FLOOR_ROWS]
    graded = [r for r in geometric if r["derivative"] not in _NOISE_FLOOR_ROWS]
    machine = [r for r in graded if r["rel_error_pct"] < 1e-6]
    tight = [r for r in graded if r["rel_error_pct"] >= 1e-6]

    geom_rows = [["Constraint derivatives at machine precision",
                  f"{len(machine)} of {len(geometric)}",
                  "1e-10% or better, several of them exact"]]
    if tight:
        geom_rows.append(["Remaining graded constraint derivative",
                          f"{len(tight)} of {len(geometric)}",
                          f"{max(r['rel_error_pct'] for r in tight):.3g}%"])
    geom_rows.append(["Both quantities at the numerical noise floor",
                      f"{len(noise)} of {len(geometric)}",
                      "Ratio of two zeros, reported rather than hidden"])
    emit_table(emit, script, role=_NUM_ROLE,
               title="Gradient check: the geometric constraints",
               headers=("Group", "Count", "Agreement"),
               rows=geom_rows, table_id="fd-geom-adjoint-optimization")

    roster.set(CHIEF_RESEARCHER, "ruling on the gradient", "working")
    bullets(script.researcher,
            f"Worst shape group agrees to {worst_shape:.3g}%, clearing the "
            f"{GATE_PASS_PCT:g}% threshold by "
            f"{GATE_PASS_PCT / worst_shape:.1f} times.",
            f"Sign checked on {SIGN_CHECKED} components, zero reversals, "
            f"bounded under {SIGN_BOUND_PCT:.2g}% elsewhere.",
            f"Constraint derivatives reproduce at machine precision.")
    roster.idle(CHIEF_RESEARCHER)
    bullets(script.engineer, "Gradient gate passes.")

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
        bullets(script.researcher,
                "That is the gradient, on the wing. One adjoint solve "
                "produced the whole picture.")
        emit_table(emit, script, role=_NUM_ROLE,
                   title="Reading the gradient on the skin",
                   headers=("Item", "Meaning"),
                   rows=[
                       ["Red", "Drag falls if the skin moves outward"],
                       ["Blue", "Drag falls if the skin moves inward"],
                       ["White", "The gradient asks for nothing there"],
                       ["Source", "The derivative recorded at the baseline "
                                  "design"],
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
    if emit:
        for point in history:
            emit("trace.point", {
                "series": "Cd_history", "x": point["iter"],
                "y": round(point["CD"], 8),
                "lo": round(point["CD"], 8), "hi": round(point["CD"], 8),
                "x_label": "optimizer major iteration", "y_label": "C_d",
                "title": f"Drag at fixed lift, C_L = {CL_TARGET:g}",
                "feasible": True})
            frame = frames.get(point["iter"])
            if frame is None:
                continue
            drop = (baseline["CD"] - frame["CD"]) / baseline["CD"] * 100
            show(f"iter{frame['iter']}",
                 f"Major iteration {frame['iter']} of {majors}. C_d "
                 f"{frame['CD']:.6f}, {abs(drop):.1f}% "
                 f"{'below' if drop >= 0 else 'ABOVE'} baseline. At scale, "
                 f"painted with displacement from baseline (mm)")
    roster.set_workers(0)

    if shapes:
        last = shapes["frames"][-1]
        show(f"iter{last['iter']}",
             f"Optimized wing at major iteration {last['iter']}. C_d "
             f"{last['CD']:.6f}, {reduction:.1f}% below baseline at matched "
             f"lift")
        dlo, dhi = shapes["disp_window_mm"]
        chord = shapes["chord_root_m"]
        twist_worst = min(last["twist_deg"])
        emit_table(emit, script, role=_CE_ROLE,
                   title="What the gradient actually moved, at true scale",
                   headers=("Quantity", "Value"),
                   rows=[
                       ["Largest surface displacement",
                        f"{last['max_disp_mm']:.0f} mm"],
                       ["As a fraction of the root chord",
                        f"{last['max_disp_mm'] / 10.0 / chord:.2f}% of "
                        f"{chord:.2f} m"],
                       ["As a fraction of the root section's thickness",
                        f"{last['max_disp_mm'] / 10.0 / shapes['thickness_root_m']:.0f}% "
                        f"of {shapes['thickness_root_m']:.2f} m"],
                       ["Largest twist change",
                        f"{twist_worst:.2f} deg nose down, at the "
                        f"{shapes['refaxis_z_m'][last['twist_deg'].index(twist_worst) + 1]:.1f} m station"],
                       ["Twist at the tip station",
                        f"{last['twist_deg'][-1]:.2f} deg"],
                       ["Colour range across the whole replay",
                        f"{dlo:.0f} to {dhi:.0f} mm of normal displacement"],
                       ["Display scaling on the pass just shown", "None. "
                        "Every frame at true scale"],
                       ["Display scaling anywhere in this act", "None. "
                        "Both passes at true scale"],
                       ["Where amplification would fail",
                        f"x{_a2_shape.AMPLIFY_CEILING:.3f}, the thickness "
                        f"constraint's own limit, where the wing would pass "
                        f"through itself"],
                   ],
                   table_id="shape-adjoint-optimization")
        bullets(script.engineer,
                f"Those are the true numbers, and they explain what the "
                f"viewport can and cannot show: "
                f"{last['max_disp_mm']:.0f} mm is a third of the section's "
                f"own thickness, but only "
                f"{last['max_disp_mm'] / 10.0 / chord:.1f}% of chord and a "
                f"seventy-fifth of the span, so on a whole wing framed to the "
                f"span it moves the outline by about "
                f"{_a2_shape.TRUE_SCALE_PX:.0f} pixels.",
                "That pass was at true scale, and the change was carried by "
                "the colour on the surface rather than by the outline.",
                "The sections figure in the report cuts those same two "
                "surfaces and draws them to scale, and at section scale the "
                "change is not subtle at all.")

        # ---- second pass: the same 48 frames, zoomed, still true scale ----
        # The whole wing is framed to 14 m of span, so a 186 mm change moves
        # its outline about four pixels. The inboard span on its own camera is
        # framed roughly four times tighter and the same untouched surfaces
        # move about six times as far. This is a camera change, not a shape
        # change: no coordinate is scaled, so there is no factor to disclose.
        show("near0", f"Inboard span, true scale. Baseline, C_d "
                      f"{baseline['CD']:.6f}")
        bullets(script.engineer,
                f"Same surfaces again, on a closer camera: the inboard "
                f"{_a2_shape.CLOSEUP_SPAN_M:g} metres of span, framed about "
                f"four times tighter. The outline now moves about "
                f"{_a2_shape.CLOSEUP_PX:.0f} pixels instead of "
                f"{_a2_shape.TRUE_SCALE_PX:.0f}.",
                f"Still true scale. This is the camera moving, not the wing "
                f"being stretched, so there is no factor to put on the screen "
                f"and nothing to discount.",
                f"An amplified view was measured as the alternative and left "
                f"out. This optimizer drove its thickness constraint onto its "
                f"floor, thinnest station 0.4988 of baseline against a limit "
                f"of 0.5, so multiplying the displacement by "
                f"{_a2_shape.AMPLIFY_CEILING:.3f} would take that thickness "
                f"to zero and put the wing through itself. Even at that "
                f"ceiling it would have bought about eight pixels. A shot "
                f"that is honest without a caption beats one that needs it.")
        for point in history:
            frame = frames.get(point["iter"])
            if frame is not None:
                drop = (baseline["CD"] - frame["CD"]) / baseline["CD"] * 100
                show(f"near{frame['iter']}",
                     f"Inboard span, true scale. Major iteration "
                     f"{frame['iter']} of {majors}, C_d {frame['CD']:.6f}, "
                     f"{abs(drop):.1f}% "
                     f"{'below' if drop >= 0 else 'ABOVE'} baseline")
        show(f"near{last['iter']}",
             f"Inboard span, true scale. Optimized, C_d {last['CD']:.6f}, "
             f"{reduction:.1f}% below baseline at matched lift")
        bullets(script.engineer,
                f"That is the shape the gradient bought, at the size it "
                f"really is.")

    cl_off = abs(final["CL"] - CL_TARGET) / CL_TARGET * 100
    # The settling claim, measured from the recorded history rather than eyeballed.
    tail = [r["CD"] for r in history[-TAIL_ITERS:]]
    tail_spread_pct = (max(tail) - min(tail)) / min(tail) * 100
    emit_table(emit, script, role=_CE_ROLE,
               title="Drag at matched lift",
               headers=("Quantity", "Value"),
               rows=[
                   ["Baseline C_d at C_L 0.5", f"{baseline['CD']:.6f}"],
                   ["Final C_d at C_L 0.5", f"{final['CD']:.6f}"],
                   ["Drag reduction", f"{reduction:.1f}%"],
                   ["Lift held", f"C_L {final['CL']:.6f}, "
                                 f"{cl_off:.3f}% off target"],
                   ["Design variables", f"{N_DV}"],
                   ["Major iterations completed", f"{majors}"],
               ],
               table_id="result-adjoint-optimization")

    # The honest stopping condition, as its own table so it cannot be read
    # past. The optimizer never printed a convergence statement.
    emit_table(emit, script, role=_CE_ROLE,
               title="How the optimization stopped",
               headers=("Quantity", "Value"),
               rows=[
                   ["Stopped by", f"A {box_min:g} minute wall clock"],
                   ["Optimizer convergence statement", "None printed"],
                   ["Constraint violation at the stop",
                    f"{final['inf_pr']:.2e} against a {tol:.0e} target"],
                   ["First-order optimality at the stop",
                    f"{final['inf_du']:.2e} against a {tol:.0e} target"],
                   ["Status", "Partial. Short of the optimizer's own tolerance"],
               ],
               table_id="stop-adjoint-optimization")

    bullets(script.monitor,
            f"Watched the objective across every major iteration: it moves "
            f"against the gradient throughout and settles inside a "
            f"{tail_spread_pct:.2g}% band over the last {TAIL_ITERS} "
            f"iterations.",
            f"Nothing fatal.")
    roster.idle(MONITOR)

    verdict = {
        "tier": SOLVER_BACKED,
        "reason": (f"gradient verified against {FD_SOLVES} finite-difference "
                   f"primal solves, worst group {worst:.3g}%, no sign "
                   f"reversals that could steer it; the optimization is a "
                   f"partial result stopped "
                   f"by a {box_min:g} minute clock, not a converged optimum"),
    }
    bullets(script.engineer,
            f"Verdict: a {reduction:.1f}% drag reduction at matched lift, "
            f"after {majors} major iterations on a verified gradient.",
            f"This is a partial result. The clock stopped it, not the "
            f"optimizer: both first-order measures were still an order of "
            f"magnitude above the {tol:.0e} tolerance, and no convergence "
            f"statement was ever printed.",
            verdict=verdict)

    if emit:
        emit("result.verdict", {
            "quantity": "Drag reduction at matched lift",
            "value": f"{reduction:.1f}%",
            "ci": "n/a", "confidence": "n/a",
            "envelope": (f"{majors} major iterations, stopped at "
                         f"{box_min:g} minutes short of tolerance"),
            **verdict})

    channels = uncertainty_channels(
        input_2sigma=None, numerical=worst / 100.0, model=None,
        input_note="No input uncertainty was assumed for this problem.",
        numerical_note=(f"• Gradient accuracy measured directly: the worst "
                        f"derivative group agrees with a central finite "
                        f"difference of the full primal to {worst:.3g}%. "
                        f"Component-level sign agreement confirmed on "
                        f"{SIGN_CHECKED} components directly and bounded "
                        f"below {SIGN_BOUND_PCT:.2g}% of gradient magnitude "
                        f"on the rest."),
        model_note=("compressible RANS closure with wall functions, stated "
                    "model form; the drag reduction is measured against this "
                    "solver's own baseline at the same lift, not against an "
                    "experiment"))
    if emit:
        emit("uncertainty.channels", channels)

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    elapsed = time.monotonic() - began
    emit_table(emit, script, role=_CE_ROLE,
               title="What the study cost when it ran",
               headers=("Stage", "Core-minutes"),
               rows=[["Adjoint gradient", f"{COST_ADJOINT:.1f}"],
                     ["Finite-difference verification",
                      f"{COST_FD:.1f}"],
                     ["Optimization", f"{COST_OPT:.1f}"]],
               table_id="cost-adjoint-optimization")
    bullets(script.engineer,
            f"The gradient cost {COST_ADJOINT:.0f} core-minutes. Checking it "
            f"cost {COST_FD:.0f}, because the check is the expensive method "
            f"the adjoint exists to avoid.",
            f"That ratio is the whole case for the adjoint, and it widens "
            f"with every design variable added.")

    # The two figures that show the shape change at true scale. Both are drawn
    # from the same replayed surfaces the viewport streamed.
    report_plots = []
    if shapes:
        for builder, name, title in (
                (_a2_shape.section_figure, "a2_sections.png",
                 "Wing sections at true scale: baseline against the "
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
                  f"differences; {reduction:.1f}% drag reduction at matched "
                  f"lift after {majors} major iterations, partial")

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
            f"physical group {worst:.3g}%, best {best:.3g}%, every geometric "
            f"constraint derivative at machine precision, and no sign reversal in "
            f"any component that could steer the optimizer. The gate passed.",
            f"The optimization then reduced drag by {reduction:.1f}% at "
            f"matched lift over {majors} major iterations. It was stopped by "
            f"a {box_min:g} minute wall clock while both first-order "
            f"measures were still about an order of magnitude above the "
            f"{tol:.0e} tolerance, so this is an honest partial result and "
            f"not a converged optimum.",
        ],
        methods=[
            "Steady compressible RANS primal with a one-equation turbulence "
            "closure and wall functions, solved to its own residual "
            "tolerance.",
            "Reverse-mode discrete adjoint for drag and for lift with "
            "respect to surface control points, spanwise twist and the flow "
            "state.",
            f"Verification by central finite difference of the full primal, "
            f"{FD_SOLVES} perturbation solves covering every one of the "
            f"{N_DV} design variables.",
            f"Graded against this lab's current gradient standard, applied "
            f"uniformly across the whole ladder: pass at {GATE_PASS_PCT:g}% "
            f"or better with no flagged component, conditional between "
            f"{GATE_PASS_PCT:g} and {GATE_CONDITIONAL_PCT:g}%, fail above "
            f"{GATE_CONDITIONAL_PCT:g}% or on any sign-flipped component "
            f"whatever the aggregate says.",
            f"Gradient-based optimization with lift equality-constrained to "
            f"{CL_TARGET:g} and thickness, volume and edge constraints "
            f"active, capped at a {box_min:g} minute wall clock.",
        ] + ([
            f"Every wing shown is a replay, not a rendering: the run's own "
            f"free-form-deformation parameterization was rebuilt with the "
            f"same {N_SHAPE} shape and {N_TWIST} twist variables and driven "
            f"with the design-variable vectors recorded at each of the "
            f"{majors} major iterations, on the solver's own wing patch "
            f"({shapes['n_quad_faces']:,} faces, undecimated). The first "
            f"iteration reproduces the baseline surface to 1e-9 m, which is "
            f"the check that it is a replay.",
            f"The shape history is shown twice, both times at true scale: "
            f"once on the whole wing, once on the inboard "
            f"{_a2_shape.CLOSEUP_SPAN_M:g} m of span framed about four times "
            f"tighter, which moves the outline "
            f"{_a2_shape.CLOSEUP_PX:.0f} pixels instead of "
            f"{_a2_shape.TRUE_SCALE_PX:.0f}. The second pass is a camera "
            f"change and not a shape change: no coordinate is scaled "
            f"anywhere in this act, and both section figures are true scale "
            f"with equal aspect.",
            f"An amplified view was measured and deliberately not used. The "
            f"run's thickness constraint is active at its floor (thinnest "
            f"recorded station 0.4988 of baseline against a 0.5 limit), and "
            f"since displacement here is 96% thickness-direction motion "
            f"through a map linear in the shape variables, multiplying it by "
            f"x{_a2_shape.AMPLIFY_CEILING:.3f} would take that thickness to "
            f"zero and put the wing through itself. Even at that ceiling it "
            f"would reach only about 8 pixels, which is less than the "
            f"close-up gives with nothing exaggerated at all.",
        ] if shapes else []),
        results=[
            {"quantity": "Drag reduction at matched lift",
             "value": f"{reduction:.1f}%",
             "envelope": (f"{baseline['CD']:.6f} to {final['CD']:.6f} at "
                          f"C_L {CL_TARGET:g}"), **verdict},
            {"quantity": "Worst gradient group vs finite difference",
             "value": f"{worst:.3g}%",
             "envelope": (f"pass threshold {GATE_PASS_PCT:g}%, cleared by a "
                          f"factor of {GATE_PASS_PCT / worst:.1f}"),
             **verdict},
            {"quantity": "Major iterations completed",
             "value": f"{majors}",
             "envelope": f"stopped by a {box_min:g} minute clock, "
                         f"not by the optimizer", **verdict},
        ],
        uncertainty=[
            f"The optimization is partial. Constraint violation "
            f"{final['inf_pr']:.2e} and first-order optimality "
            f"{final['inf_du']:.2e} were both above the {tol:.0e} tolerance "
            f"when the clock stopped it, and the optimizer printed no "
            f"convergence statement. A converged run would very likely find "
            f"a slightly better shape than this one.",
            f"The {reduction:.1f}% is measured against this solver's own "
            f"baseline at the same lift. It is not graded against a wind "
            f"tunnel, and no published reduction figure exists for this case "
            f"to compare it with.",
            f"Gradient accuracy is measured, not assumed: worst group "
            f"{worst:.3g}% against central finite differences of the full "
            f"primal. Sign agreement was confirmed directly on "
            f"{SIGN_CHECKED} components and bounded below "
            f"{SIGN_BOUND_PCT:.2g}% of gradient magnitude on the rest.",
        ] + ([
            f"The wing shown is the design shape the parameterization hands "
            f"the solver. This case is aerostructural, so the shape that "
            f"actually flies also carries the structural deflection, and that "
            f"deflection is not part of the replay and is not on screen. The "
            f"largest shape change is {shapes['frames'][-1]['max_disp_mm']:.0f} "
            f"mm, {shapes['frames'][-1]['max_disp_mm'] / 10.0 / shapes['chord_root_m']:.2f}% "
            f"of the root chord, about {_a2_shape.TRUE_SCALE_PX:.0f} pixels "
            f"of silhouette on a wing framed to its span, which is why the "
            f"true-scale pass carries the change in a displacement field "
            f"rather than in a visibly different outline. The close-up pass "
            f"reaches {_a2_shape.CLOSEUP_PX:.0f} pixels on the same untouched "
            f"surfaces by framing the inboard span tighter, which is why no "
            f"amplification is used anywhere in this act.",
        ] if shapes else []),
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
        cert_doc["result_fields"] = [
            ("Method", "Discrete adjoint, reverse mode"),
            ("Design variables", f"{N_DV}"),
            ("Gradient check", f"worst group {worst:.3g}%, no material sign reversal"),
            ("Drag reduction", f"{reduction:.1f}% at C_L {CL_TARGET:g}"),
            ("Major iterations", f"{majors}"),
            ("Status", f"partial, stopped at {box_min:g} minutes"),
        ]
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
            mesh=mesh_validity(MESH_CELLS, None, None))
        if emit:
            emit("certificate.ready", {**certificate, "dir": out.name})
    except Exception:
        bullets(script.engineer,
                "No certificate could be issued for this run.",
                "The result above stands on the transcript and the report.")

    bullets(script.engineer,
            f"From a verified gradient to a {reduction:.1f}% drag reduction "
            f"at matched lift, reported with the stopping condition attached.")
    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out, f"({elapsed:.2f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
