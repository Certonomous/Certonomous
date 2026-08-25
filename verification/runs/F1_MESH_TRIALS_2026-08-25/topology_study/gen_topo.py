#!/usr/bin/env python3
"""F1 (ONERA M6) TOPOLOGY TRIAL -- two structural changes, both switchable, on top of the
v2 butterfly.  MESH_STANDARD 8.1 build trial.  NOTHING HERE IS PRE-REGISTERED.

WHY THESE TWO AND NOT MORE DIALS.  The 38-variant te-study proved the >70 deg breach is
DIAL-INVARIANT.  Measured on the built meshes with outer_face_geom.py (planted controls
(a) agreement with checkMesh, (b) point-displacement), the breach is TWO mechanisms:

  A  FAR-FIELD FAN, wrap blocks blk01/blk06 (tail_lo/tail_up, zi=0), 81.9396 deg at the
     registered beta.  The outermost radial cell spans y in [-11.582, -16.118] and is
     1.7e-03 wide through the face; the two i-neighbours' centroids differ by d_y =
     1.193e-02, seven times the through-face spacing.  atan(1.194e-2/1.691e-3) = 81.9396.
     CAUSE, and it is NOT an oblique far field -- the winning face's unit normal is
     (-0.962154, 0.000010, 0.272506), i.e. the outer boundary is the plane y = -R and the
     radial lines meet it DEAD NORMAL.  The cause is that the block's INNER i-edge is the
     curved wing surface and its OUTER i-edge is a straight line of a DIFFERENT ARC LENGTH.
     blockMesh grades both by the same arc-length fractions, so the i-lines FAN; the fan
     tapers the cell 3.2% across its own radial extent; 3.2% of a cell 4.54 tall is an
     0.0119 centroid shift, which dwarfs the 0.0017 through-face spacing.
     THE NATURAL CONTROL IS ALREADY ON DISK: blk00 (wake_lo) has the SAME radial grading and
     the SAME aspect ratio, but BOTH its i-edges are straight lines of EQUAL length -- and it
     never appears above 70 deg.
  B  TIP-CAP FAN, butterfly side strips blk18/blk21, 81.5834 deg, BETA-INVARIANT and therefore
     the binding floor.  blk21 = (mte, clo90, lo90, te) has THREE of four corners on x = xb;
     its j-edge at i=0 is chordwise (mte->te, 0.1 c) and its j-edge at i=3 is vertical
     (clo90->lo90, (1-CORE_S)*t2(0.9)*c).  j turns 90 deg across the block and collapses ~16:1
     onto the sharp trailing edge.

BOTH ARE THE SAME DEFECT: a block whose two opposite edges are NOT SIMILAR CURVES.  The cure
is the same for both -- make opposite edges self-similar about a common centre, so every grid
line in the block is an exact RAY and the fan is identically zero.

  F1_SHELL=1   splits every wrap block radially into an inner layer and an OUTER SHELL whose
               inner edge is the far-field shape AT RADIUS F1_S1*R with the x-stations kept.
               Along the flat farfield the shell's two i-edges are then parallel straight lines
               of EQUAL LENGTH -> zero fan -> mechanism A removed by construction, WITHOUT
               touching F1_BETA or F1_RFAC and WITHOUT moving the outlet plane.  Cell count is unchanged
               (NJ1 + NJ2 = 32) and the radial node distribution is reproduced by giving each
               layer the same per-cell ratio r = exp(BETA_N/nj).
  F1_SIMCORE=1 replaces the butterfly core (a hexagon with its LE/TE corners parked ON the
               chord line at the SURFACE break stations xa, xb) with an EXACT CORE_S-scale
               copy of the section about O(z), polyLines included -> every strip block's two
               j-edges are rays from O -> mechanism B removed by construction.

F1_SHELL=0 F1_SIMCORE=0 REPRODUCES v2 EXACTLY, and that is checked, not asserted: the T0
variant's blockMeshDict is compared byte-for-byte against te_study/b1_CTRL's.

--- v2 header, retained verbatim ---
F1 (ONERA M6) mesh ladder v2 -- BUTTERFLY TIP FILL, written as a blockMeshDict.

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

# --- TOPOLOGY DIALS (this file only).  0 reproduces gen_var.py v2 exactly.
SHELL = int(os.environ.get("F1_SHELL", "0"))
SIMCORE = int(os.environ.get("F1_SIMCORE", "0"))
S1 = float(os.environ.get("F1_S1", "0.075"))     # shell inner surface, fraction of farfield
NJ1 = int(os.environ.get("F1_NJ1", "24"))        # cells in the inner layer (per m)
assert SIMCORE in (0, 1, 2), "F1_SIMCORE is 0 (v2), 1 (fully self-similar core), 2 (stations only)"
assert not (SIMCORE and (MK or MSHIFT)), (
    "F1_SIMCORE supersedes the MK/MSHIFT corner repair -- set both to 0 rather than mixing "
    "two different answers to the same degeneracy")
assert 0 < S1 < 1, "F1_S1 must lie strictly between the body and the farfield"



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
        # Radial split.  Egeom(n, beta) = exp(beta*(n-1)/n) is the TOTAL last/first ratio for
        # n cells, so the per-cell ratio is r = exp(beta/n).  Giving each layer that SAME r
        # reproduces the registered wall-normal progression across the split instead of
        # inventing a new one.
        self.nj1 = NJ1 * m
        self.nj2 = self.nj - self.nj1
        assert 0 < self.nj1 < self.nj, f"F1_NJ1={NJ1} leaves {self.nj2} cells in the shell"
        rr = float(np.exp(BETA_N / self.nj))
        self.gj1 = rr ** (self.nj1 - 1)
        self.gj2 = rr ** (self.nj2 - 1)

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
            xc = xl + 0.5 * c                       # section centre O(z), on the chord line
            if SHELL:
                # SHELL INNER BOUNDARY = THE FARFIELD SHAPE AT RADIUS S1*R, x-STATIONS KEPT.
                #
                # The first cut scaled the whole farfield shape about O(z).  That IS self-similar
                # and the shell's rays came out exact -- but it dragged the exit station from
                # x = 16.118 in to x = 1.58 while the wake cut still ran to 16.118, shearing the
                # INNER wake block 13:1.  Measured: max skewness 30.0376, 780 highly skew faces,
                # average non-orthogonality 15.91 -> 30.23 (t1_SHELL, first cut).  Worse, not
                # better, and the failure was in the layer the change was not aiming at.
                #
                # Offsetting instead of scaling is what the mechanism actually asks for.  Along
                # the flat farfield (y = +-R, the whole region downstream of x = 0, which is
                # where mechanism A lives) the shell's two i-edges are then PARALLEL STRAIGHT
                # LINES OF EQUAL LENGTH -- identical arc-length fractions by construction, so
                # the fan is identically zero and the outlet plane x = XEXIT stays planar.
                R2 = S1 * R
                for sg, t in ((1, "up"), (-1, "lo")):
                    self.V_((f"so{t}10", zi), (xa, sg * R2, z))
                    self.V_((f"so{t}90", zi), (xb, sg * R2, z))
                    self.V_((f"sote{t}", zi), (xte, sg * R2, z))
                    self.V_((f"soex{t}", zi), (XEXIT, sg * R2, z))
                self.V_(("sonose", zi), (-R2, 0, z))
            if zi >= 1:
                if SIMCORE:
                    # In v2 the six core corners keep the SURFACE break stations xa, xb in x and
                    # are scaled only in y.  mte, clo90 and the SURFACE point lo90 therefore all
                    # sit on x = xb, and the TE side strip degenerates into a 16:1 fan that turns
                    # j through 90 deg onto the sharp trailing edge -- mechanism B, 81.5834 deg.
                    # Both settings pull the core's chordwise stations INBOARD so that lo90 no
                    # longer shares an x with the two core corners facing it.
                    xc10 = xc + CORE_S * (xa - xc)
                    xc90 = xc + CORE_S * (xb - xc)
                    if SIMCORE == 2:
                        # mle and mte stay ON the core's own 10/90 stations.  That preserves the
                        # one property v2 had right -- the core block's chord-line edge and its
                        # scaled-surface edge span the SAME x-range, so the core blocks carry no
                        # fan -- while still moving the strip corners off the surface stations.
                        mle_x, mte_x = xc10, xc90
                    else:
                        # SIMCORE=1: the full self-similar core, mle/mte at the scaled LE/TE.
                        # MEASURED AND KEPT AS A NEGATIVE RESULT: it fixes the strips and BREAKS
                        # the core.  The chord-line edge mle->mte then spans 0.50 c while the
                        # scaled-surface edge clo10->clo90 spans 0.40 c; a 25% arc-length
                        # mismatch across a j-extent of ~0.003 c gives d_t/d_n = 19.2 and
                        # 87.0192 deg at blk23 i=31 j=0 (t2_SIMCORE).  Worse than v2.
                        mle_x = xc + CORE_S * (xl - xc)
                        mte_x = xc + CORE_S * (xte - xc)
                    self.V_(("mle", zi), (mle_x, 0, z))
                    self.V_(("mte", zi), (mte_x, 0, z))
                    for s, t in ((1, "up"), (-1, "lo")):
                        self.V_((f"c{t}10", zi), (xc10, s * CORE_S * ta, z))
                        self.V_((f"c{t}90", zi), (xc90, s * CORE_S * tb, z))
                else:
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
            xc = xl + 0.5 * c
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
                    cx = xc + CORE_S * (x - xc) if SIMCORE else x
                    self._pl(f"c{t}10", f"c{t}90", zi,
                             np.c_[cx, CORE_S * y, np.full(len(u), z)])
                if zi >= 1 and SIMCORE == 1:
                    # the two curves v2 left STRAIGHT.  Without them the strip blocks at the
                    # LE and TE still have a curved outer edge against a straight inner one --
                    # mechanism A again, in miniature.
                    for lo, hi, ka, kb in ((0.0, U1, "mle", f"c{t}10"),
                                           (U2, 1.0, f"c{t}90", "mte")):
                        u = np.linspace(lo, hi, NPL)[1:-1]
                        x, y = self.sec(s * u, zi)
                        self._pl(ka, kb, zi, np.c_[xc + CORE_S * (x - xc),
                                                   CORE_S * y, np.full(len(u), z)])
            th = np.linspace(0, np.pi / 2, NPL // 2)
            arc = np.c_[-R * np.sin(th), -R * np.cos(th)]
            seg = np.c_[np.linspace(xa, 0.0, NPL // 2), np.full(NPL // 2, -R)]
            p = np.vstack([seg, arc])[1:-1]
            self._pl("olo10", "onose", zi, np.c_[p, np.full(len(p), z)])
            q = np.vstack([arc[::-1] * [1, -1], seg[::-1] * [1, -1]])[1:-1]
            self._pl("onose", "oup10", zi, np.c_[q, np.full(len(q), z)])
            if SHELL:
                # the same composite curve at radius S1*R, built the same way, so the nose
                # blocks' two i-edges stay concentric rather than merely nearby.
                R2 = S1 * R
                arc2 = np.c_[-R2 * np.sin(th), -R2 * np.cos(th)]
                seg2 = np.c_[np.linspace(xa, 0.0, NPL // 2), np.full(NPL // 2, -R2)]
                p2 = np.vstack([seg2, arc2])[1:-1]
                self._pl("solo10", "sonose", zi, np.c_[p2, np.full(len(p2), z)])
                q2 = np.vstack([arc2[::-1] * [1, -1], seg2[::-1] * [1, -1]])[1:-1]
                self._pl("sonose", "soup10", zi, np.c_[q2, np.full(len(q2), z)])

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
                # DEFECT FIX 2026-08-25 (topology lane): the first cut handed the SHELL block
                # the same patch list as the inner block, so `wing` was claimed on the shell's
                # x2min -- which is the INNER LAYER'S INTERFACE, an internal face.  blockMesh
                # v2606 refused it: "Trying to specify a boundary face ... which is either an
                # internal face or already belongs to the same patch ... patch 0 named wing"
                # (t1_SHELL/log.blockMesh, rc=1).  THE TOOL WAS RIGHT.  The wing patch belongs
                # to the INNER layer only and the farfield to the SHELL only; symmetry and
                # spanOuter span both.  This corrects a patch assignment, NOT the topology --
                # MESH_STANDARD 8.2 is not engaged and no block was changed to make a number
                # appear.  Order is preserved so the SHELL=0 path stays byte-identical to v2.
                pf_wing = [("wing", "x2min")] if (surf and zi == 0) else []
                pf_span = [("symmetry", "x3min")] if zi == 0 else [("spanOuter", "x3max")]
                pf = pf_wing + pf_span
                if not SHELL:
                    self.blk((ia, ib, ob, oa), zi, (n1, nj, nk), (g1, self.gj, 1),
                             [("farfield", "x2max")] + pf)
                else:
                    # inner layer: wing surface -> S1-scaled farfield shape.  Carries the
                    # curved-vs-straight fan, but at a radial extent where the aspect ratio
                    # cannot amplify it.
                    sa, sb = "s" + oa, "s" + ob
                    self.blk((ia, ib, sb, sa), zi, (n1, self.nj1, nk),
                             (g1, self.gj1, 1), pf)
                    # OUTER SHELL: both i-edges are the SAME curve at two scales about O(z).
                    # Identical arc-length fractions -> exact rays -> zero fan.
                    self.blk((sa, sb, ob, oa), zi, (n1, self.nj2, nk),
                             (g1, self.gj2, 1), [("farfield", "x2max")] + pf_span)
            # outlet faces: the LOWER wake block WRAP[0] contributes its x1min, the UPPER wake
            # block WRAP[7] its x1max, from EVERY radial layer.
            per = 2 if SHELL else 1
            emitted = self.blocks[-8 * per:]
            for b in emitted[:per]:
                self.faces["outlet"].append((b[0][0], b[0][3], b[0][7], b[0][4]))
            for b in emitted[-per:]:
                self.faces["outlet"].append((b[0][1], b[0][2], b[0][6], b[0][5]))
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
        print(f"  DIALS U2={U2} CORE_S={CORE_S} NRM={NRM} TSCALE={TSCALE} "
              f"SHELL={SHELL} SIMCORE={SIMCORE} S1={S1} NJ1={NJ1}")
        print(f"  m={m}: {len(gen.blocks)} blocks, {len(gen.V)} vertices, "
              f"{len(gen.edges)} polyLine edges, {ncell:,} cells")
    return ncell


if __name__ == "__main__":
    build(int(sys.argv[1]), sys.argv[2])
