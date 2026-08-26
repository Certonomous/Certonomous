# VMFL064-R2 — RESULTS

Low Reynolds Number Flow in a Channel with Sudden Asymmetric Expansion
(backward-facing step, Armaly `LR/s = 5.0`), VM2026R1 **p. 195**/196.
Re-registration of VMFL064 under `ANSYS_VERIFICATION_CHARTER` §6: **a new register
row (#30) that cites row #29 and does not overwrite it.** Row #29 stands as
`NOT A RESULT` and is unchanged by anything below.

Graded by the frozen comparator `cases/ansys_verification/VMFL064-R2/grade_vmfl064_r2.py`,
blob **`e04fdf937d557b4919928ab72b9fe5eb42f8b49a`**, against the pre-registration
`cases/ansys_verification/VMFL064-R2/PREREGISTRATION.md`, blob
**`abe17c3b990acd31bba12fde01aaf757c6ab398e`**, frozen at commit
**`3e7c792cbde23a7cc105d63d01487dc5d01c8040`** — **the only commit that has ever
touched that file, and it landed before any R2 solver started.** The launcher printed
`freeze OK` against both blobs before every level.
Raw grading record: `verification/runs/ansys_verification/VMFL064-R2/GRADING_VMFL064_R2.json`.

---

## VERDICT — `GATE REACHED`

**`LR/s = 4.853056`** at the finest level against the experimental reference **5.0** —
**2.9389 %** deviation inside the frozen **10 %** band, on a **`CONVERGING`** triple.

**`GATE REACHED` is the ceiling, and it is not a `PASS`.** The reference is
experimental (Armaly et al. 1983) and experimental references *can* buy P, but
pre-registration line 4 declared the ceiling `GATE REACHED` in advance because this
team's product is **reproducing the Ansys manual**, and the comparator hard-codes that
string: it cannot print `PASS` or `HOLDS` whatever the number. **This row is not a
credential and must not be counted as one.**

## 1. THE MEASUREMENT

Gate scalar: the reattachment length `LR` on patch `bottomWall`, non-dimensionalised by
the step height `s = 4.9 mm`, read as the **LAST** negative-to-positive crossing of the
physical wall shear inside the registered window `0.0 m < x ≤ 0.05 m`.

| level | cells | wall faces | cell dx [m] | `LR` [m] | **`LR/s`** | corner vortex resolved | crossings n→p / p→n |
|---|---|---|---|---|---|---|---|
| L1 | 3 072 | 64 | 1.562500e-03 | 0.023100636296 | **4.714416** | no | 1 / 0 |
| L2 | 12 288 | 128 | 7.812500e-04 | 0.023523615943 | **4.800738** | no | 1 / 0 |
| L3 | 49 152 | 256 | 3.906250e-04 | 0.023779973479 | **4.853056** | **yes** | 1 / 1 |

**The gate, at the finest level:** `abs(LR/s − 5.0) / 5.0` = **2.9389 %** against a band
of **10.00 %** — **met**, consuming 29 % of the tolerance.
Ansys Fluent's own 4.91 is **context only and was never the gate**.

## 2. THE TRIPLE, AND ITS GCI

```
d21 = LR/s(L2) − LR/s(L1) = 0.086322377043
d32 = LR/s(L3) − LR/s(L2) = 0.052317864523
R   = d32/d21             = 0.606075      ->  CONVERGING (monotone, 0 < R < 1)
p_obs = 0.722431     GCI_fine (Fs = 1.25) = 2.0733 %     f_extrapolated = 4.933550
```

**`p_obs = 0.7224` is BELOW the formal `p_f = 2`, and that is reported as what it is.**
The pre-registration declared `p_obs > 2.3` SUSPICIOUSLY HIGH; the observed order sits
at the other end, which is the ordinary signature of a quantity read off a wall profile
by interpolation between faces on a bubble that is only just resolved. It is **above**
the registered floor `P_MIN = 0.05`, so a GCI is quoted; **2.0733 % is of the same order
as the 2.9389 % deviation itself**, and the honest reading is that the finest value and
the reference agree inside a band that is roughly three times the numerical uncertainty
— not that the reattachment length has been pinned to three digits.

## 3. WHAT THIS R2 SET OUT TO FIX, AND WHETHER IT DID

Row #29 died at a refusal: **`REFUSED (exit 2): L3: wall shear never changes sign -- no
reattachment found`**. The diagnosis was that L3 resolves a **secondary corner vortex**
the coarser levels do not, so the wall-shear profile no longer *starts* negative and the
frozen first-crossing reader lost its premise. The R2 changed the reader to the **last**
crossing inside a registered window, and nothing else.

**The record now says the diagnosis was right, and says it from this run's own data.**
`corner_vortex_resolved` is **false at L1 and L2 and true at L3**, and the crossing
census shows exactly the predicted structure: `n→p = 1, p→n = 0` at the two coarse
levels, and `n→p = 1, p→n = 1` at L3 with the profile **starting positive**. That is the
corner vortex appearing at the finest level and nowhere else — the mechanism named in
row #29's triage, measured here rather than argued.

**And the change did not move the two numbers that already existed.** L1 `LR/s` =
4.714416 and L2 = 4.800738, identical to the values row #29 published as the only two
that existed. The R2 reader agrees with the attempt-1 reader wherever the attempt-1
reader could read at all; it only adds the level the old one refused.

## 4. THE CONTROLS, ALL LIVE AT GRADE TIME

`--selftest` **37/37 PASS**, identical under `python3` and `python3 -O`, driven **by the
launcher before a core-minute was spent**; `ast.Assert` count 0.

- **Planted-zero (rule 3).** `0.001234` planted into a copy of `bottomWall`'s
  `wallShearStress` on disk and read back as **`0.0012340000000004199`** — a
  single-point plant into a single-point reader, delta equal to the plant to 12
  significant figures, no averaging dilution (L-340).
- **Corner-vortex planted control — the control that drives this repair.** On a
  constructed profile with a known primary reattachment at `6·s` and a corner eddy at
  `x_c = 7.0e-4 m`, the R2 reader recovered **`LR/s = 5.999803`** (dx = 3.90625e-04 m),
  while **the attempt-1 logic exited 2 on the same bytes**. Single-bubble agreement:
  attempt-1 and R2 readers both return **0.0294 m** exactly. **Window probe: 0.029399 m
  with the window, 0.065038 m without it** — the window is load-bearing, measured, not
  asserted.
- **Cross-instrument control.** `LR` from wall shear against `LR` from near-wall `u_x`:
  **2.42e-07 / 5.77e-08 / 1.42e-08 m** at L1/L2/L3, against a refusal threshold of three
  cell widths (4.69e-03 / 2.34e-03 / 1.17e-03 m) — four to five orders of margin, and
  the same evidence that confirmed `ORIENT = -1` on real data in attempt 1.
- **Observed-order floor `P_MIN = 0.05`**, driven both ways before any level was read:
  `p = 0.01` and the equally-spaced `(1.0, 1.1, 1.2)` both return **NOT A RESULT with no
  GCI**; `p = 0.5` returns `CONVERGING` **with** a GCI, so the floor cannot swallow a
  real result.
- **Strict completion (rule 4) held at all three levels**, with L-342 field classes:
  `rc = 0` (`MEASURED` at every level, from `RUN_RC.<level>`), an `End` line,
  `SIMPLE solution converged`, `ExecutionTime` count equal to the iteration count
  (424 / 907 / 2 152), `U`, `p`, `wallShearStress`, `Cx`, `Cy` present at that time, and
  every one of them newer than the case's own `0/U`. **The solver stopped on its own
  `residualControl` far short of the `endTime` of 20 000** — which for a steady SIMPLE
  solve is the stronger completion statement, and is the registered clause.

## 5. COST — ESTIMATE VERSUS ACTUAL (rule 12)

| level | wall [s] | core-min |
|---|---|---|
| L1 | 1 | 0.0167 |
| L2 | 17 | 0.2833 |
| L3 | 300 | 5.0000 |
| **total** | **318** | **5.3** |

**Measured 5.3 core-min** (`COST.txt`, `RUN_RC.L1/.L2/.L3`; RANKS = 1, so core-min =
wall-min) against **5.4 predicted** — **ratio 0.98**, the closest this team has come to
its own estimate. That is not luck and is not claimed as skill: the estimate was
anchored on attempt 1's **measured** 5.383 core-min for the byte-identical inputs, and
only the reader changed. **5.9 % of the 90 core-min cap**, never approached.

**WASTE: 0.000 core-min.** The 17:49:13Z first launch attempt was refused by the
launcher's own argv guard **before OpenFOAM was sourced** and spent nothing.

**$0.0045 DERIVED, NOT MEASURED** at $0.0513/core-h (c7a.4xlarge, owner-stated) — the
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Calibration row
**C-141** — issued after re-deriving the maximum id from the `HEAD` blob at commit time
(rule 11). **C-140 was drafted for this row and withdrawn before it landed**: a
heat-transfer peer took that id in commit `af6df4fe` between this lane's read and its
commit, and the collision was caught by the re-derivation rather than by a reader
later. An id written in prose before its append is a prediction, not an identifier.

## 6. INFRASTRUCTURE NOTES (L-342 — each voids bookkeeping, none voids the physics)

Sanaa's rule, verbatim: *"a bookkeeping failure invalidates the bookkeeping, never the
physics artifacts."* Three bookkeeping facts are recorded here rather than tidied away,
and **not one of them touches the verdict, the value, the triple or the cost**:

1. **`VMFL064R2-ENTRY-DEF-1` — the entry that could not launch.** The first queue entry
   (fired 17:49:13Z) omitted the launcher's required `<run_root>` argv. The launcher
   refused at zero compute:
   `run_vmfl064_r2.sh: line 49: 1: usage: run_vmfl064_r2.sh <run_root> [levels...]`
   (`launcher.queue.out.attempt1`; `STATUS.VMFL064-R2.attempt1-refused-no-run_root`
   carries `launcher_rc=1`). **The guard worked exactly as written** — an entry that
   would have run in the wrong place was stopped by the launcher, not by a person. The
   entry was re-filed with the run root at 20:45Z and the graded launch followed
   (`STATUS.VMFL064-R2`, `launcher_rc=0 end=2026-08-26T20:51:05Z`).
   **Standing lesson, and it is cheap: drive every entry's argv once against the
   launcher's usage guard before enqueueing.**
2. **`CAP_OVERRUN.txt` is keyed on the wrong epoch and reports an overrun that did not
   happen.** It is stamped `2026-08-26T20:45:38Z` and claims *"elapsed 10585 s > 1.10 x
   registered 324 s"*. The graded launch began at **20:45:43Z**, **five seconds after
   that file was written**, and finished at 20:51:05Z — **318 s of a 5 400 s per-level
   timeout and a 90 core-min cap, 5.9 % used.** 10 585 s is the interval since the
   *17:49Z attempt-1 launch epoch*, i.e. the runner priced a wall clock that includes
   the three hours during which nothing was running. It is a **runner bookkeeping
   artefact**, it says `REPORTED, NOT ENFORCED`, nothing was killed, and **no cap was
   crossed**. Recorded, not deleted.
3. **The launcher's detachment check reports `DETACH WARN` at all three levels, and the
   check is the thing that is wrong, not the detachment.** `setsid` is applied to
   `timeout` *inside* the waited-on subshell, so the subshell whose `/proc/<pid>/stat`
   is read is never a session leader and `SID == PID` can never hold in this form
   (measured here: wrapper pids 390529 / 390586 / 390833, all SID 390179; independently
   reproduced on the VMFL011-R2 launcher, which inherits the same shape). The solver
   **was** in its own session. **The check can only ever raise a false alarm, never
   certify a false pass**, and it gates nothing — so it is reported rather than repaired
   under an amendment, and it is carried as a finding against the R2 launcher family.

## 7. WHAT THIS ROW DOES NOT CLAIM

- **It is not a credential.** Ceiling `GATE REACHED`, declared before compute.
- **It does not retire row #29.** Row #29's `NOT A RESULT` is the honest record of what
  the frozen instrument did, and the charter keeps it.
- **It does not claim a converged reattachment length to three digits.** `p_obs = 0.7224`
  and `GCI_fine = 2.0733 %` are printed beside the verdict precisely because the
  numerical uncertainty is the same size as the agreement.
- **It does not establish that the corner vortex is fully resolved at L3** — only that
  it is *present* at L3 and absent at L1/L2, and that the last-crossing reader returns
  the primary reattachment either way, which is the property the reader was registered
  on.

## PROVENANCE

- **Pre-registration:** `cases/ansys_verification/VMFL064-R2/PREREGISTRATION.md`, blob
  `abe17c3b990acd31bba12fde01aaf757c6ab398e`, frozen at
  `3e7c792cbde23a7cc105d63d01487dc5d01c8040`.
- **Comparator:** `grade_vmfl064_r2.py`, blob
  `e04fdf937d557b4919928ab72b9fe5eb42f8b49a`.
  **Launcher:** `run_vmfl064_r2.sh`, blob `c17ee2e2693b382fd043aadc326bdae8e51fd7b6`.
- **Artifacts:** `verification/runs/ansys_verification/VMFL064-R2/` —
  `GRADING_VMFL064_R2.json`, `RUN_RC.{L1,L2,L3}`, `COST.txt`, `LAUNCH_RECORD.txt`,
  `CONTENTION.txt`, `CAP_OVERRUN.txt`, `STATUS.VMFL064-R2`,
  `STATUS.VMFL064-R2.attempt1-refused-no-run_root`, `launcher.queue.out`,
  `launcher.queue.out.attempt1`, and `{L1,L2,L3}/`.
- **Attempt 1, cited and not overwritten:** `cases/ansys_verification/VMFL064/RESULTS.md`,
  register row #29, comparator blob `0be9126cd6a3e3c860b98854a4e21ba1102edfdc`, refusal
  verbatim in `verification/runs/ansys_verification/VMFL064/GRADING_ATTEMPT_REFUSED.txt`.
- **Manual:** `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
  p. 195/196, title-page verified against the PDF beside it (rule 15).
- **Register row #30**; **calibration row C-141**.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING.*
