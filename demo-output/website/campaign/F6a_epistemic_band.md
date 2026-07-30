# D9 / F6a — model-form uncertainty band on the NASA wall-mounted hump

> **2026-07-30. A third instance of the same defect, this time in the
> "fix" itself.** A deliberate estate-wide convergence sweep (new tool:
> `scripts/check_convergence.py`) flags `hump_kOmega_resume_20260729T202024Z.log`
> — the run this file's own "channel 1 completed" section (below) reports as
> `k final residual 1.373e-7` and `YES` on the gate — as **not converged**.
> `1.373e-7` is the **Final** residual; the gate is checked on the
> **Initial** residual, which at t=8000 is `k` 3.21e-5 (64× over gate),
> `omega` 3.72e-9 (37× over its 1e-10 gate), `Uz` 6.14e-6 (12× over), `p`
> 1.41e-6 (2.8× over) — none under gate, and `SIMPLE solution converged`
> never prints anywhere in the log. This is the exact Final-vs-Initial
> misread already found twice tonight (the r4 sweep's Delta=0.25, and this
> same section's own original kOmega number before it was "fixed"), now
> found a third time in the fix itself. **The good news, checked
> immediately below the bad:** every field's Initial residual is decaying
> smoothly and monotonically across the whole run (k: 2.2e-4 at t=3000 →
> 3.2e-5 at t=8000, roughly ×0.7 per 1000 iterations, no plateau) — this is
> not the corner/r4-sweep floor pattern, it looks like a genuinely
> converging run that simply was not given enough iterations, the same
> character as this session's `boundedU` diagnostic. Extrapolating the
> current decay rate, k and omega (the long poles) would need roughly
> 10,000–12,000 more iterations to cross gate — a real but not
> extraordinary extension, not a re-run from scratch. **Until that
> extension is run and actually crosses the gate, kOmega's reattachment
> value (1.0722) and everything downstream of it — the "narrower channel
> catches the true answer after all" claim, the corrected public band
> `[1.0722, 1.2534]`, and the "we broke our own second prediction" framing
> on `D9_TALKING_POINTS.md` and `benchmarks.html` — rests on an unconverged
> number and should be treated as provisional, not settled.** Reported
> immediately per this project's own standing rule, before finishing the
> wider sweep it was found in. Full sweep report and the checker itself:
> `scripts/check_convergence.py`, `scripts/check_convergence_validate.py`,
> `scripts/check_convergence_sweep.py`.

> **2026-07-30, resolved. kOmega genuinely converged, and the number barely
> moved.** Extended 8000→25000, resumed from `latestTime`, nothing else
> changed. `SIMPLE solution converged in 22211 iterations` — printed once,
> for real this time. Final Initial residuals: Ux 1.54e-8, Uz 1.23e-7, p
> 1.62e-8, omega 7.40e-11, k 4.998e-07 (just inside the 5e-7 bar) — every
> gated field under target. `scripts/check_convergence.py`, wired into
> `launch_solve.sh`'s collector, classified this run CONVERGED automatically
> at completion. **Separation 0.6620, reattachment 1.0717** (extracted from
> `t=22211` with the same `hump_gate_analysis.py` used on every other rung
> in this study, single clean bubble, no fragmentation). Against the
> ungated t=8000 snapshot (sep 0.6620, reattach 1.0722): separation is
> exactly unchanged, reattachment moved by **−0.0005 (−0.047%)** — noise,
> not a real shift. **Still 2.57% below the experimental 1.100.** The
> corrected band `[1.0722→1.0717, 1.2534]`, the "narrower channel now
> catches the experiment" finding, and the "we broke our own second
> prediction" framing all survive — and for the first time tonight, on a
> run that is actually gated rather than one whose Final residual was
> mistaken for its Initial one. The provisional flag above is lifted. Table
> below updated in place; the "channel 1 completed" section's own numbers
> are left as originally written (now confirmed correct within noise) with
> its own correction note pointing here.

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

> **2026-07-29, later, more severe.** The same defect that broke channel 1
> (a number reported as converged that was not) is present in **channel 3's
> `oneC` and `twoC` corners — the two runs that carry the band's lower
> edge, 0.5278**. Neither printed `SIMPLE solution converged`; `oneC`'s wall
> shear trace is not a bubble at all (230+ sign crossings across the whole
> domain, velocity limiter active on 63% of cells — numerical noise, not a
> flow feature; the reported 0.5278 is an artifact of a search window
> finding the first crossing inside it, not a real reattachment location).
> Only `threeC` (1.1069) is genuinely converged. **The gate column below and
> "2026-07-29, later: the channel-3 corners were never gate-checked" at the
> end of this file are the correction; the "CONTAINS" verdict in the next
> section is not safe to treat as established until that section is read.**

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
| C1 | kOmega | 0.6620 | 1.0717 | **−2.57%** | YES, genuinely — converged in 22211 iter (2026-07-30, see below); supersedes the earlier 1.0722/"k final 1.37e-7" reading, which was Final-not-Initial and not actually gate-met |
| C1 | kEpsilon | 0.6679 | 1.1437 | +3.97% | YES (k final 4.35e-7) |
| C1 | SpalartAllmaras | 0.6541 | 1.2061 | +9.65% | NO, oscillating floor not a gap — see below |
| C1 | realizableKE | 0.6639 | 1.2503 | +13.66% | YES (k final 4.38e-8) |
| C3 | oneC (one-component limit) | 0.5250\* | 0.5278\* | **−52.02%\*** | **NO** — not a residual floor, not converging at all: Ux Initial 0.16, Uz Initial 0.12 (5-6 orders over gate), 63% of cells velocity-limited, wall trace is 230+ noise crossings, not a bubble |
| C3 | twoC (two-component limit) | 0.6242\* | 0.6701\* | −39.08%\* | **NO** — Uz Initial 3.25e-4 (650× over), omega Initial 8.79e-7 (8,790× over its 1e-10 gate); fragmented (5 crossings in the main-bubble region plus an unrelated reattach at x/c 1.48) |
| C3 | threeC (isotropic limit) | 0.6589 | 1.1069 | **+0.63%** | **YES** — printed "SIMPLE solution converged in 2948 iterations," all Initial residuals under gate |

\*oneC and twoC's separation/reattachment numbers are starred because they
are not measurements of a converged flow feature — see "2026-07-29, later:
the channel-3 corners were never gate-checked" at the end of this file
before using them for anything.

**Band across all completed runs: [0.5278, 1.2534] — AS PREVIOUSLY STATED,
BUT THE LOWER EDGE IS NOT A CONVERGED NUMBER.** Experiment 1.100 lies
inside the stated interval, but 0.5278 is extracted from a diverged,
noise-dominated run (see below), not a genuine reattachment measurement.
The "CONTAINS" verdict below predates this check and should be read
alongside the correction at the end of this file, not on its own.

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

> **2026-07-30 correction, then resolution.** This section's own numbers
> below (`k final residual 1.373e-7`, `omega final residual 8.8e-11`) are
> **Final** residuals, and the table below marked "gate met? YES" on that
> basis. The gate is checked on the **Initial** residual, and by that
> standard the t=8000 state did not meet it (k Initial 3.21e-5, omega
> Initial 3.72e-9, both far over gate; `SIMPLE solution converged` never
> printed). **Resolved same day**: extended 8000→25000, resumed from
> `latestTime`, nothing else changed. `SIMPLE solution converged in 22211
> iterations` — printed for real. Reattachment at t=22211: **1.0717**,
> against the ungated t=8000 snapshot's 1.0722 — moved by −0.0005 (−0.047%,
> noise), still 2.57% below the experimental 1.100. The numbers below stand,
> now on solid ground; see the top-of-file note for the full account. Left
> in place below exactly as originally written, per this record's own
> practice of correcting in a visible note rather than silently rewriting
> history.

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
| C1 | kOmega | 0.6620 | **1.0717** | **−2.57%** | **YES**, genuinely — 22211 iter, all Initial residuals under gate (2026-07-30; the 1.0722/"k final 1.37e-7" entry this superseded was never actually gate-met, see correction note above) |
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

