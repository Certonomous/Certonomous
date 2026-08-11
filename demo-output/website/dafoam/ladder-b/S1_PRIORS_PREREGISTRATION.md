# S1-with-priors — pre-registration: the regularization derived from a stated prior, and a posterior on beta instead of a point field

**Written 2026-08-11, 16:5x UTC, at repo commit `7d9e4c51`.** Item
`s1-regularization-chosen-by-prior-theory-with-a-posterior-on-beta`
(`agenda/proposals/`, filed 2026-08-10T15:10Z). This is
`CAPABILITY_STRATEGY.md` §5 sequencing item 2 — one of the three things named there as
making Stage 2 *publishable, not just runnable* — and it is the named TRIGGER that
unblocks `s1-cbfs-w1-only-arm` (that proposal's `decision_note`, chief ruling
`7b758783`).

## 0. Timing and compute claims, made checkable rather than asserted

`campaign/B52_RUNG7_PREREGISTRATION.md` certified its own timing with two clauses that
are false against filesystem birth times. This section is written so that a reader can
check every claim it makes, and so that the claims are narrow enough to survive the
check.

1. **No solver has run for this item, by any agent, at this writing.** Checkable three
   ways: (a) `ls /home/ubuntu/certonomous-runs/` contains
   `S1-cbfs-inversion`, `S1-cbfs-reinversion`, `S1-cbfs-weighted-arm`, `S1-fiml`,
   `r4-ahmed-c3s1` — **there is no run directory for this item**, and this item's
   directory name is pre-declared here as `S1-priors` so its later existence is
   evidence of the launch, not of the writing; (b) `sudo docker ps` at this writing
   returned a header row and no containers; (c) this item has no `ledger.csv`, and §5
   below requires one to exist before any evaluation is billed.
