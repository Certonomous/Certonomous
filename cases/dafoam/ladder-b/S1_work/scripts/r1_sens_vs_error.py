#!/usr/bin/env python3
"""
R1 -- Does the inferred correction land where the model is wrong, or where the
objective is sensitive?

Zero solver compute. Arithmetic over arrays already on disk.

Test statistic: rank correlation of |beta_final - 1| against |g(beta=1)|.
Null model (mandatory, Verification Charter 2a): what that correlation would be
if beta were exactly one (projected) gradient step from 1.
"""
import hashlib
import os
import re
import sys

import numpy as np
from scipy import stats

REINV = "/home/ubuntu/certonomous-runs/S1-cbfs-reinversion"
INV = "/home/ubuntu/certonomous-runs/S1-cbfs-inversion"
N = 21000
LO, HI = 0.2, 4.0


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def load(path, label):
    a = np.load(path)
    print("  %-28s %-88s shape=%s dtype=%s sha256/16=%s"
          % (label, path, a.shape, a.dtype, sha(path)))
    return a


def read_scalar_field(path, n=N):
    txt = open(path, errors="replace").read()
    i = txt.index("internalField")
    j = txt.index("(", i)
    k = txt.index(")", j)
    vals = np.array([float(x) for x in txt[j + 1:k].split()])
    assert vals.size == n, (path, vals.size)
    return vals


def read_vector_field(path, n=N):
    txt = open(path, errors="replace").read()
    i = txt.index("internalField")
    j = txt.index("(", i)
    vecs, pos = [], j
    while len(vecs) < n:
        pos = txt.index("(", pos + 1)
        end = txt.index(")", pos)
        vecs.append([float(x) for x in txt[pos + 1:end].split()])
        pos = end
    return np.array(vecs)


def corrs(a, b):
    """Spearman and Pearson of two 1-D arrays."""
    if a.size < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return float("nan"), float("nan")
    sp = stats.spearmanr(a, b).statistic
    pe = stats.pearsonr(a, b).statistic
    return float(sp), float(pe)


def line(name, a, b, n=None):
    sp, pe = corrs(a, b)
    print("    %-34s n=%6d   Spearman %+.4f   Pearson %+.4f"
          % (name, a.size if n is None else n, sp, pe))
    return sp, pe


def topdecile_overlap(a, b):
    k = a.size // 10
    ia = set(np.argsort(-a)[:k].tolist())
    ib = set(np.argsort(-b)[:k].tolist())
    ov = len(ia & ib)
    # hypergeometric tail: P(X >= ov)
    p = stats.hypergeom.sf(ov - 1, a.size, k, k)
    return ov / k, k, p


print("=" * 100)
print("R1: sensitivity vs error.  Executed", os.popen("date -u +%FT%TZ").read().strip())
print("=" * 100)

# ----------------------------------------------------------------------------
# STEP 1 -- provenance load
# ----------------------------------------------------------------------------
print("\n[1] ARRAYS LOADED (provenance)")
print("  --- run: S1-cbfs-reinversion (the 'after objective repair' arm, G1=0.25847, G2=26.9%) ---")
perm = load(REINV + "/cbfs_inv/dv_to_serial_perm.npy", "dv_to_serial_perm")
b_dv = load(REINV + "/cbfs_inv/beta_final.npy", "beta_final [eval 16]")
b_it1 = load(REINV + "/cbfs_inv/beta_accept_iter001.npy", "beta_accept_iter001")
g1 = load(REINV + "/cbfs_inv/grad_eval001.npy", "grad_eval001 [eval 1]")
g10 = load(REINV + "/cbfs_inv/grad_eval010.npy", "grad_eval010 [eval 10]")
g_a8 = load(REINV + "/cbfs_inv/grad_anchor8.npy", "grad_anchor8 [control]")

# ----------------------------------------------------------------------------
# STEP 2 -- WHICH EVALUATION IS WHICH.  Confirm eval 1 is the unperturbed field.
# ----------------------------------------------------------------------------
print("\n[2] EVALUATION IDENTITY -- is eval 1 the unperturbed state?")
hist = [l.split(",") for l in open(REINV + "/J_history_main.csv") if l.strip()]
e1 = hist[0]
print("  J_history row for eval 1: neval=%s  varU=%s  penalty=%s  beta_min=%s  beta_max=%s"
      % (e1[1], e1[2], e1[4], e1[6], e1[7]))
