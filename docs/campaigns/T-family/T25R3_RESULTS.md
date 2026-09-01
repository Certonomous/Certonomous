# T25R3 — RESULTS: **THE RUNG PRODUCED NO GRADEABLE ROW, AND THE REASON IS THAT ITS THREE MESH LEVELS WERE NEVER SOLVED TO THE SAME STANDARD**

**Written 2026-09-01T~17:40Z by a heat-transfer `lab-lane`.**
Registration: `docs/campaigns/T-family/T25R3_PREREGISTRATION.md`, frozen at
**`8cef4791`**, Amendment A1 at **`e46aa244`**, Addendum D1 at **`6b1f3968`**.
Comparator and completion marker frozen at **`629f5b32`**.

Verdict vocabulary is `CLAUDE.md` rule 1's and is used nowhere loosely. **§1.2
declines to pick a label and refers it to the supervisor**, on his instruction.

---

## 1. THE OUTCOME, IN ONE LINE

> **The `p_rgh` convergence criterion registered at §4.1 is ABSOLUTE, so the
> convergence standard tightened silently as the mesh refined. The pressure
> equation was effectively NOT SOLVED on L1 and heavily solved on L3 — a ~955×
> spread in solver effort across a ladder whose entire purpose is to compare
> three levels solved to the SAME standard. No gate was evaluated and no physics
> number exists.**

**This is not a failure of the physics, and it is not a cap stop.** It is a
registration that could not have produced a comparable ladder, discovered by
measurement four minutes after the fleet reached a steady state.

### 1.1 WHAT WAS MEASURED

Mean GAMG iterations per `p_rgh` solve, across the full leg-A logs:

| run | mesh | cells | mean GAMG iterations / solve | solves counted |
|---|---|---|---|---|
| **S1** | L1 | 16,608 | **0.4** | 80,905 |
| **S2** | L2 | 37,368 | **41.6** | 4,956 |
| **S3** | L3 | 84,078 | **382.2** | 314 |

`Initial residual = 9.72e-09` on L1 against a **1e-08 absolute** threshold.
**A mean of 0.4 means the pressure equation is not being solved; it is being
declared converged on arrival.**

The registered key is `p_rgh / p_rghFinal: tolerance 1e-08; relTol 0`. The
absolute scale of an OpenFOAM residual moves with cell count, so **an absolute
tolerance is a different physical demand on every mesh.**

### 1.2 ⚠ THE LABEL IS **REFERRED, NOT CHOSEN**

The supervisor's ruling 1 is explicit: *"Do NOT reach for a verdict from the
fixed vocabulary that flatters this; if none fits cleanly, say what happened and
let me rule on the label."* This lane therefore states the facts and the two
candidates, and picks neither.

- **`NOT A RESULT`** fits the *rows*: any value from these levels is untrustworthy
  because the levels are not comparable. But rule 1's `NOT A RESULT` normally
  labels a row that **has a value and cannot be believed**, and here the
  comparator never ran, so **no row has a value at all.**
- **`BLOCKED`** fits the *rung*: the ladder could not run to a comparable answer
  under its own registration. But `BLOCKED` in practice names an external
  obstacle (capacity, a missing dependency), and this obstacle was **internal and
  self-inflicted** — the registration's own numerics.

**Neither is a clean fit and this lane will not force one.** What is certain, and
what no label changes: **no gate was evaluated, no threshold was compared against
anything, and no physics number exists to be quoted.**

---

## 2. ⚡ THE HEADLINE: **SANAA'S §0.2 RULE CAUGHT THIS**

Her directive of 2026-09-01 ~15:45Z, §0.2, verbatim:

> *"Run all three to TIGHT iterative convergence. Rule: the iterative change in
> the graded quantity must be at least 10× smaller than the difference between
> consecutive mesh levels. If it is not, the observed order is noise, not
> discretisation."*

**That rule, promoted from prose to the gate `G-I` at §7.3 of the registration,
is what would have refused this ladder.** Three levels solved to three different
standards cannot produce an observed order that means anything; `G-I` is the gate
that asks precisely whether the iterative machinery is quiet enough for the
discretisation signal to be read, and it would have said no.

> **THE DOCTRINE SHE ISSUED THIS AFTERNOON FOUND A DEFECT THAT WOULD OTHERWISE
> HAVE PUBLISHED AN OBSERVED ORDER COMPUTED FROM THREE LEVELS SOLVED TO THREE
> DIFFERENT STANDARDS — before it published anything.**

