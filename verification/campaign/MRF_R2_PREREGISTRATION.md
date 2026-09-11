# MRF_R2 — Rushton power number `Np` on a GEOMETRICALLY SIMILAR mesh family

<!-- ===================== STRIKABLE DRAFT BANNER — BEGIN ===================== -->
> **STATUS: DRAFT / UNFROZEN. NO COMPUTE HAS RUN UNDER THIS DOCUMENT. NOT A GATE YET.**
> Authored by a cfd lab-lane, 2026-09-10; fine mesh built 2026-09-11 (§6.1). **No sha
> binds it** and **NO SOLVE HAS RUN — no verdict may be read from it.** The FINE MESH IS
> BUILT, which §6 (MESH_STANDARD §8.1) REQUIRES before a freeze; building a mesh is not
> compute under the gate and the gates are still open. The FREEZE
> (§13) and the graded launch are the cfd-supervisor's check-4; the grader diff-read is
> the supervisor's check-1. **Neither has been done.** Until the freeze commit every
> gate, threshold, cap and band below is amendable and carries no evidentiary weight
> (CLAUDE.md rule 2). **This banner is one block and is struck whole at the freeze.**
<!-- ====================== STRIKABLE DRAFT BANNER — END ====================== -->

- **Case family:** `navier_class` / `MRF` (rotating machinery, Case 2 of the Navier-class parity pack).
- **Rung:** R2 — the L4 successor to R1, which graded **NOT A RESULT**.
- **Predecessor:** `verification/campaign/MRF_R1_PREREGISTRATION.md` (frozen `ceacb3a2`, blob `54aecef3`); verdict committed at `6af542b6`; graded row `verification/runs/navier_class/MRF/MRF_R1_GRADED_ROW.json`.
- **Inputs / grader / mesh scripts:** `cases/navier_class/MRF/`
- **Outputs (none yet):** `verification/runs/navier_class/MRF/R2/`

---

## 1. What R1 returned, and the ONE change R2 makes

**R1's verdict was `NOT A RESULT`, and it was not a failed run.** All three levels
completed rule 4 cleanly (rc=0, `End`, 4000 `ExecutionTime` lines, last time == `endTime`,
all six fields present and newer than `0/`), the planted-zero control passed, and all three
levels were measured `CONVERGED` / `PLATEAUED`. The **grid triple** is what refused:

| R1 level | cells | `Np` (at `endTime`) |
|---|---:|---:|
| coarse | 154,715 | 4.23802896 |
| medium | 448,972 | 4.26804456 |
| fine | 1,273,803 | 4.45299084 |

delivered `r21 = 1.415667`, `r32 = 1.426359`, graded `form="auto"` → **unequal (Celik)**;
triple state **DIVERGENT**, observed order **p = −5.2311** at dim 3; **no GCI quoted**
(the instrument refuses one on a non-monotone triple). The band verdict was computed
first and unconditionally and was **PASS** (4.453 ∈ [4.0, 6.0]); the one-way gate turned
it into **NOT A RESULT**, which is the only direction that gate may turn.

**The tell:** `e32 = +0.030016`, `e21 = +0.184946`, so **`e21/e32 = 6.16` — the differences
GREW with refinement.** Refining moved the answer further, not less. The family is not in
the asymptotic range. This was checked to be independent of which torque sample is taken:
on the S12 window means instead of the `endTime` sample the triple is still DIVERGENT
(p = −2.9910, `e21/e32` = 2.83).

### 1.1 THE ONE CHANGE

> **R2 specifies the refinement shell AND EVERY FEATURE ZONE IN PHYSICAL THICKNESS
> (metres), so that the three levels are geometrically similar. That is the single
> change.**

R1's amendment A1.1 recorded the mechanism before the compute was spent:
`nCellsBetweenLevels` is a buffer measured **in cells, not in physical thickness**, so as
the base cell shrinks the refinement-transition shell shrinks with it and contributes
proportionally fewer cells. The levels therefore did not resolve the same features in the
same proportion, which is the definition of a non-similar family — and a Roache/Celik
extrapolation assumes similarity.

**Everything else is held fixed, and must be, or the experiment measures nothing:**
same solver (`simpleFoam`, OpenFOAM v2606), same numerics, same k-omega SST with wall
functions, same MRF setup and `nonRotatingPatches` discipline, same frozen-rotor blade
position, same flat rigid lid, same geometry, same `Re = 5.0 × 10⁴`, same `endTime` 4000
(but see §9), same grading path, **and the same gate, band and reference.**

---

## 2. Reference value and REFERENCE TIER — UNCHANGED from R1

`Np_ref = 5.0` (turbulent plateau, standard fully-baffled tank, 6-blade Rushton disc
turbine), documented literature spread ≈ 5.0–6.0. **REFERENCE TIER: bounded-agreement
(rank 3), provisional and capped by evidence state** — the reference is a **manifest
correlation value, NOT yet title-verified** (Rushton/Costich/Everett 1950; Zhou & Kresta
1996; Wu & Patterson 1989 as the later experiment-validated upgrade path). The case
carries the disavowal: *"reference is a manifest correlation value, not yet
title-verified; NOT validated against a wind-tunnel/rig experiment."* This lane does not
edit `verification/credibility/reference_tier_registry.json`; registration there is the
verification supervisor's, and only once the case completes.

---

## 3. THE GATE — UNCHANGED from R1, and deliberately so

**Gate primary quantity:** fine-level power number `Np`, graded by
`scripts/roache_triple.py` in its exact rule-5 order, at **dim = 3**, **Fs = 1.25**.

    PASS band:  Np ∈ [4.0, 6.0]        reference Np_ref = 5.0

- finest triple CONVERGING **and** `Np ∈ [4.0, 6.0]` → **PASS**
- finest triple CONVERGING **and** `Np ∉ [4.0, 6.0]` → **GATE FAIL** (a result)
- triple not CONVERGING, or any level not converged/plateaued → **NOT A RESULT**
- a run cannot complete, or the reference cannot be title-verified when required → **BLOCKED** at core-minutes actually spent
- not yet run → **PENDING: `verification/runs/navier_class/MRF/R2/`**

**THE BAND IS NOT TOUCHED, AND THAT IS THE POINT.** R1's value landed *inside* [4.0, 6.0]
and the gate refused it anyway. A successor that quietly widened the band, moved the
reference, or softened the label would be worthless as evidence — it would be a document
tuned to an answer already seen. `Np = 4.45299084` is on the record; the band that would
have admitted it is unchanged; only the mesh family changes.

`Np = 2πQ / (ρ N² D⁵)` with `Q = |axial moment|`. Constants, from §4 of the R1
registration and unchanged: **ρ = 998 kg/m³**, **N = 5.0 rev/s**, **D = 0.100 m**,
**axis = z**.

---

## 4. THE ONE CHANGE, specified concretely

**CORRECTED 2026-09-11, BEFORE ANY R2 COMPUTE AND BEFORE THE FREEZE, after reading
`cases/navier_class/MRF/system/snappyHexMeshDict` line by line rather than assuming its
contents.** An earlier draft of this section listed four controls to be changed. **Three
of them were already similar and changing them would have made R2 a four-change
experiment that could not attribute its own result.** What the dictionary actually
contains:

| control in R1's dict | is it similar across levels? | R2 action |
|---|---|---|
| `nCellsBetweenLevels 3` | **NO — a count of CELLS.** Shell = 3·Δ_L, so **30.0 / 20.0 / 13.3 mm** coarse→fine. **This is the non-similarity.** | **CHANGED — the one change** |
| `impellerZone` `searchableCylinder` `point1 (0 0 0.060) point2 (0 0 0.140) radius 0.070` | **YES — already in metres**, byte-identical at every level | untouched |
| `refinementSurfaces` / `features` levels (`impeller (2 3)`, `baffles (1 1)`, …) | **YES** — a refinement *level* halves the local cell relative to `Δ_L`, so it scales with the family | untouched |
| `addLayers false` | **N/A — R1 HAS NO PRISM LAYERS** | **left OFF.** Adding a layer stack would be a SECOND change and would confound the test |

> **THE ONE CHANGE, exactly: `nCellsBetweenLevels` is set PER LEVEL so the
> refinement-transition shell is CONSTANT IN METRES (~31 mm) at all three levels.**

| level | background block | base cell `Δ_L` | `nCellsBetweenLevels` | **delivered shell** |
|---|---|---:|---:|---:|
| coarse | 32 × 32 × 36 | 10.0000 mm | 3 | **30.00 mm** |
| medium | 51 × 51 × 57 | 6.2745 mm | 5 | **31.37 mm** |
| fine | 82 × 82 × 92 | 3.9024 mm | 8 | **31.22 mm** |

