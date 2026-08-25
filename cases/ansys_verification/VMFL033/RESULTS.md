# VMFL033 — Viscous Heating in an Annulus — RESULTS

**Case:** Ansys Fluid Dynamics Verification Manual VM2026R1, p.119.
**Graded 2026-08-25T22:57Z.** Pre-registration `PREREGISTRATION.md` frozen and committed at
**`9b0b573c`** BEFORE any solver started; the run root was **absent** at the freeze
timestamp on its line 1. Comparator `grade_vmfl033.py`, blob
**`0ac96be5abafb9257737672e10bc2c484381587b`** (repaired under `VERIFICATION_CHARTER.md`
§2d.1 — `PREREG_ADDENDUM_01.md`, §6 below). Raw output: `GRADING_OUTPUT.txt`.

---

## 1. THE VERDICT

# `NOT A RESULT`

**Not a `GATE FAIL`, and the distinction is the whole content of this record.** Rule 5's
ordering was applied in its own order: **(1)** two of three levels are **not plateaued**,
which alone forces `NOT A RESULT` whatever the values; **(2)** the Roache triple is
**`OSCILLATORY`** (R = −398.5), not `CONVERGING`; **(3)** only then would the band be
consulted. **The gate could only have turned a PASS or GATE FAIL INTO `NOT A RESULT`, and
that is the direction it moved.** No GCI is quoted — the triple is not monotone.

**TIER CEILING was and remains `GATE REACHED`**: the reference is a **closed form**, so it
buys **V (code verification)** and **never P**. This case could not have been a validation
credential at any value, and it is not one now.

## 2. THE PRE-REGISTRATION CALLED THIS FAILURE, BY NAME, BEFORE COMPUTE

Line 9 of the frozen form, verbatim:

> **9. PRINCIPAL RISK : THE SETTLING CLAUSE REFUSES.** Pr = 300 and the energy equation is
> relaxed at 0.3, so 20 000 SIMPLE iterations may not drive the volume-average temperature
> to a peak-to-peak of 1e-6 of the rise. **PREDICTED OUTCOME IF IT BITES: NOT A RESULT on
> step (1) of rule 5 — a refusal, never a lenient pass.**

**That is what happened, in the predicted mechanism, at the predicted step.** The record
notes it as a called shot, not as an excuse: **a correctly predicted failure is still a
failure, and the verdict is unchanged by having been foreseen.**

## 3. THE GRID FAMILY

| Level | Cells | T_avg (K) | max\|v−v_ex\| / wall speed | max\|T−T_ex\| / rise | worst final resid | plateau ptp/scale | n_window | max\|v_r\| |
|---|---|---|---|---|---|---|---|---|
| L1_nr32 | 256 | 284.153139 | 7.93e-04 | 6.06e-03 | 9.97e-13 | **0.00e+00** | 500 | 1.6e-07 |
| L2_nr64 | 512 | 284.146241 | 4.36e-04 | 2.79e-03 | 7.62e-10 | 6.52e-05 | 500 | 4.0e-08 |
| **L3_nr128** | **1024** | **286.895530** | **5.12e-02** | **2.82e-01** | 2.14e-08 | **7.85e-03** | 500 | 5.3e-07 |

Plateau floor 500, window **FIXED** at 500 (Amendment 4 item 1); realised `n_window`
recorded at every level (item 5). **Threshold ptp/scale ≤ 1e-6: L1 meets it, L2 misses by
65×, L3 misses by 7 800×.**

Exact reference values, **evaluated, never digitised**: interior peak **290.331779 K** at
r = 1.366405 (the walls are 273 / 274 K); volume-average **284.133655 K**; inner-wall flux
−123.839858 W/m².

## 4. WHAT THE FAMILY DOES SHOW — reported as a diagnostic, and it does NOT soften §1

**L1 and L2 agree with the closed form closely, and their errors fall.** max\|T−T_ex\| goes
6.06e-03 → 2.79e-03 of the 17.33 K viscous-heating rise (a factor 2.17), and
max\|v−v_ex\| goes 7.93e-04 → 4.36e-04 (a factor 1.82). Both are **settled to machine
precision or near it** (worst final residual 9.97e-13 and 7.62e-10).

