#!/usr/bin/env python3
"""
F24 -- BUILD ONE LADDER LEVEL into a destination directory (called by
run_f24.sh once per level; lineage cases/F20_ISENTROPIC_VORTEX/build_f20.py).
REFUSES a destination holding `0/`, a numeric time directory or processor*
directories; deletes nothing; refuses a destination inside the tracked case
tree.  Mesher and postProcess run here, so never call it against the case tree.

  1. template blockMeshDict (N -> NXA, NXB, NY; yb, yt) and controlDict (dt);
     copy the fixed dictionaries
  2. blockMesh, checkMesh -> `Mesh OK`, MESH_STANDARD section 3 gates enforced
     (non-orthogonality 70 deg, skewness 4); aspect ratio recorded
  3. mkdir 0/, `postProcess -func writeCellCentres|writeCellVolumes` -> 0/C, 0/V
  4. write 0/p and 0/T (state 1 at the mesh's own centres), then 0/U LAST.
`--scratch N` builds a SUB-LADDER grid for the instrument (refuses a registered N).
decomposePar is the LAUNCHER's step, after 0/U.  Zero `assert` (L-332).
"""
import os
import re
import sys
import math
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_f24 as EX            # noqa: E402
import foam_io_f24 as FIO          # noqa: E402
import numpy as np                 # noqa: E402

CASE_SRC = os.path.join(HERE, "case")
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
MAX_NON_ORTHO = 70.0
MAX_SKEW = 4.0
ASPECT_ADVISORY = 1000.0


def die(msg, rc=1):
    sys.stderr.write("ABORT (build_f24): %s\n" % msg)
    sys.exit(rc)


def foam(cmd, case_dir, log):
    # `set -u` is never in force here (L-339: the bashrc reads unbound variables).
    full = ". %s > /dev/null 2>&1; %s -case %s > %s 2>&1" % (FOAM_BASHRC, cmd, case_dir, log)
    return subprocess.run(["bash", "-c", full]).returncode


def refuse_if_answered(dest):
    if os.path.isdir(dest):
        for d in os.listdir(dest):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?", d) or re.fullmatch(r"processor[0-9]+", d):
                die("%s already holds %s. REFUSED, not deleted (rule 4)." % (dest, d), rc=2)


