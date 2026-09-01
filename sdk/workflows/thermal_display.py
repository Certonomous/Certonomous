"""The thermal display act: screens built from a run that has already landed.

THIS MODULE STARTS NO SOLVER. It writes no case, queues no job, invokes no
OpenFOAM binary and books no compute. Every number it puts on screen was read
off disk by the screen generator that ran earlier, and every figure it renders
is a file that generator wrote. If a figure is not on disk, the act says which
path was empty and shows nothing in its place.

That constraint is the whole reason this act can exist. The lab holds landed
conjugate thermal runs for two bodies and holds no general thermal chain the
control room may point at an arbitrary body, so the router sends a thermal
question here ONLY when it names one of those two bodies. Everything else
thermal keeps the route it has today, refusal included.

Screen sets, and the landed bundle each one reads:

``A``  the motor in a duct, ``docs/campaigns/T-family/demo/figures_actA/``
``C``  the battery module,   ``docs/campaigns/T-family/demo/figures/``

Each bundle is a ``*_screen_data.json`` holding the numbers plus vector
figures beside it. The bundle is the contract: this act reads it and does not
re-derive a single value from the case directories, so a number on screen and
the number in the record cannot drift apart.

TWO BUNDLE DIALECTS, ONE PRESENTATION PATH
------------------------------------------
The two acts were built by two generators that did not agree on key names.
Act C writes ``source_case`` / ``reader`` / ``mesh`` / ``instrument_check_*``
/ ``per_cell_table``; Act A writes ``map_rows`` / ``envelope`` / ``radial`` /
``monitors`` / ``planted_zero_controls`` / ``anchor_checks`` and none of the
first set. Rather than carry two presentation code paths, ``_normalise``
translates whichever dialect arrived into ONE internal shape and everything
below it is dialect-blind. Adding a third act is a normaliser branch, not a
second copy of the screens.

WHAT MUST NEVER HAPPEN HERE, AND THE GUARD THAT STOPS IT
--------------------------------------------------------
The planted-zero instrument checks go up BEFORE any temperature. An earlier
version of this module looked only for ``instrument_check_*`` keys and would
therefore have SILENTLY SKIPPED the whole instrument table for a bundle that
spells them ``planted_zero_controls`` -- a screen full of temperatures with no
evidence that the readers behind them can see anything at all. A verification
block that renders as nothing is worse than one that renders as "not
recorded", and both are worse than a refusal. So: if no recognisable control
block is found, this act REFUSES. It names what it looked for, names what the
bundle actually offered, draws no figure and quotes no number.

    python -m workflows.thermal_display
    python -m workflows.thermal_display --act A
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from . import OUT_ROOT, announce_geometry, announce_plot, make_transcript
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, KnowledgeBase, Roster,
                                lab_report)
from chief_engineer.transcript import CHIEF_ENGINEER as _CE_ROLE

from .geometry_study import _emit_table

BEAT = "thermal-display"
_REPO = Path(__file__).resolve().parents[2]
_DEMO = _REPO / "docs" / "campaigns" / "T-family" / "demo"

#: A figure whose file was on disk when this screen set was fixed. Its absence
#: at run time is reported as a gap, because something that was there has gone.
LANDED = "landed"
#: A figure another lane was still generating when this screen set was fixed.
#: If it is on disk when the act runs it goes up; if it is not, the beat it
#: serves is NAMED in the not-available table instead. Neither outcome is
#: silent, and the reviewer of this file can see both.
PENDING = "pending"

# One row per landed thermal act. Adding a body when its run lands is one row
# here and one router table entry, nothing else.
#
#   ``bundle``          the JSON this act reads.
#   ``extra_bundles``   further JSON files merged over it, each one a product
#                       built after the main bundle was written. A named extra
#                       that is missing is said on screen, never skipped.
#   ``figures``         (stem, title, status) resolved inside ``folder``.
#   ``not_available``   beats this act was asked for and cannot show, with the
#                       reason. ``satisfied_by`` names a figure stem: when
#                       that figure did go up, the row is dropped, because a
#                       beat that was shown must not also be declared missing.
SCREEN_SETS: dict[str, dict] = {
    "A": {
        "title": "the motor in a duct",
        "folder": _DEMO / "figures_actA",
        "bundle": "actA_screen_data.json",
        "extra_bundles": (),
        "figures": (
            ("actA_temperature_field",
             "Temperature on the computational mesh", PENDING),
            ("actA_velocity_field",
             "Velocity through the duct", PENDING),
            ("actA_map_table",
             "Peak temperature across the sixteen operating points", LANDED),
            ("actA_envelope",
             "Operating envelope against the 200 C limit", LANDED),
            ("actA_radial_profile",
             "Radial temperature profile through the hottest solid cell",
             LANDED),
            ("actA_monitor_replay",
             "Each run's own temperature monitor, replayed", LANDED),
            ("actA_assumption_beat",
             "The hand model against the coupled solve", LANDED),
        ),
        "not_available": (
            ("A3, the geometry and meshing walkthrough",
             "no meshing screen was built for this act; the mesh is read for "
             "the radial cut and for nothing else",
             None),
            ("A4, the feasibility-first framing",
             "no artifact was built for this beat, so it is not presented",
             None),
            ("A6.1, the temperature field on the mesh",
             "no field render had landed when this act's screen set was "
             "fixed, so there is no picture of the field to put up",
             "actA_temperature_field"),
            ("A6.1, the velocity panel",
             "no velocity render had landed when this act's screen set was "
             "fixed, so there is no picture of the flow to put up",
             "actA_velocity_field"),
            ("A6.6, the operating recommendation",
             "this act reports the solved map and the margin at every point "
             "and recommends nothing; choosing an operating point is not "
             "something this run decides",
             None),
            ("A8, the assumptions box",
             "no assumptions-box screen was built for this act; the hand "
             "model comparison that is shown is a different beat",
             None),
            ("A9, the export of the act as one document",
             "no export was built; the figures exist beside the bundle as "
             "vector pages and nothing assembles them into one file",
             None),
            # The stated form of an over-claim the capability table cannot
            # express. ``scope.CAPABILITIES`` is keyed on the INTENT, and the
            # intent declares UNSTEADY because Act C is a 900 second
            # transient -- so a request for a time history of THIS body is
            # not scoped down before the act starts. It is named here
            # instead. ``satisfied_by`` is None: no figure can retire this
            # row, because it is a property of the run and not a missing
            # render.
            ("A time history, or any transient response, for this body",
             "this act presents sixteen SEPARATE STEADY operating points: "
             "each one is a converged steady state, so there is no history "
             "through time to show and none is constructed. Nothing here "
             "says how this body warms up, how long it takes to reach these "
             "temperatures, or how it responds to a change in load. The "
             "battery module act is where time-resolved behaviour lives",
             None),
        ),
    },
    "C": {
        "title": "the battery module",
        "folder": _DEMO / "figures",
        "bundle": "actc_screen_data.json",
        "extra_bundles": ("actc_step_independence.json",),
        "figures": (
            ("actc_field_snapshots",
             "Temperature on the computational mesh at six times", LANDED),
            ("actc_cell_histories",
             "Cell temperature histories with the takeoff pulse marked",
             LANDED),
            ("actc_pack_uniformity",
             "Pack spread and channel surface heat removal against time",
             LANDED),
            ("actc_per_cell_table", "Peak, rise and time to peak, per cell",
             LANDED),
            ("actc_step_independence",
             "The same answer at two time steps", LANDED),
        ),
        "not_available": (
            ("C6.3, the coolant outlet temperature",
             "the cooling channels are not resolved as a fluid region in "
             "this configuration, so there is no coolant stream to have an "
             "outlet; the heat removed at the channel-facing surfaces is "
             "given instead",
             None),
            ("C7, the transitional-flow sensitivity band",
             "no run on disk supplies it: nothing in this campaign varied "
             "the flow regime, so there is no band to draw and none is "
             "constructed",
             None),
        ),
    },
}


def _png_for(stem: str, folder: Path, out: Path) -> tuple[Path | None, str]:
    """Resolve one figure to a PNG the control room can serve.

    Three outcomes and the caller must be able to tell them apart, because a
    blank panel under a caption is the failure this function exists to avoid:

      * a PNG is on disk beside the vector figure  -> it is placed and served
      * only the PDF is there and a converter is present -> a PNG is made
      * neither                                    -> ``(None, reason)``

    The reason names the path that was empty so the gap is reportable rather
    than merely visible.
    """
    src_png = folder / f"{stem}.png"
    dest = out / f"{stem}.png"
    if src_png.exists():
        shutil.copy(src_png, dest)
        return dest, ""
    src_pdf = folder / f"{stem}.pdf"
    if not src_pdf.exists():
        return None, f"no figure at {src_pdf}"
    converter = shutil.which("pdftoppm")
    if not converter:
        return None, (f"{src_pdf.name} is on disk as a vector page and no "
                      f"page converter is present on this host, so it cannot "
                      f"be placed on screen")
    try:
        subprocess.run([converter, "-png", "-r", "150", "-singlefile",
                        str(src_pdf), str(dest.with_suffix(""))],
                       check=True, capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None, f"{src_pdf.name} could not be rendered to a page image"
    if not dest.exists():
        return None, f"{src_pdf.name} produced no page image"
    return dest, ""


def _read_json(path: Path) -> tuple[dict | None, str]:
    if not path.exists():
        return None, f"nothing on disk at {path}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), ""
    except (OSError, ValueError) as exc:
        return None, f"{path} could not be read ({type(exc).__name__})"


def _load_bundle(spec: dict) -> tuple[dict | None, str, list[str]]:
    """The act's bundle, plus every extra product merged over it.

    Returns ``(bundle, gap, missing_extras)``. A named extra that is not on
    disk lands in ``missing_extras`` and is said on screen; it is never
    dropped quietly, because the whole point of naming it here is that
    somebody expects to see it.
    """
    path = spec["folder"] / spec["bundle"]
    bundle, gap = _read_json(path)
    if bundle is None:
        return None, (f"The screen bundle for {spec['title']} is not "
                      f"readable: {gap}. Nothing is shown for it."), []
    missing: list[str] = []
    for name in spec.get("extra_bundles", ()):
        extra, extra_gap = _read_json(spec["folder"] / name)
        if extra is None:
            missing.append(f"{name}: {extra_gap}")
            continue
        bundle.update(extra)
    return bundle, "", missing


# --------------------------------------------------------------------------
# The normaliser: two bundle dialects in, one internal shape out.
# --------------------------------------------------------------------------
#: What a screen cell says when the bundle does not carry the value. There is
#: no other answer in this module: see ``_fmt``.
NOT_RECORDED = "not recorded"
#: Keys a control block may use for the thing that was planted, and for
#: whether the reader saw it. Both dialects are listed; neither is preferred.
_PLANTED_KEYS = ("planted_K", "planted_W", "planted")
#: The unit each planted-magnitude key carries. ``planted_K`` is kelvin,
#: ``planted_W`` is watts, and a bare ``planted`` records no unit at all -- so
#: none is printed and the cell says the unit was not recorded. The unit is
#: taken from the key that MATCHED, never from the common case: labelling a
#: watt-valued control 'K' because kelvin is what the thermal acts usually
#: plant is a fabricated unit, which is the same defect as a fabricated value
#: one column over.
_PLANTED_UNITS = {"planted_K": "K", "planted_W": "W", "planted": ""}
_SEEN_KEYS = ("seen", "passed", "ok")
#: Keys that describe WHERE a control was planted, in the order they read
#: best on screen. Only those a given block actually carries are used.
_WHERE_KEYS = ("scope", "region", "planted_cell_index", "cell_index",
               "row_index", "n_cells_planted", "n_perturbed", "planted_time_s",
               "radius_m", "detection_floor_K", "worst_departure_K")


def _first(body: dict, keys) -> tuple[str, object] | tuple[None, None]:
    for k in keys:
        if k in body:
            return k, body[k]
    return None, None


def _fmt(body: dict | None, key: str, spec: str = "", unit: str = "") -> str:
    """One screen cell read from ``body[key]``, or ``NOT_RECORDED``.

    THIS FUNCTION TAKES NO NUMERIC DEFAULT AND MUST NEVER GROW ONE, and it is
    the only way a value reaches a screen cell in this module, so that the
    absence of ``.get(<key>, <number>)`` anywhere below is checkable by eye.

    ``body.get(key, 0.0)`` inside an f-string puts a confident ``0.0e+00`` on
    screen for a value no reader ever produced. That is worse than the silent
    skip this module was written to fix: a skipped table is VISIBLY absent,
    while a fabricated zero LOOKS LIKE A MEASUREMENT -- and it is the tightest
    possible answer, so it flatters the run besides. CLAUDE.md rule 3: a zero
    from a reader not shown able to see a non-zero is not evidence, and a zero
    conjured by ``dict.get``'s second argument was never read at all.
    ``float('nan')`` is the same mistake in a less dangerous costume: still a
    number standing where a reading should be.

    The trap is sharpest where the row is GUARDED ON A DIFFERENT KEY from the
    one it prints, because then a bundle can legitimately reach the row
    carrying the guard and not the value.

    A value that is present but not formattable the expected way is shown as
    it was recorded rather than hidden: the bundle did record something, and
    what it recorded is the honest thing to show.
    """
    value = (body or {}).get(key)
    if value is None:
        return NOT_RECORDED
    try:
        text = format(value, spec) if spec else str(value)
    except (TypeError, ValueError):
        text = str(value)
    return f"{text} {unit}" if unit else text


def _where(body: dict) -> str:
    """A plain phrase for where a control was planted, from whatever the
    block records. Nothing is invented: only keys present are used."""
    parts: list[str] = []
    for k in _WHERE_KEYS:
        if k not in body:
            continue
        v = body[k]
        if k == "scope":
            parts.append(str(v))
        elif k == "region":
            parts.append(f"region {v}")
        elif k in ("planted_cell_index", "cell_index"):
            parts.append(f"cell index {v}")
        elif k == "row_index":
            parts.append(f"row {v}")
        elif k in ("n_cells_planted", "n_perturbed"):
            parts.append(f"{v} value{'' if v == 1 else 's'} perturbed")
        elif k == "planted_time_s":
            parts.append(f"t = {float(v):.0f} s")
        elif k == "radius_m":
            parts.append(f"radius {float(v) * 1e3:.3f} mm")
        elif k == "detection_floor_K":
            parts.append(f"detection floor {float(v):.0e} K")
        elif k == "worst_departure_K":
            parts.append(f"worst departure {float(v):.1e} K")
    return "; ".join(parts) if parts else "not recorded"


def _instrument_rows(bundle: dict) -> list[list[str]]:
    """Every planted-zero control in the bundle, in either spelling.

    Act C names them ``instrument_check_<reader>`` at the top level; Act A
    collects them in ``planted_zero_controls``. Both are read here, and this
    function returning an EMPTY list is what triggers the act's refusal --
    it must never be treated as "there were none to show".
    """
    found: list[tuple[str, dict]] = []
    for name, body in bundle.items():
        if name.startswith("instrument_check_") and isinstance(body, dict):
            found.append((name[len("instrument_check_"):], body))
    controls = bundle.get("planted_zero_controls")
    if isinstance(controls, dict):
        for name, body in controls.items():
            if isinstance(body, dict):
                found.append((name, body))
    rows = []
    for name, body in sorted(found):
        planted_key, planted = _first(body, _PLANTED_KEYS)
        _sk, seen = _first(body, _SEEN_KEYS)
        # The unit comes from the key that matched. Every control block in
        # both bundles today spells it ``planted_K``, but ``_PLANTED_KEYS``
        # admits ``planted_W`` and a bare ``planted``, and a hardcoded 'K'
        # would label a watt-valued control kelvin the day one arrives.
        mag = _fmt(body, planted_key, "g") if planted_key else NOT_RECORDED
        if planted is None or mag == NOT_RECORDED:
            planted_cell = NOT_RECORDED
        else:
            unit = _PLANTED_UNITS.get(planted_key, "")
            planted_cell = (f"{mag} {unit}" if unit
                            else f"{mag}, unit not recorded")
        rows.append([
            name.replace("_", " "),
            planted_cell,
            _where(body),
            NOT_RECORDED if seen is None
            else ("seen" if seen else "NOT SEEN"),
        ])
    return rows


def _anchor_rows(bundle: dict) -> tuple[list[str], list[list[str]]] | None:
    """Act A's independent anchor checks, if the bundle carries them.

    These are NOT planted zeros and are not presented as though they were: an
    anchor check compares a value re-derived by hand against the value the
    screen quotes. It gets its own table with its own column names.
    """
    anchors = bundle.get("anchor_checks")
    if not isinstance(anchors, list) or not anchors:
        return None
    headers = ["Operating point", "Expected, C", "Measured, C",
               "Difference, K", "Agrees"]
    rows = []
    for a in anchors:
        if not isinstance(a, dict):
            continue
        rows.append([
            f"{_fmt(a, 'power_W')} W, {_fmt(a, 'airspeed_ms')} m/s",
            _fmt(a, "expected_degC", ".6f"),
            _fmt(a, "measured_degC", ".6f"),
            _fmt(a, "abs_diff_degC", ".3e"),
            # An unrecorded verdict is not a failed one. Reading absence as
            # 'NO' would report a disagreement nobody measured, the same
            # fabrication as a zero, pointing the other way.
            NOT_RECORDED if a.get("matches") is None
            else ("yes" if a["matches"] else "NO"),
        ])
    return (headers, rows) if rows else None


def _normalise_act_a(b: dict) -> dict:
    """Act A's bundle, translated into the internal shape."""
    rows = b.get("map_rows") or []
    fields = [str(r.get("source_field", "")) for r in rows
              if r.get("source_field")]
    common = os.path.commonpath(fields) if fields else ""
    unc = b.get("numerical_uncertainty") or {}
    env = b.get("envelope") or {}
    worst = env.get("worst_point") or {}
    colour = b.get("map_colour_range_degC") or {}
    mon = b.get("monitors") or {}
    settled = mon.get("settled_vs_cell_only") or {}
    radial = b.get("radial") or {}
    stats = radial.get("region_stats") or {}

    out = dict(b)
    out["source_case"] = (f"{common}, {len(rows)} operating points"
                          if common else "not recorded in this bundle")
    out["reader"] = ("not recorded in this bundle; the readers and the "
                     "build are named in the directory README beside it")
    out["mesh"] = {
        "n_mesh_cells": "not recorded in this bundle",
        "geometry_guard": "not recorded in this bundle",
    }
    extra = []
    if stats:
        extra.append(["Radial cut resolution",
                      ", ".join(f"{v.get('n_cells', '?')} {k}"
                                for k, v in sorted(stats.items()))
                      + " cells on the cut"])
    if mon.get("source_file_pattern"):
        extra.append(["Monitor files", str(mon["source_file_pattern"])])
    if unc.get("column_entry"):
        extra.append(["Numerical uncertainty", str(unc["column_entry"])])
    out["provenance_extra"] = extra

    # ---- the act's own result table, with the act's own column names ----
    if rows:
        out["result_table"] = {
            "title": "The sixteen solved operating points",
            "headers": ("Power, W", "Airspeed, m/s", "Peak temperature, C",
                        "Rise above inlet, K", "Margin to the 200 C limit, K",
                        "Uncertainty"),
            "rows": [[_fmt(r, "power_W"),
                      _fmt(r, "airspeed_ms"),
                      _fmt(r, "peak_T_degC", ".6f"),
                      _fmt(r, "rise_above_inlet_K", ".6f"),
                      _fmt(r, "margin_to_limit_K", ".6f"),
                      _fmt(r, "numerical_uncertainty")]
                     for r in rows],
        }

    # ---- the quantities, every one of them quoted from the bundle ----
    q: list[dict] = []
    if colour.get("maximum") is not None:
        q.append({
            "quantity": "Hottest point of the sixteen cases",
            "value": f"{_fmt(colour, 'maximum', '.6f')} C",
            "envelope": (f"colour scale {_fmt(colour, 'minimum', '.6f')}"
                         f" to {_fmt(colour, 'maximum', '.6f')} C, nothing "
                         f"clipped at either end")})
    if rows:
        # ``inf`` here is a SORT SENTINEL, not a screen value: a row with no
        # peak recorded cannot be the coolest one. It never reaches a cell --
        # the value below is read from the winning row without a default.
        coolest = min(rows, key=lambda r: r.get("peak_T_degC", float("inf")))
        q.append({
            "quantity": "Coolest of the sixteen operating points",
            "value": f"{_fmt(coolest, 'peak_T_degC', '.6f')} C",
            "envelope": (f"at {_fmt(coolest, 'power_W')} W and "
                         f"{_fmt(coolest, 'airspeed_ms')} m/s")})
    if env.get("worst_margin_K") is not None:
        q.append({
            "quantity": (f"Smallest margin to the "
                         f"{_fmt(env, 'limit_degC', '.0f')} C limit"),
            "value": f"{_fmt(env, 'worst_margin_K', '.6f')} K",
            "envelope": (f"at {_fmt(worst, 'power_W')} W and "
                         f"{_fmt(worst, 'airspeed_ms')} m/s, the hottest "
                         f"point solved")})
    if settled.get("offset_K") is not None:
        q.append({
            "quantity": "The run's own monitor against its internal cells",
            "value": f"{_fmt(settled, 'offset_K', '.6f')} K",
            "envelope": (f"the monitor reads "
                         f"{_fmt(settled, 'monitor_degC', '.6f')} C "
                         f"where the internal cells read "
                         f"{_fmt(settled, 'internal_cells_degC', '.6f')} C")})
    if unc.get("column_entry"):
        q.append({"quantity": "Numerical uncertainty",
                  "value": str(unc["column_entry"]),
                  "envelope": str(unc.get("reason", "not recorded"))})
    out["quantity_rows"] = q

    # ---- hoist what the run cannot say to the top level, in the one
    # spelling ``main`` scans for ----
    if unc.get("available") is False and unc.get("reason"):
        out["numerical_uncertainty_statement"] = (
            "NOT AVAILABLE; a discretisation error bar for this act: "
            + str(unc["reason"]))
    return out


