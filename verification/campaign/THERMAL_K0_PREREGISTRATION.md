# Thermal ladder, rung K0 — PREREGISTRATION

**Written before any solver ran.** Every number below the line "PREDICTIONS" was
recorded before `buoyantBoussinesqSimpleFoam` was invoked for the first time in
this campaign. Outcomes are recorded in `THERMAL_K0_RESULTS.md`, which is a
separate file so that this one can be diffed against its own commit.

**Date:** 2026-08-17
**Dispatched as:** campaign "F11", rung K0 (owner's internal label — see §0)
**Authorized compute:** K0a and K0b only. K2b, the rack-row module and any
turbulent SST case are explicitly NOT authorized and were not run.

---

## §0 — LABEL COLLISION, unresolved, needs the owner

The dispatch names this campaign **F11**. In this repository **F11 is already
taken** by a different, already-built family:

- `demo-output/website/campaign/F11_lid_driven_cavity_ladder.md` — "F11 — 2D
  Lid-Driven Cavity Verification Ladder (Ghia, Ghia & Shin, 1982)", dated
  2026-07-30, two rungs at two mesh resolutions.
- `demo-output/website/campaign/F11_runs/` — its case scripts.

F1–F12 are all in use. Writing this thermal work into `F11_*` would have
overwritten or merged into a gated family that has nothing to do with it.

**Action taken:** this work is parked under a physics name,
`THERMAL_K0_*`, which cannot collide. **The campaign label is left for the
owner to rule on** — either the thermal ladder takes a free label (F13 is the
next unused), or the existing F11 is renamed. Nothing here should be filed under
"F11" until she says which.

---

## §1 — What these rungs are, and what they are not

K0a and K0b are **capability rungs**. They establish that this lab can drive a
buoyancy-coupled solver and that the numbers coming out of it conserve energy.

**They prove nothing about the world.** They are not validated against any
published reference datum. They must not appear on the wall, on the website, in
application materials, or on any external surface as results. No data-center or
cooling-market language attaches to them. The first rung permitted to make a
claim about reality is **K0c, the validation gate against published reference
data, which is not in this dispatch.**

## §2 — Fluid properties (declared inputs, not results)

Air at 300 K, 1 atm, taken as standard tabulated values and then checked for
internal consistency by re-derivation rather than accepted as quoted:

| quantity | value | source / check |
|---|---|---|
| rho  | 1.1614 kg/m^3 | declared input |
| mu   | 1.846e-05 Pa.s | declared input |
| k    | 0.0263 W/(m.K) | declared input |
| cp   | 1007 J/(kg.K) | declared input |
| nu   = mu/rho | 1.589461e-05 m^2/s | derived |
| Pr   = mu.cp/k | 0.706814 | derived |
| alpha = k/(rho.cp) | 2.248767e-05 m^2/s | derived |
| nu/Pr | 2.248767e-05 m^2/s | derived — agrees with alpha to 6 s.f., so the four inputs are mutually consistent |
| beta = 1/TRef | 3.333333e-03 1/K | ideal gas at TRef = 300 K |
| g | 9.81 m/s^2 | declared |

`alphaEff` in `buoyantBoussinesqSimpleFoam` is `nu/Pr + nut/Prt`. Both cases are
**laminar**, so `nut = 0` and `alphaEff = nu/Pr = alpha` exactly. This is why the
heat-balance auditor's laminar path is exact for these two rungs and why it
refuses to run on a turbulent case until that path has its own control.

## §3 — Regime numbers (computed before the runs)

Ra_L = g.beta.dT.L^3 / (nu.alpha), Gr_L = Ra_L/Pr, Pr = 0.706814.

### K0a — heated box (feasibility)
2D box 0.10 m x 0.10 m x 0.01 m (one cell thick, `empty` front/back).
Hot strip on the floor, x in [0.03, 0.07]; cold ceiling; adiabatic side walls
and remaining floor. Mesh 20 x 20 x 1 = **400 cells**. Deliberately coarse.

| quantity | value |
|---|---|
| L | 0.10 m |
| dT (hot strip minus cold ceiling) | 10.0 K |
| **Ra_L** | **9.1486e+05** |
| **Gr_L** | 1.2943e+06 |
| Pr | 0.706814 |
| U_buoy = sqrt(g.beta.dT.L) | 0.1808 m/s |
| Re based on (U_buoy, L) | 1138 |
| **beta.dT (Boussinesq small parameter)** | **0.0333** |
| dT/TRef | 0.0333 |

### K0b — differentially heated square cavity (physics)
2D cavity 0.10 m x 0.10 m x 0.01 m. Hot wall at x=0, cold wall at x=L,
adiabatic top and bottom. Mesh 64 x 64 x 1 = **4096 cells**.
dT chosen to land exactly on Ra = 1.000e5:
dT = Ra.nu.alpha/(g.beta.L^3) = **1.093066 K**, T_hot = 300.546533 K,
T_cold = 299.453467 K, TRef = 300 K.

| quantity | value |
|---|---|
| L | 0.10 m |
| dT | 1.093066 K |
| **Ra_L** | **1.0000e+05** |
| **Gr_L** | 1.4148e+05 |
| Pr | 0.706814 |
| U_buoy | 0.05979 m/s |
| Re based on (U_buoy, L) | 376 |
| **beta.dT** | **0.00364** |

### Richardson number — stated plainly, and why it cannot gate anything
Both rungs are **pure natural convection**: there is no imposed velocity scale.
Ri = Gr/Re^2 requires a forced Re. If Re is built from the buoyancy velocity
U_buoy = sqrt(g.beta.dT.L), then Re^2 = g.beta.dT.L^3/nu^2 = Gr and **Ri = 1
identically, by construction, for every case in this class regardless of the
physics**. That is an identity, not a measurement, and per W-2 an identity
cannot gate anything. So: **Ri is reported as "not defined independently
(Ri = 1 by construction)" for K0a and K0b, and Ra and Pr carry the regime.**
Ri becomes a real, independent number only when a forced flow is imposed —
which is the rack-row module, and that is not authorized here.

### Boussinesq validity
The approximation requires beta.dT << 1. K0a: beta.dT = 0.0333. K0b:
beta.dT = 0.00364. Both are two to three orders below unity, so the
small-dT assumption is **satisfied and not violated** in either rung. Max dT
in the domain will be re-measured from the solved fields, not assumed, and
reported against this line.

---

## PREDICTIONS

Recorded before the first solver invocation. Each is a falsifiable band, not a
direction of travel.

### K0a
- **A1 (runs).** `buoyantBoussinesqSimpleFoam` reaches its stop condition with
  no floating-point exception and no unbounded T. Final initial-residuals:
  T < 1e-6, Ux and Uy < 1e-5, p_rgh < 1e-3.
- **A2 (temperature actually transports — advection, not conduction).**
  Nu_hotStrip = Q_hotStrip(g on) / Q_hotStrip(g off) **> 1.5**, expected in
  2 to 6. The g-off twin is a pure-conduction solve, so its Nu is 1 by
  definition; that is precisely why the twin exists — without it, "T changed"
  is satisfied by conduction alone and is not a transport test.
- **A3 (buoyancy actually acts).** g-off twin: max|U| < 1e-8 m/s.
  g-on: max|U| in 0.02 to 0.5 m/s (U_buoy = 0.18 m/s).
- **A4 (energy closes).** Boundary heat-balance imbalance **< 2%** of heat in,
  on 400 cells.

### K0b
- **B1 (runs).** Stop condition reached, no FPE. Final initial-residuals:
  T < 1e-7, U < 1e-6, p_rgh < 1e-4.
- **B2 (plume / wall boundary layer present).** Non-dimensional velocity
  extrema, V* = v.L/alpha on the horizontal mid-plane y = L/2 and
  U* = u.L/alpha on the vertical mid-plane x = L/2:
  **V*_max in 40 to 110** (boundary-layer scaling ~0.2.Ra^0.5 = 63),
  **U*_max in 20 to 60**.
- **B3 (stratified core present).** Dimensionless vertical stratification at
  the cavity centre, S = d(theta)/d(Y) with theta = (T - T_cold)/dT and
  Y = y/L, evaluated at the geometric centre:
  **S > 0.3**, expected 0.5 to 1.2. The pure-conduction solution of this
  cavity has S = 0 **exactly** (heat flows horizontally only), so S is a real
  discriminator and not an identity.
- **B4 (energy closes).** Imbalance **< 0.5%** of heat in, on 4096 cells.
- **B5 (Nusselt, prediction only).** Nu_hotWall in **3 to 7**, point estimate
  4.98 from the laminar boundary-layer scaling Nu ~ 0.28.Ra^(1/4). This is my
  own scaling estimate. **It is not a validation and is not compared to any
  published benchmark value in this rung.** Comparing it to literature is K0c's
  job and K0c is not authorized here.
- **B6 (Boussinesq).** Measured max dT across the domain equals 1.093066 K to
  within solver tolerance, and beta.dT stays at 3.64e-03.

### Controls — each with the readback that proves the plant landed

- **C1 — positive readback for the A3 zero.** A3 asserts a *zero* (no motion
  without gravity). A zero from a measurement pipeline that is silently broken
  looks identical to a zero from physics. So the *same* max|U| extractor, same
  invocation, is run against the g-on case first and must return a large
  number. **Readback required before A3 is accepted:** extractor returns
  max|U| > 0.01 m/s on the g-on case. If it does not, A3 is void, not passed.
- **C2 — auditor calibrated against closed form.** A g-off twin of the K0b
  cavity is a pure 1-D conduction problem with the exact steady answer
  Q = rho.cp.alpha.(dT/L).A. The auditor must reproduce it.
  **Prediction: Q_hotWall from the auditor agrees with the closed-form value to
  within 0.5%, Q_coldWall = -Q_hotWall to within 0.5%, and the sign convention
  puts heat entering at the hot wall.** This validates the auditor's whole
  chain — patch areas, surface-normal gradient, property values, sign — against
  an answer derived independently of the auditor.
- **C3 — auditor sensitivity (it can report a *failing* balance).** The auditor
  is run on an early, unconverged K0b snapshot where the balance is genuinely
  open. **Prediction: imbalance > 20% there**, versus < 0.5% at convergence.
  A checker that reports "closed" on everything is not a checker.
- **C4 — property-path plant, with anchor verification.** A copy of the
  converged K0b case has `Pr` in `constant/transportProperties` halved.
  alphaEff = nu/Pr then doubles, so every patch heat rate must double.
  **Prediction: Q_hotWall(mutant)/Q_hotWall(base) = 2.000 to within 0.1%.**
  **Anchor verification, performed and logged before the mutant is audited:**
  (i) the string `Pr` is present as a keyword in the mutant's
  `constant/transportProperties`, and (ii) the file differs from the base file.
  A plant keyed on a keyword that is not there is a silent no-op and would
  produce a false pass; both conditions are asserted, and the assertion output
  is recorded in the results file.

### What would count as a failure
- K0a runs to completion but Nu = 1.0 within noise -> the solver is running and
  transporting nothing. That is a **failed** rung, not a passed one.
- K0b shows no plume or S <= 0.3 -> **that absence is the finding** and is
  reported as such, not explained away.
- Imbalance above the bands above -> the rung is not clean and the auditor's own
  calibration (C2) decides whether the fault is in the physics or the checker.

---

## §4 — Cost

Both rungs are single-core laminar 2D solves of 400 and 4096 cells. Estimated
before launch: **under 2 core-minutes each, under 10 core-minutes total
including the three control twins.** No parallel decomposition, no cloud
resource, nothing that touches the spend that needs the owner's word.
Actual wall-clock is recorded in the results file.

---

# ADDENDUM — 2026-08-17, appended after the runs. §0 is superseded.

**This is an append-only addendum. Nothing above this line has been altered.**
The body of a preregistration is not editable after compute has run (W-3), and
its value is precisely that it can be diffed against its own commit. §0 is left
standing, wrong, with the answer here.

**THE COLLISION IS RULED. THIS CAMPAIGN IS F14.**

- The data-center cooling campaign is tagged **F14**, not F11.
- **F11 keeps the lid-driven cavity ladder**, by measured precedence: created
  2026-07-30, carrying gate results against Ghia, Ghia and Shin 1982 and a
  populated `F11_runs/` tree.
- **F14 was verified unused repository-wide**, as were F15 through F22.
- **§0's guess that "F13 is the next unused" is wrong and is superseded.** F12
  is a live campaign with its own preregistration, which §0 did not check.
- The campaign's gate specifications live at
  **`docs/campaigns/F14-cooling-ladder/`**, landed at commit `208fef5c`.

**What does not change.** `THERMAL_K0_*` is a physics name, it never collided,
and nothing under it is renamed. Only the campaign tag moved.

**Also recorded here, because it constrains every rung after these two:** the
F14 gate specifications mark **three reference values NOT OBTAINED** — core
stratification on the laminar rung, Nusselt number on the turbulent rung, and
the Blay primary for K0d. **No rung may be marked passed against a number the
executing agent produced itself.** That applies directly to B5 above: the
Nusselt point estimate of 4.98 in this document is my own scaling estimate,
it is labelled as such, and it is not a reference value and cannot grade
anything.
