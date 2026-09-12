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
