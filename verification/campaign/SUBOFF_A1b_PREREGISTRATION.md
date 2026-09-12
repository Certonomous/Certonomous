# SUBOFF **A1b** — TWO SOLVED LEVELS ON MESHES THAT ALREADY EXIST — PRE-REGISTRATION

> ## 🔴 §0. WHAT THIS DOCUMENT REFUSES TO CLAIM, BEFORE IT CLAIMS ANYTHING
>
> **THERE IS NO ROACHE TRIPLE HERE AND THERE NEVER WILL BE.** A1b covers **two** grid
> levels. Two levels cannot give an observed order, so:
>
> - **NO GCI IS QUOTED. NO OBSERVED ORDER `p`. NO RICHARDSON EXTRAPOLATION.** Not omitted
>   for brevity — **ABSENT, because they do not exist for two levels**, and any document
>   or page that prints one for A1b is wrong on its face.
> - **Every gate that requires a triple is `NOT A RESULT` BY CONSTRUCTION**, declared here
>   in advance rather than discovered at grading. **By name: Gate D2 / `CT` agreement.**
> - **The level-to-level change in `CT` is reported as a DIFFERENCE, explicitly NOT as a
>   convergence.** A difference between two grids bounds nothing: it is consistent with
>   convergence, with divergence, and with coincidence, and A1b cannot tell them apart.
>
> **WHAT A1b CAN CLAIM:** a **COMPLETED 3-D solve at two levels** under rule 4's strict
> completion rule; **forces and `CT` reported as measured values** with their measured
> wetted-area basis; **`y⁺` measured and gated**; and that level-to-level difference,
> labelled as one.
>
> **🔴 THE DISTINCTION THE WHOLE DOCUMENT TURNS ON: THE CLAIM SHRINKS TO FIT THE HARDWARE.
> THE GATE DOES NOT BEND TO FIT THE CLAIM.** If a reader could mistake this for the graded
> triple A1 promised, it is written wrong.

---

## 1. A1b IS A SUCCESSOR, AND IT CITES ITS PREDECESSOR'S DEATH RATHER THAN REPLACING IT QUIETLY

**`SUBOFF_A1_PREREGISTRATION.md` IS A DEAD REGISTRATION AND A1b DOES NOT REVIVE IT.**

A1's §5.1 defines Gate M verbatim as *"`PASS` iff M-a, M-b, M-c and M-d all hold at **L1,
L2 and L3**"*, with the launch bar *"and no solver is launched."* **L3 cannot be built on
this machine** — 25.45 M cells against 30 GiB of RAM. So **Gate M cannot reach `PASS` under
any mesh repair, however clean, and under any load, however idle the box.** A1 is
unsatisfiable *here*, and the cfd-supervisor has ruled `[lab-attributed]` that **no solver
launches under A1, ever.**

**A1b DOES NOT NARROW A1's GATE, EVADE IT, OR REINTERPRET IT.** A1's Gate M stands exactly
as frozen, failed and unsatisfiable. A1b is a **different, smaller, satisfiable question**
asked of the **same two meshes**, and it says so in its title block so that nobody reads
the smaller answer as the larger one.

**What A1b inherits unchanged, already measured and already paid for:** the geometry
pipeline and its title-page-verified source (A1 §2.1, §3, §11.1, §11.9); the built meshes
**L1 = 3,268,613 cells** and **L2 = 9,121,237 cells**, **305.60 core-min already spent**;
`CT_REFERENCE.json`; the `y⁺` derivation; the five instruments and their planted controls.
**NO NEW MESHING. NOTHING IS RE-DERIVED.**

---

## 2. 🔴 MESH ADMISSION — AND L1 IS **NOT ADMITTED**, STATED BEFORE THE SOLVE

A1's mesh limbs are **measured facts about these meshes** and A1b reports them as such. It
does **not** invent softer ones.

| level | cells | min cell determinant (floor `1.0e-03`) | nonOrtho (≤70) | skew (≤4) | 3-D | cells across TE base (floor 8) | **A1b admission** |
|---|---:|---|---|---|---|---|---|
| `L0c` | 1,206,389 | **3.4590623e-03** ✅ | 69.583 | 2.987 | ✅ | **6** ❌ | **NOT ADMITTED** — `GATE FAIL` on M-b-1 |
| **L1** | 3,268,613 | **8.6227045e-04** ❌ | 64.953 | 2.913 | ✅ | 8 ✅ | **NOT ADMITTED** — `GATE FAIL` on M-d |
| **L2** | 9,121,237 | **1.5198839e-03** ✅ | 64.906 | 3.126 | ✅ | 12.8 ✅ | **ADMITTED — the only level that passes every limb** |

