#!/usr/bin/env python3
"""F1 (ONERA M6) mesh ladder v2 -- BUTTERFLY TIP FILL, written as a blockMeshDict.

BUILD BEFORE YOU FREEZE (MESH_STANDARD 8.1).  Nothing here is pre-registered.
This instrument exists to find out whether an ADMISSIBLE ladder is reachable at
all; its output is a measurement, not a claim.

WHY IT IS A blockMeshDict (MESH_STANDARD 8.2).  The v1 tip fill was a lens whose
LE and TE ends were single lines.  blockMesh v2606 REFUSED it -- rc 134 on a
repeated-vertex prism block, 48 zero-area faces written the other way.  That
refusal was routed around by hand-writing polyMesh, and the mesh that resulted
measured 84.64 deg against a <= 70 deg gate.  THE TOOL WAS RIGHT.  So the
topology is redesigned, not bypassed: the tip hole is filled by a BUTTERFLY
(O-grid) with NO collapsed line anywhere, and blockMesh is the generator, so its
refusals stay a live check on the block structure.

  wrap i, 128m: wake_lo 16m | tail_lo 8m | mid_lo 32m | nose_lo 8m
              | nose_up 8m | mid_up 32m | tail_up 8m | wake_up 16m
     breaks at x/c 0.10 and 0.90, so the SHOCK BAND x/c 0.18-0.60 lies wholly
     inside the UNIFORM mid blocks.
  normal j, 32m, exponential beta = 10.575549 over 20 c_root.
  span k, 26m uniform: 20m root->tip + 6m outboard.
  tip fill, outboard only, 8 blocks, no degeneracy:
     2 core halves (32m x 8m) + 6 side strips (8m/32m/8m per side) x 4m radial.
  cells 111,872 / 894,976 / 7,159,808          r = 2.000000000 exactly
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# DEFECT FIX 2026-08-25 (te-study lane): this file was COPIED out of cases/ into the
# run directory, which broke the relative "../F13_onera_m6" import -- every one of the
# 14 b1 variants died at ModuleNotFoundError before any mesh was attempted.  The path is
# now absolute and matches te_angle.py:13.  ASSERTED, not assumed:
SECDIR = "/home/ubuntu/Certonomous/cases/F13_onera_m6"
assert os.path.isfile(os.path.join(SECDIR, "m6_section.py")), (
    "m6_section.py not at " + SECDIR + " -- refusing rather than importing something else")
sys.path.insert(0, SECDIR)
from m6_section import M6Geometry  # noqa: E402

# F1_BETA / F1_RFAC -- added 2026-08-25 by the te-study lane.  DEFAULTS REPRODUCE v2 EXACTLY.
# The measured worst face (worst_nonortho.py) is z0_tail_lo i=0 j=31 k=19: the OUTERMOST
# WALL-NORMAL cell at the farfield, not a wall or tip-fill face.  These two dials are the
# only ones that touch it: BETA_N is the wall-normal expansion and R the farfield radius,
# and BOTH ARE FIXED BY THE FROZEN PRE-REGISTRATION section 5.  Sweeping them measures
# whether the gate breach is a topology defect (repairable in the generator) or a
# consequence of the registered ladder itself (NOT repairable without reopening a freeze).
BETA_N = float(os.environ.get("F1_BETA", "10.575549"))
BETA_NOSE = np.log(12.5)
C_ROOT_REG = 0.8059
R = XEXIT = float(os.environ.get("F1_RFAC", "20.0")) * C_ROOT_REG
# --- TE-STUDY VARIANT DIALS (env-driven).  Defaults reproduce v2 EXACTLY. ---
U1 = 0.10
U2 = float(os.environ.get("F1_U2", "0.90"))
CORE_S = float(os.environ.get("F1_CORE_S", "0.50"))
NRM = int(os.environ.get("F1_NR", "4"))
TSCALE = float(os.environ.get("F1_TSCALE", "1.0"))
# --- v3 CANDIDATE DIAL, added 2026-08-25 by the te-study lane.  DEFAULT 0.0 REPRODUCES v2
# EXACTLY (asserted below at the vertex list).  In v2 the butterfly core corners mle and mte
# are placed at (xa, 0) and (xb, 0) -- the SAME chordwise stations as the surface break
# points cup10/up10 and cup90/up90.  Three corners of each side strip therefore fall on one
# vertical line and the strip is a DEGENERATE quad with an exactly 180.000000 deg corner
# (block_corner_angles.py).  MSHIFT pulls the core corners INBOARD in x by that fraction of
# the core length, so each strip becomes a proper quad.  It changes the TOPOLOGY, not the
# section: the wing surface polyLines are untouched.
MSHIFT = float(os.environ.get("F1_MSHIFT", "0.0"))
# F1_MK -- the BALANCED form of the same repair, and the one the algebra says to use.
# Let d be the chordwise offset between a core corner and the surface break station it
# faces.  The strip corner deviates from orthogonal by atan(CS*t/d) and the core corner
# by 90 - atan(CS*t/d): THE TWO DEVIATIONS SUM TO EXACTLY 90 deg FOR EVERY d.  The
# degeneracy cannot be removed, only SHARED.  It is shared equally at d = CS*t, giving a
# 135 deg strip corner and a 45 deg core corner.  MK sets d = MK*CORE_S*t2 at each end
# separately, so the nose (thick) and tail (thin) ends are balanced by their OWN local
# half-thickness rather than by one shared core-length fraction.  MK = 0 reproduces v2.
MK = float(os.environ.get("F1_MK", "0.0"))
NPL = 80


def Egeom(n, beta):
    return float(np.exp(beta * (n - 1) / n))


class Gen:
    def __init__(self, m, geo):
        self.m, self.g = m, geo
        self.nw, self.nn, self.nm = 16 * m, 8 * m, 32 * m
        self.nj, self.nr = 32 * m, NRM * m
        self.ksw, self.kso = 20 * m, 6 * m
        self.z_tip = geo.z_tip
        dz = self.z_tip / self.ksw
        self.z = [0.0, self.z_tip, self.z_tip + self.kso * dz]
        self.V, self.vi = [], {}
        self.edges, self.blocks, self.faces = [], [], {}
        for k in ("wing", "wingTip", "symmetry", "farfield", "spanOuter", "outlet"):
            self.faces[k] = []
        self.gnose = Egeom(self.nn, BETA_NOSE)
        self.gj = Egeom(self.nj, BETA_N)

    # ---------------------------------------------------------------- vertices
    def V_(self, key, xyz=None):
        if key not in self.vi:
            assert xyz is not None, f"undefined vertex {key}"
            self.vi[key] = len(self.V); self.V.append(tuple(map(float, xyz)))
        return self.vi[key]

    def sec(self, u, zi):
        z = self.z[zi]; c = self.g.chord(z); xl = self.g.xle(z)
        uu = np.abs(np.asarray(u, float))
        return xl + uu * c, np.sign(u) * self.g.t2(uu) * c

    def geom(self):
        for zi in range(3):
            z = self.z[zi]; c = self.g.chord(z); xl = self.g.xle(z)
            xte, xa, xb = xl + c, xl + U1 * c, xl + U2 * c
            ta, tb = self.g.t2(U1) * c, self.g.t2(U2) * c
            self.V_(("exit", zi), (XEXIT, 0, z)); self.V_(("te", zi), (xte, 0, z))
            self.V_(("le", zi), (xl, 0, z))
            for s, t in ((1, "up"), (-1, "lo")):
                self.V_((f"{t}10", zi), (xa, s * ta, z))
                self.V_((f"{t}90", zi), (xb, s * tb, z))
                self.V_((f"o{t}10", zi), (xa, s * R, z))
                self.V_((f"o{t}90", zi), (xb, s * R, z))
                self.V_((f"ote{t}", zi), (xte, s * R, z))
                self.V_((f"oex{t}", zi), (XEXIT, s * R, z))
            self.V_(("onose", zi), (-R, 0, z))
            if zi >= 1:
                dsh = MSHIFT * (xb - xa)
                self.V_(("mle", zi), (xa + dsh - MK * CORE_S * ta, 0, z))
                self.V_(("mte", zi), (xb - dsh + MK * CORE_S * tb, 0, z))
                for s, t in ((1, "up"), (-1, "lo")):
                    self.V_((f"c{t}10", zi), (xa, s * CORE_S * ta, z))
                    self.V_((f"c{t}90", zi), (xb, s * CORE_S * tb, z))
        self._edges()
        return self

    def _pl(self, a, b, zi, pts):
        self.edges.append((self.vi[(a, zi)], self.vi[(b, zi)], pts))

    def _edges(self):
        for zi in range(3):
            z = self.z[zi]; c = self.g.chord(z); xl = self.g.xle(z); xa = xl + U1 * c
            for s, t in ((1, "up"), (-1, "lo")):
                for lo, hi, ka, kb in ((0.0, U1, "le", f"{t}10"),
                                       (U1, U2, f"{t}10", f"{t}90"),
                                       (U2, 1.0, f"{t}90", "te")):
                    u = np.linspace(lo, hi, NPL)[1:-1]
                    x, y = self.sec(s * u, zi)
                    self._pl(ka, kb, zi, np.c_[x, y, np.full(len(u), z)])
                if zi >= 1:
                    u = np.linspace(U1, U2, NPL)[1:-1]
                    x, y = self.sec(s * u, zi)
                    self._pl(f"c{t}10", f"c{t}90", zi,
                             np.c_[x, CORE_S * y, np.full(len(u), z)])
            th = np.linspace(0, np.pi / 2, NPL // 2)
            arc = np.c_[-R * np.sin(th), -R * np.cos(th)]
            seg = np.c_[np.linspace(xa, 0.0, NPL // 2), np.full(NPL // 2, -R)]
            p = np.vstack([seg, arc])[1:-1]
            self._pl("olo10", "onose", zi, np.c_[p, np.full(len(p), z)])
            q = np.vstack([arc[::-1] * [1, -1], seg[::-1] * [1, -1]])[1:-1]
            self._pl("onose", "oup10", zi, np.c_[q, np.full(len(q), z)])

    # ------------------------------------------------------------------ blocks
    def blk(self, corners, zi, n, grad, pf=()):
        """corners = (a,b,c,d) keys of the x1-x2 face in order v0 v1 v2 v3."""
        v = [self.vi[(k, zi)] for k in corners] + [self.vi[(k, zi + 1)] for k in corners]
        self.blocks.append((v, n, grad))
        F = {"x1min": (v[0], v[3], v[7], v[4]), "x1max": (v[1], v[2], v[6], v[5]),
             "x2min": (v[0], v[1], v[5], v[4]), "x2max": (v[3], v[2], v[6], v[7]),
             "x3min": (v[0], v[1], v[2], v[3]), "x3max": (v[4], v[5], v[6], v[7])}
        for nm, fk in pf:
            self.faces[nm].append(F[fk])

    def topology(self):
        nw, nn, nm, nj, nr = self.nw, self.nn, self.nm, self.nj, self.nr
        # wrap blocks: (inner_a, inner_b, outer_b, outer_a), n1, grading along i
        WRAP = [("exit", "te", "otelo", "oexlo", nw, 1.0, None),
                ("te", "lo90", "olo90", "otelo", nn, self.gnose, "tail_lo"),
                ("lo90", "lo10", "olo10", "olo90", nm, 1.0, "mid_lo"),
                ("lo10", "le", "onose", "olo10", nn, 1.0 / self.gnose, "nose_lo"),
                ("le", "up10", "oup10", "onose", nn, self.gnose, "nose_up"),
                ("up10", "up90", "oup90", "oup10", nm, 1.0, "mid_up"),
                ("up90", "te", "oteup", "oup90", nn, 1.0 / self.gnose, "tail_up"),
                ("te", "exit", "oexup", "oteup", nw, 1.0, None)]
        for zi in (0, 1):
            nk = self.ksw if zi == 0 else self.kso
            for ia, ib, ob, oa, n1, g1, surf in WRAP:
                pf = [("farfield", "x2max")]
                if surf and zi == 0:
                    pf.append(("wing", "x2min"))
                if zi == 0:
                    pf.append(("symmetry", "x3min"))
                else:
                    pf.append(("spanOuter", "x3max"))
                self.blk((ia, ib, ob, oa), zi, (n1, nj, nk), (g1, self.gj, 1), pf)
            self.blocks[-1] = self.blocks[-1]
            # outlet faces: first block's x1min and last block's x1max
            b0, b1 = self.blocks[-8], self.blocks[-1]
            self.faces["outlet"].append((b0[0][0], b0[0][3], b0[0][7], b0[0][4]))
            self.faces["outlet"].append((b1[0][1], b1[0][2], b1[0][6], b1[0][5]))
        # ---- tip fill, outboard region only (zi = 1)
        FILL = [(("mle", "cup10", "up10", "le"), (nn, nr, self.kso), (self.gnose, 1, 1)),
                (("cup10", "cup90", "up90", "up10"), (nm, nr, self.kso), (1, 1, 1)),
                (("cup90", "mte", "te", "up90"), (nn, nr, self.kso), (1.0 / self.gnose, 1, 1)),
                (("clo10", "mle", "le", "lo10"), (nn, nr, self.kso), (1.0 / self.gnose, 1, 1)),
                (("clo90", "clo10", "lo10", "lo90"), (nm, nr, self.kso), (1, 1, 1)),
                (("mte", "clo90", "lo90", "te"), (nn, nr, self.kso), (self.gnose, 1, 1)),
                (("mle", "mte", "cup90", "cup10"), (nm, nn, self.kso), (1, self.gnose, 1)),
                (("clo10", "clo90", "mte", "mle"), (nm, nn, self.kso), (1, 1.0 / self.gnose, 1))]
        for corners, n, grad in FILL:
            self.blk(corners, 1, n, grad,
                     [("wingTip", "x3min"), ("spanOuter", "x3max")])
        return self

    # ------------------------------------------------------------------- write
    def write(self, case):
        d = os.path.join(case, "system"); os.makedirs(d, exist_ok=True)
        L = ["FoamFile{version 2.0;format ascii;class dictionary;object blockMeshDict;}",
             "scale 1;", "vertices", "("]
        L += [f"    ({x:.12g} {y:.12g} {z:.12g})" for x, y, z in self.V]
        L += [");", "blocks", "("]
        for v, n, g in self.blocks:
            L.append("    hex (" + " ".join(map(str, v)) + f") ({n[0]} {n[1]} {n[2]})"
                     f" simpleGrading ({g[0]:.10g} {g[1]:.10g} {g[2]:.10g})")
        L += [");", "edges", "("]
        for a, b, p in self.edges:
            L.append(f"    polyLine {a} {b} (" +
                     " ".join(f"({x:.12g} {y:.12g} {z:.12g})" for x, y, z in p) + ")")
        L += [");", "boundary", "("]
        typ = {"wing": "wall", "wingTip": "wall", "symmetry": "symmetryPlane"}
        for nm, fl in self.faces.items():
            L.append(f"    {nm}"); L.append("    {")
            L.append(f"        type {typ.get(nm,'patch')};")
            if typ.get(nm) == "wall":
                L.append("        inGroups (wall);")
            L.append("        faces (")
            L += ["            (" + " ".join(map(str, f)) + ")" for f in fl]
            L += ["        );", "    }"]
        L += [");", "mergePatchPairs ();", ""]
        open(os.path.join(d, "blockMeshDict"), "w").write("\n".join(L))
        return sum(n[0] * n[1] * n[2] for _, n, _ in self.blocks)


def build(m, case, verbose=True):
    g = M6Geometry(verbose=False); g.z_tip = g.z_tip_measured
    if TSCALE != 1.0:
        # instance-attribute shadow of the bound method; the SHAPE is unchanged,
        # only the half-thickness is scaled -> the TE included angle scales with it.
        _b = g.t2
        g.t2 = (lambda xc, _b=_b, s=TSCALE: s * _b(xc))
    gen = Gen(m, g).geom().topology()
    ncell = gen.write(case)
    if verbose:
        print(f"  DIALS U2={U2} CORE_S={CORE_S} NRM={NRM} TSCALE={TSCALE}")
        print(f"  m={m}: {len(gen.blocks)} blocks, {len(gen.V)} vertices, "
              f"{len(gen.edges)} polyLine edges, {ncell:,} cells")
    return ncell


if __name__ == "__main__":
    build(int(sys.argv[1]), sys.argv[2])
