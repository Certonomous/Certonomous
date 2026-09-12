# SUBOFF A1f — MATCHED-REYNOLDS HORIZONTAL-PLANE DRIFT SWEEP, HULL AND SAIL

## 0. WHAT THIS CASE IS NOT — READ THIS BEFORE ANYTHING ELSE

**THIS IS NOT A MEMBER OF THE A1b GRID FAMILY AND IT MAY NOT CONTRIBUTE TO ITS `CT`
TRIPLE.** A1b's registered condition is `Re_L = 1.2e7` on the **overall length**. Matching
Reynolds number to Roddy's experiment moves the condition to **Re_LOA = 1.45663e7**, a
different flow. **A1f is a single-level solve, at a single level, for the A1e comparison
only.** It produces no observed order, no GCI, no extrapolation, and it is not a rung of
any ladder. A1b's `Re_L = 1.2e7` is correct for its own gate and is untouched by this
file.

Stated first, rather than as a closing caveat, because a later reader folding a
single-level solve into a grid family it was never part of is the same failure mode as the
configuration-number collisions recorded in A1e §2 — one level up, and harder to see.

Author: cfd lab-lane, 2026-09-12, on the cfd-supervisor's approval of a matched-Re sibling.

---

## 1. WHY THIS CASE EXISTS

