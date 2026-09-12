# `MP_A5` — A5 U-BEND, **3D INCOMPRESSIBLE MULTIPOINT** PRESSURE-LOSS MINIMISATION OVER THREE INLET VELOCITIES

**Drafted 2026-09-12 by a `lab-lane` on the dafoam-supervisor's brief, under Sanaa's directive of
this session, her words verbatim: _"dafoam should notforget about the multipoint optimization (both
compressible and incompressible)"_ — restating her 2026-08-31 ask, quoted verbatim inside
`cases/dafoam/ladder-a/A2/curriculum_SO3D/PREREGISTRATION.md`: _"we need to find a solution for
multipoint optmization (both compresisble and incompressible"_.**

**SUBMISSIONS PARKED.** Nothing in this item is sent, emailed, filed, uploaded, registered, posted
or commented anywhere (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**THIS LANE HAS RUN NO COMPUTE AGAINST THIS ITEM.** The run root
`/home/ubuntu/certonomous-runs/CURRICULUM-MP_A5-a5-ubend-multipoint` **does not exist**, verified by
`ls` at 2026-09-12 06:17:28 UTC (`ls: cannot access …: No such file or directory`), and no
`mpa5_out.json` exists anywhere on this box. Every gate, threshold, band, cap-position and label
below is fixed **before** the first container starts.

**THE GRADING PATH IS IN THIS COMMIT.** `mpa5_grade.py` is committed together with this file, not
after it, so there is no window in which a gate could be chosen to fit an answer. At the freeze:

| file | md5 at freeze |
|---|---|
| `cases/dafoam/ladder-a/A5/curriculum_MP_A5/mpa5_grade.py` | `2624c493f11fce8a18ed786c8004c340` |
| `cases/dafoam/ladder-a/A5/curriculum_MP_A5/mpa5_run_script.py` | `d52a10df24d6c40d00aee7c94ca56056` |
| `cases/dafoam/ladder-a/A5/curriculum_MP_A5/mpa5_stage_and_run.sh` | `ebdaa2324fdde5ed175e858e1897d2da` |

Before grading, the frozen file **is** the file that ran is verified by hashing each of the three
against its committed blob at the freeze sha.

---

## 0. WHAT GAP THIS CLOSES, AND WHAT IT DOES NOT

Sanaa's multipoint ask has **two halves**, and one of them was already delivered:

| half | item | status on disk, verified this session |
|---|---|---|
| **compressible multipoint** | `D6R2`, A2 MACH wing, `DARhoSimpleFoam`, 3D | **RUNNING** (`d6r2_O_mp_20260912T033601Z_2772281`). Not this item's business. |
| **incompressible multipoint, 2D** | `SO3`, A1 NACA0012, `DASimpleFoam`, 3 AoA scenarios, 4,032 cells | **DELIVERED.** Chain `COMPLETE declared=7 executed=7`, every arm `rc=0`, frozen comparator verdict `PASS`, `EXIT: Optimal Solution Found.` in `O-P/opt_IPOPT.txt`, `so3_xopt.json` `J_final = 0.018283196351550565`. Grader md5 `0ac111ef144a62111e36f676e8114af1` **equals its committed blob at HEAD**. Its only limit is that it is **2D**. |
| **incompressible multipoint, 3D** | — | **THE GAP. This item.** |

**What this item is NOT.** It is not a grid-convergence study and **no GCI is claimed**; A5's grid
triple (4,800 / 38,400 / 307,200) remains unregistered, exactly as `A5P2/RESULTS.md` leaves it. It
is not a validation against experiment. It is one 3D incompressible multipoint optimisation, graded
against pre-registered gates.

---

## 1. THE PRECONDITION — A 3D INCOMPRESSIBLE PRIMAL THAT CONVERGES, AND WHY IT IS THIS ONE

The dafoam-supervisor's standing rule for this item is that **no optimisation is registered on top of
a primal that cannot converge** — the failure mode that cost this family D6, D6R and D6RF3. The
precondition was therefore checked on disk before this document was written.

| candidate | cells | solver | 3D? | did its primal reach an accept floor? | mesh / registration on disk? |
|---|---|---|---|---|---|
| **A5 U-bend, `UBend_Channel`** | **4,800** | `DASimpleFoam`, SA | **YES** — `constant/polyMesh/boundary` carries `inlet`/`outlet` patches, `ubend`/`ubendup` walls and a **`symmetry`** plane; **zero `empty` patches** | **YES, at the `P2` setting.** `A5P2/RESULTS.md`: `nNonOrthogonalCorrectors 0→2` takes `p` initRes from `2.056815e-04` to **`1.448577e-08`**, a factor of 14,199, reproduced independently in A5P and A5P2 to the printed digit. **Named caveat, registered here and not discovered later:** `primalMaxRes` sits on **`nuTilda` at 3.62e-04**, not on `p`; `nuTilda` does **not** reach 1e-8 on this case. | **YES** — `/home/ubuntu/certonomous-runs/W5-regrade/a5pl_stock`, plus two completed optimisations (`D9`, `D9successor`) and two plateau ladders (`A5P`, `A5P2`) |
| A4 Ahmed body, 25° slant | 2,777 (adjoint) / 45,760 (primal) | `DASimpleFoam`, kΩSST | YES — zero `empty` patches | **NO, not cleanly.** `primalMinResTol 1e-4` (loose); the **0.2510 frontal-area CD is WITHDRAWN** because the omega field diverged while the normalised residual read converged; a **22.05 % primal gap** vs the lab's own `simpleFoam` baseline is **UNEXPLAINED** (`PRIOR_WORK_INVENTORY.md` §1e) | mesh on disk at `/home/ubuntu/certonomous-runs/A4-ahmed-body/{coarse,fine}` |
| naca0015 sail | 63,920 (coarse) | `DASimpleFoam` | YES — zero `empty` patches | **UNRECORDED.** `primalMinResTol 1.0e-8` is set in its runScript, but this lab holds **no convergence record** for it — the sail appears only as a gradient regrade row (PASS 4.52 % shipped / 0.0246 % patched). No README, no curriculum record, no frozen registration. | `cases/dafoam/work_sail/naca0015_sail_{coarse,medium,full}` |
| A3 ONERA M6, A2 MACH wing, A6 CRM | — | `DARhoSimple*` | YES | — | **compressible — outside this item by construction** |

**A5 is the choice, and it is the only honest one.** It is the sole 3D incompressible case in this
lab that has (a) a measured, reproduced primal accept state, (b) two optimisations that already ran
to an endpoint on it, (c) a working mesh-quality constraint with a measured endpoint, and (d) a
decomposition-clean record (`D-B` reach table: A5 CLEAN at ~1e-04). A4 fails (a); the sail has no (a)
at all.

### 1.1 The accept floor this item registers, and the honesty it is bought with

`A5P2/RESULTS.md` measured that across four valid arms the objective `TP1−TP2` spans
`52.34509736 … 52.34619774` — a range of **2.1e-05 relative** — while `p` initRes spans
`1.449e-08 … 3.376e-04`, **a factor of 23,309**. *The pressure residual moved four orders of
magnitude and the answer did not move.* The registered prediction that `TP1−TP2` would stay within
`1e-05` of the control was **confirmed at 8.0e-08 relative**.

**So the accept floor for this item is registered on `p`, at `1.0e-06`** — four decades above the
measured `1.449e-08` and two decades below the old plateau — **and the fact that `nuTilda` does not
reach 1e-8 is registered as a limitation of this item, before compute, with the measurement that
makes it tolerable printed beside it.** No later reading may present the `nuTilda` residual as a
discovery.

---

## 2. THE OPTIMISATION PROBLEM, IN FULL

### 2.1 The scenarios and their weights — REGISTERED

| scenario | inlet `U0` (m/s) | relation to the case's own `0/U` | Re relative to centre | **weight** |
|---|---|---|---|---|
| `point0` | **6.30** | 0.75 × 8.4 | 0.750 | **0.25** |
| `point1` | **8.40** | the case's own `internalField uniform (8.4 0 0)` | 1.000 | **0.50** |
| `point2` | **10.50** | 1.25 × 8.4 | 1.250 | **0.25** |

`nu = 1.5e-5` (`constant/transportProperties`), unchanged across scenarios, so the velocity ratio
**is** the Reynolds ratio: the envelope spans **1.667×** in Re. Weights sum to exactly 1.0 and
`mpa5_run_script.py` asserts it at import; a weight set that does not sum to 1 aborts the run rather
than silently rescaling the objective.

**The physical reading:** a turbine-blade internal cooling duct that must run across a flow-rate
envelope. The registered duty cycle is centre-weighted — half the duty at the design flow, a
quarter at each flank.

### 2.2 The composite objective — REGISTERED

```
J  =  Σ_i  w_i · (TP1_i − TP2_i) / n_i
```

* `TP1_i − TP2_i` is the total-pressure loss inlet-to-outlet at scenario *i*, the same functional
  D9 and D9successor optimised, carried unchanged.
* `n_i` is the **baseline** pressure loss at scenario *i*, **measured in arm `B` of this chain at
  shape = 0**, read by the launcher from `B/mpa5_out.json` and written to `norm.json` before arm `O`
  stages. **No other source for `n_i` is admissible.** The RULE is frozen here; the NUMBERS are
  measured by the run.
* Therefore **`J` at the baseline design is exactly 1.0 by construction**, and gate **G-J0** grades
  that identity. A mis-assembled objective cannot pass silently.
* The weights and normalisers are **compiled into the `ExecComp` expression string**, and the exact
  string is written into every record as `obj_expr`; gate **G-EXPR** rebuilds it from the registered
  weights and the record's own normalisers and compares **character for character**. A changed weight
  cannot leave a stale coefficient anywhere.

### 2.3 Design variable, constraint, optimiser — carried, not re-derived

| element | value | provenance |
|---|---|---|
| design variable | **`shapexUpper` only**, 27 components, bounds ±0.04, scaler 25.0 | byte-identical to `D9`/`D9successor`. It is the **only** A5 total derivative this lab has FD-verified (PASS patched, 2.768 % aggregate, 0 sign flips, np=1). The other five DV groups stay declared-but-**commented** so the departure reads as a diff. |
| constraint | **`point1.aero_post.nonOrtho ≤ 70.0`, scaler 1.0** — `meshQualityKS`, `allCells`, `coeffKS 1.0`, metric `nonOrthoAngle` | byte-identical bound and scaler to `D9successor`, which measured a raw endpoint `maxNonOrth` of **69.2937** under it against the case's own `checkMeshThreshold { maxNonOrth 70; }`. Taken from **one** scenario because all three deform the **same** mesh from the **same** shared geometry component — gate **G-NONORTHO-IDENTITY** proves the three KS values agree to `1e-09`, which is what makes that legitimate. |
| optimiser | **SLSQP** via `pyOptSparse`, `ACC 1e-5`, `MAXIT 30` | `D9`/`D9successor`. `MAXIT` is an **optimiser convergence setting, not a resource cap**: it bounds how many majors SLSQP is willing to take, exactly as `ACC` bounds its tolerance. Nothing in this item stops a running solver. |
| image | **`dafoam-idwarp-rot:v1`**, `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | the patched IDWarp is the one bought; **stock is GATE FAIL on A5's `OBJ.val wrt shapexUpper` (2 sign flips)**, so an optimiser on the stock gradient would be driving on a broken derivative |
| ranks | **np = 1 throughout** | two independent measured reasons: A5's np=1 re-verification localised the idx16 `check_totals` anomaly to the np=4 FD path; and defect **D-B** (the parallel reverse-AD operator is not the transpose Jacobian under decomposition) is structurally absent at one rank. **It is also the smallest possible footprint on a box whose load average read 48.55 on 16 cores at registration time.** |
| primal | **`nNonOrthogonalCorrectors 0 → 2`** in `system/fvSolution` SIMPLE (the A5P2 `P2` setting), applied by the launcher and **read back**; a staged arm that does not carry `2` aborts the chain | `A5P2/RESULTS.md` |

### 2.4 The arms

| # | arm | task | what it buys |
|---|---|---|---|
| 1 | **`B`** | `run_model`, shape = 0, **no** `normFile` | the three baseline `dP_i` (which become `n_i`), the baseline raw `checkMesh` `maxNonOrth`, and the per-scenario primal convergence that **G-CONV** grades |
| 2 | **`O`** | `run_driver`, SLSQP, all three scenarios, **with** `normFile` | **the buy.** The multipoint optimisation itself. Writes `mpa5_hist.sql`, `opt_SLSQP.txt`, `OptView.hst` and the endpoint `shapexUpper`. |
| 3 | **`E`** | `run_model` at the endpoint DV, all three scenarios, **with** `normFile` | the endpoint `dP_i` that **G-MP1** and **G-SCEN-ALL** are computed from, and the endpoint raw `maxNonOrth` that **G-MESH** grades |

Arm trees are **never deleted**; `writeMinorIterations: True` leaves the field time directories on
disk, so arm `E` is the filmable endpoint and arm `B` the filmable baseline.

---

## 3. THE GATES — FIXED HERE, BEFORE COMPUTE

Verdict vocabulary is `CLAUDE.md` rule 1 and nothing else.

| gate | what it reads | threshold / band | PASS means |
|---|---|---|---|
| **G-RULE4** (per arm) | ledger `rc`, an `End` line, the record's presence, the **age guard** (record newer than that arm's own `0/U`), no fatal token | all five clauses | the arm is done. Any clause failing → **`NOT A RESULT`** for that arm and for the item. |
| **G-CONV** (arms `B`, `E`; per scenario) | the **last `p initRes:`** in each of the three primal segments of the arm log | **`< 1.0e-06`** | every operating point's primal reached the registered accept floor. Arm `O` is **REPORTED, never gated** — its endpoint is re-evaluated in `E`, which is gated. |
| **G-EXPR** | `obj_expr` in the `O` record | character-for-character equal to the formula rebuilt from the registered weights and the record's own normalisers | the objective actually assembled is the objective registered |
| **G-J0** | arm `B`'s own `dP` triple, recomputed by the comparator | **\|J₀ − 1\| ≤ 1e-06** | the normalisation is the registered one |
| **G-MP1** *(headline)* | arm `E`'s `dP` triple ÷ arm `B`'s normalisers, **recomputed by the comparator** — the instrument's own `OBJ_val` is reported beside it and is **not** what is graded | **`J_end ∈ [0.94, 0.98]`**, i.e. a **2 % – 6 %** composite weighted pressure-loss reduction | the multipoint buy landed inside its registered band |
| **G-SCEN-ALL** | arm `E` vs arm `B`, per scenario | **every** scenario's `dP` falls | multipoint's whole claim. One operating point going backwards is **`GATE FAIL`** even if the weighted sum falls. |
| **G-MESH** | the **raw** `checkMesh` `Mesh non-orthogonality Max` in arm `E`'s primal-startup block (D9successor's proven mechanism) | **`≤ 70.0`** | the constraint held the endpoint inside the case's own envelope |
| **G-NONORTHO-IDENTITY** | the three KS values in arm `E`'s record | spread **`≤ 1e-09`** | the three scenarios share one deformed mesh, so constraining `point1` alone binds all three |

**Verdict order, registered:** G-RULE4 first — a failed arm is `NOT A RESULT` whatever any number
says. Then the gates: any gate that cannot be evaluated on the artefacts present → `NOT A RESULT`;
else any gate outside its band → `GATE FAIL`; else `PASS`.

### 3.1 The planted-zero controls — the comparator REFUSES, it does not degrade

`CLAUDE.md` rule 3. Before any gate is evaluated:

* **CONTROL A** — `PLANT = 1.234e-03` is written into a **scratch copy** of arm `B`'s log, replacing
  the **last `p initRes:` line by line index** (never a regex-replace-all), and read back through the
  **same** reader. If the reader cannot see it, **exit 2**.
* **CONTROL B** — the opposite plant: `1.0e-02`, a value that **must fail** G-CONV's `1e-06` floor.
  If the gate does not read it as above the floor, the gate is blind in the passing direction and the
  comparator **refuses**. A reader that always passes is as blind as one that always returns zero.
* **CONTROL C** — `PLANT` is written into `dP[0]` of a scratch copy of arm `B`'s JSON record and read
  back through the same reader. If it cannot be seen, **exit 2**.

**Exit status is not the verdict.** `exit 0` = a verdict was produced (which may be `GATE FAIL` or
`NOT A RESULT`). `exit 2` = **REFUSED**, and a refusal is never degraded into a verdict.

---

## 4. THE REGISTERED PREDICTIONS — WRITTEN BEFORE THE RUN, FALSIFIABLE

**P-1 (the buy).** `J_end ∈ [0.94, 0.98]` — a **2 % – 6 %** composite reduction. Basis: D9's
single-point run moved `OBJ 52.34521691559307 → 50.27935096533333` (**3.947 %**) and D9successor's
constrained run moved `52.34522 → 50.04350` (**4.40 %**). A weighted three-point objective on the
same DV group and the same bounds should land in the same neighbourhood, a little worse than either
single-point figure because one shape must now serve three operating points.

**P-2 (the discriminating negative — and I expect to be right, which is why it is worth registering).**
**`TRIVIAL_MULTIPOINT`**: the multipoint endpoint will sit within **l2 = 0.02** of D9successor's
single-point endpoint (`/home/ubuntu/certonomous-runs/CURRICULUM-D9SUCCESSOR-a5-ubend-opt/opt_dv.json`,
recorded endpoint `l2 = 0.1622`), i.e. within ~12 % of the single-point endpoint's own norm. Reason:
the three Reynolds numbers span only **1.667×**, the flow stays fully turbulent and attached-then-
separated in the same places, and a pressure-loss optimum in that regime is close to Re-independent.
**Both outcomes are results and G-TRIV never converts a PASS into a GATE FAIL** — it is reported
beside the verdict. If it comes back `NON_TRIVIAL_MULTIPOINT`, that is the more interesting answer
and my prediction is falsified in the informative direction.

**P-3 (the constraint).** `G-MESH PASS`, raw `maxNonOrth ≤ 70.0`, because D9successor measured
**69.2937** under the identical constraint and this item's DV bounds are identical.

**P-4 (convergence).** `G-CONV PASS` on all three scenarios in both `B` and `E`, with `p` initRes in
the `1e-08` decade, because A5P2 measured `1.448577e-08` at this exact setting and reproduced it
independently in A5P.

---

## 5. COST — REPORTED, AND **NO CAP OF ANY KIND**

**NO CAP OF ANY KIND.** Sanaa's fourth NO-CAP ruling, 2026-09-12, directive #17: **no run is stopped
by a time or budget cap, on any team.** This item registers **no** `timeout`, no `docker stop`
deadline, no launch budget, no core-minute guard, no cumulative stop and no watchdog that can signal.
The launcher asserts at start-up that no executable `timeout` wrapper exists in its own text and
aborts if one has grown back. **Core-minutes below are a REPORTED ESTIMATE; they stop nothing.**

**Memory containment is KEPT and is not a cap.** `--memory=3g --memory-swap=3g --oom-score-adj=500`
stays on every container. On a shared 16-core box with four sibling runs live, removing it would let
this item OOM-kill a peer's solver.

**The estimate, from measured bases, each cited:**

| component | basis | core-min |
|---|---|---|
| one converged U-bend primal at the `P2` setting | `A5P2-ubend-plateau/ledger.txt`, arm `P2`: `wall_s=91 core_min=6.067` | **6.1** |
| arm `B` — three primals | 3 × 6.1 | **18.3** |
| arm `O` — 30 majors × 3 scenarios × (primal + adjoint) | `D9`: 46.77 core-min over 47 majors × 1 scenario ≈ **1.0 core-min / major / scenario** at `nNonOrth=0`; the `P2` setting multiplies the primal by 91/36 = **2.53×** → ≈ 2.5 core-min / major / scenario | **≈ 225** |
| arm `E` — three primals | 3 × 6.1 | **18.3** |
| **TOTAL REGISTERED ESTIMATE** | | **≈ 262 core-min** (4.4 core-h) |

**`cost_basis`: DERIVED, NOT MEASURED.** `$0.22` at the owner-stated `c7a.4xlarge` rate of
`$0.0513/core-h`. **The box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5), so every
dollar figure in this item is reported-by-owner and derived, never measured.

**Contention disclosure, measured at registration.** `uptime` at 2026-09-12 06:09 UTC read **load
average 48.55 on 16 cores** — roughly 3× oversubscribed, with `d6r2_O_mp`, `d6rf11_F_probe` and two
further containers live. Core-minutes are wall × ranks, so the **actual** will inflate roughly with
contention and the ratio actual/predicted is expected to exceed 1. That inflation is **contention,
not misprediction**, and the completion report will attribute it that way per `CLAUDE.md` rule 12,
with the row landing in `docs/COST_CALIBRATION.md`.

**Ranks chosen, and why.** np = 1, one core, `--cpuset-cpus` pinned to a single core and the
placement **read back** from the process (`sched_affinity` in every record). This is the smallest
footprint that can run the item, chosen deliberately because four sibling runs are live. **No
sibling is reniced, re-pinned or disturbed.**

---

## 6. INTEGRATION RISKS, NAMED BEFORE THE RUN

1. **Three `DASimpleFoam` solver instances in one process on one case directory.** This is SO3's
   proven construct on the **same solver** (`DASimpleFoam`, A1 incompressible, three scenarios,
   `EXIT: Optimal Solution Found.`), transplanted from a 2D external case to a 3D internal one. SO3's
   own notes record time-directory renaming between scenarios. **If it fails here, the arm is
   `NOT A RESULT` and the crash is triaged as a finding, not papered over.**
2. **`primalBC` `U0` on a `fixedValue` inlet.** The U-bend's `0/U` inlet is `fixedValue` with
   `value $internalField`; DAFoam's `primalBC` `U0` override is the mechanism the naca0015 sail case
   uses on its `farfield` patch (`work_sail/naca0015_sail_coarse/runScript.py:48`). If the override
   does not land, the three scenarios would be **identical**, and gate **G-J0** would still read 1.0
   — so the detection is **G-SCEN-ALL** plus the three recorded `dP_i`, which must differ; a
   completion report that shows three equal `dP_i` is reporting a failed override, not a result.
3. **The `nuTilda` residual.** Registered as a limitation in §1.1, with the measurement that makes it
   tolerable printed beside it. It is not a discovery available to a later reading.

---

## 7. WHAT THIS ITEM MAY NOT DO

* It may not alter, renice, re-pin or inspect-and-modify any sibling run.
* It may not delete an interrupted run tree; a run directory that already exists is **evidence**, and
  the launcher refuses rather than clearing it.
* It may not edit any frozen file. A departure lands as a dated amendment appended at the foot with a
  version bump.
* It may not be sent anywhere. **SUBMISSIONS PARKED.**

---

*`MP_A5` v1.0, 2026-09-12. Frozen with its grading path in one commit.*

---

## ADDENDUM 1 — 2026-09-12, after arm B of the first launch failed at 56 s

**Lines whose number changed above this section: 0.** No gate, threshold, band, label, prediction,
weight, scenario or grading-path file is altered by this addendum. `mpa5_grade.py` is **byte-identical**
to its frozen state, md5 `2624c493f11fce8a18ed786c8004c340`. This is a **staging/launcher repair**
under `CLAUDE.md` rule 2's repair clause, disclosed here rather than made silently.

### A1.1 What happened, measured

Arm `B` of the launch stamped `20260912T062033Z_2937429` exited `rc=1` at 56 s (0.9333 core-min) with

```
pyDAFoam Error: /mnt/0.0001 already exists, moving failed!
  pyDAFoam.py:1543 in renameSolution(self.nSolvePrimals)
```

**The physics before the crash was healthy:** `p` initRes had reached `9.596471842383963e-07` in 44
steps — the 1e-07 decade, tracking registered prediction **P-4**. The case is not the problem.

### A1.2 Root cause — and a correction to the first triage

**This is exactly the integration risk §6 item 1 of this document registered before compute.** Three
`DASolver` instances shared **one** case directory; each carries its own `solution_counter`; each
renamed its converged solution to the same `0.0001`. `point0` renamed and succeeded, `point1`
collided and raised. It is the verbatim SO-3aR failure recorded at `so3_runScript.py:253-277`.

**A first triage attributed this to stale time directories copied in from the source tree and to a
cold-start guard that failed to see them. The disk refutes both halves, and the record says so:**

* `ls -d /home/ubuntu/certonomous-runs/W5-regrade/a5pl_stock/[0-9]*` returns **only `0` and
  `0.orig`**. There are no stale time directories in the source tree and none were copied.
* `B/0.0001` and `B/1000` are **root-owned** with mtimes **06:21:10** and **06:21:25**, i.e. written
  by the container **during** the run — 24 and 39 seconds **after** the guard printed
  `COLDSTART_PROVED` at staging (`B/0` mtime 06:20:46). **The guard's assertion was true when it was
  made.** The predicate `^[0-9]+(\.[0-9]+)?$` already matched decimal names; it had nothing to see.

Cause class **BOOKKEEPING/INSTRUMENT**, not upstream and not physics. `MP_A5` was derived from
`D9successor`, which is **single-point** and therefore never needed the isolation, so the isolation
was never carried in. A2's `D6R` has carried the cure since it was written; `SO3` ported it to A1.

### A1.3 The three repairs

1. **`MPA5-4` / `MPA5-L5` — per-scenario `run_directory` isolation, the actual root cause.** One
   full case tree per operating point at `mp0/ mp1/ mp2/`; each builder gets
   `run_directory=RUN_DIRS[sc]` and `gridFile=os.path.join(os.getcwd(), RUN_DIRS[sc])`, so no two
   `DASolver`s and no two IDWarp instances address one directory. `RUN_DIRS` is **derived from
   `SCENARIOS`, never spelled out** — a hand-written map is one more call site of the scenario label,
   and a scenario added with no row would fall back to the shared directory, which is the failure
   being repaired. The run script asserts the map is total and injective; the launcher **reads the
   names out of the run script's own text** and refuses if they do not derive. The P2 primal setting
   is now applied and read back in the arm root **and in every per-scenario copy**, because each
   `DASolver` reads its own `system/`.
2. **`MPA5-L6` — the cold-start guard is now shown able to refuse.** The guard was truthful, but a
   guard never shown able to fail is not evidence, exactly as a zero from a reader never shown able
   to see a non-zero is not evidence (`CLAUDE.md` rule 3). `prove_time_dir_guard` runs **before any
   staging**: it plants `0.0001` and `1000` in a scratch tree and **requires the predicate to name
   both**, and requires a clean tree to read silent. Driven standalone before relaunch:
   `GUARD_CONTROL_PASSED: planted 0.0001 and 1000 were both NAMED [0.0001 1000 ]; a clean tree read
   silent.` The cold-start check now covers the arm root **and** all three per-scenario copies.
3. **`MPA5-L7` — the chain's rc reflects its arms.** On the first launch, arm B exited `rc=1`, the
   chain correctly refused to proceed (`NORMALISERS_ABSENT`), and then **exited 0 and wrote
   `MPA5_CHAIN_RC: 0`** — anything keying on `CHAIN_RC.txt` would have read success on a failed
   chain. The chain now exits the first non-zero arm rc, and **`70` if a declared arm never ran**:
   an unrun arm is not a passed arm. Exit status is still **not** the verdict; the verdict is the
   comparator's.

### A1.4 Unchanged

**No cap of any kind.** Memory containment kept (`--memory=3g --memory-swap=3g --oom-score-adj=500`).
np=1 on its own cpuset; no sibling reniced, re-pinned or touched. The failed run root is **kept as
evidence and never deleted**; the relaunch uses a fresh timestamped root.

**Cost carried from the failed launch: 0.9333 core-min**, reported, added to this item's actual at
completion and attributed to the instrument defect above, **named as waste and never absorbed into
the actual/predicted ratio** (`COMPUTE_BUDGET_CHARTER.md` §6).

*`MP_A5` v1.1, 2026-09-12.*
