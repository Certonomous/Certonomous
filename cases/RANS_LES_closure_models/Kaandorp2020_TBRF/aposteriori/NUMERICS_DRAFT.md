# Numerics drafts — Kaandorp2020_TBRF lane

For `docs/NUMERICS_KNOWLEDGE.md`. Every number measured on this machine in this
run; nothing recalled. **Section A was previously drafted in the scratchpad as
`numerics_B.md` and the scratchpad has since been cleared — rewritten here from
context; drop it if already appended.** Section B is new.

---

# SECTION A — a-priori TBRF reproduction (`../RESULTS.md`)

## N-K1. The Pope tensor basis is rank 3 to 4 on every flow in this benchmark, and that is where a tensor-basis model's extrapolation error comes from

Pope's integrity basis has 10 tensors, so a tensor-basis model fits 10
coefficients `g^(m)`. **The 10 flattened basis tensors do not span 10
dimensions on real data.** Mean numerical rank of the 9x10 matrix
`[T^(1) ... T^(10)]` at a cell (tol `1e-8 max|T|`, 500-cell sample):

| case | mean rank |
|---|---|
| `AR_1_Ret_360` (square duct) | **3.089** |
| `AR_1_Ret_180` (square duct) | 3.09 |
| `CBFS13700` (curved step) | 3.988 |
| periodic hills | 3.82 - 3.98 |

A sibling reproduction with different code and a different split measured 3.24
over its own pool: independent agreement.

Consequences, both measured. (1) Six of ten coefficients are unconstrained, and
Kaandorp's `Gamma` = 1e-12 does nothing against normal-equation entries of order
1e4: over all leaves of a 100-tree forest, `median |g|` = 2.6e-5,
`p99 |g|` = 3.4e4, `max |g|` = 4.0e6. (2) They then multiply basis tensors three
decades outside their training range — `||T^(7)||_F` p99 is **1.02e6** in the
training pool and **1.74e9** on the duct.

**Rule.** Any model `b = sum_m g^(m)(features) T^(m)` must report the numerical
rank of `T` on the *prediction* case, or truncate the basis to that rank, or
regularise at a magnitude meaningful relative to `sum T^T T`. `Gamma` = 1e-12
against `1e4` is `Gamma` = 0.

## N-K2. An RMS on a closure prediction hides the failure mode; report the distribution

On `CBFS13700` the 16-feature TBRF's error field: median **0.170**, p90 **3.40**,
p99 **153.9**, RMS **47.68** — against an SST `b_rms` of 0.319. The median cell
beats the industrial closure; the RMS is 156x worse. The tail is **15.0 % of
cells** violating `||b||_F <= sqrt(2/3) = 0.8165`, which no realisable Reynolds
stress can violate. Rescaling only those cells onto the bound takes the RMS to
**0.567** (and 6.38 to **0.411** on the held-out duct). Report median, p90, p99
and the over-bound fraction beside any anisotropy RMS.

**Median-over-trees is worth four orders of magnitude.** Same forests, mean over
trees instead of Kaandorp's median: `AR_1_Ret_360` **67,860** vs 6.382,
`CBFS13700` **256** vs 47.68. Their sec. 2.5 aggregation choice is not stylistic.

## N-K3. Durbin's time-scale bound is not Reynolds-similar and must not be applied across cases of different physical scale

`T = max(k/eps, 6 sqrt(nu/eps))`. For the tensor-basis normalisation
`S_hat = T S` that bound is not a small correction:

| case | fraction of cells where the Durbin branch is active | `k/eps` p99 | `T` used, p99 |
|---|---|---|---|
| `PHLL10595` | 8.85 % | 16.5 | 16.5 |
| `alpha_15_13929_4048` | 11.3 % | 31.7 | 31.7 |
| `CBFS13700` | **45.97 %** | 170.4 | **4045** (24x) |
| `AR_1_Ret_360` | **71.77 %** | 2.27e-4 | max 0.559 (**2500x**) |

`k/eps = 1/(0.09 omega)` is Reynolds-similar; `6 sqrt(nu/eps)` carries `nu`
explicitly and is not. The hills are non-dimensional (`H` = 1,
`nu` = 1.786e-4), the ducts are meshed in millimetres (`h` = 1 mm,
`nu` = 1.5e-5). Removing the bound moved the held-out duct from
`b_rms_F` **6.382 ± 2.110** to **0.3160 ± 0.0080**, and the feature-space
Mahalanobis p95 from **36.00** to **6.20** against a training p95 of 6.59.

## N-K4. Storing an anisotropy tensor as float32 fabricates realisability violations

`b_LES` on `CBFS13700` has **4.60 % of cells sitting exactly on an edge of the
barycentric triangle** in float64 (min coordinate exactly 0.0). A float32
round-trip moves them to **-2.98e-8**, and a zero-tolerance Schumann test then
reports 4.60 % of the *reference LES data* as unrealisable. Use `tol >= 1e-7`.

## N-K5. Wall distance from `polyMesh` wall patches: exact in the median, 0.5 % in L2

Distance from each cell centre to the nearest face centre **or vertex** of a
`type wall` patch, checked against the `walldist` OpenFOAM wrote on the 29 hills:
median cellwise relative error **2e-15 to 1e-14**, relative L2 **0.055-0.47 %**,
worst absolute 0.004-0.049 `H`.

## N-K6. Cost of an exact tensor-basis decision tree

