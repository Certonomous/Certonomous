# PERMISSION: NOT_FROZEN — DRAFT

**`A3GC` — ONERA M6 PRIMAL grid-convergence triple on a surface-refined family.**

Drafted 2026-09-10 by a `lab-lane` on the dafoam-supervisor's brief. **The freeze, the enqueue and
the launch belong to the dafoam-supervisor and are NOT taken here.** No gate, threshold, cap, band or
label in this file is registered until that supervisor freezes it by sha (`VERIFICATION_CHARTER.md`
§2b; `CLAUDE.md` rule 2). Until then this is a lane's prediction-first proposal.

**SUBMISSIONS PARKED.** Nothing in this item is sent, filed, posted or uploaded anywhere
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

---

## 0. WHAT THIS ITEM IS, AND WHAT IT DELIBERATELY IS NOT

**It is:** a three-level Richardson/GCI study of the **PRIMAL** ONERA M6 transonic solution — CD, CL
and the shock position — on a mesh family that is systematically refined **in all three directions**,
built from the surviving upstream surface mesh.

**It is not, and the omission is deliberate and stated here so no reader mistakes it for an evasion:**

- **No gradient is claimed, so no finite-difference table is owed.** `DAFOAM_CHARTER.md` §1 and §2
  bind *gradient* claims — *"a DAFoam gradient is not a result until a finite-difference table stands
  beside it at a step proved to lie in the plateau"*. A3GC computes no adjoint, requests no total
  derivative, and reports no sensitivity. Its outputs are primal functionals read from the primal's
  own force integration. **If any later reader wishes to quote a gradient from this item, the answer
  is that this item produced none.**
- **The ADJOINT grid convergence for A3 remains UNREGISTERED and UNREACHED.** It is not deferred by
  this document into some named successor; it simply does not exist. `DAFOAM_CHARTER.md` §7 and the
  A6 precedent make the reason concrete: the finest level here is ~6.4M cells, and an adjoint at that
  size is far outside this box (A6 predicted 95–116 GiB against 30 GiB at 579,072 cells). A3 rung-3's
  adjoint at 79,560 cells is itself still `GATE FAIL` / `NOT A RESULT` across four flagged rows
  (`../curriculum_A3R3PC/PREREGISTRATION.md`). **A3GC does not improve that and does not claim to.**
- **Primal-only is what makes the study deliverable at all**, and it is the question actually asked:
  the M6 is the case Sanaa keeps naming, and mesh convergence is the stated priority.

## 1. WHY A NEW FAMILY — THE EXISTING SWEEP IS NOT ONE

The four existing A3 levels — 10,920 / 21,840 / 42,120 / 79,560 cells — are **not a grid family**, and
this is measured, not argued:

| evidence | measurement |
|---|---|
| the surface mesh is shared | `surfaceMesh.cgns` is **byte-identical** across the n8, n15 and n28 levels — md5 `072cff77d15fa62c7b1fb2205c35358d`, 126,976 B, all three. *Identical hashes prove identity; that direction of the inference is safe (see §3.1 for why the converse is not).* |
| only one parameter moves | `genWingMesh.py` differs between levels in exactly one line, `"N": 8` vs `"N": 15` vs `"N": 28` — pyHyp's **wall-normal marching node count**, sitting beside `s0` and `marchDist`. |
| the scaling is 1-D | cells scale as ~n^1.0, not n^3. A 1.875× step in `n` gives the measured **2.0×** in cells, where a uniform 3-D refinement would give ~6.6×. |
| the mechanism, from the case's own script | `preProcessing.sh` in the sweep directories runs **three** `cgns_utils coarsen` passes where the 399,360-cell case runs **two**, with an in-file comment saying the extra pass exists to make the adjoint colouring fit in memory. |

All four levels are genuinely 3-D (each reports 3 geometric directions), so this is **not** the
one-cell-thick trap. It is the subtler one: a real 3-D mesh refined in only one of its three
directions.

**And it decides the physics.** A transonic shock is a **chordwise** feature. Refining only
wall-normal cannot sharpen it, so the measured shock-position disagreement on this case —
**+0.096 c at η = 0.20 falling to −0.001 c at η = 0.80**, with the computed shock weaker and smeared
outboard (Cp slope through the shock **4.70 vs 7.53** measured at η = 0.80, **9.49 vs 15.91** at
η = 0.90) — **cannot improve on the existing family however many levels are added to it.** A3GC exists
to refine the surface, which that family never did.

## 2. THE FAMILY — GENERATED AND CHECKED BEFORE REGISTRATION

### 2.1 Source geometry — present on disk, hashed