Shell spread **max/min = 1.046 (4.6 %)**, inside the 5 % invariant. Background cells are
cubic to within 0.66 % at every level (`Δz/Δx`: 1.0000 / 1.0066 / 1.0027); exact cubes at
all three simultaneously are unobtainable because `NZ = 1.125·NX` forces `NX` to a
multiple of 8, and no multiple-of-8 progression is geometric in 1.6 at a workable size.

**The invariant checked at build, per level, READ BACK FROM THE BUILT MESH and never from
the requested value** (`MESH_STANDARD` §9.2, the similarity read-back clause — the
requested value is the one that lied in the F12 branch-flip defect): the delivered cell
count, and the shell thickness in metres, equal across levels to within 5 %.

**Only the base cell size `Δ_L` and the shell's cell count change between levels, and
they change together so the shell's PHYSICAL size does not.** That is what makes the
family similar.

### 4.1 A SILENT-TRUNCATION TRAP CLOSED AT THE SAME TIME (not a physics change)

R1's dict carries `maxLocalCells 2000000` and `maxGlobalCells 6000000`. R1's fine level
delivered 1,273,803 cells and never approached them. **R2's fine level refines through a
shell 8 cells thick instead of 3 and will deliver materially more, so those caps could
bind — and when snappyHexMesh hits a cell cap it STOPS REFINING AND CONTINUES, producing
a mesh that is quietly less refined than requested.** That failure would not crash, would
not appear in `rc`, and would destroy the very similarity this rung exists to create,
while looking like a successful build.

**Raised to `maxLocalCells 40000000` / `maxGlobalCells 80000000`, and the builder ASSERTS
the delivered count is below the cap and aborts if it is not.** This changes no physics
and no gate: it removes a silent failure mode. Disclosed here rather than left as an
unexplained diff.

---

## 4A. LAUNCH ORDER: FINE FIRST — and what a fine-alone run may and may not say

**Sanaa, 2026-09-11 00:30Z, byte-exact: *"MRF: then the run i want to be run (if its not
ran already) is the one with the fine mesh not the coarse."*** R2 therefore builds and
launches **fine first**; coarse and medium follow afterwards to complete the triple.

> **REGISTERED PLAINLY, BEFORE THE RUN: A FINE-ALONE RESULT IS NOT A GRID-CONVERGENCE
> STATEMENT AND MAY NOT BE PRESENTED AS ONE.**
>
> A Roache triple needs three levels; `roache_triple.grade_ladder` refuses fewer
> ("a Roache triple needs at least three levels"). **`grade_mrf_np.py` is therefore NOT
> run on fine alone** — there is no verdict for it to produce and invoking it would
> produce only a refusal.
>
> **The registered outcome of the fine-alone run is exactly three things, and nothing
> more:**
> 1. the fine-level **`Np` value** at `endTime`, from the frozen header-driven,
>    fail-closed `moment.dat` read path under its live planted control (rule 3);
> 2. its **`iterative_state`** and **`plateau_state`**, measured by S12 of
>    `MONITOR_STANDARD` verbatim (§8), with the drift and monotone numbers printed;
> 3. its **rule-4 completion evidence** — all seven clauses of §7.
>
> **No order `p`, no GCI, no CONVERGING/DIVERGENT state, no PASS and no GATE FAIL.** The
> case's display state until the triple is complete is
> **`PENDING: verification/runs/navier_class/MRF/R2/`**.
>
> **In particular: an `Np` landing inside [4.0, 6.0] on the fine level alone is NOT a
> PASS.** R1 already demonstrated why — its fine `Np` of 4.45299084 was inside the band
> and the graded verdict was still `NOT A RESULT`, because the band verdict is computed
> first and the rule-5 gate then overrides it one-way. Quoting a single level's in-band
> value as if it were the gate is the exact error the one-way gate exists to prevent.

The triple grades only when coarse, medium and fine are all complete, and the comparator
diff-read at that point is the cfd-supervisor's check-1.

---

## 5. THE REFINEMENT RATIO — nominal **r = 1.6**, and why

### 5.1 The r²–r³ band (DrivAer lane, 2026-09-10)

A snappyHexMesh family scaled by nominal linear factor `r` does **not** deliver a cell
ratio of `r³`. Surface-banded cells scale as **r²**, volume-filled cells as **r³**, so the
delivered cell ratio lands **between r² and r³**, and the delivered LINEAR ratio that
`roache_triple.representative_h` computes (`h = N^(−1/3)`) therefore lands between
**r^(2/3)** and **r**.

| nominal r | worst case delivered `r^(2/3)` | best case delivered `r` | margin over the Celik floor 1.3 |
|---|---:|---:|---:|
| 1.5 | **1.310** | 1.500 | **+0.8 % — too thin** |
| **1.6** | **1.368** | 1.600 | **+5.2 %** |
| 1.7 | 1.424 | 1.700 | +9.6 % |
| 2.0 | 1.587 | 2.000 | +22 % |

**R1's measured effective exponent, from the delivered family:**
`ln(1.415667)/ln(1.5) = 0.857` and `ln(1.426359)/ln(1.5) = 0.876`. R1 sat at ≈ **0.87**,
i.e. toward the volume-dominated end of the band but not at it.

### 5.2 The choice, and the honest correction to the reasoning

**Registered: nominal r = 1.6.** Reasons, in order:

1. **The worst case clears the floor.** Even at pure surface scaling (exponent 2/3) the
   delivered ratio is 1.368, **5.2 % above Celik's r ≥ 1.3 minimum**. At R1's measured
   exponent 0.87 the expected delivered ratio is `1.6^0.87 ≈ 1.505`, **15 % above the
   floor.** A nominal 1.5 has only 0.8 % of worst-case margin and is rejected for that
   reason alone.
2. **Physical-thickness specification should push the exponent UP, not down.** Holding the
   shells constant in metres means the shell contributes a constant *volume*, so its cell
   count scales as `r³` like the bulk. The family should therefore behave *more*
   volume-dominated than R1's 0.87, moving delivered toward 1.6 and further from the
   floor. The 2/3 worst case is retained as the conservative bound, not the expectation.
3. **Cost.** r = 1.7 buys 4.4 points more floor margin for ~31 % more compute (§11), which
   is not warranted when 1.6's *worst* case already clears.

**A CORRECTION TO THE RECORD, made here rather than inherited silently.** It is tempting
to say the r ≥ 1.3 floor "is what caught R1". **It is not.** R1's delivered ratios were
1.415667 and 1.426359, **both comfortably above 1.3**; neither ever approached the floor.
What caught R1 was (a) the **inequality** of the two ratios — gap 1.069e-02 against
`EQUAL_RATIO_TOL = 1.0e-9`, which A1.1 caught *before* compute and routed to the unequal
Celik path, and (b) the **DIVERGENT** triple state. The floor risk is real and prospective
and is why r = 1.5 is rejected here; it is not R1's post-mortem. Recording the distinction
because a successor built on a misdiagnosis is worse than no successor.

### 5.3 DELIVERED RATIOS ARE RECORDED, NEVER NOMINAL

The nominal 1.6 above is a **build target and nothing else.** The graded record carries
the ratios computed from the **delivered** cell counts by
`roache_triple.representative_h`, cross-checked by a volume-based
`h = (V/N)^(1/3)` read from `checkMesh` (independent of the count identity), exactly as
A1.1 did for R1. **No nominal ratio appears in any grading arithmetic.**

---

## 6. BUILD-ACCEPTANCE CRITERIA — checked BEFORE the freeze, pre-compute

`MESH_STANDARD` §8.1 (BUILD BEFORE FREEZE) applies: **this document may not be frozen
until all three levels are built, `checkMesh`'d and shown admissible.** Registered
acceptance criteria, all checked at build time and all **pre-compute**, so a family that
fails them is rebuilt rather than graded:

1. **Hard mesh gates (`MESH_STANDARD` §3):** max non-orthogonality ≤ 70°, max skewness ≤ 4.
2. **Delivered ratio floor:** both `r21` and `r32` ≥ **1.35** (floor 1.3 plus margin).
3. **Delivered ratio similarity:** `|r21 − r32| ≤ 0.05`. *(This is a MESH acceptance
   criterion, not a grading threshold: the ladder is still graded `form="auto"`, which
   takes the unequal Celik path for any gap above 1e-9. R1 was graded on that path and R2
   will be too. The criterion exists so the family is demonstrably similar, not so the
   equal path can be used.)*
