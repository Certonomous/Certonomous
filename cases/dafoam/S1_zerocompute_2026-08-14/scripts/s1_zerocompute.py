#!/usr/bin/env python3
"""
S1 zero-compute triage, 2026-08-14. Reproduction script for
`demo-output/website/dafoam/S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md`.

Every number this prints is arithmetic over arrays and logs written before the file
was opened. No solver, no container, no scoring call, no network.

  S0  provenance: every gradient array in the archive, and what each one contains
  S1  the SECANT CURVATURE PAIR, and its out-of-sample control against J history
  S2  G-P4 is degenerate: three legs, all functions of (beta, g_QoI, lambda_L2)
  S3  PR-1 settled from disk: the second-QoI sensitivity map already exists
  S4  G2's numerical reproducibility under a domain-decomposition change
  S5  G-P2's stated mechanism, at the one state where it can be checked

Run:  python3 s1_zerocompute.py
Deps: numpy, scipy only. Runs as __main__ (never bytecode-cached; docket D1/D1a).
"""
import hashlib
import os
import re
import subprocess

import numpy as np
from scipy import stats

R = "/home/ubuntu/certonomous-runs/"
REINV = R + "S1-cbfs-reinversion/cbfs_inv/"
INV = R + "S1-cbfs-inversion/cbfs_inv/"
WA = R + "S1-cbfs-weighted-arm/cbfs_inv/"
N = 21000
K = N // 10

# Driver constants, read from each run's own invert_lbfgsb.py / driver_w.py (lines 24-25).
LQOI_R, LL2_R = 1.6257778891393064e+03, 1.0e-5     # reinversion, repaired objective
LQOI_I, LL2_I = 6.5448114804931393e+01, 1.0e-4     # inversion,   corrupted objective

# Objective values from each run's J_history_main.csv (written from solver stdout).
J1_R, J10_R = 9.9999999999999989e-01, 4.3760187861482003e-01
J1_I, J10_I = 1.0000000000000000e+00, 9.9907935208477494e-01


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()[:8]


def rule(t):
    print("\n" + "=" * 96 + "\n" + t + "\n" + "=" * 96)


def read_vector(path, n=N):
    t = open(path, errors="replace").read()
    i = t.index("internalField")
    j = t.index("(", i)
    out, pos = [], j
    while len(out) < n:
        pos = t.index("(", pos + 1)
        e = t.index(")", pos)
        out.append([float(z) for z in t[pos + 1:e].split()])
        pos = e
    return np.array(out)


def read_labelList(p):
    t = open(p, errors="replace").read()
    body = t[t.index("}", t.index("FoamFile")) + 1:]
    m = re.search(r"(\d+)\s*\(", body)
    n, s = int(m.group(1)), m.end()
    v = np.array([int(z) for z in body[s:body.index(")", s)].split()], dtype=np.int64)
    assert v.size == n
    return v


def dv_to_serial(case, nranks=4):
    """DV index -> serial cell index. Convention: non-distributed field inputs index by
    globalIndex = rank-offset concatenation of local cells (DAInputField.C), so the map is
    the concatenation of each rank's cellProcAddressing in rank order."""
    return np.concatenate([read_labelList(
        "%s/processor%d/constant/polyMesh/cellProcAddressing" % (case, i)) for i in range(nranks)])


# ---------------------------------------------------------------- S0
rule("S0. PROVENANCE -- every gradient array in the archive, and what it contains")

found = sorted(subprocess.run(["find", R, "-name", "*grad*.npy"],
                              capture_output=True, text=True).stdout.split())
print("  FRAME: `find /home/ubuntu/certonomous-runs -name '*grad*.npy'`, executed by this script.")
print("  These files are OUTSIDE the repo and invisible to any repo-scoped grep.")
for p in found:
    print("    %-70s n=%-6d md5=%s" % (p.replace(R, ""), np.load(p).size, md5(p)))
