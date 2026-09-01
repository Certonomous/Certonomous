# DMR rung R3 (h = 1/240) and the grid-convergence triple — pre-registration

Written 2026-09-01, **before any 1/240 mesh or solve exists**. Successor filing to
`DMR_PREREGISTRATION.md` (frozen `74797a57`, 2026-08-07T22:40:28Z), taken by the
route that document itself prescribes:

> *"1/240 is deliberately outside this item's 20 core-min budget; if wanted, it
> is a successor filing, not a quiet extension."* — `DMR_PREREGISTRATION.md:45-46`

**The 2026-08-07 freeze is CLOSED and is not amended by this file.** Gates V, P1
and P2 and their recorded verdicts in `DMR_RESULTS.md` stand exactly as written.
This is a new rung with new gates in its own document (CLAUDE.md rule 2).

**Condition checked before writing, and how:** `verification/runs/DMR_runs/res240`
does not exist — `ls` returns "No such file or directory", not inferred from a
missing entry in a listing. No 1/240 mesh, field or log exists anywhere on this box.

---

## 1. What this item is, and what it is not

It adds a third rung at h = 1/240 so that 1/60, 1/120 and 1/240 form a triple at
constant refinement ratio r = 2, and it asks **one** question: does this solver's
DMR solution converge under refinement, and at what observed order?

**It does not touch what DMR already claims.** Gate V is an absolute-accuracy
check of one quantity against a closed-form analytic solution, per rung. It is
not a convergence result and never becomes one. **Whatever this rung returns,
the two-rung pair is still a two-rung pair, and nobody describes it as
"grid converged", "mesh independent" or as carrying a GCI.**

## 2. THE QUANTITY QUESTION, SETTLED BY MEASUREMENT BEFORE THE RUNG IS BUILT

The obvious triple quantity is the Gate V shock position. **It is disqualified,
and so is shock speed.** Both were measured from the two existing rungs'
committed `locator_result.json` files on 2026-09-01, zero compute, before this
document was written. The measurements are recorded here so the choice of
quantity cannot later be read as chosen to fit an answer.

### 2.1 Shock POSITION is disqualified — three measured reasons

| | res60 (h = 1/60) | res120 (h = 1/120) |
| --- | --- | --- |
| Gate V error | +0.003987 | +0.003381 |
| **error in cells of its own grid** | **0.239** | **0.406** |
| error as share of travel | 0.173 % | 0.146 % |

1. **The apparent order is 0.2377.** Error ratio coarse/fine = 1.1791, so
   p = log2(1.1791) = **0.2377**. That is nowhere near an asymptotic range, and a
   third point on that trajectory is a live candidate for STAGNANT.
2. **The error is sub-cell on both rungs** (0.00338 < 0.00833; 0.00399 < 0.01667).
   It is extracted by linear interpolation *within* a cell, so a refinement study
   of it partly measures the interpolant rather than the discretisation.
3. **The error in CELLS GROWS with refinement, 0.239 → 0.406.** This is the
   decisive one and it is new. A discretisation error should shrink or hold in
   cell units; one that grows in cells while shrinking only slowly in physical
   units is dominated by a contribution that does not scale with h. The quantity
   is not measuring what a convergence study needs it to measure.

### 2.2 Shock SPEED is disqualified — the error changes sign

Least-squares slope of the incident-shock trace over the five usable writes
(t = 0.12 … 0.20), against the exact 20/√3 = 11.5470054:

| | res60 | res120 |
| --- | --- | --- |
| fitted speed | 11.5401516 | 11.5504766 |
| error | **−0.00685** (−0.0594 %) | **+0.00347** (+0.0301 %) |

The error **changes sign between the two rungs**; the ratio is **−1.9745**, so no
real observed order exists and a triple built on it classifies **OSCILLATORY**,
which is `NOT A RESULT` under rule 5 whatever the value. Per-interval speeds on
res120 scatter over 11.5186 … 11.5797, an order of magnitude wider than the
0.00347 error being fitted: the quantity is noise-dominated at this sample count.

**Recorded as a caveat on the existing record, not as a defect in it:** the fine
rung's headline 0.146 % agreement sits near an accidental zero-crossing of the
speed error. Gate V remains PASS on its own terms — it is an absolute-tolerance
check against exact theory and both rungs clear it honestly — but this is a
further reason the kinematics must not carry a convergence claim.

### 2.3 The quantity this rung DOES use: L1 self-convergence of the density field

**Why L1.** The DMR solution contains discontinuities. Pointwise and L∞ measures
do not converge at a clean rate across a discontinuity; **L1 does**, and it is the
norm the Euler-benchmark literature uses for exactly this reason. A whole-field
norm also removes the sub-cell interpolation objection of §2.1 entirely: no
crossing is located and no interpolant is involved.

