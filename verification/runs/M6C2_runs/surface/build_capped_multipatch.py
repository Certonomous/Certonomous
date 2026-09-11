#!/usr/bin/env python3
"""M6C2 MULTI-PATCH CAPPED WING SURFACE -- the unblock condition of M6C1 Addendum 1
section A1.2, built on THIS LAB'S OWN AR-138-faithful body instead of borrowed.

WHY MULTI-PATCH, AND WHY THE PREVIOUS TWO CAPS FAILED
-----------------------------------------------------
M6C1 Addendum 1 records three exhausted topologies. Two of them died on the SAME
defect in two costumes: a closed section loop cannot be capped by a single
structured patch without a DEGENERACY.
  * `build_surface.py`'s ellipsoidal cap scales the loop to a POINT. The apex row is
    then ni coincident points -- zero-length edges -- and pyHyp segfaults (rc = 139)
    after printing "Normals are consistent" and "Topology complete" (A1.4).
  * M6C1's structured interior fill puts a FALSE CORNER where the geometry has none:
    66.57 deg at L1, 70.99 deg at L2 against a gate of 70, WORSENING under refinement.

A3's `m6_surfaceMesh_fine.cgns` shows the construction that has neither. Its 9 zones
were read out of the file by this lane (not taken on report) and the layout is:

    4 arcs of the section loop, each its own patch          (nose / upper / base / lower)
  + the same 4 arcs swept outward through a short COLLAR    (the tip fairing)
  + ONE flat H-patch closing the shrunken loop              (the crown)
  = 9 patches, no collapsed point, no interior fill of a full-size section.

THE CROWN IS THE WHOLE TRICK. It is an H-map of a SHRUNKEN section whose four sides
are all real curves of non-zero length: the nose arc (NOT the leading-edge point),
the blunt base, and the two surfaces. The leading edge never becomes a patch corner
by itself, so the degenerate corner that killed both earlier caps cannot form.

THE BODY IS OURS, NOT A3's. This lane measured A3's trailing edge directly from its
own zone 6 -- the patch Addendum 3's measurement never opened -- and A3 holds
t_TE ABSOLUTELY constant at 0.0011366 m, so t_TE/c runs 1.419e-03 at the root to
2.483e-03 at the tip, a spread of 54.8 %. AR-138 section 2.1.11 specifies CONICAL
generation, which requires t_TE/c constant. Our loft is conical and t_TE/c is
1.4104000e-03 at every station. Only A3's CAP TOPOLOGY is reused; none of its
geometry is.

THE CAP DIMENSIONS ARE A REGISTERED DEPARTURE AND ARE STATED AS ONE
-------------------------------------------------------------------
AR-138 section 2.1.13 specifies the tip as "truncation parallel to wing root and
addition of a half body of revolution" -- verified by this lane by rendering PDF
page 328 of `docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf`
and reading the line. So a faired cap IS the source geometry. But the lab's copy is a
1979 scan whose numeric tables carry no OCR layer, and figure B1-1 -- which would
carry the fairing's dimensions -- is a page image. **The fairing's SIZE is therefore
not readable from the source in this repository.** It is taken from the A3 reference
implementation, MEASURED by this lane from its zone corners:

    truncation plane   z = 1.170027 m      crown plane   z = 1.196300 m
    overhang H        = 0.026273 m
    chord   0.457838 -> 0.450134 m         shrink s_end  = 0.983175
    half-thickness 0.006243 -> 0.006138    shrink        = 0.983181   (agrees)

and s(d) = sqrt(1 - (d/R)^2) with R = H / sqrt(1 - s_end^2) = 0.143795 m, which gives
s(0) = 1 exactly, so the fairing leaves the wing surface TANGENTIALLY and the join at
the truncation is smooth. **H, s_end and R are PHYSICAL CONSTANTS, identical at all
three levels**, so the body does not change under refinement -- the failure mode
dafoam measured on its own artefacts and which `compare_body.py` exists to catch.

The semispan is UNCHANGED at 1.1963 m: the wing is truncated at 1.1963 - H and the
fairing carries it back out to 1.1963. The cap is not an extension of the wing.

THE FAMILY IS EXACT, AND THAT IS NOT AN ACCIDENT
-------------------------------------------------
n_nose = n_base / 2 is FORCED, not chosen: the crown's nose edge and its base edge
are opposite sides of one structured patch and must carry the same point count.
    nose arc points = 2*n_nose + 1 == n_base + 1  <=>  n_nose = n_base/2
The happy consequence is that n_nose / n_surf is then IDENTICAL at all three levels
(8/92 = 12/138 = 18/207 = 0.0869565), so the patch split sits at the same physical
place on every mesh. A split that drifted with refinement would change the mesh
topology between levels and break the Roache triple's premise.
"""
import sys, pathlib, numpy as np