print("  COUNT = %d." % len(found))
print("  S1_SENSITIVITY_VS_ERROR.md S1 states 'Nine gradient arrays survive in the whole")
print("  archive ... nine, confirmed.' That is exact for the frame it enumerated")
print("  (S1-cbfs-{inversion,reinversion,weighted-arm}/cbfs_inv/) and understates the archive.")

by = {}
for p in found:
    by.setdefault(md5(p), []).append(p.replace(R, ""))
for h, ps in by.items():
    if len(ps) > 1:
        print("\n  BITWISE-IDENTICAL (md5 %s):" % h)
        for p in ps:
            print("      %s" % p)

gv1r, gv10r = np.load(REINV + "grad_eval001.npy"), np.load(REINV + "grad_eval010.npy")
b10r, bfr = np.load(REINV + "beta_eval010.npy"), np.load(REINV + "beta_final.npy")
gv1i, gv10i = np.load(INV + "grad_eval001.npy"), np.load(INV + "grad_eval010.npy")
b10i, bfi = np.load(INV + "beta_eval010.npy"), np.load(INV + "beta_final.npy")

print("\n  WHAT grad_eval*.npy CONTAINS: the RAW dJ_varU/dbeta, not the total gradient.")
print("  invert_lbfgsb.py:95 saves `gv` from runScript's -gradout; :114 composes")
print("  g_total = LQOI*gv + 2*LL2*(beta-1) host-side and never writes it.")
print("    ||gv1|| (reinversion, raw)   = %.6e" % np.linalg.norm(gv1r))
print("    LQOI * ||gv1||               = %.6e   <- J_history row 1 prints 1.986e-01"
      % (LQOI_R * np.linalg.norm(gv1r)))

print("\n  CONTROL C1 -- evaluation 1 is the unperturbed state.")
print("    J_history row 1: penalty = 0.0e+00 and beta_min = beta_max = 1.000000.")
print("    grad_eval001 vs the separately measured grad_anchor8: max abs diff = %.3e"
      % np.abs(gv1r - np.load(REINV + "grad_anchor8.npy")).max())

perm = np.load(REINV + "dv_to_serial_perm.npy").astype(np.int64)
invp = np.empty_like(perm)
invp[perm] = np.arange(N)
print("\n  CONTROL C2 -- permute-invert-assert (R1's declared kill switch).")
print("    bijection on [0,21000): %s ; perm[inv] and inv[perm] are the identity: %s %s"
      % (np.array_equal(np.sort(perm), np.arange(N)),
         np.array_equal(perm[invp], np.arange(N)), np.array_equal(invp[perm], np.arange(N))))
print("    |fields_beta[perm] - beta_final_dv(inversion)|max = %.3e  (record control 5.1e-15)"
      % np.abs(np.load(R + "S1-cbfs-inversion/fields_beta.npy")[perm] - bfi).max())

# Cell centres come off disk in SERIAL cell order. Arrays in DV order must be read with
# C_serial[perm[i]]. Both frames are built here explicitly and never mixed: S0-S3 work in
# DV order, S4 works in serial order because the two decomposition arms have different DV
# orders and only serial is common to them.
C_serial = read_vector(REINV + "2500/C")
xs, ys = C_serial[:, 0], C_serial[:, 1]
win_serial = (xs >= 0) & (xs <= 6) & (ys >= 0) & (ys <= 2)
C = C_serial[perm]
x, y = C[:, 0], C[:, 1]
win = (x >= 0) & (x <= 6) & (y >= 0) & (y <= 2)
regions = [("in-window 0<=x<=6,0<=y<=2", win), ("upstream x<0", x < 0),
           ("above shear layer y>2", y > 2), ("downstream x>6 & y<=2", (x > 6) & (y <= 2))]
W2 = ((x >= 0) & (x <= 6) & (y >= 0) & (y <= 2)) | ((x >= 6) & (x <= 16) & (y >= -1) & (y <= 0.5))


