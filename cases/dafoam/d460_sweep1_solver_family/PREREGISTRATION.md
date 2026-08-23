# PRE-REGISTRATION — D460 sweep 1, solver family: does the ADF primal's NaN survive the removal of the multigrid stopping rule?

> **NOTHING HAS BEEN LAUNCHED. No solver, no container, no `docker run` of any kind was executed to
> produce this document.** It is written and committed **before first compute**
> (`CLAUDE.md` rule 2). Its entire evidentiary content is that the gate, the threshold, the band,
> the cap and the label below were fixed **before** the answer was known.
>
> **NOT FILED ANYWHERE.** Nothing here is sent, posted, uploaded or registered outside this box.
> Filing is Sanaa's decision alone (`CLAUDE.md` rule 7).

| | |
|---|---|
| **Item** | **D460** — `cases/dafoam/DEFECT_CANDIDATE_adf_primal_nonreproduction.md` (committed `757eccf0`), §7 sweep 1 |
| **Question** | Is D460's class **conditioning / diagnosability** or **AD correctness**? |
| **Written by** | DAFoam team, lab-lane, 2026-08-23, on the dafoam-supervisor's phase-1 brief |
| **Prerequisite closed** | Blocker 1, the full-protocol novelty sweep — `cases/dafoam/LIAISON_NOVELTY_SWEEP_adf_primal_nonreproduction.md` |
| **Authorisation state** | **PENDING.** This document does not authorise its own execution. Phase 2 runs only after the dafoam-supervisor has personally verified this commit and said go (`SUPERVISION_CHARTER.md` §3 — pre-registration committed before compute is a check that may not be delegated). |

---

## 1. Why this is not the sweep D460 §7 sketched

D460 §7 sweep 1 says: re-run ARM F with `p` switched from `GAMG` to **`PBiCGStab`/`DIC`**, and read
*"NaN persists"* as **AD correctness**.

**The full novelty sweep, run before this document and while nothing had been launched, found that
reading to be unavailable.** Two independent reasons, both from
`LIAISON_NOVELTY_SWEEP_adf_primal_nonreproduction.md` §5b:

1. **`DAFoam/OpenFOAM-AD` issue #2** (open since 2026-01-25, author `friedenhe`, the DAFoam lead
   maintainer, **[verbatim, REST]**): *"If PBiCGStab/DILU are used in fvSolution, both ADR and ADF
   flow solvers generate wrong results (flow variables blow up rapidly). … If you comment out
   PBiCGStab/DILU and use GAMG/GaussSeidel in fvSolution, the flow solution is correct."*
   **A PBiCGStab arm that NaNs would be fully explained by a separately reported, already-known
   upstream defect, and would say nothing about D460's mechanism.** §7's "NaN persists → AD
   correctness" row would be wrong.
2. **`DIC` is a symmetric-matrix preconditioner.** The transonic `DARhoSimpleCFoam` pressure
   equation carries `fvm::div(phid, p)` and is asymmetric — which is why upstream #2 pairs
   PBiCGStab with **DILU**. `PBiCGStab/DIC` is likely to be refused by OpenFOAM before it computes
   anything. *(This is an inference from the solver class, not a read of the deployed source; no
   container was opened. It is recorded as an inference and is not load-bearing — the design below
   avoids PBiCGStab entirely.)*

**The discriminating arm must therefore use a pressure solver that is neither `GAMG` nor
`PBiCGStab`/`DILU`.** `smoothSolver`/`GaussSeidel` is that solver, and it is the least-novel choice
available:

- it is **not multigrid**, so it has no value-dependent V-cycle count for an 8th-significant-figure
  AD difference to flip — which is precisely the mechanism D460 §3 infers;
- it is **not** the PBiCGStab/DILU pair upstream reports as broken, so the #2 confound is excluded
  **by construction**;
- it is **already this case's own setting for every other equation** — `system/fvSolution`'s
  `"(U|T|e|h|nuTilda|k|omega|epsilon)"` block is `smoothSolver`/`GaussSeidel`, `relTol 0.1`,
  `tolerance 0`, `nSweeps 1`. The registered edit copies those five lines onto `p`;
