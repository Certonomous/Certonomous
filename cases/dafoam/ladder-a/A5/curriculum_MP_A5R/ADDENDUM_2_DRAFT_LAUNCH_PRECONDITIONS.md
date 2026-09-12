# `MP_A5R` ADDENDUM 2 — **APPLIED 2026-09-12. STILL NOT LAUNCHED.**

**Drafted 2026-09-12 by a dafoam `lab-lane` on the dafoam-supervisor's brief, against
Sanaa's `docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md`. THIS ITEM IS STILL
UNLAUNCHED AND THIS LANE LAUNCHED NOTHING.** No run root matching
`/home/ubuntu/certonomous-runs/CURRICULUM-MP_A5R-*` exists.

**IN FORCE, AND CONFINED TO LAUNCH PRECONDITIONS.** Gates, thresholds, bands and labels are
untouched and unreadable from here. `dafoam-supervisor` read the accompanying diff **as a diff,
personally** (`SUPERVISION_CHARTER.md` §3 check 1, not delegable) on 2026-09-12, approved the four
hunks and **required one change — drop the `sudo` escalation** (§A2.7). The repairs are applied and
this document is frozen with them in one commit. **The item is STILL NOT LAUNCHED and check 4 on
this addendum is still owed.**

**Lines whose number changed above this section: 0.** No line of `PREREGISTRATION.md` is
edited by this draft; it is a separate file precisely so that assertion is trivially true.

---

## A2.1 THE BLOCKING DEFECT — `MP_A5R` LAUNCHES ITS CONTAINERS AS **ROOT**

`mpa5r_stage_and_run.sh:331` reads, verbatim:

```
  sudo -n docker run --name "$cname" --user 0:0 \
```

and `:336` carries `mpirun --allow-run-as-root`.

Sanaa's directive, item 6, verbatim: **"As ubuntu. Never root. Container jobs included."**

**As frozen, this item cannot legally launch.** This is not a style preference and it is not
a finding about the past: it is a precondition the launcher fails today. The census
(`docs/RESIZE_CENSUS_2026-09-12.md` §(a)) already attributes 7,276 root-owned files written
today to exactly this habit across five DAFoam curricula, `MP_A5`'s own R3 arms among them
(1,873 files, `docker inspect User=0:0`).

### A2.1.1 The repair is MEASURED, not proposed

The obvious spelling `-u 1000:1000` **does not work on this image by itself, and that was measured
on this box tonight, not assumed**:

| probe | result |
|---|---|
| `-u 1000:1000` … `ls -l /home/dafoamuser/dafoam/loadDAFoam.sh` | `Permission denied` |
| `-u 1000:1000` … `source /home/dafoamuser/dafoam/loadDAFoam.sh` | `Permission denied` |

Cause, read off the image itself: `id dafoamuser` → **uid 1002**, and `/home/dafoamuser` is
**`drwxr-x---  dafoamuser dafoamuser`** (mode 750, confirmed on `dafoam-idwarp-rot:v1` *and* on
`dafoam/opt-packages:latest`). uid 1000 has neither owner nor group rights and cannot *traverse* the
directory. This is the same failure `a3gc_genmesh.sh:47-58` recorded independently on 2026-09-11
(`rc = 127`, whole pipeline).

**THE SPELLING THAT WORKS, AND IT IS NOT THE ONE THIS LANE FIRST PROPOSED:**

```
-u 1000:1000 --group-add 1002 -e MPLCONFIGDIR=/tmp
```

| probe, run on this box 2026-09-12 | result |
|---|---|
| `id` inside the container | **`uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu),1002(dafoamuser)`** |
| `source /home/dafoamuser/dafoam/loadDAFoam.sh` | **`LOADED_OK`** |
| `command -v python` | `/home/dafoamuser/dafoam/packages/miniconda3/bin/python` |

**uid 1000 AND gid 1000 are both `ubuntu`.** 1002 is the image's `dafoamuser` group added as a
**supplementary** group, carried for one purpose only: traversing the 0750 home. Host artifacts land
`ubuntu:ubuntu`, exactly.

> **CORRECTION, RECORDED RATHER THAN QUIETLY SWAPPED.** This lane first measured and proposed
> `-u 1000:1002`, which also reaches `LOADED_OK` and `IMPORTS_OK`. It is **worse**, and the reason is
> not cosmetic: it makes the container's *primary* group 1002, so every host artifact is group-owned
> by a gid with no host user behind it. `--group-add` buys the same traversal without moving the
> primary group. **The better spelling was not this lane's discovery** — it is a peer lane's, and it
> is already running.