### 2.1 THE CALL ON L1, MADE IN ADVANCE AND WITH ITS REASONING FROZEN

> **L1 IS SOLVED, AND IT IS NOT ADMITTED. Those are two different statements and A1b keeps
> them apart.**
>
> **L1 is `GATE FAIL` on the determinant limb and the failure travels with every number
> that comes out of it.** `minDeterminant 1.0e-03` is not moved, not softened, and not
> read narrowly. L1 is **not** promoted to admitted by any argument about how small the
> failure is.

**Why solve it anyway, stated so it can be judged:**

1. **A1b's product is a REPORTED DIFFERENCE, not a graded verdict.** Mesh admission exists
   to stop compute producing a number the mesh cannot support **and being presented as a
   verdict**. §0 has already refused every verdict that admission would protect. A
   disclosed sub-admissible level feeding a difference that is labelled a difference is
   not the thing the limb guards against.
2. **The mesh is already built and paid for.** No compute is spent making it.
3. **The failure is characterised, not mysterious:** one cell in 3,268,613 — `3.06e-07` of
   the mesh — at `8.6227045e-04`, **13.8 % below** the floor, **invariant to partitioning
   and to alignment to five significant figures** (A1 §12.8), with **zero negative
   volumes** and 98.507 % layer coverage. For contrast, R1b's family sat at `3.526e-05`,
   **28× below**, at every level.
4. **`L0c`'s new measurement makes L1 an ISLAND, not a floor.** 1.21 M clears the floor by
   3.5×; 3.27 M fails; 9.12 M clears. **The degeneracy is not monotone in resolution**, and
   A1 §12.8's broader reading — that everything at or below 3.27 M fails — is now
   **measured false**.

**WHAT WOULD HAVE MADE ME REFUSE TO SOLVE L1:** negative volumes, a determinant an order of
magnitude below the floor as R1b's was, or any claim in A1b resting on L1 **alone**. None
holds. **`L0c` IS NOT SOLVED** under this registration: 6 cells across the truncated base
cannot represent the blunt-base recirculation the truncation exists to make representable,
so its solve would answer a question about a feature it does not resolve.

### 2.2 TWO THINGS ABOUT `L0c` THAT ARE NOT IN THE TABLE, AND ONE OF THEM IS WHY IT IS NOT SOLVE-READY

**`L0c` FINISHED MESHING WITH 123 ILLEGAL FACES.** Its log's closing line reads *"Finished
meshing with 123 illegal faces (concave, zero area or negative cell pyramid volume)"*, where
**L1 and L2 both close with "Finished meshing without any errors"**. That is a **difference
in kind** between the coarsest level and the two above it, and it is the first time this
family has ended a build that way. The concave count is **not** the new part — `checkMesh`
flags concave cells at every level (34,450 / 65,027 / 131,728). **The 123 faces at close
are new, and they are flagged rather than filed.**

> **`L0c` WAS BUILT FOR THE MEMORY CURVE AND FOR P10/P11. IT IS NOT SOLVE-READY AND
> NOTHING HERE SHOULD BE READ AS MAKING IT SO.** It fails Gate M-b-1 at 6 cells across the
> truncated base and it closes with illegal faces. Its registered purpose was discharged
> the moment its `Memory per-node` and its determinant were read.

**MAXIMUM NON-ORTHOGONALITY AT `L0c` IS 69.582824 AGAINST A CEILING OF 70.** It passes, and
it passes by **0.42 degrees**. L1 and L2 sit at 64.953 and 64.906, so **the coarsest level
is 4.6 degrees worse than both and is the only level anywhere near the ceiling.** Passing by
0.42° is passing — and it is said here in prose rather than left inside a table, where a
margin that thin disappears.

---

## 3. THE RUNS

`simpleFoam`, `kOmegaSST`, `nutUSpaldingWallFunction` on `hull` and `sail`, half-model at
zero drift, `Re_L = 1.2e7`, `U = 2.7547576 m/s`, **`endTime 3000`, `deltaT 1`, 4 ranks**,
in fresh `SOLVE_L1/` and `SOLVE_L2/` with every polyMesh file **`sha256`-pinned in source
and destination**. `residualControl` is **ABSENT**: an early residual exit satisfies
neither `last == endTime` nor the `ExecutionTime`-count clause, so a *converged* run would
have been graded incomplete.

---

## 4. THE GATES