def g2(f, mask=None):
    """The published G2: top N/10 by magnitude (strict top-k), share in-window.
    `mask` names the frame of `f` -- DV order (default) or serial (`win_serial`)."""
    m = win if mask is None else mask
    t = np.argsort(-np.abs(f))[:K]
    return 100.0 * m[t].mean(), t


print("\n  CONTROL C3 -- both published G2 values reproduce (R5's G-W1 leg, discharged).")
print("    reinversion |beta_final-1| : %.4f%%  (published 26.8571%%)" % g2(bfr - 1)[0])
print("    inversion   |beta_final-1| : %.4f%%  (published 29.0476%%)" % g2(bfi - 1)[0])
print("    window base rate           : %.4f%% (%d of %d cells)" % (100 * win.mean(), win.sum(), N))
print("    W2 support (two boxes)     : %d cells = %.2f%% (prereg says 2,970)"
      % (W2.sum(), 100 * W2.mean()))

# ---------------------------------------------------------------- S1
rule("S1. THE SECANT CURVATURE PAIR")

print("""  R1 states: 'No L-BFGS curvature pair (y_k = g_{k+1} - g_k) is reconstructible from any
  completed run ... Buying curvature as fresh gradients is FORCED, not chosen, which is what
  prices the whole Bayesian line.'  True of CONSECUTIVE-ITERATE pairs. Not true of SECANT
  pairs: the driver keeps eval 1 and every 10th evaluation (invert_lbfgsb.py:96-97,120-121),
  so a run that reached evaluation 10 archived a matched (beta, grad) pair at TWO states.""")
print("\n  Availability audit:")
for nm, d in [("S1-cbfs-inversion", INV), ("S1-cbfs-reinversion", REINV),
              ("S1-cbfs-weighted-arm", WA)]:
    have = [f for f in ("grad_eval001.npy", "grad_eval010.npy", "beta_eval010.npy")
            if os.path.exists(d + f)]
    print("    %-22s %-58s -> %s" % (nm, str(sorted(have)),
                                     "SECANT PAIR" if len(have) == 3 else "no pair"))


def secant(name, b_b, gv_a, gv_b, LQOI, LL2, free=False):
    s = b_b - 1.0
    y_q, y_p = LQOI * (gv_b - gv_a), 2.0 * LL2 * (b_b - 1.0)
    m = np.ones(N, bool)
    if free:
        m = (b_b > 0.2 + 1e-12) & (b_b < 4.0 - 1e-12)
    s, y_q, y_p = s[m], y_q[m], y_p[m]
    ss, sq, sp = float(s @ s), float(s @ y_q), float(s @ y_p)
    Rq, Rp = sq / ss, sp / ss
    print("\n  --- %s%s  (n=%d)" % (name, "  [FREE CELLS]" if free else "", m.sum()))
    print("      ||s||                                    = %.6e" % np.sqrt(ss))
    print("      s^T y_penalty  (IDENTITY 2*lambda_L2*||s||^2) = %+.6e  (%.2f%% of s^T y_total)"
          % (sp, 100 * sp / (sq + sp)))
    print("      s^T y_QoI      (the MEASUREMENT)         = %+.6e  (%.2f%% of s^T y_total)"
          % (sq, 100 * sq / (sq + sp)))
    print("      R_qoi   = s^T y_QoI / ||s||^2            = %+.6e" % Rq)
    print("      R_prior = 2*lambda_L2 (every direction)  = %+.6e" % Rp)
    print("      PRIOR-PRECONDITIONED RAYLEIGH QUOTIENT   = %+.6e" % (Rq / Rp))
    return dict(s=s, y=y_q, sq=sq, Rq=Rq, rho=Rq / Rp)


