#!/usr/bin/env python3
"""
F25 -- BUILD ONE LADDER LEVEL into a destination directory (called by
run_f25.sh once per level; lineage cases/F23_HP_WEDGE/build_f23.py).
REFUSES a destination holding `0/`, a numeric time directory or processor*
directories; deletes nothing; refuses a destination inside the tracked case
tree.  Mesher and postProcess run here, so never call it against the case tree.

  1. template blockMeshDict (NX, NR, L, SIDE); copy the fixed dictionaries
     (controlDict, fvSchemes, fvSolution, decomposeParDict,
     transportProperties, turbulenceProperties, fvOptions)
  2. blockMesh, checkMesh -> `Mesh OK`, MESH_STANDARD section 3 gates enforced
     (3.1 non-orthogonality 70 deg, 3.2 skewness 4); aspect ratio RECORDED in
     MESH_LINE.txt (3.3: advisory at 1000, never a lone rejection)
  3. mkdir 0/, copy 0/p, `postProcess -func writeCellCentres` -> 0/C and
     `postProcess -func writeCellVolumes` -> 0/V; geometry cross-checked
     against exact_f25 (centres at (j + 1/2) h, volumes h^3) to 1e-9
  4. write 0/U = (0 0 0) everywhere, LAST of all (the age guard's datum).
decomposePar is the LAUNCHER's step, after 0/U.  Zero `assert` (L-332).
"""
import os
import re
import sys
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_f25 as EX            # noqa: E402
import foam_io_f25 as FIO          # noqa: E402
import numpy as np                 # noqa: E402

CASE_SRC = os.path.join(HERE, "case")
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
MAX_NON_ORTHO = 70.0               # docs/standards/MESH_STANDARD.md section 3.1 (hard gate)
MAX_SKEW = 4.0                     # section 3.2 (hard gate, boundary faces included)
ASPECT_ADVISORY = 1000.0           # section 3.3 (advisory, never a lone rejection)


