# Curriculum D6R2C — PRE-REGISTRATION for arm `FM13`: THE COMPARISON AT MATCHED LIFT, WITH THE COLLECTIVE CGNS WRITE GUARDED

**STATUS: FROZEN AT THE COMMIT THAT CARRIES THIS FILE. Gates, thresholds, caps and labels are closed
from that sha; changes land only as dated addenda (CLAUDE.md rule 2).**

**`FM12` IS `BLOCKED` AND STAYS `BLOCKED`. ITS FROZEN FILES ARE NOT EDITED (rule 6)** — its outcome is
recorded in `PREREGISTRATION_FM12_MATCHED_LIFT_PROVENANCE.md` ADDENDUM 1, appended, with the first 25,867
bytes proved byte-identical. `FM13` is a NEW registration that inherits `FM12`'s design — which was right,
and whose `Zb` sub-arm ran clean — and repairs the ONE thing that stopped it.

**SUBMISSIONS PARKED (rule 7).** Nothing in this arm is sent, filed, uploaded or registered anywhere.
**The defect this arm repairs is OUR defect in OUR script. It is a FIX, not a filing.** It is **not** an
upstream DAFoam defect, no upstream report is drafted or referenced, and the four upstream defect classes
remain **`NOT FILED`**.

---

## 1. WHY THIS ARM EXISTS

`FM12` was frozen at `3bd92d92b`, launched, and graded **`BLOCKED`** after **269 s wall / 17.933
core-min**, at the `Zo` sub-arm's `--phase deform`. **Cause class `PRODUCER`**
(`DAFOAM_CHARTER.md` §22.3, the fifth class), assigned by `dafoam-supervisor` from a personal crash
triage and verified independently in this lane against the file and the artifacts.

### 1a. THE DEFECT: ONE CGNS PATH, FOUR MPI RANKS

`d6r2c_freshmesh.py` — the **inherited frozen** producer, md5 `1d15ce361673ca600d565280441b67e0` —
computes

```
213:    rank0 = MPI.COMM_WORLD.rank == 0
```

and first **uses** it at

```
301:    if rank0:
```

**88 lines after**

```
268:    grid.writeToCGNS(surface_out)
```

`cgnsutilities`/ADF is not a parallel writer and takes no file lock. All four ranks therefore open,
truncate and write **one path** concurrently. Measured consequence in `FM12`, from its own arm log and
disk:

| observation | value |
|---|---|
| `cgio_create_node:ADF  5: String is not an ASCII-HEX string.` | **3 lines** (log 6227–6229) |
| the rank that exited 1 | **rank 1** (`Process name: [[52239,1],1]`, log 6235) |
| `FM12/Zo/surfaceMesh_final.cgns` | **8,192 bytes** |
| `FM10`, `FM8`, `FM7`, `FM5` `surfaceMesh_final.cgns` | **114,688 bytes** each |

**`FM10` ran the BYTE-IDENTICAL `mpirun -np 4 … --phase deform` command and its log carries ZERO `cgio`
lines: it won the race.**

### 1b. THE IMPLICATION, AND IT IS STATED IN EVERY RECORD THIS ARM WRITES

**EVERY FRESH-MESH ARM THIS FAMILY HAS EVER RUN WAS ROLLING THIS DICE. A SILENT WIN LOOKS EXACTLY LIKE A
CORRECT RUN.**

Swept across every fresh-mesh arm log on disk — `FM3`, `FM4`, `FM5`, `FM6`, `FM7`, `FM8`, `FM9`, `FM10`
and the `DEC`/`DEC2`/`DEC3` logs — the `cgio` count is **0 in every one**. That is **not** evidence the
writes were correct. It is the observation that **the failure is silent when it does not crash**, and
that **no arm before `FM12` carried any instrument capable of telling a won race from a correct write.**
No prior label is changed by this registration: `FM10` stays `NOT A RESULT`, `FM11` and `FM12` stay
`BLOCKED`, `O_mp` stays `GATE FAIL`.

**This is the SECOND independent `PRODUCER` defect in this one 623-line file.** The first was the double
design-variable application at `d6r2c_freshmesh.py:423-425`, which made `FM10` `NOT A RESULT` and which
`DAFOAM_CHARTER.md` §22.3 was written from. **The fifth cause class is earned twice over, in the same
file.**

### 1c. WHAT `FM12` ESTABLISHED, AND WHAT IT DID NOT

