# DRIVAER COARSE ARMS — y⁺ PER PATCH, LAYERED AND UNLAYERED GROUPS SEPARATELY

**The deliverable owed with the two completed coarse grades. Filed 2026-09-12 by a cfd `lab-lane`.**

🔴 **ONE TABLE SERVES BOTH ARMS, AND THAT IS A FACT ABOUT THE FILESYSTEM, NOT A SHORTCUT.**
`r2_coarse_R2` and `r2c_coarse_blended_R2` **symlink the identical `constant/polyMesh`**
(both resolve to `r2_coarse/constant/polyMesh`). y⁺ here is **mesh-derived**, so it is
identical for the two arms **by construction** — presenting two copies would imply an
independent measurement that does not exist.

🔴 **BASIS, QUOTED FROM THE ARTIFACT RATHER THAN PARAPHRASED:** *"u_tau from U_inf=38.889,
Re_L=7.19e6, L=2.79 m **ALONE (INPUT)**; wall distance from the **BUILT MESH (OBSERVATION)**"*.
**This is a MESH-DERIVED ESTIMATE, not a solved y⁺.** Neither DrivAer arm wrote a `yPlus`
field (`postProcessing/` holds `forceCoeffs1` only), so no solved y⁺ exists for them.
For contrast, CRM wing-alone **did** write one and its numbers are solved.

## GROUP AGGREGATES — the figures the pre-registered Y1 cap is written against

| group | patches | faces | area m² | y⁺ area-wtd median | y⁺ min | y⁺ max |
|---|---:|---:|---:|---:|---:|---:|
| **layered** | 27 | 14,057 | 24.959 | **481.565** | 34.235 | 3805.767 |
| **unlayered** | 20 | 3,803 | 5.931 | **1940.998** | 56.062 | 5128.807 |

**3,803 of 17,860 boundary faces — 16.3 % — carry no usable layer.**
The unlayered group's y⁺ median is **4.03× the layered group's**. **A `Cd` integrated over
this body is integrated over both groups at once: that is the Y1 mixed-wall-treatment
failure, and it is why the `Cd` is `NOT A RESULT` independently of convergence.**

## LAYERED GROUP — per patch (27 patches, 14,057 faces, 24.959 m²)

| patch | faces | area m² | y⁺ median | y⁺ min | y⁺ max | mesh layers | coverage % |
|---|---:|---:|---:|---:|---:|---:|---:|
| `OCDADetailedUnderbody` | 5,221 | 9.2513 | 481.56 | 43.55 | 3752.06 | 1.190 | 16.2 |
| `BodySide` | 1,698 | 2.6379 | 458.20 | 56.68 | 2253.57 | 3.480 | 75.8 |
| `BodyRear` | 644 | 1.3834 | 826.37 | 121.86 | 3805.77 | 1.370 | 35.8 |
| `BodyHood` | 515 | 1.2598 | 464.44 | 297.26 | 2087.79 | 4.140 | 91.5 |
| `NotchbackRoof` | 491 | 1.2315 | 464.38 | 460.95 | 2492.05 | 4.450 | 95.2 |
| `BodyWindowfront` | 366 | 1.0984 | 674.25 | 235.36 | 2877.09 | 2.840 | 67.1 |
| `BodyFender` | 468 | 1.0013 | 695.55 | 101.26 | 2567.61 | 2.420 | 64.1 |
| `BodyFasciafront1` | 1,076 | 0.9906 | 495.36 | 77.22 | 3303.68 | 1.650 | 41.5 |
| `NotchbackWindowside` | 301 | 0.7768 | 517.82 | 355.79 | 2325.93 | 3.660 | 84.1 |
| `NotchbackWindowrear` | 278 | 0.7242 | 464.51 | 456.41 | 1917.40 | 4.340 | 95.4 |
| `NotchbackTrunk` | 294 | 0.7216 | 699.36 | 302.28 | 2953.97 | 2.940 | 73.2 |
| `NotchbackC_Pillar` | 273 | 0.6435 | 793.06 | 295.65 | 3178.01 | 2.260 | 57.9 |
| `EngineUndershield` | 196 | 0.4806 | 356.05 | 151.87 | 3512.30 | 2.550 | 31.7 |
| `BodyRocker` | 733 | 0.4699 | 235.43 | 34.23 | 1388.45 | 3.370 | 66.6 |
| `BodyWindowSide` | 223 | 0.3822 | 519.65 | 89.38 | 1920.38 | 2.490 | 49.5 |
| `BodyRoof` | 150 | 0.3723 | 464.80 | 226.06 | 3079.30 | 3.810 | 84.6 |
| `NotchbackBodyside` | 246 | 0.3647 | 462.40 | 231.04 | 1848.45 | 3.180 | 81.3 |
| `NotchbackWindowsideframe` | 156 | 0.3076 | 748.37 | 276.35 | 2799.89 | 2.810 | 65.3 |
| `BodyRearAccess` | 108 | 0.2575 | 804.04 | 410.74 | 2006.65 | 2.460 | 70.5 |
| `BodyHeadlamps` | 210 | 0.1460 | 401.53 | 230.61 | 1094.69 | 2.030 | 53.2 |
| `NotchbackB_Pillar` | 54 | 0.1318 | 464.15 | 336.83 | 1818.80 | 4.310 | 92.2 |
| `ClosedGrillUpperInsert` | 152 | 0.1098 | 404.40 | 160.41 | 1386.43 | 1.710 | 43.4 |
| `BodyWindowsideframe` | 77 | 0.0775 | 459.83 | 108.24 | 1396.54 | 1.510 | 26.3 |
| `ClosedGrillLowerInsert` | 90 | 0.0600 | 274.62 | 58.97 | 917.74 | 2.970 | 67.7 |
| `CTRL_SURFACE_Wheelshouse_RHS` | 15 | 0.0369 | 418.95 | 316.10 | 1032.64 | 2.470 | 38.8 |
| `CTRL_SURFACE_Wheelhouse_LHS` | 15 | 0.0369 | 452.93 | 413.61 | 1057.26 | 2.330 | 37.7 |
| `NotchbackWindowrearframe` | 7 | 0.0053 | 590.95 | 53.27 | 760.86 | 3.000 | 67.2 |