2. **The author of this file launched no solver and no inversion.** Compute
   authorisation for this item is Katie's and has not been given. The item additionally
   carries `"sequencing": "SEQUENCING, BLOCKED UNTIL POST-SEND"` in its own proposal —
   it is not dispatchable until the post-send month is declared open. **Writing this
   pre-registration is not a dispatch and does not unblock it**; the proposal's own text
   asks for exactly this ("filed now so the design is priced, pre-registered and argued
   before the month opens").
3. **Every number in §2–§4 below was computed host-side from fields already on disk**,
   written by completed runs (`S1-cbfs-reinversion/cbfs_inv/2500/`,
   `S1-cbfs-inversion/fields_beta.npy`, `closure-challenge-benchmark/data/CBFS/0/U`).
   Zero solver core-min were spent producing them. The scripts are standalone
   `__main__` programs importing only `numpy`/`re`/`sys`.
4. **Bytecode-staleness disclosure** (docket D1, and the fleet correction of
   2026-08-11 that `PYTHONDONTWRITEBYTECODE=1` does *not* defeat a stale `.pyc` because
   it stops writing, not reading): the analysis here is not a mutation test and does not
   edit-and-re-import any module. Checked, not assumed — neither analysis script has
   cached bytecode (`__pycache__` contains no `inletcheck`/`prior_derive` entry), both
   run as `__main__` (never cached by construction), and neither imports a
   scratchpad-local module. **Any script this item later runs in an edit-run-restore
   loop must delete `__pycache__` between cells or set `PYTHONPYCACHEPREFIX`; the
   `PYTHONDONTWRITEBYTECODE` instruction is void.**

*Nothing below this line is a measured outcome of this item. Every threshold, cap,
prediction and label in §3–§7 is committed before any evaluation of this item runs.*

---

## 1. Where the S1 family actually stands — read this before treating anything below as new

This file is **not** an objective-repair spec and **not** a first re-inversion spec. Both
were written, pre-registered, executed and published between 2026-08-07 and 2026-08-08.
A reader arriving with the older framing should re-anchor here:

| item | status | result |
|---|---|---|
| `s1-cbfs-field-inversion-run` | **done**, 335.98/600 core-min | both gates FAIL; inlet defect diagnosed |
| `s1-cbfs-objective-repair-and-reinversion` | **done**, 424.80/450 core-min | inlet repaired; baseline collapsed 24.8x; **G1 PASS** (0.25847 vs ≤0.70); **G2 FAIL** (26.9% vs >50%) |
| `s1-cbfs-weighted-loss-offline-variant` | **done**, 0 core-min | verdict CAPTURABLE |
| `s1-cbfs-weighted-reinversion-arm` | **done**, 267.07/278 core-min | gates A,B PASS; **G1w FAIL** (0.05710 vs ≤0.05320); **G2 FAIL** (42.7% vs >50%) |
| `s1-cbfs-continuation-arm` | proposed, unrun | — |
| `s1-cbfs-w1-only-arm` | proposed, **NO-GO pending this item** | — |
| **this item** | **proposed, unrun, blocked until post-send** | — |

Records: `S1_CBFS_INVERSION_RESULT.md`, `S1_CBFS_REINVERSION_RESULT.md`,
`S1_CBFS_WEIGHTED_LOSS_VARIANT.md`, `S1_CBFS_WEIGHTED_ARM_RESULT.md`, each with its own
pre-registration.

**The gate question, answered by execution rather than restated here.** G1 *was*
re-derived against the repaired baseline (λ_QoI re-based to 1/6.1509e-4; the ≤0.70
*relative* bar kept) and it passed at 0.25847. G2's >50%-in-window bar was kept unchanged
across three runs and failed three times (29.0%, 26.9%, 42.7%); the entry-12 ruling
closed G2-bar *revisions* explicitly. So the bars are not this item's to re-open.

**What is still open, and what this item must decide:** the weighted arm measured
top-decile membership at **42.7% inside the metric window** but **79.7% inside the loss
support** (0.0% at y>2). Whether the localization question G2 exists to ask is already
answered by the second number is an open supervisor reading, and the W1-only arm was
put NO-GO precisely because *this* item "must decide loss support anyway". §3d below
pre-registers that decision.

## 2. The premise, re-verified against the files rather than inherited

The whole family rests on the inlet diagnosis. It was re-verified for this
pre-registration by reading the `0/U` boundary fields directly (frame: the `inlet` patch
of each file; parser reads the patch's own `value nonuniform List<vector>` block):

| file | md5 (whole file) | inlet faces | Ux min → max | Ux mean | Uy | Uz vs benchmark |
|---|---|---|---|---|---|---|
| `closure-challenge-benchmark/data/CBFS/0/U` | `513e83d2…` | **150** | 0.202035889 → 1.00537467 | **0.9149216132** | 111 distinct | — |
| `S1-cbfs-inversion/cbfs_inv/0/U` (pre-repair) | `f71eccf0…` | **150** | **0.72 → 0.72** (1 distinct value) | **0.72** | **all exactly 0** | **max abs diff exactly 0** |
| `S1-cbfs-reinversion/cbfs_inv/0/U` (repaired) | `e1187631…` | 150 | 0.202035889 → 1.00537467 | 0.9149216132 | 111 distinct | diff 0 |
| `S1-cbfs-weighted-arm/cbfs_inv/0/U` | `e1187631…` | 150 | identical to repaired | | | diff 0 |

**Verdict: the diagnosis verifies on every number.** 150 faces; 0.72 uniform with Uy
identically zero; the benchmark's 0.202→1.005 profile at bulk 0.9149216132; bulk ratio
0.9149216/0.72 = **1.2707**, the 27% mass-flux mismatch. The Uz columns of the benchmark
and the corrupted file agree to **exactly zero difference** while their Ux columns differ
by up to 0.517964 — so the overwrite fingerprint holds, and the comparator that reported
"no difference" in Uz is demonstrably capable of reporting a difference (positive control
on the negative).

**Positive control on the whole reader**, before any new arithmetic was trusted: the same
parser was used to recompute the *published* reinversion audit from the written fields.
It reproduces `varianceU` = 1.5897973285391019e-04 against the published
1.5897973285391003e-04 (15 significant digits), the y>2 loss share 77.6%, G2 26.9%,
window base rate 8.4%, top-decile-below-1 75.6%, pinned 223 low / 1 high,
J_qoi 0.25846573, penalty fraction 1.58%, rms|β−1| 0.1396 — **every published figure,
to the digits published**.

## 3. The prior, derived — this is the item's substance

### 3a. The likelihood, written down

Treat each of the 3N = 63,000 velocity components as `d = u(β) + ε`, `ε ~ N(0, σ_d²)`
i.i.d. Then, with `varianceU = (1/3N)·Σ|u−d|²` as DAFoam computes it,

```
−log posterior  =  (3N/2σ_d²)·varianceU  +  (1/2σ_β²)·Σ(β−1)²          [Gaussian prior]
J/λ_QoI         =  varianceU             +  (λ_L2/λ_QoI)·Σ(β−1)²
⇒   λ_L2/λ_QoI  =  σ_d² / (3N·σ_β²)
```

The penalty's value **and gradient** are composed host-side in the driver
(`S1-cbfs-reinversion/invert_lbfgsb.py:111–114`: `pen = LL2*sum((x-1)**2)`,
`g = LQOI*gv + 2*LL2*(x-1)`), verified by reading that file. **Changing the prior's form
is therefore a host-side edit only — no DAFoam change, and no new FD gate on the
objective**, because the objective DAFunction is untouched. That is what makes this item
affordable.

### 3b. What the three runs' conventional λ actually meant as priors

Inverting the relation above at the measured noise scale of §3c:

| run | λ_QoI | λ_L2 | **implied σ_β** | prior mass β<0 | prior mass β<0.2 |
|---|---|---|---|---|---|
| equal-weight, corrupted | 65.448 | 1e-4 | **0.043** | 0.00% | 0.00% |
| equal-weight, repaired | 1625.78 | 1e-5 | **0.676** | **6.96%** | **11.85%** |

**Two findings, both new, both zero-compute.**

1. The two equal-weight runs used **priors 16x apart in standard deviation** while
   describing the change as "λ_L2 re-tuned, 10x cut, disclosed". A 10x cut in λ is a
   ~3.2x widening of σ_β at fixed λ_QoI — but λ_QoI *also* moved 24.8x when the baseline
   collapsed, and the two effects compound. Nobody computed σ_β, because the convention
   is stated in λ and not in σ.
2. The repaired run's prior puts **6.96% of its mass on β < 0** — physically impossible
   (a negative multiplier flips the sign of omega production) — and 11.85% below the
   pre-registered lower bound 0.2, against 223/21000 = 1.06% of cells actually landing
   there. A Gaussian centred at 1 with σ_β = 0.676 is not a weak prior on a positive
   multiplier; it is a prior that is partly nonsense, held in check by the bound box.

*Caveat stated rather than buried:* the weighted arm's λ_QoI normalises a **raw** Σd²
over the W2 support, not a per-cell mean over all cells, so its σ_β is not directly
comparable on this formula and is deliberately omitted from the table. Its provenance row
is in `S1_CBFS_WEIGHTED_ARM_RESULT.md`.

### 3c. The noise scale σ_d, estimated from data rather than assumed

`S1_CBFS_REINVERSION_RESULT.md` §4 argues, from measurement, that the residual left at
y > 2 after the repair is *"reference-vs-RANS mismatch at the LES interpolation level,
not closure physics"* — the region the inversion could move only −21.6% while moving the
window −94.9%. That argument is the licence to read that residual as data noise.

Measured on the repaired MAP fields (14,616 cells at y>2, 69.6% of the domain):

```
σ_d = sqrt( Σ_{y>2}|u−d|² / (3·N_{y>2}) )  =  0.013315      ( = 1.46% of bulk U )
```

**This is an upper bound on σ_d**, because it also absorbs any genuine RANS error and
any incomplete convergence in the free channel. Its downward bias from being evaluated at
an optimum is small *in this region specifically*, since this is the region the optimizer
demonstrably could not reduce. **Pre-registered sensitivity band: σ_d ∈ [0.5×, 1.0×] of
0.013315.** Because λ ∝ σ_d², that is a 4x band on λ, and §4 requires the derived λ to be
reported across it.

### 3d. The prior this item pre-registers

**Form: lognormal.** `log β ~ N(0, s²)`, penalty `λ_LN·Σ(log β_j)²`, gradient
`2·λ_LN·log(β)/β` — analytic, host-side, one-line change at the driver site verified in
§3a.

**Grounds, stated so a reader can disagree with them specifically:** (i) β multiplies a
production term, so β > 0 is required by the physics and a prior with 6.96% mass on β<0
is indefensible on its face; (ii) the correction is multiplicative, so the natural
symmetry is in log β, not in β; (iii) the bound box [0.2, 4.0] is wildly asymmetric in β
(0.8 below, 3.0 above) but nearly symmetric in log β ([−1.609, +1.386]).

**Scale: s = 0.75, chosen so that the prior's 95% interval IS the pre-registered bound
box.** ±2s in log β gives β ∈ [0.223, 4.482] against the bounds [0.2, 4.0]. The prior is
thereby derived from the *same physical reasoning that set the bounds* rather than from
Wu/Zhang's penalty-fraction convention. (s = 0.693 matches the upper bound exactly,
s = 0.805 the lower; 0.75 is the midpoint and is pre-declared now, not tuned.)

**Resulting λ:**

```
λ_LN = λ_QoI·σ_d² / (3N·s²) = 1625.778 × 0.013315² / (63000 × 0.75²) = 8.1335e-06
```

σ_d band: λ_LN ∈ [2.0334e-06, 8.1335e-06].

**Loss support (the decision the W1-only arm is waiting on): equal-weight, all cells.**
Pre-registered and argued: a prior-theoretic treatment must not have its likelihood
support chosen to make a gate pass. The weighted arm already demonstrated that
localization follows the loss support cell-for-cell, so a restricted support would make
the posterior's spatial structure a restatement of the mask rather than an inference. The
W1-only arm's question is therefore **not** consumed by this item and is released back to
the chief as a separate go/no-go, with this item's reason recorded.

## 4. Gates, fixed now

The strategy PROOF clause is *"S1's regularization chosen by theory (prior
interpretation), posterior uncertainty on beta reported, not just a point field."*
Operationalised in four gates, all required.

