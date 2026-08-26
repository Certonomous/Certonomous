#!/usr/bin/env python3
"""Build the three registered T4b impinging-jet cases (wall-resolved successor of T4).

T4b re-registers T4 (ERCOFTAC case025 ij2lr, H/D = 2, Re_D = 23 000, axisymmetric
wedge, steady buoyantBoussinesqSimpleFoam with beta = 0, kOmegaSST) with TWO mesh
changes and ONE dictionary change against the frozen build_t4.py, each stated here
and in T4b_PREREGISTRATION.md, and NOTHING else changed:

  1. FIRST-CELL HEIGHT HALVED AT EVERY LEVEL: 1.2e-5 / 6.0e-6 / 3.0e-6 m (T4 had
     2.4e-5 / 1.2e-5 / 6.0e-6).  T4 measured plate y+_max = 1.2480 on its coarse
     level at first-cell centre y_p = 1.2e-5 m, i.e. u_tau,max = 1.248 * 1.5e-5 /
     1.2e-5 = 1.560 m/s (m: 1.617, f: 1.692 m/s -- rising ~4-5 % per halving).
     At y_p = 6.0e-6 m the coarse plate y+_max is 0.624 at T4's coarse u_tau and
     0.71 at an extrapolated 1.78 m/s; control C1 (y+_max < 1) fires only above
     u_tau,max = 2.5 m/s.  The family ratio r = 2 is kept exactly.

  2. THE RADIAL GRADING OF THE JET-CORE AND PIPE BLOCKS IS INVERTED.  The frozen
     build_t4.py comments its jet-core/pipe radial grading "fine at pipe wall" but
     emits simpleGrading(g_pipew ...) with g_pipew = last/first > 1 along the block's
     x1 direction, which runs AXIS -> r0: the FINE cell sat on the axis and the
     COARSEST cell (71x the first, 1.7e-3 m at level c) sat on the pipe wall.  That
     is why T4 measured pipe-wall y+ = 30.1 / 20.5 / 13.0 under nutLowReWallFunction.
     T4b writes 1/g so the first cell sits on the pipe wall / nozzle lip, at the
     same registered first-cell height as the plate; the wall-jet block already
     had its fine cell at r0 on the other side, so the lip now sees 1.2e-5 m on the
     pipe side against 2.4e-5 m on the wall-jet side instead of 1.7e-3 m against
     2.4e-5 m.  With the pipe wall resolved, control C1b (pipe-wall y+_max < 1)
     can be registered as a condition that can pass, not one that fires by
     construction.  To keep the cell-to-cell growth in the jet core below 1.15
     (it would be 1.249 at N/2 cells), the jet-core/pipe radial division is
     3N/4 instead of N/2.  Cells are therefore 2.625 N^2: 6 048 / 24 192 / 96 768.

  3. residualControl REMOVED from fvSolution (L-141): the run length is endTime by
     registration, so the strict completion rule's "last time == endTime" clause
     is decidable, and convergence is judged by the frozen comparator from the
     residual history and the written checkpoints, never by the solver.

Everything else -- every boundary condition per field per patch (T4 AMENDMENT 2
table), transportProperties, turbulenceProperties, g, schemes, linear solvers,
relaxation factors, endTime 20000 / 30000 / 40000, writeInterval endTime/10 with
purgeWrite 2 -- is produced by the FROZEN build_t4.py's own writers, imported here
and never copied.  fields() and constant_files() are called unchanged; header()
and grading_ratio() are reused.

NO `assert` STATEMENT IN THIS FILE (L-332).  Refusals are explicit exits.

Usage:  build_t4b.py [--root <dir>] [--level c|m|f] ...
"""
import argparse
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T4 = os.path.join(os.path.dirname(HERE), "T4_runs")
sys.path.insert(0, T4)
import build_t4 as B                                      # noqa: E402  FROZEN

D, H_OVER_D, R_OVER_D, LPIPE_OVER_D, WEDGE_DEG = B.D, B.H_OVER_D, B.R_OVER_D, B.LPIPE_OVER_D, B.WEDGE_DEG
NU, U_BULK, RE = B.NU, B.U_BULK, B.RE

LEVELS = {"c": dict(N=48,  endTime=20000, first_cell=1.2e-5),
          "m": dict(N=96,  endTime=30000, first_cell=6.0e-6),
          "f": dict(N=192, endTime=40000, first_cell=3.0e-6)}
