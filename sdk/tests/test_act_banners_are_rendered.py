"""AN ACT'S OWN STAGE WORDS MUST REACH THE SCREEN, NOT JUST THE VALIDATOR.

THE DEFECT THIS PINS, AND IT IS THE THIRD OF ITS CLASS IN THIS PACKAGE.
``demo_mode.DemoAct.banners`` exists and ``demo_mode.validate_act`` CHECKS it
-- it refuses an act whose map omits a stage -- and ``demo_sequencer`` then
rendered the module-level ``BANNERS`` and threw the act's map away. An act
could therefore declare Sanaa's stage words, pass its own validation against
them, and put different words on camera.

Measured on 2026-09-01: the battery act overrides ``banners()`` with her seven
words and not one of them could reach a screen.

THE CLASS, WHICH IS WHAT THIS FILE IS REALLY FOR. ``Figure.beat`` was read by
nothing and every figure was advertised under a namespace no act chose. Four
authored, validated figure captions were dropped on the floor by
``announce_plot``. Now the banner map. Each was a declaration that had a
CHECKER and no READER, and in every case the check passing is what made the
absence invisible: an author writes the declaration, the validator agrees it is
well formed, and nothing renders it.

SO THE ASSERTION HERE IS DELIBERATELY NOT "the default map is correct". It is
that OVERRIDING THE DECLARATION CHANGES WHAT GOES ON THE WIRE -- a planted
control on the reader, in the sense of CLAUDE.md rule 3. A reader that cannot
be shown to see a non-default value is not known to be reading at all, and
that is exactly the state this map was in.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import workflows.dmr_act  # noqa: E402,F401  (registers shock-reflection)
import workflows.jet_flap_act  # noqa: E402,F401  (registers jet-flap)
from workflows import demo_sequencer, make_transcript  # noqa: E402
from workflows.demo_mode import BANNERS, STAGES, registered_acts  # noqa: E402

#: A word no stage of any act would ever produce on its own, so seeing it on
#: the wire cannot be a coincidence and cannot be the default leaking through.
PLANT = "Zephyr probe banner"


def _rebannered(act, banners):
    """A real act with its banner map replaced, and nothing else touched.

    Built as a SUBCLASS of the act's own class, carrying the act's own state,
    for two reasons. A stub written to agree with the sequencer proves only
    that the stub agrees, so this reads its numbers off the landed run tree
    exactly as the act does. And a proxy object is not a ``DemoAct``: the
    sequencer refuses one at the door, which would make this control pass for
    a reason that has nothing to do with banners.
    """
    cls = type(act)
    sub = type(f"Rebannered{cls.__name__}", (cls,),
               {"banners": lambda self, _b=dict(banners): dict(_b)})
    clone = sub.__new__(sub)
    clone.__dict__.update(act.__dict__)
    return clone


def _banners_on_the_wire(act) -> dict:
    """Every ``stage.banner`` text an act publishes, keyed by stage."""
    events: list = []

    def emit(name, payload):
        events.append((name, payload))

    demo_sequencer.run_act(act, emit=emit,
                           script=make_transcript("banner-probe", emit),
                           sleep=lambda _s: None)
    seen: dict = {}
    for name, payload in events:
        if name == "stage.banner":
            seen.setdefault(payload.get("stage"), set()).add(payload.get("text"))
    return seen


def test_an_act_that_overrides_its_banners_is_the_one_that_renders():
    """THE PLANT. The act's own word reaches the wire, the default does not."""
    act = registered_acts()["shock-reflection"]
    # Every stage carries the plant, so the assertion does not depend on which
    # stages this particular act happens to publish a banner for.
    planted = _rebannered(act, {stage: PLANT for stage in STAGES})
    seen = _banners_on_the_wire(planted)

    assert seen, "no banner reached the wire at all"
    # The solving stage is deliberately excluded: its banner comes from
    # `replay_stage.banner_for`, which derives it from the frame and is a
    # different reader with its own tests. Every OTHER stage is this map's.
    checked = 0
    for stage, texts in seen.items():
        if stage == "solving":
            continue
        checked += 1
        assert texts == {PLANT}, (
            f"stage {stage!r} published {sorted(texts)!r} instead of the act's "
            f"own declared banner; the declaration is being validated and "
            f"discarded")
    assert checked >= 4, (
        f"only {checked} non-solving stages published a banner, which is too "
        f"few for this control to mean anything")


def test_the_default_map_still_renders_for_an_act_that_declares_nothing():
    """THE CONTROL. Without an override, behaviour is exactly as it was.

    Without this, the test above would pass just as well if the sequencer had
    started ignoring the module default instead of honouring the act -- and
    every act that does not override would have gone dark.
    """
    act = registered_acts()["jet-flap"]
    seen = _banners_on_the_wire(act)

    assert seen, "no banner reached the wire at all"
    for stage, texts in seen.items():
        if stage == "solving":
            continue
        assert texts == {BANNERS[stage]}, (
            f"stage {stage!r} published {sorted(texts)!r}, not the module "
            f"default {BANNERS[stage]!r}")
    assert PLANT not in {t for texts in seen.values() for t in texts}


def test_every_stage_the_contract_fixes_has_a_default_banner():
    """A stage with no banner at all cannot be caught by either test above.

    ``validate_act`` already refuses an ACT whose map omits a stage; nothing
    said the same of the module default that every act falls back to.
    """
    missing = [stage for stage in STAGES if stage not in BANNERS]
    assert missing == [], f"stages with no default banner: {missing}"