**Why it is exact here.** The three grids are cell-centred, uniform and **nested
exactly 2:1** (240×60, 480×120, 960×240). Restriction from fine to coarse is
therefore an **exact conservative block average** — 2×2 for 1/120→1/60, 4×4 for
1/240→1/60 — introducing **zero interpolation error**. This is the cleanest
possible three-grid comparison and it is available only because the rungs were
laid out as they were.

**No exact solution is required.** Woodward & Colella is a benchmark
*computation*, not an exact solution, and §3 of the frozen pre-registration
already records that no numeric transcription is held. The triple is therefore a
**self-convergence** study in Roache's no-exact-solution form.

On the common 1/60 grid, over a region declared in §4.2:

- `e32 = mean over region of |R(rho_120) − rho_60|`
- `e21 = mean over region of |R(rho_240) − R(rho_120)|`
- `R = e21 / e32`, observed order `p = log2(1/R)`

## 3. Rungs

| rung | 1/dx | cells | status |
| --- | --- | --- | --- |
| R1 | 120 | 480 × 120 = 57,600 | **already solved** 2026-08-07, unchanged, not re-run |
| R2 | 60 | 240 × 60 = 14,400 | **already solved** 2026-08-07, unchanged, not re-run |
| **R3** | **240** | **960 × 240 = 230,400** | **this filing** |

R3 uses the **identical** case generator, thermophysical constants, initial
states, boundary conditions (including the coded exact-kinematics top boundary),
flux scheme, `maxCo 0.2`, `endTime 0.2`, ten writes at 0.02, and **4 MPI ranks**
as R1 and R2. One decomposition family, one numerics family, three grids.
Anything that differs invalidates the triple and is a disqualifier (§6).

## 4. Gates

### 4.1 Gate V3 — kinematics against exact theory at 1/240

Identical in form and tolerance to the frozen Gate V, applied to the new rung.
Exact incident-shock position at t = 0.2 on the row nearest y = 0.9, reference
`x = 1/6 + (y + 4)/sqrt(3)` evaluated at that row's own y.

- **PASS** iff `|x_measured − x_exact_at_row| <= 0.0231` (1.0 % of the 2.30940
  travelled distance). Otherwise **GATE FAIL**.
- Locator increment at R3 is 0.004167 = 0.18 % of travel, so the instrument
  expresses the tolerance. Stated before the solve.

### 4.2 Gate T — the grid-convergence triple (the point of this rung)

**Region A (PRIMARY, gated).** `x` in [0.25, 3.20], `y` in [0.00, 1.00] on the
common 1/60 grid. Declared now, with reasons:
- **x >= 0.25** excludes the inlet-bottom corner artifact already documented at
  `DMR_RESULTS.md:110-115` (18 / 9 cells carrying rho up to 280.7 at x < 0.15).
  Left in, it would dominate an L1 norm with a boundary artifact no gate reads.
- **x <= 3.20** stops short of the outflow boundary while fully containing the
  incident shock, whose trace at t = 0.2 spans x = 2.476 (y = 0) to 3.053 (y = 1).

**Region B (SECONDARY, reported with its own classification, not gated).**
`x` in [0.25, 3.20], `y` in [0.55, 1.00]. **y >= 0.55 lies above the primary
triple point on every rung** (measured: y = 0.3864 at res60, 0.4188 at res120), so
region B contains the incident and reflected shock system and excludes the slip
line and the wall-jet roll-up. Declared now because the roll-up is
Kelvin-Helmholtz unstable and is expected not to converge; separating the two
regions in advance is the difference between a physical finding and a post-hoc
exclusion.

**Classification, applied per rule 5 before any value is quoted:**

| `R = e21/e32` | classification | consequence |
| --- | --- | --- |
| `R < 0.95` | **CONVERGING** | report `p = log2(1/R)` and `GCI_fine = 1.25 * e21 / (2^p − 1)`, normalised by the region-mean density and quoted as a percentage |
| `0.95 <= R <= 1.00` | **STAGNANT** | **`NOT A RESULT`** for the order claim. No p, no GCI. |
| `R > 1.00` | **DIVERGENT** | **`NOT A RESULT`** for the order claim. No p, no GCI. |

**OSCILLATORY is not reachable by this instrument and that is stated rather than
omitted:** `e21` and `e32` are norms and cannot be negative, so a sign
oscillation is invisible to them. The signed diagnostic in §4.3 is carried
precisely so the record is not silent about it.

**A GCI is quoted only when the classification is CONVERGING.** A GCI on three
values that are not monotone is never quoted (rule 5).

### 4.3 Reported, NOT gated

