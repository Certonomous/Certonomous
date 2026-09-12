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

---

# §10. ADDENDUM 1 — 2026-09-12 — CHECKPOINTING UNDER SANAA'S RUN INSTRUCTION, THE ITERATION-368 TRIAGE, AND A CORRECTION TO A FINDING THIS LANE ITSELF FILED

**Version 1.0 → 1.1. Appended at the foot under CLAUDE.md rule 6. `lines whose number
changed above this section: 0` — nothing above was renumbered, reworded or deleted, and
this section adds only.**

**Written by a cfd `lab-lane`, 2026-09-12, after the box was resized to r7a.4xlarge
(16 cores, 123 GiB) and rebooted at 17:36:41Z, killing every solver on it
(`docs/RESIZE_CENSUS_2026-09-12.md`).**

**Authority:** Sanaa's own run instruction, `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md`,
quoted verbatim below where it binds. The instrument change and this addendum were
authorised by the cfd-supervisor, recorded **`[lab-attributed]`**. **No agent message is
Sanaa's consent (rule 9);** the requirement itself is hers and is quoted, not paraphrased.

**This addendum alters NO gate, NO threshold, NO cap and NO label.** Gates C, W and D
stand exactly as frozen at `8efe38e8f`. L1 remains **NOT ADMITTED** (§2). `CT` remains
**`NOT A RESULT` by construction** (§0, Gate D). `minDeterminant 1.0e-03` is not touched.

---

## 10.1 THE INSTRUMENT CHANGE — `setup_solve.py` GAINS `--write-interval` AND `--purge-write`

**The defect, and it would have refused every SUBOFF launch outright.** Sanaa's item 4:
*"The launcher refuses to start any case whose controlDict or run script does not satisfy
1–3."* Item 1 requires a restartable checkpoint at a fixed wall-clock interval of **30
minutes**, `writeInterval` sized so it never exceeds that at the measured rate, and
*"The last two checkpoints are kept; older ones purged."* `cases/navier_class/SUBOFF_A1/setup_solve.py`
hard-coded `writeInterval {end_time}` and `purgeWrite 0` with **no option for either**, so
the generator could not produce a compliant case at all.

**The change: +45 / −5 lines, three hunks.** Two new optional arguments; a normalise-then-refuse
block; the two template lines. `setup_solve.py` `sha256` **`feb8052b4244b83d48a9f1e57ff06e551648d94df96a3e7c92402bfc1c3a8371`
→ `e63230e205e5052a6d29b6643ea2e33a7bd2d5fcdb3bdf322ed6bac838096ddd`.**