def die(msg, rc=1):
    sys.stderr.write("ABORT (build_f25): %s\n" % msg)
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
    usage = "usage: build_f25.py <dest_dir> --level <coarse|medium|fine>  |  <dest_dir> --scratch NR NX"
    if len(argv) == 3 and argv[1] == "--level":
        dest, level = os.path.abspath(argv[0]), argv[2]
        lv = dict((nm, (nr, nx)) for nm, nr, nx in EX.LEVELS)
        if level not in lv:
            die("unknown level %r" % level)
        nr, nx = lv[level]
    elif len(argv) == 4 and argv[1] == "--scratch":
        dest, level = os.path.abspath(argv[0]), "SCRATCH(not_a_ladder_level)"
        nr, nx = int(argv[2]), int(argv[3])
        if (nr, nx) in [(a, b) for _n, a, b in EX.LEVELS]:
            die("--scratch may not build a registered ladder level")
    else:
        die(usage)
    if os.path.realpath(dest).startswith(os.path.realpath(CASE_SRC)):
        die("destination %s lies inside the tracked case tree; refused" % dest, rc=2)
    refuse_if_answered(dest)
    for sub in ("system", "constant"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    for f in ("controlDict", "fvSchemes", "fvSolution", "decomposeParDict"):
        shutil.copy(os.path.join(CASE_SRC, "system", f), os.path.join(dest, "system", f))
    for f in ("transportProperties", "turbulenceProperties", "fvOptions"):
        shutil.copy(os.path.join(CASE_SRC, "constant", f), os.path.join(dest, "constant", f))
    lx = EX.SIDE / nr * nx           # the scratch arm keeps cubic cells: L follows NX
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "blockMeshDict.template"),
                            os.path.join(dest, "system", "blockMeshDict"),
                            {"__NX__": str(nx), "__NR__": str(nr), "__L__": repr(lx), "__SIDE__": repr(EX.SIDE)})
    cd = open(os.path.join(dest, "system", "controlDict")).read()
    m = re.search(r"^\s*endTime\s+([0-9]+)\s*;", cd, re.M)
    if not m or int(m.group(1)) != EX.N_ITER:
        die("controlDict endTime is not the registered %d" % EX.N_ITER)
    tp = open(os.path.join(dest, "constant", "transportProperties")).read()
    m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
    if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
        die("transportProperties nu is not exact_f25.NU")
    fo = open(os.path.join(dest, "constant", "fvOptions")).read()
    m = re.search(r"U\s+\(\(\s*([0-9eE+\-.]+)\s+0\s+0\s*\)\s+0\s*\)\s*;", fo)
    if not m or abs(float(m.group(1)) - EX.G) > 1e-15:
        die("fvOptions momentum source is not exact_f25.G = %.17g" % EX.G)
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
    if cells != nr * nr * nx:
        die("built mesh has %d cells, level %s registers %d" % (cells, level, nr * nr * nx))
    if float(m_no.group(1)) > MAX_NON_ORTHO:
        die("max non-orthogonality %s exceeds the %g deg gate (MESH_STANDARD 3.1)" % (m_no.group(1), MAX_NON_ORTHO))
    if float(m_sk.group(1)) > MAX_SKEW:
        die("max skewness %s exceeds the gate %g (MESH_STANDARD 3.2)" % (m_sk.group(1), MAX_SKEW))
    aspect_note = "advisory" if float(m_ar.group(1)) > ASPECT_ADVISORY else "under_advisory"
    with open(os.path.join(dest, "MESH_LINE.txt"), "w") as f:
        f.write("level=%s nr=%d nx=%d cells=%d max_non_orthogonality_deg=%s max_skewness=%s max_aspect_ratio=%s "
                "aspect_%s=%g gate_non_ortho=%g gate_skew=%g source=log.checkMesh\n"
                % (level, nr, nx, cells, m_no.group(1), m_sk.group(1), m_ar.group(1), aspect_note, ASPECT_ADVISORY,
                   MAX_NON_ORTHO, MAX_SKEW))

    os.makedirs(os.path.join(dest, "0"))
    shutil.copy(os.path.join(CASE_SRC, "0", "p"), os.path.join(dest, "0", "p"))
    if foam("postProcess -func writeCellCentres -time 0", dest, os.path.join(dest, "log.writeCellCentres")) != 0:
        die("postProcess writeCellCentres failed")
    if foam("postProcess -func writeCellVolumes -time 0", dest, os.path.join(dest, "log.writeCellVolumes")) != 0:
        die("postProcess writeCellVolumes failed")
    C = FIO.read_field(os.path.join(dest, "0", "C"))
    if C["kind"] != "vector" or C["internal"] is None or len(C["internal"]) != cells:
        die("0/C does not carry %d cell centres" % cells)
    try:
        Vv = FIO.scalar_field_values(os.path.join(dest, "0", "V"), cells)   # cubic cells: OpenFOAM writes 0/V `uniform`
    except FIO.FieldFormatError as e:
        die("0/V does not carry %d cell volumes: %s" % (cells, e))
    V = dict(internal=Vv)
    # geometry cross-check against the model's own cubic geometry: every centre
    # must sit at ((i+1/2) h, (j+1/2) h, (k+1/2) h) and every volume must be h^3
    h = EX.h_of(nr)
    idx = np.rint(C["internal"] / h - 0.5)
    if np.max(np.abs(C["internal"] - (idx + 0.5) * h)) > 1e-9 or np.max(np.abs(V["internal"] - h ** 3)) > 1e-9 * h ** 3:
        die("mesh geometry disagrees with exact_f25 (centres not on the cubic lattice or volumes not h^3); the model "
            "would not describe this mesh")
    if np.min(idx[:, 1]) != 0 or np.max(idx[:, 1]) != nr - 1 or np.min(idx[:, 2]) != 0 or np.max(idx[:, 2]) != nr - 1:
        die("cross-section index range is not 0..%d" % (nr - 1))
    # 0/U LAST OF ALL: the age guard dates every endTime field against it.
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "U.template"), os.path.join(dest, "0", "U"),
                            {"__INTERNALFIELD__": FIO.fmt_list(np.zeros((cells, 3)), "vector")})
    print("built level %s at %s: %d cells, non-ortho %s, skew %s, aspect %s; geometry == model; 0/U written last"
          % (level, dest, cells, m_no.group(1), m_sk.group(1), m_ar.group(1)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
