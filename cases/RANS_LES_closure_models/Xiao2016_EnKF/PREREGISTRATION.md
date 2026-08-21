# PREREGISTRATION — Xiao et al. 2016, iterative ensemble Kalman inversion of the Reynolds stress

**Status at the moment of freezing: the registered H0 forward-model harness gate
has been run and FAILED. The ensemble is NOT started. This lane is BLOCKED on a
forward-model decision, and §7 states the exact gap and its cost.**

That is the intended use of a harness gate: it cost **0.5 core-hours** and it
stopped a 17-to-162-core-hour ensemble whose forward model cannot carry the truth.
The Kaandorp lane learned this the expensive way (`../Kaandorp2020_TBRF/aposteriori/RESULTS.md`
§4, H0 GATE FAIL); this lane spent the harness first.

* Paper: H. Xiao, J.-L. Wu, J.-X. Wang, R. Sun, C. J. Roy, *Quantifying and
  Reducing Model-Form Uncertainties in RANS Simulations: A Data-Driven,
  Physics-Based Bayesian Approach*, arXiv:1508.06315v3 (8 Dec 2016).
  VERIFIED-PDF: `docs/papers/closure/Xiao2016_model_uncertainties.pdf`.
* Data: Closure Challenge benchmark clone, commit `deb91557184af3cb95f5190494ec52d8f2c6a0d1`,
  `sha256(git ls-files -s data)` = `e9cd3f22ec235bd3e218931dfb76d522b429b63883a16f2c86cbb3993a360401`.
  Read-only. Everything derived is written to `/home/ubuntu/closure-data/xiao/`.

---

## 1. The paper's own design, quoted before anything is run (Table 1, p. 21; §4.1.1, pp. 18-20; §5.1, p. 33)

| item | paper, periodic hill |
|---|---|
| case | periodic hill, **`Re_b` = 2800** on crest height `H` and bulk velocity |
| mesh | **50 x 30 = 1500 cells**, domain 9H x 3.306H x 0.1H |
| baseline turbulence model | **Launder-Sharma k-epsilon** |
| perturbed fields | **`xi`, `eta`, `k`** — magnitude and barycentric shape. **Orientation is NOT perturbed** (their stated limitation) |
| KL modes per field | **16** (chosen so the reconstruction keeps >= 80 % of the total variance) |
| correlation length `l` | **`H`** (the hill crest height) |
| prior variance field | `sigma(x) = sigma_0 + sigma_local(x)`, `sigma_0` = **0.2**, `sigma_local` = **0.5** at four named locations (hill crest, recirculation centre, windward side, free-shear layer), RBF exponential kernel, length scale `H` |
| ensemble size `N` | **60** (their sensitivity study: results stop moving above 30) |
| EnKF iterations | **~10** to statistical convergence |
| observations | **18** velocity points, spaced closer where the flow changes fastest |
| observation noise | **`sigma_obs` = 10 % of the true mean value**, Gaussian, uncorrelated between locations, resampled every iteration |
| forward model | **`tauFoam`** — the RANS momentum and pressure equations with `tau` **prescribed**, no turbulence transport equations; "each forward RANS evaluation is only 10 % as expensive as a baseline RANS simulation" |
| total cost | **600 forward evaluations** = 60x one baseline solve |
| headline claim | abstract, p. 1: "even with very sparse observations, the obtained posterior mean velocities and other QoIs have significantly better agreement with the benchmark data"; "at most locations the posterior distribution adequately captures the true model error" |

Verification flag **L-157 / the paper's own p. 10 limitation**: the eigenvector
(orientation) of `tau` is not perturbed. Any coverage failure in an orientation-
dominated region is therefore a property of the parameterisation, not of the
inference, and is reported as such.

---

## 2. This is a labelled VARIANT — every departure

| # | departure | why |
|---|---|---|
| V1 | **`Re_H` = 10595, not 2800.** Our periodic hill is the Breuer case `PH_Breuer` shipped by the benchmark. PH2800 is not on disk and is not in the challenge release. | data |
| V2 | **15,600 cells (120 x 130), not 1500 (50 x 30)** — 10.4x the paper's mesh, so a forward evaluation is not 10 % of a baseline solve here | data |
| V3 | **k-omega SST baseline, not Launder-Sharma k-epsilon** — the benchmark ships SST | data |
| V4 | Observations are drawn from the shipped **interpolated LES** field, not from the paper's DNS of a different `Re` | data |
| V5 | Forward model — see §7. The paper's `tauFoam` does not exist on this machine and the two substitutes built from the validated interface both fail the H0 harness gate | **this is what blocks the lane** |

