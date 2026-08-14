"""G-P4 replacement: re-verification, negative controls, and the replacement gate.

Zero compute. Every input is an array or a log line written by a completed run,
all of them OUTSIDE the repository at /home/ubuntu/certonomous-runs/ and therefore
invisible to any repo-scoped grep. Runs as __main__ and imports no local module,
so docket D1/D1a's stale-bytecode hazard cannot apply; __pycache__ is cleared by
the caller regardless.

Frames, stated once and never mixed:
  * every array used here is in DV order, as written by the run that produced it;
  * NO permutation is applied anywhere in this file, so the DV-vs-serial trap of
    the 2026-08-14 triage section 2.4 has no surface to bite on;
  * grad_eval*.npy is the RAW d(varianceU)/d(beta) (runScript.py line 158-160,
    read), so g_QoI = LQOI * gv and g_penalty = 2*LL2*(beta-1) (invert_lbfgsb.py
    line 113, read). Both compositions are re-derived here, not assumed.
"""
import numpy as np

INV = "/home/ubuntu/certonomous-runs/S1-cbfs-inversion/"
REINV = "/home/ubuntu/certonomous-runs/S1-cbfs-reinversion/"

# From each run's own driver, read, not remembered.
LQOI_INV, LL2_INV = 6.5448114804931393e+01, 1.0e-4      # runScript_inversion.py:43-44
LQOI_RE,  LL2_RE  = 1.6257778891393064e+03, 1.0e-5      # invert_lbfgsb.py:23-24
LAM_LN = 8.1335e-06                                      # prereg 3d, the lognormal weight
S_LN = 0.75

def rule(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)

# --------------------------------------------------------------------------
rule("C0  POSITIVE CONTROL ON THE READER -- reproduce archived log lines entry for entry")
# The reinversion driver printed |g_total| into J_history_main.csv for every
# evaluation. If our composition of g_total from the two arrays is right, and if
# the two arrays are the matched pair, we reproduce those printed values. This is
# the control the triage's section 2.4 note demands before any new arithmetic.
b1_re = np.ones(21000)
gv1_re = np.load(REINV + "cbfs_inv/grad_eval001.npy")
b10_re = np.load(REINV + "cbfs_inv/beta_eval010.npy")
gv10_re = np.load(REINV + "cbfs_inv/grad_eval010.npy")
for tag, b, gv, printed in (("eval 1", b1_re, gv1_re, 1.986e-01),
                            ("eval 10", b10_re, gv10_re, 1.593e-02)):
    g = LQOI_RE * gv + 2.0 * LL2_RE * (b - 1.0)
    got = float(np.linalg.norm(g))
    print(f"  reinversion {tag:8s}  |g_total| computed {got:.6e}  "
          f"archived {printed:.3e}  agree to printed precision: {abs(got-printed)/printed < 5e-4}")
# eval 1 is beta == 1 exactly by construction of the run; check that too.
print(f"  reinversion eval 1 archived beta bmin=bmax=1.000000 in the log; "
      f"penalty term at beta=1 is exactly {2.0*LL2_RE*np.linalg.norm(b1_re-1.0):.1e}")

# --------------------------------------------------------------------------
rule("R1  REPRODUCE G-P4's THREE LEGS AND THE COSINE IDENTITY (docket D67, 2.2e-16)")
beta = np.load(INV + "cbfs_inv/beta_eval010.npy")
gv = np.load(INV + "cbfs_inv/grad_eval010.npy")
gq = LQOI_INV * gv
gp = 2.0 * LL2_INV * (beta - 1.0)
nq, npn = np.linalg.norm(gq), np.linalg.norm(gp)
ratio = npn / nq
cos = float(np.dot(gq, -gp) / (nq * npn))
rms = float(np.sqrt(np.mean((beta - 1.0) ** 2)))
gtot = gq + gp
eps = np.linalg.norm(gtot) / nq
print(f"  ratio r      = {ratio:.6f}     published 0.998441")
print(f"  cosine c     = {cos:.9f}  published 0.999542")
print(f"  rms|beta-1|  = {rms:.6f}     published 0.016502")
print(f"  |g_total|    = {np.linalg.norm(gtot):.6e}   published 1.450369e-05")
c_solved = (1.0 + ratio ** 2 - eps ** 2) / (2.0 * ratio)
print(f"\n  IDENTITY  eps^2 = 1 + r^2 - 2*r*c, solved for c:")
print(f"    c from (r, eps) = {c_solved:.15f}")
print(f"    c measured      = {cos:.15f}")
print(f"    absolute agreement = {abs(c_solved-cos):.3e}   (D67 reports 2.2e-16)")
print(f"\n  FORCED-BY-CONVERGENCE BOUND  c >= 1 - eps^2/(2r) with eps = {eps:.6e}")
print(f"    bound  = {1.0 - eps**2/(2.0*ratio):.9f}   published 0.999540922")
print(f"    actual = {cos:.9f}")

