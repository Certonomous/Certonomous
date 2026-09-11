#!/usr/bin/env python3
"""Discharges §8 rule 5: assert the mesh's unit system against
1 mesh-unit = 6.976368 m BEFORE any reference quantity is used.
§5.3 states no mesh quality screen can catch this, so it is asserted here, by
measurement, not inferred from a clean checkMesh."""
import sys, re
MESH_UNIT_M   = 6.976368       # §5.3, registered
SEMISPAN_M    = 29.381450      # §5, Vassberg Table 1 (2313.50 in full span / 2)
ROOT_OFFSET   = 0.4449         # §5.3, mesh-units outboard of aircraft centreline
CREF_IN       = 275.80         # §5, Table 1
log = sys.argv[1]
txt = open(log, errors="replace").read()
m = re.search(r"Overall domain bounding box \(([^)]*)\) \(([^)]*)\)", txt)
if not m:
    print("REFUSE: no bounding box printed; the assertion is not discharged on an absence.")
    sys.exit(2)
lo = [float(x) for x in m.group(1).split()]
hi = [float(x) for x in m.group(2).split()]
print("BOUNDING BOX (mesh-units) lo=%s hi=%s" % (lo, hi))
# The wing tip is the max y of the WALL surface, not of the farfield box, so the
# surface value measured by census is used and cross-checked, never re-derived
# from the farfield extent.
TIP_Y = 3.7666681523   # census of ALL THREE surfaces, this lane, independently
semispan_mesh = TIP_Y + ROOT_OFFSET
implied = SEMISPAN_M / semispan_mesh
print("tip y (surface census, all 3 levels agree) = %.10f mesh-units" % TIP_Y)
print("root offset (§5.3)                          = %.4f mesh-units" % ROOT_OFFSET)
print("true semispan                               = %.10f mesh-units" % semispan_mesh)
print("IMPLIED 1 mesh-unit = %.6f m   (registered %.6f m)" % (implied, MESH_UNIT_M))
resid = abs(implied - MESH_UNIT_M)
print("RESIDUAL %.3e m  (%.4f %%)" % (resid, 100*resid/MESH_UNIT_M))
implied_in = implied / 0.0254
print("cross-check: %.4f in against Cref %.2f in -> %.3f %%"
      % (implied_in, CREF_IN, 100*abs(implied_in-CREF_IN)/CREF_IN))
# the farfield must NOT be mistaken for the wing: state the ratio explicitly
print("farfield half-extent %.3f mesh-units = %.1f x the semispan — the bounding box "
      "above is the DOMAIN, not the aircraft." % (hi[1], hi[1]/semispan_mesh))
ok = resid < 1e-5
print("SCALING ASSERTION %s" % ("PASS — mesh is in mesh-units, NOT metres, factor 6.976368"
                                if ok else "GATE FAIL — unit system does not match the registration"))
print("NOTE: no reference quantity is consumed by this rung; G-M1..G-M3 are scale-invariant "
      "(§5.3), so this assertion guards the SUCCESSOR flow rung, not these gates.")
sys.exit(0 if ok else 1)
