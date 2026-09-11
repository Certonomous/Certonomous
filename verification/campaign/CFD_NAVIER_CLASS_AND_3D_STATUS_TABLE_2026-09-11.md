# cfd territory — Navier-class and 3-D case status table

**Date:** 2026-09-11. **Team:** cfd. **Author:** a cfd `lab-lane`.
**Status:** STATUS TABLE. **Not a pre-registration, not a ruling, and it issues no new verdict.**
Every verdict below is *reported from* the record that already carries it, cited by path.
Where this lane could not verify a cell it says `VERIFY` and why. **A confident wrong row is
worse than a blank one**, and that rule was applied against this lane's own convenience in
§2, §5.1 and §5.3.

**ZERO COMPUTE was spent on this document.** No solver was launched, no mesh built, no case
directory created for it. Every figure is read off an artifact already on disk.

---

## 0. WHY THIS EXISTS, AND THE ASK IT ANSWERS

Sanaa, **2026-09-10T19:35Z**, verbatim: *"I want my 3D cases that i asked for and the
additional navier cases. Also how about b-52 and motorbyke etc"* — asked again at 20:20Z.

Sanaa, **2026-09-10T19:45Z**, recorded ask: every hard case run and completed **with its mesh
convergence** — three levels, a `CONVERGING` triple, GCI at `Fs = 1.25`. **Column 5 is
therefore the column this table exists for**, and §3 reports what it actually contains rather
than what one would wish it contained.

**This document slipped a full day.** It is not re-dated to hide that.

---

## 1. HOW TO READ THE COLUMNS — INCLUDING WHAT THEY DO NOT MEAN

| column | what it means | what it does NOT mean |
|---|---|---|
| **verdict** | the fixed vocabulary ONLY — `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` (CLAUDE.md rule 1) | no synonym appears; where a record's own word is outside the vocabulary this table says so rather than translating it (§5.1) |
| **prereg** | does a pre-registration exist, and is it FROZEN | **"frozen" here = tracked in git and identical to `HEAD`**, i.e. the gate cannot now be edited without a visible commit. It is **NOT** a check that the freeze preceded first compute — see the honest limit in §5.2 |
| **mesh triple** | does a three-level grid family exist, and its Roache state: `CONVERGING` / `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` | a triple existing is not a triple converging; rule 5 makes a non-`CONVERGING` triple `NOT A RESULT` whatever the value |
| **artifact** | the path the claim is read from | — |

**Verdict source of truth, and this is the method point that decides the table's accuracy:**
**the verdicts live in `verification/campaign/*.md`, one level above the run trees.** Most
directories under `verification/runs/` carry no README, no RESULTS and no marker file at all.
**A family whose run directory has no marker is not thereby ungraded**, and this table was
built by reading the campaign records, not by looking for markers.

---

## 2. THE 3-D / NAVIER-CLASS SPINE — the rows Sanaa asked for

