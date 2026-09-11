# PERMISSION: FROZEN — frozen by the dafoam-supervisor 2026-09-11. Gates, thresholds, caps and labels are CLOSED to change except by dated addendum that cannot alter them.

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


---

## AMENDMENT 2 — 2026-09-11 — **PRE-COMPUTE. A registered gate I wrote is UNMEASURABLE AS WRITTEN — struck and REPLACED BY A STRONGER ONE. Plus three corrections, one of them to my own launch instruction.**

*lines whose number changed above this section: 0.* Appended; nothing above is rewritten or struck.

**Registered by the dafoam-supervisor.** **Pre-compute:** no A3GC level has been solved; the only compute
against this item is a **FEASIBILITY mesh probe whose outputs are declared never gradeable**. Gates may
therefore still be altered (`CLAUDE.md` rule 2). **§3 check-1 discharged by me personally on the
comparator**: I ran `a3gc_grade_selftest.sh.DRAFT` myself — **61 passed / 0 failed, exit 0** — and then
**mutated `peak_to_peak()` back into an adjacent-sample delta** (the DrivAer defect reinstated) and re-ran:
**57 passed / 4 failed**, failing exactly `B9c` and `B9d`, the two tests that assert the gated statistic is
the excursion and not the increment. **A suite that passes proves nothing until it is seen to fail, and I
saw it fail.** The file was restored byte-identical (md5 `e9930092f00b08c4a3db6063ad0c7fc0`).

### (a) §3.1 LIMB 5 — **STRUCK AS A GATE.** It cannot be satisfied by any recipe, and that is a fact about the limb, not about the meshes.

§3.1 limb 5 registered *"TE thickness at root/mid/tip agrees across the three levels to 1 %"*, and §2.4
tabulates values — but **records no measurement recipe**, and none could be reconstructed.

**MEASURED, on the real c2/c1/c0 surfaces:** root spread **0.0243 %** (passes); **mid and tip spread
100.0000 %**. The cause is structural, not numerical: **every window-based TE statistic is point-density
dependent, and these levels differ 4× in point count by construction.** The aft window holds **n=1 point on
L3**, giving a thickness of exactly **0.0**, against n=5 on L2 and n=9 on L1. **And the limb fails even
between the two FINEST levels, where no zero is involved:** tip thickness **L2 2.974395e-03 vs L1
2.917384e-03** — a **1.9 % spread against a 1 % tolerance.** Five aft-window widths, four chord-fraction
interpolations, iso-section extraction and chord normalisation were tried; none reproduces §2.4's figures
across all three levels. ⚠ **And §2.4's own tip figure (~7.14e-04) is not reproduced by any recipe tried
(~2.9e-03) — so §2.4's numbers came from a recipe that is not recorded and cannot be recovered.**

> **I am striking a gate, which is what "widening a gate to fit the answer" also looks like, so the
> distinction is stated plainly: this limb is struck because it is UNMEASURABLE AS WRITTEN, demonstrated
> by measurement, and NOT because it failed. Nothing about the three levels is in question.** Limb 5 is
> **demoted to a reported diagnostic**, printed per level, never gating.

**AND IT IS REPLACED BY A STRICTLY STRONGER LIMB, so body identity is better guarded than before, not
worse.** Registered as **§3.1 limb 5′ — `G-NEST`:**

> **Every point of the coarser surface must be present BIT-EXACTLY in the finer surface**, level by level.
> Measured on the real surfaces: **0 misses of 6,765 c2 points in c1, and 0 misses of 26,001 c1 points in
> c0.** An exact factor-2 coarsening **must** satisfy this — it selects alternate points, it does not move
> them. **A single 1e-6 nudge to one coordinate breaks it.** Not satisfied → **refuse (exit 2)**.

