"""Act C, the battery module, as a DEMO MODE act. NOT REGISTERED, AND WHY.

THIS MODULE REGISTERS NOTHING. Importing it adds no act to the registry, so
the sequencer cannot resolve ``battery-module`` and cannot put this act on a
screen. That is the point of the file, not a gap in it.

WHAT IS WRONG WITH THE RUN THIS ACT WOULD HAVE BEEN FED FROM
------------------------------------------------------------
The screen record this act would have read is a feasibility calculation that
the owner ordered off screen, at a mesh she named unacceptable. The measured
facts, every one read from the record itself and none of them repeated onto a
screen by this file:

* 960 cells for the whole module, 120 per battery cell.
* The cooling channels are NOT resolved as a fluid region, so the record's own
  outlet temperature field reads "NOT DEFINED". A cooling demonstration whose
  coolant is not a fluid cannot show cooling.
* The largest temperature rise anywhere in the module is 0.42 K, and the
  largest spread across the module is 0.11 K. On a chart of a battery pack
  those are flat lines.
* One mesh and one time step, so no discretisation error estimate exists.

The replacement run is not merely unfinished. Its first level RAN and
DIVERGED: return code 134, one fatal, a negative initial temperature at 1.5 s
of a 900 s end time, and outer-loop residuals three to five orders above the
threshold that was fixed before it started. Its two remaining levels are meshed
and have no solve at all.

WHY A SCAFFOLD AND NOT A STUB WITH NUMBERS IN IT
------------------------------------------------
The structure below is complete: the ten stages the contract requires exist,
in order, with the shapes each one must return. What none of them contains is a
value. Every stage refuses, by name, saying which fact it does not have. A
placeholder number here would be indistinguishable from a measured one three
weeks from now, and the whole reason DEMO MODE types its stages is that a
number whose artifact is gone has already reached a screen carrying this lab's
name.

So: :func:`conformance_problems` returns the list the validator produces, which
is deliberately non-empty; :func:`register_when_a_solved_run_backs_it` refuses
to register until that list is empty. When the replacement run lands and is
graded, the person wiring it fills the stages in, runs that function, and the
act registers itself or tells them exactly what is still missing.

THE LIMITATIONS ARE WRITTEN NOW, ON PURPOSE
--------------------------------------------
:data:`LIMITATIONS` is the caveat box this act will carry when it can be shown.
It is written and language-checked at import, before there is any pressure from
a result to soften it. A caveat drafted beside a number it has to survive is a
caveat that gets negotiated.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .demo_mode import (SERVED_GEOMETRY_DIR, Assumption, DemoAct,
                        DemoContractError, Feasibility, GatesAndChecks,
                        Geometry, MeshPlan, Prompt, Restatement, Results,
                        RunRecord, SolveReplay, check_demo_language,
                        validate_act)

REPO = Path(__file__).resolve().parents[2]

#: Where a solved run would have to appear before this act can be shown.
MODULE_RUNS = REPO / "verification" / "runs" / "T-family" / "T25R_MODULE_runs"

#: The surface the control room serves for this act today. It has NOT been
#: measured against any solved case, so this act does not name it as the solved
#: body and does not render it.
CANDIDATE_SURFACE = SERVED_GEOMETRY_DIR / "battery_module_8cell.stl"

#: The plain-English reasons this act is not shown. Screen-safe wording, so a
#: caller may put them in front of a viewer as they stand.
BLOCKED_ON: tuple[str, ...] = (
    "The calculation this act would read resolves no coolant as a fluid, so "
    "it cannot show a cooling system working.",
    "That calculation uses one mesh of 960 cells for the whole module, which "
    "is not enough to resolve a channel.",
    "The largest temperature difference anywhere in it is a tenth of a "
    "kelvin, so every curve it could draw is a flat line.",
    "The replacement calculation stopped with a fatal error a second and a "
    "half in, so there is no completed run behind this act.",
)

#: The caveat box this act will carry once a solved run backs it. Written
#: before the result exists, so no number ever had a chance to soften it.
LIMITATIONS: tuple[str, ...] = (
    "The cooling channels must be resolved as a fluid before any claim is "
    "made about how much heat the coolant carries away.",
    "A single mesh supports no discretisation error bar, so temperatures from "
    "one mesh are shown as computed and not as values with an error bar.",
    "A single time step size supports no statement about time accuracy, so "
    "the settling history is shown as computed.",
    "No rig or cell test data exists for this module, so nothing here is "
    "checked against a measurement.",
)

for _line in BLOCKED_ON + LIMITATIONS:
    check_demo_language(_line, zone="limitations")


def _refuse(missing: str):
    """Refuse one stage, naming the fact it does not have.

    The stage name is NOT repeated here: :func:`validate_act` prefixes every
    problem with the stage it came from, and a doubled name reads as a bug in
    the refusal rather than as the refusal working.
    """
    raise DemoContractError(
        f"this act has no solved run behind it, so it has no {missing}. "
        f"Nothing is substituted. " + BLOCKED_ON[3])


class BatteryModuleAct(DemoAct):
    """The battery module cooling act, structured and deliberately empty.

    Every stage below refuses. The shape of each refusal names the fact it is
    missing, so the person who wires the replacement run is told what to
    supply rather than left to guess from a traceback.
    """

    name = "battery module cooling"

    # -- stage 0 ------------------------------------------------------------
    def run_record(self) -> RunRecord:
        # A RunRecord asserts a COMPLETED run tree and the artifact that shows
        # the completion clauses held. Neither exists.
        _refuse("completed run tree and no completion evidence")

    # -- stages 1 to 3 ------------------------------------------------------
    def prompt(self) -> Prompt:
        """The user's request. This one is safe to state: it is not a result."""
        return Prompt(
            "Battery module cooling: hold every cell in an eight cell module "
            "inside its temperature limit under a discharge pulse, and report "
            "the hottest cell and the spread across the module.")

    def restatement(self) -> Restatement:
        _refuse("cost estimate for a run that has not been sized")

    def assumption(self) -> Assumption:
        _refuse("measured finding to correct the user with")

    # -- stage 4 ------------------------------------------------------------
    def geometry(self) -> Geometry:
        # A Geometry may not be constructed without at least one measured
        # comparison against the solved body, and there is no solved body to
        # compare against. The candidate surface stays unrendered rather than
        # being announced as something it has not been shown to be.
        _refuse("solved body to measure the served surface against")

    # -- stage 5 ------------------------------------------------------------
    def mesh_plan(self) -> MeshPlan:
        _refuse("accepted mesh; the one on record was rejected")

    # -- stage 6 ------------------------------------------------------------
    def feasibility(self) -> Feasibility:
        _refuse("check result to show")

    # -- stage 7 ------------------------------------------------------------
    def solve_replay(self) -> SolveReplay:
        _refuse("solver log from a run that reached its end")

    # -- stage 8 ------------------------------------------------------------
    def gates(self) -> GatesAndChecks:
        _refuse("reader checks over a completed run")

    # -- stage 9 ------------------------------------------------------------
    def results(self) -> Results:
        _refuse("fields, plots or tables that came from a solve")

    # -- the caveat box, ready in advance -----------------------------------
    def limitations_when_it_runs(self) -> Sequence[str]:
        """What the caveat box will say. Written before the result exists."""
        return LIMITATIONS


def conformance_problems() -> list[str]:
    """The validator's list for this act. Non-empty, deliberately."""
    return validate_act(BatteryModuleAct(), check_files=True)


def register_when_a_solved_run_backs_it():
    """Register this act, or refuse and say what is still missing.

    Called by the person wiring the replacement run, never at import. An act
    that registered itself on import would be resolvable by key, and a
    resolvable key is one typo away from a shoot.
    """
    from .demo_mode import register_act

    problems = conformance_problems()
    if problems:
        raise DemoContractError(
            "the battery module act is not registered and will not be shown: "
            + "; ".join(problems))
    return register_act("battery-module", BatteryModuleAct())


#: NOT REGISTERED. The name is bound so a caller that expects the module-level
#: ``ACT`` every other act module exposes gets ``None`` and a readable failure,
#: rather than an AttributeError that looks like a missing file.
ACT = None