---

## 3. Registered method

**Parameterisation.** Perturb the RANS Reynolds stress in its invariants only:
`k` (magnitude) and `(xi, eta)` (barycentric shape). **Orientation is not
perturbed**, matching the paper. Discrepancies `delta^k, delta^xi, delta^eta` are
non-stationary Gaussian random fields with an exponential kernel of correlation
length `l = H`, expanded in **16 KL modes each** (48 state dimensions total),
variance field `sigma_0 = 0.2` plus `sigma_local = 0.5` at the paper's four named
locations by RBF interpolation with length scale `H`.

**KL expansion, registered implementation.** A dense 15,600 x 15,600 covariance is
1.95 GB and a full eigendecomposition is O(n^3); instead the kernel is applied as
a `scipy.sparse.linalg.LinearOperator` and the leading 16 eigenpairs are taken
with `eigsh`. Registered because it changes the numbers only through eigensolver
tolerance, and the cost claim in §6 depends on it.

**Constraints, as in the paper.** Realisability is enforced by construction
(`(xi, eta)` are mapped into the barycentric triangle); smoothness comes from the
KL truncation; symmetry is inherent to the `symmTensor` representation.

**Inference.** Iterative ensemble Kalman with `N` = 60 members and 10 iterations,
observations resampled each iteration with `sigma_obs` = 10 % of truth.
**Checkpoint after every EnKF iteration** to `/home/ubuntu/closure-data/xiao/`,
resumable; every solve carries an iteration cap **and** an in-script `timeout`;
nothing is ever killed.

**Observations.** 18 points, matching the paper's count, placed by the paper's own
rule (closer where the flow changes fastest: recirculation and reattachment;
sparser in the free-shear region). **Our placement is ours, not theirs** — the
paper gives the rule and a figure, not coordinates — and the exact 18 (x/H, y/H)
pairs are frozen in `obs_points.json` before any assimilation. A held-out set of
18 further points, disjoint from the assimilated set, is frozen at the same time
for the H2 coverage test.

---

## 4. Gates and hypotheses

Verdicts from {PASS, GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING}.

### G0 — forward-model identity (RUN; result in §7)

> Prescribing the **baseline SST stress** through the forward model must
> reproduce the shipped baseline velocity field.

* Band: `|U_rms - 0.1565| < 1e-3` against the `BASELINES.md` PH10595 row.
* **Result: PASS.** 0.15658 (optimal-`nu_t` projection) and 0.15659 (baseline
  `nu_t`), both within 1e-4.

### H0 — forward-model harness (RUN; result in §7)

> Prescribing the **LES truth stress** must drive `U_rms` close to zero. Registered
> band: within a factor of **4** of the Kaandorp lane's validated `TRUTH+R`
> control, which reached `U_rms` = 0.00341 on `AR_1_Ret_360`; on this case the W2
> SpaRTA campaign record predicts `eps(U)/eps(U_0)` = 0.003331, i.e.
> `U_rms ~ 0.0090`. **Gate: `U_rms` <= 0.036.**
* **Result: GATE FAIL.** See §7.
* **Registered consequence: if H0 fails, the ensemble is not run and H1-H3 are
  reported as BLOCKED, not as failures of the method.** An inference whose forward
  model cannot reproduce the truth from the true stress cannot be graded.

### H1 — posterior mean beats the baseline

* Metric `U_rms` per `BASELINES.md` §1 over all cells. **Gate: SST 0.1565**; PASS
  requires the posterior-mean `U_rms` below **0.1252** (a >= 20 % reduction) with
  the margin exceeding the across-seed spread of three independent ensembles.
* GATE REACHED if it beats 0.1565 by less than 20 %. GATE FAIL if it does not beat it.

### H2 — credible-interval coverage (the paper's own weak point)

* Fraction of **held-out** locations at which the LES truth falls inside the
  posterior 95 % credible interval of `U`.
* **Registered expectation: under-dispersion.** Ensemble Kalman posteriors are
  well known to be over-confident, and the paper's own claim is the hedged "at
  most locations". PASS requires coverage >= **0.80** at held-out points;
  GATE REACHED **0.60-0.80**; GATE FAIL below **0.60**.
* Coverage at the 18 **assimilated** points is reported beside it and carries no
  verdict — a filter that does not cover its own observations is broken, not
  under-dispersed.

