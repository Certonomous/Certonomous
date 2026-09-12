# SO-3a MULTIPOINT — CAP FORENSICS, THE OVERRUN DIAGNOSED BY CLASS, AND THE THREE-TERM COST ANCHORS. **NOT A PRE-REGISTRATION.**

**Dated 2026-09-12. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.**
**Nothing here is filed, sent, emailed, uploaded, registered, posted or commented outside this box** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

> **THIS DOCUMENT FREEZES NOTHING.** It registers no gate, no threshold, no band, no cap, no label and no run. It is not a rule-2 freeze and **may never be cited as one**. It carries three things: a **supersession finding** that stops a duplicate registration being written; the **per-arm diagnosis by class** of SO-3aF2's 9.2833 core-min against a 9.0 ceiling; and the **measured cost anchors** for the three-term convention adopted for dafoam on 2026-09-12.
>
> **ZERO SOLVER CORE-MINUTES WERE SPENT BY THE LANE THAT WROTE IT.** No container of any kind was started. Every number below is read from an artefact that was already on disk, and every artefact is named by absolute path.

---

## 1. ⚠⚠ THE TASK'S PREMISE IS SUPERSEDED ON DISK. A NEW SO-3a GRADIENT FREEZE WOULD BE THE FOURTH DUPLICATE, AND I DID NOT WRITE ONE.

The brief this lane was given states that **no comparator exists by name** for the SO-3a incompressible multipoint and that a gradeable multipoint run therefore needs a new rule-2 gradient freeze plus a new comparator. **That is true of the feasibility item and false of the line.** It is corrected here rather than acted on, because acting on it would have produced a second record for a run that already has one.

### 1.1 The incompressible multipoint GRADIENT rung ran, graded, and carries both toolchain rows

`cases/dafoam/ladder-a/A1/curriculum_SO3aR2/PREREGISTRATION.md` is titled *"NACA0012 ALPHA-MULTIPOINT WEIGHTED OBJECTIVE, INCOMPRESSIBLE: the FD-VERIFIED MULTIPOINT GRADIENT RUNG"*, is **FROZEN** at `181bf279` and armed at `ffae7724c`, and its comparator **`cases/dafoam/ladder-a/A1/curriculum_SO3aR2/so3ar2_grade.py` exists by name.** It ran on 2026-08-31: **five of five declared stages, `chain_rc = 0`, `truncated = false`.**

