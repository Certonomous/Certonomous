# T23G — PRE-REGISTRATION: the grid triple at (305 W, 20 m/s)

**Rung id:** `T23G` — the grid triple on the T23 map's (305 W, 20 m/s) point.
**Status:** FROZEN ON COMMIT. `CLAUDE.md` rule 2.
**Version 1.0.** Amendments append at the foot as dated blocks, never by
rewriting above (`CLAUDE.md` rule 6).

**NOTHING HAS RUN UNDER THIS REGISTRATION.** At the moment this document is
committed, `verification/runs/T-family/T23G_runs/` contains no case directory,
no mesh, no `log.blockMesh`, no `log.solve` and no time directory. That is the
`§2b` condition, and it is **checked, not asserted** — see §11.

---

## 0. THE ORDER, AND WHAT IT DOES AND DOES NOT AUTHORISE

Sanaa, 2026-09-01 ~03:10Z, captured at
`etc/sessions/2026-09-01T0310Z_sanaa_actA_figure_header_standard.md`
(commit `569346b3`), Act A item (4), verbatim:

> **0.1 °C significant figures until the grid triple lands; triple at
> (305 W, 20 m/s) tonight.**

And Act A item (1), verbatim, which is why a **core** quantity is registered
here rather than added later:

> **(1) Two peak columns, core and housing; margin computed on the core; drop
> "hottest point" wording from the housing value.**

**What this authorises:** three mesh levels on one operating point, and the
gates below. **What it does not authorise:** a launch. This registration is
written before any compute and is committed before any compute. *"Tonight"* is
a throughput instruction and is not an exception to rule 2 — a pre-registration
written after the answer is known is worth nothing.

### 0.1 T23 §4.2 recorded this triple as DEFERRED and BLOCKED. That is disclosed, not stepped around.

`T23_PREREGISTRATION.md:515-532` records the map's Roache triple as
**DEFERRED and BLOCKED** on a cross-team dependency, `CASE3-DEP-1`. The same
section discloses, in the T23 lane's own words, that **`CASE3-DEP-1` is not
registered anywhere that lane could find** — it exists only in an uncommitted
T21 draft that freezes nothing.

**This rung proceeds on Sanaa's direct order of 2026-09-01, and on nothing
else.** No agent unblocked it, and no agent's reading of `CASE3-DEP-1` is
offered here as grounds. T23's own deferral text stands unaltered; it is
frozen and post-compute and is not edited. If `CASE3-DEP-1` is later found to
be a real dependency with real content, that is a finding against **this**
rung's result, and it is recorded as such rather than argued away.

### 0.2 T23 §4.4's y+ block does NOT fire, and this is measured rather than assumed

`T23_PREREGISTRATION.md:545-557` registers that a measured y+ above 1 **on the
housing surface** blocks the triple. **MEASURED** from
`T23_runs/T23_P305_U20/log.yPlus.fluid`, on the housing surface patch
`fluid_to_housing`: **min 0.7334, max 0.7515, average 0.7416.** That is ≤ 1 and
the block does not fire.

**Disclosed in the same breath:** on `duct_wall` the same file reads max
**2.3958**, and on `centrebody_up` max **1.8261**. Those are not the housing
surface and §4.4's condition is written against the housing surface, so they do
not fire it — **but they are stated here rather than left for a reader to
discover**, and §7.4 registers what happens to them under refinement.

---

## 1. THE CASE, AND THE ONE THING ABOUT IT THAT GOVERNS EVERY NUMBER BELOW

The source case is `verification/runs/T-family/T23_runs/T23_P305_U20`, a landed
L1 run: `chtMultiRegionSimpleFoam`, steady conjugate heat transfer, k-ω SST in
the fluid, three regions — `fluid`, `housing`, `core` — coupled at two
interfaces.

> ### ⚠ THE CASE IS A 5° WEDGE, ONE CELL THICK IN THE CIRCUMFERENTIAL
> ### DIRECTION. REFINEMENT HAPPENS IN **TWO** DIRECTIONS, NOT THREE.

Every `hex` block in `T23_P305_U20/system/blockMeshDict:64-77` carries divisions
of the form `(nr nz 1)`. The third division is **1 and stays 1** — a wedge with
more than one cell across the sector is not a wedge. So:

- **`dim = 2`**, and `dim = 2` is passed to every call in
  `scripts/roache_triple.py`, which prints it beside every order and every GCI.
- **The representative mesh size is `h = (1/N)^(1/2)`**, not `(1/N)^(1/3)`.
- **A level that quadruples the cell count is `r = 2`, not `r = 2` from an 8×
  jump.** The arithmetic is written out in §3 and the cost in §8 is built on
  **4×**, never on 8×.

`VERIFICATION_CHARTER.md` §3.1 is the governing clause: dimensionality decides
exactly one thing, it cannot corrupt a band, and it can only wrongly admit or
wrongly reject one. It is therefore registered here explicitly rather than left
to a default.

---

## 2. THE MESH LADDER — three levels, and how all three regions stay consistent

`build_t23.py:65-70` parameterises the entire mesh in **eight integers**, and
every block in the dict is generated from them. That is the whole reason a
consistent conjugate refinement is available at all.

| symbol | meaning | **COARSE** | **MEDIUM** | **FINE** |
|---|---|---:|---:|---:|
| `NR_BL_IN` | fluid inner boundary layer, radial | 20 | **40** | 80 |
| `NR_MID` | fluid core band, radial | 20 | **40** | 80 |
| `NR_BL_OUT` | fluid outer boundary layer, radial | 15 | **30** | 60 |
| `NR_HOUS` | **housing**, radial | 4 | **8** | 16 |
| `NR_CORE` | **core**, radial | 12 | **24** | 48 |
| `NZ_UP` | upstream, axial | 40 | **80** | 160 |
| `NZ_MID` | motor station, axial | 70 | **140** | 280 |
| `NZ_DOWN` | downstream, axial | 50 | **100** | 200 |

The MEDIUM column is `build_t23.py:65-70` **unaltered**. COARSE is every entry
halved; FINE is every entry doubled. **All sixteen derived integers are exact
integers** — no rounding, so no level is off-ladder.

### 2.1 Consistency across the three regions is STRUCTURAL, not asserted

**All eleven blocks live in one `blockMeshDict` and the regions are cut out of
it afterwards by `splitMeshRegions`.** Scaling all eight integers by the same
factor therefore refines `fluid`, `housing` and `core` by the same factor **in
the same two directions**, and it cannot do otherwise. Concretely, the shared
edges:

- The housing block `(NR_HOUS, NZ_MID)` shares its **axial** division `NZ_MID`
  with the core block and with all three mid-station fluid blocks. One integer,
  one edge, all three regions.
- The `housing_to_fluid` and `housing_to_core` interfaces are **cut from
  conforming block faces**, so both sides carry the same face count at every
  level. **The interface is the same interface at all three levels**, which is
  the condition a conjugate ladder has to meet and which a per-region
  independent refinement would break.

**REGISTERED:** the ladder is generated by scaling the eight integers and by
nothing else. No block is added, removed, split or re-graded; the geometry
(`R0`–`R5`, `Z0`–`Z3`), the wedge half-angle, the eleven-block topology and the
ten patches are byte-identical across levels because they are generated by the
same code from the same constants.

### 2.2 What IS asserted across levels, and how (mesh identity does NOT apply here)

Mesh identity is the wrong instrument for a grid ladder — the meshes are
*supposed* to differ. What is asserted instead, level to level, and checked by
the comparator before any grading:

| asserted invariant | how it is checked |
|---|---|
| **geometry** | the `vertices` block of each level's `blockMeshDict` is byte-compared across the three levels; the eight integers appear only in the `blocks` block |
| **boundary conditions** | every file under `0.orig/{fluid,housing,core}` is byte-compared across levels |
| **physics / material properties** | every file under `constant/` except `polyMesh` is byte-compared across levels |
| **numerical schemes** | `system/fvSchemes` and `system/{fluid,housing,core}/fvSchemes` are byte-compared across levels |
| **operating point** | `P_LOSS = 305.0 W`, `U_INF = 20.0 m/s`, `T_INF = 288.0 K`, and the wedge sector factor `P_SECTOR = P_LOSS × (2·HALF)/(2π)` are generated from the same constants and appear identically in each level's `constant/fluid/fvOptions` |
| **iteration count** | `endTime 10000`, `deltaT 1`, `writeInterval 10000` in every level's `system/controlDict` — **held fixed**, so the levels differ in `h` and in nothing else |
| **solver** | `chtMultiRegionSimpleFoam`, 1 rank, at every level |

A byte difference in any row above is a **REFUSAL**, not a note.

**Deliberately NOT asserted identical:** `system/fvSolution` linear-solver
tolerances are held identical, but the *number of linear iterations actually
taken* differs by level, as it must. That is not an invariant and is not
claimed as one.

---

## 3. THE REFINEMENT RATIO — DERIVED FROM THE CELL COUNTS, NOT ASSUMED

### 3.1 The cell counts

Radial totals per level: fluid `NR_BL_IN + NR_MID + NR_BL_OUT`; axial totals
`NZ_UP + NZ_MID + NZ_DOWN`.

| region | **COARSE** | **MEDIUM** | **FINE** |
|---|---:|---:|---:|
| `fluid` | 55 × 160 = **8,800** | 110 × 320 = **35,200** | 220 × 640 = **140,800** |
| `core` | 12 × 70 = **840** | 24 × 140 = **3,360** | 48 × 280 = **13,440** |
| `housing` | 4 × 70 = **280** | 8 × 140 = **1,120** | 16 × 280 = **4,480** |
| **total** | **9,920** | **39,680** | **158,720** |

**The MEDIUM column is VERIFIED against the source case's own `checkMesh`
logs**, not predicted: `T23_P305_U20/log.checkMesh.fluid:44` reads `cells:
35200`, `log.checkMesh.housing:44` reads `1120`, `log.checkMesh.core:44` reads
`3360`, and `log.blockMesh:121` reads `nCells: 39680`. **The arithmetic above
reproduces every one of those four numbers**, which is what licenses using the
same arithmetic for the two levels that do not exist yet.

### 3.2 The ratio, with the arithmetic shown

Cell-count ratios, exact:

    N_med  / N_coarse = 39,680  /  9,920 = 4.000000  (exact)
    N_fine / N_med    = 158,720 / 39,680 = 4.000000  (exact)

At `dim = 2`, `h ∝ (1/N)^(1/2)`, so

    r21 = r32 = (4)^(1/2) = 2.000000

**And the same r arrives by a second, independent route**: every one of the
eight block-division integers doubles from level to level, so each block's cell
edge halves in each of the two resolved directions. `r = 2` directly, with no
appeal to a cell count at all. **The two routes agree, and that agreement is
the check.**

> ⚠ **r = 2 IS A 4× CELL COUNT HERE, NOT AN 8× ONE.** The cost model in §8 is
> built on 4× per level. Writing `r = 2` beside a cost derived from 8× is the
> specific error this section exists to prevent.

### 3.3 r is the same in every region, which is why a total-cell input is legitimate

`scripts/roache_triple.py` takes cell counts and `dim` and derives `r` from
them. It is fed the **totals**. That is only sound because the ratio is
region-independent, and it is:

    fluid    8,800 → 35,200 → 140,800   ×4, ×4  → r = 2, 2
    core       840 →  3,360 →  13,440   ×4, ×4  → r = 2, 2
    housing    280 →  1,120 →   4,480   ×4, ×4  → r = 2, 2
    TOTAL    9,920 → 39,680 → 158,720   ×4, ×4  → r = 2, 2

**REGISTERED:** the comparator recomputes all four rows from the levels' own
`checkMesh` logs and **refuses** if any region's ratio departs from 4 by more
than 0 cells. A uniform ladder that is not uniform in one region is a build
fault, and it is caught before anything is graded.

---

## 4. THE GRADED QUANTITIES — all three, all binding

| id | quantity | region | reader path | why it is here |
|---|---|---|---|---|
| **Q1** | `max(T)` over the whole region | `housing` | `internalField` of `<endTime>/housing/T` | the housing peak column Act A shows |
| **Q2** | area-averaged `T`, area-weighted by real face areas | housing side of `housing_to_fluid` | `value` entry of the `housing_to_fluid` patch in the `boundaryField` of `<endTime>/housing/T` | the interface temperature Act A's radial figure is anchored on |
| **Q3** | `max(T)` over the whole region | **`core`** | `internalField` of `<endTime>/core/T` | **Sanaa item (1): the core peak column, and the column the 200 °C margin is computed on** |

### 4.1 ⚠ Q3 IS REGISTERED NOW, BEFORE THE ANSWER EXISTS, AND THAT IS THE POINT

Sanaa's item (1) makes the **core** peak the quantity the margin is computed
on. A core quantity added to this ladder **after** the fine level had run would
be a gate chosen with the answer in hand, which is exactly what rule 2 forbids.
**Q3 is therefore registered here, with the same standing, the same gates and
the same planted-zero control as Q1 and Q2.**

