# PREREGISTRATION - Schmelzer, Dwight & Cinnella (2020), SpaRTA

Written **before** any fitting. Amendments go in `RESULTS.md`.

Date written: 2026-08-20. **Status at time of writing: PENDING** - the
preregistration is complete and the data are in place; the fit and the
a-posteriori solves have not been run.

## 1. The paper and its numbers

**Source status: VERIFIED-PDF.** `docs/papers/closure/Schmelzer2020_algebraic_reynolds.pdf`,
printed title page: *Discovery of Algebraic Reynolds-Stress Models Using Sparse
Symbolic Regression*, Martin Schmelzer, Richard P. Dwight, Paola Cinnella,
arXiv:1905.07510v2, 28 Feb 2020; published Flow Turbulence Combustion 104:579-603.

Both of their headline tables are normalised by the k-omega SST baseline error,
which makes them **directly comparable to `BASELINES.md`** - the only paper in
the charter list with that property.

**Table 1, preprint p. 5** - the *frozen-field upper bound*: with the corrective
fields `b^Delta_ij` and `R` injected as static fields into a modified solver,

| Case | `eps(U)/eps(U_0)` | `eps(tau)/eps(tau_0)` |
|---|---|---|
| PH10595 | **0.00165** | 0.1495 |
| CD12600 | 0.0229 | 0.4781 |
| CBFS13700 | **0.22703** | 0.4949 |

**Table 2, preprint p. 14** - the *discovered sparse models*, re-solved:

| Model | PH10595 | CD12600 | CBFS13700 |
|---|---|---|---|
| M(1) | **0.22287** | 0.21146 | **0.30413** |
| M(2) | 0.38867 | 0.20828 | 0.40154 |
| M(3) | 0.22744 | 0.22422 | 0.30655 |

Also, abstract: "The predictions of the discovered models are significantly
improved over the k-omega SST also for a true prediction of the flow over
periodic hills at Re=37000."

