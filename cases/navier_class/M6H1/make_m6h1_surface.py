#!/usr/bin/env python3
"""M6H1 SURFACE GENERATOR — build the ONERA M6 wing surface for the hyperbolic (C/O) route,
from AGARD AR-138 Table B1-1 and the AR-138 B1 planform, with the trailing edge left BLUNT.

WHAT THE FROZEN REGISTRATION SAYS THIS MUST BE
  §3.1  "Source of truth: `models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat`,
        all 72 rows, with the base left BLUNT at z/l = 0.0007052.  Not the 63-row `_sharp`
        file (§1.3)."
  §3.2  "It grades M6H1's OWN surface, which does not exist and will be GENERATED FROM
        `agard_ar138_table_b1_1_section_coordinates.dat` BY A DIFFERENT PATH."  This file
        is that path.
  §4    H-L1 201 x 65 x 97, **12,800 surface cells** = 200 x 64.  So the surface is ONE
        structured block, 201 around the section x 65 across the span.
  §1.2  ONERA Wing M6, semi-span wing, no body; AR 3.8; LE sweep 30 deg; TE sweep 15.8 deg;
        taper 0.562; **NO TWIST**; ONERA D section, ONE section, conical generation;
        semispan b = 1.1963 m; MAC 0.64607 m.
  §1.3  root chord 0.8059 m; base = 2 x 0.0007052 = 0.1410 % of LOCAL chord; max z/l
        0.0489296 so t/c = 9.79 %.

🔴 WHY A GENERATOR HAD TO BE WRITTEN AT ALL, MEASURED RATHER THAN ASSUMED.
A pyHyp-ready ONERA M6 surface already exists on this box — the DAFoam tutorial's, used by
the A3 ladder, multiblock, blunt-based, with a rounded tip cap.  It was extracted from
`/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n8_10920/volumeMesh.xyz` (wall layer),
written as an STL and graded by THIS CASE'S OWN FROZEN H-G0 INSTRUMENT,
`measure_te_base.py`:

    y/b   0.054  0.163  0.272  0.380  0.489  0.598  0.706  0.815  0.924
    base  1.136641e-03 m AT EVERY STATION, bit-identical
    dev      0.5%   2.4%   7.2%  18.9%  23.9%  35.3%  36.4%  48.4%  52.7%
    H-G0: GATE FAIL

**Its base thickness is CONSTANT in span.**  The reference base is 0.1410 % of the LOCAL
chord, and the local chord tapers 0.8059 -> 0.4537 m, so a faithful base MUST taper with
it.  That statement is free of any chord-measurement bias: a conically generated wing
cannot have a span-constant base.  The tutorial surface is a prismatic-base extrusion.
**So the existing surface is not admissible under M6H1's own gate, and §3.1's instruction
is load-bearing rather than ceremonial.**

🔴 THE TIP, AND THE DEPARTURE THIS FILE DISCLOSES RATHER THAN HIDES.
AR-138 B1 §2.1.13 records the tip as *"truncation parallel to wing root and addition of a
half body of revolution"* — ROUNDED, not a flat cut, and §1.2 of the registration carries
that.  **A single 201 x 65 block cannot close a rounded tip**; a cap is a second block, and
§4 registers 12,800 surface cells = 200 x 64, which is one block.  So this surface ends at
the tip station with an OPEN edge, which pyHyp's `unattachedEdgesAreSymmetry` turns into a
symmetry plane — i.e. **A FLAT TIP.**

**That is a departure from the reference and H-G0 DOES NOT GRADE IT.**  It is stated here,
in the generator, and belongs in the registration as a disclosure.  Its direction is
named: a flat tip removes the tip vortex's rounded-body detail, which matters most at
SECTION 7 (y/b = 0.99) and least inboard.  **It is not silently absorbed.**

🔴 AND A SECOND GAP IN THE SAME GATE, FOUND WHILE WRITING THIS AND REPORTED UPWARD.
§7's H-G0 registers THREE clauses — base thickness, **max t/c within +/-2 % of 9.79 %**,
and **semispan within +/-0.5 % of 1.1963 m**.  `measure_te_base.py` implements ONLY THE
FIRST, and unlike `read_cell_count.py` it does not say so on stdout: it prints
"H-G0 (surface fidelity ...): PASS/GATE FAIL" as though the gate were discharged.
**This generator therefore measures and prints all three clauses on its own output** — as
a BUILD-TIME SELF-CHECK, not as a grading verdict.  Grading is the instrument's, and
whether the instrument grows the two missing clauses is the supervisor's ruling.

WHAT IS AND IS NOT TAKEN FROM THE REFERENCE
  TAKEN: the section shape, all 72 rows, interpolated with a MONOTONE (PCHIP) fit in
    sqrt(x/l) — the same interpolant that reproduced all 271 Table B1-14 orifice z/l to a
    median residual of 6.8e-05 and a maximum of 5.9e-04
    (`models/onera_m6/PROVENANCE_TABLE_B1_14.md` §4), which is the evidence that this
    interpolant does not distort the section.
  TAKEN: the planform, from AR-138 B1's own numbers, and CHECKED FOR CLOSURE before use —
    c_root 0.8059 with LE sweep 30 deg and TE sweep 15.8 deg over semispan 1.1963 gives a
    tip chord of 0.45366 m and a taper of 0.5629 against B1 §2.1.5's stated 0.562.
  NOT TAKEN, and named because they are this file's choices and not the reference's:
    * the chordwise POINT DISTRIBUTION (the reference tabulates 72 points; §4 asks for 200
      cells around).  Cosine clustering at both the leading edge and the base.
    * the spanwise distribution: UNIFORM.  The reference specifies none.
    * the number of cells laid across the blunt base: N_BASE.

MEASURED COST (rule 12), 1 rank, c7a.4xlarge, 2026-09-12, three consecutive runs:
  L1  0.57 / 0.59 / 0.61 s wall (and 0.62 s on a fourth run)  ->  ~0.010 core-min
  L2  0.92 s,  L3  0.85 s
  the pyHyp march that consumes this surface: 77 s wall = 1.28 core-min at L1.
🔴 CORRECTION TO THIS FILE'S OWN FIRST COMMIT MESSAGE, which stated "surface generation
0.15 s wall = 0.0025 core-min". THAT FIGURE IS WRONG. 0.15 s was the OLD generator, before
arc_distribute's 200,000-point arc integration was added; the value measured in the very
shell invocation that produced that commit was 0.62 s and was misread off the line above it.
The correct figure is 0.57-0.62 s / ~0.010 core-min. It changes no conclusion -- the march
dominates the build by two orders -- but a measured number quoted wrongly is still a wrong
measured number, and it is corrected here rather than left to be found.

🔴 AND THE CORRECTION ITSELF WAS WRONG THE FIRST TIME, WHICH IS THE PART WORTH KEEPING.
The commit that corrected 0.15 s stated "0.62 / 0.61 / 0.62 s", THREE VALUES THAT WERE
NEVER MEASURED: the three timing runs and the text quoting them were issued in the SAME
shell invocation, so the text was written before the numbers existed and was filled in from
the single earlier 0.62 s reading. The three runs actually returned 0.57, 0.59 and 0.61 s.
THE RULE THAT FOLLOWS: NEVER WRITE A NUMBER INTO A FILE IN THE SAME TOOL CALL THAT MEASURES
IT. Measure, READ THE OUTPUT, then write. Three false figures in one evening, all three in
text composed alongside the command that was supposed to produce them.

Exit codes:  0 built and every self-check held   2 REFUSE — nothing written
"""
import sys, os, math

