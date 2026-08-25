# D7 — optimisation arms `P1`, `P2` run. Arm `O` and both FD arms `BLOCKED`.

**Date:** 2026-08-25. **Lane:** dafoam `lab-lane`. **Pre-registration frozen at `337d4d84`;
instruments and both addenda committed at `0e229a0a` BEFORE the first container.**

| arm | verdict | why |
|---|---|---|
| `P1` | **PASS** | rc=0, decomposition determinism demonstrated, placement measured |
| `P2` | **GATE REACHED** | **cap-stop at the registered 60.0 core-min.** Not a failure, not a conditioning finding |
| `O` | **BLOCKED** | `D7-LAUNCHER-DEF-1` — `.d7_g8_pass` has a reader and no writer; and P2's colouring was never published to the root |
| `F-S`, `F-P` | **BLOCKED** | `D7-DEF-4` units defect (independent of the above) |

**No arm produced a drag number and none is claimed. D7's registered objective — lift-constrained
transonic drag minimisation — was NOT measured.** The optimisation driver never started.

## 1. `P1` — PASS

rc=0, wall **4 s**, **0.267 core-min** against a registered cap of 8.0, `memory=4g`,
`inspect(exit,oomkilled)=[0 false]`. Ledger row in
`/home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/ledger.txt`.

**Decomposition determinism (the G8 evidence), from `P1`'s own log:**

```
DECOMP_A {"processor0": 10635, "processor1": 10506, "processor2": 10538, "processor3": 10441}
DECOMP_B {"processor0": 10635, "processor1": 10506, "processor2": 10538, "processor3": 10441}
```

**Identical across all four subdomains** on two independent `decomposePar` runs of the same mesh
with `method scotch`, `numberOfSubdomains 4`. Artifacts `P1/d7_decomp_A.json` and
`P1/d7_decomp_B.json` are on disk and are what `d7_grade.py:570-571` reads.

**Placement, measured not inferred from the flag:** rank 0 → core 2, rank 1 → 3, rank 2 → 4,
rank 3 → 6 — **four distinct single cores, exactly the registered cpuset `2,3,4,6`.** Four
`P1/d7_placement_rank*.json` artifacts.

`delivered_cores_mean` is **`NOT_MEASURED`** for `P1` and is reported as such: the arm ran 4 s and
the host sampler took one sample. **`NOT_MEASURED` is not a pass**, and no placement-throughput
claim is made for this arm.

## 2. `P2` — GATE REACHED at the cap, with the adjoint HEALTHY at the cut

rc=**124** (`timeout`), wall **901 s**, **60.067 core-min** against the registered cap of **60.0**,
`cap_exceeded=YES`, `enforced_wall_s=900`.

**This is a cap-stop and it is labelled `GATE REACHED`, never `PASS`** — the pre-registration fixes
that mapping for a cost-derived cap.

**It is NOT an OOM and NOT a conditioning finding, and both matter:**

* `inspect(exit,oomkilled)=[1 false]` — **the kernel's own record: not OOM-killed.** Exit 1 is the
  `timeout` kill.
* `memavail_min_during=[17.125 n=60]` — **the host memory floor HELD**, 17.125 GiB minimum against
  the registered 16.0 GiB floor, over 60 samples. **The §7 memory-envelope check that `P2` exists
  to perform therefore PASSED**, and it is the one registered thing this arm did complete.
* `delivered_cores_mean=[3.9910 n=59 max_nr_throttled=3467]` — **3.991 of 4 cores delivered.** No
  core starvation. **G12's whole purpose is to rule out core contention before any
  adjoint-conditioning finding may be recorded, and it does: contention is excluded.**

**The adjoint was converging monotonically when the cap cut it**, from the arm's own log:

| KSP main iteration | residual norm |
|---|---|
| 0 | 1.839192419993e-01 |
| 400 | 3.173644035301e-02 |
| 600 | 3.022088538347e-03 |
| 700 | 1.575613201545e-03 |
| **800** | **4.841441157914e-04** |

**Three orders of magnitude down, monotone, still falling at the kill.** One
`PetscConvergedReason: 2` appears in the log. **That is NOT quoted as a verified gradient** —
`DAFOAM_CHARTER.md` §1 forbids exactly that inference, and no gradient from this arm enters any
record.

**Surviving artifacts — the run was not wasted:**

| artifact | path | size | written |
|---|---|---|---|
| baseline primal | `P2/d7_baseline.json` | 310 B | 21:37 |
| colouring cache | `P2/dRdWColoring_4.bin` | 3,076,152 B | 21:43 |

Baseline primal, measured on this mesh at the registered condition
(`U0 = 291.6`, `aoa0 = 3.06°`, `primalMinResTol = 1e-8`):
**`CD = 0.03311805865399452`**, **`CL = 0.2876130251655752`**, `A0 = 0.7575`.

## 3. Arm `O` — BLOCKED, and it never launched, so it cost ZERO core-minutes

Two independent obstructions, both recorded:

1. **`D7-LAUNCHER-DEF-1`** (`D7_LAUNCHER_DEF1_G8_TOKEN.md`) — `stage_coloring` reads
   `$BASE/.d7_g8_pass`, **nothing anywhere writes it**, so arm `O` aborts at exit 5
   unconditionally.
