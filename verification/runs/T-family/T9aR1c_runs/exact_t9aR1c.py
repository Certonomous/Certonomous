#!/usr/bin/env python3
"""T9a-R1c's referent, DERIVED BY TWO INDEPENDENT ROUTES and CROSS-CHECKED
against FOUR numbers this module did not compute.

THE PROBLEM.  Steady one-dimensional conduction through a three-layer plane
wall, piecewise-constant conductivity, no generation, Dirichlet faces:

    d/dx ( k(x) dT/dx ) = 0,   T(0) = T_hot,   T(L_tot) = T_cold

    layer 1: L 0.05 m, k 0.80 W/mK
    layer 2: L 0.10 m, k 0.04 W/mK
    layer 3: L 0.02 m, k 16.0 W/mK
    T_hot 350 K, T_cold 300 K

The exact solution is PIECEWISE LINEAR with one flux common to all layers.

ROUTE A -- the closed form (series resistance):

    R_tot = SUM_i L_i / k_i,   q = (T_hot - T_cold) / R_tot
    T_i1  = T_hot - q L_1 / k_1,   T_i2 = T_i1 - q L_2 / k_2

ROUTE B -- INDEPENDENT of route A: the two interface temperatures are the
unknowns of a 2x2 LINEAR SYSTEM built from flux continuity across the two
interfaces,

    k1 (T_hot - T_i1) / L_1  =  k2 (T_i1 - T_i2) / L_2      (interface 1)
    k2 (T_i1 - T_i2) / L_2   =  k3 (T_i2 - T_cold) / L_3    (interface 2)

solved by GENERAL GAUSSIAN ELIMINATION WITH PARTIAL PIVOTING that knows nothing
about the series-resistance formula.  Route B never evaluates R_tot.  An
algebra slip in route A -- a dropped layer, a reciprocal the wrong way up, a
sign -- moves route A and does NOT move route B, and the two are required to
agree to 1e-12 RELATIVE or this module REFUSES.

THE EXTERNAL CROSS-CHECK (VERIFICATION_CHARTER section 6a discipline, T18/T19
form).  Route A and route B are both computed HERE, so their agreement proves
arithmetic and not provenance.  The provenance check is against T9a --

    RUNG T9a, docs/campaigns/T-family/T9a_RESULTS.md, section 1 table and
    section 1.1, graded and reported 2026-08-20/22, and carried in
    verification/runs/T-family/T9aR1b_runs/T9aR1b_registered.json ("wall"):

        T_i1              348.781082 K      (section 1 table, row R1 reference)
        q                  19.502682 W/m2   (section 1 table, row R0 reference)
        layer-1 T drop      1.218918 K      (section 1.1, "1.218918 K across
                                              layer 1 for R1")
        layer-3 T drop      0.024378 K      (section 1.1, "0.024378 K across
                                              layer 3 for R2")

-- FOUR numbers, hard-coded above from that document, that this module did not
compute.  Each is stated there to SIX DECIMAL PLACES, so the agreement
tolerance is 1e-6 ABSOLUTE, which is the precision the source carries and not a
tolerance chosen to pass.  Disagreement REFUSES (exit 2); it is never a note.

The four are not four independent facts -- drop1 = T_hot - T_i1 and
drop3 = q L_3 / k_3 are functions of the same geometry -- and this file says so
rather than claiming four checks where there are two.  What the extra two buy
is that a wrong LAYER (a transposed L or k) moves drop3 while leaving T_i1
alone, which the T_i1 check alone would not see; that is measured in
--selftest, not asserted here.

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2).
Exit: 0 verified, 2 REFUSAL.
"""
import sys

EXIT_OK, EXIT_REFUSE = 0, 2

