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
