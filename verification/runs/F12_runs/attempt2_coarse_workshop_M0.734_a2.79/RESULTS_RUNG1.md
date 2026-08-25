# F12 attempt 2, rung 1 — coarse, workshop condition — `NOT A RESULT`

**Fired 2026-08-25T17:06:57Z. `rc = 134` (128 + 6 = SIGABRT), READ FROM DISK.**

## 0. The verdict

| item | outcome |
| --- | --- |
| admission gate A (mesh) | **`PASS`** — 51.12365363° against `<= 70`, skewness 0.9572299919 against `<= 4` |
| admission gate B (convergence) | **`GATE FAIL`** — the solver printed no convergence statement; it aborted |
| strict completion rule | **fails all six limbs** |
| Gates 1, 2, 3, 4 | **`PENDING`** — no values exist and none is quoted |
| **overall** | **`NOT A RESULT`** |
| cap | **NOT breached** — 0.30 core-min of a frozen 120 |

The strict completion rule is all-or-nothing, so no gate value is quoted from
this run. `grade.json` beside this file carries every limb.

| limb | pass | measured |
| --- | --- | --- |
| `rc == 0` | **no** | `rc = 134`, read back from `RC.txt`, never inferred |
| `End` line present | **no** | absent — the run aborted |
| last time == `endTime` | **no** | `148` of `6000` |
| fields present at `endTime` | **no** | no `6000/` directory; all of `T U p alphat k nut omega` ABSENT |
| `ExecutionTime` count == `endTime` | **no** | 147 of 6000 |
| age guard | **no** | no field exists at `endTime` to be newer than `0/T` |

## 1. WHAT FAILED, AND IT IS THE SAME FAILURE AS ATTEMPT 1

```
--> FOAM FATAL ERROR: (openfoam-2606)
Negative initial temperature T0: -2.384321367
    ... thermoI.H at line 57
```

**Side by side with attempt 1, same case, same physics, same schemes, same
`fvSolution`, same boundary conditions — and a mesh 19.5° better:**

| | attempt 1 | attempt 2 |
| --- | --- | --- |
| mesh max non-orthogonality | **70.646°** (`GATE FAIL`) | **51.124°** (`PASS`) |
| mesh **average** non-orthogonality | 30.213° | **17.375°** |
| faces over 70° | 892 | **0** |
| failure | `Negative initial temperature T0: -1.72234834` | `Negative initial temperature T0: -2.384321367` |
| at iteration | **180** | **148** |

**The mesh was replaced, admission gate A passes with 18° of margin, and the run
fails the same way 32 iterations EARLIER.** That is the finding this rung bought,
and it was bought for 0.30 core-min.

## 2. What the residuals were doing — evidence, not a diagnosis

Over the 148 iterations the run did not blow up globally. It stalled:

- `Ux` initial residual: 1.000 at iteration 1, then flat in a **0.021 – 0.049**
  band from iteration 21 to 141. No downward trend after the first 20.
- `e` (energy) initial residual: flat at **0.080 – 0.085** for the last 8
  iterations. The energy equation is not converging at all.
- `p`: **alternating** between ~0.21 and ~0.008 on successive iterations — a
  two-level oscillation, not a decay.

Then one cell's temperature goes negative and the thermo model aborts.

## 3. CRASH TRIAGE IS THE SUPERVISOR'S, AND THIS LANE DOES NOT DO IT

`SUPERVISION_CHARTER.md` §3 reserves crash triage to the supervisor personally.
This section states only what the measurements **eliminate** and what they
**do not**, and it draws no conclusion about cause.

**ELIMINATED BY MEASUREMENT: "the gate-A breach caused the divergence" is not
sufficient.** `F12_RESULTS.md` §6.3 recorded that reading as *"CONSISTENT BUT NOT
DEMONSTRATED"*. It now has a controlled test against it: the breach is gone —
max non-orthogonality down 19.5°, average down 42.5 %, zero faces over the limit
— and the same abort happens sooner. Whatever the cause is, removing the gate-A
breach did not remove it.

**NOT ELIMINATED, and explicitly left open for the supervisor:**

1. that mesh quality still contributes, through a channel gate A does not
   measure — the near-wall aspect ratio is 10³–10⁴ on both ladders and is
   *advisory* under the frozen gate, not gated;
2. that the initial field, the discretisation schemes, the under-relaxation or
   the `consistent` setting are implicated — the oscillating `p` residual and the
   stalled `e` residual are consistent with that and **demonstrate nothing**;
3. that the transonic condition itself needs a ramped or a first-order start,
   which is a physics-setup question and not a mesh question;
4. that the two runs share a cause that is upstream of both meshes.

