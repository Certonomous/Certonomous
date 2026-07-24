"""Operating lessons, and how a chief puts one into its own words.

A lesson recited verbatim reads like a string constant, because that is what
it would be.  What a practitioner actually does is *apply* the rule: name the
situation in front of them, and let the standing practice show through the way
they describe it.

:func:`express` composes that sentence from the lesson's content plus the
numbers of the moment.  The structural form is chosen from the measured values
themselves, so two runs with different ensembles genuinely read differently
while carrying the same rule — and the lesson identifier travels alongside as
a chip the interface can expand, rather than being read aloud.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Lesson:
    id: str
    rule: str
    full: str
    added: str = ""

    def chip(self) -> dict[str, str]:
        return {"id": self.id, "rule": self.rule, "full": self.full}


LESSONS: dict[str, Lesson] = {
    "L-001": Lesson(
        id="L-001",
        rule="reduce sampling uncertainty until only the irreducible remains",
        full=(
            "When epistemic uncertainty on a metric is high, spend additional "
            "samples in the flagged thin directions until the remaining "
            "uncertainty is irreducible. Sampling is currently the only "
            "reduction lever; further targeting methods will be added, but "
            "reducible uncertainty must never be reported as final."),
        added="2026-07-20",
    ),
}


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def express(lesson_id: str, **context: Any) -> str:
    """Say what the lesson requires, in this situation, in the chief's voice."""
    lesson = LESSONS.get(lesson_id)
    if lesson is None:
        return ""

    metric = context.get("metric", "this quantity")
    relative = float(context.get("relative", 0.0))
    threshold = float(context.get("threshold", 0.01))
    current_n = int(context.get("current_n", 0))
    proposed_n = int(context.get("proposed_n", 0))
    shrink = (1 - (current_n / proposed_n) ** 0.5) * 100 if proposed_n > current_n > 0 else 0.0

    forms = [
        (f"At {_percent(relative)} the error bar on {metric} is still mine rather than "
         f"the flow's — it is sampling noise, and standing practice is to keep buying "
         f"samples while that is true. {proposed_n} runs should take roughly "
         f"{shrink:.0f}% off it."),
        (f"That spread is dominated by how little I have sampled, not by the physics: "
         f"{_percent(relative)} against a {_percent(threshold)} threshold. We hold to "
         f"spending samples until what is left is genuinely irreducible, so I am "
         f"taking this to {proposed_n}."),
        (f"{_percent(relative)} on {metric} is reducible — {current_n} samples is simply "
         f"too few to pin the mean down. The practice I work to is that an envelope "
         f"stays open while sampling can still close it, so {proposed_n} runs next "
         f"(about {shrink:.0f}% tighter)."),
        (f"I would not report {metric} at {_percent(relative)} yet. That number is the "
         f"estimator's own noise, and the rule we operate under is to spend samples "
         f"against it until only the physical spread is left standing. Going to "
         f"{proposed_n}."),
        (f"The envelope is {_percent(relative)} wide and almost all of that is sampling "
         f"error I can pay to remove. Practice here is unambiguous: keep sampling while "
         f"the uncertainty is still reducible. {proposed_n} runs, expected "
         f"{shrink:.0f}% improvement."),
    ]

    # The measured values choose the form, so different ensembles read
    # differently while the rule underneath stays fixed.
    seed = int(round(relative * 1e6)) + current_n * 31 + proposed_n * 7
    return forms[seed % len(forms)]


def chip(lesson_id: str) -> dict[str, str]:
    lesson = LESSONS.get(lesson_id)
    return lesson.chip() if lesson else {}


# --------------------------------------------------------------------------
# Lessons the lab earns from its own missions
# --------------------------------------------------------------------------
#
# The static LESSONS above are the standing practice the lab shipped with.
# Learned lessons are the ones the debrief loop writes after each mission:
# one grounded paragraph per mission, kept on disk alongside the mission
# state and cited by the mission id that earned it. Ask-the-lab retrieval
# reads them back as first-class record sources.


def _learned_root() -> Path:
    override = os.environ.get("CERTONOMOUS_LESSONS_DIR")
    if override:
        return Path(override)
    workdir = Path(os.environ.get("CHIEF_ENGINEER_WORKDIR", "./chief-engineer-runs"))
    state = Path(os.environ.get(
        "CHIEF_ENGINEER_STATE_DIR", str(workdir.resolve() / "mission-state")))
    return state / "lessons"


def record_learned(mission_id: str, text: str) -> dict[str, str] | None:
    """Keep one mission-earned lesson, cited by the mission that taught it.

    Returns the record on success, None when there is nothing to keep or the
    write fails — the caller treats both quietly, a lesson is a bonus, never
    a dependency.
    """
    mission_id = (mission_id or "").strip()
    text = (text or "").strip()
    if not mission_id or not text:
        return None
    record = {"mission_id": mission_id, "text": text,
              "added": date.today().isoformat()}
    try:
        root = _learned_root()
        root.mkdir(parents=True, exist_ok=True)
        path = root / f"{mission_id}.json"
        staging = path.with_suffix(".json.tmp")
        staging.write_text(json.dumps(record, separators=(",", ":")),
                           encoding="utf-8")
        staging.replace(path)
    except OSError:
        return None
    return record


def learned_lessons() -> list[dict[str, str]]:
    """Every mission-earned lesson on disk, in mission-id order."""
    items: list[dict[str, str]] = []
    try:
        paths = sorted(_learned_root().glob("*.json"))
    except OSError:
        return items
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        mission_id = str(data.get("mission_id", "")).strip()
        text = str(data.get("text", "")).strip()
        if mission_id and text:
            items.append({"mission_id": mission_id, "text": text,
                          "added": str(data.get("added", ""))})
    return items