> **Update, same day, later.** The "untested window" this section describes
> below was filled a few hours after this was written — Delta=0.175, 0.20,
> 0.225 were run and none of them converged either. See "2026-07-29, later:
> the decisive window filled" at the end of this file for the gate-checked
> table and the resulting verdict. The paragraph below is left as written,
> since it was true when it was written and the gap it describes is exactly
> what got tested next.

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

---

## 2026-07-29, later: the decisive window filled — the correlation holds, not just at the extremes

The gap identified above — Delta=0.175, 0.20, 0.225 never run, sitting
exactly where the containment crossing would have to be if the trend from
0.15 to 0.25 were smooth — was filled the same day. All three checked
against the gate the same way as everything above: `SIMPLE solution
converged` string count, and each field's **Initial** residual against
`residualControl` (`(U|p|k)` 5e-7, `omega` 1e-10) — not the Final residual.
Holding the L-14 line explicitly this time, since it is the exact trap that
cost this study the Delta=0.25 conclusion earlier the same day.

### Gate-checked: none of the three converged

| Delta | `SIMPLE solution converged`? | Initial residuals at t=3800 (gate: U/p/k 5e-7, omega 1e-10) | verdict |
| --- | --- | --- | --- |
| 0.175 | 0 occurrences | Ux 1.00e-7 (ok), Uz 1.41e-6 (fail), p 1.70e-6 (fail), omega 5.45e-10 (fail, 5.4× over), k 9.94e-9 (ok) | **NOT converged** |
| 0.20 | 0 occurrences | Ux 1.47e-6 (fail), Uz 1.27e-5 (fail), p 2.09e-5 (fail), omega 3.00e-8 (fail, 300× over), k 1.30e-6 (fail) | **NOT converged** — worst of the three |
| 0.225 | 0 occurrences | Ux 1.97e-7 (ok), Uz 2.01e-6 (fail), p 1.97e-6 (fail), omega 9.41e-10 (fail, 9.4× over), k 8.70e-9 (ok) | **NOT converged** |