**And the honest addition, which is the part that makes this a real endorsement
rather than a compliment:** the defect was caught **upstream of `G-I`, by the
cost blow-up**, not by the gate firing. The gate never ran. What the doctrine
supplied was the *reason to look* — and the reason the ladder was built as three
comparable levels at all, which is what made the 955× spread visible as a defect
rather than as an unremarkable fact about bigger meshes. **The cost blow-up of
19–33× and the noise order are the same defect seen from two ends.**

---

## 3. WHAT RAN, AND WHAT WAS DELIBERATELY STOPPED

| run | mesh | s/step measured | vs POINT | needed | registered cap | disposition |
|---|---|---|---|---|---|---|
| **S1** | L1 | **0.1973** | **×1.02** | 0.65 h | 2.54 h | **allowed to finish** (§4) |
| S2 | L2 | 8.1505 | ×18.7 | 26.7 h | 5.72 h | **halted 17:24:59Z** |
| S3 | L3 | 28.185 | ×28.7 | 92.4 h | 12.86 h | **halted 17:24:59Z** |
| T2 | L2 | 11.037 | ×25.3 | 72.4 h | 11.43 h | **halted 17:25:00Z** |
| T4 | L2 | 14.564 | ×33.4 | 190.9 h | 22.87 h | **halted 17:25:01Z** |
| W30 | L2 | 15.772 | ×19.8 | 51.7 h | 10.46 h | **halted 17:25:01Z** |

**THE HALT WAS A DELIBERATE, RULED DECISION AND NOT A CRASH.** Five runs could
not reach `endTime` inside their registered `timeout`, so rule 12 fixed their
verdict as a cap stop **before they got there**. Running them to cap would have
burned **7,600 core-minutes to produce nothing gradeable.** *Idle compute is a
failure; so is compute that cannot produce a result.*

**IT IS NOT CONTENTION, AND S1 IS THE CONTROL THAT PROVES IT.** S1 ran in the
same window, on the same box, against the same competitors, and matched its
pre-registered rate to **×1.02**. Without S1 the scheduling defect (§6) and the
numerics defect (§1) could not have been separated from each other.

### 3.1 THE HALT LEFT A POSITIVE ARTEFACT, AND THAT MATTERED WITHIN THE HOUR

The supervisor triaged the box independently, saw five logs stop inside two
seconds with zero `FOAM FATAL` and no OOM, matched that signature to the
stdin-`SIGKILL` launch defect of §6.3, and **was about to order a relaunch of all
five.** He was reading a deliberate act as an accident, because from the process
table the two look identical.

**What separated them was the launcher's `EXIT` trap, which cannot run on
`SIGKILL`:**

| | `.rc.<RUN>.launcher` | `launch.<RUN>.out` | reading |
|---|---|---|---|
| S2, S3, T2, T4, W30 | **exists, `0`** | `launcher exit rc=0` | trap FIRED → catchable signal → the deliberate `SIGTERM` halt |
| S1 | absent | — | still running; trap has not fired |
| the earlier stdin defect | **absent everywhere** | **empty** | `SIGKILL` — *the failure produced no evidence of itself* |

**The trap had been added an hour earlier for an unrelated reason** — to stop a
different defect from dying silently. It is what refuted the recurrence of its
own defect. That is the whole argument for building instruments into
infrastructure, and it is recorded as **`L-432`**.

---

## 4. S1 — **COMPLETED IS NOT VALIDATED**

S1 was allowed to finish. **It is `DONE` on the completion rule and it is NOT a
graded physics row, and the limitation was registered BEFORE it completed**, at
`verification/runs/T-family/T25R3_MODULE_runs/S1/LIMITATION.S1.txt`, on the
supervisor's ruling 2. Written afterwards it would have been an excuse.

**S1's own pressure equation is the least solved of the three** (0.4 GAMG
iterations per solve), so **every pressure-dependent quantity it produces carries
the defect**: Q0, Q1, Q2, the energy ledger and the mass balance all rest on a
velocity field from a pressure equation that was not solved.

> **S1 MAY BE CITED FOR COST, FOR COMPLETION-MACHINERY EVIDENCE AND AS THE
> CONTENTION CONTROL. IT MAY NOT BE CITED FOR A TEMPERATURE, A FLUX, AN ORDER, A
> BAND OR A GATE.**