4. **Physical-similarity read-back (§4):** transition-shell thickness, feature-zone
   dimensions, first-cell height and total layer thickness equal across levels to within
   5 %, **read back from the built mesh**, never from the dictionary.
5. **§6 mesh birth certificate** per level: `points_sha256`, cell count, max
   non-orthogonality, max skewness, `max_aspect_ratio` (non-null), and derived whole-mesh
   `cell_volume_ratio`, read from that level's own `log.checkMesh` under a planted control.

**A family failing 1–4 is rebuilt before any graded compute; that is legal because it is
pre-compute (rule 2).** After the freeze, no rebuild.

### 6.1 FINE LEVEL — BUILT 2026-09-11T01:14Z, MEASURED, PRE-FREEZE

Built by `cases/navier_class/MRF/build_level_r2.sh` at
`verification/runs/navier_class/MRF/R2/fine`; all stages rc=0
(blockMesh / surfaceFeatureExtract / snappyHexMesh / topoSet / checkMesh), build wall
637 s serial ≈ **10.6 core-min**, snappy peak RSS **2.99 GB**.

| quantity | measured | gate | |
|---|---:|---|---|
| **delivered cells** | **2,418,780** | — | checkMesh `cells: 2418780` **==** `constant/polyMesh/owner` header, cross-checked |
| max non-orthogonality | **48.618** (avg 5.215) | ≤ 70 | **PASS** |
| max skewness | **3.2466** | ≤ 4 | **PASS** |
| max aspect ratio | 4.5248 | non-null (§11.4) | recorded |
| max cell openness | 4.436e-16 | — | recorded |
| dimensionality | `Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)` | 3D | **PASS** — quoted from that line explicitly, never from a grep on `directions` |
| `empty`/`wedge` in `constant/polyMesh/boundary` | **0 occurrences** | 0 | **PASS** |
| `impeller` cellZone | present (topoSet cylinder r=0.06, z 0.08–0.12) | required for MRF | **PASS** |
| cap binding | 2,418,780 ≪ `maxLocalCells` 40,000,000 | must not bind | **PASS — refinement was not silently truncated** (§4.1) |

**`***Concave cells (using face planes) found, number of cells: 26633` — `Failed 1 mesh
checks`.** Disclosed in advance in §6 and expected: it is an `-allTopology` check, it is
**not** one of the two hard gates, and it is a standing property of this snappyHexMesh
geometry. As a fraction it is **1.10 %**, continuing R1's monotone fall with refinement
(2.73 % / 2.01 % / 1.35 % at R1 coarse/medium/fine).

**THE DELIVERED COUNT IS 39 % ABOVE THE §11 TARGET of ~1,740,000, and that is reported,
not absorbed.** The 8-cell shell adds more than the projection assumed: R1's fine level
turned 419,904 background cells into 1,273,803 (×3.03), whereas R2's fine turns 618,608
into 2,418,780 (×3.91). **The projection's error was in the multiplier, not in the
background block.** §11's fine row is corrected accordingly below.

**Projection for the unbuilt levels, flagged as a PROJECTION and not a measurement.**
R2 coarse is byte-identical in configuration to R1 coarse (same 32×32×36 block, same
`nCellsBetweenLevels 3`; only the non-binding caps differ), so it is expected to deliver
**~154,715** cells again. Medium is expected at **~590,000**. Those give projected
delivered ratios **r32 ≈ 1.57, r21 ≈ 1.60** — both well clear of §6's 1.35 floor, with
`|r21 − r32| ≈ 0.03` inside the 0.05 criterion. **These are estimates; only the built
delivered counts are recorded in the grading arithmetic (§5.3).**

**Disclosed in advance, because R1 carried it:** every R1 level reported
`***Concave cells (using face planes) found` (4,216 / 9,036 / 17,212 cells, monotonically
falling with refinement). It is an `-allTopology` check, it is **not** one of the two hard
gates, and it is a standing property of this snappyHexMesh geometry. If R2 carries it too
that is expected and is not a new finding.

---

## 7. Completion rule (rule 4) — UNCHANGED from R1 §5

A level is **done** only if ALL hold: (1) `rc == 0` from an rc sidecar captured **inside**
the detached wrapper — and the sidecar is named **`rc`**, because `grade_mrf_np.py:251`
reads that exact filename and refuses the level outright without it *(R1's launcher wrote
only `RC.txt` and a triple that had run perfectly refused on a filename; the launcher now
writes both)*; (2) an `End` line; (3) `ExecutionTime` count == `round(endTime/deltaT)`;
(4) last written time == `endTime`; (5) fields **`U p phi k omega nut`** present at
`endTime` (the isothermal-incompressible analogue of rule 4's thermal list, disclosed so
it is not a silent departure); (6) every field at `endTime` **newer than the case's own
`0/`** — the age guard; (7) the grader **refuses (exit 2)** a case where a `0` or a time
directory already exists at launch.

**No `residualControl`**, for the R1 §5 reason: an early residual exit can never satisfy
clauses 3 and 4. `endTime` is a hard stop and convergence is judged on the graded
quantity, not on a residual block (L-24, S10).

---

## 8. Grader — UNCHANGED PATH

`cases/navier_class/MRF/grade_mrf_np.py`, on `scripts/roache_triple.py`. **The grading
path is not modified for R2.** At the R1 grading these were blobs `c128ad32` and
`78e56a3b`; the freeze block records the R2 values and the grade verifies the frozen file
is the file that ran. `form` is left at its default `"auto"` (the parameter is named
`form`, **not** `mode` — R1's A1.1 named it wrongly and the behaviour, not the wording,
is what was verified). Rule 3's live planted control on the actual `moment.dat` read path
is unchanged and remains a refusal, not a warning.

Per-level `iterative_state` and `plateau_state` are **measured** by
`cases/navier_class/MRF/measure_states_mrf.py`, whose plateau test is **S12 of
`docs/standards/MONITOR_STANDARD.md` verbatim** (trailing quarter, floored 20, capped
2000; fires iff |relative drift| ≥ 1e-3 **and** monotone fraction ≥ 0.90). Every threshold
and the window rule come from that standard; none is chosen for this rung.

---

## 9. SUB-FINDING 1 — fine's S12 drift limb was OVER in R1, and what R2 does about it

**On the face of this document, not in a footnote.** R1's measured S12 numbers:

| R1 level | relative drift | monotone fraction | S12 |
|---|---:|---:|---|
| coarse | +1.1519e-04 | 0.4715 | silent |
| medium | −4.8223e-04 | 0.5385 | silent |
| **fine** | **−1.1975e-03** | 0.5345 | **silent — but the DRIFT LIMB IS OVER** |

