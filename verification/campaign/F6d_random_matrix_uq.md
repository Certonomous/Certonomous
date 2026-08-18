# F6d — random-matrix / maximum-entropy model-form UQ on periodic hills, and a sign error found in F6a's eigenvalue perturbation

Date: 2026-07-30. Family F6, sub-family d. Case: **F6b periodic hills**
(`PH_Breuer`, Re_H = 10595, 15,600 cells). Framework: **Xiao, Wang & Ghanem,
"A Random Matrix Approach for Quantifying Model-Form Uncertainties in
Turbulence Modeling," arXiv:1603.09656 (2016), also CMAME 313:941-965.**

This is the piece that `F6a_epistemic_propagation.md` §9 scoped and explicitly
did not start, on the target it recommended (§9.5: *"If this framework is
pursued at all, F6b is the properly-scoped first target"*). That
recommendation was checked and honoured — see §2.

Machine-readable companion: `F6d_random_matrix_uq.json`.
Working directory: `demo-output/website/dafoam/f6d_random_matrix_uq/`.

---

## Headline

Three results, in descending order of how much they change the standing record.

1. **The eigenvalue-perturbation source term used throughout F6a applies the
   perturbation with the opposite sign to the one its own comment states.**
   All 18 `system/fvOptions` dictionaries under
   `demo-output/website/dafoam/f6a_epistemic_band/` end their `codeAddSup`
   with `eqn += fvc::div(deltaR)`, which in OpenFOAM makes the *effective*
   anisotropy `b_eff = 2 b_Bouss - b_pert`, i.e. the perturbation applied
   backwards. On F6a's own NASA-hump mesh this hands the momentum equation a
   **non-realizable** Reynolds stress in **95.93% of its 51,626 cells** for the
   1C corner. F6a's recorded channel-3 numbers are therefore not the 1C/2C/3C
   corner states. Established by four controlled solver runs, by the OpenFOAM
   v2606 sources, by a one-character A/B replication, and by a realizability
   audit on F6a's own converged baseline field — §4.
2. **The random-matrix framework was implemented, verified against the paper's
   own stated properties (15 checks, 0 failures), and propagated at both of the
   paper's own dispersion settings.** At the small-dispersion setting δ = 0.2,
   40 samples give a reattachment band that **does contain the LES truth but is
   much wider than the corner union, not tighter** — the opposite of the outcome
   this thread was hoping for (§6). At the paper's large setting δ = 0.6, also
   40 samples, the band is wider still and *worse* behaved (§7).
3. **A pre-registered risk was confirmed quantitatively, and at δ = 0.6 it is
   fatal.** `F6a_epistemic_propagation.md` §9.2 warned that silently dropping the
   hardest-to-converge Monte Carlo samples "biases the resulting distribution
   toward the calm center and away from exactly the tail behavior a model-form
   uncertainty estimate exists to capture." Measured here at δ = 0.2: the 12
   members that fail a residual gate have mean reattachment **5.556**, the 28
   that pass have **6.695**, and the truth is 4.6–4.7. Gating throws away the
   members closest to the truth (§6.4). At δ = 0.6 only 5 of 40 members meet the
   same gate, and **the gated subset stops containing the LES range altogether**
   while the ungated ensemble still contains it (§7.2) — gating does not merely
   bias the band there, it destroys the one property the band was built to have.

---

## 1. What the paper prescribes — read in full, equation by equation

Source fetched live this session and read from a local `pdftotext` extract of
the full 42-page PDF (not the abstract, not a secondary summary):

- `docs/papers/xiao_wang_ghanem_1603.09656.pdf`
- `docs/papers/xiao_wang_ghanem_1603.09656.txt`

The method, with the paper's own equation numbers (each is quoted in the
implementation's docstring at the point it is used,
`f6d_random_matrix_uq/rmt_sampler.py`):

| step | equation | content |
| --- | --- | --- |
| mean field | (9) | `[R_bar] = [L_R]^T [L_R]`, Cholesky, `L_R` upper triangular, diagonal ≥ 0 |
| realization | (8) | `[R] = [L_R]^T [G] [L_R]` with `E{[G]} = [I]` |
| normalised matrix | (14) | `[G] = [L]^T [L]`, `[L]` upper triangular, independent elements |
| off-diagonals | (15), (19) | `L_ij = σ_d w_ij`, `i < j` |
| diagonals | (16), (24) | `L_ii = σ_d √(2 u_i)` |
| scale | (20) | `σ_d = δ (d+1)^(-1/2)`, `d = 3` |
| diagonal marginal | (17) | `u_i ~ Gamma(shape (d+1)/(2δ²) + (1-i)/2, scale 1)` |
| admissible dispersion | (13) | `0 < δ < √((d+1)/(d+5)) = √2/2` for `d = 3` |
| spatial correlation | (18) | Gaussian kernel on `L_ij` and `L_ii²` |
| random field | (22), (23) | Karhunen–Loève expansion; Fredholm eigenproblem |
| non-Gaussian field | (26), (27) | polynomial chaos of the gamma marginals |
| propagation | App. A 3.1 | *"Use the obtained sampled Reynolds stress to velocity and other QoIs by solving the RANS equation"* |

