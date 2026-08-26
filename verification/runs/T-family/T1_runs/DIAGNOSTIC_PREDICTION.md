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

---

# RESULTS OF THE CONSTANT-Ts Re SWEEP, 2026-08-20 evening

Instrument: `analyse_dts.py`, written after the nine `D_Ts_*` cases had solved
but importing the frozen `analyse_t1c.py` for every number it reports — the
station rule, the measurement, the GCI and the planted-zero control are the
committed ones, not new ones. Output: `dts.json`.

## Completion and convergence, before anything is measured

All nine `D_Ts_*` cases met the strict rule (`rc = 0`, `End` in `log.solve`,
last time directory = `endTime` = 30000 holding `T U p_rgh alphat phi`, one
`ExecutionTime` line per iteration, every field newer than `0/T`) and got a
`DONE` marker; the Re = 100 ladder `L_Ts_c/m/f` already had its markers from
T1c. **All twelve cases are bit-identical between checkpoints 28000 and 30000**
(max change 0.000e+00 K), and on every one of the twelve the **planted
1.234e-03 K perturbation was recovered** by the reader (`PES.planted_zero_control`,
planting by line index and reading back from disk). Nothing is void on
convergence grounds and nothing is carried with a drift.

**No case is DISCARDED.** The driving difference at each case's own station is
0.117–0.132 of its inlet value, above the registered 0.10 floor on every level
of every ladder. All four grid triples are CONVERGING, so all four Re points
carry an h→0 excess.

## The measurement, each Re at its own station

| Re | Pe | station x/D | Nu coarse | Nu medium | Nu fine | p | GCI | Richardson | **h→0 excess** | fine excess |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 25 | 17.75 | 2.227 | 3.681432 | 3.675830 | 3.675264 | 4.88 | 0.0022 % | 3.675328 | **+0.5068 %** | +0.5051 % |
| 50 | 35.50 | 4.454 | 3.667528 | 3.664146 | 3.663023 | 2.35 | 0.0191 % | 3.663581 | **+0.1856 %** | +0.1704 % |
| 100 | 71.00 | 8.908 | 3.664111 | 3.661183 | 3.659958 | 1.85 | 0.0301 % | 3.660840 | **+0.1106 %** | +0.0865 % |
| 200 | 142.00 | 17.816 | 3.663260 | 3.660368 | 3.659208 | 1.94 | 0.0265 % | 3.659985 | **+0.0873 %** | +0.0660 % |

`f·Re` on the fine level is 63.9877 at Re = 25, 50 and 100 and 63.9984 at
Re = 200, CONVERGING at p ≈ 2.0 on every ladder: the momentum solution did not
move across the sweep.

**The Re = 25 observed order of 4.88 is not believed**, and is reported rather
than used: the nearest cell centres to the 2.227 D station sit at 2.127 / 2.268
/ 2.199 D on c/m/f, the excess varies by about −0.32 pp per D there, and the
station offset contributes −0.022 pp to a medium-to-fine difference of
+0.016 pp. The Richardson value is nevertheless within 1e-4 of the fine value,
so the h→0 excess at Re = 25 is insensitive to this; its 0.002 % GCI is not. At
the other three Re the station offset is under a tenth of the level-to-level
differences.

## The registered prediction against what was measured

| | registered | measured |
| --- | ---: | ---: |
| log–log slope of h→0 excess against Pe | **−2** | **−0.836 ± 0.176** (R² = 0.918) |
| h→0 excess at Re = 25 | **+1.78 %** | **+0.507 %** |
| Re = 25 relative to Re = 100 | 16× | 4.58× |

The fitted slope is **6.6 standard errors from −2 and 4.7 standard errors from
zero.** The secondary fit on the fine-mesh excess alone gives −0.978 ± 0.186,
5.5 standard errors from −2. Independently re-fitted by the supervisor from the
four Richardson values: −0.8359 ± 0.1763, the same.

## Verdict, by the clauses registered before the cases were built

- **"Slope ≈ 0 → axial conduction refuted on the constant-Ts arm too" did NOT
  fire.** The excess on this arm depends on Péclet number — unlike the
  constant-flux arm, where Nu was identical to seven figures over the same Re
  range. That is the first positive Péclet dependence this line of inquiry has
  produced, and it is on the arm where the mechanism can act.
- **"Slope far from −2 → the fitted slope is the finding, and 1/Pe² is the wrong
  form" FIRED.** The registered prediction of a pure O(1/Pe²) scaling is
  rejected at 6.6 standard errors, and the Re = 25 point is 3.5 times smaller
  than predicted.
- **No case was discarded**, so the third clause did not arise.

**The finding is therefore the slope, −0.84 ± 0.18, and the form it rejects.**
It does not name the mechanism. The adjacent-pair slopes are −1.45 (Re 25→50),
−0.75 (50→100) and −0.34 (100→200): the four points steepen towards low Pe and
flatten towards high Pe, which is **not the signature of any single power law**,
and the R² of 0.918 with structured residuals says the same.

## Exploratory, post hoc, NOT registered and NOT a verdict

Because the local slope runs from −0.34 to −1.45, a two-term form was tried
after the fact. A **Pe-independent floor plus a 1/Pe² term**, excess = A + B/Pe²,
fits the four Richardson values to an RMS residual of **0.0017 pp** with
**A = +0.082 %** and B = 134 %·Pe² (leave-one-out A = 0.080–0.083 %); the
alternative A + B/Pe fits to 0.033 pp RMS, twenty times worse. Read as a
hypothesis and nothing more: **the constant-Ts excess looks like a floor of
about +0.08 % that does not depend on Pe, with a 1/Pe² term on top** — the
registered form, but sitting on a floor the registration did not allow for. The
floor is numerically close to the constant-flux arm's Re-independent h→0 excess
of +0.0748 %, which the previous round found depends on Pr and not on Re.
**That coincidence is noted, not claimed.** A model chosen after seeing four
points, with two free parameters, fitting four points, is not evidence; it is a
prediction for the next test, and it is registered as one below.