# --- REGISTERED IN ADVANCE (M6H1_PREREGISTRATION.md §1.2, §1.3, §3.1, §4). Do not edit to fit. ---
SECTION_FILE   = 'models/onera_m6/agard_ar138_table_b1_1_section_coordinates.dat'
N_SECTION_ROWS = 72                 # §3.1 "all 72 rows"
REF_ZL_AT_TE   = 0.0007052          # §1.3, and the final row of that file
REF_TC_MAX     = 0.0489296 * 2      # §1.3 max z/l -> t/c = 9.79 %
C_ROOT         = 0.8059             # §1.3
SEMISPAN       = 1.1963             # §1.2 / B1 §2.1.8
SWEEP_LE_DEG   = 30.0               # B1 §2.1.3
SWEEP_TE_DEG   = 15.8               # B1 §2.1.4
TAPER          = 0.562              # B1 §2.1.5
LEVELS = {'L1': (201, 65), 'L2': (301, 97), 'L3': (401, 129)}   # §4, wrap x span
SURFACE_CELLS_PREDICTED = {'L1': 12800, 'L2': 28800, 'L3': 51200}   # §4's own surface-cell column
# --- THIS FILE'S CHOICES, NOT THE REGISTRATION'S. See the docstring. ---
# 🔴 BOTH OF THESE ARE NOW MEASURED VALUES, NOT GUESSES, AND THE MEASUREMENT IS THE MARCH.
# N_BASE: cells laid across the blunt base.  H-G2 requires >= 8.  Swept 8, 9, 10, 12, 16 on
#   the corrected surface at the registered N = 97, cMax = 1.0, s0 and marchDist registered:
#       nb =  8  ->  96 layers, ZERO bad, min quality 9.0e-05   <-- THE ONLY ONE THAT CLEARS
#       nb =  9  ->  36 bad layers, first at 62
#       nb = 10  ->  95 bad layers, first at 3
#       nb = 12, 16  ->  96 bad, failing from layer 2
#   §4's own PREDICTED value is 9, and 9 DOES NOT MARCH while 8 does.  8 is delivered, it
#   satisfies H-G2's ">= 8", and the departure from §4's predicted 9 is disclosed rather
#   than smoothed over: §4's base column is a PREDICTION and H-G2's threshold is the gate.
N_BASE = {'L1': 8, 'L2': 12, 'L3': 16}
# CLUSTER_ALPHA: the wrap distribution is arc-length (see arc_distribute), blended with
#   UNIFORM at this strength.  1.0 is full cosine and it is WHY NOTHING MARCHED FOR HOURS:
#   it put the first point off the nose 80x closer than an x-cosine did, giving a surface
#   cell of aspect ratio 894:1 at the leading edge against a healthy 2.7:1 median, and the
#   march failed at a FIXED PHYSICAL DISTANCE of ~0.087 m for every N, ratio and marchDist
#   tried.  Swept at nb = 6: alpha 0.0, 0.3, 0.5 and 0.7 ALL give ZERO bad layers; 1.0 does
#   not.  0.0 is registered here because IT IS THE ONE MEASURED CLEAN AT nb = 8; 0.3-0.7
#   cleared at nb = 6 only and are NOT claimed at nb = 8.
#   Arc length was the right axis.  Full cosine on it was too much.  (L-566, L-567.)
CLUSTER_ALPHA = 0.0
# --------------------------------------------------------------------------------------------