### H3 — realisability of posterior samples

* Fraction of (cell, member) pairs whose posterior `tau` lies outside the
  barycentric triangle, tolerance 1e-7 (`../Kaandorp2020_TBRF/RESULTS.md` §7).
* The parameterisation enforces realisability **by construction**, so
  **PASS requires 0.0000**; anything above is an implementation defect, not a
  finding. Reported beside the truth's own rate on this case (**0.0000**).

### Continuity and ensemble health (reported; thresholds relative, see §5)

* RMS `div(U)` per member, normalised by the field's own gradient scale, reported
  **relative to the measured baseline floor on this mesh**, not against an
  absolute number.
* **Ensemble-collapse diagnostic:** trace of the state covariance and the mean
  pairwise member distance, per EnKF iteration; a monotone collapse to < 1 % of
  the prior trace before iteration 10 is recorded as collapse.

---

## 5. The continuity instrument was calibrated before its threshold was written

`L-TBD-K7` from the Kaandorp lane: register a tolerance only after measuring what
the instrument can resolve, on a field whose answer is already known. Done here
first:

| field on the PH10595 mesh | RMS `div(U)` / gradient scale |
|---|---|
| shipped converged k-omega SST | **9.45e-03** |
| shipped interpolated LES truth | **5.90e-03** |
| G0 forward model reproducing the SST stress | **9.451e-03** |

`of_read.structured_gradient` has a **floor of ~9e-3 on this curved mesh**, so an
absolute continuity threshold below that is unmeasurable here and is not
registered. The supervisor's brief stated "PH mesh is measurable"; measured, it is
not, at the 1e-3 level. Registered instead:

* **primary:** OpenFOAM's own `time step continuity errors : sum local` from the
  solver log, which is flux-consistent and exact to round-off for a converged
  SIMPLE solve;
* **secondary:** the structured-gradient value **as a ratio to 9.45e-3**, with a
  registered band of `[0.5, 2.0]` for a healthy member.

---

## 6. Costing, measured on this machine before any ensemble run

**One forward evaluation, measured** (`/home/ubuntu/closure-data/xiao/harness2.log`,
`G0_sst`, single core, PH10595, 15,600 cells, prescribed-tau with outer
deferred-correction loop to `max|dU|/|U| < 1e-5`):

| | |
|---|---|
| outer iterations | 4 |
| SIMPLE iterations, total | 1,624 |
| wall seconds, single core | **99.7** |
| **core-hours per forward evaluation** | **0.0277** |

| design | forward evaluations | core-hours | wall on 16 cores | dollars @ $0.0513/core-h |
|---|---|---|---|---|
| paper's `N` = 60 x 10 iterations, **members converging** | 600 | **16.6** | ~1.0 h ideal, 2-3 h under current load | **$0.85** |
| same, **members at the registered caps** (6 outer x 2,000 SIMPLE, the worst case measured: 967.6 s) | 600 | **161.3** | ~10 h ideal | **$8.28** |
| reduced VARIANT, 30 members x 15 iterations | 450 | 12.5 - 121 | — | $0.64 - $6.21 |

**Neither the full design nor the worst case exceeds the 487-core-hour
authorisation**, so no compute approval is needed and no reduced variant is
required on cost grounds. The band 17-161 core-hours is wide because it is bounded
by the registered per-member caps rather than by a convergence guarantee, and that
is stated rather than averaged away. KL expansion, Kalman updates and I/O are
under 0.1 core-hours combined and are neglected, as the paper also does (§5.1).

**The blocker is not cost.** It is §7.

---

## 7. The H0 harness gate, and the exact gap

The paper's forward model is `tauFoam`: momentum and pressure with `tau`
prescribed and **no turbulence transport equations**. No such solver exists on
this machine. Two substitutes were built from the **already-validated**
`kOmegaSSTCorrected` interface (`sdk/openfoam/sparta`, `turbulence off;` so `k`
and `nu_t` are frozen fields), with

`tau_model = (2/3) k I - 2 nu_t S + 2 k bijDelta` and
`bijDelta = b_target + (nu_t/k) S`,

which equals `tau_target` exactly once `S` converges, while the linear part stays
implicit — Wu, Sun, Xiao & Wang's conditioning fix (flag F16; that paper is **not
in the corpus** and is still flagged for retrieval). An outer deferred-correction
loop refreshes `bijDelta` as `S` moves.

**Both substitutes reproduce the baseline (G0 PASS) and both fail on the truth:**

