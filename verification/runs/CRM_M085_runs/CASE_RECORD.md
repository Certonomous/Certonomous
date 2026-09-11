# CRM-M085 — case record. Failures, each with its fix or its measured reason.

Registration `verification/campaign/CRM_M085_PREREGISTRATION.md`, frozen at commit `ed8a6b07`,
blob `0a3dc597`. Kept short by Sanaa's 2026-09-11 rule: **documentation when a run fails and we
have the fix, and not otherwise.**

## PRE-FREEZE — three setup defects, caught by a one-iteration dry run in seconds each

| defect | fix |
|---|---|
| `forceCoeffs` refuses without `rhoInf` even with `rho rho;` | supply `rhoInf 0.048127`, the density derived for Re(cref)=5e6 — consistent with `magUInf`, unlike RUNG2_CRM_M2's `magUInf 295.0` over a M 0.196 field |
| `transonic yes` assembles a rho equation with no solver for it | add `"(rho|rhoFinal)" { solver diagonal; }` |
| `nOuterCorrectors 1` makes every solve a *Final* solve | match the Final variants: `"(p\|pFinal)"`, `"(U\|e\|k\|omega)(Final)?"` |

**The mesh was in inches and nothing had run `transformPoints`.** Scaled by 0.0254; bounding box
(-30328.2 0 -31438.1)(32996.6 31664.3 31866) → (-770.336 0 -798.527)(838.113 804.273 809.396).
The predecessor case ran `Aref 1.0` on the unscaled mesh — wrong by the entire reference area.

## R1 — `rc = 136` (SIGFPE) at `Time = 324` of 5000. 61.53 core-min.

**Chain, measured:** bad cells seed a local blow-up → local LTS collapse → `fvc::smooth` spreads it
to 100 % of cells → global freeze → arithmetic on a non-finite field → SIGFPE.

**The raw flow time scale maximum is bit-constant at `3.490203e-01 s` for all 323 iterations.**
Nothing else degraded it; the smoothing operator generalised it.

**The seed is on the worst mesh, and the correlation decays as it spreads** (enrichment of collapsed
cells in `nonOrtho>70`, base rate 1.790 %): **t=5 3.47× → t=10 10.16× → t=15 5.35× → t=300 0.14×.**
`highAspectRatioCells` enrichment at the seed is **0.00×**, so these are not boundary-layer cells.
Clamped-temperature cells at t=300: **13.21×** on `nonOrtho>70`, **45.76×** on `skew>4`.

### 🔴 THE BLOW-UP STARTS COLD, AND THE CEILING IS THE SECOND SYMPTOM
**At t=5 the FLOOR clamp fires alone — 1381 cells pinned at 100 K, ZERO at the ceiling, T max only
530.98 K.** The 1000 K ceiling does not engage until t=10 (120 cells). **Anyone tuning an upper
bound would be treating the symptom that appears second.** Any bounds work on this case starts at
the floor.

### 🔴 SURVIVAL COUNT IS NOT A MEASUREMENT — USE THE COLLAPSE RATE
R1 and the seed diagnostic are **the same configuration** (nnoc=2, 4 ranks, differing only in
`endTime`/`writeInterval`) and died at **iteration 324 and iteration 20** — a **16× spread**, near
bit-identical to iteration 10 and then separating. MPI reduction-order non-determinism amplified by
an exponentially diverging field. **No rung on this ladder is judged by how far it got. The metric
is the collapse rate of the smoothed LTS maximum at MATCHED ITERATIONS, which is deterministic
early.**

## LADDER — **EVERY RUNG CARRIES THE WINDOW IT WAS JUDGED ON**

**THE METRIC IS THE COLLAPSE RATE OF THE SMOOTHED LTS MAXIMUM, IN DECADES PER ITERATION, OVER A
STATED WINDOW OF MATCHED ITERATIONS.** Survival count is not a metric here (see above), and a rate
read at two points is not a rate either — that error was made and caught on rung 1. **A reader who
takes a verdict from this table without its window will repeat it.**

| rung | change | window judged on | rate (dec/iter) | verdict |
|---|---|---|---:|---|
| R1 baseline | `rDeltaTSmoothingCoeff 0.1`, `nnoc 2` | it 10 → 74 | **+0.0870** | reference; SIGFPE at it 324 |
| 1 | `nNonOrthogonalCorrectors` 2 → 6 | it 10 → 74, same window | **+0.1567** (overall 10→end) | **NO BENEFIT.** 1.08× — marginally faster — at **2.4×** the cost per step. Stopped by decision at it 80. |
| 2a | `rDeltaTSmoothingCoeff` 0.1 → 0.01 | it 10 → 26 | **+0.3927** | **4.5× WORSE.** And see the direction note below. Stopped by decision at it 33, `rc=143`. |
| 2b | `rDeltaTSmoothingCoeff` → 1 (**OFF**) | it 1 → 6 | **0.0000** | **THE LTS COLLAPSE STOPS COMPLETELY — AND THE CASE DIES FASTER.** SIGFPE at it 6. |

### 🔴 A DIRECTION ERROR IN RUNG 2a, AND WHAT IT ACCIDENTALLY BOUGHT
`fvc::smooth` uses `maxRatio = 1 + coeff` (`src/finiteVolume/lnInclude/fvcSmooth.C`), and
`setRDeltaT.H:63` calls it only when `coeff < 1`. **So a SMALLER coefficient means MORE smoothing.**
Rung 2a was built to "reduce the smoothing" and reducing the number did the opposite. **The rung is
therefore the high-dose arm, not the low-dose arm** — and because of that the ladder accidentally
produced a **three-point dose-response** instead of two tuning attempts.