print("  -> penalty = LL2*sum((beta-1)^2) = %s ; beta_min = beta_max = %s => beta == 1 exactly."
      % (e1[4], e1[6]))
print("  driver.out CONTROL line: grad_maxabsdiff(eval1, anchor8) = %.3e (recomputed here)"
      % np.abs(g1 - g_a8).max())
print("  |g_eval001 - g_eval010|max = %.6e  (distinct evaluations, not the same array)"
      % np.abs(g1 - g10).max())
print("  |beta_final - 1|max = %.6f ; |beta_accept_iter001 - 1|max = %.6f"
      % (np.abs(b_dv - 1).max(), np.abs(b_it1 - 1).max()))

# ----------------------------------------------------------------------------
# STEP 3 -- PERMUTE-INVERT-ASSERT.  The kill switch.
# ----------------------------------------------------------------------------
print("\n[3] PERMUTATION CONTROL (the kill switch: a correlation between differently")
print("    ordered arrays is a number with no meaning)")
perm_i = perm.astype(np.int64)
ok_bijection = np.array_equal(np.sort(perm_i), np.arange(N))
print("  perm is a bijection on [0,%d): %s" % (N, ok_bijection))
inv = np.empty(N, dtype=np.int64)
inv[perm_i] = np.arange(N)
print("  invert-assert  perm[inv] == arange : %s ; inv[perm] == arange : %s"
      % (np.array_equal(perm_i[inv], np.arange(N)), np.array_equal(inv[perm_i], np.arange(N))))

b_serial = read_scalar_field(REINV + "/cbfs_inv/2500/betaFIOmega")
C_serial = read_vector_field(REINV + "/cbfs_inv/2500/C")
d_perm = np.abs(b_serial[perm_i] - b_dv).max()
d_noperm = np.abs(b_serial - b_dv).max()
print("  |beta_serial[perm] - beta_dv|max = %.4e   <-- permuted   (record's control: 5.1e-15)" % d_perm)
print("  |beta_serial       - beta_dv|max = %.4e   <-- unpermuted (shows the orders really differ)" % d_noperm)
assert d_perm < 1e-10, "PERMUTATION CONTROL FAILED -- stop here"
print("  PERMUTATION CONTROL PASSES. serial[perm[i]] = dv[i]; cell centres for DV index i are C_serial[perm[i]].")

C_dv = C_serial[perm_i]
x, y = C_dv[:, 0], C_dv[:, 1]

# ----------------------------------------------------------------------------
# STEP 4 -- reproduce the published G2 as a provenance check on beta_final
# ----------------------------------------------------------------------------
print("\n[4] PROVENANCE CHECK -- reproduce the published G2 from these same arrays")
dev = np.abs(b_dv - 1.0)
win = (x >= 0) & (x <= 6) & (y >= 0) & (y <= 2)
k = N // 10
top = np.argsort(-dev)[:k]
g2 = win[top].mean()
print("  G2 (top decile of |beta-1| inside window 0<=x<=6, 0<=y<=2) = %.4f%%  (published: 26.8571%%)"
      % (100 * g2))
print("  window base rate = %.4f%% of cells" % (100 * win.mean()))
print("  top decile split: upstream x<0 %.1f%% ; above shear layer y>2 %.1f%% ; window %.1f%% ; other %.1f%%"
      % (100 * (x[top] < 0).mean(), 100 * (y[top] > 2).mean(), 100 * win[top].mean(),
         100 * (~win[top] & (x[top] >= 0) & (y[top] <= 2)).mean()))
print("  pinned at bounds: n(beta<=0.2+1e-9)=%d  n(beta>=4-1e-9)=%d  (ties in |beta-1|)"
      % ((b_dv <= LO + 1e-9).sum(), (b_dv >= HI - 1e-9).sum()))

# ----------------------------------------------------------------------------
# STEP 5 -- THE NULL MODEL.  Reported BEFORE the measurement.
# ----------------------------------------------------------------------------
print("\n" + "=" * 100)
print("[5] THE NULL MODEL -- what the correlation would be if beta were exactly")
print("    one projected gradient step from 1.  (Charter 2a: a quantity derivable")
print("    by construction from its own inputs is an identity, not a control.)")
print("=" * 100)

