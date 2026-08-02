# W3 — how much of the cube's published envelope is its solve not stopping

**Complete. Run 2026-08-02 06:24:48 → 06:42:5x UTC, 3000 iterations.**
Pre-registration: `W3_CUBE_SETTLE_PREREGISTRATION.md`, commit ee30a7c3,
written before any iteration was read. Case
`/home/ubuntu/certonomous-runs/w3-cube-settle`. The mesh reproduced the
production rung exactly — **299 493 cells** — which is the check that nothing
but `endTime` changed.

*(An interim version of this file was committed at 03cab7b9 with the run at
iteration 896, on the principle that an overnight finding living only in a
watcher dies with the watcher. Every interim number is unchanged. The scoring
below is now final: two of the three verdicts recorded there as "heading for
FALSE" are confirmed, and the third — P1 — is settled the other way from how
the interim read it.)*

---

## 1. The settle curve

Trailing-window mean and spread, window = a quarter of the iterations so far
(the `tmr_verification` convention), from the run's own `coefficient.dat`.

| iteration | trailing mean Cd | window | peak-to-peak | 2σ |
| --- | --- | --- | --- | --- |
| **300** — where every stored cube rung stops | **1.104100119** | 75 | **2.1011 × 10⁻²** | 1.3490 × 10⁻² |
| 400 | 1.097754713 | 100 | 1.2776 × 10⁻³ | 6.4002 × 10⁻⁴ |
| 600 | 1.098055198 | 150 | 1.0138 × 10⁻³ | 5.6623 × 10⁻⁴ |
| 900 | 1.097830653 | 225 | 1.1539 × 10⁻³ | 7.3979 × 10⁻⁴ |
| 1200 | 1.097813334 | 300 | 1.1408 × 10⁻³ | 7.4459 × 10⁻⁴ |
| 1500 | 1.097818931 | 375 | 1.1376 × 10⁻³ | 7.4417 × 10⁻⁴ |
| 2000 | 1.097821077 | 500 | 1.1397 × 10⁻³ | 7.4333 × 10⁻⁴ |
| 2500 | 1.097821300 | 625 | 1.1465 × 10⁻³ | 7.4376 × 10⁻⁴ |
| **3000** | **1.097819606** | 750 | 1.1472 × 10⁻³ | 7.4321 × 10⁻⁴ |

## 2. Three predictions, three scored FALSE

**P1 — "it settles, between 600 and 3000 iterations" — FALSE, and the way it
fails is the most useful thing in this run.** OpenFOAM **never** printed
"SIMPLE solution converged". The residuals do not reach `residualControl` 1e-4
in 3000 iterations and show no sign of doing so. The interim file at iteration
896 recorded P1 as "on track"; it was wrong, and this supersedes it.

**But the drag is stationary from iteration 900.** The trailing mean reads
1.097831, 1.097813, 1.097819, 1.097821, 1.097821, 1.097820 at 900 / 1200 /
1500 / 2000 / 2500 / 3000 — **stable to 2 × 10⁻⁵ across 2100 iterations** —
while the trailing peak-to-peak sits on a floor of 1.14 × 10⁻³ and stops
falling entirely after iteration 900.

So the residual criterion and the force criterion disagree, and in the
direction that matters: **a settle criterion reading the force would have
stopped this run at about iteration 900; the residual criterion the curriculum
runner relies on would never stop it at all.** That is direct evidence for the
design `tmr_verification` adopted on 2026-07-31 — flatness driving the run
instead of only judging it — arriving from a different module and a different
body.

A mechanism is **named and not claimed**: a spread that stops falling and then
holds a constant amplitude is what a steady solver does on a limit cycle
rather than a fixed point, which is what a bluff body with a separated wake
would be expected to produce. Confirming it needs a frequency analysis of the
force history, which was not run.

**If that reading is right the consequence for the credential is structural:**
the cube's published C_d would be a **mean over an oscillation**, not a
converged steady value, and neither the ±0.0078 envelope nor the three-mesh
ladder underneath it describes that.