**This is a statement no md5 can express** (§3.1's warning about hash comparisons is unaffected and stands),
and it is sharper than any thickness tolerance. **The body-identity purpose of §2.4 is fully retained:**
limb 4 alone already rejects the excluded `c3` at **max|Δ| = 1.06e-04 against the 8.06e-06 tolerance —
13×** — and `G-NEST` would reject it independently.

### (b) §3.6 LIMB 1 — the `Primal min residual` banner IS NOT EMITTED ON THIS FAMILY'S PATH

Measured: the string occurs **zero times** in `cases/dafoam/ladder-a/logs_A3/run_model_run3.log`, the
validated primal of this very case. It is emitted by the pyDAFoam driver, not by the runScript path this
family uses (it **does** appear in the `A3-onera-m6-transonic` run-tree logs). **This is `N-D44`'s shape
again: the obvious artifact does not exist on this case and a gate built on it measures nothing.**

**Registered:** the **per-equation `initRes` route of §3.6 limb 2 is the BINDING route**. The banner is read
**where present** and reported; **its ABSENCE is reported loudly and is NEVER a refusal**, because absence
is a property of the driver path, not of the solution. **No gate in this item reads `finalRes` — unchanged.**

### (c) THE BINDING LEVEL-TO-LEVEL DIFFERENCE IS PINNED — it was ambiguous and the comparator should not choose

`AMENDMENT 1(a)` requires the iterative error to be ten times smaller than *"that functional's
level-to-level difference"* without saying **which** of the two differences binds a given level.
**Registered: the binding difference is `min(|f_L3 − f_L2|, |f_L2 − f_L1|)`** — the conservative reading,
because the smaller difference is the one iterative noise can swamp and the one Richardson extrapolation
rests on. **This is now the registration's choice, not the comparator's.**

### (d) `autoPatch 60`, NOT 45 — CORRECTING MY OWN LAUNCH INSTRUCTION

I instructed the mesh lane to use `autoPatch 45`, transplanted from the **A6** recipe. **That was my error
and it is corrected here from this case's own record.** `cases/dafoam/ladder-a/logs_A3/logMeshGeneration.txt:207`
reads `Exec : autoPatch 60 -overwrite`, and `:233`/`:235`/`:237` record it assigning **auto0 = 6,240 /
auto1 = 8,704 / auto2 = 6,240** — exactly the decomposition
`/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/system/createPatchDict` maps to `wing` (auto0),
`sym` (auto1) and `inout` (auto2), and exactly §3.2's registered shipped patch list. **Whether 45
reproduces that on the M6 is NOT MEASURED and is not assumed.** **Registered: `autoPatch 60`**, with the
post-check refusing on any patch table other than the registered one.

### WHAT THIS AMENDMENT DOES AND DOES NOT DO

**STRIKES** §3.1 limb 5 as a gate (demoted to diagnostic) and **ADDS** the stronger `G-NEST`.
**CORRECTS** §3.6 limb 1 to reporting-only and `autoPatch` to 60. **PINS** the binding difference.
**ALTERS NO** prediction band, cap, cost, tolerance or label: §4.3's bands, §4.2's Roache order, §4.4's
falsifier, §4.5's P1–P4 and §5's cost stand exactly as registered. **The item remains primal-only and owes
no FD table.** **SUBMISSIONS PARKED.**


---

## AMENDMENT 3 — 2026-09-11 — **PRE-COMPUTE. The document registered NO COMPOSITION AT ALL — not for a partial shock result, not for the P4 branch, not for the item. Five compositions registered here, one of them an OPENLY INTERPRETIVE CHOICE. Plus a correction to AMENDMENT 1's own condition statement, which events have overtaken, and an examination of AMENDMENT 2's `G-NEST` that I did not want to have to write.**

*lines whose number changed above this section: 0.* Appended; nothing above is rewritten or struck.

**Registered by the dafoam-supervisor.** Drafted by a `lab-lane` to the supervisor's rulings; the rulings
are the supervisor's and are marked where they are interpretation rather than reading.

### CONDITION, AND HOW IT WAS CHECKED (`CLAUDE.md` rule 2)

**The registered run directories do not exist.** Checked 2026-09-11T16:42Z:

```
A3GC-L3      does not exist
A3GC-L2      does not exist
A3GC-L1      does not exist
A3GC-graded  does not exist
```

**NO LEVEL HAS SOLVED, AND THAT ZERO CARRIES A PLANTED CONTROL** (`CLAUDE.md` rule 3; §3.4 records a
reader that returned a false zero on exactly these trees). A recursive grep for
`DARhoSimpleCFoam|Starting time loop|primalMinResTol` returns **0 files** under every A3GC root — and
**the same reader, same pattern, returns 11 files** under `cases/dafoam/ladder-a/logs_A3/` and **9 files**
under `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/`. **The reader is shown able to see a
non-zero in the class being asked about, so the zero is evidence and not an absence.**

#### A MESH-GENERATION PROBE IS RUNNING, IT IS DISCLOSED HERE, AND IT IS QUARANTINED

**`/home/ubuntu/certonomous-runs/A3GC-meshgen-probe/` exists** — a second A3GC root, created
2026-09-11T15:41Z, **111 MB**, still generating L1 at the time of writing at **58.00 core-min** by its own
`BUDGET_WATCHDOG.log`. It holds `L3/` and `L2/` volume meshes at **99,840** and **798,720** cells —
both **exactly** the §2.5 registered counts, read from each level's own `constant/polyMesh/owner.gz`
note — plus `checkMesh` logs and `logMeshGeneration.txt` per level. **It is not hidden and it is not
described as nothing.**

**WHY IT IS NOT "FIRST COMPUTE", STATED AS A TEST RATHER THAN AN EXCUSE.** *"It is only a probe"* is not
a principle; it is what every violation says about itself. Rule 2 closes gates once compute has produced
**an artifact that a gate of this item reads**, because that is the configuration in which a gate could
be chosen to fit an answer. Checked, not reasoned about:

| test | result |
|---|---|
| does any comparator path read the probe root? | **no** — `grep -c 'meshgen-probe'` returns **0** in both `a3gc_grade.py.DRAFT` and `a3gc_grade_selftest.sh.DRAFT`. The two probe references the comparator carries (`:69`, `:732`) name `A3GC-mesh-family-probe`, the §2.3 **surface** probe — a **different directory** |
| do the registered run directories exist? | **no** (table above) |
| has any level solved? | **no**, proved by planted control above |
| could **this amendment's** rulings have been fitted to an answer? | **no.** They govern P1–P4 and the item composition. **P1/P2/P3 read Cp from SOLVED SURFACE FIELDS.** No solved field and no surface VTK exists for any level, and none can be computed from anything on disk. **The answer these rulings would have to be fitted to does not exist** |

#### THE PRICE, AND IT IS BINDING — `G-QUARANTINE`

> **THE PROBE'S MESHES MAY NEVER BE PROMOTED INTO THE GRADED RUN.** §6 stage 1 regenerates the family
> under this item's own registered run root. **Every artifact under
> `/home/ubuntu/certonomous-runs/A3GC-meshgen-probe/` is QUARANTINED FROM THE GRADED PATH PERMANENTLY.**
> If any A3GC level is ever graded on a mesh this probe generated, then **the probe WAS first compute
> after all, retroactively, and AMENDMENT 3 becomes illegitimate along with everything resting on it.**

**A ruling that costs its author nothing is not a ruling.** This one costs the party who made it: the
supervisor who ruled the probe out of scope is the party who **throws away 58+ core-min of correct mesh
work and pays to generate it again inside the graded chain.** That is what makes the ruling honest
rather than convenient, and it is registered so a later reader can check that the price was actually
paid.

### (a) EACH PREDICTION'S OWN TOKEN — the document implies one and never states one

§4.5 gives P1, P2 and P3 **two** thresholds each — a PASS condition and a separate, lower FALSIFICATION
condition — and §6 stage 5 demands *"verdict from the six tokens only"*, but **no token is named for any
prediction anywhere.** Registered now:

> **PASS** when the prediction meets its registered §4.5 PASS condition.
> **GATE FAIL** when its registered §4.5 FALSIFICATION condition holds.
> **`NOT A RESULT`** when it lies in the **MIDDLE BAND** between the two — **because a registration that
> supplies two thresholds has by construction declared the space between them evidence for neither.**

**The three middle bands, written out so no reader has to derive them:**

| | PASS (§4.5) | FALSIFIED (§4.5) | **MIDDLE BAND → `NOT A RESULT`** |
|---|---|---|---|
| **P1** sharpening | slope increase **≥ +40 %** at **both** η = 0.80 **and** η = 0.90 | increase **< +15 %** at **both** stations | anything else — e.g. a 15–40 % increase at both, or a split result (≥ 40 % at one station, below it at the other) |
| **P2** position | mean abs. shift drop **≥ 30 %** **and** η = 0.20 error **< +0.060 c** on L1 | η = 0.20 error **> +0.085 c** on L1 | e.g. η = 0.20 lands in [0.060, 0.085] c, or the drop misses 30 % while η = 0.20 is under 0.060 c |
| **P3** pooled Cp | pooled upper-surface Cp RMS on L1 **≤ 0.055** | RMS **> 0.070** | **0.055 < RMS ≤ 0.070** |

**A DIRECTION NOTE, because it would otherwise be a trap.** The falsification condition points *downward*
for P1 (a small increase falsifies) and *upward* for P2 and P3 (a large error falsifies). **The
comparator therefore tests each prediction's falsification condition AS §4.5 WORDS IT**, and no boundary
is restated in a direction-neutral form that would silently move it.

### (b) P4's "ALL FAIL" MEANS ALL THREE **FALSIFIED** — the strong form

§4.5 P4 fires *"If P1, P2 and P3 all fail"*, and with two thresholds per prediction that phrase reads
two ways: **all-three-not-PASS** (weak) or **all-three-FALSIFIED** (strong). Registered: **the STRONG
form.**

**Why.** P4 is registered as *"the honest counter-hypothesis"*, and **a counter-hypothesis is ADOPTED on
strong evidence, never on mere non-confirmation.** The weak reading would let P4 fire on three middling
results. The strong form is also **the conservative direction — it makes P4 HARDER to fire** — so this
choice cannot be accused of easing the item's path to a favourable reading.

### (c) PARTIAL FAILURE — P4 DOES NOT FIRE, and the stage takes the worst of the three

§4.5 registers P1, P2, P3 individually and registers only the all-three case, as P4. **The partial case
— some but not all falsified — is addressed nowhere in the document.** Registered:

> **If fewer than all three are FALSIFIED, P4 does not fire and its registered reading is NOT PRINTED**,
> so it cannot be adopted after the fact by a reader skimming for it. Each prediction carries its own
> token per (a), and **the SHOCK STAGE carries the WORST of the three** under the ordering of (e).

### (d) THE P4 BRANCH CARRIES **`GATE REACHED`** — ⚠ AN INTERPRETIVE CHOICE, SAID OUT LOUD

> When **all three are FALSIFIED** *and* the CD/CL triple is **CONVERGING**, the shock stage is
> **`GATE REACHED`**, and §4.5 P4's registered reading is printed **verbatim** beside it.
> If all three are FALSIFIED while the triple is **not** CONVERGING, **P4 does not fire** (§4.5
> conditions it on a CONVERGING triple) and the stage carries the worst of the three, i.e. `GATE FAIL`.

**⚠ THE DOCUMENT NAMES NO TOKEN HERE. A SUPERVISOR CHOSE ONE. A LATER READER MUST BE ABLE TO SEE THAT,
RATHER THAN BELIEVING THE DOCUMENT SAID IT.** §4.5 P4 gives a **prose reading** — *"that is a `result`,
reported as such, not a failure of the item"* — and names none of the six tokens, while §6 stage 5
requires a verdict from the six. The reasoning for `GATE REACHED`:

- **It is not `PASS`**, because **no shock band was met** and nothing may read as though one was.
- **It is not `GATE FAIL`**, because §4.5 registers this exact configuration as *"a `result` … not a
  failure of the item"*, and **a preference does not overwrite a frozen registration.** *(This
  supervisor made exactly that mistake earlier the same day on this same gate — ruling that a shock
  `GATE FAIL` must compose upward — read §4.5 afterwards, and withdrew it before the lane built on it.
  The withdrawal is recorded here because the error is instructive and the correction is the only
  reason this clause is right.)*