`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/m6_surfaceMesh_fine.cgns`
— **2,535,424 B, dated 2020-06-28**, md5 **`e6c853158d351de3f382ce5afa513997`**, 9 structured zones,
101,913 nodes. It is the upstream DAFoam release artefact (`preProcessing.sh` fetches it from
`github.com/dafoam/files/releases/download/v1.0.0/m6_surfaceMesh_fine.cgns.tar.gz`). It also survives
in six further run directories and as a `.tar.gz` (2,214,383 B) in nine. **The geometry source is NOT
lost, and A3 mesh convergence is not blocked on a missing input.**

### 2.2 Operator and toolchain — both inside the image, by SHA256

- `cgns_utils coarsen` — exact factor-2 coarsening in **both** surface directions.
- pyHyp via `genWingMesh.py` — hyperbolic extrusion, `marchDist 12.0`, `cMax 0.1`.
- Both live at `/home/dafoamuser/dafoam/packages/miniconda3/{bin/cgns_utils,lib/python3.10/site-packages/pyhyp}`
  inside **`dafoam-subpclu:v2` = `sha256:8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46`**.
  Neither is importable on the host. **The image is named by hash, never by tag**
  (`DAFOAM_CHARTER.md` §6: a version string is not an identity).

### 2.3 The coarsening chain — MEASURED, and it breaks at c3

Run 2026-09-10 in the image above, `--cpus=1`, working copies under
`/home/ubuntu/certonomous-runs/A3GC-mesh-family-probe/`:

| level | passes | nodes | **surface quad faces** | ratio to previous | smallest block dim |
|---|---|---|---|---|---|
| `c0` (= source) | 0 | 101,913 | **99,840** | — | 17 |
| `c1` | 1 | 26,001 | **24,960** | **4.000** | 9 |
| `c2` | 2 | 6,765 | **6,240** | **4.000** | 5 |
| `c3` | 3 | 1,827 | **1,560** | **4.000** | **3** |

Every step is **exactly 4.000** — a true factor-2 coarsening in both surface directions through c3.
**c4 would break it:** at c3 the smallest block dimension is already **3 nodes (2 cells)**, and blocks
of dims (3,3), (3,33) and (3,21) cannot halve again. This is the same failure the A6 lane measured on
its own chain (44,544 → 11,136 → 2,784 → 696 → **188**, the fourth step 3.702 instead of 4.000).
**Registered rule: no level beyond c3 may ever be described as a factor-2 coarsening of this surface.**

**Cross-check that the chain reproduces what actually ran:** c2 has 6,765 nodes and 6,240 faces, and
`logs_A3/logMeshGeneration.txt` for the shipped 399,360-cell case reports *"Total Nodes: 6765 / Unique
Nodes: 6309 / Total Faces: 6240"*. The chain regenerates the shipped surface exactly.

### 2.4 BODY IDENTITY — and this is why the family is c0/c1/c2, NOT c1/c2/c3

A refinement family must refine the **discretisation**, not change the **body**. Measured on the
coordinate arrays of all four levels:

| level | bbox min | bbox max | TE thickness, root | TE thickness, mid | TE thickness, tip |
|---|---|---|---|---|---|
| `c0` | (1e-06, −0.039426, 0.0) | (1.143957, 0.039426, 1.216405) | 6.8879e-04 | 6.8603e-04 | 7.1352e-04 |
| `c1` | (1e-06, −0.039426, 0.0) | (1.143957, 0.039426, 1.216405) | 6.8882e-04 | 6.8603e-04 | 7.1352e-04 |
| `c2` | (1e-06, −0.039426, 0.0) | (1.143957, 0.039426, 1.216405) | 6.8882e-04 | 6.8613e-04 | 7.1352e-04 |
| **`c3`** | (1e-06, **−0.039320**, 0.0) | (1.143957, **0.039320**, 1.216405) | **0.0** | (strip empty) | **0.0** |

**c3 collapses the trailing edge to zero thickness and loses 0.27 % of maximum wing thickness.** It is
**not the same discrete body** as c0/c1/c2. Under the reasoning the A6 lane recorded — a coarsest level
that closes a TE the finest resolves means the three levels are not the same body and **the triple is
dead** — c3 is excluded here **before** any solve, not discovered afterwards.

**THE REGISTERED FAMILY IS THEREFORE `c2` / `c1` / `c0`.** Bounding boxes agree to six decimals and TE
thickness agrees to four significant figures across all three.

### 2.5 The three levels

Wall-normal cells = `N − 1`. **This relation is verified on four existing meshes and is not assumed:**
6240 × 64 = 399,360 (fine, N=65); 1560 × 27 = 42,120 (n28, N=28); 1560 × 14 = 21,840 (n15); 1560 × 7 =
10,920 (n8).