| | SHIPPED | PATCHED |
|---|---|---|
| image | `dafoam/opt-packages:latest` | `dafoam-idwarp-rot:v1` |
| digest | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` |
| `libidwarp.so` md5, printed from inside the loading process | `f0fcb488e0e98156575cd19548e91663` | `85f59e87253e0a71a813f64ca6e4c425` |
| `G5J` objective aggregate rel err | **31.498 %** | **2.678 %** |
| worst component | **47.189 %** | 4.060 % |
| pairs pass / graded | 2 / 4 | 4 / 4 |
| sign flips | 0 | 0 |
| **row verdict** | **`GATE FAIL`** | **`PASS`** |

**Item verdict `GATE FAIL`**, `verdict_source = COPIED FROM THE COMPARATOR ARTEFACT`. The FD table is three steps per pair with the plateau proved **per pair** at a 10.0 % tolerance, band D 5.0 %, band E 5.0 %, `min_graded_pairs` 3. The per-scenario lift gradients `G5C` pass on both rows at 0.021–0.196 %.

**Artefacts** (all present, re-read by this lane today):
`/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient/SO3aR2_STOP_MARKER.json`;
`…/SO3aR2_grade_20260831T230221Z.json`, md5 **`29dfe8ea10aa5d6bac4730aed4fec656`** — **which equals the `grade_json_md5` the stop marker carries**, so the verdict chain is self-consistent on bytes and not merely on prose;
`…/ledger.txt`, five `ARM=` rows (`MESH`, `X-S`, `F-S`, `X-P`, `F-P`), every one `rc=0`, `oomkilled=false`, np = 1, cpuset 14, memory 12g.

### 1.2 The incompressible multipoint OPTIMISATION rung also ran, and is `PASS` on both rows

`docs/LAB_STATE.md:11455` records **SO-3**, prereg `ab27dff7`, `SO3_grade_20260901T040709Z.json`, chain COMPLETE 7/7: **`PASS`, BOTH ROWS** — weighted `J` 0.02180598 → 0.01828320, **−16.16 %**, 10 majors against `max_iter` 50, optimiser printed `Optimal Solution Found.`, **endpoint FD `PASS` on both rows** (`DAFOAM_CHARTER.md` §9's final-design-point check, discharged). Measured **28.900 core-min** against 228.59 registered, ratio **0.126**. The compressible twin **D19M** is `GATE REACHED` on both rows at **35.166 core-min**, ratio 1.0313.

**Sanaa's 2026-09-11 deliverable — the multipoint optimisations, compressible and incompressible — is delivered on both axes.**

> **⚠ THE CAVEAT TRAVELS OR THE HEADLINE IS FALSE.** `CL` is **unconstrained and collapses in both** optimisations: SO-3's lift goes 0.31190 / 0.49877 / 0.66398 → **−0.05676** / 0.15320 / 0.36119, and D19M's likewise to **−0.15737**. **Lift goes NEGATIVE at point 0 in both.** A drag reduction quoted without the lift collapse is a false statement (`docs/LAB_STATE.md:11459`).

### 1.3 The live successor already exists, is already frozen, and is what the cost anchors in §4 are for

**MP-A1** — `cases/dafoam/ladder-a/A1/curriculum_MP_A1/PREREGISTRATION.md`, **FROZEN 2026-09-07**, SO-3 plus **per-point `CL` EQUALITY** (drag-min at fixed lift), which is precisely the fix for the §1.2 collapse. **Compute is NOT launched:** the `NOT_FROZEN` sentinel is retained deliberately as the launch-block, and the registered run root `/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1-a1-naca0012-alpha-multipoint-fixedlift-optimisation` is **ABSENT**. Estimate **58.63 core-min**, ceiling **183.5**.

### 1.4 What this lane therefore did NOT do, and why refusing was the smaller error

**No new registration was written and no new comparator was authored.** Writing either would have been:

1. **A duplicate record for a run that already has one** — the one thing a lane is told not to manufacture.
2. **A rule-2 violation in substance.** Compute has already run on this exact question: SO-3aR2, 2026-08-31, **14.318 core-min** (0.167 + 2.517 + 4.367 + 2.517 + 4.750, summed from its own ledger). Gates are closed after first compute. **And this lane has now SEEN the answers — 31.498 % and 2.678 % — so it is disqualified from setting a band for that gradient at all.** A gate chosen by an author who has read the result is not a gate, whatever number it carries.
3. **Redundant against a repair already ruled.** `docs/LAB_STATE.md:11460` names the real gap — SO-3 and SO-3aR2 had no `RESULTS.md` and no standing-verdict-table rows, so *"a reader consulting this family's STANDING VERDICT TABLE concludes the incompressible multipoint was never done."* A lane was ruled onto it; `cases/dafoam/INDEX.md` and `docs/dafoam/README.md` now carry SO-3aR2 rows. **That missing-record defect is the most probable reason the brief believed no comparator existed** — the work was real and the index was not.

**What remains genuinely owed is §2, §3 and §4 below, and they are owed regardless of which item runs next.**

---

## 2. THE OVERRUN, DIAGNOSED BY CLASS, PER ARM

`cases/dafoam/ladder-a/A1/feasibility_SO3a_multipoint/` spent **9.2833 core-min against a registered §7 item ceiling of 9.0 — over by 0.2833, 3.15 %.** The record names the breach and names **6.0167 core-min as waste**, but its own §A13.5 and §A14.3 leave the largest single component — the two `ATTRCENSUS` attempts, **6.0000 core-min** — as *"UNEXPLAINED … cause UNMEASURED, parked with its evidence intact."*

**It is explained here, by class, from artefacts that were on disk the whole time and were never read.**

### 2.1 The nine launches

Core-minutes from `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility/ledger.txt` (ranks = 1 throughout, so core-min = wall s ÷ 60).

| # | arm | stamp | rc | wall s | core-min | cap | **cause class** |
|---|---|---|---|---|---|---|---|
| 1–3 | `MESH` | 214815Z, 221206Z, 222417Z | 127, 127, 1 | — | **0.0167** combined, archived | 3.0 | **DELIVERY** — inputs, environment, and the shell option that hid both. Measured and closed by the item's own addenda. |
| 4 | `MESH` | 223426Z | 0 | 3 | 0.0500 | 3.0 | **COMPLETE.** Produced a mesh; graded `NOT A RESULT`. |
| 5 | `XM` | 224931Z | 7 | 21 | 0.3500 | 6.0 | **REGISTERED REFUSAL** — the staging precondition fired as designed. Not waste: it bought three converged primals. |
| 6 | `ATTRCENSUS` | 230242Z | 9 | 221 | **3.6833** | 2.0 | **INSTRUMENT/IMPORT + BOOKKEEPING/PLUMBING — diagnosed in §2.2.** |
| 7 | `ATTRCENSUS` | 231752Z | 124 | 138 | **2.3000** | 2.0 | **same cause; killed by the in-container deadline before it could reach the same refusal.** |
| 8 | `XM` | 233357Z | 7 | 24 | 0.4000 | 6.0 | **REGISTERED REFUSAL** — produced the enumeration behind the item's one measured finding. |
| 9 | `XM` | 20260904T013622Z | 0 | 149 | **2.4833** | 6.0 | **COMPLETE, cold-start dominated** — §4.1. |

Rows 5–8 sum to **6.7333 core-min = 72.66 % of the 9.2666 of ledger rows.** That is the figure whose cause the record admits was never classified. Rows 5 and 8 are registered refusals and were already understood; **rows 6 and 7, the 5.9833 core-min the record calls unexplained, are diagnosed below.**

### 2.2 ⚠ THE CENSUS STALL: A COLD `matplotlib` FONT-CACHE BUILD, FORCED BY THE CENSUS'S OWN `getattr` SWEEP, ON AN ARM THAT WAS UNSATISFIABLE BY CONSTRUCTION ANYWAY

**THE DISCRIMINATOR IS EXACT AND IT IS ONE LINE.** Both census arm logs open with a line the working arm's log does not contain:

* `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility/ATTRCENSUS/ATTRCENSUS.log` — **3 lines, 208 bytes**, first line `Matplotlib is building the font cache; this may take a moment.`
* `…/ATTRCENSUS_stopped_rc9_20260903T231526Z/ATTRCENSUS.log` — **4 lines, 342 bytes**, same first line.
* `…/XM/XM.log` — **1,831 lines, 63,350 bytes.** Occurrences of `font cache`: **0.** Occurrences of `VSPAERO`: **1**, and that one line is common to all three.

**So the two containers that burned 6.0 core-min built the font cache and the container that produced the item's only result did not.** Both attempts rebuilt it, from the same image digest, which means **the cache is not persisted for the runtime UID and is reconstructed on every `--rm` container that imports `matplotlib`.** A font-cache build is a single-threaded scan of every font file on the system — which is exactly the signature the record observed and could not name: **208 bytes of log, static for roughly two minutes, at 1.55 % CPU.**

**THE MECHANISM, from source.** `cases/dafoam/ladder-a/A1/feasibility_SO3a_multipoint/so3af2_attr_census.py` performs an unguarded attribute sweep over the mphys/OpenMDAO object graph:

```
531:            names = sorted(set(dir(obj)))
540:                val = getattr(obj, name)
```

**A `dir()` + `getattr()` sweep forces every lazily-imported attribute to import.** The `XM` producer never sweeps, so it never touches the plotting stack and never pays the cache. **The census paid it because of what a census is**, not because of contention, memory or the solver — and the two attempts' 187.7 s and 107.9 s of container time were consumed before either reached any work.

**AND THE ARM COULD NOT HAVE SUCCEEDED AT ANY BUDGET.** The first attempt's log, after the font cache completed, carries the producer's own refusal:

> `SO3aF2 PRODUCER REFUSAL: WRONG_WORKING_DIRECTORY cwd=/mnt/ATTRCENSUS expected basename 'XM' -- the reader's contract is <root>/XM/...`