### 4.2 Which is gated: ALL THREE, and the rung verdict is the WORST of them

**REGISTERED: Q1, Q2 and Q3 are each fully gated, and each binds.** There is no
"primary" quantity and no "diagnostic only" quantity in this rung.

**The rung verdict is the worst verdict across the nine cells** (three
quantities × the three gate families of §5), on the ordering

    NOT A RESULT  <  GATE FAIL  <  PASS

**Why no quantity is demoted to a reported diagnostic:** a printed discrepancy
labelled non-binding is worse than one never computed. If Q2's triple is
`OSCILLATORY` while Q1's and Q3's converge, the rung is **NOT A RESULT** and
Act A does not get 0.1 °C — it does not get to keep two thirds of a grid
convergence claim.

### 4.3 The triple is run on ΔT = T − 288.0 K, and here is the proof that this cannot move a verdict

`T_inf = 288.0 K` is registered at `build_t23.py:75` and is the inlet
`fixedValue` in each case's own `0.orig/fluid/T`. **REGISTERED: every quantity
is converted to `ΔT = T − 288.0 K` before it is handed to
`scripts/roache_triple.py`.** The reason is `analyse_t23.py:117-120`, this
family's own precedent: the 288 K offset is common to every level and carries
no information, and a percentage taken on absolute kelvin flatters the result
by construction — **2 % of 342 K is 6.8 K, which grades nothing; 2 % of a 54 K
rise is 1.1 K, which grades something.**

**A constant shift is provably harmless to everything except the percentage:**

- `e21 = f_med − f_fine` and `e32 = f_coarse − f_med` are **differences**, so
  the shift cancels exactly.
- The observed order `p` is a function of `e32/e21` alone → **unchanged**.
- The triple's state (`CONVERGING` / `OSCILLATORY` / `STAGNANT` / `DIVERGENT` /
  `EXACT` / `DEGENERATE`) is a function of `e21`, `e32` and `r` → **unchanged**.
- `GCI_abs` is `Fs·|e21|/(r^p − 1)` → **unchanged**, and it is in kelvin.
- **`GCI_pct` divides by `f_fine` and is the ONLY quantity that moves.** That
  is the intended effect and the whole reason for the shift.

**REGISTERED: the comparator asserts this rather than trusting it** — it runs
the triple twice, once on `T` and once on `ΔT`, and **refuses** unless the
state, the observed order and `GCI_abs` agree to **1e-9 relative** between the
two. A registered claim that costs nothing to check is checked.

