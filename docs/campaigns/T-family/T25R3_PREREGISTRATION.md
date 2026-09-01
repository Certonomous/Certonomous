# T25R3 — 8-cell aviation battery module, resolved cooling channels, transient conjugate: **THE CONVERGENCE RUNG**. PRE-REGISTRATION

**Drafted 2026-09-01T~16:20Z by a heat-transfer `lab-lane`. NOTHING HAS BEEN
RUN. NO SOLVER HAS BEEN LAUNCHED.**

**AUTHORITY.** Sanaa's directive of 2026-09-01 ~15:45Z, captured verbatim at
`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`,
committed at **`f4c8e466`**. Her header, verbatim: *"Cost is not a constraint.
Every gated case runs its grid convergence study automatically; a case without
one is not a result."* Her §0 (the automatic convergence study) and her §2
(battery module) govern this document. Her §7 orders the fix run **now** and
overrides the standing board entry that halted the T25R2 successor.

**THIS DOCUMENT SUPERSEDES `docs/campaigns/T-family/T25R2_PREREGISTRATION.md`
(frozen at `bb6e5761`). THAT DOCUMENT IS NOT EDITED AND NOT STRUCK.** It remains
on disk intact, with its Amendment A1 and Addenda B1/B2/B3, as the frozen record
of the rung that produced the `GATE FAIL`. `CLAUDE.md` rule 6 forbids editing a
frozen file; a successor freezes its own.

**WHY IT IS SUPERSEDED.** T25R2's §3.5 outer-loop gate returned **`GATE FAIL` on
O3**: the coolant-outlet area-mean temperature moved **2.315190e-02 K** at
t = 60 s (and **2.404233e-02 K** at t = 30 s) when the outer sweep count was
doubled from 10 to 20, against a registered threshold of 1.234e-02 K. The solid
passed everywhere (max 1.200e-03 K). The failure is **localised to the 60 s
takeoff pulse and disappears by t = 900 s (2.006354e-03 K)**. Diagnosis, and
Sanaa's, identical: **under-iteration inside each time step during the fast load
change**, at `Co ≈ 1600`, against a source that stepped discontinuously.
`T25R2_RESULTS.md` §13 priced the levers; this rung registers them.

Verdict vocabulary is `CLAUDE.md` rule 1's and is used nowhere loosely.

---

## ⛔ 0. THREE DEPARTURES FROM SANAA'S §2, NAMED BEFORE ANYTHING ELSE

Her §2 has five instructions. **Two are implemented exactly as written. Three
cannot be, and each is named here with the arithmetic or the source line that
decides it.** None is quietly adapted. The supervisor rules on all three before
any compute; until then this rung does not launch.

### 0.1 ⛔ DEPARTURE 1 — `residualControl` **DOES NOT EXIST** on this solver's outer loop

> Her words: *"PIMPLE: nOuterCorrectors 3 -> up to 15 with residualControl on p,
> U, h (1e-7) so each step converges to a fixed tolerance rather than a fixed
> count; momentumPredictor on; nCorrectors 2. ... No fixed-count sweeps
> anywhere."*

**MEASURED FROM SOURCE, READ BY THIS LANE, NOT RELAYED.** At
`/usr/lib/openfoam/openfoam2606/applications/solvers/heatTransfer/chtMultiRegionFoam/`:

- `chtMultiRegionFoam.C:109` is
  `for (int oCorr=0; oCorr<nOuterCorr; ++oCorr)` — a **plain fixed-count C++
  for-loop**. It is not a `pimpleControl`, it has no `criteriaSatisfied`, it
  emits no "converged in"/"not converged within" line, ever.
- `readPIMPLEControls.H` reads **one key only**: `nOuterCorrectors`, from an
  `fvSolution` constructed on the `runTime` (there is no top-level mesh).
- `grep residualControl` over the whole solver directory returns hits **only**
  inside `chtMultiRegionTwoPhaseEulerFoam`, a different application.

> **`nOuterCorrectors` IS A FIXED COUNT BY CONSTRUCTION OF THE SOLVER.
> "No fixed-count sweeps anywhere" IS NOT ACHIEVABLE ON `chtMultiRegionFoam` AT
> v2606 WITHOUT PATCHING THE SOLVER.**

What the solver *does* offer, read at the same time: a `loopControl looping
(runTime, pimple, "energyCoupling")` at `chtMultiRegionFoam.C:210`, which **does**
accept `convergence { "h" <tol>; }`
(`src/finiteVolume/cfdTools/general/solutionControl/loopControl/loopControl.C:97`,
`checkConverged()` reads each region's `solverPerformanceDict` initial
residuals). It is **energy-only**, it fires **only on the first outer corrector**,
and it does not touch pressure or momentum.

**REGISTERED RESPONSE — three parts, and the third is the substantive one:**

1. `nOuterCorrectors 15` — **her number, as a fixed count**, because the solver
   admits nothing else. `momentumPredictor true` and `nCorrectors 2` are
   implemented exactly as she wrote (and were **already** the staged values;
   see §4).
2. The `energyCoupling` loop is **NOT enabled** in this rung. Reason: its cost is
   unbounded-by-construction until measured, and enabling it *simultaneously*
   with the ramp and the 25× finer time step would confound three levers in one
   run. It is named here as the successor's lever, not silently omitted.
3. **The tolerance guarantee she asked for is replaced by a MEASURED
   PREREQUISITE, gate `G-I` (§7.3), which is her own §0.2 rule promoted to a
   gate:** the change in the graded quantity between 15 and 30 outer sweeps must
   be **at least 10× smaller** than the difference between consecutive mesh
   levels. Run `W30` (§2) exists for no other purpose. If `G-I` fails, the
   observed order is noise and **the space ladder is `NOT A RESULT` whatever it
   says** — which is exactly the protection `residualControl` would have given,
   obtained by measurement instead of by a key the solver does not read.

### 0.2 ⛔ DEPARTURE 2 — channel cells **8 / 12 / 18 CANNOT BE BUILT** wall-resolved

> Her words: *"three meshes (channel cells 8/12/18, wall layers scaled)"*, under
> her §0.1 requirement *"Near-wall spacing scales with r; y+ stays under 1 on
> every level where the case is wall-resolved."*

**THE ARITHMETIC.** The channel is a 3.000 mm plane slot, graded symmetrically
about its mid-plane; the first cell height is solved by bisection from the y+
target, never typed (`build_t25R.py:120 channel_grading`). Holding the first
cell **centre** at y+ = 1.000 on the coarsest level (`Re_Dh = 3200`, Blasius
`f_D = 0.042015`, `tau_w = 0.40334 Pa`, `u_tau = 0.57976 m/s`,
`y+ = 38650.4 · y [m]`), the **required per-cell expansion ratio** is:

| her level | cells across gap | half-cells | first cell height | y+ (centre) | **REQUIRED per-cell growth** |
|---|---|---|---|---|---|
| coarse | 8 | 4 | 5.1750e-05 m | 1.000 | **2.6391** |
| middle | 12 | 6 | 3.4500e-05 m | 0.667 | **1.8240** |
| fine | 18 | 9 | 2.3000e-05 m | 0.444 | **1.4669** |

**The registered quality window is `(1, 1.35)` and `build_t25R.py:142` REFUSES
outside it; §2.3 of the predecessor registers ≤ 1.15. ALL THREE OF HER LEVELS
VIOLATE IT, the coarsest by a factor of two.** A 3 mm gap resolved to y+ ≤ 1
with 4 cells per half cannot be done at any defensible growth ratio. Her §0.1
requirement and her §2 cell counts are **mutually exclusive on this geometry**.

Two further facts, each independently decisive:

- **Her finest level would be COARSER than the mesh that produced the failure.**
  The T25R2 baseline runs **24** cells across the gap (measured, counted from
  distinct cell-centre y at x = 0.04875 m on all seven channels;
  `MESH_VERIFICATION.txt`). Grading the successor on an 18-cell channel means
  grading the repair on a mesh less resolved than the one being repaired.
- **Her growth ratios are far less similar than the existing family's.** Her
  spread is 2.6391 → 1.4669 (**80 %**); the existing family's is
  1.1499 → 1.0952 → 1.0615 (**8.5 %**). She cites the F28 similarity lesson by
  name; the family she named is the less similar of the two.

