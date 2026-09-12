# CRM BLENDED WALL-TREATMENT ARM — **NOT REGISTERED. THE CHANGE IT WOULD MAKE IS ALREADY MADE.**

**Finding, 2026-09-12, by a cfd `lab-lane`, in refusal of a costing request from the
cfd-supervisor. It registers nothing and gates nothing.**

---

## 0. THE PROPOSAL, AND WHY IT CANNOT BE EXECUTED

The proposal: *"cost a CRM blended arm — one line, identical mesh, exactly the shape of the
DrivAer B2 test."* Its reasoning was sound and is worth restating because **the reasoning
survives even though the arm does not**:

> The blended wall function differs from the log-law one **only below y⁺ ≈ 30**. DrivAer's
> entire body sits **above** y⁺ 34, so the swap could not possibly matter there. CRM's wing
> runs at **mean y⁺ 18.4**, inside the buffer layer, so the swap **should** matter there.
> Sanaa's idea was tested on the one case where it could not work.

🔴 **THE ARM CANNOT BE RUN BECAUSE CRM ALREADY USES THE BLENDED WALL FUNCTION.** Read from the
case's own boundary conditions — both `0.orig/nut` and the `0/nut` the run actually read:

```
wing     { type nutUSpaldingWallFunction; value uniform 0; }
```

against the DrivAer control's

```
"."      { type nutkWallFunction; ... }
```

**`nutUSpaldingWallFunction` IS the blended treatment** — the same one DrivAer's R2c arm
swapped *to*. **There is no one-line change to make: it is already made.** The k boundary
condition agrees: CRM uses **`kLowReWallFunction`**, the low-Re/blended form, where DrivAer
uses `kqRWallFunction`.

**A B2-shaped test needs two arms one line apart. CRM has only the blended arm, and building
the log-law arm to compare against would mean deliberately installing the treatment we already
know is wrong at this y⁺ — spending core-minutes to confirm a defect rather than remove one.**

---

## 1. THE MEASUREMENT THAT SHOWS THE EXISTING CHOICE WAS THE RIGHT ONE

y⁺ read from the run's **own** `yPlus` field at iteration 4000 — **11,136 face values parsed
from the binary field**, cross-checked against `postProcessing/yPlus/0/yPlus.dat`
(min 3.115 / max 44.370 / average 18.416 — **both agree**).

| statistic | value |
|---|---|
| min | 3.115 |
| p05 | 10.012 |
| p25 | 15.278 |
| **median** | **18.946** |
| p75 | 21.031 |
| p95 | 26.740 |
| max | 44.370 |
| mean | 18.416 |

| wall region | faces | share |
|---|---:|---:|
| viscous sublayer, y⁺ < 5 | 28 | 0.3 % |
| **BUFFER LAYER, 5 ≤ y⁺ < 30** | **10,938** | **98.2 %** |
| log layer, y⁺ ≥ 30 | 170 | 1.5 % |

🔴 **98.2 % OF THE WING SITS IN THE BUFFER LAYER.** Not the mean only — nearly the whole
surface. This is the single worst place to put a first cell, and it is **exactly** the region a
blended treatment exists for.

**Spalding vs log-law `νt/ν`** (κ = 0.41, E = 9.8, Spalding solved by bisection):

| y⁺ | Spalding | log-law | difference |
|---:|---:|---:|---:|
| 10.00 | 0.2056 | 0.0000 | log-law gives **nothing** |
| **18.42** (CRM mean) | **0.6838** | **0.4535** | **50.78 %** |
| 30.00 | 1.3746 | 1.1641 | 18.08 % |
| 44.37 (CRM max) | 2.2078 | 1.9945 | 10.69 % |
| 232.0 (DrivAer medium) | 11.7220 | 11.3067 | 3.67 % |
| 482.0 (DrivAer coarse) | 23.0339 | 22.3584 | 3.02 % |

**At CRM's mean y⁺ the two wall functions differ by ~51 %. At DrivAer's they differ by ~3 %.**
That is the supervisor's insight, quantified — **and it is why the lab's existing CRM setup is
already correct.** Had CRM used `nutkWallFunction`, its wall shear would have been wrong by
tens of percent over 98 % of the wing.

**ONE HONEST DISCREPANCY, DISCLOSED RATHER THAN SMOOTHED.** `DRIVAER_R2C_B2_INTERPRETATION_ADDENDUM.md`
registered **0.440 % at y⁺ 232** and **0.148 % at y⁺ 482**; this lane computes **3.67 %** and
**3.02 %** at the same y⁺ with its own bisection. **The qualitative conclusion is identical and
robust — the two functions are close at high y⁺ and far apart in the buffer layer — but the
exact percentages do not match, so the registered figures are NOT overwritten by these and
neither set is asserted over the other.** The difference is most likely a differing `νt/ν`
convention or E value. **It does not move any verdict**: B2 read `INACTIVE` on measured `Cd`,
not on either arithmetic.

---

## 2. 🔴 THE CONSEQUENCE FOR CRM'S `GATE FAIL`, WHICH IS THE POINT

**CRM's `GATE FAIL` is NOT a wall-treatment problem, and this closes that line of enquiry
rather than opening one.** The defensible treatment for a buffer-layer mesh is already in
place. G-S1 (residuals `Uz` 2.71e-04, `p` 2.41e-03 against 1e-4) and G-S2 (force plateau 24.21
counts against 1.0) must be diagnosed elsewhere.

**WHAT THE y⁺ DISTRIBUTION DOES SUGGEST, AS A LEAD AND NOT A DIAGNOSIS:** a blended function is
*valid* through the buffer layer, but the buffer layer is still where modelling error is
largest for any wall treatment. The standard remedies are **mesh** remedies — resolve to
y⁺ ≲ 1 and integrate to the wall, or coarsen to y⁺ ≳ 30 and sit cleanly in the log layer.
**At 98.2 % buffer-layer coverage, CRM is in neither regime.** That is a **mesh** rung, and L2
is currently the family's only mesh-admissible level (L1 and L3 both `GATE FAIL` on the mesh
gates), so it is not a change this lane can make inside the existing registration. **Named as
the candidate first triage item; not drafted, not costed, not claimed as the cause.**

---

## 3. WHAT THIS LANE DID NOT ESTABLISH

- **That the mesh is the cause of G-S1/G-S2.** §2's second paragraph is a **lead**. The
  residual and plateau failures could equally be numerics or genuine transonic shock
  unsteadiness at M = 0.85 — and the autocorrelation test already ruled out the *coherent*
  oscillation signature (r(T/2) ≈ 0, r(2T) ≈ 0; `CRM_WINGALONE_L2R_RESULTS_2026-09-12.md` §3).
- **Whether a log-law control arm would be informative.** It would be a *negative* control for a
  treatment already chosen, and §0 says why it is not proposed.
- **Any reconciliation of the two `νt/ν` figures** (§1). Both are on the record; neither is
  overwritten.

*Filed by a cfd `lab-lane`, 2026-09-12, refusing a costing request on measurement. It registers
no gate, threshold, cap or label. Submissions parked. No agent's message is Sanaa's consent.*
