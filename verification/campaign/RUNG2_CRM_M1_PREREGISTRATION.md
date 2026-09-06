# RUNG 2 pre-registration — NASA CRM / DPW5 — `R2-M1`, the SUCCESSOR to `R2-M0`: the LAST UNTESTED REMEDY, a MECHANISM INSTRUMENT THAT WAS REHEARSED BEFORE IT WAS REGISTERED, and a 2×2 THAT DE-CONFOUNDS M0's A2

**Team: cfd. Case id `RUNG2-CRM-M1`. v1.1, drafted 2026-09-06 by a `lab-lane` for the cfd supervisor.
v1.1 carries Amendment 1 (§13), landed PRE-COMPUTE, altering NO gate, threshold, cap or label.**

> # ⚠ DRAFT — NOT AUTHORISED TO LAUNCH. CHECK 4 HAS NOT BEEN PERFORMED.
>
> **NOTHING LAUNCHES AGAINST THIS FILE. NO SOLVER COMPUTE HAS BEEN RUN UNDER IT.**
>
> The rule-2 freeze — pre-registration **committed** before compute — is the cfd supervisor's
> **non-delegable personal check** (`SUPERVISION_CHARTER.md` §3). The drafting lane does not take it.
>
> **No queue row has been placed and this lane placed none.** `verification/queue/` is a live drop
> path and writing into it arms a launch. Placement is the chief's, under its own captured grant.
>
> **Solver core-minutes spent by this lane: 0.0219, all of it the §5 writer rehearsal on a 125-cell
> box.** No DPW5 grid was solved, no MPI job was started, no run root was created.
>
> **Registered run root `verification/runs/RUNG2_CRM_runs/M1_mechanism_and_warmstart/` verified
> ABSENT under a live planted control (§1.3).**
>
> **THIS PROBE PRODUCES NO CRM CLAIM.** No force, drag, lift, moment or coefficient is read out of
> it. Rung 2 (a)'s drag gate stays `BLOCKED` on the three independent grounds its own registration
> names, binding ground **(iii), the absent refinement triple** (cfd supervisor's §15 ruling,
> commit `006aff45`). Nothing in this file touches that.

---

## 0. WHAT THIS IS

`R2-M0` was graded on 2026-09-06 (`log.grade`, record `ad3cb727`). It produced:

- **`R2-G0` `PASS`** — the abort reproduces. A0 `rc=136`, thermo library in its own stack.
- **`R2-G1` `GATE FAIL`** — no arm reached `Time = 50`.
- **`R2-G2` `NOT A RESULT`** — no mechanism could be named.
- **`R2-G3` `PASS`** — 8/8 reader controls.
- **A3 `BLOCKED`** — the warm-start arm never launched.

M0's own grading record is careful about what that does **not** mean: *"one remedy was NEVER TESTED,
so 'all four exhausted' is not what happened"* (`ad3cb727`). `R2-M1` exists to close exactly that,
and to close it with an instrument that was **shown to work before it was paid for**.

M1 carries three things and nothing else:

| | what | why it is here |
|---|---|---|
| **(a)** | the warm-start arm, with its **actual** failure repaired | the single live question M0 leaves open |
| **(b)** | a mechanism instrument **registered and rehearsed per arm** | M0's mechanism gate returned silence; a second unmeasurable mechanism gate is the same money for the same silence |
| **(c)** | an estimate whose **mass cannot be zeroed by the admission gate** | M0's estimate put 93.6 % of itself in a branch that was not taken |

---

## 1. CENSUS AND THE PLANT

### 1.1 What exists

| artifact | class | path | state |
|---|---|---|---|
| `R2-M0` registration | pre-registration | `verification/campaign/RUNG2_CRM_M0_PREREGISTRATION.md` | v1.1, frozen, graded against |
| `R2-M0` run root, five arms | run output | `verification/runs/RUNG2_CRM_runs/M0_compressible_admission/` | graded, `GATE FAIL` on `R2-G1` |
| `R2-M0` frozen comparator | grading path | `cases/committee-grids/grade_r2_m0.py` | blob `b724dc85f62fd8eb26505107446295e3f2e87d4a` at `HEAD`. **FROZEN — not edited by this registration (rule 6)** |
| `R2-M0` driver | code | `cases/committee-grids/run_r2_m0.sh` | the source of the §4 defect |
| `R2-M0` calibration row | cost record | `docs/COST_CALIBRATION.md` row `C-20260906T161200.871248Z-5aae017a` | the basis of §6 |
| DPW5 `L1.T` hex committee grid | case input | `/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid/` | 638,976 cells, sha-pinned in `cases/committee-grids/COMMITTEE_GRID_NUMERICS.md` §1 |
| the archived converged **incompressible** solution, `Time = 200` | case input (warm start) | `/home/ubuntu/certonomous-runs/dpw5-committee-probe/run_hex_base_incompressible_a2.11/` | 14 processor dirs; the source B1 maps from |
| **`R2-M1` writer rehearsal, per arm, with controls** | **validation record** | `cases/committee-grids/R2_M1_WRITER_REHEARSAL.tsv` | **7/7 arms PASS, 7/7 controls DISCRIMINATE, 0.0079 core-min.** §5 |
| **`R2-M1` grading path** | **comparator** | `cases/committee-grids/grade_r2_m1.py` | **exists in git before this freeze — see §8. 12/12 controls fire.** |

### 1.2 What does not exist

| absent artifact | class |
|---|---|
| any `verification/runs/RUNG2_CRM_runs/M1*` directory | run output |
| any queue row naming `M1` in `verification/queue/cfd{,/launched,/held}` | queue entry |
| any `RUNG2-CRM-M1` row in `docs/COST_CALIBRATION.md` or `IBL_COMPUTE_ENVELOPE_LEDGER.md` | cost record |
| **any measured value for `decomposePar -fields` on this grid** | cost anchor — see §6, it is ESTIMATED and labelled so |

### 1.3 THE PLANT — the absences above are measured, not assumed

Rule 3. Each reader was shown able to see a hit **at the exact path it searches**, then shown the
absence again after the probe was removed. Run 2026-09-06, one shell invocation each:

