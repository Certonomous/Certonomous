# T1. The forced-convection canon: an exact-theory and two-correlation gate

Campaign T, tier 1, rung T1. Written 2026-08-19, **before any case was built or
solved.** Run tree `verification/runs/T-family/T1_runs/` (not yet created).

---

## 1. Why this rung is first, and why its three parts are re-ordered

The standing diagnosis (`docs/THERMAL_CAPABILITY_STATE.md`, D429) is that **the
thermal side is reference-limited, not compute-limited.** K0e demonstrated the
consequence exactly: it is fully specified, cheap, and **cannot gate**, because
**no band can be honestly derived from a single correlation** — a source that
states a fit without stating its own uncertainty arms nothing, and setting the
band to the deviation models happen to show would be setting the band to the
answer.

**T1 is the rung that breaks that, and the mechanism is in the brief: where two
independent published correlations describe the same quantity, their
disagreement is a MEASURED band rather than a chosen one.** It is citable,
reproducible from the published formulae alone, and it cannot be tuned to a
result because **it is computed before any case is solved and does not depend on
any solution.**

**The three parts are therefore attacked in the order (c), (b), (a), which
inverts the brief, and the reason is stated rather than assumed:**

1. **T1c, laminar pipe — EXACT THEORY.** `Nu = 3.657` and `Nu = 48/11`, plus
   `f·Re = 64`, are closed-form results, not fits. **Nothing needs sourcing and
   nothing can be argued about the reference.** It is the only thermal rung this
   lab can build whose reference is beyond dispute, so it goes first and it
   calibrates the numerics that everything above it inherits.
2. **T1b, turbulent pipe — TWO CORRELATIONS.** The self-arming band.
3. **T1a, flat plate — ONE CORRELATION.** This is K0e, and it is last because it
   is the part the band mechanism helps least; §5 records what would have to be
   true for it to gate.

**If Sanaa prefers the brief's order, that is a re-ordering of work and not a
change to any registered number.**

---

## 2. T1c — fully developed laminar pipe flow, against closed form

### 2.1 The references, which are derivations

| quantity | value | boundary condition |
| --- | --- | --- |
| `Nu_D` | **3.657** | constant wall temperature |
| `Nu_D` | **48/11 = 4.3636…** | constant wall heat flux |
| Darcy `f` | **64/Re** | either |

**These are exact solutions of the fully developed problem, and they are
reproduced in the rung's own comparator from the derivation, not typed in from a
textbook page.** `f·Re = 64` follows from the Hagen–Poiseuille profile; `48/11`
follows from integrating that profile against a linear axial temperature rise.
**Any disagreement is the lab's error, never the reference's.** A rung whose
reference cannot be wrong is the right instrument for separating solver error
from closure error, which is the confound D429 named.

### 2.2 The band, which is derived and not chosen

**No band is typed into this specification.** The band is the **numerical
uncertainty of this lab's own solution**, established by a three-level mesh
refinement and reported as a **Roache GCI at Fs = 1.25** on the finest mesh, by
the same `grid_convergence.py` classification D428 shipped. **Three levels, not
two** — K0cS's missing third level is the whole reason K0cG exists, and this
rung will not repeat it.

**Registered consequence:** if the observed order is OSCILLATORY, STAGNANT or
DIVERGENT, **no band is armed and the row reports NOT A RESULT.** It does not
fall back to a chosen number.

### 2.3 The controls, registered as rows that MUST fail

**This is written in deliberately, because D433 retired four rows across two
geometries that a laminar solution of a turbulent flow passed.** A rung whose
controls are designed after the fact inherits that defect. Each control below is
a row that **fails if the rung is sound**:

- **C1, thermally developing.** `Nu_D` sampled at `x/D = 1`, inside the thermal
  entry length. **MUST exceed the fully developed constant substantially**; a
  band that admits it is a band too wide to grade with.
- **C2, wrong boundary condition.** The constant-`q"` case graded against
  **3.657** instead of 4.364. **MUST FAIL** — the two constants differ by 19 %,
  so a band that admits both cannot tell the two thermal boundary conditions
  apart, and a rung that cannot do that is measuring nothing.
