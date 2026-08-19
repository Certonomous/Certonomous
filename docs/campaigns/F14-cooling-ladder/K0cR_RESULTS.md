# K0cR. Reynolds-stress transport on both cavities: results

Campaign F14, gate K0c. Experiment **X3** of `K0c_THERMAL_CLOSURE_SYNTHESIS.md`
section 8, described there as *"the single most informative outcome on this
list"*. Solved 2026-08-18 23:50Z to 2026-08-19 00:56:16Z; analysed 00:57Z.

Pre-registration `K0cR_PREREGISTRATION.md`, committed `d5c43c53` at
**23:50:13Z**. Run tree `verification/runs/F14-cooling-ladder/K0cR_runs/`,
machine record `gate_k0cr.json`. 4 cases, 4 markers, all `rc=0`.

---

## 1. Verdict: WORSE, by the rule registered before compute

| | `kEpsilon` twin | `SSG` | band | change |
| --- | ---: | ---: | ---: | ---: |
| **Square `Nu_hot` coarse** | +17.15 % | **+31.30 %** | 10 % | **-14.15 pts** |
| **Square `Nu_hot` fine** | +20.55 % | **+31.52 %** | 10 % | **-10.97 pts** |
| **Tall `Nu_avg` coarse** | +26.98 % | **+59.90 %** | 5.41 % | **-32.92 pts** |
| **Tall `Nu_avg` fine** | +29.92 % | **+59.44 %** | 5.41 % | **-29.53 pts** |

§5's WORSE branch: *"the Nusselt deviation grows materially"* — it grew on
every mesh of both geometries, by 11 to 33 points. **`SSG` roughly doubled the
tall cavity's wall-heat-transfer error.**

**The registered reading of WORSE was *"SSG is not the instrument that separates
the split on this flow, and the reason would be unknown."* That reading is now
too weak for what the rung measured**, and section 3 says why. The verdict is
what the pre-registered rule returns; the reading is stated separately and is
not smuggled into it.

---

## 2. Realizability held on every cell of every case

Registered in §6 as a condition, because `SSG` transports six stress components
with nothing forcing the tensor to stay physical.

| Case | cells | min diagonal | min determinant | negative cells |
| --- | ---: | ---: | ---: | ---: |
| `R_sq_c` | 14 400 | +4.137e-06 | +9.343e-17 | **0 / 0** |
| `R_sq_f` | 36 864 | +2.859e-06 | +3.081e-17 | **0 / 0** |
| `R_tl_c` | 4 800 | +9.200e-05 | +1.042e-12 | **0 / 0** |
| `R_tl_f` | 12 288 | +5.687e-05 | +2.591e-13 | **0 / 0** |

**No case is NOT A RESULT on realizability grounds.** Trap 2 of
`K0c_THERMAL_CLOSURE_SYNTHESIS.md` §8.2 — *"a Reynolds-stress initial condition
built from a linear eddy-viscosity field is not realizable"* — was answered by
**construction** rather than by care: `R` was initialised isotropic, `2k/3 I`,
which is positive definite by definition, and it stayed positive definite for
30 000 to 60 000 iterations.

**Convergence also held**, against the §7 refusal this rung registered as a
live risk. Final initial residuals reached 1e-12 on the tall pair and 1e-8 on
the square coarse case, and **`bounding` fired zero times in all four**. The
`LRR` limit cycle and `realizableKE` non-convergence the synthesis warned of did
not appear.

---

## 3. What the rung actually established: the stress closure fixed the velocity field and broke the heat transfer

**This is the finding, and it is sharper than the verdict.**

| Row | `kEpsilon` | `SSG` | band | change | evidence? |
| --- | ---: | ---: | ---: | ---: | --- |
| **Tall `Vup` coarse** | -29.67 % **FAIL** | **-10.64 % PASS** | 15 % | **+19.04 pts** | **carries evidence** |
| **Tall `Vup` fine** | -30.06 % **FAIL** | **-10.53 % PASS** | 15 % | **+19.53 pts** | **carries evidence** |
| Square `Vpeak` coarse | -7.80 % PASS | +4.88 % PASS | 15 % | +2.91 pts | carries evidence |
| Square `Vpeak` fine | -7.60 % PASS | +5.09 % PASS | 15 % | +2.51 pts | carries evidence |

