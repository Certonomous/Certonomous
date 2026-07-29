# D9 / F6a — model-form uncertainty band on the NASA wall-mounted hump

**Harvested by the supervisor** from the D9 agent's completed runs after it was
interrupted four times (three host restarts, one API failure) without landing a
record. The prediction file `f6a_epistemic_band/PREDICTION.md` was written by the
agent **before any of these runs executed** and is scored below unedited.

> **2026-07-29 update, reconciled.** Section 1 below originally scored the
> pre-registered "channel 1 alone under-covers" prediction as CORRECT. It
> is not — channel 1 was incomplete, its lower edge (kOmega) was resting on
> an unconverged number, and finishing the sweep flips the verdict. Section
> 1 has been rewritten in place to say so; the full evidence (per-model logs,
> residuals, the SA oscillation, and the corrected baseline check) is in
> "2026-07-29: channel 1 completed" further down. This is the corrected
> version — the three public surfaces (benchmarks.html, Active Research
> board, SPC speaking notes) were corrected from this same finding and
> should already agree with it.

## The binary test

> Does a defensible model-form uncertainty band on hump reattachment `x/c`
> **contain** the measured +13.95% over-prediction?

**Answer: YES — but the band is very wide, and where the width comes from
matters more than the pass.**

## Measured (2026-07-29, channel 1 fully re-converged)

| channel | model / corner | separation x/c | reattachment x/c | vs experiment | gate |
| --- | --- | --- | --- | --- | --- |
| — | **NASA experiment** | 0.6650 | **1.1000** | — | — |
| — | kOmegaSST (our baseline) | — | 1.2534 | **+13.95%** | YES, converged in 1772 iter (checked 2026-07-29, see below) |
| C1 | kOmega | 0.6620 | 1.0722 | **−2.53%** | YES (k final 1.37e-7) |
| C1 | kEpsilon | 0.6679 | 1.1437 | +3.97% | YES (k final 4.35e-7) |
| C1 | SpalartAllmaras | 0.6541 | 1.2061 | +9.65% | NO, oscillating floor not a gap — see below |
| C1 | realizableKE | 0.6639 | 1.2503 | +13.66% | YES (k final 4.38e-8) |
| C3 | oneC (one-component limit) | 0.5250 | 0.5278 | **−52.02%** | — |
| C3 | twoC (two-component limit) | 0.6242 | 0.6701 | −39.08% | — |
| C3 | threeC (isotropic limit) | 0.6589 | 1.1069 | **+0.63%** | — |

