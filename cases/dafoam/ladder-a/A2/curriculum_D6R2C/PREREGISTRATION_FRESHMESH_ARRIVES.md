# Curriculum D6R2C — PRE-REGISTRATION for arm `FM9`: THE FRESH MESH ACTUALLY ARRIVES

**Item id:** `D6R2C-FM9`, arm **`FM9`**.
**Version 1.0 — DRAFT, NOT YET FROZEN.** Written 2026-09-13 by a dafoam `lab-lane` for `dafoam-supervisor`.
**This item has burned 0 core-min and started 0 containers at the time of writing.**
**Rule-2 pre-compute condition, checked:** the registered run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM9-a2-wing-freshmesh-arrives` **does not exist**.
Frozen by the commit that introduces this file **with its three instruments** (§11).
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7).

**ONE REGISTERED CHANGE.** The freshly extruded mesh is put into every condition case and the stale
decomposition is removed, so the solver's `prob.setup()` decomposes **the fresh mesh**. Nothing else
moves: no field transfer, no new producer, the same solver, the same weights, `primalMinResTol` untouched.

---

## 1. WHY THIS ARM EXISTS

### 1a. THE DEFECT — MEASURED, AND IT IS A TIMELINE

**`FM5`, `FM7` AND `FM8` EACH GENERATED THE FRESH MESH CORRECTLY AND NEVER SOLVED ON IT.**

| arm | fresh mesh written | the mesh the solver read | gap |
|---|---|---|---|
| `FM8` | **08:28:11** | all 12 `mp0X/processorN/…/points.gz` at **08:27:06–08:27:09** | 62–65 s **earlier** |
| `FM5` | **06:48:26** | **06:47:13** | 73 s **earlier** |
| `FM7` | **08:12:50** | **08:11:42** | 68 s **earlier** |

**A decomposition cannot be of a mesh that does not yet exist.** The hashes agree with the timeline:

```
arm/constant/polyMesh/points.gz        a7bfb41c5b5f   the FRESH mesh, generated and hashed for H2
mp04/constant/polyMesh/points.gz       0fb1935a9b87   THE BASE MESH, dated 2026-07-28, never updated
mp04/processor0/…/points.gz            c7f5feda2f4dc6774cf320d4cb2ffcb3
                                                      the base mesh DECOMPOSED — WHAT THE SOLVER READ
