#!/usr/bin/env python3
"""
F27 -- BUILD ONE LADDER LEVEL into a destination directory (called by
run_f27.sh once per level; lineage cases/F25_DUCT3D/build_f25.py).
REFUSES a destination holding `0/`, a numeric time directory or processor*
directories; deletes nothing; refuses a destination inside the tracked case
tree.  Mesher and postProcess run here, so never call it against the case tree.

  1. template blockMeshDict (NC, NR, NZ) and controlDict (DT); copy the fixed
     dictionaries (fvSchemes, fvSolution, decomposeParDict, transportProperties,
     turbulenceProperties, fvOptions)
  2. blockMesh, checkMesh -> `Mesh OK`, MESH_STANDARD section 3 gates enforced
     (3.1 non-orthogonality 70 deg, 3.2 skewness 4); aspect ratio RECORDED in
     MESH_LINE.txt (3.3: advisory at 1000, never a lone rejection)
  3. MESH_STANDARD section 9.2 READ-BACK: every `simpleGrading` triple is read
     back OUT OF THE WRITTEN DICTIONARY (never out of the parameter that was
     requested) and must be (1 1 1) in all five blocks; the built mesh's own
     min/max cell volume and volume ratio are recorded beside it.
  4. mkdir 0/, copy 0/p, `postProcess -func writeCellCentres` -> 0/C and
     `-func writeCellVolumes` -> 0/V; the geometry is cross-checked against
     exact_f27 (cell count, max radius, total volume) AND the level's
     REGISTERED same-stencil reference W_REF_MESH is RECOMPUTED from the built
     0/C and 0/V and must match to exact_f27.W_REF_TOL -- the pin that proves
     the mesh that ran is the mesh the band was registered against.
  5. write 0/U = the EXACT Bessel solution at t = 0 at the mesh's own cell
     centres, LAST of all (the age guard's datum).
decomposePar is the LAUNCHER's step, after 0/U.  Zero `assert` (L-332).
"""
import os
import re
import sys
import math
import json
import shutil
import subprocess

if not __debug__:
    sys.stderr.write("REFUSED: build_f27.py must not run under `python3 -O`.\n")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_f27 as EX            # noqa: E402
import foam_io_f27 as FIO         # noqa: E402
import numpy as np                # noqa: E402

CASE_SRC = os.path.join(HERE, "case")
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
MAX_NON_ORTHO = 70.0               # docs/standards/MESH_STANDARD.md section 3.1 (hard gate)
MAX_SKEW = 4.0                     # section 3.2 (hard gate, boundary faces included)
ASPECT_ADVISORY = 1000.0           # section 3.3 (advisory, never a lone rejection)
VOLUME_RATIO_BOUND = 8.0           # sanity bound on max/min cell volume; RECORDED, and a butterfly
                                   # whose ratio ran away would be a different mesh family
N_BLOCKS = 5                       # one Cartesian core + four O-ring blocks


def die(msg, rc=1):
    sys.stderr.write("ABORT (build_f27): %s\n" % msg)
    sys.exit(rc)


def foam(cmd, case_dir, log):
    # `set -u` is never in force here (L-339: the bashrc reads unbound variables).
    # L-343: USER is exported before the bashrc is sourced, because the bashrc
    # resolves WM_PROJECT_USER_DIR from it and a cron-started runner carries none.
    full = ('export USER="${USER:-${LOGNAME:-$(id -un)}}"; . %s > /dev/null 2>&1; '
            '%s -case %s > %s 2>&1' % (FOAM_BASHRC, cmd, case_dir, log))
    return subprocess.run(["bash", "-c", full]).returncode


def refuse_if_answered(dest):
    if os.path.isdir(dest):
        for d in os.listdir(dest):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?", d) or re.fullmatch(r"processor[0-9]+", d):
                die("%s already holds %s. REFUSED, not deleted (rule 4)." % (dest, d), rc=2)


