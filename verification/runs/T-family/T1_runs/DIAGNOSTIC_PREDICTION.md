# T1c diagnostic: what is the 0.075–0.111 % excess that survives mesh refinement?

Written 2026-08-19, **before either diagnostic case was built or solved.**

## The observation being explained

Both arms of T1c converge at second order and both **overshoot the exact
constant in the limit of zero mesh spacing**:

| arm | Richardson h→0 | exact | excess |
| --- | ---: | ---: | ---: |
| constant `Ts` | 3.6608395 | 3.6567934 | **+0.1106 %** |
| constant `q″` | 4.3669013 | 4.3636364 | **+0.0748 %** |

**The excess is therefore not discretisation error** — it is what remains after
discretisation is extrapolated away. It is small, but it is the difference
between the constant-Ts row passing and failing: that row deviates 0.0865 %
against a GCI band of 0.0301 %.

## The two candidates, which happen to sit at the same order of magnitude

**A — axial conduction.** The Graetz solution that produces 3.6568 and 48/11
**neglects axial conduction**, valid as the Péclet number → ∞. These cases run at
**Pe = Re·Pr = 71**, and the neglected term is O(1/Pe²) = **0.0198 %**.

**B — the wedge chord.** An OpenFOAM wedge replaces the circular arc by a flat
chord. The relative geometric defect is O((θ/2)²) = (2.5° in radians)² =
**0.190 %**.

**Both are within a factor of five of the observed excess, so neither can be
chosen by magnitude alone.** They are separated by experiment instead.

## The design: two cases, each a SINGLE-parameter change from `L_q_f`

Both use the constant-flux arm, whose exact constant is the clean rational 48/11
and which has no saturation complication, on the finest mesh (26 112 cells),
`endTime` 30000.

| case | change | Pe | wedge | everything else |
| --- | --- | ---: | ---: | --- |
| `D_Pe` | **`Pr` 0.71 → 2.84** | 71 → **284** | 5° | identical |
| `D_wedge` | **wedge 5° → 1°** | 71 | **1°** | identical |

**Why `Pr` and not `Re` for the Péclet test, which is the point of the design:**
raising `Re` would change the velocity field, the entry length and the friction
simultaneously. Raising `Pr` at fixed `Re` leaves **the momentum solution
bit-for-bit unchanged** — same mesh, same `U`, same pressure gradient, same
station — so any change in Nusselt is attributable to the thermal transport
alone. The thermal entry length grows to 0.05·Re·Pr = 14.2 D, still far short of
the 40 D sampling station.

## REGISTERED PREDICTIONS

**If A (axial conduction) dominates:** `D_Pe` raises Pe by 4×, so an O(1/Pe²)
term falls by **16×**. The excess should drop from **+0.0748 %** to about
**+0.005 %**. `D_wedge` should show **no significant change**.

**If B (the wedge chord) dominates:** `D_wedge` reduces the angle by 5×, so an
O(θ²) term falls by **25×**. The excess should drop from **+0.0748 %** to about
**+0.003 %**. `D_Pe` should show **no significant change**.

**If both contribute**, both cases reduce the excess and neither reaches zero,
and the two reductions should approximately account for the total.

**The falsifying outcome, stated so it cannot be explained away afterwards: if
NEITHER case moves the excess materially, both hypotheses are wrong** and the
excess is something this study has not named — in which case the honest report is
that the constant-Ts GATE FAIL has **no identified cause**, not that it has a
plausible one.

## What this diagnostic does not do

**It does not change any T1c verdict.** Row L0 GATE FAILs at 0.0865 % against a
0.0301 % band whatever the cause turns out to be, and these two cases are
**diagnostic, not graded** — they have no registered band and cannot pass or
fail. Explaining a failure is not the same as excusing it.

---

# RESULTS, 2026-08-19 evening

Both cases ran to `endTime` 30000, `rc = 0`, and are **byte-identical between
checkpoints 28000 and 30000** — with the zero controlled by a **planted
1.234e-03 K perturbation** recovered exactly, not trusted. Neither is void on
convergence grounds.

| case | change | Pe | Nu | excess over 48/11 | vs baseline |
| --- | --- | ---: | ---: | ---: | ---: |
| `L_q_f` baseline | — | 71 | 4.365298 | **+0.0381 %** | — |
| `D_Pe` | `Pr` → 2.84 | **284** | 4.366688 | **+0.0699 %** | **1.84×** |
| `D_wedge` | wedge → 1° | 71 | 4.365298 | **+0.0381 %** | **1.000×** |

## B — the wedge chord: REFUTED, decisively

**Predicted a 25-fold reduction. Measured no change whatsoever.**

