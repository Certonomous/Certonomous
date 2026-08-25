# VMFL036 — Laminar Flow Past Sphere — RESULTS

**Graded 2026-08-25T22:21:30Z.** Manual VM2026R1 pp. 125–126.
Pre-registration frozen and committed at **`ff9e28da`** BEFORE any solver
started; the run root did not exist at the freeze timestamp on its line 1.
Comparator `grade_vmfl036.py`, blob **`8a1aea3bd6f0dcd1d720c54a92f76b780924d028`**
(repaired under §2d.1 at `591f659e` — see ADDENDUM 02, and §7 below).

---

## 1. THE VERDICT

| Arm | Verdict | Cd (finest) | Reference | \|rel\| | Band | Triple |
|---|---|---|---|---|---|---|
| **A — THE GATE** (nu = 0.01, Re = 100) | **`GATE REACHED`** | **1.088834** | 1.0895 | **0.0611%** | 3% | CONVERGING |
| **B — diagnostic** (nu = 0.02, Re = 50) | **`NOT A RESULT`** *(by registration)* | 1.577375 | — | — | — | CONVERGING |

**`GATE REACHED` IS THE CEILING AND IT WAS FROZEN AS THE CEILING, NOT DISCOVERED
AFTERWARDS.** Mittal (1999) is a Fourier–Chebyshev **spectral collocation
computation** and Tabata & Itakura (1998) is titled *"a precise **computation** of
drag coefficients"*. Both are **code-to-code**, so this reference buys **neither V
nor P**. `PASS`/`HOLDS` was **not available to this case whatever the number
landed at** — pre-registration lines 3–4, and the comparator hard-codes it.
**Reproducing another solver's number is not a validation credential**, and a
0.0611% agreement does not change that.

---

## 2. THE GRID FAMILY — ARM A

| Level | Cells | Cd | Final residual | Cd plateau (ptp/Cd) | wall s | core-min |
|---|---|---|---|---|---|---|
| L1_32x48 | 3 072 | 1.091486 | 1.05e-11 | 3.20e-12 | 82 | 1.37 |
| L2_64x96 | 12 288 | 1.089233 | 1.22e-11 | 5.06e-13 | 400 | 6.67 |
| **L3_128x192** | **49 152** | **1.088834** | 1.04e-11 | 1.50e-11 | 2 004 | 33.40 |

**Roache (rule 5):** d32 = 2.252e-03, d21 = 3.992e-04, **R = 0.177234**,
state **CONVERGING**. **GCI_fine at Fs = 1.25 = 0.0099%.** Richardson
extrapolate f_ex = 1.088748 — which is **0.069% from the manual's target**, i.e.
the zero-mesh limit agrees with the reference at least as well as the finest grid.

### The observed order is ABOVE the formal order, and that is a WARNING, not a win

**p_obs = 2.4963 against a formal p_f = 2.** Pre-registration line 10 declared
`p_obs > 2.3` **SUSPICIOUSLY HIGH in advance**, and the comparator printed the
flag itself. It is reported as the warning it was registered to be. The honest
reading: with d21 already at 4e-04 on a quantity of order 1, the fine-grid
difference is small enough that a modest amount of error cancellation between the
pressure and viscous contributions will inflate the fitted order. **The GCI is
quoted because the triple is monotone; it is NOT evidence of third-order
accuracy, and no such claim is made.**

## 3. THE GRID FAMILY — ARM B

| Level | Cells | Cd | Final residual | wall s | core-min |
|---|---|---|---|---|---|
| L1_32x48 | 3 072 | 1.577946 | 1.47e-11 | 81 | 1.35 |
| L2_64x96 | 12 288 | 1.577388 | 1.01e-11 | 390 | 6.50 |
| **L3_128x192** | **49 152** | **1.577375** | 9.97e-12 | 1 987 | 33.12 |

Triple CONVERGING, but **p_obs = 5.4607 is not interpretable**: d21 = 1.27e-05 is
within an order of the plateau noise, so the fitted order is fitting round-off.
**Stated rather than quoted as a result.** Arm B's content is §4, not its order.

---

## 4. WHAT ARM B ESTABLISHES — the manual's viscosity IS the error

The supervisor's committed pre-freeze check (`3fa6058d`) found the manual's page
**internally inconsistent**: stated `mu = 0.02` gives **Re = 50**, but the target
**Cd = 1.0895 is the Re = 100 value**. Arm B ran the manual's stated viscosity
**exactly as printed**, against a prediction **registered before the run**:

| Quantity | Registered before the run | Measured | Test |
|---|---|---|---|
| Cd at Re = 50, Schiller–Naumann | **1.5381** | **1.577375** | \|rel\| = **2.55%**, band 10% → **AGREES** |
| Distance from the manual's target 1.0895 | must be **≥ 25%** | **44.78%** | → **DISCRIMINATES** |

**Both registered tests pass.** Running the manual's own stated properties
produces **1.577**, not **1.0895** — a 44.8% miss — while the same solver, same
mesh family, same schemes, at the Re the target actually belongs to, lands
**0.0611%** from it.

