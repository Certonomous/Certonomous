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
X_OUTLET = -1500.0        # 6D downstream of the propeller plane
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


def shaft_extension(n_ax: int = 160, n_th: int = 120) -> np.ndarray:
    """Closed cylinder r = R_SHAFT from the CAD's termination to the outlet, with an end cap.

    Generated, not CAD.  Registered as a flow boundary and EXCLUDED from both graded
    integrations (amendment 2): it is our domain's artefact, not part of the physical model
    the dynamometer measured.
    """
    xs = np.linspace(X_CAD_END, X_OUTLET, n_ax + 1)
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
        tris.append([(X_OUTLET, 0.0, 0.0),
                     (X_OUTLET, R_SHAFT * math.cos(t1), R_SHAFT * math.sin(t1)),
                     (X_OUTLET, R_SHAFT * math.cos(t0), R_SHAFT * math.sin(t0))])
    return np.asarray(tris, dtype=float)


def write_multi_solid(path: str, groups: dict) -> None:
    with open(path, 'w') as fh:
        for name in PATCHES:
            t = groups.get(name)
            if t is None or len(t) == 0:
                continue
            fh.write(f'solid {name}\n')
            v0, v1, v2 = t[:, 0], t[:, 1], t[:, 2]
            n = np.cross(v1 - v0, v2 - v0)
            ln = np.linalg.norm(n, axis=1)
            ln[ln == 0] = 1.0
            n = n / ln[:, None]
            for k in range(len(t)):
                fh.write(f'  facet normal {n[k,0]:.7e} {n[k,1]:.7e} {n[k,2]:.7e}\n')
                fh.write('    outer loop\n')
                for p in t[k]:
                    fh.write(f'      vertex {p[0]:.7e} {p[1]:.7e} {p[2]:.7e}\n')
                fh.write('    endloop\n  endfacet\n')
            fh.write(f'endsolid {name}\n')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='src', required=True, help='tessellated admitted CAD (STL)')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    tris = read_stl(a.src)
    lab = classify(tris)
    groups = {p: tris[lab == p] for p in PATCHES[:4]}
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

    write_multi_solid(a.out, groups)
    print(f'\nwrote {a.out}  ({os.path.getsize(a.out)/1e6:.1f} MB)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