# ---- T9a's REGISTERED numbers, hard-coded from T9a_RESULTS.md -------------
# THIS MODULE DID NOT COMPUTE THESE.  Source named in the docstring above.
T9A_REGISTERED = dict(
    rung="T9a",
    source="docs/campaigns/T-family/T9a_RESULTS.md section 1 table and section 1.1",
    T_i1=348.781082,
    q=19.502682,
    drop_layer1=1.218918,
    drop_layer3=0.024378,
    tol_abs=1e-6,        # the precision to which the source states them
)


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def _solve2(A, b):
    """Gaussian elimination with partial pivoting on a 2x2 system.  A general
    linear solver: it is told the matrix and the right-hand side and nothing
    about where they came from."""
    M = [list(A[0]) + [b[0]], list(A[1]) + [b[1]]]
    n = 2
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) == 0.0:
            refuse("route B: the flux-continuity system is singular at column %d" % c)
        M[c], M[piv] = M[piv], M[c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            for cc in range(c, n + 1):
                M[r][cc] -= f * M[c][cc]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = M[r][n] - sum(M[r][cc] * x[cc] for cc in range(r + 1, n))
        x[r] = s / M[r][r]
    return x


def route_a(layers, T_hot, T_cold):
    """CLOSED FORM: series resistance."""
    R = sum(l["L"] / l["k"] for l in layers)
    if R <= 0.0:
        refuse("route A: total thermal resistance %.17g is not positive" % R)
    q = (T_hot - T_cold) / R
    T_i1 = T_hot - q * layers[0]["L"] / layers[0]["k"]
    T_i2 = T_i1 - q * layers[1]["L"] / layers[1]["k"]
    return dict(R_tot=R, q=q, T_i1=T_i1, T_i2=T_i2)


def route_b(layers, T_hot, T_cold):
    """INDEPENDENT: flux continuity as a 2x2 linear system, general solver.
    Unknowns x = [T_i1, T_i2].

      c1 (T_hot - T_i1) = c2 (T_i1 - T_i2)   ->  (c1 + c2) T_i1 - c2 T_i2 = c1 T_hot
      c2 (T_i1 - T_i2)  = c3 (T_i2 - T_cold) ->  c2 T_i1 - (c2 + c3) T_i2  = -c3 T_cold

    with c_i = k_i / L_i.  R_tot is never formed."""
    c = [l["k"] / l["L"] for l in layers]
    A = [[c[0] + c[1], -c[1]],
         [c[1], -(c[1] + c[2])]]
    b = [c[0] * T_hot, -c[2] * T_cold]
    T_i1, T_i2 = _solve2(A, b)
    q = c[0] * (T_hot - T_i1)
    return dict(q=q, T_i1=T_i1, T_i2=T_i2)


def solve(layers, T_hot, T_cold, tol_route=1e-12, quiet=False):
    """Both routes, their agreement, and the FOUR external cross-checks.
    Refuses on any failure; returns the referent dict on success."""
    a = route_a(layers, T_hot, T_cold)
    b = route_b(layers, T_hot, T_cold)
    worst = 0.0
    for name in ("q", "T_i1", "T_i2"):
        d = abs(a[name] - b[name]) / abs(a[name])
        worst = max(worst, d)
        if d > tol_route:
            refuse("ROUTE A and ROUTE B disagree on %s: closed form %.17g, flux-continuity "
                   "linear solve %.17g, relative %.3e > %.1e" % (name, a[name], b[name], d, tol_route))

    # ---- the four external cross-checks, against T9a's registered numbers ----
    R = T9A_REGISTERED
    got = dict(T_i1=a["T_i1"], q=a["q"],
               drop_layer1=T_hot - a["T_i1"],
               drop_layer3=a["T_i2"] - T_cold)
    xdev = {}
    for name in ("T_i1", "q", "drop_layer1", "drop_layer3"):
        d = abs(got[name] - R[name])
        xdev[name] = d
        if d > R["tol_abs"]:
            refuse("CROSS-CHECK against %s's registered %s FAILED: this module derives %.9f, "
                   "%s states %.6f (%s), |difference| %.3e > %.1e -- a referent that cannot "
                   "reproduce a registered value is not graded against, it is refused"
                   % (R["rung"], name, got[name], R["rung"], R[name], R["source"], d, R["tol_abs"]))

    out = dict(q=a["q"], T_i1=a["T_i1"], T_i2=a["T_i2"], R_tot=a["R_tot"],
               drop_layer1=got["drop_layer1"], drop_layer3=got["drop_layer3"],
               route_agreement_rel=worst,
               cross_check=dict(rung=R["rung"], source=R["source"], tol_abs=R["tol_abs"],
                                registered={k: R[k] for k in ("T_i1", "q", "drop_layer1", "drop_layer3")},
                                abs_deviation=xdev))
    if not quiet:
        print("referent (exact_t9aR1c): q = %.9f W/m2, T_i1 = %.12f K, T_i2 = %.12f K"
              % (out["q"], out["T_i1"], out["T_i2"]))
        print("  route A (closed form) vs route B (flux-continuity linear solve): agree to %.2e relative"
              % worst)
        print("  cross-check vs %s registered (%s), tol %.0e abs: T_i1 %.2e, q %.2e, drop1 %.2e, drop3 %.2e"
              % (R["rung"], R["source"], R["tol_abs"], xdev["T_i1"], xdev["q"],
                 xdev["drop_layer1"], xdev["drop_layer3"]))
    return out


# ------------------------------------------------------------------ selftest
WALL = dict(layers=[dict(L=0.05, k=0.8), dict(L=0.1, k=0.04), dict(L=0.02, k=16.0)],
            T_hot=350.0, T_cold=300.0)


def selftest():
    import ast
    import copy
    fails = []
    print("exact_t9aR1c selftest:")

    ref = solve(WALL["layers"], WALL["T_hot"], WALL["T_cold"])
    ok = (ref["route_agreement_rel"] <= 1e-12)
    print("  [%s] the registered wall: routes A and B agree to %.2e relative; four cross-checks pass"
          % ("ok " if ok else "FAIL", ref["route_agreement_rel"]))
    if not ok:
        fails.append("routes")

    # DRIVEN: a planted conductivity error must be caught by the cross-checks.
    for label, mutate, want in (
            ("layer-1 k planted 1e-4 relative high -> cross-check REFUSES", ("k", 0, 1.0 + 1e-4), True),
            ("layer-2 k planted 1e-4 relative high -> cross-check REFUSES", ("k", 1, 1.0 + 1e-4), True),
            ("layer-3 L planted 1e-3 relative high -> cross-check REFUSES", ("L", 2, 1.0 + 1e-3), True)):
        key, idx, fac = mutate
        w = copy.deepcopy(WALL["layers"])
        w[idx][key] *= fac
        fired = False
        try:
            solve(w, WALL["T_hot"], WALL["T_cold"], quiet=True)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        ok = (fired == want)
        print("  [%s] %s" % ("ok " if ok else "FAIL", label))
        if not ok:
            fails.append(label)

    # DRIVEN: the layer-3 checks buy something the T_i1 check alone does not.
    # Transposing L_3 and k_3's ROLES leaves nothing about layer 1 unchanged in
    # general, so the honest demonstration is the narrow one: perturb layer 3
    # ONLY, and show T_i1 moves LESS than drop_layer3 does, i.e. the drop3 check
    # is the SENSITIVE one for a layer-3 defect.
    w = copy.deepcopy(WALL["layers"])
    w[2]["k"] *= 1.0 + 1e-5
    a0 = route_a(WALL["layers"], WALL["T_hot"], WALL["T_cold"])
    a1 = route_a(w, WALL["T_hot"], WALL["T_cold"])
    d_Ti1 = abs(a1["T_i1"] - a0["T_i1"])
    d_drop3 = abs((a1["T_i2"] - WALL["T_cold"]) - (a0["T_i2"] - WALL["T_cold"]))
    ok = (d_drop3 > d_Ti1)
    print("  [%s] layer-3 k perturbed 1e-5: drop3 moves %.3e K, T_i1 moves %.3e K -- the drop3 "
          "cross-check is the sensitive one for a layer-3 defect"
          % ("ok " if ok else "FAIL", d_drop3, d_Ti1))
    if not ok:
        fails.append("layer3-sensitivity")

    # DRIVEN: a planted disagreement between the routes must refuse.  The plant
    # goes into route A's OUTPUT via a wall whose layer 2 resistance is doubled
    # only in the closed form -- expressed here by calling solve() with a wall
    # route B would not see.  Cheapest faithful drive: shrink tol_route below the
    # true agreement and confirm the refusal path fires on the real wall.
    fired = False
    try:
        solve(WALL["layers"], WALL["T_hot"], WALL["T_cold"], tol_route=0.0, quiet=True)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] route-agreement tolerance driven to 0 -> the disagreement path REFUSES "
          "(the refusal is reachable, not decorative)" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("route-refusal-reachable")

    # DRIVEN: a singular flux-continuity system refuses rather than dividing.
    fired = False
    try:
        _solve2([[0.0, 0.0], [0.0, 0.0]], [1.0, 1.0])
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] singular 2x2 flux-continuity system -> REFUSE (never a silent divide)"
          % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("singular")

    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count in this file = %d (planted control: the counter sees %d)"
          % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    solve(WALL["layers"], WALL["T_hot"], WALL["T_cold"])
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