**REGISTERED RESPONSE — the space ladder is 24 / 36 / 54 cells across the gap**,
which is the family `build_t25R.py` already defines as `L1`/`L2`/`L3` and whose
`L1` and `L2` are already staged and `checkMesh`-verified on disk. It satisfies
**every governing requirement in her §0.1**: one parametric script, identical
topology (29 blocks: 8 module + 7 channels × 3 streamwise bands), uniform
refinement, near-wall spacing scaled with r, y+ ≤ 1 on every level. See §3.

### 0.3 ⛔ DEPARTURE 3 — adaptive stepping at `maxCo 0.5` is **infeasible by four orders of magnitude**

> Her words: *"Time step: dt = 0.02 s while t < 70 s, 0.1 s after; or adaptive
> with maxCo 0.5. Pick one, register which and why."*

**PICKED: the fixed two-segment schedule, dt = 0.02 s for t ≤ 70 s and
dt = 0.1 s thereafter — her first option, her exact numbers.** §6.

**WHY NOT THE SECOND.** T25R2 measured `Co ≈ 1600` at dt = 0.5 s. Scaling
linearly, `maxCo 0.5` requires `dt ≈ 1.6e-04 s`, i.e. **≈ 5.8 million steps over
900 s** against the registered 11,800 — a factor of **≈ 490**, or **≈ 31,600
core-minutes for a single L1 run** (22 core-days), before the mesh ladder. It
also **destroys the time ladder**: an adaptively chosen dt is not exactly
halvable, so `dt`, `dt/2`, `dt/4` would not be a Roache triple and no observed
temporal order could be read from it. Both grounds are independently sufficient.

---

## 1. WHAT THIS RUNG IS, AND WHAT NO READER MAY TAKE FROM IT

T25R3 is **the convergence rung**. It exists to answer one question with a
number and a band: **does this case's answer stop moving when the mesh is
refined and when the time step is refined?** Sanaa's §0.5: *"Only then is the
case gradable. The band goes on every number."*

It inherits **no `PASS` from anything**. T25R2 is `NOT A RESULT` on every row, by
its own registered §3.5.4 propagation. T25R is gone. T20 is `NOT A RESULT` on its
own terms. **This rung starts from zero and every number it reports is its own.**

Three levers are changed together relative to T25R2, and the document says so
plainly rather than claiming a controlled experiment: **(a)** the discontinuous
source becomes a 1 s linear ramp at both edges; **(b)** the time step through the
pulse falls from 0.5 s to 0.02 s, a factor of **25**; **(c)** outer sweeps rise
from 10 to 15. **No single-lever attribution may be read from this rung.** What
it can establish is convergence, which is what it is for.

---

## 2. THE REGISTERED RUN SET — **SIX RUNS, NAMED AND CLOSED**

| id | mesh | cells | ladder | dt schedule (s) | steps | `nOuterCorrectors` | purpose |
|---|---|---|---|---|---|---|---|
| **S1** | L1 | 16,608 | space, coarse | 0.02 / 0.1 | 11,800 | 15 | Roache triple, level 1 |
| **S2** | L2 | 37,368 | space, **middle** | 0.02 / 0.1 | 11,800 | 15 | Roache triple, level 2; base of the time ladder |
| **S3** | L3 | 84,078 | space, **finest** | 0.02 / 0.1 | 11,800 | 15 | Roache triple, level 3; **the reported answer** |
| **T2** | L2 | 37,368 | time, dt/2 | 0.01 / 0.05 | 23,600 | 15 | temporal triple, level 2 |
| **T4** | L2 | 37,368 | time, **dt/4** | 0.005 / 0.025 | 47,200 | 15 | temporal triple, level 3 |
| **W30** | L2 | 37,368 | iterative | 0.02 / 0.1 | 11,800 | **30** | `G-I` prerequisite (§7.3) — Sanaa's §0.2 rule as a gate |

**The run set is closed. No seventh run is admitted under this registration.**
`S2` is deliberately the shared member of all three ladders: the space triple is
`S1/S2/S3`, the time triple is `S2/T2/T4`, the iterative pair is `S2/W30`. That
sharing is what makes six runs sufficient.

**No level below L1 and no level above L3 is admitted** — see §3.4 for the
arithmetic that closes both ends.

---

## 3. GEOMETRY, MESH AND THE THREE LEVELS

### 3.1 Geometry — inherited unchanged from T25R2 §2.1, every number frozen there

2-D, unit depth (1.000 m), `front`/`back` `empty`. Eight solid cells
0.100 m × 0.030 m at 0.033 m pitch; seven resolved 3.000 mm air channels between
them; 0.050 m upstream plenum and 0.100 m downstream plenum. Solid volume
0.024 m³ = 8 × 0.003 m³, exact. Inlet area 0.021 m² = 7 × 0.003 × 1.000, exact;
at ρ = 1.2 and U = 8.0 m/s, ṁ = 0.20160 kg/s.

### 3.2 The three levels — **ONE PARAMETRIC SCRIPT, `build_t25R.py`**

Her §0.1 requires three geometrically similar meshes **built from one parametric
script**. `verification/runs/T-family/T25R_MODULE_runs/build_t25R.py` is that
script and it already carries all three levels in its `LEVELS` dict
(`build_t25R.py:46-50`); its `selftest` asserts, for every key, that each level
is **exactly** 3/2 of the level below with no rounding (`build_t25R.py:800`).
**No level is hand-edited. Nothing in the mesh definition changes for T25R3.**

| | L1 | L2 | L3 |
|---|---|---|---|
| `nx_up / nx_mid / nx_dn` | 16 / 40 / 20 | 24 / 60 / 30 | 36 / 90 / 45 |
| cells across each 3 mm gap (`ny_ch`) | **24** | **36** | **54** |
| cells across each 30 mm solid cell | 12 | 18 | 27 |
| fluid cells | 12,768 | 28,728 | 64,638 |
| solid cells | 3,840 | 8,640 | 19,440 |
| **total cells** | **16,608** | **37,368** | **84,078** |
| streamwise dx in the cell zone | 2.5000 mm | 1.6667 mm | 1.1111 mm |
| coupled interface faces, each region | 560 | 840 | 1,260 |
| first cell height at the channel wall | 5.1750e-05 m | 3.4500e-05 m | 2.3000e-05 m |
| **y+ at the first cell centre** (estimated, §3.3) | **1.000** | **0.667** | **0.444** |
| per-cell channel growth ratio | 1.1499 | 1.0952 | 1.0615 |
| block expansion (last/first) | 4.648 | 4.692 | 4.721 |

### 3.3 ⚠ THE REFINEMENT RATIO, AND WHETHER IT MEETS SANAA'S BAND — **STATED PLAINLY**

- **Cell-count ratio: 2.2500 exactly, at both steps** (37,368/16,608 and
  84,078/37,368). Not approximately — exactly.
- **This is a 2-D mesh (one cell in z), so the effective grid refinement ratio is
  `r = (N₂/N₁)^(1/2) = 2.2500^0.5 = 1.5000`, exactly, at both steps.**
- Her §0.1 band is *"uniform refinement ratio r between 1.5 and 2.0 in every
  direction (r = 1.3 is the floor)"*.

> **VERDICT ON THE BAND: `r = 1.5000` IS INSIDE HER BAND — AT ITS LOWER EDGE, and
> well above the 1.3 floor. IT MEETS THE REQUIREMENT AS WRITTEN.**

**AND THE HONEST CAVEAT, which she herself flags:** *"larger r gives a cleaner
observed order."* At r = 1.5 with a formally first-order scheme (§4.2), the
level-to-level difference shrinks by only 1.5× per level, so the observed order
is read off a shorter lever arm than r = 2 would give. **The alternative was
priced and is stated rather than hidden:** a family at r = 2.0 from L1 would be
16,608 → 66,432 → 265,728 cells — **16× L1 at the finest**, ≈ 1,037 core-min for
that single run against 328, and it would require rebuilding the `LEVELS` dict
and re-verifying both meshes already staged. **This lane registers r = 1.5, in
band, and discloses that r = 2.0 would have been cleaner and was not chosen.**

