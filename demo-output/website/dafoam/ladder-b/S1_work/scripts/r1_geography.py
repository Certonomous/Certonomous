#!/usr/bin/env python3
"""
R1, second leg -- the three geographies, compared directly.

The correlation |beta-1| vs |g| has a null that sits at exactly 1.0 by
arithmetic. This leg avoids that trap: it measures the geography of the
SENSITIVITY FIELD ALONE, which makes no reference to beta at all and therefore
cannot be produced by a barely-moved inversion.

  where the model is wrong  = per-cell loss |U(beta=1) - U_LES|^2
  where the objective is sensitive = |g(beta=1)|
  where the correction landed = |beta_final - 1|
"""
import numpy as np
from scipy import stats

REINV = "/home/ubuntu/certonomous-runs/S1-cbfs-reinversion"
INV = "/home/ubuntu/certonomous-runs/S1-cbfs-inversion"
N = 21000
LQOI = 1.6257778891393064e+03


def read_scalar(path, n=N):
    t = open(path, errors="replace").read()
    i = t.index("internalField"); j = t.index("(", i); k = t.index(")", j)
    v = np.array([float(z) for z in t[j + 1:k].split()]); assert v.size == n
    return v


def read_vector(path, n=N):
    t = open(path, errors="replace").read()
    i = t.index("internalField"); j = t.index("(", i)
    out, pos = [], j
    while len(out) < n:
        pos = t.index("(", pos + 1); e = t.index(")", pos)
        out.append([float(z) for z in t[pos + 1:e].split()]); pos = e
    return np.array(out)


perm = np.load(REINV + "/cbfs_inv/dv_to_serial_perm.npy").astype(np.int64)
b_dv = np.load(REINV + "/cbfs_inv/beta_final.npy")
g1 = np.load(REINV + "/cbfs_inv/grad_eval001.npy") * LQOI
C = read_vector(REINV + "/cbfs_inv/2500/C")[perm]
x, y = C[:, 0], C[:, 1]

U0 = read_vector(REINV + "/cbfs_inv/0/U")[perm]        # starting field
Ud = read_vector(REINV + "/cbfs_inv/0/UData")[perm]    # LES reference
U16 = read_vector(REINV + "/cbfs_inv/2500/U")[perm]    # at beta_final

print("=" * 100)
print("[A] IS 0/U THE CONVERGED beta=1 SOLUTION?  (provenance for the loss geography)")
print("=" * 100)
d2_0 = np.sum((U0 - Ud) ** 2, axis=1)
d2_16 = np.sum((U16 - Ud) ** 2, axis=1)
varU0 = d2_0.sum() / (3 * N)
varU16 = d2_16.sum() / (3 * N)
print("  varianceU from 0/U      = %.16e" % varU0)
print("  eval-1 varianceU (driver, beta=1) = 6.1509017109920479e-04")
print("  ratio = %.6f  -> %s" % (varU0 / 6.1509017109920479e-04,
      "0/U IS the beta=1 baseline (residual = the stored start field vs the same solve "
      "reconverged at primalTol 1e-8)" if abs(varU0 / 6.1509017109920479e-04 - 1) < 1e-4
      else "0/U is NOT the beta=1 solution; baseline loss geography quoted from the record instead"))
print("  varianceU from 2500/U   = %.16e  (at beta_final; audit_final.py's figure)" % varU16)

win = (x >= 0) & (x <= 6) & (y >= 0) & (y <= 2)
regions = [("in-window 0<=x<=6,0<=y<=2", win), ("upstream x<0", x < 0),
           ("above shear layer y>2", y > 2), ("downstream x>6 & y<=2", (x > 6) & (y <= 2))]

print("\n  BASELINE LOSS GEOGRAPHY (where the model is wrong), from 0/U vs 0/UData:")
for nm, m in regions:
    print("    %-28s %5.2f%% of cells  carries %5.1f%% of the loss  (loss/cell x%.2f)"
          % (nm, 100 * m.mean(), 100 * d2_0[m].sum() / d2_0.sum(),
             (d2_0[m].sum() / d2_0.sum()) / m.mean()))
print("    record (prereg amendment D, stage-A loss audit): window = 41.2%% of loss on 8.4%% of cells")

print("\n" + "=" * 100)
print("[B] THE SENSITIVITY GEOGRAPHY -- |g(beta=1)| ALONE, no reference to beta")
print("=" * 100)
gm = np.abs(g1)
k = N // 10
top_g = np.argsort(-gm)[:k]
dev = np.abs(b_dv - 1.0)
top_b = np.argsort(-dev)[:k]
print("  'G2 applied to the gradient': where does the top decile of |g(beta=1)| live?")
print("    %-28s %8s %10s %10s %10s" % ("region", "base%", "top10|g|%", "top10|b-1|%", "loss%"))
for nm, m in regions:
    print("    %-28s %7.2f%% %9.1f%% %10.1f%% %9.1f%%"
          % (nm, 100 * m.mean(), 100 * m[top_g].mean(), 100 * m[top_b].mean(),
             100 * d2_0[m].sum() / d2_0.sum()))
