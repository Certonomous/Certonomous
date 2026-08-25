# VMFL036 — Laminar Flow Past a Sphere — RESULTS

**Case:** Ansys Fluid Dynamics Verification Manual VM2026R1, VMFL036, pp. 125–126.
**Graded 2026-08-25T22:24Z** by a fresh lane, from the frozen comparator, re-run in full.
**Pre-registration** `cases/ansys_verification/VMFL036/PREREGISTRATION.md`, frozen and
committed at **`ff9e28da`** BEFORE any solver started; its line 19 records the run root
as absent at the freeze timestamp.
**Comparator** `cases/ansys_verification/VMFL036/grade_vmfl036.py`, blob
**`8a1aea3bd6f0dcd1d720c54a92f76b780924d028`** (repaired under `VERIFICATION_CHARTER.md`
§2d.1 at `591f659e`; see `PREREG_ADDENDUM_02.md` and §7.1 below).
**Raw comparator output:** `cases/ansys_verification/VMFL036/GRADING_OUTPUT.txt`.

---

## 0. PROVENANCE OF THIS RECORD — what THIS lane measured, and what it inherited

A predecessor lane graded this case and was lost to a connection drop before committing
its `RESULTS.md`. It **had** committed the register row and the cost-calibration row at
`6a229113`, both of which cite `cases/ansys_verification/VMFL036/RESULTS.md` — **a
citation that pointed at a file not in git.** That dangling citation is what this record
closes.

**This lane did not trust the uncommitted draft.** Before running anything it re-derived
`HEAD` and asserted, by hash, that the comparator and the pre-registration on disk ARE the
blobs committed at HEAD (`8a1aea3b…` and `5f228280…` respectively, both matching), then
re-ran the frozen comparator from scratch.

