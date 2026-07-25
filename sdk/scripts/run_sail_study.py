"""Run the geometry-study act headless on the NACA 0015 submarine sail.

Chord 1.2 m along +X; target regime Re = 6e6. With the pipeline's air
kinematic viscosity nu = 1.5e-5 m^2/s (chief_engineer.external_aero.build_case),
V = Re * nu / c = 6e6 * 1.5e-5 / 1.2 = 75.0 m/s, so the case sits at
exactly Re 6.0e6 on the record. Events are captured to a JSONL file so the
run is auditable without a GUI.

    python scripts/run_sail_study.py [events.jsonl]
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))


def main(argv: list[str]) -> int:
    events_path = Path(argv[0]) if argv else SDK.parent / "demo-output" / "plots" / "submarine_sail" / "events.jsonl"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(events_path, "w", encoding="utf-8")

    def emit(event: str, payload: dict) -> None:
        try:
            fh.write(json.dumps({"t": time.time(), "event": event,
                                 "payload": payload}) + "\n")
            fh.flush()
        except (TypeError, ValueError, OSError):
            pass

    from workflows import geometry_study

    started = time.monotonic()
    code = geometry_study.main(
        request="Study the NACA 0015 sail, chord 1.2 m, Re 6e6",
        params={"surface": "naca0015_sail.stl",
                "velocity": 75.0,
                "streamwise_axis": 0},
        emit=emit)
    emit("runner.done", {"exit": code,
                         "wall_seconds": round(time.monotonic() - started, 1)})
    fh.close()
    print(f"exit={code} wall={time.monotonic() - started:.0f}s events={events_path}")
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
