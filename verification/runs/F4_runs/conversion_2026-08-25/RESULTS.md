# F4 CONVERSION — RESULTS

**Graded 2026-08-25. Team: cfd. Lane: lab-lane under cfd-supervisor.**
**Pre-registration frozen at `3e82e989604e540ea2e9cfbef62e0530a086a98d`, BEFORE
any solver started.** Grading path pinned there and verified at grade time:
`grade_f4.py` blob `f51961435729558dc768d89e429c1818e8ae1da6`, sha256
`55636d92a8def8729ad3d5bc811adaa06067b268b76d3d0b0df3ee8283bbe410` — **the
frozen file IS the file that ran.**

---

## 1. SPEND — AND THE CAP WAS CROSSED. REPORTED, NOT ABSORBED.

**HARD CAP: 24.0 core-minutes (prereg §10.3). MEASURED: 24.1108 core-minutes.
THE CAP IS CROSSED, by 0.1108 core-min (0.46 %).**

**The crossing landed on the final accounting, after the ninth case had already
completed**, so no work was cancelled and nothing was lost — but that is a fact
about the timing, not a mitigation, and the cap is **not** extended here. **The
ruling is the cfd supervisor's.** This lane does not extend a cap it registered
and does not stop work to save money; it reports the number it measured.

### 1.1 A DEFECT IN THIS LANE'S OWN INSTRUMENTS, disclosed rather than resolved in its own favour

**The launcher and the grader disagree about whether the cap was crossed, and
the pre-registration did not say which quantity the cap governs.**

| instrument | quantity | total | verdict against the 24.0 cap |
|---|---|---:|---|
| `rerun_f4.py` (launcher) | **wall seconds of the solver subprocess** ÷ 60 | **24.1108** | **CROSSED** |
| `grade_f4.py` (grader) | the solver's own final `ExecutionTime` ÷ 60 | 22.3098 | not crossed |

The gap is **1.8010 core-minutes** — process spawn, OpenFOAM startup (mesh and
dictionary reads) and final teardown, about 12 s per case, which the solver's own
`ExecutionTime` counter does not include.

**The registered quantity is the WALL figure, and this lane takes the number
against itself.** `CLAUDE.md` rule 12 defines the unit as **"core-minutes
(wall s × ranks ÷ 60)"**. `ExecutionTime` is not wall time. **So the cap is
crossed, and the grader's `cap_crossed: false` is the wrong answer produced by
the wrong quantity.** Choosing the 22.3098 figure because it sits under the cap
would be exactly the fitting rule 2 exists to prevent.

**This cannot be repaired here.** §10.3's cap is post-compute and frozen; rule 2
closes it. **The fix belongs in a successor registration**, which must state the
cap's quantity explicitly — wall or `ExecutionTime` — rather than leaving two
instruments free to disagree. Recorded as **F4C-Q1**.

### 1.2 A SECOND GAP: mesh and sampling time were never captured

`rerun_f4.py` records only the **solver** subprocess time. `blockMesh`,
`checkMesh` and the two `postProcess` sampling passes were run and **their wall
time was not recorded anywhere.** So **24.1108 core-min is a LOWER BOUND on gross
spend, not the gross spend.**

This matters for the comparison, because the prereg's §10.1 basis of **14.66
core-min explicitly INCLUDED** meshing and sampling. **The measured actual and
the predicted basis are therefore not the same quantity**, and §5's ratio is
stated with that named rather than reconciled away. This is the same defect class
as **F4-Q4** — a build allowance that could not be closed because the timing
artifact was never written. Recorded as **F4C-Q2**.

### 1.3 What was actually spent

| M | coarse | medium | fine | row (wall core-min) |
|---|---:|---:|---:|---:|
| 6.0 | 0.1892 | 0.8822 | 6.2617 | 7.3331 |
| 7.0 | 0.2019 | 1.0099 | 6.8414 | 8.0532 |
| 8.0 | 0.2181 | 1.1850 | 7.3213 | 8.7244 |

**Total 24.1108 core-min wall (22.3098 `ExecutionTime`).** Batch elapsed
**473.9 s** at ≤ 6 concurrent workers, all `np = 1`. **Dollars: 24.1108 core-min
= 0.40185 core-h × $0.0513/core-h = $0.02062 — DERIVED, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5: the box cannot read its own billing).

---

## 2. ADMISSIBILITY — all nine cases COMPLETE, all five controls PASSED

**Completion (prereg §7), all nine:** `rc = 0` **read back from `RC.txt`** and
never inferred; `End` present; `Time =` count == `ExecutionTime` count; last
logged time == latest written time directory; **the reach test
`t_last + Δt_final > endTime` satisfied**; four fields (`T U p rho`) present at
the latest time; **every one newer than the case's own `0/T`** (age guard); no
case over the 1200 wall s runaway guard.