Configuration follows the paper's own Table 1 wherever the case allows:
`N_KL = 30` modes, KL mesh 50 × 30, `N_p = 3`, anisotropic uniform correlation
lengths `l_x/H = 2`, `l_y/H = 1`, and the two demonstrated dispersion values
`δ = 0.2` (Case 1) and `δ = 0.6` (Case 2).

### 1.1 Two internal inconsistencies in the paper, both recorded rather than quietly patched

Found by implementing it, not by reading it.

- **Appendix A step 2.4 writes `L_ii = σ_d √u_i`, dropping the factor 2** that
  the main text carries in Eqs. (16) and (24). The main text is right: only
  with the 2 does `E{[G]} = [I]` hold. Verified numerically both ways —
  200,000 point samples give `diag E[G] = [0.99936, 0.99985, 0.99981]` with the
  factor 2, and `[0.49983, 0.50504, 0.51025]` without it (δ = 0.2). The
  Appendix-A form would silently halve the whole construction.
- **Appendix A step 1.3 says the polynomial-chaos expansion of Eq. (17) is
  "for off-diagonal terms only."** Eq. (17) is the gamma PDF of `u_i`, which by
  Eq. (16) enters the *diagonal* terms. §§3.3–3.4 state the correct
  assignment. The main text was followed.

Neither changes the method; both would silently break an implementation that
followed Appendix A literally, so both are recorded.

---

## 2. Confirming the target case, as instructed

`F6a_epistemic_propagation.md` §9.5 recommended F6b periodic hills over the
NASA hump, on the grounds that (a) the paper's own demonstration geometry is
periodic hills, and (b) the hump had already broken two UQ machineries. Both
grounds check out — the paper's §4 opens *"we use the flow over periodic hills
at Reynolds number Re = 2800 to demonstrate the proposed model-form uncertainty
quantification scheme"* — and the recommendation is honoured. One difference
is recorded rather than glossed: **the paper's demonstration is at Re = 2800;
F6b is at Re_H = 10595**, a factor of 3.8 higher and a genuinely harder,
thinner-shear-layer flow. Nothing in this record assumes the paper's
convergence experience transfers.

### 2.1 The F6b baseline is real, converged, and independently corroborated

| check | result |
| --- | --- |
| Solve | `demo-output/website/solve_registry/f6b_gate_20260729T035745Z.log`, simpleFoam, 4 ranks, 10,000 iterations, 03:57:45→04:06:16 UTC |
| Residual history (initial residuals, read from that log) | t=1000: Ux 5.54e-4, p 4.45e-3 → t=5000: Ux 1.45e-6, p 3.50e-6 → **t=10000: Ux 3.60e-9, Uy 2.52e-9, p 1.35e-8, k 8.94e-9, omega 8.94e-10** — monotone over four decades, flat at the end |
| `scripts/check_convergence.py` verdict | `NOT_CONVERGED` — **and this is a false negative, diagnosed, not waved away** |
| Why the checker is wrong here | the case's own `system/fvSolution` line 82 sets `residualControl { p 1e-15; }`. 1e-15 is below what a GAMG pressure solve on this mesh can reach, so simpleFoam never prints its `SIMPLE solution converged` sentence and the checker's signature 3 fires. This is exactly the failure mode **L-21** already names (a `residualControl` entry that means the gate never fires); it is being reported here rather than silently overridden. |
| Independent corroboration | our own reconstructed solve reproduces the benchmark's *shipped* kOmegaSST result to **5 significant figures**: separation x/h 0.2589993 vs 0.2590151, reattachment **7.643915 vs 7.643895** (`f6b_periodic_hills/case_breuer_re10595/gate_result.json`) |

**Baseline QoI**: separation x/h **0.2590**, reattachment x/h **7.6439**,
against the Fröhlich et al. (2005, JFM 526:19-66) LES reference of separation
≈ 0.2 and reattachment **4.6–4.7**. The baseline over-predicts the
recirculation length by **≈ 64%** — a large, well-known kOmegaSST deficiency,
and a great deal of room for a band to be informative in.

---

## 3. What was built

All under `demo-output/website/dafoam/f6d_random_matrix_uq/`.

| file | what it is |
| --- | --- |
| `rmt_sampler.py` | the sampler: KL expansion (Nyström solution of Eq. 23), PCE of the gamma marginals (Eq. 27), Cholesky of the mean field with a realizability audit, `[R] = [L_R]^T [G] [L_R]`, OpenFOAM symmTensor I/O |
| `verify_sampler.py` | 15 checks of the sampler against the paper's own stated properties, run before any CFD |
| `build_ensemble.py` | builds and drives the ensemble; documents and implements the propagation model |
| `build_signdemo.py`, `run_live_corners.py` | the eigenspace-corner comparison and the sign A/B |
| `realizability_of_flipped_corner.py` | the realizability audit of §4.4 |
| `barycentric_reach.py` | how far each method actually moves the anisotropy state |
| `analyse.py`, `aggregate.py`, `plot_band.py`, `cost.py` | QoI extraction, aggregation, figure, measured cost |
| `signcheck/` | the four-run sign-convention experiment of §4.2 |

