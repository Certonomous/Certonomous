# FINDING NOTE — `D6R2C` — THE FRESH-MESH PRODUCER WRITES ONE CGNS PATH FROM ALL FOUR MPI RANKS

**Team:** dafoam. **Date:** 2026-09-13. **Status:** a MEASUREMENT and a FIX. **It grades nothing and
re-opens nothing.** `FM10` remains `NOT A RESULT`, `FM11` and `FM12` remain `BLOCKED`, `O_mp` remains
`GATE FAIL`.

**THIS IS OUR DEFECT IN OUR SCRIPT. IT IS A FIX, NOT A FILING.** It is **not** an upstream DAFoam defect.
No upstream report is drafted here, none is referenced, and the four upstream defect classes remain
**`NOT FILED`**. **SUBMISSIONS PARKED (CLAUDE.md rule 7).**

---

## 1. THE DEFECT

`d6r2c_freshmesh.py`, md5 `1d15ce361673ca600d565280441b67e0`:

| line | statement |
|---|---|
| **213** | `rank0 = MPI.COMM_WORLD.rank == 0` |
| **268** | `grid.writeToCGNS(surface_out)` |
| **301** | `if rank0:` |

The rank flag is computed **55 lines before** the write and first used **33 lines after** it — **88 lines
apart in total**. The write at `:268` is therefore executed by **every MPI rank**, onto **one path**.
`cgnsutilities`/ADF is not a parallel writer and takes no file lock.

The producer is run at **4 ranks** by every fresh-mesh arm this family has:
`mpirun -np 4 python d6r2c_freshmesh.py --phase deform …`.

---

## 2. WHAT WAS MEASURED

### 2a. IN ARM `FM12`, ON THE REAL RUN

From `FM12`'s own arm log and disk:

| observation | value |
|---|---|
| `cgio_create_node:ADF  5: String is not an ASCII-HEX string.` | **3 lines** (log 6227–6229) |
| the rank that exited 1 | **rank 1** (`Process name: [[52239,1],1]`, log 6235) |
| `FM12/Zo/surfaceMesh_final.cgns` | **8,192 bytes** |
| `FM10`, `FM8`, `FM7`, `FM5` `surfaceMesh_final.cgns` | **114,688 bytes** each |

`FM10` ran the **byte-identical** command and its log carries **zero** `cgio` lines.

### 2b. THE UNGUARDED PATH, DRIVEN DELIBERATELY, 12 TIMES

In the pinned image `dafoam-idwarp-rot:v1`, 4 ranks, measurably idle cores, the same structure as `:268`:

| trials | rc | bytes | `cgio` lines |
|---|---|---|---|
| 1, 2, 4 | 1 | 69,632 | 3 |
| 3 | 1 | **12,288** | 4 |
| 5, 8, 9, 11, 12 | 1 | **114,688** | 3 (2 on trial 11) |
| 6, 7 | 1 | 102,400 | 3 |
| 10 | 1 | 94,208 | 3 |

**12 of 12 failed. Sizes ranged 12,288 → 114,688 bytes.**

### 2c. **THE PART THAT MATTERS MOST: A RACED WRITE CAN LOOK PERFECT**

**FIVE OF TWELVE produced the FULL, CORRECT 114,688 bytes.** One was captured and probed in the pinned
image: it **read successfully**, reported the **correct** 9 blocks and 1,215 points, and its coordinates
were **identical to the input to 0.0 exactly** — 3,645 values compared, **0 differing**.

**A size check, a readability check and a structure check all PASS that file.**

### 2d. AND THE CORRUPT FILE IS NOT GARBAGE

The 8,192-byte artifact's first 32 bytes are `c0 a8 a3 a9 "ADF Database Version A02011>"` — a **valid ADF
signature**, byte-identical in form to the good file's. **A header check would pass it.**

### 2e. A CORRUPT CGNS CANNOT BE CAUGHT IN-PROCESS

Driven against the preserved artifact: `readGrid` **raises no Python exception**. The ADF C library prints
`cgio_children_ids:ADF 11: Block/offset out of legal range.` and **terminates the process** with rc 1. A
`try/except BaseException` around it never runs.

---

## 3. THE IMPLICATION, AND IT IS NOT SOFTENED