> **The conclusion this supports: the error is in the manual's printed viscosity,
> not in this lab's solver.** `mu = 0.02` on that page is a transcription error
> for `mu = 0.01`.

**And what it does NOT do:** Arm B is **`NOT A RESULT`**, by registration and by
construction. It is evidence **about the manual**. It is not a gate on the solver,
it scores nothing, and it appears in no credential count.

**Had the gate been frozen the obvious way** — target 1.0895 at the manual's
stated `mu = 0.02` — this case would have returned a **guaranteed `GATE FAIL`
measuring a typo**. That is the VMFL059 class, and it was caught **before** the
freeze this time rather than after.

---

## 5. CONTROLS — every one fired against REAL artifacts

- **PLANTED FORCE (rule 3).** `total_x = 7.7e-03` planted into a **copy** of the
  finest level's real `force.dat`; the reader returned **7.700000e-03** (a Cd of
  1.4136). **The reader is shown able to see a non-zero**, so its readings are
  evidence.
- **PLANTED GEOMETRY (rule 3).** Every point of a **copy** of the finest mesh
  scaled by 2; sphere area went **0.04360473 → 0.17441892** against a required
  0.17441892 (exactly ×4). **The geometry reader is shown able to see a changed
  geometry.**
- **PERMUTED-COLUMN READER.** `total_x` placed in a deliberately permuted column
  and still found **by name**; a planted zero read back as **0.0**; a header with
  no `total_x` **REFUSED**, not guessed.
- **ROACHE CLASSIFIER.** All five states — CONVERGING, DIVERGENT, OSCILLATORY,
  STAGNANT, EXACT — constructed and each correctly classified; the
  exactly-second-order triple returned p_obs = 2 to 1e-9.
- **GEOMETRY IDENTITY.** Closed-form Aref `1.0894467844e-02` against an
  independent 200 000-point quadrature `1.0894467844e-02`.