### 🔴 THE DOSE-RESPONSE, AND IT SETTLES THE MECHANISM

| smoothing | coeff | LTS collapse | temperature clamps, early | died |
|---|---|---|---|---|
| most | 0.01 | **+0.3927 dec/iter** | — | (stopped it 33) |
| baseline | 0.1 | +0.0870 dec/iter | 1,381 low / 0 high at t=5 | it 324 |
| **none** | 1 | **ZERO — smoothed ≡ raw, max pinned at 0.34902029 every step** | **18,600 low / 9,729 high at it 6** | **it 6** |

**`fvc::smooth` is BOTH the amplifier of the LTS collapse AND the stabiliser holding the temperature
field together.** Turn it up and the LTS collapse accelerates 4.5×; turn it off and the LTS collapse
stops **entirely** while the temperature field goes unphysical **13× faster** and the run dies in six
iterations. **There is no setting of this operator that saves the case — both directions fail, for
different reasons.**

The disable was **verified, not assumed**: with `coeff 1` the `Smoothed flow time scale` line equals
the raw line on every one of the six iterations, and the source guard was read on this box.

## VERDICT: **`NOT A RESULT`** — THE CASE PARKS

Three measured rungs plus the seed diagnosis. **No rung 3 was climbed**, deliberately: a fourth
setting would be chasing a mesh defect with numerics.

**The measured reason:** the seed is **9,158 cells, 1.4 % of the mesh**, enriched **10.16×** in
`nonOrtho>70` and **11.28×** in `skew>4` at t=10, on a grid whose max non-orthogonality is
**89.7134°** against a gate of 70 and whose max skewness is **14.0593** against a gate of 4. The
smoothing operator spreads that seed to 100 % of cells; removing it leaves the seed to kill the run
directly. **Settings do not rescue an 89.71° / 14.06 mesh.**

**The case waits on a conforming grid, not on a numerics rung.** `COMMITTEE_GRID_NUMERICS.md` §4's
*"Relaxation buys iterations, not stability"* was recorded for the tet families; **on this evidence
it is a property of this hex family too.**

**Gate P and Gate G were never evaluated. No credential, no validated force, no drag claim.**

---

## MESH SOURCE — 2026-09-11, cfd `lab-lane`. **THE DPW5 COMMITTEE HEX FAMILY CANNOT SUPPLY THE CONFORMING GRID. MEASURED, ACROSS THREE LEVELS.**

The verdict above says *"the case waits on a conforming grid."* The obvious candidate was the
rest of the family this case already drew L1.T from. **It is measured and it is refuted.**

| level | source `.ugrid` | cells | max non-orth (gate 70) | max skew (gate 4) | misoriented pyramids | concave cells |
|---|---|---:|---:|---:|---:|---:|
| L1.T | `L1.T.rev01.p3d.hex.r8` | 638,976 | 89.7134 | 14.0593 | 35 | 499 |
| L2.C | `L2.C.rev01.p3d.hex.r8` | 2,156,544 | 89.7374 | 15.1516 | 45 | 780 |
| L3.M | `L3.M.rev01.p3d.hex.r8` | 5,111,808 | 89.7454 | 17.4801 | 53 | 1065 |

**EVERY COLUMN WORSENS MONOTONICALLY UNDER REFINEMENT.** Skewness climbs **+24.3 %** across the
family against a gate of 4; non-orthogonality is pinned just under 90° at all three levels — a
sliver face, not a resolution deficit. **Refining this family moves every gate metric AWAY from
its gate.** There is no finer member that clears, and waiting for one is waiting for a trend to
reverse that has been measured three times and never has.

Artifacts: `verification/runs/RUNG2_CRM_runs/GRID_ACQ/{L2C,L3M}/log.checkMesh` and
`BIRTH_CERTIFICATE.json`; `verification/runs/CRM_M085_runs/L1T/log.checkMesh_POSTSCALE`.

**ROUTE KILLED.** The CRM mesh source must come from outside this family. The case stays
`BLOCKED` on its mesh source; nothing here is a result and no gate is evaluated.

### THE INCHES HAZARD — VERIFIED AGAINST A KNOWN DIMENSION, NOT ASSUMED

**`GRID_ACQ`'s L2.C and L3.M are in INCHES and carry no `transformPoints`.** Their `wall` patch
spans y = 0 → **1159.85**, against the NASA CRM semispan of **1156.75 in** (ratio 1.00268, the
tip cap). In metres that number would read 29.38.

L1.T is the control: **pre-scale wall y-max 1159.85 → post-scale 29.4601 m**, against
1156.75 in × 0.0254 = **29.3815 m** — **the same 1.00268 ratio at both levels**, so the scale
factor is confirmed by an independent known dimension rather than by the number it produced.

**🔴 AND THE GATE METRICS ARE SCALE-INVARIANT — MEASURED, NOT ARGUED.** The same L1.T mesh in
both unit systems: non-orthogonality **89.7134 in both**, skewness **14.0594 vs 14.0593**, max
aspect ratio **14426.8 in both**. So the table above is valid gate evidence **even though L2.C
and L3.M were checked before scaling** — and, the other way round, **a wrong-units mesh passes
or fails exactly the same quality gates, which is precisely why no gate screen can catch it.**
Units are verified against a known dimension or they are not verified.