**y+ is ESTIMATED, NOT MEASURED, on this line.** The basis is Blasius on
`Re_Dh = 3200` (`Dh = 2 × 3 mm = 6 mm`, a plane slot), reproduced above.
`Y1_L1 = 5.175e-05 m` was originally solved to put the first cell **centre** at
y+ = 1.000 exactly, and the arithmetic here reproduces 1.0000 to four figures,
which is a check on the inherited constant rather than a new claim.
**Registered obligation: y+ is MEASURED on every level from the run's own wall
shear and reported on the row; the estimate above is never quoted as the
measurement.**

### 3.4 ⚠ BOTH ENDS OF THE LADDER ARE CLOSED BY ARITHMETIC — HER §0.4(c) IS **UNAVAILABLE HERE**

Her §0.4(c): if p lands outside the band, *"add a FOURTH, finer level at the same
r and recompute p on the finest three."* **On this family that is not
constructible, for three independent reasons, all computed before any run:**

L4 = L3 × 1.5 gives `nx_up 54` ✓, `nx_mid 135` ✓, but
**`nx_dn = 67.5` — NOT AN INTEGER**, **`ny_cell = 40.5` — NOT AN INTEGER**, and
**`ny_ch = 81` — ODD**, which `build_t25R.py:128` refuses outright because the
channel is graded symmetrically about its mid-plane and needs an even count.

A level **below** L1 is equally impossible: L1 ÷ 1.5 gives `nx_up = 10.67`,
`nx_mid = 26.67`, `nx_dn = 13.33`, `ny_cell = 8` — three non-integers.

> **REGISTERED CONSEQUENCE: if the observed order lands outside its band, the
> escalations available under this registration are her §0.4(a) (tighten
> iterative convergence and re-read) and §0.4(b) (verify similarity). §0.4(c),
> the fourth level, is `BLOCKED` on this family and becomes a successor rung that
> rebuilds the whole family from a base divisible by 3 twice.** A candidate base
> that works is `(nx_up, nx_mid, nx_dn, ny_ch, ny_cell) = (8, 24, 16, 16, 8)`,
> giving four integer levels with `ny_ch` even throughout: 16 → 24 → 36 → 54.
> **It is priced nowhere and registered nowhere. It is not this rung.**

### 3.5 What is reusable and what must be built

| artifact | state | action |
|---|---|---|
| L1 mesh (`T25R2_L1`, `T25R2_L1_OC20`) | staged, `checkMesh` OK, `maxNonOrth 0`, `maxSkew 6.7e-14`, 24 cells/gap **counted** | **reusable as a mesh source**; `0.orig`, `constant`, `system` are **re-derived**, not copied (loads and dt change) |
| L2 mesh (`T25R2_L2`, `T25R2_L2_DT025`) | staged, `checkMesh` OK, `maxSkew 2.9e-13`, 36 cells/gap **counted**, **never launched** | **reusable as a mesh source**, same terms |
| **L3 mesh** | **DOES NOT EXIST** | **must be built** from `build_t25R.py` at `T25R_LEVEL=L3`; 84,078 cells and 1,260 interface faces per region are registered assertions |
| `run_one_t25R2.sh`, `mark_done_t25R2.py`, `report_completion_t25R2.py` | serial, single-leg | **must be rebuilt** for 2 ranks and the two-leg schedule (§6.3, §9) |
| `analyse_t25R2.py` | frozen with T25R2, carries the §10 reader defect | **must be rebuilt** under this freeze; the defect is a MUST-FIX (§10.2) |
| `verify_mesh_t25R2.py` | measures cells, gap resolution, interface faces, dt/ramp compatibility | **reusable pattern**; extended to L3 and to the two-leg schedule |

**The T25R2 case directories are NOT deleted and NOT reused in place.** T25R3
stages its own tree under `verification/runs/T-family/T25R3_MODULE_runs/`.

---

## 4. NUMERICS

### 4.1 What changes and what does not

| key | T25R2 | **T25R3** | why |
|---|---|---|---|
| `nOuterCorrectors` (top-level `PIMPLE`) | 10 | **15** | Sanaa §2 |
| `momentumPredictor` (coolant) | `true` | **`true`** | Sanaa §2 — **already the staged value** |
| `nCorrectors` (coolant) | 2 | **2** | Sanaa §2 — **already the staged value** |
| `nNonOrthogonalCorrectors` | 0 | 0 | `maxNonOrth` is **0** on every level; a corrector would be inert |
| `residualControl` | absent | **absent — IMPOSSIBLE, §0.1** | `chtMultiRegionFoam.C:109` |
| `p_rgh` solver tolerance | 1e-08 | 1e-08 | T25R2 measured 36,000 GAMG solves, 65,949 iterations, mean 1.83, **zero at `maxIter`** — the stall is gone and the tolerance is what removed it |
| relaxation, **all five `Final` keys written LITERALLY** | `p_rgh`/`p_rghFinal` 0.3; `U`,`h`,`k`,`omega` and their `Final` 0.7 | **unchanged** | this block is the fix for the T25R_L1 divergence; a quoted regex is **refused** by the comparator because `"(U\|h\|k\|omega)"` matched in full and **did not match `UFinal`** — the exact defect that crashed T25R_L1 |
| `adjustTimeStep` | `no` | **`no`** | §6 |
| `writePrecision` / `timePrecision` | 12 / 12 | **12 / 12** | at T ≈ 293 K the default 6 leaves a ~1 mK write quantum, larger than the signals gated here |
| `runTimeModifiable` | `false` | `false` | reproducibility |

### 4.2 ⚠ THE FORMAL ORDER OF THE SCHEMES IS **ONE**, NOT TWO — AND THE ACCEPTANCE BAND FOLLOWS FROM IT

Read from the staged `system/coolant/fvSchemes` and `system/module/fvSchemes`
before this document was written:

- `ddtSchemes { default Euler; }` on **both** regions → **formal temporal order 1**.
- `divSchemes` on the coolant: `div(phi,U)`, `div(phi,K)`, **`div(phi,h)`**,
  `div(phi,k)`, `div(phi,omega)`, `div(phi,Ekp)` are all
  **`bounded Gauss upwind`** → **formal spatial order 1** on every advected
  scalar, including enthalpy.

Sanaa's §0.3 acceptance is *"p within 0.5 of **the scheme's formal order**
(second order: p in 1.5 to 2.5)"*. She gives the rule and one worked example.
**The rule applied to the schemes that will actually run gives:**

> **REGISTERED ACCEPTANCE BANDS: `p_space ∈ [0.5, 1.5]` and
> `p_time ∈ [0.5, 1.5]`. NOT [1.5, 2.5].**

**Registering [1.5, 2.5] against a first-order scheme would have made the gate
unpassable by construction and would have burned the whole spend.** The schemes
are **not** upgraded to second order in this rung: upwind was chosen for
boundedness at `Co ≫ 1` and T25R's divergence history is the reason; a TVD
limiter would put the formal order between 1 and 2 and make the acceptance band
itself ambiguous. **The first-order spatial error is a registered accuracy cost
and the GCI band is what quantifies it — which is the point of this rung.**

### 4.3 Courant number — REPORTED, never controlled

`Co` is reported per level from the solver's own output and gates nothing.
Indicative, from `U ≈ 8 m/s` and the streamwise dx of §3.2: base dt gives
`Co ≈ 64` (L1) to `Co ≈ 144` (L3), against T25R2's ≈ 1600 — a **25× reduction**
from the time step alone. `chtMultiRegionFoam` is implicit; `max Co = 1` is a
choice, not a stability requirement, and it is not made here (§0.3).

### 4.4 Turbulence and thermophysics — inherited unchanged

RAS `kOmegaSST` on the coolant (`constant/coolant/turbulenceProperties`), so the
second turbulence field is **`omega`, not `epsilon`** — see §9.2. Solid heat
conduction on the module. Air: ρ 1.2, cp 1005, k 0.026 (Pr **derived** so k is
exactly 0.026), μ 1.8e-5. Solid: ρ 2500, cp 1000, k 3.0 isotropic. Inlet
turbulence intensity 0.05.

---

## 5. THE HEAT LOAD — **THE 1 s RAMPS, AND THEIR EXACT ENERGY**