CASE_PREFIX = "T4b_IJ_"


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def block_mesh_dict(N, first_cell):
    """Wedge blockMeshDict.  Same topology as the frozen build_t4.block_mesh_dict
    (collapsed axis edge, three blocks); the jet-core/pipe radial grading is
    INVERTED so the fine cell is at r0, and the radial division there is 3N/4."""
    h = H_OVER_D * D
    r0 = 0.5 * D
    rout = R_OVER_D * D
    lp = LPIPE_OVER_D * D
    t = math.tan(math.radians(WEDGE_DEG))

    nrj = (3 * N) // 4    # radial cells, jet core and pipe (T4: N // 2)
    nrw = (3 * N) // 2    # radial cells, wall-jet block (unchanged)
    nyj = N               # axial cells, impingement height (unchanged)
    nyp = max(2, N // 2)  # axial cells, pipe length (unchanged)

    g_plate = B.grading_ratio(h, nyj, first_cell)                 # y: fine at plate
    g_pipew = 1.0 / B.grading_ratio(r0, nrj, first_cell)          # r: fine at r0 (INVERTED)
    g_out = B.grading_ratio(rout - r0, nrw, first_cell * 2.0)     # r: fine at r0
    g_pipey = 8.0

    pts, idx = [], {}

    def v(r, y):
        key = (round(r, 12), round(y, 12))
        if key in idx:
            return idx[key]
        z = r * t
        if r == 0.0:
            i = len(pts)
            pts.append((0.0, y, 0.0))
            idx[key] = (i, i)
        else:
            i = len(pts)
            pts.append((r, y, -z))
            pts.append((r, y, +z))
            idx[key] = (i, i + 1)
        return idx[key]

    A0 = v(0.0, 0.0);      P0 = v(r0, 0.0);      Q0 = v(rout, 0.0)
    A1 = v(0.0, h);        P1 = v(r0, h);        Q1 = v(rout, h)
    A2 = v(0.0, h + lp);   P2 = v(r0, h + lp)

    def hexblk(c00, c10, c11, c01, nx, ny, gx, gy):
        b = (c00[0], c10[0], c11[0], c01[0])
        f = (c00[1], c10[1], c11[1], c01[1])
        return ("    hex (%d %d %d %d %d %d %d %d) (%d %d 1) "
                "simpleGrading (%.10g %.10g 1)\n" % (b + f + (nx, ny, gx, gy)))

    blocks = (hexblk(A0, P0, P1, A1, nrj, nyj, g_pipew, g_plate) +
              hexblk(P0, Q0, Q1, P1, nrw, nyj, g_out, g_plate) +
              hexblk(A1, P1, P2, A2, nrj, nyp, g_pipew, g_pipey))
    vt = "".join("    (%.10g %.10g %.10g)\n" % q for q in pts)

    def face(*cols):
        return "(" + " ".join(str(c[0][c[1]]) for c in cols) + ")"

    def wedge_face(c0, c1, c2, c3, side):
        return "(" + " ".join(str(c[side]) for c in (c0, c1, c2, c3)) + ")"

    bnd = """
boundary
(
    plate
    {{
        type            wall;
        faces           ( {plate1} {plate2} );
    }}
    pipeWall
    {{
        type            wall;
        faces           ( {pipew} );
    }}
    inlet
    {{
        type            mappedPatch;
        sampleMode      nearestCell;
        sampleRegion    region0;
        samplePatch     none;
        offsetMode      uniform;
        offset          (0 {roff:.10g} 0);
        faces           ( {inlet} );
    }}
    entrainment
    {{
        type            patch;
        faces           ( {entr} );
    }}
    farfield
    {{
        type            patch;
        faces           ( {farf} );
    }}
    front
    {{
        type            wedge;
        faces           ( {f1} {f2} {f3} );
    }}
    back
    {{
        type            wedge;
        faces           ( {b1} {b2} {b3} );
    }}
);
""".format(
        plate1=face((A0, 0), (P0, 0), (P0, 1), (A0, 1)),
        plate2=face((P0, 0), (Q0, 0), (Q0, 1), (P0, 1)),
        pipew=face((P1, 0), (P2, 0), (P2, 1), (P1, 1)),
        inlet=face((A2, 0), (P2, 0), (P2, 1), (A2, 1)),
        entr=face((P1, 0), (Q1, 0), (Q1, 1), (P1, 1)),
        farf=face((Q0, 0), (Q1, 0), (Q1, 1), (Q0, 1)),
        roff=-0.5 * lp,
        f1=wedge_face(A0, P0, P1, A1, 1),
        f2=wedge_face(P0, Q0, Q1, P1, 1),
        f3=wedge_face(A1, P1, P2, A2, 1),
        b1=wedge_face(A0, A1, P1, P0, 0),
        b2=wedge_face(P0, P1, Q1, Q0, 0),
        b3=wedge_face(A1, A2, P2, P1, 0))
    q_pipe = (1.0 / g_pipew) ** (1.0 / (nrj - 1))
    return ("%s\nscale   1;\n\nvertices\n(\n%s);\n\nblocks\n(\n%s);\n\n"
            "edges ();\n%s\nmergePatchPairs ();\n"
            % (B.header("dictionary", "blockMeshDict", "system"), vt, blocks, bnd),
            dict(g_plate=g_plate, g_pipew=g_pipew, g_out=g_out, g_pipey=g_pipey,
                 q_pipe=q_pipe, nrj=nrj, nrw=nrw, nyj=nyj, nyp=nyp,
                 cells=nrj * nyj + nrw * nyj + nrj * nyp))


def system_files(endTime):
    """The frozen build_t4.system_files() output with ONE registered change:
    the residualControl block is removed (L-141).  Refuses unless exactly one
    residualControl line was present and removed."""
    files = B.system_files(endTime)
    sol, n = re.subn(r"^\s*residualControl\s*\{[^}]*\}\s*\n", "", files["fvSolution"], flags=re.M)
    if n != 1:
        refuse("fvSolution: expected exactly one residualControl block to remove, found %d" % n)
    if "residualControl" in sol:
        refuse("fvSolution still mentions residualControl after the registered removal")
    files["fvSolution"] = sol
    return files


def build(root, level):
    spec = LEVELS[level]
    case = os.path.join(root, CASE_PREFIX + level)
    if os.path.exists(case):
        refuse("%s already exists; this builder never overwrites a case" % case)
    for sub in ("system", "constant", "0.orig"):
        os.makedirs(os.path.join(case, sub))
    bmd, info = block_mesh_dict(spec["N"], spec["first_cell"])
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(bmd)
    for n, t in system_files(spec["endTime"]).items():
        open(os.path.join(case, "system", n), "w").write(t)
    for n, t in B.constant_files().items():
        open(os.path.join(case, "constant", n), "w").write(t)
    for n, t in B.fields(level).items():
        open(os.path.join(case, "0.orig", n), "w").write(t)
    open(os.path.join(case, "CASE.txt"), "w").write("\n".join([
        "case              %s" % (CASE_PREFIX + level),
        "rung              T4b (wall-resolved successor of T4; ERCOFTAC case025 ij2lr, H/D 2, Re 23000)",
        "level             %s   N = %d" % (level, spec["N"]),
        "solver            buoyantBoussinesqSimpleFoam (ESI v2606), kOmegaSST, beta 0, wedge %.1f deg" % WEDGE_DEG,
        "first_cell        %.3e m (plate AND pipe wall / nozzle lip)" % spec["first_cell"],
        "divisions         jet-core/pipe radial %d (3N/4), wall-jet radial %d, axial %d, pipe axial %d"
        % (info["nrj"], info["nrw"], info["nyj"], info["nyp"]),
        "cells             %d  (2.625 N^2)" % info["cells"],
        "grading           plate %.6g  jet-core radial %.6g (INVERTED: fine at r0, cell growth %.4f)  wall-jet %.6g  pipe axial %.6g"
        % (info["g_plate"], info["g_pipew"], info["q_pipe"], info["g_out"], info["g_pipey"]),
        "endTime           %d   writeInterval %d   purgeWrite 2" % (spec["endTime"], spec["endTime"] // 10),
        "residualControl   none (L-141; removed from the frozen build_t4 fvSolution by registration)",
        "fields / BCs      build_t4.fields() and constant_files() FROZEN, called unchanged (T4 AMENDMENT 2 table)",
    ]) + "\n")
    print("built %-10s N=%-4d cells=%-7d endTime=%-6d first_cell=%.3g m  "
          "grading(plate=%.4g jetcore=%.4g[q=%.4f, fine at r0] outer=%.4g pipey=%.4g)"
          % (CASE_PREFIX + level, spec["N"], info["cells"], spec["endTime"],
             spec["first_cell"], info["g_plate"], info["g_pipew"], info["q_pipe"],
             info["g_out"], info["g_pipey"]))
    return info["cells"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--level", action="append", choices=list(LEVELS))
    a = ap.parse_args()
    tot = 0
    for lv in (a.level or ["c", "m", "f"]):
        tot += build(a.root, lv)
    print("U_bulk = %.4f m/s   Re = %.0f   total cells = %d" % (U_BULK, RE, tot))