- **G-P1 — the λ is derived, not matched.** The derivation of §3a–§3d is executed at the
  measured σ_d and its band, and the resulting λ_LN is reported against the three values
  already used. **A value chosen to match a previous run fails this gate.** Note the
  derived λ_LN = 8.13e-6 is already 0.81× the 1e-5 in use, so the *magnitude* will land
  near convention — that is a real result and is pre-declared here so it cannot be
  presented later as a derivation triumph. **The experiment is the prior's FORM, not its
  magnitude.**
- **G-P2 — the pinning prediction, stated before the run.** Under the lognormal prior the
  restoring pull at β = 0.2 is `2λ_LN·log(0.2)/0.2` = 1.309e-4 against the Gaussian's
  `2λ_L2·(0.2−1)` = 1.600e-5 — **8.2× stronger**. **Prediction: the count of cells at the
  lower bound falls from 223 to fewer than 60.** PASS if < 60; recorded as a wrong
  prediction, loudly, if ≥ 223; the band between is reported as a partial.
- **G-P3 — the posterior is a posterior.** The reported product is, at minimum, per-cell
  credible intervals on β over all 21,000 cells and the prior mass on the truncation
  bound, **plus the leading spectrum of the prior-preconditioned Hessian** that the
  intervals were built from. A point field with error bars asserted rather than computed
  fails.