`Nu` = **4.365297870135518** baseline against **4.365297870133508** at a fifth of
the wedge angle — **identical to 12 significant figures**, with `f·Re` identical
to 9. **And the mesh genuinely changed**: `R_wall` 0.00999048 → 0.00999962,
`D_used`, near-wall spacing, `T_bulk` and `T_wall` all differ, and the wedge
patch angle reads 0.5° per patch against the baseline's 2.5°.

**The conclusion is stronger than "the wedge is not the cause".** An OpenFOAM
wedge is an **exact axisymmetric discretisation, not a chord approximation of a
3D sector**, so the solution is self-similar in `r/R_wall` and the wedge angle
cannot enter a dimensionless result at all. **This also retroactively confirms
the T1c fix**: reading `R_wall` from the mesh absorbed the entire geometric
effect, and there is nothing left over.

## A — axial conduction: NOT TESTED. The test was confounded, and the design error is mine.

**Predicted a 16-fold reduction. Measured a 1.84-fold INCREASE.** That is not a
refutation, because **the comparison does not isolate what it claimed to.**

The registered design argued `Pr` was a clean lever because raising it at fixed
`Re` **leaves the momentum solution untouched.** It does. **But leaving the
momentum field untouched is not the same as leaving the THERMAL RESOLUTION
untouched.** The thermal boundary layer scales as `Pr^(-1/3)`, so at `Pr` = 2.84
it is **1.59× thinner**, and T1c's radial mesh is **uniform** — `simpleGrading
(1 1 1)`, no wall clustering at all. A thinner thermal layer is therefore
resolved by proportionally fewer cells and **the fine-mesh discretisation error
grows.**

**A single-mesh comparison mixes the physical term with a changed discretisation
error and cannot decide between them.** The registered prediction compared
`D_Pe`'s single-mesh excess against the baseline's **Richardson-extrapolated**
excess of +0.0748 % — **comparing a value contaminated by discretisation against
one with discretisation removed.** That is not a like-for-like test and should
not have been registered as one.

**The repair, which needs no re-solve of `D_Pe`:** `D_Pe_c` and `D_Pe_m` give the
`Pr` = 2.84 arm its own three-level ladder, so its **`h → 0` excess** can be
compared against the baseline's **`h → 0` excess**. That is the comparison the
original design should have specified.

## What stands right now

- **The wedge contributes nothing.** Refuted at 12 significant figures.
- **Axial conduction is untested**, not confirmed and not refuted.
- **The T1c constant-`Ts` GATE FAIL therefore still has NO identified cause**,
  and per the falsifying clause registered above, **that is what gets reported
  until a test that actually isolates a mechanism says otherwise.**
- **No T1c verdict has moved and none can move on this.**

---

# AMENDED DESIGN, 2026-08-19 evening. Registered before any case was built.

## Two design errors in the original, both mine

**1. `Re` is the clean Péclet lever, not `Pr`, and I had it backwards.** For
fully developed **laminar** flow the velocity profile is exactly parabolic and the
constant-`q″` temperature profile shape is **Reynolds-independent in normalised
coordinates.** Changing `Re` therefore changes the Péclet number and **essentially
nothing about what the mesh has to resolve.** Changing `Pr` changes the thermal
layer thickness as `Pr^(-1/3)` — which is exactly the confound that voided the
first test. **The original reasoning — "raising `Pr` at fixed `Re` leaves the
momentum solution untouched" — was true and irrelevant.** What had to stay fixed
was not the momentum field but the resolution demand.

**2. The test suppressed the signal instead of amplifying it.** Raising Pe pushes
the predicted effect **down toward the discretisation floor**, where it cannot be
distinguished from numerical noise. **Lowering Pe raises it far above that
floor.**

## The amended test: a SCALING law, not a before-and-after

If axial conduction is the cause, the excess is `O(1/Pe²)` and must scale as
such across a sweep. Five points at the finest mesh, `Pr` = 0.71 throughout,
**`Re` the only quantity changed**:

| `Re` | Pe | `1/Pe²` relative to baseline | predicted excess if axial conduction |
| ---: | ---: | ---: | ---: |
| **25** | 17.75 | **16.0×** | **+1.197 %** |
| 50 | 35.50 | 4.0× | +0.299 % |
| 100 *(baseline)* | 71.00 | 1.0× | +0.075 % |
| 200 | 142.00 | 0.25× | +0.019 % |
| 400 | 284.00 | 0.062× | +0.005 % |

**At `Re` = 25 the predicted excess is +1.20 %, THIRTY TIMES the fine-mesh
discretisation error of about 0.04 %.** A single mesh suffices to detect a signal
that large, which is the whole point of amplifying rather than suppressing.

### REGISTERED PREDICTION

**If axial conduction is the cause, a log–log fit of excess against Pe over the
five points has slope −2**, and the `Re` = 25 point lands near +1.2 %.

**Falsifying outcomes, stated in advance:**
- **Slope ≈ 0** — the excess does not depend on Péclet at all, so axial
  conduction is refuted and the cause remains unidentified.
- **Slope significantly different from −2** — some other Péclet-dependent
  mechanism, and `1/Pe²` is the wrong form; the fitted slope is then the finding.
- **The `Re` = 400 point failing its development check** — at `Re` = 400 the
  hydrodynamic entry length is 20 D against a 40 D station, the tightest margin
  in the sweep, so `Nu` is measured at **30 D and 40 D** and the point is
  **discarded** if those disagree by more than the excess being measured.

**Still diagnostic, still not graded. No T1c verdict moves on this.**

---

# RESULTS OF THE AMENDED DESIGN, 2026-08-20

## Convergence, and one point carried with its drift disclosed

Every zero below is controlled by a **1.234e-03 K perturbation planted by line
index into the earlier checkpoint and read back off disk before the reader is
asked anything.** The control caught two of its own faults before it caught
anything else: the first version demanded the reader return exactly the plant
and so declared `D_Re25` BROKEN for really moving 2.761e-01 K, and the second
version located the internal field by looking for a numeric line whose
predecessor was all digits — but an OpenFOAM field is `<count>`, then `(`, then
the values, so nothing was ever planted and a perfectly good reader was reported
BROKEN on a genuine zero. **A control that is not itself controlled is
decoration.**

| case | max change, 28000 → 30000 | state |
| --- | ---: | --- |
| `D_Re25` | 2.761e-01 K | **NOT CONVERGED** |
| `D_Re50` | 0.000e+00 | CONVERGED |
| `L_q_f` | 0.000e+00 | CONVERGED |
| `D_Re200` | 0.000e+00 | CONVERGED |
| `D_Re400` | 0.000e+00 | CONVERGED |

`D_Re25` is **kept, with its drift located and quantified rather than waved
through**. All five largest changes are in the outlet cell column at x/D = 50.00;
within 1 D of the 40 D measuring station the largest change is 1.324e-04 K. Its
**Nusselt number moves 2.211e-05 between the last two checkpoints, against an
excess being measured of 1.662e-03 — a factor of 75.** The point is used; the
drift is on the record.

## The measurement

| case | Re | Pe | Nu | excess over 48/11 | f·Re |
| --- | ---: | ---: | ---: | ---: | ---: |
| `D_Re25` | 25 | 17.73 | 4.365298 | **+0.0381 %** | 63.9877 |
| `D_Re50` | 50 | 35.47 | 4.365298 | **+0.0381 %** | 63.9877 |
| `L_q_f` | 100 | 70.93 | 4.365298 | **+0.0381 %** | 63.9877 |
| `D_Re200` | 200 | 141.86 | 4.365305 | **+0.0382 %** | 63.9984 |
| `D_Re400` | 400 | 283.73 | 4.369223 | +0.1280 % | 64.4809 |

**`D_Re400` is DISCARDED under the clause registered for it**: Nu at 30 D and
40 D differ by 0.3581 pp, which exceeds the 0.1280 pp excess being measured. At
Pe = 284 the 40 D station is only 0.141 thermal development lengths in, so the
point is still developing. That was registered as the tightest margin in the
sweep and it failed exactly there.

## A — axial conduction: REFUTED on this arm

**Registered prediction: slope −2, and the Re = 25 point near +1.20 %.**

| | predicted | measured |
| --- | ---: | ---: |
| log–log slope of excess against Pe | **−2** | **+0.0017 ± 0.0011** |
| excess at Re = 25 | **+1.197 %** | **+0.0381 %** |

The fitted slope is **1894 standard errors from −2**, and the Re = 25 point is
**31 times smaller** than predicted. The registered falsifying outcome
"slope ≈ 0 → axial conduction is refuted" has fired.

The measurement is blunter than the fit makes it sound. **Nu is 4.365298 at
Re = 25, 50 and 100 — identical to seven significant figures across a 16-fold
change in 1/Pe² — with f·Re identical to 63.9877 at all three.** There is no
small effect to fit. There is no effect.

## Why there is no effect, which the design should have foreseen

For **fully developed flow with a constant wall flux**, the temperature rises
linearly in x at every radius: T(x, r) = T_wall(x) + g(r) with dT_wall/dx
constant. Therefore **∂²T/∂x² ≡ 0, and the axial conduction term is not small —
it is identically zero.** Measured over 202 stations in the developed window,
near-wall row:

| | `L_q_f` (constant q″) | `L_Ts_f` (constant Ts) |
| --- | ---: | ---: |
| dT/dx | +28.196 K/m, spread 4.7e-06 | +1.86e-03 K/m, spread 7.5e-03 |
| ∂²T/∂x² | **−1.23e-05 K/m²** | **−1.91e-02 K/m²** |
| α·∂²T/∂x² ÷ u·∂T/∂x | **1.2e-10** | **2.9e-03** |

**The diagnostic was run on the one arm where the mechanism it was testing
cannot act, and it was chosen for that arm because 48/11 is a clean rational
reference and it has no saturation complication.** Convenience of the reference
picked the arm; nobody checked whether the hypothesis was alive there. It was
not.

## The repaired Pr test agrees, from the other direction

The `Pr` = 2.84 arm now has its own three-level ladder, so h→0 can be compared
against h→0 — the like-for-like comparison the original design failed to make.

| arm | Pe | coarse | medium | fine | p | Richardson | **h→0 excess** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pr = 0.71 | 71 | +0.2492 % | +0.0968 % | +0.0381 % | 2.031 | 4.3669013 | **+0.0748 %** |
| Pr = 2.84 | 284 | +0.3444 % | +0.1346 % | +0.0699 % | 2.506 | 4.3679436 | **+0.0987 %** |

Raising Pe fourfold was predicted to cut the excess sixteenfold, to about
+0.005 %. **It increased it by 1.32×.** Caveat, stated rather than buried: the
Pr arm's observed order is 2.506 against the baseline's 2.031, above formal
second order, which usually means its coarsest level is outside the asymptotic
range — so its Richardson value is indicative, not exact.

## What the two levers say together

**The excess does not depend on Re at all** (identical to seven figures over
Re = 25–200) **and does depend on Pr** (+0.0748 % → +0.0987 %). A quantity that
varies with Pr at fixed Re, and not at all with Re at fixed Pr, **is not a
function of Pe = Re·Pr.** Péclet number is refuted as the governing parameter by
two independent levers that were designed to move it in the same direction.

## Standing verdict

- **The wedge contributes nothing** — refuted at 12 significant figures (above).
- **Axial conduction is refuted for the constant-flux arm**, empirically and
  analytically.
- **It has never been tested on the constant-Ts arm**, where ∂²T/∂x² is seven
  orders of magnitude larger and the ratio to convection is 2.9e-03 — the right
  order of magnitude for the +0.111 % excess that the GATE FAIL turns on.
- **The T1c constant-Ts GATE FAIL therefore still has NO identified cause**, per
  the falsifying clause registered before any of this ran. What has changed is
  that the candidate is now located on the arm where it can act, instead of
  being refuted on the arm where it cannot.
- **No T1c verdict has moved and none can move on this.**

---

# NEXT TEST, REGISTERED BEFORE IT IS BUILT, 2026-08-20

**`D_Ts_Re25/50/200`: the Re sweep, on the constant-Ts arm.**

The station cannot be held at 40 D: on the constant-Ts arm the driving
difference decays as exp(−4·Nu·x / (D·Re·Pr)), so a fixed physical station sits
at a different point of the decay for every Re, and at low Re it lands in the
saturated region where Nu is round-off over round-off. **The station moves with
Re** by `analyse_t1c.amended_station`, which places it at the geometric centre of
the window where the driving difference is between 100 % and 10 % of its inlet
value — the same rule already used and already committed for T1c.

**REGISTERED PREDICTION.** If axial conduction is the cause of the constant-Ts
excess, the h→0 excess scales as 1/Pe², so a log–log fit against Pe over
Re = 25, 50, 100, 200 has **slope −2**, and Re = 25 (Pe = 17.7, 16× the
baseline's 1/Pe²) lands near **+1.78 %** against the baseline's +0.111 %.

**Falsifying outcomes, registered in advance:**
- **slope ≈ 0** — axial conduction is refuted on the constant-Ts arm too, and the
  excess is then unexplained on **both** arms, which is the end of this line of
  inquiry and gets reported as such.
- **slope far from −2** — the fitted slope is the finding, and 1/Pe² is the wrong
  form.
- **any case whose driving difference at its own station falls below the 10 %
  saturation floor is DISCARDED**, not rescued by moving its station again.

Each Re needs its own three-level ladder for an h→0 excess, so this is 12 cases,
not 4. **Still diagnostic, still ungraded, and no T1c verdict can move on it.**
