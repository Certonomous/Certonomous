#!/usr/bin/env python3
r"""Curriculum D19M -- the instrument's own controls.

WHAT THIS SUITE CAN AND CANNOT DO, STATED FIRST.  `d19m_xf.py` needs `mphys`,
`dafoam`, `pygeo` and `idwarp`, none importable outside the containers.  So this
suite drives the PURE functions, the WRITERS, the producer's PHYSICS assertion,
and the AST.  **IT DOES NOT PROVE THE MODEL BUILDS IN-CONTAINER**, and for this
item that residual is larger than it was for D19O: the producer is NEW, the
model has three `DAFoamBuilder`s where D19O had one, and mode `O` drives a
weighted objective no compressible item has ever assembled.
"""
import ast
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d19m_xf as XF                                              # noqa: E402

FAILED = []


def unit(name, want, got, note=""):
    good = (got == want)
    if not good:
        FAILED.append(name)
    print("  %-18s expect=%-28s got=%-28s %s%s"
          % (name, str(want)[:28], str(got)[:28],
             "OK" if good else "**FAILED**", (" " + note) if note else ""))
    return good


def _pair(dJ, dCLs, step, J0=0.0163267546, cl0=(0.42, 0.50, 0.58)):
    return (J0 + dJ * step, J0 - dJ * step,
            [c + d * step for c, d in zip(cl0, dCLs)],
            [c - d * step for c, d in zip(cl0, dCLs)])


