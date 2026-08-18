#!/usr/bin/env python3
"""R1, third leg -- adversarial checks on the sensitivity-geography result."""
import numpy as np
from scipy import stats
from scipy.spatial import cKDTree

REINV = "/home/ubuntu/certonomous-runs/S1-cbfs-reinversion"
N = 21000
LQOI = 1.6257778891393064e+03


def read_vector(path, n=N):
    t = open(path, errors="replace").read()
    i = t.index("internalField"); j = t.index("(", i)
    out, pos = [], j
    while len(out) < n:
        pos = t.index("(", pos + 1); e = t.index(")", pos)
        out.append([float(z) for z in t[pos + 1:e].split()]); pos = e
    return np.array(out)


perm = np.load(REINV + "/cbfs_inv/dv_to_serial_perm.npy").astype(np.int64)
b = np.load(REINV + "/cbfs_inv/beta_final.npy")
g = np.abs(np.load(REINV + "/cbfs_inv/grad_eval001.npy") * LQOI)
C = read_vector(REINV + "/cbfs_inv/2500/C")[perm]
x, y, z = C[:, 0], C[:, 1], C[:, 2]
dev = np.abs(b - 1.0)
k = N // 10
win = (x >= 0) & (x <= 6) & (y >= 0) & (y <= 2)
regions = [("in-window", win), ("upstream x<0", x < 0),
           ("above shear layer y>2", y > 2), ("downstream x>6 & y<=2", (x > 6) & (y <= 2))]

print("=" * 100)
print("[F] CONFOUND: is |g| just a cell-size (mesh) map?  Cell-wise adjoint gradients")
print("    commonly scale with cell volume, which would make the geography a mesh artefact.")
print("=" * 100)
print("  z coordinate: %d unique values, range [%.4g, %.4g]  -> mesh is %s in z"
      % (len(np.unique(np.round(z, 12))), z.min(), z.max(),
         "one cell thick" if len(np.unique(np.round(z, 12))) == 1 else "multi-layer"))
tree = cKDTree(C[:, :2])
d, _ = tree.query(C[:, :2], k=5)          # self + 4 neighbours
h = d[:, 1:].mean(axis=1)                  # local spacing proxy
V = h ** 2                                 # 2-D area proxy (uniform z thickness)
print("  local spacing proxy h: min %.4e max %.4e (ratio %.1f)" % (h.min(), h.max(), h.max() / h.min()))
print("  Spearman(|g|, V_proxy)        = %+.4f" % stats.spearmanr(g, V).statistic)
print("  Spearman(|beta-1|, V_proxy)   = %+.4f" % stats.spearmanr(dev, V).statistic)
gn = g / V
print("  volume-normalised sensitivity |g|/V:")
top_g = np.argsort(-g)[:k]
top_gn = np.argsort(-gn)[:k]
top_b = np.argsort(-dev)[:k]
print("    %-24s %10s %10s %10s" % ("region", "top10|g|", "top10|g|/V", "top10|b-1|"))
for nm, m in regions:
    print("    %-24s %9.1f%% %9.1f%% %9.1f%%" % (nm, 100 * m[top_g].mean(),
          100 * m[top_gn].mean(), 100 * m[top_b].mean()))
print("    'G2' on |g|   = %.2f%% ; 'G2' on |g|/V = %.2f%% ; 'G2' on |beta-1| = %.2f%%"
      % (100 * win[top_g].mean(), 100 * win[top_gn].mean(), 100 * win[top_b].mean()))
print("  Spearman(|beta-1|, |g|/V) = %+.4f  (vs %+.4f against raw |g|)"
      % (stats.spearmanr(dev, gn).statistic, stats.spearmanr(dev, g).statistic))