LQOI = 1.6257778891393064e+03
LL2 = 1.0e-5
g_tot1 = LQOI * g1 + 2.0 * LL2 * (np.ones(N) - 1.0)   # L2 term is exactly zero at beta=1
gmag = np.abs(g_tot1)
print("  g_total(beta=1) = LQOI*g_varU + 2*LL2*(beta-1); second term identically 0 at beta=1.")
print("  ||g_total(beta=1)|| = %.4e  (driver.out eval-1 line: 1.986e-01)" % np.linalg.norm(g_tot1))

# fit alpha: least squares beta_final ~ 1 - alpha*g, then the projected version
alpha_ls = float(np.dot(-(b_dv - 1.0), g_tot1) / np.dot(g_tot1, g_tot1))
def step(a):
    return np.clip(1.0 - a * g_tot1, LO, HI)
# also fit alpha minimising ||clip(1-a g) - beta_final|| over a grid (projection is nonlinear)
grid = np.concatenate([np.logspace(-3, 4, 4001), [abs(alpha_ls)]])
res = [np.linalg.norm(step(a) - b_dv) for a in grid]
alpha_fit = float(grid[int(np.argmin(res))])
print("  fitted step length: unprojected least squares alpha = %.6e ; projected best-fit alpha = %.6e"
      % (alpha_ls, alpha_fit))

for tag, a in [("least-squares alpha", alpha_ls), ("projected best-fit alpha", alpha_fit)]:
    bn = step(a)
    dn = np.abs(bn - 1.0)
    sp, pe = corrs(dn, gmag)
    ov, _, _ = topdecile_overlap(dn, gmag)
    print("    NULL (%s = %.4e): Spearman %+.4f  Pearson %+.4f  top-decile overlap %.1f%%  n_pinned=%d"
          % (tag, a, sp, pe, 100 * ov, int(((bn <= LO + 1e-9) | (bn >= HI - 1e-9)).sum())))

bn = step(alpha_fit)
dn = np.abs(bn - 1.0)
NULL_SP, NULL_PE = corrs(dn, gmag)
NULL_OV, _, _ = topdecile_overlap(dn, gmag)

# the ACTUAL first accepted iterate -- an unfitted, measured first step
print("\n  The actual first accepted L-BFGS-B iterate (beta_accept_iter001, reinversion)")
print("  is a MEASURED first step, not a fitted one -- the same null with nothing fitted:")
d_it1 = np.abs(b_it1 - 1.0)
sp, pe = corrs(d_it1, gmag)
ov, _, _ = topdecile_overlap(d_it1, gmag)
print("    beta_accept_iter001 vs |g(beta=1)| : Spearman %+.4f  Pearson %+.4f  top-decile overlap %.1f%%"
      % (sp, pe, 100 * ov))
a_it1 = float(np.dot(-(b_it1 - 1.0), g_tot1) / np.dot(g_tot1, g_tot1))
print("    implied step length alpha = %.6e ; |beta_it1 - (1 - alpha*g)|max = %.3e (is it a pure -g step?)"
      % (a_it1, np.abs(b_it1 - (1.0 - a_it1 * g_tot1)).max()))

# ----------------------------------------------------------------------------
# STEP 6 -- IS THE RUN TOO CLOSE TO ITS FIRST STEP?
# ----------------------------------------------------------------------------
print("\n[6] IS THE MEASURED FIELD TOO CLOSE TO ITS OWN FIRST STEP?")
print("    (R1's stated abort: agreement beyond rho = 0.9 => TOO CLOSE, inconclusive)")
sp_f, pe_f = corrs(b_dv, bn)
sp_d, pe_d = corrs(dev, dn)
print("    beta_final vs fitted first step (fields)   : Spearman %+.4f  Pearson %+.4f" % (sp_f, pe_f))
print("    |beta_final-1| vs |fitted first step -1|   : Spearman %+.4f  Pearson %+.4f" % (sp_d, pe_d))
sp_f1, pe_f1 = corrs(b_dv, b_it1)
print("    beta_final vs actual first iterate (fields): Spearman %+.4f  Pearson %+.4f" % (sp_f1, pe_f1))
print("    displacement ratio ||beta_final-1|| / ||beta_it1-1|| = %.2f"
      % (np.linalg.norm(b_dv - 1) / np.linalg.norm(b_it1 - 1)))
