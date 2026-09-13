# Curriculum D6R2C — PRE-REGISTRATION for after-item 8, RUNG 1 (MESH): arm `DEC5`

**Item id:** `D6R2C-AFTER8-R3`. Successor to `DEC4` (`NOT A RESULT`, stalled at state `S`).
**Version 1.0 — DRAFT, NOT YET FROZEN.** Written 2026-09-13 by a dafoam `lab-lane` for
`dafoam-supervisor`. **This lane did not write the `DEC4` registration; it ran it.**
**This item has burned 0 core-min, started 0 containers and generated 0 meshes at the time of writing.**
It is frozen by the commit that introduces this file **together with its instruments** (§9).
**No container starts until that commit exists** (`CLAUDE.md` rule 2).
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7).
**No frozen file is edited** (rule 6).

---

## 0. WHY THIS RUNG, AND WHY NOW

Sanaa's rule 13: **two stops on the same cause means climb — mesh, then numerics, then model.** The
climb is the rule, not a decision to refer.

| stop | arm | state | primal's final residual | against |
|---|---|---|---|---|
| 1 | `DEC3` | `S` | **`1.0912e-05`** | `primalMinResTol = 1.0e-8` |
| 2 | `DEC4` | `S` | stalled again, after the registered incidence continuation ran | same |

**`DEC4` is measured, not assumed, on two points that matter here.** Its states `B` and `T` reproduced
`DEC3` **bitwise** — `J_B = 3.064250791464e-02`, `J_T = 3.161324957616e-02` — and its governor counter
**read** (`n_trim = 2` at `B`, `14` at `T` against `TRIM_MAX_EVALS = 15`), so the §2b defect find is
repaired and the continuation worked mechanically. **It did not prevent the stall.** Two stops, same
cause, same state. We are on the mesh rung.

**WHAT IS ALREADY REFUTED AND IS NOT RE-TESTED HERE.** `FINDING_NOTE_D6R2C_LAYER_GROWTH.md` measured
the fresh and base meshes' wall-normal growth ratios as **median `1.330314` vs `1.330151` — 0.012 %
apart** — and their `faces.gz`, `owner.gz`, `neighbour.gz` and `boundary` as byte-identical. *"The fresh
mesh carries a defect the base does not"* is **dead**, and this registration does not revisit it.

**WHAT IS STILL OPEN, AND IS THIS ITEM'S ONE CHANGE.** Both meshes grow at **~1.33 per layer**, with
**69.66 % of cell pairs above 1.30 and 98.73 % above 1.20**, against a boundary-layer practice of
1.1–1.2. That is the family script's extrusion; it is in the mesh `O_mp` ran on; and it is the best
standing candidate for why this configuration stalls **at all**.

---

## 1. THE ONE CHANGE, AND THE PROOF THAT IT IS ONE

**Change `N` in the family script's pyHyp options from `39` to `62`. Nothing else moves.**

`s0 = 1.0e-3`, `marchDist = 300.0`, `cMax = 0.1`, `unattachedEdgesAreSymmetry`, `outerFaceBC`,
`autoConnect`, `families`, and every commented pseudo-grid and smoothing option stay **exactly** as the
family script has them. Same design vector `s*`/`t*`, same three conditions and CL targets, same
solver, same `primalMinResTol`, same `TRIM_TOL`, same weights.

**THE PROOF IS EXECUTABLE, NOT PROSE.** The registered instrument `d6r2c_dec5_genwingmesh.py` is a copy
of `/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing/genWingMesh.py`
(md5 **`dab5e959187ab2e2bfb4e2c0ded0feb6`**, unchanged and never edited — rule 6) with one line altered.
`guard_freeze` **runs `diff` between the two and refuses (exit 4) unless the diff is exactly one changed
line, and that line is the `N` line.** A one-parameter claim that is asserted rather than checked is
exactly the family of defect §8c was written for.

```
-    "N": 39,  # number of layers to march
+    "N": 62,  # number of layers to march   (D6R2C-AFTER8-R3 §1: THE ONE CHANGE)
```

---

## 1a. WHERE `62` COMES FROM — DERIVED, NOT CHOSEN

**Step 1 — the model, and it is VALIDATED against the measurement before it is used.** A geometric
wall-normal march of `n` cells from first height `s0` at ratio `r` reaches
`s0 (r^n − 1)/(r − 1)`. The family runs `N = 39` **layers of points**, i.e. **38 cells per chain**.

- **Topology check, exact:** 1008 wall faces × 38 cells = **38,304** — the mesh's measured cell count,
  and 1008 × 37 = 37,296, the finding note's measured pair count. The model has the geometry right.
- **Ratio check:** solving `s0 (r^38 − 1)/(r − 1) = 300.0` gives **`r = 1.356247`** against a
  **measured** base median of **`1.330151`**. **The model overshoots by 1.962 %.**

**THAT 1.962 % IS DISCLOSED, NOT ABSORBED.** pyHyp's march is hyperbolic with `cMax` limiting and
smoothing, not a pure geometric series, so the model is an *upper* estimate of the ratio. It is used
only to choose `N`, and **the achieved ratio is MEASURED on the generated mesh and gated (`M1`, §3)** —
never assumed from the model.

**Step 2 — the target.** The hypothesis under test is that the ratio is outside boundary-layer practice.
The finding note states that practice as **1.1–1.2** (§3). **`1.20` is the upper edge of that range,
and therefore the SMALLEST change that brings the mesh inside it.** Choosing 1.15 or 1.10 would be a
larger intervention than the hypothesis requires and would cost 2.03× and 2.87× the cells respectively.
**This is a minimum-intervention derivation; the number is round only because the practice bound it is
taken from is round.**

> **`GROWTH_TARGET = 1.20` IS DECLARED, NOT MEASURED.** This lab has not independently established the
> 1.1–1.2 practice range; it is inherited from the finding note, which states it without a measurement
> of its own. It is labelled **DECLARED** everywhere it appears, exactly as `FM_BAND_ABS` was. Declaring
> a number honestly is the alternative to choosing one after seeing the answer.

**Step 3 — `N` follows by arithmetic, with no freedom left.** The smallest `n` with
`s0 (r^n − 1)/(r − 1) ≥ 300.0` at `r ≤ 1.20` is **`n = 61` cells**, giving **`N = 62` layers** and a
model ratio of **`1.197394`**. Total cells **1008 × 61 = 61,488 = 1.6053 × the base**.

| target `r` | cells/chain | `N` | model ratio | total cells | × base |
|---|---|---|---|---|---|
| ≤ 1.30 | 44 | 45 | 1.295533 | 44,352 | 1.158 |
| ≤ 1.25 | 51 | 52 | 1.245790 | 51,408 | 1.342 |
| **≤ 1.20** | **61** | **62** | **1.197394** | **61,488** | **1.6053** |
| ≤ 1.15 | 77 | 78 | 1.149217 | 77,616 | 2.026 |
| ≤ 1.10 | 109 | 110 | 1.099104 | 109,872 | 2.868 |

**Every row is in the table so a reader can see the choice was made from a range, not from one number.**

---

## 2. THE PREDICTION, STATED BEFORE THE RUN SO IT CAN REFUTE ITSELF

> **If the aggressive wall-normal growth ratio is the cause of the stall, state `S`'s primal converges to
> `primalMinResTol = 1.0e-8` where it stalled at `1.0912e-05`. If it stalls at a similar floor, the mesh
> rung is EXHAUSTED and the ladder climbs to numerics.**

