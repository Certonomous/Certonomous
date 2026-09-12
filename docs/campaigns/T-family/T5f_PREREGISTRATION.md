# T5f — the T5b conjugate ladder re-solved with a turbulence setup that can produce an admissible field, graded on a clause (1) with BOTH limbs: pre-registration (FROZEN)

**Version 1.0. Rung `T5f`. Family: T. Team: heat-transfer. Dated 2026-09-12.**
**Status: FROZEN at this commit. NO T5f CASE HAS BEEN BUILT AND NO T5f CASE HAS RUN.**

> **RULE 2, PRE-COMPUTE CONDITION NAMED AND CHECKED.** At this commit
> `verification/runs/T-family/T5f_runs/T5F_CUBE_c`, `…/T5F_CUBE_m` and
> `…/T5F_CUBE_f` **do not exist** — verified on disk by this lane immediately
> before freezing. There is no T5f answer for any gate below to have been chosen
> to fit.

> **T5d IS NOT SUPERSEDED AND IS NOT REPAIRED BY THIS RUNG.** T5d remains stopped
> for the reason its own DATED ADDENDUM 1 of 2026-09-10 records; that addendum
> stands untouched and is not lifted, amended or worked around here. **T5f does
> not use T5d's mesh, does not build T5d and does not depend on T5d in any way**
> — see §3.1, where using T5b's existing mesh is a deliberate design choice and
> not a convenience.

---

## 1. WHAT T5e ESTABLISHED, AND WHY IT MAKES THIS RUNG NECESSARY

`T5e_PREREGISTRATION.md`, graded at `10de627d`: **0 of 6 rows, all `NOT A RESULT`
at clause (1)**, on the three completed T5b levels, at zero solver cost.

**And the part that makes a re-solve the only remaining move:** under the T5e
comparator the **`y+` gate is `MET` on all three levels**. T5b's original failure
was a `y+` **maximum**; the `R_max`/`R_area` split registered in T5c moves it. So
the ladder's problem is **not** the near-wall mesh. It is that the three solves
did not produce admissible fields.

| level | omega max at `endTime`, from the field on disk | k min | cells at the solver's clamp floor |
|---|---:|---:|---:|
| `c` | 3.418609e+05 | 2.282118e-06 | 0 of 52,684 |
| `m` | **2.336752e+20** | **1.000000e-15** | **123,250 of 212,942 — 57.9 %** |
| `f` | **2.950019e+27** | **1.000000e-15** | **493,836 of 882,024 — 56.0 %** |

**On the medium and fine levels more than half the fluid cells carry no modelled
turbulence at all.** `bounding k` fires on **1000 of the final 1000 iterations**
on every level; `bounding omega` on 1000/1000 on `c` and 953/1000 on `f`. On the
medium, `k` and `omega` report `No Iterations 0` on **1000 of 1000** — the linear
solver is not solving them.

**Artifacts:** `verification/runs/T-family/T5b_runs/T5_CUBE_{c,m,f}/5000/air/{k,omega,nut}`;
`…/log.solve`; `verification/runs/T-family/T5e_runs/T5E_GRADE_OUTPUT.txt`.

**SCOPE.** Measured on T5b's three levels only. T5 and T5c ran the same setup;
**this lane has not read their logs and this registration claims nothing about
them.** That is on the heat-transfer supervisor's board.

---

## 2. THE HYPOTHESIS, IN ONE SENTENCE

**H1 — the inadmissible fields are produced by the discretisation and the
near-wall boundary conditions, not by the mesh and not by the geometry; changing
five named setup items and nothing else produces a ladder whose final fields are
physically admissible.**

---

## 3. WHAT CHANGES, AND ONLY THIS — five items, each with its measured reason

### 3.1 THE MESH DOES NOT CHANGE, AND THAT IS THE POINT

**T5f runs on T5b's mesh definition, unchanged**: the same `blockMesh` lattice,
the same first layer of **128 µm**, the same cell counts **52,684 / 212,942 /
882,024** air and **869 / 3,272 / 14,507** epoxy.

**Why, stated so it can be attacked:** T5d changed the mesh to repair `y+`. T5e
then measured `y+` as `MET` on **T5b's** mesh. **The mesh motivation is gone, and
changing the mesh and the setup together would confound the one variable this
rung exists to test.** One change at a time. A successor may repair the mesh
after H1 is settled; this rung does not.