- **`GATE REACHED` is what the token means in this lab:** the item reached and evaluated its registered
  gate and produced a graded outcome that is **not a band statement**. The lab's own precedent is
  **D8R's `G-O`**, where an optimiser that hit max iterations while meeting a registered intermediate
  threshold graded `GATE REACHED` rather than `PASS` or `GATE FAIL`.

### (e) THE ITEM DOES CARRY A COMPOSED VERDICT — registered now, and **IT IS NOT A GATE**

**Measured on the document: the string `overall` does not occur in this pre-registration at all**
(`grep -ci overall` returns 0), and no composition of any kind was registered. `A3GC OVERALL` was the
comparator's own construct with no registered basis. Registered:

> **The item's verdict is composed WORST-FIRST over every graded gate — the CD triple, the CL triple and
> the shock stage — using the fixed vocabulary's own severity ordering:**
>
> ```
> NOT A RESULT  <  GATE FAIL  <  BLOCKED  <  PENDING  <  GATE REACHED  <  PASS
> ```

**THIS ORDERING IS NOT A GATE AND REGISTERS NO THRESHOLD.** It is the six tokens ranked by **how little
evidence each carries**, and every clause cites the standing rule that forces it:

| clause | forced by |
|---|---|
| `NOT A RESULT` outranks everything | standing rule 5 / §4.2: *"the gate can only turn a PASS or GATE FAIL **into** NOT A RESULT, never the reverse."* Nothing may outrank it |
| `GATE FAIL` above `BLOCKED` and `PENDING` | `CLAUDE.md` rule 1: PENDING is a display/queue state, *"use it for 'not yet run', **never to soften a GATE FAIL**"* |
| `BLOCKED` and `PENDING` above the graded-good tokens | both mean **no graded evidence**. An item may not stand at `PASS` on a stage that produced none. `BLOCKED` is an obstruction hit; `PENDING` is simply not yet run |
| `GATE REACHED` below `PASS` | a graded outcome short of a band statement |

