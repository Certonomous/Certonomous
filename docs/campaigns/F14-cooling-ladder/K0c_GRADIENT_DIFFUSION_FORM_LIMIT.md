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