**Band across all completed runs: [0.5278, 1.2534].** Experiment 1.100 lies
inside. **CONTAINS.** (Unchanged by the channel-1 rework — the full band was
always carried by channel 3's corners, see point 2 below.)

## Reading it honestly — three things matter more than the verdict

### 1. Channel 1 alone DOES contain the truth — the pre-registered prediction was FALSIFIED

**This section originally said the opposite, scored as CORRECT, on the
strength of a table where one of the four channel-1 entries (kOmega) had not
met its own convergence gate.** Converged honestly, channel 1 now reads:

| model | reattachment x/c | vs 1.100 | side | gate |
| --- | --- | --- | --- | --- |
| kOmega | 1.0722 | −2.53% | **under** | met |
| kEpsilon | 1.1437 | +3.97% | over | met |
| SpalartAllmaras | 1.2061 | +9.65% | over | not formally met (see below) |
| realizableKE | 1.2503 | +13.66% | over | met |

**Channel-1 range: [1.0722, 1.2503]. Experiment 1.100 is INSIDE it.** Three of
four models over-predict; kOmega alone under-predicts, by a small margin. The
range straddles the experimental value because the models disagree about
which *side* of it they land on, not because any one of them was designed to
bound it.

The pre-registered prediction said the opposite would happen: *"the hump's
bubble-length over-prediction is understood in the literature as a shared
property of the whole linear-eddy-viscosity class ... expect all four to land
in roughly the same neighborhood, not below it. **Prediction: channel 1 alone
under-covers.**"* **That prediction is FALSE.** It looked correct only while
kOmega's number was propped up by 5800 fewer iterations than it needed — see
"2026-07-29: channel 1 completed" below for the full account, including why
this is the finding with the most teeth in the study precisely *because* it
overturns the punchiest sentence in the original result, not despite that.

**What this does and does not mean for the underlying literature claim:**
see "Straddling by disagreement is not the same as bracketing by
construction" further down — the four-model spread containing 1.100 is a
different, weaker kind of fact than channel 3's designed bounds containing
it, and the two should not be read the same way.

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

- ~~kOmega did not meet its residual gate~~ **RESOLVED 2026-07-29.** Converged
  to k final residual 1.37e-7 at t=8000. The fix changed the sign of kOmega's
  deviation, not just its size — see below.
- ~~kEpsilon and realizableKE case directories exist but have no converged
  time directory~~ **RESOLVED 2026-07-29.** Both diverged for different
  reasons and both are now converged and gate-met — see below.
- **SpalartAllmaras does not formally meet its gate as of 2026-07-29**
  (Ux final residual oscillates in a ~5e-7 to ~2e-6 band rather than decaying
  through it; nuTilda and Uz are under the bar). This was not previously
  checked or flagged. Unlike kOmega's case, the reattachment *number* itself
  is stable across 2200 extra iterations (1.2092 → 1.2071 → 1.2061, a 0.26%
  drift) while the residual oscillates — treated as a converged-in-practice
  value with the gate miss reported honestly rather than as an open item.
  See "SpalartAllmaras: predicted before reading the result" below.
- The baseline kOmegaSST case (+13.95%, the number the whole study is
  answering to) was independently checked 2026-07-29 given two of four
  channel-1 models turned out to have unmet gates: it converged cleanly,
  "SIMPLE solution converged in 1772 iterations" against endTime=2000, U/p/k
  at 5e-7 and omega at 1e-10. Not a soft number.
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

### realizableKE: harder divergence, different root cause, now converged

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
only about the flow physics both models solve. Converged from that IC at
relaxation 0.3, original schemes: k final residual 4.38e-8, epsilon 1.01e-8,
both far under the 5e-7 gate.

A second bug surfaced along the way: `writeInterval $endTime` (only write at
the literal end) combined with resuming from a synthetic start time of "1"
meant the run could converge, print "End", and write **nothing** — no
crash, no error, confirmed-converged residuals sitting only in the log, zero
new field data on disk. Caught by checking for the expected time directory
rather than trusting "the process exited cleanly." Fixed by switching to
periodic `writeInterval 100`; final numbers taken from t=1901 (last
checkpoint, residuals already ~4e-8, an order of magnitude under gate).

realizableKE result: separation x/c=0.6639, reattachment x/c=**1.2503**,
**+13.66%** vs experiment — the largest over-prediction of the four
channel-1 models, close to the kOmegaSST baseline's own +13.95%.

### SpalartAllmaras: predicted before reading the result

Re-checking convergence status of all four channel-1 models (not just the
one the brief named) turned up a second unmet gate. The case-directory
`log.simpleFoam` for SA was a stale fragment from an earlier aborted attempt
(last entry t=369; the case's actual `2000/` directory postdates it by 8
minutes). The authoritative log,
`solve_registry/hump_SpalartAllmaras_20260729T023234Z.log`, shows at t=2000:
**Ux final residual 8.86e-7, Uz 1.51e-6, nuTilda 1.263e-6** — all above the
5e-7 gate. Extended `endTime` 2000→3200 and resumed.

**Prediction, written before reading the resumed run's result:** nuTilda and
Ux/Uz were decaying cleanly and monotonically at t=2000, the same pattern
kOmega showed right before it moved substantially. If SA behaves like
kOmega, the number could move a lot. I do not expect that, for a reason
visible before the final answer: at t=3200 (1200 more iterations), Ux had
*not* continued its clean decay — after reaching ~5.4e-7 near t=2600 it
began oscillating with growing amplitude, plateauing around 1.8e-6, while
the reattachment number itself barely moved (1.2092 → 1.2071, a 0.17% drift)
over those same 1200 iterations. That is the signature of a small persistent
unsteady mode (plausibly shear-layer flapping near reattachment) holding the
formal SIMPLE residual up while the mean solution is already close to
stationary — a residual floor, not a slow monotonic transient. **Prediction:
extending further will not bring the reattachment number materially closer
to 1.100; it will stay in the 1.19-1.21 neighborhood, and Ux will keep
oscillating rather than cross the gate.** I would be surprised, and would
need to retract this, if the extended run instead showed continued
monotonic drift at anything like kOmega's rate.

**Result at t=4200 (2200 more iterations):** Ux final residual 1.446e-6 —
still oscillating, still has not crossed 5e-7 (its oscillation envelope is
slowly decaying, ~1.86e-6 at t=3201 down to ~1.45e-6 by t=4200, but nowhere
near done). Reattachment x/c: **1.2061** — down from 1.2071, a further 0.08%
drift. Total drift from t=2000 to t=4200 (2200 iterations): **1.2092 →
1.2061, −0.26%.** The prediction holds: SA is not moving toward 1.100, and
more iterations mostly cycle the residual rather than the physical answer.

**Reported honestly: SA's gate is NOT formally met** (Ux residual has not
crossed 5e-7; nuTilda and Uz have). No further extension is planned — the
evidence above (three checkpoints across 2200 iterations, reattachment
stable to within 0.3%) supports treating 1.2061 as the physically converged
value despite the open residual, rather than chasing an oscillating
bookkeeping number for diminishing returns. This is reported as a plateau
with its value, per the study's own standing rule for models that will not
cleanly converge — not resolved by relaxing the gate, because the gate was
never relaxed and still reads NO.

