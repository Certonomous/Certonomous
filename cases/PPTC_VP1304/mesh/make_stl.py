#!/usr/bin/env python3
"""Build the PPTC VP1304 snappyHexMesh input surfaces from the admitted CAD tessellation.

Produces one multi-solid ASCII STL carrying the FIVE registered patches of
pre-registration amendments 2 and 3:

    blades  hub  cap  shaft          -- the admitted CAD body, split here
    shaftExtension                   -- generated: the CAD terminates at x = -356 mm and
                                        the outlet sits at x = -1500 mm

CLASSIFIER.  The hub, cap and shaft are bodies of revolution about x; the blades are not.
A surface of revolution has a normal with NO circumferential component, so the test is
geometric rather than positional:

    axisymmetric  <=>  |n . e_theta| < AXISYM_TOL      (e_theta at the facet centroid)

Axial position then separates cap from hub from shaft.  Position alone would misclassify the
blade root, where blade and hub surfaces occupy the same radii; the normal test does not.

All lengths here are MILLIMETRES, the CAD's own units (pre-registration 2.3).  The registered
import scale of exactly 1e-3 is applied by OpenFOAM at read time, not here, so the STL stays
in the units its provenance records.
"""
from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from stl_metrics import read_stl                      # noqa: E402

# --- registered geometry, measured in GEOMETRY_ADMISSION_RECORD.md section 3 (mm) --------
X_CAP_START = 25.0        # hub / nose-cap junction, r = 36.2300
X_HUB_AFT = -50.0         # hub / aft-fairing junction
X_CAD_END = -356.0        # the CAD's own aft termination
X_OUTLET = -1500.0        # 6D downstream of the propeller plane -- the DOMAIN boundary
# The extension surface is carried 100 mm PAST the outlet so it cuts that plane cleanly.
# A surface terminating exactly on a boundary plane leaves snappyHexMesh deciding a
# coincident intersection, which is a silent source of leaked or ragged cells.
X_EXT_END = -1600.0
R_SHAFT = 20.0            # measured: r = 20.000 mm exactly -> diameter 0.040 m (amendment 1)
AXISYM_TOL = 0.15
# The bodies of revolution never exceed this radius: hub 37.60, cap base 36.23, fairing 33.25
# (all measured, GEOMETRY_ADMISSION_RECORD.md section 3).  Anything beyond it is blade, whatever
# its normal does -- and the normal test alone DOES fail there, because the narrow strips along
# the blade tip and the leading and trailing edges face radially, and a radial normal has no
# circumferential component either.  Position alone fails at the root; the normal alone fails at
# the edges; together they do not.
R_REVOLUTION_MAX = 45.0

# Report 3752 Table 1: expanded area ratio AE/A0 = 0.77896, D = 250 mm.  The wetted blade area
# must exceed 2 x AE (two sides) by a small margin for edge strips and surface curvature.  This
# is a check of the SPLIT against the report, not against itself.
AE_OVER_A0 = 0.77896
A0_MM2 = math.pi * 250.0 ** 2 / 4.0

PATCHES = ('blades', 'hub', 'cap', 'shaft', 'shaftExtension')


def classify(tris: np.ndarray) -> np.ndarray:
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    n = np.cross(v1 - v0, v2 - v0)
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    n = n / ln[:, None]
    c = tris.mean(axis=1)
    r = np.hypot(c[:, 1], c[:, 2])
    r_safe = np.where(r == 0, 1.0, r)
    # circumferential unit vector at the centroid: e_theta = x_hat cross r_hat
    e_t = np.stack([np.zeros_like(r), -c[:, 2] / r_safe, c[:, 1] / r_safe], axis=1)
    axisym = np.abs(np.einsum('ij,ij->i', n, e_t)) < AXISYM_TOL
    x = c[:, 0]
    rev = axisym & (r <= R_REVOLUTION_MAX)
    out = np.full(len(tris), 'blades', dtype=object)
    out[rev & (x > X_CAP_START)] = 'cap'
    out[rev & (x <= X_CAP_START) & (x >= X_HUB_AFT)] = 'hub'
    out[rev & (x < X_HUB_AFT)] = 'shaft'
    return out


