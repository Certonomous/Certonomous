"""Control-room web service for the Certonomous lab.

A single-file server built on the standard library. It hands the browser the
control room, accepts a natural-language objective and runs the matching
workflow on a background thread, streams that mission's transcript over
Server-Sent Events, and serves the artifacts a mission leaves behind — envelope
plots, the pressure-painted surface, the sealed certificate, and the standing
validation wall. Every mission's events are broadcast live and appended to disk,
so a reload replays the run rather than losing it.
"""

from __future__ import annotations

import json
import os
import secrets
import sys
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .adapters import SoftwareAdapterRegistry, synthetic_registry
from .api import SyntheticApi
from .events import EventBus
from . import lab_stats

# Kept public for the module entrypoint and any external caller.
HERE = _PACKAGE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("CHIEF_ENGINEER_PORT", "8765"))
MAX_MISSIONS = 24


# --------------------------------------------------------------------------
# Where artifacts, credentials, and mission state live on disk
# --------------------------------------------------------------------------

def _output_root() -> Path:
    return Path(os.environ.get(
        "CERTONOMOUS_OUTPUT", HERE.parents[1] / "mission-output")).resolve()


def _credentials_root() -> Path:
    return Path(os.environ.get(
        "CERTONOMOUS_CREDENTIALS",
        HERE.parents[1] / "models" / "curriculum" / "results")).resolve()


def _state_root() -> Path:
    workdir = Path(os.environ.get("CHIEF_ENGINEER_WORKDIR", "./chief-engineer-runs")).resolve()
    root = Path(os.environ.get("CHIEF_ENGINEER_STATE_DIR", str(workdir / "mission-state"))).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _events_path(mission_id: str) -> Path:
    return _state_root() / f"{mission_id}.events.jsonl"


# --------------------------------------------------------------------------
# The validation wall
# --------------------------------------------------------------------------

# Earned credentials lead; the honest caveats follow. Legacy tier names in
# stored records are translated to the current fidelity chips at serve time.
_TIER_RANK = {"VALIDATED": 0, "SOLVER-BACKED": 1, "CONCEPTUAL MODEL": 2,
              "UNCONVERGED": 3}
_LEGACY_TIERS = {"TREND ONLY": "SOLVER-BACKED",
                 "REFERENCE REGIME MISMATCH": "SOLVER-BACKED",
                 "NEEDS WORK": "UNCONVERGED"}


def _credentials() -> list[dict]:
    """One card per graded curriculum body for the standing 'Lab credentials'
    panel — the tier it earned, measured-vs-reference, source, and the honest
    one-line reason. The wall shows judgement, not only trophies, so TREND ONLY
    and REGIME MISMATCH bodies appear alongside the validated ones."""
    root = _credentials_root()
    if not root.exists():
        return []
    cards: list[dict] = []
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        name = data.get("name")
        if not name:
            continue
        # ONE number everywhere: the wall displays the coefficient on the
        # reference's own area basis — the same figure the verdict was judged
        # on and the reason text quotes. The raw solver value stays available
        # as measured_raw for the evidence trail.
        compared = data.get("cd_compared")
        tier = data.get("tier") or "UNCONVERGED"
        cards.append({
            "name": name,
            "tier": _LEGACY_TIERS.get(tier, tier),
            "measured": compared if compared is not None else data.get("cd_measured"),
            "measured_raw": data.get("cd_measured"),
            "area_basis": data.get("area_basis"),
            "envelope": data.get("envelope"),
            "reference_cd": data.get("reference_cd"),
            "source": data.get("reference_source"),
            "reason": data.get("reason"),
            "wall_minutes": data.get("wall_minutes"),
            "finished_at": data.get("finished_at"),
        })
    cards.sort(key=lambda card: (_TIER_RANK.get(card["tier"], 9), card["name"]))
    return cards


# --------------------------------------------------------------------------
# Mission bookkeeping
# --------------------------------------------------------------------------

@dataclass
class MissionRecord:
    id: str
    request: str
    bus: EventBus
    state: str = "queued"
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    result_snapshot: dict | None = None
    error: str | None = None

    def public(self) -> dict:
        """The JSON view the control room reads for a mission."""
        return {
            "mission_id": self.id,
            "request": self.request,
            "state": self.state,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
            "result": self.result_snapshot,
        }


_missions: dict[str, MissionRecord] = {}
_missions_lock = threading.Lock()


def _record(mission_id: str) -> MissionRecord | None:
    with _missions_lock:
        return _missions.get(mission_id)


