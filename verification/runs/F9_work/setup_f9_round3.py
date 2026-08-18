#!/usr/bin/env python3
"""Build the round-3 F9 cases (2026-07-30):

  mesh_coarse_q100 / mesh_fine_q100
      Grid-convergence pair for the steady q100 reference point. Same
      geometry, same BCs, same probe stations as ``steady_q100``; only the
      block counts change, by a factor 2 in every direction (h ratio 2 both
      ways). maxCo is held at 0.9, so the timestep refines with the mesh --
      a combined space+time refinement. The separate ``physio_dt_half`` run
      below measures how much of that is temporal.

  pulsatile_fine
      ``pulsatile_physio`` re-solved on the fine mesh, 3 cycles, so the
      headline cycle-mean dp would carry a direct grid-sensitivity number
      instead of one inherited from the steady map. LAUNCHED AND CANCELLED
      2026-07-30 after 364 s: the fine mesh's Courant-limited timestep came
      out ~5x smaller than the base mesh's rather than the ~2x a uniform
      refinement suggests, putting the run at an estimated 5 hours on one
      core. The steady grid triplet below plus Gate 1's quasi-steady
      agreement carry the same information for a twentieth of the cost.
      Recorded rather than quietly dropped; the partial case directory was
      deleted so it cannot be mistaken for a result, and its launch log
      survives in ``solve_registry``.

  mesh_med_q100
      Third grid level at h/1.5, added once the h/2 level's cost became
      clear, so a three-level convergence index does not depend on the
      most expensive run finishing.

  lowalpha_ext
      Restart of ``pulsatile_lowalpha`` from its t=5.4 checkpoint out to
      t=10.8 (3 full cycles at T=3.6). The original run stopped at 1.5
      cycles, so NO cycle-to-cycle convergence check was ever possible for
      it -- its Gate-1 number rested on a cycle never shown to be periodic.

  physio_dt_half
      Restart of ``pulsatile_physio`` from its t=1.8 checkpoint over the
      final cycle with maxCo halved (0.45) -- temporal discretization
      sensitivity on the same mesh.

Cases are written here; every launch goes through scripts/launch_solve.sh.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# NOT `parents[3]`, and this is a defect class rather than a typo: a
# repository root derived by COUNTING segments up from a path under a
# MOVING tree points somewhere else the moment the tree moves.  MOVE_MAP
# batch 7 made this file ONE SEGMENT SHALLOWER, so `parents[3]` went from
# the repository root to `/home/ubuntu`.  There is no path literal in the
# expression, so no prefix rewrite and no grep for `demo-output` reaches it
# -- the same class cost `sdk/tests/test_a2_shape.py:28` a green comparison
# over ten synthetic bodies at batch 6.  DERIVED BY SEARCHING for the
# marker, so the answer no longer depends on this file's depth.
ROOT = next((_p for _p in Path(__file__).resolve().parents
            if (_p / "scripts" / "lab_paths.py").is_file()), None)
if ROOT is None:
    raise RuntimeError(
        "cannot locate scripts/lab_paths.py above %s; refusing to "
        "guess a repository root" % __file__)
for p in (ROOT / "sdk", ROOT / "models" / "curriculum" / "aortic_valve"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from workflows import valve_pulsatile_cfd as v  # noqa: E402

BASE_MESH = dict(nx_up=60, nx_throat=6, nx_down=90, nr_in=24, nr_out=8)
COARSE_MESH = dict(nx_up=30, nx_throat=3, nx_down=45, nr_in=12, nr_out=4)
MED_MESH = dict(nx_up=90, nx_throat=9, nx_down=135, nr_in=36, nr_out=12)
FINE_MESH = dict(nx_up=120, nx_throat=12, nx_down=180, nr_in=48, nr_out=16)

U_Q100 = v.Q_PEAK / v.A_PIPE          # 1.20344 m/s, same as steady_q100


def _cells(m):
    return ((m["nx_up"] + m["nx_down"]) * (m["nr_in"] + m["nr_out"])
            + m["nx_throat"] * m["nr_in"])


def build_steady(name: str, mesh: dict, dt0: float) -> Path:
    case = HERE / name
    if case.exists():
        shutil.rmtree(case)
    v.write_case(case, steady_u=U_Q100, t_cycle=v.T_CYCLE, end_time=1.2,
                 dt0=dt0, write_interval=0.3, **mesh)
    return case


def build_pulsatile(name: str, mesh: dict, dt0: float, end_time: float) -> Path:
    case = HERE / name
    if case.exists():
        shutil.rmtree(case)
    v.write_case(case, steady_u=None, t_cycle=v.T_CYCLE, end_time=end_time,
                 dt0=dt0, write_interval=v.T_CYCLE, **mesh)
    return case


def build_restart(name: str, source: str, t_start: float, t_end: float,
                  max_co: float | None = None) -> Path:
    """Clone a finished case's mesh + one time directory and restart it.

    Only constant/polyMesh and the single restart time directory are copied
    -- no postProcessing, no other time dirs -- so the new run's probe file
    starts clean at t_start and cannot be confused with the parent's.
    """
    src = HERE / source
    case = HERE / name
    if case.exists():
        shutil.rmtree(case)
    (case).mkdir(parents=True)
    shutil.copytree(src / "constant", case / "constant")
    tdir = src / f"{t_start:g}"
    if not tdir.is_dir():
        raise SystemExit(f"restart time dir missing: {tdir}")
    shutil.copytree(tdir, case / f"{t_start:g}")
    shutil.copytree(src / "system", case / "system")
    cd = case / "system" / "controlDict"
    text = cd.read_text()
    text = text.replace("startTime       0;", f"startTime       {t_start:g};")
    old_end = [ln for ln in text.splitlines() if ln.startswith("endTime")][0]
    text = text.replace(old_end, f"endTime         {t_end:g};")
    text = text.replace("purgeWrite      3;", "purgeWrite      0;")
    if max_co is not None:
        old_co = [ln for ln in text.splitlines() if ln.startswith("maxCo")][0]
        text = text.replace(old_co, f"maxCo           {max_co:g};")
        old_mdt = [ln for ln in text.splitlines()
                   if ln.startswith("maxDeltaT")][0]
        val = float(old_mdt.split()[-1].rstrip(";"))
        text = text.replace(old_mdt, f"maxDeltaT       {val * max_co / 0.9:g};")
    cd.write_text(text)
    return case


def main():
    print("cells: coarse", _cells(COARSE_MESH), "base", _cells(BASE_MESH),
          "med", _cells(MED_MESH), "fine", _cells(FINE_MESH))
    made = []
    made.append(build_steady("mesh_coarse_q100", COARSE_MESH, 1e-4))
    made.append(build_steady("mesh_fine_q100", FINE_MESH, 2.5e-5))
    made.append(build_steady("mesh_med_q100", MED_MESH, 3.3e-5))
    made.append(build_restart("lowalpha_ext", "pulsatile_lowalpha", 5.4, 10.8))
    made.append(build_restart("physio_dt_half", "pulsatile_physio", 1.8, 2.7,
                              max_co=0.45))
    for c in made:
        print("wrote", c)


if __name__ == "__main__":
    main()
