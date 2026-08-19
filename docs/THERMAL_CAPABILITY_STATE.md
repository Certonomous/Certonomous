# What this lab can and cannot do in heat transfer, as of 2026-08-19

**Zero compute.** A consolidation, not a new result. Every number is cited to a
record that established it. **Read `VALIDATION_INVENTORY.md` §3.2 first** — this
does not replace the inventory's count of campaign F14; it states the
*capability*, which the inventory does not, and it names the gaps in the order
they should be closed.

---

## 0. The headline, before the detail

**The thermal side is deep on one flow class and has no second one.**

Every graded thermal result this lab owns is a **buoyancy-driven cavity**: a
laminar differentially heated cavity, a turbulent square cavity, and a turbulent
tall cavity. There is **no forced-convection heat-transfer rung, no mixed-
convection rung, and no conjugate rung.** The aerodynamic side spans ducts, a
flat plate, the NASA hump, periodic hills and a backward-facing step; the
thermal side spans **cavities**.

**Within that one class the work is now unusually deep** — a closure form has
been refuted three independent ways — **and that depth is what makes the absence
of a second class the binding limitation.** A closure conclusion drawn on one
flow class is a conclusion about that flow class.

---

## 1. What is validated, and what the verdicts are

| Rung | Flow | Reference | Verdict |
| --- | --- | --- | --- |
| **K0c** | laminar differentially heated cavity, Ra 1e3-1e6 | de Vahl Davis | **GATE PASS**, 0 of 20 graded rows failed (D419 corrected the denominator from 24) |
| **K0cS** | turbulent square cavity, Ra 1.58e9 | Ampofo & Karayiannis 2003 | **GATE FAIL**, `kOmegaSST` 8 of 10, `kEpsilon` 6 of 10, `LaunderSharmaKE` **REFUSED** |
| **K0cX** | turbulent tall cavity, AR 28.7, two Rayleigh numbers | Betts & Bokhari, ERCOFTAC Case 079 | **GATE FAIL** on all three models, 24 of 42 rows (D420 corrected from 60) |
| **K0cT** | tall cavity Nusselt regrade | as above | **GATE FAIL** |
| K0b | mesh sensitivity | internal | capability rung |
| K2b, K2e, KV1 | rack-row module, Boussinesq limit, heat-balance path | internal | capability and limit rungs, not gates against experiment |
| **K0d** | turbulent **mixed** convection | Blay 1992 | **NOT RUN.** Primary data **NOT OBTAINED** |

**No turbulence model has passed a turbulent thermal gate in this lab.** Three
models, two geometries, three Rayleigh decades, zero passes.

---

## 2. What is now attributable, which is new as of tonight

A deviation is model error only once discretisation error is bounded.

| Case | Attribution | Source |
| --- | --- | --- |
| **Tall cavity, `kOmegaSST` Nusselt, -24.8 %** | **model error, by a factor of 68** — 0.49 % movement over a 6.5x cell increase | D428 |
| **Tall cavity, `kEpsilon` Nusselt** | **not numerical** — it gets monotonically *worse* under refinement, +26.98 -> +29.92 -> +32.71 % | D428 |
| Tall cavity, `LaunderSharmaKE` Nusselt | **band straddled** — passes on coarse and finest, fails on the graded fine mesh | D428 |
| Tall cavity stratification | **divergent** for two of three models | D428 |
| **Square cavity, everything** | **NO BOUND AT ALL** until K0cG reports — two mesh levels only | K0cG pre-registration |

**Only 1 of 6 quantity-model pairs on the tall cavity is in the asymptotic
range.** That is the honest state of numerical error control on the thermal
side, and it is worse than the aerodynamic side's.

---

## 3. The closure finding, which is the deepest thing the thermal side owns

**The gradient-diffusion thermal closure `alpha_t = nu_t/Prt` is refuted on this
flow, three independent ways:**

1. **By experiment on the value** (D425, `K0cP`): no constant works. Ampofo's
   measured *wall* value 0.21 makes the error **66-67 points worse** and reverses
   the horizontal-wall heat flux; his measured *outer* value 1.02 helps by 5
   points and reaches nothing; the constant that would reach band extrapolates to
   **1.115-1.243**, above everything measured, and differs between meshes.
2. **By construction on the form** (D426, D427): Ampofo measured
   `alpha_t/nu = 0.90` where `nu_t/nu = 0.00`. A closure proportional to `nu_t`
   delivers **at most 0.18** at the physical `Prt`. **Reduced but not withdrawn**
   after a second flagged point was found to sit at the velocity maximum, where
   the paper itself declares `nu_t` discontinuous.
