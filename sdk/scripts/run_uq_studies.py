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
        try:
            level = _run_geometry_study(stl_name, r, f"{body}-r{r}", extra)
        except Exception as exc:
            # A crashed rung must not lose the study: finalize honestly with
            # whatever distinct levels exist (Q5 rails handle the shortfall).
            _log(f"{body} rung r={r} FAILED ({type(exc).__name__}: {exc}); "
                 f"finalizing with completed levels")
            break
        level["wall_minutes"] = round((time.time() - began) / 60, 1)
        levels[r] = level
        _checkpoint(body, levels=[levels[k] for k in sorted(levels)])
        _log(f"{body} rung r={r}: cells {level['cells']:,}, "
             f"Cd {level['cd']:.4f}, {level['wall_minutes']} min")
    ordered = [levels[k] for k in sorted(levels)]
    # dim=3 is stated, not defaulted: every body on this path is a closed
    # STL meshed by snappyHexMesh, refining in all three directions. The fit
    # refuses an unstated dimensionality, so the assumption is on the record.
    band = uq.ladder_band([lv["cells"] for lv in ordered],
                          [lv["cd"] for lv in ordered], dim=3)
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
    # The fingerprint must key the setup the rungs ACTUALLY solved: the
    # registry's velocity hint (passed through extra) wins over the default,
    # exactly as it did inside the geometry runs themselves. Keying the
    # default while solving the hint was the NACA 4412 mismatch bug.
    fingerprint = uq.setup_fingerprint(
        body=body, solver="openfoam-simpleFoam", closure="kOmegaSST",
        velocity=float(extra.get("velocity", velocity)),
        refinement=act_refinement, iterations=ITERATIONS)
    _checkpoint(
        body, fingerprint=fingerprint,
        # The fit is copied wholesale (uq.study_numerical); only what the
        # fit cannot know is added here. The old hand-typed key list dropped
        # every field the fit learned to record after the list was written --
        # the dimensionality, the monotone flag, the extrapolated value, the
        # guard record -- without saying so.
        numerical=uq.study_numerical(
            band,
            band_abs=band_abs,
            band_rel=None if rel is None else round(rel, 5),
            method=method,
            value_working=act_level.get("cd")),
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
    # dim=3: the motorBike tutorial mesh is a three-dimensional
    # snappyHexMesh case and its snappy levels refine in all three.
    band = uq.ladder_band([lv["cells"] for lv in ordered],
                          [lv["cd"] for lv in ordered], dim=3)
    fine = ordered[-1]
    rel = band["band_abs"] / abs(fine["cd"]) if fine["cd"] else None
    fingerprint = uq.setup_fingerprint(
        body=body, solver="openfoam-simpleFoam", closure="kOmegaSST",
        velocity=20.0, refinement="tutorial-5-6", iterations=ITERATIONS)
    _checkpoint(
        body, fingerprint=fingerprint,
        # `value_working`, not the `value_fine` this writer used to spell it:
        # `transferred_model_band` pools stored studies by reading
        # `value_working`, so a study written under the other spelling dropped
        # out of the pool without anything saying it had.
        numerical=uq.study_numerical(
            band,
            band_rel=None if rel is None else round(rel, 5),
            value_working=fine["cd"]),
        provenance=[lv["mission"] for lv in ordered])
    _log(f"motorBike ladder DONE: {band['method']}, band {band['band_abs']:.4g}")


# --------------------------------------------------------------------------
# Closure trios (same fine mesh, three closures) — Q2a
# --------------------------------------------------------------------------

def _strip_named_blocks(text: str, names: tuple[str, ...]) -> str:
    """Remove named dict blocks (and bare #include lines) from a FOAM dict.

    foamDictionary rewrites controlDict with includes expanded inline, so the
    diagnostics appear as full named blocks; removing only their header line
    orphans the braces. This walks brace depth and drops each whole block.
    """
    out: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        token = stripped.rstrip("{").strip()
        if any(f'#include "{n}"' in stripped for n in names):
            i += 1
            continue
        if token in names:
            # Skip the header, then the block from its opening brace to close.
            depth = 0
            j = i + (0 if "{" in stripped else 1)
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                j += 1
                if depth <= 0 and j > i + 1:
                    break
            i = j
            continue
        # foamDictionary may also leave ANONYMOUS expanded blocks whose type
        # line names the diagnostic; detect "{ ... type streamLine; }".
        if stripped == "{":
            depth, j, body = 0, i, []
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                body.append(lines[j])
                j += 1
                if depth <= 0:
                    break
            first = body[1].strip() if len(body) > 1 else ""
            blob = "\n".join(body)
            diag_types = tuple({n, n[:-1] if n.endswith("s") else n}
                               for n in names)
            if first.startswith("type") and any(
                    re.search(rf"type\s+{t};", blob)
                    for group in diag_types for t in group):
                i = j
                continue
        out.append(line)
        i += 1
    return "\n".join(out)


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
    # simpleFoam needs solver, scheme, and relaxation entries for the new
    # fields. Two dict styles exist: generated cases use a quoted
    # "(U|k|omega)" selector; the tutorial uses separate k/omega blocks, a
    # $turbulence macro in fvSchemes, and per-field relaxation. Cover both.
    engineer._wsl(
        f"sed -i 's/\"(U|k|omega)\"/\"(U|k|omega|epsilon|nuTilda)\"/' {case}/system/fvSolution || true")
    engineer._wsl(
        "sed -i 's/^    omega$/    \"(omega|epsilon|nuTilda)\"/' "
        f"{case}/system/fvSolution || true")
    engineer._wsl(
        "sed -i 's/^        omega           0.7;/        omega           0.7;"
        "\\n        epsilon         0.7;\\n        nuTilda         0.7;/' "
        f"{case}/system/fvSolution || true")
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
        # The tutorial's streamline/cutting-plane diagnostics reference fields
        # a different closure does not carry; the force coefficients are the
        # answer, the rest are visual diagnostics and are dropped here.
        # Pull-edit-push: shell quoting through the WSL seam is unreliable.
        control = engineer._wsl(
            f"cat {engineer.remote_case}/system/controlDict").stdout
        kept = _strip_named_blocks(
            control, ("streamLines", "wallBoundedStreamLines",
                      "cuttingPlane", "ensightWrite")).splitlines()
        staging = OUT / "closure-fields"
        staging.mkdir(parents=True, exist_ok=True)
        (staging / "controlDict").write_text("\n".join(kept) + "\n",
                                             newline="\n")
        wsl_cd = str(staging / "controlDict").replace("C:", "/mnt/c").replace("\\", "/")
        engineer._wsl(f"cp '{wsl_cd}' {engineer.remote_case}/system/controlDict")
        _closure_files(engineer, closure, k=0.24, nu=1.5e-5, length=2.0)
        engineer._run_step("potentialFoam", "potentialFoam -writephi", 3600)
        engineer._run_step("simpleFoam", "simpleFoam", 7200)
        results = engineer.postprocess(("Cd", "Cl"))
        cd = float(results["Cd"]["value"])
        sigma = float(results["Cd"].get("sigma") or 0.0)
        if cd and 2.0 * sigma / abs(cd) > 0.05:
            # An unconverged solve is not evidence; exclude it, say why.
            members[closure] = {"excluded": "unconverged at "
                                f"{ITERATIONS} iterations "
                                f"(window spread {2*sigma:.2g})"}
            _log(f"motorBike {closure}: EXCLUDED unconverged "
                 f"(Cd {cd:.4f} +- {2*sigma:.2g})")
        else:
            members[closure] = cd
            _log(f"motorBike {closure}: Cd {cd:.4f} "
                 f"({round((time.time()-began)/60, 1)} min)")
        _checkpoint(body, closures=members)
    converged = {k: v for k, v in members.items() if isinstance(v, float)}
    excluded = {k: v["excluded"] for k, v in members.items()
                if isinstance(v, dict)}
    label = "inter-closure spread (screening estimate)"
    if excluded:
        label += ("; excluded: "
                  + "; ".join(f"{k}: {v}" for k, v in excluded.items()))
    spread = uq.spread_estimate(converged, label=label)
    _checkpoint(body, model={"band_abs": spread["band_abs"],
                             "method": spread["method"],
                             "members": spread["members"],
                             "excluded": excluded or None,
                             "screening_estimate": True})
    _log(f"motorBike closures DONE: spread {spread['band_abs']:.4g} "
         f"({len(converged)} converged, {len(excluded)} excluded)")


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
# B-52 fourth refinement rung (agenda: resolve the non-monotone 3-rung ladder)
# --------------------------------------------------------------------------

def b52_fourth_rung() -> None:
    """One more rung for the B-52 ladder, aimed at the medium-to-production
    gap, to try to resolve the ladder's non-monotone convergence.

    Placement reasoning: the non-monotone signature is a dip at the medium
    rung (coarse 0.0551 at 40,656 cells, medium 0.0448 at 107,489, production
    0.0472 at 193,880). A rung near that dip tests whether the finest segment
    of the ladder is itself monotone, and when it is, the Eca and Hoekstra
    fit lands on the production mesh, the mesh the act actually reports. A
    rung finer than production (surface level (4 5)) would roughly double the
    solve cost and put the band on a mesh no act solves. The rung is the
    production case with ONE knob moved: the background-mesh divisions scaled
    by 0.9 (the same second knob the in-act rung machinery uses when the
    castellated level floors out); the surface refinement stays at the
    production level (3 4). The snappy refinement cascade is nonlinear in the
    background density, so the cell count the knob produces is measured, not
    chosen; the rung is stored at whatever count checkMesh reports, provided
    it is distinct from every existing rung. Setup matches the stored
    fingerprint exactly: velocity 100.0, published 48.5 m scale basis,
    refinement 3, 300 iterations, with the rung solved at the standard rung
    budget.
    """
    from chief_engineer.external_aero import analyse_surface, build_case
    from workflows.geometry_study import rung_iterations, scale_basis

    body = "b52"
    stl_name = "b52.stl"
    study = uq.load_study(body) or {}
    levels = sorted(study.get("levels", []), key=lambda lv: lv["cells"])
    if len(levels) < 3:
        raise RuntimeError("b52 fourth rung needs the existing 3-rung ladder")
    tag = "intermediate"
    existing = next((lv for lv in levels if lv.get("tag") == tag), None)
    if existing is None:
        _log(f"b52 rung {tag} starting (production case, background "
             f"divisions scaled 0.9)")
        began = time.time()
        engineer = HeadEngineer(f"uq-b52-{tag}", OUT / f"b52-{tag}")
        source = GEOMETRY_DIR / stl_name
        geometry = analyse_surface(source)
        # The act works the B-52 to its published 48.5 m length (scale_basis);
        # the rung must solve the same scaled body or its Reynolds number and
        # Cd basis drift off the ladder's.
        reference, _basis = scale_basis(stl_name, geometry["length"], {})
        scale = reference / geometry["length"]
        case_dir = Path(engineer.out_root) / "case"
        build_case(case_dir, stl_name, geometry, velocity=100.0, scale=scale,
                   refinement=3, iterations=ITERATIONS)
        shutil.copy(source, case_dir / "constant" / "triSurface" / stl_name)
        wsl_case = str(case_dir).replace("C:", "/mnt/c").replace("\\", "/")
        engineer._wsl(f"rm -rf {engineer.remote_case} && "
                      f"cp -r '{wsl_case}' {engineer.remote_case}")
        # The case's domain is scaled to the published length; the staged STL
        # must be scaled with it (exactly as the act stages its case), or the
        # body never meets the domain and snappy meshes an empty box.
        engineer._wsl(
            f"cd {engineer.remote_case} && openfoam2606 surfaceTransformPoints "
            f"-scale '({scale:.6f} {scale:.6f} {scale:.6f})' "
            f"constant/triSurface/{stl_name} constant/triSurface/_scaled.stl && "
            f"mv constant/triSurface/_scaled.stl constant/triSurface/{stl_name}")
        scaled = engineer.scale_background_divisions(0.9)
        if not scaled:
            raise RuntimeError("background divisions unchanged; the rung "
                               "would duplicate the production mesh")
        engineer.set_iteration_count(rung_iterations(ITERATIONS))
        for step, command in (("surfaceFeatureExtract", "surfaceFeatureExtract"),
                              ("blockMesh", "blockMesh"),
                              ("snappyHexMesh", "snappyHexMesh -overwrite")):
            engineer._run_step(step, command, 5400)
        stats = engineer.collect_mesh_stats()
        cells = int(stats.get("cells", 0))
        if not cells:
            raise RuntimeError("checkMesh reported no cells")
        if cells in {int(lv["cells"]) for lv in levels}:
            raise RuntimeError(f"rung mesh duplicates an existing rung "
                               f"({cells} cells); no rung stored")
        _log(f"b52 {tag}: {cells:,} cells, mesh_ok={stats.get('mesh_ok')}, "
             f"max non-orthogonality {stats.get('max_non_orthogonality')}")
        # A generated case carries its pristine fields in 0/ directly; only a
        # case with a 0.orig needs the reset (the in-act rung guard).
        engineer._wsl(f"cd {engineer.remote_case} && test -d 0.orig && "
                      f"rm -rf 0 && cp -r 0.orig 0 || true")
        engineer._run_step("potentialFoam", "potentialFoam -writephi", 3600)
        engineer._run_step("simpleFoam", "simpleFoam", 7200)
        results = engineer.postprocess(("Cd",))
        if not results.get("Cd"):
            raise RuntimeError("no force history from the rung solve")
        cd = float(results["Cd"]["value"])
        sigma = float(results["Cd"].get("sigma") or 0.0)
        if not cd:
            # A zero force coefficient means the solve never saw the body;
            # storing it would poison the ladder.
            raise RuntimeError("rung produced Cd = 0; the case did not "
                               "resolve the body, no rung stored")
        if 2.0 * sigma / abs(cd) > 0.05:
            # An unconverged rung is not ladder evidence; refuse to store it.
            raise RuntimeError(f"rung unconverged: Cd {cd:.4f} window spread "
                               f"{2 * sigma:.2g} exceeds 5 percent")
        existing = {"tag": tag, "cells": cells, "cd": cd,
                    "mission": f"b52-rung-{tag}",
                    "wall_minutes": round((time.time() - began) / 60, 1)}
        levels = sorted(levels + [existing], key=lambda lv: lv["cells"])
        _checkpoint(body, levels=levels)
        _log(f"b52 {tag}: cells {cells:,}, Cd {cd:.4f} "
             f"(window 2-sigma {2 * sigma:.2g}), "
             f"{existing['wall_minutes']} min")
    else:
        _log(f"b52 rung {tag} already done (cells {existing['cells']:,})")
    # Recompute the band over the 4-rung ladder exactly as the in-act
    # machinery will on warm replay: eca_hoekstra_band over the cell-sorted
    # rungs (the fit, clamp rules included, when the finest triplet is
    # monotone; the conservative largest-spread band with the honest
    # sentence when it is not).
    # dim=3: the B-52 ladder is a three-dimensional snappyHexMesh body.
    band = uq.eca_hoekstra_band([lv["cells"] for lv in levels],
                                [lv["cd"] for lv in levels], dim=3)
    production = next(lv for lv in levels if lv.get("tag") == "production")
    working = production.get("cd")
    numerical = uq.study_numerical(
        band,
        band_rel=(None if not working
                  else round(band["band_abs"] / abs(working), 5)),
        value_working=working)
    _checkpoint(body, numerical=numerical,
                provenance=[lv.get("mission", f"{body}-{lv['tag']}")
                            for lv in levels])
    _log(f"b52 fourth rung DONE: monotone={band.get('monotone')}, "
         f"{band['method']}, band {band['band_abs']:.4g}")


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
    # The winning angle of the extended act sweep (30 to 87.5 deg): the study
    # channels are measured at the angle the act actually reports.
    angle = 87.5
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

    # Quadrature convergence, NOT a discretization ladder. k = 3 / 5 / 9 are
    # segment counts the half-sine ejection window is chopped into; each level
    # is closed-form arithmetic on the same reduced-order orifice model. There
    # is no mesh, no solver and no fit anywhere in this block.
    #
    # WHAT THIS BLOCK USED TO SAY, AND WHY IT WAS WRONG. `conclusive` was the
    # literal True, typed here. It never passed through a fit and never faced a
    # guard, and it made this the ONLY stored study whose band reached a live
    # surface: `uq.reportable_band` returned 76.5 Pa for the valve and None for
    # all eight genuine ladders, because those eight were adjudicated and
    # declined and this one was never adjudicated at all. The nine published
    # numbers are not in dispute -- every one of them reproduces from the
    # formula above. The fault is the slot they sat in. So the record now
    # declines itself, names the guard that excludes it, and says in its method
    # string what the number actually measures.
    k_levels = (3, 5, 9)
    values = [cycle_loss(k, 0.62) for k in k_levels]
    spread = max(values) - min(values)
    fine = values[-1]
    numerical = {
        "band_abs": round(abs(values[-1] - values[0]), 1),
        "band_rel": round(abs(values[-1] - values[0]) / fine, 5),
        "method": (f"quadrature convergence of a reduced-order orifice model, "
                   f"k = {'/'.join(map(str, k_levels))} segments of the "
                   f"ejection window; not a mesh refinement"),
        "values": {str(k): round(v, 1) for k, v in zip(k_levels, values)},
        "conclusive": False,
        "not_conclusive_guard": uq.GUARD_NOT_A_DISCRETIZATION_LADDER,
        "guards": {uq.GUARD_NOT_A_DISCRETIZATION_LADDER: False},
        "guards_failed": [uq.GUARD_NOT_A_DISCRETIZATION_LADDER],
        "channel_kind": "quadrature-convergence",
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
    # THE TWO CHANNELS SHARE A POINT, EXACTLY. Both are cycle_loss() on the
    # same waveform and the same reduced-order model; the family member at
    # cd = 0.62 is evaluated at k = 3, which is bit-for-bit the numerical
    # channel's first level. Both read 1252.8 Pa and neither rounding nor
    # coincidence is doing it. Two channels sharing an evaluation are not
    # independent, so combining them in quadrature -- which is what
    # `combine_expanded` does -- double-counts that point and reports a total
    # wider than either channel earned. The overlap is recorded here so the
    # surfaces can refuse the combination instead of rediscovering it.
    shared = sorted(
        name for name, dp in family_dp.items()
        if any(abs(dp - v) < 1e-9 for v in values))
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
               "shares_points_with_numerical": shared,
               "independent_of_numerical": not shared,
               "unmodeled": ["phase-interaction neglected",
                             "leaflet motion not modeled",
                             "Newtonian blood"]},
        provenance=["valve-quadrature-ladder", "orifice-correlation-family"])
    _log(f"valve DONE: quadrature convergence {numerical['band_abs']} Pa "
         f"(NOT conclusive: {uq.guard_clause(uq.GUARD_NOT_A_DISCRETIZATION_LADDER)}), "
         f"family spread {model['band_abs']:.0f} Pa "
         f"(k=3 loss {values[0]:.0f} Pa); "
         f"{len(shared)} shared point(s) with the numerical channel")


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
    "b52_rung4": b52_fourth_rung,
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