### 3.1 The propagation model, stated exactly

The paper prescribes the sampled Reynolds stress and solves the RANS equations
for velocity (Appendix A step 3.1). Implemented literally: `turbulence off`
freezes k, ω and ν_t at their converged baseline values; ν_t is retained only
inside the implicit diffusion operator for linear-solver conditioning and is
then cancelled exactly by an explicit source, so that at convergence the
deviatoric stress carried by the momentum equation is `dev([R_sample])` and
nothing else:

```
deltaR = -nut*dev(twoSymm(grad U)) - dev(Rsample)
eqn += fvc::div(deltaR)            =>   R_eff = R_model - deltaR = dev(Rsample)
```

Every member restarts from the converged baseline field (including its
`meanVelocityForce` driving gradient) and runs a fixed 4,000-iteration budget,
serial, one core.

### 3.2 Sampler verification — 15 checks, 0 failures, before any solve

`verify_sampler_result.json`. Selected results:

| check | result |
| --- | --- |
| V1 `E{[G]} = [I]` | max abs error 0.00064 (δ=0.2), 0.00220 (δ=0.6), over 200,000 draws |
| V2 δ recovered from Eq. (12) | 0.19971 vs 0.2; 0.59873 vs 0.6 |
| V3 every `[G]` positive definite | min eigenvalue 4.462e-1 (δ=0.2), 1.501e-2 (δ=0.6) over 200,000 draws |
| V4b KL variance captured by 30 modes | **98.95%** (the paper reports ~90% for its own setup — ours is a uniform bounding-box KL mesh, so this is *not* a reproduction of their number and is not claimed as one) |
| V5 PCE marginal vs Gamma(k_i,1) | worst KS statistic 9.6e-4 (δ=0.2), 1.3e-3 (δ=0.6) |
| V5b PCE coefficients quadrature-converged | max relative change 1.4e-16 between two quadrature orders; `U_β(i=1)` = [50.0, 7.055389, 0.332712, 0.003953] at δ=0.2 — `U_0 = 50` is exactly the gamma shape `4/(2·0.2²)`, an independent check |
| V6 synthesised field reproduces kernel Eq. (18) | max deviation 0.0505 over 60 probe points, 4,000 realisations |
| V7a sampled `[R]` realizable on the RANS mesh | min eigenvalue **+1.850e-7** over 60 field realisations × 15,600 cells — never negative |
| V7b `E{[R]}` returns `[R_bar]` | 2.68% of max\|R_bar\| over 60 samples (Monte Carlo error, falls as 1/√N) |

Two bugs in the *implementation* were caught by these checks and are recorded
because a silent version of either would have produced plausible garbage:
`numpy.polynomial.hermite_e.hermegauss` loses its weights to floating-point
overflow well before 200 nodes; and `gammaincinv(k, Φ(w))` returns `+inf` once
the double-precision normal CDF saturates at exactly 1 (w ≳ 8.3), which
poisoned every PCE coefficient. Both are fixed and both now fail loudly.

### 3.3 The baseline Reynolds stress is realizable — checked, not assumed

The Cholesky step of Eq. (9) needs `[R_bar]` positive semi-definite, and a
Boussinesq stress `R = (2/3)k I - 2 ν_t S` is *not* guaranteed to be. Measured
on the F6b baseline: **0 of 15,600 cells** have a negative eigenvalue; worst
`λ_min/tr(R)` = 0.140. No diagonal jitter was needed anywhere. (On the F6a
hump baseline the same audit gives 0.897% of cells with a negative eigenvalue
— a separate, real property of that field, reported in §4.4.)

### 3.4 The null test: the injection path is exact

Propagating `R_sample = R_bar` must leave the baseline where it is, because
`deltaR` is then identically zero at the baseline velocity field.

| quantity | baseline | null propagation, 4,000 iterations |
| --- | --- | --- |
| first-iteration Ux initial residual | — | **5.46e-8** |
| separation x/h | 0.2589993 | 0.2589800 |
| reattachment x/h | 7.643915 | **7.643814** |

This is the end-to-end verification of the sign, the field I/O, the frozen
turbulence, and the discretisation, in one number. It also **calibrates the
method's noise floor**, which every band below is judged against: the null
member's final Ux initial residual drifts from 5.46e-8 up to a floor of
1.57e-5, and that floor moves reattachment by **1.0e-4 in x/h** and the
station-profile scaled MAE by **0.44 percentage points**. Anything narrower
than that is noise, not signal.

---

## 4. The sign error in F6a's eigenvalue perturbation

This was not the object of the exercise. It was found while establishing the
sign convention needed to inject a Reynolds stress correctly, and it is
reported because it changes what `F6a_epistemic_band.md` and
`F6a_epistemic_propagation.md` mean.

### 4.1 What the code does

All 18 `system/fvOptions` dictionaries under `f6a_epistemic_band/` (checked by
`grep -rl "eqn += fvc::div(deltaR)" --include=fvOptions`, 18 files; zero use
`-=`) build `deltaR = blendDelta·2k(b_pert − b_B)` and end with

```
eqn += fvc::div(deltaR);
```

with the dictionary's own comment stating that *"the momentum forcing is
deltaR = 2k(bBlend - bBoussinesq)"*.