**`P1` — MESH RUNG IMPLICATED.** Every state's primal reaches `primalMinResTol = 1.0e-8` (no stall at
any state, `S` included).

**`P2` — MESH RUNG EXHAUSTED.** State `S`'s primal stalls with final residual **`> 1.0912e-06`** — the
floor has moved by **less than one decade** from the measured `1.0912e-05`. **On `P2` this registration
declares the mesh rung closed and the next rung is numerics.** The `FM8` field-transfer instrument —
proved an hour ago to make a fresh-mesh primal converge where it had stalled twice — is the obvious
rung-2 candidate and **is deliberately not this registration's change.**

**`P3` — PARTIAL, REPORTED, NOT A RUNG DECISION.** State `S` stalls with final residual
**`≤ 1.0912e-06` and `> 1.0e-8`**: the ratio is implicated but the intervention was insufficient.
Reported with the achieved floor and the achieved ratio; **the ladder decision on `P3` is the
supervisor's and this document does not pre-empt it.**

**The one-decade boundary of `P2` is DECLARED, not measured**, and is labelled so wherever it appears.
It is registered now precisely so that "a similar floor" cannot be argued about afterwards.

**A RUNG THAT CANNOT BE EXHAUSTED BY ITS OWN RUN IS NOT A RUNG.** `P1`/`P2`/`P3` are exhaustive over the
real line above `1.0e-8` and `P2` is reachable, so this run can close its own rung. That is the point of
registering the disjunction rather than only the hope.

---

## 3. THE GATES

Graded by **`d6r2c_dec5_grade.py --item 8`**, after the container exits.

- **`M1` — THE MESH IS THE MESH THIS DOCUMENT DERIVED.** The generated `constant/polyMesh` has
  **1008 × 61 = 61,488 cells** and **1008 wall faces**; the wall-normal marching finds **1008 chains of
  exactly 61 cells**; and the **measured median growth ratio is `≤ GROWTH_TARGET = 1.20`**. Measured by
  the finding note's own method (§2 of that note: march each chain off the `wing` patch through opposite
  hexahedron faces). **A miss on any limb is `NOT A RESULT` with the achieved value printed** — the
  intervention did not happen and nothing downstream means anything.
- **`M2` — THE ONE-CHANGE PROOF.** `diff` between `d6r2c_dec5_genwingmesh.py` and the family script at
  `dab5e959187ab2e2bfb4e2c0ded0feb6` is **exactly one changed line, and it is the `N` line**; the family
  script's own md5 is asserted **unchanged** before the diff is taken. `rc = 0` for the mesh step.
- **`D1` — EVERY TRIMMED STATE IS AT MATCHED LIFT.** `max_i |CL_i − target_i| ≤ TRIM_TOL = 1.0e-6`, with
  `TRIM_MAX_EVALS = 15` **in the governor's own unit — `run_model` calls per state, not distinct
  incidences per condition** (see §4). **A null trim count is `NOT A RESULT`**, inherited from `f23bab95`.
  `TRIM_TOL` **is never widened** — registered prohibition.
- **`D3` — THE ACCOUNTING CLOSES.** `|(Δ_shape + Δ_twist + Δ_trim) − (J_opt − J_B)| ≤ CLOSE_TOL`,
  inherited unchanged at `8.423462e-15`. An arithmetic identity on a floating-point band, registered as
  such and **not presented as a physics test**.
- **`D4` — THE SPLIT IS ORDER-INDEPENDENT ENOUGH TO BE CALLED A SPLIT.** `INTERACT_TOL = 0.10`,
  inherited unchanged. `DECLARED, not measured`, as in the parent.
- **`D6` — COMPLETION AND HYGIENE.** `rc = 0`; all six states present with `fail = 0` and finite `J` and
  `CL`; **each primal converged to `primalMinResTol = 1.0e-8` or its residual recorded and the state
  graded `NOT A RESULT`**; every artefact newer than the arm's own age datum (`0/U`); **zero** files
  under the arm directory newer than the datum owned by uid 0 or gid 0; the §6 cap reported.

**LABELS.** `PASS` = `M1∧M2∧D1∧D3∧D4∧D6`. `GATE FAIL` = `M1∧M2∧D1∧D3∧D6` hold and `D4` misses.
`NOT A RESULT` = `M1`, `M2`, `D1`, `D3` or `D6` fails. **No other label, no synonyms** (rule 1).
**No Roache triple is claimed and no GCI is quoted** — rule 5 does not apply and nothing here will be
dressed as grid convergence. See §5.

---

## 3a. `D2` CANNOT BE CARRIED FORWARD, AND THIS DOCUMENT SAYS SO RATHER THAN PRETENDING

**`D2` is dropped, and its loss is the most important thing in this registration.**

`DEC4`'s `D2` compares `J_B` against the inherited `J0 = 0.0306416314389976151` within
`REPRO_TOL = 1.7162447e-04` relative. **`J0` was produced on the 38,304-cell mesh. This arm runs on a
61,488-cell mesh. `J_B` will differ from `J0` by a DISCRETISATION amount, which is the very thing this
arm changes** — and a drag coefficient shifting by O(1 %) between those two meshes would exceed
`REPRO_TOL` by a factor of order 58. **`D2` would fail by construction, and a gate that must fail is not
a gate.**

**IT IS NOT REPLACED BY A LOOSENED VERSION.** Widening `REPRO_TOL` to whatever the new mesh happens to
produce is choosing a number to fit an answer. **`D2` is struck for this arm, with its reason, and the
external anchor it provided is replaced by three clauses that are anchored OUTSIDE this run** (§8c's
requirement):

1. **`M1`'s growth-ratio limb** — anchored to the measured base median **`1.330151`** and to
   `GROWTH_TARGET = 1.20`, neither of which this run produced.
2. **`M1`'s topology limb** — anchored to the **1008** wall faces registered in the parent's §9a and
   measured independently in the finding note, which this run did not produce.
3. **`D1`'s CL targets** — `0.400 / 0.500 / 0.600`, external, fixed, and gated.

**AND THE QUANTITY `D2` USED TO PROTECT IS STILL REPORTED, NEVER GATED.** `|J_B − J0| / J0` is printed
beside the table as **the measured discretisation shift between the two meshes at the identical
baseline design point** — which is a number this family has never had. **It is REPORTED, NOT GATED**, it
is **not** a GCI, **not** an observed order, and **not** a grid-convergence claim (§5).

---

## 3a.1 A CORRECTION TO §3a ABOVE — `D2` IS NOT STRUCK WHOLE. ITS SHARPEST LIMB IS MESH-INDEPENDENT AND IS KEPT AT FULL TIGHTNESS

**§3a said "`D2` is struck". That was too broad, and reading the instrument rather than the registration
is what corrected it.** `D2` is a conjunction of five limbs, and **they do not all depend on the mesh**:

| limb | quantity | mesh-dependent? |
|---|---|---|
| `rel_B` | `\|J_B − J0\|/J0` | **YES** — a CFD output |
| `rel_O` | `\|J_opt − Jf\|/Jf` | **YES** — a CFD output |
| `B_CL`, `O_CL` | the inherited `CL`s at `n = 2` and `n = 88` | **YES** — CFD outputs |
| **`D2GEO`** | **`thickcon` and `volcon` at both anchored states, against the inherited md5-pinned records, at `GEO_TOL = 1.0e-12`** | **NO** |