# --------------------------------------------------------------------------
rule("R2  THE HEADLINE -- treatment W reports the PRIOR as the posterior")
# A "treatment" here is exactly what a graded submission is: a bundle of reported
# quantities. Treatment W's point field is the archived MAP; its posterior is the
# prior, unchanged -- covariance = prior covariance, so every credible interval
# straddles beta = 1, the informed rank is 0, and the variance reduction is 0
# in every direction. That is the shape falsifier F1 exists to catch.
def treatment(name, beta_rep, gv_rep, lam_l2, lam_qoi, hess_eigs, post_sd, prior_sd):
    return dict(name=name, beta=beta_rep, gv=gv_rep, lam_l2=lam_l2,
                lam_qoi=lam_qoi, hess_eigs=np.asarray(hess_eigs, float),
                post_sd=np.asarray(post_sd, float), prior_sd=np.asarray(prior_sd, float))

prior_sd_vec = np.full(21000, S_LN)
W = treatment("W  prior reported as posterior", beta, gv, LL2_INV, LQOI_INV,
              hess_eigs=np.zeros(6), post_sd=prior_sd_vec, prior_sd=prior_sd_vec)
# Treatment M is the mismatched-evaluation error that produced the 1.684 confusion:
# the plateau beta paired with a gradient from a DIFFERENT evaluation.
gv1_inv = np.load(INV + "cbfs_inv/grad_eval001.npy")
M = treatment("M  plateau beta paired with the eval-1 gradient", beta, gv1_inv,
              LL2_INV, LQOI_INV, hess_eigs=np.zeros(6),
              post_sd=prior_sd_vec, prior_sd=prior_sd_vec)

def gp4_old(t, targets=(0.998441, 0.999542, 0.016502), tol=0.01):
    g_q = t["lam_qoi"] * t["gv"]
    g_p = 2.0 * t["lam_l2"] * (t["beta"] - 1.0)
    a, b = np.linalg.norm(g_q), np.linalg.norm(g_p)
    legs = (b / a, float(np.dot(g_q, -g_p) / (a * b)),
            float(np.sqrt(np.mean((t["beta"] - 1.0) ** 2))))
    rel = [abs(l - tg) / tg for l, tg in zip(legs, targets)]
    return legs, rel, all(r <= tol for r in rel)

for t in (W, M):
    legs, rel, ok = gp4_old(t)
    print(f"\n  {t['name']}")
    print(f"    legs      ratio {legs[0]:.6f}  cos {legs[1]:.6f}  rms {legs[2]:.6f}")
    print(f"    rel error {rel[0]:.1e}      {rel[1]:.1e}     {rel[2]:.1e}")
    print(f"    G-P4 (restored, ratio-and-cosine, 1%): {'PASS' if ok else 'FAIL'}")

# --------------------------------------------------------------------------
rule("R3  THE SECANT CURVATURE THAT SUPPLIES THE REPLACEMENT BAR (docket D70)")
# state A = evaluation 1 (beta == 1); state B = evaluation 10. By the mean-value
# form of the gradient map, s'y = s'Hbar s EXACTLY for the segment-averaged
# Hessian Hbar. This is not a finite difference.
s = b10_re - b1_re
y_qoi = LQOI_RE * (gv10_re - gv1_re)
y_pen = 2.0 * LL2_RE * s
sty_qoi = float(np.dot(s, y_qoi))
sty_pen = float(np.dot(s, y_pen))
ss = float(np.dot(s, s))
print(f"  ||s||           = {np.sqrt(ss):.6e}    D70 4.312344e+00")
print(f"  s'y_QoI         = {sty_qoi:+.6e}   D70 +7.313133e-01   <- MEASUREMENT")
print(f"  s'y_penalty     = {sty_pen:+.6e}   D70 +3.719261e-04   <- IDENTITY 2*lam*||s||^2, never gated on")
print(f"  R_qoi = s'y/||s||^2 = {sty_qoi/ss:+.6e}   D70 +3.932573e-02")
rho_gauss = (sty_qoi / ss) / (2.0 * LL2_RE)
print(f"  rho (Gaussian prior metric, 2*lam_L2) = {rho_gauss:.4e}   D70 1.966e+03")