| reader (exact searched path) | before | probe planted | after removal | |
|---|---|---|---|---|
| `ls -d verification/runs/RUNG2_CRM_runs/M1_mechanism_and_warmstart` | **0** | **1** | **0** | **DISCRIMINATES** |
| `ls verification/campaign/RUNG2_CRM_M1_PREREGISTRATION.md` (pre-drafting) | **0** | **1** | **0** | **DISCRIMINATES** |
| `ls verification/queue/cfd{,/launched,/held} \| grep -ci M1` | **0** | **1** | **0** | **DISCRIMINATES** |

A fourth, broader reader (`grep -ci 'M1\|RUNG2\|CRM'`) reads **1 → 2 → 1**. It also discriminates;
its standing **1** is `verification/queue/cfd/launched/RUNG2-CRM-M0.json`, **M0's row, not an M1
row**, and it is named here rather than left as an unexplained non-zero.

---

## 2. (a) THE WARM START — WHAT ACTUALLY FAILED, ESTABLISHED BEFORE ANYTHING WAS REPAIRED

M0 recorded `A3 warm start: FAILED TO MAP. Arm BLOCKED, not run, no conclusion drawn.`
(`M0_compressible_admission/A3/WARMSTART.txt`). **That sentence is wrong about its own cause, and a
successor that repairs "the map" would be repairing something that was never broken.**

### 2.1 The map did not fail. It succeeded.

`M0_compressible_admission/A3/log.reconstructPar` records, in full:

> ```
> Exec   : reconstructPar -case .../A3/_warmstart_src -time 200 -fields (U k omega)
> Time = 200
> Reconstructing FV fields
>     Reconstructing volScalarFields
>         k
>         omega
>     Reconstructing volVectorFields
>         U
> End
> ```

`rc = 0` (`COST.tsv` row `A3_reconstruct 0 2 1 2`), an `End` line, all three registered fields
reconstructed at the registered time. And the driver's own `cp` landed them:
`A3/0/U` **15,656,211 bytes**, `A3/0/k` **5,326,147**, `A3/0/omega` **5,326,211**, all mtime
2026-09-06 09:09 — the reconstructed fields are **on disk in the arm right now**.

So the decomposition did not mismatch, the time directory was not absent, and the field set was not
wrong. **All three of the obvious guesses are excluded by the artifact.**

### 2.2 What failed is the POST-MAP GUARD, and it failed on I/O mode, not on physics

`run_r2_m0.sh:306-316` runs a patch-transcription check between the map and the re-decomposition:

```python
s = open(sys.argv[1]).read()
for patch in ("wall", "symmetry", "farfield"):
    if patch not in s:
        raise SystemExit("warm-start U lost patch %s" % patch)
```

`open(...).read()` opens in **text** mode. `A3/system/controlDict:18` is `writeFormat binary`, so the
reconstructed `U` is a binary OpenFOAM field. Driven verbatim against the exact file it read:

> ```
> UnicodeDecodeError: 'utf-8' codec can't decode byte 0xfd in position 900: invalid start byte
> GUARD_EXIT=1
> ```

`if [ $? -eq 0 ]` is therefore false, `decomposePar -fields` never runs — **there is no
`A3/log.decomposePar` and no `A3_decompose_fields` row in `COST.tsv`, which is the independent
confirmation that the branch was never entered** — `A3_OK` stays `0`, and the driver writes "FAILED
TO MAP" for a map that had already succeeded.

**And the guard's own test was satisfied all along.** Read binary-safe, `A3/0/U` contains all three
patch names. The guard never got far enough to find that out.

### 2.3 The repair, and it has no degrees of freedom

Read bytes; test bytes. **The test itself is unchanged** — this is the property that makes a
crash repair safe to accept from the party that found it (`VERIFICATION_CHARTER.md` §2av, the
2026-09-06 ruling: for a crash repair the anti-gaming question is *how many ways could it be
fixed*). There is exactly one:

```python
data = open(sys.argv[1], 'rb').read()
missing = [p for p in (b"wall", b"symmetry", b"farfield") if p not in data]
if missing:
    raise SystemExit("warm-start U lost patch %s" % missing[0].decode())
```

**Driven in both directions on the real 15.6 MB file, 2026-09-06:**

| direction | input | result |
|---|---|---|
| accept | the real `A3/0/U` — where M0's guard died | `guard OK: all three patches present, 15656211 bytes read binary-safe`, rc **0** |
| **refuse** | the same file with `farfield` scrubbed to `XXXXXXXX` | `warm-start U lost patch farfield`, rc **1** |

**The repaired guard is shown able to refuse. A guard only ever seen to pass is not a guard.**

### 2.4 WHAT IS STILL NOT KNOWN, AND IT IS REGISTERED AS UNKNOWN

`decomposePar -fields -time 0` on this grid **has never run on this box.** M0's pipeline stopped one
step short of it. So:

- its **cost** is **ESTIMATED, NOT MEASURED** (§6), and labelled so in the estimate table;
- its **success** is **NOT ASSUMED**. `R2M1-G3` is written so that if the re-decomposition fails,
  B1 is recorded **`BLOCKED`** and the admission gate `R2M1-G4` is **`BLOCKED`, NOT `GATE FAIL`** —
  because a remedy that could not be exercised has still not been tested, and calling that a
  failure of the remedy would be exactly the error M0's grading record refused to make.
- `R2M1-G3` does **not** accept "the command exited 0" as proof the field arrived. It requires the
  driver to have written a `B1/WARMSTART_MAPPED` marker **after** the repaired guard passed **and**
  the re-decomposition returned 0, and it checks `B1`'s arm state independently.

---

## 3. (b) THE MECHANISM INSTRUMENT — WHY M0's WENT SILENT, AND WHAT IS DIFFERENT

### 3.1 M0's writer was not broken. M0's GATE was unsatisfiable.

This matters because the obvious lesson ("the function object didn't write") is the wrong one and
would produce the wrong repair.

`fieldMinMax` **did** write. `M0/A0/postProcessing/r2m0MinMax/0/fieldMinMax.dat` carries a complete
record — `T`, `mag(U)`, `p`, `rho`, each with min, max and location — at `Time = 1`. So do A1's and
A4's. The arms completed **exactly one** time step each, and the writer produced **exactly one**
record. That is a writer working correctly.