**CONSEQUENCE, REGISTERED BEFORE IT CAN EMBARRASS ANYONE:** §6 stage 5 registers P1–P4 evaluation as
part of the grading path, so **while the shock stage is un-evaluated the item is `PENDING` and CANNOT be
`PASS`**, however well the CD and CL triples grade. **A registered stage that produced no evidence does
not leave the item at PASS.**

### CORRECTION TO **AMENDMENT 1**'s CONDITION STATEMENT — events overtook it, clause by clause

`CLAUDE.md` rule 6: frozen files are never edited. AMENDMENT 1's condition statement (`:420`–`:425`) is
**not rewritten**; it is corrected here, and **the whole clause did not die**:

| clause | line | status |
|---|---|---|
| *"the only A3GC root on disk is `…/A3GC-mesh-family-probe/`"* | `:420`–`:421` | **NOW FALSE.** A second root, `…/A3GC-meshgen-probe/`, exists and is the supervisor's |
| *"The three VOLUME meshes of §2.5 do not exist"* | `:424` | **NOW FALSE IN PART.** Volume meshes at the registered counts (**99,840** and **798,720**, both exact) exist **in the PROBE root**; the third is mid-generation; **NONE exists in a graded run directory** |
| *"and no level has been solved"* | `:424` | **STILL TRUE** — and now **proved by planted control**, not asserted |
| *"The run directories this item will create — one per level — do not exist"* | `:425` | **STILL TRUE** |

### THE `G-NEST` DISCLOSURE QUESTION — examined because it is the supervisor's own work

AMENDMENT 2(a) registered `G-NEST` **carrying its own passing measurement inside the registered gate
text** — *"Measured on the real surfaces: 0 misses of 6,765 c2 points in c1, and 0 misses of 26,001 c1
points in c0."* **The measurement therefore preceded the registration, and it is disclosed in as many
words, in the block quote that IS the gate.** That is the lab's accepted pattern — measuring
**ACHIEVABILITY** before registering, disclosed — which `D8G` used and which **AMENDMENT 1(a) of this
very document used**, under the heading *"ACHIEVABILITY CHECKED BEFORE REGISTERING — this is not a gate
registered to fail."*

**⚠ BUT THE SYMMETRY IS NOT EXACT, AND THE DIFFERENCE IS NAMED RATHER THAN WAVED THROUGH.** AMENDMENT
1(a) measured a **threshold** gate to check a criterion was *meetable*. `G-NEST` is a **binary
structural** gate that was measured to **pass outright** before being registered — and it was
registered in the same session, by the same author, on the same surfaces, **as the replacement for a
limb that had just been measured to FAIL.** That is a configuration in which the choice of which limb to
register **could** have been made by consulting which one passed, and saying so is the only way a later
reader can weigh it.

**What defends `G-NEST`, and it is not that it passed:**

1. **It is a priori, not fitted.** *"An exact factor-2 coarsening **must** satisfy this — it selects
   alternate points, it does not move them."* The gate follows from the operator's definition; the
   measurement **confirms the operator behaved as defined**, it does not choose the criterion.
2. **It is STRICTLY STRONGER than what it replaced**, which is the direction that cannot be
   self-serving. A struck gate replaced by a weaker one is the failure mode; this is its opposite.
3. **It can fail, and has been SEEN to fail.** AMENDMENT 2(a) predicted *"a single 1e-6 nudge to one
   coordinate breaks it"*, and the selftest demonstrates it: unit `B4a` nudges one `CoordinateY` by
   1e-6 and the limb reports **1 miss of 6765, FAIL**, and the comparator **refuses**.
4. **It rejects the excluded `c3` independently** of limb 4.

**Verdict on the question: DISCLOSED AND DEFENSIBLE, with the asymmetry recorded above rather than
resolved away.** No change to `G-NEST` is made.

### WHAT THIS AMENDMENT DOES AND DOES NOT DO

**ADDS** five compositions the document never contained — (a) each prediction's token including the
middle band, (b) the strong reading of P4's "all fail", (c) the partial case, (d) the P4 branch's token,
(e) the item's composed verdict — plus **`G-QUARANTINE`**. **CORRECTS** AMENDMENT 1's condition
statement, clause by clause, by appending. **EXAMINES** `G-NEST` and changes nothing about it.

**ALTERS NO gate, band, threshold, cap or label registered above.** §4.5's P1–P4 texts and every one of
their thresholds, §4.2's Roache limbs and order, §4.3's `p` band and GCI bands, §3.5's tolerances,
§3.1's limbs including `G-NEST`, AMENDMENT 1's `G-PLAT`, AMENDMENT 2's `autoPatch 60` and pinned binding
difference, §5's cost and cap, and §6's stage table **all stand exactly as registered.** **No number in
this document moved.** The item remains **primal-only and owes no FD table** (`DAFOAM_CHARTER.md` §1) —
restated because this amendment touches the shock gate and a later reader must not infer that the
adjoint scope moved.

**`evaluate_shock` HAS NEVER RUN AGAINST REAL VTK.** None exists for any level. Everything in (a)–(d) is
registered **before** the data that would exercise it can be produced, which is the entire evidentiary
point, and no green selftest may be read as saying otherwise. **SUBMISSIONS PARKED.**


---

## FREEZE RECORD — 2026-09-11, the dafoam-supervisor

**`A3GC` IS FROZEN.** `CLAUDE.md` rule 2: the grading path is fixed at the pre-registration
commit, and the frozen file is verified to be the file that ran by hashing it against the
committed blob. These are the hashes that pin it.

