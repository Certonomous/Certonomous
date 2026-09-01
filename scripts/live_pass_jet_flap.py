#!/usr/bin/env python3
"""The jet-flap live pass, as one command.

WHAT THIS IS FOR. The jet-flap act reaches a screen through the mission
server: a prompt is POSTed, the router picks an intent, a workflow module
walks nine stages, and every fact it publishes lands on the mission's event
bus. This harness drives that path once and MEASURES what came out of it,
so the pass is a reading rather than a watch.

It runs in two modes and the checks are the SAME CODE in both:

* ``--offline`` drives ``demo_sequencer.run_act("jet-flap")`` in process,
  with a collecting emit, and never opens a socket. This is the PREDICTION:
  the numbers it prints are what the live pass must reproduce.
* the default drives a real server over HTTP.

WHAT IT NEVER DOES. It never starts, stops, signals or binds anything. In
live mode it POSTs and GETs; a server that is not up is reported, not
launched.

THE ZERO CONTROL, and it is the reason this file is longer than its checks.
CLAUDE.md rule 3: a zero from a reader not shown able to see a non-zero is
not evidence. Every check here is a check that can only report "clean", so
every check here is planted BEFORE its verdict is believed:

* the language sweep gets sixteen planted strings, one per alternative of
  every rule it claims to enforce, planted into a COPY of the collected
  events at a key the sweep actually reads;
* the ordering check gets four planted mutations, one per way an order can
  be wrong;
* the banner/content sync check gets two planted desynchronisations;
* the counters get the legacy-path shape planted, so "605 frames" is a
  reading from an instrument shown able to read zero as well.

If ANY plant is invisible the harness exits 2 and prints nothing green. A
guard that is called but cannot abort is worse than one that is absent.

THE INFLECTION DEFECT (L-425 addendum, twice in this lab). A vocabulary
check written ``\\b(a|b|c)\\b`` is blind to every inflection of every word in
it: ``\\bPASS\\b`` does not match "PASSED". Every plant below is therefore
WRITTEN BY HAND, one per alternative, and several are deliberately inflected.
None is generated from the pattern being tested, because a plant derived
from the pattern can only prove the pattern matches itself.

EXIT CODES
    0  every check green
    1  a check failed (the pass is a NO-GO)
    2  the harness refuses: a plant was invisible, or it could not do its job
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SDK = REPO / "sdk"
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

# ---------------------------------------------------------------------------
# What is asked for, verbatim
# ---------------------------------------------------------------------------

#: Sanaa's prompt, character for character. NOT paraphrased and NOT rewrapped
#: at a different column: the act's own PROMPT constant is asserted equal to
#: this below, so a drift in either is a refusal rather than a silent
#: substitution.
GOAL = ("Blown-wing high-lift: sweep the trailing-edge jet momentum "
        "coefficient from 0 to 0.4 and report lift against blowing with the "
        "classical jet-flap theory.")

SURFACE = "airfoil_blown_slot.stl"

EXPECTED_INTENT = "jet-flap-display"
ACT_KEY = "jet-flap"

#: Board 42, measured on the real dispatcher shape. These are the numbers the
#: live pass is graded against, and they are also derivable from the code:
#: 635 banners = 18 sequencer publications (9 stage.begin + 8 stage payloads +
#: demo.elapsed) + 617 replay publications (solve.begin + 5x(point.begin +
#: point.end) + 605 frames + solve.end); 1281 events = 2x635 + 1 geometry.ready
#: + 4 plot.ready + 3 transcript.table + 3 transcript.entry.
#: WHAT THE ACT PUBLISHES. Mode-invariant, and that is the point: this is the
#: same number in process and over HTTP, so it is the number worth gating on.
#:
#: THE DEFECT THIS SPLIT REPLACES, measured rather than reasoned. The first cut
#: gated on 1281 events END TO END and the live pass returned GATE FAIL on that
#: one clause with 1283. Diffing the live stream against the offline baseline on
#: the same tree, the delta was exactly two events and exactly two TYPES:
#: `mission.routed` at sequence 1 and `mission.completed` at sequence 1283.
#: Neither is published by the act. Both are published by
#: `chief_engineer.server._run_workflow` around it, so a harness that drives
#: `run_act` in process cannot emit them and never could. The expectation was
#: mode-blind, which is a defect in this file, not in the act -- and it was NOT
#: caused by either of the two commits that landed in between (the figure
#: namespace fix and the caption pass-through), both of which add keys and
#: staging, not events.
#:
#: Gating on the act's own census instead of the wire total also means a future
#: `mission.scoped` line -- published only when the prompt asks for more than
#: the run delivers -- lands as a reported envelope event rather than as a
#: spurious GATE FAIL.
EXPECT = {
    "total": 1281,
    "stage.banner": 635,
    "solve.frame": 605,
    "transcript.table": 3,
    "stage.begin": 9,
}

#: The nine stages, in the order the sequencer walks them. Taken from
#: demo_mode.STAGES at import time rather than retyped, so this harness cannot
#: disagree with the sequencer about what the order is. The literal is kept
#: only as a cross-check.
STAGES_LITERAL = ("prompt", "restatement", "assumption", "geometry",
                  "meshing", "feasibility", "solving", "gates", "results")

#: THE SERVER'S OWN MISSION ENVELOPE. Published by
#: `chief_engineer.server._run_workflow` before and after it calls the workflow
#: module, never by the act. Counted and reported, never gated: an offline run
#: has none of them by construction, and gating a mode-invariant census on
#: mode-dependent events is what produced a GATE FAIL on a healthy run.
SERVER_ENVELOPE = frozenset({"mission.routed", "mission.scoped",
                             "mission.completed", "mission.failed"})

#: THE LEGACY TELL. The pre-sequencer jet-flap surface published a flat
#: transcript of about thirty events and no stage machinery at all. If the
#: dispatcher is wired to that path the pass is a hard NO-GO, and the shape is
#: unmistakable: no banners and no frames.
LEGACY_TELL_MAX_EVENTS = 60

# ---------------------------------------------------------------------------
# Geometry bind, as declared
# ---------------------------------------------------------------------------

GEOMETRY_MD5 = "8c76afb4079995b25991e26248f81ffa"
GEOMETRY_COPIES = (
    SDK / "geometry" / SURFACE,              # what /api/geometry serves
    REPO / "cases" / "demo-surfaces" / SURFACE,   # the tracked operator copy
)
SOLVED_CHORD_M = 1.0
SOLVED_H_OVER_C = 0.005


# ---------------------------------------------------------------------------
# WHICH KEY OF WHICH EVENT IS RENDERED, and why each is on the list
# ---------------------------------------------------------------------------
#
# THE DEFECT THIS LIST EXISTS FOR. A previous sweep of this act walked every
# string in every payload and reported seventeen violations, all of them
# false: it read machine identifiers as prose. The three named offenders are
# the ones below, and each is excluded for a reason that is a property of the
# payload rather than a convenience:
#
#   `stage`      -- a routing key. Its values are the nine STAGES tokens.
#                   Nothing renders it; the control room has no handler that
#                   reads it, and the banner it names is carried as `text`.
#   `for_event`  -- the name of the event a banner describes, carried so a
#                   banner and its content can be AUDITED as a pair (this
#                   harness's sync check is exactly that audit). Reading
#                   "demo.prompt" as prose is how a guard earns a reputation
#                   for crying wolf.
#   `url`/`file` -- fetch addresses. `/api/geometry?name=airfoil_blown_slot.stl`
#                   and `jet_flap_1_lift_vs_blowing.png` are what the browser
#                   GETs, not what a viewer reads. The path rule fires on both
#                   by construction, and it is right to: a path is never on
#                   screen. It is not on screen. It is in an href.
#
# THIS IS NOT THIS HARNESS'S OPINION. The exclusion set is lifted verbatim
# from the act's own publication guard, `demo_mode.assert_screen_safe`, whose
# `audit_keys` is the authority on which keys are machine identifiers. Copying
# it means the sweep and the guard cannot disagree about what counts as text;
# it is asserted equal below rather than trusted, so a change there fails here
# instead of silently widening or narrowing this sweep.
AUDIT_KEYS_EXPECTED = {"for_event", "table_id", "beat", "event", "stage_id",
                       "url", "file"}

#: Additionally excluded, beyond the guard's own set.
EXTRA_EXCLUDED = {
    # A routing key, justified above. The guard DOES check it (its values are
    # innocent lowercase words), so excluding it here can only narrow, never
    # widen, the sweep -- and the ordering check reads it as an identifier,
    # which is the only thing it is.
    "stage",
    # Wall-clock floats and sequence numbers reach the sweep as numbers, not
    # strings, so they are excluded by type already; named here so the reader
    # does not have to derive that.
    "at",
}

#: TIER 1 -- keys `chief_engineer/control_room.html` DEMONSTRABLY renders, with
#: the line of that file that renders each. This is the list that matters for
#: "what a viewer reads today".
TIER1_RENDERED: dict[str, tuple[tuple[str, str], ...]] = {
    # el.innerHTML = ... bulletHTML(p.message) -- control_room.html:1444
    "transcript.entry": (("message", "control_room.html:1444 bulletHTML(p.message)"),
                         ("role", "control_room.html:1444 esc(p.role)")),
    # headers :1545, title :1547, rows :1536+, role :1546
    "transcript.table": (("title", "control_room.html:1547 subScript(esc(p.title))"),
                         ("headers", "control_room.html:1545 esc(h) per header"),
                         ("rows", "control_room.html:1536 rows rendered as cells"),
                         ("role", "control_room.html:1546 esc(p.role)")),
    # subText('viewportLabel', p.label) :1759 and :733 (the filmed still)
    # subText('viewportCaption', p.caption) :1765 and :734
    "geometry.ready": (("label", "control_room.html:1759,733 viewportLabel"),
                       ("caption", "control_room.html:1765,734 viewportCaption")),
    # addPlot builds <figure><img><figcaption><b>title</b>caption</figcaption>.
    # Before that, the title was `img.title` ONLY -- a hover tooltip, and a
    # filmed screen has no mouse, so four titles and four captions rendered
    # nowhere a camera could see.
    "plot.ready": (("title", "control_room.html addPlot figcaption <b>"),
                   ("caption", "control_room.html addPlot figcaption text")),
    # setStageBanner writes #stageBanner.textContent, latest-wins and unpaced.
    "stage.banner": (("text", "control_room.html setStageBanner -> #stageBanner"),),
    # solveFrame feeds pushTrace: the label is the trace title AND the series
    # key. The iteration and the lift coefficient are numbers, not text.
    "solve.frame": (("label", "control_room.html solveFrame -> pushTrace title"),),
    # $('routeRationale').innerHTML = bulletHTML(r.rationale) -- :946
    "mission.routed": (("rationale", "control_room.html:946 bulletHTML(r.rationale)"),),
}

#: TIER 2 -- the DEMO MODE screen contract. These payloads are published by the
#: sequencer and the replay stage and are swept by the act's own publication
#: guard, so they are screen text by contract. They are swept here by the SAME
#: walk the guard uses (audit keys skipped, `limitations` in its own zone), so
#: this harness reproduces the guard rather than inventing a second opinion.
#:
#: The nine `demo.*` payloads are now rendered by `addStageCard`, whose
#: `DEMO_SKIP` set is deliberately the SAME exclusion set this walk uses, so
#: the sweep reads exactly the fields the page shows. The remaining `solve.*`
#: and `stage.begin` payloads are swept more widely than they are rendered,
#: which is the conservative direction and is left that way on purpose.
#:
#: HISTORY, kept because it is the reason any of this exists: before the
#: handlers were added, `control_room.html` had NO case for `stage.banner`,
#: `stage.begin`, `demo.*` or `solve.*`, and its `switch` has no `default:`
#: branch -- so 1,270 of this act's 1,281 events fell through it silently.
TIER2_PREFIXES = ("stage.", "demo.", "solve.")

#: TEXT THE PAGE ITSELF PUTS ON SCREEN that no act published. It is two axis
#: labels, and they are swept through the same checker as everything on the
#: wire rather than exempted for being short. A guard with a carve-out for
#: "just a label" is how a label reaches a screen unswept.
PAGE_FIXED_STRINGS = (
    ("control_room.html solveFrame x_label", "Iteration"),
    ("control_room.html solveFrame y_label", "Lift coefficient"),
)


# ---------------------------------------------------------------------------
# Refusals
# ---------------------------------------------------------------------------

class HarnessRefused(RuntimeError):
    """The harness will not report a verdict. Exit 2, never a green line."""


def _refuse(message: str) -> None:
    raise HarnessRefused(message)


# ---------------------------------------------------------------------------
# The language sweep
# ---------------------------------------------------------------------------

def _language_checker():
    """`demo_mode.check_demo_language`, and the guard's own audit-key set.

    Imported rather than reimplemented, and the audit keys are ASSERTED
    against this file's expectation so a change to the guard breaks this
    harness loudly instead of quietly changing what it sweeps.
    """
    from workflows.demo_mode import DemoContractError, check_demo_language

    # The guard keeps its audit keys as a local inside assert_screen_safe, so
    # they cannot be imported. Read them out of the source, which is the only
    # honest way to assert against them, and refuse if the shape has changed.
    source = (SDK / "workflows" / "demo_mode.py").read_text(encoding="utf-8")
    block = re.search(r"audit_keys\s*=\s*\{(.*?)\}", source, flags=re.S)
    if not block:
        _refuse("demo_mode.assert_screen_safe no longer declares audit_keys; "
                "this harness cannot state which keys the guard treats as "
                "machine identifiers, so it will not claim to agree with it")
    found = set(re.findall(r'"([^"]+)"', block.group(1)))
    if found != AUDIT_KEYS_EXPECTED:
        _refuse(f"the publication guard's audit keys have changed to {sorted(found)}; "
                f"this harness sweeps on the assumption they are "
                f"{sorted(AUDIT_KEYS_EXPECTED)}. Re-read the guard before "
                f"believing any sweep result.")
    return check_demo_language, DemoContractError


def _rendered_strings(event: dict, tier2: bool = True):
    """Yield (key_path, text) for every RENDERED string in one event.

    Tier 1 keys are taken by name, from the explicit table above. Tier 2
    payloads are walked the way the publication guard walks them.
    """
    name = str(event.get("event") or "")
    payload = event.get("payload") or {}

    if name in TIER1_RENDERED:
        for key, _why in TIER1_RENDERED[name]:
            if key not in payload:
                continue
            yield from _leaves(payload[key], f"{name}.{key}", "screen")
        return

    if tier2 and name.startswith(TIER2_PREFIXES):
        for key, value in payload.items():
            if str(key) in AUDIT_KEYS_EXPECTED or str(key) in EXTRA_EXCLUDED:
                continue
            zone = "limitations" if str(key) == "limitations" else "screen"
            yield from _leaves(value, f"{name}.{key}", zone)


def _leaves(node, trail: str, zone: str):
    if isinstance(node, dict):
        for key, value in node.items():
            if str(key) in AUDIT_KEYS_EXPECTED or str(key) in EXTRA_EXCLUDED:
                continue
            sub = "limitations" if str(key) == "limitations" else zone
            yield from _leaves(value, f"{trail}.{key}", sub)
    elif isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            yield from _leaves(value, f"{trail}[{i}]", zone)
    elif isinstance(node, str):
        yield trail, node, zone


def sweep_language(events: list[dict]) -> list[dict]:
    """Every rendered string that breaks the on-screen language rules.

    Returns a list of {index, key, text, offending, reason}. An empty list is
    only evidence AFTER the plants below have been shown visible.
    """
    check, contract_error = _language_checker()
    violations: list[dict] = []
    for index, event in enumerate(events):
        for key, text, zone in _rendered_strings(event):
            try:
                check(text, zone=zone)
            except contract_error as exc:
                violations.append({
                    "index": index,
                    "event": event.get("event"),
                    "key": key,
                    "text": text,
                    "reason": str(exc),
                })
    return violations


def sweep_all_strings(events: list[dict]) -> list[dict]:
    """DIAGNOSTIC ONLY, and labelled so at the point of use.

    The naive walk: every string in every payload, machine identifiers
    included. Reported beside the real sweep so the reader can SEE the
    difference between "clean" and "clean because I looked at the right
    fields", rather than take this harness's word for it.
    """
    check, contract_error = _language_checker()
    out: list[dict] = []
    for index, event in enumerate(events):
        name = str(event.get("event") or "")
        # _raw_leaves, not _leaves: the naive walk deliberately skips nothing,
        # which is the whole point of quoting its number beside the real one.
        for key, text in _raw_leaves(event.get("payload") or {}, name):
            try:
                check(text, zone="screen")
            except contract_error as exc:
                out.append({"index": index, "event": name, "key": key,
                            "text": text, "reason": str(exc)})
    return out


def _raw_leaves(node, trail: str):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _raw_leaves(value, f"{trail}.{key}")
    elif isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            yield from _raw_leaves(value, f"{trail}[{i}]")
    elif isinstance(node, str):
        yield trail, node


# ---------------------------------------------------------------------------
# The counters
# ---------------------------------------------------------------------------

def count_events(events: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for event in events:
        name = str(event.get("event") or "")
        counts[name] = counts.get(name, 0) + 1
    return counts


def stage_begins(events: list[dict]) -> list[str]:
    """The stage of every stage.begin, in publication order, NOT deduped.

    Deduping first is how a stage begun twice out of order becomes invisible:
    first-appearance dedupe swallows the second. The ordered DISTINCT list the
    brief asks for is derived from this one, after it has been checked whole.
    """
    return [str((e.get("payload") or {}).get("stage"))
            for e in events if e.get("event") == "stage.begin"]


def distinct_in_order(values: list[str]) -> list[str]:
    seen, out = set(), []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def check_order(events: list[dict], stages: tuple[str, ...]) -> list[str]:
    """Every way the stage order is wrong. Empty means it is right."""
    raw = stage_begins(events)
    problems: list[str] = []
    unknown = [s for s in raw if s not in stages]
    if unknown:
        problems.append(f"stage.begin names stages the sequencer does not "
                        f"have: {sorted(set(unknown))}")
    if len(raw) != len(stages):
        problems.append(f"{len(raw)} stage.begin events, expected "
                        f"{len(stages)}")
    missing = [s for s in stages if s not in raw]
    if missing:
        problems.append(f"stages never begun: {missing}")
    duplicated = sorted({s for s in raw if raw.count(s) > 1})
    if duplicated:
        problems.append(f"stages begun more than once: {duplicated}")
    if raw != list(stages):
        problems.append(f"stage.begin order is {raw}, expected {list(stages)}")
    return problems


def check_legacy_tell(events: list[dict]) -> str | None:
    """The hard NO-GO shape: the old flat path, wired instead of the act."""
    counts = count_events(events)
    banners = counts.get("stage.banner", 0)
    frames = counts.get("solve.frame", 0)
    if banners == 0 and frames == 0:
        return (f"{len(events)} events, zero stage banners and zero solve "
                f"frames: this is the pre-sequencer flat path, not the act")
    if len(events) <= LEGACY_TELL_MAX_EVENTS:
        return (f"only {len(events)} events; the act publishes over a "
                f"thousand, so something short-circuited the walk")
    return None


# ---------------------------------------------------------------------------
# Banner / content synchronisation
# ---------------------------------------------------------------------------
#
# HOW THIS IS TESTED, stated because "the banner matches" is the kind of claim
# that is easy to make vacuously.
#
# Both publishers emit a banner as the SECOND half of a single tick: the
# content event, then `stage.banner` carrying `for_event` (the content event's
# name), `stage`, and `text`. Three legs, and the third is the one that is not
# circular:
#
#   LEG 1 (pairing). Every stage.banner at index i is immediately preceded by
#          a content event at i-1 whose name equals the banner's `for_event`
#          and whose `stage` equals the banner's `stage`. This catches a
#          banner running ahead of or behind its content, because "ahead" and
#          "behind" are exactly a banner whose neighbour is not its subject.
#
#   LEG 2 (stamped equality). The content payload carries its own `banner`
#          field, stamped in the same tick. It must equal the banner event's
#          `text`. This is a weak leg on its own -- one variable read twice --
#          and it is stated as weak.
#
#   LEG 3 (independent recomputation). For every event whose banner is a pure
#          function of the payload that was published -- the 605 solve.frame
#          events and the 18 sequencer publications -- the banner is RECOMPUTED
#          here from the content payload alone, by calling the same pure
#          functions the publishers call, and compared. This is the leg that
#          could fail if a banner were set on stage entry and drifted.
#
#          Twelve events are deliberately NOT recomputable and are named as
#          such: solve.begin, the five solve.point.begin, the five
#          solve.point.end and solve.end derive their banner from a separate
#          `banner_state` dictionary that is not published. They get legs 1
#          and 2 only, and the report says so rather than implying otherwise.

def check_banner_sync(events: list[dict]) -> dict:
    from chief_engineer.replay_stage import banner_for
    from workflows.demo_sequencer import banner_for_stage

    problems: list[str] = []
    paired = recomputed = stamped_only = 0

    for index, event in enumerate(events):
        if event.get("event") != "stage.banner":
            continue
        payload = event.get("payload") or {}
        if index == 0:
            problems.append("a stage banner was the first event, so it had no "
                            "content to describe")
            continue
        content = events[index - 1]
        cpay = content.get("payload") or {}

        # LEG 1
        if content.get("event") != payload.get("for_event"):
            problems.append(
                f"[{index}] banner names {payload.get('for_event')!r} but "
                f"follows {content.get('event')!r}: the banner is out of step "
                f"with the content it describes")
            continue
        if str(cpay.get("stage")) != str(payload.get("stage")):
            problems.append(
                f"[{index}] banner is for stage {payload.get('stage')!r} while "
                f"its content is stage {cpay.get('stage')!r}")
            continue
        paired += 1

        # LEG 2
        if cpay.get("banner") is not None and cpay["banner"] != payload.get("text"):
            problems.append(
                f"[{index}] the banner event says {payload.get('text')!r} and "
                f"the content it was stamped onto says {cpay['banner']!r}")

        # LEG 3
        name = str(content.get("event"))
        try:
            if name == "solve.frame":
                expected = banner_for(cpay)
            elif name.startswith("demo.") or name == "stage.begin":
                expected = banner_for_stage(cpay)
            else:
                stamped_only += 1
                continue
        except Exception as exc:                       # pragma: no cover
            problems.append(f"[{index}] the banner for {name} could not be "
                            f"recomputed: {type(exc).__name__}: {exc}")
            continue
        recomputed += 1
        if expected != payload.get("text"):
            problems.append(
                f"[{index}] banner {payload.get('text')!r} does not match the "
                f"banner recomputed from its own content, {expected!r}")

    return {"problems": problems, "paired": paired,
            "recomputed": recomputed, "stamped_only": stamped_only}


# ---------------------------------------------------------------------------
# Geometry bind
# ---------------------------------------------------------------------------

def check_geometry(events: list[dict]) -> dict:
    """The STL on screen IS the section the numbers came from.

    Three independent legs: the bytes (md5 of both copies), the shape (chord
    and slot-height ratio measured off the served file), and the wire (the
    name in the published geometry.ready address).
    """
    from workflows import _jf1_geometry as geo

    out: dict = {"problems": [], "md5": {}, "measured": {}}
    for path in GEOMETRY_COPIES:
        if not path.is_file():
            out["problems"].append(f"a declared copy of the served surface is "
                                   f"not on disk: {path}")
            continue
        digest = hashlib.md5(path.read_bytes()).hexdigest()
        out["md5"][str(path)] = digest
        if digest != GEOMETRY_MD5:
            out["problems"].append(
                f"{path} is md5 {digest}, declared {GEOMETRY_MD5}")

    served = geo.STAGING / SURFACE
    if served.is_file():
        chord, h_over_c = geo.measure_blown_slot(served)
        out["measured"] = {"chord_m": float(chord), "h_over_c": float(h_over_c)}
        tol = float(geo.SOLVED_GEOMETRY_TOL)
        if abs(chord - SOLVED_CHORD_M) > tol:
            out["problems"].append(
                f"served chord {chord:.6f} m is not the solved chord "
                f"{SOLVED_CHORD_M:.6f} m within {tol}")
        if abs(h_over_c - SOLVED_H_OVER_C) > tol:
            out["problems"].append(
                f"served h/c {h_over_c:.6f} is not the solved h/c "
                f"{SOLVED_H_OVER_C:.6f} within {tol}")
        out["is_solved_section"] = bool(geo.is_solved_section(SURFACE))
        if not out["is_solved_section"]:
            out["problems"].append("the act's own bind test says the served "
                                   "surface is not the solved section")

    urls = [str((e.get("payload") or {}).get("url") or "")
            for e in events if e.get("event") == "geometry.ready"]
    out["announced_urls"] = urls
    if len(urls) != 1:
        out["problems"].append(f"{len(urls)} geometry announcements, expected 1")
    elif SURFACE not in urls[0]:
        out["problems"].append(
            f"the announced surface address does not name {SURFACE}: {urls[0]}")
    return out


# ---------------------------------------------------------------------------
# The caption row, as DATA
# ---------------------------------------------------------------------------

def caption_report(events: list[dict]) -> dict:
    """WHICH figures carry a caption on the wire, and what it says.

    THIS IS A READING, NOT A VERDICT. The caption row is
    ``#viewportCaption``; ``control_room.html`` fills it from the ``caption``
    key of a ``geometry.ready`` or ``field.ready`` payload (lines 734, 1765,
    1782) and collapses the row with ``.viewport-caption:empty`` (line 242).

    NOTHING ON THIS BOX EXECUTES CSS LAYOUT. This harness can say what text is
    on the wire and what is absent from it. It CANNOT say the row collapsed,
    that the text wrapped, or that anything is legible. Those are
    REQUIRES A HUMAN EYE ON A REAL BROWSER and are reported that way.
    """
    rows = []
    for index, event in enumerate(events):
        name = str(event.get("event") or "")
        if name not in {"geometry.ready", "field.ready", "plot.ready"}:
            continue
        payload = event.get("payload") or {}
        rows.append({
            "index": index,
            "event": name,
            "title_or_label": payload.get("title") or payload.get("label") or "",
            "file": payload.get("file") or payload.get("url") or "",
            "caption": payload.get("caption"),
        })
    with_caption = [r for r in rows if r["caption"]]
    return {"rows": rows, "with_caption": len(with_caption),
            "without_caption": len(rows) - len(with_caption)}


# ---------------------------------------------------------------------------
# THE PLANTS -- rule 3. Each derived by hand, one per alternative.
# ---------------------------------------------------------------------------
#
# Every plant carries the marker its refusal MUST quote. Asserting only "it
# raised" is how a plant passes for the wrong reason: a sentence written to
# test the gate vocabulary that happens to contain a banned register word
# would raise, prove nothing, and read as green.

#: One per alternative of demo_mode._GATE_PHRASES. Written out longhand and
#: deliberately inflected where English inflects, because a word-boundary
#: check is blind to every inflection of every word in it and this lab has
#: paid for that twice.
GATE_PLANTS = (
    # "PASS" -> "PASSED". THE measured instance: four planted-control lines
    # rendered on a filmed gates table as "... control PASSED" and walked
    # through a \bPASS\b check untouched.
    ("PASS", "Coefficient control PASSED", "the gate word 'PASS'"),
    ("BLOCKED", "The lane is BLOCKED", "the gate word 'BLOCKED'"),
    # The standalone-label form: the whole string IS the word.
    ("PENDING", "PENDING", "the gate word 'PENDING'"),
    # Multi-word, plural inflection on the final word.
    ("NOT A RESULT", "These rows are NOT A RESULTS",
     "the gate word 'NOT A RESULT'"),
    # Multi-word, title case: the gate word wearing a hat.
    ("GATE REACHED", "Gate Reached on the second rung", "'GATE REACHED'"),
    ("GATE FAIL", "The sweep GATE FAILS at the top",
     "the gate word 'GATE FAIL'"),
)

#: One per remaining rule the sweep claims to enforce. Also longhand.
CLASS_PLANTS = (
    ("case id", "The JF1_L1_BLOWN_CMU020_A0 point moved",
     "JF1_L1_BLOWN_CMU020_A0"),
    ("lesson id", "Recorded against L-425 in the notes", "L-425"),
    ("docket id", "Recorded against D438 in the notes", "D438"),
    ("tier word", "This is a tier 2 answer", "tier 2"),
    ("blocked-gpu", "The rung is BLOCKED-GPU today", "BLOCKED-GPU"),
    ("pre-registration", "The pre-registration fixed the threshold",
     "pre-registration"),
    ("process id", "Worker pid 3491 finished", "pid 3491"),
    ("port number", "The service answered on port 8765", "port 8765"),
    ("commit hash", "Recorded at commit a2a72dd2 today", "a2a72dd2"),
    ("filesystem path",
     "Written to /home/ubuntu/Certonomous/verification/runs/JF/lift.csv",
     "a path is never on screen"),
    ("finer companion grid, outside the caveat box",
     "Flow picture from a finer companion grid", "finer companion grid"),
)


def plant_language(events: list[dict]) -> list[str]:
    """Plant a forbidden string where the sweep reads, and read it back.

    ONE PLANT PER COPY. Planting all sixteen into one list would let a single
    detection stand in for sixteen, which is exactly the arithmetic that lets
    a blind alternative hide behind a sighted one.

    The plant goes into ``stage.banner.text`` -- a key this harness's rendered
    list actually reads and the banner's only prose field -- so it exercises
    the sweep's real path rather than a side door.

    Returns the plants that were INVISIBLE. Any entry means exit 2.
    """
    host = None
    for index, event in enumerate(events):
        if event.get("event") == "stage.banner":
            host = index
            break
    if host is None:
        _refuse("no stage.banner event to plant into; the sweep cannot be "
                "shown able to see anything, so its clean result is not "
                "evidence")

    invisible: list[str] = []
    for label, text, marker in GATE_PLANTS + CLASS_PLANTS:
        salted = copy.deepcopy(events)
        salted[host]["payload"]["text"] = text
        found = sweep_language(salted)
        hits = [v for v in found
                if v["index"] == host and v["key"].endswith(".text")]
        if not hits:
            invisible.append(f"{label}: {text!r} was planted at "
                             f"stage.banner.text and the sweep did not see it")
            continue
        if not any(marker in v["reason"] for v in hits):
            # It raised, but not for the reason the plant tests. A plant that
            # passes for the wrong reason proves nothing about the rule it was
            # written for.
            invisible.append(
                f"{label}: {text!r} was refused, but not by the rule it tests "
                f"(expected the refusal to quote {marker!r}); got "
                f"{hits[0]['reason'][:160]!r}")
    return invisible


def plant_order(events: list[dict], stages: tuple[str, ...]) -> list[str]:
    """Four wrong orders, one per way an order can be wrong. Read them back."""
    begins = [i for i, e in enumerate(events) if e.get("event") == "stage.begin"]
    if len(begins) < 3:
        _refuse("fewer than three stage.begin events to mutate; the ordering "
                "check cannot be shown able to see a wrong order")

    invisible: list[str] = []

    # (a) two stages swapped.
    swapped = copy.deepcopy(events)
    first, second = begins[0], begins[1]
    swapped[first]["payload"]["stage"], swapped[second]["payload"]["stage"] = (
        swapped[second]["payload"]["stage"], swapped[first]["payload"]["stage"])
    if not check_order(swapped, stages):
        invisible.append("two stage.begin events were swapped and the "
                         "ordering check reported no problem")

    # (b) one stage never begun.
    dropped = copy.deepcopy(events)
    del dropped[begins[len(begins) // 2]]
    if not check_order(dropped, stages):
        invisible.append("a stage.begin event was deleted and the ordering "
                         "check reported no problem")

    # (c) a stage begun twice, at the end, where first-appearance dedupe hides
    #     it. This is the alternative a deduped check is blind to, so it is
    #     planted explicitly.
    doubled = copy.deepcopy(events)
    doubled.append(copy.deepcopy(events[begins[3]]))
    if not check_order(doubled, stages):
        invisible.append("a stage was begun a second time after the walk "
                         "finished and the ordering check reported no problem")

    # (d) a stage the sequencer does not have.
    renamed = copy.deepcopy(events)
    renamed[begins[2]]["payload"]["stage"] = "postprocessing"
    if not check_order(renamed, stages):
        invisible.append("a stage.begin was renamed to a stage that does not "
                         "exist and the ordering check reported no problem")

    return invisible


def plant_banner_sync(events: list[dict]) -> list[str]:
    """Two desynchronisations, read back. Any invisible one is exit 2."""
    banners = [i for i, e in enumerate(events)
               if e.get("event") == "stage.banner"]
    if len(banners) < 2:
        _refuse("fewer than two banners to desynchronise")
    invisible: list[str] = []

    # (a) a banner running BEHIND its content: it still names the previous
    #     event. Mutating `for_event` is the honest way to say "this banner
    #     belongs to a different tick".
    behind = copy.deepcopy(events)
    behind[banners[-1]]["payload"]["for_event"] = "demo.prompt"
    behind[banners[-1]]["payload"]["stage"] = "prompt"
    if not check_banner_sync(behind)["problems"]:
        invisible.append("a banner was re-pointed at another stage's content "
                         "and the sync check reported no problem")

    # (b) a banner whose TEXT drifted from the content it was stamped onto:
    #     the drift that a banner set on stage entry would produce. Chosen by
    #     hand as another stage's real banner, not as nonsense, because
    #     nonsense would also be caught by a check that only tested for
    #     emptiness.
    drifted = copy.deepcopy(events)
    target = banners[-1]
    drifted[target]["payload"]["text"] = "meshing"
    if not check_banner_sync(drifted)["problems"]:
        invisible.append("a banner's text was replaced with another stage's "
                         "banner and the sync check reported no problem")

    return invisible


def plant_counters(events: list[dict]) -> list[str]:
    """Show the counters can read the legacy shape as well as this one."""
    invisible: list[str] = []
    stripped = [e for e in events
                if e.get("event") not in {"stage.banner", "solve.frame"}]
    tell = check_legacy_tell(stripped)
    if tell is None:
        invisible.append("every banner and frame was removed and the "
                         "legacy-path detector still reported nothing")
    if check_legacy_tell(events) is not None:
        invisible.append("the legacy-path detector fires on the real stream, "
                         "so a clean reading from it would mean nothing")
    return invisible


def run_all_plants(events: list[dict], stages: tuple[str, ...]) -> None:
    """Every plant, before any verdict. Refuses rather than degrading."""
    invisible: list[str] = []
    invisible += plant_language(events)
    invisible += plant_order(events, stages)
    invisible += plant_banner_sync(events)
    invisible += plant_counters(events)
    if invisible:
        _refuse("PLANTED CONTROLS INVISIBLE, so no clean result from this "
                "harness is evidence:\n  - " + "\n  - ".join(invisible))


# ---------------------------------------------------------------------------
# Collection: offline
# ---------------------------------------------------------------------------

def collect_offline() -> tuple[list[dict], dict]:
    """Drive the act in process and collect what it published.

    NOT through the server, and nothing is bound. The transcript is built the
    way ``make_act_entry`` builds it, because the meshing, gates and results
    stages publish their tables ONLY when a script exists; driving with
    ``script=None`` would silently lose all three tables and make the count
    look like a different defect.
    """
    from workflows import make_transcript
    from workflows.demo_sequencer import run_act
    import workflows.jet_flap_act  # noqa: F401  (importing REGISTERS the act)

    collected: list[dict] = []

    def emit(name, payload):
        collected.append({"sequence": len(collected) + 1,
                          "event": str(name),
                          "payload": _jsonable(payload)})

    script = make_transcript("jet-flap", emit)
    started = time.time()
    record = run_act(ACT_KEY, emit=emit, script=script,
                     typed_prompt=GOAL, sleep=lambda _s: None)
    return collected, {"seconds": round(time.time() - started, 2),
                       "sequencer_emitted": record.get("emitted"),
                       "stages_returned": sorted(record.get("stages", {}))}


def _jsonable(payload):
    """A payload as the live path would serialise it, with a refusal if it
    cannot be. The bus writes events.jsonl with json.dumps and no default, so
    a payload carrying a Path would crash the live run; catching it here makes
    that a finding offline rather than a mission failure on camera."""
    try:
        return json.loads(json.dumps(payload))
    except (TypeError, ValueError) as exc:
        _refuse(f"a published payload is not JSON-serialisable, so the live "
                f"event log could not be written: {type(exc).__name__}: {exc}")


# ---------------------------------------------------------------------------
# Collection: live
# ---------------------------------------------------------------------------

def _get_json(url: str, timeout: float = 30.0):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _post_json(url: str, body: dict, timeout: float = 30.0):
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def collect_live(base: str, timeout_s: float, state_dir: Path
                 ) -> tuple[list[dict], dict]:
    """POST the prompt, wait for the mission, and read its events back.

    BOTH READERS ARE USED AND CROSS-CHECKED. ``events.json`` is what the page
    reads; ``<id>.events.jsonl`` is what survives a restart. If the two
    disagree the harness says so rather than picking one, because a
    disagreement between them is itself the finding.
    """
    launch = _post_json(f"{base}/api/missions",
                        {"goal": GOAL, "surface": SURFACE})
    mission_id = launch["mission_id"]
    route = launch.get("route") or {}

    deadline = time.time() + timeout_s
    state = launch.get("state")
    detail: dict = {}
    while time.time() < deadline:
        detail = _get_json(f"{base}/api/missions/{mission_id}")
        state = detail.get("state")
        if state in {"complete", "failed", "incomplete"}:
            break
        time.sleep(2.0)

    payload = _get_json(f"{base}/api/missions/{mission_id}/events.json")
    over_http = [{"sequence": e["sequence"], "event": e["event"],
                  "payload": e.get("payload") or {}}
                 for e in payload.get("events", [])]

    on_disk: list[dict] = []
    log = state_dir / f"{mission_id}.events.jsonl"
    if log.is_file():
        for line in log.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            on_disk.append({"sequence": raw["sequence"], "event": raw["event"],
                            "payload": raw.get("payload") or {}})

    disagreement = None
    if on_disk:
        if len(on_disk) != len(over_http):
            disagreement = (f"the event log holds {len(on_disk)} events and "
                            f"the API returned {len(over_http)}")
        else:
            for a, b in zip(on_disk, over_http):
                if a["event"] != b["event"]:
                    disagreement = (f"sequence {a['sequence']}: log says "
                                    f"{a['event']!r}, API says {b['event']!r}")
                    break
    else:
        disagreement = f"no event log found at {log}"

    return over_http, {
        "mission_id": mission_id,
        "state": state,
        "error": detail.get("error"),
        "route_intent": route.get("intent"),
        "route_confidence": route.get("confidence"),
        "events_log": str(log),
        "log_events": len(on_disk),
        "reader_disagreement": disagreement,
    }


def live_credentials(base: str) -> list[dict]:
    return _get_json(f"{base}/api/credentials")


def offline_credentials() -> list[dict]:
    from chief_engineer import server

    return server._credentials()


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def route_offline() -> dict:
    from chief_engineer.router import WORKFLOWS, apply_surface, classify

    route = apply_surface(classify(GOAL), SURFACE)
    return {"intent": route.intent, "confidence": route.confidence,
            "workflow": WORKFLOWS.get(route.intent)}


def check_prompt_verbatim() -> list[str]:
    """The prompt this harness POSTs IS the act's own registered prompt."""
    from workflows.jet_flap_act import PROMPT

    if PROMPT != GOAL:
        return [f"the act's registered prompt and the prompt this harness "
                f"sends differ; one of them has been reworded.\n"
                f"    act:     {PROMPT!r}\n    harness: {GOAL!r}"]
    return []


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def report(events, meta, mode, credentials, stages) -> int:
    counts = count_events(events)
    failures: list[str] = []
    lines: list[str] = []

    def say(text=""):
        lines.append(text)

    say(f"JET-FLAP LIVE PASS  --  mode: {mode}")
    say("=" * 72)

    # -- 1. routing --------------------------------------------------------
    say()
    say("1. PROMPT AND ROUTING")
    for problem in check_prompt_verbatim():
        failures.append(problem)
        say(f"   GATE FAIL  {problem}")
    if mode == "live":
        intent = meta.get("route_intent")
        confidence = meta.get("route_confidence")
        say(f"   mission          {meta.get('mission_id')}  state={meta.get('state')}")
        if meta.get("error"):
            failures.append(f"the mission failed: {meta['error']}")
            say(f"   GATE FAIL  mission error: {meta['error']}")
    else:
        route = route_offline()
        intent, confidence = route["intent"], route["confidence"]
        say(f"   workflow module  {(route['workflow'] or {}).get('module')}")
    say(f"   routed intent    {intent}")
    say(f"   confidence       {confidence}")
    if intent != EXPECTED_INTENT:
        failures.append(f"routed intent is {intent!r}, expected "
                        f"{EXPECTED_INTENT!r}")
        say(f"   GATE FAIL  expected intent {EXPECTED_INTENT!r}")
    say("   prompt sent verbatim, matched against the act's own constant")

    # -- 2. counts ---------------------------------------------------------
    say()
    say("2. EVENT CENSUS")
    tell = check_legacy_tell(events)
    if tell:
        failures.append(f"LEGACY PATH: {tell}")
        say(f"   GATE FAIL  {tell}")
        say("   This is the hard NO-GO. The old flat surface is wired, not "
            "the act.")
    envelope = [e for e in events
                if str(e.get("event")) in SERVER_ENVELOPE]
    act_events = [e for e in events
                  if str(e.get("event")) not in SERVER_ENVELOPE]
    say(f"   wire total                    {len(events):>6}")
    say(f"   the server's mission envelope {len(envelope):>6}   "
        f"{sorted(count_events(envelope))}")
    say(f"   the act's own census          {len(act_events):>6}   "
        f"(gated below; mode-invariant)")
    say()
    measured = {
        "total": len(act_events),
        "stage.banner": counts.get("stage.banner", 0),
        "solve.frame": counts.get("solve.frame", 0),
        "transcript.table": counts.get("transcript.table", 0),
        "stage.begin": counts.get("stage.begin", 0),
    }
    for key, want in EXPECT.items():
        got = measured[key]
        flag = "ok " if got == want else "OFF"
        if got != want:
            failures.append(f"{key}: {got}, expected {want}")
        say(f"   {flag}  {key:<20} {got:>6}   expected {want}")
    say()
    say("   full census:")
    for name in sorted(counts, key=lambda n: (-counts[n], n)):
        say(f"      {counts[name]:>6}  {name}")

    # -- 3. stage order ----------------------------------------------------
    say()
    say("3. STAGE ORDER")
    raw = stage_begins(events)
    say(f"   stage-begins, in order   {raw}")
    say(f"   distinct, in order       {distinct_in_order(raw)}")
    problems = check_order(events, stages)
    for problem in problems:
        failures.append(problem)
        say(f"   GATE FAIL  {problem}")
    if not problems:
        say(f"   ok   nine stage-begins, in the sequencer's own order")

    # -- 4. language sweep -------------------------------------------------
    say()
    say("4. LANGUAGE SWEEP OVER RENDERED FIELDS")
    swept = 0
    for event in events:
        swept += sum(1 for _ in _rendered_strings(event))
    violations = sweep_language(events)
    naive = sweep_all_strings(events)
    check, contract_error = _language_checker()
    for where, text in PAGE_FIXED_STRINGS:
        try:
            check(text, zone="screen")
        except contract_error as exc:
            failures.append(f"page-fixed text: {where}: {exc}")
            say(f"   GATE FAIL  page-fixed text at {where}: {exc}")
    say(f"   page-fixed strings swept {len(PAGE_FIXED_STRINGS)} "
        f"(text the page adds, not the act)")
    say(f"   rendered strings swept   {swept}")
    say(f"   violations               {len(violations)}")
    say(f"   (diagnostic) a naive walk of EVERY string would report "
        f"{len(naive)},")
    say(f"   which is the machine-identifier false-positive count, not a "
        f"finding.")
    for violation in violations:
        failures.append(f"language: [{violation['index']}] "
                        f"{violation['key']}: {violation['reason']}")
        say(f"   GATE FAIL  [{violation['index']}] {violation['key']}")
        say(f"              {violation['reason']}")
    if naive and not violations:
        say("   the excluded keys, by class:")
        classes: dict[str, int] = {}
        for item in naive:
            leaf = item["key"].rsplit(".", 1)[-1]
            classes[leaf] = classes.get(leaf, 0) + 1
        for leaf in sorted(classes, key=lambda k: -classes[k]):
            say(f"      {classes[leaf]:>4}  ...{leaf}")

    # -- 5. banner sync ----------------------------------------------------
    say()
    say("5. BANNER / CONTENT SYNCHRONISATION")
    sync = check_banner_sync(events)
    say(f"   banners paired with the content of their own tick   "
        f"{sync['paired']}")
    say(f"   banners independently recomputed from that content  "
        f"{sync['recomputed']}")
    say(f"   banners tested by pairing and stamp only            "
        f"{sync['stamped_only']}")
    say("   (the last group derive their banner from a state dictionary that")
    say("    is not published, so no independent recomputation exists)")
    for problem in sync["problems"]:
        failures.append(f"banner sync: {problem}")
        say(f"   GATE FAIL  {problem}")

    # -- 6. geometry -------------------------------------------------------
    say()
    say("6. GEOMETRY BIND")
    geometry = check_geometry(events)
    for path, digest in geometry["md5"].items():
        say(f"   md5 {digest}  {path}")
    if geometry.get("measured"):
        say(f"   chord    {geometry['measured']['chord_m']:.6f} m")
        say(f"   h/c      {geometry['measured']['h_over_c']:.6f}")
    say(f"   announced address(es)  {geometry['announced_urls']}")
    for problem in geometry["problems"]:
        failures.append(f"geometry: {problem}")
        say(f"   GATE FAIL  {problem}")
    if not geometry["problems"]:
        say("   ok   the served surface is the solved section, by bytes and "
            "by shape")

    # -- 7. captions -------------------------------------------------------
    say()
    say("7. THE CAPTION ROW  --  DATA ONLY")
    captions = caption_report(events)
    say(f"   figure/surface announcements  {len(captions['rows'])}")
    say(f"   carrying a caption            {captions['with_caption']}")
    say(f"   carrying none                 {captions['without_caption']}")
    for row in captions["rows"]:
        mark = "caption" if row["caption"] else "NO CAPTION"
        say(f"      [{row['index']:>5}] {row['event']:<15} {mark:<11} "
            f"{row['title_or_label']!r}")
        if row["caption"]:
            say(f"              {row['caption']!r}")
    say()
    say("   REQUIRES A HUMAN EYE ON A REAL BROWSER:")
    say("     - whether .viewport-caption:empty actually collapses the row")
    say("     - whether any caption text wraps, truncates or overlaps")
    say("   No harness on this box executes CSS layout. Nothing above is a")
    say("   claim about what the row LOOKS like; it is what is on the wire.")

    # -- 8. the wall -------------------------------------------------------
    say()
    say("8. THE CURATED CREDENTIALS WALL, IN SERVED ORDER")
    if credentials is None:
        say("   not read")
    else:
        for position, card in enumerate(credentials, start=1):
            say(f"   {position}. {card.get('name')}  "
                f"[{card.get('tier')}]  measured={card.get('measured')}")
        say(f"   {len(credentials)} cards")

    # -- meta --------------------------------------------------------------
    say()
    say("9. COLLECTION")
    for key in sorted(meta):
        say(f"   {key:<22} {meta[key]}")
    if meta.get("reader_disagreement"):
        failures.append(f"readers disagree: {meta['reader_disagreement']}")
        say(f"   GATE FAIL  the two event readers disagree")

    say()
    say("=" * 72)
    if failures:
        say(f"VERDICT: GATE FAIL  --  {len(failures)} finding(s)")
        for failure in failures:
            say(f"   - {failure}")
    else:
        say("VERDICT: PASS  --  every check green, every check planted first")
    print("\n".join(lines))
    return 1 if failures else 0


# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--offline", action="store_true",
                        help="drive the act in process; bind nothing")
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--timeout", type=float, default=900.0,
                        help="seconds to wait for the live mission")
    parser.add_argument("--state-dir",
                        default=str(SDK / "chief-engineer-runs" /
                                    "mission-state"),
                        help="where the server writes <id>.events.jsonl")
    parser.add_argument("--dump", default=None,
                        help="write the collected events to this path")
    args = parser.parse_args(argv)

    try:
        from workflows.demo_mode import STAGES
    except Exception as exc:
        print(f"REFUSED: the demo-mode contract could not be imported, so "
              f"this harness does not know what order to expect: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    stages = tuple(STAGES)
    if stages != STAGES_LITERAL:
        print(f"REFUSED: the sequencer's stage list is {stages}, and this "
              f"harness was written against {STAGES_LITERAL}. Re-read the "
              f"sequencer before believing any ordering result.",
              file=sys.stderr)
        return 2

    try:
        if args.offline:
            events, meta = collect_offline()
            credentials = offline_credentials()
            mode = "offline (in process, nothing bound)"
        else:
            events, meta = collect_live(args.base_url, args.timeout,
                                        Path(args.state_dir))
            credentials = live_credentials(args.base_url)
            mode = f"live ({args.base_url})"
    except urllib.error.URLError as exc:
        print(f"REFUSED: no server answered at {args.base_url}: {exc}. This "
              f"harness never starts one.", file=sys.stderr)
        return 2
    except HarnessRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    if args.dump:
        Path(args.dump).write_text(
            "\n".join(json.dumps(e, separators=(",", ":")) for e in events),
            encoding="utf-8")

    # RULE 3, BEFORE ANY VERDICT. Nothing green is printed until every reader
    # has been shown able to see a non-zero.
    try:
        run_all_plants(events, stages)
    except HarnessRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    print(f"[planted controls] {len(GATE_PLANTS) + len(CLASS_PLANTS)} language "
          f"plants, 4 ordering plants, 2 banner-sync plants, 2 counter plants: "
          f"all visible.")
    print()
    return report(events, meta, mode, credentials, stages)


if __name__ == "__main__":
    raise SystemExit(main())
