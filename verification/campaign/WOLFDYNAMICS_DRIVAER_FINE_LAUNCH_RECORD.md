# Wolf Dynamics DrivAer FINE — LAUNCH RECORD

**STATUS: `PENDING` — launched 2026-09-13T20:37:54Z, running. No verdict exists yet and none
may be written until the run completes and F1–F5 are graded.**

This file exists because **a session limit killed the whole fleet at ~19:10Z tonight** and
this run is ~36–40 h long. It is the resume handle: everything a later session needs to pick
this up without re-deriving it.

---

## 1. THE FREEZE — VERIFIED BY THIS LANE, NOT ACCEPTED ON RELAY

| item | value |
|---|---|
| **Freeze commit** | **`58d24721e15bc18604d0f638775cfb09a4406242`** |
| **Correction 1** | **`541a04cb1e1aca6c4f35c59860077a30604698e9`** |
| Blob at freeze | `3c223c8b57de8ae2a769a2484c0eb7dad30fc864` |
| Blob at correction 1 | `d3c2b04c7370d4b6361a8be8c4a4ebc1f194a77d` |
| **Blob live on disk at launch** | **`d3c2b04c7370d4b6361a8be8c4a4ebc1f194a77d` — MATCHES** |

**`git hash-object` of the live pre-registration equals the blob committed at correction 1.
The frozen file IS the file that will grade this run.** Both commits are ancestors of HEAD.

**Correction 1 was read as a diff, not taken as described.** `git diff 58d24721 541a04cb`
touches **one file** and adds **25 lines at the foot only** (lines 405+). It asserts *"Lines
whose number changed above this section: 0"* and that assertion is **true as measured** — the
diff has no hunk above line 404. **It alters no gate, threshold, cap or label.** It strikes a
stale "NOT FROZEN" footer at line 396 and the "the lane will not launch until the supervisor
has committed" clause at line 400. The freeze commit itself changed **only the status header**
— `git diff 29e9be0c 58d24721` is a single hunk at lines 1–6. **Gates F1–F5 are byte-identical
to the drafted ones.**

---

## 2. THE RUN

