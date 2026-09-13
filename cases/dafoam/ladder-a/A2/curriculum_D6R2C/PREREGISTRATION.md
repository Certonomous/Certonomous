# Curriculum D6R2C — the 3D transonic MULTIPOINT optimisation, RESTARTABLE, run as ubuntu

**Item id:** `D6R2C` (dafoam curriculum successor to `D6R2`).
**Version 1.0 — FROZEN 2026-09-12 by dafoam `lab-lane` for `dafoam-supervisor`.**
**Committed BEFORE any container starts** (`CLAUDE.md` rule 2). The freeze sha is the commit that
introduces this file together with its five instruments and its grading path.
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7).
**No frozen file is edited** (rule 6). **This item has burned 0 core-min and started no container
at freeze.**

> **ID-NAMESPACE WARNING.** `docs/DOCKET.md` carries fleet-defect rows numbered D6. Every `D<n>`
> here is the **curriculum** item. `D6R3` is reserved by `curriculum_D6R2/PREREGISTRATION.md`
> section 5 for the `DARhoSimpleCFoam` solver change and is **not** this item; D6R2C takes no
> solver change at all.

---

## 0. THE RULING THIS ITEM CARRIES, IN ONE LINE

**The production run RESTARTS FROM ITERATION 0 under this registration. It does NOT hot-start from
the dead D6R2 run's `OptView.hst`.** Ruled by `dafoam-supervisor` 2026-09-12 on three grounds: the
dead run executed as **root**, violating Sanaa's Launch item 6; this registration adds arm 0, the
restart machinery and the checkpoint policy, so it is a **different item**; and adopting a prior
run's state into a registration frozen *after* that run started is the adoption the supervisor
refused on A3GC L2 the same night. **Hot-start CAPABILITY is built here and proved by the
kill-and-resume test in section 5; the dead run's state is not a result and is not inherited.**

## 0a. What the dead D6R2 run was, and what is and is not carried

`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic/O_mp`, container
`d6r2_O_mp_20260912T033601Z_2772281`, started 2026-09-12T03:36:01Z, **Finished 17:32:57Z exit 255**.
Twelve IPOPT majors completed (`obj.J` 3.0641631e-02 → 2.3260046e-02) plus a partial thirteenth;
`D6R2_WATCH.tsv` row 17:31:00 reads **3292.33 core-min** against D6R2's registered cap of 2900,
already logged `D4S_CAP_CROSSED … action=REPORTED_RUN_CONTINUES`. `docker inspect` reads
`User=0:0`; the census counts **3,456 root-owned files** written into that run root
(`docs/RESIZE_CENSUS_2026-09-12.md` row 11 and the root-ownership table).

**CARRIED FROM D6R2:** the case (`base/`, 1.8 MB, copied read-only and hashed at seed), the mesh,
the FFD, the three scenarios, the CL targets, the weights, the constraints, the solver, every
tolerance, the image by digest, and the launcher's guard design. **NOT CARRIED:** `OptView.hst`,
`opt_IPOPT.txt`, the `mp0*/processor*` fields, the design vector, the objective trajectory, the
spend, and every number above. **D6R2's twelve majors are quoted in this document exactly twice:
once in this section as the history of why D6R2C exists, and once in section 6 as the REAL DATA the
stop-rule detector is driven against. Neither use is a result of this item.**

---

## 1. THE SPECIFICATION, FROZEN. Conditions, weights, targets, variables, constraints.

Every row below is `d6r2c_opt_runScript.py`'s own bytes, and the diff against D6R2's producer is
restricted to the four registered deltas of section 2. **No physics changes.**

| | value | where it lives in the instrument |
|---|---|---|
| flight conditions | three, one geometry: `cl04`, `cl05`, `cl06` | `POINTS` |
| free-stream | `U0 = 100.0 m/s`, `p0 = 101325 Pa`, `T0 = 300 K`, `nuTilda0 = 4.5e-5`, `aoa0 = 4.0 deg`, `A0 = 45.5` | Input Parameters block |
| **lift target per condition** | **`cl04` → CL = 0.4, `cl05` → CL = 0.5, `cl06` → CL = 0.6** | `CL_TARGETS` |
| **weights** | **`w = (0.25, 0.50, 0.25)`** on `(cl04, cl05, cl06)` | `WEIGHTS` |
| objective | **`J = 0.25·CD04 + 0.50·CD05 + 0.25·CD06`**, a weighted mean drag coefficient | the `obj` `ExecComp` |
| **design variables — shape** | **96**, local FFD displacements on a 6×2×8 lattice, bounds `[-1, 1]`, scaler 10.0 | `nom_addLocalDV("shape", …)`, `add_design_var("shape", …)` |
| **design variables — twist** | **7**, `rot_z` about a 25 %-chord reference axis, root twist NOT free, bounds `[-10, 10] deg`, scaler 0.1 | `nom_addGlobalDV("twist", …)` |
| trim variables | `patchV_<pt> = (U, AoA)` per condition, `U` pinned at `U0`, AoA in `[0, 10] deg`, scaler 0.1 | `add_design_var("patchV_" + pt, …)` |
| **constraint — lift** | `CL_i = target_i` **as an equality**, one per condition, scaler 1.0 | `add_constraint("%s.aero_post.CL", equals=…)` |
| **constraint — thickness** | `0.5 ≤ t/t_0 ≤ 3.0` on a 10 × 10 span×chord grid between `leList` and `teList`, on the `cl05` geometry | `nom_addThicknessConstraints2D("thickcon", …)` |
| **constraint — volume** | `V/V_0 ≥ 1.0` on the same box | `nom_addVolumeConstraint("volcon", …)` |
| **constraint — LE/TE** | `lecon = 0`, `tecon = 0`, **linear** | `nom_add_LETEConstraint(…)` |
| trim before iteration 1 | `findFeasibleDesign` solves the three CL targets on the three `patchV` variables at once | `run_driver` branch, cold path only |
| solver | `DARhoSimpleFoam`, `primalMinResTol = 1.0e-8`, `primalMinResTolDiff = 1e3`, wall functions on | `daOptions` |
| adjoint | GMRES, `gmresRelTol = 1.0e-6`, `pcFillLevel = 1`, `rcm` reordering | `adjEqnOption` |
| optimiser | IPOPT via pyOptSparse, `tol = 1e-5`, `constr_viol_tol = 1e-5`, `mu_strategy adaptive`, `nlp_scaling_method none`, `limited_memory_max_history 10` | `opt_settings` |
| image | `dafoam-idwarp-rot:v1` @ `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`, **PATCHED row only**, pinned by digest and refused on any other | launcher `G-IMG` |
| mesh | 9,504 cells, single grid | `base/constant/polyMesh` |

### 1a. THE ITERATION CAP IS A CAP, NOT A TOLERANCE. THIS IS EXPLICIT.

**`max_iter = 25` is a BUDGET ON IPOPT MAJOR ITERATIONS. It is NOT a convergence tolerance and no
reader may present a run that reaches it as converged.** The convergence tolerances are separate
and are `tol = 1.0e-5` and `constr_viol_tol = 1.0e-5`; on D6R2's measured trajectory the
constraint violation at major 12 was still `3.87e-03`, three decades above `constr_viol_tol`, so
**this problem is expected to terminate at the cap and not at a tolerance.** The registered,
expected termination line is therefore `EXIT: Maximum Number of Iterations Exceeded.` and that is
what G1 requires. `d6r2c_opt_runScript.py` REFUSES (exit 70) any `-max_iter` other than the two
registered values: **25 for production, 4 for the kill-and-resume proof of section 5.**

---

## 2. THE FOUR REGISTERED DELTAS TO THE PRODUCER, AND NO OTHERS

`d6r2c_opt_runScript.py` is `curriculum_D6R2/d6r2_opt_runScript.py`
(md5 `0abba50ab8baeefa3f59a3f1fc8f5336`) with exactly these changes. Verified by diff at the
freeze: the ONLY lines removed are the five anchors the deltas replace.

