# K0cR. Reynolds-stress transport on both cavities: pre-registration

Campaign F14, gate K0c. Written 2026-08-18, **before any graded case was
solved**. This is experiment **X3** of `K0c_THERMAL_CLOSURE_SYNTHESIS.md`
section 8, described there as *"the single most informative outcome on this
list"*.

**X3 was registered as not to be scheduled until X2 had reported.** X2 reported
SMALL (`K0cQ_RESULTS.md`, D418): a constitutive anisotropy correction does not
move the cavities' graded integrals. **A Reynolds-stress transport model is a
different instrument and is not ruled out by that null**, which is what makes
this rung the next one.

Run tree: `verification/runs/F14-cooling-ladder/K0cR_runs/`.

---

## 1. The question

The synthesis's central split is **stress closure or heat flux closure**.

`SSG` is the instrument that separates them, because it **replaces the tensorial
stress form entirely** — six transported Reynolds-stress equations instead of an
isotropic eddy viscosity — **while keeping exactly the same simple
gradient-diffusion heat flux** its twin uses, `alphat = nut/Prt` with the same
constant `Prt`. Anything that moves is attributable to the stress closure.
Anything that does not move, is not.

---

## 2. Why the twin is `kEpsilon` and not `kOmegaSST`

`SSG` in OpenFOAM v2606 is a **high-Reynolds-number model with wall
functions**; it carries no low-Re damping. `kEpsilon` on these cavities was run
with exactly that treatment — `nutkWallFunction`, `kqRWallFunction`,
`epsilonWallFunction` — and already carries the `epsilon` field `SSG`
transports. `kOmegaSST` and `LaunderSharmaKE` integrate to the wall.

**So `kEpsilon` is the only twin for which the wall treatment, the transported
scalar and the heat-flux closure are all held fixed and the stress form is the
single difference.** Pairing `SSG` against `kOmegaSST` would confound the stress
form with the wall treatment.

**The wall-function admissibility objection is inherited, not resolved.**
`K0cT_RESULTS.md` §1.2a holds wall functions inadmissible at this cavity's y+ of
about 0.2. `K0cX_PREREGISTRATION.md` §3.1 declined to use that argument to
exclude a model without evidence and ran `kEpsilon` anyway. **This rung inherits
that decision and the objection with it**, and neither is settled here.

---

## 3. What the baselines already do, which sharpens the prediction

Recorded values, from `gate_k0cs.json` and `gate_k0cx.json`:

| Quantity | Reference | Band | `kEpsilon` coarse | `kEpsilon` fine | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| **Square** `Nu_hot` | 63.45 | 10 % | 74.329 (+17.1 %) | 76.488 (+20.5 %) | **FAIL** |
| Square `Sp` | 0.481 | 0.12 abs | 0.4925 | 0.4888 | **PASS** |
| Square `Vpeak` | 0.2127 | 15 % | 0.19612 (-7.8 %) | 0.19655 (-7.6 %) | **PASS** |
| Square `uv_peak` | 0.00108 | 40 % | 0.0012087 (+11.9 %) | 0.0012459 (+15.4 %) | **PASS** |
| **Tall hi** `Nu_avg` | 7.57 | 5.41 % | 9.612 (+27.0 %) | 9.835 (+29.9 %) | **FAIL** |
| Tall hi `S` | 0.095 | 0.05 abs | 0.01975 | 0.01831 | **FAIL** |

**On the square cavity the linear model already passes velocity, stratification
AND the Reynolds shear stress, and fails only the wall heat flux.** That is the
cleanest possible setting for this question: **the stress-side quantities are
already inside band, so there is little for a better stress closure to fix
there, and an SSG null on Nusselt would point at the heat-flux closure
directly.**

On the tall cavity both stratification and Nusselt fail, so there is room for the
stress closure to act, and the two geometries ask the question differently. Both
are run for that reason.

---

## 4. Case set — 4 cases, each a twin of an already-solved baseline

