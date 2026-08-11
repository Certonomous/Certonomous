# S1-with-priors — pre-registration: the regularization derived from prior theory, and a posterior on beta instead of a point field

> **NOT THE CANONICAL PRE-REGISTRATION. Superseded 2026-08-11 by chief ruling.**
> Two chief sessions dispatched the S1 spine off the same directive block and neither
> claimed it first, so this item was pre-registered twice in parallel. **S1 consolidates on
> the owning session, whose artifact is `S1_PRIORS_PREREGISTRATION.md` (commit `ecbdc288`);
> that file governs, and its `est_core_min` of 260 is the item's price.** This document is
> retained, not deleted, for two things that are not duplicated there and that survive the
> ruling:
>
> 1. **§1 — the independent re-verification of the inlet premise**, measured from the four
>    `0/U` files directly. Both sessions verified it separately and got identical digits;
>    that replication is the reason the premise under *both* specs is sound, and it is the
>    thing the chief asked for above everything else.
> 2. **The addendum at the end — the plateau-balance reconciliation**, which refutes
>    `S1_PRIORS_PREREGISTRATION.md` §8 and docket D8 by executed check, and which matters
>    because that document re-based a control gate on the disputed number. Filed as docket
>    D9 and as an advisory field on the proposal; not corrected in place, per C3.
>
> Everything else here — the caps, the 560 core-min, the gates, the loss-support ruling of
> §5 — is **withdrawn as a competing plan** and should be read as a second opinion, not as a
> pre-registration binding anything. Where the two differ on design, the owning session's
> ordering is the better-founded one: a Laplace posterior belongs at the MAP of the
> posterior being claimed, not at the existing `beta_final`, and §6 here has that wrong.

**Item:** `s1-regularization-chosen-by-prior-theory-with-a-posterior-on-beta`
(CAPABILITY_STRATEGY §3 Bayesian inverse problems; §5 sequencing item 2, one of the
three things that make Stage 2 *publishable, not just runnable*).

**Timing, stated so it can be checked and not merely asserted.** This file was written
2026-08-11 by the closure/UQ agent under an explicit no-compute constraint. Two claims,
both checkable:

1. **No solver, inversion, or container was launched by this agent at any point.** The
   item's own sequencing field reads `BLOCKED UNTIL POST-SEND`; nothing here unblocks it.
2. **No run directory for this item exists.** `ls -d /home/ubuntu/certonomous-runs/*prior*`
   returns no match at this writing; the S1 family directories present are
   `S1-cbfs-inversion`, `S1-cbfs-reinversion`, `S1-cbfs-weighted-arm`, `S1-fiml`, all
   with mtimes from 2026-08-05 to 2026-08-08.

Every number in §1 and §3 below is **measured** host-side from files those earlier runs
wrote, and is presented as measured, with the file it came from named. Every number in
§4–§9 is **committed in advance** and unmeasured at this writing. The two categories are
kept in separate sections on purpose: this document does not certify that its own
analysis section was written before it was computed, because that would be false.
The pre-registration proper is §4 onward.

> A note on why that paragraph is worded that way. `campaign/B52_RUNG7_PREREGISTRATION.md`
> opens by certifying its own timing in terms that do not survive a filesystem check. The
> science there was untouched, but a self-certifying claim invites the check. This file
> makes only claims it can pass.

---

## 1. The premise, re-verified from the files rather than inherited

The S1 line rests on one diagnosis: the CBFS case's inlet was not the benchmark's inlet.
That diagnosis is the load-bearing premise of everything downstream, so it was re-measured
here from the actual OpenFOAM files rather than read out of the result document.
**Frame: the four `0/U` files named below, parsed host-side; `inlet` patch `boundaryField`
only; no repo grep involved — three of these paths are outside the repository entirely
and no repo-scoped sweep can see them.**

| file | inlet faces | Ux min → max | Ux mean | Uy distinct values |
|---|---|---|---|---|
| `closure-challenge-benchmark/data/CBFS/0/U` | 150 | 0.202035889 → 1.00537467 | **0.9149216132** | 111 |
| `S1-cbfs-inversion/cbfs_inv/0/U` (pre-repair) | 150 | 0.72 → 0.72 | **0.72** | 1 (all zero) |
| `S1-cbfs-reinversion/cbfs_inv/0/U` (repaired) | 150 | 0.202035889 → 1.00537467 | 0.9149216132 | 111 |
| `S1-cbfs-weighted-arm/cbfs_inv/0/U` | 150 | 0.202035889 → 1.00537467 | 0.9149216132 | 111 |

