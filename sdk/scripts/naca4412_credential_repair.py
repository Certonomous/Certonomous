"""Re-mesh and re-solve the NACA 4412 wing with a resolved boundary layer.

The credential at models/curriculum/results/naca4412_wing.json was graded
against a mesh built with ``addLayers false`` (see
models/curriculum/naca4412_wing/reference.yaml and
models/curriculum/uq-studies/naca4412_wing.json for the un-layered
67,826 / 137,569 / 337,334-cell ladder). At Re_c = 1e6 the boundary layer on
this wing is a few centimetres thick and cannot be represented by whatever
flat cut-cell snappyHexMesh happens to leave at the wall without layers; the
drag the solver reports in that state is not a resolved viscous force.

This script builds two boundary-layer-resolved meshes (a "medium" and a
"fine" rung, at the same near-body surface levels the old ladder used for its
r3/r4 rungs, so the new numbers sit next to the old ones on a like-for-like
axis) and solves each to convergence. Every stage runs the real OpenFOAM
2606 binaries on this machine directly (no WSL layer — this box is native
Linux). Capped at 4 MPI ranks per the lab's current core-sharing agreement.

Run:
    python3 naca4412_credential_repair.py medium
    python3 naca4412_credential_repair.py fine
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SDK))

from chief_engineer.external_aero import analyse_surface, build_case  # noqa: E402

RUN_ROOT = Path.home() / "certonomous-runs"
GEOMETRY = SDK / "geometry" / "naca4412_wing.stl"
NPROCS = 4                       # hard cap: other agents hold the rest of the box
ITERATIONS = 800                 # generous budget; convergence checked, not assumed

# Flow condition, taken from the credential's own reference.yaml (solve hints):
# chord ~1 m, velocity 15 m/s, air kinematic viscosity 1.5e-5 m^2/s -> Re_c ~ 1e6.
VELOCITY = 15.0
VISCOSITY = 1.5e-5
RHO = 1.225                       # matches forceCoeffs rhoInf in external_aero._control

RUNGS = {
    # near = max(2, refinement); matches the old uq ladder's r3 (medium) and
    # r4 (production) surface levels so the comparison is apples to apples.
    "medium": {"refinement": 3},
    "fine": {"refinement": 4},
    # A third, finer rung: medium->fine dropped Cd ~25% even with layers
    # resolved, so two points cannot tell a real asymptote from a still-open
    # trend. A third point is the minimum needed to fit an observed order
    # (same reasoning the old, layerless r1/r3/r4 ladder used).
    "finer": {"refinement": 5},
}


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def target_first_layer_thickness(chord: float, velocity: float, viscosity: float,
                                  rho: float, y_plus_target: float) -> dict:
    """First prism-layer height for a target y+, from flat-plate turbulent skin
    friction (Schlichting): Cf = 0.058 * Re_x^-0.2, evaluated at the trailing
    edge (x = chord) as the worst case (thinnest sublayer, highest u_tau).

    This is an a-priori sizing estimate only, used to size the mesh before the
    mesh exists. The achieved y+ is measured after the solve (yPlus function
    object) and reported alongside this estimate, not substituted for it.
    """
    re_c = velocity * chord / viscosity
    cf = 0.058 * re_c ** -0.2
    tau_w = cf * 0.5 * rho * velocity ** 2
    u_tau = math.sqrt(tau_w / rho)
    y = y_plus_target * viscosity / u_tau
    return {
        "reynolds_chord": re_c, "cf_flat_plate": cf, "tau_w": tau_w,
        "u_tau": u_tau, "y_plus_target": y_plus_target,
        "first_layer_thickness_m": y,
    }


def run(cmd: list[str], cwd: Path, log_name: str, timeout: float) -> str:
    log_path = cwd / log_name
    _log(f"  $ {' '.join(cmd)}  (cwd={cwd})")
    with log_path.open("w") as fh:
        proc = subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT,
                              timeout=timeout)
    text = log_path.read_text(errors="replace")
    if proc.returncode != 0:
        tail = "\n".join(text.splitlines()[-25:])
        raise RuntimeError(f"{cmd[0]} failed (exit {proc.returncode}) in {cwd}:\n{tail}")
    return text


def foam(case: Path, args: list[str], log_name: str, timeout: float = 1800.0) -> str:
    return run(["openfoam2606", *args], case, log_name, timeout)


def build(tag: str, refinement: int, layer_sizing: dict) -> Path:
    case = RUN_ROOT / f"credential-repair-naca4412-{tag}"
    if case.exists():
        subprocess.run(["rm", "-rf", str(case)], check=True)
    case.mkdir(parents=True)
    (case / "constant" / "triSurface").mkdir(parents=True)
    (case / "constant" / "triSurface" / "naca4412_wing.stl").write_bytes(GEOMETRY.read_bytes())

    geometry = analyse_surface(GEOMETRY, streamwise_axis=0)
    resolved = build_case(
        case, "naca4412_wing.stl", geometry,
        velocity=VELOCITY, viscosity=VISCOSITY, refinement=refinement,
        iterations=ITERATIONS, add_layers=True, n_surface_layers=12,
        first_layer_thickness=layer_sizing["first_layer_thickness_m"],
        layer_expansion_ratio=1.2)
    (case / "decompose_setup.json").write_text(json.dumps(
        {"geometry": {k: v for k, v in geometry.items() if k not in ("min", "max")},
         "resolved": resolved, "layer_sizing": layer_sizing}, indent=2, default=str))

    # 4-way decomposition, hard-capped (the mesh cache/mega-batch elsewhere is
    # using the other 4 of the box's 16 cores; other agents hold the rest).
    (case / "system" / "decomposeParDict").write_text(
        "FoamFile\n{\n    version 2.0;\n    format ascii;\n    class dictionary;\n"
        "    object decomposeParDict;\n}\n\n"
        f"numberOfSubdomains {NPROCS};\nmethod scotch;\n")
    return case


def mesh(case: Path) -> None:
    foam(case, ["surfaceFeatureExtract"], "log.surfaceFeatureExtract", 300)
    foam(case, ["blockMesh"], "log.blockMesh", 300)
    foam(case, ["snappyHexMesh", "-overwrite"], "log.snappyHexMesh", 3600)
    foam(case, ["checkMesh"], "log.checkMesh", 600)


def solve(case: Path) -> None:
    foam(case, ["decomposePar", "-force"], "log.decomposePar", 300)
    # mpirun must run *inside* the openfoam2606 launcher (not as a bare
    # subprocess) so the spawned ranks inherit simpleFoam on PATH; a bare
    # mpirun here fails with "unable to find the specified executable file".
    foam(case, ["mpirun", "-np", str(NPROCS), "simpleFoam", "-parallel"],
        "log.simpleFoam", 7200)
    foam(case, ["reconstructPar", "-latestTime"], "log.reconstructPar", 900)


def yplus(case: Path) -> str:
    # The generic `postProcess` utility cannot find the turbulence model in
    # its database for this solver; yPlus must run through the solver's own
    # -postProcess entry point (simpleFoam -postProcess -func yPlus), or it
    # silently reports 0/0/0 (see yPlus.C's own warning about this).
    return foam(case, ["simpleFoam", "-postProcess", "-func", "yPlus", "-latestTime"],
               "log.yPlus", 600)


# --------------------------------------------------------------------------
# Result extraction
# --------------------------------------------------------------------------

def parse_checkmesh(text: str) -> dict:
    out = {}
    m = re.search(r"cells:\s*([0-9]+)", text)
    if m:
        out["cells"] = int(m.group(1))
    m = re.search(r"Max non-orthogonality = ([0-9.]+)", text)
    if m:
        out["max_non_orthogonality"] = float(m.group(1))
    m = re.search(r"Max skewness = ([0-9.]+)", text)
    if m:
        out["max_skewness"] = float(m.group(1))
    out["mesh_ok"] = "Mesh OK" in text or "Mesh OK." in text
    return out


def parse_layer_coverage(text: str) -> dict:
    """The layer-addition summary snappyHexMesh prints per patch."""
    out = {}
    m = re.search(r"Layer thickness for layer 1 :\s*([0-9.eE+-]+)", text)
    if m:
        out["layer1_thickness_reported"] = float(m.group(1))
    # Table rows look like: "body                 20000    12    12    1     ..."
    for line in text.splitlines():
        if line.strip().startswith("body") and "Wanted" not in line:
            parts = line.split()
            if len(parts) >= 4 and parts[0] == "body":
                out["layer_summary_line"] = line.strip()
    return out


def parse_forcecoeffs(case: Path) -> dict:
    root = case / "postProcessing" / "forceCoeffs1"
    files = sorted(root.rglob("coefficient.dat")) + sorted(root.rglob("*.dat"))
    if not files:
        raise RuntimeError(f"no forceCoeffs output under {root}")
    path = files[-1]
    header: list[str] = []
    rows: list[list[float]] = []
    for line in path.read_text(errors="replace").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            tokens = s.lstrip("#").split()
            if len(tokens) > 1:
                header = tokens
            continue
        try:
            rows.append([float(t) for t in s.split()])
        except ValueError:
            continue
    cols = {name: i for i, name in enumerate(header)}
    window = rows[-max(2, len(rows) // 6):]

    def series(name):
        i = cols.get(name)
        if i is None:
            return None
        return [r[i] for r in window if i < len(r)]

    cd = series("Cd")
    cl = series("Cl")
    full_cd = series("Cd") and [r[cols["Cd"]] for r in rows]
    out = {
        "cd_final": rows[-1][cols["Cd"]] if "Cd" in cols else None,
        "cl_final": rows[-1][cols["Cl"]] if "Cl" in cols else None,
        "cd_window_mean": sum(cd) / len(cd) if cd else None,
        "cl_window_mean": sum(cl) / len(cl) if cl else None,
        "cd_window_std": (sum((v - sum(cd) / len(cd)) ** 2 for v in cd) / (len(cd) - 1)) ** 0.5
                        if cd and len(cd) > 1 else None,
        "n_rows": len(rows),
        "path": str(path),
    }
    return out


def parse_residuals(text: str) -> dict:
    last: dict[str, float] = {}
    for line in text.splitlines():
        m = re.search(r"Solving for (\w+),.*Final residual = ([0-9.eE+-]+)", line)
        if m:
            last[m.group(1)] = float(m.group(2))
    converged = ("SIMPLE solution converged" in text)
    return {"final_residuals": last, "converged_flag": converged}


def parse_yplus(text: str) -> dict:
    out = {}
    m = re.search(r"y\+\s*:\s*min\s*=\s*([0-9.eE+-]+),\s*max\s*=\s*([0-9.eE+-]+),\s*"
                 r"average\s*=\s*([0-9.eE+-]+)", text)
    if m:
        out["y_plus_min"] = float(m.group(1))
        out["y_plus_max"] = float(m.group(2))
        out["y_plus_average"] = float(m.group(3))
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in RUNGS:
        print(f"usage: {argv[0]} <{'|'.join(RUNGS)}>")
        return 2
    tag = argv[1]
    refinement = RUNGS[tag]["refinement"]

    geometry = analyse_surface(GEOMETRY, streamwise_axis=0)
    chord = geometry["length"]
    layer_sizing = target_first_layer_thickness(chord, VELOCITY, VISCOSITY, RHO,
                                                y_plus_target=30.0)
    _log(f"rung={tag} refinement={refinement} chord={chord:.4f} m "
        f"first_layer_thickness={layer_sizing['first_layer_thickness_m']:.4g} m "
        f"(target y+={layer_sizing['y_plus_target']:g})")

    case = build(tag, refinement, layer_sizing)
    _log(f"case staged at {case}")

    t0 = time.monotonic()
    mesh(case)
    t_mesh = time.monotonic() - t0
    check = parse_checkmesh((case / "log.checkMesh").read_text(errors="replace"))
    layers = parse_layer_coverage((case / "log.snappyHexMesh").read_text(errors="replace"))
    _log(f"mesh done in {t_mesh:.0f}s: {check}")
    _log(f"layer coverage: {layers}")

    t1 = time.monotonic()
    solve(case)
    t_solve = time.monotonic() - t1
    log_solve = (case / "log.simpleFoam").read_text(errors="replace")
    residuals = parse_residuals(log_solve)
    forces = parse_forcecoeffs(case)
    _log(f"solve done in {t_solve:.0f}s: residuals={residuals} forces={forces}")

    yp_text = yplus(case)
    yp = parse_yplus(yp_text)
    _log(f"y+ (post-solve, actual): {yp}")

    result = {
        "tag": tag, "refinement": refinement, "case": str(case),
        "wall_seconds_mesh": round(t_mesh, 1), "wall_seconds_solve": round(t_solve, 1),
        "layer_sizing": layer_sizing, "checkmesh": check, "layer_coverage": layers,
        "residuals": residuals, "forces": forces, "y_plus": yp,
        "geometry": {k: v for k, v in geometry.items() if k not in ("min", "max")},
        "velocity": VELOCITY, "viscosity": VISCOSITY, "nprocs": NPROCS,
        "iterations_budget": ITERATIONS,
    }
    out_path = SDK.parent / "mission-output" / "uq-studies" / f"naca4412_repair_{tag}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=str))
    _log(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