### 4.2 What that operator actually means — established by experiment, not by reading

simpleFoam assembles `div(phi,U) + divDevReff(U) == fvOptions(U)`
(`.../applications/solvers/incompressible/simpleFoam/UEqn.H` lines 9, 11) with
`divDevReff(U) = -div(2 ν_eff symm(grad U))`
(`.../src/TurbulenceModels/turbulenceModels/linearViscousStress/linearViscousStress.C`
lines 107–117); `fvMatrix::operator+=` on an explicit field does
`source() -= V*su` (`.../src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.C` line
1682); and OpenFOAM's own `meanVelocityForce`, whose physical meaning is
unambiguous, drives the flow with exactly `eqn += flowDir*gradP`
(`.../src/fvOptions/lnInclude/meanVelocityForce.C` line 209). Together these
give `R_eff = R_model − deltaR`.

Because reading source code is not the same as running it, that conclusion was
put to a **controlled four-run experiment** on this very mesh
(`f6d_random_matrix_uq/signcheck/`): laminar periodic-hill flow at Re = 100,
driven by `meanVelocityForce` to hold Ubar = 0.72, discriminated by the
driving pressure gradient the solver must find.

| run | ν | coded source | driving gradient found |
| --- | --- | --- | --- |
| `ref_nu1` | ν₀ = 0.0072 | none | **0.01541756** |
| `src_minus` | 2ν₀ | `deltaR = -2ν₀ S` | **0.01542612** (matches `ref_nu1` to 0.055%) |
| `ref_nu3` | 3ν₀ = 0.0216 | none | **0.03802645** |
| `src_plus` | 2ν₀ | `deltaR = +2ν₀ S` | **0.03802046** (matches `ref_nu3` to 0.016%) |

`src_minus` collapses onto the ν₀ reference and `src_plus` onto the 3ν₀
reference. That is only possible if `R_eff = R_model − deltaR`. The two
reference runs carry no coded source at all, so the comparison needs no
interpretation of flow physics. (A first attempt at this test, at Re = 10, was
non-discriminating and was discarded: in the Stokes limit the velocity field
is independent of viscosity, so all four runs agree by construction. That
dead end is recorded because it looked like a result for about ten minutes.)

### 4.3 Consequence: the perturbation runs backwards

Substituting `deltaR = 2k(b_pert − b_B)` and `R_model,dev = 2k b_B`:

```
b_eff = 2 b_B - b_pert        i.e.   b_eff - b_B = -(b_pert - b_B)
```

The intended perturbation is applied with the opposite sign and the same
magnitude — a reflection of the corner state through the baseline.

### 4.4 And it leaves the realizable set — measured on F6a's own mesh

`realizability_of_flipped_corner.py`, run on both projects' own converged
kOmegaSST baselines (`turbulenceFields(R)` written by
`simpleFoam -postProcess`). Fraction of cells whose imposed Reynolds stress has
a negative eigenvalue, i.e. is not the covariance of any velocity field:

| case | corner | intended `b_pert` | **actual, with `eqn +=`** |
| --- | --- | --- | --- |
| **F6a NASA hump** (51,626 cells, t=1795) | 1C | 0.90%\* | **95.93%** (worst barycentric coordinate −2.325) |
| | 2C | 0.13%\* | 0.23% |
| | 3C | 0.00% | 4.33% |
| **F6b periodic hill** (15,600 cells, t=10000) | 1C | 0.00% | **98.83%** |
| | 2C | 0.00% | 0.00% |
| | 3C | 0.00% | 1.17% |

\* the hump's *baseline* Boussinesq stress is itself non-realizable in 0.897%
of cells (worst barycentric coordinate −1.162); that residue carries into the
"intended" column and is a property of the baseline field, not of the
perturbation.

### 4.5 The direct A/B, and the single most damning number

Two runs on the F6b mesh, byte-identical except one character of C++
(`f6d_random_matrix_uq/signdemo/`), both with the turbulence model live exactly
as F6a ran it, both restarting from the converged baseline, both 4,000
iterations, 3C corner (`b_pert = 0`, so the two hypotheses predict opposite
things: zero deviatoric Reynolds stress, versus double it):