- **C3, under-resolved radially.** The coarsest mesh graded against the finest
  mesh's band.

**C2 is the discrimination test in its sharpest form: 19 % is the smallest
physically meaningful separation this rung must resolve, so the armed band must
come in well under it or the rung is declared unable to grade.**

### 2.4 Row tags

Rows are tagged **`L1 … Ln` at creation, in build order, before any split**, and
the tags are carried in the row records themselves. **Positional tags are not
identifiers** — D433 established that by measuring it, when a retirement
renumbered every later row and silently re-pointed historical citations.

---

## 3. T1b — fully developed turbulent pipe flow, against two correlations

### 3.1 The two correlations and their stated validity

**Dittus–Boelter**, `Nu = 0.023 Re^0.8 Pr^n`, `n = 0.4` heating / `0.3` cooling.
Stated validity: `0.6 ≤ Pr ≤ 160`, `Re ≳ 10^4`, `L/D ≳ 10`.

**Gnielinski**, `Nu = (f/8)(Re − 1000)Pr / [1 + 12.7 (f/8)^{1/2} (Pr^{2/3} − 1)]`
with the Petukhov friction factor `f = (0.790 ln Re − 1.64)^{-2}`.
Stated validity: `0.5 ≤ Pr ≤ 2000`, `3000 ≤ Re ≤ 5×10^6`.

**Both formulae are evaluated in the comparator from the expressions above.
Neither is a digitised curve and neither is transcribed from a table.**

### 3.2 The band mechanism, stated before any case exists

At each swept Reynolds number the comparator computes both correlations and
takes the reference as their **midpoint**, with the **half-spread as the band**:

```
Nu_ref(Re) = (Nu_DB + Nu_Gn) / 2
band(Re)   = |Nu_DB − Nu_Gn| / 2
```

**Why this is honest and not convenient:** it is fixed by two published formulae
and the swept Reynolds numbers alone, so **it is fully determined before a
single case is solved and no solution can move it.** It is also the correct
statement of what the literature actually knows — where two accepted
correlations disagree by 15 %, a claim to 5 % accuracy is a claim about the
correlations, not about the solver.

**Registered honesty condition, and it is the one that can embarrass this rung:
where the two correlations agree closely the band becomes very small, and a
solution may fail against a band far tighter than any correlation's own accuracy.
That is registered as a REPORTED failure and NOT a GATE FAIL**, because the band
would then be measuring the correlations' coincidental agreement rather than the
lab's error. **The threshold is registered now: where the half-spread falls below
2 % of the midpoint, the row is REPORTED, NEVER GRADED.**

### 3.3 The sweep and the friction check

`Re ∈ {1×10^4, 3×10^4, 1×10^5, 3×10^5}` at `Pr = 0.71` (air), all inside both
correlations' stated validity. **The Prandtl number is inside Dittus–Boelter's
`0.6 ≤ Pr` floor by a small margin and that is noted, not hidden.**

**Friction factor is graded separately against the smooth-pipe relation**, and it
matters more than it looks: **the momentum solution is the best-validated thing
this lab owns, so a friction error is a solver or mesh fault, while a Nusselt
error with correct friction is attributable to the THERMAL closure alone.**
**That attribution is the entire reason a forced-convection rung was ranked
first in D429**, and it is why friction is graded and not merely reported.

---

## 4. T1a — turbulent flat plate

**This rung is K0e**
(`docs/campaigns/F14-cooling-ladder/K0e_FORCED_CONVECTION_FLAT_PLATE_GATE.md`),
already specified, with its reference obtained (Bahrami, NASA TM, sha256
`0cd29adb…`). **It is NOT re-specified here and none of its registered numbers
is touched.**