**The mechanism claim is confirmed exactly.** Benchmark vs pre-repair: Ux max abs
difference **0.517964**, Uy **0.00190188**, and Uz max abs difference **exactly 0**, i.e.
the noise column is bit-identical while the two velocity components carrying the physics
are overwritten. That is the fingerprint of a write-back into the benchmark's own file,
not an independently authored inlet.

**Positive control on that zero.** A comparator that reports "no difference" has to be
shown capable of reporting a difference. The same parser, in the same invocation, on the
same file pair, reported 0.517964 on Ux — so the exact zero on Uz is a measurement, not a
silent read failure. The repaired and weighted-arm files return 0 on all three components
against the benchmark, which independently confirms the repair was taken from the
benchmark source and not hand-authored.

**The loss geography reproduces too**, computed from the archived final fields
(`S1-cbfs-inversion/cbfs_inv/1563/{U,Cx,Cy}` against `0/UData`, 21,000 cells):

| quantity | measured here | as recorded |
|---|---|---|
| Σ&#124;U−UData&#124;² share at y > 2 | **85.15%** | 85.1% |
| share in window 0≤x≤6, 0≤y≤2 | **3.73%** | 3.7% |
| share at y < 0.5 | **1.42%** | 1.4% |
| window cell base rate | **8.44%** | 8.4% |
| inlet column x<−7: RANS / LES bulk Ux | **0.719413 / 0.915297**, ratio 1.2723 | 0.7194 / 0.9153, 1.272 |

**Objective-convention control, unplanned and load-bearing.** Σ&#124;U−UData&#124;² = 961.1569839
over 21,000 cells; dividing by 3N = 63,000 gives 1.525646e-02 against the recorded
`varianceU` of 1.5256460061195715e-02. So DAFoam's `variance` DAFunction normalizes by
**component count × cell count**, and this parse is reading the same field the objective
read. That convention is what §3's prior arithmetic depends on, and it is now measured
rather than assumed.

**Verdict: the inlet finding verifies in full.** Nothing downstream of it is void.

## 2. The state of this family — read before filing anything

The brief that commissioned this document asked for an objective-repair specification, a
Stage 2 specification, a pre-registration, and a costed proposal for the CBFS
re-inversion. **All four already exist, and the work they specify has been executed,
twice.** Recording the state here so that a fifth filing does not happen:

| item | status | spend | outcome |
|---|---|---|---|
| `s1-cbfs-field-inversion-run` | done | 335.98 / 600 | both gates fail; inlet defect diagnosed |
| `s1-cbfs-objective-repair-and-reinversion` | **done** | 424.80 / 450 | repair confirmed on its pre-stated prediction (baseline collapsed 24.8×); **G1 PASS** at 0.25847 (−74.2%); **G2 FAIL** at 26.9% |
| `s1-cbfs-weighted-loss-offline-variant` | done | 0 | verdict CAPTURABLE |
| `s1-cbfs-weighted-reinversion-arm` | **done** | 267.07 / 278 amended | G1w FAIL 0.05710; G2 FAIL 42.7%; localization follows loss support 79.7% |
| `s1-cbfs-continuation-arm` | proposed | — | largely answered by the eval-8 completion |
| `s1-cbfs-w1-only-arm` | proposed, **NO-GO with a named trigger** | — | trigger is *this* design phase |
| **this item** | **proposed, no pre-registration until this file** | — | — |

So the repair spec the brief asked for is a historical document, and the gates it asked
me to re-derive were already re-derived once (G1 re-based from 0.70-of-the-corrupted
baseline to 0.70-of-the-repaired baseline, which is a 1625.78 normalizer against 65.448).
The open frontier is this item, and the W1-only arm is held explicitly behind it.

## 3. What the regularization actually was — measured, and the reason this item exists

The weighted arm left a provenance table of every lambda the family used. This section
converts it into the quantity prior theory actually speaks about, which the table does
not state: **the implied prior-to-noise ratio.**

Minimizing `J = λ_QoI·varianceU + λ_L2·Σ(β−1)²` is, up to an irrelevant positive scale,
minimizing the negative log posterior
`Φ = (1/2σ²)·Σ|U−UData|² + (1/2s²)·Σ(β−1)²` under a Gaussian likelihood of per-component
noise σ and an i.i.d. Gaussian prior `β ~ N(1, s²)`. Matching the two coefficient ratios,
and using the measured convention `varianceU = Σd²/3N` from §1:

```
    s²/σ²  =  λ_QoI / (3N · λ_L2)          [equal-weight runs, 3N = 63000]
    s²/σ²  =  λ_QoI,w / λ_L2               [weighted arm: Jw_raw is an unnormalized sum]
```

