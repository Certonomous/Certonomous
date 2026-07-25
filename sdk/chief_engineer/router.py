"""Read an engineering request and decide how the organization should answer it.

The Chief Engineer does not run a fixed script: it reads what was asked, states
its interpretation on the record, and routes to the workflow that fits.  Five
routes exist today:

``shape-optimization``
    An objective over a design space with constraints — explore, select, and
    report the winner with its uncertainty.
``time-constrained``
    A deadline is stated. Fidelity must be traded for speed, which requires a
    Chief Researcher ruling on whether a closure model may cover the gap.
``unseen-geometry``
    The request names something outside case memory. Retrieve the nearest real
    cases, separate what transfers from what does not, and refuse to invent a
    magnitude.
``uncertainty-reduction``
    The request is about confidence itself — how sure are we, tighten the
    error bars, how many samples.
``geometry-study``
    A surface is named, or a body is to be taken through the whole chain:
    intake, surface check, meshing, solving, and a reported force with its
    envelope. The expensive path, measured in minutes rather than seconds.

Routing is keyword-and-pattern based and fully inspectable: every decision
carries the evidence that produced it, so the interpretation can be argued
with rather than guessed at.  When nothing matches strongly the request falls
through to the general capability-driven mission planner.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SHAPE_OPTIMIZATION = "shape-optimization"
AIRCRAFT_OPTIMIZATION = "aircraft-optimization"
VALVE_STUDY = "valve-study"
TIME_CONSTRAINED = "time-constrained"
UNSEEN_GEOMETRY = "unseen-geometry"
UNCERTAINTY_REDUCTION = "uncertainty-reduction"
GEOMETRY_STUDY = "geometry-study"
RACE_COMPARISON = "race-comparison"
GENERAL_MISSION = "general-mission"

# Optimising lift-to-drag for an aircraft against mission requirements is a
# distinct beat from the OpenFOAM shape sweep: it searches a wing design space.
_LIFT_DRAG = re.compile(
    r"\b(l\s*/?\s*d\b|lift[\s-]?to[\s-]?drag|lift[\s/-]+drag|aerodynamic efficiency)\b", re.I)
_AIRCRAFT = re.compile(
    r"\b(aircraft|airplane|airliner|aeroplane|plane|jet|wing|fuselage|flight)\b", re.I)
_MISSION_REQ = re.compile(
    r"\b(passengers?|pax|seats?|range|take[\s-]?off|landing|cruise|mtow|payload)\b", re.I)

# A pulsatile internal-flow study — the valve opening-angle screen over the
# cardiac cycle. Routes to the multi-point (cycle-decomposition) workflow.
_VALVE = re.compile(
    r"\b(valve|leaflet|cardiac|pulsatile|systol\w+|orifice)\b", re.I)

# A head-to-head speed comparison — a full Monte-Carlo sweep against a
# reduced-order path on the same objective, both timed. The "race" act: it
# runs the two methods concurrently on screen and reports the measured speedup.
# A race is framed by a contest word (race / head-to-head / versus) and is
# reinforced when the two methods it pits are named (Monte-Carlo vs reduced
# order). Either signal alone is weak; together they are unambiguous.
_RACE_FRAME = re.compile(
    r"\b(race|head[\s-]?to[\s-]?head|versus|vs\.?|face[\s-]?off|"
    r"against\s+the\s+reduced[\s-]?order|both\s+timed|measured\s+speed[\s-]?up)\b",
    re.I)
_RACE_METHODS = re.compile(
    r"\b(monte[\s-]?carlo|reduced[\s-]?order|surrogate|"
    r"response\s+surface|brute[\s-]?force)\b", re.I)

_OPTIMIZE = re.compile(
    r"\b(minimi[sz]e|maximi[sz]e|optimi[sz]e|reduce|lower|improve|increase|"
    r"best|optimal)\b", re.I)
_SHAPE_NOUNS = re.compile(
    r"\b(shape|geometry|design|diameter|chord|span|thickness|profile|body)\b", re.I)
_DEADLINE = re.compile(
    r"\b(deadline|urgent|asap|quickly|fast|hurry|rush|by (?:tomorrow|tonight|"
    r"end of day|eod)|within|in)\s*(\d+)?\s*(minute|min|hour|hr|day)s?\b", re.I)
_DEADLINE_SOFT = re.compile(
    r"\b(deadline|urgent|asap|as soon as possible|quickly|right away|"
    r"no time|short on time|in a hurry)\b", re.I)
_UNSEEN = re.compile(
    r"\b(never (?:run|seen|done)|unfamiliar|unseen|new geometry|"
    r"haven'?t (?:run|seen)|not in (?:our )?(?:memory|records|library)|"
    r"first time|no (?:data|experience|history))\b", re.I)
_GEOMETRY_RUN = re.compile(
    r"\b(run|simulate|solve|mesh|analyse|analyze|study)\b[^.]{0,40}?"
    r"\b(geometry|stl|obj|surface|model|body|bike|motorbike|motorcycle|"
    r"aircraft|airplane|plane|wing|sail|car|hull|case|simulation)\b",
    re.I)
_SURFACE_FILE = re.compile(r"\b([\w.-]+\.(?:stl|obj))\b", re.I)
# The owner asking the lab to leave compute headroom on the box ("don't use all
# my workers", "I'm running locally") — honored inside the routed mission, on
# the record, not routed to a different workflow.
_HOLD_WORKERS = re.compile(
    r"\b(?:don'?t|do not|not)\s+(?:use\s+)?(?:all|every)\b[^.?!]{0,40}\bworkers?\b|"
    r"\bhold\s+(?:some\s+)?workers?\s+back\b|\bleave\s+(?:some\s+)?headroom\b|"
    r"\bhalf\s+(?:the\s+|my\s+)?workers?\b", re.I)

# --- named-body resolution -------------------------------------------------
# When a prompt NAMES a body the lab has staged ("the NACA 4412 finite-wing
# geometry") but no file is uploaded and no *.stl/*.obj literal is typed, the
# geometry study must solve the body that was ASKED FOR, not silently fall back
# to the default motorBike. This table maps prompt vocabulary to the staged
# surface; ``classify`` sets ``params["surface"]`` from it so the decision is
# visible on the route panel (router-level, not buried in the workflow).
#
# Each entry is (pattern, staged filename, curriculum subdir to stage from if
# the surface is not present in sdk/geometry). Ordered most-specific first.
_GEOMETRY_DIR = Path(__file__).resolve().parents[1] / "geometry"
_CURRICULUM_DIR = Path(__file__).resolve().parents[2] / "models" / "curriculum"
_NAMED_BODIES: tuple[tuple["re.Pattern[str]", str, str | None], ...] = (
    (re.compile(r"\bnaca[\s-]*4412\b|\b4412\b", re.I),
     "naca4412_wing.stl", "naca4412_wing"),
    (re.compile(r"\bnaca[\s-]*0012\b|\b0012\b", re.I),
     "naca0012_wing.stl", "naca0012_wing"),
    (re.compile(r"\bnaca[\s-]*0015\b|\b0015\b", re.I),
     "naca0015_sail.stl", "naca0015_sail"),
    (re.compile(r"\b(?:b[\s-]?52|stratofortress)\b", re.I), "b52.stl", None),
    (re.compile(r"\b(?:motorcycle|motorbike|motor[\s-]?bike)\b", re.I),
     "motorBike.obj", None),
)


def _stage_body(filename: str, curriculum_subdir: str | None) -> bool:
    """Ensure the named surface is present in sdk/geometry; stage it if not.

    Returns whether a usable surface file now exists. A body named in a prompt
    but absent from both the staging dir and the curriculum is NOT staged, and
    the caller must say so honestly rather than solve the default body.
    """
    dest = _GEOMETRY_DIR / filename
    if dest.exists():
        return True
    if curriculum_subdir:
        src = _CURRICULUM_DIR / curriculum_subdir / filename
        if src.exists():
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src, dest)
                return True
            except OSError:
                return False
    return dest.exists()


def resolve_named_body(text: str) -> tuple[str | None, str | None, bool]:
    """Map body vocabulary in a prompt to a staged surface filename.

    Returns ``(filename, matched_phrase, available)``. ``available`` is False
    when the body is recognized but no staged surface backs it, so the caller
    can report the gap honestly instead of silently solving the default body.
    Returns ``(None, None, False)`` when no known body is named.
    """
    for pattern, filename, subdir in _NAMED_BODIES:
        match = pattern.search(text or "")
        if match:
            return filename, match.group(0), _stage_body(filename, subdir)
    return None, None, False

# Naming a turbulence model or solver is an instruction to run a case.
_SOLVER_SETUP = re.compile(
    r"\b(k[\s-]?omega|k[\s-]?epsilon|komega|kepsilon|k[\s-]?sst|sst|rans|les|des|"
    r"spalart|laminar|simplefoam|pimplefoam|potentialfoam|turbulence model)\b", re.I)
_UNCERTAINTY = re.compile(
    r"\b(uncertain(?:ty|ties)?|confiden(?:ce|t)|error bar|how sure|how "
    r"reliable|tighten|converge[d]? enough|sample[s]?|noisy|trust)\b", re.I)

# What this lab actually solves, and the physics it does not. The out-of-scope
# map names each domain for an honest refusal and fires on the phenomenon, not on
# incidental words ("temperature" alone is a fluid property and stays in-domain;
# "heat transfer" is not). Ported from the objective-compiler triage so the
# demo's front door gives a specific "out of scope" answer, not a generic one.
LAB_DOMAIN = ("incompressible external aerodynamics — forces and coefficients "
              "via steady or unsteady RANS")
_OUT_OF_SCOPE_DOMAINS: dict[str, "re.Pattern[str]"] = {
    "melting or phase change": re.compile(
        r"\b(melt(?:s|ing)?|solidif\w+|freez\w+|phase[\s-]change|ablat\w+|"
        r"vaporis\w+|vaporiz\w+)\b", re.I),
    "combustion or fire": re.compile(
        r"\b(combustion|reacting\s+flow|flame|fire|burn(?:s|ing|t)?|ignition|"
        r"detonation|deflagration|species\s+transport|chemical\s+react)\w*", re.I),
    "heat transfer or thermal analysis": re.compile(
        r"\b(heat\s+transfer|heat\s+flux|conjugate\s+heat|thermal\s+(?:analysis|"
        r"management|load|field|stress)|conduction|convective\s+heat|radiativ\w*|"
        r"boiling|nusselt)\b", re.I),
    "structural or FEA": re.compile(
        r"\b(FEA|finite[\s-]element|structural\s+(?:analysis|stress|load|"
        r"integrity)|fatigue|modal\s+analysis|deflection|buckling)\b", re.I),
    "electromagnetics": re.compile(
        r"\b(electromagnetic|magnetic\s+field|MHD|magnetohydrodynamic|plasma|"
        r"antenna|electrostatic)\w*", re.I),
    "free-surface or multiphase flow": re.compile(
        r"\b(free[\s-]surface|multi-?phase|two-?phase|cavitation|sloshing|VOF|"
        r"breaking\s+wave|droplet|spray|liquid\s+film)\b", re.I),
    "compressible or supersonic flow": re.compile(
        r"\b(supersonic|hypersonic|transonic|shock\s*wave|compressible|mach)\b", re.I),
}


def out_of_scope_domain(text: str) -> str | None:
    """Name the physics domain a request needs, if it is outside this lab."""
    for name, pattern in _OUT_OF_SCOPE_DOMAINS.items():
        if pattern.search(text or ""):
            return name
    return None
_NUMBER_UNIT = re.compile(r"(\d+(?:\.\d+)?)\s*(minute|min|hour|hr|day)s?\b", re.I)
# A stated reference length, either way round: "1.2 m long / 1.2 m span" or
# "chord 1.2 m / span of 1.2 m / reference length 1.2 m". The chord of a wing
# IS its reference length, so a stated chord flows to the geometry study's
# scale basis the same way a stated length does.
_REFERENCE_LENGTH = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:m|metre|meter)s?\s*(?:long|length|span|wide)\b|"
    r"\b(?:chord|span|reference\s+length)\s*(?:of|=|:)?\s*"
    r"(\d+(?:\.\d+)?)\s*(?:m|metre|meter)s?\b", re.I)
_REYNOLDS = re.compile(r"\bre(?:ynolds)?\s*(?:number)?\s*(?:of|=|:)?\s*"
                       r"([\d.]+(?:e[+-]?\d+)?)\b", re.I)

# Geometries the organization has actually solved; anything else is unseen.
KNOWN_GEOMETRIES = ("cylinder", "motorbike", "motorcycle")
# "valve" is absent deliberately: the dedicated valve-study pattern owns that
# vocabulary, and double-counting it as unseen geometry only muddies routing.
CANDIDATE_GEOMETRIES = (
    "airfoil", "aerofoil", "wing", "aircraft", "airplane", "plane", "sphere",
    "car", "vehicle", "turbine", "blade", "propeller", "rotor", "hull", "duct",
    "nozzle", "heat exchanger", "building", "bridge", "drone", "rocket",
)


@dataclass
class Route:
    intent: str
    confidence: float
    rationale: str
    evidence: tuple[str, ...] = ()
    params: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"intent": self.intent, "confidence": self.confidence,
                "rationale": self.rationale, "evidence": list(self.evidence),
                "params": dict(self.params)}


def _deadline_minutes(text: str) -> float | None:
    match = _NUMBER_UNIT.search(text)
    if not match:
        return None
    value, unit = float(match.group(1)), match.group(2).lower()
    if unit.startswith("min"):
        return value
    if unit.startswith(("hour", "hr")):
        return value * 60
    return value * 60 * 24


def _mentioned_geometry(text: str) -> tuple[str | None, bool]:
    """Return the geometry named in the request and whether we have run it.

    Whole-word matching only — "car" must not fire inside "cardiac"."""
    lowered = text.lower()
    for name in KNOWN_GEOMETRIES:
        if re.search(rf"\b{re.escape(name)}\b", lowered):
            return name, True
    for name in CANDIDATE_GEOMETRIES:
        if re.search(rf"\b{re.escape(name)}\b", lowered):
            return name, False
    return None, False


def classify(request: str) -> Route:
    """Interpret an engineering request; never raises, always explains."""
    text = (request or "").strip()
    if not text:
        return Route(GENERAL_MISSION, 0.0, "Empty request.", (), {})

    geometry, known = _mentioned_geometry(text)
    surface_match = _SURFACE_FILE.search(text)
    surface_file = surface_match.group(1) if surface_match else None
    # A named body (no file uploaded, no literal *.stl typed) resolves to its
    # staged surface so the study solves what was asked for, not the default.
    named_surface, named_phrase, named_available = (None, None, False)
    if not surface_file:
        named_surface, named_phrase, named_available = resolve_named_body(text)
    deadline = _deadline_minutes(text)
    length_match = _REFERENCE_LENGTH.search(text)
    reynolds_match = _REYNOLDS.search(text)
    reynolds = float(reynolds_match.group(1)) if reynolds_match else None

    scores: dict[str, float] = {}
    evidence: dict[str, list[str]] = {}

    def add(intent: str, weight: float, why: str) -> None:
        scores[intent] = scores.get(intent, 0.0) + weight
        evidence.setdefault(intent, []).append(why)

    # --- a named surface, or an explicit instruction to run one ---
    if surface_file:
        add(GEOMETRY_STUDY, 1.2, f"names the surface {surface_file!r}")
    elif named_surface and named_available:
        add(GEOMETRY_STUDY, 1.2,
            f"names the staged body {named_phrase!r} -> {named_surface}")
    elif named_phrase and not named_available:
        add(GEOMETRY_STUDY, 0.8,
            f"names {named_phrase!r}, which is not in the staged catalog")
    if _GEOMETRY_RUN.search(text):
        add(GEOMETRY_STUDY, 1.4, "asks for a geometry to be meshed and solved")
    solver_setup = _SOLVER_SETUP.search(text)
    if solver_setup:
        add(GEOMETRY_STUDY, 1.0,
            f"names a solver setup ({solver_setup.group(0)}), which is a request to "
            f"run a case rather than a question about one")

    # --- deadline / fidelity trade ---
    if _DEADLINE.search(text) or _DEADLINE_SOFT.search(text):
        detail = (f"a {deadline:.0f}-minute budget" if deadline
                  else "explicit time pressure")
        add(TIME_CONSTRAINED, 1.0, f"states {detail}")
    # --- geometry we have never solved ---
    if _UNSEEN.search(text):
        add(UNSEEN_GEOMETRY, 1.0, "says this case is outside our experience")
    if geometry and not known:
        add(UNSEEN_GEOMETRY, 0.7,
            f"names {geometry!r}, which is absent from case memory")
    # --- head-to-head speed race: full Monte-Carlo vs reduced-order, both timed ---
    race_frame = _RACE_FRAME.search(text)
    race_methods = _RACE_METHODS.search(text)
    if race_frame:
        add(RACE_COMPARISON, 1.9,
            "frames a head-to-head comparison of two methods on one objective")
        if race_methods:
            add(RACE_COMPARISON, 0.6,
                "names a full sweep against a reduced-order path")
    # --- pulsatile internal-flow valve screen (multi-point cycle decomposition) ---
    if _VALVE.search(text):
        add(VALVE_STUDY, 1.7,
            "screens a pulsatile internal flow by decomposing the cycle into phase points")
    # --- aircraft L/D optimization against mission requirements ---
    hold_workers = bool(_HOLD_WORKERS.search(text))
    if _LIFT_DRAG.search(text) and (_AIRCRAFT.search(text) or _MISSION_REQ.search(text)):
        add(AIRCRAFT_OPTIMIZATION, 1.6,
            "optimises lift-to-drag for an aircraft against mission requirements")
        # Live operating constraints ride INSIDE the aircraft mission — the
        # chief honors a time budget and a compute-headroom ask on the record
        # rather than handing the request to a different workflow.
        if deadline:
            add(AIRCRAFT_OPTIMIZATION, 0.3,
                f"states a {deadline:.0f}-minute budget the mission will honor")
        if hold_workers:
            add(AIRCRAFT_OPTIMIZATION, 0.3,
                "asks the lab to hold workers back on this box")
    # --- optimization ---
    if _OPTIMIZE.search(text):
        add(SHAPE_OPTIMIZATION, 0.7, "asks for an objective to be improved")
    if _SHAPE_NOUNS.search(text):
        add(SHAPE_OPTIMIZATION, 0.5, "refers to a shape or design variable")
    # --- uncertainty ---
    if _UNCERTAINTY.search(text):
        add(UNCERTAINTY_REDUCTION, 0.8, "asks about confidence in the answer")

    if not scores:
        return Route(
            GENERAL_MISSION, 0.3,
            "No dominant pattern — handing this to the capability-driven "
            "planner, which will decompose it against the connected adapters.",
            (), {"request": text})

    intent = max(scores, key=lambda key: scores[key])
    total = sum(scores.values()) or 1.0
    confidence = round(min(0.99, scores[intent] / total), 2)
    reasons = evidence[intent]

    params: dict[str, Any] = {"request": text}
    if surface_file:
        params["surface"] = surface_file
    elif named_surface and named_available:
        # Router-level surface: the route panel reflects the resolved body.
        params["surface"] = named_surface
    elif named_phrase and not named_available:
        # Named but never staged: carried so the workflow says so honestly
        # instead of silently solving the default body.
        params["surface_unavailable"] = named_phrase
    if solver_setup:
        params["solver_setup"] = solver_setup.group(0)
    if geometry:
        params["geometry"] = geometry
        params["geometry_known"] = known
    if deadline:
        params["deadline_minutes"] = deadline
    if hold_workers:
        params["hold_workers_back"] = True
    if reynolds:
        params["reynolds"] = reynolds
    if length_match:
        params["reference_length"] = float(
            length_match.group(1) or length_match.group(2))

    rationale = {
        RACE_COMPARISON: (
            "Reading this as a head-to-head speed race: the same objective and "
            "the same tolerance answered two ways — a full Monte-Carlo sweep "
            "against a reduced-order path — with every evaluation on both sides "
            "run through the selected solver and both wall clocks measured live. I will run the two "
            "lanes concurrently, show the polar forming on each, and report the "
            "agreement and the measured speedup."),
        VALVE_STUDY: (
            "Reading this as a pulsatile internal-flow screen. The cycle is "
            "periodic, so I will decompose it into a few steady phase points, "
            "solve each, and cycle-weight the result — after the Chief Researcher "
            "rules the decomposition admissible for this Womersley number."),
        AIRCRAFT_OPTIMIZATION: (
            "Reading this as an aircraft lift-to-drag optimisation against mission "
            "requirements. I will fix the requirements, search a wing design space "
            "for the highest cruise L/D that meets them all, and show the "
            "infeasible designs alongside the winner."),
        SHAPE_OPTIMIZATION: (
            "Reading this as a design-space search: an objective to improve "
            "under constraints. I will audit compute, explore real designs, and "
            "report the winner with its uncertainty envelope."),
        TIME_CONSTRAINED: (
            "Reading this as a fidelity-versus-deadline trade. A coarser mesh "
            "than I would choose is implied, so the Chief Researcher has to "
            "rule on whether a validated closure can cover the gap before any "
            "number is reported."),
        UNSEEN_GEOMETRY: (
            "This falls outside case memory. Rather than guess, the chiefs will "
            "retrieve the nearest cases we have actually solved and separate "
            "what transfers from what does not."),
        GEOMETRY_STUDY: (
            "Reading this as a full geometry study: take the surface in, check it, "
            "mesh it, solve it, and report the forces with their envelope. "
            "• Meshing and solving a full body takes minutes, not seconds. "
            "• Planning the delegation around the available workers, the body's "
            "complexity, and the quality gates."),
        UNCERTAINTY_REDUCTION: (
            "This is a question about confidence itself. I will quantify the "
            "current envelope, decide whether it is reducible, and spend "
            "samples until only irreducible uncertainty remains."),
    }[intent]

    # The rationale stands alone on the interpretation panel; the raw evidence
    # clauses stay machine-readable in ``evidence`` rather than being appended
    # as a "Basis:" sentence that restates the rationale in router shorthand.
    return Route(intent, confidence, rationale, tuple(reasons), params)


# Intents that keep their route when a surface is uploaded with the prompt:
# each of these acts accepts the surface honestly on its own terms (starting
# geometry, raced wing, reference body) rather than being rerouted.
_SURFACE_KEEPS_ROUTE = (AIRCRAFT_OPTIMIZATION, RACE_COMPARISON, VALVE_STUDY,
                        SHAPE_OPTIMIZATION)


def apply_surface(route: Route, surface: str | None) -> Route:
    """Fold an uploaded surface into an already-classified route.

    An aircraft optimisation keeps its route and takes the surface as the
    starting geometry for the search; a race comparison keeps its route and
    races on the uploaded wing; a valve study keeps its route and holds the
    surface as the reference body while the parametric orifice family runs
    the screen; a shape optimisation likewise keeps its route with the
    surface on file. Anything else with an uploaded surface means "run it on
    this body" and becomes a full geometry study.
    """
    surface = (surface or "").strip()
    if not surface:
        return route
    route.params["surface"] = surface
    if route.intent not in _SURFACE_KEEPS_ROUTE:
        route.intent = GEOMETRY_STUDY
        route.confidence = max(route.confidence, 0.9)
    return route


# Which module and entry point serves each route.
WORKFLOWS: dict[str, dict[str, Any]] = {
    GEOMETRY_STUDY: {"module": "workflows.geometry_study",
                     "output": "geometry-study"},
    SHAPE_OPTIMIZATION: {"module": "workflows.shape_optimization",
                         "output": "shape-optimization"},
    VALVE_STUDY: {"module": "workflows.valve_study", "output": "valve-study"},
    RACE_COMPARISON: {"module": "workflows.race_study",
                      "output": "race-comparison"},
    AIRCRAFT_OPTIMIZATION: {"module": "workflows.aircraft_optimization",
                            "output": "aircraft-optimization"},
    TIME_CONSTRAINED: {"module": "workflows.time_constrained",
                       "output": "time-constrained"},
    UNSEEN_GEOMETRY: {"module": "workflows.unseen_geometry",
                      "output": "unseen-geometry"},
    UNCERTAINTY_REDUCTION: {"module": "workflows.uncertainty_reduction",
                            "output": "uncertainty-reduction"},
}
