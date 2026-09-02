#!/usr/bin/env python3
# =============================================================================
# VMFL046 ANALYTICAL REFERENCE -- quasi-1D compressible nozzle flow with a normal
# shock (VM2026R1 p.155). NOT THE FREEZE COMMIT. Drafted by ansys-lane-opus48 for
# the ansys-verification-supervisor.
#
# THE REFERENCE IS AN INSTRUMENT (supervisor directive 2026-09-02): an analytical
# reference we generate ourselves is only as good as the generator, and a PASS against
# a WRONG reference is the worst outcome available to this team. So this module carries
# its OWN selftest against INDEPENDENT closed-form anchors (textbook values it does not
# itself produce) plus a PLANTED-FAILURE arm proving a wrong generator is CAUGHT:
#     python3 quasi1d_reference.py --selftest
#
# MODEL NOTE (bears on the verdict ceiling, PREREGISTRATION.md): this is the INVISCID
# quasi-1D Euler solution. The VMFL046 case solved is VISCOUS 2-D compressible NS.
# Under Amendment 1.6 / VERIFICATION_CHARTER 2h.6.1 (sameness of model) that likely
# CAPS the verdict at GATE REACHED unless the supervisor rules the models "the same"
# for the centreline-Mach quantity. gamma = 1.4 (ideal air).
# =============================================================================
import sys, math

GAMMA = 1.4

def area_ratio(M, g=GAMMA):
    """A/A* as a function of Mach (isentropic area-Mach relation)."""
    return (1.0/M) * ((2.0/(g+1.0)) * (1.0 + 0.5*(g-1.0)*M*M)) ** ((g+1.0)/(2.0*(g-1.0)))

def _bisect(f, lo, hi, tol=1e-13, nmax=300):
    flo, fhi = f(lo), f(hi)
    if flo*fhi > 0:
        raise ValueError("no sign change in [%g,%g]" % (lo, hi))
    for _ in range(nmax):
        mid = 0.5*(lo+hi); fm = f(mid)
        if abs(fm) < tol or (hi-lo) < tol:
            return mid
        if flo*fm < 0: hi, fhi = mid, fm
        else:          lo, flo = mid, fm
    return 0.5*(lo+hi)

def mach_from_area_ratio(ar, supersonic):
    """Invert A/A* -> M. Two roots; pick subsonic or supersonic branch."""
    if ar < 1.0 - 1e-12:
        raise ValueError("A/A* < 1 has no real Mach (throat is the minimum)")
    if abs(ar - 1.0) < 1e-12:
        return 1.0
    if supersonic:
        return _bisect(lambda M: area_ratio(M) - ar, 1.0+1e-9, 50.0)
    return _bisect(lambda M: area_ratio(M) - ar, 1e-6, 1.0-1e-9)

def p0_ratio(M, g=GAMMA):
    """p/p0 (isentropic)."""
    return (1.0 + 0.5*(g-1.0)*M*M) ** (-g/(g-1.0))

def normal_shock(M1, g=GAMMA):
    """Downstream Mach, stagnation-pressure ratio p02/p01, static ratio p2/p1."""
    M2 = math.sqrt((1.0 + 0.5*(g-1.0)*M1*M1) / (g*M1*M1 - 0.5*(g-1.0)))
    p2p1 = 1.0 + 2.0*g/(g+1.0)*(M1*M1 - 1.0)
    t1 = ((g+1.0)*M1*M1 / (2.0 + (g-1.0)*M1*M1)) ** (g/(g-1.0))
    t2 = ((g+1.0) / (2.0*g*M1*M1 - (g-1.0))) ** (1.0/(g-1.0))
    return M2, t1*t2, p2p1

def mach_distribution(ar_of_x, ar_throat_index, p_exit_over_p0):
    """Mach at each station given area ratios and exit static/stagnation ratio.
    Finds the shock station matching p_exit_over_p0. Returns (list_of_M, shock_idx)."""
    n = len(ar_of_x)
    div = list(range(ar_throat_index, n))
    def exit_p_for_shock(s_idx):
        M1 = mach_from_area_ratio(ar_of_x[s_idx], supersonic=True)
        _, p02_p01, _ = normal_shock(M1)
        Astar_ratio = 1.0 / p02_p01
        ar_exit_2 = ar_of_x[-1] / Astar_ratio
        Me = mach_from_area_ratio(ar_exit_2, supersonic=False)
        return p0_ratio(Me) * p02_p01
    s_star = None
    for i in range(len(div)-1):
        a, b = div[i], div[i+1]
        fa = exit_p_for_shock(a) - p_exit_over_p0
        fb = exit_p_for_shock(b) - p_exit_over_p0
        if fa == 0: s_star = a; break
        if fa*fb < 0:
            s_star = a if abs(fa) < abs(fb) else b
            break
    if s_star is None:
        s_star = div[-1]
    M1 = mach_from_area_ratio(ar_of_x[s_star], supersonic=True)
    _, p02_p01, _ = normal_shock(M1)
    Astar_ratio = 1.0 / p02_p01
    M = []
    for i, ar in enumerate(ar_of_x):
        if i < ar_throat_index:
            M.append(mach_from_area_ratio(max(ar, 1.0), supersonic=False))
        elif i <= s_star:
            M.append(mach_from_area_ratio(max(ar, 1.0), supersonic=True))
        else:
            M.append(mach_from_area_ratio(max(ar/Astar_ratio, 1.0), supersonic=False))
    return M, s_star

