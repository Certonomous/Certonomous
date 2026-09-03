# VMFL046 — RESULTS

**Supersonic Flow with a Normal Shock in a Converging–Diverging Nozzle**
Ansys Fluid Dynamics Verification Manual **VM2026R1, printed p. 155**.

| field | value |
|---|---|
| case | VMFL046, **FIRST registration; supersedes nothing; NEVER-RUN class** |
| solver | OpenFOAM v2606 `rhoSimpleFoam`, steady compressible SIMPLE, first-order upwind |
| mesh family | 2-D Cartesian all-hex, **r = 2**, `3 200 / 12 800 / 51 200` cells |
| ranks | 1, serial, one level at a time |
| run window | 2026-09-02T23:24:19Z – 23:52:22Z |
| graded | 2026-09-03 |
| freeze commit | **`28a4a37580d683d074d939b76df57f2ce199bb03`** |
| comparator blob | **`cbe98dc821cdbeaba0c27363117b65b7ee199dcf`** |
| register row | **#54** |
| **VERDICT** | **`GATE FAIL`** · tier **`NOT HELD`** |

---

## VERDICT — `GATE FAIL`

**The PRIMARY limb failed on its own terms and carries the verdict alone.**

> `GATE FAIL -- primary(shock<=5%)=False [p in[0.5,2.5]=True, GCI<=15%=True, Mdev<=10%=True]`
> — `verification/runs/ansys_verification/VMFL046/GRADE_VMFL046.out`

Shock location at the finest level is **7.7939 %** from the analytical reference against
the frozen **5 %** band, on a **`CONVERGING`** Roache triple. Missed by **1.56×**.

**THE THREE SECONDARY LIMBS DID NOT FIRE, AND THAT IS NOT EVIDENCE OF QUALITY.** Under
charter **§21.3** they are **contaminated-loose and DEMOTE-ONLY** — they were fixed after
coarse-smoke Mach numbers had been seen, so they may turn a `PASS` into a `GATE FAIL` and
may **never** license a `PASS`. Their silence is the silence of a threshold that cannot
speak in this direction, and it must not be reported as agreement. **One of them came
within 2.0 % of firing:** `p_obs` = 0.510 against the registered floor `P_OBS_LO` = 0.5.
This triple did **not** sit comfortably inside its own order band.

**This row is not a credential and could never have become one from this run.** VMFL046
was registered as this team's first genuine `PASS` candidate from the manual's never-run
set (charter §23.3). It failed its primary gate. That is the outcome this register exists
to record without softening.

---

## 1. THE MEASUREMENT

### 1.1 The primary gate quantity — shock location

| level | cells | `x_shock` (m) | deviation from analytical 1.250000 m |
|---|---|---|---|
| L1 | 3 200 | 1.257629 | **+0.6103 %** |
| L2 | 12 800 | 1.192596 | **−4.5923 %** |
| L3 | 51 200 | **1.152576** | **−7.7939 %** |

**Frozen band 5 % at the finest level. L3 misses it by 1.56×.**

> **THE SHOCK MOVES AWAY FROM THE REFERENCE UNDER REFINEMENT, MONOTONICALLY.**
> **A single-level submission at L1 would have PASSED this limb outright at 0.61 %.**
> The pre-freeze smoke's *"shock location matched analytical to <1 %"* — cited in the
> registration as evidence this was a `PASS` candidate — **was that same coarse-grid
> reading. The grid triple is the only reason it was caught** (charter §24.6).

### 1.2 The convergence quantity — pre-shock centreline Mach

Station `x = 0.9` m, fixed a-priori from the **analytical** shock location (safely
pre-shock, supersonic branch, smooth) and **never** from the CFD.

| level | `M(0.9)` | plateau `abs(dM)` over W = 500 |
|---|---|---|
| L1 | 1.738725 | **0** |
| L2 | 1.781806 | **8.7e-11** |
| L3 | **1.812050** | **4.3e-10** |
| analytical | **1.882125** | threshold `δ_M` = **4.25e-04** |

Fine-level deviation **3.72 %**. **The plateau criterion is MET at every level**, by six
to nine orders of magnitude. It was frozen before compute and was **binding including if
it had failed**, with LTS the pre-committed fallback (§22.5).

---

## 2. THE TRIPLES, AND WHAT MAY AND MAY NOT BE QUOTED FROM THEM

### 2.1 The gate triple — `M(0.9)`, `CONVERGING`