| level | surface | faces | `N` | wall-normal cells | **volume cells** | ratio |
|---|---|---|---|---|---|---|
| **L3** coarse | `c2` | 6,240 | 17 | 16 | **99,840** | — |
| **L2** medium | `c1` | 24,960 | 33 | 32 | **798,720** | **8.000** |
| **L1** fine | `c0` | 99,840 | 65 | 64 | **6,389,760** | **8.000** |

**r = 2 exactly in all three directions; cell-count ratio is the exact integer 8 at each step.**
Surface face counts are **MEASURED** (§2.3). Volume cell counts are **PREDICTED-NOT-MEASURED** — they
follow from the verified `faces × (N−1)` relation, and stage 1 of this item measures them. Any
departure from 99,840 / 798,720 / 6,389,760 is a **launch-blocking refusal**, not a note.

### 2.6 The one non-systematic dimension, disclosed rather than buried

`s0` is **held fixed at 1.0e-4 on all three levels.** This is a deliberate, registered choice and it
makes the **near-wall spacing non-systematic**:

- **Why not scale `s0` by r (4e-4 / 2e-4 / 1e-4), which would be strictly systematic:** the shipped
  399,360-cell solution runs `useWallFunction: True` at measured y+ **min 5.69 / mean 33.75 / max
  103.52**. Scaling `s0` by 4 on L3 puts y+ mean near 135 and max near 414 — **outside the range in
  which the wall function is valid**. A strictly systematic family whose coarsest level is solving a
  different wall physics is a worse instrument than a family with one disclosed non-systematic
  direction.
- **Consequence, stated before the run:** the observed order `p` reported by this item is a **surface
  and outer-field order, not a full-field order**, and the document must say so wherever `p` appears.
- **The rejected alternative is named** so a later reader can re-open the choice: scaled-`s0`,
  rejected for the y+ reason above.

## 3. EXECUTABLE REFUSALS TO REGISTER AT FREEZE

Every one of these **refuses (exit 2) rather than degrades**.

### 3.1 `G-SYS` — the family is proved systematic, by COORDINATES, never by md5

Asserts, before any solve:
1. **Cell-count ratio is 8.000 ± 0.001 at each step** (the strong discriminator).
2. **Surface face-count ratio is exactly 4** at each step.
3. **Coordinate arrays of the three surface meshes DIFFER** — compared as point coordinates read out
   of each CGNS, level by level, not as file hashes.
4. **Bounding boxes agree** across the three levels to 1e-5 of root chord (body identity, §2.4).
5. **TE thickness at root/mid/tip agrees** across the three levels to 1 % (body identity, §2.4).

> **WHY THIS IS A COORDINATE COMPARISON AND NOT AN md5, AND DO NOT "SIMPLIFY" IT BACK.**
> **md5-on-CGNS is not reproducible, and this lane measured it on the M6 itself.** Re-running
> `cgns_utils coarsen` on the archived source reproduced the shipped surfaces at **identical size and
> different hash**: c2 came out **258,048 B** with md5 `e83c9a3190f7b895cd3f31446ea52d3e` against the
> shipped `A3-onera-m6-transonic/surfaceMesh.cgns` at **258,048 B**, md5 `897e6ae9f6ab63309e125f954075be85`;
> c3 came out **126,976 B**, md5 `e7374cf2a6e2d71954b54f656d3c722e` against the shipped sweep surface at
> **126,976 B**, md5 `072cff77d15fa62c7b1fb2205c35358d`. Same operator, same input, same byte count,
> different hash — CGNS carries non-deterministic content. The A6 lane measured the same
> independently. A hash comparison therefore gives a **false "the levels differ"** (two levels could
> hash differently while being the same mesh) and a **false "regeneration drifted"**. The *identity*
> direction is still safe — identical hashes do prove identity, which is what §1's one-directional
> finding on the existing sweep rests on — but the *difference* direction, and any hash of a
> regenerated file, is unreliable.

### 3.2 `G-MESH` — checkMesh on every level

`checkMesh -allGeometry -allTopology` on **each** of L3, L2, L1, plus plain `checkMesh`. Registered
assertions:
- The line **`Mesh has N geometric (non-empty/wedge) directions`** is present and **N = 3** on every
  level, cited by name in the record. (Measured on the shipped 399,360-cell mesh:
  `Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)`.)
- **No patch of type `empty` or `wedge`** on any level. The full patch list with types is recorded per
  level. (Shipped mesh: `wing` = `wall` 6240, `inout` = `patch` 6240, `sym` = `symmetry` 8704.)
