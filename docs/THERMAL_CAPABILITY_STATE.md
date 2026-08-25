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
models, two geometries, **three Rayleigh numbers from 8.6e5 to 1.58e9, at two
effectively distinct conditions**, zero passes.

> **CORRECTED 2026-08-25 by the heat-transfer supervisor, by quote-and-strike
> (rule 6), under K0d `AMENDMENT 1` §A1.1.** The struck wording was:
>
> > ~~*"Three models, two geometries, three Rayleigh decades, zero passes."*~~
>
> **The ground.** The three Rayleigh numbers are **8.6e5** and **1.43e6** (tall
> cavity AR 28.7, Betts & Bokhari, K0cT / K0cX) and **1.58e9** (square cavity,
> Ampofo & Karayiannis, K0cS). Their `log10` values are **5.93, 6.16 and 9.20**.
> **The two low values differ by a factor of 1.66, not by a decade** — they are
> essentially one Rayleigh condition sampled twice. The true coverage is **two
> effectively distinct conditions about 1100x apart**, not three decades of it.
>
> **The defence for the old wording is recorded rather than suppressed:** under a
> *bin* reading the three values fall in the `1e5`, `1e6` and `1e9` bins, which
> makes "three decades" literally defensible. It is corrected anyway, because the
> phrase *reads* as three decades of coverage and this sentence is the lab's
> headline honest prior — it is quoted into `K0d_PREREGISTRATION.md` §11, where
> prediction 1 rests on it. **A prior must not be stronger than its evidence at
> the moment the prediction it supports is graded**, and correcting it before
> K0d's first compute weakens the prior slightly in the direction of the truth.
>
> **Unchanged: "zero passes".** That half is not touched, is not in doubt, and is
> the load-bearing half of the sentence.

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
| Meinders 1998 TU Delft thesis (added 2026-08-21, T-family) | OPEN primary for the heated-cube class; title-page verified; stated 5 %/10 % uncertainty in local h |
| ERCOFTAC case025 impinging jet (added 2026-08-21, T-family) | primary data files, 88 kept incl. 4 Nusselt tables; flow uncertainties stated, Nu uncertainty second-hand only |

| **NOT OBTAINED** | Blocks |
| --- | --- |
| **Tian & Karayiannis Part II** | every K0cS turbulence statistic is single-source (X6) |
| **Blay, Mergui & Niculae 1992** | **all of K0d — the entire mixed-convection class** |
| **Schwenke 1975** | the Annex 20 nonisothermal case |
| **Vogel & Eaton 1985** | heated backward-facing step; regime match unverified |
| **Any forced-convection heat-transfer reference** | **there is none in the library at all** [SUPERSEDED 2026-08-21: the Meinders thesis, the case025 Nusselt files and a digitised Smirnov 2016 secondary for Vogel & Eaton now exist in the library; the Vogel & Eaton primary itself remains NOT OBTAINED] |

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

---

## Dated correction, 2026-08-19 02:20Z — §6 item 1 said this needed a decision outside the compute authorisation. It did not, and it is now done

**Nothing above is edited.** W-4.

**§6 ranked "obtain one forced-convection heat-transfer reference" as the
highest-value action available and recorded its blocker as "requires a decision
outside the compute authorisation."** That was wrong in the direction §5 of
`K0cS_RESULTS.md` warns about and D415 has a name for: **the lab disclaimed a
reference it could have had for nothing.** The reasoning assumed the class was
paywalled because the four references already recorded as NOT OBTAINED are.
**An open route existed and was not looked for.**

### What was obtained

**Bahrami, P. A. (2005). *Heat Transfer on a Flat Plate with Uniform and Step
Temperature Distributions.* NASA/TM-2005-212841.** US government work, openly
distributed by NTRS. Tier **READ IN FULL** — full text fetched and read this
session.

Filed as `docs/papers/forced_convection_heat_transfer/bahrami_2005_nasa_tm_212841.pdf`
with its `.txt` sidecar, sha256
`0cd29adb20c0f6c21c07f37f101f0f8d3f3a7f85a81a95abc023da25a66f8be6`.
**It is the first entry in a topic folder this library did not have.**

### What it carries, quoted rather than summarised

| Item | Value, as printed |
| --- | --- |
| Reference correlation, uniform wall temperature | **`St = 0.0296 Re^-0.2 (Pr Tw/T_inf)^-0.4`**, eq. (1) |
| Stanton definition | `St = q / (Cp_inf rho_inf U_inf dT)` |
| Free-stream conditions | `U_inf = 19.39 m/s`, `T_inf = 309.4 K`, `rho_inf = 1.185 kg/m3` |
| Mach, unit Reynolds | `Ma = 0.055`; `Re/x = 1 215 400 m^-1` |
| Experimental uncertainties (Moretti & Kays) | temperature **3 %**, heat flux **2 %**, velocity **1 %** |
| Reported model behaviour | SST closest to the Von Karman analogy; `k-omega` higher and Baldwin-Lomax lower, with **"deviations of approximately 10 percent"** |

**The last row matters: this document states in advance roughly how far a
two-equation model lands from the reference on this flow.** A thermal rung built
here has a published expectation to be graded against, which no cavity rung had.

