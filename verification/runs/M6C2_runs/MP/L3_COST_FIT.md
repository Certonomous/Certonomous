# M6C2 ROUTE (c) L3 — COST FIT AND PROPOSED CAP. **NOT A LAUNCH REGISTRATION.**

**L3 IS NOT LAUNCHED AND MUST NOT BE LAUNCHED ON THIS FILE.** The supervisor reserved
the decision on Axis C, and **L2 returned C2** (`MP/L2_RESULT.md`). This file supplies
the fitted cap so that ruling can be made on a number rather than an estimate. Instrument:
`MP/fit_l3_cost.py`, which prints every intermediate and re-runs its own checks.

## 🔴 THE COST LAW, AND WHY EVERY PRIOR ESTIMATE WAS LOW

Three successive estimates — Addendum 4 §A4.4, and two corrections to it — all came in
low. **They are not three careless readings. They are one structural fact.**

**The primitive is seconds per SUB-ITERATION per surface FACE**, and it is **not** a
single invariant across the family. Measured L1 against L2 at matched march fraction it
holds to within 0.84–1.01 for `eta < 0.75`, then diverges: **1.09 at 0.81, 1.38 at 0.91,
1.51 at 1.00.** Both curves are fit by one two-branch law in the **absolute layer index**:

> `k(i) = max(K_BASE, C · i)`  — `i` = layers laid, **not** `eta`, **not** the level count

**Mechanism:** `volSmoothIter = 100` smooths **every layer already laid**, so once that
term dominates, per-sub-iteration cost is **linear in layers laid**. Fitted jointly on
L1+L2: `K_BASE = 2.74e−06`, `C = 8.80e−08`, **crossover at layer 31.1**. In-sample wall
error **−1.3 % (L1) and −3.0 % (L2)**.

**THE DEGENERACY, WHICH IS THE REAL FINDING. L1's crossover falls at layer 31.1 of its
32, so L1's march barely enters the rising branch and CANNOT IDENTIFY `C`.** A fit on L1
alone is unidentifiable — it places the crossover at layer 47.5, beyond L1's own range —
and under-predicts L2's wall by **32.1 %**. **One level structurally cannot predict the
next one's cost under this law.** Every low estimate was a fit on a level whose own range
does not contain the crossover. That 32.1 % is the cost of extrapolating from a degenerate
fit and is **NOT carried forward as a bias**; the bias carried to L3 is the joint fit's
own L2 residual, **+3.1 %**.

**NAMING.** pyHyp's header is `| Grid Lvl | CPU Time | Sub Its | KSP Its |`. Column 3 is
**Sub Its**; column 4 is KSP-per-sub-iteration and is flat at 5. Earlier notes called
`Σ`(column 3) "ΣKSP"; the instrument uses **`SIGMA_SUBITS`**, the log's own name. The
quantities are proportional, so the physics of the earlier notes survives; the name does not.

## WHAT IS KNOWN EXACTLY, AND WHAT IS FITTED

**Exact, from the surface files' own block dims — not from the plan:** faces
**14,144 / 31,824 / 71,604** (×2.25 each step); layers **32 / 48 / 72** from `N` = 33/49/73
as **node** counts (×1.5 each step); volume cells **452,608 / 1,527,552 / 5,155,488**
(×3.375, ×11.39), the first two **confirmed by `checkMesh`**.

**The only fitted quantity is `SIGMA_SUBITS` at L3**, and the mechanism pins it tightly:

| | `SIGMA_SUBITS` | layers | **mean sub-its per layer** |
|---|---:|---:|---:|
| L1 | 26,514 | 32 | **828.6** |
| L2 | 38,920 | 48 | **810.8** |

**`SIGMA_SUBITS` is linear in layers with a near-invariant per-layer mean (trend 0.9786),
and the profile peak barely moves (5,772 at eta 0.88 → 5,920 at eta 0.85, +2.6 %).** So
`g32 = 1.5 × (per-layer trend)` and the trend is the only free quantity.

**Two earlier endpoints are DISCARDED as mechanismless:** `g32 = 1.00` would require
sub-iterations not to grow when layers grow ×1.5; `g32 = g21²` makes `SIGMA_SUBITS`
scale as `layers^1.97` with nothing behind it. They gave a band of 259–559 core-min. **A
band that wide was not uncertainty, it was two arbitrary endpoints.**

## THE BAND