- **Every failed `-allGeometry -allTopology` check is named in the record**, whether or not the level
  is used. A level with a named failure may still be used only if the supervisor records why; it may
  never be used silently.
- Trailing-edge thickness per level re-measured on the **volume** mesh and compared to §2.4.

### 3.3 `G-COLD` — the warm-start trap, guarded

pyDAFoam writes the primal end state back into the time-0 directory at run end, so a second run of a
case directory silently warm-starts (`DAFOAM_CHARTER.md` §6; `FAMILY_SUPERVISION_GUIDELINES.md` §8).
**This lane measured it live on this very case:**
`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/processor0/0/U.gz` is **5,476,863 B with mtime
2026-07-28 02:48** — the same size as the t=629 field and **newer than it**, while every other field in
that `0` directory is a ~450 B placeholder. That case's `0` is **not a clean cold start**.

`G-COLD` asserts, at launch, per level:
1. **No time directory other than `0` exists** in the case root or in any `processor*` directory.
2. **Every field in `0` predates the launch timestamp** and is a placeholder-sized initial condition,
   not a written solution.
3. The first `Time step continuity errors` value is checked against the registered cold signature.

A guard that finds either condition violated **refuses the level**; it does not clean up and proceed.

### 3.4 `G-PLANT` — planted-zero control on the grading reader

Per `CLAUDE.md` rule 3, the comparator plants a known perturbation into the field it will read, reads
it back **through the real path**, and refuses if it cannot see it.

> **WHY THIS GUARD HAS TEETH HERE, in this lane's own words and from today.** While inventorying A3 I
> wrote a reader that tested for `constant/polyMesh/owner`. It returned **zero cases for every A3/M6
> directory** while correctly finding **7** cases elsewhere on the same walk. The zero was **false** —
> these meshes store `owner.gz`. **A reader shown able to see a non-zero SOMEWHERE is still not shown
> able to see one IN THE CLASS BEING ASKED ABOUT.** `G-PLANT` therefore plants into a field of **this
> family's own levels**, in this family's own on-disk format, and a control that only demonstrates the
> reader working on some other case does not satisfy it.

### 3.5 `G-TOL` — the accept floor is read from THIS item's own script

`primalMinResTol` and `primalMinResTolDiff` are read from the runScript each level actually uses and
recorded **per level**. The accept floor is the **PRODUCT** (`N-D43`).

Measured on disk today, for orientation only — **these are NOT carried into this item**:
- A3 **rung 3**: `primalMinResTol 1e-06` × `primalMinResTolDiff 100` = **1e-04** accept floor
  (`A3FL2-PREFLIGHT-EXERCISE/BASELINE_R3/a3fl2_ex_BASELINE_R3.log:271` and `:442`).
- A3 **fine `run_model`**: `primalMinResTol 1e-08`, `primalMinResTolDiff 100`
  (`logs_A3/run_model_run3.log:271`, `:442`).

**A3GC registers `primalMinResTol = 1.0e-08` and `primalMinResTolDiff = 100` on all three levels**,
matching the tolerance the validated 399,360-cell primal actually ran at, giving an accept floor of
**1e-06**. `G-TOL` refuses if the solver's own DAOption dump on any level prints anything else. **No
number is carried across from A2 (1e3) or S1 (1e2) or from another level of this family.**

### 3.6 `G-RES` — acceptance reads the right residual (`N-D44`)

**No gate in this item reads `finalRes`.** A `finalRes` comparator is structurally blind to the
condition DAFoam fails on. Acceptance per level reads:
1. the printed **`Primal min residual`** line, and
2. the **per-equation INITIAL residuals** (`U0/U1/U2 initRes`, `he initRes`, `p initRes`,
   `nuTilda initRes`) at the last written time.

A level is **iteratively converged** only if every per-equation initial residual is ≤ 1e-06 **and** the
printed primal min residual is below the §3.5 accept floor. Confirmed by first-hand grep: `finalRes`
appears **0 times** under `cases/dafoam/ladder-a/A3/` today, against **323 files** containing it
elsewhere under `cases/dafoam/` — the reader was live, so the zero is real.

### 3.7 Standard guards

Strict completion rule and age guard (`CLAUDE.md` rule 4). Decomposition disclosed with every number:
method, `numberOfSubdomains`, and for `simple` the subdivision (`DAFOAM_CHARTER.md` §5).

## 4. THE GATES

### 4.1 Functionals