**Consequence for the Roache triple:** the measured refinement ratios are T5b's
and are unchanged — air `r32 = 1.5929`, `r21 = 1.6060`; epoxy `r32 = 1.5557`,
`r21 = 1.6428`. **The two regions refine at different ratios and the heat-transfer
supervisor holds an open ruling on whether a conjugate triple whose regions refine
differently is three geometrically similar meshes. That ruling is owed BEFORE any
T5f triple is graded and this registration does not pre-empt it.** The regions
agree end-to-end to **0.095 %** and the divergence is equal and opposite
(−2.34 % then +2.29 %), the signature of integer rounding of division counts.

### 3.2 THE FIVE SETUP CHANGES

| # | change | measured reason |
|---|---|---|
| **S1** | `div(phi,k)` and `div(phi,omega)`: `bounded Gauss linearUpwind grad(…)` → **`bounded Gauss limitedLinear 1`** | `linearUpwind` is second-order and **unlimited** — not TVD — so it undershoots. Measured pre-clamp minima: `omega` **−1.636e+03** (level `c`, at `Time = 5000`) and **−6.323e+16** (level `f`). The clamp then fires on 1000 of the final 1000 iterations. A limited scheme is the direct remedy for an undershoot. |
| **S2** | `k` on all six walls: `fixedValue uniform 0` → **`kLowReWallFunction`** | The wall set pairs a **hard zero** `k` with `omegaWallFunction` and `nutLowReWallFunction`. OpenFOAM's low-Re companion for `nutLowReWallFunction` is `kLowReWallFunction`, not a hard zero. Measured: 57.9 % and 56.0 % of fluid cells sit at the clamp floor on `m` and `f`. |
| **S3** | `omega` `internalField`: `uniform 55.9957` → **a value consistent with the wall scale** (registered in §3.3) | `omega_w ≈ 6ν/(β₁y₁²)` is **1.929e+05** at level `c`. The initial field is **four orders of magnitude below** the value the wall function imposes in the first cell from iteration 1. |
| **S4** | `relaxationFactors/equations`: `k 0.5; omega 0.5` → **`k 0.3; omega 0.3`** | The near-wall `k`–`omega` stack is stiff; 0.5 is aggressive for a low-Re SST wall treatment. **This is the one item whose reason is an ALLOWANCE, not a measurement** — no measurement on this box isolates the relaxation factor, and it is labelled as such rather than dressed up. |
| **S5** | `nNonOrthogonalCorrectors` | **UNCHANGED at 0, deliberately.** The mesh is a Cartesian lattice: max skewness **4.180131424e-13**, cell openness **1.636908269e-16**, and every cell is an **exact axis-aligned box** (worst face thin/wide span ratio **0.000e+00**, measured 2026-09-11). **Zero correctors is correct here and raising it would be cargo-cult.** Recorded because an earlier note named it as a candidate and the measurement says it is not. |

### 3.3 THE REGISTERED VALUES

| quantity | value |
|---|---|
| `omega` `internalField` | **1.0e+04** — between the free-stream scale and the level-`c` wall value 1.929e+05, chosen so the initial field is within one order of the wall scale rather than four |
| `k` `internalField` | **0.0119885**, unchanged from T5b |
| `endTime` | **5000**, unchanged — see §5's outcome partition |
| solver, model, `Prt`, interface scheme, ranks | unchanged from T5b: `chtMultiRegionSimpleFoam`, `kOmegaSST`, `Prt 0.85`, `harmonic`, **1 rank** |

---

## 4. CLAUSE (1) — BOTH LIMBS, AND WHY ONE LIMB IS NOT ENOUGH

**T5e proved limb A catches a ladder whose fields are still MOVING.** It does
**not** follow that it catches a solve that has stopped being solved: a fully
frozen case presents a checkpoint delta of ≈ 0 and would **pass** limb A while its
turbulence model had locally ceased to exist. **The medium level was caught in
T5e only because its temperature kept moving while its turbulence was dead.** A
case where everything freezes would have walked through.

### LIMB A — the checkpoint field-delta, carried BYTE-IDENTICAL from T5e