| run | λ_QoI | λ_L2 | **implied s/σ** | achieved rms&#124;β−1&#124; |
|---|---|---|---|---|
| equal-weight, corrupted objective | 65.448114804931393 | 1e-4 | **3.22** | 0.0165 |
| equal-weight, repaired objective | 1625.7778891393064 | 1e-5 | **50.80** | 0.1396 |
| weighted arm | 1/27.465931825190644 | 1e-5 | **60.34** | 0.1111 |

**The implied prior moved by a factor of 18.7 across three runs, and no run derived it.**
Each λ_L2 was chosen by a defensible convention — the top of Wu/Zhang's stated band, then
a disclosed 10× cut, then "kept" — and the *statistical* consequence of those choices was
never computed. That is the precise, quantified statement of the problem this item exists
to fix, and it is the strongest single argument for the item.

Taking the noise scale as the residual the model can actually reach,
σ = √(varianceU_final) = √(1.5897973285391003e-04) = **0.012609** per velocity component
(1.38% of the 0.91492 inlet bulk — a defensible magnitude for LES-to-RANS interpolation
error, and see §4.3 for how it is re-derived rather than assumed), the three runs imply
prior standard deviations on β of **0.041, 0.641, 0.761**. The corrupted run's prior was
genuinely constraining (implied s = 0.041 against an achieved rms of 0.0165) and the
record shows exactly that: the run terminated at a penalty balance. The repaired and
weighted runs carried priors 4.6× and 6.8× wider than the deviation they achieved, i.e.
effectively unregularized — which is the mechanism behind the cell-by-cell scatter both
G2 verdicts foundered on.

**The plateau-balance control is reproducible at zero compute, and was reproduced.**
From the surviving matched pair `beta_eval010.npy` / `grad_eval010.npy` in the corrupted
run (evals 11–17 agree in J to seven digits, so eval 10 is at the plateau):

| quantity | measured here | as recorded |
|---|---|---|
| rms&#124;β−1&#124; | **0.016502** | 0.0165 |
| &#124;g_penalty&#124;/&#124;g_QoI&#124; | **0.998441** | 0.998 |
| cos(g_QoI, −g_penalty) | **0.999542** | 0.9995 |
| β min / max | **0.7353 / 1.1443** | 0.735 / 1.145 |

This matters twice: it confirms the gradient convention the arithmetic above depends on
(`g_total = λ_QoI·g_raw + 2λ_L2(β−1)`, driver line 114), and it establishes that gate (c)
of §7 is executable without buying a single core-minute.

**A capability limit found while checking this, which changes the item's price.** The
proposal's cost basis states that the posterior analysis "rides the arm's converged fields
at no additional solver time." Converged *fields* are indeed on disk. **Curvature is not.**
Both drivers delete the per-evaluation gradient immediately after use —
`invert_lbfgsb.py` line 97, `os.remove(gpath)  # keep every 10th + eval001 (the control)`.
Of 16 evaluations, two gradients survive in each run. The L-BFGS (s,y) curvature pairs are
therefore **not reconstructible from disk**: `s_k` is available from the eleven
`beta_accept_iter*.npy` files, but `y_k = g_{k+1} − g_k` needs gradients at consecutive
iterates and fourteen of them were discarded. A posterior needs second-order information,
and the second-order information this family generated was not retained. §6 prices the
consequence honestly instead of inheriting the proposal's estimate.

---

*Everything above this line is measurement on existing files. Everything below is
committed in advance and is unmeasured at this writing.*

---

## 4. The prior, derived

### 4.1 Why the current prior is the wrong object, not merely the wrong number

The `Σ(β−1)²` penalty is an i.i.d. (white) Gaussian prior on a **field**. In Stuart's
framework (*Acta Numerica* 19, 2010, §2 and §6) a Gaussian prior measure `N(0, C)` is
well defined on a function space only if `C` is trace-class; for `C = (κ² − Δ)^(−α)` on a
domain in `R^d` this requires `α > d/2`. CBFS is a two-dimensional case, so the
requirement is `α > 1`, and white noise is `α = 0`. The white prior is therefore not a
well-defined prior on the correction field at all — it is a mesh-level object whose
implied field roughness has no mesh-independent limit.

