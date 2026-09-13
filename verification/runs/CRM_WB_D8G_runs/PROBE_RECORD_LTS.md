# CRM-WB-D8G-SOLVE-T-LTS-PROBE — RUN RECORD

**Registered under** `verification/campaign/CRM_WINGBODY_DPW6_ACT_PREREGISTRATION.md` **ADDENDUM 15**
(version 1.14), frozen at commit `0a97d4128a444870e47644a9f3c722af122c4bb2`, blob
`94f90952a9d360f7e405a4da7b248702b8951c73`. Launcher commit `5f7d9b227f9cb0d3a3743ea83ad931438e6204a5`,
sha256 `609aecdac79209598f8f4621dec51f01ac0f56a776d4552a458196e72ff9c8d0`.
Launched 2026-09-13T16:37:40Z, ended 16:43:21Z, 32 ranks, `rc=0`.

**This is the 20-step RATE PROBE of A15.8, not the production run.**

---

## 1. VERDICTS

| channel | registered threshold | measured | verdict |
|---|---|---|---|
| **L1** | `h` initial residual < 0.99 by step 20 | 0.1999 at step 1 → **0.0318** at step 20, monotone from step 4, never above 0.2 | **PASS** |
| **L2** | clamped fraction, both branches, < 1 % at step 50 | step 50 not reached; at step 20 **3 cells of 20,657,615 = 1.45e-5 %** | **PENDING** (reading point not reached) |
| **L4a** | `rDeltaT` finite | min 4.29234, max 2.81547e+07 s⁻¹; **0 non-finite, 0 zero, all positive**; local dt 3.55e-08 – 0.2330 s, below the registered `maxDeltaT 1 s` | **PASS** |
| **L4b** | "the **reported** Courant number ≤ maxCo 0.2" | **no reader exists** — 0 occurrences in the log; `setRDeltaT.H`'s `Flow time scale min/max` print is inside `if (debug)` | **NOT A RESULT** (gate names a channel nothing writes) |
| **L5** | `\|p\|` max < 12,854 Pa **and** `max\|U\|` < 600.038 m/s, **read from the field** | `\|p\|`max **8,014.789298 Pa** (0.624×) — see §3; **`max\|U\|` 2,471.0759 m/s at t=12 (4.118×), 2,122.8240 at t=18 (3.538×)** | **GATE FAIL** |

**COMPLETION RULE: FAILED — the run is NOT A COMPLETED RUN.** `rc=0` ✓; `End` line ✓; last
`Time = 20` == `endTime 20` ✓; `ExecutionTime` count 20 == endTime at `deltaT 1` ✓; age guard ✓
(newest field 16:42:50 against `processor0/0/T` 16:38:03); **fields present at endTime ✗ — no
`processor*/20` directory exists.** `writeInterval 6` does not divide `endTime 20`, so writes fell
at t=6, 12, 18 and `purgeWrite 2` then discarded t=6. **Cause is a staging error by this lane:**
the queue entry registered that `writeInterval` must place a write *inside* 20 steps, which it
does; **the clause that binds is a write AT `endTime`, and those are different conditions.**
Production at `endTime 6000` is unaffected — 6000/6 divides exactly.

## 2. THE MEASURED RATE — A15.8's REGISTERED PRODUCT