What it is genuinely worth:

1. **The completion path ran end to end for the first time** — two chained legs
   (leg A finished exactly at `Time = 70.00000000000321`, 3,500/3,500 steps),
   the `controlDict` swap, `reconstructPar -allRegions`, rule 4's six conjuncts
   across both legs including the age guard, and `mark_done_t25R3.py`.
2. **A measured rate to price T25R4 from** — 0.1988 s/step at 2 ranks on L1 at
   `nOuterCorrectors 15`. **The cost model was right (×1.02) exactly where the
   pressure solve behaved**, which is itself evidence that the model's failure
   above L1 is the numerics defect and not a bad model.

---

## 5. COST — rule 12

| run | leg A `ExecutionTime` (s) | leg B (s) | core-min | POINT | ratio | cap | % of cap |
|---|---|---|---|---|---|---|---|
| S1 | 643.78 | *(running at writing)* | 22.73 | 76.2 | 0.298 | 305 | 7.5 % |
| S2 | 263.99 | — | 8.80 | 171.5 | 0.051 | 686 | 1.3 % |
| S3 | 250.99 | — | 8.37 | 385.8 | 0.022 | 1,543 | 0.5 % |
| T2 | 260.99 | — | 8.70 | 342.9 | 0.025 | 1,372 | 0.6 % |
| T4 | 258.52 | — | 8.62 | 685.9 | 0.013 | 2,744 | 0.3 % |
| W30 | 250.68 | — | 8.36 | 313.8 | 0.027 | 1,255 | 0.7 % |
| **TOTAL** | | | **65.57** | **1,979.1** | **0.033** | **7,916** | **0.8 %** |

**Dollars $0.0561 — DERIVED, NOT MEASURED**, at $0.0513/core-h,
`cost_basis = REPORTED-BY-OWNER`; this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5).

**ATTRIBUTION — this is a MISPREDICTION, and it is named as one.** The POINT
extrapolated T25R2's measured L1 rate **linearly in cell count**. That
extrapolation was invalid because per-step cost is dominated by a pressure solve
whose iteration count jumps from ~0 to ~382 across the ladder. **The cost model
was not merely optimistic; it was measuring a solver that was not running.**

**WASTE, NAMED SEPARATELY AND NOT ABSORBED INTO THE RATIO** (`COMPUTE_BUDGET`
§6). Three launch attempts aborted before the surviving fleet, each consuming a
few core-minutes: the `set -u` death, the stdin-`SIGKILL` death, and the
core-binding fleet. **Their total is small (order 10 core-min) and it is real,
and it is this lane's, not the box's.**

**THE HALT IS WHY THIS RUNG COST 65.57 CORE-MINUTES INSTEAD OF 7,916.**

---

## 6. THE THREE INFRASTRUCTURE DEFECTS FOUND, AND THE ONE THAT IS LAB-WIDE

### 6.1 ⚡ `mpirun` BINDS FROM CORE 0 — **`L-431`, AND IT IS NOT ABOUT THIS RUNG**

**Every independent `mpirun` numbers cores from zero.** Six concurrent
`mpirun -np 2` jobs therefore pinned **all twelve ranks to CPUs 0 and 1 — six
processes per core — while cores 2–7 and 9–15 sat 100 % idle.** Measured with
`taskset -pc` (`allowed_cpus = 0` or `1` on every rank) and `mpstat -P ALL`, not
inferred. `--bind-to none` fixes it and **changes no number**: rank count,
decomposition and arithmetic are identical, so only wall time moves.

> **THIS IS A FACT ABOUT EVERY CONCURRENT-`mpirun` CAMPAIGN IN THIS LAB, NOT
> ABOUT T25R3.** The symptom reads as a slow solver, which is why nobody finds
> it, and **Sanaa's 80–90 % utilisation directive is unreachable for any campaign
> that misses it** — the box reports a high load average while most cores idle.

### 6.2 `ps -o comm` TRUNCATES AT 15 CHARACTERS — a false zero that did damage

`chtMultiRegionFoam` is 18 characters, so it never matched, and the count read
**zero while twelve ranks were running.** This lane believed that zero and
**deleted case directories out from under a live fleet**, then launched a second
fleet on top; both competed until they were killed. Nothing was lost — no run had
gradable output and all six were restaged and re-verified — but the reader was
wrong and the belief was acted on.

