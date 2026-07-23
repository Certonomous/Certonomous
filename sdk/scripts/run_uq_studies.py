"""Overnight UQ study batch: refinement ladders and closure trios, for real.

Every number stored by this runner comes from an actual solve (OpenFOAM in
WSL, VSPAERO for the airliner anchors) or a real evaluation of the actual
model under study (valve quadrature and correlation family). Studies
checkpoint per level, so a crash loses nothing.

    python scripts/run_uq_studies.py naca4412_ladder
    python scripts/run_uq_studies.py motorbike_closures
    python scripts/run_uq_studies.py airliner valve
    python scripts/run_uq_studies.py all          # Sanaa's sequencing

Sequencing (per the orders): naca4412 + motorBike first (ladder then
closures), B-52 next, airliner anchors, valve last.
"""
from __future__ import annotations

import json
import math
import re
import shutil
import sys
import time
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer import uq                                    # noqa: E402
from chief_engineer.head_engineer import FOAM_TUTORIALS, HeadEngineer  # noqa: E402

REPO = SDK.parent
GEOMETRY_DIR = SDK / "geometry"
CURRICULUM = REPO / "models" / "curriculum"
OUT = REPO / "mission-output" / "uq-studies"
# The finalist VSPAERO anchors live in the primary repo's mission output even
# when this runner executes from a worktree.
PRIMARY_MISSION_OUTPUT = Path(
    "C:/Users/mouza/github-cleanup/Certonomous/mission-output")

ITERATIONS = 300
CLOSURES = ("kOmegaSST", "kEpsilon", "SpalartAllmaras")


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _registry():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "curriculum_registry", CURRICULUM / "registry.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _checkpoint(body: str, **fields) -> dict:
    study = uq.load_study(body) or {"body": body}
    study.update(fields)
    uq.save_study(body, study)
    return study


# --------------------------------------------------------------------------
# Unfamiliar-path ladders (geometry-study chain, refinement 1/2/3)
# --------------------------------------------------------------------------

def _run_geometry_study(surface: str, refinement: int, tag: str,
                        extra_params: dict | None = None) -> dict:
    """One headless geometry-study run; returns {cells, cd, mission}."""
    from workflows.geometry_study import main as geometry_main

    captured: dict[str, dict] = {}

    def emit(event: str, payload) -> None:
        if event in ("result.verdict", "mesh.stats", "report.ready"):
            captured[event] = payload

    label = Path(surface).stem
    # The mesh cache is keyed by body label only; a ladder MUST NOT reuse a
    # different rung's mesh, so the entry is cleared before each rung. The
    # final (fine) rung leaves its mesh cached for the closure trio.
    HeadEngineer(f"uq-clear-{label}", OUT / "tmp").clear_mesh_cache(label)
    code = geometry_main(
        request=f"UQ refinement ladder rung {tag}: mesh and solve {label}.",
        params={"surface": surface, "refinement": refinement,
                **(extra_params or {})},
        iterations=ITERATIONS, emit=emit)
    if code != 0:
        raise RuntimeError(f"{tag}: geometry study exited {code}")
    verdict = captured.get("result.verdict", {})
    stats = captured.get("mesh.stats", {})
    cd = float(verdict.get("value"))
    cells = int(stats.get("cells", 0))
    if not cells:
        raise RuntimeError(f"{tag}: no mesh stats captured")
    return {"cells": cells, "cd": cd, "mission": f"uq-{tag}",
            "refinement": refinement}


