"""What a dispatched run can and cannot answer, said before it runs.

A prompt can ask for more than the run it routes to is able to do. The failure
this module exists to stop happened on camera: a prompt asking for a blown slot
routed to the plain single-body study, the study solved the unblown baseline it
could solve, and the screen reported the mission complete at high confidence
over a request most of which had not been run.

The rule is that the lab says so, at the moment it commits and again at the
end. Nothing here changes what is solved. It changes what is claimed.

The check is deliberately narrow, because a false scope-down on a matched
prompt would be its own failure on camera:

* A capability set is DECLARED per dispatched run. A run whose set is not
  declared here raises nothing -- an undeclared set is an unknown, and an
  unknown must never manufacture a mismatch.
* An ask is detected only from vocabulary that names the physics it needs, not
  from a stray noun.
* Compressibility is deliberately NOT an ask here. The single-body study
  already has its own beat for a speed that would need it, and a second
  sentence saying the same thing is the duplication that beat was trimmed to
  avoid.

Every sentence this module puts on screen is plain English and carries no
internal vocabulary: no route names, no rule numbers, no case ids.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .router import (ADJOINT_OPTIMIZATION, AHMED_BODY, AIRCRAFT_OPTIMIZATION,
                     CRM_WINGBODY, CYLINDER_VORTEX_SHEDDING, DIAMOND_AIRFOIL,
                     GEOMETRY_STUDY, HYPERSONIC_CYLINDER, JET_FLAP_DISPLAY,
                     NASA_HUMP, ONERA_M6,
                     SHAPE_OPTIMIZATION, SUPERSONIC_CONE, SUPERSONIC_WEDGE,
                     THERMAL_DISPLAY, VALVE_STUDY)
# Imported on its own line rather than folded into the tuple above, so this
# addition cannot conflict with another act's addition to the same list. See
# the MERGE NOTE in router.py for the night that cost.
from .router import DOUBLE_MACH_REFLECTION

# Capability tags. One per thing a prompt can ask for that a run either can or
# cannot do. Kept few on purpose: each one is a promise the lab has to keep.
BLOWING = "blowing"
THERMAL = "thermal"
UNSTEADY = "unsteady"
OPTIMISATION = "optimisation"


@dataclass(frozen=True)
class Ask:
    """One thing a prompt asked for, and the plain words for it."""

    tag: str
    #: What the user asked for, as a noun phrase: "a blowing sweep".
    asked: str
    #: What the dispatched run does instead: "solves the unblown baseline only".
    instead: str
    #: What would answer it: "the blown-slot case".
    needs: str


_ASKS: tuple[tuple[Ask, re.Pattern[str]], ...] = (
    (Ask(BLOWING, "a blowing sweep", "solves the unblown baseline only",
         "the blown-slot case"),
     re.compile(r"\b(blow(?:n|ing)|jet[\s-]?flap|slot\s+jet|jet\s+sweep|"
                r"jet\s+momentum|circulation\s+control|"
                r"c[\s_-]?mu|momentum\s+coefficient)\b", re.I)),
    (Ask(THERMAL, "a thermal solve",
         "solves the flow only, with no temperature field",
         "a thermal case"),
     re.compile(r"\b(thermal|temperature|conjugate\s+heat|nusselt|"
                r"heat\s+(?:transfer|flux|load|sink)|"
                r"cooling|coolant|hot[\s-]?spot)\b", re.I)),
    (Ask(UNSTEADY, "a time-varying solution", "solves a single steady state",
         "an unsteady case"),
     re.compile(r"\b(unsteady|transient|time[\s-]?histor(?:y|ies)|"
                r"time[\s-]?accurate|vortex\s+shedding|shedding\s+frequency|"
                r"strouhal|pulsatile)\b", re.I)),
    (Ask(OPTIMISATION, "a design search", "solves one fixed shape",
         "a shape-optimisation case"),
     re.compile(r"\b(optimi[sz]\w*|design\s+sweep|parameter\s+sweep|"
                r"minimi[sz]e|maximi[sz]e|best\s+shape)\b", re.I)),
)


# What each dispatched run declares it can do. An intent absent from this table
# is NOT assumed incapable: it is simply not checked. Adding a row is a promise
# that the run really does cover every tag listed.
CAPABILITIES: dict[str, frozenset[str]] = {
    # The plain single-body chain: one steady incompressible solve of one fixed
    # shape, no jet boundary condition and no energy equation.
    GEOMETRY_STUDY: frozenset(),
    AHMED_BODY: frozenset(),
    NASA_HUMP: frozenset(),
    ONERA_M6: frozenset(),
    CRM_WINGBODY: frozenset(),
    # The searches.
    SHAPE_OPTIMIZATION: frozenset({OPTIMISATION}),
    ADJOINT_OPTIMIZATION: frozenset({OPTIMISATION}),
    AIRCRAFT_OPTIMIZATION: frozenset({OPTIMISATION}),
    # Time-resolved by construction.
    CYLINDER_VORTEX_SHEDDING: frozenset({UNSTEADY}),
    VALVE_STUDY: frozenset({UNSTEADY}),
    # The one route that really does blow. Declaring it here is the promise
    # that a blowing prompt reaching this screen is answered rather than
    # scoped down, and it is the only entry in this table that makes that
    # promise.
    JET_FLAP_DISPLAY: frozenset({BLOWING}),
    # Steady compressible bodies graded against exact theory.
    SUPERSONIC_WEDGE: frozenset(),
    SUPERSONIC_CONE: frozenset(),
    DIAMOND_AIRFOIL: frozenset(),
    HYPERSONIC_CYLINDER: frozenset(),
    # The shock-interaction benchmark is genuinely time resolved, so the
    # UNSTEADY promise is one the runs behind it keep: they are integrated to a
    # stated instant and have no steady state. It carries no other tag, so a
    # prompt that asks this act to optimise a shape or to report a temperature
    # is told so before the screen starts rather than after it finishes.
    DOUBLE_MACH_REFLECTION: frozenset({UNSTEADY}),
    # The thermal display act. It presents two landed conjugate thermal
    # runs and starts no solver, so the honest declaration is the union of
    # what those two runs did: one of them resolves temperature and the
    # other resolves temperature through time. Neither searches a design,
    # and neither has a jet boundary condition, so a prompt asking this act
    # to optimise a duct or to blow a slot is scoped down before it starts.
    #
    # KNOWN COARSENESS, recorded rather than papered over: this table is
    # keyed on the intent and the two acts behind that intent do not have
    # the same capabilities. Act C is a transient; Act A is a set of steady
    # points. UNSTEADY is declared because withholding it would put a FALSE
    # scope-down on Act C -- telling a viewer that a run which solved 900
    # seconds of history 'solves a single steady state' -- and a false
    # scope-down on a matched prompt is the failure this module's own
    # docstring warns against. The cost is that a request for a time
    # history of the motor is not scoped down here; the act names its own
    # missing beats on screen instead, from its per-act not-available
    # table. Splitting the key per act is the repair and belongs to
    # whoever owns this module.
    #
    # RULED 2026-09-01, heat-transfer supervisor: this declaration STANDS as
    # {THERMAL, UNSTEADY} and is not to be narrowed to {THERMAL}. Narrowing
    # would fire a false scope-down on Act C's OWN REGISTERED PROMPT, on
    # camera, telling a viewer that a run which solved 900 seconds of history
    # solves a single steady state. Keeping UNSTEADY leaves the Act A
    # over-claim, which fires only OFF the two registered prompts. A false
    # statement on the filmed path is worse than a latent one off it. The
    # over-claim is no longer SILENT: Act A carries a not_available row in
    # ``workflows.thermal_display`` stating that it holds sixteen separate
    # steady points and no time history at all. Splitting the key per act
    # remains the proper repair and is REFERRED to whoever owns scope.py; it
    # is not withdrawn by this ruling, only deferred past the shoot.
    THERMAL_DISPLAY: frozenset({THERMAL, UNSTEADY}),
}

# L-221/L-222, the same insert-not-replace assert as the routing table carries
# and for the same reason: this is a dict literal, a repeated key is silently
# the last one written, and nothing would raise. Narrow on purpose.
assert CAPABILITIES[DOUBLE_MACH_REFLECTION] == frozenset({UNSTEADY}), (
    "the shock-reflection declaration is not what was written above")
assert CAPABILITIES[JET_FLAP_DISPLAY] == frozenset({BLOWING}), (
    "adding the shock-reflection declaration displaced the jet-flap one")


def unmet_asks(request: str, intent: str) -> tuple[Ask, ...]:
    """The things this prompt asked for that the dispatched run cannot do.

    Empty when the prompt asked for nothing out of reach, and empty when the
    run's capabilities are not declared -- an unknown is never a mismatch.
    """
    if intent not in CAPABILITIES:
        return ()
    text = request or ""
    can = CAPABILITIES[intent]
    return tuple(ask for ask, pattern in _ASKS
                 if ask.tag not in can and pattern.search(text))


def _listed(unmet: tuple[Ask, ...], field: str) -> str:
    """The asks as one plain phrase: "a" / "a and b" / "a, b and c"."""
    items = [getattr(ask, field) for ask in unmet]
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def commit_line(unmet: tuple[Ask, ...]) -> str:
    """What the Chief Engineer says when the run is committed to, before it
    starts. Names the gap first, then what would close it."""
    if not unmet:
        return ""
    asked = _listed(unmet, "asked")
    instead = _listed(unmet, "instead")
    needs = _listed(unmet, "needs")
    return (f"• You asked for {asked}. This run cannot do that: it "
            f"{instead}. "
            f"• {asked[0].upper() + asked[1:]} needs {needs}, which is a "
            f"separate run. "
            f"• What follows is scoped to what this run can answer.")


def conclusion_line(unmet: tuple[Ask, ...]) -> str:
    """What the Chief Engineer says at the end, so the completion is never
    read as covering the whole request."""
    if not unmet:
        return ""
    asked = _listed(unmet, "asked")
    return (f"• Not run: {asked}. "
            f"• This run answered the rest, and the result below covers that "
            f"part alone.")


#: The words the screen shows in place of an unqualified completion. No dash:
#: the register rails ban an em dash in anything user-visible, and this string
#: is as user-visible as text gets.
SCOPED_HEADLINE = "COMPLETE: PART OF THE REQUEST NOT RUN"


def completion(unmet: tuple[Ask, ...]) -> dict[str, object]:
    """The completion fields the interface reads: whether this run answered the
    whole request, and the headline it may show if it did not."""
    if not unmet:
        return {"scoped": False}
    return {
        "scoped": True,
        "headline": SCOPED_HEADLINE,
        "not_run": [ask.asked for ask in unmet],
        "note": conclusion_line(unmet),
    }
