#!/usr/bin/env python3
"""taylor_maccoll_reference.py -- REGENERATE the EXACT-tier reference for Navier-class
Case-3 (SUP_BOOSTER), the supersonic sharp cone, by numerically integrating the
Taylor-Maccoll ODE.  NO external reference PDF is needed for the EXACT tier: the reference
IS this integration, and it is fully regenerable from M_inf, theta_c and gamma alone.

Physics (Anderson, Modern Compressible Flow, Ch. 10; NACA 1135 conical-flow tables):
  * oblique-shock jump at the (unknown) shock angle beta for freestream M_inf;
  * behind a STRAIGHT conical shock the flow is isentropic along rays, and the radial and
    polar velocity components (nondimensionalised by V_max = sqrt(2 h0)) obey the
    Taylor-Maccoll ODE with V_theta = dV_r/dtheta;
  * shoot on beta until V_theta = 0 is reached exactly at theta = theta_c (the cone
    surface, where the flow is parallel to the wall);
  * surface Mach M_c and surface pressure p_c/p_inf follow from the surface radial
    velocity and the isentropic + oblique-shock relations, hence the surface Cp.

STRONGLY-ATTACHED-SHOCK regime: theta_c is chosen well below the detachment (maximum) cone
angle for M_inf, so a real attached conical shock exists and the shooting converges.

NUMERICAL RIGOR: the integration is repeated at max_step and max_step/4; the reported
beta, M_c and Cp are ACCEPTED only if the two agree to REL_TOL (a numerical
grid-independence check on the ODE solve itself).  Refuses (exit 2) otherwise.

Writes at most one JSON report to the path the caller names.  Sends nothing, commits
nothing (rules 7, 16).  Deterministic: same inputs -> same reference.
"""
import argparse, json, math, sys
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

REL_TOL = 1.0e-5   # ODE grid-independence acceptance (beta, M_c, Cp between two step sizes)

def oblique(Minf, beta, g):
    """Oblique-shock jump at wave angle beta: returns (deflection delta, M2, p2/p1)."""
    Mn1 = Minf*math.sin(beta)
    tand = 2.0/math.tan(beta)*(Mn1**2-1.0)/(Minf**2*(g+math.cos(2*beta))+2.0)
    delta = math.atan(tand)
    Mn2 = math.sqrt((1.0+0.5*(g-1)*Mn1**2)/(g*Mn1**2-0.5*(g-1)))
    M2 = Mn2/math.sin(beta-delta)
    p2_p1 = 1.0+2.0*g/(g+1.0)*(Mn1**2-1.0)
    return delta, M2, p2_p1

def vprime_from_M(M, g):
    """Nondimensional speed V/V_max as a function of Mach number."""
    x = 0.5*(g-1)*M*M
    return math.sqrt(x/(1.0+x))

def tm_rhs(theta, y, g):
    Vr, Vt = y
    A = 0.5*(g-1)*(1.0-Vr*Vr-Vt*Vt)
    dVt = (Vr*Vt*Vt - A*(2.0*Vr+Vt/math.tan(theta)))/(A-Vt*Vt)
    return [Vt, dVt]

def integrate_cone(Minf, beta, g, max_step_deg):
    """Integrate TM inward from theta=beta until V_theta=0; return (theta_c, Vr_c, M2, p2/p1)."""
    delta, M2, p2_p1 = oblique(Minf, beta, g)
    V2 = vprime_from_M(M2, g)
    Vr0 =  V2*math.cos(beta-delta)
    Vt0 = -V2*math.sin(beta-delta)      # negative: flow turns toward the axis as theta decreases
    ev = lambda th, y, gg: y[1]         # V_theta = 0 -> cone surface
    ev.terminal = True; ev.direction = 1
    sol = solve_ivp(tm_rhs, [beta, 1e-4], [Vr0, Vt0], args=(g,), events=ev,
                    rtol=1e-11, atol=1e-13, max_step=math.radians(max_step_deg), dense_output=False)
    if sol.t_events[0].size == 0:
        return None
    return sol.t_events[0][0], sol.y_events[0][0][0], M2, p2_p1

def surface_state(Minf, beta, g, max_step_deg):
    theta_c, Vr_c, M2, p2_p1 = integrate_cone(Minf, beta, g, max_step_deg)
    Mc = math.sqrt(Vr_c**2/(0.5*(g-1)*(1.0-Vr_c**2)))
    fac = g/(g-1)
    pc_p1 = p2_p1*((1+0.5*(g-1)*M2**2)/(1+0.5*(g-1)*Mc**2))**fac
    Cp = (pc_p1-1.0)/(0.5*g*Minf**2)
    return dict(theta_c_deg=math.degrees(theta_c), beta_deg=math.degrees(beta),
                M_cone=Mc, Cp_cone=Cp, pc_over_pinf=pc_p1, M2=M2, p2_over_pinf=p2_p1)

def solve_beta(Minf, theta_c_deg, g, max_step_deg):
    """Shoot on beta so the integrated cone angle equals theta_c."""
    tc = math.radians(theta_c_deg)
    mach_angle = math.asin(1.0/Minf)
    bl, bu = mach_angle+math.radians(0.2), math.radians(70.0)
    f = lambda b: integrate_cone(Minf, b, g, max_step_deg)[0] - tc
    if f(bl)*f(bu) > 0:
        raise SystemExit("no attached-shock beta bracket -- theta_c may exceed detachment for this M_inf")
    return brentq(f, bl, bu, xtol=1e-11, rtol=1e-13)

def regenerate(Minf, theta_c_deg, g):
    coarse_step, fine_step = 0.10, 0.025   # degrees; fine = coarse/4
    b1 = solve_beta(Minf, theta_c_deg, g, coarse_step)
    s1 = surface_state(Minf, b1, g, coarse_step)
    b2 = solve_beta(Minf, theta_c_deg, g, fine_step)
    s2 = surface_state(Minf, b2, g, fine_step)
    checks = {
        "beta_deg":  abs(s1["beta_deg"]-s2["beta_deg"])/abs(s2["beta_deg"]),
        "M_cone":    abs(s1["M_cone"]-s2["M_cone"])/abs(s2["M_cone"]),
        "Cp_cone":   abs(s1["Cp_cone"]-s2["Cp_cone"])/abs(s2["Cp_cone"]),
    }
    converged = all(v < REL_TOL for v in checks.values())
    out = dict(inputs=dict(M_inf=Minf, theta_c_deg=theta_c_deg, gamma=g),
               reference=s2, ode_grid_independence=dict(rel_change=checks,
               rel_tol=REL_TOL, converged=converged, coarse_step_deg=coarse_step,
               fine_step_deg=fine_step),
               note="EXACT-tier reference regenerated by Taylor-Maccoll ODE integration; no external PDF.")
    return out, converged

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--M-inf", type=float, default=2.0)
    ap.add_argument("--theta-c-deg", type=float, default=15.0)
    ap.add_argument("--gamma", type=float, default=1.4)
    ap.add_argument("--out", help="write reference JSON here")
    args = ap.parse_args()
    out, converged = regenerate(args.M_inf, args.theta_c_deg, args.gamma)
    txt = json.dumps(out, indent=2)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(txt+"\n")
    print(txt)
    if not converged:
        sys.stderr.write("REFUSE: TM ODE integration not grid-independent to REL_TOL\n")
        sys.exit(2)

if __name__ == "__main__":
    main()