def _normalise_act_c(b: dict) -> dict:
    """Act C's bundle. It is already close to the internal shape; this fills
    in the two keys the shared presentation path expects by name."""
    out = dict(b)
    table = b.get("per_cell_table")
    if isinstance(table, list) and table:
        out["result_table"] = {
            "title": "Per cell peak and rise",
            "headers": ("Cell", "Peak, K", "Rise, K", "Time to peak, s",
                        "Uncertainty"),
            "rows": [[_fmt(r, "cell"),
                      _fmt(r, "peak_T_K", ".6f"),
                      _fmt(r, "peak_rise_K", ".6f"),
                      _fmt(r, "time_to_peak_s", ".0f"),
                      _fmt(r, "uncertainty")]
                     for r in table],
        }
    extra = []
    mesh = b.get("mesh") or {}
    if mesh.get("mesh_cells_per_module_cell") is not None:
        extra.append(["Mesh cells per module cell",
                      str(mesh["mesh_cells_per_module_cell"])])
    if b.get("coolant_reference_temperature_K") is not None:
        extra.append(["Coolant reference temperature",
                      f"{b['coolant_reference_temperature_K']:.6f} K"])
    out["provenance_extra"] = extra

    q: list[dict] = []
    scale = b.get("shared_colour_scale_K")
    if isinstance(scale, (list, tuple)) and len(scale) == 2:
        q.append({
            "quantity": "Hottest temperature anywhere",
            "value": f"{scale[1]:.6f} K",
            "envelope": (f"colour scale {scale[0]:.6f} to {scale[1]:.6f} K, "
                         f"nothing clipped at either end")})
    if b.get("max_spread_K") is not None:
        q.append({
            "quantity": "Largest spread across cells",
            "value": f"{_fmt(b, 'max_spread_K', '.6f')} K",
            "envelope": f"at t = {_fmt(b, 'max_spread_time_s', '.0f', 's')}"})
    if b.get("surface_heat_removal_final_W") is not None:
        q.append({
            "quantity": "Heat removed at the channel facing surfaces",
            "value": f"{_fmt(b, 'surface_heat_removal_final_W', '.4f')} W",
            "envelope": "at the last written time"})
    if b.get("energy_closure_percent") is not None:
        q.append({
            "quantity": "Energy closure",
            "value": f"{_fmt(b, 'energy_closure_percent', '.4f')}%",
            "envelope": "input against accumulation plus removal"})
    if b.get("unaccounted_percent_fine") is not None:
        # THE GUARD ABOVE IS A DIFFERENT KEY FROM THE VALUES BELOW. A bundle
        # can legitimately reach this row carrying ``unaccounted_percent_fine``
        # and none of the three values it prints, so none of them is read with
        # a default: 'under 0.0e+00 K' would announce perfect time-step
        # independence -- the tightest result the study could possibly have --
        # off a number no reader ever produced.
        largest = _fmt(b, "largest_abs_diff_K", ".1e", "K")
        q.append({
            "quantity": "Change in the peak rise when the time step is halved",
            "value": (largest if largest == NOT_RECORDED
                      else f"under {largest}"),
            "envelope": (f"largest disagreement at any of the "
                         f"{_fmt(b, 'n_write_times')} write times, at t = "
                         f"{_fmt(b, 'largest_abs_diff_time_s', '.0f', 's')}, "
                         f"cell {_fmt(b, 'largest_abs_diff_cell')}")})
    out["quantity_rows"] = q
    return out