Tracked over the last 1800 iterations (t=2000→3800), none of the three
show a decaying trend on their failing fields — p and Uz oscillate around a
plateau at 0.175 and 0.225, and at 0.20 the p residual is trending *up*
(4.19e-5 → 6.08e-5 → 9.22e-5 → 1.13e-4 across that window, i.e. getting
worse, not better, as the run proceeds). Same signature as Delta=0.25:
residual floor, not slow convergence caught mid-transient.

**Every single run at Delta ≥ 0.10 has now failed its gate.** That is seven
non-control points (0.10, 0.15, 0.175, 0.20, 0.225, 0.25 by residual floor;
0.50, 0.75 by outright divergence — eight, counting both) covering the
entire tested range beyond the two converged control points, with zero
exceptions. This is no longer three data points at the extremes — it is
continuous coverage of the interval that matters, and the correlation
between "moves toward or past 1.100" and "fails to converge" holds across
all of it.

### What actually happens in the window, and it is not a smooth interpolation between 0.15 and 0.25

The wall-shear crossings in this window are not a tidy bridge between
Delta=0.15's ~1.36–1.38 and Delta=0.25's ~0.71. Instead the bubble
structure re-organizes: a short bubble reappears near the same location as
the fully-converged control (sep ~0.64–0.65, reattach ~0.70–0.72), followed
by a second separation that does not close until far downstream — x/c 1.38
at Delta=0.175, 1.42 at Delta=0.20, and by Delta=0.225 the flow downstream
of x/c≈1.46 breaks into a cluster of six more sign crossings packed into
0.13 of a chord, right at the edge of the sampled domain:

- Delta=0.175: sep 0.6495 → reattach 0.7191 → sep 0.7336 → reattach 1.3778 (4 crossings)
- Delta=0.20: sep 0.6474 → reattach 0.7089 → sep 0.7624 → reattach 1.4216 → sep 1.4415 → reattach 1.4461 → sep 1.5950 (7 crossings)
- Delta=0.225: sep 0.6434 → reattach 0.7049 → sep 0.7984 → reattach 1.4621 → [6 more crossings between 1.46 and 1.59] (13 crossings total downstream of the leading edge)

None of this is a single-valued "reattachment x/c." Reporting any one
number from this window as *the* reattachment point would misrepresent
what the wall-shear trace actually shows.

### Verdict on the correlation: it holds across the decisive interval, not just at the extremes

Per this task's earlier framing, three failed points at the extremes
(0.25, 0.50, 0.75) were a pattern, not a result. Eight failed points
covering Delta=0.10 through 0.75 continuously, including the exact window
where a containment crossing would have to sit, is a different kind of
evidence. Combined with the topology finding above — the bubble does not
smoothly shrink through this window, it splits into a near-wall remnant of
the control-case bubble plus a much longer, increasingly fragmented
downstream structure — the working interpretation is:

**Tightening this band by scanning Delta for containment is not merely
circular here. On the evidence gathered on this mesh with these schemes,
no genuinely converged, single-bubble steady solution exists anywhere in
the Delta range that would be needed to bring reattachment down to 1.100.**
That is a stronger and more useful claim than "we could not tighten it" —
it says *why*: the perturbation strong enough to move the mean flow toward
the experimental value also pushes it into a flow topology (a
short near-wall bubble plus a long, unsteady downstream separated region)
that a steady RANS solve cannot represent as a fixed point on this
discretization. Whether that limit is intrinsic to the physics or an
artifact of this specific mesh/scheme combination is exactly what the two
diagnostics below are for — this section reports the observation, not the
attribution.

