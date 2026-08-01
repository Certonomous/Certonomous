# F6a — the epistemic-uncertainty case: campaign record

**Status: DRAFT — being written while the final T2 runs settle; every number
below already cites a settled log; rows marked [pending] are the only open
slots.**

Katie's roadmap note on F6a, verbatim: *"Pass with an \*. Overpredicted
bubble length. Could k-SST diffusion. Must 1. Try different models 2. If
confirmed this becomes a good case to show for epistemic uncertainty."*
Item 1 is executed and scored in `F6a_DIFFUSION_PREREGISTRATION.md` /
`F6a_DIFFUSION_RESULTS.md`. This document is item 2: the evidence record
that makes the NASA wall-mounted hump the campaign's demonstration case for
**bounding a documented model-form (epistemic) error**. The demo/act side
belongs to other agents; nothing here is a script.

## The shape of the case, in one paragraph

A NASA validation experiment gives reattachment x/c = 1.1000. Our
production-grade baseline (kOmegaSST, gate-met, 1772–1795 iterations,
independently re-checked) predicts 1.2534 — a +13.95% error that no amount
of iteration convergence or mesh refinement will remove, because it is not
a numerical error. Swapping only the turbulence closure — nothing else in
the case — moves the answer across a 0.18-wide interval that **straddles
the experiment**. The error is epistemic: it lives in the model equations,
it is documented in the literature independently of us, its mechanism now
has direct causal evidence from this project's own runs (the a1 probe), and
a multi-model ensemble brackets the truth that any single closure misses.
That is the textbook shape of model-form uncertainty, realized end-to-end
on 51,626 cells at ~17 s a solve.

## 1. The numerical channel is small — the error is not discretization

- **Iteration convergence:** every number in the band below meets the
  project gate (Initial residuals, `SIMPLE solution converged` printed;
  `scripts/check_convergence.py`), except the two entries explicitly
  starred. The baseline's own gate was independently re-verified
  (`F6a_epistemic_band.md`, 2026-07-29).