`r = 2`, `Fs = 1.25`. **State `CONVERGING`**, `R` = 0.702, **`p_obs` = 0.510**,
**`GCI_fine` = 4.91 %**.

`p_obs` = 0.510 is consistent with the frozen **first-order upwind** scheme, whose formal
order is ~1, and it sits **only 2.0 % above the registered floor `P_OBS_LO` = 0.5**. The
band [0.5, 2.5] is a demote-only secondary; it did not fire, and had it fired it could
only have moved the verdict in the direction it already went.

### 2.2 Diagnostics — NOT gate limbs, and recorded as such

`verification/runs/ansys_verification/VMFL046/DIAGNOSTIC_shock_roache.out`.

| quantity | R | `p_obs` | Richardson limit | against |
|---|---|---|---|---|
| `x_shock` | 0.615385 | 0.700440 | **1.088544 m** | analytical 1.250 → **−12.9165 %** |
| peak centreline Mach | 0.777853 | 0.362431 | **2.175831** | manual's printed 2.2 → **−1.0986 %** |

Both triples are **`CONVERGING`**.

**THE REFERENCE INSTRUMENT IS CORROBORATED AGAINST THE MANUAL'S OWN PRINTED NUMBER**, and
this is the check that keeps the reference honest rather than self-certifying: our
lab-generated analytical peak Mach is **2.197198** against the manual's printed **2.2**
(p. 155) — **−0.1274 %**.

### 2.3 The refuted bound — charter v1.19 §24, carried here in full

Charter **v1.18 §23.3** lifted VMFL046's `GATE REACHED` cap on a bound the supervisor
re-derived personally on an independent path: the model-form effect on shock location is
`dx_shock/x ≤ 0.63 %`, *"8× below the 5 % band"*. The graded run's grid-converged answer
is **−12.9165 %**.

> **12.9165 / 0.63 = 20.50×. THE BOUND IS REFUTED** — not strained, not at its edge,
> exceeded by more than an order of magnitude, in the one place it was load-bearing.

Three things must travel together, and carrying only one of them misleads:

1. **This row's `GATE FAIL` is PERMANENT and is not re-graded by any amendment.**
   Charter §24.7: *"It does not re-grade row #54: VMFL046's `GATE FAIL` was reached on
   the primary limb's own terms, is permanent, and no amendment touches it."*
2. **The cap-lift was OUTCOME-NEUTRAL here** (§24.2(a)): the primary limb failed at
   7.79 % against 5 %, so under the un-lifted cap the outcome would still have been
   `GATE FAIL`.
3. **That is a fact, not a defence** (§24.2(b)): *"A bound wrong by 20.5× that happened
   not to matter is a bound wrong by 20.5×."*

---

## 3. STRICT COMPLETION — `CLAUDE.md` RULE 4, MEASURED AT ALL THREE LEVELS

| arm | L1 | L2 | L3 |
|---|---|---|---|
| `RUN_RC` | **0** | **0** | **0** |
| `End` line present | yes | yes | yes |
| last time == `endTime` | **20000 == 20000** | **20000 == 20000** | **20000 == 20000** |
| `ExecutionTime` count == `endTime` | **20000** | **20000** | **20000** |
| fields `T` `U` `p` at `endTime` | present | present | present |
| written time directories | **one** (`20000`) | **one** | **one** |

`residualControl` was **removed before the freeze** (§22.5) and replaced by the frozen
gate-quantity plateau, so `stopAt endTime` with `endTime 20000` governs and the
`last == endTime` arm **applies** — the pre-registration says exactly this at §10.
`writeInterval` equals `endTime`, so exactly one time directory is written and the **age
guard** compares fields against the case's own `0/T` with no intermediate directory to
confuse it.

---

## 4. THE CONTROLS

**Planted zero (`CLAUDE.md` rule 3) — BOTH readers, and BOTH FIRED.** The comparator
plants into **both** readers the gate uses — the centreline sample reader **and** the
T-field reader — through a real disk round trip, and refuses (exit 2) if either cannot
see its plant.

**`--selftest`: 15 arms, ALL PASS**, run at grade time and persisted to
`SELFTEST_VMFL046.out`. Both plants fire; known-bad input refuses; **all five strict-
completion arms refuse** (including the `endTime`-mismatch arm); both plateau arms
behave (converged and not-converged driven separately).

