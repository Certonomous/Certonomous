# VMFL017-R3 — launcher self-smoke (PREREG_TEMPLATE Amendment 3 item 6)

**Zero graded compute. Scratch only. The graded Cd/Cl were NEVER read for grading.**
The launcher `run_vmfl017_r3.sh` was run end-to-end in `VMFL_SMOKE=1` mode against the
frozen HEAD (freeze commit `174d57fc`), into a scratch run root
(`.../scratchpad/r3_launcher_smoke`, refused unless under `scratchpad/`). This exercises
the launcher plumbing; it does not produce and does not grade a result.

## What the self-smoke verified (all green, launcher rc 0, 0.067 core-min)

- **Freeze check** — `PREREGISTRATION.md` (`5a0cdf8d`) and `grade_vmfl017_r3.py`
  (`b011df5b`) on disk hash equal to their HEAD blobs; the three `blockMeshDict.L1/L2/L3`
  on disk hash equal to their HEAD blobs (`a8bc3cd7` / `c0b0773c` / `f0840bd4`); mesh
  birth certificate present at HEAD (`516dd5e0`).
- **Registered-number assertions** — controlDict `endTime 0.05`, `deltaT 1e-9`,
  `maxCo 0.2`, `maxDeltaT 1e-5`, `writeControl adjustableRunTime` + `writeInterval 0.05`
  + `adjustTimeStep yes`, `forceCoeffs1 executeInterval 1e-4`, the `yPlus1` function
  object present, comparator `ENDTIME_PHYS == controlDict endTime`, and 500 samples over
  the run / 100 in the final 20% window ≥ `PLATEAU_MIN_SAMPLES 20`.
- **Controls** — comparator `--selftest` green (planted-zero, p-floor, and the y+ regime
  precondition all driven).
- **Solver path** — `blockMesh` + `checkMesh` + `rhoCentralFoam` ran (endTime shortened
  to `1e-5` s IN THE SCRATCH COPY ONLY); `forceCoeffs1` and `yPlus1` both wrote output
  (`postProcessing/forceCoeffs1/<t>/coefficient.dat`, `postProcessing/yPlus1/<t>/yPlus.dat`),
  so the comparator's reader paths (Cd col 1, Cl col 4; y+ min/max/avg) have data.
  Last smoke sample (NOT a result — 1e-5 s of physical time, forces NOT read for
  grading): Cd 2.02e-1, Cl 2.54e-1, wall yPlusMax 57.2 (in the log-law band).

## Underlying answer-blind physics smoke (recorded in PREREGISTRATION.md / birth certificate)

An earlier ephemeral answer-blind smoke on L1 measured the fix-until-runs evidence:
Δt ≈ 1.866e-7 s (~100× the row #32 low-Re step), L1 ≈ 132 core-min to reach endTime
(~128× cheaper), zero temperature blow-up over 8136 steps, wall y+ avg ≈ 43–51 / max ≈
53–66. That is the evidence that `rhoCentralFoam` CAN run this case; this launcher
self-smoke is the separate proof that the launcher itself is correct.

**VMFL017-R3 remains `NOT YET RUN`. The launch gate is HELD on Sanaa's decision (rule 9).**