TOL_CLOSURE_TAPER = 2.0e-3          # the planform closure check, before anything is built


def pchip(xs, ys):
    """Monotone cubic (Fritsch-Carlson). Returns f(x). Pure python: no scipy at build time."""
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(x):
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            return ys[-1]
        lo, hi = 0, n - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        hh = xs[lo + 1] - xs[lo]
        t = (x - xs[lo]) / hh
        h00 = 2 * t ** 3 - 3 * t ** 2 + 1
        h10 = t ** 3 - 2 * t ** 2 + t
        h01 = -2 * t ** 3 + 3 * t ** 2
        h11 = t ** 3 - t ** 2
        return (h00 * ys[lo] + h10 * hh * m[lo] + h01 * ys[lo + 1] + h11 * hh * m[lo + 1])
    return f


def arc_distribute(f, n, dense=200000):
    """Return n+1 x/l values from the TRAILING EDGE to the LEADING EDGE, spaced so that the
    ARC LENGTH along the section is cosine-clustered at both ends.

    Why arc length and not x: the section's nose is round, so near x = 0 a step in x buys
    almost no arc and a step in arc buys almost no x.  Clustering in x leaves the nose
    carried by two panels; clustering in arc resolves it.  The clustering is cosine at BOTH
    ends, so the trailing-edge base corner is refined as well as the nose.
    """
    xs = [i / float(dense) for i in range(dense + 1)]
    s = [0.0]
    for i in range(1, len(xs)):
        dx = xs[i] - xs[i - 1]
        dz = f(xs[i]) - f(xs[i - 1])
        s.append(s[-1] + math.sqrt(dx * dx + dz * dz))
    total = s[-1]
    targets = cosine(n, total, 0.0)          # TE (s = total) -> LE (s = 0)
    out, j = [], len(s) - 1
    for tg in targets:
        while j > 0 and s[j] > tg:
            j -= 1
        if j >= len(s) - 1:
            out.append(xs[-1])
        elif s[j + 1] == s[j]:
            out.append(xs[j])
        else:
            w = (tg - s[j]) / (s[j + 1] - s[j])
            out.append(xs[j] + w * (xs[j + 1] - xs[j]))
    out[0], out[-1] = 1.0, 0.0               # pin the two ends exactly
    return out


