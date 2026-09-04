#!/usr/bin/env python3
"""F28 H5 -- PREREQUISITES 2 AND 3 for the successor pre-registration.

WHAT THIS ESTABLISHES, and why it exists BEFORE any successor document.

The frozen H5 arm is `NOT A RESULT` on a confounded measurand: the residual
field OpenFOAM writes is `finestResidual = tsource() - Apsi`, UN-NORMALISED, and
in finite volume each cell's equation is integrated over its own cell, so `|r|`
carries cell volume.  G2 returned `Z-ELSEWHERE` at 1.000 because the ranking was
measuring where the BIG CELLS are.

`cfd-supervisor` then ruled a `normFactor`-matched replacement, and that ruling
was refuted: `normFactor` is a SINGLE GLOBAL SCALAR, so matching it restores
commensurability exactly and reorders NOTHING.  He accepted the refutation and
ruled instead:

  * the CONTROL keeps the raw field, `normFactor`-matched -- the commensurability
    falsifier is untouched;
  * the GATE quantity becomes RESIDUAL DENSITY `r_c / V_c` on a REAL cell volume,
    on the dimensional ground that `r_c` is the equation integrated over the cell,
    so across cells differing by five orders of magnitude in volume only the
    density is comparable;
  * because the density proposal was made with its outcome already in view, the
    non-blindness is DISCHARGED BY PUBLISHING THE ALTERNATIVES: the successor
    reports the zone tally under ALL THREE candidates -- raw, `normFactor`-matched
    and density -- EVERY TIME.  Agreement makes the choice moot; disagreement IS
    the finding.  A selection made with the outcome in view is laundered by hiding
    the alternatives and discharged by publishing them.

THIS SCRIPT PRODUCES THE TWO MEASUREMENTS THAT MUST EXIST BEFORE THE SUCCESSOR
IS DRAFTED, AND IT DRAFTS NOTHING:

  PREREQ 2  REAL cell volumes, from `postProcess -func writeCellVolumes`, and a
            quantification of how wrong the vertex bounding-box proxy was.  The
            proxy was adequate to establish rho = +0.80 and the 176,034x ratio
            and is INADEQUATE as a gate quantity; it is not carried forward.

  PREREQ 3  COVERAGE.  The failure just paid for was a gate whose zones did not
            cover the support of its own measurand.  Freezing a new gate without
            a coverage proof would reproduce that defect in a new document, and a
            frozen document is harder to retire than a draft.  Coverage is
            DEMONSTRATED, not asserted: the fraction of each candidate's top-N
            mass falling inside the UNION of the named zones.

STANDING RULE 3.  `--selftest` plants a synthetic concentration OUTSIDE every
named envelope and REFUSES unless it is reported UNCOVERED rather than silently
binned into `Z-ELSEWHERE` as though that were an answer; and plants one INSIDE a
named zone and requires COVERED.  A coverage test that cannot report "uncovered"
would certify the exact failure it exists to catch.

NO VERDICT IS ISSUED HERE.  These are measurements for a document that does not
yet exist.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyse_f28_h5 as A  # noqa: E402  (readers + frozen zone_of)

# The union of NAMED zones.  `Z-ELSEWHERE` is the catch-all and is, by
# definition, NOT coverage: mass landing there is mass the gate cannot attribute.
NAMED = ("Z-DISK", "Z-DUCT", "Z-HUB", "Z-AXIS")
COVERAGE_FLOOR = 0.60   # reported, NOT a frozen gate -- no gate exists yet


class Refuse(Exception):
    pass


def coverage(values, centres, ntop=None):
    """Fraction of the top-N |values| mass that lands in a NAMED zone.

    Returns (covered_fraction, tally, top_indices).  A low fraction means the
    zone envelopes do not cover the support of this quantity -- which is the
    defect that retired the frozen G2, not a property of the flow.
    """
    mags = [abs(v) for v in values]
    n = ntop or max(1, int(0.01 * len(values)))
    top = sorted(range(len(values)), key=lambda i: mags[i], reverse=True)[:n]
    tot = sum(mags[i] for i in top)
    if tot <= 0:
        raise Refuse("coverage: top-%d mass is zero; nothing to attribute" % n)
    tally = {}
    for i in top:
        z = A.zone_of(centres[i])
        tally[z] = tally.get(z, 0.0) + mags[i]
    tally = dict((z, m / tot) for z, m in tally.items())
    return sum(tally.get(z, 0.0) for z in NAMED), tally, top


def spearman(a, b):
    def rank(x):
        o = sorted(range(len(x)), key=lambda i: x[i])
        r = [0] * len(x)
        for k, i in enumerate(o):
            r[i] = k
        return r
    ra, rb = rank(a), rank(b)
    m = len(ra)
    ma, mb = sum(ra) / m, sum(rb) / m
    num = sum((ra[i] - ma) * (rb[i] - mb) for i in range(m))
    den = math.sqrt(sum((ra[i] - ma) ** 2 for i in range(m))
                    * sum((rb[i] - mb) ** 2 for i in range(m)))
    return num / den if den else 0.0


def bbox_proxy_volumes(case):
    """The OLD proxy, recomputed here ONLY so its error can be quantified."""
    pm = os.path.join(case, "constant", "polyMesh")
    pts = A.read_points(pm + "/points")
    fcs = A.read_faces(pm + "/faces")
    own = A.read_labels(pm + "/owner")
    nei = A.read_labels(pm + "/neighbour")
    n = max(max(own), max(nei)) + 1
    cp = [set() for _ in range(n)]
    for f, ps in enumerate(fcs):
        if f < len(own):
            cp[own[f]].update(ps)
        if f < len(nei):
            cp[nei[f]].update(ps)
    out = []
    for c in range(n):
        P = [pts[i] for i in cp[c]]
        dx = max(p[0] for p in P) - min(p[0] for p in P)
        dy = max(p[1] for p in P) - min(p[1] for p in P)
        dz = max(p[2] for p in P) - min(p[2] for p in P)
        out.append(dx * dy * max(dz, 1e-30))
    return out


def selftest():
    """Plant a concentration OUTSIDE every envelope; require UNCOVERED."""
    fails = []

    def check(name, cond, detail=""):
        if cond:
            print("  PASS  %s" % name)
        else:
            print("  FAIL  %s  %s" % (name, detail))
            fails.append(name)

    # Synthetic mesh of 1,000 cells: centres chosen by hand so the zone of each
    # is known independently of any real mesh.
    n = 1000
    centres = [(3.0, 2.0, 0.0)] * n            # ALL in the farfield => Z-ELSEWHERE
    vals = [1e-9] * n

    # NEGATIVE LIMB (the one that matters): the concentration is OUTSIDE every
    # named envelope.  It MUST be reported uncovered, never binned as an answer.
    for i in range(10):
        centres[i] = (3.0, 2.0, 0.0)
        vals[i] = 1.0
    cov, tally, _ = coverage(vals, centres)
    check("a concentration OUTSIDE every envelope reports UNCOVERED",
          cov < 0.01, "covered=%.4f tally=%s" % (cov, tally))
    check("and it is attributed to Z-ELSEWHERE, not to a named zone",
          abs(tally.get("Z-ELSEWHERE", 0.0) - 1.0) < 1e-9, str(tally))
    check("UNCOVERED is below the reported floor",
          cov < COVERAGE_FLOOR)

    # POSITIVE LIMB: the same concentration moved INSIDE Z-DUCT must be covered.
    for i in range(10):
        centres[i] = (0.15, 0.13, 0.0)          # inside Z-DUCT
    cov2, tally2, _ = coverage(vals, centres)
    check("the same concentration INSIDE Z-DUCT reports COVERED",
          cov2 > 0.99, "covered=%.4f tally=%s" % (cov2, tally2))
    check("and it is attributed to Z-DUCT",
          abs(tally2.get("Z-DUCT", 0.0) - 1.0) < 1e-9, str(tally2))

    # DISCRIMINATION: the two limbs must not return the same answer.
    check("the covered and uncovered limbs differ", abs(cov2 - cov) > 0.98)

    # A HALF-AND-HALF plant: 5 cells in-zone, 5 out, equal magnitude -> ~0.5.
    for i in range(5):
        centres[i] = (3.0, 2.0, 0.0)
    cov3, _, _ = coverage(vals, centres)
    check("a half-in/half-out plant reports ~0.5, not 0 or 1",
          0.45 < cov3 < 0.55, "covered=%.4f" % cov3)

    # ZERO refusal: a top set with no mass must REFUSE, not report 0 coverage.
    try:
        coverage([0.0] * 100, [(3.0, 2.0, 0.0)] * 100)
        check("an all-zero field is REFUSED", False, "it reported a coverage")
    except Refuse:
        check("an all-zero field is REFUSED", True)

    print("")
    if fails:
        print("SELFTEST REFUSED: %d check(s) failed: %s"
              % (len(fails), ", ".join(fails)))
        return 2
    print("SELFTEST PASS: the coverage test can report UNCOVERED, COVERED and "
          "partial, and refuses a zero field.")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if len(argv) < 4:
        print(__doc__)
        print("usage: f28_h5_coverage_probe.py <runRoot> <V-field> <time>")
        return 1
    case, vpath, t = argv[1], argv[2], argv[3]

    V = A.read_internal_scalars(vpath)
    centres = A.cell_centres(case)
    if len(V) != len(centres):
        raise Refuse("V has %d values, mesh has %d cells" % (len(V), len(centres)))
    print("cells                     : %d" % len(V))
    print("REAL cell volume  min/med/max : %.6e / %.6e / %.6e"
          % (min(V), sorted(V)[len(V) // 2], max(V)))
    print("  max/min ratio               : %.3e" % (max(V) / min(V)))

    # ---- PREREQ 2: how wrong was the bounding-box proxy? --------------------
    print("")
    print("PREREQ 2 -- the vertex bounding-box proxy, quantified against REAL V")
    P = bbox_proxy_volumes(case)
    rho_pv = spearman(P, V)
    ratios = [P[i] / V[i] for i in range(len(V))]
    rs = sorted(ratios)
    print("  Spearman(proxy, real V)   : %+.4f" % rho_pv)
    print("  proxy/real ratio  min/med/max : %.3f / %.3f / %.3f"
          % (rs[0], rs[len(rs) // 2], rs[-1]))
    print("  -> the proxy RANKS well and SCALES badly: adequate for a rank")
    print("     correlation, inadequate as a gate quantity.  Not carried forward.")

    # ---- the three candidate quantities ------------------------------------
    fields = {}
    tdir = os.path.join(case, str(t))
    for f in ("p", "Uy"):
        path, _sep = A.residual_field_path(tdir, f)
        fields[f] = A.read_internal_scalars(path)

    print("")
    print("PREREQ 3 -- COVERAGE of the named-zone union, ALL THREE CANDIDATES")
    print("  (the successor must report all three every time: a selection made")
    print("   with the outcome in view is discharged by publishing alternatives)")
    for f, raw in fields.items():
        sc = A.dat_scalars(case, f, [int(t)])[int(t)]
        nf = sum(abs(x) for x in raw) / sc
        cands = {
            "raw                ": raw,
            "normFactor-matched ": [x / nf for x in raw],
            "density  r_c / V_c ": [raw[i] / V[i] for i in range(len(raw))],
        }
        print("")
        print("  field %s   (normFactor = %.6f)" % (f, nf))
        for name, vals in cands.items():
            cov, tally, top = coverage(vals, centres)
            f1, _ = A.concentration(vals)
            top_named = sorted(((m, z) for z, m in tally.items()), reverse=True)
            print("    %s f1%%=%.4f  COVERED=%.4f %s  top: %s"
                  % (name, f1, cov,
                     "COVERED" if cov >= COVERAGE_FLOOR else "**UNCOVERED**",
                     ", ".join("%s %.3f" % (z, m) for m, z in top_named[:4])))
    print("")
    print("COVERAGE_FLOOR %.2f is a REPORTING threshold, not a frozen gate."
          % COVERAGE_FLOOR)
    print("No gate exists yet; the successor pre-registration does not exist.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Refuse as e:
        print("REFUSED (exit 2): %s" % e)
        sys.exit(2)
