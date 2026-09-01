"""THE FIGURE NAMESPACE, and the two sequencer-generated payloads nothing planted.

PART ONE -- the namespace. The results stage advertised every figure of every
act under the literal string ``"results"``, while :class:`demo_mode.Figure`
carried a ``beat`` field that nothing read. Two separate consequences, and the
second was the one the report missed:

* an act declaring any other namespace had that declaration DISCARDED. Its
  figures were advertised at an address it never chose, and nothing failed.
* the stage also STAGED NOTHING. ``announce_plot`` composes
  ``/api/plot/<namespace>/<file>``; ``chief_engineer.server._serve_artifact``
  resolves that as ``<output root>/<namespace>/<file>``. An act's
  ``Figure.path`` points into its own run tree, which is not under the output
  root, so the address was unreachable for EVERY act -- the jet-flap act
  included. Measured on the assembled jet-flap results stage before the fix:
  four of four figure URLs answered 404, from a resolver shown in the same run
  able to answer 200.

So the tests below check BOTH halves. Deriving the namespace without staging
the file is a tidier 404, and staging without deriving puts every act's
pictures in one drawer.

THE RESOLVER CARRIES A PLANTED CONTROL (CLAUDE.md rule 3). A resolver that
answered "unreachable" to everything would make a 404 here meaningless and a
200 here impossible to trust, so :func:`_resolve` is exercised on a file known
to be there and on a file known not to be, and the tests refuse if either
answer is wrong.

PART TWO -- the audit the guard test does not cover. ``test_demo_sequencer_guard``
plants a forbidden string into each of the five DELEGATED publications: the
geometry announcement, the meshing table, the gates table, the results figure
titles and the results tables. It does not plant into either payload the
SEQUENCER ITSELF generates -- the stage header and the banner -- and the
sequencer's own docstring names both as covered by invariant 3. A guard named
in a docstring and never driven to its refusal is exactly the specimen class
VERIFICATION_CHARTER 2n.18 records, so the last two tests here drive them.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chief_engineer.server import _output_root  # noqa: E402
from workflows import OUT_ROOT, demo_sequencer, jet_flap_act  # noqa: E402
from workflows.demo_mode import (BANNERS, DemoContractError,  # noqa: E402
                                 Figure, Results)

ACT = jet_flap_act.ACT

#: One planted string per forbidden class, from the DEMO STANDARD v2 R5 rules.
#: Kept identical to the guard test's set so the two audits cover one list.
PLANTS = {
    "case_id": "JF1_L1_BLOWN_CMU020_A0",
    "gate_word": "GATE FAIL",
    "tier_word": "tier 2",
    "path": "verification/runs/JF1_jet_flap/artefacts/lift.png",
}


# ---------------------------------------------------------------------------
# The resolver, and the control that makes its answers evidence
# ---------------------------------------------------------------------------

def _resolve(url: str) -> str:
    """What the control-room server answers for ``url``: "200" or why not.

    Mirrors ``server._serve_artifact`` plus ``_serve_guarded_file``: exactly
    four segments, a ``.png`` tail, resolved under the output root, and
    refused if it escapes that root.
    """
    parts = url.strip("/").split("/")
    if len(parts) != 4 or not parts[3].endswith(".png"):
        return "404 the address is not the shape the server parses"
    root = _output_root()
    target = (root / parts[2] / parts[3]).resolve()
    if root not in target.parents:
        return "404 outside the served root"
    if not target.exists():
        return "404 no such file under the served root"
    return "200"


def _plant_the_resolver() -> None:
    """Show the resolver able to answer BOTH ways before any answer is read."""
    root = _output_root()
    staged = sorted(root.glob("*/*.png"))
    assert staged, ("nothing is staged under the served root, so this file "
                    "cannot show its resolver able to see a reachable URL and "
                    "none of its 404s would be evidence")
    hit = staged[0]
    good = f"/api/plot/{hit.parent.name}/{hit.name}"
    assert _resolve(good) == "200", (
        f"the resolver cannot see a file that is on disk ({good}); its 404s "
        f"are not evidence")
    assert _resolve(f"/api/plot/{hit.parent.name}/absent_by_construction.png"
                    ) != "200", (
        "the resolver calls an absent file reachable; its 200s are not "
        "evidence")


def test_the_resolver_is_shown_both_answers():
    """The plant itself is a test, so a broken control fails loudly."""
    _plant_the_resolver()


def test_the_output_root_the_sequencer_stages_into_is_the_one_served():
    """The two halves of the fix must name ONE directory.

    The sequencer stages into ``workflows.OUT_ROOT`` and the server serves
    from ``server._output_root()``. They are computed independently, from the
    same environment variable with the same default, and if they ever part the
    staging would land somewhere nothing serves -- which is the original defect
    wearing a different hat.
    """
    assert Path(OUT_ROOT).resolve() == _output_root()


# ---------------------------------------------------------------------------
# Part one: the namespace is the act's declaration
# ---------------------------------------------------------------------------

def _capture_results(act, record) -> list:
    """Drive the results stage on the guarded emit and return every event."""
    events: list = []
    seq = demo_sequencer.Sequencer(act=act, sleep=lambda _s: None,
                                  clock=lambda: len(events) * 0.001)
    guarded = seq._guarded(lambda name, payload: events.append((name, payload)))
    seq._stage_results(guarded, None, record)
    return events


def _plots(events) -> list:
    return [payload for name, payload in events if name == "plot.ready"]


class _Rebeaten:
    """The real jet-flap act with every figure's declared namespace replaced.

    The act is otherwise untouched and reads its numbers off the landed run
    tree as usual, so this measures the SEQUENCER's treatment of a declaration
    rather than a stub built to agree with it.
    """

    def __init__(self, act, beat: str):
        self._act = act
        self._beat = beat

    def results(self) -> Results:
        r = self._act.results()

        def rebeat(f: Figure) -> Figure:
            return Figure(f.path, f.title, f.caption, self._beat)

        return Results(fields=[rebeat(f) for f in r.fields],
                       plots=[rebeat(f) for f in r.plots],
                       tables=list(r.tables),
                       verification_lines=list(r.verification_lines),
                       limitations=list(r.limitations),
                       cost_actual=r.cost_actual,
                       cost_estimate_from_stage_2=r.cost_estimate_from_stage_2)

    def __getattr__(self, name):
        return getattr(self._act, name)


def test_a_declared_namespace_is_honoured_rather_than_discarded():
    """THE CASE THAT USED TO FAIL: an act that declares its own namespace."""
    _plant_the_resolver()
    act = _Rebeaten(ACT, "namespace-probe")
    plots = _plots(_capture_results(act, ACT.run_record()))

    assert plots, "the results stage announced no figure at all"
    for payload in plots:
        assert payload["url"].startswith("/api/plot/namespace-probe/"), (
            f"the act's declared namespace was discarded: {payload['url']}")
        assert _resolve(payload["url"]) == "200", (
            f"the address published is not one the server can serve: "
            f"{payload['url']} -> {_resolve(payload['url'])}")


def test_the_jet_flap_act_publishes_exactly_the_addresses_it_declares():
    """THE CASE THAT MUST NOT MOVE: the jet-flap act, whose figures declare
    ``results`` and whose published event stream must therefore be unchanged
    by deriving the namespace instead of hard-coding it.

    Pinned as a literal list rather than compared to the act, so a change to
    either side is a failure here rather than a tautology.
    """
    _plant_the_resolver()
    plots = _plots(_capture_results(ACT, ACT.run_record()))
    urls = sorted(p["url"] for p in plots)
    assert urls == sorted([
        "/api/plot/results/jet_flap_1_lift_vs_blowing.png",
        "/api/plot/results/jet_flap_2_chordwise_pressure.png",
        "/api/plot/results/jet_flap_3_flow_field.png",
        "/api/plot/results/jet_flap_7_mesh_forcesweep.png",
    ]), urls
    for url in urls:
        assert _resolve(url) == "200", (
            f"the jet-flap act's own figure address does not resolve: {url}")


@pytest.mark.parametrize("bad", ["", "   ", ".", "..", "a/b", "../escape",
                                 "with space", "/leading"])
def test_a_namespace_that_is_not_a_directory_name_is_refused(bad):
    """A namespace with a slash does not reach a 404; it reaches an address
    the server cannot parse into four segments, and the act never learns."""
    figure = copy.copy(ACT.results().fields[0])
    object.__setattr__(figure, "beat", bad)
    with pytest.raises(demo_sequencer.SequencerRefused):
        demo_sequencer.figure_namespace(figure)


def test_a_refusal_does_not_quote_the_namespace_it_refused():
    """The refusal is published as the mission's failure reason, so quoting a
    namespace that contained a path would put that path on the screen through
    the guard that exists to keep it off -- the leak-by-error-message failure
    ``screen_refusal_class`` was written for."""
    figure = copy.copy(ACT.results().fields[0])
    object.__setattr__(figure, "beat", "/home/ubuntu/certonomous-runs/secret")
    with pytest.raises(demo_sequencer.SequencerRefused) as caught:
        demo_sequencer.figure_namespace(figure)
    assert "certonomous-runs" not in str(caught.value)


# ---------------------------------------------------------------------------
# Part two: the two payloads the sequencer itself generates
# ---------------------------------------------------------------------------

def _publish_probe(payload: dict, event: str = "stage.begin"):
    """Publish one payload through the one publication point.

    Returns ``(refusal, events)``. Nothing is delegated here: this is the
    sequencer generating a payload of its own, which is the half of invariant
    3 the guard test does not reach.
    """
    events: list = []
    seq = demo_sequencer.Sequencer(act=ACT, sleep=lambda _s: None)
    guarded = seq._guarded(lambda name, p: events.append((name, p)))
    try:
        seq._publish(guarded, event, payload)
    except DemoContractError as exc:
        return str(exc), events
    return None, events


@pytest.mark.parametrize("plant", sorted(PLANTS), ids=sorted(PLANTS))
def test_a_stage_header_carrying_a_forbidden_string_is_refused(plant):
    """SITE 6: the stage header, generated by ``run`` and by nothing else."""
    refusal, events = _publish_probe({"stage": PLANTS[plant], "agents": 3})
    assert refusal, f"a planted {plant} in a STAGE HEADER was published"
    assert not events, "the payload went out before the guard refused it"

    # THE CONTROL ON THE CONTROL: the identical publication, clean, must go
    # out. Without it, a refusal caused by something ambient would read as a
    # working guard.
    clean, clean_events = _publish_probe({"stage": "results", "agents": 3})
    assert clean is None, clean
    assert [name for name, _ in clean_events] == ["stage.begin", "stage.banner"]


@pytest.mark.parametrize("plant", sorted(PLANTS), ids=sorted(PLANTS))
def test_a_banner_carrying_a_forbidden_string_is_refused(plant, monkeypatch):
    """SITE 7: the banner, derived at publication from the very payload being
    published, and never authored by an act.

    Planted at its SOURCE -- the stage-to-banner map -- rather than by writing
    a "banner" key into the payload, because ``_publish`` overwrites that key
    and a plant it overwrites is not a plant.
    """
    monkeypatch.setitem(BANNERS, "results", PLANTS[plant])
    refusal, events = _publish_probe({"stage": "results"}, event="demo.results")
    assert refusal, f"a planted {plant} in a BANNER was published"
    assert not events, "the banner went out before the guard refused it"

    monkeypatch.setitem(BANNERS, "results", "results")
    clean, clean_events = _publish_probe({"stage": "results"},
                                         event="demo.results")
    assert clean is None, clean
    assert [name for name, _ in clean_events] == ["demo.results",
                                                  "stage.banner"]
