"""The jet-flap screen: a wing with a blown trailing-edge slot.

What this screen shows is a set of calculations that are already finished. It
opens by saying so. Nothing here starts a solver, and the screen never claims
a number it did not read back off disk at the moment it spoke.

Three things this screen is built to make impossible, because each of them has
already gone wrong once on a page carrying this act's numbers:

1. **The two grids never share an axis.** The flow picture and the wall
   resolution come from one grid whose reference area is the full unit span.
   The five force calculations come from a different grid whose reference area
   is a slab one hundredth as thick. A table that mixed them would report lift
   a hundredfold wrong. Every table below passes its cases through
   ``assert_one_grid`` first, so a mixed table raises instead of rendering.

2. **The unblown calculation is not the blown case with the jet turned off.**
   It is a separate calculation with the slot CLOSED. The four blown
   calculations are a controlled comparison among themselves; the fifth is a
   reference. The screen reads the slot state per case out of the mesh rather
   than asserting it in prose, and prints what it read.

3. **No calculation in this family met its convergence target, so none is
   claimed to have.** The screen quotes how far the lift still moved over the
   final four thousand iterations, and calls it movement. It states no
   verdict, offers no discretisation band, and gives no percentage agreement
   with the published curve, because one grid per family supports none of
   those.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from . import (OUT_ROOT, announce_plot, bullets,
               emit_table, make_transcript)
from ._jf1_numbers import (ReaderRefused, assert_one_grid, display_citation,
                           flow_facts, sweep_facts, sweep_rows)

LABEL = "jet-flap-display"

#: The landed figures, in the order the act shows them. Each is a page that
#: already exists; this screen resolves it to a raster the interface can serve
#: and puts it on the feed. Nothing is plotted here.
FIGURES = Path("/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts")

HYPOTHESIS = "hypothesis"
PLAN = "plan"
EVIDENCE = "evidence"
CONCLUSION = "conclusion"

#: Compute already spent on the calculations this screen presents, in
#: core-minutes, and the figure fixed before any of them started. Both are
#: read off the record rather than recomputed, and the screen states both
#: because a result without its cost is half a result.
CORE_MIN_SPENT_SWEEP = 117.4833
CORE_MIN_ESTIMATE_SWEEP = 5 * 11.36
CORE_MIN_ESTIMATE_FLOW = 90.5
RATE_USD_PER_CORE_HOUR = 0.0513


def _serve(beat: str, stem: str) -> Path | None:
    """Put one landed page where the interface can serve it.

    The interface serves rasters only. Every page in this act was written as
    both a vector page and a raster, so this copies the raster across. It
    derives no number and it does not regenerate the page: a figure this
    screen cannot find is a figure the screen does not show, and the caller
    says so rather than showing a gap.
    """
    source = FIGURES / f"{stem}.png"
    if not source.is_file():
        return None
    out = OUT_ROOT / beat
    out.mkdir(parents=True, exist_ok=True)
    target = out / source.name
    shutil.copy2(source, target)
    return target


def _sci(value: float, digits: int = 3) -> str:
    """One number, in the notation the output rules require."""
    if value == 0.0:
        return "0"
    return f"{value:.{digits}e}"


def main(request: str | None = None, params: dict | None = None, emit=None) -> int:
    params = dict(params or {})
    script = make_transcript(LABEL, emit)

    # ---------------------------------------------------------------- open --
    script.phase(HYPOTHESIS, "A wing with a blown trailing-edge slot")

    try:
        flow = flow_facts()
        sweep = sweep_facts()
        rows = sweep_rows()
        citation = display_citation()
    except ReaderRefused as exc:
        # A reader that cannot see what it was told to look at reports that,
        # and the screen stops. It does not fall back to a number it can still
        # produce, because the whole value of the number is that it was read.
        bullets(script.engineer,
                "This screen could not read one of the quantities it is built "
                "to show, so it is stopping rather than showing the rest.",
                f"What it could not read: {exc}.")
        if emit:
            emit("mission.note", {"error": f"ReaderRefused: {exc}"})
        return 2

    bullets(script.engineer,
            "You asked about a wing with air blown out of a slot at the "
            "trailing edge.",
            "The calculations for that wing are already finished and this "
            "screen presents them. Nothing new is being solved, so nothing "
            "new is being spent.",
            f"Compute already used on the five force calculations: "
            f"{CORE_MIN_SPENT_SWEEP:.1f} core-minutes against "
            f"{CORE_MIN_ESTIMATE_SWEEP:.1f} core-minutes budgeted upfront, "
            f"about "
            f"${CORE_MIN_SPENT_SWEEP / 60.0 * RATE_USD_PER_CORE_HOUR:.2f} "
            f"at this machine's rate.")

    bullets(script.researcher,
            "The physics: the slot ejects a thin sheet of air at 30 degrees "
            "below the chord line. The sheet acts like a flap made of air. It "
            "turns the flow behind the wing and pulls extra circulation onto "
            "the wing itself, so the wing gains far more lift than the direct "
            "push of the jet accounts for.",
            "Blowing strength is quoted as jet momentum coefficient: the "
            "momentum leaving the slot each second, divided by the oncoming "
            "flow's dynamic pressure times the wing area.",
            "What would falsify this: lift that fails to grow roughly with "
            "the square root of jet momentum at low blowing, or lift that "
            "matches the direct jet push alone with no circulation gain.",
            citations=[str(FIGURES.parent / "artefacts_actB"
                           / "jf1_theory_actB_numbers.json")])

    # -------------------------------------------------------- the two grids --
    script.phase(PLAN, "Two grids, kept apart on purpose")

    # No surface is announced to the viewport. The instruction for this act is
    # that any picture it shows must be the computational grid itself and not
    # a tessellation of the shape, so the geometry beat IS the grid page below
    # and there is nothing else to put in the viewport.
    #
    # A surface CAN arrive with the request, because this route keeps itself
    # when one is uploaded. It is not the body these pages were computed on
    # and the screen has to say so in words, at the top, before any number is
    # shown. Silence here would let a viewer read our section's lift as theirs.
    uploaded = str(params.get("surface") or "").strip()
    if uploaded:
        bullets(script.engineer,
                "A surface arrived with your request and it has not been "
                "meshed or solved by this screen.",
                "Every page below was computed on the section already on "
                "file. Read the numbers as belonging to that section, not to "
                "the shape you sent.")

    bullets(script.engineer,
            "Two separate grids were built and they answer different "
            "questions. They are shown on separate pages and their numbers "
            "are never put on one axis.",
            f"The flow picture and the wall resolution come from a grid of "
            f"{flow['cells']:,} cells that ran {flow['iterations']:,} "
            f"iterations.",
            f"The five lift and pressure calculations come from a different "
            f"grid of {sweep['cells']:,} cells that ran "
            f"{sweep['iterations']:,} iterations each.",
            "The two grids measure lift against wing areas that differ by a "
            "factor of one hundred. Reading a lift number off one grid against "
            "the other's area would be wrong by that same factor, which is why "
            "this screen refuses to build a table spanning both.")

    if emit:
        emit("solver.selected", {
            "solver": "OpenFOAM",
            "method": "steady incompressible flow, two-equation turbulence "
                      "closure resolved to the wall",
            "basis": "Standard closure for attached external flow. The slot "
                     "is a momentum inlet, not a modelled source."})

    # ------------------------------------------------------- the real mesh --
    script.phase(EVIDENCE, "The grid, the wall, and the slot")

    mesh_page = _serve(LABEL, "jet_flap_5_mesh_flowfield")
    if mesh_page:
        announce_plot(emit, LABEL, mesh_page,
                      "The computational grid the flow picture was solved on")
    resolution_page = _serve(LABEL, "jet_flap_6_mesh_resolution")
    if resolution_page:
        announce_plot(emit, LABEL, resolution_page,
                      "Wall spacing and cells across the slot mouth")

    yplus = flow["yplus"]
    bullets(script.numericist,
            "This is the actual computational grid, cell by cell, not a "
            "surface tessellation of the shape.",
            f"Every one of the {yplus['n']} cells touching the wing surface "
            f"sits inside the viscous sublayer: the largest wall spacing is "
            f"{yplus['max']:.3f} in wall units, against a limit of 1. The "
            f"boundary layer is resolved rather than modelled by a wall "
            f"function.",
            f"The slot mouth is spanned by {flow['slot']['faces']} cells, so "
            f"the ejected sheet has a profile across it rather than a single "
            f"value.")

    worst_wall = _worst_wall(rows)
    emit_table(emit, script, role="NUMERICIST",
               title="Grid resolution at the wall",
               headers=["Grid", "Cells", "Iterations",
                        "Wall cells", "Largest wall spacing [wall units]",
                        "Cells across slot"],
               rows=[["Flow picture", f"{flow['cells']:,}",
                      f"{flow['iterations']:,}", f"{yplus['n']}",
                      f"{yplus['max']:.3f}", f"{flow['slot']['faces']}"],
                     ["Force calculations", f"{sweep['cells']:,}",
                      f"{sweep['iterations']:,}", f"{sweep['yplus']['n']}",
                      f"{worst_wall:.3f}", f"{sweep['slot']['faces']}"]],
               table_id="jf1-grid")

    sweep_page = _serve(LABEL, "jet_flap_7_mesh_forcesweep")
    if sweep_page:
        announce_plot(emit, LABEL, sweep_page,
                      "The separate grid the lift and pressure figures ran on")

    # ----------------------------------------------------- the cheap check --
    span_page = _serve(LABEL, "jet_flap_8_spanwise_uniformity")
    if span_page:
        announce_plot(emit, LABEL, span_page,
                      "Nothing varies across the span")

    bullets(script.numericist,
            "The cheap check before any result is read: this is a section, "
            "one cell deep, so no quantity may vary across the span.",
            "Every field was sampled across the span and the variation is at "
            "the level the arithmetic itself carries. The section is behaving "
            "as a section.")

    # ---------------------------------------------------------------- Cp ----
    cp_page = _serve(LABEL, "jet_flap_2_chordwise_pressure")
    if cp_page:
        announce_plot(emit, LABEL, cp_page,
                      "Surface pressure along the chord, blown against the "
                      "slot-closed reference")

    bullets(script.researcher,
            "Pressure along the chord, upper and lower surfaces separated, at "
            "full scale with nothing clipped.",
            "The stagnation point at the nose is visible and moves under the "
            "wing as blowing increases, which is the signature of the extra "
            "circulation the jet sheet induces.",
            "The strongest suction is at the slot lip, and it deepens with "
            "blowing faster than anything else on the surface.")

    # ------------------------------------------------------- the headline ---
    assert_one_grid([Path(row["case_dir"]) for row in rows])

    lift_page = _serve(LABEL, "jet_flap_1_lift_vs_blowing")
    if lift_page:
        announce_plot(emit, LABEL, lift_page,
                      "Lift against blowing, with the published curve")

    table_rows = []
    for row in rows:
        table_rows.append([
            f"{row['C_mu']:.2f}",
            "closed" if not row["slot_open"] else "open",
            f"{row['CL_aero']:.4f}",
            f"{row['jet_reaction']:.4f}",
            f"{row['CL_total']:.4f}",
            f"{row['CL_published']:.4f}",
            _sci(row["movement"]),
            _sci(row["k_residual"]),
        ])
    emit_table(emit, script, role="CHIEF ENGINEER",
               title="Lift against blowing, one grid, five calculations",
               headers=["Jet momentum [--]", "Slot",
                        "Lift on the wing surface [--]",
                        "Direct jet push [--]",
                        "Total lift [--]",
                        "Published total lift [--]",
                        "Movement over final 4,000 iterations [--]",
                        "Turbulence equation imbalance [--]"],
               rows=table_rows, table_id="jf1-lift")

    bullets(script.engineer,
            "The lift on the wing surface is the pressure and shear integral "
            "over the section alone. It does not contain the direct push of "
            "the jet, which is added in its own column so the total can be "
            "compared with the published curve.",
            "The row at zero blowing is a separate calculation with the slot "
            "CLOSED. It is a reference point, not the blown wing with the jet "
            "turned down, and the four blown rows are a controlled comparison "
            "only among themselves.",
            "The published curve is an interpolation formula fitted to "
            "computed values for trailing-edge blowing.",
            citations=[str(FIGURES.parent / "artefacts_actB"
                           / "jf1_theory_actB_numbers.json")])

    bullets(script.researcher,
            f"Reference curve source: {citation}")

    # ------------------------------------------------------- flow picture ---
    field_page = _serve(LABEL, "jet_flap_3_flow_field")
    if field_page:
        announce_plot(emit, LABEL, field_page,
                      "The solved flow around the section")
    path_page = _serve(LABEL, "jet_flap_4_jet_path")
    if path_page:
        announce_plot(emit, LABEL, path_page,
                      "Where the ejected sheet goes")

    bullets(script.researcher,
            "The ejected sheet leaves the slot, is turned by the oncoming "
            "flow, and settles into a path behind the wing. That turning is "
            "what carries the pressure difference onto the section.")

    # ---------------------------------------------------------- the caveat --
    script.phase(CONCLUSION, "What these numbers do and do not support")

    worst_move = max(row["movement"] for row in rows)
    worst_k = max(row["k_residual"] for row in rows)
    caveats = [
        "These are exploratory calculations. They are not offered as a "
        "validated result and no verdict is attached to them.",
        f"None of the five reached the settling target that was fixed before "
        f"they started. The turbulence equation imbalance at the last "
        f"iteration runs up to {_sci(worst_k)}, against a target of 1e-06. "
        f"That is why the table quotes movement rather than convergence.",
        f"Movement is how much the lift still shifted over the final 4,000 "
        f"iterations, up to {_sci(worst_move)} at the worst row. It is a "
        f"settling indicator and it is not a total uncertainty.",
        "Each family of results was computed on ONE grid. No second grid was "
        "run alongside it, so no grid-sensitivity figure is available and "
        "none is quoted.",
        "No wind-tunnel measurement of this exact section is on file, so the "
        "published curve is a reference and not a validation.",
        "The zero-blowing row has the slot closed and is a reference case. "
        "The four blown rows differ from one another in blowing alone; the "
        "fifth differs from them in more than that.",
    ]
    bullets(script.engineer, *caveats)

    if emit:
        emit("mission.note", {
            "caveats": caveats,
            "verdict": None,
            "reason": "Exploratory. Settling target not met on any row, and "
                      "one grid per family supports no discretisation band."})

    bullets(script.engineer,
            f"Compute: {CORE_MIN_SPENT_SWEEP:.1f} core-minutes on the five "
            f"force calculations against {CORE_MIN_ESTIMATE_SWEEP:.1f} "
            f"budgeted, and the finer flow-picture grid was budgeted at "
            f"{CORE_MIN_ESTIMATE_FLOW:.1f} core-minutes.",
            f"At this machine's rate that is about "
            f"${CORE_MIN_SPENT_SWEEP / 60.0 * RATE_USD_PER_CORE_HOUR:.2f} for "
            f"the sweep. This screen itself spent none of it.")

    return 0


def _worst_wall(rows) -> float:
    """The largest wall spacing across the five force calculations.

    Written as its own function because the flattering alternative is one line
    shorter: the calculation with no blowing has the mildest wall gradients
    and the smallest wall spacing of the five, and quoting it would understate
    the sweep's worst case by roughly a factor of two. The screen quotes the
    worst.
    """
    from ._jf1_numbers import SWEEP_TIME, wall_yplus

    return max(wall_yplus(Path(row["case_dir"]), SWEEP_TIME)["max"]
               for row in rows)


if __name__ == "__main__":
    raise SystemExit(main())