**Fine's |drift| = 1.1975e-03 exceeds S12's 1e-3 threshold by 1.20×.** S12 stayed silent
only because it requires **both** limbs and the monotone fraction was 0.5345, far below
0.90 — which the standard explains in terms ("a settled history wobbles without
displacement, a truncated one travels"; 0.53 is wobbling, not travelling). **The
`PLATEAUED` call was correct per the standard and is not revisited.** But fine was both
the least-settled level and the level carrying the divergence, and that is worth
registering rather than discovering twice.

**REGISTERED DECISION: `endTime` stays 4000 at all three levels, WITH A PRE-DECLARED
CONTINGENCY, declared here BEFORE any compute so it cannot be a post-hoc rescue:**

> **If R2's fine level reports S12 |relative drift| ≥ 1e-3 at `endTime` 4000 — whether or
> not S12 fires — the fine level is RE-RUN FROM `0` with `endTime = 8000`, and the 8000
> run is the graded one.** It is a re-run from zero, never a restart from 4000, so rule 4
> clauses 3 and 4 hold cleanly against the single pinned `endTime`. The contingency fires
> on the drift limb alone; the `PLATEAUED`/`NOT_PLATEAUED` state continues to be decided
> by S12's own two-limb rule and is not altered by this clause.

**Basis for 8000, stated honestly as an extrapolation and not a measurement:** R1's fine
drift was 1.20× the threshold at 4000 iterations, and drift decays as the solve approaches
steady state. Doubling the iteration count is the smallest round extension expected to
carry 1.20× of margin. **No measurement supports the specific factor of 2** — no fine run
past 4000 iterations exists. If 8000 also leaves |drift| ≥ 1e-3, that is a **finding about
the steady MRF formulation, not a licence for a third extension**, and R2's fine level
reports at the core-minutes spent.

---

## 10. SUB-FINDING 2 — THE HYPOTHESIS, AND WHAT WOULD FALSIFY IT

**On the face of this document.** R2 is a test of one hypothesis and is designed so that
it can fail.

> **H₁ (the hypothesis under test):** R1's DIVERGENT triple was caused by the **geometric
> non-similarity** of its mesh family — refinement controls specified in cells rather
> than physical thickness, so the levels did not resolve the same features in the same
> proportion. Because a Rushton `Np` is dominated by **blade-edge separation**, a family
> whose blade-edge resolution does not scale in proportion cannot be in the asymptotic
> range, whatever its nominal ratio.

**H₁ is a hypothesis. It has not been tested. R2 tests it.**

**COROBORATING RESULT** — H₁ survives if **all** of:
- the delivered family meets §6's acceptance criteria (both ratios ≥ 1.35, `|r21 − r32| ≤ 0.05`, physical similarity read back to 5 %); **and**
- all three levels are measured `CONVERGED` / `PLATEAUED`; **and**
- the finest triple is **CONVERGING** with a positive observed order in a physically
  admissible range, **0 < p ≤ 4** (a second-order-accurate scheme on a well-resolved
  family should land near 2; p above 4 is a coincidence of three points, not an order).

**FALSIFYING RESULT — registered explicitly, because this is the outcome that must not be
explained away:**

> **If R2's triple is again `DIVERGENT` (or `STAGNANT` / `OSCILLATORY`) while §6's
> acceptance criteria were met and all three levels are `CONVERGED` / `PLATEAUED`, then
> H₁ IS FALSIFIED. Geometric non-similarity was NOT the cause of R1's divergence.**

In that event the honest outcome is `NOT A RESULT` again, **and the rung's deliverable
becomes the falsification itself** — not a third mesh family. The next hypotheses, named
here so that reaching for one later is a registered step and not an improvisation, are:
**H₂** frozen-rotor position dependence (R1 §4 disclosed the blade position as an ungated
uncertainty; the test is a position-averaged or multi-position variant);
**H₃** the steady MRF formulation itself cannot deliver a grid-convergent `Np` for this
quantity, which is F8's finding on its own steady branch and would be a substantive
negative result about the method rather than about this mesh.

**A CONVERGING triple whose `Np` falls outside [4.0, 6.0] is `GATE FAIL` — a result, and
it corroborates H₁** (the family became gradeable) while failing the band. These are
independent outcomes and the registration does not conflate them.

---

## 11. COMPUTE (rule 12) — costed, and calibrated against R1's ACTUALS

Unit is **core-minutes = wall-s × ranks ÷ 60**. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5), so **every dollar figure is derived, not measured.**

**Unit cost, measured from R1 and not assumed:** coarse ran 871 s × 4 ranks = 58.07
core-min for 154,715 cells × 4000 iterations = **5.63e-06 core-s per cell-iteration**.
Coarse is used as the anchor because it ran with the least company; medium and fine were
contended.

**Concurrency factor, measured from R1 and applied here — this is the R1 calibration
lesson carried forward:** R1's per-level ratios were 0.88 / 1.14 / 1.24 for a total
**954.77 core-min against ~804 projected, ratio 1.19**, and the ratios track how much
company each level had and nothing else (fine measured 0.528 it/s under load against
0.689 it/s after medium retired, a 30 % recovery on the same decomposition). **The gap was
concurrency, not misprediction, so R2 applies a ×1.19 concurrency factor explicitly rather
than pretending to a better unit cost.**

Projected delivered family at nominal r = 1.6 and expected delivered ratio ≈ 1.505
(cell ratio ≈ 3.41 per step), coarse targeted at ~150 k:

**CORRECTED 2026-09-11 against the BUILT fine level (§6.1), pre-compute. The original
row is struck, not rewritten.**

| level | cells | endTime | est. core-min (anchor) | **× 1.19 concurrency** |
|---|---:|---:|---:|---:|
| coarse | ~154,715 *(projected)* | 4000 | ~58 | **~69** |
| medium | ~590,000 *(projected)* | 4000 | ~221 | **~264** |
| **fine** | **2,418,780 (MEASURED, §6.1)** | 4000 | ~908 | **~1,080** |
| meshing | fine build **measured 10.6 core-min**; three levels | — | ~21 | **~25** |
| **total** | | | | **~1,438 core-min** |
| ~~*struck: ~150,000 / ~512,000 / ~1,740,000, total ~1,121*~~ | | | | |

**Derived ≈ $1.23** at $0.0513/core-h — **derived, not measured**.
**Fine alone (the run Sanaa asked for first, §4A): ~1,080 core-min, derived ≈ $0.92.**

The overrun against the struck estimate is **+28 %**, and its cause is named rather than
absorbed: the 8-cell shell multiplies the background block by 3.91 where R1's 3-cell
shell multiplied it by 3.03 (§6.1). That is a **misprediction of the multiplier**, not
contention — the ×1.19 concurrency factor carried from R1 is applied separately and on
top, exactly so the two cannot be confused.

**Contingency cost (§9), priced but not assumed:** if fine re-runs at `endTime` 8000 it
costs a further **~777 core-min** (~$0.66 derived), taking the rung to **~1,898 core-min
(~$1.62 derived)**. Registered so the ceiling is visible in advance.

**`budget_gate: NONE — Sanaa 2026-09-10`**, verbatim: *"for all these 3D cases that still
need to run, i dont want to see any budget gates ( time or money)"*. MRF is a 3D
Navier-class case she named, and the M6CP1 §1 precedent applies. **No core-minute or
wall-clock cap STOPS this rung.** What is **not** suspended is the costing: the figures
above are the pre-registered estimate and are **calibration data, not a gate**. The actual
lands in `docs/COST_CALIBRATION.md` under rule 12's estimate-versus-actual comparison, in
core-minutes measured from the logs, with dollars derived and labelled so, and with
**contention named separately and never absorbed into the ratio**.

A **report-only** runaway monitor is set at **3× each level's own projection**
(**207 / 792 / 3,241 core-min** on the corrected table). It reports and never kills.

---

## 12. What this document is NOT

- It is **not frozen** — no sha, no committed grading-path hash. §13 is blank.
- **NO SOLVE HAS RUN under it.** The FINE MESH IS BUILT and measured (§6.1) — that is the
  §8.1 build-before-freeze precondition, not compute under the gate. Coarse and medium are
  NOT built. Every verdict shape above is a template keyed to data that does not exist.
- The coarse and medium cell counts in §6.1 and §11 are **projections, not measurements**,
  and are marked as such; only delivered counts enter the grading arithmetic (§5.3).
- The reference is **manifest-only**, not title-verified; the tier claim is provisional (§2).
- The cell counts in §11 are **targets, not measurements** — §6 forbids freezing until the
  three levels are built and shown admissible, and §5.3 forbids any nominal ratio entering
  the grading arithmetic.
- **H₁ is a hypothesis, not a finding** (§10), and the registration is written so that R2
  can falsify it.
- The `endTime` 8000 contingency factor (§9) is an **extrapolation, not a measurement**.

*Nothing below this line exists yet; addenda after the freeze may not alter any gate,
threshold, cap, band or label (rule 2).*

---

## 13. FREEZE BLOCK — cfd-SUPERVISOR, CHECK 4, UNDELEGATED

<!-- INTENTIONALLY BLANK. Check 4 is the cfd-supervisor's and may not be delegated to a
     lane. This lane has neither frozen this document nor built any mesh for it. The
     block below is the shape to be completed AT the freeze, after section 6's
     build-acceptance criteria have been met and read back from built meshes. -->

```
FROZEN BY:        <cfd-supervisor, date, check 4 undelegated>
FREEZE COMMIT:    <git log -1 --format=%H -- verification/campaign/MRF_R2_PREREGISTRATION.md>
REGISTRATION BLOB:<git rev-parse HEAD:verification/campaign/MRF_R2_PREREGISTRATION.md>
GRADED FAMILY:    <coarse / medium / fine DELIVERED cell counts>
                  <delivered r32, r21 -- measured, never nominal; graded form="auto">
GRADING PATH:     <grade_mrf_np.py blob, roache_triple.py blob>
GATE:             fine-level Np, PASS band [4.0, 6.0], rule-5 one-way gating, GCI at Fs = 1.25
BUDGET GATE:      NONE -- Sanaa 2026-09-10. Estimate ~1,121 core-min is CALIBRATION DATA.
HYPOTHESIS:       H1 (section 10) under test; falsifying result registered at section 10.
NO GRADED COMPUTE UNDER THIS DOCUMENT AS AT FREEZE, to be verified by a LIVE PLANTED
CONTROL: the time-directory reader must be shown able to SEE a known-positive time
directory elsewhere BEFORE its absence under verification/runs/navier_class/MRF/R2/
is believed (rule 3).
```