## The Graetz entry residual at the station, computed rather than recalled

The station rule puts every Re at x* = x/(D·Pe) ≈ 0.1255, so whatever
thermal-entry residual remains there is common to all four points — but its
size still matters for the floor. A Crank–Nicolson march of the classical Graetz
problem (parabolic flow from the inlet, no axial conduction), verified to
reproduce 3.6567934 at x* = 0.5 to 1.6e-6 and the bulk decay slope −2λ₀² =
−14.627 to 1.2e-6, with a grid-halving change of 5e-6, gives a local excess at
x* = 0.1255 of **+0.0051 %** — +0.0057 / +0.0051 / +0.0049 / +0.0050 % at the
actual fine sample points of Re = 25 / 50 / 100 / 200. **The station is clear
of the thermal entry by a factor of sixteen against the smallest excess
measured.** Subtracting it moves the slope to −0.859 ± 0.177; nothing changes.

**What the same computation rules out is the x-dependence.** Across the
admissible window Graetz decays from +0.034 % (x* = 0.10) to +0.0003 %
(x* = 0.157), a drop of 0.034 pp. The cases drop 0.315 / 0.174 / 0.145 /
0.133 pp over the same window — four to nine times steeper. **The decline of Nu
along x that the station sensitivity shows is not thermal entry development.**
Something else is still developing along the pipe at 1.4–2.2 nominal
hydrodynamic entry lengths, and the slug inlet velocity profile is the named
candidate (see "cannot see", item 1, and the next test). The c/m/f station
mismatch, put through the same curve, contributes at most 0.0036 pp to any
level-to-level difference, 2 % of the smallest one it enters.

## Addendum, 2026-08-20 evening: two independent checks of the above

Two verification agents, briefed separately and using different numerical
methods, re-derived the numbers in this section after it was drafted.

- **Measurement**: re-running the frozen `analyse_t1c.measure` at
  `amended_station` reproduces every Nu in `dts.json` bit for bit; the log–log
  slope refits to −0.8359 ± 0.1763 in both hands.
- **Graetz residual**: a second solver (L-stable BDF2 march, cross-checked
  against a 40-eigenpair shift-invert expansion whose first five eigenvalues
  match Graetz's 2.704364 / 6.679032 / 10.67338 / 14.67108 / 18.66987 to
  1e-5) gives +0.00522 % at x* = 0.1255 against the +0.0051 % above. Its
  first attempt, a Crank–Nicolson march, was wrong at large x* (Nu = 4.93 at
  x* = 1 from parasitic non-decaying modes) and was discarded before any
  number was reported — which is why the verification checks are stated
  beside the numbers.
- **The Re = 25 observed order**: correcting the c/m/f Nusselt differences for
  the station mismatch using the measured fine-level x-slope (−0.32 pp/D)
  takes the Re = 25 order from 4.88 to **2.25**, and the other three ladders
  to 2.13 / 2.15 / 2.10. The 4.88 was a station-mismatch artefact, as the
  section above suspected; the Re = 25 h→0 excess changes by 0.002 pp under
  the correction and its 0.002 % GCI should be read as understated.
- **Still exploratory**: leaving the exponent free in excess = A + B·Pe^s
  lands at **s = −2.03** with A = +0.083 % on the h→0 values (one degree of
  freedom) and at s = −2.003 with A = +0.059 % on the fine-level values (RMS
  0.00015 pp). The floor differs between the fine level and h→0 (0.059 against
  0.082 %), so it carries its own mesh dependence. Four points and three
  parameters remain four points and three parameters; the registered next
  test, not this fit, decides.

## Heat-balance closure, every case

Computed from the written fields and the mesh read from `polyMesh/points`,
`faces`, `owner`, `boundary` — face areas validated against the wedge's chord
geometry to 2e-16 (wall strip `L·2R_wall·tan(θ/2)`, inlet triangle
`R_wall²·tan(θ/2)`, θ = 5.000000° read from the points) before any flux was
summed. Kinematic units (W per ρc_p).

| case | Q_wall | Q_inlet,cond / Q_wall | closure residual (Q_wall + Q_inlet,cond − Q_conv,net) / Q_wall |
| --- | ---: | ---: | ---: |
| `D_Ts_Re25_c` | 9.502e-07 | −14.01 % | +2.3e-10 |
| `D_Ts_Re25_m` | 9.834e-07 | −16.91 % | +5.3e-10 |
| `D_Ts_Re25_f` | 1.019e-06 | −19.80 % | +1.2e-09 |
| `D_Ts_Re50_c` | 1.739e-06 | −6.01 % | +2.4e-10 |
| `D_Ts_Re50_m` | 1.766e-06 | −7.48 % | +5.5e-10 |
| `D_Ts_Re50_f` | 1.796e-06 | −9.00 % | +1.3e-09 |
| `L_Ts_c` | 3.346e-06 | −2.33 % | −8.6e-13 |
| `L_Ts_m` | 3.369e-06 | −2.98 % | +5.4e-10 |
| `L_Ts_f` | 3.394e-06 | −3.70 % | +1.3e-09 |
| `D_Ts_Re200_c` | 6.565e-06 | −0.85 % | −8.6e-14 |
| `D_Ts_Re200_m` | 6.582e-06 | −1.11 % | +1.2e-11 |
| `D_Ts_Re200_f` | 6.602e-06 | −1.42 % | +1.2e-09 |

**Every case closes to 1.3e-09 or better**; mass flux in and out agree to
1e-13; the phi-weighted outlet bulk temperature equals the last cell column's
U- and V-weighted bulk to 1e-13 K; `alphat` is identically zero everywhere (the
solution is laminar as declared). The naive column cross-check
`ṁ(T_b,last − T_b,first)` under-reads by 6–26 % only because the first cell
column, half a cell from the inlet, is already 0.6–2.6 K above T_in — the same
fact as the next paragraph.