def _persist(record: MissionRecord) -> None:
    """Write the mission's public view atomically so a crash never leaves a
    half-written file."""
    path = _state_root() / f"{record.id}.json"
    staging = path.with_suffix(".json.tmp")
    staging.write_text(json.dumps(record.public(), separators=(",", ":")))
    staging.replace(path)


def _rehydrate_missions() -> None:
    """Bring prior missions back from disk on start-up so their evidence stays
    replayable. A mission caught mid-flight by a restart is marked failed but
    keeps whatever it had streamed."""
    with _missions_lock:
        if _missions:
            return
        for path in sorted(_state_root().glob("m-*.json")):
            try:
                item = json.loads(path.read_text())
                mission_id = str(item["mission_id"])
            except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError):
                continue
            bus = EventBus(mission_id, _events_path(mission_id))
            record = MissionRecord(
                id=mission_id,
                request=str(item.get("request", "")),
                bus=bus,
                state=str(item.get("state", "failed")),
                created_at=float(item.get("created_at", path.stat().st_mtime)),
                started_at=item.get("started_at"),
                finished_at=item.get("finished_at"),
                result_snapshot=item.get("result"),
                error=item.get("error"),
            )
            if record.state in {"queued", "running"}:
                record.state = "failed"
                record.error = ("Mission interrupted by a service restart. "
                                "Existing evidence remains replayable.")
                record.finished_at = time.time()
                bus.publish("mission.failed", {"reason": record.error})
                _persist(record)
            bus.close()
            _missions[mission_id] = record