| | verified by THIS lane | inherited, NOT re-verified |
|---|---|---|
| §1–§3, §5, §6 (every Cd, residual, plateau, triple, order, GCI, control, mesh certificate, azimuthal bracket) | **yes** — reproduced digit-for-digit from the frozen comparator's own re-run | — |
| §4 (Arm B's registered predictions and both tests) | **yes** — the 1.5381 prediction and the ≥ 25 % discriminator read off `PREREGISTRATION.md` lines 194–195 at HEAD | — |
| §8 (costs) | **yes** — read from each level's own `RUN_RC.txt` | — |
| endTime / writeInterval assertion | **yes** — asserted independently of the comparator (§5, last bullet) | — |
| §7.2 (predecessor inheritance) and §7.4 (the VMFL023 throughput near-miss) | — | **inherited narrative.** Retained because suppressing a disclosure is worse than carrying an unverified one; **labelled so no reader mistakes it for a measurement of this lane.** |

---

## 1. THE VERDICT

| Arm | Verdict | Cd (finest) | Reference | \|rel\| | Band | Roache triple |
|---|---|---|---|---|---|---|
| **A — THE GATE** (μ = 0.01, Re = 100) | **`GATE REACHED`** | **1.088834** | 1.0895 | **0.0611 %** | 3 % | CONVERGING |
| **B — disclosed diagnostic** (μ = 0.02, Re = 50) | **`NOT A RESULT`** *(by registration, scores nothing)* | 1.577375 | — | — | — | CONVERGING |

**`GATE REACHED` is the ceiling, and it was frozen as the ceiling rather than discovered
after.** Mittal (1999) is a Fourier–Chebyshev **spectral collocation computation**;
Tabata & Itakura (1998) is titled *"a precise **computation** of drag coefficients"*.
Both are **code-to-code**, so this reference buys **neither V nor P**. `PASS` / `HOLDS`
was **not available to this case whatever number it landed on** — pre-registration lines
3–4, and the comparator hard-codes it. **Reproducing another solver's number is not a
validation credential, and 0.0611 % agreement does not change that.** This row is **not**
a credential and must not be counted as one.

Context only, never a gate: Ansys Fluent reports 1.0875.

---

## 2. ARM A — the grid family (THE GATE)

| Level | Cells | Cd | Worst final residual | plateau ptp/Cd | plateau samples | wall s | core-min |
|---|---|---|---|---|---|---|---|
| L1_32x48 | 3 072 | 1.091486 | 1.05e-11 | 3.20e-12 | 2 000 | 82 | 1.37 |
| L2_64x96 | 12 288 | 1.089233 | 1.22e-11 | 5.06e-13 | 2 000 | 400 | 6.67 |
| **L3_128x192** | **49 152** | **1.088834** | 1.04e-11 | 1.50e-11 | 2 000 | 2 004 | 33.40 |

**Roache (CLAUDE.md rule 5):** d32 = 2.252e-03, d21 = 3.992e-04, **R = 0.177234**, state
**CONVERGING**. **GCI_fine at Fs = 1.25 = 0.0099 %.** Richardson extrapolate
f_ex = 1.088748 — **0.069 % from the manual's target**, i.e. the zero-mesh limit agrees
with the reference at least as well as the finest grid does.

**Rule 5's ordering was applied in its own order and nothing was softened.** (1) Every
level is iteratively converged (worst final residual ≤ 1.22e-11) and plateaued; (2) the
triple is CONVERGING, not DIVERGENT / STAGNANT / OSCILLATORY / EXACT; (3) only then is
the value compared with the pre-registered band. The gate could only have turned this
into `NOT A RESULT`; it could never have turned a `NOT A RESULT` into a pass.

### The observed order is ABOVE the formal order — a WARNING, not a win

**p_obs = 2.4963 against a formal p_f = 2.** Pre-registration line 96 declared
`p_obs > 2.3` **SUSPICIOUSLY HIGH in advance**, and the comparator prints the flag
itself. It is reported as the warning it was registered to be. Honest reading: with d21
already at 4e-04 on a quantity of order 1, the fine-grid difference is small enough that
a modest amount of error cancellation between the pressure and viscous contributions will
inflate the fitted order. **The GCI is quoted only because the triple is monotone. It is
not evidence of third-order accuracy and no such claim is made here.**

---

## 3. ARM B — the grid family (DISCLOSED DIAGNOSTIC)

| Level | Cells | Cd | Worst final residual | plateau ptp/Cd | plateau samples | wall s | core-min |
|---|---|---|---|---|---|---|---|
| L1_32x48 | 3 072 | 1.577946 | 1.47e-11 | 2.33e-13 | 2 000 | 81 | 1.35 |
| L2_64x96 | 12 288 | 1.577388 | 1.01e-11 | 0.00e+00 | 2 000 | 390 | 6.50 |
| **L3_128x192** | **49 152** | **1.577375** | 9.97e-12 | 2.06e-10 | 2 000 | 1 987 | 33.12 |

Triple CONVERGING (d32 = 5.575e-04, d21 = 1.266e-05, R = 0.022707). **p_obs = 5.4607 is
NOT interpretable**: d21 = 1.27e-05 is within an order of magnitude of the plateau noise,
so the fitted order is fitting round-off. **Stated, never quoted as a result.** Arm B's
content is §4, not its order. Its GCI prints as 0.0000 % and is likewise not a claim.

---

## 4. WHAT ARM B ESTABLISHES — the supervisor's pre-freeze finding is SUPPORTED

The supervisor's committed pre-freeze check (`3fa6058d`) found the manual's page
**internally inconsistent**: the stated μ = 0.02 gives **Re = 50**, but the target
**Cd = 1.0895 is the Re = 100 value**. Arm B ran the manual's stated viscosity **exactly
as printed**, against a prediction registered **before the run**
(`PREREGISTRATION.md` lines 194–195).

| Test | Registered BEFORE the run | Measured | Outcome |
|---|---|---|---|
| Agreement with Schiller–Naumann at Re = 50, Cd = **1.5381** | within **10 %** | **1.577375**, \|rel\| = **2.5538 %** | **AGREES** |
| Distance from the manual's target 1.0895 | must be **≥ 25 %** | **44.7798 %** | **DISCRIMINATES** |

**BOTH registered tests pass.** Running the manual's own stated properties returns
**1.577**, not **1.0895** — a 44.78 % miss — while the same solver, the same mesh family
and the same schemes, at the Reynolds number the target actually belongs to, land
**0.0611 %** from it.

> **The supervisor's finding is SUPPORTED, not refuted: the error is in the manual's
> printed viscosity, not in this lab's solver.** μ = 0.02 on that page is a transcription
> error for μ = 0.01.
>
> **Stated plainly, as instructed, in the direction it actually fell.** Had Arm B landed
> near 1.0895 rather than near 1.5381, that would have weakened the finding, and this
> section would have said so with the same prominence. It landed at 1.577375 — **2.55 %
> from the registered prediction and 44.78 % from the manual's target.**

**What Arm B does NOT do.** It is **`NOT A RESULT`**, by registration and by
construction. It is evidence **about the manual**. It is not a gate on this solver, it
scores nothing, and it enters no credential count.

**Had the gate been frozen the obvious way** — target 1.0895 at the manual's stated
μ = 0.02 — this case would have returned a **guaranteed `GATE FAIL` measuring a typo**.
That is the VMFL059 class of failure, caught **before** the freeze this time rather than
after it.

---

## 5. CONTROLS — every one fired against REAL artifacts

- **PLANTED FORCE (rule 3).** `total_x = 7.7e-03` planted into a **copy** of the finest
  level's real `force.dat`; the reader returned **7.700000e-03** (a Cd of 1.4136). **The
  reader is shown able to see a non-zero**, so its zeros and its readings are evidence.
- **PLANTED GEOMETRY (rule 3).** Every point of a **copy** of the finest mesh scaled by 2;
  the sphere patch area went **0.04360473 → 0.17441892** against a required 0.17441892
  (exactly ×4). **The geometry reader is shown able to see a changed geometry.**
- **PERMUTED-COLUMN READER.** `total_x` placed in a deliberately permuted column and still
  found **by name**; a planted zero read back as **0.0**; a header carrying no `total_x`
  **REFUSED**, never guessed.
- **ROACHE CLASSIFIER.** All five states — CONVERGING, DIVERGENT, OSCILLATORY, STAGNANT,
  EXACT — constructed and each correctly classified; an exactly-second-order triple
  returned p_obs = 2 to 1e-9.
- **GEOMETRY IDENTITY.** Closed-form Aref `1.0894467844e-02` against an independent
  200 000-point quadrature `1.0894467844e-02`.
- **MESH BIRTH CERTIFICATE** (MESH_STANDARD §6), read off `constant/polyMesh` by the frozen
  pure-python reader at **every** level — never off the solver, never off a function object.
  **Frontal PROJECTED area / frozen Aref = 1.000000000 at all three levels, both arms**;
  half-angle 2.5000° at every level; 64 / 128 / 256 sphere faces.
- **STRICT COMPLETION (rule 4), NO DEPARTURE DECLARED.** Every clause checked literally at
  every level of both arms: `rc = 0`; an `End` line; last time == `endTime`; the log's final
  `Time =` matching it; `ExecutionTime` count == 10 000; `U` and `p` present at `endTime`;
  and the **age guard** — every `endTime` field newer than the case's own `0/`.
- **endTime / writeInterval ASSERTION, asserted by THIS lane OUTSIDE the comparator.**
  `endTime = 10000`, `writeInterval = 10000`, `endTime mod writeInterval = 0`, and a field
  directory exists at `10000/`, **at all six levels**. This is the failure that made another
  case tonight run clean and write no gradeable output; it is asserted here, not assumed.

### Plateau clause — classified against PREREG_TEMPLATE AMENDMENT 4, and disclosed

Amendment 4 classifies this comparator **Class C-minus**: it uses **peak-to-peak over a
fractional window** (`PLATEAU_FRAC = 0.2`, `PLATEAU_PTP_REL = 1.0e-5`), which **correctly
rejects a growing series** — a trending series has a large ptp — but carries **no
minimum-sample refusal.** The pre-registration was frozen before Amendment 4 existed, and
a frozen comparator is never edited (rule 6), so the gap is **disclosed rather than
patched**.

**It did not bite, and here is the number that shows it.** Each level's `force.dat`
carries **10 000 rows**, so the realised window is **k = 2 000 samples at every level of
both arms** — recorded here per Amendment 4 item 5, so a reader can check the floor
without re-running anything. The exposure Amendment 4 names is a *short* run silently
collapsing the window to two samples; **2 000 is three orders of magnitude clear of it**,
and the ptp statistic in use is one of the three Amendment 4 accepts. **The verdict does
not rest on the missing floor.**

---

## 6. THE AZIMUTHAL BIAS — carried, not assumed away (N-AV9)

The predecessor lane froze `Aref = D²sin(a)/4` and argued the `sin(a)` cancels. **It does
not fully.** The wedge maps `(x,y) → (x, y·cos a, ±y·sin a)`, and two **different**
factors follow — exactly the charter's warning that the wedge term is case-shaped:

| quantity | azimuthal factor |
|---|---|
| **wetted** area | `sin(a)/a` |
| **frontal projected** area | `sin(a)·cos(a)/a` |

The projected form carries an **extra cos(a)**. `Aref` was corrected to
`D²sin(a)cos(a)/4 = 1.08944678435e-02`, which matches the value read off the **real mesh**
to 1 part in 1e8; the predecessor's form was **0.095 % larger**.

**The residual bracket is carried, not dropped.** The projected normalisation makes the
*pressure* drag azimuthally exact and leaves the *viscous* part biased by `1/cos(a)`; the
two limits bracket the truth and differ by exactly `cos(a)`:

> **Cd = 1.088834** (projected — the gate) **vs 1.087798** (wetted).
> **Bracket = 0.0952 % of Cd, half-width 0.0476 %. No grid refinement removes it.**

Both are printed beside the verdict by the comparator itself. The bracket is ~1/30 of the
band, so **it cannot decide the gate** — the wetted-form value misses the target by
0.157 %, still inside 3 % by a factor of 19. **It is disclosed regardless.**

---

## 7. WHAT WENT WRONG, AND WHAT IT COST

### 7.1 The comparator could not read its own launcher (repaired under §2d.1) — VERIFIED
Both launchers write `rc = 0` **with spaces**; both comparators parsed `(\w+)=(.*)`, which
requires the `=` to abut the key. **No key matched**, `rc` defaulted to `"1"`, and the
strict-completion guard **refused every level**. **VMFL036 would have been ungradable.**

Caught by the **rule-4 guard — which grades nothing — BEFORE grading, not after.** Repaired
to `(\w+)\s*=\s*(.*)` under `VERIFICATION_CHARTER.md` §2d.1, all four conditions answered in
`PREREG_ADDENDUM_02.md`. **The load-bearing condition is satisfied in its strongest form:
the defect made the comparator emit NO NUMBER AT ALL (exit 2), so the repair cannot have
been selected to move a verdict — there was no verdict and no direction in which to select.**
Before either file was touched, both comparators were probed in memory against every
completed level to find every defect in one pass; the regex was the only one. **No gate,
band, reference, window or label moved** — this lane re-checked that the committed blob at
HEAD still hard-codes the 3 % band, the 1.0895 target, the `GATE REACHED` ceiling and the
1.5381 Arm-B prediction, and it does.

### 7.2 The predecessor lane's inheritance — INHERITED NARRATIVE, not re-verified here
A predecessor died before committing anything. Its work was **judged, not trusted and not
deleted**: `polymesh_area.py`, the name-based force reader, the Roache classifier, the
completion checker, both planted controls and the K = 400 exact-nesting scheme were **kept**;
the **mesh topology** was rewritten (it emitted two coincident axis vertices, which
`blockMesh` does **not** merge under the default `mergeType topology`) to the
shared-axis-vertex pattern OpenFOAM's own `SandiaD_LTS` tutorial uses; the **reference area**
was corrected (§6); a broken `spherePatchArea` function object and a stray
`constant/momentumTransport` were **discarded**. `grade_vmfl036.py` was truncated mid-file at
line 472 with no `main`, no `--selftest` and no verdict logic — completed.

### 7.3 A pre-freeze observation, disclosed — VERIFIED against the frozen document
Validating the rewritten mesh required 300 scratch iterations, so **a coarse partial Cd of
~1.09 was visible to that lane before the freeze**. Fully disclosed in the
pre-registration's DISCLOSURE 1 (line 208): the target 1.0895 is **printed in the manual**
and the 3 % band is argued from four sources **fixed before any lane ran anything**, so
neither was choosable; the observation is not in the graded family; and the launcher's smoke
test was rebuilt to **print no value**.
**Arm B carries no such caveat** — its 1.5381 prediction was registered with no corresponding
observation of any kind (`PREREGISTRATION.md` line 233), **and Arm B is the arm that
establishes §4.**

### 7.4 A near-miss, recorded because it nearly became a finding — INHERITED, not re-verified
A throughput sample taken during VMFL023's start-up transient projected all three of that
case's levels to **cross their caps**. Re-measured on a clean window, they all fit. **Nothing
was reported off the bad sample** — it was re-measured before anything was written — but it
was one step from becoming a finding.

---

## 8. COST — estimate versus actual (CLAUDE.md rule 12 calibration)

**The arms had SEPARATE budgets and could not starve each other**: each arm is its own
invocation with its own 120 core-min budget file, so Arm B (the diagnostic) could not consume
any part of Arm A's (the gate). Both ran concurrently, one core each, serial (`ranks = 1`),
so **core-min = wall-min on every figure in this section**. All actuals read from each level's
own `RUN_RC.txt`.

| Level | predicted (core-min) | Arm A actual | Arm B actual | ratio (A) |
|---|---|---|---|---|
| L1 | 1.7 | 1.37 | 1.35 | 0.80× |
| L2 | 6.7 | 6.67 | 6.50 | 1.00× |
| L3 | 26.7 | 33.40 | 33.12 | **1.25×** |
| **arm total** | **35.0** | **41.43** | **40.97** | **1.18×** |

**BOTH ARMS: predicted 70.0 core-min, actual 82.40 core-min, ratio 1.18×.**
Cap **120 core-min per arm** — **no overrun; ~79 core-min of headroom unused on each.**

- **Gross = cleaned, 82.40 core-min.** The largest row is 2 004 wall s, well under the
  3 600-s stall rule, so it matches nothing and there is nothing to clean.
- **WASTE: ZERO, and named separately rather than absorbed into the ratio** (COMPUTE_BUDGET
  §6). Nothing killed, nothing re-run, no level discarded. The launcher's smoke tests are
  explicitly **refunded** from the budget in the executable path, so machinery does not eat
  the graded run's allowance.
- **CONTENTION, named separately as rule 12 requires.** A mid-run throughput sample taken
  while five solvers shared the box read as low as **1.49e5 cell-iter/s** against the
  **3.07e5** the estimate was built on. Contention is therefore **present and named**, but it
  is **not the whole of the 1.18× gap** — see the attribution below, which does not launder
  one into the other.
- **$0.0705 DERIVED** at the owner-stated c7a.4xlarge rate of $0.0513/core-h.
  **DERIVED, NOT MEASURED** — this box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5).