**CD** and **CL**, read from the primal's own force integration on the `wing` patch, `directionMode`
`parallelToFlow` / `normalToFlow`, `scale = 1/(0.5·U0²·A0·ρ0)` with `A0 = 0.7575`, `ρ0 = 1.0` — the
same definitions the validated run used. Flow conditions unchanged and re-asserted per level:
`U0 = 291.6`, `p0 = 101325.0`, `T0 = 300.0`, `nuTilda0 = 4.5e-5`, `aoa0 = 3.06`, giving
**M∞ = 0.83997**; solver `DARhoSimpleCFoam`; turbulence `SpalartAllmaras` with wall functions.

**Anchor, measured:** at 6,240 surface faces × 64 layers = 399,360 cells the converged primal gives
**CD = 0.0229956, CL = 0.3131159** (`logs_A3/run_model_run3.log`, `primalMinResTol 1e-08`, endTime
6000, `End` line present, np=4). **That case is NOT a member of this family** — it is c2 with N=65,
off the r=2 diagonal — and it is used as a sanity anchor, never as a fourth level.

### 4.2 Roache gating — standing rule 5, applied in order and not negotiable

1. **Any level not iteratively converged (§3.6) or not plateaued → the row is `NOT A RESULT`.** No
   value is quoted from it as a result.
2. **Triple classified.** `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` → **`NOT A RESULT`**,
   with the value, both triples and both orders printed beside it.
3. **`CONVERGING` → `PASS` inside the registered band, else `GATE FAIL`**, GCI printed.

**GCI at Fs = 1.25.** **A GCI is NEVER quoted when the three values are not monotone.** The gate can
only turn a PASS or GATE FAIL **into** `NOT A RESULT`, never the reverse.

### 4.3 Registered predictions and bands — written before the run

| quantity | prediction | band for `PASS` |
|---|---|---|
| observed order `p` on CD | 1.6 | **1.0 ≤ p ≤ 3.0**; outside → the triple is not `CONVERGING` → `NOT A RESULT` |
| observed order `p` on CL | 1.8 | **1.0 ≤ p ≤ 3.0**, same rule |
| GCI(fine) on CD, Fs = 1.25 | ≤ 2.0 % | **≤ 3.0 %** |
| GCI(fine) on CL, Fs = 1.25 | ≤ 1.5 % | **≤ 2.5 %** |
| Richardson-extrapolated CD | 0.0218 ± 0.0015 | reported with band, not gated |
| Richardson-extrapolated CL | 0.316 ± 0.008 | reported with band, not gated |

`p` is registered as a **surface-and-outer-field order** for the reason given in §2.6, and every
appearance of it in the result record carries that qualifier.

### 4.4 FALSIFIER

> **A3GC is REFUTED if the CD triple over L3/L2/L1 is not `CONVERGING`** — that is, if the three CD
> values are non-monotone, stagnant, exact, or give an observed order outside [1.0, 3.0]. The verdict
> is then **`NOT A RESULT`** and the honest statement is that **a surface-refined family did not
> deliver a convergent primal on this case either**, which would be a finding about the case and not
> about the family. It is **not** repaired by adding a level, by widening the band, or by dropping the
> coarse level. Adding a fourth level is a **new item** with its own pre-registration.

### 4.5 THE SHOCK — the physics payoff, predicted before the run

This is the scientific content of the item and the thing the old family could not test.

**Measured on the existing 399,360-cell solution** (`logs_A3/shock_location.json`,
`logs_A3/cp_comparison.json`), CFD minus AGARD AR-138 Case 2308:

| η | Δ(x/c) | CFD slope | exp slope | upper-surface Cp RMS |
|---|---|---|---|---|
| 0.20 | **+0.096** | 4.78 | 3.65 | 0.0741 |
| 0.44 | +0.074 | 5.03 | 6.54 | 0.0662 |
| 0.65 | +0.045 | 4.97 | 8.44 | 0.0814 |
| 0.80 | −0.001 | 4.70 | **7.53** | 0.0799 |
| 0.90 | +0.026 | 9.49 | **15.91** | 0.0704 |
| 0.96 | +0.042 | 9.89 | 14.39 | 0.0491 |
| 0.99 | +0.022 | 6.70 | 13.51 | 0.1139 |

Pooled Cp RMS over 260 common points: **0.0575**. Lower-surface RMS 0.0128–0.0265; upper-surface RMS
0.0491–0.1139; worst pointwise deviation **0.2745 Cp** at η = 0.80 upper.

**REGISTERED PREDICTIONS — each can fail, and failure is reported as failure:**

- **P1 (sharpening).** Surface refinement L3 → L1 (chordwise cell count ×4) **increases the measured
  Cp slope through the shock by ≥ 40 % at η = 0.80 and η = 0.90** on L1 relative to L3. *Falsified if
  the increase is < 15 % at both stations — which would say the smearing is model, not mesh.*
