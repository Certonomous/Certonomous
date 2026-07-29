# D9 — prediction, written before any new compute (P2)

Date: 2026-07-29. Written before launching channel 1 (RANS inter-model sweep
on the hump) or channel 3 (eigenvalue-perturbation UQ) runs. This file is not
edited after results come in; the results file references it and states
agreement/disagreement honestly.

**Target:** does a defensible model-form-uncertainty band on NASA-hump
reattachment `x/c` CONTAIN the measured +13.95% over-prediction
(ours 1.2534 vs NASA experiment 1.100)?

## Per-channel prediction

- **Channel 1 (inter-model spread, linear EVMs on the hump: SA, kEpsilon,
  kOmega, realizableKE vs. kOmegaSST baseline).** Predict this spread will be
  NARROW and will NOT by itself span down to the experimental value. Reason:
  F6c already showed all five linear (Boussinesq) models tested agree to the
  bit on a structural question (secondary flow); the hump's bubble-length
  over-prediction is understood in the literature as a shared property of
  the whole linear-eddy-viscosity class (excess turbulent shear stress in
  reattaching shear layers), not a coefficient difference between SA/SST/kε.
  Expect all four new models to also over-predict reattachment, landing
  within roughly the same neighborhood as kOmegaSST's +13.95%, not below it.
  **Prediction: channel 1 alone under-covers.**

- **Channel 2 (documented SST bias from literature).** Expect the literature
  to describe the *direction* (over-prediction of separated-shear-layer
  reattachment length by linear EVMs) robustly and consistently, but I do
  not yet know whether a precise citable *quantification* (a percentage)
  exists for this specific case family. Will report tier honestly; if no
  citable number is found, channel 2 contributes qualitative support only
  and the band leans on channels 1 and 3.

- **Channel 3 (eigenvalue perturbation, Emory/Iaccarino, full corner
  projection Δ=1, eigenvectors fixed, live/coupled propagation through the
  SIMPLE loop from the converged baseline field).** Predict this is the
  widest channel. The 1C (one-component / minimum turbulent mixing) corner
  is expected to suppress the effective turbulent shear stress in the
  reattaching shear layer relative to the Boussinesq baseline, which should
  *elongate* the separation bubble further (reattachment `x/c` pushed
  higher, deeper into or past the already-measured +13.95% miss). The 2C
  corner is expected to do the opposite (shorter bubble, reattachment `x/c`
  pulled down, likely below the baseline's 1.2534, possibly toward or past
  the experimental 1.100). The isotropic/3C corner is expected to sit
  between the two, closest to baseline since kOmegaSST's own predicted
  anisotropy is not maximally anisotropic everywhere.

## Combined prediction

**I predict the combined band (min/max across the three channels) DOES
contain the +13.95% measured miss**, primarily on the strength of channel
3's 1C corner, which I expect to land at or beyond +13.95%, with the 2C
corner supplying the lower bound. If channel 3 turns out not to be
tractable in the time available, or if the corner runs land inside a
narrower range than predicted, I expect the honest result to flip to
DOES-NOT-CONTAIN, and I will report that as a measured UQ gap, not adjust
the method to force containment.

This prediction is falsifiable and stated before any of the three channels'
new numbers exist.