**The inlet plane carries a conduction flux against the flow, and it grows
with refinement.** It is −14.0 / −16.9 / −19.8 % of the wall heat input at
Re = 25 on c/m/f, −6.0 / −7.5 / −9.0 % at Re = 50, −2.3 / −3.0 / −3.7 % at
Re = 100, −0.85 / −1.11 / −1.42 % at Re = 200. It grows like log(1/h): the
inlet is `fixedValue 300 K` and the wall `fixedValue 310 K`, so the corner cell
sees a 10 K jump over a distance that halves with every refinement. **This is
axial conduction, and it is the inlet boundary condition's, not the developed
pipe's**: the extended-Graetz problem of the literature has an unheated upstream
section into which the fluid may conduct, and these cases do not. The wall flux
rises by exactly the same amount, because the outlet bulk is saturated at the
wall temperature in every case and Q_conv,net = ṁ·10 K is fixed.

## Station sensitivity, reported and never used to discard

On the fine level the excess falls monotonically across the admissible window
at every Re: from the 100 %-of-window bound to the 10 % bound it drops
0.315 / 0.174 / 0.145 / 0.133 pp at Re = 25 / 50 / 100 / 200, which is 0.62,
0.94, 1.31 and 1.52 times the h→0 excess being measured. The station rule fixes
x* = x/(D·Pe) = 0.1255 at every Re, so this sensitivity is the same kind of
thing at every point and does not bias the comparison across Re — but it is of
the order of the signal and the registration did not anticipate it.

## What this result cannot see

1. **Which Péclet-dependent mechanism it is.** The Re lever moves Pe, but at
   low Re it also moves the hydrodynamic development: the inlet is a uniform
   slug, the station is 1.76–1.79 nominal hydrodynamic entry lengths down at
   every Re, and the centreline velocity there is 1.9942 / 1.9958 / 1.9963 /
   1.9964 times the bulk at Re = 25 / 50 / 100 / 200 against 1.99966 for the
   exact parabola at that cell — a 0.29 % deficit at Re = 25 against 0.18 % at
   Re = 200, because the creeping-flow correction to the entry length grows as
   Re falls. A fuller profile raises Nu, and the Nu decline along x across the
   window is four to nine times steeper than thermal entry allows, which is
   what a profile still filling out would do. **Thermal axial conduction and
   hydrodynamic under-development both scale the right way with Re and this
   sweep cannot separate them.**
2. **Whether the Pe-dependent part lives in the developed pipe or at the inlet
   corner.** The inlet conduction flux is mesh-dependent and does not converge,
   so part of what is measured downstream may be the corner singularity's
   upstream reach rather than the developed-flow axial-conduction eigenvalue
   shift of the extended Graetz problem.
3. **The floor.** Whatever sits under the Pe term — about +0.08 % if the
   post-hoc form is right — is exactly the size of the T1c constant-Ts GATE FAIL
   (0.0865 % against a 0.0301 % band), and this sweep says nothing about what
   it is, only that it does not move with Re.
4. **Anything graded.** No band, no verdict, no T1c row moves.

## Cost

Nine serial solves, 14 419 s of wall = **4.00 core-hours, $0.21** at
$0.0513/core-hour, plus about 25 s of post-processing per analysis run.

## Standing verdict

- **The wedge contributes nothing** (refuted at 12 significant figures).
- **Axial conduction is refuted on the constant-flux arm** (empirically and
  analytically).
- **On the constant-Ts arm the excess IS Péclet-dependent, with a fitted
  log–log slope of −0.84 ± 0.18 — the registered pure 1/Pe² form is rejected at
  6.6 σ, and the slope is the finding.**
- **The T1c constant-Ts GATE FAIL still has NO identified cause.** The part of
  the excess that does not move with Re is the part the GATE FAIL turns on, and
  it is unexplained on both arms.
- **No T1c verdict has moved and none can move on this.**

---

# NEXT TEST, REGISTERED BEFORE IT IS BUILT, 2026-08-20 evening

**`D_Ts_Re25_P` and `L_Ts_P`: the same two ladders with a PARABOLIC inlet
velocity profile** (`fixedProfile`/coded Poiseuille `U = 2U_b(1 − (r/R)²)` at
the inlet; T inlet, wall, mesh, Re, Pr, station rule all unchanged). Six cases,
about 2.5 core-hours. With a parabolic inlet there is no hydrodynamic
development at all, so the first thing this result cannot see is removed by
construction, and the configuration becomes exactly the Graetz one (thermal
entry only) that the reference 3.6567934 describes.

**REGISTERED PREDICTIONS, both ladders compared h→0 against h→0 at the same
stations:**

- **If the Pe-dependent part is thermal (axial conduction) and the floor is not
  hydrodynamic:** the Re = 25 h→0 excess stays at **+0.51 %** and the Re = 100
  one at **+0.11 %**, each within its own GCI band of the slug-inlet value, and
  their difference stays near 0.40 pp.
- **If the Pe-dependent part is hydrodynamic under-development:** the Re = 25
  excess falls towards the Re = 100 value and the difference shrinks to well
  under 0.40 pp — by how much is not predicted, only the direction.
- **If the floor is hydrodynamic:** the Re = 100 excess falls from +0.11 %
  towards the Graetz entry residual at x* = 0.1255 quoted above.

**Falsifying outcomes, registered now:** if both excesses move by less than
their GCI bands, the hydrodynamic explanation is refuted for both the floor and
the Pe term, and the inlet-corner hypothesis (item 2 above) is next. If the
post-hoc floor + 1/Pe² form is right and hydrodynamics are not involved, the
Re = 25 parabolic-inlet point lands at **+0.082 % + 134/17.75² = +0.507 %**; if
it lands elsewhere, that form is dropped without a replacement being fitted to
the same four points again.

**Still diagnostic, still ungraded, and no T1c verdict can move on it.**

---

# RESULTS OF THE PARABOLIC-INLET TEST, 2026-08-21