**Four of the nine landed BELOW `endTime = 6.0`** — M6/coarse `5.9998543386`,
M7/fine `5.9999993531`, M8/coarse `5.99979092006`, M8/fine `5.999927519` — the
identical pattern the repaired clause exists for. **Under the defective
`t_last ≥ endTime` clause caught pre-compute, those four would have been reported
`NOT A RESULT`.**

**Controls (prereg §8) — all passed, and the grader would have refused had any
failed:**

| control | result |
|---|---|
| **P1** | plant at index 137 located at **138**; plant at index 300 located at **301** — both within one sample. **The reader can see a plant.** |
| **P2** | planting into the θ≈36° station (`r3_T_p_rho.xy`) left the θ=0 gate value **bit-identical** at `0.44853801000000004` before, after and restored. **The selector cannot see a plant it does not declare.** |
| **P3** | perturbing the medium dict to `(100 41 1)` was **refused** — "written mesh has 4100 cells, registered 4000". |
| **C1** | accepted a landing at `5.9999` (under `endTime` by 0.4·Δt); **refused** one at `5.99925` (by 3·Δt). |

**Ladder similarity, measured from the WRITTEN `blockMeshDict`s** (not from
`RES`): `r21 = r32 = 2.0` exactly at all three Mach numbers, near-wall h₁ ratios
**1.982046 / 1.991308**. `form="equal"` accepted the ladder rather than falling
back to Celik.

---

## 3. THE GATES

| gate | values (coarse → medium → fine) | triple state | verdict |
|---|---|---|---|
| **G-F4-1-M6.0** | 0.438012 → 0.436842 → 0.448538 | `OSCILLATORY` | **`NOT A RESULT`** |
| **G-F4-1-M7.0** | 0.428070 → 0.438596 → 0.434503 | `OSCILLATORY` | **`NOT A RESULT`** |
| **G-F4-1-M8.0** | 0.442690 → 0.408187 → 0.418129 | `OSCILLATORY` | **`NOT A RESULT`** |
| **G-F4-2-M6.0** | fine 0.448538 vs Billig 0.439466, dev **+2.0644 %**, band ±3.1747 % | — | **`NOT A RESULT`** |
| **G-F4-2-M7.0** | fine 0.434503 vs 0.424598, dev **+2.3327 %**, band ±3.2005 % | — | **`NOT A RESULT`** |
| **G-F4-2-M8.0** | fine 0.418129 vs 0.415219, dev **+0.7007 %**, band ±3.2728 % | — | **`NOT A RESULT`** |
| **G-F4-3-M6.0** | 4.479217 → 4.207655 → 3.909620 % | `DIVERGENT`, p = **−0.1342** | **`NOT A RESULT`** |
| **G-F4-3-M7.0** | 4.693088 → 3.850089 → 3.908692 % | `OSCILLATORY` | **`NOT A RESULT`** |
| **G-F4-3-M8.0** | 4.080258 → 3.889367 → 3.868458 % | `CONVERGING`, p = **3.1905** | **`CONVERGING`**, GCI **0.0831 %** at Fs = 1.25 |

**No GCI is quoted anywhere the triple is not monotone** — the grader returns
`None` for those rows, so none can be quoted by accident.

**The three G-F4-2 deviations all fall INSIDE their registered bands**
(+2.0644 % < 3.1747 %; +2.3327 % < 3.2005 %; +0.7007 % < 3.2728 %). **They are
nonetheless `NOT A RESULT`**, because prereg §3 and standing rule 5 forbid a band
verdict on a non-converging triple. **The gate turned a would-be `PASS` INTO a
`NOT A RESULT` — the only direction rule 5 permits.** Had the door swung the
other way this record would read PASS ×3, and that is precisely the reading the
2026-07-28 record took.

---

## 4. WHAT THIS ESTABLISHES

**(a) The solver is reproducible; the LADDER is what fails.** The re-run
reproduces 2026-07-28 to four or five significant figures on every one of the
nine cases — standoff `0.448538 / 0.434503 / 0.418129` against the recorded
`0.4485 / 0.4345 / 0.4181`, Cp RMS `3.9096 / 3.9087 / 3.8685 %` against
`3.91 / 3.91 / 3.87 %`. **Nothing about F4's physics or its solver has been shown
wrong**, and this conversion does not claim otherwise.

**(b) The 2026-07-28 `PASS` on Gate 1 does not survive conversion, at any Mach
number.** All three standoff triples are `OSCILLATORY`. The old record's own
diagnosis — *"a genuine, resolution-dependent systematic bias in the
peak-density-gradient detector itself"* — is **confirmed**, and it is exactly why
rule 5 refuses the row. **The detector, not the flow, is what moves.**