def ladder_unfamiliar(body: str, stl_name: str, *,
                      refinements=(2, 3, 4), velocity: float = 100.0) -> None:
    """Three distinct meshes need refinement >= 2: the case builder floors its
    surface level at 2, so rungs 1 and 2 are the same mesh (the degenerate
    ladder the first batch produced). The act runs refinement 3, so the act
    mesh is the MIDDLE rung and its band is the middle-level GCI."""
    registry = _registry()
    src = registry.stl_path(body) if hasattr(registry, "stl_path") else None
    if src and Path(src).exists() and not (GEOMETRY_DIR / stl_name).exists():
        shutil.copy(src, GEOMETRY_DIR / stl_name)
    hints = registry.solve_hints(body) or {}
    extra = {k: v for k, v in hints.items() if k in
             ("streamwise_axis", "reference_length", "velocity")}

    study = uq.load_study(body) or {}
    levels = {int(lv["refinement"]): lv for lv in study.get("levels", [])}
    for r in refinements:
        if r in levels:
            _log(f"{body} rung r={r} already done (cells {levels[r]['cells']})")
            continue
        _log(f"{body} ladder rung refinement={r} starting")
        began = time.time()
        level = _run_geometry_study(stl_name, r, f"{body}-r{r}", extra)
        level["wall_minutes"] = round((time.time() - began) / 60, 1)
        levels[r] = level
        _checkpoint(body, levels=[levels[k] for k in sorted(levels)])
        _log(f"{body} rung r={r}: cells {level['cells']:,}, "
             f"Cd {level['cd']:.4f}, {level['wall_minutes']} min")
    ordered = [levels[k] for k in sorted(levels)]
    band = uq.ladder_band([lv["cells"] for lv in ordered],
                          [lv["cd"] for lv in ordered])
    # The act solves at refinement 3. When the ladder's fine rung is coarser
    # or finer than that, the band reported for the act mesh is the middle-
    # level GCI (Celik's GCI_med), and the method note says so.
    act_refinement = 3
    act_level = levels.get(act_refinement, ordered[-1])
    use_middle = (band.get("band_abs_middle") is not None
                  and ordered[-1]["refinement"] != act_refinement)
    band_abs = band["band_abs_middle"] if use_middle else band["band_abs"]
    method = band["method"] + (
        "; band for the working mesh (middle level)" if use_middle else "")
    rel = band_abs / abs(act_level["cd"]) if act_level.get("cd") else None
    fingerprint = uq.setup_fingerprint(
        body=body, solver="openfoam-simpleFoam", closure="kOmegaSST",
        velocity=velocity, refinement=act_refinement, iterations=ITERATIONS)
    _checkpoint(
        body, fingerprint=fingerprint,
        numerical={"band_abs": band_abs,
                   "band_rel": None if rel is None else round(rel, 5),
                   "observed_order": band["observed_order"],
                   "method": method, "conclusive": band["conclusive"],
                   "value_working": act_level.get("cd")},
        provenance=[lv["mission"] for lv in ordered])
    _log(f"{body} ladder DONE: {method}, band {band_abs:.4g}")


# --------------------------------------------------------------------------
# motorBike ladder (tutorial case, snappy levels 3-4 / 4-5 / 5-6)
# --------------------------------------------------------------------------

_MB_RUNGS = (  # (tag, feature level, surface levels, region level)
    ("coarse", 4, "(3 4)", 2),
    ("mid", 5, "(4 5)", 3),
    ("fine", 6, "(5 6)", 4),
)


def _motorbike_case(engineer: HeadEngineer) -> None:
    engineer.stage_case(f"{FOAM_TUTORIALS}/incompressible/simpleFoam/motorBike")
    geometry = GEOMETRY_DIR / "motorBike.obj"
    wsl = str(geometry).replace("C:", "/mnt/c").replace("\\", "/")
    engineer.intake_geometry(wsl, "motorBike.obj")
    engineer.set_iteration_count(ITERATIONS)


def _motorbike_solve(engineer: HeadEngineer, *, mesh: bool,
                     feature=None, surface=None, region=None) -> dict:
    if mesh:
        if feature is not None:
            engineer._wsl(
                f"cd {engineer.remote_case} && "
                f"sed -i 's/level (5 6);/level {surface};/' system/snappyHexMeshDict && "
                f"sed -i 's/level 6;/level {feature};/' system/snappyHexMeshDict && "
                f"sed -i 's/levels ((1E15 4));/levels ((1E15 {region}));/' system/snappyHexMeshDict")
        for step, command in (("surfaceFeatureExtract", "surfaceFeatureExtract"),
                              ("blockMesh", "blockMesh"),
                              ("snappyHexMesh", "snappyHexMesh -overwrite")):
            engineer._run_step(step, command, 7200)
    engineer._wsl(f"cd {engineer.remote_case} && rm -rf 0 && cp -r 0.orig 0")
    engineer._run_step("potentialFoam", "potentialFoam -writephi", 3600)
    engineer._run_step("simpleFoam", "simpleFoam", 7200)
    stats = engineer.collect_mesh_stats()
    results = engineer.postprocess(("Cd", "Cl"))
    return {"cells": int(stats.get("cells", 0)),
            "cd": float(results["Cd"]["value"])}