This is not a purely formal complaint. It makes a prediction that the S1 record already
half-confirms: under a white prior the MAP correction has no spatial coherence, which is
what the first result document reported ("lets the deviation scatter cell-by-cell instead
of forming coherent regions"), and it is a candidate explanation for both G2 failures that
is **independent of the loss-support explanation** the weighted arm established.

### 4.2 The prior committed here

- **Log-normal, not normal.** `log β ~ GP(0, C)`. Grounds: β multiplies a production term
  and is physically positive; a Gaussian on β puts prior mass on β ≤ 0. This also makes
  the operating bounds symmetric — [0.2, 4.0] is [−ln 5, +ln 4] in log space — where on β
  they are lopsided.
- **Whittle–Matérn covariance**, `C = σ_pr²(κ² − Δ)^(−α)` with **α = 2**, giving Matérn
  smoothness `ν = α − d/2 = 1` in d = 2 (Lindgren, Rue & Lindström 2011 convention):
  once mean-square differentiable, trace-class, the minimum smoothness the theory permits
  — chosen at the boundary deliberately so the prior is the weakest one that is
  well posed, not the smoothest one that would flatter G2.
- **Correlation range ρ = 0.5 h** (h = step height = 1 mesh unit), so κ = √(8ν)/ρ =
  **5.6569**. Ground: the correction field should vary on the scale of the shear layer it
  corrects, not on the cell scale. **Pre-registered sensitivity band: ρ ∈ {0.25h, 0.5h, 1.0h}**,
  all three reported; the headline uses 0.5h.
- **Marginal σ_pr = 0.35 in log space.** Ground: ±2σ spans β ∈ [0.497, 2.014], the range
  within which a production multiplier is arguable on physical grounds, while placing the
  operating bounds at −4.60σ and +3.96σ so the truncation is effectively inactive.

**Consequence, computed now and stated as a pre-registered number.** Mapped back through
§3's identity at σ = 0.012609, σ_pr = 0.35 implies **λ_L2 = 3.349e-05** for the repaired
equal-weight objective — **3.35× the 1e-5 actually used**, and 8.6× the corrupted run's
implied prior. Across the sensitivity band the theory value is 6.56e-05 (ρ-independent,
σ_pr = 0.25) to 1.64e-05 (σ_pr = 0.50). **The theory value differs from every value this
family has used**, which is what gate (a) requires; had it landed on one of them, gate (a)
fails by its own wording and this document says so in advance.

### 4.3 The noise scale is derived, not assumed — and this is where it could break

σ = 0.012609 above is taken from the achievable residual, which is circular if used
uncritically: it is the residual *after* an inversion that the prior in question helped
produce. The committed procedure removes the circularity:

- **σ is estimated from a region the correction does not act on.** The free-channel band
  y > 2 carries residual that the reinversion moved by only −21.6% and that the record
  attributes to LES-to-RANS interpolation mismatch rather than closure error. σ is
  estimated there, on the repaired baseline (β = 1) fields, and reported with its
  spatial distribution.
- **This makes σ heteroscedastic, and that is the point** — see §5.
- **Falsifier for the noise model itself:** if the y > 2 residual is not approximately
  spatially uncorrelated at the mesh scale — checked by its empirical two-point
  correlation — then it is not noise, it is unmodelled structure, and calling it noise
  would be inflating σ to manufacture a comfortable posterior. That check is reported
  before any posterior is quoted, and a failure is reported as a failure of this
  specification.

## 5. The loss-support ruling — and why it absorbs the W1-only arm

The W1-only arm is held with its trigger named as this design phase, on the grounds that
this phase "must decide loss support anyway." It does, and the ruling committed here is:

**Do not narrow the loss. Replace the mask with a noise model.**

The weighted arm imposed a hard 0/1 spatial mask on the objective, and the W1-only arm
would impose a narrower one. Under the Bayesian reading, a hard mask is the statement
`σ = ∞` outside the box — an assertion that the free-channel data carries *no* information
about β. The measured evidence contradicts the strong form of that assertion: the
equal-weight inversion did move the free-channel residual, by −21.6%. What the data
actually supports is the weaker, quantitative statement that free-channel observations are
**noisier**, because they are dominated by reference-interpolation error. A heteroscedastic
`σ(x)`, estimated per §4.3, expresses exactly that, and **derives the down-weighting the
weighted arm imposed by hand.**

Three consequences, all pre-registered:

1. **The W1-only arm is superseded rather than triggered.** Its hard window mask is the
   `σ → ∞` limit of the noise model committed here, so it is a special case of this arm
   and not an independent experiment. Recommendation to the chief: **close it as absorbed**,
   with this section as the reason. That is a recommendation, not a decision — the arm was
   held by a chief ruling and only the chief closes it.
2. **G2's accounting question gets answered rather than relitigated.** The weighted arm
   showed localization follows loss support (79.7% in support). Under a smooth `σ(x)` there
   is no sharp support to follow, so the top-decile geography becomes an actual measurement
   of where the data constrains β rather than an echo of where the mask was drawn.
3. **The comparison is against the equal-weight repaired run**, not against the weighted
   arm, because that run's loss support is the whole field and so is this one's.

## 6. The posterior, and its honest price

Gate (b) asks for a per-cell credible interval. The route and its cost, stated plainly
because §3 established that the cheap route is unavailable:

**Laplace approximation at the MAP**, `posterior ≈ N(β_MAP, H⁻¹)` with
`H = J^T Γ_noise⁻¹ J + C_pr⁻¹`, exploiting the standard result that the
prior-preconditioned data-misfit Hessian is compact and its spectrum decays, so a
low-rank approximation of rank r captures it (Flath et al. 2011; Bui-Thanh et al. 2013).
The eigenpairs come from a randomized range finder needing `r + p` Hessian-vector products.

**DAFoam exposes no second-order adjoint on this configuration** — check named: the
driver's only solver task is `compute_totals`, and the item's own history contains no
Hessian-vector capability. So each HVP is a finite difference of the gradient,
`Hv ≈ (g(β + εv) − g(β))/ε`, one-sided to reuse a single base gradient. **One HVP =
one `compute_totals` = ~20 core-min** at the measured `-primalTol 1e-8`, `--cpus=2` rate.

| tier | what it buys | core-min |
|---|---|---|
| **T1 — prior side, zero compute** | §3's implied-prior audit (done), the theory prior of §4, λ derivation, truncation-mass accounting, gate (c) plateau control (done) | **0** |
| **T2 — Laplace posterior** | base gradient re-anchor (20) + 24 HVPs at rank r = 20, oversampling p = 4 (480) + eigen-analysis and write-out (~15) | **~515** |
| **T3 — re-inversion under the theory prior** | MAP at λ_L2 = 3.349e-05 with the Matérn prior, ~10 evals + controls | **~230** |

**The filed `est_core_min` of 150 does not buy gate (b), and I am not going to pretend it
does.** At 150 core-min the affordable rank is r ≈ 5 on a 21,000-dimensional field, which
is a token, not a posterior — and a rank-5 credible interval reported as a credible
interval would be the kind of number this lab exists to not produce. §9 re-prices the item.

**Rank adequacy is itself gated, not assumed.** The eigenvalue spectrum is reported, and
if the r-th eigenvalue of the prior-preconditioned misfit Hessian has not fallen below 1
by r = 20, the low-rank truncation has not captured the data-informed subspace and the
posterior is reported as **rank-limited**, with the credible intervals labelled as lower
bounds on width. That is a pre-registered failure mode with a pre-registered label.

## 7. Gates

The strategy PROOF clause is carried verbatim in the proposal and operationalised there in
three parts. Restated here with bars fixed:

- **(a) DERIVATION.** λ_L2 is derived from a stated prior and a stated noise scale, the
  derivation is written down, and the resulting value is compared against all three values
  the family has used. **A value that reproduces a previously used value fails.** Committed
  in advance: the derivation yields **3.349e-05** at σ_pr = 0.35, band 1.64e-05 – 6.56e-05,
  against the used values 1e-4 and 1e-5. Bar met in advance by construction, and it is
  recorded here so that no later reader has to wonder whether it was fitted afterwards.
- **(b) POSTERIOR.** The reported product is a per-cell credible interval over the
  correction field plus the prior mass sitting on the truncation bound — not a point field
  with a caption. Rank-adequacy labelled per §6.
- **(c) CONTROL.** The posterior treatment reproduces the recorded plateau balance of the
  corrupted run — `|g_pen|/|g_QoI| = 0.998` at rms 0.0165 — as a check that the prior it
  claims is the prior the optimization actually felt. **Bar: both quantities within 2% of
  0.998441 and 0.016502** (the values §3 measured from disk). A posterior that cannot
  recover that balance is reported as failing its own control, and nothing is inferred
  from it.

**On whether the inherited gates should be restated — argued, not assumed.**
G1 was already correctly re-based once, from the corrupted baseline to the repaired one,
and that re-basing is why it went from a 0.149% move to a 74.2% move against the same
0.70 bar. **G1 is not carried into this arm at all**, and that is deliberate: a MAP under a
different prior is not comparable to a MAP under the old one on a normalized-QoI bar,
because the prior changes what the optimum *is*, not merely how fast it is reached.
Reporting `J_qoi` against 0.70 here would be inheriting a number nobody re-derived for
this prior — the exact failure mode the brief warned about. What is reported instead is
the QoI at the theory-prior MAP alongside the equal-weight run's 0.25847, **as a
disclosure with no bar attached**, because the honest comparison is between posteriors and
this arm has the only one.

**G2 is carried unchanged, at >50%, and this is the one bar that should not move.** It was
set against a defective objective, survived the repair, and its two failures (26.9%, 42.7%)
were both explained by mechanisms measured afterwards rather than by the bar being wrong.
It is also the only bar in the family that is independent of the loss and the prior — it
asks a question about geography, not about a normalized objective value. A bar that has
caught a real property of the setup twice is not a bar to loosen because a third arm might
fail it. Under this arm G2 is scored on the **posterior mean** field, and additionally on
the subset of cells whose 95% credible interval excludes 1 — the second being the
localization statement a point field could not make.

## 8. What would falsify the closure hypothesis

The hypothesis on trial: *there exists a production-term β field on SST, identifiable from
CBFS LES velocity data, representing a real and spatially coherent model-form correction
in the separated-flow region.* Falsifiers, in decreasing sharpness. These are falsifiers,
not disappointments; the difference is stated at the end.

1. **Identifiability falsifier — the primary one.** If the 95% posterior credible interval
   for β **includes 1 in ≥ 50% of the window cells** (0≤x/h≤6, 0≤y/h≤2), then the data does
   not identify a correction where the physics says the model error lives. Every point
   field this family has produced would then be a regularization artifact in the window,
   and the −94.9% window error reduction would be a statement about the flexibility of
   21,000 free parameters rather than about closure physics. **This is measurable directly
   from gate (b)'s output and it would end the production-term line.**
2. **Prior-artifact falsifier.** If the theory-prior posterior mean differs from the
   white-prior MAP, in the window, by more than the posterior standard deviation, then the
   earlier β fields were determined by the regularization choice rather than by the data,
   and the family's published fields require an annotation to that effect.
3. **Control falsifier.** If gate (c) fails — the posterior cannot reproduce the observed
   plateau balance — the machinery does not describe the optimization actually run and no
   inference from it stands, independently of what it says about β.
4. **Noise-model falsifier.** If the y > 2 residual shows mesh-scale spatial correlation
   (§4.3), the free-channel term is unmodelled structure, not noise, and the heteroscedastic
   design of §5 is invalid as specified.

**What would merely be disappointing, and is not a falsifier:** the theory prior landing
close to the conventional 1e-5 (that is the proposal's own outcome 2, and a defensible
choice that agrees with habit is still the first defensible choice this line has had); the
posterior being well constrained but G2 still failing (that is a localization finding, and
the credible-interval subset gives it a sharper form than either previous arm had); or the
rank-20 truncation proving inadequate (that is a labelled, priced, re-runnable limitation).

## 9. Caps, and the basis for the estimate

**Calibration.** The family's measured per-evaluation cost on this exact case is the only
basis used. S1 spent **335.98 against a 600 cap** at ~16.4 core-min/eval on the corrupted
objective; the reinversion spent **424.80 of 450** at ~20 core-min/eval once `-primalTol 1e-8`
was adopted (320.13 for 16 evaluations = 20.0 each); the weighted arm spent **229.07 of 250**
and then **267.07 of an amended 278**. The tightened primal tolerance is the reason the
per-eval price rose from 16.4 to ~20, and ~20 is the number used throughout.

| stage | basis | core-min |
|---|---|---|
| T1 prior-side analysis | host-side arithmetic on written fields | **0** |
| base gradient re-anchor at the MAP | 1 `compute_totals` @ 20 | 20 |
| 24 Hessian-vector products (r = 20, p = 4) | 24 × 20 | 480 |
| noise-model estimation on baseline fields | reuses `cbfs_inv/2500/`, no solve | 0 |
| eigen-analysis, credible intervals, write-out | 1 field write-out @ ~9 + host arithmetic | 15 |
| **T2 subtotal — the posterior, gate (b)** | | **515** |
| T3 re-inversion under the theory prior (optional, separately gated) | ~10 evals @ 20 + controls | 230 |

**Committed request: a 560 core-min hard cap for T1+T2**, which is 515 estimated plus 45
of headroom — 8.7%, sized on the family's own overrun history (the weighted arm's first two
evaluations billed 27.1 and 26.5 against a 18.9 uncontended basis under A3 contention, a
~40% per-eval penalty that ate the eighth evaluation). **T3 is not requested here** and
should be a separate decision taken after the posterior exists, because the posterior is
what tells you whether a re-inversion is worth 230 core-min.