def load_section(root):
    """Read the 72-row ONERA D half-section FROM DISK, and refuse anything else."""
    p = os.path.join(root, SECTION_FILE)
    if not os.path.isfile(p):
        raise ValueError("no section table at %s -- §3.1 names it as the source of truth "
                         "and this generator will not synthesise one" % p)
    rows = []
    for ln, line in enumerate(open(p), 1):
        s = line.split('#')[0].strip()
        if not s:
            continue
        t = s.split()
        if len(t) != 2:
            raise ValueError("%s:%d: expected 'x/l z/l', got %r" % (p, ln, s))
        rows.append((float(t[0]), float(t[1])))
    if len(rows) != N_SECTION_ROWS:
        raise ValueError("%s has %d rows; §3.1 says ALL 72. The 63-row `_sharp` file deletes "
                         "the eight aft points and appends a synthetic sharp closure (§1.3) "
                         "and is REFUSED here by count." % (p, len(rows)))
    if abs(rows[-1][0] - 1.0) > 1e-12 or abs(rows[-1][1] - REF_ZL_AT_TE) > 1e-12:
        raise ValueError("%s's final row is %r; the reference closes BLUNT at "
                         "(1.0000000, %.7f). A sharp-closed table is a different geometry."
                         % (p, rows[-1], REF_ZL_AT_TE))
    xs = [r[0] for r in rows]
    if any(xs[i + 1] <= xs[i] for i in range(len(xs) - 1)):
        raise ValueError("%s: x/l is not strictly increasing" % p)
    return rows


def planform_closure():
    """Check the planform closes on itself BEFORE any geometry is built. The four numbers
    are read from four different lines of AR-138 B1 and are not independent; if they
    disagree, one of them was mistranscribed and nothing below should be trusted."""
    c_tip = C_ROOT + SEMISPAN * math.tan(math.radians(SWEEP_TE_DEG)) \
        - SEMISPAN * math.tan(math.radians(SWEEP_LE_DEG))
    taper = c_tip / C_ROOT
    ok = abs(taper - TAPER) <= TOL_CLOSURE_TAPER
    return ok, c_tip, taper