---

## §13 FREEZE BLOCK — cfd-SUPERVISOR, CHECK 4, UNDELEGATED

```
FROZEN BY:        cfd-supervisor (Opus 5), 2026-09-11, check 4 undelegated
FREEZE COMMIT:    the commit carrying this block; verify with
                  git log -1 --format=%H -- verification/campaign/MRF_R2_PREREGISTRATION.md
REGISTRATION BLOB:git rev-parse HEAD:verification/campaign/MRF_R2_PREREGISTRATION.md
LAUNCHED FIRST:   FINE, on Sanaa's 2026-09-11 00:30Z instruction -- "the run i want to
                  be run ... is the one with the fine mesh not the coarse."
                  Coarse and medium follow; only then does the triple grade.
FINE, AS BUILT:   2,418,780 cells. `Mesh has 3 geometric (non-empty/wedge)
                  directions (1 1 1)`, quoted from that line explicitly. Zero
                  empty/wedge patches. checkMesh `cells:` == the owner header.
                  max non-orthogonality 48.618 (gate 70) PASS
                  max skewness        3.2466 (gate 4)  PASS
                  BOTH HARD GATES PASS -- no non-conformance is declared or needed.
                  `Failed 1 mesh checks` = concave cells 26,633 = 1.10 %, NOT a hard
                  gate, continuing R1's monotone fall 2.73/2.01/1.35 -> 1.10 %.
THE ONE CHANGE:   `nCellsBetweenLevels`, the only genuinely non-similar control.
                  R1 held it at 3 CELLS -> shells of 30.0/20.0/13.3 mm. R2 sets it
                  per level, 3/5/8 -> 30.00/31.37/31.22 mm, spread 4.6 %, inside the
                  5 % invariant. Background blocks cubic to within 0.66 %.
UNCHANGED:        band [4.0, 6.0], reference 5.0, endTime 4000, form="auto",
                  solver, numerics, MRF setup, grading path.
FINE-ALONE OUTCOME, REGISTERED (§4A): a Roache triple needs three levels and
                  `grade_ladder` REFUSES fewer, so `grade_mrf_np.py` IS NOT RUN on
                  fine alone. The registered outcome is exactly three things: the Np
                  value under its planted control, its S12 iterative/plateau states
                  with drift and monotone printed, and its rule-4 completion
                  evidence. NO order, NO GCI, NO CONVERGING/DIVERGENT, NO PASS, NO
                  GATE FAIL. Display state stays PENDING.
                  AN IN-BAND Np ON FINE ALONE IS NOT A PASS, and R1 is the proof:
                  its fine Np of 4.45299084 sat inside [4.0, 6.0] and the verdict
                  was still NOT A RESULT.
BUDGET GATE:      NONE -- Sanaa 2026-09-10 (3D exemption). Fine alone ~1,080
                  core-min, derived ~$0.92; full triple ~1,438 core-min, ~$1.23.
                  +28 % on the struck estimate, attributed to MISPREDICTION OF THE
                  SHELL MULTIPLIER -- not contention, which stays separately named
                  as the x1.19 factor applied on top.
NO COMPUTE UNDER THIS DOCUMENT AS AT FREEZE, verified by a LIVE PLANTED CONTROL:
  the time-directory reader returned 2 on verification/runs/navier_class/MRF/coarse
    -- SHOWN ABLE to see a time directory before an absence is believed (rule 3);
  the same reader returned ZERO on verification/runs/navier_class/MRF/R2/fine,
    which holds no time directory, no rc and no solver log.
```

**AFTER THIS FREEZE THE GATES ARE CLOSED.** Changes land only as dated addenda that cannot alter a
gate, threshold, cap, band or label.

---

## ADDENDUM 1 — 2026-09-11 — THE `endTime` 8000 RELAUNCH, ALL THREE LEVELS, FROM `0`

**Document version: FROZEN v1.0 (freeze commit `558a430a`, blob `dba6e43a`) → v1.1 with this addendum.**
Authored by a cfd lab-lane, 2026-09-11T16:25Z, **BEFORE any compute under it.**

### A1.0 — The frozen-file assertion, PROVED and not asserted (rule 6)

**`lines whose number changed above this section: 0`.**

Not offered as a claim. The 600 lines above this heading are byte-identical to the
committed blob, and the proof is a hash, not an assurance:

| what | value |
|---|---|
| registration blob (git sha1), freeze commit `558a430a` | `dba6e43ac046ae642eae259efad524cb801a6004` |
| `git show HEAD:verification/campaign/MRF_R2_PREREGISTRATION.md \| sha256sum` | `2942e35143364e533731e8e157987c5b4a0fcbc2163fb3ba6acd2045f5348041` |
| `head -n 600 <this file> \| sha256sum` **after this addendum was appended** | `2942e35143364e533731e8e157987c5b4a0fcbc2163fb3ba6acd2045f5348041` |
| bytes above this section | 36,063 — the byte count of the frozen file, which ends in `\n` |

The two sha256 values are equal, so every pre-existing line is unmoved and unedited.
Anyone may re-run those three commands; the check fails loudly if a byte above moved.

### A1.1 — THE RULING [lab-attributed]

**Recorded by the cfd-supervisor on `docs/LAB_STATE.md` block 140.** §9's contingency is
executed **literally on fine** and **the same remedy is extended to coarse and medium**:
all three levels re-run **from `0`** at **`endTime` 8000**, and **the 8000 family is the
graded one**.

**Why, in the supervisor's reason:** the deliverable is a **triple**. A family that
breaches its own drift limb at **every** level yields a DIVERGENT triple that cannot
distinguish *"this family diverges"* from *"this family is not finished"*. Re-running one
level of three would produce levels that no longer share a convergence history — the
comparison would then be between an 8000-iteration fine and two 4000-iteration siblings,
and the grid-convergence claim would be contaminated by an iteration-count difference that
no Roache triple can separate from a mesh effect.

**The condition that fired, re-measured by this lane rather than accepted** — `measure_states_mrf.py`'s
own S12 functions, imported unmodified, applied to the three R2 `moment.dat` files, with
that reader first shown able to see a planted `1.234e-03` (rule 3, PASS, reader returned
`1.234e-03`):

| level | S12 relative drift at 4000 | monotone fraction | ≥ 1e-3 ? | S12 two-limb state |
|---|---:|---:|---|---|
| coarse | **+1.3001e-03** | 0.5195 | **YES, 1.30×** | SILENT → `PLATEAUED` |
| medium | **+4.9190e-03** | 0.4935 | **YES, 4.92× — the worst level** | SILENT → `PLATEAUED` |
| fine | **−4.2576e-03** | 0.4675 | **YES, 4.26×** | SILENT → `PLATEAUED` |

Artifacts: `verification/runs/navier_class/MRF/R2/{coarse,medium,fine}/postProcessing/impellerForces/0/moment.dat`.
The §9 limb fires **on the drift limb alone**, exactly as §9 wrote it; the `PLATEAUED`
calls above are S12's own two-limb verdict and are **not** revisited or overturned here.

**§9 registered the contingency for fine. It did not contemplate all three breaching.**
That is stated plainly rather than smoothed over: the extension to coarse and medium is a
**supervisor ruling of 2026-09-11, not a clause of the frozen document**, and it is
labelled `[lab-attributed]` for exactly that reason.

**THERE WILL BE NO 16000.** §9 already settled it — *"If 8000 also leaves |drift| ≥ 1e-3,
that is a finding about the steady MRF formulation, not a licence for a third extension."*
This addendum does not reopen that and no third extension may be proposed under it.

### A1.2 — WHAT THIS ADDENDUM DOES NOT ALTER, AND WHAT IT DOES

**IT ALTERS NO GATE, NO THRESHOLD, NO CAP AND NO LABEL.** Specifically and by name:

- **Gate** — unchanged: fine-level `Np`, one-way rule-5 grid gating, GCI at Fs = 1.25.
- **Threshold / band** — unchanged: PASS band **[4.0, 6.0]**, reference 5.0, tier unchanged (§2, §3).
- **Threshold, S12** — unchanged: |relative drift| ≥ 1e-3 and monotone ≥ 0.90, MONITOR_STANDARD S12.
- **Cap** — unchanged: `budget_gate: NONE` (Sanaa 2026-09-10, 3-D exemption). No cap is created, raised or lowered here.
- **Label** — unchanged: the rule-1 vocabulary, and the one-way direction of §3's gate.
- **Grading path** — unchanged: `cases/navier_class/MRF/grade_mrf_np.py`, sha256
  `2a443bfe731ea43e2fe1cab5dbe692e9bf935c751bef463ea585409d7f63f08d`, verified byte-identical
  to its HEAD blob as this addendum was written.