| item | value |
|---|---|
| Run directory | `/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/fine_R1` |
| `LAUNCH_STAMP.txt` | **2026-09-13T20:37:42Z** (written **before** the container started, so F4's age guard has a reference older than every field it will check) |
| Container started | 2026-09-13T20:37:54Z |
| Container id | `b6fafc4fbcf8377557e0c98ce3b6fd7553eebf4738b645a8c63dd58c49fb2798`, name `wd_drivaer_fine_R1` |
| Image | `openfoam/openfoam9-paraview56:latest` (`eb76be2b2088`) |
| **Ranks** | **4** — their `decomposeParDict numberOfSubdomains 4` and their `run_solver_fluent.sh procs=4`, unmodified. **The lane's other 16 reserved ranks stay idle by Sanaa's explicit order.** |
| Command | `sh run_all_fluent.sh`, unmodified |
| `RUN_PIN.txt` | at the run root, carrying both freeze shas and every check below |

**The invocation is byte-identical to the graded coarse run's**, compared by
`docker inspect` on both:

```
/bin/bash -c "source /opt/openfoam9/etc/bashrc; sh run_all_fluent.sh; rc=$?; echo \"RC=$rc\" > /case/RUN_RC.txt"   user 1000:1000
```

**`rc` is captured INSIDE the container**, not around the launch — the `setsid`-parent trap
(a detached wrapper's parent exits 0 for every outcome).

---

## 3. STAGING — TWO PROOFS AND A PLANTED CONTROL

1. **Published manifest, paths rebased: 50 of 50 `OK`, 0 failures.** (The archive's 101-entry
   manifest verified whole at `101 OK` immediately before staging.)
2. **20 of 20 direct sha256 comparisons source-vs-staged identical** — all nine `system/`
   dictionaries, both `constant/` property files, all five `0_org/` fields, all three run
   scripts, and `mesh/mesh_fine.msh` (`372b8ae2…`, 820,744,718 B).
3. File counts and byte totals match exactly: **50 files, 1,774,124,576 B** on both sides.
4. **PLANTED CONTROL on the comparator itself** (rule 3): a one-byte-appended copy of
   `system/controlDict` was fed to the same sha256 comparison and **was reported as
   differing**. The instrument was shown able to see a difference **before** its 20/20
   "identical" was believed.

As staged and verified after copying: `numberOfSubdomains 4`, `method scotch`,
`endTime 10000`, `deltaT 1`.

---

## 4. WHAT MUST BE REPORTED, IN THIS ORDER, AT COMPLETION

**P1 FIRST, BEFORE F1 AND F2.** The registration predicts the force file will **NOT** be
byte-identical to their shipped
`sol_logs/fine/postProcessing/all/0/forceCoeffs.dat` (`17b702a2…`, 1,190,523 B), because our
4-way scotch partition is not their 40-way one. **If it IS byte-identical, the `nProcs : 40`
reading is wrong and §2 of the registration must be RETRACTED.** Report it either way.

**And plant the control before believing the `cmp`** — as the coarse rung did at offset
119,000. **A byte-identity claim from a comparator not shown able to see a difference is
worthless in either direction.**

Then, in order:

- **F1** window mean 200→10000 (**9,801 rows**) vs **0.256412**, band **1.0 %** — primary.
- **F2** endpoint at 10000 vs **0.257031**, band **2.0 %** — deliberately wider; a GATE FAIL
  here with a PASS on F1 reads as iterate noise, and that reading is registered in advance.
- **F3** cells == **4,048,483**.
- **F4** completion — all clauses, any failure → **`NOT A RESULT`**.
- **F5** our `log.solver` must print **`nProcs : 4`**, and the verdict section **must carry
  their `nProcs : 40`** or the verdict is incomplete.

**`Cd` is resolved BY NAME from the header** `# Time Cm Cd Cl Cl(f) Cl(r)` → index 2, column
3. No column index is assumed.

**COUNT `SIMPLE solution converged` IN OUR LOG.** Theirs has **zero in 10,000 iterations**.
**If ours converges and theirs did not, that is a finding in its own right and belongs beside
the verdict**, not in a footnote.

Then **renders** (mesh, `p`, `yPlus`) under `RENDERS/` with the face-count guard, the planted
colour control and the graded-tree census; then the **calibration row** against the
registered **9,100 core-minutes**.

---

## 5. HOW TO RESUME IF THIS SESSION DIES

- `docker ps --filter name=wd_drivaer_fine_R1` — the container is the run; it **does not die
  with the agent**. An agent watcher dying is not the run dying (L: *agent watchers die with
  the agent — reattach, do not restart*).
- `tail log.solver` in the run directory for the current iteration.
- **`RUN_RC.txt` appears only at the end**, written from inside the container.
- **DO NOT RESTART IT.** Reattach.

---

*Written by a cfd `lab-lane`, 2026-09-13, at launch. No verdict is claimed. Contains no
submission and no external communication. Nothing leaves the box.*

---

## 6. STOP RECORD — 2026-09-14, BY OWNER RULING. LABEL STAYS `PENDING`.

*Appended dated section. **Lines whose number changed above this section: 0.** No gate,
threshold, cap or label above is altered, added or relaxed by this section.*

### 6.1 THE AUTHORITY

Sanaa's ruling, relayed to this lane, verbatim:

> *"no lets stop them and stop drivaer as well that way we gain 32 ranks. But cfd first
> checks that all residuals are converged"*

and, withdrawing an intermediate Time-1000 amendment, relayed verbatim:

> *"we dont need that fine run to complete."*

### 6.2 HOW IT WAS STOPPED — A FORCED CLEAN CHECKPOINT, NOT A KILL

`system/controlDict:53` carries `runTimeModifiable yes`, so OpenFOAM's own mechanism was
used: `stopAt endTime` → `stopAt writeNow` at 2026-09-14T00:16Z. The solver wrote the
current time and exited through its normal path. **No signal was sent to the solver and no
field was written during a kill.** `log.solver` prints `End` then `Finalising parallel run`;
`RUN_RC.txt` reads `RC=0`. `docker stop wd_drivaer_fine_R1` then tore down an already-exited
solver; `docker ps -a` shows `Exited (0)`. **The fields are kept.**

| item | value | artifact |
|---|---|---|
| **stop iteration (last written time)** | **879** | `/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/fine_R1/processor{0..3}/879/` |
| last `Time =` line in the log | 879 | `log.solver` |
| `ExecutionTime` print count | 879 | `log.solver` |
| `nProcs` | 4 | `log.solver` (F5's our-side clause; theirs still reads 40) |
| `SIMPLE solution converged` count, ours | **0** in 879 iterations | `log.solver` |
| solver rc | 0 | `RUN_RC.txt` |
| checkpoint time directories retained | `800` and `879` | `processor0/` |

### 6.3 THE CHECKPOINT IS COMPLETE AND BANNER-CLOSED — WITH A PLANTED CONTROL

**80 of 80** files across `processor0..3/879/` end with the OpenFOAM closing banner
`// ****…**** //` as their last non-blank line. Fields present in each of the four
processor directories: `Q QMean U UMean UPrime2Mean k kMean nut nutMean nutPrime2Mean omega
omegaMean p pMean pPrime2Mean phi wallShearStress wallShearStressMean yPlus yPlusMean`,
plus `uniform/`.

**Standing rule 3 — the zero is planted.** A reader that cannot see a truncated file is not
evidence that no file is truncated. The same checker was handed a deliberately truncated
copy of `processor0/879/U` (first 2,000,000 bytes) alongside an intact `processor0/879/yPlus`
and returned **`NOT banner-closed: 1`**, naming the truncated file and clearing the intact
one. The `0` above is therefore a zero from a reader shown able to return a non-zero.

### 6.4 NO RESULT IS CLAIMED. NONE OF F1, F2 OR F4 CAN BE EVALUATED.

**F1** is defined on the window **200 → 10000**. **F2** is defined on the **endpoint 10000**.
**F4** requires **last time == `endTime` = 10000**. The run stopped at **879 of 10,000**, so
**none of the three has an input**. The label is:

> ### `PENDING` — stopped by owner ruling at iteration 879 of 10,000. Nothing failed.

Not `GATE FAIL`: no gate was evaluated, let alone missed. **No partial `Cd` in this section
is a fine result**, and no number below may be quoted without the window printed beside it.

### 6.5 WINDOW-MATCHED CORROBORATION AT AN INTERMEDIATE POINT — NOT A RESULT

Every figure below is a **window-matched** comparison of our series against **their own
shipped series over the identical iteration range**, both read from disk tonight, `Cd`
resolved **by header name** from `# Time Cm Cd Cl Cl(f) Cl(r)` in both files. `Cl(f)`/`Cl(r)`
is the **front/rear axle split**, not a pressure/viscous split.

- ours: `/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/fine_R1/postProcessing/all/0/forceCoeffs.dat` (880 rows, last `Time` 879)
- theirs: `/home/ubuntu/certonomous-runs/WOLFDYNAMICS_DRIVAER/fine_R1/sol_logs/fine/postProcessing/all/0/forceCoeffs.dat` (10,001 rows, last `Time` 10000)

| window | ours | theirs, SAME window | difference |
|---|---|---|---|
| mean over **200 → 879** | **0.271076** (n=680) | **0.270381** (n=680) | **0.257 %** |
| mean over **780 → 879** (our last 100, ending at the stop iteration) | **0.255369** (n=100) | **0.255520** (n=100) | **0.059 %** |
| mean over **200 → 621** | **0.277335** (n=422) | **0.277375** (n=422) | **0.0146 %** |
| **instantaneous at 879** | **0.256231** | **0.259471** | 1.249 % |

**BOTH HALVES OR NEITHER.** Matching their own series to **0.0146 %** over 200 → 621 is
evidence that **the setup reproduces their trajectory** — a real thing, and the thing this
staging was built to establish. It is **not** evidence that we have reproduced their
converged answer, because **their series is still descending** at this point: their running
mean 200 → 1000 is **0.269583**, 200 → 3000 is **0.259377**, and only 200 → 10000 is
**0.256412**, the published figure. Our 780 → 879 mean of **0.255369 is a transient-window
number** and **must never be set against their 0.256412**, which is a 200 → 10000 mean of a
converged run; those are different quantities and their closeness would be an artifact of
the mismatch, not an agreement.

**Experimental reference, citable but deliberately not compared against:** `Ref. [1] – EXP
TUM ASME 0.247` and `Ref. [1] – EXP TUM SA 0.243`, at
`docs/papers/benchmark_test_cases/guerrero_2022_drivaer_validation_wolfdynamics.txt:417` and
`:420`. It is cited here only to record that it *is* citable to a named artifact and line.
**No comparison against it is made**, because a transient-window mean is not a `Cd`.

### 6.6 RESUME, DO NOT REBUILD

`startFrom latestTime` picks up **879** directly. Restore `system/controlDict:25` to
`stopAt endTime;` (this lane changed exactly that one line; the pre-stop copy was kept in
this lane's scratch and the change is a one-token revert), relaunch the container on the same
image `openfoam/openfoam9-paraview56:latest`, and the run continues from the checkpoint. The
freeze pins above are unchanged. **Do not re-mesh and do not restart from 0.**

### 6.7 COST, AND THE CALIBRATION ROW THIS DOES NOT YET EARN

879 iterations on 4 ranks over 2026-09-13T20:37:42Z → 2026-09-14T00:16Z ≈ 3.65 wall h =
**876 core-minutes** (gross), against a registered **9,100 core-minutes** for the full
10,000. The estimate-versus-actual row of standing rule 12 is **not** filed here, because
**this process did not complete** — a partial run's spend calibrates nothing about a
prediction made for a whole one. It will be filed when the run is resumed and finishes.

*Appended by a cfd `lab-lane`, 2026-09-14. No verdict is claimed. No submission, nothing
sent, nothing leaves the box.*
