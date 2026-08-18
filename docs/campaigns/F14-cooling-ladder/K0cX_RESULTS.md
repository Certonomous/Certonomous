# K0cX. Cross-geometry rung: results

Campaign F14, gate K0c. Solved 2026-08-18 18:43:23Z to 19:35:34Z; analysed
2026-08-18 21:48:55Z. Pre-registration `K0cX_PREREGISTRATION.md`, committed
`2ab6c77b` at 18:42:52Z — **31 seconds before the first graded solve**, recorded
in `K0cX_runs/PREREG_TIMESTAMP.txt`. Nothing below amended it.

Run tree `verification/runs/F14-cooling-ladder/K0cX_runs/`, machine record
`gate_k0cx.json`. 22 cases, 22 completion markers, none missing.

---

## 1. Verdicts

| Model | Verdict | Graded rows failed |
| --- | --- | --- |
| `kOmegaSST` | **GATE FAIL** | 10 of 20 |
| `kEpsilon` | **GATE FAIL** | 7 of 20 |
| `LaunderSharmaKE` | **GATE FAIL** | 7 of 20 |
| `laminar` | control, counted toward no verdict | 12 of 20 |
| **The rung** | **GATE FAIL** | 24 of 60 graded rows; 0 of 3 models passed |

`every_row_reachable_both_ways: true` over all 60 rows — the mutation control
confirmed each row could have returned either verdict.

**The three model verdicts survived the discrimination audit of Section 5.**
Removing every non-discriminating row left each model failing on rows that did
separate it from the laminar control, and no verdict moved.

---

## 2. The four registered transfer questions

The rung existed to ask, of each K0cS result, **does it travel to a different
geometry?** Predictions were registered in both directions.

| # | K0cS result | Did it travel? |
| --- | --- | --- |
| **F1** | kOmegaSST **GATE FAIL**, 8 of 10 rows | **YES.** GATE FAIL here too, 10 of 20 |
| **F2** | Refinement moved stratification **away** from the experiment | **PARTLY, and it reversed for kOmegaSST.** Section 3 |
| **F3** | LaunderSharmaKE **relaminarised** on refinement; REFUSED | **NO.** No collapse at any of three mesh levels. Section 4 |
| **F4** | Constant Prt closed **negative** — 1.75 % on Nusselt | **NO.** Up to **14.2 %** here, and in the wrong direction. Section 6 |

**Three of the four did not transfer, and two of those non-transfers are the
rung's substance.** A failure that travels and a failure that does not are
different findings, and the pre-registration committed to reporting both.

---

## 3. F2 — refinement reversed direction between geometries

K0cS recorded refinement moving the stratification parameter *away* from the
experiment for `kOmegaSST` (+0.080) and `LaunderSharmaKE` (+0.158), and read the
coarse-mesh agreement as cancellation.

On the tall cavity, measured coarse-to-fine on the R1 stratification row:

| Model | lo Ra | hi Ra |
| --- | --- | --- |
| `kOmegaSST` | 0.22872 -> 0.22087, **toward** | 0.24274 -> 0.23527, **toward** |
| `kEpsilon` | 0.015439 -> 0.014128, toward | 0.019753 -> 0.018310, **away** |
| `LaunderSharmaKE` | 0.012910 -> 0.010591, toward | 0.020316 -> 0.018627, **away** |

**The K0cS direction reversed for the model it was first observed on.** The two
`k`-`epsilon`-family models moved away at the high Rayleigh number, as K0cS
recorded, but `kOmegaSST` moved toward the experiment at both.

**Carried caution, not resolved.** `X_hi_c_SST` — the coarse case that supplies
the high-Rayleigh `kOmegaSST` entry above — **missed the registered convergence
criterion** on `Nu_pct` and `Uy_pct` (`gate_k0cx.json`, `convergence`). Grading
used the fine mesh, which converged, so no verdict rests on it; the *direction*
claim in that one cell does. It is reported with that defect attached rather
than dropped or quietly used.

