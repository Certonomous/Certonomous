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