sys.path.insert(0, "/home/ubuntu/Certonomous/verification/runs/M6C1_runs/geometry")
import m6_section as M
from build_ohgrid import section_loop
from elliptic import winslow, ttm_sources

# --- cap constants, measured from A3's zone corners. PHYSICAL, level-independent. ---
H_CAP   = 0.026273          # m, truncation plane to crown plane
S_END   = 0.983175          # loop shrink at the crown
R_CAP   = H_CAP / np.sqrt(1.0 - S_END**2)      # 0.143795 m


def arc_indices(ni, n_base, n_nose):
    """The four arcs of the closed loop, as index lists into loop[0..ni-1].

    loop layout, from build_ohgrid.section_loop:
        i = 0            leading edge
        i = 0 .. n_surf-1        upper surface, LE -> just before the TE corner
        i = n_surf               UPPER TE CORNER (base[0])
        i = n_surf .. n_surf+n_base     the blunt base, upper corner -> lower corner
        i = n_surf+n_base        LOWER TE CORNER
        i = n_surf+n_base .. ni-1       lower surface, TE -> just before the LE
        i wraps to 0
    """
    n_surf = (ni - n_base) // 2
    assert 2 * n_nose == n_base, f"n_nose must be n_base/2: {n_nose} vs {n_base}"
    w = lambda a, b: [k % ni for k in range(a, b + 1)]
    UP   = w(n_nose,            n_surf)                 # nose end -> upper TE corner
    BASE = w(n_surf,            n_surf + n_base)        # upper TE corner -> lower
    LO   = w(n_surf + n_base,   ni - n_nose)            # lower TE corner -> nose start
    NOSE = w(ni - n_nose,       ni + n_nose)            # lower nose -> LE -> upper nose
    nc, nt = n_surf - n_nose, n_base
    assert len(UP) == len(LO) == nc + 1, (len(UP), len(LO), nc + 1)
    assert len(BASE) == len(NOSE) == nt + 1, (len(BASE), len(NOSE), nt + 1)
    # the four corners must be shared, point for point, or the patches will not close
    assert UP[0] == NOSE[-1] and UP[-1] == BASE[0]
    assert LO[0] == BASE[-1] and LO[-1] == NOSE[0]
    return UP, BASE, LO, NOSE, nc, nt


def shrunk(loop, s):
    """Similarity shrink of the 2-D normalised loop about its own centroid.

    A SIMILARITY, deliberately: x and z scale by the same factor, so the section
    SHAPE is untouched and t_TE/c is preserved EXACTLY through the fairing. A
    non-uniform shrink would thin the trailing edge relative to the chord and would
    reintroduce, inside the cap, the very defect this whole rung exists to avoid.
    """
    ctr = loop.mean(axis=0)
    return ctr + s * (loop - ctr)