**Stop rule**, carried from the family's proven driver unchanged: the driver polls the
billed ledger and refuses to launch any evaluation whose projected completion would cross
**545** cumulative, reserving the last 15 for write-out. A stop at the cap is recorded
**budget-capped, not converged** (charter §4). Because the HVPs are independent of each
other — unlike optimizer evaluations, which form a chain — a budget stop here degrades
gracefully: it lands at a lower rank, which §6 already labels, rather than at an
uninterpretable partial iterate.

**Concurrency.** `--cpus=2` per the standing instruction whenever another agent is solving;
the choice is recorded per launch in `ledger.csv`, as in every run of this family.

## 10. Protocol clauses that bind the execution

- **Bytecode-cache handling for any mutation-based validity check.** Where this arm
  verifies that a host-side script is genuinely sensitive to an input it claims to read —
  perturbing a mask, a noise field, or a prior parameter and confirming the reported number
  moves — the check **deletes `__pycache__` before every cell, or sets a fresh
  `PYTHONPYCACHEPREFIX` per cell, and asserts the clean control and the mutated case within
  a single invocation.** `PYTHONDONTWRITEBYTECODE=1` is **not** sufficient and is not
  accepted as the mitigation here: it prevents writing a `.pyc`, not reading a stale one,
  and a stale one exists whenever the module was imported before the mutation. Python's
  timestamp invalidation compares `int(st_mtime)` in whole seconds plus file size, so a
  length-preserving edit inside a one-second mutate-run-restore cycle matches both halves
  and the cell silently reports the pre-mutation result. A matrix gathered across separate
  invocations can be inverted end to end without any single cell looking wrong, which is
  why the control and the mutant must be asserted in the same run. This is a gate-integrity
  clause, not a performance note: without it, gate (c) and the §4.3 noise check could each
  return exactly backwards.