### Are the non-convergence and the fragmentation the same phenomenon, or two?

**The same phenomenon, on the evidence gathered.** Every converged run
(0.00, 0.05) has a single clean bubble. Every non-converged run (0.10
through 0.75) is fragmented, and fragmentation severity tracks
non-convergence severity step for step: 0.10/0.15 have a small
secondary crossing riding on a mild residual floor; 0.175/0.20/0.225 have a
genuinely split bubble structure (near-field remnant plus a long,
increasingly multi-valued downstream region) riding on a residual floor
that in one case (0.20) is actively getting worse with iteration count; 0.50
and 0.75 are total numerical noise riding on outright divergence. There is
no run in this sweep where one occurs without the other. The coherent
reading is that a genuinely steady SIMPLE iteration requires a genuinely
steady flow topology to converge *to*; once the perturbation is strong
enough to push the mean flow into a state with more than one candidate
separation/reattachment structure, there is no single fixed point for the
outer iteration to find, and what gets logged as a "residual floor" is the
iteration hunting between quasi-steady states that a true unsteady
simulation would resolve as a low-frequency oscillation (bubble
pulsing/shear-layer flapping) rather than a bug. This reading is
consistent with, not a repeat of, the SpalartAllmaras residual-floor entry
elsewhere in this record, which showed the same signature (oscillating
residual, near-stationary mean field) from an unrelated cause (a model
difference, not an imposed anisotropy perturbation) — the mechanism
proposed here is specific to this sweep and has not been independently
confirmed, which is exactly what the mesh and scheme diagnostics below
test.

### Separation stays well-posed while reattachment does not — worth stating on its own

Across every point in this sweep that has not fully diverged (Delta=0.00
through 0.225), the *first* separation crossing is a single, smooth,
monotonically decreasing number, fragmentation-free even where everything
downstream of it is not: 0.6544 → 0.6534 (0.05) → 0.6523 (0.10) → 0.6507
(0.15) → 0.6495 (0.175) → 0.6474 (0.20) → 0.6434 (0.225) → 0.6396 (0.25).
Reattachment, over that same span, goes from a single converged number, to
two crossings, to a split bubble with a downstream tail that fragments
into more crossings the higher Delta goes. Only at Delta=0.50/0.75, where
the solution has diverged outright, does separation stop being
well-behaved too — but that is total solution breakdown, a different and
more severe failure than fragmentation. This extends the pattern already
on record from channel 1 ("separation onset is the easy part, recovery is
the hard part," a statement about *accuracy*) into a statement about
*numerical well-posedness*: separation location is not just easier to get
right, it is easier to compute a fixed point for. It stays a well-posed
scalar quantity across the entire range where reattachment stops being one.

### Diagnostics launched to separate an intrinsic limit from a fixable artifact

Two single-variable probes were launched at the already-established
failing point Delta=0.25, neither replacing the original non-converged
sweep point, neither touching a gate or a relaxation factor:

- **`oneC_delta0.25_boundedU`** — one change: `div(phi,U)` switched from
  `bounded Gauss linearUpwind unlimited` to `bounded Gauss linearUpwind
  limited`, i.e. the momentum convection scheme now uses the same bounded
  gradient reconstruction (`cellLimited Gauss linear 1`) that k and omega's
  convection already used. The asymmetry — turbulence quantities bounded,
  momentum not — was present in every case in this sweep and is a
  plausible numerical (not physical) contributor to instability in a
  reversing/recirculating shear layer.
- **`oneC_delta0.25_finemesh`** — same case, mesh refined 4× in the two
  physically relevant in-plane directions via `refineMesh -dict
  ... -all` (51,626 → 206,504 cells; confirmed via edge-length statistics,
  not assumed, that the true empty/spanwise direction was left untouched;
  `checkMesh` reports a valid mesh, max non-orthogonality 43.1°, max
  skewness 0.74). One mechanical fix was required and is recorded here
  because it touches case files: `refineMesh` does not remap hardcoded
  nonuniform boundary-profile lists (`U_inlet`, `k_inlet`, `omega_inlet`,
  `p_inlet`, `p_outlet`, each a literal 83-entry list describing the
  inlet/outlet boundary-layer profile), so the first launch attempt failed
  immediately with a field-size mismatch (83 vs. the refined patch's 166
  faces). Fixed by duplicating each entry onto its two child faces in
  order — the same piecewise-constant mapping `refineMesh` performs
  automatically for internal fields — not by altering any value. This is a
  mesh-topology fix, not a tuning of the physics or the gate.

Both were run to the same t=3800 cap and the same residualControl gate as
every other point in this sweep. Results were not available at the time
this section was written; they will be appended as a further dated update
rather than folded into this one, so the sequence of what was known when
stays honest.

---

## 2026-07-29, later: the channel-3 corners were never gate-checked

Prompted by the r4 sweep's pattern (every non-control point past Delta=0.05
fails its gate) — the obvious next question was whether the original
Delta=1 corner runs that this whole study's headline claim rests on had
ever actually been checked the same way. They had not. Checked now, exactly
as everything above: `SIMPLE solution converged` string, Initial residual
against `residualControl` (`(U|p|k)` 5e-7, `omega` 1e-10), source
`solve_registry/uq_oneC_20260729T023701Z.log`,
`uq_twoC_20260729T023709Z.log`, `uq_threeC_20260729T023709Z.log`.