# Transfer to the prior this item actually pre-registers. The lognormal penalty
# lam_LN*sum(log b)^2 has cell-wise second derivative 2*lam_LN*(1 - log b)/b^2.
def h_prior_ln(b):
    return 2.0 * LAM_LN * (1.0 - np.log(b)) / b ** 2
for tag, bstate in (("at beta == 1 (prior mode)", np.ones(21000)),
                    ("at the reinversion eval-10 field", b10_re),
                    ("at the reinversion final field", np.load(REINV + "cbfs_inv/beta_final.npy"))):
    h = h_prior_ln(bstate)
    sths = float(np.dot(s, h * s))
    print(f"  lognormal prior metric {tag:34s}: s'H_prior s = {sths:+.6e}"
          f"   rho_LN = {sty_qoi/sths:+.4e}" if sths > 0 else
          f"  lognormal prior metric {tag:34s}: s'H_prior s = {sths:+.6e} (INDEFINITE)")
h1 = h_prior_ln(np.ones(21000))
rho_ln_mode = sty_qoi / float(np.dot(s, h1 * s))
print(f"\n  A Rayleigh quotient LOWER-BOUNDS the top generalised eigenvalue, so a correct")
print(f"  rank-6 posterior on this problem returns lambda_1 at or above the numbers")
print(f"  above. They span 6.2e+01 to 2.4e+03 -- a 40x spread, driven entirely by the")
print(f"  223 cells pinned at beta = 0.2, where the lognormal prior curvature")
print(f"  2*lam*(1-log b)/b^2 is 65x its value at b = 1. THAT SPREAD IS WHY THE")
print(f"  REPLACEMENT DOES NOT BAR ON THIS NUMBER DIRECTLY: a bar at 2.4e+03 would be")
print(f"  a bar on which state the MAP lands in. It is used as the independent")
print(f"  EXPECTATION behind a bar of 10, declared in R4.")

# Negative control on the bar itself: cross-pair s and y from the two runs.
b10_inv = beta
s_inv = b10_inv - 1.0
y_inv = LQOI_INV * (np.load(INV + "cbfs_inv/grad_eval010.npy") - gv1_inv)
print(f"\n  NEGATIVE CONTROL (mismatched pair, no shared state):")
print(f"    s(reinv)'y(inv)/||s_reinv||^2 = {float(np.dot(s, y_inv))/ss:+.4e}"
      f"  against the matched {sty_qoi/ss:+.4e}")
print(f"    s(inv)'y(reinv)/||s_inv||^2   = "
      f"{float(np.dot(s_inv, y_qoi))/float(np.dot(s_inv,s_inv)):+.4e}"
      f"  against the matched {float(np.dot(s_inv,y_inv))/float(np.dot(s_inv,s_inv)):+.4e}")

# Sign-randomised null on the measurement (N3 of D70), reproduced independently.
rng = np.random.default_rng(20260814)
draws = np.array([float(np.dot(s, rng.choice([-1.0, 1.0], size=y_qoi.size) * y_qoi))
                  for _ in range(200)])
print(f"\n  NULL N3 sign-randomised y_QoI, 200 draws: mean {draws.mean():+.4e} "
      f"sd {draws.std(ddof=1):.4e}  ->  measured is "
      f"{(sty_qoi - draws.mean())/draws.std(ddof=1):.1f} sd from the null")

