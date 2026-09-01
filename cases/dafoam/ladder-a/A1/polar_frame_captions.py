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
#: THE APPROVED CAPTIONS, to Sanaa's caption rule (2026-09-01, newest of her
#: directives by GIT COMMIT ORDER -- the filename timestamps invert across the
#: 2006Z naming boundary and are not the authority): captions carry NUMBERS,
#: SYMBOLS AND UNITS, never English sentences; short and bulleted.
#:
#: HER RULE AND THE HONESTY CONSTRAINT POINT THE SAME WAY, which is why the flat
#: English sentence this file first carried is gone with nothing lost. A number
#: cannot assert a mechanism. "alpha = 18 deg, iter 1000/1000" makes no claim
#: about separation, shedding or stall, and it cannot be read as one.
#:
#: WHAT IS NOT QUOTED, AND WHY. The residual for this point is NOT given as a
#: number, because `AOA_POINTS.json` records `achieved_min_residual: None` for
#: alpha = 18 -- DAFoam printed no satisfaction line, so there is no measured
#: residual to quote. `1e-8` is the REGISTERED tolerance and the mark says it
#: was not met; that is a verdict, not a measurement, and the caption does not
#: dress it as one.
#: BULLETS, NOT ONE LINE, and the change was forced by a measurement rather than
#: by style. The single-line form ran off the right edge of a 900 px render --
#: 69 non-background pixels in the last twelve columns, with "converged" sliced
#: in half on screen -- while every text-side check stayed green. Her rule asks
#: for bullets and the render agrees with her: short lines fit.
CAPTIONS: dict[str, list[str]] = {
    "polar_field_alpha18_not_converged": [
        "alpha = 18 deg",
        "iter 1000/1000",
        "tol 1e-8 not met",
        "9/19 converged (both arms)",
    ],
    "section_grid": [
        "4032 cells | 8316 points",
        "O-grid, coarse A1 mesh",
    ],
    # THE QUALIFIER LIVES IN THE SAME BULLET AS THE NUMBER, and that was forced
    # by an arm going red on this very entry. The first version put "coarse A1
    # mesh" in bullet [0] and "y+ 16.7-92.4" in bullet [1] -- and a bullet is
    # read on its own, so bullet [1] published a y+ range naming no mesh. That
    # is the two-channel failure again, one level down from the G-STALL case:
    # a qualifier one line away from its number is a qualifier the reader of
    # that line does not have.
    "section_grid_leading_edge": [
        "leading edge | 4032 cells",
        "coarse A1 mesh y+ 16.7-92.4",
    ],
}

#: Per-frame caption for the progressive grid reveal. Both numbers are MEASURED
#: per frame: the radius is the clip the frame was rendered at and the cell
#: count is what ParaView reported it kept, not an estimate.
REVEAL_CAPTION = "r = {radius:.2f} m  |  {kept}/{total} cells"

#: The refusal, in numbers. Bulleted, no sentence.
REFUSAL_BULLETS = [
    "19 angles run  |  9 converged  |  10 not converged",
    "tol 1e-8  |  cap 1000 iter",
    "wall-resolved study: running",
]

# ---------------------------------------------------------------------------
#: MUST BE REJECTED, WITHOUT AN ANGLE IN THE STRING. These are the OLD prose
#: caption shape, where the angle sat in the frame label and the claim sat in the
#: caption. EVERY ONE OF THEM PASSES `G-STALL` UNTOUCHED.
FORBIDDEN_NO_ANGLE = [
    "The flow separates over the upper surface here.",
    "The wake is shedding behind the section.",
    "You can see the boundary layer separating.",
    "The flow is unsteady at this angle.",
    "Large vortices form above the section.",
    "This shows the flow breaking down past the leading edge.",
    "The recirculation region is visible above the chord.",
    "The wake is turbulent here.",
]

