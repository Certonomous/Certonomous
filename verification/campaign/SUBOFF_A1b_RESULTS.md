# SUBOFF A1b — RESULTS RECORD (LIVE; the runs are in flight)

**Graded against `verification/campaign/SUBOFF_A1b_PREREGISTRATION.md`, frozen at
`8efe38e8f5bcf7c82cf34e68344bd02b457419aa`, blob `5ffb6537a4a3696d6ffc4c12603300c5c003d542`,
verified to BE the file on disk by `git hash-object` rather than assumed.**

> **NO VERDICT IS ISSUED IN THIS FILE YET.** `SOLVE_L1` is mid-flight and `SOLVE_L2` has not
> started. Everything below is either a run state or a measurement about the *instruments*,
> never a graded result. Per §0 of the registration: **no GCI, no observed order, no
> Richardson extrapolation — absent, because they do not exist for two levels.**

---

## 1. RUN STATE

| | state |
|---|---|
| **`SOLVE_L1`** | **RUNNING.** 4 ranks, launched 2026-09-12T01:46:28Z (`free -g` available **11 GiB** read immediately before). 51+ complete outer iterations, **no `FOAM FATAL`**, all six residuals falling smoothly and together. Watcher armed at a **derived** 190,800 s ceiling that **escalates and never kills**. |
| **`SOLVE_L2`** | **`BLOCKED` on memory** — measured **1.54–1.71 kB/cell** from L1's own running ranks ⇒ **13.4–14.9 GiB**, against a ceiling of `available − 4`. A detached gated launcher polls and will start it unattended at `available ≥ 19 GiB`, **derived from the UPPER end of the measured range** (14.9 + 4), because *a memory prediction is not a best estimate, it is a bound, and the only error that hurts is the low one.* Proven polling: `reading 11` logged at 02:15:31Z, exactly twenty minutes after `reading 1`. |
| first `SOLVE_L1` launch | **crashed at iteration zero**, 4.80 core-min, on an upstream OpenFOAM documentation defect. Case **moved, never cleared**. `SUBOFF_A1_RESULTS.md` §7. |

**`Cd` at iteration 51 is `2.1608e-03`, −41.5 % against `CT_ref = 3.6916168e-03`. IT ENTERS
THIS RECORD AS A LIVENESS OBSERVATION AND NOTHING ELSE** — 51 of 3000 iterations, and §2
below is why no weight may be put on it.

---

## 2. 🔴 AN EARLY FALSE SETTLE, MEASURED — AND IT IS THE ARGUMENT FOR TWO REGISTERED DESIGN CHOICES

**`Cd` drift at iteration 51, the same series at the same instant, by window length:**

| window | drift as a fraction of the window mean |
|---|---|
| last **10** iterations | **+0.787 %** |
| last **20** iterations | **+0.047 %** |
| last **30** iterations | **+7.039 %** |

> **A TWENTY-ITERATION WINDOW CALLS IT FLAT TO FIVE HUNDREDTHS OF A PERCENT WHILE A
> THIRTY-ITERATION WINDOW CALLS IT SEVEN PERCENT. ONE SERIES, ONE INSTANT, A FACTOR OF 150
> ON WINDOW LENGTH ALONE.**

**This is not a hypothetical failure mode. It is this case's own predecessor**, verified here
by reading `SUBOFF_R1b_RESULTS.md` rather than by quoting a paraphrase of it:

- `grade_suboff.py:368` implemented the plateau test as
  `abs(ct_series[-1] - ct_series[-2]) <= PLATEAU_TOL_REL * abs(ct)` with
  `PLATEAU_TOL_REL = 0.005` (`:65`) — **it compares only the final two writes.**