# --------------------------------------------------------------------------
rule("R4  THE REPLACEMENT GATE, EVALUATED -- and the negative controls firing")
# ---------------------------------------------------------------------------
# The bars, pre-registered here and nowhere else.
#
# BAR_A: lambda_1 of the prior-preconditioned data-misfit Hessian, in the metric
#   of the prior the run itself reports. Bar 10. INDEPENDENT EXPECTATION, declared
#   before the run so it cannot later be presented as a triumph: the secant
#   Rayleigh quotient measured in R3 lower-bounds lambda_1 at between 6.2e+01 and
#   2.4e+03 across the state band, so this bar is expected to pass with 6x to 240x
#   margin. It is set at 10 and not at the measured value BECAUSE that measurement
#   moves 40x with the state the lognormal prior Hessian is evaluated at -- driven
#   by the 223 cells pinned at beta = 0.2, where 2*lam*(1-log b)/b^2 is 65x its
#   value at b = 1. A bar at the measured value would be a bar on which state the
#   MAP lands in, which is not what this gate is asking.
# BAR_B: the first Hessian-vector product, taken along the direction s fixed in
#   R3, must reproduce s'H s = +7.313133e-01 within a factor of 3.
# BAR_C: the per-cell posterior spread must be traceable to the reported spectrum.
# ---------------------------------------------------------------------------
BAR_A = 10.0
STS_REF = sty_qoi          # +7.313133e-01, measured in R3 from archived arrays
BAR_B = 3.0                # multiplicative band, either side

def gp4_new(t):
    lam = np.asarray(t["hess_eigs"], float)
    lam1 = float(lam.max()) if lam.size else 0.0
    legA = "PASS" if lam1 >= BAR_A else "FAIL"
    band = (STS_REF / BAR_B, STS_REF * BAR_B)
    legB = "PASS" if band[0] <= t["hv_sts"] <= band[1] else "FAIL"
    # Leg C, two sided, and the bound is a RANK bound rather than a per-cell one.
    # For a rank-k Laplace posterior Gamma_post = Gamma_pr - Gamma_pr^0.5 V D V'
    # Gamma_pr^0.5 with D_i = lam_i/(1+lam_i) and V orthonormal, the TOTAL variance
    # a treatment is entitled to remove is
    #     sum_j (var_pr,j - var_post,j) = s^2 * sum_i D_i  <=  k * s^2.
    # With k = 6 and 21,000 cells that ceiling is 0.03% of the total prior
    # variance. This is section 5's rank disclosure -- "posterior marginal
    # variances will equal the prior variance in every direction outside that
    # subspace" -- turned into a number a submission can be scored against.
    removed = float(np.sum(t["prior_sd"] ** 2 - t["post_sd"] ** 2))
    entitled = float(S_LN ** 2 * np.sum(lam / (1.0 + lam))) if lam.size else 0.0
    legC = "PASS" if (removed > 0.0 and removed <= entitled * 1.01
                      and lam.size >= 6 and np.all(np.isfinite(lam))
                      and np.all(lam >= 0)) else "FAIL"
    verdict = "PASS" if legA == legB == legC == "PASS" else "FAIL"
    return dict(lam1=lam1, sts=t["hv_sts"], removed=removed,
                entitled=entitled, legA=legA, legB=legB, legC=legC,
                verdict=verdict)

def mk(name, beta_rep, gv_rep, eigs, post_sd, hv_sts):
    return dict(name=name, beta=beta_rep, gv=gv_rep, lam_l2=LL2_INV,
                lam_qoi=LQOI_INV, hess_eigs=np.asarray(eigs, float),
                post_sd=np.asarray(post_sd, float), prior_sd=prior_sd_vec,
                hv_sts=float(hv_sts))

# W -- the prior reported as the posterior. rank 0, no curvature computed, so the
# Hv it would report is the PRIOR curvature along s, which R3 measured as the
# identity 2*lam_L2*||s||^2 = 3.72e-04.
W2 = mk("W  prior reported as posterior", beta, gv, np.zeros(6),
        prior_sd_vec, sty_pen)
# M -- the mismatched-evaluation error, carried through to the Hv as well.
M2 = mk("M  plateau beta paired with the eval-1 gradient", beta, gv1_inv,
        np.zeros(6), prior_sd_vec, sty_pen)
# Z -- a spectrum computed from the prior alone: eigenvalues identically 1.
Z2 = mk("Z  spectrum taken from the prior alone (eigenvalues == 1)", beta, gv,
        np.ones(6), prior_sd_vec * (1.0 / np.sqrt(2.0)), sty_pen)
