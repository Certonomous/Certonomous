# DRIVAER_LAYERFIX_B1 — **H1 REFUTED**

Registration frozen `a0b87680b9d04ba3a9e0a4501c20a4913fc4e618`, committed **before**
compute. One change from A1, verified by diff: `maxThicknessToMedialRatio 0.3 → 0.6`.

## Gate, in the registered order. Every row evaluated; outcome falls in exactly one.

| row | condition | result |
|---|---|---|
| 1 | rc≠0 / cap / splice / unreadable | NO — rc 0, 3.52 of 15 core-min, index test PASS |
| 2 | C < 3.00 (control regressed) | NO — **C = 4.14** |
| 3 | G < 50.057 % (global regressed) | NO — **G = 50.475 %** |
| 4 | R ≥ 7 | NO |
| 5 | 1 ≤ R ≤ 6 | NO |
| 6 | **R = 0** | **YES → H1 REFUTED** |

## R = 0 of 14. Not one local-group patch reached 1.00 layers.

| patch | A1 | B1 | reached ≥1.00? |
|---|---|---|---|
| CTRL_SURFACE_Outlet | 0.00 | **0.66** | no |
| Mirrors2 | 0.00 | **0.55** | no |
| Tiresfront | 0.11 | 0.12 | no |
| Tiresrear | 0.03 | 0.06 | no |
| Rimsfront | 0.00 | 0.04 | no |
| WheelSupportfront1 | 0.02 | 0.02 | no |
| BrakeDiscfront, BrakeDiscrear, ExhaustSystem1, Rimsrear, TirePlinthfront, TirePlinthrear, WheelSupportfront2, WheelSupportrear | 0.00 | **0.00** | no |

**The pre-registered noise floor did the work it was registered for.** Two patches
moved substantially — `CTRL_SURFACE_Outlet` 0.00 → 0.66 and `Mirrors2` 0.00 → 0.55 —
and without the **1.00 threshold fixed sight-unseen in §5** that would read as "the
mechanism reaches them". It does not: below one full layer there is no continuous
prismatic layer, only partial extrusion, which is what A1 already had.

## The refutation is not marginal — nothing moved

| | A1 | B1 |
|---|---|---|
| achieved layer cells | 58,479 / 116,825 = 50.057 % | 58,968 / 116,825 = **50.475 %** |
| final extrusion | 72.296 % | 73.105 % |
| layer mesh cells | 186,709 | 187,198 |
| max skewness | 4.7820 | 4.8492 |
| small-determinant cells | 40 | 37 |
| concave cells | 14,723 | 14,733 |
| checkMesh | Failed 3 | Failed 3 |

Doubling `maxThicknessToMedialRatio` moved the global result by **+0.42 percentage
points** and moved **zero** of the fourteen blocked patches past one layer.

## Index test (§8, mandatory before any checkMesh number)

points supplied **221,881**; max point index used by faces **221,880** → needs
**221,881**; unused trailing points **0**; `0/polyMesh` **ABSENT**; both figures agree
exactly with snappy's own `Layer mesh : faces:594251 points:221881`. **No splice — the
checkMesh numbers above are readings of a mesh that exists.**

## What is now excluded, and what is not

`maxThicknessToMedialRatio` is **not** what holds the wheel/underbody group at zero.
The alternatives registered in §6 *before* this result stand untested:
`minMedialAxisAngle 90`; `featureAngle 130` across the many small patch junctions; or
the gaps being narrower than `minThickness` permits at any ratio. **The third is now
the most likely** — a limb that cares about thickness-to-medial-axis ratio was doubled
and moved nothing, which is what a hard geometric floor would look like — but that is
a reading, not a result, and it needs its own registration.

**Cost:** 211 wall s × 1 rank = **3.52 core-min** against 3.0 estimated, ratio **1.17**,
cap 15. No waste. Anchored on A1's measured 2.52 core-min, not on the collapsed build.

**Not claimed:** nothing here licences A2, which stays contingent on A1 being `PASS`.
Both A1 and B1 exceed `MESH_STANDARD` §3.2's skewness gate of 4 (4.78 and 4.85) — a
pre-existing property of this coarse family, recorded, not introduced by B1, and not
part of this rung's gate.