- **P2 (position).** The mean absolute shock-position error over the seven stations **falls by ≥ 30 %**
  from L3 to L1, and **the inboard error at η = 0.20 falls below +0.060 c** on L1. *Falsified if the
  η = 0.20 error stays above +0.085 c on L1 — which would say the aft bias is the SA model's
  shock/boundary-layer interaction, not resolution.*
- **P3 (pooled Cp).** Pooled upper-surface Cp RMS on L1 **improves to ≤ 0.055** from the 0.0575 pooled
  figure. *Falsified above 0.070.*
- **P4 (the honest counter-hypothesis, registered so it cannot be adopted after the fact).** If P1, P2
  and P3 all fail while the CD/CL triple is `CONVERGING`, the registered reading is **"the M6 shock
  disagreement on this configuration is a turbulence-model limitation, not a grid limitation"** — and
  that is a *result*, reported as such, not a failure of the item.

**P1–P3 are measured by re-running the archived comparator path** — `logs_A3/extract_cp.py` then
`logs_A3/compare_cp.py` against `logs_A3/case_2308.dat` — on **copies**. **The `logs_A3` archive is
read-only and is never edited: it is the record of what ran.**

## 5. COST — arithmetic shown, anchored on a measurement

**Anchor (measured):** the 399,360-cell primal ran `ExecutionTime = 1221.21 s` at **np = 4** for 6,000
iterations (`logs_A3/run_model_run3.log`) → **81.4 core-min**, i.e. **2.04e-04 core-min per cell per
6,000 iterations**. Cost is scaled linearly in cells; that is optimistic for the largest level (linear
solver work grows super-linearly) and the cap absorbs it.

| level | cells | ranks | wall estimate | **core-min** | basis |
|---|---|---|---|---|---|
| L3 | 99,840 | 4 | ~5.1 min | **20.4** | 81.4 × (99,840 / 399,360) |
| L2 | 798,720 | 8 | ~20.4 min | **163** | 81.4 × (798,720 / 399,360) |
| L1 | 6,389,760 | 8 | ~163 min | **1,302** | 81.4 × (6,389,760 / 399,360) |
| mesh generation, 3 levels (cgns_utils + pyHyp + plot3dToFoam + autoPatch + createPatch + renumberMesh) | — | 1 | ~35 min | **35** | scaled from the shipped run's own `logMeshGeneration.txt` |
| checkMesh `-allGeometry -allTopology` ×3 | — | 1 | ~4 min | **4** | measured 2.1 s at 399,360 cells; L1 is 16× |
| **TOTAL ESTIMATE** | | | | **≈ 1,525 core-min** | |
| **CAP** | | | | **2,290 core-min** | 1.5 × estimate |

**cost_basis:** ≈ **$1.30** at the estimate and ≈ **$1.96** at the cap, from 25.4 / 38.2 core-h ×
$0.0513/core-h. **DERIVED, not measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Well inside the $25 pre-authorisation.

**THE CAP IS CALIBRATION, NOT A STOP, FOR THIS ITEM.** Per Sanaa's Case Protocol closing clause
(2026-09-10, ~16:50Z): *"for all these 3D cases that still need to run, i dont want to see any budget
gates ( time or money)"*. §4's "cap reached: stop, NOT A RESULT" and `CLAUDE.md` rule 12's "an overrun
stops the run" are **suspended for this item**. The estimate is recorded so the actual can be compared
against it; the comparison is owed at completion into `docs/COST_CALIBRATION.md` with the ratio
actual/predicted and the gap attributed (rule 12, Sanaa 2026-08-23).

**Memory envelope, predicted before launch** (`DAFOAM_CHARTER.md` §7): L1 primal-only at 6.39M cells is
predicted at **9–14 GiB** against the box's 30.64 GiB `MemTotal`, at np=8 with a `--memory` cap
registered at freeze. **A run stopped by memory is recorded as stopped by memory and is `NOT A RESULT`
about convergence, with no second budget.** No adjoint is attempted at any level, so the mesh-sized
`d[residuals]/d[vol_coords]` matrix that killed A3 campaign 1 and blocks A6 never forms.

## 6. STAGES AND EXIT CONDITIONS (Case Protocol Charter §1–§5)