```

`dafoam-supervisor` scanned **every** `processor*/constant/polyMesh/points.gz` under the whole runs
tree — **1486 files, zero matches** against the fresh mesh's hash. With a non-zero scan count, that zero
is evidence and not silence. **No arm in this item's history has ever loaded the freshly extruded mesh.**

### 1b. WHY THE GATES DID NOT SEE IT

`H2` required the mesh to **exist**, to come from `genWingMesh.py` at the pinned md5, and to **differ
from the base**. **All three were true of all three arms while the solver read something else.** `H1`
compares a CGNS surface against `O_mp`'s stored wall points and is independent of the solve's mesh.

> **A CHECK MUST EXERCISE THE THING, NOT DESCRIBE IT** (L-595). `H2` described a file. This arm's gate
> reads **the mesh the solver loaded**.

### 1c. WHAT IS RETRACTED, AND WHAT IS NOT

- **`FM8`'s `PASS` does not support what it was read as.** `H3` was registered as *"the only thing that
  differs is the mesh"*; the mesh did not differ. This registration does not re-grade it — that is the
  supervisor's — and records that the `|d| = 1.869382e-08` anomaly, **46.9× tighter than this solver's
  own measured path-dependence**, has its explanation here.
- **`FM5` and `FM7` keep their `NOT A RESULT` labels; their stated CAUSE was wrong.** They did not stall
  on a fresh mesh.
- **`1.278377566e-05` IS NOT A FRESH-MESH FLOOR.** The number is real and measured; the description is
  wrong, and it is carried as a fresh-mesh anchor in `PREREGISTRATION_GRADIENT_SPOTCHECK.md` §3e and in
  the `GS2` grader. Those are frozen or drafted elsewhere and their correction is not this file's.
- **The 2×2 is withdrawn**, on two independent grounds: no arm ever loaded the fresh mesh, and the index
  transfer is invalid on one (§2b).

---

## 2. THE ONE CHANGE

### 2a. WHAT `phase stage` DOES, AND WHICH HALF IS OPERATIVE

For each of `mp04`, `mp05`, `mp06`: copy the fresh `points/faces/owner/neighbour/boundary` into
`mp0X/constant/polyMesh`, **then delete every `processorN/` directory**.

> **THE DELETION IS THE OPERATIVE HALF.** Copying the mesh in changes nothing on its own: **DAFoam
> decomposes only when `processorN/` is ABSENT**, and reads whatever decomposition it finds otherwise —
> which is exactly how three arms solved on a mesh they had not generated. **Evidence that removal is
> sufficient:** each of those arms' own deform phase created `processorN/` from a clean tree, at
> `08:27:06` in `FM8`'s case.

The producer writes **`d6r2c_fm9_stage.json`** into the arm directory — the fresh hash, what each
condition's mesh read before and after, and which processor directories were removed — and `M1` grades
against the arm itself rather than against that record. The producer **refuses** if the generated mesh
equals the base (`REFUSE_FRESH_IS_BASE` — *staging it
would prove nothing*), if a condition case is missing, if the copy does not read back as the fresh mesh,
or if any `processorN/` survives (`REFUSE_PROCESSOR_DIRS_REMAIN`).

### 2b. THERE IS NO FIELD TRANSFER, AND THAT IS A DELIBERATE SUBTRACTION

**The cell-for-cell index transfer used by `FM8` is NOT VALID once the fresh mesh genuinely arrives.**
Measured 2026-09-13 by reconstructing the warped mesh's undecomposed points from `FM8`'s own
`pointProcAddressing` and comparing them point-for-point against the fresh mesh:

| quantity | value | in units of the median first-cell height (`2.313647e-03 m`) |
|---|---|---|
| min displacement | **0.0** | **0** — the WALL points coincide exactly |
| median | `4.1124e-02 m` | **17.8 cell heights** |
| p99 | `5.2846 m` | 2284 |
| max | `1.0160e+01 m` | 4391 |
| points beyond one cell height | **29,931 of 40,209** | **74.4 %** |

The zero minimum is the corroboration: it is `H1`'s `5.010837892761856e-09` equality seen from the other
side. **The two meshes agree on the surface and diverge in the interior**, one being extruded from the
deformed surface with its own 300 m march and the other a base extrusion pulled onto that surface.

> **THE INDEX CORRESPONDENCE IS TOPOLOGICAL, NOT SPATIAL.** Cell `i` in the fresh mesh sits a median 18
> first-cell heights from cell `i` in the warped mesh. A copy by index is **not a small-error
> interpolation; it is a scramble.** It looked exact in `FM8` **only because its destination was never
> the fresh mesh.**

**So the transfer is DROPPED, not broken, and this arm starts from the case's own freestream `0.orig`.**
Fixing the mesh and keeping the transfer would be two changes that cannot both be true.

**AND THAT MAKES THE PRIOR QUESTION THE ONLY QUESTION.** Nothing has ever solved on this mesh, so *does
a freshly extruded mesh converge at all?* comes first. **Freestream-versus-warm-start cannot be asked
until it is answered**, and if the warm start is wanted later it needs a **proper interpolation** — a new
instrument, separately frozen — not an index copy.

---

## 3. THE GATES, FROZEN

Graded by **`d6r2c_fm9_grade.py --item FM9`**, after the container exits.

- **`M1` — THE MESH THE SOLVER LOADED IS THE FRESH MESH. FOUR LIMBS, ALL REQUIRED.**
  1. **CONTENT.** For each condition, the undecomposed mesh is **rebuilt from the solver's own
     `processorN/constant/polyMesh` via `pointProcAddressing`** and compared to the generated mesh by
     **exact point equality — `max |Δ| == 0.0`**.
     *A note on what is achievable, because it was asked for differently:* **a processor's own
     `points.gz` md5 can never equal the whole mesh's — it holds a SUBSET.** "Twelve hashes equal to the
     fresh mesh's" would have to be weakened to pass. Rebuilding the arrays is achievable, is **stronger
     than a hash**, and is the technique that exposed the defect.
  2. **TIMELINE.** Every one of the twelve processor meshes has an mtime **at or after** the fresh mesh's
     creation. **This is the check that would have caught `FM8` in one line**, and it costs nothing.
  3. **CORROBORATION FROM A DIFFERENT OBJECT.** The solver's **own reported cell and point counts in the
     log** against `38,304` and `40,209`. A hash check and a log check read different things; **if they
     disagree the arm refuses rather than believing either.**
  4. **The generated mesh must differ from the base** `0fb1935a9b8781b73ac4ccb136e3ec68`, and the
     processor count must be the registered 4. The hash of what three arms actually solved on,
     **`c7f5feda2f4dc6774cf320d4cb2ffcb3`**, is registered beside it so a reader can recognise the old
     state on sight.
  **A failure names which conditions did not arrive.**
- **`H1` — THE FRESH MESH IS THE FINAL SHAPE.** `SHAPE_MATCH_TOL = 1.0e-8` **and** the ADDENDUM 4 §A4.3
  **equality**, `worst_dist = 5.010837892761856e-09`, bit for bit. Inherited unchanged.
- **`H3` — THE BAND.** `|J_fresh − Jf| ≤ FM_BAND_ABS = 3.064163144e-04`, with
  `Jf = 0.0230632595286777639`. **Inherited unchanged — but for the first time `J_fresh` really is a
  fresh-mesh value**, which is what §4 is about.
- **`H4` — COMPLETION AND HYGIENE.** `rc = 0`; the staged inputs are the registered inputs; the record
  newer than the age datum; **zero** files newer than the datum owned by uid 0 or gid 0; the §8 cap not
  crossed.
- **`H2` IS DEMOTED TO REPORTED AND IS NEVER A GATE.** Provenance of the file is still worth recording;
  **it is not evidence that the solver read it**, and all three of its clauses passed in `FM5`, `FM7`
  and `FM8`.

**LABELS.** `PASS` = `H1 ∧ M1 ∧ H3 ∧ H4`. `GATE FAIL` = `H1 ∧ M1 ∧ H4` hold and `H3` misses.
`NOT A RESULT` = `H1`, `M1` or `H4` fails, or the cap is crossed. **No other label** (rule 1).

### 3a. WHAT A STALL MEANS HERE — DECIDED IN ADVANCE

**`FM9` IS EXPECTED TO STALL AND THAT IS STILL A RESULT.** `FM5` and `FM7` stalled from freestream — but
on the base mesh, so they say nothing about this one. If `FM9` stalls with `M1` holding, **this item has
its first honest fresh-mesh datum**, and the warm start becomes the next registered change with a proper
interpolation. If it converges, that is a larger finding about the mesh. **`primalMinResTol` is never
loosened to make either happen.**

### 3b. CONVERGENCE COMES FROM THE LOG, NOT FROM `primal_converged`

`H4` does **not** rest on the producer's `primal_converged` field. **That field defaults to `True`, and
its source `primal_residual.json` has four readers and no writer anywhere in this repository** — the
clause it feeds is vacuous. `H4` counts `Primal solution failed` in the arm log, and **a missing log is
`NOT A RESULT`, never a silent pass.** The field is still recorded, for the reader, with a note saying
no clause rests on it.

---

## 4. WHAT THIS ARM LICENSES

| claim | supported? |
|---|---|
| the fresh mesh **arrived at the solver** | **YES** — that is `M1`, and it is the point |
| whether a freshly extruded mesh **converges at all** | **YES** — first measurement either way |
| `H3`'s band, as **a genuine two-mesh comparison** | **YES, for the first time.** In `FM5`/`FM7`/`FM8` both sides came from the same mesh |
| any **re-validation of the 24.732 %** | **NO.** That is a single-mesh measurement and stays one |
| any **mesh-level claim** | **NO.** The `N = 39` vs `N = 62` layer-count shift is **6.7033 drag counts, 2.1877 %** at the baseline (`J_B(N=62) = 2.997129747951e-02` against `J0(N=39) = 3.064163143900e-02`), with no grid study behind it. *This arm's mesh and the optimisation's are both `N = 39` and differ only by warping* |

---

## 5. THE ARM

| arm | phases | ranks | run here? |
|---|---|---|---|
| `FM9` | `deform → mesh → STAGE → solve`, one container | 4 | **YES** |

**Run root, NEW:** `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM9-a2-wing-freshmesh-arrives`.
The `D6R2C`, `D6R2C-AFTER`, `D6R2C-AFTER8R2` and `D6R2C-AFTER9R2` roots are all in `FORBIDDEN_ROOTS`.
Ranks, cpuset, memory, uid, image digest and `O_mp` mounted `:ro` are inherited unchanged.
**Nothing is stopped by a cap** (directive #17).

---

## 6. THE MONITOR

**None.** Primal-only, no optimiser, no adjoint; the item-7 stop rules have no iterate to act on. A
primal that fails to converge is `H4` completion and §3a, not a stop rule.

---

## 7. THE PLANTED CONTROL (rule 3)

`PLANT = 1.234e-03`, planted into values read back from disk; the grader **REFUSES** if any plant leaves
the verdict at `PASS`. Plants: `CD_fresh`, the inherited `Jf`, `H1`'s `worst_dist`, and **`M1`'s
measured point difference for two separate conditions**.

`--selftest` drives **41 grader, 19 stage and 13 launcher controls**, both directions, on synthetic
trees. **A failing control for every gate**, anchored to this document's literals **typed as assertions,
not as sources** — including **the exact `FM8` state**, every condition un-staged, which must be
`NOT A RESULT` with all three named.
**Driven at this draft: `D6R2C_FM9_GRADE SELFTEST PASS n=41`, `D6R2C_FM9_STAGE SELFTEST PASS n=19`,
`D6R2C_FM9_LAUNCH SELFTEST PASS n=13`, all exit 0.**

---

## 8. COST (rule 12)

**Measured anchor:** `FM5` end to end — container, deform, mesh generation and one stalled
1000-iteration primal — **114 s wall = 7.600 core-min** (its ledger row, `rc = 1`).

| phase | wall s | basis |
|---|---|---|
| everything `FM5` did | **114.0** | **measured** |
| `stage` — the one registered change | **5.0** | **ESTIMATE, LABELLED** — file copy and directory removal |
| re-decomposition of the fresh mesh at solve | **20.0** | **ESTIMATE, LABELLED** |
| `cl05` and `cl06`, which `FM5` never reached | **32.0** | `2 × 16.0`, from `FM5`'s own per-condition primal |
| **TOTAL** | **171.0** | |

```
PREDICTION      171.0 s × 4 ranks / 60 = 11.400 core-min
REGISTERED CAP  3.00 × 11.400          = 34.200 core-min
```

**The cap is 3.00× the REGISTERED prediction, not 3× an unrounded intermediate.** Derived dollars
**$0.0098**; at the cap **$0.0292** — **DERIVED, NOT MEASURED**, `cost_basis` **reported-by-owner**.
**The cap has one source:** the grader derives it and the launcher **asks** the grader, after `G-FREEZE`.
**Calibration row OWED** at completion.

---

## 9. THE GRADED QUANTITY

```
J = 0.25 × CD04  +  0.50 × CD05  +  0.25 × CD06
targets: cl04 → CL = 0.400 , cl05 → CL = 0.500 , cl06 → CL = 0.600
```
Carried unchanged from `PREREGISTRATION.md` §1. The grader recomputes `J` from the per-condition `CD`.
Mesh: **38,304 cells, 40,209 points**, `M∞ = 0.288`, compressible subsonic.

---

## 10. WHAT THIS ITEM DOES NOT CLAIM

- **It does not re-grade `FM5`, `FM7`, `FM8` or `O_mp`.**
- **It does not claim `FM9` will converge.** §3a registers both outcomes as results.
- **It does not transfer any field**, and §2b says why that is a subtraction and not an omission.
- **It is not a grid study.** No Roache triple, no GCI, no observed order.
- **It does not touch `primalMinResTol`.**
- **It does not correct the fresh-mesh-floor description in the `GS1` registration.** That is frozen and
  its addendum belongs to whoever ratified it.

---

## 11. THE FROZEN INSTRUMENTS

| file | role | md5 | selftest |
|---|---|---|---|
| `d6r2c_fm9_grade.py` | **THE GRADING PATH** — `M1`, `H1`, `H3`, `H4`, the plants, `--print-cap` | `b3a07cfa4d61f44ac0b555c64c31669b` | **`PASS n=41`** |
| `d6r2c_fm9_stage.py` | **THE ONE REGISTERED CHANGE** — staging and the reconstruction the gate uses | `ea6d180fda38a3980bbb275b86d192c1` | **`PASS n=19`** |
| `d6r2c_fm9_run_arm.sh` | launcher — `G-ROOT`, `G-BOX`, `G-FREEZE`, `G-DEPS`, `G-COLD`. **Carries no cap** | `3f0c1fc6ab8f58b790e26a8a16018f96` | **`PASS n=13`** |

**REUSED UNCHANGED, and the pins are the evidence that nothing else moved:**

| file | md5 |
|---|---|
| `d6r2c_freshmesh.py` — `deform`, `mesh`, `solve` | **`1d15ce361673ca600d565280441b67e0`** |
| `d6r2c_decomp.py` — its library | **`42ec0dd582584812a69129a474b2783e`** |
| `d6r2c_opt_runScript.py` — the frozen model | **`2f2ae43a627146cf8e0f065b035ada4b`** |

**`d6r2c_fm6_init.py` IS NEITHER STAGED NOR PINNED HERE**, and a launcher control asserts it is not
referenced in the executed path — the index transfer is invalid on this arm and staging it would invite
its use.

### 11a. THE HONEST GAP

**`d6r2c_fm9_stage.py` has never run against a real decomposed case**, and **no arm has ever reached a
solve with the fresh mesh loaded**, so the solve phase's behaviour on it is unmeasured. `--selftest`
drives the pure logic: staging, removal, the reconstruction, and every refusal path.
**Registered in advance:** if `phase stage` cannot remove a decomposition, or `M1` reports the mesh did
not arrive, that is a **producer defect** — stopped, `NOT A RESULT`, repaired under
`VERIFICATION_CHARTER` §2d.1, **and the grading path is not touched by such a repair.**

---

## 12. THE CONSTANT SWEEP

Per `PREREGISTRATION_AFTER_ITEM8_R2.md` §8c: every constant in every named instrument compared against
this document, **reported in full including matches**. Result in §12a.

### 12a. THE SWEEP, EVERY ROW

**24 rows. 24 OK. 0 mismatches.** Where a constant lives in **both** instruments — `BASE_POINTS_MD5`,
`STALE_PROC_POINTS_MD5`, `RUN_DIRS` — the two agree with each other as well as with this text.

Covered: both mesh hashes (the base, and the one three arms actually solved on); the registered cell and
point counts; the processor count; `SHAPE_MATCH_TOL` and `H1`'s registered `worst_dist`; `FM_BAND_ABS`
and `Jf`; the `genWingMesh.py` and runscript pins; `primalMinResTol`; `PREDICTION_CORE_MIN`,
`CAP_FACTOR` and the derived cap; `PLANT`; the objective weights; the condition list; the staged mesh
file set; the stage record's filename; both reused pins; **the absence of a cap literal in the
launcher**; and **the absence of the invalid field transfer from the staged set and the pin block**.

**TWO ROWS FAILED ON THE FIRST PASS AND BOTH WERE GAPS IN THIS DOCUMENT, NOT IN THE INSTRUMENTS** — the
full `c7f5feda…` hash appeared only truncated, and the stage record's filename was nowhere in the text.
Closed at §1a, §3 and §2a. **Third time this check has caught exactly this shape, and all three times
the instruments were right and the prose was short.**

---

## ADDENDUM 5 — 2026-09-13 — THE CPUSET COLLISION, THE GRADER'S DEAD ENTRY POINT, AND `FM10`

**This addendum alters no gate, no threshold, no cap and no label.** `FM9`'s row stands at
**`NOT A RESULT`** and is never re-seeded. `FM10` is the re-run and carries the **identical registered
cap of 34.200 core-minutes** from §8. Repairs land under `VERIFICATION_CHARTER` §2d.1; the grading path
is unchanged in what it computes.

### A5.1 — `FM9` CROSSED ITS CAP BECAUSE I PUT IT ON CORES ANOTHER ARM WAS USING

`FM9` was launched onto cpuset `2,3,4,5` — **the same four cores `DEC7` already held** — putting eight
MPI ranks on four cores. Measured on `DEC7`'s own log: its clock/exec ratio moved from ~1.00–1.15
across thousands of samples to a steady **1.98–2.19**, and recovered to 0.77–1.20 the moment `FM9` was
stopped. `DEC7` ran at half speed for roughly fifteen minutes. `FM9`'s ledger row:
`rc=137 wall_s=950 core_min=63.333 cap=34.200`, `CAP_CROSSED`. **N-D4 already records this class** — a
pinned 4-rank DAFoam job degrading 21.5× under co-tenants.

**`guard_box` was running and it passed.** It measured `load1 = 41 of 96`, **which was true and
irrelevant**: a box-level average over 96 cores cannot see four saturated ones. That is a guard reading
an **adjacent quantity** — L-595 — and it is the fourth member of that family.

### A5.2 — `G-CPUSET`: A LAUNCH PRECONDITION THAT REFUSES TO START AND STOPS NOTHING

New in `d6r2c_fm9_run_arm.sh`, structurally identical to `guard_box`'s load and swap limbs:

- **`CPUSET` is no longer a constant** (E5). It is chosen at launch by `free_cpuset()` from cores
  nothing else is using. The selftest asserts **no `^CPUSET=<digit>` assignment survives in the file**.
- **`guard_cpuset()` refuses to start** (E6) if the chosen set intersects the occupied set, and names
  the clashing cores. If no `RANKS` cores are free, **the arm does not start** — waiting for the box is
  the default, not sharing it.
- **Occupancy has two sources and they are unioned**, because each alone has the other's blind spot.

**`occupied_cpus()`** reads every running container's `HostConfig.CpusetCpus`.
**`busy_cpus()`** samples `/proc/stat` twice over `BUSY_INTERVAL = 2.0 s` and calls a core occupied at
or above `BUSY_PCT`. **The second source is not theoretical.** Measured 2026-09-13, minutes after
`DEC7` exited: **`docker ps` was empty and reported no occupied cores at all, while cores 1, 2 and 7
sat at 100%.** The old hardcoded `2,3,4,5` would have put two ranks on core 2 **and the container limb
would have called it free** — bare-metal `mpirun` from another team is invisible to the daemon exactly
as fleet agents are invisible to `pgrep` (L-41). Driven live against the current box, the guard
**refuses `2,3,4,5` naming core 2**, and `free_cpuset` chooses `3,4,5,6` instead.

### A5.3 — `BUSY_PCT` WAS REGISTERED WRONG AND ITS OWN CONTROL SAID SO BEFORE THE FREEZE

**Recorded because the correction is the evidence.** The first version of this addendum registered
`BUSY_PCT = 50.0` as **derived**: a 2.0 s sample of all 96 cores gave 37 at ≥90% busy, 59 at <10%, and
**not one core in between**, so 50.0 was the midpoint of a measured empty band and every threshold in
`(0.5, 100)` would partition identically. A control was written asserting exactly that.

**The control failed on its first run.** Over a 1.0 s window the same box gives **40 cores at ≥1%, 38
at ≥50%, 36 at ≥99%**. The band is not empty; it only looked empty at one interval, and a handful of
cores are genuinely partially loaded. **`BUSY_PCT` is therefore not a derived separator and this
document no longer calls it one.** It is set to **1.0**, the conservative end of a guard whose only
action is to refuse: any core doing measurable work counts as occupied. That costs nothing here — at
1% the box still showed 56 free cores against the 4 this arm needs.

What is asserted instead is the property that **is** true of the reader: **monotonicity** — the busy
set at 1% contains the set at 99%, so the most conservative setting is also the widest. The count at
each end is **printed every run**, and the difference is the partially-loaded population the first
claim denied existed.

### A5.4 — THE GRADER COULD ONLY EVER HAVE RETURNED `NOT A RESULT`

`d6r2c_fm9_grade.py` was forked from `d6r2c_fm6_grade.py`, which has no `--log`. The launcher emitted
`--log`, the parser did not accept it, and `main()` never passed `log_path` — so on the CLI path the
convergence limbs and the mesh corroboration limb were skipped and **the grader's only reachable
verdict was `NOT A RESULT`, whatever the arm did.** The selftest had driven the *function* and the
*entry point* was shipped: L-595's shape again, inside my own instrument.

Repaired: `--log` added to the parser, `log_path=a.log` passed through `main()`, and **a control that
drives `main()` through the CLI**, asserting a `PASS` where the unrepaired entry point produced an
unconditional `NOT A RESULT`, plus a negative control asserting that `main()` *without* `--log` is
still `NOT A RESULT`. **No gate, threshold, cap or label moved** — §2d.1.

**A correction I owe the record:** I reported to my supervisor that `d6r2c_gs2_grade.py` shared this
hole. **That was wrong.** `d6r2c_gs2_grade.py` already accepts `--log` and already passes `log_path`,
as does `d6r2c_gs1_grade.py`. **Only the `FM9` grader had the defect**, because only it was forked from
the `FM6` grader. No change was made to either `GS` grader.

### A5.5 — `FM10`, AND THE REPINNED INSTRUMENTS

`FM10` is accepted by the launcher alongside `FM9` and resolves to the **same cap of 34.200** from the
same single source (`--print-cap`), asserted in the selftest. **`FM9`'s directory and its `NOT A
RESULT` row are untouched.**

| Instrument | md5 at `317ab5b3` | md5 now | Changed |
|---|---|---|---|
| `d6r2c_fm9_stage.py` | `ea6d180fda38a3980bbb275b86d192c1` | `ea6d180fda38a3980bbb275b86d192c1` | **no** |
| `d6r2c_fm9_grade.py` | `b3a07cfa4d61f44ac0b555c64c31669b` | `bcf2c674741955066b8a09f97d6e4262` | yes — A5.4 |
| `d6r2c_fm9_run_arm.sh` | `3f0c1fc6ab8f58b790e26a8a16018f96` | `8694935d672e87109fad65dc6ef291e5` | yes — A5.2, and the grader repin |

`G-FREEZE` refused the tree the moment the grader's bytes moved, which is the pin doing its job; the
launcher's `# PIN d6r2c_fm9_grade.py` line carries the new md5. Selftests after every repair:
**grader `PASS n=47`**, **launcher `PASS n=27`** (13 before this addendum).

### A5.6 — WHAT THIS ADDENDUM DOES NOT CLAIM

- It does **not** claim `FM10` will converge. Nothing here touches the open question of whether a
  freshly extruded mesh reaches a converged primal at all; `M1` still has no datum.
- It does **not** claim the occupancy union is complete. A process that starts **after** the sample and
  before `mpirun` is invisible to both sources, and a core idle in the sampled instant reads free.
  **This is a launch precondition, not a supervisor**: it cannot protect a run already under way.
- It does **not** claim `BUSY_PCT` is derived. §A5.3 says the opposite in the document and in the code.
- It does **not** re-open any gate. `FM9` stays `NOT A RESULT`.