The census arm ran in `/mnt/ATTRCENSUS` while the producer's path contract requires a `cwd` whose basename is `XM`. **The second attempt was killed by the deadline before it could print the same line.** So the record's *"no enumeration was produced"* has a cause, and the cause is not mysterious: **it is the same path-contract defect class the item had already closed twice on the `MESH` arm, arriving a third time on an arm nobody re-checked.**

**CAUSE CLASS, REGISTERED SO IT CANNOT RECUR SILENTLY:**

> **`INSTRUMENT/IMPORT`** — a `dir()`/`getattr()` sweep forcing a cold `matplotlib` font-cache build inside a `--rm` container, single-threaded at ~1.5 % of one core; **compounded by `BOOKKEEPING/PLUMBING`** — a working-directory contract violated at launch, making the arm unsatisfiable by construction. **Neither limb is physics, contention, memory or the solver, and none of the 5.9833 core-min was ever going to buy an enumeration.**

**THE REPAIR IS CHEAP AND IT APPLIES TO EVERY dafoam CONTAINER THIS LAB STARTS**, because this is the high tail of the `F` term in §4: **set `MPLCONFIGDIR` to a writable bind-mounted path, or keep the plotting stack out of an instrument's import graph.** Recommended, **not taken** — a launcher change is the supervisor's to order.