| stage | exit condition | action on failure |
|---|---|---|
| 1. mesh generation | three levels at **exactly** 99,840 / 798,720 / 6,389,760 cells | any other count → **refuse, do not solve**; report the measured counts |
| 2. `G-SYS`, `G-MESH`, `G-COLD`, `G-PLANT`, `G-TOL`, `G-RES` | all green | any red → named in the record with file and line; the smallest fix from the lessons ledger; a red is never inferred green |
| 3. smoke on L3 | residuals falling, monitors alive, cost per iteration inside the estimate's band | one registered escalation step, then re-smoke; three failures on one cause → park `NOT A RESULT` |
| 4. full runs, L3 → L2 → L1 | strict completion rule (rc=0, `End`, last time == `endTime`, fields present, age guard) | a stop is diagnosed by class and recorded; the cap does not stop this item (§5) |
| 5. grade | Roache order applied (§4.2); GCI at Fs=1.25; shock predictions P1–P4 evaluated | verdict from the six tokens only |

**Detached execution.** Every level is launched detached and parented to init, so the fleet dying does
not touch the solver.

---

## 7. WHAT THIS DOCUMENT DOES NOT AUTHORISE

It authorises **no launch, no freeze, no commit and no send.** When the dafoam-supervisor freezes it by
sha it becomes an item with its own frozen pre-registration, its own commit and its own budget. Until
then every number above that is labelled a prediction is a prediction, and every number labelled
measured cites the artifact it was read from.

---

## AMENDMENT 1 — 2026-09-11 — **PRE-COMPUTE. The plateau limb was INVOKED AND NEVER DEFINED, and the residual condition is numerically IDENTICAL to the solver's own acceptance product. Both settled here, before the freeze.**

*lines whose number changed above this section: 0.* Appended; nothing above is rewritten or struck.

