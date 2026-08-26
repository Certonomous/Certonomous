#!/usr/bin/env python3
"""
F18 -- BUILD ONE LADDER LEVEL into a destination directory (called by
run_f18.sh once per level).  REFUSES a destination holding `0/` or a numeric
time directory; deletes nothing; refuses a destination inside the tracked case
tree.  Mesher and postProcess run here, so never call it against the case tree.

  1. template blockMeshDict (N) and controlDict (dt); copy fixed dictionaries
  2. blockMesh, checkMesh -> `Mesh OK`, MESH_STANDARD section 3 gates enforced
  3. mkdir 0/, `postProcess -func writeCellCentres -time 0` -> 0/C
  4. write 0/p (exact at t = 0 at the mesh's own centres), then 0/U LAST.
Zero `assert` (L-332).
"""
import os
import re
import sys
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_f18 as EX            # noqa: E402
import foam_io_f18 as FIO          # noqa: E402
import numpy as np                 # noqa: E402

CASE_SRC = os.path.join(HERE, "case")
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
MAX_NON_ORTHO = 70.0
MAX_SKEW = 4.0


def die(msg, rc=1):
    sys.stderr.write("ABORT (build_f18): %s\n" % msg)
    sys.exit(rc)


def foam(cmd, case_dir, log):
    full = ". %s > /dev/null 2>&1; %s -case %s > %s 2>&1" % (FOAM_BASHRC, cmd, case_dir, log)
    return subprocess.run(["bash", "-c", full]).returncode


def refuse_if_answered(dest):
    if os.path.isdir(dest):
        for d in os.listdir(dest):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?", d):
                die("%s already holds time directory %s. REFUSED, not deleted (rule 4)." % (dest, d), rc=2)


def main(argv):
    if len(argv) != 3 or argv[1] != "--level":
        die("usage: build_f18.py <dest_dir> --level <coarse|medium|fine>")
    dest, level = os.path.abspath(argv[0]), argv[2]
    lv = dict((nm, (n, s)) for nm, n, s in EX.LEVELS)
    if level not in lv:
        die("unknown level %r" % level)
    n, steps = lv[level]
    dt = EX.dt_of(steps)
    if os.path.realpath(dest).startswith(os.path.realpath(CASE_SRC)):
        die("destination %s lies inside the tracked case tree; refused" % dest, rc=2)
    refuse_if_answered(dest)
    for sub in ("system", "constant"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    for f in ("fvSchemes", "fvSolution"):
        shutil.copy(os.path.join(CASE_SRC, "system", f), os.path.join(dest, "system", f))
    shutil.copy(os.path.join(CASE_SRC, "constant", "transportProperties"),
                os.path.join(dest, "constant", "transportProperties"))
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "blockMeshDict.template"),
                            os.path.join(dest, "system", "blockMeshDict"), {"__N__": str(n)})
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "controlDict.template"),
                            os.path.join(dest, "system", "controlDict"), {"__DT__": repr(dt)})
    cd = open(os.path.join(dest, "system", "controlDict")).read()
    m = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", cd, re.M)
    if not m or abs(float(m.group(1)) - EX.T_END) > 1e-12:
        die("controlDict endTime is not the registered %g" % EX.T_END)

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
    if not (m_cells and m_no and m_sk):
        die("could not read cells / non-orthogonality / skewness from log.checkMesh")
    cells = int(m_cells.group(1))
    if cells != n * n:
        die("built mesh has %d cells, level %s registers %d" % (cells, level, n * n))
    if float(m_no.group(1)) > MAX_NON_ORTHO:
        die("max non-orthogonality %s exceeds the %g deg gate" % (m_no.group(1), MAX_NON_ORTHO))
    if float(m_sk.group(1)) > MAX_SKEW:
        die("max skewness %s exceeds the gate %g" % (m_sk.group(1), MAX_SKEW))
    with open(os.path.join(dest, "MESH_LINE.txt"), "w") as f:
        f.write("level=%s n=%d cells=%d dt=%r max_non_orthogonality_deg=%s max_skewness=%s "
                "gate_non_ortho=%g gate_skew=%g source=log.checkMesh\n"
                % (level, n, cells, dt, m_no.group(1), m_sk.group(1), MAX_NON_ORTHO, MAX_SKEW))

    os.makedirs(os.path.join(dest, "0"))
    if foam("postProcess -func writeCellCentres -time 0", dest, os.path.join(dest, "log.writeCellCentres")) != 0:
        die("postProcess writeCellCentres failed")
    C = FIO.read_field(os.path.join(dest, "0", "C"))
    if C["kind"] != "vector" or C["internal"] is None or len(C["internal"]) != cells:
        die("0/C does not carry %d cell centres" % cells)
    xc, yc = C["internal"][:, 0], C["internal"][:, 1]
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "p.template"), os.path.join(dest, "0", "p"),
                            {"__INTERNALFIELD__": FIO.fmt_list(EX.p_exact(xc, yc, 0.0), "scalar")})
    internal = np.column_stack([EX.u_exact(xc, yc, 0.0), EX.v_exact(xc, yc, 0.0), np.zeros(cells)])
    # 0/U LAST OF ALL: the age guard dates every endTime field against it.
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "U.template"), os.path.join(dest, "0", "U"),
                            {"__INTERNALFIELD__": FIO.fmt_list(internal, "vector")})
    print("built level %s at %s: %d cells, dt %r, non-ortho %s, skew %s; 0/U written last"
          % (level, dest, cells, dt, m_no.group(1), m_sk.group(1)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