- **D1 — hot start** (Sanaa Checkpoints item 2). `-hotstart <file>` sets
  `pyOptSparseDriver.hotstart_file`. pyoptsparse 2.10.1 then restores the initial design vector
  from **call counter 0** of that history (`pyOpt_optimizer.py:184-199`) and replays every cached
  evaluation whose `x` matches to numpy `EPS`, writing the exact cached dictionary back out
  (`:232-299`). **The history file (`hist_file`, already D6R2's bytes) IS the per-iteration
  design-vector record** — pyoptsparse writes `xuser`, `funcs` and `funcsSens` for every call.
- **D2 — the per-evaluation record.** A driver subclass calls `super()` FIRST and records AFTER,
  on rank 0, to `d6r2c_evals.jsonl`: kind, iteration, fail flag, wall seconds, the full design
  vector and every function value. It has no branch that can change a number it observes. **A
  replayed evaluation never reaches it** — pyoptsparse serves those from cache — and that asymmetry
  is load-bearing: it is how the comparator in section 5 tells a genuine replay from a silent cold
  restart wearing a resume's name.
- **D3 — `-max_iter`**, default 25, refusing anything but 25 or 4 (section 1a).
- **D4 — the x0 identity guard.** On a cold start the design vector *after* `findFeasibleDesign`
  is written to `d6r2c_x0.json`. On a hot start `findFeasibleDesign` is **skipped** (its result is
  already call counter 0 of the history) and the script **REFUSES, before any compute (exit 73)**,
  if the history's call-0 design vector differs from the staged `d6r2c_x0.json` by more than
  **1.0e-12** in any component. A restart that silently began from a different point is the failure
  this guard exists to make impossible.

### 2a. The six registered LAUNCH deltas, all hygiene, none physics

`d6r2c_run_arm.sh` derives from `curriculum_D6R2/d6r2_run_arm.sh`
(md5 `715a2b9c42519b2ad25e9deeadb6351c`), carrying its `G-ROOT.1/2/3`, digest pin, `G-COLD`, age
datum and ledger design.

- **L1 — AS UBUNTU, NEVER ROOT** (Sanaa Launch item 6). `--user 1000:1000 --group-add 1002`.
  **Measured at the freeze, by execution, not assumed:** uid 1000 is named `ubuntu` *inside* this
  image as well as on the host; `/home/dafoamuser` is mode `0750` owned by uid **1002**, so uid
  1000 cannot source `loadDAFoam.sh` without gid 1002 — `--group-add 1002` grants traverse while
  the **primary gid stays 1000**, so every file the run writes is `ubuntu:ubuntu` on the host.
  `-e HOME=/tmp` because uid 1000 has no home in the image. `mpirun --allow-run-as-root` is
  **removed**: we are not root. The run script refuses (exit 72) if `getuid() == 0`, and the
  launcher counts root-owned files written after the age datum into the ledger row.
- **L2 — the memory guard** (Launch item 7 and the D6R2 brief item 3). `memory_footprint_gb = 17`
  is **declared** and checked against `MemAvailable` before start; the cgroup limit stays `20g`.
- **L3 — box hygiene** (item 18). The launcher **refuses to start** if `load1 > nproc` or if any
  swap is in use. This is a **launch precondition**: it refuses to START and never stops anything
  running (directive #17).
- **L4 — the resume staging.** `KR_RES` stages the killed arm's `OptView.hst` and `d6r2c_x0.json`
  as **inputs, before the age datum is set**, so the age guard dates them as inputs, not outputs.
- **L5 — the kill.** `KR_KILL` alone carries a watcher that `SIGKILL`s the container at IPOPT
  major 2. **This is not a cap and not a stop rule: it IS the experiment.**
- **L6 — the checkpoint rotator** (Checkpoints item 1): every **1800 s wall**, history + design
  vector + evaluation log + the latest primal time from every `mp0*/processor*` are copied to
  `ckpt/<UTC>/`; **the last two are kept and older ones are purged.**

### 2b. Why the primal's own writeInterval already satisfies "never exceeds 30 minutes"

Her Checkpoints item 1: *"writeInterval on iteration count is set so it never exceeds 30 minutes at
the measured rate; if the rate is unknown, checkpoint every 200 iterations until it is."*
`base/system/controlDict` carries `endTime 1000`, `writeInterval 1000`, `writeControl timeStep`, so
**the primal writes its fields at the end of every design major**. The measured rate is
**31.258 core-min/major at 4 ranks = 7.81 wall-minutes per major** (C-188, `8262f123`), so the worst
field-write interval is **7.81 minutes**, inside 30 by a factor of 3.8. **The rate is therefore
known and the 200-iteration fallback does not apply.** `writeInterval` is NOT changed — changing it
would be a physics-adjacent edit made for a bookkeeping reason. The 30-minute cadence she asked for
is supplied by L6 on top, and L6 is what keeps *two* checkpoints.

**Honest exposure, registered:** if contention pushes the rate above 30 wall-minutes per major —
D6R2's own dying run measured **69 wall-minutes per major** at load 40–77 — then the *field* write
interval exceeds 30 minutes even though L6's *rotator* does not. L6 still snapshots on the clock,
so at most 30 minutes of optimiser history is ever at risk; what can exceed 30 minutes is the
freshness of the primal fields inside a snapshot. **This is named here rather than hidden, and it
is a contention symptom, not a configuration one: the box at freeze carries load 0.32 on 16 cores.**

---

## 3. ARMS

| arm | what it is | ranks | `max_iter` | run in this registration? |
|---|---|---|---|---|
| `KR_REF` | the unkilled reference | 4 | 4 | **YES — section 5** |
| `KR_KILL` | a cold run SIGKILLed at IPOPT major 2 | 4 | 4 | **YES — section 5** |
| `KR_RES` | hot-started from `KR_KILL`'s history | 4 | 4 | **YES — section 5** |
| `ARM0_4R` | multipoint gradient, `compute_totals` | 4 | — | registered, **NOT run by this lane** |
| `ARM0_2R` | the same gradient at 2 ranks | 2 | — | registered, **NOT run by this lane** |
| `O_mp` | **the production multipoint optimisation, FROM ITERATION 0** | 4 | **25** | registered, **NOT run by this lane** |

**Only the three `KR_*` arms are compute this lane is permitted to run.** `ARM0_*` and `O_mp` are
frozen here and launched by the runner (`scripts/queue_runner.py`) once its guards land — **item
19: the runner is the only launcher, and nothing launched by hand counts as a case.** The
`KR_*` arms are **not cases**: they are the item-5 *proof* the directive requires *before* the
fleet launches anything, and they are graded as a proof, not as a result about the wing.

---

## 4. THE PRODUCTION GATES, FROZEN (arm `O_mp`)

Graded by `d6r2c_grade.py`'s inputs — the arm's own log, `opt_IPOPT.txt`, `OptView.hst`,
`d6r2c_evals.jsonl` and the arm directory — all read **after** the container exits.

- **G1 — THE OPTIMISER TERMINATED ITSELF AT ITS REGISTERED BUDGET.** `rc = 0`; `opt_IPOPT.txt`
  present and newer than the age datum, carrying `Number of Iterations....: 25` and
  `EXIT: Maximum Number of Iterations Exceeded.`. Any other `EXIT:` line — in particular
  `Invalid number in NLP function or derivative detected`, which is how D6R died at major 73 —
  **FAILS G1**. Any non-zero `rc`, including `137` (OOM) and `255`, **FAILS G1**.
- **G2 — THE PHYSICS GATE, WITH ITS BAND.** `J0` = the FIRST `obj.J` printed by THIS run, `Jf` =
  the LAST. **PASS requires `Jf ≤ 0.90 × J0`** — at least a **10 %** reduction in the weighted mean
  drag coefficient across the three lift points. (D6R2 measured 24.1 % by major 12 and D6R 27.4 %
  by major 73; 10 % at 25 majors is a bar this case can miss and is not a formality.)
- **G3 — THE LIFT CONSTRAINTS ARE HELD AT THE FINAL DESIGN.**
  `max_i |CL_i − target_i| ≤ 1.0e-3` over `cl04 / cl05 / cl06`.
- **G4 — THE RESULTS ARE SAVED, AND THEY ARE THIS RUN'S.** `OptView.hst`, `opt_IPOPT.txt`,
  `d6r2c_evals.jsonl`, `d6r2c_x0.json` and field data at time `1000` under `mp04/`, `mp05/`, `mp06/`
  `processor*`, all present and **strictly newer than the age datum `0/U`**.
- **G5 — IT RAN AS UBUNTU.** **Zero** files under the arm directory newer than the age datum are
  owned by uid 0 or gid 0. This gate exists because the run this item replaces failed it 3,456
  times and nothing in that run's registration could see it.

**LABELS.** `PASS` = G1∧G2∧G3∧G4∧G5. `GATE FAIL` = G1∧G4∧G5 hold and G2 or G3 misses, with `J0`,
`Jf`, the ratio and the three CL misses printed beside it. `NOT A RESULT` = G1, G4 or G5 fails, or
the registered cap of section 8 is crossed. No other label, no synonyms (rule 1).

**A Roache triple is NOT claimed and no GCI is quoted.** Single grid; rule 5 does not apply and
nothing here will be dressed as grid convergence.

---

## 5. THE KILL-AND-RESUME PROOF — THE ONLY COMPUTE THIS REGISTRATION AUTHORISES NOW

Sanaa, Checkpoints item 5, verbatim: *"one kill-and-resume test on one case per solver class, once,
before the fleet launches anything; the resumed result must match an unkilled reference to the
solver's tolerance."* **Solver class proved: DAFoam optimisation** (pyOptSparse/IPOPT driving
`DARhoSimpleFoam` primals and their adjoints under mphys/OpenMDAO).

**Protocol.** `KR_REF` runs cold to `max_iter 4`. `KR_KILL` runs cold, identically, and is
**SIGKILLed** — unhandled, the same class of death as the 17:32:57Z `exit 255` and as a reboot —
20 s after IPOPT prints major 2. `KR_RES` stages `KR_KILL`'s `OptView.hst` and `d6r2c_x0.json` as
inputs and runs to `max_iter 4` with `-hotstart`. `d6r2c_kr_compare.py` grades `KR_RES` against
`KR_REF`.

### 5a. THE TOLERANCES, REGISTERED BEFORE THE TEST RUNS

| quantity | tolerance | why this number |
|---|---|---|
| objective `J` | **1.0e-5 relative** | IPOPT's own `tol` on this problem is `1.0e-5`; a restart cannot be required to agree more closely than the optimiser's function precision |
| each `CD_i` | **1.0e-5 relative** | same basis |
| each `CL_i` | **1.0e-6 absolute** | `CL ∈ [0.4, 0.6]`, so ≈ 2e-6 relative — tighter than `constr_viol_tol = 1e-5` |
| design vector | **1.0e-6 absolute** on the scaled DVs | shape bounds are `[-1, 1]` at scaler 10, twist `[-10, 10]` at scaler 0.1 |
| hot-start x0 identity | **1.0e-12 absolute** | pyoptsparse restores x0 from the history itself; this is an identity check, not a physics one |

**WHY NOT BITWISE, STATED BEFORE THE ANSWER IS KNOWN.** `KR_RES`'s first *real* primal starts from
the field state left on disk by staging, while `KR_REF`'s corresponding primal starts from the
state its predecessor left in memory. Both are converged to `primalMinResTol = 1.0e-8`, so they
agree to that residual level and not to the last bit. **Bitwise agreement is not a property this
solver class has across a restart, and registering it would be a bar written to be failed.** What
*is* required bitwise is the **replayed** portion — see KR-G2 — because those are literal cached
dictionaries and anything else means the cache was not used.

### 5b. THE PROOF GATES

- **KR-G1 — THE MECHANISM ENGAGED.** `KR_RES` wrote an `X0_GUARD` row with
  `worst_abs_diff ≤ 1.0e-12`, **and** performed **strictly fewer** real evaluations than `KR_REF`.
  *A resumed run that re-evaluated everything did not hot-start, whatever its numbers say.*
- **KR-G2 — THE REPLAY IS EXACT.** For every call counter in `KR_KILL`'s history, `KR_RES`'s
  history entry carries **bitwise identical** objective and constraint values.
- **KR-G3 — THE ANSWER MATCHES.** At the final common IPOPT major, every tolerance of 5a holds.
- **KR-G4 — BOTH RUNS COMPLETED, AS UBUNTU.** `rc = 0` for `KR_REF` and `KR_RES`; both
  `opt_IPOPT.txt` carry `Number of Iterations....: 4` and
  `EXIT: Maximum Number of Iterations Exceeded.`; artefacts newer than each arm's own age datum;
  **zero** root-owned files from either.

**LABELS.** `PASS` = all four. `GATE FAIL` = KR-G1∧KR-G4 hold and KR-G2 or KR-G3 misses.
`NOT A RESULT` = KR-G1 or KR-G4 fails. **A `GATE FAIL` or `NOT A RESULT` here BLOCKS the
production launch of `O_mp`**, because item 5 makes the proof a precondition of the fleet.

### 5c. THE PLANTED CONTROL (rule 3)

`d6r2c_kr_compare.py` plants **`PLANT = 1.234e-03`** into the value it **read back from disk** for
the resumed run — separately into `J`, into `cl05`'s `CD`, and into the design vector — and
**REFUSES (exit 2)** if any plant leaves the verdict at `PASS`. **A comparator that cannot see a
disagreement of that size in these artefacts cannot certify an agreement, and its zero is not
evidence.** `--selftest` drives **13 controls in both directions** on synthetic inputs, touching no
run directory: the clean case must PASS, five plants must reach `GATE FAIL`, three mechanism
controls and three completion controls must reach `NOT A RESULT`, and a replayed value perturbed by
one part in 1e14 must reach `GATE FAIL`. **Driven at the freeze: `D6R2C_KR SELFTEST PASS`.**

---

## 6. THE MONITOR AND SANAA'S ITEM-7 STOP RULES

`d6r2c_monitor.py` writes `D6R2C_MONITOR.jsonl` per tick with: IPOPT major, **objective**,
**constraint violation** (`inf_pr`), dual infeasibility, the full objective history, **each
condition's convergence** (last primal time and final residual per equation, per `mp0*`, reported
`NOT_MEASURED` and never as converged when no log is readable), real evaluations so far,
**cost in core-minutes and core-minutes per major**, and **wall vs the registered cap**.

