#!/usr/bin/env python3
"""Measure the ONERA M6 mean section's TRAILING-EDGE INCLUDED ANGLE from the
registered STL-derived section, and the angle a linear closure could reach.

No mesh is involved.  This is the geometric quantity the TE-study's mechanism
law is stated in.  PLANTED CONTROL (CLAUDE.md rule 3): a synthetic section whose
TE half-angle is known EXACTLY by construction is pushed through the same
estimator and must come back within 0.02 deg, and a scaled copy must return the
scaled angle -- otherwise the estimator is refused and nothing below is believed.
"""
import sys, os
import numpy as np
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/F13_onera_m6")
from m6_section import M6Geometry


def te_half_angle_deg(t2, eps=1e-4):
    """half-angle of the closure at x/c = 1, from the limiting slope."""
    x = 1.0 - eps
    return float(np.degrees(np.arctan(t2(np.array([x]))[0] / eps)))


class Synth:
    """t2(x) = SLOPE*(1-x) exactly -> TE half-angle = atan(SLOPE), by construction."""
    def __init__(self, slope): self.s = slope
    def t2(self, xc): return self.s * (1.0 - np.asarray(xc, float))


if __name__ == "__main__":
    # ---- planted control, BEFORE any measurement below is believed
    for a_true in (4.0, 12.5, 30.0):
        s = Synth(np.tan(np.radians(a_true)))
        got = te_half_angle_deg(s.t2)
        assert abs(got - a_true) < 0.02, f"CONTROL FAILED: {a_true} -> {got}"
    s1 = Synth(np.tan(np.radians(6.0)))
    g2 = te_half_angle_deg(lambda x: 3.0 * s1.t2(x))
    assert abs(g2 - np.degrees(np.arctan(3.0 * np.tan(np.radians(6.0))))) < 0.02, "SCALE CONTROL FAILED"
    print("PLANTED CONTROL PASSED: estimator recovers a known TE half-angle to <0.02 deg,")
    print("                        and recovers the scaled angle of a scaled section.")

    g = M6Geometry(verbose=False)
    a0 = te_half_angle_deg(g.t2)
    print(f"\nMEASURED M6 mean section: TE half-angle alpha = {a0:.4f} deg")
    print(f"                          TE INCLUDED angle 2*alpha = {2*a0:.4f} deg")
    print(f"                          predicted max non-orth 90 - 2*alpha = {90-2*a0:.4f} deg")
    print(f"  t/c_max = {g.tc_max:.5f} at x/c = {g.tc_max_at:.4f}")

    print("\nTHICKNESS-SCALE DIAL (same topology, section half-thickness x S):")
    print("   S      alpha(S) deg   2*alpha deg   predicted 90-2alpha")
    for S in (1.0, 2.0, 2.35, 3.0, 4.0, 6.0, 8.0):
        a = np.degrees(np.arctan(S * np.tan(np.radians(a0))))
        print(f"  {S:4.2f}    {a:9.4f}     {2*a:9.4f}     {90-2*a:9.4f}")
    # S that puts 2*alpha at exactly 20 deg (i.e. predicted non-orth = 70)
    Sstar = np.tan(np.radians(10.0)) / np.tan(np.radians(a0))
    print(f"\n  S* for 2*alpha = 20.0000 deg (predicted 70.0000): S* = {Sstar:.4f}")

    print("\nCAN A **SHARP** LINEAR CLOSURE REACH 2*alpha = 20 deg?")
    print("  A section truncated at x_t and closed straight to (1,0) has")
    print("  tan(alpha) = t2(x_t)/(1-x_t).  Sweep x_t over the whole aft half:")
    xt = np.linspace(0.40, 0.999, 600)
    r = g.t2(xt) / (1.0 - xt)
    i = int(np.argmax(r))
    print(f"   max over x_t of t2/(1-x_t) = {r[i]:.6f} at x_t = {xt[i]:.4f}"
          f"  -> alpha_max = {np.degrees(np.arctan(r[i])):.4f} deg,"
          f" 2*alpha_max = {2*np.degrees(np.arctan(r[i])):.4f} deg")
    print(f"   required for 70 deg: tan(alpha) >= {np.tan(np.radians(10.0)):.6f}"
          f"  ({np.tan(np.radians(10.0))/r[i]:.2f}x the best available)")
    for x in (0.90, 0.95, 0.98, 0.99):
        print(f"   t2({x:.2f}) = {float(g.t2(np.array([x]))[0]):.6f} c")
