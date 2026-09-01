# T25R2 — RESULTS: **THE OUTER-LOOP GATE IS `GATE FAIL`, AND EVERY ROW OF THE RUNG IS `NOT A RESULT`**

**Written 2026-09-01T06:10Z by a heat-transfer `lab-lane`.**
Registration: `docs/campaigns/T-family/T25R2_PREREGISTRATION.md`, frozen at
**`bb6e5761`**, Amendment A1 at **`227240b5`**, Addenda B1/B2 at **`51f56095`**
/ **`1810973d`**. Grading path fixed at the freeze; the comparator hashes the
document against the committed blob and refuses on a mismatch.

Verdict vocabulary is `CLAUDE.md` rule 1's and is used nowhere loosely.

---

## 1. THE VERDICT, IN ONE LINE

> **§3.5's outer-loop gate — demonstrated sweep-count independence in kelvin —
> is `GATE FAIL` on O3. Under the propagation registered at §3.5.4 before any
> compute, EVERY ROW OF THIS RUNG IS `NOT A RESULT`.**

**This is a real finding, not an instrument failure.** The arm was registered so
that it could fail, the threshold was frozen before the answer existed, and the
answer is no. **`T25R2_L1` and `T25R2_L1_OC20` are both complete, `rc = 0`, and
`DONE` on all six conjuncts of rule 4** — they did not crash, they were not
capped, and nothing about them is broken. **The runs are sound and the numbers
they produced are not sweep-count independent, which is a different thing and is
the thing this rung was built to find out.**

---

## 2. THE THREE REGISTERED DELTAS, AS MEASURED

`Δ(X) = |X(T25R2_L1_OC20, 20 sweeps) − X(T25R2_L1, 10 sweeps)|`, both L1, both
`deltaT 0.5`, **identical in every other respect** — same mesh (byte-identical,
proved sha256-for-sha256 at staging), same loads, same relaxation, same
tolerances.

| id | quantity | measured | threshold | verdict |
|---|---|---|---|---|
| **O1** | max \|ΔT\| over all 8 solid cells and every written `t > 0` | **1.199542e-03 K** (cell 7, t = 300 s) | ≤ 1.234e-02 K (10×PLANT) | **PASS**, by a factor of **10.3** |
| **O2** | Δ of the **D3 quantity**, `min_i[T_dn−T_up]` at t = 60 s | **6.675809e-04 K** (0.040833398 → 0.041500979 K) | ≤ 1.234e-03 K (1×PLANT) | **PASS**, by a factor of **1.85** |
| **O3** | max \|Δ\| of the **coolant outlet** area-mean `T` over `t ∈ {60, 900 s}` | **2.315190e-02 K** (at t = 60 s) | ≤ 1.234e-02 K (10×PLANT) | **`GATE FAIL`**, over by a factor of **1.88** |

**All three were required. One failed. The gate fails.**

### 2.1 THE FAILURE IS LOCALISED, AND THE LOCALISATION IS THE USEFUL PART

The coolant outlet delta over **every** written time, not only the two O3
samples:

| t (s) | 10 sweeps | 20 sweeps | \|Δ\| | vs 1.234e-02 K |
|---|---|---|---|---|
| 30 | 293.360042142 | 293.384084474 | **2.404233e-02** | **1.95× OVER** |
| 60 | 293.748543957 | 293.771695855 | **2.315190e-02** | **1.88× OVER** |
| 120 | 293.909361233 | 293.913765493 | 4.404260e-03 | under |
| 300 | 294.279392127 | 294.283114631 | 3.722504e-03 | under |
| 900 | 295.074737853 | 295.076744208 | 2.006354e-03 | under |

**The coolant outlet is sweep-count dependent ONLY DURING THE 60 s TAKEOFF
PULSE, and converges to well inside the threshold once cruise is established.**
By t = 900 s it is 2.0e-03 K — a sixth of the threshold.

The solid, over the same times, passes everywhere:

| t (s) | 30 | 60 | 120 | 300 | 900 |
|---|---|---|---|---|---|
| max \|ΔT\| solid (K) | 5.208e-04 | 9.965e-04 | 1.056e-03 | 1.200e-03 | 1.061e-03 |