| instrument | md5 | what it is |
|---|---|---|
| `a3gc_grade.py` | `74bae3b43a1d6cf29e4b3e50ec1b6275` | THE COMPARATOR — the grading path |
| `a3gc_grade_selftest.sh` | `6adcf46aca9aad7b3f249e7aa1285dac` | its selftest, 119 units / 0 failures |
| `a3gc_genmesh.sh` | `07bc22d7b591dfae3c22661b00b40ddf` | the §2.5 family generator, §6 stage 1 |

**VERIFIED BY THE SUPERVISOR PERSONALLY, not relayed**, immediately before this freeze:
selftest **119 passed / 0 failed** on the supervisor's own run; `ast.Assert` census **0**
(L-332); `bash -n` clean on both shell instruments; **zero `meshgen-probe` references in any
of the three**, so the `G-QUARANTINE` of AMENDMENT 3 is intact in the instruments themselves;
`diff <(git show HEAD:PREREGISTRATION.md) <(head -610 PREREGISTRATION.md)` **empty, rc 0**, so
`lines whose number changed above this section: 0` holds byte-exactly for AMENDMENT 3; and the
repaired `a3gc_genmesh.sh:221` reference was **driven** — `a3gc_grade.py probe --case
A3-onera-m6-transonic` returns rc 0 reading a real mesh.

### THE RENAME MAPPING — stated here because committed records name the old files

The `.DRAFT` suffix was dropped **in the same act as the freeze**: a `.DRAFT` suffix on a frozen
instrument misleads exactly as badly as a suffix-less unfrozen one, only in the other direction.
Records committed earlier today — `PREREGISTRATION.md:535` (AMENDMENT 2), `:656` (AMENDMENT 3),
`docs/LAB_STATE.md:7017` and `:7020`, and the three diffs — name the OLD filenames. **Those
records are NOT rewritten.** Rule 6 forbids editing a frozen amendment, and each is a
*historically accurate* record of a check performed on a file that then bore that name. The gap
was discoverability, not truth, and this mapping closes it:

    a3gc_grade.py.DRAFT           ->  a3gc_grade.py
    a3gc_grade_selftest.sh.DRAFT  ->  a3gc_grade_selftest.sh
    a3gc_genmesh.sh.DRAFT         ->  a3gc_genmesh.sh

The three diffs (`a3gc_grade_REPAIR.diff`, `a3gc_grade_RULINGS.diff`, `a3gc_FREEZE_RENAME.diff`)
retain the old names **deliberately**: a diff is the record of a file state that existed, and
renaming inside it would falsify what was read.

### FROZEN BEFORE ITS RUNNER EXISTS — DELIBERATELY, AND IN THAT ORDER

**This item has NO runner.** There is no launcher, no runScript and no `decomposeParDict`; the
comparator takes `--l3 --l2 --l1` as SOLVED case directories that nothing yet produces. The
freeze is taken anyway and on purpose: **the comparator is the SPECIFICATION and the runner
conforms to it.** Freezing first makes it impossible for the grader to be shaped to whatever the
solver happens to emit. If the runner cannot satisfy this contract, that is a finding brought to
the supervisor, and the grader is not adjusted to accommodate it.

**What this freeze does NOT assert.** `evaluate_shock` has **never run against real VTK** — none
exists for any A3GC level and none can be computed from anything on disk. Every shock fixture in
the selftest is synthetic and is banner-marked as such in the comparator's own output. A 119/0
suite says the gates refuse what they claim to refuse; **it says nothing whatever about the M6
shock.** No A3GC level has been solved.

**SUBMISSIONS PARKED.**


---

## AMENDMENT 4 — 2026-09-11 — **PRE-COMPUTE. THE COMPARATOR FROZEN THIS AFTERNOON DID NOT IMPLEMENT §3.7, AND A DEAD SOLVE WOULD HAVE GRADED `CONVERGING`.**

**Lines whose number changed above this section: 0.**

### THE DEFECT

`a3gc_grade.py`, as frozen at commit `2215b4e765264a3f4d1f87157b0d3374acfdd15e` with md5
`74bae3b43a1d6cf29e4b3e50ec1b6275`, **did not implement the strict completion rule or the age
guard that §3.7 registers.** `read_log` parsed `end_line`, `times` and `exec_times` and **nothing
ever read them again.** There was no `rc` check, no `End`-line gate, no `last time == endTime`, no
`ExecutionTime` count and no field-age guard.

**The consequence, and it is the dangerous kind because every number in it looks like success.** A
level that died partway through would have been graded on its truncated history, and **a dead solve
plateaus perfectly** — so `G-PLAT` would have seen an immaculate tail and passed it, and the triple
could have returned `CONVERGING` on a corpse. At §5's registered **1,525 core-min** that is the whole
spend of the item, used to certify a dead solve as converged.

### WHY THIS IS A REPAIR AND NOT A NEW GATE

**§3.7 has registered the completion rule since this document was written.** The comparator was not
missing a gate; it was **failing to do what its own document says it does.** Making an instrument
obey its own registration is a repair, not a registration change.

**Legal because `CLAUDE.md` rule 2 closes gates after FIRST COMPUTE, and no A3GC level has solved.**
Re-checked at this amendment: `/home/ubuntu/certonomous-runs/A3GC-L3`, `A3GC-L2` and `A3GC-L1` **do
not exist**, and the reader was shown able to see a directory that does — `A3-onera-m6-transonic`
resolves — so that absence is measured, not assumed. `VERIFICATION_CHARTER.md` §2d.1's four-condition
repair exception was consulted and **does not apply**: it governs changes made after the FIRST GRADED
SOLVE, and there has been none.

**EVERY HAZARD POINTS ONE WAY, which is the test that decides it.** The change is **strictly
stricter**, adding refusals only. **A completion gate can turn a `PASS` into `NOT A RESULT` and can
never manufacture a favourable verdict.** It implements something already registered rather than
inventing a criterion. No result exists that could have shaped it. And it was **found by reading the
code, not by anyone looking at an answer they wanted.**

### THE RE-FREEZE, WITH BOTH HASHES ON THE RECORD

**A freeze that quietly changed its own hash would be worthless.** Both are recorded:

| instrument | frozen `2215b4e76` | **re-frozen, this amendment** |
|---|---|---|
| `a3gc_grade.py` | `74bae3b43a1d6cf29e4b3e50ec1b6275` | **`73dbe368934956700da87e5a1f44ea0c`** |
| `a3gc_grade_selftest.sh` | `6adcf46aca9aad7b3f249e7aa1285dac` | **`3a709fa46edfe996a7cd5d1de2100bab`** |
| `a3gc_genmesh.sh` | `07bc22d7b591dfae3c22661b00b40ddf` | `07bc22d7b591dfae3c22661b00b40ddf` — UNCHANGED |

Selftest **119 → 143 passed, 0 failed**, verified on the supervisor's own run; `ast.Assert` census
**0**; zero `meshgen-probe` references, so AMENDMENT 3's `G-QUARANTINE` is intact.

### `G-COMPLETE`, AND THE FOUR THINGS DECIDED BY MEASUREMENT

Six clauses, **each printing its measured value pass or fail**, because a completion gate that reports
only its verdict is unauditable: (1) `rc == 0`; (2) an `End` line; (3) last printed `Time =` equals
`endTime`; (4) the field set present at `endTime`; (5) the `ExecutionTime` count; (6) **the age
guard**, referenced to the case's own `0/T` because `0/T` is touched last at launch and so dates the
run allowed to produce the answer. A failing clause makes the level `NOT A RESULT` and, by standing
rule 5 clause 1, the triple with it.

* **`endTime` IS NOT IN THE LOG** — zero occurrences in this case's validated primal — so clause 3 is
  uncheckable from the log alone and the case's own `system/controlDict` is the only source.
  **Absent → REFUSE, never assume.**
* **`rc` IS NOT IN THE LOG.** Read from `<case>/<log>.rc` then `<case>/rc`; **absent → REFUSE, because
  a missing exit code is not a zero exit code.** The refusal names where the runner must write it and
  that it must be captured **inside** the detached wrapper — `setsid timeout cmd` exits 0 for every
  outcome.
* **WHICH FORM OF RULE 4 CLAUSE 5 APPLIES, decided by measurement.** The rule gives
  `round(endTime/deltaT)` for the historical unit-step case where every step prints, and
  `n_exec == steps written` otherwise. **This family prints at `printInterval`** — measured, 61
  `ExecutionTime` lines against `endTime` 6000 at `deltaT` 1 — so **`n_exec == n_times` is the gated
  form**, and the `1 + floor(endTime/printInterval)` arithmetic is printed beside it as a **reported
  cross-check, never gated.** Gating the unit-step form would have refused every correct level.
* **"FIELDS PRESENT" IS NOT AN INVENTED LIST.** The required set is whatever the case's **own `0`**
  holds: the item must write back what it initialised. Searched under the case root and every
  `processor*/`; **no `endTime` directory is a FAILURE, never a pass.**

### THE CONTROL THAT PROVES IT, AND THE DEFECT IT CAUGHT IN ITS OWN FIXTURE

`D-NO-COMPLETION-GATE` removes the gate and requires the dead solve to be **SEEN** to grade `PASS`.
**On its first run it reported "THE SUITE FAILED TO FAIL"** — the dead fixture carried only 8 samples,
so **`G-PLAT` refused it for want of evidence and `G-COMPLETE` was never the thing under test.** The
fixture now carries **12 samples flat to 1e-9 ending at `Time = 1100` against an `endTime` of 6000**:
a solver that died at 1,100 of 6,000 iterations with an immaculate tail. Unit `F1g` asserts that
**G-PLAT has no complaint about it** and that G-COMPLETE is the only thing catching it.

**The lesson is recorded because it generalises past this file: a control that happens to fire for an
unrelated reason reads as a gate that works.** Rebuilding the fixture to remove that luck is what
turned a coincidence into a proof. In the same pass every fixture `cp -r` became `cp -a` — **mtimes
are now evidence, and a copy that resets them destroys the thing under test.**

### THE INPUT CONTRACT MOVED, AND THE RUNNER IS WHAT MUST SATISFY IT

**A graded level must now carry `system/controlDict` and an `rc` artifact.** Nothing on disk has
either, because nothing has run. This is recorded beside the hashes because the runner — which does
not yet exist — is the only thing that will satisfy it, and it must be written to this contract
rather than the contract bent to it.

### WHAT THIS AMENDMENT DOES AND DOES NOT DO

**IMPLEMENTS** §3.7 in the instrument that claims to grade under it, and re-freezes with both hashes
disclosed. **ALTERS NO** gate, band, threshold, cap, tolerance, cost or label: §4.2's Roache order and
`p` band, §4.3's prediction bands, §4.4's falsifier, §4.5's P1–P4, §5's cost and cap, §3.5's
tolerances and AMENDMENT 3's compositions all stand **exactly as registered**. It adds refusals and
nothing else. **THE ITEM STILL HAS NO RUNNER AND NO A3GC LEVEL HAS BEEN SOLVED.**

**SUBMISSIONS PARKED.**


---

## AMENDMENT 5 — 2026-09-11 — **PRE-COMPUTE. THE FROZEN MESH GENERATOR COULD NOT EXECUTE AT ALL, AND THE DEFECT WAS A SILENT `|| true`, NOT THE uid IT HID.**

**Lines whose number changed above this section: 0.**

### THE DEFECT

`a3gc_genmesh.sh`, frozen at `2215b4e76` / re-frozen at `367799db0` with md5
`07bc22d7b591dfae3c22661b00b40ddf`, **exits `rc=127` — `cgns_utils: command not found` — at its
FIRST container step.** All seven container steps route through one `RUN()` helper, so **not one of
them could ever have worked.** §6 stage 1 was unreachable and the item could not have been run.

**THE DEFECT IS THE SUPPRESSION, NOT THE uid.** `RUN()` ran
`source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1 || true`. That silenced the one step
that makes every later step possible, so **a dead environment presented itself as a missing binary,
seven times, with no cause attached.** Unsuppressed, the identical invocation names its own cause in
one line — `Permission denied` — and the diagnosis takes a second. **A silent `|| true` on a
prerequisite is not defensive: it converts a precise failure into an imprecise one and moves it
seven steps downstream.**

