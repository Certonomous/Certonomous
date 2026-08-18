# F6a — the k-SST diffusion hypothesis: pre-registration

**Written and committed BEFORE any run in this study executed.** Scored later
against this text, unedited, per this project's standing practice
(`PREDICTION.md`, `D5_RSM_PREDICTION.md`, `F12_PREREGISTRATION.md` precedents).

Date: 2026-08-01. Agent: F6a follow-up (Katie's roadmap item on F6a).

## The hypothesis, verbatim from the roadmap

> "Pass with an *. Overpredicted bubble length. Could k-SST diffusion. Must
> 1. Try different models 2. If confirmed this becomes a good case to show
> for epistemic uncertainty."

## Operationalization

kOmegaSST over-predicts the NASA wall-mounted-hump reattachment (1.2534 vs
experiment 1.100, +13.95%, gate-met — `F6a_epistemic_band.md`). The
hypothesis **H** as tested here: *the level of turbulent momentum transport
(effective diffusivity → turbulent shear stress) that the closure sustains in
the separated shear layer is what sets the predicted bubble length; SST's
shear-stress limiter suppresses that transport, and that suppression is the
dominant cause of its over-prediction.*

The mechanism named: OpenFOAM v2606 SST computes
`nut = a1*k / max(a1*omega, b1*F23*|S|)`
(`src/TurbulenceModels/turbulenceModels/Base/kOmegaSST/kOmegaSSTBase.C:123`,
`a1 = 0.31`, `b1 = 1.0` defaults). In a separated shear layer, where
production far exceeds dissipation, the second argument governs and caps the
eddy viscosity — exactly the "k-SST diffusion" lever Katie's note points at.

## Two pre-registered tests, falsifiers stated before running

### T1 — the limiter coefficient as a causal probe (a SENSITIVITY STUDY, disclosed as such)

Three runs of stock kOmegaSST on the identical 51,626-cell hump mesh, schemes,
BCs, and gates as every channel-1 model:

| run | a1 | role |
| --- | --- | --- |
| control | 0.31 (default) | template-validity gate: must reproduce the recorded baseline 1.2534 within ±0.005 in reattachment x/c, else the template is fixed before anything else runs |
| low | 0.25 | limiter stronger → less shear-layer nut |
| high | 0.40 | limiter weaker → more shear-layer nut |

The ±~30% bracket around 0.31 is a plain sensitivity bracket chosen for
mechanism visibility. **No a1 value will be promoted as an improved or
recommended model, and no a1 will be chosen because of where its answer lands
relative to 1.100.** This is a probe of the limiter mechanism, not tuning.
betaStar is deliberately NOT swept: it recalibrates the log-law/near-wall
balance globally, which would confound wall physics with the shear-layer
diffusion question H actually poses; a1 is the coefficient that names the
limiter directly.

**Prediction under H:** reattachment x/c is monotonically DECREASING in a1
(more permitted shear-layer eddy viscosity → faster shear-layer growth →
earlier reattachment), and the total swing
|x_r(a1=0.25) − x_r(a1=0.40)| > 0.01 in x/c — an order of magnitude above
both the measured numerical channel (separation moved 0.0002 under 4x
refinement) and observed convergence noise (~0.0005, kOmega t=8000 vs
t=22211).

**T1 falsifies H if:** the a1 trend is non-monotonic, or reattachment moves
the wrong way (longer bubble with larger a1), or the total swing is < 0.005.
Swing in [0.005, 0.01] with the right sign: inconclusive, reported as such.

### T2 — cross-closure correlation between shear-layer transport and bubble length

New closures added to the four-model channel-1 sweep, all stock OpenFOAM
v2606, same mesh/BCs/gates:

- **LRR** (Reynolds-stress transport, wall functions) — D5 precedent on the duct
- **SSG** (Reynolds-stress transport) — D5 precedent on the duct
- **EBRSM** (elliptic-blending RSM) — attempted; D5 showed it is the most
  fragile of the three; if it diverges on this mesh that is recorded with log
  evidence per L-22, not hidden

Excluded, with reasons stated now: **kOmegaSSTLM** (transition variant — the
hump validation case is fully turbulent by construction, inlet I = 0.077%;
a transition model introduces a laminar-separation confound and tests
transition, not diffusion); **GEKO** (its coefficients are explicitly
user-tunable with no canonical default physics claim — running it "at
defaults" would add a point whose diffusivity is a dial, not a closure).

**Metric, defined before extraction:** for every gate-met closure (the
existing kOmegaSST 1.2534, kOmega 1.0717, kEpsilon 1.1437, realizableKE
1.2503, plus SA 1.2061 carried with its documented residual-floor caveat,
plus every new model that settles), compute the turbulent shear stress
profile R_xz (u'w') on vertical lines at x/c = 0.8, 0.9 and 1.0 (inside the
separated region for every model — all separate at x/c 0.65–0.67). For
eddy-viscosity models R comes from `postProcess -func R` (R_xz =
−nut·2S_xz; valid for SA too since the k-dependent part of R is diagonal
only); for RSMs R is the transported field itself. The scalar per model:
**peak |R_xz| over the line, averaged over the three stations, normalized by
Uinf² (34.6253 m/s, from caseDef)**. Extraction runs happen in copies under
`/home/ubuntu/certonomous-runs/` — the published case directories are not
written to.

**Prediction under H:** across closures, reattachment x/c decreases with
peak shear-layer |R_xz|: Spearman rank correlation **rho ≤ −0.6** over the
closure set (a1 variants are T1's evidence and are excluded from the primary
T2 set; a secondary rho including them will be reported, labeled). In
particular H requires realizableKE — whose variable-Cmu formulation also
suppresses nut at high strain, and which lands within 0.3% of SST's
reattachment — to show a shear-layer stress level comparably low to SST's.
If realizableKE sustains HIGH shear-layer stress while still predicting the
long bubble, that alone breaks the mechanism H proposes.

**T2 falsifies H if:** rho > −0.3, or positive. rho in (−0.6, −0.3]:
inconclusive, reported as such.

### Interpretation matrix, committed now

| T1 | T2 | reading |
| --- | --- | --- |
| pass | pass | H survives; the model-form spread is a documented mechanism, and the epistemic-uncertainty case record (roadmap item 2) is written |
| pass | fail | limiter is causal within SST but does not set the cross-family spread; H as Katie stated it survives only in the narrow (within-SST) sense — reported exactly so |
| fail | pass | shear-layer transport correlates across families but SST's own limiter is not the operative lever; H's mechanism is wrong even if its family-level intuition is right |
| fail | fail | H falsified; the epistemic case, if written at all, must not claim a diffusion mechanism |

## Settle standard, committed now

Every new run uses the same `residualControl` gates as its channel-1
template ((U|p|k|epsilon-or-omega-or-R) at 5e-7 on **Initial** residuals,
omega at 1e-10 where transported), is checked with
`scripts/check_convergence.py` (the L-14 Final-vs-Initial trap is the
checker's whole reason to exist), and is extended — never cap-accepted — 
until it either prints `SIMPLE solution converged`, exhibits a documented
residual floor with a QoI stable to <0.3% across ≥2000 iterations (the SA
precedent, reported as gate-NOT-met), or diverges (recorded as a failure
with its log, L-22). Separation and reattachment are read only by Cf sign
change via the same `hump_gate_analysis.py` used by every rung of the act.
RSM cases get `residualControl` naming the fields the model actually
transports (the D5 trap, now preflight check 2b) and are initialized from
kEpsilon's converged t=2000 field per the documented multi-stage restart
precedent (realizableKE, `F6a_epistemic_band.md`) — a numerics choice
carrying no information about the experimental target.

## What this study will NOT do

- No coefficient will be tuned to 1.100, and no run will be re-launched,
  re-relaxed, or re-meshed *because of the answer it produced* (numerics
  fixes for divergence are permitted and documented, per the kEpsilon /
  realizableKE precedents).
- Nothing from the withdrawn eigenvalue-perturbation corner runs (L-26 sign
  error) is built upon or cited as evidence here.
- Nothing here revises `D9_TALKING_POINTS.md` numbers; the closest-single-
  check remains kEpsilon 1.1437 (+3.97%) unless a new model both settles and
  lands closer, in which case that is reported to the supervisor rather than
  silently edited into the filmed narrative.