> **THE SOLID IS SWEEP-COUNT CONVERGED. THE COOLANT OUTLET IS NOT, DURING THE
> PULSE.** That is physically coherent rather than surprising: the outlet mean
> responds on the channel residence time (`L/U = 31.25 ms`) to a source that is
> large and about to step, while the solid responds on `τ ≈ 696 s`. At
> `Co ≈ 1600`, ten outer sweeps do not resolve the fluid's response to the
> strong part of the transient. **Nothing here says the answer is wrong; it says
> the answer still moves when an arbitrary iteration count is doubled, which is
> exactly what §3.5 was written to detect.**

### 2.2 THE AMENDMENT A1 REPORT — **NO THRESHOLD, NOT A GATE**

At t = 30 s the 10-vs-20 solid gap is **5.208319e-04 K**, against the T25RF
probe's **measured 5-vs-10 gap of 6.02e-03 K** at the same instant, on the same
mesh, the same loads and the same relaxation.

**SMALLER by a factor of 11.6 — the sequence 5 → 10 → 20 is visibly converging
at t = 30 s.** That is why A1 was added: a bare pass/fail could not have said
whether 10 and 20 were converging together or merely sitting close. **It is a
report, it gated nothing, and it did not contribute to the verdict.**

---

## 3. WHAT IS `NOT A RESULT`, AND WHY EACH

| row | verdict | why |
|---|---|---|
| `T25R2_L1` physics (D1/D2/D3, §6.2 energy) | **`NOT A RESULT`** | §3.5.4 propagation; `CLAUDE.md` rule 5 clause (1) — a level not iteratively converged is `NOT A RESULT` whatever its value says |
| `T25R2_L1_OC20` physics | **`NOT A RESULT`** | same |
| mesh-sensitivity panel | **`PENDING`** | both arms must be graded; neither is |
| step-sensitivity panel | **`PENDING`** | `T25R2_L2_DT025` has not run |

**NO PHYSICS NUMBER WAS PRINTED.** The comparator withheld D1, D2, D3, the
energy ledger and every per-cell temperature — verified in its own output: the
string `D1 (T_dn > T_up` does not appear. **The planted-zero controls were not
even reached**, because §3.5 is evaluated before any reader is admitted.

**Completion is untouched by the gate.** Both arms are `DONE`:

| | `T25R2_L1` | `T25R2_L1_OC20` |
|---|---|---|
| rc, **recorded not inferred** | 0 | 0 |
| `End` / `FOAM FATAL` | 1 / 0 | 1 / 0 |
| last time | 900 | 900 |
| `ExecutionTime` count | 1800 == registered | 1800 == registered |
| fields, both regions | complete | complete |
| age guard, tightest over **all 181 times, both regions** | +15.957 s | +18.873 s |

---

## 4. COST — rule 12

| run | POINT | actual (solver core-min) | ratio | cap | used |
|---|---|---|---|---|---|
| staging + verify | 0.50 | **0.017** | 0.034 | 2 | 0.9 % |
| `T25R2_L1` | 8.30 | **7.148** | **0.861** | 34 | 21.0 % |
| `T25R2_L1_OC20` | 18.09 | **12.615** | **0.697** | 73 | 17.3 % |
| **spent so far** | 26.89 | **19.780** | **0.736** | **390** | **5.1 %** |

**370.2 core-min unspent.** Dollars **$0.0169**, **DERIVED, NOT MEASURED**, at
$0.0513/core-h, `cost_basis = REPORTED-BY-OWNER`.

**ATTRIBUTION — misprediction, conservative direction, cause measured.** The
POINT priced the sweep doubling at **×2.18**, taken from the probe's A1→A2 pair,
which **still carried the `p_rgh` stall** the registered 1e-8 tolerance removes.
The measured factor is **12.615 / 7.148 = ×1.765**, and on the like-for-like
cruise branch **0.4044 / 0.2285 = ×1.77**. **Doubling the sweeps costs 1.77×,
not 2.18×, once the stall is gone** — the sub-linear part being the per-step
work that is not per-sweep. **Waste: 0 core-min.** Contention bounded, not
measured, not subtracted.