**Frozen-instrument integrity.** All four case blobs on disk are byte-identical to the
freeze `28a4a375`: comparator `cbe98dc8…`, pre-registration `a01b70c4…`, reference
generator `0089c7fb…`, launcher `9d04e63e…`. The freeze landed 23:20:59Z; the launch
began 23:24:19Z, **200 seconds later**.

**Reference independence — charter §18 CLEARED, with the independent path PERFORMED and
not asserted.** The gate value `M(0.9)` reproduces across three independent paths: this
generator **1.882125**; an independent Newton solver of different method **1.882125**
(difference **0**); NACA-1135 published-table interpolation **1.8817** (difference
**4.3e-04**). That is §18 forms 1+3, the strongest available.

---

## 5. A DISCLOSED, UNREPAIRED DEFECT IN THE FROZEN COMPARATOR

**Documentation only. It moved no number. It is NOT edited** — `CLAUDE.md` rule 6, frozen
files are never edited.

`cases/ansys_verification/VMFL046/grade_vmfl046.py` carries a **stale header**:

- **`:4`** still reads `DRAFT (ansys-lane-opus48). NOT THE FREEZE COMMIT.` — this blob
  **is** the freeze commit.
- **`:10-13`** still read that the model-form difference *"caps the verdict at GATE
  REACHED"* and that **`THIS COMPARATOR NEVER EMITS PASS: at most GATE REACHED`**.

**The code refutes its own header.** `verdict = "PASS"` is reachable and is assigned at
**`:305`** (block `:304-307`), printed at **`:308-312`**. The constants block is the part
that is current and correct: `SHOCK_TOL = 0.05` at **`:47`**, with its citation
*"model-form bound 0.18-0.63% << 5%, §12.2 SAME per v1.18"* at **`:49`**.

The header was written against the pre-§23 cap and was never updated when charter v1.18
lifted it. **No gate constant, no threshold, no reader and no printed number is
affected.**

---

## 6. COST — ESTIMATE VERSUS ACTUAL (`CLAUDE.md` rule 12)

| figure | value |
|---|---|
| registered estimate | **12.00** core-min ($0.010260 derived) |
| **actual, MEASURED** | **28.05** core-min ($0.023983 derived) |
| per level | **L1 0.95** (57 s) · **L2 5.16667** (310 s) · **L3 21.93333** (1 316 s) |
| gross vs cleaned | **equal** — longest level 1 316 s against the 3 600 s stall rule |
| **ratio** | **2.3375** |
| cap | **30.00** core-min — **93.5 % consumed, 1.95 headroom, NOT CROSSED** |
| **waste** | **0.000 core-min, MEASURED** |

**The per-level figures above are per level.** `launcher.queue.out` prints
`core_min_used` as a **running total** (0.95 → 6.11667 → 28.05); reading those three as
per-level costs double-counts.

**WASTE IS MEASURED ZERO, AND THE MEASUREMENT REFUTES THE CONTENTION FRAMING THIS RUN WAS
LAUNCHED UNDER.** `ExecutionTime/ClockTime` from the final line of each
`log.rhoSimpleFoam`: **0.98754** (56.29/57), **0.98913** (306.63/310), **0.99801**
(1313.38/1316) — idle-wait 1.25 %, 1.09 %, 0.20 %. The job held a full core at every
level. The pre-registration's own instruction that *"any excess at grading is contention
WASTE, reported separately, not misprediction"* **pre-attributed the excess to the wrong
bucket**, and the correction is measurement, not argument.

**The 2.3375 is misprediction end to end**, and it has a named root cause:

> **AN ITERATION-COUNT REGIME CHANGE THE ESTIMATOR NEVER PRICED.** The L1 datum the
> estimate scaled was the smoke's **0.18 core-min, and that solve CONVERGED at 2 777
> iterations under `residualControl`**. The frozen run had `residualControl` **removed**
> and ran the full **20 000** iterations — **the same frozen document says so at §10**.
> The work per level changed by **20 000 / 2 777 = 7.202×**. Correcting only this:
> 0.18 × 7.202 × 21 = **27.2236** core-min against the actual 28.05 — **ratio 1.0304**.
> One a-priori-knowable mechanism closes 97 % of the miss.