---

## 3. THREE INSTRUMENTS DISAGREE ABOUT WHAT A CAP IS, ONE ORPHAN NUMBER PRETENDS TO BE A FOURTH, AND ONLY ONE CAN KILL

### 3.1 The census

| | instrument | where | what it does | **can it stop a run?** |
|---|---|---|---|---|
| **A** | launcher post-`docker wait` check | `feasibility_SO3a_multipoint/so3af2_run_arm.sh`, `docker wait` at `:497`, `cap_exceeded` computed and written at `:517`/`:520` | computes `cap_exceeded` **after** the container has already ended | **NO.** It reports a breach that something else ended. |
| **B** | queue-runner `CAP_OVERRUN.txt` | `scripts/queue_runner.py`; enforcement half pre-registered at `docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md` | writes a file at 1.00 × `cap_core_min_registered` | **NO**, and it says so in its own text. The clause is **ADVISORY, INERT, OFF**; switching it on is **Sanaa's alone**. |
| **C** | **in-container deadline** | `so3af2_run_arm.sh:272` derives `DEADLINE_S = cap × 60 / ranks − FRAME_ALLOWANCE_S`; `:480` wraps the arm in `timeout -k $KILL_AFTER $DEADLINE_S` **inside** the container | kills the process with no agent alive | **YES — the only one.** |
| **—** | the **item CEILING**, `9.0` | `so3af2_run_arm.sh:131` sets it, `:517` echoes it into every ledger row | **nothing compares the cumulative item total against it.** Two occurrences, one file. | **It is not an instrument at all.** |

**A's blindness is measured, not argued.** On `230242Z` it printed `cap_exceeded=1` correctly **only because a lane had already stopped the container by hand.** Left alone, `docker wait` blocks indefinitely and the registered stop rule never fires.

**B's own file states the conflict against the rule it is named for.** `CAP_OVERRUN.txt` in the feasibility directory reads *"CAP OVERRUN REPORTED, NOT ENFORCED … The run was NOT killed"* against `COMPUTE_BUDGET_CHARTER.md:197` and `CLAUDE.md` rule 12, both of which say an overrun **stops** the run.

**The orphan is the worst of the four and it is `CLAUDE.md` rule 14's shape exactly** — a registered number with no call site. A cap at least reports. **A ceiling written into every row and read by nothing produced the 3.15 % breach**, because the per-arm caps all passed individually and no instrument was ever looking at the sum.

### 3.2 **REGISTER ONE: instrument C, and invert it from the frame's measured MAXIMUM, not from a constant fitted at n = 1**

**C governs, because it is the only one with an actuator.** It is proved to work: `231752Z` returned **`rc = 124`, unattended.**