**L3 is not converged, and that is the entire story of the failure.** Its worst final
residual is **2.14e-08** — four orders worse than L1 — its plateau peak-to-peak is
7.85e-03 of the rise, and its volume-average sits **2.75 K above** L2's. The refinement
did not degrade the discretisation; **the finest mesh simply ran out of iterations**, which
is exactly the mechanism line 9 named.

> **This is a strong hint that the case would meet its band on a longer run. It is NOT
> evidence that it does, and this record makes no such claim.** `endTime = 20000` is fixed
> by the freeze; a longer run is a **new pre-registration** (an R2 attempt), not an
> extension of this one. Until that runs, the answer is `NOT A RESULT`.

**The physics IS wired, independently of the gate.** `max|v_r| ≤ 5.3e-07` at every level
against a tangential wall speed of 1 m/s — the rotational cyclic sector reproduces a
purely tangential field to seven digits, which was the **secondary** risk declared on
line 9 and it did **not** bite.

## 5. CONTROLS — every one fired against REAL artifacts

- **PLANTED FIELD (rule 3).** `1.234e-03` planted into a **copy** of the finest level's
  real `T`; the reader returned **1.23400000001e-03**. **The reader is shown able to see a
  non-zero.**
- **PLANTED GEOMETRY (rule 3).** Every cell centre of a **copy** of the finest level's real
  `C` scaled by 2; radius **1.00367241 → 2.00734483** against a required 2.00734483. **The
  geometry reader is shown able to see a changed geometry.**
- **EVERY RADIUS READ BACK FROM OpenFOAM'S OWN `C` FIELD.** Nothing geometric is
  constructed from `nr`, `dr` or `(j+1/2)`; the mesh birth certificate at each level is
  built from `C` too.
- **STRICT COMPLETION (rule 4), no departure declared** — `rc = 0`; an `End` line; last
  time == `endTime`; `ExecutionTime` count == 20 000; the required fields present; and the
  **age guard** at every level.
- **`endTime` % `writeInterval` == 0 AND a field directory AT `endTime`**, asserted in
  **both** launcher and comparator.
- **AMENDMENT 5 field enumeration**, and it **caught a real defect before the freeze**:
  `fvSolution` carries `"(U|h|e|k|epsilon|omega)"` while the closure is `laminar`, and a
  draft comparator demanded **`alphat`**, which laminar `buoyantSimpleFoam` **does not
  write**. That draft would have **refused every level of a correct run**.
- **AMENDMENT 6: ZERO `assert` statements** carry any guard, refusal, control or gate.
- **SELFTEST GREEN, and PROVEN ABLE TO FAIL** — see §6.

## 6. THE COMPARATOR REPAIR (§2d.1) — the selftest could not fail, and now it can

The frozen comparator printed `SELFTEST GREEN` and exited 0 **with a control that must
fail having failed**. Found by the supervisor's mutation testing, **reproduced by this
lane** rather than taken on faith, and repaired under §2d.1 with all four conditions
answered in `PREREG_ADDENDUM_01.md`.

**The cause was NARROWER than the diagnosis**, and the difference is recorded because the
two need different fixes: the reader and plateau controls were correctly shaped and **did**
fail on break. **The real cause was a MISSING control — the selftest never exercised
`completion()` at all.** A missing control is invisible to any amount of reshaping.

**A second defect surfaced that the mutation set could not have found**: controls matched
an expected refusal **by substring** inside `except Refusal:` blocks whose fall-through was
itself a `refuse(...)` — caught by the same handler whenever the message contained the
substring. Fixed **structurally**, with a `ControlFailure` type no `except Refusal` catches.

**Verified by mutation, not by reading: 8 mutants × 2 interpreters = 16 runs, every one
`rc = 2` with no green line; the unmutated file `rc = 0` with it.**

**Load-bearing §2d.1 condition, in its strongest form:** the defect was found by an
instrument that **grades nothing**; it sits in the **selftest, not the grading path**; it
emitted **no number**; and **no level had been graded and no verdict existed** when the
repair was made — so there was **no direction in which to select**. Nothing on the grading
path moved.

## 7. COST — estimate versus actual (CLAUDE.md rule 12 calibration)

Serial, `ranks = 1`, so **core-min = wall-min**. All actuals from each level's own
`RUN_RC.txt`.