**On the tall cavity the peak velocity moved from a 30 percent failure to a
10 percent pass, and the laminar control fails that row, so the pass carries
evidence in the §2c sense.** In the same solve, on the same mesh, at the same
iteration, **the wall heat flux got worse by 30 points.**

**The two fields moved in opposite directions under a change that touched only
the stress closure.** `SSG` replaces the tensorial stress form and leaves the
heat flux exactly as it was — `alphat = nut/Prt`, the same constant `Prt`. So
the momentum field responded to a better stress closure by improving markedly,
and the thermal field, fed through an unchanged gradient-diffusion closure,
responded by degrading.

**The synthesis registered *"velocity improving while the Nusselt error stays"*
as the outcome that would *"justify a thermal-closure research direction
outright"*. What occurred is that outcome with the second half amplified:
velocity improved and the Nusselt error did not merely stay — it doubled.**

**The registered rule does not have a branch for that**, which is why the
verdict is WORSE. The rule was written expecting the thermal error to be
inert under a stress-side change, and it was not inert; it was actively made
worse. **Registering four outcomes and meeting a fifth is a defect in the
pre-registration, not in the result**, and it is recorded as such rather than
resolved by choosing whichever registered branch reads best.

### 3.1 What this does NOT license

- **It is not a measurement of the heat-flux closure.** No heat-flux closure was
  varied here. The inference is from a stress-side change producing a
  thermal-side degradation, which is indirect.
- **A single alternative stress closure is not the stress closure.** `SSG` is
  one Reynolds-stress model. `LRR` and `EBRSM` were not run, and
  `F6a_DIFFUSION_RESULTS.md` records `LRR` behaving very differently from `SSG`
  on aerodynamic cases.
- **The wall treatment is confounded and was inherited knowingly.**
  `K0cR_PREREGISTRATION.md` §2 records that `kEpsilon` is the only twin holding
  wall treatment, transported scalar and heat-flux closure fixed — but both
  models use wall functions at a y+ near 0.2, which `K0cT_RESULTS.md` §1.2a
  holds inadmissible. **That objection is inherited by both arms equally and is
  not resolved here.**

---

## 4. The mechanism is NOT a bulk eddy-viscosity effect, and this rung does not identify it

The obvious explanation — `SSG` produces more turbulence, so `alphat = nut/Prt`
rises and the wall heat flux with it — **is contradicted by the measurement.**

| Case | `nu_t/nu` domain max | change | `k` max | change | `Nu` change |
| --- | --- | ---: | --- | ---: | ---: |
| `R_sq_c` | 25.235 -> 20.636 | **-18.22 %** | -10.71 % | | **+14.15 pts worse** |
| `R_sq_f` | 26.377 -> 20.845 | **-20.97 %** | +6.05 % | | **+10.97 pts worse** |
| `R_tl_c` | 39.721 -> 41.807 | +5.25 % | +40.24 % | | +32.92 pts worse |
| `R_tl_f` | 40.077 -> 41.771 | +4.23 % | +39.24 % | | +29.53 pts worse |

**On the square cavity the peak eddy viscosity fell by about 20 percent while
the wall heat flux rose by 14 points.** Those move in opposite directions, so
the wall heat flux is not tracking the bulk eddy-viscosity level.

**The mechanism is therefore in the near-wall distribution of `alphat`, not in
its domain maximum, and this rung did not instrument that.** `nu_t/nu` domain
maximum is a **single-cell** quantity and the noisiest measure in this record.
**No mechanism is claimed.** The next rung that wants one should measure
`alphat` and the turbulent heat flux **at the wall**, on both models, which is
a diagnostic neither comparator currently carries.

---

## 5. §2c: only two hollow passes, and they are the row family this ladder has now flagged on four geometries

Every `SSG` pass was checked against the laminar control on the same row.

- **Four passes carry evidence**: both tall `Vup` rows and both square `Vpeak`
  rows. The laminar control fails all four.
- **Two passes are hollow**: `Vpeak_X` on both square meshes — the
  velocity-peak **location** row. `SSG` passes it, `kEpsilon` passes it, and the
  **laminar control passes it too**, so it separates nothing.

