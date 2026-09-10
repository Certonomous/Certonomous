# M6CP1 L2 STAGE 4 — LAUNCH REFUSED. `BLOCKED`.

**Status: `BLOCKED`. Drafted by a cfd `lab-lane`, 2026-09-10, UNCOMMITTED. Not a grading record.**
**No gate, threshold, cap, band or label is touched by this file.** It exists because
`STAGE4_MANIFEST_L2.json` on disk records `"launched": true, "launch_pid": 1583918` and **that record
is false**, and a later reader must not believe it.

## 1. WHAT HAPPENED

At **2026-09-10 20:52:54Z**, under Addendum 3 (`[SANAA-DIRECT]`, commit `f1024091`, registration blob
`8967bf01`), `scripts/case_protocol_stage4_run.py` was invoked with `--go` on level **L2**, **ranks 1
(serial)**. Its five preflight checks all returned PASS and it printed:

    [STAGE4] EXIT: LAUNCHED | pid=1583918

**Nothing launched.** Measured at 20:54:32Z, 100 s later:

| evidence | reading |
|---|---|
| `L2/case/STATUS.stage4` | **does not exist** — the wrapper's FIRST write never happened |
| `L2/case/log.rhoPimpleFoam` | does not exist |
| `L2/case/RC.txt` | does not exist |
| time directories under `L2/case` | none |
| `L2/case/0/T` mtime | **2026-09-09 01:03:38Z — UNTOUCHED** |
| pid 1583918 | gone |
| `pgrep rhoPimpleFoam` | no match |

**The case is pristine and the age-guard datum is intact.** `0/T` is touched by the wrapper
immediately before the solver starts, and it was not touched, so no compute occurred and no field can
be mistaken for this run's. **Zero solver core-seconds were spent.**

## 2. THE CAUSE, WITH A PLANTED POSITIVE CONTROL

The generated wrapper `L2/case/launch_stage4.sh` (from the template at
`scripts/case_protocol_stage4_run.py:182` and `:189`) reads:

    set -u                                                    # line 8 of the wrapper
    ...
    source /usr/lib/openfoam/openfoam2606/etc/bashrc '' >/dev/null 2>&1

**Under `set -u`, sourcing the OpenFOAM bashrc is fatal.** Reproduced in a throwaway shell, touching
no case file:

- **TEST A** — the wrapper's exact two lines, `set -u` present: **rc = 1**, stderr
  `/usr/lib/openfoam/openfoam2606/etc/bashrc: line 184: WM_PROJECT_DIR: unbound variable`. The line
  after the source is **never reached**.
- **TEST B — THE PLANTED CONTROL, because a failure from a reader not shown able to see a success is
  not evidence (rule 3)** — identical, `set -u` removed: **rc = 0**, the line after the source IS
  reached, and `which rhoPimpleFoam` resolves to
  `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/rhoPimpleFoam`.

So the wrapper dies at its source line, **before** `cd`, **before** its first `echo` into
`STATUS.stage4`, **before** `touch 0/T`, and **before** the solver.

## 3. 🔴 WHY THE FAILURE WAS SILENT — AND IT IS THE SCRIPT'S OWN NAMED TRAP, ONE LEVEL UP

Two redirections erase the error completely: `>/dev/null 2>&1` on the source line inside the wrapper,
and `stdout=DEVNULL, stderr=DEVNULL` on the `subprocess.Popen` that starts it.

**And then the script infers success from a launching process's exit status — the exact move its own
docstring forbids.** `case_protocol_stage4_run.py:365-373` calls `Popen(["setsid","nohup",launcher])`,
sleeps 2 s, sets `manifest["launched"] = True`, and prints `EXIT: LAUNCHED`. **It never checks that
the wrapper is alive, never checks that `STATUS.stage4` was created, and never checks `RC.txt`.**
`Popen` succeeding means `setsid` was executed; it says nothing about the wrapper.

The file's header says: *"`setsid timeout cmd` exits 0 for EVERY outcome, including SIGFPE. So rc is
captured INSIDE the detached wrapper."* That discipline is correctly applied to the **solver** and is
**absent at the launcher's own level**. A wrapper that died in 30 ms and a solver running for an hour
produce **the same printed line and the same manifest**.

## 4. WHY STAGE 3 RAN AND STAGE 4 DOES NOT

`grep -n "set -u|set +u|source|bashrc"` over `scripts/case_protocol_stage3_smoke.py` returns **zero
hits**. Stage 3's launcher neither sets `-u` nor sources the bashrc in a wrapper, which is why the M0,
M1 and N1 smokes launched. **The defect is specific to stage 4, and stage 4 has therefore never
successfully launched anything in this lab** — every prior `STAGE4_MANIFEST_*.json` records
`"launched": false`, and the first `--go` ever passed produced a false `true`.

## 5. WHAT IS NOT DONE HERE, AND WHY

**The pinned launcher is NOT repaired by this lane.** `scripts/case_protocol_stage4_run.py` is pinned
in §10.1 of the registration at blob `425aeed988ae63843a851b9aa720a721a142c98c` (verified matching at
launch time), Amendment 1 records that the gates are **CLOSED**, and A1.5 already set this precedent
for the stage-3 reader defect: *a supervisor quietly repairing a pinned instrument after compute is
the exact move the freeze exists to prevent.* **`STAGE4_MANIFEST_L2.json` is also left exactly as the
instrument wrote it** — it is disclosed here, not edited, for the same reason.

**The minimal repair, stated so it is not re-derived, and NOT applied:** in the `LAUNCHER` template,
guard the source — `set +u` before line 189 and `set -u` after it — or move `set -u` below the source.
A second, independent repair is owed at `case_protocol_stage4_run.py:365-373`: **verify after
launching** that `STATUS.stage4` exists and the wrapper is alive before writing `"launched": true`,
so that a dead wrapper cannot report LAUNCHED.

**Referred to the cfd-supervisor.** Whether to amend, repair under `VERIFICATION_CHARTER` §2d.1, or
route the run another way is not this lane's call.

## 6. COST

**Zero solver core-seconds.** Two preflight builds and the shell diagnostics, 1 rank,
**≈ 0.05 core-min, $0.00004 DERIVED, NOT MEASURED** at $0.0513/core-h — the box cannot read its own
billing. Addendum 3's registered estimate of **27.1 core-min** for L2 is **unspent**.
