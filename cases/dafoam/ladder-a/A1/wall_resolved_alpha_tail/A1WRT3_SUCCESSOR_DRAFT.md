# A1WRT3 — THE WALL-RESOLVED α-TAIL, ON `symmetry` — **SUCCESSOR PRE-REGISTRATION, DRAFT**

> ## ⚠ THIS IS A **DRAFT**. IT IS NOT FROZEN, IT HAS NO EVIDENTIARY FORCE, AND NOTHING IS ENQUEUED.
>
> **The freeze commit is the `dafoam-supervisor`'s and no lane takes it.** The freeze is this
> document's entire evidentiary content (`CLAUDE.md` rule 2) and a lane cannot manufacture it by
> writing the word. **No queue row is written by this draft. `LAUNCH_ENABLED` stays `0`.**
>
> **Run root `/home/ubuntu/certonomous-runs/A1WRT3` — ABSENT, CHECKED BY EXECUTION at
> 2026-09-06T01:38:13Z in the drafting invocation** (`ls -d` → `No such file or directory`).
> That is `CLAUDE.md` rule 2 limb 1 / `VERIFICATION_CHARTER.md` §2b's condition, **named as the
> directory that does not exist and checked, not asserted**, which is what makes every pre-freeze
> edit to this document lawful.
>
> **Drafted against HEAD `08ed8d9715dced0e8465d4b0ee7caac8590cf767`.**
>
> **SUBMISSIONS PARKED.** Nothing in this item is sent, emailed, filed, uploaded, registered,
> posted or commented outside this box, by any agent, ever (`CLAUDE.md` rule 7).

---

## 0. WHY THIS IS A SUCCESSOR AND NOT A REPAIR — THE LAW, NOT A PREFERENCE

`A1WRT2` (`A1WRT2_SUCCESSOR_DRAFT.md`, frozen `4e39c370`, §13 enqueue at `6d52f0af`, queue row
`a4f71837`) **has burned compute.** Its `SEAM` arm ran 2026-09-05T22:20:44Z → 22:20:48Z, `rc=1`,
**0.067 core-min**, and its run root `/home/ubuntu/certonomous-runs/A1WRT2/` exists
`[MEASURED, A1WRT2_SEAM_RESULTS.md §1 and §6, from `SEAM/out/rc` and `ledger.txt`]`.

**`CLAUDE.md` rule 2 closed `A1WRT2`'s gates at that moment.** After first compute, changes land
only as dated addenda **that cannot alter a gate, threshold, cap or label**. The `A1WRT2` defect
is a *missing gate* and a *missing environment channel* — repairing either is exactly what an
addendum may not do.

> **A successor is the only lawful route. This document is it.**

**`A1WRT2` keeps everything it earned and this document amends nothing in it.** Its `SEAM` verdict
stands as `NOT A RESULT`; its `P-SEAMTIME` stands as `UNRESOLVED`; its §5 family sweep stands as a
measured finding. **No `A1WRT2` gate, threshold, cap, label or reading is altered here.**

---

## 1. THE DEFECT THIS ITEM EXISTS TO REPAIR — `A1WRT2-DEF-ENVSEAM`

**One deletion, four consequences, two of them still open at the moment this draft opens.**

`A1WRT` ran a **two-layer container command**. The outer layer (`a1wrt_run_unit.sh:664-678`)
sourced `loadDAFoam.sh`, checked the `libidwarp` md5 in-process, and invoked
**`timeout -k … bash /mnt/cmd.sh`**. The inner layer, `/home/ubuntu/certonomous-runs/A1WRT/cmd.sh`
(102 lines, **58 non-comment non-blank lines**, counted in this drafting invocation), did the
preflight, the translation and the rc discipline.

**`A1WRT2` transcribed the innermost command and deleted `cmd.sh`** — `a1wrt2_run_arm.sh:851-853`:

    timeout 900 docker run --rm --user 0:0 --cpuset-cpus="0" --memory=8g \
      -e OMP_NUM_THREADS=1 -v "$SEAM_CASE:/mnt" -v "$RUN_ROOT:/run_root" \
      "$IMG" /bin/bash -lc "source $DAFOAM_LOADER && cd /mnt && python /run_root/runScript.py -task sweep"

**`-e OMP_NUM_THREADS=1` and nothing else**, against a producer that reads **four** fatal names
from `os.environ` at **module scope** `[MEASURED by AST, A1WRT2_SEAM_RESULTS.md §3.2, and
re-read directly in this invocation from `/home/ubuntu/certonomous-runs/A1WRT2/runScript.py`]`:

| variable | line | scope | class |
|---|---|---|---|
| `AOA_ALPHA0` | `:51` | **module** | **REQUIRED**, fatal — this is where it died |
| `AOA_ALPHAS` | `:285` | module | **REQUIRED**, fatal |
| `AOA_MODE` | `:286` | module | **REQUIRED**, fatal |
| `AOA_POINTS_JSON` | `:287` | module | **REQUIRED**, fatal |
| `A1WR_PRIMAL_TOL` | `:60` | module | optional, default `"1.0e-8"` |
| `AOA_LEDGER` | `:288` | module | optional, default `/mnt/out/LEDGER.tsv` |

### 1.1 ⚠ THE VARIABLE NAMES DO NOT MATCH ACROSS THE SEAM. **COPYING THE `-e` BLOCK WOULD ALSO HAVE FAILED.**

`a1wrt_run_unit.sh:667-668` passes **`A1WR_MODE`, `A1WR_ALPHAS`, `A1WR_TOL`, `A1WR_TMO`**.
The producer reads **`AOA_MODE`, `AOA_ALPHAS`, `AOA_POINTS_JSON`, `AOA_ALPHA0`**.
**Not one name is shared.** `cmd.sh:57-64` **is** the mapping:

    AOA_MODE="$MODE_FOR_LEDGER" \
    AOA_ALPHAS="$A1WR_ALPHAS" \
    AOA_POINTS_JSON=/mnt/out/points.json \
    AOA_ALPHA0="$FIRST_ALPHA" \
    AOA_LEDGER=/mnt/out/LEDGER.tsv \
    A1WR_PRIMAL_TOL="$A1WR_TOL" \
    timeout -k 60 "$A1WR_TMO" \
      python /mnt/runScript.py -task sweep > /mnt/out/sweep.log 2>&1

> **The deleted layer IS the translation.** Two of its four outputs — `AOA_POINTS_JSON` and
> `AOA_ALPHA0` — **have no launcher-side counterpart at all**: one is a literal path, the other is
> the *first element of a list* the launcher passes whole. A launcher that forwarded every `-e` it
> had would still have crashed at `runScript.py:51`.
>
> **THEREFORE: this item RESTORES THE TRANSLATION, NOT THE FLAGS.** §2 is that restoration, and
> §4's `G-ENVSEAM` is the gate that refuses if it is ever incomplete again.

### 1.2 ⚠ THE 2026-09-05 REPAIR WAS SYMPTOM-DRIVEN, AND THAT IS THE LESSON THIS ITEM CARRIES

`A1WRT2`'s loader repair (`a1wrt2_run_arm.sh:828-842`) restored `source loadDAFoam.sh`
**because driving `measure_image_pins` tripped over `python: command not found`.** It fixed what
it tripped over. **It never asked what else the same deletion had taken** — and three more things
had gone with it, one of them a registered configuration assertion.

> **A repair aimed at the symptom it tripped over will not find the siblings of its own defect.**
>
> **THE STRUCTURAL ANSWER, AND IT IS THIS DOCUMENT'S CENTRAL METHOD:** §2 enumerates
> **every clause of the deleted file, by line, and accounts for every one** — RESTORED, REPLACED,
> or **DELIBERATELY DROPPED WITH A REASON**. **An unaccounted clause is the same defect a third
> time**, so the accounting is written as a closed set with a stated denominator, not as a list of
> the things this lane happened to notice.

---

## 2. THE CLAUSE-BY-CLAUSE `cmd.sh` ACCOUNTING — **THE CLOSED SET**

**Method, stated so it is auditable.** The subject is `/home/ubuntu/certonomous-runs/A1WRT/cmd.sh`
as it stands on disk. **Denominator: 102 lines, of which 58 are non-comment and non-blank**
(`grep -vcE '^\s*(#|$)'`, run in this drafting invocation). The 58 executable lines are
partitioned into **17 clauses** by the line ranges below; **the ranges are contiguous and
exhaustive over the 58** and each carries a disposition. **Nothing is "not applicable" without a
reason and nothing is silent.**

