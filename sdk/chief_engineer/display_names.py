"""Human display names for geometries — the only names allowed on camera.

Every body the lab solves has an internal slug (a filename stem, a curriculum
label, a router ``geometry`` param) and a human display name. Narration,
report titles, certificates, and any GUI-facing label must use the display
name; the internal slug is a lookup key, never a screen string.

This module is the single ratified mapping. Import ``display_name`` rather
than writing a name inline, so the website/certificate agent and every
workflow stay in agreement without duplicating the list.
"""

from __future__ import annotations

from pathlib import Path

# Ratified display names, keyed by a normalized slug — the lowercased filename
# stem or curriculum label the rest of the codebase already uses internally to
# refer to a body. Add here, not inline at a call site.
_DISPLAY_NAMES: dict[str, str] = {
    "b52": "B-52 Stratofortress-class airframe",
    "motorbike": "Motorcycle with rider, highway configuration",
    "airliner": "300-passenger twin-aisle airliner, planform study",
    "aircraft-optimization": "300-passenger twin-aisle airliner, planform study",
    "aircraft_optimization": "300-passenger twin-aisle airliner, planform study",
    "naca4412": "NACA 4412 finite wing",
    "naca4412_wing": "NACA 4412 finite wing",
    "naca0012": "NACA 0012 finite wing",
    "naca0012_wing": "NACA 0012 finite wing",
    "naca0015": "NACA 0015 sail",
    "naca0015_sail": "NACA 0015 sail",
    "valve": "Idealized trileaflet aortic valve, systolic configuration",
    "aortic_valve": "Idealized trileaflet aortic valve, systolic configuration",
    "valve_study": "Idealized trileaflet aortic valve, systolic configuration",
    "valve-study": "Idealized trileaflet aortic valve, systolic configuration",
    "ahmed_25": "Ahmed reference body, 25° slant",
    "ahmed_35": "Ahmed reference body, 35° slant",
    "sphere": "Canonical calibration body: sphere",
    "cube": "Canonical calibration body: cube",
    "plate": "Canonical calibration body: plate",
    "flat_plate": "Canonical calibration body: plate",
    "cylinder": "Canonical calibration body: cylinder",
}


def _slug(key: str) -> str:
    """Normalize a filename or label to the lookup key: no path, no extension,
    no case, dashes and spaces folded to underscores."""
    text = str(key).strip()
    if any(sep in text for sep in ("/", "\\", ".")):
        text = Path(text).stem
    return text.strip().lower().replace(" ", "_").replace("-", "_")


def display_name(key_or_filename: str | None) -> str:
    """Return the human display name for a geometry key or filename.

    Looks up the ratified table first; an unregistered body still reads as a
    name rather than a path or a code slug — the fallback strips any
    extension/directory and turns underscores into spaces, title-cased.
    Never returns a raw dotted filename or an underscored slug.
    """
    if not key_or_filename:
        return "Unnamed body"
    slug = _slug(key_or_filename)
    if slug in _DISPLAY_NAMES:
        return _DISPLAY_NAMES[slug]
    fallback = slug.replace("_", " ").strip()
    return fallback[:1].upper() + fallback[1:] if fallback else "Unnamed body"


__all__ = ["display_name"]