`R2-M0` §6's gate required *"a per-iteration `min/max` line for `T`, `p` and `rho` **in each arm's
log** ... up to its last completed iteration"*. Two independent things then defeated it:

1. **A2 completed ZERO time steps.** It aborted inside `Time = 1`, before the first end-of-step
   write, so it has **no last completed iteration** and no `postProcessing` directory at all. The
   gate was **unsatisfiable for that arm by construction.**
2. The gate read the **solver log**, and `fieldMinMax` with `log true` writes its block to stdout
   only at the same end-of-step moment — so an arm that dies mid-step has nothing there either.

### 3.2 AND THE DEEPER PROBLEM: an end-of-step writer can never record the step that kills the run

This is the structural point, and it is why M1 does not simply re-register M0's function object with
a different threshold. `fieldMinMax` fires at the **end** of a completed time step. The failure
happens **inside** a step. The last record therefore describes the last **survived** state, which is
pre-divergence **by construction**. Tightening the threshold cannot fix that.

M1 therefore registers **three** instruments, two of which are new in kind:

| | instrument | when it writes | what it can see |
|---|---|---|---|
| **W1** | `fieldMinMax` on `(T p rho U)`, `writeControl timeStep`, `writeInterval 1` | end of each **completed** step | the last survived state. **Cannot see the killing step.** |
| **W2** | the solver's own intra-step lines — `pressureControl: p min`, `time step continuity errors` | **during** a step | survives the abort. Free; no configuration. |
| **W3** | **arm B2: the same case with the FPE trap OFF** (`FOAM_SIGFPE=false`), `endTime 3` | — | the killing step **completes**, so W1 and W2 record the diverged state **instead of it being guessed from a stack trace** |

**W3 is the instrument M0 did not have**, and it is the one that can actually name a mechanism: it
converts an abort into a measurement.

### 3.3 THE REHEARSAL — per arm, before the freeze, at negligible cost

`VERIFICATION_CHARTER.md` §2ap: prove the writer writes before the run pays for it.
Script `cases/committee-grids/rehearse_r2_m1_writers.sh`; record
`cases/committee-grids/R2_M1_WRITER_REHEARSAL.tsv`.

Each of the seven M1 arms was assembled on a **125-cell box** — not the DPW5 grid, and the record
says so on its own second line — using **that arm's own registered dictionaries**
(`thermophysicalProperties` with its energy form, `fvSolution` with its `transonic` switch,
`fvOptions` with its bounds, and the `controlDict` function-object block **character-for-character
as §7 registers it**), then run for 3 steps and read back.

**Per arm, not once** — because M0's A2 produced no `postProcessing` directory while A0, A1 and A4
did, on the same driver and the same function-object block, so a rehearsal on one arm's
configuration is not evidence about another's.

| arm | rc | steps completed | W1 records `T`/`p`/`rho`/`mag(U)` | W2 | W1 | W2 |
|---|---|---|---|---|---|---|
| B0 | 0 | 3 | 3 / 3 / 3 / 3 | 3 | **PASS** | **PASS** |
| B1 | 0 | 3 | 3 / 3 / 3 / 3 | 3 | **PASS** | **PASS** |
| B2 | 0 | 3 | 3 / 3 / 3 / 3 | 3 | **PASS** | **PASS** |
| B3 | 0 | 3 | 3 / 3 / 3 / 3 | 3 | **PASS** | **PASS** |
| B4 | 0 | 3 | 3 / 3 / 3 / 3 | 3 | **PASS** | **PASS** |
| B5 | 0 | 3 | 3 / 3 / 3 / 3 | 3 | **PASS** | **PASS** |
| B6 | 0 | 3 | 3 / 3 / 3 / 3 | 3 | **PASS** | **PASS** |

**One record per completed step, per field, on every arm, on both instruments.**

**THE PLANTED CONTROL ON THE READER (rule 3), per arm, both directions, using the SAME reader
functions the gate uses:**

| arm | W1 live → hidden → restored | W2 live → scrubbed → restored | |
|---|---|---|---|
| B0 … B6 (all seven) | **3 → 0 → 3** | **3 → 0 → 3** | **DISCRIMINATES** |

The reader is shown able to see a per-iteration record **and** to report its absence, on every arm,
in both directions. **Measured cost of the rehearsal: 0.007850 core-min** (471 wall ms, 1 rank);
**0.0219 core-min gross** across all three passes, including the two that failed on defects in the
rehearsal harness itself (§11).

### 3.4 What the rehearsal does NOT establish, stated plainly

It is a **writer** test on a 125-cell box. It says **nothing** about whether these arms survive on
the DPW5 grid, and nothing about the physics. An arm that writes here can still abort there — that
is what the graded run is for. It establishes one thing only, and that thing is the one M0 lacked:
**the registered writers write, per arm, one record per completed step, and the reader that will
grade them can tell a record from its absence.**

### 3.5 ⚠ AN OBSERVATION THAT WAS ON DISK THE WHOLE TIME — recorded here, and it is NOT a mechanism claim

M0's `R2-G2` is `NOT A RESULT` and **nothing has licensed a cause.** But one measured fact about
what the solver saw before it died has been sitting in the run root since 2026-09-06 09:09, unread,
and it belongs in the file where the mechanism arms are specified rather than being rediscovered
later:

> `verification/runs/RUNG2_CRM_runs/M0_compressible_admission/A0/log.solve:145`
> ```
> pressureControl: p min -252762.6
> ```

**That is a negative ABSOLUTE pressure — −252,762.6 Pa — reported by the solver during A0's first
time step**, one step before the abort. Beside it, from the same arm's `Time = 1` record
(`A0/postProcessing/r2m0MinMax/0/fieldMinMax.dat`):

| quantity | value at `Time = 1` | for comparison |
|---|---|---|
| `min(rho)` | **0.096767402** | the arm's own registered `rhoMin` is **0.1** — the field is **outside its own bound** |
| `max(mag(U))` | **690.81616** m s⁻¹ | registered `magUInf` is **295** |
| `min(p)` (end of step, after limiting) | 8613.056 Pa | — |
| `max(p)` | 642624.31 Pa | — |

