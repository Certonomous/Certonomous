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
from dataclasses import dataclass, field
from typing import Any

SHAPE_OPTIMIZATION = "shape-optimization"
AIRCRAFT_OPTIMIZATION = "aircraft-optimization"
VALVE_STUDY = "valve-study"
TIME_CONSTRAINED = "time-constrained"
UNSEEN_GEOMETRY = "unseen-geometry"
UNCERTAINTY_REDUCTION = "uncertainty-reduction"
GEOMETRY_STUDY = "geometry-study"
GENERAL_MISSION = "general-mission"

# Optimising lift-to-drag for an aircraft against mission requirements is a
# distinct beat from the OpenFOAM shape sweep: it searches a wing design space.
_LIFT_DRAG = re.compile(
    r"\b(l\s*/?\s*d\b|lift[\s-]?to[\s-]?drag|lift[\s/]drag|aerodynamic efficiency)\b", re.I)
_AIRCRAFT = re.compile(
    r"\b(aircraft|airplane|airliner|aeroplane|plane|jet|wing|fuselage|flight)\b", re.I)
_MISSION_REQ = re.compile(
    r"\b(passengers?|pax|seats?|range|take[\s-]?off|landing|cruise|mtow|payload)\b", re.I)

# A pulsatile internal-flow study — the valve opening-angle screen over the
# cardiac cycle. Routes to the multi-point (cycle-decomposition) workflow.
_VALVE = re.compile(
    r"\b(valve|leaflet|cardiac|cycle|pulsatile|systol\w+|orifice)\b", re.I)

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
    r"aircraft|airplane|plane|wing|car|hull|case|simulation)\b",
    re.I)
_SURFACE_FILE = re.compile(r"\b([\w.-]+\.(?:stl|obj))\b", re.I)
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
_REFERENCE_LENGTH = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:m|metre|meter)s?\s*(?:long|length|span|wide)\b", re.I)
_REYNOLDS = re.compile(r"\bre(?:ynolds)?\s*(?:number)?\s*(?:of|=|:)?\s*"
                       r"([\d.]+(?:e[+-]?\d+)?)\b", re.I)

# Geometries the organization has actually solved; anything else is unseen.
KNOWN_GEOMETRIES = ("cylinder", "motorbike", "motorcycle")
CANDIDATE_GEOMETRIES = (
    "airfoil", "aerofoil", "wing", "aircraft", "airplane", "plane", "sphere",
    "car", "vehicle", "turbine", "blade", "propeller", "rotor", "hull", "duct",
    "nozzle", "valve", "heat exchanger", "building", "bridge", "drone", "rocket",
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
    """Return the geometry named in the request and whether we have run it."""
    lowered = text.lower()
    for name in KNOWN_GEOMETRIES:
        if name in lowered:
            return name, True
    for name in CANDIDATE_GEOMETRIES:
        if name in lowered:
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
    # --- pulsatile internal-flow valve screen (multi-point cycle decomposition) ---
    if _VALVE.search(text):
        add(VALVE_STUDY, 1.7,
            "screens a pulsatile internal flow by decomposing the cycle into phase points")
    # --- aircraft L/D optimization against mission requirements ---
    if _LIFT_DRAG.search(text) and (_AIRCRAFT.search(text) or _MISSION_REQ.search(text)):
        add(AIRCRAFT_OPTIMIZATION, 1.6,
            "optimises lift-to-drag for an aircraft against mission requirements")
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
    if solver_setup:
        params["solver_setup"] = solver_setup.group(0)
    if geometry:
        params["geometry"] = geometry
        params["geometry_known"] = known
    if deadline:
        params["deadline_minutes"] = deadline
    if reynolds:
        params["reynolds"] = reynolds
    if length_match:
        params["reference_length"] = float(length_match.group(1))

    rationale = {
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
            "mesh it, solve it, and report the forces with their envelope. This is "
            "the expensive path — meshing and solving a real body takes minutes, "
            "not seconds — so I will say what each stage costs as it runs."),
        UNCERTAINTY_REDUCTION: (
            "This is a question about confidence itself. I will quantify the "
            "current envelope, decide whether it is reducible, and spend "
            "samples until only irreducible uncertainty remains."),
    }[intent]

    return Route(intent, confidence,
                 f"{rationale} Basis: {'; '.join(reasons)}.",
                 tuple(reasons), params)


# Which module and entry point serves each route.
WORKFLOWS: dict[str, dict[str, Any]] = {
    GEOMETRY_STUDY: {"module": "workflows.geometry_study",
                     "output": "geometry-study"},
    SHAPE_OPTIMIZATION: {"module": "workflows.shape_optimization",
                         "output": "shape-optimization"},
    VALVE_STUDY: {"module": "workflows.valve_study", "output": "valve-study"},
    AIRCRAFT_OPTIMIZATION: {"module": "workflows.aircraft_optimization",
                            "output": "aircraft-optimization"},
    TIME_CONSTRAINED: {"module": "workflows.time_constrained",
                       "output": "time-constrained"},
    UNSEEN_GEOMETRY: {"module": "workflows.unseen_geometry",
                      "output": "unseen-geometry"},
    UNCERTAINTY_REDUCTION: {"module": "workflows.uncertainty_reduction",
                            "output": "uncertainty-reduction"},
}
