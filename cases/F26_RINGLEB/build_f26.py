#!/usr/bin/env python3
"""
F26 -- BUILD ONE LADDER LEVEL (or a scratch instrument grid) into a destination
directory (called by run_f26.sh once per level; lineage cases/F23_HP_WEDGE/build_f23.py).
REFUSES a destination holding `0/`, a numeric time directory or processor*
directories; deletes nothing; refuses a destination inside the tracked case
tree; refuses to build a registered level under --scratch.  Mesher and
postProcess run here, so never call it against the case tree.

  1. copy the fixed dictionaries; template blockMeshDict (N_ALONG, N_ACROSS)
     and controlDict (rhoSimpleFoam: deltaT 1, endTime = the level's registered
     SIMPLE ITERATION COUNT, writeInterval)
  2. blockMesh on the unit square (TOPOLOGY), then REMAP constant/polyMesh/points
     through the exact flow-net map (every node snapped to exact_f26.lattice),
     checkMesh -> `Mesh OK`, MESH_STANDARD section 3 gates enforced
     (non-orthogonality 70 deg, skewness 4), aspect ratio recorded (advisory)
  3. mkdir 0/, `postProcess -func writeCellCentres|writeCellVolumes` -> 0/C, 0/V;
     0/C and 0/V cross-checked against the model geometry (knp_f26.geometry) to 1e-9
  4. write 0/p, 0/T (exact at cell centres; exact at the inflow/outflow FACE
     centres from 0/C's boundary field), then 0/U LAST (the age guard's datum).
Zero `assert` (L-332).
"""
import os
import re
import sys
import json
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_f26 as EX            # noqa: E402
import knp_f26 as K               # noqa: E402
import foam_io_f26 as FIO         # noqa: E402
import numpy as np                # noqa: E402

CASE_SRC = os.path.join(HERE, "case")
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
MAX_NON_ORTHO = 70.0
MAX_SKEW = 4.0
ASPECT_ADVISORY = 1000.0
GEOM_TOL = 1e-9


def die(msg, rc=1):
    sys.stderr.write("ABORT (build_f26): %s\n" % msg)
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


def remap_points(dest, lat, na, nc):
    """snap every blockMesh unit-square node to the exact lattice node it indexes."""
    ppath = os.path.join(dest, "constant", "polyMesh", "points")
    head, pts, tail = FIO.read_points(ppath)
    i = np.rint(pts[:, 0] * na).astype(int)
    j = np.rint(pts[:, 1] * nc).astype(int)
    if np.max(np.abs(pts[:, 0] * na - i)) > 1e-9 or np.max(np.abs(pts[:, 1] * nc - j)) > 1e-9:
        die("blockMesh did not place the unit-square nodes on the i/N lattice; the remap would not be exact")
    if pts.shape[0] != (na + 1) * (nc + 1) * 2:
        die("points file carries %d nodes, expected %d" % (pts.shape[0], (na + 1) * (nc + 1) * 2))
    new = np.column_stack([lat["X"][j, i], lat["Y"][j, i], pts[:, 2]])
    FIO.write_points(ppath, head, new, tail)
    return pts.shape[0]


