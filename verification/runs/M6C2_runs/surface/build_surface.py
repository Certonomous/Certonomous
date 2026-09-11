#!/usr/bin/env python3
"""M6C2 WING SURFACE MESH -- the thing a hyperbolic extruder (pyHyp) consumes.

Reuses M6C1's verified geometry unchanged: the source-faithful 72-row AGARD
section, the blunt base at t_TE/c = 1.4104e-03, and the conical loft. Nothing
about the section or the loft is rebuilt -- they were verified at 20 stations on
two built meshes and the TE sweep closes on 15.763 deg against the source's
documented 15.8, a number that was never an input.

WHAT IS DIFFERENT FROM M6C1: there is no interior to fill. A hyperbolic extrusion
grows OUTWARD from this surface, and outward-marching normals DIVERGE, which is the
stable direction -- measured on M6C1's annulus at 60.83 deg with ZERO severe faces
in the wing region, against every interior fill which failed.

Writes PLOT3D (formatted, multiblock), which is what pyHyp reads.
"""
import sys, numpy as np, pathlib
sys.path.insert(0, "/home/ubuntu/Certonomous/verification/runs/M6C1_runs/geometry")
import m6_section as M
from build_ohgrid import section_loop

def wing_surface(ni, nkw, nb, ncap=0, R_cap=0.0201):
    """(nkw+ncap+1, ni+1, 3): spanwise x around-the-section, i CLOSED.

    THE TIP CAP. AR-138 section 2.1.13 specifies "truncation parallel to wing root
    AND addition of a half body of revolution" -- so a faired cap IS the source
    geometry, not a departure. (M6CP1 section 3 recorded the opposite and that has
    been withdrawn.) The wording is ambiguous about the AXIS of revolution, so the
    cap is built as an ELLIPSOIDAL closure over an overhang measured from the
    reference implementation: A3's surface fairs 0.0201 m beyond the truncation.
    Chord and thickness both scale by sqrt(1-(d/R)^2), closing to a degenerate point
    -- the construction A3 also uses and which pyHyp is known to digest, and which
    this lane's own structured writer could NOT (9 failed checks, 566 cells at
    openness 1). Whether pyHyp's volume clears our gates is the open question.
    """
    loop = section_loop(ni, nb)
    nk = nkw + ncap
    S = np.zeros((nk+1, ni+1, 3))
    for k in range(nkw+1):
        p = M.loft(loop, k/nkw)
        S[k, :ni] = p; S[k, ni] = p[0]
    if ncap:
        tip = M.loft(loop, 1.0)
        cx, cz = tip[:,0].mean(), tip[:,2].mean()
        for j in range(1, ncap+1):
            d = R_cap*j/ncap
            s = np.sqrt(max(0.0, 1.0 - (d/R_cap)**2))
            q = tip.copy()
            q[:,0] = cx + (tip[:,0]-cx)*s
            q[:,2] = cz + (tip[:,2]-cz)*s
            q[:,1] = M.SEMISPAN + d
            S[nkw+j, :ni] = q; S[nkw+j, ni] = q[0]
    return S, loop

def write_plot3d(path, blocks):
    with open(path, "w") as f:
        f.write(f"{len(blocks)}\n")
        for B in blocks:
            f.write(f"{B.shape[1]} {B.shape[0]} 1\n")
        # ONE VALUE PER LINE. The reference writer (cgns_utils cgns2plot3d) emits one
        # per line and cgns_utils' Fortran reader hit "End of file" on a six-per-line
        # file that had exactly the right VALUE COUNT -- so the reader is doing a
        # formatted read, not list-directed. Matching the writer the toolchain itself
        # produces is the safe move; guessing a format is how the first two attempts
        # were spent.
        for B in blocks:
            for c in range(3):
                v = B[:, :, c].T.ravel(order="F")
                f.write("".join(f" {x:.15g}\n" for x in v))

if __name__ == "__main__":
    ni, nkw, nb = (int(x) for x in sys.argv[1:4])
    out = pathlib.Path(sys.argv[4])
    ncap = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    S, loop = wing_surface(ni, nkw, nb, ncap)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_plot3d(out, [S])
    n_surf = (ni - nb)//2
    print(f"  wing surface: {S.shape[1]-1} around x {S.shape[0]-1} spanwise = "
          f"{(S.shape[1]-1)*(S.shape[0]-1)} quads -> {out}")
    # ---- VERIFY ON THE WRITTEN SURFACE, not on the generator's intent
    print(f'  cap stations: {ncap}   total spanwise nodes {S.shape[0]}   tip closes at y={S[:,:,1].max():.6f} m')
    ks = np.unique(np.clip((np.linspace(0.05,0.95,20)*nkw).astype(int), 0, nkw))
    cnt=[]; tc=[]
    for k in ks:
        line = S[k,:ni]
        xm = line[:,0].max()
        at = np.where(np.isclose(line[:,0], xm, rtol=0, atol=1e-12))[0]
        cnt.append(len(at)-1)
        c = M.C_ROOT + (M.C_TIP-M.C_ROOT)*(k/nkw)
        tc.append((line[at,2].max()-line[at,2].min())/c)
    cnt=np.array(cnt); tc=np.array(tc)
    print(f"  cells across the blunt base: min {cnt.min()} max {cnt.max()} over {len(ks)} stations "
          f"(floor 8) -> {'PASS' if cnt.min()>=8 else 'FAIL'}")
    print(f"  t_TE/c at every station: {tc.min():.7e} .. {tc.max():.7e}   source 1.4104e-03")
    root, tip = S[0,:ni], S[nkw,:ni]
    import math
    te = math.degrees(math.atan((tip[:,0].max()-root[:,0].max())/M.SEMISPAN))
    le = math.degrees(math.atan((tip[:,0].min()-root[:,0].min())/M.SEMISPAN))
    print(f"  LE sweep {le:.5f} deg (registered 30.0)   TE sweep {te:.5f} deg "
          f"(source documents 15.8, NOT an input)")
    print(f"  closed in i: {np.allclose(S[:,0], S[:,ni])}   semispan {S[:,:,1].max():.6f} m")
