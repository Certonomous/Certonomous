"""Mission debrief: the lab reads its own transcript and keeps one lesson.

After a mission finishes, Claude is handed the transcript and asked for ONE
grounded operating lesson: what worked, what stayed uncertain, and what to
investigate next. The lesson is prose only. It is discarded outright if it
carries any number the transcript does not, so the model can never introduce
or revise a measured value; what survives lands in the learned-lessons record
(``lessons.record_learned``) with the mission id as its citation, where
ask-the-lab retrieval grounds on it like any other record source.

Everything here runs off the mission's critical path: :func:`debrief_async`
spawns a daemon thread and swallows every failure, so mission completion is
never blocked and a Claude outage changes nothing but the absence of a lesson.
"""

from __future__ import annotations

import re
import threading

from . import claude_lab
from .lessons import record_learned

_NUMBER = re.compile(r"[-+]?\d+(?:[.,]\d+)*(?:[eE][-+]?\d+)?")
_MAX_TRANSCRIPT_CHARS = 24000

SYSTEM_PROMPT = (
    "You are the chief engineer of Certonomous, an autonomous aerodynamics "
    "laboratory, writing the debrief note after a mission. You receive the "
    "mission transcript. Write exactly ONE operating lesson for the lab's "
    "record: what worked, what stayed uncertain, and what to investigate "
    "next.\n"
    "Hard rules:\n"
    "- Ground every claim in the transcript. Never introduce a number, body, "
    "or result the transcript does not contain, and quote any number you use "
    "verbatim.\n"
    "- The lesson is working guidance in prose; it never restates a measured "
    "value as a new finding and never revises one.\n"
    "- Never describe any result as cached, stored, saved, or pre-computed.\n"
    "- Two to four sentences, one paragraph. No preamble, no markdown, no "
    "headings, no em dashes (use commas).\n"
    "Reply with the lesson only."
)


def transcript_lines(events) -> list[str]:
    """Pull the spoken transcript out of a mission's event snapshot.

    Accepts either :class:`chief_engineer.events.MissionEvent` objects or
    their ``as_dict`` form, so the caller can hand over whatever it holds.
    """
    lines: list[str] = []
    for event in events or ():
        data = event.as_dict() if hasattr(event, "as_dict") else dict(event)
        if data.get("event") != "transcript.entry":
            continue
        payload = data.get("payload") or {}
        role = str(payload.get("role", "")).strip()
        message = str(payload.get("message", "")).strip()
        if message:
            lines.append(f"{role}: {message}" if role else message)
    return lines


def _numbers_grounded(source: str, lesson: str) -> bool:
    """Every numeric token in the lesson must appear verbatim in the source."""
    return all(token in source for token in _NUMBER.findall(lesson))


def compose(mission_id: str, request: str, status: str,
            lines: list[str]) -> str | None:
    """One lesson from the transcript, or None when there is nothing safe."""
    if not lines:
        return None
    body = "\n".join(lines)[-_MAX_TRANSCRIPT_CHARS:]
    user = (f"Mission {mission_id} finished as {status or 'unknown'}.\n"
            f"REQUEST: {request}\n\nTRANSCRIPT:\n{body}")
    lesson = claude_lab.complete(SYSTEM_PROMPT, user,
                                 max_tokens=1000, effort="medium")
    if not lesson:
        return None
    lesson = lesson.replace("—", ",").replace("\n", " ").strip()
    if not lesson or not _numbers_grounded(user, lesson):
        return None
    return lesson


def run(mission_id: str, request: str, status: str, events) -> dict | None:
    """The full debrief, synchronously: compose the lesson and record it."""
    try:
        lesson = compose(mission_id, request, status, transcript_lines(events))
        if not lesson:
            return None
        return record_learned(mission_id, lesson)
    except Exception:
        return None


def debrief_async(mission_id: str, request: str, status: str, events) -> None:
    """Debrief on a daemon thread; never blocks or raises into the mission."""
    try:
        if not claude_lab.enabled():
            return
        snapshot = list(events or ())
        threading.Thread(
            target=run, args=(mission_id, request, status, snapshot),
            daemon=True, name=f"debrief-{mission_id}").start()
    except Exception:
        pass