## UNLAYERED GROUP — per patch (20 patches, 3,803 faces, 5.931 m²)

| patch | faces | area m² | y⁺ median | y⁺ min | y⁺ max | mesh layers | coverage % |
|---|---:|---:|---:|---:|---:|---:|---:|
| `Tiresfront` | 533 | 1.2687 | 1984.28 | 148.43 | 4282.82 | 0.107 | 1.0 |
| `Tiresrear` | 596 | 1.2616 | 2008.34 | 58.72 | 3731.41 | 0.027 | 0.1 |
| `Rimsrear` | 200 | 0.5552 | 1874.10 | 247.98 | 3180.48 | 0.000 | 0.0 |
| `Rimsfront` | 179 | 0.5156 | 1857.25 | 361.88 | 2767.22 | 0.000 | 0.0 |
| `ExhaustSystem2` | 809 | 0.4678 | 688.29 | 56.06 | 2179.08 | 0.604 | 10.4 |
| `Powertrain` | 361 | 0.4115 | 1141.79 | 94.98 | 3354.63 | 0.283 | 5.7 |
| `BodyA_Pillar` | 163 | 0.1970 | 911.60 | 131.54 | 3168.55 | 0.399 | 8.0 |
| `BrakeDiscrear` | 45 | 0.1763 | 2542.77 | 1686.86 | 3181.76 | 0.000 | 0.0 |
| `Mirrors1` | 273 | 0.1564 | 482.45 | 71.25 | 1972.46 | 0.714 | 15.8 |
| `WheelSupportrear` | 71 | 0.1555 | 2311.04 | 874.07 | 5128.81 | 0.000 | 0.0 |
| `WheelSupportfront1` | 83 | 0.1415 | 1941.00 | 246.96 | 4717.17 | 0.024 | 0.2 |
| `BodyFasciafront2` | 51 | 0.1361 | 797.02 | 246.25 | 2332.27 | 0.255 | 3.8 |
| `BodyWindowfrontframe` | 53 | 0.1087 | 1081.96 | 168.91 | 3152.06 | 0.434 | 13.0 |
| `BodyDoorhandles` | 125 | 0.0755 | 817.95 | 90.47 | 1758.93 | 0.160 | 2.5 |
| `WheelSupportfront2` | 38 | 0.0714 | 1719.56 | 383.54 | 3643.47 | 0.000 | 0.0 |
| `CTRL_SURFACE_Outlet` | 50 | 0.0695 | 1502.36 | 266.14 | 1852.45 | 0.000 | 0.0 |
| `ExhaustSystem3` | 88 | 0.0622 | 746.68 | 119.78 | 1649.78 | 0.341 | 5.8 |
| `BrakeDiscfront` | 14 | 0.0584 | 1726.82 | 708.90 | 2018.88 | 0.000 | 0.0 |
| `Mirrors2` | 65 | 0.0381 | 856.51 | 295.31 | 1791.00 | 0.000 | 0.0 |
| `ExhaustSystem1` | 6 | 0.0038 | 526.20 | 194.05 | 736.89 | 0.000 | 0.0 |

