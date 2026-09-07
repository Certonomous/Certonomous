#!/usr/bin/env python3
"""Build the three registered T4d impinging-jet cases (successor of T4b, itself the
wall-resolved successor of T4).

T4d re-runs T4b (ERCOFTAC case025 ij2lr, H/D = 2, Re_D = 23 000, axisymmetric wedge,
steady buoyantBoussinesqSimpleFoam with beta = 0, kOmegaSST) with THREE registered
changes against build_t4b.py, each stated here and in T4d_PREREGISTRATION.md, and
NOTHING else changed.  It carries over every band, reference, threshold, floor and
control of T4b UNCHANGED; what changes is the three things the T4b run measured to be
wrong (T4b_RESULTS.md, gate_t4b.json):

  A. JET-CORE/PIPE RADIAL RESOLUTION DOUBLED, FAMILY-WIDE: nrj = 3N/2 (T4b: 3N/4).
     The wall-jet radial (3N/2), axial (N) and pipe-axial (N/2) divisions are
     unchanged, so r = 2 is preserved exactly in every direction and cells become
     3.75 N^2 (T4b: 2.625 N^2): 8 640 / 34 560 / 138 240.  Ground: coarse C2
     (U_c/U_bulk = 1.1746) is RESOLUTION-limited, not pipe-length limited -- it
     converges c->m->f (1.1746, 1.1909, 1.2021 toward 1.2245) and the T4b medium
     level, which carries 72 jet-core-radial cells, PASSES C2.  Doubling the radial
     count with the first cell FIXED gives a gentler grading and finer axis cells
     -- resolving the centreline exit peak -- without moving the wall cell, so C1
     (plate y+) and C1b (pipe y+) are unaffected.  The refinement also lowers every
     level's residual plateau (the coarse-C6.1 and medium-C6.3 levers).

  B. UNDER-RELAXATION of U, T, k, omega reduced 0.7 -> 0.6, family-wide (p_rgh 0.3
     unchanged), applied in system_files() below.  Ground: the T4b medium velocity
     residual plateaus in a LIMIT CYCLE (~7.3e-7, COV 0.28 from ~15 000 iterations),
     so more iterations alone cannot clear C6.3; a modest under-relaxation reduction
     damps the cycle so the residual decays.  This changes only the iteration PATH,
     never the converged fixed point, so it moves no band and games no gate.

  C. endTime schedule 20000 / 30000 / 40000 -> 30000 / 60000 / 64000, sized so the
     predicted C6.3 field change clears the 2e-04 floor with margin at every level
     (T4d_PREREGISTRATION.md section 3).  writeInterval (2000 / 3000 / 4000) and
     purgeWrite 2 are UNCHANGED, so C6.3 measures the IDENTICAL iteration window it
     measured in T4b -- the measurement is not shortened to manufacture a pass.

The two T4b mesh changes (first cell halved at every level; jet-core/pipe radial
grading INVERTED so the fine cell sits on the pipe wall for the C1b y+ gate) are
INHERITED unchanged through the same block_mesh_dict topology.  Everything else --
every boundary condition per field per patch, transportProperties,
turbulenceProperties, g, schemes, linear solvers -- is produced by the FROZEN
build_t4.py's own writers, imported here and never copied.  fields() and
constant_files() are called unchanged; header() and grading_ratio() are reused.

NO `assert` STATEMENT IN THIS FILE (L-332).  Refusals are explicit exits.

Usage:  build_t4d.py [--root <dir>] [--level c|m|f] ...
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

LEVELS = {"c": dict(N=48,  endTime=30000, writeInterval=2000, first_cell=1.2e-5),
          "m": dict(N=96,  endTime=60000, writeInterval=3000, first_cell=6.0e-6),
          "f": dict(N=192, endTime=64000, writeInterval=4000, first_cell=3.0e-6)}
CASE_PREFIX = "T4d_IJ_"


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

    nrj = (3 * N) // 2    # radial cells, jet core and pipe (T4b: 3N/4; DOUBLED, T4d Change A)
    nrw = (3 * N) // 2    # radial cells, wall-jet block (unchanged; now equals nrj)
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


def system_files(endTime, writeInterval):
    """The frozen build_t4.system_files() output with THREE registered changes:
    (1) the residualControl block is removed (L-141); (2) the U/T/k/omega
    under-relaxation factors are reduced 0.7 -> 0.6 (T4d Change B) to damp the
    medium velocity-residual limit cycle measured in T4b (p_rgh 0.3 unchanged);
    (3) writeInterval is PINNED to the registered value (part of Change C).  The
    frozen build_t4 writer derives writeInterval = endTime/10; T4d's endTimes
    (30000/60000/64000) would give 3000/6000/6400, but T4d keeps the T4b windows
    2000/3000/4000 so C6.3 measures the IDENTICAL iteration window (the last two
    written checkpoints) it measured in T4b.  Refuses unless exactly one
    residualControl block, exactly four 0.7 relaxation factors, and exactly one
    writeInterval line were present and changed -- so a change to the inherited
    frozen writer cannot pass silently -- and unless endTime is a multiple of
    writeInterval (else the last checkpoint would not land on endTime)."""
    files = B.system_files(endTime)
    sol, n = re.subn(r"^\s*residualControl\s*\{[^}]*\}\s*\n", "", files["fvSolution"], flags=re.M)
    if n != 1:
        refuse("fvSolution: expected exactly one residualControl block to remove, found %d" % n)
    if "residualControl" in sol:
        refuse("fvSolution still mentions residualControl after the registered removal")
    sol, m = re.subn(r"\b(U|T|k|omega)(\s+)0\.7\b", r"\g<1>\g<2>0.6", sol)
    if m != 4:
        refuse("fvSolution: expected exactly four 0.7 under-relaxation factors "
               "(U, T, k, omega) to change to 0.6, changed %d" % m)
    files["fvSolution"] = sol
    if endTime % writeInterval != 0:
        refuse("endTime %d is not a multiple of writeInterval %d -- the last "
               "checkpoint would not land on endTime" % (endTime, writeInterval))
    cd, w = re.subn(r"^(\s*writeInterval\s+)\d+(\s*;)", r"\g<1>%d\g<2>" % writeInterval,
                    files["controlDict"], flags=re.M)
    if w != 1:
        refuse("controlDict: expected exactly one writeInterval line to pin, found %d" % w)
    files["controlDict"] = cd
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
    for n, t in system_files(spec["endTime"], spec["writeInterval"]).items():
        open(os.path.join(case, "system", n), "w").write(t)
    for n, t in B.constant_files().items():
        open(os.path.join(case, "constant", n), "w").write(t)
    for n, t in B.fields(level).items():
        open(os.path.join(case, "0.orig", n), "w").write(t)
    open(os.path.join(case, "CASE.txt"), "w").write("\n".join([
        "case              %s" % (CASE_PREFIX + level),
        "rung              T4d (successor of T4b; ERCOFTAC case025 ij2lr, H/D 2, Re 23000)",
        "level             %s   N = %d" % (level, spec["N"]),
        "solver            buoyantBoussinesqSimpleFoam (ESI v2606), kOmegaSST, beta 0, wedge %.1f deg" % WEDGE_DEG,
        "first_cell        %.3e m (plate AND pipe wall / nozzle lip)" % spec["first_cell"],
        "divisions         jet-core/pipe radial %d (3N/2), wall-jet radial %d, axial %d, pipe axial %d"
        % (info["nrj"], info["nrw"], info["nyj"], info["nyp"]),
        "cells             %d  (3.75 N^2)" % info["cells"],
        "grading           plate %.6g  jet-core radial %.6g (INVERTED: fine at r0, cell growth %.4f)  wall-jet %.6g  pipe axial %.6g"
        % (info["g_plate"], info["g_pipew"], info["q_pipe"], info["g_out"], info["g_pipey"]),
        "endTime           %d   writeInterval %d   purgeWrite 2" % (spec["endTime"], spec["writeInterval"]),
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