def _normalise(bundle: dict, key: str) -> dict:
    """One internal shape, whichever dialect arrived.

    The dialect is detected from the bundle's own content, not from the act
    letter, so a bundle that changes hands does not change meaning.
    """
    if "map_rows" in bundle:
        return _normalise_act_a(bundle)
    return _normalise_act_c(bundle)


# --------------------------------------------------------------------------
# The screens.
# --------------------------------------------------------------------------
#: Returned by ``_present`` when the act refuses. 1 = nothing on disk to show;
#: 2 = there is something to show and no evidence that it can be read, which
#: is the refusal the comparators in this family use.
_RC_NO_BUNDLE = 1
_RC_NO_CONTROL = 2


def _present(script, emit, roster, out: Path,
             key: str) -> tuple[dict | None, int]:
    """Put one act's screens up.

    Returns ``(bundle, rc)``. A ``None`` bundle means nothing was drawn and
    nothing was quoted, and ``rc`` says which of the two refusals it was.
    """
    spec = SCREEN_SETS[key]
    bundle, gap, missing_extras = _load_bundle(spec)
    if bundle is None:
        script.engineer(
            f"• {gap} "
            f"• Nothing is drawn in its place and no number for that body "
            f"appears anywhere below.")
        return None, _RC_NO_BUNDLE
    for item in missing_extras:
        script.engineer(
            f"• A screen product this act expects is not on disk: {item}. "
            f"• Nothing is shown in its place and nothing is inferred from "
            f"its absence.")
    # The keys the bundle ARRIVED with, kept before the normaliser adds any
    # of its own. The refusal below names what was actually on disk, and a
    # normaliser artefact in that list would misdescribe the file.
    offered_keys = sorted(bundle)
    bundle = _normalise(bundle, key)

    # ---- provenance, before any picture ----
    mesh = bundle.get("mesh") or {}
    prov_rows = [
        ["Source case", str(bundle.get("source_case", "not recorded"))],
        ["Reader", str(bundle.get("reader", "not recorded"))],
        ["Mesh cells", f"{mesh.get('n_mesh_cells', 'not recorded'):,}"
         if isinstance(mesh.get("n_mesh_cells"), int)
         else str(mesh.get("n_mesh_cells", "not recorded"))],
        ["Geometry guard", str(mesh.get("geometry_guard", "not recorded"))],
    ] + [list(r) for r in bundle.get("provenance_extra", [])]
    _emit_table(emit, script, role=_CE_ROLE,
                title=f"Where these screens come from: {spec['title']}",
                headers=("Item", "Value"), rows=prov_rows,
                table_id=f"provenance-thermal-{key}")

    # ---- the planted-zero instrument checks, on screen before the result ----
    #
    # THE REFUSAL. A bundle whose controls this act cannot find is a bundle
    # whose numbers this act cannot vouch for, and the failure mode being
    # guarded is silence: an earlier version simply drew nothing here and went
    # on to the temperatures. Nothing below this block runs unless a control
    # was found and named.
    rows = _instrument_rows(bundle)
    if not rows:
        offered = ", ".join(offered_keys[:12]) or "nothing at all"
        script.engineer(
            "• REFUSED, and no temperature is shown. "
            "• This act puts the instrument checks up before any number, "
            "because a reader never shown able to see a planted change "
            "cannot be trusted with the numbers it reports. "
            "• This body's screen bundle carries no control block that this "
            "act can recognise: it was looked for under 'instrument_check_' "
            "and under 'planted_zero_controls', and neither is present. "
            f"• What the bundle does carry: {offered}. "
            "• No figure is drawn and no quantity is quoted for this body "
            "until a control block is recorded beside its numbers.")
        return None, _RC_NO_CONTROL
    _emit_table(emit, script, role=_CE_ROLE,
                title="Instrument checks: a known perturbation, read back",
                headers=("Reader", "Planted", "Where", "Result"),
                rows=rows, table_id=f"instrument-thermal-{key}")
    if any(r[3] != "seen" for r in rows):
        script.engineer(
            "• One of the readers behind these screens could not see its "
            "own planted perturbation. "
            "• Treat every number below as unverified until that is "
            "resolved.")

    anchors = _anchor_rows(bundle)
    if anchors:
        headers, arows = anchors
        _emit_table(emit, script, role=_CE_ROLE,
                    title="Anchor checks: the same value, worked out twice",
                    headers=headers, rows=arows,
                    table_id=f"anchor-thermal-{key}")

    # ---- figures ----
    roster.set(CHIEF_ENGINEER, f"putting up the screens for {spec['title']}",
               "working")
    placed: set[str] = set()
    missing: list[str] = []
    for stem, title, status in spec["figures"]:
        path, reason = _png_for(stem, spec["folder"], out)
        if path is None:
            # A PENDING figure that is not there is not a fault: it was
            # declared as one that might not have landed, and the beat it
            # serves is named in the not-available table below instead.
            if status == LANDED:
                missing.append(f"{title}: {reason}")
            continue
        placed.add(stem)
        announce_plot(emit, BEAT, path, title)
    if missing:
        script.engineer(
            "• A screen this act expects to be able to put up was not there. "
            + " ".join(f"• {item}" for item in missing))

    # ---- the result table, from the bundle rather than from the picture ----
    table = bundle.get("result_table")
    if isinstance(table, dict) and table.get("rows"):
        _emit_table(emit, script, role=_CE_ROLE,
                    title=f"{table['title']}: {spec['title']}",
                    headers=table["headers"], rows=table["rows"],
                    table_id=f"result-thermal-{key}")

    # ---- what was asked for in this act and is not here ----
    #
    # Named, every time, rather than approximated or quietly left out. A row
    # whose figure did go up is dropped: a beat that was shown must not also
    # be declared missing.
    na_rows = [[item, why] for item, why, satisfied_by
               in spec.get("not_available", ())
               if satisfied_by is None or satisfied_by not in placed]
    if na_rows:
        _emit_table(emit, script, role=_CE_ROLE,
                    title=(f"Asked for in this act and NOT AVAILABLE from "
                           f"this run: {spec['title']}"),
                    headers=("What was asked for", "Why it is not shown"),
                    rows=na_rows, table_id=f"notavailable-thermal-{key}")
        bundle["_not_available_lines"] = [f"{item}: {why}"
                                          for item, why in na_rows]
    return bundle, 0


