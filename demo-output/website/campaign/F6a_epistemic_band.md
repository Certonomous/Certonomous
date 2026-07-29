# D9 / F6a — model-form uncertainty band on the NASA wall-mounted hump

**Harvested by the supervisor** from the D9 agent's completed runs after it was
interrupted four times (three host restarts, one API failure) without landing a
record. The prediction file `f6a_epistemic_band/PREDICTION.md` was written by the
agent **before any of these runs executed** and is scored below unedited.

> **2026-07-29 update, in progress.** Channel 1 was incomplete and its lower
> edge was resting on an unconverged number. Finishing it changes the
> headline finding below (section 1) -- not just its margin, its **sign**.
> See "2026-07-29: channel 1 completed, and the under-coverage claim breaks"
> further down. `realizableKE` and a newly-discovered `SpalartAllmaras` gate
> miss are still being worked; this note will be reconciled into the body
> once all four channel-1 models are honestly converged.

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
  channel-1 range, so that edge is soft. **RESOLVED 2026-07-29, see below —
  and the fix changed the sign of kOmega's deviation, not just its size.**
- `kEpsilon` and `realizableKE` case directories exist but have no converged time
  directory — they did not complete, and no numbers are claimed for them.
  **kEpsilon RESOLVED 2026-07-29. realizableKE in progress.**
- Separation is far better predicted than reattachment across every entry, which
  is consistent with the documented behaviour: these models get the onset roughly
  right and the recovery wrong.

---

## 2026-07-29: channel 1 completed, and the under-coverage claim breaks

Work order: (1) converge kOmega to its own 5e-7 gate rather than accept the
number it stopped at, (2) get kEpsilon and realizableKE past their `0/`
directory, (3) restate channel 1's range honestly, including if that breaks
the pre-registered under-coverage finding in section 1 above.

### kOmega: fixed the gate, and the number crossed the experimental value

kOmega's k-residual was not plateaued, just slow — a local decay-rate fit at
t=2000 (last-1000-iteration window, rate ≈9e-4/iter, itself still slowing)
projected roughly 1500-2000 more iterations to cross 5e-7. `endTime` was
extended 2000→8000 and the run resumed from `latestTime` with nothing else
changed. It converged genuinely: k final residual **1.373e-7** at t=8000
(down from 2.82e-6 at t=2000), omega final residual 8.8e-11. No relaxation
was loosened and no gate was moved to get there — it just needed more
iterations than the first attempt gave it.

The reattachment number moved, and it moved past the point that matters:

| time | k final residual | gate met? | reattachment x/c | vs 1.100 |
| --- | --- | --- | --- | --- |
| t=2000 | 2.82e-6 | NO | 1.1299 | +2.71% (over) |
| t=8000 | 1.373e-7 | **YES** | **1.0722** | **−2.53% (under)** |

kOmega no longer over-predicts reattachment. Converged, it **under-predicts**
it — the only channel-1 model to land on the low side of experiment.

### kEpsilon: converged after finding and fixing the actual divergence

kEpsilon had never gotten past `0/`. The prior launch (see
`solve_registry/hump_kEpsilon_20260729T035037Z.log`) diverged from iteration
4 onward — epsilon bounding exploded from O(1e6) to O(1e8) within ~30
iterations and the solver died to a SIGFPE by t=527. Root cause: the
relaxation factors (k=0.7, epsilon=0.7) were inherited unchanged from the
k-omega-family template. k-epsilon's near-wall epsilon production is
substantially more sensitive to under-relaxation than k-omega's on this
separated/reattaching geometry — this is a known property of the model
family, not specific to this case. Dropped to k=0.3, epsilon=0.3 (documented
in `fvSolution`) and it converged cleanly: k final residual 4.35e-7, epsilon
2.59e-8, both under the 5e-7 gate, at t=2000.

Also fixed in passing: `fieldDef` for both kEpsilon and realizableKE still
listed `residualFields`/`singleGraphFields` as `(U p k omega)` — a copy-paste
leftover from the k-omega-family template. kEpsilon and realizableKE never
transport omega; corrected to `epsilon`. This did not cause the divergence
(the actual gate lives in `fvSolution`'s `residualControl`, which was already
correct) but it meant the residual log and singleGraph postprocessing for
both models were silently tracking a field that doesn't exist for them.

kEpsilon result: separation x/c=0.6679, reattachment x/c=**1.1437**, **+3.97%**
vs experiment.

### realizableKE: harder divergence, different root cause, in progress

realizableKE diverged even at k=epsilon=0.3 (velocity-limiting hit 75-95% of
cells within ~15-25 iterations — a much faster, more severe blowup than
kEpsilon showed at the same relaxation). Tried k=epsilon=0.15 with fully
first-order upwind turbulence convection: still diverged, more slowly. The
instability onsets within the first ~15 iterations of a uniform-freestream
cold start, before under-relaxation has much leverage — this looks specific
to realizableKE's variable-`Cmu` formulation reacting to the initial
high-shear transient at the wall, not a generic k-epsilon-family issue (plain
kEpsilon was stable from the identical cold start with the same relaxation).