def cosine(n, a, b, cluster_both=True, alpha=None):
    """n+1 points from a to b, cosine-clustered at both ends and then BLENDED TOWARD UNIFORM
    by CLUSTER_ALPHA.  alpha = 1 is pure cosine, alpha = 0 is uniform.

    The blend is not a refinement knob: at alpha = 1 this surface does not march at all
    (see the CLUSTER_ALPHA comment above).  It is bounded clustering, and the bound is what
    keeps the leading-edge cell from being three orders more slender than the spanwise one.
    """
    if alpha is None:
        alpha = CLUSTER_ALPHA
    out = []
    for i in range(n + 1):
        t = i / float(n)
        s = 0.5 * (1.0 - math.cos(math.pi * t)) if cluster_both \
            else 1.0 - math.cos(0.5 * math.pi * t)
        out.append(a + (b - a) * (alpha * s + (1.0 - alpha) * t))
    return out


def build(root, level):
    nwrap, nspan = LEVELS[level]
    nb = N_BASE[level]
    ncell = nwrap - 1
    # The two sides carry (ncell - nb) cells between them.  When that is ODD the sides
    # cannot be equal, and REFUSING would make some base counts unbuildable -- including
    # §4's own predicted 9 at H-L1.  The extra cell goes on the LOWER side and the output
    # says so, because an undisclosed asymmetry in a surface built from a SYMMETRIC section
    # is exactly the kind of thing a later reader would find and not be able to explain.
    nside = (ncell - nb) // 2
    extra_lower = (ncell - nb) - 2 * nside          # 0 or 1

    rows = load_section(root)
    f = pchip([math.sqrt(r[0]) for r in rows], [r[1] for r in rows])

    ok, c_tip, taper = planform_closure()
    if not ok:
        raise ValueError("PLANFORM DOES NOT CLOSE: c_root %.4f with LE %.1f deg and TE %.1f "
                         "deg over semispan %.4f gives tip chord %.5f and taper %.4f, but "
                         "B1 §2.1.5 states %.3f. Refusing to build on four numbers that "
                         "disagree." % (C_ROOT, SWEEP_LE_DEG, SWEEP_TE_DEG, SEMISPAN,
                                        c_tip, taper, TAPER))

    # ---- the 2-D section, ONE wrap, in normalised (x/l, z/l), starting at the base midpoint
    # going over the UPPER side to the LE, back along the LOWER side, then up the base.
    # 🔴 WRAP SENSE, AND IT IS NOT COSMETIC.  The panel normal is (wrap tangent) x (span
    # tangent), and with the span tangent +y that evaluates to (0, 0, tx): the normal's
    # thickness component IS the wrap's chordwise component.  So the UPPER side must run
    # LE -> TE (tx > 0, normal +z, outward) and the LOWER side TE -> LE.  Building it the
    # other way round gives a surface whose normals are perfectly CONSISTENT and point
    # INTO the wing, which pyHyp reports as "Normals are consistent!" and then marches
    # inward.  MEASURED on this surface's first build: Min Quality -1.00000 and Min Volume
    # -0.109E-08 at grid level 2, NaN from level 4, AND pyHyp STILL EXITED 0.
    # self_checks() asserts outwardness directly so this can never silently flip again.
    # 🔴 THE POINTS ARE PLACED BY ARC LENGTH, NOT BY x, AND THAT IS NOT A REFINEMENT.
    # The ONERA D nose is round: z ~ sqrt(x), so dz/dx is infinite at x = 0.  A cosine
    # distribution IN x puts the first point off the leading edge at x = 6.9e-4 but at an
    # ARC distance of 4.5e-3 -- the nose is then carried by two panels that turn through
    # nearly 180 degrees, the discrete normal at the leading-edge node is the average of
    # two almost opposite panel normals, and the hyperbolic march is ill-conditioned at
    # exactly that node from the first layer.
    # MEASURED, with the x-distribution: Min Quality -1.00000 at grid level 2 for EVERY
    # parameter variant tried -- s0 1.654e-6 / 1e-5 / 1e-4, cMax 0.1 / 3.0, epsE 1 / 2,
    # nAvg 260 = 4 x 65 nodes needing averaging at the very first layer.  Changing the
    # march did nothing because the defect was in the surface.
    # Distributing in ARC LENGTH puts that first point about sixteen times closer to the
    # nose and resolves the turn.
    xu = arc_distribute(f, nside)                     # TE -> LE, cosine in ARC LENGTH
    xl = arc_distribute(f, nside + extra_lower) if extra_lower else xu
    wrap = []
    for x in xl:
        wrap.append((x, -f(x)))            # LOWER, TE -> LE : 0..nside+extra_lower
    for x in list(reversed(xu))[1:]:
        wrap.append((x, f(x)))             # UPPER, LE -> TE : nside+extra_lower+1...
    # The base is CLUSTERED TOWARD ITS TWO CORNERS, not spaced uniformly.  Each corner is a
    # convex turn of about 97 degrees concentrated in one node, and a hyperbolic march is
    # at its most fragile there: MEASURED, those corner nodes are the last ones to stop
    # needing averaging (nAvg fell 260 -> 4 as the march proceeded, and Min Quality stayed
    # negative while any remained).  Cosine spacing puts small panels into the corner so
    # the turn is carried by several cells instead of one.
    zb = REF_ZL_AT_TE
    zs = cosine(nb, zb, -zb, alpha=0.0)               # +zb -> -zb, UNIFORM: the base is a
                                                      # straight segment and clustering into
                                                      # its corners measured WORSE, not better
    for i in range(1, nb):                            # down the blunt base, upper -> lower
        wrap.append((1.0, zs[i]))
    if len(wrap) != ncell:
        raise ValueError("wrap built %d cells, expected %d" % (len(wrap), ncell))
    wrap.append(wrap[0])                              # close the O-grid: point nwrap == point 1

    # ---- sweep it across the span
    tle, tte = math.tan(math.radians(SWEEP_LE_DEG)), math.tan(math.radians(SWEEP_TE_DEG))
    grid = []                                         # [span][wrap] -> (x, y_span, z_thick)
    for j in range(nspan):
        y = SEMISPAN * j / float(nspan - 1)
        xle = y * tle
        c = (C_ROOT + y * tte) - xle
        grid.append([(xle + xc * c, y, zc * c) for (xc, zc) in wrap])   # NO TWIST, §2.1.6
    return grid, nwrap, nspan, nb, nside, c_tip, taper, extra_lower