#: MUST BE REJECTED, WITH AN ANGLE IN THE STRING. These are the NEW numeric
#: caption shape. `G-STALL` DOES catch these, and that is the interaction the
#: caption directive produced without anybody designing it: moving the angle
#: into the caption puts the stall word and the angle in ONE string, which is
#: the only arrangement `G-STALL` can see. MEASURED, both ways:
#:
#:   "The flow separates over the upper surface here."   G-STALL SILENT
#:   "alpha = 18 deg | stall | 9/19"                     G-STALL FIRES
#:
#: The mechanism guard STAYS PRIMARY regardless: it needs no angle, so it is
#: unaffected by where the angle lives, and it is the only one of the two that
#: covers a caption carrying no number at all.
#: ...BUT ONLY FOR THE VOCABULARY `G-STALL` ALREADY HAS. These carry a word from
#: its own list (`stall`, `separation onset`) beside an angle, and it fires.
FORBIDDEN_WITH_ANGLE = [
    "alpha = 18 deg  |  stall  |  9/19",
    "18 deg  |  separation onset  |  10/19",
]

#: AND HERE IS THE HALF THAT SURVIVES THE FORMAT CHANGE, found when an arm went
#: red on an overclaim of mine. I first put "wake shedding" in the list above,
#: expecting the numeric format to make G-STALL catch it. IT DOES NOT, and it
#: never could: `shedding` is not in G-STALL's vocabulary at all, and neither
#: are `separates`, `recirculation` or `turbulent`.
#:
#: SO THE FORMAT CHANGE RESTORES COVERAGE ONLY FOR THE WORDS G-STALL ALREADY
#: KNOWS. A mechanism claim outside its vocabulary is invisible to it in EITHER
#: format, with or without an angle. That is the precise reason the mechanism
#: guard stays primary rather than becoming redundant.
FORBIDDEN_WITH_ANGLE_OUTSIDE_GSTALL_VOCAB = [
    "alpha = 18 deg  |  wake shedding  |  9/19",
    "18 deg  |  flow separates  |  10/19",
    "alpha = 18 deg  |  turbulent wake  |  9/19",
]

FORBIDDEN_PLANTS = (FORBIDDEN_NO_ANGLE + FORBIDDEN_WITH_ANGLE
                    + FORBIDDEN_WITH_ANGLE_OUTSIDE_GSTALL_VOCAB)

#: MUST BE ACCEPTED. Numeric, provenance-carrying, mechanism-free. Without this
#: arm a guard that rejected everything would score full marks.
ALLOWED_PLANTS = [
    "alpha = 18 deg  |  iter 1000/1000  |  9/19 converged",
    "4032 cells  |  8316 points  |  O-grid",
    "r = 0.19 m  |  118/4032 cells",
    "coarse A1 mesh  |  4032 cells  |  y+ 16.7-92.4",
]