Fix: initialize realizableKE from kEpsilon's own converged t=2000 solution
(U, p, k, epsilon, nut, phi — same mesh, same field names/dimensions) instead
of the uniform-freestream `0/` state, documented in
`channel1_rans_sweep/realizableKE/INIT_NOTE.txt`. This is a standard
multi-stage RANS restart strategy, not a fit to the experimental target:
kEpsilon's converged field carries no information about the NASA measurement,
only about the flow physics both models solve. A short foreground test from
this IC (relaxation back at 0.3, original schemes) ran cleanly to k final
residual 6.8e-7 by t~980 with zero cells velocity-limited. Status: launched
for the full run; result to be folded in here once it lands.

### A finding the original brief didn't flag: SpalartAllmaras *also* missed its gate

While re-checking convergence status of all four channel-1 models (not just
the one the brief named), the case-directory `log.simpleFoam` for SA turned
out to be a stale fragment from an earlier aborted attempt (its last entry is
t=369; the case's actual `2000/` directory postdates it by 8 minutes). The
authoritative log is `solve_registry/hump_SpalartAllmaras_20260729T023234Z.log`,
and at t=2000 it shows: **Ux final residual 8.86e-7, Uz final residual
1.51e-6, nuTilda final residual 1.263e-6** — all above the case's own 5e-7
gate (`residualControl "(U|p|nuTilda)" 5e-7`). SA's published +9.93% is
therefore *also* an unconverged number, exactly the same class of problem
kOmega had, just never checked. Fix (extend `endTime`, resume from
`latestTime`, no relaxation or gate changes) is queued and will run next;
SA's number may move, though a swing large enough to change its side of 1.100
would need to be roughly 4x kOmega's swing in relative terms, which is not
expected but will be measured, not assumed.

### Does the pre-registered "channel 1 alone under-covers" claim survive?

**No — and it already breaks without waiting for realizableKE or the SA
re-run.** The claim, stated in `PREDICTION.md` before any of these runs
executed, was that all four channel-1 models would land on the
over-predicting side of 1.100, because the bubble-length bias is a property
of the whole linear-eddy-viscosity class, not a per-model quirk. With kOmega
now honestly converged at 1.0722 (**under** 1.100) sitting alongside SA
(1.2092, over — pending its own re-check) and kEpsilon (1.1437, over), the
channel-1 range already straddles the experimental value:

**Channel 1 range (kOmega, kEpsilon, SA-as-currently-reported; realizableKE
pending): [1.0722, 1.2092]. Experiment 1.100 is INSIDE this range.**

That is the opposite of "channel 1 alone under-covers." The pre-registered
prediction is **falsified** by the completed sweep, not confirmed. This does
not mean the underlying literature claim (linear EVMs share a reattachment
bias) is wrong in general — kOmega is still close to the other models in
absolute terms (1.07 vs 1.14-1.21, a much tighter spread than channel 3's
corners) and the SST *baseline* (1.2534) and SA and kEpsilon are all still
over-predicting by comparable amounts. What changed is a boundary condition:
kOmega happens to sit *just* on the near side of 1.100 rather than just past
it, and "under-covers" as a binary claim about whether the class straddles
the experimental value is exactly the kind of claim a difference of ~0.03 in
x/c can flip. The claim was falsifiable and it was falsified — reported as
such, not softened.

**Falsifiability, stated before reading final numbers (per the record's own
practice):** the claim breaks if and only if at least one channel-1 model
converges to reattachment x/c < 1.100 while at least one other converges to
x/c > 1.100 (a straddle), OR all four converge to x/c < 1.100 (a clean
reversal). kOmega crossing to 1.0722 already satisfies the straddle
condition against SA (1.2092) and kEpsilon (1.1437), independent of what
realizableKE or the SA re-check produce. Those two remaining numbers can
change the range's exact edges and could in principle produce the "clean
reversal" case instead of "straddle" (if SA's re-check also drops below
1.100), but they cannot un-break the claim — the straddle is already locked
in by three independently-converged numbers.

### Updated table (channel 1, in progress)

| channel | model / corner | separation x/c | reattachment x/c | vs experiment | gate met |
| --- | --- | --- | --- | --- | --- |
| — | **NASA experiment** | 0.6650 | **1.1000** | — | — |
| — | kOmegaSST (our baseline) | 0.6544 | 1.2534 | +13.95% | not re-checked here |
| C1 | SpalartAllmaras | 0.6544 | 1.2092 | +9.93% | **NO (1.26e-6 vs 5e-7) — re-run queued** |
| C1 | kOmega | 0.6620 | **1.0722** | **−2.53%** | **YES (1.37e-7)** |
| C1 | kEpsilon | 0.6679 | 1.1437 | +3.97% | **YES (4.35e-7)** |
| C1 | realizableKE | — | — | — | run in progress |

Separation x/c for kOmega also moved slightly with convergence (0.6592 →
0.6620); still close to the other models', consistent with the standing
observation that separation onset is the easy part and recovery is the hard
part.