# The stand-in posterior spread used by H and R below, CONSTRUCTED rather than
# asserted: six orthonormal directions, each an equal-weight bump over a disjoint
# block of 3,500 cells, and the per-cell posterior variance that a rank-6 Laplace
# with spectrum lamR actually produces from them. Building it this way rather
# than picking numbers is what made leg C's first draft visibly wrong: a draft
# that tightened 2,000 cells by 97% was not a rank-6 posterior at all, and the
# rank bound below is what said so.
lamR = rho_ln_mode * np.array([1, .31, .10, .031, .010, .0031])
V = np.zeros((21000, 6))
for i in range(6):
    V[i * 3500:(i + 1) * 3500, i] = 1.0 / np.sqrt(3500.0)
D = lamR / (1.0 + lamR)
var_post = S_LN ** 2 * (1.0 - (V ** 2 * D).sum(axis=1))
post_sd_R2 = np.sqrt(var_post)
print(f"  stand-in rank-6 posterior: total prior variance {21000*S_LN**2:.1f},"
      f" variance removed {float(np.sum(prior_sd_vec**2-post_sd_R2**2)):.4f}"
      f" = {100*float(np.sum(prior_sd_vec**2-post_sd_R2**2))/(21000*S_LN**2):.4f}%"
      f" of it; largest per-cell sd reduction {100*float((1-post_sd_R2/prior_sd_vec).max()):.4f}%")
print(f"  THAT is what rank 6 in 21,000 dimensions looks like, and section 5 says so.\n")
# H -- correct science, broken instrument: the Hv is computed in the WRONG frame.
#   Exhibited with a real number rather than an invented one: R3's cross-pairing
#   control, s from one run against y from the other.
sts_wrong = float(np.dot(s, y_inv))
H2 = mk("H  correct spectrum, Hessian-vector product in the wrong frame", beta,
        gv, lamR, post_sd_R2, sts_wrong)
# Q -- asserted error bars: a real spectrum, but per-cell intervals 10x tighter
#   than a rank-6 posterior with that spectrum can produce. This is G-P3's
#   "error bars asserted rather than computed", made scoreable.
post_sd_Q = prior_sd_vec * 0.02   # a 98% tightening in every one of 21,000 cells
Q2 = mk("Q  real spectrum, credible intervals asserted not derived", beta, gv,
        lamR, post_sd_Q, STS_REF)
# R -- a genuine rank-6 low-rank Laplace posterior. STAND-IN, and labelled one:
#   the leading eigenvalue is set to the secant Rayleigh quotient measured in R3,
#   which is a lower bound on what a correct computation returns, and the tail
#   decays geometrically. This is not a prediction of the run's spectrum and is
#   evidence about the GATE only, never about the experiment.
R2t = mk("R  a genuine rank-6 low-rank Laplace posterior (stand-in)", beta, gv,
         lamR, post_sd_R2, STS_REF * 1.4)

print(f"  BAR_A lambda_1 >= {BAR_A:.0f}")
print(f"  BAR_B  s'Hs in [{STS_REF/BAR_B:.4e}, {STS_REF*BAR_B:.4e}]  around the archived {STS_REF:.6e}")
print(f"  BAR_C  0 < total variance removed <= s^2 * sum_i lam_i/(1+lam_i), the rank bound\n")
print(f"  {'treatment':56s} {'OLD':>5s} {'NEW':>5s} A/B/C   lambda_1     s'Hs        var removed/entitled")
for t in (W2, M2, Z2, H2, Q2, R2t):
    _, _, old_ok = gp4_old(t)
    n = gp4_new(t)
    print(f"  {t['name']:56s} {'PASS' if old_ok else 'FAIL':>5s} {n['verdict']:>5s}"
          f"  {n['legA'][0]}/{n['legB'][0]}/{n['legC'][0]}"
          f"   {n['lam1']:.3e}  {n['sts']:+.3e}  {n['removed']:.4g} / {n['entitled']:.4g}")
