#!/usr/bin/env python3
"""CROWN IN-PLANE QUALITY -- a PREDICTIVE diagnostic on the SURFACE, before any volume
exists. It grades nothing and gates nothing.

🔴 THIS FILE REPLACES A WRONG-METRIC VERSION OF ITSELF, AND THE REASON IS THE POINT.
Its first version gated the crown on |interior angle - 90| and read 82.515 / 84.828 /
86.920 deg across L1/L2/L3 -- monotonically worsening, the exact signature that killed
topology 1 -- and would have reported route (c) as failing under refinement.

IT IS THE WRONG QUANTITY. `build_capped_multipatch.of_nonortho` (lines 141-152) records
that this lane already made and caught that error: the reading is a 180 deg TANGENT
JUNCTION where two arcs of ONE SMOOTH LOOP meet, which is not a corner at all and
produces no non-orthogonal face, because the grid lines leave it smoothly. That the
angle marches toward 180 deg under refinement is the junction converging to the
tangency it always had -- CORRECT behaviour read as a defect.

`MESH_STANDARD` section 3 gates OpenFOAM non-orthogonality at 70 deg. So that is what is
measured here, with the builder's own operator rather than a second implementation of it.
The interior angle is still printed, labelled DIAGNOSTIC, never compared to a threshold.

PLANTED CONTROL, CALIBRATED AND NOT MERELY LIVE. A shear of s makes the cell edges
(1,0) and (s,1), so the in-plane non-orthogonality is EXACTLY degrees(arctan(s)) -- for
s = 0.9, 41.98721249581666 deg. The control asserts THAT VALUE, not a direction of travel.
A "bent > clean + 1 deg" control is passed by a reader returning HALF the truth, which
would then certify a 140 deg cell as 70 -- and this script does print a pass/fail line
against the 70 deg threshold, so liveness alone is not enough. The expected value is
DERIVED here, never hardcoded.
"""
import sys, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, "/home/ubuntu/Certonomous/verification/runs/M6C1_runs/geometry")
from compare_body_mp import CB
import build_capped_multipatch as BC

# --- planted control: CALIBRATED against the analytic value, not just liveness ---
S_SHEAR = 0.9
EXPECT = float(np.degrees(np.arctan(S_SHEAR)))       # derived, not hardcoded
TOL = 1e-6
g = np.stack(np.meshgrid(np.linspace(0, 1, 9), np.linspace(0, 1, 9), indexing="ij"), -1)
clean = BC.inplane_quality(g)[0]
sh = g.copy(); sh[:, :, 0] += S_SHEAR * sh[:, :, 1]
bent = BC.inplane_quality(sh)[0]
print(f"PLANT: clean grid {clean:.6f} deg (expect 0); sheared grid {bent:.6f} deg "
      f"(expect exactly arctan({S_SHEAR}) = {EXPECT:.6f})")
if abs(clean) > TOL:
    print(f"REFUSED (2): an orthogonal grid read {clean:.6e} deg, not 0.")
    sys.exit(2)
if abs(bent - EXPECT) > TOL:
    print(f"REFUSED (2): sheared grid read {bent:.6f} deg against an analytic "
          f"{EXPECT:.6f} deg. A reader off by a factor would pass a direction-only control "
          f"and then misreport the crown against the 70 deg threshold.")
    sys.exit(2)

print("\nCROWN PATCH, identified by PLANARITY and never by block order, in its own plane.")
print("GATE: OpenFOAM non-orthogonality <= 70 deg, inherited from MESH_STANDARD section 3.")
print(f"{'level':10s} {'ni x nj':>11s} {'max nonOrtho':>13s} {'faces>70':>9s} "
      f"{'|ang-90| DIAG':>14s} {'areaRatio':>10s} {'folded':>7s}")
PLANAR_TOL = 1e-9

def crown_of(path):
    """IDENTIFY the crown by MEASUREMENT, not by block order, and verify its planarity in
    the SAME step. `blocks[-1]` is an assumption about ordering: if it ever changes, the
    old code silently reported a different patch under the crown's name. And projecting to
    (x, z) is only valid if y really is constant -- otherwise every angle below is
    silently distorted. The crown is the UNIQUE block planar in y; both facts are asserted."""
    B = CB.read_plot3d(path)
    spreads = [float(b[:, :, 1].max() - b[:, :, 1].min()) for b in B]
    planar = [i for i, s in enumerate(spreads) if s < PLANAR_TOL]
    if len(planar) != 1:
        print(f"REFUSED (3): expected exactly ONE block planar in y; found {len(planar)} "
              f"({planar}). y-spreads: {[f'{s:.3e}' for s in spreads]}")
        sys.exit(3)
    i = planar[0]
    print(f"  crown identified as block {i} of {len(B)} by planarity, "
          f"y-spread {spreads[i]:.3e} m (next smallest {sorted(spreads)[1]:.3e} m)")
    return B[i]

rows = []
for f in sys.argv[1:]:
    C = crown_of(f)
    P = C[:, :, [0, 2]]                      # valid ONLY because planarity was just proven
    no, n70, ang, ar, fold = BC.inplane_quality(P)
    rows.append((pathlib.Path(f).stem, no, n70, fold))
    print(f"{pathlib.Path(f).stem:10s} {C.shape[0]:4d} x{C.shape[1]:4d} {no:13.3f} {n70:9d} "
          f"{ang:14.3f} {ar:10.2f} {fold:7d}")

print("\nTREND under refinement, on the GATED quantity:")
for i in range(len(rows) - 1):
    d = rows[i + 1][1] - rows[i][1]
    print(f"  {rows[i][0]} -> {rows[i+1][0]}:  max nonOrtho {rows[i][1]:.3f} -> {rows[i+1][1]:.3f} deg "
          f"({'WORSENS' if d > 1e-9 else 'improves/flat'} by {abs(d):.3f})")
worst = max(r[1] for r in rows); tot70 = sum(r[2] for r in rows); fold = sum(r[3] for r in rows)
print(f"\nworst over all levels: {worst:.3f} deg; faces over 70 across all levels: {tot70}; folded cells: {fold}")
print("SURFACE-PLANE SCREEN CLEARS 70" if worst <= 70 and fold == 0 else "SURFACE-PLANE SCREEN DOES NOT CLEAR 70")
print("This is the SURFACE only. It does not pre-empt checkMesh on the volume.")