---

## 5. WHAT THIS RUNG DOES **NOT** SAY

1. **It does not say the physics is wrong.** It says the reported quantity moves
   by 1.9× the registered tolerance when an arbitrary iteration count doubles.
2. **It does not say 20 sweeps is right either.** Twenty is the second point of a
   two-point comparison, not a converged answer.
3. **It produces no observed order, no GCI and no Roache classification** — and
   `T25R2_L1_OC20` is **not** a third mesh level. No order may be read from the
   L1 / L1_OC20 collection under any pretext.
4. **It inherits no `PASS` from T20**, which remains `NOT A RESULT` on its own
   registered terms.
5. **It says nothing about L2**, which has not run. §3.5.5's asymmetry is what
   makes the L1 failure decisive: a `PASS` at `Co ≈ 1600` would not have
   certified L2 at `Co ≈ 2400`, but a **failure** at 1600 does transfer upward.

---

## 6. THE LAB'S RECOMMENDATION — **HALT `T25R2_L2` AND `T25R2_L2_DT025`**

**They are staged and verified and they should not be launched under this
registration.** §3.5.4's propagation was frozen before any compute and makes
**every row of this rung `NOT A RESULT`**. Both L2 arms run at `nOuterCorrectors
10`, at a **higher** Courant number where the outer loop converges no faster.
**Their verdict is already registered, before they run, as `NOT A RESULT`.**

- POINT cost of running them anyway: **56.03 core-min** (18.68 + 37.35); at hard
  cap, **281**.
- What they would produce: nothing gradeable. Both sensitivity panels require
  two **graded** arms and would print `PENDING` regardless.

**Spending 56 core-min to produce rows whose verdict is pre-determined is waste
by construction, and rule 12 names waste rather than absorbing it.** *Idle
compute is a failure; so is compute that cannot produce a result.*

**THE DECISION IS THE SUPERVISOR'S, NOT THIS LANE'S.** It is recorded here as a
recommendation with its arithmetic.

## 7. THE SUCCESSOR — WHAT THE MEASUREMENT POINTS AT, PRICED, AND **NOT REGISTERED**

The failure is **localised to the coolant outlet during the 60 s pulse** (§2.1),
so the levers the data actually supports are:

1. **more outer sweeps** — L1 at 20 sweeps measured **12.615 core-min**, so a
   40-sweep arm prices at roughly **22 core-min** on the measured ×1.77;
2. **a finer `deltaT` through the pulse only**, which the registered 1 ms ramp
   placement constrains (§4.4: a `deltaT` finer than 1 ms would sample the ramp
   and must revisit the breakpoints);
3. **O3 covering every written time**, not the two instants §3.5.4 registered —
   t = 30 s is measurably **worse** (2.404e-02) than the t = 60 s sample that
   fired the gate. The registered gate caught the failure; it did not catch it
   at its worst point, and a successor should widen O3 to O1's coverage.

**L3 stays refused** (§8.6) and **an L2 outer-loop arm stays refused** (§8.5).
**None of this is registered. A successor rung freezes its own pre-registration
and runs again** — and it can now be priced off T25R2's **own measured** rates
rather than a borrowed or probe-extrapolated one.

---

## 8. ARTIFACTS

- comparator output: `verification/runs/T-family/T25R2_MODULE_runs/OC_GATE.json`
- completion records: `.../T25R2_L1/COMPLETION.T25R2_L1.txt`,
  `.../T25R2_L1_OC20/COMPLETION.T25R2_L1_OC20.txt`
