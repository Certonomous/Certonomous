#!/usr/bin/env python3
"""Paired k-family FPE diagnosis arm (bump + hills).

Pre-registration: FPE_DIAG_PREREGISTRATION.md (same directory) -- read it
first; this script implements it and decides nothing on its own. Five runs:
three instrumented crash probes (HP1, BP1, BP2) and two single-variable
levers (HL1, BL1). Every case carries log.checkMesh before its solver
launches (Verification Charter v1.5 section 9); solver logs carry the
mechanical lever echo via tv._foam, so levers_verified_active is built from
the log itself. Records: FPE_DIAG_runs/<run>/record.json. No band changes.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import time
from pathlib import Path

REPO = Path("/home/ubuntu/Certonomous")
sys.path.insert(0, str(REPO / "sdk"))
from workflows import tmr_verification as tv  # noqa: E402
from scripts import model_form_batch as mfb  # noqa: E402
from chief_engineer import lever_echo  # noqa: E402

HERE = REPO / "demo-output" / "website" / "campaign" / "FPE_DIAG_runs"
H_SRC = mfb.H_SOURCE_CASE
RUN_ROOT = Path(tv._RUN_ROOT)
DRIVER_LOG = HERE / "driver.log"


def log(msg: str) -> None:
    line = f"[{mfb._now()}] {msg}"
    print(line, flush=True)
    with DRIVER_LOG.open("a") as handle:
        handle.write(line + "\n")


def minmax_fo(fields: str) -> str:
    return (
        "    fpeMinMax\n"
        "    {\n"
        "        type            fieldMinMax;\n"
        "        libs            (fieldFunctionObjects);\n"
        f"        fields          ({fields});\n"
        "        location        yes;\n"
        "        executeControl  timeStep;\n"
        "        writeControl    timeStep;\n"
        "    }\n")


def add_function_object(control_text: str, fo: str) -> str:
    if "functions" in control_text:
        idx = control_text.find("functions")
        brace = control_text.find("{", idx)
        return control_text[:brace + 1] + "\n" + fo + control_text[brace + 1:]
    return control_text + "\nfunctions\n{\n" + fo + "}\n"


def grade(remote: Path, out_dir: Path, name: str, wall: float,
          returncode: int, extras: dict) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    log_text = (remote / "log.simpleFoam").read_text(errors="replace") \
        if (remote / "log.simpleFoam").exists() else ""
    for item in ("log.simpleFoam", "log.checkMesh", "log.potentialFoam"):
        src = remote / item
        if src.exists():
            shutil.copy2(src, out_dir / item)
    logv = mfb.log_verdict(log_text)
    record = {
        "run": name,
        "prereg": "campaign/FPE_DIAG_runs/FPE_DIAG_PREREGISTRATION.md",
        "fatal": logv["fatal"],
        "crashed": bool(logv["fatal"]) or returncode != 0,
        "returncode": returncode,
        "last_iteration": logv["last_iteration"],
        "residual_control_met": logv["residual_control_met"],
        "levers_verified_active": lever_echo.levers_verified_active(log_text),
        "wall_seconds": round(wall, 1),
        "core_min": round(wall / 60.0, 3),
        "timestamp": mfb._now(),
    }
    record.update(extras)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def stage_hills_kepsilon(name: str, endtime: int, monitored: bool) -> Path:
    remote = RUN_ROOT / f"fpediag-{name}"
    shutil.rmtree(remote, ignore_errors=True)
    remote.mkdir(parents=True)
    for sub in ("0", "constant", "system"):
        shutil.copytree(H_SRC / sub, remote / sub)
    shutil.copy2(H_SRC / "log.checkMesh", remote / "log.checkMesh")
    (remote / "constant" / "turbulenceProperties").write_text(
        mfb.turbulence_properties_for("kEpsilon"), newline="\n")
    field_name, field_text = mfb._hills_field_from_omega(
        (remote / "0" / "omega").read_text(), "kEpsilon")
    (remote / "0" / field_name).write_text(field_text, newline="\n")
    sol_path = remote / "system" / "fvSolution"
    sol = sol_path.read_text()
    sol = sol.replace("        omega   1e-6;",
                      "        omega   1e-6;\n        epsilon 1e-6;", 1)
    sol = sol.replace("    omega   0.7;",
                      "    omega   0.7;\n    epsilon 0.7;", 1)
    sol_path.write_text(sol, newline="\n")
    sch_path = remote / "system" / "fvSchemes"
    sch_path.write_text(sch_path.read_text().replace(
        "    div(phi,omega)  bounded Gauss linearUpwind grad(U);",
        "    div(phi,omega)  bounded Gauss linearUpwind grad(U);\n"
        "    div(phi,epsilon) bounded Gauss linearUpwind grad(U);", 1),
        newline="\n")
    ctrl = remote / "system" / "controlDict"
    text = re.sub(r"endTime\s+\d+;", f"endTime         {endtime};",
                  ctrl.read_text())
    if monitored:
        text = add_function_object(text, minmax_fo("p U k epsilon nut"))
    ctrl.write_text(text, newline="\n")
    return remote


def read_scalar_internal(path: Path) -> list[float]:
    text = path.read_text(errors="replace")
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(",
                  text)
    if not m:
        raise RuntimeError(f"{path}: no nonuniform scalar internalField")
    count = int(m.group(1))
    body = text[m.end():]
    vals = []
    for token in body.split(")", 1)[0].split():
        vals.append(float(token))
    if len(vals) != count:
        raise RuntimeError(f"{path}: {len(vals)} values, header says {count}")
    return vals


def write_seeded_field(template: Path, out: Path, obj: str,
                       values: list[float]) -> None:
    """The template's boundaryField with a nonuniform internalField."""
    text = template.read_text()
    text = re.sub(r"object\s+\w+;", f"object      {obj};", text)
    body = "internalField   nonuniform List<scalar>\n" \
           f"{len(values)}\n(\n" + "\n".join(f"{v:.10g}" for v in values) \
           + "\n)\n;"
    text = re.sub(r"internalField\s+uniform\s+[0-9eE.+-]+;", body, text, 1)
    out.write_text(text, newline="\n")


