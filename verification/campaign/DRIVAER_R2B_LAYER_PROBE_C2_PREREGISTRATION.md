# DRIVAER R2b — ABSOLUTE-FIRST-LAYER PROBE C2 (coarse only)

**Status: FROZEN ON COMMIT. No compute has run. Awaiting cfd-supervisor check 4.**
Rung id `R2b-C2`. One level, one build, no solver. 2026-09-12, cfd.

**C1's `GATE FAIL` STANDS AND IS NOT REHABILITATED.** Its 50 % coverage floor does not
move, no C1 number is reinterpreted, and F1 fired correctly at 32.390 %. C2 is a new
hypothesis about a **different quantity** — the *delivered* first-layer thickness, which
C1 measured and no registration had predicted — not a softening of a gate that bit.

## 0. THE EXITS, WRITTEN FIRST

**E1 — THE ROUTE IS REFUTED.** Coverage **< 50.0 %** at this ~2.4× thickness. Then
absolute layer sizing does not work on this geometry at this resolution, **DrivAer Cd is
`BLOCKED` on snappyHexMesh layer addition, and the lab stops.** This is **not** a third
value to try; two measured points at 0.040 and 0.096 thickness ratio bracketing a failure
is a refutation, and I will honour it the way I honoured F1.

**E2 — COVERED BUT OUT OF BAND.** Coverage ≥ 50 % **and** layered median y⁺ **> 300**.
Then absolute sizing can cover this surface but cannot do so inside the wall-function band
at coarse resolution. The **coarse** level is refuted. A finer level has smaller `h_surf`
and is not refuted by this — **and is NOT authorised by this registration.**

**PASS** requires **both**: coverage ≥ 50.0 % **and** layered area-weighted median
y⁺ ∈ [30, 300].

## 1. THE ONE CHANGE, and why this value

Against `r2_coarse`'s dict (`d13bbac3…`), three lines, everything else byte-identical:

```
relativeSizes false;   firstLayerThickness 5.00e-3;   minThickness 1.25e-3;
```

`expansionRatio 1.25`, `nSurfaceLayers 5` unchanged. C1 used 2.10e-3 / 5.25e-4.

## 2. PREDICT THE DELIVERED THICKNESS, NOT THE REQUESTED ONE

**C1's sharpest measurement: snappy delivered 3.519 mm against 2.10 mm requested — a
factor of 1.676 — on the faces it extruded.** y⁺ = 45,311.6 × t₁ (t₁ in metres), from the
measured `yplus_per_metre` = 90,623.25. A prediction that ignores that factor is one I
already know to be wrong.

| request | thickness ratio | predicted coverage | delivered y⁺ at factor 1.0 | at factor 1.676 |
|---|---|---|---|---|
| 3.60 mm | 0.0694 | **45.6 %** — fails the floor | 163 | 273 |
| **5.00 mm (REGISTERED)** | **0.0963** | **53.7 %** | **227** | **380** |
| 6.62 mm | 0.1276 | 60.6 % | 300 | 503 |

**THE TWO GATES ARE IN TENSION AND NO REQUEST SATISFIES BOTH UNDER THE FULL FACTOR
UNCERTAINTY. THAT IS WHAT C2 ACTUALLY TESTS.** 3.60 mm keeps y⁺ in band under either
factor but is predicted to fail coverage; 6.62 mm passes coverage but is out of band
unless the factor is ~1. **5.00 mm is the only request where both gates CAN pass, and it
passes only if the delivery factor falls toward 1 as the request grows.** That is
physically plausible — snappy over-delivers when asked for less than the extruder wants,
so the factor should approach 1 as the request approaches its preference — **but it is
measured at ONE point and is not established.** Resolving it is the point of C2.

**Registered prediction: coverage 53.7 %, delivered layered median y⁺ between 227 and 380
— and the upper half of that range is OUT OF BAND.** If the run lands there, E2 fires.

## 3. WHAT IS WEAK IN THE ABOVE, STATED BEFORE THE RUN

- **The coverage fit is TWO POINTS**, log-linear in thickness ratio, 24.6 points per ln
  unit. It has no third point and no mechanism behind it.
- **The thickness-ratio axis depends on `h_surf` = 51.9 mm**, which was backed out of the
  control's y⁺ **assuming delivered ≈ requested for the RELATIVE spec** — and C1 has just
  shown that assumption false for absolute sizing. If it is also false for relative
  sizing, every ratio in the table shifts and the coverage column moves with it.
  **The y⁺ predictions do NOT depend on `h_surf` and are unaffected.**
- Coverage is therefore the **softer** of the two predictions, and it is the one the
  exits turn on. Registered as such rather than discovered later.

## 4. Cost

**Predicted 80 core-min** — from C1's own **measured 79.77 core-min** on identical work,
not from the 4.4 core-min uncontended figure that C1 missed by 18.13×. That miss was the
box, not the estimate: 4,786 s wall against 264 s uncontended. **Predicted peak 0.6 GiB**
(C1 measured 0.46 GiB). 80 core-min = 1.33 core-h → **$0.068 DERIVED, NOT MEASURED**.
**NO CAP KILLS ANYTHING.** The MemAvailable refusal is armed as a physics guard.

## 5. Grading path — LITERAL HASHES

| instrument | sha256 |
|---|---|
| `cases/navier_class/DRIVAER/mesh/run_build.sh` | `7577f707d17e0718aacefadb95fb304f94e934578e2926ae2ca623ed72aecebd` |
| `cases/navier_class/DRIVAER/mesh/stage_r2_measure.py` | `c86a8ea4317f0dc21a00c9c739f8de7932bebf86345751632deddffd1640bb0e` |
| control `r2_coarse/system/snappyHexMeshDict` | `d13bbac350e032546546c0f228e45978b296ca2ae3428cc4bf581c17cca32ec3` |

Re-computed and compared before any verdict is believed; a mismatch is a REFUSAL.

## 6. Two C1 defects that are FIXED here, not merely noted

1. **`writeCellCentres` runs BEFORE the measurement.** C1's wrapper omitted it, so
   `stage_r2_measure.py` REFUSED on a missing `constant/C` — it refused rather than
   degraded, which is the discipline working, but the wrapper should not have made it
   necessary.
2. **`RUN_RC` IS WRITTEN AFTER THE MEASUREMENT, NEVER BEFORE**, and any consumer that
   cannot find the measurement **REFUSES — it never chooses.** C1's armed launcher read
   the verdict file before it existed and picked a spec with the reason "(b) unproven".
   It reached the correct answer for the wrong reason, which is the hardest version to
   catch. **An absent instrument result is not evidence for either branch.**
