"""The jet-flap screen: a wing with a blown trailing-edge slot.

The screen presents solved calculations and never claims a number it did not
read back off disk at the moment it spoke.

SANAA'S FIGURE/HEADER/COMPACT-TEXT STANDARD (2026-09-01 ~03:10Z, captured at
``etc/sessions/2026-09-01T0310Z_sanaa_actA_figure_header_standard.md``) is
applied here in the three places this module owns:

* **The header line.** ``SOLVER_HEADER`` below is the one place in this act
  where the solver binary and the turbulence model are allowed to appear, and
  it is stated once, at the top of the results screen, in her pattern
  ``OpenFOAM <solver>, <plain physics description>``. Both halves were read
  out of the runs themselves rather than taken from a brief: ``application
  simpleFoam`` in each case's ``system/controlDict``, ``Exec : simpleFoam`` in
  each ``log.simpleFoam``, ``RASModel kOmegaSST`` in each
  ``constant/turbulenceProperties``, and ``nutLowReWallFunction`` on the
  ``airfoil`` patch of ``0/nut``, which is what makes "resolved to the wall"
  a statement rather than a hope.

  This deliberately re-specifies what the jargon scrub of 2026-09-01 02:44
  (``be88c786``) left generic. That commit was right that the model name must
  not appear wherever a viewer happens to look; her standard says the header
  is the one place it may, named exactly once. Both hold at the same time.

* **Compact text.** Every spoken line goes through ``_lines`` below, which
  REFUSES a line of more than two sentences and refuses a capitalised phrase.
  The rule is asserted rather than merely followed, so a later edit that
  writes a three-sentence line fails at authorship instead of on camera.

* **Present-tense solved-case wording.** Nothing on screen says replayed,
  re-displayed, recorded, presented-not-solved, or "no new number is
  produced". The screen states what was solved, on how many cells, with which
  instrument checks, in the present tense.

  It does NOT claim the uploaded surface is the solved geometry. Act A could
  bind that statement and make it true; this act cannot, measured: the demo
  surface ``cases/demo-surfaces/airfoil_blown_slot.stl`` is the same NACA 0012
  truncated profile at chord 0.991114 m with h/c = 0.005045, and the solved
  ``airfoil`` patch is chord 1.000000 m with h/c = 0.005000. Same shape, 0.9%
  apart in scale. Until those agree, the honest line stays.

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

import re
import shutil
from pathlib import Path

from . import (OUT_ROOT, announce_geometry, announce_plot, bullets,
               emit_table, make_transcript)
from ._jf1_geometry import is_solved_section
from ._jf1_numbers import (PLANT, ReaderRefused, assert_one_grid,
                           display_citation, flow_facts, sweep_facts,
                           sweep_rows)

LABEL = "jet-flap-display"

#: The landed figures, in the order the act shows them. Each is a page that
#: already exists; this screen resolves it to a raster the interface can serve
#: and puts it on the feed. Nothing is plotted here.
FIGURES = Path("/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap/artefacts")

HYPOTHESIS = "hypothesis"
PLAN = "plan"
EVIDENCE = "evidence"
CONCLUSION = "conclusion"

#: Compute spent on the five force calculations, in core-minutes, and the
#: figure fixed before any of them started. Both are read off the record
#: rather than recomputed, and the screen states both because a result
#: without its cost is half a result.
CORE_MIN_SPENT_SWEEP = 117.4833
CORE_MIN_ESTIMATE_SWEEP = 5 * 11.36
RATE_USD_PER_CORE_HOUR = 0.0513

#: The companion grid's own forecast. NOT QUOTED ON SCREEN and kept here
#: deliberately: Sanaa's one-grid rule confines that grid to a single line in
#: the limitations box, so its cost belongs to its own record and not to this
#: act's cost line. Deleting the constant would lose the figure; quoting it
#: would break the rule.
CORE_MIN_ESTIMATE_FLOW = 90.5

#: The results-screen header, in Sanaa's pattern, stated once. The solver
#: binary and the turbulence model appear HERE and nowhere else in this act.
#: Every clause is read out of the runs: see the module docstring for which
#: artefact carries which half.
SOLVER_HEADER = (
    "Solver: OpenFOAM simpleFoam, steady incompressible turbulent flow over a "
    "wing section with a blown trailing-edge slot, k-omega SST resolved to "
    "the wall.")

#: The badge the control room puts on its masthead. It renders ``solver``
#: uppercased and renders ``method`` nowhere, so the short binary name goes on
#: the badge and the full header line is spoken on the results screen.
SOLVER_BADGE = "OpenFOAM simpleFoam"

#: Capitalised tokens the compact-text guard allows through. Everything else
#: in block capitals is the shouting Sanaa struck out.
_CAPS_ALLOWED = {"SST"}


#: A full stop that ends a sentence, as opposed to one inside a decimal, an
#: initial or an abbreviation. Counting naively is not a detail: the published
#: reference this act must name reads "Williams, J., Butler, S. F. J. and
#: Wood, M. N. (1961) ... Memoranda No. 3304, H.M.S.O. 1963, printed p.5
#: eq. (2)", which a naive counter scores as nine sentences and refuses. A
#: guard that refuses the one line the output rules REQUIRE on screen would be
#: deleted within the hour, and the citation would go with it.
#:
#: The rule kept: a stop ends a sentence when what follows is whitespace then
#: a capital letter (or the end of the line), and what precedes is not a lone
#: initial. Decimals ("0.10"), "No. 3304" and "eq. (2)" all fail it correctly.
_SENTENCE_END = re.compile(r"(?<![A-Z])[.!?](?:\s+(?=[A-Z])|\s*$)")


def _sentences(text: str) -> int:
    """How many sentences one spoken line holds."""
    return len(_SENTENCE_END.findall(text)) or 1


def _lines(sayer, *lines: str, **kwargs):
    """Speak, refusing anything that breaks the compact-text standard.

    Two clauses, both hers, both checked rather than trusted:

    * at most two sentences per line, and
    * no capitalised phrase.

    A guard is the point. The wording rules this act already carried lived in
    prose comments, and prose comments are how "with the slot CLOSED" survived
    a review that was looking for it. This raises at authorship, in the caller
    that wrote the line, before anything reaches a screen.
    """
    for line in lines:
        text = line.strip()
        if not text:
            continue
        if _sentences(text) > 2:
            raise ValueError(
                f"compact-text standard: {_sentences(text)} sentences in a "
                f"spoken line, at most 2 are allowed: {text!r}")
        for word in re.findall(r"[A-Za-z]{2,}", text):
            if word.isupper() and word not in _CAPS_ALLOWED:
                raise ValueError(
                    f"compact-text standard: capitalised phrase {word!r} in "
                    f"a spoken line: {text!r}")
    return bullets(sayer, *lines, **kwargs)


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
    """THE DISPATCHED ENTRY POINT — DEMO MODE, the nine-stage sequencer.

    Sanaa's DEMO MODE directive (``etc/sessions/2026-09-01T0340Z_sanaa_demo_
    mode_binding.md``) makes the nine stages MANDATORY for this act: "every
    stage renders in its normal place and its normal order". The router sends
    intent ``jet-flap-display`` here, so here is where the act is walked.

    THE CONNECTOR IS LOCAL, DELIBERATELY. The alternative was a branch in
    ``chief_engineer.server._run_workflow``, which every other team's intent
    also runs through; a shared dispatcher is the wrong place to carry one
    act's special case, and the blast radius of an edit there is every route
    on the box. Nothing outside this module changes, so every other intent
    takes a byte-identical path by construction rather than by inspection.

    SIGNATURE MAPPING, and what is dropped. The workflow contract is
    ``main(request=, params=, emit=)``; the sequencer's is
    ``run_act(key, emit=, script=)``.

    * ``emit`` is passed straight through and IS the mission EventBus's
      ``publish`` (``server._run_workflow`` calls with ``emit=record.bus.
      publish``), so ``stage.banner`` and ``solve.frame`` reach the page.
    * ``script`` is built here, because the sequencer's meshing, gates and
      results stages publish their tables only when a script exists; with
      ``script=None`` the three measured tables would silently not render.
    * ``request`` sets the PROMPT LINE and nothing else, as
      ``typed_prompt``. Measured before it was wired: with the act's
      registered prompt shown unconditionally, a run driven with a reworded
      prompt of the same intent still published Sanaa's exact registered
      string, so the screen quoted a viewer words they had not typed, with no
      mismatch shown. Echoing someone's own prompt back is not a wording
      override; it is the one string on screen that is unambiguously theirs.
      Everything else the screen says stays the act's, so a prompt still
      cannot reword a display whose wording is fixed by directive.
    * ``params`` is DROPPED, and that is a property of the act rather than an
      oversight. The act reads every number off the landed run tree and
      serves its own surface; there is no free parameter an uploaded filename
      could set, so threading one in would change nothing and imply that it
      had.
    * Scope honesty is the dispatcher's and is already live for this intent:
      ``scope.unmet_asks`` declares ``jet-flap-display`` as capable of
      blowing, and MEASURED, it returns a scope-down on a prompt that also
      asks this act for a temperature field, a time history or a design
      search. It does not fire on a prompt that merely differs in wording or
      asks for something outside its four-tag vocabulary, which is why the
      prompt line itself has to be honest.

    NO DEMO-MODE SWITCH IS INVENTED. There is no environment flag or runtime
    toggle for DEMO MODE anywhere in the tree; the directive is unconditional
    for this act, so a second switch would only add a way to be off.

    A refusal is not caught here. ``SequencerRefused``, ``DemoContractError``
    and ``ReaderRefused`` all propagate to ``_run_workflow``, which publishes
    ``mission.failed`` with the reason. Swallowing one would put a silent
    completion on screen in place of a screen that refused.

    The pre-sequencer behaviour is kept whole and reachable as
    :func:`legacy_main`.
    """
    from . import demo_sequencer
    from . import jet_flap_act  # noqa: F401  registers the "jet-flap" act

    script = make_transcript(LABEL, emit)
    demo_sequencer.run_act("jet-flap", emit=emit, script=script,
                           typed_prompt=request)
    return 0


def legacy_main(request: str | None = None, params: dict | None = None,
                emit=None) -> int:
    """The pre-DEMO-MODE jet-flap screen, unchanged and still callable.

    Kept whole: it is the only path that renders this act as a single flat
    transcript, and it is what a caller wanting the old screen calls. Nothing
    dispatches to it now; :func:`main` walks the nine stages instead.
    """
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
        # THE PATH GOES TO THE RECORD, NOT THE SCREEN. A ReaderRefused message
        # names the absolute file the reader was looking at, which is exactly
        # what makes it worth keeping and exactly what Sanaa's never-list bars
        # from a screen. The record keeps the whole message; the screen says a
        # reader refused, which is the part a viewer can act on.
        _lines(script.engineer,
               "This screen could not read one of the quantities it is built "
               "to show, so it is stopping rather than showing the rest.",
               "A reader refused, and its full reason is on the run record.")
        if emit:
            emit("mission.note", {"error": f"ReaderRefused: {exc}"})
        return 2

    # The restatement beat: what was asked, restated, with the cost forecast
    # that was fixed before anything ran. Results come later and in the past
    # tense; nothing here anticipates a number.
    _lines(script.engineer,
           "You asked about a wing with air blown out of a slot at the "
           "trailing edge.",
           "The sweep takes jet momentum from 0 to 0.40: four blown settings "
           "and one slot-closed reference.",
           f"Cost forecast fixed before any of it ran: "
           f"{CORE_MIN_ESTIMATE_SWEEP:.1f} core-minutes for the five, about "
           f"${CORE_MIN_ESTIMATE_SWEEP / 60.0 * RATE_USD_PER_CORE_HOUR:.2f} "
           f"at this machine's rate.")

    _lines(script.researcher,
           "The physics: the slot ejects a thin sheet of air 30 degrees below "
           "the chord line, and that sheet acts like a flap made of air.",
           "The sheet turns the flow behind the wing and pulls extra "
           "circulation onto the wing, so the wing gains far more lift than "
           "the direct push of the jet accounts for.",
           "Blowing strength is the jet momentum coefficient: momentum "
           "leaving the slot each second, divided by the oncoming flow's "
           "dynamic pressure times the wing area.",
           "What would falsify this: lift failing to grow roughly with the "
           "square root of jet momentum at low blowing, or lift matching the "
           "direct jet push alone with no circulation gain.",
           citations=[str(FIGURES.parent / "artefacts_actB"
                          / "jf1_theory_actB_numbers.json")])

    # -------------------------------------------------------- the two grids --
    script.phase(PLAN, "One grid, five calculations")

    # No surface is announced to the viewport. The instruction for this act is
    # that any picture it shows must be the computational grid itself and not
    # a tessellation of the shape, so the geometry beat IS the grid page below
    # and there is nothing else to put in the viewport.
    #
    # A surface CAN arrive with the request, because this route keeps itself
    # when one is uploaded. It is not the body these pages were computed on
    # and the screen has to say so in words, at the top, before any number is
    # shown. Silence here would let a viewer read our section's lift as theirs.
    #
    # Sanaa's standard removes this disclaimer for Act A by BINDING the
    # mission to the uploaded file so the statement becomes true. That binding
    # is not available here and the difference is measured, not assumed: see
    # the module docstring. A true sentence stays until the geometry agrees.
    uploaded = str(params.get("surface") or "").strip()
    if uploaded:
        # THE CLAIM IS MEASURED, NOT ASSUMED. Sanaa's demo-mode binding says
        # the uploaded surface IS the solved geometry; that became true for
        # the shipped body when it was regenerated to unit chord, and it says
        # nothing about a body somebody else uploads. So the act reads what
        # actually arrived and speaks accordingly. The screen never carries
        # the sentence unless the file on disk earns it.
        announce_geometry(emit, name=uploaded,
                          label="Wing section with a blown trailing-edge slot")
        if is_solved_section(uploaded):
            _lines(script.engineer,
                   "The surface you uploaded is the section these "
                   "calculations ran on.")
        else:
            _lines(script.engineer,
                   "A surface arrived with your request, and the numbers "
                   "below belong to the solved section.")

    # ONE GRID ON SCREEN (Sanaa, demo-mode binding 2026-09-01 ~03:40Z). The
    # force grid carries the fields, the pressures and the lift table alike.
    # The finer companion grid is named in exactly one place, the limitations
    # box at the foot, and nowhere else on this screen.
    #
    # This does NOT merge the two grids: their reference areas differ by a
    # factor of one hundred and ``assert_one_grid`` still refuses any table
    # spanning both. Her rule decides which grid is shown; the guard that
    # keeps them off one axis is untouched.
    # The companion grid is named only in the limitations box, and that line
    # has to be TRUE there. This is the check that earns it: if the two ever
    # became the same grid, "a finer companion grid" would be a sentence about
    # nothing, and the guard says so instead of the screen saying it quietly.
    if flow["cells"] <= sweep["cells"]:
        raise ReaderRefused(
            f"the companion grid is stated to be finer and reads "
            f"{flow['cells']} cells against the force grid's "
            f"{sweep['cells']}; the limitations box would be describing a "
            f"grid that is not there")

    _lines(script.engineer,
           f"The five lift and pressure calculations ran on one grid of "
           f"{sweep['cells']:,} cells, each for {sweep['iterations']:,} "
           f"iterations.",
           "Four had the slot open and blew at different strengths, and the "
           "fifth was a reference with the slot closed.")

    if emit:
        emit("solver.selected", {
            "solver": SOLVER_BADGE,
            "method": "steady incompressible turbulent flow over a wing "
                      "section with a blown trailing-edge slot, k-omega SST "
                      "resolved to the wall",
            "basis": "Standard closure for attached external flow. The slot "
                     "is a momentum inlet, not a modelled source."})

    # ------------------------------------------------------- the real mesh --
    script.phase(EVIDENCE, "The grid, the wall, and the slot")

    # The results-screen header, in her pattern, once. Every clause below is a
    # value this run wrote, not a description of the run.
    _lines(script.engineer,
           SOLVER_HEADER,
           f"Five blowing settings solved on this section, "
           f"{sweep['cells']:,} cells.",
           f"Instrument checks: the wall-spacing reader and the lift reader "
           f"each detected a planted {PLANT:.3e} value before any number "
           f"here was quoted.")

    # The grid page shown is the FORCE grid's, because that is the grid the
    # lift table and the pressures come from. The finer grid's own mesh pages
    # (jet_flap_5_mesh_flowfield, jet_flap_6_mesh_resolution) are deliberately
    # NOT served here: showing a second grid's mesh is the thing her one-grid
    # rule removes, and a page that is never shown cannot be misread.
    mesh_page = _serve(LABEL, "jet_flap_7_mesh_forcesweep")
    if mesh_page:
        announce_plot(emit, LABEL, mesh_page,
                      "The computational grid the five calculations ran on")

    # The worst wall spacing across the five rows, at the final state, not the
    # spacing of whichever row happened to be rendered. The slot-closed row is
    # the mildest of the five at 0.191 and quoting it would understate the
    # sweep by roughly a factor of two.
    worst_wall = _worst_wall(rows)
    _lines(script.numericist,
           "This is the computational grid itself, cell by cell, not a "
           "surface tessellation of the shape.",
           f"All {sweep['yplus']['n']} cells touching the wing surface sit "
           f"inside the viscous sublayer, the largest wall spacing "
           f"{worst_wall:.3f} in wall units against a limit of 1.",
           f"The slot mouth is spanned by {sweep['slot']['faces']} cells, so "
           f"the ejected sheet has a profile across it rather than a single "
           f"value.")

    emit_table(emit, script, role="NUMERICIST",
               title="Grid resolution at the wall",
               headers=["Cells", "Iterations", "Wall cells",
                        "Largest wall spacing [wall units]",
                        "Cells across slot"],
               rows=[[f"{sweep['cells']:,}", f"{sweep['iterations']:,}",
                      f"{sweep['yplus']['n']}", f"{worst_wall:.3f}",
                      f"{sweep['slot']['faces']}"]],
               table_id="jf1-grid")

    # ----------------------------------------------------- the cheap check --
    span_page = _serve(LABEL, "jet_flap_8_spanwise_uniformity")
    if span_page:
        announce_plot(emit, LABEL, span_page,
                      "Nothing varies across the span")

    _lines(script.numericist,
           "The cheap check before any result is read: this is a section one "
           "cell deep, so no quantity may vary across the span.",
           "Every field was sampled across the span and the variation sits at "
           "the level the arithmetic itself carries.")

    # ---------------------------------------------------------------- Cp ----
    cp_page = _serve(LABEL, "jet_flap_2_chordwise_pressure")
    if cp_page:
        announce_plot(emit, LABEL, cp_page,
                      "Surface pressure along the chord, blown against the "
                      "slot-closed reference")

    _lines(script.researcher,
           "Pressure along the chord, upper and lower surfaces separated, at "
           "full scale with nothing clipped.",
           "The stagnation point at the nose moves under the wing as blowing "
           "increases, the signature of the extra circulation the jet sheet "
           "induces.",
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

    _lines(script.engineer,
           "The lift on the wing surface is the pressure and shear integral "
           "over the section alone.",
           "The direct push of the jet is added in its own column, so the "
           "total can be compared with the published curve.",
           "The row at zero blowing is a separate calculation with the slot "
           "closed, a reference point and not the blown wing with the jet "
           "turned down.",
           "The four blown rows are a controlled comparison only among "
           "themselves.",
           citations=[str(FIGURES.parent / "artefacts_actB"
                          / "jf1_theory_actB_numbers.json")])

    # THE REFERENCE IS STATED ONCE (Sanaa, demo-mode binding). It used to be
    # said twice: an unattributed sentence about the published curve here, and
    # the attribution a beat later. The two are merged into this one line.
    #
    # The string still comes from display_citation(), which checks the short
    # form against the full citation in the reference file and refuses if the
    # authors or the report number have drifted. A literal typed here would be
    # the same defect the single reader was built to remove.
    _lines(script.researcher,
           "The published curve is an interpolation formula fitted to "
           "computed values for trailing-edge blowing.",
           f"Source: {citation}.")

    # ------------------------------------------------------- flow picture ---
    field_page = _serve(LABEL, "jet_flap_3_flow_field")
    if field_page:
        announce_plot(emit, LABEL, field_page,
                      "The solved flow around the section")
    path_page = _serve(LABEL, "jet_flap_4_jet_path")
    if path_page:
        announce_plot(emit, LABEL, path_page,
                      "Where the ejected sheet goes")

    _lines(script.researcher,
           "The ejected sheet leaves the slot, is turned by the oncoming "
           "flow, and settles into a path behind the wing.",
           "That turning is what carries the pressure difference onto the "
           "section.")

    # ---------------------------------------------------------- the caveat --
    script.phase(CONCLUSION, "What these numbers do and do not support")

    worst_move = max(row["movement"] for row in rows)
    worst_k = max(row["k_residual"] for row in rows)
    # EVERY LIMITATION HERE IS ABOUT THE PHYSICS OR THE EVIDENCE, and Sanaa's
    # compact-text rule is a length rule, not a licence to drop one. Each was
    # shortened to at most two sentences with its claim intact; none was
    # merged with another, because merging two caveats is how one of them
    # stops being read.
    # THE LIMITATIONS BOX. Sanaa's four compact limitations, in her own
    # wording, each expanded by at most one clause carrying the measured value
    # that makes it checkable. Her compact-text rule is a LENGTH rule and not
    # a licence to drop a limitation, so none of the four was merged away and
    # none of the physics was softened.
    #
    # The companion-grid line is here because this is the one place her rule
    # allows the finer grid to be named. It appears nowhere else on the
    # screen: not in the header, not in the grid table, not in a caption.
    caveats = [
        "Exploratory, with no verdict attached.",
        f"The settling target is not reached at high blowing, the turbulence "
        f"equation imbalance at the last iteration running up to "
        f"{_sci(worst_k)} against a target of 1e-06.",
        "That is why the table quotes movement rather than convergence.",
        f"Movement is how much the lift still shifted over the final 4,000 "
        f"iterations, up to {_sci(worst_move)} at the worst row. It is a "
        f"settling indicator and not a total uncertainty.",
        "Single grid, so no grid-sensitivity figure is available and none is "
        "quoted.",
        "No wind-tunnel data for this section, so the published curve is a "
        "reference and not a validation.",
        "Flow picture from a finer companion grid.",
        "The zero-blowing row has the slot closed and is a reference case.",
        "The four blown rows differ from one another in blowing alone; the "
        "fifth differs from them in more than that.",
    ]
    _lines(script.engineer, *caveats)

    if emit:
        emit("mission.note", {
            "caveats": caveats,
            "verdict": None,
            "reason": "Exploratory. Settling target not met on any row, and "
                      "one grid per family supports no discretisation band."})

    # The cost line states the five calculations' own cost against their own
    # forecast. The companion grid's budget used to be quoted here and is
    # gone: naming that grid outside the limitations box is what her one-grid
    # rule removes, and its cost belongs to its own record.
    _lines(script.engineer,
           f"Compute: {CORE_MIN_SPENT_SWEEP:.1f} core-minutes against "
           f"{CORE_MIN_ESTIMATE_SWEEP:.1f} forecast, "
           f"{CORE_MIN_SPENT_SWEEP / CORE_MIN_ESTIMATE_SWEEP:.2f} times the "
           f"forecast.",
           f"At this machine's rate that is about "
           f"${CORE_MIN_SPENT_SWEEP / 60.0 * RATE_USD_PER_CORE_HOUR:.2f}.")

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