---

## 4. F3 did not travel — LaunderSharmaKE did not relaminarise here

K0cS recorded the damping function's implied maximum falling **0.887 -> 0.034**
on refinement, **25 996 `bounding k` events of 40 000 iterations**, and Reynolds
stress four orders below molecular. The model was **REFUSED**, not failed.

On the tall cavity, over a **three-level** mesh ladder:

| Case | cells | `fmu` implied max | `bounding k` events | `nu_t/nu` max |
| --- | ---: | ---: | ---: | ---: |
| `X_lo_c_LS` | 4 800 | 0.9513 | **0** | 31.03 |
| `X_lo_f_LS` | 12 288 | 0.9514 | **0** | 31.10 |
| `X_hi_c_LS` | 4 800 | 0.9675 | **0** | 39.80 |
| `X_hi_f_LS` | 12 288 | 0.9676 | **0** | 39.89 |
| `X_hi_x_LS` | 31 314 | 0.9677 | **0** | 39.93 |

**No collapse, at any refinement level, at either Rayleigh number.** Every
LaunderSharmaKE case met the convergence criterion, and the eddy viscosity rose
slightly with refinement rather than falling. The model was **graded** here,
which at K0cS was impossible.

### 4.1 A numerical trap in this comparison, recorded because it is easy to misread

`gate_k0cx.json` carries a second damping-function diagnostic,
`fmu_launder_sharma_formula_first_cell`, which measured **0.0335 to 0.0342** in
every LaunderSharmaKE case above. **That number is not K0cS's 0.034 and means
close to its opposite.** K0cS's 0.034 was the *domain maximum* of `fmu` after
collapse — the damping function switched off everywhere. The 0.034 here is the
*first cell at the wall*, where a damping function is supposed to be near zero,
while the domain maximum stood at 0.95-0.97. **The two diagnostics coincide to
two significant figures and carry opposite readings.** Anything comparing the
two rungs on this quantity must compare `fmu_implied_max` with
`fmu_implied_max`.

### 4.2 What this does to the damping-function hypothesis, and what it does not

`K0c_THERMAL_CLOSURE_SYNTHESIS.md` section 2.3 read the collapse as possibly
triggered by mesh refinement alone, and registered experiment **X1** to separate
"refinement alone" from "refinement plus a low turbulent-Reynolds-number core".

**This rung narrows that hypothesis space from a direction X1 does not reach, and
it rules out the simpler half.** The tall cavity was refined to a first cell of
0.0784 mm, finer than the square cavity's, and `Re_t` at the first cell fell to
**0.0278** at the extra-fine level — *lower* than the values at which the square
cavity collapsed. Refinement alone did not trigger it, and **a low `Re_t` core
did not trigger it either.** Whatever distinguishes the square cavity is
therefore neither of the two candidates section 2.3 named.

**X1 remains worth running and is not superseded.** It asks whether the collapse
occurs on a *non-buoyant* flow at all, which no case here addresses. What
changed is that X1's two registered outcomes no longer exhaust the possibilities,
and its pre-registration should say so before it runs.

---

## 5. Row discrimination audit, per `VERIFICATION_CHARTER.md` §2c

Every graded row was compared against the laminar control on the same rung and
row, following the rule D413 shipped.

| Row | quantity | model passes | control passes | separated from control |
| --- | --- | ---: | ---: | ---: |
| R1 | core stratification S | 2/6 | 0/2 | 6/6 |
| R2 | peak upward velocity, magnitude | 0/6 | 0/2 | 6/6 |
| **R3** | peak upward velocity, **location** | **6/6** | **2/2** | **0/6** |
| R4 | peak downward velocity, magnitude | 0/6 | 0/2 | 6/6 |
| R5 | peak downward velocity, **location** | 6/6 | 2/2 | 1/6 |
| R6 | mid-width T at y/H = 0.30 | 4/6 | 0/2 | 2/6 |
| **R7** | mid-width T at y/H = 0.50 | **6/6** | **2/2** | **0/6** |
| R8 | mid-width T at y/H = 0.70 | 6/6 | 0/2 | 6/6 |
| **R9** | antisymmetry defect | **6/6** | **2/2** | **0/6** |
| R10 | average Nusselt number | 0/6 | 0/2 | 6/6 |