| case | dim | verdict | prereg / frozen | mesh triple + Roache state | artifact | blocked on |
|---|---|---|---|---|---|---|
| **SUBOFF A1** (hull+fairwater, 3-D) | 3-D | **PENDING** | exists; **COMMITTED** blob `b0f441fdee05`, but its own DRAFT banner still stands ⇒ **UNFROZEN** | **L1 + L2 BUILT AND MEASURED; L3 NOT BUILT.** No triple yet, so no Roache state | `verification/campaign/SUBOFF_A1_PREREGISTRATION.md`; `verification/runs/navier_class/SUBOFF_A1/L{1,2}/log.checkMesh.FULLFLAG` | **L3 blocked on box RAM — §4.** Freeze is the supervisor's check-4 |
| **SUBOFF R1** | axisym. wedge | **NOT A RESULT** (cap-stop on incompleteness; no gate was read) | exists; COMMITTED `6ea3283938af` | triple not completed | `verification/campaign/SUBOFF_R1_RESULTS.md:1` | superseded by R1b |
| **SUBOFF R1b** | axisym. wedge | **NOT A RESULT** | exists; COMMITTED `0ff780e4b823` | three levels ran; **DIVERGENT** | `verification/campaign/SUBOFF_R1b_RESULTS.md:1,49`; `verification/runs/navier_class/SUBOFF/VERDICT.R1b_triple.txt` | `CT` anomaly OPEN; A1 §1 diagnoses, does not close it |
| **MRF R1** | 3-D | **NOT A RESULT** | exists; COMMITTED `41cc27ae89e8` | **DIVERGENT**, observed order **−5.2311**, Celik unequal-ratio form. Band verdict was `PASS` (4.453 ∈ [4,6]) and the one-way gate turned it | `verification/runs/navier_class/MRF/MRF_R1_GRADED_ROW.json` | the divergence itself |
| **MRF R2** | 3-D | **NOT A RESULT** | exists; COMMITTED `dba6e43ac046` | **DIVERGENT**, observed order **−5.7784**, unequal-ratio form. Band verdict again `PASS` | `verification/runs/navier_class/MRF/R2/MRF_R2_TRIPLE_AT_4000.json` | **the family has now lost twice the same way** |
| **DRIVAER R1 / Stage A** | 3-D | **PENDING** | both exist; COMMITTED (`f981f46448a6`, `c98bfa280065`) | three levels **BUILT AND MEASURED** (128,230 / 748,658 / 5,025,587 cells), **all three `Failed 3 mesh checks`**; no solved triple ⇒ no Roache state | `verification/runs/navier_class/DRIVAER/MESH_FAMILY_MEASURED.json` | the layer defect, §5.3 |
| **CRM M0.85** | 3-D | **PENDING** | exists; COMMITTED `cd40259a9242`; record states frozen at `ed8a6b07` | not yet built | `verification/campaign/CRM_M085_PREREGISTRATION.md`; `verification/runs/CRM_M085_runs/CASE_RECORD.md` | setup defects fixed pre-freeze; run not yet graded — `VERIFY` the live rung |
| **M6C1** | 3-D | **PENDING** | exists but **DRAFT/UNFROZEN**, and its worktree copy **differs from `HEAD`** | L1/L2/L3 directories exist with `log.checkMesh`; no graded triple | `verification/campaign/M6C1_PREREGISTRATION.md`; `verification/runs/M6C1_runs/L{1,2,3}/` | the uncommitted edit, §5.4 |
| **M6C2** | 3-D | **PENDING** | `VERIFY` — no `M6C2_PREREGISTRATION.md` in `verification/campaign/` | **no triple**; run dir holds only `L1`, `MP`, `ROUTE_PROBE`, `surface` | `verification/runs/M6C2_runs/` | not yet registered |
| **M6CP1** | 3-D | **NOT A RESULT**, parked | exists; COMMITTED `7b056ce43c20` | the cusp case — feature count flat across levels | `verification/campaign/M6CP1_PREREGISTRATION.md`; cited at `M6C1_PREREGISTRATION.md:24` | geometry: zero cells across the TE by construction |
| **PRD E1** | 3-D | **PENDING** | exists; COMMITTED `65dc864325e6` | **12 DONE level-dirs present**: `us{0.25,0.50,1.00,2.00}_L{1,2,3}` ⇒ four triples staged | `verification/runs/navier_class/PRD/DONE.us*`; ruling `PRD_E1_GATE_RULING_2026-09-09.md` | ruling requires **L4** before PASS/GATE FAIL; four of five `U_s` points have no triple |
| **SUP_BOOSTER E1** | — | **NOT A RESULT** | exists | `VERIFY` | `verification/campaign/SUP_BOOSTER_E1_VERDICT.md:1` | superseded by E2 |
| **SUP_BOOSTER E2** | — | **PASS** | exists; record states freeze commit `34797ce9` | `VERIFY` | `verification/campaign/SUP_BOOSTER_E2_VERDICT.md` | — **closed** |
| **B-52 rung 6 (replicate)** | 3-D | **`VERIFY` — outside the vocabulary.** Record's own word is **"REPRODUCE"** | exists; COMMITTED `af911f73d980` | two same-recipe replicate meshes — a **replicate pair, not a refinement triple** | `verification/campaign/B52_RUNG6_REPLICATE_RESULTS.md:22` | §5.1 — pre-vocabulary record |
| **B-52 rung 7** | 3-D | **`VERIFY`** — no fixed-vocabulary verdict found in the record | exists; COMMITTED `60e45a6c9eaa` | `VERIFY` | `verification/campaign/B52_RUNG7_RESULTS.md` | §5.1 |
| **B-52 rung 8** | 3-D | **`VERIFY`** — record carries two prose "Verdicts", neither in the vocabulary | exists; COMMITTED `b5a81b1149f0` | `VERIFY` | `verification/campaign/B52_RUNG8_RESULTS.md:11,47` | §5.1 |
| **MOTORBIKE** | 3-D | **NO SUCH CASE — see §5.5** | **none** | **none** | `models/curriculum/motorBike`, `demo-output/website/motorbike-video` | it is a curriculum/demo asset, **never a graded verification case** |

