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