# ---------------------------------------------------------------------------
# TRAP 2: A NUMBER MUST NAME WHAT IT IS TRUE OF.
#
# `CLAUDE.md` rule 3 says the number wins -- but only if the number is TRUE OF
# THE THING IT SITS NEXT TO, and numeric compression is exactly what invites
# dropping the qualifier that keeps it true. Heat-transfer measured the case:
# `y+ < 1` was true on their housing (0.73-0.75) and FALSE on their duct wall
# (2.40), and a compressed caption would have carried the true-sounding half.
#
# FOUR ARE LIVE ON OUR OWN GROUND AND EVERY PLANT BELOW IS ONE WE KNOW IS FALSE
# WHEN STRIPPED -- which makes them evidence rather than illustration:
#
#   y+     the coarse A1 mesh measures y+ 16.7-92.4; A1WR only TARGETS y+ < 1
#          and has produced no frame. A bare "y+ < 1" is false of every frame
#          rendered so far.
#   Re     two of them, one per regime: 6.6628e5 incompressible, 6.5338e6
#          compressible. A bare "Re 6.5e6" is false of the incompressible arm.
#   A0     0.1 m^2 is NOMINAL against a true planform of 0.0999416 m^2.
#   twin   25.985 % is D19M's and false of D19O; 21.652 % is D19O's and false
#          of D19M. Both are true; NEITHER is true of the other row. A
#          percentage without its row undoes the whole reason the twin table
#          beats an assertion.
#
# A UNIT IS NOT A QUALIFIER. "m^2" does not say which area.
#
# `9/19 converged` is the one number here that needs no arm qualifier, and that
# is MEASURED rather than assumed: AOAC 9/19 and AOAI 9/19, counted from each
# arm's own AOA_POINTS.json. The bullet says "(both arms)" because that is what
# was counted.
QUALIFIER_RULES: list[tuple[str, re.Pattern, re.Pattern]] = [
    ("y+ must name its mesh",
     re.compile(r"\by\+\s*[<>=]|\by\+\s*\d", re.I),
     re.compile(r"\b(coarse|A1WR|wall-resolved|target|A1 mesh)\b", re.I)),
    ("Reynolds must name its regime",
     re.compile(r"\bRe\b\s*[=~]?\s*\d|\bReynolds\b", re.I),
     re.compile(r"\b(incompressible|compressible)\b", re.I)),
    ("the reference area must say it is nominal",
     re.compile(r"\bA0?\s*=\s*0\.1\b", re.I),
     re.compile(r"\b(nominal|reference)\b", re.I)),
    ("a drag-reduction percentage must name its row",
     re.compile(r"\b(25\.985|21\.65\d?|28\.2768|28\.3)\s*(?:%|per cent)", re.I),
     re.compile(r"\b(D19M|D19O|A2|twist|shape|unconstrained|constrained|"
                r"CL 0\.5|lift held)\b", re.I)),
]


def qualifier_hits(text: str) -> list[str]:
    """Every number here that does not name what it is true of."""
    out = []
    for name, number, qualifier in QUALIFIER_RULES:
        if number.search(text) and not qualifier.search(text):
            out.append(f"unqualified number: {name}")
    return out


#: MUST BE REJECTED: true-sounding numbers stripped of the qualifier that makes
#: them true. Every one of these is FALSE as written, on our own measurements.
UNQUALIFIED_PLANTS = [
    "y+ < 1",                                   # false of every frame we have
    "y+ 16.7-92.4",                             # true, but of WHICH mesh
    "Re 6.5e6",                                 # false of the incompressible arm
    "Reynolds 6.6628e5",                        # true, but of WHICH arm
    "A0 = 0.1 m^2",                             # nominal, not the true planform
    "25.985 % drag reduction",                  # D19M's, false of D19O
    "21.652 % drag reduction",                  # D19O's, false of D19M
]