**THE MECHANISM IS NOT WHAT IT LOOKS LIKE, and the supervisor's first statement of it was wrong.**
`loadDAFoam.sh` is `-rwxr-xr-x` and **world-readable**, so this is not a file mode. It is
**DIRECTORY TRAVERSAL**: `/home/dafoamuser` is `drwxr-x---` `1002:1002`, so uid 1000 cannot enter it
at all. Host `id -u` = **1000**; the image's `dafoamuser` = **1002**.

**AND HERE IS WHY IT SURVIVED INTO A FROZEN FILE: THE `--dry-run` PRINTER OMITTED EXACTLY THE TWO
THINGS THAT BREAK** — the `-u` flag and the environment-load prefix. `--dry-run` was never a
rehearsal of the real command, so it produced confidence instead of evidence. The feasibility probe
worked only because its own launcher passed **no `-u` at all** and ran as the image default.

### THE REPAIR — THREE PARTS, AND BOTH OBVIOUS FIXES WERE MEASURED AND ARE WRONG

**(a) THE SUPPRESSION IS DELETED AND NOT REPLACED BY A QUIETER ONE.** It is replaced by a
**POSITIVE CAPABILITY ASSERTION** — `CLAUDE.md` rule 3, plant-the-zero, applied to an *environment*
rather than a field — which demands the shell SHOW a variable and a binary that exist only after a
successful load, and **exits 97 naming `WM_PROJECT_DIR`, `cgns_utils` and `id`** if it cannot.
**Both obvious alternatives were measured and both fail:**
* **`set -e` hoisted above the source ABORTS THE SHELL, rc=1**, at `OpenFOAM-v2506
  etc/config.sh/setup:207` — measured in this pinned image under both `bash -c` and `bash -lc`, at
  uid 1002 and uid 0. **That is the same defect class that breaks D8G's generated `cmd.sh`
  (`d8g_genmesh.sh:232-233`), and the obvious fix would have imported it straight into A3GC.**
* **The source's rc is not a test:** without `set -e` it returns **rc 0 even when the environment did
  not load** (measured at uid 1000: rc 0, `WM_PROJECT_DIR` empty, `cgns_utils` absent). **A silent
  success and a silent failure carry the same rc.**
PLANTED CONTROL, measured, so the assertion is shown able to fail: uid 1000 → `SENTINEL_FAIL`;
uid 1002 → `SENTINEL_PASS`. `set -e` is armed **after** the assertion, where it can do its job.

**(b) THE uid.** `-u "$(id -u):$(id -g)"` → `-u 1002:<host gid>`, plus `-e HOME=/home/dafoamuser` so
`HOME` no longer leaks from the host. uid 1002 traverses by the **owner** bit regardless of gid,
which is what makes (c) possible.

**(c) PRINT EQUALS EXEC, STRUCTURALLY.** `RUN()` and `HOST()` now build **one** argv array and either
print it or execute it — never two spellings. **A dry-run that rehearses a different command is worse
than no dry-run, because it manufactures confidence.** Exercised rather than argued: the dry-run's own
printed lines were fed back to `bash` verbatim, nothing retyped, and produced a real
`surfaceMesh.cgns`. Two divergences remain by design and are **named** in the repair diff rather than
left to be rediscovered.

### THE OWNERSHIP DECISION, AND WHY THE PROBE'S `0777` WAS A HALF-MEASURE

`uid 1002` + **the host's own gid** + `umask 0002` + `chmod 2775` on the mesh root + `chmod -R g+w`
over the copied template. **Measured:** with a `0777` root the container writes fine and then creates
`1002:1002` `0755` **subdirectories** that the host cannot modify or delete — **`rm -rf` of its own
run root fails.** That is a level-three discovery, bought here for nothing. The setgid + host-gid
choice yields artifacts `0664`/`0775` in the host's own group: the host can read, modify and remove
them, and **nothing on this box is made world-writable.**

### WHAT THIS AMENDMENT DOES AND DOES NOT DO

**CHANGES HOW THE CONTAINER IS INVOKED. CHANGES NOTHING ABOUT WHAT IS MEASURED OR WHAT WOULD PASS.**
`COARSEN_PASSES`, `N_LAYERS`, `WANT_CELLS`, `WANT_WING`, `S0`, `MARCH_DIST`, `CMAX`,
`AUTOPATCH_ANGLE` and the `IMAGE_DIGEST` are **byte-identical**, verified key by key; so are §6's
exit condition, the 99,840 / 798,720 / 6,389,760 refusal, the wing-`nFaces` refusal and the `G-MESH`
`checkMesh` assertion. **The grading path is NOT TOUCHED** — `a3gc_grade.py`
`73dbe368934956700da87e5a1f44ea0c` and `a3gc_grade_selftest.sh` `3a709fa46edfe996a7cd5d1de2100bab`
re-verify byte-identical against HEAD.

**LEGAL PRE-COMPUTE:** rule 2 closes gates after FIRST COMPUTE and **no A3GC level has solved**. The
`rc=127` attempt is ruled **not** to touch AMENDMENT 4's absence condition — it produced no mesh, no
cell count, **no artifact any gate reads**, the same test applied to the feasibility probe in the
`G-QUARANTINE` ruling. All three registered roots re-checked **ABSENT**, with the reader shown able
to return EXISTS for three directories that are there. The failed attempt is preserved as evidence at
`/home/ubuntu/certonomous-runs/A3GC-STAGE1-FAILED-L3-20260911T1754Z`.

### RE-FREEZE — ALL THREE HASHES ON THE RECORD

| instrument | frozen `367799db0` | **re-frozen, this amendment** |
|---|---|---|
| `a3gc_genmesh.sh` | `07bc22d7b591dfae3c22661b00b40ddf` | **`9fa240d9643308f5e9a4988614b58884`** |
| `a3gc_grade.py` | `73dbe368934956700da87e5a1f44ea0c` | unchanged |
| `a3gc_grade_selftest.sh` | `3a709fa46edfe996a7cd5d1de2100bab` | unchanged |