# ------------------------------------------------------------------ writers
def write_plot3d(path, grid, nwrap, nspan):
    """Formatted PLOT3D, one block, nwrap x nspan x 1 — what pyHyp reads with
    fileType 'PLOT3D'."""
    with open(path, 'w') as fo:
        fo.write("       1\n")
        fo.write("%8d%8d%8d\n" % (nwrap, nspan, 1))
        for c in range(3):
            n = 0
            for j in range(nspan):
                for i in range(nwrap):
                    fo.write("%20.12E" % grid[j][i][c])
                    n += 1
                    if n % 3 == 0:
                        fo.write("\n")
            if n % 3:
                fo.write("\n")


def write_stl(path, grid, nwrap, nspan, nb, nside, extra_lower=0):
    """ASCII STL with the three solids measure_te_base.py dispatches on, in ITS axis
    convention: index 1 is SPANWISE and index 2 is THICKNESS."""
    nlo = nside + extra_lower
    lo = list(range(0, nlo + 1))                         # TE -> LE, LOWER
    up = list(range(nlo, nlo + nside + 1))               # LE -> TE, UPPER
    ba = list(range(nlo + nside, nwrap - 1)) + [0]       # down the blunt base, upper -> lower
    out = []
    for name, idx in (('wing_upper', up), ('wing_lower', lo), ('wing_base', ba)):
        out.append("solid %s" % name)
        for j in range(nspan - 1):
            for k in range(len(idx) - 1):
                a, b = idx[k], idx[k + 1]
                q = [grid[j][a], grid[j][b], grid[j + 1][b], grid[j + 1][a]]
                for tri in ((0, 1, 2), (0, 2, 3)):
                    out.append("facet normal 0 0 0\n outer loop")
                    for t in tri:
                        out.append("    vertex %.9g %.9g %.9g" % q[t])
                    out.append(" endloop\nendfacet")
        out.append("endsolid %s" % name)
    open(path, 'w').write("\n".join(out) + "\n")