| # | `cmd.sh` lines | executable lines | what it does | **disposition in `A1WRT3`** |
|---|---|---|---|---|
| **C1** | `:27` | 1 | `set -uo pipefail` — strict on unset vars and pipe failures, **and deliberately NOT `-e`** | **RESTORED verbatim.** The absence of `-e` is not an oversight and is restored as-is: the script **must** reach its own rc-propagation line (C17′) rather than dying at the first non-zero. **Recorded as a deliberate restoration of an absence.** |
| **C2** | `:29` | 1 | `cd /mnt/case` else `exit 90` | **REPLACED — path only.** `A1WRT3` mounts the arm case at `/mnt` (as `A1WRT2` did). Becomes `cd /mnt \|\| exit 90`, **same refusal, same code**. |
| **C3** | `:31` | 1 | `test -f /mnt/runScript.py` else `exit 91` — **the producer present AT THE POINT OF USE** | **RESTORED**, retargeted to the `A1WRT3` mount `/run_root/runScript.py`. **This is casualty 3 of `A1WRT2-DEF-ENVSEAM` and it is closed here.** |
| **C4** | `:32` | 1 | `test -d 0.orig` else `exit 92` — the COLD-start source present | **DELIBERATELY DROPPED, WITH REASON.** `A1WRT3`'s arms are **CONTINUED** from a staged `4000/`; `0.orig` is a cold-start artefact this item never uses. Retaining it would refuse a correctly-staged continued case. **Replaced by C4′, which asserts the inverse.** |
| **C4′** | *new* | — | `test -d 4000` **and** `test ! -d 0` else `exit 92` — the CONTINUED-start state present and no cold `0/` shadowing it | **REPLACEMENT.** The in-container limb of `G-COLDSTART-SEAM` (§4). Same exit code as the clause it replaces, so the refusal vocabulary does not fork. |
| **C5** | `:33` | 1 | `test -f constant/polyMesh/points.gz` else `exit 93` | **RESTORED verbatim.** |
| **C6** | `:34-37` | 4 | four `test -n` on `A1WR_MODE`/`A1WR_ALPHAS`/`A1WR_TOL`/`A1WR_TMO` else `exit 94` — **the launcher-side names present at the point of use** | **RESTORED**, retargeted to `A1WRT3_MODE`/`A1WRT3_ALPHAS`/`A1WRT3_TOL`/`A1WRT3_TMO`, **and EXTENDED** by `G-ENVSEAM` clause 2 (§4), which additionally asserts every **`AOA_*`** name is non-empty *after* the translation and *before* `python` is invoked. |
| **C7** | `:39` | 1 | `mkdir -p /mnt/out` else `exit 95` | **RESTORED**, retargeted to the arm's own out directory. |
| **C8** | `:41-44` | 3 | **`G-WALLTREAT` clause 1** — `grep -q '"useWallFunction": False,' /mnt/runScript.py` else `exit 98`, then `echo A1WR_WALLTREAT_SCRIPT_OK` | **RESTORED, STRENGTHENED AND PROPERLY REGISTERED — see §3.** **This is casualty 4 and it is the one that is not cosmetic.** |
| **C9** | `:46-48` | 3 | `DECLARED` = count of the α list; `FIRST_ALPHA` = its first element | **RESTORED in shape.** `FIRST_ALPHA` is the sole source of `AOA_ALPHA0` — **the value with no launcher-side counterpart (§1.1)**, and the immediate cause of tonight's `KeyError`. |
| **C10** | `:49` | 1 | `echo A1WR_UNIT mode=… declared=… list=… tol=… tmo=… omp=… utc=…` — the in-container provenance line | **RESTORED**, renamed `A1WRT3_UNIT`, **and now GATED**: §3's host-side presence assertion pins this line's **count**, so the guard's silence is no longer indistinguishable from its success. |
| **C11** | `:51-52` | 2 | `rm -rf 0 && cp -r 0.orig 0` else `exit 96`; `echo A1WR_COLD_START` — **the 0/ reset** | **DELIBERATELY DROPPED, AND IT IS THE ONE CLAUSE THAT MUST NOT BE RESTORED.** Executing it would destroy the staged `4000/` continuation the `SEAM` arm exists to read back, and would drive `G-SEAM` to `GATE FAIL` **for a reason that is not the restart mechanism** — manufacturing the very false negative this item is built to avoid. **Replaced by C11′.** |
| **C11′** | *new* | — | `echo A1WRT3_CONTINUED_START 0/ NOT reset -- this unit continues from 4000/`, and re-assert `0/` still absent **after** any staging step | **REPLACEMENT.** The positive statement of what was deliberately not done, printed into the record rather than left as an absence. |
| **C12** | `:54-55` | 2 | `MODE_FOR_LEDGER`; `PROBE → COLD` remap (*"runScript knows CONTINUED/COLD only"*) | **DELIBERATELY DROPPED, WITH REASON, AND REPLACED BY AN ASSERTION.** `A1WRT3` registers **no `PROBE` arm**, so the remap is unreachable. In its place: `test "$A1WRT3_MODE" = "CONTINUED"` else `exit 94`. **A dropped translation is replaced by a refusal, never by silence.** |
| **C13** | `:57-64` | 8 | **THE `AOA_*` TRANSLATION**, plus `timeout -k 60 "$TMO"`, plus `python … -task sweep > sweep.log 2>&1` | **RESTORED. THIS IS THE REPAIR.** All six assignments restored; `AOA_POINTS_JSON` and `AOA_ALPHA0` — the two with no launcher counterpart — restored **by name**. The `timeout -k 60` in-container deadline is restored and is the cap that survives the death of every agent (§6). |
| **C14** | `:65-66` | 2 | `SRC=$?`; `echo A1WR_SWEEP_RC rc=$SRC` | **RESTORED AND MADE LOAD-BEARING.** In `A1WRT`, `SRC` was captured, printed **and never used again** — `grep -n 'SRC'` over the 102-line file returns exactly those two lines. Here it is the sole input to C17′. |
| **C15** | `:68-71` | 4 | `EXEC`/`CONV`/`BCOK` marker counts; `echo A1WR_COUNTS` | **RESTORED AS REPORTED COUNTS ONLY, AND EXPLICITLY DEMOTED.** They are printed for the reader and consumed by `G-TAILCOUNT`'s *reported* channel. **They never decide an exit status** — see C17. `BCOK` (`grep -c 'BCType=nutLowReWallFunction'`) is promoted into `G-WALLTREAT` clause 2 (§3), where it becomes a gated quantity instead of a printed one. |
| **C16** | `:73-95` | 17 | the entire `PROBE` branch — the fixed-1500 y+ read via the solver-hosted `postProcess` form | **DELIBERATELY DROPPED, WITH REASON.** `A1WRT3` registers no `PROBE` arm; the y+ obligation is discharged instead by **`G-YPLUS`** on the host, from each arm's own written state. **The forbidden-form warning inside C16 is NOT dropped:** `cmd.sh:19-21` records that the *bare* `postProcess` form reads y+ = 0 everywhere — a measured rule-3 blind reader — and **`G-YPLUS` carries that prohibition forward by name** (§4). **A dropped clause's lesson does not drop with it.** |
| **C17** | `:97-102` | 6 | `if [ "$EXEC" -eq "$DECLARED" ]; then exit 0; fi; echo A1WR_TRUNCATED; exit 97` — **the exit status recomputed from `grep -c '^AOA_POINT_END '`** | **DELIBERATELY DROPPED, AND IT IS A DEFECT, NOT A FEATURE.** `AOA_POINT_END` prints for a **crashed** point as well as a successful one, so `A1WRT` U1 scored `EXEC=1 == DECLARED=1` and **exited 0 over its own producer's `rc=97`** `[MEASURED, `A1WRT2_SUCCESSOR_DRAFT.md` §4.1, from `A1WRT/ledger.txt:3` and `alpha12_symmetry_20260903T211651Z_823815.log:9`]`. **Replaced by C17′.** |
| **C17′** | *new* | — | `exit "$SRC"` — **the producer's own rc, propagated, never recomputed from markers** | **REPLACEMENT.** The in-container limb of `G-RC-HONEST`. `A1WRT2`'s host side already refused this defect by construction (`a1wrt2_run_arm.sh:858`); **restoring `cmd.sh` re-opens the hole unless the replacement is registered here, and it is.** |

**ACCOUNTING CLOSED: 1+1+1+1+1+4+1+3+3+1+2+2+8+2+4+17+6 = 58 executable lines = the whole file.**
**12 RESTORED** (C1, C2, C3, C5, C6, C7, C8, C9, C10, C13, C14, C15 — C2, C3, C6 and C7 restored
with a retarget; C8 restored and strengthened). **5 DROPPED, EVERY ONE WITH A STATED REASON**
(C4, C11, C12, C16 deliberately; **C17 dropped as a DEFECT**). **4 of the 5 carry a registered
replacement** — C4→C4′, C11→C11′, C12→the `MODE = CONTINUED` assertion, C17→C17′; **C16 carries no
replacement clause and carries its LESSON instead**, `G-YPLUS`'s bare-`postProcess` prohibition.
**12 + 5 = 17 clauses = 58 executable lines. Unaccounted clauses: ZERO.**

### 2.1 THE FOUR CASUALTIES OF `A1WRT2-DEF-ENVSEAM`, EACH CLOSED BY A NAMED CLAUSE

| casualty | `A1WRT2` state at this draft's opening | closed here by |
|---|---|---|
| 1. `source loadDAFoam.sh` | **repaired 2026-09-05** — but **nothing asserts its effect at the point of use** | **C0** (new, §2.2): `command -v python >/dev/null \|\| exit 89`. The 2026-09-05 fix restored the *line*; this asserts the *outcome*. |
| 2. the `AOA_*` translation channel | **OPEN — caused the crash** | **C13** + **`G-ENVSEAM`** (§4) |
| 3. `cmd.sh:31` runScript-present refusal | **OPEN** | **C3** |
| 4. `cmd.sh:42-44` **`G-WALLTREAT`** | **OPEN — a registered configuration assertion with nothing enforcing it** | **C8** + **§3**, three clauses |

### 2.2 `C0` — THE ONE CLAUSE `cmd.sh` DID NOT HAVE, ADDED BECAUSE ITS ABSENCE WAS MEASURED

`cmd.sh` never checked that `python` resolved, because in `A1WRT` the outer layer sourced the
loader **and then immediately ran a python one-liner** (`a1wrt_run_unit.sh:676-677`), so a broken
loader failed loudly before `cmd.sh` was reached. **`A1WRT3` keeps the loader in the outer layer
and adds the check to the inner one anyway**, because 2026-09-05 measured that `/bin/sh` and
`/bin/bash -lc` both report `python: command not found` on this image without it, and a check that
exists only as a side effect of an unrelated one-liner is not a check.