**Stop rule 1** (her item 7): the objective rising **three consecutive majors** → stop, halve the
step, resume from the last good iterate. **Stop rule 2**: the D6/D6R primal-non-convergence / NaN
signature in any condition → stop, resume from the last good iterate with the step halved.
The monitor **detects and records** by default; `--act` is required before it will `docker stop`
anything, and **even with `--act` it never acts on a cap** — a crossed cap is reported, the row is
graded `NOT A RESULT`, and the cap is never raised (directive #17 read with her item 7).

**THE DETECTORS ARE DRIVEN ON REAL DATA, NOT ONLY SYNTHETIC.** `--selftest` runs stop rule 1 over
the **actual objective sequence of the D6R2 run that died at 17:32:57Z** — majors 0–12, which
contain a genuine **two**-in-a-row rise at majors 3→4→5 — and requires it **NOT to fire**; then over
the **same real sequence at run length 2**, where it **must** fire at major 5, proving the reader
sees those rises; then over the **same real sequence mutated** to carry three consecutive rises,
where it **must** fire at major 6. Plus four boundary controls (falling, flat, exactly two, exactly
three), three for rule 2, and four on the IPOPT table reader driven on that file's own text.
**Driven at the freeze: `D6R2C_MONITOR SELFTEST PASS`, 13 controls.**

---

## 7. ARM 0 — PARALLELISM HEALTH, TOLERANCE REGISTERED BEFORE IT RUNS

Sanaa's D6R2 item 5. `d6r2c_arm0_gradient_health.py --dump` runs the multipoint model and its
adjoint once at the rank count `mpirun` was given and writes **every** total derivative of
`{obj.J, CL_cl04, CL_cl05, CL_cl06}` with respect to `{twist, shape}` to JSON from rank 0.
`--compare` grades the 2-rank dump against the 4-rank dump.

- **REGISTERED TOLERANCE: `1.0e-4` relative**, per component, normalised by `‖g₄‖∞` for that
  `(of, wrt)` pair. **Registered before the arm runs, and before iteration 1 of `O_mp`.**
- Components whose 4-rank magnitude is below `ABS_FLOOR = 1.0e-12` are graded on `ABS_TOL = 1.0e-12`
  and are **counted and named**; if **more than half** the components fall below the floor the
  comparison is **`NOT A RESULT`** — a gradient that is all noise cannot certify a decomposition.
- **Why 1e-4 and not bitwise:** the adjoint is GMRES to `gmresRelTol = 1.0e-6` and the primal to
  `1.0e-8`, on **different partitions** at 2 and 4 ranks — different sequences of floating-point
  reductions. 1e-4 is two decades looser than the adjoint's own relative tolerance and two decades
  tighter than the ~1e-2 level at which a real parallel defect (a missed halo exchange, an unsummed
  boundary contribution) shows up in this family.
- **`O_mp` does not launch until `ARM0` reads `PASS`.** An `ARM0` `GATE FAIL` is a finding about
  the decomposition and is reported as one; it is not a reason to change the rank count and then
  re-grade.
- **Selftest driven at the freeze: `D6R2C_ARM0 SELFTEST PASS`, 6 controls** — identical gradients
  PASS; a planted `1.0e-3` (ten times the tolerance) and a planted `1.234e-03` both FAIL; a planted
  `1.0e-5` correctly still PASSes; two dumps at the same rank count REFUSE; an all-noise gradient
  reads `NOT A RESULT`.

---

## 8. COST, IN CORE-MINUTES, BEFORE THE RUN (rule 12)

Anchor: **31.258 core-min per IPOPT major at 4 ranks**, MEASURED (C-188, `8262f123`).

| arm | predicted core-min | basis | **registered cap (3.00×)** |
|---|---|---|---|
| `KR_REF` | **140.0** | 4 majors × 31.258 = 125.03, + ~15 for `findFeasibleDesign` and container preamble | **420.0** |
| `KR_KILL` | **78.0** | 2 majors × 31.258 = 62.52, + ~15 preamble | **234.0** |
| `KR_RES` | **140.0** | 2 real majors + a cached replay + preamble; the cap is deliberately slack because a replay that costs as much as a solve is itself a finding | **420.0** |
| **KR PROOF TOTAL** | **358.0** | | **1074.0** |
| `ARM0_4R` | 15.0 | one primal + one adjoint at 4 ranks | 45.0 |
| `ARM0_2R` | 20.0 | the same at 2 ranks | 60.0 |
| `O_mp` | **786.5** | 25 majors × 31.258 = 781.5, + 5 preamble | **2359.5** |

**Derived dollars.** KR proof `358.0 core-min = 5.967 core-h × $0.0513 = $0.306`. `O_mp`
`786.5 core-min = 13.108 core-h × $0.0513 = $0.672`. **DERIVED, NOT MEASURED** — the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); `cost_basis` class **reported-by-owner** at
the owner-stated c7a.4xlarge rate. *(The box is now an r7a.4xlarge; the rate on record is the
c7a.4xlarge figure and is used unchanged rather than invented, and that substitution is named here
rather than buried.)*

**THE CAP REPORTS; NOTHING KILLS ON IT.** A crossing writes `D6R2C_CAP_CROSSED` to the ledger, the
row is graded **`NOT A RESULT`**, and **the cap is never raised** (Sanaa's item 7 read with her
2026-09-12 directive #17; the chief's reading at `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md`
line 71). No wrapper carries a `timeout`, and `D6R2C_DEADLINE_IN_CONTAINER_S: NONE` is printed by
every container.

**Contention caveat, registered in advance.** The 31.258 anchor was measured at
`delivered_cores_mean ≈ 3.98` of 4. D6R2's dying run measured **≈ 277 core-min/major** at load
40–77 — **8.9× the anchor** — because `core_min = wall_s × ranks / 60` inflates with contention at
identical compute work. At this freeze the box reads **load1 = 0.32 on 16 cores, 0 B swap in use,
111 GiB free**. A recorded figure above the prediction attributable to delivered-core starvation is
**REPORTED with the measured `delivered_cores_mean`** and named as waste, never absorbed into the
ratio (rule 12, `COMPUTE_BUDGET_CHARTER.md` §6).

**Calibration row OWED** to `docs/COST_CALIBRATION.md` at every process completion — the KR proof
and each arm — comparing actual against the estimate above, stating the ratio and attributing
contention, waste and misprediction separately (rule 12).

---

## 9. PLACEMENT, RANKS, MEMORY

`RANKS = 4`; `CPUSET = 2,3,4,5`; `--memory=20g --memory-swap=20g`, **declared
`memory_footprint_gb = 17`** and checked against `MemAvailable` before start. Core guard: 4 solver
ranks against `nproc = 16` (Launch item 8). An OOM kill (`rc = 137`) is a registered outcome and
fails G1 as `NOT A RESULT`.

## 10. WHAT THIS ITEM DOES NOT CLAIM

- **It does not inherit the dead D6R2 run.** Section 0. The production run starts at iteration 0.
- **It does not verify the gradient against finite differences.** That is the `F_mp` / D6RF family.
  `ARM0` compares the gradient **to itself at another rank count** — that is a *decomposition*
  check, not an *accuracy* check, and no reader may present it as one.
- **It does not claim the primal reaches the A2 accept floor of `1.0e-5`.** D6RF10 measured that
  this `DARhoSimpleFoam` configuration does **not** (`p_first_uncorrected = 1.681e-05`, `GATE FAIL`)
  and that a `DARhoSimpleCFoam` configuration **does** (`6.323e-06`). **That solver change is
  `D6R3`, a separate registered successor, and is deliberately NOT taken here** — its adjoint has
  never been exercised on this case, and an untested adjoint is not what an overnight run to a demo
  should carry.
- **It is not a grid study.** Single mesh, disclosed. No Roache triple, no GCI, no observed order.
- **The KR proof is not a result about the wing.** It is a result about restartability, at
  `max_iter 4`, and no number from `KR_REF`, `KR_KILL` or `KR_RES` may be quoted as an optimisation
  outcome.
- **Sanaa's D6R2 items 8, 9 and 10** — the shape/twist/trim decomposition, the fresh-mesh
  confirmation and the report — are **after** `O_mp` and are registered separately. They are named
  here so no reader mistakes this freeze for the whole instruction.

## 11. THE FROZEN INSTRUMENTS

| file | md5 at freeze |
|---|---|
| `d6r2c_opt_runScript.py` | `0558fb194b013b54c725d3d49a9dd0a1` |
| `d6r2c_run_arm.sh` | `f92865b3cba5d3ae49bcd1dcfb0919f6` |
| `d6r2c_kr_compare.py` | `e3f78650b2995cd5aeaa3cc2e5755b04` |
| `d6r2c_monitor.py` | `fd927f36ee47acef09fc8a08b790ccbe` |
| `d6r2c_arm0_gradient_health.py` | `7da73e35a50b146247dd1b214d4e69c8` |