- **G-P4 — the posterior reproduces the plateau balance it claims.** The corrupted run's
  stationary point is where the prior pull cancels the likelihood gradient.

  > **[RESTORED 2026-08-11 by the chief supervisor. §8's correction is WITHDRAWN — the
  > triple reconciles — so the re-basing it justified is reversed. The superseded wording
  > is retained immediately below, struck, per the supersession rule.]**
  >
  > **The gate is the ratio AND the cosine**, against the plateau state (**eval 10**, the
  > matched `beta_eval010.npy` / `grad_eval010.npy` pair, evals 11–17 agreeing in J to seven
  > digits): **ratio 0.998441, cos 0.999542**, with rms‖β−1‖ **0.016502** as the third leg.
  > A posterior treatment that cannot recover **all three** to 1% fails its own control.
  >
  > **Why not the analytic quantity alone**, which is the tempting simplification and was the
  > mistake: `|g_penalty| = 2·λ_L2·‖β−1‖₂` is an **identity**. Any treatment that knows λ_L2
  > and β reproduces it exactly — **including one whose posterior is wrong.** It cannot
  > fail, so it cannot be a control. The **cosine** is the informative leg: it is the only
  > number here that carries whether the prior pull actually *opposed* the likelihood
  > gradient, which is the claim the gate exists to test.
  >
  > **State the frame with the number when this is graded.** The whole 1.684 confusion came
  > from pairing a plateau-state ratio and cosine with a gradient norm reported at eval 16.
  > `‖g_total‖` moves by a factor 1.6 between those evaluations while the ratio and cosine
  > move in the fourth decimal, so a mismatched state is invisible in two of the three
  > numbers and dominant in the third.

  ~~**The control target is re-based here** (see §8): `|g_penalty| = 2·λ_L2·‖β−1‖₂ =
  4.785304e-04`, computed exactly and analytically from `fields_beta.npy` on disk
  (‖β−1‖₂ = 2.392652, rms 0.016511 against the published 0.0165), **not** from the published
  ratio/cosine pair, which §8 shows is not self-consistent. A posterior treatment that
  cannot recover this number to 1% is reported as failing its own control.~~