**`C0`: `command -v python >/dev/null 2>&1 || { echo "A1WRT3_FATAL python unresolved -- loader did not take"; exit 89; }`**, placed before C2. Exit 89 is new and unused elsewhere in this family.

---

## 3. **`G-WALLTREAT` — REGISTERED PROPERLY.** THREE CLAUSES, AND CLAUSE 1 FIRES **BEFORE THE SOLVER**

**Why this is not cosmetic.** `A1WRT3` is a **wall-resolved** case: `useWallFunction: False`, SA,
y+ < 1 on the `wing` patch, an L3 mesh cut for it. **A wall-resolved run that silently uses wall
functions is measuring something other than what it claims** — the near-wall momentum balance is
modelled rather than resolved, `nut` at the wall comes from a log law instead of from the
resolved profile, and every coefficient in the α-tail is then a number from a different physical
model wearing this item's label. **It is a correctness assertion about what ran, not a
bookkeeping nicety.**

**What the predecessor actually asserted**, `cmd.sh:41-44`, verbatim:

    # G-WALLTREAT clause 1, asserted AT THE POINT OF USE on the staged bytes:
    grep -q '"useWallFunction": False,' /mnt/runScript.py \
      || { echo "A1WR_FATAL G-WALLTREAT: staged runScript does not carry useWallFunction False"; exit 98; }
    echo "A1WR_WALLTREAT_SCRIPT_OK useWallFunction False present in staged runScript"

and the item registered **two** clauses, not one — `A1WR_PREREGISTRATION.md:520`: *"`useWallFunction:
False` present in the run script **AND** `BCType=nutLowReWallFunction` present in the solver log
for the `wing` patch; exit 2 if the log does not confirm the BC that actually ran."*
`MAAOA_PREREGISTRATION.md:111` adds the negative limb: *"every point log carries
`BCType=nutLowReWallFunction` **and never the Spalding line**"*.

> ### `G-WALLTREAT`, AS REGISTERED FOR `A1WRT3`
>
> **Subject:** the wall treatment that **actually ran**, read in three independent places.
> **Composition:** `G-WALLTREAT` is a **hard** gate. Any clause failing ⇒ the composed item token
> is at worst `NOT A RESULT`; clauses 1 and 3 refuse at their own exit codes and no verdict is
> composed at all.

| clause | when | where | what it reads | verdict rule |
|---|---|---|---|---|
| **1 — CONFIGURATION, PRE-SOLVER** | **inside the container, before `python` is invoked** (`a1wrt3_cmd.sh`, clause C8) | the **staged producer at its mount path**, `/run_root/runScript.py` | (a) `"useWallFunction": False,` **present**; (b) `"useWallFunction": True` **absent**; (c) the **md5 of the exact bytes grepped**, printed | any of (a)/(b) failing → `exit 98`, **the solver never starts** |
| **2 — WHAT THE SOLVER SAID IT DID** | after the arm, host-side, in `a1wrt3_grade.py` | that arm's own `sweep.log` | `Setting nut wall BC for wing. BCType=nutLowReWallFunction` — **count**, per arm | count `0` → **`GATE FAIL`**; unreadable log → refuse, `exit 2` |
| **3 — THE NEGATIVE LIMB** | same pass | same file | any Spalding wall-function line (`nutUSpaldingWallFunction`, `nutkWallFunction`, `nutUWallFunction`) | any occurrence → refuse, **`exit 2`** |

### 3.1 ⚠ THE STRENGTHENING THAT MATTERS: **CLAUSE 1 NAMES WHAT IT READ, AND ITS SILENCE IS GATED**

**Three defects in the predecessor's form, each repaired by a named limb.**

1. **`grep -q` for the *positive* alone is satisfiable by a file that also carries the negative.**
   A producer containing both a commented `False` and a live `True` passes `cmd.sh:42` and runs
   with wall functions. **Limb (b) closes it**, and its planted control plants a live
   `"useWallFunction": True` **beside** an untouched `False` line and asserts `exit 98`.

2. **It never named *what* it read.** *"present in staged runScript"* does not say **which**
   staged runScript, and `A1WRT2_SEAM_RESULTS.md` §5 measured this family resolving
   `runScript.py` **by basename across 59 candidates in different run roots and silently picking
   the wrong one**. **Limb (c) closes it: the guard prints the absolute mount path, the file's
   byte count and its md5**, and the host side asserts that md5 **equals the pinned producer md5
   `d48f48c5e2e41e86981acbf6feccb3c4`** `[MEASURED in this drafting invocation, `md5sum
   /home/ubuntu/certonomous-runs/A1WRT2/runScript.py`]`. **A gate that reports on bytes it cannot
   identify is a gate on nothing.**

3. **ITS SILENCE WAS INDISTINGUISHABLE FROM ITS SUCCESS.** `cmd.sh:44` prints
   `A1WR_WALLTREAT_SCRIPT_OK` on the pass path — **and nothing on the host ever asserted that line
   was present.** If `cmd.sh` had never been reached at all, the host side would have seen exactly
   what it sees on a pass: no failure. **This is `A1ZE` ADDENDUM C's general test —
   *can the code path distinguish "the check ran and found nothing" from "the check did not
   run"?*** — and `cmd.sh:42-44` fails it.

> **REGISTERED REPAIR, AND IT IS PINNED BY COUNT, NOT BY APPEARANCE (L-493).** `a1wrt3_grade.py`
> asserts `A1WRT3_WALLTREAT_SCRIPT_OK` occurs **exactly once** in **that arm's own
> `container.log`** — not "at least once", not "somewhere in the run root". **L-493: a planted
> control that tests for PRESENCE can be satisfied by the right answer arriving by the WRONG
> ROUTE; pin the count or the path, not the appearance.** Absent or count ≠ 1 → **`GATE FAIL`**,
> reported as *the pre-solver wall-treatment guard did not run*, which is a different finding from
> *it ran and failed* and is reported as a different one.

### 3.2 THE OUTPUT-STREAM SEPARATION THIS REQUIRES, REGISTERED AS A DESIGN COMMITMENT

`A1WRT2` redirected the **whole `docker run`** into `sweep.log`. `A1WRT` redirected **only the
python process** into `sweep.log` (`cmd.sh:64`), leaving `cmd.sh`'s own echoes on the container's
stdout. **`A1WRT3` restores the separation and names both files:**

* **`<ARM>/out/container.log`** — the container's stdout/stderr, i.e. `a1wrt3_cmd.sh`'s own lines:
  `C0`, `C10`'s provenance line, `G-WALLTREAT` clause 1's OK line with its md5, `C11′`, `C14`'s
  `A1WRT3_SWEEP_RC`, `C15`'s counts.
* **`<ARM>/out/sweep.log`** — the producer's stdout/stderr only, exactly as `cmd.sh:64` wrote it.

**This is what makes clause 1's presence assertion independent of the solver's output**, and it is
registered here rather than left to the implementation, because collapsing the two streams is what
made the predecessor's guard unobservable.

### 3.3 `G-WALLTREAT`'s PLANTED CONTROLS (`CLAUDE.md` rule 3) — BOTH DIRECTIONS, ON REAL BYTES

**Every control reads the target bytes before mutating, asserts the bytes actually changed, drives
the REAL gate function, asserts the verdict FLIPPED, restores, and re-asserts the restore landed.**
Each reports **`EXERCISED-PASS` / `EXERCISED-FAIL` / `NOT EXERCISED`**, printed beside the verdict
it accompanies; **`NOT EXERCISED` is never counted as a pass.**

| control | direction | fixture | assertion |
|---|---|---|---|
| `W1a` | fail | static copy of the producer with the `False` line deleted | `exit 98`; restore; re-assert clean |
| `W1b` | fail | static copy carrying a live `"useWallFunction": True` **beside** an untouched `False` | `exit 98` — **the limb (b) control, and the one `cmd.sh` could not have passed** |
| `W1c` | fail | static copy, one byte changed, md5 therefore ≠ the pin | md5 limb refuses; restore |
| `W2a` | **known-positive, MEASURED AND FREE** | `/home/ubuntu/certonomous-runs/A1WRT/alpha12_symmetry/out/sweep.log` — **carries `Setting nut wall BC for wing. BCType=nutLowReWallFunction`, count `1` `[MEASURED, this drafting invocation]`** | clause 2 reads **1**, `PASS` |
| `W2b` | fail | that log with the BC line stripped | count `0` → `GATE FAIL` |
| `W3a` | fail | that log with `nutUSpaldingWallFunction` planted | clause 3 refuses, `exit 2` |
| `W4a` | fail | a `container.log` fixture with the OK line **deleted** | `GATE FAIL`, reported as *the guard did not run* |
| `W4b` | fail | a `container.log` fixture with the OK line **duplicated** | count = 2 → `GATE FAIL` — **the L-493 limb: presence is not enough, the count is pinned** |

---

## 4. `G-ENVSEAM` — THE NEW GATE, AND WHY A SHELL CHECK CANNOT BE IT

**`A1WRT2` had 153 controls and none of them could see this defect, and the reason is
structural, not a shortfall of diligence.** `a1wrt2_run_arm.sh:184` (`g_unbound_precondition`) and
`:244` (`unbound_guard`, armed at `:790`) **read the launcher for unbound *shell* variables**.
`AOA_ALPHA0` is not an unbound shell variable — it is an **absent process-environment entry,
consumed by a python interpreter, on the far side of a `docker run`.** The launcher's shell was
entirely well-formed. **A 154th control of the same kind repairs nothing.**

> ### `G-ENVSEAM`, AS REGISTERED — **hard gate, two clauses on two sides of the container boundary**
>
> **Clause 1 — HOST-SIDE, STATIC, BEFORE THE CONTAINER STARTS.** `a1wrt3_run_arm.sh` parses the
> **staged producer** with Python's `ast`, extracts every `os.environ["X"]` subscript
> (**fatal**) separately from every `os.environ.get(...)`/`getenv(...)` (**defaulted**), records
> the scope of each, and asserts **every fatal name is in the set the container will actually
> receive**. Any fatal name not supplied → **`BLOCKED`**, and **the container does not start.**
>
> **Clause 2 — CONTAINER-SIDE, DYNAMIC, AT THE POINT OF USE.** `a1wrt3_cmd.sh` asserts, after
> the C13 translation is constructed and before `python` is invoked, that **every `AOA_*` name it
> is about to set is non-empty** — `exit 94`, the C6 code.
>
> **NEITHER CLAUSE ALONE SUFFICES AND THAT IS THE POINT.** Clause 1 cannot see a translation that
> computes the wrong *value*; clause 2 cannot run at all if the container never starts. The
> defect lived precisely in the gap between them.

### 4.1 ⚠ CLAUSE 1 READS THE **SAME ARRAY** THAT IS PASSED TO `docker run`, NOT A RE-TYPED COPY

**Registered as a construction requirement, not as an implementation detail.** The supplied set is
built **once**, as a shell array, and **both** the `docker run` invocation and `G-ENVSEAM` clause 1
consume **that array**. A clause-1 implementation that compares the producer's reads against a
hand-maintained list of names **is a second list that will drift from the first**, and the gate
would then certify a correspondence between two things neither of which is what runs — the
**L-493 wrong-route shape** in its most literal form. **A drafted implementation carrying two
lists is rejected at the §3-check-1 diff read, and this sentence is the standard it is rejected
against.**

### 4.2 `G-ENVSEAM`'s PLANTED CONTROL — **ITS KNOWN-POSITIVE IS TONIGHT'S CRASH, ON REAL BYTES, AT ZERO COMPUTE**

| control | direction | fixture | assertion |
|---|---|---|---|
| `E1` | **fail — the MEASURED known-positive** | a **static committed copy** of `A1WRT2`'s exact configuration: the producer reading four fatal names at module scope (`:51`, `:285`, `:286`, `:287`) against a supplied set of `{OMP_NUM_THREADS}` only | clause 1 returns **`BLOCKED`** and **names all four**: `AOA_ALPHA0`, `AOA_ALPHAS`, `AOA_MODE`, `AOA_POINTS_JSON`. **Naming one is not a pass** — `A1WRT2_SEAM_RESULTS.md` §3.2 exists so that no successor "fixes" this by adding a single `-e`, and this control enforces that in code. |
| `E2` | pass | the repaired `A1WRT3` configuration | clause 1 returns clean, **and prints the supplied set it compared against**, so its silence is not its evidence |
| `E3` | fail | producer mutated to add a **fifth** fatal read the translation does not supply | `BLOCKED`, naming the fifth — the gate is not hard-coded to four |
| `E4` | fail | clause 2 driven with `AOA_ALPHA0` set to the empty string | `exit 94` — an **empty** value is not a **present** value |
| `E5` | fail | a producer whose only `os.environ` reads are `.get(...)` with defaults | clause 1 returns **clean**, and the control asserts it does **NOT** block — **the false-positive direction, exercised.** `A1WRT2_SEAM_RESULTS.md` §5.1 measured **31 of 37** resolved entry scripts in this family reading nothing fatal at all; a gate that blocked them would be useless. |

**`G-FIXTURE` binds every one of these:** every fixture is **static, committed bytes**, and **no
fixture path resolves inside this item's run root** (the L-435 repair, inherited unweakened).

---

## 5. GATES, VERDICT COMPOSITION, AND THE SUCCESS LABEL

**`A1WRT3` CAN SUCCEED. Success is called `GATE REACHED`.** It is emitted by `a1wrt3_grade.py`,
by a function `compose_item()` whose last statement prints the single line
**`A1WRT3_VERDICT <token>`**, and by nothing else. **No verdict for this item is composed by a
supervisor, by a lane, by a board write or by a commit message.** If that line is absent from the
grader's stdout, **this item has no verdict**, and the honest statement is `PENDING`.

```
hard = [G-PATCH, G-COLDSTART-SEAM, G-IMG, G-FREEZE, G-UNBOUND,
        G-ENVSEAM, G-WALLTREAT,
        G-NOGRAD, G-WARPPROBE, G-FIXTURE, G-NOBAND, G-STALL]