2. **The colouring was never published to the run root.** `stage_coloring` copies from
   `$BASE/dRdWColoring_4.bin`; the cache exists only at **`$BASE/P2/dRdWColoring_4.bin`**, because
   `P2` was cap-killed before its publish step. **The chain halted on `P2`'s rc=124 before arm `O`
   was reached, so the predicted exit-5 abort was NEVER OBSERVED — it is a reading of the frozen
   launcher, not a measurement, and is labelled so.**

## 4. A POLICY TENSION THIS RUN EXPOSED, for the supervisor's desk

**Sanaa lifted cost constraints on 2026-08-25**: no run stops to save compute, and registered caps
are **runaway guards reported upward**, not budgets.

**D7's launcher was frozen the same day and enforces its cap as a hard kill** —
`timeout $TMO sudo -n docker run ...`, with `TMO` derived from the registered core-minute cap.
**`P2` was therefore killed by a budget that lab policy no longer imposes, while its adjoint was
three orders down and still converging.**

**No rigor was traded to go faster and no cap was widened.** `CLAUDE.md` rule 6 bars this lane from
editing the frozen launcher, and retiring or widening a registered cap is reserved and is not a
lane's call. **The cap did exactly what it was registered to do.** What is now open — and is the
supervisor's, not this lane's — is whether a cap frozen before the lifting should still terminate
a healthy solve. **It is recorded rather than acted on.**

## 5. Cost — actual versus predicted (`CLAUDE.md` rule 12)

Calibration row **`C-89`** in `docs/COST_CALIBRATION.md`.

| arm | predicted | actual | ratio |
|---|---|---|---|
| `P1` | 1.5 | **0.267** | **0.178** |
| `P2` | 30.0 | **60.067** | **2.002** |
| **arms run** | **31.5** | **60.334** | **1.915** |
| `O`, `F-S`, `F-P` | 760.0 | **0.000** — never launched | — |

Dollars at the recorded $0.0513/core-h: **≈ $0.052 derived, NOT measured** — the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Gap attribution.** `P2`'s registered basis is *"13.60 (adjoint) + 2 × 3.38 (primals) + coloring
build"* — **the colouring build carries NO NUMBER.** It is the single largest cost in the arm:
setup, primals and colouring together consumed **682 s of the 901 s** wall
(≈ **45.5 core-min** of the 60.067), leaving the adjoint only 219 s (**≈ 14.6 core-min**) against
its predicted 13.60. **The adjoint prediction was approximately right; the unnumbered colouring
term is essentially the entire 2× overrun.** A cost basis with an unpriced term cannot be
calibrated, and this row is what that costs.

**WASTE, NAMED SEPARATELY AND NOT ABSORBED INTO THE RATIO: ≈ 14.6 core-min** — the incomplete
adjoint solve, killed mid-convergence, which produced nothing that enters a record. The remaining
≈ 45.5 core-min produced the colouring cache and the baseline primal, both on disk and both usable,
and is **not** waste. **CONTENTION: excluded by measurement** — 3.991 of 4 cores delivered.
No row exceeds the 3600-s stall rule; the longest wall is 901 s.

## 6. Toolchain rows — one bought, one NAMED AS UNBOUGHT

`DAFOAM_CHARTER.md` §6: a DAFoam verdict is two rows, shipped and patched, or it is not a verdict
about DAFoam.

| row | image | digest | status |
|---|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd…f07fc` — **verified by the launcher against the registered digest before each container** | **BOUGHT** for `P1`, `P2` |
| **PATCHED** | `dafoam-idwarp-rot:v1` | `sha256:2927768a16ac…f6d35` | **NOT BOUGHT** |

**The PATCHED row is unbought and its consequence is stated:** the patched row is registered
(§9a) to arm **`F-P`** only, and `F-P` is `BLOCKED` by `D7-DEF-4`. **Nothing in this record is a
verdict about DAFoam** in the charter's two-row sense — it is a report on two preparatory arms of
one toolchain row. `P1`'s measured `D7_IDWARP_SO_MD5 = f0fcb488e0e98156575cd19548e91663` is
recorded as the shipped-row IDWarp identity for whenever the second row is bought.

## 7. What this lane could NOT verify, named as unverified

* **D7's registered objective was not measured.** No drag number, no lift constraint, no
  optimisation history. The driver never started.
* **The predicted arm-`O` exit-5 abort was never observed** — the chain halted on `P2` first.
  §3's obstruction 1 is read from the frozen launcher, not measured.
* **`D7-DEF-4`'s pinned-witness prediction (`patchV[0]` → `29.16` rather than `291.6`) remains
  UNTESTED**, because it needs an `OptView.hst` and no optimisation ran. It stands as registered
  in `D7_DEF4_SCALER_BLOCKER.md` §3.
* **`d7_grade.py` was never run on real arms.** Every statement about it here is from its selftest
  (65 units) and from mutation testing (16 mutants, all exit 3), not from a graded run.
* **`delivered_cores_mean` for `P1` is `NOT_MEASURED`**, not passing.