| run | operator | final Ux initial residual | reversed-flow regions on the floor |
| --- | --- | --- | --- |
| `f6asign_threeC` | `eqn +=` (F6a's) | **2.41e-7** (converged) | 2 |
| `corrected_threeC` | `eqn -=` | 2.70e-3 (not converged) | 7 |

And then the same one-character change applied to **F6a's own hump case, mesh,
schemes and restart field** (`f6d_random_matrix_uq/f6a_recheck/`, 3,800
iterations, the case's own cap):

| corner | F6a's recorded run (`+=`) | corrected (`-=`) |
| --- | --- | --- |
| 1C | **velocity limiter active on 24,864 cells (48.16%)**; wall trace 230+ noise crossings; reported reattachment 0.5278 described in F6a's own record as "an artifact of a search window" | **limiter active on 0 cells (0.00%)**; a clean two-crossing bubble, separation x/c 0.6636, reattachment x/c **1.0409** |
| 2C | unconverged, slow monotone growth | limiter 0.00%; main bubble 0.6582 → **1.1085** |
| 3C | converged in 2,948 iterations, reattachment 1.1069 | limiter 0.00%; wall trace fragments into 14 crossings |

The limiter line is the cleanest single piece of evidence in this record:
`limitVelocity limitVelocity1 Limited 24864 (48.16%) of cells` in
`demo-output/website/solve_registry/uq_oneC_20260729T023701Z.log`, versus
`Limited 0 (0%) of cells` in
`f6d_random_matrix_uq/f6a_recheck/corrected_oneC/log.simpleFoam`. Half the
mesh was being velocity-clipped because it was being fed a Reynolds stress that
no flow can have.

### 4.6 What this does and does not do to F6a's conclusions

**Does not overturn the headline negative result.** All three corrected-sign
hump corners still come back `NOT_CONVERGED` from
`scripts/check_convergence.py` at the 3,800-iteration cap, with Ux initial
residuals plateauing at 7.08e-3 (1C), 1.05e-3 (2C), 2.85e-3 (3C). F6a's
statement that the corners are not reachable on that case within that budget
**stands**.

**Does overturn the numbers and the mechanism.** `F6a_epistemic_band.md`'s
channel-3 values (1C 0.5278, 2C 0.6701, 3C 1.1069) are not the 1C/2C/3C corner
states, and `F6a_epistemic_propagation.md` §4's reduced envelope
**[1.1069, 1.3077]** — the document's own "single most important number" — is
built entirely from channel-3 runs and therefore does not mean what it says it
means. §8's reading that 1C's failure is "a property of the target perturbed
state itself on this mesh" is not supported: the target state actually being
imposed was non-realizable in 96% of cells, and with the intended target the
limiter goes quiet and the wall trace becomes a clean single bubble.

**Adds something F6a never had.** With the corrected sign the hump's 1C and 2C
corners give reattachment x/c **1.0409** and **1.1085**, which bracket the NASA
experimental value **1.100** — from below and above, by −5.4% and +0.8%. Those
two numbers are **not** gate-passing and must not be quoted as a band; they are
recorded as the first evidence that the intended corners are physically
sensible on that case, and as the reason the next attempt is worth its cost.

---

## 5. How far each method actually moves the Reynolds stress

Before any comparison of bands, the diagnostic that explains them
(`barycentric_reach.json`): distance travelled in the barycentric plane from
the baseline state, turbulent-kinetic-energy weighted, over 200 field draws.

| perturbation | k-weighted mean barycentric displacement | mean \|log(k_sample/k_baseline)\| |
| --- | --- | --- |
| 1C corner | 0.785 | 0 (corners hold k fixed) |
| 2C corner | 0.697 | 0 |
| 3C corner | 0.331 | 0 |
| random matrix, δ = 0.2 | **0.090** | 0.068 |
| random matrix, δ = 0.6 | **0.262** | 0.204 |

The two frameworks are not small and large versions of one thing. The corner
method makes a **large, spatially coherent, k-preserving** move; the random
matrix makes a **small, spatially incoherent, k-perturbing** one. At the
paper's own large dispersion δ = 0.6 the random field still travels only about
a third of the way to the 1C corner. Any comparison of band widths has to be
read against that.

---

## 6. The propagated band, δ = 0.2 (the paper's Case 1)

40 samples, seed 20260730, 4,000 iterations each, serial.
`f6d_random_matrix_uq/aggregate_result.json`.

### 6.1 Yield

| | |
| --- | --- |
| members built | 40 |
| members producing a primary recirculation region at iteration 4,000 | **40** |
| members meeting a final Ux initial-residual gate of 1e-3 | 28 |
| final Ux initial residual across admitted members | min 2.54e-4, median 8.28e-4, max 4.27e-3 |
| reversed-flow regions on the floor | min 1, median 3, max 6; only **12.5%** (5 of 40) of members keep the baseline's single clean bubble |

Two of the 40 (`d0.2_s035`, `d0.2_s037`) completed 4,000 iterations and logged
a successful `wallShearStress` write but had no `4000/` directory on disk
afterwards, with no error anywhere in either log. **The cause was not
identified.** Both were re-run unchanged and completed normally; their first
logs are kept as `log.simpleFoam.attempt1`. Per L-22 no cause is asserted.
Because those two re-runs landed after a first pass of the aggregation, an
earlier draft of this section reported the ensemble as 38 admitted / 27 gated.
**Every number in §§6–7 below is recomputed from the final
`aggregate_result.json` over all 40 members**, and that file's δ = 0.2 block
was checked to reproduce bit-for-bit against the earlier one before the two
re-runs were folded in.

### 6.2 The band on reattachment

Fröhlich et al. LES: **4.6–4.7**. kOmegaSST baseline: **7.6439**.

| statistic | all 40 admitted members | 28 residual-gated members |
| --- | --- | --- |
| min | 2.710 | 3.098 |
| 5th percentile | 3.933 | 4.702 |
| median | 6.312 | 7.395 |
| mean | 6.353 | 6.695 |
| 95th percentile | 7.912 | 7.903 |
| max | 8.112 | 8.112 |
| 90% interval width | **3.979** | 3.201 |
| full support width | 5.402 | 5.014 |
| contains the LES range? | **yes** | yes |
| fraction of members at or below the LES upper bound | 15.0% | 7.1% |

### 6.3 Against the eigenspace corner union — the question this thread asked

The corners were run on the same case, from the same baseline, two ways.

**In the corner method's own live form** (turbulence model live, perturbation
recomputed each outer iteration, corrected sign — `signdemo/live_*`):

| corner | primary-bubble reattachment x/h | reversed regions | final Ux residual |
| --- | --- | --- | --- |
| 1C | 4.022 | 2 | 1.09e-3 |
| 2C | **4.819** | 1 (clean) | 2.97e-4 |
| 3C | fragments (7 regions) | 7 | 2.70e-3 |

**In this study's prescribed-stress form** (identical injection path to every
random-matrix member — `ens/corner_*`):

