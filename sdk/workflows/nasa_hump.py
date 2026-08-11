"""Act 6 — the NASA wall-mounted hump: a separated turbulent boundary layer
against NASA's own published wind-tunnel and CFD record.

The Glauert-Goldschmied hump (chord 0.42 m, Re_c 936,000, M 0.1) is a
classic separated-flow validation case: the flow leaves the wall partway
down the hump and reattaches downstream, and the location of both events is
published by NASA's own Turbulence Modeling Resource, both from the real
wind tunnel and from NASA's own CFD. A steady k-omega SST solve is known to
get the separation point close and over-predict how far downstream the flow
reattaches — that is the textbook linear-eddy-viscosity deficiency, not a
bug, and this act's gate is built to say exactly that rather than hide it.

This act stages the case's own mesh (a benchmark asset, not one this act
generates by snapping an STL) and solves it fresh. A fourfold refinement of
that mesh is on the permanent record, and the numerical channel reports the
spread it measured on the graded station: the refined rung is not in the
asymptotic range, so the act states that measured spread and extrapolates no
band from it.

    python -m workflows.nasa_hump
"""
from __future__ import annotations

import math
import re
import time
from pathlib import Path

from . import (OUT_ROOT, RUN_PREFIX, announce_field, announce_geometry,
               announce_plot, make_transcript, withdraw_certificate)
from chief_engineer.compute_audit import audit
from chief_engineer.display_names import display_name
from chief_engineer.head_engineer import HeadEngineer
from chief_engineer.researcher import ENGINEER_ACK, MissionProperties, method_memo
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, MONITOR, PLAN, SOLVER_BACKED,
                                UNCONVERGED, VALIDATED, ComputeLedger, KnowledgeBase,
                                Roster, lab_report, per, uncertainty_channels)
from chief_engineer.transcript import CHIEF_ENGINEER as _CE_ROLE
from chief_engineer.transcript import NUMERICIST as _NUM_ROLE

from .geometry_study import (INPUT_ASSUMED_NOTE, MAX_NON_ORTHOGONALITY,
                             MAX_SKEWNESS, _emit_table, mesh_gates_pass,
                             mesh_validity)

LABEL = "nasa_hump"
SURFACE = "nasa_hump.stl"
CASE_TEMPLATE = (Path(__file__).resolve().parents[2] / "demo-output" / "website"
                / "dafoam" / "f6a_nasa_hump" / "case_template")
CASE_DEF = CASE_TEMPLATE / "caseDef"
GATE_SOURCE = "NASA Turbulence Modeling Resource, wall-mounted hump experiment"
CHORD = 0.42
EXP_SEPARATION_XC = 0.665
EXP_REATTACH_XC = 1.100
SEPARATION_GATE = 0.05          # +/-5% of chord location: a clean solve should land here
REATTACHMENT_MODEL_BAND = 0.20  # wide, stated model-form band for the known SST bias
BUDGET_ITERATIONS = 2000        # this case's own endTime; SIMPLE stops on residualControl

# Grid sensitivity of the graded station: the separation station measured on
# this case's own mesh and on that mesh refined fourfold, 51,626 cells to
# 206,504. Both rungs and both stations are on the permanent record in
# demo-output/website/campaign/F6a_epistemic_band.md; the rung sizes are kept
# here rather than narrated, so the basis stays visible to a reader of the
# source without putting two more numbers on camera.
#
# The DIFFERENCE of these two is the numerical channel's figure, and nothing
# is extrapolated from it: the refined rung is not in the asymptotic range,
# so this pair supports a statement about how little the separation station
# moves under refinement and does not support a Richardson band. Inventing
# one from two rungs outside that range would be manufacturing a number.
REFINEMENT_SEPARATION_XC = (0.6396, 0.6398)

# Solver-log taps for the streaming trace: the iteration header and the
# streamwise momentum residual the steady solver prints on every iteration.
_TIME_RE = re.compile(r"^Time = (\d+)")
_MOMENTUM_RESIDUAL_RE = re.compile(
    r"Solving for Ux,\s*Initial residual = ([-+0-9.eE]+)")
_TRACE_MIN_INTERVAL_S = 0.75    # at most a few points a second on the wire

# The wall this act solves is 1.523 m long and the hump stands 0.054 m off it,
# 3.5% of the body's longest side. The viewport infers "draw the planform"
# whenever the third extent falls under 12% of the longest, so this body trips
# that inference, and the planform camera on a wall-bounded body looks along
# the wall and draws a featureless sliver with no hump in it. The decision is
# pinned here instead, which is what the hint exists for. The axes are left
# alone: the case's own convention (streamwise x, spanwise y, height z)
# already suits the fixed camera, and only an even permutation would be
# honoured anyway, since an odd one mirrors the body.
HUMP_VIEW = {"flat": False}
# The wall patch carrying the solved surface field. This case is wall bounded:
# the body IS the tunnel floor, so the patch is named for the floor rather
# than for a vehicle, and the painter has to be told which one to paint.
WALL_PATCH = "bottom"
# The value the case's own definition evaluates to, kept as the fallback so a
# parse failure can never take the act down. ``freestream_velocity`` reads it
# from the case; this is the same expression, already evaluated.
UINF_FALLBACK = 34.62531106959954

# Which quantity the painted wall carries. Pressure is the default everywhere
# and stays fully supported; this act selects the coefficient, which on a
# wall-bounded body reads better than pascals and puts the painted wall on
# the same scale as the wall curve beside it. Flip this to False and the act
# paints pressure with nothing else changed. A caller may override it for one
# run with a ``field_quantity`` parameter of "cp" or "pressure".
PAINT_AS_CP = True

GEOMETRY_DIR = Path(__file__).resolve().parents[1] / "geometry"

_CASE_DEF_ENTRY = re.compile(r"^\s*(\w+)\s+([-+0-9.eE]+)\s*;", re.M)


def announce_body(emit, out: Path, label: str) -> None:
    """Put the wall in the viewport under the pinned camera.

    The surface is the act's own body file read by the same reader every
    viewport payload goes through, with ``HUMP_VIEW`` added and nothing else:
    not one coordinate is touched. It is written into the act's own output
    directory and announced from there because the shared surface route
    carries no camera hint, and without the hint this body draws as a sliver.
    Any failure falls back to that shared route, so the body always reaches
    the screen.
    """
    if emit is None:
        return
    import json

    try:
        from chief_engineer.geometry import load_surface

        payload = load_surface(GEOMETRY_DIR / SURFACE)
        payload["view"] = HUMP_VIEW
        target = out / f"{LABEL}_body.json"
        target.write_text(json.dumps(payload), encoding="utf-8")
    except Exception:
        announce_geometry(emit, name=SURFACE, label=label)
        return
    emit("geometry.ready", {"url": f"/api/field/{out.name}/{target.name}",
                            "label": label})


