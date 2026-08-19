# K0cP. The defect is the FORM of the closure, not the value: results

Campaign F14, gate K0c. Solved 2026-08-19 01:06Z to 01:51:16Z; analysed 01:52Z.
Pre-registration `K0cP_PREREGISTRATION.md`, committed `4d4f9e78` at **01:05:41Z**,
before the first solve. Run tree `K0cP_runs/`, record `gate_k0cp.json`.
4 cases, 4 markers, all `rc=0`.

---

## 1. Verdict: FORM. Both registered predictions were met, in direction and in scale

| Case | `Prt` | `alpha_t` scale | `Nu_hot` baseline | `Nu_hot` arm | deviation | change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `P021_sq_c` | **0.21** | **x4.048** | 74.329 (+17.15 %) | **116.430** | **+83.50 %** | **-66.35 pts** |
| `P021_sq_f` | **0.21** | **x4.048** | 76.488 (+20.55 %) | **119.026** | **+87.59 %** | **-67.04 pts** |
| `P102_sq_c` | **1.02** | **x0.833** | 74.329 (+17.15 %) | 71.256 | **+12.30 %** | **+4.84 pts** |
| `P102_sq_f` | **1.02** | **x0.833** | 76.488 (+20.55 %) | 73.202 | **+15.37 %** | **+5.18 pts** |

§3 registered, before compute: *`Prt = 0.21` -> substantially WORSE*, and
*`Prt = 1.02` -> modestly BETTER, and does not reach the 10 % band.* **Both
happened.** The 10 % band is not reached by either arm on either mesh, so the
VALUE branch did not fire.

**The value Ampofo measured AT THE WALL is the one that damages the answer
most.** `Prt = 0.21` is the correct local number in the region that sets the
wall heat flux, and imposing it everywhere made a 17-20 % over-prediction into
an **84-88 %** one.

---

## 2. `Prt = 0.21` did not merely degrade the answer, it reversed the horizontal walls

| Row | baseline | `Prt = 0.21` | band |
| --- | ---: | ---: | ---: |
| `Nu_bot` | 8.819 (-38.9 %) | **-11.107 (-176.9 %)** | 20 % |
| `Nu_top` | 9.111 (-39.4 %) | **-10.229 (-168.0 %)** | 20 % |
| `Sp` | 0.4925 (**PASS**) | 0.1499 (-0.331, **FAIL**) | 0.12 |
| `Nu_mid_hot` | 78.62 (+33.8 %) | 122.58 (**+108.6 %**) | 12 % |

**The horizontal-wall Nusselt numbers changed sign.** With four times the
turbulent thermal diffusivity, the cavity transports so much heat through the
core that the top and bottom walls reverse their heat flux direction relative to
the reference convention. **And the stratification row, which the baseline
PASSED, was driven far outside its band** — 0.012 to -0.331 against 0.12.

**A single constant, set to a value the experiment measured, broke rows the
constant-0.85 baseline had passed.** That is the FORM reading in its strongest
form.

---

## 3. `Prt = 1.02` improves nearly everything and reaches nothing

| Row | baseline dev | `Prt = 1.02` dev | change | in band? |
| --- | ---: | ---: | ---: | --- |
| `Nu_hot` | +20.55 % | +15.37 % | +5.18 | **no** |
| `Nu_cold` | +19.12 % | +14.09 % | +5.04 | **no** |
| `Nu_bot` | -38.87 % | -33.60 % | +5.27 | **no** |
| `Nu_top` | -39.25 % | -34.63 % | +4.62 | **no** |
| `Nu_mid_hot` | +37.83 % | +30.59 % | +7.24 | **no** |
| `Nu_max_hot` | -27.96 % | -28.70 % | **-0.74** | no |
| `Sp` | +0.008 | +0.020 | -0.01 | yes (both) |
| `uv_peak` | +15.36 % | +16.46 % | -1.11 | yes (both) |