- **`medium`**: two-point difference **0.0998 %** ⇒ flagged **`PLATEAUED`**. Actually
  **falling 10.02 % per 100 iterations.** *(`SUBOFF_R1b_RESULTS.md` §3a, and §1(i)'s table.)*
- **`fine`**: two-point difference **0.0535 %** ⇒ flagged **`PLATEAUED`**. Actually
  **rising 5.71 % per 100 iterations, monotone over 500.**
- That record's own words: ***"a rule-3-shaped hole: a plateau detector never shown able to
  see a non-plateau"***, and ***"this is the more dangerous of the two defects. Blocker."***

**TWO REGISTERED CHOICES ARE VINDICATED BY THIS MEASUREMENT, AND BOTH WERE MADE BEFORE IT:**

1. **`residualControl` REGISTERED ABSENT.** The registration's stated reason was a collision
   between frozen clauses — an early residual exit satisfies neither `last == endTime` nor
   the `ExecutionTime`-count clause. **The measurement adds a second, independent reason: a
   short-window or residual-based stop would take the state at iteration 51 for convergence.**
   The run goes to `endTime = 3000` regardless.
2. **THE PLATEAU TEST IS A REGRESSION OVER THE FINAL 500 ITERATIONS**, not a two-point
   difference. **51 iterations is 10 % of that window.** A flat spell now is not a plateau.
   **R1b's `fine` was monotone over 500 — so the registered window is exactly the length that
   would have caught the case that fooled its predecessor.**

**A flat `Cd` window is therefore evidence of nothing at this stage, and this record declines
to treat it as any.**

---

## 3. 🔴 AN INSTRUMENT HAZARD THAT IS NOT LOCAL TO THIS CASE — READING `p` RESIDUALS OFF AN OPENFOAM LOG

**Measured on this run:** **153** `Solving for p, Initial residual` lines across **51**
complete outer iterations — **exactly 3.00 per outer iteration**, because
`nNonOrthogonalCorrectors 2` performs **three pressure solves per SIMPLE iteration** and the
2nd and 3rd start from an **already-corrected** field.

> **SO ANY READER THAT TAKES THE LAST `Solving for p` MATCH — `findall(...)[-1]`, or a
> `grep | tail -1` — IS REPORTING A NON-ORTHOGONAL CORRECTOR'S RESIDUAL AND CALLING IT THE
> OUTER-ITERATION RESIDUAL. THE CORRECT READ IS THE *FIRST* `p`-SOLVE OF EACH OUTER
> ITERATION.**

**Measured size of the error on this run, at iteration 51:**

| | value |
|---|---|
| last `Solving for p` match in the log | **3.67e-06** |
| **true outer-iteration `p` initial residual** | **3.6892e-04** |
| ratio | **~100×** |

**The failure direction is the one nobody audits: it reports convergence about a hundred
times better than reality.** A convergence check built that way cannot fail conservatively.

**How it was caught, and how it was not.** It was **not** caught by a planted control — the
plants validate the readers the comparator uses, and this was an ad-hoc analysis query.
**It was caught by re-deriving the number from the artifact when a conclusion was about to be
built on it.** The corrected picture at iteration 51 — `Ux` 4.4393e-05, `Uy` 4.4932e-04,
`Uz` 2.5976e-04, **`p` 3.6892e-04**, `k` 2.2436e-05, `omega` 1.4021e-06, **worst momentum / p
= 1.22** — shows pressure and momentum at **the same order**, falling together.

---

## 4. A CONCLUSION THAT WAS ASKED FOR AND IS **NOT** RECORDED, AND WHY

A pairing was put to this lane for the record: *"a pressure equation that looks converged
while the force is still 42 % off and trending is the signature of an easy pressure solve on
a developing momentum field."* **It is not recorded, because on measurement BOTH of its
premises are false:**

- **`p` is NOT anomalously converged** — worst momentum / `p` = **1.22**, the same order. The
  "converged `p`" figure was this lane's own mis-read of a corrector residual (§3).
- **`Cd` is NOT trending** — drift over the last 20 iterations is **+0.047 %**. It is flat.

**The reasoning was sound; the inputs were not, and one of them was this lane's error.**
Recording it would have laundered a mis-read number into the evidentiary record behind two
layers of credibility — a supervisor's reasoning over a lane's measurement — **where the next
reader has no way to catch it.** It is written here as **refuted**, with the measurements that
refute it, rather than omitted: a conclusion that was considered and killed by data is part of
the record, and a silently dropped one is not.

---

## 5. WHAT THIS RECORD DOES NOT CLAIM

- **No convergence, no plateau, no `CT` verdict.** §1's `Cd` is a liveness observation.
- **No grid convergence of any kind** — §0 of the registration: two levels, so **no GCI, no
  observed order, no Richardson extrapolation**, and Gate D is **`NOT A RESULT` by
  construction**.
- **No claim resting on L1**, which is **not admitted** (registration §2.1): L1 is `GATE FAIL`
  on the determinant limb and that failure travels with every number out of it.
- **No experimental agreement.** `CT_ref` is a manifest/engineering anchor; no title-verified
  SUBOFF force measurement is on disk.

---

# §6. AMENDMENT 1 — 2026-09-14 — **THE RUNS THIS RECORD CALLS "RUNNING" AND "`BLOCKED`" BOTH FINISHED ON 2026-09-13, AND THEY SAT UNGRADED FOR A DAY BECAUSE THE AUTOGRADERS DIED BEFORE THEY LANDED**

**Version 1.0 → 1.1. Appended at the foot under CLAUDE.md rule 6. `lines whose number
changed above this section: 0` — nothing above was renumbered, reworded or deleted. The
superseded sentences are quoted and STRUCK here, in place, so a reader sees what was
believed and when.**

**Written by a cfd `lab-lane`, 2026-09-14T02:19Z, after reading the run directories rather
than this file. No gate, threshold, cap or label is altered. L1 remains NOT ADMITTED
(registration §2). `CT` remains `NOT A RESULT` by construction (registration §0, Gate D).**

---

## 6.1 WHAT IS STRUCK

> **STRUCK — title line 1:** ~~"RESULTS RECORD (LIVE; the runs are in flight)"~~
> **Neither run is in flight. Both finished 2026-09-13.**

> **STRUCK — §1 header block, lines 7–8:** ~~"`SOLVE_L1` is mid-flight and `SOLVE_L2` has
> not started."~~ **`SOLVE_L2` started 2026-09-12T21:52:32Z and finished
> 2026-09-13T17:21:32Z.**

> **STRUCK — §1 table, `SOLVE_L1` row (line 18):** ~~"**RUNNING.** … 51+ complete outer
> iterations"~~ **That launch was lost to the 2026-09-12T17:36:41Z reboot. Its successor
> `SOLVE_L1_R3` ran 3,000 complete outer iterations and finished 2026-09-13T03:20:28Z.**

> **STRUCK — §1 table, `SOLVE_L2` row (line 19):** ~~"**`BLOCKED` on memory** … A detached
> gated launcher polls and will start it unattended at `available ≥ 19 GiB`"~~ **The gated
> launcher fired. `SOLVE_L2` — 9,121,237 cells — ran to `endTime` 3000 and `rc = 0`.**

> **STRUCK — §1, lines 22–24:** ~~"`Cd` at iteration 51 is `2.1608e-03` … IT ENTERS THIS
> RECORD AS A LIVENESS OBSERVATION AND NOTHING ELSE"~~ **Superseded by converged values at
> iteration 3000 at both levels, below. §2's warning about short windows is NOT struck and
> is vindicated: the iteration-51 figure was 34.2 % below the level's own converged `Cd`.**

**§2, §3 and §4 stand unamended. They are measurements about instruments, not run states,
and none of them is stale.**

---

## 6.2 WHAT IS ON DISK — THE STRICT COMPLETION RULE, CLAUSE BY CLAUSE, PER LEVEL

**Artifacts:** `verification/runs/navier_class/SUBOFF_A1/SOLVE_L1_R3/` (L1, 3,268,613
cells) and `verification/runs/navier_class/SUBOFF_A1/SOLVE_L2/` (L2, 9,121,237 cells);
cell counts read from each case's own `constant/polyMesh/owner` `note` field.

| clause (rule 4 / registration Gate C) | **L1 — `SOLVE_L1_R3`** | **L2 — `SOLVE_L2`** |
|---|---|---|
| `rc = 0` | **0** — `SOLVE_L1_R3/solve_rc` | **0** — `SOLVE_L2/solve_rc` |
| an `End` line | **1** — `log.simpleFoam` | **1** — `log.simpleFoam` |
| last `Time` == `endTime` | **3000 == 3000** (`system/controlDict`) | **3000 == 3000** |
| fields at `3000/` | `U k nut omega p phi yPlus` **present** | same, **present** |
| `ExecutionTime` count == 3000 | **3000 ✅** | **3002 ❌ — THE ONE CLAUSE THAT FAILS** |
| age guard vs the case's own `0/U` | **PASS**, smallest margin **+19,002.15 s** (`k`) | **PASS**, smallest margin **+70,135.69 s** (`k`) |
| every `processor*/3000/` field fresh, none missing | **PASS**, 4 ranks | **PASS**, 4 ranks |
| `decomposePar` older, `reconstructPar` newer | **PASS** | **PASS** |
| **Gate C** | **`PASS`** | **`NOT COMPLETE`** |

**There is no `0/T` — this is an incompressible case and the age anchor is the case's own
`0/U`, as the registration's Gate C states.**

**Mesh provenance checked, not assumed.** All five `constant/polyMesh` files in each solve
case hash identically to that case's `SOLVE_MANIFEST.json` **and** to the built mesh under
`SUBOFF_A1/L1/` and `SUBOFF_A1/L2/`. `residualControl` is absent from both
`system/fvSolution`, as registered.

### 6.2.1 WHY L2's `ExecutionTime` COUNT IS 3002, STATED AS ARITHMETIC RATHER THAN AS AN EXCUSE

`SOLVE_L2/log.simpleFoam` is **two OpenFOAM processes concatenated** — two `Build :`
banners (lines 8 and 2120) and two `Starting time loop` lines. Segment 1 ran `Time = 1 … 63`
and wrote **62** `ExecutionTime` lines before dying mid-iteration-63. Segment 2 opens
`Create mesh for time = 60` and runs `Time = 61 … 3000`, **2,940** lines. `62 + 2940 =
3002`. **Distinct `Time` values in the file: exactly 3000.** Times 61, 62 and 63 appear
twice; they were computed once in the surviving chain.

> **THE RUN COVERED EVERY ITERATION AND THE CLAUSE STILL FAILS, AND BOTH HALVES OF THAT
> SENTENCE STAY.** Rule 4 is all-or-nothing and the comparator implements the clause as
> written. **The clause is not reinterpreted here to let the run through.**

---

## 6.3 THE GRADE — THE PINNED COMPARATOR, RUN UNMODIFIED, WITH ITS PLANTS FIRING

**Instrument:** `verification/runs/navier_class/SUBOFF_A1/GRADER_PINNED_8efe38e8f.py`,
`sha256` **`41a41f02cf3242ed8ebd675ab78dbd2ba746d4d8ce9eff441ecd4aec7e62b0d6`**, verified
byte-identical to `git show 8efe38e8f:cases/navier_class/SUBOFF_A1/grade_suboff_a1.py`.
**The worktree copy has since diverged (`e0b4a4c4…`) and was NOT used.** Rule 2's grading
path holds. Invoked exactly as `cases/navier_class/SUBOFF_A1/autograde_on_completion.sh:71`
invokes it. **Nothing in the comparator was edited.**

**Rule 3 — all three planted controls ARMED at both levels**, recorded in
`GRADE_L1_FROM_SOLVE_L1_R3.json` and `GRADE_L2_FROM_SOLVE_L2.json` (same directory):
`P_A` the `Cd` reader returned the planted **1.234e-03** past a decoy **5.678e-03** at
`t = 1`; `P_B` the `y⁺` reader returned the planted **987.654** past a decoy patch;
`P_C` the age guard reported **FAIL on the stale plant and PASS on the fresh one** — the
two-sided form, because a "pass" from a checker that never looked reads the same as a
real one.

| | **L1 — `SOLVE_L1_R3`** | **L2 — `SOLVE_L2`** |
|---|---|---|
| **Gate C — completion** | **`PASS`** | **`NOT COMPLETE`** |
| **Gate W — `y⁺` < 300** | **`GATE FAIL`** — hull max **342.871357** over written times, **342.849220** at iteration 3000; sail **96.696946**. Ceiling 300. | **`BLOCKED`** — behind Gate C (registration §4: *"Any clause failing ⇒ NOT COMPLETE, and every gate behind it `BLOCKED`"*). §6.4 explains why the comparator's printed value there is not evidence. |
| **Gate D — `CT`** | **`NOT A RESULT`** by construction | **`NOT A RESULT`** by construction, **and `BLOCKED` behind Gate C** |
| `CT` reported | **3.28309615e-03** | see §6.4 — the comparator's **2.01606087e-03** is iteration 62, not 3000 |
| **S1** | **`RISING`** — `p` initial residual **8.2825662e-07 → 8.8552738e-07** over the final 500 | not reached |
| **S3** | **`PLATEAUED`** — drift **5.585e-08** of the window mean against a 5 % threshold | **`BLOCKED`** — 62 rows < 500 |

### 6.3.1 THE REGISTERED PREDICTIONS, SCORED

| | prediction | outcome |
|---|---|---|
| **Q1** | both levels clear all eight Gate C clauses | **FALSIFIED at L2** on the `ExecutionTime` clause. Holds at L1. |
| **Q2** | Gate W `PASS` at both levels | **FALSIFIED at L1** — 342.87 against a ceiling of 300. Not reached at L2. |
| **Q3** | hull **average** `y⁺` ∈ [30.0, 70.1] at L1 | **HOLDS** — **50.096** at iteration 3000. |
| **Q4** | `S1 = NOT RISING` and `S3 = PLATEAUED` at both | **FALSIFIED at L1** on S1. S3 `PLATEAUED` at L1. |
| **Q5** | `CT` at L2 inside the ±15 % band | **NOT SCORABLE** — L2 is not complete. **L1's 3.28309615e-03 falls inside the band [3.137874e-03, 4.245359e-03], and Gate D's label is `NOT A RESULT` either way**, exactly as Q5 was written to ensure. |
| **Q6** | \|Δ\| between the levels < 25 % | **see §6.5 — reported as a DIFFERENCE, and it is not the comparator's output.** |

> **🔴 GATE W IS THE SUBSTANTIVE FAILURE AND IT IS NOT BOOKKEEPING.** A `y⁺` of 342.9 on
> the hull is outside the range where the registration's wall-treatment argument holds.
> **Q2 was written to say that a `y⁺` breach falsifies the ITTC `u_τ` anchor and the wall
> treatment with it, not merely a number. It does.**

---

## 6.4 🔴 THE COMPARATOR CANNOT SEE L2's RESUMED SEGMENT, AND EVERY L2 NUMBER IT PRINTED IS FROM THE FIRST 62 ITERATIONS

**The comparator reads three hard-coded paths** — `postProcessing/yPlus/**0**/yPlus.dat`,
`postProcessing/residuals/**0**/solverInfo.dat` and
`postProcessing/forceCoeffs/**0**/coefficient.dat` (`GRADER_PINNED_8efe38e8f.py` lines 349,
375, 389). **On resume, OpenFOAM opened a second set under `…/60/`.** Measured:

| file | rows | time span |
|---|---:|---|
| `SOLVE_L2/postProcessing/forceCoeffs/0/coefficient.dat` | **62** | 1 → 62 |
| `SOLVE_L2/postProcessing/forceCoeffs/60/coefficient.dat` | **2,940** | 61 → **3000** |
| `SOLVE_L2/postProcessing/yPlus/0/yPlus.dat` | **8** | the startup transient |
| `SOLVE_L2/postProcessing/yPlus/60/yPlus.dat` | **392** | through **3000** |

**So the comparator's `CT_reported = 2.01606087e-03` is the `Cd` at iteration 62**, and its
`max y⁺ = 1058.28277` is the startup transient. The converged values, read from the `60/`
files the comparator never opens: **`Cd` at 3000 = 3.31521629e-03**; **hull `y⁺` max at 3000
= 228.243087, sail 71.9514041 — both BELOW the 300 ceiling.**

> **THIS IS EXACTLY THE CASE WHERE AN INSTRUMENT WOULD BE EDITED TO PRODUCE THE WANTED
> ANSWER, AND IT WAS NOT EDITED.** Making the comparator read `…/60/` would turn L2's
> `y⁺` from 1058 to 228 and its `Cd` from 2.0e-03 to 3.3e-03 — a `GATE FAIL` into a `PASS`
> and an out-of-band `CT` into an in-band one. **A frozen instrument changed after seeing
> the run it grades is worth nothing, whatever the change's merits.** The runs stay
> ungraded at L2 and the requirement is reported instead.

**WHAT IT WOULD TAKE, STATED SO SOMEBODY ELSE CAN JUDGE IT — AND IT IS A NEW PRE-REGISTRATION, NOT A PATCH.** Four code sites: the three `postProcessing/<fo>/0/` paths
would have to enumerate every segment directory in time order and merge them, keeping the
**later** segment's row wherever two segments carry the same time; and `clause_exec_count`
(line 188) would need a restart-aware form — *distinct* `Time` values equal to `endTime`,
or per-process reconciliation. **Neither change may be made under `8efe38e8f`:** rule 2
closed the gates at first compute, and a comparator amended after the fact is a new
instrument that needs its own freeze and its own both-branches demonstration.

**A CHEAPER AND HONESTER ROUTE EXISTS: re-run L2 from `0/` in one unbroken process.** It
clears the `ExecutionTime` clause and the segmented `postProcessing` tree at once, under
the registration exactly as frozen, at a **measured** 4,673.70 core-min. It is not launched
here; **no solver was launched by this amendment.**

---

## 6.5 THE LEVEL-TO-LEVEL DIFFERENCE — **A DIFFERENCE, NOT A CONVERGENCE**, AND NOT THE COMPARATOR'S OUTPUT

Read directly from `SOLVE_L1_R3/postProcessing/forceCoeffs/0/coefficient.dat` (row 3000)
and `SOLVE_L2/postProcessing/forceCoeffs/60/coefficient.dat` (row 3000):

| level | cells | `Cd` at iteration 3000 |
|---|---:|---|
| L1 | 3,268,613 | **3.28309615e-03** |
| L2 | 9,121,237 | **3.31521629e-03** |

**`Δ = (CT_L1 − CT_L2)/CT_L2 = −0.969 %.`**

> **🔴 THIS IS A DIFFERENCE. IT BOUNDS NOTHING.** Registration §0: two levels give no
> observed order, **no GCI, no Richardson extrapolation, and none is computed anywhere in
> this amendment.** Its coarse member **failed mesh admission** (§2.1) and its fine member
> **failed Gate C**. A 0.97 % agreement between two grids is consistent with convergence,
> with coincidence, and with two meshes wrong in the same direction, and **A1b cannot tell
> them apart.** Q6's \|Δ\| < 25 % is satisfied and **that is a statement about a difference,
> not evidence of anything about the solution.**

**There is no Roache triple here and no third level exists on disk.** `SUBOFF_A1/` holds
`L0c`, `L1`, `L1_DECOMP4`, `L1_SHIFT` and `L2` — **no `L3`**. See §6.7.

---

## 6.6 RULE-12 CALIBRATION — ESTIMATE VERSUS ACTUAL, AT PROCESS COMPLETION

**Actuals from each run's own `STATUS.solve` (`total_core_min`), predictions from
registration §6.**

| | predicted | **actual** | ratio |
|---|---:|---:|---:|
| `SOLVE_L1_R3` | 6,280 core-min | **1,265.37** | **0.2015×** |
| `SOLVE_L2` | 17,540 core-min | **4,673.70** | **0.2665×** |
| **family** | **23,820** | **5,939.07** | **0.2493×** |

**Measured rates:** L1 **6.32 s/iteration** against a predicted 31.4; L2 **23.84
s/iteration** (segment 2, 70,094 s / 2,940 iterations) against a predicted 87.7.

**ATTRIBUTION, KEPT OFF THE RATIO.** The §6 anchor was **10 s/iteration measured under peer
load on the 16-core box**, chosen as the pessimistic of two readings 40 minutes apart. The
runs executed on a box now reading **96 cores and 739 GiB** (`free -g`, `nproc`,
2026-09-14T02:20Z) with far less contention. **This is a misprediction of the MACHINE, not
of the method** — and it runs in the **opposite** direction from `L0c`'s 3.31× overrun,
which was contention. **A four-fold over-prediction and a three-fold under-prediction in one
family is the real calibration finding: the estimator is accurate about the solver and
blind to what else is on the box.**

**WASTE, SEPARATELY NAMED AND NEVER FOLDED INTO THE RATIO:** `SOLVE_L1_R2` died at
iteration 49, **≈29.4 core-min**; the first `SOLVE_L1` launch crashed at iteration zero,
**4.80 core-min**; the pre-reboot `SOLVE_L1` lost 369 iterations, **≈3,295 gross core-min**
(`SOLVE_L2/CHECKPOINT_REPAIR_NOTE.txt`).

**Derived USD: $5.08** at the owner-stated $0.0513/core-h — **DERIVED, NOT MEASURED**; the
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5). **And the rate is owner-stated
for a c7a.4xlarge while this box now reports 96 vCPUs, so the dollar figure is unreliable in
a second way and core-minutes are the only figure to quote.**