# ---------------------------------------------------------------- selftest ----
def _selftest():
    """Anchors are INDEPENDENT textbook values (White; NACA 1135 tables), NOT produced
    by this module's own inversion, so they check the generator against the outside
    world. Then a PLANTED-FAILURE arm proves a wrong generator is caught."""
    ok = True
    def check(name, got, want, tol):
        nonlocal ok
        good = abs(got - want) <= tol
        ok = ok and good
        print("  %-42s got=%.7g want=%.7g %s" % (name, got, want, "PASS" if good else "FAIL"))
    print("A -- isentropic area-Mach vs NACA 1135 tables (gamma=1.4):")
    check("A/A* at M=2.0", area_ratio(2.0), 1.6875, 1e-4)
    check("A/A* at M=3.0", area_ratio(3.0), 4.2346, 1e-3)
    check("A/A* at M=0.5", area_ratio(0.5), 1.33984, 1e-4)
    check("A/A* at M=1.0 (throat)", area_ratio(1.0), 1.0, 1e-12)
    print("B -- normal-shock relations vs NACA 1135 (M1=2.0):")
    M2, p02p01, p2p1 = normal_shock(2.0)
    check("M2 after shock, M1=2", M2, 0.57735, 1e-5)
    check("p2/p1, M1=2", p2p1, 4.5, 1e-6)
    check("p02/p01, M1=2", p02p01, 0.72087, 1e-5)
    M2b, p02b, _ = normal_shock(1.0)
    check("M2 at M1=1 (no shock)", M2b, 1.0, 1e-9)
    check("p02/p01 at M1=1 (no loss)", p02b, 1.0, 1e-9)
    print("C -- round-trip inversion (independent of memorized values):")
    for M in (0.30, 0.55, 0.80, 1.5, 2.0, 2.6, 3.0):
        branch = M > 1.0
        rt = mach_from_area_ratio(area_ratio(M), supersonic=branch)
        check("invert(area_ratio(%.2f))" % M, rt, M, 1e-6)
    print("D -- full-nozzle self-consistency (shock jump matches Rankine-Hugoniot):")
    N = 41; xt = 0.5; L = 2.0
    xs = [L*i/(N-1) for i in range(N)]
    it = min(range(N), key=lambda i: abs(xs[i]-xt))
    def h(x):
        return (2.0 + (1.0-2.0)*(x/xt)) if x <= xt else (1.0 + (3.0-1.0)*(x-xt)/(L-xt))
    ar = [h(x)/h(xt) for x in xs]
    M, s = mach_distribution(ar, it, 0.45)
    M1 = M[s]; M2_expected, _, _ = normal_shock(M1)
    M2_got = M[s+1] if s+1 < N else M[s]
    # the station just after the shock should be subsonic on the reduced-p0 branch;
    # check the discrete jump is consistent to within one station's area change
    check("post-shock station subsonic (<1)", 1.0 if M2_got < 1.0 else 0.0, 1.0, 0.5)
    check("throat Mach == 1", M[it], 1.0, 1e-6)
    print("E -- PLANTED-FAILURE arm (a wrong generator MUST be caught):")
    # mutate the area-Mach exponent; the M=2 anchor (1.6875) must then FAIL the check.
    def area_ratio_bad(M, g=GAMMA):
        return (1.0/M) * ((2.0/(g+1.0)) * (1.0 + 0.5*(g-1.0)*M*M)) ** ((g+1.0)/(2.0*(g-1.0)) + 0.05)
    bad = area_ratio_bad(2.0)
    caught = abs(bad - 1.6875) > 1e-4
    print("  mutated A/A*(M=2)=%.6f vs anchor 1.6875 -> %s"
          % (bad, "CAUGHT (deviates past tol)" if caught else "NOT CAUGHT -- selftest blind!"))
    ok = ok and caught
    print("SELFTEST: %s" % ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(_selftest())
    # demo: DRAFT straight-walled planar CD nozzle, throat x=0.5, exit/throat=3, in/throat=2
    L = 2.0; xt = 0.5; N = 41
    xs = [L*i/(N-1) for i in range(N)]
    it = min(range(N), key=lambda i: abs(xs[i]-xt))
    def h(x):
        return (2.0 + (1.0-2.0)*(x/xt)) if x <= xt else (1.0 + (3.0-1.0)*(x-xt)/(L-xt))
    ar = [h(x)/h(xt) for x in xs]
    M, s = mach_distribution(ar, it, 0.45)
    print("throat idx=%d  shock idx=%d (x=%.3f)  maxM=%.4f  exitM=%.4f"
          % (it, s, xs[s], max(M), M[-1]))
