"""Typed value objects shared across the lab.

Plain data records — an engineering domain, the specification of a tunable
parameter or a reported metric, a candidate design, and the result of evaluating
one. They carry no behaviour beyond the defaults declared here; the reasoning
that consumes them lives in the workflows and the lab.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, TypeAlias


class Domain(str, Enum):
    """The engineering domains a parameter or metric can belong to."""

    AERODYNAMICS = "aerodynamics"
    STABILITY = "stability"
    STRUCTURES = "structures"
    GEOMETRY = "geometry"


# A domain may be a known enum member or a free string, so an adapter can name a
# domain the core does not enumerate.
DomainName: TypeAlias = "str | Domain"


def domain_name(domain: DomainName) -> str:
    """Normalise a domain reference to its stable string identifier."""
    return domain.value if isinstance(domain, Domain) else str(domain)


@dataclass(frozen=True)
class ParameterSpec:
    """A tunable input: name, bounds, a relative step, and where it belongs."""

    name: str
    minimum: float
    maximum: float
    relative_step: float = 0.10
    unit: str = ""
    description: str = ""
    domains: tuple[DomainName, ...] = (Domain.GEOMETRY,)


@dataclass(frozen=True)
class MetricSpec:
    """A reported quantity: its name, the analysis that yields it, and how it is
    read — direction of improvement, human aliases, unit, owning domains."""

    name: str
    analysis: str
    default_direction: str = "min"
    aliases: tuple[str, ...] = ()
    unit: str = ""
    domains: tuple[DomainName, ...] = ()


@dataclass
class Candidate:
    """One proposed design point in a search."""

    id: str
    parent_id: str | None
    design: Mapping[str, float]
    proposed_by: DomainName
    rationale: str
    iteration: int


@dataclass
class Evaluation:
    """The outcome of running one candidate through a worker."""

    candidate_id: str
    worker_id: str
    metrics: dict[str, float] = field(default_factory=dict)
    feasible: bool = False
    violations: dict[str, float] = field(default_factory=dict)
    score: float = float("-inf")
    elapsed_s: float = 0.0
    error: str | None = None
    artifacts: list[dict[str, Any]] = field(default_factory=list)