`Zb` ran to `rc = 0` and is carried into this arm **unchanged**. Its numbers, from
`FM12/Zb/d6r2c_fm12.jsonl`:

| quantity | measured | comparator | margin |
|---|---|---|---|
| `J_base_fresh` | **0.030642507915** | `J0` **0.030641631439** | **8.765e-07** = **0.0029 %**, **349.6×** inside `FM_BAND_ABS` |
| max \|`CL` − target\| | **5.643e-07** | `TRIM_TOL` **1.0e-3** | closed in **2** trim evaluations |
| `M0b.5` read-back | **pass** | | **0.0 m exactly**, all three conditions |
| as-run `checkMesh` max non-orth | **66.965** | declared **70.0** | **INSIDE**, unlike the optimisation mesh at 71.24 and `FM10` at 79.21 |
| `R1` | **40209/40209** identical, md5 identical, gzip `MTIME` = 0 both | | **47.743 days** |

> **`Zb` shows the BASELINE reproduces on a freshly generated mesh to 0.0029 %. It says NOTHING about
> whether the optimum reproduces. The 24.7 % remains untested in both directions, and no reading of `Zb`
> supports it.**

That sentence is the reason `FM13` exists: the arm's actual question is carried entirely by `Zo`, and
`Zo` did not run.

---

## 2. THE ONE REGISTERED CHANGE

> **THE CGNS WRITE IS GUARDED TO RANK 0, WITH A COLLECTIVE BARRIER ON EITHER SIDE AND A POST-WRITE
> ASSERTION EXECUTED INDEPENDENTLY ON EVERY RANK.**

It is carried by a **new** producer, `d6r2c_fm13_deform.py`. **`d6r2c_freshmesh.py` IS NOT EDITED**
(rule 6) and is staged byte-for-byte at its pinned md5, which `d6r2c_fm13_deform.py` asserts at startup
before it does anything else.

The change is applied by **rebinding `Grid.writeToCGNS`**, not by copying `phase_deform`'s 90-line body.
A copy would be a second producer free to drift from the first — which is how this family acquired its
first `PRODUCER` defect. A rebind cannot drift, and the provability of "exactly one change" rests on the
frozen module's md5 rather than on a reader's diff.

### 2a. THE ASSERTION'S FOUR LIMBS

| limb | what it reads | refusal |
|---|---|---|
| 1 | the file exists | `REFUSE_CGNS_ABSENT` |
| 2 | `size ≥ MIN_CGNS_BYTES` | `REFUSE_CGNS_SHORT_WRITE` |
| 3 | a **subprocess** `readGrid` returns rc 0 and reports 9 blocks / 1215 points | `REFUSE_CGNS_UNREADABLE`, `REFUSE_CGNS_STRUCTURE` |
| 4 | the coordinates **on disk** equal the array **this rank holds in memory** | `REFUSE_CGNS_CONTENT` |

`MIN_CGNS_BYTES = 1215 × 3 × 8 = 29160`, **DERIVED** as the raw coordinate payload of the registered
block-structured point count and **ignoring every byte of ADF structure**, so it is a true lower bound.
It is **not** a number chosen to sit between the observed good and bad sizes. The registered point count
9 blocks / 1215 points is itself **MEASURED** in the pinned image on `surfaceMesh_base.cgns`, not recalled.

**LIMB 3 RUNS IN A SUBPROCESS FOR A MEASURED REASON.** Driven against the preserved 8,192-byte artifact
in the pinned image: `readGrid` **does not raise a Python exception**. The ADF C library prints
`cgio_children_ids:ADF 11: Block/offset out of legal range.` and **terminates the process** with rc 1; a
`try/except BaseException` around it never runs. Out of process, a library abort arrives as a return code
this producer converts into its own registered refusal instead of an opaque ADF line.

**AND THE CORRUPT FILE IS NOT GARBAGE.** Its first 32 bytes are
`c0 a8 a3 a9 "ADF Database Version A02011>"` — a **valid ADF signature**, byte-identical in form to the
good file's. **A header check would pass it.** That is precisely why this failure is silent when it does
not crash, and it is why no header limb is registered.

---

## 3. THE CONTROLS — AND THE ONE THAT FALSIFIES A COMFORTABLE READING

All four were driven **before this freeze**, in the pinned image
`dafoam-idwarp-rot:v1` (`sha256:2927768a…`), on measurably idle cores.

### C1 — THE KNOWN-BAD CONTROL, AND IT IS NOT SYNTHETIC