def seed_hl1(remote: Path) -> None:
    k_sst = read_scalar_internal(H_SRC / "5997" / "k")
    omega_sst = read_scalar_internal(H_SRC / "5997" / "omega")
    eps = [0.09 * k * w for k, w in zip(k_sst, omega_sst)]
    write_seeded_field(remote / "0" / "k", remote / "0" / "k", "k", k_sst)
    write_seeded_field(remote / "0" / "epsilon", remote / "0" / "epsilon",
                       "epsilon", eps)


def stage_bump(name: str, model: str, endtime: int, monitored: bool) -> Path:
    level = [lv for lv in tv.BUMP_LEVELS if lv.name == "coarse"][0]
    nu = tv.U_INF / 1.2e7
    omega_inf = 1.0e-6 * (tv.U_INF / tv.MACH) ** 2 / nu
    nut_inf = tv.K_INF / omega_inf
    case_root = RUN_ROOT / f"fpediag-{name}-case"
    shutil.rmtree(case_root, ignore_errors=True)
    case_root.mkdir(parents=True)
    case_dir = tv.write_bump_case(case_root, level)
    mfb.patch_case(case_dir, model, nu=nu, k_inf=tv.K_INF, nut_inf=nut_inf,
                   omega_inf_old=tv.BUMP_OMEGA_INF, omega_inf_new=omega_inf,
                   nut_inf_old=tv.BUMP_NUT_INF)
    mfb.set_backstop(case_dir, endtime)
    if monitored:
        ctrl = case_dir / "system" / "controlDict"
        fields = "p U k omega nut" if model == "kOmegaSST" \
            else "p U k epsilon nut"
        ctrl.write_text(add_function_object(ctrl.read_text(),
                                            minmax_fo(fields)), newline="\n")
    remote = RUN_ROOT / f"fpediag-{name}"
    out_dir = HERE / name
    out_dir.mkdir(parents=True, exist_ok=True)
    tv._stage_and_mesh(level, case_root, out_dir, str(remote),
                       lambda root, lv: case_dir, log)
    shutil.rmtree(case_root, ignore_errors=True)
    return remote


def ensure_phi_solver(remote: Path) -> None:
    """The F8 section 12 mechanical lesson: potentialFoam needs a Phi block."""
    path = remote / "system" / "fvSolution"
    text = path.read_text()
    if re.search(r"^\s*Phi\s*$", text, re.MULTILINE) or "Phi\n" in text:
        return
    text = text.replace("solvers\n{", """solvers
{
    Phi
    {
        solver          GAMG;
        smoother        DIC;
        tolerance       1e-06;
        relTol          0.01;
    }
""", 1)
    if "potentialFlow" not in text:
        text += ("\npotentialFlow\n{\n    nNonOrthogonalCorrectors 10;\n}\n")
    path.write_text(text, newline="\n")


def solve(remote: Path, name: str, extras: dict, *,
          potential_first: bool = False, timeout: int = 3600) -> dict:
    mfb.assert_mesh_certified_at_entry(remote, "DIAG", name)
    start = time.monotonic()
    if potential_first:
        ensure_phi_solver(remote)
        result = tv._foam(["potentialFoam"], remote, "log.potentialFoam",
                          timeout=600)
        if result.returncode != 0:
            log(f"{name}: potentialFoam failed rc={result.returncode}")
    result = tv._foam(["simpleFoam"], remote, "log.simpleFoam",
                      timeout=timeout)
    wall = time.monotonic() - start
    record = grade(remote, HERE / name, name, wall, result.returncode, extras)
    log(f"{name}: crashed={record['crashed']} fatal={record['fatal']} "
        f"last_iter={record['last_iteration']} {record['core_min']} core-min")
    shutil.rmtree(remote, ignore_errors=True)
    return record


def main() -> int:
    log("FPE diagnosis arm starting (prereg FPE_DIAG_PREREGISTRATION.md)")
    # Phase 1: instrumented probes
    r = stage_hills_kepsilon("HP1", 100, monitored=True)
    solve(r, "HP1", {"phase": 1, "geometry": "hills", "model": "kEpsilon",
                     "change": "fieldMinMax monitoring only"})
    r = stage_bump("BP1", "kOmegaSST", 200, monitored=True)
    solve(r, "BP1", {"phase": 1, "geometry": "bump", "model": "kOmegaSST",
                     "change": "fieldMinMax monitoring only"})
    r = stage_bump("BP2", "kEpsilon", 200, monitored=True)
    solve(r, "BP2", {"phase": 1, "geometry": "bump", "model": "kEpsilon",
                     "change": "fieldMinMax monitoring only"})
    # Phase 2: one lever per geometry
    r = stage_hills_kepsilon("HL1", 3000, monitored=False)
    seed_hl1(r)
    solve(r, "HL1", {"phase": 2, "geometry": "hills", "model": "kEpsilon",
                     "lever": "k/epsilon seeded per-cell from converged SST "
                              "field (medium/5997), eps=0.09*k*omega"})
    r = stage_bump("BL1", "kOmegaSST", 2000, monitored=False)
    solve(r, "BL1", {"phase": 2, "geometry": "bump", "model": "kOmegaSST",
                     "lever": "potentialFoam initialization (Phi block per "
                              "F8 section 12 lesson)"},
          potential_first=True)
    log("FPE diagnosis arm complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
