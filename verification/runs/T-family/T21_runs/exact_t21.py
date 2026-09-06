#!/usr/bin/env python3
"""exact_t21.py -- the T21 REFERENCE, DERIVED HERE AND NEVER TRANSCRIBED.

REGISTERED BY docs/campaigns/T-family/T21_PREREGISTRATION.md §1 line 2:
"the closed-form steady radial-conduction solution for a cylindrical shell,
derived in this document (§3) and re-derived independently in the comparator,
NEVER TRANSCRIBED.  No paper is required and none is cited as a source of
constants."  Precedent: exact_t18.py, exact_t9a.py.

THE DERIVATION, FROM CONSERVATION AND FOURIER'S LAW AND NOTHING ELSE
--------------------------------------------------------------------
Steady conduction, no source inside the shell, so the radial power crossing
every cylindrical surface of radius r is the same constant P_sector.  Through a
sector of included angle theta and axial length L the area at radius r is

    A(r) = theta * r * L

Fourier:  P_sector = -k A(r) dT/dr = -k theta L r dT/dr

Separating and integrating from r_i to r_o:

    dT = T(r_i) - T(r_o) = P_sector * ln(r_o/r_i) / (theta * k * L)      (1)

At theta = 2*pi this reduces to the full-cylinder form P ln(r_o/r_i)/(2 pi k L),
which is why §3.4 registers P_sector = P_full * theta/(2*pi): entering that into
fvOptions makes (1) return the FULL-CYLINDER drop for P_full, so the referent is
literally the directive's formula and the 5-degree wedge cancels exactly.

TWO READERS, TWO DIFFERENT EXTENTS -- THE ANTI-DEGENERACY CONTROL (§4.4)
------------------------------------------------------------------------
Q1 reads PATCH averages, so its extent is r_i -> r_o exactly.
Q2 reads the innermost and outermost CELL RINGS, whose centres on a uniform
radial mesh of N cells sit at r_i + dr/2 and r_o - dr/2, dr = (r_o-r_i)/N.
Q2's referent is therefore (1) evaluated over a SHORTER span, and the two
referents MUST DIFFER -- if a comparator ever reports them equal, the readers
have collapsed onto one code path and the control is dead.  Q2's residual is
required by §1 line 3 to differ from Q1's.

Nothing here reads a case, a mesh or a field.  Pure functions of the registered
geometry and materials, so the reference cannot inherit a defect from the run it
is used to judge.

Exit 0 selftest passed, 1 failed.  Zero bare `assert` (L-332).
"""
import math
import sys

sys.dont_write_bytecode = True

# Registered geometry and materials -- T21_PREREGISTRATION.md §1 line 1.
R_I = 0.0335        # m, housing inner radius
R_O = 0.0375        # m, housing outer radius
L_AX = 0.125        # m, axial length
K_HOUSING = 167.0   # W/m/K, aluminium
THETA_DEG = 5.0     # wedge included angle


def p_sector(p_full, theta_rad):
    """§3.4, THE WEDGE POWER FACTOR, AND IT LIVES IN EXACTLY ONE PLACE.

    The number written into fvOptions is P_full * theta/(2*pi).  The builder
    computes it from a theta READ FROM THE GENERATED blockMeshDict; the
    comparator recomputes theta from the mesh and asserts the fvOptions value
    against this function to 1e-12 relative, REFUSING on mismatch.  A wedge
    angle appearing as a literal in two files is a defect waiting to happen."""
    return p_full * theta_rad / (2.0 * math.pi)


def dT_shell(p_sector_w, r_in, r_out, theta_rad, k, length):
    """Equation (1).  The ONLY place the closed form appears."""
    if r_out <= r_in or theta_rad <= 0.0 or k <= 0.0 or length <= 0.0:
        return None
    return p_sector_w * math.log(r_out / r_in) / (theta_rad * k * length)


def dT_wall(p_full, r_in=R_I, r_out=R_O, theta_deg=THETA_DEG,
            k=K_HOUSING, length=L_AX):
    """Q1's referent: PATCH to PATCH, extent r_i -> r_o."""
    th = math.radians(theta_deg)
    return dT_shell(p_sector(p_full, th), r_in, r_out, th, k, length)


def dT_cells(p_full, n_radial, r_in=R_I, r_out=R_O, theta_deg=THETA_DEG,
             k=K_HOUSING, length=L_AX):
    """Q2's referent: innermost to outermost CELL-RING CENTRE on a uniform
    radial mesh of n_radial cells.  A SHORTER span than Q1's, by half a cell at
    each end, and therefore a DIFFERENT number (§4.4)."""
    if n_radial < 2:
        return None
    dr = (r_out - r_in) / float(n_radial)
    th = math.radians(theta_deg)
    return dT_shell(p_sector(p_full, th), r_in + 0.5 * dr, r_out - 0.5 * dr,
                    th, k, length)