print()
print("  READ THIS AS THE 2x2 IT IS. The OLD gate cannot tell W, Z, Q or R apart:")
print("  it returns PASS for all four, because none of its three legs is a function")
print("  of any covariance, credible interval or Hessian. The NEW gate returns PASS")
print("  for R alone. W fails all three: no curvature computed, so leg A gets 0, leg B")
print("  gets the prior identity 2*lam*||s||^2 back, and leg C sees no interval move.")
print("  Z fails all three too, and differently: it read its spectrum off the prior,")
print("  so lambda_1 is identically 1 and its intervals remove 5,906 units of variance")
print("  against an entitlement of 1.69. H fails leg B alone, which is the point of B --")
print("  the science is right and the instrument is in the wrong frame; Q fails leg C")
print("  alone: it removes 11,808 units of variance where a rank-6 posterior with its")
print("  own reported spectrum is entitled to remove 3.37, a factor of 3,500.")
print()
print("  M is the mismatched-evaluation error that produced the 1.684 confusion. It")
print("  is the one treatment the OLD legs DO catch, which is why they are retained")
print("  under their own name as G-P4a, the gradient reproduction control, rather")
print("  than deleted. G-P4a FAILS M at ratio 0.501974 against 0.998441.")

rule("R5  IDENTITY TEST APPLIED TO THE REPLACEMENT ITSELF (the two W-2 questions)")
print("  Q1  WHAT RESULT WOULD MAKE THIS GATE FAIL?")
print("      Leg A: lambda_1 < 10 at the lognormal MAP, i.e. the data does not beat")
print("        the prior by 10x in even its single best direction. Reachable: it is")
print("        the neighbourhood of falsifier F2, and it is what an ill-posed inverse")
print("        problem with a 21,000-dimensional parameter and 6 informed directions")
print("        may genuinely look like once the prior is widened from sigma 0.043.")
print("      Leg B: the first Hessian-vector product returning s'Hs outside")
print(f"        [{STS_REF/BAR_B:.3e}, {STS_REF*BAR_B:.3e}]. Reachable: the finite-difference")
print("        step, the sign convention, and the design-variable ordering are each")
print("        capable of moving it, and R3's cross-pair control moves it by two")
print("        orders of magnitude, far outside the band.")
print("      Leg C: intervals that do not move, or that remove more variance in")
print("        total than the reported rank and spectrum entitle them to. Both")
print("        exhibited above, by W and Z on the lower side and by Q on the upper.")
print()
print("  Q2  COULD A WRONG TREATMENT STILL PASS?")
print("      YES, and the holes are named rather than papered over.")
print("      (i) A treatment whose lambda_1 is right and whose EIGENVECTORS are")
print("          wrong passes all three legs. Leg C bounds the magnitude of the")
print("          interval tightening, not its location. Closing that needs a second")
print("          external referent on a direction, which this stage does not have.")
print("      (ii) A treatment that reports the archived secant value back instead of")
print("          computing an Hv passes leg B. Mitigation, pre-registered: the run")
print("          must ALSO report the raw Hv vector, its norm, the finite-difference")
print("          step used, and the symmetry check v1'Hv2 against v2'Hv1 that section")
print("          5 already requires, with v2 drawn from numpy default_rng(20260814),")
print("          a direction whose curvature is on no disk in this lab.")
print("      (iii) The MAP arm itself is not graded by this gate at all. G-P1, G-P2")
print("          and F3 grade it. This gate grades the posterior only, which is what")
print("          the strategy PROOF clause asks for and what G-P4 never did.")
print()
print("  Q3  IS ANY LEG DERIVABLE BY CONSTRUCTION FROM ITS OWN INPUTS?  (rule W-2)")
print("      Leg A: no. lambda_1 needs Hessian-vector products, which need adjoint")
print("        solves. No closed form in (beta, lambda) supplies one.")
print("      Leg B: no, in BOTH directions. The reference value s'y_QoI needs")
print("        grad_eval010 from a run this item does not perform; the reported")
print("        value needs an adjoint solve this item does perform. Two independent")
print("        computations of the same scalar.")
print("      Leg C: PARTIALLY, and it is scored accordingly. The entitlement ceiling")
print("        s^2*sum_i lam_i/(1+lam_i) IS derivable from the spectrum, so the UPPER side of")
print("        leg C is a consistency check on the treatment's own arithmetic and")
print("        adds no information about nature. The LOWER side is not derivable and")
print("        is what fails W. Stated here so nobody later reads leg C as evidence.")
print("      The quantity in this whole analysis that IS a pure identity --")
print("        s'y_penalty = 2*lam_L2*||s||^2, printed in R3 -- is reported and is")
print("        gated on nowhere, which is what rule W-2 prescribes.")
