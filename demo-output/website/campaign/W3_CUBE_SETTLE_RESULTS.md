# W3 — how much of the cube's published envelope is its solve not stopping

**Interim, written 2026-08-02 06:31 UTC with the run still in flight at
iteration 896 of 3000.** Pre-registration:
`W3_CUBE_SETTLE_PREREGISTRATION.md`, commit ee30a7c3, written before any
iteration was read. Case:
`/home/ubuntu/certonomous-runs/w3-cube-settle`, force history at
`postProcessing/forceCoeffs1/0/coefficient.dat`.

**This file is committed before the run ends deliberately.** An overnight
finding that lives only in a watcher dies with the watcher, and the answer to
the question that mattered is already unambiguous at iteration 896.

The mesh reproduced the cube's production rung exactly — **299 493 cells** —
which is the check that nothing but `endTime` changed.

---

## 1. The settle curve

Trailing-window mean and peak-to-peak, window = a quarter of the iterations so
far (the `tmr_verification` convention), from the run's own `coefficient.dat`.

| iteration | trailing mean Cd | window | peak-to-peak |
| --- | --- | --- | --- |
| **300** — where every stored cube rung stops | **1.104100119** | 75 | **2.1011 × 10⁻²** |
| 400 | 1.097754713 | 100 | 1.2776 × 10⁻³ |
| 500 | 1.098197905 | 125 | 6.5428 × 10⁻⁴ |
| 600 | 1.098055198 | 150 | 1.0138 × 10⁻³ |
| 700 | 1.097911238 | 175 | 1.1149 × 10⁻³ |
| 800 | 1.097851290 | 200 | 1.1404 × 10⁻³ |
| 896 | 1.097829945 | 224 | 1.1539 × 10⁻³ |

## 2. What is already settled, at 896 of 3000

**The cube's 300-iteration cap stops it in the middle of its transient, and by
a margin that matters to the published number.**

Between iteration 300 and iteration 400 the trailing peak-to-peak collapses by
a factor of **16**, from 2.1011 × 10⁻² to 1.2776 × 10⁻³, and the mean drops
**6.345 × 10⁻³**. From 400 onward the value is flat to about 4 × 10⁻⁴ and
drifting slowly downward toward **≈1.0978**.

So the number the credential rests on, read at the cap, is about
**6.3 × 10⁻³ above where the solve is going** — which is **81% of the
±0.0078 envelope the credentials wall prints beside it.**

**P1 — "it settles, between 600 and 3000 iterations" — on track but not yet
scored.** The solve has not printed "SIMPLE solution converged" by 896. The
value is stable to ~1 × 10⁻³ from iteration 400, which is settled for any
practical purpose but is 3× above `tmr_verification`'s own `SETTLE_TOL` of
3 × 10⁻⁷ — a tolerance set on a 2D flat plate, not on a bluff body with a
separated wake, and it should not be transplanted here without being re-earned.

**P2 — "the settled value lands outside [1.0946, 1.1102]" — heading for
FALSE.** ≈1.0978 is **inside** that interval. The published envelope, whatever
else is wrong with it, is wide enough to contain the value the solve actually
converges to. That is the prediction failing in the direction that favours the
record, and it is reported as such.

**P3 — "the distance still to travel at iteration 300 exceeds the window 2σ
measured there" — heading for FALSE, and instructively.** The distance is
6.3 × 10⁻³ and the 2σ at the cap was 1.4686 × 10⁻². **The wobble at the cap
over-reports what is left to travel, by 2.3×.** That is the *opposite* of the
flat plate's failure mode quoted in the pre-registration, where a tail-50
spread read as a plateau while the value was still 1.05% from home. The two
bodies fail the fixed cap in opposite directions: the flat plate looks calmer
than it is, the cube looks wilder than it is.

**That is the finding worth carrying.** A single settle tolerance, or a single
per-cell iteration budget, will not serve both. `iteration_backstop()` is
sized from 0.147 iterations per cell measured on the flat plate; at 299 493
cells that gives a backstop of 88 000 iterations for a body that is done at
about 500. The cure for the cube's fixed 300 is not the flat plate's number —
it is a settle criterion that drives each run on its own history, which is
what `w3-run-uq-studies-still-caps-every-rung-at-300` asks for and why it asks
for a criterion rather than a bigger constant.

## 3. What this does and does not say about the wall row

**Does:** the cube's published Cd is read from an unconverged solve, and the
reading is high by about 81% of its own envelope. Three of the numbers in the
stored three-rung ladder — 1.102982, 1.109239, 1.104172 — were each taken at
the same cap, so the ladder's 6.26 × 10⁻³ spread is substantially transient
and not discretization.

**Does not:** it does not say the envelope is too small. The settled value sits
inside it. It says the envelope is measuring the wrong thing, and that the
right recomputation is from three rungs that each stopped because they were
done — not from three rungs that each stopped at 300.

The row is not edited here, per the pre-registration's §4 and per the open
ruling `w3-a-declined-ladder-still-publishes-an-envelope`.

## 4. Cost, and the handover

Estimated at ≈126 core-minutes for 3000 iterations at 4 ranks. At iteration
896 the run has consumed roughly a third of that. The box carried 15
concurrent `simpleFoam` processes from other wells during this run, so its
wall clock is not comparable with anything; the cost that will be reported is
`ExecutionTime` × 4, per the B-52 lesson earlier tonight.

**If this file is the last word on the run, the run is still on disk.** The
remaining work is: read the final `coefficient.dat`, score P1 against whether
"SIMPLE solution converged" ever appears, and record the settled Cd. Nothing
above depends on it.