### oneC — not a residual floor, not converging at all

Zero occurrences of `SIMPLE solution converged`; ran to the `endTime=3800`
cap. At t=3800: **Ux Initial residual = 0.162, Uz Initial = 0.123** — five
to six orders of magnitude over gate, not a near-miss (k = 9.03e-4, omega =
4.99e-5, both several orders over their own thresholds too). The velocity
limiter is active on **62.67% of cells, 20.99% of faces** at the final
iteration. The wall-shear trace is not a bubble: the gate script finds
**230+ sign crossings spanning the entire domain**, x/c = −2.02 to +1.58 —
the same signature as this sweep's Delta=0.50/0.75 divergence, numerical
noise rather than a flow feature. **The published 0.5278 is the first
"sep→reattach" crossing the analysis script's `[0.3, 1.6]` search window
happens to find inside an otherwise chaotic field.** It is not a physical
reattachment location and should not be used as one. No resume was ever
attempted for this run (unlike kOmega/kEpsilon/realizableKE/SA in channel
1, each of which got a documented fix); a precursor feasibility run shows
the same instability as early as t≈1792 (p Initial residual 0.17 there
too) — this was never close to settling, not a fluke of one run.

### twoC — also not converged, fragmented rather than pure noise

Zero occurrences of `SIMPLE solution converged`. At t=3800: Uz Initial =
3.25e-4 (650× over gate), p Initial = 5.95e-5 (119× over), **omega Initial
= 8.79e-7 (8,790× over its 1e-10 gate)**, k Initial = 7.86e-5 (157× over).
Not pure noise like oneC — the main crossing (sep 0.6242, reattach 0.6701,
the published number) is real in the sense of being a genuine local
feature, but it is immediately followed by four more small
separation/reattachment pairs between x/c 0.69–0.80, then an unrelated
reattachment far downstream at x/c 1.48. Multi-valued and non-converged,
same class of problem as this sweep's Delta=0.10–0.225 points.

### threeC — genuinely converged, trust this one

`SIMPLE solution converged in 2948 iterations` — printed, real. All Initial
residuals under gate at that step (Ux 9.83e-9, Uz 6.29e-9, p 6.52e-9, omega
9.70e-11, k 2.08e-8). Clean single bubble (plus the small leading-edge
artifact present in every case in this family), sep 0.6589 / reattach
1.1069. This number — publicly quoted as the closest single check to the
experiment — is solid.

### What this means for the flagship claim

The band `[0.5278, 1.2534]` reported as "CONTAINS" the +13.95% experimental
miss has its **lower edge built on a diverged, noise-dominated run**, not a
converged measurement — the same defect class as the channel-1 kOmega
misread earlier this same day, except more severe (that one was a genuine
slow transient that finished converging on a longer run; `oneC` shows no
sign of ever settling and is majority velocity-limited). `twoC`, also
load-bearing in the published table, is likewise not converged. **Channel
3 alone currently has no genuinely converged number below the experimental
value of 1.100** — `threeC` (1.1069) sits just above it. Excluding `oneC`
and `twoC` as their own gate requires, the only real, converged number
anywhere in this entire study that falls below 1.100 is channel 1's kOmega
at 1.0722. This does not mean the band fails to contain — it means the
"CONTAINS" verdict currently rests on a different, weaker foundation than
the one stated in the "Measured" table at the top of this file, and the
public surfaces that quote 0.5278 and the channel-3-designed-bound
narrative should be re-examined against this finding, the same way they
already were once today for the channel-1 reversal.

---

## 2026-07-29, later still: what the literature says this sweep actually is, and the two diagnostics land

### Delta is the field's own "moderation factor" — this was not an idiosyncratic sweep

