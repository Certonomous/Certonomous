"""Certonomous mission workflows.

Each module answers one class of engineering request. The Chief Engineer's
router (``chief_engineer.router``) reads the request and dispatches here; every
number these workflows report comes from a real solver run.
"""

import os
import sys
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

# Resolved per host rather than hard-coded to WSL. See
# chief_engineer.openfoam.host_run_prefix for why.
from chief_engineer.openfoam import host_run_prefix  # noqa: E402
RUN_PREFIX = host_run_prefix()
OUT_ROOT = Path(os.environ.get(
    "CERTONOMOUS_OUTPUT",
    Path(__file__).resolve().parents[2] / "mission-output"))
OUT_ROOT.mkdir(parents=True, exist_ok=True)

NOMINAL_CYLINDER = {
    "cylinder_diameter": 1.0,
    "inlet_velocity": 1.0,
    "kinematic_viscosity": 0.05,
    "mesh_refinement": 1.0,
}


def safe_print(text: str) -> None:
    """Print without dying on a legacy console encoding.

    The chiefs speak in engineering prose (≈, ±, →, σ). A Windows console
    running cp1252 raises UnicodeEncodeError on those, which would otherwise
    kill a beat mid-run — the transcript must never be the thing that fails.
    """
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "ascii"
        print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"))


def make_transcript(mission: str, emit=None):
    """Transcript that prints to the terminal and streams to the control room."""
    from chief_engineer.transcript import Transcript

    sink = None
    if emit is not None:
        def sink(entry):
            emit("transcript.entry", entry.as_dict())
    return Transcript(mission, echo=safe_print, sink=sink)


def announce_plot(emit, beat: str, path, title: str) -> None:
    """Tell the control room a plot is ready so it can render it inline."""
    if emit is None or not path:
        return
    from pathlib import Path as _Path

    emit("plot.ready", {"beat": beat, "file": _Path(path).name, "title": title,
                        "url": f"/api/plot/{beat}/{_Path(path).name}"})


def announce_geometry(emit, *, name: str | None = None,
                      diameter: float | None = None, label: str = "") -> None:
    """Tell the control room which surface this mission is working on."""
    if emit is None:
        return
    if name:
        from chief_engineer.display_names import display_name

        emit("geometry.ready", {"url": f"/api/geometry?name={name}",
                                "label": label or display_name(name)})
    else:
        value = float(diameter if diameter is not None else 1.0)
        emit("geometry.ready", {"url": f"/api/geometry?diameter={value:.4f}",
                                "label": label or f"cylinder D={value:.3g} m"})


def acknowledge_reference_surface(script, emit, params, *, family: str
                                  ) -> str | None:
    """Acknowledge an uploaded surface as the reference body on file.

    Used by acts that run on a parametric family (the valve's orifice screen,
    the cylinder shape sweep): the surface is announced to the viewport under
    its display name, and the transcript states plainly that the screen runs
    on the parametric family while the uploaded surface stays on file as the
    reference shape. Nothing pretends the surface is meshed or solved by the
    screen. Returns the display name when a surface was acknowledged.
    """
    surface = str((params or {}).get("surface") or "").strip()
    if not surface:
        return None
    from chief_engineer.display_names import display_name

    surface_name = display_name(surface)
    announce_geometry(emit, name=surface,
                      label=f"reference body: {surface_name}")
    script.engineer(
        f"• Reference body received: {surface_name}. "
        f"• The surface is on file as the reference shape for this study. "
        f"• The screen itself runs on the parametric {family} family; the "
        f"uploaded surface is not meshed or solved by this screen.")
    return surface_name


# Wording doctrine (owner rule): the on-camera transcript never narrates the
# reuse machinery, never names a dash character, and never leans on the
# banned register below. Checked at authorship time rather than trusted, so a
# slip fails loudly in a test run instead of reaching the control room.
_BANNED_PHRASES = (
    "live", "real solve", "real solves", "solver backed", "solver-backed",
    "conceptual model", "demo", "stored", "saved", "cached", "precomputed",
    "reused", "trend",
)


def check_wording(text: str) -> None:
    """Raise if ``text`` breaks the on-camera wording doctrine."""
    if "—" in text or " - " in text:
        raise ValueError(f"dash not allowed in transcript prose: {text!r}")
    lowered = text.lower()
    for phrase in _BANNED_PHRASES:
        if phrase in lowered:
            raise ValueError(f"banned phrase {phrase!r} in transcript prose: {text!r}")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("•"):
            body = stripped[1:].strip()
            if body and not body[0:1].isupper():
                raise ValueError(f"bullet must start with a capital letter: {line!r}")


def bullets(sayer, *lines: str, **kwargs):
    """Emit one role entry holding every bullet on its own row.

    ``sayer`` is a bound method on the transcript, e.g. ``script.numericist``.
    Every line is prefixed with a bullet mark, checked against the wording
    doctrine, and joined into the single entry that role owns for this beat
    (never split across several entries, never the same role called twice in
    a row for one thought).
    """
    body = "\n".join(f"• {line.strip()}" for line in lines if line.strip())
    check_wording(body)
    return sayer(body, **kwargs)


def emit_table(emit, script, *, role: str, title: str, headers, rows,
              table_id: str, append: bool = False) -> None:
    """Put a transcript table on the record. Every result an act reports
    belongs here, never repeated as bare numbers in prose.

    The control room renders it as a compact table in the paced feed;
    ``append=True`` lands new rows into the existing table so rows arrive
    live as solves finish. Every row is mirrored into the saved transcript
    so the on-disk record keeps the numbers."""
    import time as _time

    from chief_engineer.transcript import Entry

    if emit:
        emit("transcript.table", {
            "role": role, "title": title,
            "headers": [str(h) for h in headers],
            "rows": [[str(cell) for cell in row] for row in rows],
            "table_id": table_id, "append": bool(append), "at": _time.time()})
    for row in rows:
        line = " | ".join(f"{h} {cell}" for h, cell in zip(headers, row))
        entry = Entry(role, f"[{title}] {line}")
        script.entries.append(entry)
        if emit is None and script.echo:
            script.echo(entry.render())


def announce_field(emit, beat: str, path, label: str) -> None:
    """Tell the control room a solved surface is painted and ready to render.

    Carries a bounding-box hint from the painted body so the viewport can
    auto-frame the camera on the vehicle rather than the old (possibly larger)
    geometry extent.
    """
    if emit is None or not path:
        return
    import json
    from pathlib import Path as _Path

    payload = {"beat": beat, "file": _Path(path).name, "label": label,
               "url": f"/api/field/{beat}/{_Path(path).name}"}
    try:
        bounds = json.loads(_Path(path).read_text(encoding="utf-8")).get("bounds")
        if bounds:
            payload["bounds"] = bounds
    except (OSError, ValueError):
        pass
    emit("field.ready", payload)