The launcher **pins `d6r2c_opt_runScript.py` by md5 and refuses (exit 4) on any difference**
(`G-FREEZE`), so the instrument that runs is the instrument that was frozen. **The grading path
(`d6r2c_kr_compare.py`, `d6r2c_arm0_gradient_health.py`) is in THIS COMMIT**, fixed before any
compute, per rule 2.

---

# ADDENDUM 1 — 2026-09-12, after KR_RES refused at rc=73 on a defect in this item's OWN GUARD

**Version 1.1.** **Lines whose number changed above this section: 0.** This addendum is appended,
never inserted; nothing above it is edited (rule 6). **It alters no gate, no threshold, no cap and
no label** (rule 2): `KR-G1`–`KR-G4`, the section 5a tolerances, the section 4 production gates and
every cap in section 8 stand exactly as frozen at `7f685867d`.

## A1.1 The verdict that stands, and is not rewritten

**The kill-and-resume proof of section 5 is `NOT A RESULT`.** Section 5b: *"`NOT A RESULT` = KR-G1
or KR-G4 fails."* `KR_RES` exited `rc = 73`; KR-G4 requires `rc = 0`. **That row is closed at
`NOT A RESULT` and this addendum does not touch it.** The repaired attempt below produces a **new**
row, graded by the **untouched** comparator.

| arm | rc | wall s | core-min | cap | root-owned |
|---|---|---|---|---|---|
| `KR_REF` | 0 | 4073 | 271.533 | 420.0 | 0 |
| `KR_KILL` | 137 | 3595 | **239.667** | **234.0 — CROSSED by 5.667 (2.4 %)** | 0 |
| `KR_RES` | **73** | 21 | 1.400 | 420.0 | 0 |

`D6R2C_CAP_CROSSED` is in the ledger for `KR_KILL`, as registered, and **the cap is not raised.**
Attribution (rule 12, named separately, never blended): `KR_KILL` reached major 0 in 3120 s against
`KR_REF`'s 2682 s, a **measured** contention factor of **1.163** from the unpinned `K2h_L3`
neighbour sharing cpuset 2,3,4,5. De-contended, `KR_KILL` is **206.0 core-min — inside 234**. The
crossing is **contention, not misprediction**; the row still crossed and is reported as crossed.

## A1.2 The defect, and why it is in this item's guard and not in the restart machinery

The x0 identity guard compared **pyoptsparse's history against `prob.get_val()`**. Those are **two
different spaces**: the history stores the **driver-scaled** design vector; `prob.get_val()` returns
the **physical** one. `patchV` is registered at `scaler = 0.1`, so:

```
history  call-0 patchV_cl04 = [ 10.0, 0.29303833722365635]   driver-scaled
d6r2c_x0.json   patchV_cl04 = [100.0, 2.9303833722365633 ]   physical
ratio = 10.0 exactly on every component = 1 / scaler
worst_abs_diff = 90.0 exactly = 100.0 − 10.0
```

**The resume was never wrong. The guard was.** Driven on the real artefacts after the repair, the
comparison in the history's own space returns **`worst_abs_diff = 0.000e+00` — bitwise identical.**

## A1.3 The deeper defect a units-only fix would have left in place

Of the **109** design-variable components, **103 — all 96 `shape` and all 7 `twist` — are exactly
zero at x0.** Zero times any scaler is zero, so **those 103 match under every unit convention and
are blind to the error.** All discriminating power sat in the **6** non-zero `patchV` components.
**Had the trim returned AoA = 0, the guard would have passed and been believed.** The guard's
controls were built on **synthetic dictionaries and never touched a real history**, which is
precisely why this survived to launch.

## A1.4 The repair, under `VERIFICATION_CHARTER` §2d.1

§2d governs changes **on the grading path**; the grading path here is `d6r2c_kr_compare.py`, which
is **untouched**. The guard is a **launch precondition**. §2d therefore does not strictly bind, and
its discipline is **invoked anyway** as the conservative choice. The four conditions:

1. **Demonstrable error, not preference** — the ratio is exactly `1/scaler` on all six informative
   components and exactly 0 on the 103 uninformative ones. Arithmetic, not taste.
2. **Established by an instrument independent of the hypothesis, that grades nothing** — the x0
   guard is a precondition refusal, no part of `KR-G1`–`KR-G4`, and it produced **the least
   convenient outcome available: `NOT A RESULT` on this lane's own item.** It cannot have been
   selected to move a verdict in a wanted direction.
3. **Disclosed here, instrument named, movement quantified** — this section.
4. **Pre-repair values recorded beside the published ones** — the table in A1.1 and the `90.0` above.

**The repair, and its three parts:**
- **One named space.** The guard compares in `X0_SPACE = "driver-scaled"` and **prints which space
  and how the reference was obtained.** A comparison whose units are implicit is the bug itself.
- **Scalers read from OpenMDAO's own metadata** (`prob.model.get_design_vars(...)['total_scaler']`),
  **never re-typed** from the `add_design_var` calls — a second hand-written copy of a number is a
  second thing that can drift (L-221/222).
- **The blindness floor, registered: `X0_INFORMATIVE_FLOOR = 6`.** A component is *informative* only
  if non-zero on either side. The guard **counts** them, **prints** the count, and **REFUSES below
  the floor**: *a guard that cannot see must say so rather than pass quietly.* Six because this
  problem has exactly 6 non-zero DV components at x0 (3 conditions × `[U, AoA]`).
- Going forward `d6r2c_x0.json` records **both** spaces plus the scalers. The pre-addendum file
  carries physical only; the guard converts it and **says that it did.**

## A1.5 The control that did not exist before, driven on REAL artefacts

`d6r2c_x0_guard_selftest.py` reads `KR_KILL/OptView.hst` (1,077,248 bytes) and
`KR_KILL/d6r2c_x0.json` — **the actual files, not synthetic stand-ins** — and drives **11 controls
in both directions**. Result at this addendum: **`D6R2C_X0_SELFTEST PASS`.**

- correct space on the real history → `PASS`, `worst = 0.000e+00`
- **the historical defect reproduced to the exact `90.0`** → `REFUSE_MISMATCH`
- four planted `1.234e-03` disagreements, in `patchV`, `twist` and `shape` → all `REFUSE_MISMATCH`
- **an all-zero design vector → `REFUSE_BLIND`**, and **`shape`+`twist` only → `REFUSE_BLIND`**
  — *under the original guard both of these would have PASSED*
- floor boundary: 6 informative against a floor of 6 → `PASS`; against 7 → `REFUSE_BLIND`

## A1.6 What is re-run, and what is not

**`KR_RES` ONLY.** `KR_REF` (`rc=0`) and `KR_KILL` (`rc=137`, killed as designed at IPOPT major 2)
are **not re-run**: their artefacts are intact, `KR_KILL`'s history holds majors 0–2, and re-running
them would spend ~511 core-min to repair a defect in a precondition. The repaired `KR_RES` is graded
by `d6r2c_kr_compare.py` **unchanged**, at the md5 frozen at `7f685867d`.

**Instrument hashes after this addendum:**

| file | md5 at freeze `7f685867d` | md5 at ADDENDUM 1 |
|---|---|---|
| `d6r2c_opt_runScript.py` | `0558fb194b013b54c725d3d49a9dd0a1` | **`2f2ae43a627146cf8e0f065b035ada4b`** |
| `d6r2c_run_arm.sh` | `f92865b3cba5d3ae49bcd1dcfb0919f6` | **`85a296e562ed54700ead608fd698f802`** (md5 pin only) |
| `d6r2c_kr_compare.py` | `e3f78650b2995cd5aeaa3cc2e5755b04` | **UNCHANGED — the grading path** |
| `d6r2c_monitor.py` | `fd927f36ee47acef09fc8a08b790ccbe` | UNCHANGED |
| `d6r2c_arm0_gradient_health.py` | `7da73e35a50b146247dd1b214d4e69c8` | UNCHANGED |
| `d6r2c_x0_guard_selftest.py` | — | **`c20ca4514bade1fc596447c8655d69de`** (new control) |

## A1.7 What this addendum does not claim

- **It does not claim the hot start works.** `KR_RES` never reached one evaluation, so `KR-G1`,
  `KR-G2` and `KR-G3` remain **untested**. That pyoptsparse restores x0 self-consistently is an
  **inspection**, and refusing to trust inspection is the whole reason this test exists.
- **It does not rewrite the `NOT A RESULT` verdict** of A1.1, and no number from `KR_RES`'s refused
  21-second run is quoted as a result.
- **It does not widen a band or relax a tolerance.** `X0_MATCH_TOL` stays `1.0e-12`; the repaired
  comparison meets it at **0.000e+00**.

---

# ADDENDUM 2 — 2026-09-12, a LABEL ERROR IN THIS DOCUMENT'S OWN TITLE

**Version 1.2.** **Lines whose number changed above this section: 0.** Appended, never inserted.
**Alters no gate, threshold, cap or label-of-verdict** (rule 2). It corrects a **descriptive word**,
and the distinction matters: nothing about the physics, the case, the mesh or any gate changes.

## A2.1 The error

This document is titled *"the 3D transonic MULTIPOINT optimisation"* and its run root is
`CURRICULUM-D6R2C-a2-wing-multipoint-**transonic**-restartable`. **The case is not transonic.**
From this registration's own frozen inputs (section 1: `U0 = 100.0 m/s`, `T0 = 300 K`, air):

```
a     = sqrt(1.4 x 287 x 300) = 347.1887 m/s
M_inf = 100 / 347.1887        = 0.288028
```

**M∞ = 0.288 — subsonic, by a wide margin.** Transonic conventionally begins near M ≈ 0.7.
A peer lane independently measured the **maximum LOCAL Mach at 0.380** (`16e4d5f34`), which is the
stronger statement and is **cited here rather than re-derived**: there is no shock anywhere in this
flow, so there is nothing transonic to show and nothing for a render to display as one.

## A2.2 Where the word came from, and why that is the interesting part

**Inherited.** `curriculum_D6R2/PREREGISTRATION.md` carries it, and this item copied its title
wholesale when it copied its case. **No one checked it against the two numbers that define it, both
of which were sitting in section 1 of the document carrying the word.** The arithmetic is one line.
That is the whole failure mode: *a descriptive label propagated by copy for as long as nobody
divided one frozen number by another.*

## A2.3 What changes, and what deliberately does not