### Does the pre-registered "channel 1 alone under-covers" claim survive?

**No.** The claim, stated in `PREDICTION.md` before any of these runs
executed, was that all four channel-1 models would land on the
over-predicting side of 1.100, because the bubble-length bias is a property
of the whole linear-eddy-viscosity class, not a per-model quirk. All four
channel-1 models are now honestly converged (SA's residual gate is the one
exception, and its physical answer is stable — see above), and the range is:

**Channel 1 range: [1.0722, 1.2503]. Experiment 1.100 is INSIDE this range.**
kOmega alone under-predicts (−2.53%); kEpsilon, SA, and realizableKE all
over-predict (+3.97%, +9.65%, +13.66%).

That is the opposite of "channel 1 alone under-covers." The pre-registered
prediction is **falsified**, not confirmed. This does not mean the
underlying literature claim (linear EVMs share a reattachment bias) is wrong
in general — three of four models still over-predict by comparable amounts,
and kOmega's under-prediction is a small margin (−2.53%) next to how far the
others over-predict (up to +13.66%). What changed is a boundary condition:
kOmega happens to sit *just* on the near side of 1.100 rather than just past
it, and "under-covers" as a binary claim about whether the class straddles
the experimental value is exactly the kind of claim a difference of ~0.03 in
x/c can flip. The claim was falsifiable and it was falsified — reported as
such, not softened.

**Falsifiability, as stated mid-investigation (before realizableKE or SA's
extension landed):** the claim breaks if and only if at least one channel-1
model converges to reattachment x/c < 1.100 while at least one other
converges to x/c > 1.100 (a straddle), or all four converge to x/c < 1.100
(a clean reversal). kOmega's crossing to 1.0722 already satisfied the
straddle condition against SA and kEpsilon before either realizableKE or
SA's extension ran; both landed as predicted (over-predicting, not flipping
the outcome) and the final range confirms a straddle, not a reversal.

### Straddling by disagreement is not the same as bracketing by construction

Channel 1's range now contains 1.100. Channel 3's range also contains 1.100.
These look like the same kind of result and are not.

Channel 3's `oneC`/`twoC` corners are **deliberately constructed** extremal
states of the Emory/Iaccarino barycentric-map perturbation — a method
designed to bound plausible Reynolds-stress anisotropy. If that method is
implemented correctly, containing the truth is closer to a *guarantee* than
a *finding*: the corners are chosen precisely to overshoot in both
directions. Containment there validates the machinery, not the specific
number.

Channel 1's range contains 1.100 for a different and much less structural
reason: four independent closure models, none of them designed to bound
anything, happened to disagree about which side of 1.100 they land on. That
disagreement is not large — kOmega's under-prediction (−2.53%) and the
others' over-predictions (+3.97% to +13.66%) are all modest compared to
channel 3's designed spread (−52% to +14%). The straddle exists because
kOmega's converged value (1.0722) happens to sit 0.0278 below 1.100, a gap
about half the size of the gap between kOmega and kEpsilon, the next-closest
model. Nothing about the RANS closure literature predicts *that specific
margin*; it is what four particular coefficient sets and wall treatments
produced on this particular mesh. A slightly different mesh, a slightly
different convergence point, or a fifth linear model could easily have
landed the whole class on one side, exactly as `PREDICTION.md` expected.