`LITERATURE_REPRODUCTION_REVIEW.md` section 2, read in full: Heyse, Mishra
& Iaccarino (2021, JGPPS, open access, DOI 10.33737/jgpps/134643) apply the
same full-corner eigenvalue perturbation (their `Delta_B`, our channel 3's
method exactly) and report, quoted directly: *"the perturbations had an
effect on the convergence of the solver... the convergence difficulties
were dependent on the particular limiting state."* Convergence difficulty
being **corner-dependent** is a property the method's own developers
report, on a different (milder, gradual-expansion) geometry, not something
peculiar to this project's setup. Matha & Morsbach (2023, DLR,
arXiv:2303.06149 / *Physics of Fluids* 35(6):065130) report that the
field's standard response to a hard-converging corner is a **moderation
factor `f`** (sometimes called an "under-relaxation factor" in other
publications) that weakens the perturbation below the full corner to
recover a steady solution — and explicitly not a switch to an
unsteady/URANS solver.

**Our `Delta` parameter is exactly this moderation factor**, by
construction (`system/fvOptions`: `deltaR = blendDelta * 2k(bPert - bB)`,
a linear scaling of the full-corner forcing). This sweep was not an
unusual experiment bolted onto the method — it was the field's own
documented remedy, applied systematically, with every point checked
against a hard convergence gate rather than accepted on inspection. Framed
this way, the result reads differently: **the standard remedy does not
rescue the corners in the range this band would need them in.** Eight
moderation values (0.10 through 0.75) were tried; none converged; the two
that did (0.00, 0.05) sit on the far side of the experimental value from
where the band needs a converged floor. That is a specific, checkable
claim about a documented field practice failing on this specific case, not
a complaint about this project's own setup.

### Do the literature's stated moderation values match what we tried?

Checked directly against both sources (Heyse et al. full text already read
in the literature review; re-fetched here specifically searching for
numeric values, plus a fresh fetch of the Matha & Morsbach arXiv text).
**Neither paper states a specific numeric moderation value used in common
practice.** Heyse et al. only ever uses the full corner, `Delta_B=1.0` (their
data-driven variant predicts a spatially-varying strength via a trained
model, not a constant practitioners could quote). Matha & Morsbach name
the practice and cite two further sources (their refs 22, 23) for its
origin, but those were not retrieved this session — first by the literature
review, and confirmed again now by a direct fetch of the arXiv PDF, whose
extracted text contains no numeric `f` value either. **This is a genuine
gap, not a convenient one**: it means neither "our failing range (0.10-0.75)
brackets normal practice" nor "our converged Delta=0.05 is unusually
gentle" can be asserted from what has actually been read. What can be said
is narrower and still worth stating: Delta=0.05 is the smallest moderation
this sweep tried short of the unperturbed baseline, it is the only
moderated (nonzero) point that converged, and it moved the reattachment
*away* from the experiment (1.2534 → 1.3077, +18.88% vs. the baseline's
+13.95%) rather than toward it. Whatever the field's typical `f` turns out
to be, the direction of this one converged, moderated data point is itself
a result about the method on this case, not a curiosity to set aside:
on the hump, at least the first step of moderation in this direction makes
the over-prediction worse, not better.

### The corner-dependence test, and it narrows the claim usefully

