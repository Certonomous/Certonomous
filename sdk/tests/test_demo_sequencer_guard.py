"""INVARIANT 3 has no bypass: the planted control for the sequencer's guard.

``demo_sequencer``'s own docstring says every payload passes
:func:`demo_mode.assert_screen_safe` at publication. It did not. Five
delegated publications were handed the RAW ``emit`` and so never reached
:meth:`Sequencer._publish`: the geometry announcement, the meshing resolution
table, the gates planted-check table, the results figure announcements and the
results tables. Between them they carry every table cell and every figure
title the act shows.

THE FIX IS A CHOKE POINT, NOT FIVE PATCHES. :meth:`Sequencer.run` wraps the
raw emit ONCE and hands only the wrapper to every stage, so no stage holds the
raw emit and a SIXTH delegated publication cannot be added unguarded. Patching
five call sites would have closed the instances and left the possibility; this
removes the possibility. ``_publish`` refuses an emit not carrying
``GUARD_MARK``, so the wrapping is checked rather than arranged.

WHY A PLANTED CONTROL AND NOT A WIRING CHECK. CLAUDE.md rule 3 says a zero
from a reader not shown able to see a non-zero is not evidence, and
VERIFICATION_CHARTER §2n.18 says a guard is measured by driving it to its
refusal, never inferred from its source — three specimens there were guards
two supervisors had personally READ and certified, which could not fail at
all. A guard that is called but cannot abort is WORSE than one that is absent,
because it reads green. So each test below plants a payload the DEMO STANDARD
v2 R5 rules forbid — a case id, a gate word, a tier word, a path — into one
delegated path and asserts the walk ABORTS with the offending event never
reaching the sink.

AND THE CONTROL ON THE CONTROL. Each test then re-runs the identical plant
with the RAW emit handed to the stage, which is exactly what those five sites
received before the choke point, and asserts the bad payload LANDS in the sink
un-refused. Without that half, a test that aborts for some unrelated reason
would look like a working guard. Note where the unguarded control's refusal
lands: ``_publish``'s choke assertion fires, but only AFTER the payload has
already gone out. That is precisely why the choke point had to be at the wrap
and not only at ``_publish``.

Structural note on what the type system does and does not catch: ``Table`` and
``MeshPlan`` check their titles and headers in ``__post_init__`` and do NOT
check their ROWS, so a bad cell is constructible and only the publication
guard stands between it and the screen. That is the defect class this file
exists for.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from chief_engineer.transcript import Transcript  # noqa: E402
from workflows import demo_sequencer, jet_flap_act  # noqa: E402
from workflows.demo_mode import DemoContractError  # noqa: E402

#: One planted string per forbidden class, from the DEMO STANDARD v2 R5 rules.
#: Each is asserted to raise on its own so a checker that stopped matching one
#: class cannot hide behind the others.
PLANTS = {
    "case_id": "JF1_L1_BLOWN_CMU020_A0",
    "gate_word": "GATE FAIL",
    "tier_word": "tier 2",
    "path": "verification/runs/JF1_jet_flap/artefacts/lift.png",
}


class _PlantedAct:
    """The real jet-flap act with exactly one accessor overridden.

    Everything else is read off the landed run tree as usual, so a test that
    passes here passes on the act the screen actually shows rather than on a
    stub built to agree with it.
    """

    def __init__(self, act, **overrides):
        object.__setattr__(self, "_act", act)
        object.__setattr__(self, "_overrides", overrides)

    def __getattr__(self, name):
        overrides = object.__getattribute__(self, "_overrides")
        if name in overrides:
            return overrides[name]
        return getattr(object.__getattribute__(self, "_act"), name)


def _mutated(obj, **fields):
    """A copy of a frozen dataclass instance with fields set after the fact.

    Deliberately NOT ``dataclasses.replace``: replace re-runs
    ``__post_init__``, which for a title or a label would refuse the plant at
    construction and the publication guard would never be reached. The defect
    being reproduced is a value that is assigned after validation, which is
    how a bad cell gets past an authorship check in the first place.
    """
    clone = copy.copy(obj)
    for key, value in fields.items():
        object.__setattr__(clone, key, value)
    return clone


def _script(sink):
    return Transcript("guard-control", echo=None,
                      sink=lambda entry: sink("transcript.entry",
                                              entry.as_dict()))


def _drive(stage: str, act, *, guarded: bool):
    """Run ONE stage of ``act`` and return (raised, events).

    ``guarded=True`` hands the stage exactly what :meth:`Sequencer.run` hands
    it: the emit wrapped ONCE at the choke point. ``guarded=False`` hands it
    the RAW emit, which is what every one of these five sites received before
    the choke point existed, so the same plant can be shown to leak.
    """
    events: list[tuple[str, dict]] = []

    def emit(name, payload):
        events.append((name, payload))

    seq = demo_sequencer.Sequencer(act=act, sleep=lambda s: None)
    handed = seq._guarded(emit) if guarded else emit
    record = act.run_record()
    raised = None
    try:
        getattr(seq, f"_stage_{stage}")(handed, _script(emit), record)
    except DemoContractError as exc:
        raised = str(exc)
    except demo_sequencer.SequencerRefused as exc:
        # The unguarded control reaches ``_publish`` after it has already
        # leaked, and ``_publish`` refuses an unmarked emit. That refusal is
        # the choke point doing its job; it arrives AFTER the leak, which is
        # exactly why the delegated sites needed closing and not just
        # ``_publish``. Recorded, not swallowed: the leak assertions below
        # read the events that got out before it.
        raised = str(exc)
    return raised, events


def _names(events):
    return [name for name, _ in events]


def _blob(events):
    return repr(events)


ACT = jet_flap_act.ACT


# -- site 1: the geometry announcement --------------------------------------

@pytest.mark.parametrize("plant", sorted(PLANTS), ids=sorted(PLANTS))
def test_geometry_announcement_is_guarded(plant):
    bad = PLANTS[plant]
    geometry = _mutated(ACT.geometry(), display_label=bad)
    act = _PlantedAct(ACT, geometry=lambda: geometry)

    raised, events = _drive("geometry", act, guarded=True)
    assert raised, f"the guard did not abort on a planted {plant}"
    assert bad in raised or plant == "path"
    assert "geometry.ready" not in _names(events)

    leaked, leaked_events = _drive("geometry", act, guarded=False)
    assert leaked is None or "geometry.ready" in _names(leaked_events), (
        "the control could not show the plant leaking without the guard, so "
        "the abort above is not evidence the guard caused it")


# -- site 2: the meshing resolution table -----------------------------------

@pytest.mark.parametrize("plant", sorted(PLANTS), ids=sorted(PLANTS))
def test_meshing_table_cell_is_guarded(plant):
    bad = PLANTS[plant]
    mesh = ACT.mesh_plan()
    rows = [list(r) for r in mesh.resolution_rows]
    rows[0][0] = bad
    act = _PlantedAct(ACT, mesh_plan=lambda: _mutated(mesh,
                                                      resolution_rows=rows))

    raised, events = _drive("meshing", act, guarded=True)
    assert raised, f"a planted {plant} in a mesh table CELL was published"
    assert "transcript.table" not in _names(events)

    _, leaked_events = _drive("meshing", act, guarded=False)
    assert "transcript.table" in _names(leaked_events)
    assert bad in _blob(leaked_events), (
        "the unguarded control did not carry the plant, so this test cannot "
        "see the leak it claims to close")


# -- site 3: the gates planted-check table ----------------------------------

@pytest.mark.parametrize("plant", sorted(PLANTS), ids=sorted(PLANTS))
def test_gates_table_cell_is_guarded(plant):
    bad = PLANTS[plant]
    gates = ACT.gates()
    rows = [list(r) for r in gates.planted_checks.rows]
    rows[0][0] = bad
    checks = _mutated(gates.planted_checks, rows=rows)
    act = _PlantedAct(ACT, gates=lambda: _mutated(gates,
                                                  planted_checks=checks))

    raised, events = _drive("gates", act, guarded=True)
    assert raised, f"a planted {plant} in a gates table CELL was published"
    assert "transcript.table" not in _names(events)

    _, leaked_events = _drive("gates", act, guarded=False)
    assert "transcript.table" in _names(leaked_events)
    assert bad in _blob(leaked_events)


# -- site 4: the results figure announcements -------------------------------

@pytest.mark.parametrize("plant", sorted(PLANTS), ids=sorted(PLANTS))
def test_results_figure_title_is_guarded(plant):
    bad = PLANTS[plant]
    results = ACT.results()
    figures = list(results.fields)
    assert figures, "the act has no field figure to plant into"
    figures[0] = _mutated(figures[0], title=bad)
    act = _PlantedAct(ACT, results=lambda: _mutated(results, fields=figures))

    raised, events = _drive("results", act, guarded=True)
    assert raised, f"a planted {plant} in a FIGURE TITLE was published"
    assert "plot.ready" not in _names(events)

    _, leaked_events = _drive("results", act, guarded=False)
    assert "plot.ready" in _names(leaked_events)
    assert bad in _blob(leaked_events)


# -- site 5: the results tables ---------------------------------------------

@pytest.mark.parametrize("plant", sorted(PLANTS), ids=sorted(PLANTS))
def test_results_table_cell_is_guarded(plant):
    bad = PLANTS[plant]
    results = ACT.results()
    tables = list(results.tables)
    assert tables, "the act has no results table to plant into"
    rows = [list(r) for r in tables[0].rows]
    rows[0][0] = bad
    tables[0] = _mutated(tables[0], rows=rows)
    act = _PlantedAct(ACT, results=lambda: _mutated(results, tables=tables))

    raised, events = _drive("results", act, guarded=True)
    assert raised, f"a planted {plant} in a results table CELL was published"
    assert "transcript.table" not in _names(events)

    _, leaked_events = _drive("results", act, guarded=False)
    assert "transcript.table" in _names(leaked_events)
    assert bad in _blob(leaked_events)


# -- the choke point itself --------------------------------------------------

def test_run_wraps_the_emit_exactly_once():
    """``run`` is the only place the raw emit is touched, and it wraps once.

    Both halves matter. Wrapping in more than one place is how the five sites
    got out of step in the first place; wrapping more than once on the same
    emit would sweep 605 solve frames twice for one answer.
    """
    source = Path(demo_sequencer.__file__).read_text(encoding="utf-8")
    wraps = source.count("self._guarded(emit)")
    assert wraps == 1, (
        f"the raw emit is wrapped at {wraps} places; the choke point is one "
        f"wrap in run(), and every stage receives the wrapper")

    calls = []

    def emit(name, payload):
        calls.append(name)

    seq = demo_sequencer.Sequencer(act=ACT, sleep=lambda s: None)
    once = seq._guarded(emit)
    assert getattr(once, demo_sequencer.GUARD_MARK, False)
    assert seq._guarded(once) is once, (
        "wrapping an already-guarded emit nested instead of returning it")
    assert seq._guarded(None) is None


def test_publishing_on_an_unguarded_emit_is_refused():
    """The choke point is CHECKED, not merely arranged.

    A future stage that somehow obtained the raw emit and published on it is
    refused at ``_publish``, so "no stage holds the raw emit" is a property of
    the code rather than a convention a later edit may not have read.
    """
    seen = []
    seq = demo_sequencer.Sequencer(act=ACT, sleep=lambda s: None)

    with pytest.raises(demo_sequencer.SequencerRefused):
        seq._publish(lambda name, payload: seen.append(name),
                     "demo.prompt", {"stage": "prompt", "text": "Meshing"})
    assert not seen, "the unguarded payload was published before the refusal"

    # The control: the SAME payload on a guarded emit publishes normally, so
    # the refusal above is about the wrapping and not about the payload.
    guarded = seq._guarded(lambda name, payload: seen.append(name))
    seq._publish(guarded, "demo.prompt", {"stage": "prompt", "text": "Meshing"})
    assert seen == ["demo.prompt", "stage.banner"]


# -- the prompt stage shows what was TYPED -----------------------------------

def test_prompt_stage_shows_what_was_typed():
    """A viewer's own words, not the act's registered string.

    Measured before this was wired: the prompt stage published
    ``jet_flap_act.PROMPT`` whatever the user typed, so a reworded prompt of
    the same intent was answered with canned text echoed back as the viewer's
    own, silently. Both limbs are driven here: the typed string when there is
    one, the act's own when there is not.
    """
    typed = ("Blown wing high lift: sweep the trailing edge jet momentum "
             "coefficient from 0 to 0.6 and give me the drag polar.")
    assert typed != jet_flap_act.PROMPT

    def run(typed_prompt):
        events = []
        seq = demo_sequencer.Sequencer(act=ACT, sleep=lambda s: None,
                                       typed_prompt=typed_prompt)
        guarded = seq._guarded(lambda n, p: events.append((n, p)))
        seq._stage_prompt(guarded, None, ACT.run_record())
        return [p["text"] for n, p in events if n == "demo.prompt"]

    assert run(typed) == [typed], "the screen did not show what was typed"
    assert run(None) == [ACT.prompt().text]
    assert run("   ") == [ACT.prompt().text], (
        "a blank prompt must fall back to the act's own, not show whitespace")


def test_a_typed_prompt_is_guarded_like_every_other_payload():
    """The typed string is NOT exempt from the screen guard.

    The flagged trade-off, driven rather than asserted: a typed prompt
    carrying an internal identifier refuses, and the mission fails with the
    reason, rather than being silently swapped for the act's own wording.
    """
    seq = demo_sequencer.Sequencer(
        act=ACT, sleep=lambda s: None,
        typed_prompt="run the case in verification/runs/JF1_jet_flap please")
    events = []
    guarded = seq._guarded(lambda n, p: events.append(n))
    with pytest.raises(DemoContractError):
        seq._stage_prompt(guarded, None, ACT.run_record())
    assert not events, "the banned string was published before the refusal"


# -- the three internal-identifier classes added 2026-09-01 ------------------

#: MEASURED before these rules existed: the checker refused case ids, gate
#: words, tier words, lesson ids, docket ids and paths, and ALLOWED all three
#: of these. Sanaa's rule is "no internal information"; enforcing six of nine
#: classes while reading as complete is how the other three reach a screen.
NEWLY_BANNED = {
    "pid bare": "the solver is running as pid 1103918",
    "pid colon": "pid: 1103918",
    "pid hash": "pid #1103918",
    "commit sha short": "landed at commit d0fea770",
    "commit sha long": "landed at 4905abddc0ffee1234567890abcdef1234567890",
    "commit sha upper": "landed at D0FEA770",
    "port": "the control room is on port 8765",
}

#: THE FALSE-POSITIVE HALF, and it is not decoration. A checker that fires on
#: the act's own physics wording gets switched off, and a switched-off checker
#: is why these strings survived a manual grep in the first place. Every entry
#: is wording this family really uses or plausibly would.
MUST_STAY_ALLOWED = {
    "seven-digit iteration count": "The counter reached 1234567 iterations.",
    "hex-alphabet word, seven letters": "The trailing edge is defaced by the slot.",
    "hex-alphabet word, eight letters": "A cabbaged profile is not admissible.",
    "port side of the aircraft": "the port wing carries the slot",
    "port as a verb": "We port the case to the finer grid.",
    "rapid": "a rapid rise in lift",
    "cell count": "39,984 cells on the force grid",
    "seven-digit cell count": "1000000 cells on the companion grid",
    "scientific notation": "The residual is 1.234e-03 at the last iteration.",
    "a date": "2026-09-01",
    "turbulence model": "k-omega SST resolved to the wall",
    "wall resolution": "Wall spacing y+ below 1 across the section.",
    "the sweep": "The jet momentum coefficient sweeps from 0 to 0.4.",
    "the citation": "Williams, Butler and Wood, ARC R&M 3304 (1961), eq. 2.",
    "the solver header": "OpenFOAM simpleFoam, steady incompressible turbulent flow",
    "a row of values": "0.4 0.30 0.20 0.10 0.0",
    "a percentage": "The lift is 12.4 percent above the unblown reference.",
}


@pytest.mark.parametrize("name", sorted(NEWLY_BANNED), ids=sorted(NEWLY_BANNED))
def test_new_internal_identifier_rules_abort(name):
    from workflows.demo_mode import check_demo_language

    with pytest.raises(DemoContractError):
        check_demo_language(NEWLY_BANNED[name])


@pytest.mark.parametrize("name", sorted(MUST_STAY_ALLOWED),
                         ids=sorted(MUST_STAY_ALLOWED))
def test_new_rules_do_not_fire_on_legitimate_wording(name):
    from workflows.demo_mode import check_demo_language

    check_demo_language(MUST_STAY_ALLOWED[name])


def test_the_real_screen_carries_no_false_positive():
    """Drive the WHOLE act and check every rendered string it publishes.

    The rate matters more than the principle: measured on this walk, 715
    distinct rendered strings, zero refusals. A rule set is only honest if its
    cost on the real screen has been counted rather than assumed.
    """
    import itertools

    from workflows.demo_mode import assert_screen_safe

    events = []
    tick = itertools.count()
    script = Transcript("fp-probe", echo=None,
                        sink=lambda e: events.append(("transcript.entry",
                                                      e.as_dict())))
    demo_sequencer.run_act("jet-flap",
                           emit=lambda n, p: events.append((n, p)),
                           script=script, sleep=lambda s: None,
                           clock=lambda: next(tick) * 0.001)
    assert len(events) > 1000, "the act did not walk; this proves nothing"
    for name, payload in events:
        # Exactly the walk the sequencer performs, zones and skip-list
        # included. Re-checking with a flat screen zone would manufacture a
        # false positive on the act's own limitations box.
        assert_screen_safe(payload)