**Their method:** `k`-corrective-frozen-RANS to build `b^Delta_ij` and `R` from
high-fidelity data without an adjoint ("requires full-field data, but is not
based on an inversion procedure ... which makes it very cost-efficient", p. 5),
then elastic-net sparse regression over a library of tensor-polynomial candidate
functions, then an ensemble of hand-selected models (5 for `b^Delta`, 3 for `R`,
1 for CBFS13700, p. 14).

## 2. Which of their numbers we can and cannot target

* **PH10595 and CBFS13700 are literally the same cases in our benchmark**
  (`PHLL10595`, `CBFS13700`; `BASELINES.md` sec. 6.1). Their normalised errors on
  those two cases are **genuine targets**, not analogues. This is the only
  reproduction in the charter list where that is true.
* **CD12600 is not on this machine** (converging-diverging channel, Laval &
  Marquillie). Its column is recorded above so it is never confused with ours.
* **PH37000 is not on this machine**; the "true prediction" claim cannot be
  tested here.
* Their normalisation `eps(U_0)` is the k-omega SST error, which we have per case
  in `sst_baseline_metrics.json`. **Our `eps(U_0)` will not be numerically
  identical to theirs**, because their SST solve is their own and ours is the one
  the benchmark ships (and the benchmark's SST uses the strain-rate rather than
  the vorticity magnitude in the `a1` limiter - see
  `docs/closure/FOUNDATIONAL_MODELS_INVENTORY.md` sec. 5.1). Ratios are compared,
  never absolute errors.

## 3. Staged plan, with a gate between stages

**Stage A - `k`-corrective-frozen-RANS (a-priori).** Their equations, quoted so
the implementation can be checked against them [VERIFIED-PDF: Schmelzer et al.
2020, eqs. (3)-(6), preprint p. 5]:

```
b_ij      = -(nu_t/k) S_ij + b^Delta_ij                                     (3)

d_t k     + U_j d_j k = P_k + R - beta* omega k + d_j[(nu + sigma_k nu_t) d_j k]      (4)

d_t omega + U_j d_j omega = (gamma/nu_t)(P_k + R) - beta omega^2
                            + d_j[(nu + sigma_omega nu_t) d_j omega] + CD_komega      (5)

P_k  = 2 k ( b^o_ij + b^Delta_ij ) d_j U_i ,     nu_t = a1 k / max(a1 omega, S F2)
```

The procedure: **freeze** `U_i`, `k` and `b_ij` at their high-fidelity values,
solve **only** the `omega` equation (5) iteratively to convergence, take `nu_t`
from the converged `omega`, obtain `b^Delta_ij` from (3), and read `R` off as the
residual of the `k` equation (4). In their words, "only one equation is solved
iteratively while the remaining variables are frozen" (p. 5). No adjoint and no
optimisation loop are involved - the method's chief practical virtue.

**Gate A:** with `b^Delta_ij` and `R` injected as static fields and the flow
re-solved, the velocity error must fall below **0.05** of the k-omega SST
baseline on PH10595. Their Table 1 gives **0.00165**; anything above 0.05 means
our frozen-field construction is wrong, and Stage B must not start.

**Data availability note, checked before writing this:** the 29 parametric hills
ship `gradU`, `Pk`, `Pk_bouss`, `Dk`, `k_conv`, `k_diff`, `tauij_B` and
`walldist`, which is everything (4) and (5) need. **`PHLL10595` and `CBFS13700`
ship none of those** - only `U k omega nut p` plus the truth fields - so on the
two cases that matter every gradient and every budget term must be reconstructed,
with `of_read.structured_gradient()` (validated to 0.47-0.96% interior relative
L2 against OpenFOAM's own `gradU` on the hills, `BASELINES.md` sec. 1) and with a
wall distance that the benchmark does not ship for those two cases and that must
be computed from the mesh. **That reconstruction, not the regression, is the
risky part of this reproduction**, and Gate A exists to catch it.

**Stage B - sparse regression.** Elastic net over a library of tensor-polynomial
candidates built from `T^(1..10)` and the five invariants, with the same
`(alpha, lambda)` sweep structure. Report the discovered model forms verbatim -
the point of the method is that the model is readable.

**Stage C - a-posteriori.** Inject the discovered `b^Delta` and `R` into
`simpleFoam` (OpenFOAM v2606, installed and verified working on this machine) and
re-solve. **This is the only stage that produces a number comparable to their
Table 2**, and it is the only stage that can fail in the way that matters
(divergence, or an improved `b` that makes `U` worse).

## 4. Acceptance band, declared now

* **PASS**: Stage C normalised velocity error `eps(U)/eps(U_0)` **below 0.5** on
  PH10595 **and** below 0.6 on CBFS13700, from a converged re-solve, with the
  discovered model written out in closed form.
* **GATE REACHED**: Stage A passes (frozen fields verified) and Stage B produces
  sparse models with lower a-priori error than SST, but Stage C does not converge
  or does not reach the band.
* **GATE FAIL**: Stage C converges but the normalised error is above 1.0 - i.e.
  the discovered model is **worse than doing nothing**, which is the specific
  failure the ill-conditioning literature predicts
  (`Wu2018_rans_explicit_closure_ill_conditioned.pdf`, VERIFIED-PDF on disk).
* **NOT A RESULT**: Stage A fails Gate A.
* **BLOCKED**: if the modified solver cannot be built.

The band is deliberately looser than their 0.223 / 0.304, because our SST
baseline, mesh handling and frozen-field construction differ; a value between
0.5 and their 0.22 would be reported as a partial reproduction with the gap
stated, not rounded into a PASS.

## 5. Split

`PHLL10595` and `CBFS13700` are both **training** cases in the benchmark split
(`BASELINES.md` sec. 6.2), and Schmelzer et al.'s own protocol is
model-discovery-plus-cross-validation on the same three separating flows. There
is therefore **no held-out test case in this reproduction as designed**, and that
is stated as a limitation rather than hidden: a model fitted and evaluated on
PH10595 is an interpolation result. The cross-validation variant - fit on
CBFS13700, predict PH10595 and vice versa - **will** be run and reported
alongside, and is the only part of this reproduction that tests generalisation.
`assert_disjoint()` is applied to the cross-validation variant.

## 6. Seeds and checks

The elastic net is deterministic given `(alpha, lambda)`; the seed controls only
the cross-validation folds. Three fold-seeds. Reported regardless of outcome:
realisability of the corrected `b` beside the truth's own violation rate;
Mahalanobis distance of the evaluation cells from the fitted cells; **continuity
residual of the re-solved velocity field** (Stage C produces a velocity field, so
this check *is* applicable here, unlike the three sibling reproductions); and an
explicit statement of solver, scheme and convergence criterion.

## 7. Compute

Stage A < 0.2 core-hours. Stage B < 1. Stage C: ~0.3 core-hours per case per
model; an ensemble of 5 models on 2 cases is ~3 core-hours. Total well under 10.