3. **By transmission** (D424): `Prt_eff` measured **exactly 0.8500 in every
   cell**, so a better stress closure was forced by a constant into being a worse
   heat-flux closure — `SSG` improved the velocity field by 19 points and
   degraded the wall heat flux by 30.

**And the obvious replacement was ruled out before it was built** (D427): GGDH's
diffusivity is bounded by `3.529 nu_t`, so it vanishes in the same place, and
near this wall it would *lower* the wall-normal diffusivity, which D424 measured
raises Nusselt on a rung already over-predicting it.

**The indicated direction — a buoyancy-driven flux term requiring transported
temperature variance — is named and NOT built.**

---

## 4. The reference base, and what is missing from it

| Held | Tier |
| --- | --- |
| Ampofo & Karayiannis 2003, square cavity | READ IN FULL; Fig. 11 digitised (D417) with +/- 0.15 |
| Betts & Bokhari, ERCOFTAC Case 079 | primary data files, 22 kept |
| de Vahl Davis | reference values in the K0c gate |

| **NOT OBTAINED** | Blocks |
| --- | --- |
| **Tian & Karayiannis Part II** | every K0cS turbulence statistic is single-source (X6) |
| **Blay, Mergui & Niculae 1992** | **all of K0d — the entire mixed-convection class** |
| **Schwenke 1975** | the Annex 20 nonisothermal case |
| **Vogel & Eaton 1985** | heated backward-facing step; regime match unverified |
| **Any forced-convection heat-transfer reference** | **there is none in the library at all** |

**That last row is the structural gap.** A search of every paper sidecar for
Stanton number, Colburn analogy or Reynolds analogy returns essentially nothing.
**The thermal side cannot currently build a forced-convection rung, because it
has nothing to grade one against.**

---

## 5. Why the missing flow class matters more than another cavity rung

**Every thermal error this lab has measured is confounded.** On a buoyant cavity
the momentum field and the thermal field are both wrong, and they are coupled
through buoyancy, so a thermal-closure conclusion always carries a momentum
caveat. `K0cR` is the clean demonstration: fixing the stress closure moved the
velocity field 19 points *toward* the experiment and the heat flux 30 points
*away*.

**A forced-convection rung breaks that confound**, because the momentum closure
on a zero-pressure-gradient boundary layer is the best-validated thing this lab
owns. Any Stanton-number error there is attributable to the thermal closure
**alone**.

**It is also the cheapest possible rung to build and the most expensive to
reference.** The lab already has runnable TMR flat-plate cases, and running one
with `beta = 0` gives forced convection with a **built-in bit-for-bit control**:
the momentum solution must reproduce `simpleFoam` exactly. **The blocker is
entirely the reference, not the compute.**

---

## 6. What to do next, ranked, with what each costs and what blocks it

| # | Action | Cost | Blocker |
| --- | --- | --- | --- |
| **1** | **Obtain one forced-convection heat-transfer reference** — a correlation with stated validity, a DNS dataset, or an open benchmark | **not compute** | **requires a decision outside the compute authorisation.** This is the single highest-value unblocking action available |
| **2** | Finish `K0cG` and give the square cavity a discretisation bound | $0.19, running | none |
| 3 | Third mesh on the tall lo-Ra rung, and `LaunderSharmaKE` on the square | ~$0.3 | none |
| 4 | Temperature-variance transport closure | large | design, not compute |
| 5 | X8: the three cavity closures on an aerodynamic case, one instrument | $0.246 | none; `LaunderSharmaKE` has never been run on any aerodynamic case here |
| 6 | X5, X1 | $0.17 | X1 needs its pre-registration rewritten (addendum 1 §A3) |
| — | **K0d mixed convection** | — | **Blay primary NOT OBTAINED**; explicitly outside the compute authorisation |

**Item 1 is the recommendation.** Four of the seven rows above are limited by
references rather than by compute, and the compute authorisation cannot buy a
paper. **The thermal side is not compute-limited. It is reference-limited**, and
that is the difference between it and the aerodynamic side.

---

## 7. What this document is not

- **Not a gate.** It grades nothing and no verdict here is new.
- **Not a claim that the cavity work is finished.** X4 arm (b), X5, X8 and the
  variance-transport programme are all open.
- **Not a substitute for `VALIDATION_INVENTORY.md`**, which counts the
  population and states the tiers. This states the capability and the gaps.
- **Nothing here was submitted, sent, filed, uploaded or registered.**
  Submissions are PARKED.