- run trees (out of git, as `T25R_MODULE_runs`' are):
  `/home/ubuntu/Certonomous/verification/runs/T-family/T25R2_MODULE_runs/T25R2_L1{,_OC20}/`
  — `log.solve`, `STATUS.*`, `.rc.*`, `postProcessing/`, 181 time directories each
- launch contexts: `.../LAUNCH_CONTEXT.T25R2_L1{,_OC20}.txt`

**SUBMISSIONS PARKED** (rule 7). **Permanently private** (rule 8).

<!-- END OF T25R2 RESULTS v1.0 -->

---

## 9. THE HALT — **A DELIBERATE, RULED DECISION, NOT A SILENT OMISSION**

*Appended 2026-09-01T06:20Z. Results document v1.1. §6 above was this lane's
RECOMMENDATION; this section is the SUPERVISOR'S RULING and the record of the
decision as taken.*

**`T25R2_L2` AND `T25R2_L2_DT025` WERE NOT RUN. THE REGISTRATION NAMED FOUR RUNS
AND TWO OF THEM WERE DELIBERATELY NOT LAUNCHED.** A successor reading this record
must find the reason here rather than a gap, so it is stated in full.

### 9.1 ⛔ THIS IS NOT A CAP STOP, AND THE NUMBERS SAY SO

| | core-min |
|---|---|
| registered HARD CAP, all four runs + staging | **390** |
| **spent** | **19.780** |
| **UNSPENT** | **370.2 — 94.9 % of the cap** |

**No run was capped. No run reached its `timeout_s`. `capped=no` and `rc=0` on
both arms.** Rule 12's cap-stop machinery was never engaged and this halt must
not be read as one.

### 9.2 THE THREE GROUNDS, IN THE ORDER THAT DECIDES THEM

1. **L2's rows are ALREADY `NOT A RESULT`, by registered propagation, before any
   decision was taken.** §3.5.5's transfer is **asymmetric and was frozen that
   way before compute**: a `PASS` at `Co ≈ 1600` would **not** have certified L2
   at `Co ≈ 2400`, but a **`GATE FAIL` does** void it — the failure direction
   transfers. Both L2 arms run at **`nOuterCorrectors 10` at a higher Courant
   number**, where the outer loop converges no faster.
2. **Both sensitivity panels require two GRADED arms** (§6.3) and would print
   `PENDING` whatever L2 produced.
3. **56.03 core-min POINT, producing nothing gradeable.** *Idle compute is a
   failure; so is compute that cannot produce a result.* **The second half of
   that is the half that gets forgotten.**

### 9.3 ⚠ HALTING CHANGES NO VERDICT

**Every row of this rung was `NOT A RESULT` the moment O3 failed**, by a
propagation registered at §3.5.4 **before any compute and before this decision
existed**. Running L2 would have produced two more `NOT A RESULT` rows and two
`PENDING` panels. **The halt saves compute; it does not change a single
verdict, and no verdict in this document rests on it.**

**The two cases remain STAGED AND VERIFIED on disk** — mesh proved byte-identical
sha256-for-sha256, cell counts, gap resolution, interface faces and numerics all
measured before solving (`MESH_VERIFICATION.txt`). They are **not** deleted: a
successor may reuse the staging, and destroying it would destroy the verification
record with it.

---

## 10. ⚠ MUST-FIX BEFORE ANY SUCCESSOR CAN GRADE D2 AT ALL

**THIS RUNG HAD TWO INDEPENDENT BLOCKERS AND ONLY ONE OF THEM FIRED**, because
§3.5 is evaluated before any reader is admitted.

The second is Addendum B3.2: `read_patch_T` accepts **only** a
`nonuniform List<scalar>` patch entry and **REFUSES** anything else, expressly
declining to fall back to `refValue` (§7.2). The real staged coolant inlet is
written by OpenFOAM as

```
    inlet { type fixedValue; value uniform 293; }
```

**So `read_inlet_T` REFUSES at every written time, and D2 — "outlet > inlet at
every written `t > 0`" — would have made this rung `NOT A RESULT` on an
INSTRUMENT REFUSAL even if the outer-loop gate had passed.**

> **A SUCCESSOR THAT FIXES THE NUMERICS AND NOT THE READER GETS A REFUSAL
> INSTEAD OF AN ANSWER.** This is not a curiosity to be filed; it is a
> **MUST-FIX**, and it must be fixed **in the successor's own comparator, under
> its own freeze**, before D2 is gradeable at all.

**It is NOT repaired here**, and the grounds are §2d.1's and B1.5's: the grading
path is frozen post-compute; conditions (3) and (4) presuppose published numbers
and **there are none**; the failure direction is a **REFUSAL**, which withholds
and cannot publish; and the defect is now **unreachable in this rung** because
§3.5 fails first.

**Root cause, sixth instance of the night's recurring class and this lane's
own:** `--selftest` forged the inlet patch **with** a `nonuniform` value list, so
the reader was never exercised against the form OpenFOAM actually writes for a
uniform `fixedValue`. **The fixture did not resemble the situation.**

---

## 11. THE LIMITATION OF A THRESHOLD THIS LANE CHOSE ITSELF

**§3.5.4 registered O3 as the maximum over `t ∈ {60, 900 s}` only, while O1
covers every written `t > 0`.** Measured across all five written times, the
coolant outlet delta at **t = 30 s is 2.404e-02 K — WORSE than the 2.315e-02 K at
t = 60 s that actually fired the gate.**

**The registered O3 caught the failure, but not at its worst point.** That is a
limitation of a threshold's *coverage* chosen by this lane, stated in the
document that reports its failure, because a limitation disclosed anywhere else
is disclosed too late. **A successor should give O3 O1's coverage.**

---

## 12. THE COST FINDING, WHICH IS A DELIVERABLE IN ITS OWN RIGHT

**Do not read this under the ratio.** §8.2's POINT priced the sweep doubling at
**×2.18**, taken from the T25RF probe's A1→A2 pair — which **still carried the
`p_rgh` stall** that the registered `1e-8` tolerance removes.

> **MEASURED: doubling the outer sweeps costs ×1.765 whole-run, and ×1.77 on the
> like-for-like cruise branch (0.4044 / 0.2285 core-s per step). NOT ×2.18.**

The sub-linear part is per-step work that is not per-sweep. **This is the number
a successor prices its sweep arms from**, and it is measured on this solver,
this mesh, these loads and these numerics rather than borrowed or extrapolated.

Confirmed alongside it, over the full 900 s where the probe could only see 30 s:
**36,000 `p_rgh` GAMG solves, 65,949 iterations, mean 1.83, ZERO at `maxIter`
1000** — the registered `1e-8` eliminates the stall across the whole run.

---

## 13. THE SUCCESSOR — PRICED, AND **NOTHING IS REGISTERED**

**NO SUCCESSOR IS STARTED AND NOTHING BELOW IS REGISTERED.** A successor freezes
its own pre-registration before any compute and runs again.

| lever | priced off T25R2's OWN measured rates | reading |
|---|---|---|
| **more sweeps** | L1 at 20 measured **12.615 core-min**, so 40 sweeps ≈ **22 core-min** at the measured ×1.77 | **⚠ NOT OBVIOUSLY ENOUGH.** The supervisor's reading, and this lane re-derived it: if the outer-loop error falls roughly as `1/n`, the 20→40 gap lands at **1.158e-02 K against the 1.234e-02 threshold — a ratio of 0.938. That is a coin toss, and it does not touch the cause.** |
| **a finer `deltaT` through the pulse alone** | to be priced by the successor | **THE MORE PROMISING LEVER.** It attacks the measured mechanism — the fluid's **31.25 ms** residence time against a large, about-to-step source at `Co ≈ 1600` — rather than throwing iterations at it. Constrained by §4.4: a `deltaT` finer than **1 ms** would sample the registered ramp and must revisit the breakpoint placement. |
| **O3 widened to O1's coverage** | free | §11 |
| **the D2 reader** | free | §10, **MUST-FIX** |

**L3 stays refused** (§8.6). **An L2 outer-loop arm stays refused** (§8.5).

<!-- END OF T25R2 RESULTS v1.1 -->

---

## 14. ADDENDUM — SANAA'S DIAGNOSIS OF THE O3 FAILURE, AND THE PRESCRIBED FIX

*Appended 2026-09-01 by a heat-transfer `lab-lane`. **Results document v1.2.***

**Lines whose number changed above this section: 0.** Verified, not assumed:
this addendum was appended at the foot and §§1–13 were compared line-for-line
against the committed blob before the commit — every line above this heading
holds the number it held at v1.1.

**⛔ THIS ADDENDUM CHANGES NO VERDICT.** §3.5's outer-loop gate remains
`GATE FAIL` on O3, and **every row of this rung remains `NOT A RESULT`** by the
propagation registered at §3.5.4 before any compute. Nothing below re-grades
anything or makes any withheld number quotable. This section records the
**diagnosis and the procedure for the successor**.

### 14.1 THE DIRECTIVE

Sanaa's directive of **2026-09-01 ~15:45Z**, captured verbatim at
`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`
(commit `f4c8e466`). Her header, which is lab law under her authority: *"Cost is
not a constraint. Every gated case runs its grid convergence study
automatically; a case without one is not a result."* Her **§2** responds to this
rung by name — *"BATTERY MODULE (Act C): the outlet temperature depends on sweep
count"*.

Her **§0** doctrine — the automatic convergence study as a pipeline stage on
every gated case — is set out in full at
`docs/campaigns/T-family/T23G_RESULTS.md` §11.1 and filed as **`L-429`** in
`docs/LESSONS.md`. Its operative clause for this rung is point 2: **the
iterative change in the graded quantity must be at least 10× smaller than the
difference between consecutive levels, or the observed order is noise rather
than discretisation.**

### 14.2 HER DIAGNOSIS, IN ONE LINE

> **"This is under-iteration inside each time step during the fast load
> change."**

**That is a diagnosis of the mechanism, and it is consistent with what §2.1
measured rather than a substitute for it.** This record found the failure
localised precisely to the 60 s takeoff pulse — 2.404e-02 K at t = 30 s and
2.315e-02 K at t = 60 s, both over the 1.234e-02 K threshold, falling to
2.006e-03 K by t = 900 s — and attributed it to the fluid responding on a
31.25 ms residence time to a source that is large and about to step, at
`Co ≈ 1600`. **Her diagnosis names the same window and the same cause, and adds
the term this record did not: the source is DISCONTINUOUS, and a discontinuous
source destroys time accuracy at the jump.**

### 14.3 THE PRESCRIBED FIX, IN FULL

| # | lever | prescription |
|---|---|---|
| 1 | **ramp the load** | replace the **step** at `t = 0` and `t = 60 s` with a **1 s linear ramp** — *"a discontinuous source destroys time accuracy at the jump"* |
| 2 | **PIMPLE** | `nOuterCorrectors` **3 → up to 15**, with **`residualControl` on `p`, `U`, `h` at 1e-7**, so each step converges **to a fixed tolerance rather than a fixed count**; `momentumPredictor` **on**; `nCorrectors` **2** |
| 3 | **time step** | `dt = 0.02 s` during the pulse window (`t < 70 s`), `0.1 s` after; **or** adaptive with `maxCo 0.5`. **"No fixed-count sweeps anywhere."** |
| 4 | **convergence study** | **three meshes** (channel cells **8 / 12 / 18**, wall layers scaled) **AND three time steps** (`dt`, `dt/2`, `dt/4`) on the middle mesh; observed order **in space and in time** |
| 5 | **the gate** | the **outlet temperature history and per-cell peaks** change by **less than the registered tolerance** between the **two finest levels of each ladder** |
| 6 | **loads** | volumetric, as ruled — **1e5 W/m³** pulse, **2.5e4 W/m³** cruise |

**Her Act C decision, recorded as taken:** *"run this fix now; if graded before
the demo, show it; if not, show the honest-refusal act (option a). Never show
the 0.4 K run."*

### 14.4 WHY LEVER 2 IS THE ONE THAT ANSWERS THIS RUNG'S GATE

**§3.5 detected that the answer moves when an arbitrary iteration count is
doubled. Her lever 2 removes the arbitrary count.** With `residualControl` on
`p`, `U` and `h` at 1e-7 and `nOuterCorrectors` as a *ceiling* of 15 rather than
a fixed 3 or 10, each time step converges to a **tolerance**, and the question
this rung failed — *"does the answer depend on the sweep count?"* — stops being
asked with an arbitrary number in it. **That is a change of kind, not a change
of degree, and it is why more-sweeps-at-a-fixed-count was never going to settle
it.**

**This confirms, from her side, the reading §13 reached from this rung's own
measurements.** §13 priced a 40-sweep arm at ≈22 core-min and called it **"⚠ NOT
OBVIOUSLY ENOUGH… a coin toss, and it does not touch the cause"** (the 20→40 gap
landing at 1.158e-02 K against a 1.234e-02 K threshold, ratio 0.938), and named
**"a finer `deltaT` through the pulse alone"** the more promising lever because
it attacks the measured mechanism. **Her §2 prescribes exactly that (lever 3),
plus the ramp (lever 1) and the tolerance-bounded outer loop (lever 2).** The
record's own reading and the directive converge; neither was derived from the
other.

