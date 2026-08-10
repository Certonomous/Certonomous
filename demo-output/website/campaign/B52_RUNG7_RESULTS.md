# B-52 seventh rung — results

**Solved 2026-08-02 05:23:25 → 05:27:47 UTC.** Pre-registration:
`B52_RUNG7_PREREGISTRATION.md`, committed at d92a87f0 before the solver was
launched. Item `agp-880b4f92bdc5`.

---

## 1. The number

**Cd(441 057 cells) = 0.048220173**, mean over the final 20% of the force
history (60 of 300 rows), read from
`/home/ubuntu/certonomous-runs/study-b52-rung7-uq/postProcessing/forceCoeffs1/0/coefficient.dat`.

## 2. The pre-registered prediction is scored FALSE

G4 predicted, before the solve: *"Cd rises again, to between 0.0535 and
0.0575, and the third successive increment is larger than +0.002702."*

**Cd fell.** The increment is **−0.004055**, and it is the largest single
increment anywhere in this ladder's valid family.

| step | cells | h-ratio | Cd | increment |
| --- | --- | --- | --- | --- |
| | 135 779 | | 0.049053 | |
| 1 | 193 880 | 1.1261 | 0.047196 | −0.001857 |
| 2 | 255 358 | 1.0962 | 0.049573 | +0.002377 |
| 3 | 330 950 | 1.0903 | 0.052275 | +0.002702 |
| 4 | **441 057** | **1.1005** | **0.048220173** | **−0.004055** |

The alternative outcome named in G4 is the one that happened: *"If Cd instead
falls, or the increment shrinks, the divergence is not a constant-rate one and
the ladder has a turning point between 330 950 and 441 057 cells."*