- **Solver, numerics, MRF setup, mesh** — unchanged. The 8000 family reuses the 4000
  family's `constant/polyMesh` **byte-for-byte**, asserted by the launcher's own md5 over
  `points faces owner neighbour cellZones`. No level is re-meshed, so the geometric
  similarity this rung exists to establish is carried over exactly rather than rebuilt.
- **Rank counts** — unchanged per level (coarse 2, medium 2, fine 6), deliberately, so the
  decomposition is not a second thing that changed.

**WHAT IT DOES ALTER, and this is the whole of it:**

1. **`endTime`: 4000 → 8000**, on **all three levels**, each **re-run from `0`** — never a
   restart from 4000, so rule 4 clauses 3 and 4 hold cleanly against a single pinned `endTime`.
2. **Which artifacts grade:** the 8000 family. The 4000 family is **retained, not deleted,
   not superseded in the record** — it is the measured evidence that the contingency fired,
   it is cited by `verification/runs/navier_class/MRF/R2/MRF_R2_TRIPLE_AT_4000.json`, and
   its verdict **`NOT A RESULT`** at `endTime` 4000 stands as a graded fact.
3. **Where the 8000 family lives:** a new subtree, **not** on top of the 4000 trees.

### A1.3 — WRITTEN BEFORE COMPUTE: the run directories that DO NOT EXIST (rule 2)

Rule 2 requires the condition and **how it was checked**. Checked on disk at
**2026-09-11T16:22:37Z**, before any staging and before any solver:

| directory | state at 16:22:37Z |
|---|---|
| `verification/runs/navier_class/MRF/R2/ET8000/coarse` | **ABSENT** |
| `verification/runs/navier_class/MRF/R2/ET8000/medium` | **ABSENT** |
| `verification/runs/navier_class/MRF/R2/ET8000/fine` | **ABSENT** |

`verification/runs/navier_class/MRF/R2/` at that moment held exactly:
`COST_CALIBRATION_ROW_PENDING.md`, `LIMB6_AGE_GUARD_STRENGTHENING.md`,
`MRF_R2_TRIPLE_AT_4000.json`, `RUNAWAY_REPORT.txt`, `coarse`, `fine`, `medium` — **no
`ET8000`**. This addendum therefore cannot be a post-hoc rescue of a number it has not seen.

**Why `ET8000` and not `8000`.** A directory literally named `8000` sitting directly under
`R2/` is a **time-directory-shaped name**. `grade_mrf_np.py` finds time directories by
`os.listdir` over a case directory and keeps the numeric-named ones; a reader ever pointed
one level too high at `R2/` would see `8000` and read it as a time. The name is made
non-numeric so that mistake is not available. This costs nothing and removes a trap.

**The 4000 trees are preserved and were not touched.** Staging copies **out of** them and
**into** `ET8000/`; nothing is deleted, moved or overwritten. The launcher itself refuses
(exit 2) if `RC.txt` or any numeric time directory other than `0` is already present
(`cases/navier_class/MRF/launch_graded.sh` lines 61–64) and its header states *"NOTHING IS
EVER DELETED to clear this"* — which is the rule-4 age guard's precondition, not a
convenience.

### A1.4 — COST (rule 12), on the MEASURED rates of the 4000 family, not the lab's anchor

**Re-derived by this lane from the 4000 family's own `log.simpleFoam` files rather than
copied.** The rate is `ExecutionTime_last × ranks ÷ (cells × iterations)`, i.e. CPU-held
core-seconds per cell-iteration:

| level | ranks | cells | cells/rank | `ExecutionTime` at 4000 | re-derived rate (core-s per cell-iter) | figure on record |
|---|---:|---:|---:|---:|---:|---:|
| coarse | 2 | 154,715 | 77,358 | 2,805.12 s | **9.0654e-06** | 9.066e-06 |
| medium | 2 | 601,696 | 300,848 | 11,997.59 s | **9.9698e-06** | 9.968e-06 |
| fine | 6 | 2,418,780 | 403,130 | 22,203.9 s | **1.3770e-05** | 1.3770e-05 |

**The re-derivation AGREES** to four significant figures on all three levels (medium differs
by 0.02 %, rounding only). The lab's anchor **5.630e-06** was measured at 38,679 cells per
rank and is optimistic by **1.61× / 1.77× / 2.45×** here; it is **not** used below. Because
the 8000 family keeps the same ranks and the same meshes, **no cells-per-rank correction is
needed** — the rate transfers directly.

**The linear-in-iterations assumption is measured, not assumed.** Per-iteration
`ExecutionTime` over the last quarter against the first quarter: coarse ×1.056, medium
×1.105, fine ×1.039. Carrying the *last-quarter* rate forward for iterations 4001–8000 gives
189.1 / 804.7 / 4,333.0 core-min — within **2 %** of the linear-doubling figures below, so
doubling is supported by the run's own slope.

**ESTIMATE — two bases, both stated, neither hidden:**

| level | CPU-held floor (contention-free) | charged, at the 4000 family's own measured contention (×1.311) |
|---|---:|---:|
| coarse | 187.0 core-min | **381.7 core-min** |
| medium | 799.8 core-min | **1,272.1 core-min** |
| fine | 4,440.8 core-min | **5,460.8 core-min** |
| meshing | **0** — the 4000 meshes are reused byte-for-byte | **0** |
| **total** | **5,427.6 core-min** | **7,114.7 core-min** |

**REGISTERED ESTIMATE: 7,115 core-min charged, with a contention-free floor of 5,428 core-min.**
The 31.1 % contention uplift is the 4000 family's **own measured** figure (charged 3,557.34
core-min against CPU-held 2,713.81), taken from `verification/runs/navier_class/MRF/R2/COST_CALIBRATION_ROW_PENDING.md`
and reproducible from the per-level `CORE_MINUTES.txt`, `WALL_SECONDS_SOLVE.txt` and `RANKS.txt`.

**Dollars: 7,114.7 core-min = 118.58 core-h × $0.0513/core-h = $6.08 — DERIVED, NOT
MEASURED.** The floor derives to $4.64. **The box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5); the rate is owner-stated 2026-08-21/22. `cost_basis:
derived-from-core-minutes-at-owner-stated-rate; reported-by-owner; NOT measured.` 0 GPU-h.

**Two honest reasons the charged figure may be exceeded, declared in advance:** (1) this
lane runs its levels at **`nice 10`** (A1.6), which buys wall time back to the uncapped runs
already on the box and therefore **inflates charged core-minutes** relative to a nice-0
forecast; (2) box contention in this window is not the contention of the 02:00Z window the
uplift was measured in. Neither is a licence to re-forecast after the fact: the estimate
above is the registered one and the ratio actual/predicted will be reported against it.

### A1.5 — CAP-STOP EXEMPTION, AND THE CALIBRATION THAT STILL OWES

`budget_gate: NONE` — **Sanaa 2026-09-10 CASE PROTOCOL, 3-D demo runs are exempt from
cap stops.** The exemption is from the *stop*, not from the *accounting*: this run is costed
here **before** it starts (rule 12: a proposal with no cost is disqualified), and at
completion the **estimate-versus-actual comparison is owed** in the lab's measured unit —
actual core-minutes from the logs against the **7,115 core-min** registered above, ratio
stated, gap attributed, waste named separately and never absorbed into the ratio, landing as
a row in `docs/COST_CALIBRATION.md`. **A completion report without that comparison is
incomplete.** Note that this case's *previous* calibration row is already **BLOCKED** on a
pre-existing malformed id in that ledger (documented in
`verification/runs/navier_class/MRF/R2/COST_CALIBRATION_ROW_PENDING.md`); that blocker is not
cleared by this addendum and the 8000 row will meet the same refusal until it is repaired by
its owner.

### A1.6 — HOW THE RELAUNCH IS RUN, AND THE PRIORITY IT IS RUN AT

- **Launcher:** `cases/navier_class/MRF/launch_graded.sh`, invoked as
  `<RUNDIR> <RANKS> 8000 <STAGGER>`. **`endTime` is already a parameter of that script** —
  no script edit was needed or made for this relaunch. The bytes launched with are recorded
  in each level's `RELAUNCH_PROVENANCE.txt`.