The practical consequence: channel 1's containment should not be read as
"inter-model spread is a validated uncertainty band, use it going forward."
It is closer to a coincidence that happened to be informative — worth
reporting exactly as measured, not worth promoting to a method. Channel 3
remains the part of this study that is a *method*; channel 1, even now that
it contains the truth, is a *sample of four points that disagreed enough to
straddle it once*.

### Final table (channel 1 complete)

| channel | model / corner | separation x/c | reattachment x/c | vs experiment | gate met |
| --- | --- | --- | --- | --- | --- |
| — | **NASA experiment** | 0.6650 | **1.1000** | — | — |
| — | kOmegaSST (our baseline) | — | 1.2534 | +13.95% | **YES** (1772 iter, checked 2026-07-29) |
| C1 | kOmega | 0.6620 | **1.0722** | **−2.53%** | **YES** (k final 1.37e-7) |
| C1 | kEpsilon | 0.6679 | 1.1437 | +3.97% | **YES** (k final 4.35e-7) |
| C1 | SpalartAllmaras | 0.6541 | 1.2061 | +9.65% | **NO** (Ux oscillates ~1.4e-6; physically stable, see above) |
| C1 | realizableKE | 0.6639 | 1.2503 | +13.66% | **YES** (k final 4.38e-8) |

Separation x/c for kOmega also moved slightly with convergence (0.6592 →
0.6620); still close to the other models', consistent with the standing
observation that separation onset is the easy part and recovery is the hard
part.

---

## 2026-07-29: r4 band-tightening sweep read, and the tightening does not survive the gate

The question this sweep was set up to answer: not "does the band contain
1.100" (already YES, via the full-corner channel-3 band
`[0.5278, 1.2534]`), but **how tight can the band be made while still
containing**, by dialing the channel-3 eigenvalue-perturbation magnitude
`Delta` up from 0 (unperturbed kOmegaSST) toward 1 (the full oneC corner)
and finding the smallest `Delta` at which the perturbed reattachment first
drops below 1.100.

Seven points exist in `r4_band_tightening_hump/`: Delta = 0.00, 0.05, 0.10,
0.15, 0.25, 0.50, 0.75. Delta=0.00, 0.25, 0.75 had already been looked at.
Delta=0.05, 0.10, 0.15, 0.50 had finished but nobody had read them. Reading
all seven together, checked against `system/fvSolution`'s actual
`residualControl` gate (`(U|p|k)` at 5e-7, `omega` at 1e-10, checked on each
field's **Initial residual** — the value printed before the linear solve
each SIMPLE iteration, which is what OpenFOAM's own convergence check uses
and what triggers the `SIMPLE solution converged` message), gives a
materially different picture than the one carried into this task.

### The curve, gate-checked

| Delta | iterations | gate met | separation x/c | reattachment x/c | vs 1.100 | flow topology |
| --- | --- | --- | --- | --- | --- | --- |
| 0.00 | 1795 | **YES** — printed "SIMPLE solution converged in 1795 iterations"; all fields' Initial residuals under gate at that step | 0.6544 | **1.2534** | +13.95% | single clean bubble |
| 0.05 | 2124 | **YES** — printed "SIMPLE solution converged in 2124 iterations"; all fields' Initial residuals under gate (Ux 9.8e-9, Uz 8.9e-9, p 7.9e-9, omega 9.85e-11, k 2.3e-8) | 0.6534 | **1.3077** | +18.88% | single clean bubble |
| 0.10 | 3800 (hit endTime cap) | **NO** — p's Initial residual oscillates 9e-8 to 5.2e-7 over the last 1400 iterations with no decaying trend, ends at 5.24e-7 (just over the 5e-7 gate); everything else is under gate | 0.6523 | 1.3509 / 1.3724 (two crossings) | above, ambiguous | fragments: reattaches, re-separates almost immediately, reattaches again |
| 0.15 | 3800 (cap) | **NO** — p and Uz both oscillate well above gate through the whole tail (p: 5.7e-7–1.5e-5, Uz: 6.4e-7–1.2e-6); GAMG needs 47–96 inner iterations per pressure solve by the end (vs. ~2 for the converged points) — the pressure solve itself is struggling | 0.6507 | 1.3567 / 1.3777 (two crossings) | above, ambiguous | fragments the same way as 0.10, worse |
| 0.25 | 3800 (cap) | **NO — corrected, see below** | 0.6396 (first main-bubble crossing) | 0.7111 (main crossing; a further sep at 0.8468 has no matching reattach in-domain), plus a small extra bubble near x/c≈0 | below | multiply-fragmented, bubble does not close cleanly |
| 0.50 | 3800 (cap) | **NO — diverged.** k/omega bounding exploding (k avg 960, omega avg 1.91e5), velocity limiter active on 3.1% of cells | — | dozens of spurious Cf sign crossings across nearly the whole domain | n/a | numerical noise, not physics |
| 0.75 | 3800 (cap) | **NO — diverged, worse.** k avg 5.26e4, omega avg 4.88e5, limiter active on up to 48% of cells (already flagged before this task) | — | 80+ spurious sign crossings | n/a | numerical noise, not physics |