- **The Gate V position-error triple** (0.003987, 0.003381, and R3's value) with
  its Roache classification. This is the direct test of §2.1's argument and it is
  registered as a *prediction* in §5, not as a gate.
- Fitted shock speed at R3 and the three-rung speed sequence, with sign.
- Density at t = 0.2 on 30 uniformly spaced contour levels at R3, matching the
  convention of the frozen filing.

### 4.4 The reader, and its planted control

Grading uses **`verification/runs/DMR_runs/dmr_locator_v2.py`**, committed with
this filing and **before** the rung it grades. It carries a two-sided planted
control that runs **before** any number is produced (CLAUDE.md rule 3):

- **planted perturbation** — the density field is displaced by exactly 7 whole
  cells; on a uniform grid an integer roll is exact, so the located front must
  move by exactly `7*dx`. Verified 2026-09-01 on both existing rungs: planted
  0.116666667 / 0.058333333, reader moved 0.116666667 / 0.058333333.
- **planted absence** — the crossing is removed from the Gate V row; the reader
  must **refuse**, not return a null.
- **Both sides are demonstrated able to FAIL**: with the plant neutered the
  control reports NOT SEEN and exits 2; with the refusal downgraded to a silent
  `None` it reports DID NOT REFUSE and exits 2. A control that cannot fail is
  not a control.
- **Regression:** v2 reproduces the 2026-08-07 recorded Gate V positions on both
  rungs to `|delta| = 0.000e+00`, so it is the same instrument plus a control.

`dmr_locator.py` is **not edited** and keeps the provenance of the recorded V/P1/P2
verdicts. Recorded honestly: measured against this control, **the original reader
fails the planted-absence side** — that is the shape of `x_incident_y09: null` at
t = 0.10 in both committed records.

## 5. Predictions (scored afterwards, left as written)

1. **Gate V3 PASSES** at 1/240, with `|error| < 0.006`.
2. **The Gate V position-error triple is NOT CONVERGING** — predicted STAGNANT or
   DIVERGENT. This is the falsifiable form of §2.1 and the reason the triple was
   not built on it.
3. **Region A classifies CONVERGING with 0.5 <= p <= 1.2.** First-order-ish:
   degraded from the scheme's formal order by the discontinuities.
4. **Region B classifies CONVERGING with p_B >= p_A**, the shock-only region
   converging at least as fast as the region containing the roll-up.
5. **If region A is not CONVERGING while region B is, the wall-jet roll-up is the
   cause** — a physical finding, reported as such, and region A's label stands
   unrescued.
6. Cost <= 16 core-min gross.

## 6. Budget, disqualifiers, honesty clause

| item | core-min | basis |
| --- | --- | --- |
| R3 solve | **14.0** | 8.36x res120's measured 25.09 s x 4 ranks: 4x cells and 2.09x steps (res120 took 2,111 steps, res60 1,008) |
| mesh, `setExprFields`, `decomposePar`, `reconstructPar`, `writeCellCentres` | 1.5 | 4x res120's measured sub-0.5 overhead |
| locator v2 + L1 triple analysis | 0.5 | serial post-processing |
| **ESTIMATE** | **16.0** | 4 MPI ranks, setsid, native openfoam2606 |
| **HARD CAP** | **35.0** | **a breach STOPS the run; it does not get a new budget** |

**Dollars are DERIVED, never measured** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). At $0.0513/core-h, c7a.4xlarge,
**reported-by-owner**: estimate **$0.0137**, cap **$0.0299**.

**Estimate-versus-actual calibration is owed at completion** and lands as a row in
`docs/COST_CALIBRATION.md` (CLAUDE.md rule 12). A completion report without it is
incomplete.

**Disqualifiers.** Solver crash (recorded, not softened); cap breach; **any
difference in scheme, constants, boundary conditions, `maxCo`, write times or rank
count between R3 and the two existing rungs** — the triple requires one numerics
family and a difference invalidates it rather than being corrected for; failure of
the v2 planted control, after which no number from the reader is evidence; any
edit to a gate, threshold, cap or label in this file after the first solve.

**What this rung buys, honestly.** A CONVERGING Gate T is a **self-convergence**
result: it says the scheme's own solution settles under refinement and at what
rate. **It does not say the solution is right.** The only thing in this campaign
that touches truth is Gate V, because it alone has a closed-form reference. A
`NOT A RESULT` on Gate T is a **fully acceptable pre-registered outcome** and is
recorded as the answer, not rescued by re-cutting the region, re-choosing the
norm, or adding a fourth rung to reach a nicer number. Inviscid Euler, no
turbulence model, no experimental anchor; anchor-2-class, as the frozen filing has
it.

---
*Nothing below this line existed when the rung was launched.*