If convergence difficulty is corner-dependent (Heyse et al.'s own finding),
the cheap check is whether our three corners behave differently from each
other at the same nominal strength. They do, sharply: **`threeC`
(isotropic) converges cleanly at full strength (Delta=1, 2948 iterations,
gate met). `oneC` (one-component) does not converge at any tested Delta
from 0.10 to 1.0 — the entire range past the control points — and `twoC`
(two-component) also fails at its own full strength.** This is the same
asymmetry Heyse et al. report on their diffuser, now shown on a harder
geometry and with a resolution the earlier report did not have: **it is
not "perturbation breaks the solve," it is "the `oneC`/`twoC` corners break
the solve, `threeC` does not."** That is a narrower, more useful statement
than a blanket claim about the method — it points at the one-component and
two-component limiting states specifically (the two extremes that suppress
or redirect turbulent shear stress most aggressively) as the source of the
difficulty, consistent with `threeC` sitting closest to the Boussinesq
baseline of the three corners and thus requiring the least departure from
a state the solver already knows how to hold steady.

### The two diagnostics have landed: neither rescues convergence, and refinement makes it worse

Both diagnostics — one variable changed each, neither replacing the
original Delta=0.25 sweep point — ran to the same t=3800 cap and the same
gate. **Neither converged.**

| variant | `SIMPLE solution converged`? | Initial residuals at t=3800 (gate: U/p/k 5e-7, omega 1e-10) | crossings |
| --- | --- | --- | --- |
| original (unlimited scheme, 51,626 cells) | 0 occurrences | Ux 2.68e-7, Uz 2.59e-6, p 4.73e-6, omega 7.79e-9, k 2.44e-8 | 3 (sep 0.6396, reattach 0.7111, sep 0.8468 unmatched) |
| `boundedU` (limited scheme, same 51,626-cell mesh) | 0 occurrences | Ux 1.96e-7, Uz 1.62e-6, p 1.97e-6, omega 5.99e-9, k 2.68e-8 | 3 (sep 0.6395, reattach 0.7119, sep 0.8383 unmatched) — essentially identical to the original |
| `finemesh` (unlimited scheme, 206,504 cells, 4× refined) | 0 occurrences | Ux 1.75e-4, Uz 7.76e-3, p 1.04e-3, omega 1.05e-7, k 7.39e-6 | 13 (multiply-fragmented near-wall bubble plus a long downstream tail to x/c≈1.60) |

**Bounding the momentum convection scheme to match the (already-bounded)
turbulence-quantity scheme improved the residual magnitude by roughly 2×
but did not converge, and left the flow topology essentially unchanged** —
the crossing locations move by less than 0.001 in x/c from the original.
Whatever is driving the non-convergence, it is not primarily the
unbounded-gradient momentum reconstruction; that was a plausible, testable
hypothesis and it did not hold up.

**Refining the mesh 4× did not converge either, and made every residual
substantially worse** — 2 to 3 orders of magnitude worse than the original
51,626-cell case's already-failing residuals, with the velocity field
(Uz) alone now 15,500× over its gate rather than 5×. The wall-shear trace
also gained structure rather than losing it: 13 crossings instead of 3,
with a topology — a near-wall remnant bubble plus a long, multiply-broken
downstream tail extending to the edge of the sampled domain — that closely
resembles what this sweep found at Delta=0.20-0.225, not a cleaner version
of the original Delta=0.25 result.

**Verdict.** A genuine coarse-mesh discretization artifact would be
expected to improve, or at worst stay flat, under refinement — refineMesh
here did neither; residuals got dramatically worse and the flow revealed
more structure, not less. A genuine scheme artifact from the unbounded
momentum reconstruction would be expected to at least partially resolve
under a bounded scheme — it did not; the topology barely moved. Neither
of the two most obvious "our own setup is at fault" explanations survives
contact with its own diagnostic. On the evidence gathered — two
single-variable probes, not an exhaustive search of mesh/scheme space —
**the non-convergence at this Delta looks like a property of the flow
under this perturbation on a steady RANS (SIMPLE) formulation, not an
artifact of the specific 51,626-cell mesh or the specific unbounded
momentum scheme this sweep happened to start with.** This is stated as the
best current reading of the two tests actually run, not as a proof that no
mesh or scheme anywhere would converge — that would require a broader
search than two points, and is exactly the kind of overclaim this study
has been warned against making. Combined with the literature finding
above (corner-dependent convergence difficulty is a documented property of
this method, and the standard remedy — moderation — does not rescue
`oneC`/`twoC` anywhere in the tested range on this case), the honest
summary is: **on the NASA hump specifically, the `oneC` and `twoC`
eigenvalue-perturbation corners appear to have no accessible steady RANS
solution between their converged control point and the full corner, on
every mesh and scheme variant tried so far.**

### Closing detail: residual trends and fragmentation timing, not just endpoints

Read the full trend, not just the t=3800 snapshot, per the standing rule
that an endpoint number is not evidence of what happened to get there.

**`boundedU`** genuinely improves over the run: Uz Initial residual falls
from 6.66e-5 at t=1000 to 1.62e-6 at t=3800 (≈40×), k and omega both decay
by two to three orders of magnitude over the same span, and Ux ends inside
its gate. Only p and Uz plateau just above gate in the final third of the
run (p's inner GAMG sweep count climbs from 2 at t=1000 to 81 by t=3800 —
the pressure solve is straining harder, not less, even as the outer
residual sits still). This is a real, if incomplete, transient — closer to
"still converging, ran out of iterations" than a locked floor.

**`finemesh` does not show this.** Ux and Uz Initial residuals are
essentially flat from t=1000 (2.24e-4, 9.38e-3) to t=3800 (1.75e-4,
7.76e-3) — under a 30% change across 2800 iterations, not a decaying
transient. p is the same story (0.0194 → 0.0164, and most of that drop
happens in the first 800 iterations). Only k and omega show real decay,
and even they remain 15–1000× over gate at the end. **This is a harder,
more immediately-locked failure than the original 51,626-cell case
showed, not a slower version of the same recovery.**

**The fragmentation on the fine mesh is not growing chaos — it is an
early, stable pattern.** Checked at t=1000, 1800, 2600, 3200, 3800: by
t=1000 the wall-shear trace already shows 11 crossings in the main-bubble
region; by t=1800 it has settled into essentially the same 13-crossing
shape (a near-wall cluster of small crossings between x/c 0.64–0.72,
disconnected from a long downstream tail reattaching and re-fragmenting
between x/c 1.42–1.60) that persists with only cosmetic drift through
t=3800. **The fine-mesh run fails the SAME way throughout its length, not
a different or worsening way** — it locks onto a 13-crossing multi-valued
structure early and stays there, which is the signature of resolving a
genuinely multi-valued (or slowly, persistently unsteady) flow state, not
of noise accumulating from an unstable numerical scheme. A scheme-driven
blow-up typically gets worse monotonically over time; this doesn't — it
converges, just not to a single value.

**Read together, against the coarse-mesh original (3 crossings) and
`boundedU` (3 crossings, essentially the same 3 as the original, sep/
reattach/sep locations agreeing to under 0.001 in x/c):** refining the
mesh 4× did not shrink or clarify the structure toward a single bubble —
it revealed more than four times as many crossings, present from early in
the run and stable thereafter, while every residual got two to three
orders of magnitude worse. Under-resolution produces the opposite
signature — spurious structure that a finer mesh smooths away. Getting
*more* structure and *worse* convergence from a *better* mesh is what a
genuinely multi-valued flow state looks like under a formulation (steady
SIMPLE) that requires a single fixed point to converge to.

### What is licensed, and what is not

**Licensed by direct test:** the non-convergence at Delta=0.25 is not a
consequence of the unbounded-gradient momentum reconstruction (bounding it
left the topology unmoved to under 0.001 in x/c and only partially
improved residuals), and it is not a consequence of insufficient mesh
resolution (refining 4× made it worse on both residuals and fragmentation
count, the opposite of what under-resolution artifacts do). Both were the
two most plausible fixable explanations and both are eliminated by direct
test, not by assumption.

**Not licensed:** "intrinsic to the method," unqualified. Two artifacts
eliminated is not all artifacts eliminated. Untested and remaining on the
table: a different pressure-velocity coupling or relaxation strategy
(only the standard SIMPLE/GAMG combination with this case's original
relaxation factors was tried); a coupled or pseudo-transient solver
(PIMPLE/local-time-stepping) rather than SIMPLE; a genuinely unsteady
(URANS/DES) treatment, which the moderation-factor literature notes is
*not* the field's documented remedy but which was never tried here either
and would be the direct test of whether the multi-valued structure is a
low-frequency physical oscillation, as hypothesized, rather than an
artifact of demanding a steady solution at all; and a systematic mesh/
scheme sweep rather than the two single points tested. The honest form:
**the failure survives the two most likely setup explanations, so the
evidence now favors an intrinsic limit over an artifact for this specific
Delta on this case, with the above list still open.**

### Fold-in: what the literature and the diagnostics say together

Delta is the field's own documented moderation factor (Matha & Morsbach
2023). The standard remedy for a hard-converging corner is to moderate it
until a steady solution is achievable (not to switch solvers). This sweep
applied that remedy systematically — eight values, 0.10 through 0.75 —
and none converged. The representative failing point (Delta=0.25) was then
tested against its two most obvious fixable explanations, and both were
ruled out by direct test. **So: on this case, the field's documented
remedy for hard-converging eigenvalue-perturbation corners does not work,
and the two most likely reasons it might not be our own setup's fault are
eliminated.** That is a specific, citable, negative result about a
documented practice, not a complaint about this project's implementation
— and it is the strongest claim this sweep is able to support.

### Separation stayed well-posed under 4× refinement too

The separation-vs-reattachment asymmetry already on record extends
through the fine-mesh diagnostic. The finemesh case's first separation
crossing is 0.6398 at every time checked (1000 through 3800, drifting by
under 0.0003) — as single-valued and stable as the coarse mesh's, even
while everything downstream of it fragments into 13 crossings and the
residuals sit two to three orders of magnitude over gate. Separation
location is not just easier to get right and easier to find a fixed point
for on the original mesh — it stays that way under 4× refinement, on a
run whose reattachment region is actively unable to settle. The asymmetry
is mesh-independent; the failure to converge is not evenly distributed
across the flow, it is concentrated entirely downstream of separation.