| Case | Geometry | Mesh | Baseline twin | `endTime` |
| --- | --- | --- | --- | ---: |
| `R_sq_c` | square, Ampofo | 14 400 | `K0cS_runs/S_KE_c` | 30 000 |
| `R_sq_f` | square, Ampofo | 36 864 | `K0cS_runs/S_KE_f` | 40 000 |
| `R_tl_c` | tall, Betts hi Ra | 4 800 | `K0cX_runs/X_hi_c_KE` | 60 000 |
| `R_tl_f` | tall, Betts hi Ra | 12 288 | `K0cX_runs/X_hi_f_KE` | 50 000 |

**`endTime` is held at the baseline's value so the comparison is a twin
comparison.** The consequence is registered in §7: if `SSG` has not converged by
its twin's iteration count, that is a reported outcome and a grading refusal,
not a reason to extend one arm and not the other.

### 4.1 The four setup changes `SSG` requires, and why none is a tuning choice

Established by a 20-iteration scratch pilot charged in §8. Every one of these is
required for the model to run at all.

1. `RASModel SSG;`
2. **`0/R` and `0.orig/R`**, created because the `kEpsilon` cases carry no `R`.
   **Initialised ISOTROPIC**, `R = (2k/3) I` from the case's own `k` seed, with
   `kqRWallFunction` walls inherited from the `k` field's own boundary
   conditions. **This is trap 2 of `K0c_THERMAL_CLOSURE_SYNTHESIS.md` §8.2**,
   which records that *"a Reynolds-stress initial condition built from a linear
   eddy-viscosity field is not realizable"*. An isotropic tensor is positive
   definite by construction, which is exactly why it is used here instead of
   `-2 nut symm(grad(U))`.
3. **`fvSchemes`**: `div(phi,R)` given the same scheme as `div(phi,epsilon)`;
   `div(R)` and `div((nu*dev2(T(grad(U)))))` given the same `Gauss linear` as
   the existing `div((nuEff*dev2(T(grad(U)))))`. `SSG` needs the **molecular**
   stress divergence because it carries the turbulent part in `R`.
4. **`fvSolution`**: `R` added to the existing `"(U|T|k|omega|epsilon)"` solver
   selector and the `"(k|omega|epsilon)" 0.4` relaxation selector, **so `R` gets
   the same solver and the same relaxation factor the other turbulence fields
   already have.** No new number is introduced anywhere in this rung.

**Trap 1 of §8.2 — `residualControl` naming a field the model does not
transport — does not bite here and the reason is recorded rather than assumed:**
the square cases set every `residualControl` target to `1e-30` and the tall
cases carry no `residualControl` block at all, so no run exits early on a
turbulence residual and the regex `"(k|omega|epsilon)"` failing to match `R` has
no effect. Convergence is assessed after the fact, in §7.

---

## 5. The registered decision rule, fixed before compute

Deviations are against each geometry's own recorded reference and band, in
§3's table. **"Improves materially" means the absolute deviation falls by at
least 3 percentage points, in the same direction, on BOTH meshes of the pair.**
A single-mesh move is not enough, because the baselines' own mesh pairs
disagree.

| Outcome | Condition | Reading |
| --- | --- | --- |
| **STRESS** | The `Nu` deviation falls **inside the gate band** on both meshes of at least one geometry | The residual defect **was the stress closure**. The tensorial form was the thing that was wrong |
| **HEAT FLUX** | `Nu` stays **outside** its band and changes by **less than 3 points** on both meshes, while velocity and `uv_peak` stay inside band or improve | **The defect is the heat-flux closure.** A fully tensorial stress transport model, with the same gradient-diffusion heat flux, did not move the wall heat flux. **This is the outcome that would justify a thermal-closure research direction outright** |
| **PARTIAL** | `Nu` improves materially but not into band | The stress closure carries **part** of the defect. Registered as its own outcome so it cannot be reported as either of the two above |
| **WORSE** | `Nu` deviation grows materially | `SSG` is not the instrument that separates the split on this flow, and the reason would be unknown |
| **NOT A RESULT** | see §7 | |