The **preserved 8,192-byte corrupt CGNS from `FM12`**, at
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance/FM12/Zo/surfaceMesh_final.cgns`.
**It is the evidence and it is not to be deleted.** `FM12`'s root is on this launcher's `G-ROOT.2`
forbidden list, asserted in its selftest, so this arm **reads** it and can never write it.

**RESULT: `REFUSE_CGNS_SHORT_WRITE … bytes=8192 minimum=29160`. The guard refused it.** A guard that has
never said no is not a guard.

### C2 — A PLANTED CONTENT CONTROL (CLAUDE.md rule 3)

The family's own `PLANT = 1.234e-03` is added to one coordinate of a correct file, which is then written
and read back **from disk**.

**RESULT:** the reader **sees** the plant (`coord_md5` moved `0161b00d…` → `a9b3cfb4…`); limb 4
**refuses** the planted file against the clean expectation; and limb 4 **accepts** the same file against
its own md5 — so it refuses a **mismatch**, not merely any file it is shown.

### C3 — THE POSITIVE CONTROL

`surfaceMesh_base.cgns`, 114,688 bytes. **RESULT: ACCEPTED**, blocks 9, points 1215,
`coord_md5 0161b00d2b24a9895ac101c6873ed1d1`. A guard that refuses everything is not a guard either.

### C4 — THE UNGUARDED PATH, DRIVEN, AND IT FIRES ON DEMAND

The unguarded structure of `d6r2c_freshmesh.py:268` — all four ranks calling `writeToCGNS` on one path —
was driven **12 times at 4 ranks**.

| trial | rc | bytes | `cgio` lines |
|---|---|---|---|
| 1, 2, 4 | 1 | 69,632 | 3 |
| 3 | 1 | **12,288** | 4 |
| 5, 8, 9, 11, 12 | 1 | **114,688** | 3 (2 on trial 11) |
| 6, 7 | 1 | 102,400 | 3 |
| 10 | 1 | 94,208 | 3 |

**12 of 12 failed.** The output size ranged **12,288 → 114,688 bytes**.

#### C4a — **THE FINDING THAT LIMITS THIS ARM'S OWN INSTRUMENT, REGISTERED BEFORE IT COULD BE DISCOVERED**

**FIVE OF TWELVE RACED WRITES PRODUCED THE FULL, CORRECT 114,688 BYTES.** One was captured and probed: it
**read successfully**, reported the **correct** 9 blocks and 1,215 points, and its coordinates were
**identical to the input to 0.0 exactly** (3,645 values compared, 0 differing). Handed to this arm's own
assertion, **the guard ACCEPTED it**, `coord_md5` equal to the clean file's.

> **SO A SIZE-AND-READABILITY ASSERTION WOULD HAVE PASSED 5 OF 12 RACED WRITES, AND THIS ARM'S FULL
> FOUR-LIMB ASSERTION PASSES THE ONE THAT WAS CAPTURED.**
>
> **The assertion is registered as the instrument that catches TRUNCATION — which is what `FM12` actually
> suffered — AND NOT as the instrument that detects the race. THE INSTRUMENT THAT REMOVES THE RACE IS THE
> RANK-0 GUARD ITSELF.** The assertion is a net under the guard, and a net with a measured hole.

### C4b — THE CAVEAT ON C4, KEPT IN THE FROZEN TEXT

**C4 deliberately barrier-synchronises the four ranks immediately before the write**, which maximises
collision probability. The real run's ranks arrive at `:268` at slightly different times, having just
finished `prob.run_model()`. **C4 therefore demonstrates that concurrent writes to one CGNS path corrupt;
it does NOT measure the real run's collision rate.**

**THE INTERMITTENCY OF THE REAL RUN IS INFERRED FROM ONE SUCCESS (`FM10`) AND ONE FAILURE (`FM12`).**
**IT IS NOT MEASURED OVER REPEATS.** No rate, probability or expected-frequency claim is made or may be
quoted from this registration.

---

## 4. THE STATES — `FM12`'s TABLE, UNCHANGED

| sub-arm | state | mesh extruded around | `shape` | `twist` | incidence | trimmed | `G-WALL` |
|---|---|---|---|---|---|---|---|
| `Zb` | `Zb` | `surfaceMesh_base.cgns` | **0** | **0** | re-trimmed from `x0` | yes | **GATED** |
| `Zo` | `Zo` | the FFD-updated surface | **0** | **0** | re-trimmed from `x0` | yes | **GATED** |
| `Zo` | `Ez` | (the same mesh) | **0** | **0** | `a*_opt`, as flown | no | **GATED** |
| `Zo` | `Do` | (the same mesh) | `s*` | `t*` | `a*_opt` | no | **REPORTED** |

**`Zb` IS CARRIED FORWARD UNCHANGED — it worked, on instruments that are reused byte for byte — and `Zo`
is re-run.** The phase order, emitted by `d6r2c_fm13_run_arm.sh --emit-cmd`:

```
Zb:  freshmesh --phase mesh                    ->  fm12_states --sub-arm Zb --datum-file ...
Zo:  fm13_deform --phase deform  ->  freshmesh --phase mesh  ->  fm12_states --sub-arm Zo --datum-file ...
```

`d6r2c_freshmesh.py --phase deform` — the unguarded collective write — **is not emitted by this arm**,
and the launcher's selftest asserts **both** that the guarded producer appears on the deform line **and**
that the unguarded one does not.

**GATES ARE `FM12`'s, UNCHANGED**, graded by `d6r2c_fm13_grade.py`, which differs from
`d6r2c_fm12_grade.py` **only** in `ARM_IDS` and in `ZB_TRIM_WALL_S` (§7). `G1`, `G2`, `G-WALL`, `M0b`,
`M0o`, `M0b.5`, `M1`, `D1`, `D2`, `Q1`, `H4` and `R1` keep their registered thresholds, and `FM_BAND_ABS`,
`RATIO_BAND` and `TRIM_TOL = 1.0e-3` are unchanged. The planted-zero control of `FM12` §3 is unchanged and
still refuses `REFUSE_PLANT_UNSEEN`.

---

## 5. THE ARM-ID COLLISION, REGISTERED RATHER THAN DISCOVERED

`PREREGISTRATION_FM11_MATCHED_LIFT.md:349` registers **`FM13` as one of `FM11`'s re-run ids**, and
`d6r2c_fm11_run_arm.sh:99` and `:671` will launch it under `FM11`'s cap. **`FM11` is graded `BLOCKED`.**
**This document ALSO registers `FM13`**, on its supervisor's assignment.

The two **cannot** be told apart by arm id. They are told apart by:

- **run root** — `CURRICULUM-D6R2C-FM13-a2-wing-matched-lift-guarded-write` here versus
  `CURRICULUM-D6R2C-FM11-a2-wing-matched-lift` there; and
- **the ledger's `ITEM=` line** — `ITEM=D6R2C-FM13` here.

Both separations are **asserted in this launcher's selftest**, and `d6r2c_fm13_grade.py`'s selftest
asserts the collision explicitly rather than inheriting `FM12`'s assertion that `FM13` is foreign.
`FM11`'s frozen files are **not edited** to resolve it (rule 6), so **the residual hazard is that a human
reads "FM13" without its root.** It is named here so that it is read rather than discovered.

---

## 6. THE INSTRUMENTS, AT THEIR FROZEN md5

| file | md5 | role |
|---|---|---|
| `d6r2c_fm13_deform.py` | `bcb0685b56453bf96eda98b21d233556` | **NEW.** The guarded deform producer. The one registered change. |
| `d6r2c_fm13_grade.py` | `04a2735424527e2b2650a3ce3e13e4bd` | **NEW.** `FM12`'s grader with `ARM_IDS` and `ZB_TRIM_WALL_S` changed, and nothing else. |
| `d6r2c_fm13_run_arm.sh` | `38b9a71e266a98dd8d4909b6076ee4ed` | **NEW.** The launcher. |
| `d6r2c_freshmesh.py` | `1d15ce361673ca600d565280441b67e0` | **INHERITED, BYTE-IDENTICAL, NOT EDITED.** Wrapped, never modified. |
| `d6r2c_fm12_states.py` | `612fb2e6d60320e1f225a2e7555eb1d1` | **INHERITED, BYTE-IDENTICAL.** `Zb` ran clean on it. |
| `d6r2c_fm12_stage.py` | `d0d969a925da7e7b04ff35f8f8bb2d75` | **INHERITED, BYTE-IDENTICAL.** |
| `d6r2c_fm9_stage.py` | `ea6d180fda38a3980bbb275b86d192c1` | **INHERITED, BYTE-IDENTICAL.** `REFUSE_FRESH_IS_BASE` stays exactly where it is. |
| `d6r2c_decomp.py` | `42ec0dd582584812a69129a474b2783e` | **INHERITED, BYTE-IDENTICAL.** |
| `d6r2c_dec5_decomp.py` | `fb19791784ebb73747c2f6c466a0d174` | **INHERITED, BYTE-IDENTICAL.** |
| `d6r2c_opt_runScript.py` | `2f2ae43a627146cf8e0f065b035ada4b` | **INHERITED, BYTE-IDENTICAL.** |

`genWingMesh.py` is **not** a row here: it does not live in the source directory, it is staged from the
run tree, and its md5 `dab5e959187ab2e2bfb4e2c0ded0feb6` is pinned as `MD5_GENWINGMESH` inside
`d6r2c_fm12_stage.py` and asserted by `G-FREEZE` before every launch. Naming it here as though clause
(a) could hash it in `$SRC` would be a table that is true as written about a file that is not there,
which is L-579 exactly.

---

## 7. THE COST, RE-ANCHORED ON MEASUREMENT

| term | value | anchor |
|---|---|---|
| per objective evaluation | 5.447 core-min | DEC7 `d6r2c_dec5.jsonl` STATE `O`, 81.7 s × 4 ÷ 60 |
| per gradient evaluation | 11.863 core-min | `O_mp` `d6r2c_evals.jsonl`, median of 26 `G` records |
| **gradient evaluations in this arm** | **0** | **registered so the zero is BY DESIGN and VISIBLE. `FM13` runs no adjoint.** |
| **`Zb` trim** | **61.113 s** | **RE-ANCHORED, MEASURED — see below** |
| `Zo` trim | 2400.3 s | DEC7 STATE `S` — **UNTESTED** |
| mesh + deform + stage | 88.2 s × 2 | `FM10` arm wall 160 s − its solve 71.847 s |
| model load per process | 14.1 s × 2 | DEC7 FOOTER 5918.862 − Σ states |
| `Ez` + `Do` | 81.7 s × 2 | one objective evaluation each |

### 7a. WHAT WAS RE-ANCHORED, AND WHAT IT WAS RE-ANCHORED FROM

**`ZB_TRIM_WALL_S`: 574.5 s → 61.113 s.** `FM12` registered **676.8 s** for the whole `Zb` sub-arm
(574.5 trim + 88.2 mesh/deform/stage + 14.1 model load) and **it ran in 163.413 s** — its own `FOOTER`
— **4.14× faster**. The cause is measured, not guessed: **the trim closed in 2 evaluations where DEC7
`STATE B` needed 6**, because `Zb` starts from `x0` on a mesh generated at zero shape. Subtracting the
same 88.2 and 14.1 terms the formula already carries leaves **61.113 s** for the trim itself.
**The 574.5 s DEC7 anchor is now KNOWN TOO LARGE for this state, and is named here rather than quietly
dropped.**

**`ZO_TRIM_WALL_S` IS UNTESTED AND IS LABELLED SO.** `FM12` never reached a `Zo` solve. The 2400.3 s
term is neither confirmed nor falsified and is carried forward **unchanged**, as are every other `Zo`
term. Nothing in this registration claims otherwise.

### 7b. THE REGISTERED FIGURES

`PREDICTED_WALL_S = 2829.413 s` at 4 ranks ⇒ **`PREDICTION = 188.628 core-min`**, cap at ×3.00 =
**`565.884 core-min`** (printed by `d6r2c_fm13_grade.py --print-cap FM13`, which is the launcher's one
source). That is **15.4 % below `FM12`'s 222.853**, and the whole reduction is the re-anchored `Zb` term.

**Dollars are DERIVED at the owner-stated $0.0513/core-h and are NOT MEASURED** — the box cannot read its
own billing (`COMPUTE_BUDGET_CHARTER.md` §5): prediction **$0.1613**, cap **$0.4838**.

### 7c. `FM12`'s ESTIMATE-VERSUS-ACTUAL CALIBRATION (CLAUDE.md rule 12)

| | core-min | $ (DERIVED) |
|---|---|---|
| `FM12` predicted | 222.853 | 0.1905 |
| `FM12` cap | 668.559 | 0.5716 |
| **`FM12` actual** | **17.933** | **0.0153** |
| ratio actual/predicted | **0.080470** | |

**Cap not crossed. ATTRIBUTION: the `Zo` refusal, not misprediction** — `Zo` carried 2400.3 s of the
3342.8 s prediction and never reached a solve. **Named separately and NOT folded into that ratio:** `Zb`'s
**4.14×** speedup, which is genuine calibration information and is what §7a re-anchors.

---

## 8. THE PRE-FREEZE CHECK — `DAFOAM_CHARTER.md` §22.4's THREE CLAUSES

`d6r2c_fm13_prefreeze.sh`.

**(a)** every instrument named in §6 exists at its stated md5, read out of §6's own rows — the script
carries no list of its own — plus the assertion that the launcher's `$PINNED_PY` and §6's table are one
list.

**(b) — DRIVEN AGAINST THE REAL ANCHORS, AND THE SYNTHETIC CASE REPORTED SEPARATELY.** `FM12` did this
correctly and the method is carried forward without weakening. **(b1)** runs the emitted grading command
**verbatim, with not one flag altered**, so it reads the real `d6r2c_evals.jsonl` and the real `FM10`
record through the launcher's own defaults, and asserts the printed `R_def` is `0.752677271`. **(b2)**
runs the synthetic-anchor form as an **additional** case, reported separately and never as the only one —
`FM11`'s clause (b) drove the command line and not the data the command line reads, which is L-595
surviving its own lesson. **(b3)** lifts the **guarded producer's** argument vector out of the emitted
container block and drives it through that producer's own argparse.

**(c)** every channel a gate reads has a writer that ran: zero live read sites for `primal_residual.json`
in the `FM13` instruments, the sweep itself driven to its failing side; `H4`'s log limb read against a
real arm log and refused against an absent one.

**And beyond the charter:** the four controls of §3 driven in the pinned image, C1 against the **real
preserved corrupt artifact**; `M0b`/`M0o` driven to both sides against the real artifacts; `R1` at zero
and at a planted non-zero; `G-WALL` driven to its failing side; every cost constant re-derived in the same
invocation; and all instrument selftests.

**HONEST GAP, NAMED BEFORE IT IS DISCOVERED.** The guarded write has **not** executed against the real
`Zo` deform path — that is the compute this registration authorises. What **has** been exercised is the
assertion against the real corrupt artifact, against a real correct artifact, against a planted one, and
the unguarded path 12 times. What remains unexercised is the rank-0 guard itself running under
`prob.run_model()` at 4 ranks with `mpi4py` live, and every `Zo` gate downstream of it.

---

## 9. THE LAUNCH

```
/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_fm13_run_arm.sh FM13 \
  dafoam-idwarp-rot@sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