**WHAT THIS IS AND IS NOT.** It is a **measurement of the state the solver was in before it died**,
with its path and line. It is **not** a cause, **not** a mechanism, and **not** a verdict — `R2-G2`
returned `NOT A RESULT` and this registration does not reopen it. It is recorded here for three
reasons, all of them about the design rather than the physics: it is the empirical basis of §5.6's
named prediction; it is why `rho` and `p` are in the registered writer's field list; and it
demonstrates the §3.2 point concretely — **this was the last SURVIVED state, and the state that
actually killed the run was never written by anything**. Naming a mechanism remains `R2M1-G2`'s
job, and `R2M1-G2` rests on B2.

---

## 4. THE ARM SET

Seven arms, all on the DPW5 `L1.T` hex committee grid, 14 ranks, assembled from the same archived
compressible seed M0 used.

| arm | energy | `transonic` | bounds | FPE trap | `endTime` | what it is for |
|---|---|---|---|---|---|---|
| **B0** | `sensibleInternalEnergy` | no | none | **on** | 120 (seed's own) | **reproduction control.** Anchors M1's instrument set to a known outcome. |
| **B1** | `sensibleInternalEnergy` | no | yes | on | **50** | **(a) THE WARM START**, repaired. Carries the only admission gate. |
| **B2** | `sensibleInternalEnergy` | no | none | **OFF** | **3** | **(b) THE MECHANISM ARM (W3).** The killing step completes and is recorded. |
| **B5** | `sensibleInternalEnergy` | no | yes | on | 3 | 2×2 cell: neither factor |
| **B3** | **`sensibleEnthalpy`** | no | yes | on | 3 | 2×2 cell: **energy form alone** |
| **B4** | `sensibleInternalEnergy` | **yes** | yes | on | 3 | 2×2 cell: **transonic alone** |
| **B6** | **`sensibleEnthalpy`** | **yes** | yes | on | 3 | 2×2 cell: both — reproduces M0's A2 |

"bounds" = M0's registered `limitTemperature` fvOption (100–1000 K) plus `pMin 1000; pMax 1e7` in
the `SIMPLE` dict, applied by the same code M0 used.

**Why B3–B6 carry `endTime 3` and not 50.** Their question is **where** the failure occurs, not
whether the arm survives 50 steps. M0 already answered the survival question for this configuration
family with `GATE FAIL`. Giving diagnostic arms an admission-length `endTime` would move the
estimate's mass back into a survival branch — which is exactly the §6 defect this registration is
built to avoid. **Only B1 is an admission arm.**

---

## 5. WHY THE 2×2 EXISTS — AND WHAT IT MAY NOT CLAIM

### 5.1 The observation

M0's A2 died differently from the rest, and nothing in M0 asked why. Measured from the four logs:

| arm | last `Time` | steps completed | ranks trapping | trap site in the stack |
|---|---|---|---|---|
| A0 | 2 | 1 | 8 | `libfluidThermophysicalModels.so` at frames [4]–[6], 31 frame mentions |
| A1 | 2 | 1 | 8 | `libfluidThermophysicalModels.so`, 32 frame mentions |
| A4 | 2 | 1 | 3 | `libfluidThermophysicalModels.so` at frames [4]–[6], 12 frame mentions |
| **A2** | **1** | **0** | **4** | **`mca_op_avx.so` → `ompi_coll_base_allreduce_intra_recursivedoubling` → `PMPI_Allreduce`. NO THERMO FRAME.** |

### 5.2 But all four abort at the SAME point in the algorithm

This sharpens the observation and simultaneously limits it. Reading the last lines before each
abort, every arm dies **immediately after the energy equation is solved and before the pressure
equation**:

| arm | the last solver line before the trace | first `[stack trace]` line |
|---|---|---|
| A0 | `log.solve:182` — `Solving for e, Initial residual = 0.0002617854` | `:183` |
| A1 | `log.solve:196` — `Solving for e, Initial residual = 0.00026183626` | `:197` |
| A4 | `log.solve:196` — `Solving for e, Initial residual = 0.00011930455` | `:197` |
| **A2** | `log.solve:156` — `Solving for **h**, Initial residual = 0.99999982` | `:157` |

In every arm the very next line after the energy solve is the stack trace, and in `rhoSimpleFoam`
the very next thing after the energy equation is the thermodynamic update that converts `e` or `h`
back to `T` and then to `rho`, `mu` and `alpha`.

So A2 does **not** fail at a different stage. It fails at the **same** stage, one step earlier, and
what differs is **where the floating-point exception was caught** — inside a thermophysical property
evaluation in three arms, inside a global MPI reduction in the fourth.

### 5.3 AND M0's A2 CANNOT ANSWER THE QUESTION, BECAUSE IT CHANGES TWO THINGS AT ONCE

`run_r2_m0.sh:255-256`:

```
sed -i 's/sensibleInternalEnergy/sensibleEnthalpy/' "$ROOT/A2/constant/thermophysicalProperties"
sed -i 's/transonic no;/transonic yes;/'            "$ROOT/A2/system/fvSolution"
```

A2 differs from A1 in **the energy formulation AND the pressure-equation formulation**. **No share
of A2's earlier death can be assigned to either factor.** The observation is real; the attribution
is unavailable from M0's design. B3 and B4 are the two singletons that make it available, and B5 and
B6 re-measure the corners **with the same instrument**, because M0's A2 produced no record at all
and a 2×2 whose cells were measured by different instruments is not a 2×2.

### 5.4 What weak prior evidence exists, cited and not claimed

M0 §3 reports the ungraded 2026-08-01 probe: `hex_trans_compressible_a2.11` (**`transonic yes`,
energy form unchanged**) died at **`Time = 2`** — i.e. `transonic` **alone** did not move the death
earlier — while `hex_transu1_compressible_a2.11` died at `Time = 1`. That is suggestive of the
energy formulation being the mover. It comes from a probe that **carries no pre-registration and no
verdict from the fixed vocabulary** (M0 §2), so it is **cited, never claimed**, and it is written
here **before** the run precisely so it cannot be produced afterwards as if it had been.

### 5.5 THE STANDING CAUTION, REGISTERED BEFORE THE RUN

**A trap site is where an exception was CAUGHT, not where a bad value was BORN.** Under
`FOAM_SIGFPE`, whichever rank first touches a non-finite value traps; a value born in a thermo
evaluation on one rank can be trapped in an `allreduce` on another. A2 trapped on **4** of 14 ranks
where A0 and A1 trapped on **8**, which is itself consistent with the exception being caught at a
collective rather than at its origin. **`R2M1-G5` therefore reports four cells and assigns no cause**,
and the comparator prints that sentence beside the cells so it cannot be dropped in transcription.
Naming a mechanism is `R2M1-G2`'s job, and `R2M1-G2` rests on **B2**, where the trap is off and the
diverged state is **recorded** rather than inferred from a stack.

### 5.6 A NAMED PREDICTION, WITH ITS FALSIFIER — registered before the run

Prediction-first is worth more than a gate that only counts. From A0's `Time = 1` record — which is
already on disk and is the only pre-divergence state M0 captured:

- `pressureControl: p min -252762.6` (`A0/log.solve:145`) — **the pressure went NEGATIVE in absolute
  terms** during step 1;
- `min(rho) = 0.096767402`, **below the arm's own registered `rhoMin 0.1`**;
- `max(mag(U)) = 690.81616` m s⁻¹ against a registered `magUInf` of 295.

**PREDICTION.** At B2's first step beyond B0's abort point, the first registered field outside its
physical range will be **`p`, going non-positive**, with `rho` following through the `perfectGas`
equation of state, and the thermo inversion being the **site** rather than the source.

**FALSIFIER, stated now.** If B2's record shows `T` or `rho` leaving range at a step where `p`
remains positive and inside `[pMin, pMax]`, the prediction is **wrong** and will be recorded as
wrong. **A wrong prediction here does not change any gate**, threshold or label — `R2M1-G2` grades
whether the mechanism was *measured*, not whether this lane guessed it correctly.

---

## 6. (c) THE COST — RESTRUCTURED SO THE ADMISSION GATE CANNOT ZERO ITS MASS

### 6.1 Why the structure changed, so the next reader inherits the reasoning

`docs/COST_CALIBRATION.md` row `C-20260906T161200.871248Z-5aae017a`, on M0, in its own words:

> *"The registration's dominant term is 'two arms survive to 50 iterations = 62.6 core-min' — 93.6 %
> of the whole 66.9 — and its actual is ZERO, because no arm ran past iteration 2. … AN ESTIMATE
> WHOSE MASS SITS IN 'THE ARMS SURVIVE' IS NOT CALIBRATED BY ITS OWN RATIO WHEN THE ADMISSION GATE
> FAILS — 0.0284 measures the branch the run took, not the quality of the rate model."*

M0's 35.2× over-prediction therefore says nothing about anyone's estimating. **M1 splits the
estimate so that its ratio is a real statement.** The **headline** is the cost incurred **regardless
of any gate outcome**; every survival-conditional term is stated **separately and explicitly as
conditional**, and is never folded in — not in the total, not in the cap arithmetic, and not in the
calibration row this run will owe at completion.

### 6.2 The rate anchors, with their provenance

| anchor | value | provenance |
|---|---|---|
| per 14-rank arm, to the SIGFPE at iteration ≤ 2, on this grid | **0.4667 core-min** | **MEASURED.** M0 `COST.tsv`: A0, A1, A2, A4 each 2 wall s × 14 ranks = 28 core-s. **Four arms agreeing.** |
| per completed iteration, 14 ranks, 638,976 cells | 0.626 core-min | **BORROWED**, from the incompressible log. M0's calibration row: *"stays BORROWED … nothing on this box has yet carried a compressible arm on this grid past iteration 2, so a successor must not read this row as validating that rate in either direction."* |
| `reconstructPar`, serial, 3 fields | **0.0333 core-min** | **MEASURED.** M0 `COST.tsv` `A3_reconstruct` = 2 core-s. |
| `decomposePar -fields`, serial | 0.5 core-min | **ESTIMATED, NEVER MEASURED.** M0's never ran (§2.4). 30 wall s allowed for ~26 MB of field I/O over 14 subdomains. |

### 6.3 HEADLINE — incurred regardless of outcome

| line item | derivation | rate provenance | core-min |
|---|---|---|---|
| seven arms each reach at least the abort point | 7 × 0.4667 | **MEASURED** | **3.267** |
| B2's two extra completed steps (trap off, `endTime 3`) | 2 × 0.626 | borrowed | 1.252 |
| B1 warm start: `reconstructPar` | — | **MEASURED** | 0.033 |
| B1 warm start: `decomposePar -fields` | — | **ESTIMATED** | 0.500 |
| assembly, mesh `decomposePar` ×7, selftest, grade | M0 actual 0.033 for five arms | measured-anchored | 0.200 |
| **the §3.3 writer rehearsal — ALREADY SPENT at drafting** | measured | **MEASURED** | 0.022 |
| **REGISTERED HEADLINE ESTIMATE** | | | **5.27** |

**73.1 % of the headline rests on the measured 0.4667 anchor. No line item in it depends on any arm
surviving anything.** If every arm aborts exactly as M0's did, the headline is still incurred in
full — which is the property M0's estimate lacked.

### 6.4 CONDITIONAL — stated separately, folded into nothing

| conditional line item | condition | derivation | core-min |
|---|---|---|---|
| B1 runs to `endTime 50` | **only if the warm start survives past iteration 2** | 48 × 0.626 (**borrowed**) | up to **30.05** |
| B3–B6 each reach `endTime 3` | only if a diagnostic arm survives to 3 | 4 × 2 × 0.626 (**borrowed**) | up to **5.01** |
| **CONDITIONAL WORST CASE** | | | **35.06** |

**Every core-minute in this table sits on the BORROWED 0.626 rate, which nothing on this box has
tested.** That is the second reason it is not in the headline: it is conditional in its *occurrence*
and unvalidated in its *rate*, and mixing either property into a headline destroys the calibration.

### 6.5 Cap, and dollars

**REGISTERED CAP: 55.0 core-min.** = headline 5.27 + conditional worst case 35.06, plus ≈1.36×
margin on the sum; **10.4× the headline alone**. **An overrun STOPS the run; it does not get a new
budget** (rule 12). The driver's per-arm accounting is checked against the cap after every step and
a cap hit records the remaining arms `BLOCKED`, never extended.

**Dollars are DERIVED, NOT MEASURED — the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5). At the owner-stated `c7a.4xlarge` rate of **$0.0513/core-h**,
`cost_basis: on-box-owner-stated, REPORTED-BY-OWNER`:

- headline 5.27 core-min = 0.08783 core-h → **$0.0045 DERIVED**
- conditional worst case 35.06 core-min = 0.58433 core-h → **$0.0300 DERIVED**
- cap 55.0 core-min = 0.91667 core-h → **$0.0470 DERIVED**

The single-run escalation line is $150 = 175,439 core-min; **this cap is 0.031 % of it.** On-box run,
no rented node, no GPU, no unpriced backlog.

### 6.6 The calibration row this run will owe

Rule 12. At completion the row states the ratio **against the headline**, and reports any conditional
spend **on its own line**, never absorbed. If B1 aborts at iteration 2 like every M0 arm, the
conditional term's actual is zero **and that is not a misprediction** — it is a branch not taken,
and the row must say so in those words rather than divide by it.

---

## 7. THE REGISTERED WRITER BLOCK — the exact text, so what is rehearsed is what runs

Appended to every arm's `system/controlDict`. This is the block §3.3 rehearsed, character for
character.

```
functions
{
    r2m1MinMax
    {
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        writeControl    timeStep;
        writeInterval   1;
        mode            magnitude;
        log             true;
        fields          (T p rho U);
    }
}
```

**M0's `forceCoeffs` function object is NOT carried forward.** M0's arms wrote one
(`postProcessing/forceCoeffs/0/coefficient.dat`, with `Cd: 135.9` at `Time = 1` on a diverging
field). This probe produces no force claim, and an instrument whose output cannot be used is an
invitation to quote it. It is removed rather than ignored.

