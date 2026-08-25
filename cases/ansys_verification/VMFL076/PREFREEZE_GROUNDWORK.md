# VMFL076 — Forced Convection Over a Flat Plate — PRE-FREEZE GROUNDWORK

# THIS IS **NOT** A PRE-REGISTRATION AND **NOTHING IS FROZEN BY IT**

**No gate, band, tolerance, cap or label is registered here, and no solver has run.**
This document carries only the two things that had to be established **before** a freeze
could be written honestly: the **mandatory consistency check** against the manual's own
inputs, and the **reference solution**, derived and confirmed. A pre-registration built on
it must still be written, frozen and committed **before any compute**, under
`docs/ansys_verification/PREREG_TEMPLATE.md` and all six amendments.

**Written 2026-08-25T23:0xZ by `ansys-lane-opus`.** Manual: VM2026R1 **p.219**.
Executable: `cases/ansys_verification/VMFL076/consistency_and_similarity_vmfl076.py`.

---

## 1. THE MANDATORY CONSISTENCY CHECK — **it fell CONSISTENT**

Manual p.219, verbatim: density 900 kg/m³; viscosity 0.01 kg/m-s; specific heat
42.6 J/kg-K; thermal conductivity 142 W/m-K; flat plate length 1 m; inlet velocity 1 m/s;
inlet temperature 300 K; plate temperature 350 K.

| group | from the manual's own numbers | reading |
|---|---|---|
| **Prandtl** | `mu cp/k` = **3.00e-03** | The page calls the case *"very low Prandtl numbers, typically encountered in liquid metal flows"* and its reference is titled *"EXACT **LOW PRANDTL NUMBER** BOUNDARY-LAYER SOLUTIONS"*. **CONSISTENT.** |
| **Reynolds** | `rho U L/mu` = **9.00e+04** | Below the ~5e5 transition. The page's *"Laminar steady flow"* is **CONSISTENT**. |
| Péclet | `Re_L Pr` = **270** | convection and conduction both matter; not a degenerate limit. |
| Eckert | `U²/(cp dT)` = **4.70e-04** | viscous dissipation is **negligible**; Sparrow & Gregg's forced-convection problem carries none, so none should be modelled. |

**Reported whichever way it fell: it fell CONSISTENT.** Unlike VMFL036 — whose stated
viscosity gave Re = 50 against an Re = 100 target — **this page's inputs and its stated
physics agree, and no diagnostic arm is needed to test the manual.**

**NO DRIVING INPUT IS MISSING.** `rho, mu, cp, k, U_inf, T_inf, T_wall, L` are all printed.
**The case is therefore NOT contested on the missing-input limb** and the ten-line
template-speed form applies.

### 1.1 The one thing the page does NOT give, and why it is not a missing input

**The manual's only result for this case is a FIGURE** — *"Figure .76.2: Comparison of
Normalized Temperature with **analytical results**"* — and **no numeric table**. That is
precisely the Tier-1 situation the reference-form census identified: **the reference is
ANALYTIC, so it is EVALUATED rather than digitised**, at any resolution, with **zero
digitisation error**. **Figure .76.2 is context only and must not be digitised or gated on.**

## 2. THE REFERENCE SOLUTION — derived here, and CONFIRMED against a known constant

Sparrow & Gregg's low-Prandtl forced-convection result is the **similarity solution** of
the laminar flat-plate boundary layer. With `eta = y sqrt(U_inf/(nu x))` and
`theta = (T - T_wall)/(T_inf - T_wall)`:

    Blasius   :  f''' + (1/2) f f'' = 0 ,   f(0) = f'(0) = 0 ,  f'(inf) = 1
    Energy    :  theta'' + (Pr/2) f theta' = 0 ,  theta(0) = 0 ,  theta(inf) = 1

    theta(eta) = INT_0^eta exp(-(Pr/2) INT_0^s f dt) ds  /  INT_0^inf (same)
    Nu_x / sqrt(Re_x) = theta'(0)

**Solved here by RK4 with shooting — no table was consulted:**

| quantity | value | check |
|---|---|---|
| **f''(0)** | **0.3320573362** | the classical Blasius constant, matched to **1.5e-11**. **This is the control on the ODE solver**, and the script REFUSES if it misses. |
| **theta'(0) at Pr = 0.003** | **0.0293707857** | = `Nu_x/sqrt(Re_x)`, the natural gate scalar |
| eta_99 (theta = 0.99) | **67.76** | y = **0.2259 m** at x = L |

### 2.1 A RESULT THAT DECIDES THE METHOD: the slug-flow shortcut is NOT good enough

The textbook low-Pr shortcut replaces the Blasius profile with uniform flow, giving
`theta'(0) -> sqrt(Pr/pi)` and an `erfc` profile. At the manual's Pr = 0.003:

    slug-flow asymptote  sqrt(Pr/pi) = 0.0309019362
    exact similarity ODE               0.0293707857
    ratio 0.9505  ->  THE SHORTCUT IS 4.955% HIGH

> **4.955 % would sit outside any tolerance worth registering for a closed-form reference.
> The slug/erfc form must NOT be used as the reference, even though Pr = 0.003 looks
> "small enough". The full similarity ODE at the actual Pr is the reference.** Recorded
> because the shortcut is the obvious move and it would have quietly biased the gate.

## 3. WHAT THIS IMPLIES FOR A CASE BUILD (guidance, NOT a registration)

- **Domain height is set by the THERMAL layer, not the momentum one.** `delta_mom(L) =
  0.0167 m` but `delta_th(L) ~ 0.30 m` — **18.3x thicker**, because
  `delta_th/delta_mom ~ 1/sqrt(Pr)`. A domain sized off the momentum layer would **clip the
  thermal layer and bias every gated point**. Height should comfortably exceed
  `eta = 120` (y = 0.40 m at x = L).
- **Viscous dissipation must be OFF** (Ec = 4.7e-04, and the reference carries none) —
  the opposite of VMFL033, where it is the whole physics.
- **Reference kind: closed-form/exact -> buys V, NEVER P. Tier ceiling `GATE REACHED`.**
- A natural gate pair: the **normalised temperature profile** at one or more x-stations,
  gated **pointwise** against `theta(eta)` evaluated at the mesh's own cell-centre `eta`
  (radii/coordinates **read back from the `C` field**, never constructed); plus the scalar
  `Nu_x/sqrt(Re_x)` against **0.0293707857**.

## 4. STATUS AND WHAT IS NOT DONE

**NOT DONE, and stated plainly rather than implied:**

- **No pre-registration is written and nothing is frozen.**
- **No case, mesh, launcher or comparator exists.** No solver has run; the run root
  `verification/runs/ansys_verification/VMFL076/` does not exist.
- **No verdict.** Under the fixed vocabulary the case's status is **`PENDING`**.
- The comparator, when written, must carry the full non-droppable list and — per this
  team's rule of tonight — **a selftest PROVEN ABLE TO FAIL by mutation, green-on-break
  under both `python3` and `python3 -O`, with the mutation results recorded in the
  pre-registration.**

**What this lane could NOT verify:** whether Sparrow & Gregg's NASA Memorandum 02-27-1959
tabulates values that differ from this similarity solution at Pr = 0.003 — **the memorandum
itself is not in the lab's archive**, and §2 reconstructs the physics the manual's page
describes rather than reproducing that document's tables. The Blasius constant match is a
control on the **solver**, not proof that the memorandum agrees. **A freeze built on this
should state that limitation on its reference line.**