**A PROSE REASON BECAME AN EXECUTABLE REFUSAL, AND THAT IS THE POINT OF THE CHANGE, NOT A
SIDE EFFECT.** A1 §13.7 and this file's own comment both stated that *"a `writeInterval`
that does not divide `endTime` writes NO fields at all, which the completion rule reads as
an incomplete run."* While `writeInterval` was hard-wired to `endTime` that reason could
not be violated. **The moment it became a CLI option it could be** — a caller could satisfy
Sanaa's 30-minute ceiling and silently build a case that writes nothing and grades `NOT
COMPLETE` after 73 hours. The script now **refuses (exit 2)** a non-divisor, and refuses a
negative `purgeWrite`, before anything is written.

**BOTH BRANCHES DEMONSTRATED, AND THE NO-OP BRANCH DEMONSTRATED HARDEST.** Run on the real
`L0c` mesh (1,206,389 cells) into scratch, never into a graded tree:

| # | what was run | result |
|---|---|---|
| **A/B** | the **pre-change** script and the **post-change** script, same argv, **no checkpoint flags**, into two separate trees, compared with `diff -r` | **IDENTICAL IN EVERY FILE**, `system/controlDict` byte-for-byte included. The only difference in the whole tree is `SOLVE_MANIFEST.json`'s own `written_utc` (18:46:20Z vs 18:46:00Z) — the field whose job is to record wall-clock. **The default path is proven a no-op against the frozen behaviour, not asserted to be one.** |
| **C** | post-change with `--write-interval 50 --purge-write 2` | **exactly two lines move**: `writeInterval 3000→50`, `purgeWrite 0→2`. Nothing else in the case changes. |
| **D** | `--write-interval 7 --end-time 3000` (7 does not divide 3000) | **REFUSED, exit 2**, with the mechanism in the message. |
| **E** | `--purge-write -1` | **REFUSED, exit 2.** |
| **F** | after D and E | **neither refusal created a directory.** The refusal is before the first write, not a cleanup after one. |

**🔴 A CORRECTION TO §7 OF THIS DOCUMENT, REPORTED AND NOT REPAIRED (rule 6).** §7 states
the five instruments are *"all frozen at commit `05ca5550`"*. **That was already inaccurate
for two of them when it was written**, and `verification/runs/navier_class/SUBOFF_A1/GRADER_PIN.txt`
says so in its own closing note: `grade_suboff_a1.py` changed in `8efe38e8f` itself (+4/−1,
an explanatory string) and `setup_solve.py` changed post-compute in `5e7f618de` (+14, the
`forceCoeffs` `liftDir`/`dragDir` repair under `VERIFICATION_CHARTER` §2d.1). **This
addendum makes it a third state for `setup_solve.py` and says so here rather than editing
§7.** **The GRADING path is unaffected:** grading runs from the `sha256`-pinned
`GRADER_PINNED_8efe38e8f.py` (`41a41f02cf3242ed8ebd675ab78dbd2ba746d4d8ce9eff441ecd4aec7e62b0d6`),
and `setup_solve.py` is a **case builder, not a comparator** — it cannot reach a verdict.

---

## 10.2 THE CHECKPOINT VALUES, AND THEY ARE SIZED AGAINST THE **PESSIMISTIC** RATE ON PURPOSE

| level | cells | `writeInterval` | `purgeWrite` | at §6's registered rate | at this lane's measured rate | divides 3000? |
|---|---:|---:|---:|---|---|---|
| **L1** | 3,268,613 | **50** | **2** | 31.4 s/it ⇒ **26.2 min** | 14.22 s/it ⇒ 11.9 min | ✅ 60 writes |
| **L2** | 9,121,237 | **15** | **2** | 87.7 s/it ⇒ **21.9 min** | 39.68 s/it ⇒ 9.9 min | ✅ 200 writes |

**Both sized on §6's own registered figures, which are the SLOWER of the two rates
available** — §6 anchors on the worse, later MRF measurement (10 s/it at 01:15Z, not
4.085 s/it at 00:35Z, a **2.4× swing in forty minutes**). **Sizing on the slower rate is
the safe direction**: if the box runs faster, checkpoints fall closer together, never
further apart. The faster column is this lane's own measurement on **this case's own
predecessor** — `SOLVE_L1/log.simpleFoam`, `ExecutionTime` 5568.40 s at iteration 355 →
5639.51 s at iteration 360 = **14.22 s/iteration at 4 ranks**, taken from a contention-free
stretch, scaled by cell count for L2.

**🔴 THE MONITOR NUMBER THAT WOULD HAVE SIZED THIS WRONG BY MORE THAN 10×.**
`SOLVE_L1/WATCH.log` reports *"137.524 s/iteration measured over the run so far"*. **That is
a CUMULATIVE MEAN.** The instantaneous cost at the same moment was **1,900–20,190 s per
iteration**. Sanaa's rule says *"at the measured rate"* — a watcher's running average is not
that rate, and any lane sizing a 30-minute checkpoint from it gets an interval an order of
magnitude too long. **Recorded here because the defect is in the instrument, not in this
case.**

**`purgeWrite 2` cannot touch `endTime`.** `endTime` is always the last write, so `2985/`
and `3000/` (L2) and `2950/` and `3000/` (L1) survive, and **Gate C's clause "fields
`p U k omega nut phi` present at `3000/`" is unaffected.**

**A SIDE EFFECT THAT REPAIRS AN UNARMED GATE.** The `yPlus` functionObject is
`executeControl writeTime`. Under `writeInterval 3000` **no `y⁺` could exist before
iteration 3000** — `SOLVE_L1/postProcessing/yPlus/0/yPlus.dat` is a **two-line header with
no data rows**, which is precisely the §5 CLASS-2 condition under which **Gate W is
`BLOCKED`, never `PASS`**. Under the new intervals the first `y⁺` per patch lands at
iteration 15 (L2) / 50 (L1). Sanaa asked for *"y+ per patch after the first converged
solve"*; this is what makes that reportable at all.

**APPLIED TO `SOLVE_L2` IN PLACE, NOT BY REBUILD.** That case was already built and its
`polyMesh` is `sha256`-pinned; rebuilding would re-copy 9.1 M cells to change two lines.
The edit follows the directory's own existing precedent (`controlDict.PRE_REPAIR` /
`controlDict.REPAIR_DIFF.txt`, the `liftDir` repair): the as-built file is preserved as
`controlDict.PRE_CHECKPOINT_2026-09-12`, the two-line diff as
`controlDict.CHECKPOINT_DIFF.txt`, and the reasoning as `CHECKPOINT_REPAIR_NOTE.txt`. The
new values were **read back from disk**, not asserted. **`SOLVE_L1` is NOT edited** — see
§10.4.

---

## 10.3 🔴 A CORRECTION TO A FINDING THIS LANE FILED EARLIER TODAY, AND IT IS A CORRECTION AGAINST ITSELF

**WHAT THIS LANE REPORTED, AND IT WAS WRONG:** that `SOLVE_L1` ran 369 iterations under
`SUBOFF_A1_PREREGISTRATION.md`, whose §10 freeze block is blank and whose §5.1 bars a
launch — i.e. that a launch had occurred which the governing document forbade.

**WHY IT IS WRONG.** **A1 is not the governing document for that run. THIS ONE IS.** §1
above already records the cfd-supervisor's ruling that *"no solver launches under A1,
ever"*, and A1b was frozen at **`8efe38e8f`, 2026-09-12T01:34:37Z** — **before** the first
solver compute (the crashed attempt at 01:38:17Z, the live run at 01:46:28Z). §2 of this
document **declares L1 NOT ADMITTED**, and §2.1 then registers, in advance and with its
reasoning frozen, **why L1 is solved anyway** — four numbered reasons and an explicit
*"what would have made me refuse to solve L1"*. §3 names the runs as *"fresh `SOLVE_L1/`
and `SOLVE_L2/`"*. **The L1 launch was therefore authorised by a frozen pre-registration
that had already refused it admission and had already said so out loud. It is not a
departure and no disclosure of one is owed.**

**THE NARROWER FINDING THAT DOES SURVIVE, AND IT IS REAL.** **§9's FREEZE BLOCK IS BLANK
AT `HEAD`** — `FROZEN AT COMMIT: ....................`, `DOCUMENT BLOB SHA` blank, and the
pre-compute condition checkbox **unticked**. The freeze is asserted in the **commit
subject** (`8efe38e8f`, *"SUBOFF A1b FROZEN"*) and in `GRADER_PIN.txt`, **not recorded in
the block reserved for the supervisor's undelegated check-4.** Every commit on this box
carries one Ubuntu identity, so a commit subject cannot evidence who performed a personal
check. **What is owed is §9 being filled by the cfd-supervisor, not a new document.**

**WHY THIS LANE IS NOT DRAFTING THE NEW STANDALONE L2 ARM IT WAS ASKED FOR, AND THE CALL
IS THE SUPERVISOR'S.** The arm described — one level, L2 only, no family claim, gating on
L2's own limbs which it passes on every one, Gate D `NOT A RESULT` by construction, tier
CODE-VERIFIED with the disavowal, `y⁺` per patch, rule-4 completion including the age
guard — **is this document**, minus its L1 companion. Three facts, stated at equal
strength rather than argued to a conclusion:

1. **A third document would duplicate A1b's L2 limb** and would have to explain why A1b's
   own L2 was not used. A1 §13.3's warning cuts here in reverse: *"a rung invented to
   escape a gate is the gate not applying to itself."* Nothing is being escaped, and the
   shape is the same shape.
2. **Dropping L1 from A1b's run set is not free.** §4's *"reported DIFFERENCE"* `Δ =
   (CT_L1 − CT_L2)/CT_L2` is this registration's declared product. Removing L1 removes it.
   **After first compute that is a change to what the document claims, which an addendum
   may not make** (rule 2) — so it would require the new document, not an edit here.
3. **Solving only L2 costs 17,540 of the family's 23,820 registered core-min** — L1 is
   **26 %** of the spend and is already registered, already disclosed, and already
   labelled as bounding nothing.

> **THE RECOMMENDATION, OFFERED AS INPUT AND NOT ACTED ON: run A1b EXACTLY AS FROZEN —
> both levels — and fill §9. It needs no new registration, it discards nothing already
> paid for, and it is already the smaller satisfiable question the supervisor asked for.
> If the supervisor still wants an L2-only arm after reading this, that is his call and
> this lane will draft it; it is not drafted here because drafting it first would have
> made the duplication a fact before he could weigh it.**

---

## 10.4 THE ITERATION-368 STALL — TRIAGED UNDER §5's X3/S6, AND IT IS **NEITHER** OF THE TWO THINGS SANAA NAMED

Sanaa's instruction: *"Triage the L1 stall (pinned at iteration 368): read the residual
history and the pressure-solver iterations; classify plateau vs oscillation. A plateau with
the pressure solver at its cap is the wall-layer/mesh signature — fix the mesh, do not relax
the solver."*

**THE ANTECEDENT IS MEASURED FALSE, SO THE CONSEQUENT DOES NOT FIRE.**

| what was read | value | source |
|---|---|---|
| GAMG iterations for `p`, the three non-orthogonal correctors, iterations 366–369 | **5, 2, 1** | `SOLVE_L1/log.simpleFoam` |
| the cap they would have to be pinned at | **1000** | `/usr/lib/openfoam/openfoam2606/src/OpenFOAM/matrices/lduMatrix/lduMatrix/lduMatrix.H:125`, `static constexpr const label defaultMaxIter = 1000`; `lduMatrixSolver.C:205` `readIfPresent("maxIter", ...)` — this case's `fvSolution` sets no `maxIter`, so the default IS the cap |
| **so the pressure solver sat at** | **0.5 % of its cap** | — |
| `Ux` initial residual, iteration 300 → 369 | **5.43e-07 → 2.06e-07**, falling | same log |
| `time step continuity errors`, `sum local` / cumulative at 368 | 2.07e-09 / −1.28e-07, stable | same log |
| `bounding k` at 368 | min **−5.05e-06** against max 0.254 — **0.002 %**, round-off level; `bounding omega` stopped by iteration ~40 | same log |

**MULTI-WINDOW DRIFT, COMPUTED AT ONE INSTANT, BECAUSE ONE WINDOW IS NOT EVIDENCE.**
Linear-fit drift of `Cd` across the last **10 / 20 / 30 / 50 / 100 / 150 / 200** iterations:
**+0.011 / +0.025 / +0.041 / +0.081 / +0.244 / +0.574 / +1.225 %**. **Monotone in magnitude
AND single-signed at every window**, with `Cd` **strictly increasing** over the last 100
(all 99 differences positive) and the mean per-iteration relative increment decaying
**6.83e-05 → 1.67e-05** between the 200- and 50-iteration windows.

> **CLASSIFICATION: NEITHER A PLATEAU NOR AN OSCILLATION. It is an asymptotic approach from
> below, still converging, with the linear solvers idle.** An oscillation would scramble the
> sign across windows; a plateau would flatten the drift toward zero at every window
> together. Neither happened.

**WHAT DID HAPPEN: A WALL-CLOCK COLLAPSE, NOT A NUMERICAL ONE.** `ClockTime` per iteration
**70 s at iteration 360 → 9,361 s at 367 → 20,190 s at 368**, against `ExecutionTime` of
**14.22 s** per iteration in the clean stretch. `WATCH.log` records it advancing
366→367→368 across eight hours in ~1,900 s steps: **crawling, never stuck.** Iterations 367
and 368 **alone** consumed **1,970 of the run's 3,295 gross core-min — 59.8 % of the entire
spend for 0.54 % of its iterations.** The cause is on record independently: the old box's
`MemAvailable` reached **1.42 GiB**, and this family's own `SOLVE_L2.gatedlaunch.log` logged
**251 consecutive `GATE CLOSED` readings**, the last 41 at `available=0 GiB`.

> **NO MESH CHANGE AND NO RELAXATION CHANGE IS MADE TO EITHER LEVEL ON THIS EVIDENCE.**
> L1's `GATE FAIL` on M-d (**8.6227045e-04** against **1.0e-03**, one cell in 3,268,613)
> stands exactly as §2 records it and is **not** what stalled this run. Changing the mesh
> because a run was starved would be a second action on the wrong state.

**`SOLVE_L1` IS LEFT BYTE-UNTOUCHED** — no checkpoint edit, no repair, nothing — because it
is the sole artifact every number above cites. A relaunch goes to a **fresh `SOLVE_L1_R2/`**,
which is how monitor stop S5 is satisfied: *"A guard is satisfied by MOVING the case, never
by disabling the guard"* — and here by leaving it and building a sibling, so the evidence
survives too.

**NO CHECKPOINT EXISTS AND NEITHER LEVEL CAN RESUME.** `SOLVE_L1/processor*/` hold only
`0/`; `writeInterval` was 3000 so the first field write was to have been at `endTime` and
never fired. `docs/RESIZE_CENSUS_2026-09-12.md` row 6 reaches the same verdict
independently. **369 iterations and ~3,295 gross core-min are lost, and §10.1–10.2 are
exactly the change that stops it recurring.**

---

## 10.5 `y⁺` — THE TWO WALL PATCHES ARE IN **DIFFERENT REGIMES**, WHICH IS WHY GATE W REPORTS PER PATCH

Registered arithmetic carried forward from A1 §13.5, unaltered: hull **50.0** (L1) / **27.9**
(L2) at the cell centre, estimated local maxima 87 / 48; sail **9.6** / **5.4**.

A parallel cfd finding on DrivAer measured `nutUSpaldingWallFunction` and `nutkWallFunction`
to be **the same function above `y⁺ ≈ 30`** — 0.44 % apart at `y⁺` 232, 0.15 % at 482, 0.12 %
at 557 — diverging only **below** it: 11 % at 30, 88 % at 15. **Applied here that splits by
patch, and the split is the reason Sanaa asked for `y⁺` per patch:**

- **The hull sits in the log layer.** Blending buys **nothing** there; `nutkWallFunction`
  would give the same answer. A high-`y⁺` problem, if this case had one, would not be fixed
  by blending.
- **The sail sits in the buffer layer and below** (9.6 and 5.4). **That is exactly where the
  blended form earns its keep**, and it is what Sanaa's *"so y+ in the buffer zone is
  tolerated"* describes.

**Both caveats stated, neither softened:** the equivalence holds under **local equilibrium**
and fails in separated regions, so the **stern taper and the sail wake** are outside it; and
the local-maximum column is a **√3 estimate with its mechanism named, not a measurement.**
**No measured `y⁺` exists for either level yet** (§10.2), so nothing above is a Gate W
result — Gate W is `BLOCKED` until armed.

**THE WALL TREATMENT IS ALREADY THE BLENDED ONE AND HAS BEEN SINCE THE FIRST BUILD.**
`0/nut` at **both** `SOLVE_L1` and `SOLVE_L2` carries `nutUSpaldingWallFunction` on `hull`
and `sail` — read from disk, not inferred. **Applying a "blended wall treatment arm" to
SUBOFF is a no-op; it is already what §3 registered.**

**🔴 AND A GEOMETRIC FACT THAT DELETES THREE REQUESTED QUANTITIES.** `constant/polyMesh/boundary`
lists exactly **`inlet outlet farfield symm hull sail`**. **THERE ARE NO FINS AND NO STERN
APPENDAGES.** A1/A1b is hull **plus fairwater**. So *"layer coverage on the fins"*, *"cells
across the appendage roots"* and the *"hull/fin split"* **have no referent on this geometry**
and are reported as inapplicable rather than answered. A `hull`/`sail` split **is** available
and needs one extra `forceCoeffs` per patch — the single frozen block currently covers
`(hull sail)` together.

---

## 10.6 THE SOURCES, RE-CHECKED RATHER THAN INHERITED — AND WHAT CANNOT BE REGISTERED BECAUSE OF THEM

Sanaa's instruction asks for *"reference = Roddy 1990 captive-model forces and moments (band
per derivative written first), Huang 1992 surface pressure at α = 0 as the anchor"*. §8
already says no title-verified SUBOFF force measurement is on disk. **This lane checked the
claim instead of inheriting it**, per rule 15:

- The off-repository reference pack's `PDFs/CASE_1_DARPA_SUBOFF/` directory contains
  **exactly one file, and it is `README.txt`** — a bibliography of twelve citations. **There
  is no PDF behind any of them.**
- **Roddy 1990** (DTRC/SHD-1298-08) and **Huang et al. 1992** exist only as `.url` link
  stubs, as do Crook 1990, Liu & Huang 1998, Toxopeus 2008 and Gertler & Hagen 1967 — so
  even the **derivative conventions** for `Z_w` and `M_w` are not held from a source.
- The **only** title-page-verified SUBOFF source on the box remains **Groves 1989,
  DTRC/SHD-1298-01** (institution, report number, March 1989, title and authors all read
  from the document). Searching it for drag / resistance / force-coefficient content
  returns **nothing** — it is a **geometry** report.

> **CONSEQUENCE, STATED AS A REFUSAL RATHER THAN A DIFFICULTY: the validation registration
> Sanaa specified CANNOT BE WRITTEN AS SPECIFIED. A band per derivative referenced to a
> paper the lab does not hold would be fabrication, and rule 15 forbids treating a stub or
> a third party's bibliography as a source.** What **is** writable is the α-sweep **method**
> — α = −12, −8, −4, 0, +4, +8, +12; `Z` and `M`; derivatives by linear fit over |α| ≤ 8;
> neutral point `x_np/L = −M_w/Z_w` — at tier **CODE-VERIFIED with the disavowal "NOT
> experiment-validated"**, which is the ceiling §8 already sets. **That is a reporting
> registration, not a validation one, and it must never be presented as the latter.** Two
> geometry notes for whoever drafts it: a pitch sweep **preserves** the `z = 0` symmetry
> plane, so the half model is valid and the frozen `liftDir (0 1 0)` / `CmPitch`-about-`z`
> are already the right quantities; and the hull/fin split does not exist (§10.5).

---

## 10.7 WHAT §10 DOES NOT DO

- It does **not** move a gate, a threshold, a cap or a label. Gates C, W and D, `minDeterminant
  1.0e-03`, L1's `NOT ADMITTED`, and `CT`'s `NOT A RESULT` all stand as frozen at `8efe38e8f`.
- It does **not** revive A1, narrow A1's Gate M, or relabel anything to reach a verdict.
- It does **not** freeze this document. **§9 is still blank and is still the cfd-supervisor's,
  personal and undelegated.**
- It does **not** launch anything. Nothing here started a solver; the two queue entries
  prepared alongside it sit in `verification/queue/cfd/held/`, which the daemon does not poll.
- It does **not** send, file, upload or register anything outside this box (rule 7).