Six cases, `D_Ts_Re25_P_c/m/f` and `L_Ts_P_c/m/f`, built by `build_d_ts_p.py`
from the frozen `build_t1c.py` generators: `polyMesh/points`, `faces`,
`owner`, `neighbour` and `boundary` are **byte-identical** to the slug-inlet
cases (`cmp`), radial spacing uniform to 2e-15 from the points, 4000 / 10240 /
26112 cells, R_wall = 0.0099904822 from the points, and a recursive diff against
the slug case shows **only `0.orig/U` and `0/U` differ**. The inlet is a
`fixedValue nonuniform List<vector>` with U_x = s·2U_b·(1 − (r_c/R_wall)²) at
each inlet face centroid read from the mesh, s the single scalar that makes the
discrete flow rate equal U_b·A_inlet exactly (s − 1 = −4.2e-4 / −1.6e-4 /
−6.4e-5 on c/m/f; the flow rate was exact on the slug inlet, so flow-rate-exact
is the like-for-like choice; re-read from disk, the flow rate matches to 0
relative). No runtime-compiled code.

Instrument: `analyse_dts_p.py`, reusing `analyse_dts.py`'s machinery on the two
new ladders, sha256 `caec3804…a74615`. **One disclosed amendment before any
answer existed**: at 21:11:40Z on 2026-08-20, with no `STATUS` or `DONE` file
for any `_P_` case (checked and recorded in its docstring), the "unchanged
within its own GCI band" criterion was changed from the slug GCI alone to
**max(slug GCI, parabolic GCI, station-corrected slug band)**, because the
Re = 25 slug GCI of 0.0022 % is the station-mismatch artefact recorded in the
addendum above (corrected order 2.25 → band 0.0249 %; Re = 100 corrected
0.0240 %, below its raw 0.0301 %). All three bands are printed beside every
difference. Pre-amendment hash `568f09e0…47df19`.

## Completion, convergence, and proof that the lever worked

All six met the strict rule and got markers; all six are **bit-identical
between 28000 and 30000** with every planted 1.234e-03 K control recovered;
none is discarded (driving fractions 0.130–0.152, floor 0.10). At the station
the centreline cell carries **U_cl/U_b = 1.99887 (Re 25) and 1.99886 (Re 100)
against 1.99966 for the exact parabola at that cell** — −0.04 % — where the
slug cases had 1.9942 and 1.9963; the maximum deviation of the whole profile
from the parabola at the station is 7.9e-4 (rms 2.9e-4). In the inlet-adjacent
column the centreline reads +0.27 % above the parabola on the fine mesh
(+0.84 % coarse): the face-centroid list relaxes into the discrete parabola
over the first cells. Disclosed; it is gone by the station.

## The measurement, same stations, same estimator, same reference

| Re | inlet | Nu coarse | Nu medium | Nu fine | p | GCI | Richardson | **h→0 excess** | fine excess |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 25 | slug | 3.681432 | 3.675830 | 3.675264 | 4.88 | 0.0022 % | 3.675328 | +0.5068 % | +0.5051 % |
| 25 | **parabolic** | 3.678705 | 3.673683 | 3.672582 | 3.23 | 0.0105 % | 3.672891 | **+0.4402 %** | +0.4318 % |
| 100 | slug | 3.664111 | 3.661183 | 3.659958 | 1.85 | 0.0301 % | 3.660840 | +0.1106 % | +0.0865 % |
| 100 | **parabolic** | 3.662825 | 3.659835 | 3.658649 | 1.97 | 0.0267 % | 3.659429 | **+0.0721 %** | +0.0507 % |

`f·Re` is unchanged at 63.9203 / 63.9688 / 63.9877 on every ladder. The Re = 25
parabolic order of 3.23 carries the same station-mismatch caveat as the slug
4.88 and is not believed; the Richardson value is within 3e-4 of the fine value.

| | slug | parabolic | change | bands: slug GCI / parabolic GCI / corrected slug | band used | change ÷ band |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| Re = 25 h→0 excess | +0.5068 % | +0.4402 % | **−0.0666 pp** | 0.0022 / 0.0105 / 0.0249 % | 0.0249 % | **2.67** |
| Re = 100 h→0 excess | +0.1106 % | +0.0721 % | **−0.0386 pp** | 0.0301 / 0.0267 / 0.0240 % | 0.0301 % | **1.28** |
| Re 25 − Re 100 | +0.3962 pp | +0.3681 pp | −0.0281 pp | combined 0.0551 pp | | 0.51 |

## The registered predictions, taken literally

- **(1) "thermal Pe term, non-hydrodynamic floor: both stay, each within its
  own band, difference near 0.40 pp" — NOT met.** Both excesses moved by more
  than their bands (2.67× and 1.28×).
- **(2) "hydrodynamic Pe term: Re 25 falls towards Re 100, the difference
  shrinks to well under 0.40 pp" — NOT met.** The difference went 0.396 →
  0.368 pp, a change of 0.028 pp inside the 0.055 pp resolution of the
  comparison. **The Péclet-dependent part of the excess is not hydrodynamic.**
- **(3) "hydrodynamic floor: Re 100 falls from +0.11 % towards the Graetz
  residual" — MET in direction, not in full.** The Re = 100 excess fell from
  +0.1106 to +0.0721 %, closing **36.5 % of the gap** to the +0.0051 % Graetz
  residual. About a third of the floor was the slug inlet's hydrodynamic
  development; **two-thirds of it is not.** The Re = 25 point fell by a
  comparable amount (−0.067 pp against −0.039 pp, the 0.028 pp difference inside
  resolution), which is what a common floor shift looks like.
- **Falsifier "both move by less than their bands → hydrodynamics refuted for
  both" did not fire.**
- **Falsifier "post-hoc floor + B/Pe² lands the parabolic Re 25 at +0.507 %;
  elsewhere → the form is dropped" FIRED.** Measured **+0.4402 %**, 0.067 pp
  from the prediction against a parabolic GCI of 0.0105 %. **The floor + 1/Pe²
  form is dropped**, and per the clause no replacement is fitted to the same
  points.

## What else the test showed, reported

