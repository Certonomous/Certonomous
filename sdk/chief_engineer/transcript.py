"""On-record mission transcript shared by every Certonomous role.

Each entry names the role that spoke, what it decided, and which knowledge or
lesson entry it cited.  The transcript is the demo's audit trail: nothing a
chief claims on screen is unattributed, and every citation resolves to a real
file in this repository.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

CHIEF_ENGINEER = "CHIEF ENGINEER"
CHIEF_RESEARCHER = "CHIEF RESEARCHER"
NUMERICIST = "NUMERICIST"
MONITOR = "MONITOR"
SYSTEM = "SYSTEM"

ROLE_ORDER = (SYSTEM, CHIEF_ENGINEER, CHIEF_RESEARCHER, NUMERICIST, MONITOR)


@dataclass
class Entry:
    role: str
    message: str
    citations: tuple[str, ...] = ()
    data: dict[str, Any] = field(default_factory=dict)
    at: float = field(default_factory=time.time)

    def as_dict(self) -> dict[str, Any]:
        from .citations import display_all

        return {
            "role": self.role,
            "message": self.message,
            # Raw file references stay for the audit trail; the interface
            # renders `citations_display` so no path ever reaches the screen.
            "citations": list(self.citations),
            "citations_display": display_all(self.citations),
            "data": dict(self.data),
            "at": self.at,
        }

    def render(self) -> str:
        cited = f"  [cites: {', '.join(self.citations)}]" if self.citations else ""
        return f"{self.role}: {self.message}{cited}"


class Transcript:
    """Ordered, printable, serializable record of a mission's decisions."""

    def __init__(self, mission: str, *, echo: Callable[[str], None] | None = print,
                 sink: Callable[[Entry], None] | None = None):
        self.mission = mission
        self.entries: list[Entry] = []
        self.echo = echo
        # A sink lets the control room stream the same entries the terminal
        # prints, so both surfaces show one identical record.
        self.sink = sink

    def say(self, role: str, message: str, *,
            citations: Iterable[str] = (), **data) -> Entry:
        entry = Entry(role, message, tuple(citations), dict(data))
        self.entries.append(entry)
        if self.echo:
            self.echo(entry.render())
        if self.sink:
            self.sink(entry)
        return entry

    def engineer(self, message: str, **kwargs) -> Entry:
        return self.say(CHIEF_ENGINEER, message, **kwargs)

    def researcher(self, message: str, **kwargs) -> Entry:
        return self.say(CHIEF_RESEARCHER, message, **kwargs)

    def numericist(self, message: str, **kwargs) -> Entry:
        return self.say(NUMERICIST, message, **kwargs)

    def monitor(self, message: str, **kwargs) -> Entry:
        return self.say(MONITOR, message, **kwargs)

    def system(self, message: str, **kwargs) -> Entry:
        return self.say(SYSTEM, message, **kwargs)

    def phase(self, name: str, headline: str = "") -> Entry:
        """Open a section of the study: hypothesis, plan, evidence, conclusion."""
        entry = Entry("PHASE", headline or name, (), {"phase": name})
        self.entries.append(entry)
        if self.echo:
            self.echo(f"== {name.upper()} ==" + (f" {headline}" if headline else ""))
        if self.sink:
            self.sink(entry)
        return entry

    def citations(self) -> list[str]:
        seen: list[str] = []
        for entry in self.entries:
            for citation in entry.citations:
                if citation not in seen:
                    seen.append(citation)
        return seen

    def render(self) -> str:
        header = f"=== Certonomous mission transcript — {self.mission} ==="
        return "\n".join([header, *(entry.render() for entry in self.entries)])

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render() + "\n", encoding="utf-8", errors="replace")
        return path