> **EVERY FRESH-MESH ARM THIS FAMILY HAS EVER RUN WAS ROLLING THIS DICE. A SILENT WIN LOOKS EXACTLY LIKE
> A CORRECT RUN.**

Swept across every fresh-mesh arm log on disk — `FM3`, `FM4`, `FM5`, `FM6`, `FM7`, `FM8`, `FM9`, `FM10`,
and `DEC`/`DEC2`/`DEC3` — the `cgio` count is **0 in every one**. That is **not** evidence those writes
were correct. It is the observation that the failure is **silent when it does not crash**, and that **no
arm before `FM12` carried any instrument capable of telling a won race from a correct write.**

**No label is changed by this note.** What is recorded is that **their fresh-surface provenance was never
evidenced.**

**This is the SECOND independent `PRODUCER` defect in this one 623-line file.** The first was the double
design-variable application at `:423-425`, which made `FM10` `NOT A RESULT` and from which
`DAFOAM_CHARTER.md` §22.3 — the fifth cause class — was written. **It is now earned twice over, in the
same file.**

---

## 4. THE FIX, AND ITS HONEST LIMIT

Registered in `PREREGISTRATION_FM13_GUARDED_WRITE.md` and carried by **`d6r2c_fm13_deform.py`**.
**`d6r2c_freshmesh.py` IS NOT EDITED** (CLAUDE.md rule 6): the new producer imports it, asserts its md5,
and rebinds `Grid.writeToCGNS` — so "exactly one change" rests on a hash, not on a reader's diff.

**The change:** the CGNS write is guarded to **rank 0**, with a collective **barrier on either side**, and
a **four-limb assertion run independently on every rank** — exists; `size ≥ 29160` (**DERIVED** as
1215 × 3 × 8, the raw coordinate payload, ignoring all ADF structure); a **subprocess** `readGrid`
returning 9 blocks / 1215 points; and the coordinates on disk equal to **the array that rank already holds
in memory**. Limbs 3 and 4 are out of process because of §2e.

**Controls, all driven before the freeze:**

| control | result |
|---|---|
| **C1** the **real preserved 8,192-byte** `FM12` artifact (not synthetic) | **REFUSED** — `REFUSE_CGNS_SHORT_WRITE … bytes=8192 minimum=29160` |
| **C2** a `PLANT = 1.234e-03` moved into one coordinate | reader **sees** it (`coord_md5` moves); limb 4 **refuses** the mismatch and **accepts** the match |
| **C3** a correct 114,688-byte CGNS | **ACCEPTED**, 9 blocks, 1215 points |
| **C4** the unguarded path | **12/12 fail**, §2b |

### 4a. THE LIMIT, REGISTERED BEFORE IT COULD BE DISCOVERED

> **A SIZE-AND-READABILITY ASSERTION WOULD HAVE PASSED 5 OF 12 RACED WRITES, AND THE FULL FOUR-LIMB
> ASSERTION PASSES THE ONE FULL-SIZE OUTPUT THAT WAS CAPTURED (§2c).**
>
> **The assertion is the TRUNCATION net — which is what `FM12` actually suffered. THE INSTRUMENT THAT
> REMOVES THE RACE IS THE RANK-0 GUARD ITSELF.**

### 4b. THE CAVEAT ON C4

C4 **barrier-synchronises** the ranks immediately before the write, which **maximises** collision. The
real run's ranks arrive at `:268` at slightly different times. C4 therefore demonstrates that concurrent
writes to one CGNS path corrupt; it **does not measure the real run's collision rate**.

**THE INTERMITTENCY OF THE REAL RUN IS INFERRED FROM ONE SUCCESS (`FM10`) AND ONE FAILURE (`FM12`).**
**IT IS NOT MEASURED OVER REPEATS.** No rate or probability may be quoted from this note.

---

## 5. THE EVIDENCE IS PRESERVED AND IS NOT TO BE DELETED

`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance/FM12/Zo/surfaceMesh_final.cgns`
— **8,192 bytes.** It is `FM13`'s known-bad control. `FM12`'s root is on `d6r2c_fm13_run_arm.sh`'s
`G-ROOT.2` forbidden list, asserted in its selftest, so `FM13` **reads** it and can never write it.

**SUBMISSIONS PARKED.**
