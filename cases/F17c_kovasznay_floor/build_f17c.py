#!/usr/bin/env python3
"""
F17 -- BUILD ONE LADDER LEVEL into a destination directory.

Called by run_f17.sh once per level, and by nobody else in the case tree.  It
REFUSES a destination that already holds a `0/` or a numeric time directory
(rule 4's age guard is dated from 0/U, written LAST here) and deletes nothing.

Sequence (mesher and postProcess run here, so THIS SCRIPT IS COMPUTE-ADJACENT:
never call it against the tracked case tree, only against a run root or a
scratch copy):
  1. template blockMeshDict for the level, copy the fixed dictionaries
  2. blockMesh, checkMesh -> require `Mesh OK`, read max non-orthogonality and
     max skewness, REFUSE above MESH_STANDARD section 3 gates (70 deg, 4)
  3. write 0/p, then `postProcess -func writeCellCentres -time 0` -> 0/C
  4. write 0/U from 0/C: internalField = exact at the mesh's OWN cell centres;
     inlet/outlet = FACE-AVERAGED exact velocity over each face's own y-span
     (face centre from 0/C's patch values).  Written LAST of all.
Zero `assert` (L-332); refusals exit 2 or 1.
"""
import os
import re
import sys
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_f17c as EX            # noqa: E402
import foam_io_f17c as FIO          # noqa: E402

CASE_SRC = os.path.join(HERE, "case")
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
MAX_NON_ORTHO = 70.0
MAX_SKEW = 4.0


def die(msg, rc=1):
    sys.stderr.write("ABORT (build_f17c): %s\n" % msg)
    sys.exit(rc)


def foam(cmd, case_dir, log):
    full = ". %s > /dev/null 2>&1; %s -case %s > %s 2>&1" % (FOAM_BASHRC, cmd, case_dir, log)
    return subprocess.run(["bash", "-c", full]).returncode


def refuse_if_answered(dest):
    if os.path.isdir(dest):
        for d in os.listdir(dest):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?", d):
                die("%s already holds time directory %s. REFUSED, not deleted "
                    "(standing rule 4)." % (dest, d), rc=2)


def main(argv):
    if len(argv) != 3 or argv[1] != "--level":
        die("usage: build_f17c.py <dest_dir> --level <coarse|medium|fine>")
    dest, level = os.path.abspath(argv[0]), argv[2]
    lv = dict((n, (nx, ny)) for n, nx, ny in EX.LEVELS)
    if level not in lv:
        die("unknown level %r" % level)
    nx, ny = lv[level]
    if os.path.realpath(dest).startswith(os.path.realpath(CASE_SRC)):
        die("destination %s lies inside the tracked case tree; refused" % dest, rc=2)
    refuse_if_answered(dest)
    for sub in ("system", "constant"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    for f in ("fvSchemes", "fvSolution"):
        shutil.copy(os.path.join(CASE_SRC, "system", f), os.path.join(dest, "system", f))
    # L-346: the iteration count is PER LEVEL and is written from the frozen
    # registration, never copied from a dictionary that carries one number for
    # all three levels. That copy is exactly what F17b did.
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "controlDict.template"),
                            os.path.join(dest, "system", "controlDict"),
                            {"__ENDTIME__": str(EX.n_iter(level))})
    for f in ("transportProperties", "turbulenceProperties"):
        shutil.copy(os.path.join(CASE_SRC, "constant", f), os.path.join(dest, "constant", f))
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "blockMeshDict.template"),
                            os.path.join(dest, "system", "blockMeshDict"),
                            {"__NX__": str(nx), "__NY__": str(ny)})

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
    if cells != nx * ny:
        die("built mesh has %d cells, level %s registers %d" % (cells, level, nx * ny))
    if float(m_no.group(1)) > MAX_NON_ORTHO:
        die("max non-orthogonality %s exceeds the %g deg gate" % (m_no.group(1), MAX_NON_ORTHO))
    if float(m_sk.group(1)) > MAX_SKEW:
        die("max skewness %s exceeds the gate %g" % (m_sk.group(1), MAX_SKEW))
    with open(os.path.join(dest, "MESH_LINE.txt"), "w") as f:
        f.write("level=%s nx=%d ny=%d cells=%d max_non_orthogonality_deg=%s max_skewness=%s "
                "gate_non_ortho=%g gate_skew=%g source=log.checkMesh\n"
                % (level, nx, ny, cells, m_no.group(1), m_sk.group(1), MAX_NON_ORTHO, MAX_SKEW))

    os.makedirs(os.path.join(dest, "0"))
    shutil.copy(os.path.join(CASE_SRC, "0", "p"), os.path.join(dest, "0", "p"))
    if foam("postProcess -func writeCellCentres -time 0", dest,
            os.path.join(dest, "log.writeCellCentres")) != 0:
        die("postProcess writeCellCentres failed")
    C = FIO.read_field(os.path.join(dest, "0", "C"))
    if C["kind"] != "vector" or C["internal"] is None or len(C["internal"]) != cells:
        die("0/C does not carry %d cell centres" % cells)
    xc, yc = C["internal"][:, 0], C["internal"][:, 1]
    h = EX.h_of(nx)
    import numpy as np
    internal = np.column_stack([EX.u_exact(xc, yc), EX.v_exact(xc, yc), np.zeros(cells)])
    patch_vals = {}
    for name, xb in (("inlet", EX.X0), ("outlet", EX.X1)):
        fc = C["patches"].get(name)
        if fc is None or len(fc) != ny:
            die("0/C patch %s does not carry %d face centres" % (name, ny))
        if np.max(np.abs(fc[:, 0] - xb)) > 1e-12:
            die("patch %s face centres are not at x = %g" % (name, xb))
        ya, yb = fc[:, 1] - 0.5 * h, fc[:, 1] + 0.5 * h
        patch_vals[name] = np.column_stack([EX.u_face_avg_x(xb, ya, yb),
                                            EX.v_face_avg_x(xb, ya, yb), np.zeros(ny)])
    net = float(np.sum(patch_vals["outlet"][:, 0]) - np.sum(patch_vals["inlet"][:, 0])) * h
    if abs(net) > 1e-12:
        die("net boundary flux %.3e is not zero; adjustPhi would refuse the case" % net)
    # 0/U LAST OF ALL: the age guard dates every endTime field against it.
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "U.template"),
                            os.path.join(dest, "0", "U"),
                            {"__INTERNALFIELD__": FIO.fmt_list(internal, "vector"),
                             "__INLET__": FIO.fmt_list(patch_vals["inlet"], "vector"),
                             "__OUTLET__": FIO.fmt_list(patch_vals["outlet"], "vector")})
    print("built level %s at %s: %d cells, non-ortho %s, skew %s, net boundary flux %.2e; 0/U written last"
          % (level, dest, cells, m_no.group(1), m_sk.group(1), net))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
