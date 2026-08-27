# M1 — TWO-ARM MULTI-MODEL SWEEP: `kOmegaSST` (null) vs `kOmega`, 39 CASES, 78 RUNS

**FROZEN** by the closure supervisor on 2026-08-27 in a commit of its own, with
the sha256 of this document and all four instruments in that commit message.
`SUPERVISION_CHARTER.md` §3 check 4 was performed personally. Standing rule 2 now
applies in full: **the gates, thresholds, cap and label below are closed.**

# M1 — MULTI-MODEL SOLVE SWEEP ON THE CLOSURE CHALLENGE BENCHMARK MESHES
## PRE-REGISTRATION — 2 arms x 39 cases = 78 runs

**Drafted 2026-08-27 by a closure drafting lane on the closure supervisor's
dispatch. NOT FROZEN. NOT COMMITTED. NOT ENQUEUED. ZERO COMPUTE: no solver,
no `blockMesh`, no staging, no queue entry was produced by the lane that wrote
this file, and the run root `/home/ubuntu/closure-data/multimodel_sweep/` was
verified ABSENT at drafting time — 0.000 core-minutes exist in the tree.**

**The freeze is the supervisor's, personally.** `SUPERVISION_CHARTER.md` §3
check 4 may not be delegated, and this lane did not perform it and does not
claim it. Until the supervisor commits this file and writes the resulting
40-character sha into the queue entries, every entry in `QUEUE_ENTRIES_DRAFT/`
carries the literal string `PENDING_SUPERVISOR_FREEZE` in `prereg_commit` and
therefore **cannot pass `queue_entry_check.py` check 1 (SCHEMA) or check 2
(COMMIT-EXISTS)**. Nothing here can launch by accident.