**And the near-exact predictor was computed, printed in the frozen document, and then
discarded.** `PREREGISTRATION.md` §9 records the disclosed smoke's **total as 28.2
core-min**; §8 rejects it as *"contention-inflated, not representative"* and substitutes
the a-priori 12.00. **28.2 predicts the actual 28.05 to 0.53 %.** The contention premise
is refuted on the one level that is apples-to-apples: the smoke's L2 and the graded L2 ran
the **same 12 800-cell mesh to the same 20 000 iterations**, in **321 s** and **310 s** —
**3.5 % apart**. (Honest qualification: the smoke's L1 *was* 1.36× slower per iteration —
3.89 ms/iter against the graded 2.85 — so contention was not zero; it was simply far too
small to justify discarding a 0.53 %-accurate total.)

**Secondary term, measured from this triple: superlinear per-cell cost.** Linear-in-cells
from the graded L1 predicts 228 s at L2 and 912 s at L3; actual 310 s and 1 316 s, so
**actual/linear = 1.3596 at L2 and 1.4430 at L3, 1.4060 over the triple**. It **grows with
level** — a triple average, not a law.

The full comparison is filed in `docs/COST_CALIBRATION.md`.

---

## 7. INFRASTRUCTURE NOTE — VOIDING NOTHING

`ESTIMATE_OVERRUN.txt` in the run root reports an overrun of the **estimate**, not of the
**cap**, and **nothing was killed**. Stamped 2026-09-02T23:38:22Z at elapsed 842 s against
1.10 × the 720 s estimate; the queue entry carried no `cap_core_min_registered`, so no cap
existed there to cross. The file says `REPORTED, NOT ENFORCED` on its own face. Kept
rather than deleted.

---

## 8. WHAT THIS RECORD DOES NOT CLAIM

**THE VISCOUS-LOSS READING IS AN OPEN HYPOTHESIS AND IS NOT A FINDING.** Charter §24.3
names viscous total-pressure loss through the diverging section — setting the downstream
pressure-matching state, and **not** a displacement-thickness effect — as the mechanism
that plausibly sits outside §23.1's enumerated-channel bound.

> **IT IS NOT ESTABLISHED. THE DECISIVE INVISCID/EULER COMPARISON HAS NOT BEEN RUN.**
> No figure in this record or in register row #54 rests on it, and it must not be relayed
> as the explanation of the −12.92 %.

Charter §24.5 records the one competing explanation that has been **excluded** by the
data: a discretisation bias in locating a captured shock **refines away with the mesh**,
and this shock moved monotonically *away* from the reference under refinement toward a
`CONVERGING` limit of 1.0885. **The coarse-grid agreement was the artefact; the fine-grid
disagreement is not made of discretisation bias.**

Also not claimed:

- **No credential.** A `GATE FAIL` is not a `PASS`. The register's credential count does
  not move for this row.
- **No secondary-limb quality claim.** The three secondaries are demote-only and
  contaminated-loose; their not firing says nothing.
- **The first-order scheme is a disclosed limitation, budgeted rather than concealed.**
  It forces `p_obs` ≈ 1 and a grid-smeared shock. The higher-order scheme diverges on
  negative-T at a forming shock in this lab's own hands (VMFL017, register row #19). A
  higher-order R2 is future work, not a defect hidden here.

---

## PROVENANCE

**Artifacts**, all under `verification/runs/ansys_verification/VMFL046/`, the four graded
outputs committed at **`4a4b0dbd`**:

`GRADE_VMFL046.out` · `GRADE_VMFL046.err` (empty, 0 bytes, measured) ·
`SELFTEST_VMFL046.out` · `DIAGNOSTIC_shock_roache.out` · `launcher.queue.out` ·
`STATUS.queue.VMFL046` · `ESTIMATE_OVERRUN.txt` · per level `L{1,2,3}/` with `RUN_RC`,
`log.blockMesh`, `log.rhoSimpleFoam`, `system/`, `constant/`, `postProcessing/` and the
single time directory `20000`.

**Frozen at** `28a4a37580d683d074d939b76df57f2ce199bb03`, 2026-09-02T23:20:59Z —
*"VMFL046 FROZEN: this team's first PASS-CAPABLE case from the never-run set"*, the only
commit that has ever touched this pre-registration.

**Manual reference** VM2026R1 printed **p. 155**, verified against the PDF itself
(`CLAUDE.md` rule 15), not by filename or hash.

**Charter clauses governing this record:** §12.2 (model sameness), §18 (lab-generated
reference independence), §21.3 (demote-only secondaries), §22.5 (plateau criterion),
§23 (the cap-lift), §24 (its refutation, and the permanence of this verdict).