**What T1b offers it:** the same two-source mechanism, if and only if a second
*independent* route to the same quantity can be cited — for instance a
Colburn-analogy route `St · Pr^{2/3} = C_f/2` with `C_f` from a separately cited
skin-friction correlation, compared against a direct `Nu_x` correlation.
**Whether those two are genuinely independent is a question about the sources
and NOT something this specification may assume**; it is listed as work, not as
a result. **Until then K0e's §3 stands unchanged: BLOCKED and PENDING, unable to
PASS and unable to GATE FAIL by construction.**

---

## 5. What this rung cannot do

- **It cannot validate a turbulence model for separated or buoyant flow.** Fully
  developed pipe flow is the friendliest turbulent geometry there is; passing
  here is a **precondition** for the harder rungs, never a substitute.
- **It cannot resolve K0e's band problem.** §4 states what would.
- **T1c cannot fail a closure**, because a laminar solution has none. It grades
  the solver, the mesh and the boundary conditions — which is exactly what must
  be trusted before any closure claim above it means anything.
- **It says nothing about entrance effects, roughness, variable properties or
  buoyancy-affected forced convection**, all of which are excluded by the
  fully developed, smooth, constant-property, `Ri → 0` design.

---

## 6. Status

**NOT BUILT AND NOT RUN.** No case directory exists, no builder and no
comparator has been written, and **no compute has been spent.**

**The launch step is currently BLOCKED**: two attempts to start a solver in this
session were refused by the command classifier (D432). **The pre-registration is
written first regardless, which is the campaign's standing discipline and is
what makes an interrupted rung cheap to resume.**

**Per the campaign rule, the builder and the comparator are to be committed
before any case produces a result** (Charter §2d), and every dictionary line that
follows D432's finding — a `writeInterval` strictly less than `endTime` — so that
an interruption costs one interval and not the whole run.

---

## 7. The band, armed — computed before any case directory existed

`verification/runs/T-family/T1_runs/correlation_band.py`, run 2026-08-19 with
**no case built and no solver run**, writes `T1b_band.json`:

| `Re` | Dittus–Boelter | Gnielinski | reference (midpoint) | band | band % |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1×10⁴ | 31.786 | 30.028 | **30.907** | 0.879 | **2.84 %** |
| 3×10⁴ | 76.547 | 70.822 | **73.684** | 2.863 | **3.89 %** |
| 1×10⁵ | 200.554 | 180.243 | **190.398** | 10.156 | **5.33 %** |
| 3×10⁵ | 482.979 | 430.467 | **456.723** | 26.256 | **5.75 %** |

**All four points arm a band; none falls under the 2 % report-only floor.** The
half-spread **widens with Reynolds number**, 2.84 % to 5.75 % — the two
correlations agree best at the bottom of the sweep.

**This is the result K0e could not reach.** K0e arms **no** band from its single
correlation and is BLOCKED and PENDING by construction; **T1b arms four.**

**What the band is NOT, and it is written here so no later reader has to infer
it:** it is the **disagreement between two accepted correlations**, not either
correlation's own stated accuracy, which neither source provides. A solution
inside it is **consistent with the published canon — not verified to that
tolerance.**

### 7.1 The registered discrimination prediction

**A band is only worth arming if something real can fail it, and that is
predicted here, in writing, before any solve.** The turbulent Prandtl number is
the single dictionary scalar that most directly sets the thermal closure, and
`Nu` in the log layer varies roughly as `1/Pr_t`.

**REGISTERED PREDICTION: the change from `Pr_t = 0.85` to `Pr_t = 1.0` is of
order 15 %, which is between 2.6 and 5.3 times the armed band across the sweep.
This rung must therefore SEPARATE those two settings at every swept Reynolds
number.** If it does not, the band is too wide to grade a thermal closure with,
and that finding is **reportable as a failure of the rung**, not of the model.

**REGISTERED TRIVIAL BASELINE (Charter §2c): the same case with turbulence off.**
At `Re = 10⁴` a laminar solution gives `Nu = 3.657`, against a reference of
**30.907** — a factor of 8.5, far outside the band. **The row that a laminar
solution passes is the row that grades nothing (D433), so this control is
registered before the rung is built rather than checked after it reports.**
