# DESK ITEM — SANAA. The motor's order target is unreachable as the case is discretised

**Two-minute read. Recorded with the lab's recommendation and ADOPTED unless
Sanaa rules within one day, marked `[lab-attributed]`. T23G2 does not wait on
this.**

Raised 2026-09-01 by heat-transfer, against her directive of the same day
(`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`,
commit `f4c8e466`), §0 and §1. **Nothing here is a criticism of the directive.**
These are places where the directive and the case disagree, and the case is the
authority.

---

## 1. Her §1 target of **p in 1.5–2.5 is unreachable** on the motor as currently discretised

`verification/runs/T-family/T23G_runs/T23G_F/system/fluid/fvSchemes`:

```
div(phi,h)      bounded Gauss upwind;      <-- FIRST order
div(phi,k)      bounded Gauss upwind;
div(phi,omega)  bounded Gauss upwind;
div(phi,U)      bounded Gauss linearUpwind grad(U);   (second order)
```

**Every quantity the motor grades is a temperature, set by the energy equation,
whose convection term is first-order upwind.** No mesh — however fine, however
similar, however many levels — drives a first-order scheme to second-order
convergence.

**Nobody knew this, and it is why p = 0.375 read as a mystery.** It was found by
reading the schemes while checking her four cause candidates.

## 2. Her own §0 rule already makes the band scheme-relative, so **[0.5, 1.5] is her rule, not a lowered bar**

Her §0 point 3: *"Acceptance: p within 0.5 of the scheme's formal order (second
order: p in 1.5 to 2.5)."* The parenthesis is the **second-order instance** of a
scheme-relative rule. On a first-order scheme the same rule gives **[0.5, 1.5]**.

Her §1's *"run until p lands in 1.5 to 2.5"* is that rule instantiated under an
assumption nobody had checked — that the scheme was second order. **Two sentences
of the directive presuppose something false about the case. The rule itself is
untouched and is being applied exactly as written.**

**She should not read the change from [1.5, 2.5] to [0.5, 1.5] as the lab
lowering a bar.** It is the same bar, measured against the scheme that is
actually running.

## 3. Recommendation — fix the mesh first at unchanged scheme, then decide about the scheme

| rung | what it does | cost | wall clock | band |
|---|---|---|---|---|
| **T23G2** — registered, awaiting a supervisor's read of the comparator, **not launched** | rebuilt mesh family only: r = 1.5, wall-resolved on every level, similarity repaired, 8 cells across the wall. **Scheme unchanged.** | **579 core-min** ($0.50, derived) | **~7.9 h** | [0.5, 1.5] |
| **T23G3** — named and priced, **not run, not authorised** | second-order convection **plus** a re-run of all sixteen map points at that scheme | **2,146 core-min** ($1.84, derived) | ~16 h | [1.5, 2.5] |

**Why the mesh first, and why the scheme cannot be changed cheaply.** Her §1 says
*"the sixteen points get their band (measured at 305 W / 20 m/s, applied to all,
disclosed)."* **The sixteen points are solved with upwind.** A band measured on a
second-order ladder is a band for a *different discretisation*, so changing the
scheme costs the ladder **and** a re-solve of all sixteen points — or it costs
the transfer's honesty. Keeping upwind gives Act A a band that legitimately
applies to the numbers already on screen.

**The recommendation is therefore: run T23G2 now; treat T23G3 as hers to
authorise if she wants the second-order product.**

## 4. Three places the directive and the case disagree — she should see all three

1. **The wall is 3.9962 mm, not 3.5 mm.** Measured from the housing region's
   bounding box (0.0374643083093 − 0.0334681154230 m). Her 8-cell floor is being
   applied to the wall the geometry actually has.
2. **`NR_HOUS = 4` at T23G's coarsest level — below her floor of 8**, and
   `build_t23.py`'s own comment admits it ("the COARSE arm of a ladder is
   deliberately below it"). T23G2's coarsest carries 8.
3. **Her "L4 at r = 1.5 from L3, about 130k cells" does not fit this ladder.**
   `T23G_F` is 158,720 cells, so r = 1.5 gives 357,120. Her 130k is close to
   `T23G_F`'s **fluid region alone** (140,800), so the arithmetic appears anchored
   on a different count. T23G2 rebuilds the family rather than extending it, for
   the reasons above.

## 5. One further caveat that must travel with the band, whatever she rules

`T23_RESULTS.md` §4 measured y+ on the solved map:

| point | max y+ on the housing surface |
|---|---|
| `T23_P305_U10` | 0.4037 |
| `T23_P305_U20` | **0.7515** — where the band is measured |
| `T23_P305_U30` | **1.079** |
| `T23_P305_U40` | **1.397** |

**A band measured at U = 20 m/s, where the housing surface is wall-resolved,
would transfer to U = 30 and U = 40 m/s, where it is not.** That was registered
before compute by T23 §4.4 and is not new; it is repeated here because her §1
authorises exactly that transfer. **Any display of the sixteen points carrying
the band must disclose it.**

---

## What was settled without spending compute, so she knows what the ~180 core-min was not spent on

Three of her four cause candidates were answered from artifacts the lab already
owned, read-only, no solver launched:

- **(a) iterative convergence — EXCLUDED.** The measured change in max(T) over the
  last 2,000 iterations is an **exact zero at 12 significant figures** on every
  level. Her 10× ratio test is cleared by **≥ 4,116×**. The energy residual was
  **already at her 1e-9 target** (8.7e-10 / 9.6e-10 / 1.0e-9). Her remedy would
  have spent ~180 core-min to reproduce a zero already on disk.
- **(b) mesh similarity — a REAL DEFECT, and NOT the cause.** `build_t23.py` holds
  the expansion ratio at 40:1 while doubling layers, so the first cell refines by
  1.951 and 1.976 instead of 2.000. It is repaired in T23G2. It moves p by
  **0.014** against a shortfall of 1.1.
- **(d) a smoother companion quantity — MEASURED, and it does not rescue the
  order.** The core's volume-averaged temperature gives **p = 0.3769** against the
  maximum's 0.3796. The housing surface heat flux is **worse** — its differences
  *grow* with refinement, because it is pinned by the imposed 305 W source.
- **(c) the coarsest level outside the asymptotic range — CONFIRMED**, with an
  instrument: y+ on the heat-transfer surface is **1.42 / 0.74 / 0.38** across the
  three levels. The coarse level fails her own y+ < 1 requirement. T23G2 drops
  that resolution.

**If the rebuilt ladder still returns p ≈ 0.375, the surviving candidate is the
conjugate interface flux reconstruction** — one-sided and formally first order on
both sides, which no mesh refinement lifts. That is registered in advance as the
falsifier of the whole reading.

---

*`[lab-attributed]` pending her ruling. **Nothing here is sent, filed or shown
outside this box** (`CLAUDE.md` rule 7). T23G2 has launched no solver and is
awaiting the supervisor's read of its comparator and build script as a diff.*