| implicit viscosity | G0: prescribe SST stress | H0: prescribe LES truth stress | outer-loop `max|dU|/|U|` per iteration | cells with `nu_t^L` clipped at 0 |
|---|---|---|---|---|
| baseline SST `nu_t` (frozen) | **0.15659** (gate 0.1565) | **0.29799** (gate <= 0.036) | 0.58, 0.18, 0.31 — oscillating | n/a |
| optimal `nu_t^L = -<tau_dev:S>/(2<S:S>)`, clipped >= 0 | **0.15658** | **3.8815** | 0.19, 0.13, 1.21, 1.21, 1.14, 1.22 — **diverging** | 1,872 -> 7,337 (**47 % of the mesh**) |

**H0: GATE FAIL. The lane is BLOCKED.**

**The gap, precisely.** It is not missing code — a `tauFoam` clone is roughly 100
lines of a `simpleFoam` copy. It is **conditioning**. Prescribing the true
Reynolds stress explicitly on a separated hill at `Re_H` = 10595 on 15,600 cells
diverges; the optimal linear projection makes it worse because **47 % of cells
want a negative eddy viscosity against the true stress**, and clipping removes the
implicit stabilisation exactly where it is most needed. Xiao et al. ran
`Re_b` = 2800 on 1,500 cells, where the molecular viscosity is ~3.8x larger
relative to the flow and the cell Reynolds number is roughly an order of magnitude
smaller. **Writing `tauFoam` would reproduce the divergence in C++.**

**One path does work on this exact case, and it was measured:** `b^Delta` **and**
`R` together, with `R` extracted by `kCorrectiveFrozenFoam` and `k` transported,
gives `U_rms` = **0.009319** on PH10595 against the SST baseline's 0.1565 — a
**94.0 % reduction**, inside the H0 band. It independently reproduces the W2
SpaRTA campaign record, which reports `eps(U)/eps(U_0)` = 0.003331 on this case
(`sqrt(0.003331) x 0.1565 = 0.00903`, agreement to 3 %).

**But it cannot be used for an EnKF member as it stands**, and the reason is
structural: `kCorrectiveFrozenFoam` computes `R` as the residual of the steady `k`
equation with the **true** velocity field frozen in. An ensemble member has a
perturbed stress and an unknown velocity. `R` is not available to it.

### Three costed options, for the supervisor to choose between. None is started.

1. **Inner-loop `R`.** Recompute `R` per member inside the outer loop from the
   member's own current `U` rather than from the truth. Adds one frozen-solve
   (29 s measured on PH10595) per outer iteration: forward-evaluation cost rises
   from 0.0277 to ~0.055 core-hours, so the full design becomes **33-190
   core-hours** — still inside the authorisation. **This is a departure from
   Xiao's algorithm and would have to be registered as such.** Untested.
2. **Change the case.** Run the lane at a Reynolds number closer to the paper's.
   PH2800 is not on disk; the closest available is the parametric hill family at
   `Re_H` = 5600 (`alpha_10`, standard geometry), roughly 2x the paper's `Re`
   instead of 3.8x. Requires re-running G0/H0 there: **~0.5 core-hours** to find
   out. Cheap, and it tests the conditioning explanation directly.
3. **Ship BLOCKED.** Record the forward-model gap as the finding — that the
   paper's `tauFoam` propagation does not transfer to a 10x finer mesh at 3.8x the
   Reynolds number — and stop.

**Recommendation: option 2 first**, because it costs half a core-hour, it is a
direct test of the stated cause, and if it passes then option 1 is unnecessary and
the lane runs as designed at a labelled lower `Re`.

---

## 8. What this lane CANNOT see (registered now, whatever is decided)

* **A single case at a single Reynolds number**, on one mesh, with no
  grid-refinement study.
* **Orientation is never perturbed**, by design and by the paper's own admission
  (p. 10). Any region where the error is an eigenvector error is outside the
  uncertainty space by construction, and a coverage failure there says nothing
  about the inference.
* **Observation placement is ours.** The paper gives a rule and a figure, not
  coordinates. Coverage and posterior accuracy both depend on it, and a different
  reader would place them differently.
* **`Re` = 10595 against the paper's 2800, SST against Launder-Sharma, 15,600
  cells against 1,500.** No number here is comparable to a number there.
* **If a reduced ensemble is used**, the posterior spread is biased low and the
  H2 coverage verdict inherits that bias.
* **The continuity instrument floors at ~9e-3 on this mesh** (§5), so per-member
  continuity is graded as a ratio, not against an absolute tolerance.