---

## 6.7 🔴 THE HARDWARE PREMISE UNDER THE `BLOCKED` RULINGS IS OBSOLETE, AND IT IS A FINDING FOR THE cfd-SUPERVISOR, NOT A RULING MADE HERE

**`SUBOFF_A1_RESULTS.md` §6 blocks L3 on "37–49 GiB against **30 GiB** of RAM", called
"UNCONDITIONAL … however empty the box, it does not fit."** The box measured at
2026-09-14T02:20Z reports **739 GiB total, 588 GiB available, 96 cores.** **Every member of
the 37–49 GiB range now fits with two orders of margin.** The ruling was correct on its
facts and its facts changed.

**WHAT THAT DOES AND DOES NOT BUY.** It does **not** make `{L1, L2, L3}` a triple: **L1 is
`GATE FAIL` on M-d and is NOT ADMITTED**, and that is a mesh property no hardware touches.
The admissible triple is **`{L2, L3, L4}`** at 9.12 / 25.45 / 71.0 M cells, equal delivered
ratio **1.407873** (`SUBOFF_A1_PREREGISTRATION.md` §12.9.2–§12.9.3).

**COST OF THAT TRIPLE, ON TWO BASES, BOTH DERIVED:**

| basis | L2 | L3 | L4 | total |
|---|---:|---:|---:|---:|
| **as registered** (T26 anchor, 1703 core-min/Mcell) | 15,535 | 43,353 | 120,963 | **179,851 core-min** |
| **from this family's OWN measured rate** (L2 actual, 512.4 core-min/Mcell) | 4,674 *(spent)* | **13,043** | **36,380** | **≈54,100 core-min** |

