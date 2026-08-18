# D5 — Reynolds-stress models on the square duct: PREDICTION

**Written and committed BEFORE any RSM run executes (P2).** A confirmation only
counts if the prediction predates the data. If this prediction is wrong, that is
the finding and it stays on the record unedited.

## The question D5 closes

The six-model sweep established that **all five linear (Boussinesq) eddy-viscosity
models produce exactly zero** duct secondary flow — measured 5.5e-16 to 9.2e-16
percent of bulk, machine zero, agreeing essentially to the bit — while the one
nonlinear model (LienCubicKE) produced **0.174%**, some 1.9e14 times larger, but
only **7.84% of the DNS magnitude**.

So: *mechanism* fixable by leaving the linear family, *magnitude* not yet. The
open question is whether **any** RANS closure reaches the DNS magnitude, or
whether the duct secondary flow is beyond the entire RANS family. Either answer
is a result; the second is publishable.

## Reference (measured, from `secondary_flow_gate.json`)

| quantity | value |
| --- | --- |
| DNS secondary-flow RMS | 0.7344 m/s = **2.2201% of U_bulk** |
| kOmegaSST (linear) RMS | 2.01e-16 = **6.09e-16% of U_bulk** |
| U_bulk | 33.0777 m/s |
| cells | 3,025 |

## Prediction

**1. All three RSMs will produce clearly nonzero secondary flow.** LRR, SSG and
EBRSM solve transport equations for the individual Reynolds-stress components,
so normal-stress anisotropy exists **by construction** rather than being
identically zero. Secondary flow of the second kind is driven by gradients of
that anisotropy, so the mechanism is present. I expect all three to land orders
of magnitude above the linear models and above LienCubicKE's 0.174%.

**2. Magnitude: I predict 30–80% of DNS, not 100%.** Full RSMs are documented to
capture duct secondary flow qualitatively — the eight-vortex structure appears —
while commonly under-predicting its strength. I do not expect any of them to
reach 2.22%.

**3. Ordering: EBRSM ≥ SSG ≥ LRR.** EBRSM's elliptic blending is specifically a
near-wall treatment, and the anisotropy gradients that drive this flow live near
the wall and in the corner. SSG's pressure–strain model is more modern than
LRR's. So I expect the ordering to follow near-wall fidelity.

**4. Convergence risk is real and I expect at least one failure.** RSMs are
stiffer than eddy-viscosity models: seven transported equations, and the
pressure–strain terms are numerically delicate. The earlier sweep already saw
`realizableKE` and `LienCubicKE` each crash twice with floating-point exceptions
before converging with reduced relaxation. **I expect at least one of the three
RSMs to require relaxation tuning or to fail outright.** A model that will not
converge is a reportable result, not a reason to fiddle until it does.

## What each outcome means

| outcome | interpretation |
| --- | --- |
| An RSM reaches ~2.2% | RANS *can* do this; our closure work should target the model class, not post-hoc correction |
| All three land well short (say <50%) | The duct secondary flow is **beyond the practical RANS family**. That is the publishable finding, and it reframes the 62.9% duct deficit as partly irreducible for any linear-or-RSM entry |
| All three fail to converge | Inconclusive on magnitude, and a real statement about RSM robustness on this case |

## Standing caveat carried from the C2 bound

Even a perfect secondary flow would close **at most ~24%** of our duct error —
the earlier bound showed at least 76% is streamwise-profile error. So this study
answers a *mechanism* question about the closure family, not the whole deficit.
It should not be oversold as the fix for the ducts.
