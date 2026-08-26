#!/usr/bin/env python3
"""
T10aR2 builder: the 2LI ladder (H-3(a), second refinement arm on T10a's B1).

Writes R2_c, R2_m, R2_f -- dictionaries and 0.orig fields -- then runs the
MESH-SIDE preprocessing (blockMesh, checkMesh, viewFactorsGen; Charter 2d) per
case with wall time and peak RSS recorded in <case>/BUILD.txt.  NO SOLVER IS
RUN BY ANYTHING IN THIS FILE.

EVERY dictionary is produced by the FROZEN build_t10a.py's own writers,
imported and never copied.  Each case applies exactly ONE registered change to
the frozen T10a level it descends from (B_c, B_m, B_f):

    constant/viewFactorsDict   distTol 8 -> 80

which is the T10a-R R-q knob applied at EVERY level instead of at f only.
Everything else -- blockMeshDict, controlDict, fvSchemes, fvSolution, the
radiation dictionaries, g, thermo, turbulence and every 0.orig field -- is
required byte-identical (sha256) to the frozen level, and this builder REFUSES
(exit 2) if it is not, in either direction.

NO `assert` STATEMENT APPEARS IN THIS FILE (L-332).  Every refusal is an explicit
exit.  The one-line "verified byte-identical" sentence at the end is printed
FROM THE VALUES COMPARED (count and the parent name per case), never from a
literal (T10aR_RESULTS.md section 9 disclosed that defect in build_t10aR.py).

Exit codes: 0 built and preprocessed, 2 refusal.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
T10A = os.path.join(os.path.dirname(HERE), "T10a_runs")
sys.path.insert(0, T10A)
import build_t10a as B                                    # noqa: E402  FROZEN

REG = json.load(open(os.path.join(HERE, "T10aR2_registered.json")))
CASES = {k: v for k, v in REG["cases"].items() if k != "note"}
BX = B.BX
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
NICE = 15


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def with_dist_tol(txt, dist_tol):
    out, n = re.subn(r"(distTol\s+)8;", r"\g<1>%d;" % dist_tol, txt)
    if n != 1:
        refuse("distTol substitution matched %d times, not 1" % n)
    return out


def write_case(name, c):
    d = os.path.join(HERE, name)
    if os.path.exists(d):
        refuse("%s already exists; this builder never overwrites a case (delete it "
               "deliberately if a rebuild is intended)" % d)
    for sub in ("0.orig", "constant", "system"):
        os.makedirs(os.path.join(d, sub))

    def w(rel, txt):
        open(os.path.join(d, rel), "w").write(txt)
    patches = [(p, BX["patches"][p]["T"], BX["eps"])
               for p in ("floor", "ceiling", "x0", "x1", "y0", "y1")]
    pn = [p for p, _, _ in patches]
    w("system/blockMeshDict", B.box_block_mesh(c["N"]))
    w("system/controlDict", B.control_dict())
    w("system/fvSchemes", B.fv_schemes())
    w("system/fvSolution", B.fv_solution())
    w("constant/g", B.gravity())
    w("constant/thermophysicalProperties", B.thermo())
    w("constant/turbulenceProperties", B.turbulence())
    w("constant/radiationProperties", B.radiation_props(c["smoothing"]))
    w("constant/boundaryRadiationProperties",
      B.boundary_radiation([(p, e) for p, _, e in patches]))
    w("constant/viewFactorsDict",
      with_dist_tol(B.view_factors_dict_gen(c["GaussQuadTol"]), c["distTol"]))
    w("0.orig/T", B.field_T([(p, t) for p, t, _ in patches]))
    w("0.orig/U", B.field_U(pn))
    w("0.orig/p_rgh", B.field_p_rgh(pn))
    w("0.orig/p", B.field_p(pn))
    w("0.orig/qr", B.field_qr(pn))
    # cell count READ from the frozen mesh writer, not assumed
    m = re.search(r"hex \(0 1 2 3 4 5 6 7\) \((\d+) (\d+) (\d+)\)",
                  open(os.path.join(d, "system/blockMeshDict")).read())
    if not m:
        refuse("%s: cannot read the block divisions back from blockMeshDict" % name)
    nx, ny, nz = (int(v) for v in m.groups())
    cells = nx * ny * nz
    faces = 2 * (nx * ny) + 2 * (ny * nz) + 2 * (nx * nz)
    if cells != c["cells"] or faces != c["faces"]:
        refuse("%s: blockMeshDict gives %d cells / %d faces, registered %d / %d"
               % (name, cells, faces, c["cells"], c["faces"]))
    w("CASE.txt", "\n".join([
        "case              %s" % name,
        "rung              T10aR2 (H-3(a): the 2LI ladder, second refinement arm on T10a's B1)",
        "level             %s" % c["level"],
        "one change from   %s: constant/viewFactorsDict distTol 8 -> %d" % (c["one_change_from"], c["distTol"]),
        "solver            buoyantSimpleFoam (ESI v2606), laminar, g = (0 0 0), carrier fluid",
        "generator         viewFactorsGen (mesh-side preprocessing at build; wall time in BUILD.txt)",
        "Lx Ly Lz          %s %s %s m" % (BX["Lx"], BX["Ly"], BX["Lz"]),
        "N per m           %d   divisions (%d %d %d)" % (c["N"], nx, ny, nz),
        "cells_from_dict   %d" % cells,
        "faces_from_dict   %d" % faces,
        "GaussQuadTol      %s" % c["GaussQuadTol"],
        "distTol           %d" % c["distTol"],
        "smoothing         %s" % c["smoothing"],
    ] + ["patch             %s: T = %s K, emissivity = %s" % (p, t, e) for p, t, e in patches]) + "\n")
    return d, cells


IDENTICAL = ["system/blockMeshDict", "system/controlDict", "system/fvSchemes",
             "system/fvSolution", "constant/g", "constant/thermophysicalProperties",
             "constant/turbulenceProperties", "constant/radiationProperties",
             "constant/boundaryRadiationProperties", "0.orig/T", "0.orig/U",
             "0.orig/p", "0.orig/p_rgh", "0.orig/qr"]
CHANGED = ["constant/viewFactorsDict"]


def verify(name, c, d):
    """Refuse a case that is not exactly what was registered.  Returns the
    number of files verified identical and the parent name -- the values the
    final sentence is printed FROM."""
    parent = os.path.join(T10A, c["one_change_from"])
    if not os.path.isdir(parent):
        refuse("frozen parent %s is missing" % parent)
    n_same = 0
    for rel in IDENTICAL:
        if sha(os.path.join(d, rel)) != sha(os.path.join(parent, rel)):
            refuse("%s %s differs from %s but is registered identical" % (name, rel, c["one_change_from"]))
        n_same += 1
    for rel in CHANGED:
        if sha(os.path.join(d, rel)) == sha(os.path.join(parent, rel)):
            refuse("%s %s is identical to %s but is registered CHANGED" % (name, rel, c["one_change_from"]))
    dtxt = open(os.path.join(d, "constant/viewFactorsDict")).read()
    ptxt = open(os.path.join(parent, "constant/viewFactorsDict")).read()
    diff = [(a, b) for a, b in zip(dtxt.splitlines(), ptxt.splitlines()) if a != b]
    if len(diff) != 1 or "distTol" not in diff[0][0]:
        refuse("%s viewFactorsDict differs from the parent on %d lines, not the one distTol line: %r"
               % (name, len(diff), diff))
    return n_same, c["one_change_from"], diff[0]


def preprocess(name, d):
    """blockMesh, checkMesh, viewFactorsGen at nice 15; rc, wall, peak RSS to BUILD.txt.
    Refuses if constant/F already exists (never regenerates over evidence)."""
    if os.path.isfile(os.path.join(d, "constant", "F")):
        refuse("%s already holds constant/F; not regenerating over it" % name)
    env = "set +u; . %s >/dev/null 2>&1; set -u; cd %s && " % (FOAM_BASHRC, d)

    def run(cmd, log, timed=False):
        full = env + ("/usr/bin/time -v " if timed else "") + "nice -n %d %s > %s 2> %s" % (
            NICE, cmd, log, (log + ".time" if timed else "/dev/null"))
        t0 = time.time()
        rc = subprocess.run(["bash", "-c", full]).returncode
        return rc, time.time() - t0
    bm, tbm = run("blockMesh", "log.blockMesh")
    cm, tcm = run("checkMesh", "log.checkMesh.build")
    vf, tvf = run("viewFactorsGen", "log.viewFactorsGen", timed=True)
    rss = ""
    tl = os.path.join(d, "log.viewFactorsGen.time")
    if os.path.isfile(tl):
        m = re.search(r"Maximum resident set size \(kbytes\): (\d+)", open(tl).read())
        rss = m.group(1) if m else ""
    # the generator may write 0/viewFactorField; the run tree must hold NO 0/
    # (the launcher arms 0/ from 0.orig and the age guard dates the run by 0/T)
    z = os.path.join(d, "0")
    if os.path.isdir(z):
        vff = os.path.join(z, "viewFactorField")
        if os.path.isfile(vff):
            shutil.move(vff, os.path.join(d, "viewFactorField.build"))
        if os.listdir(z):
            refuse("%s: the generator left unexpected files in 0/: %r" % (name, os.listdir(z)))
        os.rmdir(z)
    fpath = os.path.join(d, "constant", "F")
    gpath = os.path.join(d, "constant", "globalFaceFaces")
    fsha = sha(fpath) if os.path.isfile(fpath) else "ABSENT"
    lines = ["case            %s" % name,
             "date            %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "generator       viewFactorsGen  (nice %d)" % NICE,
             "blockMesh_rc    %d   wall %.2f s" % (bm, tbm),
             "checkMesh_rc    %d   wall %.2f s" % (cm, tcm),
             "viewFactorsGen_rc  %d   wall %.2f s   maxRSS_kB %s" % (vf, tvf, rss),
             "F_size          %s bytes" % (os.path.getsize(fpath) if os.path.isfile(fpath) else "ABSENT"),
             "gFF_size        %s bytes" % (os.path.getsize(gpath) if os.path.isfile(gpath) else "ABSENT"),
             "F_sha256        %s" % fsha,
             "loadavg_at_gen  %s" % open("/proc/loadavg").read().split()[0]]
    open(os.path.join(d, "BUILD.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join("    " + l for l in lines))
    if bm != 0 or cm != 0 or vf != 0:
        refuse("%s preprocessing failed: blockMesh %d checkMesh %d viewFactorsGen %d" % (name, bm, cm, vf))
    return fsha


def main(argv):
    only = [a for a in argv[1:] if not a.startswith("--")]
    do_pre = "--no-preprocess" not in argv
    pre_only = "--preprocess-only" in argv
    print("T10aR2 builder.  frozen build_t10a imported from %s" % T10A)
    built = []
    for name, c in CASES.items():
        if only and name not in only:
            continue
        if pre_only:
            d = os.path.join(HERE, name)
            if not os.path.isdir(d):
                refuse("%s does not exist; --preprocess-only needs a written case" % d)
            cells = c["cells"]
        else:
            d, cells = write_case(name, c)
        n_same, parent, diff = verify(name, c, d)
        print("  %s N=%3d cells=%6d faces=%5d  parent %s: %d files byte-identical, "
              "1 file changed on 1 line: %r -> %r"
              % (name, c["N"], cells, c["faces"], parent, n_same, diff[1].strip(), diff[0].strip()))
        built.append((name, d))
    if do_pre:
        for name, d in built:
            print("  preprocessing %s" % name)
            preprocess(name, d)
    for name, d in built:
        for t in os.listdir(d):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t):
                refuse("%s holds a time directory %s after build" % (name, t))
    print("built %d case(s); no time directory in any of them; no solver was run." % len(built))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
