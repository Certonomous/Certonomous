# T1b design: the wall-treatment decision, and why it is graded rather than chosen

Campaign T, tier 1, rung T1b. Written 2026-08-19, **before any case was built.**
Extends `T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md` §3, whose band is already
armed and committed (`T1b_band.json`).

---

## 1. The decision that has to be made first

Dittus–Boelter and Gnielinski are **empirical correlations fitted to
experiment.** They describe physical reality, not a numerical method — so
"does this lab reproduce them" can be asked of a **wall-resolved** mesh or a
**wall-function** mesh, and the two are different questions.

**Wall-resolved (`y⁺ ≈ 1`) isolates the thermal closure.** It is the
configuration D429 argued for: the momentum solution on a smooth pipe is the
best-validated thing this lab owns, so a Nusselt error with correct friction is
attributable to the thermal closure alone.

**Wall functions (`y⁺ ≈ 50`) are what industry actually runs**, and there the
Nusselt number depends on the *thermal wall function* and its `Pr_t` — often more
than on the turbulence model.

**Choosing one would throw away a result, so both are built.** The difference
between them is not a nuisance to be minimised; **it is a measurement of how much
of the thermal answer is the wall treatment rather than the model**, and this
lab has never quantified that.

### REGISTERED PREDICTION

**The two wall treatments will differ by MORE than the armed band** (2.84–5.75 %
across the sweep). If they differ by less, the wall treatment does not matter at
these Reynolds numbers and that is itself reportable. **If they differ by much
more than the band, then no single "does OpenFOAM match Dittus–Boelter" claim is
meaningful without naming the wall treatment**, and every such claim this lab
makes later must carry that qualifier.

---

## 2. What is graded, and against what

The band is **already armed and committed**, computed before any case existed:
reference = the midpoint of the two correlations, band = the half-spread —
**2.84 / 3.89 / 5.33 / 5.75 %** at `Re` = 1×10⁴ / 3×10⁴ / 1×10⁵ / 3×10⁵.

**Friction is graded separately and it is the attribution lever.** `f` against
the Petukhov smooth-pipe relation. **A friction error is a solver or mesh fault;
a Nusselt error with correct friction is the thermal closure.** That separation
is the entire reason a forced-convection rung was ranked first.

---

## 3. The cases

`D = 0.2 m`, `nu = 1.5e-5`, `Pr = 0.71`. **The diameter is set by a constraint,
not by taste:** at `Re = 3×10⁵` a 0.02 m pipe would need `U = 225 m/s`, which is
Mach 0.66 and not incompressible. At `D = 0.2 m` the same Reynolds number runs at
**22.5 m/s**, Mach 0.066.

| arm | wall treatment | target `y⁺` | `Re` | mesh levels |
| --- | --- | ---: | --- | ---: |
| `R_*` | resolved, low-Re `kOmegaSST` | ≈1 | all four | **3** |
| `W_*` | wall functions | ≈50 | all four | 1 |
| `P_*` | resolved, `Pr_t` = 1.0 | ≈1 | all four | 1 |
| `C_lam` | **laminar — the trivial baseline** | — | 1×10⁴ | 1 |

**`C_lam` is the Charter §2c control and it is registered before the rung
exists**, because D433 retired four rows across two geometries that a laminar
solution passed. At `Re = 10⁴` laminar gives `Nu = 3.657` against a reference of
**30.907** — a factor of 8.5 outside the band. **A row this control passes grades
nothing.**

**`P_*` is the discrimination test** registered in T1 §7.1: `Pr_t` 0.85 → 1.0 is
of order 15 %, between 2.6 and 5.3 times the armed band, so **this rung must
separate them at every swept Reynolds number or it is too blunt to grade a
thermal closure.**

---

## 4. Two preconditions that are measured, never assumed

**4.1 Fully developed flow.** Turbulent pipe flow needs a long entry — far longer
than the laminar `0.05 Re D`, and estimates in the literature spread from about
10 to 60 diameters. **This design does not pick one and hope.** `L = 100 D`, the
station is at `80 D`, and **Nusselt is also measured at 60 D and 70 D**: if it has
not plateaued to within a fifth of the band across those three stations, the case
is **NOT A RESULT** and no development claim is made for it.

**4.1a The wall-function arm does not exist at every Reynolds number, and that
is a finding rather than a build failure.** A `y⁺ = 50` first cell has height
`2·50·nu/u_tau`. Against `R = 0.1 m`:

| `Re` | first cell | as a fraction of `R` | cells that fit across `R` |
| ---: | ---: | ---: | ---: |
| 1×10⁴ | 3.19e-02 | **31.9 %** | **3** |
| 3×10⁴ | 1.23e-02 | 12.3 % | 8 |
| 1×10⁵ | 4.22e-03 | 4.2 % | 23 |
| 3×10⁵ | 1.57e-03 | 1.6 % | 63 |

A geometrically growing mesh needs `first ≤ R/N`, so **at `Re = 10⁴` a
wall-function mesh would have three cells across the radius, the first of them a
third of the pipe.** No tuning fixes it: at low Reynolds number the viscous
sublayer occupies a large fraction of a small pipe. **The arm is built only at
`Re` = 1×10⁵ and 3×10⁵, and its absence below that is reported with the
arithmetic rather than passed over.**

**4.2 The achieved `y⁺`.** The target is a mesh input; the achieved value is an
output and is **reported per case**. A wall-function case that lands below
`y⁺ ≈ 30` is outside the wall function's own validity and is reported as such
rather than graded — **the same defect class as T1c's saturation guard firing on
an arm it could not judge, and it is registered here in advance instead of being
discovered afterwards.**

---

## 5. Carried forward from T1c, because they were paid for once

- **The wall radius is READ from `polyMesh/points`, never taken as `D/2`.** In
  T1c that assumption cost 9 % of the Nusselt number and produced a false
  DIVERGENT verdict.
- **`writeInterval` strictly less than `endTime`** (L-140).
- **The iterative-convergence gate**: no grid claim from a triple containing a
  level still moving between its last two checkpoints. In T1c **no case tripped
  `residualControl`**, and the offending case's residual was an unremarkable
  4e-05, so the residual is not the instrument — **the written fields are.**