**R3, R7 and R9 carried no discriminating power** — every model passed them,
the laminar control passed them, and none separated from the control by more
than its own band. That is **18 of the 60 graded rows, 30 percent**. R5 passed
for everything and separated in 1 of 6.

**R3 and R5 are the velocity-peak LOCATION rows, and this is their third
appearance.** D413 recorded the same shape as K0cS G9 and as K0cT R11 and R13.
The quantity has now been hollow on **three geometries spanning three Rayleigh
decades**, which is enough repetitions to treat the row design as the defect
rather than the individual rungs. A contributing cause is visible in the data:
the peak location is reported at a cell centre, so it takes only a handful of
distinct values on a given mesh, and the 5 mm band spans several of them.

### 5.1 R9 is additionally not independent of R2 and R4

`analyse_k0cx.py:458` computed the antisymmetry defect as
`100 * abs(abs(Vup) - abs(Vdn)) / max(abs(Vup), abs(Vdn))` — **entirely from
`Vup` and `Vdn`, which were themselves graded as R2 and R4.** R9 introduced no
measurement those two rows did not already carry.

This is not a §2a identity, because it is derived from measurements rather than
from the case setup, and the charter's identity clause does not reach it. It is
a **row-independence** defect: the rung reported 60 graded rows, of which 6 were
a function of 12 others. **The denominator overstated the number of independent
tests**, in the same direction and for a related reason as D414.

It also explains why R9 always passed. The models produced near-perfectly
antisymmetric solutions — defects of 3.8e-05 to 5.5e-03 percent — against an
experiment showing a real 3.6 percent (lo) and 0.5 percent (hi) defect, under a
band phrased as **`defect <= 10 percent`**. A bound of that shape is passed most
easily by a solution with no defect at all. **The laminar control scored 3.6564
percent at lo Ra, nearer the measured 3.6 than any turbulence model reached.**

### 5.2 What this changes, and what it does not

**No verdict moved and no number moved.** All three models failed rows that
discriminated: R2, R4 and R10 failed for every model on both rungs and separated
from the control 6 of 6 times.

**Owed, and named rather than performed:** R3, R7 and R9 should be moved out of
the graded tally into a reported block, as `analyse_k0cx.py` already does for the
heat balance. That regenerates a published artifact and is a re-run, so it is
filed here rather than done silently — the same disposition D414 took, and the
same debt.

---

## 6. F4 did not travel, and the direction is the finding

K0cS moved Prt from 0.85 to 1.28 and measured **1.75 percent** on average
Nusselt against a registered 5-20 percent, and read constant Prt as **not** where
the square cavity loses accuracy.

Three cases were run at the Prt **measured** for this cavity — 1.071 at lo Ra
and 1.283 at hi Ra, DERIVED in addendum A1.6b from Betts Table 1 — against
their 0.85 twins, changing nothing else.

| Pair | Prt | Nusselt | error vs experiment | stratification S |
| --- | --- | --- | --- | --- |
| `X_lo_f_SST` -> `P_lo_f_SST` | 0.85 -> 1.071 | 4.8680 -> 4.6971, **-3.51 %** | -16.79 % -> **-19.71 %**, widens | 0.2209 -> 0.2829, away |
| `X_hi_f_SST` -> `P_hi_f_SST` | 0.85 -> 1.283 | 5.6965 -> 5.3322, **-6.39 %** | -24.75 % -> **-29.56 %**, widens | 0.2353 -> 0.3530, away |
| `X_hi_f_KE` -> `P_hi_f_KE` | 0.85 -> 1.283 | 9.8346 -> 8.4368, **-14.21 %** | +29.92 % -> **+11.45 %**, narrows | 0.0183 -> 0.0466, **into band** |

