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

---

# AMENDMENT 1 — 2026-09-12. **§3's MECHANISM IS WRONG. ITS CONCLUSION IS RIGHT, REACHED BY A DIFFERENT ROUTE.**

**lines whose number changed above this section: 0**

**Nothing above is edited.** §3 stands as written, including the part now known to be
wrong, because a right answer reached by a wrong mechanism must stay visible beside its
correction or the error is invisible to the next reader.

## A1.1 WHAT IS WRONG

§3 named **the last-layer-to-surface-cell jump** as the constraint forcing level 6. **It is
not the binding constraint, and as a transferable test it is VACUOUS wherever
`relativeSizes true` is used.**

Under `relativeSizes true`, the requested last layer **is** `finalLayerThickness × local
surface cell`, by definition. So `surface_cell / last_layer = 1 / finalLayerThickness`
**always, at every refinement level**:

| `finalLayerThickness` | surface_cell / last_layer |
|---:|---:|
| 0.3 | 3.33 |
| 0.5 | **2.00** |
| 0.7 | 1.43 |

**The ratio is the dictionary restated, not the mesh measured. A criterion with no failing
branch is not a test.** The tell is that it returns the *same* number at two different
refinement levels.

## A1.2 WHAT ACTUALLY BINDS — **TOTAL STACK THICKNESS AGAINST δ**

On M6's as-built level-4 cell (0.03125 m) with `relativeSizes true`, r = 1.2, f = 0.5,
against **δ = 0.01150 m**:

| layers | first layer | **y⁺** | total stack | **vs δ** |
|---:|---:|---:|---:|---:|
| 18 | 7.043e-04 | 212.9 | 0.0902 m | **7.8×** |
| 24 | 2.359e-04 | 71.3 | 0.0926 m | 8.0× |
| 30 | 7.899e-05 | 23.9 | 0.0934 m | 8.1× |
| 36 | 2.645e-05 | **8.0** | 0.0936 m | **8.1×** |

**Enough layers to approach y⁺ ≈ 1 build a stack eight times thicker than the boundary
layer they are meant to resolve.** That — not a transition jump — is what makes the
as-built surface cell unusable.

## A1.3 THE CONCLUSION IS UNCHANGED

Derived the correct way: first layer 3.308e-06 m for y⁺ = 1; stack must total
δ = 0.01150 m; **36 layers at r = 1.2**, last layer 1.954e-03 m; under f = 0.5 that demands
a **surface cell of 3.908e-03 m — level 6 to 7.**

**Identical to §3's answer.** **Layers alone still cannot fix M6, and the surface
refinement must still rise two levels first.** Only the reason changes.

## A1.4 THE CORRECTED OFFER TO THE DrivAer THREAD — AND A WITHDRAWAL

**§5's criterion is WITHDRAWN as a test for DrivAer.** It is **NOT APPLICABLE** there, which
is **not** the same record as **RULED OUT** — "ruled out" would claim something was learned
about DrivAer, and nothing was.

**What replaces it:** **total ACHIEVED stack thickness versus the LOCAL boundary-layer
thickness**, measured on the **achieved** mesh — the layers that actually extruded — and
**never from the dictionary**, because the dictionary states a *request* and DrivAer's
entire problem is that the request is not being met. **On a case where layers are not
forming there may be no achieved stack to measure at all**, and that is the honest reason
this criterion cannot be tested the way §5 assumed.

## A1.5 THE LESSON, WHICH IS NOT THE ARITHMETIC

A second party verifying §5 would have computed **2.00 correctly and recorded a false
conclusion**, because the defect sat **upstream of the arithmetic**. **A relayed-number
check catches transcription; it does not catch a test that cannot fail.** The question to
ask of any offered criterion is not "is the number right" but **"what measurement would
make this fail, and can that measurement exist on the target case?"**

*Document version 1.1. Submissions parked.*