**MEASURED, before the freeze, by driving the instrument on a synthetic
first-order triple** (`p = 1`, `r = 2`, ΔT 55.525 / 54.175 / 53.500 K on this
rung's actual cell counts):

| | on **ΔT** | on **absolute T** | moved? |
|---|---:|---:|---|
| state | `CONVERGING` | `CONVERGING` | no |
| observed order | 1.000000 | 1.000000 | no — 6.9e-14, float noise |
| `GCI_abs` | 0.84375 K | 0.84375 K | no — 9.8e-14, float noise |
| **`GCI_pct`** | **1.5771 %** | **0.2471 %** | **yes — a factor of 6.4** |

**Grading the percentage on absolute kelvin would have made the 2 % legacy bar
trivially passable.** That is the flattery-by-construction this section exists
to prevent, and it is now a measured number rather than an argument.

*(The same drive found a defect in this instrument's first draft: a bare
absolute 1e-12 tolerance had only 10× margin over that float noise and would
have spuriously refused a triple whose `GCI_abs` ran to tens of kelvin. The
tolerance is relative for that reason, and the reason is in the comparator at
`SHIFT_INVARIANCE_RTOL`. A genuine failure of shift-invariance is O(1), not
O(1e-13), so nothing this assertion exists to catch is let through.)*

---

## 5. THE GATES — frozen thresholds, frozen labels

Rule 5 governs first and governs absolutely. `scripts/roache_triple.py`
implements it and is **called, never reimplemented**; its `_seal` (line 656)
raises rather than asserts, so `-O` cannot strip it.

### 5.0 Rule 5's order, restated so the gates below cannot be read out of order

1. **any level not iteratively converged or not plateaued → NOT A RESULT**, and
   G-ORDER, G-GCI-DISPLAY and G-GCI-LEGACY are **NOT EVALUATED** and are printed
   as `NOT EVALUATED`, never as passed;
2. **finest triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` /
   `DEGENERATE` → NOT A RESULT**, with the value, **every** triple and **every**
   order printed beside it, and **no GCI quoted**;

   *(Rule 5's wording "both triples" comes from `T1b_L4_AMENDMENT.md`, where a
   FOUR-level ladder yields two. **A three-level ladder yields exactly one
   triple**, and `roache_triple.all_triples` returns that one. The instrument
   prints all of them, however many there are; this rung's records will show
   one, and that is the correct count, not a missing second.)*
3. **`CONVERGING` → the band verdict**, with the GCI printed at **Fs = 1.25**.

**The gate is one-way: it may turn a PASS or a GATE FAIL INTO NOT A RESULT and
never the reverse.** `roache_triple._seal` refuses if that is violated.

**A GCI is never quoted beside three values that are not monotone.** The module
refuses; the comparator does not get an opportunity to print one.

### 5.1 The four gate families

| gate | threshold, FROZEN | what makes it FAIL | could a wrong treatment still pass it? |
|---|---|---|---|
| **G-CONV** — iterative convergence, per level | initial residual at the last `Time = 10000` block ≤ **1e-6** for **`Uy`, `Uz`, `h`, `p_rgh`, `k`, `omega`** | any one component above 1e-6 → that level is not CONVERGED → rule 5 step (1) → **NOT A RESULT** | a solve stalled at a wrong answer with tiny residuals would pass; that is why G-PLATEAU and the triple sit on top of it |
| **G-PLATEAU** — stationarity, per level, per quantity | peak-to-peak spread of the last **11** samples (iterations 9000…10000, `writeInterval` 100) ≤ **0.010 K** | a spread above 0.010 K → not PLATEAUED → rule 5 step (1) → **NOT A RESULT** | a limit cycle of amplitude < 0.01 K would pass; it would also be irrelevant to a 0.1 °C claim, which is why the threshold is set at one tenth of the display quantum |
| **G-BAND** — the physicality band on the fine value | `ΔT_fine ∈ [−14.85 K, +185.15 K]`, i.e. **0 °C to 200 °C**, carried forward from `T23_PREREGISTRATION.md:183` B1/B2 | a fine value outside → **GATE FAIL** | yes — a wrong treatment can land inside 0–200 °C. It is a physicality floor, not the grid claim; G-ORDER and G-GCI-DISPLAY carry the grid claim |
| **G-ORDER** — the observed order | `p ∈ [0.80, 2.50]` at `dim = 2` | `p` outside → **GATE FAIL** | a coincidental order from a wrong discretisation could pass; the falsification statement in §6 is what makes this a claim rather than a net |
| **G-GCI-DISPLAY** — **the gate that answers Sanaa's actual question** | `GCI_abs ≤ 0.050 K` at Fs = 1.25 | above 0.050 K → **GATE FAIL**, and **Act A does not get 0.1 °C significant figures** | no wrong treatment passes a 0.05 K bar by accident on a 54 K rise; this is the tightest gate in the rung |
| **G-GCI-LEGACY** — the bar the directive already wrote | `GCI_pct(ΔT) < 2.0 %` at Fs = 1.25 | ≥ 2 % → **GATE FAIL** | yes; it is a loose bar and is graded only because `T23_PREREGISTRATION.md:518` already registered it, so dropping it silently would be a quiet lowering of a bar |
| **G-REPRO** — determinism of the MEDIUM level | `\|Q1(T23G_M) − 342.1749743329 K\| ≤ 1e-6 K` | above → **GATE FAIL**, and the whole ladder is suspect because its middle rung is not the case it claims to be | a build with a different mesh, a different BC or a different source would **not** reproduce this to 1e-6 K, so it is a control, not an identity (`VERIFICATION_CHARTER.md` §2a) |

### 5.2 ⚠ G-GCI-DISPLAY AND G-GCI-LEGACY ARE DIFFERENT BARS, AND SAYING SO NOW IS THE MOST USEFUL THING THIS DOCUMENT DOES

`T23_PREREGISTRATION.md:518` carries directive §3.6's bar: **GCI_fine < 2 %**.
Sanaa's order asks a different question: **may Act A print 0.1 °C?**

On a ~54 K rise, 2 % is **≈ 1.1 K**. A ±1.1 K uncertainty **does not support a
0.1 °C display.** The two bars are 22× apart. **REGISTERED, before any level
runs: passing G-GCI-LEGACY is NOT passing G-GCI-DISPLAY, and a PASS on the
legacy bar may never be reported as licensing 0.1 °C.**

**And the honest prediction, registered now so it cannot be claimed afterwards:
G-GCI-DISPLAY is EXPECTED TO FAIL.** See §6.3. **The expected honest outcome of
this rung is that Act A drops to 1 °C, not that it earns 0.1 °C.** If the run
says otherwise, the run wins.

### 5.3 ⚠ THE FINE VALUE IS GRADED. THE RICHARDSON EXTRAPOLATE IS NEVER GRADED.

`scripts/roache_triple.py` carries a **live, documented sign defect in its
Richardson extrapolate** — its module docstring, lines 26-74, records that both
parent implementations return `f_fine + e21/den` where Roache's convention is
`f_fine − e21/den`, and that `richardson + richardson_parent_convention ==
2·f_fine` exactly.

**The defect is survivable in that module for exactly one reason: it is
display-only there.** `grade_ladder` grades `levels[-1]["value"]` — the fine
value — and no verdict it emits is a function of `richardson`.

> **REGISTERED: this rung grades the FINE VALUE. No gate in §5.1 reads the
> extrapolate. Both forms are printed beside the fine value, under their own
> names, with the sign disclosure carried through to the artifact's face.**

Gating on the extrapolate would make a **known** display-only defect
**load-bearing in a document written after the defect was known.** That is not
a risk this rung takes.

---

## 6. THE EXPECTED OBSERVED ORDER, AND WHAT WOULD FALSIFY IT

### 6.1 ⚠ IT IS NOT SECOND ORDER, AND THE REASON IS ON DISK

The obvious registration would be *"second order is the expectation for these
schemes."* **It is wrong here, and reading the frozen scheme files before
writing the band is what found it.**

From `T23_P305_U20/system/fluid/fvSchemes`:

| scheme | setting | formal order |
|---|---|---|
| `div(phi,U)` | `bounded Gauss linearUpwind grad(U)` | ~2 (limited) |
| **`div(phi,h)`** | **`bounded Gauss upwind`** | **1** |
| `div(phi,k)`, `div(phi,omega)`, `div(phi,K)` | `bounded Gauss upwind` | 1 |
| `laplacianSchemes` | `Gauss linear corrected` | 2 |
| `snGradSchemes` | `corrected` | 2 |

And from `system/housing/fvSchemes` and `system/core/fvSchemes`: the solids
carry **`divSchemes { default none; }`** — no convection at all — and a
second-order `Gauss linear corrected` Laplacian.

**The energy equation's convective transport in the fluid is FIRST-ORDER
UPWIND.** It is the lowest-order scheme in the causal path that sets Q1, Q2 and
Q3, and in a composite the lowest order dominates asymptotically.

**The physical argument that this carries through to the solids rather than
being attenuated:** the solids are highly conductive (`k_Al = 167`,
`k_core = 40 W/mK`) against air (`k_air = 0.026 W/mK`), so both solids are close
to isothermal and the whole registered temperature rise is set by the **air-side
convective resistance**. Confirmed on the medium level already on disk:
Q3 − Q1 = **4.09 K** against a rise above `T_inf` of **54–58 K**, so ~93 % of
the answer is the fluid's. **The first-order error in the fluid transfers to the
solid peaks essentially undiluted.**

### 6.2 THE REGISTERED PREDICTION, AND ITS FALSIFIER

> **PREDICTION, FROZEN: `p ≈ 1.0`** on all three quantities, because
> `div(phi,h) = bounded Gauss upwind` is rate-limiting.
>
> **FALSIFIER, FROZEN: a measured `p > 1.5` falsifies this reading.** It would
> say the first-order energy convection is *not* rate-limiting for the solid
> peak temperatures — plausibly because the near-wall grading is fine enough
> that numerical diffusion is subdominant to the resolved gradient. **That is a
> real finding about this discretisation and it is reported as one**, not
> quietly enjoyed as a better-than-expected number.

**The band `p ∈ [0.80, 2.50]` (G-ORDER) is wider than the prediction on
purpose**, and its edges are derived rather than chosen: **0.80** sits just
below first order, **2.50** just above second, and the interval is exactly the
span the scheme mix on disk can produce. **It is not directive §3.6's
`[1.3, 2.5]`**, and that departure is declared here, loudly, before any level
runs:

> ⚠ **THIS RUNG DOES NOT ADOPT `T23_PREREGISTRATION.md:518`'s BAND
> `p ∈ [1.3, 2.5]`.** That band presumes second order. Against
> `div(phi,h) = upwind`, a `p` near 1.0 would GATE FAIL it — and the failure
> would be a fact about the *band*, not about the grid. **The band is being
> widened at the bottom BEFORE any level has run, on evidence that is a file on
> disk and quotable today.** Widening it after a `p = 1.02` came back would be
> indefensible; widening it now, with the scheme file quoted, is the only
> honest moment to do it.

**Interaction with rule 5, stated so it cannot be read out of order:**
`roache_triple.STAGNANT_FLOOR = 0.5`. So `0 < p < 0.5` is **STAGNANT →
NOT A RESULT** (rule 5 step 2, before G-ORDER is reached). `0.5 ≤ p < 0.80` is
`CONVERGING` per the module but **GATE FAIL** on G-ORDER. The two do not
conflict and neither is skipped.

### 6.3 The consequence for G-GCI-DISPLAY, registered as a prediction

At `r = 2` and `p = 1`, the GCI denominator `r^p − 1` is **1**, not the **3** a
second-order ladder would give. **First order costs a factor of 3 in the error
bar.** To pass `GCI_abs ≤ 0.050 K` at `p = 1` and `Fs = 1.25`, the
medium-to-fine change must satisfy `|e21| ≤ 0.040 K` on a ~54 K rise — a
relative change of **0.074 %** across a 4× cell jump.

> **REGISTERED PREDICTION: G-GCI-DISPLAY is expected to GATE FAIL, and the
> expected honest outcome of this rung is that Act A's temperatures drop to
> 1 °C significant figures rather than rising to 0.1 °C.**

This is written down **because it is the outcome a lane would be tempted to
soften after the fact.** If the measured `GCI_abs` comes in at 0.03 K, the gate
passes on its own terms and this prediction was simply wrong — which is what a
registered prediction is for.

---

## 7. THE INSTRUMENTS

### 7.1 The planted-zero control — `CLAUDE.md` rule 3, one per reader, per level

Three readers (Q1, Q2, Q3) × three levels = **nine controls**, each carrying
every clause of this family's registered pattern
(`T23_PREREGISTRATION.md:464` §3.6; model instrument
`T24_runs/analyse_t24.py`):

1. **COPY FIRST.** The control never writes into a case. A scratch tree is
   made; **if the scratch's `realpath` resolves inside the case, the control
   REFUSES.**
2. **NEGATIVE ARM AT BITWISE ZERO.** Two reads of identical bytes must differ
   by **exactly `0.0`**. **No absolute tolerance.** A noisy reader is a refusal.
3. **POSITIVE ARM: a MEASURED magnitude ladder**
   `(10, 1, 1e-1, 1e-2, PLANT, 1e-3, 1e-4, 1e-5, 1e-6)` K, with the **detection
   floor MEASURED and printed**, exact and epsilon-free.
4. **REFUSE IF THE READER IS BLIND.** No magnitude producing a non-zero read →
   refusal, not a zero.
5. **THE SIZING PREDICATE IS RELATIVE:** `got >= PLANT * (1 - 1e-9)`, plus
   `got >= 0.1 * PLANT`. No absolute epsilon anywhere.
6. **`PLANT` IS IMPORTED** from `scripts/roache_triple.py` (`PLANT =
   1.234e-03`) and **is never redefined** in the comparator.
7. **The Q2 planter plants into EVERY face** of `housing_to_fluid`, so Q2's
   expected shift is exactly `mag` and not `mag/N`.
8. **Restore is verified**: the case file and the restored copy are byte-compared
   afterwards; a difference is a refusal.

`grade_ladder` **refuses to grade at all** without a passed control
(`assert_plant_control`, line 509). A missing control is not a warning.

**A live false zero this family already caught, and why the y+ reader keeps its
own guard:** `postProcess -func yPlus` prints *"Unable to find turbulence model
… yPlus will not be calculated"* and then *"y+ : min = 0, max = 0"*. A reader
parsing only the second line reports a perfect zero from a tool that has
already said it cannot see a non-zero. **REGISTERED: those zeros are REFUSED,
never read** (`analyse_t23.py:436-447`).

### 7.2 Strict completion — rule 4, DELEGATED and CALLED, never reimplemented

**REGISTERED: `verification/runs/T-family/T23_runs/mark_done_t23.py` is the sole
completion authority, and the comparator CALLS it as a subprocess** —
`mark_done_t23.py --root <T23G_runs> T23G_C T23G_M T23G_F`. It is already
parameterised by `--root` and by case name (`mark_done_t23.py:396-405`) and it
carries its own `--selftest`. **No new completion instrument is written.** A
second implementation of rule 4 for the same case family is a divergence
hazard, not a safeguard; the comparator contains no independent completion
logic, and a case without a fresh `DONE.<case>` marker is not graded.

**Stale-marker re-check, REGISTERED:** a `DONE.<case>` marker older than the
case's own `<endTime>` field files is **re-verified from raw artefacts, not
trusted.**

**⚠ THIS RUNG'S FIELD TUPLE, STATED EXPLICITLY AND NOT INHERITED FROM T1b.**
This is a three-region conjugate case, so the tuple is **PER REGION** and there
is **no `0/T`** to guard against:

| region | required at `<endTime>` |
|---|---|
| `fluid` | **`T`, `U`, `p`, `p_rgh`, `alphat`, `nut`, `k`, `omega`** |
| `housing` | **`T`, `p`** |
| `core` | **`T`, `p`** |

**This tuple is transcribed from the instrument that enforces it**
(`mark_done_t23.py:79-83`), not restated from memory, and it is **not** T1b's
single-region `T U p_rgh alphat nut k omega`: this case has two solid regions
that carry only `T` and `p`, and a fluid that additionally carries `p`.

**The age-guard referent is `0/housing/T`, not `0/T`** — the launcher touches
`0/housing/T` **last**, so that file dates the run allowed to produce the
answer (`mark_done_t23.py:14-22`, T23 §3.5 conjuncts 4 and 6). Every field in
the table above, in every region, must be **NEWER** than it.

The six clauses, all of which must hold: `rc = 0`; an `End` line; **last time ==
`endTime` = 10000**; the per-region fields above present; `ExecutionTime` count
== the registered step count **10,000**; and the age guard. **Any failing clause
means NOT DONE. The instrument REFUSES rather than degrades.**

### 7.3 The Ux exclusion — a registered decision, with its justification measured

**REGISTERED: G-CONV asserts on `Uy`, `Uz`, `h`, `p_rgh`, `k`, `omega`.
`Ux` is EXCLUDED BY DECISION.**

`x` is the wedge-normal direction. A wedge is axisymmetric by construction, so
`Ux ≈ 0` everywhere, and OpenFOAM normalises each component's initial residual
by that component's own scale — **a 0/0 normalisation that carries no
information.** On the source case the last `Time = 10000` block reads
`Ux` initial residual **0.137** while `Uy` reads **5.48e-10** and `Uz`
**3.75e-12**. **A reader that greps "the last U residual" would call this case
unconverged, and would be wrong.**

**The exclusion is never asserted bare: `max|Ux| / max|Uz|` is MEASURED per
level and printed beside it**, so a reader can see that `Ux` is negligible
rather than take the exclusion on trust (`analyse_t23.py:414-431`).

**G-CONV on the source case, MEASURED, all six components ≤ 1e-6:**
`h` 9.574e-10, `p_rgh` 9.923e-09, `omega` 6.091e-10, `k` 9.729e-10,
`Uy` 5.478e-10, `Uz` 3.754e-12.

### 7.4 y+ under refinement — MEASURED and REPORTED, NOT GATED

`simpleGrading` holds each block's **total** expansion ratio fixed while the
divisions double, so the first cell height falls roughly linearly and **y+
approximately halves per level**. Projected from the source case's measured
values: housing surface max ~1.50 / **0.75** / ~0.38 across coarse / medium /
fine; `duct_wall` max ~4.79 / **2.40** / ~1.20.

**REGISTERED: y+ is MEASURED per level and REPORTED beside every row, and is
NOT a gate in this rung** — following `T23_PREREGISTRATION.md:545-557`, on the
same ground: a quantity whose value is unknown at registration cannot honestly
carry a pre-registered threshold in the document that first measures it.

**REGISTERED DISCLOSURE, not a verdict-changer:** if any level's measured y+
exceeds **5** on any wall patch, that level has crossed out of the viscous
sublayer into the buffer region, where k-ω SST's blended wall treatment changes
character. **That is disclosed on the artifact's face beside the order**, because
it would mean the levels do not share one wall treatment and the measured order
is partly a wall-model artefact. **It does not by itself void the triple**, and
saying so now prevents it being used later either to excuse a bad order or to
quietly void a good one. On the projection above no level reaches 5, so this is
registered against a contingency rather than a expectation.

### 7.5 Q2's plateau is NOT MEASURED, and is reported as absent rather than as a pass

`fieldMinMax` function objects write `postProcessing/housing/housing_T/…` and
`postProcessing/core/core_T/…` every 100 iterations, giving **102-row series**
that make G-PLATEAU directly measurable for **Q1 and Q3**. **There is no
equivalent series for Q2**, which is a patch area-average.

**REGISTERED: Q2 is graded with `plateau_states=None`, and the artifact prints
`Q2 PLATEAU: NOT MEASURED` on its face.** An absent measurement is reported as
absent, never as a pass (`VERIFICATION_CHARTER.md` §9;
`roache_triple.grade_ladder` docstring requires exactly this).

**And no function object is added to fix it.** `T23_PREREGISTRATION.md:534-543`
registers the reason: an inline function object that fails does so at
**construction**, before the first iteration, and takes the whole solve with it.
Buying a plateau series for Q2 at the price of a 121-core-minute fine solve
dying at startup is a bad trade. **This is a registered instrument gap, named
here, and it is a candidate for a later rung.**

---

## 8. COST — `CLAUDE.md` rule 12

### 8.1 The rate, derived from THIS CASE'S OWN log, and from nothing else

> ⚠ **A CELL-RATE IS NOT BORROWED ACROSS A MESH JUMP OR ACROSS A CASE.** This
> family missed by **31.4 %** on T1b L4 doing exactly that, and
> `T23_PREREGISTRATION.md:589-594` had to register the same hazard when it
> borrowed T5's Cartesian anchors. **This rung borrows nothing: the rate is
> derived from `T23_P305_U20`'s own `log.solve` and its own cell count.**

**MEASURED**, from `T23_runs/T23_P305_U20/log.solve`, final line
`ExecutionTime = 1813.14 s  ClockTime = 1814 s`, at `endTime` 10,000,
**1 rank**, **39,680 cells**:

    rate = 1813.14 s / (39,680 cells x 10,000 iterations)
         = 4.56941e-06 s per cell-iteration          [MEASURED, this geometry,
                                                      this solver, this rank count]

**A contention reading, MEASURED rather than assumed:** `ExecutionTime`
(1813.14 s CPU) and `ClockTime` (1814 s wall) agree to **0.05 %**, so this
process held a full core for its entire run despite three sibling T23 cases
running alongside it on 16 vCPUs. **The anchor is not a contended figure**, and
contention is therefore **not** a named upward risk for this rung — T23G plans
**three** concurrent single-rank cases, which is *less* concurrency than the
anchor already survived.

### 8.2 POINT and HARD CAP, per level and total

Scaling by cell-iterations at the measured rate:

| level | cells | cell-iterations | derived wall s | **POINT core-min** | `timeout` s | **HARD CAP core-min** | cap / point |
|---|---:|---:|---:|---:|---:|---:|---:|
| `T23G_C` | 9,920 | 9.920e07 | 453.3 | **7.56** | 1,500 | **25.0** | 3.31× |
| `T23G_M` | 39,680 | 3.9680e08 | 1,813.1 | **30.22** | 6,000 | **100.0** | 3.31× |
| `T23G_F` | 158,720 | 1.5872e09 | 7,252.6 | **120.88** | 24,000 | **400.0** | 3.31× |
| **TOTAL** | | | | **158.65** | | **525.0** | 3.31× |

| figure | value | tag |
|---|---:|---|
| **TOTAL POINT** | **158.65 core-min** | **DERIVED** from the measured rate in §8.1 |
| **TOTAL HARD CAP** | **525.0 core-min** | **REGISTERED**, hard, enacted as `timeout` |
| USD at POINT | **$0.1356** | **DERIVED, NOT MEASURED** |
| USD at CAP | **$0.4489** | **DERIVED, NOT MEASURED** |

USD at the owner-stated **c7a.4xlarge $0.0513/core-h** (**REPORTED-BY-OWNER**,
2026-08-21/22). **The box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5), so **no dollar figure in this document is
measured.** Both are far under the $25 pre-authorisation — **and a blanket
authorisation is not a per-item reading** (`CLAUDE.md` rule 9), which is why the
cost is registered per level rather than waved through.

**`T23G_M`'s cap of 100.0 core-min is not an estimate.** It is the cap
`run_t23.sh:24` already enacted on this exact mesh, under which it completed in
1,813 s. That level's cap is **measured-backed**; the other two are derived.

### 8.3 ⚠ THE NAMED MISPREDICTION RISK, sized rather than gestured at

**The rate in §8.1 is measured at 39,680 cells and is applied at 9,920 and
158,720. That extrapolation across a 4× and a 16× mesh jump is THE named
misprediction risk of this rung.** The mechanism: `p_rgh` uses GAMG (near-linear
in N, but gaining a multigrid level); `h`, `k`, `omega` use DILUPBiCGStab, whose
iteration count grows with the condition number as the mesh refines. **Cost is
therefore expected to scale as `N^α` with `α > 1`, not `α = 1`.**

**Sized, at `α = 1.3` (`4^1.3 = 6.063` instead of 4.000):**

| level | POINT at α = 1.0 | stressed at α = 1.3 | its CAP | headroom at α = 1.3 |
|---|---:|---:|---:|---:|
| `T23G_C` | 7.56 | **4.98** | 25.0 | 5.02× |
| `T23G_M` | 30.22 | 30.22 (anchor) | 100.0 | 3.31× |
| `T23G_F` | 120.88 | **183.22** | 400.0 | **2.18×** |
| **TOTAL** | 158.65 | **218.42** | 525.0 | **2.40×** |

**The caps are sized for the asymmetry**, not for symmetric error: the risk is
one-sided (superlinear scaling makes the coarse level *cheaper* and the fine
level *dearer*), and the fine level's cap absorbs `α = 1.3` with 2.18× to spare.

**AN OVERRUN STOPS THE RUN. IT DOES NOT GET A NEW BUDGET.** The cap is
**ENACTED, not merely written**: `timeout <TIMEOUT_S>s` at 1 rank inside the
launcher, `cap_core_min = TIMEOUT_S × RANKS / 60`. A queue runner's
`CAP_OVERRUN.txt` only *reports*; the wrapper's own `timeout` is what stops the
run, as rule 12 requires. **A capped level is `capped=1` in its STATUS, fails
rule 4's `End`-line clause, and its quantity is NOT A RESULT — it is not
restarted with a bigger number.**

### 8.4 Ranks, and the wall-clock consequence

**REGISTERED: `nProcs = 1` per level**, this family's precedent
(`run_t23.sh:20`, `RANKS=1`). **The three levels run concurrently** — three
single-rank processes on a 16-vCPU box — which is legitimate parallel batching
and not a rank claim: `core-min = wall_s × 1 / 60` for each level independently,
and the total is their sum.

**Wall clock, stated plainly because "tonight" was the instruction:** the wall
is set by `T23G_F` alone. **≈ 2.0 h at POINT; up to 6.7 h at its cap.** The
coarse and medium levels finish inside the first half hour. **At POINT this
lands tonight. At the cap it does not**, and that is registered here rather
than discovered at 08:00Z.

### 8.5 Build compute, registered separately

`blockMesh` + `splitMeshRegions` + `checkMesh` × 3 regions × 3 levels.
**POINT 1.0 core-min, CAP 5.0 core-min**, derived from the source case's own
`log.blockMesh` and `log.splitMeshRegions` (both complete in seconds at 39,680
cells; the fine level is 4× that). **This is compute under this registration**
(`VERIFICATION_CHARTER.md` §2d.2: gates close at first compute, **feasibility
compute included**), so it is costed here and it is **not** run before this
document is committed.

### 8.6 The cost-calibration row, registered in the form the comparison will need

Rule 12 requires estimate-versus-actual at every process completion, landing in
`docs/COST_CALIBRATION.md`. **REGISTERED NOW, so the comparison has a frozen
predicted column to compare against:**

| field | value at registration |
|---|---|
| `item` | `T23G` grid triple, (305 W, 20 m/s) |
| `predicted_core_min` | **158.65** total — **7.56** / **30.22** / **120.88** per level |
| `predicted_basis` | **DERIVED** from `T23_P305_U20/log.solve` `ExecutionTime = 1813.14 s` at 39,680 cells, 10,000 iterations, 1 rank; **rate 4.56941e-06 s/cell-iteration**; scaled **linearly in cell-iterations (α = 1.0)** |
| `cap_core_min` | **525.0** total — **25.0** / **100.0** / **400.0** |
| `named_misprediction_risk` | **superlinear linear-solver scaling across a 4× and a 16× mesh jump**; sized at α = 1.3 in §8.3 |
| `actual_core_min` | **PENDING** — from each level's own `STATUS.<case>` `core_min`, gross, with any stall (> 3600 wall s beyond its POINT) named as **waste** and reported separately, never absorbed into the ratio |
| `ratio` | **PENDING** — actual / predicted, per level and total |
| `usd` | **DERIVED, NOT MEASURED**, at $0.0513/core-h, REPORTED-BY-OWNER |

---

## 9. HONEST CEILINGS — what this rung can and cannot earn, registered before it runs

> ### ⚠ A GRID TRIPLE IS CODE-AND-GRID CONVERGENCE EVIDENCE. IT IS NOT A
> ### VALIDATION AGAINST A PHYSICAL EXPERIMENT.

Under `THERMAL_TIERING_DIRECTIVE.md`, verdict and tier are two vocabularies and
are never conflated. **Registered now, so nobody over-reads a PASS later:**

**This rung CAN move the G column** for the T23 map's (305 W, 20 m/s) point —
and only if every level is iteratively converged and plateaued **and** the
finest triple is `CONVERGING`. `§3.1` of that directive is explicit: a row whose
triple is not `CONVERGING`, or any one of whose levels did not plateau, **cannot
hold G**, whatever its deviation.

**This rung CANNOT move the P column, and no result of it may be read as doing
so.** There is no primary experimental source for this geometry.
`T23_PREREGISTRATION.md:503-513` already records the correlation tier as
deferred for want of a title-page-verified paper (`CLAUDE.md` rule 15) that this
lab does not hold for annular flow. **A perfectly converged grid ladder on a
wrong model converges perfectly to the wrong answer**, and this rung has no
instrument that could tell.

**This rung does not move V beyond what T23 already holds.**

**What a PASS here means, in one sentence, for anyone quoting it:** *the
answer is no longer changing appreciably with mesh density at this operating
point* — **not** *the answer is right.*

**Specific over-readings that are refused in advance:**

- A PASS does **not** validate the 200 °C margin against any experiment; it
  bounds the *discretisation* contribution to that margin and nothing else.
- A PASS on **G-GCI-LEGACY** does **not** license 0.1 °C (§5.2).
- The result belongs to **(305 W, 20 m/s) only.** The other fifteen points of
  the T23 map inherit **nothing** from it. An order or a GCI quoted from this
  rung beside another operating point is a category error, and Act A may not
  print one.
- Radiation remains **OFF** — a disclosed omission inherited from
  `T23_PREREGISTRATION.md` §1 line 1, untouched by any grid claim.

---

## 10. ⚠ FULL DISCLOSURE: THE MEDIUM LEVEL'S ANSWER IS ALREADY ON DISK, AND I HAVE READ IT

**The MEDIUM level is the same mesh as the already-solved `T23_P305_U20`.** One
of the three values in this ladder is therefore knowable today, and I have read
it. **Concealing that would be worse than the fact itself, so it is quoted here
in the frozen document:**

| quantity | medium-level value, **MEASURED**, from `T23_runs/T23_P305_U20/postProcessing/…/fieldMinMax.dat` row `10000` |
|---|---|
| **Q1** — `max(T)` housing | **342.1749743329 K** = ΔT **54.1749743329 K** = **68.9750 °C** |
| **Q3** — `max(T)` core | **346.2656409141 K** = ΔT **58.2656409141 K** = **73.1156 °C** |
| **Q2** — interface area-average | not computed here; it is an area-weighted average of the same file's `housing_to_fluid` patch and is **equally knowable today**. The disclosure covers it either way. |

**Why this does not compromise the freeze, stated as an argument that can be
attacked rather than as a reassurance:** rule 2 protects one property — that the
gate could not have been chosen to fit **the answer**. The answer of this rung
is the triple: the **observed order**, the **GCI**, and the **fine value**. All
three are functions of all three levels, and **two of the three levels do not
exist**. `p` depends on `e32/e21`; one value out of three constrains neither.

**What the medium value IS used for, openly:** it is the reference for
**G-REPRO** (§5.1), which requires the fresh `T23G_M` run to reproduce
342.1749743329 K to **1e-6 K**. That is a determinism control with a real
failure mode — a build that differs in mesh, boundary condition or source term
will miss it — and it is registered rather than smuggled in.

**And the medium level is RE-RUN rather than reused**, at a cost of 30.22
core-min, so that all three levels are produced by one launcher, under one
registration, with one age guard, on one day. The 30 core-min buys the
reproducibility check and the provenance; it is not saved.

---

## 11. THE §2b CONDITION — CHECKED, NOT ASSERTED

`VERIFICATION_CHARTER.md` §2b requires that a pre-registration state the
no-answer-to-tune-to condition **and how it was checked** — *"name the run
directory that does not exist."*

**Named, and checked at the moment of commit** —
`/home/ubuntu/Certonomous/verification/runs/T-family/T23G_runs/`:

**The directory exists and holds exactly one file, `analyse_t23g.py`, the
comparator being frozen by this same commit.** The run directories named in §12
— `T23G_C/`, `T23G_M/`, `T23G_F/` — **do not exist.** There is no
`blockMeshDict`, no `log.blockMesh`, no `log.splitMeshRegions`, no
`log.checkMesh.*`, no `log.solve`, no time directory, no `postProcessing/`, no
`STATUS.` and no `DONE.` file anywhere under a `T23G` name. The identifier
`T23G` appeared **nowhere** in `docs/` or `verification/` before this commit —
checked by search, not assumed.

**No compute of any kind, feasibility or build included, has occurred under this
registration** (`§2d.2`: gates close at first compute, feasibility compute
included). §8.5 costs `blockMesh` as compute under this registration precisely
so that it cannot be run as a free action before the freeze.

**The grading path is fixed at this commit.** Three files carry it, and all
three are hashed against their committed blobs before any grading:

| file | role |
|---|---|
| `verification/runs/T-family/T23G_runs/analyse_t23g.py` | **the comparator**, frozen here |
| `scripts/roache_triple.py` | rule 5's machinery, `PLANT`, `FS = 1.25` — **imported, never reimplemented** |
| `verification/runs/T-family/T23_runs/analyse_t23.py` | the **imported** field-parsing and reader path (`internal_window`, `patch_value_window`, `patch_face_areas`) |

**The third entry is a coupling and is declared as one:** the comparator imports
a module that lives in a sibling rung's directory, so a later edit to
`analyse_t23.py` would silently change this rung's grading path.
**REGISTERED: `analyse_t23g.py` records all three shas at grade time and the
record carries them**, so a divergence is visible rather than silent. The
coupling is accepted deliberately — it means this rung reads Q1 and Q2 through
**the same proven parsing path Act A's numbers already come from**, rather than
through a second implementation that could drift from it.

---

## 12. OUTPUTS

Under `verification/runs/T-family/T23G_runs/` — **never beside this prose**
(`FILING_CHARTER.md`; `scripts/check_filing.py` governs):

- `T23G_C/`, `T23G_M/`, `T23G_F/` — the three cases, each with its own
  `log.blockMesh`, `log.splitMeshRegions`, `log.checkMesh.{fluid,housing,core}`,
  `log.solve`, `log.yPlus.fluid`, `STATUS.<case>` and `DONE.<case>`
- `T23G_GRADE.txt` — the graded record: per quantity, the three level values,
  **every** triple, **every** order, the state, the GCI at Fs = 1.25 with
  `GCI_abs` in K beside `GCI_pct`, **both** Richardson forms with the sign
  disclosure, the nine planted-zero controls with their measured floors, the
  per-level residuals and `max|Ux|/max|Uz|`, the per-level y+, and the verdict
- `T23G_GRADE.json` — the same, machine-readable, with the three grading-path
  shas
- A row in `docs/COST_CALIBRATION.md` per §8.6, at completion

**Verdicts use the fixed vocabulary and nothing else:** `PASS` / `GATE REACHED` /
`GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`.

---

## 13. WHAT THIS DOCUMENT DOES NOT DO

**It does not launch anything.** `SUPERVISION_CHARTER.md` §3 reserves to the
heat-transfer supervisor personally (a) the confirmation that this
pre-registration is **committed** before compute and (b) the **diff read of the
comparator, read as a diff**. Neither is delegable and neither has happened at
the moment this is written.

**No mesh has been built.** §8.5 registers `blockMesh` as compute under this
registration, and `§2d.2` closes gates at first compute. Building before the
comparator's diff read would close the gates on a comparator the supervisor has
not yet accepted, and a repair after that point needs the four-condition `§2d.1`
exception. **The order is: commit → diff read → mesh → launch.**

---

*End of registration. Frozen on commit.*
