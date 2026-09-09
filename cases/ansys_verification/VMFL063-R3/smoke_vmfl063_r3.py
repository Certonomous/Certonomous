#!/usr/bin/env python3
# =============================================================================
# VMFL063-R3 ANSWER-BLIND LR-PIPELINE SMOKE  (PREREGISTRATION sec.7; deliverable 3)
#
# WHAT IT IS. A CHEAP, SCRATCH-ONLY plumbing check that the de-confined case builds,
# the new far-field BC (pressureInletOutletVelocity / p fixedValue 0) runs, and the
# LR reader pipeline (wallShearStress -> last-crossing -> cross-instrument u_x) parses
# real solver bytes end to end on the COARSEST, NON-GRADED mesh (D0 L1, no padding).
#
# WHY IT IS NOT A CONTAMINATING PRE-FREEZE RUN (ANSYS_VERIFICATION_CHARTER sec.20.3).
#   * It runs on the COARSEST mesh only (D0 L1). The graded answer is the r=2 gate
#     triple at D* on the FIXED R2-L3 grid; a coarse, iteration-bounded solve cannot
#     reveal a plateau, an observed order, a GCI, or the graded LR.
#   * It is declared here as a pipeline check, and the ONE quantity it could reveal --
#     a coarse LR -- is printed to STDERR ONLY, behind a loud banner, NEVER persisted,
#     NEVER compared to anything. The gate quantity it protects is untouched.
#   * IT NEVER READS THE REFERENCE. REF_LR2T (4.0) is not imported, mentioned or
#     compared. The pipeline VERDICT on stdout is a BOOLEAN: did the reader return a
#     finite in-window crossing on which the two instruments agree? -- nothing more.
#   * It runs entirely under a scratch directory, NEVER under verification/runs/, so it
#     creates no graded run root, no `0/` and no time dir there, and does not consume
#     the age guard. The scratch tree is deleted on exit unless --keep is given.
#
# IT LAUNCHES NO GRADED SOLVE. Running it is a separate, answer-blind act; nothing here
# authorises a graded run (rule 9). Usage:
#     smoke_vmfl063_r3.py [--iters N] [--scratch DIR] [--keep]
# =============================================================================
import os, re, sys, glob, shutil, tempfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
GEN  = os.path.join(HERE, "gen_domain_mesh.py")
CASE = os.path.join(HERE, "case")
OPENFOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

SMOKE_DOMAIN, SMOKE_LEVEL, SMOKE_ZERO = "D0", "L1", "0"   # coarsest, de-confined top