- **STRICT COMPLETION (rule 4), NO DEPARTURE DECLARED.** Every clause checked
  literally at every level: rc = 0, `End` line, last time == endTime,
  `ExecutionTime` count == 10 000, U and p present at endTime, and the **age
  guard** (every endTime field newer than the case's own `0/`).
- **MESH BIRTH CERTIFICATE**, read off `constant/polyMesh` by the frozen
  pure-python reader at **every** level — never the solver, never a function
  object. **Frontal PROJECTED area / frozen Aref = 1.000000000 at all three
  levels.**

---

## 6. THE AZIMUTHAL BIAS — carried, not assumed away (N-AV9)

The predecessor lane froze `Aref = D²sin(a)/4` and argued the `sin(a)` cancels.
**It does not fully.** The wedge maps `(x,y) → (x, y·cos a, ±y·sin a)`, and two
**different** factors follow — exactly the charter's warning that the wedge term
is case-shaped:

| quantity | azimuthal factor |
|---|---|
| **wetted** area | `sin(a)/a` |
| **frontal projected** area | `sin(a)·cos(a)/a` |

The projected form carries an **extra cos(a)**. `Aref` was corrected to
`D²sin(a)cos(a)/4 = 1.08944678435e-02`, which matches the value read off the
real mesh **to 1 part in 1e8**; the predecessor's form was **0.095% larger**.

**The residual bracket is carried, not dropped.** The projected normalisation
makes the *pressure* drag azimuthally exact and leaves the *viscous* part biased
by `1/cos(a)`; the two limits bracket the truth and differ by exactly `cos(a)`:

> **Cd = 1.088834** (projected, the gate) **vs 1.087798** (wetted).
> **Bracket = 0.0952% of Cd, half-width 0.0476%. No grid refinement removes it.**

Both are printed beside the verdict. The bracket is ~1/30 of the band, so **it
cannot decide the gate** — the wetted-form value misses the target by 0.157%,
still inside 3% by a factor of 19. **It is disclosed regardless.**

---

## 7. WHAT WENT WRONG, AND WHAT IT COST

### 7.1 The comparator could not read its own launcher (repaired under §2d.1)
Both launchers write `rc = 0` **with spaces**; both comparators parsed
`(\w+)=(.*)`, which requires the `=` to abut the key. **No key matched**, `rc`
defaulted to `"1"`, and the strict-completion guard **refused every level**.
**VMFL036 would have been ungradable.**

Caught by the **rule-4 guard** — which grades nothing — **before** grading, not
after. Repaired to `(\w+)\s*=\s*(.*)` under `VERIFICATION_CHARTER.md` §2d.1,
with all four conditions answered in `PREREG_ADDENDUM_02.md`. **The
load-bearing condition is satisfied in its strongest form: the defect made the
comparator emit NO NUMBER AT ALL (exit 2), so the repair cannot have been
selected to move a verdict — there was no verdict and no direction to select.**
Before touching either file, **both comparators were probed in memory against
every completed level to find every defect in one pass; the regex was the only
one.** No gate, band, reference, window or label moved.

### 7.2 The predecessor lane's inheritance
A predecessor died before committing anything. Its work was **judged, not trusted
and not deleted**: `polymesh_area.py`, the name-based reader, the Roache
classifier, the completion checker, both planted controls and the K = 400
exact-nesting scheme were **kept**; the **mesh topology** was rewritten (it
emitted two coincident axis vertices, which blockMesh does **not** merge under
the default `mergeType topology`) to the shared-axis-vertex pattern OpenFOAM's
own `SandiaD_LTS` tutorial uses; the **reference area** was corrected (§6); a
broken `spherePatchArea` function object and a stray `constant/momentumTransport`
were **discarded**. `grade_vmfl036.py` was truncated mid-file at line 472 with no
`main`, no `--selftest` and no verdict logic — completed.

### 7.3 A pre-freeze observation, disclosed
Validating the rewritten mesh required 300 scratch iterations, so **a coarse
partial Cd of ~1.09 was visible to this lane before the freeze**. Fully disclosed
in the pre-registration's DISCLOSURE 1: the target 1.0895 is **printed in the
manual** and the 3% band is argued from four sources **fixed before this lane ran
anything**, so neither was choosable; the observation is not in the graded family;
and the launcher's smoke test was rebuilt to **print no value**.
**Arm B carries no such caveat** — its 1.5381 prediction was registered with no
corresponding observation of any kind, and it is the arm that establishes §4.

### 7.4 A near-miss, recorded because it nearly became a finding
A throughput sample taken during VMFL023's start-up transient projected all three
of that case's levels to **cross their caps**. Re-measured on a clean window they
all fit. **Nothing was reported off the bad sample** — it was re-measured before
anything was written — but it was one step from becoming a finding.

---

## 8. COST — estimate versus actual (rule 12 calibration)

**Arms had SEPARATE budgets and could not starve each other**: each arm is its
own invocation with its own 120 core-min budget file, so Arm B (the diagnostic)
could not consume any part of Arm A's (the gate). Both ran concurrently, one core
each, serial (`ranks = 1`), so **core-min = wall-min**.

| Level | predicted (core-min) | Arm A actual | Arm B actual | ratio |
|---|---|---|---|---|
| L1 | 1.7 | 1.37 | 1.35 | 0.80x |
| L2 | 6.7 | 6.67 | 6.50 | 0.98x |
| L3 | 26.7 | 33.40 | 33.12 | **1.25x** |
| **arm total** | **35.0** | **41.43** | **40.97** | **1.18x** |

**BOTH ARMS TOTAL: predicted 70.0 core-min, actual 82.40 core-min, ratio 1.18x.**
Cap 120 core-min per arm — **no overrun; ~79 core-min of headroom unused on each**.

- **Gross = cleaned, 82.40 core-min.** The largest row is 2 004 wall s, well under
  the 3 600 s stall rule, so it matches nothing and there is nothing to clean.
- **WASTE: ZERO.** Nothing killed, nothing re-run, no level discarded. The
  launcher's smoke tests are explicitly **refunded** from the budget in the
  executable path, so machinery does not eat the graded run's allowance.
- **$0.0705 DERIVED** at the owner-stated c7a.4xlarge rate $0.0513/core-h.
  **DERIVED, NOT MEASURED** — this box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER.md` §5).
- **GAP ATTRIBUTION — MISPREDICTION, and specifically a CACHE-RESIDENCY one.**
  The estimate used a throughput of 3.07e5 cell-iterations/s measured on the
  **3 072-cell L1**, which is cache-resident. L1 and L2 came in at 0.80x and 0.98x
  — the basis is good where it was measured. **L3, at 49 152 cells, ran 1.25x
  over**, and a mid-run sample under five concurrent solvers read as low as
  1.49e5 cell-iter/s before recovering. **The lesson for the next estimate: a
  throughput basis taken on the coarsest level under-predicts the finest by ~25%,
  because the coarse level fits in cache and the fine one does not. State the
  cell count a throughput basis was measured at, beside it.**

---

## 9. ARTIFACTS

- Runs: `verification/runs/ansys_verification/VMFL036/{A,B}/{L1_32x48,L2_64x96,L3_128x192}/`
  — each with `log.simpleFoam`, `log.blockMesh`, `log.checkMesh`,
  `RUN_RC.txt`, `MESH_BIRTH_CERTIFICATE.txt`, `constant/polyMesh/`,
  `postProcessing/forces/0/force.dat`, and the `10000/` field directory.
- Launch records (blobs verified at launch):
  `verification/runs/ansys_verification/VMFL036/{A,B}/LAUNCH_RECORD.txt`
- Pre-registration: `cases/ansys_verification/VMFL036/PREREGISTRATION.md` @ `ff9e28da`
- Addenda: `PREREG_ADDENDUM_01.md` (geometry/budget instructions), `PREREG_ADDENDUM_02.md` (the §2d.1 repair)
- Supervisor's pre-freeze check: `SUPERVISOR_PREFREEZE_CHECK.md` @ `3fa6058d`
- Comparator: `cases/ansys_verification/VMFL036/grade_vmfl036.py`
