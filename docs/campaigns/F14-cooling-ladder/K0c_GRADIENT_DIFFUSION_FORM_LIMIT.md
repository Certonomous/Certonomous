# The measurement lies outside the gradient-diffusion closure's range, not at an awkward point inside it

Campaign F14, gate K0c. Written 2026-08-19. **Zero compute. Grades nothing.**
Instrument: `verification/runs/F14-cooling-ladder/K0cS_runs/form_limit.py`.
Input: the D417 digitisation of Ampofo Fig. 11 and its stated reading
uncertainty. **No solve was run and no verdict moves.**

---

## 1. The claim

**A gradient-diffusion thermal closure sets `alpha_t = nu_t / Prt`, so `alpha_t`
is PROPORTIONAL to `nu_t` and `Prt` fixes only the constant of proportionality.**
Wherever `nu_t` vanishes, the closure forces `alpha_t` to vanish — for every
finite positive `Prt`, constant or field.

**Ampofo measured substantial turbulent thermal diffusivity in a region where he
measured no eddy viscosity.**

| X = x/L | measured `alpha_t/nu` | measured `nu_t/nu` | `Prt` required to reproduce `alpha_t` from `nu_t` |
| ---: | ---: | ---: | --- |
| 0.0037 | **0.90** | **0.00** | **0.0000** |
| 0.0067 | **2.40** | **-0.05** | **-0.0208** |

**To reproduce the measurement pointwise the closure needs `Prt = 0` at
X = 0.0037 and `Prt < 0` at X = 0.0067.** A gradient-diffusion closure requires
`Prt` to be **positive and finite**. `Prt = 0` is an infinite thermal
diffusivity; `Prt < 0` is counter-gradient heat transport with co-gradient
momentum transport.

**So the measurement is not an awkward point inside the closure's range. It is
outside it.**

---

## 2. It survives the reading uncertainty, which is why it is stated as a result

D417 carries **+/- 0.15** on both `alpha_t/nu` and `nu_t/nu`. The test was run at
the **most generous** setting available to the closure: `nu_t` at the top of its
uncertainty band, divided by **0.21**, the smallest `Prt` the experiment shows
anywhere in the layer.

| X | measured `alpha_t/nu`, low end of its band | most the closure can deliver | gap |
| ---: | ---: | ---: | ---: |
| 0.0037 | **>= 0.75** | **<= 0.71** | closure short |
| 0.0067 | **>= 2.25** | **<= 0.95** | **closure short by 2.4x** |

**Even granting the closure every benefit the uncertainty allows, it falls short
at X = 0.0067 by more than a factor of two.**

---

## 3. What this refutes, and what it does not

**Refuted: the FORM, on this flow, in this region.** Not the value of `Prt`, and
not any particular value. `K0cP` established the same conclusion by experiment —
no constant works, and the constant that would work is unphysical and
mesh-dependent — **and this establishes it by construction, from the measurement
alone, with no solve.** The two are independent and they agree.

**NOT refuted:**

- **Gradient diffusion elsewhere in the flow.** From X = 0.0095 outward the
  required `Prt` runs 0.29, 0.88, 1.00, 1.00, 1.00 — ordinary values. **The form
  fails in the inner layer and is unremarkable outside it**, and the inner layer
  is where the wall heat flux is set.
- **Gradient diffusion on other flows.** This is one cavity, one figure, one
  digitisation carrying +/- 0.15.
- **Any claim that a specific alternative closure succeeds.** Nothing here has
  been run.

---

## 4. This redirects X4 arm (b), and the redirection is the point

`K0c_THERMAL_CLOSURE_SYNTHESIS.md` §8 registered X4 arm (b) as *"a generalised
gradient-diffusion `alpha_t` through `fvOptions`"*, and `K0cP_RESULTS.md` §8
handed it the job of testing whether **a variable `Prt`** fixes the cavity.

**A variable `Prt` cannot fix it, and this document is why.** A variable `Prt`
still sets `alpha_t` proportional to `nu_t` pointwise; it changes the constant of
proportionality from place to place and leaves `alpha_t = 0` wherever `nu_t = 0`.
**The two points that refute the form refute the variable-`Prt` version of arm
(b) along with it.**

**The closure family that can reach these points is one whose heat flux is not
proportional to a scalar eddy viscosity.** The generalised gradient diffusion
hypothesis forms the turbulent heat flux from the **Reynolds stress tensor**,

    q_i = -C_theta (k/epsilon) <u_i u_j> dT/dx_j

so it carries a heat flux wherever the **stress tensor** is non-zero, which is
not the same set of places as where a scalar `nu_t` is non-zero. **K0cR
established that `SSG` runs on both cavities, converges, and keeps `R`
realizable on every cell**, so the tensor this closure needs is already
available in this lab.

**Arm (b) should therefore be built as GGDH on top of `SSG`, not as a variable
`Prt` on top of `kEpsilon`.** That is a change to a registered experiment's
design, made **before it is run**, on evidence, and recorded here rather than
made silently.

---

## 5. Where this sits against the lab's aerodynamic side

The aerodynamic side already owns this shape of argument. `W3_QCR_DUCT_FALSIFIER.md`
records the linear eddy-viscosity model reading **5.5e-16** for a secondary flow
the experiment measures at **0.813 percent** — *a structural zero*, a quantity
the closure form cannot produce at any coefficient. **QCR was built because of
it.**

**This is the thermal counterpart of that finding, and it arrives with the same
signature:** a measured quantity the closure form yields **zero** for, which no
coefficient can rescue. The aerodynamic side answered it by writing a
constitutive model. **The thermal side has not answered it yet.**