**CORROBORATION FROM A LIVE RUN, not from this lane's probe alone.** At the time of writing, a peer
lane's container `d6r2c_KR_REF_20260912T184838Z_79250` is up on **the same image**
(`dafoam-idwarp-rot:v1`), carrying `User=1000:1000` and `GroupAdd=["1002"]`, and its own first log
line reads `D6R2C_CONTAINER_UID: 1000 ubuntu GID: 1000 GROUPS: 1000 1002`. It sources the identical
`loadDAFoam.sh` and is solving. **That is a working precedent under load, which is stronger evidence
than a five-second probe, and it was found by looking rather than assumed.**

**One measured side effect, recorded rather than discovered later.** Matplotlib cannot create
`/home/dafoamuser/.config/matplotlib` under this uid and falls back to a temp cache with a warning.
Harmless, and silenced by `-e MPLCONFIGDIR=/tmp`; included in the diff so nobody later reads the
warning as a defect. `$HOME` itself is never written to, so no `-e HOME=` override is needed.

---

## A2.2 THE SECOND BLOCKING DEFECT — SANAA'S CHECKPOINT ITEM 2 IS **NOT SATISFIED** FOR ARM `O`

Her item 2, verbatim: **"Every optimization writes its history and design vector every
iteration and can hot-start from them."** Two clauses. This item meets neither cleanly.

### A2.2.1 "writes its history and design vector every iteration" — **BEST EFFORT, NOT GUARANTEED**

`mpa5r_run_script.py:443-471` adds `om.SqliteRecorder("mpa5r_hist.sql")` to the driver
inside a bare `try/except` that writes `rec["recorder_error"]` and **continues**. The
script's own header, `:55`, states it: *"the driver history recorder is BEST EFFORT and
reaches no gate (D9-5)."*

A history that is allowed to be absent is not a checkpoint. A recorder that fails silently at
driver construction leaves an optimisation that has been running for hours with **nothing to
resume from**, and nothing in the chain notices. Addendum 1 correctly diagnosed that the
recorder was what was *growing*; it did not make the recorder *mandatory*.

**Repair, APPLIED 2026-09-12 (hunk 4):** the `except` becomes a **refusal** — the arm
aborts before `run_driver()` rather than running unrecorded. This is a *stop-before-start*,
not a cap: it never signals, throttles or shortens anything that is running.

### A2.2.2 "can hot-start from them" — **THE CAPABILITY DOES NOT EXIST**

`grep -n 'hotStart\|hot_start\|storeHistory\|hist_file\|restart'` over `mpa5r_run_script.py`
returns **nothing**. `prob.driver = om.pyOptSparseDriver()` is configured with
`opt_settings` only. pyOptSparse's restart mechanism is its own `.hst` history — the driver
attributes `hist_file` and `hotstart_file` — and **an OpenMDAO `SqliteRecorder` is not that
file and cannot feed it.** `mpa5r_hist.sql` is a *record*, not a *restart*.