print("\n  Frame: state A = evaluation 1 (beta == 1 exactly, C1 above); state B = evaluation 10")
print("  (beta_eval010 / grad_eval010, the matched pair D9 established). s = beta_10 - 1.")
rr = secant("S1-cbfs-reinversion (repaired)", b10r, gv1r, gv10r, LQOI_R, LL2_R)
ri = secant("S1-cbfs-inversion (corrupted)", b10i, gv1i, gv10i, LQOI_I, LL2_I)
secant("S1-cbfs-reinversion (repaired)", b10r, gv1r, gv10r, LQOI_R, LL2_R, free=True)

print("""
  IDENTITY vs MEASUREMENT. s^T y_penalty = 2*lambda_L2*||s||^2 is derivable by construction
  from (beta, lambda_L2): any treatment knowing those reproduces it exactly, including one
  whose curvature is wrong. Reported, never gated on. s^T y_QoI needs grad_eval010.npy --
  an adjoint solve no closed form supplies -- and is a measurement.

  NULLS, stated before the numbers:
    N1 flat objective (H_qoi = 0)                  -> s^T y_QoI = 0, rho = 0
    N2 the two gradients are the same array        -> identical to N1
    N3 sign-randomised y_QoI, 200 draws            -> E[s^T y_QoI] = 0 (chance level)""")
rng = np.random.default_rng(20260814)
for nm, d in [("reinversion", rr), ("inversion", ri)]:
    dr = np.array([float(d["s"] @ (d["y"] * rng.choice([-1.0, 1.0], d["s"].size)))
                   for _ in range(200)])
    print("    %-12s N3 null: mean %+.3e sd %.3e | MEASURED %+.3e  (%.1f sd from null)"
          % (nm, dr.mean(), dr.std(), d["sq"], abs(d["sq"] - dr.mean()) / dr.std()))

print("\n  NEGATIVE CONTROL -- cross-pairing s from one run with y from the other:")
s_r, s_i = b10r - 1.0, b10i - 1.0
y_i, y_r = LQOI_I * (gv10i - gv1i), LQOI_R * (gv10r - gv1r)
print("    s(reinv)^T y(inv)/||s||^2  = %+.6e   vs matched reinversion R_qoi = %+.6e"
      % (float(s_r @ y_i) / float(s_r @ s_r), rr["Rq"]))
print("    s(inv)^T y(reinv)/||s||^2  = %+.6e   vs matched inversion   R_qoi = %+.6e"
      % (float(s_i @ y_r) / float(s_i @ s_i), ri["Rq"]))

rule("S1b. OUT-OF-SAMPLE CONTROL -- does the secant curvature predict the OBJECTIVE HISTORY?")
print("  J_history_main.csv is written from solver stdout and shares no array with")
print("  grad_eval*.npy. A quadratic model built from (g1, s, y) is scored against it.\n")
for nm, gva, gvb, b10, LQOI, LL2, Ja, Jb in [
        ("S1-cbfs-reinversion", gv1r, gv10r, b10r, LQOI_R, LL2_R, J1_R, J10_R),
        ("S1-cbfs-inversion", gv1i, gv10i, b10i, LQOI_I, LL2_I, J1_I, J10_I)]:
    s = b10 - 1.0
    lin = float((LQOI * gva) @ s)
    quad = 0.5 * float(s @ (LQOI * (gvb - gva) + 2 * LL2 * s))
    dJ = Jb - Ja
    print("  %s" % nm)
    print("    actual J(eval10)-J(eval1)          = %+.6f" % dJ)
    print("    linear only  g^T s                 = %+.6f   (%.2f%% error)"
          % (lin, 100 * abs(lin - dJ) / abs(dJ)))
    print("    linear + 0.5 s^T y (SECANT)        = %+.6f   (%.2f%% error)"
          % (lin + quad, 100 * abs(lin + quad - dJ) / abs(dJ)))
print("""
  A quadratic is exact only if J is quadratic; the residual is the cubic-and-higher
  remainder over the step actually taken. What the check establishes is that s^T y carries
  the sign and the magnitude needed to close the gap the linear term leaves -- which a
  mismatched or spurious y could not do.""")