---

## Dated correction, 2026-08-19 — one of the two points was at the velocity maximum, where the paper says the eddy viscosity is discontinuous

**Nothing above is edited.** W-4. **§1 and §2 rested on two points. One of them
must be withdrawn, and the source says so in its own words.**

### What was wrong

`X = 0.0067` is **the measured velocity maximum**. The K0cS gate's G9 row puts
Ampofo's peak velocity location at **X = 0.00667**. Ampofo p. 3569:

> *"Reynolds stress takes a very small value of almost zero near the wall, in
> the presence of a large mean velocity gradient and has a positive value at the
> maximum velocity location (ov/ox = 0) without u'v' becoming zero. **Therefore,
> the distribution of turbulent viscosity for momentum has a discontinuity at the
> maximum velocity location.**"*

`nu_t = -u'v' / (ov/ox)` is **singular** there. A plotted value near zero at that
X is **the rendering of a discontinuity, not a measurement of a small eddy
viscosity**, and using it as though it were a measurement is the error.

**The instrument was corrected** — `form_limit.py` now excludes a guard band
around `X = 0.00667` and says why — **and the point is withdrawn from the
argument.** D415 had already recorded this discontinuity from the same page;
this document failed to apply it to its own evidence.

### What survives, and its margin stated honestly

**`X = 0.0037` survives, and Ampofo's own sentence supports it.** That point lies
**between the wall and the velocity maximum**, where the paper says the Reynolds
stress is *"almost zero near the wall, in the presence of a large mean velocity
gradient"* — so `nu_t` there is **well defined and genuinely small**, which is
exactly the condition the argument needs.

| At `X = 0.0037` | value |
| --- | ---: |
| measured `alpha_t/nu` | **0.90**, and **>= 0.75** at the low end of +/- 0.15 |
| measured `nu_t/nu` | **0.00**, and **<= 0.15** at the high end |
| closure delivers at the physical `Prt = 0.85` | **<= 0.18** |
| closure delivers at `Prt = 0.21`, the smallest the figure shows anywhere | **<= 0.71** |

**At the physical `Prt` the closure is short by more than a factor of four. At
the most generous `Prt` in the measurement it is short by 0.04, which is
marginal and is reported as marginal.**

**The conclusion of §1 stands on one point rather than two, and with a thinner
margin than §2 claimed.** It is not withdrawn; it is reduced.

---

## The same test applied to GGDH, before building it — and GGDH fails it too

**§4 above proposed building arm (b) as GGDH on top of SSG. That proposal is
withdrawn, on two measurements taken before any code was written.**

### 1. GGDH's diffusivity is bounded by a multiple of `nu_t`, so it vanishes in the same place

GGDH sets `D_ij = C_theta (k/eps) <u_i u_j>`. Choosing `C_theta` so that GGDH's
**isotropic part exactly equals the existing `alpha_t`** — the design that
isolates tensorial character from magnitude, exactly as `Ccr1` does for QCR —
gives

    C_theta = 3 Cmu / (2 Prt) = 0.158824

**verified against the lab's own SSG fields**, where `nu_t . eps / k^2 = 0.090000`
and `alpha_t/nu_t = 1.176471` hold to six decimals in **all 14 400 cells**.

Since every diagonal `<u_i u_i> <= 2k`, the wall-normal diffusivity obeys

    D_nn <= (2 C_theta / Cmu) nu_t = 3.529 nu_t

**So at `X = 0.0037`, where `nu_t/nu <= 0.15`, GGDH delivers at most 0.53 against
a measured 0.75 at the low end. GGDH cannot reach it either.**

### 2. Worse: near this wall GGDH moves the diffusivity DOWN, not up

Measured in the lab's own converged SSG solution, `R_sq_c`, out from the hot wall
at mid-height:

| cell | x/L | `R_xx` / `(2k/3)` |
| ---: | ---: | ---: |
| 0 | 1.67e-04 | **0.935** |
| 1 | 5.14e-04 | **0.771** |
| 2 | 8.91e-04 | **0.689** |
| 3 | 1.30e-03 | **0.648** |
| 4 | 1.74e-03 | **0.631** |
| 5 | 2.22e-03 | **0.625** |

**The wall-normal Reynolds stress is damped to 0.63-0.94 of isotropic**, which is
what wall blocking does to the normal component. So GGDH's wall-normal
diffusivity is **6 to 37 percent SMALLER** than the isotropic `alpha_t` it
replaces.

**And D424 measured what less near-wall diffusivity does on this cavity: it
steepens the wall temperature gradient and RAISES the Nusselt number**, on a rung
that already over-predicts it. **GGDH would therefore be expected to make the
over-prediction worse**, in the same direction and by the same mechanism as SSG
already did.

### 3. What this leaves

**Arm (b) should not be built as GGDH.** Both the bound and the direction were
established from measurements already on disk, at zero compute, **before the
model was written** — which is the only time such a check is cheap.

**The indicated direction, stated as a direction and not as a result:** the
measurement asks for a turbulent heat flux that does **not** scale with `k^2/eps`
in the near-wall region. The closure families that carry one are those with a
**buoyancy-driven flux term**, which requires the **temperature variance** as a
transported quantity rather than an algebraic function of `k`. **That is a
larger programme than a coded `fvOption`, and naming it is not running it.**

**Nothing in this section has been run. It is an argument from two measurements
about what would happen, and it is recorded so that the experiment it cancels is
cancelled in the open.**