- **Frames on every count.** Any cell count, share, or fraction is reported with the mask
  that produced it and the field it was computed on, in DV order or serial order stated
  explicitly. The reinversion record carries a dated correction addendum for exactly this
  (FD cell labels applied serial-order centres to DV-order indices); the
  `dv_to_serial_perm.npy` recovered from `cellProcAddressing` is on disk in both run
  directories and is used rather than re-derived.
- **Gradient retention is changed for this arm.** The `os.remove(gpath)` at driver line 97
  is removed. 24 HVP gradients at 168 KB each is 4 MB, and discarding second-order
  information to save four megabytes is what made this item expensive in the first place.
- **Nothing is sent, filed externally, uploaded, or published.** External submission is
  parked and reserved to Katie.

## 11. What this arm can and cannot establish

**Can:** whether the correction field is identifiable from the data or is a regularization
artifact; the first theory-derived regularization in this family's history; a posterior
that Stage 2 can propagate rather than a point field it would have to trust; a ruling on
loss support that supersedes an arm currently held.

**Cannot:** anything about the destruction term (`w3-beta-on-omega-destruction-model-patch`
remains the term-parity item); anything about generalization, which is Stage 2's question;
any benchmark score — CBFS is the field-inversion **training** case, the loss reads only
CBFS's own LES `0/UData`, no scored test case is opened, and this arm makes no scoring
claim. Any later filing that proposes carrying the posterior to a scored case owes its own
in-sample verdict; this one does not grant it.