def main(argv):
    usage = ("usage: build_f26.py <dest_dir> --level <coarse|medium|fine>  |  "
             "<dest_dir> --scratch NA NC --steps S --write-every W")
    steps = write_every = None
    if len(argv) == 3 and argv[1] == "--level":
        dest, level = os.path.abspath(argv[0]), argv[2]
        na, nc = EX.level_shape(level)
        steps, write_every = EX.steps_of(level), EX.write_every_of(level)
    elif len(argv) == 8 and argv[1] == "--scratch" and argv[4] == "--steps" and argv[6] == "--write-every":
        dest, level = os.path.abspath(argv[0]), "SCRATCH(not_a_ladder_level)"
        na, nc, steps, write_every = int(argv[2]), int(argv[3]), int(argv[5]), int(argv[7])
        if (na, nc) in [(a, b) for _n, a, b in EX.LEVELS]:
            die("--scratch may not build a registered ladder level")
    else:
        die(usage)
    if steps % write_every != 0:
        die("steps %d is not a multiple of write-every %d" % (steps, write_every))
    if os.path.realpath(dest).startswith(os.path.realpath(CASE_SRC)):
        die("destination %s lies inside the tracked case tree; refused" % dest, rc=2)
    refuse_if_answered(dest)
    for sub in ("system", "constant"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    for f in ("fvSchemes", "fvSolution"):
        shutil.copy(os.path.join(CASE_SRC, "system", f), os.path.join(dest, "system", f))
    for f in ("thermophysicalProperties", "turbulenceProperties"):
        shutil.copy(os.path.join(CASE_SRC, "constant", f), os.path.join(dest, "constant", f))
    tp = open(os.path.join(dest, "constant", "thermophysicalProperties")).read()
    m = re.search(r"molWeight\s+([0-9eE+\-.]+)\s*;", tp)
    mc = re.search(r"\bCp\s+([0-9eE+\-.]+)\s*;", tp)
    if not m or abs(float(m.group(1)) - EX.MOL_WEIGHT) > 1e-9 or not mc or abs(float(mc.group(1)) - EX.CP) > 1e-15:
        die("thermophysicalProperties molWeight/Cp are not exact_f26's")

    # ---- the lattice, the model geometry and the registered dt on THIS mesh
    lat = EX.lattice(na, nc)
    g = K.geometry(lat["X"], lat["Y"])
    # rhoSimpleFoam: the time axis IS the SIMPLE iteration index.  deltaT is 1 and
    # endTime is the registered iteration count, so rule 4's `last time == endTime`
    # reads `every registered iteration ran`.  dt_phys is the explicit-scheme time
    # step this mesh would have carried at CO_TARGET -- recorded as a registration
    # instrument reading only (it is what knp_f26 measured in prereg section 2); it
    # does not enter the dictionaries and no gate depends on it.
    dt_phys = K.dt_for_co_geometry(g, EX.CO_TARGET)
    dt = 1
    end_time = steps
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "blockMeshDict.template"),
                            os.path.join(dest, "system", "blockMeshDict"),
                            {"__N_ALONG__": str(na), "__N_ACROSS__": str(nc)})
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "controlDict.template"),
                            os.path.join(dest, "system", "controlDict"),
                            {"__END_TIME__": str(end_time), "__WRITE_EVERY__": str(write_every)})
    cdt = open(os.path.join(dest, "system", "controlDict")).read()
    if not re.search(r"^\s*application\s+rhoSimpleFoam\s*;", cdt, re.M):
        die("controlDict does not select rhoSimpleFoam; the registered solver is rhoSimpleFoam (prereg section 2)")
    if not re.search(r"^\s*deltaT\s+1\s*;", cdt, re.M):
        die("controlDict deltaT is not 1; the SIMPLE time axis must be the iteration index")

    if foam("blockMesh", dest, os.path.join(dest, "log.blockMesh")) != 0:
        die("blockMesh failed; see %s/log.blockMesh" % dest)
    n_pts = remap_points(dest, lat, na, nc)
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
    if cells != na * nc:
        die("built mesh has %d cells, registers %d" % (cells, na * nc))
    if float(m_no.group(1)) > MAX_NON_ORTHO:
        die("max non-orthogonality %s exceeds the %g deg gate" % (m_no.group(1), MAX_NON_ORTHO))
    if float(m_sk.group(1)) > MAX_SKEW:
        die("max skewness %s exceeds the gate %g" % (m_sk.group(1), MAX_SKEW))
    aspect_note = "advisory" if float(m_ar.group(1)) > ASPECT_ADVISORY else "under_advisory"
    with open(os.path.join(dest, "MESH_LINE.txt"), "w") as f:
        f.write("level=%s n_along=%d n_across=%d cells=%d nodes_remapped=%d max_non_orthogonality_deg=%s max_skewness=%s "
                "max_aspect_ratio=%s aspect_%s=%g gate_non_ortho=%g gate_skew=%g deltaT=%d iterations=%d endTime=%d "
                "write_every=%d source=log.checkMesh\n"
                % (level, na, nc, cells, n_pts, m_no.group(1), m_sk.group(1), m_ar.group(1), aspect_note, ASPECT_ADVISORY,
                   MAX_NON_ORTHO, MAX_SKEW, dt, steps, end_time, write_every))

    os.makedirs(os.path.join(dest, "0"))
    # a placeholder p is needed by postProcess only to read the mesh? No: writeCellCentres needs no fields.
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
    # ---- geometry cross-check: the mesh the solver sees IS the model's (band rests on it)
    dC = np.max(np.abs(C["internal"][:, :2] - g["C"]))
    dV = np.max(np.abs(V["internal"] - g["V"]))
    if dC > GEOM_TOL or dV > GEOM_TOL:
        die("mesh geometry disagrees with knp_f26.geometry: max |dC| %.3e, max |dV| %.3e (tol %g); the model would not "
            "describe this mesh" % (dC, dV, GEOM_TOL))
    for pn in ("inflow", "outflow"):
        if pn not in C["patches"] or C["patches"][pn] is None:
            die("0/C carries no face-centre list for patch %s" % pn)
        fc = C["patches"][pn][:, :2]
        idx = g["bidx"][pn]
        if fc.shape[0] != idx.size or np.max(np.abs(fc - g["Cf"][idx])) > GEOM_TOL:
            die("patch %s face centres disagree with the model geometry" % pn)
    # ---- the exact fields
    ex_c = EX.fields_at(C["internal"][:, 0], C["internal"][:, 1])
    ex_b = dict((pn, EX.fields_at(C["patches"][pn][:, 0], C["patches"][pn][:, 1])) for pn in ("inflow", "outflow"))
    if float(np.max(ex_c["M"])) >= 1.0:
        die("a cell centre is supersonic: M = %.4f" % float(np.max(ex_c["M"])))
    # p carries the single subsonic-OUTFLOW condition; T carries one of the three
    # subsonic-INFLOW conditions.  Each template holds exactly the placeholders its
    # own Dirichlet patch needs and write_from_template refuses a missing one, so a
    # boundary-condition edit that drops a patch cannot pass here silently.
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "p.template"), os.path.join(dest, "0", "p"),
                            {"__INTERNALFIELD__": FIO.fmt_list(ex_c["p"], "scalar"),
                             "__OUTFLOW__": FIO.fmt_list(ex_b["outflow"]["p"], "scalar")})
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "T.template"), os.path.join(dest, "0", "T"),
                            {"__INTERNALFIELD__": FIO.fmt_list(ex_c["T"], "scalar"),
                             "__INFLOW__": FIO.fmt_list(ex_b["inflow"]["T"], "scalar")})
    Uc = np.column_stack([ex_c["u"], ex_c["v"], np.zeros(cells)])
    Ub = dict((pn, np.column_stack([ex_b[pn]["u"], ex_b[pn]["v"], np.zeros(ex_b[pn]["u"].size)])) for pn in ex_b)
    # 0/U LAST OF ALL: the age guard dates every checkpoint field against it.
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "U.template"), os.path.join(dest, "0", "U"),
                            {"__INTERNALFIELD__": FIO.fmt_list(Uc, "vector"),
                             "__INFLOW__": FIO.fmt_list(Ub["inflow"], "vector")})
    with open(os.path.join(dest, "BUILD_LINE.json"), "w") as f:
        json.dump(dict(level=level, n_along=na, n_across=nc, cells=cells, deltaT=dt, iterations=steps, end_time=end_time,
                       dt_phys_explicit_at_CO_TARGET=dt_phys, solver="rhoSimpleFoam",
                       write_every=write_every, M_max_cells=float(np.max(ex_c["M"])), M_min_cells=float(np.min(ex_c["M"])),
                       geometry_max_dC=float(dC), geometry_max_dV=float(dV), non_ortho_model_deg=g["nonortho_max"]), f, indent=1)
    print("built %s at %s: %d cells, non-ortho %s, skew %s, aspect %s; geometry == model to %.1e/%.1e; deltaT %d x %d "
          "SIMPLE iterations = endTime %d, write every %d; M in [%.4f, %.4f]; 0/U written last"
          % (level, dest, cells, m_no.group(1), m_sk.group(1), m_ar.group(1), dC, dV, dt, steps, end_time, write_every,
             float(np.min(ex_c["M"])), float(np.max(ex_c["M"]))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