def _quantities(bundle: dict) -> list[dict]:
    """Result rows for the report, and only quantities the bundle defines.

    The normaliser has already reduced both dialects to one list, so this is
    a read rather than a computation.
    """
    return list(bundle.get("quantity_rows") or [])


def main(request: str | None = None, params: dict | None = None,
         emit=None) -> int:
    params = dict(params or {})
    out = OUT_ROOT / BEAT
    out.mkdir(parents=True, exist_ok=True)

    key = str(params.get("thermal_screens") or "C").upper()
    if key not in SCREEN_SETS:
        key = "C"
    spec = SCREEN_SETS[key]

    script = make_transcript(f"Thermal screens: {spec['title']}", emit)
    roster = Roster(emit)
    knowledge = KnowledgeBase(emit)
    began = time.monotonic()

    script.system(request or f"Request: show the thermal result for "
                             f"{spec['title']}.")

    # ---------------- What this act will and will not do ----------------
    script.phase(HYPOTHESIS)
    roster.set(CHIEF_ENGINEER, "restating the request", "working")
    script.engineer(
        f"• Reading this as a thermal question about {spec['title']}, a body "
        f"this lab has already run. "
        f"• No solver starts on this request and no new number is produced: "
        f"the screens come from that run's own fields. "
        f"• Anything the run does not define will be named as undefined "
        f"rather than shown as something adjacent.")

    surface = str(params.get("surface") or "").strip()
    if surface:
        from chief_engineer.display_names import display_name

        announce_geometry(emit, name=surface,
                          label=f"reference body: {display_name(surface)}")
        script.engineer(
            f"• Reference body received: {display_name(surface)}. "
            f"• The surface is on file as the reference shape. "
            f"• The screens below come from the run that landed for this "
            f"body, not from the uploaded file, and the uploaded file is "
            f"neither meshed nor solved by this act.")

    if emit:
        emit("solver.selected", {
            "solver": "none on this request",
            "method": "presentation of a landed conjugate thermal run",
            "basis": "the numbers exist already; running the case again "
                     "would produce the same field at a cost this request "
                     "does not need to pay"})

    # ---------------- The screens ----------------
    script.phase(EVIDENCE)
    roster.set(CHIEF_RESEARCHER, "checking the provenance of the screens",
               "working")
    bundle, rc = _present(script, emit, roster, out, key)
    roster.idle(CHIEF_RESEARCHER)
    if bundle is None:
        if rc == _RC_NO_BUNDLE:
            script.engineer(
                "• There is nothing on disk for this body, so there is "
                "nothing to show. "
                "• No figure is drawn and no number is quoted.")
            note = f"No landed screen bundle for {spec['title']}."
        else:
            script.engineer(
                "• This act refuses rather than showing numbers it cannot "
                "vouch for. "
                "• No figure is drawn and no number is quoted.")
            note = (f"Refused: the screen bundle for {spec['title']} records "
                    f"no instrument check, so its numbers are not evidence.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        if emit:
            emit("mission.note", {"note": note})
        return rc

    # ---------------- What the run cannot say ----------------
    undefined = [f"{name.replace('_', ' ')}: {value}"
                 for name, value in bundle.items()
                 if isinstance(value, str) and value.upper().startswith("NOT ")]
    for item in undefined:
        script.engineer(f"• {item[:1].upper()}{item[1:]}")

    quantities = _quantities(bundle)
    if quantities:
        _emit_table(emit, script, role=_CE_ROLE,
                    title=f"Quantities this run defines: {spec['title']}",
                    headers=("Quantity", "Value", "Basis"),
                    rows=[[q["quantity"], q["value"], q["envelope"]]
                          for q in quantities],
                    table_id=f"quantities-thermal-{key}")

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    elapsed = time.monotonic() - began
    script.engineer(
        f"• Screens up in {elapsed:.1f} seconds, with no solver started and "
        f"no compute booked against this request. "
        f"• The cost of the run these screens come from sits in that run's "
        f"own record, not against this one.")
    knowledge.add(f"Thermal screens presented for {spec['title']} from "
                  f"{bundle.get('source_case', 'the landed case')}")

    agenda = [
        {"title": "A second mesh for this body",
         "scope": "one refinement level would turn the uncertainty column "
                  "from a statement into a measured band",
         "cost": "one further solve at the finer level"},
        {"title": "Resolve the coolant as a fluid region",
         "scope": "the channels carry a convective coefficient rather than a "
                  "coupled stream, which is why no outlet temperature exists",
         "cost": "a conjugate case with a meshed fluid region"},
    ]
    if emit:
        emit("agenda.updated", {"entries": agenda})
        emit("report.ready", lab_report(
            title=f"Thermal screens: {spec['title']}",
            abstract=[
                f"The screens above were built from the run that landed for "
                f"{spec['title']}, at {bundle.get('source_case', 'its case directory')}.",
                "Nothing was solved to produce them and no quantity was "
                "re-derived: every value is the one the screen generator "
                "read off the written fields.",
            ],
            methods=[
                f"Read the screen bundle at "
                f"{spec['folder'] / spec['bundle']} and put its figures and "
                f"tables on screen unchanged.",
                "Placed the instrument checks in front of the result, so a "
                "reader that could not see its own planted perturbation "
                "would be visible before any number was quoted, and refused "
                "outright rather than showing numbers with no control "
                "behind them.",
            ],
            results=quantities,
            uncertainty=[
                "One mesh in this configuration, so no discretisation error "
                "estimate is available and the uncertainty column says so "
                "rather than carrying a number nobody measured.",
            ] + undefined + list(bundle.get("_not_available_lines", [])),
            next_investigations=[f"{e['title']}: {e['scope']}" for e in agenda],
            compute={"spent_core_minutes": 0.0,
                     "note": "no solver ran on this request"},
        ))

    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out)
    return 0


if __name__ == "__main__":
    act = "C"
    if "--act" in sys.argv:
        act = sys.argv[sys.argv.index("--act") + 1]
    raise SystemExit(main(params={"thermal_screens": act}))
