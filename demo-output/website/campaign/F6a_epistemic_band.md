# D9 / F6a — model-form uncertainty band on the NASA wall-mounted hump

**Harvested by the supervisor** from the D9 agent's completed runs after it was
interrupted four times (three host restarts, one API failure) without landing a
record. The prediction file `f6a_epistemic_band/PREDICTION.md` was written by the
agent **before any of these runs executed** and is scored below unedited.

## The binary test

> Does a defensible model-form uncertainty band on hump reattachment `x/c`
> **contain** the measured +13.95% over-prediction?

**Answer: YES — but the band is very wide, and where the width comes from
matters more than the pass.**

## Measured

| channel | model / corner | separation x/c | reattachment x/c | vs experiment |
| --- | --- | --- | --- | --- |
| — | **NASA experiment** | 0.6650 | **1.1000** | — |
| — | kOmegaSST (our baseline) | 0.6544 | 1.2534 | **+13.95%** |
| C1 | SpalartAllmaras | 0.6544 | 1.2092 | +9.93% |
| C1 | kOmega | 0.6592 | 1.1299 | +2.71% |
| C3 | oneC (one-component limit) | 0.5250 | 0.5278 | **−52.02%** |
| C3 | twoC (two-component limit) | 0.6242 | 0.6701 | −39.08% |
| C3 | threeC (isotropic limit) | 0.6589 | 1.1069 | **+0.63%** |

**Band across all completed runs: [0.5278, 1.2534].** Experiment 1.100 lies
inside. **CONTAINS.**

## Reading it honestly — three things matter more than the verdict

### 1. Channel 1 alone does NOT contain the truth, exactly as predicted

Inter-model spread over the linear eddy-viscosity models spans **[1.1299,
1.2534]** — and the experimental 1.100 sits **below all of them**. Every linear
model over-predicts the bubble.

The agent's prediction said precisely this, before running: *"the hump's
bubble-length over-prediction is understood in the literature as a shared
property of the whole linear-eddy-viscosity class ... expect all four to land in
roughly the same neighborhood, not below it. **Prediction: channel 1 alone
under-covers.**"* **That prediction is CORRECT.**

This is the finding with the most teeth. **A band built from inter-model spread
alone would have failed**, and it would have failed for a structural reason:
sampling several members of one model class does not sample the error of the
class itself.

### 2. The containment is carried by the eigenvalue perturbation, and that is
the method behaving as designed

Channel 3 perturbs the Reynolds-stress anisotropy toward the limiting states of
the barycentric map. `oneC` and `twoC` are **extreme realizable limits** — they
are not predictions and are not meant to be. The Emory/Iaccarino construction
produces **bounds, not point corrections**, so a wide interval is the correct
output of that method rather than a defect in it.

So the band passing is a validation of the **machinery**, not evidence that our
uncertainty is tight.

### 3. The most interesting single number is `threeC` at +0.63%

The isotropic-limit perturbation lands at reattachment 1.1069 against the
experimental 1.100 — **0.63% away**. That is closer than any turbulence model
tested here, including plain kOmega at +2.71%. Worth investigating rather than
filing: it may be coincidence on one quantity, and it should be checked against
separation and the Cp distribution before anyone reads meaning into it.

## What this does and does not establish

**Establishes:** our three-channel machinery produces a band that contains a
known, published, independently-verified model-form error on a NASA case. The
product thesis survives its first real test.

**Does not establish:** that the band is useful. A span of **−52% to +14%** in
reattachment position is a factor of ~2.4. A band that wide would accept almost
any result, so containment here is necessary but far from sufficient. **The next
question is not "does it contain" but "how tight can it be made while still
containing".**

**Also does not establish anything about channel 2.** Documented SST bias from
the literature was not incorporated in these runs.

## Caveats carried

- **kOmega did not meet its residual gate** (k final ~2.8e-6 against a 5e-7 bar)
  and is therefore an unconverged number. It defines the lower edge of the
  channel-1 range, so that edge is soft.
- `kEpsilon` and `realizableKE` case directories exist but have no converged time
  directory — they did not complete, and no numbers are claimed for them.
- Separation is far better predicted than reattachment across every entry, which
  is consistent with the documented behaviour: these models get the onset roughly
  right and the recovery wrong.