### Three limits, stated before the rung is designed

1. **The primary is still NOT OBTAINED.** Moretti & Kays (1965) exists here only
   as figures inside a secondary. Any use of their data would be a digitisation
   of a secondary, one tier below the Betts primary files.
2. **A correlation is not a measurement.** Eq. (1) is an empirical fit. Grading
   against it is grading against a fit, and the rung must say so.
3. **The circularity caution, which is the important one.** Eq. (1) is a
   Colburn-type correlation and sits in the same family as the Reynolds and Von
   Karman analogies — **and the Reynolds analogy is very close to what a
   constant-`Prt` gradient-diffusion closure asserts.** Agreement between a
   `Prt = 0.85` RANS solve and eq. (1) is therefore **partly structural rather
   than evidential**, and a rung that does not carry this caution would be
   claiming as validation something it partly assumed. **`Pr^-0.4` in eq. (1)
   against `Pr^-2/3` in the Colburn analogy is the gap that keeps it from being
   fully circular**, and that gap is the only part of the comparison that is
   genuinely a test.

### What this changes

- **§6 item 1 is closed.** The forced-convection class is now referenced.
- **§0's "no second flow class" and §5's confound argument are unchanged**, and
  become **actionable**: the lab has runnable TMR flat-plate cases and now has
  something to grade them against.
- **§4's last row — "any forced-convection heat-transfer reference: there is
  none in the library at all" — is superseded** and is left standing above as the
  state that was true when it was written.

**The rung is NOT built.** What exists is a reference, a set of conditions, an
uncertainty figure and a published expectation. **Naming that as a capability
would be the same error in the other direction.**

---

## Addendum 3 — 2026-08-19, the evening. The forced-convection class is no longer just referenced: it is GRADED.

**§0's headline — that every graded thermal result this lab owns is a
buoyancy-driven cavity — stopped being true today.** It is left standing above
as the state that was true when it was written.

### What changed

**T1c graded a thermal rung against a reference that cannot be wrong.** Fully
developed laminar pipe flow: `Nu = 3.6567934` for constant wall temperature (the
first Graetz eigenvalue, solved here by inverse iteration to `λ₀² = 7.313587`,
agreeing with tabulation to **1.6e-08**), `Nu = 48/11` for constant wall heat
flux, and `f·Re = 64`. **Each is derived twice in the rung's own code and the
comparator refuses to run if the two derivations disagree.**

| row | value | exact | deviation | band | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `f·Re` | 63.98771 | 64 | 0.0192 % | 0.0236 % (GCI) | **PASS** |
| `Nu`, constant `q″` | 4.365298 | 4.3636364 | 0.0381 % | 0.0459 % (GCI) | **PASS** |
| `Nu`, constant `Ts` | 3.659958 | 3.6567934 | 0.0865 % | 0.0301 % (GCI) | **GATE FAIL** |

**The rung verdict is GATE FAIL and it is not excused.** Both arms overshoot even
after Richardson extrapolation to zero mesh spacing (+0.111 %, +0.075 %), so the
excess is **not discretisation error**; its cause is under test against a
prediction registered before the diagnostic cases were built.

### What this does and does not do to §5's confound argument

**§5 said every thermal error this lab had measured was confounded, because on a
buoyant cavity the momentum and thermal fields are both wrong and coupled.**
T1c does not resolve that argument — **it removes the excuse for it.** The
laminar rung establishes that the solver, the mesh and the boundary conditions
reproduce exact theory to better than 0.1 % at second order, on **both** thermal
boundary conditions **and** on friction. **That is the precondition every
turbulent thermal claim above it rests on, and until today this lab had never
checked it.**

**T1c grades no turbulence model.** A laminar solution has no closure. The
unconfounded turbulent test is **T1b**, whose 19 cases are running and whose
comparator is frozen.

### §6's ranking, revisited

**§6 ranked "obtain one forced-convection heat-transfer reference" first, and
called it "not compute — requires a decision outside the compute
authorisation."** Addendum 2 closed that item by finding an open reference.
**Today's work shows the ranking itself was too pessimistic in one specific
way**: T1c needed **no reference at all**. Its constants are closed-form
solutions of the governing equations. **The cheapest forced-convection rung
available to this lab was one nobody had to obtain anything for**, and it sat
unbuilt while the docket recorded the class as reference-blocked.

**The generalisable form: "we are reference-limited" is true of the class, and
was not true of every rung in it.** Before ranking a class as blocked on an
acquisition, the exact-theory members of that class should be enumerated —
they have no acquisition step.

### And T1b arms the band K0e could not

K0e is BLOCKED and PENDING by construction because **no band can be honestly
derived from a single correlation**. T1b arms four, from a mechanism that costs
nothing: **where two accepted correlations describe the same quantity, their
disagreement is a measured band rather than a chosen one** — half-spreads of
**2.84 / 3.89 / 5.33 / 5.75 %** across the Reynolds sweep, computed and committed
before any case directory existed.

**What that band is NOT**, stated so no later reader has to infer it: it is the
disagreement between two correlations, **not either one's own accuracy**, which
neither source states. A solution inside it is **consistent with the published
canon — not verified to that tolerance.**
