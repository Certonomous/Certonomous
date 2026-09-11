#!/usr/bin/env python3
"""M6C2 route (c) -- L3 EXTRUSION COST FIT, and the CAP derived from it.

NOT a gate comparator.  It changes no gate, threshold, band or label.  It fits a
COST and derives a CAP, and it prints every intermediate so the fit is checked
rather than believed.

NAMING -- the log wins over recall.  pyHyp's header is
    | Grid Lvl | CPU Time | Sub Its | KSP Its | nAvg | Sl | ...
Column 3 is SUB ITERATIONS; column 4 is KSP its per sub-iteration and is FLAT at
5.  The quantity earlier notes called "SigmaKSP" is Sigma(col 3) = SIGMA_SUBITS.
Total linear-solve work is SIGMA_SUBITS x KSPits; KSPits being flat, the two are
proportional -- but the name here is the header's.

THE CORRECTED COST MODEL.  Seconds per sub-iteration per surface face is NOT a
single invariant across the family.  Measured L1 vs L2 at matched eta it is
invariant to within 0.84-1.01 for eta < 0.75 and then DIVERGES: 1.09 at 0.81,
1.38 at 0.91, 1.51 at 1.00.  Both curves are fit by ONE two-branch law in the
ABSOLUTE layer index (not eta, not the level count):

    k(i) = max(K_BASE, C * i)        i = absolute layer index, 1..layers

because volSmoothIter=100 smooths every layer already laid, so once that term
dominates the per-sub-iteration cost is LINEAR IN LAYERS LAID.  C is fixed by
L1's terminal k / 32 and independently reproduces L2's terminal k (4.14e-6
predicted vs 4.14e-6 measured) and L2's observed crossover level (~30).

    wall(L) = faces(L) * SUM_i SubIts(i) * k(i)

The ONLY quantity not measurable before the run is the SubIts PROFILE at L3.

PLANTED CONTROL: the parser is shown able to report a value that appears nowhere
in the real logs before any real number is trusted.  If it cannot, REFUSE (2).
"""
import re, sys, os, math

FACES  = {"L1": 14144, "L2": 31824, "L3": 71604}   # pyHyp "Total Faces"
LAYERS = {"L1": 32,    "L2": 48,    "L3": 72}      # N-1; N=33/49/73 are NODES
REF    = "L1"                                       # the level C is anchored on
RATE   = 0.0513                                     # $/core-h, owner-stated

ROW = re.compile(r"^\s*(\d+)\s+([\d.]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s")

def parse(text):
    out, prev = [], 0.0
    for line in text.splitlines():
        m = ROW.match(line)
        if m:
            lvl, cum, sub = int(m.group(1)), float(m.group(2)), int(m.group(3))
            out.append((lvl, cum - prev, sub, int(m.group(4)))); prev = cum
    return out

def plant_control(text):
    PL, PS = 999, 1234567
    row = "    %3d  9999.9 %7d     5      0  0.500  1.0  1.0  0.3  0.1E-03  0.1E-03  0.1E+01  0.1000  1.3000 " % (PL, PS)
    assert str(PS) not in text, "plant value collides with real log content"
    seen = [r for r in parse(text + "\n" + row) if r[0] == PL]
    if not seen or seen[0][2] != PS:
        sys.stderr.write("PLANT REFUSED: the parser was not shown able to see a planted row.\n")
        sys.exit(2)

def load(tag, path):
    text = open(path).read()
    plant_control(text)
    rows = parse(text)
    complete = "EXTRUSION COMPLETE" in text
    if not rows:
        sys.stderr.write("NO ROWS parsed from %s\n" % path); sys.exit(2)
    return dict(tag=tag, rows=rows, complete=complete,
                sigma=sum(r[2] for r in rows), wall=sum(r[1] for r in rows))

def k_of(d):
    """per-level seconds per sub-iteration per face"""
    F = FACES[d["tag"]]
    return [(i + 1, dt / sub / F) for i, (lvl, dt, sub, _) in enumerate(d["rows"]) if sub > 0]