Instrument: `verification/runs/T-family/T5e_runs/analyse_t5e.py`, frozen sha256
`c97d355d278b6523021d40a7a4925b8b9f3430bec25250b24238fdaa9daabfbc`. Tolerance
`1e-6 × range`, stride `1000`, checkpoints `4000` and `5000`, fields
`(air,T) (epoxy,T) (air,U)` — all **parsed** by that instrument out of
`T5_PREREGISTRATION.md` §5.5, not typed in. **No threshold is changed.**

### LIMB B — physical admissibility of the FINAL fields

Instrument: `verification/runs/T-family/T5f_runs/t5f_convergence_gate.py`, frozen
sha256 `9c4049b69d64ee7d5462340ab5e26dee66633aabb0a44672749da031dec31fb3`.

| bar | criterion | physical anchor |
|---|---|---|
| **B1** | `max(omega)` at `endTime` < **1.0e+09** | the largest legitimate `omega` is the wall value `6ν/(β₁y₁²)`; with the case's own `mu 1.7917e-05` and `ρ ≈ 1.161`, that is 1.929e+05 / 4.938e+05 / **1.264e+06** on `c`/`m`/`f`. The ceiling is **~800× above the finest level's wall value** — an absurdity bar, not a tuning knob. |
| **B2** | `min(k)` at `endTime` > **1.0e-12** | OpenFOAM clamps `k` to a small **positive** value, measured on this box as exactly **1.0e-15** — so a test for `k ≤ 0` **could never fire** and is not used. The bar sits **1000× above the observed floor**, so a cell must be genuinely at the floor, not merely small. |
| **B3** | `bounding k` and `bounding omega` each fire on ≤ **1 %** of the final **1000** iterations | a clamp exists to catch a transient. A clamp firing on nearly every iteration is the discretisation producing inadmissible values **as a steady state**. |

**THE RESIDUAL IS REPORTED AND NEVER GATED.** `T5_PREREGISTRATION.md` §5.5
refuses `residualControl` as a convergence instrument (L-141) and **T5f does not
overturn a frozen registration.** Residual *movement* and `nIter == 0` counts are
computed and printed as **REPORTED, NEVER GATED** (L-342 class). Every gating
quantity is read from a field file or counted from `bounding` lines. *(Recorded
plainly: the supervisor asked for residual movement as a criterion; it is
registered as a diagnostic instead, for the reason above, rather than silently
demoted.)*

### THE ORDER

**A level is CONVERGED only if limb A and limb B both pass.** Clause (1) then
proceeds exactly as T5e registered it: any level NOT CONVERGED → **`NOT A
RESULT`**, ahead of the `y+` clause, ahead of the triple, no GCI quotable.

### CALIBRATION HONESTY, AND A WEAKNESS STATED RATHER THAN HIDDEN

Limb B's thresholds were chosen with **T5b's three completed levels in hand as
prior evidence**. They are not fitted to T5f's answer — T5f has none (§0). Driven
against T5b as calibration, limb B returns `NOT CONVERGED` on all three: `c` on
B3 alone; `m` on B1, B2 and B3:k; `f` on B1, B2 and both B3 arms.

> **THE WEAKNESS: LIMB B HAS NEVER BEEN SHOWN TO PASS ON A REAL CASE.** Its
> "can pass" arm is demonstrated only on synthetic fields in `--selftest`. **A bar
> that has only ever rejected is a bar whose ability to accept is unproven**, and
> that is registered here as a live risk rather than discovered later. **If T5f
> returns `NOT CONVERGED` on limb B for all three levels, that outcome is
> ambiguous between "H1 is refuted" and "B1/B2/B3 are too tight", and §5 registers
> how it will be told apart.**

---

## 5. PREDICTIONS, AND AN OUTCOME PARTITION THAT MAKES EACH ONE READABLE

**P1 — the setup change produces admissible fields.** All three levels pass
**limb B**: `max(omega) < 1e9`, `min(k) > 1e-12`, and `bounding` on ≤ 10 of the
final 1000 iterations for both `k` and `omega`.
*Falsified if* any level fails any of B1, B2, B3.

**P2 — the collapse was the discretisation and the wall pairing, and it is
measurable as a count.** The number of cells at or below the `k` clamp bar falls
from **123,250 / 493,836** on `m` / `f` to **0** on every level.
*Falsified if* any level ends with a single cell at or below `1e-12`.