---

## 8. THE GRADING PATH — FROZEN, AND IT EXISTS

**`cases/committee-grids/grade_r2_m1.py`**, committed with this registration.

M0 v1.0 **failed check 4** because it named a comparator that did not exist and was not in git, so
there was no committed blob to hash against. **That is not repeated here: the file exists, is
committed in the same commit as this registration, and is hashable now.** The driver verifies at run
time that the file that ran **is** the committed blob and writes
`comparator_matches_committed_blob=1` into `STATUS.R2_M1`.

`grade_r2_m0.py` is **frozen and is not edited** (rule 6). `grade_r2_m1.py` is a new file and imports
nothing from it.

### 8.1 The comparator's controls — 12/12 fire, driven 2026-09-06

`python3 cases/committee-grids/grade_r2_m1.py --selftest` → `R2M1-G6: PASS -- 12/12 controls fired`:

| | control |
|---|---|
| C0 | assert-free proved (0 found) **and** the detector sees a planted one (1) — L-221/L-222 in the checking direction |
| C1 | the **real** archived 2026-08-01 abort log reads `ABORTED` at `Time = 2`, thermo frame seen 32× |
| C2 | the **real** archived clean log reads `COMPLETED`, no abort signature |
| C3 | **mutation** — the abort signature planted into the clean log flips it to `ABORTED` |
| C4 | a planted `nan` fires the scan; unplanted stays silent |
| C5 | `rc=0` beside a SIGFPE log **REFUSED**; `rc=0` beside a clean log allowed |
| C6 | the **age guard**: fields newer than `0/T` pass; `0/T` touched forward **fails** |
| C7 | the **run-root guard**: absent root permitted; occupied root **REFUSED** |
| C8 | **W1 reader planted**: `[3,3,3,3]` live → `[0,0,0,0]` absent → `[3,3,3,3]` restored — **DISCRIMINATES** |
| C9 | **W2 reader planted**: 2 live → 0 scrubbed → 2 restored — **DISCRIMINATES** |
| C10 | **THE WRITER GATE ITSELF driven in the REFUSING direction**: passes 3-of-3, **fails** 1-of-3 and 0-of-3, and passes a zero-step arm with zero records |
| C11 | **the completion rule driven in the refusing direction**: all six clauses together pass; `rc`, `End`, last-time, `ExecutionTime` count and a missing field each fail on their own clause |

**C10 is the one that matters most.** A reader that discriminates is not enough — M0's reader
discriminated too. The **gate** must be shown able to fail, and to pass the one case M0's gate could
not express (an arm that completed zero steps).

### 8.2 The grading path was driven on REAL data, not only on its selftest

A sibling team lost a verdict on 2026-09-06 to a comparator that passed its selftest and then
**crashed on real data at three of its four plant call sites** (`00cb4530`). So `grade_r2_m1.py` was
run end-to-end against M0's **real** arm directories — real `log.solve`, real `rc.txt`, real
`postProcessing` trees — mapped onto M1's arm names **in a scratch directory, as a shape check
only**. It completed with `rc = 0`, produced no exception, and returned the correct shapes: `G1`
`PASS` including for the zero-step arms; `G2` `NOT A RESULT` (the stand-in for B2 had its trap on);
`G3`/`G4` `BLOCKED` (no warm-start marker). **That exercise is NOT A RESULT and is not evidence
about M1's arms** — its B3/B4/B5/B6 stand-ins are duplicates of M0's A1 and A2, so only two distinct
logs are present. It is evidence about **the comparator**, which is what it was for.

---

## 9. THE GATES

