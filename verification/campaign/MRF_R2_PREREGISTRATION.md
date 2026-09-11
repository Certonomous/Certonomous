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
