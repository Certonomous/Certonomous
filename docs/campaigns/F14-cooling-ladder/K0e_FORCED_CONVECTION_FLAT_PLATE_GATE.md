# K0e. Forced-convection flat plate: gate specification

Campaign F14, gate K0e. Written 2026-08-19, **zero compute spent, no solver
launched.** Specification only. The rung it specifies has **not** been run.

---

## 1. Why this rung, and what it is for

**Every thermal result this lab owns is a buoyant cavity, where the momentum
field and the thermal field are both wrong and are coupled through buoyancy**
(`THERMAL_CAPABILITY_STATE.md` §5). `K0cR` is the demonstration: fixing the
stress closure moved the velocity field **19 points toward** the experiment and
the wall heat flux **30 points away**, in the same solves.

**A zero-pressure-gradient flat plate breaks that confound.** Its momentum
closure is the best-validated thing this lab owns, and buoyancy is absent by
construction. **Any Stanton-number error is then attributable to the thermal
closure alone**, which no rung in this campaign can currently claim.

**This is the rung that would make the thermal side's closure findings
transferable rather than cavity-specific.**

---

## 2. The reference, its tier, and three limits carried into the design

**Bahrami, P. A. (2005). *Heat Transfer on a Flat Plate with Uniform and Step
Temperature Distributions.* NASA/TM-2005-212841.** Tier **READ IN FULL**
(D430). Held at
`docs/papers/forced_convection_heat_transfer/bahrami_2005_nasa_tm_212841.pdf`,
sha256 `0cd29adb20c0f6c21c07f37f101f0f8d3f3a7f85a81a95abc023da25a66f8be6`.

**Equation (1), as printed:**

    St = 0.0296 Re^-0.2 (Pr Tw / T_inf)^-0.4

with **`St = q / (Cp_inf rho_inf U_inf dT)`**, `Re` based on distance from the
leading edge and free-stream properties.

### 2.1 The limits, stated in the specification rather than discovered in the results

1. **The primary is NOT OBTAINED.** Moretti & Kays (1965) exists in this library
   only as figures inside this secondary. **No row below grades against their
   data.**
2. **Equation (1) is a correlation, not a measurement.** It is an empirical fit.
3. **Circularity, and it is the load-bearing caution.** Eq. (1) is Colburn-type
   and sits in the family of the Reynolds and Von Karman analogies. **The
   Reynolds analogy is close to what a constant-`Prt` gradient-diffusion closure
   asserts**, so agreement between a `Prt = 0.85` RANS solve and eq. (1) is
   **partly structural rather than evidential**. The `Pr^-0.4` exponent against
   the analogy's `Pr^-2/3` is the gap that keeps the comparison from being fully
   circular, **and at `Pr = 0.71` that gap is small.** A rung that reported
   agreement here as validation of a thermal closure would be claiming as
   evidence something it largely assumed.

---

## 3. The consequence of §2.1, and it is the central design decision

**This rung REPORTS the Stanton number against equation (1). It does NOT gate
on it.**

**No band is armed, and the reason is that no band can be honestly derived from
the source in hand.** Bahrami states measurement uncertainties for Moretti &
Kays — temperature 3 %, heat flux 2 %, velocity 1 % — but those belong to their
step-temperature experiment, **not to equation (1)**, and the document states no
uncertainty for the correlation itself.

`LITERATURE_CHARTER.md` §2 forbids a fourth tier for *"well known"*, *"standard
result"* or *"widely reported"*, **so the correlation's conventional accuracy
may not be invoked to arm a band.** Setting the band instead to the ~10 % at
which Bahrami reports two-equation models sitting would be **setting the band to
what we expect to achieve**, which is the error the whole gate discipline
exists to prevent.

**What would arm a band:** a source stating equation (1)'s own uncertainty, or
the Moretti & Kays primary data. **Until then this rung is a MEASUREMENT with a
reported deviation, and its verdict vocabulary is limited to NOT A RESULT,
BLOCKED and PENDING.** It cannot PASS and it cannot GATE FAIL, by construction,
and that is registered here rather than discovered later.

---

## 4. The case