**Written and registered by the dafoam-supervisor** (§3 check-4: pre-registration read personally before
compute). This is a **pre-compute amendment** and is therefore legal to add a gate
(`CLAUDE.md` rule 2: *"Before first compute, amendments are legal and must state the condition and how
it was checked (name the run directory that does not exist)."*).

### CONDITION, AND HOW IT WAS CHECKED

**No solve compute has been spent on A3GC.** Checked first-hand, 2026-09-11: the only A3GC root on disk
is `/home/ubuntu/certonomous-runs/A3GC-mesh-family-probe/`, holding **four CGNS surface files,
3.5 MB total** — `m6_surfaceMesh_fine.cgns`, `s_c1.cgns`, `s_c2.cgns`, `s_c3.cgns` — the
mesh-coarsening probe of §2.3. A `find` for `log*`, `processor*` and any time directory under that root
returned **nothing**. **The three VOLUME meshes of §2.5 do not exist and no level has been solved.**
The run directories this item will create — one per level — do not exist.

### (a) `G-PLAT` — THE PLATEAU CRITERION, REGISTERED. It was invoked at §4.2 and defined nowhere.

§4.2 clause 1 refuses a level that is *"not iteratively converged (§3.6) **or not plateaued**"*. §3.6
defines the first half. **The second half had no criterion anywhere in this document.** Measured on the
document itself: `plateau` occurs **twice** — once at §0 quoting the charter's *adjoint* clause, which
does not bind a primal-only item, and once at §4.2 invoking it as a gate; `iterative error`,
`level-to-level` and any ten-times rule occur **zero times**. **A gating limb with no criterion cannot
refuse anything**, and standing rule 5 clause 1 is the limb that catches a level the solver accepted
but which never settled.

**Registered now, per `CASE_PROTOCOL_CHARTER.md` §5** (*"iterative error verified at least ten times
smaller than the level-to-level difference"*):

> **`G-PLAT`.** For each graded functional (CD, CL) and each level, the **iterative error** must be
> **at least ten times smaller than that functional's level-to-level difference**. Not satisfied → that
> level is **`NOT A RESULT`**, and by standing rule 5 clause 1 the whole triple is `NOT A RESULT`
> whatever its value.

**Source of the functional history — MEASURED, not assumed.** The history is read from **the solver's
own log**, the `CD:` / `CL:` lines emitted by `calcAllFunctions` at `printInterval`. Measured on the
validated 399,360-cell primal (`cases/dafoam/ladder-a/logs_A3/run_model_run3.log`): `printInterval 100`
(`:440`) gives **61 CD samples and 61 CL samples across 6,000 iterations**, against **61 `Time = `
lines** — cadence exactly 100, one sample per printed step. **There is no `forceCoeffs` functionObject
writing a coefficient history on this case:** `postProcessing/` under
`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/` holds **only** `wingPatchSample/6000/`, a surface
sample at the final time. **The log is the only available route**, and the grader reads it. (This is the
same shape of finding as `N-D44` on the residual banner: the obvious artifact does not exist on this
case, and a reader built on it would silently measure nothing.)

**Window: the last 10 printed samples** — at `printInterval 100`, the last 1,000 iterations.
**A window holding fewer than 10 samples makes that level `NOT A RESULT` for want of evidence.** A
window that cannot exhibit an excursion cannot prove a plateau, and a level that printed too rarely to
be judged is not thereby judged converged.

**Statistic: the PEAK-TO-PEAK excursion `max − min` over the window. It is NOT an adjacent-sample
delta, and that form is refused by name.** An adjacent-sample difference is an *increment*, not an
*excursion*: a signal drifting steadily in one direction has a small increment at every step and never
plateaus at all. **This is precisely the defect the cfd team's DrivAer Gate A1 plateau limb carried and
that this lab caught on 2026-09-10** — a two-sample increment wearing a plateau's name, passing by 120×
while the signal's own excursion over 500 iterations was 8.35 %. It is not repeated here.

**ACHIEVABILITY CHECKED BEFORE REGISTERING — this is not a gate registered to fail.** Measured on the
validated run's own history by this supervisor:

| functional | peak-to-peak, last 10 samples | relative to final value |
|---|---|---|
| CD | **1.666e-07** | 7.24e-06 |
| CL | **2.543e-08** | 8.12e-08 |

Against a level-to-level CD difference expected of order **1e-3** (§4.3 predicts Richardson CD
0.0218 ± 0.0015 against the 0.0230 anchor), the ten-times rule demands iterative error ≤ ~1.2e-4 and the
measured figure is 1.67e-07 — **roughly three orders of margin.** A criterion nobody can meet is
theatre; this one is met with room, and that was established before it was registered rather than hoped
for afterwards.

**One honesty note, so the contrast is not overstated.** On this *well-converged* log the adjacent-sample
delta is **1.083e-07** for CD — only ~1.5× below the 10-sample excursion of 1.666e-07. **The two forms
nearly agree here.** Peak-to-peak is registered not because it always differs, but because it is the
form that stays correct on a **drifting** signal, which is the case where the distinction decides the
verdict.

### (b) §3.6'S RESIDUAL CONDITION EQUALS THE SOLVER'S OWN ACCEPTANCE PRODUCT — disclosed, and it is WHY (a) matters

§3.5 registers `primalMinResTol 1e-08` × `primalMinResTolDiff 100` → **accept floor 1e-06**. §3.6 then
requires **every per-equation initial residual ≤ 1e-06**. **Same residual family, same number.** DAFoam's
`checkPrimalFailure()` tests `primalMaxRes / primalMinResTol_ > primalMinResTolDiff` (`N-D44`, confirmed
at source), so **a primal handed back without an `AnalysisError` has already satisfied approximately what
§3.6 asks.** Under `CASE_PROTOCOL_CHARTER.md` §1 — *"Solver tolerance strictly tighter than any gate that
reads its output (the T23G2Rn2 rule: **a tolerance equal to a gate voids the rung**)"* — that coincidence
is exactly the configuration the charter forbids. **It is the same defect this supervisor recorded against
the D6 family on 2026-09-10, found here in a fresh registration on a different case one day later.**

**What is registered:**

1. **§3.6 is RETAINED as a completion PRECONDITION and is explicitly NOT a discriminating gate.** It is
   never quoted, alone, as evidence that a level converged.
2. **The discriminating limb of standing rule 5 clause 1 on this item is `G-PLAT` above.** It reads a
   *different quantity* — the functional's own history — against a threshold *derived from the family*
   (the level-to-level difference), which the solver's acceptance test knows nothing about and cannot
   pre-satisfy.
3. **A tighter residual floor of 1e-07 is reported per level as a DIAGNOSTIC — reported, never graded** —
   mirroring what `D8G` does with its own tighter tutorial floor, so the coincidence is **visible in the
   record rather than inferred by a later reader**.

**Why the tolerances in §3.5 are NOT changed:** tightening `primalMinResTolDiff` to 10 would move the
accept floor to 1e-07 and leave the §3.6 gate at 1e-06 *looser* than acceptance — still unable to fail,
in the other direction. The repair is not a different number on the same quantity; it is a gate that reads
a different quantity, which is (a). **`primalMinResTol 1e-08` and `primalMinResTolDiff 100` stand exactly
as registered**, matching the tolerance the validated 399,360-cell primal actually ran at.

### WHAT THIS AMENDMENT DOES AND DOES NOT DO

**ADDS** `G-PLAT` and the 1e-07 diagnostic. **ALTERS NO** gate, threshold, band, cap or label registered
above: §4.3's prediction bands, §4.2's Roache order, §4.4's falsifier, §5's cost and cap, and §3.5's
tolerances are untouched. **The item remains primal-only and claims no gradient, so no FD table is owed**
(`DAFOAM_CHARTER.md` §1) — restated here because this amendment adds a gate and a later reader must not
infer that the adjoint scope moved. **SUBMISSIONS PARKED.**