| corner | primary-bubble reattachment x/h | reversed regions | profile scaled MAE vs LES | final Ux residual |
| --- | --- | --- | --- | --- |
| 1C | 2.056 | 9 | **77.1%** | 7.54e-3 |
| 2C | 5.745 | 5 | 27.2% | 3.87e-3 |
| 3C | 6.515 | 8 | 26.7% | 1.50e-3 |

**Answer: no. The probabilistic band is not tighter than the corner union — it
is roughly five times wider.** The live-form corner union spans
[4.022, 4.819], width **0.797** in x/h, and covers the LES value; the
random-matrix 90% interval spans [3.933, 7.912], width **3.979** — a factor of
**5.0**. Both contain the truth; the corner union is far more informative about
where it is.

Three qualifications, because that comparison is not clean and pretending
otherwise would be the easy mistake here:

1. **None of the corner runs met a convergence gate either** (best is 2C at
   2.97e-4, still 600× the case's nominal 5e-7 target, and 3C fragments
   outright). A width computed from two unconverged runs is not a validated
   envelope. The corner union's apparent tightness is at least partly the
   tightness of a two-point sample.
2. **The two are propagated differently.** The corner runs let the turbulence
   model respond to the perturbed field; the random-matrix members, following
   the paper, prescribe a frozen stress. In the *same* prescribed mode the
   corners are far worse behaved than the random-matrix samples (5–9 reversed
   regions and a 77% profile error for 1C, against a median of 3 regions and a
   15.4% mean profile error for the ensemble). So the corner method's advantage
   here is partly an advantage of its propagation mode, not of its parameterisation.
3. **The random-matrix band is doing something the corner union cannot.** It
   has a density, not just endpoints: a median, percentiles, and a measurable
   probability mass (15.0%) at or below the LES value. The corner union has
   two points and no measure. Wider is not automatically worse if the width is
   honest — but on this case, at this δ, the width is not buying accuracy.

### 6.4 The pre-registered risk, confirmed

`F6a_epistemic_propagation.md` §9.2, written before any of this ran, warned
that dropping the hardest-to-converge samples "biases the resulting
distribution toward the calm center and away from exactly the tail behavior a
model-form uncertainty estimate exists to capture."

Measured: the 12 admitted members that fail a 1e-3 residual gate have **mean
reattachment 5.556**; the 28 that pass have **6.695**. The truth is 4.6–4.7.
The members the gate would discard are systematically the ones *closest to the
truth*. Applying the gate moves the 5th percentile from 3.933 to 4.702 and
halves the probability mass at or below the LES upper bound, from 15.0% to
7.1%. §7.2 shows the same mechanism at δ = 0.6, where it is no longer a bias
but a loss of containment outright.

**That is why nothing in this record is filtered.** Both versions are reported
side by side, and the gated version is the one that looks better and is more
wrong.

### 6.5 Velocity profiles

Scaled MAE of |U| against the shipped LES field at the case's own nine
stations, same metric and scaling as the F6b gate record.

| | value |
| --- | --- |
| baseline (serial, same pipeline as every member — the null run) | **12.515%** |
| ensemble mean, δ = 0.2 | 15.386% |
| ensemble best member | 10.109% |
| ensemble worst member | 31.450% |
| noise floor of the propagation scheme (from the null test) | 0.44 percentage points |

The ensemble **mean profile error is worse than the baseline's**. **11 of the
40 members** do beat the baseline, the best by 2.4 percentage points (about
five times the noise floor, so a real improvement) — but 29 are worse, the
worst by 19 points, and nothing in the method identifies which is which in
advance. (An earlier draft of this section stated that only one member beat the
baseline. That was wrong on the ensemble's own data and is corrected here
rather than quietly dropped; the count is `profile_mae_pct < 12.515` over the
`members` array of `aggregate_result.json`.) Sampling the Reynolds stress from the maximum-entropy
distribution at δ = 0.2 does not, on this case, move the mean prediction toward
the LES.

A footnote on comparability that matters: the F6b case's own parallel (4-rank)
run gives 12.952% for the *same* baseline field, against 12.515% serial. The
difference is line-sampling across processor boundaries, not physics. Every
number in this record uses the serial pipeline, because every ensemble member
is serial.

---

## 7. δ = 0.6 (the paper's Case 2)