## 5. Caps, cost basis, stopping rule

**The proposal's filed `est_core_min` of 150 is underpriced for its own gate G-P3, and
this pre-registration says so.** The arithmetic:

| stage | core-min | basis |
|---|---|---|
| prior derivation, provenance, σ_d, §8 re-basing | **0** | already executed for this file, host-side on written fields |
| MAP arm under the lognormal prior, warm-started from `beta_final` | ~120 | 6 evaluations × ~20 core-min; the 20 is measured — weighted arm billed 19–20/eval uncontended at `-primalTol 1e-8`, `--cpus=2` |
| final-state cold control + field/centres write-out | ~9 | measured 8.10 (reinversion) and 8.54 (weighted arm) |
| Hessian-vector products for the low-rank posterior | ~120 | 6 Hv × ~20; one-sided FD of the adjoint gradient sharing the MAP gradient, so 1 evaluation per Hv |
| **hard cap, everything included** | **260** | |

Repricing rationale, stated plainly: a posterior over β needs curvature, and this stack
exposes gradients, so curvature costs gradient evaluations. The filed proposal's line
that the posterior "rides the arm's converged fields at no additional solver time" is not
achievable for per-cell credible intervals; 150 buys the arm and roughly one Hv. The
proposal JSON is amended to 260 alongside this file.

- **Rank limit, disclosed in advance:** 6 Hv gives a **rank-6** low-rank Laplace
  approximation in a 21,000-dimensional parameter space. Posterior marginal variances
  will equal the prior variance in every direction outside that subspace. **This is
  reported as the result, not hidden**: an ill-posed inverse problem in which the data
  informs a handful of directions is the honest finding, and it is what a Bayesian
  treatment exists to expose.
- **FD protocol, inherited from a paid-for lesson:** Hv by finite-differencing the
  adjoint gradient is the same hazard class that cost the reinversion 23.97 core-min —
  at `primalMinResTol` 1e-6 central FD missed the adjoint by fd/adj ≈ 0.7. **Every Hv
  runs at `-primalTol 1e-8`**, non-negotiable, and the first two Hv are checked for
  symmetry (`v₁ᵀHv₂` vs `v₂ᵀHv₁`) as a free control before the remaining four are bought.
  Asymmetry > 5% stops the item and is reported.