def coons(eU, eL, eN, eB):
    """Transfinite (Coons) interpolation from four consistently-oriented edges.

    eU, eL : (nc+1, 2) nose -> TE, upper and lower
    eN, eB : (nt+1, 2) lower -> upper, at the nose and at the base
    """
    nc, nt = len(eU) - 1, len(eN) - 1
    u = np.linspace(0, 1, nc + 1)[:, None, None]
    v = np.linspace(0, 1, nt + 1)[None, :, None]
    Su = eL[:, None, :] * (1 - v) + eU[:, None, :] * v
    Sv = eN[None, :, :] * (1 - u) + eB[None, :, :] * u
    C = (eL[0][None, None, :] * (1 - u) * (1 - v) + eU[0][None, None, :] * (1 - u) * v
         + eL[-1][None, None, :] * u * (1 - v) + eU[-1][None, None, :] * u * v)
    return Su + Sv - C


def of_nonortho(P2):
    """OpenFOAM's NON-ORTHOGONALITY, computed in plane: for every internal edge
    between two adjacent quads, the angle between the edge normal and the line
    joining the two cell centroids.

    IT IS THIS QUANTITY, AND NOT THE QUAD'S INTERIOR ANGLE, THAT `MESH_STANDARD`
    section 3 GATES AT 70 deg. This lane first gated the crown on
    |interior angle - 90| and refused a fill that measures 52.35 deg on the quantity
    actually gated -- an 82.5 deg reading that is a 180 deg TANGENT JUNCTION on the
    boundary, where two arcs of one smooth loop meet, and which produces no
    non-orthogonal face at all because the grid lines leave it smoothly. The wrong
    metric against the right threshold is a refusal that looks rigorous and is not.
    The interior-angle figure is still reported, as a DIAGNOSTIC, never as a gate.
    """
    ctr = 0.25 * (P2[:-1, :-1] + P2[1:, :-1] + P2[1:, 1:] + P2[:-1, 1:])
    out = []
    for e, d in ((P2[1:-1, 1:, :] - P2[1:-1, :-1, :], ctr[1:, :, :] - ctr[:-1, :, :]),
                 (P2[1:, 1:-1, :] - P2[:-1, 1:-1, :], ctr[:, 1:, :] - ctr[:, :-1, :])):
        n = np.stack([e[..., 1], -e[..., 0]], -1)
        n = n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-300)
        d = d / (np.linalg.norm(d, axis=-1, keepdims=True) + 1e-300)
        out.append(np.degrees(np.arccos(np.clip(np.abs((n * d).sum(-1)), 0, 1))))
    return out


def inplane_quality(X):
    """(max OpenFOAM non-orthogonality deg, faces over 70, max |interior angle - 90|
    deg [DIAGNOSTIC], max area ratio, folded-cell count)."""
    P = X[:, :, :2] if X.shape[-1] > 2 else X
    a, b, c, d = P[:-1, :-1], P[1:, :-1], P[1:, 1:], P[:-1, 1:]
    cr = lambda p, q: p[..., 0] * q[..., 1] - p[..., 1] * q[..., 0]
    area = 0.5 * (cr(b - a, c - a) + cr(c - a, d - a))
    worst = 0.0
    for (p, q, r) in ((d, a, b), (a, b, c), (b, c, d), (c, d, a)):
        u, v = q - p, r - q
        cs = (u * v).sum(-1) / (np.linalg.norm(u, axis=-1) * np.linalg.norm(v, axis=-1) + 1e-300)
        worst = max(worst, float(np.abs(np.degrees(np.arccos(np.clip(cs, -1, 1))) - 90.0).max()))
    no = of_nonortho(P)
    return (max(float(x.max()) for x in no), sum(int((x > 70).sum()) for x in no),
            worst, float(abs(area).max() / (abs(area).min() + 1e-300)), int((area <= 0).sum()))