### Gate C — COMPLETION (rule 4, unchanged from A1 §7 + §11.4)
> **`PASS` iff:** `rc = 0`; an `End` line; **last `Time` == 3000**; fields **`p U k omega
> nut phi`** present at `3000/`; `ExecutionTime` count **== 3000**; every field at `3000/`
> **newer** than the case's own `0/U`; every `processor*/3000/` field newer than `0/U` with
> none stale and none missing; `log.decomposePar.solve` **older** than those fields and
> `log.reconstructPar.solve` **newer**. **Any clause failing ⇒ NOT COMPLETE, and every gate
> behind it `BLOCKED`.**
> **WHAT WOULD HAVE FAILED THIS:** any one of the eight clauses; each is printed separately.

### Gate W — THE WALL TREATMENT MUST BE VALID WHERE IT IS USED
> **ARMED** iff `yPlus.dat` exists with both wall patches in it **and** both wall patches
> in `0/nut` carry `nutUSpaldingWallFunction`. **UNARMED ⇒ `BLOCKED`, never `PASS`.**
> **`PASS` iff `max(y⁺) < 300` over both wall patches at `endTime`; else `GATE FAIL`.**
> `y⁺` is REPORTED per patch whatever the outcome, from the `.dat` **and** independently
> from the log.
> **WHAT WOULD HAVE FAILED THIS:** any wall-patch `y⁺` maximum ≥ 300, or either wall patch
> carrying a different `nut` boundary condition.

**PREDICTED `y⁺`, carried forward from A1 §13.5, computed from `Re`, `ν` and `L` and the
BUILT layer stacks BEFORE any solver ran:** hull **50.0** at L1 and **27.9** at L2 at the
cell centre; estimated local maxima **87** and **48**; sail 9.6 and 5.4. **`y⁺` forbids
nothing here** and Gate W is expected to `PASS`. *(A1 §11.7's P5 is already falsified at L1
by this arithmetic — 50.0 outside its [15, 45] — and stays falsified; it is not restated.)*

### Gate D — `CT`, **REPORTED, `NOT A RESULT` BY CONSTRUCTION**
> **`CT` from both levels is `NOT A RESULT`, registered before any compute.** Two levels
> give no CONVERGING triple, so rule 5 fixes the label whatever the value.
> **`CT` IS REPORTED** with `CT_ref = 3.6916168e-03` and A1 §5.3's frozen ±15 % band
> **[3.1378743e-03, 4.2453593e-03]**, against each level's **own measured** wall-patch
> area (`Aref`; L2 = 3.0760958 m², hull 2.9841723 + sail 0.0919234, cross-checked against
> the hull STL half-area at ratio 0.99670 with the sign registered in advance).
> **The comparator has NO code path that emits `PASS` or `GATE FAIL` here** — demonstrated
> on a synthetic case whose `CT` lands **inside** the band at 3.70007e-03 and still returns
> `NOT A RESULT`.
> **WHAT WOULD HAVE FAILED THIS TEST: nothing either run can produce.** Declared as the
> gate's own limitation rather than disguised.

### The reported DIFFERENCE, and what it is not
> **`Δ = (CT_L1 − CT_L2)/CT_L2`, REPORTED, labelled `DIFFERENCE — NOT A CONVERGENCE`.**
> **Its coarse member FAILED mesh admission (§2.1), so it bounds nothing**, and the
> disclosure is printed beside the number every time the number is printed. **No observed
> order, no GCI, no extrapolation is computed from it — not even "for information".**

### Monitor states — findings, never budget kills
| # | state | action |
|---|---|---|
| S1 | a worst initial residual **higher** than its value 500 iterations earlier | **RECORD `RISING`.** R1b's signature; it is the answer, not an obstacle. No re-run with different relaxation. |
| S3 | **regression** of `Cd` over the final 500 iterations drifting **> 5 %** of the window mean | **RECORD `NOT PLATEAUED`.** R1b's two-point test called a −10.02 %/100-iteration drift `PLATEAUED`. |
| S5 | a time dir or solver artifact present at launch | **REFUSE to launch. Never clear the directory.** |
| **S6** | divergence, an unbounded field, or a non-zero solver rc | **STOP and TRIAGE. A crash is a FINDING until triage says otherwise.** |

---

## 5. FALSIFIERS — THREE CLASSES, EXECUTION FIRST