**The §4.4 constraint still binds and the successor must not lose it:** a
`deltaT` finer than **1 ms** would sample the registered ramp and must revisit
the breakpoint placement. Her lever 1 changes the ramp to **1 s**, which relaxes
that constraint substantially — but the successor must **re-derive** the
breakpoints under the new ramp rather than inherit §4.4's numbers.

### 14.5 ⚠ WHAT HER §2 DOES **NOT** ADDRESS, AND WHICH REMAINS A MUST-FIX

**§10's blocker is untouched by any lever above, and it is the one that will
bite a successor that reads only this addendum.**

`read_patch_T` accepts **only** a `nonuniform List<scalar>` patch entry and
**REFUSES** anything else. The real staged coolant inlet is written by OpenFOAM
as `inlet { type fixedValue; value uniform 293; }`, so **`read_inlet_T` refuses
at every written time, and D2 would have made this rung `NOT A RESULT` on an
INSTRUMENT REFUSAL even if the outer-loop gate had passed.**

> **A SUCCESSOR THAT FIXES THE NUMERICS AND NOT THE READER GETS A REFUSAL
> INSTEAD OF AN ANSWER.** It must be fixed **in the successor's own comparator,
> under its own freeze**, before D2 is gradeable at all.

**§11 also stands:** the successor should give **O3 the coverage O1 has** — every
written `t > 0`, not the two instants §3.5.4 registered. The registered O3 caught
the failure but not at its worst point.