rule("S1c. HEAVY-TAIL DISCIPLINE")
for nm, ga, gb in [("reinversion", gv1r, gv10r), ("inversion", gv1i, gv10i)]:
    a = np.abs(ga)
    print("    %-12s |g(eval1)| vs |g(eval10)|: Spearman %+.4f  Pearson %+.4f  (max/median %.2e)"
          % (nm, stats.spearmanr(a, np.abs(gb)).statistic,
             stats.pearsonr(a, np.abs(gb)).statistic, a.max() / np.median(a)))
print("""    SPEARMAN carries every claim in this document. Both gradient fields have
    max/median above 1e6; a Pearson coefficient over that dynamic range is a statement
    about a few hundred extreme cells and moves with tail shape. Pearson is reported
    because the lab asks for both, and is not relied on.""")

# ---------------------------------------------------------------- S2
rule("S2. G-P4 IS DEGENERATE -- all three legs are functions of (beta, g_QoI, lambda_L2)")

b, gv = b10i, gv10i
g_q, g_p = LQOI_I * gv, 2.0 * LL2_I * (b - 1.0)
g_t = g_q + g_p
nq, npn, nt = np.linalg.norm(g_q), np.linalg.norm(g_p), np.linalg.norm(g_t)
r_, c_ = npn / nq, float(np.dot(g_q, -g_p) / (nq * npn))
rms, eps = float(np.sqrt(np.mean((b - 1.0) ** 2))), nt / nq
print("  Recomputed from beta_eval010.npy + grad_eval010.npy (S1-cbfs-inversion):")
print("    ratio r = |g_pen|/|g_QoI| = %.6f   (gate target 0.998441)" % r_)
print("    cos(g_QoI, -g_pen)        = %.6f   (gate target 0.999542)" % c_)
print("    rms|beta-1|               = %.6f   (gate target 0.016502)" % rms)
print("    ||g_total||               = %.6e (J_history row 10 prints 1.450e-05)" % nt)
print("    eps = ||g_total||/|g_QoI| = %.6e" % eps)

print("\n  LEG BY LEG -- what does a treatment need in order to reproduce each number?")
print("    rms|beta-1| : a function of BETA ALONE, and beta is an INPUT to the gate.")
print("    ratio r     : 2*lambda_L2*||beta-1|| / ||g_QoI||. Numerator is the identity the")
print("                  withdrawal removed; the only new content is the scalar ||g_QoI||.")
print("    cosine c    : fixed by the other two through eps^2 = 1 + r^2 - 2*r*c. Solving:")
cf = (1.0 + r_ ** 2 - eps ** 2) / (2.0 * r_)
print("                    c from (r, eps) = %.15f" % cf)
print("                    c measured      = %.15f   (relative agreement %.1e)"
      % (c_, abs(cf - c_) / c_))

print("""
  THE FAILURE MODE, EXHIBITED. Treatment W reports the PRIOR as the posterior: covariance
  = prior covariance, credible intervals straddling beta = 1 in 100% of cells, rank 0. It is
  the exact shape falsifier F1 exists to catch. Handed the archived beta and re-evaluating
  the same g_QoI, its G-P4 is:""")
print("    ratio %.6f  cos %.6f  rms %.6f  -> agreement with the targets %.1e. G-P4: PASS."
      % (r_, c_, rms, 0.0))
print("""    None of the three legs is a function of any covariance, any credible interval or
    any Hessian, so G-P4 cannot see the defect. It grades the GRADIENT, not the posterior --
    structurally the same finding as 'G2 scores the adjoint, not the closure'.

  AND THE COSINE IS NEAR 1 FOR A REASON UNRELATED TO THE PRIOR BEING RIGHT. At any interior
  stationary point g_QoI + g_pen = 0, hence r = c = 1 exactly. The plateau is stationary to
  within eps, so""")