**This is the fourth geometry on which the velocity-peak location row has been
found hollow.** D413 recorded it as `K0cS` G9 and as `K0cT` R11 and R13;
`K0cX_RESULTS.md` §5 found `R3` and `R5` the same way and D420 moved them out of
that rung's tally. **The quantity has now failed to discriminate on the square
cavity, the tall cavity, the K0cT geometry and here, across three Rayleigh
decades and two closure families.**

**It is a row-design defect, not a run-by-run accident**, and the cause is
visible in the numbers: a peak *location* is reported at a cell centre, so it
takes a handful of discrete values on any mesh, and the band spans several of
them. **Recommended, and named rather than performed:** the location rows
should be retired from graded tallies campaign-wide, or re-banded to a fraction
of the local cell spacing so that they can fail.

---

## 6. Departure disclosed: one display label was corrected after the results were read

**On the grading path: nothing.** The change is one printed annotation.

The comparator flagged a row `hollow pass, 2c` whenever
`pass_carries_evidence` was false. That field is false both for a hollow pass
**and for a row `SSG` simply failed**, so **20 of the 26 rows were annotated as
hollow passes when they were plain failures.** The label was corrected to fire
only when `SSG` is in band **and** the control is in band.

**Verified: the verdict, `per_geometry`, every row and every realizability
figure compare EQUAL across the re-run** — the corrected file changed the
printed table and nothing else. Under `VERIFICATION_CHARTER.md` §2d this is
instrumentation off the grading path, permitted with a dated disclosure, and
this is the disclosure.

**The comparator was otherwise frozen and verified**: committed 23:52:32Z with
**zero completion markers on disk**, and its sha256 at analysis time
(`e5c6695c936f0097`) matched the committed blob exactly.

---

## 7. A precondition that had to be checked, because K0cS's comparator changed mid-rung

`K0cS`'s `wall_nu` was changed from an arithmetic to an area-weighted mean of
local Nusselt **after its first case finished** (D422, `VERIFICATION_CHARTER.md`
§2d.1). **This rung compares `SSG` arms against recorded `kEpsilon` baselines,
so it is only valid if those baselines were produced by the post-repair
comparator.**

Verified three ways: `gate_k0cs.json` was written by exactly one commit,
`336a364d`, which is **the same commit that introduced the area weighting**; the
recorded `S_KE_c` `Nu_hot` of **74.329** matches `K0cS_RESULTS.md`'s post-repair
figure of 74.3; and the recorded heat balance on both converged `kEpsilon` cases
is **0.0000 %**, which is the closure the record states the repair produced.
**The baselines are post-repair and the comparison is sound.**

---

## 8. Cost

| Case | exec s | `kEpsilon` baseline s | ratio |
| --- | ---: | ---: | ---: |
| `R_sq_c` | 950.14 | 669.94 | 1.418 |
| `R_sq_f` | 3913.49 | 3055.73 | 1.281 |
| `R_tl_c` | 512.45 | 345.66 | 1.483 |
| `R_tl_f` | 1065.48 | 859.40 | 1.240 |
| **Total** | **6441.6 s** | | mean **1.355** |

**107.4 core-minutes = 1.789 core-hours = $0.092**, against a pre-registered
estimate of $0.176 and the synthesis's $0.650 for X3. Wall clock 66 minutes.

**The x2.5 overhead factor was an over-estimate; measured 1.24 to 1.48.** The
caveat X2's record carried applies with less force here: all four ratios exceed
1 and they were all measured under the same four-way concurrency, so the
direction is trustworthy even though the concurrency differs from the
baselines'. **A factor near 1.35 for six Reynolds-stress equations against two
scalars is the number a future rung should carry.**

---

## 9. What X3 leaves for the list

- **The synthesis's central split is not resolved, and the evidence now leans.**
  A tensorial stress closure improved the momentum field and degraded the
  thermal field. That is a reason to instrument the **heat-flux closure**
  directly, which is **X4 arm (b)** — a generalised gradient-diffusion `alphat`
  through `fvOptions` — and **X5**.
- **The near-wall `alphat` diagnostic is owed** before any of those runs, per
  section 4.
- **`LaunderSharmaKE` still has no aerodynamic case in this lab** (X8), and
  `SSG` now has no *isothermal* cavity comparison either.
- **Nothing here was submitted, sent, filed, uploaded or registered.**
  Submissions are PARKED.