**`thickcon` and `volcon` are pyGeo outputs.** `d6r2c_dec4_grade.py:252` says so in its own words —
*"thickcon and volcon are pyGeo outputs — pure"* — they are computed by `DVCon` from the **FFD-deformed
surface**, and **the CFD volume mesh is not an input to them.** Changing `N` from 39 to 62 changes the
volume mesh and **cannot change them at all.**

> **`D2GEO` IS THEREFORE CARRIED FORWARD UNCHANGED, AT `GEO_TOL = 1.0e-12`, AND IT IS THE REAL
> REPLACEMENT FOR WHAT `D2` WAS DEFENDING.** It is anchored to the inherited, md5-pinned
> `d6r2c_evals.jsonl` — outside this run — and it is the **sharpest scaler-class defect detector in the
> instrument: `thickcon` and `volcon` are normalised to ≈ 1.0, so a `shape` installed ten times too
> large moves them by order 100 %, which is TWELVE DECADES outside `GEO_TOL`.** No widening, no
> re-derivation, no sanity band — the tight gate survives the mesh change intact because the quantity it
> reads does.

**WHAT IS STRUCK IS NARROWER THAN §3a CLAIMED:** the two `J` limbs and the two `CL` limbs, all four of
them CFD outputs that the mesh change moves by construction. **§3a's reasoning stands for those four and
is wrong for `D2GEO`; the original text is left above, struck here rather than rewritten** (rule 2).

---

## 3b. `M3` — THE WIDE SANITY NET OVER THE FOUR MESH-DEPENDENT LIMBS

**`M3` is `D2`'s two `J` limbs re-banded, not a new gate** — and it is the SECOND line of defence, not
the first. **`D2GEO` (§3a.1) is the first.** `M3` exists because a defect that somehow left the pyGeo
constraints intact would still have to produce a plausible drag.

### 3b.1 WHICH END CARRIES THE DISCRIMINATING POWER — AND IT IS NOT `J_B`

**A sanity gate on `J_B` alone would be structurally blind to the defect it is meant to catch.** At
state `B`, `shape ≡ 0` and `twist ≡ 0`, and **zero times a wrong scaler is still zero.** This is the
identical blindness the runscript's own ADDENDUM 1 records for the `KR_RES` guard — *"of the 109 DV
components, 103 are EXACTLY ZERO at x0 … all of the discriminating power lived in the 6 non-zero
components"* — and the identical blindness that let the scaler defect through `H1` in item 9.

**`D2` already had both ends** (`rel_B` and `rel_O`, `d6r2c_dec4_grade.py:505-506`); a replacement
specified at the `J_B` end alone would have **dropped the discriminating one.** `M3` keeps both:

- **`M3a`** — `|J_B − J0| / J0 ≤ SANITY_BAND`. Both DV vectors are zero here; this end tests the
  **mesh**, not the design.
- **`M3b`** — `|J_opt − Jf| / Jf ≤ SANITY_BAND`, with `Jf = 0.0230632595286777639`. Here
  `shape = s*`, `twist = t*`, `AoA = a*`, all non-zero. **This is the end a scaler-class defect cannot
  hide from.**

### 3b.2 `SANITY_BAND = 0.123661365`, DERIVED FROM TWO MEASURED ANCHORS

| anchor | value | what it is |
|---|---|---|
| **physics scale** (must PASS) | `\|J_T − J_B\|/J_B` = **`0.031680`** (3.1680 %) | the largest **measured** shift in `J` from a full registered design-variable change at matched lift — `DEC3` and `DEC4`, bitwise identical |
| **defect scale** (must FAIL) | `\|Jf − J0\|/J0` = **`0.247323`** (24.7323 %) | the **measured** full-design change. A scaler defect applies a design an **order of magnitude larger**, so this is a **LOWER BOUND** on the defect's shift, not an estimate |

```
SANITY_BAND = 0.5 × 0.247323  =  0.123661365
    3.904× headroom ABOVE the measured physics scale
    2.000× margin  BELOW the measured lower bound on the defect scale
```

**The geometric mean of the two anchors, `0.088516`, was computed and REJECTED**: it leaves only 2.79×
over the physics scale, and the physics side is the side this arm deliberately perturbs. **Both
candidates are shown so the choice is visibly made from a range.** The factor `0.5` is **DECLARED, NOT
MEASURED**, and is labelled so wherever it appears.

### 3b.3 HOW A `M3` MISS IS TOLD APART FROM A DEFECT — FREE, AND REGISTERED IN ADVANCE

**If the wall-normal refinement genuinely shifts `J` by more than 12.366 %, `M3` fails a legitimate run.
That outcome is not a flaw in the gate — it is the finding that the base mesh was badly under-resolved**,
which is this item's own hypothesis arriving by another route. The two cases are distinguishable **at no
extra cost**, because `M3` is evaluated at both ends:

- **BOTH ends shift by a similar amount** → a **discretisation** shift, which moves the baseline and the
  optimum together. Graded `NOT A RESULT` with both shifts printed, and reported as a finding that the
  `N = 39` mesh was under-resolved at the 12 % level.
- **ONLY `M3b` shifts** → the design vector is wrong where the design is non-zero and right where it is
  zero. That is the **signature of a scaler-class defect**, graded `NOT A RESULT`, escalated as a
  producer defect, and **not** reported as a mesh finding.

**Registering the discriminator before the run is the whole point**: without it, a single number would
have been argued about afterwards.

**`M3` IS A SANITY GATE AND IS LABELLED ONE EVERYWHERE.** It carries no precision claim, it is not a
reproduction control, and **it must never be quoted as agreement between the two meshes.** The precise
quantity stays reported and ungated (§3a).

---

## 4. `TRIM_MAX_EVALS = 15`, RE-DERIVED IN THE GOVERNOR'S OWN UNIT

The parent's §2b found the old cap **inert**: it tested `prob.model._nl_solver_evals`, which was absent,
so every `DEC3` state recorded a null count and the branch was never entered. `f23bab95` repaired it and
**`DEC4` proved the repair by reading `n_trim = 2` at `B` and `14` at `T`**.

**The unit is `run_model` calls per state, not distinct incidences per condition, and this document
states that explicitly because the two differ and the old defect lived in the gap between them.**
Retained at **15** on `DEC4`'s own measurement: `B` used 2, `T` used **14** — within the cap, and close
enough to it that lowering the cap would risk refusing a state that converges. **A null count remains
`NOT A RESULT`.**

---

## 5. WHAT THIS ITEM IS NOT

**IT IS NOT A GRID-CONVERGENCE STUDY AND NO GCI IS QUOTED FROM IT.** Two meshes at two different
wall-normal resolutions is not a Roache triple; there is no third level, no observed order and no
monotonicity claim. The `|J_B − J0|/J0` number of §3a is a **two-mesh difference**, reported, and rule 5
does not apply to it because nothing here is presented as grid convergence. Anyone quoting it as a
discretisation uncertainty is misusing it.

**IT IS NOT A REPAIR OF `primalMinResTol`.** That tolerance is untouched and **will not be loosened to
make anything pass** — on `P2` the honest outcome is that the rung is exhausted, not that the bar moves.