This is the identical defect the census found in `D6R2` (§"NEEDS RELAUNCH FROM SCRATCH …
`d6r2_opt_runScript.py` has no `hotStart`, no `storeHistory`, no restart branch"), which is
why twelve completed design iterations were lost at the reboot. **`MP_A5R` would lose the
same way, and at `endTime 5000` each evaluation costs ≈ 9.0 core-min (Addendum 1 §A1.6), so
33 evaluations is ≈ 297 core-min thrown away by one reboot.**

**Repair, APPLIED 2026-09-12 (hunk 4):** set `prob.driver.hist_file =
"mpa5r_opt.hst"` unconditionally, and `prob.driver.hotstart_file` to the same path **only
when the file already exists at start-up**, recording in the JSON record which of the two
branches was taken. Arm `O`'s stage directory is already a fresh timestamped tree, so a
hot-start is an explicit act, never an accident.

**What this repair does NOT claim.** That hot-start has been *demonstrated* on this problem.
It has not. Sanaa's item 5 requires **"one kill-and-resume test on one case per solver class,
once, before the fleet launches anything … the resumed result must match an unkilled
reference to the solver's tolerance."** `MP_A5R` arm `O` is the DAFoam-optimisation solver
class. **That test is owed and has not been run**, and this addendum does not pretend
otherwise. It is the cheapest place in the lab to run it: arm `B` is ≈ 5.7 core-min.

### A2.2.3 What IS already satisfied, so the supervisor is not asked to re-check it

* **Primal fields at 30-minute intervals (item 1).** Arms `B` and `E` are single `run_model`
  calls of ≈ 5.7 core-min at np = 1 — **under 30 minutes of wall by construction**, so
  `writeInterval = endTime = 5000` writes fields once, at the end, and loses nothing a
  30-minute rule would have saved. `MP_A5R-L1` (launcher `:296-301`) *forces* that equality
  and aborts if it does not land, because a non-endpoint interval writes **no fields at
  `endTime`** at all. For arm `O` the governing clause is item 2, not item 1: the resumable
  state of an optimiser is its history and design vector, not one primal's fields.
* **Detached, parented to init (item 9).** `:118-134` detaches once via `setsid`, captures
  `rc` **inside** the wrapper, and logs `PPID` at `:145`.
* **Rank count (item 8).** np = 1, `--cpus=1`, one explicit `CPUSET`. One solver rank.
* **Memory footprint declared (item 7).** 12g container ceiling; see §A2.3.
* **No cap (directive #17).** Unchanged; the launcher asserts no executable `timeout` grew back.

---

## A2.3 THE 12g FIGURE ON A 123 GiB BOX — **RE-EXAMINED AND DELIBERATELY UNCHANGED**

The brief asked whether `12g`, sized when the box had 30 GiB, is still right at 123 GiB.

**It is, and it is not changed.** `--memory` is a *containment ceiling on one process*, and
what that process needs — three `DASolver` instances, three IDWarp instances and three meshes
in one address space — is a property of the problem, not of the host. Addendum 1 took 12g
from **SO3's measured precedent**, the lab's own proven three-scenario multipoint on the same
solver, which ran to `EXIT: Optimal Solution Found.` at that figure. Nothing about the resize
touches that measurement. Raising it because there is now room would be sizing a guard to the
host instead of to the problem — the exact error Addendum 1 §A1.2 was written to correct, run
backwards.

**What the resize DOES change is the `MemAvailable ≥ 14 GiB` launch precondition of §A1.5,
and only its bite:**

| reading | value | source |
|---|---|---|
| at Addendum 1 (old box) | `MemAvailable` **2.77 GiB** → *WOULD REFUSE*, correctly | Addendum 1 §A1.5 |
| at this draft (new box) | `MemAvailable` **120 GiB** of 123 total, swap 15 GiB **0 used** | `free -g`, this box, 2026-09-12 |

The precondition now **passes with 106 GiB of headroom**. The threshold itself is not moved:
it was never a judgement about this box's size, and a standing condition that is rewritten
each time the hardware changes is not a standing condition.

`--memory-swap` is held **equal** to `--memory`, which disables container swap entirely —
independently required by Sanaa's item 18 ("swap use above zero for solver jobs is a defect").

---

## A2.4 A DEFECT IN THE FREEZE RECORD ITSELF, FOUND WHILE PREPARING THE QUEUE ENTRY

**`PREREGISTRATION.md` §0's md5 table is STALE and two of its three rows are now false.**
Rule 2 requires verifying that *"the frozen file **is** the file that ran by hashing it
against the committed blob"*. Run against §0's table today, that verification **fails**:

| file | §0 table says | on disk AND at `d72bee62a` | agree? |
|---|---|---|---|
| `mpa5r_grade.py` | `895f2146ab203e41b2767aa9a3ed248a` | `895f2146ab203e41b2767aa9a3ed248a` | **yes** |
| `mpa5r_run_script.py` | `37e31d71c9216249cee926ed12fe4e8f` | `36ec1afa94c28347419042f4aaad543b` | **NO** |
| `mpa5r_stage_and_run.sh` | `c87677b9e0f575dbfe005912cd4cc83d` | `a6a9761613e71e0c9c29b40f40d9bf6a` | **NO** |

Nothing is wrong with the *files*: Addendum 1 legitimately changed both (memory 3g→12g,
`includes ["*"]`→`[]`) and said so in prose. What it did not do is **record the new hashes**,
so the only machine-checkable statement of grading-path identity in the document now points
at blobs that no longer exist anywhere. The working tree is clean against `HEAD` for all
three files, so the current state is exactly `d72bee62a` and nothing is unaccounted for.

**Consequence for the queue entry, and it is the reason this was worth finding:** the
`prereg_commit` for `MP_A5R` is **`d72bee62aa07f89a48b35a8dae21f9cfda089f2c`**, the Addendum-1
commit — **not** `36a2a1040`, whose blobs for two of three instruments are superseded. An
entry pinned to `36a2a1040` would pass `queue_entry_check.py` (which checks only that the
commit holds `prereg_path`) and would nonetheless name a grading path that is not the one on
disk.

**Proposed repair:** a `| file | md5 |` table at the foot of each addendum that changes an
instrument, carrying the post-change hashes. Included as §A2.6 below for this addendum.

---

## A2.5 WHAT THIS DRAFT DOES NOT DECIDE, AND MAY NOT

* Whether the diff is applied. That is the supervisor's personal read (§3 check 1).
* Whether the item launches. Check 4 on this addendum is owed and is not discharged here.
* The kill-and-resume proof of §A2.2.2. **Owed, not run, and not assumed.**
* Any gate, threshold, band, weight, scenario or label. **None is touched.**
* Anything leaving this box. **SUBMISSIONS PARKED.**

## A2.6 INSTRUMENT HASHES — BEFORE AND AFTER, BOTH RECORDED

§A2.4 found that Addendum 1 changed two instruments and never recorded the new hashes, so §0's table
now points at blobs that exist nowhere. **This addendum does not repeat that**, and the table below is
the repair pattern §A2.4 proposed, applied to itself first.

| file | md5 **before** (= `d72bee62a`) | md5 **after** (this commit) |
|---|---|---|
| `mpa5r_grade.py` | `895f2146ab203e41b2767aa9a3ed248a` | `895f2146ab203e41b2767aa9a3ed248a` — **byte-identical, untouched** |
| `mpa5r_run_script.py` | `36ec1afa94c28347419042f4aaad543b` | **`24d6b505ac68a8b9d1af45698e8af92c`** |
| `mpa5r_stage_and_run.sh` | `a6a9761613e71e0c9c29b40f40d9bf6a` | **`5f36035beca8aaeab206d27583801f6d`** |

**The comparator is byte-identical to its original freeze.** No gate, threshold, band, weight,
scenario, prediction or label moved; every change is a launch precondition.

`mpa5r_queue_launch.sh`'s `PIN` is filled with `5f36035beca8aaeab206d27583801f6d`. If the launcher
changes again the wrapper refuses (exit 90) until somebody deliberately re-pins it.

---

## A2.7 — THE SUPERVISOR'S REQUIRED CHANGE: **THE `sudo` ESCALATION IS GONE**

Check 1 approved the four hunks and required one thing: **drop `sudo`.** It is dropped.

**Verified independently by this lane rather than taken on the supervisor's word**, because a
delegate's measurement is evidence and a supervisor's message is not this lane's authority:

| probe | result |
|---|---|
| `id ubuntu` | `uid=1000(ubuntu) … 27(sudo),**113(docker)**` |
| `stat /var/run/docker.sock` | **`660 root:docker`** |
| plain `docker ps` as this unprivileged process | **`rc=0`, and it listed the live peer container `d6r2c_KR_REF_…`** |

The third row is the one that matters: it is a **live positive control**. A `docker ps` that returned
nothing would have proved only that the reader was blind; it returned the container that is actually
running, so the unprivileged client is shown reaching the daemon and *seeing* something.

The container's user is set by `--user`, never by the client, so the escalation bought **zero
behavioural change**. **Shipping a root-execution repair with a needless privilege escalation on the
same line would undercut the repair.**

### A2.7.1 SCOPE — THIS IS FOUR CALLS, NOT THE TWO THE SUPERVISOR NAMED

Recorded here rather than done quietly, because approval of an item is approval of *its* cap and not
a new ceiling. The supervisor said the diff "still carries it twice". **The launcher had four**
(`docker ps` :179, `docker images` :184, `docker run` :332, `docker inspect` :343) and **all four are
now plain.** The reason for exceeding the letter of the instruction: removing two and leaving two in
the same file is incoherent, and the next reader copies the ones left. The change is strictly
privilege-**reducing** and measured behaviour-neutral, **reverting the two read-only calls is a
one-line change, and nothing has launched.** If the supervisor meant exactly two, say so and it goes
back.

The same escalation is dropped from this lane's own new A3GC instrument,
`a3gc_l1_plot3d_reentry.sh`, for the identical measured reason.

---

## A2.8 — A DEFECT THIS LANE PUT IN ITS OWN GUARD, FOUND BY DRIVING IT, AND WORTH A LESSON

`mpa5r_queue_launch.sh` refuses to launch a launcher that still runs as root. Its first spelling was
`grep -q -- '--user 0:0' "$LAUNCHER"`. **Driven against the correctly repaired launcher, it
REFUSED** — because the repaired file carries a comment reading ``WAS `… --user 0:0` ``.

**A guard that greps a whole file for the name of a defect fires on the record of that defect being
fixed.** The better the repair is documented, the more certainly the guard blocks it. **This happened
twice in one hour**: the same shape also fired on the `sudo` assertion's own explanatory comment
while the diff was being built.

Every guard in the wrapper now anchors on `^[[:space:]]*` and tests **what bash would run**, and each
was **driven in both directions** before being trusted:

| control | result |
|---|---|
| real repaired launcher | **passes** |
| launcher with `--user 0:0` planted back as an executable line | **refuses** |
| launcher with `sudo -n` planted back as an executable line | **refuses** |

A control that only ever shows green is as useless as one that only ever shows red.

*`MP_A5R` Addendum 2 v1.0, 2026-09-12. Applied. **NOT LAUNCHED.** Check 4 owed.*
