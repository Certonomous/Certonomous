# D5 — Reynolds-stress models on the square duct: RESULT

Companion to `D5_RSM_PREDICTION.md`, which was committed as `45c0103` **before
any RSM run executed**. The prediction is scored below without editing it.

Case: AR_1_Ret_360, 3,025 cells, reusing the converged baseline mesh from
`ladder-b/duct_baseline/`. U_bulk 33.0777 m/s. DNS secondary-flow RMS 0.7344 m/s
= 2.2201% of U_bulk.

---

## Measured

| model | class | secondary flow (% U_bulk) | % of DNS | converged at |
| --- | --- | --- | --- | --- |
| **DNS reference** | — | **2.2201%** | 100% | — |
| kOmegaSST | linear | 6.09e-16% | **0%** | baseline |
| SpalartAllmaras | linear | ~6.6e-16% | 0% | prior sweep |
| kEpsilon | linear | ~5.5e-16% | 0% | prior sweep |
| realizableKE | linear | ~9.2e-16% | 0% | prior sweep |
| kOmega | linear | ~7.9e-16% | 0% | prior sweep |
| LienCubicKE | nonlinear | 0.1740% | 7.84% | prior sweep |
| **SSG** | **RSM** | **1.2213%** | **55.01%** | iter 118,424 |
| **LRR** | **RSM** | **4.5948%** | **206.96%** | iter 141,982 |
| EBRSM | RSM | — | — | see convergence note |

---

## Scoring the prediction — two of four right

**1. "All three RSMs will produce clearly nonzero secondary flow." — CORRECT for
the two that converged.** SSG and LRR both produce signals ten to fourteen orders
of magnitude above the linear models. The mechanism is genuinely fixable by
leaving the linear eddy-viscosity family, exactly as the physics argued.

**2. "Magnitude 30–80% of DNS, not 100%." — HALF RIGHT, AND WRONG IN AN
INTERESTING WAY.** SSG landed at 55.01%, squarely inside the predicted band.
**LRR over-predicts at 206.96% — more than double DNS.** I framed the expected
failure mode as under-prediction and never considered overshoot. That was a
failure of imagination, not of arithmetic: I reasoned from "RSMs capture the
structure but weakly" without asking whether any of them could overshoot.

**3. "Ordering EBRSM ≥ SSG ≥ LRR." — WRONG, or at least meaningless as stated.**
LRR, the oldest and simplest of the three, produces the *largest* signal. But
"largest" is no longer the same as "best" once a model overshoots, so the
ordering I predicted was framed on an assumption that collapsed. Ranked by
**accuracy** rather than magnitude, SSG (−45% error) beats LRR (+107% error).

**4. "At least one RSM will need relaxation tuning or fail outright." —
CORRECT.** EBRSM required four separate setup corrections and then hit a
floating-point exception at iteration 300 in the matrix solve. It is rerunning at
relaxation 0.3.

---

## What this settles, and what it does not

**Settled: RANS is not structurally incapable here.** The open question from the
six-model sweep was whether *any* RANS closure could reach DNS magnitude. SSG and
LRR **bracket** the DNS value — one below, one well above. That is a materially
different situation from "everything falls short", and it means an RSM-based
entry is a live option for the duct cases rather than a dead end.

**Not settled: which RSM is right.** A 55% under-prediction and a 207%
over-prediction are both wrong. The spread between two respectable RSMs on the
same mesh and the same case is itself a model-form uncertainty result, and a
useful one — it is precisely the kind of inter-closure spread that a
model-form UQ band should be built from.

**Standing caveat, unchanged.** Even a perfect secondary flow closes **at most
~24%** of our duct error; at least 76% is streamwise-profile error (the bound in
`closure_challenge_C2_error_decomposition.md`). This answers a *mechanism*
question about the closure family. It is not the fix for the 62.9% duct deficit
and must not be sold as one.

---

## Setup findings worth carrying

Four EBRSM launches failed before it ran, each caught by `launch_solve.sh`'s
missing-artifact flag rather than reading as success:

1. no solver entry for `epsilon` in `fvSolution`
2. `0/f` missing (elliptic blending function, EBRSM-specific)
3. no solver entry for `f` — **a field in `0/` is not enough; transported fields
   need solver entries**
4. `DILU` on `f` — `f` is a *symmetric* equation and DILU is an asymmetric
   preconditioner; it needs PCG/DIC while `R` and `epsilon` keep PBiCGStab/DILU

Causes 1 and 3 are now **preflight check 2b**, generalised: every field the
selected model transports must have a solver entry covering it.

**A fifth finding, which cost the most:** `residualControl` in this case lists
only `k` and `omega` — fields an RSM does not transport. **The stop criterion can
therefore never be satisfied**, so both runs ground on toward `endTime` 500,000
while already converged (LRR's Ux initial residual was 1.6e-12 by iteration
120,000). They were stopped gracefully with `stopAt writeNow`, which preserved
the converged fields instead of discarding roughly two hours of compute. Any
RSM run on a case configured for an eddy-viscosity model inherits this.