40 samples, same seed stream, same 4,000-iteration serial budget, same
prescribed-stress propagation path, same baseline restart — the *only* change
from §6 is `δ = 0.2 → 0.6` in the sampler. `aggregate_result.json`,
`random_matrix.d0.6`. δ = 0.6 is inside the paper's own admissibility bound
Eq. (13) (`δ < √2/2 = 0.7071` for `d = 3`) and is the paper's demonstrated
Case 2.

### 7.1 Yield — the ensemble degrades sharply

| | δ = 0.2 (§6) | **δ = 0.6** |
| --- | --- | --- |
| members built | 40 | 40 |
| members producing a primary recirculation region at 4,000 iterations | 40 | **40** |
| members meeting the same 1e-3 final-Ux gate | 28 | **5** |
| final Ux initial residual | min 2.54e-4, median 8.28e-4, max 4.27e-3 | min 5.48e-4, median **2.47e-3**, max 5.44e-3 |
| reversed-flow regions on the floor | min 1, median 3, max 6 | min **2**, median **6**, max **11** |
| members keeping a single clean bubble | 5 of 40 (12.5%) | **0 of 40 (0.0%)** |

Every member still produces a primary recirculation region, so nothing is lost
to outright failure. But the median member now carries six separate reversed-flow
patches on the floor, **no member anywhere in the ensemble reproduces the
baseline's single clean bubble**, and the residual gate that 28 members cleared
at δ = 0.2 is cleared by 5. This is the sampler's own §5 diagnostic showing up
in the solver: at δ = 0.6 the k-weighted barycentric displacement is 0.262
against 0.090, and the sampled field perturbs `k` itself by
`mean |log(k_sample/k_baseline)| = 0.204`.

### 7.2 The band — wider, and gating now destroys containment

Fröhlich et al. LES: **4.6–4.7**. kOmegaSST baseline: **7.6439**.

| statistic | all 40 admitted members | 5 residual-gated members |
| --- | --- | --- |
| min | 1.702 | 4.916 |
| 5th percentile | 2.621 | 4.918 |
| median | 6.382 | 5.114 |
| mean | 6.091 | 6.175 |
| 95th percentile | 8.309 | 7.975 |
| max | 8.336 | 7.984 |
| 90% interval width | **5.688** | 3.057 |
| full support width | 6.635 | 3.068 |
| contains the LES range? | **yes** | **NO** |
| fraction of members at or below the LES upper bound | 17.5% | **0.0%** |

Two things in that table matter more than the widths.

1. **The band gets wider, not more informative.** The 90% interval is 5.688 in
   x/h against 3.979 at δ = 0.2 and 0.797 for the live-form corner union — now
   **7.1× the corner union**. Turning the dispersion up does not buy sharpness;
   it buys a band that spans most of the domain. The station-profile error goes
   with it: ensemble mean scaled MAE **24.92%** at δ = 0.6, against 15.39% at
   δ = 0.2 and 12.52% for the unperturbed baseline, with exactly **1 of 40**
   members beating the baseline (against 11 of 40 at δ = 0.2).
2. **The gated subset stops containing the truth.** `covers_LES_range` is
   `true` for all 40 members and **`false`** for the 5 that meet the residual
   gate: the gated minimum is 4.916, above the LES upper bound of 4.7. At
   δ = 0.2 the convergence gate biased the band (§6.4); at δ = 0.6 the same gate
   **removes containment altogether** — the ungated ensemble bounds the truth
   and the "clean" subset of it does not.

That second point is the sharpest form of the pre-registered §9.2 risk anywhere
in this record. A study that had reported only gate-passing members at δ = 0.6
would have published a band that misses the LES reattachment entirely, and
would have looked *more* rigorous for having filtered.

The gating-bias arithmetic itself is weaker at δ = 0.6 than at δ = 0.2 and is
reported as such: the 35 failing members mean **6.079**, the 5 passing mean
**6.175** — a difference of 0.10 in x/h, far smaller than δ = 0.2's 1.14. The
damage at δ = 0.6 is done by *which* members survive at the low tail, not by a
shift of the whole distribution, and a 5-member subset is too small to carry a
distributional claim. Both facts are stated; neither is used beyond its weight.

### 7.3 Verdict on Case 2

δ = 0.6 does not rescue the negative result of §6, it deepens it. Neither of
the paper's own two demonstrated dispersion settings produces a band on this
case that is tighter than the deterministic corner union, and the larger of the
two produces an ensemble in which no member retains the baseline's flow
topology, 35 of 40 miss a convergence gate, and the conventional act of
filtering to the converged members loses the containment the method exists to
provide.

---

## 8. Cost

Measured from each run's own final `ExecutionTime` line, not estimated
(`cost.json`). All runs serial, one core, OpenFOAM v2606 simpleFoam.

| stage | runs | core-minutes |
| --- | --- | --- |
| sign-convention verification | 4 | 26.00 |
| null test | 1 | 2.26 |
| prescribed corners | 3 | 14.07 |
| live-model corners + sign A/B | 5 | 20.62 |
| random matrix δ = 0.2 | 40 | 135.47 |
| random matrix δ = 0.6 | 40 | 170.35 |
| F6a hump corner recheck | 3 | 26.02 |
| **total** | **96** | **394.79** |