---

## 3. 🔴 THE MESH-CONVERGENCE COLUMN, READ HONESTLY — THE ANSWER TO SANAA'S 19:45Z ASK

This is the column she asked for, so it gets its own section rather than a shrug in a cell.

**Across the sixteen rows of §2, the number of cases holding a `CONVERGING` three-level
triple with a quotable GCI at `Fs = 1.25` is ZERO.**

The distribution, stated plainly:

| state | cases |
|---|---|
| triple exists and is **`DIVERGENT`** | **3** — MRF R1, MRF R2, SUBOFF R1b |
| triple exists and is **`CONVERGING`** | **0** |
| three levels **meshed** but no solved triple | **2** — DRIVAER (measured), SUBOFF A1 (two of three built) |
| triples **staged but not graded** | PRD E1 (four `U_s` × 3 levels; the ruling demands L4 before any grade) |
| **no triple at all** | M6C2, CRM, B-52 rungs (replicate pair, not a refinement family), MOTORBIKE (no case) |

**The three `DIVERGENT` triples are not three unrelated accidents.** MRF lost the same way
twice — order **−5.2311** then **−5.7784** — and both times the *band* verdict underneath was
`PASS` and rule 5's one-way gate correctly refused to let it stand. A negative observed order
of magnitude five is not near-asymptotic behaviour; it is the family moving the wrong way
under refinement. **The lab's 3-D mesh-convergence position is weaker than any single case
record suggests, and that is the honest headline of this table.**

Corroborating standing hazard, from this lane's own SUBOFF A1 work today: the **delivered**
refinement ratio was **1.4079** against a nominal **1.5** (re-derived from built cell counts
3,268,613 → 9,121,237, ratio 2.790553). MRF delivered 1.4157/1.4264 against the same nominal
1.5. **`nCellsBetweenLevels` buffers in CELLS, not physical thickness**, so a background block
scaled by exactly 1.5 does not deliver 1.5. **A family whose ratios are taken as nominal is
already mis-graded before it is solved** — and where ratios come out unequal the **Celik
unequal-ratio form** is required, which is what the MRF graded rows already use (`"form":
"unequal"`), not the equal-ratio shortcut.

---

## 4. 🔴 SUBOFF A1 — THE LIVE CASE, AND WHY L3 IS NOT BUILT

Measured by this lane today. Full-flag `checkMesh`, **`rc` read as nothing** (§5.3):

| | **L1** | **L2** |
|---|---|---|
| cells | **3,268,613** | **9,121,237** |
| faces / points | 10,145,599 / 3,618,354 | 28,106,791 / 9,884,456 |
| geometric directions | **3** `(1 1 1)` | **3** `(1 1 1)` |
| max non-orthogonality (≤ 70) | **64.953** | **64.906** |
| max skewness (≤ 4) | **2.913** | **3.126** |
| max aspect ratio | 13.054 | 15.892 |
| **min cell determinant** (gated ≥ 1.0e-03) | **8.6227045e-04** ⬅ **BELOW FLOOR** | **1.5198839e-03** |
| printed verdict | **`Failed 2 mesh checks`** (determinant: **1 cell**; concave: 65,027) | **`Failed 1 mesh checks`** (concave: **131,728**) |
| **layers added** | **1,181,952 / 1,199,862 = 98.507 %** | **3,070,138 / 3,112,452 = 98.640 %** |
| layer table | hull 5.92/6, sail 5.90/6 | hull 6.92/7, sail 6.88/7 |
| **negative-volume / illegal faces, final pass** | **0** | **0** |
| snappy peak memory | 7.52 GiB | 17.71 GiB |
| cost | 578 s × 8 = **77.07 core-min** | 1714 s × 8 = **228.53 core-min** |

Artifacts: `verification/runs/navier_class/SUBOFF_A1/L{1,2}/log.checkMesh.FULLFLAG`,
`.../log.snappyHexMesh`, `.../STATUS.mesh`, `L1/FEATURE_PROBE.json`.

### 4.1 L3 IS `BLOCKED`, AND THE BINDING CONSTRAINT IS RAM, NOT THE CAP

Holding the delivered ratio 1.4079 puts L3 at **25.45 M cells**. Two independent reasons it
does not run, both measured from the two levels already built:

1. **MEMORY — the hard one.** Peak snappy memory, read off each log's own `Memory per-node`:
   7.52 GiB at 3.269 M cells, 17.71 GiB at 9.121 M cells. Two-point power-law fit
   `peak[GiB] = 2.799 × (Mcell)^0.835` predicts **41.7 GiB at 25.45 M cells** (49.4 GiB if
   scaled linearly at L2's rate). **The box has 30 GiB of RAM.** Labelled **ESTIMATED** — a
   two-point extrapolation, not a measurement — but it exceeds the whole box by ~40 % on the
   more favourable fit.
2. **COST.** At the registration's own T26 anchor (1703 core-min/Mcell), the triple costs
   **64,455 core-min = 2.01× the registered 32,000 cap**; L3 alone is 43,353 core-min, above
   the *family* cap. Derived **$55.11** at the owner-stated $0.0513/core-h — **DERIVED, NOT
   MEASURED**; the box cannot read its own billing. Under §8's 3-D exemption this is
   `M3 REPORTING` and would not by itself stop the run. **The memory wall is not exempted by
   anything.**

**Why this lane did not simply try it.** The two largest long-lived processes on this box
belong to other teams — `rhoCentralFoam` (3 d 04 h) and `buoyantBoussinesqSimpleFoam`
(1 d 00 h). A 42 GiB build on a 30 GiB box invites the OOM killer, which does not respect
ownership. **Killing another team's multi-day solve by memory pressure is touching a running
solver by another route**, and the hard limit holds.

**And shrinking L3 to fit is a trap, not a fix:** a 24 GiB peak allows only 13.1 M cells ⇒
`r23 = 1.129`; an 18 GiB peak ⇒ `r23 = 1.006`. Celik wants `r ≥ 1.3`. Those are triples in
name only, and a GCI computed off `r = 1.13` would be a number that cannot discriminate.
**Reporting `BLOCKED` is correct here; manufacturing a triple would not be.**

Two repairs are costed and **neither is chosen here** — a gate threshold and a family
definition are not a lane's to move (rule 9), and `SUBOFF_A1_PREREGISTRATION.md` §11.6
already reserved this exact collision to the cfd-supervisor: (a) build the triple *downward*
with a ~1.17 M-cell level below L1, giving equal delivered ratios of 1.4079 on two levels
already built — at the cost that its TE-base count falls below Gate M-b-1's floor of 8; or
(b) §11.6's own option (b), coarsening the registered truncation from 0.995 c to 0.990 c,
~8× cheaper in the level-9 `teBox` region that carries 1,604,248 of L2's cells.

### 4.2 🔴 THE DETERMINANT FINDING — AND IT IS AN INSTRUMENT DEFECT, NOT A MESH DEFECT

**Gate M-d's determinant limb fails at L1 and passes at L2.** §5.1 M-d registers a floor of
`1.0e-03`, inherited — `docs/standards/MESH_STANDARD.md:139` records it as snappy's own
generation default `minDeterminant 0.001`, and it is the threshold `checkMesh` itself uses.
**It was not invented for this registration and so cannot have been fitted to a measured
mesh.** L1 measures `8.6227045e-04`, below it, **by one cell out of 3,268,613**; L2 measures
`1.5198839e-03`, above.

**The floor does not move.** For a mesh-admission gate, *first compute is the mesh build*, not
the solver: the meshes exist and cost 305.6 core-min, so amending M-d now would be choosing a
gate after seeing what it grades — whatever the document's DRAFT banner says.

### 🔴 AND HERE IS THE MECHANISM, MEASURED — TWO OPENFOAM INSTRUMENTS DISAGREE ON ONE MESH

`L1/system/snappyHexMeshDict:74` and `:76` set **`minDeterminant 0.001` in the strict block
AND in the `relaxed` block**, identically at L1 and L2 (the only dict differences between the
two levels are `locationInMesh` and `nSurfaceLayers` 6 vs 7). **So the escaping cell was not
admitted by a loosened threshold — both passes enforce the same 0.001.**

Then, on the **same mesh, in the same directory, minutes apart**:

| instrument | what it printed about determinant < 0.001 |
|---|---|
| `snappyHexMesh`, its own final quality check (`L1/log.snappyHexMesh`) | **`faces on cells with determinant < 0.001 : 0`** — followed by **`Finished meshing without any errors`** |
| `checkMesh -allGeometry -allTopology` (`L1/log.checkMesh.FULLFLAG:132`) | **`***Cells with small determinant (< 0.001) found, number of cells: 1`**, and **`Failed 2 mesh checks.`** |

**Same threshold literal. Same mesh. Opposite answers.** snappy counts *faces on cells*;
`checkMesh` counts *cells* — and whatever the definitional difference, **snappy's
self-certification at its own configured threshold does not detect a cell that `checkMesh`
flags at that same threshold.**

**Apply `VERIFICATION_CHARTER` §2da — could OpenFOAM do this if it were working correctly?
YES: it did, at L2, same dict, same geometry, finer.** So this is **DEFECT-SHAPED**, and it is
the **ninth** instance in this lab of a tool reporting success while not doing the thing. It
is a sharper instance than the layer one, because here the *same numeric threshold* is
evaluated by two instruments on one artifact and they disagree.

**🔴 CONSEQUENCE, AND IT CORRECTS THE OBVIOUS FIX.** Tightening the `relaxed` block cannot
repair this: the relaxed block relaxes `maxNonOrtho` 65 → 70 but **already holds
`minDeterminant` at 0.001**. There is no loosened determinant threshold to tighten. **The cell
escaped because snappy's check never saw it, not because snappy was told to allow it** — so a
repair must perturb the mesh (quality-repair loop `nSmoothScale` / `errorReduction`, or the
decomposition, which changes snapping order), not the thresholds. **L2's clean determinant is
therefore luck of the draw, not enforcement.**

Neither `minDeterminant` value is touched in either direction: raising it to force a pass
would be fitting, and lowering it is precisely what must be refused.

### 4.3 A REGISTERED PREDICTION WHOSE FALSIFIER CANNOT FIRE — SPLIT BY LEVEL

§11.7's **P1** predicts every level fails on *"`Cells with small determinant` or high aspect
ratio, not non-orthogonality or skewness"*, with its falsifier registered as *"a level failing
on non-orthogonality or skewness instead"*.

- **At L1 it PARTIALLY HOLDS** — `Failed 2 mesh checks`, and one of the two *is* small
  determinant (the other is `Concave cells`, 65,027).
- **At L2 it is UNCLASSIFIABLE** — `Failed 1 mesh checks`, and that one is **`Concave cells`**
  (131,728), which is in **neither** the predicted set nor the falsifying set.

**So P1 holds at one level and cannot be graded at another — which is worse for the prediction
than a clean miss**, because no reading of its own clause can retire it. This is the §11.2
*"gate that cannot fail"* defect reappearing one level up, in a prediction rather than a gate.
**The transferable repair: a falsifier must partition the outcome space, not name two points
inside it.**

### 4.4 P2 HOLDS, AND IT IS THE GOOD NEWS

Min determinant moves 8.6227e-04 → 1.5199e-03, a **76 % change**. R1b's family held
`3.526225e-05` at all three levels to seven significant figures. **This family re-snaps and
does not carry R1b's scale-invariant degeneracy** — the §1.1 pathology is measured *absent*,
not assumed absent.

### 4.5 🔴 THE PRE-REGISTRATION'S DRAFT BANNER IS FALSE AS WRITTEN

`SUBOFF_A1_PREREGISTRATION.md`'s opening banner asserts **`NO COMPUTE HAS RUN UNDER THIS
DOCUMENT`**. **That is no longer true:** L1 and L2 mesh building have consumed **305.60
core-min** (77.07 + 228.53, from each level's `STATUS.mesh`).

**The `DRAFT` / `UNFROZEN` status is still correct and must stand** — no solver has run, and
§11.0 correctly restates the rule-2 condition as the absence of a *solver result* rather than
of a directory. **It is the compute claim inside the banner that is stale.** Disclosed here
rather than quietly edited. This is the **fifth** instance of the named pattern in which a fix
lands where the code reads a value while the stale claim survives where a human reads it, and
no passing test sees the difference.

### 4.6 THE CHOICE THAT IS SANAA'S, COSTED SO IT CAN BE READ

**A true 25.45 M-cell fine level needs more RAM than this machine has, and an instance change
is reserved to Sanaa.** Both options, costed, neither chosen by any agent:

| option | what it buys | cost |
|---|---|---|
| **A larger instance** | the **registered** triple {3.27 M, 9.12 M, 25.45 M} at the delivered ratio **1.4079** | needs ≥ ~42 GiB RAM for the build; solve ≈ **64,455 core-min**, $55.11 DERIVED NOT MEASURED, **2.01× the registered 32,000 cap** |
| **The downward triple on this box** | a **valid** triple {~1.17 M, 3.27 M, 9.12 M}, equal ratios **1.4079**, two levels already built | ~30 core-min for the new level; **ceiling is coarser**, and its coarsest level's TE-base count falls below Gate M-b-1's floor of 8 |

**Struck from the menu, with the arithmetic shown:** coarsening the registered truncation from
0.995 c to 0.990 c (§11.6's own option (b)) does **not** clear the binding constraint. Level-9
cells are 1,604,248 of L2's 9.12 M; at ~8× cheaper they become ~0.20 M, L2 falls to ~7.72 M,
and L3 scales to **21.54 M cells ⇒ a predicted 36.3 GiB peak, still 21.0 % over the box**.
**A repair that does not clear the binding constraint is not a repair**, and it would pay for
that failure in geometry fidelity. Verified independently by this lane at the
cfd-supervisor's request.

## 5. WHAT THIS LANE COULD NOT VERIFY, AND FIVE CORRECTIONS

### 5.1 `VERIFY` — the pre-vocabulary records (**4 rows**)

**B-52 rungs 6, 7 and 8** and several older lettered records carry verdicts in words **outside
CLAUDE.md rule 1's fixed vocabulary** — rung 6 says **"REPRODUCE"**, `GEN_ALT` says
**"GENERATOR-OWNED"**, `DPW8_V2_joukowski` says **"VERIFIED"**. These predate the vocabulary.

**This table does not translate them.** Mapping "REPRODUCE" onto `PASS` would be inventing a
verdict nobody issued, and rule 1 exists precisely to stop that. They are marked `VERIFY` and
**re-grading them into the vocabulary is a supervisor action, not a table-filling exercise.**

### 5.2 🔴 THE "FROZEN" COLUMN IS WEAKER THAN IT LOOKS — STATED AGAINST THIS LANE'S INTEREST

This table's freeze test is **"tracked in git and identical to `HEAD`"**. That proves the gate
cannot now be edited invisibly. **It does NOT prove the freeze preceded first compute**, which
is what rule 2 actually protects. Establishing that per case means comparing each
pre-registration's first commit against its run directory's first solver artifact — **not done
here, for any row.** Every "COMMITTED" cell should be read as *"the gate is fixed now"*, never
as *"rule 2 was satisfied then"*. **This is the table's single largest unverified claim and it
is flagged rather than buried.**

### 5.3 🔴 CORRECTION — THE DRIVAER 52,165 FIGURE IS ATTACHED TO THE WRONG MESH

A standing hazard relayed to this lane stated that *"on the DrivAer mesh snappy added ZERO
layers and left 52,165 negative-volume cells of 128,230 — 40.7 %"*, as one mesh. **Checked
against the artifacts, that conflates two different builds:**

- the **`addLayers true` DIAGNOSTIC** build has the 52,165 negative-volume cells
  (`DRIVAER_R1_STAGE_A_PREREGISTRATION.md:405`), and 52,248 when rebuilt with
  `mergeTolerance 1e-8`, refuting point-merging as the mechanism (`:416`);
- the **GRADED r1 family** has **`n_negative_volume_cells = 0` at all three levels**
  (`verification/runs/navier_class/DRIVAER/MESH_FAMILY_MEASURED.json`), because layers were
  turned **off** after that diagnosis.

**Both facts are real and the defect is real** — snappy printed *"Finished meshing without any
errors"* with an all-zero final check over a mesh with 179.7° non-orthogonality and a layer
table claiming 5 layers on 47 patches. **But a record citing "52,165 negative-volume cells"
against the graded DrivAer family would be false**, and a defect note whose control is
mis-attributed is a weaker note. Corrected here.

**The instrument rule that follows stands unchanged and is why the §4 table reads as it does:**
`checkMesh`'s `rc` is meaningless **in both directions** — rc=1 on the broken layer mesh, rc=0
on levels printing `Failed 3 mesh checks` (`DRIVAER_R1_STAGE_A_PREREGISTRATION.md:340`, §12.2).
**Never read rc; read the printed verdict line.** SUBOFF A1 records its own as
`checkMesh_rc_NOT_THE_VERDICT=0` so the name itself refuses the misreading.

**A working-case control now exists on the same box the same day.** SUBOFF A1 added
**98.507 %** (L1) and **98.640 %** (L2) of available layer cells with **zero** final illegal
faces. Whatever ails the DrivAer layer build, **it is not that `snappyHexMesh` cannot add
layers on this box** — that is evidence by demonstration rather than by argument, and it is
available to the snappy-defect work when that gets a lane.

### 5.4 UNCOMMITTED WORK FOUND — INSPECTED, NOT REVERTED

`verification/campaign/M6C1_PREREGISTRATION.md` is **tracked but its worktree copy differs from
`HEAD`**. Under rule 10 an unexpected change is **inspected, never reverted**; this lane did
not touch it. **Consequence for this table: M6C1's gate text is not currently pinned by a
commit**, so its row cannot be read as frozen. Surfaced for the supervisor.

### 5.5 THE MOTORBIKE ANSWER, GIVEN STRAIGHT

Sanaa asked about *"motorbyke"*. Swept: `models/curriculum/motorBike`,
`demo-output/website/motorbike-video`, `mission-output/geometry-study/study-motorBike*`,
`cases/demo-surfaces/motor_in_duct.stl`.

**There is no graded motorBike verification case in this repository** — no
`verification/campaign/` record, no pre-registration, no gate, no triple. It exists as an
**OpenFOAM tutorial/curriculum asset and a demo render**. It is the canonical
`snappyHexMesh` exercise and would be a reasonable 3-D candidate, **but nothing about it has
been verified here and no verdict of any kind attaches to it.** Stated as absent, not
approximated.

### 5.6 CASES FOUND THAT THE BRIEFING LIST DID NOT NAME

Swept rather than assumed. Present in cfd territory and **absent from the list this lane was
given**:

| found | state |
|---|---|
| **SUP_BOOSTER E1 / E2** | E1 `NOT A RESULT`, **E2 `PASS`** — *a closed `PASS` that the ordered list omitted entirely* |
| **M6 variants** `M6I`, `M6SR`, `M6S`, `M6_LE_RESOLVED`, `M6_OWN_FAMILY` | additional M6 families beyond M6C1/M6C2/M6CP1, several with their own pre-registrations |
| **JF1 jet flap** (`JF1`, `JF1E` E1/E2a/E2b, `JF1G`, `JF1R`) | 13 campaign records incl. a grid-convergence pre-registration and a mesh-gate finding |
| **F29_CONE_TM** | `cases/F29_CONE_TM/` exists with builder, exact solution and grader — **no campaign record at all** |
| **MDS1** | `verification/runs/MDS1_runs/` with survey artifacts — **no campaign record** |
| **RUNG0 / RUNG0b / RUNG1_M6 / RUNG2_CRM** | mesh-import and M6/CRM rungs with their own pre-registrations |
| `hlpw6`, `tmr`, `valve`, `unsteady-cylinder`, `committee-grids`, `mega-batch` | case directories in `cases/` not represented in the list |

**The two worth a supervisor's eye are `F29_CONE_TM` and `MDS1`: code and run artifacts exist
with no campaign record**, which is the shape a case takes when it is worked and never graded.

---

## 6. COVERAGE, AND WHAT THIS TABLE IS NOT

- **Rows in §2: 16.** Render backlog: **2 renderable, 1 contested, 13 not** (§7). Additional families identified in §5.6: **7 groups**.
- **`VERIFY` rows: 4 verdicts** (B-52 ×3 outside the vocabulary; M6C2 unregistered), plus
  `VERIFY` cells on SUP_BOOSTER triples and the CRM live rung.
- **The `VERIFY` marks are not laziness; each names its reason** — §5.1 pre-vocabulary
  records, §5.2 the freeze-ordering limit, M6C2 having no registration to read.
- **This table issues no verdict and moves no gate.** It reports what the records carry.
- **Nothing here is sent, filed or submitted (rule 7).** SUBMISSIONS PARKED.
- The **F-series, W-series, DMR, D5_rsm, R4, 4G, MESH_AUDIT, MODEL_FORM, GEN_ALT, FPE_DIAG
  and DPW8** families are predominantly 1-D/2-D verification rungs. They were swept for this
  table and their verdicts are on record in `verification/campaign/*_RESULTS.md`; they are
  **not** reproduced row-by-row here because Sanaa's ask was the **3-D and Navier-class**
  spine, and padding §2 with 1-D rungs would dilute the column she actually asked for. The
  one genuinely 3-D member outside the spine is **F25-DUCT3D**, whose record carries **`PASS`
  on a `CONVERGING` triple** (`verification/campaign/F25_DUCT3D_RESULTS.md`) — **the lab's
  one 3-D `CONVERGING` triple, and it is a laminar square duct, not a hard case.**

---

## 7. 🔴 THE RENDER COLUMN — SANAA'S 2026-09-11 RENDER-AS-WE-GO DIRECTIVE

Sanaa, **2026-09-11**, byte-exact: *"whenever a case finishes and completes (i.e run converged
or is within bands of a known reference/ solution), an agent from the designated team needs to
render the stl file (3D geometry) then the mesh paraview, better to do this as we go since
well use them in the demos, instead of us waiting for the day we shoot. (But only whenever a
case is done and checked)."*

**The trigger, as the chief read it** — labelled the chief's reading and correctable by Sanaa:
rule-4 complete **AND** graded by the frozen instrument as converged or `PASS` in band.
**`NOT A RESULT`, `GATE FAIL`, `BLOCKED` and `PENDING` are NOT rendered.** **This table is the
instrument that decides the backlog**, which is why the column lives here rather than in a
second document.

| case | verdict | **renderable now?** | why |
|---|---|---|---|
| **SUP_BOOSTER E2** | **`PASS`** | ✅ **YES** | the only §2 row that clears the test |
| **F25-DUCT3D** | **`PASS`** on a `CONVERGING` triple | ✅ **YES** | genuinely 3-D, graded, in band |
| PRD E1 | `PENDING` | ⚠️ **CONTESTED — §7.1** | named as the demo case, but its own ruling says `PENDING` |
| SUBOFF A1 | `PENDING` | ❌ no | L3 `BLOCKED`; no solver has run at all |
| SUBOFF R1 / R1b | `NOT A RESULT` | ❌ no | R1b's triple is `DIVERGENT` |
| MRF R1 / R2 | `NOT A RESULT` | ❌ no | both triples `DIVERGENT` |
| DRIVAER | `PENDING` | ❌ no | meshed, not solved; layer defect open |
| M6C1 / M6C2 / M6CP1 | `PENDING` / `PENDING` / `NOT A RESULT` | ❌ no | M6CP1 parked on the cusp |
| CRM M0.85 | `PENDING` | ❌ no | not yet built |
| B-52 rungs 6/7/8 | `VERIFY` (outside the vocabulary) | ❌ no | **a `VERIFY` is not a `PASS`** — §5.1 |
| MOTORBIKE | no case | ❌ no | nothing to render §5.5 |

**BACKLOG: 2 renderable now** (SUP_BOOSTER E2, F25-DUCT3D), **1 contested** (PRD E1),
**13 not renderable.**

### 7.1 🔴 THE CONTESTED ROW, SURFACED RATHER THAN RESOLVED

**PRD's fine grid was named as cfd's demo case for today. Under the chief's own stated test it
does not qualify**, and this lane is not going to quietly render it or quietly refuse it:

- **Against rendering:** `PRD_E1_GATE_RULING_2026-09-09.md` requires **L4** before any
  `PASS` / `GATE FAIL` is issued, and holds that four of the five `U_s` points are single-grid
  values with **no triple ⇒ `NOT A RESULT` for a grid-gated quantity**. The rung's verdict is
  therefore **`PENDING`**, and `PENDING` is on the chief's own do-not-render list.
- **For rendering:** Sanaa's words are *"run converged or is within bands"*, which attaches to
  **a run**, not to a rung's gate. Twelve level directories are marked `DONE`
  (`verification/runs/navier_class/PRD/DONE.us*`), and a rule-4-complete converged *level*
  may satisfy her sentence while its *rung* is still `PENDING`.

**These two readings differ, and the difference is Sanaa's to settle, not an agent's.** The
honest statement of the gap: *the render trigger is written against runs; the lab's verdict
vocabulary is written against rungs, and a rung can be `PENDING` while a level inside it is
complete and converged.* **Recorded as an open question, with no render performed under either
reading.**

### 7.2 THE ROW THE ORDERED LIST DID NOT NAME

**The one §2 case that unambiguously clears the render test today is `SUP_BOOSTER E2`** — and
it appears in neither the ordered case list this lane was given nor in the demo-case
instruction. It is a closed `PASS` (`verification/campaign/SUP_BOOSTER_E2_VERDICT.md`, freeze
commit `34797ce9`). **Flagged because a render backlog built from the ordered list would have
missed the only clean candidate in it.**

**Constraints carried, not yet acted on:** offscreen `pvpython`/`pvbatch`, **zero solver
compute**, not charged to any cap, **touching no graded tree and never a running solver**,
outputs under `docs/campaigns/<FAMILY>/demo/` named with case id, level and record sha, paths
recorded on the case record. **No rendering has been started** — the instruction was to commit
this table first.

---

*Authored by a cfd `lab-lane`, 2026-09-11. Zero compute. No verdict issued. No submission made.*
