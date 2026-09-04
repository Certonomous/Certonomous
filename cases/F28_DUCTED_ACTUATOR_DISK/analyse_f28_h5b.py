#!/usr/bin/env python3
"""F28 H5B -- CONCENTRATION COMPARATOR.  The grading path for the H5B arm.

Registered by:
  verification/campaign/F28G_H5B_CONCENTRATION_PREREGISTRATION.md

WHAT IT GRADES, and what it deliberately does not.

  G1   CONCENTRATION of the residual DENSITY of `p`.  GATED at f1% >= 0.50,
       which is 50.06x the count null of 355/35544 = 0.0099876.
  G2'  EXCLUSION, applied SYMMETRICALLY to all five zones: a zone carrying
       <= 0.10 x its OWN null is EXCLUDED.  No zone is named in advance.
  G3'  STABILITY: G1 and every exclusion must hold in >= 4 of 5 snapshots.
       G3' IS LOAD-BEARING HERE, NOT DECORATIVE -- the observed margin is
       1.30x, not the retired gate's 2.0x, so snapshot variation can decide
       the verdict.  A SINGLE-SNAPSHOT f1% IS NEVER THE RESULT.

  LOCATION ATTRIBUTION IS REPORTED AND EXPLICITLY NOT GATED.  Every zone share
  prints WITH ITS NULL AND ITS MULTIPLE, because a bare `0.5262` can be cited as
  though it passed something and `0.5262 (null 0.2510, 2.10x, UNGATED)` cannot.
  That mitigation is required: "reported but not gated" is L-478's family.

THE MEASURAND IS DENSITY `d_c = r_c / V_c` ON REAL CELL VOLUMES.  The raw field
OpenFOAM writes is `finestResidual = tsource() - Apsi`, UN-NORMALISED, and in
finite volume each cell's equation is integrated over its own volume, so `|r|`
carries cell volume -- real volumes on this mesh span 3.333e+14, so raw `r_c`
compares incommensurable quantities.  `normFactor`-matching does NOT fix this:
`normFactor` is a single global scalar, so it restores commensurability exactly
and reorders nothing (measured: identical f1% to 17 digits).  All three
candidates are reported every time, because the density choice was made with its
outcome in view and the discharge is publication, not assurance.

THE DETERMINISM RULES D1-D6 ARE THE REGISTRATION'S, NOT THIS FILE'S.  At a 1.30x
margin an incidental implementation choice could move the verdict, so:
  D1  top set is EXACTLY 355 by COUNT -- never "355 plus ties"
  D2  total order (-|d|, cell index) -- independent of sort stability
  D3  math.fsum for every sum -- exactly rounded, so order-independent
  D4  d = r/V then abs; V > 0 everywhere
  D5  comparisons exact, no epsilon
  D6  zone shares by the same fsum over the same top set
Changing any of them is an amendment to a frozen document, not an edit here.

CONTROLS (standing rule 3).  `--selftest` runs the planted limbs, and
`--fragility <case> <V> <t>` re-runs the registered fragility control on real
data: perturbing tie-break and accumulation order must not move the verdict.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyse_f28_h5 as A  # noqa: E402  readers, zone_of, completion, age guard

# ---------------------------------------------------------------------------
# FROZEN -- these are the registration's numbers.  Moving one is an amendment.
# ---------------------------------------------------------------------------
N_CELLS = 35544
N_TOP = int(0.01 * N_CELLS)                 # D1: 355, by COUNT
CONC_NULL = N_TOP / float(N_CELLS)          # 0.0099876
G1_THRESHOLD = 0.50                         # = 50.06 x CONC_NULL
EXCLUSION_FACTOR = 0.10                     # share <= 0.10 x the zone's own null
G3_MIN = 4                                  # of 5
SNAPSHOTS = [15040, 15080, 15120, 15160, 15200]
RATIO_TOL = 1.0e-3                          # commensurability constancy
GATED_FIELD = "p"                           # p ONLY; Uy is reported, not gated
REPORTED_FIELDS = ["p", "Ux", "Uy", "Uz", "k", "omega"]
ZONES = ["Z-DISK", "Z-DUCT", "Z-HUB", "Z-AXIS", "Z-ELSEWHERE"]


class Refuse(Exception):
    pass


# ---------------------------------------------------------------------------
# D1-D4: the registered statistic.  One function, so there is one place the
# rules live and one place a control can perturb them.
# ---------------------------------------------------------------------------

def density(raw, V):
    """D4: d = r/V then abs.  Refuses a non-positive volume rather than
    producing a silently signed or infinite density."""
    if len(raw) != len(V):
        raise Refuse("density: %d residual values against %d volumes"
                     % (len(raw), len(V)))
    bad = [i for i, v in enumerate(V) if not v > 0.0]
    if bad:
        raise Refuse("density: %d cells have non-positive volume (first: %d). "
                     "A density cannot be formed." % (len(bad), bad[0]))
    return [abs(raw[i] / V[i]) for i in range(len(raw))]


def top_set(d, tie_key=None):
    """D1 + D2.  Exactly N cells, by the total order (-|d|, index).

    `tie_key` exists ONLY for the fragility control: it replaces the
    tie-breaking component.  Grading always uses the registered default.
    """
    n = max(1, int(0.01 * len(d)))
    key = tie_key or (lambda i: i)
    return sorted(range(len(d)), key=lambda i: (-d[i], key(i)))[:n]


def concentration(d, tie_key=None, acc=math.fsum):
    """D3: both sums by fsum -- exactly rounded, hence order-independent."""
    total = acc(d)
    if not total > 0.0:
        raise Refuse(
            "PLANTED-ZERO LIMB REFUSES: the summed density is %r over %d cells. "
            "A field of zeros is not a concentrated-nowhere answer; it is a "
            "reader or a run that produced nothing.  No verdict is issued."
            % (total, len(d)))
    top = top_set(d, tie_key)
    return acc(d[i] for i in top) / total, top


def zone_shares(d, top, centres, acc=math.fsum):
    """D6: zone shares of the top-set mass, same accumulation rule."""
    tot = acc(d[i] for i in top)
    if not tot > 0.0:
        raise Refuse("zone_shares: the top-set mass is %r" % tot)
    out = {}
    for z in ZONES:
        out[z] = acc(d[i] for i in top if A.zone_of(centres[i]) == z) / tot
    return out


def zone_nulls(centres):
    """The COUNT fraction -- the null for a share of the top-N by density.

    Under uniform density every cell ties, so the top-N is an arbitrary subset
    and each zone's expected share is its share of CELLS.  (Volume fraction is
    the null for a share of TOTAL MASS, which is a different statistic.)
    """
    n = len(centres)
    out = dict((z, 0) for z in ZONES)
    for p in centres:
        out[A.zone_of(p)] += 1
    return dict((z, c / float(n)) for z, c in out.items())


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------

def commensurability(raw_by_t, dat_by_t, times):
    """The founding argument's own falsifier, on the RAW field.

    `solverInfo.dat` records `gSumMag(finestResidual)/normFactor`, so
    `sum|r| / (.dat scalar)` IS `normFactor` and must be CONSTANT across
    snapshots.  If it is not, the field is not the quantity the record carries
    and the arm's founding argument fails with it.  `normFactor` is written to
    no artifact, so only the CONSTANCY is testable -- stated as the weaker
    check it is.
    """
    ratios = []
    for t in times:
        s = dat_by_t[t]
        if not s > 0:
            raise Refuse("commensurability: .dat scalar at %d is %r" % (t, s))
        ratios.append(math.fsum(abs(x) for x in raw_by_t[t]) / s)
    lo, hi = min(ratios), max(ratios)
    spread = (hi - lo) / hi
    if spread > RATIO_TOL:
        raise Refuse(
            "COMMENSURABILITY LIMB REFUSES: sum|r| / (.dat scalar) is not "
            "constant across snapshots -- spread %.3e exceeds %.3e.  ratios=%s. "
            "The field is not the quantity the .dat records."
            % (spread, RATIO_TOL, ["%.6g" % r for r in ratios]))
    return ratios


# ---------------------------------------------------------------------------
# GRADING
# ---------------------------------------------------------------------------

def grade(case, vpath):
    times = SNAPSHOTS
    print("case      : %s" % case)
    print("snapshots : %s" % times)
    print("measurand : residual DENSITY d = r/V on REAL cell volumes (%s)" % vpath)
    print("")

    problems = A.completion(case, times[-1], 200, REPORTED_FIELDS, times)
    if problems:
        print("NOT A RESULT -- strict completion (standing rule 4) failed:")
        for p in problems:
            print("   - %s" % p)
        return 1
    A.age_guard(case, times, REPORTED_FIELDS)
    print("age guard : PASS (anchor %s)" % A.SENTINEL)

    V = A.read_internal_scalars(vpath)
    centres = A.cell_centres(case)
    if not (len(V) == len(centres) == N_CELLS):
        raise Refuse("cells: V %d, centres %d, registered %d"
                     % (len(V), len(centres), N_CELLS))
    nulls = zone_nulls(centres)

    raw_by_t, dat_by_t = {}, {}
    for t in times:
        path, _sep = A.residual_field_path(os.path.join(case, str(t)),
                                           GATED_FIELD)
        vals = A.read_internal_scalars(path)
        if len(vals) != N_CELLS:
            raise Refuse("%s carries %d values, registered %d"
                         % (path, len(vals), N_CELLS))
        raw_by_t[t] = vals
    dat_by_t = A.dat_scalars(case, GATED_FIELD, times)

    ratios = commensurability(raw_by_t, dat_by_t, times)
    print("commensurability: PASS -- sum|r|/(.dat scalar) constant to %.1e "
          "across %d snapshots (%s)"
          % (RATIO_TOL, len(times), ", ".join("%.6g" % r for r in ratios)))

    # ---- the three candidate quantities, ALL reported EVERY time -----------
    print("")
    print("ALL THREE CANDIDATES (the density choice was made with its outcome")
    print("in view; the discharge is publication, not assurance):")
    for t in times:
        raw = raw_by_t[t]
        nf = math.fsum(abs(x) for x in raw) / dat_by_t[t]
        cands = [("raw", [abs(x) for x in raw]),
                 ("normFactor-matched", [abs(x) / nf for x in raw]),
                 ("density r/V", density(raw, V))]
        print("  iter %d" % t)
        for name, q in cands:
            f1, top = concentration(q)
            sh = zone_shares(q, top, centres)
            best = max(sh.items(), key=lambda kv: kv[1])
            print("    %-20s f1%%=%.6f   top zone %s %.4f (null %.6f, %.2fx, "
                  "UNGATED)" % (name, f1, best[0], best[1], nulls[best[0]],
                                best[1] / nulls[best[0]] if nulls[best[0]] else float("nan")))

    # ---- G1 / G2' / G3' on the DENSITY, the registered measurand ----------
    print("")
    print("GATED MEASURAND: density, field %s" % GATED_FIELD)
    n_conc = 0
    excl_count = dict((z, 0) for z in ZONES)
    for t in times:
        d = density(raw_by_t[t], V)
        f1, top = concentration(d)
        sh = zone_shares(d, top, centres)
        if f1 >= G1_THRESHOLD:
            n_conc += 1
        print("  iter %-6d f1%%=%.6f (null %.6f, %.2fx, threshold %.2f) %s"
              % (t, f1, CONC_NULL, f1 / CONC_NULL, G1_THRESHOLD,
                 "OK" if f1 >= G1_THRESHOLD else "below"))
        for z in ZONES:
            excluded = sh[z] <= EXCLUSION_FACTOR * nulls[z]
            if excluded:
                excl_count[z] += 1
            print("      %-12s share %.6f  null %.6f  %.2fx  %s"
                  % (z, sh[z], nulls[z],
                     sh[z] / nulls[z] if nulls[z] else float("nan"),
                     "EXCLUDED" if excluded else "carried"))

    print("")
    cond, satisfied, lines = A.g1_outcome(
        dict((t, concentration(density(raw_by_t[t], V))[0]) for t in times),
        times)
    for ln in lines:
        print(ln)
    if not satisfied:
        print("VERDICT G1 : %s" % ("NOT A RESULT" if cond == "INSUFFICIENT"
                                   else "GATE FAIL -- %s" % cond))
    else:
        print("VERDICT G1 : PASS (concentrated in %d of %d, threshold %d)"
              % (n_conc, len(times), G3_MIN))

    print("")
    print("VERDICT G2' -- EXCLUSION, applied identically to all five zones:")
    for z in ZONES:
        ok = excl_count[z] >= G3_MIN
        print("   %-12s EXCLUDED in %d of %d snapshots -> %s"
              % (z, excl_count[z], len(times),
                 "EXCLUDED (PASS)" if ok else "not excluded"))
    if excl_count["Z-AXIS"] >= G3_MIN:
        print("   Z-AXIS is EXCLUDED across the required snapshots: registered")
        print("   BEFORE the run as EVIDENCE AGAINST H4, whose whole content is")
        print("   the near-axis extreme aspect ratio.")
    else:
        print("   Z-AXIS is NOT excluded.  Registered as ONE-DIRECTIONAL: this")
        print("   does NOT support H4.")

    print("")
    print("LOCATION ATTRIBUTION: NO GATE WAS REGISTERED AND NO LOCATION CLAIM")
    print("IS GRADED.  Every share above carries its null and its multiple.")
    print("`Uy` is REPORTED UNCOVERED and NOT GATED -- a finding about the zone")
    print("model, not a defect to engineer away.")
    print("")
    print("SINGLE GRID: no Roache triple exists, so NO GCI is computed or")
    print("quoted and no result here is grid-converged.")
    return 0


# ---------------------------------------------------------------------------
# THE FRAGILITY CONTROL -- the registration's §4.2c, re-runnable on real data
# ---------------------------------------------------------------------------

def fragility(case, vpath, t):
    import random
    V = A.read_internal_scalars(vpath)
    raw = A.read_internal_scalars(
        A.residual_field_path(os.path.join(case, str(t)), GATED_FIELD)[0])
    d = density(raw, V)

    def naive(seq):
        s = 0.0
        for x in seq:
            s += x
        return s

    rnd = list(range(len(d)))
    random.seed(12345)
    random.shuffle(rnd)
    rank = dict((c, k) for k, c in enumerate(rnd))

    combos = [
        ("index ASC  + fsum", None, math.fsum),
        ("index DESC + fsum", (lambda i: -i), math.fsum),
        ("random     + fsum", (lambda i: rank[i]), math.fsum),
        ("index ASC  + naive L->R", None, naive),
        ("index ASC  + naive R->L", None, lambda s: naive(reversed(list(s)))),
        ("index ASC  + sorted-asc", None, lambda s: naive(sorted(s))),
    ]
    vals = []
    print("FRAGILITY CONTROL (registration §4.2c) -- threshold %.2f" % G1_THRESHOLD)
    for name, tk, acc in combos:
        f1, _ = concentration(d, tie_key=tk, acc=acc)
        vals.append(f1)
        print("   %-26s %.17f" % (name, f1))
    spread = max(vals) - min(vals)
    margin = min(vals) - G1_THRESHOLD
    print("")
    print("   spread                 = %.3e" % spread)
    print("   margin above threshold = %.6f (%.2fx)" % (margin, min(vals) / G1_THRESHOLD))
    print("   spread / margin        = %.2e" % (spread / margin if margin else float("nan")))
    moved = (min(vals) < G1_THRESHOLD) != (max(vals) < G1_THRESHOLD)
    print("   VERDICT MOVES?         : %s" % ("YES -- THE GATE IS FRAGILE TO "
                                              "IMPLEMENTATION" if moved else
                                              "NO -- all combinations agree"))
    # distinctness, which is what makes D2 moot on this data
    print("   distinct density values: %d of %d" % (len(set(d)), len(d)))
    return 2 if moved else 0


# ---------------------------------------------------------------------------
# SELFTEST
# ---------------------------------------------------------------------------

def selftest():
    fails = []

    def check(name, cond, detail=""):
        if cond:
            print("  PASS  %s" % name)
        else:
            print("  FAIL  %s  %s" % (name, detail))
            fails.append(name)

    print("LIMB 1 -- D1: the top set is EXACTLY 1%% by COUNT, never plus-ties")
    d = [1.0] * 1000                      # every value tied
    top = top_set(d)
    check("all-tied field still yields exactly 10 of 1000", len(top) == 10,
          "got %d" % len(top))
    check("and D2 picks the LOWEST indices on a total tie",
          top == list(range(10)), str(top[:12]))

    print("LIMB 2 -- D2: the result is independent of input order")
    import random
    d2 = [random.Random(7).random() for _ in range(1000)]
    a = concentration(d2)[0]
    check("tie-break by descending index gives the same f1%",
          concentration(d2, tie_key=lambda i: -i)[0] == a)

    print("LIMB 3 -- D3: `concentration` ITSELF must use an exactly-rounded sum")
    # NOTE, recorded rather than quietly corrected: the FIRST version of this
    # limb asserted that `math.fsum` is order-independent -- a fact about the
    # standard library, not about this comparator.  A mutation replacing
    # `concentration`'s DEFAULT accumulator with a naive sum PASSED it.  The
    # limb now drives `concentration` on a field where the two answers differ,
    # so it tests the code under grading rather than the library beneath it.
    hard = [1e16] + [1.0] * 2000          # naive L->R loses every small term
    f1_hard, _ = concentration(hard)
    top_h = top_set(hard)
    ref = math.fsum(hard[i] for i in top_h) / math.fsum(hard)

    def _naive_sum(seq):
        t = 0.0
        for x in seq:
            t += x
        return t
    naive_ref = (_naive_sum(hard[i] for i in top_h) / _naive_sum(hard))
    check("the two accumulations really do differ on this field",
          ref != naive_ref, "fsum %.17g naive %.17g" % (ref, naive_ref))
    check("`concentration` returns the EXACTLY-ROUNDED value, not the naive one",
          f1_hard == ref and f1_hard != naive_ref,
          "got %.17g, fsum %.17g, naive %.17g" % (f1_hard, ref, naive_ref))

    print("LIMB 4 -- D4: a non-positive cell volume REFUSES")
    try:
        density([1.0, 2.0], [1.0, 0.0])
        check("zero volume is REFUSED", False, "it produced a density")
    except Refuse:
        check("zero volume is REFUSED", True)
    except ZeroDivisionError:
        # A crash is a fail signal, but the registered behaviour is a REFUSAL
        # naming the cell.  Reported as a distinct failure so a mutation that
        # removes the guard cannot be mistaken for one that keeps it.
        check("zero volume is REFUSED", False,
              "it raised ZeroDivisionError instead of refusing -- the D4 guard "
              "is not in the path")
    try:
        density([1.0, 2.0], [1.0, 2.0])
        check("positive volumes are accepted", True)
    except Refuse as e:
        check("positive volumes are accepted", False, str(e))

    print("LIMB 5 -- the planted zero")
    try:
        concentration([0.0] * 100)
        check("an all-zero density is REFUSED", False, "it was graded")
    except Refuse:
        check("an all-zero density is REFUSED", True)

    print("LIMB 6 -- G1 discriminates at the registered threshold")
    conc = [10.0] * 10 + [0.001] * 990
    diff = [1.0] * 1000
    check("a concentrated field clears 0.50", concentration(conc)[0] >= G1_THRESHOLD)
    check("a uniform field does not", concentration(diff)[0] < G1_THRESHOLD)
    check("a uniform field sits exactly at the null",
          abs(concentration(diff)[0] - 0.01) < 1e-12)

    print("LIMB 7 -- G2' exclusion is SYMMETRIC and fires on ANY zone")
    # Five synthetic cells-per-zone sets; put all mass in Z-DUCT and require
    # every OTHER zone to be excluded -- including Z-ELSEWHERE.
    pts = {"Z-DISK": (0.0665, 0.08, 0.0), "Z-DUCT": (0.15, 0.13, 0.0),
           "Z-HUB": (0.10, 0.02, 0.0), "Z-AXIS": (3.0, 0.01, 0.0),
           "Z-ELSEWHERE": (3.0, 2.0, 0.0)}
    for z in ZONES:
        check("zone_of maps the %s probe correctly" % z,
              A.zone_of(pts[z]) == z, "got %s" % A.zone_of(pts[z]))
    # SYMMETRY IS TESTED BY ROTATION, not by one arrangement.
    # NOTE, recorded rather than quietly corrected: the FIRST version of this
    # limb put all the mass in Z-DUCT once and required the other four to be
    # excluded.  A mutation that HARD-CODED Z-DISK and Z-AXIS to a share of
    # zero -- exactly the zone-specific special-casing the symmetric rule
    # forbids -- PASSED it, because those two were expected to be excluded
    # anyway.  The limb now makes EVERY zone the carrier in turn, so any zone
    # that cannot carry mass is caught.
    for carrier in ZONES:
        centres, vals = [], []
        for z in ZONES:
            for _ in range(200):
                centres.append(pts[z])
                vals.append(1.0 if z == carrier else 1e-12)
        nl = zone_nulls(centres)
        sh = zone_shares(vals, top_set(vals), centres)
        ok_carrier = not (sh[carrier] <= EXCLUSION_FACTOR * nl[carrier])
        others = [z for z in ZONES if z != carrier]
        ok_others = all(sh[z] <= EXCLUSION_FACTOR * nl[z] for z in others)
        check("with %s carrying: it is NOT excluded" % carrier, ok_carrier,
              "share %.4g null %.4g" % (sh[carrier], nl[carrier]))
        check("with %s carrying: the other four ARE excluded" % carrier,
              ok_others,
              str({z: round(sh[z], 6) for z in others}))

    print("LIMB 8 -- the commensurability falsifier can FAIL")
    times = [1, 2, 3]
    ok = {1: [1.0] * 10, 2: [2.0] * 10, 3: [3.0] * 10}
    okd = {1: 1.0, 2: 2.0, 3: 3.0}
    try:
        commensurability(ok, okd, times)
        check("a constant ratio passes", True)
    except Refuse as e:
        check("a constant ratio passes", False, str(e))
    bad = {1: [1.0] * 10, 2: [2.0] * 10, 3: [9.0] * 10}
    try:
        commensurability(bad, okd, times)
        check("a drifting ratio is REFUSED", False, "it passed")
    except Refuse:
        check("a drifting ratio is REFUSED", True)

    print("")
    if fails:
        print("SELFTEST REFUSED: %d check(s) failed: %s"
              % (len(fails), ", ".join(fails)))
        return 2
    print("SELFTEST PASS: all limbs fired on both sides.")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--fragility" in argv:
        i = argv.index("--fragility")
        return fragility(argv[i + 1], argv[i + 2], argv[i + 3])
    if len(argv) < 3:
        print(__doc__)
        print("usage: analyse_f28_h5b.py <runRoot> <V-field>")
        print("       analyse_f28_h5b.py --selftest")
        print("       analyse_f28_h5b.py --fragility <runRoot> <V-field> <time>")
        return 1
    return grade(argv[1], argv[2])


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Refuse as e:
        print("REFUSED (exit 2): %s" % e)
        sys.exit(2)