def freestream_velocity(case_def: Path = CASE_DEF) -> float:
    """The case's own freestream velocity, in m/s.

    PROVENANCE, kept here because it is dropped from the narration: this is
    read out of the case definition the benchmark ships rather than carried
    as a literal. The reference Mach number and the reference temperature are
    the case's own; the freestream is the speed of sound at that temperature
    times that Mach number. The dynamic pressure the painted coefficient is
    normalised against is half its square, kinematic to match the
    incompressible solver's own p over rho.
    """
    try:
        entries = dict(_CASE_DEF_ENTRY.findall(
            case_def.read_text(errors="replace")))
        return float(entries["Mref"]) * math.sqrt(
            float(entries["gamma"]) * float(entries["R"])
            * float(entries["Tref"]))
    except (OSError, KeyError, ValueError):
        return UINF_FALLBACK


def paints_coefficient(params: dict) -> bool:
    """Whether this run paints the coefficient rather than the pressure.

    The act's own setting, overridable for one run. Anything unrecognised
    leaves the act's setting alone rather than guessing.
    """
    choice = str((params or {}).get("field_quantity") or "").strip().lower()
    if choice in {"cp", "coefficient"}:
        return True
    if choice in {"p", "pressure"}:
        return False
    return PAINT_AS_CP


