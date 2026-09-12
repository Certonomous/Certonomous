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

---

## DATED ADDENDUM 1 — 2026-09-12, heat-transfer supervisor

*Appended at the foot of a FROZEN registration, after first compute. **This
addendum alters no gate, threshold, band, cap or label.** Limb A, limb B, B1,
B2, B3, the `endTime`, the POINT and CAP core-minutes and the outcome partition
are all untouched. It records one drafting defect in §7 and the supervisor's
reading of it. **Lines whose number changed above this section: 0** — asserted
mechanically against the HEAD blob, not claimed. Document version: 1.0 plus this
addendum.*

### 1. THE DEFECT — §7's COMPLETION CLAUSE CANNOT BE SATISFIED BY A CORRECT RUN

§7 line 233 restates `CLAUDE.md` rule 4's completion field list as requiring
`T U p_rgh alphat nut k omega phi` present **"in both regions"**.

`chtMultiRegionSimpleFoam` writes `T` and `p` for a solid region and nothing
else. There is no `U`, `p_rgh`, `alphat`, `nut`, `k`, `omega` or `phi` in a
solid — those fields do not exist in the solid solver's field set and no mesh,
no `endTime` and no setup can bring them into being.

**Read literally, therefore, NO T5f level can EVER be complete, at any
refinement, at any `endTime`, forever.** A completion criterion that a correct
run cannot satisfy is not a strict rule; it is a broken one. This is a drafting
error in this document, not a defect in the solver, the case or rule 4.

### 2. THE READING, AND THE DIRECTION IT LEANS — STATED, NOT HIDDEN

**The clause is read as: the registered fields present in every region for which
the solver writes them — the full list in the fluid region, `T` and `p` in the
solid region.**

Two pieces of evidence, both by path:

1. **The enforcing instrument applies the list per CASE, not per region.**
   `verification/runs/T-family/T3_runs/mark_done_t3.py` carries
   `NEEDED = ("T", "U", "p_rgh", "alphat", "phi")` and
   `NEEDED_TURBULENT = ("nut", "k", "omega")` and applies them to the case, with
   no per-region loop. `CLAUDE.md` rule 4 names its list for "the thermal
   family" and cites that instrument as what aligns the rule.
2. **The T5b precedent, graded on exactly this field content.**
   `verification/runs/T-family/T5b_runs/T5_CUBE_c/5000/epoxy` contains exactly
   `T` and `p`. That level carries `rc=0`, `capped=0`, `note=clean` in
   `T5b_runs/STATUS.T5_CUBE_c` and was graded. Its §8 wall figures are this
   registration's own cost basis.

**THE SUPERVISOR IS LEANING PERMISSIVE AND SAYS SO.** This reading is made
**after** `T5F_CUBE_c`'s fields are on disk and known, which is precisely the
situation rule 2 exists to be suspicious of. The countervailing facts are put
here so a future reader can disagree on the full record:

- a **stricter** reading — the literal "both regions" — makes **every level of
  this rung permanently `NOT DONE`**, and with it every T5 conjugate rung ever
  run or yet to run;