**Sequencing, restated because it binds.** This item is **BLOCKED UNTIL POST-SEND**:
strategy rule 1 holds the now-to-send queue for Ladder V alone and rule 2 places this item
in the post-send month. This file exists so the design is derived, priced, and committed
*before* that month opens. It is not a dispatch, it does not request a launch now, and the
560 core-min is a priced request to Katie, not an authorization.

---

*Nothing in §4–§11 existed before this commit. The measurements in §1 and §3 are from
files written 2026-08-05 to 2026-08-08 and are labelled as measurements throughout. No
solve of this item launches before this file is committed, before the post-send month is
declared open, and before Katie authorizes the compute.*

---

## Addendum — dated 2026-08-11, after commit: a parallel pre-registration exists, and one disagreement is settled by execution

While this file was being written, a peer session independently pre-registered the same
item as `S1_PRIORS_PREREGISTRATION.md` (commit `ecbdc288`, landing after this file's
`47bd94a4`). **Two frozen pre-registrations for one item is the duplication this work was
briefed to avoid**, and which of the two is canonical is the chief's call, not mine. This
addendum records what agrees, what differs, and the one point that is not a matter of
judgement.

**What agrees — and it is worth stating, because the agreement is independent.** Two
agents, working separately from the same files, both re-verified the inlet premise and got
identical numbers: 150 faces, Ux 0.72 uniform pre-repair, the benchmark's
0.202035889 → 1.00537467 profile at bulk 0.9149216132, Uz max abs difference exactly 0
against Ux 0.517964. Both concluded the four commissioned deliverables were already
executed, both identified S1-with-priors as the open frontier, both re-priced the filed
150 core-min as inadequate, both derived a log-normal prior, and both named an
identifiability falsifier. That is a genuine independent replication of the premise, and
it strengthens it.

