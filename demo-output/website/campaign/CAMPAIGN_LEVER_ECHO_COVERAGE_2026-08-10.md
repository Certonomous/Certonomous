# Campaign launch paths — lever-echo coverage

**Chief-routed from the Infra family's launcher consolidation (P-4.1 C+D,
`cae65e5c`), which correctly reported three campaign scripts as drift rather
than editing across a family boundary.** Zero solver cost. Commit `95c09ff7`.

---

## 1. Done — the three assigned, routed through the canonical emitter

| script | launches | echo now |
| --- | --- | --- |
| `W1_runs/run_rung.py` | `simpleFoam` (serial) and `mpirun -np N simpleFoam -parallel`, via `subprocess.Popen`; plus `decomposePar`/`reconstructPar` | **yes** on the two solver launches, **nothing** on the utilities |
| `W1_runs/build_case.py` | `plot3dToFoam`, `transformPoints` | **routed, emits nothing** — correctly, they are mesh utilities |
| `F5_runs/cylinder_ladder.py` | `pimpleFoam` (serial and parallel) via a direct `subprocess.run` — the one path in that module not already going through `tmr_verification._foam` | **yes** |

Nothing new was written: all three call
`lever_echo.echo_if_solver(args, run_dir)`.

**Inheriting L-45 rather than re-deriving it.** In each of the three, the
directory handed to `echo_if_solver` is **the same Python object handed to
`cwd=`**. The echoed directory and the executing directory cannot disagree — not
because the script promises to keep them in step, but because there is only one
of them. That is the property L-45 asks for, and it is checkable by reading two
adjacent lines.

**Inheriting the `-postProcess` exclusion rather than re-deriving it.** None of
the three implements its own test. Verified against the exact argument vectors
these scripts build:

| launch | `launches_a_solver` |
| --- | --- |
| `openfoam2606 mpirun -np 2 simpleFoam -parallel` | **True** |
| `openfoam2606 simpleFoam` | **True** |
| `openfoam2606 mpirun -np 2 pimpleFoam -parallel` | **True** |
| `decomposePar -force`, `reconstructPar -latestTime` | False |
| `plot3dToFoam -noBlank grid.p3dfmt`, `transformPoints -rotate-x -90` | False |
| **`openfoam2606 simpleFoam -postProcess -func yPlus`** | **False** |

Functional check on a real case directory: a solver vector produces a block that
opens with `BEGIN` and carries 10 hash-bound files; a utility vector on the same
directory produces 0 bytes. `sdk/tests/test_lever_echo.py`: **35 passed, 21
subtests passed.**

## 2. Found while sweeping — FIVE more campaign launch paths, a different shape, NOT touched

A sweep for launch paths across all of `demo-output/website/campaign/` found five
more that emit no echo. They were not in the assigned three and they are not the
same shape:

| script | solver launched |
| --- | --- |
| `F4_runs/run_cylinder_case.py` | `rhoCentralFoam` |
| `F3_runs/run_diamond_case.py` | `rhoCentralFoam` |
| `F3_runs/run_wedge_case.py` | `rhoCentralFoam` |
| `F3_runs/run_cone_case.py` | `rhoCentralFoam` |
| `DPW8_V2_runs/run_case.py` | `simpleFoam`, serial and `mpirun --oversubscribe -np N simpleFoam -parallel` |

All five share one helper shape:

```python
def sh(cmd, cwd, logfile=None):
    full = f"source {FOAM_BASHRC} >/dev/null 2>&1; {cmd}"
    p = subprocess.run(["bash", "-c", full], cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if logfile:
        with open(logfile, "wb") as f:
            f.write(p.stdout)
```

**Two structural obstacles, and per the chief's instruction I am saying so and
stopping rather than approximating:**

1. **The command is a shell STRING, not an argument vector.** The argv actually
   passed is `["bash", "-c", "source …; rhoCentralFoam"]`, on which
   `launches_a_solver` correctly returns **False** — there is no solver token in
   that vector. Making it work needs the predicate applied to a *split of the
   string*, and **splitting a shell string to decide what ran is keying on a
   spelling** — the same class of mistake as keying on `args[0]`, which is the
   defect this whole thread exists to fix. A string containing a pipe, a
   redirect, or a `&&` would be split wrong, and it would fail silently.
2. **The log is written after the process exits**, from captured stdout, so
   there is no open handle to echo into at t=0. Prepending the block to
   `p.stdout` afterwards would produce a log whose echo *looks* like it was
   written at launch but was assembled after the fact — **evidence manufactured
   at record-writing time, which is exactly what the charter's §9 echo exists to
   replace.**

Obstacle 1 is the disqualifying one. Obstacle 2 is soluble on its own but not
worth solving alone.

**Recommendation (not taken):** these five want the same treatment Infra gave the
detached wrapper — a launcher that takes an argument *vector*, not a shell
string, so the predicate has something real to read. That is launcher work in
Infra's consolidation, not a patch to five campaign scripts, and it should go to
them with this note. **Direction of the gap, per Infra's own classification:
these are false-NEGATIVES — they lose verifications, they cannot forge them — so
nothing already recorded from these five is wrong. This is coverage, not
correction.**

## 3. Found while verifying — the echo block is 98% of the solver log on any case with a `potentialFoam` pre-step

Not a correctness bug, and reported to the family that owns the module rather
than patched here.

Measured on this session's own B-52 runs, which are the **first parallel launches
ever to carry an echo** (the `args[0]` predicate meant they emitted nothing until
`199e9d17`):

| log | total | echo block | share |
| --- | --- | --- | --- |
| `study-b52-rung6b-uq/log.simpleFoam` | 25.2 MB | **24.6 MB** | **98%** |
| `study-b52-rung6d-uq/log.simpleFoam` | 24.7 MB | **24.1 MB** | **98%** |
| `F5c_runs/stage_a_A1/log.simpleFoam` (no `potentialFoam`) | 1.72 MB | 8.7 kB | 0.5% |

**Cause.** `_echo_targets` includes every file in `0/`. On a case whose workflow
runs `potentialFoam -writephi` before the solver, `0/U` and `0/phi` have been
overwritten with **nonuniform fields carrying one entry per cell** — 330 000
cells here — and the echo writes their full contents.

**This is the same root cause as a defect already on the record.** The B-52
replicate arm's pre-registered G4 equality check failed on exactly `0/U` and
`0/phi` (`B52_RUNG6_REPLICATE_RESULTS.md` §5), because those two files are
*computed*, not *specified*. One root: **the echo treats `0/` as the boundary-
condition dictionaries, but after any initialization step `0/` is a mixture of
specified conditions and computed fields.** Fixing that — echoing `0.orig/` where
it exists, or hashing rather than inlining a nonuniform `internalField` —
would fix the bloat and the false mismatch together.

**Not urgent:** these logs live outside the repo on a disk with 366 GB free, and
no claim is affected. **Worth fixing before an archived solver log is ever
committed uncompressed.**

## 4. What is not claimed

- No verification already recorded from any of these eight scripts changes. All
  the gaps are false-negatives.
- The three routed scripts have not been re-run; the routing is verified against
  the predicate and the module's test suite, not by a fresh solve. None of the
  three had a solve pending.
- Section 3 is a **sizing and semantics** observation about a module owned by the
  Infra family. Nothing in `sdk/chief_engineer/lever_echo.py` was edited here.
