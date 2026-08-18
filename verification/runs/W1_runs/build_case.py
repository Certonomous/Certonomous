"""Build one NASA-grid bump case: dicts from tmr_verification, mesh from NASA bytes."""
import sys, subprocess, gzip, shutil
from pathlib import Path
sys.path.insert(0, '/home/ubuntu/Certonomous/sdk')
import workflows.tmr_verification as t
from chief_engineer import lever_echo

GRIDS = {"coarse": ("bump_4levelsdown_89x41.p3dfmt.gz", 3520),
         "medium": ("bump_3levelsdown_177x81.p3dfmt.gz", 14080),
         "fine":   ("bump_2levelsdown_353x161.p3dfmt.gz", 56320)}
name = sys.argv[1]
grid, cells = GRIDS[name]
case = Path(name); (case/"system").mkdir(parents=True, exist_ok=True)
(case/"constant").mkdir(exist_ok=True); (case/"0").mkdir(exist_ok=True)
files = {
    "system/controlDict": t.control_dict(t.iteration_backstop(cells), patch="bump",
                                          lref=t.BUMP_WALL_LENGTH, aref=t.BUMP_WALL_LENGTH),
    "system/fvSchemes": t.fv_schemes(),
    "system/fvSolution": t.fv_solution(),
    "constant/transportProperties": t.transport_properties(t.BUMP_NU),
    "constant/turbulenceProperties": t.turbulence_properties(),
}
for fn, text in t.bump_initial_fields().items():
    files[f"0/{fn}"] = text
for rel, text in files.items():
    (case/rel).write_text(text)
src = Path('/home/ubuntu/Certonomous/models/tmr/bump/grids')/grid
with gzip.open(src, 'rb') as fi, open(case/'grid.p3dfmt', 'wb') as fo:
    shutil.copyfileobj(fi, fo)
def foam(args, log):
    with open(case/log, 'w') as fh:
        # `case` is the same object passed to `cwd=`, so the echoed directory
        # and the executing directory cannot disagree (L-45). Every launch in
        # this script is a mesh utility, so the shared predicate correctly
        # emits nothing -- routed anyway so one predicate decides everywhere.
        block = lever_echo.echo_if_solver(args, case)
        if block:
            fh.write(block)
            fh.flush()
        subprocess.run(['openfoam2606', *args], cwd=case, stdout=fh,
                       stderr=subprocess.STDOUT, check=True, timeout=600)
foam(['plot3dToFoam', '-noBlank', 'grid.p3dfmt'], 'log.plot3dToFoam')
foam(['transformPoints', '-rotate-x', '-90'], 'log.transformPoints')
print(f"{name}: converted and rotated")