- **The word "transonic" is STRUCK as a description of this case.** The correct description is
  **compressible subsonic** — `DARhoSimpleFoam` is a compressible solver and remains correct and
  registered; it is the *flow regime* label that was wrong, not the solver choice.
- **The run root keeps its name.** `CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable`
  already holds `KR_REF` and `KR_KILL` artefacts that this item's records cite by path. **Renaming a
  directory to fix a word would break every existing citation to buy nothing**, and Sanaa ruled
  directly on the equivalent question for D6R2: *"its fine we can keep the compressible subsonic"*.
  **The name is therefore a known misnomer, disclosed here, and a reader who finds "transonic" in a
  path should read this section rather than infer a flow regime from a directory name.**
- **No gate, threshold, cap, tolerance or verdict label is touched.** G1–G5, KR-G1–KR-G4, the
  section 5a tolerances and every cap in section 8 stand exactly as frozen at `7f685867d`.
- **No physics changes.** `U0`, `T0`, `p0`, the solver, the mesh, the weights, the targets and the
  constraints are untouched. **The case was always subsonic; only the word was ever wrong.**

## A2.4 The consequence for the deliverable, stated so it is not discovered late

Sanaa's D6R2 item 10 asks for sections and figures to the figure standard. **No shock figure can be
produced and none should be promised**, at any Mach contour level, because the maximum local Mach in
this flow is 0.380. A demo that advertises a transonic wing optimisation and shows this case would
be advertising something the artefacts cannot support. The optimisation itself is unaffected and the
drag reduction it measures is real.

---

# ADDENDUM 3 — 2026-09-13, THE PRODUCTION GRADING INSTRUMENT DID NOT EXIST AT THE FREEZE

**Version 1.3.** **Lines whose number changed above this section: 0.** Appended, never inserted;
nothing above it is edited (rule 6). **It alters no gate, no threshold, no cap and no label**
(rule 2): `G1`–`G5`, the `G2` band `Jf ≤ 0.90 × J0`, the `G3` tolerance `1.0e-3`, the `G4` artefact
list and its literal time `1000`, `G5`, the section 5a tolerances, `KR-G1`–`KR-G4` and every cap in
section 8 stand **exactly as frozen at `7f685867d`**. What this addendum does is **disclose a defect
in this registration and record the verdict it produced.** Nothing here repairs the defect
retroactively and nothing here is offered as a reason to weigh the verdict more kindly.

## A3.1 THE DEFECT: SECTION 4 NAMED AN INSTRUMENT THAT HAD NEVER EXISTED

Section 4 opens: *"Graded by `d6r2c_grade.py`'s inputs — the arm's own log, `opt_IPOPT.txt`,
`OptView.hst`, `d6r2c_evals.jsonl` and the arm directory — all read **after** the container exits."*

**`d6r2c_grade.py` did not exist.** Measured 2026-09-13, by execution: absent from the working tree;
absent from every tree in this repository's git history; absent from **section 11's frozen-instrument
table**, which registers five files and not that one; and absent from **A1.6's post-addendum hash
table**, which re-listed all five and added a sixth control without noticing the gap.

**THE CONSEQUENCE FOR RULE 2, STATED PLAINLY AND NOT SOFTENED.** Rule 2 requires that *"the grading
path is fixed at the pre-registration commit"*. For this item that requirement was met for the
kill-and-resume proof (`d6r2c_kr_compare.py`, in the freeze commit, hash-pinned, and deliberately
left **UNCHANGED** through ADDENDUM 1) and for arm 0 (`d6r2c_arm0_gradient_health.py`, likewise).
**It was NOT met for the production gates `G1`–`G5`.** At the moment `O_mp` started, the five gates
that decide this item's headline verdict had **no instrument at all**. Section 11's closing sentence
— *"The grading path (`d6r2c_kr_compare.py`, `d6r2c_arm0_gradient_health.py`) is in THIS COMMIT,
fixed before any compute, per rule 2"* — is true as written and **names only the two paths it
covers**; it is the absence of the third name, not a false claim, that carried the defect past the
freeze. A table that lists what exists cannot show what is missing, and nothing in this item's
instrument set asserted that section 4's named grader was among them.

## A3.2 THE INSTRUMENT WAS THEREFORE WRITTEN AFTER ITS RUN HAD PRODUCED DATA

`cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_grade.py`, written 2026-09-13 while `O_mp` was at
IPOPT iteration 23 of 25 and finished after it exited. **md5 `ca159f6cee00c3e571195b44d2967659`.**
This is exactly the hazard rule 2 exists to prevent, and the mitigations below are named as
mitigations, not as a cure.

- **Every threshold, literal, comparison direction and label is COPIED VERBATIM from the frozen
  section 4**, and each constant in the file carries the sentence it was copied from as its comment.
  The cap comparison `core_min > cap` is copied from `d6r2c_run_arm.sh:352`'s own strict `>`.
- **The author chose nothing.** Where section 4's prose is ambiguous the instrument does not resolve
  the ambiguity: it computes the strict reading, **reports the alternative beside it**, and
  **REFUSES (exit 2)** rather than pick when two registered artefacts disagree about one quantity.
  Four such ambiguities are enumerated in the file's own header (A-1 the printed form of `obj.J`;
  A-2 which record is the final design; A-3 what "field data" enumerates; A-4 the log's print
  precision as a floor on `G2`).
- **43 planted controls (rule 3), `D6R2C_GRADE SELFTEST PASS n=43`, exit 0**, on synthetic trees in
  a temporary directory, touching no run directory: three negative controls including a real
  `copytree` regraded, five on `G1`, three on `G2`, four on `G3`, eight on `G4`, one on `G5`, three
  on the cap, two on label precedence, and fourteen refusals. **The `G5` control plants a REAL
  uid-0 file** via `sudo -n touch`, verified uid 0 by `lstat`, and removes it — not simulated.
- **The supervisor read the instrument as a diff before any of its output was believed**, which is
  the non-delegable check of `SUPERVISION_CHARTER` §3, and that read caught a real defect (A3.4).

**TWO FINDINGS THE CONTROLS PRODUCED ABOUT THE FROZEN GATES THEMSELVES**, recorded because they are
properties of the registration and not of the instrument, and because **neither was accommodated**:

1. **`G3`'s band edge is not representable.** For every registered target (0.4, 0.5, 0.6) there is
   no IEEE double `v` with `|v − target| == 1.0e-3`: the attainable misses step by ~1.1e-16 and
   straddle the literal without landing on it. `target + 1.0e-3` evaluates to a miss of
   **1.0000000000000009e-3**, which is **outside** the band and `GATE FAIL`s under section 4's `≤`
   — correctly. The boundary is therefore driven from both sides, one ulp apart. **No tolerance was
   added to the gate to make the edge reachable.**
2. **`G2`'s resolution is floored by the log's print.** Section 4 registers *the log* as the source
   of `J0` and `Jf`, and the log prints `obj.J` at eight decimals. A `G2` margin below that last
   digit is not resolvable from the registered source, whatever `d6r2c_evals.jsonl` holds at full
   precision. The instrument computes that floor from the printed string itself and reports it as
   `j_print_ulp` (here **1e-08**) so that a rounding is never read as a measurement.

**THIS DISCLOSURE TRAVELS WITH THE VERDICT PERMANENTLY.** A reader is entitled to weigh a verdict
produced by a late-written instrument below one produced by a frozen path, and this section exists
so that the weighing is possible rather than prevented.

## A3.3 THE SUPERVISOR'S RULING ON AMBIGUITY A-1

The arm's log carries `obj.J` in two printed forms: the per-evaluation dictionary
`{'obj.J': array([…])}`, and pyOptSparse's optimisation-summary table row `0  obj.J  <value>`.
Section 4 says only *"the FIRST `obj.J` printed by THIS run"*. The lane refused to choose. **The
`dafoam-supervisor` ruled 2026-09-13: grade on the dictionary form.** The ruling is recorded with
its reasons so it is reviewable rather than asserted:

1. The summary-table form's pre-solve row prints `0.000000E+00`. That is an uninitialised slot, not
   an objective. Section 4 defines `J0` inside a sentence whose whole purpose is the ratio
   `Jf ≤ 0.90 × J0`; **a reading that puts a zero in the denominator cannot be the one the clause
   intends.**
2. The dictionary form's first print is `0.03064163` and its last `0.02306326`, which coincide with
   IPOPT's own iteration-0 and iteration-25 objectives. That is the sequence the 10 % bar is about.

**`g2_alternative_reading` is preserved in `O_mp_GRADE.json` exactly as built** — the table-form
reading, its `J0`, its `Jf`, its ratio and its `G2` outcome — so a later reader can disagree with
the ruling **on the evidence** rather than having to rediscover that there was a choice.

## A3.4 THE DEFECT THE SUPERVISOR'S READ CAUGHT, AND HOW CLOSE IT CAME

`gate_g3` **degraded to NaN arithmetic instead of refusing.** A failed evaluation writes NaN into
`obj.J` and into the three CLs; **every comparison against NaN is `False` in Python**, so the
instrument's own A-2 cross-check (`if abs(jlast - jf) > jf_ulp: raise Refusal`) **did not fire on a
NaN record.** Execution fell through, the misses became NaN, `max(..., key=…)` over NaN has
undefined ordering, and `ok = nan <= 1.0e-3` evaluated `False` — the instrument would have reported
**`GATE FAIL` manufactured out of a non-measurement.**

**This was one evaluation away from happening.** Measured from `d6r2c_evals.jsonl`: of 87
`kind == "F"` records, **52 carry `fail = 1`**, and the tail of the fail-flag sequence is **seven
consecutive failures followed by the single successful evaluation the run ended on**. Had IPOPT
stopped one evaluation earlier, this item's headline verdict would have been NaN arithmetic wearing
a registered label.

**Repaired before the instrument was ever run on the arm**, by an A-2a non-measurement guard placed
**before** the cross-check — the ordering is load-bearing and the file says so. It refuses (exit 2)
if the final-design record has a missing or non-zero `fail`, a non-finite `obj.J`, or any non-finite
CL; it **prints** the record's `n`, `utc` and `fail`, and **names** the last record that *is* a
measurement with its numbers, **and does not fall back to it** — that choice belongs to the
supervisor, not to the instrument. Three controls drive it, including one with `fail = 0` and NaN
values, which isolates the NaN path and proves the `fail` flag is not carrying the guard alone.

## A3.5 THE REGISTERED STOP-RULE INSTRUMENT WAS NEVER INVOKED