### 5.1 The registered source

Sanaa's §2: *"Ramp the load: replace the step at t = 0 and t = 60 s with a 1 s
linear ramp (a discontinuous source destroys time accuracy at the jump)"* and
*"Loads: volumetric, as ruled (1e5 W/m3 pulse, 2.5e4 W/m3 cruise)."*

`constant/module/fvOptions`, `scalarSemiImplicitSource`, `volumeMode specific`
(so the values are W/m³ — the wrong mode is a silent scale error by exactly the
zone volume), `sources { h { explicit table (...); implicit none; } }`,
`Function1 table` with its default `linear` interpolation:

```
(  0.000        0.0)
(  1.000   100000.0)
( 60.000   100000.0)
( 61.000    25000.0)
(900.000    25000.0)
```

**THE VOLUMETRIC RATE IS THE REGISTERED QUANTITY. A PER-CELL WATTAGE IS NOT AN
INPUT ANYWHERE IN THIS RUNG** (Sanaa's 2026-09-01 04:20Z ruling, inherited).

### 5.2 The exact energy, computed before the run

Trapezoidal integration of the table above, which is exact for a piecewise-linear
Function1:

| quantity | **T25R3, ramped** | T25R2, stepped | difference |
|---|---|---|---|
| ∫ q‴ dt over 0–900 s | **2.698750e+07 J/m³** | 2.700000e+07 J/m³ | −1.250e+04 |
| adiabatic bound on the 900 s rise, `∫q‴dt/(ρc_p)` | **10.7950 K** | 10.8000 K | −0.0050 K |
| ∫ q‴ dt over 0–60 s | **5.950000e+06 J/m³** | 6.000000e+06 J/m³ | −5.000e+04 |
| adiabatic bound on the pulse rise | **2.3800 K** | 2.4000 K | −0.0200 K |
| total energy generated, × 0.024 m³ | **647,700 J** | 648,000 J | −300 J |

**The two ramps cost exactly 0.0050 K of adiabatic bound and exactly 300 J.**
That is registered so the §7.5 energy ledger closes against the ramped figure and
not the stepped one — a 300 J error hidden inside a 2 % residual gate would look
like physics.

**Sanaa's ruling on the answer is binding and inherited verbatim:** *"The
temperature rise is then whatever the physics gives... If the result is 8 K, 8 K
is the answer."* **Nothing is tuned toward a target.**

### 5.3 The registered breakpoint condition — **CHECKED, NOT ASSERTED**

Every breakpoint of the table (1.000, 60.000, 61.000 s), the schedule breakpoint
(70.000 s) and the write interval (5.000 s) is an **exact integer multiple of
every registered time step** in both ladders — verified by computation for all
six values of dt ∈ {0.02, 0.01, 0.005, 0.1, 0.05, 0.025}:

| dt (s) | 1 s | 60 s | 61 s | 70 s | 5 s |
|---|---|---|---|---|---|
| 0.02 / 0.01 / 0.005 | 50 / 100 / 200 | 3000 / 6000 / 12000 | 3050 / 6100 / 12200 | 3500 / 7000 / 14000 | 250 / 500 / 1000 |
| 0.1 / 0.05 / 0.025 | — | — | — | 700 / 1400 / 2800 | 50 / 100 / 200 |

> **NO TIME STEP AT ANY LADDER LEVEL LANDS STRICTLY INSIDE EITHER RAMP'S
> INTERIOR WITHOUT ALSO LANDING ON BOTH ITS ENDS.** The coarsest schedule
> resolves each 1 s ramp with **50** steps; the finest with **200**. T25R2's
> 1 ms ramp at deltaT 0.5 was resolved with **zero**.

---

## 6. THE TIME STEP — SCHEDULE, IMPLEMENTATION, AND WHY THIS IMPLEMENTATION

### 6.1 The registered schedule — Sanaa's first option, her exact numbers

| ladder level | t ∈ [0, 70] s | t ∈ (70, 900] s | steps (leg A + leg B) |
|---|---|---|---|
| **base** (S1, S2, S3, W30) | **0.02** | **0.1** | 3,500 + 8,300 = **11,800** |
| **dt/2** (T2) | 0.01 | 0.05 | 7,000 + 16,600 = **23,600** |
| **dt/4** (T4) | 0.005 | 0.025 | 14,000 + 33,200 = **47,200** |

The temporal refinement ratio is **r_t = 2 exactly** at both steps. **The entire
load transient — both ramps and the whole 60 s pulse — lives inside leg A at the
fine step; leg B is pure thermal soak** against a lumped `τ ≈ 696 s`.

### 6.2 ⚠ THE FLOATING-POINT WRITE-TIME QUESTION, SETTLED AT SOURCE BEFORE REGISTERING

0.02 s is not a binary-exact fraction, and a drifted write index would produce a
time directory named `5.02` instead of `5`, breaking both the comparator's time
lookups and rule 4's `last time == endTime` clause — a whole-spend-loses failure
mode. **It was checked at source rather than assumed:**

- `src/OpenFOAM/db/Time/Time.C:1117-1124`: the write index for `wcRunTime` is
  `label(((value() - startTime_) + 0.5*deltaT_)/writeInterval_)`. **The
  `+ 0.5·deltaT_` guard makes the write index immune to accumulated drift of
  order 1e-13.**
- Time-directory naming uses `timeFormat general` at `timePrecision 12`.
  Accumulated drift to t = 900 is of order 1e-11 s against a 12-significant-digit
  resolution of 1e-09 s at that magnitude — **two orders of margin.**

> **REGISTERED FINDING: dt = 0.02 s with `writeInterval 5` is SAFE at v2606, and
> the reason is a source line, not a habit.** A binary-exact departure
> (dt = 1/64 and 1/8) was drafted and is **not** registered, because it would
> have been a departure from her numbers bought with nothing.

### 6.3 ⚠ IMPLEMENTATION — **TWO CHAINED INVOCATIONS**, and the one-invocation route is REFUSED with its reason

`chtMultiRegionFoam` reads one scalar `deltaT` from `controlDict` and, with
`adjustTimeStep no`, never changes it. A two-segment schedule therefore needs
either an override or a restart. **Both were investigated at source.**

**REFUSED — the `setTimeStep` function object.** It exists
(`src/functionObjects/utilities/setTimeStep/`), it takes a `Function1<scalar>`,
and its hook `functionObjects_.adjustTimeStep()` is genuinely called **last**
inside `Time::adjustDeltaT()` (`Time.C:143`), so it would win against
`setMultiRegionDeltaT.H`. **It is refused anyway**, because it requires
`adjustTimeStep true`, which activates the solver's Courant/diffusion control
(`chtMultiRegionFoam/include/setMultiRegionDeltaT.H`) whose interaction with the
FO on the **first** step (`setInitialMultiRegionDeltaT.H`) cannot be established
without running the solver.

> **THE PRINCIPLE THAT DECIDES IT: a time-step schedule that can only be verified
> from a log line AFTER the solver ran cannot be pre-registered as an INPUT.**
> Under the restart, dt is a literal scalar in a `controlDict` that a supervisor
> reads as a diff before compute. That is the whole evidentiary content of rule 2.

**REGISTERED — two chained invocations per run:**

- **Leg A:** `startFrom startTime; startTime 0; endTime 70; deltaT <fine>;
  adjustTimeStep no;`
- **Leg B:** `startFrom latestTime; endTime 900; deltaT <coarse>;
  adjustTimeStep no;`

**DISCLOSED CONSEQUENCE — the restart is not bit-continuous.** Leg B reads leg
A's ASCII fields at `writePrecision 12`, so the restart truncates at ~12
significant figures: on T ≈ 293 K the write quantum is **≈ 3e-10 K**, which is
**≈ 3.3e8 times smaller than the registered tolerance** of §7.2 and **≈ 4.1e6
times smaller** than the reported second tier. It applies **identically to all
six runs**, so it cannot contaminate either observed order. It is stated because
it is real, not because it matters.

**DISCLOSED CONSEQUENCE — rule 4's launch guard applies to LEG A ONLY.** The
guard refuses a case where `0` or a time directory already exists; at leg B's
launch, time directories exist **by design**. Registering that exception here,
before compute, is the difference between a designed restart and a defeated
guard.

**DISCLOSED CONSEQUENCE — function-object output splits.** Leg B writes into
`postProcessing/<fo>/70/`. The comparator reads **both** directories and
**REFUSES** if either is missing or if their union does not cover [0, 900]
without a gap.

---

## 7. THE GATES — GRADED QUANTITIES, TOLERANCE, AND ACCEPTANCE

### 7.1 The graded quantities

Sanaa's §2 gate: *"the outlet temperature history and per-cell peaks change by
less than the registered tolerance between the two finest levels of each
ladder."* Registered as two quantities, both comparable across meshes because
both are **integrals over fixed physical regions**, never single-cell samples:

- **Q1 — the outlet temperature history.** The area-mean `T` on the coolant
  `outlet` patch, at **every one of the 181 written times** (t = 0, 5, …, 900).
  **This is T25R2's O3 given O1's full coverage**, which `T25R2_RESULTS.md` §11
  identified as its own registered gate's blind spot: the worst outlet delta
  (2.404e-02 K at t = 30 s) fell **outside** O3's two registered instants.
  **That limitation is repaired here, in the successor, before the answer
  exists.**
- **Q2 — the per-cell peaks.** For each of the eight solid cells, the
  **volume-averaged** `T` of its cell zone, and the **peak of that average over
  the 181 written times**. Eight numbers per run.

Also **reported, not gated**: the single-cell maximum `T` in the module, carrying
**the band derived from the smooth order quantity** — Sanaa's §0.4(d), *"A
quantity sampled at a single cell (a max) may need a smoother companion quantity
for the order study; use it for p, apply the band to the reported max, and say
so."* **Said so.**

- **Q0 — the order quantity (smooth).** `E_out` = the time integral over
  0–900 s of `c_p · Σ_outlet(φ_f T_f)` [J per metre of depth], from the existing
  `outlet_hflux` `surfaceFieldValue` function object (`weightedSum` of `T`
  weighted by `phi`, written every time step). It is an integral over the whole
  outlet **and** the whole run — the smoothest quantity this case produces.
  **The observed orders p_space and p_time are computed on Q0 and on Q0 alone.**
  The GCI band from Q0 is applied to Q1 and Q2, and this sentence is the
  disclosure her §0.4(d) requires.

### 7.2 ⚠ THE REGISTERED TOLERANCE — **AND WHY A READER IS ENTITLED TO BE SUSPICIOUS OF IT**

> **τ = 1.00e-01 K (0.1 K), on Q1 and on Q2, on both ladders.**

**Basis, registered before any of the six runs exists:**

- It is **0.93 %** of the registered adiabatic bound on the 900 s rise
  (10.7950 K) and **4.2 %** of the bound on the pulse rise (2.3800 K).
- It is **81×** the comparator's demonstrated resolution
  (`PLANT = 1.234e-03 K`), so a violation **81× smaller than the threshold** is
  still visible to the instrument. The gate is engineering-limited, not
  instrument-limited.
- It is an **engineering** tolerance on a peak-battery-temperature prediction. A
  0.01 K band on such a prediction is below thermocouple resolution and below
  anything a thermal-management decision turns on.

**⚠ THE SUSPICION, STATED BY THE LANE THAT REGISTERED IT.** τ = 0.1 K is
**8.1× looser** than the 1.234e-02 K threshold T25R2 failed. A successor that
loosens the threshold its predecessor failed is exactly the move a reader should
distrust, and no basis paragraph earns a free pass. **Therefore the predecessor's
threshold is ALSO registered here:**

> **SECOND TIER, REPORTED, GATES NOTHING: `1.234e-02 K` (= 10 × PLANT). Every Q1
> and Q2 delta is printed against BOTH tiers, always, whatever the verdict. A
> gate at 0.1 K cannot hide a number that 1.234e-02 K would have caught, because
> that number is printed beside it.**

### 7.3 `G-I` — THE PREREQUISITE GATE (Sanaa's §0.2, promoted)

> Her §0.2: *"the iterative change in the graded quantity must be at least 10x
> smaller than the difference between consecutive mesh levels. If it is not, the
> observed order is noise, not discretisation."*

Registered as a **gate that fires before any order is read**:

| | condition | on failure |
|---|---|---|
| **G-I(space)** | `max_t \|Q1(W30) − Q1(S2)\| ≤ 0.1 × max_t \|Q1(S3) − Q1(S2)\|` **and** the same on Q2 and on Q0 | **the space ladder is `NOT A RESULT`**, whatever p and GCI say |
| **G-I(time)** | `max_t \|Q1(W30) − Q1(S2)\| ≤ 0.1 × max_t \|Q1(T4) − Q1(T2)\|` **and** the same on Q2 and on Q0 | **the time ladder is `NOT A RESULT`** |

**This is the substantive replacement for the `residualControl` the solver does
not have (§0.1).** It is strictly stronger than a residual threshold in one
respect and weaker in another, and both are stated: **stronger**, because it is
expressed in the graded quantity in kelvin rather than in a residual whose
mapping to kelvin is unknown; **weaker**, because it is a two-point comparison at
15 and 30 sweeps and not a proof that 30 is converged.

### 7.4 `G-S` and `G-T` — Sanaa's gate as written

| gate | comparison | condition | verdict |
|---|---|---|---|
| **G-S** | the **two finest mesh levels**, S3 vs S2 | `max over 181 times \|ΔQ1\| ≤ τ` **AND** `max over 8 cells \|ΔQ2\| ≤ τ` | `PASS` / `GATE FAIL` |
| **G-T** | the **two finest time levels**, T4 vs T2 | same two conditions | `PASS` / `GATE FAIL` |

**Both conditions of a gate are required. One failing fails the gate.**

### 7.5 Supporting checks — registered, each gating nothing unless named

| id | check | threshold |
|---|---|---|
| C1 | energy ledger: `\|H_out − H_in − E_gen\| / E_gen` over 0–900 s, against the **ramped** `E_gen = 647,700 J` (§5.2) | ≤ 2 %, **gating** |
| C2 | mass balance: `\|ṁ_out − ṁ_in\| / ṁ_in`, ṁ_in registered 0.20160 kg/s | ≤ 0.1 %, **gating** |
| C3 | outlet area-mean T > inlet T at every written t > 0 | **gating**; requires the §10.2 reader fix |
| C4 | y+ at the first cell centre, measured per level from wall shear | **reported**, band on the row |
| C5 | `Co` per level, from the solver's own output | **reported** |
| C6 | last-sweep initial-residual census per equation per level | **reported, no threshold** (T25R2 established that the T25R calibration is invalid under the relaxed final sweep) |

### 7.6 ⚠ THE PROPAGATION RULE, FROZEN HERE BEFORE ANY COMPUTE

1. **`G-I` fails on a ladder → every row of that ladder is `NOT A RESULT`**,
   value printed beside the reason.
2. **A Roache triple that is not `CONVERGING` → every row of that ladder is
   `NOT A RESULT`** (`CLAUDE.md` rule 5), value, both triples and both orders
   printed beside it.
3. **C1 or C2 fails → the whole rung is `NOT A RESULT`.** A run that does not
   conserve energy or mass has no gradable content.
4. `G-S` or `G-T` failing is a **`GATE FAIL` on that gate**. It does **not**
   propagate to the other ladder and does **not** void Q0's order or GCI — a
   discretisation error too large for τ is a *measurement*, and its size is the
   deliverable.
5. **The gate can only turn a `PASS` or a `GATE FAIL` INTO `NOT A RESULT`, never
   the reverse** (rule 5).

---

## 8. ROACHE TRIPLE GATING AND THE OBSERVED ORDER — `CLAUDE.md` RULE 5, IN FORCE ON BOTH LADDERS

Both ladders are graded by the same machinery, in this order, and **the order is
not negotiable**:

1. **Any level not iteratively converged** — i.e. `G-I` failed on that ladder —
   **→ `NOT A RESULT`.**
2. Classify the triple: `CONVERGING` / `DIVERGENT` / `STAGNANT` / `OSCILLATORY` /
   `EXACT`. **Anything but `CONVERGING` → `NOT A RESULT`**, with the value, both
   triples and both orders printed beside it.
3. `CONVERGING` → observed order `p` on **Q0**, and the **GCI at Fs = 1.25** on
   the finest pair.

| | space ladder | time ladder |
|---|---|---|
| triple | S1, S2, S3 | S2, T2, T4 |
| refinement ratio | **r = 1.5000 exactly** (§3.3) | **r_t = 2 exactly** (§6.1) |
| formal order of the scheme | **1** (`bounded Gauss upwind`, §4.2) | **1** (`Euler`, §4.2) |
| **registered acceptance band** | **p ∈ [0.5, 1.5]** | **p ∈ [0.5, 1.5]** |

**A GCI IS NEVER QUOTED WHEN THE THREE VALUES ARE NOT MONOTONE.** At p = 1 and
r = 1.5 the GCI on the finest pair is `1.25 · |ε| / (1.5 − 1) = 2.5 |ε|`, i.e.
**2.5× the level-to-level difference** — a wide band, and that width is the
honest price of first-order upwind, registered here so no reader is surprised by
it after the fact.

**If p lands outside its band**, her §0.4 escalation applies in her order:
**(a)** re-check iterative convergence on the finest level; **(b)** verify
similarity (cell-count ratios, layer counts, growth ratios — all tabulated in
§3.2 and all re-measured at staging); **(c)** a fourth level — **`BLOCKED`, see
§3.4**, and the reason is arithmetic, not effort.

---

## 9. THE STRICT COMPLETION RULE — `CLAUDE.md` RULE 4, AND ITS FIELD TUPLE

### 9.1 The six conjuncts, per run, evaluated over BOTH LEGS

A run is `DONE` only if **all** of the following hold. **Any one failing means
the run is not done; there is no partial completion.**

1. **`rc = 0` on BOTH legs**, recorded not inferred, from the detached wrapper's
   own captured rc (`setsid timeout cmd` exits 0 for every outcome — the rc is
   captured **inside** the wrapper, never around the `setsid` line).
2. **Exactly one `End` line in EACH leg's log**, and **zero `FOAM FATAL`** in
   either.
3. **Last written time == 900**, and leg A's last written time == 70.
4. **Fields present at t = 900 in both regions** — the tuple of §9.2.
5. **`ExecutionTime` line count == the registered step count PER LEG**: leg A
   3,500 / 7,000 / 14,000 and leg B 8,300 / 16,600 / 33,200 as registered in
   §6.1. This is a **step-count identity, not a time-value identity**.
6. **THE AGE GUARD: every field file at every written time, in both regions and
   across both legs, is NEWER than the case's own `0/module/T`**, which is
   touched last at leg A's launch and therefore dates the run allowed to produce
   the answer. **Fields older than the reference: NONE.** The tightest margin
   over all 181 times and both regions is reported on the row.

**The launch guard** — refusing a case where `0` or a time directory already
exists — **applies to LEG A only, by the registration of §6.3.**

### 9.2 ⚠ THE FIELD TUPLE — **GET THIS WRONG AND THE WHOLE SPEND PRODUCES NOTHING**

The solver is **`chtMultiRegionFoam` at OpenFOAM v2606**, RAS `kOmegaSST` on the
fluid region, solid heat conduction on the solid region.

| region | type | **REGISTERED FIELD TUPLE at every written time** |
|---|---|---|
| `module` | solid | **`T`, `p`** |
| `coolant` | fluid | **`T`, `U`, `p`, `p_rgh`, `alphat`, `nut`, `k`, `omega`** |

**Measured, not assumed:** this is exactly the set `T25R2_L1` wrote at t = 900
and exactly the set present in `0.orig` for each region.

**THREE TRAPS, NAMED, EACH OF WHICH WOULD MAKE RULE 4 UNSATISFIABLE:**

1. **`h` IS NOT A WRITTEN FIELD AND MUST NOT BE REGISTERED AS ONE.**
   `chtMultiRegionFoam` **solves** for enthalpy `h` and **writes** temperature
   `T`. Sanaa's §2 names `h` as a residual-control target, which is a *solved*
   variable, not a *written* one. **Registering `h` in the completion tuple would
   make conjunct 4 unsatisfiable forever, on every run, and the entire 1,976
   core-minutes would produce nothing.** This is precisely the K0d defect —
   registering `omega` against a solver that writes `epsilon` — with the roles
   swapped.
2. **The turbulence field is `omega`, NOT `epsilon`**, because the model is
   `kOmegaSST` (`constant/coolant/turbulenceProperties`, read).
3. **`p_rgh` is present and `p` is present, and they are different fields.** A
   conjugate transient with buoyancy writes both. **The solid region writes `p`
   and does NOT write `p_rgh`, `U`, `k`, `omega` or `nut`** — registering a
   uniform tuple across both regions would fail on the solid every time.

**Written but NOT registered as required** (present in T25R2's output, admitted
as evidence, never as a completion condition): `Qdot`, `phi`, `rho` on the
coolant. `phi` **must** be present at t = 70 for leg B's restart, and that is
registered as a **separate** leg-boundary assertion in §15 step 6.

---

## 10. INSTRUMENT ADMISSION — THE PLANTED CONTROLS, AND THE MUST-FIX

### 10.1 Planted-zero controls — `CLAUDE.md` rule 3

**A zero from a reader not shown able to see a non-zero is not evidence.** Every
reader admitted by this rung plants a known perturbation into a copy of the
artifact it reads, reads it back **from disk**, and **REFUSES (exit 2) rather
than degrades** if it cannot see the plant.

`PLANT = 1.234e-03 K`, inherited. Planted by **line index into the field file**,
never by value match. Readers under control: the outlet area-mean reader (Q1),
the solid cell-zone volume-average reader (Q2), the `outlet_hflux` integrator
(Q0), the inlet patch reader (C3), the energy-ledger reader (C1) and the mass
reader (C2). **A comparator that reaches a verdict without every plant having
been seen is a defect, and the comparator refuses rather than reporting one.**

### 10.2 ⚠ MUST-FIX — THE D2 READER. **T25R2 §10 IS BINDING ON THIS RUNG.**

T25R2's Addendum B3.2 recorded a **second, independent blocker that never fired**
because §3.5 was evaluated first: `read_patch_T` accepts **only** a
`nonuniform List<scalar>` patch entry and expressly **refuses** to fall back to
`refValue`. The real staged coolant inlet is written by OpenFOAM as

```
    inlet { type fixedValue; value uniform 293; }
```

— **verified again on disk for this registration** in
`T25R2_L2/0.orig/coolant/T`. **So the inlet reader would refuse at every written
time and C3 would be `NOT A RESULT` on an INSTRUMENT REFUSAL even if every
physics gate passed.**

> **REGISTERED OBLIGATION: `analyse_t25R3.py` MUST read a `uniform <scalar>`
> patch entry, and its `--selftest` MUST exercise the reader against the exact
> form OpenFOAM writes, not a forged `nonuniform` list.** T25R2's root cause was
> that *the fixture did not resemble the situation* — the sixth instance of that
> class in one night. The selftest fixture for this rung is generated **by
> copying a real staged `0.orig/coolant/T`**, never by hand-writing one.

---

## 11. DECOMPOSITION — **RECORDED EXPLICITLY, NOT OPTIONAL**

| item | registered value |
|---|---|
| ranks per run | **2**, IDENTICAL on all six runs |
| method | **`simple`** |
| coefficients | `n (2 1 1); delta 0.001;` — the split is streamwise |
| applied to | **both regions**, `system/module/decomposeParDict` and `system/coolant/decomposeParDict`, identical |
| **seed** | **NONE EXISTS, AND THAT IS THE POINT.** `simple` is deterministic by construction — it partitions by geometric bisection with no RNG. **This specification IS the recorded decomposition state, in place of a seed.** |
| `scotch` | **REFUSED.** Its partition is not seed-controlled at v2606, so a partition difference between mesh levels could contaminate the observed order and could not be shown not to have. |

**WHY THE RANK COUNT IS FROZEN ACROSS THE LADDERS.** The number of partitions
changes summation order and GAMG agglomeration, and therefore changes the answer
in the last digits. Holding it at exactly 2 on **every** run of **both** ladders
means partition count **cannot** contribute to any level-to-level difference. A
ladder run at mixed rank counts has no readable observed order and this
registration forbids one.

**DISCLOSED: T25R3 IS NOT BIT-COMPARABLE WITH T25R2.** T25R2 ran serial
(`RANKS=1`, both launch contexts). No T25R3 number may be differenced against a
T25R2 number and called a lever's effect.

**CONCURRENCY AND CONTENTION.** **Five concurrent slots × 2 ranks = 10 cores**,
on a 16-core box (`nproc` = 16; load average at drafting **4.84**, with the motor
convergence ladder concurrent per Sanaa's §7). **`W30` launches into slot 1 on
`S1`'s completion** (S1 finishes at ≈ 38 min, W30 needs ≈ 157 min, so it lands at
≈ 195 min — well inside T4's ≈ 343 min critical path and costing nothing in wall
clock). **Expected contention 5–11 %**, disclosed on every row, **never
subtracted and never absorbed into the actual/predicted ratio**
(`COMPUTE_BUDGET_CHARTER` §6). The ratio is computed from `ExecutionTime`, the
solver's own CPU accounting; wall-derived core-minutes are reported separately
and carry the contention.

---

## 12. COST — `CLAUDE.md` RULE 12

### 12.1 The rate is **T25R2's OWN MEASURED RATE**, not a borrowed one

Measured on this solver, this mesh, these loads, these numerics, at
**L1 = 16,608 cells, 1 rank, 1,800 steps**:

| `nOuterCorrectors` | measured core-min | **s/step** |
|---|---|---|
| 10 (`T25R2_L1`) | **7.148** | **0.23827** |
| 20 (`T25R2_L1_OC20`) | **12.615** | **0.42050** |

Linear fit in the sweep count — the same construction T25R2's §12 published as a
deliverable in its own right (it measured **×1.765** for a sweep doubling, not
the ×2.18 the probe had predicted):

> **per-step seconds = 0.056033 + 0.018223 · n**, giving **n = 15 → 0.32938 s/step
> (×1.3824)** and **n = 30 → 0.60273 s/step (×2.5297)**.

**Mesh scaling is ASSUMED LINEAR IN CELL COUNT and is UNMEASURED** — no level
above L1 has ever run in this family. That assumption is the largest single
source of error in the table below and the cap margin of §12.3 is sized for it.

### 12.2 ⚠ **THE MULTIPLIER, SAID OUT LOUD**

| factor | value |
|---|---|
| steps: 11,800 against T25R2's 1,800 | **× 6.556** |
| per-step cost: 15 sweeps against 10 | **× 1.382** |
| **combined, per base run, same mesh** | **× 9.06** |
| the time ladder's finest arm, ×4 steps again | **× 36.2** vs T25R2_L1 |
| **the whole registered rung against T25R2's ACTUAL total spend of 19.780 core-min** | **× 99.9** |

**This rung costs approximately one hundred times what its predecessor spent.**
Sanaa's header is *"Cost is not a constraint"*, and rule 12 still requires the
figure and the cap, so both are here.

### 12.3 The registered table — POINT, CAP and timeout, per run

Core-minutes at **2 ranks**, with an **assumed parallel efficiency of 0.85**
(also unmeasured on this case):

| run | mesh | steps | serial-equiv core-min | **POINT core-min (2 ranks)** | wall min | **HARD CAP core-min** | **`timeout_s`** |
|---|---|---|---|---|---|---|---|
| S1 | L1 | 11,800 | 64.8 | **76.2** | 38.1 | **305** | 9,145 |
| S2 | L2 | 11,800 | 145.8 | **171.5** | 85.7 | **686** | 20,577 |
| S3 | L3 | 11,800 | 327.9 | **385.8** | 192.9 | **1,543** | 46,298 |
| T2 | L2 | 23,600 | 291.5 | **342.9** | 171.5 | **1,372** | 41,154 |
| T4 | L2 | 47,200 | 583.0 | **685.9** | 342.9 | **2,744** | 82,307 |
| W30 | L2 | 11,800 | 266.7 | **313.8** | 156.9 | **1,255** | 37,653 |
| staging, meshing, `checkMesh`, verification | — | — | — | **3.0** | ~10 | **12** | — |
| **TOTAL** | | | **1,679.7** | **1,979.1** | | **7,916** | |

**Dollars: POINT $1.69, at cap $6.77.** At $0.0513/core-h, c7a.4xlarge.
**DERIVED, NOT MEASURED**; `cost_basis = REPORTED-BY-OWNER` — this box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER` §5). **Even at the hard cap the
rung is inside the $25 pre-authorisation**, which is stated as a fact and not
used as a licence: rule 9 says a blanket is not a per-item read.

### 12.4 ⚠ THE CAP MARGIN IS **×4** AND ITS BASIS IS STATED, BECAUSE A CAP THAT STOPS A RUN SANAA ORDERED IS A BAD CAP

**An overrun STOPS the run; it does not get a new budget** (rule 12). A cap set
tight against a POINT built on two unmeasured assumptions would kill a run she
ordered, so the margin is sized to cover **all three** of the following
**simultaneously**:

- mesh scaling **super-linear by up to ×2** (GAMG on a 5× mesh — the assumption
  of §12.1 failing in the expensive direction);
- parallel efficiency falling from 0.85 to **0.45** at 2 ranks;
- contention at **20 %**, double the disclosed expectation.

`2.0 × (0.85/0.45) × 1.20 = 4.53` — so **×4 covers all three at once except in
the very worst corner**, and the corner is named rather than papered over.
**This is the same ×4 margin T25R2 registered and under which its actual/POINT
ratios came in at 0.861 and 0.697** — i.e. the margin has never yet been needed
on this case, which is stated as evidence for the number and not as a promise.

### 12.5 Estimate-versus-actual calibration — rule 12, mandatory at completion

At the completion of this rung, **each of the six runs** contributes a row to
**`docs/COST_CALIBRATION.md`** giving the pre-registered POINT, the actual
`ExecutionTime`-derived core-minutes, the **ratio actual/predicted**, and the
attribution split into **contention / waste / misprediction**, with waste named
separately and never folded into the ratio. **A completion report without this
comparison is incomplete.** The two unmeasured assumptions of §12.1 and §12.3
(mesh scaling, parallel efficiency) are each **measured for the first time** by
this rung and each gets its own calibration line — that is a deliverable of the
spend independent of the physics verdict.

---

## 13. ⚠ THE REGISTERED CEILING — WHAT THIS RUNG CAN REACH AT BEST, STATED BEFORE IT RUNS

**BEST REACHABLE OUTCOME:** `PASS` on `G-I`, `G-S` and `G-T`, with `CONVERGING`
Roache triples on both ladders, observed orders inside [0.5, 1.5], and a GCI band
on every reported number. That is a **VERIFICATION** result: the case's answer is
demonstrated grid-converged and step-converged to a registered tolerance, with an
uncertainty band.

**WHAT IT CAN NEVER REACH, AND THE READER IS TOLD NOW RATHER THAN LATER:**

> **`P` — validation against a public primary source — IS NOT REACHABLE BY THIS
> RUNG, AND NOT BY ANY SUCCESSOR ON THIS CASE AS DEFINED.**

The grounds are structural, not a matter of effort:

1. **The geometry is a construction, not a specimen.** An 8-cell, 2-D,
   unit-depth module with 3 mm channels at 33 mm pitch corresponds to no
   published experiment.
2. **The loads are Sanaa's ruling, not a measurement.** 1e5 W/m³ and 2.5e4 W/m³
   were set by directive on 2026-09-01 04:20Z as a plausible 5–8C-class rate.
   They are an input she chose, and no external record can confirm the answer
   they imply.
3. **There is no public dataset for the outlet history or the per-cell peaks of
   this configuration.** None was found and none is claimed.

**Consequently every number this rung produces is a statement about the
CONSISTENCY of a computation, never about the accuracy of a prediction.** The
band from §8 is a **numerical** uncertainty and contains **no model-form
uncertainty at all**: first-order upwind, `kOmegaSST` at `Re_Dh = 3200` (which is
barely past the laminar–turbulent transition for a duct and where the model is
weakest), an isotropic solid conductivity, and a 2-D idealisation of a 3-D module
are **four unquantified modelling assumptions that the GCI does not see**. Saying
so here, in the registration, is the only place saying it costs nothing.

---

## 14. THE PREDICTION — **REGISTERED SO THAT IT CAN LOSE**

This team's standing practice. Four separable claims, each falsifiable by the six
runs, each with its ground:

1. **`G-S` FAILS on Q1 (the outlet history) and PASSES on Q2 (the solid peaks).**
   Ground: T25R2 measured the outlet moving **2.404e-02 K** under a sweep
   doubling while the solid moved **1.200e-03 K** — a factor of **20**. The
   outlet responds on the channel residence time `L/U = 31.25 ms`; the solid on
   `τ ≈ 696 s`. The quantity that was sensitive to iteration will be the quantity
   sensitive to mesh.
2. **`G-T` PASSES on both quantities.** Ground: the load is now C⁰ rather than
   discontinuous, and even the coarsest ladder level resolves each ramp with 50
   steps.
3. **`p_space` lands inside [0.5, 1.5]** — i.e. the ladder behaves like the
   first-order scheme it is. Ground: `bounded Gauss upwind` on every advected
   scalar, and three levels at exactly r = 1.5 from one script.
4. **`G-I` PASSES.** Ground: T25R2's 10→20 sweep gap on the solid was already
   **11.6× smaller** than the T25RF probe's 5→10 gap at the same instant, so the
   sweep sequence was visibly converging at 10; at 15 versus 30, with a C⁰ load
   and a 25× finer step, the iterative change should be far below a tenth of the
   mesh difference.

**Claim 1 is the one this lane expects to lose the rung on.** A first-order
scheme at r = 1.5 shrinks the level-to-level difference by only 1.5× per level,
and if the L1→L2 outlet difference is of order 0.1 K then L2→L3 lands at
≈ 0.067 K — **inside** τ = 0.1 K, but not by much, and a larger L1→L2 difference
puts it outside. **This is registered as a coin toss and the coin is not this
lane's to weight.**

---

## 15. ORDER OF OPERATIONS — REGISTERED, AND NOT NEGOTIABLE

1. **This document is committed.** Nothing below happens before the commit sha
   exists.
2. **The supervisor reads this registration and the comparator AS A DIFF.**
   `SUPERVISION_CHARTER` §3 and `CLAUDE.md` rule 2. **Undelegable.** The three
   departures of §0 are ruled on here. **No solver launches before this step
   completes.**
3. `build_t25R.py --selftest` passes; **L3 is built**; `checkMesh` on both
   regions of all three levels.
4. Staging: `0.orig`, `constant`, `system` written for all six runs from one
   script. **`0` is created from `0.orig` by the LAUNCHER, immediately before the
   solve, never by the stager** — the age guard depends on it.
5. `verify_mesh_t25R3.py` measures and **refuses on any mismatch**: cell counts
   16,608 / 37,368 / 84,078; cells across each 3 mm gap 24 / 36 / 54 counted on
   all seven channels from distinct cell-centre y; cells across each 30 mm solid
   cell 12 / 18 / 27; interface faces 560 / 840 / 1,260 equal on both regions;
   streamwise dx 2.5000 / 1.6667 / 1.1111 mm; `nOuterCorrectors` 15 (30 on W30);
   all five literal `Final` relaxation keys present and **no quoted regex**;
   `p_rgh` tolerance 1e-08; the §5.1 source table byte-for-byte; the §5.3
   breakpoint condition on every registered dt; **no `0` and no time directory
   present**.
6. `analyse_t25R3.py --selftest` passes, **including the §10.2 uniform-patch
   reader exercised against a real staged `0.orig/coolant/T`**, and every planted
   control demonstrated visible.
7. Launch S1, S2, S3, T2, T4 into five slots at 2 ranks. **Leg A then leg B per
   run**; leg B launches only after leg A is `DONE` on conjuncts 1, 2, 3 and 5
   **and** `70/coolant/phi` is present.
8. **W30 launches into slot 1 on S1's completion.**
9. Completion is marked per run by `mark_done_t25R3.py`, which decides rule 4 and
   is **not reimplemented anywhere else**.
10. Grading: `G-I` first; then the Roache classification on both ladders; then
    `G-S` and `G-T`; then C1–C3; then C4–C6 reported. **No physics number is
    printed before `G-I` and the triple classification have been decided** — the
    comparator withholds, exactly as T25R2's did.
11. `docs/campaigns/T-family/T25R3_RESULTS.md`, with the §12.5 calibration rows.

---

## 16. FREEZE

**This registration is frozen at its commit.** The gate, the thresholds, the
caps and the labels are fixed at that sha, before any compute, and the freeze is
this document's entire evidentiary content: it proves the gate could not have
been chosen to fit an answer that does not yet exist.

- **Before first compute**, amendments are legal and **must state the condition
  and how it was checked**, naming a run directory that does not exist. The
  supervisor's ruling on the three departures of §0 lands as such an amendment if
  it changes anything.
- **After first compute the gates are closed.** Changes land only as dated
  addenda that cannot alter a gate, threshold, cap or label. Originals are
  struck, never rewritten.
- **The grading path is fixed at this commit.** `analyse_t25R3.py` hashes this
  document against the committed blob and **REFUSES on a mismatch**.

**The frozen table** — files whose content is fixed by this registration and
whose hash the comparator checks:

| file | role |
|---|---|
| `docs/campaigns/T-family/T25R3_PREREGISTRATION.md` | this document |
| `verification/runs/T-family/T25R3_MODULE_runs/stage_t25R3.py` | writes every dictionary; executes no solver |
| `verification/runs/T-family/T25R3_MODULE_runs/verify_mesh_t25R3.py` | measures; grades nothing |
| `verification/runs/T-family/T25R3_MODULE_runs/analyse_t25R3.py` | the comparator; the only file that reaches a verdict |
| `verification/runs/T-family/T25R3_MODULE_runs/mark_done_t25R3.py` | decides rule 4 |

**SUBMISSIONS PARKED** (`CLAUDE.md` rule 7). **PERMANENTLY PRIVATE** (rule 8).

---

## 17. WHAT THIS LANE COULD NOT VERIFY

Stated plainly, because an honest gap is worth more than a confident guess.

1. **The mesh cost scaling is ASSUMED, not measured.** No level above L1 has ever
   run in this family. Linear-in-cells is an assumption and §12.4's cap margin
   exists to survive its failure.
2. **The parallel efficiency at 2 ranks is ASSUMED (0.85), not measured.** T25R2
   ran serial. It is measured for the first time by this rung.
3. **y+ is ESTIMATED from Blasius, not measured.** No `yPlus` field object has
   ever been run on this case. C4 measures it; nothing here quotes the estimate
   as the measurement.
4. **`Co` at the new time steps is inferred by scaling T25R2's reported ≈ 1600.**
   It is reported from the solver's own output (C5), not from this scaling.
5. **L3 has never been built.** Its 84,078 cells, 1,260 interface faces and
   1.1111 mm streamwise dx are **arithmetic from the registered `LEVELS` dict**,
   not measurements. Step 5 of §15 measures them and refuses on a mismatch.
6. **The restart's effect on the answer is BOUNDED, not measured.** §6.3 bounds
   the ASCII truncation at ≈ 3e-10 K by arithmetic on `writePrecision 12`. No run
   has demonstrated it.
7. **The `energyCoupling` `loopControl` was read at source and never exercised.**
   §0.1 declines to use it on cost and confounding grounds; this lane has not
   demonstrated that it behaves as its documentation says.
8. **The `setTimeStep` function-object route was read at source and never
   exercised** (§6.3). It is refused on a principle, not on a measured failure,
   and a reader should not take this document as evidence that it does not work.
9. **Whether τ = 0.1 K is passable on this case is unknown to this lane.** §7.2
   states the basis and §14 states the expectation; neither is evidence.

---

**NOTHING IN THIS DOCUMENT HAS RUN. NO SOLVER HAS BEEN LAUNCHED. THE NEXT ACTION
IS THE SUPERVISOR'S DIFF-READ OF §0, NOT A LAUNCH.**

<!-- END OF T25R3 PRE-REGISTRATION v1.0 -->