### GAP ATTRIBUTION — MISPREDICTION, and specifically a CACHE-RESIDENCY one

The estimate used a throughput of **3.07e5 cell-iterations/s measured on the 3 072-cell L1**,
which is **cache-resident**. L1 and L2 came in at 0.80× and 1.00× — **the basis is good where
it was measured.** L3, at 49 152 cells, ran **1.25× over**. Contention (above) contributes,
but the level-by-level pattern is the tell: contention would have inflated all three levels,
and it did not — **only the level that no longer fits in cache missed.**

> **The lesson for the next estimate: a throughput basis taken on the COARSEST level
> under-predicts the finest by ~25 %, because the coarse level fits in cache and the fine one
> does not. State the cell count a throughput basis was measured at, beside the basis.**

This comparison also landed as row **C-92** in `docs/COST_CALIBRATION.md` at `6a229113`.

---

## 9. WHERE THIS CASE STANDS IN THE REGISTER

**Register row #20**, `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`,
committed at **`6a229113`**, carries **Arm A** as `GATE REACHED` and describes **Arm B** in
full inside the same row, including its verdict, its two registered tests and its cost.

**No row #21 was appended, deliberately.** Arm B is already carried by row #20; the register
is append-only and a second row for the same graded family would (a) duplicate a run that is
already in the ledger and (b) **double-count 40.97 core-min**, since row #20's cost column
already reports **82.40 core-min across BOTH arms**. A second row here would be a duplicate,
not a correction and not a re-run — the two cases the register's append rules reserve new rows
for.