print("    c >= 1 - eps^2/(2r) = %.9f is forced by convergence alone; measured c = %.9f."
      % (1 - eps ** 2 / (2 * r_), c_))
print("""    The published 0.9995 is 'the run converged', restated as an angle.

  WHAT G-P4 DOES TEST, so a replacement can keep it: exactly two scalars -- ||g_QoI|| at the
  plateau state and the angle between g_QoI and (beta-1). That is a sound REPRODUCTION
  control on the gradient and would catch the mismatched-evaluation error that produced the
  1.684x confusion. It is not, and cannot be, a control on a posterior.""")

# ---------------------------------------------------------------- S3
rule("S3. PR-1 SETTLED FROM DISK -- the second-QoI sensitivity map already exists")

print("""  PR-1 (S1_SENSITIVITY_VS_ERROR.md S7) asks for 25 core-min to buy 'a second-QoI
  sensitivity map on CBFS at beta = 1', and pre-registers the decision rule:
  'If the second map's geography matches the first, reading 2 is confirmed outright and
   R5/R8 are closed.'

  The map is already on disk. S1-cbfs-weighted-arm/cbfs_inv/grad_anchorw.npy is
  dJw/dbeta at beta = 1, where Jw = 5319*varUwin + 3591*varUrec -- two disjoint boxToCell
  variances over 2,970 cells (runScript_w.py:79-105), a DIFFERENT functional from the
  all-cells varianceU. It cost 16.83 core-min and was billed on 2026-08-08.""")
gW = np.load(WA + "grad_anchorw.npy")
print("\n  PROVENANCE of grad_anchorw, three ways:")
print("    (a) runScript_w.py:144 sets b0 = np.ones(NCELLS) unless -betafile is given;")
print("        log.anchorw carries no -betafile.")
print("    (b) driver_w.py:24 comments LQOI = 1/27.465931825190644 = '1 / Jw_raw(beta=1),")
print("        anchorw', and log.anchorw:18720 prints OBJ Jw: 2.7465931825190644e+01.")
print("    (c) log.anchorw:18721 prints GRAD norm 7.3228773523e+00; measured here %.10e"
      % np.linalg.norm(gW))
print("    ledger.csv: anchorw rc=0 wall=505 core_min=16.83")
print("    DV order control: weighted-arm dv_to_serial_perm == reinversion's: %s"
      % np.array_equal(np.load(WA + "dv_to_serial_perm.npy").astype(np.int64), perm))


def geo(f, label):
    t = np.argsort(-np.abs(f))[:K]
    print("\n  %s" % label)
    print("    G2 on this map (bar >50%%): %.4f%%" % (100 * win[t].mean()))
    for nm, m in regions + [("ON the W2 support", W2)]:
        print("      %-28s %6.2f%%  (base %5.2f%%, enrichment x%.2f)"
              % (nm, 100 * m[t].mean(), 100 * m.mean(), m[t].mean() / m.mean()))
    return t


tF = geo(gv1r, "OBJECTIVE 1: varianceU over ALL 21,000 cells (grad_eval001, reinversion)")
tW = geo(gW, "OBJECTIVE 2: Jw over 2,970 cells in two boxes (grad_anchorw, weighted arm)")
print("\n  DO THE TWO MAPS AGREE?")
print("    Spearman(|g_varU|, |g_Jw|) = %+.4f   [carries the claim]"
      % stats.spearmanr(np.abs(gv1r), np.abs(gW)).statistic)
print("    Pearson (|g_varU|, |g_Jw|) = %+.4f   [tail-dominated, reported not relied on]"
      % stats.pearsonr(np.abs(gv1r), np.abs(gW)).statistic)
print("    top-decile set overlap = %d of %d = %.2f%%   (chance 10%%)"
      % (len(set(tF.tolist()) & set(tW.tolist())), K,
         100 * len(set(tF.tolist()) & set(tW.tolist())) / K))