- it is **the fix the maintainer himself named** for a GAMG-in-an-AD-build failure
  (`DAFoam/OpenFOAM-v1812-AD` #2, 2020-12-07, **[verbatim, REST]**: *"It seems that this is related
  to the GAMG solver for pressure in system/fvSolution. Change it to smoothSolver fixes the
  problem."*).

**D460 is a committed, frozen record and is NOT edited by this lane** (`CLAUDE.md` rule 6). The
departure from its §7 is disclosed here and the corresponding dated addendum to D460 is the
supervisor's call.

## 2. A control arm is added, and why it is not optional

D460 §7 sketches **one** arm. One arm cannot answer the question. If the forward-AD arm stops
producing NaN under `smoothSolver`, that could mean the AD perturbation is no longer amplified —
or it could mean `smoothSolver` changed the trajectory so much that the comparison is a different
experiment. **The comparison of record must be forward-AD against plain at the SAME `fvSolution`.**

So: **two arms, one variable.** Both new, both cold, both np = 1.

| arm | build | `p` solver | role |
|---|---|---|---|
| **F-SM** | forward AD (`useAD` block present → `libDASolverADF.so`) | `smoothSolver`/`GaussSeidel` | the discriminator |
| **P-SM** | plain (`useAD` block absent) | `smoothSolver`/`GaussSeidel` | **the control** |

The two arms already on record supply the GAMG half of the 2×2 and are **not re-run**:

| arm | build | `p` solver | log on record |
|---|---|---|---|
| F-GAMG | forward AD | `GAMG` | `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/s1b.log` |
| P-GAMG | plain | `GAMG` | `/home/ubuntu/certonomous-runs/P2-a6-n16/patched.log` |

## 3. The registered edit — exactly one dictionary block, exactly five lines

`system/fvSolution`, in both new arms, the `"(p|p_rgh|G)"` block only. **From:**

```
        solver                         GAMG;
        smoother                       GaussSeidel;
        relTol                         0.1;
        tolerance                      0;
```

**to:**

```
        solver                         smoothSolver;
        smoother                       GaussSeidel;
        relTol                         0.1;
        tolerance                      0;
        nSweeps                        1;
```

Nothing else in `fvSolution` changes. `relaxationFactors`, `SIMPLE`, `potentialFlow` and the
`"(U|T|e|h|nuTilda|k|omega|epsilon)"` block are untouched.

**Declared side effect:** the `Phi` entry is `{ $p; relTol 0; tolerance 1e-6; }` and therefore
inherits the new solver. `Phi` is used only by potential-flow initialisation, which this case does
not run. Recorded as a known, accepted, inert consequence rather than discovered later.

### 3a. Arm construction, and the identity assertions that make it a one-variable comparison

Each arm is built from `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/base/` by the same
`gen_arm.py` that built `s1b`, with `s1b`'s parameters, then the §3 edit. **Three assertions run
before launch and a failure VOIDS the arm:**

- **A1** `diff <arm>/runScript.py /home/ubuntu/certonomous-runs/P3-a6-n16-ref/s1b/runScript.py`
  is **empty** for F-SM, and differs **only** by the `useAD` dictionary line and the Edit-4
  `add_dvgeo` block for P-SM.
- **A2** `diff <arm>/system/fvSolution` against `s1b/system/fvSolution` touches **only** the five
  lines of §3.
- **A3** `diff <arm>/system/controlDict` against `s1b/system/controlDict` is **empty**
  (`endTime 10`).

`printInterval` is set to **1** in **both** new arms. It is asserted numerically inert by D460 §6
trap 3 (`DASolver.C:124` calls `calcAllFunctions(printToScreen_)` every iteration and the flag gates
only the `Info` output) — and, unusually, **that assertion is itself tested by gate G0 below**: if
`printInterval 1` perturbed anything, G0 breaks. It is set because without it only iteration 1
prints, the divergence point is invisible, and the `ExecutionTime`-count completion clause cannot be
evaluated.

## 4. Toolchain identity — by hash, never by version string

| | |
|---|---|
| image | `dafoam-idwarp-rot:v1` — the image that produced D460's measurement |
| **IDWarp `.so` md5** | **`85f59e87253e0a71a813f64ca6e4c425`** — already asserted by `run_arm.sh`; `ASSERT_MD5 FAIL` VOIDS the arm |
| **`libDASolverADF.so` md5** | **`44538ed4ac157ecb5dbb6850cf4bde64`** — D460 §4, byte-identical to `dafoam/opt-packages:latest`, which is what licenses this as a statement about **shipped** DAFoam |
| DAFoam / OpenFOAM / PETSc | 5.0.0 / v2506 / 3.15.5 |

**Newly registered assertion A4:** the ADF library's md5 is asserted **inside the container at run
time** and must equal `44538ed4ac157ecb5dbb6850cf4bde64`; a mismatch, or a `find` that returns no
such file, **VOIDS the arm**. The in-container path is **not** stated here because establishing it
requires opening a container and this document was written without launching one — the assertion is
written as a `find`, and the fact that the path is unverified is recorded rather than guessed.

**A4 does not apply to ARM P-SM**, which does not load the ADF library. For P-SM the assertion is
the complement: `libDASolverADF` must **not** appear in the loaded-library set. *(If the run harness
cannot produce that set without extra tooling, A4-complement degrades to the `useAD`-absent check of
A1, and the degradation is recorded in RESULTS.md rather than passed over.)*

## 5. Frozen predictions

Registered **before** the run, with the lane's confidence stated rather than implied.

| # | prediction | registered value / band | confidence |
|---|---|---|---|
| **P1** | Gate **G0** holds: the quantities computed **before** the pressure solve at `Time = 1` are bit-identical to the same-build GAMG arm | exact string equality on `U0`, `U1`, `U2` `finalRes`, `he initRes`, `he finalRes` | **0.95** |
| **P2** | The **control** arm P-SM completes 10 iterations with no NaN | `NaN_P == False` | **0.90** |
| **P3** | **THE DISCRIMINATOR.** ARM F-SM does **not** reach NaN | `NaN_F == False` | **0.55** |
| **P4** | The iteration-1 continuity amplification collapses | `r = |cum_F| / |cum_P| ≤ 2.0`, against the GAMG pair's measured **`r = 10.029307311562496`** | **0.50** |
| **P5** | `p nIters` differs between F-SM and P-SM by fewer sweeps than the GAMG pair's 7 vs 5 | not gated — recorded only | — |

**P3's confidence is 0.55, not higher, and the reason is on record.** D460 §3's inference predicts
the NaN disappears. The novelty sweep found `DAFoam/OpenFOAM-AD` #2, in which the maintainer names
**GAMG/GaussSeidel as the configuration that works** and PBiCGStab/DILU as the one that breaks AD
builds — the **opposite polarity** to this lab's measurement. Something in that pair of facts is
not yet understood, and a lane that registered 0.9 here would be pretending otherwise.

## 6. Gates

**G0 — validity.** At `Time = 1`, for each new arm against its **own-build** GAMG reference:
`U0/U1/U2 finalRes`, `he initRes` and `he finalRes` must be **bit-identical**, compared as the
printed strings. Nothing upstream of the pressure solve in the first SIMPLE iteration depends on the
pressure solver, so any difference means the arm is not the registered one-variable comparison.
**G0 failure → `NOT A RESULT`.** Frozen reference values:

| quantity | F-GAMG (`s1b.log`) | P-GAMG (`patched.log`) |
|---|---|---|
| `U0 finalRes` | `0.07283048716260687` | `0.07283048716260687` |
| `U1 finalRes` | `0.003381492464613624` | `0.003381492464613624` |
| `U2 finalRes` | `0.07283327010584476` | `0.07283327010584476` |
| `he initRes` | `0.9999999999746546` | `0.9999999999746546` |
| `he finalRes` | `0.06128001402295498` | `0.06128002514528321` |
| *(not gated)* `cumulative` | `-0.05058272456310364` | `-0.00504349133910657` |

**G1 — control.** `NaN_P == False` and P-SM strict-complete. **Failure → `NOT A RESULT`**, plus the
separate finding that `smoothSolver` on `p` destabilises even the plain primal.

**G2 — discriminator.** `NaN_F`.

**G3 — band.** `r = |cum_F| / |cum_P|` at `Time = 1`, threshold **2.0**.

### 6a. Strict completion, per arm (`CLAUDE.md` rule 4)

All of it, or the arm is not done: `rc == 0`; an `End` line; **last `Time =` == `endTime` (10)**;
**`ExecutionTime` line count == 10**; the `10/` directory exists and carries
`T U p nut nuTilda alphat`; and **every field in `10/` is NEWER than the arm's own `0/T`** — the age
guard. Any clause failing → `NOT A RESULT`; the comparator **refuses rather than degrades**.

**Field list note:** this is the compressible aero family, so the registered fields are
`T U p nut nuTilda alphat`, **not** the thermal family's `T U p_rgh alphat nut k omega`. `k` and
`omega` do not exist in this case — the turbulence model is Spalart-Allmaras (`nuTilda`). Registering
the thermal list here would have produced a guaranteed, meaningless failure.

**A NaN run can still be strict-complete.** `s1b` was: `rc=0`, `End`, and NaN residual statistics.
Completion and the NaN observable are independent, and conflating them would destroy the experiment.

## 7. The decision rule — frozen, and evaluated in this order

| order | condition | **verdict** | **class** |
|---|---|---|---|
| 1 | any arm fails strict completion (§6a) | **`NOT A RESULT`** | undetermined |
| 2 | **G0** fails | **`NOT A RESULT`** | undetermined |
| 3 | **G1** fails (`NaN_P == True`) | **`NOT A RESULT`** | undetermined — the control did not hold |
| 4 | `NaN_F == True` | **`GATE FAIL`** | **AD CORRECTNESS** |
| 5 | `NaN_F == False` and `r ≤ 2.0` | **`PASS`** | **CONDITIONING / DIAGNOSABILITY** |
| 6 | `NaN_F == False` and `r > 2.0` | **`GATE REACHED`** | **CONDITIONING / DIAGNOSABILITY, PARTIAL** |

**`GATE FAIL` at row 4 means the pre-registered prediction was refuted. It is the MORE serious
scientific outcome, not a failed run** — it would mean the forward-AD primal reaches NaN under a
pressure solver that is neither multigrid nor the pair upstream already reports as broken, with the
plain build surviving the identical setting. This is stated here, before the run, so that neither
outcome can be dressed up afterwards.

**What each outcome buys D460**, per its §7 table:

- **Row 5/6 → conditioning:** the upstream ask is a documentation + warning change, and the report
  attaches to `OpenFOAM-AD` #2 as a second, opposite-polarity instance.
- **Row 4 → AD correctness:** a materially more serious report, and the `OpenFOAM-v1812-AD` open
  defects (`atan2` #14, and the "not differentiated properly" family) become relevant context.

## 8. Grading path — fixed at this commit

| | |
|---|---|
| comparator | `cases/dafoam/d460_sweep1_solver_family/analyse_sweep1.py` |
| **sha256** | **`239c1764c6b2ff8db5736c45f0f5f00f0debba0a4a93e745b080e1e641be7e94`** |
| invocation | `python3 analyse_sweep1.py <F-SM arm dir> <F-SM rc> <P-SM arm dir> <P-SM rc>` |

**Before grading, the file that runs is hashed against the committed blob** (`CLAUDE.md` rule 2).
If the hashes differ the grading is void.

The comparator **refuses (exit 2) rather than degrading** on: a missing log, a missing `Time = 1`
block, a missing registered quantity, an unparseable value, a reference log that has moved off its
frozen values, or any planted control that does not read back.

### 8a. Planted controls, run on every invocation (`CLAUDE.md` rule 3)

Three known perturbations are written to a copy of ARM F-SM's log **on disk** and re-read **from
disk** through the same parser used for grading. If any is invisible the comparator exits 2 **before
grading anything**.

| plant | what is planted | what must be read back |
|---|---|---|
| 1 | `he finalRes` × (1 + **1.234e-03**) | the reader reports a relative change of 1.234e-03 ± 5%, **and** the G0 string test now fails |
| 2 | a literal `nan` appended to the log | the NaN detector fires |
| 3 | `cumulative` × 3 | the reader reports 3.000000× |

**These have already been exercised against the logs on record**, before this commit, and all three
read back exactly (plant 1: `1.2340e-03`; plant 2: detector fired; plant 3: `3.000000x`). Both
polarities of the NaN detector are demonstrated on real files: `patched.log` (plain) reads
`_nan = False`, `s1b.log` (ADF) reads `_nan = True`. **A zero from a reader not shown able to see a
non-zero is not evidence, and this reader has been shown.**

One defect in the comparator was found and fixed by this exercise and is recorded because it
generalises: the NaN pattern was first written `\bn?an\b`, **which matches the English word "an"**
and would have reported NaN in every log ever written — a false positive that would have sent every
arm to row 4 of §7, the most serious verdict on the table.

## 9. Cost — `CLAUDE.md` rule 12

The unit is **core-minutes** (wall s × ranks ÷ 60). Both arms are np = 1, `--cpus=1`.

| | core-min | basis |
|---|---|---|
| ARM P-SM (predicted) | **1.5** | plain build, 10 iterations. Measured neighbour: `s1a` ran 1,000 healthy iterations in 946 s = 15.767 core-min → **0.95 s/iter**; 10 iterations ≈ 0.16 core-min, inflated ×~9 for `smoothSolver` needing more sweeps on `p` than GAMG |
| ARM F-SM (predicted) | **3.5** | if healthy, as P-SM; if NaN-contaminated, the measured `s1b` cost for the identical 10 iterations was **5.383 core-min** (NaN defeats GAMG's convergence test, D460 §10.7) |
| **predicted total** | **5.0** | matches D460 §7's ~5 core-min price for sweep 1 |
| **HARD CEILING** | **20.0** | **an overrun STOPS the run; it does not get a new budget** |
| per-arm timeout | **600 s** wall (= 10.0 core-min at np = 1) | `timeout 600` on the `docker run` |

**cost_basis:** c7a.4xlarge at **$0.0513/core-h**, **owner-stated 2026-08-21/22 and therefore
reported-by-owner, NOT measured** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

- predicted 5.0 core-min = 0.0833 core-h → **$0.0043**
- at the hard ceiling 20.0 core-min = 0.3333 core-h → **$0.0171**

Both are far under the $25 pre-authorisation. **A blanket authorisation is not a per-item read
(`CLAUDE.md` rule 9): this run is costed here, individually, and the ceiling above is this run's
ceiling and not a new floor for anything else.** No GPU is involved.

**Spend already incurred against this item: 0.000 core-min.** The novelty sweep was read-only web
and REST traffic; the comparator was exercised against logs already on disk. No container was
started.

## 10. Launch gate

| gate | registered threshold | reading at 2026-08-23T19:59:55Z |
|---|---|---|
| **MemAvailable** | **≥ 12 GiB** — a registered threshold, unchanged until Sanaa rules | **25.96 GiB — SATISFIED** |
| load1 | **recorded, not gated** | 8.56 (16 cores) |
| peak RSS expectation | ~0.64 GiB, from `s1b`'s measured `peak_rss_GiB=0.63623` | — |

**Load is recorded and not gated, deliberately.** `preflight.sh` defaults to `LOADCAP=8` and the
prior lane overrode it to `LOADCAP=60` in `queue.sh` — an effectively open gate. Inventing a third
threshold is not this lane's call; the memory gate is the binding one, and each arm takes
`--cpus=1` against the team's 8-concurrent-core cap.

**The reading above was taken with `awk` on `/proc/meminfo`. NOTHING WAS LAUNCHED.**

## 11. Run directories — asserted absent at this commit

`CLAUDE.md` rule 2: before first compute an amendment must name the run directory that does not
exist. Checked 2026-08-23T19:59:55Z:

```
ABSENT (good): /home/ubuntu/certonomous-runs/D460-sweep1-solver-family
```

The registered run root is **`/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/`**, with arms
`fsm/` and `psm/` and logs `fsm.log`, `psm.log`. **It does not exist at this commit**, and the guard
of §6a refuses any arm whose `0/` or a time directory already exists.

## 12. Amendment discipline

Before first compute, amendments are legal and must state the condition and how it was checked,
naming the run directory that does not exist (§11). **After the first `docker run` of either arm,
gates §6, thresholds §5, the ceiling §9 and the labels §7 are CLOSED.** Changes then land only as
dated addenda appended at the foot, which cannot alter a gate, threshold, cap or label. Originals
are struck, never rewritten.

## 13. What this sweep will NOT establish

1. **The scope.** One case, one solver, one mesh, np = 1. D460 §7 sweep 2 (case family, ~10
   core-min) is unrun and is not authorised here.
2. **Which build is *right*.** D460 §10.4 stands: the two builds differ; nothing measured here
   determines which side of the 8th-digit `he finalRes` difference is correct.
3. **That `OpenFOAM-AD` #2 and D460 share a mechanism.** This sweep excludes #2 as a *confound* for
   its own arm. It does not connect or disconnect the two defects.
4. **Anything about parallel behaviour.** Every arm np = 1, undecomposed (`DAFOAM_CHARTER.md` §5).
5. **A performance or memory claim.** A NaN-contaminated wall time is not an AD cost factor
   (D460 §10.7).
6. **The §8 `-1e10` false-convergence finding.** Untouched by this sweep; its novelty is clean
   (zero hits in every venue) and it needs no compute.

---

**Nothing in this file has been sent, filed, posted, uploaded or pushed. Nothing has been launched.**

---

## AMENDMENT 1 — 2026-08-23, BEFORE FIRST COMPUTE

**Condition, and how it was checked (`CLAUDE.md` rule 2).** This amendment is legal because **no
compute has occurred against this pre-registration**. The check: the registered run root
**`/home/ubuntu/certonomous-runs/D460-sweep1-solver-family` DOES NOT EXIST** — verified by
`ls -d` at 2026-08-23T20:2x UTC, which returned `No such file or directory`, and re-verified in the
same shell invocation as this amendment's commit. No arm directory, no log, no ledger and no
container has been created. **It amends an assertion, not a gate, a threshold, a cap or a label** —
§5's predictions, §6's gates, §7's decision rule and §9's ceiling are **unchanged**.

*Appended at the foot, not rewritten. Lines whose number changed above this section: 0.*

### 1a. §3a assertion A1 was wrong as written, and would have failed on a correct arm

**A1 said** that `diff <arm>/runScript.py s1b/runScript.py` must be **empty** for ARM F-SM.

**That is false, and the error is mine.** §3a also registers `printInterval 1` for both new arms,
and `s1b` was generated **without** it — `s1b/runScript.py` carries `primalMinResTol`,
`primalMinResTolDiff`, `useAD` and `primalMinIters` at lines 36–39 and no `printInterval` key at
all. A correctly built F-SM arm therefore differs from `s1b` by **exactly one inserted line**, and
A1 as written would have voided it.

**A1 is replaced by:**

- **A1-F (ARM F-SM):** `diff <run root>/fsm/runScript.py <P3>/s1b/runScript.py` contains
  **exactly one added line**, and that line is `    "printInterval": 1,`. Any other difference
  **VOIDS the arm.**
- **A1-P (ARM P-SM):** the same diff contains **exactly** that one added line, **plus** the removal
  of the `"useAD": {...}` dictionary line, **plus** the removal of the Edit-4 `add_dvgeo` block that
  `gen_arm.py` inserts only when `useAD_dv` is set. Any other difference **VOIDS the arm.**

A2 (fvSolution, five lines) and A3 (controlDict, empty) are **unchanged**.

### 1b. Arm ordering is registered: the CONTROL runs first

Not previously stated. **ARM P-SM is launched before ARM F-SM.** If the control fails §6a strict
completion or trips G1 (`NaN_P == True`), the run **stops there** and the discriminator is not
launched — §7 row 3 already makes the outcome `NOT A RESULT` regardless of what F-SM would do, so
spending on F-SM would buy nothing. This lowers the expected spend and cannot affect any verdict.

### 1c. Assertion A4's concrete form

§4 registered the `libDASolverADF.so` md5 assertion without a path, because establishing the path
requires opening a container and none was opened. Its concrete form is registered here as a
**search**, not a guess:

```
find / -name 'libDASolverADF.so' -type f 2>/dev/null | xargs -r md5sum
```

run inside the container in the same `bash -lc` as the solve, with its output captured to the arm
log. **ARM F-SM is VOID unless the log contains `44538ed4ac157ecb5dbb6850cf4bde64`.** If the `find`
returns no file at all, that is itself a finding and the arm is VOID, not silently passed.

### 1d. The launcher for this run root does not exist yet, and creating it is a pre-compute step

`run_arm.sh` and `preflight.sh` live in `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/` with `BASE`
hard-coded to that directory. Phase 2's first action is to copy them to the new run root with `BASE`
retargeted and assertion A4 (§1c) added. **This is zero compute and happens before any
`docker run`.** It is recorded here rather than discovered at launch, because a launcher edited
after first compute would be an edit to the grading path.

---

## AMENDMENT 2 — 2026-08-23, BEFORE FIRST COMPUTE

**Legality condition, stated and checked (CLAUDE.md rule 2):** no compute has occurred against
this pre-registration. The registered run root
**`/home/ubuntu/certonomous-runs/D460-sweep1-solver-family` DOES NOT EXIST** — checked by the
lane at 20:39Z, 20:43Z and 20:51Z, and re-checked by `test ! -d` **in the same shell invocation
as this amendment's commit**; the commit aborts if the directory exists. No arm directory, log,
ledger or container exists for this item. The lane that found the defect built its trial arm in
**scratch, outside the registered run root, precisely to keep this condition intact**, and was
right to.

**This amendment alters an assertion, not a gate, threshold, cap or label.** §5, §6, §7 and §9
stand exactly as committed.

### 2a. A1-P as amended by Amendment 1 voids every correctly built control arm

Found by the lane's scratch trial and **verified independently by the supervisor, read as code,
before this amendment was written**: `gen_arm.py` line 112,

```python
NEW = NEW.replace("__DV__", useAD_dv).replace("__IDX__", useAD_idx)
```

is **unconditional**, while the `useAD` dictionary line and the Edit-4 `add_dvgeo` block are
gated on `useAD_dv`. The injected template's `fwdad` task branch (line 74 of `gen_arm.py`)
therefore carries a **second, ungated** function of `useAD_dv`: its `print` literals. A plain
arm gets `("", "-9999", v)` where `s1b/runScript.py:312` has `("patchV", "1", v)`. So every
correctly built P-SM arm shows a **fourth** difference — one changed line — and Amendment 1's
"Any other difference **VOIDS the arm**" fires on a correct arm. Same defect class as the A1
error Amendment 1 repaired.

The changed line is a `print` of string literals inside `elif args.task == "fwdad"`, downstream
of `prob.run_model()`; ARM P-SM never invokes the `fwdad` task, and the literals appear only in
a log label. **It is numerically inert.**

### 2b. A1-P is replaced by

- **A1-P (ARM P-SM):** `diff <run root>/psm/runScript.py <P3>/s1b/runScript.py` contains
  **exactly**: (1) the one added line `    "printInterval": 1,`; (2) the removal of the
  `"useAD": {...}` dictionary line; (3) the removal of the Edit-4 `add_dvgeo` block that
  `gen_arm.py` inserts only when `useAD_dv` is set; (4) the **single changed line** in the
  `fwdad` task branch whose printed literals are `("", "-9999", v)` where `s1b` has
  `("patchV", "1", v)`. Any other difference **VOIDS the arm.**

A1-F, A2, A3 and A4 are **unchanged**.

*End of Amendment 2. Nothing above this section was edited.*

---

## ADDENDUM 3 — 2026-08-23, AFTER FIRST COMPUTE, BEFORE ANY GRADED SOLVE

**Harness-repair record. This addendum alters no gate, threshold, cap, label, arm definition,
assertion or grader.** §5, §6, §6a, §7, §8 and §9 stand exactly as committed; A1-F, A1-P (as
amended by Amendment 2), A2, A3 and A4 stand exactly as committed. It records an incident, a
triage, a supervisor ruling and a repair to the **launcher** created by AMENDMENT 1 §1d.

*Appended at the foot, not rewritten. **Lines whose number changed above this section: 0.***

### 3a. The legality marker has CHANGED, irreversibly, and this section is where that is recorded

**The condition used by AMENDMENT 1 and AMENDMENT 2 — "the registered run root
`/home/ubuntu/certonomous-runs/D460-sweep1-solver-family` DOES NOT EXIST" — is SPENT.** The run
root was created at 2026-08-23T20:57Z as the AMENDMENT 1 §1d pre-compute step, and a `docker run`
followed. **That condition can never be cited again for this item and no later amendment may use
it.**

**Its replacement, and the evidence for it:** *no graded solve has occurred.* Concretely, from the
attempt-1 artifacts preserved under §3e:

| evidence | reading |
|---|---|
| `ledger.txt` row | `ARM=psm TASK=probe rc=134 wall_s=1 ranks=1 core_min=0.017 peak_rss_GiB=unmeasured` |
| `Time = ` blocks in `psm.log` | **0** |
| `ExecutionTime` lines in `psm.log` | **0** |
| `End` lines in `psm.log` | **0** |
| numeric time directories in `psm/` | **none** — only the staged `0/`, still carrying the copied `base/` mtimes of 2026-08-21 16:38 |
| `ASSERT_MD5` | **FAIL — ARM VOID** |
| `ASSERT_A4_ADF_MD5` | **ABSENT**; `A4_FIND_LINES: 0` |

**ARM P-SM attempt 1 is VOID by its own registered assertions.** Not one registered observable
exists: no residual, no continuity value, no NaN reading, no field. Nothing gradable was produced,
so nothing on the grading path can have been chosen to fit an answer — which is the entire
evidentiary content §2 says a freeze carries.

### 3b. **`ASSERT_MD5 FAIL` IS NOT AN IDWARP IDENTITY FINDING. No reader may cite it as one.**

The attempt-1 ledger row reads `ASSERT_MD5 FAIL -- ARM VOID`. **That is a SYMPTOM of the control-flow
defect of §3c and nothing else.** The IDWARP md5 is asserted by grepping the arm log for the string
`IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425`. In attempt 1 the `python -c` that *prints* that
string was inside the backgrounded and-or list and **never executed**, so the string was absent from
the log and the grep failed. **The library was never read, never hashed, and never compared.**

`85f59e87253e0a71a813f64ca6e4c425` is neither confirmed nor contradicted by attempt 1. Any later
record that cites this row as evidence about IDWARP identity is misreading it, and this paragraph
exists so that misreading is not available.

### 3c. The incident and its triage

**Attempt 1, ARM P-SM, launched 2026-08-23T20:57Z**, control-first per AMENDMENT 1 §1b, after all
pre-launch assertions passed: A1-P showed **exactly** the four differences AMENDMENT 2 §2b permits
and no others; A2 touched only §3's five lines; A3 was empty; the §6a guard found no time directory;
`useAD` was absent. Preflight passed at 20:57:55Z with `MemAvailableGiB=13` against the registered
`≥ 12` floor; `load1=14.50`, recorded and not gated per §10.

**The container exited in 1 s with `rc=134`**, the log carrying only OpenMPI's
`mpirun was unable to find the specified executable file … Executable: python`.

**Root cause, read as code.** The launcher's in-container body was written as an `&&` chain ending
in a backgrounded watcher subshell:

```
source loadDAFoam.sh && python -c '<idwarp assert>' && … && ( watcher ) & WPID=$!; mpirun … python runScript.py
```

**`&` binds looser than `&&`.** The trailing `&` therefore terminated the **entire and-or list**,
backgrounding the source of `loadDAFoam.sh` together with both asserts, and `mpirun` ran in the
foreground shell where DAFoam's environment had never been established. The defect was introduced by
the §1d splice itself: the P3 original is a flat foreground `&&` chain with no watcher and no `&`,
and the copied header's claim *"Nothing else is changed from the P3 script"* was true of the
commands and **false of the control flow**.

**Demonstrated outside any container, on the shell alone**, so the diagnosis is measured rather than
inferred. Running the attempt-1 shape with a variable set inside the chain and read after it: the
chain saw `FOO=setbychain`, the foreground shell saw `FOO=unset` — proving the chain executed in a
separate, backgrounded shell whose environment `mpirun` could not see. Running the repaired shape,
the environment step completed **before** `mpirun` and only the watcher ran concurrently.

This is a defect in a harness file written by the lane minutes earlier. It is not a defect in DAFoam,
in the image, in the case, or anywhere in this frozen document.

### 3d. The ruling, quoted verbatim from the dafoam-supervisor

> RULING — the repair PROCEEDS under this registration. Legal basis: §1d classifies the launcher as
> grading path; VERIFICATION_CHARTER §2d.1 governs grading-path changes and its boundary is the
> first GRADED solve — none has occurred (a fortiori the repair is legal there under its four
> conditions, all met: demonstrable error, not preference; established by instruments that grade
> nothing — the shell-semantics demonstration and mpirun's own error line; disclosed; pre-repair
> state preserved). The two readings compose rather than conflict. Recorded as a dated ADDENDUM to
> PREREGISTRATION.md — not RESULTS-only.

The supervisor states the triage was verified personally before ruling: the launcher body read as
code, the `psm.log` fingerprint matched, the ledger row re-read, the `Time =` blocks counted at zero,
and the text diffed against the P3 original.

**§2d.1's condition (2) is the load-bearing one and is satisfied in its strongest form.** The error
was established by **mpirun's own executable resolution** and by **shell semantics** — two
instruments that grade nothing, know no hypothesis, and cannot prefer a verdict direction. Condition
(4) is satisfied vacuously and completely: there are no pre-repair values to record beside published
ones, because attempt 1 produced no value.

**The harness-repair exception for this item is now SPENT.** Per the supervisor's binding terms, any
further failure of any kind ends the item with the verdict it has earned; the lane reports and does
not repair again.

### 3e. Attempt 1 is preserved, not overwritten, and its cost is charged as waste

The attempt-1 arm directory, log and launch output are moved to **`attempt1/`** inside the run root
and are not deleted. `ledger.txt` remains **append-only**, so the attempt-1 row stays visible above
every later row.

**`0.017 core-min` is charged to this item and is named WASTE**, not absorbed (`CLAUDE.md` rule 12).
At $0.0513/core-h that is **$0.0000145, derived, on an owner-stated rate** — the box cannot read its
own billing. The §9 hard ceiling of **20.0 core-min is unchanged** and this spend counts against it.

### 3f. The repair, in full

Confined to the in-container body. **Source, the idwarp assert and the A4 `find` execute in the
FOREGROUND, and `mpirun` is not reached if any of them fails** (explicit `exit 91`, `exit 92`,
`exit 93`); **only the watcher subshell is backgrounded.** No command, path, image, assertion,
timeout, cpu or memory limit changes. `bash -n` passes on the repaired file. The diff below is the
authority for what changed.

```diff
--- a/run_arm.sh   (attempt 1, as launched 2026-08-23T20:57Z)
+++ b/run_arm.sh   (attempt 2, repaired under this addendum)
@@ -9,7 +9,13 @@
 #     /proc/<pid>/maps of the live runScript.py process, so the "libDASolverADF
 #     is absent" reading is taken from a reader that ARM F-SM proves can see a
 #     presence (CLAUDE.md rule 3 -- F-SM is the positive control for P-SM's zero)
-# Nothing else is changed from the P3 script.
+# REPAIRED per PREREGISTRATION.md ADDENDUM 3 (attempt 1, rc=134): the in-container
+# body is NEWLINE-SEPARATED, not "&&"-chained. In the attempt-1 text the trailing
+# "&" on the watcher subshell terminated the ENTIRE and-or list, so the source of
+# loadDAFoam.sh and both asserts were backgrounded together and mpirun ran with no
+# environment. Here source, the idwarp assert and the A4 find run in the
+# FOREGROUND and mpirun is not reached if any of them fails; only the watcher
+# subshell is backgrounded. Nothing else is changed.
 set -uo pipefail
 BASE=/home/ubuntu/certonomous-runs/D460-sweep1-solver-family
 ARM="$1"; TASK="$2"; TMO="${3:-600}"
@@ -20,17 +26,22 @@
 NAME="d460_$ARM"
 T0=$(date -u +%s)
 timeout "$TMO" sudo -n docker run --rm --name "$NAME" --cpus=1 --memory=12g -v "$BASE":/mnt -w "/mnt/$ARM" \
-    "$IMG" bash -lc \
-    "source /home/dafoamuser/dafoam/loadDAFoam.sh \
-     && python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"IDWARP_IMPORTED_FROM:\",p); print(\"IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' \
-     && echo 'A4_FIND_BEGIN' && find / -name 'libDASolverADF.so' -type f 2>/dev/null | xargs -r md5sum && echo 'A4_FIND_END' \
-     && ( U=/tmp/dasolver_seen.txt; : > \$U; for i in \$(seq 1 900); do for p in /proc/[0-9]*; do grep -qa runScript.py \$p/cmdline 2>/dev/null || continue; grep -ao '/[^ ]*libDASolver[A-Za-z0-9]*\.so' \$p/maps 2>/dev/null >> \$U; done; sleep 2; done ) & \
-     WPID=\$!; \
-     mpirun --allow-run-as-root -np 1 -x PYTHONPATH python runScript.py -task $TASK; RC=\$?; \
-     kill \$WPID 2>/dev/null; \
-     echo 'LOADED_DASOLVER_SET_BEGIN'; sort -u /tmp/dasolver_seen.txt 2>/dev/null | sed 's/^/  /'; \
-     if [ -s /tmp/dasolver_seen.txt ]; then :; else echo '  (EMPTY -- the maps watcher recorded no DASolver mapping)'; fi; \
-     echo 'LOADED_DASOLVER_SET_END'; exit \$RC" \
+    "$IMG" bash -lc "
+source /home/dafoamuser/dafoam/loadDAFoam.sh || exit 91
+python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"IDWARP_IMPORTED_FROM:\",p); print(\"IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' || exit 92
+echo 'A4_FIND_BEGIN'
+find / -name 'libDASolverADF.so' -type f 2>/dev/null | xargs -r md5sum || exit 93
+echo 'A4_FIND_END'
+( U=/tmp/dasolver_seen.txt; : > \$U; for i in \$(seq 1 900); do for p in /proc/[0-9]*; do grep -qa runScript.py \$p/cmdline 2>/dev/null || continue; grep -ao '/[^ ]*libDASolver[A-Za-z0-9]*\.so' \$p/maps 2>/dev/null >> \$U; done; sleep 2; done ) &
+WPID=\$!
+mpirun --allow-run-as-root -np 1 -x PYTHONPATH python runScript.py -task $TASK
+RC=\$?
+kill \$WPID 2>/dev/null
+echo 'LOADED_DASOLVER_SET_BEGIN'
+sort -u /tmp/dasolver_seen.txt 2>/dev/null | sed 's/^/  /'
+if [ -s /tmp/dasolver_seen.txt ]; then :; else echo '  (EMPTY -- the maps watcher recorded no DASolver mapping)'; fi
+echo 'LOADED_DASOLVER_SET_END'
+exit \$RC" \
     > "$BASE/${ARM}.log" 2>&1 &
 DPID=$!
 # RECORD-ONLY RSS monitor. It never kills anything.
```

### 3g. What this addendum does NOT do

1. **It does not touch the grading path of §8.** `analyse_sweep1.py` is untouched; its sha256 is
   still `239c1764c6b2ff8db5736c45f0f5f00f0debba0a4a93e745b080e1e641be7e94`, matching §8 and the
   committed blob, and it will be re-hashed against the committed blob before it grades.
2. **It does not relax any gate.** G0's frozen reference strings, G1, G2, G3's threshold of 2.0,
   §6a's strict-completion clauses and §7's decision rule are exactly as committed.
3. **It does not make attempt 1 gradable.** Attempt 1 is `NOT A RESULT` in the plainest sense: it
   produced no result at all.
4. **It does not re-open the "run root does not exist" condition.** That condition is spent (§3a).
5. **It does not license a second repair.** §3d records the exception as spent for this item.

*End of Addendum 3. Nothing above this section was edited.*
