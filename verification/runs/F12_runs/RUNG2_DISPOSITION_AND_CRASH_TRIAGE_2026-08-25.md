# F12 — RUNG 2 DISPOSITION, A CORRECTION AGAINST MY OWN RULING, AND THE RUNG-1 CRASH TRIAGE

**Written by the cfd supervisor personally, 2026-08-25.** Crash triage is a
`SUPERVISION_CHARTER.md` §3 check and may not be delegated. `[lab-attributed]`
under Sanaa's desk-item disposal rule of this date; **overrulable**.

Evidence: `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/RESULTS_RUNG2_ATTEMPT.md`
(committed `fd7a5b70`), and rung 1's own `RC.txt` and `grade.json` read from disk.

---

## 1. RUNG 2 — `BLOCKED`. THE INTERLOCK WINS AND MY RULING DOES NOT OVERRIDE IT.

`launch_f12_rung.py`'s `rate_calibration_gate()` refused rung 2 on its own,
unmodified, before `compose_case()` and before any compute. Three conjuncts
failed: rung 1's `rc = 134, not 0`; all six completion limbs `false`; `not
complete`. Corroborated at source — rung 1's `RC.txt` holds `134` and its
`grade.json` carries `complete: false`.

**The refusal is correct and I am upholding it.** It encodes frozen §5's ordering:
*the measured rate replaces both estimates before rungs 2-5 are considered.* Rung 1
never produced a measured rate, so the condition §5 sets has not been met.

**Three reasons, and the third is the one that binds hardest.**

1. **My ruling could not have overridden it even if I had wanted it to.** F12 rung 1
   has fired, so §2d is live and gates are closed. §5's ordering is part of the
   frozen instrument, and a post-compute ruling cannot alter it — that is standing
   rule 2, and it is not discretionary.
2. **My ruling says so in its own terms.** `F12_GATE_B_RULING_2026-08-25.md` §6:
   *"It is a scheduling and reading ruling and nothing wider — standing rule 9."*
   A scheduling ruling schedules within the frozen ordering; it does not reorder it.
3. **Opening the interlock needs launcher BYTES changed.** Editing a launch or
   measurement instrument so that it stops refusing is the precise move this team
   has already ruled against in another costume — C1.3, `MESH_STANDARD.md` §8.2:
   *a refusal from the tool whose job is to refuse is a DIAGNOSTIC, not an obstacle
   to route around.* **A generator that cannot refuse is a generator with no second
   opinion in it**, and an interlock that can be edited when it fires is not an
   interlock. The lane wrote no diff and stopped. **That was the right call and I
   am recording it as the right call**, so the next lane does not read stopping as
   under-performance.

## 2. A CORRECTION AGAINST MYSELF, AND IT IS THE USEFUL PART OF THIS RECORD

**My gate-B ruling was correct and was NOT the binding constraint. I did not see
that when I wrote it, and the lane found the boundary.**

I ruled at length on whether rung 2 *should* fire on gate-B grounds, and answered
yes. That analysis stands untouched — the mechanism objection really is dismissed,
the multiplicity correction really does hold, and S17 came out of it. **But rung 2
was never gated on gate B.** It was gated on §5's rate calibration, upstream of
everything I examined. I ruled on a live question that was not the blocking one.

**The lesson, and I am naming it against myself rather than filing it as a
near-miss: I reasoned about the gate a run would eventually meet, without first
establishing what was actually stopping it TODAY.** The interlock was readable in
the launcher the whole time. **Triage the blocker you have before you rule on the
gate you expect.**

## 3. THE CRASH TRIAGE — rung 1's `rc = 134`

A crash is a finding about the case, the method or the toolchain **until triage
demonstrates otherwise** (§3 check 2). `rc = 134` is `128 + 6` — **`SIGABRT`**,
consistent with a floating-point trap raising `abort()`.

### 3.1 What is already established, and what is NOT

**Established.** The `transonic` hypothesis is **REFUTED** by arm B′: with the
pressure equation actually solving, the run is **600x worse**. The `N-C` numerics
row on GAMG registration was **refuted from source and must not be landed** — GAMG
is registered for both symmetric and asymmetric matrices, and an unregistered
solver raises a **selection-time error, not an FPE**.

**What arm B established is narrower and must be quoted narrowly:** GAMG failed
with an FPE **in its coarsest-level solve, on that asymmetric matrix**. **Why is
not established.** Three of the last four mechanism claims on this line have been
corrected, twice from source. The honest position is that the mechanism is open.

### 3.2 THE NEW EVIDENCE, and it changes the direction of the search

The rung-2 lane applied its validated first-solve reader to rung 1's truncated
log (`rung1_first_solve_reference.json` — it grades nothing and is not the stable-run
measurement, but it is a legitimate diagnostic):

> **First-solve `p` never got below `9.5548e-03`, at iteration 5. It was RISING at
> the abort. Median q4/q3 = 1.399.**

**Read that plainly: rung 1 was DIVERGING, from about iteration 5, and it never
converged at any point in its life.** It did not descend and then blow up. It
never descended.

### 3.3 MY TRIAGE CONCLUSION — the FPE is downstream, not upstream

**The FPE is a SYMPTOM of an outer iteration that was already diverging, not an
independent defect of the linear solver.** A coarsest-level GAMG solve that traps
on a matrix assembled from a field that has been rising for tens of iterations is
doing the expected thing with garbage input. **"Why did GAMG FPE" is very likely
the wrong question, and it is the question every arm so far has asked.**

Stated as a falsifiable claim rather than a story: **if the outer iteration were
made to descend, the FPE would not occur** — and if it still occurred on a
descending run, my triage is wrong and the linear solver is implicated after all.
That is the test.

### 3.4 THE NEXT PROBE — and it is deliberately NOT another lever swap

My predecessor lane declined to propose the next arm, on the stated ground that
*three of my last four messages have corrected a mechanism, and the next move
should follow your triage rather than my guess.* **That was right and I am
honouring it.** The next probe follows from §3.3 and from nothing else.

> **Stop asking why the linear solve traps. Establish WHERE IN THE DOMAIN the
> field first goes wrong, and WHEN.**

Concretely: write **every** field at **every** iteration for the first ~15
iterations of rung 1 and locate, spatially, the cell or patch where `p` first
departs. Every arm to date has swapped a solver, a scheme or a relaxation — a
lever — and read a scalar residual afterwards. **No arm has yet LOOKED AT THE
FIELD.** A residual is a single number summarising a whole domain; it cannot tell
you whether the problem is a boundary, a corner, the far field, the trailing edge
or the whole flow, and those have entirely different fixes.

**Why this is the highest-value next step even though it grades nothing:** it
discriminates between hypothesis classes that no residual can separate, at trivial
cost (~15 iterations), and it is the only probe on the table whose outcome is not
already predictable from what we know. **A localised departure indicts a boundary
condition or the mesh at that location. A global one indicts the initial state or
the relaxation. Either answer eliminates most of the remaining search space.**

**What it must NOT do:** change a solver, a scheme, a relaxation factor, a
tolerance or any registered value. It is an **observation** arm. If it cannot be
run without changing a lever, that fact is itself the finding and it comes back to
me unchanged.

## 4. STANDING OF THIS RECORD

Rung 2 is **`BLOCKED`** — not `PENDING`, not `GATE FAIL`. Nothing ran, no gate was
read, the cap is unconsumed at **0 of 160 core-min**, **waste zero** (the refusal
preceded compute). Rung 1 stands **`NOT A RESULT`** and is not regraded here.
Rungs 3-5 remain unlaunched and were asserted **absent before and after**. No
frozen file was edited and no gate, threshold, cap or label moves.

**A debt carried forward, named because it binds any future rung-2 firing:**
`scripts/roache_triple.py` is **still not pinned**, and the launcher's own
docstring records it as owed before rungs 2-5 — where the triple is the graded
object.

---

## AMENDMENT 1 — 2026-08-25 — **§3's MECHANISM IS STRUCK. RUNG 1 WAS NEVER AN FPE.**

**Written by the cfd supervisor personally.** Crash triage is a `SUPERVISION_CHARTER.md` §3
check 2 and may not be delegated; this correction was **verified by me at source**, not relayed.
**Lines whose number changed above this section: 0.** The original text above is preserved
exactly as written, not rewritten (standing rule 6).

**Found by the field-localisation lane and confirmed independently by me.** Credit where it
belongs: the lane read the log to its end. I had not.

### WHAT ACTUALLY KILLED RUNG 1

`verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/log.rhoSimpleFoam` ends:

```
--> FOAM FATAL ERROR: (openfoam-2606)
Negative initial temperature T0: -2.384321367
    ... in file ./src/thermophysicalModels/specie/lnInclude/thermoI.H at line 57.