**SUBMISSIONS PARKED.**


---

## AMENDMENT 6 — 2026-09-11 — **TWO INSTRUMENTS, EACH CORRECT ALONE, WERE JOINTLY IMPOSSIBLE: STAGE 1 GUARANTEED THE CONDITION STAGE 2 REFUSES ON, SO A3GC COULD NEVER HAVE REACHED A SOLVE AT ANY LEVEL.**

**Lines whose number changed above this section: 0.**

### THE DEFECT

`a3gc_genmesh.sh:264` copies `0.orig` into **every** case directory it builds
(`HOST cp -r "$TEMPLATE/0.orig" "$WD/"`). `a3gc_run.sh:329` then globs `"$WD"/[0-9]*`, takes the
`basename`, and **refuses anything that is not exactly `0`** as *"a non-zero time directory … this
case has been run before."* `0.orig` begins with a digit, so it matches the glob; its basename is not
`0`, so it refuses. **Stage 1 therefore GUARANTEES the condition stage 2 refuses on, at every level.**
Measured: `--stage prepare` on the freshly generated, never-solved `A3GC-L3` exits 2 on `G-COLD`.

**Each file is correct on its own** — shipping `0.orig` beside a case is ordinary OpenFOAM practice,
and refusing a stale time directory is exactly what §3.3 asks for. **The defect exists only in their
composition, which is why neither file's own review could have caught it** and why it appeared at the
first attempt to run the two in sequence.

**AND THE SAME FILE BOTH REQUIRES AND REFUSES IT:** `a3gc_run.sh:326` refuses a template that has
**no** `0.orig`, then `:329` refuses the work directory for **having** one.

### THE RULING: THIS IS NOT A GATE CHANGE, AND THE DISTINCTION IS LOAD-BEARING

**§3.3 registers, verbatim: "No TIME DIRECTORY other than `0` exists."** `0.orig` **is not a time
directory.** It is OpenFOAM's standard pristine initial-condition template, it is never a time
directory in any OpenFOAM case, and this item's own runner depends on it being present. **The glob
`[0-9]*` with a `basename != 0` test is simply a WRONG TEST for "is a time directory".** So the gate's
registered *meaning* is untouched; what is repaired is an implementation that **misclassifies a
non-time directory as a time directory**. That is the same class as AMENDMENT 4's repair — an
instrument failing to do what its own registration says.

**DISCLOSED PLAINLY, BECAUSE IT WOULD BE CONVENIENT TO LEAVE UNSAID: A3GC'S FIRST COMPUTE HAS NOW
OCCURRED.** The L3 mesh at `/home/ubuntu/certonomous-runs/A3GC-L3` is an artifact `G-MESH` and
`G-SYS` read, so by the test this item has applied throughout — *rule 2 closes gates once compute has
produced an artifact a gate of this item reads* — **A3GC's gates are CLOSED.** A gate change is
therefore no longer available, which is exactly why this amendment states the repair/gate-change
distinction rather than relying on it quietly. **If this were a gate change it would be refused and
the rung would stand `BLOCKED` instead.**

**Belt and braces, against `VERIFICATION_CHARTER.md` §2d.1's four conditions:** (1) it repairs a
**demonstrable error** — two frozen instruments that are jointly impossible — not a preference;
(2) it was established by **something that grades nothing**: `--stage prepare` exiting 2, a producer
step that renders no verdict, on a case with no result in any direction, so it **cannot have been
selected to move a verdict**; (3) this record discloses it, names the instrument and quantifies what
moved; (4) no pre-repair value exists to record beside a published one, because **nothing has been
graded**.

### THE REPAIR REFUSES *MORE* THAN THE ORIGINAL, NOT LESS

The name is **classified**, not pattern-matched: `0` is the cold start; a well-formed OpenFOAM time
name that is not `0` gets the original refusal, unchanged and word for word; **anything that begins
with a digit but is NOT a valid time name is now REFUSED EXPLICITLY** where the frozen code would
have refused it with a misleading message. The exemption is the **single literal string `0.orig`** —
not a prefix rule, not a suffix rule. **`0.orig.bak` REFUSES.** Widening a guard's exemption to a
pattern is how a guard dies, and it is not done here.

**THE LANE DID NOT DELETE `0.orig` TO GET PAST THE GUARD, AND THAT RESTRAINT IS THE POINT.** Deleting
it would have produced a green stage 2 and destroyed the case's initial-condition template — the
tidy, wrong move that converts a real finding into a silent corruption.

### SECOND FINDING: `prepare` IS NOT ATOMIC

Before refusing, `prepare` had already moved both stage-1 logs into `meshgen/` and written
`controlDict`, `decomposeParDict` and the runScript. **A step that refuses should leave nothing
behind, and this one does not.** Measured mitigations: the log move is **idempotent**, and **no cold
`0` was created**, so the refusal is re-runnable without corruption. Recorded rather than repaired —
the partial side effects are harmless here and repairing them is a larger change than this amendment
should carry.

### WHAT THIS AMENDMENT DOES AND DOES NOT DO

**REPAIRS the classification of one directory name in `G-COLD`'s implementation.** **ALTERS NO** gate,
band, threshold, cap, tolerance, cost or label: §3.3's three assertions stand verbatim, and the
warm-start protection they exist for is **strictly stronger** after this change than before.
`a3gc_run.sh` is the **producing** path and is **not** part of the frozen grading path; the frozen
`a3gc_grade.py` `73dbe368934956700da87e5a1f44ea0c`, `a3gc_grade_selftest.sh`
`3a709fa46edfe996a7cd5d1de2100bab` and `a3gc_genmesh.sh` `9fa240d9643308f5e9a4988614b58884` are
**NOT TOUCHED**. **The six `G-COMPLETE` clauses remain UNVERIFIED against a real solve.**

**SUBMISSIONS PARKED.**
