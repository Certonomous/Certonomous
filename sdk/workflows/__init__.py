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

RUN_PREFIX = ["wsl", "-d", "Ubuntu", "-u", "foam", "--", "openfoam2606"]
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