100 TBDTs on 21,000 samples x 16 features, 10x10 least squares at every candidate
split: **85 s wall on 16 cores** (~0.38 core-hours per forest), 1817 leaves per
tree; fully grown (`min_leaf` = 1) 127 s and 13,201 leaves. Accumulating
`A_i = That_i^T That_i` and `c_i = That_i^T bhat_i` once per sample and taking a
cumulative sum over the feature-sorted order makes an **exact brute-force**
threshold search cheaper than the paper's Brent 1-D search, and removes their
150-sample fallback entirely.

---

# SECTION B — a-posteriori injection lane (`RESULTS.md` in this directory)

## N-K7. `kOmegaSSTCorrected` with zero corrections is bit-identical to stock `kOmegaSST`

Registered gate G0a: run stock `kOmegaSST` and `kOmegaSSTCorrected` with
`bijDelta = 0`, `kDeficit = 0`, `bScale = RScale = 1` from the same shipped start
for the same 200 iterations. Measured relative L2 difference in `U`:
**0.0 exactly** (`AR_1_Ret_360`, 3025 cells, 3.9 s vs 4.0 s). The gate was
registered at 1e-10; the answer is round-off-free.

**Do not phrase this gate as "re-solve to convergence and compare to the shipped
field".** The shipped benchmark fields are not converged to 1e-10 — restarting
the converged `AR_1_Ret_360` solution gives an initial `Ux` residual of
**1.8e-5** — so any further iteration moves `U` by far more than 1e-10 for
reasons unrelated to the correction terms, and that form of the gate fails on a
correct solver. Compare two solvers over an identical trajectory instead.

## N-K8. Injecting `b^Delta` without `R` collapses `k`, and inverts the propagation ceiling

Registered choice: `kDeficit` (R) = 0, because the TBRF predicts `b` only.
Measured consequence on `AR_1_Ret_360`, mean `k`:

| configuration | mean `k` | mean `nu_t` | `U_rms` |
|---|---|---|---|
| LES truth | **43.42** | — | 0 |
| shipped k-omega SST | 26.68 | 6.65e-5 | 0.1985 |
| zero-correction control (30,000 it) | 26.71 | 6.65e-5 | 0.19874 |
| **truth `b`, R = 0** | **8.74** | 2.88e-5 | **0.3215** |
| train-mean `b`, R = 0 | **0.128** | **4.03e+7** | 0.6826 |
| TBRF `b`, R = 0 (seed 0) | 5.25 | 1.96e-5 | 0.2594 |
| **truth `b` AND `R`** (frozen extraction) | — | — | **0.00341** |

Injecting `b^Delta` changes k-production by `Gextra = -2 k (b^Delta : grad U)`,
strongly negative here. With no `R` to balance it `k` collapses, `nu_t` follows,
and the momentum correction `2 k b^Delta` shrinks toward zero simultaneously —
so the "true anisotropy" injection ends up **62 % worse than the baseline it was
meant to bound**. With `R` extracted by `kCorrectiveFrozenFoam` and propagated
alongside, the same case gives `U_rms` = **0.00341**, a **98.3 % reduction**.

`b^Delta` and `R` are not two independent corrections you can take one of. A
`b`-only learned closure that is propagated needs its own k-equation treatment
(Kaandorp's "modified k-equation") or it will be graded against a ceiling that is
below its own baseline.

## N-K9. A residual-based convergence criterion fails on a periodic duct driven by a source term

`AR_1_Ret_360` is streamwise-periodic with a `meanVelocityForce`. After **30,000
iterations** of the zero-correction control the initial residuals are:

| field | initial residual at iteration 30,000 |
|---|---|
| `p` | **0.144** |
| `Ux` | **8.4e-16** |
| RMS `div(U)` / gradient scale | **6.1e-18** |

The field has not moved (`U_rms` 0.19874 against the published SST 0.1985) and
`p` is *converged*: the cross-plane pressure is nearly uniform, so OpenFOAM's
residual normaliser divides by a near-zero scale. Two related traps in the same
case: the baseline has `Uy, Uz ~ 0`, so their initial residuals are **O(0.3) at
restart with zero corrections**; and a solver that stops at first satisfaction of
`residualControl` can never exhibit a criterion phrased as "sustained for 100
iterations".

Use field movement between checkpoints as the primary convergence measure for any
flow whose driving pressure gradient is a source term rather than a boundary
condition, and read the zero-correction control's residuals before registering a
criterion.

## N-K10. Continuity, re-solved, against this lab's own published post-hoc figure

Volume-weighted RMS `div(U)` normalised by the field's own gradient scale:

| configuration (`AR_1_Ret_360`) | RMS `div(U)` / gradient scale |
|---|---|
| zero-correction control | **6.1e-18** |
| train-mean `b` injection | 4.0e-5 |
| truth `b` injection | 1.1e-4 |
| truth `b` **and** `R` | 1.7e-4 |
| TBRF `b` injection (3 seeds) | 3.1e-4 to 3.8e-4 |
| **lab's published post-hoc correction** (`METHOD.md` §6.2) | **10.5 %** and **9.7 %** |

Re-solving buys between **2.5e4x** and **1.7e16x** on continuity. Charter §22.2's
"continuity by construction" is not a figure of speech; it is five to sixteen
orders of magnitude, and the cheapest way to earn it is to put the correction
inside the equations rather than on top of the answer.