def _read_raw(text: str, ncols: int) -> tuple[list[float], list[list[float]]]:
    xs: list[float] = []
    vals: list[list[float]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        xs.append(float(parts[0]))
        vals.append([float(v) for v in parts[3:3 + ncols]])
    return xs, vals


def _crossings(xc: list[float], f: list[float]) -> list[tuple[float, str]]:
    out = []
    for i in range(len(xc) - 1):
        if f[i] == 0:
            continue
        if (f[i] > 0) != (f[i + 1] > 0):
            xc0 = xc[i] - f[i] * (xc[i + 1] - xc[i]) / (f[i + 1] - f[i])
            typ = "separation" if f[i] > 0 else "reattachment"
            out.append((xc0, typ))
    return out


def compute_gate(engineer: HeadEngineer, remote_case: str, time_dir: str,
                 uinf: float) -> dict:
    """Read the wall-sampled skin friction and pressure at the converged time
    and locate separation and reattachment the same way the lab's own
    reference analysis does: sign changes of Cf along the wall."""
    q = 0.5 * uinf * uinf
    tau_raw = engineer._wsl(
        f"cat {remote_case}/postProcessing/wallValues/{time_dir}/"
        f"wallShearStress_wallValues.raw 2>/dev/null", timeout=120).stdout
    p_raw = engineer._wsl(
        f"cat {remote_case}/postProcessing/wallValues/{time_dir}/"
        f"p_wallValues.raw 2>/dev/null", timeout=120).stdout
    x_tau, tau = _read_raw(tau_raw, 3)
    x_p, pvals = _read_raw(p_raw, 1)
    if not x_tau or not x_p:
        return {}
    order = sorted(range(len(x_tau)), key=lambda i: x_tau[i])
    xc_tau = [x_tau[i] / CHORD for i in order]
    cf = [-tau[i][0] / q for i in order]
    order2 = sorted(range(len(x_p)), key=lambda i: x_p[i])
    xc_p = [x_p[i] / CHORD for i in order2]
    p = [pvals[i][0] for i in order2]
    x0 = min(xc_p)
    upstream = [v for x, v in zip(xc_p, p) if x < x0 + 0.15]
    p_ref = sum(upstream) / len(upstream) if upstream else 0.0
    cp = [(v - p_ref) / q for v in p]

    crossings = _crossings(xc_tau, cf)
    bubble = [c for c in crossings if 0.3 < c[0] < 1.6]
    separation = next((xc for xc, typ in bubble if typ == "separation"), None)
    reattachment = next((xc for xc, typ in bubble if typ == "reattachment"), None)
    # The measured distributions travel with the summary: the two zero
    # crossings below are read off exactly these arrays, so the figures the
    # act draws are the same numbers the gate is decided on.
    return {"n_wall_points": len(xc_tau), "separation_xc": separation,
            "reattachment_xc": reattachment, "cf_min": min(cf), "cf_max": max(cf),
            "cp_min": min(cp), "cp_max": max(cp), "p_ref": p_ref, "q_inf": q,
            "xc_tau": xc_tau, "cf": cf, "xc_p": xc_p, "cp": cp,
            "crossings": crossings}


_XC_LABEL = r"chordwise station  $x/c$  [dimensionless]"


def skin_friction_figure(out_png, xc, cf, separation=None, reattachment=None):
    """Cf along the wall, with the measured zero crossings marked.

    Every point drawn here is a wall sample from the converged state; the two
    marked stations are the sign changes this act grades on, not annotations
    placed by hand. Returns None if a figure cannot be drawn, so a missing
    plotting backend never takes down the act.
    """
    try:
        from chief_engineer import plot_theme as t

        plt = t._pyplot()
        fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
        ax.axhline(0.0, color=t.MUTED, linewidth=1.2, linestyle=(0, (4, 4)),
                   label="zero wall shear")
        ax.fill_between(xc, 0.0, cf, where=[v < 0 for v in cf],
                        interpolate=True, color=t.NEEDS, alpha=0.16,
                        linewidth=0, label="reversed flow at the wall")
        ax.plot(xc, cf, color=t.LIVE, linewidth=1.8,
                label=f"wall samples ({len(xc):,} points)")
        marks = (("separation", separation, t.TREND, (-8, 22), "right"),
                 ("reattachment", reattachment, t.VALID, (8, -34), "left"))
        for name, station, color, offset, align in marks:
            if station is None:
                continue
            ax.axvline(station, color=color, linewidth=1.4,
                       linestyle=(0, (3, 3)))
            ax.annotate(f"{name}\n$x/c = {station:.3f}$", xy=(station, 0.0),
                        xytext=offset, textcoords="offset points", ha=align,
                        fontsize=10.5, color=color, fontfamily="monospace",
                        weight="bold")
        # Headroom above the curve so the legend never sits on the data.
        low, high = min(cf), max(cf)
        span = (high - low) or 1e-6
        ax.set_ylim(low - 0.12 * span, high + 0.45 * span)
        t.style_axes(ax, _XC_LABEL, r"skin friction $C_f$ [dimensionless]",
                     "Skin friction along the wall, the two sign changes "
                     "that fix the bubble")
        leg = ax.legend(frameon=False, fontsize=10, labelcolor=t.INK,
                        loc="upper right")
        for text in leg.get_texts():
            text.set_color(t.INK)
        fig.tight_layout()
        fig.savefig(out_png)
        plt.close(fig)
        return str(out_png)
    except Exception:
        return None


def surface_pressure_figure(out_png, xc, cp, separation=None,
                            reattachment=None):
    """Cp along the wall, referenced to the measured upstream pressure."""
    try:
        from chief_engineer import plot_theme as t

        plt = t._pyplot()
        fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
        ax.axhline(0.0, color=t.MUTED, linewidth=1.0, linestyle=(0, (4, 4)))
        ax.plot(xc, cp, color=t.TREND, linewidth=1.8,
                label=f"wall samples ({len(xc):,} points)")
        peak = min(range(len(cp)), key=lambda i: cp[i])
        ax.scatter([xc[peak]], [cp[peak]], s=110, color=t.TREND,
                   edgecolor=t.INK, linewidth=1.2, zorder=5,
                   label="strongest suction")
        # Flip the label inboard if the suction peak sits near the right edge.
        span_x = (max(xc) - min(xc)) or 1.0
        rightish = (xc[peak] - min(xc)) / span_x > 0.6
        ax.annotate(f"$C_p = {cp[peak]:.3f}$ at $x/c = {xc[peak]:.3f}$",
                    xy=(xc[peak], cp[peak]),
                    xytext=(-12 if rightish else 12, -6),
                    textcoords="offset points",
                    ha="right" if rightish else "left", fontsize=11,
                    color=t.INK, fontfamily="monospace", weight="bold")
        for name, station, color in (("separation", separation, t.TREND),
                                     ("reattachment", reattachment, t.VALID)):
            if station is None:
                continue
            ax.axvline(station, color=color, linewidth=1.2,
                       linestyle=(0, (3, 3)), alpha=0.8,
                       label=f"{name}, read from skin friction")
        low, high = min(cp), max(cp)
        span = (high - low) or 1e-6
        ax.set_ylim(low - 0.16 * span, high + 0.45 * span)
        t.style_axes(ax, _XC_LABEL, r"pressure $C_p$ [dimensionless]",
                     "Surface pressure along the wall, referenced to the "
                     "measured upstream value")
        leg = ax.legend(frameon=False, fontsize=10, labelcolor=t.INK,
                        loc="upper right")
        for text in leg.get_texts():
            text.set_color(t.INK)
        fig.tight_layout()
        fig.savefig(out_png)
        plt.close(fig)
        return str(out_png)
    except Exception:
        return None


def comparison_figure(out_png, rows):
    """Each measured wall event against its published station and band.

    ``rows`` are ``(name, measured_xc, published_xc, band_fraction)`` tuples,
    all four values already measured or already on the case's record.
    """
    try:
        from chief_engineer import plot_theme as t

        plt = t._pyplot()
        rows = [r for r in rows if r[1] is not None]
        if not rows:
            return None
        fig, ax = plt.subplots(figsize=(9.0, 4.6), dpi=150)
        ticks, labels = [], []
        for index, (name, measured, published, band) in enumerate(rows):
            y = len(rows) - 1 - index
            lo, hi = published * (1 - band), published * (1 + band)
            ax.plot([lo, hi], [y, y], color=t.VALID, linewidth=16,
                    alpha=0.18, solid_capstyle="butt",
                    label="accepted band" if index == 0 else None)
            ax.plot([published, published], [y - 0.17, y + 0.17],
                    color=t.VALID, linewidth=2.6, zorder=4,
                    label="published experiment" if index == 0 else None)
            ax.scatter([measured], [y], s=150, color=t.LIVE,
                       edgecolor=t.INK, linewidth=1.2, zorder=5,
                       label="this solve" if index == 0 else None)
            deviation = (measured - published) / published * 100
            ax.annotate(f"$x/c = {measured:.3f}$  ({deviation:+.1f}%)",
                        xy=(measured, y), xytext=(0, 16),
                        textcoords="offset points", ha="center", fontsize=11,
                        color=t.INK, fontfamily="monospace", weight="bold")
            ticks.append(y)
            labels.append(name)
        ax.set_yticks(ticks)
        ax.set_yticklabels(labels)
        # A clear strip under the lowest row keeps the legend off the data.
        ax.set_ylim(-1.0, len(rows) - 0.4)
        t.style_axes(ax, _XC_LABEL, "wall event",
                     "Measured wall events against the published experiment")
        leg = ax.legend(frameon=False, fontsize=10.5, labelcolor=t.INK,
                        loc="lower center", ncol=3)
        for text in leg.get_texts():
            text.set_color(t.INK)
        fig.tight_layout()
        fig.savefig(out_png)
        plt.close(fig)
        return str(out_png)
    except Exception:
        return None


def main(request: str | None = None, params: dict | None = None,
        emit=None) -> int:
    params = dict(params or {})
    out = OUT_ROOT / "nasa-hump"
    out.mkdir(parents=True, exist_ok=True)
    shown = display_name(LABEL)

    script = make_transcript(f"Act 6: {shown}", emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    began = time.monotonic()

    script.system(request or "Request: solve the NASA wall-mounted hump and "
                             "check separation.")

    # ---------------- Hypothesis ----------------
    script.phase(HYPOTHESIS)
    roster.set(CHIEF_RESEARCHER, "selecting the method", "working")
    props = MissionProperties(
        kind="single-body-study",
        objective="the converged separation and reattachment location on a "
                  "separated turbulent boundary layer",
        dimensionality=0, regime="steady turbulent (RANS), separated flow",
        smoothness="gated", fidelity="a solved field",
        admissibility_cite="against the standard mesh-quality acceptance band")
    for line in method_memo(props):
        script.researcher(line)
    roster.idle(CHIEF_RESEARCHER)
    script.engineer(ENGINEER_ACK)

    # A surface uploaded with the prompt is acknowledged, put on screen, and
    # changes no number. This act is a comparison against a published
    # experiment: every station it reports is read off the wall of the case
    # that experiment is published with. Meshing and solving the uploaded
    # body instead would produce a different result with nothing to grade it
    # against, and reporting these stations as if they came from it would
    # attach a measurement to a body that did not produce it. So the surface
    # is shown as the reference shape and the transcript says which geometry
    # the numbers belong to, in the same breath. It gets the viewport to
    # itself through the opening beats; the wall takes over at staging.
    uploaded = str(params.get("surface") or "").strip()
    if uploaded:
        uploaded_name = display_name(uploaded)
        roster.set(CHIEF_ENGINEER, f"reading {uploaded_name}", "working")
        announce_geometry(emit, name=uploaded,
                          label=f"reference surface: {uploaded_name}")
        script.engineer(
            f"• Surface received: {uploaded_name}. "
            f"• The stations below are read off the published case's own "
            f"wall and belong to that geometry.")
    roster.set(CHIEF_ENGINEER, f"reading {shown}", "working")
    if not uploaded:
        announce_body(emit, out, shown)
    script.engineer(
        f"• Hypothesis: a quality-gated steady k-omega SST solve lands the "
        f"separation point within ±{SEPARATION_GATE * 100:.0f}% of NASA's "
        f"published experiment, and shows the known model-form bias on how "
        f"far downstream the flow reattaches. "
        f"• Falsifier: the mesh misses its gates, the residuals never settle, "
        f"or the converged separation point sits outside that band with no "
        f"stated cause.")
    # The gate is the Chief Researcher's to set: she frames and rules, the
    # engineer executes. Condensed to three short bullets, and "the real
    # tunnel" went with the condensing: "real" is never a qualifier on a
    # camera surface. Nothing measured or cited was dropped.
    roster.set(CHIEF_RESEARCHER, "setting the gate", "working")
    script.researcher(
        f"• Gate: converged separation within "
        f"±{SEPARATION_GATE * 100:.0f}% of {GATE_SOURCE}. "
        f"• Reattachment against the same source on a wider stated model-form "
        f"band. "
        f"• NASA maintains the validation record for this case, tunnel and "
        f"CFD.")
    roster.idle(CHIEF_RESEARCHER)
    script.numericist(
        f"• The mesh gates are the standard acceptance band, "
        f"{per('mesh-quality')}. "
        f"• The numerical channel carries the graded station's measured "
        f"sensitivity to a fourfold refinement, with no band extrapolated "
        f"from it.")

    # ---------------- Plan ----------------
    script.phase(PLAN)
    capacity = audit(1, memory_per_worker_mb=2048)
    if emit:
        emit("audit.completed", capacity.panel())
        emit("solver.selected", {
            "solver": "OpenFOAM", "method": "steady RANS, k-omega SST",
            "basis": "plan commits the body to the meshed-and-solved chain"})
    script.engineer(capacity.headline(), panel=capacity.panel())
    script.engineer(
        f"• Plan: receive the case's own mesh, check it against the "
        f"standard gates, then a steady solve run to its own residual "
        f"convergence. "
        f"• Skin friction and pressure are sampled along the wall at the "
        f"converged state and read for the sign changes that mark "
        f"separation and reattachment.")

    # Every number here is committed before the solver starts: the case's own
    # chord, the published stations this act is graded against, the bands
    # around them, and the mesh gates. Nothing measured has arrived yet.
    sep_lo = EXP_SEPARATION_XC * (1 - SEPARATION_GATE)
    sep_hi = EXP_SEPARATION_XC * (1 + SEPARATION_GATE)
    reattach_lo = EXP_REATTACH_XC * (1 - REATTACHMENT_MODEL_BAND)
    reattach_hi = EXP_REATTACH_XC * (1 + REATTACHMENT_MODEL_BAND)
    _emit_table(
        emit, script, role=_CE_ROLE,
        title="What would falsify this, fixed before the solve",
        headers=("Quantity", "Committed Value", "Falsified If"),
        rows=[
            ["Hump chord", f"{CHORD:.3f} m",
             "Not a gate, the benchmark's own fixed geometry"],
            ["Separation station, published experiment",
             f"x/c {EXP_SEPARATION_XC:.3f}",
             f"Converged separation sits outside x/c {sep_lo:.3f} "
             f"to {sep_hi:.3f}"],
            ["Separation gate",
             f"±{SEPARATION_GATE * 100:.0f}% of the published station",
             "Separation misses that band with no stated cause"],
            ["Reattachment station, published experiment",
             f"x/c {EXP_REATTACH_XC:.3f}",
             f"Converged reattachment sits outside x/c {reattach_lo:.3f} "
             f"to {reattach_hi:.3f}"],
            ["Reattachment model-form band",
             f"±{REATTACHMENT_MODEL_BAND * 100:.0f}% of the published station",
             "Reported against this wider band, the documented closure bias"],
            ["Mesh non-orthogonality gate", f"{MAX_NON_ORTHOGONALITY:.0f}°",
             "The received mesh exceeds it, no validated result stands"],
            ["Mesh skewness guidance", f"{MAX_SKEWNESS:.1f}",
             "The received mesh exceeds it, trust is capped"],
            ["Iteration ceiling", f"{BUDGET_ITERATIONS:,}",
             "Residuals never settle inside it"],
        ],
        table_id="plan-act6-nasa_hump")
    # The engineer commits the table; the researcher rules that it is closed.
    script.researcher(
        "• Every falsifier is on the table before the solver starts. "
        "• Nothing on it moves once wall samples arrive.")

    engineer = HeadEngineer("act6-nasa_hump", out, novel=True,
                            on_event=lambda event, payload: None)

    def on_anomaly(anomaly):
        if anomaly.kind in {"nan", "fpe"}:
            roster.set(MONITOR, f"fatal: {anomaly.kind}", "blocked")
            script.monitor(f"• Stopping the study: {anomaly.detail} during {anomaly.step}.")
        elif anomaly.kind == "residual-spike":
            roster.set(MONITOR, "residual spike flagged", "watching")
            script.monitor(f"• Residual spike during {anomaly.step}: {anomaly.detail}")
        elif anomaly.kind == "novel-warning":
            roster.set(MONITOR, "unfamiliar solver warning", "watching")
            script.monitor(f"• New on this case: {anomaly.line[:150]}")

    engineer.monitor.on_anomaly = on_anomaly

    stage_table = {"created": False}

    def stage_row(step: str, seconds: float | None, note: str,
                  time_text: str | None = None) -> None:
        # `time_text` exists for the one case where a stage has no solver time
        # to report: a warm path, which runs no solver at all. Ruling R10. The
        # stage still prints, and the Time cell says what it is rather than
        # carrying a number nothing paid for.
        _emit_table(emit, script, role=_CE_ROLE,
                    title="Pipeline stages, as run",
                    headers=("Stage", "Time", "What ran"),
                    rows=[[step, time_text or f"{seconds:.0f} s",
                           note[:1].upper() + note[1:]]],
                    table_id="stages-act6-nasa_hump", append=stage_table["created"])
        stage_table["created"] = True

    # ---------------- Evidence ----------------
    script.phase(EVIDENCE)
    roster.set(MONITOR, "watching solver output", "watching")
    roster.set(CHIEF_ENGINEER, "staging the case", "working")

    try:
        template_path = str(CASE_TEMPLATE).replace("C:", "/mnt/c").replace("\\", "/")
        engineer.stage_case(template_path)
        if uploaded:
            announce_body(emit, out, shown)
        script.engineer(
            "• Case received: the benchmark's own case, initial fields, and "
            "mesh, staged as it starts, no solved state carried over.")

        # Mesh-cache-first: the shipped mesh is stashed aside and the case's
        # own polyMesh is removed, so a warm run restores the mesh from the
        # cache before anything else -- exactly as a snapped mesh would.
        engineer._wsl(
            f"cd {engineer.remote_case} && cp -r constant/polyMesh "
            f"constant/_shipped_polyMesh && rm -rf constant/polyMesh")
        warm_mesh = engineer.restore_cached_mesh(LABEL)
        if warm_mesh:
            roster.set(CHIEF_ENGINEER, "preparing the mesh", "working")
            script.engineer("• Mesh prepared; on to the quality gates.")
            engineer._wsl(f"rm -rf {engineer.remote_case}/constant/_shipped_polyMesh")
        else:
            roster.set(CHIEF_ENGINEER, "receiving the case mesh", "working")
            started = time.monotonic()
            engineer._wsl(
                f"cd {engineer.remote_case} && mv constant/_shipped_polyMesh "
                f"constant/polyMesh")
            seconds = time.monotonic() - started
            stage_row("mesh", seconds,
                      "receiving the benchmark's own mesh, no snappyHexMesh "
                      "stage applies to this fixed case")
            engineer.save_mesh_to_cache(LABEL)

        engineer._wsl(f"cd {engineer.remote_case} && test -d 0.orig || cp -r 0 0.orig")

        stats = engineer.collect_mesh_stats()
        cells = int(stats.get("cells", 0))
        non_ortho = stats.get("max_non_orthogonality")
        skew = stats.get("max_skewness")
        if emit:
            emit("mesh.stats", {"cells": cells,
                                "max_non_orthogonality": non_ortho,
                                "max_skewness": skew})
        non_ortho_s = f"{non_ortho:.1f}°" if non_ortho is not None else "n/a"
        skew_s = f"{skew:.2f}" if skew is not None else "n/a"
        gate_ok = mesh_gates_pass(non_ortho, skew)
        skew_ok = (skew or 0) <= MAX_SKEWNESS
        roster.set(CHIEF_RESEARCHER, "ruling on mesh quality", "working")
        script.researcher(
            f"• Mesh: {cells:,} cells; non-ortho {non_ortho_s}; skew {skew_s}. "
            + (f"• Non-ortho inside the {MAX_NON_ORTHOGONALITY:.0f}° gate, discretization acceptable. "
               if gate_ok else
               f"• Non-ortho exceeds the {MAX_NON_ORTHOGONALITY:.0f}° gate, no validated result from this mesh. ")
            + (f"• Skew {skew_s} above the {MAX_SKEWNESS:.0f} guidance, caps trust."
               if not skew_ok else "• Skewness inside guidance as well."))
        roster.idle(CHIEF_RESEARCHER)

        # -- solve, fresh from the case's own initial fields --
        ranks = 4
        engineer._wsl(f"cd {engineer.remote_case} && rm -rf 0 && cp -r 0.orig 0")
        parallel = engineer.decompose_for_parallel(ranks)
        solve_key = f"{LABEL}-c{cells}-i{BUDGET_ITERATIONS}"
        warm_solve = engineer.restore_cached_solve(solve_key)
        if parallel:
            script.engineer(
                f"• The steady solve runs in parallel: same mesh, same "
                f"numbers.")

        # Telemetry while the steady solver marches: it prints the streamwise
        # momentum residual on every iteration, and this hook forwards each
        # one the moment it prints, so the viewer watches convergence happen
        # instead of a frozen screen. Read on a log scale because the residual
        # falls across several decades. Any failure inside a line hook is
        # swallowed by the runner, so telemetry can never stop a solve.
        residual_trace = {"iteration": None, "last": 0.0}

        def _residual_line_hook(line: str) -> None:
            if not emit:
                return
            match = _TIME_RE.match(line)
            if match:
                residual_trace["iteration"] = int(match.group(1))
                return
            match = _MOMENTUM_RESIDUAL_RE.search(line)
            if not match or residual_trace["iteration"] is None:
                return
            now = time.time()
            if now - residual_trace["last"] < _TRACE_MIN_INTERVAL_S:
                return
            residual_trace["last"] = now
            emit("trace.point", {
                "series": "momentum_residual",
                "x": residual_trace["iteration"],
                "y": round(math.log10(max(float(match.group(1)), 1e-12)), 4),
                "x_label": "solver iteration",
                "y_label": "log10 momentum residual",
                "title": "Momentum residual falling through the steady solve",
                "feasible": True})

        if warm_solve:
            note = "steady solve, run to its own residual convergence"
            roster.set(CHIEF_ENGINEER, note, "working")
            # NO FLEET ON THIS PATH, and this is deliberate. Ruling R2,
            # answering conflict C-3 with option B. On the warm path the mesh
            # and the solve are both restored, nothing is dispatched, and the
            # `elapsed` below is a clamped zero-length interval rather than a
            # measurement of anything. `roster.set_workers(ranks, note)` used
            # to sit here, and it reached the worker numeral on camera, the
            # roster and the spend line. A worker count is a claim about the
            # run, and a claim about a run that did not happen is the same
            # defect as a band that was never adjudicated.
            #
            # Moving the declaration earlier so the timing computes to
            # something non-zero is NOT the fix and is explicitly refused: it
            # would invent a fleet the run never used. The numeral reads zero
            # when nothing is running. The cold branch below genuinely
            # dispatches `ranks` and keeps its declaration.
            roster.set_workers(0)
            # NOTHING IS SPENT TO THE LEDGER ON THIS PATH. Ruling R10. The
            # ledger records compute this lab performed, and no solver runs
            # here. What used to sit on these lines was
            # `elapsed = max(1.0, time.time() - started)` across a zero-length
            # window, spent as `simpleFoam (1s)`: one core-second per warm run
            # credited to a solver that never started. The clamp was not the
            # defect and a longer measurement would not have been better; what
            # the interval paid for is the test, and it paid for nothing.
            #
            # The stage stays on camera. It just stops naming a cost.
            stage_row("selected solver", None,
                      f"{note}, replayed from the run that solved it",
                      time_text="none this pass")
        else:
            note = "steady solve, run to its own residual convergence"
            roster.set(CHIEF_ENGINEER, note, "working")
            roster.set_workers(ranks, note)
            command = f"mpirun -np {ranks} simpleFoam -parallel" if parallel else "simpleFoam"
            result = engineer._run_step("simpleFoam", command, 3600,
                                        line_hook=_residual_line_hook)
            ledger.spend(result.seconds, f"simpleFoam ({result.seconds:.0f}s)")
            stage_row("selected solver", result.seconds, note)
            roster.set_workers(0)
            if parallel:
                engineer.reconstruct_latest()
            engineer.save_solve_to_cache(solve_key)
    except Exception as exc:
        roster.set(CHIEF_ENGINEER, "halted", "blocked")
        step_match = re.match(r"step '(\w+)' failed", str(exc))
        stopped_at = step_match.group(1) if step_match else "a solver stage"
        script.engineer(f"• The study stopped: {stopped_at} did not complete "
                        f"cleanly; detail in the run log, not on screen.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    # ---------------- Results ----------------
    roster.set(CHIEF_ENGINEER, "reading the converged state", "working")
    solved_times = engineer._solved_time_dirs()
    if not solved_times:
        script.engineer("• No converged state from the solver, nothing to report.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1
    time_dir = solved_times[-1]
    converged_iterations = int(time_dir)

    uinf = freestream_velocity()
    roster.set(CHIEF_ENGINEER, "sampling the wall", "working")
    gate = compute_gate(engineer, engineer.remote_case, time_dir, uinf)
    if not gate or gate.get("separation_xc") is None:
        script.engineer(
            "• Wall-sampled skin friction did not show a clean separation "
            "and reattachment pair; nothing to grade against the reference.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    separation_xc = gate["separation_xc"]
    reattachment_xc = gate.get("reattachment_xc")
    sep_dev = (separation_xc - EXP_SEPARATION_XC) / EXP_SEPARATION_XC
    reattach_dev = ((reattachment_xc - EXP_REATTACH_XC) / EXP_REATTACH_XC
                    if reattachment_xc is not None else None)

    # The two wall distributions, drawn from the same arrays the gate is read
    # from. Both are optional: if a figure cannot be drawn the act carries on
    # with the numbers it already has.
    xc_tau = gate.get("xc_tau") or []
    cf_series = gate.get("cf") or []
    xc_p = gate.get("xc_p") or []
    cp_series = gate.get("cp") or []
    n_crossings = len(gate.get("crossings") or [])
    if xc_tau and len(xc_tau) == len(cf_series):
        cf_png = skin_friction_figure(
            out / "nasa_hump_skin_friction.png", xc_tau, cf_series,
            separation=separation_xc, reattachment=reattachment_xc)
        if cf_png:
            announce_plot(emit, out.name, cf_png,
                          "Skin friction along the wall, separation and "
                          "reattachment marked")
            script.engineer(
                f"• Skin friction plotted from {len(xc_tau):,} wall samples "
                f"at the converged state. "
                f"• It changes sign {n_crossings} time"
                f"{'' if n_crossings == 1 else 's'} along the wall. "
                f"• Separation and reattachment are the pair inside the "
                f"bubble.")
    if xc_p and len(xc_p) == len(cp_series):
        cp_png = surface_pressure_figure(
            out / "nasa_hump_surface_pressure.png", xc_p, cp_series,
            separation=separation_xc, reattachment=reattachment_xc)
        if cp_png:
            announce_plot(emit, out.name, cp_png,
                          "Surface pressure along the wall")
            script.engineer(
                f"• Surface pressure over the same wall, "
                f"{len(xc_p):,} samples. "
                f"• Referenced to the measured upstream pressure, not an "
                f"assumed one. "
                f"• The strongest suction is marked with its measured "
                f"station.")

    # The wall carrying its own solved surface field. Which quantity it
    # carries is this act's choice (see PAINT_AS_CP), and the reference pair
    # for the coefficient is the one the wall curve above already uses, so
    # the painted wall and that figure land on the same scale. The painter
    # decides the outcome, not the request: without a positive dynamic
    # pressure the coefficient is undefined and the pressure is painted
    # instead, so what reached the screen is read back off the payload rather
    # than assumed from what was asked for.
    roster.set(CHIEF_ENGINEER, "painting the wall with its solved field",
               "working")
    painted, painted_quantity = None, None
    try:
        import json as _json

        from chief_engineer.field_render import QUANTITY_CP, extract_and_paint

        try:
            from chief_engineer.geometry import load_surface
            input_triangles = load_surface(
                GEOMETRY_DIR / SURFACE)["triangles_total"]
        except Exception:
            input_triangles = None
        painted = extract_and_paint(
            engineer.remote_case, engineer.out_root / f"{LABEL}_field",
            RUN_PREFIX[:-1] if RUN_PREFIX and RUN_PREFIX[-1] == "openfoam2606"
            else RUN_PREFIX,
            field="p", name=LABEL, patches=(WALL_PATCH,),
            input_triangles=input_triangles,
            q_kinematic=gate["q_inf"], p_inf=gate["p_ref"],
            as_cp=paints_coefficient(params), view=HUMP_VIEW)
        if painted:
            painted_quantity = (
                (_json.loads(Path(painted).read_text(encoding="utf-8"))
                 .get("field") or {}).get("quantity"))
    except Exception:
        painted = None
    if painted:
        served = out / Path(painted).name
        try:
            served.write_bytes(Path(painted).read_bytes())
            painted = str(served)
        except OSError:
            pass
        as_cp = painted_quantity == QUANTITY_CP
        announce_field(
            emit, out.name, painted,
            f"{shown}, surface pressure coefficient (C_p)" if as_cp
            else f"{shown}, surface pressure")
        script.engineer(
            "• Wall carrying its own solved surface field, "
            + ("as a pressure coefficient." if as_cp else "as pressure."))

    gate_rows = [
        ["Converged at iteration", f"{converged_iterations:,}"],
        ["Separation x/c (converged)", f"{separation_xc:.4f}"],
        [f"Separation x/c ({GATE_SOURCE}, experiment)", f"{EXP_SEPARATION_XC:.3f}"],
        ["Separation deviation", f"{sep_dev * 100:+.1f}%"],
        ["Separation gate", f"±{SEPARATION_GATE * 100:.0f}%"],
    ]
    if reattachment_xc is not None:
        gate_rows += [
            ["Reattachment x/c (converged)", f"{reattachment_xc:.4f}"],
            [f"Reattachment x/c ({GATE_SOURCE}, experiment)", f"{EXP_REATTACH_XC:.3f}"],
            ["Reattachment deviation", f"{reattach_dev * 100:+.1f}%"],
            ["Reattachment model-form band", f"±{REATTACHMENT_MODEL_BAND * 100:.0f}%"],
        ]
    # The gate table grows a row at a time, each one landing as it is
    # decided, rather than nine rows arriving at once with nothing to watch.
    # The numericist speaks this one: measurement is hers, not the engineer's.
    for index, gate_row in enumerate(gate_rows):
        _emit_table(emit, script, role=_NUM_ROLE,
                   title="Gate: converged separation and reattachment vs the "
                         "published experiment",
                   headers=("Quantity", "Value"), rows=[gate_row],
                   table_id="gate-act6-nasa_hump", append=index > 0)
        if emit:
            time.sleep(0.6)

    sep_ok = abs(sep_dev) <= SEPARATION_GATE
    reattach_ok = reattach_dev is not None and abs(reattach_dev) <= REATTACHMENT_MODEL_BAND

    if not gate_ok:
        verdict = {"tier": SOLVER_BACKED,
                  "reason": (f"mesh quality outside the acceptance band; the "
                             f"numerical channel carries the residual, not a "
                             f"comparison with {GATE_SOURCE}")}
    elif not sep_ok:
        verdict = {"tier": SOLVER_BACKED,
                  "reason": (f"separation at x/c {separation_xc:.3f} is "
                             f"{sep_dev * 100:+.1f}% from {GATE_SOURCE}, "
                             f"outside the ±{SEPARATION_GATE * 100:.0f}% gate")}
    elif reattach_ok:
        verdict = {"tier": VALIDATED,
                  "reason": (f"separation within {abs(sep_dev) * 100:.1f}% of "
                             f"{GATE_SOURCE} and reattachment within the "
                             f"stated model-form band")}
    else:
        verdict = {"tier": SOLVER_BACKED,
                  "reason": (f"separation within {abs(sep_dev) * 100:.1f}% of "
                             f"{GATE_SOURCE}, but reattachment is "
                             f"{reattach_dev * 100:+.1f}% downstream of the "
                             f"experiment, the documented linear eddy-viscosity "
                             f"bias toward a longer separation bubble")}

    script.engineer("• Residuals settled; the wall-sampled state is read at "
                    "the converged time.", verdict=verdict)

    monitor_summary = engineer.monitor.summary()
    script.monitor(
        f"• Watched every solver line: {monitor_summary['anomalies']} watch-pattern "
        f"event{'' if monitor_summary['anomalies'] == 1 else 's'} {monitor_summary['by_kind'] or ''}. "
        + ("• Nothing fatal." if not monitor_summary["fatal"] else
           "• One fatal: do not use this result."))
    roster.idle(MONITOR)

    # Uncertainty channels, all three carrying what was measured.
    #
    # Numerical: the refinement pair above. The figure is the spread of the
    # graded station across a fourfold refinement of this case's own mesh, so
    # it is a measured sensitivity of the quantity this act reports, not a
    # band extrapolated from rungs that do not sit in the asymptotic range.
    #
    # Model: the reattachment band this act committed to before the solve,
    # expressed in the same units as the station it qualifies. It is a
    # literature constant, justified by the documented over-prediction of
    # this bubble by a linear eddy-viscosity closure, and it is the channel a
    # comparison against the published experiment belongs to.
    refinement_spread = abs(REFINEMENT_SEPARATION_XC[1]
                            - REFINEMENT_SEPARATION_XC[0])
    channels = uncertainty_channels(
        input_2sigma=None,
        numerical=refinement_spread,
        model=REATTACHMENT_MODEL_BAND * EXP_REATTACH_XC,
        input_note=INPUT_ASSUMED_NOTE,
        numerical_note=(
            f"• Separation moved {refinement_spread:.4f} in x/c under a "
            f"fourfold refinement of this mesh. "
            f"• The refined rung is not in the asymptotic range, so no band "
            f"is extrapolated from that spread."),
        model_note=(
            f"turbulence closure k-omega SST, stated model-form; band "
            f"±{REATTACHMENT_MODEL_BAND * EXP_REATTACH_XC:.3f} in x/c on the "
            f"reattachment station, the documented over-prediction of this "
            f"bubble by a linear eddy-viscosity closure; "
            + ("reattachment inside that band"
               if reattach_ok else
               "reattachment sits outside that band, stated not hidden")))
    # The total, over the channels that carry a figure. The lab's own
    # combination is the root sum of squares of the quantified channels
    # (V&V-20 treats independent channels that way), and it is the same call
    # every other act that reports a total goes through, so no act invents its
    # own arithmetic. The input channel is not in the sum and is not counted
    # as zero: it is stated as unquantified, on the table below and in the
    # channel block, so the total is read for what it covers.
    from chief_engineer import uq as uq_studies

    model_band = REATTACHMENT_MODEL_BAND * EXP_REATTACH_XC
    total = uq_studies.combine_expanded(
        input_2sigma=None, numerical_abs=refinement_spread,
        model_abs=model_band)
    combined = total["combined_95"]
    # BEYOND KATIE'S LIST, same division: the uncertainty table is measurement,
    # so the numericist presents it, and the ruling on what the total covers
    # goes to the researcher. It used to be the engineer's table with the
    # numericist explaining it, which had the two of them the wrong way round.
    _emit_table(
        emit, script, role=_NUM_ROLE,
        title="Total uncertainty on the separation station",
        headers=("Channel", "Value in x/c", "In the total"),
        rows=[
            ["Input", "Not quantified", "No, and not counted as zero"],
            ["Numerical", f"{refinement_spread:.4f}", "Yes"],
            ["Model form", f"{model_band:.4f}", "Yes"],
            ["Total", f"{combined:.4f}", "The two quantified channels"],
        ],
        table_id="uncertainty-act6-nasa_hump")
    script.researcher(
        f"• The total covers the numerical and model channels. "
        f"• No input spread was assumed for this benchmark, so that channel "
        f"is stated rather than set to zero.")
    if emit:
        emit("result.verdict", {"quantity": "Separation location (x/c)",
                                "value": f"{separation_xc:.4f}",
                                "ci": f"{combined:.4f}", "confidence": "95%",
                                "envelope": f"converged at iteration {converged_iterations:,}",
                                **verdict})
        emit("uncertainty.channels", channels)

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    # The wall clock is still measured and still reported: it is the
    # certificate's Solve Time row below. What came off the narration (Katie,
    # 2026-07-31) is the sentence that announced it alongside the convergence
    # iteration, which the gate table already carries.
    elapsed = (time.monotonic() - began) / 60
    # The measurement against the published experiment, as a table rather
    # than a sentence, with the bubble length carried alongside the two
    # stations it is the difference of.
    comparison_rows = [
        ["Separation station (x/c)", f"{separation_xc:.4f}",
         f"{sep_dev * 100:+.1f}%", f"{EXP_SEPARATION_XC:.3f}",
         (f"Inside the ±{SEPARATION_GATE * 100:.0f}% gate" if sep_ok
          else f"Outside the ±{SEPARATION_GATE * 100:.0f}% gate")]]
    if reattachment_xc is not None:
        bubble_solved = reattachment_xc - separation_xc
        bubble_published = EXP_REATTACH_XC - EXP_SEPARATION_XC
        comparison_rows += [
            ["Reattachment station (x/c)", f"{reattachment_xc:.4f}",
             f"{reattach_dev * 100:+.1f}%", f"{EXP_REATTACH_XC:.3f}",
             (f"Inside the ±{REATTACHMENT_MODEL_BAND * 100:.0f}% model-form band"
              if reattach_ok else
              f"Outside the ±{REATTACHMENT_MODEL_BAND * 100:.0f}% model-form band")],
            ["Bubble length (x/c)", f"{bubble_solved:.4f}",
             f"{(bubble_solved - bubble_published) / bubble_published * 100:+.1f}%",
             f"{bubble_published:.3f}",
             "Not gated, the difference of the two stations"],
        ]
    # BEYOND KATIE'S LIST: same class of table as the gate table in item 2,
    # measured stations against a published reference, so the same speaker.
    _emit_table(emit, script, role=_NUM_ROLE,
               title=f"Measured wall events against {GATE_SOURCE}",
               headers=("Quantity", "Value", "Deviation", "Reference",
                        "Verdict"),
               rows=comparison_rows, table_id="comparison-act6-nasa_hump")

    # The verdict is a ruling, so the Chief Researcher gives it.
    roster.set(CHIEF_RESEARCHER, "ruling on the gate", "working")
    if verdict["tier"] == VALIDATED:
        script.researcher(f"• Verdict: validated. {verdict['reason']}.")
    else:
        script.researcher(f"• Verdict: {verdict['tier'].lower()}. {verdict['reason']}.")
    roster.idle(CHIEF_RESEARCHER)

    knowledge.add(f"{shown} solved: {cells:,} cells, separation x/c "
                  f"{separation_xc:.4f}, converged at iteration "
                  f"{converged_iterations:,}")

    _AGENDA = [
        {"title": "The pressure comparison",
         "scope": "grade the wall pressure now on record against the "
                  "published C_p curve point by point, and put a gate on the "
                  "suction peak as well as on the two wall events",
         "cost": "no new solve, the converged state already carries it"},
        {"title": "Sweep the Reynolds number",
         "scope": "hold the geometry fixed and solve a small span of Re "
                  "around the published condition to see how the bubble "
                  "length moves",
         "cost": "one solve per Reynolds number on the same mesh"},
        {"title": "A corrected closure",
         "scope": "carry the same wall sampling and gate to a data-driven "
                  "correction and measure whether the reattachment bias closes",
         "cost": "one solve per candidate closure on this mesh"},
    ]
    if emit:
        emit("agenda.updated", {"entries": _AGENDA})

    # The report opens on the picture, not the prose: each measured station
    # against its published value and the band it is graded on.
    comparison_png = comparison_figure(
        out / "nasa_hump_experiment_comparison.png",
        [("separation", separation_xc, EXP_SEPARATION_XC, SEPARATION_GATE),
         ("reattachment", reattachment_xc, EXP_REATTACH_XC,
          REATTACHMENT_MODEL_BAND)])
    if comparison_png:
        announce_plot(emit, out.name, comparison_png,
                      "Measured wall events against the published experiment")

    report_doc = lab_report(
        title=f"Act 6: {shown}",
        # Prose carries no numbers: every one of them is in a table above,
        # and repeating a value in a sentence is how two versions of it
        # start to drift.
        abstract=[
            f"The benchmark's own mesh for the NASA wall-mounted hump, gate "
            f"checked and solved in OpenFOAM to its own residual "
            f"convergence, then graded against {GATE_SOURCE}.",
        ],
        methods=[
            "Case mesh received and checked against the standard quality "
            "gates.",
            "Steady k-omega SST in OpenFOAM, to the case's own convergence "
            "criteria.",
            "Wall skin friction and pressure sampled at the converged state; "
            "both events read from the sign change of skin friction.",
        ],
        # One row per quantity: value, deviation against its reference, and
        # the tier. The verdict's reasoning is stated once, on the transcript
        # and in the model channel, never repeated onto every row.
        #
        # The HEADLINE row carries the total band and nothing else. The
        # certificate prints the first result's envelope as the caption under
        # a 24 point number, so a whole sentence there ran off the page and
        # cut the reference in half. The deviation and the source it is
        # measured against are rows of the result table below, where they
        # read in full, and the headline states the band the number carries.
        results=[{
            "quantity": "Separation location (x/c)",
            "value": f"{separation_xc:.4f}",
            "envelope": f"{combined:.4f}",
            "tier": verdict["tier"],
        }] + ([{
            "quantity": "Reattachment location (x/c)",
            "value": f"{reattachment_xc:.4f}",
            "envelope": f"{reattach_dev * 100:+.1f}% vs x/c "
                        f"{EXP_REATTACH_XC:.3f}, {GATE_SOURCE}",
            "tier": verdict["tier"],
        }] if reattachment_xc is not None else []) + [{
            "quantity": "Mesh",
            "value": f"{cells:,} cells",
            "envelope": (f"non-orthogonality {non_ortho_s} vs "
                        f"{MAX_NON_ORTHOGONALITY:.0f}° "
                        f"({'pass' if gate_ok else 'caveat'}), skewness "
                        f"{skew_s} vs {MAX_SKEWNESS:.1f} "
                        f"({'pass' if skew_ok else 'caveat'})"),
            "tier": verdict["tier"],
        }],
        uncertainty=[
            f"Numerical: separation moved {refinement_spread:.4f} in x/c "
            f"under a fourfold refinement of this mesh. No band is "
            f"extrapolated from that spread.",
            f"Model: ±{REATTACHMENT_MODEL_BAND * EXP_REATTACH_XC:.3f} in x/c "
            f"on the reattachment station, the documented over-prediction of "
            f"this bubble by a linear eddy-viscosity closure. Measured "
            f"reattachment sits "
            f"{'inside' if reattach_ok else 'outside'} it.",
            INPUT_ASSUMED_NOTE,
        ],
        next_investigations=[f"{e['title']}: {e['scope']}" for e in _AGENDA],
        compute=ledger.as_dict(),
    )
    if emit:
        emit("report.ready", report_doc)

    cert_path = out / "certificate.pdf"
    # DOCKET B2. Withdrawal has THREE outcomes, not two, and the act publishes
    # the one that happened: a page that could not be removed is not a page
    # that was withdrawn.
    _withdrawn, _withdrawal = withdraw_certificate(cert_path)
    try:
        from chief_engineer.certificate import build_certificate_v2

        cert_doc = dict(report_doc)
        # The reference this act is graded against gets a row of its own, at
        # full length, rather than being crushed into the headline caption.
        cert_doc["result_fields"] = [
            ("Separation x/c", f"{separation_xc:.4f}, {sep_dev * 100:+.1f}% "
                               f"of x/c {EXP_SEPARATION_XC:.3f}"),
        ] + ([("Reattachment x/c",
               f"{reattachment_xc:.4f}, {reattach_dev * 100:+.1f}% of x/c "
               f"{EXP_REATTACH_XC:.3f}")]
             if reattachment_xc is not None else []) + [
            # The full source, on a row of its own and at full length. The
            # cell count is not repeated here: the mesh-validity block below
            # carries it with its gates.
            ("Reference", GATE_SOURCE),
            ("Converged Iteration", f"{converged_iterations:,}"),
            ("Solve Time", f"{elapsed:.1f} min"),
        ]
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path,
            geometry=shown,
            # The objective is the request, verbatim and however short it was
            # typed. What the run actually covered is the scope field's job,
            # so a one-line prompt no longer costs the page its statement of
            # what was graded and what it was graded against.
            objective=(request or "Solve the NASA wall-mounted hump and check "
                                  "separation"),
            scope=(f"Separation on a ±{SEPARATION_GATE * 100:.0f}% gate, "
                   f"reattachment on a "
                   f"±{REATTACHMENT_MODEL_BAND * 100:.0f}% stated band."),
            mission_id=f"nasa-hump-{LABEL}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels,
            display_name=shown,
            source_filename=SURFACE,
            solver="OpenFOAM, k-omega SST steady RANS",
            mesh=mesh_validity(cells, non_ortho, skew))
        if emit:
            emit("certificate.ready", {**certificate, "dir": out.name})
    except Exception:
        script.engineer(
            "• No certificate could be issued for this run. "
            f"• {_withdrawal} "
            "• The result above stands on the transcript and the report.")
    engineer.report_markdown()
    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