### 14.6 THE SUCCESSOR — ORDERED, AND **NOT YET REGISTERED**

**Sanaa's directive ORDERS this fix** (*"Act C: run the fix in §2 now"*;
*"convergence studies launch in parallel on every case named above, starting
now"*).

> **⛔ AS OF THIS ADDENDUM, NO SUCCESSOR PRE-REGISTRATION EXISTS ON DISK FOR
> T25R2.** Checked, and the check is named so it can be repeated:
> `docs/campaigns/T-family/` and `verification/campaign/` were listed, and no
> file registers a T25R2 successor. **A directive orders; it does not register.**

Under `CLAUDE.md` rule 2 the successor freezes **its own** pre-registration, by
sha, **before any compute**. §13's *"NO SUCCESSOR IS STARTED AND NOTHING BELOW IS
REGISTERED"* is unchanged by this addendum, and **no compute is authorised by
it.** **L3 stays refused** (§8.6); **an L2 outer-loop arm stays refused** (§8.5);
the §9 halt of `T25R2_L2` and `T25R2_L2_DT025` stands, and their staging remains
on disk for reuse.

**One thing the successor inherits that is worth money:** §12's measured
`×1.765` cost of doubling the outer sweeps, and the 20-sweep arm's measured
**12.615 core-min**, are this solver's own rates on this mesh and these loads —
the successor prices its ladders from them rather than from a probe
extrapolation.

### 14.7 FILED AS A LESSON

The transferable content is filed as **`L-429`** in `docs/LESSONS.md`, commit
**`f83a403e`**, together with T23G's. The clause that binds hardest here:
**a non-`CONVERGING` triple, and a failed gate, stay `NOT A RESULT` throughout —
"do not stop" means keep measuring, not keep going until the number becomes
usable.**

**SUBMISSIONS PARKED** (rule 7). **Permanently private** (rule 8).

<!-- END OF T25R2 RESULTS v1.2 -->