def main(argv):
    usage = "usage: build_f24.py <dest_dir> --level <coarse|medium|fine>  |  <dest_dir> --scratch N"
    if len(argv) == 3 and argv[1] == "--level":
        dest, level = os.path.abspath(argv[0]), argv[2]
        lv = dict((nm, (n, s)) for nm, n, s in EX.LEVELS)
        if level not in lv:
            die("unknown level %r" % level)
        n, steps = lv[level]
    elif len(argv) == 3 and argv[1] == "--scratch":
        dest, level = os.path.abspath(argv[0]), "SCRATCH(not_a_ladder_level)"
        n = int(argv[2])
        if n in [a for _nm, a, _s in EX.LEVELS]:
            die("--scratch may not build a registered ladder level")
        steps = int(round(EX.T_END * n / EX.DT_OVER_H))
    else:
        die(usage)
    dt = EX.dt_of(steps)
    if os.path.realpath(dest).startswith(os.path.realpath(CASE_SRC)):
        die("destination %s lies inside the tracked case tree; refused" % dest, rc=2)
    refuse_if_answered(dest)
    for sub in ("system", "constant"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    for f in ("fvSchemes", "fvSolution", "decomposeParDict"):
        shutil.copy(os.path.join(CASE_SRC, "system", f), os.path.join(dest, "system", f))
    for f in ("thermophysicalProperties", "turbulenceProperties"):
        shutil.copy(os.path.join(CASE_SRC, "constant", f), os.path.join(dest, "constant", f))
    d = math.radians(EX.DELTA_DEG)
    yb = EX.X_OUT * math.tan(d)
    nxa, nxb, ny = int(round((EX.X_CORNER - EX.X_IN) * n)), int(round((EX.X_OUT - EX.X_CORNER) * n)), int(round(EX.H_TOP * n))
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "blockMeshDict.template"),
                            os.path.join(dest, "system", "blockMeshDict"),
                            {"__N__": str(n), "__NXA__": str(nxa), "__NXB__": str(nxb), "__NY__": str(ny),
                             "__YB__": repr(yb), "__YT__": repr(EX.H_TOP - yb)})
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "controlDict.template"),
                            os.path.join(dest, "system", "controlDict"), {"__DT__": repr(dt)})
    cd = open(os.path.join(dest, "system", "controlDict")).read()
    m = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", cd, re.M)
    if not m or abs(float(m.group(1)) - EX.T_END) > 1e-12:
        die("controlDict endTime is not the registered %g" % EX.T_END)
    m = re.search(r"^\s*writeInterval\s+([0-9.]+)\s*;", cd, re.M)
    if not m or abs(float(m.group(1)) - EX.WRITE_DT) > 1e-12:
        die("controlDict writeInterval is not the registered %g" % EX.WRITE_DT)
    tp = open(os.path.join(dest, "constant", "thermophysicalProperties")).read()
    m = re.search(r"molWeight\s+([0-9.eE+-]+)\s*;", tp)
    if not m or abs(float(m.group(1)) - EX.MOL_WEIGHT) > 1e-9:
        die("thermophysicalProperties molWeight is not exact_f24.MOL_WEIGHT")
    dp = open(os.path.join(dest, "system", "decomposeParDict")).read()
    m = re.search(r"numberOfSubdomains\s+([0-9]+)\s*;", dp)
    if not m or int(m.group(1)) != EX.RANKS:
        die("decomposeParDict numberOfSubdomains is not the registered %d" % EX.RANKS)

    if foam("blockMesh", dest, os.path.join(dest, "log.blockMesh")) != 0:
        die("blockMesh failed; see %s/log.blockMesh" % dest)
    if foam("checkMesh", dest, os.path.join(dest, "log.checkMesh")) != 0:
        die("checkMesh failed; see %s/log.checkMesh" % dest)
    cm = open(os.path.join(dest, "log.checkMesh"), errors="replace").read()
    if "Mesh OK" not in cm:
        die("checkMesh did not report `Mesh OK`")
    m_cells = re.search(r"^\s*cells:\s+(\d+)", cm, re.M)
    m_no = re.search(r"non-orthogonality Max: ([0-9.eE+-]+)", cm)
    m_sk = re.search(r"Max skewness = ([0-9.eE+-]+)", cm)
    m_ar = re.search(r"Max aspect ratio = ([0-9.eE+-]+)", cm)
    if not (m_cells and m_no and m_sk and m_ar):
        die("could not read cells / non-orthogonality / skewness / aspect ratio from log.checkMesh")
    cells = int(m_cells.group(1))
    if cells != (nxa + nxb) * ny:
        die("built mesh has %d cells, level %s registers %d" % (cells, level, (nxa + nxb) * ny))
    if float(m_no.group(1)) > MAX_NON_ORTHO:
        die("max non-orthogonality %s exceeds the %g deg gate" % (m_no.group(1), MAX_NON_ORTHO))
    if float(m_sk.group(1)) > MAX_SKEW:
        die("max skewness %s exceeds the gate %g" % (m_sk.group(1), MAX_SKEW))
    with open(os.path.join(dest, "MESH_LINE.txt"), "w") as f:
        f.write("level=%s n=%d cells=%d dt=%r steps=%d max_non_orthogonality_deg=%s max_skewness=%s max_aspect_ratio=%s "
                "aspect_advisory=%g gate_non_ortho=%g gate_skew=%g source=log.checkMesh\n"
                % (level, n, cells, dt, steps, m_no.group(1), m_sk.group(1), m_ar.group(1), ASPECT_ADVISORY,
                   MAX_NON_ORTHO, MAX_SKEW))

    os.makedirs(os.path.join(dest, "0"))
    if foam("postProcess -func writeCellCentres -time 0", dest, os.path.join(dest, "log.writeCellCentres")) != 0:
        die("postProcess writeCellCentres failed")
    if foam("postProcess -func writeCellVolumes -time 0", dest, os.path.join(dest, "log.writeCellVolumes")) != 0:
        die("postProcess writeCellVolumes failed")
    C = FIO.read_field(os.path.join(dest, "0", "C"))
    if C["kind"] != "vector" or C["internal"] is None or len(C["internal"]) != cells:
        die("0/C does not carry %d cell centres" % cells)
    V = FIO.read_field(os.path.join(dest, "0", "V"))
    if V["kind"] != "scalar" or V["internal"] is None or len(V["internal"]) != cells:
        die("0/V does not carry %d cell volumes" % cells)
    xc, yc = C["internal"][:, 0], C["internal"][:, 1]
    nbox = int(EX.box_mask(xc, yc).sum())
    if nbox < 16:
        die("the sampling box selects only %d cells" % nbox)
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "p.template"), os.path.join(dest, "0", "p"),
                            {"__INTERNALFIELD__": FIO.fmt_list(np.full(cells, EX.P1), "scalar"), "__P1__": repr(EX.P1)})
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "T.template"), os.path.join(dest, "0", "T"),
                            {"__INTERNALFIELD__": FIO.fmt_list(np.full(cells, EX.T1), "scalar"), "__T1__": repr(EX.T1)})
    internal = np.column_stack([np.full(cells, EX.U1), np.zeros(cells), np.zeros(cells)])
    # 0/U LAST OF ALL: the age guard dates every endTime field against it.
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "U.template"), os.path.join(dest, "0", "U"),
                            {"__INTERNALFIELD__": FIO.fmt_list(internal, "vector"), "__U1__": repr(EX.U1)})
    print("built level %s at %s: %d cells (%d+%d x %d), dt %r, %d steps, non-ortho %s, skew %s, aspect %s, box cells %d; 0/U written last"
          % (level, dest, cells, nxa, nxb, ny, dt, steps, m_no.group(1), m_sk.group(1), m_ar.group(1), nbox))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
