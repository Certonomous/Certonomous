# RUNG 1 R2 pre-registration — ONERA M6 surface pressures against AGARD AR-138, with the family band

**Team: cfd. Case id `RUNG1-M6-R2`. v1.0, drafted 2026-09-03 by a cfd lane.**

> ## 🔒 FROZEN 2026-09-03T19:41Z. NO COMPUTE HAS BEEN RUN UNDER THIS FILE.
>
> **STATUS FLIP ONLY. NO GATE, THRESHOLD, CAP OR LABEL IS CHANGED BY THE FREEZE.** The
> commit that carries this flip changes this block and nothing else; the diff is the
> evidence and is asserted in that commit's message.
>
> **What the freeze means and who did what.** The cfd supervisor performed the rule-2
> personal check (`SUPERVISION_CHARTER.md` §3 check 4) by reading this file at commit
> `63c12a9e` and authorised the freeze. Authorship of the registration's text is this
> lane's; the *check* is the supervisor's and was not delegated. **The supervisor
> separately verifies THIS freeze commit exists before `S5` launches** — that check is
> theirs, is not satisfied by this paragraph, and no message from any agent substitutes
> for it.
>
> **Registered run roots RE-VERIFIED ABSENT AT FREEZE TIME, not merely at drafting**
> (rule 2's before-first-compute clause requires the condition and how it was checked):
> at 2026-09-03T19:41Z a test of each of `verification/runs/RUNG1_M6_R2_runs/` and its
> `mesh/`, `L1/`, `L2/`, `L3/` returned ABSENT for all five, and `ls verification/runs/`
> piped to a count of `RUNG1_M6_R2_runs` returned 0.
>
> **From this commit the gates are closed.** Changes land only as dated addenda that
> cannot alter a gate, threshold, cap or label; originals are struck, never rewritten.

---

## 0. THIS IS A SUCCESSOR. THE PREDECESSOR IS NOT MODIFIED, AND ITS §5 OUTCOME STANDS.

**It succeeds `verification/campaign/RUNG1_M6_PREREGISTRATION.md`, frozen at `c7f99bb1`.**
That file is **not edited, not amended and not reinterpreted here.** Its §5 conditional —
*"outcome if max non-orth > 70°: branches (a1)/(a2) are dead, snappy becomes the route"* —
**executed correctly against the regime in force when it was written, and its outcome stands as
committed.**

**Why a successor and not an addendum.** The measurement that reopens the question (`R1-M1`,
§0.2) carries **no verdict of the fixed vocabulary** and decided **no gate**, so nothing in
`c7f99bb1` has been graded or altered by it. Reviving, *after seeing a measurement*, a branch
that a frozen registration killed — by editing that registration — is precisely the shape rule 2
exists to forbid: it would let the gate be chosen to fit the answer. A successor at a new path,
frozen before its own compute, is the clean instrument. **Ruling taken by the cfd supervisor,
2026-09-03.**

### 0.1 THE ONE REASON A CLOSED ROUTE IS OPEN, AND IT IS NOT A NEW MEASUREMENT

The predecessor's branch-killing conditional was **gate-based**: it killed `(a1)`/`(a2)` because
a mesh-quality gate **blocked**. **Sanaa's ruling of 2026-09-03 ~21:00Z reclassifies mesh-quality
mismatch out of the blocking class into the record-as-prediction class** —
`etc/sessions/2026-09-03T2100Z_sanaa_launch_rule.md`, which lists *"Mesh quality gates —
skewness, non-orthogonality, aspect ratio, y+ commitment failing the standard"* among the
categories handled by *"record the mismatch as a prediction …, launch, monitor, then write
predicted vs actual on the certificate."* Corroborating captures:
`etc/sessions/2026-09-03T2000Z_sanaa_governance_reform.md` (reported-not-gated is the default
mode) and `etc/sessions/2026-09-03T2200Z_sanaa_running_first.md` (*"non physics/ill posedness
relqted gqtes blocking a run"* named as a thing never to be seen again).

> **THE GATE DID NOT MOVE. WHEN IT APPLIES MOVED.** The 70° threshold is unchanged, the frozen
> grader still applies it, and it still lands on the certificate. It simply no longer refuses a
> launch. **No new measurement reopened `(a1)`. A ruling did.** Nothing in this paragraph is
> evidence about the mesh.

### 0.2 `R1-M1` RAN UNGRADED AND UNCOVERED, AND THAT IS DISCLOSED HERE RATHER THAN CURED

`verification/runs/RUNG1_M6_runs/M1_ugrid_reimport/` was executed on 2026-09-03 at
**0.5668 core-min** with **no covering frozen pre-registration**. Its own record stamps this:
`M1_CHECKMESH_READING.json` carries `"covered_by_a_frozen_preregistration": false` and
`"verdict": "NONE — no verdict of the fixed vocabulary attaches to this record."`
The cfd supervisor has recorded the breach as the supervisor's, arising from an internally
inconsistent brief.

> **NOTHING IS RETROACTIVELY FROZEN TO COVER IT.** That is the one move rule 2 exists to forbid.
> `R1-M1` stands as an **ungraded admissibility measurement**, it grades nothing, and **no gate
> in this registration rests on it.** Its readings are used below only as *inputs and
> predictions*, never as evidence for a verdict.

---

## 1. THE REFERENCE — UNCHANGED FROM THE PREDECESSOR, AND RE-PINNED HERE

| the reference | `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/case_2308.dat` |
|---|---|
| sha256 | **`020c5fcc58060737024eb87d9404f56bc563f3f6f15e337675c47477fa91f0d0`** |
| structure | 7 zones, `I = 34/34/34/34/45/45/45` = **271 rows**, matching AR-138 §5.1.1's own prose count of *"271 pressure orifices divided in 7 sections"* |
| conditions | `Run= 308, Mach= 0.8395, Alpha= 3.06, Re= 11.72x10**6` |

🔴 **THE AR-138 PDF IS PROVENANCE AND IS NEVER A SOURCE OF NUMBERS.** Its OCR sidecar
`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.txt` renders this very
case's Mach as `.9395` against the machine file's `0.8395` — **an 8 read as a 9, 12 % in the
freestream Mach of a transonic case** — and the numeric body of every table is absent from the
text layer. **Every Gate P reference value comes from `case_2308.dat` at the pinned sha256, and
the comparator REFUSES if the hash does not match.**

---

## 2. THE GRID — THE ROUTE IS THE ~61.5° WALL-FUNCTION pyHyp FAMILY

### 2.1 The finding that selects it, stated with its evidence and its limits

**The 88.889° of `R1-M0` is a property of the WALL-RESOLVED COMMITMENT, not a limit of pyHyp on
this geometry.** The same generator, on the same downloaded surface mesh, at wall-function
spacing, measures **61.1581°** at 399,360 cells
(`verification/runs/MESH_AUDIT_runs/2026-08-08/mesh-cache__onera_m6__polyMesh.log.checkMesh`,
mesh present on disk at `/home/ubuntu/certonomous-runs/.mesh-cache/onera_m6/polyMesh/`), with
max skewness 1.44081, max aspect ratio 222.355, boundary openness 4.66e-17, 1 region, and
**three correctly typed patches — `wing`(wall) 6240, `inout`(patch) 6240, `sym`(symmetry) 8704.**
Four sibling pyHyp meshes read **61.4935 / 61.4935 / 61.4937 / 61.4938°** at 10,920 / 42,120 /
79,560 / 99,840 cells.

🔴 **AND THE LIMIT ON THAT EVIDENCE, WHICH THIS REGISTRATION DOES NOT PAPER OVER.** Those are
**five separate pyHyp runs, not a nested family.** Their cell ratios are 3.86 / 2.37 / 4.00 —
no `r³` anywhere. **That 61.49° is flat across five independent meshes is strong, and it is NOT
evidence that a NESTED triple holds 61.5° at every level.** `S3`/`S4` measure that, and
**this registration does not assume it.** One sibling is broken and is named so it cannot be
used by mistake: `A3-onera-m6-adjoint-vcoarse`, 24,960 cells, **135.318°, skewness 55.378**.

### 2.2 Provenance, stated and not decided

The surface mesh `m6_surfaceMesh_fine.cgns` (2,535,424 B, mtime 2020-06-28) is **downloaded and
unmodified** — the only external M6 geometry artifact on this box. **The volume grid is
LAB-BUILT** by pyHyp here. The 70° gate is therefore this lab's own generation standard applied
to its own mesh, unchanged.

**Sanaa's §2.3 boundary question from the predecessor — is a publisher's generator on the
publisher's UNMODIFIED namelist a "committee family"? — is NOT reached by this registration and
is NOT answered here.** It concerned the M6I family, which was built from a namelist this lab
**modified** in four documented places (`verification/runs/M6I_runs/build_m6i_ladder.sh` lines
30-38: `target_y_plus 1.0→0.25`, `nnodes_cylinder_input 32→64`, `nr_gs 8→16`, `nre 64→128`), so
that family is outside the question whichever way it is eventually ruled. **The question is now
documentation, not critical path**, because the gate it turned on no longer blocks.

---

## 3. CASE AND CONDITIONS

ONERA M6 semi-span wing, **AGARD AR-138 test 2308**: **M∞ = 0.8395, α = 3.06°,
Re = 11.72 × 10⁶ on the MAC c = 0.64607 m**, `S_ref = 0.7532 m²`.

**Carried forward so it cannot be re-confused:** TMR's page gives `Re_c_root = 14.6e6` on the
**root** chord; `14.6e6 × 0.64607/0.810491 = 11.64e6`. **This ladder uses Re = 11.72e6 on the
MAC. Applying 14.6e6 to the MAC would be wrong by 25 %.**

**Solver:** `rhoSimpleFoam` (steady compressible SIMPLE), **k-ω SST**, fully turbulent,
**`nutUSpaldingWallFunction`** — continuous across the whole `y⁺` range, so the discrete
operator cannot change part-way along a triple even though this family sits at wall-function
spacing.

Closed non-dimensionally (AR-138 B1-3 §3.7 records tunnel stagnation temperature 292–315 K,
*"cannot be controlled"*): `T∞ = 288.15 K`, `p∞ = 101 325 Pa` (ISA, **chosen not measured**),
`U∞` from `M∞`, and **`μ∞` back-solved to deliver Re = 11.72e6 — `μ` reproduces `Re`; it is not
a physical property of air at 288.15 K.**

### 3.1 NUMERICAL SETTINGS — REGISTERED, NOT SILENTLY PICKED

Sanaa's 2100Z lists *"scheme/order not pre-approved"* as a prediction category, so an unusual
choice is **recorded and launched**, never refused — but it must be **named here**, and it is.

| setting | value | why |
|---|---|---|
| `snGradSchemes default` | **`limited corrected 0.5`** | the non-orthogonal correction is what makes a >65° face solvable; `limited 0.5` bounds the explicit correction so it cannot destroy diagonal dominance where the correction is large |
| `laplacianSchemes default` | **`Gauss linear limited corrected 0.5`** | same correction, same limiter, consistently applied |
| `nNonOrthogonalCorrectors` | **2** | at a predicted max of ~61.5° (and up to 88.9° in the recorded-prediction case) the explicit correction is not small; 0 correctors loses diffusion accuracy first and boundedness second |
| `divSchemes` momentum | `bounded Gauss linearUpwind grad(U)` | second order with a gradient limiter; first order would not resolve the shock position Gate P is graded on |
| `divSchemes` turbulence | `bounded Gauss upwind` | boundedness of `k`/`ω` bought deliberately at first order |
| `decomposition method` | **`hierarchical`, coeffs `(n 1 1)`** | **the decomposition-seed field, satisfied by construction.** `hierarchical` is a pure geometric bisection with **no random number generator**, so the partition is a deterministic function of the recorded coefficient triple and the cell centres. `scotch` is not reproducible run-to-run and is **not used**. The triple IS the seed and is recorded per level in §7. |

---

## 4. GATES, THRESHOLDS, CAPS AND LABELS — **DRAFTED, NOT FROZEN**

**Under Sanaa's 2100Z every gate below is graded AFTER the run, on evidence, by the frozen
grader. None of them blocks a launch.** The single exception is §6, physical ill-posedness.

### Gate A — mesh admission. **REPORTED AND GRADED, NOT BLOCKING.**

Read off the named numeric maxima, **never off a verdict string** (L-459: on this box checkMesh
prints `Non-orthogonality check OK.` at 88.889° and its closing `Failed N mesh checks` counts a
different check entirely).

| check | threshold | source |
|---|---|---|
| max non-orthogonality | **≤ 70°** | `docs/standards/MESH_STANDARD.md` §3.1 |
| max skewness | **≤ 4** | §3.2 |
| max aspect ratio | **advisory 1000, never a lone rejection** | §3.3 |
| cell-count ratio, both pairs | **`r³` exact on integers** | L-430 |
| **points-file sha256 all three DISTINCT** | **required** | §5.1 |
| §11.4 fields non-null | required | |

### Gate G — grid convergence. Graded: `C_D` primary, `C_L` companion.

| gate | threshold |
|---|---|
| **G1** iterative convergence | change in `C_D` over the last 500 iterations **≤ 1/10 of the L1–L2 difference**, every level |
| **G2** residual behaviour | §4.1 |
| **G3** observed order | `p` in **1.5 – 2.5** |
| **G4** GCI | `GCI_fine` on `C_D` at **`Fs = 1.25`**, printed on every number, **never quoted when the three values are not monotone** |

**Rule 5 ordering unmodified.** (1) any level not iteratively converged or not plateaued →
**`NOT A RESULT`**; (2) triple `DIVERGENT`/`STAGNANT`/`OSCILLATORY`/`EXACT` → **`NOT A RESULT`**,
value and both triples and orders printed beside it; (3) `CONVERGING` → `PASS` inside the band
else `GATE FAIL`, GCI printed. **The gate can only turn a `PASS` or `GATE FAIL` INTO
`NOT A RESULT`, never the reverse.**

### 4.1 G2 — PLATEAU-AND-STATIONARITY, NOT 1e-8, AND NOW MACHINE-CHECKED

The predecessor established on measured evidence that a hard `1e-8` floor on this case spends the
whole budget and returns `NOT A RESULT` on a solution whose answer stopped moving in the sixth
decimal place. That reasoning is **carried forward unchanged**, and it is now **executed by an
instrument rather than by hand**: `scripts/residual_max_over_equations.py`.

- **G2a — REDUCTION.** Every scaled initial residual has fallen **≥ 4 orders** from iteration 1.
- **G2b — PLATEAU.** Over the last **1,000 iterations**, the **max-over-equations initial
  residual** drifts **≤ 5 %**, either direction.
- **G2c — STATIONARITY OF THE ANSWER.** `C_D` stationary over the last **2,000 iterations** to
  **≤ 1/10 of the L1–L2 difference**.

**THE DISCLOSURE THAT TRAVELS ONTO THE CERTIFICATE, and it is not optional:**
> **The residual reaches a FLOOR and does not converge to machine zero. The plateau value of the
> max-over-equations residual is REPORTED beside the result.** A plateau is not convergence.

**Disclosed:** the 4-order / 5 % / 1,000-iteration numbers were chosen by the predecessor while
looking at a **different configuration's** data (`DARhoSimpleCFoam` / Spalart–Allmaras at
`yPlus` mean 33.75). They are not fitted to this ladder's own answer. **Newly relevant and
stated honestly: this registration runs at wall-function spacing, so that reference history is
now MUCH CLOSER to the registered configuration than it was for the predecessor — which
strengthens the basis and is disclosed as a change in the basis, not smuggled in as new data.**

### Gate P — surface pressures against AGARD AR-138. **SANAA'S DELIVERABLE.**

`C_p` at the seven published sections `y/b = 0.20 / 0.44 / 0.65 / 0.80 / 0.90 / 0.96 / 0.99`
against the 271 tapped values, with the grid-family band on every station.

| band channel | value | status |
|---|---|---|
| numerical (mesh) | **`GCI_fine` from Gate G**, `Fs = 1.25` | measured by this ladder |
| reference accuracy | **`ΔCp = ±0.02` at `Mo = 0.84`** — AR-138 B1-4 §6.1 | published |
| read-off | **ZERO — machine-readable at a pinned hash** | claimed, and defensible |

**Two systematics disclosed and deliberately NOT put in the band**, because quantifying them
would be inventing a number: (1) AR-138 B1-4 §6.2 records *"Wall interference corrections: no
corrections"* at a semispan-to-tunnel-width ratio of 0.7, and the report declines to quantify it;
(2) AGARD's design TE is **0.14104 % chord thick** while the geometry here is **sharp** — so
**Gate P is graded on `x/c ≤ 0.90` and the rear 10 % is plotted and reported, never graded.**

**Gate P sits behind Gate G. A `PASS` on a family that is not `CONVERGING` is `NOT A RESULT`.**

---

## 5. PREDICTED MISMATCHES — RECORDED AS PREDICTIONS, NONE LAUNDERED

Sanaa 2100Z: *"record the mismatch as a prediction …, launch, monitor, then write predicted vs
actual on the certificate. That comparison is the payoff."* **Each row below is a prediction this
registration makes and the frozen grader judges afterward.**

| # | prediction | basis, and its honesty label |
|---|---|---|
| P1 | **Max non-orthogonality will exceed the 70° standard on the `R1-M0` topology: 88.88926674°, 206 severe faces, max aspect ratio 35,820.55869** | **MEASURED**, `verification/runs/RUNG1_M6_runs/M0_pyhyp_admission/foam/log.checkMesh:91`. **Carried forward, not erased and not softened.** Expect degraded near-wall accuracy and possible convergence difficulty; expect the band to widen. |
| P2 | **The nested triple built at wall-function spacing will land near 61.5°, and this is the prediction most likely to be wrong** | **INFERENCE from five NON-NESTED meshes** (61.1581 / 61.4935 / 61.4935 / 61.4937 / 61.4938°). Not measured on any nested family. If the triple exceeds 70°, that is a recorded miss and the run still launches. |
| P3 | **`y⁺ ≈ 1.05` on the wall-resolved branch is DERIVED FROM A FLAT-PLATE CORRELATION, NOT MEASURED** | Stated as an input, never as a measurement. The **only** honest `y⁺` number is the one the solver prints from the converged field, and it does not exist yet. |
| P4 | **First-cell height as BUILT differs from as REQUESTED: median 1.6167e-06 m against a requested 1.319e-06 m, spread max/min 11.36 across the wall** | **MEASURED**, `verification/runs/M6S_runs/P_pyhyp_wall_resolved_probe/read_grid_first_cell.py`. The requested parameter is the thing that lied in F12; only the value read back off the built grid is the truth. |
| P5 | **Max skewness will exceed the standard's 4 on the M6I route: 5.11159 (L1) and 8.30139 (L2)** | **MEASURED**, `R1-M1`, ungraded. Recorded here so the M6I route cannot be described as a one-axis miss if it is ever revisited. |
| P6 | **The `.mesh-cache` topology's farfield is only ~12.7 chords** — bounding box `(-10.51, -12.69, 0)` to `(12.90, 12.69, 11.97)` — against M6I's 100 | **MEASURED** from the checkMesh log. **Tight for a transonic case; expect a blockage-like `C_p` bias, direction and magnitude UNKNOWN and not quantified here.** The registered build in `S3` uses `marchDist` ≥ 50 to reduce it, and whichever is used is reported. |
| P7 | **Patch names differ by level in any hcf-generated family: `wing/symmetry/farfield` on the generator level and `WING3D/SYMMETRY/FARFIELD` on every coarsened level** | **MEASURED**, `R1-M1`. A driver assuming one name set would **silently mis-apply boundary conditions to two of three levels**. Every `boundaryField` in this ladder uses an explicit per-level name set or a regex, and the launcher **refuses** a level whose patch names it did not expect. |
| P8 | **Cost will land near 101.7 core-min and the estimate's basis is a different solver** | §7. Direction of the error is known to be **upward** (two turbulence equations instead of one) and is NOT corrected for. |

**Two BLOCKING PHYSICS FIXES were required before this registration could exist. Both are
landed, and neither is a prediction:**

| fix | what was wrong | evidence it is fixed |
|---|---|---|
| **S1** | **No monitor on this box computed a max-over-equations residual.** A sweep of `scripts/`, `sdk/` and `verification/runs/` returned one hit, `sdk/workflows/mega_batch.py:669`, Ahmed-body specific and on the **final** residual — which `scripts/check_convergence.py` documents as its own failure mode 4. Sanaa 2000Z names a residual print that is not the max over equations as a blocking physics fix. | `scripts/residual_max_over_equations.py`, five planted controls all firing, identical under `python3 -O` (L-332), verified against a real production log |
| **S2** | **`R1-M0`'s mesh was a closed all-wall box**: one patch `defaultFaces` type `wall`, 9,376 faces — no inlet, no outlet, no symmetry. Sanaa 2100Z's named ill-posed class. | `verification/runs/RUNG1_M6_runs/M2_M0_patch_identity/` — `wing`(wall) 1560, `symmetry`(symmetry) 6256, `farfield`(patch) 1560, with every checkMesh geometry field **identical before and after**, proving a re-labelling and not a re-meshing |

> 🔴 **AND THE FINDING ABOUT OUR OWN PROCEDURE, RECORDED BECAUSE IT IS UNCOMFORTABLE.**
> The predecessor's §5 selected *"snappy is the route"* off an 88.889° reading **taken on a mesh
> that could never have been solved at all.** The geometric measurement stands — checkMesh reads
> real geometry regardless of patch typing — but **a branch-killing decision rested on a grid
> with no boundary conditions. We measured admissibility without ever asking whether the object
> could be run.** Gate A of this registration therefore requires patch identity as an admission
> field, not as an afterthought.

---

## 6. THE ONE THING THAT STILL BLOCKS: PHYSICAL ILL-POSEDNESS

Sanaa 2100Z's named exception: *"a setup that's physically ill-posed (no outlet, inconsistent
boundary conditions, geometry with leaks) will diverge and teach nothing — that's a blocking
physics fix."* **Checked per level before launch, and a failure BLOCKS:**

1. **≥ 3 patches present, with `wing` type `wall`, a symmetry plane type `symmetry` (never
   `empty`, never `wall`), and a farfield type `patch` carrying a freestream in/out condition.**
2. **`Boundary openness` ≤ 1e-12** — no leaks.
3. **`Number of regions: 1`.**
4. **Min cell volume > 0** — no inverted cells.
5. **Patch names matched against the level's own expected set (P7), refusing on a mismatch.**

**High non-orthogonality is NOT ill-posedness. It is a quality miss and it launches.**

---

## 7. COST, CAP, AND THE FLEET SAFETY CEILING

**Unit: core-minutes.** Dollars **DERIVED, NOT MEASURED**, at `c7a.4xlarge` **$0.0513/core-h**
(owner-stated; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5).
Rate basis: **4.02e-08 core-min/cell/iteration**, the predecessor's conservative figure,
re-derived across a 9.5× mesh range. Iteration schedule **2,000 / 3,000 / 4,000**.

| step | what | levels (cells) | est. core-min | **cap (3×)** | derived $ at cap | decomposition |
|---|---|---|---|---|---|---|
| `S3` | build the nested pyHyp triple, `r = 2` | 8,970 / 71,760 / 574,080 | **2.0** | **6** | $0.0051 | serial |
| `S4` | `checkMesh` ×3 + points-hash family proof | — | **0.5** | **2** | $0.0017 | serial |
| `S5` | solve, three levels | as above | **101.7** | **306** | **$0.2617** | `hierarchical (4 1 1)` / `(8 1 1)` / `(16 1 1)` |
| `S6` | grade: Roache triple, then Gate P | — | ~0 | — | — | serial |
| | **TOTAL** | | **≈ 104.2** | **314** | **≈ $0.27** | |

### 7.1 🔴 THE FLEET SAFETY CEILING — THE ONE HARD STRUCTURAL STOP THAT SURVIVES 2100Z

Sanaa: *"a fleet-wide safety ceiling on any single run (e.g. 3× its registered cost cap, or the
box's remaining budget, whichever is smaller) … at the ceiling the monitor stops the run
gracefully regardless of residual trend."*

> **CEILING FOR `S5` = min(3 × 306, remaining envelope) = 918 core-min = $0.7849 DERIVED.**
> The $1,000 standing envelope is 1,169,591 core-min at the recorded rate, so **3× the cap is the
> binding term and the ceiling is 918 core-min.**
> **At the ceiling the monitor stops the run GRACEFULLY, regardless of residual trend.**
> Justification, hers: the T12 lesson is that the launcher's own flag never fired, so something
> must be **structurally guaranteed** to stop a run — but that something is a ceiling far above
> the estimate, not the estimate itself. The estimate is a prediction to be tested; the ceiling
> is protection against the box being eaten.

### 7.2 THE MONITOR'S AT-DEADLINE BEHAVIOUR — per 2000Z, sidecar on the LOG

At the deadline the monitor classifies the **max-over-equations initial residual**
(`scripts/residual_max_over_equations.py`, window **1,000 iterations**, converted from the
**measured** print interval so the classification cannot depend on a print setting):

| classification | action |
|---|---|
| **descending** (fell ≥ 0.10 decades over the window) | **extend, bounded and booked** — each extension recorded, never open-ended, and never past §7.1's ceiling |
| **plateaued-or-oscillating** | **stop gracefully — "non-convergent, reported not gated"** |
| **diverging** (rose ≥ 0.50 decades, or any non-finite residual) | **kill** |

**The sidecar is attached to the LOG, not the process** — `<log>.residual_sidecar.json` — so it
survives a detached run whose pid this lab does not own, and a session that ends mid-solve.
Thresholds are the **fleet defaults**; any override is recorded in the sidecar as an override.

### 7.3 CALIBRATION — rule 12's estimate-versus-actual

At every step's completion the actual core-minutes are read **from the logs**, the ratio
actual/predicted stated, the gap attributed (contention / waste / misprediction, **waste named
separately, never absorbed**), and a row filed to `docs/COST_CALIBRATION.md` and to
`docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md`.
**A completion report without that comparison is incomplete.**

**Ranks are taken from the SOLVER LOG's own banner, never from `system/decomposeParDict`** —
measured trap: that file can post-date the run, and the banner's **first** occurrence is not
necessarily the primal's.

---

## 8. COMPLETION — rule 4, strict, all-or-nothing

A level is done only if **all** of it holds: `rc = 0`; an `End` line; **last time == `endTime`**;
fields `U p T rho nut k omega` present at `endTime`; `ExecutionTime` count == `endTime`; and
**every field at `endTime` NEWER than the case's own `0/U`** — the age guard. **The launcher
refuses a case where `0` or a time directory already exists.** The comparator **refuses (exit 2)
rather than degrade** on any failed clause. **An absent `checkMesh` log reads `ABSENT`. It never
reads clean.**

---

## 9. THE FAMILY MUST BE A FAMILY — §5.1, AND IT IS A GATE

**Measured hazard from RUNG 0, this box, today:** its three DPW5 "levels" (hex, prism, hybrid)
have **byte-identical points files** — sha256
`870e6c6fceab6dbeea0d6494793fcbb7dd7f41c8e92056814c5398938d51f7fd`, 24,857,286 bytes each —
differing only in connectivity. **They are one resolution in three cell types, and a Roache
triple over them would measure cell-type sensitivity while calling itself refinement.**

**Therefore, before any level set is registered as a family:**

1. **The three `constant/polyMesh/points` files are hashed against each other and must be
   DISTINCT.** *(Worked precedent, `R1-M1`: `baabcad4…be89` / `1ef6c8c4…723e` / `46d8afba…db60`
   at 40,055,934 / 5,017,044 / 630,330 bytes.)*
2. **Cell-count ratios exact on integers at `r³ = 8`.**
3. **`MESH_STANDARD.md` §9.1 (three levels) and §9.2 (the similarity clause) are checked and the
   result printed**, whichever way it comes out.

> **A FAMILY THAT IS NOT A FAMILY IS WORSE THAN NO BAND.**

---

## 10. PLANTED CONTROLS — rule 3, on every zero this ladder can report

| reader | plant | must see |
|---|---|---|
| `checkMesh` quality reader | a log of the **`=`** label form **and** one of the **`:`** form | a non-null max aspect ratio from **each** |
| `checkMesh` quality reader | `Min volume` ≠ `Max volume` | a non-trivial derived cell-volume ratio, never 1 |
| `checkMesh` quality reader | replace one log's non-orthogonality maximum with a known value | that value read back |
| residual reducer | a log of the **stock OpenFOAM** print form and one of the **DAFoam** form | the same reduction from each; **measured trap — a real DAFoam log contains ZERO occurrences of "Initial residual"** |
| residual reducer | a synthetic falling, rising and flat series | **all three classes reachable** — a classifier that can only say one thing is not evidence for the thing it says |
| residual reducer | a step whose max is carried by a **different field** than the previous step's | the max **moves between fields** |
| `C_p` comparator | perturb one tap's `CP` in a **scratch copy** of `case_2308.dat` | the station deviation moves by the planted amount |
| `C_p` comparator | corrupt the reference file's sha256 | **REFUSAL**, not a silent fallback |
| force reader | perturb `C_D` in a scratch `postProcessing` file | the deviation moves |
| family reader | perturb one built mesh's node position | the points hash changes and nesting reports **non-zero** |

**A zero from a reader not shown able to see a non-zero is not evidence. A `PASS` reported by a
reader whose plant did not fire is `NOT A RESULT`, not a pass.**

---

## 11. FROZEN PATHS — the grading path is fixed at this registration's commit

| what | path |
|---|---|
| this registration | `verification/campaign/RUNG1_M6_R2_PREREGISTRATION.md` |
| predecessor, **NOT MODIFIED** | `verification/campaign/RUNG1_M6_PREREGISTRATION.md` @ `c7f99bb1` |
| run root (**ABSENT at drafting**) | `verification/runs/RUNG1_M6_R2_runs/` |
| level roots (**ABSENT at drafting**) | `verification/runs/RUNG1_M6_R2_runs/{L1,L2,L3}/` |
| reference data, hash-pinned | `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/case_2308.dat` sha256 `020c5fcc…f0d0` |
| residual reducer (**EXISTS**) | `scripts/residual_max_over_equations.py` |
| comparator (**does not exist; to be written**) | `verification/runs/RUNG1_M6_R2_runs/analyse_rung1_m6_r2.py` |
| calibration ledger | `docs/COST_CALIBRATION.md` |
| envelope ledger | `docs/campaigns/IBL-industrial-benchmark-ladder/IBL_COMPUTE_ENVELOPE_LEDGER.md` |

---

## 12. WHAT THIS REGISTRATION DOES NOT CLAIM

1. **It does not claim a nested M6 family clears 70°.** §2.1 is inference from five non-nested
   meshes, with its limits stated; `S3`/`S4` measure it and no gate rests on the inference.
2. **It does not claim `R1-M1` is evidence for any verdict.** It ran ungraded and uncovered and
   says so on its own face.
3. **It does not modify, amend or reinterpret `c7f99bb1`.**
4. **It does not answer Sanaa's committee-grid boundary question** and does not need to.
5. **It does not claim a measured `y⁺`.** P3 is a flat-plate correlation, labelled.
6. **It does not quantify the uncorrected wall interference** or the ~12.7-chord farfield bias.
7. **It does not claim `C_p` agreement in the rear 10 % of chord means anything.**
8. **It claims no rented-instance dollar figure and proposes no instance change** — that is
   reserved to Sanaa.
9. **Nothing is sent, filed, submitted or registered outside this box (rule 7).**

---

## ADDENDUM 1 — 2026-09-03, POST-COMPUTE. `v1.1`

**lines whose number changed above this section: 0**

**This addendum alters NO gate, NO threshold, NO cap and NO label.** It is appended at the
foot under rule 2's permitted post-first-compute form and rule 6's mechanics. Everything
above is untouched; the gates frozen at `3126345f` stand exactly as committed.

### A1.1 🔴 THE REGISTRATION WAS SILENT ON THREE BUILD PARAMETERS, AND THIS LANE CHOSE THEM **AFTER** THE FREEZE

**Stated plainly, because a smoothed version implying prior registration would be worse
than no addendum at all.** `3126345f` fixes the three cell counts — 8,970 / 71,760 /
574,080 — and says **nothing** about:

1. the near-wall spacing `s0` at any level,
2. `marchDist` per level (§5's P6 registers only "≥ 50"),
3. which surface file feeds which level.

**That is a drafting gap in this registration, made by the lane that wrote it.** It was
found while building `S3`, i.e. **after the freeze**, and the choices below were therefore
made **post-freeze, on 2026-09-03, by the cfd lane, with the cfd supervisor's endorsement.**
They were **not** registered in advance and this addendum does not pretend otherwise.

| parameter | L3 | L2 | L1 | why |
|---|---|---|---|---|
| surface faces | **390** | **1,560** | **6,240** | `r = 2` in each surface direction. Measured, not inferred from file size: existing volume meshes on these same surfaces divide exactly by their 64 layers — 24,960/64 = 390.0, 99,840/64 = 1,560.0, 399,360/64 = 6,240.0 |
| surface file | `A3-onera-m6-adjoint-vcoarse/surfaceMesh.cgns` | `A3-onera-m6-adjoint-coarse/surfaceMesh.cgns` | `A3-onera-m6-adjoint-coarse/m6_surfaceMesh_fine.cgns` | all under `/home/ubuntu/certonomous-runs/`, read-only |
| pyHyp `N` | **24** | **47** | **93** | 23 / 46 / 92 cell layers, `r = 2` |
| **`s0`** | **4.0e-04** | **2.0e-04** | **1.0e-04** | **halves with `r`** — see A1.2 |
| **`marchDist`** | **50.0** | **50.0** | **50.0** | **uniform** — see A1.2 |

`390 × 23 = 8,970`, `1,560 × 46 = 71,760`, `6,240 × 92 = 574,080` — the registered counts
exactly.

### A1.2 THE REASONING, WHICH IS THE ONLY THING THAT MAKES A POST-FREEZE CHOICE ACCEPTABLE

**`s0` HALVES because a Roache triple is meaningless otherwise.** The triple measures the
**observed order of a discretisation**, and that is only meaningful if **every length scale
refines together at the same ratio**. Hold `s0` fixed while the cell count rises 8×: the
near-wall spacing does not refine at all, the near-wall discretisation error does not shrink
with `r`, and the extracted order is contaminated by a term that is not converging.
`MESH_STANDARD.md` §9.2's similarity clause exists to prevent exactly that. Halving `s0` at
`r = 2` makes it refine at the same rate as the linear dimension, which **is** the
definition of a similar family.

**`marchDist` is UNIFORM for the opposite reason: it is a DOMAIN EXTENT, not a resolution.**
Domain size must be **identical** across levels or the three meshes are solving **three
different problems**. A far-field boundary that moves with refinement changes the physics,
not the discretisation. 50.0 satisfies P6's "≥ 50" on every level.

**CONSEQUENCE, REGISTERED AS A PREDICTION AND NOT A DEFECT: this is a WALL-FUNCTION family
and `y⁺` will be in the TENS, not of order 1.** §3 already registers
`nutUSpaldingWallFunction` precisely because it is continuous across the whole `y⁺` range,
so the discrete operator cannot change part-way along the triple. **This is the trade this
route was chosen to make** — the ~61.5° wall-function family was preferred over the
wall-resolved 88.889° one exactly to buy mesh admissibility with `y⁺`. **A `y⁺` in the tens
is the trade working, not the trade failing.**

### A1.3 🔴 THE L3 CONSEQUENCE, REGISTERED **BEFORE** `checkMesh` ANSWERS

**Written now, while the answer is unknown, so that it cannot later read as an excuse
constructed after a bad result.**

§5's P2 already names the near-61.5° expectation as "the prediction most likely to be
wrong". The sharpest reason is L3's surface: **the only volume mesh ever built on the
390-face surface — `A3-onera-m6-adjoint-vcoarse` — measured 135.318° max non-orthogonality
and skewness 55.378. Broken.** That build used `N = 65` and stock `s0`, against L3's
`N = 24` and `s0 = 4.0e-04`, so it is **not** the same build — but it **is** the same
surface, and this registration does not pretend that difference is reassurance.

> **IF L3 IS INADMISSIBLE, THE GRID-CONVERGENCE GATE (Gate G) IS `NOT A RESULT` UNDER
> RULE 5. IT IS NOT A `GATE FAIL`, AND IT IS NOT A `PASS` ON TWO LEVELS.**
> A Roache triple requires three levels. Two levels yield no observed order, no GCI, and
> therefore no band — and Gate P's band is the deliverable. Rule 5's single permitted
> direction (a gate may turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the
> reverse) covers this, but a reader arriving cold should not have to derive it.
>
> **A two-level result is not a smaller result. It is no result.**

`S3` builds **coarse-first** for this reason: L3 is the cheapest **and** the riskiest, so
the ladder learns early and spends nothing discovering it.

### A1.4 COST — `S3` ATTEMPT 1 FAILED AND ITS SPEND IS NAMED AS WASTE

Attempt 1 (`verification/runs/RUNG1_M6_R2_runs.ATTEMPT1_PRESERVED_docker_rc127/`, moved
aside and **not deleted**) invoked the pyHyp container as
`bash -lc 'python3 genWingMesh.py'` with the volume at `/w` and no user flag, and returned
**`rc=127`, `python3: command not found`, on all three levels**: the image ships DAFoam's
interpreter as `python` behind an environment script that must be sourced first. The
working recipe is `cases/RUNG1_M6/run_r1m0.sh:190-192` — `-u 1002:1002`, mount at
`/home/dafoamuser/mount`, `source loadDAFoam.sh` before `python` — and is now copied in
shape rather than reinvented.

**Attempt 1 spend: 0.9802 core-min, ALL OF IT WASTE, named separately and never absorbed
into the actual/predicted ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). No level was built;
`levels_built: []`, and its family proof correctly reads **`NOT A RESULT` — "an unbuilt
level is NOT A RESULT, never an absent difference."**

**This waste is charged against `S3`'s registered 6.0 core-min cap, not excused from it.**
An overrun stops the run; it does not get a new budget (rule 12).