print("\n  'G2' scored on the sensitivity field itself: %.4f%% (bar >50%%) -- the SAME gate,"
      % (100 * win[top_g].mean()))
print("  applied to a field that contains no inversion result whatsoever.")
print("  overlap of top-decile(|g|) with top-decile(|beta-1|) = %.2f%% (chance 10%%)"
      % (100 * len(set(top_g.tolist()) & set(top_b.tolist())) / k))

print("\n  Loss-vs-sensitivity: are they the same geography?")
sp = stats.spearmanr(d2_0, gm).statistic
print("    Spearman(|g(beta=1)|, per-cell baseline loss) = %+.4f" % sp)
print("    Spearman(|beta_final-1|, per-cell baseline loss) = %+.4f"
      % stats.spearmanr(d2_0, dev).statistic)
print("    top-decile(loss) n overlap with top-decile(|g|)   = %.1f%%"
      % (100 * len(set(np.argsort(-d2_0)[:k].tolist()) & set(top_g.tolist())) / k))
print("    top-decile(loss) n overlap with top-decile(|b-1|) = %.1f%%"
      % (100 * len(set(np.argsort(-d2_0)[:k].tolist()) & set(top_b.tolist())) / k))

print("\n" + "=" * 100)
print("[C] THE PART THE NULL CANNOT EXPLAIN -- per-cell gain r = |beta-1| / |g|")
print("=" * 100)
print("  Under the null (one step) r is a CONSTANT. Any geography in r is a departure")
print("  from the null and is therefore not derivable by construction.")
good = gm > 0
r = np.full(N, np.nan)
r[good] = dev[good] / gm[good]
print("  cells with g == 0 exactly: %d" % (~good).sum())
allmed = np.nanmedian(r)
print("  whole-domain median gain r = %.4e" % allmed)
print("    %-28s %8s %12s %12s %10s" % ("region", "n", "median r", "r / global", "IQR ratio"))
for nm, m in regions:
    rr = r[m & good]
    q1, q2, q3 = np.percentile(rr, [25, 50, 75])
    print("    %-28s %8d %12.4e %12.3f %10.2f" % (nm, m.sum(), q2, q2 / allmed, q3 / max(q1, 1e-300)))
print("  spread of the gain within the whole domain: p10/p50/p90 = %.3e / %.3e / %.3e (p90/p10 = %.1f)"
      % (*np.nanpercentile(r, [10, 50, 90]), np.nanpercentile(r, 90) / np.nanpercentile(r, 10)))

print("\n  Rank residual: rank(|beta-1|) - rank(|g|), by region")
ra = stats.rankdata(dev)
rb = stats.rankdata(gm)
res = ra - rb
for nm, m in regions:
    print("    %-28s mean rank shift %+9.1f  (%.2f%% of N)" % (nm, res[m].mean(), 100 * res[m].mean() / N))

print("\n" + "=" * 100)
print("[D] DIRECTION, NOT JUST MAGNITUDE -- is beta_final still ON the -g direction?")
print("=" * 100)
db = b_dv - 1.0
cos = float(np.dot(db, -g1) / (np.linalg.norm(db) * np.linalg.norm(g1)))
print("  cosine( beta_final - 1 , -g(beta=1) ) = %+.4f" % cos)
b_it1 = np.load(REINV + "/cbfs_inv/beta_accept_iter001.npy")
print("  cosine( beta_it1  - 1 , -g(beta=1) ) = %+.4f  (the first step, for scale)"
      % float(np.dot(b_it1 - 1, -g1) / (np.linalg.norm(b_it1 - 1) * np.linalg.norm(g1))))
agree = np.sign(db) == np.sign(-g1)
print("  sign(beta_final-1) == sign(-g(beta=1)) in %.2f%% of cells (chance 50%%)" % (100 * agree.mean()))
for nm, m in regions:
    print("    %-28s sign agreement %.2f%% ; cosine %+.4f"
          % (nm, 100 * agree[m].mean(),
             float(np.dot(db[m], -g1[m]) / (np.linalg.norm(db[m]) * np.linalg.norm(g1[m])))))
print("  among the top decile of |beta-1|: sign agreement %.2f%%" % (100 * agree[top_b].mean()))

print("\n" + "=" * 100)
print("[E] SENSITIVITY GEOGRAPHY, SECOND ARM (S1-cbfs-inversion eval-1 gradient)")
print("=" * 100)
g1i = np.load(INV + "/cbfs_inv/grad_eval001.npy")
top_gi = np.argsort(-np.abs(g1i))[:k]
print("  'G2' on the pre-repair eval-1 gradient = %.4f%%" % (100 * win[top_gi].mean()))
for nm, m in regions:
    print("    %-28s top10|g_inv|%% = %5.1f%%" % (nm, 100 * m[top_gi].mean()))
print("  Spearman(|g_inv(beta=1)|, |g_reinv(beta=1)|) = %+.4f  (two independent baselines,"
      % stats.spearmanr(np.abs(g1i), gm).statistic)
print("   different objective normalisation and different L2 weight)")
print("\nDONE.")