The lab's existing TMR flat plate, `certonomous-runs/tmr-flatplate-*`:
`simpleFoam`, `kOmegaSST`, **52 224 cells**, plate from `x = 0` to `x = 2.0` m
with a symmetry section from `x = -1/3` to `0`, `U_inf = 1.0 m/s`,
`nu = 2e-07 m2/s`.

**`Re_x` therefore runs 0 to 1.0e7 along the plate**, which brackets Bahrami's
`Re/x = 1 215 400 m^-1` in its first quarter metre. **Comparison is made at
matched `Re_x`, not at matched dimensional velocity.**

### 4.1 Thermal setup

| Item | Value | Reason |
| --- | --- | --- |
| Solver | `buoyantBoussinesqSimpleFoam` | the solver the whole thermal ladder uses, so the closure is the same object |
| `beta` | **0** | removes buoyancy exactly |
| `g` | **(0 0 0)** | removes it again, independently |
| `T_inf` | 300 K | |
| `T_wall` | 310 K, uniform | eq. (1) is the uniform-wall case; `Tw/T_inf = 1.033`, so the temperature-ratio factor is near unity and is **applied, not neglected** |
| `Pr` | 0.71 | air |
| `Prt` | 0.85 | the ladder's value, so this rung is comparable to K0cS and K0cX |

**`dT = 10 K` is chosen small on purpose**: large enough that Stanton is well
conditioned, small enough that constant properties hold and that a Boussinesq
solver with `beta = 0` is not being asked to represent variable-density physics.

### 4.2 The two controls, both bit-for-bit

1. **MOMENTUM control.** With `beta = 0` and `g = 0` the momentum equation
   reduces to `simpleFoam`'s. **The velocity field must reproduce the recorded
   `simpleFoam` solution to machine zero**, in the sense `K0cQ`'s `Ccr1 = 0` and
   `W3_QCR_DUCT_FALSIFIER.md` achieved. **If it does not, the rung is NOT A
   RESULT**, because the thermal field would then be sitting on a different
   momentum field from the validated one and the whole point of the rung is
   lost.
2. **ZERO-`dT` control.** With `T_wall = T_inf` the heat flux must be identically
   zero and the Stanton number undefined rather than small. This catches a
   spurious flux from the discretisation or the boundary conditions.

---

## 5. What is measured

| # | Quantity | Against | Status |
| --- | --- | --- | --- |
| **M1** | `St(Re_x)` over the turbulent range | eq. (1) | **REPORTED**, not graded (§3) |
| **M2** | `Cf(Re_x)` | the lab's existing TMR flat-plate validation | **control**, and it must match what the lab already records |
| **M3** | `Prt_eff` through the boundary layer | — | reported, and it is the quantity D424 found pinned at exactly 0.8500 on the cavity |
| **M4** | momentum control residual, `max abs dU` vs `simpleFoam` | 0 exactly | **NOT A RESULT if non-zero** |
| **M5** | thermal boundary-layer thickness and the near-wall `alpha_t` profile | — | reported; the diagnostic D424 had to build after the fact |

**M3 is the row this rung exists for.** On the cavity, `alpha_t` is slaved to
`nu_t` by a constant and the measured `Prt` is not constant. **On a flat plate
the same closure is being asked a question whose answer is far better known**,
and whether it fails the same way is the transferability question.

---

## 6. What this rung cannot do

- **It cannot validate a thermal closure**, for the circularity reason in §2.1.3.
- **It cannot fail a model**, because no band is armed (§3).
- **It is not the mixed-convection rung.** K0d remains blocked on Blay.
- **It says nothing about buoyant flows.** A plate with `beta = 0` has no
  buoyancy production of anything.

---

## 7. Cost, if it is run

Two cases — the thermal arm and the zero-`dT` control — on the existing
52 224-cell mesh. The recorded `simpleFoam` solve on this mesh is the momentum
reference and is **not re-run**. On the cavity ladder's measured rates a case of
this size and iteration count is of order **0.5-1.5 core-hours**, so the rung is
**well under $0.10**. **The cost is not the obstacle; §3 is.**