**The same closure knob that moved the square cavity by 1.75 percent moved this
one by up to 14.2 percent.** That is a **measured geometry dependence of a named
failure mode**, and it is the first one this ladder owns.

**But it did not close the gap the synthesis hoped it would.** X4 registered
"arm (a) closing the tall cavity's -16.8 / -24.8 percent Nusselt gap" as the
informative outcome. Moving `kOmegaSST` to the *measured* Prt made its Nusselt
error **worse on both rungs**, because the model already under-predicted and the
correction pushed it further down.

**The sign of the benefit depended on which side of the experiment the model
already sat.** `kEpsilon` over-predicted by 29.9 percent, and the same
correction improved it by 18.5 points and carried its stratification row from
FAIL to inside the band. `kOmegaSST` under-predicted, and the same correction
degraded both quantities.

**The reading this supports is narrow and is not that Prt is the defect.**
Constant Prt is a knob that trades against whatever else is wrong, large enough
on this geometry to matter and pointed the wrong way for the model that fails
worst. Using the measured value is more defensible than using 0.85 and makes
`kOmegaSST` agree with the experiment less well. **Both of those are true at
once, and a correction that is right on the physics and wrong on the answer is
evidence about the rest of the model, not about the correction.**

### 6.1 These three cases were NOT graded, and could not have been

The Prt arm ran at the fine mesh only. Specification §2.5 forbids grading a
solve without its grid-sensitivity pair, and `analyse_k0cx.py` excluded all
three from every model's row count. **They are a sensitivity, reported and
gated on nothing.** The 60 graded rows come from the `X_` cases alone.

---

## 7. Convergence, and the control's standing

| Case class | Converged |
| --- | --- |
| All `kOmegaSST`, `kEpsilon`, `LaunderSharmaKE` cases | yes, except `X_hi_c_SST` |
| `X_hi_c_SST` | **no** — `Nu_pct`, `Uy_pct` |
| **All four `laminar` cases** | **no** — `Nu_pct`, `S_abs`, `Uy_pct` |

**The laminar control did not converge on any mesh at either Rayleigh number**,
and its heat-balance closure — 0.32 to 1.19 percent against 0.03 to 0.12 percent
for the turbulence models — is an order of magnitude worse, consistent with a
genuinely unsteady flow being forced to a steady solve.

**This weakens the discrimination test of Section 5 and the weakening is not
symmetric.** Where a row separated a model from the control, the separation
stands against a control that is a poorly converged steady approximation to an
unsteady flow. Where a row did *not* separate — R3, R7, R9 — the finding is
**stronger**, not weaker: those rows failed to distinguish a turbulence model
from a solve that did not even converge.

`analyse_k0cx.py` refused the laminar arm's own verdict on convergence grounds
and reported its rows on the same footing without counting them, which is the
correct disposition and is why the control's 12 of 20 appears above with the
refusals attached.

---

## 8. Wall-function admissibility was tested rather than assumed

`K0cT_RESULTS.md` §1.2a argued that wall functions are inadmissible at this
cavity's y+ of about 0.19. The pre-registration declined to use that argument to
exclude `kEpsilon` and ran it with the high-Re treatment it was built for.

Measured y+ maxima, from each solve's own near-wall velocity gradient rather
than from the `yPlus` function object, ranged **0.102 to 0.419** across all 22
cases — so the treatment was indeed applied far outside its intended range.

**`kEpsilon` nonetheless returned a stratification far closer to the
experiment than `kOmegaSST` did** — 0.0141 against 0.2209 at lo Ra, where the
reference was 0.016 — **while failing Nusselt by +29.9 percent, the largest
error of any turbulence model here.** It was not uniquely good at it:
`LaunderSharmaKE` also passed R1 at lo Ra, and at hi Ra came 0.0003 closer
than `kEpsilon` did, both still failing. Of the two models carried into the
measured-Prt arm, `kEpsilon` was the one whose stratification row reached the
band there. The wall
treatment cannot be read off that pattern in either direction, and this rung
does not resolve §1.2a. It records that the exclusion argument was not needed to
reach a GATE FAIL, and that the model excluded by it was not uniformly worst.