### CLASS 3 — EXECUTION AND TERMINATION
| # | how it may not complete | what is reported |
|---|---|---|
| **X1′** | **spend exceeds the §6 figures** | **NOTHING STOPS.** Sanaa, ~2026-09-12T01:10Z, verbatim: *"dont forget i dont want any cap on any run"*. §6's figures are **CALIBRATION PREDICTIONS TO BE SCORED, NEVER KILLS.** The overrun is reported with contention on its own line. *(A1 §13's X1 hard stop is withdrawn — see A1 §14.)* |
| **X2** | memory | the launcher reads `free -g` and **REFUSES** if `available − 4 GiB` is below the level's predicted footprint, writing `VERDICT=BLOCKED` with the measured figure. **She lifted caps; she did not add RAM.** A build or solve that OOMs another team's multi-day run is touching a running solver by another route. |
| **X3** | solver crash / divergence | **a FINDING until triage says otherwise**, reported with its last iteration and residual history. *(`trapFpe: Floating point exception trapping enabled` is the STARTUP BANNER saying trapping is ARMED — the opposite of an exception, present in every healthy log.)* |
| **X4** | the session dies | solver is `setsid`-detached with **rc captured INSIDE the wrapper**; a dead watcher is **reattached, never restarted** — a restart would violate S5 and the age guard. |
| **X5** | **the watcher gives up on a healthy long run** | **the watcher ESCALATES ON STALL AND NEVER KILLS.** Its ceiling is **DERIVED, not literal** — §6. **With no caps a run may be arbitrarily long, so a ceiling sized against a capped run is under-sized by construction**, and a watcher that quits on a healthy run produces no record, which is the same loss by another route. |

### CLASS 2 — ARTIFACT USABILITY
`coefficient.dat` absent or carrying no column **named** `Cd` ⇒ the reader **REFUSES
(exit 2)**, never guesses positionally. `yPlus.dat` absent or missing a wall patch ⇒ Gate W
**`BLOCKED`**. Fewer than 500 `Cd` rows ⇒ S3 **`BLOCKED`**. A serial run ⇒ the
`processor*` limbs **`BLOCKED`**, per A1 §11.4's own stated limitation. A wall patch
carrying another `nut` BC ⇒ Gate W **`BLOCKED`** *(demonstrated: substituting
`nutkWallFunction` flips a passing synthetic case `PASS` → `BLOCKED`)*.

### CLASS 1 — HYPOTHESIS. **Each falsifier is the COMPLEMENT of its prediction.**
| # | PREDICTION | FALSIFIED BY |
|---|---|---|
| **Q1** | both levels reach `endTime = 3000` and clear all eight clauses of Gate C | any clause failing at either level |
| **Q2** | Gate W `PASS` at both levels | `max(y⁺) ≥ 300` at either level — which falsifies the ITTC `u_τ` anchor and the wall-treatment argument with it, not merely a number |
| **Q3** | measured **average** hull `y⁺` within **±40 %** of §4's table: L1 ∈ [30.0, 70.1], L2 ∈ [16.8, 39.1] | a measured average outside those intervals at either level |
| **Q4** | **A1b marches where R1b blew up** — `S1 = NOT RISING` and `S3 = PLATEAUED` at both levels. *(R1b ran `CT` 0.011283 / 0.339200 / 4.732715 against a band of [0.00324, 0.00396] with residuals RISING under refinement.)* | `RISING` or `NOT PLATEAUED` at either level — which says A1's §1 diagnosis did **not** account for R1b's anomaly, and **the anomaly stays OPEN and gets larger** |
| **Q5** | reported `CT` at **L2** lands inside [3.1378743e-03, 4.2453593e-03] | a reported `CT` outside it. **🔴 NEITHER OUTCOME CHANGES THE LABEL** — Gate D is `NOT A RESULT` either way. Q5 exists **only** so a number in band cannot later be sold as agreement and a number out of band cannot be blamed on the physics rather than on the absent triple. |
| **Q6** | `|Δ|` between the levels is **< 25 %** | `|Δ| ≥ 25 %`. **This is a prediction about a DIFFERENCE and is not evidence of convergence at any value** (§0). |

---

## 6. COST — CALIBRATION FIGURES, NOT KILLS; AND THE WATCHER CEILING **DERIVED**

**MEASURED RATE, WITH ITS TIMESTAMP, BECAUSE TONIGHT'S RATES ARE NOT STABLE.** The
cfd-supervisor measured MRF fine (2,418,780 cells, 6 ranks) at **4.085 s/iteration at
00:35Z** and **10 s/iteration at 01:15Z** under peer load — a **2.4× swing in forty
minutes**. **An unqualified rate from tonight will mislead whoever reuses it.** A1b
anchors on the **worse, later** figure.

