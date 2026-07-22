"""A registry of the solver adapters the lab can call.

Each adapter advertises a :class:`AdapterManifest` — the analyses it provides,
the parameters it accepts, the metrics it returns — and a factory that builds the
live :class:`SimulationApi` for a given worker handle. The registry lets the
control room list what the lab can do (``/api/capabilities``) and lets a single
multidisciplinary evaluation be fanned across whichever adapters own the
requested analyses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from .api import SimulationApi
from .fleet import VmHandle
from .models import MetricSpec, ParameterSpec, domain_name


@dataclass(frozen=True)
class AdapterManifest:
    """What one solver adapter offers, in a form the control room can render."""

    name: str
    version: str
    analyses: tuple[str, ...]
    input_parameters: tuple[str, ...]
    output_metrics: tuple[str, ...]
    artifact_types: tuple[str, ...] = ("design-state/json",)
    concurrency: str = "isolated-process"
    parameter_specs: tuple[ParameterSpec, ...] = ()
    metric_specs: tuple[MetricSpec, ...] = ()
    domain_dependencies: Mapping[str, tuple[str, ...]] | None = None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "analyses": list(self.analyses),
            "input_parameters": list(self.input_parameters),
            "output_metrics": list(self.output_metrics),
            "artifact_types": list(self.artifact_types),
            "concurrency": self.concurrency,
            "parameters": [self._parameter_dict(spec) for spec in self.parameter_specs],
            "metrics": [self._metric_dict(spec) for spec in self.metric_specs],
            "domain_dependencies": {
                str(domain): list(deps)
                for domain, deps in (self.domain_dependencies or {}).items()
            },
        }

    @staticmethod
    def _parameter_dict(spec: ParameterSpec) -> dict:
        return {
            "name": spec.name,
            "minimum": spec.minimum,
            "maximum": spec.maximum,
            "relative_step": spec.relative_step,
            "unit": spec.unit,
            "description": spec.description,
            "domains": [domain_name(d) for d in spec.domains],
        }

    @staticmethod
    def _metric_dict(spec: MetricSpec) -> dict:
        return {
            "name": spec.name,
            "analysis": spec.analysis,
            "default_direction": spec.default_direction,
            "aliases": list(spec.aliases),
            "unit": spec.unit,
            "domains": [domain_name(d) for d in spec.domains],
        }


AdapterFactory = Callable[[VmHandle], SimulationApi]


class SoftwareAdapterRegistry:
    """The set of registered adapters, keyed by name, plus derived views of them."""

    def __init__(self):
        self._entries: dict[str, tuple[AdapterManifest, AdapterFactory]] = {}

    def register(self, manifest: AdapterManifest, factory: AdapterFactory) -> None:
        if manifest.name in self._entries:
            raise ValueError(f"adapter {manifest.name!r} is already registered")
        self._entries[manifest.name] = (manifest, factory)

    def manifests(self) -> list[AdapterManifest]:
        return [manifest for manifest, _ in self._entries.values()]

    def factory_for(self, analysis: str) -> tuple[AdapterManifest, AdapterFactory]:
        for manifest, factory in self._entries.values():
            if analysis in manifest.analyses:
                return manifest, factory
        raise LookupError(f"no adapter provides analysis {analysis!r}")

    def parameter_specs(self) -> tuple[ParameterSpec, ...]:
        merged: dict[str, ParameterSpec] = {}
        for manifest, _ in self._entries.values():
            for spec in manifest.parameter_specs:
                merged[spec.name] = spec
        return tuple(merged.values())

    def metric_specs(self) -> tuple[MetricSpec, ...]:
        merged: dict[str, MetricSpec] = {}
        for manifest, _ in self._entries.values():
            for spec in manifest.metric_specs:
                merged[spec.name] = spec
        return tuple(merged.values())

    def domain_dependencies(self) -> dict[str, tuple[str, ...]]:
        merged: dict[str, list[str]] = {}
        for manifest, _ in self._entries.values():
            for domain, deps in (manifest.domain_dependencies or {}).items():
                bucket = merged.setdefault(str(domain), [])
                for dep in deps:
                    if dep not in bucket:
                        bucket.append(str(dep))
        return {domain: tuple(deps) for domain, deps in merged.items()}

    def domain_parameter_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for spec in self.parameter_specs():
            for domain in spec.domains:
                key = domain_name(domain)
                counts[key] = counts.get(key, 0) + 1
        return counts

    def composite_factory(self) -> AdapterFactory:
        return lambda handle: CompositeSimulationApi(self, handle)


class CompositeSimulationApi:
    """Fan one multidisciplinary evaluation across the adapters that own each analysis."""

    def __init__(self, registry: SoftwareAdapterRegistry, handle: VmHandle):
        self.registry = registry
        self.handle = handle
        self._live: list[SimulationApi] = []
        self._progress_sink = None

    def set_progress_sink(self, sink) -> None:
        self._progress_sink = sink

    def evaluate(self, design: Mapping[str, float],
                 analyses: Sequence[str]) -> Mapping[str, float]:
        # Group requested analyses by the adapter that provides them, so each
        # adapter is built once even when it covers several analyses.
        by_adapter: dict[str, tuple[AdapterFactory, list[str]]] = {}
        for analysis in analyses:
            manifest, factory = self.registry.factory_for(analysis)
            by_adapter.setdefault(manifest.name, (factory, []))[1].append(analysis)

        metrics: dict[str, float] = {}
        for factory, adapter_analyses in by_adapter.values():
            adapter = factory(self.handle)
            self._live.append(adapter)
            setter = getattr(adapter, "set_progress_sink", None)
            if callable(setter):
                setter(self._progress_sink)
            produced = adapter.evaluate(design, adapter_analyses)
            clash = set(metrics).intersection(produced)
            if clash:
                raise RuntimeError(f"adapters returned overlapping metrics: {sorted(clash)}")
            metrics.update({k: float(v) for k, v in produced.items()})
        return metrics

    def artifacts(self) -> list[dict]:
        collected: list[dict] = []
        for adapter in self._live:
            reader = getattr(adapter, "artifacts", None)
            if callable(reader):
                collected.extend(reader())
        return collected

    def close(self) -> None:
        for adapter in reversed(self._live):
            adapter.close()
        self._live.clear()


def synthetic_registry(factory: AdapterFactory) -> SoftwareAdapterRegistry:
    """A registry with a single synthetic flight-physics adapter, for development."""
    registry = SoftwareAdapterRegistry()
    registry.register(
        AdapterManifest(
            name="synthetic-flight-physics",
            version="1.0",
            analyses=("geometry", "aerodynamics", "stability", "structures"),
            input_parameters=(
                "wing_span", "wing_sweep", "wing_taper", "wing_twist",
                "htail_span", "htail_area", "htail_arm", "cg_shift", "skin_thickness",
            ),
            output_metrics=("L_D", "CL", "CD", "static_margin", "mass", "wing_span"),
            concurrency="thread-safe",
        ),
        factory,
    )
    return registry