Section 6 registers `d6r2c_monitor.py` by md5 (`fd927f36ee47acef09fc8a08b790ccbe`, section 11) with
13 controls driven at the freeze, to write `D6R2C_MONITOR.jsonl` per tick and to detect Sanaa's
item-7 stop rules. **Measured 2026-09-13, by execution, not assumed: no `D6R2C_MONITOR.jsonl` exists
anywhere on this box, and the string `d6r2c_monitor` appears in no launcher, chain or script** —
not in `d6r2c_run_arm.sh`, not in `d6r2c_queue_chain.sh`, not in `d6r2c_omp_only_chain.sh`, not in
`scripts/`. **Section 6 was unsatisfied for this run.** The instrument exists and is selftested; it
was never started, so nothing watched this run against the stop rules while it ran.

**The `dafoam-supervisor` ruled that item 7 did not fire, on independent measured grounds** rather
than on the absence of a monitor that could have said so: no NaN entered the solver's own solution;
no divergence in the objective; the evaluation failures do not track step size; and eleven step
halvings were measured to fail. **The ruling is recorded here as a supervisor's ruling with its
evidence, and the underlying measurements are the supervisor's, not this lane's** — this lane
measured only the two facts in the paragraph above, and says so rather than adopting a peer's
measurement as its own.

## A3.6 WHAT THE FAILED EVALUATIONS ACTUALLY WERE — SECTION 6 ASSUMED A SIGNATURE THIS RUN DID NOT PRODUCE

Section 6's stop rule 2 is written against *"the D6/D6R primal-non-convergence / NaN signature"*.
**This run's failures do not carry that signature**, and recording what they *are* is the point of
this section.

- **The fail threshold is `1.0e-5`**, and it is arithmetic on this registration's own frozen
  constants: `primalMinResTol = 1.0e-8` × `primalMinResTolDiff = 1e3`
  (`d6r2c_opt_runScript.py:126-127`). **Measured by this lane** from the frozen instrument.
- **48 `Primal min residual` blocks appear in the arm's log and all 48 are failures**; the minimum
  failed residual is **`1.000006e-05`** and the maximum **`7.312316e-05`**. **Measured by this
  lane** from `O_mp_20260913T013230Z_226722.log`. The minimum sits **six parts in ten million above
  the threshold** — these are primals that missed the bar by rounding, not primals that diverged.
- **The partition has zero overlap**: the largest non-failed residual is **`9.985532e-06`**, below
  the smallest failed one. **This figure is the supervisor's measurement, relayed and labelled as
  such.** This lane confirmed that the value `9.985532e-06` occurs in the log as a converged
  primal's `p` initial residual but **did not independently reproduce it as the maximum over the
  non-failed partition**, and does not present it as its own.
- **A single-cell mesh-quality trip.** `checkMesh` in this run's log reports
  ***`High aspect ratio cells found, Max aspect ratio: 1026.908433, number of cells 1`*** — **one
  cell**, on a deformed geometry, against a base mesh whose maximum aspect ratio the same log reports
  as `684.4022128 OK`. **Measured by this lane** (one occurrence in the log). The `1000` trip level
  is `checkMesh`'s own reporting threshold, not a quantity this registration fixed, and is named as
  `checkMesh`'s rather than adopted as a gate.

**None of this moves a gate.** Section 4 does not gate on evaluation failures, on residuals or on
mesh quality, and this section adds no gate that does. It is recorded because section 6 assumed a
different failure mode, and a reader of that section is entitled to know this run did not exhibit it.

## A3.7 THE VERDICT AS GRADED

**`GATE FAIL`**, written by `d6r2c_grade.py` to
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp_GRADE.json`,
exit 0. Section 4's label rule, unchanged: `G1 ∧ G4 ∧ G5` hold and `G3` misses.

| gate | result | the numbers behind it |
|---|---|---|
| `G1` | **PASS** | `rc = 0`; `Number of Iterations....: 25`; exactly one `EXIT:` line in `opt_IPOPT.txt`, the registered `EXIT: Maximum Number of Iterations Exceeded.` |
| `G2` | **PASS** | `J0 = 0.03064163` (log line 11568), `Jf = 0.02306326` (log line 54198), ratio **0.752677**, a **24.732 %** reduction against the registered 10 % bar; margin `Jf − 0.90×J0 = −4.514e-03`; print resolution `1e-08` |
| `G3` | **MISS** | `cl04` miss `5.539e-04`; `cl05` miss **`1.210e-03`**; `cl06` miss **`2.787e-03`** — against `1.0e-3`. Final design: `F` record `n = 88`, `fail = 0` |
| `G4` | **PASS** | all four artefacts present and strictly newer than the age datum; time `1000` present in **all twelve** `mp0{4,5,6}/processor{0..3}` directories, 15 files each, **zero** entries not newer than the datum |
| `G5` | **PASS** | **7,291** entries scanned under the arm directory, **zero** owned by uid 0 or gid 0 and newer than the datum |
| cap | **not crossed** | **672.933** core-min against the registered **2359.5**, margin **−1686.567** |

**THE CORROBORATION, AT SEVENTEEN DIGITS.** `opt_IPOPT.txt` reports
`Constraint violation....: 2.7869956827836218e-03`. The grader's `cl06` miss, computed from
`d6r2c_evals.jsonl` by an entirely separate code path, is `0.0027869956827836218`. **Identical to
the last digit.** The `dafoam-supervisor` independently recomputed `G3` by a third path and obtained
the same value. Two instruments that share no code agree, which is what makes the `G3` miss a
property of the run rather than of the reading the grader took for ambiguity A-2. The A-2
cross-check itself closed at `|obj.J − log Jf| = 4.71e-10` against the print ulp `1e-08`.

**THIS IS THE OUTCOME SECTION 1a REGISTERED IN ADVANCE.** *"`max_iter = 25` is a BUDGET ON IPOPT
MAJOR ITERATIONS. It is NOT a convergence tolerance and no reader may present a run that reaches it
as converged."* The run terminated at the budget with `inf_pr = 2.79e-03`, **two decades above**
`constr_viol_tol = 1.0e-5`. The drag bar is cleared with room; **the lift equality constraints are
not held to `1.0e-3` at the final design**, and `GATE FAIL` is precisely the label section 4 assigns
to that.

## A3.8 WHAT THIS ADDENDUM DOES NOT CLAIM

- **It does not repair the rule-2 defect.** The production grading path was not fixed at the
  pre-registration commit. It cannot be made so afterwards, and this addendum does not pretend
  otherwise; it records the defect so the verdict is read with it.
- **It does not add `d6r2c_grade.py` to the section 11 frozen-instrument table.** That table records
  what was frozen **at the freeze**; this file was not. Its md5 is recorded in A3.2 **as of this
  addendum**, explicitly as an instrument written late.
- **It does not alter a gate, a threshold, a cap or a label**, and no finding in A3.2 was
  accommodated by widening one.
- **It does not claim the monitor ran.** Section 6 is recorded as unsatisfied, and the ruling that
  item 7 did not fire rests on the supervisor's independent measurements, named as the supervisor's.
- **It does not present the supervisor's residual-partition measurement as this lane's.** A3.6 says
  which figures are measured here and which are relayed.
- **It does not re-describe the flow regime.** ADDENDUM 2 stands: `M∞ = 0.288`, compressible
  subsonic, and no shock figure can be produced from these artefacts.

---

# ADDENDUM 4 — 2026-09-13, THREE ERRORS OF RECORD: A REFUTED MECHANISM ON THE BOARD, A MESH SIZE IN SECTION 1 THAT IS PROCESSOR 0's SHARE, AND A `checkMesh` COUNT IN ADDENDUM 3 THAT IS ONE OF FOUR

**Version 1.4.** **Lines whose number changed above this section: 0.** Appended, never inserted;
nothing above it is edited (rule 6). **It alters no gate, no threshold, no cap and no label**
(rule 2): `G1`–`G5`, the `G2` band `Jf ≤ 0.90 × J0`, the `G3` tolerance `1.0e-3`, the `G4` artefact
list and its literal time `1000`, `G5`, the section 5a tolerances, `KR-G1`–`KR-G4`, section 7's
`REL_TOL = 1.0e-4` / `ABS_FLOOR = ABS_TOL = 1.0e-12` / `MAX_SMALL_FRACTION = 0.50`, and every cap
in section 8 stand **exactly as frozen at `7f685867d`**. **No verdict word moves.** `ARM0` remains
**`GATE FAIL`** and `O_mp` remains **`GATE FAIL`**; neither `ARM0_VERDICT.json` nor `O_mp_GRADE.json`
is edited and neither md5 moves. What this addendum does is **correct three things this item has on
record that are wrong**, one of which withdraws an interpretation already published to the lab board.

**No solver was run for this addendum.** Every number below is read from artefacts already on disk,
by a lane that launched no compute. Where a question cannot be settled without compute it is marked
**`NOT MEASURED`** and left open rather than guessed.

---

## A4.1 ERROR 1 — THE ARM-0 GRADIENT DUMP IS **NOT** ALIASING. IT IS AN UNTRIMMED OPERATING POINT, AND WHAT THAT RETRACTS IS DIFFERENT FROM AND NARROWER THAN THE RETRACTION THIS LANE WAS ASKED TO WRITE.

### A4.1.1 The observation, reproduced independently by this lane

In `ARM0_4R/arm0_totals.json` (md5 `f117d3afde460878ebba0f55a5f9bfa2`), under `totals`, the three
arrays `cl04.aero_post.CL|shape`, `cl05.aero_post.CL|shape` and `cl06.aero_post.CL|shape` are
**bit-identical** — `max|diff| = 0.000000e+00` for all three pairs, and the md5 of each array's
canonical JSON is the same `594d706de072…`. The same holds for `|twist` (md5 `1be46b6e41d9…`).
In `ARM0_2R/arm0_totals.json` (md5 `16be0732443caadde8b9db56dcb2cfb1`), `cl04` and `cl06` are
bit-identical but `cl05` differs from both by **`7.819924e-05`** (shape) and **`7.656112e-07`**
(twist). **All of these are reproduced by this lane from the JSON, not relayed.**

### A4.1.2 The hypothesis put to this lane, and the finding: mechanism **(c)**, not (a) and not (b)

Three mechanisms were put: **(a)** the dump writer reuses or rebinds one array across the three
scenario keys; **(b)** the `compute_totals` call resolves one `of` list against one scenario;
**(c)** the coincidence is real in the arm-0 model *state* and not in the driver's.

**(a) is refuted.** The writer is `d6r2c_arm0_gradient_health.py:147-148`:

```
for k, v in totals.items():
    out["totals"]["%s|%s" % (k[0], k[1])] = [float(x) for x in np.asarray(v).flatten()]
