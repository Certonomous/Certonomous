#!/usr/bin/env python3
"""The polar act's frame captions, and the guard that keeps them honest.

WHY THIS FILE EXISTS. The polar act's strongest screen is the rendered velocity
field at alpha = 18 degrees -- the angle the platform REFUSED -- because its
wake carries visible disorder that a viewer reads without arithmetic. That makes
it better staging than the negative drag coefficient, which needs a viewer who
already knows drag cannot be negative and which the COMPRESSIBLE arm does not
even offer.

AND IT OPENS A HOLE THAT NOTHING IN THIS LAB CURRENTLY WATCHES.

`aoa_read.G-STALL` is the guard that stops us binding a stall word to a numeric
angle. It is fail-closed, it has two-sided controls (C7/C7b), and it PASSED on
both arms. But it reads STRINGS, and it requires the stall word and the angle to
sit in ONE string within sixty characters of each other. MEASURED, not argued:

    "the stall angle is 13.0 deg"                        FIRES   (control C7)
    "At 18 deg the flow stalls over the upper surface."  FIRES
    "The flow separates over the upper surface here."    DOES NOT FIRE
    "The wake is shedding behind the section."           DOES NOT FIRE

On a rendered frame the ANGLE lives in the frame label and the CLAIM lives in
the caption. Two channels. The regex cannot see them together, so a caption may
assert a mechanism the run never measured and every existing instrument stays
green. *No gate reads prose* was already this family's hazard; **no gate reads
pictures either, and this is the first time a picture has been put where an
argument used to be.**

WHAT WE MAY AND MAY NOT SAY ABOUT THAT FRAME. Oscillatory striping in a
non-converged steady RANS field can be numerical oscillation, an unconverged
transient, or a real unsteady structure the steady formulation cannot hold. **We
do not know which. We have not measured it. The act may not say.** The frame is
a CORRELATE of a refused state, not a MECHANISM for it: the refusal rests on the
solver's own residual verdict and on nothing in the picture.

    python3 cases/dafoam/ladder-a/A1/polar_frame_captions.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE / "feasibility_aoa_polar"))
sys.path.insert(0, str(REPO / "sdk"))

from aoa_read import STALL_CLAIM  # noqa: E402  the existing, narrower guard

# ---------------------------------------------------------------------------
# THE MECHANISM GUARD: what a caption may not assert about a picture.
#
# NARROW ON PURPOSE, on the same reasoning as the tense rule's present-run
# narration list. A caption saying "velocity magnitude" or "the upper surface"
# is describing what is drawn and stays. What is forbidden is naming a FLOW
# MECHANISM as something the viewer can see, because for a non-converged
# iterate we have not established that any of it is physical.
#
# Note this deliberately catches words `G-STALL` does not carry at all
# (`separates`, `shedding`, `recirculation`, `reattach`) and does NOT require an
# angle anywhere, because the angle is in the other channel.
MECHANISM = re.compile(
    r"\b(separat(?:es|ing|ed|ion)|shed(?:s|ding)?|stall(?:s|ed|ing)?|"
    r"recirculat(?:es|ing|ion)|reattach(?:es|ing|ment)?|vort(?:ex|ices)|"
    # `turbulent` ALONE, not `turbulent wake`: the first version carried the
    # two-word form and "The wake is turbulent here." walked straight through
    # it -- caught by the plant, not by reading. A phrase pattern is only as
    # good as the word order its author imagined. `turbulent` is also safe to
    # take bare, because the thing it would falsely catch is "turbulence
    # model", and "turbulence" is a different word.
    r"transition(?:s|ing)?|boundary layer|turbulent|flow is unsteady|"
    r"unsteady flow|breaks down|breakdown)\b", re.I)

#: A caption may not present a refused iterate as a flow result either.
RESULT_VOICE = re.compile(
    r"\b(shows the flow|you can see the|this is the flow|the flow is|"
    r"demonstrat(?:es|ing)|prov(?:es|ing)|because the flow)\b", re.I)

# ---------------------------------------------------------------------------
#: THE APPROVED CAPTIONS. Every one describes WHAT IS DRAWN and WHERE IT CAME
#: FROM, and none explains it.
CAPTIONS: dict[str, str] = {
    "polar_field_alpha18_not_converged": (
        "Velocity magnitude on the last iterate at the angle the platform "
        "declined to report. The solver did not meet its own residual "
        "tolerance here, so no number is read from this state."),
    "section_grid": (
        "The grid every angle in the sweep is solved on: 4,032 cells, counted "
        "from the mesh rather than quoted."),
    "section_grid_leading_edge": (
        "The same grid at the leading edge, all cells in view."),
}

#: THE REFUSAL CAPTION IS THE ACT'S OWN SENTENCE and it states the ground of the
#: refusal, which is the residual verdict and not the picture.
REFUSAL_LINE = (
    "Ten of the nineteen angles did not meet the residual tolerance, so the "
    "platform reports them as not converged rather than as physics. The "
    "wall-resolved study that settles whether the boundary is physical is "
    "running now.")

# ---------------------------------------------------------------------------
#: MUST BE REJECTED. Each is a mechanism claim a viewer might think the picture
#: licenses, and EVERY ONE OF THEM PASSES `G-STALL` UNTOUCHED.
FORBIDDEN_PLANTS = [
    "The flow separates over the upper surface here.",
    "The wake is shedding behind the section.",
    "You can see the boundary layer separating.",
    "The flow is unsteady at this angle.",
    "Large vortices form above the section.",
    "This shows the flow breaking down past the leading edge.",
    "The recirculation region is visible above the chord.",
    "The wake is turbulent here.",
]

#: MUST BE ACCEPTED. Descriptive, provenance-carrying, mechanism-free. Without
#: this arm a guard that rejected everything would score full marks.
ALLOWED_PLANTS = [
    "Velocity magnitude on the last iterate at a refused angle.",
    "The grid the section is solved on, 4,032 cells.",
    "Colour is velocity magnitude in metres per second.",
    "The same grid at the leading edge, all cells in view.",
]


def caption_hits(text: str) -> list[str]:
    """Every reason this caption may not go on a frame."""
    out = []
    for m in MECHANISM.finditer(text):
        out.append(f"mechanism claim: {m.group(0)!r}")
    for m in RESULT_VOICE.finditer(text):
        out.append(f"presented as a flow result: {m.group(0)!r}")
    if STALL_CLAIM.search(text):
        out.append("G-STALL: a stall word bound to a numeric angle")
    return out


def check() -> int:
    blind: list[str] = []
    n = 0

    # ---- the two-sided control on the caption guard ------------------------
    for p in FORBIDDEN_PLANTS:
        n += 1
        if not caption_hits(p):
            blind.append(f"forbidden caption NOT rejected: {p!r}")
    for p in ALLOWED_PLANTS:
        n += 1
        if caption_hits(p):
            blind.append(f"honest caption wrongly rejected: {p!r} "
                         f"-> {caption_hits(p)}")

    # ---- THE GAP, MEASURED AND ASSERTED RATHER THAN DESCRIBED --------------
    # This arm exists so the claim in the docstring cannot rot: if a successor
    # widens G-STALL to cover these, this arm goes red and the docstring gets
    # corrected instead of quietly becoming false.
    evade = [p for p in FORBIDDEN_PLANTS if not STALL_CLAIM.search(p)]
    n += 1
    if len(evade) != len(FORBIDDEN_PLANTS):
        blind.append(
            "the premise of this file has changed: G-STALL now catches "
            f"{len(FORBIDDEN_PLANTS) - len(evade)} of the forbidden captions. "
            "Rewrite the docstring rather than leaving it stale.")
    n += 1
    if not STALL_CLAIM.search("the stall angle is 13.0 deg"):
        blind.append("G-STALL no longer fires on its own control C7")

    # ---- the published captions themselves ---------------------------------
    for tag, text in list(CAPTIONS.items()) + [("refusal line", REFUSAL_LINE)]:
        n += 1
        hits = caption_hits(text)
        if hits:
            blind.append(f"published caption {tag!r}: {hits}")

    # ---- and through the act's own camera-string checker --------------------
    try:
        from workflows.demo_mode import check_demo_language
        for tag, text in list(CAPTIONS.items()) + [("refusal", REFUSAL_LINE)]:
            n += 1
            try:
                check_demo_language(text, zone="screen")
            except Exception as exc:                       # noqa: BLE001
                blind.append(f"demo language, {tag!r}: {exc}")
    except ImportError as exc:                             # noqa: BLE001
        blind.append(f"could not load the camera-string checker: {exc}")

    print(f"CAPTION CONTROL: {n - len(blind)}/{n} arms behaved")
    print(f"  {len(evade)}/{len(FORBIDDEN_PLANTS)} forbidden captions evade "
          f"G-STALL entirely -- that gap is why this file exists")
    if blind:
        print("REFUSE:")
        for b in blind:
            print(f"  {b}")
        return 2
    print("ok  every published caption describes what is drawn and explains "
          "nothing; the guard rejects mechanism claims and accepts honest ones")
    return 0


if __name__ == "__main__":
    sys.exit(check())