Median cost of one random-matrix ensemble member: **194.0 core-seconds** at
δ = 0.2, **269.0** at δ = 0.6 — the larger dispersion is 39% more expensive per
member as well as less informative, because its members converge more slowly.
`F6a_epistemic_propagation.md` §9.4 estimated 14–31 core-hours for the paper's
own 100-sample propagation on the hump; the same 100 samples on F6b would cost
**5.39 core-hours** at δ = 0.2, i.e. the case choice recommended by §9.5 is also
a factor-of-2.6-to-5.8 saving. That estimate is now measured rather than
projected.

---

## 9. Verdict

- The random-matrix / maximum-entropy framework of Xiao, Wang & Ghanem (2016)
  is **implemented, verified against the paper's own properties, and
  propagated** on the case its own §9.5 recommended. The infrastructure that
  §9.1 listed as "none of items 1–4 exist in this project today" now exists.
- The probabilistic band on reattachment **contains the LES truth** but is
  **5.0× wider than the eigenspace corner union** at the paper's δ = 0.2 and
  **7.1× wider** at its δ = 0.6. It is not tighter at either of the paper's own
  settings. That is a negative answer to the question this thread was opened to
  ask, and it is recorded as one.
- The band's own **convergence-gating bias is measurable and points the wrong
  way** — the members closest to the truth are the ones a residual gate would
  discard. This confirms, quantitatively, a risk that was written down before
  the work started. At δ = 0.6 it is worse than a bias: gating to the 5 of 40
  members that meet the residual gate **loses containment of the LES range
  entirely**, while the unfiltered ensemble keeps it.
- **A sign error in F6a's eigenvalue-perturbation source term was found,
  demonstrated four independent ways, and quantified on F6a's own mesh.** It
  does not overturn F6a's headline conclusion that the corners are unreachable
  within budget; it does invalidate F6a's channel-3 numbers, its reduced
  envelope, and its explanation of why the corners fail.

---

## 10. Evidence record

| what | where |
| --- | --- |
| Paper, full text | `docs/papers/xiao_wang_ghanem_1603.09656.pdf` / `.txt` |
| Sampler + verification | `demo-output/website/dafoam/f6d_random_matrix_uq/rmt_sampler.py`, `verify_sampler.py`, `verify_sampler_result.json` |
| Sign-convention experiment | `.../f6d_random_matrix_uq/signcheck/{ref_nu1,ref_nu3,src_minus,src_plus}/log.simpleFoam` |
| Sign A/B on F6b | `.../f6d_random_matrix_uq/signdemo/{f6asign_threeC,corrected_threeC}/log.simpleFoam` |
| Realizability audit | `.../f6d_random_matrix_uq/realizability_of_flipped_corner.{py,json}` |
| F6a hump recheck | `.../f6d_random_matrix_uq/f6a_recheck/corrected_{oneC,twoC,threeC}/{log.simpleFoam,gate_result_3800.json}` |
| F6a's original 1C log (limiter evidence) | `demo-output/website/solve_registry/uq_oneC_20260729T023701Z.log` |
| F6b baseline solve | `demo-output/website/solve_registry/f6b_gate_20260729T035745Z.log` |
| Ensemble members | `.../f6d_random_matrix_uq/ens/d0.2_s000…s039`, `d0.6_s000…s039`, `corner_{oneC,twoC,threeC}`, `null` (manifests: `ens/manifest_{rmt,corners,null}.json`) |
| Aggregated band, both δ | `.../f6d_random_matrix_uq/aggregate_result.json` (regenerate with `python3 aggregate.py > aggregate_result.json`) |
| Barycentric reach | `.../f6d_random_matrix_uq/barycentric_reach.json` |
| Measured cost | `.../f6d_random_matrix_uq/cost.json` |
| Figure | `.../f6d_random_matrix_uq/F6d_band.png` |


---

## Paper-library forwarding note — appended 2026-08-18

**Nothing above this line was edited.** The `docs/papers/` paths cited above were
correct when the sentences carrying them were written. Commit `5c0d2483`
(2026-08-18) refiled the paper library into topic subdirectories and renamed most
of its files, and `4323d7e3` lowercased two of the new names afterwards. Those
citations were left exactly as they stood, because each records where a file was
at the moment its statement was made; rewriting one would have changed what this
record says happened.

Each pair below was resolved by **git blob identity** — the old path's blob hash
matched to the path carrying the identical hash — and not by name similarity, and
each destination was then confirmed against the filesystem at commit `4323d7e3`.

| as cited above | the same bytes, as of `4323d7e3` |
| --- | --- |
| `docs/papers/xiao_wang_ghanem_1603.09656.pdf` | `docs/papers/uncertainty_quantification/xiao_wang_ghanem_1603.09656.pdf` |
| `docs/papers/xiao_wang_ghanem_1603.09656.txt` | `docs/papers/uncertainty_quantification/xiao_wang_ghanem_1603.09656.txt` |

The whole 87-path table was appended to `docs/papers/README.md` in the same
commit. `python3 scripts/check_paper_citations.py` re-derives the rows above and
exits non-zero if any destination stops resolving.