**DERIVATION, ONE LINE PER LEVEL.** Per-rank work relative to the anchor × the itemised
×1.55 solver correction (`nNonOrthogonalCorrectors` 2 vs 1; `p` `relTol` 0.01 vs 0.05):

- **L1**: `10 s/it × [(3.268613/4)/(2.418780/6)] × 1.55 = 31.4 s/it` ⇒ `× 3000 = 94,200 s
  = 26.2 h wall` ⇒ **6,280 core-min**, **$5.37 DERIVED NOT MEASURED**.
- **L2**: `10 s/it × [(9.121237/4)/(2.418780/6)] × 1.55 = 87.7 s/it` ⇒ `× 3000 = 263,100 s
  = 73.1 h wall` ⇒ **17,540 core-min**, **$15.00 DERIVED NOT MEASURED**.
- **Family: 23,820 core-min, $20.37 DERIVED NOT MEASURED.**

`cost_basis`: rate **$0.0513/core-h** is **owner-stated** (Sanaa 2026-08-21/22); **the box
cannot read its own billing** (`COMPUTE_BUDGET_CHARTER` §5). **These are PREDICTIONS TO BE
SCORED at completion under rule 12, with contention attributed on its own line and never
absorbed into the actual/predicted ratio. THEY STOP NOTHING.**

> **WATCHER CEILING, DERIVED: `26.2 h × 2 = 53 h` for L1 and `73.1 h × 2 = 147 h` for L2.**
> The ×2 covers the measured 2.4× intra-night rate swing at its midpoint. **The watcher
> ESCALATES at the ceiling; it NEVER KILLS.** Reaching a derived ceiling is a report to the
> cfd-supervisor, not a termination.

---

## 7. INSTRUMENTS — CARRIED FORWARD, NOT REBUILT

`cases/navier_class/SUBOFF_A1/{suboff_a1_polymesh,make_reference_ct,setup_solve,
grade_suboff_a1}.py` and `solve_level.sh`, all frozen at commit `05ca5550`. **Four planted
controls, each mutation-tested, each reading its plant back FROM DISK, each refusing exit 2
if the reader cannot see it:** a 12.345 m² patch area behind a **decoy** of 6.1725 m² at
`startFace 0` (separating an area-formula error from an indexing error — a 0.2 % formula
mutation refuses at `rel err 2.0e-03`, an indexing mutation at `5.0e-01`); `Cd = 1.234e-03`
behind a decoy at `t = 1`, with the column matched **by header name** and a file without
one **refused rather than guessed**; `y⁺ max = 987.654` on `hull` with an absent-patch
check so the filter cannot be inert; and **the age guard planted TWICE**, stale then fresh,
because a "pass" can also come from a checker that never looked.

**Both branches of every gate demonstrated on synthetic cases BEFORE the run**, because a
gate with one reachable branch is empty however clean its arithmetic: Gate C `PASS` /
fail / `BLOCKED`; Gate W `PASS` at `y⁺` 141.7, `GATE FAIL` at 412.9, `BLOCKED` on a
substituted wall function; S3 `PLATEAUED` at 0.13 % drift, `NOT PLATEAUED` at 12.2 %,
`BLOCKED` under 500 rows; S1 both ways.

---

## 8. WHAT A1b DOES NOT CLAIM

- **No grid convergence, no observed order, no GCI, no Richardson extrapolation** (§0).
- **No experimental agreement.** No title-verified SUBOFF force measurement is on disk
  (A1 §2.2: Huang et al. 1992, Liu & Huang 1998, Crook 1990 all **NOT OBTAINED**, `.url`
  stubs only, and rule 15 forbids treating a stub as a source). `CT_ref` is a **MANIFEST /
  ENGINEERING ANCHOR** and the tier is **CODE-VERIFIED with the disavowal "NOT
  experiment-validated"**.
- **No revival of A1.** A1's Gate M stands failed and unsatisfiable; no solver runs under it.
- **No claim resting on L1 alone**, which is not admitted (§2.1).
- A `PASS` on Gates C and W means **a source-faithful 3-D SUBOFF hull-plus-sail mesh exists,
  marches to `endTime`, and uses a wall treatment valid where it is applied.** That is all
  it means.

---

## 9. FREEZE BLOCK — cfd-SUPERVISOR, CHECK 4, UNDELEGATED

```
FROZEN AT COMMIT: ....................
DOCUMENT BLOB SHA: ....................
PRE-COMPUTE CONDITION (checked by ls, printed, not asserted):
   SOLVE_L1/ and SOLVE_L2/ carry no time directory, no log.simpleFoam,
   no solve_rc, no postProcessing/                                       [ ]
```