---

## 10. ARTIFACTS

- **Runs:** `verification/runs/ansys_verification/VMFL036/{A,B}/{L1_32x48,L2_64x96,L3_128x192}/`
  — each with `log.simpleFoam`, `log.blockMesh`, `log.checkMesh`, `RUN_RC.txt`,
  `MESH_BIRTH_CERTIFICATE.txt`, `constant/polyMesh/`,
  `postProcessing/forces/0/force.dat`, and the `10000/` field directory.
- **Launch records** (blobs verified at launch):
  `verification/runs/ansys_verification/VMFL036/{A,B}/LAUNCH_RECORD.txt`
- **Comparator output (this lane's re-run):** `cases/ansys_verification/VMFL036/GRADING_OUTPUT.txt`
- **Pre-registration:** `cases/ansys_verification/VMFL036/PREREGISTRATION.md` @ `ff9e28da`
- **Addenda:** `cases/ansys_verification/VMFL036/PREREG_ADDENDUM_01.md` (geometry/budget
  instructions), `cases/ansys_verification/VMFL036/PREREG_ADDENDUM_02.md` (the §2d.1 repair)
- **Supervisor's pre-freeze check:** `cases/ansys_verification/VMFL036/SUPERVISOR_PREFREEZE_CHECK.md` @ `3fa6058d`
- **Comparator:** `cases/ansys_verification/VMFL036/grade_vmfl036.py` @ blob `8a1aea3bd6f0dcd1d720c54a92f76b780924d028`
- **Register row #20:** `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` @ `6a229113`
- **Cost calibration row C-92:** `docs/COST_CALIBRATION.md` @ `6a229113`