`pgrep -f <pattern>` has the mirror defect: **it matches the matcher's own
command line** and reports phantoms after everything is dead.

**`readlink /proc/<pid>/exe` neither truncates nor self-matches, and a
known-live process was PLANTED in the target directory to prove the reader could
see a non-zero before its zero was trusted.** `CLAUDE.md` rule 3 is usually read
as a rule about comparators. **It is a rule about any zero, process counts
included.**

### 6.3 A launcher that dies silently is worse than one that dies

The first launcher carried `set -u` and sourced the OpenFOAM bashrc as
`. bashrc >/dev/null 2>&1`. The bashrc references unset variables, `set -u`
killed the shell inside it, and **the redirect swallowed the message**: six runs
exited in under two seconds leaving an empty log and no rc file. Two defects, and
**the second is the worse one, because the failure produced no evidence of
itself.** The `EXIT` trap added in response is what later refuted the
supervisor's misdiagnosis (§3.1).

A third: the guard glob `[0-9]*` **matches `0.orig`**, so it refused every
freshly staged case for a time directory that did not exist. **A guard that fires
on a clean case is not strict, it is broken — and it would have been "fixed" by
deleting the guard.**

---

## 7. WHAT T25R3 DOES **NOT** SAY

1. **It does not say the physics is wrong.** No physics was evaluated.
2. **It does not say the mesh family is wrong.** The 24/36/54 family is built,
   `checkMesh`-clean on all three levels, at exactly r = 1.5, and is reusable.
3. **It does not say the ramp, the time-step schedule, the field tuple, the
   decomposition or the comparator are wrong.** All were verified (192 checks,
   0 FAIL) and all carry forward.
4. **It does not vindicate T25R2.** T25R2 remains `NOT A RESULT` on its own
   registered terms, and its L1 numbers carry this same absolute-tolerance defect.
5. **It produces no observed order, no GCI and no Roache classification.**

---

## 8. ARTIFACTS

- registration + A1 + D1: `docs/campaigns/T-family/T25R3_PREREGISTRATION.md`
- S1's limitation, registered before completion:
  `verification/runs/T-family/T25R3_MODULE_runs/S1/LIMITATION.S1.txt`
- staging verification, 192 checks 0 FAIL:
  `.../T25R3_MODULE_runs/VERIFY.T25R3.txt`
- run trees (out of git, as T25R2's are): `.../T25R3_MODULE_runs/{S1,S2,S3,T2,T4,W30}/`
  — `log.solve.legA`, `log.solve.legB`, `log.decomposePar`, `.rc.*`,
  `LAUNCH_CONTEXT.*.txt`
- comparator + marker: `.../analyse_t25R3.py`, `.../mark_done_t25R3.py`
- lessons: **`L-431`** (mpirun core binding), **`L-432`** (a halt and a crash
  leave identical artefacts)

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).

---

## 9. THE SUCCESSOR — **T25R4, A NEW REGISTRATION, AND §16 STAYS CLOSED**

The fix is a **numerics** change. §4.1 registers the `p_rgh` tolerance and §16
closed the gates at first compute, so **it cannot land as an addendum.**

The supervisor's ruling 3 fixes the shape of the fix and this lane records it
rather than re-deciding it:

- **A MESH-INDEPENDENT PRESSURE CRITERION** — the final pressure solve must
  reduce the initial residual by a **FIXED FACTOR** on every level, with an
  absolute floor beneath it, so the same convergence standard applies at every
  mesh density.
- **NOT a tighter absolute tolerance**, which would make the fine levels costlier
  while **leaving the coarse level still unsolved** — the defect inverted rather
  than repaired.
- **THE VERIFICATION OF THE FIX IS REGISTERED, NOT JUST THE FIX**: mean GAMG
  iterations per step must be **comparable across the three levels**, checked on
  a **short probe as a PRE-COMPUTE acceptance gate**. If they still differ by an
  order of magnitude the criterion is still mesh-dependent and **the ladder does
  not launch.** *A fix whose success is only observable after the expensive run
  is not a fix this lab can afford twice.*
- **NO WALL-CLOCK PRESSURE.** Act C shows the honest-refusal act today, so T25R4
  is registered properly rather than fast.

<!-- END OF T25R3 RESULTS v1.0 -->