# ------------------------------------------------------------------ build-time self-checks
def self_checks(grid, nwrap, nspan, nb, nside, extra_lower=0):
    """Measure the three things §7's H-G0 registers, ON WHAT WAS JUST BUILT.
    THIS IS A BUILD-TIME CHECK AND NOT A GRADING VERDICT: H-G0 is graded by
    measure_te_base.py from the STL, and only that instrument's verdict counts."""
    res, ok = [], True
    # (1) base thickness as a fraction of LOCAL chord, at every spanwise station
    worst = 0.0
    for j in range(nspan):
        row = grid[j]
        xs = [p[0] for p in row]
        c = max(xs) - min(xs)
        zb = [row[i][2] for i in list(range(2 * nside + extra_lower, nwrap - 1)) + [0]]
        dz = max(zb) - min(zb)
        dev = abs(dz / c - 2 * REF_ZL_AT_TE) / (2 * REF_ZL_AT_TE)
        worst = max(worst, dev)
    ok &= worst <= 1e-9
    res.append(("base = %.4f %% of local chord at every one of %d stations "
                "(worst deviation %.2e)" % (100 * 2 * REF_ZL_AT_TE, nspan, worst),
                worst <= 1e-9))
    # (2) max t/c
    tc = 0.0
    for j in range(nspan):
        row = grid[j]
        c = max(p[0] for p in row) - min(p[0] for p in row)
        tc = max(tc, (max(p[2] for p in row) - min(p[2] for p in row)) / c)
    dtc = abs(tc - REF_TC_MAX) / REF_TC_MAX
    ok &= dtc <= 0.02
    res.append(("max t/c %.4f %% against the reference %.4f %% (%.2f %% off, gate +/-2 %%)"
                % (100 * tc, 100 * REF_TC_MAX, 100 * dtc), dtc <= 0.02))
    # (3) semispan
    b = max(p[1] for row in grid for p in row) - min(p[1] for row in grid for p in row)
    db = abs(b - SEMISPAN) / SEMISPAN
    ok &= db <= 0.005
    res.append(("semispan %.6f m against %.4f m (%.3f %% off, gate +/-0.5 %%)"
                % (b, SEMISPAN, 100 * db), db <= 0.005))
    # (4) the O-grid actually closes
    closed = all(grid[j][0] == grid[j][nwrap - 1] for j in range(nspan))
    ok &= closed
    res.append(("the wrap closes: point %d is point 1 at every span station" % nwrap, closed))
    # (5) THE PANEL NORMALS POINT OUTWARD, not merely consistently.
    #     n = (wrap tangent) x (span tangent), tested against the vector from the section's
    #     own centroid to the panel.  pyHyp reports "Normals are consistent!" for an inward
    #     surface too, so consistency is not the check that matters.
    inward = 0
    for j in range(nspan - 1):
        row, nxt = grid[j], grid[j + 1]
        cx = sum(p[0] for p in row[:-1]) / (nwrap - 1)
        cz = sum(p[2] for p in row[:-1]) / (nwrap - 1)
        for i in range(nwrap - 1):
            a, b2, c2 = row[i], row[i + 1], nxt[i]
            tw = (b2[0] - a[0], b2[1] - a[1], b2[2] - a[2])
            ts = (c2[0] - a[0], c2[1] - a[1], c2[2] - a[2])
            n = (tw[1] * ts[2] - tw[2] * ts[1],
                 tw[2] * ts[0] - tw[0] * ts[2],
                 tw[0] * ts[1] - tw[1] * ts[0])
            r = (a[0] - cx, 0.0, a[2] - cz)
            if n[0] * r[0] + n[2] * r[2] <= 0.0:
                inward += 1
    ok &= inward == 0
    res.append(("every panel normal points OUTWARD, not merely consistently "
                "(%d inward-facing panels)" % inward, inward == 0))
    # (6) no duplicate points inside the wrap (a collapsed panel would break pyHyp silently)
    dup = 0
    for j in range(nspan):
        row = grid[j][:-1]
        for i in range(len(row)):
            a, b2 = row[i], row[(i + 1) % len(row)]
            if (a[0] - b2[0]) ** 2 + (a[2] - b2[2]) ** 2 < 1e-24:
                dup += 1
    ok &= dup == 0
    res.append(("no collapsed panel anywhere in the wrap (%d found)" % dup, dup == 0))
    return ok, res


