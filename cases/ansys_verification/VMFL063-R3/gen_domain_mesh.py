#!/usr/bin/env python3
# =============================================================================
# VMFL063-R3 DOMAIN-MESH GENERATOR -- the SOLE, FROZEN, DOF-FREE mesh-construction
# authority (PREREGISTRATION sec.4.2). The launcher calls it as:
#     gen_domain_mesh.py <DOMAIN> <LEVEL>   ->  blockMeshDict on stdout
# DOMAIN in {D0,D1,D2}; LEVEL in {L1,L2,L3}.  It emits NOTHING else, and is
# DETERMINISTIC: identical (DOMAIN,LEVEL) -> identical bytes.
#
# DESIGN (answer-blind; L-501 grading-DOF hazard absent by construction):
#   * The NEAR-FIELD blocks A/B/C -- x in [-0.9,1.5], y in [0,1.8] -- reproduce
#     R2's geometry EXACTLY: same block boundaries, same r=2 octave counts
#     (NXU/NXD/NYL/NYU), same gradings A(0.1 0.2 1) B(0.1 160 1) C(20 160 1).
#     This region holds the blunt corner, the shear layer and the reattachment
#     bubble -- ALL the physics that sets LR -- so its cell sizes equal R2-L3's
#     and grid-independence is INHERITED (PREREGISTRATION sec.4.1). No near-field
#     grading DOF.
#   * ENLARGEMENT (D1,D2) APPENDS FAR-FIELD padding blocks (upstream x<-0.9, top
#     y>1.8). Padding SHARES the near-field cell COUNT on every shared edge, and
#     uses UNIFORM grading with counts that DOUBLE per level (r=2), so the whole
#     mesh stays one self-similar family. Padding is far from the bubble and
#     cannot move LR; its counts are fixed by a stated rule, not hand-tunable.
#   * The far-field top (y=H) and outer upstream face (x=-Lu) carry a plain
#     `patch` (the de-confined open BC lives in 0/U, 0/p). centreline stays
#     symmetryPlane; plateFace/plateTop stay wall; frontAndBack stays empty.
#
# Frozen under CLAUDE.md rule 2; the launcher pins it disk==HEAD before compute.
# =============================================================================
import sys

# --- FROZEN geometry (VM2026R1 p.193) ---
T_HALF = 0.045        # plate top surface y
LD     = 1.500        # plate length / downstream extent (manual; held fixed)
LU_NF  = 0.900        # near-field upstream boundary (R2's; x=-0.9)
H_NF   = 1.800        # near-field top boundary (R2's; y=1.8)
ZF, ZB = -0.005, 0.005

# --- FROZEN domain ladder (PREREGISTRATION sec.4.3): (Lu, H); Ld held at LD ---
DOMAIN_EXTENTS = {"D0": (0.900, 1.800), "D1": (1.800, 3.600), "D2": (3.600, 7.200)}

# --- FROZEN near-field r=2 octave counts (R2's): NXU NXD NYL NYU ---
LEVEL_COUNTS = {"L1": (64, 160, 24, 96), "L2": (128, 320, 48, 192),
                "L3": (256, 640, 96, 384)}
# --- FROZEN near-field gradings (R2's): last/first per direction ---
GR_A = (0.1, 0.2)     # block A: x, y
GR_B = (0.1, 160.0)   # block B: x, y
GR_C = (20.0, 160.0)  # block C: x, y

# --- FROZEN padding counts at L1; DOUBLE per level (r=2), UNIFORM grading. Far
#     field, so these do not affect LR; stated deterministically all the same. ---
NX_UP_L1, NY_TOP_L1 = 12, 24
LEVEL_FACTOR = {"L1": 1, "L2": 2, "L3": 4}


class Mesh:
    def __init__(self):
        self.V = []
        self.idx = {}
        self.blocks = []
    def v(self, x, y, z):
        k = (round(x, 9), round(y, 9), round(z, 9))
        if k not in self.idx:
            self.idx[k] = len(self.V)
            self.V.append(k)
        return self.idx[k]
    def block(self, x0, x1, y0, y1, nx, ny, gx, gy):
        c = [(x0, y0, ZF), (x1, y0, ZF), (x1, y1, ZF), (x0, y1, ZF),
             (x0, y0, ZB), (x1, y0, ZB), (x1, y1, ZB), (x0, y1, ZB)]
        self.blocks.append(([self.v(*p) for p in c], nx, ny, gx, gy))
    def face(self, x0, x1, y0, y1):
        if x0 == x1:
            pts = [(x0, y0, ZF), (x0, y1, ZF), (x0, y1, ZB), (x0, y0, ZB)]
        else:
            pts = [(x0, y0, ZF), (x1, y0, ZF), (x1, y0, ZB), (x0, y0, ZB)]
        return "( %s )" % " ".join(str(self.v(*p)) for p in pts)