- **Iteration cap:** 6 MAP evaluations, 6 Hv. **Stop rule:** the driver's own budget
  guard refuses to launch any evaluation whose projected completion crosses **245**
  cumulative core-min, reserving 15 for the write-out. A run stopped by the cap is
  recorded **budget-capped, not converged** (charter §4).
- **Ledger:** `S1-priors/ledger.csv`, START/END epochs per line, written before the first
  evaluation is billed.
- **Concurrency:** `--cpus=2` if another agent is solving, `--cpus=4` if the box is free;
  recorded per launch. The weighted arm's evals 1–2 billed 27.1/26.5 against a 18.9
  uncontended basis under A3 contention — that ~16 core-min is exactly what cost it its
  8th evaluation, so contention is logged, not absorbed.

## 6. What would falsify the closure hypothesis — as distinct from disappointing it

The hypothesis on trial: *a per-cell multiplicative correction to the SST omega
production term, inferred from CBFS LES velocity data, is an identified model-form
correction rather than an artifact of an under-regularized ill-posed fit.*

**Falsifiers — any one of these kills it, and each is reachable within the cap:**

- **F1.** The posterior credible intervals straddle β = 1 in a **majority of the
  separated-flow window cells**. Then the −94.9% window error reduction is a fit the data
  does not constrain, and the point field cannot be published as an identified
  correction. This is the sharpest falsifier and it is a live possibility.
- **F2.** The leading prior-preconditioned Hessian eigenvalues are all ≫ 1 and show **no
  decay across the six computed**. Then the problem is not effectively low-dimensional,
  no finite-rank posterior is defensible at any affordable rank, and the parameterization
  itself (not the objective, not the prior) is the obstruction — which promotes the
  Dow-style nu_t-discrepancy alternative from "named alternative" to "indicated". Note
  this falsifier also invalidates this item's own posterior; it is reported as such.
- **F3.** The theory-derived prior collapses the window fix — window error reduction
  falls below 50% against the achieved 94.9%. Then the correction was being carried by an
  almost-flat prior, and the convention was doing load-bearing work nobody had accounted
  for.

**Disappointing but not falsifying:** the derived λ lands near 1e-5 (it will —
§4 G-P1 pre-declares 0.81×), the pinning drops as predicted, the posterior is
computable, and the gates land where they already are. That outcome confirms the
convention was defensible by luck and gives this line its first *derived* prior. It is a
weak result and will be labelled one.

## 7. What this item cannot establish

Cannot: any benchmark score; any generalization claim (CBFS is the field-inversion
**training** case and the loss reads only its own LES — leakage position unchanged from
`S1_CBFS_REINVERSION_RESULT.md` §5); any like-for-like comparison with Wu/Zhang, whose
inversion is on the **destruction** term (C2, R6 — the production-term label binds here
as in every S1 file); anything about the destruction term itself
(`w3-beta-on-omega-destruction-model-patch`); and — at rank 6 — any claim that the
posterior is *tight*, only claims about the directions actually computed.

## 8. ~~Correction: the published plateau-balance triple is not self-consistent~~ — **WITHDRAWN 2026-08-11**