# ---------------------------------------------------------------------------
def selftest():
    ok = [True]

    def chk(c, msg):
        ok[0] = ok[0] and bool(c)
        print("  [%s] %s" % ("PASS" if c else "FAIL", msg))

    print("exact_t21 selftest")

    # 1. the four registered band anchors, §1 line 4
    REG = {100.0: 0.0859974153, 300.0: 0.257992246,
           600.0: 0.515984492, 1000.0: 0.859974153}
    worst = 0.0
    for p, want in REG.items():
        got = dT_wall(p)
        worst = max(worst, abs(got - want) / want)
        chk(abs(got - want) / want < 1e-9,
            "P_full=%-6.0f W -> dT_wall %.10f K, registered %.10f" % (p, got, want))
    chk(worst < 1e-9, "worst relative deviation from the registered anchors %.2e" % worst)

    # 2. the wedge power factor, §3.4 table
    chk(abs(p_sector(100.0, math.radians(5.0)) - 1.388888889) < 1e-9,
        "P_sector(100 W, 5 deg) = %.9f W, registered 1.388888889" % p_sector(100.0, math.radians(5.0)))
    chk(abs(dT_wall(100.0, theta_deg=360.0) - dT_wall(100.0, theta_deg=5.0)) < 1e-15,
        "dT_wall is WEDGE-INVARIANT: the theta in P_sector cancels the theta in (1)")

    # 3. PLANTED CONTROLS -- a referent that does not move with its inputs is
    #    not a referent.  Each plant must MOVE the answer in the derived
    #    direction; a reference insensitive to k or geometry would pass a gate
    #    for the wrong reason.
    base = dT_wall(100.0)
    chk(dT_wall(100.0, k=K_HOUSING * 2.0) < base * 0.51 + 1e-12,
        "PLANT k x2 -> dT halves (%.6e -> %.6e)" % (base, dT_wall(100.0, k=2 * K_HOUSING)))
    chk(dT_wall(100.0, length=L_AX * 2.0) < base * 0.51 + 1e-12,
        "PLANT L x2 -> dT halves")
    chk(dT_wall(200.0) > base * 1.99,
        "PLANT P x2 -> dT doubles")
    chk(dT_wall(100.0, r_out=R_O * 1.01) > base,
        "PLANT r_o up -> dT rises (thicker shell)")
    chk(dT_shell(1.0, 0.05, 0.05, 1.0, 1.0, 1.0) is None,
        "DEGENERATE GUARD: r_out == r_in returns None, never 0.0")
    chk(dT_shell(1.0, 0.05, 0.06, 1.0, 0.0, 1.0) is None,
        "DEGENERATE GUARD: k = 0 returns None, never 0.0")

    # 4. THE ANTI-DEGENERACY CONTROL (§4.4): Q1 and Q2 must DIFFER, and Q2 must
    #    approach Q1 as the mesh refines.  Equality at any N is the tell that
    #    the two readers have collapsed onto one path.
    prev = None
    for n in (8, 16, 32):
        q2 = dT_cells(100.0, n)
        gap = base - q2
        chk(gap > 0.0, "N=%-3d  Q2 %.10f K is BELOW Q1 %.10f K, gap %.3e K" % (n, q2, base, gap))
        if prev is not None:
            chk(gap < prev, "N=%-3d  the Q1-Q2 gap SHRANK with refinement (%.3e < %.3e)" % (n, gap, prev))
        prev = gap
    chk(dT_cells(100.0, 1) is None, "N < 2 returns None rather than a fabricated number")

    print("\nSELFTEST %s" % ("PASSED" if ok[0] else "FAILED"))
    return 0 if ok[0] else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    th = math.radians(THETA_DEG)
    print("T21 reference, derived from geometry and materials only")
    print("  r_i %.4f m  r_o %.4f m  L %.3f m  k %.1f W/m/K  theta %.1f deg"
          % (R_I, R_O, L_AX, K_HOUSING, THETA_DEG))
    for p in (100.0, 300.0, 600.0, 1000.0):
        print("  P_full %6.0f W  P_sector %12.9f W  dT_wall %.10f K  band +/- %.4f mK"
              % (p, p_sector(p, th), dT_wall(p), 0.01 * dT_wall(p) * 1000.0))
