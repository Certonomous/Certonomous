# M6 — WHAT A LAYER STACK WOULD HAVE TO DELIVER, IN NUMBERS

**Not an experiment and not a registration.** The DrivAer line holds the layer-extrusion
thread; duplicating it would produce two records for one question. This states **the
requirement M6 imposes**, once, so that work has a second consumer and so a proposed fix
can be checked against a number instead of an impression.

Everything below follows from **M = 0.8395, Re = 11.72e6, MAC = 0.64607 m** (AGARD AR-138
B1) and the route (d) L1 mesh as built. Nothing is assumed: U = 285.7 m/s,
ν = 1.5748e-05 m²/s, Cf = 0.00222 (Cf = 0.0576·Re^−1/5), u_τ = 9.521 m/s.

**Turbulent boundary-layer thickness at the root chord: δ = 0.01150 m = 1.43 % of chord.**

## 1. FIRST-CELL HEIGHT REQUIRED, AND THE SHORTFALL

| wall treatment | target y⁺ | **first cell height** |
|---|---:|---:|
| wall-resolved | 1 | **3.308e-06 m** |
| wall function, lower bound | 30 | 9.924e-05 m |
| wall function, mid-range | 100 | 3.308e-04 m |
| wall function, upper bound | 300 | 9.924e-04 m |

**Route (d) L1 has a first cell of 0.03125 m (refinement level 4), i.e. y⁺ ≈ 9,447.**

- **9,447× too coarse for y⁺ = 1**
- **315× too coarse even for the bottom of the wall-function range**

## 2. THE LAYER STACK, IF THE STACK IS TO FILL THE BOUNDARY LAYER

Total stack thickness = δ = 0.01150 m.

| target y⁺ | expansion | **layers** | first | last |
|---:|---:|---:|---:|---:|
| 1 | 1.15 | 45 | 3.308e-06 | 1.550e-03 |
| **1** | **1.20** | **36** | **3.308e-06** | **1.954e-03** |
| 1 | 1.30 | 27 | 3.308e-06 | 3.035e-03 |
| 30 | 1.15 | 21 | 9.924e-05 | 1.624e-03 |
| **30** | **1.20** | **18** | **9.924e-05** | **2.202e-03** |
| 30 | 1.30 | 14 | 9.924e-05 | 3.006e-03 |

## 3. THE FINDING THAT MATTERS — **LAYERS ALONE CANNOT FIX M6**

The last layer must land within roughly **2–4×** the surface cell, or the stack meets a
step it cannot transition into.

At y⁺ = 1 with expansion 1.2 the last layer is **1.954e-03 m**, so the surface cell must be
about **3.9e-03 – 7.8e-03 m**:

| surface refinement | surface cell | in range? |
|---|---:|---|
| level 4 (**as built**) | 0.03125 m | no — **16× too large** |
| level 5 | 0.01562 m | no |
| **level 6** | **0.00781 m** | **yes** |
| level 7 | 0.00391 m | marginal |

**So the surface refinement must rise from level 4 to level 6 BEFORE a layer stack is even
admissible.** Adding layers to the mesh as it stands would leave a **16× jump** between the
last layer and the surface cell — precisely the kind of discontinuity an extruder declines
to build into.

## 4. WHAT THAT COSTS

L1's wing carries **2,089 faces** at level 4; each further level is ~4× the faces.

| surface level | wing faces | × 36 layers = **layer cells alone** |
|---|---:|---:|
| 4 | ~2,089 | ~75,204 |
| 5 | ~8,356 | ~300,816 |
| **6** | **~33,424** | **~1,203,264** |
| 7 | ~133,696 | ~4,813,056 |

**A wall-resolved M6 therefore needs ~1.2 M layer cells before any volume mesh** — against
route (d) L1's **152,399 cells in total**.

## 5. THE ONE THING THIS MAY OFFER THE DrivAer THREAD

DrivAer has refuted three registered hypotheses for why snappy will not extrude layers on
its wheel/underbody group. **§3 above gives a quantitative transition criterion — last
layer within ~2–4× the local surface cell — that is checkable on any case.**

**This is offered as a candidate to test, NOT as a diagnosis.** No DrivAer mesh has been
measured here, its geometry is not M6's, and a criterion that explains one case is not
evidence about another. **If DrivAer's last-layer-to-surface-cell ratio is already inside
2–4×, this is ruled out and should be recorded as ruled out.**

---

*Derived 2026-09-12 from AR-138 B1 and the route (d) L1 mesh. No claim about M6
aerodynamics is made or implied: route (d) L1 remains an admission mesh, L2 is
`GATE FAIL`, and §A1.3 stays `FALSIFIED`. Submissions parked.*