**Only two points on this sweep are genuinely converged: Delta=0.00 and
Delta=0.05.** Both are *above* the experimental 1.100. Everything from
Delta=0.10 upward fails its own gate, and by Delta=0.10 the flow has already
fragmented into multiple separation/reattachment events — "reattachment
x/c" stops being a single number exactly where the curve starts to matter.

### Correction: Delta=0.25 was reported "converged cleanly." It is not.

This task's brief carried forward "Delta=0.25 converged cleanly (k 1.67e-9,
omega 4.25e-11) at reattachment 0.7111" as an established result. Both
residual figures are real and are in the log at t=3800 — but they are each
field's **Final residual**, the value *after* that iteration's linear
solve, not the Initial residual the gate actually checks. Tracking the
Initial residuals for the same run from t=2000 to t=3800:

| t | p (last GAMG solve), Initial | Uz, Initial | omega, Initial |
| --- | --- | --- | --- |
| 2000 | 5.27e-6 | 3.41e-6 | 1.42e-8 |
| 2400 | 4.14e-6 | 3.08e-6 | 6.00e-9 |
| 2800 | 2.48e-6 | 2.45e-6 | 4.57e-9 |
| 3200 | 4.04e-6 | 2.02e-6 | 4.77e-9 |
| 3600 | 3.88e-6 | 2.32e-6 | 5.31e-9 |
| 3800 | 4.73e-6 | 2.59e-6 | 7.79e-9 |

Gate is p/U at 5e-7, omega at 1e-10. p is 10–150× over gate throughout,
Uz is 4–7× over, omega is 46–140× over — and none of the three is decaying;
omega's Initial residual is *rising* over the last 1200 iterations, not
falling. This is a residual floor, the same signature already documented
for SpalartAllmaras elsewhere in this record ("a residual floor, not a slow
monotonic transient") — except here it was not caught, and the point was
carried into this task as a landed value on the curve. It is not one.
Reported here per the study's own rule: a point that does not meet its gate
is reported separately, not on the curve, regardless of who reported it or
when.

### The containment-breaking Delta cannot be established from converged data

The two converged points (0.00 → 1.2534, 0.05 → 1.3077) are both above
1.100, and 0.05 moved *away* from the experiment relative to 0.00, not
toward it — the response is non-monotonic near the origin before whatever
happens later. No converged run in this sweep reaches below 1.100. The
unconverged, provisional numbers suggest the crossing happens somewhere
between Delta=0.15 (provisional ~1.36–1.38, still above 1.100, still
fragmenting) and Delta=0.25 (provisional ~0.71 on the main crossing, below
1.100, worse fragmented) — an untested, badly-conditioned window where
pressure-solve inner iterations were already climbing into the 70–96 range
before the run ended. **That window was never actually run**, so this is
not a bracket, it is a gap with two non-converged endpoints on either side
of it.

Per the standing rule, a point that does not meet its gate is not a point
on the curve. Since every run at Delta ≥ 0.10 fails its gate (0.10, 0.15,
0.25 by residual floor; 0.50, 0.75 by outright divergence), **this sweep
does not honestly establish any containment-breaking Delta**, and does not
honestly establish any band tighter than the one already on record.

### The tightest defensible band is therefore unchanged: [0.5278, 1.2534]

That band comes from the already-established, already-converged channel-3
corner runs (oneC at Delta=1, reported earlier in this record), not from
anything in this sweep. Nothing gate-met in `r4_band_tightening_hump/`
narrows it. Reporting Delta=0.25's provisional 0.7111 (or any other
unconverged point) as a "tighter band" would be exactly the failure mode
this task warned against: picking the Delta that produces a pleasing
result and calling it a finding. The two points that are actually solid
(0.00, 0.05) don't tighten anything — they sit above the existing ceiling
and, if anything, argue the ceiling could be a hair higher.