#: MUST BE ACCEPTED: the same numbers carrying the noun they are true of.
QUALIFIED_PLANTS = [
    "A1WR target y+ < 1",
    "coarse A1 mesh y+ 16.7-92.4",
    "Re 6.5338e6 compressible",
    "Re 6.6628e5 incompressible",
    "A0 = 0.1 m^2 nominal | planform 0.0999416 m^2",
    "D19M 25.985 % drag | lift unconstrained",
    "D19O 21.652 % drag | CL 0.5 held",
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
    out.extend(qualifier_hits(text))
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

    # ---- TRAP 2: the qualifier arms, both directions -----------------------
    for q in UNQUALIFIED_PLANTS:
        n += 1
        if not qualifier_hits(q):
            blind.append(f"unqualified number NOT rejected: {q!r}")
    for q in QUALIFIED_PLANTS:
        n += 1
        if qualifier_hits(q):
            blind.append(f"qualified number wrongly rejected: {q!r} "
                         f"-> {qualifier_hits(q)}")

    # ---- THE GAP, MEASURED AND ASSERTED RATHER THAN DESCRIBED --------------
    # These arms exist so this file's central factual claim cannot rot: if a
    # successor widens G-STALL, they go red and the claim gets CORRECTED rather
    # than quietly becoming false.
    #
    # ⚠ AND HERE IS THE LIMIT OF THAT PATTERN, WRITTEN DOWN BECAUSE IT WAS
    # DISCOVERED RATHER THAN DESIGNED. These arms assert the claim against
    # G-STALL'S BEHAVIOUR, so they fire when the INSTRUMENT changes. They did
    # NOT fire when the caption FORMAT changed -- and that change is what
    # actually moved the claim, because numeric captions put the angle in the
    # caption where G-STALL can finally see it. The guard never moved; the
    # SUBJECT moved.
    #
    # A rot-arm catches the instrument changing under a document. It does not
    # catch the world changing under it. That is the honest boundary of the
    # pattern, and the mitigation here is that the claim is now stated
    # CONDITIONALLY -- "of captions carrying no angle" -- so a format change
    # narrows its scope rather than falsifying it.
    evade = [q for q in FORBIDDEN_NO_ANGLE if not STALL_CLAIM.search(q)]
    n += 1
    if len(evade) != len(FORBIDDEN_NO_ANGLE):
        blind.append(
            "the premise of this file has changed: G-STALL now catches "
            f"{len(FORBIDDEN_NO_ANGLE) - len(evade)} of the angle-less "
            "captions. Rewrite the docstring rather than leaving it stale.")
    caught = [q for q in FORBIDDEN_WITH_ANGLE if STALL_CLAIM.search(q)]
    n += 1
    if len(caught) != len(FORBIDDEN_WITH_ANGLE):
        blind.append(
            "G-STALL no longer catches numeric captions carrying one of its "
            "OWN vocabulary words beside an angle; the caption-format "
            "interaction this file records has changed.")
    # The other half of that finding, asserted so it cannot be forgotten: an
    # angle does NOT save G-STALL from a mechanism word it does not know.
    outside = [q for q in FORBIDDEN_WITH_ANGLE_OUTSIDE_GSTALL_VOCAB
               if not STALL_CLAIM.search(q)]
    n += 1
    if len(outside) != len(FORBIDDEN_WITH_ANGLE_OUTSIDE_GSTALL_VOCAB):
        blind.append(
            "G-STALL's vocabulary has widened to cover mechanism words it did "
            "not have; the claim that the mechanism guard is primary needs "
            "re-checking rather than assuming.")
    n += 1
    if not STALL_CLAIM.search("the stall angle is 13.0 deg"):
        blind.append("G-STALL no longer fires on its own control C7")

    # ---- the published captions themselves ---------------------------------
    published = [(f"{k}[{i}]", b) for k, v in CAPTIONS.items()
                 for i, b in enumerate(v)] + [
        (f"refusal bullet {i}", b) for i, b in enumerate(REFUSAL_BULLETS)] + [
        ("reveal caption", REVEAL_CAPTION.format(radius=0.19, kept=118, total=4032))]
    for tag, text in published:
        n += 1
        hits = caption_hits(text)
        if hits:
            blind.append(f"published caption {tag!r}: {hits}")

    # ---- and through the act's own camera-string checker --------------------
    try:
        from workflows.demo_mode import check_demo_language
        for tag, text in published:
            n += 1
            try:
                check_demo_language(text, zone="screen")
            except Exception as exc:                       # noqa: BLE001
                blind.append(f"demo language, {tag!r}: {exc}")
    except ImportError as exc:                             # noqa: BLE001
        blind.append(f"could not load the camera-string checker: {exc}")

    print(f"CAPTION CONTROL: {n - len(blind)}/{n} arms behaved")
    print(f"  {len(evade)}/{len(FORBIDDEN_NO_ANGLE)} angle-less captions evade "
          f"G-STALL; {len(caught)}/{len(FORBIDDEN_WITH_ANGLE)} numeric captions "
          f"using ITS OWN vocabulary are caught; "
          f"{len(outside)}/{len(FORBIDDEN_WITH_ANGLE_OUTSIDE_GSTALL_VOCAB)} "
          f"outside its vocabulary still evade it even WITH an angle")
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