**P2 — "the settled value lands outside [1.0946, 1.1102]" — FALSE.** The
settled value is **1.097819606**, comfortably **inside**. It sits
−4.585 × 10⁻³ from the credential's own `value_working` of 1.1024049215, which
is 59% of the published envelope. **The envelope is wide enough to contain
where the solve actually goes.** The prediction failed in the direction that
favours the record, and is reported as such.

**P3 — "the distance still to travel at iteration 300 exceeds the window 2σ
measured there" — FALSE, by 2.34×, and instructively.** The distance is
**6.2805 × 10⁻³**; the 2σ measured at the cap on the production re-solve was
1.4686 × 10⁻². **The wobble at the cap over-reports what is left to travel.**

That is the *opposite* of the flat plate's failure mode quoted in the
pre-registration, where a tail-50 spread read as a plateau while the value was
still 1.05% from home. **Two bodies, two opposite failures of one fixed cap:
the flat plate looks calmer than it is, the cube looks wilder than it is.**

**Zero of three.** All three were written to be falsifiable and all three were
falsified. What they bought is §3.

## 3. What is established

**The cube's 300-iteration cap stops it mid-transient by a margin that matters
to the published number.** Between iteration 300 and 400 the trailing
peak-to-peak collapses **16-fold**, from 2.1011 × 10⁻² to 1.2776 × 10⁻³, and
the mean drops **6.2805 × 10⁻³** — **81% of the ±0.0078 envelope the
credentials wall prints beside it.** The credential's C_d is read high, off a
solve caught in its own startup.

**The stored ladder inherits this at every rung.** All three stored cube values
— 1.102982, 1.109239, 1.104172 — were taken at the same cap. Their total spread
of 6.26 × 10⁻³ across a 5.6× change in cells is essentially the same size as
the transient this run measures at a single rung. **That ladder's "rungs not
monotone" verdict is a reading of leftover transient, not of discretization.**

**The fix cannot be a bigger constant, and this run is why.**
`iteration_backstop()` is sized at 0.147 iterations per cell, measured on the
flat plate; at the cube's 299 493 cells that budgets **88 000 iterations** for
a body whose force is stationary by 900 and whose residuals will not converge
at 3 000 000. One tolerance cannot serve two bodies that fail in opposite
directions. The fix is a settle criterion driving each run on its own force
history with the backstop as a backstop — exactly what
`w3-run-uq-studies-still-caps-every-rung-at-300` asks for, and this is the
evidence for why it must not be simplified into a larger number.

## 4. What this does and does not say about the wall row

**Does:** the cube's published C_d is read from a solve stopped mid-transient
and is high by about 81% of its own envelope; the ladder underneath it is
measuring transient rather than mesh.

**Does not:** it does not say the envelope is too small — the settled value
sits inside it, 59% of the way out from the published value. It says the
envelope is **measuring the wrong thing**. The right recomputation is from
three rungs that each stopped because they were done.

The row is not edited here, per the pre-registration's §4 and per the open
ruling `w3-a-declined-ladder-still-publishes-an-envelope`.

## 5. Cost

`ExecutionTime = 1026.93 s`, `ClockTime = 1028 s`, 4 ranks, **74 873 cells per
rank** → **68.5 core-minutes.**

Estimated at ≈126 core-minutes in the pre-registration, from 300 iterations
costing 189.68 s of `ExecutionTime`, scaled ×10. **Measured 68.5 — 46%
under**, and the reason is worth carrying: **the first 300 iterations are the
expensive ones.** Cost per iteration falls sharply once the transient clears,
so scaling a long run linearly from a short one's cost **over**-prices it —
the same shape of error as scaling from a contended run's wall clock, which
over-priced the B-52 rung earlier tonight. Two over-pricing mechanisms in one
night, both from extrapolating a rate measured in the wrong regime.

The box carried up to 17 concurrent `simpleFoam` processes from other wells
during this run; `ClockTime` and `ExecutionTime` agree to 1 s here, so
contention did not distort the figure.