def build(domain, level):
    Lu, H = DOMAIN_EXTENTS[domain]
    NXU, NXD, NYL, NYU = LEVEL_COUNTS[level]
    f = LEVEL_FACTOR[level]
    # padding counts scale with the r=2 level AND with how far the boundary is
    # pushed out, so the padding CELL SIZE stays ~constant across the ladder and
    # the far-field aspect ratio stays bounded. Deterministic from frozen extents.
    mult_up  = int(round((Lu - LU_NF) / LU_NF))
    mult_top = int(round((H - H_NF) / H_NF))
    NX_up, NY_top = NX_UP_L1 * f * mult_up, NY_TOP_L1 * f * mult_top
    up  = Lu > LU_NF + 1e-12
    top = H > H_NF + 1e-12
    m = Mesh()

    # --- NEAR-FIELD (R2 geometry, EXACT) -------------------------------------
    m.block(-0.9, 0.0, 0.0, T_HALF, NXU, NYL, GR_A[0], GR_A[1])   # A
    m.block(-0.9, 0.0, T_HALF, H_NF, NXU, NYU, GR_B[0], GR_B[1])  # B
    m.block(0.0, LD, T_HALF, H_NF, NXD, NYU, GR_C[0], GR_C[1])    # C

    # --- FAR-FIELD padding (uniform grading; shares near-field counts) -------
    if up:                       # upstream padding, split at y=T_HALF (match A/B)
        m.block(-Lu, -0.9, 0.0, T_HALF, NX_up, NYL, 1.0, GR_A[1])
        m.block(-Lu, -0.9, T_HALF, H_NF, NX_up, NYU, 1.0, GR_B[1])
    if top:                      # top padding, split at x=-0.9, x=0 (and -Lu if up)
        m.block(-0.9, 0.0, H_NF, H, NXU, NY_top, GR_B[0], 1.0)
        m.block(0.0, LD, H_NF, H, NXD, NY_top, GR_C[0], 1.0)
        if up:
            m.block(-Lu, -0.9, H_NF, H, NX_up, NY_top, 1.0, 1.0)

    # --- boundary patches (only NON-degenerate sub-faces emitted) ------------
    inlet, outlet, centre, pface, ptop, far = [], [], [], [], [], []
    inlet.append(m.face(-Lu, -Lu, 0.0, T_HALF))
    inlet.append(m.face(-Lu, -Lu, T_HALF, H_NF))
    if top:
        inlet.append(m.face(-Lu, -Lu, H_NF, H))
    outlet.append(m.face(LD, LD, T_HALF, H_NF))
    if top:
        outlet.append(m.face(LD, LD, H_NF, H))
    if up:
        centre.append(m.face(-Lu, -0.9, 0.0, 0.0))
    centre.append(m.face(-0.9, 0.0, 0.0, 0.0))
    pface.append(m.face(0.0, 0.0, 0.0, T_HALF))
    ptop.append(m.face(0.0, LD, T_HALF, T_HALF))
    if up:
        far.append(m.face(-Lu, -0.9, H, H))
    far.append(m.face(-0.9, 0.0, H, H))
    far.append(m.face(0.0, LD, H, H))

    out = ["/*----- generated by gen_domain_mesh.py %s %s (VMFL063-R3, frozen) -----*/"
           % (domain, level),
           "FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }",
           "scale 1;", "vertices ("]
    for (x, y, z) in m.V:
        out.append("    (%.9g %.9g %.9g)" % (x, y, z))
    out.append(");")
    out.append("blocks (")
    for ids, nx, ny, gx, gy in m.blocks:
        out.append("    hex (%s) (%d %d 1) simpleGrading (%.9g %.9g 1)"
                   % (" ".join(map(str, ids)), nx, ny, gx, gy))
    out.append(");")
    out.append("edges ();")
    out.append("boundary (")

    def patch(name, typ, fs):
        return "  %s { type %s; faces ( %s ); }" % (name, typ, " ".join(fs))
    out.append(patch("inlet", "patch", inlet))
    out.append(patch("outlet", "patch", outlet))
    out.append(patch("centreline", "symmetryPlane", centre))
    out.append(patch("plateFace", "wall", pface))
    out.append(patch("plateTop", "wall", ptop))
    out.append(patch("farfield", "patch", far))
    out.append(");")
    out.append('defaultPatch { name frontAndBack; type empty; }')
    return "\n".join(out) + "\n"


def main(argv):
    if len(argv) != 2 or argv[0] not in DOMAIN_EXTENTS or argv[1] not in LEVEL_COUNTS:
        sys.stderr.write("usage: gen_domain_mesh.py <D0|D1|D2> <L1|L2|L3>\n")
        return 2
    sys.stdout.write(build(argv[0], argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