**This lane changed no scheme, no relaxation factor and no boundary condition,
and recommends that nobody does so before the triage is read** — a mesh replaced
and a solver setting changed in the same step would make the next run
uninterpretable, which is exactly the position this rung has just escaped.

## 4. THE RATE THE RUNG EXISTED TO MEASURE — obtained despite the crash

The frozen §5 makes rung 1 the rate-calibration rung: *"That measured rate then
replaces both estimates before rungs 2-5 are considered."* **It did its job.**

| | s per cell-iteration | ratio to measured |
| --- | --- | --- |
| **MEASURED, this run** | **3.8975e-6** | 1.00 |
| Basis A (F2 `rhoSimpleFoam`) | 4.7015e-6 | 1.21 |
| Basis B (DPW8_V2 L3 `simpleFoam`) | 4.6010e-5 | **11.80** |

**Basis A is right to within 21 %. Basis B over-predicts by 11.8×.** The frozen §5
anticipated exactly this fork and said the medium rung would blow its cap if the
true rate were Basis B's; it is not.

**Re-costed off the measured rate**, 6,000 iterations at ranks 1:

| rung | cells | predicted core-min | frozen cap | headroom |
| --- | --- | --- | --- | --- |
| 1 coarse | 23,040 | **8.98** | 120 | 13.4× |
| 2 medium | 92,160 | **35.9** | 160 | 4.5× |
| 3 fine | 368,640 | **143.6** | 700 | 4.9× |

**Honest limit on that rate:** it is measured over **148 of 6,000 iterations** on
a run that **did not complete**, at `loadavg` 9.1–9.9 with three other teams'
solvers on the box. The extrapolation to 6,000 assumes a constant cost per
iteration, which **is not measured**. It is a measured rate; the extrapolation
from it is an estimate and is labelled one.

## 5. Two defects in this lane's own launcher — REPORTED, NOT REPAIRED

The launcher is now fired and its bytes are the bytes that ran. Editing it now
would be a post-compute change to a run's own instrument, so both are recorded
here for the supervisor rather than quietly fixed.

1. **The age-guard limb prints a misleading detail on a correct verdict.** With
   no `endTime` directory the limb correctly returns `False`, but its detail
   string reads `"all newer"` because the "no field is older" branch is evaluated
   over an empty list. **The verdict is right and the annotation is wrong**, which
   is the shape this lab already has on record as worse than no annotation.
   Recommended: report `"no fields exist at endTime"` when the list is empty.
2. **The rungs-2-to-5 interlock is keyed on `RC.txt` EXISTING, not on rung 1
   SUCCEEDING.** `RC.txt` now exists holding `134`, so the interlock has **opened
   on a crashed rung**. Recommended: require `rc == 0` and `complete == True`.
   **Nothing has been fired through the opened gate** and rungs 2-5 remain
   unfired.

## 6. Cost — calibration at completion

| | value |
| --- | --- |
| frozen cap (§5, rung 1) | **120 core-min** |
| **actual** | **0.3007 core-min** (18.0 s wall × 1 rank ÷ 60) |
| ratio actual / cap | **0.0025** |
| solver only | 13.29 s `ExecutionTime`, 14 s `ClockTime` |
| mesh phase in this rung | 1.35 s (`blockMesh` + `checkMesh` + dry-run `decomposePar`) |
| cap breached | **no** |
| waste, named separately | **0.00 core-min** — the spend bought a measured rate and a falsification |
| dollars | **$0.000257, DERIVED at $0.0513/core-h, reported-by-owner, NEVER measured** |
| loadavg at launch | **9.10 / 8.52 / 7.29**, and in every sample (9.93 / 8.72 / 7.38 at the last) |

**The ratio 0.0025 is not a misprediction finding.** The cap is a ceiling for a
6,000-iteration run; this run stopped at 148. The prediction that matters is the
rate in §4, and it is good to 21 % against Basis A.

## 7. Artifacts

`RC.txt` · `RESUME.json` · `SAMPLES.jsonl` · `grade.json` · `log.rhoSimpleFoam` ·
`log.blockMesh` · `log.checkMesh` · `log.decomposePar` · `PGID.txt` ·
`system/blockMeshDict` (the substituted attempt-2 dictionary, sha256
`d47f5b9c…`, replacing the frozen generator's `83e05f27…`).

Detachment recorded and verified: `pid = pgid = 2265888`, **session leader
`True`**, **`ppid = 1`**. Decomposition `hierarchical`, 4 subdomains,
`Cells min:5760 max:5760 median:5760 (100%)`, dry run, no processor directories.
Frozen evidence at launch: pre-registration blob
`462492a82b6cf848eaaff25661ded45e623e723f`, 7 frozen sentences found verbatim,
grading module blob `a18314f77160b7a58f443073850a44b4d8fada7d`, **26 grading
functions hashed individually and matched**.
