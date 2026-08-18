"""
F6d -- the specific, cheap test that F6a's corner-convergence negative result
now demands: re-run F6a's OWN 1C / 2C / 3C corners on F6a's OWN NASA-hump case
and mesh, changing NOTHING except the sign of the source term, from

    eqn += fvc::div(deltaR);       (what all 18 F6a fvOptions dictionaries do)
to
    eqn -= fvc::div(deltaR);       (what makes R_eff = R_model + (R_pert - R_model))

F6a recorded all three corners as effectively unreachable and, in
F6a_epistemic_propagation.md Sec. 8, read that as an intrinsic limit of the
eigenspace-perturbation machinery on that case.  realizability_of_flipped_corner.py
measures that with the `+=` sign the 1C corner hands the momentum equation a
NON-REALIZABLE Reynolds stress in 95.9% of the hump's 51,626 cells.  If the
corrected sign converges, the recorded negative result was a property of the
implementation, not of the method.

Restart is from F6a's own converged baseline field (t=1795), which is also the
initialisation F6a's own Sec. 8 "lever 2" used.
"""
import re, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "f6a_epistemic_band" / "r4_band_tightening_hump" / "oneC_delta0.00"
OUT = HERE / "f6a_recheck"
FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
BASE_T = "1795"

FVO_TEMPLATE = (SRC / "system" / "fvOptions").read_text()

def build(name, corner, op):
    dst = OUT / name
    if dst.exists():
        shutil.rmtree(dst)
    (dst / "0").mkdir(parents=True)
    for sub in ("constant", "system"):
        shutil.copytree(SRC / sub, dst / sub)
    for extra in ("fieldDef", "caseDef"):
        p = SRC / extra
        if p.is_file():
            shutil.copy(p, dst / extra)
        elif p.is_dir():
            shutil.copytree(p, dst / extra)
    for f in (SRC / BASE_T).iterdir():
        if f.is_file():
            shutil.copy(f, dst / "0" / f.name)
        elif f.name == "uniform":
            pass  # never copy uniform/time -- it resets the write time index
    txt = FVO_TEMPLATE
    # regex, not a literal replace: the template case is oneC_delta0.00, whose
    # dictionary carries `blendDelta      0.00;`.  A literal replace of "0.05"
    # silently left the perturbation switched OFF and the first attempt of this
    # script produced a converged unperturbed baseline that looked like a
    # spectacular result.  Fail loudly instead.
    n1 = len(re.findall(r"perturbCorner\s+\w+;", txt))
    n2 = len(re.findall(r"blendDelta\s+[0-9.]+;", txt))
    assert n1 == 1 and n2 == 1, f"unexpected fvOptions template ({n1},{n2})"
    txt = re.sub(r"perturbCorner\s+\w+;", f"perturbCorner   {corner};", txt)
    txt = re.sub(r"blendDelta\s+[0-9.]+;", "blendDelta      1.0;", txt)
    assert "blendDelta      1.0;" in txt
    assert "eqn += fvc::div(deltaR);" in txt
    if op == "-=":
        txt = txt.replace("eqn += fvc::div(deltaR);", "eqn -= fvc::div(deltaR);")
    txt = txt.replace("name            uqEigPerturb;", f"name            uqEig{name.replace('_','')};")
    (dst / "system" / "fvOptions").write_text(txt)
    cd = (dst / "system" / "controlDict").read_text()
    cd = cd.replace("startFrom       latestTime;", "startFrom       startTime;\nstartTime       0;")
    cd = cd.replace("endTime         3800;", "endTime         3800;")
    (dst / "system" / "controlDict").write_text(cd)
    return dst

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    which = sys.argv[1:] or ["oneC", "twoC", "threeC"]
    procs = []
    for corner in which:
        d = build(f"corrected_{corner}", corner, "-=")
        print("built", d, flush=True)
        procs.append(subprocess.Popen(["bash", "-lc",
            f"source {FOAM} && cd {d} && nice -n 10 simpleFoam > log.simpleFoam 2>&1"]))
    for p in procs:
        p.wait()
    print("f6a recheck done", flush=True)
