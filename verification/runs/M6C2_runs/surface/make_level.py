#!/usr/bin/env python3
"""Build ONE M6C2 multi-patch capped level, and REFUSE it rather than degrade it.

Every check below is armed: it is shown able to see the defect it hunts, on a
PLANTED copy, before any clean verdict it reports is believed (CLAUDE.md rule 3).
A check that cannot be shown to fail is not a check, and this script exits non-zero
rather than print a reassuring line.

    exit 0  surface built and every check passed
    exit 2  a planted control came back undetected -- the READER is broken
    exit 3  coincident points in the surface (the pyHyp NaN/segfault hazard, A1.4)
    exit 4  the patches do not close on each other point-for-point
    exit 5  a geometry limb failed (cells across the base, t_TE/c, sweep, semispan)
    exit 6  the crown fill is folded or exceeds the in-plane non-orthogonality gate
"""
import sys, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, "/home/ubuntu/Certonomous/verification/runs/M6C1_runs/geometry")
import m6_section as M
import build_capped_multipatch as BC

TOL_COINC   = 1e-12
GATE_NONORTH_2D = 70.0          # the same MESH_STANDARD number the volume is gated on
SRC_TC      = 1.4104e-03        # AR-138 Table B1-1: 2*0.0007052


# --------------------------------------------------------------------------- #
#  ARMED CHECK 1 -- COINCIDENT POINTS. Geometry-agnostic; it knows nothing about
#  wings. It exists because a zero-length edge surfaces as NaN in a pyHyp quality
#  column while pyHyp still prints "Normals are consistent" and "Topology
#  complete" -- BOTH topology checks pass straight over it (M6C1 A1.4). So the
#  check cannot read a log. It scans the arrays and refuses BEFORE the extruder.
# --------------------------------------------------------------------------- #
def coincident(p, tol=TOL_COINC):
    di = np.linalg.norm(np.diff(p, axis=0), axis=2)
    dj = np.linalg.norm(np.diff(p, axis=1), axis=2)
    return int((di < tol).sum() + (dj < tol).sum())

def scan(patches, tol=TOL_COINC):
    return sum(coincident(p, tol) for p in patches)


# --------------------------------------------------------------------------- #
#  ARMED CHECK 2 -- PATCH CLOSURE. Every shared edge must match POINT FOR POINT.
#  pyHyp's autoConnect will silently leave a hairline gap as a free edge and then
#  `unattachedEdgesAreSymmetry` will call that gap a symmetry plane. That is how a
#  capped surface becomes an uncapped one without anybody being told.
# --------------------------------------------------------------------------- #
def edges(P):
    return {"i0": P[0, :, :], "i1": P[-1, :, :], "j0": P[:, 0, :], "j1": P[:, -1, :]}

def closure_defects(patches, tol=1e-10):
    """Count boundary edges that match NO other edge (forward or reversed)."""
    E = []
    for n, P in enumerate(patches):
        for k, e in edges(P).items():
            E.append((n, k, e))
    free = []
    for a, (na, ka, ea) in enumerate(E):
        hit = False
        for b, (nb, kb, eb) in enumerate(E):
            if a == b or na == nb or len(ea) != len(eb):
                continue
            if np.allclose(ea, eb, atol=tol) or np.allclose(ea, eb[::-1], atol=tol):
                hit = True; break
        if not hit:
            free.append((na, ka))
    return free


def geometry_limbs(diag, ni, nkw, n_base, nstat=20):
    """M-b-1 and the conical trailing-edge law, measured ON THE BUILT SURFACE."""
    Wsec = diag["Wsec"]
    ks = np.unique(np.clip((np.linspace(0.05, 0.95, nstat) * nkw).astype(int), 0, nkw))
    cnt, tc = [], []
    for k in ks:
        S = Wsec[k]
        xm = S[:, 0].max()
        at = np.where(np.isclose(S[:, 0], xm, rtol=0, atol=1e-12))[0]
        cnt.append(len(at) - 1)
        c = S[:, 0].max() - S[:, 0].min()
        tc.append((S[at, 2].max() - S[at, 2].min()) / c)
    return np.array(cnt), np.array(tc), ks