**[WITHDRAWN 2026-08-10 — chief ruling `7abb0ba3`. The B-52 ladder's "turn" is withdrawn as a claim: the published −4.055e-3 is max(rung 6) − min(rung 7) of eight same-recipe draws, and re-estimated from all of them the rung 6→7 increment is +8.2e-5 ± 1.2e-3 (t = 0.071) — 49× smaller, opposite in sign, and smaller than the resolution-mismatch bias. A selected extremum is not a measurement. See `campaign/B52_TURN_WITHDRAWAL_2026-08-10.md`. Original text retained below.]**

**So the B-52's ladder does not diverge. It oscillates.** Down, up, up, down,
with the swings getting wider: 0.001857, 0.002377, 0.002702, 0.004055. The
reading this record has carried since 2026-07-31 — "successive Cd increments
GROW with refinement instead of shrinking" — was true of the three increments
then available and is **still true of the magnitudes**, but the sign pattern it
was read as (a monotone climb away from a limit) is not what this flow does.
The `monotone: true` flag on the stored four-rung fit was an accident of where
the ladder happened to stop.

## 3. The gates

**G1 — constant ratio. HOLDS.** h-ratio 1.1005 against the family's 1.0903,
0.94% apart, fixed before the solve.

**G2 — the rung is settled. HOLDS, on both limbs.** Final-20% window 2σ =
**3.584 × 10⁻⁵**, which is 0.074% of |Cd| (ceiling 5%) and **0.88% of the new
increment** (ceiling 10%). Halves drift, 150–225 against 225–300 iterations:
+3.95 × 10⁻⁶, 0.097% of the increment. The window spans 0.04819005 to
0.04825624. As with fine-uq and finer2, OpenFOAM printed no "SIMPLE solution
converged" message, so settledness is measured from the force history rather
than assumed.

The turn is therefore not iterative noise. It is **113 times** the window 2σ.

**A caveat that belongs to `w5-tmr-iteration-caps-are-guesses-not-measurements`.**
At the same fixed 300-iteration cap the three finest rungs settle to 2σ of
1.07 × 10⁻⁵ (255 358 cells), 2.25 × 10⁻⁶ (330 950) and 3.584 × 10⁻⁵
(441 057). The new rung is the least settled of the three, by 16× against
finer2 — but the middle rung is the most settled, so three points do not make
a trend and none is claimed. What is claimed is narrower and sufficient: the
cap was never derived from cell count, the settledness at that cap is not
improving with refinement, and both G2 limbs still pass here with two orders
of margin.

**G3 — the refit.** `uq.eca_hoekstra_band(dim=3)` on the five-rung valid
family:

| | stored (4 rungs) | **now (5 rungs)** |
| --- | --- | --- |
| `observed_order` | 2.253 | **None** |
| `monotone` | true | **false** |
| `richardson_extrapolated` | 0.06484235 | **None** |
| `band_abs` | 0.00634875 | **0.00506853** |
| `not_conclusive_guard` | increment_trend | **monotone** |
| `guards_holding` | increment_trend, extrapolation_sanity | **monotone** |
| `conclusive` | false | false |
| **`uq.reportable_band`** | **None** | **None** |

**Which number moved, and in which direction.** The fallback band falls 20%,
from 0.00634875 to 0.00506853 (10.74% of the production Cd 0.04719921, against
13.45%). That is the only number that moved in a direction anyone could call
favourable, and it is not a reportable one: `uq.reportable_band` returns None
before and after, because `conclusive` is false both times. Everything else
moved the other way — the ladder **loses** its observed order, **loses** its
Richardson extrapolate, and goes from monotone to non-monotone. A fifth rung
bought a worse verdict, which is what §1 of the pre-registration said a fifth
rung was for.

**G5 — what is not claimed.** The ladder is not conclusive, not asymptotic,
and earns no band anyone may print. `band_abs` was not read as a result;
`reportable_band` and `guards_holding` were.

## 4. Controls

* **Mesh recipe.** `system/` copied verbatim from
  `/home/ubuntu/certonomous-runs/study-b52-finer2-uq`; only `blockMeshDict`'s
  division triple differs, (51 45 75) → (55 49 82). `constant/triSurface/b52.stl`
  md5 `c27eec6c710f0a937ec8cfe84aec2cfe`, identical to finer2's. Pristine
  `0.orig` taken from `study-b52-030bc9`, whose `k`, `p`, `nut` and `omega`
  are byte-identical to finer2's pre-solve copies; `U` uniform (−0 −0 100),
  matching finer2's freestream.
* **Decomposition.** `system/decomposeParDict` unchanged from finer2:
  2 subdomains, hierarchical `n (2 1 1)`. **220 529 cells per rank.** The
  step this rung measures ends on two rungs solved at that same
  decomposition, so decomposition is not available as an explanation for the
  turn.
* **Mesh quality is not the cause.** Max non-orthogonality 64.641 here against
  finer2's 64.647 and fine-uq's 57.716; max skewness 3.535 against 3.999 and
  3.966. Both metrics are flat or better at the finer mesh, so a quality cliff
  cannot explain a sign reversal.
* **Solver ordering** matches finer2's `driver.log` exactly: serial
  potentialFoam `-writephi`, then decomposePar, then `mpirun -np 2 simpleFoam
  -parallel`.

## 5. Cost

| stage | ranks | cells/rank | measured |
| --- | --- | --- | --- |
| mesh attempt 1, (57 50 84), discarded on ratio | 1 | — | 119 s, **1.98 core-min** |
| mesh attempt 2, (55 49 82), used | 1 | — | 77 s, **1.28 core-min** |
| potentialFoam (serial) + decomposePar | 1 | — | 9 s, **0.15 core-min** |
| simpleFoam | 2 | 220 529 | 262 s wall / 261.11 s ExecutionTime, **8.73 core-min** |
| **total** | | | **12.14 core-minutes against `est_core_min` 20.0** |

Predicted in the pre-registration at ≈16.5 core-minutes; **measured 12.14,
26% under.** The over-prediction has an identifiable cause worth carrying
forward. The basis was finer2's simpleFoam **wall clock**, 285 s. That run's
own log reads `ExecutionTime = 183.26 s ClockTime = 284 s` — it spent 100 s,
35% of its wall time, waiting on a contended box. This rung ran on an idle one
and reads `ExecutionTime = 261.11 s ClockTime = 262 s`. **On ExecutionTime the
scaling is clean and slightly superlinear: 1.425× the CPU for 1.333× the
cells.** A cost basis taken from a contended run's wall clock over-predicts by
whatever the contention was, and it will do it again; take the ExecutionTime.

## 6. What this rung changes, and what it does not

It changes the B-52's fitted verdict from "monotone, order 2.253, held back by
a growing-increment trend" to "not monotone, no order". It does **not** move
any published number: the B-52 carries no row on the credentials wall, and the
band it does carry was already not reportable.

It does not settle the body. Four increments alternating in sign with growing
magnitude are consistent with a steady solution that is genuinely
mesh-dependent on this snapped-hex family, and consistent with a turning point
that a sixth rung would cross again. R4 met the same wall on the Ahmed 25°
from the other direction — a valid constant-ratio family that turned at its
fourth rung — and found there that iterations-to-convergence ran 158, 212,
220, 623, 1668, then never.

**[WITHDRAWN 2026-08-10 — chief ruling `7abb0ba3`. The B-52 ladder's "turn" is withdrawn as a claim: the published −4.055e-3 is max(rung 6) − min(rung 7) of eight same-recipe draws, and re-estimated from all of them the rung 6→7 increment is +8.2e-5 ± 1.2e-3 (t = 0.071) — 49× smaller, opposite in sign, and smaller than the resolution-mismatch bias. A selected extremum is not a measurement. See `campaign/B52_TURN_WITHDRAWAL_2026-08-10.md`. Original text retained below.]** *The Ahmed 25° half is NOT withdrawn: it has a single replicate pair, exactly the standing the B-52's turn had before this measurement, and it is the open question this withdrawal leaves behind.*

**Two of this lab's two genuine single-knob
ladders now both turn.** That is the finding worth taking further, and it is a
finding about steady RANS on refined snapped-hex meshes, not about either
body.