**P3 — the ladder reaches a steady state within the registered `endTime`.** All
three levels also pass **limb A**.
*Falsified if* any level's checkpoint delta exceeds `1e-6 × range` on any of the
three registered fields.

### THE OUTCOME PARTITION — registered in advance so no result is unreadable

| limb B | limb A | reading, registered BEFORE the run |
|---|---|---|
| pass | pass | **H1 SUPPORTED.** The ladder is converged and admissible; proceed to the `y+` clause and the triple — **subject to the supervisor's open ruling on the unequal region ratios (§3.1)**. |
| **pass** | **fail** | **H1 SUPPORTED, RUN TOO SHORT.** The setup works and the solve simply has not finished. This is **not** a refutation, and it is registered as such **in advance** so it cannot be spun either way. The response is a successor with a longer `endTime` and its own budget — **never a quiet extension of this one.** |
| fail | either | **H1 REFUTED** as to the level that failed. The failing bar is named, and §4's weakness applies: if **all three** fail limb B, the report must state that the result is ambiguous between refutation and over-tight bars, and must say which bar fired on which level. |

**No GCI is quoted for any row that never reached a triple. No observed order is
quoted for a non-monotone triple.**

---

## 6. `checkMesh` — THE STOP IS LIMB-SPECIFIC FROM THE OUTSET, AND THE GROUND IS A PROOF

**T5d's §6 registered `anything other than "Mesh OK"` as one boolean, and it
fired on a check that is a restatement of registered design.** T5f does not
repeat that, and does not need an amendment to avoid it, because the ground is
measured.

**MEASURED 2026-09-11**, on the built coarse mesh, all 52,684 air cells: a closed
form seeing **only each cell's three edge lengths and its internal-face pattern**
— never a face normal, face centre, cell volume or cell centre — reproduces
`checkMesh`'s `cellDeterminant` to a **maximum relative difference of 3.865e-15**
across a determinant range spanning **7.49 decades**. Scale invariance
demonstrated: rescaling the whole mesh ×3.7 changes it by **2.949e-15**. Three
planted controls all moved (+5 % on every thin edge: 52,539 of 52,684 cells; one
cell's edge doubled: rel 9.647; **cross-mesh**, the predictor fed T5b's geometry:
47,949 of 52,684). **A first control that permuted edge lengths was discarded by
its author as an exact symmetry of the formula that could never have moved.**

**Conclusion, measured:** on a Cartesian lab mesh the cell-determinant test
carries **no information the three edge lengths do not already carry**. It is
anisotropy, restated.

**SO T5f REGISTERS:**
- **the cell-determinant limb is REPORTED** — flagged-cell count and worst value
  printed beside the mesh record, never gating;
- **every other `checkMesh` limb is a HARD STOP**: a build reporting a failed
  check other than the determinant stops, is a finding, and goes to the
  supervisor — it is not worked around.

**Artifacts:** `verification/runs/T-family/T5d_runs/DETERMINANT_IDENTITY_2026-09-11/{IDENTITY_T5d_c.txt,COST_OF_FIX.txt,UNREACHABLE_228.txt}`.

---

## 7. RULE 4 — COMPLETION, AND RULE 3 — THE PLANTED ZERO

**Completion** is `CLAUDE.md` rule 4 unchanged and is not re-registered here:
`rc=0`; an `End` line; last time == `endTime`; fields `T U p_rgh alphat nut k
omega phi` present in **both** regions; `ExecutionTime` count == `round(endTime/deltaT)`;
and **every field at `endTime` newer than the case's own `0/T`** (the age guard).
A guard refuses a case where `0` or a time dir already exists. **Completion is
INFRASTRUCTURE and never voids physics, and physics never excuses an incomplete
run** (L-342 classes as T5e prints them).

**The planted zero** is exercised by both instruments and each **refuses rather
than degrades**. Limb A: `PLANT_OFFSET 1.234e-03`, `PLANT_SPIKE 9.876e+02`, read
back from disk with the **argmax question asked**. Limb B `--selftest`, measured
2026-09-12, `SELFTEST PASS (0 failed)`: B1 fires on a single planted cell **and
its argmax is the planted cell 437**; B2 fires on one cell planted at the measured
clamp floor **and its argmin is the planted cell 88**; **B2 discriminates** — a
cell 10× above the bar does not fire it, so B2 is not merely a test for "small";
and both negatives confirm the unplanted copy is unmoved.