def ladder_motorbike() -> None:
    body = "motorBike"
    study = uq.load_study(body) or {}
    levels = {lv["tag"]: lv for lv in study.get("levels", [])}
    for tag, feature, surface, region in _MB_RUNGS:
        if tag in levels:
            _log(f"motorBike rung {tag} already done")
            continue
        _log(f"motorBike ladder rung {tag} starting")
        began = time.time()
        engineer = HeadEngineer(f"uq-mb-{tag}", OUT / f"mb-{tag}")
        _motorbike_case(engineer)
        level = _motorbike_solve(engineer, mesh=True, feature=feature,
                                 surface=surface, region=region)
        if tag == "fine":
            engineer.save_mesh_to_cache("uq-motorBike-fine")
        level.update(tag=tag, mission=f"uq-motorBike-{tag}",
                     wall_minutes=round((time.time() - began) / 60, 1))
        levels[tag] = level
        _checkpoint(body, levels=[levels[t] for t, *_ in _MB_RUNGS if t in levels])
        _log(f"motorBike {tag}: cells {level['cells']:,}, Cd {level['cd']:.4f}, "
             f"{level['wall_minutes']} min")
    ordered = [levels[t] for t, *_ in _MB_RUNGS]
    band = uq.ladder_band([lv["cells"] for lv in ordered],
                          [lv["cd"] for lv in ordered])
    fine = ordered[-1]
    rel = band["band_abs"] / abs(fine["cd"]) if fine["cd"] else None
    fingerprint = uq.setup_fingerprint(
        body=body, solver="openfoam-simpleFoam", closure="kOmegaSST",
        velocity=20.0, refinement="tutorial-5-6", iterations=ITERATIONS)
    _checkpoint(
        body, fingerprint=fingerprint,
        numerical={"band_abs": band["band_abs"],
                   "band_rel": None if rel is None else round(rel, 5),
                   "observed_order": band["observed_order"],
                   "method": band["method"], "conclusive": band["conclusive"],
                   "value_fine": fine["cd"]},
        provenance=[lv["mission"] for lv in ordered])
    _log(f"motorBike ladder DONE: {band['method']}, band {band['band_abs']:.4g}")


# --------------------------------------------------------------------------
# Closure trios (same fine mesh, three closures) — Q2a
# --------------------------------------------------------------------------

def _derive_epsilon(omega_text: str, eps_value: float) -> str:
    text = omega_text
    text = re.sub(r"object\s+omega\s*;", "object      epsilon;", text)
    text = re.sub(r"dimensions\s+\[[^\]]*\]\s*;",
                  "dimensions      [0 2 -3 0 0 0 0];", text)
    text = text.replace("omegaWallFunction", "epsilonWallFunction")
    text = re.sub(r"uniform\s+[0-9eE.+-]+", f"uniform {eps_value:.6g}", text)
    return text


def _derive_nutilda(omega_text: str, ntl_value: float) -> str:
    text = omega_text
    text = re.sub(r"object\s+omega\s*;", "object      nuTilda;", text)
    text = re.sub(r"dimensions\s+\[[^\]]*\]\s*;",
                  "dimensions      [0 2 -1 0 0 0 0];", text)
    # Wall-function blocks become plain no-slip-consistent fixed values.
    text = text.replace("omegaWallFunction", "fixedValue")
    text = re.sub(r"uniform\s+[0-9eE.+-]+", f"uniform {ntl_value:.6g}", text)
    return text


