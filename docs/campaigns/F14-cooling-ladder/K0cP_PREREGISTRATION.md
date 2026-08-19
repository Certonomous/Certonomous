# K0cP. Is the defect the VALUE of the turbulent Prandtl number or the FORM of the closure? Pre-registration

Campaign F14, gate K0c. Written 2026-08-19, **before any graded case was
solved**. Run tree `verification/runs/F14-cooling-ladder/K0cP_runs/`.

---

## 1. Why this rung exists now, and why it is not X4 arm (b)

**D424 measured the transmission path.** `Prt_eff` is **exactly 0.8500 at every
cell of every case**, so `alpha_t` is rigidly slaved to `nu_t` by one constant,
and X3's better stress closure was forced by that constant into being a worse
heat-flux closure.

**D417 measured what the constant should have been, and it is not a constant.**
Ampofo Fig. 11 digitised: `Prt` reads **0.21 at the wall**, **0.00 at
X = 0.0067**, 0.30 at 0.0095, 0.89 at 0.0133, and **0.89-1.02 over
X = 0.015-0.03**.

**X4 arm (b) — a generalised gradient-diffusion `alpha_t` through `fvOptions` —
is the right experiment and it needs solver-level code**, because
`buoyantBoussinesqSimpleFoam` reads `Prt` as a single `dimensionedScalar` from
`transportProperties` and recomputes `alpha_t = nu_t/Prt` every iteration.
**This rung is not that experiment.** It is the cheap decisive probe that runs
first, needs no code, and tells arm (b) what it is testing.

**The question, put so that either answer is informative:** the imposed 0.85 is
wrong everywhere in the boundary layer. **Is it wrong because 0.85 is the wrong
NUMBER, or because no number can be right?**

---

## 2. Design — 4 cases, one dictionary scalar changed

`kEpsilon` on the square cavity, both meshes, against the **recorded** `Prt =
0.85` twins in `gate_k0cs.json`. **The only difference from the baseline is the
value of `Prt` in `constant/transportProperties`.** Nothing else is touched: same
mesh, same model, same wall treatment, same `endTime`, same schemes, same
relaxation.

| Case | Baseline twin | `Prt` | Where that value comes from |
| --- | --- | ---: | --- |
| `P021_sq_c` | `K0cS_runs/S_KE_c` | **0.21** | Ampofo Fig. 11 at the wall (D417) |
| `P021_sq_f` | `K0cS_runs/S_KE_f` | **0.21** | as above |
| `P102_sq_c` | `K0cS_runs/S_KE_c` | **1.02** | Ampofo Fig. 11 outer layer, X = 0.033 (D417) |
| `P102_sq_f` | `K0cS_runs/S_KE_f` | **1.02** | as above |

**Both values are MEASURED on this exact cavity and neither is tuned.** They
bracket the measured profile. `kEpsilon` is the twin because it is the model
whose baseline is recorded on both meshes with this wall treatment and because
K0cS graded it.

---

## 3. Registered predictions, in both directions, with the mechanism stated first

The baseline **over-predicts** the wall heat flux: `Nu_hot` **+17.15 %**
(coarse) and **+20.55 %** (fine) against a 10 % band.

`alpha_t = nu_t/Prt`, so **lowering `Prt` raises the turbulent thermal
diffusivity** and, on a model that already carries too much heat to the wall,
should carry more.

| Arm | `alpha_t` vs baseline | Registered prediction |
| --- | --- | --- |
| **`Prt = 0.21`** | **x4.05 larger** | `Nu_hot` over-prediction gets **substantially WORSE** |
| **`Prt = 1.02`** | **x0.83 smaller** | `Nu_hot` over-prediction gets **modestly BETTER**, and does **not** reach the 10 % band |

**The tall cavity already ran the second half of this and agrees.** `K0cX`'s
`P_hi_f_KE` moved `Prt` 0.85 -> 1.283 and Nusselt over-prediction fell from
**+29.92 % to +11.45 %** — better, and still failing. **That is a prediction
this rung inherits rather than invents**, and if the square cavity contradicts
it, the contradiction is the finding.

### 3.1 The outcome table, fixed before compute

| Outcome | Condition | Reading |
| --- | --- | --- |
| **FORM** | `Prt = 0.21` makes it **worse** AND `Prt = 1.02` does **not** reach band | **No single constant can be right.** The measured field runs 0.00 to 1.02 across the layer; the value that is correct at the wall is the one that damages the answer most. The defect is the **form** of the closure, and X4 arm (b) is the experiment |
| **VALUE** | either arm brings `Nu_hot` **inside the 10 % band** on both meshes | The defect is the **value**. A constant `Prt` can be right if it is the right constant, and the measured near-wall value is the one to use |
| **REFUTED** | `Prt = 0.21` makes it **better** | **The mechanism in §3 is wrong**, and D424's transmission argument is withdrawn along with it |
| **NOT A RESULT** | any case misses the registered convergence criterion | |

**The REFUTED row is the one to watch.** It falsifies D424's reading of the
transmission path, which was measured on already-solved fields and never tested
by changing anything. **This rung is the first thing that can break it.**

---

## 4. What this rung cannot do

- **It does not implement a variable `Prt`.** Two constants bracketing a
  measured profile are not the profile. Establishing that no constant works is
  not the same as showing that the measured profile works, and **only X4 arm (b)
  can do the second.**
- **It does not touch the stress closure.** `kEpsilon` throughout.
- **It grades nothing against the gate.** Every number is a difference from a
  recorded twin, and `K0cS` keeps its verdicts.
- **The wall-function admissibility objection is inherited**, as in every rung
  on this cavity since `K0cT` §1.2a.

### 4.1 The §2c control, at zero compute

The registered trivial baseline is `K0cS_runs/C1_laminar`, already solved. **A
`Prt` arm that lands inside a band the laminar control also passes carries no
evidence**, and every pass is checked against it.

---

## 5. Cost

Baselines: `S_KE_c` 669.94 s, `S_KE_f` 3055.73 s. Two arms over both meshes:
**2 x (669.94 + 3055.73) = 7451.3 s**. `Prt` changes no equation count, so no
overhead factor is carried and **this estimate is expected to be accurate rather
than conservative** — which is itself a small check on the cost model.

**7451 s = 124.2 core-minutes = 2.070 core-hours = $0.106**, against a standing
$25 authorisation. Wall clock about 51 minutes, set by the two fine meshes run
concurrently.

---

## 6. Falsifier

**Exhibit a constant `Prt` that brings the square cavity's `Nu_hot` inside its
10 % band on both meshes.** That withdraws the FORM reading and makes X4 arm (b)
unnecessary.