- **The decline of Nu along x was mostly hydrodynamic.** Across the admissible
  window the fine-level excess now drops 0.151 pp at Re 25 (slug 0.315) and
  **0.041 pp at Re 100 (slug 0.145) — within 0.007 pp of the 0.034 pp the
  Graetz curve predicts.** At Re = 100 with a parabolic inlet, the x-dependence
  is thermal entry and nothing else. At Re = 25 the 0.151 pp that remains is
  five times Graetz and is Péclet-dependent: **the entry region at low Pe is
  longer than Graetz says**, which is what axial conduction does to a thermal
  entry.
- **Heat balance**, from the mesh as before (face geometry VALID on all six):

| case | closure residual | Q_inlet,cond / Q_wall | slug closure | slug Q_inlet,cond / Q_wall |
| --- | ---: | ---: | ---: | ---: |
| `D_Ts_Re25_P_c` | +2.6e-10 | −13.55 % | +2.3e-10 | −14.01 % |
| `D_Ts_Re25_P_m` | +5.8e-10 | −16.92 % | +5.3e-10 | −16.91 % |
| `D_Ts_Re25_P_f` | +1.4e-09 | −20.48 % | +1.2e-09 | −19.80 % |
| `L_Ts_P_c` | −8.9e-14 | −2.55 % | −8.6e-13 | −2.33 % |
| `L_Ts_P_m` | +5.9e-10 | −3.38 % | +5.4e-10 | −2.98 % |
| `L_Ts_P_f` | +1.4e-09 | −4.38 % | +1.3e-09 | −3.70 % |

  Every case closes to 1.4e-09 or better; mass flux in and out agree to 1e-14.
  The inlet-plane conduction flux is unchanged in size and still grows with
  refinement: **the corner singularity is a property of the thermal inlet
  condition and did not care about the velocity profile.**

## Standing after this test

- Of the slug-inlet constant-Ts excess, **the Péclet-dependent part (+0.37 pp
  between Re 25 and Re 100) is thermal**: it survived the removal of all
  hydrodynamic development. **Axial conduction remains the only named
  candidate for it, still not demonstrated**, and its form is not
  floor + 1/Pe² (dropped above).
- **Of the Re-independent floor, about a third was the slug inlet** and is now
  gone; **+0.072 % (h→0) remains at Re = 100 with a parabolic inlet**, fourteen
  times the Graetz residual, unexplained.
- **No T1c verdict moves.** For the record and not as a grade: even with the
  parabolic inlet the fine-level Re = 100 deviation is 0.0507 % against a GCI
  band of 0.0267 %, so a graded row would still GATE FAIL on the slug inlet's
  removal alone.

## What this test cannot see

1. **Corner versus pipe.** Developed-flow axial conduction and the inlet-corner
   conduction flux are both thermal and both Péclet-dependent; removing the
   velocity development separates neither from the other. Only an unheated
   upstream section can.
2. **The remaining two-thirds of the floor.**
3. **Its own inlet's discretisation**: the face-centroid list with its
   flow-rate scale s and the +0.27 % first-column overshoot are inside the
   ladder and are extrapolated away only as far as the ladder's order is real —
   and at Re = 25 the order is a station artefact at both inlets.
4. **Anything graded.**

## Cost

Six serial solves, 17 729 s of wall = **4.92 core-hours, $0.25** at
$0.0513/core-hour — on a box shared with another team's training jobs
(load 33 on 16 cores), so the CPU time was 10 195 s = 2.83 core-hours; the
wall figure is the one billed.

---

# NEXT TEST, REGISTERED BEFORE IT IS BUILT, 2026-08-21

**An unheated upstream section**: `D_Ts_Re25_U` and `L_Ts_U` ladders with the
parabolic inlet moved to x = −10 D, the wall **adiabatic** for −10 D < x < 0 and
at 310 K for x > 0, T_in = 300 K at the upstream inlet, stations unchanged
(measured from x = 0). The 300 K / 310 K corner no longer exists; whatever
conducts upstream does so into fluid, as in the extended-Graetz configuration
of the literature. Six cases, about 5 core-hours at the longer domain.

**REGISTERED PREDICTIONS, h→0 against h→0 at the same stations:**

- **If the Péclet-dependent term is the inlet-corner flux**, the Re 25 − Re 100
  difference collapses from +0.37 pp towards the combined bands (about
  0.05 pp), and the conduction through the x = 0 plane becomes
  mesh-independent across c/m/f.
- **If it is developed-flow axial conduction**, the difference persists within
  the combined bands of +0.37 pp, and the conduction through the x = 0 plane
  is mesh-independent as well — the corner was the only mesh-dependent thing.
- **If the remaining Re = 100 floor (+0.072 %) does not move** by more than its
  band, it is not an entrance effect of any kind, hydrodynamic or thermal.

**Falsifying outcomes, registered now:** if the difference persists AND the
x = 0 conduction flux stays mesh-dependent, the corner hypothesis survives in a
form this design cannot kill and the line is reported as unresolved. If the
difference persists, the comparison value for developed-flow axial conduction
at Pe = 17.75 and 71 is to be **obtained from a cited extended-Graetz source
and checked against its own asymptotes before use** — never recalled. **Still
diagnostic, still ungraded, and no T1c verdict can move on it.**

---

# DATED ADDENDUM (2026-08-24): the h→0 excesses in this file carry an inverted Richardson sign

**Appended at the foot. Lines whose number changed above this section: 0** —
verified by byte-comparing everything above against
`git show HEAD:verification/runs/T-family/T1_runs/DIAGNOSTIC_PREDICTION.md`.
**No registered prediction, band or threshold in this file is altered, and no
T1c verdict moves** — this file states, and it remains true, that everything in
it is diagnostic and ungraded.

