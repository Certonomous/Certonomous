"""The per-mission event stream the control room reads from.

Every mission owns one :class:`EventBus`. Workflows publish typed events to it as
they run; the HTTP layer both replays the backlog (``snapshot``) and tails it
live (``stream``). Publishing is serialised under a condition variable so the
SSE readers wake the instant a new event lands, and — when a bus is given a file
path — each event is appended to a JSON-lines log so a restarted server can still
replay a finished mission.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Condition
from typing import Iterator


@dataclass(frozen=True)
class MissionEvent:
    """One published fact about a mission, numbered in publication order."""

    sequence: int
    timestamp: float
    event: str
    mission_id: str
    payload: dict

    def as_dict(self) -> dict:
        return {
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "event": self.event,
            "mission_id": self.mission_id,
            "payload": self.payload,
        }


class EventBus:
    """An append-only, thread-safe log of a single mission's events."""

    def __init__(self, mission_id: str, persist_path: str | Path | None = None):
        self.mission_id = mission_id
        self._log: list[MissionEvent] = []
        self._gate = Condition()
        self._closed = False
        self._persist_path = Path(persist_path) if persist_path else None
        self._rehydrate()

    # -- state ---------------------------------------------------------------
    @property
    def closed(self) -> bool:
        return self._closed

    def _rehydrate(self) -> None:
        """Reload a persisted backlog so a restarted server can replay it."""
        path = self._persist_path
        if not path or not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                self._log.append(MissionEvent(
                    int(raw["sequence"]),
                    float(raw["timestamp"]),
                    str(raw["event"]),
                    str(raw.get("mission_id", self.mission_id)),
                    dict(raw.get("payload", {})),
                ))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue

    # -- writing -------------------------------------------------------------
    def publish(self, event: str, payload: dict | None = None) -> MissionEvent:
        with self._gate:
            record = MissionEvent(
                sequence=len(self._log) + 1,
                timestamp=time.time(),
                event=event,
                mission_id=self.mission_id,
                payload=payload or {},
            )
            self._log.append(record)
            self._append_to_disk(record)
            self._gate.notify_all()
            return record

    def _append_to_disk(self, record: MissionEvent) -> None:
        path = self._persist_path
        if not path:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.as_dict(), separators=(",", ":")) + "\n")

    def close(self) -> None:
        with self._gate:
            self._closed = True
            self._gate.notify_all()

    # -- reading -------------------------------------------------------------
    def snapshot(self, after: int = 0) -> list[MissionEvent]:
        """Every event published after sequence ``after`` (a point-in-time copy)."""
        with self._gate:
            return [event for event in self._log if event.sequence > after]

    def stream(self, after: int = 0, heartbeat_s: float = 10.0
               ) -> Iterator[MissionEvent | None]:
        """Yield events past ``after`` as they arrive; ``None`` marks a heartbeat.

        Returns once the bus is closed and the caller has seen every event.
        """
        cursor = after
        while True:
            with self._gate:
                pending = [event for event in self._log if event.sequence > cursor]
                if not pending and not self._closed:
                    self._gate.wait(timeout=heartbeat_s)
                    pending = [event for event in self._log if event.sequence > cursor]
                if not pending:
                    if self._closed:
                        return
                    yield None
                    continue
            for event in pending:
                cursor = event.sequence
                yield event