def main():
    print("D19M INSTRUMENT SELFTEST")
    print("  d19m_xf.py : %s" % XF.md5_of(os.path.join(HERE, "d19m_xf.py")))
    print()

    # ================= A. THE PRODUCER =======================================
    print("A. THE PRODUCER -- NEW, AND THE PHYSICS IS THE PART THAT IS INHERITED")
    prod = os.path.join(HERE, XF.PRODUCER)
    unit("A1-exists", True, os.path.isfile(prod))
    src = open(prod).read()
    unit("A2-markers-once", (1, 1),
         (src.count(XF.PHYSICS_BEGIN), src.count(XF.PHYSICS_END)))
    blk = src.split(XF.PHYSICS_BEGIN)[1].split(XF.PHYSICS_END)[0].strip()
    unit("A3-physics-md5", XF.PHYSICS_MD5, hashlib.md5(blk.encode()).hexdigest(),
         "(byte-identical to D19O's physics block)")
    # THE CLAIM IS CHECKED AGAINST D19O's ACTUAL FILE, not against a remembered hash.
    d19o = os.path.join(HERE, "..", "curriculum_D19O", "d19o_runScript.py")
    if os.path.isfile(d19o):
        o = open(d19o).read()
        i, j = o.index("U0 = 100.0"), o.index("# Mesh deformation setup")
        ob = "".join(l for l in o[i:j].splitlines(keepends=True)
                     if not l.startswith("aoa0 = ")).strip()
        unit("A4-vs-D19O-on-disk", True, blk == ob,
             "(compared against D19O's REAL file, not a remembered hash)")
    else:
        unit("A4-vs-D19O-on-disk", "SKIPPED", "SKIPPED", "(D19O's producer absent)")
    unit("A5-compressible", True, '"solverName": "DARhoSimpleFoam"' in blk)
    unit("A6-T0-present", True, '"T0"' in blk, "(the compressible energy BC)")
    unit("A7-no-header-claim", False, "HEADER_MD5_SHARED_WITH_D15" in open(
        os.path.join(HERE, "d19m_xf.py")).read(),
        "(this item makes NO D15 header-reproduction claim, and must not)")
    unit("A8-producer-parses", True, bool(ast.parse(src)))
    # the producer must NOT declare patchV as a design variable
    # AST, NOT A SUBSTRING.  The first version of this leg grepped for
    # `add_design_var("patchV"` and FAILED -- on the producer's own COMMENT
    # saying that call is GONE.  A substring check cannot tell code from prose
    # about code, and the prose here is deliberately explicit.
    dv_names = []
    for n in ast.walk(ast.parse(src)):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "add_design_var" and n.args
                and isinstance(n.args[0], ast.Constant)):
            dv_names.append(n.args[0].value)
    unit("A9-design-vars", ["shape"], dv_names,
         "(read from the AST: `shape` ONLY. alpha is the OPERATING POINT and "
         "cannot also be a DV. A substring check failed here on the COMMENT.)")
    unit("A10-patchV-not-a-DV", False, "patchV" in dv_names)
    unit("A11-obj-is-J", True, 'add_objective("obj.J"' in src)
    unit("A12-one-geometry", 1, src.count('add_subsystem("geometry"'),
         "(ONE shared OM_DVGEOCOMP -- the D6 defect was geometry_<pt> PER SCENARIO)")
    unit("A13-run-dirs", True, "run_directory=RUN_DIRS[sc]" in src,
         "(one case per point -- the SO-3aR collision needs two writers in one dir)")

    # ================= B. INSTRUMENT/PRODUCER AGREEMENT ======================
    print()
    print("B. THE INSTRUMENT AND THE PRODUCER MUST AGREE ON THE OPERATING POINTS")
    import re
    p_alphas = [float(x) for x in
                re.search(r"ALPHAS = \[([^\]]*)\]", src).group(1).split(",")]
    unit("B1-alphas", XF.ALPHAS, p_alphas)
    unit("B2-three-points", 3, len(XF.ALPHAS))
    unit("B3-weights-sum-1", True, abs(sum(XF.WEIGHTS) - 1.0) < 1e-15)
    unit("B4-equal-weights", True, len(set(XF.WEIGHTS)) == 1,
         "(EQUAL weights are a CHOICE, registered as one)")
    unit("B5-centre-is-D19O's", 4.787333582, XF.ALPHAS[1],
         "(D19O's MEASURED trimmed angle at CL=0.5, not the incompressible tutorial's)")
    unit("B6-bracket", (2.0, 2.0),
         (round(XF.ALPHAS[1] - XF.ALPHAS[0], 9), round(XF.ALPHAS[2] - XF.ALPHAS[1], 9)))
    unit("B7-inside-aoa-bound", True,
         all(0.0 <= a <= 10.0 for a in XF.ALPHAS),
         "(the tutorial's own [0, 10] bound)")
    unit("B8-runtime-check-exists", True,
         "D19M_XF REFUSE %s disagree" in open(os.path.join(HERE, "d19m_xf.py")).read(),
         "(a scenario added in one file and not the other REFUSES at runtime)")

    # ================= C. shape[7] ==========================================
    print()
    print("C. shape[7] -- THE REGISTRATION IS CARRIED FORWARD, NOT RE-DECIDED")
    unit("C1-excluded", True, XF.is_excluded("shape", 7))
    unit("C2-only-one", 1, len(XF.EXCLUDED_FROM_AGGREGATE))
    unit("C3-four-components", 4, len(XF.COMPONENTS))
    unit("C4-no-patchV-component", True,
         all(dv == "shape" for dv, _ in XF.COMPONENTS),
         "(patchV is not a DV here, so there is no patchV derivative to grade)")
    unit("C5-reason-cites-D19O", True, "D19O" in XF.EXCLUSION_REASON,
         "(the reason names D19O's finding AND why it does not license grading here)")
    unit("C6-reason-says-not-licence", True,
         "NOT licence to grade it here" in XF.EXCLUSION_REASON)

    # ================= D. THE PLATEAU RULE ==================================
    print()
    print("D. THE DECADE PLATEAU RULE -- G19R-1b's, UNCHANGED")
    unit("D1-tol", 10.0, XF.PLATEAU_TOL_PCT)
    unit("D2-decade", [1.0e-2, 1.0e-3, 1.0e-4], XF.FD_STEPS_ENDPOINT["shape"])
    unit("D3-sstar-centre", XF.S_STAR["shape"], XF.FD_STEPS_ENDPOINT["shape"][1])
    # a flat component closes; a fine-side-broken one does not
    flat = {s: _pair(1.0e-2, [1.0, 1.1, 1.2], s) for s in XF.FD_STEPS_ENDPOINT["shape"]}
    r = XF.build_fd_row("shape", 0, flat)
    unit("D4-green", True, r["plateau_J"]["two_sided"])
    broken = dict(flat)
    broken[1.0e-4] = _pair(1.0e-2 * 1.25, [1.0, 1.1, 1.2], 1.0e-4)
    r2 = XF.build_fd_row("shape", 0, broken)
    unit("D5-red", False, r2["plateau_J"]["two_sided"],
         "(a 25 %% fine-side excursion does NOT close -- the reader is not stuck True)")
    unit("D6-per-scenario-CL", 3, len(r["plateau_CL"]),
         "(the plateau is read PER SCENARIO on CL, not once for the vector)")

    # ================= E. THE WEIGHTED OBJECTIVE ============================
    print()
    print("E. J = SUM_i w_i CD_i, AND THE ASSEMBLY IS CHECKABLE")
    unit("E1-weighted_J", 0.02, round(XF.weighted_J([0.01, 0.02, 0.03]), 12),
         "(equal weights on 0.01/0.02/0.03)")
    unit("E2-mp-rtol", 1.0e-10, XF.MP_STRUCT_RTOL)
    # G-MP-STRUCT's arithmetic, driven here on the instrument's own weights
    dCD = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    recon = [sum(XF.WEIGHTS[i] * dCD[i][k] for i in range(3)) for k in range(2)]
    unit("E3-reconstruction", [3.0, 4.0], [round(v, 12) for v in recon])

    # ================= F. THE PLANT AND THE TRIVIAL BASELINE ================
    print()
    print("F. THE RELATIVE PLANT AND THE CHARTER-4 BASELINE")
    c = XF.build_ctrl_row(0.0163267546, [0.42, 0.50, 0.58])
    unit("F1-zero-is-zero", 0.0, float(c["fd"][repr(XF.CTRL_STEP)]["dJ"]))
    unit("F2-crosses", True, c["planted"]["crosses_band"])
    unit("F3-red-leg", False, c["planted_shrunk"]["crosses_band"])
    unit("F4-formula", 25.0, float(c["planted"]["moved_pp"]),
         "(K x band = 5.0 x 5.0 = 25.0 pp BY CONSTRUCTION, at any scale)")
    small = XF.build_ctrl_row(1.63e-05, [0.4, 0.4, 0.4])
    unit("F5-scale-free", 25.0, float(small["planted"]["moved_pp"]))
    unit("F6-tb-step", 1.0e-8, XF.TB_STEP)
    unit("F7-tb-flagged", True,
         XF.build_fd_step(XF.TB_STEP, 1.0, 1.0, [1.0] * 3, [1.0] * 3)["is_trivial_baseline"])
    unit("F8-nan-not-ok", False,
         XF.build_fd_step(1e-3, float("nan"), 0.0, [1.0] * 3, [0.0] * 3)["ok"])

    # ================= G. THE AST ===========================================
    print()
    print("G. THE AST -- the structural claims the pre-registration makes")
    xsrc = open(os.path.join(HERE, "d19m_xf.py")).read()
    tree = ast.parse(xsrc)
    unit("G1-no-asserts", 0,
         sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert)),
         "(python3 -O strips asserts; L-332)")
    planted = ast.parse(xsrc + "\ndef _p():\n    assert True\n")
    unit("G1-control", 1,
         sum(1 for n in ast.walk(planted) if isinstance(n, ast.Assert)),
         "(a PLANTED assert IS seen -- the counter is not blind)")
    unit("G2-mpi-abort", True, "MPI.COMM_WORLD.Abort(2)" in xsrc)
    unit("G3-np-required", 1, XF.NP_REQUIRED)
    unit("G4-no-row-flag", False, '"-row"' in xsrc)
    unit("G5-two-rows", {"PATCHED", "SHIPPED"}, set(XF.ROW_BY_SO_MD5.values()))
    unit("G6-xopt-required", True, "mode %s needs %s from arm O" in xsrc)
    unit("G7-max-majors", 40, XF.MAX_MAJORS)
    unit("G8-expected-majors", 12, XF.EXPECTED_MAJOR_ROWS)
    unit("G9-one-row-writer", 1, xsrc.count("def row_from_fd("),
         "(ONE writer for a component row -- the D19O leg that caught two)")

    print()
    if FAILED:
        print("D19M INSTRUMENT SELFTEST: FAILED -- %d leg(s): %s" % (len(FAILED), FAILED))
        return 1
    print("D19M INSTRUMENT SELFTEST: OK -- every leg driven, every control fired")
    print("RESIDUAL, NAMED AND LARGER THAN D19O's: the producer is NEW, carries THREE")
    print("DAFoamBuilders, and mode `O` drives a weighted objective no compressible item")
    print("has ever assembled. None of that is proved here. PREREGISTRATION.md section 15.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
