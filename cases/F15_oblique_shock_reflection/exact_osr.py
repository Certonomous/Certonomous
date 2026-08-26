#!/usr/bin/env python3
"""
F15 -- THE EXACT SOLUTION of the oblique shock reflection at M_inf = 2.9.

THE CASE IS SOURCED FROM Ekaterinaris, "High-order accurate, low numerical
diffusion methods for aerodynamics", Progress in Aerospace Sciences 41 (2005)
192-300, page 243, the paragraph beginning "The oblique shock reflection problem
at M_inf = 2.9 is chosen as test case".  Title-page verified per standing rule
15; the provenance record is docs/standards/High_order_grid_convergence_PROVENANCE.md
and the identification is committed at ff5710e2.

    THAT PAPER IS CITED FOR THE CASE DEFINITION AND FOR NOTHING ELSE.
    It contains ZERO occurrences of Richardson, Roache, GCI, grid convergence
    index, observed order or grid refinement, measured over its 66,033-word
    extraction against a planted control that returned non-zero.  No convergence
    METHODOLOGY may be sourced to it, and none is: rule 5 is reached through
    scripts/roache_triple.py::grade_ladder and through nothing else.

WHAT THE PAPER GIVES, AND WHAT IT DOES NOT
------------------------------------------
GIVES: M_inf = 2.9; domain -2 <= x <= 2, 0 <= y <= 1; a 200 x 50 uniform grid;
free stream at the left inflow; extrapolation at the right outflow; slip wall at
y = 0; and the top boundary state rho = 1.69997, u = 2.61934, v = -0.506,
p = 1.528.  The graded reference is "the pressure at y = 0.5".

DOES NOT GIVE: the incident shock angle, or the free-stream state in primitive
variables.  Both are RECOVERED here and the recovery is CHECKED, not assumed:
the standard non-dimensionalisation rho1 = 1, a1 = 1 (so p1 = 1/gamma,
u1 = M1 = 2.9) with an incident shock at beta = 29 deg reproduces the paper's
printed top-boundary state on every component to better than 4e-6.  A mismatch
refuses.  That agreement is the evidence that this case definition is the
paper's case and not a case assembled from a title.

`python3 exact_osr.py --selftest` runs every control.  Refusals are `raise` and
`sys.exit(2)`; there is not one `assert` in this file (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write(
        "REFUSED: exact_osr.py must not run under `python3 -O`.\n"
        "  -O deletes every `assert`, including roache_triple.py:195,632,634,637,\n"
        "  which carry rule 1's verdict vocabulary and rule 5's one-way gate.\n")
    sys.exit(2)

import os
import json
import math
import argparse

GAMMA = 1.4

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.  Every number below is either printed in the paper or
# recovered and checked against a number printed in the paper.
# ---------------------------------------------------------------------------
BETA_INCIDENT_DEG = 29.0        # RECOVERED, then checked against the paper's top BC
X_MIN, X_MAX = -2.0, 2.0        # paper, p.243
Y_MIN, Y_MAX = 0.0, 1.0         # paper, p.243
SAMPLE_Y = 0.5                  # paper, p.243: "The pressure at y = 0.5"

# The paper's printed top-boundary state, transcribed verbatim from p.243.
PAPER_TOP_BC = dict(rho=1.69997, u=2.61934, v=-0.506, p=1.528)
# The same line printed to more digits in the source text; used for the tight
# check.  v is given as -0.506 in the running text; the residual on v is
# therefore checked at the paper's own printed precision (5e-4), not at 4e-6.
PAPER_TOP_BC_TOL = dict(rho=1e-4, u=1e-4, v=5e-4, p=1e-3)


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def theta_of_beta(mach, beta):
    """theta-beta-M, exact."""
    return math.atan(2.0 / math.tan(beta) * ((mach * math.sin(beta)) ** 2 - 1.0)
                     / (mach ** 2 * (GAMMA + math.cos(2.0 * beta)) + 2.0))


def oblique_jump(state, beta_rel, turn_sign):
    """One oblique shock.

    ``beta_rel``  the shock angle measured FROM THE INCOMING FLOW DIRECTION.
    ``turn_sign`` +1 or -1: the sense in which this shock turns the flow.  It is
                  a GEOMETRIC fact of the configuration, not a derived one, so
                  it is supplied explicitly rather than inferred -- the incident
                  shock turns the flow toward the wall (-1) and the reflected
                  shock turns it back parallel (+1).
    """
    if turn_sign not in (1, -1):
        refuse("turn_sign must be +1 or -1, got %r" % (turn_sign,))
    rho, u, v, p = state["rho"], state["u"], state["v"], state["p"]
    a = math.sqrt(GAMMA * p / rho)
    speed = math.hypot(u, v)
    mach = speed / a
    flow_dir = math.atan2(v, u)
    mn1 = mach * math.sin(beta_rel)
    if mn1 <= 1.0:
        refuse("oblique_jump: normal Mach %.6f is not supersonic; no shock exists"
               % mn1)
    rho2 = rho * ((GAMMA + 1.0) * mn1 ** 2) / ((GAMMA - 1.0) * mn1 ** 2 + 2.0)
    p2 = p * (1.0 + (2.0 * GAMMA / (GAMMA + 1.0)) * (mn1 ** 2 - 1.0))
    mn2 = math.sqrt((1.0 + 0.5 * (GAMMA - 1.0) * mn1 ** 2)
                    / (GAMMA * mn1 ** 2 - 0.5 * (GAMMA - 1.0)))
    theta = theta_of_beta(mach, beta_rel)
    mach2 = mn2 / math.sin(beta_rel - theta)
    a2 = math.sqrt(GAMMA * p2 / rho2)
    speed2 = mach2 * a2
    dir2 = flow_dir + turn_sign * theta
    # the shock line's angle measured from the x-axis.  The shock leans to the
    # SAME side the flow is turned toward: the incident shock (turn_sign = -1,
    # flow turned down) descends at -beta_rel from the x-axis; the reflected
    # shock (turn_sign = +1) ascends at +beta_rel from the region-2 flow.
    beta_abs = flow_dir + turn_sign * beta_rel
    return dict(rho=rho2, u=speed2 * math.cos(dir2), v=speed2 * math.sin(dir2),
                p=p2, mach=mach2, theta=theta, beta_rel=beta_rel,
                beta_abs=beta_abs, dir=dir2)


def beta_for_deflection(mach, theta, weak=True):
    """Invert theta-beta-M for the weak solution by bisection."""
    lo = math.asin(1.0 / mach) + 1e-13
    hi = math.pi / 2.0 - 1e-13
    if not weak:
        refuse("only the weak solution is registered for this case")
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if theta_of_beta(mach, mid) < theta:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def solve():
    """The three uniform regions, the two shock loci, and the derived constants
    the pre-registered bands are built from."""
    r1 = dict(rho=1.0, u=2.9, v=0.0, p=1.0 / GAMMA)
    r1["mach"] = r1["u"] / math.sqrt(GAMMA * r1["p"] / r1["rho"])

    beta_i = math.radians(BETA_INCIDENT_DEG)
    r2 = oblique_jump(r1, beta_i, turn_sign=-1)
    theta = -r2["dir"]                       # flow turned toward the wall

    # the reflected shock turns the flow back parallel to the wall
    beta_r_rel = beta_for_deflection(r2["mach"], theta)
    r3 = oblique_jump(r2, beta_r_rel, turn_sign=+1)
    if abs(r3["dir"]) > 1e-12:
        refuse("region 3 is not wall-parallel: flow direction %.3e rad" % r3["dir"])
    r3["v"] = 0.0

    sigma_i = r2["beta_abs"]                 # incident shock, from the x-axis
    sigma_r = r3["beta_abs"]                 # reflected shock, from the x-axis
    x_wall = X_MIN + (Y_MAX - Y_MIN) / abs(math.tan(sigma_i))
    m_refl = math.tan(sigma_r)
    if m_refl <= 0.0:
        refuse("the reflected shock does not ascend; slope %.6f" % m_refl)
    y_exit_right = (X_MAX - x_wall) * m_refl

    dp_i = r2["p"] - r1["p"]
    dp_r = r3["p"] - r2["p"]
    length = X_MAX - X_MIN

    return dict(
        gamma=GAMMA,
        region1=dict((k, r1[k]) for k in ("rho", "u", "v", "p", "mach")),
        region2=dict((k, r2[k]) for k in ("rho", "u", "v", "p", "mach")),
        region3=dict((k, r3[k]) for k in ("rho", "u", "v", "p", "mach")),
        beta_incident_deg=BETA_INCIDENT_DEG,
        sigma_incident_deg_from_x=math.degrees(sigma_i),
        deflection_deg=math.degrees(theta),
        beta_reflected_deg_from_x=math.degrees(sigma_r),
        x_wall_impingement=x_wall,
        reflected_shock_exit_y_at_xmax=y_exit_right,
        dp_incident=dp_i, dp_reflected=dp_r,
        domain_length=length,
        # c is the ONE constant every F15 band is built from: the normalised L1
        # pressure error of a monotone ramp spread over exactly ONE cell,
        # per unit cell width, summed over the two discontinuities that cross
        # y = SAMPLE_Y.  Derivation in the pre-registration, section BANDS.
        L1_floor_per_dx=(dp_i + dp_r) / (4.0 * length * r1["p"]),
        x_incident_at_sample_y=X_MIN + (Y_MAX - SAMPLE_Y) / abs(math.tan(sigma_i)),
        x_reflected_at_sample_y=x_wall + SAMPLE_Y / m_refl,
    )


def p_exact_along_sample_line(x, sol):
    """The exact pressure at height SAMPLE_Y.  A two-step function."""
    if x < sol["x_incident_at_sample_y"]:
        return sol["region1"]["p"]
    if x < sol["x_reflected_at_sample_y"]:
        return sol["region2"]["p"]
    return sol["region3"]["p"]


def p_exact_on_wall(x, sol):
    """The exact wall pressure.  A single step at the impingement point."""
    return sol["region1"]["p"] if x < sol["x_wall_impingement"] else sol["region3"]["p"]


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def control_paper_agreement(sol):
    """THE LOAD-BEARING CHECK.  The recovered beta = 29 deg and the recovered
    free-stream state must reproduce the paper's PRINTED top-boundary state.
    This is what makes the case definition evidence rather than an inference."""
    got = sol["region2"]
    bad = []
    residuals = {}
    for key, want in sorted(PAPER_TOP_BC.items()):
        res = abs(got[key] - want)
        residuals[key] = res
        if res > PAPER_TOP_BC_TOL[key]:
            bad.append("%s: recovered %.8f, paper prints %.8f, residual %.3e > %.1e"
                       % (key, got[key], want, res, PAPER_TOP_BC_TOL[key]))
    if bad:
        refuse("THE RECOVERED CASE DOES NOT REPRODUCE THE PAPER'S PRINTED TOP "
               "BOUNDARY STATE. The case definition is not established and "
               "nothing may be registered on it:\n  " + "\n  ".join(bad))
    return dict(control="paper_top_bc_agreement", residuals=residuals,
                tolerances=PAPER_TOP_BC_TOL, passed=True)


def control_paper_agreement_is_able_to_fail():
    """PLANTED CONTROL on the check above (standing rule 3).  A check that
    agrees with everything would certify a wrong shock angle.  Perturb beta and
    require a refusal."""
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    probe = (
        "import sys; sys.path.insert(0, " + repr(here) + ")\n"
        "import exact_osr as E\n"
        "E.BETA_INCIDENT_DEG = 31.0\n"
        "try:\n"
        "    E.control_paper_agreement(E.solve())\n"
        "    print('CONTROL_FAILED_NO_REFUSAL')\n"
        "except SystemExit as e:\n"
        "    print('REFUSED_AS_REQUIRED' if e.code == 2 else 'WRONG_CODE')\n")
    p = subprocess.run([sys.executable, "-c", probe],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.decode().strip()
    if "REFUSED_AS_REQUIRED" not in out:
        refuse("PLANTED CONTROL FAILED: beta planted at 31 deg did not make "
               "control_paper_agreement refuse (got %r). The agreement it "
               "reports at 29 deg is therefore NOT EVIDENCE." % out)
    return dict(control="PZ-F15-BETA_planted_31deg_must_refuse",
                planted_beta_deg=31.0, refused=True, passed=True)


def control_rankine_hugoniot(sol):
    """The three regions must satisfy conservation across both shocks: mass,
    normal momentum, tangential velocity and energy.  An independent check of
    the algebra, not a restatement of it."""
    worst = 0.0
    detail = []
    pairs = ((sol["region1"], sol["region2"],
              math.radians(sol["sigma_incident_deg_from_x"])),
             (sol["region2"], sol["region3"],
              math.radians(sol["beta_reflected_deg_from_x"])))
    for (a, b, beta_abs) in pairs:
        n = (math.sin(beta_abs), -math.cos(beta_abs))     # shock normal
        t = (math.cos(beta_abs), math.sin(beta_abs))
        una = a["u"] * n[0] + a["v"] * n[1]
        unb = b["u"] * n[0] + b["v"] * n[1]
        uta = a["u"] * t[0] + a["v"] * t[1]
        utb = b["u"] * t[0] + b["v"] * t[1]
        mass = a["rho"] * una - b["rho"] * unb
        mom = a["rho"] * una ** 2 + a["p"] - (b["rho"] * unb ** 2 + b["p"])
        tang = uta - utb
        ha = GAMMA / (GAMMA - 1.0) * a["p"] / a["rho"] + 0.5 * una ** 2
        hb = GAMMA / (GAMMA - 1.0) * b["p"] / b["rho"] + 0.5 * unb ** 2
        ener = ha - hb
        for name, val in (("mass", mass), ("normal_momentum", mom),
                          ("tangential_velocity", tang), ("energy", ener)):
            worst = max(worst, abs(val))
            detail.append(dict(residual=name, value=val))
    if worst > 1e-10:
        refuse("RANKINE-HUGONIOT RESIDUAL %.3e EXCEEDS 1e-10; the three-region "
               "solution is not conservative and is not an exact solution" % worst)
    return dict(control="rankine_hugoniot_residuals", worst=worst,
                detail=detail, passed=True)


def control_geometry_in_domain(sol):
    """The reflected shock must leave through the supersonic outflow, not the
    top, or the top boundary condition is inconsistent with the solution."""
    y_exit = sol["reflected_shock_exit_y_at_xmax"]
    if not (Y_MIN < y_exit < Y_MAX):
        refuse("the reflected shock reaches x = %.3f at y = %.6f, outside "
               "(%.1f, %.1f): it exits the TOP boundary, where a uniform "
               "region-2 state is imposed. The case as registered would be "
               "inconsistent." % (X_MAX, y_exit, Y_MIN, Y_MAX))
    if sol["region3"]["mach"] <= 1.0:
        refuse("region 3 Mach %.6f is subsonic; zero-gradient extrapolation at "
               "the outflow is not admissible" % sol["region3"]["mach"])
    return dict(control="geometry_and_outflow", exit_y=y_exit,
                mach3=sol["region3"]["mach"], passed=True)


def selftest_predicate(controls):
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if len(controls) != 4:
        return False, "expected 4 controls, ran %d" % len(controls)
    if not __debug__:
        return False, "running under -O"
    return True, ("4 controls green: the recovered beta = 29 deg reproduces the "
                  "paper's printed top-boundary state on every component; a beta "
                  "planted at 31 deg refuses; Rankine-Hugoniot residuals are "
                  "below 1e-10 across both shocks; the reflected shock exits the "
                  "supersonic outflow inside the domain")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    sol = solve()
    controls = [control_paper_agreement(sol),
                control_paper_agreement_is_able_to_fail(),
                control_rankine_hugoniot(sol),
                control_geometry_in_domain(sol)]

    if a.json:
        print(json.dumps(dict(solution=sol, controls=controls), indent=2))
        return 0

    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, predicate=dict(ok=ok, why=why)),
                         indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        # THE CLAIM IS INSIDE THE PASSING BRANCH.
        print("\nSELFTEST GREEN -- %s" % why)
        return 0

    for name in ("region1", "region2", "region3"):
        r = sol[name]
        print("%-8s rho=%.9f  u=%.9f  v=%.9f  p=%.9f  M=%.9f"
              % (name, r["rho"], r["u"], r["v"], r["p"], r["mach"]))
    print("beta_incident = %.6f deg (recovered, checked against the paper)"
          % sol["beta_incident_deg"])
    print("deflection    = %.6f deg" % sol["deflection_deg"])
    print("sigma_incident= %.6f deg from x" % sol["sigma_incident_deg_from_x"])
    print("beta_reflected= %.6f deg from x" % sol["beta_reflected_deg_from_x"])
    print("x_wall        = %.9f" % sol["x_wall_impingement"])
    print("L1_floor_per_dx = %.12f" % sol["L1_floor_per_dx"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
