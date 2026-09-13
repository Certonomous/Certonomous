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