def read_back_grading(dict_path):
    """MESH_STANDARD 9.2: the ACTUAL grading of every block, READ BACK OUT OF THE
    WRITTEN DICTIONARY.  The requested value is the thing that lied in F12; only
    the written one tells the truth."""
    text = open(dict_path).read()
    text = re.sub(r"//[^\n]*", "", text)
    trips = re.findall(r"simpleGrading\s*\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)", text)
    if len(trips) != N_BLOCKS:
        die("read-back found %d simpleGrading triples in %s, expected %d (MESH_STANDARD 9.2)"
            % (len(trips), dict_path, N_BLOCKS))
    vals = [tuple(float(x) for x in t) for t in trips]
    for v in vals:
        if max(abs(x - 1.0) for x in v) > 0.0:
            die("read-back: block grading %s is not exactly (1 1 1); this ladder registers NO grading "
                "parameter at any level (MESH_STANDARD 9.2)" % (v,))
    counts = re.findall(r"\)\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)\s*simpleGrading", text)
    if len(counts) != N_BLOCKS:
        die("read-back found %d block cell-count triples, expected %d" % (len(counts), N_BLOCKS))
    return dict(gradings=[list(v) for v in vals], block_counts=[[int(x) for x in c] for c in counts])


def main(argv):
    usage = "usage: build_f27.py <dest_dir> --level <coarse|medium|fine>  |  <dest_dir> --scratch NC NR NZ STEPS"
    if len(argv) == 3 and argv[1] == "--level":
        dest, level = os.path.abspath(argv[0]), argv[2]
        if level not in EX.NCNRNZ:
            die("unknown level %r" % level)
        nc, nr, nz = EX.NCNRNZ[level]
        steps = EX.STEPS[level]
        pin_reference = True
    elif len(argv) == 6 and argv[1] == "--scratch":
        dest, level = os.path.abspath(argv[0]), "SCRATCH(not_a_ladder_level)"
        nc, nr, nz, steps = (int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5]))
        if (nc, nr, nz) in EX.NCNRNZ.values():
            die("--scratch may not build a registered ladder level")
        pin_reference = False
    else:
        die(usage)
    if os.path.realpath(dest).startswith(os.path.realpath(CASE_SRC)):
        die("destination %s lies inside the tracked case tree; refused" % dest, rc=2)
    refuse_if_answered(dest)

    for sub in ("system", "constant"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    for f in ("fvSchemes", "fvSolution", "decomposeParDict"):
        shutil.copy(os.path.join(CASE_SRC, "system", f), os.path.join(dest, "system", f))
    for f in ("transportProperties", "turbulenceProperties", "fvOptions"):
        shutil.copy(os.path.join(CASE_SRC, "constant", f), os.path.join(dest, "constant", f))
    bm = os.path.join(dest, "system", "blockMeshDict")
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "blockMeshDict.template"), bm,
                            {"__NC__": str(nc), "__NR__": str(nr), "__NZ__": str(nz)})
    FIO.write_from_template(os.path.join(CASE_SRC, "system", "controlDict.template"),
                            os.path.join(dest, "system", "controlDict"),
                            {"__DT__": repr(EX.dt_of(steps))})

    # ---- the dictionaries on disk must carry the registered physics ----------
    cd = open(os.path.join(dest, "system", "controlDict")).read()
    m = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", cd, re.M)
    if not m or abs(float(m.group(1)) - EX.T_END) > 1e-12:
        die("controlDict endTime is not the registered %g" % EX.T_END)
    m = re.search(r"^\s*writeInterval\s+([0-9.]+)\s*;", cd, re.M)
    wi = float(m.group(1)) if m else 0.0
    if not wi or abs(EX.PERIOD / wi - round(EX.PERIOD / wi)) > 1e-12 or abs(EX.T_END / wi - round(EX.T_END / wi)) > 1e-12:
        die("writeInterval does not divide both PERIOD and endTime; t = endTime - PERIOD would not be written")
    tp = open(os.path.join(dest, "constant", "transportProperties")).read()
    m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
    if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
        die("transportProperties nu is not exact_f27.NU = %.17g" % EX.NU)
    fo = open(os.path.join(dest, "constant", "fvOptions")).read()
    m = re.search(r"type\s+cosine\s*;\s*frequency\s+([0-9.eE+\-]+)\s*;\s*amplitude\s+([0-9.eE+\-]+)\s*;"
                  r"\s*scale\s+\(\s*0\s+0\s+1\s*\)", fo)
    if not m or abs(float(m.group(1)) - EX.OMEGA / (2 * math.pi)) > 1e-15 or abs(float(m.group(2)) - EX.A_DRIVE) > 1e-15:
        die("fvOptions does not carry the registered cosine drive (frequency %.17g, amplitude %g, z-hat)"
            % (EX.OMEGA / (2 * math.pi), EX.A_DRIVE))
    dp = open(os.path.join(dest, "system", "decomposeParDict")).read()
    m = re.search(r"numberOfSubdomains\s+([0-9]+)\s*;", dp)
    if not m or int(m.group(1)) != EX.RANKS:
        die("decomposeParDict numberOfSubdomains is not the registered %d" % EX.RANKS)
    if nz % EX.RANKS:
        die("nz = %d is not divisible by %d ranks; the simple (1 1 %d) decomposition would be uneven"
            % (nz, EX.RANKS, EX.RANKS))

    grading = read_back_grading(bm)

    # ---- MESH ---------------------------------------------------------------
    if foam("blockMesh", dest, os.path.join(dest, "log.blockMesh")) != 0:
        die("blockMesh failed; see %s/log.blockMesh. MESH_STANDARD 8.2: a blockMesh refusal is a "
            "DIAGNOSTIC and the topology is redesigned, never bypassed by writing polyMesh by hand." % dest)
    if foam("checkMesh", dest, os.path.join(dest, "log.checkMesh")) != 0:
        die("checkMesh failed; see %s/log.checkMesh" % dest)
    cm = open(os.path.join(dest, "log.checkMesh"), errors="replace").read()
    if "Mesh OK" not in cm:
        die("checkMesh did not report `Mesh OK`")
    m_cells = re.search(r"^\s*cells:\s+(\d+)", cm, re.M)
    m_no = re.search(r"non-orthogonality Max: ([0-9.eE+-]+)", cm)
    m_sk = re.search(r"Max skewness = ([0-9.eE+-]+)", cm)
    m_ar = re.search(r"Max aspect ratio = ([0-9.eE+-]+)", cm)
    m_vol = re.search(r"Min volume = ([0-9eE+.-]*[0-9])\. Max volume = ([0-9eE+.-]*[0-9])\.\s+"
                      r"Total volume = ([0-9eE+.-]*[0-9])\.", cm)
    if not (m_cells and m_no and m_sk and m_ar and m_vol):
        die("could not read cells / non-orthogonality / skewness / aspect ratio / volumes from log.checkMesh")
    cells = int(m_cells.group(1))
    want = EX.cells_of(nc, nr, nz)
    if cells != want:
        die("built mesh has %d cells, (nc, nr, nz) = (%d, %d, %d) registers %d" % (cells, nc, nr, nz, want))
    non_ortho, skew, aspect = float(m_no.group(1)), float(m_sk.group(1)), float(m_ar.group(1))
    vmin, vmax, vtot = (float(m_vol.group(1)), float(m_vol.group(2)), float(m_vol.group(3)))
    if non_ortho > MAX_NON_ORTHO:
        die("max non-orthogonality %g exceeds the %g deg gate (MESH_STANDARD 3.1)" % (non_ortho, MAX_NON_ORTHO))
    if skew > MAX_SKEW:
        die("max skewness %g exceeds the gate %g (MESH_STANDARD 3.2)" % (skew, MAX_SKEW))
    vratio = vmax / vmin
    if vratio > VOLUME_RATIO_BOUND:
        die("max/min cell volume ratio %g exceeds the recorded bound %g; this is not the registered "
            "butterfly family" % (vratio, VOLUME_RATIO_BOUND))
    aspect_note = "advisory" if aspect > ASPECT_ADVISORY else "under_advisory"

    # ---- 0/ : p, then C and V, then U LAST ----------------------------------
    os.makedirs(os.path.join(dest, "0"))
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "p.template"),
                            os.path.join(dest, "0", "p"), {"__P0__": "0"})
    if foam("postProcess -func writeCellCentres -time 0", dest, os.path.join(dest, "log.writeCellCentres")) != 0:
        die("postProcess writeCellCentres failed")
    if foam("postProcess -func writeCellVolumes -time 0", dest, os.path.join(dest, "log.writeCellVolumes")) != 0:
        die("postProcess writeCellVolumes failed")
    C = FIO.read_field(os.path.join(dest, "0", "C"))
    V = FIO.read_field(os.path.join(dest, "0", "V"))
    if C["kind"] != "vector" or C["internal"] is None or len(C["internal"]) != cells:
        die("0/C does not carry %d cell centres" % cells)
    if V["kind"] != "scalar" or V["internal"] is None or len(V["internal"]) != cells:
        die("0/V does not carry %d cell volumes" % cells)
    xyz, vol = C["internal"], V["internal"]
    rad = np.hypot(xyz[:, 0], xyz[:, 1])
    if float(rad.max()) >= EX.R:
        die("a cell centre sits at r = %.9f, outside the pipe radius %g" % (float(rad.max()), EX.R))
    if float(xyz[:, 2].min()) <= 0.0 or float(xyz[:, 2].max()) >= EX.LZ:
        die("cell centres are outside z in (0, %g)" % EX.LZ)
    if abs(float(vol.sum()) - vtot) > 1e-9 * vtot:
        die("0/V sums to %.12g but checkMesh reported total volume %.12g" % (float(vol.sum()), vtot))
    if float(vol.sum()) > math.pi * EX.R ** 2 * EX.LZ:
        die("the faceted mesh volume %.12g exceeds the exact pipe volume %.12g; the arc edges are wrong"
            % (float(vol.sum()), math.pi * EX.R ** 2 * EX.LZ))

    # ---- THE PIN: the level's REGISTERED same-stencil reference, recomputed --
    w_ref = float(np.sum(vol * EX.u_exact(rad, EX.T_END)) / np.sum(vol) / EX.U_REF)
    pin = None
    if pin_reference:
        reg = EX.W_REF_MESH[level]
        if abs(w_ref - reg) > EX.W_REF_TOL:
            die("SAME-STENCIL REFERENCE PIN FAILED at level %s: the built mesh gives W_ref = %.15f, the "
                "pre-registration froze %.15f (difference %.3e > %.1e). The mesh that would run is NOT the "
                "mesh gate 2's band was registered against." % (level, w_ref, reg, w_ref - reg, EX.W_REF_TOL))
        pin = dict(registered=reg, rebuilt=w_ref, difference=w_ref - reg, tolerance=EX.W_REF_TOL)

    mesh_line = dict(level=level, nc=nc, nr=nr, nz=nz, cells=cells, steps=steps, dt=EX.dt_of(steps),
                     max_non_orthogonality_deg=non_ortho, max_skewness=skew, max_aspect_ratio=aspect,
                     aspect_note=aspect_note, gate_non_ortho=MAX_NON_ORTHO, gate_skew=MAX_SKEW,
                     aspect_advisory=ASPECT_ADVISORY, min_volume=vmin, max_volume=vmax,
                     volume_ratio_readback=vratio, total_volume=float(vol.sum()),
                     exact_pipe_volume=math.pi * EX.R ** 2 * EX.LZ, max_cell_centre_radius=float(rad.max()),
                     grading_readback=grading, W_ref_mesh=w_ref, W_ref_pin=pin,
                     source="log.checkMesh + 0/C + 0/V + the WRITTEN system/blockMeshDict")
    with open(os.path.join(dest, "MESH_LINE.txt"), "w") as f:
        f.write(json.dumps(mesh_line, sort_keys=True) + "\n")

    # ---- 0/U LAST OF ALL: the age guard dates every endTime field against it.
    U0 = EX.u_vector_exact(xyz[:, 0], xyz[:, 1], 0.0)
    FIO.write_from_template(os.path.join(CASE_SRC, "0", "U.template"), os.path.join(dest, "0", "U"),
                            {"__INTERNALFIELD__": FIO.fmt_list(U0, "vector")})
    print("built level %s at %s: %d cells (nc %d, nr %d, nz %d), non-ortho %.4f deg (gate %g), skew %.4f "
          "(gate %g), aspect %.4f, volume ratio %.4f, W_ref %.15f%s; grading read back (1 1 1) x %d blocks; "
          "0/U = exact(t=0) written last"
          % (level, dest, cells, nc, nr, nz, non_ortho, MAX_NON_ORTHO, skew, MAX_SKEW, aspect, vratio, w_ref,
             "" if pin is None else " PINNED to the registration (diff %.3e)" % pin["difference"], N_BLOCKS))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