def _closure_files(engineer: HeadEngineer, closure: str, *,
                   k: float, nu: float, length: float) -> None:
    """Patch a staged case (fields in 0/) to run under ``closure``."""
    case = engineer.remote_case
    if closure == "kOmegaSST":
        return
    omega_text = engineer._wsl(f"cat {case}/0/omega").stdout
    staging = OUT / "closure-fields"
    staging.mkdir(parents=True, exist_ok=True)
    if closure == "kEpsilon":
        eps = 0.09 ** 0.75 * max(k, 1e-8) ** 1.5 / (0.1 * length)
        (staging / "epsilon").write_text(_derive_epsilon(omega_text, eps),
                                         newline="\n")
        wsl_staging = str(staging / "epsilon").replace("C:", "/mnt/c").replace("\\", "/")
        engineer._wsl(f"cp '{wsl_staging}' {case}/0/epsilon")
        engineer._wsl(f"sed -i 's/kOmegaSST/kEpsilon/' {case}/constant/turbulenceProperties")
    elif closure == "SpalartAllmaras":
        ntl = 4.0 * nu
        (staging / "nuTilda").write_text(_derive_nutilda(omega_text, ntl),
                                         newline="\n")
        wsl_staging = str(staging / "nuTilda").replace("C:", "/mnt/c").replace("\\", "/")
        engineer._wsl(f"cp '{wsl_staging}' {case}/0/nuTilda")
        engineer._wsl(f"sed -i 's/kOmegaSST/SpalartAllmaras/' {case}/constant/turbulenceProperties")
        engineer._wsl(f"sed -i 's/nutkWallFunction/nutUSpaldingWallFunction/' {case}/0/nut")
    # simpleFoam needs solver entries for the new fields; reuse the k/omega
    # smoothSolver group by widening its selector.
    engineer._wsl(
        f"sed -i 's/\"(U|k|omega)\"/\"(U|k|omega|epsilon|nuTilda)\"/' {case}/system/fvSolution || true")
    engineer._wsl(
        f"grep -q 'div(phi,epsilon)' {case}/system/fvSchemes || "
        f"sed -i 's#div(phi,omega)\\(.*\\)#div(phi,omega)\\1\\n    div(phi,epsilon)\\1\\n    div(phi,nuTilda)\\1#' {case}/system/fvSchemes")


def closures_motorbike() -> None:
    body = "motorBike"
    study = uq.load_study(body) or {}
    fine = None
    for lv in study.get("levels", []):
        if lv.get("tag") == "fine":
            fine = lv
    if not fine:
        raise RuntimeError("motorBike closures need the fine ladder rung first")
    members = dict(study.get("closures", {}))
    members["kOmegaSST"] = fine["cd"]
    for closure in ("kEpsilon", "SpalartAllmaras"):
        if closure in members:
            _log(f"motorBike closure {closure} already done")
            continue
        _log(f"motorBike closure {closure} starting")
        began = time.time()
        engineer = HeadEngineer(f"uq-mbc-{closure}", OUT / f"mbc-{closure}")
        _motorbike_case(engineer)
        if not engineer.restore_cached_mesh("uq-motorBike-fine"):
            raise RuntimeError("fine mesh cache missing")
        engineer._wsl(f"cd {engineer.remote_case} && rm -rf 0 && cp -r 0.orig 0")
        _closure_files(engineer, closure, k=0.24, nu=1.5e-5, length=2.0)
        engineer._run_step("potentialFoam", "potentialFoam -writephi", 3600)
        engineer._run_step("simpleFoam", "simpleFoam", 7200)
        results = engineer.postprocess(("Cd", "Cl"))
        members[closure] = float(results["Cd"]["value"])
        _checkpoint(body, closures=members)
        _log(f"motorBike {closure}: Cd {members[closure]:.4f} "
             f"({round((time.time()-began)/60, 1)} min)")
    spread = uq.spread_estimate(
        members, label="inter-closure spread (screening estimate)")
    _checkpoint(body, model={"band_abs": spread["band_abs"],
                             "method": spread["method"],
                             "members": spread["members"],
                             "screening_estimate": True})
    _log(f"motorBike closures DONE: spread {spread['band_abs']:.4g}")