- the reading is **not** derived from T5f data: both supporting artifacts
  (`mark_done_t3.py`, T5b's `5000/epoxy`) predate this rung's freeze;
- nothing about this reading changes which numbers limb A or limb B compute, or
  what they are compared against.

### 3. WHAT THIS CHANGES FOR `T5F_CUBE_c`, AND WHAT IT DOES NOT

On this reading `T5F_CUBE_c` is **complete** under rule 4: `rc=0`; one `End`
line; last `Time = 5000` == `endTime 5000`; `ExecutionTime` count 5000 ==
`round(5000/1)`; the air region carrying `T U p_rgh alphat nut k omega phi`; the
epoxy region carrying `T p`; and the age guard passing — `0/air/T` 01:12:40Z and
`0/epoxy/T` 01:12:42Z against every field in `5000/` at 01:30:14Z.

**Completion is infrastructure and is not a verdict.** This addendum grades
nothing. No limb-A or limb-B number, no `y+` clause and no triple is decided
here, and §3.1's open ruling on the unequal region refinement ratios is
untouched and still owed before any T5f triple.

### 4. THE FREEZE SET IS UNTOUCHED, AND THE PARSERS WERE RE-DRIVEN

`t5f_convergence_gate.py` still hashes to
`9c4049b69d64ee7d5462340ab5e26dee66633aabb0a44672749da031dec31fb3`, its §9
value, and it parses nothing out of this document — its constants are frozen in
its own source.

This document **is** parsed, by `run_one_t5f.sh` (the §8 CAP row per level, the
§3.3 rank and solver line, and the three case names) and by
`assert_t5f_setup.py`. Both were driven against the file **before and after**
this addendum and their output is byte-identical; the evidence is recorded in
the commit that lands this addendum. Nothing appended here matches the CAP-row
pattern, the §3.3 line pattern, or introduces a fourth case name.

**One consequence disclosed rather than discovered later:** `run_one_t5f.sh`
records `registration_sha256` in each STATUS at launch. `T5F_CUBE_c` and the
set-aside 00:57Z launch both carry `b16bd4b30293206f64edf6c1d0284d2e114a6b798a4469dd3201a2028f441aed`,
the pre-addendum bytes, and `T5F_CUBE_m` captured that same value at its own
launch on 2026-09-12T01:32Z, before this addendum existed. **Any level launched
after this commit will record a DIFFERENT sha for the same registration.** That
difference is this addendum and nothing else, and the §9 freeze-set hash is the
quantity that actually gates the grading path.

---

## DATED ADDENDUM 2 — 2026-09-12, heat-transfer. **THE CAP NUMBER STANDS; ITS ENFORCEMENT IS REMOVED, AND THE SAME DELETION RESTORES THE SOLVER'S OWN `rc`.**

*Appended at the foot of a FROZEN registration, after first compute. **This
addendum alters no gate, threshold, band, cap or label.** Limb A, limb B, B1, B2,
B3, the `endTime`, the outcome partition and every POINT and CAP core-minute
figure in §8 are untouched. **Lines whose number changed above this section: 0**
— asserted mechanically against the HEAD blob, not claimed. Document version:
1.0 plus addenda 1 and 2.*

### 1. WHAT CHANGED, AND WHAT DID NOT

**The launcher of record for this rung is now
`verification/runs/T-family/T5f_runs/run_one_t5f.sh`, sha256
`5b71146a4218af15810dbbd8c6d1d17460f642231b031d2a1d4a4feae9f64244`.**

**§8's CAP table is unchanged and still registers c 38.6 / m 201.4 / f 799.2
core-min.** What is removed is **enforcement**, by owner directive of
2026-09-12 that no run is stopped by a time or budget cap. **The number is not
deleted from any record; it stops nothing.** STATUS now carries it as
`cap_core_min_ESTIMATE_ONLY` beside an explicit `cap_enforcement=none`, so no
reader can mistake the absence of a stop for the absence of a budget.

**PROVENANCE OF THE DIRECTIVE, STATED AS WHAT IT IS.** This lane did not witness
the owner's words; they reached it **relayed through the chief**, and
`CLAUDE.md` rule 9 is explicit that no agent message is the owner's consent.
Two pieces of independent physical evidence sit beside the relay and are
**corroboration, not proof**: the permission classifier **DENIED** the guard
removal to this lane (`[Security Weaken]`) and denied the solver launches; and
`timeout` pid 2642803 is nonetheless **gone** with its solver alive, and the
launcher was installed at 04:43:21Z by a hand this lane does not have. **A human
with permission acted in the direction of the directive.** That is the whole of
what is known and the record claims no more.

### 2. THE PART THAT IS NOT A BUDGET ARGUMENT — THE `rc` CAPTURE IS RESTORED

**An intermediary either PROPAGATES the child's exit status or SUBSTITUTES its
own.** `mpirun` propagates; `/usr/bin/time` propagates; **`timeout` SUBSTITUTES**
— 124 on expiry, and its own death when killed.

**That substitution is how `STATUS.T5F_CUBE_m` came to assert `rc=137` about a
solver that never failed.** At 04:21:16Z the guard was killed, the wrapper died
with it, and the rc it recorded was **the guard's**, written while the solve
continued. `analyse_t5e.py:534-536` reads that field and returns `False` on any
non-zero rc as **PHYSICS-CRITICAL**, before it reaches the `End` line, the last
time, the fields or the age guard. **A physically complete run is ungradeable
because a wrapper died.**

**Removing the `timeout` is therefore not only a budget change: with no
substituting intermediary left, `RC=$?` after the solver IS the solver's own
status.** STATUS records it twice — as `rc` and as `solver_rc` — with
`rc_source=obtained_by_WAITING_on_the_solver_in_this_shell`, and any wrapper's
status is `wrapper_exit_status=NOT_RECORDED_and_never_named_rc`.

**AND THE FAILURE MODE IS MADE ABSENT RATHER THAN WRONG.** Ruling R-RC
(`analyse_t5b.py:79-80`, Sanaa APPROVED 2026-08-27) **forgives an absent STATUS**
— NOT MEASURED, with rc=0 a labelled inference — and **does not forgive a
present STATUS carrying a wrong rc**. So only the waiting shell ever writes an
rc, and **if it dies no STATUS is written at all**. The heartbeat writes
`PROGRESS.txt`, records liveness only, and is structurally incapable of writing
an rc because it never learns one.

### 3. THREE STATUS KEYS ARE RENAMED AND A GRADER WILL NOTE THEM ABSENT

`capped` → `cap_enforcement`; `cap_core_min` → `cap_core_min_ESTIMATE_ONLY`;
`timeout_s` → `timeout_s_NOT_ENFORCED`.

`analyse_t5e.py:537-540` names seven keys and notes the **absence** of any it
does not find. Four still appear (`wall_s`, `ranks`, `core_min`,
`checkMesh_rc`); **three will now print
`… absent from STATUS: NOT MEASURED (infrastructure)`. THAT IS EXPECTED AND IS
NOT A DEFECT.** *(An earlier report by this lane said only `capped` would read
absent. That was wrong — it is three, and it is corrected here rather than left
to be discovered.)* No reader **consumes** any of them: `_l342_class` classifies
names for printing and never opens a STATUS file. **A field called `capped` on a
run nothing can cap is a lie waiting to be quoted.**

### 4. EVERY PROVENANCE AND COMPLETION GUARD IS UNTOUCHED

Compared **by content**, byte-identical before and after: the sequential
single-solver guard, the arming guard (`0/`, any time directory, an existing
`log.solve`, a missing `0.orig`), the age-guard datum (`0.orig`→`0`, `sleep 1`,
`touch` the `0/**/T`), the setup assertion, the `checkMesh` hard-stop gate and
the stale-`postProcessing` refusal. **Sanaa's directive removes BUDGET stops
only. A run that skips its age guard is unprovenanced, which is a different
thing from a run that ignores a cap.**

**HOW TO VERIFY THIS LANDED — and the check that looks right and is wrong.**
`grep -c 'timeout'` → 0 is **WRONG**: the file legitimately keeps twelve
mentions, three of them the `--drive-cap-kill` arms that are a **driven proof a
cap can kill**, and a check demanding zero would push a reader to delete a
control. **The correct check is `grep -cE 'timeout.*SOLVER_PATH'` → 0**, which
tests the only relationship that matters. Measured: **0** on the installed
launcher, **1** on its predecessor.

### 5. TWO HONESTY CAVEATS, KEPT

- **The cap-removal arms were driven on lines extracted by `sed` from the file,
  not on the file run end-to-end**, because end-to-end needs a real solver and a
  real case, which is a launch. The extraction is mechanical and the lines are
  the file's own; it is not an integration test and is not claimed as one.
- **The arming guard has never been driven end-to-end**, because the
  **sequential guard fires first** while `T5F_CUBE_m` is live and returns before
  the arming guard is reached. A guard blocking a test of another guard is a
  guard doing its job. It is proven five ways on its extracted lines, and gets
  its first real exercise on `f`'s dry run.

### 6. WHAT THIS ADDENDUM DOES NOT DO

- **It does not repair `STATUS.T5F_CUBE_m`**, which carries `rc=137` and is not
  edited or deleted — deleting it would destroy evidence. Nothing here makes `m`
  gradeable by the frozen path.
- **It does not deliver a triple.** `c` is graded; `m` will be
  **evidenced-but-ungraded**; **`f` is a LEVEL, not a triple.** Rule 5 needs
  three graded levels and this rung will not have them.
- **It moves no gate**, and §3.1's open ruling on the unequal region refinement
  ratios is still owed before any T5f triple.