> **BUT A DEADLINE THAT FIRES IS NOT YET A GUARANTEE THAT THE CAP HOLDS, AND HERE IS THE MEASUREMENT OF WHY.** That arm landed **`core_min = 2.3000` against a cap of 2.0, `cap_exceeded = 1`, even though the deadline fired.**

**The frame is not a constant.** Container durations from each arm's own `docker inspect` sidecar (`StartedAt` → `FinishedAt`), against the ledger's `wall_s`:

| arm | container duration s | ledger `wall_s` | **frame s** |
|---|---|---|---|
| `XM` 233357Z | 24.449 | 24 | **−0.449** |
| `XM` 013622Z | 137.102 | 149 | **+11.898** |
| `ATTRCENSUS` 231752Z | 107.897 | 138 | **+30.103** |
| `ATTRCENSUS` 230242Z | 187.726 | 221 | **+33.274** |

`FRAME_ALLOWANCE_S = 15` (`so3af2_run_arm.sh:130`) is a constant **fitted at n = 1 in the middle of a 33.7-second spread**, and on the two arms where the cap was actually binding the frame was **30.1 s and 33.3 s — 2.0× and 2.2× the allowance.** That is the whole of the residual overrun. The derived deadlines check out arithmetically (`MESH` 165 s, `XM` 345 s, `ATTRCENSUS` 105 s, all `cap × 60 / ranks − 15`), and the `231752Z` container ran **107.897 s against its 105 s deadline**, i.e. the kill itself was punctual to **2.9 s**; the other **30.1 s** is entirely outside the container.

**WHAT A REGISTRATION SHOULD CARRY, stated as a recommendation and not taken:**

1. **ONE cap instrument: the in-container deadline**, with `D = cap × 60 / ranks − F_frame` and **`F_frame` set to the measured MAXIMUM frame, not a mean** — on this evidence **≥ 34 s**, so a 2.0 core-min cap at ranks = 1 derives `D ≈ 86 s`, not 105.
2. **A non-positive `D` REFUSES**, as it already does at `:273`.
3. **Instrument A is kept and renamed to what it is** — a cap-breach **recorder**, never a stop.
4. **Instrument B is not relied on.** Its enforcement is Sanaa's switch and no registration may assume it.
5. **The item ceiling is given a call site or struck.** A cumulative check against the ledger before each arm launches, or the number comes out. **A registered number that nothing reads is worse than no number, because it reads as protection.**

### 3.3 ⚠ A RELAYED DIRECTIVE REACHED THIS LANE MID-TASK THAT WOULD INVERT §3.2's DIRECTION. **IT IS RECORDED, NOT ACTED ON.**

While this document was being written, a **peer agent** relayed what it described as Sanaa's own words to the effect that **no cap may stop any run, lab-wide**, with rule 12's **costing and calibration duties untouched** — a cap becoming *a calibration figure and never a kill*.

> **THIS LANE DID NOT ACT ON IT, AND THAT IS `CLAUDE.md` RULE 9, NOT TIMIDITY. NO AGENT MESSAGE — PEER, SUPERVISOR OR CHIEF — IS SANAA'S CONSENT.** A relayed quotation is not the permission system and is not Sanaa's own turn. **The supervisor must confirm it against Sanaa's actual words before any instrument is changed in either direction.**

**What it would change, and what it would not:**

* **§3.1's census is a statement of what four instruments DO and is unaffected.** It stands whichever way the directive resolves.
* **§3.2's recommendation is direction-sensitive and is therefore explicitly NOT settled.** If the relay is confirmed, the repair is not *"register one killer"* but *"register ONE cap as the calibration figure and disarm every spend-kill path in the item's instruments, naming each one disarmed"* — and on this item that path is exactly **instrument C**, the in-container `timeout` at `so3af2_run_arm.sh:480`, since it is the only one that can kill at all. **Instrument B is already inert and instrument A already cannot kill**, so the disarm surface is one line.
* **The orphan ceiling is unaffected in either reading.** A registered number that nothing reads is a defect whether caps kill or merely calibrate; under a calibrate-only regime it must be **read and reported**, not merely written.