```

- run root: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM13-a2-wing-matched-lift-guarded-write`
- **`G-ROOT.2` forbids writing `FM12`'s root** — which holds the preserved corrupt CGNS, this arm's
  known-bad control — alongside `FM11`, the parent, `FM9`/`FM10`, `AFTER`, `DEC4`, `FM6`, the A2 surface
  root and the tutorial directory. All are READ, never written.
- 4 ranks; the cpuset is **chosen at launch** by `free_cpuset` from the union of docker occupancy and a
  1 %-busy sample over 2 s, and `G-CPUSET` refuses to start on any intersection. **Nothing running is ever
  stopped.**
- registered arm ids: **`FM13`, `FM13R2`, `FM13R3`** — re-run ids carrying the identical registered cap.
  `FM12`'s own ids get no cap here and this launcher refuses them. See §5 for the `FM11` collision.
- **NOTHING IS STOPPED BY THE CAP** (Sanaa's directive #17, 2026-09-12). A crossing is REPORTED, the row
  is graded `NOT A RESULT`, and the cap is never raised.

---

## 10. WHAT THIS ARM DOES NOT CLAIM

- **No collision rate, probability or frequency** for the real run. §3 C4b governs: one success, one
  failure, not measured over repeats.
- **The four-limb assertion does not detect a raced write in general.** §3 C4a governs, and it is
  measured: a raced write can be full-size, readable, structurally correct and coordinate-identical.
- **No prior arm is re-graded.** `FM10` `NOT A RESULT`; `FM11` `BLOCKED`; `FM12` `BLOCKED`; `O_mp`
  `GATE FAIL`.
- **No GCI is computed and none may be quoted** — a Roache triple would need three grid levels this arm
  does not run (CLAUDE.md rule 5).
- **The cross-mesh ratio `J_fresh / Jf`** mixes a fresh-mesh numerator with a deformed-mesh denominator
  and must not be quoted.
- **`Zb` says nothing about the optimum.** The 24.7 % remains untested in both directions.
- **Nothing here is an upstream defect report.** The defect is ours; the fix is ours. **SUBMISSIONS
  PARKED (rule 7)**, and the four upstream defect classes remain **`NOT FILED`**.