```

It iterates OpenMDAO's own returned mapping, keys each entry by the `(of, wrt)` tuple it was
handed, and **materialises a fresh Python list of floats per key**. There is no binding that two
keys could share and no key that is written twice: the key is built from `k`, so a duplicate key
would require `compute_totals` to have returned duplicate tuples.

**(b) is refuted, and by the run's own log rather than by reading.** The `of` list at
`d6r2c_arm0_gradient_health.py:137` is `["obj.J"] + ["%s.aero_post.CL" % p for p in POINTS]` —
three distinct promoted names. `ARM0_4R_20260913T000043Z_152777.log` records **three separate
adjoint solves for CL**, each a `Solving Linear Equation…` followed by its own
`Computing d[aero_residuals]/d[patchV]^T * psi` and `Computing d[CL]/d[patchV]^T * psi`, at
`1880.26 → 1902.42 s`, `1902.92 → 1925.22 s` and `1925.43 → 1947.86 s` (log lines 3121-3130,
3132-3141, 3143-3150). Three solves, roughly 22.3 s each. The three arrays were **computed**, not
copied. The 2-rank dump settles it a second way: an aliasing writer cannot produce a dump in which
`cl05` differs from `cl04`, and the 2-rank dump does exactly that.

**(c) is the mechanism, and it is settled by line and by measurement.**

- `d6r2c_opt_runScript.py:270` gives **every** point the same initial trim variable:
  `self.dvs.add_output("patchV_" + pt, val=np.array([U0, aoa0]))` — one `aoa0 = 4.0`
  (`:113`) for `cl04`, `cl05` and `cl06` alike. `shape` and `twist` are zero at `:267-268`.
- The trim that separates the three points, `optFuncs.findFeasibleDesign(...)`, is at
  **`d6r2c_opt_runScript.py:532`**, inside the `if args.task == "run_driver":` branch opened at
  `:529` — i.e. **240 lines below the anchor `# OpenMDAO setup` at `:292`**. `dump()` execs only
  `src[:anchor]` (`d6r2c_arm0_gradient_health.py:98`, `:121`) and then builds its own
  `om.Problem` and calls `run_model` / `compute_totals` directly (`:132-139`). **The trim
  therefore never runs in the `--dump` path.**
- **The measured consequence, and it is decisive.** In the 4-rank arm's log all three primals
  converge to **bit-identical** final values: `CD: 0.02772949388  CL: 0.4775877833` at log lines
  2310-2311, 2534-2535 and 2758-2759. Three scenarios, three converged states, one number to
  eleven significant figures. **The three scenarios are not three operating points at arm 0; they
  are one operating point evaluated three times.** Identical models require identical derivatives,
  and that is what the dump contains.
- **The contrast with the driver, also reproduced by this lane**, read directly from
  `O_mp/OptView.hst` (sqlite, table `unnamed`, pickled values; 52 records carry `funcsSens`,
  174 carry `xuser`). At call counter `'0'` — x0, *after* `findFeasibleDesign` — the three trim
  variables are **distinct**: `dvs.patchV_cl04 = [10.0, 0.29303834]`,
  `dvs.patchV_cl05 = [10.0, 0.43261269]`, `dvs.patchV_cl06 = [10.0, 0.5941267]`, i.e.
  AoA **2.930 / 4.326 / 5.941 deg** at the registered scaler 0.1. And the driver's three CL
  gradients are distinct at every record inspected, never bit-identical:

  | `funcsSens` record | AoA cl04/cl05/cl06 (deg) | max&#124;d(CL04)−d(CL05)&#124;/d(shape) | cl04−cl06 | cl05−cl06 |
  |---|---|---|---|---|
  | #1 (rowid 8, hst key `'1'`) | 2.930 / 4.326 / 5.941 | `1.928490e-03` | `4.931654e-03` | `3.274477e-03` |
  | #27 (rowid 148, hst key `'71'`) | 1.313 / 2.514 / 3.778 | `1.114459e-03` | `2.134883e-03` | `1.135502e-03` |
  | #52 (rowid 352, hst key `'173'`) | 0.577 / 1.772 / 3.038 | `1.004606e-03` | `2.901037e-03` | `1.896431e-03` |

  On `twist` the separation is an order larger again (`1.644147e-02` / `1.082687e-02` /
  `7.221111e-03` for cl04−cl05 at the same three records). **The deliverable's multipoint problem
  is genuinely multipoint; arm 0's is not.**

**Therefore: the arm-0 dump does not alias. `ARM 0 CERTIFIES RANK AGREEMENT AT AN OPERATING POINT
THE DELIVERABLE NEVER VISITS`, and the triplication is the arithmetic consequence of that, not a
writer defect.** This is the same mechanism the `dafoam-supervisor` recorded in the board's S-176
block; this section confirms it against the primal values, which S-176 did not have, and **records
that the competing aliasing hypothesis is refuted so that no successor registration inherits it.**

### A4.1.3 What IS retracted, stated bluntly

The board's S-176 block reads, of the 2-rank pattern: *"Three bitwise-identical problems, one rank
count, one run, **TWO DIFFERENT ANSWERS**… **THIS IS THE FIRST REAL PARALLEL-DECOMPOSITION SIGNAL
THE LADDER HAS PRODUCED**"*.

**The premise "three bitwise-identical problems" is false as stated, and this lane is the one
naming it.** `geometry_cl05` is **not** the same component as `geometry_cl04` and `geometry_cl06`.
At `d6r2c_opt_runScript.py:260-264` the `cl05` geometry alone carries four extra objects —
`nom_addThicknessConstraints2D("thickcon", …)`, `nom_addVolumeConstraint("volcon", …)` and two
`nom_add_LETEConstraint(…)` — because section 1 registers the geometric constraints on the `cl05`
geometry only. **`cl05` is the one point that differs structurally, and `cl05` is exactly the point
that differs numerically at 2 ranks.** That is a confound the self-consistency argument does not
clear, and a self-consistency argument with an uncleared confound is not a demonstrated defect.

**The 2-rank finding is therefore downgraded from *a demonstrated parallel-decomposition defect*
to *an open finding with a named benign candidate*.** It remains worth its own registered item —
it is not dismissed — but it may not be reported as a parallel defect on this evidence.

**A second measurement, new here, narrows it further and cuts one branch off.** The 2-rank
difference is **already present in the PRIMAL, before any adjoint runs.** Final converged values in
`ARM0_2R_20260913T003347Z_188691.log`:

| point | log lines | `CD` | `CL` |
|---|---|---|---|
| first (`cl04`) | 2180-2181 | `0.02773273449` | `0.4775871603` |
| second (`cl05`) | 2404-2405 | `0.02772732376` | `0.4775876687` |
| third (`cl06`) | 2628-2629 | `0.02773273449` | `0.4775871603` |

`cl04` and `cl06` agree to the last printed digit; `cl05` does not. **Whatever this is, it is not a
halo-exchange or unsummed-boundary defect in the ADJOINT** — section 7's own examples — because it
is visible in the primal's converged force coefficients. It is a primal-or-earlier difference:
mesh warping, the geometry component's output, or the primal solve itself.

**`NOT MEASURED`, and named as such.** This lane cannot say *which*, and cannot say why the same
structural difference between `cl05` and its siblings produces **bit-identity** at 4 ranks
(`CD: 0.02772949388 / CL: 0.4775877833` for all three) while producing a difference at 2. The
extra-pointsets candidate is **not obviously consistent with the 4-rank result** and is offered as
a candidate to be tested, not as an explanation. Settling it requires compute this addendum did not
spend and this registration does not authorise.

### A4.1.4 What SURVIVES, and is not overstated in the other direction

**The `ARM0` verdict stands as a number and as a word.** The two dumps do disagree: worst
**`2.925612e-04`** at `cl04.aero_post.CL|shape[80]` against the **REGISTERED `1.0e-4`**, 27 of 412
components over tolerance, 0 below the `1e-12` floor, 2 ranks vs 4. **Reproduced component-by-
component by this lane from the two JSON dumps against section 7's frozen constants, matching
`ARM0_VERDICT.json` (md5 `41dd8ac74d298390e6f398f058306b2e`) exactly.** **`GATE FAIL` is the word
and this addendum does not move it.** Both dumps carry the same `producer_md5`
`2f2ae43a627146cf8e0f065b035ada4b`, which is the md5 of `d6r2c_opt_runScript.py` as it stands
today — the comparator's same-producer refusal (`:165-168`) had something real to check and passed
it.

What is withdrawn is the verdict's **interpretation** and its **component count**.

### A4.1.5 HOW MUCH OF THE PARALLELISM-HEALTH CHECK WAS ACTUALLY PERFORMED

**412 graded components, 206 distinct derivatives.** `cl04/cl05/cl06 × {shape, twist}` is
`3 × (96 + 7) = 309` slots holding `96 + 7 = 103` distinct derivatives; `obj.J|shape` (96) and
`obj.J|twist` (7) are **single arrays that cannot be duplicated** and hold the other 103.
`309 + 103 = 412`; `103 + 103 = 206`. This confirms the `206 of 412` figure already on the board.

**Where the 27 disagreements sit** — measured by this lane, re-running section 7's frozen
comparison arithmetic over the two dumps:

| pair | length | disagreeing | worst (relative to ‖g₄‖∞ of that pair) |
|---|---|---|---|
| `cl04.aero_post.CL\|shape` | 96 | **9** | `2.925612e-04` |
| `cl05.aero_post.CL\|shape` | 96 | **1** | `1.285219e-04` |
| `cl06.aero_post.CL\|shape` | 96 | **9** | `2.925612e-04` |
| `cl04/cl05/cl06.aero_post.CL\|twist` | 7 each | **0** | — |
| **`obj.J\|shape`** | 96 | **7** | `1.708777e-04` |
| **`obj.J\|twist`** | 7 | **1** | `1.055954e-04` |

- **19 of the 27 are in the triplicated `CL` rows; 8 are in the single `obj.J` rows.**
- Of the 19, `cl04` and `cl06` contribute the **identical index set**
  `[1, 64, 65, 72, 73, 80, 81, 88, 89]` — **nine misses counted twice** — and `cl05` contributes
  one, index `4`.