def main():
    lvl, ni, nkw, n_base, ncap = sys.argv[1], *[int(x) for x in sys.argv[2:6]]
    out = pathlib.Path(sys.argv[6])
    sweeps = int(sys.argv[7]) if len(sys.argv) > 7 else 400

    print(f"=== {lvl}: ni={ni} nkw={nkw} n_base={n_base} ncap={ncap} sweeps={sweeps} ===")
    patches, names, diag = BC.build(ni, nkw, n_base, ncap, sweeps=sweeps)
    for n, p in zip(names, patches):
        print(f"  patch {n:12s} {p.shape[0]:4d} x {p.shape[1]:4d}")
    print(f"  arcs: nc={diag['nc']} nt={diag['nt']} n_nose={diag['n_nose']}  "
          f"n_nose/n_surf = {diag['n_nose']/((ni-n_base)//2):.7f}")
    print(f"  truncation at eta = {diag['eta_trunc']:.7f}  "
          f"(y = {diag['eta_trunc']*M.SEMISPAN:.6f} m)   crown at y = {diag['y_crown']:.6f} m")

    # ---------------- ARMED CHECK 1 ----------------
    base = scan(patches)
    q = [p.copy() for p in patches]
    q[0][1, 0, :] = q[0][0, 0, :]                     # plant ONE duplicated point
    planted = scan(q)
    print(f"  PLANT (coincident): clean {base} pairs; one duplicate planted -> {planted}")
    if not planted > base:
        print("  REFUSED (2): the coincident-point reader was not shown able to see a duplicate.")
        return 2
    print("    control PASSES -- the reader is shown able to SEE the defect")
    if base > 0:
        print(f"  REFUSED (3): {base} coincident point pairs in the surface.")
        return 3

    # ---------------- ARMED CHECK 2 ----------------
    free = closure_defects(patches)
    q = [p.copy() for p in patches]
    q[8] = q[8] + np.array([0.0, 0.0, 1e-3])          # lift the crown off its collar
    free_planted = closure_defects(q)
    print(f"  PLANT (closure): as built {len(free)} unmatched edges; crown displaced "
          f"1 mm -> {len(free_planted)}")
    if not len(free_planted) > len(free):
        print("  REFUSED (2): the closure reader was not shown able to see a detached crown.")
        return 2
    print("    control PASSES -- the reader is shown able to SEE a detached patch")
    # the ROOT edges of the four wing patches are legitimately free: they are the
    # symmetry plane, and pyHyp is told so by unattachedEdgesAreSymmetry.
    root_free = [(n, k) for (n, k) in free if names[n].startswith("wing") and k == "i0"]
    other = [(names[n], k) for (n, k) in free if (n, k) not in root_free]
    print(f"    free edges: {len(root_free)} at the ROOT (the symmetry plane, expected); "
          f"{len(other)} elsewhere {other if other else ''}")
    if other:
        print(f"  REFUSED (4): {len(other)} unmatched edges that are not the symmetry plane.")
        return 4

    # ---------------- GEOMETRY LIMBS ----------------
    cnt, tc, ks = geometry_limbs(diag, ni, nkw, n_base)
    print(f"  M-b-1 cells across the blunt base: min {cnt.min()} max {cnt.max()} over "
          f"{len(ks)} stations (floor 8) -> {'PASS' if cnt.min() >= 8 else 'FAIL'}")
    print(f"  t_TE/c: {tc.min():.7e} .. {tc.max():.7e}   source {SRC_TC:.4e}   "
          f"spread {(tc.max()-tc.min())/tc.mean()*100:.6f} %")
    T = diag["T"]
    xmT = T[:, 0].max()
    atT = np.where(np.isclose(T[:, 0], xmT, rtol=0, atol=1e-12))[0]
    tc_crown = (T[atT, 2].max() - T[atT, 2].min()) / (T[:, 0].max() - T[:, 0].min())
    print(f"  t_TE/c ON THE CROWN LOOP (the fairing must not thin it): {tc_crown:.7e}")
    root, tip = diag["Wsec"][0], diag["Wsec"][-1]
    import math
    dy = tip[:, 1].mean() - root[:, 1].mean()
    le = math.degrees(math.atan((tip[:, 0].min() - root[:, 0].min()) / dy))
    te = math.degrees(math.atan((tip[:, 0].max() - root[:, 0].max()) / dy))
    semi = max(p[:, :, 1].max() for p in patches)
    print(f"  LE sweep {le:.5f} deg (source 30.0, an INPUT)   TE sweep {te:.5f} deg "
          f"(source documents 15.8, NOT an input)")
    print(f"  semispan reached: {semi:.6f} m (source 1.1963)")
    bad = []
    if cnt.min() < 8: bad.append("cells across the base")
    if abs(tc.mean() - SRC_TC) / SRC_TC > 1e-4 or (tc.max()-tc.min())/tc.mean() > 1e-6:
        bad.append("t_TE/c conical law")
    if abs(tc_crown - SRC_TC) / SRC_TC > 1e-3: bad.append("t_TE/c on the crown")
    if abs(te - 15.8) > 0.1: bad.append("TE sweep")
    if abs(semi - M.SEMISPAN) > 1e-6: bad.append("semispan")
    if bad:
        print(f"  REFUSED (5): geometry limbs failed: {', '.join(bad)}")
        return 5

    # ---------------- THE CROWN'S OWN IN-PLANE QUALITY ----------------
    for lbl, key in (("Coons only", "crown_raw"), ("+ Winslow ", "crown_smooth")):
        no, o70, dev, ar, fold = diag[key]
        print(f"  crown fill, {lbl}: non-orth(OpenFOAM def) {no:7.3f} deg, faces>70 {o70:3d}"
              f" | interior-angle dev {dev:7.3f} deg [DIAGNOSTIC, NOT the gated quantity]"
              f" | area ratio {ar:9.1f} | folded {fold}")
    no, o70, dev, ar, fold = diag["crown_smooth"]
    if fold > 0 or no > GATE_NONORTH_2D:
        print(f"  REFUSED (6): crown fill folded ({fold}) or over the gate "
              f"({no:.3f} > {GATE_NONORTH_2D} on OpenFOAM's own non-orthogonality).")
        return 6
    print(f"    the crown is a SURFACE. The binding gate is `checkMesh "
          f"-allGeometry -allTopology` on the EXTRUDED VOLUME; this in-plane figure "
          f"is the crown's own contribution to it, measured before the extrusion.")

    out.parent.mkdir(parents=True, exist_ok=True)
    BC.write_plot3d(out, patches)
    print(f"  WROTE {out}  ({sum(p.shape[0]*p.shape[1] for p in patches)} surface points, "
          f"{len(patches)} patches)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
