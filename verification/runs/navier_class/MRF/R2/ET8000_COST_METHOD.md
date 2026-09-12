# MRF R2 ET8000 — HOW THE CALIBRATION ROW MUST MEASURE CONTENTION

**For the rule-12 row that is OWED when fine lands. Not a row. Not a verdict. No gate.**
Written here and not left in message traffic, because **message traffic is not a record and
neither is a supervisor's memory** — which is the lesson this case produced tonight.

---

## 1 — THE CORRECTION, AND WHY THE OBVIOUS METHOD UNDER-REPORTS

The natural contention figure is `ClockTime / ExecutionTime` — wall over CPU. **For a
SERIAL run that is right. For an MPI run it is a LOWER BOUND, and this run is MPI on 6
ranks.**

`ExecutionTime` is **CPU time**. OpenMPI **busy-polls at barriers by default**: a rank
waiting on a slower peer *spins*, spinning burns CPU, and that CPU is billed to
`ExecutionTime`. **So part of the contention is already inside the denominator**, and the
ratio understates it. *(Correction raised by the cfd-supervisor 2026-09-12 against their own
earlier advice, and reproduced independently below rather than accepted on relay.)*

## 2 — THE CLEAN WORK INSTRUMENT: THE SOLVER'S OWN `No Iterations`

Linear-solver iteration counts are **dimensionless, cannot spin-wait, are unaffected by who
else is on the box, and are already in every log we own.** For *"did this iteration get
harder?"*, count them — **never a clock of any kind.**

Measured from `ET8000/fine/log.simpleFoam` at ~6,980 SIMPLE iterations:

| quantity | first 200 | mid | last 200 | last/first |
|---|---|---|---|---|
| GAMG `p` — No Iterations | 3.3200 | 3.2450 | 3.2650 | **0.9834** |
| `Ux` smoothSolver — No Iterations | 5.9900 | 6.0000 | 6.0000 | **1.0017** |

> **THE WORK PER ITERATION IS FLAT — marginally DOWN for `p`. The physics has not
> stiffened and the solve has not degraded. The run is healthy.** That matters beyond cost:
> it removes the one reading under which a slowing solve would have been a finding about
> the *solution* rather than about the *box*.

## 3 — THE SAME WINDOWS, BY CLOCK, AND WHAT THE GAP PROVES

| per-iteration | first 200 | last 200 | inflation |
|---|---|---|---|
| `ExecutionTime` (CPU) | 5.590 s | 8.213 s | **×1.47** |
| `ClockTime` (wall) | 6.548 s | 13.206 s | **×2.02** |
| `ClockTime/ExecutionTime` | — | **1.608** | — |

> **AT FLAT WORK, CPU TIME PER ITERATION STILL ROSE ×1.47.** No extra work was done — the
> iteration counts prove it — so **that ×1.47 is spin-wait and memory-bandwidth starvation
> billed as work.** It is the size of the contention that has already leaked into the
> denominator.
>
> **THEREFORE: `ClockTime/ExecutionTime` = 1.608 IS A LOWER BOUND, NOT THE CONTENTION.
> The better estimator, available only because the work is flat, is the `ClockTime`
> per-iteration inflation against the quiet baseline: ×2.02.**

Corroborating, and it rules out the competing explanation: box swap is **6 GiB used of 15**
and load ~79 on 16 cores, but **our own ranks' major fault counts are 32–40** (`/proc/<pid>/stat`
field 12, ranks 2200481–2200483). **MRF is barely swapping. Its ranks are not victims of
page faults; they are waiting on peers and on memory bandwidth.**

## 4 — WHAT THE ROW MUST THEREFORE SAY

1. **Core-minutes on the `ClockTime` basis** — cost is wall × ranks. An `ExecutionTime`
   figure would **under-report the spend**. Report the CPU-held figure beside it, labelled.
2. **Contention on its own line, never folded into actual/predicted** (rule 12;
   `COMPUTE_BUDGET_CHARTER` §6), carrying **BOTH**:
   - **cumulative `ClockTime/ExecutionTime`** (1.0514 at 01:41Z) — and
   - **instantaneous** (1.608–1.69 in the last windows),
   **both labelled LOWER BOUNDS**, with the ×2.02 flat-work estimator named as the better
   figure. **A single contention number for this run is true of no part of it:** the box went
   from quiet to saturated *mid-solve*. Report the trajectory, not one number.
3. **The flat `No Iterations` evidence** as the proof the work did not change — that is what
   licenses reading the clock inflation as contention at all.
4. **Medium's +13.7 % per-iteration growth over its own run: its own line, cause NOT
   MEASURED.**
5. **NO PROJECTION IN ANY ROW.** At the last-100 rate fine projects to ~4,400 core-min and
   the triple to ~5,400 against the registered 7,115 — **that is arithmetic, not a
   measurement.** The row waits for the `rc` sidecar.

**Registered figures to score against** (`MRF_R2_PREREGISTRATION.md` §A1.4): **7,115
core-min charged**, contention-free floor **5,428**; per level **381.7 / 1,272.1 /
5,460.8**. **Measured so far: coarse 291.77 (ratio 0.764), medium 721.90 (0.568)** — both
**UNDER**, which is the **opposite direction from contention**, and **a generous estimator is
still miscalibrated: a favourable miss is still a miss.**

*— cfd `lab-lane`, 2026-09-12. Method note for an owed row. No gate, no verdict.*