def closures_unfamiliar(body: str, stl_name: str, *,
                        velocity: float = 100.0) -> None:
    """Closure trio for a build_case body on its cached fine mesh."""
    from chief_engineer.external_aero import analyse_surface, build_case

    study = uq.load_study(body) or {}
    levels = study.get("levels", [])
    if len(levels) < 3:
        raise RuntimeError(f"{body} closures need the completed ladder first")
    fine = levels[-1]
    members = dict(study.get("closures", {}))
    members["kOmegaSST"] = fine["cd"]

    registry = _registry()
    hints = registry.solve_hints(body) or {}
    axis = hints.get("streamwise_axis")
    source = GEOMETRY_DIR / stl_name
    geometry = analyse_surface(
        source, streamwise_axis=int(axis) if axis is not None else None)
    for closure in ("kEpsilon", "SpalartAllmaras"):
        if closure in members:
            _log(f"{body} closure {closure} already done")
            continue
        _log(f"{body} closure {closure} starting")
        began = time.time()
        engineer = HeadEngineer(f"uq-{body}-{closure}", OUT / f"{body}-{closure}")
        case_dir = Path(engineer.out_root) / "case"
        reference = build_case(case_dir, stl_name, geometry,
                               velocity=velocity, refinement=3,
                               iterations=ITERATIONS)
        shutil.copy(source, case_dir / "constant" / "triSurface" / stl_name)
        wsl_case = str(case_dir).replace("C:", "/mnt/c").replace("\\", "/")
        engineer._wsl(f"rm -rf {engineer.remote_case} && "
                      f"cp -r '{wsl_case}' {engineer.remote_case}")
        if not engineer.restore_cached_mesh(body):
            raise RuntimeError(f"{body} fine mesh cache missing; re-run the ladder")
        nu = 1.5e-5
        k = 1.5 * (velocity * 0.01) ** 2
        _closure_files(engineer, closure, k=k, nu=nu,
                       length=reference["length"])
        engineer._run_step("potentialFoam", "potentialFoam -writephi", 3600)
        engineer._run_step("simpleFoam", "simpleFoam", 7200)
        results = engineer.postprocess(("Cd", "Cl"))
        members[closure] = float(results["Cd"]["value"])
        _checkpoint(body, closures=members)
        _log(f"{body} {closure}: Cd {members[closure]:.4f} "
             f"({round((time.time()-began)/60, 1)} min)")
    spread = uq.spread_estimate(
        members, label="inter-closure spread (screening estimate)")
    _checkpoint(body, model={"band_abs": spread["band_abs"],
                             "method": spread["method"],
                             "members": spread["members"],
                             "screening_estimate": True})
    _log(f"{body} closures DONE: spread {spread['band_abs']:.4g}")


# --------------------------------------------------------------------------
# Airliner anchors (Q2b) — no new solves, deviations at the solved anchors
# --------------------------------------------------------------------------

def airliner_anchors() -> None:
    from workflows.aircraft_optimization import (_CD0_NONWING,
                                                 evaluate_design,
                                                 parse_requirements)

    body = "airliner-wing"
    anchor_dir = PRIMARY_MISSION_OUTPUT / "aircraft-optimization" / "vspaero"
    reqs = parse_requirements(
        "300 passengers, 6000 km range, take-off at 85 m/s, landing at 72 m/s")
    deviations: dict[str, float] = {}
    for result_path in sorted(anchor_dir.glob("wing-*/result.json")):
        try:
            data = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        matched = data.get("matched") or {}
        built = data.get("built") or {}
        if not matched or matched.get("cdi") is None:
            continue
        span = round(float(built.get("span", 0)), 3)
        area = round(float(built.get("area", 0)), 2)
        if not span or not area:
            continue
        screened = evaluate_design(span, area, 27.5, reqs)
        solved_ld = matched["cl"] / (_CD0_NONWING + matched["cdo_wing"]
                                     + matched["cdi"])
        deviations[f"span{span:g}-area{area:g}"] = screened["L_D"] - solved_ld
    if len(deviations) < 2:
        _log("airliner: not enough solved anchors on disk; study pending")
        return
    magnitudes = [abs(v) for v in deviations.values()]
    band = max(magnitudes)
    fingerprint = uq.setup_fingerprint(
        body=body, solver="vspaero", closure="vortex-lattice",
        velocity=230.0, refinement=None, iterations=None)
    _checkpoint(
        body, fingerprint=fingerprint,
        model={"band_abs": round(band, 3),
               "method": "model-form vs solver anchors",
               "members": {k: round(v, 3) for k, v in deviations.items()},
               "screening_estimate": True},
        provenance=[p.parent.name for p in
                    sorted(anchor_dir.glob("wing-*/result.json"))])
    _log(f"airliner anchors DONE: {len(deviations)} anchors, "
         f"max |dL/D| {band:.3f}")


# --------------------------------------------------------------------------
# Valve (Q1 analog + Q2c) — quadrature ladder + correlation family
# --------------------------------------------------------------------------