**IT DOES NOT RE-GRADE ANYTHING.** `O_mp` stands at `GATE FAIL`; `DEC`, `DEC2`, `DEC3`, `DEC4`, `FM3`,
`FM4`, `FM5` stand at `NOT A RESULT`.

---

## 6. COST, FROM MEASURED ANCHORS, BEFORE THE RUN (rule 12)

**Measured anchors, both from `DEC4`'s own record, both at 4 ranks:**

| anchor | value | where measured |
|---|---|---|
| state `B`, 3 `run_model` calls (2 trim + 1 final) | **117.0 s wall → 39.0 s per call** | `DEC4/d6r2c_dec4.jsonl`, `STATE B` |
| state `T`, 15 `run_model` calls (14 trim + 1 final) | **965.8 s wall → 64.39 s per call** | same, `STATE T` |
| whole `DEC4` arm, `B` + `T` + a failed `S` | 1331 s wall = **88.733 core-min** | `ledger.txt` |

**Planning figure: 65 s per `run_model` call on the 38,304-cell mesh** — the measured 64.39 rounded
**up**, stated as rounded up so the estimate is conservative rather than flattering.

**Scaling to the new mesh: × 1.6053**, the cell ratio. **THIS IS THE ESTIMATE'S WEAKEST ASSUMPTION AND
IT IS NAMED.** Primal cost per iteration is roughly linear in cells, but the **iteration count** on a
gentler mesh is not measured and could move either way — a better-conditioned pressure equation could
converge in fewer iterations, which would make this an over-estimate. **It is not measured, it is
labelled an assumption, and it is bounded by the cap rather than trusted.**
→ **104.3 s per `run_model` call** on the 61,488-cell mesh.

| line | calls | s/call | wall s |
|---|---|---|---|
| `B` (trimmed) | 3 | 104.3 | 313 |
| `T` (trimmed) | 15 | 104.3 | 1564 |
| `S`, `F`, `B2` (trimmed, 10 each assumed) | 30 | 104.3 | 3129 |
| `O` (untrimmed) | 1 | 104.3 | 104 |
| mesh generation (pyHyp at 61 layers + `plot3dToFoam`/`autoPatch`/`createPatch`/`renumberMesh`) | — | — | 120 |
| cold preamble (container, 3 case copies, 3 `decomposePar`) | — | — | 180 |
| **TOTAL** | **49** | | **5410** |

**PREDICTION: 5410 s × 4 / 60 = `360.7` core-min.**
**REGISTERED CAP, `CAP_FACTOR = 3.00`: `1082.1` core-min.**

**Derived dollars.** `360.7 core-min = 6.011 core-h × $0.0513 = $0.308`; cap `$0.925`.
**DERIVED, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5);
`cost_basis` class **reported-by-owner** at the owner-stated c7a.4xlarge rate.

**Worst case, bounded not trusted:** five trimmed states at the full `TRIM_MAX_EVALS = 15` plus one
final call each, plus `O`, is `5 × 16 + 1 = 81` calls = 8448 s + 300 s = **583.2 core-min — inside the
1082.1 cap.** The cap is therefore reachable only through contention, not through this misprediction.