tI = np.argsort(-np.abs(gv1i))[:K]
print("\n    For scale, R1's OWN 'second independent baseline gradient' (same objective,")
print("    different inlet): Spearman %+.4f (R1 published +0.9450), top-decile overlap %.2f%%"
      % (stats.spearmanr(np.abs(gv1r), np.abs(gv1i)).statistic,
         100 * len(set(tF.tolist()) & set(tI.tolist())) / K))
print("    Changing the objective's support by 7x moves the geography LESS than repairing")
print("    the inlet did.")

print("""
  THE IDENTITY HAZARD, STATED. Jw is supported on the two boxes, so a high IN-WINDOW share
  of its top decile is partly derivable by construction from the mask and is not gated on.
  The leg that is NOT derivable is the share OFF the support, reachable only by adjoint
  propagation, and the upstream x<0 share in particular -- no box touches x<0.""")
off = ~W2
for nm, t in [("varianceU (obj 1)", tF), ("Jw        (obj 2)", tW)]:
    print("    %-20s top decile OFF the W2 support %6.2f%% | upstream x<0 %6.2f%%"
          % (nm, 100 * off[t].mean(), 100 * (x[t] < 0).mean()))
print("    The two upstream shares agree to %.2f percentage points."
      % abs(100 * (x[tF] < 0).mean() - 100 * (x[tW] < 0).mean()))

# ---------------------------------------------------------------- S4
rule("S4. G2's NUMERICAL REPRODUCIBILITY under a domain-decomposition change")

print("""  W4-defect-reach/run_cbfs_arm.sh copies 0/, constant/, system/ and runScript.py from
  W4-adjoint-pc-unblock/cbfs_beta and changes ONE thing: decomposeParDict to simple [4,1,1].
  Same image, same DAFOAM_SUBPC_TYPE=lu, np=4, beta == 1, same objective. Pure numerics.""")
gA = np.load(R + "W4-adjoint-pc-unblock/cbfs_beta/cbfs_beta_grad.npy")
gB = np.load(R + "W4-defect-reach/cbfs_simple411/cbfs_beta_grad.npy")
print("\n  THE ORDERING TRAP, EXHIBITED FIRST. DV order follows the decomposition, so the two")
print("  arrays are in DIFFERENT DV orders and are a permutation of one another:")
print("    max |sorted(|A|) - sorted(|B|)|  = %.3e   (they hold the same values)"
      % np.abs(np.sort(np.abs(gA)) - np.sort(np.abs(gB))).max())
print("    UNPERMUTED Spearman(|A|,|B|)     = %+.4f  and G2 would read %.4f%% vs %.4f%%"
      % (stats.spearmanr(np.abs(gA), np.abs(gB)).statistic, g2(gA)[0], g2(gB)[0]))
print("    A 17-point 'finding' is available to anyone who skips the permutation.")

mapA, mapB = dv_to_serial(R + "W4-adjoint-pc-unblock/cbfs_beta"), dv_to_serial(
    R + "W4-defect-reach/cbfs_simple411")
print("\n  POSITIVE CONTROL on the addressing parser: the map built here for arm A is")
print("    identical to the archived dv_to_serial_perm.npy, entry for entry: %s"
      % np.array_equal(mapA, perm))
print("    per-rank cell counts  A %s   B %s"
      % ([len(read_labelList("%s/processor%d/constant/polyMesh/cellProcAddressing"
                             % (R + "W4-adjoint-pc-unblock/cbfs_beta", i))) for i in range(4)],
         [len(read_labelList("%s/processor%d/constant/polyMesh/cellProcAddressing"
                             % (R + "W4-defect-reach/cbfs_simple411", i))) for i in range(4)]))