| branch | `g32` | `SIGMA_SUBITS`(L3) | core-min |
|---|---:|---:|---:|
| per-layer mean keeps declining at 0.9786 | 1.468 | 57,131 | **380.6** |
| per-layer mean flat (exactly linear in layers) | 1.500 | 58,380 | **388.9** |
| per-layer mean rises with the peak (+2.6 %) | 1.538 | 59,877 | **398.8** |

Each includes the +3.1 % joint-fit bias. 1 rank, so core-min = wall minutes.

## THE PROPOSED CAP — **430 core-min**

| component | basis | core-min |
|---|---|---:|
| extrusion, **TOP of the fitted band** | fit above | 398.8 |
| wrapper overhead outside pyHyp's clock | see below | 15.5 |
| conversion + `checkMesh` + localisation | L2's 85 s × cells ×3.375, with margin | 8.0 |
| | | **422.3** |
| **REGISTERED CAP** | | **430** |

**430 core-min = 7.17 core-h. Derived $0.368 at $0.0513/core-h — DERIVED, NOT MEASURED;
the box cannot read its own billing.** Under the $25 per-run pre-authorisation.

**The wrapper overhead is the weakest component and is stated as such.** Outside pyHyp's
own clock it was **5.5 s at L1 and 71.7 s at L2 — ×13.0, while the CGNS grew only ×3.26.**
Neither cells nor bytes explain it. The 15.5 core-min above is the ×13 growth repeated;
scaling by cells instead gives 4.1. **It is carried at its top because it is unexplained,
not because it is expected.**

**THE CAP IS AT THE TOP OF THE HONEST BAND, NOT AT ITS MODE. A cap is a prediction one is
willing to be stopped by.** Overrun **stops the run**; it does not get a new budget.
**A missed forecast is not an overrun** — an estimate that misses is corrected and the gap
recorded; only the registered cap stops anything.

## 🔴 THIS CAP CANNOT LIVE INSIDE §A4.4's 300 core-min ROUTE CAP

Route (c) spend to date, timer-backed unless marked:

| item | core-min |
|---|---:|
| L1 extrusion (`EXTRUDE_WALL_S 1048.43`) | 17.47 |
| L1 conversion (~30 s of stage time) | 0.50 |
| L2 extrusion (`EXTRUDE_WALL_S 4738.16`) | 78.97 |
| L2 conversion (85 s) | 1.41 |
| probe + surface build — **stated in prior records, NOT timer-backed** | ~11 |
| **total against the 300 cap** | **~109** |
| **remaining** | **~191** |

**L3's honest band starts at 380.6 core-min for the extrusion alone — more than double
what remains.** No branch fits, and none is made to fit.

**§A4.4's cap is NOT stretched and NOT amended.** It is a frozen cap and rule 2 closes it
after first compute. **L3 therefore requires its own rung with its own pre-registration
and this cap**, committed before the solver starts and hashed against the committed blob
at launch. That separation is what keeps the arithmetic honest: a correctly derived large
number needs a correct registration, not a permission.

**The 3-D cap-stop exemption is NOT invoked.** §A4.4 re-asserts its own stop in its own
text, and this is not a cost error being covered — it is a correctly derived number.
Rule 9: a blanket is not a per-item reading.

## WHAT RUNNING L3 BUYS, AND WHAT NOT RUNNING IT COSTS

**Axis B is defined on `S3 − S1` and is unreadable without L3 by construction.** If L3 is
never built, **six of the partition's nine cells become unreachable**, including `A3·B1` —
the cell the partition names **in advance** as the route-kill and the most valuable
outcome available here. Axis A is also undetermined: `S2 = 4.15016 > 4` excludes A1, but
A2 and A3 both remain open.

**Against that: L2 returned C2.** The far-field mechanism is present on our own body, so
the route's character has changed since L1, and whether a third level of this family is
worth 430 core-min is the supervisor's call and is reserved to them. **Disk is not the
constraint** — 36 GB free; L3's artifacts project to ≈1.35 GB.

## ESTIMATE-VERSUS-ACTUAL, L2 (rule 12)

Registered 44 core-min; actual **78.97** extrusion + 1.41 conversion = **80.38**.
**Ratio 1.827.** Attribution is **misprediction, not contention** — pyHyp held 99.8 % of
one core throughout, so the box's load average of ~16.9 on 16 vCPU did not starve it.
The misprediction is the degeneracy above: the registered figure was scaled from L1 on a
node count, by a fit that could not see the crossover. Waste: **none** — no run was
abandoned and no level was re-run. A ledger row lands in `docs/COST_CALIBRATION.md`.