**THE CAP REPORTS; NOTHING KILLS ON IT** (directive #17). A crossing writes
`D6R2C_DEC5_CAP_CROSSED`, the row is graded **`NOT A RESULT`**, and **the cap is never raised**.

**Calibration row OWED** to `docs/COST_CALIBRATION.md` at completion — actual against the 360.7, the
ratio, and contention / waste / misprediction attributed **separately** (rule 12).

**Spend already incurred against after-item 8, carried forward and NEVER merged into this figure:**
`DEC` 0.533, `DEC2` 14.800, `DEC3` 63.000, `DEC4` 88.733 core-min. `DEC` and `DEC2` are
**defect-attributable waste**; **`DEC3` and `DEC4` are not** — each falsified something.

---

## 7. PLACEMENT, RANKS, MEMORY

`RANKS = 4`; `CPUSET = 2,3,4,5`; `--user 1000:1000 --group-add 1002`, `-e HOME=/tmp`, **never root**;
detached, PPID 1; **no `timeout` anywhere** and the container prints
`D6R2C_DEC5_DEADLINE_IN_CONTAINER_S: NONE`.

**Memory: `--memory=32g --memory-swap=32g`, declared `memory_footprint_gb = 28`.** Raised from the
parent's 20 g / 17 GB **in proportion to the 1.6053× cell count** (17 × 1.6053 = 27.3, rounded up to 28),
because a footprint registered for a smaller mesh is a registration that does not describe the run.

**Run root, NEW and separate:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER8R3-a2-wing-gentler-layers`
The `DEC4` and `D6R2C` roots hold graded artefacts and are in `FORBIDDEN_ROOTS`.

**GUARDS CARRIED FORWARD BY CALLING THEM, NEVER BY RE-SPELLING THEM** (L-221/L-222):
- the **per-process swap guard** — `swap_offenders()` from `scripts/queue_runner.py`, **imported and
  called**, solver processes only, threshold `VmSwap > 0`, offenders named with pid and kB, and the
  guard **refuses if it cannot import** rather than passing quietly;
- the **dependency-closure guard** — **RESOLVED, see §7a.**

---

## 7a. THE DEPENDENCY-CLOSURE GUARD — EXTRACTED, PROVED IDENTICAL, AND ONE PROPERTY OF IT REPORTED

**It was not callable.** It is a shell function inside `d6r2c_fm6_run_arm.sh`, which is **frozen and has
already run compute**. Sourcing that file would execute its top-level code; editing it would touch a
frozen instrument (rule 6). So it is **extracted**, not re-spelled and not sourced in place:

**`d6r2c_guard_deps.sh`** (md5 **`1de7fcd349b7227a49a008f180f909cc`**) carries `guard_deps()` as the
**verbatim bytes of lines 189–222** of `d6r2c_fm6_run_arm.sh` (md5
`cead1008eeb4d151c0ccddae2653d64b`, committed at HEAD). One definition; every launcher from here on
sources it.

**THE EQUALITY IS PROVED, NOT ASSERTED** — and re-checked as a guard at run time:

```
sed -n '189,222p' d6r2c_fm6_run_arm.sh        -> e4fe26ad6e29900ce4b67255c9ddc9c1
the function body inside d6r2c_guard_deps.sh  -> e4fe26ad6e29900ce4b67255c9ddc9c1   BYTE-IDENTICAL
```

The PASS banner still reads `D6R2C_FM6_G_DEPS_PASS`. **That is deliberate:** it is the origin's own byte,
and changing it would make the copy differ from the file it claims to be. The banner names its origin.

**FAILING CONTROL, DRIVEN AGAINST THE EXTRACTED VERSION, FROM OUTSIDE THE INSTRUMENT:**

| control | result |
|---|---|
| the registered set (3 files) | `D6R2C_FM6_G_DEPS_PASS scanned=3 staged=3`, **rc = 0** |
| **the set that killed `FM6`** — `d6r2c_freshmesh.py` staged without what it imports | `ABORT G-DEPS … imports d6r2c_decomp, which is NOT staged`, **rc = 1** |
| a staged file that does not exist | **rc = 1** |
| through the `guard_deps … \|\| exit` idiom a launcher actually uses | refuses the broken set, accepts the registered set |

### 7a.1 A PROPERTY OF THE ORIGIN, FOUND WHILE CONTROLLING IT, REPORTED AND NOT FIXED

**`guard_deps` with an EMPTY staged list returns `rc = 0`.** A launcher that calls it without arguments
— or with a list that silently evaluates to nothing — gets a **PASS from a check that examined nothing**.
That is the same disease as the inert `TRIM_MAX_EVALS` of §2b: *a guard that cannot fail because it was
never given anything to check.*

**IT IS NOT FIXED HERE, DELIBERATELY.** Repairing the body would destroy the byte-identity that is this
extraction's entire anti-drift property, and the origin is frozen. Instead:

1. **The call site carries the assertion.** `d6r2c_dec5_run_arm.sh` asserts the staged list is
   **non-empty and has the registered length** before calling `guard_deps`, and aborts if not.
2. **The property is reported upward**, because it is a property of the **committed** `FM6` launcher too
   and is not this item's to repair.

---

**Original bullet, struck and retained rather than rewritten (rule 2):** *~~the dependency-closure guard
— carried from the `DEC4` launcher by calling it; if it proves to be inline there rather than callable,
this document must say so before freeze.~~* It proved to be inline. §7a is what was done instead.

---

## 8. THE PLANTED CONTROL (rule 3) AND THE §8c STANDING CHECK

`d6r2c_dec5_grade.py` plants into values it **read back from disk** and **REFUSES (exit 2)** if any
plant leaves the verdict at `PASS` — into `J_B`, `J_T`, `J_F`, `J_opt`, into one `CL` of one
matched-lift state, into `thickcon`, and **into the measured growth ratio feeding `M1`**.

### 8a. `PLANT_SANITY = 1.234e-02` — THE REGISTERED PLANT CANNOT TEST THE WIDENED LIMB, AND THAT IS A FINDING

**Driving the plant control during the build surfaced this, and it is registered rather than worked
around.** `PLANT = 1.234e-03` into one condition's `CD` moves `J` by `PLANT × 0.50 = 6.170e-04`, which
is **2.0136 % of `J0`**. **`SANITY_BAND` is 12.3661 %.** So **the registered plant is INVISIBLE to
`M3`** — and a plant smaller than the band it is meant to test is not a test of that band. Left alone,
rule 3 would have this grader refuse forever, correctly.

```
smallest CD perturbation that can flip M3 = SANITY_BAND × J0 / 0.50 = 7.578372e-03
PLANT_SANITY = 10 × PLANT = 1.234e-02  →  20.1360 % of J0   →  flips it
```

**`PLANT_SANITY` is used for the `CD` plants only.** The `CL` and `GEO` plants keep `PLANT`, which
`TRIM_TOL = 1.0e-6` and `GEO_TOL = 1.0e-12` see by three and nine decades. **The decade multiple is
DECLARED, NOT MEASURED**; `7.578372e-03` is the measured floor it had to clear.

**AND THE CONSEQUENCE IS STATED RATHER THAN HIDDEN: on this arm the two `J` limbs cannot see a
perturbation below ~12.4 %.** That blindness is the price of changing the mesh. **Input faults are
still covered — by `D2GEO` at `1.0e-12` (§3a.1), which the mesh change does not touch.** What is
uncovered is a pure CFD-output corruption between 0 and 12.4 %, and **no clause in this registration
claims otherwise.**

**§8c's STANDING CHECK, AND THE PART OF IT ALREADY DONE.** Every constant of the `f23bab95` instruments
was compared against that document's stated value **and the comparison is reported in full including the
matches**, because a check that reports only mismatches cannot be distinguished from a check that did
not run:

```
AOA_LOWER_DEG -4.9570114 MATCH   AOA_STEP_MAX_DEG 0.987284431 MATCH   AOA_UPPER_DEG 10.0 MATCH
CAP_FACTOR 3.00 MATCH           CLOSE_TOL 8.423462e-15 MATCH          CONT_MAX_STEPS 12 MATCH
FINAL_RECORD_N 88 MATCH         GEO_TOL 1.0e-12 MATCH                 INTERACT_TOL 0.10 MATCH
J0_INHERITED 0.0306416314389976151 MATCH   JF_INHERITED 0.0230632595286777639 MATCH
PLANT 1.234e-03 MATCH           PREDICTION_CORE_MIN 138.973 MATCH     REPRO_TOL 1.7162447e-04 MATCH
TRIM_MAX_EVALS 15 MATCH         TRIM_TOL 1.0e-6 MATCH
```
**21 of 21 present in the document, 0 mismatches.** The same comparison is **OWED on this item's own
instruments before its freeze** and is not yet possible: they do not exist (§9).

**A FAILING CONTROL FOR EVERY GATE, DRIVEN FROM OUTSIDE THE INSTRUMENT.** For each of `M1`, `M2`, `D1`,
`D3`, `D4`, `D6`, `--selftest` drives a synthetic tree in a temporary directory in which that gate
**must fail**, built from values written into the fixture **by the test**, not read from the
instrument's own constants — a selftest built from the instrument's own constants is a check on
arithmetic and not on registration, which is how findings 2, 3 and 4 of §8c stayed invisible. Named
controls: a mesh with 60 cells per chain (`M1` topology), a mesh whose measured median ratio is 1.25
(`M1` ratio), a two-line diff (`M2`), a state at miss `1.000000000029e-06` (`D1`, the attainable value
one ulp outside the band), a `J` perturbed by `1e-14` absolute (`D3`), `I` at `0.11 × |J_F − J_B|`
(`D4`), and a null trim count (`D1`).

---

## 9. THE INSTRUMENTS — AND WHAT IS NOT YET RESOLVED

| file | role | md5 | selftest |
|---|---|---|---|
| `d6r2c_dec5_grade.py` | **THE GRADING PATH** — `M1`, `M2`, `M3`, `D1`, `D2GEO`, `D3`, `D4`, `D6`, the table, the plants | `434dfbd6b45e7b6e31792fc37cc2db00` | **`PASS n=89`** |
| `d6r2c_dec5_decomp.py` | producer: six states, trims, `d6r2c_dec5.jsonl` | `fb19791784ebb73747c2f6c466a0d174` | **`PASS n=56`** |
| `d6r2c_dec5_genwingmesh.py` | the family script + the one `N` line | `554b6bba6bbcc90d7d00cb39c17d635d` | **no selftest — proved by `diff`, §1** |
| `d6r2c_dec5_run_arm.sh` | launcher: guards, digest pin, age datum, ledger, the mesh phase, the `diff` assertion of `M2` | `dbf2567cbbc323d8edc6aa93669f928b` | **`PASS n=9`** |
| `d6r2c_guard_deps.sh` | the extracted dependency-closure guard (§7a) | `1de7fcd349b7227a49a008f180f909cc` | driven against the `FM6` killer set |

**The producer differs from `d6r2c_dec4_decomp.py` in SIX lines — the record constant, its selftest
assertion and the selftest banner, all the same `dec4`→`dec5` rename.** The mesh script differs from the
family script in **exactly one line**, proved by `diff` and refused on at launch by `G-ONECHANGE`.
**Nothing frozen was touched**: `d6r2c_dec4_*`, `d6r2c_fm6_run_arm.sh`,
`PREREGISTRATION_AFTER_ITEM8_R2.md` and the family `genWingMesh.py` are all byte-identical to `HEAD`.

**§8c ON THIS ITEM'S OWN CONSTANTS — DRIVEN, AND REPORTED IN FULL INCLUDING THE MATCHES:**

```
AOA_LOWER_DEG -4.9570114 MATCH     AOA_STEP_MAX_DEG 0.987284431 MATCH   AOA_UPPER_DEG 10.0 MATCH
CAP_FACTOR 3.00 MATCH              CLOSE_TOL 8.423462e-15 MATCH         CONT_MAX_STEPS 12 MATCH
FINAL_RECORD_N 88 MATCH            GEO_TOL 1.0e-12 MATCH                GROWTH_TARGET 1.20 MATCH
INTERACT_TOL 0.10 MATCH            J0_INHERITED 0.0306416314389976151 MATCH
JF_INHERITED 0.0230632595286777639 MATCH   MESH_N_LAYERS 62 MATCH       MESH_WALL_FACES 1008 MATCH
PLANT 1.234e-03 MATCH              PLANT_SANITY 1.234e-02 MATCH (added to §8a BY this check)
PREDICTION_CORE_MIN 360.7 MATCH    REPRO_TOL 1.7162447e-04 MATCH (struck, retained for the record)
SANITY_BAND 0.123661365 MATCH      TRIM_MAX_EVALS 15 MATCH              TRIM_TOL 1.0e-6 MATCH
```

**21 of 21 present, 0 mismatches — after the check found one.** On its first run it reported
**`PLANT_SANITY = 1.234e-02` present in the instrument and ABSENT from this document**: a constant
derived during the build and never written into the registration. **That is precisely the defect class
§8c exists for, caught on this item's own work, and §8a is the paragraph it forced.**

**THE HONEST GAPS THAT REMAIN:**

1. ~~No instrument exists yet~~ **RESOLVED.** All four exist, all selftests pass, §8c is driven above.
2. ~~**The dependency-closure guard's callability is UNVERIFIED.**~~ **RESOLVED — §7a.** It was inline
   in the frozen `d6r2c_fm6_run_arm.sh`; it is now extracted verbatim into `d6r2c_guard_deps.sh`
   (md5 `1de7fcd349b7227a49a008f180f909cc`), proved byte-identical to lines 189–222 of its origin, and
   driven against the `FM6` killer set. **One new finding came out of controlling it: the guard returns
   `rc = 0` on an EMPTY staged list — a vacuous pass — which is left unfixed to preserve byte-identity
   and is instead asserted at the call site and reported upward (§7a.1).**
3. **The mesh generation has never run at `N = 62`.** pyHyp's hyperbolic march may not reach
   `marchDist = 300.0` in 61 cells at the smoothing settings the family script uses, or `cMax = 0.1`
   may bind. **`M1` is the gate that catches it**, and a first mesh step that fails is a finding about
   the extrusion at higher layer counts, reported with `mesh_generation.log`, not worked around.
4. **The 1.6053× memory scaling is an assumption**, not a measurement; `--memory=32g` is a declared
   footprint and an OOM kill (`rc = 137`) is a registered outcome that fails `D6` as `NOT A RESULT`.

---

## 10. WHAT THIS DOCUMENT DOES NOT CLAIM

- **It does not claim the growth ratio causes the stall.** It registers a falsifiable test of a
  candidate, with `P2` — refutation — reachable and pre-registered.
- **It does not claim `N = 62` will produce a ratio of 1.197394.** That is the model's number; the gate
  is on the **measured** ratio.
- **It does not claim the decomposition will complete.** `S` may stall again; that is `P2`.
- **It does not move any inherited gate.** `TRIM_TOL`, `CLOSE_TOL`, `INTERACT_TOL`, `TRIM_MAX_EVALS`,
  `PLANT`, `CAP_FACTOR` are inherited unchanged; `D2` is **struck with its reason** (§3a), not loosened.
- **It does not satisfy Sanaa's item 10.** The report is a separate record.

---

## ADDENDUM 1 — 2026-09-13 — `rc = 127`: THE COMMAND FILE'S NAME LIVED IN TWO PLACES, AND THE GUARD THAT PINS EVERY INSTRUMENT DOES NOT PIN ITSELF

**This addendum carries the document to version 1.1.** Line 4 still reads `Version 1.0` and is
**deliberately not edited**: editing it would falsify this section's own assertion below.

**Lines whose number changed above this section: 0.** Proof in §A1.9.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** `M1`, `M2`, `M3`, `D1`, `D2GEO`,
`D3`, `D4`, `D6`, `GROWTH_TARGET`, `SANITY_BAND`, `PLANT`, `PLANT_SANITY`, `TRIM_TOL`,
`TRIM_MAX_EVALS`, `CLOSE_TOL`, `INTERACT_TOL`, `GEO_TOL` and the §6 cap of `1082.100` core-min all
stand exactly as frozen at `6f20e1394a60a507698cc155d6c5c0cb17942421`.
**`DEC5`'s `NOT A RESULT` row stands, is never re-seeded and is never re-graded.**

### A1.0 WHAT HAPPENED

`DEC5` launched 2026-09-13T09:09:31Z. **Every guard passed** — `G_ROOT`, `G_BOX`
(`solver_swap_offenders=0`), `G_FREEZE`, `G_DEPSLIB_PASS`
(`body=e4fe26ad6e29900ce4b67255c9ddc9c1 origin=d6r2c_fm6_run_arm.sh:189-222`),
`D6R2C_FM6_G_DEPS_PASS scanned=2 staged=2`, cap `1082.100` from the frozen grader, `G_COLD`. Then:

```
bash: /mnt/DEC5/d6r2c_dec4_cmd.sh: No such file or directory
rc = 127, 12 s wall, 0.800 core-min
```

The frozen grader **REFUSED, exit 2, `REFUSE_MISSING_DECOMP_RECORD`** → **`NOT A RESULT`**. Cap
untouched, hygiene clean, zero root-owned files, zero containers left.

### A1.1 THE DEFECT — THE TENTH MEMBER OF THIS ITEM'S FAMILY, AND THE AUTHOR'S OWN

**The command file's name existed in two places** — the `CMDFILE=` assignment and the `docker run`
line — **and the rename moved one.** Four `d6r2c_dec4_` literals survived: the container command path,
the container `NAME` (visible in the launch line as `d6r2c_dec4_DEC5_…`), the `G-LIVE` filter and the
usage string.

**That is the same defect as the inert `TRIM_MAX_EVALS`, the `_flat` that did not flatten, the scaler
divisor read without its fallback, and the stale `head -1140` line count: one string, two copies, one
updated.** §8c of the parent registration states the disease in one sentence — *a registered clause
that is not the clause that executes* — and this document's author shipped a fresh instance of it into
this very registration.

**AND THE SELFTEST PASSED `n = 9` ON A LAUNCHER THAT COULD NOT START**, because it never read the
`docker run` line. **A selftest that exercises everything except the invocation is a check on the parts
nobody doubted.**

### A1.2 THE REPAIR, AND THE CONTROLS THAT WOULD HAVE CAUGHT IT

1. The container command path is **derived from `$CMDFILE`** — one source, no second literal.
2. All four surviving predecessor literals removed.
3. **Two new controls**: the `docker run` line must derive its path from `$CMDFILE`; and **no
   predecessor literal may survive anywhere in the launcher.**
4. **Both are DRIVEN AGAINST A DELIBERATELY BROKEN COPY and FAIL on it, naming the offending line** —
   not assumed. On a copy with the literal reintroduced they report
   `SELFTEST FAIL the docker line carries its own copy of the command-file name` and
   `SELFTEST FAIL a predecessor literal survives: 474: … d6r2c_dec4_cmd.sh`.

### A1.3 THE FIRST DRAFT OF THAT CONTROL WAS ITSELF L-580

`grep -c 'd6r2c_dec4_' "$0"` **counted its own error message** and reported `FAIL` on a clean launcher.
**The check matched itself** — the same shape as the process audit L-580 records. The predicate is now
written so its own line cannot satisfy it: the file holds the bracketed form `d6r2c_de[c]4_`, which the
regex `d6r2c_de[c]4_` does not match, and the comment at the site says why.
**It was found by DRIVING the control, not by trusting it.**

### A1.4 THE STRUCTURAL FINDING — **THE GUARD THAT CHECKS OTHERS DOES NOT CHECK ITSELF**

**`guard_freeze` pins `d6r2c_dec5_grade.py`, `d6r2c_dec5_decomp.py` and `d6r2c_dec5_genwingmesh.py` —
and NOT the launcher that contains it.** So this file could drift arbitrarily from §9's table **with
nothing firing**: every guard would pass, the cap would resolve, and the recorded instrument table
would simply be false. That is this night's most general defect: **a verifier that verifies everything
except itself.**

**IT IS CLOSED WITHOUT A FIXED POINT.** A file cannot contain its own hash, but it can **report** it:

```
D6R2C_DEC5_ROW arm=… rc=… core_min=… cap=… root_owned=… launcher_md5=$(md5sum "$0" …) log=…
```

**REGISTERED REQUIREMENT:** the `launcher_md5` recorded in the ledger row **must equal the launcher md5
in §9's table as amended by §A1.6**. The grader is frozen and is **not** reopened for this; the
comparison is made by `dafoam-supervisor` at grading, against the ledger and the table. **That converts
an unverifiable claim into a checkable one at the cost of one line**, and it is checkable by any reader
afterwards, not only at run time.

### A1.5 `DEC6` — THE RE-RUN ID, IDENTICAL CAP, NO NEW THRESHOLD

`DEC5` holds a ledger row and a directory, so `G-COLD` refuses it. **`DEC6` is the successor**, handled
exactly as `DEC2`/`DEC3` and `FM2`–`FM5` were: **it inherits the IDENTICAL registered figure by reading
DEC5's own cap out of the FROZEN grader** (`cap_core_min` maps `DEC6 → DEC5` before the lookup).
**No new threshold is invented, none is raised, none is reduced, and the grader is not touched.**
Measured: `DEC5 = 1082.100`, `DEC6 = 1082.100`, unknown arm empty — **asserted by a selftest control**,
not by this sentence. **Every arm-id site is keyed**: the cap function, the accepted-arm `case`, and the
usage string.

### A1.6 SECTION 9 — WHAT MOVED AND, MORE IMPORTANTLY, WHAT DID NOT

| file | md5 at freeze | md5 now | moved? |
|---|---|---|---|
| `d6r2c_dec5_grade.py` | `434dfbd6b45e7b6e31792fc37cc2db00` | `434dfbd6b45e7b6e31792fc37cc2db00` | **NO — THE GRADING PATH DID NOT MOVE AND ITS PIN DID NOT CHANGE** |
| `d6r2c_dec5_decomp.py` | `fb19791784ebb73747c2f6c466a0d174` | `fb19791784ebb73747c2f6c466a0d174` | **NO — the producer did not move and its pin did not change** |
| `d6r2c_dec5_genwingmesh.py` | `554b6bba6bbcc90d7d00cb39c17d635d` | unchanged | **NO** |
| `d6r2c_guard_deps.sh` | `1de7fcd349b7227a49a008f180f909cc` | unchanged | **NO** |
| `d6r2c_dec5_run_arm.sh` | `dbf2567cbbc323d8edc6aa93669f928b` | **`0d1d117ac90b19636152eb6999dfde5f`** | **YES — this addendum is that disclosure** |

**The reader's first question is whether the grading path shifted. It did not.** `d6r2c_dec5_grade.py`
is byte-identical to the freeze, its `# PIN` line is unchanged, and `guard_freeze` still refuses any
difference. **Only the launcher moved, and only in the four places named in §A1.2 plus §A1.4's one
reporting line and §A1.5's cap mapping.**
**Selftests at the new bytes: launcher `PASS n=13`, producer `PASS n=56`, grader `PASS n=89`.**

### A1.7 THE BANNER COUNT DRIFTED AGAIN, AND IT WAS THE AUTHOR'S SECOND TIME

The launcher printed **`SELFTEST PASS n=9` while driving 13 checks.** This is the **same** defect the
same author fixed in the `d6r2c_after_run_arm.sh` launcher hours earlier — *a banner whose number does
not match its checks is a second copy of a number that can drift* — **and it was reintroduced here by
adding controls without updating the count.** Corrected to `n=13`. **Recorded rather than quietly
fixed, because the repetition is the finding: knowing a lesson is not applying it.**

### A1.8 SPEND

`DEC5`: **0.800 core-min**, cap `1082.100` untouched (0.07 % used). **Defect-attributable waste** — the
launcher was the author's own. `= $0.00068` derived, not measured, `cost_basis` **reported-by-owner**.
**No calibration row: no arm has completed.**

### A1.9 THE APPEND-ONLY PROOF

- **THE PROOF IS PREFIX BYTE-IDENTITY, AND IT IS SOUND:** `HEAD`'s blob is **572 lines**, md5
  **`33992c44d65a99fe944a1f2a657acb2e`**, and `head -572` of the worktree hashes to **the same value**.
  Nothing above line 572 was touched. The worktree is 714 lines; **142 appended.** The line count is
  **DERIVED from the committed blob in the same shell invocation, never typed** — the lesson this lane
  paid for earlier tonight with a stale `head -1140`.
- **`git diff --numstat` IS NOT THE PROOF, AND USING IT AS ONE WAS A DEFECT IN THIS LANE'S METHOD.**
  Bare `git diff` compares the worktree against the **INDEX**, not against `HEAD`, and **the index is
  shared and moves under you as peers stage and commit.** This very check read
  **`238 insertions / 19 deletions`** on one invocation and **`142 / 0`** on the next, **with the file
  untouched between them and `HEAD` unmoved** — the first reading raced the freeze commit updating the
  index. **A proof whose answer depends on when a peer last staged something is not a proof.**
  Where a numstat is quoted it must be **`git diff HEAD --numstat`**, and it is corroboration, never the
  proof. Measured here: `git diff HEAD --numstat` = **142 insertions, 0 deletions**.
- **Lines whose number changed above this section: 0.**

### A1.10 WHAT THIS ADDENDUM DOES NOT DO

- **It does not move the grading path**, any gate, any threshold, any cap or any label.
- **It does not re-grade `DEC5`.** That row stands at `NOT A RESULT`.
- **It does not claim the launcher is now correct.** It claims two specific defects are repaired, two
  controls now fail on a broken copy, and the launcher reports its own md5 so the table and the artefact
  are comparable. **`DEC6` is the test.**

---

## ADDENDUM 2 — 2026-09-13 — `rc = 2`: THE ADDENDUM 1 REPAIR SHIPPED A QUOTING DEFECT, AND ITS CONTROL WAS A GREP

**This addendum carries the document to version 1.2.** Line 4 still reads `Version 1.0` and is
**deliberately not edited.**

**Lines whose number changed above this section: 0.** Proof in §A2.7.

**THIS ADDENDUM ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** Every gate and constant stands as
frozen. **`DEC5`'s and `DEC6`'s `NOT A RESULT` rows both stand, are never re-seeded and are never
re-graded.**

### A2.0 WHAT HAPPENED

`DEC6` launched 2026-09-13T09:19:38Z. **Every guard passed**, including the new ones — cap `1082.100`
resolved under the `DEC6 → DEC5` mapping, `G_DEPSLIB_PASS`, `scanned=2 staged=2`, `G_COLD`. Then:

```
bash: -c: line 1: unexpected EOF while looking for matching `"'
rc = 2, 1 s wall, 0.067 core-min
```

Frozen grader **REFUSED, exit 2, `REFUSE_MISSING_DECOMP_RECORD`** → **`NOT A RESULT`**. Cap untouched
(0.006 % used), hygiene clean.

### A2.1 THE DEFECT — INTRODUCED BY THE ADDENDUM 1 REPAIR ITSELF

ADDENDUM 1 replaced a hard-coded command-file name with `$(basename "$CMDFILE")` **and got the escaping
wrong**. Reproduced exactly, not inferred:

```
ADDENDUM 1 built:  . /home/dafoamuser/dafoam/loadDAFoam.sh && bash /mnt/DEC6/d6r2c_dec5_cmd.sh"
                                                                                              ^ stray quote
bash -n:           bash: -c: line 1: unexpected EOF while looking for matching `"'
```

**The trailing `"` is the whole failure**, and it reproduces the container's message character for
character. **This is the third launch attempt stopped by this launcher and the SECOND defect introduced
while repairing the previous one.**

### A2.2 THE FINDING THAT MATTERS MORE THAN THE QUOTE — **A GREP IS NOT A TEST THAT SOMETHING RUNS**

ADDENDUM 1 added a control for exactly this line. **It passed.** It was:

```
grep -q 'bash /mnt/\$ARM/\$(basename' "$0"
```

**It asserted that the line MENTIONED `$CMDFILE`. It could not tell whether the result was valid
shell.** The launcher selftest reported `PASS n=13` on a launcher that could not start a container —
the same shape as ADDENDUM 1's own finding, one level in: **a check on the TEXT of a line is not a check
that the line RUNS.** Tonight this family has now produced: a check that read its own error message
(§A1.3), a check that read the wrong git reference (§A1.9), and a check that read a line instead of
executing it.

### A2.3 THE REPAIR — BUILD ONCE, VALIDATE, THEN PASS

```
CONTAINER_CMD=". /home/dafoamuser/dafoam/loadDAFoam.sh && bash /mnt/$ARM/$(basename "$CMDFILE")"
bash -n -c "$CONTAINER_CMD" || { echo "ABORT G-CMDSTRING …"; exit 6; }
```

**The string that is checked is the string that runs** — one object, constructed once, validated as
shell before `docker run` ever sees it, and echoed into the log as `D6R2C_DEC5_CONTAINER_CMD` so a
reader can see what the container was told to do. A malformed string now **aborts at launch** instead of
burning a container.

**AND THE CONTROL NOW EXECUTES INSTEAD OF GREPPING.** It builds the string the same way the launcher
does, requires `bash -n -c` to accept it, **and** requires it to name the staged file.
**DRIVEN AGAINST A COPY CARRYING ADDENDUM 1's ESCAPING, IT FAILS**:
`SELFTEST FAIL the container command string is malformed`. Verified on the repaired file:
`CONTAINER_CMD = . /home/dafoamuser/dafoam/loadDAFoam.sh && bash /mnt/DEC6/d6r2c_dec5_cmd.sh`,
`bash -n: VALID`.

### A2.4 §A1.4's MECHANISM WORKED ON ITS FIRST RUN

The ledger row reads:

```
D6R2C_DEC5_ROW arm=DEC6 … launcher_md5=0d1d117ac90b19636152eb6999dfde5f
```

**That is exactly the value §A1.6 registered**, so the table and the artefact that ran were comparable
by a reader, on the first arm after the mechanism was added. **The self-md5 report did its job even
though the launcher failed** — which is the point of a channel that records rather than gates.

### A2.5 SECTION 9 — WHAT MOVED AND WHAT DID NOT

| file | md5 at ADDENDUM 1 | md5 now | moved? |
|---|---|---|---|
| `d6r2c_dec5_grade.py` | `434dfbd6b45e7b6e31792fc37cc2db00` | unchanged | **NO — THE GRADING PATH DID NOT MOVE, ITS PIN DID NOT CHANGE** |
| `d6r2c_dec5_decomp.py` | `fb19791784ebb73747c2f6c466a0d174` | unchanged | **NO** |
| `d6r2c_dec5_genwingmesh.py` | `554b6bba6bbcc90d7d00cb39c17d635d` | unchanged | **NO** |
| `d6r2c_guard_deps.sh` | `1de7fcd349b7227a49a008f180f909cc` | unchanged | **NO** |
| `d6r2c_dec5_run_arm.sh` | `0d1d117ac90b19636152eb6999dfde5f` | **`e1de4e8b303153d7a6ac2e7da13f1379`** | **YES — this addendum is that disclosure** |

Launcher selftest **`PASS n=14`** (the count updated with the new control, §A1.7's lesson applied this
time without being told); producer **`PASS n=56`**; grader **`PASS n=89`**.

### A2.6 `DEC7` — THE RE-RUN ID

`DEC6` holds a ledger row and a directory, so `G-COLD` refuses it. **`DEC7` is the successor and
inherits the IDENTICAL registered figure** by the same `→ DEC5` mapping into the frozen grader.
**`DEC7` IS KEYED AT EVERY ARM-ID SITE IN THIS SAME REPAIR** — the cap mapping, the accepted-arm
`case`, the usage string — and the launcher md5 in §A2.5 is the value AFTER that keying, because a
table written before the last edit is the defect this addendum is about. **No new
threshold; the grader is not touched.** Every arm-id site keyed, asserted by control.

### A2.7 THE APPEND-ONLY PROOF — BY THE SOUND METHOD OF §A1.9

- `HEAD`'s blob is **723 lines**, md5 **`94e72afc41fa7bf86414ef4fc202fbe0`**, and `head -723` of the
  worktree hashes identically. **Nothing above line 723 was touched.** The count is derived from the
  blob in the same shell invocation.
- **`git diff HEAD --numstat`** — never bare `git diff`, which reads the shared index (§A1.9, L-594) —
  is quoted as corroboration only.

### A2.8 SPEND

`DEC6`: **0.067 core-min**, defect-attributable waste, the author's own. Cumulative on this
registration: `DEC5` 0.800 + `DEC6` 0.067 = **0.867 core-min = $0.00074 derived, not measured.**
**Three launch attempts have cost 0.867 core-min between them** — §11a's cheap-and-disposable design
holding, with the expense in turnaround rather than compute. **No calibration row: no arm has
completed.**

### A2.9 WHAT THIS ADDENDUM DOES NOT DO

- **It does not move the grading path**, any gate, threshold, cap or label.
- **It does not re-grade `DEC5` or `DEC6`.** Both stand at `NOT A RESULT`.
- **It does not claim the launcher is now correct.** It claims one further defect is repaired and that
  the control for it now executes rather than greps. **`DEC7` is the test.**