def _load_reader():
    """Import the FROZEN comparator's reader functions -- the SAME code the gate uses,
    so the smoke exercises the real pipeline. Only readers are used; completion() (which
    requires full convergence) is deliberately NOT called -- this is a plumbing check."""
    spec = importlib.util.spec_from_file_location(
        "grade_vmfl063_r3", os.path.join(HERE, "grade_vmfl063_r3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sh(cmd, cwd, log):
    with open(log, "w") as fh:
        return subprocess.run(["bash", "-lc", cmd], cwd=cwd, stdout=fh, stderr=fh).returncode


def main(argv):
    iters = 200
    scratch = None
    keep = "--keep" in argv
    for i, a in enumerate(argv):
        if a == "--iters" and i + 1 < len(argv):
            iters = int(argv[i + 1])
        if a == "--scratch" and i + 1 < len(argv):
            scratch = argv[i + 1]

    G = _load_reader()
    work = scratch or tempfile.mkdtemp(prefix="vmfl063_r3_smoke_")
    case = os.path.join(work, "case")
    ok = True
    try:
        os.makedirs(os.path.join(case, "system"), exist_ok=True)
        os.makedirs(os.path.join(case, "0"), exist_ok=True)
        shutil.copytree(os.path.join(CASE, "constant"), os.path.join(case, "constant"))
        for f in ("fvSchemes", "fvSolution"):
            shutil.copy(os.path.join(CASE, "system", f), os.path.join(case, "system", f))
        for f in ("U", "p"):
            shutil.copy(os.path.join(CASE, SMOKE_ZERO, f), os.path.join(case, "0", f))

        # controlDict: bounded iterations so the smoke is cheap and cannot converge to
        # the graded answer; write fields at the end so the reader has bytes to parse.
        tmpl = open(os.path.join(CASE, "system", "controlDict.template")).read()
        cd = tmpl.replace("__ENDTIME__", str(iters))
        cd = re.sub(r"^writeInterval\s+\d+;", "writeInterval %d;" % iters, cd, flags=re.M)
        open(os.path.join(case, "system", "controlDict"), "w").write(cd)

        # mesh from the FROZEN generator (coarsest, no padding, de-confined top)
        bmd = subprocess.run(["python3", GEN, SMOKE_DOMAIN, SMOKE_LEVEL],
                             capture_output=True, text=True)
        if bmd.returncode != 0:
            print("PIPELINE SMOKE: FAIL -- gen_domain_mesh %s %s rc=%d"
                  % (SMOKE_DOMAIN, SMOKE_LEVEL, bmd.returncode)); return 1
        open(os.path.join(case, "system", "blockMeshDict"), "w").write(bmd.stdout)

        pre = "source %s >/dev/null 2>&1; " % OPENFOAM_BASHRC
        if _sh(pre + "blockMesh", case, os.path.join(case, "log.blockMesh")) != 0:
            print("PIPELINE SMOKE: FAIL -- blockMesh (see log.blockMesh)"); return 1
        _sh(pre + "checkMesh", case, os.path.join(case, "log.checkMesh"))
        chk = open(os.path.join(case, "log.checkMesh"), errors="replace").read()
        mesh_ok = "Mesh OK" in chk
        cells = (re.search(r"cells:\s+(\d+)", chk) or [None, "?"])[1]

        if _sh(pre + "timeout 900s simpleFoam", case,
               os.path.join(case, "log.simpleFoam")) not in (0, 124):
            print("PIPELINE SMOKE: FAIL -- simpleFoam did not run (see log.simpleFoam)")
            return 1
        _sh(pre + "postProcess -func writeCellCentres -latestTime", case,
            os.path.join(case, "log.writeCellCentres"))

        # latest numeric time dir (key=float; NEVER lexicographic)
        tdirs = [(float(os.path.basename(d)), os.path.basename(d))
                 for d in glob.glob(os.path.join(case, "*"))
                 if os.path.isdir(d) and re.match(r"^[0-9]+(\.[0-9]+)?$", os.path.basename(d))
                 and os.path.basename(d) != "0"]
        if not tdirs:
            print("PIPELINE SMOKE: FAIL -- no time directory written"); return 1
        t = max(tdirs)[1]

        # --- THE PIPELINE: run the SAME reader the gate uses -----------------------
        x, tau, orec = G.wallshear_profile(case, t)
        lr = G.last_sign_change_in_window(x, tau)
        xu, uu = G.nearwall_u_profile(case, t)
        lr_u = G.last_sign_change_in_window(xu, uu)
        crossing = lr is not None
        cross_ok = (crossing and lr_u is not None
                    and abs(lr - lr_u) <= G.CROSS_TOL_CELLS * G.local_dx_at(x, lr))

        # coarse LR to STDERR ONLY, behind a banner; NEVER to stdout, NEVER persisted,
        # NEVER compared to the reference.
        if crossing:
            sys.stderr.write(
                "\n  [PIPELINE-ONLY BANNER] coarse D0/L1 un-converged LR = %.6g m "
                "(LR/2t = %.4g). NOT A GRADED VALUE; coarse non-graded mesh; the "
                "reference 4.0 is never read. Do not quote this.\n\n" % (lr, lr / G.TWO_T))

        print("PIPELINE SMOKE (D0/L1, de-confined top; scratch %s)" % work)
        print("  buildability : blockMesh+checkMesh Mesh OK = %s, cells = %s" % (mesh_ok, cells))
        print("  reader parse : wallShearStress + Cx/Cy + U parsed = %s"
              % (x is not None and len(x) > 0))
        print("  in-window crossing found (wall shear) = %s" % crossing)
        print("  cross-instrument (wall shear vs near-wall u_x) agree = %s" % cross_ok)
        verdict = mesh_ok and crossing and cross_ok
        print("  PIPELINE VERDICT: %s" % ("OK -- reader plumbing confirmed end to end"
                                          if verdict else "NOT OK -- see logs"))
        ok = verdict
        return 0 if verdict else 1
    finally:
        if not keep:
            shutil.rmtree(work, ignore_errors=True)
        elif not ok:
            sys.stderr.write("  (scratch kept for inspection: %s)\n" % work)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