soft = [G-SEAM, G-TAILCOUNT, G-RC-HONEST, G-YPLUS, G-CAPS, G-CEILING]

if "NOT A RESULT" in hard or "NOT A RESULT" in soft:  raw = "NOT A RESULT"
elif "BLOCKED"    in hard or "BLOCKED"    in soft:    raw = "BLOCKED"
elif "GATE FAIL"  in hard or "GATE FAIL"  in soft:    raw = "GATE FAIL"
elif "GATE REACHED" in soft:                          raw = "GATE REACHED"
else:                                                 raw = "PASS"
final = min(raw, CEILING)     # CEILING = "GATE REACHED"
assert final in {"PASS","GATE REACHED","GATE FAIL","NOT A RESULT",
                 "BLOCKED","PENDING"}   # else REFUSE, exit 2
```

**`G-ENVSEAM` and `G-WALLTREAT` are the two additions to `A1WRT2`'s list and both go in `hard`.**
Every hard list is tested for **both** `GATE FAIL` and `NOT A RESULT` — the `D19M-COMPOSE-DEF-1`
repair, carried as control `Q-COMPOSE-1`, which plants `NOT A RESULT` into one hard gate and
asserts the composed token is `NOT A RESULT` and **not** `GATE REACHED`.

**`PASS` IS UNREACHABLE AND THAT IS REGISTERED, NOT AN OVERSIGHT.** The L3 family has no Roache
triple, so no value this item produces can be grid-converged or carry a band (`G-NOBAND`).
`min(raw, CEILING)` caps a `PASS` to `GATE REACHED` **and the grader prints both `raw` and
`final`** so the cap is visible.

**`NO ITEM VERDICT BY CONSTRUCTION` IS FORBIDDEN.** If `a1wrt3_grade.py` reaches its end without
printing `A1WRT3_VERDICT`, an `EXIT` trap prints
`A1WRT3_VERDICT PENDING -- the composer did not run, last checkpoint <n>` and exits **12**.

**The remaining gates are inherited from `A1WRT2` §4 by name and unweakened** — `G-SEAM`
(band `SEAM_BAND_REL = 1.0e-03`), `G-TAILCOUNT` (6 of 6, *executed* meaning a value or a certified
failure with a residual history, never a printed marker), `G-RC-HONEST`, `G-UNBOUND`, `G-NOGRAD`,
`G-WARPPROBE`, `G-PATCH` (`Mesh has 3 solution (non-empty) directions (1 1 1)`),
`G-COLDSTART-SEAM`, `G-CAPS`, `G-CEILING`, `G-YPLUS`, `G-STALL`, `G-NOBAND`, `G-FIXTURE`,
`G-IMG`/`G-FREEZE`, and the `Q-COMPOSE-1..4` composer controls. **`G-YPLUS` additionally carries
forward `cmd.sh:19-21`'s prohibition by name: the bare `postProcess` form reads y+ = 0 everywhere
— a measured rule-3 blind reader — and is FORBIDDEN; only the solver-hosted form is used.**

---

## 6. THE DESIGN — TWO ARMS, **`SEAM` FIRST, `TAIL` ONLY BEHIND `SEAM`'s VERDICT**

| arm | patch | start | points | iterations | what it isolates |
|---|---|---|---|---|---|
| **`SEAM`** | `symmetry` | CONTINUED from a **staged copy** of `A1WRT` U1's `4000/` | α = 12 | **200** (`endTime` 4000 → 4200) | **that the restart actually loaded the state** — the restart-fidelity control, and nothing else |
| **`TAIL`** | `symmetry` | CONTINUED from `SEAM`'s final state | α = 13,14,15,16,17,18 | 4,000 each | **the tail** |

**Inherited unchanged, by md5:** producer `d48f48c5e2e41e86981acbf6feccb3c4` `[MEASURED, this
invocation]`; mesh `A1WR` L3, 130,304 cells; image `dafoam-idwarp-rot:v1`,
`sha256:2927768a16ac…`, `libidwarp` md5 `85f59e87253e0a71a813f64ca6e4c425`;
`primalMinResTol = 1.0e-8`, SA, `useWallFunction: False`, np = 1, `OMP_NUM_THREADS=1`, one-core
cpuset. **Changing any of them would make the tail non-comparable to the α 0…12 body it extends.**

**`A1WRT3` stages a COPY of `A1WRT` U1's `4000/` and never writes into `A1WRT`'s run root.**

**`SEAM`'s `endTime` change is ring-fenced exactly as `A1WRT2` §3 registered it:** `SEAM`'s
coefficients are used by `G-SEAM` and by nothing else, are never compared against any
4,000-iteration value as physics, and never enter a polar.

> ### ⚠ THE PRECONDITION, REGISTERED AS THE ITEM'S SPINE
>
> **`TAIL` DOES NOT LAUNCH UNTIL `SEAM` HAS PRODUCED A VERDICT.** `a1wrt3_run_arm.sh` refuses
> `--arm TAIL` at **`rc=7`** against a run root whose `SEAM` verdict does not permit it.
> **675 core-min does not move until 10 has spoken.** Both arms are priced in §7; **only `SEAM` is
> bought.**
>
> **AND AN UNRESOLVED `SEAM` IS NOT A PERMISSION.** `A1WRT2` measured this the hard way: an
> unresolved prediction *"is not a permission and is not a refusal either; it is a hole where a
> measurement should be."* **Registered here: `SEAM` `UNRESOLVED` ⇒ `TAIL` refused at `rc=7`, and
> the refusal reason recorded as `SEAM-UNRESOLVED`, distinct from `SEAM-GATE-FAIL`.**

**No point is retried, relaxed, re-tuned or dropped.** A point that fails is recorded with its
residual history and the sweep continues, every subsequent point flagged `after_exception=TRUE`.
**A missing point on a polar is a lie by omission.**

---

## 7. COST — REGISTERED HERE, PER ARM, WITH A CAP, BEFORE ANY COMPUTE (`CLAUDE.md` rule 12)

**`cost_basis`: core-minutes MEASURED from logs (wall s × ranks ÷ 60). Dollars DERIVED at
c7a.4xlarge $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5). **No dollar figure in this document is a measurement.**

### 7.1 The anchors, with their program statements and the match assertion (`DAFOAM_CHARTER.md` §18.1)

| anchor | value | ranks | adjoint | colouring | start mode | box state | artefact |
|---|---|---|---|---|---|---|---|
| **A-CONT** | **0.46178 s/it** | 1 | NO | NO | **CONTINUED** | **NOT LABELLED — disclosed** | `A1WR/STAGE12/sweep_I/out/sweep.log`, `AOA_POINT_VALUES idx=12 alpha=12 … wall_s=1847.1318` over 4,000 it `[MEASURED]` |
| **A-COLD** | **0.814982 s/it** | 1 | NO | NO | **COLD** | 63.1 % min / 76.6 % mean / 90.5 % max busy, 1 sibling `[MEASURED]` | `A1WRT/alpha12_symmetry/out/sweep.log`, `ExecutionTime = 3259.93 s` over 4,000 it; `docs/COST_CALIBRATION.md` row `C-20260903T223309.077366Z-bc699e66` |
| **A-IMPORT** | **93.85 s** container start + DAFoam import | 1 | NO | NO | — | — | `A1WRT` §4.3 `[MEASURED]` |
| **A-FRAME** | **4 s (0.067 core-min)** container frame to a **python-import death** | 1 | — | — | — | — | `A1WRT2/SEAM/ledger.txt`, `wall_s=4 ranks=1` `[MEASURED 2026-09-05]` |

**MATCH ASSERTION.** `A1WRT3`'s registered program is **ranks 1, adjoint NO, colouring NO, tree
CONTINUED**. It matches **A-CONT on all four terms** and is priced from it.

* **A-COLD differs on the fourth term** (COLD vs CONTINUED) → **not an anchor**; used only as the
  pessimistic end of a bracket, which is a deliberate over-price and is labelled as one.
* **⚠ A-FRAME IS NOT AN ANCHOR AND IS NOT USED AS ONE, AND THE REFUSAL IS DELIBERATE.** It is
  tonight's newest and most tempting number, and **it prices a different program**: a container
  that dies at python import, before DAFoam is imported and before the mesh is read. **A-IMPORT
  prices the program `A1WRT3` will actually run.** A-FRAME is recorded as the **measured floor**
  of the container term and is quoted nowhere in the estimate. *(§18.1's discipline applied
  against this document's own convenience.)*

**A-CONT's box state is unlabelled and is the term that is missing**, which is why the estimate is
a **BRACKET and not a point**, and why the caps are sized against the bracket's upper end.

### 7.2 The estimate — per arm, every term named

| arm | term | arithmetic | core-min |
|---|---|---|---|
| `SEAM` | 200 it × 0.46178 s/it (A-CONT) | 92.356 s | **1.539** |
| `SEAM` | container start + DAFoam import (A-IMPORT) | 93.85 s | **1.564** |
| `SEAM` | `a1wrt3_cmd.sh` preflight — C0/C3/C4′/C5/C6/C7/C8/C9/C12 tests and greps | ≈ 1 s | **0.017** |
| | **`SEAM` ESTIMATE** | | **≈ 3.120** |
| `TAIL` | 6 points × 4,000 it × 0.46178 s/it (A-CONT) | 11,082.72 s | **184.712** |
| `TAIL` | container start + import (A-IMPORT) | 93.85 s | **1.564** |
| `TAIL` | tail-stiffening allowance on α 14…18, **EXTRAPOLATED** | 5 × 4,000 × 0.46178 × 0.25 = 2,308.9 s | **38.482** |
| `TAIL` | `a1wrt3_cmd.sh` preflight | ≈ 1 s | **0.017** |
| | **`TAIL` ESTIMATE (point)** | | **≈ 224.775** |
| | **ITEM ESTIMATE (point)** | 3.120 + 224.775 | **≈ 227.895 core-min** |
| | **ITEM ESTIMATE (pessimistic bracket end**, A-COLD substituted) | 6 × 4,000 × 0.814982 ÷ 60 = 325.993; + 38.482 + 3.120 | **≈ 367.595 core-min** |

**Dollars, DERIVED, not measured:** `SEAM` **$0.00267**; `TAIL` **$0.19218**; item point
**$0.19485**; pessimistic bracket end **$0.31429**; the item ceiling below **$0.58567**.
All under the $25 pre-authorisation **and costed here anyway, because a blanket is not a per-item
reading** (`CLAUDE.md` rule 9).

**A host-side term that is NOT in either arm's ledger and is named rather than omitted:**
`G-ENVSEAM` clause 1's `ast` parse plus the instrument md5 sweep run on the host before each
container — **≈ 0.5 s per arm ≈ 0.017 core-min for the item**. It is real spend, it does not
appear in `ledger.txt` because `ledger.txt` records container wall time, and **an estimate that
quietly excludes what it cannot see is the shape this family keeps finding.**

**Every point is priced at the FULL 4,000 iterations and no saving is taken in advance**, because
§8's `P3` predicts **no** tail point converges — so 4,000 is the *expected* case, not a
conservative one. If a point converges and stops early, the ratio comes in low and that is
reported at calibration as a favourable misprediction with its cause named, never quietly
absorbed. **The term most likely to carry the error is the tail-stiffening allowance**, and it is
labelled `EXTRAPOLATED` in advance.

### 7.3 The caps, the deadlines, and the item ceiling

| arm | estimate | **cap** | basis | in-container deadline |
|---|---|---|---|---|
| `SEAM` | 3.120 | **10.0** | **3.205×** the estimate | **900 s** |
| `TAIL` | 224.775 | **675.0** | **3.003×** the estimate, and **1.836×** the pessimistic bracket end | **41,400 s** |
| | | **ITEM CEILING 685.0** | the two caps summed — **not a new budget** | |

Sanaa, 2026-09-03, verbatim: *"still carries a hard per-run cap (set by the team at ~3× its own
estimate, not by me) … The estimate is an instrument, not a permission slip."*

**The deadline lives INSIDE the container** — restored by clause C13's `timeout -k 60 "$TMO"` —
**so the cap stops the run even if the driver, the daemon and every agent die.** `A1WR`'s own kill
is the argument: its driver was polling healthily at 02:24:58Z and the box went down seven seconds
later. **`A1WRT2` deleted `cmd.sh` and with it the in-container `timeout`; this restores it.**

**An overrun STOPS the run. It does not get a new budget** (`CLAUDE.md` rule 12). `G-CAPS` reports
`NOT A RESULT` on the affected points; `G-CEILING` sums this item's own ledger spend, adds the
next arm's cap, and **refuses before that arm launches** if the projection crosses 685.0 — with
the `A1WRT` `:296-304` **UNMEASURED-refusal limb** carried unweakened: **an unparseable ledger
REFUSES rather than assuming zero, because a zero that means "could not read" is a planted zero**
(`CLAUDE.md` rule 3).

### 7.4 Memory envelope, predicted before the launch (`DAFOAM_CHARTER.md` §7)

**Predicted peak ≤ 8 GiB per container, one at a time, np = 1.** Basis: `A1WRT` U1 ran the
identical mesh, image and solver at `memory=8g` with `inspect(exit,oomkilled)=[0 false]`,
`memavail_pre_GiB=26.11`, `memavail_post_GiB=27.42` `[MEASURED, `A1WRT/ledger.txt:3`]`.
**No adjoint is built**, so §7's A3/A6 mesh-sized-matrix mechanism does not apply, and that is
stated rather than left unmentioned.

### 7.5 Calibration at completion — **AND THE REGISTERED REFUSAL**

At each arm's completion a row lands in **`docs/COST_CALIBRATION.md`** under that file's append
rules and the rule-10 private-index protocol, stating the ratio actual/predicted, attributing the
gap (contention / waste / misprediction — **waste separately named and never absorbed into the
ratio**, `COMPUTE_BUDGET_CHARTER.md` §6), and naming the item row it anticipates so no census
double-counts.

> ### ⚠ REGISTERED **BEFORE** IT IS NEEDED: A RATIO IS FILED **ONLY** IF THE ESTIMATE'S MODEL WAS EXERCISED
>
> **If the arm dies before the solver runs, NO calibration ratio is filed**, and the row reads
> *a crash at N core-min, with the estimate UNTESTED.*
>
> **This is registered now, in advance, because `A1WRT2` had to reason it out afterwards** —
> `0.067 / 3.10344 = 0.0216` was computable and was correctly **refused**, because the 3.10344
> figure prices 200 solver iterations at 0.46178 s/it and **zero iterations ran**. A ratio of
> 0.0216 would have entered the ledger as evidence that this family over-estimates by 46×, **and
> it is evidence of nothing but that a python interpreter exits quickly.** A rule reasoned out
> after the fact is a rule that could have been reasoned the other way; **this one is frozen
> before the compute.**

---

## 8. THE REGISTERED PREDICTIONS, THE THIRD OUTCOME, AND THE `UNRESOLVED` TOKEN

**Predictions are scored `HIT` / `MISS` / `UNRESOLVED`. A `MISS` is a FINDING and is reported as
one; it is never written as `GATE FAIL`. Predictions are not gates and do not enter the
composition.**

### 8.1 ⚠ **`UNRESOLVED` IS REGISTERED AS A FIRST-CLASS READING, FOR EVERY PREDICTION AND EVERY FALSIFIER IN THIS DOCUMENT**

> **Definition, registered:** a prediction or falsifier reads **`UNRESOLVED`** when **the leg that
> produces its statistic did not run, or ran and did not produce the statistic**. It is printed
> with **the reason** and **the artefact that is absent, by absolute path**.
>
> **`UNRESOLVED` is never scored `HIT`, never `MISS`, and never enters the composition.**
> **`UNRESOLVED` is an honest token; silence is not**, and the grader's `EXIT` trap (§5) makes
> silence impossible.

**This clause exists because two items measured its absence in one day.** `D6RF3`'s **`F1`** is
`UNRESOLVED` tonight because its bar — `eta_raw`, the primal's own repeatability, **measured in
the same run** — was never computed, the producing leg having stopped early. `A1WRT2`'s
`P-SEAMTIME` is `UNRESOLVED` because its statistic was never emitted.

> **THE ENUMERATION THE QUALIFICATION DEMANDS — checked by going through every bar in this
> document, not by recollection:**
>
> | gate | its bar | run-derived? |
> |---|---|---|
> | `G-SEAM` | `SEAM_BAND_REL = 1.0e-03`, relative | **NO — registered constant** |
> | `G-TAILCOUNT` | 6 of 6 | **NO — declared constant** |
> | `G-YPLUS` | y+max < 1.0 | **NO — registered constant** |
> | `G-CAPS` | 10.0 / 675.0 core-min | **NO — registered constants (§7.3)** |
> | `G-CEILING` | 685.0 core-min | **NO — registered constant** |
> | `G-WALLTREAT` | presence/absence, and count = 1 | **NO** |
> | `G-ENVSEAM` | set membership | **NO** |
> | `G-RC-HONEST` | producer rc | **NO** |
>
> **`A1WRT3` REGISTERS NO RUN-DERIVED BAR.** Its bars cannot go missing the way `D6RF3`'s `F1`
> bar did.
>
> **BUT THE SAME HOLE EXISTS ON THE OTHER SIDE AND IS REGISTERED HERE.** `F-SEAM` (§9) and
> `P-SEAM*` read their **statistic** from `SEAM`'s own output — **and `SEAM` is precisely the leg
> that did not run last time.** A fixed bar with a missing statistic is exactly as unscoreable as
> a measured bar with a present one. **§8.1's `UNRESOLVED` clause covers both directions and is
> the reason it is written as a general clause rather than as a note on one row.**

### 8.2 The predictions

| id | prediction | how scored | what a MISS means |
|---|---|---|---|
| **P1** | `G-SEAM` **PASSES** — the restart loads the state and `SEAM`'s first print reproduces U1's terminal `CL 1.1836353615763` / `CD 0.030758033132912` inside the 1.0e-03 band | the gate's own reading | the continuation is silently cold-starting — the `A1WRT` §2.2 mechanism reaching a CONTINUED arm. **A defect finding, and the most valuable single outcome this item can produce** |
| **P2** | `G-TAILCOUNT` reaches **6 of 6** | the gate's own reading | the tail is not reachable in one process and the successor is a per-point item |
| **P3** | **ZERO tail points converge** — `satisfied the prescribed tolerance` occurs **0** times across α 13…18 | counted from the log, **with the counter shown able to count a planted occurrence** | the coupling changes at high α in a way §7's floor analysis does not predict — and it would be the first convergence this mesh family has ever produced |
| **P4** | **`dCL/dα` REMAINS POSITIVE across α 13 → 18** | recomputed by the grader from the per-point series | — |
| **P5** | DAFoam prints `Primal solution failed!` for **at least one** point in α 13…18 | counted from the log | the 1e-6…1e-8 dead band swallows the whole tail and the certification channel is blind across the range — a finding about the instrument, not the physics |
| **P6** | **`G-ENVSEAM` clause 1 returns CLEAN on the first attempt** — the restored translation supplies all four fatal names | the gate's own reading | **the repair is incomplete**, and the item stops at `BLOCKED` **before spending anything**, which is the whole purpose of putting the gate in front of the container |

> **`P4` IS REGISTERED AND IS PREDICTED TO MISS.** NACA0012 at α 13…18 is at or past the onset of
> significant separation, `dCL/dα` should flatten and reverse, and `A1WR`'s α 0…12 body already
> shows `dCL/dα` **strictly decreasing** across its whole range. **It is registered anyway,
> unhedged, in the direction this lane expects to be wrong**, because a prediction set in which
> every entry is expected to hit is a set chosen to be safe.
>
> **AND A `P4` MISS MAY NOT BE READ AS A STALL MEASUREMENT.** `G-STALL` refuses at `exit 2` on any
> output binding a stall or separation word to a numeric angle, and it binds on this row as on
> every other. **The temptation lives exactly here, which is why the gate is carried unweakened.**

### 8.3 ⚠ `P-SEAMTIME3` — **THE SEAM-TIME PREDICTION, WITH THE CRASH BRANCH REGISTERED EXPLICITLY**

**`A1WRT2`'s `P-SEAMTIME` registered two branches and wrote "BOTH ARE RESULTS". The run produced a
third: the script died before emitting any output at all.** *A prediction can only be scored
against the test it actually met* — so this successor registers the third branch **by name, before
the compute**, and then registers what happens if a fourth arrives.

**Statistic:** the anchored `^Time = ` lines in `SEAM/out/sweep.log`, read by a counter **shown
able to see a planted anchored line and to reject an indented decoy** (`CLAUDE.md` rule 3 — the
`A1WRT2` watcher's control passed and is reused by design, `a1wrt2_seam_watch.out`:
*"CONTROL planted first=4001 last=4200 count=2 … CONTROL PASS"*).

| branch | observed | reading | registered consequence |
|---|---|---|---|
| **A** | `anchored_count > 0`, **first = 4001**, **last = 4200** | **the restart loaded the state** | `P-SEAMTIME3` **HIT**; `G-SEAM` decides `PASS`/`GATE FAIL` on the coefficients; `TAIL` may be authorised by the supervisor |
| **B** | `anchored_count > 0`, **first = 1** | **the producer resets on a `latestTime` start** | `P-SEAMTIME3` **HIT (branch B)**; `G-SEAM` `GATE FAIL`; **`TAIL` refused at `rc=7`**; the item stops at ≤ 10.0 core-min **with the mechanism measured for the first time in this family** |
| **C — THE CRASH BRANCH** | **`anchored_count = 0`** — no `Time` line of any value; the producer died before OpenFOAM was invoked | **`UNRESOLVED`. The quantity is `UNMEASURED`.** This says **NOTHING** about `startFrom latestTime` | item verdict **`NOT A RESULT`**; **`TAIL` refused at `rc=7`, reason `SEAM-UNRESOLVED`**; **NO calibration ratio filed** (§7.5); the record must quote `SEAM/out/rc`, the last line of `SEAM/out/container.log` and the last line of `SEAM/out/sweep.log` **by absolute path** |
| **D** | `anchored_count > 0`, **first = 4001**, **last ≠ 4200** | **the seam IS measured — the restart loaded — and the arm is TRUNCATED** | `P-SEAMTIME3` **HIT (branch D)**; `G-SEAM` evaluates normally on the first print; `G-COMPLETE` **`GATE FAIL`** on the last-time clause; **`TAIL` refused**; this is a **real result about the seam** and is not collapsed into C |
| **E — CATCH-ALL** | **anything else** | — | the grader prints **`P-SEAMTIME3 UNCLASSIFIED`** with the observed tuple `(anchored_count, first, last, rc)` and the item is **`NOT A RESULT`** |

> **BRANCH E IS THE POINT OF THIS TABLE.** Four branches are not more exhaustive than two by any
> argument this lane can make — **`A1WRT2` believed two were exhaustive and was wrong within four
> seconds.** So the enumeration is closed by a **refusal**, not by a claim: **an outcome in none of
> the registered branches produces `NOT A RESULT` and prints what it saw.** Registering a
> catch-all that PASSES would reproduce the defect one level up; **this one fails.**
>
> **AND BRANCH C IS NOT A PERMISSION.** An `UNRESOLVED` `SEAM` is neither an authorisation for
> `TAIL` nor a refusal of the physics — *"it is a hole where a measurement should be."*
> **`TAIL` stays PARKED.**

---

## 9. **THE FALSIFIER — `F-SEAM`, WITH ITS §21 ARITHMETIC SHOWN AT REGISTRATION**

**`DAFOAM_CHARTER.md` §21 (v1.0g, 2026-09-05) binds this draft**, and it is new law: a registered
trivial baseline **names the gate it is predicted to fail**, that gate **must be the one whose
verdict the withdrawal clause withdraws**, and the pre-registration **shows the arithmetic** —
predicted value beside that gate's own bar, inequality written out. **A falsifier whose predicted
value does not fail its named gate is not a falsifier.**

**§4's own instantiation does not attach to this item and that is stated rather than assumed:**
§4's subject is *"the registered trivial baseline for a DAFoam FD gate … the same probe at a
deliberately wrong step."* **`A1WRT3` has no FD gate and computes no gradient** (`G-NOGRAD`
refuses if `compute_totals` appears even once in the staged producer). **§21's requirement,
however, binds any registered trivial baseline**, so this item registers one **in §4's shape,
adapted to the gate it actually has.**

### 9.1 The trivial baseline, and the deliberately-wrong variable

**For an FD gate the deliberately-wrong variable is the STEP. For a restart-fidelity gate it is
the START.** `F-SEAM` is **the same probe with the one registered variable set wrong**: `G-SEAM`
driven against a **COLD** α = 12 terminal state instead of a **CONTINUED** one.

> ### `F-SEAM`, REGISTERED
>
> **NAMED GATE: `G-SEAM`.** **That gate's own bar: `SEAM_BAND_REL = 1.0e-03`, relative.**
>
> **THE ARITHMETIC, AT REGISTRATION, IN ONE SENTENCE WITH THE INEQUALITY WRITTEN OUT:**
> the COLD α = 12 terminal `CL = 1.1836353615763` against the CONTINUED α = 12 terminal
> `CL = 1.19079592024` gives a relative disagreement of
> **|1.1836353615763 − 1.19079592024| ÷ 1.19079592024 = 6.013254e-03**, and
> **6.013254e-03 > 1.0e-03** — **6.013× the bar — so the trivial baseline FAILS `G-SEAM`.**
>
> **THE WITHDRAWAL CLAUSE WITHDRAWS `G-SEAM`'s VERDICT — the same gate, and no other.**
> If `G-SEAM`, driven on the cold-vs-continued pair, returns anything other than **`GATE FAIL`**,
> then **`G-SEAM` is not measuring restart fidelity at all**, and **`G-SEAM`'s verdict on the real
> `SEAM` arm is WITHDRAWN**, together with §10's claim that the tail is a continuation of `A1WR`'s
> polar. **Named gate = withdrawn gate. §21.3 satisfied on both limbs.**

**⚠ THE PREDICTED VALUE IS NOT PREDICTED — IT IS ALREADY MEASURED, AND THE FALSIFIER COSTS ZERO
COMPUTE.** Both operands are on disk before the freeze:
`[MEASURED, `A1WRT` ADDENDUM 8 §A8.2 and `A1WRT2_SUCCESSOR_DRAFT.md` §2.3, from
`A1WRT/alpha12_symmetry/out/sweep.log`, `A1WR/STAGE12/sweep_I/out/sweep.log` and
`a1wr_alpha12_reference.tsv`]`. **§21.3's "cost of compliance: zero" is literal here.**

**THE CLEARANCE, STATED HONESTLY AND NOT INFLATED (§21.5).** 6.013× is a real clearance and it is
not a large one. This is a bar **exercised against a value it must reject**, which §21.5 counts as
the working case — **8 families of 52 have ever managed that** — but a lane should read `6.013×`
as *comfortably outside and nowhere near an order of magnitude*, not as *unassailable*. **The CD
limb is tighter and is registered as the weaker of the two:** CD rel **3.018116e-03** against the
same 1.0e-03 bar is **3.018×**, and it is disclosed rather than quietly dropped in favour of the
better number.

**THE A8.3 CAVEAT TRAVELS AND IS NOT DROPPED.** These CL/CD are read from per-iteration prints on
a point whose solver wrote `CL=NA CD=NA`. **The residual channel is free of that caveat** — same
mesh, image, solver, α and 4,000-iteration budget, one variable moved: the CONTINUED point printed
`Primal min residual` **0** times and `Primal solution failed` **0** times; the COLD point printed
them **1** and **2** times, value `1.051926887799928e-06` `[MEASURED, `A1WRT2_SUCCESSOR_DRAFT.md`
§2.3]`. **The solver's own certification state flips between the two.** The caveat is on the
magnitude, not on the direction, and **the direction is what `F-SEAM` rests on.**

### 9.2 `F-SEAM`'s third reading

**If `SEAM` does not run, or runs and emits no first-print coefficients (§8.3 branch C),
`F-SEAM` reads `UNRESOLVED`** under §8.1 — **and the trivial-baseline limb still runs**, because
it reads only bytes already on disk. **So the falsifier's own arithmetic is scoreable even when
the item's compute is not**, which is the property `D6RF3`'s `F1` lacked and paid for. **That is
not luck; it is why the trivial baseline was sized against artefacts that exist before the freeze.**

### 9.3 The item's other registered falsifiers

* **`F-ENV`** — **named gate: `G-ENVSEAM` clause 1.** Its bar is set membership, and its trivial
  baseline is control `E1` (§4.2): the `A1WRT2` configuration, four fatal reads against a supplied
  set of one. **Predicted value: 4 unsupplied fatal names; bar: 0 unsupplied permitted;
  4 > 0 — it fails the named gate.** **Withdrawal:** if `E1` does **not** return `BLOCKED` naming
  **all four**, `G-ENVSEAM` is not measuring the environment seam and **`G-ENVSEAM`'s verdict is
  withdrawn** — the item then reports `NOT A RESULT` for want of a working guard rather than
  shipping a gate it cannot trust. **Named gate = withdrawn gate.**
* **`F-WALL`** — **named gate: `G-WALLTREAT` clause 1.** Trivial baseline: control `W1b`, a
  producer carrying a live `"useWallFunction": True` beside an untouched `False`. **Predicted
  value: exit 98; bar: exit 0 required to proceed; the baseline does not proceed — it fails the
  named gate.** **Withdrawal:** if `W1b` proceeds, clause 1 is a substring test and not a
  configuration assertion, and **`G-WALLTREAT`'s verdict is withdrawn**, taking every
  wall-resolved claim in the item's output with it. **Named gate = withdrawn gate.**

**Every falsifier in this document names one gate, and the gate it names is the gate its
withdrawal clause withdraws. Checked row by row in this drafting invocation: 3 falsifiers,
3 named gates, 3 matching withdrawals, 0 mismatches.**

---

## 10. WHAT THIS ITEM MAY NOT CONCLUDE

Inherited from `A1WRT` §7 and `A1WRT2` §10 **unweakened**, and none of it is relaxed:

- **`FEASIBILITY`.** The L3 family has no Roache triple. **No value carries a band, none is
  grid-converged, and `PASS` against a threshold is unavailable on any physical quantity.**
  Ceiling `GATE REACHED`.
- **NO STALL ANGLE IS REPORTED AND NONE MAY BE DERIVED.** `G-STALL` refuses at `exit 2` on any
  output binding such a word to a numeric angle. **The tail is exactly where that temptation
  lives.**
- **A non-converged point is not evidence of separation** — it is evidence that the steady solver
  stopped converging, reported with its residual history.
- **A converged high-α point is not evidence of attached flow.** 2-D steady RANS with SA past the
  onset of significant separation is not a valid model of the flow at **any** resolution.
  **Convergence and correctness remain independent claims and only the first is measured here.**
- **No adjoint claim.** Primal only, undeformed geometry, no optimiser, no trim.
- **Nothing about `empty`**, nothing about the compressible arm, nothing about
  `symmetry`-versus-`empty` coefficient contamination (`A1ZE`'s question, BLOCKED at the
  toolchain).
- **The build confound stands**: the coarse sweeps ran the SHIPPED image; this and `A1WR` run the
  PATCHED `dafoam-idwarp-rot:v1`. `G-WARPPROBE` converts it from a caveat into a measurement.
- **⚠ AND ONE THAT IS NEW TO THIS ITEM: a passing `G-WALLTREAT` IS NOT EVIDENCE THAT y+ < 1.**
  Clause 1 says the configuration requested the wall-resolved path; clause 2 says the solver set
  the low-Re BC. **Neither says the mesh delivered the resolution that path assumes** — that is
  `G-YPLUS`'s subject and only `G-YPLUS`'s. **The two are reported as two rows and are never
  composed into one claim.**

---

## 11. WHAT IS OWED BEFORE THIS CAN FREEZE, AND WHAT IS OWED BEFORE IT CAN LAUNCH

### `[OWED — GATES THE FREEZE]`

1. **`a1wrt3_cmd.sh` written** — §2's 17 clauses as code, **one file, not an inline heredoc**
   (the SO-1b lesson, `cmd.sh:8`, and the reason `A1WRT2` could delete it invisibly was that it
   was never a file there at all). **Does not exist.**
2. **`a1wrt3_run_arm.sh`, `a1wrt3_stage.py`, `a1wrt3_grade.py` written**, with §4's `G-ENVSEAM`
   (both clauses, single-array construction per §4.1), §3's `G-WALLTREAT` (three clauses plus the
   count-pinned presence assertion), §5's composer and `EXIT` trap, §6's `rc=7` precondition,
   §7.3's ceiling guard with the UNMEASURED-refusal limb. **None exists.**
3. **Every control driven, BOTH directions, with its `EXERCISED-*` state printed** — `W1a/W1b/W1c`,
   `W2a/W2b`, `W3a`, `W4a/W4b`, `E1`–`E5`, `F-SEAM`'s two directions, `Q-COMPOSE-1..4`. The
   selftest's own rc and control count quoted in the freeze banner. **`NOT EXERCISED` is never
   counted as a pass.**
4. **The instrument table enumerated by EXTRACTION, not from memory** (`DAFOAM_CHARTER.md` §18.3):
   every `$HERE/`, `$BASE/`, `$LAUNCHER`-style path and every local import pulled out of the
   frozen scripts, resolved against the item directory, and **asserted to EXIST in the freeze
   commit's tree BEFORE any md5 is asserted** — existence first, separately, because an
   md5-agreement control can read 8 of 8 while a dependency the frozen code executes is absent.
5. **The `a1wrt3_cmd.sh` md5 pinned in `PIN_INSTRUMENTS` and GATED by `G-FREEZE`.**
   `A1WRT2` §13.1 measured that its launcher's md5 was **recorded in `MANIFEST.json` but never
   gated** (`a1wrt2_grade.py:94`), so a post-freeze edit to it would have falsified an asserted
   row **silently**. **The restored `cmd.sh` is the single most load-bearing file in this item and
   it is not going in ungated.**
6. **`MANIFEST.json` must declare the CONTAINER's environment, not the launcher's.** `A1WRT2`'s
   `env_declared` listed `A1WRT2_RUN_ROOT`, `A1WRT2_STATUS_DIR`, `BASH_SOURCE` — **the launcher's
   own shell environment, the wrong side of the boundary** — which is `A1WRT2-DEF-ENVSEAM` showing
   up a second time in a second instrument. **`A1WRT3`'s manifest declares the `-e` array and the
   `AOA_*` translation set.**
7. **The run root `/home/ubuntu/certonomous-runs/A1WRT3/` re-checked ABSENT by execution in the
   freezing shell**, named as the directory that does not exist and **checked, not asserted.**

### `[OWED — GATES THE ENQUEUE, NOT THE FREEZE]`

8. **The `dafoam-supervisor`'s `SUPERVISION_CHARTER.md` §3 check 4, personally**: §7's cap
   arithmetic and §9's falsifier arithmetic read **as arithmetic and not as a summary**.
   **Not delegable, and a lane's arithmetic is not a substitute for it.** §21.1 is on record that
   a supervisor certified a freeze claiming a falsifier was *"read AS ARITHMETIC"* having read one
   of its two limbs that way.
9. **The §3 check 1 diff read** of every instrument, **as a diff** — with §4.1's single-array
   requirement as an explicit rejection criterion.
10. **`LAUNCH_ENABLED` stays `0`.** Raising it is the enqueue act and **it is the supervisor's**
    (`A1WRT2` §13.1). **No lane raises it. No queue row is written by this draft.**
    *"That it would trip no gate is a reason to say it, not to do it."*

### `[OWED — TO THE SUPERVISOR, NOT TO THIS ITEM]`

11. **The `a1wr_cmd.sh:96-102` swallowed-rc defect** — a live defect in an instrument `A1WR`,
    `A1WRT` and every future member of this family inherit **by md5**. **Reported, not repaired
    here**: it is a frozen instrument of another item and a lane editing it would break two
    freezes.
12. **The `D13` environment gap** — `d13_opt_runScript.py` reads `D1_ENDPOINT_IN` at module scope
    while `D13`'s forward loop lists only the three `D13_`-prefixed names `[MEASURED,
    `A1WRT2_SEAM_RESULTS.md` §5.2]`. **The prefix changed and one read did not.** Whether it has
    ever fired in a real run is **not investigated**.
13. **`STATUS.queue.*` reads `launcher_rc=0` over a crashed arm.** Honestly labelled and still a
    surface a reader sweeping for failures will misread. **`A1WRT3`'s status writer should carry
    the producer rc in its own field**; whether the family-wide surface changes is the
    supervisor's call and is not taken here.
14. **The 10 unresolvable `genMesh.py` references** (`d12r_`/`d12x_`/`d12y_`/`d12e_`/`d12f_`/
    `d12_`/`w3s_stage_and_run.sh`) — the file ships inside the container image and the family
    sweep **makes no claim about it in either direction.**

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**

---

## 12. WHAT THIS DRAFT COULD NOT VERIFY, STATED PLAINLY

1. **No instrument of this item has been written or run.** Every gate, control and refusal in
   §§3–5 is **registered, not demonstrated**. The `[OWED]` list is the honest statement of that
   and the freeze may not close over it.
2. **The `-e` set `A1WRT3` will actually pass has not been constructed**, because
   `a1wrt3_run_arm.sh` does not exist. §4's `G-ENVSEAM` is registered against a set that will be
   built later; **the gate is what makes that safe, and the gate is also unwritten.**
3. **`A1WRT` U1's `4000/` was not re-verified field-by-field in this invocation.** Its contents
   are quoted from `A1WRT2_SUCCESSOR_DRAFT.md` §3 `[MEASURED there, this drafting invocation not
   repeated]`. **`G-COLDSTART-SEAM` is the instrument that must confirm it, on the staged copy,
   before `SEAM` runs.**
4. **Whether the container image's `python` still resolves after sourcing the loader was not
   re-measured tonight.** It was measured 2026-09-05 and clause **C0** exists precisely so that
   the answer is checked at the point of use rather than inherited from a four-day-old reading.
5. **No claim is made that §2's accounting is the last word on `cmd.sh`.** It is exhaustive over
   the file's **58 executable lines** by a stated partition; a reader who finds a 59th has found a
   defect in this section and it should be reported as one.

**SUBMISSIONS PARKED.**

---

## 13. AMENDMENT — 2026-09-06T02:14:32Z — **`G-NOGRAD` AS §9 WORDS IT REFUSES ITS OWN PINNED PRODUCER. THE GATE IS RE-WORDED TO PIN THE ENUMERATION, NOT THE ABSENCE.**

**PRE-FIRST-COMPUTE AMENDMENT under `CLAUDE.md` rule 2. The condition is stated and was CHECKED BY EXECUTION in this invocation:** `/home/ubuntu/certonomous-runs/A1WRT3` **ABSENT**; **0 core-min burned**; gates open. **After first compute it could not have been made at all.**

### 13.1 THE MEASUREMENT, AND THE LANE WAS RIGHT TO LEAVE IT REFUSING

§9 words `G-NOGRAD` as *"refuses if `compute_totals` appears even once in the staged producer."* **Implemented literally, it REFUSES the pinned producer.** I verified the three occurrences myself rather than on report:

| line | what it is | reachable under the registered task? |
|---|---|---|
| `:40` | **a COMMENT** listing the `-task` options — **it ships with the upstream DAFoam template** | **no — it is not code** |
| `:257` | `elif args.task == "compute_totals":` — a branch **guard** | **no — the branch is not entered** |
| `:260` | `totals = prob.compute_totals()` — the only call, **inside that branch** | **no** |

**The launcher's only producer invocation is `a1wrt3_cmd.sh:368`: `python "$A1WRT3_PRODUCER" -task sweep`.** So `args.task` is `sweep`, the `compute_totals` limb is **never entered**, and the call is **never made**. No gradient and no adjoint work occurs — which is the entire purpose of the gate.

> **A GATE THAT NO ADMISSIBLE PRODUCER CAN PASS IS NOT A GATE; IT IS A TYPO.** As worded, `G-NOGRAD` refuses **every stock DAFoam runScript in existence**, because the offending string sits in a comment upstream ships. It cannot separate a producer that computes gradients from one that cannot — **it refuses both** — and **a test that fails everything discriminates exactly as poorly as one that passes everything.** That is §21's `S1FDP` lesson arriving from the opposite direction: the two failures look nothing alike and are the same defect.

**THE LANE DID NOT AMEND IT TO MAKE ITS OWN ITEM PASS, AND THAT WAS CORRECT.** It implemented the registered wording, left it refusing, recorded the refusal as a measured fact with the three line numbers, and escalated. **The amendment is mine and only mine.**

### 13.2 THE AMENDMENT — PIN THE ENUMERATION AND THE REACHABILITY, NOT THE APPEARANCE

**This is `L-493` applied where it is already law in this family: *pin the count or the path, not the appearance*.** `G-NOGRAD` now refuses unless **all three** clauses hold, each mechanically checkable on md5-gated bytes:

> **(a) THE TASK IS PINNED.** The staged launcher contains **exactly one** producer invocation and it passes **`-task sweep`**. More than one invocation, or any other `-task` value, **REFUSES**.
>
> **(b) THE OCCURRENCES ARE ENUMERATED, NOT COUNTED.** `compute_totals` appears at **exactly** the three registered sites, each matching its registered content: the comment; the `elif args.task == "compute_totals":` guard; and the call **lexically inside that guard's suite**. **A FOURTH OCCURRENCE ANYWHERE REFUSES**, and so does a change to any of the three.
>
> **(c) THE CALL STAYS BEHIND THE GUARD.** If the call is ever **outside** the `compute_totals` branch, **REFUSE** — that is the condition the gate actually cares about, and it is now the one being tested.

**THIS IS NOT A LOOSENING, and I asked the question rather than asserting the answer.** The original admits **no** producer. The amendment admits **exactly one** — the pinned bytes, at the pinned sites, under the pinned task — and refuses every mutation, **including three the original could not even express**: a **second** invocation, a **different task**, and the call **escaping its guard**. **It is strictly more discriminating than what it replaces.** Its predicted value on the pinned producer is **already measured** — the three sites above — so §21's show-the-arithmetic requirement is met **at zero compute**.

**WHAT IS NOT CHANGED:** no band, cap, deadline, ceiling, label or prediction moves. `SEAM` 3.120 / cap 10.0, `TAIL` 224.775 / cap 675.0, ceiling 685.0, and `P-SEAMTIME3`'s four branches plus its refusing catch-all stand exactly as drafted. **`SEAM` first; `TAIL` only behind `SEAM`'s verdict; an `UNRESOLVED` `SEAM` is neither a permission nor a refusal.**

### 13.3 ⚠ A SECOND FINDING FROM THE SAME LANE, AND IT GENERALISES

`a1wrt3_grade.py` and `a1wrt3_selftest.py` each loaded `a1wrt3_instruments.py` **by path**, producing **two module objects carrying two distinct `Refusal` classes**, so `except I.Refusal` could not catch a refusal raised through the grader's copy. **Ten controls scored `NOT EXERCISED`.**

**The direction it failed in was the harmless one. Reverse it and it is not.** A control written the other way round — expecting a refusal it can never catch — scores **a PASS while catching nothing**: rule 3's exact failure mode arriving **through the import system** rather than through a reader. Repaired by taking the module through the grader (`I = G.INSTR`), **with the reason recorded at the import site**, because the next person to add an instrument will otherwise re-import it by path.

**SUBMISSIONS PARKED.**
