"""Staged still-capture sequence for the motorBike website video.

The beats, in order, are: upload/route -> mesh gates with real numbers ->
Cp-painted body -> drag + envelope -> certificate. This script drives a live
mission on YOUR server (port 8770 by default), watches the event stream, and at
each beat trigger captures a numbered 1920x1080 still with headless Chrome into
demo-output/website/motorbike-video/.

    python sdk/scripts/capture_motorbike_video.py \
        --geometry-path sdk/geometry/motorBike.obj

DEPENDENCY: the motorBike act must be green first (ACT-FIXER's D2 — the WSL case
directory is theirs, not mine, so I cannot run the solve). Until then this is
the ready-to-run kit; run it once the act completes on port 8770. If a beat
never fires within the timeout, its still is skipped and noted in the manifest —
the script never fabricates a frame.

Standard library only; no external packages.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_OUT = _REPO / "demo-output" / "website" / "motorbike-video"
_CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

# Each beat: (order, filename-stem, human title, trigger predicate over an event).
BEATS = [
    (1, "01-upload-route", "Upload & route",
     lambda ev: ev.get("type") == "mission.routed"),
    (2, "02-mesh-gates", "Mesh gates with real numbers",
     lambda ev: ev.get("type") == "transcript.entry"
     and "Mesh:" in json.dumps(ev.get("payload", {}))),
    (3, "03-cp-painted", "Cp-painted body",
     lambda ev: ev.get("type") == "field.ready"),
    (4, "04-drag-envelope", "Drag + envelope",
     lambda ev: ev.get("type") == "result.verdict"),
    (5, "05-certificate", "Certificate",
     lambda ev: ev.get("type") == "certificate.ready"),
]

_TERMINAL = {"mission.completed", "mission.failed"}


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _upload_surface(base: str, path: Path) -> str:
    body = path.read_bytes()
    req = urllib.request.Request(
        f"{base}/api/geometry/upload", data=body, method="POST",
        headers={"Content-Type": "application/octet-stream",
                 "X-Surface-Name": path.name})
    with urllib.request.urlopen(req, timeout=120) as resp:
        info = json.loads(resp.read().decode())
    print(f"[capture] uploaded {info['name']} — {info.get('triangles')} triangles")
    return info["name"]


def _shoot(base: str, mission_id: str, out_file: Path, budget_ms: int = 6000) -> bool:
    url = f"{base}/?mission={mission_id}&present=1"
    cmd = [
        _CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--window-size=1920,1080", f"--virtual-time-budget={budget_ms}",
        "--run-all-compositor-stages-before-draw",
        f"--screenshot={out_file}", url,
    ]
    try:
        subprocess.run(cmd, timeout=60, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except Exception as exc:
        print(f"[capture] chrome failed for {out_file.name}: {exc}")
        return False
    ok = out_file.exists() and out_file.stat().st_size > 0
    print(f"[capture] {'shot' if ok else 'MISSED'} {out_file.name}")
    return ok


def run(base: str, goal: str, surface: str, geometry_path: Path | None,
        out_dir: Path, timeout_s: float) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)

    if geometry_path is not None:
        surface = _upload_surface(base, geometry_path)

    launch = _post_json(f"{base}/api/missions", {"goal": goal, "surface": surface})
    mission_id = launch["mission_id"]
    print(f"[capture] mission {mission_id} — route {launch.get('route', {}).get('intent')}")

    captured: dict[str, str] = {}
    after = 0
    deadline = time.time() + timeout_s
    closed = False
    while time.time() < deadline and len(captured) < len(BEATS):
        try:
            page = _get_json(f"{base}/api/missions/{mission_id}/events.json?after={after}")
        except Exception as exc:
            print(f"[capture] poll error: {exc}")
            time.sleep(2.0)
            continue
        events = page.get("events", [])
        after = page.get("next_after", after)
        for ev in events:
            for order, stem, title, trigger in BEATS:
                if stem in captured:
                    continue
                try:
                    hit = trigger(ev)
                except Exception:
                    hit = False
                if hit:
                    out_file = out_dir / f"{stem}.png"
                    # Small settle so the page's replay renders this beat.
                    time.sleep(1.0)
                    if _shoot(base, mission_id, out_file):
                        captured[stem] = title
            if ev.get("type") in _TERMINAL:
                closed = True
        if closed or page.get("closed"):
            # Give late beats (certificate) a last poll pass before exiting.
            if len(captured) >= len(BEATS):
                break
            if closed and not events:
                break
        time.sleep(1.5)

    manifest = {
        "mission_id": mission_id,
        "goal": goal,
        "surface": surface,
        "server": base,
        "captured": [{"order": o, "stem": s, "title": t,
                      "file": f"{s}.png", "present": s in captured}
                     for (o, s, t, _) in BEATS],
        "complete": len(captured) == len(BEATS),
    }
    (out_dir / "capture-manifest.json").write_text(json.dumps(manifest, indent=2))
    missing = [s for (_, s, _, _) in BEATS if s not in captured]
    if missing:
        print(f"[capture] INCOMPLETE — missing beats: {', '.join(missing)}")
    else:
        print("[capture] all five beats captured")
    return 0 if not missing else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture the motorBike video stills.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--surface", default="motorBike.obj",
                        help="surface name already known to the server")
    parser.add_argument("--geometry-path", type=Path, default=None,
                        help="local .obj/.stl to upload first (overrides --surface)")
    parser.add_argument("--goal", default="Show me the pressure field on this motorbike.")
    parser.add_argument("--out", type=Path, default=_OUT)
    parser.add_argument("--timeout", type=float, default=1800.0,
                        help="max seconds to wait for the full solve")
    args = parser.parse_args(argv)

    base = f"http://{args.host}:{args.port}"
    return run(base, args.goal, args.surface, args.geometry_path,
               args.out.resolve(), args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