**What differs, legitimately.** (i) *Loss support:* that file rules equal-weight all-cells
and releases the W1-only arm back to the chief; §5 here rules for a heteroscedastic `σ(x)`
estimated from the free-channel residual and recommends the arm be closed as absorbed. Both
are arguable and the chief should pick one. (ii) *Price:* 260 there against 560 here — the
gap is rank, 6 Hessian-vector products against 24, and that file discloses its rank 6 as
thin in advance. (iii) That file makes a point this one missed and which is worth carrying
into whichever survives: **the penalty value and gradient are composed host-side**
(`invert_lbfgsb.py:111–114`), so changing the prior's *form* needs no DAFoam change and no
new FD gate. That materially lowers the cost of the prior change itself, and it is correct.

**What is settled by execution, not judgement — the plateau-balance control.**

> **[UPDATED 2026-08-11 by the chief supervisor, after acting on this section.** Two pointer
> corrections, both of the kind that rot quietly. **(1)** The docket row named below as `D8`
> was renumbered **`D8b`** when it was landed — it had been filed as a second `D8` by a
> concurrent session while another row already held that number, the third such collision in
> that file the same day. **(2)** The sentences below are written in the present tense about
> a state that has since changed: `S1_PRIORS_PREREGISTRATION.md` **§8 is now WITHDRAWN** and
> its **gate G-P4 restored to the ratio-and-cosine form** (commit `57fd0d83`), on the
> strength of exactly the measurement recorded here. The refutation below stands unedited
> because it is the evidence; only its object has moved.
>
> **The reason the restoration mattered more than the arithmetic**, and it is worth stating
> where the refutation lives rather than only where the withdrawal does:
> `|g_penalty| = 2·λ_L2·‖β−1‖₂` is an **identity**. Any treatment knowing λ_L2 and β
> reproduces it exactly, **including one whose posterior is wrong** — so the re-basing had
> replaced a control that can fail with one that cannot. The **cosine** is the leg carrying
> whether the prior pull actually opposed the likelihood gradient.**]**

That file's §8, and its `docs/DOCKET.md` D8b row, report the published triple
(`|g_pen|/|g_QoI| = 0.998`, `cos = 0.9995`) as failing to reconcile with the archived field
**by a factor 1.684**, and re-base its gate G-P4 onto `|g_penalty|` alone in consequence.
**The published triple reconciles.** §3 of this document measured all three from disk —
0.998441, 0.999542, rms 0.016502 — from the *matched* pair `beta_eval010.npy` /
`grad_eval010.npy`, both DV order, written by the same `run_eval` call, at a state evals
11–17 agree with in J to seven digits. The internal identity
`‖g_total‖ = |g_QoI|·√(1 + r² − 2rc)` closes to **six digits** (1.450369e-05 both directly
and via the identity).

The 1.684 arises from combining the plateau-state ratio and cosine with `‖g‖₂ = 9.011e-06`,
which the trajectory table reports at **eval 16** — a different state. The quantities
are not interchangeable across evaluations here because the cancellation is extreme:
`‖g_total‖` moves 1.45e-05 → 9.01e-06 between eval 10 and eval 16 while `r` and `c` move
only in the fourth decimal, so a 1.6x change in the small residual difference is compatible
with a nearly unchanged ratio and cosine. The inference was sound arithmetic on inputs
drawn from two states; no gradient needed re-deriving, because one was on disk.

**Why this matters beyond bookkeeping.** `|g_penalty| = 2·λ_L2·‖β−1‖` is an *identity* —
any treatment that knows λ_L2 and β reproduces it exactly, including a treatment whose
posterior is wrong. Re-basing the control onto it therefore removes the only part that
tests the *balance*: the cosine is what carries the information that the prior pull actually
opposed the likelihood gradient. **Gate (c) of §7 stands as written**, on the ratio and the
cosine, with the 2% bars against 0.998441 and 0.016502. Filed as `docs/DOCKET.md` D9 rather
than corrected in place, because the D8 row and that §8 belong to their author (C3).

## Related

- `S1_PRIORS_PREREGISTRATION.md` (the parallel pre-registration; see the addendum above)
- `S1_CBFS_INVERSION_RESULT.md` / `S1_CBFS_INVERSION_PREREGISTRATION.md` (the corrupted run)
- `S1_CBFS_REINVERSION_RESULT.md` / `S1_CBFS_REINVERSION_PREREGISTRATION.md` (the repair)
- `S1_CBFS_WEIGHTED_ARM_RESULT.md` (the regularization provenance table this section 3 converts)
- `S1_CBFS_WEIGHTED_LOSS_VARIANT.md` (the offline verdict, and the DV→serial permutation)
- `docs/CAPABILITY_STRATEGY.md` §3, §5 (the strategy clause and the sequencing block)