- **Distinct disagreeing components: 18 of 206.** Union over the distinct derivatives:
  `CL|shape` indices `{1, 4, 64, 65, 72, 73, 80, 81, 88, 89}` (10), `CL|twist` (0),
  `obj.J|shape` (7), `obj.J|twist` (1).

**THE GATE FAIL DOES NOT REST ON THE DUPLICATED ROWS, AND IT IS THE PART OF THIS SECTION THAT
MATTERS MOST.** `obj.J|shape` and `obj.J|twist` are single arrays, structurally incapable of
duplication, and they alone carry **8 components over the registered `1.0e-4`**, worst
`1.708777e-04`. **Discard every triplicated row and the comparison is still `GATE FAIL`.** The
2-vs-4 disagreement is real and is not an artefact of the replication.

**What the replication does cost is discriminating power, and it is honestly one number:** the
check was believed to compare 412 independent derivatives of a three-point multipoint problem; it
compared 206 derivatives of a **single-point** problem, at `AoA = 4.0 deg`, a condition the
deliverable visits at no iteration. `ARM0_VERDICT.json`'s `"n_components": 412` is a count of
**graded slots**, not of independent derivatives. **That artefact is not edited and its md5 does
not move** — it is read with this section.

---

## A4.2 ERROR 2 — SECTION 1's MESH ROW RECORDS PROCESSOR 0's SHARE, NOT THE MESH. THE MESH IS **38,304** CELLS.

**Line 72 of this document**, in the section 1 specification table, reads:

> `| mesh | 9,504 cells, single grid | base/constant/polyMesh |`

**`9,504` is processor 0's share under the 4-way decomposition**, not the cell count of the grid.
**Two independent sources, both on disk:**

1. **The run's own decomposition table.** `ARM0_4R_20260913T000043Z_152777.log` lines 94-132:
   `Processor 0 … Number of cells = 9504`, `Processor 1 … 9600`, `Processor 2 … 9608`,
   `Processor 3 … 9592`. **Sum = 38,304.** The same table repeats for the second and third points
   at lines 783-821 and beyond, with the same four numbers.
2. **The mesh's own header, written by the mesher and independent of any run.**
   `base/constant/polyMesh/owner.gz`, FoamFile `note`:
   `"nPoints:40209  nCells:38304  nFaces:116756  nInternalFaces:113068"`.

**The two sources agree exactly: `nCells:38304` = `9504 + 9600 + 9608 + 9592`.** The registered
figure is low by a factor of **`38304 / 9504 = 4.0303`** (not exactly 4 — `38304 / 4 = 9576`, and
processor 0 happens to hold 72 cells fewer than an even quarter).

**NO GATE READS CELL COUNT, SO NO VERDICT MOVES.** Section 4's `G1`–`G5`, section 5's
`KR-G1`–`KR-G4`, section 5a's tolerances, section 7's tolerance and section 8's caps contain no
cell-count term; the figure appears in section 1 as description only. **Line 72 is struck, not
rewritten** (rule 2): the correct value is recorded **here**, at the foot, and the line above is
left exactly as frozen.

**THE DOWNSTREAM CONSEQUENCE, NAMED SO IT IS NOT FOUND LATER.** The landed calibration row
**`C-20260913T043733.251556Z-17681dfe`** in `docs/COST_CALIBRATION.md` carries
*"4 ranks, 9,504 cells, three lift conditions"* in its process cell, inherited from this line.
Under that file's **append rule 1** — *"An existing row is never edited; a correction is a new row
naming the row it corrects"* — **the landed row is not touched.** A correction row is owed and is
drafted at
`cases/dafoam/ladder-a/A2/curriculum_D6R2C/COST_CALIBRATION_ROW.D6R2C_Omp_MESH_CORRECTION.md`.

**No core-minute figure in that row moves.** Its predicted `786.5`, gross `672.933`, cleaned
`672.933`, ratio `0.856`, per-major `26.917`, the named waste `51.955` and the residue `203.468`
are wall-clock × ranks ÷ 60 arithmetic and never touched cell count. **What is wrong is every
per-cell figure a reader would derive from the row**, and any such figure is **4.0303× too large**.
For a reader who needs one: `672.933 core-min / 38,304 cells = 1.757e-02 core-min per cell` for the
whole 25-major arm, where the row as landed would yield `7.080e-02`.

---

## A4.3 ERROR 3 — ADDENDUM 3 §A3.6 RECORDS **ONE** `checkMesh` ASPECT-RATIO TRIP. THERE ARE **FOUR**, AND THE ONE ON RECORD IS NOT THE WORST.

**A3.6's fourth bullet reads:**

> *"A single-cell mesh-quality trip. `checkMesh` in this run's log reports **`High aspect ratio
> cells found, Max aspect ratio: 1026.908433, number of cells 1`** — one cell … **Measured by this
> lane** (one occurrence in the log)."*

**`grep -c 'High aspect ratio cells found'` on `O_mp_20260913T013230Z_226722.log` returns `4`.**
All four, in log order, each reporting `number of cells 1`:

| # in log | log line | `Max aspect ratio` |
|---|---|---|
| 1 | 22928 | **`1050.3162`** ← **the worst** |
| 2 | 31050 | `1007.373135` |
| 3 | 33015 | **`1026.908433`** ← **the value on record** |
| 4 | 46373 | `1049.209899` |

Ascending: `1007.373135 < 1026.908433 < 1049.209899 < 1050.3162`.

**The value on record is the third of the four in log order, and it is the second-smallest of the
four. The worst is `1050.3162`, and it is the FIRST occurrence in the log** — the one a reader
scanning from the top meets before any other. Against the `maxAspectRatio 1000.0` registered in
`daOptions["checkMeshThreshold"]` (`d6r2c_opt_runScript.py:162`), the worst trip is **5.03 % over**,
not the 2.69 % the recorded value implies. The zero-trip count on all eleven other logs in the run
base was also checked: only `O_mp` trips at all. A3.6's other facts stand — each trip is genuinely
**one cell**, on a deformed geometry, against the base mesh's `684.4022128 OK`.

**ATTRIBUTION, AND IT IS THE PART THAT MATTERS MORE THAN THE NUMBER.** The "one occurrence" figure
**did not originate with the lane that wrote A3.6.** It came from the `dafoam-supervisor`'s brief to
that lane, and the lane repeated it under the label **"Measured by this lane"**. Two failures, of
different sizes, and they belong to different people:

- **The supervisor's:** the figure itself, and the fact that a brief supplied a measurement a lane
  was expected to stamp.
- **The lane's:** stamping a relayed figure as its own measurement. `REPORTING` forbids exactly
  this, and A3.8 promises in writing three bullets later that this addendum *"does not present the
  supervisor's residual-partition measurement as this lane's"* — the discipline was applied to the
  bullet above and dropped on the bullet below it.

**The error is the supervisor's; the mislabel is the lane's.** Recording it the other way round —
as a lane that miscounted — would be the cheaper story and is the one this section refuses.

**NO GATE MOVES.** A3.6 already records that section 4 does not gate on evaluation failures, on
residuals or on mesh quality, and this section adds no gate that does. The `1000` level remains
`checkMesh`'s own reporting threshold, **named as `checkMesh`'s and not adopted as a gate**, exactly
as A3.6 has it.

---

## A4.4 THE ARTEFACTS THIS ADDENDUM READ, WITH THEIR md5 AT THIS ADDENDUM

| artefact | md5 at ADDENDUM 4 | note |
|---|---|---|
| `d6r2c_opt_runScript.py` | `2f2ae43a627146cf8e0f065b035ada4b` | the frozen producer; **equals the `producer_md5` recorded inside both arm-0 dumps** |
| `d6r2c_arm0_gradient_health.py` | `21419e51dd6ee177ff79684867659fa8` | the arm-0 instrument, **not edited by this addendum** |
| `d6r2c_grade.py` | `ca159f6cee00c3e571195b44d2967659` | unchanged from A3.2; still **not in the freeze** |
| `ARM0_VERDICT.json` | `41dd8ac74d298390e6f398f058306b2e` | **not edited**; still reads `GATE FAIL` |
| `ARM0_4R/arm0_totals.json` | `f117d3afde460878ebba0f55a5f9bfa2` | the 4-rank dump |
| `ARM0_2R/arm0_totals.json` | `16be0732443caadde8b9db56dcb2cfb1` | the 2-rank dump |

Logs read, under
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/`:
`ARM0_4R_20260913T000043Z_152777.log`, `ARM0_2R_20260913T003347Z_188691.log`,
`O_mp_20260913T013230Z_226722.log`; plus `O_mp/OptView.hst` and `base/constant/polyMesh/owner.gz`.

---

## A4.5 WHAT THIS ADDENDUM DOES NOT CLAIM

- **It does not move a verdict word.** `ARM0` is `GATE FAIL`; `O_mp` is `GATE FAIL`. Neither
  artefact is edited, neither md5 moves, and nothing here is offered as a reason to read either
  more kindly. A4.1.5 in fact *strengthens* the `ARM0` result by showing it survives discarding
  every duplicated row.
- **It does not repair anything.** `d6r2c_arm0_gradient_health.py` is not edited by this addendum.
  The instrument still certifies the untrimmed condition, and a successor registration owes the
  trimmed one, **frozen before it runs**.
- **It does not edit section 1 line 72, and does not edit A3.6.** Both are struck here and left in
  place above (rule 2, rule 6). `Lines whose number changed above this section: 0`.
- **It does not correct `ARM0_VERDICT.json`'s `"n_components": 412`.** That is a count of graded
  slots and is accurate as such; the distinct-derivative figure lives here.
- **It does not edit the landed calibration row.** `docs/COST_CALIBRATION.md` append rule 1 forbids
  it; a correction row is drafted, not landed by this addendum.
- **It does not settle the 2-rank `cl05` difference — `NOT MEASURED`.** No solver was run. The
  extra-constraint-pointsets candidate is a candidate, is not obviously consistent with the 4-rank
  bit-identity, and is not presented as a finding.
- **It does not claim the aliasing hypothesis was ever written into this registration.** It was a
  hypothesis in a supervisor's brief; it is recorded here as **refuted**, with its evidence, so that
  no successor inherits it from a half-remembered board block.
- **It does not re-describe the flow regime.** ADDENDUM 2 stands: `M∞ = 0.288`, compressible
  subsonic.