def shaft_extension(n_ax: int = 800, n_th: int = 120) -> np.ndarray:
    """Closed cylinder r = R_SHAFT from the CAD's termination to the outlet, with an end cap.

    Generated, not CAD.  Registered as a flow boundary and EXCLUDED from both graded
    integrations (amendment 2): it is our domain's artefact, not part of the physical model
    the dynamometer measured.

    The default divisions are set by the ADEQUACY GATE and not by eye.  At n_ax = 160 the
    facets were 7.8 x 1.05 mm slivers of equivalent size 3.07 mm, against this patch's finest
    surface cell of 2.22 mm -- tessellation-limited on a surface we generate ourselves, which
    would have been an entirely self-inflicted defect.  n_ax = 800 gives 1.55 x 1.05 mm,
    equivalent size about 1.37 mm, comfortably inside it.
    """
    xs = np.linspace(X_CAD_END, X_EXT_END, n_ax + 1)
    th = np.linspace(0.0, 2.0 * math.pi, n_th + 1)
    tris = []
    for i in range(n_ax):
        for j in range(n_th):
            a, b = xs[i], xs[i + 1]
            t0, t1 = th[j], th[j + 1]
            p00 = (a, R_SHAFT * math.cos(t0), R_SHAFT * math.sin(t0))
            p01 = (a, R_SHAFT * math.cos(t1), R_SHAFT * math.sin(t1))
            p10 = (b, R_SHAFT * math.cos(t0), R_SHAFT * math.sin(t0))
            p11 = (b, R_SHAFT * math.cos(t1), R_SHAFT * math.sin(t1))
            tris.append([p00, p10, p11])
            tris.append([p00, p11, p01])
    # end cap at the outlet so the surface is closed
    for j in range(n_th):
        t0, t1 = th[j], th[j + 1]
        tris.append([(X_EXT_END, 0.0, 0.0),
                     (X_EXT_END, R_SHAFT * math.cos(t1), R_SHAFT * math.sin(t1)),
                     (X_EXT_END, R_SHAFT * math.cos(t0), R_SHAFT * math.sin(t0))])
    return np.asarray(tris, dtype=float)