```

The last solve before it is `Solving for e` — **the energy equation**. The pressure equation had
not run that iteration.

**At source**, `/usr/lib/openfoam/openfoam2606/src/thermophysicalModels/specie/thermo/thermo/thermoI.H`
lines 54-60:

```
    if (T0 < 0)
    {
        FatalErrorInFunction
            << "Negative initial temperature T0: " << T0
            << abort(FatalError);
    }
```

**That is an explicit physical range check, not a floating-point trap.** The stack trace's frame
#1 is `Foam::error::simpleExit` in `libOpenFOAM.so`; frames #2-#4 are
`libfluidThermophysicalModels.so`. **GAMG is not on the stack.**

**And the exit code says so too.** `kill -l 6` = `ABRT`, `kill -l 8` = `FPE`. `rc = 134` is
`128 + 6` = **SIGABRT**. **A SIGFPE would have been 136.**

### WHAT IS STRUCK, AND WHAT SURVIVES

**STRUCK — §3 heading and §3.3's mechanism.** §3 reads *"`rc = 134` is `128 + 6` — `SIGABRT`,
consistent with a floating-point trap raising `abort()`."* §3.3 reads *"A coarsest-level GAMG
solve that traps on a matrix assembled from a field that has been rising for tens of iterations
is doing the expected thing with garbage input."* **There was no trap and GAMG was not involved.
Both sentences are withdrawn as statements about rung 1.** They remain true of **arm B**, which
is a different case.

**MY OWN ERROR, NAMED: I read an exit code permissively when the log carried the answer in plain
text.** `128 + 6` is *consistent with* an FPE-induced abort, and it is also consistent with every
other `abort()` OpenFOAM raises — which is most of them. I chose the reading that fitted the
story the previous arms had been telling. **The log's last twenty lines would have refuted it at
any point.** This is the **fourth** corrected mechanism claim on this line and **the first that
is mine**.

**SURVIVES, AND IS STRENGTHENED — §3.3's CONCLUSION and §3.4's DIRECTION.**

§3.3 concluded that the crash is **downstream of an outer iteration that was already diverging**,
not an independent defect of the linear solver. That is now on **firmer** ground, not weaker:
`T = -2.384321367 K` is unambiguous divergence of the solution itself, and the thing that caught
it is a **physical bound on a field**. The corroborating residual reading is unchanged and was
re-derived independently from the log: first-solve `p` minimum **`0.009554815904` at iteration
5**, rising to **`0.2006112477` by iteration 10**.

§3.4 ruled: *"Stop asking why the linear solve traps. Establish WHERE IN THE DOMAIN the field
first goes wrong, and WHEN."* **That direction is now more clearly right than when it was
written** — the failing quantity is a field, the killer is a physical range check on that field,
and "why did GAMG FPE" turns out never to have been rung 1's question at all.

### CONSEQUENCE FOR THE FALSIFIABLE TEST IN §3.3

§3.3 offered: *"if the outer iteration were made to descend, the FPE would not occur — and if it
still occurred on a descending run, my triage is wrong."* **Restate it without the FPE:** if the
outer iteration were made to descend, `T` would not go negative; if `T` still went negative on a
descending run, the triage is wrong. **The test is unchanged in substance and its subject is
corrected.**

Full verification and the probe that found it: the field-localisation registration
`verification/campaign/F12_FIELD_LOCALISATION_PREREGISTRATION.md`, frozen `56d72ac3`, blob
sha256 `bca4074a7de26f478115a1efc1706c9cba6daedab8174cf72c202566d534b667` — **recomputed by me
from the commit object, not accepted from the lane.**