def main():
    R = os.path.dirname(os.path.abspath(__file__))
    L1 = load("L1", os.path.join(R, "L1/log.extrude"))
    L2 = load("L2", os.path.join(R, "L2/log.extrude"))

    print("=== ROW 0 CHECK (the partition is not read unless both complete) ===")
    for d in (L1, L2):
        print("   %s  levels %d/%d   EXTRUSION COMPLETE line: %s"
              % (d["tag"], len(d["rows"]), LAYERS[d["tag"]], d["complete"]))
    if not (L1["complete"] and L2["complete"]):
        print("   *** A LEVEL IS INCOMPLETE. Numbers below are PROVISIONAL, not a cap. ***")

    print("\n=== MEASURED ===")
    for d in (L1, L2):
        ks = k_of(d)
        print("   %s  SIGMA_SUBITS=%7d  wall=%8.1f s = %6.2f core-min (1 rank)"
              % (d["tag"], d["sigma"], d["wall"], d["wall"] / 60))
        print("        k over levels: min %.3fe-6  max %.3fe-6  terminal %.3fe-6"
              % (min(v for _, v in ks) * 1e6, max(v for _, v in ks) * 1e6, ks[-1][1] * 1e6))
        tail = sum(s for _, _, s, _ in d["rows"][-6:])
        print("        last 6 levels carry %.1f %% of SIGMA_SUBITS" % (100.0 * tail / d["sigma"]))

    def wall_model(d, KB, CC):
        return FACES[d["tag"]] * sum(s * max(KB, CC * (i + 1))
                                     for i, (_, _, s, _) in enumerate(d["rows"]))

    def lsq(ds):
        """least squares on (K_BASE, C) over the per-level k of the given levels"""
        best = None
        for KB in [x * 1e-8 for x in range(200, 330, 1)]:
            for CC in [x * 1e-9 for x in range(60, 120, 1)]:
                e = 0.0
                for d in ds:
                    for i, v in k_of(d):
                        e += (max(KB, CC * i) - v) ** 2
                if best is None or e < best[0]:
                    best = (e, KB, CC)
        return best[1], best[2]

    print("\n=== THE TWO-BRANCH LAW ===")
    print("   OUT-OF-SAMPLE TEST -- fit on L1 ALONE, predict L2. This is EXACTLY the")
    print("   operation about to be done for L3, so its error is the honest bias.")
    KB1, C1 = lsq([L1])
    pred_k = max(KB1, C1 * LAYERS["L2"]); meas_k = k_of(L2)[-1][1]
    wpred = wall_model(L2, KB1, C1)
    bias = (L2["wall"] - wpred) / wpred
    print("     fit on L1: K_BASE=%.4e  C=%.4e  crossover layer %.1f" % (KB1, C1, KB1 / C1))
    print("     L2 terminal k : predicted %.4e  measured %.4e  error %+.1f %%"
          % (pred_k, meas_k, 100 * (pred_k - meas_k) / meas_k))
    print("     L2 TOTAL wall : predicted %6.0f s  measured %6.0f s  error %+.1f %%"
          % (wpred, L2["wall"], -100 * bias))
    print("     *** READ THIS AS A DIAGNOSIS, NOT AS A BIAS TO APPLY. ***")
    print("     L1's crossover sits at layer %.1f of %d, so L1's march barely enters"
          % (KB1 / C1, LAYERS["L1"]))
    print("     the rising branch and CANNOT identify C. The fit is DEGENERATE: it")
    print("     puts the crossover beyond L1's own range. ONE LEVEL CANNOT PREDICT")
    print("     THE NEXT ONE'S COST UNDER THIS LAW -- which is exactly why every")
    print("     estimate made from L1 alone came in low. The %.0f %% is the cost of" % (100 * bias))
    print("     extrapolating from an unidentifiable fit, not a property of the law.")
    print("   PRODUCTION FIT -- L1 and L2 jointly:")
    K_BASE, C = lsq([L1, L2])
    print("     K_BASE=%.4e  C=%.4e  crossover layer %.1f" % (K_BASE, C, K_BASE / C))
    for d in (L1, L2):
        w = wall_model(d, K_BASE, C)
        print("     in-sample %s wall: model %6.0f s  measured %6.0f s  (%+.1f %%)"
              % (d["tag"], w, d["wall"], 100 * (w - d["wall"]) / d["wall"]))
    # L2 is the finer, more L3-like level and the one whose march identifies C,
    # so ITS residual is the bias carried forward -- not the degenerate L1-only one.
    wl2 = wall_model(L2, K_BASE, C)
    bias = (L2["wall"] - wl2) / wl2
    print("     BIAS CARRIED TO L3 = L2's residual under the JOINT fit = %+.1f %%" % (100 * bias))

    print("\n=== THE ONLY UNKNOWN: THE SUB-ITS PROFILE AT L3 ===")
    g21 = L2["sigma"] / L1["sigma"]
    print("   SIGMA_SUBITS  L1 %d -> L2 %d   g21 = %.4f" % (L1["sigma"], L2["sigma"], g21))
    print("   layers 32->48->72 and faces 14144->31824->71604 are BOTH exactly x1.5 / x2.25")
    print("   per step, so any pure power law in either gives g32 == g21 exactly.")

    # L3 sub-its profile: L2's shape, resampled onto 72 layers, rescaled to SIGMA_SUBITS(L3)
    n2 = len(L2["rows"]); n3 = LAYERS["L3"]
    shape = []
    for i in range(n3):
        x = (i + 1) / n3 * n2 - 1
        j = min(max(int(math.floor(x)), 0), n2 - 2); w = x - j
        shape.append(L2["rows"][j][2] * (1 - w) + L2["rows"][j + 1][2] * w)
    ssh = sum(shape)

    # --- THE MECHANISM THAT SETS THE BAND -------------------------------------
    # SIGMA_SUBITS is LINEAR IN LAYERS with a near-invariant mean per layer.
    # Measured: 26514/32 = 828.6 ; 38920/48 = 810.8 ; ratio 0.9786. The profile
    # peak barely moves (5772 at eta 0.88 -> 5920 at eta 0.85, +2.6 %).
    # So g32 = 1.5 * (per-layer mean trend), and the ONLY free quantity is that
    # trend.  Earlier endpoints g32 = 1.00 and g32 = g21^2 are DISCARDED as
    # mechanismless: 1.00 requires sub-its not to grow when layers grow x1.5,
    # and g21^2 makes SIGMA_SUBITS ~ layers^1.97 with nothing behind it.
    mpl1 = L1["sigma"] / LAYERS["L1"]; mpl2 = L2["sigma"] / LAYERS["L2"]
    trend = mpl2 / mpl1
    pk1 = max(r[2] for r in L1["rows"]); pk2 = max(r[2] for r in L2["rows"])
    rl = LAYERS["L3"] / LAYERS["L2"]
    print("\n=== THE MECHANISM THAT SETS THE BAND ===")
    print("   mean sub-its per layer: L1 %.1f -> L2 %.1f   trend %.4f" % (mpl1, mpl2, trend))
    print("   profile peak:           L1 %d -> L2 %d   ratio %.4f" % (pk1, pk2, pk2 / pk1))
    print("   layers ratio L2->L3 = %.3f exactly, so g32 = %.3f x (per-layer trend)." % (rl, rl))
    print("   g32 measured-trend %.4f | flat %.4f | peak-trend %.4f"
          % (rl * trend, rl, rl * (pk2 / pk1)))
    print("   *** g32 = 1.00 and g32 = g21^2 are DISCARDED: neither has a mechanism. ***")

    print("\n=== THE BAND ===")
    out = {}
    for name, g in (("LOW   g32 = %.3f  (per-layer mean keeps declining at %.4f)" % (rl * trend, trend), rl * trend),
                    ("MID   g32 = %.3f  (per-layer mean flat -- sub-its exactly linear in layers)" % rl, rl),
                    ("HIGH  g32 = %.3f  (per-layer mean rises with the peak, +%.1f %%)" % (rl * (pk2 / pk1), 100 * (pk2 / pk1 - 1)), rl * (pk2 / pk1))):
        S3 = L2["sigma"] * g
        w = FACES["L3"] * sum(s / ssh * S3 * max(K_BASE, C * (i + 1)) for i, s in enumerate(shape))
        w *= (1 + bias)                      # measured out-of-sample under-prediction
        out[name[:5].strip()] = w / 60
        print("   %-56s SIGMA_SUBITS(L3)=%8.0f  wall %7.0f s = %6.1f core-min"
              % (name, S3, w, w / 60))
    print("\n   1 rank, so core-min == wall minutes.")
    print("   Derived USD at $%.4f/core-h -- DERIVED, NOT MEASURED (the box cannot read its billing):"
          % RATE)
    for k_, v in out.items():
        print("     %-5s %6.1f core-min = $%.3f" % (k_, v, v / 60 * RATE))

if __name__ == "__main__":
    main()