def write_binary_stl(path: str, tris: np.ndarray, name: str) -> None:
    """One patch, one binary STL.

    Binary STL carries no region names, so a multi-region surface must either be ASCII (which
    at this facet count would exceed a gigabyte per file) or be split into one file per
    region.  Split is also the better shape for snappyHexMesh: each patch becomes its own
    `triSurfaceMesh` entry and carries its own refinement level, which is what
    `MESH_PIPELINE_RECORD.md` correction 1 addendum A registers -- resolution follows the
    geometry, and the blades are not the hub.
    """
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    n = np.cross(v1 - v0, v2 - v0)
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    n = (n / ln[:, None]).astype('<f4')
    rec = np.zeros(len(tris), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    rec['n'] = n
    rec['v'] = tris.astype('<f4')
    with open(path, 'wb') as fh:
        hdr = f'PPTC VP1304 patch {name} -- generated by make_stl.py'.encode()
        fh.write(hdr[:80].ljust(80, b'\0'))
        fh.write(np.uint32(len(tris)).tobytes())
        fh.write(rec.tobytes())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='src', required=True, help='tessellated admitted CAD (STL)')
    ap.add_argument('--outdir', required=True,
                    help='directory to write one binary STL per patch into')
    ap.add_argument('--scale', type=float, default=1e-3,
                    help='registered import scale, mm -> m (pre-registration 2.3). '
                         'Use 1.0 to keep the CAD units.')
    a = ap.parse_args()

    tris = read_stl(a.src)
    lab = classify(tris)
    groups = {p: tris[lab == p] for p in PATCHES[:4]}

    # The CAD is a CLOSED solid, so it carries a disc capping its aft termination at
    # x = X_CAD_END.  Left in place that disc becomes an INTERNAL WALL inside the shaft
    # extension: snappyHexMesh would refine and snap to a surface buried in solid, for nothing,
    # and the union of the patches would not be a single closed body.  It is removed so the CAD
    # body opens into the extension.
    #
    # The removal is VERIFIED, not assumed: the discarded area must equal pi r^2 of the shaft.
    sh = groups['shaft']
    cx = sh.mean(axis=1)[:, 0]
    capm = cx < X_CAD_END + 0.5
    v0, v1, v2 = sh[capm][:, 0], sh[capm][:, 1], sh[capm][:, 2]
    cap_area = float((0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1)).sum())
    want = math.pi * R_SHAFT ** 2
    if abs(cap_area - want) / want > 0.05:
        print(f'*** ABORT: the facets removed at the CAD aft termination total {cap_area:.2f} '
              f'mm2 but the shaft end disc should be {want:.2f} mm2. Something other than the '
              f'end cap is being discarded.')
        return 2
    groups['shaft'] = sh[~capm]
    print(f'  removed the CAD aft end cap: {int(capm.sum())} facets, {cap_area:.2f} mm2 '
          f'against pi r^2 = {want:.2f} mm2 ({100*(cap_area-want)/want:+.2f}%) -- verified, '
          f'so the CAD body opens into the extension and the union is one closed surface')

    groups['shaftExtension'] = shaft_extension()

    print(f'source {a.src}: {len(tris)} triangles')
    print(f"{'patch':>16} {'triangles':>10} {'area mm2':>14} {'x range':>24} {'r max':>9}")
    total = 0.0
    for p in PATCHES:
        t = groups[p]
        v0, v1, v2 = t[:, 0], t[:, 1], t[:, 2]
        ar = float((0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1)).sum())
        pts = t.reshape(-1, 3)
        rr = float(np.hypot(pts[:, 1], pts[:, 2]).max())
        print(f'{p:>16} {len(t):10d} {ar:14.2f} '
              f'{"[%9.2f,%9.2f]" % (pts[:,0].min(), pts[:,0].max()):>24} {rr:9.3f}')
        if p != 'shaftExtension':
            total += ar
    print(f'{"CAD body total":>16} {"":10} {total:14.2f}')

    # check the split against Report 3752 Table 1, not against itself
    t = groups['blades']
    v0, v1, v2 = t[:, 0], t[:, 1], t[:, 2]
    blade_area = float((0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1)).sum())
    ae = AE_OVER_A0 * A0_MM2
    ratio = blade_area / (2.0 * ae)
    print(f'\n  blade wetted area {blade_area:.1f} mm2 against 2 x AE = {2*ae:.1f} mm2 '
          f'(AE/A0 = {AE_OVER_A0}, D = 250 mm, Report 3752 Table 1)')
    print(f'  ratio {ratio:.4f} -- expected slightly above 1 (edge strips and surface '
          f'curvature beyond the expanded projection)')
    if not (1.00 <= ratio <= 1.20):
        print('  *** SPLIT CHECK FAILED: the blade patch does not reproduce the report\'s '
              'expanded area ratio; the classifier is wrong.')
        for pp in ('hub', 'cap', 'shaft'):
            rr = groups[pp].reshape(-1, 3)
            print(f'      {pp} max radius {np.hypot(rr[:,1], rr[:,2]).max():.3f} mm '
                  f'(must not exceed {R_REVOLUTION_MAX})')
        return 2
    print('  SPLIT CHECK PASS')

    if a.scale != 1.0:
        print(f'\n  applying the REGISTERED import scale {a.scale:g} (pre-registration 2.3): '
              f'CAD millimetres -> metres')
        groups = {k: v * a.scale for k, v in groups.items()}
        pts = np.concatenate([v.reshape(-1, 3) for v in groups.values()])
        print(f'  after scaling: max radius {np.hypot(pts[:,1], pts[:,2]).max():.6f} m '
              f'(R = 0.125 m), x in [{pts[:,0].min():.4f}, {pts[:,0].max():.4f}] m')

    os.makedirs(a.outdir, exist_ok=True)
    print()
    for p in PATCHES:
        fp = os.path.join(a.outdir, f'{p}.stl')
        write_binary_stl(fp, groups[p], p)
        print(f'  wrote {fp}  ({os.path.getsize(fp)/1e6:.1f} MB, {len(groups[p])} facets)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