`analyse_t1c.py:337` (imported by `analyse_dts.py` and `analyse_dts_p.py` as
`T1C.gci`) returns `richardson = f_fine + e21/den` with `e21 = f_med - f_fine`;
Roache's extrapolate for that convention is `f_fine - e21/den`. Every `h → 0
excess` in this file is `100 (richardson - Nu_exact)/Nu_exact`
(`analyse_dts.py:722`, `analyse_dts_p.py:374`) and therefore carries the defect.
Found by verification's audit pass 9 (`CROSS_TEAM_GATE_AUDIT.md` §66/§72).

**Every published h→0 excess in this file, corrected** (from `dts.json`,
`dts_p.json` and `gate_t1c.json` level values; corrected = `2*f_fine − frozen`):

| line | ladder | frozen | **corrected** |
| --- | --- | ---: | ---: |
| :12, :388, :684 | constant `Ts`, Re = 100 | +0.1106 % (3.6608395) | **+0.0624 % (3.6590762)** |
| :13, :294 | constant `q″`, Pr = 0.71 | +0.0748 % (4.3669013) | **+0.0013 % (4.3636945)** |
| §Re sweep | Re = 200 | +0.0873 % | **+0.0448 %** |
| §Re sweep | Re = 50 | +0.1856 % | **+0.1551 %** |
| §Re sweep | Re = 25 | +0.5068 % | **+0.5034 %** |
| :694, :708, foot | parabolic-inlet Re = 100 | +0.0721 % | **+0.0294 %** |
| `dts_p.json` | parabolic-inlet Re = 25 | +0.4402 % | **+0.4233 %** |

**What this changes in the readings above.**
* The **Re = 100 → parabolic-inlet** movement quoted at :694/:708 as
  *"+0.1106 to +0.0721 %, closing 36.5 % of the gap"* becomes
  **+0.0624 → +0.0294 %**, closing **52.9 %** of the gap to the +0.0051 %
  Graetz figure. The **direction and the sign of every registered prediction
  are unchanged**; the magnitudes move.
* The **constant-`q″` baseline of +0.0748 %**, which §:127 and
  `build_diag_ladder.py:21` treat as the like-for-like reference excess, is
  **+0.0013 %** corrected — indistinguishable from zero at this precision. Any
  reading that rests on that baseline being non-zero is withdrawn; the
  Pr-dependence claim at :306 (+0.0748 % → +0.0987 %) must be recomputed from
  corrected extrapolates before it is quoted again. **It is not recomputed
  here** — the Pr-sweep triples are not all in the artifacts this addendum
  re-read, and an uncomputed number is left uncomputed rather than estimated.
* Nothing that is a **per-level** excess (the `c`/`m`/`f` columns) is affected:
  those never pass through `richardson`.

**The frozen comparators are NOT edited.** `analyse_t1c.py` sha256
`60893b28…7e6c5135` is a registered frozen import that
`E4a2_runs/analyse_e4a2.py:139-141` refuses on. The derivation and citer list:
`analyse_t1c.ADDENDUM_2026-08-24_richardson_sign.md`, beside this file.

---

# DATED ADDENDUM (2026-08-26): a lane was dispatched to REGISTER the Péclet-scaling arm. **IT IS ALREADY REGISTERED AND ALREADY RUN, ON BOTH THERMAL BOUNDARY CONDITIONS, AND SO IT WAS NOT REGISTERED AGAIN**

**Appended at the foot by a heat-transfer lane, `[lab-attributed]`, ZERO COMPUTE. Lines whose number changed above this section: 0** — verified by byte-comparing everything above against `git show HEAD:verification/runs/T-family/T1_runs/DIAGNOSTIC_PREDICTION.md`. **No registered prediction, band, threshold or falsifier in this file is altered; no verdict moves; nothing is regraded here.** Nothing has been sent, filed, submitted, uploaded, registered or posted outside this box (`CLAUDE.md` rule 7).

A lane was dispatched to freeze a new rung, `T1c-L0b`, for the arm this file registers at **`:166–:200`** — five cases at `Re` 25/50/100/200/400 on T1c's fine mesh, `Pr` = 0.71, log–log slope of the `Nu` excess against `Pe`, predicted **−2** if axial conduction, with `Re` = 25 near **+1.2 %**. **That rung was not frozen, and the reason is `CLAUDE.md` rule 2: the gate, threshold, cap and label are committed BEFORE the solver starts, and here the solvers finished on 2026-08-20.** A pre-registration written on top of results already on disk is a pre-registration in name only.

**What is on disk, in HEAD, and was read before the decision:**

| arm | artifact (all in HEAD) | cases | fitted slope | registered `Re` = 25 point | measured |
|---|---|---|---|---:|---:|
| constant `q″` (this file `:166`) | `pesweep.json`, `analyse_pesweep.py` | `D_Re25`, `D_Re50`, `L_q_f`, `D_Re200`; `D_Re400` **discarded** on this file's own registered development check | **+0.00170 ± 0.00106**, `R²` 0.563 | +1.197 % | **+0.03808 %** |
| constant `Ts` (this file `:327`, "NEXT TEST, REGISTERED BEFORE IT IS BUILT") | `dts.json`, `analyse_dts.py` | three-level `c/m/f` ladders at `Re` 25, 50, 200 plus the `L_Ts` `Re` = 100 ladder — twelve completed cases | **−0.9782 ± 0.1863** (`f`), **−0.8359 ± 0.1763** (`h→0`), `R²` 0.93 / 0.92 | +1.78 % | **+0.5068 %** (`h→0`, frozen sign; **+0.5034 %** corrected by the 2026-08-24 addendum above) |

The `q″` arm's slope sits **1 894 standard errors** from −2; the constant-`Ts` arm's sits **5.5 σ** (`f`) and **6.6 σ** (`h→0`) from it. **Both are already scored against this file's own registered falsifiers** at `:249` and `:417`, and this addendum re-scores neither.

**Two further consequences, stated so that the next dispatch does not repeat this one.** First, the brief's five-point set is not quite either arm as executed: `Re` = 400 has **no constant-`Ts`** case on disk at all, and the constant-`q″` `Re` = 400 point was **discarded by this file's registered development check**, not lost. A single new `Re` = 400 constant-`Ts` point could be registered as an *extension* — but its slope prediction could no longer be honest, because the four-point slope is now visible to whoever writes it, and rule 2 exists precisely to stop a gate being chosen once the answer is in view. Second, **this line already has a successor that IS registered and has NOT been built**: the unheated-upstream test at `:786` (`D_Ts_Re25_U` and `L_Ts_U`, six cases, about 5 core-hours), with its predictions and falsifiers frozen on 2026-08-21. **That, and not a re-registration of a finished sweep, is where this diagnostic's next compute belongs**, and placing it is the supervisor's call.

---

# PRE-FIRST-COMPUTE BUILD/RUN AMENDMENT (2026-08-26) for the unheated-upstream arm registered at `:786`

**Appended at the foot by a heat-transfer lane, `[lab-attributed]`. Lines whose number changed above this section: 0** — verified by byte-comparing everything above against `git show HEAD:verification/runs/T-family/T1_runs/DIAGNOSTIC_PREDICTION.md`. **NO REGISTERED PREDICTION, BAND, THRESHOLD OR FALSIFYING OUTCOME IN THIS FILE IS ALTERED, NARROWED, WIDENED OR REINTERPRETED.** The `:786` arm remains, in its own words, *"Still diagnostic, still ungraded, and no T1c verdict can move on it."* Nothing has been sent, filed, submitted, uploaded, registered or posted outside this box (`CLAUDE.md` rule 7).

## Condition, and how it was checked — this amendment is PRE-FIRST-COMPUTE

`CLAUDE.md` rule 2 permits amendment **before first compute** and requires the condition to be stated with the way it was checked, naming the run directory that does not exist. Checked immediately before the commit that carries this section:

- **The six run directories `D_Ts_Re25_U_{c,m,f}` and `L_Ts_U_{c,m,f}` did not exist on disk and have never existed in any git ref** — `git log --all --diff-filter=A -- 'verification/runs/T-family/T1_runs/D_Ts_Re25_U*' 'verification/runs/T-family/T1_runs/L_Ts_U*'` returns nothing. **Zero core-minutes have ever been spent on this arm.**
- The arm's registered text is **frozen at commit `6a0d7f45d5bc19a3fa06fffac4a20c2a3ecbf82c`** (2026-08-21). `git cat-file -e 6a0d7f45…:verification/runs/T-family/T1_runs/DIAGNOSTIC_PREDICTION.md` succeeds, and the 28 lines of the `:784`–`:811` section are **byte-identical** at that sha and at HEAD.
- After this amendment the six directories hold `0.orig/`, `constant/`, `system/`, `CASE.txt`, `log.blockMesh`, `log.checkMesh.build` and **no `0/`, no numeric time directory, no `log.solve`, no `STATUS_u.*`, no `DONE_u.*`.**

## What was missing, and why an amendment was needed at all

`:786` registers **predictions and falsifiers** and the physical design — *"the parabolic inlet moved to x = −10 D, the wall adiabatic for −10 D < x < 0 and at 310 K for x > 0, T_in = 300 K at the upstream inlet, stations unchanged (measured from x = 0)"*, six cases, about 5 core-hours. It registers **no mesh, no `endTime`, no cap, no completion rule and no launcher that can be queued**, and no builder for it was ever committed. The cases could not be enqueued without those, and they are added here — **all of them build/run specification, none of them a gate.**

## The build specification, registered now

| | value | ground |
|---|---|---|
| radial ladder `nr` | **20 / 32 / 51** | the parent chain's, **unchanged** |
| axial `nx` over 60 D | **240 / 384 / 612** = `12 nr` | makes the axial cell size **uniform across `x = 0`** — the plane whose conduction flux the registered predictions read — and the upstream 10 D an **exact integer** 40 / 64 / 102 cells; the level ratios 1.6 and 1.59375 are **exactly the parent's own `nr` ratios** |
| cells | **4 800 / 12 288 / 31 212** | `checkMesh` **Mesh OK**, non-orthogonality **Max 0** on all six |
| wall patches | **`wall_adiabatic`** (10 D, `zeroGradient` T) + **`wall_hot`** (50 D, `fixedValue` 310 K) | measured face counts 40/64/102 and 200/320/510 — the 300 K / 310 K corner is gone by construction, which is the arm's entire purpose |
| inlet | parabolic at the mesh's **own** face centroids, single scale `s` making the **discrete** flow rate exact (`s` = 0.999584367 / 0.999837410 / 0.999935950; residual ≤ 1e-12 relative) | `build_d_ts_p.py`'s construction, re-derived from the mesh this builder wrote |
| `endTime` / `writeInterval` | **40 000** / 2 000 | the domain is 1.2× longer than the parent's, so the same convergence per unit length needs ≈1.2× the iterations; 40 000 is 1.33× and leaves margin. `writeInterval` **strictly less** than `endTime` (L-140) |
| everything else | **byte-copied** from each case's own parent (`D_Ts_Re25_<lvl>`, `L_Ts_<lvl>`) | `nu`, `Pr`, the turbulence dictionary, the zero gravity vector, `fvSchemes`, `fvSolution` are **inherited, not retyped** |

**Convergence is the campaign's own registered criterion, unchanged:** `analyse_t1c.iterative_convergence` on the **last two written checkpoints**, `max|a−b|/(max b − min b) ≤ 1e-6`, **not the solver residual** — T1c's own docstring records a non-converged case impersonating a discretisation failure behind "a merely unremarkable 4e-05". `mark_done_dts_u.py` therefore makes **two written checkpoints** a physics-critical completion clause: a run with one cannot be tested against the criterion at all.

## The launcher, and why a new one was written rather than the old one reused

**`run_one_dts.sh` predates the queue runner and cannot be queued.** Four defects, each measured on the file as it stands:

1. **Guard G2 refuses ANY process whose cwd is the case directory, with no lineage exclusion.** Under the runner's `setsid nohup bash -c 'cd <cwd>; …'` form the runner's own wrapper shell holds the case as cwd, so the launcher **refuses its own launch** — verbatim the cwd-guard defect that produced three zero-compute refusals per rung on T10aR2, T4b and `R_ff`, repaired for those by the lineage-aware scan of `9fa66065`.
2. **Guard G1 requires a `LAUNCH_LOCK` that only `launch_dts.sh` creates**, and `launch_dts.sh` self-detaches — so a queue entry can name neither.
3. **No `timeout` anywhere.** Rule 12's *"an overrun stops the run"* has **no mechanism** in it.
4. **`STATUS` is a single `rc= wall= checkMesh_rc=` line** carrying no `capped`, `ranks`, `core_min` or `timeout_s`, so the L-342 field classes cannot be applied to it.

**`run_one_dts.sh` is NOT edited and NOT deleted** — the existing arms' provenance stands on it. **`run_one_dts_u.sh`** is written instead, on the `run_one_t14.sh` pattern (freeze `5a870e54`): solver in the wrapper's **foreground** under `timeout`; **rc captured in-wrapper**; `capped` as an independent expiry witness; the cap read from `DTS_U_registered.json` and a differing `--timeout` **refused**; `--ranks` other than 1 refused; an existing `STATUS_u` refused; time directories matched by **regex fullmatch, never a glob**; `0/T` touched **last**; `exit "$RC"` last; **`--no-detach`** the queue mode; and the **lineage-aware foreign-process guard**. It writes **`STATUS_u.<case>`** — a separate namespace, so the older arms' `STATUS.<case>` files are never collided with or overwritten.

**Driven on scratch, both arms, 2026-08-26.** **ARM A** (runner form, registered dictionaries, `endTime` cut to 200): launched, **solver rc 0**, 200 `ExecutionTime` lines, two written checkpoints, `STATUS_u` written (`wall_s 6`, `capped no`, `note clean`), `0/Cx` and `0/V` written by OpenFOAM before `0/T` was touched. **ARM B** (planted `sleep` with cwd in the case): `REFUSE: pid 599762 is already running in D_Ts_Re25_U_c (foreign process, outside this launcher's lineage)`, **exit 2, no `STATUS_u` written, no `0/` created**.

## Cost — rule 12, priced from the parent's own measured walls

Each U case is priced from **the wall time its own parent level actually spent** (`dts.json` completion block, `wall_seconds / (cells × endTime)`), so the level-to-level rate drift is carried rather than averaged away. The parent six ran **146.745 core-min** measured.

| case | cells | parent | parent rate (core-s / cell-it) | **POINT core-min** | **cap** | `timeout` s |
|---|---:|---|---:|---:|---:|---:|
| `D_Ts_Re25_U_c` | 4 800 | `D_Ts_Re25_c` | 2.8667e-06 | **9.173** | 30 | 1 800 |
| `D_Ts_Re25_U_m` | 12 288 | `D_Ts_Re25_m` | 3.0469e-06 | **24.960** | 80 | 4 800 |
| `D_Ts_Re25_U_f` | 31 212 | `D_Ts_Re25_f` | 4.1718e-06 | **86.807** | 270 | 16 200 |
| `L_Ts_U_c` | 4 800 | `L_Ts_c` | 2.3627e-06 | **7.561** | 25 | 1 500 |
| `L_Ts_U_m` | 12 288 | `L_Ts_m` | 2.5934e-06 | **21.245** | 70 | 4 200 |
| `L_Ts_U_f` | 31 212 | `L_Ts_f` | 4.0550e-06 | **84.376** | 260 | 15 600 |
| **total** | | | | **234.122** | **735** | |

POINT 234.1 core-min = 3.90 core-h = **$0.200 derived**; CAP 735 core-min = 12.25 core-h = **$0.628 derived**, at the owner-stated $0.0513/core-h — **reported-by-owner, not measured** (`COMPUTE_BUDGET_CHARTER` §5). **The frozen text's own estimate was "about 5 core-hours"; the measured-rate POINT is 3.90 core-h, inside it.**

**A contention measurement, recorded rather than folded in.** The ARM-A scratch probe measured **6.494e-06 core-s per cell-iteration** on this arm's own `c` case — **2.27× the parent's measured `c`-level rate** — on a box carrying several other teams' solves. **The POINT stays the parent-measured figure**, because that is the honest estimate of the *work*; **the caps are set at ≈3.2× the POINT** so that a run under that contention is not cap-stopped by a budget that priced an idle box. If the actuals come in near 2.3× the POINT, the completion calibration attributes the gap to **contention** and not to misprediction (rule 12), and the figure to attribute it with is on this page in advance.

## Freeze set (committed with this section)

| file | sha256 (first 16) | git blob | lines |
|---|---|---|---:|
| `verification/runs/T-family/T1_runs/build_dts_u.py` | `48fa36d5b0146128` | `953089050cb73abd27437f87c163a76dcf81012f` | 463 |
| `verification/runs/T-family/T1_runs/run_one_dts_u.sh` | `dc06ca93e36794d6` | `0e68db8915659a1aaa4522751508d27ef6835eca` | 213 |
| `verification/runs/T-family/T1_runs/mark_done_dts_u.py` | `f09156b5c5c87c7f` | `156d8ffdf9ab84d7f514ab464a03135173bdddff` | 253 |
| `verification/runs/T-family/T1_runs/DTS_U_registered.json` | `d3886edce266d64a` | `0a5896046a40f6a19bf6a4266752d1ef33b67529` | 200 |

`0 ast.Assert` in each Python instrument, the counter shown able to count a planted one; every refusal is `sys.exit(2)`; both selftests PASS under `python3` **and** `python3 -O` (`build_dts_u.py` 9 checks including a two-route agreement between its own `polyMesh` reader and `analyse_dts`'s on the parent `L_Ts_c` mesh — 8 241 points, 16 020 faces, identical; `mark_done_dts_u.py` 13 clauses). Case inputs for the six (`0.orig/`, `constant/` less `polyMesh`, `system/`, `CASE.txt`, build logs) are committed alongside.

**What this amendment does not do:** it does not alter a registered prediction, band, threshold or falsifier; it does not grade anything; it does not move any T1c verdict; it does not edit `run_one_dts.sh`, `analyse_dts.py`, `analyse_t1c.py` or any other frozen file; and it does not authorise a launch — **enqueueing is not authorisation** (`QUEUE_ENTRY_STANDARD` §1), and the supervisor's check 4 is personal.