### 5.1 The §2c control costs nothing and already exists

The registered trivial baseline is the **laminar** arm already solved and
recorded: `K0cS_runs/C1_laminar` for the square cavity and
`K0cX_runs/X_hi_{c,f}_LAM` for the tall. **Any row on which `SSG` passes will be
checked against the laminar control on the same row**, and a pass the control
also achieves carries no evidence, per `VERIFICATION_CHARTER.md` §2c.

**This matters here more than usual.** The square laminar control records
`Nu_hot = 55.264`, a **-12.90 %** deviation against a 10 % band. It **fails**
that row — but it fails it by 2.90 points, where `kEpsilon` fails it by 7.1 and
10.5. **So on the square cavity's wall heat flux, no turbulence model in this
lab has yet come closer to the experiment than no turbulence model at all.**
That comparison is registered here, before `SSG` runs, rather than discovered
afterwards, and it is the number `SSG` has to beat for a pass on that row to
mean anything.

---

## 6. Realizability is checked, not assumed

`SSG` transports six stress components with no constraint forcing the tensor to
stay physical. **Registered check, on every case at its final time:**

- every diagonal component `Rxx, Ryy, Rzz >= 0`
- `det(R) >= 0`

**Reported for every case whether it passes or fails.** A case whose `R` has
gone non-realizable is **NOT A RESULT** and its numbers are not compared to
anything, because a Reynolds stress that is not positive semi-definite is not a
Reynolds stress.

---

## 7. Convergence, and the refusal it can trigger

Each case is assessed on its own final residuals, by the same standard
`K0cX_RESULTS.md` §7 applied. **If `SSG` has not converged at its twin's
`endTime`, the case is REFUSED for grading and reported with the refusal
attached.**

**REFUSED is not the same as WORSE and will not be reported as it.** The
synthesis records `LRR` entering a characterised limit cycle on the hump and
`realizableKE` failing to converge by 30 000 on the hills, so non-convergence is
a live and expected outcome for this model family, and it is registered here as
its own result rather than as a failure against the experiment.

---

## 8. Cost, estimated before compute

Baselines: `S_KE_c` 669.94 s, `S_KE_f` 3055.73 s, `X_hi_c_KE` 345.66 s,
`X_hi_f_KE` 859.40 s. Total **4930.73 s**.

`SSG` solves **six** Reynolds-stress equations plus `epsilon` where `kEpsilon`
solves `k` and `epsilon`. A factor of **2.5** is carried, deliberately above the
naive equation count, and **it is an estimate this rung will measure**:

**4930.73 x 2.5 = 12 327 s = 205 core-minutes = 3.42 core-hours = $0.176.**

**This is far below the synthesis's $0.650 estimate for X3, and the reason is a
design difference that must not be mistaken for a saving.** That estimate
carried a factor of three on *iteration count*, because the aerodynamic RSM runs
needed 118 424 to 251 703 iterations. **This rung fixes `endTime` at the twin's
value instead**, so it buys comparability and pays for it with the convergence
risk registered in §7. If the fine meshes come back unconverged, the extension
is a separate rung with its own pre-registration.

### 8.1 Pilot charged here, which produced a rate and no case value

One scratch solve of **20 iterations** outside this tree, used to establish that
`SSG` constructs and runs in `buoyantBoussinesqSimpleFoam` and to discover the
four setup changes in §4.1 — each of which surfaced as a fatal dictionary error
in turn. `ExecutionTime = 0.27 s`. **No case value in this rung came from it.**

---

## 9. Falsifier

**For the HEAT FLUX outcome, which is the one this lab would most want:** exhibit
a `Nu` deviation that falls inside the gate band, or improves by 3 points or
more on both meshes of either geometry. Either would make the stress closure a
carrier of the defect and withdraw the reading.