---

## 8. RULE 12 — COST, AND AN HONEST SENTENCE ABOUT WHAT THE LAST ONE BOUGHT

**BASIS — MEASURED, on T5b's own triple**, the same mesh, the same cell counts,
the same solver, the same `endTime`, the same 1 rank, from
`T5b_runs/STATUS.T5_CUBE_{c,m,f}` (all `rc=0`, `capped=0`, `note=clean`):

| level | wall s | core-min |
|---|---:|---:|
| `c` | 1,007 | 16.783 |
| `m` | 5,252 | 87.533 |
| `f` | 20,851 | 347.517 |
| **total** | | **451.833** |

**POINT = measured × 1.15.** The 15 % is an **allowance, not a measurement**:
`limitedLinear` costs marginally more per face than `linearUpwind`, and
relaxation 0.5 → 0.3 changes the inner-loop work at a fixed 5,000 outer
iterations. No measurement on this box isolates either, and the figure is
declared an allowance rather than dressed up.

| level | POINT core-min | CAP core-min |
|---|---:|---:|
| `c` | 19.3 | **38.6** |
| `m` | 100.7 | **201.4** |
| `f` | 399.6 | **799.2** |
| **total** | **519.6** | **1039.2** |

**CAP = 2.0 × POINT**, contention headroom on a saturated box, not model
uncertainty. **An overrun STOPS the run; it does not get a new budget** (rule 12).
**$0.888 total at CAP, DERIVED and NEVER MEASURED** at $0.0513/core-h — this box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**AND THE SENTENCE THAT BELONGS IN A COST SECTION RATHER THAN A FOOTNOTE: T5b's
451.833 measured core-minutes bought three results that are now, by measurement,
`NOT A RESULT`.** T5f is asking for the same spend again on a changed setup. **If
limb B fails on all three levels, the honest reading is that this team has now
spent ~900 core-minutes on this ladder for no graded number, and the next move is
not a third solve.**

**Estimate-versus-actual is owed at completion**, per rule 12, as a row in
`docs/COST_CALIBRATION.md`. **The T5e row records a 47 % wall-time spread between
two byte-identical invocations of one deterministic comparator; this rung's
prediction should not be read as tighter than that.**

---

## 9. THE FREEZE SET

| file | sha256 (disk bytes; never a git blob SHA-1 — L-450) |
|---|---|
| `verification/runs/T-family/T5f_runs/t5f_convergence_gate.py` | `9c4049b69d64ee7d5462340ab5e26dee66633aabb0a44672749da031dec31fb3` |
| `verification/runs/T-family/T5e_runs/analyse_t5e.py` (limb A, frozen by T5e) | `c97d355d278b6523021d40a7a4925b8b9f3430bec25250b24238fdaa9daabfbc` |

**A DEFECT INHERITED WITH LIMB A, DISCLOSED BEFORE IT GRADES ANYTHING.**
`analyse_t5e.py`'s own mutation arms run children with `cwd=d` in a temp
directory, so `--selftest` reports **2 failed** (control arm, `-O` arm); driven
with `cwd=HERE` the unmutated control passes and six of eight arms reject on their
own reasons, **one mutation is inert by construction (N5)** and **one is a real
blind spot (N7 — the planted-zero arm's argmax predicate replaced by a tautology,
unseen)**. The one-word fix is proven and **deliberately not applied**: it is
routed to verification as a finding against another lane's file. **T5f inherits
that instrument in that state and says so here rather than letting a reader find
it.**

---

## 10. WHAT THIS RUNG CANNOT DO

- **It cannot settle the unequal region refinement ratios** (§3.1). That ruling is
  the supervisor's and is owed **before any T5f triple is graded**.
- **It cannot repair the `y+` mesh**, and does not try — T5e measured `y+` as
  `MET` on this mesh, so the motivation is gone.
- **It cannot tell "H1 refuted" from "limb B too tight" if all three levels fail
  limb B** — §4 and §5 register that ambiguity in advance.
- **It does not re-open T5, T5b, T5c or T5d.** T5d stays stopped on its own
  addendum.
- **It does not repair `analyse_t5e.py`.**
- **Nothing here is sent, filed, uploaded, registered, posted or commented
  outside this box** (rule 7).
