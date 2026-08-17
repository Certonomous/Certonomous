"""Staged still-capture kit for the five website videos.

One driver for all five GUI-native acts — airplane (B-52), motorBike, valve,
optimization (airliner), and the race. For a chosen video it POSTs that act's
directive to YOUR server (port 8772 by default), watches the mission's event
stream, and at each beat trigger captures a numbered 1920x1080 still with
headless Chrome into demo-output/website/<video>/. It also writes a shotlist.md
with a one-line narration bullet per beat (<=14 words, no em-dashes).

    python sdk/scripts/capture_video.py --video race
    python sdk/scripts/capture_video.py --video valve
    python sdk/scripts/capture_video.py --video optimization
    python sdk/scripts/capture_video.py --video motorbike
    python sdk/scripts/capture_video.py --video airplane      # long: cold mesh
    python sdk/scripts/capture_video.py --video all            # every fast act

A beat that never fires within the timeout is skipped and noted in the manifest
and shotlist — the script never fabricates a frame. The numbers on screen come
from the live mission; this kit only decides WHEN to press the shutter.

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

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

_REPO = Path(__file__).resolve().parents[2]
_SDK = Path(__file__).resolve().parents[1]
# MOVE_MAP s4 calls this one UNRESOLVABLE STATICALLY: the child is
# `spec["out"]`, so the successor is DATA and no constant can name it.
# `lab_paths.WEB` is the honest binding -- the webroot itself -- and any
# spec naming a child that leaves the webroot is a data repair, not a
# code one.
_WEBSITE = lab_paths.WEB
_CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"


# --------------------------------------------------------------------------
# Beat triggers — predicates over a single mission event (event + payload)
# --------------------------------------------------------------------------

def _payload_text(ev: dict) -> str:
    return json.dumps(ev.get("payload", {}))


def evt(name: str):
    return lambda ev: ev.get("event") == name


def transcript_has(*needles: str):
    def _pred(ev: dict) -> bool:
        if ev.get("event") != "transcript.entry":
            return False
        text = _payload_text(ev).lower()
        return any(n.lower() in text for n in needles)
    return _pred


def role_speaks(role: str):
    def _pred(ev: dict) -> bool:
        if ev.get("event") != "transcript.entry":
            return False
        return (ev.get("payload", {}).get("role") or "").lower() == role.lower()
    return _pred


def lane_done(lane: str):
    def _pred(ev: dict) -> bool:
        p = ev.get("payload", {})
        return (ev.get("event") == "race.lane" and p.get("lane") == lane
                and p.get("state") == "done")
    return _pred


def lane_progress(lane: str, frac: float):
    def _pred(ev: dict) -> bool:
        p = ev.get("payload", {})
        if ev.get("event") != "race.lane" or p.get("lane") != lane:
            return False
        total = p.get("total") or 0
        return (p.get("state") != "done" and total
                and (p.get("done") or 0) / total >= frac)
    return _pred


# --------------------------------------------------------------------------
# The five videos: directive, optional surface, and the beat list
# --------------------------------------------------------------------------
# Each beat: (order, stem, title, narration, trigger). Narration lines are the
# video's spoken bullets: <=14 words, no em-dashes, method language (no tool or
# vendor names, no self-grading).

_B52 = ("Solve the external aerodynamics of the supplied B-52 geometry at "
        "240 m/s, sea-level conditions. Select the appropriate turbulence "
        "model and solver, gate the mesh on quality, and report drag and lift "
        "with confidence envelopes.")
_MOTO = ("Solve the external aerodynamics of the supplied motorcycle-with-rider "
         "geometry at highway speed, sea-level conditions. Select the "
         "appropriate turbulence model and solver, gate the mesh on quality, "
         "and report the drag coefficient with a confidence envelope.")
_VALVE = ("Optimize the leaflet opening angle of the aortic valve to minimize "
          "pressure loss over the cardiac cycle. Decompose the cycle into "
          "representative phase points, rule on the admissible method, and "
          "report the cycle-weighted loss with its uncertainty.")
_AIRLINER = ("Optimize the lift-to-drag ratio of a twin-aisle airliner "
             "carrying 300 passengers over a 6000 km range, with take-off at "
             "85 m/s and landing at 72 m/s. Search the wing design space, mark "
             "any infeasible designs, and report the best feasible L/D with "
             "its envelope.")
_RACE = ("Race a full Monte-Carlo sweep against the reduced-order path on the "
         "NACA 4412 finite wing: same objective, same tolerance, both timed. "
         "Report the polar, the agreement, and the measured speedup.")

_CFD_BEATS = lambda body: [
    (1, "01-upload-route", "Upload and route",
     f"We hand the lab a {body} and it plans the whole run.", evt("mission.routed")),
    (2, "02-mesh-gates", "Mesh gates with real numbers",
     "The mesh is built and gated on real quality numbers.",
     transcript_has("mesh", "non-ortho", "skew")),
    (3, "03-cp-painted", "Pressure-painted body",
     "The solved surface pressure paints the body in place.", evt("field.ready")),
    (4, "04-drag-envelope", "Force with its envelope",
     "The force lands as a value with a confidence envelope.", evt("result.verdict")),
    (5, "05-certificate", "Sealed certificate",
     "A sealed certificate records exactly how it was solved.", evt("certificate.ready")),
]

VIDEOS: dict[str, dict] = {
    "airplane": {
        "out": "airplane", "goal": _B52, "surface": "b52.stl",
        "present": True, "beats": _CFD_BEATS("B-52"),
        "note": "long: cold snapped mesh is roughly eight minutes",
    },
    "motorbike": {
        "out": "motorbike", "goal": _MOTO, "surface": "motorBike.obj",
        "present": True, "beats": _CFD_BEATS("motorcycle"),
        "note": "solve-bound; pre-warm the mesh cache for the on-camera run",
    },
    "valve": {
        "out": "valve", "goal": _VALVE, "surface": None, "present": True,
        "beats": [
            (1, "01-interpretation", "Interpretation",
             "The lab reads this as a pulsatile internal-flow screen.",
             evt("mission.routed")),
            (2, "02-womersley", "Periodicity and Womersley",
             "It computes the Womersley number and rules the method admissible.",
             transcript_has("womersley")),
            (3, "03-phase-plan", "Phase-point plan",
             "The cardiac cycle splits into three weighted phase points.",
             transcript_has("phase", "weight", "0.25")),
            (4, "04-result", "Cycle-weighted result",
             "The cycle-weighted pressure loss lands with its uncertainty.",
             evt("result.verdict")),
            (5, "05-agenda", "Research agenda",
             "The lab records the higher-fidelity steps it would take next.",
             evt("agenda.updated")),
        ],
        "note": "compute-light; the real internal-flow solve is the marked next step",
    },
    "optimization": {
        "out": "optimization", "goal": _AIRLINER, "surface": None, "present": True,
        "beats": [
            (1, "01-interpretation", "Interpretation",
             "The lab reads this as a wing lift-to-drag optimization.",
             evt("mission.routed")),
            (2, "02-researcher-memo", "Method-selection memo",
             "The researcher picks the method before anything runs.",
             role_speaks("Chief Researcher")),
            (3, "03-landscape", "Design-space landscape",
             "The design space fills in, infeasible wings greyed out.",
             evt("landscape.init")),
            (4, "04-finalists", "Finalists solved for real",
             "The top wings promote to real parallel aerodynamic solves.",
             evt("vspaero.polar")),
            (5, "05-result", "Best feasible L/D",
             "The winner is chosen on solved numbers, with its envelope.",
             evt("result.verdict")),
            (6, "06-report", "Report and certificate",
             "The report leads with figures and a sealed certificate.",
             evt("report.ready")),
        ],
        "note": "compute-light on camera; six real finalist solves in parallel",
    },
    "race": {
        "out": "race-gui", "goal": _RACE, "surface": None, "present": True,
        "beats": [
            (1, "01-start", "The race is set",
             "Same question, two methods, both real and both timed.",
             evt("race.init")),
            (2, "02-mid-mc-grinding", "Monte-Carlo grinding",
             "The brute-force lane grinds through every solved point.",
             lane_progress("mc", 0.45)),
            (3, "03-reduced-order-finished", "Reduced-order crosses first",
             "The reduced-order lane certifies the peak in a handful of solves.",
             lane_done("rom")),
            (4, "04-finish", "Speed, certified",
             "Same answer, measured speedup, every number from this run.",
             evt("race.result")),
        ],
        "note": "both lanes real VSPAERO solves under a four-slot cap",
    },
}


# --------------------------------------------------------------------------
# HTTP + Chrome plumbing
# --------------------------------------------------------------------------

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


def _shoot(base: str, mission_id: str, out_file: Path, present: bool,
           upto: int | None = None, budget_ms: int = 8000) -> bool:
    # Deterministic still: the ?static=1 path replays the persisted event log
    # synchronously (no live SSE race in headless), and ?upto=<sequence> freezes
    # the exact mid-flight beat instead of the end-state.
    parts = [f"mission={mission_id}", "static=1"]
    if present:
        parts.append("present=1")
    if upto:
        parts.append(f"upto={int(upto)}")
    url = f"{base}/?" + "&".join(parts)
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


_TERMINAL = {"mission.completed", "mission.failed"}


def _write_shotlist(video: str, spec: dict, out_dir: Path, mission_id: str,
                    captured: dict[str, str]) -> None:
    lines = [f"# {video} website video shotlist", "",
             f"Directive: {spec['goal']}", "",
             f"Mission: {mission_id}", ""]
    if spec.get("note"):
        lines += [f"Note: {spec['note']}.", ""]
    lines += ["Per-beat narration (spoken bullets, <=14 words):", ""]
    for order, stem, title, narration, _ in spec["beats"]:
        mark = "" if stem in captured else "  (beat did not fire this run)"
        lines.append(f"{order}. {title} · `{stem}.png`{mark}")
        lines.append(f"   - {narration}")
    lines.append("")
    (out_dir / "shotlist.md").write_text("\n".join(lines), encoding="utf-8")


def run(base: str, video: str, geometry_root: Path, timeout_s: float,
        settle_s: float) -> int:
    spec = VIDEOS[video]
    out_dir = _WEBSITE / spec["out"]
    out_dir.mkdir(parents=True, exist_ok=True)

    surface = spec.get("surface")
    if surface:
        local = geometry_root / surface
        if local.exists():
            # Known to the server already (lives in its geometry dir), but an
            # upload guarantees it and returns the canonical name.
            surface = _upload_surface(base, local)

    payload = {"goal": spec["goal"]}
    if surface:
        payload["surface"] = surface
    launch = _post_json(f"{base}/api/missions", payload)
    mission_id = launch["mission_id"]
    print(f"[capture] {video}: mission {mission_id} — route "
          f"{launch.get('route', {}).get('intent')}")

    beats = spec["beats"]
    # Phase 1 — watch the live mission and record the event SEQUENCE at which
    # each beat first fires. No shooting yet: the solver should not compete with
    # four headless Chrome instances, and the still is deterministic anyway.
    beat_seq: dict[str, int] = {}
    after = 0
    deadline = time.time() + timeout_s
    closed = False
    while time.time() < deadline and len(beat_seq) < len(beats):
        try:
            page = _get_json(f"{base}/api/missions/{mission_id}/events.json?after={after}")
        except Exception as exc:
            print(f"[capture] poll error: {exc}")
            time.sleep(2.0)
            continue
        events = page.get("events", [])
        after = page.get("next_after", after)
        for ev in events:
            for _order, stem, _title, _narr, trigger in beats:
                if stem in beat_seq:
                    continue
                try:
                    hit = trigger(ev)
                except Exception:
                    hit = False
                if hit:
                    beat_seq[stem] = ev.get("sequence")
                    print(f"[capture] beat '{stem}' at seq {ev.get('sequence')}")
            if ev.get("event") in _TERMINAL:
                closed = True
        if closed and not events:
            break
        time.sleep(1.0)

    # Phase 2 — shoot each recorded beat as a deterministic frozen frame.
    time.sleep(settle_s)
    captured: dict[str, str] = {}
    for _order, stem, title, _narr, _trigger in beats:
        seq = beat_seq.get(stem)
        if seq is None:
            continue
        if _shoot(base, mission_id, out_dir / f"{stem}.png",
                  spec.get("present", True), upto=seq):
            captured[stem] = title

    manifest = {
        "video": video, "mission_id": mission_id, "goal": spec["goal"],
        "surface": surface, "server": base,
        "captured": [{"order": o, "stem": s, "title": t,
                      "present": s in captured}
                     for (o, s, t, _n, _tr) in beats],
        "complete": len(captured) == len(beats),
    }
    (out_dir / "capture-manifest.json").write_text(json.dumps(manifest, indent=2))
    _write_shotlist(video, spec, out_dir, mission_id, captured)
    missing = [s for (_o, s, _t, _n, _tr) in beats if s not in captured]
    if missing:
        print(f"[capture] {video}: INCOMPLETE — missing: {', '.join(missing)}")
    else:
        print(f"[capture] {video}: all {len(beats)} beats captured")
    return 0 if not missing else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture website video stills.")
    parser.add_argument("--video", default="race",
                        choices=[*VIDEOS.keys(), "all", "fast"],
                        help="which act ('all' = every act, 'fast' = valve, "
                             "optimization, race)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8772)
    parser.add_argument("--geometry-root", type=Path,
                        default=_SDK / "geometry")
    parser.add_argument("--timeout", type=float, default=2400.0,
                        help="max seconds to wait for the full act")
    parser.add_argument("--settle", type=float, default=1.2,
                        help="seconds to let the page render a beat before shooting")
    args = parser.parse_args(argv)

    base = f"http://{args.host}:{args.port}"
    if args.video == "all":
        order = ["valve", "optimization", "race", "motorbike", "airplane"]
    elif args.video == "fast":
        order = ["valve", "optimization", "race"]
    else:
        order = [args.video]

    rc = 0
    for video in order:
        rc = run(base, video, args.geometry_root.resolve(), args.timeout,
                 args.settle) or rc
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