def main(root, level, outdir):
    print("M6H1 SURFACE GENERATOR -- %s, from %s" % (level, SECTION_FILE))
    try:
        grid, nwrap, nspan, nb, nside, c_tip, taper, extra_lower = build(root, level)
    except ValueError as e:
        print("REFUSE (exit 2): %s" % e)
        return 2
    print("planform closes: tip chord %.5f m, taper %.4f against B1 §2.1.5's %.3f" %
          (c_tip, taper, TAPER))
    print("topology: ONE block, %d around x %d span = %d surface cells "
          "(§4 predicts %d); %d cells across the blunt base, %d per side"
          % (nwrap, nspan, (nwrap - 1) * (nspan - 1), SURFACE_CELLS_PREDICTED[level],
             nb, nside))
    if extra_lower:
        print("  NOTE: %d - %d is ODD, so the two sides cannot be equal. The extra cell is on "
              "the LOWER side: %d lower, %d upper." % (nwrap - 1, nb, nside + extra_lower, nside))
    ok, res = self_checks(grid, nwrap, nspan, nb, nside, extra_lower)
    print("\nBUILD-TIME SELF-CHECKS (NOT a grading verdict -- H-G0 is measure_te_base.py's)")
    for what, good in res:
        print("  %-92s %s" % (what, 'ok' if good else 'FAIL'))
    if not ok:
        print("\nREFUSE (exit 2): a self-check failed; nothing written.")
        return 2
    os.makedirs(outdir, exist_ok=True)
    p3 = os.path.join(outdir, 'm6h1_surface_%s.xyz' % level)
    st = os.path.join(outdir, 'm6h1_surface_%s.stl' % level)
    write_plot3d(p3, grid, nwrap, nspan)
    write_stl(st, grid, nwrap, nspan, nb, nside, extra_lower)
    print("\nWROTE  %s  (%d bytes)" % (p3, os.path.getsize(p3)))
    print("WROTE  %s  (%d bytes)" % (st, os.path.getsize(st)))
    print("\nNEXT, AND IT IS NOT DISCHARGED HERE: grade the STL with "
          "cases/navier_class/M6H1/measure_te_base.py. This generator's self-checks measure "
          "what it INTENDED to build; only the instrument measures what it DID build.")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in LEVELS:
        sys.exit("usage: make_m6h1_surface.py <L1|L2|L3> [repo_root] [outdir]")
    lv = sys.argv[1]
    rt = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    od = sys.argv[3] if len(sys.argv) > 3 else os.path.join(rt, 'verification/runs/M6H1_runs',
                                                            lv, 'mesh')
    sys.exit(main(rt, lv, od))