**(c) The 2026-07-28 `PASS` on Gate 2 does not survive either, at two of three
Mach numbers** — and **one limb survives and is stronger than what it replaces**:
**G-F4-3-M8.0 is `CONVERGING` at observed order 3.19 with a GCI of 0.0831 %.**
That is a real, quantified convergence statement, where the 2026-07-28 Gate 2
`PASS` was graded against **no threshold at all**.

**(d) The conversion did its job.** Two undefendable `PASS` verdicts are replaced
by eight `NOT A RESULT`s and one quantified `CONVERGING`. **A `NOT A RESULT` here
is a successful conversion, not a failed one** — the defensible label replaced an
indefensible one, and it cost 24.1108 core-minutes to find out.

### 4.1 The pre-registered prediction, scored honestly — 8 of 9

Prereg §12.1 registered a prediction **before the run**. Scored strictly:

| predicted | outcome | |
|---|---|---|
| G-F4-1 `OSCILLATORY` → `NOT A RESULT` ×3 | all three `OSCILLATORY` | **3/3 right** |
| G-F4-2 `NOT A RESULT` ×3 regardless of band | all three | **3/3 right** |
| G-F4-3-M7.0 `NOT A RESULT` | `OSCILLATORY` | **right** |
| G-F4-3-M8.0 "monotone and may converge" | `CONVERGING`, p = 3.19 | **right** |
| G-F4-3-M6.0 "monotone and may converge" | **`DIVERGENT`, p = −0.1342** | **WRONG** |

**The M=6 Cp limb is monotone but its observed order is NEGATIVE**, which
`roache_triple` classifies `DIVERGENT`. The values fall 4.479 → 4.208 → 3.910
with the *increments growing* rather than shrinking, so refinement is moving the
functional further, not settling it. **My prediction read monotonicity as
convergence; it is not the same thing**, and that is the lesson this row paid
for.

---

## 5. COST CALIBRATION (rule 12) — predicted vs actual

| | value |
|---|---|
| **Predicted** (prereg §10.2) | **17.36 core-min** (basis 14.66 × 1.15 contention + 0.5 grading) |
| **Actual, solver wall** | **24.1108 core-min** |
| **RATIO actual/predicted** | **1.389** |
| Actual vs the raw measured basis (14.4533 `ExecutionTime`) | **1.668** |

**Gap attribution, and the misprediction is mine.** The gap is **CONTENTION, not
waste.** The prereg took a contention factor of **1.15**, reasoned from C-33's
measured 1.058× and a box the supervisor reported at load **3.70/16**. **At launch
the box was at load 11.14 and it reached 15.05 during the batch** — three other
teams' work, none of it this lane's, and none of it touched. Per-case ratios
against basis came in at **≈1.9×** on the coarse cases. **The error is in the
contention estimate, not in the solver and not in the cases.**

**WASTE: 0.0 core-minutes, named separately and NOT absorbed into the ratio.** All
nine cases completed on the first attempt, `rc = 0`, no stall, no re-run, no
cancelled work. No row exceeded 3600 wall s (the charter's stall definition); the
slowest was 439 s.

**Dollars $0.02062 — DERIVED, NOT MEASURED.**

**The calibration lesson, stated so the next prereg can use it:** a contention
factor must be taken from **the box's load at launch**, not from a supervisor's
earlier reading or from a prior row measured under different load. **1.15 was
predicting a quiet box while queuing onto a busy one.**

---

## 6. OPEN ITEMS

| id | item | who |
|---|---|---|
| **F4C-Q1** | The cap's quantity was never specified — launcher (wall) and grader (`ExecutionTime`) disagree by 1.80 core-min and give opposite cap verdicts. **Cannot be amended here** (§10.3 is post-compute and frozen). A successor registration must name the quantity. | next prereg |
| **F4C-Q2** | Mesh and sampling wall time not captured, so 24.1108 is a **lower bound** on gross spend and is not the same quantity as the 14.66 basis. Same class as F4-Q4. | launcher change |
| **THE CAP CROSSING** | **24.1108 > 24.0.** Reported, not extended, not absorbed. | **cfd-supervisor rules** |
| **The three 2026-07-28 record defects** | no band; PASS over a non-monotone triple; no `RC.txt` anywhere | **cfd-supervisor rules — not this lane's** |
| **Gate 3 / SWBLI** | **`BLOCKED`** on F4-W1 and on the event-1/event-2 ruling **`PENDING` on Sanaa's desk** | Sanaa |

**Nothing was sent, filed, uploaded, registered, posted or commented (rule 7).**
**The 2026-07-28 production tree was never written to.** The empty untracked
`conversion_2026-08-24/` was **inspected and not removed** — and `rerun_f4.py`
was smoke-tested against it, refusing with rc 3.