**Marginal cost to complete the triple, measured-basis: ≈49,400 core-min** for the two
missing levels, plus **≈640 core-min** to build L3's mesh (scaled from L2's measured 228.53,
`SUBOFF_A1_RESULTS.md:279`) and more for L4's. **All DERIVED, NOT MEASURED.**

> **NOTHING IS LAUNCHED, DECIDED OR REGISTERED BY THIS SECTION.** A triple needs its own
> pre-registration, frozen before compute. **Retiring the `BLOCKED` ruling is the
> cfd-supervisor's call and the instance question was Sanaa's; the only thing done here is
> to put the measured RAM beside the premise so neither is quoted stale again.**

---

## 6.8 AN INFRASTRUCTURE FINDING, REPORTED AND NOT FIXED

The queue still counts **`SUBOFF-A1B-SOLVE-L1-R2`** as in flight: its
`ESTIMATE_OVERRUN.txt` was written **2026-09-14T02:10:54Z** citing `pid=180438` and
"elapsed 103633 s". **That solver last wrote to `log.simpleFoam` at 2026-09-12T21:31:15Z at
iteration 49 and pid 180438 does not exist.** The runner has been reporting overruns for a
dead process for 28.8 hours. **Not this lane's tree and not touched — handed to the
cfd-supervisor.**