Every wall-averaged Nusselt row improved by 4.6 to 7.2 points. **None reached
its band**, and `Nu_max_hot` — the local peak — moved the other way. **The
tall-cavity prediction this rung inherited from `K0cX` (`P_hi_f_KE`, where
`Prt` 0.85 -> 1.283 moved Nusselt +29.92 % -> +11.45 %) is reproduced in
direction on a different geometry.**

---

## 4. The constant that would work is outside the measured range, and the two meshes want different ones

Fitting `Nu ~ alpha_t^b` through the two points each mesh provides — **an
extrapolation from two points, and labelled as one**:

| Mesh | fitted exponent | `alpha_t` scale to reach the 10 % band | implied constant `Prt` |
| --- | ---: | ---: | ---: |
| coarse | 0.2316 | x0.762 | **~1.115** |
| fine | 0.2408 | x0.684 | **~1.243** |

**Ampofo measured `Prt` nowhere above 1.02** anywhere in the boundary layer
(D417). **Both extrapolated constants exceed every value the experiment
recorded**, and the two meshes disagree with each other by 0.13.

**So the constant that would make this rung pass is (a) unphysical against the
measurement it is supposed to represent, and (b) mesh-dependent.** That is the
compensating-error signature this lab already names on the aerodynamic side: a
coefficient tuned to make an integral right, at a value the physics does not
support, which then fails to transfer.

---

## 5. D424's transmission mechanism was given a chance to break and did not

`K0cP_PREREGISTRATION.md` §3.1 carried a **REFUTED** branch: *if `Prt = 0.21`
makes it better, the mechanism in §3 is wrong and D424's transmission argument
is withdrawn with it.*

**D424 was measured entirely on already-solved fields and had never been tested
by changing anything.** This rung changed something. The prediction it implied —
that scaling `alpha_t` up by 4.05 would drive the over-prediction sharply
further up — **was registered before compute and came out at 66-67 points in the
predicted direction.**

**The mechanism now rests on a prediction that was made in advance and could
have failed.** It is no longer only an interpretation of static fields.

---

## 6. §2c and the rows that carry nothing

**No arm reached the band on any Nusselt row, so there are no hollow passes to
report on the deciding quantity.** `Sp` and `uv_peak` stayed in band on the
`Prt = 1.02` arm, and the laminar control fails both, so those passes carry
evidence — but they are also rows the **baseline already passed**, so they
discriminate the arms from nothing.

---

## 7. Cost, and a check on the cost model

| Case | exec s | baseline s |
| --- | ---: | ---: |
| `P021_sq_c` | 635.16 | 669.94 |
| `P021_sq_f` | 2574.33 | 3055.73 |
| `P102_sq_c` | 575.59 | 669.94 |
| `P102_sq_f` | 2704.29 | 3055.73 |
| **Total** | **6489.4 s** | 7451.3 estimated |

**108.2 core-minutes = 1.803 core-hours = $0.0925**, against a pre-registered
$0.106.

§5 predicted this estimate would be **accurate rather than conservative**,
because changing `Prt` changes no equation count. **It came in 13 percent under**,
and every arm ran faster than its baseline — the same concurrency confound
`K0cQ` recorded, since these four ran together and the baselines did not. **The
prediction was right about the mechanism and the residual is machine load, not
model cost.**

---

## 8. What this rung establishes, and what it hands to X4 arm (b)

- **No constant turbulent Prandtl number can close this cavity.** The measured
  field runs 0.00 to 1.02 across the layer; the wall value makes it four times
  worse; the outer value helps and stops short; and the value that would work is
  above everything measured and differs between meshes.
- **The defect is the FORM of the gradient-diffusion closure**, which is what
  D415 argued from Ampofo's prose — *"a constant turbulent Prandtl number cannot
  represent a discontinuous field"* — and what D417 measured. **This rung is the
  first time that argument has been tested by running something.**
- **It does NOT show that a variable `Prt` fixes the cavity.** Two constants
  bracketing a profile are not the profile. **That is X4 arm (b)**, and this rung
  exists to say that arm (b) is testing something real.
- **Nothing here was submitted, sent, filed, uploaded or registered.**
  Submissions are PARKED.