- **Grid:** under 4x in-plane refinement (51,626 → 206,504 cells),
  separation location moved by ~0.0002–0.0003 in x/c
  (`F6a_epistemic_band.md`, "Separation stayed well-posed under 4x
  refinement too"). Disclosure carried with the citation: that diagnostic
  ran on a perturbed variant (later found sign-flipped, L-26), so it
  evidences discretization-insensitivity of the separation point on a
  perturbed state, not a full baseline grid ladder; reattachment could not
  be compared under refinement because that variant does not converge on
  either mesh. It remains the only direct refinement measurement on this
  case and is consistent with the NASA-workshop finding that this bubble's
  error is a closure property, not a grid property
  (`LITERATURE_REPRODUCTION_REVIEW.md`).
- **Scale of channels:** numerical channel O(0.0003) on separation vs
  model-form channel O(0.18) on reattachment — three orders of magnitude
  apart on the quantities each is measurable on.

## 2. The model-form band, all evidence gate-checked

| closure | class | reattachment x/c | vs experiment 1.1000 | settle evidence |
| --- | --- | --- | --- | --- |
| kOmega | linear EVM | 1.0717 | −2.57% | gate-met, 22,211 iter (`hump_kOmega_resume_20260729T202024Z` + extension) |
| **experiment** | — | **1.1000** | — | NASA |
| kEpsilon | linear EVM | 1.1437 | +3.97% | gate-met (k final 4.35e-7) |
| SSG | Reynolds-stress transport | [pending — run near gate, bubble stationary at ~1.162] | ~+5.7% | [pending] |
| SpalartAllmaras | linear EVM | 1.2061\* | +9.65% | residual floor, QoI stable to 0.3% over 2,200 iter — gate NOT met, disclosed |
| realizableKE | linear EVM | 1.2503 | +13.66% | gate-met (k final 4.38e-8) |
| kOmegaSST (baseline) | linear EVM | 1.2534 | +13.95% | gate-met, re-verified |
| LRR | Reynolds-stress transport | 1.2647\* ± 0.007 | +14.97%\* | limit cycle, NOT gate-met — characterized, starred, in no band |

Gate-met band: **[1.0717, 1.2534]** — contains the experiment. Its width is
set by closure disagreement alone: same mesh, same BCs, same schemes, same
gates. (LRR's starred mean lies just above the top edge; if treated as a
data point it would widen, not break, the story — but it is not gate-met
and is not in the band.)

## 3. The mechanism is identified, not just bracketed (what makes this case *showable*)

Katie's hypothesis — the bubble length is set by how much turbulent
momentum transport the closure sustains in the separated shear layer, and
SST's limiter suppresses it — was pre-registered with falsifiers
(`F6a_DIFFUSION_PREREGISTRATION.md`, committed before any run) and tested:

- **Causally, within SST (T1):** raising the limiter coefficient a1
  0.31→0.40 raised shear-layer stress 15% and pulled reattachment
  1.2534→1.1873 (−0.066, 6.6x the significance bar), gate-met; lowering it
  to 0.25 cut the stress 40% and destroyed the steady solution entirely
  (residual floor, fragmented bubble, closure wandering ≥1.375). The dial
  named by the hypothesis moves the error, in both directions.
- **Across closures (T2):** [pending final correlation — five-model interim
  Spearman rho = −0.600, with the two highest-stress closures producing the
  two shortest bubbles, and realizableKE showing exactly the SST-like low
  stress H required of it]
- **Historical alignment:** kEpsilon's +3.97% on this case echoes the
  literature's known "k-epsilon looks better on this bubble" behaviour,
  which `LITERATURE_REPRODUCTION_REVIEW.md` shows is partly numerical-
  viscosity luck on coarser meshes in published work — our version is
  gate-met on the same mesh as every other model, so the comparison here is
  clean of that confound.

## 4. What "epistemic" buys that "error bar" does not

- A single-model answer of 1.2534 ± (numerical noise) would be **confidently
  wrong**: the numerical noise is O(0.0005) while the true error is 0.15.
- The multi-model band is an **honest ignorance statement**: the ensemble
  disagrees about the shear-layer transport level, the disagreement spans
  the truth, and the mechanism of disagreement is demonstrated (§3), so the
  band's width is physically interpretable — not a coincidence of four
  arbitrary codes.
- The band is cheap: five settled closures on a 51,626-cell case, minutes
  each on one core — the expensive part was the discipline (gates,
  falsifiers, failure records), not the compute.

## 5. Standing honesty constraints, carried forward

- The channel-1 straddle is a **sample of closures that happened to
  disagree across the truth**, not a designed bound
  (`F6a_epistemic_band.md`, "Straddling by disagreement is not the same as
  bracketing by construction"). The T1/T2 mechanism evidence upgrades its
  interpretability, not its guarantees. Any act built on this case must say
  "the band contained the truth and we can show why the models disagree,"
  never "the band is guaranteed to contain the truth."
- Nothing in this record touches or is touched by the withdrawn
  eigenvalue-perturbation corners (L-26). The one public number affected
  (`threeC` 1.1069) stays dropped per `D9_TALKING_POINTS.md`; the closest
  single check remains kEpsilon 1.1437 (+3.97%).
- Failures are part of the record: LRR's limit cycle, SSG's two false-gate
  divergences (and the new *converged-string-on-a-diverged-state* trap they
  exposed), the non-realizable-R root cause, and a1=0.25's destroyed fixed
  point are all in `F6a_DIFFUSION_RESULTS.md` with their logs — they are
  evidence about the physics (weak-diffusion states resist steady
  representation), not blemishes to hide.

## 6. Verdict on Katie's item 2

[pending T2 close-out — drafted conditional: if the final correlation holds
at the pre-registered threshold, the confirmation clause of her note is
satisfied and this case is the campaign's epistemic-uncertainty exhibit;
if it lands in the inconclusive zone, the exhibit stands on T1 + the band +
the small numerical channel, with the cross-model correlation reported at
its measured strength and not oversold.]