`SUBOFF_A1e_HORIZONTAL_PLANE_ARM_PREREGISTRATION.md` is **REPORTED, NOT GRADED** on
Reynolds grounds (its Addendum 3 §E, supervisor's ruling). Our solve runs at
**Re_LBP = 1.1738e7** against Roddy's **1.4248e7**, **17.6 % low**, and Roddy states on
his page 3 that his coefficients "vary with Reynolds number up to a Reynolds number based
on the length of the hull of about 10 to 15 million" — **both conditions lie inside that
band and ours lies lower in it.** The ±4 % band is his *measurement* uncertainty and
carries no allowance for Reynolds sensitivity, so grading across that gap would bury a
systematic offset of unknown size beneath a gate.

A1e Addendum 4 established that **the gap cannot be bounded from Roddy's data**, and the
reason is structural rather than accidental: **every static derivative, for all six
configurations, was measured at a single speed — 6.5 knots** (Table 3, report pages 17–18,
read as page images). The four-speed Yawing and Pitching rows are **not** a Reynolds
sweep — `Omega` is fixed at 2.220 rad/s, so varying `U` varies the nondimensional yaw rate
`r' = omega·L/U` and Reynolds is confounded with `r'` by construction.

**So the only route to a graded arm is to match the condition.** That is this case.

---

## 2. THE CONDITION — MATCHED TO RODDY, QUOTED FROM HIS PAGE 3

> "The static stability experiments were conducted at a **model speed of 6.5 knots** which
> corresponds to a Reynolds number (based on the length between perpendiculars) of **about
> 14 million**."

| quantity | value | basis |
|---|---|---|
| `U` | **3.343886 m/s** | 6.5 knots exactly, at 0.514444 m/s per knot |
| `nu` | 1e-6 m²/s | unchanged from the A1 family |
| **Re_LBP** | **1.42478e7** | on L_BP = 4.2608602 m — matches Roddy's "about 14 million" |
| Re_LOA | 1.45663e7 | on L_OA = 4.3561001016 m, reported for orientation only |
| `k_inf` | **1.118157e-05** | scales as `U²` from the family's 7.588690e-06 |
| `omega_inf` | **4.658989** | `= k_inf / nut_inf`; the same construction reproduces the family's 3.161954 at the old `U`, which is the check that it is the same rule and not a new one |
| `nut_inf` | 2.4e-06 | unchanged, `nut/nu = 2.4` |

---

## 3. MESH — THE ADMITTED LEVEL, AND ONLY IT

**L2, 9,121,237 cells.** A1b §2 records `L0c` and `L1` as **NOT ADMITTED** (`GATE FAIL` on
M-b-1 and M-d respectively); L2 is the admitted level and is the only one this case uses.
No new mesh is built. The geometry is the hull-and-fairwater body already verified against
Liu & Huang page 2 to the millimetre (A1e §2).

**Mesh quality, disclosed not gated (two-tier standard):** L2's own
`log.checkMesh.FULLFLAG` reports **131,728 concave cells = 1.444 %** of the mesh — a
*lower* fraction than L1's 1.989 %. The force-share question governed by
`SUBOFF_A1b_CONCAVE_FORCE_SHARE_PREREGISTRATION.md` (frozen
`bc73dc0cae2063477d9d54ee5512b93a68be3249`) **applies to this case exactly as to any
other**, and `F = max(Q2, Q3)` is unmeasured on L2 at the time of writing. Nothing here
pre-empts it.

---

## 4. THE SWEEP

- **Drift angles β = −12, −8, −4, 0, +4, +8, +12 degrees**, inside Roddy's tested ±18°.
- **7 points × 4 ranks = 28 ranks in one wave**, which is exactly Sanaa's SUBOFF
  allocation of 28.
- `endTime` 3000, `deltaT` 1, `writeInterval` 15, `purgeWrite` 2 — the A1b family's own
  checkpoint policy, ~5.9 min per checkpoint at the measured rate, inside the directive's
  30-minute ceiling.
- **Derivatives `Y_v'` and `N_v'` by linear fit over |β| ≤ 8**, the linear range.
- Hull/sail split reported per point. y+ per patch reported per point.

---

## 5. NORMALISATION — QUOTED FROM RODDY'S PAGE 3, NOT INHERITED

The defect A1e Addendum 3 exists to repair is **not repeated here**. The post-processing
constants are stated as numbers, not as the phrase "Roddy's own convention":

| constant | value | Roddy's words |
|---|---|---|
| reference length | **4.2608602 m** | "the length between perpendiculars of 13.9792 feet (4.261 m)" |
| reference area | **18.154929 m²** | `= L_BP²`; his derivatives are `Y/(½ρU²L²)` |
| moment origin | **(2.013, 0, 0)** | "origin 6.6042 feet (2.013 m) aft of the forward perpendicular (nose) on the hull centerline" |

`Aref` is **L_BP², not the wetted area.** A1b's `CT` gate keeps its own wetted-area
normalisation; the two are a **factor of 5.902 apart** and are not interchangeable.

---

## 6. THE BANDS

Reference: **Roddy 1990, DTRC/SHD-1298-08, Table 4, report page 19, "Horizontal Plane",
column printed `Config 4 / B.H. + Sail`** — the hull-with-fairwater body, **named by its
geometry and never by a bare number** (A1e §2's binding rule; `Config 4` in Roddy is not
`Config 4` elsewhere).

| quantity | Roddy | gate |
|---|---|---|
| **`Y_v'`** | −0.023008 | **GATED, ±4 %: [−0.023928, −0.022088]** |
| **`N_v'`** | −0.015534 | **REPORTED, NOT GRADED** — inherited from A1e Addendum 1 |

**`N_v'` stays ungated here for a reason that has nothing to do with Reynolds and is not
repaired by matching it.** A1e Addendum 1 measured that `|Config 4| N_v'` is *larger* than
the fully appended value the ±4 % was stated for, so the transferred band is **13.8 %
looser than the rig floor** — it errs in our favour. Matching the condition does not fix a
band that is too wide. Recorded so nobody reads A1f as lifting that restriction.

±4 % is the **tighter** end of Roddy's stated "4 to 5 percent" (page 105). ±5 % is the
outer reading and does not gate.

---

## 7. TURBULENCE TREATMENT — MATCHED, AND CHECKED RATHER THAN ASSUMED

Fully-turbulent k-ω SST with `nutUSpaldingWallFunction`, no transition model. **This is
the matched choice, not a disclosed mismatch**: Liu & Huang 1998, page 23, footnote to
Table 14, read as a page image — "Hull, bridge fairwater and four identical stern
appendages all have tripwires installed at 5 percent of chord length." **Both of our
patches carried tripwires; the measured body was fully turbulent by design.**

---

## 8. COST

**33,180 core-min estimated** = 7 points × 3000 iterations × 23.7 s/iteration × 4 ranks
/ 60. **$28.37 DERIVED, NOT MEASURED**, at the owner-stated $0.0513/core-h; the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER` §5).

Rate basis: **measured on SOLVE_L2's own resumed segment on this 96-core host** —
5461.9 s of `ExecutionTime` over 230 iterations at 4 ranks — not inherited from the
16-core readings.

**No cap is registered.** Sanaa's directive #17 (2026-09-12): no run is stopped by a time
or budget cap. This figure is a **calibration prediction to be scored** under rule 12 at
completion, never a kill. Convergence may arrive well before 3000 iterations, in which
case the actual is lower and the ratio is what the calibration row records.

## 9. WHAT THIS CASE DOES NOT CLAIM

No vertical-plane result: no `Z`, no `M`, no neutral point, no hull/fin split — there are
no fins on this body. Nothing about the fully appended configuration, **whose own name
means two different bodies in the two source reports** (A1e Addendum 4 §D: Roddy's
"fully appended" includes Ring Wing No. 1; Liu & Huang's Config 8 does not). No grid
convergence, no observed order, no GCI — **single level, by construction, as §0 states.**

## 10. FREEZE

Frozen at the commit adding this file, before any compute at this condition. No band,
threshold, condition or normalisation above may be altered afterwards; departures land as
dated addenda that strike the original legibly and cannot move a gate.