| id | gate | **threshold (pre-registered)** | cap (core-min) | label if met | label if not |
|---|---|---|---|---|---|
| **R2M1-G0** | **Reproduction control.** B0 reproduces the known abort with M1's instrument set attached. | B0 exits **136**, log classifies `ABORTED`, last `Time ≤ 2`, `libfluidThermophysicalModels.so` in its own stack | 1.0 | proceed | **`NOT A RESULT` for the whole probe** — no conclusion is drawn from any other arm |
| **R2M1-G1** | **Writer liveness, PER ARM.** | For **every launched arm**: W1 records == `steps_completed`, exactly, for **each** of `T`, `p`, `rho`, `mag(U)`; and W2 ≥ `steps_completed`. An arm with `steps_completed = 0` satisfies this with zero records and is recorded as `COMPLETED_STEPS=0`, **not** as a missing file | 0.0 (inside G0's runs) | **`PASS`** | **`GATE FAIL` on the writer, and `NOT A RESULT` for the mechanism** — and the **writer**, not the physics, is named as what failed |
| **R2M1-G2** | **Mechanism named by measurement.** | B2 (FPE trap **off**) reaches `Time ≥ 3` — at least one step **beyond** B0's abort point — **and** carries a W1 record at that step for all four fields, **and** G1 passed | 1.3 | **`PASS`** — the mechanism may be named, and §5.6's prediction is scored | **`NOT A RESULT`** for the mechanism. G0/G4 stand; **no cause may be named** |
| **R2M1-G3** | **The warm start MAPS AND EXERCISES.** | `B1/WARMSTART_MAPPED` present — written only after the **repaired binary-safe guard** passes **and** `decomposePar -fields` returns 0 — **and** `B1` arm state is not `BLOCKED` | 0.6 | **`PASS`** | **`BLOCKED`** — the last untested remedy is **still** untested. **Explicitly NOT a `GATE FAIL`** |
| **R2M1-G4** | **ADMISSION — the only admission gate.** | B1 reaches `Time = 50` satisfying **all six clauses of rule 4** (rc = 0; `End`; last time == `endTime`; `ExecutionTime` count == `endTime`; `T U p k omega nut alphat` present at `endTime`; **every field newer than the case's own `0/T`**), with **no** signal 8 and **no** `nan`/`inf` token anywhere in its log | 30.1 (**conditional**) | **`PASS`** — the warm start clears Blocker 1 | **`GATE FAIL`** — the last remedy is now tested and Blocker 1 stands with **all five** exhausted. If G3 is `BLOCKED`, this is **`BLOCKED`**, not `GATE FAIL` |
| **R2M1-G5** | **The 2×2 cells, measured with a live writer.** | B3, B4, B5, B6 all launched, all passing G1, and each cell's abort step and trap site **recorded**. **This gate grades MEASUREMENT, NOT OUTCOME, and NAMES NO CAUSE** | 5.0 (**conditional**) | **`PASS`** — four cells measured | **`NOT A RESULT`** for the de-confound |
| **R2M1-G6** | **Planted control on the reader** (rule 3). **ALREADY MEASURED — §8.1.** | 12/12 controls fire, including the writer gate and the completion rule driven in the **refusing** direction | 0.5 (spent: **0.000**) | **`PASS`** — measured 2026-09-06 | **`NOT A RESULT` for every other gate** — a reader not shown able to see both outcomes has measured nothing |

**The item verdict is carried by `R2M1-G4`.** `R2M1-G0` and `R2M1-G6` can only turn a `PASS` or a
`GATE FAIL` **into** `NOT A RESULT`, never the reverse (rule 5's ordering, applied to a gate table
rather than a grid triple).

**`R2M1-G3` returning `BLOCKED` is a real, reportable outcome and not a failure to report.** It is
written this way because M0's grading record made exactly this distinction and was right to.

---

## 10. WHAT THIS PROBE MAY NOT CLAIM

1. **No force, drag, lift, moment, coefficient or CRM number.** None is read out, and the comparator
   prints that sentence as its last line so it cannot be lost in transcription.
2. **A `PASS` on `R2M1-G4` does not make Rung 2 (a) gradeable.** It clears **Blocker 1 only**. Rung 2
   (a)'s drag gate stays `BLOCKED` on three independent grounds, binding ground **(iii), the absent
   refinement triple** — a compute result cannot move a ground that is about grids that do not exist
   on this box.
3. **No mechanism may be named unless `R2M1-G2` passes.** A stack trace is not a mechanism.
4. **No cause may be assigned to any 2×2 difference** (§5.5). `R2M1-G5` reports cells.
5. **No claim that the 0.626 core-min/iteration rate is validated**, in either direction, unless an
   arm actually carries past iteration 2 — and then only for the configuration that did.
6. **The 125-cell rehearsal is not a physics result** and is not cited as one anywhere.

---

## 11. HONEST RECORD OF THIS DRAFTING

**Check-repair cycles, counted (the check-loop bound is three per stage):**

| stage | cycles | what each was |
|---|---|---|
| §3.3 writer rehearsal | **2** | (1) OpenFOAM's own `etc/bashrc` dereferences unset variables, so `set -u` killed the harness with a silent `exit 1` before anything ran. (2) `grep -c PAT f \|\| echo 0` emits **two** lines on no-match — `grep -c` prints `0` **and** exits 1, so the `\|\|` fires too; the reader returned `"0\n0"`, `[` refused it as a non-integer, and **all seven controls were scored `DOES_NOT_DISCRIMINATE` for a reason that had nothing to do with discrimination.** Replaced with `awk`, which returns exactly one integer on every path. |
| §8 comparator | **0** | 12/12 on the first drive; real-data drive clean on the first drive |
| this registration | **0** | check 4 not yet performed — it is the supervisor's |

**The second rehearsal cycle is worth keeping.** The harness **refused** rather than reporting a
number it could not stand behind, and the refusal was correct behaviour on a defect that would
otherwise have been invisible: had the reader returned a clean `0` instead of `"0\n0"`, the controls
would have silently read as failing and the rehearsal would have been abandoned for a phantom.

**Spend by this lane: 0.0219 core-min GROSS**, all of it §3.3, all of it on a 125-cell serial box.
`cost_basis: on-box-owner-stated`; **$0.0000187 DERIVED, NOT MEASURED**. No DPW5 solve, no MPI job,
no run root, no queue row.

**What this lane could not settle, and it needs someone else:**

1. **`decomposePar -fields` on this grid has never run** (§2.4). Its cost is estimated, not measured,
   and its success is not assumed. Measuring it costs ≈0.5 core-min but is a **run**, and this lane
   was authorised for zero compute beyond the rehearsal. **Named and stopped.**
2. **Whether `endTime 3` is the right diagnostic length for B2.** If the diverged state is already
   saturated at step 3 the record may be uninformative; if divergence is slower, 3 is too short.
   Nothing on this box can answer that without running B2, so 3 is registered as the minimum that
   guarantees at least one step **beyond** B0's abort point, and the choice is disclosed rather than
   defended.
3. **Check 4 — the pre-registration committed before compute — is the cfd supervisor's and is not
   taken here.**
4. ~~**The driver `run_r2_m1.sh` is NOT written.**~~ **STRUCK by Amendment 1, §13 — the driver
   exists.** Original text preserved: *"This registration fixes the grading path, the arm set, the
   gates, the writer block and the cost; the driver that assembles and launches the arms remains to
   be written and reviewed, and the registration is not freeze-ready for launch until it exists.
   The grading path — the thing rule 2 freezes and check 4 hashes — does exist."*

---

## 12. STATUS

| | |
|---|---|
| registration | **v1.0 DRAFT — gates OPEN, amendments legal until first compute** |
| check 4 | **NOT PERFORMED** — the cfd supervisor's, non-delegable |
| queue row | **NONE PLACED.** Placement is the chief's, under its own captured grant |
| run root | **ABSENT**, plant-verified 0 → 1 → 0 (§1.3) |
| grading path | `cases/committee-grids/grade_r2_m1.py` — **exists, committed, 12/12 controls, driven on real data** |
| driver | `cases/committee-grids/run_r2_m1.sh` — **exists (Amendment 1, §13). Cap selftest 7/7; root guard driven refusing on the real path.** |
| solver core-min spent under this registration | **0.0219**, all of it the §3.3 rehearsal on a 125-cell box |
| Rung 2 (a) | **BLOCKED**, untouched, binding ground **(iii)** |

---

## 13. AMENDMENT 1 — 2026-09-06, **PRE-COMPUTE**, on the cfd supervisor's instruction

**THE CONDITION, AND HOW IT WAS CHECKED.** Rule 2 permits amendment **only before first compute**,
and requires the condition to be stated and checked, naming the run directory that does not exist.

> **Condition: no compute has been run under this registration.** Checked, not asserted: the
> registered run root **`verification/runs/RUNG2_CRM_runs/M1_mechanism_and_warmstart`** is
> **ABSENT**, re-verified at amendment time (2026-09-06T16:38:10Z) under a live planted control —
> **0 → 1 → 0, DISCRIMINATES**, no residue. No `COST.tsv`, no `STATUS.R2_M1`, no arm directory and
> no queue row exists. **The only core-minutes spent under this registration remain the 0.0219 of
> the §3.3 writer rehearsal on a 125-cell box, which is not a run against any gate here.**

**NO GATE, THRESHOLD, CAP OR LABEL IS ALTERED BY THIS AMENDMENT.** The seven gates of §9, the
55.0 core-min cap of §6.5, the 5.27 core-min headline and every label are **unchanged**. §11 item 4
is **struck, not rewritten**, and its original text is preserved verbatim beside the strike.

### 13.1 What this amendment adds

1. **§3.5** — the `pressureControl: p min -252762.6` observation, with its path and line, recorded
   **as an observation and explicitly not as a cause or a mechanism claim.**
2. **The driver now exists**: `cases/committee-grids/run_r2_m1.sh`, committed with this amendment.

### 13.2 The driver, and the two things it was required to demonstrate rather than assert

**(i) THE CAP HAS BEEN SHOWN TO WORK.** M0's calibration row is explicit that its cap path was
**never exercised**: *"both remain UNEXERCISED and this run is not evidence that either works."*
`run_r2_m1.sh --selftest-cap` drives it, costs nothing, and the driver **runs it before any compute
is bought and refuses to continue if it does not pass**. Measured 2026-09-06, **7/7**:

| | control | result |
|---|---|---|
| K0 | `budget_left` is `CAP − SPENT` | 1000−0=1000, 1000−400=600 |
| K1 | the timeout **shrinks** with spend and **never reaches 0 s** (`timeout 0s` means *no limit* — a runaway, not a stop) | 100 s → 50 s → 1 s |
| **K2** | **an exhausted cap returns 66 AND THE COMMAND DOES NOT RUN** — planted: the refused command would have created a witness file | rc **66**, **witness absent** |
| **K3** | the **same** command **does** run with budget left — a refusal that refuses everything is not a cap, it is a broken driver | rc 0, **witness present** |
| K4 | the step is **charged** `wall × ranks` — a cap that never charges never bites | 2 wall-s at 14 ranks charged **28 core-s** |
| **K5** | **the timeout actually fires**: `sleep 60` under a 28 core-s budget | killed at 2 s, **rc 124** |
| K6 | the budget is then exhausted, so the run **stops** and does not get a new one | 0 core-s left |

**(ii) THE GUARD IS NOT TRUSTED UNTIL IT HAS BEEN WATCHED DISCRIMINATE.** §2 established that M0
recorded a map failure that never happened, because **a crashed guard's exit code is
indistinguishable from the failure it was watching for**, and that sentence then travelled up four
levels unchallenged. `run_r2_m1.sh` therefore drives its own warm-start guard **at run time, on the
real reconstructed field**, watching it accept the good field and **refuse** a copy with `farfield`
scrubbed. **If it does not discriminate, B1 is recorded `BLOCKED` and the guard's verdict is
discarded** — not believed in either direction.

**And when B1 does not map, the driver writes `B1/WARMSTART_NOT_MAPPED` carrying the reason
verbatim** — never the words "FAILED TO MAP", which is precisely the sentence M0 wrote about a map
that had already succeeded.

**Rule 4's root guard was also driven in the REFUSING direction on the real registered path**: with
the root present the driver exits **3** and starts nothing; the probe left no residue and the root
is absent again. A bare invocation prints usage and launches nothing.

### 13.3 What this amendment does NOT do

- It does **not** run `decomposePar -fields`. That stays **NAMED AND STOPPED** (§2.4, §11 item 1):
  its cost is **ESTIMATED, not measured**, its success is **not assumed**, and `R2M1-G3` returns
  **`BLOCKED`, not `GATE FAIL`**, if it fails.
- It does **not** perform check 4. **That is the cfd supervisor's and non-delegable.**
- It does **not** place a queue row. **None has been placed and this lane placed none.**
- It spends **no additional solver core-minutes**. The cap and guard controls are shell arithmetic
  and a `sleep`; no solver, no MPI job, no mesh operation, no DPW5 grid.