- **Priority, set deliberately and recorded:** the levels are launched under **`nice 10`**.
  A capped or discretionary run must never compete at equal priority with an uncapped one,
  and three uncapped solves belonging to other teams were live on this box at launch. The
  nice value is set **at the launcher**, so it is inherited by `mpirun` **and by the
  `simpleFoam` rank processes**; **the verification is taken on the CHILD ranks' `ni` column,
  never on `mpirun`'s** — the two agree only when the nice came from the launcher, and
  reading the parent would hide exactly the case where it did not.
- **THE RUNG IS TAKEN FROM THE PATH, NEVER FROM THE BANNER.** That rule is not decorative
  here — see A1.7 — and it applies to `LAUNCH.log` as much as to `controlDict`.
  *Correction to a statement this lane was handed and checked:* the three graded R2
  `LAUNCH.log` files (02:10–02:21Z) already read `=== MRF graded launch`, rung-neutral; the
  mislabel `MRF_R1 graded launch` **on an R2 path** survives in exactly one place on disk,
  `verification/runs/navier_class/MRF/R2/fine/STOPPED_2RANK_ATTEMPT/LAUNCH.log` (01:36:57Z),
  which predates the fix. The R1 trees' own logs say `MRF_R1` and are correct. The rule
  stands on its own merits regardless of how many files currently violate it.

### A1.7 — DISCLOSURE: SIX `system/controlDict` FILES SHARE ONE sha256 AND ITS BANNER IS FALSE

**Verified on disk by this lane, 2026-09-11, before writing this paragraph.** Six
`system/controlDict` files — **the three R1 graded levels and the three R2 graded levels** —
are byte-identical:

```
sha256 a16a4a814675a414887c748856b4a1f68ef89a87b9e0b003bea0527b3803f467
  verification/runs/navier_class/MRF/{coarse,medium,fine}/system/controlDict      <- R1, GRADED
  verification/runs/navier_class/MRF/R2/{coarse,medium,fine}/system/controlDict   <- R2, GRADED
```

In that one file:

- **line 2** reads `| MRF_R1 controlDict. THIS COPY IS THE EXERCISE-SMOKE config: endTime 50, a |`
- **line 25** reads `endTime         4000;          // EXERCISE SMOKE (graded run: 4000, set by launcher)`

So the banner calls the file an exercise-smoke config at `endTime` 50 while the file it sits
in is the graded config at 4000, and it calls every copy `MRF_R1` including the three that
are R2. The case-source copies (`cases/navier_class/MRF/system/controlDict` and
`cases/navier_class/MRF/R2/system/controlDict`, sha256 `7b6a51a9884cc5a4…`) genuinely do
carry `endTime 50;` — the banner was true where it was written and became false in every
copy the launcher stamped.

**R1 IS ALREADY GRADED UNDER THIS FILE.** That is disclosed, not minimised. What the defect
does and does not reach:

- It does **not** change any computed number. The `endTime` actually in force is line 25,
  substituted by the launcher with a read-back assert (lines 93–97), and the R1 and R2
  graded rows both show 4,000 `ExecutionTime` lines and `last time == endTime == 4000`. The
  banner is a comment; OpenFOAM does not read it.
- It **does** mean a reader auditing provenance by the banner would conclude a graded run was
  a smoke test, and would attribute three R2 runs to R1. **That is why the rung is taken from
  the path.**

**NOTHING WAS EDITED.** Not one of the six. They are the graded inputs of two rungs and
editing them would rewrite the provenance of a completed grade to make a comment tidy. The
8000 family will inherit the same false banner, by copy, and this paragraph is its disclosure.

**The durable repair is not six edits.** One template was stamped six times by the tooling
that stages a run directory; six hand-edits would leave the stamp intact and the seventh copy
would be wrong again. **The repair belongs in whatever writes the copy** — either it stops
copying a banner that describes a different file, or it rewrites line 2 in the same
assert-and-read-back way it already rewrites line 25. **This lane does not make that change:**
it touches a path that stages graded runs, so it goes to the cfd-supervisor as a diff first
(supervision check 1, undelegable). Recorded here so it is not rediscovered a third time.

### A1.8 — REGISTERED PREDICTION, AGAINST INTEREST, TIMESTAMPED BEFORE THE DATA

**Registered 2026-09-11T16:25Z, before `ET8000` held a single iteration.** This block
**cannot alter any gate, threshold, cap or label** and is not consulted by the grader. It
exists so the 8000 grading cannot be read backwards.

**On record before the data, the cfd-supervisor does NOT expect the 8000 family to
converge.** This lane's own prediction, which is against the interest of the ~7,115
core-minutes it is about to spend:

- **P1 — at least one of the three levels will still show |S12 relative drift| ≥ 1e-3 at
  8000.** Stated with high confidence. The drift *grew* from R1 to R2 at every level
  (1.15e-4 → 1.30e-3 coarse, 4.82e-4 → 4.92e-3 medium, 1.20e-3 → 4.26e-3 fine) while the
  meshes grew; the residual tail of a steady MRF solve on a rotating-impeller tank is not
  obviously a decaying transient, and §9's own basis for the factor of 2 was declared an
  extrapolation with **no measurement behind it**.
- **P2 — the 8000 triple will again be DIVERGENT and the row will again grade
  `NOT A RESULT`.** Concretely: `Np(fine)` will remain above **both** `Np(coarse)` and
  `Np(medium)` by more than 2 %. Two independent mesh families (R1 at r ≈ 1.42, R2 at
  r ≈ 1.59) have now produced the same shape — coarse ≈ medium, fine markedly higher — with
  observed orders −5.2311 and −5.7784. That is the signature of something that appears at the
  fine level, not of a coin landing the same way twice.
- **P3 — each level's `Np` at 8000 will differ from its 4000 value by less than 2 %**
  (coarse 4.206205499, medium 4.221156836, fine 4.439168331).

**P2 and P3 are jointly the point.** If both hold, then doubling the iterations did not move
the physics and the divergence is a property of the mesh family or the formulation rather
than of under-convergence — which is precisely the **finding** §9 anticipated, and it will be
reported as a finding at the core-minutes spent, **not** as a licence for a third extension.
**If P2 fails and the triple grades CONVERGING, this lane was wrong and says so in the same
breath as the result.**

---

*A1.8 ends. Section A1.9 below completes Addendum 1. Nothing above line 600 was edited;
A1.0 proves it by hash rather than asserting it.*

---

## ADDENDUM 1, SECTION A1.9 — DISK FEASIBILITY: THE FINE LEVEL CANNOT START. `BLOCKED`.

**Measured 2026-09-11T16:25:16Z, before any of the 8000 family was staged.** This section is
part of Addendum 1 and alters no gate, threshold, cap or label. It records a **physical
constraint discovered while costing the relaunch**, and it is written here rather than
discovered halfway through a 5,460-core-minute solve that dies with the disk full.

The graded MRF configuration writes fields every 50 timesteps with `purgeWrite 0`
(`system/controlDict` lines 28–30). Nothing reads those intermediate writes: the grader
reads the **reconstructed** `endTime` directory and `postProcessing/impellerForces/0/moment.dat`,
`reconstructPar -latestTime` reconstructs only the last time, and the `processor*/` time
directories are never opened again. They are nevertheless kept in full.