**Worst coverage:** `Rimsfront`, `Rimsrear`, `BrakeDiscfront`, `BrakeDiscrear`,
`WheelSupportrear`, `WheelSupportfront2`, `Mirrors2`, `ExhaustSystem1`, `CTRL_SURFACE_Outlet`
— **0.000 mesh layers, 0.0 % coverage**. `Tiresrear` 0.027 (0.1 %), `Tiresfront` 0.107 (1.0 %).
**Best:** `NotchbackWindowrear` 4.34 (95.4 %), `NotchbackRoof` 4.45 (95.2 %), `BodyHood` 4.14 (91.5 %).

**The wheels, tyres, rims, brake discs and wheel supports — the entire rotating-assembly
group — are unlayered.** They are also where a notchback's wake is fed.

---

## FORCES AGAINST THE REGISTERED BAND — **WITH THE CAP STATED FIRST**

🔴 **BOTH `Cd` VALUES ARE `NOT A RESULT`.** Two independent pre-registered bars:
the **Y1 mixed-wall-treatment failure** above, and **`NOT_PLATEAUED`** (a coherent limit
cycle, period 33 / 30 iterations, excursion 3.30× / 4.06× tolerance, not decaying).
**The numbers below are printed so the gap can be seen, NOT as a drag coefficient.**

Gate **B3** (REPORTED, never primary): `|Cd − 0.2758368| ≤ 0.10 × 0.2758368`
→ band **[0.2482531, 0.3034205]**. Reference **DrivAerML** (Ashton et al. 2024) — a
**CODE** reference, rank 2, **NOT experiment**; any pass carries the disavowal.

| arm | Cd | Cl | vs reference | band | drag counts |
|---|---:|---:|---:|---|---:|
| control (non-blended) | 0.35525032 | 0.00507984 | **+28.79 %** | **OUTSIDE** | 3552.5 vs 2758.4 = **+794.1** |
| blended | 0.35516290 | 0.01397983 | **+28.76 %** | **OUTSIDE** | 3551.6 vs 2758.4 = **+793.3** |

**B3 is OUTSIDE the band on both arms — and that is REPORTED, not a verdict**, because a
`NOT A RESULT` cannot also be a `GATE FAIL` against a reference (rule 5: the gate can only
turn a result INTO `NOT A RESULT`, never the reverse). **+794 drag counts against a code
reference on a body with 16.3 % of its faces unlayered is exactly what the Y1 cap predicts.**

`Cl` moved +175.2 % between arms and **is not a signal**: it is 0.528× the control's own
trailing-200 `Cl` range, i.e. inside its own noise.

## GATES

| gate | result |
|---|---|
| rule 4 completion, **both arms** | **PASS 6/6** — `rc=0`, `End`, last==`endTime` 2000, fields, `ExecutionTime` count **2000**, age guard |
| **B2** — is blending active? | **`INACTIVE`**. Relative `|ΔCd|` 2.460684e-04 vs threshold 3.295176e-02 — **134× below**, and still `INACTIVE` at three tighter thresholds it never had to clear. **Mechanism measured:** layered-group y⁺ min **34.235**, unlayered min **56.062** — the whole body is above the y⁺ ≈ 30 crossover where the two wall functions coincide, so there was no buffer-layer region for blending to act on. **A predicted null with its cause measured.** |
| **B1** — y⁺ insensitivity | **`PENDING`** — medium arm running. **And it is known IN ADVANCE to carry no evidence of y⁺ insensitivity**, on the registration's own words, because B2 showed no change. |
| **B3** — reference agreement | **OUTSIDE** the band, both arms, **REPORTED not gated** |

## FAMILY SCOPE — **TWO LEVELS, NO FINE MESH, NO ROACHE CLAIM**

Sanaa's ruling, 2026-09-12: *"for Drivaer, we can keep the level up to medium (no fine
mesh), if the results are good."* **DrivAer is a TWO-LEVEL family: coarse + medium.**
**A Roache triple needs three admissible levels. This family has two, so NO observed order
and NO GCI exists or will be computed**, and nothing about a fine level is owed, costed or
queued. **Disclosed here rather than left to be inferred from an absent row.**

*Filed by a cfd `lab-lane`, 2026-09-12. Alters no gate, threshold, cap or label.
Submissions parked. No agent's message is Sanaa's consent.*