print("    ||g(eval1)|| = %.4e -> ||g(eval10)|| = %.4e   (gradient norm change over the run)"
      % (np.linalg.norm(LQOI * g1), np.linalg.norm(LQOI * g10)))

# ----------------------------------------------------------------------------
# STEP 7 -- THE MEASUREMENT
# ----------------------------------------------------------------------------
print("\n" + "=" * 100)
print("[7] THE MEASUREMENT -- |beta_final - 1| (eval 16) vs |g(beta=1)| (eval 1)")
print("=" * 100)
SP, PE = line("WHOLE DOMAIN", dev, gmag)
ov, kk, p = topdecile_overlap(dev, gmag)
print("    top-decile overlap %.2f%% (k=%d, chance 10%%, hypergeom P(>=obs)=%.3g)" % (100 * ov, kk, p))
print("    NULL for comparison: Spearman %+.4f  Pearson %+.4f  overlap %.1f%%"
      % (NULL_SP, NULL_PE, 100 * NULL_OV))

# log-space Pearson (heavy tails)
eps = 1e-300
lp = stats.pearsonr(np.log10(dev + 1e-12), np.log10(gmag + eps)).statistic
print("    auxiliary: Pearson on log10 of both quantities = %+.4f" % lp)

# ----------------------------------------------------------------------------
# STEP 8 -- REGIONS
# ----------------------------------------------------------------------------
print("\n[8] BY REGION (regions in DV order via the verified permutation)")
regions = [
    ("in-window 0<=x<=6, 0<=y<=2", win),
    ("upstream x<0", x < 0),
    ("above shear layer y>2", y > 2),
    ("downstream x>6 & y<=2", (x > 6) & (y <= 2)),
]
cov = np.zeros(N, dtype=int)
for _, m in regions:
    cov += m.astype(int)
print("    region coverage: cells in exactly one region = %d ; in none = %d ; in >1 = %d"
      % ((cov == 1).sum(), (cov == 0).sum(), (cov > 1).sum()))
print("    %-30s %7s  %10s  %10s | %10s %10s" % ("region", "ncells", "Spearman", "Pearson", "NULL Sp", "NULL Pe"))
for name, m in regions:
    sp, pe = corrs(dev[m], gmag[m])
    nsp, npe = corrs(dn[m], gmag[m])
    print("    %-30s %7d  %+10.4f  %+10.4f | %+10.4f %+10.4f" % (name, m.sum(), sp, pe, nsp, npe))

# ----------------------------------------------------------------------------
# STEP 9 -- CONTROLS
# ----------------------------------------------------------------------------
print("\n[9] CONTROLS")
print("    positive control 1 (the null model itself, a field known to be a pure")
print("      gradient step):                     Spearman %+.4f" % NULL_SP)
sp_pc2, _ = corrs(np.abs(b_it1 - 1.0), gmag)
print("    positive control 2 (the run's own measured first iterate):"
      "  Spearman %+.4f" % sp_pc2)
rng = np.random.default_rng(20260811)
sps = [corrs(dev[rng.permutation(N)], gmag)[0] for _ in range(200)]
print("    negative control (|beta-1| shuffled, 200 draws): Spearman mean %+.5f  sd %.5f  |max| %.4f"
      % (np.mean(sps), np.std(sps), np.max(np.abs(sps))))
print("    => the instrument returns ~1 where a relation exists and ~0 where none does.")

# spatial-autocorrelation-aware significance: block shuffle by x-column
print("    (rank correlation p-values are not quoted: both fields are spatially")
print("     autocorrelated, so the 21000 cells are not 21000 independent samples.)")

# ----------------------------------------------------------------------------
# STEP 10 -- SECOND ARM: the first inversion (the 29.0% pre-repair run)
# ----------------------------------------------------------------------------
print("\n" + "=" * 100)
print("[10] SECOND ARM -- S1-cbfs-inversion (pre-repair, G2 = 29.0476%)")
print("=" * 100)
b_dv_i = load(INV + "/cbfs_inv/beta_final.npy", "beta_final [inv]")
g1_i = load(INV + "/cbfs_inv/grad_eval001.npy", "grad_eval001 [inv, eval 1]")
b_fields_i = load(INV + "/fields_beta.npy", "fields_beta [inv, serial]")
C_i = load(INV + "/fields_C.npy", "fields_C [inv, serial]")
win_i_serial = load(INV + "/mask_win.npy", "mask_win [inv, serial]")