# --------------------------------------------------------------------------
# Request handling
# --------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # -- silence the default access log --
    def log_message(self, *_args) -> None:
        return

    # -- response primitives --
    def _write(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _write_json(self, code: int, payload) -> None:
        self._write(code, json.dumps(payload).encode(), "application/json")

    def _fail(self, code: int, message: str) -> None:
        self._write_json(code, {"error": message})

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def _serve_guarded_file(self, root: Path, target: Path, content_type: str,
                            missing: str) -> None:
        """Serve a file only if it resolves to somewhere under ``root`` — the
        traversal guard for every artifact endpoint."""
        target = target.resolve()
        if root not in target.parents or not target.exists():
            self._fail(404, missing)
            return
        self._write(200, target.read_bytes(), content_type)

    # ---- GET ----------------------------------------------------------------
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path, query = parsed.path, parse_qs(parsed.query)

        exact = {
            "/": self._serve_control_room,
            "/health": self._serve_health,
            "/api/capabilities": self._serve_capabilities,
            "/api/credentials": lambda _q: self._write_json(200, _credentials()),
            "/api/lab-stats": lambda _q: self._write_json(200, lab_stats.lifetime_counters()),
            "/api/geometry": self._serve_geometry,
            "/api/compute-audit": self._serve_compute_audit,
            "/api/missions": self._serve_mission_list,
        }
        if path in exact:
            exact[path](query)
            return
        if path.startswith("/api/plot/"):
            self._serve_artifact(path, ".png", "image/png", "unknown plot")
            return
        if path.startswith("/api/field/"):
            self._serve_artifact(path, ".json", "application/json", "unknown field surface")
            return
        if path.startswith("/api/surface/"):
            self._serve_surface_artifact(path)
            return
        if path.startswith("/api/certificate/"):
            self._serve_certificate(path)
            return
        if self._serve_mission_detail(path, query):
            return
        self._fail(404, "not found")

    def _serve_control_room(self, _query) -> None:
        self._write(200, (HERE / "control_room.html").read_bytes(),
                    "text/html; charset=utf-8")

    def _serve_health(self, _query) -> None:
        self._write_json(200, {
            "service": "certonomous",
            "backend": _backend_name(),
            "worker_provider": _worker_provider_name(),
            "reasoning": _reasoning_name(),
            "persistence": "durable-jsonl",
            "missions": len(_missions),
        })

    def _serve_capabilities(self, _query) -> None:
        self._write_json(200, [manifest.as_dict() for manifest in _registry().manifests()])

    def _serve_geometry(self, query) -> None:
        from .geometry import (cylinder_surface, load_surface, valve_surface,
                               wing_surface)

        name = (query.get("name") or [""])[0]
        try:
            if name:
                root = (HERE.parent / "geometry").resolve()
                target = (root / name).resolve()
                if root not in target.parents or not target.exists():
                    self._fail(404, "unknown geometry")
                    return
                payload = load_surface(target)
            elif query.get("valve_angle"):
                payload = valve_surface(float((query.get("valve_angle") or ["60"])[0]))
            elif query.get("span"):
                payload = wing_surface(
                    float((query.get("span") or ["40"])[0]),
                    float((query.get("area") or ["300"])[0]),
                    sweep_deg=float((query.get("sweep") or ["27.5"])[0]),
                    taper=float((query.get("taper") or ["0.3"])[0]))
            else:
                diameter = float((query.get("diameter") or ["1.0"])[0])
                payload = cylinder_surface(diameter)
        except Exception as exc:
            self._fail(400, f"{type(exc).__name__}: {exc}")
            return
        self._write_json(200, payload)

    def _serve_compute_audit(self, query) -> None:
        from .compute_audit import audit as compute_audit

        workers = int((query.get("workers") or ["8"])[0])
        self._write_json(200, compute_audit(workers, memory_per_worker_mb=256).panel())

    def _serve_mission_list(self, _query) -> None:
        with _missions_lock:
            ordered = sorted(_missions.values(), key=lambda item: item.created_at, reverse=True)
            self._write_json(200, [record.public() for record in ordered])

    def _serve_artifact(self, path: str, suffix: str, content_type: str, missing: str) -> None:
        parts = path.strip("/").split("/")
        if len(parts) != 4 or not parts[3].endswith(suffix):
            self._fail(404, "not found")
            return
        self._serve_guarded_file(_output_root(), _output_root() / parts[2] / parts[3],
                                 content_type, missing)

    def _serve_surface_artifact(self, path: str) -> None:
        """Serve a mission-produced surface (e.g. a solved finalist wing) as
        the same decimated viewport payload /api/geometry returns."""
        from .geometry import load_surface

        parts = path.strip("/").split("/")
        if len(parts) != 4 or not parts[3].endswith((".stl", ".obj")):
            self._fail(404, "not found")
            return
        root = _output_root().resolve()
        target = (root / parts[2] / parts[3]).resolve()
        if root not in target.parents or not target.exists():
            self._fail(404, "unknown surface")
            return
        try:
            self._write_json(200, load_surface(target))
        except Exception as exc:
            self._fail(400, f"{type(exc).__name__}: {exc}")

    def _serve_certificate(self, path: str) -> None:
        parts = path.strip("/").split("/")
        if len(parts) != 3:
            self._fail(404, "not found")
            return
        self._serve_guarded_file(_output_root(), _output_root() / parts[2] / "certificate.pdf",
                                 "application/pdf", "no certificate for this mission")

    def _serve_mission_detail(self, path: str, query) -> bool:
        """Handle /api/missions/<id>[/events|/events.json]. Returns True if the
        path was a mission path (handled), False to let the caller 404."""
        parts = path.strip("/").split("/")
        if len(parts) < 3 or parts[:2] != ["api", "missions"]:
            return False
        mission_id = parts[2]
        suffix = parts[3] if len(parts) > 3 else ""
        record = _record(mission_id)
        if record is None:
            self._fail(404, "unknown mission")
            return True
        if suffix == "events.json":
            after = int((query.get("after") or ["0"])[0])
            events = [event.as_dict() for event in record.bus.snapshot(after=after)]
            self._write_json(200, {
                "mission_id": mission_id,
                "after": after,
                "next_after": events[-1]["sequence"] if events else after,
                "closed": record.bus.closed,
                "events": events,
            })
        elif suffix == "events":
            after = int((query.get("after") or ["0"])[0])
            self._stream_events(record, after)
        elif not suffix:
            self._write_json(200, record.public())
        else:
            self._fail(404, "not found")
        return True

    # ---- POST ---------------------------------------------------------------
    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/geometry/upload":
            self._accept_surface()
            return
        if path == "/api/ask":
            self._answer_question()
            return
        if path == "/api/missions":
            self._launch_mission()
            return
        self._fail(404, "not found")

    def _answer_question(self) -> None:
        from . import ask_the_lab
        from .citations import display

        try:
            question = str(self._read_json_body().get("question") or "").strip()
        except Exception:
            question = ""
        if not question:
            self._fail(400, "a question is required")
            return
        answer = ask_the_lab.answer(question)
        payload = answer.to_dict()
        # Citations always render as human display titles, never file paths.
        payload["citations"] = [display(c) for c in answer.citations]
        self._write_json(200, payload)

    def _launch_mission(self) -> None:
        try:
            payload = self._read_json_body()
            request = str(payload.get("goal") or payload.get("request") or "").strip()
            if not request:
                raise ValueError("goal is required")
            record, route = _start_mission(request, payload)
            self._write_json(202, {"mission_id": record.id, "state": record.state,
                                   "route": route.as_dict()})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._fail(400, f"{type(exc).__name__}: {exc}")

    def _accept_surface(self) -> None:
        """Store a surface the caller uploaded so a mission can run on it.

        The file body arrives raw with its name in a header. Only STL/OBJ are
        taken, the name is stripped to a bare filename so nothing lands outside
        the geometry directory, and the surface is parsed on the spot — an
        unreadable file is refused here, not half way through a long mesh."""
        from .geometry import load_surface

        raw_name = self.headers.get("X-Surface-Name", "surface.stl")
        name = Path(raw_name).name.replace("\\", "").strip() or "surface.stl"
        if Path(name).suffix.lower() not in {".stl", ".obj"}:
            self._fail(400, "only .stl and .obj surfaces are accepted")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 200 * 1024 * 1024:
                raise ValueError("empty or oversized upload")
            body = self.rfile.read(length)
        except Exception as exc:
            self._fail(400, f"upload failed: {exc}")
            return

        directory = (HERE.parent / "geometry").resolve()
        directory.mkdir(parents=True, exist_ok=True)
        target = (directory / name).resolve()
        if directory not in target.parents:
            self._fail(400, "invalid surface name")
            return
        target.write_bytes(body)
        try:
            surface = load_surface(target)
        except Exception as exc:
            target.unlink(missing_ok=True)
            self._fail(400, f"that file could not be read as a surface: {exc}")
            return
        self._write_json(200, {
            "name": name,
            "triangles": surface["triangles_total"],
            "bounds": surface["bounds"],
            "url": f"/api/geometry?name={name}",
            "suggested": f"Mesh and solve {name} and report the drag.",
        })

    # ---- Server-Sent Events -------------------------------------------------
    def _stream_events(self, record: MissionRecord, after: int) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        try:
            for event in record.bus.stream(after=after, heartbeat_s=8.0):
                if event is None:
                    frame = b": heartbeat\n\n"
                else:
                    frame = (f"id: {event.sequence}\n"
                             f"event: mission\n"
                             f"data: {json.dumps(event.as_dict())}\n\n").encode()
                self.wfile.write(frame)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return


# --------------------------------------------------------------------------
# Mission dispatch
# --------------------------------------------------------------------------

def _start_mission(request: str, payload: dict):
    """Classify the request, register the mission, and start it on a thread.

    The router decides which workflow the objective is: a geometry study, a
    shape or aircraft optimisation, a deadline trade, an uncertainty question.
    A surface uploaded with the prompt means "run it on this body", so the
    objective can stay plain language with no filename — the surface is threaded
    into the workflow params, and anything not already an optimisation is taken
    through the full geometry study. A request no workflow matches is answered
    honestly rather than run on a guess.
    """
    from .router import (AIRCRAFT_OPTIMIZATION, GEOMETRY_STUDY,
                         SHAPE_OPTIMIZATION, WORKFLOWS, classify)

    route = classify(request)
    surface = str(payload.get("surface") or "").strip()
    if surface and route.intent not in (SHAPE_OPTIMIZATION, AIRCRAFT_OPTIMIZATION):
        route.params["surface"] = surface
        route.intent = GEOMETRY_STUDY
        route.confidence = max(route.confidence, 0.9)

    mission_id = "m-" + secrets.token_hex(6)
    record = MissionRecord(mission_id, request, EventBus(mission_id, _events_path(mission_id)))
    with _missions_lock:
        if len(_missions) >= MAX_MISSIONS:
            oldest = min(_missions.values(), key=lambda item: item.created_at)
            if oldest.state in {"complete", "failed", "incomplete"}:
                _missions.pop(oldest.id, None)
        _missions[mission_id] = record
    _persist(record)

    workflow = WORKFLOWS.get(route.intent)
    if workflow:
        runner, args = _run_workflow, (record, route, workflow)
    else:
        runner, args = _run_mission, (record, payload)
    threading.Thread(target=runner, args=args, daemon=True,
                     name=f"chief-{mission_id}").start()
    return record, route


def _run_workflow(record: MissionRecord, route, workflow: dict) -> None:
    """Import and run a routed workflow, streaming its transcript out live."""
    import importlib

    record.state = "running"
    record.started_at = time.time()
    record.bus.publish("mission.routed", route.as_dict())
    _persist(record)
    try:
        module = importlib.import_module(workflow["module"])
        module.main(request=record.request, params=route.params,
                    emit=record.bus.publish)
        record.state = "complete"
        record.bus.publish("mission.completed", {
            "status": "complete", "intent": route.intent,
            "output": workflow["output"], "reason": "Workflow finished."})
    except Exception as exc:
        record.state = "failed"
        record.error = f"{type(exc).__name__}: {exc}"
        record.bus.publish("mission.failed", {"reason": record.error})
    finally:
        record.finished_at = time.time()
        _persist(record)
        # The learning loop: hand the finished transcript to the debrief so the
        # lab keeps one grounded lesson per mission. Fully defensive and on a
        # daemon thread — completion never waits on it and no failure escapes.
        try:
            from .debrief import debrief_async

            debrief_async(record.id, record.request, record.state,
                          record.bus.snapshot())
        except Exception:
            pass
        record.bus.close()


def _run_mission(record: MissionRecord, payload: dict) -> None:
    """Fallback for a request no workflow matched: the lab says, honestly, what
    it could not read and what it can actually measure — it never invents an
    objective and spends compute on a guess."""
    record.state = "running"
    record.started_at = time.time()
    _persist(record)
    try:
        _explain_unparsed(record, "no workflow matched the request")
    except Exception as exc:
        record.state = "failed"
        record.error = f"{type(exc).__name__}: {exc}"
        record.bus.publish("mission.failed", {"reason": record.error})
    finally:
        record.finished_at = time.time()
        _persist(record)
        record.bus.close()


def _explain_unparsed(record: MissionRecord, reason: str) -> None:
    """Report what could not be turned into an objective and what the lab can
    measure. If the request needs physics the solver cannot model, name the
    domain and refuse plainly rather than pretending to cover it."""
    from .router import LAB_DOMAIN, out_of_scope_domain

    publish = record.bus.publish
    publish("transcript.entry", {
        "role": "SYSTEM", "message": record.request, "citations": [],
        "citations_display": [], "data": {}, "at": time.time()})
    domain = out_of_scope_domain(record.request)
    opening = (
        f"• That needs {domain}, outside what this lab solves. "
        f"• This lab solves {LAB_DOMAIN}. "
        f"• No plan will pretend to cover physics the solver cannot model."
        if domain else
        "• No measurable objective found in that request. "
        "• Nothing expensive runs on a guess. "
        "• Name a quantity to improve or report, and I will start.")
    publish("transcript.entry", {
        "role": "CHIEF ENGINEER", "citations": [], "citations_display": [],
        "data": {}, "at": time.time(), "message": opening})
    publish("transcript.entry", {
        "role": "CHIEF ENGINEER", "citations": [], "citations_display": [],
        "data": {}, "at": time.time(),
        "message": (
            "• On offer: mesh-and-solve a named surface; optimise a shape; trade "
            "fidelity against a deadline. "
            "• Also: quantify and reduce uncertainty; reason about unseen geometry. "
            "• Name the body or the quantity, and I will start.")})
    record.state = "incomplete"
    publish("mission.completed", {
        "status": "incomplete",
        "reason": (f"Out of scope: {domain}. This lab solves {LAB_DOMAIN}." if domain
                   else "The request needs a measurable objective or a named geometry.")})


# --------------------------------------------------------------------------
# Capability registry and status strings
# --------------------------------------------------------------------------

def _registry(mission_id: str = "capabilities") -> SoftwareAdapterRegistry:
    """The adapter registry behind /api/capabilities — the real OpenFOAM solver
    when it is selected, otherwise the synthetic development adapter."""
    if _adapter_name().startswith("openfoam"):
        from .openfoam import openfoam_registry

        workdir = Path(os.environ.get("CHIEF_ENGINEER_WORKDIR", "./chief-engineer-runs"))
        return openfoam_registry(workdir / mission_id / "openfoam")
    latency = float(os.environ.get("CHIEF_SYNTHETIC_LATENCY_S", "0.16"))
    return synthetic_registry(lambda _handle: SyntheticApi(latency_s=latency))


def _adapter_name() -> str:
    return os.environ.get("CHIEF_ADAPTER", "").strip().lower()


def _backend_name() -> str:
    if _adapter_name().startswith("openfoam"):
        from .openfoam import available

        return "openfoam-real-solvers" if available() else "openfoam-synthetic"
    return "synthetic"


def _worker_provider_name() -> str:
    return "local"


def _reasoning_name() -> str:
    configured = all(os.environ.get(key) for key in (
        "CHIEF_REASONING_BASE_URL",
        "CHIEF_REASONING_API_KEY",
        "CHIEF_REASONING_MODEL",
    ))
    return "openai-compatible" if configured else "deterministic-chief"


# --------------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------------

def main() -> None:
    # Transcripts carry engineering notation; a cp1252 console would otherwise
    # abort a beat on its first sigma or degree sign.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    _rehydrate_missions()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Certonomous mission control listening on :{PORT} ({_backend_name()})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