| Level | predicted (core-min) | actual | ratio | cap | headroom |
|---|---|---|---|---|---|
| L1_nr32 | 0.80 | 0.4167 | 0.52× | 5 | 4.583 |
| L2_nr64 | 1.60 | 0.6333 | 0.40× | 8 | 7.367 |
| L3_nr128 | 3.19 | 1.0167 | 0.32× | 15 | 13.983 |
| **total** | **5.6 raw / 8.4 registered** | **2.0667** | **0.37× / 0.246×** | 28 | — |

**No cap crossed at any level. Caps were PER LEVEL, not a shared drawdown**, so no level
could starve a later one.

**WASTE: 1.0334 core-min, named separately and NEVER absorbed into the ratio**
(`COMPUTE_BUDGET_CHARTER.md` §6) — the abandoned attempt 1 (L1 0.4167 + L2 0.6167 + an L3
fragment of **zero** solver iterations), preserved at
`verification/runs/ansys_verification/VMFL033_attempt1_ABANDONED_PARTIAL/`.
**Gross including waste = 3.1001 core-min; cleaned = 2.0667.** No row approaches the
3600 s stall rule.

**$0.00265 DERIVED** at the owner-stated c7a.4xlarge rate $0.0513/core-h — **derived, not
measured**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

### GAP ATTRIBUTION — a NEW misprediction mode, complementary to VMFL036's

The estimate over-predicted by ~3×, in the **opposite direction** to VMFL036's C-92 row.
Measured throughput, per level:

| level | cells | cell-iterations | wall s | cell-iter/s |
|---|---|---|---|---|
| L1 | 256 | 5.12e6 | 25 | **2.05e5** |
| L2 | 512 | 1.02e7 | 38 | **2.69e5** |
| L3 | 1024 | 2.05e7 | 61 | **3.36e5** |

**Throughput RISES with mesh size**, against a basis of 1.07e5 measured on a **50-iteration,
128-cell** smoke.

> **THE LESSON: a throughput basis taken on a very SHORT run is dominated by fixed startup
> and I/O cost, not by steady-state throughput, and it UNDER-predicts a long run —
> here by 3×. State the ITERATION COUNT a throughput basis was measured at, beside the
> cell count VMFL036's C-92 already requires.**

**The C-92 cache-residency effect did NOT repeat, exactly as predicted in advance** on
line 12: no level here leaves cache (L3 is 1024 cells), and the throughput trend is
monotonically upward rather than collapsing at the fine level. **CONTENTION is named
separately and is not the driver** — box load was ~12.7 of 16 throughout, yet every level
beat its estimate.

## 8. WHAT THIS LANE COULD NOT VERIFY

- **Whether the case meets its bands on a converged L3.** §4's hint is a hint. It is
  untested and this record claims nothing from it.
- **The manual's own figures (.33.2, .33.3) were never digitised or compared.** The manual
  prints no numeric table for this case; the reference here is the closed form, and Ansys's
  own curves are context only.
- **The chord-vs-arc geometric bias is neutralised by construction, not measured** — the
  reference is evaluated at the radii `C` reports, so the compared pair share the mesh's own
  radius. The residual cell-centroid-versus-`C` difference was not separately quantified.

## 9. ARTIFACTS

- Runs: `verification/runs/ansys_verification/VMFL033/{L1_nr32,L2_nr64,L3_nr128}/` — each
  with `log.buoyantSimpleFoam`, `log.blockMesh`, `log.checkMesh`, `RUN_RC.txt`,
  `MESH_BIRTH_CERTIFICATE.txt`, `constant/polyMesh/`,
  `postProcessing/Tmean/0/volFieldValue.dat`, and the `20000/` field directory incl. `C`.
- Abandoned attempt 1 (preserved): `verification/runs/ansys_verification/VMFL033_attempt1_ABANDONED_PARTIAL/`
- Launch record: `verification/runs/ansys_verification/VMFL033/LAUNCH_RECORD.txt`
- Pre-registration: `cases/ansys_verification/VMFL033/PREREGISTRATION.md` @ `9b0b573c`
- Addendum: `cases/ansys_verification/VMFL033/PREREG_ADDENDUM_01.md`
- Comparator: `cases/ansys_verification/VMFL033/grade_vmfl033.py` @ blob `0ac96be5abafb9257737672e10bc2c484381587b`
- Comparator output: `cases/ansys_verification/VMFL033/GRADING_OUTPUT.txt`