---

## 9. Cost

Measured from each solve's own `ExecutionTime`, summed over all 22 cases:
**19 310 s = 321.8 core-minutes = 5.364 core-hours**, at
$0.0513/core-hour = **$0.275**, against a standing $25 authorisation.

Wall clock was 52 minutes for 22 cases across two waves, confirming the
K0cS observation that wall clock rather than cost binds on this hardware.

---

## 10. What this rung did not establish

- **It measured no anisotropy on either cavity.** R3 of the synthesis stays
  unsupported and unrefuted, and **X2** stays the experiment that would decide
  it. Nothing here substitutes for it.
- **It did not identify which term is wrong.** The Prt result bounds one knob's
  size on one geometry; it names no mechanism.
- **It did not compare severity against the aerodynamic side.** The gates remain
  incommensurately graded, as section 4.6 of the synthesis recorded.
- **Its Nusselt reference carries the two cautions the specification attached**
  — Betts Table 1 not re-deriving its own lo-Ra Nusselt from its own tabulated
  gradient (carried into `u_val` at 2.09 %), and an 8.8 percent rig-to-rig
  reproducibility spread wider than the authors' stated ±5 %. **`LaunderSharmaKE`
  at hi Ra missed by 5.50 percent, outside `u_val` = 5.41 % and inside the 8.8 %
  spread.** That row is recorded GATE FAIL against the registered band, and no
  model is called validated by it.
- **`LaunderSharmaKE` still has no aerodynamic case in this lab**, so its
  non-collapse here cannot yet be compared with anything isothermal. That is
  **X8**.

---

## 11. Departure disclosed: the comparator was extended after solving began

**The pre-registration's comparator was not frozen for the whole of compute, and
this section states exactly what changed, when, and what it could and could not
have reached.**

`analyse_k0cx.py`, `report_diagnostics.py` and `write_report_tables.py` were
modified at **18:58:28 to 18:59:05Z**. The first graded solve started at
**18:43:23Z** and six cases had already written completion markers by then — the
earliest at 18:55:43Z. **Results were readable when the comparator was edited.**

### 11.1 What did not change

`build_cases.py` and `launch_all.sh` — everything that defines the physics, the
meshes, the boundary conditions and the run control — were **byte-identical to
the pre-registration commit** and were not touched at any point. No case was
rebuilt or re-solved.

The whole change to `analyse_k0cx.py` was **55 added lines and 2 removed**, and
both removed lines were re-added in extended form: the `diag` dictionary
initialiser, gaining new keys, and `uv = []` becoming `uv, uvx = [], []`.

**No band, no reference used for grading, no row definition, no verdict rule, no
discrimination test and no mutation control was altered.** Verified by
inspection of every removed line and by confirming that the two newly parsed
references, `nut_over_nu_centreline` and `uv_centreline`, appear **only at their
own assignment statements and are read by nothing** — they were parsed so the
rung could report against Betts Table 1 without inventing a band, and they reach
no verdict. The four new per-case diagnostics are written into `diagnostics` and
read by no grading function. The two reporting scripts add table columns and
compute no verdict.

### 11.2 What this does and does not touch in the findings above

| Claim | Diagnostic it rests on | Present before compute? |
| --- | --- | --- |
| **§4 headline** — no relaminarisation: `fmu` implied max 0.951-0.968, **zero** bounding-k events, `nu_t/nu` 31-40 | `fmu_implied_max`, `bounding_k_events`, `nut_over_nu_max` | **YES** — unchanged from the pre-registration commit |
| §4.1 the 0.034 trap | `fmu_launder_sharma_formula_first_cell` | **NO** — added 18:59 |
| §4.2 `Re_t` down to 0.0278 | `Re_t_first_cell_midheight` | **NO** — added 18:59 |
| §1, §2, §3, §5, §6, §7, §8 and every verdict | grading path only | **YES** — unchanged |