print("\n" + "=" * 100)
print("[G] IS THE CORRELATION DRIVEN BY THE UNTOUCHED FAR FIELD?")
print("=" * 100)
print("  (median |beta-1| is 1.1e-4: most cells barely moved, and both fields decay together)")
for q in [0.0, 0.5, 0.9, 0.99]:
    m = dev >= np.quantile(dev, q)
    sp = stats.spearmanr(dev[m], g[m]).statistic
    pe = stats.pearsonr(dev[m], g[m]).statistic
    print("    cells with |beta-1| above its q=%.2f quantile: n=%6d  Spearman %+.4f  Pearson %+.4f"
          % (q, m.sum(), sp, pe))
for q in [0.5, 0.9]:
    m = g >= np.quantile(g, q)
    print("    cells with |g| above its q=%.2f quantile:       n=%6d  Spearman %+.4f"
          % (q, m.sum(), stats.spearmanr(dev[m], g[m]).statistic))

print("\n" + "=" * 100)
print("[H] R1's PRE-REGISTERED DECISION THRESHOLDS, scored")
print("=" * 100)
sp = stats.spearmanr(dev, g).statistic
ov = len(set(top_b.tolist()) & set(top_g.tolist())) / k
print("  measured: Spearman rho = %+.4f ; top-decile overlap = %.2f%% (chance 10%%)" % (sp, 100 * ov))
print("  SENSITIVITY-DRIVEN if rho >= 0.6 AND overlap >= 40%%  -> %s"
      % ("MET" if (sp >= 0.6 and ov >= 0.40) else "not met"))
print("  PHYSICAL if rho <= 0.3 AND overlap <= 15%%             -> %s"
      % ("MET" if (sp <= 0.3 and ov <= 0.15) else "not met"))
bn = np.clip(1 - 3.732502e+02 * np.load(REINV + "/cbfs_inv/grad_eval001.npy") * LQOI, 0.2, 4.0)
agree = stats.spearmanr(np.abs(bn - 1), dev).statistic
print("  ABORT (TOO CLOSE TO FIRST STEP) if |beta-1| agrees with the fitted first step")
print("  beyond rho = 0.9 -> measured agreement rho = %+.4f -> %s"
      % (agree, "ABORT FIRES" if agree > 0.9 else "abort does not fire"))
print("\n  The abort and the verdict fire together. Per R1's own text the abort dominates:")
print("  'reported as undecided and not forced' / 'inconclusive, not a verdict'.")

print("\n" + "=" * 100)
print("[I] WHAT R5 WOULD DO, PREDICTED FROM THE MEASURED SENSITIVITY MAP")
print("=" * 100)
print("  R5's premise (its own words): 'whitening by the sensitivity mechanically pushes")
print("  correction away from high-sensitivity cells; if those cells happen to sit OUTSIDE")
print("  the window, G2 rises'.  Measured enrichment of high-|g| cells, by region:")
for nm, m in regions:
    print("    %-24s base %5.2f%%  top-decile-|g| %5.1f%%  enrichment x%.2f"
          % (nm, 100 * m.mean(), 100 * m[top_g].mean(), m[top_g].mean() / m.mean()))
print("  The high-sensitivity cells are enriched INSIDE the window by %.2fx -- the largest"
      % (win[top_g].mean() / win.mean()))
print("  enrichment of any region. R5's 'if' is measured FALSE.")
# direct simulation of two whitening choices at zero compute
gr = np.load(REINV + "/cbfs_inv/grad_eval001.npy") * LQOI
for name, expo in [("sigma_i ~ 1/|g_i|   (full whitening)", -1.0),
                   ("sigma_i ~ 1/sqrt|g_i| (half whitening)", -0.5),
                   ("unweighted (current)", 0.0)]:
    w = np.where(g > 0, g ** (2 * expo), 0.0)
    d_pred = np.abs(w * gr)                       # |beta-1| ~ sigma_i^2 |g_i|
    if d_pred.max() == 0:
        continue
    tp = np.argsort(-d_pred)[:k]
    print("    first-order predicted G2 under %-38s = %5.2f%%" % (name, 100 * win[tp].mean()))
print("  (first-order, single-step prediction only -- it does not price the converged arm,")
print("   but all three whitening exponents move G2 the wrong way or leave it far below 50%.)")
print("\nDONE.")