* **The forward model is not the paper's `tauFoam`** and, as of this freeze, no
  substitute on this machine passes the H0 harness. Whatever runs later runs under
  §7's disclosure.

---

## DEPARTURE 1 — 2026-08-21, Reynolds-number switch, registered BEFORE the re-run

**The frozen text above is untouched.** This section is appended under the
supervisor's GO on §7 option 2 and is written before the re-test is run. Its
purpose is to make the outcome binding in both directions.

### The case

**`alpha_10_9000_3036`**, from the benchmark's `Parm_PH_29/alpha_10/` family.
`nu` = 1.786e-4, **`Re_H` = 5600** (the case's own `transportProperties` comment),
15,600 cells, domain length 9.000`H` x height 3.036`H` — the **standard periodic
hill geometry**, `alpha` = 1.0, the same shape as `PH_Breuer` and as the paper's
hill. Benchmark split: **train**, so no strict test case is opened by this lane;
Xiao's method is per-case inference against that case's own sparse observations
and touches no held-out data of any other lane.

### The Reynolds numbers, stated plainly

The paper and the benchmark use the same definition — crest height `H` and bulk
velocity at the crest.

| | `Re` | ratio to the paper |
|---|---|---|
| Xiao et al. 2016, their own hill | **2800** | 1.0 |
| `alpha_10_9000_3036` (this departure) | **5600** | **2.0x** |
| `PH_Breuer` / PH10595 (the frozen registration) | **10595** | **3.78x** |

Moving from 10595 to 5600 halves the Reynolds number and leaves the mesh count
unchanged at 15,600 against the paper's 1,500, so the cell Reynolds number falls
by ~2x while the mesh disparity is untouched. **If the conditioning explanation in
§7 is right, halving `Re` should move the harness measurably toward the gate; if
the harness fails identically at 5600, the explanation is wrong.** That is the
test.

### Gates at 5600, registered now

Baseline row, `BASELINES.md` §3, `alpha_10_9000_3036`: **SST `U_rms` = 0.1556**,
`U_mae` = 0.1304.

* **G0 (identity), repeated on this case.** Prescribing the case's own baseline
  SST stress through the forward model must return `U_rms` within **1e-3
  absolute** of 0.1556.
* **H0 (harness).** Prescribing the case's **LES truth stress** must return
  **`U_rms` <= 0.0358**, i.e. **a >= 77 % reduction** against the 0.1556 baseline.
  This is the same *relative* band that was frozen for PH10595 (there: 0.036
  against 0.1565, a 77 % reduction), re-expressed on this case's own baseline so
  the two are the same test and not two different ones.
* Both configurations of §7 are run: frozen baseline `nu_t`, and the optimal
  `nu_t^L` projection with its clip fraction reported.

### Decision rule, verbatim and binding

> **H0 PASS at 5600** -> the full EnKF runs at 5600 as a **labelled VARIANT** —
> lower Reynolds number than the registered PH10595, and still 2.0x the paper's
> own regime of `Re_b` = 2800. The registered design is unchanged: `N` = 60
> members, 10 EnKF iterations, 16 KL modes per field, `l` = `H`, 18 observations,
> `sigma_obs` = 10 % of truth, checkpoint every EnKF iteration, hard stop
> unchanged at 487 core-hours.
>
> **H0 FAIL at 5600** -> **the conditioning explanation is REFUTED**, no ensemble
> runs, and the case ships **BLOCKED with the refutation as the cause** — not with
> the conditioning story, which will have been tested and found wrong.

### Standing, regardless of the outcome at 5600

**The PH10595 H0 GATE FAIL of §7 stands in `RESULTS.md` as the forward-model
harness finding.** Moving down in Reynolds number does not erase it. The
divergence numbers — `U_rms` **0.29799** with an oscillating outer loop
(0.58 / 0.18 / 0.31) under frozen baseline `nu_t`; **3.8815** with a diverging
outer loop (0.19 / 0.13 / 1.21 / 1.21 / 1.14 / 1.22) under the optimal projection;
the `nu_t^L` clip fraction rising to **7,337 of 15,600 cells = 47 %** — and the
paper's `Re` and mesh contrast stay in the record as written.

### Cost of this departure

Two forward evaluations (G0 and H0) on 15,600 cells at the measured 0.0277
core-hours each for a converging run, and at most 0.269 core-hours each at the
registered caps: **0.06 to 0.54 core-hours**. Charged to this lane.