**The rung's verdicts and all four transfer answers rest entirely on
instrumentation that predates the first solve.** The two supplementary readings
in §4.1 and §4.2 do not, and are marked here rather than left for a reader to
discover from file timestamps.

### 11.3 The reading

Adding a diagnostic after seeing partial results is a weaker act than moving a
band, and it is not a free one. **The added quantities were chosen while some
answers were visible**, which is exactly the condition under which a diagnostic
gets chosen because it will say something. The honest description is that
`Re_t_first_cell_midheight` and the LaunderSharma `fMu` formula were added
because the relaminarisation question had become the interesting one, and the
existing diagnostics could show *that* it had not happened without showing
*what* the causal variable was doing.

**The defensible version of this work adds those diagnostics before compute, or
adds them afterwards and re-derives them under a fresh registration.** Neither
happened. The measurements are reported, they are reproducible from stored
fields, and no verdict depends on them.

**Falsifier for this disclosure:** exhibit any line in the 18:58-18:59 edits
that changes a graded value, a band, or a verdict. The diff is 88 lines over
three files and is fully contained in the commit that lands this record.

---

## Dated correction, 2026-08-18 — the debt §5.2 named is paid, and nothing moved

**Nothing above is edited.** W-4. §5.2 recorded that R3, R7 and R9 *"should be
moved out of the graded tally into a reported block"* and filed it as **owed**
because it regenerates a published artifact. It has been done.

**The change is six lines in `analyse_k0cx.py`.** A module-level constant
`NON_DISCRIMINATING = ("R3", "R7", "R9")` and a split of each model's rows into
`rows` and `reported_never_graded`, with `n_rows`, `n_fail` and the verdict
computed from the graded rows only. **No measurement code, no band, no
reference and no verdict rule was touched.**

**R5 is deliberately NOT in that list.** §5 measured it separating in 1 of 6,
so it is not in the class the rule catches, and widening the fix past what the
audit measured would have been the same error in the other direction.

### The re-run, and what it proves

| | before | after |
| --- | --- | --- |
| `kOmegaSST` | GATE FAIL, 10 of **20** | GATE FAIL, 10 of **14** |
| `kEpsilon` | GATE FAIL, 7 of **20** | GATE FAIL, 7 of **14** |
| `LaunderSharmaKE` | GATE FAIL, 7 of **20** | GATE FAIL, 7 of **14** |
| `laminar` control | 12 of **20** | 12 of **14** |
| **The rung** | GATE FAIL, 24 of **60** | GATE FAIL, 24 of **42** |

**Every measurement is byte-identical across the re-run** — `measurements`,
`convergence`, `reference_parsed`, `bands_parsed` and `laminar_rows` all compare
equal between the two `gate_k0cx.json` files. **No verdict moved, no failure
count moved, and no number moved.** The 18 rows were not deleted: they are
carried in `reported_never_graded` with their values, deviations, bands and
their own PASS verdicts intact.

**What moved is the denominator, and only the denominator.** The evidence base
was overstated by 43 % — 60 rows claimed where 42 carried evidence.

### The reading, which is the same one D414 reached from the other side

**This was invisible for the same reason D414's was: the rows all PASSED.** A
row that grades nothing is only visible when something else fails, and R3, R7
and R9 passed for every model on every mesh and for the laminar control too.
**An inflated denominator made of passing rows is the hardest kind to see and
the kind that most flatters the record.**

D414 counted an identity as evidence; §5.1 here counted a row derived from two
other graded rows as independent of them. **Both were denominators, both were
found by instrument rather than by review, and in both cases no verdict moved —
which is exactly why neither was caught when it was written.**