sA = np.empty(N); sA[mapA] = gA
sB = np.empty(N); sB[mapB] = gB
d = np.abs(sA - sB); rel = d / np.maximum(np.abs(sA), 1e-300)
t20 = np.argsort(-np.abs(sA))[:20]
print("\n  PERMUTED, in serial cell order:")
print("    ||A-B|| / ||A||                 = %.3e  (record publishes 1.13e-04)"
      % (np.linalg.norm(sA - sB) / np.linalg.norm(sA)))
print("    top-20 |g| cells: max rel %.3e, median rel %.3e  (record publishes 1.58e-04, 4.0e-05)"
      % (rel[t20].max(), np.median(rel[t20])))
print("    Spearman(|A|,|B|) = %+.8f" % stats.spearmanr(np.abs(sA), np.abs(sB)).statistic)
a2, ta = g2(sA, win_serial)
b2, tb = g2(sB, win_serial)
print("\n    G2  arm A (scotch)        = %.4f%%   (R1 publishes 31.19%% for this array)" % a2)
print("    G2  arm B (simple 4x1x1)  = %.4f%%" % b2)
print("    DELTA under a lever with no physics in it = %+.4f percentage points" % (b2 - a2))
print("    top-decile set agreement = %d of %d cells = %.2f%%"
      % (len(set(ta.tolist()) & set(tb.tolist())), K,
         100 * len(set(ta.tolist()) & set(tb.tolist())) / K))

# ---------------------------------------------------------------- S5
rule("S5. G-P2's STATED MECHANISM, at the one state where it can be checked")

print("""  G-P2 (S1_PRIORS_PREREGISTRATION.md S4) predicts before any compute:
    'the restoring pull at beta = 0.2 is 2*lambda_LN*log(0.2)/0.2 = 1.309e-4 against the
     Gaussian's 2*lambda_L2*(0.2-1) = 1.600e-5 -- 8.2x stronger. Prediction: the count of
     cells at the lower bound falls from 223 to fewer than 60.'
  Whether a cell unpins is not decided by prior-vs-prior. It is decided by prior pull versus
  LIKELIHOOD pull at that cell, and the likelihood pull is on disk at evaluation 10.""")
pl = 2 * 8.1335e-06 * abs(np.log(0.2)) / 0.2
pg = 2 * LL2_R * 0.8
print("\n    lognormal pull at beta=0.2 (lambda_LN 8.1335e-06) = %.4e" % pl)
print("    Gaussian  pull at beta=0.2 (lambda_L2 1e-5)        = %.4e   ratio %.2fx (prereg 8.2x)"
      % (pg, pl / pg))
pin = b10r <= 0.2 + 1e-12
print("\n    Cells at the lower bound at evaluation 10: %d of %d." % (pin.sum(), N))
print("    FRAME, stated not glossed: the FINAL state has 223 low + 1 high, but its gradient")
print("    is deleted by invert_lbfgsb.py:96-97. Evaluation 10 is the only archived state")
print("    where beta and its gradient can both be read, and it is early in the trajectory.")
if pin.sum():
    a = np.abs(LQOI_R * gv10r[pin])
    print("\n    |g_QoI| at those cells: min %.4e  p50 %.4e  max %.4e" % (a.min(), np.median(a), a.max()))
    print("    exceeding the lognormal pull %.4e : %.2f%% (%d of %d)"
          % (pl, 100 * (a > pl).mean(), (a > pl).sum(), pin.sum()))
    print("    exceeding the Gaussian  pull %.4e : %.2f%% (%d of %d)"
          % (pg, 100 * (a > pg).mean(), (a > pg).sum(), pin.sum()))
    print("    median |g_QoI| at the bound is %.1fx the lognormal restoring pull." % (np.median(a) / pl))
print("""
    Reading, bounded by the frame: at every archived pinned cell the likelihood pull already
    exceeds the stronger prior's restoring pull by a factor of several, so the 8.2x prior
    ratio does not by itself imply unpinning. n = %d is small and the state is not the one
    G-P2 grades; this is a caution on the mechanism, not a measurement of the gate.""" % pin.sum())

print("\nDONE.")