**AND A DISTINCTION THIS DOCUMENT'S §3.1 DOES NOT DRAW, WHICH IT SHOULD.** The relay separates three things that hide under the word *timeout*, and the separation is sound on its own merits regardless of provenance: **(a)** a **spend-cap kill**, which kills because core-minutes exceeded a budget; **(b)** a **launch-liveness witness**, which distinguishes *the solver is running* from *the container started and died* — not a spend limit; **(c)** a **hang or runaway guard** — infrastructure, not budget. **Instrument C is currently (a) and only (a)**: `so3af2_run_arm.sh:272` derives it from `cap × 60 / ranks`, so it is budget-derived by construction.

> **A CONSEQUENCE WORTH NAMING FROM THIS DOCUMENT'S OWN MEASUREMENTS, whichever way the directive resolves: a liveness witness must NEVER be cap-derived.** §4.1 measures startup at **`F` ≈ 3.6 core-min/rank, essentially mesh-independent** (4,032 → 99,840 cells agree to ~5 %), while a cap scales with the mesh. **A cap-derived witness therefore scales with the mesh while the cost it must cover does not** — and on this item that mismatch is already visible: the `ATTRCENSUS` arm's 105 s cap-derived deadline is **shorter than the ≥ 107.9 s its own startup demonstrably needed**, so it killed a container during import and could never have done otherwise.

---

## 4. THE COST ANCHORS, UNDER THE THREE-TERM CONVENTION — `C = F(n) + r(N)·N·iters + W(N, writes)`

Adopted for dafoam 2026-09-12, `[lab-attributed]`, `docs/COST_CALIBRATION.md` row `C-20260912T005048.507107Z-c94d1535`. **Three separately named terms, never one.**
**`cost_basis`: REPORTED-BY-OWNER, NOT MEASURED.** Wall seconds and ranks are read from ledger rows and `docker inspect`; the **$0.0513/core-h** rate is owner-stated for c7a.4xlarge and **the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). **Every dollar figure below is DERIVED, NEVER MEASURED.**

### 4.1 `F` — and it is **not a constant on this case, it is a 22× distribution**

**The standing anchor: `F ≈ 3.6 core-min per rank`**, cited to a **measured `waited_s`** and not assumed — D8G's `waited_s = 215` plus 5 s measured post-solve teardown = 220 s at 4 ranks = **14.667 core-min → 3.667 core-min/rank**
(`/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple/ledger.txt`; `cases/dafoam/ladder-a/A6/curriculum_D8G/PREREGISTRATION.md` §6.2 `:490`).

**Independently corroborated on THIS case, from a completely different failure.** The `ATTRCENSUS` `230242Z` arm spent **3.6833 core-min at ranks = 1 and never left startup** (§2.2) — **0.45 % from the anchor.** *Stated as corroboration of magnitude and not as a replicate:* the census pays a cold font-cache build that D8G's arm does not, so the two compositions differ and the closeness is partly coincidence. It is quoted because it independently confirms the **order**, from a 4,032-cell 2-D case against a 5,568-cell one.

**⚠ THE FINDING THAT SHOULD CHANGE HOW `F` IS REGISTERED.** On **one case, one rank count, one image digest**, `F` measured three ways:

| state | arm | container s − solver s | **`F`, core-min** |
|---|---|---|---|
| **warm** | `XM` 233357Z | 24.449 − 14.11 | **0.172** |
| **cold** | `XM` 013622Z | 137.102 − 14.13 | **2.050** (11.9×) |
| **cold + forced `matplotlib` import** | `ATTRCENSUS` 230242Z | 187.726, never reached the solver | **3.128** container-only; **3.6833** with frame (21.4×) |

> **`F` IS NOT A POINT AND MUST NOT BE REGISTERED AS ONE.** For A1 at np = 1 the honest registration is a **band `[0.17, 3.69]` core-min with the point at the cold edge, 2.05**. This is the mechanism behind the feasibility item's own **6.21× estimate miss** on its clean arm, which its §A16.6 measured to be **entirely outside the solve** (three primals identical to 0.02 s; 137.1 s container against 24.4 s for the same work) and could only attribute, not measure, as page-cache state. **The attribution now has a named, testable second component: the import graph.**