`ExecutionTime = 307.91 s` over 20 steps = **15.396 s/step**; excluding step 1's setup,
(307.91 − 22.76)/19 = **15.008 s/step**. Actual **164.2 core-min** against the registered
worst-case cap of **2,994 core-min** — **ratio 0.055**. Attribution: the cap was deliberately taken
from `rhoSimpleFoam` at 280.7 s/it, 18× slower than the application that ran. No waste, no
contention. Production projection at the measured rate: 6000 × 15.396 × 32/60 = **49,267 core-min**
(≈ $42.12 **derived, not measured** — the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER`
§5; $0.0513/core-h is reported-by-owner). A calibration row is owed to `docs/COST_CALIBRATION.md`.

The four rates now measured on this mesh at 32 ranks: `rhoSimpleFoam` worst **280.7**, R1 **10.81**,
SST **24.73**, `rhoPimpleFoam`+LTS **15.396** s/step.

> **A14.2b BINDS THIS NUMBER, INCLUDING AGAINST ITS OWN AUTHOR. A rate is a COST INPUT and nothing
> else.** P5 once predicted a faster rate would mean a healthier run, and the prediction came true
> while the run destroyed itself. **No health claim rests on 15.396 s/step.**

## 3. 🔴 THE `p` CLAUSE IS INSIDE THE THRESHOLD **ON A CLAMPED FIELD**, AND IS NOT RECORDED AS A BARE PASS

`max(p)` is **identical to ten significant figures at t=12 and t=18 — 8,014.789298 Pa — in the same
cell 153701 on processor 0.** That is a **clamp signature, not a converged value**: `pressureControl`'s
registered `pMaxFactor 2.0` ceiling is holding it. Cells pinned at exactly that value:
**18,868 at t=12 (0.09134 %) rising to 22,766 at t=18 (0.11021 %)** — **the pinned population grows
between the only two times the gate can see.** A gate satisfied by the clamp that is hiding the
excursion is not a gate satisfied.

## 4. 🔴 A DEFECT IN L5 ITSELF — THE GATE IS BLIND TO THE EXCURSIONS IT EXISTS TO CATCH

The solver's own `pressureControl` log line reports `p max` **20,176.58 Pa at step 4** — **1.57× the
L5 threshold** — and breaches on **7 of 20 steps** (15254.2, 20176.6, 17774.9, 17922.6, 19296.6,
15032.8, 16604.6 Pa). **The field at t=12 and t=18 reads 8,014.79.** Fields exist at two times only,
so **L5 as registered sees 2 of 20 steps.** This is a defect in the instrument, of the same family
as L4b naming a channel nothing writes. Note also that `pressureControl: p min` printed **zero
times** — it prints only when the low clamp fires, so **a channel silent when healthy cannot be
distinguished from a channel that is dead.**

## 5. HOW L5 WAS READ, AND WHY THE READING IS TRUSTED

**Read from the field, all 32 ranks, all 20,657,615 cells, at both surviving write times** — not
from the log. The first reading of L5 by this lane was taken from the log while L4 was taken from
the field; **two standards in one act**, corrected on the supervisor's refusal.

- **Independent confirmation by a different code path.** `mpirun -np 32 postProcess -parallel -func
  'fieldMinMax(fields=(p U))' -time 12,18` — OpenFOAM's own reader — returns
  `max(mag(U)) = 2471.07588975` / `2122.8240118` and `max(p) = 8014.789298`, matching this lane's
  binary parser to every digit. Agreement between two of one's own functions is not verification.
- **Planted control, run BEFORE either verdict.** 99,999 Pa injected into `p` and 5,000 m/s into `U`
  on an untouched rank, **in memory, disk unmodified**: read back as 99999 and 5000, **both
  DETECTED**. The reader is shown able to see a value it was not given, so the clean `p` clause is
  evidence and so is the breach.
- **A near-miss, recorded because it nearly became the finding.** An 8-rank sanity sample returned
  an unphysical median (3.15 m/s in a 300 m/s freestream) and **zero** cells above the gate,
  apparently contradicting the full scan. The cause was a **sampling error by this lane, not a parse
  error**: the eight ranks were taken in *lexicographic* order (processor0, 1, 10, 11, …) and **the
  breach is on processor 17**, which was not among them. **A lexicographic sample of ranks is not a
  sample of the field.**

## 6. WHERE THE BREACH SITS — OFFERED AS A DIRECTION, NOT AS A FINDING

The breach is **localized and shrinking**: **329 cells of 20,657,615 (0.001593 %) at t=12, 265
(0.001283 %) at t=18**, with the peak falling 2,471 → 2,123 m/s. The breach cell **120629 at
(47.9279, 29.4312, 7.4801)** sits on the **same spot to two decimals** as the global pressure
minimum, cell **268542 at (47.9663, 29.4073, 7.4931)**, both on processor 17.

A single localized point carrying both the velocity maximum and the pressure minimum, on a grid
whose committee quality record is `Mesh OK = false` at all three levels — **740,519 faces above 70°,
maximum non-orthogonality 89.4641°, minimum cell determinant 0** — points at **rung 1, the MESH**,
which this act has never stood on. **This lane has not demonstrated that and does not assert it.**

## 7. 🔴 THE REPAIRS, VERIFIED IN PRODUCTION AND NOT ONLY IN SIMULATION

`LAUNCH.log` line 4 reads **`registered endTime=20  ramp=0 iterations`**, and the run stopped at
`Time = 20`. **That line is the 300× overrun failing to happen, observed live.** Before the
A15.6(b) repair, stage 2 would have restored `endTime 6000` from `system/controlDict.registered` —
a file created once under a `[ -f ] ||` guard and never refreshed — and the md5 assert would have
compared that file **with itself** and passed. **This is the first entry in the act's history where
the argv endTime and the inherited value differ, so it is the first run that could ever have
demonstrated either outcome:** R1 and SST both passed 6000 into cases already holding 6000. A repair
verified in simulation and then again in production, on the first entry capable of distinguishing
the two, is a stronger artifact than either half alone.

`LAUNCH.log` line 2 reads **`application: rhoPimpleFoam (ASSERTED against system/controlDict, not
assumed)`** — a line that did not exist before this rung, and the reason the run is `rhoPimpleFoam`
rather than a silent twenty-third `rhoSimpleFoam` variant.

**PIMPLE reported `Operating solver in PISO mode` and `Using LTS` at startup** — the PISO-mode line
is precisely why the A15.6(a) `Final` solver keys were required, confirmed in production.

## 8. WHAT WAS NOT READ

**NO FORCE NUMBER FROM THIS RUN HAS BEEN READ.** A15.6(c) — the planted-force control under
`rhoPimpleFoam` — is **UNDISCHARGED**, so the force reader is presumed blind. A15.3 is why that is
urgent rather than formal: SST's **pressure** force integral returned an ordinary-looking
`Cd 0.00912114085539` while the field stood at `p max 3.87e+129`. **A force reader that returns a
plausible number from a diverged field is the exact hazard standing rule 3 exists for.**

## 9. ARTIFACTS

`log.rhoPimpleFoam` (20 `Time` blocks, one `End`), `LAUNCH.log`, `RC.txt`, `log.potentialFoam`,
`log.isentropic_init`, `processor*/{12,18}/{p,U,T,rDeltaT,rho,phi,nut,nuTilda,alphat}`,
`system/*.PRE_A15` (the before-image of every dictionary change),
`verification/queue/cfd/launched/CRM-WB-D8G-SOLVE-T-LTS-PROBE.json`.