**AND THE REASON THESE RUNS SAT UNGRADED FOR A DAY:** both autograders
(`AUTOGRADE_L1.log`, `AUTOGRADE_L2.log`) were armed on the **superseded** directories
`SOLVE_L1/` and `SOLVE_L2/` and their last entries are **2026-09-12T17:02:53Z** and
**2026-09-12T21:00:35Z** — they died with the reboot and the session. **`SOLVE_L1_R3` never
had a watcher on it at all.** A completed 9.1 M-cell solve was invisible to this record for
a day because the only thing that would have written the verdict was a process, and
processes die.

---

## 6.9 WHAT §6 DOES NOT DO

- It does **not** move a gate, a threshold, a cap or a label; Gates C, W and D stand as
  frozen at `8efe38e8f`. L1 stays **NOT ADMITTED**; `CT` stays **`NOT A RESULT`**.
- It does **not** edit the comparator, and it reports the L2 defect rather than repairing it.
- It does **not** compute a GCI, an observed order or a Richardson extrapolation — **two
  levels, no triple** (§0).
- It does **not** claim experimental agreement. `CT_ref` is a manifest/engineering anchor.
- It does **not** launch a solver, revive A1, or retire the `BLOCKED` ruling on L3.
- It does **not** send, file, upload or register anything outside this box (rule 7).

*Submissions parked. No agent's message is Sanaa's consent.*