d_perm_i = np.abs(b_fields_i[perm_i] - b_dv_i).max()
print("  permute-invert-assert on THIS run with the reinversion's perm:")
print("    |fields_beta[perm] - beta_final_dv|max = %.4e (same mesh+decomposition => same perm)" % d_perm_i)
if d_perm_i < 1e-9:
    C_dv_i = C_i[perm_i]
    xi, yi = C_dv_i[:, 0], C_dv_i[:, 1]
    win_i = (xi >= 0) & (xi <= 6) & (yi >= 0) & (yi <= 2)
    dev_i = np.abs(b_dv_i - 1.0)
    # this run's own LQOI is different; scale is irrelevant to both correlations
    gmag_i = np.abs(g1_i)
    top_i = np.argsort(-dev_i)[:k]
    print("  G2 reproduced for this arm = %.4f%% (published: 29.0476%%)" % (100 * win_i[top_i].mean()))
    sp, pe = line("WHOLE DOMAIN [inv]", dev_i, gmag_i)
    ovi, _, _ = topdecile_overlap(dev_i, gmag_i)
    print("    top-decile overlap %.2f%%" % (100 * ovi))
    # null for this arm
    a_i = float(np.dot(-(b_dv_i - 1.0), g1_i) / np.dot(g1_i, g1_i))
    grid_i = np.logspace(np.log10(abs(a_i)) - 3, np.log10(abs(a_i)) + 3, 2001)
    res_i = [np.linalg.norm(np.clip(1 - a * g1_i, LO, HI) - b_dv_i) for a in grid_i]
    a_ifit = float(grid_i[int(np.argmin(res_i))])
    bn_i = np.clip(1 - a_ifit * g1_i, LO, HI)
    nsp_i, npe_i = corrs(np.abs(bn_i - 1), gmag_i)
    print("    NULL [inv]: Spearman %+.4f  Pearson %+.4f (alpha=%.4e)" % (nsp_i, npe_i, a_ifit))
    fsp_i, _ = corrs(b_dv_i, bn_i)
    print("    beta_final[inv] vs its fitted first step: Spearman %+.4f" % fsp_i)
    for name, m in [("in-window", win_i), ("upstream x<0", xi < 0),
                    ("above shear layer y>2", yi > 2), ("downstream x>6 & y<=2", (xi > 6) & (yi <= 2))]:
        sp, pe = corrs(dev_i[m], gmag_i[m])
        print("      %-28s n=%6d  Spearman %+.4f  Pearson %+.4f" % (name, m.sum(), sp, pe))
else:
    print("  PERM DOES NOT TRANSFER -- second arm restricted to order-free (whole-domain) quantities.")
    dev_i = np.abs(b_dv_i - 1.0)
    gmag_i = np.abs(g1_i)
    line("WHOLE DOMAIN [inv]", dev_i, gmag_i)

# ----------------------------------------------------------------------------
# STEP 11 -- an auxiliary the verdict may need: does |beta-1| track a LATER gradient?
# ----------------------------------------------------------------------------
print("\n[11] AUXILIARY -- the eval-10 gradient (a DIFFERENT evaluation; reported separately")
print("     so no mismatched-evaluation pairing can hide inside a single number)")
line("|beta_final-1| vs |g(eval10)|", dev, np.abs(g10))
sp, pe = corrs(np.abs(g1), np.abs(g10))
print("    |g(eval1)| vs |g(eval10)| : Spearman %+.4f  Pearson %+.4f  (how much the sensitivity map moved)"
      % (sp, pe))

print("\n[12] MAGNITUDE DISTRIBUTIONS (why Spearman is the trusted leg)")
for nm, a in [("|beta_final-1|", dev), ("|g(beta=1)|", gmag)]:
    q = np.quantile(a, [0.5, 0.9, 0.99, 1.0])
    print("    %-16s median %.4e  p90 %.4e  p99 %.4e  max %.4e  (max/p50 = %.3g)"
          % (nm, q[0], q[1], q[2], q[3], q[3] / max(q[0], 1e-300)))
print("\nDONE.")