> **[WITHDRAWN 2026-08-11 by the chief supervisor. The section below is retained in full,
> unedited, per the supersession rule — it is wrong, and deleting it would remove the
> evidence of how.]**
>
> **The triple reconciles.** An independent agent recomputed it from the run's own archived
> matched pair — `beta_eval010.npy` with `grad_eval010.npy`, both in DV order, written by the
> same `run_eval` call — and got **ratio 0.998441, cos 0.999542, rms‖β−1‖ 0.016502** against
> the published **0.998 / 0.9995 / 0.0165**. Three for three. The governing identity
> `‖g_total‖ = |g_QoI|·√(1+r²−2rc)` closes to **six digits**, so the triple is internally
> self-consistent.
>
> **Where the 1.684 came from.** The section below combines the plateau-state ratio and
> cosine with `‖g‖₂ = 9.011e-06`, which the trajectory table reports at **eval 16 — a
> different state.** Near-cancellation is what makes the mix bite: `‖g_total‖` moves
> 1.45e-05 → 9.01e-06 (a factor 1.6) between eval 10 and eval 16, while the ratio and cosine
> move only in the fourth decimal. Evals 11–17 agree in J to seven digits, so **eval 10 is
> the plateau** and a matched gradient was on disk the whole time. Nothing needed
> re-deriving.
>
> **Why the withdrawal matters more than the arithmetic.** §4's gate G-P4 was re-based, on
> the strength of this section, onto `|g_penalty|` **alone** — and
> `|g_penalty| = 2·λ_L2·‖β−1‖₂` is an **identity**. Any treatment that knows λ_L2 and β
> reproduces it exactly, **including one whose posterior is wrong.** The re-basing therefore
> removed the only half of the control that tests the *balance*: the **cosine** is the part
> carrying whether the prior pull actually opposed the likelihood gradient. A control that
> cannot fail is the defect this lab spent 2026-08-11 cataloguing, and here it was
> introduced *by* a correction. **G-P4 is restored to the ratio-and-cosine form in §4.**
>
> **On who is amending this.** The section's author was a peer Claude session that has since
> ended, so the rule that a superseded entry is withdrawn by its author names nobody, and an
> unowned withdrawal is how a refuted claim stays published. Recorded as docket **D9**
> against **D8b**.
>
> **On amending a pre-registration at all.** L-44 freezes these against improvement, and the
> freeze is what makes them evidence: it proves a gate could not be tuned to an answer.
> **No compute has run against this document** — there is no `S1-priors` run directory — so
> there is no answer to tune to, and the property the freeze protects is intact. The original
> text is retained below rather than rewritten, and this amendment is dated.

**The withdrawn text follows, unedited:**

`S1_CBFS_INVERSION_RESULT.md` §4(2) reports, at the corrupted run's plateau,
`|g_penalty|/|g_QoI| = 0.998`, `cos(g_QoI, −g_penalty) = 0.9995`, and the trajectory
table gives `‖g‖₂ = 9.011e-06` at eval 16 (the driver writes
`np.linalg.norm(g)` of the **total** gradient — `invert_lbfgsb.py:117`, read).

Those three numbers over-determine `|g_penalty|`, and the value they imply is
**2.841e-04**. The value computed exactly from the archived field is
`2·1e-4·‖β−1‖₂ = 2·1e-4·2.392652 = ` **4.785304e-04** — a factor **1.684** apart.
Solving back, `‖g‖₂ = 9.011e-06` at ratio 0.998 requires
`cos = 0.999826`, which does not round to the published 0.9995.

**What this does and does not affect.** It does not touch the *finding* — the plateau
being a penalty/likelihood cancellation is confirmed independently by the near-cancellation
itself (‖g_total‖ = 9.011e-06 against |g_pen| = 4.785e-04, a 53x cancellation) and by
rms|β−1| = 0.016511 reproducing the published 0.0165 exactly. It affects the *published
cosine*, and it matters here because the proposal's gate (c) names that balance as the
control a posterior must reproduce. **Gate G-P4 is therefore re-based onto the exact
analytic quantity** (§4), which is reproducible from a file on disk and needs no
recomputation of an angle nobody can now re-derive.

Filed to `docs/DOCKET.md` §D as D8 rather than corrected in place, per C3
(supersession in place, dated — and the correction belongs to that document's owner).

## Related

- `S1_CBFS_REINVERSION_RESULT.md`, `S1_CBFS_WEIGHTED_ARM_RESULT.md` (the regularization
  provenance table this item was told to use as its design input)
- `S1_CBFS_INVERSION_RESULT.md` (the corrupted run and the plateau balance of §8)
- `docs/CAPABILITY_STRATEGY.md` §3 (Bayesian inverse problems), §5 item 2
- `agenda/proposals/s1-cbfs-w1-only-arm.json` (released back to the chief by §3d)