def build(ni, nkw, n_base, ncap, sweeps=400):
    """Returns (patches, names, diagnostics). Axes: x chord, y SPAN, z thickness."""
    n_nose = n_base // 2
    loop = section_loop(ni, n_base)
    UP, BASE, LO, NOSE, nc, nt = arc_indices(ni, n_base, n_nose)
    eta_trunc = (M.SEMISPAN - H_CAP) / M.SEMISPAN

    def station(eta, s):
        """The 3-D section at spanwise fraction eta, shrunk by s. Conical loft."""
        return M.loft(shrunk(loop, s), eta)

    # ---- 1-4: the wing, four arcs, root to the truncation plane
    etas = eta_trunc * np.linspace(0.0, 1.0, nkw + 1)
    Wsec = [station(e, 1.0) for e in etas]
    W = {n: np.array([S[idx] for S in Wsec]) for n, idx in
         (("wing_upper", UP), ("wing_base", BASE), ("wing_lower", LO), ("wing_nose", NOSE))}

    # ---- 5-8: the collar, truncation plane to the crown plane
    ds = H_CAP * np.linspace(0.0, 1.0, ncap + 1)
    ss = np.sqrt(np.clip(1.0 - (ds / R_CAP) ** 2, 0.0, None))
    Csec = [station((M.SEMISPAN - H_CAP + d) / M.SEMISPAN, s) for d, s in zip(ds, ss)]
    C = {n: np.array([S[idx] for S in Csec]) for n, idx in
         (("cap_upper", UP), ("cap_base", BASE), ("cap_lower", LO), ("cap_nose", NOSE))}

    # ---- 9: the crown, an H-fill of the shrunken loop, all four sides real curves
    T = Csec[-1]                                    # the crown loop, in 3-D
    y_crown = T[:, 1].mean()
    xz = lambda idx: T[idx][:, [0, 2]]
    X0 = coons(xz(UP), xz(LO)[::-1], xz(NOSE), xz(BASE)[::-1])
    P, Q = ttm_sources(X0)
    Xs = winslow(X0, sweeps=sweeps, omega=0.6, P=P, Q=Q)
    # the boundary is held fixed by winslow(); assert it rather than trust it
    for e, got in (("nose", Xs[0]), ("base", Xs[-1])):
        pass
    assert np.allclose(Xs[0], X0[0]) and np.allclose(Xs[-1], X0[-1])
    assert np.allclose(Xs[:, 0], X0[:, 0]) and np.allclose(Xs[:, -1], X0[:, -1])
    crown = np.empty(Xs.shape[:2] + (3,))
    crown[:, :, 0] = Xs[:, :, 0]; crown[:, :, 1] = y_crown; crown[:, :, 2] = Xs[:, :, 1]

    names = ["wing_upper", "wing_base", "wing_lower", "wing_nose",
             "cap_upper", "cap_base", "cap_lower", "cap_nose", "crown"]
    patches = [W["wing_upper"], W["wing_base"], W["wing_lower"], W["wing_nose"],
               C["cap_upper"], C["cap_base"], C["cap_lower"], C["cap_nose"], crown]
    diag = dict(nc=nc, nt=nt, n_nose=n_nose, eta_trunc=eta_trunc,
                crown_raw=inplane_quality(X0), crown_smooth=inplane_quality(Xs),
                y_crown=y_crown, loop=loop, Wsec=Wsec, Csec=Csec, T=T,
                UP=UP, BASE=BASE, LO=LO, NOSE=NOSE)
    return patches, names, diag


def write_plot3d(path, blocks):
    """Formatted multiblock PLOT3D, ONE VALUE PER LINE -- the format the toolchain's
    own writer emits and its Fortran reader can read back (M6C1 Addendum 1 A1.4)."""
    with open(path, "w") as f:
        f.write(f"{len(blocks)}\n")
        for B in blocks:
            f.write(f"{B.shape[1]} {B.shape[0]} 1\n")
        for B in blocks:
            for c in range(3):
                for x in B[:, :, c].T.ravel(order="F"):
                    f.write(f" {x:.15g}\n")