**Is tightening via this method legitimate, or is it circular?** As
attempted here, it would have been circular by construction: the only way
to name a "tighter" Delta is to scan Delta until the perturbed value drops
below 1.100 and report that Delta — which means the band is chosen because
it contains the answer, not because Delta has independent physical
grounding at that specific value. That is a fitted number wearing a
UQ-bound costume, and it is exactly what the rules for this task forbid.
On top of the circularity, there is a second, sharper problem specific to
this case: **every run that actually reaches down toward or past 1.100
(0.25, 0.50, 0.75) is also a run that failed to converge**, with severity
increasing together — 0.25 sits on a mild residual floor, 0.50 and 0.75
diverge outright. That correlation, from only three non-converged data
points, is suggestive rather than proven, but it points at a real
possibility: the perturbation strong enough to move reattachment down to
the experimental value may also be strong enough to destabilize the SIMPLE
iteration on this mesh/scheme combination, so a genuinely-converged,
single-bubble solution at the tightening Delta might not exist to be found.
If that holds up under more testing, tightening this band isn't just
methodologically circular here — it may not be reachable with a physically
well-posed steady solve at all, which would be a limitation of the
approach, not a result to report as a number.

### Fragmentation is real, starts earlier than previously noted, and undermines the scalar comparison independent of convergence

The record already flagged fragmentation at Delta=0.25 (three sign
crossings in the bubble region instead of one). This sweep shows it starts
earlier: **Delta=0.10**, the mildest perturbation beyond the converged
control points, already produces a double crossing right at reattachment
(1.3509 then immediately 1.3513/1.3724) — a small secondary bubble
appearing right where the single number would be read. Delta=0.15 shows the
same shape, larger. By Delta=0.25 the leading edge has its own extra
bubble and the main bubble does not close within the domain. By Delta=0.50
and 0.75 the wall shear stress trace is not a bubble at all — it is
numerical noise from a diverged bounded solution (dozens to 80+ sign
crossings), which is a divergence symptom, not a flow feature, and should
not be read as "extreme fragmentation."

This matters beyond convergence status: at exactly the Delta range where a
containment-breaking crossing would need to be identified, "reattachment
x/c" is not a well-defined scalar even before checking whether the run
converged. Comparing a multi-valued or ill-defined quantity to the single
NASA number is not meaningful there. Separation x/c, by contrast, stayed
single-valued and moved smoothly across every point in this sweep (0.6544 →
0.6534 → 0.6523 → 0.6507 → 0.6396) even as reattachment fragmented — the
same "separation is the easy part, reattachment is the hard part" pattern
already on record, now shown to hold for numerical well-posedness as well
as for model accuracy.

### What this sweep actually establishes

- The control point (Delta=0.00) still reproduces the independent baseline
  exactly — 0.6544 / 1.2534 — and Delta=0.05 is a second, independently
  gate-met point, so the machinery is not in question.
- No tighter containing band than `[0.5278, 1.2534]` is honestly supported
  by this sweep. The tightening exercise did not succeed, and reporting
  that it did not succeed is the correct output, not a gap to paper over.
- The attempted method for tightening was circular by construction (scan
  Delta for containment, report the Delta that contains). That the sweep
  additionally failed on convergence grounds means the circularity was
  never actually exercised to produce a false-positive "tight band" — but
  it would have been, had the Delta=0.25 misread gone unchecked.
- Fragmentation of the separation bubble at moderate Delta is a genuine
  property of the perturbed flow, appears earlier than previously
  documented (Delta=0.10, not 0.25), and is a standing objection to reading
  "reattachment x/c" as a single comparable scalar in that regime — not an
  artifact of any one non-converged run.