def valve_studies() -> None:
    valve_dir = CURRICULUM / "aortic_valve"
    if str(valve_dir) not in sys.path:
        sys.path.insert(0, str(valve_dir))
    from waveform import Q_PEAK, T_CYCLE, RHO_BLOOD          # noqa: E402
    from generate_valve import effective_orifice_area        # noqa: E402

    body = "aortic-valve"
    angle = 80.0
    area = effective_orifice_area(angle)
    systole = T_CYCLE / 3.0          # half-sine ejection window

    def cycle_loss(k: int, cd: float) -> float:
        """k-segment quadrature of the half-sine ejection, mirroring the
        act's exact construction: flows sampled at segment MIDPOINTS,
        weighted by each segment's stroke-volume fraction. k = 3 reproduces
        the act's phase_points() to machine precision."""
        total = 0.0
        raw = [(math.cos(math.pi * i / k) - math.cos(math.pi * (i + 1) / k))
               / math.pi for i in range(k)]
        weights = [r / sum(raw) for r in raw]
        for i in range(k):
            tau_mid = (i + 0.5) / k
            q = Q_PEAK * math.sin(math.pi * tau_mid)
            v = q / max(cd * area, 1e-9)
            total += weights[i] * 0.5 * RHO_BLOOD * v * v
        return total

    # Quadrature ladder: the numerical channel of the screen is the cycle
    # quadrature, refined k = 3 / 5 / 9 on the same waveform and model.
    k_levels = (3, 5, 9)
    values = [cycle_loss(k, 0.62) for k in k_levels]
    spread = max(values) - min(values)
    fine = values[-1]
    numerical = {
        "band_abs": round(abs(values[-1] - values[0]), 1),
        "band_rel": round(abs(values[-1] - values[0]) / fine, 5),
        "method": f"phase-quadrature ladder k = {'/'.join(map(str, k_levels))}",
        "values": {str(k): round(v, 1) for k, v in zip(k_levels, values)},
        "conclusive": True,
    }
    # Correlation family: recognized sharp-orifice discharge coefficients.
    family_cd = {
        "ISO 5167 orifice plate (C ~ 0.60)": 0.60,
        "Idelchik, Handbook of Hydraulic Resistance (0.61)": 0.61,
        "classic sharp-edge orifice (0.62)": 0.62,
        "upper sharp-orifice literature value (0.65)": 0.65,
    }
    family_dp = {name: cycle_loss(3, cd) for name, cd in family_cd.items()}
    model = uq.spread_estimate(family_dp, label="correlation-family spread")
    fingerprint = uq.setup_fingerprint(
        body=body, solver="reduced-order-orifice", closure="orifice-correlation",
        velocity=None, refinement=3, iterations=None)
    _checkpoint(
        body, fingerprint=fingerprint,
        numerical=numerical,
        model={"band_abs": round(model["band_abs"], 1),
               "method": model["method"],
               "members": {k: round(v, 1) for k, v in model["members"].items()},
               "screening_estimate": True,
               "unmodeled": ["phase-interaction neglected",
                             "leaflet motion not modeled",
                             "Newtonian blood"]},
        provenance=["valve-quadrature-ladder", "orifice-correlation-family"])
    _log(f"valve DONE: quadrature band {numerical['band_abs']} Pa, "
         f"family spread {model['band_abs']:.0f} Pa "
         f"(k=3 loss {values[0]:.0f} Pa)")


# --------------------------------------------------------------------------
# Entry
# --------------------------------------------------------------------------

STAGES = {
    "naca4412_ladder": lambda: ladder_unfamiliar("naca4412_wing", "naca4412_wing.stl"),
    "naca4412_closures": lambda: closures_unfamiliar("naca4412_wing", "naca4412_wing.stl"),
    "motorbike_ladder": ladder_motorbike,
    "motorbike_closures": closures_motorbike,
    "b52_ladder": lambda: ladder_unfamiliar("b52", "b52.stl"),
    "b52_closures": lambda: closures_unfamiliar("b52", "b52.stl"),
    "airliner": airliner_anchors,
    "valve": valve_studies,
}
SEQUENCE = ("naca4412_ladder", "naca4412_closures", "motorbike_ladder",
            "motorbike_closures", "b52_ladder", "b52_closures",
            "airliner", "valve")


def main(argv: list[str]) -> int:
    stages = argv or ["all"]
    if stages == ["all"]:
        stages = list(SEQUENCE)
    failures = 0
    for stage in stages:
        runner = STAGES.get(stage)
        if runner is None:
            _log(f"unknown stage {stage!r}; choices: {', '.join(STAGES)}")
            return 2
        try:
            runner()
        except Exception as exc:
            failures += 1
            _log(f"STAGE FAILED {stage}: {type(exc).__name__}: {exc}")
    _log(f"batch finished, {failures} failed stage(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