**This registration is written under Sanaa's FREEZE-AHEAD >= 3 directive**
(2026-08-27T16:54Z, `etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md`
§2: *"every team keeps at least three frozen, queue-ready registrations at all
times. A starved queue is a planning defect."*). It is one of three closure owes.

**Scope ruled, not reopened.** The feasibility measurement is
`cases/RANS_LES_closure_models/_common/MULTIMODEL_SWEEP_FEASIBILITY_DRAFT.md`
(849 lines, at HEAD) and the supervisor's rulings are docket **D536**. This
document implements those rulings. Where this lane disagreed with a ruling it
says so in §14 and implements the ruling anyway.

---

## 1. THE QUESTION

> **On 39 benchmark flows with identical meshes, identical numerics, identical
> forcing, identical boundary conditions and an identical iteration budget, how
> far apart do two linear eddy-viscosity closures — `kOmegaSST` and `kOmega` —
> put the velocity field; and does the harness that produces that difference
> reproduce the shipped `kOmegaSST` answer when handed the `kOmegaSST` model?**

The second clause is not a formality. It is the whole reason the sweep has two
arms rather than one: **a uniform difference across 39 cases and a staging bug
are indistinguishable without a null arm that has to land on a known answer.**

**What this sweep is FOR:** it produces the per-cell multi-model input that
space-dependent model aggregation (de Zordo-Banliat, Dergham, Merle & Cinnella
2023, arXiv:2301.09013v1; `_common/FEASIBILITY.md:77`) requires and the lab does
not have. **It is not, and is not registered as, a validation** — see §11.

---

## 2. ARMS, CASES, AND THE EXCLUSIONS

### 2.1 Two arms. No third.

| arm id | `RASModel` | role |
|---|---|---|
| `kOmegaSST_null` | `kOmegaSST` | **the sweep's planted control.** Re-solves the shipped model in the identical staged harness and must land on each case's shipped converged field (gate G2). It is not padding and it is not an arm of the comparison; it is the instrument's calibration. |
| `kOmega` | `kOmega` | the substitute closure. Requires **no new `0/` field, no new wall boundary condition, no new `fvSolution` solver block and no new `fvSchemes` entry** — it is a `constant/turbulenceProperties` one-line change on all 39 cases. |

Both arms solve exactly `U`, `p`, `k`, `omega` and compute `nut`. **That
identity of the solved-field set is what makes a single convergence criterion
model-uniform** (§4) and it is the property the three cut arms did not have.

**`SpalartAllmaras`, `kEpsilon` and `LaunderSharmaKE` are CUT from M1** and are
a separate registration, per D536:

* **`SpalartAllmaras`** — every case ships `0/nut` `internalField uniform 0`;
  `nut = nuTilda*fv1(chi)` is monotone so the inversion is unique, but it
  inverts to **zero**, and `nuTilda = 0` is a **fixed point** of the SA
  transport equation. The arm would terminate cleanly, write fields, satisfy the
  strict completion rule and mean nothing — standing rule 3's failure shape
  arriving through the **initial condition** rather than through a reader. The
  alternatives are a warm start from the SST answer (which destroys the arm's
  independence) or a textbook `nuTilda = 3*nu` (an invented IC). Neither belongs
  in a sweep whose null arm is its only control.
* **`kEpsilon` / `LaunderSharmaKE`** — `epsilon = Cmu*k*omega` is derivable, but
  the **epsilon wall boundary condition is not** for the 11 cases that ship no
  `epsilon`, and `LaunderSharmaKE`'s recommended wall treatment was not
  established from source. An undetermined BC inside an arm is an unregistered
  modelling choice.

### 2.2 One case excluded: `NASA_2DWMH`

**`NASA_2DWMH` is excluded on two independent blockers**, either of which is
sufficient:

1. Its `constant/turbulenceProperties` names **`AugmentedkOmegaSST`**, which
   does not exist in OpenFOAM v2606 and is supplied by
   `libfrozenIncompressibleTurbulenceModels.so` — **absent from this box**. Its
   shipped configuration cannot be reproduced here at all, so its null arm has
   no reference and the sweep's only control does not exist for it.
2. It is the **one case of 40** whose `0/nut` reads `internalField uniform $nut;`
   — an **unexpanded dictionary variable**, not a value. The other 39 read
   `uniform 0`.

**Both blockers were re-derived from disk by this lane in the enumeration that
produced the table in §2.3**, and the second is the control that fired: 39 of 40
`uniform 0`, one `uniform $nut`. `stage_m1.py` carries this as guard **R4** and
**refuses any case whose `0/nut` internalField is not `uniform 0`**, so the
exclusion is enforced by an instrument and not by a list somebody has to
remember to keep correct.

### 2.3 The 39 cases

Cells are read from the `note` header of each case's own
`constant/polyMesh/owner`; `stage_m1.py` re-reads the count from the **staged**
`owner` and corroborates it against the integer length of the staged `points`
file (guard R15), so no number in the manifest is inherited from this table.

`ref` is the shipped converged time directory used as the null arm's reference
field in gate G2. `caseDef` marks the cases whose `system/fvOptions` does
`#include "../caseDef"` (§5.5). `libs` marks the cases whose
`system/controlDict` carries the `libs ( "libfrozenIncompressibleTurbulence
Models.so" );` line, which is **left in place** (§5.6).

| # | case_id | family | source path (rel. to benchmark `data/`) | cells | shipped endTime | ref | caseDef | libs | est core-min/run | cap core-min/run |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `CBFS` | CBFS | `CBFS` | 21,000 | 30000 | `30000` | - | YES | 23.100 | 33.684 |
| 2 | `AR_10_Ret_180` | DUCT | `DUCT/AR_10_Ret_180` | 22,090 | 500000 | `5125` | YES | YES | 24.299 | 35.432 |
| 3 | `AR_14_Ret_180` | DUCT | `DUCT/AR_14_Ret_180` | 31,819 | 500000 | `7009` | YES | YES | 35.001 | 51.038 |
| 4 | `AR_1_Ret_180` | DUCT | `DUCT/AR_1_Ret_180` | 2,209 | 500000 | `334` | YES | YES | 2.430 | 3.543 |
| 5 | `AR_1_Ret_360` | DUCT | `DUCT/AR_1_Ret_360` | 3,025 | 500000 | `405` | YES | YES | 3.328 | 4.852 |
| 6 | `AR_3_Ret_180` | DUCT | `DUCT/AR_3_Ret_180` | 6,627 | 500000 | `1109` | YES | YES | 7.290 | 10.630 |
| 7 | `AR_3_Ret_360` | DUCT | `DUCT/AR_3_Ret_360` | 8,748 | 500000 | `1540` | YES | YES | 9.623 | 14.032 |
| 8 | `AR_5_Ret_180` | DUCT | `DUCT/AR_5_Ret_180` | 11,045 | 500000 | `2428` | YES | YES | 12.150 | 17.716 |
| 9 | `AR_7_Ret_180` | DUCT | `DUCT/AR_7_Ret_180` | 15,463 | 500000 | `3636` | YES | YES | 17.009 | 24.803 |
| 10 | `PH_Breuer` | PH_Breuer | `PH_Breuer` | 15,600 | 10000 | `10000` | - | YES | 17.160 | 25.022 |
| 11 | `alpha_05_10071_2024` | hill | `Parm_PH_29/alpha_05/alpha_05_10071_2024` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 12 | `alpha_05_10071_3036` | hill | `Parm_PH_29/alpha_05/alpha_05_10071_3036` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 13 | `alpha_05_10071_4048` | hill | `Parm_PH_29/alpha_05/alpha_05_10071_4048` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 14 | `alpha_05_4071_2024` | hill | `Parm_PH_29/alpha_05/alpha_05_4071_2024` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 15 | `alpha_05_4071_3036` | hill | `Parm_PH_29/alpha_05/alpha_05_4071_3036` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 16 | `alpha_05_4071_4048` | hill | `Parm_PH_29/alpha_05/alpha_05_4071_4048` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 17 | `alpha_05_7071_2024` | hill | `Parm_PH_29/alpha_05/alpha_05_7071_2024` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 18 | `alpha_05_7071_3036` | hill | `Parm_PH_29/alpha_05/alpha_05_7071_3036` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 19 | `alpha_05_7071_4048` | hill | `Parm_PH_29/alpha_05/alpha_05_7071_4048` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 20 | `alpha_075` | hill | `Parm_PH_29/alpha_075/alpha_075` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 21 | `alpha_10_12000_2024` | hill | `Parm_PH_29/alpha_10/alpha_10_12000_2024` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 22 | `alpha_10_12000_3036` | hill | `Parm_PH_29/alpha_10/alpha_10_12000_3036` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 23 | `alpha_10_12000_4048` | hill | `Parm_PH_29/alpha_10/alpha_10_12000_4048` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 24 | `alpha_10_6000_2024` | hill | `Parm_PH_29/alpha_10/alpha_10_6000_2024` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 25 | `alpha_10_6000_3036` | hill | `Parm_PH_29/alpha_10/alpha_10_6000_3036` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 26 | `alpha_10_6000_4048` | hill | `Parm_PH_29/alpha_10/alpha_10_6000_4048` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 27 | `alpha_10_9000_2024` | hill | `Parm_PH_29/alpha_10/alpha_10_9000_2024` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 28 | `alpha_10_9000_3036` | hill | `Parm_PH_29/alpha_10/alpha_10_9000_3036` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 29 | `alpha_10_9000_4048` | hill | `Parm_PH_29/alpha_10/alpha_10_9000_4048` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 30 | `alpha_125` | hill | `Parm_PH_29/alpha_125/alpha_125` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 31 | `alpha_15_10929_2024` | hill | `Parm_PH_29/alpha_15/alpha_15_10929_2024` | 15,600 | 20000 | `20000` | - | YES | 17.160 | 25.022 |
| 32 | `alpha_15_10929_3036` | hill | `Parm_PH_29/alpha_15/alpha_15_10929_3036` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 33 | `alpha_15_10929_4048` | hill | `Parm_PH_29/alpha_15/alpha_15_10929_4048` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 34 | `alpha_15_13929_2024` | hill | `Parm_PH_29/alpha_15/alpha_15_13929_2024` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 35 | `alpha_15_13929_3036` | hill | `Parm_PH_29/alpha_15/alpha_15_13929_3036` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 36 | `alpha_15_13929_4048` | hill | `Parm_PH_29/alpha_15/alpha_15_13929_4048` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 37 | `alpha_15_7929_2024` | hill | `Parm_PH_29/alpha_15/alpha_15_7929_2024` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 38 | `alpha_15_7929_3036` | hill | `Parm_PH_29/alpha_15/alpha_15_7929_3036` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| 39 | `alpha_15_7929_4048` | hill | `Parm_PH_29/alpha_15/alpha_15_7929_4048` | 15,600 | 20000 | `20000` | - | - | 17.160 | 25.022 |
| | **39 cases** | | | **590,026** | | | **8** | **11** | **649.0** | **946.4** |

**EXCLUDED, and why the exclusion is a measurement rather than a decision:**

| case_id | `RASModel` | `0/nut` internalField | blocker |
|---|---|---|---|
| `NASA_2DWMH` | `AugmentedkOmegaSST` | `uniform $nut` | model not in v2606 (absent library) AND unexpanded dictionary variable |

**Totals re-derived from disk in the same invocation that wrote this table: 39 cases, 590,026 cells, 1 excluded, 40 enumerated.**
Per arm at the 20,000-iteration cap and the 3.30 us point rate: **649.0 core-min**. Two arms: **1298.1 core-min = 21.63 core-h**.

---

## 3. THE UNIFORM ITERATION CAP: **20,000**, AND THE MEASUREMENT THAT FIXES IT

**Registered: `endTime 20000`, `deltaT 1`, `startFrom startTime`, `startTime 0`,
`writeInterval 20000`, on all 78 runs, with NO exception and NO per-family
variation.**

This single line is the largest cost lever in the sweep. At the **shipped**
`endTime` values the same 39 cases cost **~277 core-h across two arms with 84 %
of it on the eight ducts**, because those eight dictionaries say
`endTime 500000` against 20,000 elsewhere. At a uniform 20,000 the sweep is
**21.63 core-h**. That is a factor of 12.8 from one dictionary line.

### 3.1 The evidence, from this box's own logs

All rates and residual histories below are read from
`/home/ubuntu/closure-data/aposteriori/kaandorp/*/log.run` — `simpleFoam`,
OpenFOAM v2606, `nProcs : 1`, on **these exact meshes**. Every run named is a
run that already happened; **this lane started nothing.**

**Cold starts (`Create mesh for time = 0`) are the only rows that bound a cold
sweep**, and there are three, one per archetype:

| log | case | archetype | model | iterations | outcome |
|---|---|---|---|---|---|
| `AR_1_Ret_360__FROZENEXTRACT/log.run` | duct, 3,025 cells | 3-D streamwise-periodic duct | `kOmegaSSTFrozen` | **405** | `SIMPLE solution converged in 405 iterations` under the shipped `k 5e-6; omega 1e-10` |
| `CBFS13700__FROZENEXTRACT/log.run` | CBFS, 21,000 cells | inlet/outlet separated | `kOmegaSSTFrozen` | 30,000 | never met `p 1e-15`; **residuals flat from ~5,000 to 30,000** |
| `PHLL10595__FROZENEXTRACT/log.run` | periodic hill, 15,600 cells | streamwise-cyclic hill | `kOmegaSSTFrozen` | 10,000 | never met `p 1e-15`; still descending at 10,000 |

**Measured initial-residual histories (first solve of each outer iteration):**

| iteration | CBFS `p` | CBFS `Ux` | CBFS `k` | CBFS `omega` | hill `p` | hill `Ux` | hill `k` | hill `omega` |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 1.00 | 1.00 | 1.6e-1 | 1 | 1.00 | 1.00 | 1.7e-1 |
| 1,000 | 8.8e-6 | 2.0e-5 | 1.9e-5 | 1.9e-6 | 3.8e-3 | 4.9e-4 | 1.2e-3 | 2.2e-5 |
| 5,000 | 1.2e-6 | 2.1e-9 | 1.1e-6 | 8.8e-9 | 3.2e-6 | 1.3e-6 | 3.6e-6 | 4.3e-8 |
| 10,000 | 1.2e-6 | 1.9e-9 | 8.7e-7 | 8.5e-9 | 9.7e-9 | 2.9e-9 | 7.3e-9 | 9.7e-10 |
| 20,000 | 1.5e-6 | 2.4e-9 | 1.2e-6 | 1.0e-8 | — | — | — | — |
| 30,000 | 1.1e-6 | 1.9e-9 | 8.2e-7 | 9.1e-9 | — | — | — | — |

**CBFS is at its iterative plateau by ~5,000 iterations. The 25,000 further
iterations its shipped `endTime 30000` buys change every residual by less than a
factor of 1.5.** The periodic hill reaches 1e-8/1e-9 on all four channels by
10,000. The duct converged cold in 405.

### 3.2 Why 20,000 and not 10,000 or 5,000

| bound | value | source |
|---|---|---|
| slowest measured `kOmegaSST` convergence on any of the 39 | **7,009** iterations (`AR_14_Ret_180`, the shipped reference time directory, produced under `k 5e-6; omega 1e-10`) | §2.3 table, `ref` column |
| CBFS plateau onset | **~5,000** | §3.1 |
| hill residuals at 1e-8 | **10,000** | §3.1 |
| the hills' own shipped `endTime` | **20,000** | §2.3 |

**20,000 is 2.85x the slowest measured `kOmegaSST` convergence on any case in
the sweep, 4x the CBFS plateau onset, 2x the `PH_Breuer` shipped `endTime`, and
exactly equal to the 29 hills' shipped `endTime`.** That last equality is not
cosmetic: it makes the null arm's iteration count **identical** to the count
that produced 29 of the 39 reference fields gate G2 compares against.

**`kOmega`'s convergence behaviour on these meshes has never been measured on
this box.** 20,000 is chosen with that margin precisely because the second arm
is unmeasured; a row that still fails the criterion at 20,000 is reported as
**CAP-BOUND** (§4.3) and is not silently averaged into anything.

**The cap is a runaway guard, not a target** (`COMPUTE_BUDGET_CHARTER`). Under
`kOmegaSST` most rows are expected to be converged long before it and to keep
iterating at the plateau; that waste is bought deliberately, and §4.2 says why.

---

## 4. THE MODEL-UNIFORM CONVERGENCE CRITERION

### 4.1 The criterion

> **A run is CONVERGED at iteration `n` if there exists `n <= 20000` such that
> for every outer iteration `i` in `[n, 20000]`, the initial residual of `k`
> is `<= 5e-6` AND the initial residual of `omega` is `<= 5e-6`.**
> **Otherwise the run is CAP-BOUND.**

`n` is reported per row. The criterion is evaluated **post hoc by
`grade_m1.py` from `log.run`**, not by the solver — see §4.2, which is the part
of this section that is forced rather than chosen.

**Why `k` and `omega`, and why NOT `p` and NOT `U`.** This is a measurement, not
a preference. On the eight duct cases, under a linear eddy-viscosity model, the
normalised initial residuals of `p`, `Uy` and `Uz` **never decrease at all**:

| `AR_1_Ret_360__NULL` (`kOmegaSST`, 30,000 iterations from the shipped 405) | it 1 | it 5,000 | it 10,000 | it 20,000 | it 30,000 |
|---|---|---|---|---|---|
| `p` | 0.201 | 0.186 | 0.205 | 0.162 | **0.144** |
| `Uy` | 0.306 | 0.243 | 0.405 | 0.533 | **0.289** |
| `Uz` | 0.414 | 0.244 | 0.203 | 0.413 | **0.190** |
| `Ux` | 1.6e-3 | 1.3e-13 | 1.2e-15 | 7.4e-16 | **7.3e-16** |
| `k` | 3.6e-5 | 9.58e-9 | 9.58e-9 | 9.58e-9 | **9.58e-9** |
| `omega` | 1.9e-8 | 9.1e-16 | 9.8e-16 | 9.8e-16 | **9.8e-16** |

`AR_3_Ret_360__NULL` behaves identically (`p` 0.26–0.45 throughout, `Uy`/`Uz`
0.28–0.68 throughout, `k` 9.9e-9, `omega` 1.0e-15 at 30,000).

**That is not non-convergence; it is a degenerate residual normalisation.** A
linear eddy-viscosity model produces essentially **no secondary flow** in a
square or rectangular duct — the very failure `_common/BASELINES.md` §5 records
as the dominant duct error. With no in-plane motion, the in-plane pressure and
velocity variation is at machine noise, OpenFOAM normalises the residual by that
noise, and the ratio is O(0.1–0.7) forever. **Both M1 arms are linear
eddy-viscosity models, so both are in exactly this regime on all eight ducts.**

The shipped duct `residualControl { k 5e-6; omega 1e-10; }` names `k` and
`omega` and not `p` — whoever built the benchmark had already found this.

**Why the thresholds are `5e-6` and not tighter.** The tightest threshold
reachable on *all three* archetypes is set by CBFS, whose `k` residual
**plateaus at 8.2e-7** and never goes lower in 30,000 iterations. A `k 1e-7`
criterion would leave CBFS permanently CAP-BOUND; a `k 1e-8` criterion sits
**inside the measured duct plateau** (9.58e-9) and would flip on noise. `5e-6`
sits **6x above the CBFS `k` floor**, **520x above the duct `k` floor** and
**550x above the CBFS `omega` floor (9.1e-9)** — far enough from every measured
floor that meeting it is a statement about the solution and not about the
plateau. It is also, unchanged, the ducts' own shipped `k` threshold.

Measured first crossings of `5e-6` under `kOmegaSST`: duct ~1,400; CBFS
~2,000–3,000 (`k`), ~1,000 (`omega`); hill ~4,700 (`k`), ~2,000 (`omega`).
**All three archetypes cross by ~5,000 iterations, i.e. at 25 % of the cap.**

### 4.2 `residualControl` IS REMOVED FROM ALL 78 RUNS — and this is forced by standing rule 4, not chosen

Every staged `system/fvSolution` has its `SIMPLE { residualControl { ... } }`
sub-dictionary **emptied** (`residualControl { }`). Nothing stops the solver
early; every run executes exactly 20,000 outer iterations.

**The reason is standing rule 4.** The strict completion rule requires **`last
time == endTime`** and **`ExecutionTime` count == `endTime`**. A run that exits
early on `residualControl` violates *both* clauses and would be refused by the
lab's own completion rule on all 78 rows. There is no version of a
solver-enforced early stop that satisfies rule 4, and this lane is not entitled
to amend rule 4. So the criterion moves to the comparator, where it decides a
**row class** instead of a stop.

Four properties follow, and they are why this is the better design anyway:

1. **`ExecutionTime` count == 20000 exactly on every complete row**, so rule 4's
   fifth clause becomes an exact integer check rather than an inequality.
2. **The null arm's iteration count is identical to the 29 hills' reference
   fields'** (both 20,000), removing an iteration-count confound from gate G2 on
   29 of 39 cases.
3. **Every arm-to-arm difference in §6 G3 is taken between two fields computed
   with the same number of outer iterations**, so the spread cannot be an
   artefact of one arm having been allowed to stop sooner.
4. **A criterion in a dictionary can silently change meaning between arms; a
   criterion in the comparator cannot.** The shipped duct criterion names
   `omega`; three of the four originally-proposed arms do not solve `omega`.
   That trap is retired here for good.

**The cost of removing it** is the plateau iterations we pay for and do not use:
on the eight ducts, ~18,600 of 20,000 iterations per run, ~103 core-min per arm,
**~206 core-min of the 1,298.1 total (16 %)**. That waste is **named here, in
advance, and it is not absorbed into the estimate** (`COMPUTE_BUDGET_CHARTER`
§6). It buys clauses 1–4 and compliance with rule 4.

### 4.3 What happens to a row that hits the cap without meeting the criterion

**A CAP-BOUND row is a distinct row class and is printed as such beside every
number it contributes to.** Specifically, and `grade_m1.py` enforces all four:

1. Every per-case line carries a literal `CONVERGED@<n>` or `CAP-BOUND` tag.
2. **No aggregate is reported once.** Every aggregate (counts, medians, maxima,
   the G3 census) is printed **twice** — over converged rows only, and over all
   rows — with the two never merged and never averaged into each other.
3. A CAP-BOUND row's `min(k)` and `min(omega)` residuals reached, and the
   iteration at which each was reached, are printed beside it, so a row that
   missed by a factor of two is distinguishable from one that never descended.
4. **A gate is never PASSed on the strength of a CAP-BOUND row.** If a gate's
   pass set contains a CAP-BOUND row, the gate result is printed with the count
   of such rows and the gate is recomputed excluding them; if the two verdicts
   differ, the verdict reported is the **more conservative** one and both are
   shown.

`CAP-BOUND` is a row class, never a verdict. It is not `GATE FAIL`, it is not
`NOT A RESULT`, and it is not a synonym for either.

---

## 5. STAGING DESIGN

Run root, outside the repository (run outputs never live beside the prose
describing them, and this is far too large for git):

    /home/ubuntu/closure-data/multimodel_sweep/
      kOmegaSST_null/<CASE_ID>/     0.orig/  constant/  system/  [caseDef]
      kOmega/<CASE_ID>/             0.orig/  constant/  system/  [caseDef]
      STAGING_MANIFEST_M1.json

**Verified ABSENT at drafting time.** 78 case directories, `<CASE_ID>` exactly
the basenames in §2.3.

### 5.1 `0.orig/` and NO `0/` — the age-guard constraint

`QUEUE_ENTRY_STANDARD.md` §4 check 4 (`AGE-GUARD`) refuses a `cwd` that already
contains `0/` **or any numeric time directory**, and **`0` is itself a numeric
time directory**. The lab's prior art is
`verification/runs/T-family/T5_runs/run_one_t5.sh:128-130`, which arms `0/` from
`0.orig/` as the launcher's first act and **refuses when `0.orig` is missing**.
M1 follows it exactly.

`0.orig/` holds **exactly five files**: `U p k omega nut`, copied byte-for-byte
from the source `0/`. Everything else in the source `0/` is dropped: the truth
fields `U_LES k_LES p_LES tauij_LES`, the geometry fields `C Cx Cy Cz`, the
`uniform/` sub-directory (it carries time-index state and would let a staged
case believe it has a history), `interpolatedFields/` (CBFS), `wallShearStress`
(hills) and `epsilon` (hills — neither arm solves it).

**No numeric time directory is copied.** All 39 case roots already hold one
(`30000`, `20000`, `10000`, `334`…`7009`) and **all 39 `controlDict`s say
`startFrom latestTime`**. A naive copy would restart from the converged answer,
write nothing, and produce a null arm that reproduces its reference perfectly
because it never moved. The staged `controlDict` therefore says
`startFrom startTime; startTime 0;`.

### 5.2 The `controlDict` patch — exactly eight keys, and nothing else

| key | staged value | why |
|---|---|---|
| `application` | `simpleFoam` | **absent** from CBFS, `PH_Breuer` and all 8 duct `controlDict`s; present on the 29 hills as `application simpleFoam;//` |
| `startFrom` | `startTime` | §5.1 |
| `startTime` | `0` | §5.1; **absent entirely** from the 8 duct `controlDict`s |
| `stopAt` | `endTime` | shipped as `endTime;//writeNow` on hills and `PH_Breuer` |
| `endTime` | `20000` | §3 |
| `deltaT` | `1` | shipped value everywhere; iteration == time |
| `writeControl` | `timeStep` | shipped value everywhere |
| `writeInterval` | `20000` | one write, at `endTime`. Shipped as `$endTime` on the ducts (which would expand to 500,000) and `4000` on the hills |
| `purgeWrite` | `0` | shipped value everywhere; restated so the `endTime` directory cannot be purged |
| `writeFormat` / `writePrecision` | `ascii` / `15` | shipped as precision **6** on the ducts and **15** elsewhere. Unified so the write-precision floor is ~1e-15 on our side of every G2 comparison. *The reference side of the eight duct comparisons is still precision 6, so the G2 floor on those eight is ~1e-6 — six orders below the G2 threshold.* |
| `functions` | **emptied to `functions { }`** | see below |

**Everything else in `controlDict` is left byte-identical, including the `libs`
line (§5.6) and `runTimeModifiable`.**

**The `functions` block is emptied.** All 39 invoke sampling function objects by
`#includeFunc` (`residuals`, `convergenceProbes`, `singleGraph_x0..x8`,
`faceValues`, `wallValues`, `bottomValues`, `singleGraphDiag`), and the set
differs per family. Emptying it (a) removes every dependence on the dropped
truth fields and on per-family sampling dictionaries, (b) makes all 78 runs
compute exactly the same thing, and (c) removes a per-family cost difference
from the arm comparison. **It does NOT touch `fvOptions`**, which is a
different mechanism: the `meanVelocityForce` that drives the 8 ducts and the 29
hills survives, and `stage_m1.py` guard **R10** refuses if a case whose source
had `system/fvOptions` reaches the staged tree without it.

Residuals are read from `log.run`, not from the `residuals` function object, so
nothing needed is lost.

### 5.3 The `fvSolution` patch — exactly one edit

`SIMPLE { residualControl { ... } }` is **emptied** (§4.2). Guard **R12**
re-reads the staged file and refuses if the block is non-empty.

**Nothing else in `fvSolution` is touched.** Linear-solver choices (GAMG vs PCG
vs PBiCG/PBiCGStab), tolerances, `relTol`, `nNonOrthogonalCorrectors`,
`pRefCell`/`pRefPoint` and all `relaxationFactors` differ per family and are
**left exactly as shipped**. They are identical between the two arms of a given
case, so they cancel in the arm-to-arm comparison, and leaving them preserves
the null arm's comparability with the shipped reference field. This is Sanaa
§3's *one change per run* applied to the dictionary: the only physics change
between arms is `RASModel`, and the only harness change from shipped is the
iteration budget.

The 29 hills' inert `SIMPLE { convergence 1e-8; }` is **left in place**.
`convergence` is **not a v2606 `simpleControl` keyword** and is silently
ignored, which is why the hills ship with no working criterion at all; deleting
it would be a change with no effect, and this registration prefers a recorded
inert key to an unrecorded edit. Its inertness is stated here so no later reader
mistakes it for a criterion.

`fvSchemes` is **not touched at all**. Both arms solve the same equations, so
the missing `div(phi,omega)` on the 29 hills (which falls to
`divSchemes default Gauss linear`) is the shipped condition and is identical
across arms.

### 5.4 `constant/{C,Cx,Cy,Cz,V}` — DROPPED, uniformly, on all 78

The eight ducts ship `constant/C`, `Cx`, `Cy`, `Cz` and `V`; the other 31 cases
ship none. **The registered policy is to DROP them on all 78**, and the argument
is about failure modes rather than tidiness:

* Nothing `simpleFoam` runs reads them. They are `writeCellCentres` /
  `writeCellVolumes` output, derived from `polyMesh` and reconstructible.
* **Dropping fails loudly; copying fails silently.** If some staged dictionary
  did need one, the absent file raises a `FatalError` at read time, the run
  exits non-zero, and the completion rule refuses the row. A *stale* copied
  field inconsistent with anything would be read without complaint.
* Uniformity is the actual requirement: an inconsistency between the eight
  ducts and the other 31 becomes a phantom family-to-family difference that no
  gate could attribute.

Guard **R14** re-reads the staged `constant/` and refuses if any of the five
names is present.

### 5.5 `caseDef` and `fieldDef` — copied, and every `#include` guarded

Two files sit at the case root and are staged when present:

* **`caseDef`** — the eight ducts. `system/fvOptions` does
  `#include "../caseDef"`, which resolves relative to `system/`, i.e. to the case
  root, and supplies `h`, `AR`, `Re_b`, `Re_tau` and `nu`. **It is also
  `#include`d by `0/U` itself** — see §5.9, which is why this file is load-bearing
  for the *initial fields* and not only for the forcing.
* **`fieldDef`** — CBFS, `PH_Breuer` and the eight ducts. It defines
  `residualFields`, `convergenceFields`, `faceValuesFields` and
  `singleGraphFields`, which are consumed by the sampling dictionaries in
  `system/`. Those dictionaries are never read once the `functions` block is
  emptied (§5.2), so `fieldDef` is not strictly required — **it is staged anyway**,
  because a one-line file removes a whole class of read-time failure and costs
  nothing. The 29 hills have neither file and need neither.

**`dynamicCode/` is NOT copied.** The eight duct source trees ship one (left by
whoever generated the benchmark). `#calc` regenerates it at read time, and a
stale compiled object matched against a different build is a silent hazard where
a regenerated one is not. Evidence it regenerates on this box: the lab's own
duct re-runs under `/home/ubuntu/closure-data/aposteriori/kaandorp/` each carry
their own `dynamicCode/` and ran to completion.

**Guard R9 is a general include-resolution guard, not a `caseDef` special case.**
It refuses if (a) the source has `caseDef` or `fieldDef` and the staged tree does
not, or (b) **any** `#include "<relpath>"` in **any** staged `system/` or
`0.orig/` file fails to resolve to a file that is in the staged tree. The second
clause is the one that matters: it catches a case that acquires an include
without the file, and it covers the initial fields as well as the dictionaries.

### 5.6 The `libs` line — LEFT IN PLACE, never deleted to tidy a case (rule 14)

Eleven of the 39 carry `libs ( "libfrozenIncompressibleTurbulenceModels.so" );`
in `system/controlDict`: CBFS, `PH_Breuer`, all eight ducts, and **exactly one
hill, `alpha_15_10929_2024`, whose 28 siblings do not**. The library is absent
from this box. In v2606 that is a **warning, not a fatal error**:
`src/OpenFOAM/db/dynamicLibrary/dlLibraryTable/dlLibraryTable.C:185-190` takes
the `!ptr` branch, emits *"Could not load"* through `WarningInFunction`, and
returns a null pointer without raising `FatalError`.

**Standing rule 14: `libs` entries are inserted with an assert, never replaced —
and never quietly deleted.** `stage_m1.py` does not touch the line, and guard
**R8** re-reads the staged `controlDict` and refuses unless the multiset of its
`libs (...)` lines is **identical to the source's**.

**A bulk script that assumes the 29 hills are byte-identical in `system/` is
wrong on `alpha_15_10929_2024/system/controlDict:18`.** `stage_m1.py` is
per-case and file-driven, never templated from one exemplar, and the manifest
records a sha256 of every source and staged file so this heterogeneity stays
visible instead of being averaged away.

### 5.7 The staging manifest reads back off disk what it claims

`STAGING_MANIFEST_M1.json` records, per staged `(arm, case)`:

* source path, destination path, and a **sha256 of every staged file**;
* **`cells_from_owner_note`** — read from the **staged** `constant/polyMesh/owner`
  header, not from the source and not from §2.3;
* **`cells_from_points_length`** — the integer count at the head of the **staged**
  `points` file. Guard **R15 refuses if the two disagree**, so the cell count in
  the manifest has been corroborated by a second independent read of the staged
  tree;
* `zero_dir_absent: true` and `numeric_time_dirs: []`, **asserted by listing the
  staged directory**, not by trusting that the copy skipped them (guard R6);
* `orig_fields` — the actual listing of `0.orig/`, refused unless it is exactly
  `[U, p, k, omega, nut]` (guard R7);
* `rasmodel_readback` — `RASModel` re-parsed from the **staged**
  `constant/turbulenceProperties`, refused unless it equals the arm (guard R13);
* `controldict_readback` — the eight patched keys re-parsed from the staged file
  (guard R11);
* `libs_lines_src` / `libs_lines_dst` (guard R8), `caseDef` and `fvOptions`
  presence (guards R9, R10);
* a self-sha256 of `stage_m1.py` itself, and the UTC timestamp.

**A staging script that reports success without having read those things back
off disk is the shape standing rule 3 refuses**, so `stage_m1.py` also carries
its own planted control: it plants a known perturbation into a **copy on disk**
of a staged `0.orig/U`, re-reads it through the same field reader the manifest
uses, and **refuses (`sys.exit(2)`) if the reader cannot see it** (guard R16).

### 5.9 SYMBOLIC INITIAL FIELDS — the eight ducts, found while building the tools

**The eight duct cases do NOT ship numeric initial fields for `U`, `k` and
`omega`.** They ship dictionary expressions:

| file | `internalField` | where the symbol is defined |
|---|---|---|
| `0/U` | `uniform $Uinlet;` | in `0/U` itself: `Uinlet ($U_b 0 0);` above it, with `U_b #calc "$Re_b*$nu/$h";` above that, resolved through `#include "../caseDef"` **inside the field file** |
| `0/k` | `uniform $kInlet;` | `kInlet 0.02;`, literal, in `0/k` itself — self-contained |
| `0/omega` | `uniform $omegaInlet;` | `omegaInlet 10.0;`, literal, in `0/omega` itself — self-contained |
| `0/p`, `0/nut` | `uniform 0;` | numeric |

CBFS, `PH_Breuer` and the 29 hills ship numeric values throughout
(`U uniform (0.72 0 0)` etc.).

**This was found by running the staging tool's own rule-3 planted control against
the real source tree in dry-run mode: the control REFUSED on all sixteen duct
entries** with *"no numeric token after the internalField header"*, because a
reader cannot plant into `$Uinlet`. That refusal is the instrument working, and
it is recorded here rather than worked around. Four consequences, all registered:

1. **`caseDef` is load-bearing for the FIELDS, not only for `fvOptions`.**
   Staging `0.orig` without it produces eight cases that fail at read time on
   `0/U`. Guard R9's include-resolution clause covers exactly this.
2. **`0.orig/*` is copied byte-for-byte and is never "cleaned".** An attempt to
   normalise these files into numeric values would be an unregistered change to
   an initial condition.
3. **The rule-3 planted control uses `0.orig/nut` as its primary carrier**, which
   is `uniform 0` on all 39 cases — so the control is literally *plant a non-zero
   into a field of zeros and prove the reader sees it*. `0.orig/U` is used
   **additionally** on the 31 cases where it is numeric. The staging manifest
   records, per case, exactly which fields were symbolic and which carried the
   plant. **If NO field can be read numerically, the tool refuses** rather than
   reporting a control it did not run.
4. **`#calc` compiles a small function at read time** into the case's own
   `dynamicCode/`. Each of the 16 duct runs does this in its own directory, so
   there is no shared-object contention, and it is the shipped condition.

**Relation to the `NASA_2DWMH` exclusion.** D536 records that case's second
blocker as `0/nut internalField uniform $nut` — an unexpanded dictionary
variable. That reading stands and is exact: it is about **`0/nut`**, and the 39
included cases all read `uniform 0` there. §5.9 is a *different* finding about a
*different* field, and it does not weaken the exclusion — but it does mean the
sentence "the other 39 are `uniform 0`" is true of `nut` and **not** of `U` on
the eight ducts. Said plainly so nobody later reads the narrower claim as the
wider one.

### 5.8 Staging is not compute and needs no queue entry

Staging is a file copy. It runs before any entry is written — an entry whose
`cwd` does not yet exist is refused at check 4 in any case. **`stage_m1.py`
writes nothing without an explicit `--execute` flag**; its default is a dry run
that prints the plan and touches nothing.


---

## 6. CONTROLS

Every control below is an instrument that **refuses** rather than degrades, and
every refusal is `raise` or `sys.exit(2)` — **never an `assert`**, because
`python3 -O` deletes assertions and a refusal that vanishes under an optimiser
flag is not a refusal (L-332). **Both `stage_m1.py --selftest` and
`grade_m1.py --selftest` are run under `python3 -O` and every refusal must still
fire.** Every guard ships its planted-failure proof: the guard is mutated to a
no-op and the control must flip (L-314).

### C1 — PLANTED ZERO, ON DISK (standing rule 3)

`grade_m1.py`, **before it computes any number**, copies a real staged
`20000/U` to a temporary directory, adds `PLANT = 1.234e-03` to the first
component of the first internal cell **in the file on disk**, re-reads the file
**through the same reader used for every graded number**, and computes the
relative L2 change between the planted and unplanted copies. **It refuses
(`sys.exit(2)`) if the reader does not see a change consistent with `PLANT`**,
with the message that its zeros mean nothing.

*An in-memory plant does not satisfy this and is not used.* The plant is written
to a file, closed, and re-opened.

`stage_m1.py` carries the same control (guard R16) on the staged `0.orig/nut` --
`uniform 0` on all 39 cases, so the control is literally *plant a non-zero into
a field of zeros and prove the reader sees it* -- and additionally on
`0.orig/U` wherever that field is numeric (31 of 39; see §5.9). **If no field
can be read numerically the tool refuses**, rather than reporting a control it
did not run.

### C2 — THE NULL ARM (the sweep's own planted control)

The `kOmegaSST_null` arm is not a result and is not an arm of the comparison.
It is the instrument's calibration: **the identical staged harness, handed the
model the case shipped with, must land on the answer the case shipped with.**
Gate G2 is its threshold. If G2 fails, **no arm-to-arm number from this sweep
is a result**, because a uniform difference and a staging bug are the same
observation.

### C3 — ARM APPLICATION, READ BACK FROM THE SOLVER'S OWN OUTPUT

For all 78 runs the comparator reads `RASModel` from **two independent places**:
the staged `constant/turbulenceProperties` on disk, and the model name
`simpleFoam` itself prints in `log.run` when it selects the RAS model. **It
refuses if the two disagree, or if either differs from the arm the entry
names.** This is what stops the failure mode where the sweep runs 78 times with
the same model and reports a spread of zero as a physical finding.

### C4 — STRICT COMPLETION AND THE AGE GUARD (standing rule 4)

A run is done only if **all** of it holds:

1. `rc = 0`;
2. an `End` line in `log.run`;
3. **last time == `endTime` == 20000**;
4. fields present at `20000`: `U`, `p`, `k`, `omega`, `nut`;
5. `ExecutionTime` line count == 20000;
6. **every field at `20000` NEWER than the case's own `0/U`** — the age guard.

**The registered age datum for this incompressible family is `0/U`**, the
analogue of the thermal family's `0/T`: it is the file `run_m1.sh` touches
**last** before the solver starts, so its mtime dates the run allowed to produce
the answer. This is a registration of the analogue, not a weakening of the rule.

`run_m1.sh` additionally **refuses to start** a case that already holds `0/` or
any numeric time directory, and refuses if `0.orig/` is missing.

**A run that fails any clause is not done, and `grade_m1.py` refuses rather than
degrading it.**

### C5 — L-342: PHYSICS-CRITICAL vs INFRASTRUCTURE FIELDS

The comparator labels every field it reads:

| class | fields | rule |
|---|---|---|
| **physics-critical** | `20000/{U,p,k,omega,nut}`, the `End` line, the last time directory, the `ExecutionTime` count, the `0/U` age datum, the residual history in `log.run` | absence or failure is a **physics** finding and the row is refused |
| **infrastructure** | the `STATUS` file and everything in it — the rc **record**, wall time, timestamps, `checkMesh_rc`, core-minutes | absence is **NOT MEASURED**, never a failure of the run |

Per Sanaa's desk ruling **R-RC** (2026-08-27T16:54Z §0, approved as written):
*"rc value is physics, rc record is infrastructure; absent record -> NOT MEASURED
only when the other four rule-4 conditions hold."* So: **if `STATUS` is missing
but clauses 2–6 of C4 all hold, the rc is reported `NOT MEASURED`, the row's
cost is reported `NOT MEASURED`, and the physics row STANDS.** A dead poller or
a lost ledger row cannot void an intact physics artefact.

The converse is also enforced: a `STATUS` that is present and says `rc != 0` is
a **physics** finding, because the rc *value* is physics.

### C6 — THE `0/nut` CONTROL THAT ALREADY FIRED

`stage_m1.py` guard **R4** refuses any case whose `0/nut` `internalField` is not
`uniform 0`. This is the control that produced the `NASA_2DWMH` exclusion (39 of
40 `uniform 0`, one `uniform $nut`), and it is shipped in the instrument so the
exclusion survives someone re-running staging without reading §2.2.

---

## 7. THE GATES

**Thresholds are fixed HERE, before staging has run and before any solver has
started.** `stage_m1.py` has never been executed. No gate below may be changed
after the first compute; a departure lands only as a dated addendum that cannot
alter a gate, threshold, cap or label (standing rule 2).

### G0 — COMPLETION / HARNESS GATE

> **All 78 runs satisfy the strict completion rule of §C4 including the age
> guard, at `endTime = 20000`, with `U p k omega nut` present.**

* **PASS**: 78 / 78.
* **GATE FAIL**: any row incomplete. The failing rows are named individually.
* A row failing G0 is **excluded from every other gate** and is printed in the
  exclusion list beside each gate it was excluded from — never dropped silently.

### G1 — ARM-APPLICATION CONTROL

> **For all 78 runs, `RASModel` read from the staged dictionary on disk equals
> the arm the entry names, AND equals the model `simpleFoam` reports selecting
> in `log.run`.**

* **PASS**: 78 / 78.
* **Otherwise the whole sweep is `NOT A RESULT`** — not GATE FAIL. If the arms
  are not the models we think they are, no number the sweep produces is about
  what it claims to be about.

### G2 — NULL-ARM IDENTITY (the planted control's threshold)

For each of the 39 `kOmegaSST_null` runs, on the **internal field only**:

    relL2_U(case) = || U_null(20000) - U_shipped(t_ref) ||_2 / || U_shipped(t_ref) ||_2

with `t_ref` the shipped time directory in the §2.3 `ref` column.

* **PASS**: `relL2_U <= 1.0e-3` on **>= 37 of 39** cases, **AND**
  `max relL2_U <= 1.0e-2` over all 39.
* **GATE FAIL**: the band is not met.
* **`NOT A RESULT` for the entire sweep**: any case with `relL2_U > 1.0e-1`.
  A tenth-scale disagreement is not a tolerance question; it is a different
  problem being solved, and it condemns the harness rather than the row.

**What this threshold is, honestly.** It is a **gross-harness-error detector,
not a precision claim**, and this is a judgement fixed before staging rather
than a derived quantity:

* The null re-solves under a **changed** `controlDict` (uniform `endTime 20000`,
  `functions` emptied, `startFrom startTime`) and a **changed** `fvSolution`
  (`residualControl` emptied), so exact identity is not the right expectation
  and the tolerance is set to the **convergence level**, not to machine epsilon.
* The reference fields' provenance is **unknown**: OpenFOAM version, hardware,
  compiler and linear-solver tolerances of whoever generated the benchmark are
  not recorded anywhere this lane could find. `relL2_U <= 1e-3` accommodates all
  of that.
* On the eight ducts the reference was written at `writePrecision 6`, putting a
  ~1e-6 floor under those comparisons — six orders below the threshold.
* Anything genuinely wrong — wrong mesh, wrong boundary condition, missing
  `meanVelocityForce`, wrong `nu`, missing `caseDef`, wrong model — produces
  `relL2_U` of order 1e-2 to 1. **The gate is placed in the gap between the
  convergence level and the failure level, and there is a lot of room in it.**
* **`>= 37 of 39` and not `39 of 39`** because the reference iteration counts are
  not uniform: 29 hills at 20,000 (identical to ours), CBFS at 30,000, PH_Breuer
  at 10,000, and the eight ducts at 334–7,009 under a criterion we do not use.

**SUPERVISOR'S RULING, 2026-08-27, made BEFORE staging and BEFORE any solver
started — the flat count is replaced by a STRUCTURAL PARTITION.** The lane was
right to flag `37 of 39` as the weakest number here, and right about *why*: as
written it is a **lottery** over *which* two cases may miss the band, and a gate
that does not say in advance which rows are allowed to fail is a gate that can
absorb the wrong failure. Ruled instead, at the same headline count and strictly
stronger:

> **The 29 `Parm_PH_29` hills are ITERATION-MATCHED** — their shipped reference
> was written at `endTime 20000`, *exactly* this sweep's cap — so on those there
> is no excuse and **ALL 29 must meet the 1e-3 band**.
> **The 10 unmatched cases** (8 ducts at 334–7,009 under a criterion we do not
> use, CBFS at 30,000, PH_Breuer at 10,000) may contribute **at most 2**
> outliers, and those still sit under the hard 1e-2 ceiling.

Total in-band is still `>= 37 of 39`, but **the two permitted outliers can no
longer hide among the hills**, which are the only cases where a miss would have
no available excuse. The partition is fixed here, in the frozen text, and is
implemented at `grade_m1.py` `G2_MATCHED_PREFIX` / `G2_UNMATCHED_MAX_OUT`.

**It ships with its planted-failure proof (L-314), because a partition that
cannot bite is a partition that reads as a gate and is not one.** Two selftest
controls run at **the same 37-of-39 count**: with both outliers on unmatched
cases the gate **PASSES**; move one of them onto a hill and the gate **GATE
FAILS**, naming the hill in `matched_out_of_band`. A third control asserts the
rule is a **no-op on fixtures containing no hill**, so it cannot silently have
changed the controls that predate it.

`relL2` on `k` and on `nut` is computed and printed for all 39 as a
**diagnostic**, and is **not gated**.

### G3 — ARM SEPARATION. A SPREAD, AND ONLY A SPREAD.

For each of the 39 cases, on the internal field only:

    relL2_arms(case) = || U_kOmega(20000) - U_kOmegaSST(20000) ||_2 / || U_kOmegaSST(20000) ||_2

* **GATE REACHED**: `relL2_arms > 1.0e-2` on **>= 30 of 39** cases.
* **GATE FAIL**: fewer than 30.

**The label, and it is part of the gate.** This is a statement about **how
sensitive the solution is to the choice of closure**, on this mesh, at this
iteration budget, between these two specific models. It is **NOT** a model-form
uncertainty, **NO** interval is calibrated from it, and the record may not use
the word "uncertainty" for it. See §11.

**What a GATE FAIL here means, and what it does not.** With G1 passing, two arms
producing near-identical fields is a **finding about the two models** — that
`kOmega` and `kOmegaSST` agree on these flows — and the record must report it as
such. It is explicitly **not** grounds to change the arms, the schemes, the
relaxation or the cap in search of separation: that is exactly the
answer-changing parameter hunt Sanaa's §3 **ANTI-GAMING** clause forbids
(*"Answer-changing choices (model, scheme class, formulation) are never selected
by agreement with the reference"*). G1 is what distinguishes "the models agree"
from "the arm did not apply", and G1 is decided before G3 is read.

### G4 — CAP-BOUND CENSUS. A ROW CLASS, NOT A VERDICT.

> **Count of the 78 runs that are CAP-BOUND under §4.1.**

* **GATE REACHED**: `<= 8 of 78` CAP-BOUND.
* **GATE FAIL**: more than 8.

**Why 8.** Under `kOmegaSST` all three measured archetypes meet the criterion by
~5,000 iterations (§4.1), so the expectation for the null arm is zero. Eight is
one whole family's worth of cases, and the gate is deliberately loose because
**`kOmega`'s residual plateau on these meshes has never been measured on this
box** and this registration will not pretend otherwise.

Whatever the count, §4.3's four reporting rules apply to every capped row.

### G5 — NOT REGISTERED IN M1: the error against LES/DNS truth

The truth fields are on disk (`U_LES`, `k_LES`, `tauij_LES`, and `p_LES` on CBFS
and `PH_Breuer`), and a per-case error gate against them in `BASELINES.md`'s own
metric would be legitimate. **It is deliberately NOT in M1**, and the reason is
sequencing rather than difficulty: an error band per arm must be fixed in
advance, and a band fixed in the same document that first measures the spread is
a band that could have been chosen to fit. **The truth comparison is a separate
registration (proposed: M2), frozen after M1's fields exist and before its own
bands are computed.** M1 therefore ranks nothing.

---

## 8. WHAT IS EXPLICITLY NOT GATED

* **Any gate calling the inter-model spread a model-form UNCERTAINTY, or
  calibrating a confidence interval from it.** The two arms are not
  independent (§11); the spread is a lower bound of unknown tightness, and a
  gate treating it as an interval would assert exactly what the work cannot see.
* **Any gate on grid convergence, GCI or observed order.** **One mesh per case
  is shipped; there is no triple.** **Standing rule 5 (Roache triple gating)
  DOES NOT APPLY to this rung, and `grade_m1.py` prints that sentence in its
  own output** so no reader of the results file has to infer it. No GCI is
  quoted anywhere, at any `Fs`, for any row. Discretisation error in the shipped
  meshes is common to both arms and invisible to the spread.
* **Any ranking of the two models as better or worse.** Without truth that is an
  opinion with a number attached (§7 G5).
* **Any gate on the de Zordo-Banliat aggregation's accuracy.** M1 produces that
  method's inputs. Whether a random forest learns useful per-cell weights from
  them is a separate question with its own registration.
* **Any threshold chosen after staging has run.** Standing rule 2: the freeze is
  this document's entire evidentiary content.

---

## 9. COST

**Unit: core-minutes = wall s x ranks / 60.** Ranks = 1 on every entry (§10).

### 9.1 Basis — measured on this box, on these meshes

`simpleFoam`, OpenFOAM v2606, `nProcs : 1`:

| case | cells | s/iteration | us per cell-iteration | source |
|---|---|---|---|---|
| `AR_1_Ret_360` | 3,025 | 0.010814 | 3.575 | `Kaandorp2020_TBRF/aposteriori/RESULTS.md:393` |
| `AR_3_Ret_360` | 8,748 | 0.035079 | 4.010 | same, `:394` |
| `CBFS13700` | 21,000 | 0.069512 | 3.310 | same, `:395-396` |
| `alpha_10_9000_3036` | 15,600 | 0.037242–0.048116 | 2.387–3.084 | `/home/ubuntu/closure-data/aposteriori/kaandorp/alpha_10_9000_3036__EIG_*/log.run` |

**Point rate 3.30 us/cell-iteration; measured envelope 2.387–4.010.**

Deliberately **excluded**: `/home/ubuntu/closure-data/xiao/G0_sst_alpha_10_9000_3036/log.run`
at 0.21 us/cell-iteration. Its header reads `Create mesh for time = 20000` — it
is a restart from a converged field, where every linear solve meets tolerance in
its minimum sweeps. Using it would understate the sweep by an order of magnitude.

### 9.2 The registered numbers

590,026 cells x 20,000 iterations x 2 arms = **2.360e10 cell-iterations**.

| basis | core-min per arm | **total (2 arms)** | core-h | $ at $0.0513/core-h |
|---|---|---|---|---|
| 2.387 us (measured floor) | 469.5 | 938.9 | 15.65 | $0.80 |
| **3.30 us (POINT — the REGISTERED ESTIMATE)** | **649.0** | **1,298.1** | **21.63** | **$1.11** |
| 4.010 us (measured ceiling) | 788.7 | 1,577.3 | 26.29 | $1.35 |
| **REGISTERED CAP (the runaway guard)** | 946.4 | **1,900.0** | **31.67** | **$1.62** |

* **`cost_core_min_estimate` = the point column**, per entry, in the §2.3 table.
* **`cap_core_min_registered` = the cap column**, per entry, in the §2.3 table:
  `cells x 20000 x 4.010e-6 x 1.20 / 60`. The 1.20 is margin over the **measured
  ceiling**, taken because two cases (`AR_10_Ret_180` 22,090 and
  `AR_14_Ret_180` 31,819) sit **outside the 3,025–21,000-cell range the envelope
  was measured over**.
* The per-entry cap is **1.458x** the per-entry estimate. The **largest
  actual/estimate ratio observable in the existing logs is 1.215**
  (`AR_3_Ret_360`: measured 0.035079 s/it gives 11.69 core-min at 20,000 against
  a 9.62 estimate), so the cap covers the worst measured misprediction with 20 %
  to spare.
* **An overrun STOPS the run. It does not get a new budget** (standing rule 12).
  `run_m1.sh` enforces it as a wall-clock `timeout` of `cap_core_min x 60`
  seconds (ranks = 1), and records `capped=1` **from an independent witness —
  the wall clock — never from the rc**, because 124 and 137 are both legal child
  exit codes and reading a budget stop off an rc would relabel an OOM kill.
* **Every dollar figure above is DERIVED, NOT MEASURED.** The rate
  **c7a.4xlarge at $0.0513/core-h** is **owner-stated** (2026-08-21/22) and this
  box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
* Against `CLOSURE_MODELLING_CHARTER.md` §18's 487 core-h: **4.4 %** at the
  point estimate, **6.5 %** at the registered cap. Inside the 2026-08-21 blanket
  — **and costed anyway, because a blanket is not a per-item read** (rule 9).

### 9.3 Named waste, not absorbed

**~206 core-min (16 % of the estimate) are plateau iterations bought
deliberately** by removing `residualControl` (§4.2) — most of it on the eight
ducts, which converge by ~1,400 iterations and then run 18,600 more. This is
**waste, it is named here in advance, and it is reported separately at
completion**; it is never folded into the actual/predicted ratio
(`COMPUTE_BUDGET_CHARTER.md` §6).

### 9.4 Calibration at completion is mandatory (standing rule 12)

At completion — all 78 graded — the record compares the pre-registered estimate
against the actual incurred cost, in core-minutes summed from the 78 `STATUS`
files, and lands **a row in `docs/COST_CALIBRATION.md`** stating:

* the ratio **actual / predicted**, against the 1,298.1 core-min registered here;
* attribution split three ways — **contention**, **named waste** (§9.3), and
  **misprediction of the rate** — never merged;
* dollars derived at the recorded rate and labelled **derived, not measured**.

**Contention will be material and must be attributed, not absorbed.** Read at
drafting time: `nproc` = 16, `/proc/loadavg` = **18.16 20.38 19.20** — the box
is already oversubscribed, and wall time per run will exceed the serial-rate
prediction for reasons that have nothing to do with this sweep. **A completion
report without §9.4's comparison is incomplete.**

### 9.5 Headline metrics (Sanaa §2)

Every report on this rung carries: **CPU %, GPU %, closure queue depth,
idle-minutes per resource.** M1 uses **no GPU**; its GPU % is 0 by construction
and is reported as such rather than omitted.

---

## 10. RANKS, CONCURRENCY AND MEMORY

**`ranks: 1` on every entry.** Total work is fixed at ~1,298 core-min and the 78
runs are embarrassingly parallel with no communication, so throughput is
maximised by running many single-rank entries concurrently. The meshes are far
too small to decompose: 15,600 cells over the hills' shipped 8 subdomains is
1,950 cells per rank, and the smallest duct over its shipped 4 is 552 — below
the ~1e4 cells/rank where OpenFOAM's SIMPLE loop amortises halo exchange and
GAMG's coarse-level global reductions, adding ranks **increases** core-minutes.
Every measured run of these cases on this box is `nProcs : 1`. **No
`decomposeParDict` is used and no `processor*` directory is created**; the
shipped ones are inherited from the benchmark's author and are staged unread.

**Honest limitation: there is no parallel run of these cases on disk, so "serial
is better" is reasoned from cells-per-rank and fixed total work, NOT measured.**

`memory_floor_gb: 1.0` on every entry. **This is an ESTIMATE, not a
measurement** — no resident-set size was measured for these cases. The largest
case is 31,819 cells; the box reads 30 GB total with ~10 GB available.

**Concurrency is a runner property, not an entry property.**
`QUEUE_ENTRY_STANDARD.md` §6: the validator *"does not schedule, order,
prioritise or start anything."*

---

## 11. WHAT IT CANNOT SEE

*Mandatory under `CLOSURE_MODELLING_CHARTER.md` §16. A record without this
section is returned.*

### 11.1 The disclosure that matters most

**`kOmegaSST` and `kOmega` are BOTH linear eddy-viscosity models. They share the
Boussinesq constitutive assumption — that the Reynolds-stress anisotropy is
aligned with and proportional to the mean strain rate. Their errors are
therefore CORRELATED, NOT INDEPENDENT, and the spread between them
SYSTEMATICALLY UNDERSTATES the true model-form uncertainty.**

The spread is a **lower bound of unknown tightness**. It has **no access
whatever** to the error both models make together, and on these very cases that
shared error is the dominant one: `_common/BASELINES.md` §5 records the duct
failure as *"the secondary flow a linear model cannot make"* — a failure that is
**identical in both arms** and contributes **exactly zero** to the spread. On
the eight ducts, the quantity of greatest physical interest is precisely the
quantity this sweep is blindest to.

**Two models disagreeing tells you the answer is closure-sensitive. It does not
tell you which is right, or that either is.** The disagreement can be small
where both are badly wrong in the same direction — and on the ducts it will be.

### 11.2 A spread is not an error, and M1 is not a validation

M1 registers no comparison against truth (§7 G5). Its entire validation content
is deferred. A record that reports the spread and calls it uncertainty, or
ranks the two models, would be claiming what the work does not support.

### 11.3 The rest, named rather than implied

* **No grid dependence, no GCI, no observed order, and standing rule 5 does not
  apply** — one mesh per case, no triple exists (§8).
* **No iterative-convergence claim on `p`, `Uy` or `Uz` for the eight ducts.**
  Under a linear eddy-viscosity model those residuals are un-normalisable and
  sit at O(0.1–0.7) forever (§4.1). The sweep can say the duct **turbulence**
  fields converged; it cannot say the duct **in-plane momentum** field did, and
  it does not.
* **`kOmega`'s convergence behaviour on these meshes has never been measured on
  this box.** Every cost figure and every cap in §9 rests on `kOmegaSST` /
  `kOmegaSSTFrozen` rates.
* **The measured us/cell-iteration envelope spans 3,025–21,000 cells only.**
  `AR_10_Ret_180` (22,090) and `AR_14_Ret_180` (31,819) are extrapolations.
* **The reference fields' provenance is unknown** — version, hardware, compiler,
  tolerances. G2 therefore cannot be a precision statement (§7 G2).
* **`NASA_2DWMH` is excluded**, so nothing here bears on the NASA wall-mounted
  hump, and the sweep's case count is 39 rather than the benchmark's 40.
* **No genuinely three-dimensional external flow.** The 29 hills, `PH_Breuer`
  and CBFS are 2-D/quasi-2-D; the eight ducts are 3-D but streamwise-periodic.
  The clone contains no wing-body junction, Ahmed body or FAITH hill
  (`_common/BASELINES.md:317-318`).
* **`y+` was not computed on any case.** The "wall-resolved" reading is inferred
  from boundary-condition types (`nutLowReWallFunction`, `k` fixed at 1e-15 at
  the wall), not measured.
* **Memory floors are estimates** (§10).
* **Serial-is-better is reasoned, not measured** (§10).
* **Nothing here bears on unsteady or transient behaviour.** `ddtSchemes default
  steadyState` throughout; both arms are steady RANS.

---

## 12. INSTRUMENTS

All four live in this directory. **None has been executed.**

| file | role |
|---|---|
| `stage_m1.py` | staging. Default is a **dry run**; writing requires `--execute`. Guards R1–R16 (§5), each `raise`/`sys.exit(2)`, `--selftest` under `-O`, planted-failure proof per guard. Writes `STAGING_MANIFEST_M1.json` with everything read back off disk (§5.7). |
| `run_m1.sh` | the driver a queue entry names. Refuses an unreachable solver, an already-armed case, a missing `0.orig`. Arms `0/` from `0.orig/`, touches `0/U` last, runs `simpleFoam` **in its own foreground with the rc captured from it**, and **writes `STATUS` at exit** (Sanaa §2) atomically via a same-directory temp file and `mv`. |
| `grade_m1.py` | the comparator. C1 planted zero on disk before any number; C3–C5; §4.1 convergence classification; G0–G4; `gate_m1.json`; `--selftest` under `-O`; planted-failure proofs. |
| `make_queue_entries_m1.py` | regenerates the 78 entries. Cell counts are read from each case's own `polyMesh/owner` at generation time; nothing is typed from a table. After the freeze: `--prereg-commit <40-hex> --enqueued-by <who>`. It **refuses** a `--prereg-commit` that is not 40 lowercase hex. |
| `QUEUE_ENTRIES_DRAFT/` | 78 entry JSONs with `prereg_commit` = `PENDING_SUPERVISOR_FREEZE` and `enqueued_by` = `PENDING_SUPERVISOR_ENQUEUE`. **NOT in `verification/queue/closure/`.** |

**`run_m1.sh`'s shebang is INERT** — line 1 is the mandatory DRAFT banner and the kernel honours a shebang only on line 1. Every queue entry therefore names `/bin/bash` explicitly in its `launch_cmd` argv and never invokes `./run_m1.sh`, which would fall through to `/bin/sh`. Stated because it is exactly the kind of thing that works in a test shell and fails under a daemon.

**`run_m1.sh` captures the rc INSIDE the wrapper.** `setsid timeout cmd` returns
0 for every outcome, so an rc captured around a `setsid` line is meaningless.
`run_m1.sh` runs the solver itself, in its own foreground, and captures `$?`
immediately. Anything that detaches it may do so freely; the rc is already
safely inside `STATUS`.

**A defect found in the prior art while writing this, reported not copied:**
`verification/runs/T-family/T5_runs/run_one_t5.sh` records `checkMesh`'s exit
code as

    checkMesh -case "$CASE_DIR" -allRegions > ... 2>&1 || true
    CHECKMESH_RC=$?

`$?` after `|| true` is **always 0**, so that field records nothing.
`run_m1.sh` uses `set +e; checkMesh ...; RC=$?; set -e` instead. **This is a
finding about T5's STATUS field, not about T5's physics**, it is
infrastructure-class under L-342, and it is raised for the heat-transfer team's
owner rather than fixed here by a closure lane.

---

## 13. FREEZE PROTOCOL

1. The **supervisor personally** reads this file and performs
   `SUPERVISION_CHARTER.md` §3 check 4. **This lane did not and does not claim
   it.**
2. The supervisor commits this file under the rule-10 private-index protocol,
   capturing HEAD once, asserting on `git diff-tree --stat`, and **verifying
   after the commit** that only the intended paths landed (L-223).
3. The supervisor writes the resulting **40-character sha** into all 78 entries'
   `prereg_commit`, replacing `PENDING_SUPERVISOR_FREEZE`, and re-runs
   `scripts/queue_entry_check.py`.
4. **`stage_m1.py --execute` runs only after the freeze**, and its manifest is
   inspected before any entry is copied into `verification/queue/closure/`.
5. Only then may entries be dropped into `verification/queue/closure/`. **A
   valid entry there is launched by a cron-restarted daemon within ~60 s**,
   which is why this lane wrote none.
6. **After the first compute, the gates are closed.** Changes land only as dated
   addenda that cannot alter a gate, threshold, cap or label; originals are
   struck, never rewritten; and the addendum asserts `lines whose number changed
   above this section: 0`.

---

## 14. WHERE THIS LANE DISAGREED, OR WOULD HAVE DECIDED DIFFERENTLY

Recorded because a drafting lane that only agrees is not adding a check.

1. **The `kOmegaSST` null arm should arguably be run TWICE, not once** — a
   second null run differing only in a harmless nuisance parameter would
   separate "the harness reproduces the reference" from "the harness is
   deterministic". It is not proposed here because it costs a third arm's
   compute for a property that `relL2 = 0` between two identical runs would
   establish more cheaply, and because the supervisor ruled two arms. **Flagged,
   not fought.**
2. **G2's `>= 37 of 39` is the weakest number in this document.** It is a
   judgement, not a derivation, and the supervisor should either ratify it or
   replace it with `39 of 39` at `1e-2`, which is defensible and simpler. This
   lane leans to ratifying 37/39 at 1e-3 *with* the 1e-2 ceiling, because the
   two thresholds together are more informative than either alone — but the
   choice is the supervisor's and it must be made **before** staging.
3. **This lane would have preferred `LaunderSharmaKE` in M1 over `kOmega`**, on
   physics: it is the low-Re k-epsilon variant appropriate to a wall-resolved
   mesh, and pairing a k-omega with a k-epsilon would put a genuine
   two-equation-family boundary inside the sweep, where `kOmegaSST` vs `kOmega`
   puts only a blending-function boundary. **The supervisor's ruling is
   correct and this lane implements it**: `LaunderSharmaKE` needs an `epsilon`
   wall boundary condition that is not derivable for 11 of the 39 cases, and an
   undetermined BC inside an arm is an unregistered modelling choice. The
   preference is recorded so that when the k-epsilon registration is written,
   the epsilon wall BC is understood to be **the** open item and not a detail.
4. **The 20,000 cap is generous and this lane considered 10,000.** 10,000 is
   above every measured `kOmegaSST` convergence in the sweep and would halve the
   cost. It was rejected on one ground: it would break the equality between the
   null arm's iteration count and the 29 hills' reference fields', which is the
   single cleanest property gate G2 has. **Cost was traded for a control, and
   the trade is 649 core-min = ~$0.55 derived.**

---

## 15. PROVENANCE OF THE LOAD-BEARING NUMBERS

Every number in §2.3, §3.1, §4.1 and §9.1 was read from disk **inside the same
shell invocation that reported it**. Nothing load-bearing was read back from a
scratch file written by an earlier invocation, and **nothing in this document
cites a scratch path** (L-186).

| claim | how it was established |
|---|---|
| 39 cases / 590,026 cells / 1 excluded | enumerated afresh by walking `polyMesh` directories under `/home/ubuntu/closure-challenge-benchmark/data`, requiring `0/` + `system/` + `constant/turbulenceProperties`; the §2.3 table was **generated by that enumeration**, not typed |
| the exclusion's two blockers | `RASModel` and `0/nut` `internalField` re-parsed per case in the same walk; 39 `uniform 0`, 1 `uniform $nut` |
| `libs` on 11 of 39, one of them a hill | re-parsed per case in the same walk |
| `caseDef` on the 8 ducts | `os.path.isfile` per case in the same walk |
| shipped `endTime` and `ref` directory | re-parsed / re-listed per case in the same walk |
| the residual histories in §3.1 and §4.1 | extracted per-outer-iteration from the named `log.run` files, first solve of each time step only |
| the four us/cell-iteration rates | quoted from `Kaandorp2020_TBRF/aposteriori/RESULTS.md:393-396` and re-derived from `ExecutionTime` line counts in the `alpha_10_9000_3036__EIG_*` logs |
| `dlLibraryTable.C:185-190` warns rather than raises | cited from the feasibility memo §2.4, which read the source. **This lane did not re-read the OpenFOAM source**, and the citation is therefore secondary |
| box state (`nproc` 16, load 18.16, 30 GB) | read at drafting time; it is a snapshot and will not hold at run time |

**Documents read from the HEAD blob (`git show HEAD:<path>`), never from the
worktree:** the Sanaa directives capture, the feasibility memo, `DOCKET.md`,
`QUEUE_ENTRY_STANDARD.md`, `run_one_t5.sh`, `analyse_t3.py`,
`REPORTING_CHARTER.md`. `git diff HEAD` currently reports 236 paths as pure
deletions, of which 222 are byte-identical to HEAD — an artefact of the
private-index protocol — so **nothing in this document was concluded from
`git status` or `git diff HEAD`**.

---

---

## 16. PRE-FREEZE VERIFICATION LOG, AND THE CORRECTIONS IT FORCED

**Condition, and how it was checked** (standing rule 2: before first compute,
amendments are legal and must state the condition and how it was checked):
**the run root `/home/ubuntu/closure-data/multimodel_sweep/` DOES NOT EXIST** —
verified by `ls -d` after every change below — **so no compute has occurred, no
gate has been closed, and this document has never been committed.** Everything
in this section is a pre-freeze correction, not an addendum to a frozen file.

### 16.1 What was executed (no solver, no staging, no queue entry)

| check | result |
|---|---|
| `python3 -O stage_m1.py --selftest` | **PASS** — 16 guards, each refusing its own planted failure, plus an L-314 no-op proof per guard, all under `-O` with every refusal still firing |
| `python3 stage_m1.py --selftest` (assertions live) | **PASS** |
| `python3 -O stage_m1.py` (DRY RUN, real benchmark tree) | 40 case roots enumerated; **78 planned**, **2 skipped by guard R2** (`NASA_2DWMH`, both arms), **0 failures**; run root confirmed still absent afterwards |
| `python3 -O grade_m1.py --selftest` | **PASS** — rule-4 clauses, the age guard, L-342/R-RC, the C1 plant and its blind-reader planted failure, the convergence classifier, `rel_l2` and its refusals, the G2/G3 verdict logic and the double-aggregate rule |
| `python3 -O grade_m1.py` (real run root) | **exit 2**, 78 rows `PENDING` — a partial sweep receives no verdict |
| `bash -n run_m1.sh`, then 11 refusal paths | every one exits 2, **and NONE writes a STATUS** — nothing ran, so no rc is invented |
| `scripts/queue_entry_check.py` on a draft entry | **REFUSED** on two independent grounds: `SCHEMA` (`prereg_commit` is not a 40-hex sha) and `EXEC` (`cwd` does not exist). Nothing in `QUEUE_ENTRIES_DRAFT/` can launch |

### 16.2 Three corrections the tools forced, before the freeze

1. **§5.9 is new.** The eight ducts ship **symbolic initial fields**
   (`0/U uniform $Uinlet`, `0/k uniform $kInlet`, `0/omega uniform $omegaInlet`),
   with `$Uinlet` resolved through `#include "../caseDef"` and `#calc` **inside
   `0/U` itself**. Found by the staging tool's own rule-3 control refusing on all
   sixteen duct entries. This makes `caseDef` load-bearing for the initial
   fields, changed guard R9 from a `caseDef` special case into a general
   include-resolution guard over `system/` **and** `0.orig/`, and moved the
   rule-3 plant's primary carrier to `0.orig/nut`.
2. **§5.5 now stages `fieldDef` as well as `caseDef`**, and records that
   `dynamicCode/` is deliberately not copied.
3. **A defect in the prior art was found and reported rather than copied**
   (§12): `run_one_t5.sh` records `checkMesh`'s rc after a `|| true`, where `$?`
   is always 0. `run_m1.sh` does not.

**A fourth defect was found in this lane's own first draft of `stage_m1.py` and
is recorded because it is the more instructive one:**
`open(p, "w").write(transform(open(p).read()))` **truncates the file before the
inner read is evaluated**, so it silently writes an empty file. It defeated guard
R12 (and made three mutation tests pass for the wrong reason — the guards fired
on emptiness, not on the planted defect). It was caught only because the selftest
checks the *content* R12 is supposed to see rather than checking that R12
refused. The fix is `_rewrite()`, which reads fully before opening for write.
**A mutation test that only asks "did the guard refuse?" can pass while the guard
is refusing for a reason that has nothing to do with the mutation.**

### 16.3 What this lane could not verify

* **Nothing was solved, staged or enqueued.** Every figure in §3.1, §4.1 and
  §9.1 comes from runs that already existed on disk.
* **The staging tool has never been run with `--execute`**, so guards R6–R15 have
  been exercised only on synthetic trees and on the source tree in dry run —
  never on a real staged case.
* **`kOmega` has never been run on any of these meshes on this box.** Its
  convergence behaviour, its cost, and whether it meets the §4.1 criterion inside
  the cap are all **unmeasured**.
* **G2's `>= 37 of 39` and G3's `>= 30 of 39` are judgements**, not derived
  quantities (§14 item 2).
* **`dlLibraryTable.C:185-190` warns rather than raises** is cited from the
  feasibility memo, which read the source. **This lane did not re-read it.**
* **No `#calc` compilation was exercised by this lane.** That it works on this
  box is inferred from the existence of `dynamicCode/` in the lab's earlier duct
  run directories, not from a run this lane made.

---

**END OF PRE-REGISTRATION. NOT FROZEN. NOT COMMITTED. NOT ENQUEUED. 0.000
CORE-MINUTES SPENT.**