**Measured footprint of the 4000 family** (`du` over the `processor*` trees, scaled by the
level's rank count):

| level | numeric time dirs written at 4000 | footprint per written step, all ranks | level total at 4000 |
|---|---:|---:|---:|
| coarse | 81 (`0` + 80 writes) | 20 MiB | 1.7 GiB |
| medium | 81 | 78 MiB | 6.4 GiB |
| fine | 81 | **314 MiB** | **28 GiB** |

**Projection to `endTime` 8000** (161 time dirs: `0` + 160 writes), same meshes, same ranks:

| level | projected 8000 footprint | fits? |
|---|---:|---|
| coarse | ≈ 3.1 GiB | yes |
| medium | ≈ 12.2 GiB | yes |
| **fine** | **≈ 49.1 GiB** | **NO** |
| **total** | **≈ 64.4 GiB** | **NO** |

**Free space on `/` at 16:25:16Z: 52 GiB (484 G total, 432 G used, 90 % full).** Coarse and
medium together need ≈ 15.3 GiB and leave ≈ 36.7 GiB. **Fine needs ≈ 49.1 GiB and cannot
have it**, and the margin does not exist even if coarse and medium were held back: 49.1
against 52 is a 6 % margin on a shared box where other teams are actively writing (the
SUBOFF_A1 ladder alone is about to mesh an L3 of roughly 25 M cells).

**REGISTERED CONSEQUENCE, declared before compute:**

1. **coarse and medium launch now**, at `endTime` 8000, from `0`, with **nothing changed but
   `endTime`** — no write-policy change, no config change of any kind.
2. **fine is `BLOCKED`** — not `PENDING`, not "deferred". It is blocked on a measured
   physical constraint, and the constraint is disclosed here rather than absorbed.
3. **No file was edited to clear it and nothing was deleted to make room.** Both available
   remedies — changing the run copy's write policy (`purgeWrite` / `writeInterval`), or
   reclaiming space from the 4000 family's `processor*` trees — touch either a graded run's
   staging path or a graded run's artifacts. **Neither is this lane's call.** Both go to the
   cfd-supervisor as a diff and a proposal (supervision check 1, undelegable; and
   "INSPECT, NEVER DELETE").
4. **For the record, so the supervisor is choosing between measured options:** a write-policy
   change alters **no computed number** — `simpleFoam` with `runTimeModifiable false` does not
   feed writes back into the solution, the graded quantity comes from a function object that
   writes every timestep into `postProcessing/`, and rule 4 requires fields at `endTime` only.
   It does change wall time slightly through I/O, i.e. it changes the **cost**, not the answer.
   That is an argument for the change being safe; it is **not** authority to make it.
5. **The triple cannot grade until fine runs.** `grade_ladder` refuses fewer than three
   levels (§4A), so the rung's display state stays `PENDING: verification/runs/navier_class/MRF/R2/`
   and **no verdict of any kind may be read from coarse and medium alone** — §4A already
   settled that, and R1's in-band fine `Np` of 4.45299084 under a `NOT A RESULT` verdict is
   the standing proof that an agreeable number is not a result.

*A1.9 ends. This is a constraint report, not a gate change.*

---

## ADDENDUM 1, SECTION A1.10 — `writeInterval` ON FINE: A DECLARED NON-CONFORMANCE, PROVED INERT

**2026-09-11, written and committed BEFORE fine's compute.** Alters no gate, no threshold, no
cap, no label. The 600 lines above the foot remain unmoved; A1.0's hash proof still holds and
is re-verified in this commit.

### The change

`verification/runs/navier_class/MRF/R2/ET8000/fine/system/controlDict:29`,
`writeInterval 50;` → `writeInterval 4000;`, set at **staging**, before the level had run.
Authorised by the cfd-supervisor 2026-09-11 on the condition that it be **measured, not
argued**. Cause: A1.9 — fine's intermediate writes are 49.1 GiB that nothing reads, against a
disk that has fallen from 52 to 45 GiB free (91 %) during this session. **Coarse and medium
were NOT touched**: they were already running, and `runTimeModifiable false` means a change
could not have taken effect in them, only corrupted the record.

### THE DECLARED NON-CONFORMANCE — three parameters vary across the graded triple, not one

| parameter | coarse | medium | fine | status |
|---|---|---|---|---|
| mesh | 154,715 | 601,696 | 2,418,780 cells | **the intended variable** — this is the grid triple |
| ranks | 2 | 2 | 6 | inherited from the 4000 family for comparability; **declared, not hidden** |
| `writeInterval` | 50 | 50 | **4000** | A1.9 disk constraint; **proved inert below** |

Neither ranks nor `writeInterval` varies *with h* in the way the Roache extrapolation reads:
both are fixed per level and identical between the 4000 and 8000 families. A reader must see
**both** extra parameters, not one.

### THE PROOF — and the first attempt at it FAILED, which is why there is a proof at all

**Attempt 1 (confounded, reported rather than discarded).** Two arms on the coarse mesh,
`endTime` 200, differing in one controlDict line. `moment.dat` **differed at byte 207, line 5 —
the first data row, iteration 1**, before any write can exist. The cause was not
`writeInterval`: `scotch` partitioned the same 154,715-cell mesh **differently on every
invocation** of one identical `decomposeParDict` (md5 `ea1336801ca0`, `method scotch;`, no seed,
no coeffs) — measured **77900/76815, 77011/77704, 77505/77210, 76965/77750**. A third arm,
identical to the first in every file, took its own partition and landed **6.554504e-03** away in
`Np` at iteration 200, *further* than the arm that also differed in `writeInterval`
(3.637007e-03). **`writeInterval`'s effect was invisible beneath the decomposition scatter.**
The registered decision rule — written before the comparison, at
`WRITEINTERVAL_CONTROL/CONTROL_PREDICTION_REGISTERED_BEFORE_RESULT.txt` — said a two-arm design
could not attribute such a difference to `writeInterval`, and it was right.

**Attempt 2 (the confound REMOVED, not argued past).**
`WRITEINTERVAL_CONTROL/CLEAN_D1_wi50/` and `CLEAN_D2_wi4000/`: `decomposePar` run **exactly
once**, the fully prepared tree copied with `cp -a` including `processor*/`, then one line
changed. Verified before either solve started — `diff -r` over the two arms returns **exactly
one line** and "no other difference"; `processor0` owner md5 `b4929f87d94f` and `processor1`
`1b017f468f70` **identical in both**.

**RESULT: `postProcessing/impellerForces/0/moment.dat` is BIT-FOR-BIT IDENTICAL.**
```
CLEAN_D1_wi50   sha256 b54c9004bf37f6d8eb573697d97296f3823019d272761acc05dea5252edc9877
CLEAN_D2_wi4000 sha256 b54c9004bf37f6d8eb573697d97296f3823019d272761acc05dea5252edc9877
```
Both rc=0, 200 `ExecutionTime` lines, one `End` each, 10.40 and 10.43 core-min.

**AND THE COMPARISON IS NOT BLIND (rule 3).** A zero from a reader not shown able to see a
non-zero is not evidence. `1.234e-09` was planted into `total_z` of the first data row of a
**copy**, and the same comparison **saw it**. The identity above is therefore evidence, not a
reader that cannot tell files apart.

**`writeInterval` IS INERT ON THIS SOLVER AND THIS CASE — MEASURED, NOT ARGUED.**

### A constraint that would bite a successor

OpenFOAM writes only at an output time, so **`writeInterval` must divide `endTime`**.
Demonstrated, not asserted: at `endTime` 200, D1 (`writeInterval` 50) wrote
`processor0/{0,50,100,150,200}`; **D2 (`writeInterval` 4000) wrote only `processor0/0`** —
nothing at 200, because 200 is not a multiple of 4000. `8000 % 4000 = 0`, so fine writes
`processor*/4000` and `processor*/8000`, `reconstructPar -latestTime` has 8000 to reconstruct,
and rule 4's "fields present at `endTime`" holds. **A successor picking a non-divisor would pass
every argument above and still fail rule 4.** Disk, measured on the arms: 143 MB against 61 MB.

### The larger finding this control produced, recorded because it outlives the rung

**`scotch` decomposition is not reproducible on this box, and no parallel run in this lab has
ever been checked for it.** This is **ours, not an OpenFOAM defect** — the library offers
deterministic methods and we asked for none; we chose `scotch`, never pinned the partition and
never verified reproducibility. It is **not** filed as a §2da defect.

Transferable form: ***a Roache triple is meaningless unless the level-to-level differences
exceed the run-to-run reproducibility floor — and this lab has never measured that floor for
any family.*** If the floor is the order of the signal, a `DIVERGENT` triple is exactly what
one would expect. **Candidate root cause for MRF grading the same way twice with a band-PASS
value underneath both times — candidate, not conclusion.** The measurement that tests it is
running at no cost: `ET8000/free_scatter_at_4000.py`, with its criterion (**5.095632e-04**,
nominal-r, the stricter of three) and its three branches **registered before the number
existed**. **Nothing in this addendum claims the R2 triple is inside noise, and nothing may.**

**The durable repair costs negative compute:** decompose once per level and archive
`processor*/constant/polyMesh` as a run artifact. The 8000 family's disk problem is 49.1 GiB of
`processor*` field writes we throw away, while the ~60 MB of `processor*/constant/polyMesh` that
would make the run reproducible is the part nobody kept. That goes to `MESH_STANDARD` as a
**proposal**; this lane does not amend a standard.

### Cost of the controls (rule 12)

**55.86 core-min** charged, 2 ranks, all rc=0: A 12.50, B 10.80, C 11.73, D1 10.40, D2 10.43.
Derived **$0.048** at $0.0513/core-h — **DERIVED, NOT MEASURED**; the box cannot read its own
billing. Not in the 7,115 core-min registered for the relaunch, and named separately here
rather than absorbed into it.