**⚠ WHAT FRACTION OF `F` IS IDLE-CORE RENT — the number the convention says decides `np`.** Measured from the sampler's own series, `/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple/L1-P_20260911T234236Z_2435242.cpu.jsonl`, 14 samples over 196.83 s:

* For the **first 166.5 s — twelve consecutive samples — the container delivered `0.0847`–`0.2917` cores of the 4 it held**, none above 0.30, **mean 0.16215**. That is **4.05 % delivered, 95.95 % IDLE-CORE RENT.**
* Only at +181.7 s does delivery jump to **1.3153**, then 1.1482 — **that is the solve beginning**, and it is how the startup phase is identified rather than assumed.
* Over the full 14-sample window the mean is **0.31495 cores → 7.87 % delivered, 92.13 % rent.**

**This is not contention, and reading it as contention would produce the wrong repair.** The startup phase — container start, TensorFlow import in DAFoam init, `DASolver` construction — is essentially **serial and I/O-bound**, so it uses well under one core while holding `n`.

> **CONSEQUENCE FOR `np`, WHICH IS THE POINT OF MEASURING IT: `F(n) = 3.6 × n`, and ≈ 96 % of it buys nothing while holding `n` cores away from cfd, heat-transfer and ansys-verification. Raising `np` on a coarse level makes the cost worse with no return.** For a 4,032-cell A1 multipoint the answer is **np = 1** — which is independently what `DAFOAM_CHARTER.md` §5 requires (*serial before parallel; a new case's first FD verification is run at np = 1*) and what SO-3aR2 in fact ran (np = 1, cpuset 14). **At np = 4 the same item would rent ≈ 13.8 core-min of idle cores to buy ≈ 0.6 of work.**

### 4.2 `r(N)` — anchored **on this case**, so nothing is extrapolated and no band widening is owed

**MEASURED** from `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility/XM/XM.log`: cumulative `ExecutionTime = 14.13 s` (15 samples, **monotone with no reset**, so it is the whole process and not one solver), over **1,303 iterations** (443 + 436 + 424, the three run directories in `so3af2_M.json`), at **4,032 cells, np = 1**:

> **`r` = 14.13 / (4,032 × 1,303) = `2.6896e-6` core-s / cell / iteration.**

**Cross-checks at other cell counts, from other items' own logs:**

| case | cells | `r`, core-s/cell/iter |
|---|---|---|
| **A1 `SO3aF2`** | **4,032** | **2.6896e-6** |
| A3-derived (D8G anchor `:490`) | 41,760 | 2.7906e-6 |
| A3GC L3 | 99,840 | 2.9354e-6 |
| A3 (the anchor A3GC extrapolated FROM) | 399,360 | 2.0387e-6 |

**Spread across 4,032 → 99,840 cells, a 24.8× range: 9.2 %.**

> **⚠ A CORRECTION HANDED UP, BECAUSE IT CHANGES WHICH ANCHOR A REGISTRATION SHOULD PICK.** The convention's **1.44–2.16× "coarse costs more per cell" penalty** is measured against the **399,360-cell** run — and **that run is the outlier at `2.0387e-6`**, while everything from 4,032 to 99,840 cells sits inside `2.69`–`2.94e-6`. **So the penalty is a property of extrapolating DOWN from the largest anchor, not a property of coarse meshes.** Anchoring an A1 multipoint on the 399,360 figure would **under-price the solve rate by 24.2 %, i.e. the measured A1 rate is 31.9 % ABOVE it**; anchoring on A1's own measured rate extrapolates **1.0×** and therefore owes **no widening at all** under the convention's own ~4× rule.

### 4.3 `W` — **no measured anchor on this case. An upper bound is quoted instead of a number that was never measured.**

* The available figure is A3GC's: **12.26 core-min at four checkpoints, 99,840 cells, np = 4 → 3.065 core-min per write.** Scaled to 4,032 cells at np = 1 that is **≈ 0.031 core-min/write — `[EXTRAPOLATED DOWN 24.8×]`**, which the convention requires be widened, and which this lane does **not** quote as an estimate.
* **MEASURED UPPER BOUND, on this case:** the warm `XM` arm's **entire** non-solver time is **10.3 s**, and that 10.3 s contains `F` **and every write the arm performed**. Therefore **`W`(4,032 cells, 3 run directories) ≤ 0.172 core-min in total, ≤ 0.057 core-min per write.**

> **A registration either measures `W` in a first arm or carries the bound and says it is a bound. It does not quote a point value it has not measured** — and A3GC's row exists because a registration costed **zero** writes and paid 12.26 core-min for four.

### 4.4 Dollars, and the rule-12 comparison that is owed

* SO-3aF2 item: **9.2833 core-min = 0.154722 core-h = $0.00794 DERIVED, NEVER MEASURED.**
* SO-3aR2 item, summed from its own ledger: **14.318 core-min = 0.238633 core-h = $0.01224 DERIVED, NEVER MEASURED.**
* 0 GPU-h. **Zero solver core-minutes were spent producing this document.**

**⚠ AN OPEN RULE-12 EXPOSURE ON THE LIVE ITEM, found while assembling §4 and reported rather than absorbed.** **MP-A1's registered cost is a single per-major rate**, carried from SO-3's measured `O-S` 0.660 and `O-P` 0.695 core-min/major (`curriculum_MP_A1/PREREGISTRATION.md:186`), estimate **58.63**, ceiling **183.5**. **`F` is paid once per ARM, not once per major**, so a per-major rate silently multiplies `F` by the major count. On this case that errs **conservatively** (over-pricing) and the ceiling is 3.1× the estimate, so **no gate is at risk and nothing here asks for one to move**. What it costs is **attribution**: if the estimate misses, the miss cannot be split between startup, solve rate and writes, which is exactly the defect the three-term convention was adopted to end. **MP-A1 has recorded zero solver core-minutes, so a before-compute rule-2 amendment restating the same total as three named terms is legal** (`CLAUDE.md` rule 2). **NOT DRAFTED HERE — an amendment to a frozen registration is the supervisor's call, not a lane's.**

---

## 5. WHAT THIS LANE COULD NOT VERIFY, STATED PLAINLY

1. **Why the `matplotlib` cache is absent for the runtime UID was not tested.** The **discriminator** is measured (the line is present in both census logs and absent from `XM.log`); the **reason the image ships no usable cache** is inferred from the fact that both `--rm` containers rebuilt it. **Testing it costs one container and this lane started none.**
2. **The font-cache build was not timed directly.** It is bounded: attempt 2 reached **107.9 s** of container time with **3 lines of log and no refusal**, so the import phase exceeds 107.9 s. The split between font cache, DAFoam/TensorFlow import and OpenVSP within that window is **NOT MEASURED**.
3. **`W` has no measured anchor on this case** — §4.3 gives a bound, not a value.
4. **The `−0.449 s` frame** in §3.2 means `wall_s` and `docker inspect` do not measure the same span to sub-second precision. The three positive frames are large enough that the conclusion is unaffected, but **the frame basis is a difference of two differently-taken clocks and is stated as such.**
5. **Nothing in §1 was re-graded.** SO-3aR2's and SO-3's verdicts are **read from their frozen artefacts** and re-verified only to the extent that the stop marker's `grade_json_md5` was checked against the grade file on disk. **No comparator was re-run.**
6. **`docs/COST_CALIBRATION.md` carries no row for this document** and none is owed: no process completed here and no compute was spent.

---

## 6. STATUS

**`PENDING`** — forensics complete, nothing frozen, nothing registered, nothing enqueued, **zero solver core-minutes, no container started.** The three decisions this document raises and does **not** take are the supervisor's: **(a)** whether the SO-3a multipoint line needs any new registration at all given §1, or whether the live item is MP-A1; **(b)** the single-cap-instrument repair of §3.2, which changes a launcher; **(c)** the MP-A1 three-term cost amendment of §4.4, which touches a frozen file before its first compute; **(d)** the relayed no-cap-may-kill directive of §3.3, which **must be confirmed against Sanaa's own words before any instrument moves in either direction** — a peer agent's relay is not consent (`CLAUDE.md` rule 9). **SUBMISSIONS PARKED.**
